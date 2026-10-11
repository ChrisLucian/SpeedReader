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


def _texts(widget):
    texts = []
    for child in widget.winfo_children():
        try:
            texts.append(child.cget("text"))
        except Exception:
            pass
        texts.extend(_texts(child))
    return texts


def test_f1_and_button_open_shortcuts(frame):
    from unittest.mock import patch
    assert "show_shortcuts" in frame.master.bind("<F1>")
    with patch("Frames.dialogs.open_shortcuts_dialog") as opener:
        frame.shortcuts_button.invoke()
        frame.show_shortcuts(None)
    assert opener.call_count == 2


def test_shortcuts_dialog_lists_every_shortcut(frame):
    from Frames import dialogs
    dialog = dialogs.open_shortcuts_dialog(frame)
    try:
        texts = _texts(dialog)
        for s in shortcuts.SHORTCUTS:
            assert s.keys in texts and s.action in texts
    finally:
        dialog.destroy()
