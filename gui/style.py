from __future__ import annotations


def app_stylesheet() -> str:
    return """
QWidget {
    background-color: #0f1115;
    color: #e7e7e7;
    font-family: "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 13px;
}

QLabel#TitleLabel {
    font-size: 20px;
    font-weight: 600;
}

QFrame#Card {
    background-color: #151922;
    border-radius: 12px;
    border: 1px solid #242a36;
}

QPushButton {
    background-color: #3f6bff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
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

QSlider::sub-page:horizontal {
    background: #2f4fb8;
    border-radius: 3px;
}
"""
