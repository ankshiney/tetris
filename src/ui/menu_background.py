"""Animated menu backdrop — aurora, light rays, falling tetrominoes."""

from __future__ import annotations

import math
import random

import pygame

from config.settings import WINDOW_HEIGHT, WINDOW_WIDTH
from src.core.tetromino import SHAPES
from src.ui.blocks import draw_mini_block
import src.ui.colors as colors


class MenuBackground:
    """Full-screen cinematic background for title / options."""

    def __init__(self) -> None:
        self.time = 0.0
        self._gradient: pygame.Surface | None = None
        self._size = (0, 0)
        self._rays = [random.uniform(0, math.tau) for _ in range(5)]
        self._fallers: list[dict] = []
        self._spawn_timer = 0.0
        kinds = list(colors.PIECE_COLORS.keys())
        for _ in range(8):
            self._fallers.append(self._new_faller(kinds))

    def _new_faller(self, kinds: list[str]) -> dict:
        kind = random.choice(kinds)
        return {
            "kind": kind,
            "x": random.uniform(0.05, 0.95),
            "y": random.uniform(-0.3, 1.1),
            "speed": random.uniform(28, 65),
            "drift": random.uniform(-12, 12),
            "rot": random.uniform(0, math.tau),
            "rot_speed": random.uniform(-1.2, 1.2),
            "cell": random.randint(10, 14),
            "alpha": random.randint(35, 75),
        }

    def invalidate(self) -> None:
        self._gradient = None

    def update(self, dt: float) -> None:
        self.time += dt
        self._spawn_timer += dt
        if self._spawn_timer > 1.8:
            self._spawn_timer = 0.0
            kinds = list(colors.PIECE_COLORS.keys())
            self._fallers.append(self._new_faller(kinds))
            if len(self._fallers) > 14:
                self._fallers.pop(0)

        w, h = WINDOW_WIDTH, WINDOW_HEIGHT
        for f in self._fallers:
            f["y"] += f["speed"] * dt / h
            f["x"] += f["drift"] * dt / w
            f["rot"] += f["rot_speed"] * dt
            if f["y"] > 1.15:
                f.update(self._new_faller(list(colors.PIECE_COLORS.keys())))
                f["y"] = -0.15

    def _rebuild_gradient(self, w: int, h: int) -> None:
        self._gradient = pygame.Surface((w, h))
        for y in range(h):
            t = y / max(1, h - 1)
            color = tuple(
                int(colors.BG_GRADIENT_TOP[i] + (colors.BG_GRADIENT_BOTTOM[i] - colors.BG_GRADIENT_TOP[i]) * t)
                for i in range(3)
            )
            pygame.draw.line(self._gradient, color, (0, y), (w, y))
        self._size = (w, h)

    def draw(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()
        if self._gradient is None or self._size != (w, h):
            self._rebuild_gradient(w, h)
        surface.blit(self._gradient, (0, 0))

        aurora = pygame.Surface((w, h), pygame.SRCALPHA)
        for i, phase in enumerate(self._rays):
            cx = int(w * (0.2 + 0.15 * i + 0.05 * math.sin(self.time * 0.3 + phase)))
            cy = int(h * (0.35 + 0.1 * math.sin(self.time * 0.45 + phase * 1.3)))
            radius = int(120 + 40 * math.sin(self.time * 0.5 + i))
            color = (*colors.TITLE_TEXT, int(12 + 8 * math.sin(self.time + i)))
            pygame.draw.circle(aurora, color, (cx, cy), radius)
        surface.blit(aurora, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        for i in range(3):
            angle = self.time * 0.08 + i * 1.4
            ray = pygame.Surface((w, h), pygame.SRCALPHA)
            cx, cy = w // 2, int(h * 0.25)
            length = int(max(w, h) * 1.2)
            x2 = cx + int(math.cos(angle) * length)
            y2 = cy + int(math.sin(angle) * length)
            pygame.draw.line(ray, (*colors.STAR_TINT, 8), (cx, cy), (x2, y2), 3)
            surface.blit(ray, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        for f in self._fallers:
            self._draw_faller(surface, f, w, h)

        vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        max_r = int(max(w, h) * 0.85)
        for r in range(max_r, 0, -18):
            t = r / max_r
            pygame.draw.circle(vignette, (0, 0, 0, int(22 * t * t)), (cx, cy), r)
        surface.blit(vignette, (0, 0))

    def _draw_faller(self, surface: pygame.Surface, f: dict, w: int, h: int) -> None:
        kind = f["kind"]
        cell = f["cell"]
        offsets = SHAPES[kind][0]
        min_c = min(c for c, _ in offsets)
        min_r = min(r for _, r in offsets)
        max_c = max(c for c, _ in offsets)
        max_r = max(r for _, r in offsets)
        pw = (max_c - min_c + 1) * cell + 8
        ph = (max_r - min_r + 1) * cell + 8
        temp = pygame.Surface((pw, ph), pygame.SRCALPHA)
        color = colors.PIECE_COLORS[kind]
        for col, row in offsets:
            draw_mini_block(temp, (col - min_c) * cell + 4, (row - min_r) * cell + 4, cell, color)
        temp.set_alpha(f["alpha"])
        rotated = pygame.transform.rotate(temp, math.degrees(f["rot"]))
        px = int(f["x"] * w) - rotated.get_width() // 2
        py = int(f["y"] * h) - rotated.get_height() // 2
        surface.blit(rotated, (px, py))