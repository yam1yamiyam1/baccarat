# pyrefly: ignore [missing-import]
import cv2
import numpy as np
from dataclasses import dataclass
from enum import Enum

import config

class BeadColor(Enum):
    """Represents the color of a bead."""
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    EMPTY = "empty"

@dataclass
class GridResult:
    """Holds the 2D grid of parsed bead colors."""
    grid: list[list[BeadColor]]

class BeadReader:
    """Reads the cropped bead plate ROI and returns a 2D grid of colors."""
    
    def _classify_color(self, hsv_patch: np.ndarray) -> BeadColor:
        """Takes an HSV image patch, gets the median color, and returns the matching BeadColor."""
        if hsv_patch.size == 0:
            return BeadColor.EMPTY
            
        # Reshape to a list of pixels: shape (N, 3)
        pixels = hsv_patch.reshape(-1, 3)
        
        # Filter out pixels that are too white/gray (low saturation) or too dark (low value)
        # We use S > 50 and V > 50 to ignore the pure white "T"/"B"/"P" letters and shadows
        valid_pixels = pixels[(pixels[:, 1] > 50) & (pixels[:, 2] > 50)]
        
        if len(valid_pixels) == 0:
            # Fallback to median of all if no saturated pixels found (e.g., truly empty)
            h, s, v = np.median(pixels, axis=0)
        else:
            h, s, v = np.median(valid_pixels, axis=0)
        
        # Check red (wraps around 180)
        is_red1 = (config.HSV_RED_LOWER1[0] <= h <= config.HSV_RED_UPPER1[0] and
                   config.HSV_RED_LOWER1[1] <= s <= config.HSV_RED_UPPER1[1] and
                   config.HSV_RED_LOWER1[2] <= v <= config.HSV_RED_UPPER1[2])
        is_red2 = (config.HSV_RED_LOWER2[0] <= h <= config.HSV_RED_UPPER2[0] and
                   config.HSV_RED_LOWER2[1] <= s <= config.HSV_RED_UPPER2[1] and
                   config.HSV_RED_LOWER2[2] <= v <= config.HSV_RED_UPPER2[2])
        if is_red1 or is_red2:
            return BeadColor.RED
            
        # Check blue
        is_blue = (config.HSV_BLUE_LOWER[0] <= h <= config.HSV_BLUE_UPPER[0] and
                   config.HSV_BLUE_LOWER[1] <= s <= config.HSV_BLUE_UPPER[1] and
                   config.HSV_BLUE_LOWER[2] <= v <= config.HSV_BLUE_UPPER[2])
        if is_blue:
            return BeadColor.BLUE
            
        # Check green
        is_green = (config.HSV_GREEN_LOWER[0] <= h <= config.HSV_GREEN_UPPER[0] and
                    config.HSV_GREEN_LOWER[1] <= s <= config.HSV_GREEN_UPPER[1] and
                    config.HSV_GREEN_LOWER[2] <= v <= config.HSV_GREEN_UPPER[2])
        if is_green:
            return BeadColor.GREEN
            
        return BeadColor.EMPTY

    def read_grid(self, frame: np.ndarray, box_rect: tuple[int, int, int, int]) -> GridResult:
        """Crops the frame using the bounding box, samples a grid of beads, and classifies them."""
        x, y, width, height = box_rect
        cropped_frame = frame[y:y+height, x:x+width]
        
        columns = int((width - config.GRID_PAD_X) / config.GRID_CELL_WIDTH)
        
        hsv_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
        
        grid_colors = []
        for col_idx in range(columns):
            col_colors = []
            for row_idx in range(config.GRID_ROWS):
                # Calculate center coordinate of this cell using tunable configuration
                center_x = int(config.GRID_PAD_X + (col_idx + 0.5) * config.GRID_CELL_WIDTH)
                center_y = int(config.GRID_PAD_Y + (row_idx + 0.5) * config.GRID_CELL_HEIGHT)
                
                # Extract sample patch around the center
                radius = config.BEAD_SAMPLE_RADIUS
                y_start = max(0, center_y - radius)
                y_end = min(height, center_y + radius + 1)
                x_start = max(0, center_x - radius)
                x_end = min(width, center_x + radius + 1)
                
                hsv_patch = hsv_frame[y_start:y_end, x_start:x_end]
                
                # Classify
                color = self._classify_color(hsv_patch)
                col_colors.append(color)
            
            grid_colors.append(col_colors)
            
        return GridResult(grid=grid_colors)
