"""Runtime platform detection — desktop vs Android."""

from __future__ import annotations

import os
import sys


def is_android() -> bool:
    """True when running inside a python-for-android APK."""
    if os.environ.get("ANDROID_ARGUMENT") or os.environ.get("ANDROID_PRIVATE"):
        return True
    try:
        import android  # type: ignore[import-untyped]  # noqa: F401

        return True
    except ImportError:
        pass
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