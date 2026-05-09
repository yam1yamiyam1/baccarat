"""Simple Tkinter UI to launch debug scripts."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEBUG_FOLDER = PROJECT_ROOT / "debug"
WINDOW_TITLE = "Baccarat Debug Launcher"


def discover_debug_scripts() -> list[Path]:
    """Return sorted debug scripts from the debug folder."""
    script_paths = sorted(DEBUG_FOLDER.glob("test_*.py"))
    return [script_path for script_path in script_paths if script_path.name != Path(__file__).name]


def launch_script(script_path: Path) -> None:
    """Launch one debug script in a separate Python process."""
    try:
        process_environment = os.environ.copy()
        existing_pythonpath = process_environment.get("PYTHONPATH", "")
        if existing_pythonpath:
            process_environment["PYTHONPATH"] = f"{PROJECT_ROOT};{existing_pythonpath}"
        else:
            process_environment["PYTHONPATH"] = str(PROJECT_ROOT)
        subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            env=process_environment,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    except OSError as launch_error:
        messagebox.showerror("Launch Error", f"Failed to launch {script_path.name}\n\n{launch_error}")


def format_button_label(script_path: Path) -> str:
    """Convert script filename into a readable button label."""
    human_label = script_path.stem.replace("_", " ").title()
    return human_label


def build_ui() -> tk.Tk:
    """Create and return the launcher window."""
    root_window = tk.Tk()
    root_window.title(WINDOW_TITLE)
    root_window.geometry("420x320")
    root_window.minsize(360, 240)

    content_frame = tk.Frame(root_window, padx=14, pady=14)
    content_frame.pack(fill=tk.BOTH, expand=True)

    title_label = tk.Label(
        content_frame,
        text="Debug Script Launcher",
        font=("Segoe UI", 13, "bold"),
        anchor="w",
    )
    title_label.pack(fill=tk.X, pady=(0, 10))

    help_label = tk.Label(
        content_frame,
        text="Click a button to run a debug script in a new process.",
        anchor="w",
    )
    help_label.pack(fill=tk.X, pady=(0, 12))

    script_paths = discover_debug_scripts()
    if not script_paths:
        empty_label = tk.Label(content_frame, text="No debug scripts found in /debug.", fg="red")
        empty_label.pack(fill=tk.X)
        return root_window

    for script_path in script_paths:
        button = tk.Button(
            content_frame,
            text=format_button_label(script_path),
            command=lambda current_path=script_path: launch_script(current_path),
            height=2,
        )
        button.pack(fill=tk.X, pady=4)

    return root_window


def main() -> None:
    """Run the launcher application."""
    launcher_window = build_ui()
    launcher_window.mainloop()


if __name__ == "__main__":
    main()
