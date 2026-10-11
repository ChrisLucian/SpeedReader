"""Opening .txt/.md files into the text area (dialog always mocked)."""
from types import SimpleNamespace
from unittest.mock import patch


def test_open_file_loads_text_area(frame, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("hello file", encoding="utf-8")
    frame.text_area.insert("end", "old")
    frame.open_file(str(path))
    assert frame.text_area.get("1.0", "end-1c") == "hello file"
