# Baccarat Reader - Architecture & Rules

## Overview
A Windows desktop application that captures a browser-based baccarat game, reads the bead plate using computer vision, analyzes patterns, and displays bet recommendations via a transparent Tkinter overlay. **Read-only system (no browser interaction).**

## Tech Stack
Python 3.10+, `mss` (screen capture), `opencv-python` (vision), `numpy` (matrix math), `tkinter` (overlay), `win32gui` (window management).

## Pipeline Architecture
The system runs in a strict forward-pipeline. **Do not mix responsibilities.**
1. `capture.py`: Grabs full monitor frame (`mss`).
2. `box_finder.py`: Finds the bead plate bounding box (ROI).
3. `bead_reader.py`: Crops ROI, samples grid, classifies HSV colors.
4. `analyzer.py`: Runs pattern strategies on sequence.
5. `bet_engine.py`: Calculates bet sizing based on confidence.
6. `overlay.py`: Draws results on screen (Tkinter).

## Strict Coding Rules
- **Data Flow:** Pass data between modules using strict typed `dataclasses` (e.g., `CaptureResult`, `RoiResult`). No plain dictionaries.
- **Thread Safety:** The UI thread (Tkinter) and the background scan thread (OpenCV/mss) must never block each other. Shared state uses `threading.Lock()`.
- **No Magic Numbers:** All thresholds, colors, timings, and ratios must live in `config.py`.
- **No Silent Failures:** Never use `except: pass`. If a process fails, return `None`, log it, and handle it upstream.
- **Short Functions:** Keep functions under 30 lines. One job per function.

## Code Readability & Style
- **Descriptive Naming:** No single-letter variables except in simple loops (e.g., use `bead_box_width` instead of `w`, and `cropped_frame` instead of `img`).
- **Type Hints:** Every function signature must have strict type hints.
- **Docstrings:** Every class and function must have a concise docstring explaining *what* goes in and *what* comes out.
- **Explain the 'Why':** Use inline comments to explain *why* an OpenCV or math operation is happening (e.g., `# 20x20 kernel fills the gaps between the bead dots`).
- **Vertical Spacing:** Group related lines of code together and separate logical blocks with blank lines.