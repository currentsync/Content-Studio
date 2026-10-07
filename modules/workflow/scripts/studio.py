"""Small Agent-facing CLI; Workflow alone writes project snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contracts.io import read_yaml, sha256_file, write_yaml_atomic  # noqa: E402
from modules.workflow.scripts.paths import ARCHIVE, PROJECTS, RUNTIME, project_dir, project_file  # noqa: E402
from modules.workflow.scripts.project_store import (  # noqa: E402
    initialize_project,
    load_snapshot,
    rebuild_index,
    save_snapshot,
    stale_references,
    require_passing_review,
    validate_snapshot,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _append_run(entry: dict[str, Any]) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    references = entry.get("inputs", [])
    detail = str(entry.get("detail", ""))
    if references:
        suffix = "inputs=" + ",".join(f"{ref['path']}#{ref['sha256']}" for ref in references)
        detail = f"{detail}; {suffix}" if detail else suffix
    outputs = [item["path"] if isinstance(item, dict) else str(item) for item in entry.get("outputs", [])]
    normalized = {
        "time": entry["time"],
        "project_id": entry["project_id"],
        "workflow": entry["workflow"],
        "result": entry["result"],
        "detail": detail,
        "outputs": outputs,
    }
    with (RUNTIME / "runs.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(normalized, ensure_ascii=False) + "\n")


def _reference(project_id: str, value: str) -> dict[str, str]:
    path = project_file(project_id, value)
    if not path.is_file():
        raise FileNotFoundError(f"项目产物不存在：{value}")
    return {"path": value.replace("\\", "/"), "sha256": sha256_file(path)}


def cmd_status(args: argparse.Namespace) -> int:
    snapshot = load_snapshot(args.project, archived=args.archived)
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    path = initialize_project(args.project, args.name, args.kind)
    print(json.dumps({"created": True, "project_id": args.project, "path": str(path.relative_to(ROOT)).replace("\\", "/")}, ensure_ascii=False))
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    snapshot = load_snapshot(args.project, archived=args.archived)
    waiting = snapshot.get("waiting_for_user")
    todo = snapshot.get("todo", [])
    if waiting:
        print(json.dumps({"project_id": args.project, "status": "blocked", "waiting_for_user": waiting}, ensure_ascii=False))
    elif stale := stale_references(args.project, archived=args.archived):
        print(json.dumps({"project_id": args.project, "status": "needs_revision", "stale_references": stale, "next": "重新生成受影响产物并复核其下游审阅"}, ensure_ascii=False))
    elif todo:
        step_id = todo[0]
        step = read_yaml(ROOT / "modules" / "workflow" / "config" / "workflows.yaml").get("steps", {}).get(step_id, {})
        payload = {
            "project_id": args.project,
            "target_id": args.target,
            "status": "ready",
            "next": step_id,
            "owner": step.get("owner"),
            "skill": step.get("skill"),
            "requires": step.get("requires", []),
            "input_refs": snapshot.get("current", {}),
        }
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(json.dumps({"project_id": args.project, "status": "no_pending_work"}, ensure_ascii=False))
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    snapshot = load_snapshot(args.project, archived=args.archived)
    output_refs = [_reference(args.project, value) for value in args.output]
    input_refs = [_reference(args.project, value) for value in args.input]
    if args.result in {"blocked", "failed"} and not args.detail:
        raise ValueError("blocked/failed 结果必须提供 --detail")
    if args.result == "succeeded" and not output_refs:
        raise ValueError("succeeded 结果必须至少提供一个项目内 --output")

    entry = {
        "time": _now(),
        "project_id": args.project,
        "workflow": args.operation,
        "result": args.result,
        "detail": args.detail or "",
        "inputs": input_refs,
        "outputs": output_refs,
    }
    if args.result in {"succeeded", "no_op"}:
        snapshot.setdefault("completed", [])
        if args.operation not in snapshot["completed"]:
            snapshot["completed"].append(args.operation)
        if args.operation in snapshot.get("todo", []):
            snapshot["todo"].remove(args.operation)
        if output_refs:
            snapshot.setdefault("current", {})[args.operation] = output_refs[-1]["path"]
        snapshot["waiting_for_user"] = None
    elif args.result == "blocked":
        snapshot["waiting_for_user"] = args.detail
    save_snapshot(args.project, snapshot, archived=args.archived)
    _append_run(entry)
    print(json.dumps({"recorded": True, "project_id": args.project, "result": args.result}, ensure_ascii=False))
    return 0


def cmd_confirm(args: argparse.Namespace) -> int:
    snapshot = load_snapshot(args.project, archived=args.archived)
    if not re.fullmatch(r"[a-f0-9]{64}", args.sha256):
        raise ValueError("--sha256 必须是64位小写十六进制")
    ref = _reference(args.project, args.artifact)
    if ref["sha256"] != args.sha256:
        raise ValueError("文件指纹与确认指纹不一致")
    if args.kind in {"delivery", "complete"}:
        require_passing_review(args.project, args.artifact, ref["sha256"])
    if args.kind == "complete":
        delivery = next((item for item in snapshot.get("approvals", []) if item.get("kind") == "delivery"), None)
        if not delivery:
            raise ValueError("complete approval requires a prior delivery approval")
        delivery_ref = delivery.get("artifact", {})
        if delivery_ref.get("path") != args.artifact or delivery_ref.get("sha256") != ref["sha256"]:
            raise ValueError("complete approval must reference the exact delivered artifact version")
    if not args.evidence.strip():
        raise ValueError("必须记录可核对的真实用户确认依据")
    approvals = snapshot.setdefault("approvals", [])
    approvals = [item for item in approvals if not (item.get("kind") == args.kind and item.get("artifact", {}).get("path") == args.artifact)]
    if args.kind == "delivery":
        approvals = [item for item in approvals if item.get("kind") != "complete" or (item.get("artifact", {}).get("path") == args.artifact and item.get("artifact", {}).get("sha256") == ref["sha256"])]
    approvals.append({"kind": args.kind, "artifact": {"artifact_id": Path(args.artifact).stem, **ref}, "evidence": args.evidence.strip()})
    snapshot["approvals"] = approvals
    save_snapshot(args.project, snapshot, archived=args.archived)
    _append_run({"time": _now(), "project_id": args.project, "workflow": "confirm", "result": "succeeded", "detail": f"{args.kind}: {args.artifact}"})
    print(json.dumps({"confirmed": True, "project_id": args.project, "kind": args.kind}, ensure_ascii=False))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    if args.project:
        snapshots = [(args.project, args.archived)]
    else:
        snapshots = []
        for root, archived in ((PROJECTS, False), (ARCHIVE, True)):
            if root.exists():
                snapshots.extend((item.parent.name, archived) for item in root.glob("*/project.yaml"))
    errors = []
    for project_id, archived in snapshots:
        try:
            validate_snapshot(load_snapshot(project_id, archived=archived))
            errors.extend({"project_id": project_id, **item} for item in stale_references(project_id, archived=archived))
        except (OSError, ValueError) as exc:
            errors.append({"project_id": project_id, "error": str(exc)})
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "projects_checked": len(snapshots)}, ensure_ascii=False))
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    snapshot = load_snapshot(args.project)
    if snapshot.get("todo") or snapshot.get("waiting_for_user"):
        raise ValueError("项目仍有待办或等待确认，不能归档")
    required = {"delivery", "complete"}
    approvals = {item.get("kind"): item for item in snapshot.get("approvals", [])}
    if not required.issubset(approvals):
        raise ValueError("归档需要实际的 delivery 与 complete 确认")
    delivery_ref = approvals["delivery"].get("artifact", {})
    complete_ref = approvals["complete"].get("artifact", {})
    if (complete_ref.get("path"), complete_ref.get("sha256")) != (delivery_ref.get("path"), delivery_ref.get("sha256")):
        raise ValueError("complete approval must match the current delivery artifact version")
    actual_ref = _reference(args.project, delivery_ref.get("path", ""))
    if actual_ref["sha256"] != delivery_ref.get("sha256"):
        raise ValueError("delivery approval artifact has changed since confirmation")
    require_passing_review(args.project, delivery_ref["path"], actual_ref["sha256"])
    source = project_dir(args.project)
    target = project_dir(args.project, archived=True)
    if target.exists():
        raise FileExistsError(f"归档目标已存在：{target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    rebuild_index()
    _append_run({"time": _now(), "project_id": args.project, "workflow": "archive-project", "result": "succeeded", "outputs": [str(target.relative_to(ROOT)).replace("\\", "/")]})
    print(json.dumps({"archived": True, "project_id": args.project}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="studio.py", description="Content Studio Workflow 命令入口")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="从最小模板创建项目")
    init.add_argument("--project", required=True)
    init.add_argument("--name", required=True)
    init.add_argument("--kind", choices=("knowledge", "account_intro", "legacy_media"), default="knowledge")
    init.set_defaults(func=cmd_init)

    status = commands.add_parser("status", help="读取项目快照")
    status.add_argument("--project", required=True)
    status.add_argument("--archived", action="store_true")
    status.set_defaults(func=cmd_status)

    next_cmd = commands.add_parser("next", help="显示下一步或阻塞")
    next_cmd.add_argument("--project", required=True)
    next_cmd.add_argument("--target")
    next_cmd.add_argument("--archived", action="store_true")
    next_cmd.set_defaults(func=cmd_next)

    record = commands.add_parser("record", help="登记执行结果并更新唯一项目快照")
    record.add_argument("--project", required=True)
    record.add_argument("--operation", required=True)
    record.add_argument("--result", choices=("succeeded", "no_op", "blocked", "failed"), required=True)
    record.add_argument("--output", action="append", default=[])
    record.add_argument("--input", action="append", default=[])
    record.add_argument("--detail", default="")
    record.add_argument("--archived", action="store_true")
    record.set_defaults(func=cmd_record)

    confirm = commands.add_parser("confirm", help="记录用户对具体文件指纹的真实确认")
    confirm.add_argument("--project", required=True)
    confirm.add_argument("--kind", choices=("core", "base_shell", "channel_shell", "packaging", "script", "direction", "delivery", "complete"), required=True)
    confirm.add_argument("--artifact", required=True)
    confirm.add_argument("--sha256", required=True)
    confirm.add_argument("--evidence", required=True)
    confirm.add_argument("--archived", action="store_true")
    confirm.set_defaults(func=cmd_confirm)

    check = commands.add_parser("check", help="检查项目快照结构")
    check.add_argument("--project")
    check.add_argument("--archived", action="store_true")
    check.set_defaults(func=cmd_check)

    archive = commands.add_parser("archive", help="在确认完整后归档项目")
    archive.add_argument("--project", required=True)
    archive.set_defaults(func=cmd_archive)

    rebuild = commands.add_parser("rebuild-index", help="从项目快照重建索引")
    rebuild.set_defaults(func=lambda _args: print(json.dumps({"projects": rebuild_index()}, ensure_ascii=False)) or 0)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except (OSError, ValueError, KeyError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
