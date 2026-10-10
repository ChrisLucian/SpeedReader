"""Engine callbacks reach widgets only via the UI-thread pump."""


def test_engine_word_callback_waits_for_ui_pump(frame):
    frame.spoken_text = "Hello World"
    frame.speech._on_word(None, 0, 5)
    assert frame.current_word_label["text"] == ""
    frame.pump_callbacks()
    assert frame.current_word_label["text"] == "Hello"
