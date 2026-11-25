import os, sys, json, subprocess
from PIL import Image, ImageDraw

mp4_path = sys.argv[1]
out_jpg = sys.argv[2]
safe_mask = r"d:\AI\full studio\edit\canvas-tools\vung_an_toan_tiktok_reels_1080x1920.png"

pr = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate,codec_type",
    "-of", "json", mp4_path
]).decode())
dur = float(pr["format"]["duration"])
vstream = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
astream = [s for s in pr["streams"] if s["codec_type"] == "audio"]
print(f"MP4: {os.path.basename(mp4_path)} | {vstream['width']}x{vstream['height']} | fps={vstream['r_frame_rate']} | dur={dur:.2f}s | audio_streams={len(astream)}")

times = [0.5, 2.2, 5.5, 11.8, 18.5, 23.2, 28.5, 36.0, 41.5, 44.5, max(0.5, dur - 2.0), max(0.5, dur - 0.5)]
cols, rows = 4, 3
cw, ch = 300, 560
sheet = Image.new("RGB", (cols * cw, rows * ch), (14, 18, 24))
draw = ImageDraw.Draw(sheet)

mask_im = None
if os.path.exists(safe_mask):
    mask_im = Image.open(safe_mask).convert("RGBA")

tmp_dir = os.path.dirname(os.path.abspath(out_jpg))
for idx, t in enumerate(times):
    tt = min(dur - 0.1, t)
    tf = os.path.join(tmp_dir, f"_qa_f_{idx}.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{tt:.2f}", "-i", mp4_path, "-frames:v", "1", tf], check=True)
    im = Image.open(tf).convert("RGBA")
    # Overlay faint red boundary guide of TikTok/Reels forbidden zones (Y<248, Y>1548, X<52, X>1026, right-bottom X>886 & Y>860)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, 1080, 248], fill=(255, 0, 0, 38))
    od.rectangle([0, 1548, 1080, 1920], fill=(255, 0, 0, 38))
    od.rectangle([0, 248, 52, 1548], fill=(255, 0, 0, 38))
    od.rectangle([1026, 248, 1080, 860], fill=(255, 0, 0, 38))
    od.rectangle([886, 860, 1080, 1548], fill=(255, 0, 0, 48))
    im = Image.alpha_composite(im, ov).convert("RGB")
    im.thumbnail((cw - 16, ch - 44), Image.Resampling.LANCZOS)
    x = (idx % cols) * cw + (cw - im.width) // 2
    y = (idx // cols) * ch + 8
    sheet.paste(im, (x, y))
    draw.text(((idx % cols) * cw + 12, (idx // cols) * ch + ch - 30), f"t = {tt:.2f}s", fill=(255, 232, 120))
    os.remove(tf)

sheet.save(out_jpg, quality=92)
print("SAVED_FINAL_QA:", out_jpg)
