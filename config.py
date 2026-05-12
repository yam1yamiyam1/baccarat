"""Global configuration constants for the baccarat reader pipeline."""

SCAN_INTERVAL_MS = 500

# ── box_finder configuration ─────────────────
MIN_BOX_AREA = 30000
ASPECT_MIN = 3.0
ASPECT_MAX = 20.0
SEARCH_REGION_Y_START = 0.50  # Search bottom 50% of screen
SEARCH_REGION_X_END = 0.50  # Search left 50% of screen

WHITE_THRESH = 200  # Pixel brightness to be considered "white"
MORPH_KERNEL_SIZE = 20  # Kernel size to merge dots into one box

# ── chat bar trimming ────────────────────────
TRIM_DARK_THRESH = 220  # A row averaging below this is part of the dark chat bar
TRIM_WHITE_THRESH = (
    245  # A row averaging above this is the white gap below the chat bar
)
TRIM_SCAN_LIMIT_RATIO = 0.40  # Only scan the top 40% of the box for a chat bar

# ── debug overlay ────────────────────────────
DEBUG_BG_COLOR = "black"
DEBUG_BOX_COLOR = "yellow"
DEBUG_STATIC_COLOR = "green"
DEBUG_TEXT_COLOR = "red"
DEBUG_LINE_WIDTH = 1
DEBUG_FONT = ("Consolas", 12, "bold")
DEBUG_TEXT_PAD = 10

# ── lock settings ────────────────────────────
LOCK_KEEP_THRESH = 180  # Min average brightness to maintain the box lock
MAX_MISS_COUNT = 3  # Frames to wait before dropping a locked box

# (Update your DEBUG_LINE_WIDTH to 5 if you like the thicker line)
DEBUG_LINE_WIDTH = 5

# ── bead_reader configuration ────────────────
GRID_ROWS = 6

# Tune these values to perfectly align the bead sensors (white squares)
# with the centers of the actual beads on screen.
GRID_PAD_X = 0  # Left margin inside the yellow box
GRID_PAD_Y = 3.0  # Top margin inside the yellow box
GRID_CELL_WIDTH = 22  # Horizontal spacing between bead centers
GRID_CELL_HEIGHT = 22.0  # Vertical spacing between bead centers

# HSV Color Ranges (H, S, V) — calibrated from actual bead screenshot
HSV_RED_LOWER1 = (0, 80, 100)
HSV_RED_UPPER1 = (15, 255, 255)
HSV_RED_LOWER2 = (155, 80, 100)
HSV_RED_UPPER2 = (180, 255, 255)
HSV_BLUE_LOWER = (95, 80, 80)
HSV_BLUE_UPPER = (120, 255, 255)
HSV_GREEN_LOWER = (40, 50, 80)
HSV_GREEN_UPPER = (90, 255, 255)

# Bead sampling
# Assumes: 1920x1080 screen, 125% Windows DPI scaling, fullscreen game
# At this setup beads are ~20x20px. A 5x5 patch (radius=2) covers ~25%
# of the bead width, staying safely away from corner pair dots (~3-4px from edge)
BEAD_SAMPLE_RADIUS = 2

# ── simulator configuration ──────────────────
SIM_STARTING_CAPITAL = 50_000
SIM_BASE_BET = 500
SIM_DAILY_PROFIT_TARGET = 1000
SIM_DAILY_STOP_LOSS = 5000
SIM_NUM_DAYS = 30
SIM_MAX_SHOES_PER_DAY = 20
SIM_STREAK_TRIGGER = 4
SIM_BANKER_WEIGHT = 45.859
SIM_PLAYER_WEIGHT = 44.615
SIM_TIE_WEIGHT = 9.526
SIM_MAX_BET_LIMIT = 200_000
