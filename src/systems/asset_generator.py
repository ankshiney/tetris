"""Procedural generation of menu and UI image assets."""

import pygame

from src.systems.paths import assets_dir


def _assets_dir():
    return assets_dir()


def _gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface(size)
    for y in range(h):
        t = y / max(1, h - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(surf, color, (0, y), (w, y))
    return surf


def generate_all_assets() -> None:
    out = _assets_dir()
    out.mkdir(parents=True, exist_ok=True)

    menu_bg = _gradient((520, 680), (12, 14, 28), (24, 30, 52))
    for x in range(0, 520, 40):
        pygame.draw.line(menu_bg, (35, 45, 70), (x, 0), (x, 680), 1)
    for y in range(0, 680, 40):
        pygame.draw.line(menu_bg, (35, 45, 70), (0, y), (520, y), 1)

    panel = pygame.Surface((360, 420), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 24, 40, 210), panel.get_rect(), border_radius=14)
    pygame.draw.rect(panel, (90, 130, 210, 180), panel.get_rect(), 2, border_radius=14)

    logo = pygame.Surface((320, 80), pygame.SRCALPHA)
    font = pygame.font.SysFont("consolas", 54, bold=True)
    for offset, alpha in ((3, 40), (2, 70), (0, 255)):
        text = font.render("TETRIS", True, (80, 180, 255))
        text.set_alpha(alpha)
        logo.blit(text, (offset, offset))

    pause = pygame.Surface((280, 56), pygame.SRCALPHA)
    pygame.draw.rect(pause, (30, 40, 70, 200), pause.get_rect(), border_radius=10)
    pfont = pygame.font.SysFont("consolas", 28, bold=True)
    ptext = pfont.render("PAUSED", True, (120, 210, 255))
    pause.blit(ptext, ptext.get_rect(center=pause.get_rect().center))

    music = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(music, (100, 180, 255, 200), (24, 24), 20)
    for i, h in enumerate((18, 26, 14, 22)):
        pygame.draw.rect(music, (20, 30, 50), (10 + i * 7, 36 - h, 4, h), border_radius=2)

    pygame.image.save(menu_bg, str(out / "menu_bg.png"))
    pygame.image.save(panel, str(out / "panel.png"))
    pygame.image.save(logo, str(out / "logo_glow.png"))
    pygame.image.save(pause, str(out / "pause_banner.png"))
    pygame.image.save(music, str(out / "music_icon.png"))