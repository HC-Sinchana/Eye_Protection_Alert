import json

from eyeguard.config import Settings, load_settings


def test_defaults_load_without_overrides(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = load_settings()
    assert settings.safe_distance_cm == Settings().safe_distance_cm


def test_json_override(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"safe_distance_cm": 55.0}))
    settings = load_settings()
    assert settings.safe_distance_cm == 55.0


def test_env_override_takes_precedence_over_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"safe_distance_cm": 55.0}))
    monkeypatch.setenv("EYEGUARD_SAFE_DISTANCE_CM", "70.0")
    settings = load_settings()
    assert settings.safe_distance_cm == 70.0


def test_invalid_json_falls_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text("{not valid json")
    settings = load_settings()
    assert settings.safe_distance_cm == Settings().safe_distance_cm
