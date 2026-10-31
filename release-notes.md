## SpeedReader v0.9

### New
- **Resume where you left off** — the text and the word you stopped at (Pause, Stop, finishing, or quitting mid-read) are saved to `%LOCALAPPDATA%\SpeedReader\session.json`. Next launch the text is back and **Resume** continues from that word (**Speak** starts over). Agent speech never replaces your saved reading.
- **Training** checkbox (under Speed) — every reading you finish adds 25 WPM, up to 500. Stopped or paused readings don't count. Saved to `config.json` as `ui.train`.
- **Markdown is read as plain words** — when text (yours or an AI agent's) looks like Markdown, `#` headings, `**bold**`/`*italic*`, backticks, list bullets, `>` quotes, table pipes and link URLs are no longer read aloud. Links read their text, images their alt text; plain text like `5 * 3` or `snake_case` is untouched.

### Fixed
- Opening a file (`Ctrl+O` or drag onto the EXE) no longer leaves an old Resume point that would read the previous text.

### Install
1. `winget install ChrisLucian.SpeedReader`, or download `SpeedReader-v0.9-win-x64.zip` and verify it against `SpeedReader-v0.9-win-x64.zip.sha256`.
2. Extract and run `SpeedReader\SpeedReader.exe`.
3. A brand-new certificate may still show a SmartScreen prompt on download until it builds reputation: **More info → Run anyway**.

`pystray` (LGPL-3.0) ships as plain, replaceable source in `SpeedReader\pystray\`.
