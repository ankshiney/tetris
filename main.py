"""Entry point — run the Tetris game."""

import traceback

from src.systems.platform import configure_android_env, write_android_log

# Configure SDL/Android before any module touches JNI, storage, or pygame display.
configure_android_env()


def main() -> None:
    try:
        from src.core.game import Game

        game = Game()
        game.run()
    except Exception:
        write_android_log(traceback.format_exc())
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()