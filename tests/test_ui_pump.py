"""Engine callbacks reach widgets only via the UI-thread pump."""
import time
from unittest.mock import Mock


def test_external_speech_renders_via_pump(frame):
    frame.speech.speak = Mock()
    frame.speak_external("agent text", 300)
    assert frame.text_area.get("1.0", "end-1c") == ""
    frame.pump_callbacks()
    assert frame.text_area.get("1.0", "end-1c") == "agent text"


def test_pump_reschedules_itself(frame):
    from Frames.ui_pump import PUMP_MS
    calls = []
    for value in (1, 2):
        frame.callbacks.post(calls.append, value)
        time.sleep(PUMP_MS * 3 / 1000)
        frame.update()
    assert calls == [1, 2]


def test_engine_word_callback_waits_for_ui_pump(frame):
    frame.spoken_text = "Hello World"
    frame.speech._on_word(None, 0, 5)
    assert frame.current_word_label["text"] == ""
    frame.pump_callbacks()
    assert frame.current_word_label["text"] == "Hello"
