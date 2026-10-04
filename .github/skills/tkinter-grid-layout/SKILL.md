---
name: tkinter-grid-layout
description: Avoid overlapping widgets in tkinter grid layouts (MainFrame settings rows). Use when adding/moving widgets in Frames/MainFrame.py.
---

# tkinter grid layout — no overlaps

HIGH-RISK/REPEAT: `grid` does NOT prevent two widgets from occupying the same cell.
A widget with `columnspan=N` claims every column it spans; any other widget gridded
into one of those columns on the same row draws ON TOP of it (even an empty Label).

## Rules
- Before gridding, list each row's `(column, columnspan)` pairs; ranges must not intersect.
- Status/feedback labels whose text appears later (StringVar starting `""`) still occupy
  their cell — give them their own cell or row.
- `settings_frame` columns: 0 label, 1 entry, 2 label, 3 combo (wide), 4 button. Reuse them
  rather than spanning across.
- REPEAT: check `widget.grid_info()` for every widget on the row you touched.

## Verify
- No automated GUI coverage: run `python SpeedReader.py` and look at the changed row.
