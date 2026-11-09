"""The stdio MCP server: voices from config, speed from the GUI's saved ui.wpm."""
import json
import os
from unittest.mock import MagicMock

import mcp_server


def test_build_stdio_enables_configured_voices_at_saved_wpm():
    with open(os.environ["SPEEDREADER_CONFIG"], "w", encoding="utf-8") as handle:
        json.dump({"mcp": {"voices": ["v2"]}, "ui": {"wpm": 640}}, handle)

    _, service, registry = mcp_server.build_stdio(
        load_voices=lambda: [("v1", "One"), ("v2", "Two")], speak_fn=MagicMock())

    assert registry.enabled() == [("v2", "Two")]
    assert service.speak("hi") == 640
