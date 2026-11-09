---
name: mcp-stdio-smoke
description: Use after changing mcp_server.py, Core/speech.py, config loading or anything the stdio MCP server imports, or when an agent says the speedreader MCP "failed to connect". Spawns the real server over stdio with the MCP SDK client and calls list_tools, list_voices, claim_voice and speak (speaks one short line).
---

# Smoke-test the stdio MCP server

```pwsh
.\.venv\Scripts\python.exe .github\skills\mcp-stdio-smoke\smoke.py
```

Pass = tools listed, a voice claimed, `Spoke 12 characters at <ui.wpm> WPM.`

Then confirm Claude Code's registration: `claude mcp list` → `speedreader: … ✔ Connected`.

## Traps (HIGH-RISK / REPEAT)
- `McpError: Connection closed` right after `initialize` = the server process died. Read its stderr in the client output (the traceback is printed above the ExceptionGroup).
- The SDK's `stdio_client` passes a MINIMAL Windows environment by default. SAPI then fails in `pyttsx3.init()` (`Voice.Id` com_error -2147200966). Always pass `env=dict(os.environ)` (smoke.py does). Claude Code / VS Code pass the full env, so this is a test-harness trap, not a product bug.
- stdout is the JSON-RPC channel: any `print()` on the server path corrupts the session. `echo '' | python mcp_server.py` must answer with JSON only (a parse-error notification is fine).
- A running Claude Code session keeps the MCP config it started with. After changing `.mcp.json`, use `/mcp` → reconnect (or restart the session).
