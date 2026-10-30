"""MCP agent speech for MainFrame: show the agent's text, speak it on the server thread."""
from tkinter.constants import END


class AgentSpeechMixin:
    """Mixed into MainFrame; uses ``callbacks``, ``speech``, ``text_area``."""

    def speak_external(self, text, rate, voice=None):
        # Entry point for MCP agent speech (called from the server thread).
        # Update the UI on the tkinter main thread, but run the BLOCKING speak on
        # this server thread (never inside `after`, which would freeze the UI).
        # Blocking serializes per-utterance voices so agents don't bleed voices.
        self.callbacks.post(self._render_external, text)
        self.speech.speak(text, rate, voice=voice, block=True)

    def _render_external(self, text):
        self.spoken_text = text
        self.speak_offset = 0
        self.text_area.delete("1.0", END)
        self.text_area.insert(END, text)
