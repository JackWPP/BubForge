# BubForge

BubForge 是一个偏「剪辑软件心智」的视频挑帧工具：先预览，再打点（关键帧/区间），最后导出数据集骨架。

## 你能用它做什么
- 快速预览视频并逐帧定位
- 保存关键帧（增量写盘，不重复写）
- 选择 In/Out 区间并按 FPS 批量抽帧
- 维护可追溯元数据 `metadata/frames.csv`
- 导出三类数据集骨架：Raw / Ultralytics / COCO
- 使用可拖拽 Dock 工作区（像剪辑软件那样自定义布局）

## 环境要求
- Windows 10 / 11
- Python 3.10+
- FFmpeg + FFprobe（在 PATH 中可用，或后续通过配置接入）

## 安装与启动
```bash
pip install -r requirements.txt
python main.py
```

## 界面与工作区
- **中央区域**：视频预览 + 传输控制
- **Dock 面板**：
  - 底部：时间线
  - 左侧：素材选择（关键帧/区间）
  - 右侧：导出面板
- 支持拖拽停靠、浮动窗口、隐藏/显示（菜单 `视图`）
- 支持重置工作区（按钮“重置工作区”）
- 关闭窗口时会自动保存当前布局并在下次恢复

## 关键交互
| 快捷键 | 行为 |
|---|---|
| `Space` | 播放 / 暂停 |
| `A / D` | 上一帧 / 下一帧 |
| `J / L` | 连续快退 / 快进 |
| `← / →` | 1 帧步进 |
| `Shift + ← / →` | 10 帧步进 |
| `Ctrl + ← / →` | 约 1 秒步进 |
| `Ctrl + Shift + ← / →` | 约 5 秒步进 |
| `I / O` | 设置 In / Out |
| `Enter` | 添加区间 |
| `S` | 保存关键帧（保存后自动跳下一帧） |
| `E` | 执行区间抽帧 |
| `Esc` | 清空当前 In/Out |

补充说明：
- 设置 `Out` 时会自动把当前 In/Out 区间加入区间列表（带去重）。
- 已保存关键帧会在时间线上显示标记，并在重新打开同视频时自动恢复显示。

## 两种“导出”概念（重要）
1. **区间抽帧（快捷键 `E`）**
   - 将区间帧抽到项目目录：`frames/<video_folder>/ranges`
   - 并写入 `metadata/frames.csv`
2. **数据集骨架导出（右侧“开始导出”按钮）**
   - 把项目内容导出为目标格式目录结构（Raw/Ultralytics/COCO）

## 项目目录结构
```text
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

命名规则：
- `video_folder`: `<原文件名>__<short_hash>`
- 帧文件名: `t{timestamp_ms}_f{frame_index}.jpg|png`

## 文档索引
- 用户手册：`docs/user_guide.md`
- 开发文档：`docs/dev_guide.md`
- 常见问题：`docs/troubleshooting.md`
- 第三方声明：`THIRD_PARTY_NOTICES.md`
