import os
import sys
import tkinter as tk
import ctypes

# Add the parent directory to the path so we can import from the root of the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from capture import ScreenCapturer
from box_finder import BoxFinder
from bead_reader import BeadReader, BeadColor
import config

class BeadReaderOverlay:
    """Class-based Tkinter overlay for the bead reader test."""
    
    def __init__(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

        self.root = tk.Tk()
        
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
            highlightthickness=0,
            width=screen_width,
            height=screen_height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.capturer = ScreenCapturer(monitor_index=1)
        self.finder = BoxFinder()
        self.reader = BeadReader()

    def update_overlay(self):
        """Updates the overlay canvas every interval."""
        self.canvas.delete("all")
        
        capture_result = self.capturer.grab_frame()
        if capture_result is not None:
            roi_result = self.finder.find_roi(capture_result)
            
            if roi_result is not None and roi_result.rect is not None:
                x, y, width, height = roi_result.rect
                
                # Inset drawing so the stroke isn't clipped by the edges of the box
                inset = config.DEBUG_LINE_WIDTH // 2
                draw_x1 = x + inset
                draw_y1 = y + inset
                draw_x2 = x + width - inset
                draw_y2 = y + height - inset
                
                # Draw yellow bounding box
                self.canvas.create_rectangle(
                    draw_x1, draw_y1, draw_x2, draw_y2,
                    outline=config.DEBUG_BOX_COLOR,
                    width=config.DEBUG_LINE_WIDTH
                )
                
                self.canvas.create_text(
                    x, y - config.DEBUG_TEXT_PAD,
                    text=f"ROI FOUND [{width}x{height}] (ESC to exit)",
                    fill=config.DEBUG_BOX_COLOR,
                    anchor="w",
                    font=config.DEBUG_FONT
                )
                
                # Read grid
                grid_result = self.reader.read_grid(capture_result.frame, roi_result.rect)
                        
                # Draw beads and sensors
                for col_idx, col in enumerate(grid_result.grid):
                    for row_idx, bead_color in enumerate(col):
                        center_x = x + int(config.GRID_PAD_X + (col_idx + 0.5) * config.GRID_CELL_WIDTH)
                        center_y = y + int(config.GRID_PAD_Y + (row_idx + 0.5) * config.GRID_CELL_HEIGHT)
                        
                        # Draw the sensor sampling patch so the user sees exactly what is read
                        sensor_radius = config.BEAD_SAMPLE_RADIUS
                        sensor_x1 = center_x - sensor_radius
                        sensor_y1 = center_y - sensor_radius
                        sensor_x2 = center_x + sensor_radius
                        sensor_y2 = center_y + sensor_radius
                        
                        self.canvas.create_rectangle(
                            sensor_x1, sensor_y1, sensor_x2, sensor_y2,
                            outline="white",
                            width=1
                        )
                        
                        if bead_color != BeadColor.EMPTY:
                            # Choose color
                            fill_color = "red"
                            if bead_color == BeadColor.BLUE:
                                fill_color = "blue"
                            elif bead_color == BeadColor.GREEN:
                                fill_color = "green"
                                
                            draw_radius = max(5, sensor_radius * 2)
                            self.canvas.create_oval(
                                center_x - draw_radius, center_y - draw_radius,
                                center_x + draw_radius, center_y + draw_radius,
                                fill=fill_color,
                                outline=fill_color
                            )
                            
                # ── MIRROR PANEL ──────────────────────────────────────────────
                mirror_y = y - height - 100
                mirror_draw_y1 = mirror_y + inset
                mirror_draw_y2 = mirror_y + height - inset
                
                # Draw yellow bounding box for mirror
                self.canvas.create_rectangle(
                    draw_x1, mirror_draw_y1, draw_x2, mirror_draw_y2,
                    outline=config.DEBUG_BOX_COLOR,
                    width=config.DEBUG_LINE_WIDTH
                )
                
                # Draw beads inside mirror with text
                sequence_chars = []
                for col_idx, col in enumerate(grid_result.grid):
                    for row_idx, bead_color in enumerate(col):
                        if bead_color != BeadColor.EMPTY:
                            mirror_cx = x + int(config.GRID_PAD_X + (col_idx + 0.5) * config.GRID_CELL_WIDTH)
                            mirror_cy = mirror_y + int(config.GRID_PAD_Y + (row_idx + 0.5) * config.GRID_CELL_HEIGHT)
                            
                            fill_color = "red"
                            char = "B"
                            if bead_color == BeadColor.BLUE:
                                fill_color = "blue"
                                char = "P"
                            elif bead_color == BeadColor.GREEN:
                                fill_color = "green"
                                char = "T"
                                
                            sequence_chars.append(char)
                                
                            mirror_draw_radius = 10
                            self.canvas.create_oval(
                                mirror_cx - mirror_draw_radius, mirror_cy - mirror_draw_radius,
                                mirror_cx + mirror_draw_radius, mirror_cy + mirror_draw_radius,
                                fill=fill_color,
                                outline=fill_color
                            )
                            self.canvas.create_text(
                                mirror_cx, mirror_cy,
                                text=char,
                                fill="white",
                                font=("Consolas", 10, "bold")
                            )

                # ── SEQUENCE PANEL ────────────────────────────────────────────
                seq_y = mirror_y - height - 100
                seq_draw_y1 = seq_y + inset
                seq_draw_y2 = seq_y + height - inset
                
                # Draw yellow bounding box for sequence
                self.canvas.create_rectangle(
                    draw_x1, seq_draw_y1, draw_x2, seq_draw_y2,
                    outline=config.DEBUG_BOX_COLOR,
                    width=config.DEBUG_LINE_WIDTH
                )
                
                seq_str = " -> ".join(sequence_chars)
                self.canvas.create_text(
                    x + config.DEBUG_TEXT_PAD, seq_y + config.DEBUG_TEXT_PAD,
                    text=seq_str,
                    fill="white",
                    anchor="nw",
                    width=width - (config.DEBUG_TEXT_PAD * 2),
                    font=config.DEBUG_FONT
                )
            else:
                self.canvas.create_text(
                    config.DEBUG_TEXT_PAD, config.DEBUG_TEXT_PAD,
                    text="Searching for Bead Road... (ESC to exit)",
                    fill=config.DEBUG_TEXT_COLOR,
                    anchor="nw",
                    font=config.DEBUG_FONT
                )
        else:
            self.canvas.create_text(
                config.DEBUG_TEXT_PAD, config.DEBUG_TEXT_PAD,
                text="Searching for Bead Road... (ESC to exit)",
                fill=config.DEBUG_TEXT_COLOR,
                anchor="nw",
                font=config.DEBUG_FONT
            )
                            
        self.root.after(config.SCAN_INTERVAL_MS, self.update_overlay)

    def run(self):
        """Starts the main loop."""
        self.update_overlay()
        self.root.mainloop()

def main():
    """Runs a visual test overlay for the bead reader."""
    app = BeadReaderOverlay()
    app.run()

if __name__ == "__main__":
    main()
