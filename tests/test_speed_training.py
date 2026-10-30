"""Speed training: each fully finished reading adds 25 WPM, up to 500."""
from Core import speed_training


def test_next_training_wpm_adds_25():
    assert speed_training.next_training_wpm(200) == 225
