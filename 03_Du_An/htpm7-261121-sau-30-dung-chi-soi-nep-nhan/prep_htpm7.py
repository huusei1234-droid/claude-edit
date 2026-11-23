import json, os, shutil, subprocess, time
import numpy as np
from PIL import Image, ImageDraw

SRC_Z     = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\06. Video Quay Gốc\260904 - Chị Hằng Biệt Thự\260904 HTPM KB03 - Sau 30 Tuổi Đừng Chỉ Soi Nếp Nhăn - Góc 1 (Lẻ Góc 2).MP4"
PROJ_DIR  = r"d:\AI\full studio\output\htpm7-261121"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
for d in (AROLL_DIR, CHECK_DIR, MEDIA_DIR, STEMS_DIR):
    os.makedirs(d, exist_ok=True)

PY_EXE     = r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
TRANSCRIBE = r"d:\AI\full studio\phong-cach\talking-head\tools\transcribe.py"
MATTE      = r"d:\AI\full studio\phong-cach\talking-head\tools\matte.py"
LUT_ROSY   = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\01_HTPM_Beauty_Rosy_Skin.cube"

local_src = os.path.join(AROLL_DIR, "_src_kb03_local.mp4")
mc_raw    = os.path.join(AROLL_DIR, "_mc_full.mp4")
mc        = os.path.join(AROLL_DIR, "main_cut.mp4")
mc_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
mc_json   = os.path.join(AROLL_DIR, "main_cut.json")
matte_out = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

t0 = time.time()
print("[0/5] Copying KB03 source from Z: to local D: NVMe...", flush=True)
if not os.path.exists(local_src):
    shutil.copy2(SRC_Z, local_src)
print(f"  -> Copied ({os.path.getsize(local_src)/(1024*1024):.1f} MB) in {time.time() - t0:.1f}s", flush=True)

pr_src = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "stream=index,codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration",
    "-of", "json", local_src
], text=True))
print("[SRC INFO]", json.dumps(pr_src, ensure_ascii=False), flush=True)

print("[1/5] Normalizing KB03 -> 1080x1920 30fps CFR (h264_nvenc)...", flush=True)
# Check source orientation/dimensions first
v_stream = [s for s in pr_src["streams"] if s["codec_type"] == "video"][0]
sw, sh = int(v_stream["width"]), int(v_stream["height"])
vf_norm = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" if (sw, sh) != (1080, 1920) else "null"

subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", local_src,
    "-vf", vf_norm,
    "-r", "30", "-fps_mode", "cfr",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
    mc_raw
], check=True)

cnt_raw = int(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
    "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", mc_raw
], text=True).strip())

tail_start = max(0, cnt_raw - 90)
raw_tail = subprocess.check_output([
    "ffmpeg", "-v", "error", "-i", mc_raw,
    "-vf", f"select='gte(n,{tail_start})',scale=90:160", "-fps_mode", "passthrough",
    "-f", "rawvideo", "-pix_fmt", "gray", "-"
])
tail_arr = np.frombuffer(raw_tail, dtype=np.uint8).reshape((-1, 160, 90))
valid_frames = cnt_raw
for k in range(len(tail_arr) - 1, -1, -1):
    if float(tail_arr[k].mean()) > 12.0:
        valid_frames = min(cnt_raw, tail_start + k + 1)
        break

dur_exact = valid_frames / 30.0
print(f"  -> Raw frames={cnt_raw}, non-black valid frames={valid_frames} ({dur_exact:.3f}s)", flush=True)

if valid_frames < cnt_raw:
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", mc_raw,
        "-frames:v", str(valid_frames), "-t", f"{dur_exact:.6f}",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        mc
    ], check=True)
    os.remove(mc_raw)
else:
    if os.path.exists(mc):
        os.remove(mc)
    os.rename(mc_raw, mc)

if os.path.exists(local_src):
    os.remove(local_src)

subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "3.50", "-i", mc, "-frames:v", "1", os.path.join(AROLL_DIR, "speaker_ref.png")], check=True)

grid = Image.new("RGB", (270 * 6, 480 * 2))
for i in range(12):
    ts = min(dur_exact - 0.25, 0.4 + i * (dur_exact - 0.9) / 11.0)
    fp = os.path.join(CHECK_DIR, f"_r_{i:02d}.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mc, "-frames:v", "1", fp], check=True)
    im = Image.open(fp).convert("RGB")
    d = ImageDraw.Draw(im)
    for y_mark in (205, 320, 380, 440, 750, 1096, 1568, 1602):
        d.line([(0, y_mark), (1080, y_mark)], fill=(255, 220, 40), width=3)
        d.rectangle([8, y_mark - 28, 130, y_mark - 2], fill=(16, 20, 32))
        d.text((14, y_mark - 24), f"y={y_mark}", fill=(255, 235, 110))
    d.rectangle([10, 10, 260, 58], fill=(16, 20, 32))
    d.text((20, 22), f"t={ts:.1f}s", fill=(255, 255, 255))
    grid.paste(im.resize((270, 480), Image.Resampling.LANCZOS), ((i % 6) * 270, (i // 6) * 480))
    os.remove(fp)
grid.save(os.path.join(CHECK_DIR, "raw_sheet.jpg"), quality=92)

lut_tmp = os.path.join(AROLL_DIR, "_rosy.cube")
shutil.copy2(LUT_ROSY, lut_tmp)
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", mc, "-frames:v", str(valid_frames), "-an",
    "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_rosy.cube[bg];[a][bg]blend=all_expr=A*0.45+B*0.55[v]",
    "-map", "[v]", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
    mc_graded
], cwd=AROLL_DIR, check=True)
os.remove(lut_tmp)
print(f"[2/5] GPU RosySkin LUT graded ({valid_frames} frames) in {time.time() - t0:.1f}s!", flush=True)

orig_wav = os.path.join(STEMS_DIR, "orig_input.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-ar", "44100", "-ac", "2", orig_wav], check=True)

half = valid_frames // 2
p1 = os.path.join(AROLL_DIR, "_mc_p1.mp4")
p2 = os.path.join(AROLL_DIR, "_mc_p2.mp4")
m1 = os.path.join(AROLL_DIR, "_mc_m1.mp4")
m2 = os.path.join(AROLL_DIR, "_mc_m2.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-vf", f"select='lt(n,{half})',setpts=N/30/TB", "-fps_mode", "cfr", "-r", "30", "-an", "-c:v", "h264_nvenc", "-preset", "p3", "-cq", "16", p1], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-vf", f"select='gte(n,{half})',setpts=N/30/TB", "-fps_mode", "cfr", "-r", "30", "-an", "-c:v", "h264_nvenc", "-preset", "p3", "-cq", "16", p2], check=True)

print("[3/5] Launching Whisper + Demucs GPU + 2x RVM in parallel...", flush=True)
proc_wh  = subprocess.Popen([PY_EXE, "-X", "utf8", TRANSCRIBE, mc, mc_json, "--lang", "vi", "--cpu", "--prompt", "Hằng Thu Pharma, nếp nhăn, lão hóa, nội tiết tố, collagen, sắc tố, nám, tàn nhang, phụ khoa, chị em, tuổi 30"])
proc_dem = subprocess.Popen([PY_EXE, "-m", "demucs.separate", "--two-stems", "vocals", "-n", "htdemucs", "-o", os.path.join(STEMS_DIR, "demucs_out"), orig_wav])
proc_m1  = subprocess.Popen([PY_EXE, "-X", "utf8", MATTE, p1, m1])
proc_m2  = subprocess.Popen([PY_EXE, "-X", "utf8", MATTE, p2, m2])

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
print(f"[4/5] Verified RVM Matte frames={mcnt}/{valid_frames}!", flush=True)

# Measure original non-speech RMS (dBFS) + Demucs stems!
raw_orig = subprocess.check_output(["ffmpeg", "-v", "error", "-i", orig_wav, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"])
arr_orig = np.frombuffer(raw_orig, dtype=np.float32).reshape((-1, 2))
voc_p = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "vocals.wav")
bgm_p = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "no_vocals.wav")
raw_voc = subprocess.check_output(["ffmpeg", "-v", "error", "-i", voc_p, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"])
arr_voc = np.frombuffer(raw_voc, dtype=np.float32).reshape((-1, 2))
raw_bgm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", bgm_p, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"])
arr_bgm = np.frombuffer(raw_bgm, dtype=np.float32).reshape((-1, 2))

n_min = min(len(arr_orig), len(arr_voc), len(arr_bgm))
hop = 2400  # 50ms at 48kHz
nh = n_min // hop
voc_hops = np.sqrt(np.mean(arr_voc[:nh*hop].reshape((nh, hop, 2))**2, axis=(1, 2)))
orig_hops = np.sqrt(np.mean(arr_orig[:nh*hop].reshape((nh, hop, 2))**2, axis=(1, 2)))
non_sp_mask = voc_hops < 0.008
non_sp_rms = float(np.sqrt(np.mean(orig_hops[non_sp_mask]**2))) if np.any(non_sp_mask) else float(np.min(orig_hops))
non_sp_dbfs = 20.0 * np.log10(max(1e-7, non_sp_rms))
bgm_dbfs = 20.0 * np.log10(max(1e-7, float(np.sqrt(np.mean(arr_bgm**2)))))
voc_dbfs = 20.0 * np.log10(max(1e-7, float(np.sqrt(np.mean(arr_voc**2)))))
print(f"[AUDIO CHECK] Orig Non-Speech RMS = {non_sp_dbfs:.2f} dBFS | Demucs Vocals = {voc_dbfs:.2f} dBFS | Demucs No-Vocals = {bgm_dbfs:.2f} dBFS", flush=True)

tr = json.load(open(mc_json, "r", encoding="utf-8"))
print(f"\n=== TRANSCRIPT ({len(tr['segments'])} segments, {valid_frames} frames = {dur_exact:.3f}s) ===")
for seg in tr["segments"]:
    print(f"  [{seg['start']:5.2f} - {seg['end']:5.2f}] {seg['text'].strip()}")
