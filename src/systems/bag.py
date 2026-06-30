"""7-bag randomizer — every 7 pieces contains one of each tetromino."""

import random

PIECE_KINDS = ["I", "O", "T", "S", "Z", "J", "L"]


class Bag:
    """Shuffles all seven pieces and deals them one at a time."""

    def __init__(self) -> None:
        self._queue: list[str] = []
        self._refill()

    def next(self) -> str:
        """Return the next piece kind, refilling the bag when empty."""
        if not self._queue:
            self._refill()
        return self._queue.pop(0)

    def peek(self, count: int) -> list[str]:
        """Return upcoming piece kinds without consuming them."""
        if count <= 0:
            return []
        while len(self._queue) < count:
            self._refill()
        return self._queue[:count]

    def _refill(self) -> None:
        bag = PIECE_KINDS.copy()
        random.shuffle(bag)
        self._queue.extend(bag)