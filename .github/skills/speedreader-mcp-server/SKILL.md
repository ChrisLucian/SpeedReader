---
name: speedreader-mcp-server
description: 'Use when adding, changing, running, registering or debugging the SpeedReader MCP server (mcp_server.py) or its tools. Covers the stdio-only model (agent spawns the server), build_stdio (config voices + the GUI saved ui.wpm per call), the speak/claim tool contract, .mcp.json / .vscode/mcp.json registration, the stdout-is-the-protocol trap, and testing without audio.'
---

# SpeedReader MCP server (stdio)

[mcp_server.py](../../../mcp_server.py) lets agents read text aloud on the host.

## Transport: stdio ONLY (HIGH-RISK / REPEAT)
- The agent spawns `python mcp_server.py`; `main()` -> `build_stdio(...)` -> `server.run("stdio")`. It is up whenever the agent is — the GUI does NOT need to run.
- The GUI no longer hosts MCP (no HTTP, no uvicorn thread, no Server… dialog, no `mcp.enabled/host/port`). REPEAT: do not re-add GUI hosting; it made every agent's MCP fail with ECONNREFUSED whenever the app was closed.
- REPEAT: **stdout IS the JSON-RPC channel.** Never `print()` in code the server runs (Core/speech, voice listing, config). Log to stderr (`logging`).
- The built EXE can't serve stdio (Nuitka forces stdout to `{TEMP}\SpeedReader.out.txt`). Agents run the server from a Python checkout/venv.
- An MCP client's minimal Windows env breaks SAPI (`Voice.Id` -> com_error). Claude Code / VS Code pass the full env; the Python SDK `stdio_client` does NOT unless you pass `env=dict(os.environ)`.

## build_stdio (what each spawned process gets)
- Voices: `Core.speech.sapi_voices(pyttsx3.init)` filtered by `config.json` `mcp.voices` (none listed/matching = all).
- Speed: `SpeakService(rate_source=load_ui_wpm)` re-reads the GUI's saved `ui.wpm` on EVERY speak, so a speed change in the app applies to the next agent sentence. REPEAT: `speak`'s `rate=None` means "saved UI speed" — never hard-code a WPM.
- Speech: `Core.speech.speak_blocking` (fresh SAPI engine + `runAndWait()` per call, on the calling thread — COM same-thread rule holds). SAPI tops out ~470 WPM.
- `mcp.pause_when_mic_in_use` gates `speak` (skips, returns a message) via `build_mcp(pause_when_mic_in_use, call_active)`.
- Each agent process has its OWN `VoiceRegistry`: claims are per process, not shared across agents, and the GUI user's voice isn't reserved. Two agents may speak at once.

## Tool contract
- `speak(text, agent=None, voice=None, rate=None)`; `list_voices()`; `claim_voice(agent=None, voice=None)`; `release_voice(agent)`; `stop_speaking()`; `speech_status()`.
- REPEAT: with >1 enabled voice and no reserved `agent`/explicit `voice`, `speak` raises and tells the agent to `claim_voice` first.
- FastMCP builds the schema from type hints + docstrings — keep them.

## Registration
- Claude Code: repo [.mcp.json](../../../.mcp.json) `speedreader` = `{"command": "${CLAUDE_PROJECT_DIR:-.}/.venv/Scripts/python.exe", "args": ["${CLAUDE_PROJECT_DIR:-.}/mcp_server.py"]}`.
- VS Code: `.vscode/mcp.json` (git-ignored) `servers.speedreader` = `{"type": "stdio", "command": "${workspaceFolder}/.venv/Scripts/python.exe", "args": ["${workspaceFolder}/mcp_server.py"]}`.

## Testing
- Unit: inject `load_voices`/`speak_fn` into `build_stdio`, `init` into `sapi_voices`, `build` into `main` ([tests/test_mcp_stdio.py](../../../tests/test_mcp_stdio.py)). Never real audio in pytest.
- Real smoke (speaks one line): an SDK client — `StdioServerParameters(command=<venv python>, args=["mcp_server.py"], env=dict(os.environ), cwd=<repo>)`, `initialize`, `list_tools`, `claim_voice`, `speak`.
