"""Main menu — cinematic background, glow title, mouse-driven layout."""

from __future__ import annotations

import math

import pygame

from config.settings import WINDOW_HEIGHT, WINDOW_WIDTH
from src.core.tetromino import SHAPES
from src.systems.platform import is_android, platform_label
from src.systems.settings_store import SettingsStore
from src.ui.blocks import draw_mini_block
import src.ui.colors as colors
from src.ui.fonts import get_font, render_glow_text
from src.ui.menu_background import MenuBackground
from src.ui.themes import THEME_ORDER, get_theme
from src.ui.widgets import UIButton, UIThemeCard, UICursor, _font, draw_glass_panel

PIECE_KINDS = ("I", "O", "T", "S", "Z", "J", "L")


class MainMenuScreen:
    def __init__(self) -> None:
        self.time = 0.0
        self.cursor = UICursor()
        self.background = MenuBackground()
        self.section_font = get_font(16, bold=True)
        self.body_font = get_font(14)
        self._title_surf = render_glow_text("TETRIS", 58, colors.TITLE_TEXT)
        self._rebuild_widgets()

    def _rebuild_widgets(self) -> None:
        cx = WINDOW_WIDTH // 2
        h = WINDOW_HEIGHT
        self.play_btn = UIButton(
            pygame.Rect(cx - 130, int(h * 0.38), 260, 52),
            "▶  PLAY",
            "play",
            style="primary",
            font=_font(22, bold=True),
        )
        self.options_btn = UIButton(
            pygame.Rect(cx - 130, int(h * 0.46), 260, 44),
            "⚙  OPTIONS",
            "options",
            style="secondary",
            font=_font(17, bold=True),
        )
        card_w = max(72, (WINDOW_WIDTH - 80) // len(THEME_ORDER) - 8)
        gap = 8
        total = len(THEME_ORDER) * card_w + (len(THEME_ORDER) - 1) * gap
        x = cx - total // 2
        self.theme_cards: list[UIThemeCard] = []
        for name in THEME_ORDER:
            self.theme_cards.append(
                UIThemeCard(get_theme(name), pygame.Rect(x, int(h * 0.54), card_w, 62))
            )
            x += card_w + gap

    def invalidate(self) -> None:
        self.background.invalidate()
        self._title_surf = render_glow_text("TETRIS", 58, colors.TITLE_TEXT)

    def update(self, dt: float, mouse: tuple[int, int]) -> None:
        self.time += dt
        self.background.update(dt)
        self.play_btn.update(dt, mouse)
        self.options_btn.update(dt, mouse)
        for card in self.theme_cards:
            card.update(dt, mouse)
        hovered = (
            self.play_btn.rect.collidepoint(mouse)
            or self.options_btn.rect.collidepoint(mouse)
            or any(c.rect.collidepoint(mouse) for c in self.theme_cards)
        )
        self.cursor.set_hand(hovered)

    def handle_click(self, mouse: tuple[int, int], settings: SettingsStore) -> str | None:
        if self.play_btn.on_press(mouse):
            return "play"
        if self.options_btn.on_press(mouse):
            return "options"
        for card in self.theme_cards:
            if card.on_press(mouse):
                settings.set_theme(card.theme.name)
                self.sync_theme_selection(settings)
                self.invalidate()
                return "theme"
        return None

    def sync_theme_selection(self, settings: SettingsStore) -> None:
        for card in self.theme_cards:
            card.selected = card.theme.name == settings.theme

    def draw(self, surface: pygame.Surface, high_scores: list[dict[str, int]]) -> None:
        pulse = 0.5 + 0.5 * math.sin(self.time * 2.2)
        cx = WINDOW_WIDTH // 2
        card = pygame.Rect(14, 16, WINDOW_WIDTH - 28, WINDOW_HEIGHT - 32)

        self.background.draw(surface)
        draw_glass_panel(surface, card)

        self._draw_piece_strip(surface, cx, card.y + 20)
        title_rect = self._title_surf.get_rect(center=(cx, card.y + 88))
        surface.blit(self._title_surf, title_rect)
        self._draw_color_bar(surface, title_rect, pulse)

        self.play_btn.draw(surface)
        self.options_btn.draw(surface)

        label = self.body_font.render("THEME", True, (130, 135, 155))
        surface.blit(label, label.get_rect(center=(cx, int(WINDOW_HEIGHT * 0.52))))
        for theme_card in self.theme_cards:
            theme_card.draw(surface)

        self._draw_high_scores(surface, card, high_scores)
        self._draw_footer(surface, card)

    def _draw_footer(self, surface: pygame.Surface, card: pygame.Rect) -> None:
        if is_android():
            label = f"v1.0  •  {platform_label()}  •  Tap board or buttons to play"
        else:
            label = "v1.0  •  Made with Pygame"
        footer = self.body_font.render(label, True, (90, 95, 115))
        surface.blit(footer, footer.get_rect(center=(card.centerx, card.bottom - 18)))

    def _draw_color_bar(self, surface: pygame.Surface, title_rect: pygame.Rect, pulse: float) -> None:
        bar_w = min(240, WINDOW_WIDTH - 80)
        bar_x = title_rect.centerx - bar_w // 2
        bar_y = title_rect.bottom + 12
        seg = bar_w // len(PIECE_KINDS)
        for i, kind in enumerate(PIECE_KINDS):
            color = colors.PIECE_COLORS[kind]
            bright = tuple(min(255, int(c + 40 * pulse)) for c in color)
            pygame.draw.rect(surface, bright, (bar_x + i * seg, bar_y, seg - 1, 5), border_radius=3)

    def _draw_piece_strip(self, surface: pygame.Surface, cx: int, y: int) -> None:
        cell, gap = 11, 6
        piece_w = 4 * cell
        total = len(PIECE_KINDS) * piece_w + (len(PIECE_KINDS) - 1) * gap
        x = cx - total // 2
        for kind in PIECE_KINDS:
            self._draw_piece(surface, kind, x, y, cell=cell, alpha=255)
            x += piece_w + gap

    def _draw_piece(
        self,
        surface: pygame.Surface,
        kind: str,
        x: int,
        y: int,
        *,
        cell: int,
        alpha: int,
    ) -> None:
        offsets = SHAPES[kind][0]
        min_c = min(c for c, _ in offsets)
        min_r = min(r for _, r in offsets)
        max_c = max(c for c, _ in offsets)
        max_r = max(r for _, r in offsets)
        temp = pygame.Surface(
            ((max_c - min_c + 1) * cell + 4, (max_r - min_r + 1) * cell + 4),
            pygame.SRCALPHA,
        )
        for col, row in offsets:
            draw_mini_block(temp, (col - min_c) * cell + 2, (row - min_r) * cell + 2, cell, colors.PIECE_COLORS[kind])
        temp.set_alpha(alpha)
        surface.blit(temp, (x, y))

    def _draw_high_scores(self, surface: pygame.Surface, card: pygame.Rect, high_scores: list[dict[str, int]]) -> None:
        section_y = int(WINDOW_HEIGHT * 0.64)
        left, right = card.x + 24, card.right - 24
        cx = card.centerx
        pygame.draw.line(surface, colors.PANEL_BORDER, (left, section_y), (right, section_y), 1)
        header = self.section_font.render("HIGH SCORES", True, colors.PANEL_TEXT)
        surface.blit(header, header.get_rect(center=(cx, section_y)))

        y = section_y + 24
        if not high_scores:
            empty = self.body_font.render("No scores yet — click Play!", True, (120, 125, 145))
            surface.blit(empty, empty.get_rect(center=(cx, y + 20)))
            return

        for i, entry in enumerate(high_scores[:5], start=1):
            row = pygame.Rect(left, y, right - left, 36)
            if i % 2 == 0:
                stripe = pygame.Surface(row.size, pygame.SRCALPHA)
                stripe.fill((255, 255, 255, 10))
                surface.blit(stripe, row.topleft)
            rank_color = colors.HIGH_SCORE_TEXT if i == 1 else colors.TITLE_TEXT
            rank = self.body_font.render(f"#{i}", True, rank_color)
            score = get_font(16, bold=True).render(f"{entry['score']:,}", True, colors.PANEL_TEXT)
            meta = self.body_font.render(f"Lv {entry['level']} · {entry['lines']} lines", True, (110, 115, 135))
            surface.blit(rank, (left + 8, y + 10))
            surface.blit(score, (left + 42, y + 4))
            surface.blit(meta, (left + 42, y + 20))
            y += 38