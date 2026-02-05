from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QVBoxLayout, QWidget


class SelectionPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.keyframes_list = QListWidget()
        self.ranges_list = QListWidget()

        keyframes_layout = QVBoxLayout()
        keyframes_layout.addWidget(QLabel("关键帧"))
        keyframes_layout.addWidget(self.keyframes_list)

        ranges_layout = QVBoxLayout()
        ranges_layout.addWidget(QLabel("区间"))
        ranges_layout.addWidget(self.ranges_list)

        layout = QHBoxLayout(self)
        layout.addLayout(keyframes_layout)
        layout.addLayout(ranges_layout)

    def add_keyframe(self, label: str) -> None:
        self.keyframes_list.addItem(label)

    def add_range(self, label: str) -> None:
        self.ranges_list.addItem(label)
