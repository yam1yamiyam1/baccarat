"""Global configuration constants for the baccarat reader pipeline."""

SCAN_INTERVAL_MS = 500

# ── box_finder configuration ─────────────────
MIN_BOX_AREA = 30000
ASPECT_MIN = 3.0
ASPECT_MAX = 20.0
SEARCH_REGION_Y_START = 0.50  # Search bottom 50% of screen
SEARCH_REGION_X_END = 0.50    # Search left 50% of screen

WHITE_THRESH = 200            # Pixel brightness to be considered "white"
MORPH_KERNEL_SIZE = 20        # Kernel size to merge dots into one box

# ── chat bar trimming ────────────────────────
TRIM_DARK_THRESH = 220        # A row averaging below this is part of the dark chat bar
TRIM_WHITE_THRESH = 245       # A row averaging above this is the white gap below the chat bar
TRIM_SCAN_LIMIT_RATIO = 0.40  # Only scan the top 40% of the box for a chat bar

# ── debug overlay ────────────────────────────
DEBUG_BG_COLOR = "black"
DEBUG_BOX_COLOR = "yellow"
DEBUG_STATIC_COLOR = "green"
DEBUG_TEXT_COLOR = "red"
DEBUG_LINE_WIDTH = 3
DEBUG_FONT = ("Consolas", 12, "bold")
DEBUG_TEXT_PAD = 10

# ── lock settings ────────────────────────────
LOCK_KEEP_THRESH = 180        # Min average brightness to maintain the box lock
MAX_MISS_COUNT = 3            # Frames to wait before dropping a locked box

# (Update your DEBUG_LINE_WIDTH to 5 if you like the thicker line)
DEBUG_LINE_WIDTH = 5