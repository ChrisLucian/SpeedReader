"""Resume where you left off: save the text + resume word, restore it at startup."""
from Core.session import load_session, save_session


class SessionMemoryMixin:
    """Mixed into MainFrame; uses ``spoken_text``, ``paused_at``, ``current_location``."""

    def restore_session(self):
        """Startup: put last session's text back in the text area."""
        saved = load_session()
        if saved:
            text, offset = saved
            self.text_area.insert("end", text)

    def remember_position(self, name, completed):
        """Called from ``onEnd`` (Pause, Stop or the end of the text).

        Agent (MCP) utterances carry no int session id and are never saved.
        """
        if isinstance(name, int):
            self._save_position(0 if completed else self.paused_at)

    def remember_on_quit(self):
        """Quit while reading: save the current word (Pause/Stop/end already saved)."""
        self._save_position(self.current_location)

    def _save_position(self, offset):
        """Save the text area; ``offset`` only applies while it still holds the spoken text."""
        text = self.text_area.get("1.0", "end-1c")
        save_session(text, offset if text == self.spoken_text else 0)
