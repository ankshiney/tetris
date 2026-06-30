"""Procedural background music track definitions."""

import array
import math

import pygame

MUSIC_TRACK_ORDER = ["chill", "pulse", "retro", "dream", "drive", "ambient", "arcade", "synth"]

TRACK_LABELS = {
    "chill": "Chill",
    "pulse": "Pulse",
    "retro": "Retro",
    "dream": "Dream",
    "drive": "Drive",
    "ambient": "Ambient",
    "arcade": "Arcade",
    "synth": "Synth",
}


def _append_note(
    buf: array.array,
    freq: float,
    duration: float,
    *,
    sample_rate: int,
    volume: float,
    wave: str = "sine",
) -> None:
    n_samples = max(1, int(sample_rate * duration))
    for i in range(n_samples):
        t = i / sample_rate
        attack = min(1.0, i / (sample_rate * 0.012))
        release = 1.0 - (i / n_samples) ** 1.4
        if wave == "square":
            raw = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif wave == "triangle":
            raw = (2 / math.pi) * math.asin(math.sin(2 * math.pi * freq * t))
        else:
            raw = math.sin(2 * math.pi * freq * t)
            raw += 0.22 * math.sin(2 * math.pi * freq * 2 * t)
        sample = int(volume * 32767 * attack * release * raw)
        buf.append(sample)
        buf.append(sample)


def build_track(track_id: str, sample_rate: int = 22050) -> pygame.mixer.Sound | None:
    """Synthesize a looping music clip for the given track id."""
    try:
        buf = array.array("h")
        if track_id == "chill":
            notes = [196, 233, 262, 311, 349, 311, 262, 233]
            beat = 0.42
            for n in notes:
                _append_note(buf, float(n), beat, sample_rate=sample_rate, volume=0.08)
        elif track_id == "pulse":
            pattern = [(130, 0.22), (0, 0.08), (196, 0.18), (262, 0.18), (0, 0.08)]
            for freq, dur in pattern:
                if freq:
                    _append_note(buf, float(freq), dur, sample_rate=sample_rate, volume=0.09, wave="square")
                else:
                    buf.extend([0, 0] * int(sample_rate * dur))
        elif track_id == "retro":
            melody = [262, 294, 330, 392, 330, 294, 262, 220]
            for n in melody:
                _append_note(buf, float(n), 0.28, sample_rate=sample_rate, volume=0.085, wave="triangle")
        elif track_id == "dream":
            chords = [(174, 220, 262), (196, 247, 294)]
            for a, b, c in chords:
                for n in (a, b, c):
                    _append_note(buf, float(n), 0.55, sample_rate=sample_rate, volume=0.045)
        elif track_id == "drive":
            seq = [392, 440, 494, 523, 494, 440, 392, 349]
            for n in seq:
                _append_note(buf, float(n), 0.2, sample_rate=sample_rate, volume=0.09)
        elif track_id == "ambient":
            pads = [(130, 0.9), (164, 0.9), (196, 0.9), (164, 0.9)]
            for freq, dur in pads:
                _append_note(buf, float(freq), dur, sample_rate=sample_rate, volume=0.04)
        elif track_id == "arcade":
            melody = [(523, 0.12), (494, 0.12), (440, 0.12), (392, 0.24), (440, 0.12), (494, 0.12)]
            for freq, dur in melody:
                _append_note(buf, float(freq), dur, sample_rate=sample_rate, volume=0.085, wave="square")
        elif track_id == "synth":
            seq = [(220, 0.35), (277, 0.35), (330, 0.35), (277, 0.35)]
            for freq, dur in seq:
                _append_note(buf, float(freq), dur, sample_rate=sample_rate, volume=0.06, wave="triangle")
        else:
            return build_track("chill", sample_rate)
        return pygame.mixer.Sound(buffer=buf)
    except pygame.error:
        return None