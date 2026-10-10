"""Pause/Resume and read-from-a-word for MainFrame.

SAPI pause can't be driven safely across threads, so Pause stops speech and
remembers the current word; Resume speaks the rest of the text from it.
"""
import tkinter.ttk as ttk
from tkinter.constants import E

from Core.reading_position import word_start


class ReadingControlsMixin:
    """Mixed into MainFrame; uses ``speech``, ``current_location``, ``speak_from``."""

    def _build_pause_button(self, row):
        self.paused_at = None
        self.pause_button = ttk.Button(self, text="Pause", width=10, command=self.toggle_pause)
        self.pause_button.grid(row=row, column=0, sticky=E, padx=(0, 4), pady=12)
        self.text_area.bind("<Double-Button-1>", self.on_text_double_click)

    def on_text_double_click(self, event):
        self.read_from_index("@{},{}".format(event.x, event.y))
        return "break"

    def toggle_pause(self):
        if self.paused_at is not None:
            self.resume_reading()
        else:
            self.pause_reading()

    def pause_reading(self):
        self.paused_at = self.current_location
        self.speech.stop()
        self.pause_button["text"] = "Resume"

    def resume_reading(self):
        offset, self.paused_at = self.paused_at, None
        self.pause_button["text"] = "Pause"
        self.speak_from(offset)

    def read_from_index(self, index):
        self.spoken_text = self.text_area.get("1.0", "end-1c")
        clicked = len(self.text_area.get("1.0", index))
        self.speak_from(word_start(self.spoken_text, clicked), interrupt=True)
