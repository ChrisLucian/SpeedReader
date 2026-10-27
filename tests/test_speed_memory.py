"""The Speed (WPM) the user picks is remembered in config.json across restarts."""
from Core.config import load_ui_wpm


def test_ui_wpm_defaults_to_500_without_file(tmp_path):
    assert load_ui_wpm(str(tmp_path / "missing.json")) == 500
