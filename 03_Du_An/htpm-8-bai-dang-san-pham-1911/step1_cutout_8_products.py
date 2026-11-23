import os, sys, shutil
from collections import deque
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from cutout_product_png import ISNetCutout

PROJ_DIR  = r"d:\AI\full studio\projects\htpm_8_posts_1911"
CUT_DIR   = os.path.join(PROJ_DIR, "assets", "cutouts")
STAGE_DIR = os.path.join(PROJ_DIR, "assets", "stages")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
ANH_DIR   = r"Z:\Máy tính khác\My Computer\hằng thu pharma\Ảnh"

for d in (CUT_DIR, STAGE_DIR, CHECK_DIR):
    os.makedirs(d, exist_ok=True)

_isnet = None
def get_isnet():
    global _isnet
    if _isnet is None:
        _isnet = ISNetCutout()
    return _isnet

def trim_rgba(im: Image.Image, pad: int = 8) -> Image.Image:
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 18)
    if len(xs) == 0:
        return im
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(im.width, int(xs.max()) + 1 + pad)
    y1 = min(im.height, int(ys.max()) + 1 + pad)
    return im.crop((x0, y0, x1, y1))

def decontaminate_white_halo(im_rgba: Image.Image) -> Image.Image:
    """Gently pulls semi-transparent border RGB inward & tightens outer 1px white fringe."""
    arr = np.array(im_rgba, dtype=np.float32)
    rgb = arr[:, :, :3]
    a = arr[:, :, 3] / 255.0

    # Tighten ultra-faint halo (<0.12 -> 0, smooth ramp to 0.88)
    a_clean = np.clip((a - 0.08) / 0.86, 0.0, 1.0)
    # Un-premultiply against white (250,250,250) on edge pixels (0.05 < a < 0.92)
    edge = (a > 0.05) & (a < 0.92)
    denom = np.maximum(a[:, :, None], 0.22)
    unwhite = (rgb - (1.0 - a[:, :, None]) * 248.0) / denom
    rgb_out = np.where(edge[:, :, None], np.clip(unwhite, 0.0, 255.0), rgb)

    out = np.dstack([rgb_out, a_clean * 255.0]).astype(np.uint8)
    return trim_rgba(Image.fromarray(out, "RGBA"))

def smart_cutout(src_path: str, max_side: int = 2000) -> Image.Image:
    im = Image.open(src_path)
    print(f"Loading {os.path.basename(src_path)}: mode={im.mode}, size={im.size}")
    if im.mode == "RGBA":
        a_min, a_max = im.getchannel("A").getextrema()
        if a_min < 20 and a_max > 235:
            # Already transparent studio PNG! Resize & polish crispness
            im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
            r, g, b, a = im.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb).enhance(1.15)).enhance(1.04)
            merged = Image.merge("RGBA", (*rgb.split(), a))
            return decontaminate_white_halo(merged)

    rgb = im.convert("RGB")
    rgb.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    rgb = ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb).enhance(1.16)).enhance(1.05)
    cut = get_isnet().remove_bg(rgb, trim_transparent=True)
    return decontaminate_white_halo(cut)

def extract_ht_logo():
    """Extracts crisp circular HT yin-yang lotus logo from 1.png."""
    p = os.path.join(ANH_DIR, "1.png")
    im = Image.open(p).convert("RGB")
    w, h = im.size
    # In 1.png, the circular logo sits in the upper-center of the pink box
    arr = np.array(im, dtype=np.float32)
    # Detect saturated red or blue logo circle vs pastel pink box
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    is_red_logo = (r > 195) & (g < 85) & (b < 95)
    is_blue_logo = (b > 175) & (r < 125)
    ys, xs = np.where(is_red_logo | is_blue_logo)
    cx = int(round((xs.min() + xs.max()) * 0.5))
    cy = int(round((ys.min() + ys.max()) * 0.5))
    rad = int(round(max(xs.max() - xs.min(), ys.max() - ys.min()) * 0.545))

    crop = im.crop((cx - rad, cy - rad, cx + rad, cy + rad)).resize((512, 512), Image.Resampling.LANCZOS)
    crop = ImageEnhance.Contrast(ImageEnhance.Sharpness(crop).enhance(1.25)).enhance(1.08)
    mask = Image.new("L", (1024, 1024), 0)
    ImageDraw.Draw(mask).ellipse([16, 16, 1008, 1008], fill=255)
    mask = mask.resize((512, 512), Image.Resampling.LANCZOS)
    logo_rgba = crop.convert("RGBA")
    logo_rgba.putalpha(mask)

    # Add thin crisp white studio border ring around circular HT emblem
    canvas = Image.new("RGBA", (540, 540), (0, 0, 0, 0))
    ring = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([12, 12, 1068, 1068], fill=(255, 255, 255, 255))
    ring = ring.resize((540, 540), Image.Resampling.LANCZOS)
    canvas = Image.alpha_composite(canvas, ring)
    canvas.alpha_composite(logo_rgba, dest=(14, 14))
    out_logo = os.path.join(CUT_DIR, "ht_logo_official.png")
    canvas.save(out_logo)
    # Also save into Brand Kit
    bk_logo = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma\logos_png\ht_logo_official.png"
    os.makedirs(os.path.dirname(bk_logo), exist_ok=True)
    shutil.copy2(out_logo, bk_logo)
    print("Extracted official HT logo ->", out_logo)

PRODUCTS = [
    ("01_dieu_kinh",      os.path.join(ANH_DIR, "DSC04761.png")),
    ("01_dieu_kinh_alt",  os.path.join(ANH_DIR, "DSC04758.png")),
    ("02_lt_plus",        os.path.join(ANH_DIR, "DSC04649.png")),
    ("02_lt_plus_alt",    os.path.join(ANH_DIR, "DSC04627.png")),
    ("03_da_day_ht",      os.path.join(ANH_DIR, "DSC04657.png")),
    ("03_da_day_ht_alt",  os.path.join(ANH_DIR, "DSC04655.png")),
    ("04_romance_vip",    r"D:\AI\full studio\output\htpm-ddvs-2\media\cutout_romance_vip.png"),
    ("05_vien_dat_pk",    os.path.join(ANH_DIR, "DSC04746.png")),
    ("05_vien_dat_pk_alt",os.path.join(ANH_DIR, "DSC04752.png")),
    ("06_romance_love",   os.path.join(ANH_DIR, "DSC04784.png")),
    ("06_romance_love_alt",os.path.join(ANH_DIR, "DSC04780.png")),
    ("07_ngoc_long_hoan", os.path.join(ANH_DIR, "DSC08850.jpg")),
    ("08_white_skin",     r"D:\AI\full studio\output\htpm-20261119\media\ws_cut_caps.png"),
    ("08_white_skin_alt", r"D:\AI\full studio\output\htpm-20261119\media\ws_cut_duo.png"),
]

def main():
    extract_ht_logo()
    tiles = []
    for name, sp in PRODUCTS:
        dst = os.path.join(CUT_DIR, f"{name}.png")
        if name in ("04_romance_vip", "08_white_skin", "08_white_skin_alt") and os.path.exists(sp):
            im = trim_rgba(Image.open(sp).convert("RGBA"))
            im.save(dst)
        else:
            im = smart_cutout(sp)
            im.save(dst)
        print(f"Saved cutout: {name}.png -> {im.size}")

        # Build dark+checkerboard QC tile to inspect edges!
        tw, th = 380, 380
        bg = Image.new("RGBA", (tw, th), (36, 40, 52, 255))
        d = ImageDraw.Draw(bg)
        for yy in range(0, 340, 24):
            for xx in range(0, tw, 24):
                if ((xx // 24) + (yy // 24)) % 2 == 0:
                    d.rectangle([xx, yy, xx + 23, yy + 23], fill=(48, 53, 68, 255))
        prev = im.copy()
        prev.thumbnail((340, 310), Image.Resampling.LANCZOS)
        bg.alpha_composite(prev, dest=((tw - prev.width) // 2, (335 - prev.height) // 2))
        d.text((12, 350), f"{name} ({im.width}x{im.height})", fill=(255, 232, 140, 255))
        tiles.append(bg.convert("RGB"))

    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 380, rows * 380), (24, 26, 34))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 380, (i // cols) * 380))
    qc_p = os.path.join(CHECK_DIR, "cutouts_qc_sheet.jpg")
    sheet.save(qc_p, quality=92)
    print("Saved QC sheet:", qc_p)

if __name__ == "__main__":
    main()
