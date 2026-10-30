"""Speed training checkbox: each finished reading adds 25 WPM (up to 500)."""
import tkinter.ttk as ttk
from tkinter import BooleanVar
from tkinter.constants import W

from Core.speed_training import TRAINING_GOAL, TRAINING_STEP, next_training_wpm


class SpeedTrainingMixin:
    """Mixed into MainFrame; uses ``speed_var`` and ``speak_service``."""

    def _build_training_toggle(self, parent):
        self.training_var = BooleanVar(master=self, value=False)
        self.training_check = ttk.Checkbutton(
            parent, variable=self.training_var,
            text="Training: +{} WPM after each finished reading (up to {})".format(TRAINING_STEP, TRAINING_GOAL))
        self.training_check.grid(row=1, column=0, columnspan=5, sticky=W, pady=(8, 0))

    def train_after_reading(self, name, completed):
        """Called from ``onEnd``."""
        if self.training_var.get():
            self.speed_var.set(str(next_training_wpm(self.speak_service.rate)))
