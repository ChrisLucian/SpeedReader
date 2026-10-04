import json
from tkinter import END, StringVar
from unittest.mock import MagicMock

import pytest

from Core.theme import text_style
from Frames import dialogs


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"mcp": {"enabled": True, "voices": ["voice-1"], "port": 8765}}))
    monkeypatch.setenv("SPEEDREADER_CONFIG", str(path))
    return path


def test_placeholder_shows_only_when_text_area_is_empty(frame):
    frame.update()
    assert frame.placeholder.winfo_ismapped()
    frame.text_area.insert(END, "hello")
    frame.update()
    assert not frame.placeholder.winfo_ismapped()
    frame.text_area.delete("1.0", END)
    frame.update()
    assert frame.placeholder.winfo_ismapped()


def test_toggle_theme_flips_restyles_and_persists(frame, tmp_config):
    before = frame.theme
    for _ in range(2):  # both directions; sv-ttk's async tk_setPalette must not win
        frame.toggle_theme()
        frame.update()
        assert frame.text_area["background"] == text_style(frame.theme)["background"]
    frame.toggle_theme()
    assert frame.theme != before
    assert json.loads(tmp_config.read_text())["ui"]["theme"] == frame.theme


def test_light_theme_at_startup_keeps_text_area_colours(tmp_config, monkeypatch):
    from Controllers.SpeedReaderController import SpeedReaderController
    from Core.theme import save_ui_theme
    save_ui_theme("light", path=str(tmp_config))
    monkeypatch.setattr(SpeedReaderController, "maybe_host_mcp", lambda self, frame: None)
    app = SpeedReaderController()
    try:
        app.update()
        frame = app.winfo_children()[0]
        assert frame.text_area["background"] == text_style("light")["background"]
    finally:
        app.destroy()


def test_speak_is_the_accent_button(frame):
    assert str(frame.speak_button["style"]) == "Accent.TButton"


def test_text_area_row_takes_spare_space_not_title(frame):
    title_row = frame.title.grid_info()["row"]
    text_row = frame.text_area.grid_info()["row"]
    assert frame.grid_rowconfigure(title_row)["weight"] == 0
    assert frame.grid_rowconfigure(text_row)["weight"] == 1


def test_server_dialog_without_host_reports_not_hosting(frame, tmp_config):
    frame.mcp_host = None
    dialog = dialogs.open_server_dialog(frame)
    try:
        assert "not hosting" in dialogs.server_status_text(frame)
    finally:
        dialog.destroy()


def test_restart_server_restarts_and_persists_port(frame, tmp_config):
    frame.mcp_host = MagicMock()
    result = StringVar(master=frame)
    button = MagicMock()
    dialogs.restart_server(frame, "9300", result, button)
    frame.mcp_host.restart.assert_called_once_with(port=9300)
    saved = json.loads(tmp_config.read_text())["mcp"]
    assert saved["port"] == 9300
    assert saved["voices"] == ["voice-1"]  # voices untouched
    assert result.get() == "running on 9300"


def test_restart_server_rejects_invalid_port(frame, tmp_config):
    frame.mcp_host = MagicMock()
    result = StringVar(master=frame)
    dialogs.restart_server(frame, "99999", result, MagicMock())
    frame.mcp_host.restart.assert_not_called()
    assert result.get() == "port out of range"
