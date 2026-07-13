"""
Optional Tkinter control panel.

Provides a small always-on-top window with Start/Stop buttons and a live
distance readout, so the app doesn't have to be driven from the command
line. Run with: ``python -m eyeguard.gui``
"""

from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import ttk

from eyeguard.app import EyeGuardApp
from eyeguard.config import load_settings


class EyeGuardGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("EyeGuard - Eye Protection Alert System")
        self.root.geometry("320x160")
        self.root.attributes("-topmost", True)

        self.settings = load_settings()
        self.app: EyeGuardApp | None = None
        self._thread: threading.Thread | None = None
        self._monitoring = False

        self.status_var = tk.StringVar(value="Stopped")
        self.distance_var = tk.StringVar(value="-- cm")

        ttk.Label(root, text="Status:").pack(pady=(15, 0))
        ttk.Label(root, textvariable=self.status_var, font=("Segoe UI", 12, "bold")).pack()

        ttk.Label(root, text="Closest face distance:").pack(pady=(10, 0))
        ttk.Label(root, textvariable=self.distance_var, font=("Segoe UI", 14)).pack()

        button_frame = ttk.Frame(root)
        button_frame.pack(pady=15)
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def start(self) -> None:
        if self._monitoring:
            return
        self._monitoring = True
        self.status_var.set("Running")
        self.start_button.state(["disabled"])
        self.stop_button.state(["!disabled"])

        self.app = EyeGuardApp(settings=self.settings, display=False)
        self.app.camera.start()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def _monitor_loop(self) -> None:
        assert self.app is not None
        while self._monitoring:
            frame = self.app.camera.read()
            if frame is None:
                time.sleep(0.2)
                continue
            distance = self.app._handle_frame(frame)
            label = "no face" if distance == float("inf") else f"{distance:.0f} cm"
            self.distance_var.set(label)
            time.sleep(self.settings.check_interval_s)

    def stop(self) -> None:
        self._monitoring = False
        if self.app is not None:
            self.app.shutdown()
            self.app = None
        self.status_var.set("Stopped")
        self.distance_var.set("-- cm")
        self.start_button.state(["!disabled"])
        self.stop_button.state(["disabled"])

    def _on_close(self) -> None:
        self.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    EyeGuardGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
