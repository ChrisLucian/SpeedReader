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
