## SpeedReader v0.7

### New
- **Much faster speech (up to ~840 WPM)** — the new default engine uses the Windows OneCore voices, which go well past the old ~470 WPM limit of the SAPI voices.
- To go back to the old engine, set `"speech": {"engine": "sapi"}` in `config.json`. If the OneCore voices aren't available, SpeedReader switches to SAPI by itself.

### Install
1. `winget install ChrisLucian.SpeedReader`, or download `SpeedReader-v0.7-win-x64.zip` and verify it against `SpeedReader-v0.7-win-x64.zip.sha256`.
2. Extract and run `SpeedReader\SpeedReader.exe`.
3. A brand-new certificate may still show a SmartScreen prompt on download until it builds reputation: **More info → Run anyway**.

`pystray` (LGPL-3.0) ships as plain, replaceable source in `SpeedReader\pystray\`.
