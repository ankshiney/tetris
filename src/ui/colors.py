"""Active color palette — mutate in place so theme changes apply everywhere."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.ui.themes import THEMES, Theme, get_theme


@dataclass
class Palette:
    """Mutable color state shared across the whole game."""

    BACKGROUND: tuple[int, int, int] = (15, 15, 25)
    BG_GRADIENT_TOP: tuple[int, int, int] = (8, 8, 18)
    BG_GRADIENT_BOTTOM: tuple[int, int, int] = (20, 24, 42)
    STAR_TINT: tuple[int, int, int] = (200, 210, 255)
    BOARD_BG: tuple[int, int, int] = (18, 18, 32)
    BOARD_BORDER: tuple[int, int, int] = (70, 130, 220)
    BOARD_BORDER_GLOW: tuple[int, int, int] = (40, 80, 160)
    GRID_LINE: tuple[int, int, int] = (35, 40, 60)
    PANEL_TEXT: tuple[int, int, int] = (200, 200, 220)
    TITLE_TEXT: tuple[int, int, int] = (100, 220, 255)
    GAME_OVER_TEXT: tuple[int, int, int] = (255, 80, 80)
    HIGH_SCORE_TEXT: tuple[int, int, int] = (255, 215, 80)
    LINE_FLASH: tuple[int, int, int] = (255, 255, 255)
    TETRIS_GOLD: tuple[int, int, int] = (255, 200, 60)
    PANEL_BOX: tuple[int, int, int] = (28, 28, 48)
    PANEL_BORDER: tuple[int, int, int] = (55, 65, 100)
    PIECE_COLORS: dict[str, tuple[int, int, int]] = field(default_factory=dict)

    def load(self, theme: Theme) -> None:
        self.BACKGROUND = theme.background
        self.BG_GRADIENT_TOP = theme.bg_gradient_top
        self.BG_GRADIENT_BOTTOM = theme.bg_gradient_bottom
        self.STAR_TINT = theme.star_tint
        self.BOARD_BG = theme.board_bg
        self.BOARD_BORDER = theme.board_border
        self.BOARD_BORDER_GLOW = theme.board_border_glow
        self.GRID_LINE = theme.grid_line
        self.PANEL_TEXT = theme.panel_text
        self.TITLE_TEXT = theme.title_text
        self.GAME_OVER_TEXT = theme.game_over_text
        self.HIGH_SCORE_TEXT = theme.high_score_text
        self.LINE_FLASH = theme.line_flash
        self.TETRIS_GOLD = theme.tetris_gold
        self.PANEL_BOX = theme.panel_box
        self.PANEL_BORDER = theme.panel_border
        self.PIECE_COLORS.clear()
        self.PIECE_COLORS.update(theme.piece_colors)


_palette = Palette()
_current_theme_name = "neon"
_palette.load(get_theme("neon"))


def current_theme_name() -> str:
    return _current_theme_name


def current_theme() -> Theme:
    return get_theme(_current_theme_name)


def apply_theme(name: str) -> str:
    """Apply a theme by name and return the resolved theme name."""
    global _current_theme_name
    theme = get_theme(name)
    _current_theme_name = theme.name
    _palette.load(theme)
    return theme.name


def __getattr__(name: str):
    """Allow `colors.TITLE_TEXT` to always return the live palette value."""
    if hasattr(_palette, name):
        return getattr(_palette, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")