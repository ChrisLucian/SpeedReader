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
