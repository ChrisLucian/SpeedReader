---
name: persist-ui-setting
description: Use when a SpeedReader UI choice (speed, theme, voice, window option) must be remembered across restarts via config.json. Load/save/validate recipe, the test layout and the traps.
---

# Persist a UI setting

Done twice so far: `ui.theme` ([Core/theme.py](../../../Core/theme.py)) and `ui.wpm` ([Core/config.py](../../../Core/config.py) `load_ui_wpm` / `save_ui_wpm` / `valid_wpm`).

1. **Core (GUI-free)**: `load_ui_<x>(path=None)` reads `_read_config(resolve_config_path(path))["ui"]`, and returns a default when the value is missing or invalid. `save_ui_<x>(value, path=None)` = `update_config_section("ui", {...})`. That merges, so `mcp.*` and other `ui.*` keys survive.
2. **Validate on BOTH sides**: on load, so a hand-edited or bad file gives the default. On change, so half-typed input ("6" on the way to "650") is neither saved nor applied.
   - HIGH-RISK/REPEAT: an unvalidated 0 WPM divides by zero in `time_left_text`.
3. **Frame**: seed the widget's `StringVar` and any service (`SpeakService(rate=...)`, `prime_async(...)`) from the loaded value. Save in the existing `trace_add("write", ...)` / command handler. No new mixin is needed for a 2–3 line change; MainFrame must stay < 500 lines.
4. **Tests** (`tests/test_<x>_memory.py`):
   - Core: default without a file; round-trip that keeps other keys; bad values give the default.
   - Frame: `frame.<var>.set(...)` then `load_ui_<x>()`. No path is needed: `testsupport/locks.py` already points `SPEEDREADER_CONFIG` at a tmp file.
   - Startup: `config.save_ui_<x>(...)`, stub `maybe_host_mcp`, build with the `new_controller` fixture (never `SpeedReaderController()` directly), and `destroy()` in `finally`.
5. README: name the key (`ui.<x>`) in the feature bullet.

## Traps
- HIGH-RISK/REPEAT: a module-level `from Core.config import new_fn` in the test file turns ONE red test into a collection error for the whole file (the tdd server sees "2 fail"). Import the module (`from Core import config`) and call `config.new_fn` inside the new test.
- The Git Bash `python` is the GLOBAL interpreter (no pystray/sv_ttk, so "No module named 'pystray'"). Run tests via the tdd server's `run_tests`/`advance_tdd_phase` or the venv, not `python -m pytest` in Bash.
- The tdd server refuses comments on lines changed in the cycle, including in tests. Let names explain.
