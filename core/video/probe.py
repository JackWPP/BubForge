from __future__ import annotations

from dataclasses import dataclass
import json
import subprocess
from pathlib import Path
from typing import Optional

from utils.ffmpeg_check import ensure_ffmpeg


@dataclass(frozen=True)
class VideoProbe:
    video_path: str
    duration_s: float
    fps: float
    width: int
    height: int
    total_frames: int


def probe_video(
    video_path: str | Path, ffprobe_path: Optional[str] = None
) -> VideoProbe:
    ffprobe, _ = ensure_ffmpeg(
        custom_dir=None if ffprobe_path is None else Path(ffprobe_path).parent
    )
    if ffprobe_path is not None:
        ffprobe = ffprobe_path

    cmd = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,avg_frame_rate,r_frame_rate,nb_frames",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe 执行失败")

    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    if not streams:
        raise ValueError("未找到视频流")

    stream = streams[0]
    width = int(stream.get("width", 0))
    height = int(stream.get("height", 0))
    fps = _parse_fps(stream.get("avg_frame_rate") or stream.get("r_frame_rate"))
    duration_s = float(payload.get("format", {}).get("duration", 0.0))
    total_frames = _parse_total_frames(stream.get("nb_frames"), duration_s, fps)

    if width <= 0 or height <= 0 or fps <= 0 or duration_s <= 0:
        raise ValueError("视频元数据不完整")

    return VideoProbe(
        video_path=str(video_path),
        duration_s=duration_s,
        fps=fps,
        width=width,
        height=height,
        total_frames=total_frames,
    )


def _parse_fps(value: str | None) -> float:
    if not value:
        return 0.0
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        if float(denominator) == 0:
            return 0.0
        return float(numerator) / float(denominator)
    return float(value)


def _parse_total_frames(nb_frames: str | None, duration_s: float, fps: float) -> int:
    if nb_frames and nb_frames.isdigit():
        return int(nb_frames)
    if duration_s > 0 and fps > 0:
        return int(round(duration_s * fps))
    return 0
