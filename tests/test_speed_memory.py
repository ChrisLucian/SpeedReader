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
