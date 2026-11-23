import json, os, re, subprocess

RAW_MP4 = r"D:\AI\1\C4026.MP4"
OUT_DIR = r"d:\AI\full studio\output\av-protein-talking-head\aroll"
RAW_JSON = os.path.join(OUT_DIR, "raw.json")
TRIM_MP4 = os.path.join(OUT_DIR, "raw_trim30.mp4")
AROLL_MP4 = os.path.join(OUT_DIR, "aroll.mp4")

# Step 1: Trim out Take 1 (0 -> 5.40s) and tail noise (> 78.90s), convert 59.94fps 10-bit -> 30fps 1080x1920 8-bit yuv420p
# Note: ffmpeg auto-rotates Display Matrix 90 deg -> 1080x1920!
START_OFFSET = 5.40
END_TIME = 78.90

print("1) Converting & trimming C4026.MP4 -> raw_trim30.mp4 (1080x1920, 30fps)...")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-ss", str(START_OFFSET), "-to", str(END_TIME),
    "-i", RAW_MP4,
    "-vf", "scale=1080:1920:flags=lanczos,fps=30",
    "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
    "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
    TRIM_MP4
], check=True)

# Shift raw.json word timestamps by -START_OFFSET for trimmed clip
tr = json.load(open(RAW_JSON, encoding="utf-8"))
trim_segs = []
for s in tr["segments"]:
    if s["end"] <= START_OFFSET + 0.05:
        continue
    ws = []
    for w in s["words"]:
        ns = round(max(0.0, w["start"] - START_OFFSET), 3)
        ne = round(max(0.0, w["end"] - START_OFFSET), 3)
        if ne > 0.02:
            ws.append({**w, "start": ns, "end": ne})
    if ws:
        trim_segs.append({
            "start": ws[0]["start"],
            "end": ws[-1]["end"],
            "text": " ".join(x["word"] for x in ws),
            "words": ws
        })

TRIM_JSON = os.path.join(OUT_DIR, "raw_trim30.json")
dur_probe = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", TRIM_MP4
], text=True))
trim_dur = float(dur_probe["format"]["duration"])
json.dump({"lang": "vi", "duration": round(trim_dur, 3), "segments": trim_segs},
          open(TRIM_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# Step 2: Run cut_silence.py on raw_trim30.mp4 (--min-silence 0.42 --pad 0.10 --lufs -14)
print("2) Cutting dead silences & normalizing to -14 LUFS -> aroll.mp4...")
subprocess.run([
    r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe",
    r"d:\AI\full studio\phong-cach\talking-head\tools\cut_silence.py",
    TRIM_MP4, AROLL_MP4,
    "--transcript", TRIM_JSON,
    "--min-silence", "0.42",
    "--pad", "0.10",
    "--lufs", "-14"
], check=True)

# Also write readable aroll.transcript.txt
atr = json.load(open(os.path.join(OUT_DIR, "aroll.transcript.json"), encoding="utf-8"))
with open(os.path.join(OUT_DIR, "aroll.transcript.txt"), "w", encoding="utf-8") as f:
    for s in atr["segments"]:
        f.write(f"[{s['start']:6.2f} - {s['end']:6.2f}] {s['text']}\n")
print("Done! Final aroll duration:", atr["duration"])
