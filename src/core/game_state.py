"""High-level game flow states."""

from enum import Enum, auto


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    OPTIONS = auto()
    LINE_CLEAR = auto()
    ROW_FALL = auto()
    GAME_OVER = auto()


PAUSABLE_STATES = frozenset({
    GameState.PLAYING,
    GameState.LINE_CLEAR,
    GameState.ROW_FALL,
})