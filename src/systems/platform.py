"""Runtime platform detection — desktop vs Android."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_android() -> bool:
    """True when running inside a python-for-android APK."""
    if os.environ.get("ANDROID_ARGUMENT") or os.environ.get("ANDROID_PRIVATE"):
        return True
    try:
        from jnius import autoclass  # type: ignore[import-untyped]

        autoclass("org.kivy.android.PythonActivity")
        return True
    except Exception:
        return False


def is_mobile() -> bool:
    """Touch-first UI: Android builds and explicit mobile override."""
    if is_android():
        return True
    return os.environ.get("TETRIS_MOBILE", "").lower() in ("1", "true", "yes")


def configure_android_env() -> None:
    """SDL/Android tweaks applied before pygame.init()."""
    if not is_android():
        return
    os.environ.setdefault("SDL_ANDROID_BACK_BUTTON", "0")
    os.environ.setdefault("SDL_MOUSE_TOUCH_EVENTS", "1")
    os.environ.setdefault("SDL_TOUCH_MOUSE_EVENTS", "1")
    os.environ.setdefault("SDL_AUDIODRIVER", "android")
    os.environ.setdefault("SDL_VIDEO_ALLOW_SCREENSAVER", "1")
    try:
        import pygame

        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
    except Exception:
        pass


def android_version() -> str:
    if not is_android():
        return ""
    return os.environ.get("ANDROID_VERSION", "")


def platform_label() -> str:
    if is_android():
        ver = android_version()
        return f"Android {ver}" if ver else "Android"
    return f"{sys.platform}"


def write_android_log(message: str) -> None:
    """Persist crash text where adb logcat may be unavailable."""
    if not is_android():
        return
    targets: list[Path] = []
    private = os.environ.get("ANDROID_PRIVATE")
    if private:
        targets.append(Path(private) / "crash.log")
    try:
        from android.storage import app_storage_path  # type: ignore[import-untyped]

        targets.append(Path(app_storage_path()) / "crash.log")
    except Exception:
        pass
    for path in targets:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(message, encoding="utf-8")
            return
        except OSError:
            continue