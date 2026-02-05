from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


@dataclass
class FrameData:
    frame_index: int
    timestamp_ms: int
    image: np.ndarray


class VideoCaptureController:
    def __init__(self) -> None:
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: float = 0.0
        self._total_frames: int = 0
        self._width: int = 0
        self._height: int = 0

    def open(self, video_path: str | Path) -> None:
        self.close()
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError("无法打开视频")
        self._cap = cap
        self._fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        self._total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        self._width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        self._height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def total_frames(self) -> int:
        return self._total_frames

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def read_next(self) -> Optional[FrameData]:
        if self._cap is None:
            return None
        ret, frame = self._cap.read()
        if not ret:
            return None
        frame_index = int(self._cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        timestamp_ms = int(round((frame_index / max(self._fps, 1e-6)) * 1000))
        return FrameData(
            frame_index=frame_index, timestamp_ms=timestamp_ms, image=frame
        )

    def get_frame_at(self, frame_index: int) -> Optional[FrameData]:
        if self._cap is None:
            return None
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        return self.read_next()

    def get_frame_at_ms(self, timestamp_ms: int) -> Optional[FrameData]:
        if self._cap is None:
            return None
        self._cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        return self.read_next()

    def current_position_ms(self) -> int:
        if self._cap is None:
            return 0
        pos = self._cap.get(cv2.CAP_PROP_POS_MSEC)
        return int(round(pos))
