import json, os, subprocess, wave
import numpy as np

PROJ_DIR   = r"d:\AI\full studio\output\htpm7-261121"
IN_AROLL   = os.path.join(PROJ_DIR, "aroll_dl")
OUT_AROLL  = os.path.join(PROJ_DIR, "aroll_v2")
IN_STEMS   = os.path.join(PROJ_DIR, "audio_stems_dl", "demucs_out", "htdemucs", "orig_input")
OUT_STEMS  = os.path.join(PROJ_DIR, "audio_stems_v2")
os.makedirs(OUT_AROLL, exist_ok=True)
os.makedirs(OUT_STEMS, exist_ok=True)

# Remove exact stumble "hay hiểu có thể" at frames 1167..1197 inclusive (38.900s -> 39.933333s, 31 frames = 1.033333s)
# Kept Part A: frames 0..1166 (1167 frames, 0.000 -> 38.900s)
# Kept Part B: frames 1198..1826 (629 frames, 39.933333 -> 60.900s)
# Total: 1167 + 629 = 1796 frames = 59.866667s exact!
F_CUT_START = 1167
F_CUT_END   = 1198
N_TOTAL_IN  = 1827
N_TOTAL_OUT = N_TOTAL_IN - (F_CUT_END - F_CUT_START)  # 1796 frames
T_CUT_START = F_CUT_START / 30.0                      # 38.900000s
T_CUT_END   = F_CUT_END / 30.0                        # 39.933333s
DT_CUT      = T_CUT_END - T_CUT_START                 # 1.033333s

for fn, cq in [("main_cut_graded.mp4", "17"), ("main_cut_matte.mp4", "16")]:
    src = os.path.join(IN_AROLL, fn)
    dst = os.path.join(OUT_AROLL, fn)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", src,
        "-vf", f"select='lt(n,{F_CUT_START})+gte(n,{F_CUT_END})',setpts=N/30/TB",
        "-r", "30", "-fps_mode", "cfr", "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", cq, "-b:v", "0", "-pix_fmt", "yuv420p",
        dst
    ], check=True)
    cnt = int(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", dst
    ], text=True).strip())
    print(f"[SliceV2] {fn}: {cnt} frames (expected {N_TOTAL_OUT})", flush=True)
    assert cnt == N_TOTAL_OUT, f"Expected {N_TOTAL_OUT}, got {cnt}"

# Slice vocals.wav & no_vocals.wav at 48kHz with a smooth 35ms cosine crossfade across the cut!
SR = 48000
XF = int(0.035 * SR)  # 1680 samples = 35ms crossfade -> zero click on voice or BGM!

def slice_wav_smooth(in_wav, out_wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", in_wav, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"])
    arr = np.frombuffer(raw, dtype=np.float32).reshape((-1, 2))
    i_a = int(round(T_CUT_START * SR))
    i_b = int(round(T_CUT_END * SR))
    i_end = int(round((N_TOTAL_IN / 30.0) * SR))
    part1 = arr[:i_a + XF].copy()
    part2 = arr[i_b:i_end].copy()
    # Cosine equal-smooth crossfade over XF samples so total length == exact N_TOTAL_OUT / 30 * SR!
    u = np.linspace(0.0, 1.0, XF, dtype=np.float32)[:, None]
    w1 = 0.5 * (1.0 + np.cos(np.pi * u))
    w2 = 1.0 - w1
    part1[-XF:] = part1[-XF:] * w1 + part2[:XF] * w2
    merged = np.vstack([part1, part2[XF:]])
    target_len = int(round((N_TOTAL_OUT / 30.0) * SR))
    if len(merged) < target_len:
        merged = np.vstack([merged, np.zeros((target_len - len(merged), 2), dtype=np.float32)])
    else:
        merged = merged[:target_len]
    pcm16 = (np.clip(merged, -0.99, 0.99) * 32767.0).astype(np.int16)
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())
    print(f"[SliceV2 Audio] {os.path.basename(out_wav)}: {len(merged)/SR:.3f}s ({len(merged)} samples)", flush=True)

slice_wav_smooth(os.path.join(IN_STEMS, "vocals.wav"),    os.path.join(OUT_STEMS, "vocals.wav"))
slice_wav_smooth(os.path.join(IN_STEMS, "no_vocals.wav"), os.path.join(OUT_STEMS, "no_vocals.wav"))

# Shift transcript words after T_CUT_END earlier by DT_CUT (1.033333s)
tr = json.load(open(os.path.join(IN_AROLL, "main_cut_clean.json"), "r", encoding="utf-8"))
new_segs = []
for seg in tr["segments"]:
    nws = []
    for w in seg["words"]:
        ws, we = float(w["start"]), float(w["end"])
        if we <= T_CUT_START + 0.02:
            nws.append({"start": round(ws, 3), "end": round(min(ws + 0.6, min(we, T_CUT_START)), 3), "word": w["word"]})
        elif ws >= T_CUT_END - 0.05:
            nws.append({"start": round(max(T_CUT_START, ws - DT_CUT), 3), "end": round(we - DT_CUT, 3), "word": w["word"]})
    if nws:
        new_segs.append({
            "start": nws[0]["start"],
            "end": nws[-1]["end"],
            "text": " ".join(x["word"] for x in nws),
            "words": nws,
        })

out_tr = {"lang": "vi", "duration": round(N_TOTAL_OUT / 30.0, 4), "segments": new_segs}
with open(os.path.join(OUT_AROLL, "main_cut_clean.json"), "w", encoding="utf-8") as f:
    json.dump(out_tr, f, ensure_ascii=False, indent=2)

print(f"\n=== V2 STUMBLE-FREE TRANSCRIPT ({N_TOTAL_OUT} frames = {N_TOTAL_OUT/30.0:.3f}s) ===")
for s in new_segs:
    print(f"  [{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}")
