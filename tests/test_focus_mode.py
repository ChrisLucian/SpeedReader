"""F11 focus mode: only the big current word (and its neighbours) stay visible."""


def test_focus_mode_hides_text_and_settings(frame):
    frame.toggle_focus()
    assert frame.text_area.grid_info() == {}
    assert frame.settings_frame.grid_info() == {}
