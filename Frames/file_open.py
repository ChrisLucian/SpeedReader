"""Open .txt/.md files into MainFrame's text area (Ctrl+O)."""
from tkinter import filedialog

from Core.text_file import read_text_file

FILE_TYPES = [("Text files", "*.txt *.md"), ("All files", "*.*")]


class FileOpenMixin:
    """Mixed into MainFrame; uses ``text_area``, ``force_stop_and_reset``, ``clear_display_labels``."""

    def on_open_file(self, event):
        path = filedialog.askopenfilename(parent=self, filetypes=FILE_TYPES)
        self.open_file(path)
        return "break"

    def open_file(self, path):
        self.force_stop_and_reset()
        self.clear_display_labels()
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", read_text_file(path))
