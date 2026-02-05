from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from core.metadata.frames_csv import ensure_frames_csv
from utils.hash_gen import short_hash_for_path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    project_yaml: Path
    sources_csv: Path
    frames_dir: Path
    metadata_dir: Path
    frames_csv: Path
    logs_dir: Path
    app_log: Path


def init_project(project_dir: str | Path) -> ProjectPaths:
    root = Path(project_dir)
    project_yaml = root / "project.yaml"
    sources_csv = root / "sources.csv"
    frames_dir = root / "frames"
    metadata_dir = root / "metadata"
    frames_csv = metadata_dir / "frames.csv"
    logs_dir = root / "logs"
    app_log = logs_dir / "app.log"

    frames_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not project_yaml.exists():
        payload = {
            "name": root.name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "0.1",
        }
        project_yaml.write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )

    if not sources_csv.exists():
        sources_csv.write_text("video_id,src_video_path\n", encoding="utf-8")

    ensure_frames_csv(frames_csv)
    if not app_log.exists():
        app_log.write_text("", encoding="utf-8")

    return ProjectPaths(
        root=root,
        project_yaml=project_yaml,
        sources_csv=sources_csv,
        frames_dir=frames_dir,
        metadata_dir=metadata_dir,
        frames_csv=frames_csv,
        logs_dir=logs_dir,
        app_log=app_log,
    )


def get_video_folder_name(video_path: str | Path, hash_len: int = 8) -> str:
    path = Path(video_path)
    stem = path.stem
    short_hash = short_hash_for_path(path, length=hash_len)
    return f"{stem}__{short_hash}"


def ensure_video_subdirs(
    project_dir: str | Path, video_folder: str
) -> tuple[Path, Path]:
    base = Path(project_dir) / "frames" / video_folder
    keyframes_dir = base / "keyframes"
    ranges_dir = base / "ranges"
    keyframes_dir.mkdir(parents=True, exist_ok=True)
    ranges_dir.mkdir(parents=True, exist_ok=True)
    return keyframes_dir, ranges_dir
