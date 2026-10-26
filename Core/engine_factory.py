from Core.onecore_engine import OneCoreEngine


def create_speech_engine(name, on_start, on_word, on_end, make_backend=None):
    return OneCoreEngine(on_start, on_word, on_end, backend=make_backend())
