"""Resume where you left off: save the text + resume word, restore it at startup."""
from Core.session import save_session


class SessionMemoryMixin:
    """Mixed into MainFrame; uses ``spoken_text``, ``paused_at``, ``current_location``."""

    def remember_position(self, name, completed):
        """Called from ``onEnd`` (Pause, Stop or the end of the text)."""
        save_session(self.spoken_text, self.paused_at)
