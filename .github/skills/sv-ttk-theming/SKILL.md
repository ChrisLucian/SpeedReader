---
name: sv-ttk-theming
description: Theme SpeedReader's tkinter UI with sv-ttk (Win11 light/dark) without colour/font glitches or flaky tests. Use when adding widgets, colours, or theme behaviour.
---

# sv-ttk theming

## HIGH-RISK/REPEAT rules
1. **Explicit roots, always.** `sv_ttk.set_theme(theme, root)` and `StringVar(master=widget)`.
   Without them tkinter uses its global default root, which in tests can be a stale `Tk`:
   `Theme sun-valley-light already exists`, or a Spinbox reading `''`.
2. **Theme first, then flush, then widgets.** `sv_ttk.set_theme(...)`; `root.update()`; build widgets.
   sv-ttk's `<<ThemeChanged>>` handler runs `tk_setPalette`, which recolours every plain tk
   widget whose colour matches the old default (white text box became `#fafafa`).
   `Accent.TButton` also only exists after the theme loads.
3. **Plain tk widgets aren't themed.** `Text`, `tk.Label` (placeholder, link) get colours from
   `Core/theme.py` `palette()`/`text_style()`; re-apply in `MainFrame._apply_theme_colors()` on toggle.
4. **Entry fonts:** because the theme loads before entries exist, set `font="SunValleyBodyFont"`
   on `ttk.Entry`/`Spinbox`/`Combobox` explicitly.
5. **Title bar:** `Frames/chrome.apply_title_bar(root, theme)` (DWM attribute 20) after toggling.
6. Fixed pixel sizes don't scale with DPI — use points (`height="135p"`).

## Verify
- REPEAT: screenshot BOTH themes (PrintWindow) — sample pixels to confirm colours.
- Run the suite 3x in the venv (`.venv\Scripts\python -m pytest -q`); theme bugs show up as flaky failures.
