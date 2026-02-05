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
