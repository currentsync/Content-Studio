"""The single writer for project snapshots and the derived project index."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from contracts.io import read_yaml, sha256_file, write_yaml_atomic
from modules.workflow.scripts.paths import ARCHIVE, PROJECTS, project_dir, project_file

ROOT = Path(__file__).resolve().parents[3]


def _snapshot_validator() -> Draft202012Validator:
    schema_doc = json.loads((ROOT / "contracts" / "studio.schema.json").read_text(encoding="utf-8-sig"))
    schema = {
        "$schema": schema_doc["$schema"],
        "$id": schema_doc["$id"],
        "$defs": schema_doc["$defs"],
        "$ref": "#/$defs/ProjectSnapshot",
    }
    return Draft202012Validator(schema, format_checker=FormatChecker())


_VALIDATOR = _snapshot_validator()
_CONTRACT_DOC = json.loads((ROOT / "contracts" / "studio.schema.json").read_text(encoding="utf-8-sig"))
_CONTRACT_VALIDATOR = Draft202012Validator(_CONTRACT_DOC, format_checker=FormatChecker())


def validate_record(record: dict[str, Any]) -> None:
    errors = sorted(_CONTRACT_VALIDATOR.iter_errors(record), key=lambda err: tuple(map(str, err.absolute_path)))
    if errors:
        err = errors[0]
        location = ".".join(str(part) for part in err.absolute_path) or "record"
        raise ValueError(f"记录合同错误 {location}: {err.message}")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def snapshot_path(project_id: str, *, archived: bool = False) -> Path:
    return project_dir(project_id, archived=archived) / "project.yaml"


def load_snapshot(project_id: str, *, archived: bool = False) -> dict[str, Any]:
    path = snapshot_path(project_id, archived=archived)
    if not path.is_file():
        raise FileNotFoundError(f"找不到项目快照：{path}")
    value = read_yaml(path)
    if not isinstance(value, dict) or value.get("project_id") != project_id:
        raise ValueError(f"项目快照身份不匹配：{path}")
    validate_snapshot(value)
    return value


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    errors = sorted(_VALIDATOR.iter_errors(snapshot), key=lambda err: tuple(map(str, err.absolute_path)))
    if errors:
        err = errors[0]
        location = ".".join(str(part) for part in err.absolute_path) or "project.yaml"
        raise ValueError(f"项目快照合同错误 {location}: {err.message}")


def save_snapshot(project_id: str, snapshot: dict[str, Any], *, archived: bool = False) -> None:
    if snapshot.get("project_id") != project_id:
        raise ValueError("禁止通过 Workflow 修改其他项目的快照")
    snapshot["updated_at"] = now_utc()
    validate_snapshot(snapshot)
    write_yaml_atomic(snapshot_path(project_id, archived=archived), snapshot)
    rebuild_index()


def rebuild_index() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for base, archived in ((PROJECTS, False), (ARCHIVE, True)):
        if not base.exists():
            continue
        for snapshot_file in sorted(base.glob("*/project.yaml")):
            try:
                item = read_yaml(snapshot_file)
                if not isinstance(item, dict):
                    continue
                entries.append({
                    "project_id": str(item.get("project_id", snapshot_file.parent.name)),
                    "name": str(item.get("name", snapshot_file.parent.name)),
                    "phase": str(item.get("phase", "unknown")),
                    "location": str(snapshot_file.parent.relative_to(PROJECTS.parent)).replace("\\", "/"),
                    "archived": "true" if archived else "false",
                })
            except (OSError, ValueError):
                continue
    index_path = PROJECTS / "index.yaml"
    write_yaml_atomic(index_path, {"generated_at": now_utc(), "projects": entries})
    return entries


def initialize_project(project_id: str, name: str, kind: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", project_id):
        raise ValueError("project_id 需以小写字母或数字开头，只能包含小写字母、数字、_ 和 -")
    if kind not in {"knowledge", "account_intro", "legacy_media"}:
        raise ValueError(f"不支持的项目类型：{kind}")
    destination = project_dir(project_id)
    if destination.exists() or project_dir(project_id, archived=True).exists():
        raise FileExistsError(f"项目或同名归档已存在：{project_id}")
    destination.mkdir(parents=True)
    snapshot = deepcopy(read_yaml(ROOT / "contracts" / "examples" / "minimal-project.yaml"))
    brief = deepcopy(read_yaml(ROOT / "contracts" / "examples" / "minimal-brief.yaml"))
    snapshot["project_id"] = brief["project_id"] = project_id
    snapshot["name"] = name
    snapshot["kind"] = kind
    snapshot["updated_at"] = now_utc()
    snapshot["phase"] = "ideation" if kind == "knowledge" else "introduction" if kind == "account_intro" else "legacy_media"
    snapshot["core_status"] = "not_applicable" if kind == "account_intro" else "missing"
    if kind == "account_intro":
        snapshot["todo"] = ["confirm-account-facts"]
    elif kind == "legacy_media":
        snapshot["todo"] = ["review-existing-media"]
    validate_record(brief)
    write_yaml_atomic(destination / "brief.yaml", brief)
    save_snapshot(project_id, snapshot)
    return destination


def stale_references(project_id: str, *, archived: bool = False) -> list[dict[str, str]]:
    """Find project artifacts whose referenced input digest no longer matches."""
    root = project_dir(project_id, archived=archived)
    stale: list[dict[str, str]] = []

    def visit(value: Any, record_path: str) -> None:
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                ref_path = value["path"]
                try:
                    artifact = project_file(project_id, ref_path, archived=archived)
                    if not artifact.is_file():
                        stale.append({"record": record_path, "path": ref_path, "reason": "missing"})
                    elif sha256_file(artifact) != value["sha256"]:
                        stale.append({"record": record_path, "path": ref_path, "reason": "digest_changed"})
                except ValueError as exc:
                    stale.append({"record": record_path, "path": ref_path, "reason": str(exc)})
                return
            for child in value.values():
                visit(child, record_path)
        elif isinstance(value, list):
            for child in value:
                visit(child, record_path)

    for path in sorted(root.rglob("*.yaml")) + sorted(root.rglob("*.yml")):
        try:
            visit(read_yaml(path), str(path.relative_to(root)).replace("\\", "/"))
        except (OSError, ValueError):
            continue
    return stale


def require_passing_review(project_id: str, artifact_path: str, digest: str) -> dict[str, Any]:
    """Require the newest independent report for this exact artifact version to pass."""
    from pathlib import PurePosixPath

    parts = PurePosixPath(artifact_path.replace("\\", "/")).parts
    try:
        target_index = parts.index("channels") + 1
        target_id = parts[target_index]
    except (ValueError, IndexError):
        raise ValueError("交付产物路径必须位于 channels/<target>/ 下")
    review_dir = project_file(project_id, f"channels/{target_id}/review")
    reports = []
    if review_dir.exists():
        for path in review_dir.glob("*.yaml"):
            report = read_yaml(path)
            validate_record(report)
            if report.get("project_id") != project_id or report.get("target_id") != target_id:
                raise ValueError(f"审阅报告身份错误：{path.name}")
            reviewed = [ref for ref in report.get("reviewed_refs", []) if ref.get("path") == artifact_path]
            if any(ref.get("sha256") == digest for ref in reviewed):
                reports.append((path.stat().st_mtime_ns, path.name, report))
    if not reports:
        raise ValueError("没有审阅当前交付文件指纹的ReviewReport")
    _, report_name, latest = max(reports, key=lambda item: (item[0], item[1]))
    blockers = [item.get("issue_id") for item in latest.get("findings", []) if item.get("blocking") and item.get("resolution") == "open"]
    if not latest.get("independent"):
        raise ValueError("当前ReviewReport不是独立审阅")
    if latest.get("conclusion") != "pass" or blockers:
        raise ValueError(f"最新审阅 {report_name} 未通过或仍有阻断问题：{', '.join(blockers)}")
    return latest
