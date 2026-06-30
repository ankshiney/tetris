"""Visual themes — neon, retro, and monochrome."""

from dataclasses import dataclass
THEME_ORDER = ["neon", "retro", "cyber", "mono"]


@dataclass(frozen=True)
class Theme:
    name: str
    label: str
    background: tuple[int, int, int]
    bg_gradient_top: tuple[int, int, int]
    bg_gradient_bottom: tuple[int, int, int]
    star_tint: tuple[int, int, int]
    board_bg: tuple[int, int, int]
    board_border: tuple[int, int, int]
    board_border_glow: tuple[int, int, int]
    grid_line: tuple[int, int, int]
    panel_text: tuple[int, int, int]
    title_text: tuple[int, int, int]
    game_over_text: tuple[int, int, int]
    high_score_text: tuple[int, int, int]
    line_flash: tuple[int, int, int]
    tetris_gold: tuple[int, int, int]
    panel_box: tuple[int, int, int]
    panel_border: tuple[int, int, int]
    piece_colors: dict[str, tuple[int, int, int]]


THEMES: dict[str, Theme] = {
    "neon": Theme(
        name="neon",
        label="Neon",
        background=(15, 15, 25),
        bg_gradient_top=(8, 8, 18),
        bg_gradient_bottom=(20, 24, 42),
        star_tint=(200, 210, 255),
        board_bg=(17, 17, 17),
        board_border=(70, 130, 220),
        board_border_glow=(40, 80, 160),
        grid_line=(34, 34, 34),
        panel_text=(200, 200, 220),
        title_text=(100, 220, 255),
        game_over_text=(255, 80, 80),
        high_score_text=(255, 215, 80),
        line_flash=(255, 255, 255),
        tetris_gold=(255, 200, 60),
        panel_box=(28, 28, 48),
        panel_border=(55, 65, 100),
        piece_colors={
            "I": (0, 240, 240),
            "O": (240, 220, 0),
            "T": (180, 60, 255),
            "S": (40, 220, 80),
            "Z": (240, 50, 60),
            "J": (60, 100, 255),
            "L": (255, 150, 40),
        },
    ),
    "retro": Theme(
        name="retro",
        label="Retro",
        background=(12, 10, 22),
        bg_gradient_top=(10, 8, 28),
        bg_gradient_bottom=(28, 18, 48),
        star_tint=(255, 180, 120),
        board_bg=(22, 16, 36),
        board_border=(220, 120, 60),
        board_border_glow=(140, 60, 30),
        grid_line=(50, 35, 55),
        panel_text=(230, 200, 160),
        title_text=(255, 180, 80),
        game_over_text=(255, 60, 60),
        high_score_text=(255, 230, 100),
        line_flash=(255, 240, 200),
        tetris_gold=(255, 210, 50),
        panel_box=(36, 24, 40),
        panel_border=(100, 60, 40),
        piece_colors={
            "I": (0, 200, 220),
            "O": (220, 200, 0),
            "T": (180, 40, 200),
            "S": (60, 200, 60),
            "Z": (220, 40, 40),
            "J": (40, 60, 220),
            "L": (220, 120, 20),
        },
    ),
    "cyber": Theme(
        name="cyber",
        label="Cyber",
        background=(8, 6, 18),
        bg_gradient_top=(12, 8, 32),
        bg_gradient_bottom=(28, 12, 48),
        star_tint=(255, 100, 200),
        board_bg=(16, 10, 28),
        board_border=(255, 60, 180),
        board_border_glow=(140, 30, 120),
        grid_line=(45, 25, 55),
        panel_text=(230, 200, 240),
        title_text=(255, 120, 220),
        game_over_text=(255, 70, 120),
        high_score_text=(255, 200, 120),
        line_flash=(255, 180, 255),
        tetris_gold=(255, 180, 80),
        panel_box=(32, 18, 42),
        panel_border=(90, 40, 100),
        piece_colors={
            "I": (0, 255, 255),
            "O": (255, 230, 0),
            "T": (200, 80, 255),
            "S": (80, 255, 140),
            "Z": (255, 60, 100),
            "J": (80, 120, 255),
            "L": (255, 140, 60),
        },
    ),
    "mono": Theme(
        name="mono",
        label="Mono",
        background=(10, 10, 12),
        bg_gradient_top=(8, 8, 10),
        bg_gradient_bottom=(18, 18, 22),
        star_tint=(160, 160, 170),
        board_bg=(16, 16, 20),
        board_border=(120, 120, 130),
        board_border_glow=(60, 60, 70),
        grid_line=(32, 32, 38),
        panel_text=(190, 190, 200),
        title_text=(230, 230, 240),
        game_over_text=(220, 100, 100),
        high_score_text=(200, 200, 210),
        line_flash=(240, 240, 245),
        tetris_gold=(210, 210, 220),
        panel_box=(22, 22, 26),
        panel_border=(50, 50, 58),
        piece_colors={
            "I": (180, 220, 255),
            "O": (220, 220, 180),
            "T": (200, 160, 220),
            "S": (160, 210, 170),
            "Z": (220, 160, 160),
            "J": (160, 170, 220),
            "L": (220, 190, 140),
        },
    ),
}


def get_theme(name: str) -> Theme:
    return THEMES.get(name, THEMES["neon"])


def next_theme_name(current: str) -> str:
    try:
        idx = THEME_ORDER.index(current)
    except ValueError:
        return THEME_ORDER[0]
    return THEME_ORDER[(idx + 1) % len(THEME_ORDER)]