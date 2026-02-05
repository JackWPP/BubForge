from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtGui import QAction, QKeySequence, QColor, QKeyEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QComboBox,
    QScrollArea,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
)

from core.export.registry import get_exporter
from core.metadata.frames_csv import append_frame_records
from core.project.manager import (
    ensure_video_subdirs,
    get_video_folder_name,
    init_project,
)
from core.project.sources import append_source, normalize_source_path
from core.video.capture import VideoCaptureController
from core.video.frame_writer import save_keyframe
from core.video.extractor import extract_range_frames
from gui.shortcuts import ShortcutMap
from gui.style import app_stylesheet
from gui.widgets.export_panel import ExportPanel
from gui.widgets.selection_panel import SelectionPanel
from gui.widgets.timeline import TimelineWidget
from gui.widgets.video_player import VideoPlayerWidget
from utils.ffmpeg_check import ensure_ffmpeg


@dataclass
class RangeEntry:
    in_ms: int
    out_ms: int


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BubForge")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(app_stylesheet())

        self.shortcut_map = ShortcutMap()
        self.capture = VideoCaptureController()
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._on_playback_tick)

        self.seek_timer = QTimer(self)
        self.seek_timer.timeout.connect(self._on_seek_tick)
        self.seek_direction = 0

        self.project_dir: Optional[Path] = None
        self.video_path: Optional[Path] = None
        self.video_id: Optional[str] = None
        self.video_folder: Optional[str] = None
        self.current_frame_index = 0
        self.current_timestamp_ms = 0
        self.in_ms: Optional[int] = None
        self.out_ms: Optional[int] = None
        self.ranges: list[RangeEntry] = []

        self._build_ui()
        self._build_menu()
        self._install_shortcut_actions()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = self._card_frame("TopBar")
        header_layout = QHBoxLayout(header)
        title = QLabel("BubForge · 视频帧提取")
        title.setObjectName("TitleLabel")
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        self.project_button = QToolButton()
        self.project_button.setText("选择项目")
        self.project_button.clicked.connect(self.pick_project)
        self.video_button = QToolButton()
        self.video_button.setText("打开视频")
        self.video_button.clicked.connect(self.open_video)
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["适配", "100%", "150%", "200%"])
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_changed)
        self.project_label = QLabel("项目：未选择")
        self.video_label = QLabel("视频：未加载")
        header_layout.addWidget(self.project_button)
        header_layout.addWidget(self.video_button)
        header_layout.addSpacing(8)
        header_layout.addWidget(QLabel("显示"))
        header_layout.addWidget(self.zoom_combo)
        header_layout.addSpacing(12)
        header_layout.addWidget(self.project_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.video_label)

        self.player = VideoPlayerWidget()
        player_frame = self._card_frame("ViewerFrame")
        player_layout = QVBoxLayout(player_frame)
        self.viewer_scroll = QScrollArea()
        self.viewer_scroll.setWidget(self.player)
        self.viewer_scroll.setWidgetResizable(False)
        self.viewer_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.viewer_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_layout.addWidget(self.viewer_scroll)

        controls_frame = self._card_frame("TransportBar")
        controls_layout = QHBoxLayout(controls_frame)
        self.play_button = QToolButton()
        self.play_button.setText("播放")
        self.play_button.clicked.connect(self.toggle_play)
        self.prev_button = QToolButton()
        self.prev_button.setText("上一帧")
        self.prev_button.clicked.connect(self.step_prev)
        self.next_button = QToolButton()
        self.next_button.setText("下一帧")
        self.next_button.clicked.connect(self.step_next)
        self.in_button = QToolButton()
        self.in_button.setText("设 In")
        self.in_button.clicked.connect(self.mark_in)
        self.out_button = QToolButton()
        self.out_button.setText("设 Out")
        self.out_button.clicked.connect(self.mark_out)
        self.keyframe_button = QPushButton("保存关键帧")
        self.keyframe_button.setObjectName("PrimaryButton")
        self.keyframe_button.clicked.connect(self.save_keyframe_action)

        self.timecode_label = QLabel("00:00.000 / 00:00.000")
        self.timecode_label.setObjectName("Timecode")
        self.frame_label = QLabel("f0 / f0")
        self.frame_label.setObjectName("Framecode")
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setObjectName("Framecode")

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addSpacing(12)
        controls_layout.addWidget(self.in_button)
        controls_layout.addWidget(self.out_button)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.timecode_label)
        controls_layout.addSpacing(12)
        controls_layout.addWidget(self.frame_label)
        controls_layout.addSpacing(12)
        controls_layout.addWidget(self.fps_label)
        controls_layout.addSpacing(12)
        controls_layout.addWidget(self.keyframe_button)

        self.timeline = TimelineWidget()
        timeline_frame = self._card_frame("TimelineBar")
        timeline_layout = QVBoxLayout(timeline_frame)
        timeline_layout.addWidget(self.timeline)
        self.timeline.positionChanged.connect(self.seek_to_frame)

        self.selection_panel = SelectionPanel()
        self.export_panel = ExportPanel()
        self.export_panel.setObjectName("SidePanel")
        self.export_panel.export_button.clicked.connect(self.export_action)
        splitter_frame = self._card_frame("BottomSplit")
        splitter_layout = QHBoxLayout(splitter_frame)
        splitter_layout.setContentsMargins(8, 8, 8, 8)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.selection_panel)
        splitter.addWidget(self.export_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter_layout.addWidget(splitter)

        layout.addWidget(header)
        layout.addWidget(player_frame)
        layout.addWidget(controls_frame)
        layout.addWidget(timeline_frame)
        layout.addWidget(splitter_frame)
        self.setCentralWidget(central)
        central.installEventFilter(self)

    def _build_menu(self) -> None:
        menu = self.menuBar().addMenu("文件")
        open_project = QAction("选择项目", self)
        open_project.triggered.connect(self.pick_project)
        open_video = QAction("打开视频", self)
        open_video.triggered.connect(self.open_video)
        menu.addAction(open_project)
        menu.addAction(open_video)

    def _install_shortcut_actions(self) -> None:
        self._shortcut_actions: list[QAction] = []
        mapping = [
            (self.shortcut_map.play_pause, self.toggle_play),
            (self.shortcut_map.prev_frame, self.step_prev),
            (self.shortcut_map.next_frame, self.step_next),
            (self.shortcut_map.mark_in, self.mark_in),
            (self.shortcut_map.mark_out, self.mark_out),
            (self.shortcut_map.add_range, self.add_range),
            (self.shortcut_map.save_keyframe, self.save_keyframe_action),
            (self.shortcut_map.export, self._export_ranges),
            (self.shortcut_map.cancel, self._clear_in_out),
        ]
        for key, handler in mapping:
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(handler)
            self.addAction(action)
            self._shortcut_actions.append(action)

    def _card_frame(self, name: str = "Card") -> QFrame:
        frame = QFrame()
        frame.setObjectName(name)
        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 160))
        frame.setGraphicsEffect(shadow)
        return frame

    def _clear_in_out(self) -> None:
        self.in_ms = None
        self.out_ms = None
        self._refresh_in_out()

    def pick_project(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if not directory:
            return
        self.project_dir = Path(directory)
        init_project(self.project_dir)
        self.project_label.setText(f"项目：{self.project_dir}")

    def _on_zoom_changed(self, text: str) -> None:
        if text == "适配":
            self.player.set_scale_mode("fit")
        else:
            try:
                factor = float(text.strip("%")) / 100.0
            except ValueError:
                factor = 1.0
            self.player.set_scale_mode("zoom")
            self.player.set_zoom_factor(factor)
        self._sync_viewport()

    def open_video(self) -> None:
        if self.project_dir is None:
            self.pick_project()
            if self.project_dir is None:
                return
        video_path, _ = QFileDialog.getOpenFileName(self, "选择视频文件")
        if not video_path:
            return
        self.video_path = Path(video_path)
        self.video_folder = get_video_folder_name(self.video_path)
        self.video_id = self.video_folder
        ensure_video_subdirs(self.project_dir, self.video_folder)

        relpath = normalize_source_path(self.project_dir, self.video_path)
        append_source(self.project_dir / "sources.csv", self.video_id, relpath)

        self.capture.open(self.video_path)
        self.current_frame_index = 0
        frame = self.capture.get_frame_at(self.current_frame_index)
        if frame:
            self.current_timestamp_ms = frame.timestamp_ms
            self.player.set_frame(frame.image)
        self.timeline.set_video_info(self.capture.total_frames, self.capture.fps)
        self.timeline.set_position(self.current_frame_index)
        self._update_status_labels(self.current_frame_index)
        self._sync_viewport()
        self.video_label.setText(f"视频：{self.video_path.name}")

    def toggle_play(self) -> None:
        if self.play_timer.isActive():
            self.play_timer.stop()
            self.play_button.setText("播放")
            return
        if not self._ensure_video_loaded():
            return
        interval = int(round(1000 / max(self.capture.fps, 1.0)))
        self.play_timer.start(interval)
        self.play_button.setText("暂停")

    def _on_playback_tick(self) -> None:
        frame = self.capture.read_next()
        if frame is None:
            self.play_timer.stop()
            self.play_button.setText("播放")
            return
        self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def step_prev(self) -> None:
        if not self._ensure_video_loaded():
            return
        target = max(self.current_frame_index - 1, 0)
        frame = self.capture.get_frame_at(target)
        if frame:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def step_next(self) -> None:
        if not self._ensure_video_loaded():
            return
        target = min(self.current_frame_index + 1, self.capture.total_frames - 1)
        frame = self.capture.get_frame_at(target)
        if frame:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def seek_to_frame(self, frame_index: int) -> None:
        if not self._ensure_video_loaded():
            return
        frame = self.capture.get_frame_at(frame_index)
        if frame:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def mark_in(self) -> None:
        if not self._ensure_video_loaded():
            return
        self.in_ms = self.current_timestamp_ms
        self._refresh_in_out()

    def mark_out(self) -> None:
        if not self._ensure_video_loaded():
            return
        self.out_ms = self.current_timestamp_ms
        if (
            self.in_ms is not None
            and self.out_ms is not None
            and self.out_ms < self.in_ms
        ):
            self.in_ms, self.out_ms = self.out_ms, self.in_ms
        self._refresh_in_out()

    def add_range(self) -> None:
        if self.in_ms is None or self.out_ms is None:
            return
        entry = RangeEntry(in_ms=self.in_ms, out_ms=self.out_ms)
        self.ranges.append(entry)
        label = f"{self._format_ms(entry.in_ms)} → {self._format_ms(entry.out_ms)}"
        self.selection_panel.add_range(label)

    def save_keyframe_action(self) -> None:
        if not self._ensure_video_loaded():
            return
        if (
            self.project_dir is None
            or self.video_folder is None
            or self.video_id is None
        ):
            return
        video_path = self.video_path
        if video_path is None:
            return
        frame = self.capture.get_frame_at(self.current_frame_index)
        if not frame:
            return
        try:
            record = save_keyframe(
                project_dir=self.project_dir,
                video_folder=self.video_folder,
                video_id=self.video_id,
                src_video_path=str(video_path),
                timestamp_ms=frame.timestamp_ms,
                frame_index=frame.frame_index,
                image=frame.image,
            )
        except RuntimeError as exc:
            QMessageBox.warning(self, "关键帧", str(exc))
            return
        if record:
            append_frame_records(self.project_dir / "metadata" / "frames.csv", [record])
            self.selection_panel.add_keyframe(
                f"{self._format_ms(frame.timestamp_ms)} / f{frame.frame_index}"
            )

    def export_action(self) -> None:
        if self.project_dir is None:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not output_dir:
            return
        name = self.export_panel.current_format()
        exporter = get_exporter(name)
        exporter(self.project_dir, output_dir)
        QMessageBox.information(self, "完成", "导出完成")

    def _ensure_video_loaded(self) -> bool:
        if self.video_path is None:
            QMessageBox.warning(self, "提示", "请先打开视频")
            return False
        return True

    def _refresh_in_out(self) -> None:
        self.timeline.set_in_out(self.in_ms, self.out_ms)

    def _update_frame(self, frame_index: int, timestamp_ms: int, image) -> None:
        self.current_frame_index = frame_index
        self.current_timestamp_ms = timestamp_ms
        self.player.set_frame(image)
        self.timeline.set_position(frame_index)
        self._update_status_labels(frame_index)

    def _format_ms(self, timestamp_ms: int) -> str:
        total_seconds = max(timestamp_ms, 0) / 1000.0
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"

    def _update_status_labels(self, frame_index: int) -> None:
        fps = self.capture.fps
        total_frames = max(self.capture.total_frames - 1, 0)
        current_ms = int(round((frame_index / max(fps, 1e-6)) * 1000))
        total_ms = int(round((total_frames / max(fps, 1e-6)) * 1000))
        self.timecode_label.setText(
            f"{self._format_ms(current_ms)} / {self._format_ms(total_ms)}"
        )
        self.frame_label.setText(f"f{frame_index} / f{total_frames}")
        self.fps_label.setText(f"FPS: {fps:.2f}" if fps > 0 else "FPS: --")

    def _sync_viewport(self) -> None:
        if hasattr(self, "viewer_scroll"):
            self.player.set_viewport_size(self.viewer_scroll.viewport().size())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_viewport()

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key == ord("J"):
            self.seek_direction = -1
            self._start_seek_timer()
            return
        if key == ord("L"):
            self.seek_direction = 1
            self._start_seek_timer()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:
        if event.key() in (ord("J"), ord("L")):
            self.seek_timer.stop()
            self.seek_direction = 0
            return
        super().keyReleaseEvent(event)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
            key = event.key()
            if key == ord("J"):
                self.seek_direction = -1
                self._start_seek_timer()
                return True
            if key == ord("L"):
                self.seek_direction = 1
                self._start_seek_timer()
                return True
        if event.type() == QEvent.Type.KeyRelease and isinstance(event, QKeyEvent):
            key = event.key()
            if key in (ord("J"), ord("L")):
                self.seek_timer.stop()
                self.seek_direction = 0
                return True
        return super().eventFilter(watched, event)

    def _start_seek_timer(self) -> None:
        if not self._ensure_video_loaded():
            return
        if not self.seek_timer.isActive():
            self.seek_timer.start(120)

    def _on_seek_tick(self) -> None:
        if self.seek_direction == 0:
            return
        if not self._ensure_video_loaded():
            return
        step = int(round(self.capture.fps))
        target = self.current_frame_index + (step * self.seek_direction)
        target = max(0, min(target, self.capture.total_frames - 1))
        frame = self.capture.get_frame_at(target)
        if frame:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def _export_ranges(self) -> None:
        if not self._ensure_video_loaded():
            return
        if (
            self.project_dir is None
            or self.video_folder is None
            or self.video_id is None
        ):
            return
        video_path = self.video_path
        if video_path is None:
            return
        try:
            ensure_ffmpeg()
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "FFmpeg", str(exc))
            return
        fps = self.export_panel.current_fps()
        if self.in_ms is not None and self.out_ms is not None:
            if self.out_ms < self.in_ms:
                self.in_ms, self.out_ms = self.out_ms, self.in_ms
            self.ranges.append(RangeEntry(self.in_ms, self.out_ms))
        if not self.ranges:
            QMessageBox.warning(self, "提示", "请先添加区间")
            return
        records = []
        for entry in self.ranges:
            result = extract_range_frames(
                project_dir=self.project_dir,
                video_path=video_path,
                video_folder=self.video_folder,
                video_id=self.video_id,
                src_video_path=str(video_path),
                start_ms=entry.in_ms,
                end_ms=entry.out_ms,
                fps=fps,
                video_fps=self.capture.fps,
            )
            records.extend(result.records)
        append_frame_records(self.project_dir / "metadata" / "frames.csv", records)
        QMessageBox.information(self, "完成", "区间抽帧完成")
