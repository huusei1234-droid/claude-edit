import os, subprocess, json
from PIL import Image, ImageDraw

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
SRC_DIR   = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC\16-11-2026\Thư mục mới"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
MATTE_PY  = r"d:\AI\full studio\phong-cach\talking-head\tools\matte.py"
PY_EXE    = r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe"

os.makedirs(AROLL_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

def cut_vertical_30(src_name, t0, t1, out_name, audio_af="pan=mono|c0=c1,highpass=f=90"):
    src_p = os.path.join(SRC_DIR, src_name)
    out_p = os.path.join(AROLL_DIR, out_name)
    dur = t1 - t0
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", src_p,
        "-vf", "scale=1080:1920:flags=lanczos,fps=30",
        "-af", audio_af, "-ar", "48000", "-ac", "2",
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k",
        out_p
    ], check=True)
    print(f"Prepared {out_name} ({dur:.2f}s)", flush=True)
    return out_p

# 1. Cut key A-roll & real B-roll clips
p_s1 = cut_vertical_30("C3938.MP4", 3.20, 8.20, "s1_skit.mp4", audio_af="pan=mono|c0=0.45*c0+0.75*c1,highpass=f=95")
p_s2 = cut_vertical_30("C3942.MP4", 2.12, 11.16, "s2_table.mp4", audio_af="pan=mono|c0=c1,highpass=f=90")
p_s3 = cut_vertical_30("C3948.MP4", 2.08, 6.42, "s3_intro_khang.mp4", audio_af="pan=mono|c0=c1,highpass=f=95")
p_s5 = cut_vertical_30("C3956.MP4", 1.86, 10.66, "s5_gifts.mp4", audio_af="pan=mono|c0=c1,highpass=f=95")
p_s6 = cut_vertical_30("C3957.MP4", 1.40, 3.35, "s6_thumbs.mp4", audio_af="pan=mono|c0=c1,highpass=f=95")

# Clean real audio for s4 ("Hàng loạt câu hỏi...") from C3960.MP4 [0.00 .. 5.95s]
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-ss", "0.00", "-t", "5.95", "-i", os.path.join(SRC_DIR, "C3960.MP4"),
    "-af", "pan=mono|c0=c1,highpass=f=90,loudnorm=I=-16:TP=-1.5:LRA=9",
    "-ar", "48000", "-ac", "1", os.path.join(AROLL_DIR, "s4_questions_vo.wav")
], check=True)
print("Prepared s4_questions_vo.wav (5.95s)", flush=True)

# Real Jar B-rolls (720x1280 -> upscaled cleanly to 1080x1920 @ 30fps, muted)
for fn, t0, dur, out_n in [
    ("1794896747195_7554134916885130862_g3126275282610969305.mp4", 6.0, 6.0, "broll_jar_cut.mp4"),
    ("1794921300510_7554134916885130862_g3126275282610969305.mp4", 0.2, 3.6, "broll_jar_shake.mp4"),
    ("1794921300505_7554134916885130862_g3126275282610969305.mp4", 0.2, 5.8, "broll_jar_pick.mp4"),
]:
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{t0:.2f}", "-t", f"{dur:.2f}",
        "-i", os.path.join(SRC_DIR, fn),
        "-vf", "scale=1080:1920:flags=lanczos,fps=30",
        "-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
        os.path.join(AROLL_DIR, out_n)
    ], check=True)
    print(f"Prepared {out_n}", flush=True)

# 2. Run RVM Person Matting on s2_table.mp4, s3_intro_khang.mp4, s5_gifts.mp4 (and s1_skit.mp4 for behind-title!)
for base in ["s1_skit", "s2_table", "s3_intro_khang", "s5_gifts"]:
    inp = os.path.join(AROLL_DIR, f"{base}.mp4")
    out_m = os.path.join(AROLL_DIR, f"{base}_matte.mp4")
    subprocess.run([PY_EXE, MATTE_PY, inp, out_m], check=True)

# 3. Save geometry inspection sheet (with Y-coordinate ruler every 100px!) for s1_skit, s2_table, s5_gifts, s6_thumbs
ruler_imgs = []
for base, ts in [("s1_skit", 2.5), ("s2_table", 3.0), ("s5_gifts", 3.0), ("s6_thumbs", 1.0)]:
    fp = os.path.join(CHECK_DIR, f"_geo_{base}.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", os.path.join(AROLL_DIR, f"{base}.mp4"), "-frames:v", "1", fp], check=True)
    im = Image.open(fp).convert("RGB")
    dr = ImageDraw.Draw(im)
    for y in range(100, 1900, 100):
        dr.line([(0, y), (1080, y)], fill=(255, 230, 0) if y % 200 == 0 else (0, 220, 255), width=2 if y % 200 == 0 else 1)
        dr.rectangle([4, y - 14, 76, y + 4], fill=(0, 0, 0))
        dr.text((8, y - 12), f"y={y}", fill=(255, 255, 100))
    dr.rectangle([400, 10, 680, 46], fill=(0, 0, 0))
    dr.text((415, 18), base, fill=(255, 120, 160))
    ruler_imgs.append(im.resize((360, 640), Image.Resampling.LANCZOS))
    os.remove(fp)

sheet = Image.new("RGB", (360 * 4, 640))
for i, rim in enumerate(ruler_imgs):
    sheet.paste(rim, (i * 360, 0))
sheet.save(os.path.join(CHECK_DIR, "aroll_geometry_ruler.jpg"), quality=90)
print("Saved aroll_geometry_ruler.jpg!", flush=True)
