"""Opening .txt/.md files into the text area (dialog always mocked)."""
from types import SimpleNamespace
from unittest.mock import patch


def test_open_file_loads_text_area(frame, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("hello file", encoding="utf-8")
    frame.text_area.insert("end", "old")
    frame.open_file(str(path))
    assert frame.text_area.get("1.0", "end-1c") == "hello file"


def test_ctrl_o_opens_chosen_file(frame, tmp_path):
    path = tmp_path / "b.md"
    path.write_text("# notes", encoding="utf-8")
    assert frame.master.bind("<Control-o>")
    with patch("tkinter.filedialog.askopenfilename", return_value=str(path)):
        assert frame.on_open_file(None) == "break"
    assert frame.text_area.get("1.0", "end-1c") == "# notes"


def test_controller_opens_file_from_args(app, tmp_path):
    path = tmp_path / "dropped.txt"
    path.write_text("dropped text", encoding="utf-8")
    app.open_from_args(["SpeedReader.exe"])
    assert app.main_frame.text_area.get("1.0", "end-1c") == ""
    app.open_from_args(["SpeedReader.exe", str(path)])
    assert app.main_frame.text_area.get("1.0", "end-1c") == "dropped text"


def test_ctrl_o_cancel_keeps_text(frame):
    frame.text_area.insert("end", "keep me")
    with patch("tkinter.filedialog.askopenfilename", return_value=""):
        frame.on_open_file(None)
    assert frame.text_area.get("1.0", "end-1c") == "keep me"


def test_open_file_loads_text_area_and_clears_old_word(frame, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("hello file", encoding="utf-8")
    frame.current_word_label["text"] = "old"
    frame.open_file(str(path))
    assert frame.current_word_label["text"] == ""


def test_open_file_loads_text_area_after_stopping_speech(frame, tmp_path):
    from unittest.mock import Mock
    path = tmp_path / "a.txt"
    path.write_text("hello file", encoding="utf-8")
    frame.force_stop_and_reset = Mock()
    frame.open_file(str(path))
    frame.force_stop_and_reset.assert_called_once_with()
