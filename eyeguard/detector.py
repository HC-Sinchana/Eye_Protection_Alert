"""
Face detection and distance-estimation logic.

Uses OpenCV's Haar cascade classifier to find faces in a video frame, then
estimates the real-world distance from the camera using the simple pinhole
camera model:

    distance = (real_face_width * focal_length) / face_width_in_pixels

``focal_length`` is a camera-specific constant. Use ``calibrate.py`` to
compute an accurate value for your webcam instead of relying on the
default estimate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np


@dataclass
class DetectionResult:
    faces: List[Tuple[int, int, int, int]]  # (x, y, w, h) boxes
    distances_cm: List[float]

    @property
    def closest_distance_cm(self) -> float:
        return min(self.distances_cm) if self.distances_cm else float("inf")

    @property
    def face_detected(self) -> bool:
        return len(self.faces) > 0


class FaceDistanceDetector:
    """Wraps a Haar cascade face detector plus the distance formula."""

    def __init__(
        self,
        focal_length_px: float = 500.0,
        real_face_width_cm: float = 14.0,
        use_clahe: bool = True,
        cascade_path: str | None = None,
    ) -> None:
        self.focal_length_px = focal_length_px
        self.real_face_width_cm = real_face_width_cm
        self.use_clahe = use_clahe

        path = cascade_path or (cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.cascade = cv2.CascadeClassifier(path)
        if self.cascade.empty():
            raise RuntimeError(f"Could not load Haar cascade from: {path}")

        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) if use_clahe else None

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self._clahe is not None:
            gray = self._clahe.apply(gray)
        return gray

    def detect(self, frame: np.ndarray) -> DetectionResult:
        gray = self._preprocess(frame)
        faces = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        distances = [self.distance_from_face_width(w) for (_, _, w, _) in faces]
        return DetectionResult(faces=list(faces), distances_cm=distances)

    def distance_from_face_width(self, face_width_px: float) -> float:
        """Estimate distance (cm) from a detected face width (px)."""
        if face_width_px <= 0:
            return float("inf")
        return (self.real_face_width_cm * self.focal_length_px) / face_width_px

    @staticmethod
    def draw_annotations(frame: np.ndarray, result: DetectionResult, safe_distance_cm: float) -> np.ndarray:
        """Draw bounding boxes and distance labels on a copy of the frame."""
        annotated = frame.copy()
        for (x, y, w, h), distance in zip(result.faces, result.distances_cm):
            too_close = distance < safe_distance_cm
            color = (0, 0, 255) if too_close else (0, 200, 0)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            label = f"{distance:.0f} cm"
            cv2.putText(
                annotated,
                label,
                (x, max(y - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )
        return annotated
