"""Opening .txt/.md files into the text area (dialog always mocked)."""
from types import SimpleNamespace
from unittest.mock import patch


def test_open_file_loads_text_area(frame, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("hello file", encoding="utf-8")
    frame.text_area.insert("end", "old")
    frame.open_file(str(path))
    assert frame.text_area.get("1.0", "end-1c") == "hello file"


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
