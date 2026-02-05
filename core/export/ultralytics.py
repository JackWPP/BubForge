from __future__ import annotations

import math
from pathlib import Path

import yaml

from core.export.common import collect_frame_images, copy_images


def export_ultralytics(project_dir: str | Path, output_dir: str | Path) -> Path:
    project_dir = Path(project_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    images = collect_frame_images(project_dir)
    train_dir = output_dir / "images" / "train"
    val_dir = output_dir / "images" / "val"
    test_dir = output_dir / "images" / "test"

    split_train, split_val = _split_counts(len(images))
    train_images = images[:split_train]
    val_images = images[split_train : split_train + split_val]
    test_images = images[split_train + split_val :]

    copy_images(train_images, train_dir)
    copy_images(val_images, val_dir)
    copy_images(test_images, test_dir)

    data_yaml = {
        "path": ".",
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": [],
    }
    (output_dir / "data.yaml").write_text(
        yaml.safe_dump(data_yaml, sort_keys=False), encoding="utf-8"
    )
    return output_dir


def _split_counts(total: int) -> tuple[int, int]:
    if total <= 0:
        return 0, 0
    train = int(math.floor(total * 0.8))
    val = int(math.floor(total * 0.1))
    return train, val
