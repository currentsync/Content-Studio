"""Small ffprobe and project artifact helpers shared by media commands."""

from __future__ import annotations

import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

from contracts.io import sha256_file
from modules.workflow.scripts.paths import project_file


def probe_media(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-count_frames", "-show_entries",
            "format=duration,format_name:stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,nb_read_frames,duration",
            "-of", "json", str(path),
        ],
        check=True, capture_output=True, text=True,
    )
    document = json.loads(result.stdout)
    streams = document.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    if not video:
        raise ValueError(f"媒体没有视频流：{path}")
    fps_value = video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"
    fps = float(Fraction(fps_value))
    if fps <= 0:
        raise ValueError(f"视频帧率无效：{path}")
    frame_value = video.get("nb_read_frames")
    if not frame_value or frame_value == "N/A":
        raise ValueError(f"ffprobe 无法核对实际帧数：{path}")
    duration = float(document.get("format", {}).get("duration") or video.get("duration") or 0)
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": fps,
        "frame_count": int(frame_value),
        "duration": duration,
        "audio_present": any(item.get("codec_type") == "audio" for item in streams),
        "video_codec": video.get("codec_name"),
        "container": document.get("format", {}).get("format_name"),
    }


def resolve_artifact(project_id: str, ref: dict[str, str]) -> Path:
    path = project_file(project_id, ref["path"])
    if not path.is_file():
        raise FileNotFoundError(f"项目产物不存在：{ref['path']}")
    actual = sha256_file(path)
    if actual != ref["sha256"]:
        raise ValueError(f"项目产物指纹已变化：{ref['path']}")
    return path
