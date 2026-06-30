# Tetris (Pygame)

A polished single-player Tetris game with themes, procedural music, touch controls, and Android support.

## Desktop

```bash
pip install -r requirements.txt
python main.py
```

### Controls

| Action | Keys |
|--------|------|
| Move | ← → |
| Soft drop | ↓ |
| Hard drop | Space |
| Rotate CW | ↑ or X |
| Rotate CCW | Z |
| Hold | C |
| Pause | P or Esc |

Hotkeys: **F11** fullscreen, **F8** music, **V** theme, **[** **]** volume.

## Android

The game is adapted for mobile:

- Landscape fullscreen
- Touch buttons with hold-to-repeat (left/right/soft drop)
- Tap board zones: top = rotate, bottom = hard drop, sides = move
- System **Back** navigates menus / pauses / exits
- Settings and high scores saved to app storage

### Build the APK (Linux or WSL)

Buildozer does not run natively on Windows. Use **WSL2**, a Linux VM, or GitHub Actions.

```bash
# One-time setup (Ubuntu / WSL)
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config \
  zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev

python3.11 -m venv .venv
source .venv/bin/activate
pip install "Cython<3.0" "setuptools<71" buildozer

# Build debug APK (~15–40 min first run)
buildozer android debug
```

APK output: `bin/tetris-1.0.0-arm64-v8a_armeabi-v7a-debug.apk`

### Install on device

```bash
adb install -r bin/*-debug.apk
adb logcat -s python
```

### GitHub Actions (no local Linux)

1. Push this repo to GitHub
2. Open **Actions** → **Build Android APK** → **Run workflow**
3. Download the `tetris-android-debug` artifact

## Project layout

```
main.py              Entry point
config/settings.py   Grid, timing, layout
src/core/            Board, pieces, game loop
src/systems/         Input, audio, persistence, Android paths
src/ui/              Rendering, menus, HUD, themes
buildozer.spec       Android packaging
data/                Settings + high scores (desktop)
```

## Requirements

- Python 3.11+ (desktop)
- pygame >= 2.5.0
- Android build: Python 3.11, Cython < 3.0, JDK 17, Buildozer