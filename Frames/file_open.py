"""Open .txt/.md files into MainFrame's text area."""
from Core.text_file import read_text_file


class FileOpenMixin:
    """Mixed into MainFrame; uses ``text_area``."""

    def open_file(self, path):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", read_text_file(path))
