"""Pause/Resume and read-from-word, driven without real speech."""
from tkinter import END
from unittest.mock import Mock


def test_pause_stops_and_remembers_current_word(frame):
    frame.speech.stop = Mock()
    frame.spoken_text = "Hello World"
    frame.onStartWord(None, 6, 5)
    frame.pause_reading()
    assert frame.paused_at == 6
    frame.speech.stop.assert_called_once()
    assert frame.pause_button["text"] == "Resume"


def test_resume_speaks_rest_from_paused_word(frame):
    frame.speak_on_thread = Mock()
    frame.spoken_text = "Hello World"
    frame.paused_at = 6
    frame.resume_reading()
    frame.thread.join(1)
    assert frame.speak_on_thread.call_args.args[1] == "World"
    assert frame.speak_offset == 6
    assert frame.paused_at is None
    assert frame.pause_button["text"] == "Pause"


def test_speak_resets_speak_offset(frame):
    frame.speak_on_thread = Mock()
    frame.text_area.insert(END, "Hi there")
    frame.speak_offset = 6
    frame.speak(None)
    frame.thread.join(1)
    assert frame.speak_offset == 0


def test_word_location_is_shifted_by_speak_offset(frame):
    frame.spoken_text = "Hello World"
    frame.speak_offset = 6
    frame.onStartWord(None, 0, 5)
    assert frame.current_word_label["text"] == "World"
