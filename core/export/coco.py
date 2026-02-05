from __future__ import annotations

import json
from pathlib import Path

import cv2

from core.metadata.reader import read_frames_csv


def export_coco(project_dir: str | Path, output_dir: str | Path) -> Path:
    project_dir = Path(project_dir)
    output_dir = Path(output_dir)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    frames_csv = project_dir / "metadata" / "frames.csv"
    rows = read_frames_csv(frames_csv)

    images: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        image_path = project_dir / row.image_relpath
        if not image_path.exists():
            continue
        target = images_dir / image_path.name
        if not target.exists():
            target.write_bytes(image_path.read_bytes())

        width, height = _read_image_size(image_path)
        images.append(
            {
                "id": idx,
                "file_name": target.name,
                "width": width,
                "height": height,
            }
        )

    payload = {
        "images": images,
        "annotations": [],
        "categories": [],
    }
    (output_dir / "annotations.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_dir


def _read_image_size(image_path: Path) -> tuple[int, int]:
    image = cv2.imread(str(image_path))
    if image is None:
        return 0, 0
    height, width = image.shape[:2]
    return width, height
