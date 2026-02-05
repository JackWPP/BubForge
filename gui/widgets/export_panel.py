from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ExportPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SidePanel")
        self.format_combo = QComboBox()
        self.format_combo.addItems(
            [
                "RawFrames + Metadata",
                "Ultralytics Skeleton",
                "COCO Skeleton",
            ]
        )

        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(0.1, 120.0)
        self.fps_spin.setValue(5.0)
        self.fps_spin.setSingleStep(0.5)
        self.fps_spin.setSuffix(" fps")

        self.export_button = QPushButton("开始导出")
        self.export_button.setObjectName("PrimaryButton")

        title = QLabel("导出")
        title.setObjectName("SectionTitle")

        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("格式"))
        format_row.addStretch(1)

        fps_row = QHBoxLayout()
        fps_row.addWidget(QLabel("区间 FPS"))
        fps_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addLayout(format_row)
        layout.addWidget(self.format_combo)
        layout.addSpacing(8)
        layout.addLayout(fps_row)
        layout.addWidget(self.fps_spin)
        layout.addStretch(1)
        layout.addWidget(self.export_button)

    def current_format(self) -> str:
        return self.format_combo.currentText()

    def current_fps(self) -> float:
        return float(self.fps_spin.value())
