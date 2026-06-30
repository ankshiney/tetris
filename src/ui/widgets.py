"""Modern UI widgets — buttons, sliders, toggles, glass panels."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pygame

import src.ui.colors as colors
from src.ui.fonts import get_font
from src.ui.themes import Theme


def _font(size: int, *, bold: bool = False) -> pygame.font.Font:
    return get_font(size, bold=bold)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * max(0.0, min(1.0, t))


def _lerp_color(
    a: tuple[int, int, int],
    b: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    return tuple(int(_lerp(a[i], b[i], t)) for i in range(3))


def _ease(current: float, target: float, dt: float, speed: float = 12.0) -> float:
    return current + (target - current) * min(1.0, dt * speed)


def draw_glass_panel(surface: pygame.Surface, rect: pygame.Rect, *, alpha: int = 230) -> None:
    shadow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 55), shadow.get_rect(), border_radius=18)
    surface.blit(shadow, (rect.x - 4, rect.y + 6))

    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    top = tuple(min(255, c + 22) for c in colors.PANEL_BOX)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        color = _lerp_color(top, colors.PANEL_BOX, t * 0.4)
        pygame.draw.line(panel, (*color, alpha), (0, y), (rect.width, y))
    highlight = pygame.Rect(8, 6, rect.width - 16, max(4, rect.height // 5))
    pygame.draw.rect(panel, (255, 255, 255, 18), highlight, border_radius=8)
    pygame.draw.rect(panel, (*colors.BOARD_BORDER, 80), panel.get_rect(), 1, border_radius=16)
    pygame.draw.rect(panel, (*colors.PANEL_BORDER, 210), panel.get_rect().inflate(-4, -4), 1, border_radius=13)
    surface.blit(panel, rect.topleft)


@dataclass
class UIButton:
    rect: pygame.Rect
    label: str
    action: str
    style: str = "primary"
    hover: float = 0.0
    press: float = 0.0
    font: pygame.font.Font = field(default_factory=lambda: _font(18, bold=True))

    def update(self, dt: float, mouse: tuple[int, int]) -> None:
        hovered = self.rect.collidepoint(mouse)
        self.hover = _ease(self.hover, 1.0 if hovered else 0.0, dt)
        self.press = _ease(self.press, 0.0, dt, speed=18.0)

    def on_press(self, mouse: tuple[int, int]) -> bool:
        if self.rect.collidepoint(mouse):
            self.press = 1.0
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        scale = 1.0 + self.hover * 0.03 - self.press * 0.02
        w = max(1, int(self.rect.width * scale))
        h = max(1, int(self.rect.height * scale))
        draw_rect = pygame.Rect(0, 0, w, h)
        draw_rect.center = self.rect.center

        if self.style == "primary":
            base = _lerp_color(colors.PANEL_BOX, colors.TITLE_TEXT, 0.35 + self.hover * 0.25)
            border = _lerp_color(colors.BOARD_BORDER, colors.TITLE_TEXT, 0.4 + self.hover * 0.5)
            text_color = (255, 255, 255) if self.hover > 0.4 else colors.TITLE_TEXT
        elif self.style == "danger":
            base = _lerp_color(colors.PANEL_BOX, (180, 50, 60), 0.2 + self.hover * 0.35)
            border = _lerp_color(colors.PANEL_BORDER, (255, 90, 100), 0.3 + self.hover * 0.5)
            text_color = (255, 220, 220)
        else:
            base = _lerp_color(colors.PANEL_BOX, (50, 55, 75), self.hover * 0.4)
            border = _lerp_color(colors.PANEL_BORDER, colors.TITLE_TEXT, self.hover * 0.45)
            text_color = _lerp_color(colors.PANEL_TEXT, colors.TITLE_TEXT, self.hover * 0.6)

        if self.hover > 0.05:
            glow = pygame.Surface((w + 14, h + 14), pygame.SRCALPHA)
            pygame.draw.rect(
                glow,
                (*colors.TITLE_TEXT, int(30 + 50 * self.hover)),
                glow.get_rect(),
                border_radius=12,
            )
            surface.blit(glow, (draw_rect.x - 7, draw_rect.y - 6))

        pygame.draw.rect(surface, base, draw_rect, border_radius=10)
        pygame.draw.rect(surface, border, draw_rect, 2, border_radius=10)
        label = self.font.render(self.label, True, text_color)
        surface.blit(label, label.get_rect(center=draw_rect.center))


@dataclass
class UISlider:
    rect: pygame.Rect
    value: float
    action: str
    hover: float = 0.0
    dragging: bool = False
    font: pygame.font.Font = field(default_factory=lambda: _font(14))

    def update(self, dt: float, mouse: tuple[int, int]) -> None:
        self.hover = _ease(self.hover, 1.0 if self.rect.collidepoint(mouse) or self.dragging else 0.0, dt)
        if self.dragging:
            self._set_from_mouse(mouse)

    def _set_from_mouse(self, mouse: tuple[int, int]) -> float:
        track = self._track_rect()
        t = (mouse[0] - track.x) / max(1, track.width)
        self.value = max(0.0, min(1.0, t))
        return self.value

    def _track_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.x + 8, self.rect.centery - 3, self.rect.width - 16, 6)

    def on_press(self, mouse: tuple[int, int]) -> bool:
        if self.rect.collidepoint(mouse):
            self.dragging = True
            self._set_from_mouse(mouse)
            return True
        return False

    def on_release(self) -> None:
        self.dragging = False

    def draw(self, surface: pygame.Surface, label: str) -> None:
        text = self.font.render(label, True, colors.PANEL_TEXT)
        surface.blit(text, (self.rect.x, self.rect.y + 2))
        track = self._track_rect()
        track_color = _lerp_color((40, 44, 62), (60, 70, 95), self.hover)
        fill_color = _lerp_color(colors.BOARD_BORDER, colors.TITLE_TEXT, 0.35 + self.hover * 0.4)
        pygame.draw.rect(surface, track_color, track, border_radius=4)
        fill_w = max(4, int(track.width * self.value))
        fill = pygame.Rect(track.x, track.y, fill_w, track.height)
        pygame.draw.rect(surface, fill_color, fill, border_radius=4)
        knob_x = track.x + int(track.width * self.value)
        knob_r = 7 + int(self.hover * 2)
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, track.centery), knob_r)
        pygame.draw.circle(surface, fill_color, (knob_x, track.centery), knob_r - 2)
        pct = self.font.render(f"{int(self.value * 100)}%", True, colors.TITLE_TEXT)
        surface.blit(pct, (self.rect.right - pct.get_width(), self.rect.y + 2))


@dataclass
class UIToggle:
    rect: pygame.Rect
    enabled: bool
    action: str
    hover: float = 0.0
    anim: float = 0.0
    font: pygame.font.Font = field(default_factory=lambda: _font(14))

    def update(self, dt: float, mouse: tuple[int, int]) -> None:
        self.hover = _ease(self.hover, 1.0 if self.rect.collidepoint(mouse) else 0.0, dt)
        target = 1.0 if self.enabled else 0.0
        self.anim = _ease(self.anim, target, dt, speed=14.0)

    def on_press(self, mouse: tuple[int, int]) -> bool:
        if self.rect.collidepoint(mouse):
            self.enabled = not self.enabled
            return True
        return False

    def draw(self, surface: pygame.Surface, label: str) -> None:
        text = self.font.render(label, True, colors.PANEL_TEXT)
        surface.blit(text, (self.rect.x, self.rect.centery - text.get_height() // 2))
        sw, sh = 46, 24
        switch = pygame.Rect(self.rect.right - sw, self.rect.centery - sh // 2, sw, sh)
        off_color = _lerp_color((50, 54, 70), (70, 75, 95), self.hover)
        on_color = _lerp_color(colors.BOARD_BORDER, colors.TITLE_TEXT, 0.5 + self.hover * 0.3)
        bg = _lerp_color(off_color, on_color, self.anim)
        pygame.draw.rect(surface, bg, switch, border_radius=sh // 2)
        knob_x = int(_lerp(switch.x + 12, switch.right - 12, self.anim))
        pygame.draw.circle(surface, (245, 245, 250), (knob_x, switch.centery), 9)


@dataclass
class UIThemeCard:
    theme: Theme
    rect: pygame.Rect
    hover: float = 0.0
    selected: bool = False
    font: pygame.font.Font = field(default_factory=lambda: _font(13, bold=True))

    def update(self, dt: float, mouse: tuple[int, int]) -> None:
        hovered = self.rect.collidepoint(mouse)
        self.hover = _ease(self.hover, 1.0 if hovered else 0.0, dt)

    def on_press(self, mouse: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse)

    def draw(self, surface: pygame.Surface) -> None:
        lift = int(self.hover * 3) - (2 if self.selected else 0)
        rect = self.rect.move(0, -lift)
        alpha = 200 + int(self.hover * 40)
        card = pygame.Surface(rect.size, pygame.SRCALPHA)
        base = self.theme.panel_box
        pygame.draw.rect(card, (*base, alpha), card.get_rect(), border_radius=10)
        if self.selected:
            pygame.draw.rect(card, (*self.theme.title_text, 255), card.get_rect(), 2, border_radius=10)
        elif self.hover > 0.1:
            pygame.draw.rect(card, (*self.theme.board_border, int(120 + 80 * self.hover)), card.get_rect(), 1, border_radius=10)
        surface.blit(card, rect.topleft)

        swatch_y = rect.y + 10
        swatches = list(self.theme.piece_colors.values())[:4]
        sx = rect.x + 10
        for swatch in swatches:
            pygame.draw.rect(surface, swatch, (sx, swatch_y, 14, 14), border_radius=3)
            sx += 18
        name = self.font.render(
            self.theme.label,
            True,
            self.theme.title_text if self.selected else colors.PANEL_TEXT,
        )
        surface.blit(name, name.get_rect(midbottom=(rect.centerx, rect.bottom - 8)))


class UICursor:
    """Switch between arrow and hand cursor when hovering interactive UI."""

    def __init__(self) -> None:
        self._hand: pygame.cursors.Cursor | None = None
        self._arrow: pygame.cursors.Cursor | None = None
        self._using_hand = False

    def _ensure(self) -> None:
        if self._hand is None:
            try:
                self._hand = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
                self._arrow = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
            except (AttributeError, pygame.error):
                self._hand = None

    def set_hand(self, active: bool) -> None:
        self._ensure()
        if self._hand is None or self._arrow is None:
            return
        if active and not self._using_hand:
            pygame.mouse.set_cursor(self._hand)
            self._using_hand = True
        elif not active and self._using_hand:
            pygame.mouse.set_cursor(self._arrow)
            self._using_hand = False


def draw_icon_pause(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int], hover: float) -> None:
    """Rounded square with pause bars."""
    r = pygame.Rect(rect)
    r.inflate_ip(int(hover * 4), int(hover * 4))
    bg = _lerp_color(colors.PANEL_BOX, (45, 50, 70), hover * 0.5)
    pygame.draw.rect(surface, bg, r, border_radius=8)
    pygame.draw.rect(surface, _lerp_color(colors.PANEL_BORDER, color, hover), r, 1, border_radius=8)
    bar_w = max(3, r.width // 5)
    gap = max(3, bar_w // 2)
    cx, cy = r.center
    pygame.draw.rect(surface, color, (cx - gap - bar_w, cy - 8, bar_w, 16), border_radius=2)
    pygame.draw.rect(surface, color, (cx + gap, cy - 8, bar_w, 16), border_radius=2)


def draw_icon_gear(surface: pygame.Surface, center: tuple[int, int], radius: int, color: tuple[int, int, int]) -> None:
    cx, cy = center
    pygame.draw.circle(surface, color, (cx, cy), radius)
    for i in range(8):
        angle = i * math.pi / 4
        x1 = cx + int(math.cos(angle) * (radius + 2))
        y1 = cy + int(math.sin(angle) * (radius + 2))
        x2 = cx + int(math.cos(angle) * (radius + 6))
        y2 = cy + int(math.sin(angle) * (radius + 6))
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)