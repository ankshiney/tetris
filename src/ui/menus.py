"""Pause and options overlays with full mouse support."""

from __future__ import annotations

import pygame

from config.settings import WINDOW_HEIGHT, WINDOW_WIDTH
from src.systems.music_tracks import TRACK_LABELS
from src.systems.platform import is_android
from src.systems.settings_store import DISPLAY_SCALES, SettingsStore
import src.ui.colors as colors
from src.ui.themes import THEME_ORDER, get_theme
from src.ui.widgets import (
    UIButton,
    UICursor,
    UISlider,
    UIThemeCard,
    UIToggle,
    _font,
    draw_glass_panel,
)


class PauseMenu:
    def __init__(self) -> None:
        self.cursor = UICursor()
        self.title_font = _font(30, bold=True)
        self.hint_font = _font(13)
        self._rebuild()

    def _rebuild(self) -> None:
        cx = WINDOW_WIDTH // 2
        y = WINDOW_HEIGHT // 2 - 36
        self.buttons = [
            UIButton(pygame.Rect(cx - 130, y, 260, 46), "▶  Resume", "resume", style="primary", font=_font(18, bold=True)),
            UIButton(pygame.Rect(cx - 130, y + 56, 260, 46), "⚙  Options", "options", style="secondary"),
            UIButton(pygame.Rect(cx - 130, y + 112, 260, 46), "⌂  Quit to Menu", "menu", style="danger"),
        ]

    def update(self, dt: float, mouse: tuple[int, int]) -> None:
        for btn in self.buttons:
            btn.update(dt, mouse)
        self.cursor.set_hand(any(b.rect.collidepoint(mouse) for b in self.buttons))

    def handle_click(self, mouse: tuple[int, int]) -> str | None:
        for btn in self.buttons:
            if btn.on_press(mouse):
                return btn.action
        return None

    def handle_key(self, key: int) -> str | None:
        if key in (pygame.K_p, pygame.K_ESCAPE):
            return "resume"
        if key == pygame.K_o:
            return "options"
        if key == pygame.K_RETURN:
            return "resume"
        return None

    def draw(self, surface: pygame.Surface, assets=None) -> None:
        del assets
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))
        panel = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT // 2 - 170, 320, 340)
        draw_glass_panel(surface, panel)
        title = self.title_font.render("PAUSED", True, colors.TITLE_TEXT)
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.y + 42)))
        for btn in self.buttons:
            btn.draw(surface)
        hint = self.hint_font.render("Click or press Esc to resume", True, (120, 125, 145))
        surface.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 20)))


class OptionsMenu:
    def __init__(self) -> None:
        self.cursor = UICursor()
        self.title_font = _font(26, bold=True)
        self.row_font = _font(14)
        self.hint_font = _font(13)
        self._dragging_slider: UISlider | None = None
        self._rebuild()

    def _rebuild(self) -> None:
        cx = WINDOW_WIDTH // 2
        pw = min(340, WINDOW_WIDTH - 20)
        self.panel = pygame.Rect(cx - pw // 2, 24, pw, WINDOW_HEIGHT - 48)
        self.back_btn = UIButton(
            pygame.Rect(self.panel.x + 14, self.panel.y + 12, 90, 34),
            "← Back",
            "back",
            style="secondary",
            font=_font(14, bold=True),
        )
        card_w = max(68, (pw - 40) // len(THEME_ORDER) - 6)
        self.theme_cards = [
            UIThemeCard(
                get_theme(name),
                pygame.Rect(self.panel.x + 16 + i * (card_w + 6), self.panel.y + 56, card_w, 56),
            )
            for i, name in enumerate(THEME_ORDER)
        ]
        y = self.panel.y + 124
        w = pw - 32
        self.music_track_btn = UIButton(pygame.Rect(self.panel.x + 16, y, w, 36), "", "music_track", style="secondary")
        y += 46
        self.sliders = {
            "music_volume": UISlider(pygame.Rect(self.panel.x + 16, y, w, 38), 0.35, "music_volume"),
            "sfx_volume": UISlider(pygame.Rect(self.panel.x + 16, y + 46, w, 38), 0.8, "sfx_volume"),
        }
        y += 100
        rh = 38
        self.toggles = {
            "music_enabled": UIToggle(pygame.Rect(self.panel.x + 16, y, w, rh), True, "music_enabled"),
            "fullscreen": UIToggle(pygame.Rect(self.panel.x + 16, y + rh, w, rh), False, "fullscreen"),
            "particles": UIToggle(pygame.Rect(self.panel.x + 16, y + rh * 2, w, rh), True, "particles"),
            "touch_controls": UIToggle(pygame.Rect(self.panel.x + 16, y + rh * 3, w, rh), True, "touch_controls"),
        }
        self.scale_btn = UIButton(
            pygame.Rect(self.panel.x + 16, y + rh * 4 + 8, w, 36),
            "",
            "display_scale",
            style="secondary",
        )

    def sync_from_settings(self, settings: SettingsStore) -> None:
        self.sliders["music_volume"].value = settings.music_volume
        self.sliders["sfx_volume"].value = settings.sfx_volume
        self.toggles["music_enabled"].enabled = settings.music_enabled
        self.toggles["fullscreen"].enabled = settings.fullscreen
        self.toggles["particles"].enabled = settings.particles_enabled
        self.toggles["touch_controls"].enabled = settings.touch_controls
        for card in self.theme_cards:
            card.selected = card.theme.name == settings.theme

    def update(self, dt: float, mouse: tuple[int, int]) -> None:
        self.back_btn.update(dt, mouse)
        self.music_track_btn.update(dt, mouse)
        self.scale_btn.update(dt, mouse)
        for card in self.theme_cards:
            card.update(dt, mouse)
        for slider in self.sliders.values():
            slider.update(dt, mouse)
        for toggle in self.toggles.values():
            toggle.update(dt, mouse)
        interactive = (
            self.back_btn.rect.collidepoint(mouse)
            or self.music_track_btn.rect.collidepoint(mouse)
            or self.scale_btn.rect.collidepoint(mouse)
            or any(c.rect.collidepoint(mouse) for c in self.theme_cards)
            or any(s.rect.collidepoint(mouse) for s in self.sliders.values())
            or any(t.rect.collidepoint(mouse) for t in self.toggles.values())
        )
        self.cursor.set_hand(interactive)

    def handle_click(self, mouse: tuple[int, int], settings: SettingsStore) -> str | None:
        if self.back_btn.on_press(mouse):
            return "back"
        for card in self.theme_cards:
            if card.on_press(mouse):
                settings.set_theme(card.theme.name)
                for c in self.theme_cards:
                    c.selected = c.theme.name == settings.theme
                return "changed"
        if self.music_track_btn.on_press(mouse):
            settings.cycle_music_track()
            return "changed"
        if self.scale_btn.on_press(mouse):
            settings.cycle_display_scale()
            return "scale"
        for slider in self.sliders.values():
            if slider.on_press(mouse):
                self._dragging_slider = slider
                if slider.action == "music_volume":
                    settings.music_volume = slider.value
                else:
                    settings.sfx_volume = slider.value
                settings.save()
                return "changed"
        for toggle in self.toggles.values():
            if toggle.on_press(mouse):
                self._apply_toggle(toggle.action, toggle.enabled, settings)
                return "changed"
        return None

    def handle_release(self, settings: SettingsStore) -> str | None:
        if self._dragging_slider:
            self._dragging_slider.on_release()
            self._dragging_slider = None
            settings.save()
            return "changed"
        return None

    def handle_key(self, key: int, settings: SettingsStore) -> str | None:
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            return "back"
        if key == pygame.K_LEFT:
            settings.cycle_music_track(-1)
            return "changed"
        if key == pygame.K_RIGHT:
            settings.cycle_music_track(1)
            return "changed"
        return None

    def _apply_toggle(self, key: str, value: bool, settings: SettingsStore) -> None:
        if key == "music_enabled":
            settings.music_enabled = value
        elif key == "fullscreen":
            settings.fullscreen = value
        elif key == "particles":
            settings.particles_enabled = value
        elif key == "touch_controls":
            settings.touch_controls = value
        settings.save()

    def _track_label(self, settings: SettingsStore) -> str:
        name = TRACK_LABELS.get(settings.music_track, settings.music_track)
        return f"♫  {name}  —  click to cycle"

    def _scale_label(self, settings: SettingsStore) -> str:
        pct = int(settings.display_scale * 100)
        return f"🖥  Window size: {pct}%  —  click to cycle"

    def draw(self, surface: pygame.Surface, settings: SettingsStore, assets=None) -> None:
        del assets
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))
        draw_glass_panel(surface, self.panel)

        title = self.title_font.render("OPTIONS", True, colors.TITLE_TEXT)
        surface.blit(title, title.get_rect(midleft=(self.panel.x + 112, self.panel.y + 30)))
        self.back_btn.draw(surface)

        theme_lbl = self.row_font.render("THEME", True, (120, 125, 145))
        surface.blit(theme_lbl, (self.panel.x + 16, self.panel.y + 42))
        for card in self.theme_cards:
            card.draw(surface)

        self.music_track_btn.label = self._track_label(settings)
        self.music_track_btn.draw(surface)
        self.sliders["music_volume"].draw(surface, "Music volume")
        self.sliders["sfx_volume"].draw(surface, "SFX volume")
        self.toggles["music_enabled"].draw(surface, "Music")
        if not is_android():
            self.toggles["fullscreen"].draw(surface, "Fullscreen")
        self.toggles["particles"].draw(surface, "Particles")
        self.toggles["touch_controls"].draw(surface, "Touch controls")
        if not is_android():
            self.scale_btn.label = self._scale_label(settings)
            self.scale_btn.draw(surface)

        hint_text = "Drag sliders · tap toggles · Back to close" if is_android() else "Drag sliders · click toggles · Esc back"
        hint = self.hint_font.render(hint_text, True, (115, 120, 140))
        surface.blit(hint, hint.get_rect(center=(self.panel.centerx, self.panel.bottom - 14)))