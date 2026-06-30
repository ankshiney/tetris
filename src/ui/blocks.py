"""Glossy block rendering shared by the board and HUD previews."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.ui.block_cache import BlockCache

MIN_GLOSSY_SIZE = 8


def _clamp(value: int) -> int:
    return max(0, min(255, value))


def darken(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(_clamp(c - amount) for c in color)


def lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(_clamp(c + amount) for c in color)


def _apply_surface_alpha(surf: pygame.Surface, alpha: int) -> pygame.Surface:
    if alpha >= 255:
        return surf
    result = surf.copy()
    result.set_alpha(alpha)
    return result


def _simple_block(size: int, color: tuple[int, int, int], *, ghost: bool, alpha: int) -> pygame.Surface:
    """Fallback sprite for tiny blocks during shrink animations."""
    size = max(1, size)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = surf.get_rect()
    if ghost:
        pygame.draw.rect(surf, lighten(color, 40), rect, 1, border_radius=max(1, size // 4))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=max(1, size // 4))
    return _apply_surface_alpha(surf, alpha)


def build_block_surface(
    size: int,
    color: tuple[int, int, int],
    *,
    alpha: int = 255,
    ghost: bool = False,
) -> pygame.Surface:
    """Build a cached block sprite with mobile-style depth."""
    size = max(1, int(size))
    if size < MIN_GLOSSY_SIZE:
        return _simple_block(size, color, ghost=ghost, alpha=alpha)

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    inner = pygame.Rect(1, 1, size - 2, size - 2)

    if ghost:
        pygame.draw.rect(surf, lighten(color, 40), inner, 2, border_radius=max(2, size // 6))
        if inner.width > 0 and inner.height > 0:
            inner_fill = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
            pygame.draw.rect(inner_fill, color, inner_fill.get_rect(), border_radius=max(1, size // 8))
            inner_fill.set_alpha(35)
            surf.blit(inner_fill, inner.topleft)
        return _apply_surface_alpha(surf, alpha)

    body = darken(color, 35)
    for i in range(inner.height):
        t = i / max(1, inner.height - 1)
        row_color = (
            _clamp(int(body[0] + (color[0] - body[0]) * (1 - t) * 0.35)),
            _clamp(int(body[1] + (color[1] - body[1]) * (1 - t) * 0.35)),
            _clamp(int(body[2] + (color[2] - body[2]) * (1 - t) * 0.35)),
        )
        pygame.draw.line(surf, row_color, (inner.x, inner.y + i), (inner.right - 1, inner.y + i))

    pygame.draw.rect(surf, lighten(color, 65), inner, border_radius=max(2, size // 6))

    highlight = pygame.Rect(inner.x + 1, inner.y + 1, max(1, inner.width - 2), max(2, inner.height // 3))
    if highlight.width > 0 and highlight.height > 0:
        highlight_surf = pygame.Surface((highlight.width, highlight.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, lighten(color, 95), highlight_surf.get_rect(), border_radius=2)
        highlight_surf.set_alpha(128)
        surf.blit(highlight_surf, highlight.topleft)

    shadow_h = max(2, inner.height // 4)
    shadow = pygame.Rect(inner.x + 1, inner.bottom - shadow_h, max(1, inner.width - 2), shadow_h)
    if shadow.width > 0 and shadow.height > 0:
        pygame.draw.rect(surf, darken(color, 70), shadow, border_radius=1)

    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(glow, lighten(color, 30), glow.get_rect(), border_radius=max(2, size // 5))
    glow.set_alpha(40)
    surf.blit(glow, (0, 0))

    return _apply_surface_alpha(surf, alpha)


def draw_glossy_block(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: tuple[int, int, int],
    *,
    outline_only: bool = False,
    alpha: int = 255,
) -> None:
    if rect.width <= 0 or rect.height <= 0:
        return
    sprite = build_block_surface(rect.width, color, alpha=alpha, ghost=outline_only)
    surface.blit(sprite, rect.topleft)


def draw_mini_block(
    surface: pygame.Surface,
    x: int,
    y: int,
    size: int,
    color: tuple[int, int, int],
    cache: "BlockCache | None" = None,
    *,
    alpha: int = 255,
) -> None:
    if cache is not None and alpha >= 255:
        sprite = cache.get_mini(color, size)
        surface.blit(sprite, (x + 1, y + 1))
        return
    rect = pygame.Rect(x + 1, y + 1, size - 2, size - 2)
    draw_glossy_block(surface, rect, color, alpha=alpha)