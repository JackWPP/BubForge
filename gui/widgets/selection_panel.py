from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QTabWidget, QVBoxLayout, QWidget


class SelectionPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SidePanel")
        self.keyframes_list = QListWidget()
        self.ranges_list = QListWidget()

        tabs = QTabWidget()
        keyframe_tab = QWidget()
        keyframe_layout = QVBoxLayout(keyframe_tab)
        keyframe_layout.addWidget(self.keyframes_list)

        ranges_tab = QWidget()
        ranges_layout = QVBoxLayout(ranges_tab)
        ranges_layout.addWidget(self.ranges_list)

        tabs.addTab(keyframe_tab, "关键帧")
        tabs.addTab(ranges_tab, "区间")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)

    def add_keyframe(self, label: str) -> None:
        self.keyframes_list.addItem(label)

    def add_range(self, label: str) -> None:
        self.ranges_list.addItem(label)
