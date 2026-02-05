# BubForge v0.1 SPEC（Vibe Coding Friendly）

> **一句话目标**：像剪辑软件一样，快速预览视频、挑选关键帧与区间帧，并**增量导出**为数据集骨架。
>
> **设计哲学**：
>
> * 不做多余抽象，不引入用户不需要的复杂度
> * 用户心智 = 剪辑软件（预览 → 标记 → 导出）
> * 工程心智 = Core 稳定、GUI 轻、后续插件可扩展

---

## 0. 非目标（明确不做什么）

* v0 不做完整标注器
* v0 不集成 YOLO / SAM 推理
* v0 不做多人协作/权限/数据库服务

---

## 1. 平台与交付

### 1.1 平台

* OS：Windows（Win10 / Win11）
* 语言：Python 3.10+

### 1.2 交付形态

* `BubForge-lite.exe`

  * 不自带 FFmpeg
  * 启动时检测 ffmpeg/ffprobe
  * 若缺失 → GUI 提示配置路径
* `BubForge-full.exe`

  * 自带 FFmpeg + FFprobe
  * 开箱即用

### 1.3 合规

* 提供 `THIRD_PARTY_NOTICES.md`
* FFmpeg 许可证与二进制来源说明

---

## 2. 总体架构

```
┌──────────────┐
│     GUI      │  PySide6
│ (Qt Widgets) │
└──────┬───────┘
       │ calls
┌──────▼───────┐
│    Core      │  无 GUI 依赖
│ (Python)     │
└──────┬───────┘
       │ subprocess
┌──────▼───────┐
│   FFmpeg     │  抽帧 / 探测
└──────────────┘
```

* **Core**：视频抽帧、元数据、导出逻辑
* **GUI**：用户交互、任务调度、进度展示
* **原则**：GUI 不包含业务逻辑；CLI/插件未来复用 Core

---

## 3. 项目与数据结构

### 3.1 项目目录（v0 固定）

```
<project>/
  project.yaml
  sources.csv
  frames/
    <video_folder>/
      keyframes/
      ranges/
  metadata/
    frames.csv
  logs/
    app.log
```

### 3.2 video_folder 命名

```
<原文件名>__<short_hash>
```

* 保证唯一
* GUI 显示友好名称

### 3.3 帧文件命名（去重 + 可追溯）

```
t{timestamp_ms}_f{frame_index}.jpg|png
```

* 若文件已存在 → **跳过**

---

## 4. 元数据规范

### 4.1 metadata/frames.csv（最小集合）

| 字段名            | 含义               |
| -------------- | ---------------- |
| video_id       | 视频唯一 ID          |
| src_video_path | 源视频路径（可相对）       |
| timestamp_ms   | 帧时间戳（毫秒）         |
| frame_index    | 原视频帧号            |
| kind           | keyframe / range |
| image_relpath  | 图像相对路径           |
| created_at     | 写入时间             |

* 工况字段：**不强制**，未来可扩展列

---

## 5. GUI 设计（剪辑软件心智）

### 5.1 主窗口布局

```
┌─────────────────────────────┐
│ Video Preview               │
│ (play / pause / seek)       │
├──────── Timeline ───────────┤
│ [In]───▮──────▮───[Out]     │
├──────── Selection ──────────┤
│ Keyframes | Ranges          │
├──────── Export ─────────────┤
│ Format | FPS | Start Export │
└─────────────────────────────┘
```

### 5.2 快捷键（默认）

| 键     | 行为                    |
| ----- | --------------------- |
| Space | 播放 / 暂停               |
| A / D | 上一帧 / 下一帧             |
| J / L | 快退 / 快进（≈1 秒，支持长按）    |
| I     | 设置 In                 |
| O     | 设置 Out（Out < In 自动交换） |
| Enter | 添加区间                  |
| S     | 保存关键帧                 |
| E     | 开始导出                  |
| Esc   | 取消当前操作                |

### 5.3 区间抽帧策略

* 默认：**5 fps**
* 高级选项：全量抽帧（强磁盘风险提示）

---

## 6. 抽帧实现策略

### 6.1 预览 / 挑帧

* OpenCV (`cv2.VideoCapture`) 解码
* Qt `QTimer` 驱动显示
* 帧级控制可靠（50fps 视频）

### 6.2 批量导出

* FFmpeg 子进程
* In/Out + fps
* 解析 FFmpeg 输出生成 timestamp_ms
* 写入前检查文件是否存在（增量）

---

## 7. 导出 Profiles（v0 内置）

### 7.1 RawFrames + Metadata

* 原样导出 frames/ + metadata/frames.csv

### 7.2 Ultralytics Dataset Skeleton

* images/train|val|test（空 labels）
* data.yaml（类别占位）

### 7.3 COCO Skeleton

* images/
* annotations.json（images 部分已填，annotations 为空）

---

## 8. 插件 / 脚本扩展（预留，不在 v0 启用）

### 8.1 插件契约

* 输入：project 路径
* 读取：frames.csv + images
* 输出：

```
artifacts/<plugin_name>/
  outputs/
  artifact_manifest.json
```

* 规则：

  * 不改原始 frames
  * 只做增量输出

---

## 9. 打包与发布

### 9.1 打包

* PyInstaller
* 分别生成 lite / full

### 9.2 发布清单

* exe
* README.md（中文）
* 用户手册（docs/user_guide.md）
* 开发文档（docs/dev_guide.md）
* THIRD_PARTY_NOTICES.md

---

## 10. 验收标准（Definition of Done）

* 能播放 1080p / 50fps / 5min 视频不卡
* 能逐帧定位、标记 In/Out
* S 键抓帧即时落盘
* 区间 5fps 抽帧正确
* 重复导出不会生成重复帧
* metadata 可追溯每一张图来源

---

## 11. 推荐开发顺序（Vibe Coding Friendly）

1. Core：视频信息探测 + 帧索引
2. GUI：播放器 + Timeline
3. 快捷键（A/D/J/L/I/O/S）
4. 单视频抽帧（5fps）
5. metadata/frames.csv 写入
6. 增量跳过逻辑
7. 导出 Profiles
8. 打包 lite/full

---

> **一句话总结**：
> BubForge v0 不是“数据工程平台”，而是一个**让人愿意每天打开、像剪辑一样挑数据的工具**。
