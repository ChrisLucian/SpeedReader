"""F1 / Shortcuts… button: open the keyboard-shortcuts page."""
import tkinter.ttk as ttk

from Frames import dialogs


class ShortcutsHelpMixin:
    """Mixed into MainFrame."""

    def _build_shortcuts_button(self, parent, column):
        self.shortcuts_button = ttk.Button(parent, text="Shortcuts…", command=self.show_shortcuts)
        self.shortcuts_button.grid(row=0, column=column, padx=(8, 0))

    def show_shortcuts(self, event=None):
        dialogs.open_shortcuts_dialog(self)
