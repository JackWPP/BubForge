from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QSlider,
    QVBoxLayout,
    QWidget,
    QStyleOptionSlider,
    QStyle,
)


class MarkedSlider(QSlider):
    def __init__(self, orientation: Qt.Orientation) -> None:
        super().__init__(orientation)
        self._in_value: int | None = None
        self._out_value: int | None = None

    def set_markers(self, in_value: int | None, out_value: int | None) -> None:
        self._in_value = in_value
        self._out_value = out_value
        self.update()

    def paintEvent(self, ev) -> None:
        super().paintEvent(ev)
        if self._in_value is None and self._out_value is None:
            return
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            option,
            QStyle.SubControl.SC_SliderGroove,
            self,
        )
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        def value_to_x(value: int) -> int:
            if self.maximum() == self.minimum():
                return groove.x()
            ratio = (value - self.minimum()) / (self.maximum() - self.minimum())
            return int(groove.x() + ratio * groove.width())

        if self._in_value is not None and self._out_value is not None:
            left = value_to_x(min(self._in_value, self._out_value))
            right = value_to_x(max(self._in_value, self._out_value))
            painter.fillRect(
                left,
                groove.y() + 1,
                max(right - left, 2),
                groove.height() - 2,
                QColor(96, 142, 255, 80),
            )

        def draw_marker(value: int, color: QColor) -> None:
            x = value_to_x(value)
            y = groove.y() - 2
            path = QPainterPath()
            path.moveTo(x, y)
            path.lineTo(x - 5, y - 8)
            path.lineTo(x + 5, y - 8)
            path.closeSubpath()
            painter.fillPath(path, color)

        if self._in_value is not None:
            draw_marker(self._in_value, QColor(88, 201, 131))
        if self._out_value is not None:
            draw_marker(self._out_value, QColor(240, 98, 98))


class TimelineWidget(QWidget):
    positionChanged = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._fps = 0.0
        self._total_frames = 0
        self._in_ms: int | None = None
        self._out_ms: int | None = None

        self.slider = MarkedSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("TimelineSlider")
        self.slider.setRange(0, 0)
        self.slider.valueChanged.connect(self._emit_position)

        self.label_current = QLabel("00:00.000 / 00:00.000")
        self.label_in = QLabel("In: --")
        self.label_out = QLabel("Out: --")
        self.label_frame = QLabel("f0 / f0")

        meta_layout = QHBoxLayout()
        meta_layout.addWidget(self.label_current)
        meta_layout.addStretch(1)
        meta_layout.addWidget(self.label_in)
        meta_layout.addSpacing(12)
        meta_layout.addWidget(self.label_out)
        meta_layout.addSpacing(12)
        meta_layout.addWidget(self.label_frame)

        layout = QVBoxLayout(self)
        layout.addWidget(self.slider)
        layout.addLayout(meta_layout)

    def set_video_info(self, total_frames: int, fps: float) -> None:
        self._total_frames = max(total_frames, 0)
        self._fps = max(fps, 0.0)
        max_value = max(self._total_frames - 1, 0)
        self.slider.setRange(0, max_value)
        self._update_labels(self.slider.value())

    def set_position(self, frame_index: int) -> None:
        if frame_index != self.slider.value():
            self.slider.blockSignals(True)
            self.slider.setValue(frame_index)
            self.slider.blockSignals(False)
        self._update_labels(frame_index)

    def set_in_out(self, in_ms: int | None, out_ms: int | None) -> None:
        self._in_ms = in_ms
        self._out_ms = out_ms
        self.slider.set_markers(
            None if in_ms is None else self._ms_to_frame(in_ms),
            None if out_ms is None else self._ms_to_frame(out_ms),
        )
        self.label_in.setText(
            "In: --" if in_ms is None else f"In: {self._format_time(in_ms)}"
        )
        self.label_out.setText(
            "Out: --" if out_ms is None else f"Out: {self._format_time(out_ms)}"
        )

    def _emit_position(self, frame_index: int) -> None:
        self._update_labels(frame_index)
        self.positionChanged.emit(frame_index)

    def _frame_to_ms(self, frame_index: int) -> int:
        if self._fps <= 0:
            return 0
        return int(round((frame_index / self._fps) * 1000))

    def _ms_to_frame(self, timestamp_ms: int) -> int:
        if self._fps <= 0:
            return 0
        return int(round((timestamp_ms / 1000.0) * self._fps))

    def _update_labels(self, frame_index: int) -> None:
        current_ms = self._frame_to_ms(frame_index)
        total_ms = self._frame_to_ms(max(self._total_frames - 1, 0))
        self.label_current.setText(
            f"{self._format_time(current_ms)} / {self._format_time(total_ms)}"
        )
        self.label_frame.setText(f"f{frame_index} / f{max(self._total_frames - 1, 0)}")

    @staticmethod
    def _format_time(timestamp_ms: int) -> str:
        total_seconds = max(timestamp_ms, 0) / 1000.0
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"
