"""Speed training (README advice): start low, add 25 WPM each time you finish a reading."""

TRAINING_STEP = 25


def next_training_wpm(wpm):
    """The speed to use after finishing a reading at ``wpm``."""
    return wpm + TRAINING_STEP
