---
name: record-ui-demo
description: Use when asked for a video/GIF of SpeedReader working, or to verify UI behaviour the mocked unit tests can't see (live word highlighting) — launch the built EXE, drive it, capture the window, encode with ffmpeg.
---

# Recording a SpeedReader demo video

1. Build first (`build.ps1`). HIGH-RISK/REPEAT: in PowerShell 5.1 never `*>`-redirect `build.ps1` — with `$ErrorActionPreference = Stop`, Nuitka's stderr becomes a fatal NativeCommandError. Run it via `powershell -Command "& .\build.ps1"` and redirect from the OUTER shell. A running `SpeedReader.exe` from `SpeedReader.dist` blocks the build.
2. Recorder (venv Python + Pillow): `SetProcessDpiAwareness(2)` → launch EXE → `FindWindowW(None, "Speed Reader")` → `SetForegroundWindow` → clipboard via `Set-Clipboard` → `Ctrl+Alt+B` with `keybd_event` (system-wide paste & speak, no clicking) → `ImageGrab.grab(bbox=GetWindowRect, all_screens=True)` at 10 fps → `proc.terminate()`.
3. A paragraph at 500 WPM lasts ~6 s; afterwards other windows may cover the app — trim to frames whose title-bar crop matches a known-good frame.
4. Encode: `ffmpeg -framerate 10 -i f%04d.png -frames:v N -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -pix_fmt yuv420p -movflags +faststart out.mp4` (ffmpeg from winget `Gyan.FFmpeg`).
5. Deliver: `SendUserFile` the mp4 and/or an HTML artifact with a `data:video/mp4;base64,…` `<video>` (under 16 MB). REPEAT: read a few frames yourself first to confirm what the video shows.
- No audio is captured, but the app WILL speak on the user's speakers while recording.

## Narrated product tour WITH audio (YouTube)
- There is no loopback audio device here: dshow lists no "Stereo Mix" and ffmpeg can't capture system audio. Instead capture the audio INSIDE the app. `tour/tour.py` monkeypatches `Core.onecore_backend.OneCoreBackend.play`/`stop` to save every WAV SpeedReader plays, with its `time.perf_counter()` start and stop times.
- `tour/rec.py` (a separate process) grabs the window at 15 fps, stamped with the same perf_counter clock (QPC is system-wide), so audio and video line up exactly. Use the DWM `DWMWA_EXTENDED_FRAME_BOUNDS` (9) bbox, not `GetWindowRect`: the latter adds invisible borders, which capture the window behind.
- `tour/tour.py` drives the app in-process through its own methods (`speak`, `pause_reading`, `toggle_focus`, `toggle_theme`, `read_from_index`, `dialogs.open_shortcuts_dialog`), not mouse clicks. Each segment is narrated by SpeedReader itself. It uses a temp `SPEEDREADER_CONFIG`/`SPEEDREADER_SESSION` (MCP off), so the user's running copy and settings are untouched.
- `tour/make.py` rebuilds the narration track (each clip cut at the next play/stop), builds the frame list with real durations (ffmpeg concat), and renders 1920x1080 with a caption bar per segment (drawtext + textfile; fonts and texts copied into the run folder so filter paths need no colon escaping).
- Run (about 2.5 min, it speaks aloud): `.venv\Scripts\python.exe tour.py <out>`, wait for `<out>\log.json`, kill the leftover python processes, then `python make.py <out> <mp4>`.
- Narration at 230 WPM; 300+ is too fast for viewers. The speed segment steps the spinbox to 475: make sure the range really ends there (`range(250, 476, 25)`).
- Before delivering, review a contact sheet of one still per segment (`ffmpeg -ss <t> ... -vf tile=3x4`).

