"""
Main application loop for EyeGuard.

Run with ``python -m eyeguard`` or ``eyeguard`` (after install) from the
command line. Add ``--display`` to show a live annotated video window,
useful for calibration and debugging.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from typing import Optional

from eyeguard.config import Settings, load_settings
from eyeguard.detector import FaceDistanceDetector
from eyeguard.notifier import Notifier
from eyeguard.video_stream import Camera


def setup_logging(level: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger("eyeguard")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not open log file %s; logging to console only.", log_file)

    return logger


class EyeGuardApp:
    """Coordinates the camera, detector, and notifier in a monitoring loop."""

    def __init__(self, settings: Optional[Settings] = None, display: bool = False) -> None:
        self.settings = settings or load_settings()
        self.display = display
        self.logger = setup_logging(self.settings.log_level, self.settings.log_file)

        self.camera = Camera(
            src=self.settings.camera_index,
            use_pi_camera=self.settings.use_pi_camera,
            frame_width=self.settings.frame_width,
        )
        self.detector = FaceDistanceDetector(
            focal_length_px=self.settings.focal_length_px,
            real_face_width_cm=self.settings.real_face_width_cm,
            use_clahe=self.settings.use_clahe,
        )
        self.notifier = Notifier(
            title=self.settings.notification_title,
            message=self.settings.notification_message,
            cooldown_s=self.settings.alert_cooldown_s,
            play_sound=self.settings.play_sound,
        )

        self._running = False
        self._too_close_since: Optional[float] = None

    def _handle_frame(self, frame) -> float:
        """Process a single frame; returns the closest detected distance (cm, inf if none)."""
        result = self.detector.detect(frame)
        distance = result.closest_distance_cm

        now = time.monotonic()
        if distance < self.settings.safe_distance_cm:
            if self._too_close_since is None:
                self._too_close_since = now
            elif (now - self._too_close_since) >= self.settings.grace_period_s:
                self.notifier.notify()
        else:
            self._too_close_since = None

        if self.display:
            import cv2

            annotated = self.detector.draw_annotations(frame, result, self.settings.safe_distance_cm)
            cv2.imshow("EyeGuard", annotated)
            cv2.waitKey(1)

        return distance

    def run(self) -> None:
        self.logger.info("Starting EyeGuard (safe distance = %.1f cm)", self.settings.safe_distance_cm)
        self._running = True
        self.camera.start()

        def _stop(*_args):
            self.logger.info("Shutdown signal received.")
            self._running = False

        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)

        try:
            while self._running:
                frame = self.camera.read()
                if frame is None:
                    self.logger.warning("No frame received from camera; retrying...")
                    time.sleep(0.5)
                    continue

                distance = self._handle_frame(frame)
                self.logger.debug("Closest face distance: %.1f cm", distance)
                time.sleep(self.settings.check_interval_s)
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        self.camera.stop()
        if self.display:
            try:
                import cv2

                cv2.destroyAllWindows()
            except Exception:
                pass
        self.logger.info("EyeGuard stopped.")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EyeGuard - Eye Protection Alert System")
    parser.add_argument(
        "--display",
        action="store_true",
        help="Show a live annotated video window (useful for calibration/debugging).",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    app = EyeGuardApp(display=args.display)
    try:
        app.run()
    except RuntimeError as exc:
        app.logger.error(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
