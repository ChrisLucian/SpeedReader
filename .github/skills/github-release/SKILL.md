---
name: github-release
description: Use when cutting a SpeedReader GitHub release or winget submission (version bump, signed zip, checksum, release notes, gh release create).
---

# Releasing SpeedReader

1. Merge to `master` and push (agents never push to master themselves — the user does/approves).
2. Signed build: set `ARTIFACT_SIGNING_*` (user env), `az login --tenant <tenant> --scope "https://codesigning.azure.net/.default"`, run `.\build.ps1` (see `windows-code-signing` skill).
3. HIGH-RISK/REPEAT: smoke-run `SpeedReader.dist\SpeedReader.exe` ~10 s and check `SpeedReader.err.txt` is clean before releasing — a green build can still crash at start (e.g. Nuitka "actively excluded" pystray).
4. Update `release-notes.md` for the version.
5. Package: `python -m tools.release vX.Y` → `release\SpeedReader-vX.Y-win-x64.zip`, `.sha256`, `release\winget\*.yaml`. It refuses unsigned builds and drops the local `*.err.txt`/`*.out.txt` logs.
6. HIGH-RISK/REPEAT: publishing is public — get the user's explicit go-ahead, then `python -m tools.release vX.Y --publish` (needs `gh auth login`).
7. winget: copy `release\winget\*.yaml` to `manifests/c/ChrisLucian/SpeedReader/X.Y/` in a winget-pkgs fork and open a PR (or `wingetcreate submit`). Validate with `winget validate`.
- First-time downloads of a new certificate may still hit SmartScreen until reputation builds; Smart App Control accepts the CA-signed build.
