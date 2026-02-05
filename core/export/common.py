from __future__ import annotations

import shutil
from pathlib import Path


def collect_frame_images(project_dir: str | Path) -> list[Path]:
    project_dir = Path(project_dir)
    frames_dir = project_dir / "frames"
    if not frames_dir.exists():
        return []
    images: list[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        images.extend(frames_dir.rglob(ext))
    return sorted(images)


def copy_images(images: list[Path], output_dir: str | Path) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for image_path in images:
        target = output_dir / image_path.name
        if target.exists():
            continue
        shutil.copy2(image_path, target)
        copied.append(target)
    return copied
