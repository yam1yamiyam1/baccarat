"""Screen capture module for acquiring monitor frames."""

from dataclasses import dataclass

import cv2
import mss
import numpy as np


@dataclass
class CaptureResult:
    """Holds a captured BGR frame and its monitor rectangle."""

    frame: np.ndarray
    monitor_rect: tuple[int, int, int, int]


class ScreenCapturer:
    """Captures frames from a selected monitor using mss."""

    def __init__(self, monitor_index: int = 1) -> None:
        """Initialize the capturer with a 1-based monitor index."""
        self.monitor_index = monitor_index

    def grab_frame(self) -> CaptureResult:
        """Capture one frame and return BGR image plus monitor bounds."""
        with mss.mss() as screen_capture:
            monitor_definition = screen_capture.monitors[self.monitor_index]
            raw_screenshot = screen_capture.grab(monitor_definition)

        bgra_frame = np.array(raw_screenshot)
        bgr_frame = cv2.cvtColor(bgra_frame, cv2.COLOR_BGRA2BGR)

        monitor_rect = (
            int(monitor_definition["left"]),
            int(monitor_definition["top"]),
            int(monitor_definition["width"]),
            int(monitor_definition["height"]),
        )

        return CaptureResult(frame=bgr_frame, monitor_rect=monitor_rect)
