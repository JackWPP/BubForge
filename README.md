# BubForge

像剪辑软件一样快速预览视频、挑选关键帧与区间帧，并增量导出为数据集骨架。

## 快速开始
1. 安装依赖：`pip install -r requirements.txt`
2. 运行：`python main.py`

## 功能
- 视频预览（OpenCV + Qt）
- 帧级定位与快捷键操作
- 关键帧保存与区间抽帧（FFmpeg）
- metadata/frames.csv 增量写入
- 导出 Raw/Ultralytics/COCO 骨架
- 剪辑软件式布局：预览/时间线/面板可拖拽调整
- 自动适配视频分辨率与比例

## 目录结构
```
<project>/
  project.yaml
  sources.csv
  frames/<video_folder>/{keyframes,ranges}
  metadata/frames.csv
  logs/app.log
```

## 快捷键
Space 播放/暂停 | A/D 上一帧/下一帧 | J/L 快退/快进 | I/O 设置 In/Out | Enter 添加区间 | S 保存关键帧 | E 抽帧导出 | Esc 取消

补充：
- `S` 保存关键帧后会自动跳到下一帧，方便连续挑帧
- 方向键 `←/→` 支持多档步进：
  - `←/→`：1 帧
  - `Shift + ←/→`：10 帧
  - `Ctrl + ←/→`：约 1 秒
  - `Ctrl + Shift + ←/→`：约 5 秒
- 设置 In/Out 后会自动加入区间列表，区间导出更直观
- 关键帧会在时间线上显示标记

## 布局与适配
- 采用剪辑软件常见的 `Dock` 工作区：时间线、素材选择、导出面板都可鼠标拖拽停靠/浮动
- 可通过拖拽 Dock 边界自由调整面板大小，支持左/右/下停靠
- 支持隐藏/显示面板（菜单“视图”）
- “重置工作区”可恢复默认停靠布局
- 自动记忆上次工作区布局（窗口关闭后保存）
- “比例”可切换：比例锁定 / 自由拉伸
- “显示”可切换视频缩放（适配 / 100% / 150% / 200%）
