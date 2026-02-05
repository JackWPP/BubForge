from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_dir: str | Path, level: int = logging.INFO) -> logging.Logger:
    log_path = Path(log_dir) / "app.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("bubforge")
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
