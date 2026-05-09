"""Debug script to visually test the BoxFinder using a transparent overlay."""

import os
import sys
import tkinter as tk

# Ensure we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from box_finder import BoxFinder
from capture import ScreenCapturer


class DebugOverlay:
    """Transparent Tkinter overlay for testing bounding box detection."""

    def __init__(self) -> None:
        """Initialize the transparent window, canvas, and vision modules."""
        self.root = tk.Tk()
        self.root.title("Box Finder Debug")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Configure fullscreen, transparent, always-on-top window
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", config.DEBUG_BG_COLOR)
        self.root.config(bg=config.DEBUG_BG_COLOR)
        
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.canvas = tk.Canvas(
            self.root, 
            bg=config.DEBUG_BG_COLOR, 
            width=screen_width, 
            height=screen_height, 
            highlightthickness=0
        )
        self.canvas.pack()

        # Initialize pipeline modules
        self.capturer = ScreenCapturer(monitor_index=1)
        self.box_finder = BoxFinder()

    def update_loop(self) -> None:
        """Grab frame, find ROI, draw it on canvas, and schedule next run."""
        # Clear previous drawings to prevent ghosting
        self.canvas.delete("all")

        capture_result = self.capturer.grab_frame()
        roi_result = self.box_finder.find_roi(capture_result)

        if roi_result is not None and roi_result.is_valid:
            box_x, box_y, box_w, box_h = roi_result.rect
            
            # Draw highly visible dashed outline around detected bead road
            self.canvas.create_rectangle(
                box_x, box_y, box_x + box_w, box_y + box_h,
                outline=config.DEBUG_BOX_COLOR, 
                width=config.DEBUG_LINE_WIDTH,
                dash=(4, 4)
            )
            
            self.canvas.create_text(
                box_x, box_y - config.DEBUG_TEXT_PAD,
                text=f"ROI FOUND [{box_w}x{box_h}] (ESC to exit)",
                fill=config.DEBUG_BOX_COLOR,
                anchor="w",
                font=config.DEBUG_FONT
            )
        else:
            # Show red fallback text so we know the loop is actually running
            self.canvas.create_text(
                config.DEBUG_TEXT_PAD, config.DEBUG_TEXT_PAD,
                text="Searching for Bead Road... (ESC to exit)",
                fill=config.DEBUG_TEXT_COLOR,
                anchor="nw",
                font=config.DEBUG_FONT
            )

        # Re-schedule this method to run again
        self.root.after(config.SCAN_INTERVAL_MS, self.update_loop)

    def run(self) -> None:
        """Start the Tkinter main loop and trigger the first update."""
        self.root.after(config.SCAN_INTERVAL_MS, self.update_loop)
        self.root.mainloop()


if __name__ == "__main__":
    overlay = DebugOverlay()
    overlay.run()