"""Resume where you left off: the text and resume word survive restarts."""
import os

from Core import session


def test_build_logs_to_temp_not_beside_exe_nor_session_file(monkeypatch, tmp_path):
    monkeypatch.delenv("SPEEDREADER_SESSION", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert session.session_path() == os.path.join(str(tmp_path), "SpeedReader", "session.json")


def test_tests_never_touch_the_real_session_file(tmp_path):
    assert session.session_path() == str(tmp_path / "session.json")


def test_load_session_is_none_without_file():
    assert session.load_session() is None
