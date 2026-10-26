from Core.onecore_engine import OneCoreEngine


def test_create_speech_engine_returns_onecore_engine():
    from Core.engine_factory import create_speech_engine

    engine = create_speech_engine('onecore', None, None, None, make_backend=object)

    assert isinstance(engine, OneCoreEngine)
