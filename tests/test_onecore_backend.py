"""Real WinRT synthesis (no audio is played): checks our cue/offset mapping."""
import io
import wave

from Core.onecore_backend import SND_ASYNC, SND_MEMORY, OneCoreBackend


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


def two_second_wav():
    out = io.BytesIO()
    with wave.open(out, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b'\0' * 64000)
    return out.getvalue()


def recording_backend():
    calls = []
    return OneCoreBackend(play_sound=lambda *args: calls.append(args)), calls


def test_backend_play_starts_async_memory_sound_and_returns_duration():
    backend, calls = recording_backend()

    duration = backend.play(two_second_wav())

    assert duration == 2.0
    assert calls[0][2] == SND_ASYNC | SND_MEMORY


def test_backend_stop_silences_sound():
    backend, calls = recording_backend()

    backend.stop()

    assert calls == [(None, None, 0)]
