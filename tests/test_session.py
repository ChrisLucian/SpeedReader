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


def _reading(frame, text="Hello World", location=6):
    frame.spoken_text = text
    frame.text_area.delete("1.0", "end")
    frame.text_area.insert("end", text)
    frame.current_location = location
    frame.current_session_id = frame.speech_session_id = 7
    return 7


def test_pausing_saves_resume_word(frame):
    session_id = _reading(frame)
    frame.paused_at = 6
    frame.onEnd(session_id, False)
    assert session.load_session() == ("Hello World", 6)


def test_finished_reading_saves_from_start(frame):
    session_id = _reading(frame)
    frame.onEnd(session_id, True)
    with open(session.session_path(), encoding="utf-8") as handle:
        assert json.load(handle) == {"text": "Hello World", "offset": 0}


def test_agent_speech_keeps_saved_session(frame):
    session.save_session("Mine", 2)
    _reading(frame, "Agent says hi", 0)
    frame.onEnd(None, True)
    assert session.load_session() == ("Mine", 2)


def test_edited_text_saves_from_start(frame):
    session_id = _reading(frame)
    frame.paused_at = 6
    frame.text_area.delete("1.0", "end")
    frame.text_area.insert("end", "Other text")
    frame.onEnd(session_id, False)
    assert session.load_session() == ("Other text", 0)
