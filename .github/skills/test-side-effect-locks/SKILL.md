---
name: test-side-effect-locks
description: Use when adding code that touches the OS (media keys, clipboard, registry, hotkeys, tray, browser, network ports, config files, window chrome) or when a test fails with SideEffectLocked / pops a window / changes the user's clipboard or config.
---

# Locked side effects in SpeedReader tests

- HIGH-RISK/REPEAT: unit tests must NEVER press media keys, overwrite the clipboard, write the real `config.json`, show a window, register a global hotkey, create a tray icon, open a browser, or bind a port. These all happened before the lock existed.
- `testsupport/locks.py` is an autouse pytest plugin (registered via `pytest_plugins` in the ROOT `conftest.py` — not `-p`, or coverage misses it):
  - `STUBS` — harmless replacements so the app still runs (hidden window via `set_icon` → `withdraw`, no-op hotkey/tray, `MEDIA_SESSION_AVAILABLE=False`).
  - `LOCKED` — raise `SideEffectLocked` if reached (`ctypes` in chrome/media_control, mic registry scan, `webbrowser.*`, `start_http_in_thread`, `uvicorn.Server.run`, `pystray.Icon`). Dotted targets like `"Server.run"` are supported.
  - `SPEEDREADER_CONFIG` → per-test tmp file; `fake_clipboard` fixture replaces Tk's clipboard.
- HIGH-RISK/REPEAT: when you add an OS-touching API, add it to `STUBS`/`LOCKED` in the SAME change, plus a `tests/test_side_effect_lock.py` test proving it's locked.
- To test the real logic, inject the OS dependency (e.g. `GlobalHotkey(user32=FakeUser32())`, `TrayIcon(pystray=Mock())`, `authenticode_status(run=fake)`) — explicit test patches override the lock.
- Lock tests that are written BEFORE the lock really execute the side effect once (a browser tab opened). Write the lock entry first if the side effect is disruptive.
- Hidden windows: assert placement with `place_info()`/`grid_info()`, not `winfo_ismapped()`.
