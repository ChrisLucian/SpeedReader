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
