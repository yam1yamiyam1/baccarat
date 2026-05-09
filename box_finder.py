"""ROI detection strategies for locating the baccarat bead plate."""

from dataclasses import dataclass

import cv2
import numpy as np

import config
from capture import CaptureResult


@dataclass
class RoiResult:
    """Contains the detected ROI rectangle and strategy metadata."""

    rect: tuple[int, int, int, int]
    confidence: float
    strategy: str
    is_valid: bool


class BoxFinder:
    """Finds the bead-plate ROI from a full captured frame."""

    def __init__(self) -> None:
        """Initialize state for future lock/miss strategies."""
        self.locked_rect: tuple[int, int, int, int] | None = None
        self.miss_count = 0

    def _validate_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        frame_w: int,
        frame_h: int,
    ) -> bool:
        """Validate rectangle geometry and expected bottom-left placement."""
        if h <= 0:
            return False

        area = w * h
        if area <= config.MIN_BOX_AREA:
            return False

        aspect_ratio = w / h
        if aspect_ratio < config.ASPECT_MIN or aspect_ratio > config.ASPECT_MAX:
            return False

        region_y_start = int(frame_h * config.SEARCH_REGION_Y_START)
        region_x_end = int(frame_w * config.SEARCH_REGION_X_END)

        return x >= 0 and y >= region_y_start and x + w <= region_x_end and y + h <= frame_h

    def _strategy_1_white_morphology(self, frame: np.ndarray) -> tuple[int, int, int, int] | None:
        """Find a white-ish table region in the configured search quadrant."""
        frame_height, frame_width = frame.shape[:2]
        search_y_start = int(frame_height * config.SEARCH_REGION_Y_START)
        search_x_end = int(frame_width * config.SEARCH_REGION_X_END)

        search_region = frame[search_y_start:frame_height, 0:search_x_end]
        gray_search_region = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
        _, thresholded_region = cv2.threshold(
            gray_search_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # A close operation bridges small dark gaps between bright bead dots.
        kernel = np.ones((config.MORPH_KERNEL_SIZE, config.MORPH_KERNEL_SIZE), np.uint8)
        closed_region = cv2.morphologyEx(thresholded_region, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed_region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_rectangles: list[tuple[int, int, int, int]] = []
        for contour in contours:
            local_x, local_y, width, height = cv2.boundingRect(contour)
            global_x = local_x
            global_y = local_y + search_y_start
            if self._validate_rect(global_x, global_y, width, height, frame_width, frame_height):
                valid_rectangles.append((global_x, global_y, width, height))

        if not valid_rectangles:
            return None

        return min(valid_rectangles, key=lambda rect: rect[0])

    def find_roi(self, capture: CaptureResult) -> RoiResult | None:
        """Run ROI strategies and return the highest-confidence result."""
        detected_rect = self._strategy_1_white_morphology(capture.frame)
        if detected_rect is None:
            return None

        return RoiResult(
            rect=detected_rect,
            confidence=0.9,
            strategy="S1_white",
            is_valid=True,
        )
