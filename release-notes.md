## SpeedReader v0.6

First downloadable release: a **signed** Windows build (Azure Artifact Signing, publisher *Christopher Lucian*), so Windows Smart App Control lets it run.

### New
- **Ctrl+Alt+B anywhere** — reads the clipboard aloud from any app (system-wide hotkey).
- **System tray icon** — Show / Read clipboard / Quit. Closing the window hides it to the tray so agents can keep speaking; use **Quit** in the tray to exit.
- **Pause / Resume** — pause mid-text and pick up at the same word.
- **Double-click a word** to start reading from there.
- **← / → sentence rewind/skip** while speaking, and a **time left** readout.
- **Open files** — `Ctrl+O` for `.txt`/`.md`, or drop a file onto `SpeedReader.exe`.
- **F11 focus mode** — just the big word.
- **Shortcuts page** — press `F1` (or *Shortcuts…*) to see every keyboard shortcut.
- **Update check** — the title tells you when a newer release is on GitHub.
- **MCP `stop_speaking` and `speech_status` tools** for agents.
- **Smarter reading** — links, file paths, emails, GUIDs, hashes, code blocks and very long tokens are spoken as `[URL]`, `[file path]`, `[email]`, `[ID]`, `[hash]`, `[code]`, `[long text]` instead of being spelled out.
- **MCP server** for AI agents (per-agent voices, pauses while you're on a call), modern light/dark UI.

### Fixed
- Crash when reading a pasted file path (speech callbacks now run on the UI thread).

### Install
1. Download `SpeedReader-v0.6-win-x64.zip` and verify it against `SpeedReader-v0.6-win-x64.zip.sha256`.
2. Extract and run `SpeedReader\SpeedReader.exe`.
3. A brand-new certificate may still show a SmartScreen prompt on download until it builds reputation: **More info → Run anyway**.

`pystray` (LGPL-3.0) ships as plain, replaceable source in `SpeedReader\pystray\`.
