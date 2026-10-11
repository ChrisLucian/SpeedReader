"""The window advertises a newer release found by the background update check."""
from unittest.mock import patch

URL = "https://github.com/ChrisLucian/SpeedReader/releases/tag/v0.7"


def test_frame_show_update_sets_title(frame):
    frame.show_update("v0.7", URL)
    assert "v0.7 available" in frame.master.title()
    assert frame.contribute_link["text"] == "Get v0.7"
    with patch("webbrowser.open_new_tab") as open_tab:
        frame.open_contribute()
    open_tab.assert_called_once_with(URL)


def test_controller_starts_update_check(monkeypatch):
    from unittest.mock import Mock
    import Controllers.SpeedReaderController as module
    from Core.version import __version__
    check = Mock()
    monkeypatch.setattr(module, "check_in_background", check, raising=False)
    monkeypatch.setattr(module.SpeedReaderController, "maybe_host_mcp", lambda self, frame: None)
    app = module.SpeedReaderController()
    try:
        current, on_update = check.call_args.args
        assert current == __version__
        on_update("v9.9", URL)
        assert "v9.9" not in app.title()
        app.main_frame.pump_callbacks()
        assert "v9.9 available" in app.title()
    finally:
        app.destroy()
