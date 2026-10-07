"""Create and validate version-bound independent ReviewReport records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contracts.io import read_yaml, sha256_file, write_yaml_atomic
from modules.workflow.scripts.paths import project_file
from modules.workflow.scripts.project_store import validate_record


def validate_report(project_id: str, target_id: str, report_ref: str) -> dict:
    report = read_yaml(project_file(project_id, report_ref))
    validate_record(report)
    if report["project_id"] != project_id or report["target_id"] != target_id:
        raise ValueError("ReviewReport project/target identity mismatch")
    if not report["independent"]:
        raise ValueError("Delivery review must be completed by an independent reviewer")
    stale = []
    for ref in report["reviewed_refs"]:
        artifact = project_file(project_id, ref["path"])
        if not artifact.is_file():
            stale.append({"path": ref["path"], "reason": "missing"})
        elif sha256_file(artifact) != ref["sha256"]:
            stale.append({"path": ref["path"], "reason": "digest_changed"})
    if stale:
        raise ValueError("ReviewReport references stale artifacts: " + json.dumps(stale, ensure_ascii=False))
    blockers = [item["issue_id"] for item in report["findings"] if item["blocking"] and item["resolution"] == "open"]
    if report["conclusion"] == "pass" and blockers:
        raise ValueError("Cannot pass while blocking findings remain open: " + ", ".join(blockers))
    if report["conclusion"] == "pass" and not report["reviewed_refs"]:
        raise ValueError("A passing report must reference inspected files")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a review draft or validate a completed ReviewReport")
    parser.add_argument("--project", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--report", help="Project-relative ReviewReport path (validation mode)")
    parser.add_argument("--create", action="store_true", help="Create a draft using actual artifact fingerprints")
    parser.add_argument("--artifact", action="append", default=[], help="Project-relative artifact path; repeatable")
    parser.add_argument("--review-id", help="Lowercase review identifier")
    parser.add_argument("--scope", action="append", default=[], help="Review scope; repeatable")
    args = parser.parse_args()
    try:
        if args.create:
            if not args.review_id or not args.artifact or not args.scope:
                raise ValueError("Create mode requires --review-id, at least one --artifact and --scope")
            refs = []
            for artifact_ref in args.artifact:
                artifact = project_file(args.project, artifact_ref)
                if not artifact.is_file():
                    raise FileNotFoundError(f"Review artifact does not exist: {artifact_ref}")
                refs.append({"artifact_id": artifact.stem, "path": artifact_ref.replace("\\", "/"), "sha256": sha256_file(artifact)})
            report = {
                "record_type": "review_report", "schema_version": "1.0",
                "project_id": args.project, "target_id": args.target,
                "review_id": args.review_id, "reviewed_refs": refs,
                "scope": args.scope, "findings": [],
                "conclusion": "blocked", "independent": False,
            }
            validate_record(report)
            output = project_file(args.project, f"channels/{args.target}/review/{args.review_id}.yaml")
            if output.exists():
                raise FileExistsError(f"Refusing to overwrite existing report: {output}")
            write_yaml_atomic(output, report)
            print(json.dumps({"created": True, "report": str(output), "reviewed_refs": refs}, ensure_ascii=False))
            return 0
        if not args.report:
            raise ValueError("Validation mode requires --report; use --create for a draft")
        report = validate_report(args.project, args.target, args.report)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "conclusion": report["conclusion"], "review_id": report["review_id"], "reviewed_refs": len(report["reviewed_refs"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
