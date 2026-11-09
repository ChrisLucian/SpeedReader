import json
from tkinter import END

import pytest

from Core.theme import text_style


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"mcp": {"voices": ["voice-1"]}}))
    monkeypatch.setenv("SPEEDREADER_CONFIG", str(path))
    return path


def test_placeholder_shows_only_when_text_area_is_empty(frame):
    frame.update()
    assert frame.placeholder.place_info()
    frame.text_area.insert(END, "hello")
    frame.update()
    assert not frame.placeholder.place_info()
    frame.text_area.delete("1.0", END)
    frame.update()
    assert frame.placeholder.place_info()


def test_toggle_theme_flips_restyles_and_persists(frame, tmp_config):
    before = frame.theme
    for _ in range(2):  # both directions; sv-ttk's async tk_setPalette must not win
        frame.toggle_theme()
        frame.update()
        assert frame.text_area["background"] == text_style(frame.theme)["background"]
    frame.toggle_theme()
    assert frame.theme != before
    assert json.loads(tmp_config.read_text())["ui"]["theme"] == frame.theme


def test_light_theme_at_startup_keeps_text_area_colours(tmp_config, monkeypatch, new_controller):
    from Controllers.SpeedReaderController import SpeedReaderController
    from Core.theme import save_ui_theme
    save_ui_theme("light", path=str(tmp_config))
    app = new_controller()
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


def test_gui_does_not_host_mcp_or_show_server_button(frame):
    import mcp_server
    from Controllers.SpeedReaderController import SpeedReaderController
    assert not hasattr(SpeedReaderController, "maybe_host_mcp")
    assert not hasattr(frame, "server_button")
    assert not hasattr(mcp_server, "start_http_in_thread")
