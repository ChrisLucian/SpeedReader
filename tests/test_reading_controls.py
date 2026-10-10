"""Pause/Resume and read-from-word, driven without real speech."""
from tkinter import END
from types import SimpleNamespace
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


def test_read_from_index_starts_at_clicked_word(frame):
    frame.speak_on_thread = Mock()
    frame.text_area.insert(END, "Hello World")
    frame.read_from_index("1.8")
    frame.thread.join(1)
    assert frame.speak_on_thread.call_args.args[1] == "World"
    assert frame.speak_offset == 6


def test_double_click_reads_from_word(frame):
    frame.read_from_index = Mock()
    assert frame.text_area.bind("<Double-Button-1>")
    frame.on_text_double_click(SimpleNamespace(x=5, y=5))
    frame.read_from_index.assert_called_once_with("@5,5")


def test_pause_button_toggles_pause_and_resume(frame):
    frame.speech.stop = Mock()
    frame.speak_on_thread = Mock()
    frame.spoken_text = "Hello World"
    frame.is_speaking = True
    frame.onStartWord(None, 6, 5)
    frame.pause_button.invoke()
    assert frame.paused_at == 6
    assert frame.pause_button["text"] == "Resume"
    frame.pause_button.invoke()
    frame.thread.join(1)
    assert frame.speak_on_thread.call_args.args[1] == "World"
    assert frame.pause_button["text"] == "Pause"


def test_pause_before_first_word_resumes_from_start(frame):
    frame.speech.stop = Mock()
    frame.pause_reading()
    assert frame.paused_at == 0


def test_read_from_index_preprocesses_raw_text(frame):
    frame.speak_on_thread = Mock()
    frame.text_area.insert(END, "see http://x.com\nnow")
    frame.read_from_index("2.0")
    frame.thread.join(1)
    assert frame.speak_on_thread.call_args.args[1] == "now"
    shown = frame.text_area.get("1.0", "end-1c")
    assert "\n" not in shown and "[URL]" in shown


def test_external_speech_resets_speak_offset(frame):
    frame.speech.speak = Mock()
    frame.speak_offset = 6
    frame.speak_external("agent", 300)
    frame.pump_callbacks()
    assert frame.speak_offset == 0


def test_pause_button_when_idle_does_nothing(frame):
    frame.speech.stop = Mock()
    frame.pause_button.invoke()
    assert frame.paused_at is None
    frame.speech.stop.assert_not_called()
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
