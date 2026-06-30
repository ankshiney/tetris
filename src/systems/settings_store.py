"""Persist user preferences between sessions."""

import json

from config.settings import DEFAULT_DISPLAY_SCALE
from src.systems.music_tracks import MUSIC_TRACK_ORDER
from src.systems.paths import data_dir, seed_android_data, settings_file
from src.systems.platform import is_mobile
from src.ui.colors import apply_theme
from src.ui.themes import THEME_ORDER, THEMES

DISPLAY_SCALES = (1.0, 1.15, 1.25, 1.5)

DEFAULTS = {
    "theme": "neon",
    "music_track": "chill",
    "music_volume": 0.35,
    "sfx_volume": 0.8,
    "music_enabled": True,
    "fullscreen": False,
    "particles_enabled": True,
    "display_scale": DEFAULT_DISPLAY_SCALE,
    "touch_controls": True,
}

MOBILE_DEFAULTS = {
    **DEFAULTS,
    "fullscreen": True,
    "touch_controls": True,
    "display_scale": 1.0,
    "particles_enabled": True,
    "music_enabled": False,
}


class SettingsStore:
    """Load and save display/audio preferences."""

    def __init__(self) -> None:
        seed_android_data()
        defaults = MOBILE_DEFAULTS if is_mobile() else DEFAULTS
        self.theme = defaults["theme"]
        self.music_track = defaults["music_track"]
        self.music_volume = defaults["music_volume"]
        self.sfx_volume = defaults["sfx_volume"]
        self.music_enabled = defaults["music_enabled"]
        self.fullscreen = defaults["fullscreen"]
        self.particles_enabled = defaults["particles_enabled"]
        self.display_scale = defaults["display_scale"]
        self.touch_controls = defaults["touch_controls"]
        self._load()

    def _load(self) -> None:
        path = settings_file()
        if not path.exists():
            apply_theme(self.theme)
            return
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.theme = data.get("theme", self.theme)
                if self.theme not in THEMES:
                    self.theme = "neon"
                self.music_track = data.get("music_track", self.music_track)
                if self.music_track not in MUSIC_TRACK_ORDER:
                    self.music_track = "chill"
                self.music_volume = float(data.get("music_volume", self.music_volume))
                self.sfx_volume = float(data.get("sfx_volume", self.sfx_volume))
                self.music_enabled = bool(data.get("music_enabled", self.music_enabled))
                self.fullscreen = bool(data.get("fullscreen", self.fullscreen))
                self.particles_enabled = bool(data.get("particles_enabled", self.particles_enabled))
                self.display_scale = float(data.get("display_scale", self.display_scale))
                if not any(abs(s - self.display_scale) < 0.01 for s in DISPLAY_SCALES):
                    self.display_scale = DEFAULT_DISPLAY_SCALE
                self.touch_controls = bool(data.get("touch_controls", self.touch_controls))
        except (json.JSONDecodeError, OSError, ValueError):
            pass
        apply_theme(self.theme)

    def save(self) -> None:
        data_dir()
        payload = {
            "theme": self.theme,
            "music_track": self.music_track,
            "music_volume": round(self.music_volume, 2),
            "sfx_volume": round(self.sfx_volume, 2),
            "music_enabled": self.music_enabled,
            "fullscreen": self.fullscreen,
            "particles_enabled": self.particles_enabled,
            "display_scale": self.display_scale,
            "touch_controls": self.touch_controls,
        }
        with settings_file().open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def _cycle_list(self, current: str, order: list[str], direction: int) -> str:
        try:
            idx = order.index(current)
        except ValueError:
            return order[0]
        return order[(idx + direction) % len(order)]

    def set_theme(self, name: str) -> str:
        if name in THEMES:
            self.theme = name
            apply_theme(self.theme)
            self.save()
        return self.theme

    def cycle_theme(self, direction: int = 1) -> str:
        self.theme = self._cycle_list(self.theme, THEME_ORDER, direction)
        apply_theme(self.theme)
        self.save()
        return self.theme

    def cycle_music_track(self, direction: int = 1) -> str:
        self.music_track = self._cycle_list(self.music_track, MUSIC_TRACK_ORDER, direction)
        self.save()
        return self.music_track

    def toggle_fullscreen(self) -> bool:
        self.fullscreen = not self.fullscreen
        self.save()
        return self.fullscreen

    def toggle_music(self) -> bool:
        self.music_enabled = not self.music_enabled
        self.save()
        return self.music_enabled

    def adjust_music_volume(self, delta: float) -> float:
        self.music_volume = max(0.0, min(1.0, self.music_volume + delta))
        self.save()
        return self.music_volume

    def adjust_sfx_volume(self, delta: float) -> float:
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + delta))
        self.save()
        return self.sfx_volume

    def cycle_display_scale(self, direction: int = 1) -> float:
        scales = list(DISPLAY_SCALES)
        try:
            idx = scales.index(self.display_scale)
        except ValueError:
            idx = min(range(len(scales)), key=lambda i: abs(scales[i] - self.display_scale))
        self.display_scale = scales[(idx + direction) % len(scales)]
        self.save()
        return self.display_scale