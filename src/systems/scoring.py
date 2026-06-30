"""Score, line count, combos, and level-based gravity speed."""

from config.settings import DROP_INTERVAL

LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
LINES_PER_LEVEL = 10


class Scoring:
    """Tracks progress and computes gravity speed from level."""

    def __init__(self) -> None:
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = -1

    def add_soft_drop(self, cells: int = 1) -> None:
        self.score += cells

    def add_hard_drop(self, cells: int) -> None:
        self.score += cells * 2

    def add_lines(self, count: int) -> None:
        """Award points, combos, and advance level."""
        if count == 0:
            self.combo = -1
            return

        self.combo += 1
        base = LINE_SCORES.get(count, 0) * self.level
        combo_bonus = 50 * self.combo * self.level if self.combo > 0 else 0
        self.score += base + combo_bonus
        self.lines += count
        self.level = self.lines // LINES_PER_LEVEL + 1

    @property
    def drop_interval(self) -> float:
        return max(0.08, DROP_INTERVAL * (0.85 ** (self.level - 1)))