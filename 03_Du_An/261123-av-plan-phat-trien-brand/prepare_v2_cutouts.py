# -*- coding: utf-8 -*-
"""
Prepare ultra-clean studio RGBA cutouts + logos for An Vượng Pharma CTKM V2
and locate all synced Google Drive folders.
"""
import os, sys, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

sys.path.insert(0, r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from cutout_product_png import ISNetCutout

PROJ = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand"
CUT_DIR = os.path.join(PROJ, "assets_cutouts_v2")
os.makedirs(CUT_DIR, exist_ok=True)

HT_ROOT = r"G:\Other computers\My Computer\hằng thu pharma"
AV_BIEN = os.path.join(HT_ROOT, "04. Ảnh Sự Kiện & Nhà Máy", "Ảnh AV Biển (Đã Chỉnh)")
AV_TLH  = r"G:\Other computers\My Computer\Document HT Media\TLH\An vượng"

# Check Google Drive target folders
for g_cand in [
    r"G:\My Drive\dự án ngoài\An Vượng",
    r"G:\Other computers\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới",
    r"G:\My Drive\AI_Full_Studio\03_Du_An\261123-av-plan-phat-trien-brand",
]:
    if os.path.exists(g_cand):
        print("SYNC ROOT:", g_cand)
        for item in os.listdir(g_cand):
            if any(k in item.lower() for k in ["261123", "ctkm", "an v", "banner", "01_bo"]):
                ip = os.path.join(g_cand, item)
                print("  ->", ip)
                if os.path.isdir(ip):
                    print("     files:", os.listdir(ip)[:12])

_isnet = None
def get_isnet():
    global _isnet
    if _isnet is None:
        _isnet = ISNetCutout()
    return _isnet

def trim_rgba(im: Image.Image, pad: int = 8) -> Image.Image:
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 25)
    if len(xs) == 0:
        return im
    return im.crop((
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(im.width, int(xs.max()) + 1 + pad),
        min(im.height, int(ys.max()) + 1 + pad),
    ))

def clean_cutout_edges(im_rgba: Image.Image, unwhite_bg: float = 205.0, erode_px: int = 1) -> Image.Image:
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

def cutout_from_photo(src_path: str, crop_rel=None, max_side: int = 1800, unwhite: float = 200.0) -> Image.Image:
    rgb = Image.open(src_path).convert("RGB")
    if crop_rel is not None:
        w, h = rgb.size
        x0, y0, x1, y1 = crop_rel
        rgb = rgb.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
    rgb.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    rgb = ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb).enhance(1.18)).enhance(1.04)
    cut = get_isnet().remove_bg(rgb, trim_transparent=True)
    return clean_cutout_edges(cut, unwhite_bg=unwhite, erode_px=1)

# 1. Copy already-cached cutouts from Ngay_01_2411 if available, and generate missing _b / _stick cutouts
cached_dir = os.path.join(PROJ, "Daily_Work", "Ngay_01_2411", "video_02_combo_4sp", "07_HyperFrames_Project", "assets", "images")
for fn in ["av01_protein_a.png", "av02_bojomi_a.png", "av03_collamela_a.png", "av04_curcumilk_a.png", "logo_an_vuong_orig.png", "logo_an_vuong_on_dark.png"]:
    src = os.path.join(cached_dir, fn)
    dst = os.path.join(CUT_DIR, fn)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)
        print("Copied cached:", fn)

AV_JOBS = [
    ("av01_protein_a",     os.path.join(AV_BIEN, "DSC09523.jpg"), (0.25, 0.08, 0.76, 0.94), 195.0),
    ("av01_protein_b",     os.path.join(AV_BIEN, "DSC09608.jpg"), (0.28, 0.14, 0.74, 0.92), 195.0),
    ("av02_bojomi_a",      os.path.join(AV_BIEN, "DSC09547.jpg"), (0.24, 0.10, 0.76, 0.92), 195.0),
    ("av02_bojomi_b",      os.path.join(AV_BIEN, "DSC09536.jpg"), (0.28, 0.08, 0.74, 0.94), 195.0),
    ("av02_bojomi_stick",  os.path.join(AV_BIEN, "DSC09587.jpg"), (0.35, 0.06, 0.66, 0.95), 190.0),
    ("av03_collamela_a",   os.path.join(AV_BIEN, "DSC09558.jpg"), (0.14, 0.16, 0.80, 0.92), 205.0),
    ("av03_collamela_b",   os.path.join(AV_BIEN, "DSC09577.jpg"), (0.26, 0.14, 0.76, 0.90), 200.0),
    ("av04_curcumilk_a",   os.path.join(AV_BIEN, "DSC09557.jpg"), (0.20, 0.08, 0.76, 0.92), 195.0),
    ("av04_curcumilk_b",   os.path.join(AV_BIEN, "DSC09530.jpg"), (0.24, 0.10, 0.74, 0.93), 195.0),
    ("av04_curcumilk_stick", os.path.join(AV_BIEN, "DSC09588.jpg"), (0.35, 0.05, 0.65, 0.96), 190.0),
]

for name, path, crop_rel, unw in AV_JOBS:
    out_p = os.path.join(CUT_DIR, f"{name}.png")
    if os.path.exists(out_p) and os.path.getsize(out_p) > 30000:
        print(f"[SKIP] {name}.png ready")
        continue
    im = cutout_from_photo(path, crop_rel=crop_rel, max_side=1800, unwhite=unw)
    im.save(out_p)
    print(f"[CUTOUT OK] {name}.png -> {im.size}")

print("=== ALL V2 CUTOUTS READY ===")
