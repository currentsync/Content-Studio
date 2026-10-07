"""Validate a CreativePlan, its project references, selected style and asset permissions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml
from jsonschema import Draft202012Validator

from contracts.io import read_yaml, sha256_file
from modules.workflow.scripts.paths import project_file
from modules.workflow.scripts.project_store import validate_record


def validate(project_id: str, plan_ref: str) -> list[str]:
    plan_path = project_file(project_id, plan_ref)
    plan = read_yaml(plan_path)
    schema_path = ROOT / "modules" / "creative" / "schemas" / "creative-plan.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(plan), key=lambda err: tuple(map(str, err.absolute_path)))
    findings = []
    for error in errors:
        location = ".".join(map(str, error.absolute_path)) or "plan"
        findings.append(f"{location}: {error.message}")
    if errors:
        return findings
    if plan["project_id"] != project_id:
        findings.append("project_id 与当前项目不匹配")

    style_index = read_yaml(ROOT / "modules" / "creative" / "styles" / "index.yaml")
    usable_styles = {item["id"] for item in style_index.get("clip_grammars", []) if item.get("status") == "usable"}
    usable_styles.update(f"scene:{path.stem}" for path in (ROOT / "modules" / "creative" / "canvas" / "scenes").glob("*.js"))
    if plan["style_id"] not in usable_styles:
        findings.append(f"style_id 未登记为可用风格：{plan['style_id']}")

    refs = [(plan["based_on_script"], False)]
    for unit in plan["units"]:
        refs.extend((ref, False) for ref in unit["content_refs"])
        refs.extend((ref, True) for ref in unit["asset_refs"])
    assets_path = project_file(project_id, "assets/manifest.yaml")
    asset_manifest = read_yaml(assets_path) if assets_path.is_file() else {}
    if asset_manifest:
        validate_record(asset_manifest)
        if asset_manifest.get("project_id") != project_id:
            findings.append("素材清单 project_id 与当前项目不匹配")
    assets = asset_manifest.get("assets", []) if isinstance(asset_manifest, dict) else []

    for ref, is_asset in refs:
        try:
            artifact_path = project_file(project_id, ref["path"])
            if not artifact_path.is_file():
                findings.append(f"引用产物不存在：{ref['path']}")
                continue
            if sha256_file(artifact_path) != ref["sha256"]:
                findings.append(f"引用产物指纹已变化：{ref['path']}")
            if is_asset:
                matches = [item for item in assets if isinstance(item, dict) and item.get("ref", {}).get("path") == ref["path"]]
                if len(matches) != 1:
                    findings.append(f"素材 {ref['path']} 在 assets/manifest.yaml 中必须有且仅有一条记录")
                elif matches[0].get("allowed_usage") != "production":
                    findings.append(f"素材 {ref['path']} 的 allowed_usage 为 {matches[0].get('allowed_usage', 'unknown')}，不能进入正式制作")
        except (ValueError, KeyError) as exc:
            findings.append(f"无效产物引用：{exc}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 CreativePlan 结构、来源与正式素材用途")
    parser.add_argument("--project", required=True)
    parser.add_argument("--plan", required=True, help="项目内相对路径")
    args = parser.parse_args()
    try:
        findings = validate(args.project, args.plan)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    if findings:
        print(json.dumps({"ok": False, "findings": findings}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "project_id": args.project, "plan": args.plan}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
