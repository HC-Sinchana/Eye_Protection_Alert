"""
Cross-platform alert notifications.

The original prototype used ``ctypes.windll.user32.MessageBoxW``, which
only works on Windows. This module tries a native desktop notification
first (via ``plyer``, which supports Windows/macOS/Linux), and falls back
to a Tkinter popup, and finally to a console beep + printed message if no
GUI is available (e.g. running headless/CI).
"""

from __future__ import annotations

import logging
import sys
import time

logger = logging.getLogger("eyeguard.notifier")


class Notifier:
    def __init__(self, title: str, message: str, cooldown_s: float = 15.0, play_sound: bool = True) -> None:
        self.title = title
        self.message = message
        self.cooldown_s = cooldown_s
        self.play_sound = play_sound
        self._last_alert_ts: float = 0.0

    def _on_cooldown(self) -> bool:
        return (time.monotonic() - self._last_alert_ts) < self.cooldown_s

    def notify(self) -> None:
        """Fire an alert, respecting the cooldown between repeated alerts."""
        if self._on_cooldown():
            return
        self._last_alert_ts = time.monotonic()

        if self.play_sound:
            self._beep()

        for backend in (self._notify_plyer, self._notify_tkinter, self._notify_console):
            try:
                backend()
                return
            except Exception as exc:  # noqa: BLE001 - fall through to next backend
                name = getattr(backend, "__name__", repr(backend))
                logger.debug("Notification backend %s failed: %s", name, exc)
        logger.warning("All notification backends failed; alert was only logged.")

    def _beep(self) -> None:
        try:
            print("\a", end="", flush=True)  # terminal bell
        except Exception:
            pass

    def _notify_plyer(self) -> None:
        from plyer import notification as plyer_notification

        plyer_notification.notify(title=self.title, message=self.message, timeout=10, app_name="EyeGuard")

    def _notify_tkinter(self) -> None:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showwarning(self.title, self.message, parent=root)
        root.destroy()

    def _notify_console(self) -> None:
        logger.warning("%s: %s", self.title, self.message)
        print(f"[ALERT] {self.title}: {self.message}", file=sys.stderr)
