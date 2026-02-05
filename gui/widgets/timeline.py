from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QHBoxLayout, QSlider, QVBoxLayout, QWidget


class TimelineWidget(QWidget):
    positionChanged = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._fps = 0.0
        self._total_frames = 0
        self._in_ms: int | None = None
        self._out_ms: int | None = None

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.valueChanged.connect(self._emit_position)

        self.label_current = QLabel("00:00.000")
        self.label_in = QLabel("In: --")
        self.label_out = QLabel("Out: --")

        meta_layout = QHBoxLayout()
        meta_layout.addWidget(self.label_current)
        meta_layout.addStretch(1)
        meta_layout.addWidget(self.label_in)
        meta_layout.addSpacing(12)
        meta_layout.addWidget(self.label_out)

        layout = QVBoxLayout(self)
        layout.addWidget(self.slider)
        layout.addLayout(meta_layout)

    def set_video_info(self, total_frames: int, fps: float) -> None:
        self._total_frames = max(total_frames, 0)
        self._fps = max(fps, 0.0)
        max_value = max(self._total_frames - 1, 0)
        self.slider.setRange(0, max_value)

    def set_position(self, frame_index: int) -> None:
        if frame_index != self.slider.value():
            self.slider.blockSignals(True)
            self.slider.setValue(frame_index)
            self.slider.blockSignals(False)
        self.label_current.setText(self._format_time(self._frame_to_ms(frame_index)))

    def set_in_out(self, in_ms: int | None, out_ms: int | None) -> None:
        self._in_ms = in_ms
        self._out_ms = out_ms
        self.label_in.setText(
            "In: --" if in_ms is None else f"In: {self._format_time(in_ms)}"
        )
        self.label_out.setText(
            "Out: --" if out_ms is None else f"Out: {self._format_time(out_ms)}"
        )

    def _emit_position(self, frame_index: int) -> None:
        self.label_current.setText(self._format_time(self._frame_to_ms(frame_index)))
        self.positionChanged.emit(frame_index)

    def _frame_to_ms(self, frame_index: int) -> int:
        if self._fps <= 0:
            return 0
        return int(round((frame_index / self._fps) * 1000))

    @staticmethod
    def _format_time(timestamp_ms: int) -> str:
        total_seconds = max(timestamp_ms, 0) / 1000.0
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"
