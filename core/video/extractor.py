from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from core.metadata.frames_csv import (
    FrameRecord,
    build_frame_filename,
    build_image_relpath,
)
from utils.ffmpeg_check import ensure_ffmpeg

_SHOWINFO_PATTERN = re.compile(r"pts_time:(?P<pts>[0-9.]+)")


@dataclass(frozen=True)
class ExtractRangeResult:
    records: list[FrameRecord]
    skipped: int


def extract_range_frames(
    project_dir: str | Path,
    video_path: str | Path,
    video_folder: str,
    video_id: str,
    src_video_path: str,
    start_ms: int,
    end_ms: int,
    fps: float,
    video_fps: float,
    ext: str = "jpg",
    ffmpeg_dir: Optional[Path] = None,
) -> ExtractRangeResult:
    ffmpeg_path, _ = ensure_ffmpeg(ffmpeg_dir)
    project_dir = Path(project_dir)
    ranges_dir = project_dir / "frames" / video_folder / "ranges"
    ranges_dir.mkdir(parents=True, exist_ok=True)

    start_s = max(start_ms, 0) / 1000.0
    end_s = max(end_ms, 0) / 1000.0
    if end_s <= start_s:
        return ExtractRangeResult(records=[], skipped=0)

    temp_dir = ranges_dir / ".tmp_extract"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    output_pattern = str(temp_dir / "frame_%07d.jpg")
    cmd = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "info",
        "-ss",
        f"{start_s}",
        "-to",
        f"{end_s}",
        "-i",
        str(video_path),
        "-vf",
        f"fps={fps},showinfo",
        "-q:v",
        "2",
        output_pattern,
    ]

    timestamps = _run_ffmpeg_with_timestamps(cmd)
    timestamps = _normalize_timestamps(timestamps, start_s)

    temp_files = sorted(temp_dir.glob("frame_*.jpg"))
    records: list[FrameRecord] = []
    skipped = 0

    for idx, temp_file in enumerate(temp_files):
        if idx < len(timestamps):
            ts_s = timestamps[idx]
        else:
            ts_s = start_s + (idx / max(fps, 1e-6))
        timestamp_ms = int(round(ts_s * 1000))
        frame_index = int(round((timestamp_ms / 1000.0) * video_fps))
        filename = build_frame_filename(timestamp_ms, frame_index, ext=ext)
        image_relpath = build_image_relpath(video_folder, "ranges", filename)
        output_path = project_dir / image_relpath

        if output_path.exists():
            skipped += 1
            temp_file.unlink(missing_ok=True)
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file.replace(output_path)
        records.append(
            FrameRecord.create(
                video_id=video_id,
                src_video_path=src_video_path,
                timestamp_ms=timestamp_ms,
                frame_index=frame_index,
                kind="range",
                image_relpath=image_relpath,
            )
        )

    shutil.rmtree(temp_dir, ignore_errors=True)
    return ExtractRangeResult(records=records, skipped=skipped)


def _run_ffmpeg_with_timestamps(cmd: Iterable[str]) -> list[float]:
    timestamps: list[float] = []
    process = subprocess.Popen(
        list(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert process.stderr is not None
    for line in process.stderr:
        match = _SHOWINFO_PATTERN.search(line)
        if match:
            timestamps.append(float(match.group("pts")))

    returncode = process.wait()
    if returncode != 0:
        raise RuntimeError("FFmpeg 抽帧失败")
    return timestamps


def _normalize_timestamps(timestamps: list[float], start_s: float) -> list[float]:
    if not timestamps:
        return timestamps
    if start_s <= 0:
        return timestamps
    if min(timestamps) < start_s * 0.5:
        return [ts + start_s for ts in timestamps]
    return timestamps
