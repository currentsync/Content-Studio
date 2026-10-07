"""Assemble ordered project clips with optional narration and soft subtitles."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contracts.io import read_yaml, sha256_file, write_yaml_atomic
from media_utils import probe_media, resolve_artifact
from modules.workflow.scripts.paths import project_file
from modules.workflow.scripts.project_store import load_snapshot, validate_record


def _artifact_id(path: str) -> str:
    stem = Path(path).stem.lower()
    normalized = "".join(ch if ch.isalnum() or ch in "_-" else "-" for ch in stem).strip("-_")
    return normalized or "media-output"


def assemble(request_path: Path) -> dict:
    request = read_yaml(request_path)
    validate_record(request)
    if request["operation"] != "assemble":
        raise ValueError("ProductionRequest.operation 必须为 assemble")
    project_id, target_id = request["project_id"], request["target_id"]
    project_root = project_file(project_id, "").resolve()
    if not request_path.resolve().is_relative_to(project_root):
        raise ValueError("ProductionRequest 必须位于对应项目目录内")
    native_ref = request["native_input"]
    plan_path = resolve_artifact(project_id, native_ref)
    plan = read_yaml(plan_path)
    if not isinstance(plan, dict) or plan.get("project_id") != project_id or plan.get("target_id") != target_id:
        raise ValueError("组装清单身份与 ProductionRequest 不一致")
    segments = plan.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError("组装清单至少需要一个按序排列的 segments")
    segment_paths = [resolve_artifact(project_id, ref) for ref in segments]
    facts = [probe_media(path) for path in segment_paths]
    reference = facts[0]
    for index, item in enumerate(facts[1:], 2):
        if (item["width"], item["height"], item["fps"]) != (reference["width"], reference["height"], reference["fps"]):
            raise ValueError(f"片段 {index} 尺寸或帧率不同；请由 Production 统一规格后再组装")
    video_duration = sum(item["frame_count"] / item["fps"] for item in facts)
    declared_duration = plan.get("duration")
    if declared_duration is not None and abs(float(declared_duration) - video_duration) > max(1 / reference["fps"], 0.03):
        raise ValueError(f"组装清单时长 {declared_duration}s 与实际帧时长 {video_duration:.3f}s 不一致")

    audio_ref = plan.get("audio_ref")
    if request["output"].get("narration") == "required" and not audio_ref:
        raise ValueError("ProductionRequest 要求口播，但组装清单未提供音频")
    audio_path = resolve_artifact(project_id, audio_ref) if audio_ref else None
    audio_duration = None
    if audio_path:
        audio_probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)],
            check=True, capture_output=True, text=True,
        )
        audio_duration = float(json.loads(audio_probe.stdout)["format"]["duration"])
    subtitle_ref = plan.get("subtitle_ref")
    subtitle_mode = request["output"].get("subtitles", "optional")
    if subtitle_mode == "required" and not subtitle_ref:
        raise ValueError("ProductionRequest requires subtitles, but the assembly plan has none")
    if subtitle_mode == "none" and subtitle_ref:
        raise ValueError("ProductionRequest forbids subtitles, but the assembly plan includes them")
    subtitle_path = resolve_artifact(project_id, subtitle_ref) if subtitle_ref else None

    expected = request["output"]
    for key, actual_value in (("width", reference["width"]), ("height", reference["height"])):
        if key in expected and expected[key] != actual_value:
            raise ValueError(f"Output {key}={actual_value} does not match requested {expected[key]}")
    if "fps" in expected and abs(float(expected["fps"]) - reference["fps"]) > 0.01:
        raise ValueError(f"Output fps={reference['fps']} does not match requested {expected['fps']}")
    if "duration_range_seconds" in expected:
        minimum, maximum = expected["duration_range_seconds"]
        if not float(minimum) <= video_duration <= float(maximum):
            raise ValueError(f"Video duration {video_duration:.3f}s is outside requested range {minimum}-{maximum}s")

    output_ref = request["output"].get("path")
    if not output_ref:
        raise ValueError("ProductionRequest.output.path 缺失")
    output_path = project_file(project_id, output_ref)
    if output_path.exists():
        raise FileExistsError(f"输出已存在，为保护已有候选版本停止覆盖：{output_ref}")
    snapshot = load_snapshot(project_id)
    approved = {item.get("artifact", {}).get("path") for item in snapshot.get("approvals", [])}
    if output_ref in approved:
        raise ValueError("组装目标指向已批准产物；请使用新的候选路径")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = project_file(project_id, f"channels/{target_id}/production/artifacts.yaml")
    if manifest_path.is_file():
        manifest = read_yaml(manifest_path)
        validate_record(manifest)
        if manifest["project_id"] != project_id or manifest["target_id"] != target_id:
            raise ValueError("现有ArtifactManifest的项目或渠道身份不匹配")
    else:
        manifest = {"record_type": "artifact_manifest", "schema_version": "1.0", "project_id": project_id, "target_id": target_id, "based_on": [], "artifacts": []}

    command = ["ffmpeg", "-n", "-v", "error"]
    for segment_path in segment_paths:
        command.extend(["-i", str(segment_path)])
    audio_index = len(segment_paths)
    if audio_path:
        command.extend(["-i", str(audio_path)])
    subtitle_index = audio_index + (1 if audio_path else 0)
    if subtitle_path:
        command.extend(["-i", str(subtitle_path)])

    if len(segment_paths) == 1:
        video_filter = "[0:v:0]null[vout]"
    else:
        streams = "".join(f"[{index}:v:0]" for index in range(len(segment_paths)))
        video_filter = f"{streams}concat=n={len(segment_paths)}:v=1:a=0[vout]"
    filters = [video_filter]
    if audio_path:
        filters.append(f"[{audio_index}:a:0]apad[aout]")
    command.extend(["-filter_complex", ";".join(filters)])
    command.extend(["-map", "[vout]"])
    if audio_path:
        command.extend(["-map", "[aout]"])
    if subtitle_path:
        command.extend(["-map", f"{subtitle_index}:s:0?", "-c:s", "mov_text"])
    command.extend([
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-r", str(reference["fps"]), "-t", f"{video_duration:.6f}", "-movflags", "+faststart",
    ])
    if audio_path:
        command.extend(["-c:a", "aac", "-b:a", "192k"])
    command.append(str(output_path))
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(result.stderr.strip() or "ffmpeg 组装失败")

    actual = probe_media(output_path)
    if abs(actual["duration"] - video_duration) > max(1 / reference["fps"], 0.03):
        output_path.unlink(missing_ok=True)
        raise ValueError(f"成片实际时长 {actual['duration']:.3f}s 与计划帧时长 {video_duration:.3f}s 不符")
    output_sha = sha256_file(output_path)
    media_ref = {"artifact_id": _artifact_id(output_ref), "path": output_ref.replace("\\", "/"), "sha256": output_sha}
    for ref in [native_ref, *segments, *([audio_ref] if audio_ref else []), *([subtitle_ref] if subtitle_ref else [])]:
        if ref not in manifest["based_on"]:
            manifest["based_on"].append(ref)
    manifest["artifacts"].append({
        "role": "assembled_candidate",
        "ref": media_ref,
        "media": {"kind": "video", "width": actual["width"], "height": actual["height"], "fps": actual["fps"], "frame_count": actual["frame_count"], "duration": actual["duration"], "audio_present": actual["audio_present"], "container": actual["container"]},
    })
    validate_record(manifest)
    write_yaml_atomic(manifest_path, manifest)
    return {
        "project_id": project_id,
        "target_id": target_id,
        "artifact": media_ref,
        "media": actual,
        "expected_video_duration": round(video_duration, 3),
        "audio_duration": None if audio_duration is None else round(audio_duration, 3),
        "audio_padded": bool(audio_path and audio_duration < video_duration - 0.02),
        "manifest": str(manifest_path.relative_to(project_root)).replace("\\", "/"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="按项目组装清单连接视频片段、口播和软字幕")
    parser.add_argument("--request", required=True, help="项目内ProductionRequest YAML")
    args = parser.parse_args()
    try:
        request_path = Path(args.request).resolve()
        output = assemble(request_path)
        print(json.dumps({"ok": True, **output}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) and exc.stderr else str(exc)
        print(f"错误：{detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
