"""Pre-rendered block surfaces for fast, consistent drawing."""

from __future__ import annotations

import pygame

from src.ui.blocks import build_block_surface


class BlockCache:
    """Caches glossy block sprites keyed by color and size."""

    def __init__(self) -> None:
        self._cells: dict[tuple, pygame.Surface] = {}
        self._ghosts: dict[tuple, pygame.Surface] = {}
        self._minis: dict[tuple, pygame.Surface] = {}

    def clear(self) -> None:
        self._cells.clear()
        self._ghosts.clear()
        self._minis.clear()

    def get_cell(
        self,
        color: tuple[int, int, int],
        size: int,
        *,
        alpha: int = 255,
    ) -> pygame.Surface:
        key = (*color, size, alpha)
        if key not in self._cells:
            self._cells[key] = build_block_surface(size, color, alpha=alpha)
        return self._cells[key]

    def get_ghost(self, color: tuple[int, int, int], size: int) -> pygame.Surface:
        key = (*color, size)
        if key not in self._ghosts:
            self._ghosts[key] = build_block_surface(size, color, ghost=True)
        return self._ghosts[key]

    def get_mini(self, color: tuple[int, int, int], size: int) -> pygame.Surface:
        key = (*color, size)
        if key not in self._minis:
            self._minis[key] = build_block_surface(size, color)
        return self._minis[key]