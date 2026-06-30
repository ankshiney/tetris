"""Generate menu/pause image assets. Run: py -3.12 scripts/generate_assets.py"""

import sys
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.systems.asset_generator import generate_all_assets  # noqa: E402


def main() -> None:
    pygame.init()
    generate_all_assets()
    print("Assets written to assets/images/")
    pygame.quit()


if __name__ == "__main__":
    main()