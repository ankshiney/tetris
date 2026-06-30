"""Side-panel UI, overlays, and in-game touch controls."""

from __future__ import annotations

import pygame

from config.settings import (
    BOARD_ORIGIN_X,
    BOARD_ORIGIN_Y,
    BOARD_PADDING,
    BOARD_PIXEL_HEIGHT,
    BOARD_PIXEL_WIDTH,
    LEFT_PANEL_X,
    NEXT_QUEUE_CELL_SIZE,
    NEXT_QUEUE_COUNT,
    PANEL_WIDTH,
    PREVIEW_CELL_SIZE,
    RIGHT_PANEL_X,
    SIDE_PANEL_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.core.tetromino import SHAPES
from src.ui.blocks import draw_mini_block
import src.ui.colors as colors
from src.ui.fonts import get_font
from src.systems.platform import is_mobile
from src.ui.widgets import UIButton, UICursor, _font, draw_glass_panel, draw_icon_pause

LINES_PER_LEVEL = 10


class HUD:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.title_font = get_font(18, bold=True)
        self.stat_font = get_font(17, bold=True)
        self.score_font = get_font(22, bold=True)
        self.stat_label = get_font(13)
        self.overlay_font = get_font(38, bold=True, family="display")
        self.hint_font = get_font(16)
        self.small_font = get_font(13)
        self.left_panel_x = LEFT_PANEL_X
        self.right_panel_x = RIGHT_PANEL_X
        self.hold_flash = 0.0
        self.level_pulse = 0.0
        self.ui_cursor = UICursor()
        self._layout_widgets()

    def _layout_widgets(self) -> None:
        self.pause_btn = UIButton(
            pygame.Rect(WINDOW_WIDTH - BOARD_PADDING - 50, BOARD_ORIGIN_Y, 46, 46),
            "",
            "pause",
            style="secondary",
        )
        cx = BOARD_ORIGIN_X + BOARD_PIXEL_WIDTH // 2
        panel_cy = BOARD_ORIGIN_Y + BOARD_PIXEL_HEIGHT // 2 + 50
        self.restart_btn = UIButton(
            pygame.Rect(cx - 130, panel_cy, 120, 44),
            "↻ Restart",
            "restart",
            style="primary",
            font=_font(17, bold=True),
        )
        self.menu_btn = UIButton(
            pygame.Rect(cx + 10, panel_cy, 120, 44),
            "⌂ Menu",
            "menu",
            style="secondary",
            font=_font(17, bold=True),
        )
        touch_y = BOARD_ORIGIN_Y + BOARD_PIXEL_HEIGHT - 138
        tw, gap = (64, 12) if is_mobile() else (58, 10)
        tx = self.right_panel_x + 10
        self.touch_left = UIButton(pygame.Rect(tx, touch_y, tw, 38), "◀", "left", style="secondary", font=_font(20, bold=True))
        self.touch_right = UIButton(pygame.Rect(tx + tw + gap, touch_y, tw, 38), "▶", "right", style="secondary", font=_font(20, bold=True))
        self.touch_rotate = UIButton(pygame.Rect(tx, touch_y + 44, tw, 38), "↻", "rotate", style="secondary", font=_font(20, bold=True))
        self.touch_soft = UIButton(pygame.Rect(tx + tw + gap, touch_y + 44, tw, 38), "▽", "soft_drop", style="secondary", font=_font(18, bold=True))
        self.touch_drop = UIButton(pygame.Rect(tx, touch_y + 88, tw, 38), "⬇", "hard_drop", style="primary", font=_font(20, bold=True))
        self.touch_hold = UIButton(
            pygame.Rect(tx + tw + gap, touch_y + 88, tw, 38),
            "C",
            "hold",
            style="secondary",
            font=_font(18, bold=True),
        )

    def trigger_hold_flash(self) -> None:
        self.hold_flash = 1.0

    def trigger_level_pulse(self) -> None:
        self.level_pulse = 1.0

    def update(self, dt: float, mouse: tuple[int, int] = (0, 0), *, ui_state: str = "", touch_enabled: bool = True) -> None:
        if self.hold_flash > 0:
            self.hold_flash = max(0.0, self.hold_flash - dt * 3.5)
        if self.level_pulse > 0:
            self.level_pulse = max(0.0, self.level_pulse - dt * 2.5)

        if ui_state == "playing":
            buttons = [self.pause_btn]
            if touch_enabled:
                buttons.extend([
                    self.touch_left, self.touch_right, self.touch_rotate,
                    self.touch_soft, self.touch_drop, self.touch_hold,
                ])
            for btn in buttons:
                btn.update(dt, mouse)
            self.ui_cursor.set_hand(any(b.rect.collidepoint(mouse) for b in buttons))
        elif ui_state == "game_over":
            self.restart_btn.update(dt, mouse)
            self.menu_btn.update(dt, mouse)
            self.ui_cursor.set_hand(
                self.restart_btn.rect.collidepoint(mouse) or self.menu_btn.rect.collidepoint(mouse)
            )
        else:
            self.ui_cursor.set_hand(False)

    def handle_click(self, mouse: tuple[int, int], ui_state: str, *, touch_enabled: bool = True) -> str | None:
        if ui_state == "playing":
            if self.pause_btn.on_press(mouse):
                return "pause"
            if touch_enabled:
                for btn in (self.touch_left, self.touch_right, self.touch_rotate, self.touch_soft, self.touch_drop, self.touch_hold):
                    if btn.on_press(mouse):
                        return btn.action
        if ui_state == "game_over":
            if self.restart_btn.on_press(mouse):
                return "restart"
            if self.menu_btn.on_press(mouse):
                return "menu"
        return None

    def board_click_action(self, mouse: tuple[int, int]) -> str | None:
        """Click board zones: left/right move, top rotate, bottom hard drop."""
        board = pygame.Rect(BOARD_ORIGIN_X, BOARD_ORIGIN_Y, BOARD_PIXEL_WIDTH, BOARD_PIXEL_HEIGHT)
        if not board.collidepoint(mouse):
            return None
        rel_x = mouse[0] - BOARD_ORIGIN_X
        rel_y = mouse[1] - BOARD_ORIGIN_Y
        third = BOARD_PIXEL_WIDTH // 3
        if rel_y < BOARD_PIXEL_HEIGHT * 0.25:
            return "rotate"
        if rel_y > BOARD_PIXEL_HEIGHT * 0.82:
            return "hard_drop"
        if rel_x < third:
            return "left"
        if rel_x > third * 2:
            return "right"
        return "soft_drop"

    def draw_play_chrome(self, *, touch_enabled: bool = True) -> None:
        draw_icon_pause(self.screen, self.pause_btn.rect, colors.TITLE_TEXT, self.pause_btn.hover)
        if not touch_enabled:
            return
        box_y = BOARD_ORIGIN_Y + BOARD_PIXEL_HEIGHT - 148
        self._draw_glass_box(self.right_panel_x, box_y, 140)
        label = self.small_font.render("CONTROLS", True, (110, 115, 135))
        self.screen.blit(label, (self.right_panel_x + 12, box_y + 6))
        for btn in (self.touch_left, self.touch_right, self.touch_rotate, self.touch_soft, self.touch_drop, self.touch_hold):
            btn.draw(self.screen)

    def _draw_glass_box(self, x: int, y: int, height: int, *, width: int | None = None) -> pygame.Rect:
        w = width or (SIDE_PANEL_WIDTH - 16)
        box = pygame.Rect(x - 4, y, w, height)
        inner = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(inner, (*colors.PANEL_BOX, 210), inner.get_rect(), border_radius=10)
        pygame.draw.rect(inner, (*colors.PANEL_BORDER, 200), inner.get_rect(), 1, border_radius=10)
        self.screen.blit(inner, box.topleft)
        return box

    def _draw_piece_preview(
        self,
        kind: str | None,
        origin_x: int,
        origin_y: int,
        *,
        cell_size: int = PREVIEW_CELL_SIZE,
        alpha: int = 255,
    ) -> None:
        if kind is None:
            return
        preview_box = 4 * cell_size
        offsets = SHAPES[kind][0]
        min_col = min(col for col, _ in offsets)
        max_col = max(col for col, _ in offsets)
        min_row = min(row for _, row in offsets)
        max_row = max(row for _, row in offsets)
        piece_width = (max_col - min_col + 1) * cell_size
        piece_height = (max_row - min_row + 1) * cell_size
        x0 = origin_x + (preview_box - piece_width) // 2
        y0 = origin_y + (preview_box - piece_height) // 2
        color = colors.PIECE_COLORS[kind]
        for col, row in offsets:
            draw_mini_block(
                self.screen,
                x0 + (col - min_col) * cell_size,
                y0 + (row - min_row) * cell_size,
                cell_size,
                color,
                alpha=alpha,
            )

    def draw_hold_piece(self, kind: str | None, can_hold: bool) -> None:
        y = BOARD_ORIGIN_Y + (BOARD_PIXEL_HEIGHT - 118) // 2
        box = self._draw_glass_box(self.left_panel_x, y, 118)
        if self.hold_flash > 0:
            glow = pygame.Surface(box.size, pygame.SRCALPHA)
            alpha = int(120 * self.hold_flash)
            pygame.draw.rect(glow, (*colors.TITLE_TEXT, alpha), glow.get_rect(), 3, border_radius=10)
            self.screen.blit(glow, box.topleft)

        label_color = colors.TITLE_TEXT if self.hold_flash > 0 else (colors.PANEL_TEXT if can_hold else (90, 90, 110))
        label = self.title_font.render("HOLD", True, label_color)
        self.screen.blit(label, (self.left_panel_x + 10, y + 8))
        if kind is not None:
            self._draw_piece_preview(kind, self.left_panel_x + 8, y + 34)

    def draw_next_queue(self, kinds: list[str]) -> None:
        stats_h = 148
        y = BOARD_ORIGIN_Y + stats_h + 10
        slot_h = 52
        queue_h = 28 + slot_h * min(len(kinds), NEXT_QUEUE_COUNT)
        self._draw_glass_box(self.right_panel_x, y, queue_h)
        label = self.title_font.render("NEXT", True, colors.TITLE_TEXT)
        self.screen.blit(label, (self.right_panel_x + 10, y + 8))

        for i, kind in enumerate(kinds[:NEXT_QUEUE_COUNT]):
            slot_y = y + 30 + i * slot_h
            alpha = 255 if i == 0 else max(120, 200 - i * 30)
            self._draw_piece_preview(
                kind,
                self.right_panel_x + 8,
                slot_y,
                cell_size=NEXT_QUEUE_CELL_SIZE,
                alpha=alpha,
            )

    def draw_stats(
        self,
        score: int,
        lines: int,
        level: int,
        combo: int,
        *,
        display_score: int | None = None,
    ) -> None:
        y = BOARD_ORIGIN_Y
        self._draw_glass_box(self.right_panel_x, y, 148)
        inner_y = y + 12
        shown = display_score if display_score is not None else score

        score_lbl = self.stat_label.render("SCORE", True, (120, 125, 145))
        score_val = self.score_font.render(f"{shown:,}", True, colors.PANEL_TEXT)
        self.screen.blit(score_lbl, (self.right_panel_x + 10, inner_y))
        self.screen.blit(score_val, (self.right_panel_x + 10, inner_y + 14))

        inner_y += 54
        for lbl, val in (("LEVEL", level), ("LINES", lines)):
            t = self.stat_label.render(lbl, True, (120, 125, 145))
            if lbl == "LEVEL" and self.level_pulse > 0:
                pulse = 0.5 + 0.5 * self.level_pulse
                val_color = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in colors.TITLE_TEXT)
                scale = 1.0 + 0.18 * self.level_pulse
                v_surf = self.stat_font.render(str(val), True, val_color)
                w = max(1, int(v_surf.get_width() * scale))
                h = max(1, int(v_surf.get_height() * scale))
                v = pygame.transform.smoothscale(v_surf, (w, h))
            else:
                val_color = colors.TITLE_TEXT if lbl == "LEVEL" else colors.PANEL_TEXT
                v = self.stat_font.render(str(val), True, val_color)
            self.screen.blit(t, (self.right_panel_x + 10, inner_y))
            self.screen.blit(v, (self.right_panel_x + 80, inner_y - 2))
            inner_y += 28

        if combo > 0:
            combo_surf = self.stat_font.render(f"COMBO ×{combo}", True, colors.HIGH_SCORE_TEXT)
            self.screen.blit(combo_surf, (self.right_panel_x + 10, inner_y))

        progress = (lines % LINES_PER_LEVEL) / LINES_PER_LEVEL
        bar = pygame.Rect(self.right_panel_x + 10, y + 128, PANEL_WIDTH - 36, 8)
        pygame.draw.rect(self.screen, (35, 38, 55), bar, border_radius=4)
        fill = pygame.Rect(bar.x, bar.y, max(4, int(bar.width * progress)), bar.height)
        pygame.draw.rect(self.screen, colors.BOARD_BORDER, fill, border_radius=4)

    def draw_theme_toast(self, theme_label: str, alpha: float) -> None:
        if alpha <= 0:
            return
        text = self.hint_font.render(f"Theme: {theme_label}", True, colors.TITLE_TEXT)
        text.set_alpha(int(255 * alpha))
        rect = text.get_rect(center=(BOARD_ORIGIN_X + BOARD_PIXEL_WIDTH // 2, BOARD_ORIGIN_Y + 28))
        self.screen.blit(text, rect)

    def draw_game_over(self, score: int, is_high_score: bool, rank: int) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(
            BOARD_ORIGIN_X - 10,
            BOARD_ORIGIN_Y + BOARD_PIXEL_HEIGHT // 2 - 130,
            BOARD_PIXEL_WIDTH + 20,
            260,
        )
        draw_glass_panel(self.screen, panel)

        cx = BOARD_ORIGIN_X + BOARD_PIXEL_WIDTH // 2
        cy = panel.y + 54
        text = self.overlay_font.render("GAME OVER", True, colors.GAME_OVER_TEXT)
        self.screen.blit(text, text.get_rect(center=(cx, cy)))
        score_line = self.hint_font.render(f"Score: {score:,}", True, colors.PANEL_TEXT)
        self.screen.blit(score_line, score_line.get_rect(center=(cx, cy + 48)))
        if is_high_score:
            hs = self.hint_font.render(f"NEW HIGH SCORE! (#{rank})", True, colors.HIGH_SCORE_TEXT)
            self.screen.blit(hs, hs.get_rect(center=(cx, cy + 80)))

        btn_y = panel.bottom - 62
        self.restart_btn.rect.topleft = (cx - 130, btn_y)
        self.menu_btn.rect.topleft = (cx + 10, btn_y)
        self.restart_btn.draw(self.screen)
        self.menu_btn.draw(self.screen)