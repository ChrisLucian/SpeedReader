"""Route speech-engine callbacks onto the tkinter main thread.

HIGH-RISK/REPEAT: SAPI fires callbacks on its loop thread and tkinter is not
thread-safe, so engine callbacks are only queued there; the UI thread runs them
from ``pump_callbacks``.
"""


class UiPumpMixin:
    """Mixed into MainFrame; expects a ``callbacks`` CallbackQueue attribute."""

    def _queued(self, fn):
        return lambda *args: self.callbacks.post(fn, *args)

    def on_global_hotkey(self):
        """Ctrl+Alt+B from any app (hotkey thread): paste & speak on the UI thread."""
        self.callbacks.post(self.paste_and_speak, None)

    def pump_callbacks(self):
        self.callbacks.drain()
        self.after(PUMP_MS, self.pump_callbacks)


PUMP_MS = 15
