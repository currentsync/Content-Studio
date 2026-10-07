"""Check a Timing record against the actual narration file and emit SRT captions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contracts.io import read_yaml, sha256_file
from modules.workflow.scripts.paths import project_dir, project_file
from modules.workflow.scripts.project_store import validate_record


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(json.loads(result.stdout)["format"]["duration"])
    if duration <= 0:
        raise ValueError("音频时长必须大于0")
    return duration


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    whole, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole:02d},{millis:03d}"


def make_captions(timing: dict, duration: float) -> list[tuple[float, float, str]]:
    precision = timing["precision"]
    captions = []
    previous_end = 0.0
    for segment in timing["segments"]:
        start, end = float(segment["start"]), float(segment["end"])
        if not (0 <= start < end <= duration + 0.02):
            raise ValueError(f"时间段 {segment['segment_id']} 超出实际音频：{start}–{end}s，音频 {duration:.3f}s")
        if start < previous_end - 0.001:
            raise ValueError(f"时间段 {segment['segment_id']} 与前一段重叠或时间倒退")
        previous_end = end
        anchors = segment.get("anchors", [])
        if precision in {"word", "character"} and not anchors:
            raise ValueError(f"{precision} 级 Timing 的时间段 {segment['segment_id']} 缺少精确锚，不能退化成段级字幕")
        if precision in {"word", "character", "manual"} and anchors:
            for anchor in anchors:
                a_start, a_end = float(anchor["start"]), float(anchor["end"])
                text = anchor.get("text")
                if not text:
                    raise ValueError(f"精确字幕锚 {anchor['anchor_id']} 缺少文本")
                if not (start <= a_start < a_end <= end):
                    raise ValueError(f"锚 {anchor['anchor_id']} 未落在所属时间段内")
                captions.append((a_start, a_end, text))
        else:
            text = segment.get("text")
            if not text:
                raise ValueError(f"时间段 {segment['segment_id']} 缺少字幕文本")
            captions.append((start, end, text))
    captions.sort(key=lambda item: (item[0], item[1]))
    for previous, current in zip(captions, captions[1:]):
        if current[0] < previous[1] - 0.001:
            raise ValueError("字幕时间锚重叠；请修订 timing 后再生成")
    return captions


def main() -> int:
    parser = argparse.ArgumentParser(description="核对项目音频与Timing，并生成SRT字幕")
    parser.add_argument("--project", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--audio", required=True, help="项目内相对路径")
    parser.add_argument("--timing", required=True, help="项目内Timing YAML相对路径")
    parser.add_argument("--out", help="项目内SRT路径；默认写入对应频道production/subtitles.srt")
    args = parser.parse_args()
    try:
        project_root = project_dir(args.project)
        audio_path = project_file(args.project, args.audio)
        timing_path = project_file(args.project, args.timing)
        if not audio_path.is_file():
            raise FileNotFoundError(f"音频不存在：{args.audio}")
        timing = read_yaml(timing_path)
        validate_record(timing)
        if timing["project_id"] != args.project or timing["target_id"] != args.target:
            raise ValueError("Timing 的 project_id/target_id 与命令不匹配")
        if timing.get("audio_ref"):
            audio_ref = timing["audio_ref"]
            if audio_ref["path"] != args.audio or audio_ref["sha256"] != sha256_file(audio_path):
                raise ValueError("Timing audio_ref 与传入音频路径或SHA-256不匹配")
        script_ref = timing["script_ref"]
        script_path = project_file(args.project, script_ref["path"])
        if not script_path.is_file() or sha256_file(script_path) != script_ref["sha256"]:
            raise ValueError("Timing 所引用的制作稿缺失或指纹已变化")
        duration = probe_duration(audio_path)
        captions = make_captions(timing, duration)
        out_ref = args.out or f"channels/{args.target}/production/subtitles.srt"
        output_path = project_file(args.project, out_ref)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for index, (start, end, text) in enumerate(captions, 1):
            lines.extend((str(index), f"{srt_time(start)} --> {srt_time(end)}", text, ""))
        output_path.write_text("\n".join(lines), encoding="utf-8-sig", newline="\n")
        print(json.dumps({"ok": True, "audio_duration": round(duration, 3), "precision": timing["precision"], "caption_count": len(captions), "subtitle": str(output_path.relative_to(project_root)).replace("\\", "/")}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) and exc.stderr else str(exc)
        print(f"错误：{detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
