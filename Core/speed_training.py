"""Speed training (README advice): start low, add 25 WPM each time you finish a reading."""

TRAINING_STEP, TRAINING_GOAL = 25, 500


def next_training_wpm(wpm):
    """The speed to use after finishing a reading at ``wpm``; never past 500, never lower."""
    return max(wpm, min(wpm + TRAINING_STEP, TRAINING_GOAL))
