"""The Speed (WPM) the user picks is remembered in config.json across restarts."""
import json

from Core import config
from Core.config import load_ui_wpm


def test_ui_wpm_defaults_to_500_without_file(tmp_path):
    assert load_ui_wpm(str(tmp_path / "missing.json")) == 500


def test_save_ui_wpm_round_trips_and_preserves_other_keys(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"mcp": {"enabled": True}, "ui": {"theme": "light"}}))
    config.save_ui_wpm(650, path=str(path))
    assert load_ui_wpm(str(path)) == 650
    data = json.loads(path.read_text())
    assert data["mcp"] == {"enabled": True}
    assert data["ui"]["theme"] == "light"


def test_out_of_range_saved_wpm_falls_back_to_default(tmp_path):
    path = tmp_path / "config.json"
    for bad in (7, "fast", 5000):
        path.write_text(json.dumps({"ui": {"wpm": bad}}))
        assert load_ui_wpm(str(path)) == 500


def test_changing_speed_saves_wpm(frame):
    frame.speed_var.set("650")
    assert load_ui_wpm() == 650
    assert frame.speak_service.rate == 650


def test_partial_speed_entry_keeps_last_saved_wpm(frame):
    frame.speed_var.set("650")
    frame.speed_var.set("6")  # mid-typing; also guards time-left from 0 WPM
    assert load_ui_wpm() == 650
    assert frame.speak_service.rate == 650
