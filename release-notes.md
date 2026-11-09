## SpeedReader v0.10.0

### Changed
- **AI agents now start SpeedReader's voice server themselves (MCP over stdio).** Agents no longer need the SpeedReader window open, and they no longer fail with "connection refused" when it is closed. Agent speech still follows the speed you last set in the app.
- The **Server…** button and the `mcp.enabled` / `host` / `port` settings are gone; nothing listens on a network port any more. To let an agent speak, register `mcp_server.py` from a Python checkout (see the README's *MCP server* section). The EXE itself can't serve stdio.

### Install
1. `winget install ChrisLucian.SpeedReader`, or download `SpeedReader-v0.10.0-win-x64.zip` and verify it against `SpeedReader-v0.10.0-win-x64.zip.sha256`.
2. Extract and run `SpeedReader\SpeedReader.exe`.
3. A brand-new certificate may still show a SmartScreen prompt on download until it builds reputation: **More info → Run anyway**.

`pystray` (LGPL-3.0) ships as plain, replaceable source in `SpeedReader\pystray\`.
