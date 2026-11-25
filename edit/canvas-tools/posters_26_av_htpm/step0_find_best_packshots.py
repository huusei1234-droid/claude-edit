# -*- coding: utf-8 -*-
import os, glob
from PIL import Image, ImageDraw

PROJ = r"d:\AI\full studio\projects\av_htpm_26_posters_2211"
AUDIT = os.path.join(PROJ, "audit")
os.makedirs(AUDIT, exist_ok=True)

# 1. Inspect the first 45 photos of Ảnh AV Biển (Đã Chỉnh) (where products stand upright on stone/railings)
bien_dir = r"G:\Other computers\My Computer\hằng thu pharma\04. Ảnh Sự Kiện & Nhà Máy\Ảnh AV Biển (Đã Chỉnh)"
b_files = sorted(glob.glob(os.path.join(bien_dir, "*.jpg")))[:48]
cols = 6
rows = (len(b_files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 320, rows * 260), (24, 24, 24))
draw = ImageDraw.Draw(sheet)
for i, p in enumerate(b_files):
    im = Image.open(p).convert("RGB")
    im.thumbnail((300, 220))
    x, y = (i % cols) * 320 + 10, (i // cols) * 260 + 8
    sheet.paste(im, (x, y))
    draw.text((x, y + 226), os.path.basename(p), fill=(255, 225, 90))
sheet.save(os.path.join(AUDIT, "av_bien_first48.jpg"), quality=88)

# 2. Check existing HTPM PNG/JPG packshots in 02. Ảnh Sản Phẩm (01..09)
ht_prod_dir = r"G:\Other computers\My Computer\hằng thu pharma\02. Ảnh Sản Phẩm"
ht_samples = []
for folder in sorted(os.listdir(ht_prod_dir)):
    fdir = os.path.join(ht_prod_dir, folder)
    if os.path.isdir(fdir) and folder[:2].isdigit():
        pngs = sorted(glob.glob(os.path.join(fdir, "*.png")))
        jpgs = sorted([f for f in glob.glob(os.path.join(fdir, "*.jpg")) + glob.glob(os.path.join(fdir, "*.JPG")) if "00 -" not in f])
        picks = (pngs[:2] + jpgs[:2])[:3]
        for pk in picks:
            ht_samples.append((folder[:18], pk))

cols2 = 5
rows2 = (len(ht_samples) + cols2 - 1) // cols2
sheet2 = Image.new("RGB", (cols2 * 340, rows2 * 300), (35, 35, 35))
draw2 = ImageDraw.Draw(sheet2)
for i, (lbl, p) in enumerate(ht_samples):
    im = Image.open(p)
    bg = Image.new("RGB", im.size, (235, 235, 235))
    if im.mode == "RGBA":
        bg.paste(im, mask=im.split()[3])
    else:
        bg = im.convert("RGB")
    bg.thumbnail((320, 245))
    x, y = (i % cols2) * 340 + 10, (i // cols2) * 300 + 8
    sheet2.paste(bg, (x, y))
    draw2.text((x, y + 255), f"{lbl}\n{os.path.basename(p)} ({im.mode})", fill=(255, 230, 110))
sheet2.save(os.path.join(AUDIT, "htpm_9products_samples.jpg"), quality=88)
print("Saved both packshot audit sheets!")
