from __future__ import annotations

import shutil
from pathlib import Path


def export_raw(project_dir: str | Path, output_dir: str | Path) -> Path:
    project_dir = Path(project_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frames_src = project_dir / "frames"
    metadata_src = project_dir / "metadata"

    frames_dst = output_dir / "frames"
    metadata_dst = output_dir / "metadata"
    if frames_src.exists() and not frames_dst.exists():
        shutil.copytree(frames_src, frames_dst)
    if metadata_src.exists() and not metadata_dst.exists():
        shutil.copytree(metadata_src, metadata_dst)
    return output_dir
