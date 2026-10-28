## SpeedReader v0.8.1

### New
- **Remembers your speed** — the WPM you set in the Speed box is saved to `config.json` (`ui.wpm`) and restored the next time you start SpeedReader.

### Fixed
- **SpeedReader now starts from any folder.** v0.8 quit silently, with no window, when it was unzipped somewhere it couldn't write files (e.g. `Program Files`, or Documents/Desktop under Windows Controlled Folder Access). Logs now go to `%TEMP%\SpeedReader.err.txt`.
- Typing a speed no longer applies half-typed values (e.g. 6 WPM on the way to 650); speeds outside 100–1000 are ignored.

### Install
1. `winget install ChrisLucian.SpeedReader`, or download `SpeedReader-v0.8.1-win-x64.zip` and verify it against `SpeedReader-v0.8.1-win-x64.zip.sha256`.
2. Extract and run `SpeedReader\SpeedReader.exe`.
3. A brand-new certificate may still show a SmartScreen prompt on download until it builds reputation: **More info → Run anyway**.

`pystray` (LGPL-3.0) ships as plain, replaceable source in `SpeedReader\pystray\`.
