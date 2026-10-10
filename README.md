# SpeedReader
Python based tool to use text to speech to read books or study material quickly.

# History
In college my now father in law was using a text to speech program and talking about how he can listen to books at 500 WPM and recommended it to me. It was a pivotal point in my education because I realized I could listen & read a document at 500 words per minute and internalize the information. I began to receive better grades and was able to get ‘A’ letter grades on tests composed of 3 months of materials by listening for 2 hours. I later wrote a speed reader for myself that I used for 10 years and now I felt like it was time to write an updated version in python. I suggest trying it at low speeds first, then increasing the speed as you feel comfortable. Start at 200, and increment by 25 each time you use it until you find that your level of understanding is decreasing then take it slower till you reach 500 WPM. 

I believe if you are an auditory learning this tool can be massively helpful to you.

# Setup
## Run Locally Setup
Tested with Python 3.14 (originally developed on 3.7)

install requirements.txt
pyttsx3==2.71 due to a bug detailed here: https://github.com/nateshmbhat/pyttsx3/issues/78

## Controls
- **Speed** — words per minute (spin box, steps of 25; start low, e.g. 200, and work up to 500).
- **Voice** — pick from the text-to-speech voices installed on your system; the choice applies to both your reading and any AI agent speaking through the MCP server.
- **Agent Voices…** — choose which system voices agents are allowed to use (see below). All voices are enabled by default.
- **Server…** (shows `Server: <port>…` while hosting) — one dialog to change the MCP port and **Restart Server** without closing the app (the port is saved to `config.json` as `mcp.port`), plus live status: hosting state, pause-while-mic-in-use (and your current mic state), and each enabled voice with the agents that claimed it.
- **Light mode / Dark mode** — toggles the modern Windows 11 look ([sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)), including the title bar. Dark by default; the choice is saved to `config.json` as `ui.theme`.
- **Pause / Resume** (left of Speak) — pause mid-text; Resume picks up at the same word.
- **Double-click a word** — start reading from that word.
- Shortcuts: `Ctrl+B` paste & speak (interrupts and clears anything currently playing or queued, including agent speech, then reads the clipboard now), `Ctrl+A` select all. Agent (MCP) utterances otherwise queue and play in order.
- **`Ctrl+Alt+B` from any app** — system-wide paste & speak, even while SpeedReader is hidden. If another app already owns that hotkey, SpeedReader just skips it.
- **System tray** — closing the window hides SpeedReader to the tray (so agents can keep speaking). Tray menu: *Show SpeedReader*, *Read clipboard*, *Quit* (Quit is how you exit).
- Junk isn't read character by character — for both your text and agent speech: code blocks → "[code]", links → "[URL]", Windows paths (`C:\...`, `C:/...`, `\\server\...`) → "[file path]", emails → "[email]", GUIDs → "[ID]", hex hashes → "[hash]", any 40+ character token → "[long text]". Plain numbers and words stay as they are.

## MCP server (let AI agents speak through SpeedReader)
SpeedReader ships a [Model Context Protocol](https://modelcontextprotocol.io) server so an AI agent (e.g. in VS Code) can read text aloud on your machine. It exposes these tools:

- `speak(text, agent?, voice?, rate?)` — read text aloud. Omit `rate` to use the WPM set in the UI; pass the `agent` you claimed with (or an explicit `voice`) to speak in a specific voice, otherwise the UI's selected voice is used.
- `list_voices()` — list the voices the user enabled for agents, with claim status.
- `claim_voice(agent?, voice?)` — claim a voice to speak with (see *Per-agent voices* below).
- `release_voice(agent)` — release a claimed voice.

There are two ways to run it:

### Hosted by the running app (recommended)
This is the main use case: you keep SpeedReader open to read your own text, and agents speak through the very same window. It also means agent speech uses the **rate and voice currently set in the UI**.

1. Enable hosting in `config.json` at the repo root (hosting is **off by default**):

   ```json
   {
     "mcp": { "enabled": true, "host": "127.0.0.1", "port": 8765 }
   }
   ```

2. Start the app (`python SpeedReader.py`). It hosts the server over HTTP on `http://127.0.0.1:8765/mcp`, bound to localhost only. You can change the port at runtime in the app's **Server…** dialog (**Restart Server**) — the new port is persisted to `config.json` for next launch (update your agent's URL to match).
3. Point your agent at it. In VS Code this is already wired in [.vscode/mcp.json](.vscode/mcp.json):

   ```json
   {
     "servers": {
       "speedreader": { "type": "http", "url": "http://127.0.0.1:8765/mcp" }
     }
   }
   ```

The agent now has the tools above. Omit `rate` to use the WPM set in the UI.

### Per-agent voices (multiple agents, multiple voices)
Use **Agent Voices…** in the app to enable/disable which installed voices agents may use; the choice is saved to `config.json` under `mcp.voices`. The voice you pick in the **Voice** dropdown is reserved for you — agents avoid it and claim the other voices first (unless it's the only enabled voice). The agent handshake is:

1. **(optional) discover** — `list_voices()` shows enabled voices and who holds each.
2. **reserve** — `claim_voice(agent="my-repo")` reserves a voice and returns it. Use a stable identifier (repo folder name or current task). Re-claiming returns the same voice.
3. **speak** — `speak("hello", agent="my-repo")` reads in your reserved voice.
4. **(optional) release** — `release_voice("my-repo")` frees it for others.

Rules:
- `speak` **requires a reservation**: calling it without a reserved `agent` (or an explicit `voice="..."`) is an error that tells the agent to `claim_voice` first — unless only one voice is enabled (then it's used automatically).
- Claims are exclusive while unused voices remain. When every assignable voice is taken, `claim_voice` **requires an `agent` label** and shares another *agent's* voice (never yours, unless yours is the only voice).

Speech is serialized so each utterance reads in its own voice without bleeding into the next.

### Pause agent speech while you're on a call
Set `mcp.pause_when_mic_in_use` to `true` in `config.json` to stop agents talking over you during calls:

```json
{
  "mcp": { "enabled": true, "pause_when_mic_in_use": true }
}
```

When enabled, the `speak` tool checks whether any app is currently using your microphone (a proxy for "in a call") and, if so, **skips** speaking and returns a message instead of playing audio. It's **off by default**, only affects agent/MCP speech (your own reading is never paused), and currently uses Windows microphone state — on other platforms it never pauses.

### Media Pause on Speaking
A new setting, `mcp.pause_media_when_speaking`, controls whether the system should pause media playback (like background music or videos) when SpeedReader is actively speaking. This feature is useful for ensuring that TTS audio is not masked by other sounds playing on the system.

To enable this:
1. Update your `config.json` at the repo root to include:

   ```json
   {
     "mcp": { "enabled": true, "pause_media_when_speaking": true }
   }
   ```
2. Restart SpeedReader for the change to take effect.

### Standalone (stdio)
For development or agent-spawned use without the GUI:

```pwsh
python mcp_server.py
```

## Convert to EXE
The build uses Nuitka. For background on the bootloader fix: https://github.com/pyinstaller/pyinstaller/issues/3268

```pwsh
.\build.ps1
```

- Creates/uses `.venv`, installs `requirements.txt`, runs the tests, then builds with the **venv's** Nuitka (`python -m nuitka`) — a global `nuitka` would bundle global packages (e.g. an incompatible `mcp` 2.x) and the MCP server won't start.
- Output: `SpeedReader.dist\SpeedReader.exe`. `config.json` is copied next to it; the app reads `config.json` from the working directory first, then from the EXE's folder.
- The EXE has no console window; errors and server logs go to `SpeedReader.err.txt` (and `SpeedReader.out.txt`) beside it.
- Close any running `SpeedReader.exe` first — the script refuses to build while it locks `SpeedReader.dist`.
- The tray icon uses [pystray](https://github.com/moses-palmer/pystray) (LGPL-3.0). It is **not** compiled into the EXE: `pystray` (and its `six` dependency) ship as plain, replaceable `.py` files in `SpeedReader.dist\pystray\`.

### Code signing (Smart App Control)
Windows Smart App Control blocks unsigned EXEs/DLLs. A self-signed certificate does **not** help — the signature must chain to a Microsoft-trusted CA. The build signs with [Azure Artifact Signing](https://learn.microsoft.com/azure/artifact-signing/) (formerly Trusted Signing, ~$10/month) when configured:

1. In Azure: create an Artifact Signing account, complete identity validation, create a *Public Trust* certificate profile, and give yourself the *… Certificate Profile Signer* role on the account.
2. Install the Azure CLI (`winget install -e --id Microsoft.AzureCLI`, then open a new terminal) and sign in: `az login --tenant <your-tenant> --scope "https://codesigning.azure.net/.default"`. `--tenant` is required for personal Microsoft accounts (otherwise `AADSTS500200`); the build signs with this CLI login.
3. Set env vars and build:

```pwsh
$env:ARTIFACT_SIGNING_ENDPOINT = "https://eus.codesigning.azure.net"  # your account's region
$env:ARTIFACT_SIGNING_ACCOUNT  = "<account>"
$env:ARTIFACT_SIGNING_PROFILE  = "<certificate profile>"
.\build.ps1
```

- Installs the `sign` dotnet tool if missing, signs every not-yet-signed `.exe`/`.dll`/`.pyd` in `SpeedReader.dist`, and fails the build if `SpeedReader.exe` isn't validly signed afterwards.
- Without the env vars, the build is unsigned and prints a warning.

## Release (GitHub + winget)
After a **signed** `.\build.ps1`:

```pwsh
python -m tools.release v0.6                # release\SpeedReader-v0.6-win-x64.zip + .sha256 + release\winget\*.yaml
python -m tools.release v0.6 --publish      # ...then gh release create v0.6 (uses release-notes.md)
```

- Refuses to package if `SpeedReader.exe` isn't validly signed; leaves out the local `*.err.txt`/`*.out.txt` logs.
- `--publish` needs the [GitHub CLI](https://cli.github.com) (`winget install -e --id GitHub.cli`, then `gh auth login`) and should run from `master` after the release commit is pushed.
- winget: copy `release\winget\*.yaml` into a fork of [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs) under `manifests/c/ChrisLucian/SpeedReader/<version>/` and open a PR (or use `wingetcreate submit`).

## Tests
```pwsh
pip install -r requirements-dev.txt
python -m pytest -q
```
- ~230 tests in ~10 s. GUI tests use a hidden window; every real OS side effect (media keys, clipboard, config file, title bar/DPI, microphone registry, browser, MCP server/port, global hotkey, tray icon) is **locked** by `testsupport/locks.py` — a test that reaches one without mocking it fails with `SideEffectLocked`.


# Prompt other agents to use your local agent
```
## Speak via the SpeedReader MCP

A local MCP server named `speedreader` exposes voice tools. Use them to READ
ALOUD every task-completion summary AND every clarifying question you ask me.

Rules (follow exactly):
1. ONCE per session, reserve a voice: call `claim_voice(agent="<this-repo-folder-name>")`.
   Use a stable id (the repo folder name) as `agent` — not a random string.
2. For EVERY summary and EVERY question, call `speak(agent="<same-id>", text="<the message>")`.
   - Keep `text` to the spoken gist (1–3 sentences), not full code or logs.
   - Omit `rate` so it uses the WPM set in the SpeedReader UI.
3. When the task is fully done, call `release_voice(agent="<same-id>")`.
4. If multiple voices exist and you skip `agent`, `speak` errors — always pass `agent`.
   To see/pick a voice, call `list_voices` and optionally `claim_voice(agent=..., voice="<name|id>")`.

If the `speedreader` tools are NOT available, do NOT silently skip speaking —
tell me to enable hosting (set `mcp.enabled: true` in SpeedReader's config.json,
host 127.0.0.1, then restart the app) so the `speak` tool is reachable, and
continue the task without speaking until it's on.

REPEAT (high-risk, easy to forget): speak the summary AND every question; claim
once, speak with that same agent, release at the end.
```