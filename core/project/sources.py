from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def normalize_source_path(project_dir: str | Path, video_path: str | Path) -> str:
    project_root = Path(project_dir).resolve()
    video_path = Path(video_path).expanduser().resolve()
    try:
        return str(video_path.relative_to(project_root))
    except ValueError:
        return str(video_path)


def read_sources(sources_csv: str | Path) -> list[dict[str, str]]:
    path = Path(sources_csv)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def append_source(
    sources_csv: str | Path,
    video_id: str,
    src_video_path: str,
) -> None:
    path = Path(sources_csv)
    existing = {row.get("video_id") for row in read_sources(path)}
    if video_id in existing:
        return
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["video_id", "src_video_path"])
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([video_id, src_video_path])


def append_sources(
    sources_csv: str | Path,
    rows: Iterable[tuple[str, str]],
) -> None:
    for video_id, src_video_path in rows:
        append_source(sources_csv, video_id, src_video_path)
