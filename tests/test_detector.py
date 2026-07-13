import math

import numpy as np
import pytest

from eyeguard.detector import DetectionResult, FaceDistanceDetector


@pytest.fixture
def detector() -> FaceDistanceDetector:
    return FaceDistanceDetector(focal_length_px=500.0, real_face_width_cm=14.0)


def test_distance_from_face_width_matches_pinhole_formula(detector: FaceDistanceDetector) -> None:
    face_width_px = 200
    expected = (14.0 * 500.0) / face_width_px
    assert detector.distance_from_face_width(face_width_px) == pytest.approx(expected)


def test_distance_from_zero_width_is_infinite(detector: FaceDistanceDetector) -> None:
    assert detector.distance_from_face_width(0) == float("inf")


def test_closer_face_yields_smaller_distance(detector: FaceDistanceDetector) -> None:
    far = detector.distance_from_face_width(100)
    near = detector.distance_from_face_width(300)
    assert near < far


def test_detection_result_closest_distance_with_no_faces() -> None:
    result = DetectionResult(faces=[], distances_cm=[])
    assert result.closest_distance_cm == float("inf")
    assert result.face_detected is False


def test_detection_result_closest_distance_picks_minimum() -> None:
    result = DetectionResult(faces=[(0, 0, 10, 10), (0, 0, 20, 20)], distances_cm=[80.0, 35.0])
    assert result.closest_distance_cm == 35.0
    assert result.face_detected is True


def test_detect_on_blank_frame_returns_no_faces(detector: FaceDistanceDetector) -> None:
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = detector.detect(blank_frame)
    assert result.faces == []
    assert math.isinf(result.closest_distance_cm)
