"""Tetromino definitions and the active falling piece."""

from dataclasses import dataclass

from config.settings import COLS, HIDDEN_ROWS, ROWS
import src.ui.colors as colors

# Each shape is a list of (col, row) offsets relative to the piece origin.
# Four rotation states per piece (0–3).
SHAPES: dict[str, list[list[tuple[int, int]]]] = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (0, 1)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (2, 1), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (1, 1), (0, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

# Spawn column per piece type (tuned so each piece spawns centered)
SPAWN_X: dict[str, int] = {
    "I": 3,
    "O": 4,
    "T": 3,
    "S": 3,
    "Z": 3,
    "J": 3,
    "L": 3,
}


@dataclass
class Tetromino:
    """A single falling piece on the board."""

    kind: str
    rotation: int = 0
    x: int = 0
    y: int = 0

    @property
    def color(self) -> tuple[int, int, int]:
        return colors.PIECE_COLORS[self.kind]

    @property
    def cells(self) -> list[tuple[int, int]]:
        """Absolute board coordinates for each block in this piece."""
        offsets = SHAPES[self.kind][self.rotation]
        return [(self.x + col, self.y + row) for col, row in offsets]

    @classmethod
    def spawn(cls, kind: str) -> "Tetromino":
        """Create a new piece at the standard spawn position."""
        return cls(
            kind=kind,
            x=SPAWN_X[kind],
            y=HIDDEN_ROWS,
        )

    def moved(self, dx: int = 0, dy: int = 0) -> "Tetromino":
        """Return a copy shifted by (dx, dy) without mutating the original."""
        return Tetromino(self.kind, self.rotation, self.x + dx, self.y + dy)

    def rotated(self, direction: int) -> "Tetromino":
        """Return a copy rotated CW (+1) or CCW (-1)."""
        new_rotation = (self.rotation + direction) % 4
        return Tetromino(self.kind, new_rotation, self.x, self.y)

    def is_visible(self, col: int, row: int) -> bool:
        """True if the cell is inside the visible playfield."""
        return 0 <= col < COLS and HIDDEN_ROWS <= row < HIDDEN_ROWS + ROWS