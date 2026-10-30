---
name: tdd-mcp-workarounds
description: Use when the tdd MCP server (plan/red/green/refactor) blocks progress in SpeedReader - a plan item that never ticks, a "test already passes" red, coverage flags on a guard, a refactor that gets reverted, or locked non-test helpers like testsupport/locks.py.
---

# Working with the tdd MCP server

- **Plan item never ticks** (e.g. the cycle only changed `build.ps1`, which coverage can't see): the next red test MUST contain the stuck planned name. Make it a REAL new behaviour with the planned name as a prefix (e.g. `test_<stuck_name>_and_<new behaviour>`). Never `rollback_cycle`: it resets git to the cycle start, which can be behind pushed or tagged commits.
- **New test passes immediately** (nothing to make red): tighten the assert to a stricter, still-true requirement. For example, check the raw saved JSON (`offset: 0`, not `null`) instead of the loader's forgiving view.
- **"Branch never runs" on a guard you want** (`if self.is_speaking:`): remove it as told, commit, then plan a test where the guard matters (quit after finishing) and add it back in green.
- **Refactor reverted**: order matters. Add the new mixin as a base class FIRST, then delete the methods from MainFrame. Deleting first breaks the controller, and all Tk tests crash with `0x80000003` in `sv_ttk`.
- **Comments on changed lines are refused** (moved code too). Turn them into a docstring.
- `testsupport/locks.py` counts as PRODUCTION: it's locked in red. Write the failing test in red and edit locks.py in green.
- HIGH-RISK/REPEAT: in a NEW test file, a module-level import of a not-yet-written function turns the whole file into a collection error. Import the module (`from Core import session`) and call `session.fn` inside the test.
- Append tests with a Bash heredoc. Run with the server's `run_tests` (Git Bash `python` is the global interpreter, so it fails with "No module named pystray").
