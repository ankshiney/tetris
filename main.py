"""Entry point — run the Tetris game."""

from src.systems.platform import configure_android_env
from src.core.game import Game


def main() -> None:
    configure_android_env()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()