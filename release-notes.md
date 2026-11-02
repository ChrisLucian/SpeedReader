## SpeedReader v0.9.2

### Fixed
- **SpeedReader now starts on PCs without AVX-512** (for example Intel Core Ultra laptops). Earlier builds closed immediately on those CPUs ("illegal instruction"), because part of the program was built for the build PC's newer processor. It is now built for any 64-bit x86 CPU, and the build fails if that ever slips again.

Also in v0.9.x: only one SpeedReader runs at a time, resume where you left off, the Training checkbox, and Markdown formatting is no longer read aloud.

### Install
1. `winget install ChrisLucian.SpeedReader`, or download `SpeedReader-v0.9.2-win-x64.zip` and verify it against `SpeedReader-v0.9.2-win-x64.zip.sha256`.
2. Extract and run `SpeedReader\SpeedReader.exe`.
3. A brand-new certificate may still show a SmartScreen prompt on download until it builds reputation: **More info → Run anyway**.

`pystray` (LGPL-3.0) ships as plain, replaceable source in `SpeedReader\pystray\`.
