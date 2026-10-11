"""The keyboard-shortcuts page: one table, kept honest against the real bindings."""
from Core import shortcuts


def test_shortcuts_list_covers_hidden_features():
    keys = {s.keys for s in shortcuts.SHORTCUTS}
    for expected in ("Ctrl+B", "Ctrl+Alt+B", "Ctrl+O", "F11", "← / →", "Double-click a word", "F1"):
        assert expected in keys
