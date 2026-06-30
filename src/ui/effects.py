"""Particles, screen shake, notifications, and optimized background."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from config.settings import BOARD_ORIGIN_X, BOARD_ORIGIN_Y, CELL_SIZE, COLS, HIDDEN_ROWS, MAX_PARTICLES
import src.ui.colors as colors
from src.utils.easing import ease_out_cubic


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    life: float
    max_life: float
    size: float


class ParticleSystem:
    """Spawns and updates short-lived visual particles with a hard cap."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def clear(self) -> None:
        self.particles.clear()

    def _can_spawn(self, n: int) -> int:
        room = MAX_PARTICLES - len(self.particles)
        return max(0, min(n, room))

    def spawn_line_clear(self, rows: list[int]) -> None:
        per_cell = 4 if len(rows) >= 4 else 2
        for row in rows:
            visible_row = row - HIDDEN_ROWS
            if visible_row < 0:
                continue
            for col in range(COLS):
                self._spawn_at_cell(col, visible_row, count=per_cell)

    def spawn_from_cells(self, cells: list[tuple[int, int]], kind: str, count: int = 6) -> None:
        color = colors.PIECE_COLORS[kind]
        count = self._can_spawn(count * len(cells))
        spawned = 0
        for col, row in cells:
            if row < HIDDEN_ROWS or spawned >= count:
                continue
            px = BOARD_ORIGIN_X + col * CELL_SIZE + CELL_SIZE // 2
            py = BOARD_ORIGIN_Y + (row - HIDDEN_ROWS) * CELL_SIZE + CELL_SIZE // 2
            for _ in range(min(3, count - spawned)):
                self.particles.append(
                    Particle(
                        x=float(px),
                        y=float(py),
                        vx=random.uniform(-100, 100),
                        vy=random.uniform(-170, -50),
                        color=color,
                        life=random.uniform(0.3, 0.6),
                        max_life=0.6,
                        size=random.uniform(3, 7),
                    )
                )
                spawned += 1

    def _spawn_at_cell(self, col: int, visible_row: int, count: int = 3) -> None:
        count = self._can_spawn(count)
        px = BOARD_ORIGIN_X + col * CELL_SIZE + CELL_SIZE // 2
        py = BOARD_ORIGIN_Y + visible_row * CELL_SIZE + CELL_SIZE // 2
        for _ in range(count):
            self.particles.append(
                Particle(
                    x=float(px) + random.uniform(-10, 10),
                    y=float(py) + random.uniform(-6, 6),
                    vx=random.uniform(-140, 140),
                    vy=random.uniform(-200, -40),
                    color=random.choice(list(colors.PIECE_COLORS.values())),
                    life=random.uniform(0.35, 0.75),
                    max_life=0.75,
                    size=random.uniform(2, 6),
                )
            )

    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            t = 1.0 - p.life / p.max_life
            drag = 1.0 - 0.4 * t
            p.x += p.vx * dt * drag
            p.y += p.vy * dt * drag
            p.vy += 280 * dt
            alive.append(p)
        self.particles = alive

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            life_ratio = p.life / p.max_life
            alpha = int(255 * ease_out_cubic(life_ratio))
            size = max(2, int(p.size * (0.6 + 0.4 * life_ratio)))
            block = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(block, (*p.color, alpha), block.get_rect(), border_radius=size // 2)
            surface.blit(block, (int(p.x), int(p.y)))


class ScreenShake:
    """Eased camera jitter — smoother than raw random offsets."""

    def __init__(self) -> None:
        self.intensity = 0.0
        self.duration = 0.0
        self.timer = 0.0
        self._phase = 0.0

    def trigger(self, intensity: float, duration: float) -> None:
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)
        self.timer = self.duration

    def update(self, dt: float) -> tuple[int, int]:
        if self.timer <= 0:
            return 0, 0
        self.timer -= dt
        self._phase += dt * 42.0
        t = ease_out_cubic(self.timer / self.duration if self.duration else 0)
        magnitude = self.intensity * t
        ox = int(magnitude * math.sin(self._phase) * random.uniform(0.6, 1.0))
        oy = int(magnitude * math.cos(self._phase * 1.3) * random.uniform(0.6, 1.0))
        if self.timer <= 0:
            self.intensity = 0.0
            self.duration = 0.0
        return ox, oy


class NotificationBanner:
    """Fading center-screen messages with elastic pop-in."""

    def __init__(self) -> None:
        self.text = ""
        self.color = colors.TITLE_TEXT
        self.timer = 0.0
        self.duration = 0.0
        self.font = pygame.font.SysFont("consolas", 36, bold=True)

    def show(
        self,
        text: str,
        duration: float = 1.4,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        self.text = text
        self.color = color if color is not None else colors.TITLE_TEXT
        self.timer = duration
        self.duration = duration

    def update(self, dt: float) -> None:
        if self.timer > 0:
            self.timer -= dt

    def draw(self, surface: pygame.Surface, board_center: tuple[int, int]) -> None:
        if self.timer <= 0 or not self.text:
            return
        elapsed = self.duration - self.timer
        pop = ease_out_cubic(min(1.0, elapsed / 0.18))
        fade = min(1.0, self.timer / max(0.01, self.duration * 0.4))
        scale = 0.75 + 0.35 * pop + 0.06 * (1.0 - self.timer / self.duration)
        text = self.font.render(self.text, True, self.color)
        w = max(1, int(text.get_width() * scale))
        h = max(1, int(text.get_height() * scale))
        scaled = pygame.transform.smoothscale(text, (w, h))
        scaled.set_alpha(int(255 * fade))
        glow = pygame.font.SysFont("consolas", 36, bold=True).render(self.text, True, self.color)
        glow.set_alpha(int(60 * fade))
        rect = scaled.get_rect(center=board_center)
        glow_rect = glow.get_rect(center=(board_center[0] + 1, board_center[1] + 1))
        surface.blit(glow, glow_rect)
        surface.blit(scaled, rect)


class BackgroundAnimator:
    """Cached gradient + lightweight parallax stars."""

    def __init__(self) -> None:
        self.time = 0.0
        self._gradient: pygame.Surface | None = None
        self._size = (0, 0)
        self.stars = [
            (random.randint(0, 1200), random.randint(0, 1000), random.uniform(0.3, 1.8), random.randint(1, 3))
            for _ in range(80)
        ]
        self._orbs = [
            (random.uniform(0, 1), random.uniform(0, 1), random.uniform(50, 110), random.uniform(0.15, 0.7))
            for _ in range(8)
        ]

    def _rebuild_gradient(self, width: int, height: int) -> None:
        self._gradient = pygame.Surface((width, height))
        for i in range(height):
            t = i / max(1, height - 1)
            color = (
                int(colors.BG_GRADIENT_TOP[0] + (colors.BG_GRADIENT_BOTTOM[0] - colors.BG_GRADIENT_TOP[0]) * t),
                int(colors.BG_GRADIENT_TOP[1] + (colors.BG_GRADIENT_BOTTOM[1] - colors.BG_GRADIENT_TOP[1]) * t),
                int(colors.BG_GRADIENT_TOP[2] + (colors.BG_GRADIENT_BOTTOM[2] - colors.BG_GRADIENT_TOP[2]) * t),
            )
            pygame.draw.line(self._gradient, color, (0, i), (width, i))
        self._size = (width, height)

    def invalidate(self) -> None:
        self._gradient = None

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, surface: pygame.Surface, width: int, height: int) -> None:
        if self._gradient is None or self._size != (width, height):
            self._rebuild_gradient(width, height)
        surface.blit(self._gradient, (0, 0))

        aurora = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(3):
            cx = int(width * (0.25 + 0.25 * i + 0.04 * math.sin(self.time * 0.25 + i)))
            cy = int(height * (0.55 + 0.08 * math.cos(self.time * 0.35 + i * 1.7)))
            r = int(90 + 30 * math.sin(self.time * 0.4 + i))
            pygame.draw.circle(aurora, (*colors.STAR_TINT, 10), (cx, cy), r)
        surface.blit(aurora, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        for nx, ny, radius, speed in self._orbs:
            ox = int((nx * width + self.time * 12 * speed) % width)
            oy = int((ny * height + self.time * 8 * speed) % height)
            orb = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(orb, (*colors.STAR_TINT, 22), (radius, radius), radius)
            surface.blit(orb, (ox - radius, oy - radius), special_flags=pygame.BLEND_RGBA_ADD)

        for x, y, speed, size in self.stars:
            drift_y = (y + self.time * 20 * speed) % height
            pulse = 0.4 + 0.6 * abs((self.time * speed) % 1 - 0.5)
            color = tuple(int(c * pulse) for c in colors.STAR_TINT)
            pygame.draw.circle(surface, color, (int(x % width), int(drift_y)), size)