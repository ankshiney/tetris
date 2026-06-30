"""Smooth motion for pieces, rows, score popups, and screen fades."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from config.settings import CELL_SIZE, ROW_FALL_DURATION
from src.utils.easing import ease_out_back, ease_out_cubic, lerp, smooth_damp


@dataclass
class FallCell:
    col: int
    row: int
    kind: str
    distance: float


class PieceAnimator:
    """Sub-grid pixel motion for the active piece."""

    def __init__(self) -> None:
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.squash = 1.0
        self.alpha = 255.0
        self.rotate_pop = 0.0
        self._drop_t = 1.0
        self._drop_dur = 0.1
        self._slide_x = 0.0
        self._slide_t = 1.0
        self._squash_t = 1.0
        self._spawn_t = 1.0

    def reset(self) -> None:
        self.__init__()

    def on_spawn(self) -> None:
        self.offset_y = -CELL_SIZE * 1.5
        self.alpha = 60.0
        self._spawn_t = 0.0

    def on_step_down(self, *, fast: bool = False) -> None:
        self.offset_y = -float(CELL_SIZE)
        self._drop_t = 0.0
        self._drop_dur = 0.045 if fast else 0.09

    def on_step_horizontal(self, dx: int) -> None:
        self._slide_x = float(-dx * CELL_SIZE * 0.35)
        self._slide_t = 0.0

    def on_rotate(self) -> None:
        self.rotate_pop = 1.0

    def on_lock(self) -> None:
        self.squash = 0.72
        self._squash_t = 0.0

    def update(self, dt: float) -> None:
        if self._drop_t < 1.0:
            self._drop_t = min(1.0, self._drop_t + dt / self._drop_dur)
            self.offset_y = -CELL_SIZE * (1.0 - ease_out_cubic(self._drop_t))

        if self._slide_t < 1.0:
            self._slide_t = min(1.0, self._slide_t + dt / 0.07)
            self.offset_x = lerp(self._slide_x, 0.0, ease_out_cubic(self._slide_t))

        if self._spawn_t < 1.0:
            self._spawn_t = min(1.0, self._spawn_t + dt / 0.22)
            eased = ease_out_back(self._spawn_t)
            self.offset_y = lerp(-CELL_SIZE * 1.5, 0.0, eased)
            self.alpha = lerp(60.0, 255.0, eased)

        if self._squash_t < 1.0:
            self._squash_t = min(1.0, self._squash_t + dt / 0.14)
            self.squash = lerp(0.72, 1.0, ease_out_back(self._squash_t))

        if self.rotate_pop > 0:
            self.rotate_pop = max(0.0, self.rotate_pop - dt * 4.5)


class RowFallAnimator:
    """Animate blocks sliding down after line clears."""

    def __init__(self) -> None:
        self.cells: list[FallCell] = []
        self.progress = 1.0
        self.duration = ROW_FALL_DURATION
        self.active = False

    def start(self, cleared_rows: list[int], grid: list[list[str | None]]) -> None:
        self.cells = []
        cleared = set(cleared_rows)
        for row, line in enumerate(grid):
            if row in cleared:
                continue
            shift = sum(1 for cr in cleared_rows if cr < row)
            if shift <= 0:
                continue
            new_row = row - shift
            for col, kind in enumerate(line):
                if kind is not None:
                    self.cells.append(FallCell(col, new_row, kind, shift * CELL_SIZE))
        self.progress = 0.0
        self.active = bool(self.cells)

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.progress = min(1.0, self.progress + dt / self.duration)
        if self.progress >= 1.0:
            self.active = False
            self.cells.clear()

    def offset_for(self, col: int, row: int) -> float:
        for cell in self.cells:
            if cell.col == col and cell.row == row:
                return -cell.distance * (1.0 - ease_out_cubic(self.progress))
        return 0.0


@dataclass
class ScorePopup:
    text: str
    x: float
    y: float
    life: float
    max_life: float
    color: tuple[int, int, int]
    scale: float = 1.0


class ScorePopupManager:
    """Floating score text like mobile puzzle games."""

    def __init__(self) -> None:
        self.popups: list[ScorePopup] = []
        self.font = pygame.font.SysFont("consolas", 22, bold=True)

    def spawn(self, text: str, x: float, y: float, color: tuple[int, int, int]) -> None:
        self.popups.append(ScorePopup(text, x, y, 1.1, 1.1, color, 0.85))

    def update(self, dt: float) -> None:
        alive: list[ScorePopup] = []
        for p in self.popups:
            p.life -= dt
            p.y -= 28 * dt
            p.scale = min(1.15, p.scale + dt * 0.8)
            if p.life > 0:
                alive.append(p)
        self.popups = alive

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.popups:
            alpha = int(255 * min(1.0, p.life / (p.max_life * 0.5)))
            text = self.font.render(p.text, True, p.color)
            w = max(1, int(text.get_width() * p.scale))
            h = max(1, int(text.get_height() * p.scale))
            scaled = pygame.transform.smoothscale(text, (w, h))
            scaled.set_alpha(alpha)
            rect = scaled.get_rect(center=(int(p.x), int(p.y)))
            surface.blit(scaled, rect)


class AnimatedCounter:
    """Smoothly scrolls displayed integers toward the real value."""

    def __init__(self) -> None:
        self.display = 0.0
        self.target = 0

    def set(self, value: int) -> None:
        self.target = value

    def update(self, dt: float) -> int:
        self.display = smooth_damp(self.display, float(self.target), dt, 0.1)
        return int(self.display + 0.5)


class ScreenFader:
    """Fade overlay for state transitions."""

    def __init__(self) -> None:
        self.alpha = 0.0
        self._from = 0.0
        self._to = 0.0
        self._t = 1.0
        self._dur = 0.3

    def fade_to(self, target: float, duration: float = 0.3) -> None:
        self._from = self.alpha
        self._to = max(0.0, min(255.0, target))
        self._t = 0.0
        self._dur = duration

    def update(self, dt: float) -> None:
        if self._t < 1.0:
            self._t = min(1.0, self._t + dt / self._dur)
            self.alpha = lerp(self._from, self._to, ease_out_cubic(self._t))

    def draw(self, surface: pygame.Surface) -> None:
        if self.alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.alpha)))
        surface.blit(overlay, (0, 0))