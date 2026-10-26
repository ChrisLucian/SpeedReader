---
name: github-release
description: Use when cutting a SpeedReader GitHub release or winget submission (version bump, signed zip, checksum, release notes, gh release create).
---

# Releasing SpeedReader

1. Merge to `master` and push (agents never push to master themselves — the user does/approves).
2. Signed build: set `ARTIFACT_SIGNING_*` (user env), `az login --tenant <tenant> --scope "https://codesigning.azure.net/.default"`, run `.\build.ps1` (see `windows-code-signing` skill).
2a. HIGH-RISK/REPEAT: to log the build, redirect OUTSIDE PowerShell (`powershell -File build.ps1 > log 2>&1` from bash). `.\build.ps1 *> log` inside PS 5.1 turns Nuitka's stderr banner into a fatal `NativeCommandError` (with `$ErrorActionPreference = "Stop"`), so the build exits 1 right after the tests.
2b. HIGH-RISK/REPEAT: SpeedReader running from `SpeedReader.dist` blocks the link step ("Access is denied") — and it is usually the copy hosting the MCP voice. Announce via MCP, ask the user to quit it from the tray and NOT relaunch until done (a relaunch from Explorer re-locks the EXE), then rebuild.
3. HIGH-RISK/REPEAT: smoke-run `SpeedReader.dist\SpeedReader.exe` ~10 s and check `SpeedReader.err.txt` is clean before releasing — a green build can still crash at start (e.g. Nuitka "actively excluded" pystray).
4. Update `release-notes.md` for the version. HIGH-RISK/REPEAT: bump `Core/version.py` `__version__` to match the tag, or the in-app update check nags users of the new build.
5. Package: `python -m tools.release vX.Y` → `release\SpeedReader-vX.Y-win-x64.zip`, `.sha256`, `release\winget\*.yaml`. It refuses unsigned builds and drops the local `*.err.txt`/`*.out.txt` logs.
6. HIGH-RISK/REPEAT: publishing is public — get the user's explicit go-ahead, then `python -m tools.release vX.Y --publish` (needs `gh auth login`).
7. winget: copy `release\winget\*.yaml` to `manifests/c/ChrisLucian/SpeedReader/X.Y/` in a winget-pkgs fork and open a PR (or `wingetcreate submit`). Validate with `winget validate --manifest release\winget` and check the zip holds `SpeedReader/SpeedReader.exe` (the manifest's `RelativeFilePath`).
   - HIGH-RISK/REPEAT: the submit opens a PUBLIC PR on microsoft/winget-pkgs — the auto-mode classifier blocks it; hand the user `! wingetcreate submit -t (gh auth token) release\winget` instead of retrying. Review takes days.
   - PR checklist local test needs ADMIN (user runs it): `winget settings --enable LocalManifestFiles`, `winget install --manifest release\winget`, run `speedreader`, then `winget uninstall ChrisLucian.SpeedReader`.
   - First PR gets `Needs-CLA`: the USER (never the agent — it's a legal agreement) comments `@microsoft-github-policy-service agree` on the PR. Watch checks with `gh pr checks <n> -R microsoft/winget-pkgs`.
   - Until a PR is merged, `winget install ChrisLucian.SpeedReader` finds nothing. Install the same release with `winget install --manifest release\winget` (LocalManifestFiles is already enabled on Chris's PC). It lands in `%LOCALAPPDATA%\Microsoft\WinGet\Packages\ChrisLucian.SpeedReader__DefaultSource\SpeedReader\` (no version in the path, so pins survive upgrades) and is tracked for `winget upgrade`.
   - To point the taskbar pin at that copy, see the `windows-taskbar-pin-retarget` skill. That includes the Smart App Control/Mark-of-the-Web trap.
- First-time downloads of a new certificate may still hit SmartScreen until reputation builds; Smart App Control accepts the CA-signed build.
- After publishing, verify anonymously: download the asset URL, compare its SHA-256 with the `.sha256`, check `releases/latest` returns the new tag and the tag commit equals `origin/master`.
