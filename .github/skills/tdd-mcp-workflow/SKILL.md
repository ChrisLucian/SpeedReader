---
name: tdd-mcp-workflow
description: Use when driving changes in this repo through the tdd MCP server (plan/red/green/refactor, coverage gate) — avoids the traps that cost the most time.
---

# tdd MCP server — lessons from this repo

- Needs `pytest-cov` in the venv (in `requirements-dev.txt`). Faulthandler noise in its output ≠ failure; read the summary line.
- Anything under `tests/` AND the root `conftest.py` count as TEST files (writable only in red/refactor). Test infrastructure that green code must change lives outside (`testsupport/`).
- HIGH-RISK/REPEAT: in a new test, import the module (`from tools import release`) not names (`from tools.release import x`) — a missing name breaks every test in the file and red rejects "2 tests fail".
- HIGH-RISK/REPEAT: send dependent edits ONE AT A TIME. Parallel edit calls run sequentially and each failing refactor edit is reverted on its own (e.g. a helper added after its caller).
- The plan tracks tests by NAME. If a planned test already exists/passes, reuse the planned name for a genuinely new failing case.
- Coverage gate: every production line changed in the cycle must run in a test and carry no comment. Real-OS bodies need injection (fake `run`/`user32`/`pystray`); `if __name__ == "__main__":` is excluded via `.coveragerc`. Plugins loaded with `pytest -p` load before coverage → register via `pytest_plugins` in root `conftest.py`.
- Untested branches get flagged ("simplify until only what your test needs") — write the simple version, then add the branch with its own test.
- HIGH-RISK/REPEAT: a flaky unrelated test (e.g. Tk "couldn't read file init.tcl: No error") can leave the server stuck in green or re-asking for an already-passing planned test. Fix the flake first (`return_to_red`, edit tests, commit `. t`), then add a genuinely new failing case whose name CONTAINS the planned name (`test_<planned>_and_<new_case>`).
- Lock tests for disruptive APIs (dialogs, network) assert `isinstance(api, Locked)` BEFORE calling it, so a red run never pops a dialog or hits the network.
- Commit each red as `. t` and each green as `^ f`/`^ F`/`^ b` via racn with `paths`; `return_to_red` refuses with uncommitted green edits — commit or undo first.
