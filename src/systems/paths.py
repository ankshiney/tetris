"""Writable paths — desktop data/ folder vs Android app storage."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from src.systems.platform import is_android

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_BUNDLED_DATA = _PROJECT_ROOT / "data"


def project_root() -> Path:
    return _PROJECT_ROOT


def data_dir() -> Path:
    """Persistent storage for settings and high scores."""
    if is_android():
        try:
            from android.storage import app_storage_path  # type: ignore[import-untyped]

            path = Path(app_storage_path())
        except Exception:
            path = _PROJECT_ROOT / "data"
    else:
        path = _PROJECT_ROOT / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def settings_file() -> Path:
    return data_dir() / "settings.json"


def highscores_file() -> Path:
    return data_dir() / "highscores.json"


def seed_android_data() -> None:
    """Copy bundled defaults into app storage on first Android launch."""
    if not is_android():
        return
    target = data_dir()
    if not _BUNDLED_DATA.exists():
        return
    for name in ("settings.json", "highscores.json"):
        src = _BUNDLED_DATA / name
        dst = target / name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
        elif name == "settings.json" and not dst.exists():
            dst.write_text(
                json.dumps(
                    {
                        "theme": "cyber",
                        "music_track": "ambient",
                        "music_volume": 0.3,
                        "sfx_volume": 0.58,
                        "music_enabled": True,
                        "fullscreen": True,
                        "particles_enabled": True,
                        "display_scale": 1.0,
                        "touch_controls": True,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )