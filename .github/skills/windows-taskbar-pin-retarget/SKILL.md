---
name: windows-taskbar-pin-retarget
description: Use when a Windows 11 taskbar pin must point at a different EXE (e.g. swap a dev-build pin for the winget-installed copy) while keeping its position, or when a pinned app shows up as a second taskbar button when it runs.
---

# Retarget a Windows 11 taskbar pin (keep its position)

Win11 has no supported API to pin/reorder. A pin = a `.lnk` in
`%APPDATA%\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar` PLUS two caches in
`HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband`:

- `Favorites`: byte `00`, then per pin `DWORD cb` + shell IDList (`TaskBar\X.lnk`) + `00`. Order = taskbar order. The `.lnk` item has a `0xBEEF001D` extension block holding the **target EXE path** (UTF-16). Removed pins sit as `TaskBar\Tombstones\X.lnk`; ignore them.
- `FavoritesResolve`: per pin `DWORD size` + a full copy of the `.lnk` bytes.

HIGH-RISK/REPEAT: editing only the `.lnk` is NOT enough. Clicking the pin launches the new EXE, but Explorer groups windows by the cached path, so the running app shows as a **second button**. Patch all three.

## Steps
1. Back up: copy the `.lnk`, `reg export HKCU\...\Explorer\Taskband taskband.reg`.
2. Rewrite the `.lnk` (WScript.Shell `CreateShortcut`: TargetPath, WorkingDirectory, IconLocation).
3. `FavoritesResolve`: swap that pin's `size + lnk bytes` for the new `.lnk` file bytes.
4. `Favorites`: replace the UTF-16 path inside the `0xBEEF001D` block, then add the length delta to (a) the block's WORD size, (b) the enclosing IDList item's WORD size, (c) the entry's DWORD `cb`. Check: walking the items (WORD sizes) ends on the `00 00` terminator exactly at `5 + cb`.
5. `Stop-Process explorer -Force` (restart it if it doesn't come back), then screenshot the taskbar: one icon, in the same place, with a running dot.

## Smart App Control trap (winget/zip installs)
- HIGH-RISK/REPEAT: winget zip installs keep Mark-of-the-Web on every extracted file. Running the EXE directly works, but launching it **through a `.lnk`** fails with "An Application Control policy has blocked this file. Dangerous file extension from the web" (nothing in the CodeIntegrity log).
- Fix: `Unblock-File <exe>`, and only for a signed EXE whose download hash you verified. `winget upgrade` re-marks the file, so repeat it after every upgrade.
