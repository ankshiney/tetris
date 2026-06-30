"""Entry point — run the Tetris game."""

import traceback

from src.core.game import Game
from src.systems.platform import configure_android_env


def main() -> None:
    configure_android_env()
    try:
        game = Game()
        game.run()
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()