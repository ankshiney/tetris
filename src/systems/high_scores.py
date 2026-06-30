"""Persist and display top scores."""

import json

from config.settings import MAX_HIGH_SCORES
from src.systems.paths import data_dir, highscores_file

class HighScores:
    """Keeps a sorted list of the best runs."""

    def __init__(self) -> None:
        self.entries: list[dict[str, int]] = []
        self._load()

    def _load(self) -> None:
        path = highscores_file()
        if not path.exists():
            return
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.entries = data[:MAX_HIGH_SCORES]
        except (json.JSONDecodeError, OSError):
            self.entries = []

    def _save(self) -> None:
        data_dir()
        with highscores_file().open("w", encoding="utf-8") as f:
            json.dump(self.entries[:MAX_HIGH_SCORES], f, indent=2)

    def is_high_score(self, score: int) -> bool:
        if len(self.entries) < MAX_HIGH_SCORES:
            return score > 0
        return score > self.entries[-1]["score"]

    def add(self, score: int, lines: int, level: int) -> int:
        """Insert a score and return its rank (1-based), or 0 if unranked."""
        if score <= 0:
            return 0
        self.entries.append({"score": score, "lines": lines, "level": level})
        self.entries.sort(key=lambda e: e["score"], reverse=True)
        self.entries = self.entries[:MAX_HIGH_SCORES]
        self._save()
        for i, entry in enumerate(self.entries, start=1):
            if entry["score"] == score and entry["lines"] == lines:
                return i
        return 0