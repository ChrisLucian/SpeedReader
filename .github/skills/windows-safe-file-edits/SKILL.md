---
name: windows-safe-file-edits
description: Edit repo files from Windows PowerShell 5.1 without corrupting UTF-8 (mojibake like "â€¦") or adding BOMs. Use before any scripted find/replace.
---

# Encoding-safe edits on Windows

HIGH-RISK/REPEAT: in PowerShell 5.1, `Get-Content -Raw` reads UTF-8 files as ANSI (cp1252),
and `Set-Content -Encoding utf8` writes a BOM. Round-tripping turns `…` into `â€¦` in UI text
(seen on the "Voice Settings…" button) and prepends BOMs to `.py`/`.ps1`/`requirements.txt`.

## Rules
- Prefer the Edit tool for source changes.
- If scripting, use `[IO.File]::ReadAllText(f)` / `[IO.File]::WriteAllText(f, s)` (UTF-8, no BOM),
  or a Python one-liner with `encoding="utf-8"`.
- REPEAT: never `Get-Content | Set-Content` on a file that may contain non-ASCII.
- Don't pass multi-line Python with quotes via `python -c "..."` from PowerShell 5.1 — it mangles
  embedded `"`. Write the script to the scratchpad and run `python <file>`. Bash heredocs don't work there either.

## Detect / repair
- Detect: scan for `b"\xef\xbb\xbf"` prefix and `"â€"` in touched files.
- Repair mojibake: `s.encode("cp1252").decode("utf-8")`; strip BOM unless `git show HEAD:<f>` had one.
- REPEAT: screenshot the GUI after edits — mojibake only shows at runtime.
