"""Load or auto-generate image assets."""

from __future__ import annotations

from pathlib import Path

import pygame

from src.systems.asset_generator import generate_all_assets
from src.systems.paths import assets_dir

REQUIRED = ("menu_bg.png", "panel.png", "logo_glow.png", "pause_banner.png", "music_icon.png")


class AssetManager:
    """Caches PNG assets; generates them on first run if missing."""

    def __init__(self) -> None:
        self._cache: dict[str, pygame.Surface] = {}
        self._ensure_assets()

    def _ensure_assets(self) -> None:
        if not all((assets_dir() / name).exists() for name in REQUIRED):
            try:
                generate_all_assets()
            except Exception:
                pass

    def get(self, name: str) -> pygame.Surface | None:
        if name in self._cache:
            return self._cache[name]
        path = assets_dir() / name
        if not path.exists():
            return None
        try:
            loaded = pygame.image.load(str(path))
            try:
                surf = loaded.convert_alpha()
            except pygame.error:
                surf = loaded.convert()
            self._cache[name] = surf
            return surf
        except pygame.error:
            return None

    def invalidate(self) -> None:
        self._cache.clear()