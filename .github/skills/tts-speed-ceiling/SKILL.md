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
1. **OneCore voices** (`Windows.Media.SpeechSynthesis`, via `winrt-*` packages): `Options.SpeakingRate` 0.5–6.0 (SAPI 10 ≈ 3x). Word boundaries come from `IncludeWordBoundaryMetadata` cues with timestamps, so highlighting must be driven by playback time, not callbacks. Needs a new engine beside `Core/speech_engine.py`; keep COM/WinRT on its own thread (same rule as SAPI).
2. **Synthesize then time-stretch**: SAPI at Rate 10 -> memory WAV with word-event stream offsets -> WSOLA stretch (pitch kept) -> play; scale offsets for highlighting. No upper limit, but slurs past ~2x and adds latency; synthesize per sentence.
3. **Shorter pauses** (cheap, ~10–20%): punctuation drives most of the silence at high rates. Lossy for comprehension.

HIGH-RISK/REPEAT: any new engine must keep the threading rules in AGENTS.md (no widget access off the UI thread; `callbacks.post`) and be stubbed in `testsupport/locks.py`.
