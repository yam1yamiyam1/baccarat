"""Debug script to visually test screen capture without hall-of-mirrors."""

import os
import sys
import tkinter as tk

# Ensure we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from capture import ScreenCapturer


class CaptureDebugOverlay:
    """Transparent Tkinter overlay for testing basic frame capture."""

    def __init__(self) -> None:
        """Initialize transparent window to display capture stats."""
        self.root = tk.Tk()
        self.root.title("Capture Debug")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
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

        self.capturer = ScreenCapturer(monitor_index=1)

    def update_loop(self) -> None:
        """Grab a frame and draw a static test rectangle to prove it works."""
        self.canvas.delete("all")

        capture_result = self.capturer.grab_frame()
        frame_h, frame_w = capture_result.frame.shape[:2]
        
        # Draw a static box on the screen to verify overlay positioning
        box_x, box_y, box_w, box_h = 100, 100, 300, 300
        
        self.canvas.create_rectangle(
            box_x, box_y, box_x + box_w, box_y + box_h,
            outline=config.DEBUG_STATIC_COLOR, 
            width=config.DEBUG_LINE_WIDTH
        )
        
        self.canvas.create_text(
            box_x, box_y - config.DEBUG_TEXT_PAD,
            text=f"Capture Active! Frame Size: {frame_w}x{frame_h} (ESC to exit)",
            fill=config.DEBUG_STATIC_COLOR,
            anchor="w",
            font=config.DEBUG_FONT
        )

        self.root.after(config.SCAN_INTERVAL_MS, self.update_loop)

    def run(self) -> None:
        """Start Tkinter main loop."""
        self.root.after(100, self.update_loop)
        self.root.mainloop()


if __name__ == "__main__":
    overlay = CaptureDebugOverlay()
    overlay.run()