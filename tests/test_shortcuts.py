"""The keyboard-shortcuts page: one table, kept honest against the real bindings."""
from Core import shortcuts


def test_shortcuts_list_covers_hidden_features():
    keys = {s.keys for s in shortcuts.SHORTCUTS}
    for expected in ("Ctrl+B", "Ctrl+Alt+B", "Ctrl+O", "F11", "← / →", "Double-click a word", "F1"):
        assert expected in keys


def test_every_in_window_shortcut_is_bound(frame):
    unbound = [seq for s in shortcuts.SHORTCUTS for seq in s.sequences
               if not getattr(frame, s.on).bind(seq)]
    assert unbound == []
