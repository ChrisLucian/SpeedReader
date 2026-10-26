import Core.onecore_engine as onecore
from Core.onecore_engine import speaking_rate


class FakeBackend:
    def __init__(self, words=(), duration=0.0):
        self.words = list(words)
        self.duration = duration
        self.synthesized = []
        self.played = []

    def synthesize(self, text, rate, voice_id=None):
        self.synthesized.append((text, rate, voice_id))
        return b'wav', self.words

    def play(self, wav):
        self.played.append(wav)
        return self.duration


def test_speaking_rate_maps_wpm_and_clamps():
    assert speaking_rate(326) == 2.0
    assert speaking_rate(5000) == 6.0
    assert speaking_rate(10) == 0.5


def test_speak_synthesizes_with_rate_and_default_voice():
    fake = FakeBackend()
    engine = onecore.OneCoreEngine(backend=fake)
    engine.set_voice('v1')

    engine.speak('hi', 326)

    assert fake.synthesized == [('hi', 2.0, 'v1')]
    assert fake.played == [b'wav']
