"""Report measured media properties from ffprobe."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from media_utils import probe_media


def main() -> int:
    parser = argparse.ArgumentParser(description="读取实际媒体尺寸、帧数、时长和音轨")
    parser.add_argument("file", type=Path)
    parser.add_argument("--expected-duration", type=float)
    args = parser.parse_args()
    try:
        facts = probe_media(args.file)
        expected = args.expected_duration
        facts["duration_matches"] = None if expected is None else abs(facts["duration"] - expected) <= max(1 / facts["fps"], 0.02)
        print(json.dumps(facts, ensure_ascii=False, indent=2))
        return 0 if facts["duration_matches"] is not False else 1
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) and exc.stderr else str(exc)
        print(f"错误：{detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
