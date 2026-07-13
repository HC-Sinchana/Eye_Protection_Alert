"""
Thin wrapper around ``imutils.video.VideoStream`` so the rest of the
codebase depends on a small, testable interface rather than the raw
camera object.
"""

from __future__ import annotations

import time

import imutils
from imutils.video import VideoStream


class Camera:
    """Context-manager friendly wrapper around imutils' VideoStream."""

    def __init__(
        self,
        src: int = 0,
        use_pi_camera: bool = False,
        resolution: tuple[int, int] = (640, 480),
        warmup_s: float = 2.0,
        frame_width: int = 800,
    ) -> None:
        self.src = src
        self.use_pi_camera = use_pi_camera
        self.resolution = resolution
        self.warmup_s = warmup_s
        self.frame_width = frame_width
        self._stream: VideoStream | None = None

    def start(self) -> "Camera":
        self._stream = VideoStream(
            src=self.src, usePiCamera=self.use_pi_camera, resolution=self.resolution
        ).start()
        time.sleep(self.warmup_s)  # let the sensor warm up
        return self

    def read(self):
        if self._stream is None:
            raise RuntimeError("Camera not started. Call start() first.")
        frame = self._stream.read()
        if frame is None:
            return None
        return imutils.resize(frame, width=self.frame_width)

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream = None

    def __enter__(self) -> "Camera":
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
