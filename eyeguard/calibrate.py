"""
Focal length calibration helper.

The distance formula (``distance = real_face_width * focal_length /
face_width_px``) needs a focal length constant that depends on your
specific webcam. To calibrate:

1. Sit exactly ``KNOWN_DISTANCE_CM`` away from your screen/webcam.
2. Run: ``python -m eyeguard.calibrate``
3. Press ``c`` when your face is detected to capture the calibration
   sample. The computed focal length is printed and, if confirmed,
   written to ``config.json``.

Usage:
    python -m eyeguard.calibrate --known-distance 40 --face-width 14
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from eyeguard.video_stream import Camera


def compute_focal_length(known_distance_cm: float, real_face_width_cm: float, face_width_px: float) -> float:
    return (face_width_px * known_distance_cm) / real_face_width_cm


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate EyeGuard's focal length for your webcam.")
    parser.add_argument(
        "--known-distance", type=float, default=40.0, help="Distance (cm) you are sitting at right now."
    )
    parser.add_argument(
        "--face-width", type=float, default=14.0, help="Your real face width (cm), ~14cm average."
    )
    parser.add_argument("--camera-index", type=int, default=0)
    args = parser.parse_args()

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    print(f"Sit exactly {args.known_distance} cm from the camera.")
    print("Press 'c' to capture once your face box appears. Press 'q' to quit without saving.")

    with Camera(src=args.camera_index) as camera:
        while True:
            frame = camera.read()
            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            display = frame.copy()
            face_width_px = None
            for x, y, w, h in faces:
                face_width_px = w
                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 200, 0), 2)

            cv2.imshow("Calibration - press 'c' to capture, 'q' to quit", display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                cv2.destroyAllWindows()
                print("Calibration cancelled.")
                return 1

            if key == ord("c") and face_width_px:
                cv2.destroyAllWindows()
                focal_length = compute_focal_length(args.known_distance, args.face_width, face_width_px)
                print(f"\nDetected face width: {face_width_px}px")
                print(f"Computed focal length: {focal_length:.2f}")

                config_path = Path.cwd() / "config.json"
                existing = {}
                if config_path.exists():
                    try:
                        existing = json.loads(config_path.read_text())
                    except json.JSONDecodeError:
                        existing = {}
                existing["focal_length_px"] = round(focal_length, 2)
                existing["real_face_width_cm"] = args.face_width
                config_path.write_text(json.dumps(existing, indent=2))
                print(f"Saved to {config_path}")
                return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
