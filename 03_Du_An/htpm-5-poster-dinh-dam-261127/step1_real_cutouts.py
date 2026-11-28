# -*- coding: utf-8 -*-
import os, sys, shutil
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw

sys.path.insert(0, r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from cutout_product_png import ISNetCutout

PROJ = r"C:\AI\full studio\projects\htpm_5_trongtreo_261127"
CUT_D = os.path.join(PROJ, "cutouts")
QC_D  = os.path.join(PROJ, "qc")
os.makedirs(CUT_D, exist_ok=True)
os.makedirs(QC_D, exist_ok=True)

HT_SP = r"G:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\02. Ảnh Sản Phẩm"
LOGO_SRC = os.path.join(HT_SP, "Logo & Ảnh Mẫu Thương Hiệu", "ht_logo_official.png")
shutil.copy2(LOGO_SRC, os.path.join(CUT_D, "ht_logo_official.png"))

_isnet = None
def get_isnet():
    global _isnet
    if _isnet is None:
        _isnet = ISNetCutout()
    return _isnet

def trim_rgba(im, pad=10):
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 20)
    if len(xs) == 0:
        return im
    return im.crop((max(0, int(xs.min())-pad), max(0, int(ys.min())-pad), min(im.width, int(xs.max())+1+pad), min(im.height, int(ys.max())+1+pad)))

def clean_studio_png(src_p):
    im = Image.open(src_p).convert("RGBA")
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Color(ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb).enhance(1.18)).enhance(1.05)).enhance(1.04)
    arr = np.array(Image.merge("RGBA", (*rgb.split(), a)), dtype=np.float32)
    al = arr[:, :, 3] / 255.0
    al_c = np.clip((al - 0.06) / 0.90, 0.0, 1.0)
    edge = (al_c > 0.04) & (al_c < 0.92)
    denom = np.maximum(al_c[:, :, None], 0.25)
    unw = (arr[:, :, :3] - (1.0 - al_c[:, :, None]) * 248.0) / denom
    rgb_o = np.where(edge[:, :, None], np.clip(unw, 0, 255), arr[:, :, :3])
    return trim_rgba(Image.fromarray(np.dstack([rgb_o, al_c * 255.0]).astype(np.uint8), "RGBA"))

def cutout_whiteskin_solid(src_p):
    im = Image.open(src_p).convert("RGB")
    im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    im_enh = ImageEnhance.Contrast(ImageEnhance.Sharpness(im).enhance(1.18)).enhance(1.05)
    cut = get_isnet().remove_bg(im_enh, trim_transparent=False)
    arr = np.array(cut)
    rgb = arr[:, :, :3].astype(np.float32)
    a = arr[:, :, 3].copy()

    is_blue_box = (rgb[:, :, 2] > 155) & ((rgb[:, :, 2] - rgb[:, :, 0]) > 65) & (a > 180)
    bys, bxs = np.where(is_blue_box)
    box_top_y = int(bys.min())
    _, ub_xs = np.where(is_blue_box[box_top_y : box_top_y + 180, :])
    box_x0 = int(np.percentile(ub_xs, 0.5))
    box_x1 = int(np.percentile(ub_xs, 99.5))

    is_amber = ((rgb[:, :, 0] - rgb[:, :, 2]) > 45) & (a > 120)
    ays, axs = np.where(is_amber)
    bottle_bottom_y = int(np.percentile(ays[axs < (box_x0 + 40)], 99.2))
    gray = cv2.cvtColor(np.array(im_enh), cv2.COLOR_RGB2GRAY).astype(np.float32)
    ys0, ys1 = bottle_bottom_y - 95, bottle_bottom_y - 5
    box_bottom_y = ys0 + int(np.argmax(np.mean(np.abs(np.diff(gray[ys0:ys1, box_x0+90:box_x1-20], axis=0)), axis=1)))

    a_fixed = a.copy()
    a_fixed[box_top_y + 4 : box_bottom_y, box_x0 + 3 : box_x1 - 3] = 255
    chroma = np.max(rgb, axis=2) - np.min(rgb, axis=2)
    below_right = np.zeros_like(a_fixed, dtype=bool)
    below_right[box_bottom_y + 2 :, box_x0 + 35 :] = True
    a_fixed[below_right & (chroma < 28)] = 0
    a_fixed = np.where(a_fixed < 40, 0, a_fixed).astype(np.uint8)
    num_l, lbls, stats, _ = cv2.connectedComponentsWithStats((a_fixed > 0).astype(np.uint8))
    for lbl in range(1, num_l):
        if stats[lbl, cv2.CC_STAT_AREA] < 250:
            a_fixed[lbls == lbl] = 0
    arr[:, :, 3] = a_fixed
    return trim_rgba(Image.fromarray(arr, "RGBA"))

def cutout_romance_vip(src_p):
    im = Image.open(src_p).convert("RGB")
    im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    im_enh = ImageEnhance.Color(ImageEnhance.Contrast(ImageEnhance.Sharpness(im).enhance(1.18)).enhance(1.06)).enhance(1.05)
    cut = get_isnet().remove_bg(im_enh, trim_transparent=True)
    arr = np.array(cut, dtype=np.float32)
    a = arr[:, :, 3] / 255.0
    # Solidify any semi-transparent white interior of box/bottle
    bin_m = (a > 0.35).astype(np.uint8) * 255
    bin_cl = cv2.morphologyEx(bin_m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    cnts, _ = cv2.findContours(bin_cl, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(bin_m)
    for c in cnts:
        if cv2.contourArea(c) > 2000:
            cv2.drawContours(filled, [c], -1, 255, thickness=cv2.FILLED)
    interior = cv2.erode(filled, np.ones((5, 5), np.uint8), iterations=1)
    a_out = np.maximum(arr[:, :, 3], interior).astype(np.uint8)
    a_out = np.where(a_out < 30, 0, a_out).astype(np.uint8)
    arr[:, :, 3] = a_out
    return trim_rgba(Image.fromarray(arr.astype(np.uint8), "RGBA"))

results = [
    ("01_white_skin.png",   cutout_whiteskin_solid(os.path.join(HT_SP, "08. Viên Uống Trắng Da White Skin", "DSC08838.jpg"))),
    ("02_romance_vip.png",  cutout_romance_vip(os.path.join(HT_SP, "04. Dung Dịch Vệ Sinh Romance VIP", "Bản sao của DSC07151.jpg"))),
    ("03_lt_plus.png",      clean_studio_png(os.path.join(HT_SP, "02. Viên Đặt Phụ Khoa LT Plus", "DSC04649.png"))),
    ("04_da_day_ht.png",    clean_studio_png(os.path.join(HT_SP, "03. Dạ Dày HT", "DSC04657.png"))),
    ("05_dieu_kinh_ht.png", clean_studio_png(os.path.join(HT_SP, "01. Điều Kinh Bổ Trứng", "DSC04761.png"))),
]

tiles = []
for fn, im in results:
    p = os.path.join(CUT_D, fn)
    im.save(p)
    print(f"Saved real cutout: {fn} -> {im.size}", flush=True)
    bg = Image.new("RGBA", (360, 360), (225, 236, 248, 255))
    th = im.copy(); th.thumbnail((320, 300), Image.Resampling.LANCZOS)
    bg.alpha_composite(th, dest=((360 - th.width)//2, (320 - th.height)//2))
    ImageDraw.Draw(bg).text((12, 332), fn, fill=(20, 40, 70, 255))
    tiles.append(bg.convert("RGB"))

sh = Image.new("RGB", (360 * 5, 360), (240, 244, 248))
for i, t in enumerate(tiles):
    sh.paste(t, (i * 360, 0))
sh.save(os.path.join(QC_D, "real_5_cutouts_qc.jpg"), quality=92)
print("Saved real_5_cutouts_qc.jpg")
