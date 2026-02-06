from __future__ import annotations


def app_stylesheet() -> str:
    return """
QWidget {
    background-color: #0f1115;
    color: #e7e7e7;
    font-family: "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0f1115;
}

QLabel#TitleLabel {
    font-size: 20px;
    font-weight: 600;
}

QLabel#Timecode {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 14px;
    font-weight: 600;
    color: #9fd0ff;
}

QLabel#Framecode {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    color: #9aa4b3;
}

QLabel#SectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: #cfd6e3;
}

QFrame#Card {
    background-color: #151922;
    border-radius: 12px;
    border: 1px solid #242a36;
}

QFrame#TopBar {
    background-color: #12161f;
    border-radius: 12px;
    border: 1px solid #242a36;
}

QFrame#ViewerFrame {
    background-color: #0c0f14;
    border-radius: 14px;
    border: 1px solid #1e2430;
}

QFrame#TransportBar {
    background-color: #121722;
    border-radius: 12px;
    border: 1px solid #242a36;
}

QFrame#TimelineBar {
    background-color: #11161f;
    border-radius: 12px;
    border: 1px solid #242a36;
}

QFrame#BottomSplit {
    background-color: #11161f;
    border-radius: 12px;
    border: 1px solid #242a36;
}

QWidget#SidePanel {
    background-color: #121722;
    border-radius: 10px;
}

QPushButton {
    background-color: #3f6bff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton#PrimaryButton {
    background-color: #3f6bff;
    border: 1px solid #2d4fc2;
}

QPushButton:hover {
    background-color: #5a83ff;
}

QPushButton:pressed {
    background-color: #2c55e6;
}

QPushButton:disabled {
    background-color: #2a2f3a;
    color: #7a7f8a;
}

QToolButton {
    background-color: #1f2430;
    color: #e7e7e7;
    border: 1px solid #2a3140;
    border-radius: 8px;
    padding: 6px 10px;
}

QScrollArea {
    border: none;
}

QToolButton:hover {
    border: 1px solid #3f6bff;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #1b202a;
    border: 1px solid #2a3140;
    border-radius: 8px;
    padding: 6px 10px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #3f6bff;
}

QListWidget {
    background-color: #12161d;
    border: 1px solid #242a36;
    border-radius: 8px;
}

QListWidget::item {
    padding: 6px 8px;
}

QListWidget::item:selected {
    background-color: #2b3547;
    color: #ffffff;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #1c2230;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #3f6bff;
    width: 14px;
    margin: -4px 0;
    border-radius: 7px;
}

QSlider#TimelineSlider::groove:horizontal {
    height: 10px;
    background: #1a2130;
    border-radius: 5px;
}

QSlider#TimelineSlider::handle:horizontal {
    background: #ff6b6b;
    width: 8px;
    margin: -6px 0;
    border-radius: 3px;
}

QScrollBar:vertical {
    background: #0f1115;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #2a3140;
    border-radius: 5px;
    min-height: 20px;
}

QSlider::sub-page:horizontal {
    background: #2f4fb8;
    border-radius: 3px;
}

QTabWidget::pane {
    border: 1px solid #242a36;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #151b24;
    color: #9aa4b3;
    padding: 8px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background-color: #1f2633;
    color: #ffffff;
}

QSplitter::handle {
    background-color: #1c2230;
}

QSplitter::handle:horizontal {
    width: 6px;
}

QSplitter::handle:vertical {
    height: 6px;
}

QDockWidget {
    background-color: #11161f;
    border: 1px solid #242a36;
    border-radius: 8px;
}

QDockWidget::title {
    text-align: left;
    background-color: #161c28;
    color: #d7dce5;
    padding: 6px 10px;
    border-bottom: 1px solid #242a36;
}

QDockWidget::close-button,
QDockWidget::float-button {
    border: none;
    background-color: #202a3b;
    border-radius: 4px;
}

QMenuBar {
    background-color: #0f1115;
    color: #d7dce5;
}

QMenuBar::item:selected {
    background-color: #1a2232;
}

QMenu {
    background-color: #121722;
    color: #d7dce5;
    border: 1px solid #242a36;
}

QMenu::item:selected {
    background-color: #24324b;
}
"""
