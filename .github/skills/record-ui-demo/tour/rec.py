"""Grab the tour window region at ~15 fps; timestamps on the shared perf_counter clock."""
import ctypes
import json
import os
import sys
import time

from PIL import ImageGrab

ctypes.windll.shcore.SetProcessDpiAwareness(2)
OUT = sys.argv[1]
FRAMES = os.path.join(OUT, "frames")
os.makedirs(FRAMES, exist_ok=True)
with open(os.path.join(OUT, "bbox.json")) as f:
    bbox = tuple(json.load(f))
stamps = []
period = 1 / 15
next_t = time.perf_counter()
while not os.path.exists(os.path.join(OUT, "stop.flag")):
    t = time.perf_counter()
    ImageGrab.grab(bbox=bbox, all_screens=True).save(os.path.join(FRAMES, "f%05d.jpg" % len(stamps)), quality=92)
    stamps.append(t)
    next_t += period
    time.sleep(max(0, next_t - time.perf_counter()))
with open(os.path.join(OUT, "stamps.json"), "w") as f:
    json.dump(stamps, f)
