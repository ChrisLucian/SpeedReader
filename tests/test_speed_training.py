"""Speed training: each fully finished reading adds 25 WPM, up to 500."""
from Core import speed_training


def test_next_training_wpm_adds_25():
    assert speed_training.next_training_wpm(200) == 225


def test_next_training_wpm_stops_at_500():
    assert [speed_training.next_training_wpm(w) for w in (490, 500, 600)] == [500, 500, 600]


def test_training_setting_round_trips():
    from Core import config
    assert config.load_ui_train() is False
    config.save_ui_train(True)
    assert config.load_ui_train() is True


def _finish(frame, name=7, completed=True, wpm="200"):
    frame.speed_var.set(wpm)
    frame.spoken_text = "Hello World"
    frame.current_session_id = frame.speech_session_id = 7
    frame.onEnd(name, completed)


def test_finished_reading_with_training_raises_speed(frame):
    from Core.config import load_ui_wpm
    frame.training_var.set(True)
    _finish(frame)
    assert frame.speed_var.get() == "225"
    assert load_ui_wpm() == 225


def test_training_off_keeps_speed(frame):
    _finish(frame)
    assert frame.speed_var.get() == "200"


def test_stopped_reading_does_not_train(frame):
    frame.training_var.set(True)
    _finish(frame, completed=False)
    assert frame.speed_var.get() == "200"


def test_agent_speech_does_not_train(frame):
    frame.training_var.set(True)
    _finish(frame, name=None)
    assert frame.speed_var.get() == "200"


def test_training_checkbox_is_saved(frame):
    from Core.config import load_ui_train
    frame.training_var.set(True)
    assert load_ui_train() is True


def test_app_starts_with_saved_training_on(monkeypatch, new_controller):
    from Controllers.SpeedReaderController import SpeedReaderController
    from Core.config import save_ui_train
    save_ui_train(True)
    monkeypatch.setattr(SpeedReaderController, "maybe_host_mcp", lambda self, frame: None)
    app = new_controller()
    try:
        assert app.winfo_children()[0].training_var.get() is True
    finally:
        app.destroy()
