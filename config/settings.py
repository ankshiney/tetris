"""Global game constants — tweak these to resize the window or change speed."""

# Grid dimensions (standard Tetris playfield)
COLS = 10
ROWS = 20
HIDDEN_ROWS = 2  # spawn area above the visible board

# Rendering
CELL_SIZE = 34
GRID_LINE_WIDTH = 1
BOARD_PADDING = 24

# Window size derived from board dimensions
BOARD_PIXEL_WIDTH = COLS * CELL_SIZE
BOARD_PIXEL_HEIGHT = ROWS * CELL_SIZE

# Layout: [HOLD left] [playfield center] [stats + next queue right]
SIDE_PANEL_WIDTH = 140
PANEL_GAP = 20
BOARD_ORIGIN_X = BOARD_PADDING + SIDE_PANEL_WIDTH + PANEL_GAP
BOARD_ORIGIN_Y = BOARD_PADDING
LEFT_PANEL_X = BOARD_PADDING
RIGHT_PANEL_X = BOARD_ORIGIN_X + BOARD_PIXEL_WIDTH + PANEL_GAP
PANEL_WIDTH = SIDE_PANEL_WIDTH  # alias used by HUD helpers
WINDOW_WIDTH = RIGHT_PANEL_X + SIDE_PANEL_WIDTH + BOARD_PADDING
WINDOW_HEIGHT = BOARD_PIXEL_HEIGHT + BOARD_PADDING * 2

# Default window upscale (1.0 = native, 1.25 = 25% larger on screen)
DEFAULT_DISPLAY_SCALE = 1.15

# Timing
FPS = 60
MAX_DT = 0.05              # cap frame delta for smooth physics
DROP_INTERVAL = 0.8
LOCK_DELAY = 0.5
LINE_CLEAR_FLASH = 0.38      # flash / wave before rows are removed
ROW_FALL_DURATION = 0.22     # slide-down after clear
LINE_CLEAR_DURATION = LINE_CLEAR_FLASH + ROW_FALL_DURATION
MAX_PARTICLES = 180

# Input — DAS (Delayed Auto Shift) + ARR (Auto Repeat Rate)
DAS_DELAY = 0.15
ARR_INTERVAL = 0.05
SOFT_DROP_INTERVAL = 0.05

# Preview panel
PREVIEW_CELL_SIZE = 26
NEXT_QUEUE_COUNT = 4
NEXT_QUEUE_CELL_SIZE = 20

# Persistence
MAX_HIGH_SCORES = 5