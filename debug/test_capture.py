"""Standalone visual test for monitor capture."""

import time

import cv2

import config
from capture import ScreenCapturer


BOX_TOP_LEFT = (100, 100)
BOX_BOTTOM_RIGHT = (400, 400)
BOX_COLOR_BGR = (0, 255, 0)
BOX_THICKNESS = 2
WINDOW_NAME = "Capture Debug"
STATUS_TEXT = "Capture running - press q to exit"
STATUS_POSITION = (16, 30)
STATUS_COLOR_BGR = (255, 255, 255)


def main() -> None:
    """Continuously capture, annotate, and display monitor frames."""
    screen_capturer = ScreenCapturer(monitor_index=1)

    while True:
        time.sleep(config.SCAN_INTERVAL_MS / 1000.0)

        capture_result = screen_capturer.grab_frame()
        frame = capture_result.frame

        # Draw a fixed rectangle to confirm overlay-style annotations work.
        cv2.rectangle(
            frame,
            BOX_TOP_LEFT,
            BOX_BOTTOM_RIGHT,
            BOX_COLOR_BGR,
            BOX_THICKNESS,
        )
        cv2.putText(
            frame,
            STATUS_TEXT,
            STATUS_POSITION,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            STATUS_COLOR_BGR,
            2,
            cv2.LINE_AA,
        )
        cv2.imshow(WINDOW_NAME, frame)

        pressed_key = cv2.waitKey(1) & 0xFF
        if pressed_key == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
