# -*- coding: utf-8 -*-
"""
Step 1: Prepare crisp Studio RGBA Cutouts (2 distinct packshot angles/combos per product = 26 cutouts)
+ 2 Official Brand Logos (An Vượng Pharma & Hằng Thu Pharma) for all 13 products.
"""
import os, sys, glob, shutil
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from cutout_product_png import ISNetCutout

PROJ = r"d:\AI\full studio\projects\av_htpm_26_posters_2211"
CUT_DIR = os.path.join(PROJ, "assets", "cutouts")
AUDIT_DIR = os.path.join(PROJ, "audit")
os.makedirs(CUT_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)

HT_ROOT = r"G:\Other computers\My Computer\hằng thu pharma"
HT_PROD = os.path.join(HT_ROOT, "02. Ảnh Sản Phẩm")
AV_BIEN = os.path.join(HT_ROOT, "04. Ảnh Sự Kiện & Nhà Máy", "Ảnh AV Biển (Đã Chỉnh)")
AV_TLH  = r"G:\Other computers\My Computer\Document HT Media\TLH\An vượng"

_isnet = None
def get_isnet():
    global _isnet
    if _isnet is None:
        _isnet = ISNetCutout()
    return _isnet

def trim_rgba(im: Image.Image, pad: int = 10) -> Image.Image:
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 20)
    if len(xs) == 0:
        return im
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(im.width, int(xs.max()) + 1 + pad)
    y1 = min(im.height, int(ys.max()) + 1 + pad)
    return im.crop((x0, y0, x1, y1))

def clean_cutout_edges(im_rgba: Image.Image, unwhite_bg: float = 242.0, erode_px: int = 1) -> Image.Image:
    arr = np.array(im_rgba, dtype=np.float32)
    rgb = arr[:, :, :3]
    a = arr[:, :, 3] / 255.0

    if erode_px > 0:
        a_u8 = (a * 255.0).astype(np.uint8)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        a_eroded = cv2.erode(a_u8, k, iterations=erode_px)
        a_soft = cv2.GaussianBlur(a_eroded, (3, 3), 0.65) / 255.0
        a = np.minimum(a, a_soft * 1.04)

    a_clean = np.clip((a - 0.08) / 0.86, 0.0, 1.0)
    edge = (a_clean > 0.04) & (a_clean < 0.90)
    denom = np.maximum(a_clean[:, :, None], 0.25)
    unwhite = (rgb - (1.0 - a_clean[:, :, None]) * unwhite_bg) / denom
    rgb_out = np.where(edge[:, :, None], np.clip(unwhite, 0.0, 255.0), rgb)

    # Keep only major connected components (> 1.5% of max component area) to strip stray sand/pebbles
    mask_bin = (a_clean > 0.15).astype(np.uint8)
    num_lbl, lbls, stats, _ = cv2.connectedComponentsWithStats(mask_bin, connectivity=8)
    if num_lbl > 2:
        areas = stats[1:, cv2.CC_STAT_AREA]
        max_area = int(areas.max())
        keep = np.zeros_like(mask_bin, dtype=np.float32)
        for idx in range(1, num_lbl):
            if stats[idx, cv2.CC_STAT_AREA] >= max_area * 0.025:
                keep[lbls == idx] = 1.0
        keep = cv2.GaussianBlur(keep, (5, 5), 0.9)
        a_clean = a_clean * np.clip(keep * 1.15, 0.0, 1.0)

    out = np.dstack([rgb_out, a_clean * 255.0]).astype(np.uint8)
    return trim_rgba(Image.fromarray(out, "RGBA"))

def cutout_from_photo(src_path: str, crop_rel=None, max_side: int = 1900, unwhite: float = 225.0) -> Image.Image:
    im = Image.open(src_path)
    if im.mode == "RGBA":
        amin, amax = im.getchannel("A").getextrema()
        if amin < 20 and amax > 235:
            im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
            r, g, b, a = im.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb).enhance(1.18)).enhance(1.04)
            return clean_cutout_edges(Image.merge("RGBA", (*rgb.split(), a)), unwhite_bg=248.0, erode_px=0)

    rgb = im.convert("RGB")
    if crop_rel is not None:
        w, h = rgb.size
        x0, y0, x1, y1 = crop_rel
        rgb = rgb.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
    rgb.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    rgb = ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb).enhance(1.20)).enhance(1.05)
    cut = get_isnet().remove_bg(rgb, trim_transparent=True)
    return clean_cutout_edges(cut, unwhite_bg=unwhite, erode_px=1)

# 1. Prepare Official Logos
# 1a. An Vượng Pharma Logo (Logo AN Vượng Pharma Xanh Vàng.png has dark background -> extract gold & emerald cleanly, plus create a white+gold dark-bg version!)
av_logo_src = os.path.join(AV_TLH, "Logo AN Vượng Pharma Xanh Vàng.png")
av_im = Image.open(av_logo_src).convert("RGBA")
arr = np.array(av_im, dtype=np.float32)
rgb = arr[:, :, :3]
lum = rgb.max(axis=2)
# Background in Logo AN Vượng Pharma Xanh Vàng.png is black (0,0,0)
alpha = np.clip((lum - 14.0) / 42.0, 0.0, 1.0)
# Un-black edge pixels so zero dark halo!
denom = np.maximum(alpha[:, :, None], 0.18)
rgb_clean = np.clip(rgb / denom, 0.0, 255.0)
# Also create a high-contrast LUXURY DARK-BG version where dark-emerald text is brightened to crisp Ivory-White & Gold (just like CT Hằng's AV PROTEIN sample!)
r, g, b = rgb_clean[:, :, 0], rgb_clean[:, :, 1], rgb_clean[:, :, 2]
is_gold = (r > 135) & (g > 95) & ((r - b) > 45)
# Brighten non-gold (emerald green letters) into luminous white-mint so it pops 100% on deep emerald backgrounds!
r_lux = np.where(is_gold, np.clip(r * 1.12 + 18, 0, 255), 248.0)
g_lux = np.where(is_gold, np.clip(g * 1.10 + 14, 0, 255), 252.0)
b_lux = np.where(is_gold, np.clip(b * 1.02 + 5, 0, 255), 245.0)
av_logo_on_dark = trim_rgba(Image.fromarray(np.dstack([r_lux, g_lux, b_lux, alpha * 255.0]).astype(np.uint8), "RGBA"))
av_logo_on_dark.save(os.path.join(CUT_DIR, "logo_an_vuong_on_dark.png"))

av_logo_orig = trim_rgba(Image.fromarray(np.dstack([rgb_clean, alpha * 255.0]).astype(np.uint8), "RGBA"))
av_logo_orig.save(os.path.join(CUT_DIR, "logo_an_vuong_orig.png"))

# 1b. Hằng Thu Pharma Official Logo
ht_logo_src = os.path.join(HT_PROD, "Logo & Ảnh Mẫu Thương Hiệu", "ht_logo_official.png")
shutil.copy2(ht_logo_src, os.path.join(CUT_DIR, "logo_hang_thu.png"))

# 2. Check best Ngọc Long Hoàn & Gel Phụ Khang files first
nlh_dir = os.path.join(HT_PROD, "07. Ngọc Long Hoàn")
nlh_dsc = sorted(glob.glob(os.path.join(nlh_dir, "DSC088*.jpg")))
print("Ngoc Long Hoan DSC088*:", [os.path.basename(x) for x in nlh_dsc])
gpk_dir = os.path.join(HT_PROD, "09. Gel Phụ Khang")
gpk_pngs = sorted(glob.glob(os.path.join(gpk_dir, "*.png")))
print("Gel Phu Khang PNGs:", [os.path.basename(x) for x in gpk_pngs])

# 3. Cut out all 4 An Vượng Pharma products (2 distinct angles/combos each)
AV_JOBS = [
    # AV01: AV PROTEIN (Box upright 3/4 + Box warm angle; we'll also composite crisp stick sachet alongside!)
    ("av01_protein_a", os.path.join(AV_BIEN, "DSC09523.jpg"), (0.25, 0.08, 0.76, 0.94), 195.0),
    ("av01_protein_b", os.path.join(AV_BIEN, "DSC09608.jpg"), (0.28, 0.14, 0.74, 0.92), 195.0),
    # AV02: BOJOMI (DSC09547 has Box + 2 upright sachets! DSC09536 has hero 3/4 Box + DSC09587 upright sachet)
    ("av02_bojomi_a",  os.path.join(AV_BIEN, "DSC09547.jpg"), (0.24, 0.10, 0.76, 0.92), 195.0),
    ("av02_bojomi_b",  os.path.join(AV_BIEN, "DSC09536.jpg"), (0.28, 0.08, 0.74, 0.94), 195.0),
    ("av02_bojomi_stick", os.path.join(AV_BIEN, "DSC09587.jpg"), (0.35, 0.06, 0.66, 0.95), 190.0),
    # AV03: COLLAMELA (DSC09558 Box + foreground sachet; DSC09577 3/4 Box + DSC09592 sachet)
    ("av03_collamela_a", os.path.join(AV_BIEN, "DSC09558.jpg"), (0.14, 0.16, 0.80, 0.92), 205.0),
    ("av03_collamela_b", os.path.join(AV_BIEN, "DSC09577.jpg"), (0.26, 0.14, 0.76, 0.90), 200.0),
    # AV04: ANVUONG CURCUMILK PHYTO (DSC09557 Box + 2 upright sachets! DSC09530 3/4 Box + DSC09588 upright sachet)
    ("av04_curcumilk_a", os.path.join(AV_BIEN, "DSC09557.jpg"), (0.20, 0.08, 0.76, 0.92), 195.0),
    ("av04_curcumilk_b", os.path.join(AV_BIEN, "DSC09530.jpg"), (0.24, 0.10, 0.74, 0.93), 195.0),
    ("av04_curcumilk_stick", os.path.join(AV_BIEN, "DSC09588.jpg"), (0.35, 0.05, 0.65, 0.96), 190.0),
]

for name, path, crop_rel, unw in AV_JOBS:
    out_p = os.path.join(CUT_DIR, f"{name}.png")
    im = cutout_from_photo(path, crop_rel=crop_rel, max_side=1800, unwhite=unw)
    im.save(out_p)
    print(f"[AV] Saved {name}.png -> {im.size}")

# 4. Cut out all 9 Hằng Thu Pharma products (2 distinct angles/combos each)
HT_JOBS = [
    ("ht01_dieu_kinh_a",    os.path.join(HT_PROD, "01. Điều Kinh Bổ Trứng", "DSC04761.png"), None, 248.0),
    ("ht01_dieu_kinh_b",    os.path.join(HT_PROD, "01. Điều Kinh Bổ Trứng", "DSC04758.png"), None, 248.0),
    ("ht02_lt_plus_a",      os.path.join(HT_PROD, "02. Viên Đặt Phụ Khoa LT Plus", "DSC04649.png"), None, 248.0),
    ("ht02_lt_plus_b",      os.path.join(HT_PROD, "02. Viên Đặt Phụ Khoa LT Plus", "DSC04627.png"), None, 248.0),
    ("ht03_da_day_a",       os.path.join(HT_PROD, "03. Dạ Dày HT", "DSC04657.png"), None, 248.0),
    ("ht03_da_day_b",       os.path.join(HT_PROD, "03. Dạ Dày HT", "DSC04655.png"), None, 248.0),
    ("ht04_romance_vip_a",  os.path.join(HT_PROD, "04. Dung Dịch Vệ Sinh Romance VIP", "DSC04698.png"), None, 248.0),
    ("ht04_romance_vip_b",  os.path.join(HT_PROD, "04. Dung Dịch Vệ Sinh Romance VIP", "DSC04704.png"), None, 248.0),
    ("ht05_khit_hong_a",    os.path.join(HT_PROD, "05. Viên Đặt Phụ Khoa (Hộp Xanh)", "DSC04746.png"), None, 248.0),
    ("ht05_khit_hong_b",    os.path.join(HT_PROD, "05. Viên Đặt Phụ Khoa (Hộp Xanh)", "DSC04730.png"), None, 248.0),
    ("ht06_romance_love_a", os.path.join(HT_PROD, "Logo & Ảnh Mẫu Thương Hiệu", "SP_ROMANCE_LOVE_CUTOUT.png"), None, 248.0),
    ("ht06_romance_love_b", os.path.join(HT_PROD, "06. Viên Dưỡng Tử Cung Romance Love", "DSC04773.png"), None, 248.0),
    ("ht07_ngoc_long_a",    os.path.join(HT_PROD, "07. Ngọc Long Hoàn", "DSC08861.jpg"), (0.12, 0.08, 0.88, 0.95), 245.0),
    ("ht07_ngoc_long_b",    os.path.join(HT_PROD, "07. Ngọc Long Hoàn", "DSC08867.jpg"), (0.12, 0.08, 0.88, 0.95), 245.0),
    ("ht08_white_skin_a",   os.path.join(HT_PROD, "Logo & Ảnh Mẫu Thương Hiệu", "SP_WHITESKIN_COMBO_CUTOUT.png"), None, 248.0),
    ("ht08_white_skin_b",   os.path.join(HT_PROD, "08. Viên Uống Trắng Da White Skin", "A1_08797.jpg"), (0.18, 0.06, 0.82, 0.95), 245.0),
    ("ht09_gel_pk_a",       os.path.join(HT_PROD, "09. Gel Phụ Khang", "DSC04690.png"), None, 248.0),
    ("ht09_gel_pk_b",       os.path.join(HT_PROD, "09. Gel Phụ Khang", "DSC04671.png"), None, 248.0),
]

for name, path, crop_rel, unw in HT_JOBS:
    out_p = os.path.join(CUT_DIR, f"{name}.png")
    im = cutout_from_photo(path, crop_rel=crop_rel, max_side=1800, unwhite=unw)
    im.save(out_p)
    print(f"[HT] Saved {name}.png -> {im.size}")

# 5. Render QA Checkerboard Contact Sheet of all cutouts
all_cuts = sorted(glob.glob(os.path.join(CUT_DIR, "*.png")))
cols = 6
rows = (len(all_cuts) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 320, rows * 340), (42, 46, 52))
draw = ImageDraw.Draw(sheet)
for i, p in enumerate(all_cuts):
    im = Image.open(p).convert("RGBA")
    # Checkerboard tile behind cutout to verify clean alpha
    tile = Image.new("RGBA", (300, 280), (65, 72, 80, 255))
    td = ImageDraw.Draw(tile)
    for cy in range(0, 280, 20):
        for cx in range(0, 300, 20):
            if ((cx // 20) + (cy // 20)) % 2 == 0:
                td.rectangle([cx, cy, cx + 19, cy + 19], fill=(82, 90, 100, 255))
    im.thumbnail((280, 260), Image.Resampling.LANCZOS)
    ox = (300 - im.width) // 2
    oy = (280 - im.height) // 2
    tile.alpha_composite(im, dest=(ox, oy))
    x, y = (i % cols) * 320 + 10, (i // cols) * 340 + 10
    sheet.paste(tile.convert("RGB"), (x, y))
    draw.text((x, y + 290), f"{os.path.basename(p)}\n{im.size}", fill=(255, 230, 110))
sheet.save(os.path.join(AUDIT_DIR, "all_cutouts_qa.jpg"), quality=90)
print("ALL CUTOUTS QA SHEET READY!")
