"""Single source of truth for the keyboard-shortcuts page (F1).

``sequences`` are the Tk bindings behind each entry, on the root window
(``"master"``) or the text box (``"text_area"``); a test checks they are really
bound so this page can't drift from the app. System-wide/mouse entries have none.
"""
from collections import namedtuple

Shortcut = namedtuple("Shortcut", "keys action sequences on")

SHORTCUTS = [
    Shortcut("Ctrl+B", "Paste the clipboard and speak it now (interrupts anything playing)",
             ("<Control-KeyRelease-b>",), "master"),
    Shortcut("Ctrl+Alt+B", "Same, from any app — even while SpeedReader is hidden in the tray", (), "master"),
    Shortcut("Ctrl+O", "Open a .txt or .md file", ("<Control-o>",), "master"),
    Shortcut("Ctrl+A", "Select all text in the text box", ("<Control-Key-a>",), "text_area"),
    Shortcut("← / →", "While speaking: rewind to the sentence start / skip to the next sentence",
             ("<Left>", "<Right>"), "text_area"),
    Shortcut("Double-click a word", "Start reading from that word", ("<Double-Button-1>",), "text_area"),
    Shortcut("F11", "Focus mode: show only the big word (again to restore)", ("<F11>",), "master"),
    Shortcut("F1", "Show this list", ("<F1>",), "master"),
    Shortcut("Close window", "Hides to the tray; use the tray icon's Quit to exit", (), "master"),
]
