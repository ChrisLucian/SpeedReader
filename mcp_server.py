"""Locally hosted MCP server exposing SpeedReader's text-to-speech.

The agent spawns it over **stdio** (``python mcp_server.py``), so it is up
whenever the agent is, with or without the GUI running. It reuses the GUI-free
logic in ``Core`` and speaks at the ``ui.wpm`` the GUI last saved, re-read on
every call, so agent speech matches the speed the user has set.
"""
from mcp.server.fastmcp import FastMCP

from Core.call_detection import microphone_in_use
import logging
from Core.config import load_mcp_config, load_ui_wpm
from Core.speak_service import SpeakService
from Core.voice_registry import VoiceRegistry


def build_mcp(service=None, registry=None, host="127.0.0.1", port=8765,
              pause_when_mic_in_use=False, call_active=None):
    """Build a FastMCP server whose tools delegate to ``service``/``registry``.

    When ``pause_when_mic_in_use`` is true, the ``speak`` tool skips speaking
    while a call is detected (``call_active()`` — microphone in use by default)
    and returns a message instead, so agent speech never talks over the user.
    """
    service = service or SpeakService()
    registry = registry if registry is not None else VoiceRegistry()
    call_active = call_active or microphone_in_use
    server = FastMCP("SpeedReader", host=host, port=port)

    @server.tool()
    def list_voices() -> list:
        """List the voices the user has enabled for agents, with claim status.

        Returns a list of ``{id, name, claimed_by}`` so you can pick an unused
        voice to claim. ``claimed_by`` lists the agents currently using it.
        """
        return registry.status()

    @server.tool()
    def claim_voice(agent: str | None = None, voice: str | None = None) -> dict:
        """Claim a voice to speak with.

        While unused voices remain you may claim one (optionally requesting a
        specific ``voice`` by name or id); each is exclusive. Once every enabled
        voice is taken, you must pass an ``agent`` label to share one — use a
        stable identifier such as the repo folder name or your current task.

        Args:
            agent: Your identity (repo folder name or current task). Required to
                share a voice after all voices are claimed.
            voice: Optional specific voice (name or id) to request.

        Returns:
            ``{id, name, agent, shared, reused}`` for the claimed voice. Pass the
            same ``agent`` (or the returned voice) to ``speak``.
        """
        return registry.claim(agent=agent, voice=voice)

    @server.tool()
    def release_voice(agent: str) -> str:
        """Release the voice claimed by ``agent`` so others can use it."""
        released = registry.release(agent)
        return "Released voice for %s." % agent if released else "No voice was claimed by %s." % agent

    @server.tool()
    def speak(text: str, agent: str | None = None, voice: str | None = None,
              rate: int | None = None) -> str:
        """Read text aloud on the host machine using the local TTS voice.

        Reserve a voice first: call ``claim_voice(agent="<your repo folder or
        current task>")`` once, then pass that same ``agent`` here. Speaking
        without a reserved ``agent`` (or an explicit ``voice``) is an error when
        more than one voice is enabled.

        Args:
            text: The text to speak. Newlines are collapsed to spaces and URLs
                are replaced with a ``[URL]`` placeholder before speaking.
            agent: Your identity; resolves to the voice you reserved with
                ``claim_voice``.
            voice: Optional specific voice (name or id) to speak with, overriding
                the reservation.
            rate: Words per minute. Omit to use the rate set in the UI.

        Returns:
            A short confirmation of what was spoken.
        """
        # If an agent calls the speak tool, we assume they want to speak regardless of mic status.
        if pause_when_mic_in_use and call_active() and agent is None:
            return "Skipped: a call is in progress (microphone in use); speech was not played."
        chosen = registry.resolve_for_speak(agent=agent, voice=voice)
        logging.info(f"MCP Speak Tool called with text: '{text}'")
        used = service.speak(text, rate, voice=chosen)
        return "Spoke {} characters at {} WPM.".format(len(text), used)

    @server.tool()
    def stop_speaking() -> str:
        """Stop whatever SpeedReader is saying right now (yours or anyone's)."""
        service.stop()
        return "Stopped."

    @server.tool()
    def speech_status() -> dict:
        """``{speaking, pending}``: is agent speech playing, and how many speak calls are in flight."""
        return service.status()

    return server, service, registry


def build_stdio(load_voices, speak_fn=None):
    """The agent-spawned stdio server: config voices, and the GUI's saved speed per call."""
    cfg = load_mcp_config()
    voices = load_voices()
    enabled = [(vid, name) for vid, name in voices if vid in cfg.voices] or voices
    service = SpeakService(rate_source=load_ui_wpm, speak_fn=speak_fn)
    return build_mcp(service, VoiceRegistry(enabled=enabled),
                     pause_when_mic_in_use=cfg.pause_when_mic_in_use)


# Module-level server for the standalone stdio path (and import smoke tests).
mcp, _service, _registry = build_mcp(pause_when_mic_in_use=load_mcp_config().pause_when_mic_in_use)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
