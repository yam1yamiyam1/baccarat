"""Global configuration constants for the baccarat reader pipeline."""

SCAN_INTERVAL_MS = 500

MIN_BOX_AREA = 30000
ASPECT_MIN = 3.0
ASPECT_MAX = 20.0
MORPH_KERNEL_SIZE = 20
SEARCH_REGION_Y_START = 0.55
SEARCH_REGION_X_END = 0.50

# ── debug overlay ──────────────────────────────
DEBUG_BG_COLOR = "black"
DEBUG_BOX_COLOR = "yellow"
DEBUG_TEXT_COLOR = "red"
DEBUG_LINE_WIDTH = 3
DEBUG_FONT = ("Consolas", 12, "bold")
DEBUG_TEXT_PAD = 10