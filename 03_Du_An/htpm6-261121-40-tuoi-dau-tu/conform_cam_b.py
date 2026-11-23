import json, math, os, shutil, subprocess, time
import numpy as np
from scipy.signal import correlate
from PIL import Image, ImageDraw

PROJ_DIR  = r"d:\AI\full studio\output\htpm6-261121"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
CAM_B_SRC = r"C:\Users\Hang thu\Downloads\HTPM(1).mp4"
PY_EXE    = r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
MATTE     = r"d:\AI\full studio\phong-cach\talking-head\tools\matte.py"
LUT_ROSY  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\01_HTPM_Beauty_Rosy_Skin.cube"

mc_a      = os.path.join(AROLL_DIR, "main_cut.mp4")
voc_a_wav = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "vocals.wav")
cam_b_30  = os.path.join(AROLL_DIR, "_cam_b_30cfr.mp4")
cam_b_syn = os.path.join(AROLL_DIR, "cam_b_synced_graded.mp4")
cam_b_mat = os.path.join(AROLL_DIR, "cam_b_matte.mp4")

t0 = time.time()
print("[CamB 1/4] Normalizing HTPM(1).mp4 -> 30fps CFR & extracting speech audio...", flush=True)
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", CAM_B_SRC,
    "-r", "30", "-fps_mode", "cfr",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
    cam_b_30
], check=True)

# Also run Demucs vocals on Cam B (takes ~3.5s on GPU!) so CamA vocals vs CamB vocals have ZERO BGM interference!
b_wav_44 = os.path.join(STEMS_DIR, "camb_input.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", cam_b_30, "-ar", "44100", "-ac", "2", b_wav_44], check=True)
subprocess.run([PY_EXE, "-m", "demucs.separate", "--two-stems", "vocals", "-n", "htdemucs", "-o", os.path.join(STEMS_DIR, "demucs_b"), b_wav_44], check=True)
voc_b_wav = os.path.join(STEMS_DIR, "demucs_b", "htdemucs", "camb_input", "vocals.wav")

sr = 16000
def dec_speech(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-af", "highpass=f=180,lowpass=f=3600", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32)

va = dec_speech(voc_a_wav)
vb = dec_speech(voc_b_wav)

cnt_a = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", mc_a], text=True).strip())
cnt_b = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", cam_b_30], text=True).strip())
print(f"[CamB 2/4] Syncing {cnt_a} CamA frames against {cnt_b} CamB frames using pure Demucs vocals...", flush=True)

# Compute piecewise offset every 1.0s using a 2.6s sliding vocal window + median/monotonic jump-cut tracker!
n_sec = int(math.ceil(cnt_a / 30.0))
sec_offsets = []
for s in range(n_sec):
    tc = min(len(va) / sr - 1.4, max(1.3, s + 0.5))
    i0 = max(0, int((tc - 1.3) * sr))
    i1 = min(len(va), int((tc + 1.3) * sr))
    seg = va[i0:i1] - np.mean(va[i0:i1])
    if np.linalg.norm(seg) < 0.02:
        sec_offsets.append((s, None, 0.0))
        continue
    # Search in plausible range [-1.0s .. +12.0s] relative to CamA time
    b_lo = max(0, i0 - int(1.5 * sr))
    b_hi = min(len(vb), i1 + int(12.0 * sr))
    sub_b = vb[b_lo:b_hi] - np.mean(vb[b_lo:b_hi])
    c = correlate(sub_b, seg, mode="valid")
    bi = int(np.argmax(c))
    off = ((b_lo + bi) - i0) / float(sr)
    conf = float(c[bi] / (np.linalg.norm(seg) * np.linalg.norm(sub_b[bi:bi+len(seg)]) + 1e-8))
    sec_offsets.append((s, off, conf))

# Fill low-energy gaps & quantize clean jump-cut plateaus (within 0.05s = same continuous take!)
valid_offs = [(s, o, cf) for s, o, cf in sec_offsets if o is not None and cf >= 0.22]
print(f"  High-confidence sync points: {len(valid_offs)}/{n_sec}")
for s, o, cf in valid_offs[::4]:
    print(f"    t={s:2d}s -> offset={o:+.4f}s ({o*30:+.1f}f) | vocal_conf={cf:.3f}")

# Build frame-by-frame map: for each Cam A frame fa (0..cnt_a-1), pick exact Cam B frame fb!
frame_offs = np.zeros(cnt_a, dtype=np.float64)
for fa in range(cnt_a):
    ta = fa / 30.0
    # Find nearest confident point (preferring piecewise constant plateau unless jump > 0.08s)
    best_s, best_o, _ = min(valid_offs, key=lambda x: abs((x[0] + 0.5) - ta))
    # Smooth average of neighbors on the SAME plateau (|o - best_o| < 0.06s)
    near = [o for s, o, cf in valid_offs if abs((s + 0.5) - ta) <= 2.5 and abs(o - best_o) < 0.06]
    frame_offs[fa] = float(np.median(near)) if near else best_o

fb_indices = np.clip(np.round(np.arange(cnt_a) + frame_offs * 30.0).astype(np.int32), 0, cnt_b - 1)
json.dump({"cnt_a": cnt_a, "cnt_b": cnt_b, "sec_offsets": sec_offsets}, open(os.path.join(AROLL_DIR, "multicam_sync.json"), "w"), indent=2)

# Decode Cam B graded frames & write exact frame-synced cam_b_synced_graded.mp4 (2,064 frames)!
print("[CamB 3/4] Grading & conforming Cam B frame-for-frame to Cam A timeline...", flush=True)
lut_tmp = os.path.join(AROLL_DIR, "_rosy_b.cube")
shutil.copy2(LUT_ROSY, lut_tmp)
cam_b_gr_tmp = os.path.join(AROLL_DIR, "_cam_b_graded_all.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", cam_b_30, "-an",
    "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_rosy_b.cube[bg];[a][bg]blend=all_expr=A*0.45+B*0.55[v]",
    "-map", "[v]", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
    cam_b_gr_tmp
], cwd=AROLL_DIR, check=True)
os.remove(lut_tmp)

# Stream-read cam_b_gr_tmp into memory or seek sequentially? Wait: 2295 frames at 1080x1920 rgb24 is 14 GB, so don't hold all in RAM!
# Instead, fb_indices is monotonically non-decreasing (except tiny 0-frame jitter)! Enforce monotonic non-decreasing within same plateau and stream through once!
for i in range(1, cnt_a):
    if abs(frame_offs[i] - frame_offs[i - 1]) < 0.06 and fb_indices[i] < fb_indices[i - 1]:
        fb_indices[i] = fb_indices[i - 1]

# Even if there were any backward jump, check if monotonic:
is_mono = bool(np.all(np.diff(fb_indices) >= 0))
print("  Cam B index map monotonic:", is_mono, "| min_fb=", int(fb_indices[0]), "max_fb=", int(fb_indices[-1]), flush=True)

writer = subprocess.Popen([
    "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
    cam_b_syn
], stdin=subprocess.PIPE)

if is_mono:
    reader = subprocess.Popen(["ffmpeg", "-v", "error", "-i", cam_b_gr_tmp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    cur_b = -1
    cur_buf = None
    nb = 1080 * 1920 * 3
    for target_b in fb_indices:
        while cur_b < target_b:
            b = reader.stdout.read(nb)
            if len(b) < nb:
                break
            cur_buf = b
            cur_b += 1
        if cur_buf is not None:
            writer.stdin.write(cur_buf)
    reader.stdout.close(); reader.wait()
else:
    # Fallback chunked seek
    nb = 1080 * 1920 * 3
    all_b = []
    reader = subprocess.Popen(["ffmpeg", "-v", "error", "-i", cam_b_gr_tmp, "-vf", "scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    while True:
        b = reader.stdout.read(nb)
        if len(b) < nb: break
        all_b.append(b)
    reader.stdout.close(); reader.wait()
    for target_b in fb_indices:
        writer.stdin.write(all_b[min(len(all_b)-1, int(target_b))])

writer.stdin.close(); writer.wait()
for tmp in (cam_b_30, cam_b_gr_tmp, b_wav_44):
    if os.path.exists(tmp): os.remove(tmp)
shutil.rmtree(os.path.join(STEMS_DIR, "demucs_b"), ignore_errors=True)

# Run 2x RVM Matte on cam_b_synced_graded.mp4!
print("[CamB 4/4] Computing 2x RVM Matte for Cam B...", flush=True)
half = cnt_a // 2
bp1 = os.path.join(AROLL_DIR, "_cb_p1.mp4")
bp2 = os.path.join(AROLL_DIR, "_cb_p2.mp4")
bm1 = os.path.join(AROLL_DIR, "_cb_m1.mp4")
bm2 = os.path.join(AROLL_DIR, "_cb_m2.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", cam_b_syn, "-vf", f"select='lt(n,{half})',setpts=N/30/TB", "-fps_mode", "cfr", "-r", "30", "-an", "-c:v", "h264_nvenc", "-preset", "p3", "-cq", "16", bp1], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", cam_b_syn, "-vf", f"select='gte(n,{half})',setpts=N/30/TB", "-fps_mode", "cfr", "-r", "30", "-an", "-c:v", "h264_nvenc", "-preset", "p3", "-cq", "16", bp2], check=True)
pm1 = subprocess.Popen([PY_EXE, "-X", "utf8", MATTE, bp1, bm1])
pm2 = subprocess.Popen([PY_EXE, "-X", "utf8", MATTE, bp2, bm2])
if pm1.wait() != 0 or pm2.wait() != 0:
    raise RuntimeError("Cam B RVM matte failed!")

lst_b = os.path.join(AROLL_DIR, "_cb_concat.txt")
with open(lst_b, "w", encoding="utf-8") as f:
    f.write("file '" + bm1.replace("\\", "/") + "'\nfile '" + bm2.replace("\\", "/") + "'\n")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst_b, "-c", "copy", cam_b_mat], check=True)
for tmp in (bp1, bp2, bm1, bm2, lst_b):
    if os.path.exists(tmp): os.remove(tmp)

# Save side-by-side Cam A vs Cam B comparison sheet!
sheet = Image.new("RGB", (270 * 6, 480 * 2))
mc_a_gr = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
for k in range(6):
    ts = 3.0 + k * 11.5
    fa_png = os.path.join(CHECK_DIR, f"_sa_{k}.png")
    fb_png = os.path.join(CHECK_DIR, f"_sb_{k}.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mc_a_gr,  "-frames:v", "1", fa_png], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", cam_b_syn, "-frames:v", "1", fb_png], check=True)
    ia = Image.open(fa_png).convert("RGB")
    ib = Image.open(fb_png).convert("RGB")
    for im_x, lbl in ((ia, f"CAM A t={ts:.1f}s"), (ib, f"CAM B t={ts:.1f}s (off={frame_offs[int(ts*30)]:+.2f}s)")):
        d = ImageDraw.Draw(im_x)
        for ym in (225, 380, 440, 1036, 1522):
            d.line([(0, ym), (1080, ym)], fill=(255, 220, 40), width=3)
        d.rectangle([10, 10, 520, 58], fill=(16, 20, 32))
        d.text((20, 22), lbl, fill=(255, 255, 255))
    sheet.paste(ia.resize((270, 480), Image.Resampling.LANCZOS), (k * 270, 0))
    sheet.paste(ib.resize((270, 480), Image.Resampling.LANCZOS), (k * 270, 480))
    os.remove(fa_png); os.remove(fb_png)
sp_out = os.path.join(CHECK_DIR, "multicam_sync_sheet.jpg")
sheet.save(sp_out, quality=92)
print(f"[CamB DONE] Conformed & RVM-matted Cam B in {time.time() - t0:.1f}s -> {sp_out}", flush=True)
