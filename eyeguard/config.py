"""
Configuration for EyeGuard.

Settings can be overridden by:
  1. A ``config.json`` file in the current working directory, or
  2. Environment variables prefixed with ``EYEGUARD_`` (e.g. ``EYEGUARD_SAFE_DISTANCE_CM``).

Environment variables take precedence over the JSON file, which takes
precedence over the defaults below.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class Settings:
    # --- Distance monitoring ---
    safe_distance_cm: float = 40.0  # minimum comfortable viewing distance
    real_face_width_cm: float = 14.0  # average human face width, used for the pinhole model
    focal_length_px: float = 500.0  # calibrate with calibrate.py for your webcam
    grace_period_s: float = 3.0  # seconds face must stay too close before alerting
    check_interval_s: float = 0.5  # seconds between distance checks
    alert_cooldown_s: float = 15.0  # minimum seconds between repeated alerts

    # --- Camera / detection ---
    camera_index: int = 0
    use_pi_camera: bool = False
    frame_width: int = 800
    use_clahe: bool = True  # improves detection in low light

    # --- Notifications ---
    notification_title: str = "Eye Protection Alert"
    notification_message: str = "You're sitting too close to the screen. Please move back."
    play_sound: bool = True

    # --- Logging ---
    log_level: str = "INFO"
    log_file: str = "eyeguard.log"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json_overrides() -> Dict[str, Any]:
    config_path = Path.cwd() / "config.json"
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _load_env_overrides(defaults: Settings) -> Dict[str, Any]:
    overrides: Dict[str, Any] = {}
    for field_name, value in asdict(defaults).items():
        env_key = f"EYEGUARD_{field_name.upper()}"
        if env_key in os.environ:
            raw = os.environ[env_key]
            try:
                if isinstance(value, bool):
                    overrides[field_name] = raw.strip().lower() in ("1", "true", "yes", "on")
                elif isinstance(value, int):
                    overrides[field_name] = int(raw)
                elif isinstance(value, float):
                    overrides[field_name] = float(raw)
                else:
                    overrides[field_name] = raw
            except ValueError:
                continue
    return overrides


def load_settings() -> Settings:
    """Build a Settings object from defaults, config.json, then environment variables."""
    settings = Settings()
    json_overrides = _load_json_overrides()
    env_overrides = _load_env_overrides(settings)

    merged = {**json_overrides, **env_overrides}
    valid_fields = asdict(settings).keys()
    filtered = {k: v for k, v in merged.items() if k in valid_fields}

    return Settings(**{**asdict(settings), **filtered})


SETTINGS = load_settings()
