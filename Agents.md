# BubForge Agents 指导纲要

本文件用于指导后续所有开发工作，确保实现与 SPEC 一致、范围可控、可验证。

## 目标与范围（v0.1）
- 一句话目标：像剪辑软件一样快速预览视频、挑选关键帧与区间帧，并增量导出数据集骨架。
- 非目标：不做完整标注器、不集成 YOLO/SAM 推理、不做多人协作/权限/数据库服务。

## 架构约束
- GUI：PySide6（Qt Widgets），仅负责交互/调度/展示。
- Core：无 GUI 依赖，承担抽帧、元数据、导出逻辑；未来可被 CLI/插件复用。
- FFmpeg：通过子进程完成抽帧/探测。

## 目录与命名规范（固定）
- 项目结构：
  - project.yaml
  - sources.csv
  - frames/<video_folder>/{keyframes,ranges}
  - metadata/frames.csv
  - logs/app.log
- video_folder 命名：<原文件名>__<short_hash>
- 帧文件命名：t{timestamp_ms}_f{frame_index}.jpg|png
- 增量规则：若帧文件已存在则跳过写入。

## 元数据规范（frames.csv）
- 必填列：video_id, src_video_path, timestamp_ms, frame_index, kind, image_relpath, created_at
- kind 取值：keyframe | range
- 允许追加扩展列，但不得破坏最小集合。

## GUI 心智模型与快捷键
- 主窗口分区：预览 / 时间线 / 选择 / 导出。
- 快捷键默认：
  - Space 播放/暂停
  - A/D 上一帧/下一帧
  - J/L 快退/快进（约 1 秒，可长按）
  - I 设置 In
  - O 设置 Out（Out < In 自动交换）
  - Enter 添加区间
  - S 保存关键帧
  - E 开始导出
  - Esc 取消当前操作

## 抽帧策略
- 预览/挑帧：OpenCV 解码 + Qt QTimer 驱动显示，保证帧级控制。
- 区间导出：FFmpeg 子进程；默认 5 fps；需解析输出生成 timestamp_ms。
- 高级选项：全量抽帧时提示磁盘风险。

## 导出 Profiles（v0 内置）
- RawFrames + Metadata：原样导出 frames/ + metadata/frames.csv
- Ultralytics Skeleton：images/train|val|test（空 labels）+ data.yaml（占位）
- COCO Skeleton：images/ + annotations.json（images 已填，annotations 为空）

## 开发顺序（建议）
1. Core：视频信息探测 + 帧索引
2. GUI：播放器 + Timeline
3. 快捷键（A/D/J/L/I/O/S）
4. 单视频区间抽帧（5 fps）
5. metadata/frames.csv 写入
6. 增量跳过逻辑
7. 导出 Profiles
8. 打包 lite/full

## 验收标准（DoD）
- 1080p/50fps/5min 播放不卡
- 逐帧定位，In/Out 可标记
- S 键抓帧即时落盘
- 区间 5fps 抽帧正确
- 重复导出不生成重复帧
- metadata 可追溯每张图来源

## 变更与验证原则
- 先读后写，按现有风格实现。
- 每次变更应附带最小可运行路径与验证记录。
- 不做范围外扩展。
