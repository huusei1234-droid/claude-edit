import os, sys, json, subprocess
from PIL import Image, ImageDraw

vdir = sys.argv[1]
qc_p = sys.argv[2]
clips = sorted([f for f in os.listdir(vdir) if f.endswith(".mp4")])
if not clips:
    print("NO_CLIPS")
    sys.exit(0)
sheet = Image.new("RGB", (len(clips) * 270, 520), (16, 22, 28))
draw = ImageDraw.Draw(sheet)
for i, fn in enumerate(clips):
    p = os.path.join(vdir, fn)
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration", "-of", "json", p
    ]).decode()
    st = json.loads(out)["streams"][0]
    dur = float(st.get("duration", 0))
    w, h, fps = st["width"], st["height"], st["r_frame_rate"]
    print(f"{fn}: {w}x{h} fps={fps} dur={dur:.3f}s")
    tmp = os.path.join(vdir, f"_qc_{fn}.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{min(1.5, dur * 0.45):.2f}", "-i", p, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB")
    im.thumbnail((256, 460), Image.Resampling.LANCZOS)
    sheet.paste(im, (i * 270 + (270 - im.width) // 2, 10))
    draw.text((i * 270 + 10, 480), f"{fn} ({dur:.2f}s)", fill=(255, 230, 120))
    os.remove(tmp)
sheet.save(qc_p, quality=92)
print("SAVED_QC:", qc_p)
