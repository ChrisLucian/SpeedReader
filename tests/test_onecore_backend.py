"""Real WinRT synthesis (no audio is played): checks our cue/offset mapping."""
from Core.onecore_backend import OneCoreBackend


def test_backend_synthesize_returns_wav_and_word_offsets():
    wav, words = OneCoreBackend().synthesize('hello world', 1.0)

    assert wav[:4] == b'RIFF'
    assert [(location, length) for _, location, length in words] == [(0, 5), (6, 5)]
    assert words[0][0] < words[1][0]


def test_backend_synthesize_uses_requested_voice():
    backend = OneCoreBackend()
    voice_id, _ = backend.voices()[-1]

    backend.synthesize('hi', 1.0, voice_id)

    assert backend._synth.voice.id == voice_id
