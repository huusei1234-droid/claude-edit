import json, os, shutil, subprocess, time, wave
import numpy as np
from PIL import Image, ImageDraw

PROJ_DIR  = r"C:\AI\full studio\output\htpm-kb04-261123"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
for d in (AROLL_DIR, CHECK_DIR, MEDIA_DIR, STEMS_DIR):
    os.makedirs(d, exist_ok=True)

PY_EXE     = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
TRANSCRIBE = r"C:\AI\full studio\phong-cach\talking-head\tools\transcribe.py"
MATTE      = r"C:\AI\full studio\phong-cach\talking-head\tools\matte.py"
LUT_ROSY   = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\01_HTPM_Beauty_Rosy_Skin.cube"

ENV = os.environ.copy()
ENV["HF_HOME"]          = r"C:\AI\full studio_data\ai-cache\huggingface"
ENV["TORCH_HOME"]       = r"C:\AI\full studio_data\ai-cache\torch"
ENV["XDG_CACHE_HOME"]   = r"C:\AI\full studio_data\ai-cache"
ENV["NPM_CONFIG_CACHE"] = r"C:\AI\full studio_data\npm-cache"
ENV["PIP_CACHE_DIR"]    = r"C:\AI\full studio_data\pip-cache"
ENV["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

raw_src   = os.path.join(AROLL_DIR, "raw_camera_kb04.mp4")
norm_full = os.path.join(AROLL_DIR, "_norm_30fps_full.mp4")
mc        = os.path.join(AROLL_DIR, "main_cut.mp4")
mc_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
mc_json   = os.path.join(AROLL_DIR, "main_cut.json")
matte_out = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

# Exact 30fps kept frame ranges [f_start, f_end_exclusive):
# 1. [555,  821): 18.500s -> 27.367s (266 frames) — Hook + "...chị em" (cuts stumble "cạ,")
# 2. [838, 2063): 27.933s -> 68.767s (1225 frames) — "càng thấy hấp dẫn... Hằng cũng kinh doanh White Skin." (cuts false start #1)
# 3. [2144,2605): 71.467s -> 86.833s (461 frames) — "Nhưng Hằng không muốn chị em mua nó... chỉ để đẹp nhanh." (cuts false start #2)
# 4. [2759,3011): 91.967s ->100.367s (252 frames) — "Nếu chị em muốn Hằng nói thẳng... thì comment NÓI THẬT!" (cuts BTS post-roll)
KEPT_SEGMENTS = [
    (555,   821),
    (838,  2063),
    (2144, 2605),
    (2759, 3011),
]
TOTAL_FRAMES = sum(b - a for a, b in KEPT_SEGMENTS)  # 2204 frames = 73.466667s
DUR_EXACT    = TOTAL_FRAMES / 30.0
SR           = 48000

t0 = time.time()
print(f"[1/5] Normalizing raw Sony 59.94fps -> 1080x1920 30fps CFR...", flush=True)
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", raw_src,
    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
    "-r", "30", "-fps_mode", "cfr", "-an",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
    norm_full
], check=True)

sel_expr = "+".join(f"between(n,{a},{b-1})" for a, b in KEPT_SEGMENTS)
vid_only = os.path.join(AROLL_DIR, "_mc_vid_only.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", norm_full,
    "-vf", f"select='{sel_expr}',setpts=N/30/TB",
    "-r", "30", "-fps_mode", "cfr", "-an",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
    vid_only
], check=True)
os.remove(norm_full)

# Build click-free 48kHz stereo audio with 35ms cosine equal-power crossfades across all 3 internal splices!
raw_wav = os.path.join(STEMS_DIR, "raw_camera_kb04.wav")
with wave.open(raw_wav, "rb") as wf:
    arr = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).reshape((-1, 2)).astype(np.float32) / 32768.0

XF = int(0.035 * SR)  # 1680 samples = 35ms
merged = None
for idx, (fa, fb) in enumerate(KEPT_SEGMENTS):
    ia = int(round((fa / 30.0) * SR))
    ib = int(round((fb / 30.0) * SR))
    if idx == 0:
        merged = arr[ia:ib + XF].copy()
    else:
        part = arr[ia:ib + (XF if idx + 1 < len(KEPT_SEGMENTS) else 0)].copy()
        u = np.linspace(0.0, 1.0, XF, dtype=np.float32)[:, None]
        w1 = 0.5 * (1.0 + np.cos(np.pi * u))
        merged[-XF:] = merged[-XF:] * w1 + part[:XF] * (1.0 - w1)
        merged = np.vstack([merged, part[XF:]])

target_samples = int(round(DUR_EXACT * SR))
if len(merged) < target_samples:
    merged = np.vstack([merged, np.zeros((target_samples - len(merged), 2), dtype=np.float32)])
else:
    merged = merged[:target_samples]

# Verify if one channel is louder or mono-split; center cleanly if needed
l_rms = float(np.sqrt(np.mean(merged[:, 0] ** 2)))
r_rms = float(np.sqrt(np.mean(merged[:, 1] ** 2)))
print(f"  -> Sliced audio L_rms={l_rms:.5f}, R_rms={r_rms:.5f}", flush=True)
if max(l_rms, r_rms) > 2.2 * max(1e-6, min(l_rms, r_rms)):
    dom = 0 if l_rms >= r_rms else 1
    merged[:, 0] = merged[:, dom]
    merged[:, 1] = merged[:, dom]
    print(f"  -> Balanced single wireless mic channel {dom} -> dual-mono centered stereo!", flush=True)

orig_wav = os.path.join(STEMS_DIR, "orig_input.wav")
pcm16 = (np.clip(merged, -0.99, 0.99) * 32767.0).astype(np.int16)
with wave.open(orig_wav, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(pcm16.tobytes())

subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", vid_only, "-i", orig_wav,
    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
    mc
], check=True)
os.remove(vid_only)

cnt_mc = int(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
    "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", mc
], text=True).strip())
print(f"  -> Verified main_cut.mp4 frames={cnt_mc}/{TOTAL_FRAMES} ({DUR_EXACT:.3f}s)", flush=True)
assert cnt_mc == TOTAL_FRAMES

# Speaker reference portrait (at clean bright smile t=3.20s) + 12-panel ruler sheet!
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "3.20", "-i", mc, "-frames:v", "1", os.path.join(AROLL_DIR, "speaker_ref.png")], check=True)

grid = Image.new("RGB", (270 * 6, 480 * 2))
for i in range(12):
    ts = min(DUR_EXACT - 0.3, 0.5 + i * (DUR_EXACT - 1.0) / 11.0)
    fp = os.path.join(CHECK_DIR, f"_r_{i:02d}.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mc, "-frames:v", "1", fp], check=True)
    im = Image.open(fp).convert("RGB")
    d = ImageDraw.Draw(im)
    for y_mark in (205, 320, 410, 460, 520, 1096, 1568, 1602):
        d.line([(0, y_mark), (1080, y_mark)], fill=(255, 220, 40), width=3)
        d.rectangle([8, y_mark - 28, 130, y_mark - 2], fill=(16, 20, 32))
        d.text((14, y_mark - 24), f"y={y_mark}", fill=(255, 235, 110))
    d.rectangle([10, 10, 260, 58], fill=(16, 20, 32))
    d.text((20, 22), f"t={ts:.1f}s", fill=(255, 255, 255))
    grid.paste(im.resize((270, 480), Image.Resampling.LANCZOS), ((i % 6) * 270, (i // 6) * 480))
    os.remove(fp)
grid.save(os.path.join(CHECK_DIR, "raw_sheet.jpg"), quality=92)

# 2. Grade with 01_HTPM_Beauty_Rosy_Skin.cube @ 55%
lut_tmp = os.path.join(AROLL_DIR, "_rosy.cube")
shutil.copy2(LUT_ROSY, lut_tmp)
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", mc, "-frames:v", str(TOTAL_FRAMES), "-an",
    "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_rosy.cube[bg];[a][bg]blend=all_expr=A*0.45+B*0.55[v]",
    "-map", "[v]", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
    mc_graded
], cwd=AROLL_DIR, check=True)
os.remove(lut_tmp)
print(f"[2/5] Graded RosySkin ({TOTAL_FRAMES} frames) in {time.time() - t0:.1f}s!", flush=True)

# 3. Parallel Whisper (--cpu) + Demucs GPU + 2x RVM ONNX!
half = TOTAL_FRAMES // 2
p1 = os.path.join(AROLL_DIR, "_mc_p1.mp4")
p2 = os.path.join(AROLL_DIR, "_mc_p2.mp4")
m1 = os.path.join(AROLL_DIR, "_mc_m1.mp4")
m2 = os.path.join(AROLL_DIR, "_mc_m2.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-vf", f"select='lt(n,{half})',setpts=N/30/TB", "-fps_mode", "cfr", "-r", "30", "-an", "-c:v", "h264_nvenc", "-preset", "p3", "-cq", "16", p1], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-vf", f"select='gte(n,{half})',setpts=N/30/TB", "-fps_mode", "cfr", "-r", "30", "-an", "-c:v", "h264_nvenc", "-preset", "p3", "-cq", "16", p2], check=True)

print("[3/5] Launching Whisper + Demucs + 2x RVM in parallel...", flush=True)
proc_wh  = subprocess.Popen([
    PY_EXE, "-X", "utf8", TRANSCRIBE, mc, mc_json, "--lang", "vi", "--cpu",
    "--prompt", "Hằng Thu Pharma, Nguyễn Thị Hằng, White Skin, trắng bật tông sau 7 ngày, chống nắng, di truyền, ánh nắng, giấc ngủ, dinh dưỡng, stress, thành phần, nói thật"
], env=ENV)
proc_dem = subprocess.Popen([
    PY_EXE, "-m", "demucs.separate", "--two-stems", "vocals", "-n", "htdemucs",
    "-o", os.path.join(STEMS_DIR, "demucs_out"), orig_wav
], env=ENV)
proc_m1  = subprocess.Popen([PY_EXE, "-X", "utf8", MATTE, p1, m1], env=ENV)
proc_m2  = subprocess.Popen([PY_EXE, "-X", "utf8", MATTE, p2, m2], env=ENV)

rw   = proc_wh.wait()
rdem = proc_dem.wait()
rm1  = proc_m1.wait()
rm2  = proc_m2.wait()
if any(rc != 0 for rc in (rw, rdem, rm1, rm2)):
    raise RuntimeError(f"Subprocess failed: wh={rw}, dem={rdem}, m1={rm1}, m2={rm2}")

lst = os.path.join(AROLL_DIR, "_m_concat.txt")
with open(lst, "w", encoding="utf-8") as f:
    p_m1 = m1.replace("\\", "/")
    p_m2 = m2.replace("\\", "/")
    f.write(f"file '{p_m1}'\nfile '{p_m2}'\n")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", matte_out], check=True)
for tmp in (p1, p2, m1, m2, lst):
    if os.path.exists(tmp):
        os.remove(tmp)

mcnt = int(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
    "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", matte_out
], text=True).strip())
print(f"[4/5] Verified RVM Matte frames={mcnt}/{TOTAL_FRAMES} in {time.time() - t0:.1f}s!", flush=True)
assert mcnt == TOTAL_FRAMES
print("[5/5] ALL PREP COMPLETED SUCCESSFULLY!", flush=True)
