"""Cached font loader with display / body / mono families."""

from __future__ import annotations

import pygame

from src.systems.platform import is_android

_CACHE: dict[tuple[str, int, bool], pygame.font.Font] = {}

_FAMILIES = {
    "display": ("bahnschrift", "segoe ui", "arial black", "arial"),
    "body": ("segoe ui", "calibri", "arial", "tahoma"),
    "mono": ("cascadia mono", "consolas", "courier new"),
}


def get_font(size: int, *, bold: bool = False, family: str = "body") -> pygame.font.Font:
    key = (family, size, bold)
    if key in _CACHE:
        return _CACHE[key]
    if is_android():
        font = pygame.font.Font(None, size)
        if bold:
            font.set_bold(True)
        _CACHE[key] = font
        return font
    for name in _FAMILIES.get(family, _FAMILIES["body"]):
        path = pygame.font.match_font(name, bold=bold)
        if path:
            font = pygame.font.Font(path, size)
            _CACHE[key] = font
            return font
    font = pygame.font.SysFont("arial", size, bold=bold)
    _CACHE[key] = font
    return font


def render_glow_text(
    text: str,
    size: int,
    color: tuple[int, int, int],
    *,
    glow_color: tuple[int, int, int] | None = None,
    glow_offsets: int = 3,
) -> pygame.Surface:
    """Title text with layered glow for menus."""
    glow = glow_color or color
    base = get_font(size, bold=True, family="display").render(text, True, color)
    w, h = base.get_size()
    surf = pygame.Surface((w + glow_offsets * 4, h + glow_offsets * 4), pygame.SRCALPHA)
    gfont = get_font(size, bold=True, family="display")
    for i in range(glow_offsets, 0, -1):
        layer = gfont.render(text, True, glow)
        layer.set_alpha(40 + i * 25)
        surf.blit(layer, (glow_offsets + i, glow_offsets + i))
    surf.blit(base, (glow_offsets, glow_offsets))
    return surf