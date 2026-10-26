"""Thin WinRT adapter for :class:`Core.onecore_engine.OneCoreEngine`.

WinRT async operations are awaited with their blocking ``.get()``, which WinRT
refuses on a single-threaded apartment (the tkinter/pytest main thread). So the
WinRT work always runs on one dedicated worker thread (implicit MTA), whatever
thread calls in (GUI speak thread, MCP server thread, main thread).
"""
from concurrent.futures import ThreadPoolExecutor

from winrt.windows.media.core import SpeechCue
from winrt.windows.media.speechsynthesis import SpeechSynthesizer
from winrt.windows.storage.streams import DataReader

_MTA = ThreadPoolExecutor(max_workers=1, thread_name_prefix='onecore')


def _in_mta(fn, *args):
    return _MTA.submit(lambda: fn(*args)).result()


class OneCoreBackend:
    def __init__(self):
        self._synth = _in_mta(SpeechSynthesizer)
        self._synth.options.include_word_boundary_metadata = True

    def synthesize(self, text, rate):
        """Return ``(wav_bytes, [(seconds, char_offset, length), ...])``."""
        return _in_mta(self._synthesize, text, rate)

    def _synthesize(self, text, rate):
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
