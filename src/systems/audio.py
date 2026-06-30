"""Procedural sound effects and multiple looping music tracks."""

import array
import math

import pygame

from src.systems.music_tracks import MUSIC_TRACK_ORDER, build_track


def _make_tone(
    frequency: float,
    duration: float,
    volume: float = 0.25,
    sample_rate: int = 22050,
) -> pygame.mixer.Sound | None:
    try:
        n_samples = int(sample_rate * duration)
        buf = array.array("h")
        for i in range(n_samples):
            t = i / sample_rate
            envelope = 1.0 - (i / n_samples)
            sample = int(volume * 32767 * envelope * math.sin(2 * math.pi * frequency * t))
            buf.append(sample)
            buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)
    except pygame.error:
        return None


class AudioManager:
    """SFX and background music with track selection."""

    def __init__(self) -> None:
        self.enabled = False
        self.music_enabled = True
        self.music_volume = 0.35
        self.sfx_volume = 0.8
        self.music_track = "chill"
        self._tracks: dict[str, pygame.mixer.Sound | None] = {}
        self._music_channel: pygame.mixer.Channel | None = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._sounds = {
                "move": _make_tone(280, 0.04, 0.12),
                "rotate": _make_tone(420, 0.05, 0.15),
                "soft_drop": _make_tone(200, 0.03, 0.1),
                "hard_drop": _make_tone(150, 0.08, 0.3),
                "lock": _make_tone(110, 0.1, 0.2),
                "line_clear": _make_tone(520, 0.12, 0.25),
                "tetris": _make_tone(660, 0.2, 0.35),
                "level_up": _make_tone(780, 0.15, 0.3),
                "game_over": _make_tone(90, 0.35, 0.35),
                "hold": _make_tone(360, 0.06, 0.18),
                "menu": _make_tone(520, 0.06, 0.12),
            }
            for track_id in MUSIC_TRACK_ORDER:
                self._tracks[track_id] = build_track(track_id)
            self.enabled = any(s is not None for s in self._sounds.values())
            self._music_channel = pygame.mixer.Channel(7)
        except pygame.error:
            self._sounds = {}

    def apply_settings(
        self,
        music_volume: float,
        sfx_volume: float,
        music_enabled: bool,
        music_track: str = "chill",
    ) -> None:
        track_changed = music_track != self.music_track
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self.music_enabled = music_enabled
        self.music_track = music_track if music_track in self._tracks else "chill"
        if self.music_enabled:
            if track_changed:
                self.start_music()
            else:
                self.set_music_volume(self.music_volume)
        else:
            self.stop_music()

    def start_music(self) -> None:
        if not self.enabled or not self.music_enabled or self._music_channel is None:
            return
        music = self._tracks.get(self.music_track)
        if music is None:
            music = self._tracks.get("chill")
        if music is None:
            return
        self._music_channel.play(music, loops=-1)
        self._music_channel.set_volume(self.music_volume)

    def stop_music(self) -> None:
        if self._music_channel is not None:
            self._music_channel.stop()

    def pause_music(self) -> None:
        if self._music_channel is not None:
            self._music_channel.pause()

    def unpause_music(self) -> None:
        if self._music_channel is not None and self.music_enabled:
            self._music_channel.unpause()

    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0.0, min(1.0, volume))
        if self._music_channel is not None:
            self._music_channel.set_volume(self.music_volume)

    def set_music_track(self, track_id: str) -> None:
        if track_id not in self._tracks:
            return
        self.music_track = track_id
        if self.music_enabled:
            self.start_music()

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        sound = self._sounds.get(name)
        if sound is not None:
            sound.set_volume(self.sfx_volume)
            sound.play()