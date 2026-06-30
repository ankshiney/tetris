"""Hold-to-repeat for on-screen touch buttons."""

from __future__ import annotations

from config.settings import ARR_INTERVAL, DAS_DELAY


class TouchRepeat:
    """Fires an action once immediately, then repeats while held."""

    def __init__(self) -> None:
        self._held: str | None = None
        self._das_timer = 0.0
        self._arr_timer = 0.0

    def press(self, action: str) -> list[str]:
        self._held = action
        self._das_timer = 0.0
        self._arr_timer = 0.0
        return [action]

    def release(self, action: str | None = None) -> None:
        if action is None or self._held == action:
            self._held = None
            self._das_timer = 0.0
            self._arr_timer = 0.0

    def poll(self, dt: float) -> list[str]:
        if self._held is None:
            return []
        self._das_timer += dt
        if self._das_timer < DAS_DELAY:
            return []
        self._arr_timer += dt
        if self._arr_timer >= ARR_INTERVAL:
            self._arr_timer = 0.0
            return [self._held]
        return []