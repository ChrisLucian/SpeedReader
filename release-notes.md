## SpeedReader v0.9.1

### Fixed
- **Only one SpeedReader runs at a time.** Closing the window hides SpeedReader to the tray, and starting it again used to launch another copy each time: more tray icons, and several copies running in the background. Now starting it again (taskbar, Start menu, `speedreader`) brings the running window back instead.
- After updating, quit any extra copies once from their tray icons (*Quit*).

Also in v0.9: resume where you left off, the Training checkbox, and Markdown formatting is no longer read aloud.

### Install
1. `winget install ChrisLucian.SpeedReader`, or download `SpeedReader-v0.9.1-win-x64.zip` and verify it against `SpeedReader-v0.9.1-win-x64.zip.sha256`.
2. Extract and run `SpeedReader\SpeedReader.exe`.
3. A brand-new certificate may still show a SmartScreen prompt on download until it builds reputation: **More info → Run anyway**.

`pystray` (LGPL-3.0) ships as plain, replaceable source in `SpeedReader\pystray\`.
