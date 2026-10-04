import json
import os

from Core.config import resolve_config_path, update_config_section

THEMES = ("dark", "light")

# Colours for widgets sv-ttk does not style (tk.Text, placeholder, link).
# "window" mirrors sv-ttk's own background so tk widgets blend in.
_PALETTES = {
    "dark": {"window": "#1c1c1c", "background": "#2b2b2b", "foreground": "#fafafa", "border": "#3a3a3a",
             "highlight": "#ff6b6b", "placeholder": "#8a8a8a", "link": "#57c8ff"},
    "light": {"window": "#fafafa", "background": "#ffffff", "foreground": "#1c1c1c", "border": "#d0d0d0",
              "highlight": "#d00000", "placeholder": "#8a8a8a", "link": "#005fb8"},
}
_ACCENT = "#57c8ff"  # sv-ttk focus accent, used for the focused Text border


def load_ui_theme(path=None):
    """Return the ``ui.theme`` from config ("dark" or "light"); defaults to dark."""
    path = resolve_config_path(path)
    theme = None
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            theme = (json.load(handle) or {}).get("ui", {}).get("theme")
    return theme if theme in THEMES else "dark"


def save_ui_theme(theme, path=None):
    """Persist ``ui.theme`` so the in-app toggle survives restarts."""
    return update_config_section("ui", {"theme": theme}, path=path)


def toggled(theme):
    """The other theme: dark <-> light."""
    return "light" if theme == "dark" else "dark"


def palette(theme):
    """Named colours for ``theme``."""
    return dict(_PALETTES[theme])


def text_style(theme):
    """``tk.Text.configure`` options for ``theme``."""
    colors = _PALETTES[theme]
    return {
        "background": colors["background"],
        "foreground": colors["foreground"],
        "insertbackground": colors["foreground"],
        "highlightbackground": colors["border"],
        "highlightcolor": _ACCENT,
        "highlightthickness": 1,
    }
