import json, os, shutil, subprocess
import numpy as np

OUT = r"d:\AI\full studio\output\f20-set-qua-2011"
CACHE = os.path.join(OUT, "raw_cache")
MEDIA = os.path.join(OUT, "capcut_media")
RAW_DOC = r"Z:\Máy tính khác\My Computer\F20\video gốc\261116\Chi Oanh\dọc"
RAW_NG  = r"Z:\Máy tính khác\My Computer\F20\video gốc\261116\Chi Oanh\ngang"
os.makedirs(MEDIA, exist_ok=True)

# Check free disk space on C: and D:
for drv in ["C:\\", "D:\\"]:
    total, used, free = shutil.disk_usage(drv)
    print(f"Drive {drv} free: {free / (1024**3):.1f} GB")

# 1. Exact fine boundary detection between consecutive segments in source_v4.mp4
SR = 16000
def decode_16k(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.float32)

v4_a = decode_16k(os.path.join(OUT, "source_v4.mp4"))
TOTAL_DUR = 112.433333  # 3373 frames @ 30fps

# Known sequence of (clip_name, approximate_v4_start, approximate_v4_end, exact_delta)
# where raw_time = v4_time + delta
rough_blocks = [
    ("C3844.MP4",   0.00,   4.30,  +1.7268),
    ("C3849.MP4",   4.30,  10.30,  -2.3465),
    ("C3852.MP4",  10.30,  19.77,  -9.5065),
    ("C3852.MP4",  19.77,  50.03,  -8.5398),
    ("C3853.MP4",  50.03,  61.70, -47.8064),
    ("C3853.MP4",  61.70,  69.10, -47.5064),
    ("C3855.MP4",  69.10,  76.70, -66.7564),
    ("C3855.MP4",  76.70,  82.75, -65.0898),
    ("C3855.MP4",  82.75,  90.43, -63.3564),
    ("C3862.MP4",  90.43,  94.00, -87.6231),
    ("C3862.MP4",  94.00,  94.85, -87.3897),
    ("C3862.MP4",  94.85,  98.63, -86.9564),
    ("C3864.MP4",  98.63, 112.433333, -93.2564),
]

raw_wavs = {}
for fn, _, _, _ in rough_blocks:
    if fn not in raw_wavs:
        raw_wavs[fn] = decode_16k(os.path.join(CACHE, fn))

# Refine each boundary to exact frame (1/30s) by checking which side correlates better in 0.2s windows around boundary
boundaries = [0.0]
for i in range(len(rough_blocks) - 1):
    fn_l, _, b_est, dl = rough_blocks[i]
    fn_r, _, _, dr     = rough_blocks[i + 1]
    best_b = round(b_est * 30) / 30.0
    best_score = -1e9
    for df in range(-18, 19):
        b = round((b_est + df / 30.0) * 30) / 30.0
        # Compare [b-0.4 .. b] with left and [b .. b+0.4] with right
        i_m = int(round(b * SR))
        w = int(0.35 * SR)
        v_l = v4_a[max(0, i_m - w):i_m]
        v_r = v4_a[i_m:min(len(v4_a), i_m + w)]
        rl_i = int(round((b + dl) * SR))
        rr_i = int(round((b + dr) * SR))
        s_l = raw_wavs[fn_l][max(0, rl_i - len(v_l)):rl_i]
        s_r = raw_wavs[fn_r][rr_i:rr_i + len(v_r)]
        if len(s_l) == len(v_l) and len(s_r) == len(v_r) and len(v_l) > 100:
            err = np.mean((v_l - s_l)**2) + np.mean((v_r - s_r)**2)
            # We want minimum MSE between clean voice and v4 (since BGM is constant across boundary)
            sc = -float(err)
            if sc > best_score:
                best_score = sc
                best_b = b
    boundaries.append(best_b)
boundaries.append(TOTAL_DUR)

aroll_plan = []
print("\n=== EXACT FRAME-LOCKED CLEAN A-ROLL PLAN (3373 frames = 112.433s) ===")
tot_frames = 0
for i, (fn, _, _, delta) in enumerate(rough_blocks):
    t0 = boundaries[i]
    t1 = boundaries[i + 1]
    f0 = int(round(t0 * 30))
    f1 = int(round(t1 * 30))
    nf = f1 - f0
    dur = nf / 30.0
    r0 = max(0.0, round(t0 + delta, 4))
    aroll_plan.append({
        "idx": i, "fn": fn,
        "t0": round(f0 / 30.0, 6), "t1": round(f1 / 30.0, 6),
        "frames": nf, "dur": round(dur, 6),
        "raw_in": r0, "delta": delta
    })
    tot_frames += nf
    print(f"  [{i:02d}] {f0/30.0:6.2f}s -> {f1/30.0:6.2f}s ({nf:3d}f = {dur:5.2f}s) | {fn} in={r0:6.3f}s")
print("Total frames:", tot_frames)
json.dump(aroll_plan, open(os.path.join(OUT, "aroll_frame_plan.json"), "w", encoding="utf-8"), indent=2)

# 2. Render each clean A-roll segment as upright 1080x1920 @ 30fps MP4 + clean micro-faded 48kHz WAV!
aroll_seg_dir = os.path.join(MEDIA, "aroll_segs")
os.makedirs(aroll_seg_dir, exist_ok=True)
SR48 = 48000
voice_full = np.zeros((int(round(TOTAL_DUR * SR48)), 2), dtype=np.float32)

concat_lines = []
for seg in aroll_plan:
    idx = seg["idx"]
    src_p = os.path.join(CACHE, seg["fn"])
    seg_mp4 = os.path.join(aroll_seg_dir, f"aroll_{idx:02d}_{seg['fn'][:-4]}.mp4")
    if not os.path.exists(seg_mp4):
        # Auto-rotates Sony vertical metadata, applies subtle studio brightness/warmth polish, exact frame count!
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{seg['raw_in']:.4f}", "-i", src_p,
            "-frames:v", str(seg["frames"]),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.025:contrast=1.04:saturation=1.08,fps=30",
            "-af", f"atrim=0:{seg['dur']:.6f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.033,afade=t=out:st={max(0.01, seg['dur']-0.055):.4f}:d=0.055",
            "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            seg_mp4
        ], check=True)
    concat_lines.append(f"file '{seg_mp4.replace(chr(92), '/')}'")

    # Also decode exact clean stereo audio with micro-fade into voice_full
    raw_pcm = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{seg['raw_in']:.4f}", "-t", f"{seg['dur']:.6f}",
        "-i", src_p, "-ac", "2", "-ar", str(SR48), "-f", "f32le", "-"
    ])
    arr = np.frombuffer(raw_pcm, dtype=np.float32).reshape((-1, 2)).copy()
    need = int(round(seg["dur"] * SR48))
    if len(arr) < need:
        arr = np.vstack([arr, np.zeros((need - len(arr), 2), dtype=np.float32)])
    arr = arr[:need]
    fi = min(len(arr)//3, int(0.033 * SR48))
    fo = min(len(arr)//3, int(0.055 * SR48))
    if fi > 1: arr[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 1: arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    s0 = int(round(seg["t0"] * SR48))
    s1 = min(len(voice_full), s0 + len(arr))
    voice_full[s0:s1] = arr[:s1 - s0]

concat_txt = os.path.join(OUT, "aroll_concat.txt")
open(concat_txt, "w", encoding="utf-8").write("\n".join(concat_lines))
clean_aroll_mp4 = os.path.join(MEDIA, "00_Clean_ARoll_Full.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", clean_aroll_mp4], check=True)
print("Built 00_Clean_ARoll_Full.mp4!")

# Save raw clean voice WAV & EQ-polished -14 LUFS Voice Master WAV
import wave
raw_vo_wav = os.path.join(OUT, "voice_raw_clean.wav")
with wave.open(raw_vo_wav, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR48)
    wf.writeframes((np.clip(voice_full, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())

vo_master_wav = os.path.join(MEDIA, "01_Voice_Clean_Master.wav")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", raw_vo_wav,
    "-af", "highpass=f=85,equalizer=f=260:t=q:w=1.2:g=-1.8,equalizer=f=3400:t=q:w=1.2:g=2.0,acompressor=threshold=-19dB:ratio=2.6:attack=8:release=90,loudnorm=I=-14.5:TP=-1.2:LRA=8",
    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", vo_master_wav
], check=True)
print("Built 01_Voice_Clean_Master.wav!")

# 3. Prepare 12 upright, color-polished 1080x1920 @ 30fps B-Roll clips in capcut_media!
broll_specs = [
    ("broll_01_dolly_sets.mp4",     os.path.join(RAW_DOC, "C3909.MP4"), 0.5, 6.0, "vertical"),
    ("broll_02_rotating_tower.mp4", os.path.join(RAW_DOC, "C3875.MP4"), 0.5, 8.0, "vertical"),
    ("broll_03_arrange_table.mp4",  os.path.join(RAW_DOC, "C3871.MP4"), 1.0, 7.0, "vertical"),
    ("broll_04_mica_sunlit.mp4",    os.path.join(RAW_DOC, "C3908.MP4"), 0.5, 7.0, "vertical"),
    ("broll_05_quai_da_macro.mp4",  os.path.join(RAW_NG,  "DJI_20261116095310_0100_D.MP4"), 0.3, 6.5, "horiz_crop"),
    ("broll_06_hoa_no_macro.mp4",   os.path.join(RAW_NG,  "DJI_20261116095317_0101_D.MP4"), 0.3, 6.5, "horiz_crop"),
    ("broll_07_inside_bag_pip.mp4", os.path.join(RAW_DOC, "C3873.MP4"), 0.5, 6.5, "vertical"),
    ("broll_08_cam_nang_close.mp4", os.path.join(CACHE,   "C3854.MP4"), 1.5, 7.5, "vertical"),
    ("broll_09_factory_pack1.mp4",  os.path.join(RAW_DOC, "C3882.MP4"), 0.5, 6.0, "vertical"),
    ("broll_10_factory_carton.mp4", os.path.join(RAW_DOC, "C3892.MP4"), 0.5, 6.0, "vertical"),
    ("broll_11_delivery_car.mp4",   os.path.join(RAW_DOC, "C3901.MP4"), 0.5, 6.0, "vertical"),
    ("broll_12_handover_gift.mp4",  os.path.join(RAW_DOC, "C3921.MP4"), 1.0, 6.5, "vertical"),
]

for out_name, src_p, ss, dur, mode in broll_specs:
    dst_p = os.path.join(MEDIA, out_name)
    if os.path.exists(dst_p):
        continue
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.025:contrast=1.05:saturation=1.10,fps=30"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.2f}", "-t", f"{dur:.2f}", "-i", src_p,
        "-vf", vf, "-an",
        "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
        dst_p
    ], check=True)
    print("Prepared B-roll:", out_name)
print("ALL 12 B-ROLLS READY!")
