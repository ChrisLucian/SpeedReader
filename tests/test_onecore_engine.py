import threading
import time

import Core.onecore_engine as onecore
from Core.onecore_engine import speaking_rate


class FakeBackend:
    def __init__(self, words=(), duration=0.0):
        self.words = list(words)
        self.duration = duration
        self.synthesized = []
        self.played = []
        self.playing = threading.Event()
        self.stopped = False

    def synthesize(self, text, rate, voice_id=None):
        self.synthesized.append((text, rate, voice_id))
        return b'wav', self.words

    def play(self, wav):
        self.played.append(wav)
        self.playing.set()
        return self.duration

    def stop(self):
        self.stopped = True


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


def recording_engine(fake):
    events = []
    engine = onecore.OneCoreEngine(
        on_start=lambda **kw: events.append(('start', kw)),
        on_word=lambda **kw: events.append(('word', kw)),
        on_end=lambda **kw: events.append(('end', kw)),
        backend=fake)
    return engine, events


def test_speak_reports_start_words_end():
    engine, events = recording_engine(FakeBackend(words=[(0, 0, 2), (0, 3, 5)]))

    engine.speak('hi there', 163, name=7)

    assert events == [
        ('start', {'name': 7}),
        ('word', {'name': 7, 'location': 0, 'length': 2}),
        ('word', {'name': 7, 'location': 3, 'length': 5}),
        ('end', {'name': 7, 'completed': True}),
    ]


def speak_on_thread(engine, text='hi'):
    thread = threading.Thread(target=engine.speak, args=(text, 163), daemon=True)
    thread.start()
    return thread


def test_stop_interrupts_utterance():
    fake = FakeBackend(words=[(5, 0, 2)], duration=5)
    engine, events = recording_engine(fake)
    thread = speak_on_thread(engine)
    fake.playing.wait(1)

    engine.stop()

    thread.join(1)
    assert not thread.is_alive()
    assert fake.stopped
    assert events == [('start', {'name': None}), ('end', {'name': None, 'completed': False})]


def test_flush_drops_queued_speak():
    fake = FakeBackend(duration=5)
    engine = onecore.OneCoreEngine(backend=fake)
    first = speak_on_thread(engine, 'first')
    fake.playing.wait(1)
    queued = speak_on_thread(engine, 'queued')
    time.sleep(0.05)

    engine.flush()

    first.join(1)
    queued.join(1)
    assert not first.is_alive() and not queued.is_alive()
    assert [text for text, _, _ in fake.synthesized] == ['first']


def test_get_voices_returns_backend_voices():
    fake = FakeBackend()
    fake.voices = lambda: [('id', 'Name')]
    engine = onecore.OneCoreEngine(backend=fake)

    assert engine.get_voices() == [('id', 'Name')]
