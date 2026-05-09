"""Standalone visual test for ROI detection."""

import time

import cv2

import config
from box_finder import BoxFinder
from capture import ScreenCapturer


WINDOW_NAME = "Box Finder Debug"
ROI_COLOR_BGR = (0, 255, 255)
ROI_THICKNESS = 2
SEARCH_REGION_COLOR_BGR = (255, 0, 0)
STATUS_COLOR_BGR = (255, 255, 255)
SEARCH_REGION_THICKNESS = 2
STATUS_POSITION = (16, 30)


def main() -> None:
    """Capture frames, detect ROI, and render detection overlays."""
    screen_capturer = ScreenCapturer(monitor_index=1)
    box_finder = BoxFinder()

    while True:
        time.sleep(config.SCAN_INTERVAL_MS / 1000.0)

        capture_result = screen_capturer.grab_frame()
        frame = capture_result.frame
        roi_result = box_finder.find_roi(capture_result)
        frame_height, frame_width = frame.shape[:2]

        search_top = int(frame_height * config.SEARCH_REGION_Y_START)
        search_right = int(frame_width * config.SEARCH_REGION_X_END)
        cv2.rectangle(
            frame,
            (0, search_top),
            (search_right, frame_height),
            SEARCH_REGION_COLOR_BGR,
            SEARCH_REGION_THICKNESS,
        )

        if roi_result is not None and roi_result.is_valid:
            x, y, width, height = roi_result.rect
            top_left = (x, y)
            bottom_right = (x + width, y + height)
            cv2.rectangle(frame, top_left, bottom_right, ROI_COLOR_BGR, ROI_THICKNESS)
            status_text = "ROI detected (yellow box)"
        else:
            status_text = "No ROI detected yet"

        cv2.putText(
            frame,
            status_text,
            STATUS_POSITION,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            STATUS_COLOR_BGR,
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(WINDOW_NAME, frame)
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
