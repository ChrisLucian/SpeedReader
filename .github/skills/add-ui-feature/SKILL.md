---
name: add-ui-feature
description: Use when adding a SpeedReader UI feature or shortcut (key binding, panel, file/OS interaction) — the TDD-friendly path from Core helper to mixin to docs without blowing the 500-line gate.
---

# Adding a UI feature to SpeedReader

1. **Core first** — pure logic (parsing, timing, positions, file decoding) in `Core/<topic>.py`, unit-tested with plain values. No tkinter imports.
2. **Mixin, not MainFrame** — HIGH-RISK/REPEAT: `Frames/MainFrame.py` is ~490 lines. New behaviour goes in `Frames/<feature>.py` as `<Feature>Mixin`, added to `class MainFrame(...)` bases. MainFrame only gets the one-line `self.master.bind(...)` next to the other binds.
3. **Test through the `frame` fixture** — call the handler directly (`frame.on_open_file(None)`), assert widget state (`grid_info()`, `["text"]`, `text_area.get`). Assert the binding exists with `frame.master.bind("<Key>")`.
4. **OS touch = lock** — dialogs, network, registry, clipboard, hotkeys: add to `testsupport/locks.py` `LOCKED`/`STUBS` in the SAME change, plus an `isinstance(..., Locked)`-first lock test (see `test-side-effect-locks`). Resolve the API at call time so the lock applies.
5. **Threads** — anything from a non-UI thread posts via `main_frame.callbacks.post(...)`; never touch widgets off the UI thread.
6. **Docs** — README *Controls* (or MCP tools list), `release-notes.md`, AGENTS.md architecture list. REPEAT: not done until README reflects it.
7. **Verify by hand** — `python SpeedReader.py`, exercise the shortcut while speaking and idle.
