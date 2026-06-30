"""Map mouse coordinates between screen space and the virtual framebuffer."""

from __future__ import annotations

import pygame

from config.settings import WINDOW_HEIGHT, WINDOW_WIDTH


class DisplayMapper:
    """Converts pointer positions when the game is letterboxed or fullscreen."""

    def __init__(self) -> None:
        self.screen_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.fullscreen = False
        self.offset = (0, 0)
        self.scale = 1.0

    def refresh(self, screen: pygame.Surface, *, fullscreen: bool) -> None:
        sw, sh = screen.get_size()
        self.screen_size = (sw, sh)
        self.fullscreen = fullscreen
        if fullscreen:
            self.scale = min(sw / WINDOW_WIDTH, sh / WINDOW_HEIGHT)
            nw = WINDOW_WIDTH * self.scale
            nh = WINDOW_HEIGHT * self.scale
            self.offset = (int((sw - nw) / 2), int((sh - nh) / 2))
        else:
            self.scale = sw / WINDOW_WIDTH
            self.offset = (0, 0)

    def to_virtual(self, pos: tuple[int, int]) -> tuple[int, int]:
        x = (pos[0] - self.offset[0]) / self.scale
        y = (pos[1] - self.offset[1]) / self.scale
        return int(x), int(y)

    def in_virtual_bounds(self, pos: tuple[int, int]) -> bool:
        vx, vy = self.to_virtual(pos)
        return 0 <= vx < WINDOW_WIDTH and 0 <= vy < WINDOW_HEIGHT