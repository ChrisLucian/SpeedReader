"""Pause/Resume and read-from-a-word for MainFrame.

SAPI pause can't be driven safely across threads, so Pause stops speech and
remembers the current word; Resume speaks the rest of the text from it.
"""
import tkinter.ttk as ttk
from tkinter.constants import E


class ReadingControlsMixin:
    """Mixed into MainFrame; uses ``speech``, ``current_location``, ``speak_from``."""

    def _build_pause_button(self, row):
        self.paused_at = None
        self.pause_button = ttk.Button(self, text="Pause", width=10)
        self.pause_button.grid(row=row, column=0, sticky=E, padx=(0, 4), pady=12)

    def pause_reading(self):
        self.paused_at = self.current_location
        self.speech.stop()
        self.pause_button["text"] = "Resume"
