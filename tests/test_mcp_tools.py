"""MCP stop/status tools, driven against a mocked SpeakService."""
import asyncio
from unittest.mock import MagicMock

import mcp_server


def _call(service, tool):
    server, _, _ = mcp_server.build_mcp(service, registry=MagicMock())
    return asyncio.run(server.call_tool(tool, {}))


def test_mcp_stop_tool_stops_service():
    service = MagicMock()
    _call(service, "stop_speaking")
    service.stop.assert_called_once_with()
