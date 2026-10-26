---
name: tts-speed-ceiling
description: Use when the user wants SpeedReader faster, says speed "stopped increasing", or the WPM spinbox seems to do nothing at high values. Explains the SAPI5 rate ceiling and the ways past it.
---

# TTS speed ceiling

## The ceiling (HIGH-RISK/REPEAT: verify before promising more speed)
- pyttsx3 2.71 `drivers/sapi5.py` maps WPM -> SAPI `Rate = int(log(wpm / a, 1.11))`, `a` ≈ 156.63 (MSMary default, used for any unknown voice e.g. Hazel/Zira/David).
- SAPI `Rate` is clamped to **-10..10**. Rate 10 is reached at **~470 WPM**. Every value above that (the spinbox goes to 1000, default 500) sounds the same.
- REPEAT: raising the spinbox max or the WPM passed to `setProperty('rate')` NEVER makes SAPI faster.
- Side effect: `time_left_text` uses the spinbox WPM, so above ~470 the estimate is too low.

Check quickly:
```pwsh
python -c "import math; print([(w, int(math.log(w/156.63,1.11))) for w in (300,400,470,500,1000)])"
```

## Ways past it
1. **OneCore voices — IMPLEMENTED, default engine** (`Core/onecore_engine.py` + `Core/onecore_backend.py`, `speech.engine` in config). Measured: SpeakingRate 1.0 ≈ 163 WPM, 6.0 ≈ 843 WPM (not linear); synthesis ~50 ms per 180 words. Traps hit while building it:
   - WinRT `.get()` on an STA thread (tkinter/pytest main) → `RuntimeError: Cannot call blocking method from single-threaded apartment`. Run WinRT on a dedicated `ThreadPoolExecutor(1)` thread.
   - `executor.submit(WinRTClass)` → `TypeError: keyword arguments not supported`; wrap in `lambda`.
   - Cues come back as `_IMediaCue`; cast with `SpeechCue._from(cue)`. `end_position_in_input` is **inclusive**.
   - Need `winrt-Windows.Foundation.Collections` too, or iterating `timed_metadata_tracks` fails with `ModuleNotFoundError`.
   - `winsound.PlaySound(None, 0)` does NOT stop a synchronous play from another thread, and `winsound` rejects `SND_ASYNC|SND_MEMORY`. Use ctypes `winmm.PlaySoundW` with both flags and keep the buffer referenced.
   - Voice IDs differ from SAPI (`...Speech_OneCore\Voices\Tokens\...`), so saved `mcp.voices` matching nothing → enable all.
2. **Synthesize then time-stretch**: SAPI at Rate 10 -> memory WAV with word-event stream offsets -> WSOLA stretch (pitch kept) -> play; scale offsets for highlighting. No upper limit, but slurs past ~2x and adds latency; synthesize per sentence.
3. **Shorter pauses** (cheap, ~10–20%): punctuation drives most of the silence at high rates. Lossy for comprehension.

HIGH-RISK/REPEAT: any new engine must keep the threading rules in AGENTS.md (no widget access off the UI thread; `callbacks.post`) and be stubbed in `testsupport/locks.py`.
