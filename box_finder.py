"""Module for detecting the baccarat bead road bounding box on screen."""

from dataclasses import dataclass
import cv2
import numpy as np

import config
from capture import CaptureResult


@dataclass
class RoiResult:
    """Holds the result of a region of interest (ROI) search."""

    rect: tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    strategy: str
    is_valid: bool


class BoxFinder:
    """Detects and tracks the bead road bounding box."""

    def __init__(self) -> None:
        """Initialize BoxFinder state."""
        self.locked_rect: tuple[int, int, int, int] | None = None
        self.miss_count: int = 0

    def _validate_rect(self, box_x: int, box_y: int, box_w: int, box_h: int, frame_w: int, frame_h: int) -> bool:
        """Check if a bounding box meets the physical requirements of a bead road."""
        box_area = box_w * box_h
        if box_area < config.MIN_BOX_AREA:
            return False

        aspect_ratio = box_w / float(box_h)
        if not (config.ASPECT_MIN <= aspect_ratio <= config.ASPECT_MAX):
            return False

        # Ensure it falls within the expected bottom-left screen quadrant
        if box_y < (frame_h * config.SEARCH_REGION_Y_START):
            return False
        
        if box_x > (frame_w * config.SEARCH_REGION_X_END):
            return False

        return True

    def _trim_chat_bar(self, gray_frame: np.ndarray, box_x: int, box_y: int, box_w: int, box_h: int) -> tuple[int, int, int, int]:
        """Scan from the top of the box down to remove the dark chat input bar."""
        roi_gray = gray_frame[box_y : box_y + box_h, box_x : box_x + box_w]
        
        scan_limit = int(box_h * config.TRIM_SCAN_LIMIT_RATIO)
        has_hit_dark_bar = False
        
        # Scan row by row from the top of the detected box
        for row_index in range(scan_limit):
            row_mean = np.mean(roi_gray[row_index, :])
            
            # Identify the dark grey background of the input field
            if row_mean < config.TRIM_DARK_THRESH:
                has_hit_dark_bar = True
            
            # Once passed the dark bar, the first bright white row is our true top boundary
            if has_hit_dark_bar and row_mean > config.TRIM_WHITE_THRESH:
                new_y = box_y + row_index
                new_h = box_h - row_index
                return (box_x, new_y, box_w, new_h)
                
        # Return original coordinates if no chat bar signature was found
        return (box_x, box_y, box_w, box_h)

    def _strategy_1_white_morphology(self, frame: np.ndarray) -> tuple[int, int, int, int] | None:
        """Find the box by looking for large, wide, white shapes in the search region."""
        frame_h, frame_w = frame.shape[:2]
        
        # Crop to bottom-left to save processing power and ignore other UI elements
        crop_y1 = int(frame_h * config.SEARCH_REGION_Y_START)
        crop_x2 = int(frame_w * config.SEARCH_REGION_X_END)
        cropped_frame = frame[crop_y1:frame_h, 0:crop_x2]
        
        gray = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, config.WHITE_THRESH, 255, cv2.THRESH_BINARY)
        
        # Use a large morphological CLOSE to fill the gaps between the bead dots
        kernel = np.ones((config.MORPH_KERNEL_SIZE, config.MORPH_KERNEL_SIZE), np.uint8)
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_candidates = []
        for contour in contours:
            crop_x, crop_y, box_w, box_h = cv2.boundingRect(contour)
            
            # Map cropped coordinates back to the full monitor frame coordinates
            box_x = crop_x
            box_y = crop_y + crop_y1
            
            if self._validate_rect(box_x, box_y, box_w, box_h, frame_w, frame_h):
                valid_candidates.append((box_x, box_y, box_w, box_h))
                
        if not valid_candidates:
            return None
            
        # The bead road is always the furthest left element
        best_rect = min(valid_candidates, key=lambda rect: rect[0])
        
        # Convert full frame to gray once for the trimming method
        full_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        trimmed_rect = self._trim_chat_bar(full_gray, *best_rect)
        
        return trimmed_rect

    def find_roi(self, capture: CaptureResult) -> RoiResult | None:
        """Execute the strategy cascade to locate the bead road."""
        frame_h, frame_w = capture.frame.shape[:2]

        # 1. Fast Verify: If we already have a locked box, check if it's still there
        if self.locked_rect is not None:
            box_x, box_y, box_w, box_h = self.locked_rect
            
            # Ensure it's still within screen bounds (in case resolution changed)
            if box_x + box_w <= frame_w and box_y + box_h <= frame_h:
                roi = capture.frame[box_y:box_y+box_h, box_x:box_x+box_w]
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                
                # If the area is still predominantly white, keep the lock!
                if np.mean(gray_roi) > config.LOCK_KEEP_THRESH:
                    self.miss_count = 0
                    return RoiResult(rect=self.locked_rect, confidence=0.99, strategy="locked", is_valid=True)
            
            # Box is no longer white (user moved window, etc.)
            self.miss_count += 1
            if self.miss_count >= config.MAX_MISS_COUNT:
                self.locked_rect = None

        # 2. Full Search: Only runs if we don't have a lock
        if self.locked_rect is None:
            best_rect = self._strategy_1_white_morphology(capture.frame)
            
            if best_rect is not None:
                # Lock onto this rectangle so we stop twitching on future frames
                self.locked_rect = best_rect
                self.miss_count = 0
                return RoiResult(
                    rect=best_rect,
                    confidence=0.9,
                    strategy="S1_white",
                    is_valid=True
                )
            
        return None