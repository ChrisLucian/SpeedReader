from Core.onecore_engine import OneCoreEngine
from Core.speech_engine import SpeechEngine


def create_speech_engine(name, on_start, on_word, on_end, make_backend=None):
    """Build the configured engine; OneCore falls back to SAPI if WinRT fails."""
    if name == 'sapi':
        return SpeechEngine(on_start, on_word, on_end)
    try:
        backend = make_backend()
    except Exception as error:
        print(f"OneCore speech unavailable ({error}); using SAPI.")
        return SpeechEngine(on_start, on_word, on_end)
    return OneCoreEngine(on_start, on_word, on_end, backend=backend)
