import json, os, subprocess
import numpy as np

PROJ = r"d:\AI\full studio\output\htpm-tokyo"
AROLL = os.path.join(PROJ, "aroll")

# 1. Clean 100% of transcript words
d = json.load(open(os.path.join(AROLL, "main_cut.json"), encoding="utf-8"))
FIXES = {
    0: {1: "rát", 14: "rát", 21: "hằng", 22: "ngày."},
    1: {2: "tế,", 10: "hàng", 11: "rào", 20: "yếu."},
    2: {2: "vi", 16: "nhiễm."},
    3: {19: "kín,"},
    4: {0: "nên", 10: "độ", 18: "mạc."},
    5: {3: "Glycerin,", 4: "Niacinamide", 8: "cúc", 9: "La", 10: "Mã", 16: "Viên", 18: "phụ", 19: "khoa", 20: "Hằng", 21: "Thu."},
    6: {1: "vùng", 2: "kín", 19: "nhiên."},
}
for si, seg in enumerate(d["segments"]):
    wl = seg["words"]
    for wi, nw in FIXES.get(si, {}).items():
        if wi < len(wl):
            wl[wi]["word"] = nw
    seg["text"] = " ".join(w["word"] for w in wl)

clean_p = os.path.join(AROLL, "main_cut_clean.json")
with open(clean_p, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print("=== CLEAN TRANSCRIPT ===")
for si, seg in enumerate(d["segments"]):
    print(f"{si:02d} [{seg['start']:5.2f}-{seg['end']:5.2f}] {seg['text']}")

# 2. Detect bass/beat onsets in Tokyo Drift Remix starting at 29.0s!
raw = subprocess.check_output([
    "ffmpeg", "-v", "error", "-ss", "29.0", "-t", "38.0",
    "-i", os.path.join(AROLL, "tokyo_bgm.mp3"),
    "-af", "lowpass=f=150", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"
])
bass = np.frombuffer(raw, dtype=np.float32)
hop = 160  # 10ms
n_h = len(bass) // hop
env = np.sqrt(np.mean(bass[:n_h * hop].reshape((n_h, hop)) ** 2, axis=1))
diff = np.maximum(0.0, np.diff(env, prepend=env[0]))
# Find strong bass hits separated by >= 0.38s (~127 BPM = 0.472s/beat)
peaks = []
for i in range(5, n_h - 5):
    if diff[i] == np.max(diff[i - 18:i + 18]) and diff[i] > np.percentile(diff, 82):
        if not peaks or (i - peaks[-1]) >= 38:
            peaks.append(i)
beat_secs = [round(p * 0.01, 2) for p in peaks[:30]]
intervals = np.diff(beat_secs)
est_bpm = 60.0 / float(np.median(intervals)) if len(intervals) else 127.0
print(f"=== TOKYO DRIFT (from 29.0s) EST BPM: {est_bpm:.1f}, FIRST 25 BEATS: {beat_secs[:25]} ===")
