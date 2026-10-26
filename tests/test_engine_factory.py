from Core.onecore_engine import OneCoreEngine
from Core.speech_engine import SpeechEngine


def test_create_speech_engine_returns_onecore_engine():
    from Core.engine_factory import create_speech_engine

    engine = create_speech_engine('onecore', None, None, None, make_backend=object)

    assert isinstance(engine, OneCoreEngine)


def test_create_speech_engine_falls_back_to_sapi_when_onecore_unavailable():
    from Core.engine_factory import create_speech_engine

    def unavailable():
        raise ImportError('no winrt')

    engine = create_speech_engine('onecore', None, None, None, make_backend=unavailable)

    assert isinstance(engine, SpeechEngine)
