from __future__ import annotations

import hashlib
from pathlib import Path


def short_hash_for_path(path: str | Path, length: int = 8) -> str:
    resolved = Path(path).expanduser().resolve()
    stat = resolved.stat()
    payload = f"{resolved}|{stat.st_size}|{stat.st_mtime_ns}"
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return digest[:length]
