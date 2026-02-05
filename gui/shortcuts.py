from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShortcutMap:
    play_pause: str = "Space"
    prev_frame: str = "A"
    next_frame: str = "D"
    rewind: str = "J"
    forward: str = "L"
    mark_in: str = "I"
    mark_out: str = "O"
    add_range: str = "Return"
    save_keyframe: str = "S"
    export: str = "E"
    cancel: str = "Escape"
