"""Thin WinRT adapter for :class:`Core.onecore_engine.OneCoreEngine`.

WinRT async operations are awaited with their blocking ``.get()``, which WinRT
refuses on a single-threaded apartment (the tkinter/pytest main thread). So the
WinRT work always runs on one dedicated worker thread (implicit MTA), whatever
thread calls in (GUI speak thread, MCP server thread, main thread).

Playback uses winmm ``PlaySoundW(SND_ASYNC | SND_MEMORY)`` directly: Python's
``winsound`` forbids that combo and its synchronous play can't be stopped from
another thread. The WAV buffer is kept on ``self`` while it plays.
"""
import ctypes
import struct
from concurrent.futures import ThreadPoolExecutor

from winrt.windows.media.core import SpeechCue
from winrt.windows.media.speechsynthesis import SpeechSynthesizer
from winrt.windows.storage.streams import DataReader

SND_ASYNC = 0x1
SND_MEMORY = 0x4
WAV_HEADER_BYTES = 44

_play_sound = ctypes.windll.winmm.PlaySoundW
_play_sound.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]

_MTA = ThreadPoolExecutor(max_workers=1, thread_name_prefix='onecore')


def _in_mta(fn, *args):
    return _MTA.submit(lambda: fn(*args)).result()


def wav_duration(wav):
    """Seconds of audio in a PCM WAV (byte rate lives at header offset 28)."""
    byte_rate = struct.unpack_from('<I', wav, 28)[0]
    return (len(wav) - WAV_HEADER_BYTES) / byte_rate


class OneCoreBackend:
    def __init__(self, play_sound=None):
        self._play_sound = play_sound or _play_sound
        self._playing = None
        self._synth = _in_mta(SpeechSynthesizer)
        self._synth.options.include_word_boundary_metadata = True

    def voices(self):
        return _in_mta(lambda: [(v.id, v.display_name) for v in SpeechSynthesizer.all_voices])

    def synthesize(self, text, rate, voice_id=None):
        """Return ``(wav_bytes, [(seconds, char_offset, length), ...])``."""
        return _in_mta(self._synthesize, text, rate, voice_id)

    def _synthesize(self, text, rate, voice_id):
        voice = {v.id: v for v in SpeechSynthesizer.all_voices}.get(voice_id)
        if voice is not None:
            self._synth.voice = voice
        self._synth.options.speaking_rate = rate
        stream = self._synth.synthesize_text_to_stream_async(text).get()
        reader = DataReader(stream.get_input_stream_at(0))
        reader.load_async(stream.size).get()
        wav = bytearray(stream.size)
        reader.read_bytes(wav)
        cues = [SpeechCue._from(cue) for cue in stream.timed_metadata_tracks[0].cues]
        words = [(cue.start_time.total_seconds(), cue.start_position_in_input,
                  cue.end_position_in_input - cue.start_position_in_input + 1) for cue in cues]
        return bytes(wav), words

    def play(self, wav):
        """Start playing ``wav`` without blocking; return its length in seconds."""
        self._playing = ctypes.create_string_buffer(wav, len(wav))
        self._play_sound(ctypes.addressof(self._playing), None, SND_ASYNC | SND_MEMORY)
        return wav_duration(wav)
