import json, os, shutil, subprocess, time
import numpy as np
from PIL import Image, ImageDraw

SRC_MP4   = r"C:\Users\Hang thu\Downloads\HTPM.mp4"
PROJ_DIR  = r"d:\AI\full studio\output\htpm6-261121"
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

mc_raw    = os.path.join(AROLL_DIR, "_mc_full.mp4")
mc        = os.path.join(AROLL_DIR, "main_cut.mp4")
mc_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
mc_json   = os.path.join(AROLL_DIR, "main_cut.json")
matte_out = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

t0 = time.time()
print("[1/5] Normalizing Downloads\\HTPM.mp4 -> 30fps CFR...", flush=True)
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", SRC_MP4,
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
    if os.path.exists(mc): os.remove(mc)
    os.rename(mc_raw, mc)

subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "3.50", "-i", mc, "-frames:v", "1", os.path.join(AROLL_DIR, "speaker_ref.png")], check=True)

grid = Image.new("RGB", (270 * 6, 480 * 2))
for i in range(12):
    ts = min(dur_exact - 0.25, 0.4 + i * (dur_exact - 0.9) / 11.0)
    fp = os.path.join(CHECK_DIR, f"_r_{i:02d}.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mc, "-frames:v", "1", fp], check=True)
    im = Image.open(fp).convert("RGB")
    d = ImageDraw.Draw(im)
    for y_mark in (220, 320, 380, 440, 750, 1036, 1522, 1590):
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
proc_wh  = subprocess.Popen([PY_EXE, "-X", "utf8", TRANSCRIBE, mc, mc_json, "--lang", "vi", "--cpu", "--prompt", "Hằng Thu Pharma, nội tiết, phụ khoa, chị em, sức khỏe, chu kỳ, kinh nguyệt, sinh sản"])
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
    if os.path.exists(tmp): os.remove(tmp)

mcnt = int(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
    "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", matte_out
], text=True).strip())
print(f"[4/5] Verified RVM Matte frames={mcnt}/{valid_frames}!", flush=True)

voc_p = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "vocals.wav")
bgm_p = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "no_vocals.wav")
for lbl, ap in [("VOCALS", voc_p), ("NO_VOCALS", bgm_p)]:
    raw_a = subprocess.check_output(["ffmpeg", "-v", "error", "-i", ap, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"])
    arr_a = np.frombuffer(raw_a, dtype=np.float32).reshape((-1, 2))
    print(f"  [{lbl}] L_rms={np.sqrt(np.mean(arr_a[:,0]**2)):.4f} R_rms={np.sqrt(np.mean(arr_a[:,1]**2)):.4f}")

tr = json.load(open(mc_json, "r", encoding="utf-8"))
print(f"\n=== TRANSCRIPT ({len(tr['segments'])} segments, {valid_frames} frames = {dur_exact:.3f}s) ===")
for seg in tr["segments"]:
    print(f"  [{seg['start']:5.2f} - {seg['end']:5.2f}] {seg['text'].strip()}")
