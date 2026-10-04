---
name: nuitka-build-debug
description: Diagnose a SpeedReader Nuitka EXE that misbehaves (e.g. MCP server not starting). Use when the built app differs from `python SpeedReader.py`.
---

# Debugging the Nuitka build

HIGH-RISK/REPEAT: build with the venv — `.venv\Scripts\python -m nuitka`, never bare `nuitka`.
Bare `nuitka` resolves to the GLOBAL Python and bundles GLOBAL packages (unpinned `mcp` 2.x, etc).

## Steps
1. Capture the EXE's traceback (console build):
   `Start-Process SpeedReader.dist\SpeedReader.exe -WorkingDirectory . -RedirectStandardError $env:TEMP\err.txt`
   then `Test-NetConnection 127.0.0.1 -Port 8765` to check the MCP host.
2. Disabled "Restart Server" button = MCP never hosted: either `config.json` not found
   (cwd, then EXE folder) or `import mcp_server` raised.
3. Compare envs: `(Get-Command nuitka).Source`, `pip show mcp pydantic` in venv vs global.
4. Minimal repro before a full rebuild: compile a 2-line `import mcp.types` script in the
   scratchpad with `--standalone`; run it.
5. `EOFError: marshal data too short` / `Frozen object named 'encodings' is invalid` with
   no traceback = corrupt Nuitka cache. Fix: `python -m nuitka --clean-cache=all`, delete
   `SpeedReader.build`/`SpeedReader.dist`, rebuild. Never run two Nuitka builds in parallel.
6. `Can't find a usable init.tcl` = half-written dist from a build that failed (usually a
   running SpeedReader.exe locked it). Close the app, delete `SpeedReader.dist`, rebuild.
   `build.ps1` now refuses to build while the dist EXE is running.
7. REPEAT: pin majors of fast-moving deps (`mcp<2`) in `requirements.txt`.
