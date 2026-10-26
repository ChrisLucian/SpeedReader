"""OneCore (Windows.Media.SpeechSynthesis) speech engine.

SAPI5 clamps its rate at ~470 WPM; OneCore's ``SpeakingRate`` goes to 6.0
(~840 WPM measured). ``BASE_WPM`` is OneCore David at SpeakingRate 1.0.
"""
import threading
import time

BASE_WPM = 163
MIN_RATE = 0.5
MAX_RATE = 6.0


def speaking_rate(wpm):
    """Map words per minute to OneCore ``SpeakingRate`` (0.5-6.0, 1.0 = normal)."""
    return min(MAX_RATE, max(MIN_RATE, wpm / BASE_WPM))


def _ignore(**kwargs):
    pass


class OneCoreEngine:
    def __init__(self, on_start=None, on_word=None, on_end=None, backend=None):
        self._backend = backend
        self._on_start = on_start or _ignore
        self._on_word = on_word or _ignore
        self._on_end = on_end or _ignore
        self._voice = None
        self._stopped = threading.Event()
        self._speak_lock = threading.Lock()
        self._flush_generation = 0

    def get_voices(self):
        return self._backend.voices()

    def set_voice(self, voice_id):
        self._voice = voice_id

    def speak(self, text, rate, voice=None, block=True, interrupt=False, name=None):
        my_generation = self._flush_generation
        with self._speak_lock:
            if self._flush_generation == my_generation:
                self._speak_now(text, rate, voice, name)

    def _speak_now(self, text, rate, voice, name):
        wav, words = self._backend.synthesize(text, speaking_rate(rate), voice or self._voice)
        self._stopped.clear()
        self._on_start(name=name)
        started = time.monotonic()
        duration = self._backend.play(wav)
        for at, location, length in words:
            if self._wait_until(started + at):
                break
            self._on_word(name=name, location=location, length=length)
        completed = not self._wait_until(started + duration)
        self._on_end(name=name, completed=completed)

    def flush(self):
        self._flush_generation += 1
        self.stop()

    def stop(self):
        self._stopped.set()
        self._backend.stop()

    def _wait_until(self, deadline):
        """Sleep until ``deadline`` (monotonic); True if stopped meanwhile."""
        return self._stopped.wait(max(0.0, deadline - time.monotonic()))
