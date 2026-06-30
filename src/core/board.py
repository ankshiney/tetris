"""The Tetris playfield — grid storage and collision checks."""

from config.settings import COLS, HIDDEN_ROWS, ROWS
from src.core.tetromino import Tetromino

TOTAL_ROWS = HIDDEN_ROWS + ROWS


class Board:
    """10×20 visible grid with hidden rows for spawning."""

    def __init__(self) -> None:
        self.grid: list[list[str | None]] = [
            [None for _ in range(COLS)] for _ in range(TOTAL_ROWS)
        ]

    def is_valid_position(self, piece: Tetromino) -> bool:
        """Return True if the piece fits without hitting walls or locked cells."""
        for col, row in piece.cells:
            if col < 0 or col >= COLS or row >= TOTAL_ROWS:
                return False
            if row >= 0 and self.grid[row][col] is not None:
                return False
        return True

    def compute_ghost(self, piece: Tetromino) -> Tetromino:
        """Return the piece dropped as far down as it can go."""
        ghost = piece
        while self.is_valid_position(ghost.moved(dy=1)):
            ghost = ghost.moved(dy=1)
        return ghost

    def lock_piece(self, piece: Tetromino) -> None:
        """Write a landed piece into the grid."""
        for col, row in piece.cells:
            if row >= 0:
                self.grid[row][col] = piece.kind

    def get_full_rows(self) -> list[int]:
        """Return indices of every completely filled row."""
        return [
            row
            for row in range(TOTAL_ROWS)
            if all(self.grid[row][col] is not None for col in range(COLS))
        ]

    def clear_lines(self) -> int:
        """Remove full rows, drop everything above, and return lines cleared."""
        kept_rows: list[list[str | None]] = []
        cleared = 0

        for row in range(TOTAL_ROWS):
            if all(self.grid[row][col] is not None for col in range(COLS)):
                cleared += 1
            else:
                kept_rows.append(self.grid[row][:])

        while len(kept_rows) < TOTAL_ROWS:
            kept_rows.insert(0, [None for _ in range(COLS)])

        self.grid = kept_rows
        return cleared