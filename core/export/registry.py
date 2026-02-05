from __future__ import annotations

from pathlib import Path
from typing import Callable

from core.export.coco import export_coco
from core.export.raw import export_raw
from core.export.ultralytics import export_ultralytics

Exporter = Callable[[str | Path, str | Path], Path]


def get_exporter(name: str) -> Exporter:
    if name == "RawFrames + Metadata":
        return export_raw
    if name == "Ultralytics Skeleton":
        return export_ultralytics
    if name == "COCO Skeleton":
        return export_coco
    raise ValueError(f"未知导出格式: {name}")
