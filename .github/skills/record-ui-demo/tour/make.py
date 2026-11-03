"""Mux the tour: frames (perf_counter stamps) + the exact WAV clips SpeedReader played + captions."""
import array
import json
import os
import shutil
import subprocess
import sys
import wave

OUT = sys.argv[1]
MP4 = sys.argv[2]
stamps = json.load(open(os.path.join(OUT, "stamps.json")))
log = json.load(open(os.path.join(OUT, "log.json")))
t0, t_end = stamps[0], stamps[-1]

# ---- audio timeline -------------------------------------------------------
plays = [e for e in log if e[0] == "play"]
with wave.open(plays[0][2]) as w:
    rate, width, chans = w.getframerate(), w.getsampwidth(), w.getnchannels()
assert width == 2, "expected 16-bit PCM"
total = int((t_end - t0) * rate) + rate
track = array.array("h", bytes(total * 2 * chans))
cut_times = sorted(e[1] for e in log if e[0] in ("play", "stop"))
for _, t, path in plays:
    with wave.open(path) as w:
        assert (w.getframerate(), w.getnchannels()) == (rate, chans)
        samples = array.array("h", w.readframes(w.getnframes()))
    later = [c for c in cut_times if c > t + 0.001]
    limit = int(((later[0] - t) if later else 1e9) * rate) * chans
    start = int((t - t0) * rate) * chans
    chunk = samples[:limit]
    end = min(start + len(chunk), len(track))
    track[start:end] = chunk[:end - start]
with wave.open(os.path.join(OUT, "narration.wav"), "wb") as w:
    w.setnchannels(chans)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes(track.tobytes())

# ---- frame list with real durations ---------------------------------------
with open(os.path.join(OUT, "frames.txt"), "w") as f:
    for i, t in enumerate(stamps):
        nxt = stamps[i + 1] if i + 1 < len(stamps) else t + 1 / 15
        f.write("file 'frames/f%05d.jpg'\nduration %.4f\n" % (i, nxt - t))
    f.write("file 'frames/f%05d.jpg'\n" % (len(stamps) - 1))

# ---- captions ---------------------------------------------------------------
labels = [e for e in log if e[0] == "label"]
shutil.copy(r"C:\Windows\Fonts\segoeuib.ttf", os.path.join(OUT, "font.ttf"))
draws = []
for i, (_, t, text) in enumerate(labels):
    if text == "END":
        continue
    a = max(0.0, t - t0)
    b = labels[i + 1][1] - t0 if i + 1 < len(labels) else t_end - t0
    name = "cap%02d.txt" % i
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text)
    draws.append(
        "drawtext=fontfile=font.ttf:textfile=%s:fontsize=46:fontcolor=white:"
        "x=(w-text_w)/2:y=990:enable='between(t,%.2f,%.2f)'" % (name, a, b))

vf = ",".join([
    "scale=1920:960:force_original_aspect_ratio=decrease",
    "pad=1920:1080:(ow-iw)/2:12:color=0x101418",
    "drawbox=x=0:y=972:w=1920:h=108:color=0x1f6feb@0.92:t=fill",
] + draws + ["fps=30", "format=yuv420p"])

subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-f", "concat", "-safe", "0", "-i", "frames.txt",
    "-i", "narration.wav",
    "-vf", vf,
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-movflags", "+faststart", "-shortest", MP4,
], cwd=OUT, check=True)
print("wrote", MP4, "duration %.1fs" % (t_end - t0), "audio %d Hz" % rate, "captions", len(draws))
