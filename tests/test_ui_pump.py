"""Engine callbacks reach widgets only via the UI-thread pump."""
import time


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
