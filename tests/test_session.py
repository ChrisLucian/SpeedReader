"""Resume where you left off: the text and resume word survive restarts."""
import json
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


def test_save_session_round_trips_text_and_offset(tmp_path):
    path = str(tmp_path / "new" / "session.json")
    session.save_session("Hello World", 6, path)
    assert session.load_session(path) == ("Hello World", 6)


def test_load_session_resets_bad_offset_to_start(tmp_path):
    path = tmp_path / "session.json"
    for bad in (999, -3, "x"):
        path.write_text(json.dumps({"text": "Hello World", "offset": bad}))
        assert session.load_session(str(path)) == ("Hello World", 0)


def test_load_session_ignores_corrupt_file(tmp_path):
    path = tmp_path / "session.json"
    path.write_text("not json")
    assert session.load_session(str(path)) is None


def test_save_session_reports_unwritable_location(tmp_path):
    assert session.save_session("x", 0, str(tmp_path)) is False
