"""Draw the board grid and tetromino blocks onto the screen."""

import pygame

from config.settings import (
    BOARD_ORIGIN_X,
    BOARD_ORIGIN_Y,
    BOARD_PIXEL_HEIGHT,
    BOARD_PIXEL_WIDTH,
    CELL_SIZE,
    COLS,
    GRID_LINE_WIDTH,
    HIDDEN_ROWS,
    ROWS,
)
from src.core.board import Board
from src.core.tetromino import Tetromino
from src.ui.block_cache import BlockCache
from src.ui.blocks import lighten
import src.ui.colors as colors


class Renderer:
    """Converts grid coordinates into pixel positions and draws them."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.cache = BlockCache()
        self._shake_x = 0
        self._shake_y = 0
        self._glow_pulse = 0.0
        self._wave_x = -1.0

    @property
    def board_origin(self) -> tuple[int, int]:
        return (BOARD_ORIGIN_X + self._shake_x, BOARD_ORIGIN_Y + self._shake_y)

    def invalidate_cache(self) -> None:
        self.cache.clear()

    def set_shake(self, ox: int, oy: int) -> None:
        self._shake_x = ox
        self._shake_y = oy

    def set_glow_pulse(self, value: float) -> None:
        self._glow_pulse = max(0.0, min(1.0, value))

    def set_clear_wave(self, progress: float) -> None:
        self._wave_x = progress * (COLS + 1)

    def _grid_to_pixel(self, col: int, row: int, *, y_offset: float = 0.0, x_offset: float = 0.0) -> tuple[int, int]:
        visible_row = row - HIDDEN_ROWS
        x = self.board_origin[0] + col * CELL_SIZE + int(x_offset)
        y = self.board_origin[1] + visible_row * CELL_SIZE + int(y_offset)
        return x, y

    def draw_board_background(self) -> None:
        ox, oy = self.board_origin
        board_rect = pygame.Rect(ox, oy, BOARD_PIXEL_WIDTH, BOARD_PIXEL_HEIGHT)

        glow_size = 8 + int(6 * self._glow_pulse)
        glow_rect = board_rect.inflate(glow_size * 2, glow_size * 2)
        glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        alpha = int(50 + 100 * self._glow_pulse)
        pygame.draw.rect(glow_surf, (*colors.BOARD_BORDER_GLOW, alpha), glow_surf.get_rect(), border_radius=10)
        self.screen.blit(glow_surf, glow_rect.topleft)

        frame = board_rect.inflate(6, 6)
        pygame.draw.rect(self.screen, colors.BOARD_BORDER, frame, 3, border_radius=8)
        inner_frame = frame.inflate(-4, -4)
        pygame.draw.rect(self.screen, lighten(colors.BOARD_BORDER, 40), inner_frame, 1, border_radius=6)
        pygame.draw.rect(self.screen, colors.BOARD_BG, board_rect, border_radius=4)

        for col in range(COLS + 1):
            x = ox + col * CELL_SIZE
            pygame.draw.line(self.screen, colors.GRID_LINE, (x, oy), (x, oy + BOARD_PIXEL_HEIGHT), GRID_LINE_WIDTH)

        for row in range(ROWS + 1):
            y = oy + row * CELL_SIZE
            pygame.draw.line(self.screen, colors.GRID_LINE, (ox, y), (ox + BOARD_PIXEL_WIDTH, y), GRID_LINE_WIDTH)

    def _blit_block(
        self,
        col: int,
        row: int,
        color: tuple[int, int, int],
        *,
        ghost: bool = False,
        alpha: int = 255,
        shrink: float = 0.0,
        y_offset: float = 0.0,
        x_offset: float = 0.0,
        squash: float = 1.0,
    ) -> None:
        if row < HIDDEN_ROWS:
            return

        x, y = self._grid_to_pixel(col, row, y_offset=y_offset, x_offset=x_offset)
        margin = 1 + int(shrink * (CELL_SIZE // 2))
        w = CELL_SIZE - 2 * margin
        h = max(1, int((CELL_SIZE - 2 * margin) * squash))
        if w <= 0 or h <= 0 or alpha <= 0:
            return
        y_adjust = (CELL_SIZE - 2 * margin) - h
        cell_rect = pygame.Rect(x + margin, y + margin + y_adjust, w, h)

        if ghost:
            sprite = self.cache.get_ghost(color, w)
        else:
            sprite = self.cache.get_cell(color, w, alpha=alpha)
        if alpha < 255 and not ghost:
            sprite = sprite.copy()
            sprite.set_alpha(alpha)
        self.screen.blit(sprite, cell_rect.topleft)

    def draw_locked_cells(
        self,
        board: Board,
        flashing_rows: list[int] | None = None,
        clear_progress: float = 0.0,
        row_fall=None,
    ) -> None:
        for row in range(HIDDEN_ROWS, HIDDEN_ROWS + ROWS):
            for col in range(COLS):
                kind = board.grid[row][col]
                if kind is None:
                    continue

                fall_offset = row_fall.offset_for(col, row) if row_fall else 0.0
                color = colors.PIECE_COLORS[kind]
                shrink = 0.0
                alpha = 255

                if flashing_rows and row in flashing_rows:
                    wave_boost = 0.0
                    if self._wave_x >= 0 and abs(col - self._wave_x) < 1.2:
                        wave_boost = 1.0
                    pulse = abs((clear_progress * 8) % 2 - 1)
                    if clear_progress < 0.5:
                        color = colors.LINE_FLASH if pulse > 0.4 or wave_boost else colors.PIECE_COLORS[kind]
                    else:
                        fade = (clear_progress - 0.5) / 0.5
                        color = lighten(colors.PIECE_COLORS[kind], int(30 * (1 - fade)))
                        shrink = fade * 0.9
                        alpha = int(255 * (1 - fade * 0.95))

                self._blit_block(
                    col,
                    row,
                    color,
                    shrink=shrink,
                    alpha=alpha,
                    y_offset=fall_offset,
                )

    def draw_piece_shadow(self, piece: Tetromino, y_offset: float, x_offset: float) -> None:
        shadow_a = 45
        for col, row in piece.cells:
            if row < HIDDEN_ROWS:
                continue
            x, y = self._grid_to_pixel(col, row, y_offset=y_offset + 3, x_offset=x_offset + 2)
            rect = pygame.Rect(x + 4, y + 5, CELL_SIZE - 8, CELL_SIZE - 8)
            shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, shadow_a))
            self.screen.blit(shadow, rect.topleft)

    def draw_ghost_piece(self, piece: Tetromino) -> None:
        for col, row in piece.cells:
            self._blit_block(col, row, piece.color, ghost=True)

    def draw_piece(
        self,
        piece: Tetromino,
        *,
        y_offset: float = 0.0,
        x_offset: float = 0.0,
        alpha: int = 255,
        squash: float = 1.0,
    ) -> None:
        self.draw_piece_shadow(piece, y_offset, x_offset)
        for col, row in piece.cells:
            self._blit_block(
                col,
                row,
                piece.color,
                alpha=alpha,
                y_offset=y_offset,
                x_offset=x_offset,
                squash=squash,
            )