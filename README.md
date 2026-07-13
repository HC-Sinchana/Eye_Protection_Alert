# EyeGuard — Eye Protection Alert System

[![CI](https://github.com/your-username/eyeguard/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/eyeguard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

EyeGuard watches you through your webcam and gives you a friendly nudge when
you've been sitting too close to the screen for too long — helping reduce
eye strain and Computer Vision Syndrome (CVS) during long study, work, or
gaming sessions.

It uses real-time face detection to estimate the distance between your face
and the screen, and fires a desktop alert when you're closer than a
configurable safe threshold for longer than a configurable grace period.

## Features

- 📏 **Real-time distance monitoring** using a standard webcam and OpenCV's Haar cascade face detector
- 🔔 **Cross-platform alerts** (native OS notifications via `plyer`, with a Tkinter and console fallback)
- 🌓 **Low-light robustness** via CLAHE contrast enhancement
- 🧵 **Non-blocking** — monitoring runs without freezing the rest of your desktop
- ⚙️ **Configurable** via `config.json` or environment variables (safe distance, grace period, cooldown, camera index, etc.)
- 🎯 **Calibration tool** to compute an accurate focal length for your specific webcam
- 🖥️ **Optional GUI** control panel (Start/Stop + live distance readout)
- ✅ **Tested** with a pytest suite that doesn't require a physical camera

## How it works

1. `imutils.video.VideoStream` captures live frames from the webcam.
2. Each frame is converted to grayscale and (optionally) contrast-enhanced with CLAHE.
3. A Haar cascade classifier detects faces and returns bounding boxes.
4. The detected face width (in pixels) is converted to a real-world distance
   using the pinhole camera model:

   ```
   distance_cm = (real_face_width_cm * focal_length_px) / face_width_px
   ```

5. If the closest face stays below `safe_distance_cm` for longer than
   `grace_period_s`, EyeGuard fires a notification (respecting a cooldown so
   you aren't spammed).

## Installation

```bash
git clone https://github.com/your-username/eyeguard.git
cd eyeguard
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install .
```

## Usage

Run the monitor:

```bash
python -m eyeguard
# or, after `pip install .`:
eyeguard
```

Run with a live annotated video preview (handy while tuning settings):

```bash
python -m eyeguard --display
```

Launch the optional GUI control panel:

```bash
python -m eyeguard.gui
```

Stop the monitor any time with `Ctrl+C` (or the Stop button in the GUI).

### Calibrating for your webcam

The default `focal_length_px` is a rough estimate. For accurate distance
readings, calibrate it for your own camera:

```bash
python -m eyeguard.calibrate --known-distance 40 --face-width 14
```

1. Sit exactly 40 cm (or your chosen distance) from the screen.
2. Press `c` when your face box appears on screen.
3. The computed focal length is saved to `config.json` automatically.

### Configuration

Copy `config.example.json` to `config.json` and edit as needed, or set
environment variables prefixed with `EYEGUARD_` (e.g.
`EYEGUARD_SAFE_DISTANCE_CM=50`). See [`eyeguard/config.py`](eyeguard/config.py)
for the full list of settings and defaults.

| Setting | Default | Description |
|---|---|---|
| `safe_distance_cm` | 40.0 | Minimum comfortable viewing distance |
| `grace_period_s` | 3.0 | How long you must be too close before an alert fires |
| `alert_cooldown_s` | 15.0 | Minimum time between repeated alerts |
| `check_interval_s` | 0.5 | How often frames are analyzed |
| `camera_index` | 0 | Which camera to use |
| `use_pi_camera` | false | Set true when running on a Raspberry Pi camera module |

## Project layout

```
eyeguard/
├── eyeguard/
│   ├── app.py           # main monitoring loop / CLI entry point
│   ├── calibrate.py      # focal-length calibration tool
│   ├── config.py          # settings loading (defaults, JSON, env vars)
│   ├── detector.py        # face detection + distance estimation
│   ├── gui.py              # optional Tkinter control panel
│   ├── notifier.py          # cross-platform alert notifications
│   └── video_stream.py       # webcam lifecycle wrapper (imutils)
├── tests/                      # pytest suite (no camera hardware needed)
├── docs/                         # project report / background reading
├── config.example.json
├── requirements.txt
└── pyproject.toml
```

## Running tests

```bash
pip install -r requirements-dev.txt
pytest --cov=eyeguard
```

## Requirements

- Python 3.9+
- A webcam
- OpenCV, imutils, numpy, plyer (see `requirements.txt`)

## Background

This project grew out of an "Eye Protection Alert System" report exploring
Computer Vision Syndrome and the gap left by existing tools (blue-light
filters, break reminders, posture guides) that don't monitor viewing
*distance*. See [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) for the
full background, motivation, and module breakdown. The original single-file
Windows-only prototype has been refactored here into a tested, configurable,
cross-platform package.

## Roadmap

- [ ] Deep-learning based face detection (e.g. MediaPipe) for better accuracy
- [ ] Cross-platform packaging (PyInstaller builds for Windows/macOS/Linux)
- [ ] Customizable per-user distance profiles
- [ ] Break-timer integration
- [ ] System tray icon instead of a separate GUI window

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
