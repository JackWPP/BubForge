from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QByteArray, QEvent, QSettings, QTimer, Qt
from PySide6.QtGui import QAction, QColor, QKeyEvent, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from core.export.registry import get_exporter
from core.metadata.reader import read_frames_csv
from core.metadata.frames_csv import append_frame_records
from core.project.manager import (
    ensure_video_subdirs,
    get_video_folder_name,
    init_project,
)
from core.project.sources import append_source, normalize_source_path
from core.video.capture import VideoCaptureController
from core.video.extractor import extract_range_frames
from core.video.frame_writer import save_keyframe
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
        self.setMinimumSize(1280, 820)
        self.setStyleSheet(app_stylesheet())
        self.setDockNestingEnabled(True)
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowNestedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
        )

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
        self.keyframe_indices: set[int] = set()

        self._build_ui()
        self._build_menu()
        self._install_shortcut_actions()
        self._restore_layout_state()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        top_bar = self._card_frame("TopBar")
        top_layout = QHBoxLayout(top_bar)
        title = QLabel("BubForge · 预览中心")
        title.setObjectName("TitleLabel")
        self.project_button = QToolButton()
        self.project_button.setText("选择项目")
        self.project_button.clicked.connect(self.pick_project)
        self.video_button = QToolButton()
        self.video_button.setText("打开视频")
        self.video_button.clicked.connect(self.open_video)
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["比例锁定", "自由拉伸"])
        self.aspect_combo.currentTextChanged.connect(self._on_aspect_mode_changed)
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["适配", "100%", "150%", "200%"])
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_changed)
        self.reset_layout_button = QToolButton()
        self.reset_layout_button.setText("重置工作区")
        self.reset_layout_button.clicked.connect(self._reset_dock_layout)
        self.project_label = QLabel("项目：未选择")
        self.video_label = QLabel("视频：未加载")

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.project_button)
        top_layout.addWidget(self.video_button)
        top_layout.addWidget(QLabel("比例"))
        top_layout.addWidget(self.aspect_combo)
        top_layout.addWidget(QLabel("显示"))
        top_layout.addWidget(self.zoom_combo)
        top_layout.addWidget(self.reset_layout_button)
        top_layout.addSpacing(8)
        top_layout.addWidget(self.project_label)
        top_layout.addSpacing(8)
        top_layout.addWidget(self.video_label)

        viewer_frame = self._card_frame("ViewerFrame")
        viewer_layout = QVBoxLayout(viewer_frame)
        viewer_layout.setContentsMargins(10, 10, 10, 10)
        self.player = VideoPlayerWidget()
        self.viewer_scroll = QScrollArea()
        self.viewer_scroll.setWidget(self.player)
        self.viewer_scroll.setWidgetResizable(False)
        self.viewer_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.viewer_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        viewer_layout.addWidget(self.viewer_scroll)

        transport = self._card_frame("TransportBar")
        transport_layout = QHBoxLayout(transport)
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

        transport_layout.addWidget(self.play_button)
        transport_layout.addWidget(self.prev_button)
        transport_layout.addWidget(self.next_button)
        transport_layout.addWidget(self.in_button)
        transport_layout.addWidget(self.out_button)
        transport_layout.addStretch(1)
        transport_layout.addWidget(self.timecode_label)
        transport_layout.addWidget(self.frame_label)
        transport_layout.addWidget(self.fps_label)
        transport_layout.addWidget(self.keyframe_button)

        root.addWidget(top_bar)
        root.addWidget(viewer_frame, 1)
        root.addWidget(transport)
        self.setCentralWidget(central)
        central.installEventFilter(self)

        self.timeline = TimelineWidget()
        self.timeline.positionChanged.connect(self.seek_to_frame)
        self.selection_panel = SelectionPanel()
        self.export_panel = ExportPanel()
        self.export_panel.export_button.clicked.connect(self.export_action)

        self.timeline_dock = self._make_dock("时间线", self.timeline)
        self.selection_dock = self._make_dock("素材选择", self.selection_panel)
        self.export_dock = self._make_dock("导出面板", self.export_panel)

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_dock)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.selection_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.export_dock)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("文件")
        action_project = QAction("选择项目", self)
        action_project.triggered.connect(self.pick_project)
        action_video = QAction("打开视频", self)
        action_video.triggered.connect(self.open_video)
        action_reset = QAction("重置工作区", self)
        action_reset.triggered.connect(self._reset_dock_layout)
        file_menu.addAction(action_project)
        file_menu.addAction(action_video)
        file_menu.addSeparator()
        file_menu.addAction(action_reset)

        view_menu = self.menuBar().addMenu("视图")
        view_menu.addAction(self.timeline_dock.toggleViewAction())
        view_menu.addAction(self.selection_dock.toggleViewAction())
        view_menu.addAction(self.export_dock.toggleViewAction())

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

    def _card_frame(self, name: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName(name)
        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 160))
        frame.setGraphicsEffect(shadow)
        return frame

    def _make_dock(self, title: str, widget: QWidget) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(f"dock_{title}")
        dock.setWidget(widget)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        return dock

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

    def _on_aspect_mode_changed(self, text: str) -> None:
        self.player.set_aspect_lock(text == "比例锁定")
        self._sync_viewport()

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

        self.in_ms = None
        self.out_ms = None
        self.ranges.clear()
        self.keyframe_indices.clear()
        self.selection_panel.clear_all()
        self.timeline.clear_keyframe_markers()
        self._refresh_in_out()

        self.capture.open(self.video_path)
        self.current_frame_index = 0
        frame = self.capture.get_frame_at(self.current_frame_index)
        if frame is not None:
            self.current_timestamp_ms = frame.timestamp_ms
            self.player.set_frame(frame.image)

        self.timeline.set_video_info(self.capture.total_frames, self.capture.fps)
        self.timeline.set_position(self.current_frame_index)
        self._load_existing_keyframes()
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
        if frame is not None:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def step_next(self) -> None:
        if not self._ensure_video_loaded():
            return
        target = min(self.current_frame_index + 1, self.capture.total_frames - 1)
        frame = self.capture.get_frame_at(target)
        if frame is not None:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def seek_to_frame(self, frame_index: int) -> None:
        if not self._ensure_video_loaded():
            return
        frame = self.capture.get_frame_at(frame_index)
        if frame is not None:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def mark_in(self) -> None:
        if not self._ensure_video_loaded():
            return
        self.in_ms = self.current_timestamp_ms
        self.out_ms = None
        self._refresh_in_out()

    def mark_out(self) -> None:
        if not self._ensure_video_loaded():
            return
        if self.in_ms is None:
            QMessageBox.information(self, "区间", "请先设置 In 点，再设置 Out 点")
            return
        self.out_ms = self.current_timestamp_ms
        if (
            self.in_ms is not None
            and self.out_ms is not None
            and self.out_ms < self.in_ms
        ):
            self.in_ms, self.out_ms = self.out_ms, self.in_ms
        self._refresh_in_out()
        self.add_range(silent=True)

    def add_range(self, silent: bool = False) -> None:
        if self.in_ms is None or self.out_ms is None:
            if not silent:
                QMessageBox.information(self, "区间", "请先设置 In/Out 点")
            return
        entry = RangeEntry(self.in_ms, self.out_ms)
        if self._has_range(entry):
            return
        self.ranges.append(entry)
        self.selection_panel.add_range(
            f"{self._format_ms(entry.in_ms)} -> {self._format_ms(entry.out_ms)}"
        )

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
        if frame is None:
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

        if record is not None:
            append_frame_records(self.project_dir / "metadata" / "frames.csv", [record])
            self.keyframe_indices.add(frame.frame_index)
            self.timeline.add_keyframe_marker(frame.frame_index)
            self.selection_panel.add_keyframe(
                f"{self._format_ms(frame.timestamp_ms)} / f{frame.frame_index}"
            )
            self.step_next()

    def export_action(self) -> None:
        if self.project_dir is None:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not output_dir:
            return
        exporter = get_exporter(self.export_panel.current_format())
        exporter(self.project_dir, output_dir)
        QMessageBox.information(self, "完成", "导出完成")

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
        self.add_range(silent=True)
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

    def _has_range(self, entry: RangeEntry) -> bool:
        return any(
            r.in_ms == entry.in_ms and r.out_ms == entry.out_ms for r in self.ranges
        )

    def _load_existing_keyframes(self) -> None:
        if self.project_dir is None or self.video_id is None:
            return
        frames_csv = self.project_dir / "metadata" / "frames.csv"
        rows = read_frames_csv(frames_csv)
        key_rows = [
            row
            for row in rows
            if row.video_id == self.video_id and row.kind == "keyframe"
        ]
        if not key_rows:
            return
        self.keyframe_indices = {row.frame_index for row in key_rows}
        self.timeline.set_keyframe_markers(sorted(self.keyframe_indices))
        for row in sorted(key_rows, key=lambda r: r.timestamp_ms):
            self.selection_panel.add_keyframe(
                f"{self._format_ms(row.timestamp_ms)} / f{row.frame_index}"
            )

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
        self.player.set_viewport_size(self.viewer_scroll.viewport().size())

    def _format_ms(self, timestamp_ms: int) -> str:
        total_seconds = max(timestamp_ms, 0) / 1000.0
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"

    def _reset_dock_layout(self) -> None:
        self.removeDockWidget(self.timeline_dock)
        self.removeDockWidget(self.selection_dock)
        self.removeDockWidget(self.export_dock)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_dock)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.selection_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.export_dock)
        self.timeline_dock.show()
        self.selection_dock.show()
        self.export_dock.show()

    def _restore_layout_state(self) -> None:
        settings = QSettings("BubForge", "BubForge")
        geometry = settings.value("window_geometry")
        state = settings.value("window_state")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)
        if isinstance(state, QByteArray):
            self.restoreState(state)

    def _save_layout_state(self) -> None:
        settings = QSettings("BubForge", "BubForge")
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())

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
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            self._step_by_keyboard(key, event.modifiers())
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
            if event.key() == ord("J"):
                self.seek_direction = -1
                self._start_seek_timer()
                return True
            if event.key() == ord("L"):
                self.seek_direction = 1
                self._start_seek_timer()
                return True
            if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
                self._step_by_keyboard(event.key(), event.modifiers())
                return True
        if event.type() == QEvent.Type.KeyRelease and isinstance(event, QKeyEvent):
            if event.key() in (ord("J"), ord("L")):
                self.seek_timer.stop()
                self.seek_direction = 0
                return True
        return super().eventFilter(watched, event)

    def _step_by_keyboard(self, key: int, modifiers) -> None:
        if not self._ensure_video_loaded():
            return
        step = self._step_for_modifiers(modifiers)
        delta = -step if key == Qt.Key.Key_Left else step
        self._seek_by_frames(delta)

    def _step_for_modifiers(self, modifiers) -> int:
        fps_step = max(int(round(self.capture.fps)), 1)
        if (
            modifiers & Qt.KeyboardModifier.ControlModifier
            and modifiers & Qt.KeyboardModifier.ShiftModifier
        ):
            return fps_step * 5
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            return fps_step
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            return 10
        return 1

    def _seek_by_frames(self, delta: int) -> None:
        target = self.current_frame_index + delta
        target = max(0, min(target, self.capture.total_frames - 1))
        frame = self.capture.get_frame_at(target)
        if frame is not None:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

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
        if frame is not None:
            self._update_frame(frame.frame_index, frame.timestamp_ms, frame.image)

    def closeEvent(self, event) -> None:
        self._save_layout_state()
        super().closeEvent(event)
