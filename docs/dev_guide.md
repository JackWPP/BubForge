# 开发文档

## 架构
- GUI：PySide6 (Qt Widgets)
- Core：纯 Python，无 GUI 依赖
- FFmpeg/FFprobe：子进程调用

## 关键目录
- core/：抽帧、元数据、导出逻辑
- gui/：界面与快捷键
- utils/：通用工具

## 运行
```
pip install -r requirements.txt
python main.py
```

## 规范
请遵循 `Agents.md` 中的约束与命名规则。
