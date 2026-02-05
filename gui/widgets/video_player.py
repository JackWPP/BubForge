from __future__ import annotations

from typing import Optional

import cv2
import numpy as np
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel


class VideoPlayerWidget(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(320)
        self._last_frame: Optional[np.ndarray] = None
        self._scale_mode = "fit"
        self._zoom_factor = 1.0
        self._viewport_size: Optional[QSize] = None

    def set_frame(self, frame: np.ndarray) -> None:
        self._last_frame = frame
        self._render_frame()

    def set_viewport_size(self, size: QSize) -> None:
        if size.isEmpty():
            return
        self._viewport_size = size
        if self._last_frame is not None:
            self._render_frame()

    def set_scale_mode(self, mode: str) -> None:
        self._scale_mode = mode
        if self._last_frame is not None:
            self._render_frame()

    def set_zoom_factor(self, factor: float) -> None:
        self._zoom_factor = max(factor, 0.1)
        if self._last_frame is not None:
            self._render_frame()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._last_frame is not None:
            self._render_frame()

    def _render_frame(self) -> None:
        if self._last_frame is None:
            return
        rgb_frame = cv2.cvtColor(self._last_frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width
        image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(image)
        target_size = self._compute_target_size(width, height)
        scaled = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
        self.setFixedSize(scaled.size())

    def _compute_target_size(self, width: int, height: int) -> QSize:
        if self._scale_mode == "fit" and self._viewport_size:
            scale = min(
                self._viewport_size.width() / max(width, 1),
                self._viewport_size.height() / max(height, 1),
            )
            scale = max(scale, 0.1)
            return QSize(int(width * scale), int(height * scale))
        if self._scale_mode == "zoom":
            return QSize(
                int(width * self._zoom_factor), int(height * self._zoom_factor)
            )
        return QSize(width, height)
