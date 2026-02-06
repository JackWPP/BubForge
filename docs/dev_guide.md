# 开发文档

## 1. 目标与边界
基于 `SPEC.md`，v0.1 聚焦：
- 视频预览与逐帧控制
- 关键帧/区间帧的增量落盘
- `frames.csv` 元数据可追溯
- 导出三类数据集骨架

非目标（v0）：
- 完整标注器
- YOLO/SAM 推理集成
- 多人协作与服务端系统

## 2. 架构分层
- `gui/`：PySide6 Qt Widgets，负责交互与展示
- `core/`：业务逻辑（项目、抽帧、元数据、导出）
- `utils/`：通用工具（FFmpeg 检测、hash、日志）

设计原则：GUI 不直接包含重业务逻辑，核心能力尽量沉入 `core/`。

## 3. 模块地图
### 3.1 Project
- `core/project/manager.py`
  - `init_project()`：初始化项目目录与基础文件
  - `get_video_folder_name()`：视频目录命名（含短 hash）
  - `ensure_video_subdirs()`：确保 keyframes/ranges 子目录
- `core/project/sources.py`
  - `append_source()`：登记视频来源

### 3.2 Video
- `core/video/capture.py`
  - OpenCV 预览读取与逐帧定位
- `core/video/frame_writer.py`
  - 关键帧写入（含写盘 fallback）
- `core/video/extractor.py`
  - FFmpeg 区间抽帧、showinfo 时间戳解析、增量跳过

### 3.3 Metadata
- `core/metadata/frames_csv.py`
  - `FrameRecord`、表头定义、追加写入
- `core/metadata/reader.py`
  - 读取 `frames.csv`（用于恢复关键帧显示）

### 3.4 Export
- `core/export/registry.py`：导出器分发
- `core/export/raw.py`：原样导出
- `core/export/ultralytics.py`：Ultralytics 骨架
- `core/export/coco.py`：COCO 骨架

### 3.5 GUI
- `gui/main_window.py`：主窗口、Dock 工作区、快捷键、交互编排
- `gui/widgets/timeline.py`：时间线、In/Out 与关键帧标记
- `gui/widgets/selection_panel.py`：关键帧/区间列表
- `gui/widgets/export_panel.py`：导出参数面板
- `gui/widgets/video_player.py`：视频显示与缩放策略

## 4. 关键业务流程
### 4.1 保存关键帧
1. GUI 获取当前帧
2. `save_keyframe()` 落盘（增量）
3. 追加 `frames.csv`
4. 时间线和列表更新关键帧标记

### 4.2 区间抽帧
1. 设置 In/Out（Out 时自动入列）
2. `_export_ranges()` 调用 `extract_range_frames()`
3. FFmpeg 输出写入 ranges 目录并生成记录
4. 追加 `frames.csv`

### 4.3 工作区布局
- 使用 `QDockWidget` 可拖拽停靠/浮动
- 使用 `QSettings` 持久化窗口几何与布局状态

## 5. 开发与验证
### 5.1 运行
```bash
pip install -r requirements.txt
python main.py
```

### 5.2 快速语法检查
```bash
python -m compileall main.py core gui utils
```

### 5.3 LSP 说明
当前环境若为 Windows + Bun 1.3.5，LSP 工具可能不可用（已知问题）。

## 6. 打包脚本
- `scripts/build_lite.py`
- `scripts/build_full.py`

当前为打包占位脚本，可按发布流程继续完善参数与资源收集。

## 7. 代码风格与约束
- 遵循 `Agents.md` 里的命名、目录、元数据与增量规则
- 避免在 GUI 中堆积业务逻辑
- 修改前先读现有结构，优先小步增量改动
