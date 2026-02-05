# 用户手册

## 1. 创建/选择项目
启动后点击“选择项目”，指定一个目录作为项目根目录。系统会自动创建标准目录结构。

## 2. 打开视频
点击“打开视频”选择本地视频文件。视频会被登记到 `sources.csv`。

## 3. 预览与标记
- Space：播放/暂停
- A/D：逐帧后退/前进
- J/L：快退/快进（约 1 秒）
- I/O：标记 In/Out
- Enter：添加区间

## 4. 保存关键帧
按 S 或点击“保存关键帧”，当前帧将保存到 `frames/<video_folder>/keyframes/`，并写入 `metadata/frames.csv`。

## 5. 区间抽帧
按 E 开始区间抽帧，默认 5fps。帧保存到 `frames/<video_folder>/ranges/`。

## 6. 导出数据集骨架
选择导出格式并点击“开始导出”，生成 Raw/Ultralytics/COCO 骨架。
