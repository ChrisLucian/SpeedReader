"""Resume where you left off: save the text + resume word, restore it at startup."""
from Core.session import save_session


class SessionMemoryMixin:
    """Mixed into MainFrame; uses ``spoken_text``, ``paused_at``, ``current_location``."""

    def remember_position(self, name, completed):
        """Called from ``onEnd`` (Pause, Stop or the end of the text).

        Agent (MCP) utterances carry no int session id and are never saved.
        """
        if isinstance(name, int):
            save_session(self.spoken_text, 0 if completed else self.paused_at)
