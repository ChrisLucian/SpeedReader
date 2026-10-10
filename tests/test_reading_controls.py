"""Pause/Resume and read-from-word, driven without real speech."""
from tkinter import END
from unittest.mock import Mock


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
