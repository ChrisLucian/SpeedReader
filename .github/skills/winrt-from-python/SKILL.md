---
name: winrt-from-python
description: Use when calling Windows Runtime (WinRT) APIs from Python with the pywinrt `winrt-*` packages (speech synthesis, media control, storage streams), especially from tkinter apps, worker threads or pytest.
---

# WinRT from Python (pywinrt 3.x)

- HIGH-RISK/REPEAT: blocking on an async op (`op.get()`) raises `RuntimeError: Cannot call blocking method from single-threaded apartment` on STA threads (the tkinter main thread, the pytest main thread). Run WinRT work on a dedicated `ThreadPoolExecutor(max_workers=1)` thread (implicit MTA). `.get()` there means no asyncio is needed.
- `executor.submit(SomeWinRTClass)` fails with `TypeError: keyword arguments not supported`; submit `lambda: fn(*args)` instead.
- Every namespace you touch is a separate package: e.g. `winrt-Windows.Media.SpeechSynthesis`, `winrt-Windows.Media.Core`, `winrt-Windows.Storage.Streams`, and `winrt-Windows.Foundation.Collections` (for iterating any `IVector`/`IVectorView`). A missing one shows up as `ModuleNotFoundError: winrt.windows...` only when the code first runs. Add each one to `requirements.txt` and to Nuitka `--include-module`.
- Interface-typed results (e.g. `_IMediaCue`) need casting to the runtime class: `SpeechCue._from(obj)`.
- `TimeSpan` values arrive as `datetime.timedelta` (`.total_seconds()`).
- Read a stream into bytes: `DataReader(stream.get_input_stream_at(0))`, `reader.load_async(stream.size).get()`, then `reader.read_bytes(bytearray(stream.size))`.
- REPEAT: keep real WinRT/OS calls out of unit tests unless they are side-effect free (synthesis is; playback isn't). Lock the rest in `testsupport/locks.py`.
