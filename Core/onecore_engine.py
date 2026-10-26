"""OneCore (Windows.Media.SpeechSynthesis) speech engine.

SAPI5 clamps its rate at ~470 WPM; OneCore's ``SpeakingRate`` goes to 6.0
(~840 WPM measured). ``BASE_WPM`` is OneCore David at SpeakingRate 1.0.
"""
BASE_WPM = 163
MIN_RATE = 0.5
MAX_RATE = 6.0


def speaking_rate(wpm):
    """Map words per minute to OneCore ``SpeakingRate`` (0.5-6.0, 1.0 = normal)."""
    return min(MAX_RATE, max(MIN_RATE, wpm / BASE_WPM))
