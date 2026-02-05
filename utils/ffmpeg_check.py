from __future__ import annotations

from pathlib import Path
import shutil
from typing import Optional, Tuple


def find_ffmpeg(
    custom_dir: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[str]]:
    ffmpeg_name = "ffmpeg.exe"
    ffprobe_name = "ffprobe.exe"

    if custom_dir:
        ffmpeg_path = custom_dir / ffmpeg_name
        ffprobe_path = custom_dir / ffprobe_name
        if ffmpeg_path.exists() and ffprobe_path.exists():
            return str(ffmpeg_path), str(ffprobe_path)

    ffmpeg_path = shutil.which(ffmpeg_name) or shutil.which("ffmpeg")
    ffprobe_path = shutil.which(ffprobe_name) or shutil.which("ffprobe")
    return ffmpeg_path, ffprobe_path


def ensure_ffmpeg(custom_dir: Optional[Path] = None) -> Tuple[str, str]:
    ffmpeg_path, ffprobe_path = find_ffmpeg(custom_dir)
    if not ffmpeg_path or not ffprobe_path:
        raise FileNotFoundError("未找到 ffmpeg/ffprobe，可在设置中配置路径")
    return ffmpeg_path, ffprobe_path
