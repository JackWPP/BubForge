from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from core.metadata.frames_csv import (
    FrameRecord,
    build_frame_filename,
    build_image_relpath,
)


def save_keyframe(
    project_dir: str | Path,
    video_folder: str,
    video_id: str,
    src_video_path: str,
    timestamp_ms: int,
    frame_index: int,
    image: np.ndarray,
    ext: str = "jpg",
) -> Optional[FrameRecord]:
    filename = build_frame_filename(timestamp_ms, frame_index, ext=ext)
    image_relpath = build_image_relpath(video_folder, "keyframes", filename)
    output_path = Path(project_dir) / image_relpath
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        return None

    _write_image(output_path, image, ext)

    return FrameRecord.create(
        video_id=video_id,
        src_video_path=src_video_path,
        timestamp_ms=timestamp_ms,
        frame_index=frame_index,
        kind="keyframe",
        image_relpath=image_relpath,
    )


def _write_image(output_path: Path, image: np.ndarray, ext: str) -> None:
    if image is None or image.size == 0:
        raise RuntimeError("关键帧为空，无法写入")
    safe_image = np.ascontiguousarray(image)
    success = cv2.imwrite(str(output_path), safe_image)
    if success:
        return
    encoded = cv2.imencode(f".{ext}", safe_image)
    if not encoded[0]:
        raise RuntimeError("关键帧写入失败")
    output_path.write_bytes(encoded[1].tobytes())
