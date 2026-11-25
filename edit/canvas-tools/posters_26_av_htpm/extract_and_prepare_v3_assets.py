# -*- coding: utf-8 -*-
"""
Extract all clean 3D illustrations & backdrops from yesterday's 26 PSDs on Z:,
prepare ultra-sharp 2200px hero product cutouts + upright stick sachets + 3D stone/marble podiums,
and create a contact sheet of AV stick sachets (DSC09580..DSC09612) to pair AV Protein & Collamela with upright sachets!
"""
import os, sys, glob, shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
import struct
import types
import packbits as _raw_packbits
import pytoshop
import pytoshop.codecs

def _psd_rle_decode(data, h, w, depth_bytes, version):
    hdr_sz = h * (2 if version == 1 else 4)
    counts = struct.unpack_from(f">{h}H" if version == 1 else f">{h}I", data, 0)
    pos = hdr_sz
    out = bytearray()
    for c in counts:
        out.extend(_raw_packbits.decode(data[pos : pos + c]))
        pos += c
    return bytes(out)

pytoshop.codecs.packbits = types.SimpleNamespace(decode=_psd_rle_decode, encode=_raw_packbits.encode)
from pytoshop.user import nested_layers

DRIVE_PROJ = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\261122-26-thiet-ke-infographic-av-htpm"
sys.path.insert(0, os.path.join(DRIVE_PROJ, "code"))
from step3_product_catalog_26_designs import POSTERS_26

sys.path.insert(0, r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from cutout_product_png import ISNetCutout

V3_DIR = r"d:\AI\full studio\projects\av_htpm_26_posters_v3"
BG_DIR = os.path.join(V3_DIR, "assets", "backdrops")
ILL_DIR = os.path.join(V3_DIR, "assets", "illusts")
CUT_DIR = os.path.join(V3_DIR, "assets", "cutouts")
AUDIT_DIR = os.path.join(V3_DIR, "audit")
for d in (BG_DIR, ILL_DIR, CUT_DIR, AUDIT_DIR):
    os.makedirs(d, exist_ok=True)

# Copy step3 catalog locally for fast access
shutil.copy2(
    os.path.join(DRIVE_PROJ, "code", "step3_product_catalog_26_designs.py"),
    os.path.join(V3_DIR, "step3_product_catalog_26_designs.py"),
)

HT_ROOT = r"Z:\Máy tính khác\My Computer\hằng thu pharma"
HT_PROD = os.path.join(HT_ROOT, "02. Ảnh Sản Phẩm")
AV_BIEN = os.path.join(HT_ROOT, "04. Ảnh Sự Kiện & Nhà Máy", "Ảnh AV Biển (Đã Chỉnh)")
AV_TLH  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\An vượng"


def layer_to_rgba(lyr, W=1600, H=2000) -> np.ndarray:
    out = np.zeros((H, W, 4), dtype=np.uint8)
    t, l, b, r = lyr.top, lyr.left, lyr.bottom, lyr.right
    if b <= t or r <= l:
        return out
    ch_r = lyr.channels[0].image
    ch_g = lyr.channels[1].image
    ch_b = lyr.channels[2].image
    ch_a = lyr.channels[-1].image if -1 in lyr.channels else np.full((b - t, r - l), 255, dtype=np.uint8)
    out[t:b, l:r, 0] = ch_r
    out[t:b, l:r, 1] = ch_g
    out[t:b, l:r, 2] = ch_b
    out[t:b, l:r, 3] = ch_a
    return out


def extract_clean_illustration_from_card(l2_rgba: np.ndarray, layout: str, card_idx: int) -> Image.Image:
    """
    Slices strictly inside the illustration zone of Layer 2 ('02_Khung_The_Bento_Va_Minh_Hoa_3D', which has ZERO text!),
    strips the cream card fill (#FFFDF9 -> #FBF2DF), tight-crops 100% of empty margin, and boosts crispness!
    """
    if layout == "A":
        # Exact illustration wrap boxes from yesterday's CSS:
        # card-1: left 692, w 426, top 482, h 638 -> illust sits at y: 572..898, x: 716..1094
        # card-2: left 1140, w 426, top 482, h 638 -> illust sits at y: 572..898, x: 1164..1542
        # card-3: left 34, w 752, top 1158, h 646 -> illust sits at y: 1236..1582, x: 145..675
        # card-4: left 814, w 752, top 1158, h 646 -> illust sits at y: 1236..1582, x: 925..1455
        boxes = [
            (714, 570, 1096, 902),
            (1162, 570, 1544, 902),
            (140, 1234, 680, 1584),
            (920, 1234, 1460, 1584),
        ]
    else:
        # Layout B yesterday:
        # card-1: left 34, top 778 -> illust wrap left=52, top=806, w=276, h=412 -> [54..326, 814..1218]
        # card-2: left 814, top 778 -> [834..1106, 814..1218]
        # card-3: left 34, top 1312 -> [54..326, 1348..1752]
        # card-4: left 814, top 1312 -> [834..1106, 1348..1752]
        boxes = [
            (55, 816, 325, 1216),
            (835, 816, 1105, 1216),
            (55, 1350, 325, 1750),
            (835, 1350, 1105, 1750),
        ]
    x0, y0, x1, y1 = boxes[card_idx]
    sub = l2_rgba[y0:y1, x0:x1, :3].astype(np.float32)

    # Estimate local card background gradient per-row from left & right 6px borders!
    left_strip = np.median(sub[:, :6, :], axis=1, keepdims=True)
    right_strip = np.median(sub[:, -6:, :], axis=1, keepdims=True)
    bg_row = 0.5 * (left_strip + right_strip)  # shape (H_c, 1, 3)

    # In Layout B, there was a faint radial golden glow in the center; also check corner median
    diff = np.linalg.norm(sub - bg_row, axis=2)
    # Tightly segment non-cream pixels
    alpha = np.clip((diff - 9.0) / 16.0, 0.0, 1.0)
    mask_u8 = (alpha > 0.28).astype(np.uint8) * 255
    closed = cv2.morphologyEx(mask_u8, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    # Fill interior holes inside white bowls/pearls/capsules!
    h_m, w_m = closed.shape
    flood = closed.copy()
    ff_mask = np.zeros((h_m + 2, w_m + 2), dtype=np.uint8)
    cv2.floodFill(flood, ff_mask, (0, 0), 255)
    cv2.floodFill(flood, ff_mask, (w_m - 1, 0), 255)
    cv2.floodFill(flood, ff_mask, (0, h_m - 1), 255)
    cv2.floodFill(flood, ff_mask, (w_m - 1, h_m - 1), 255)
    holes = cv2.bitwise_not(flood)
    filled = cv2.bitwise_or(closed, holes)
    eroded = cv2.erode(filled, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
    alpha_final = np.maximum(alpha, (eroded / 255.0) * 0.99)
    alpha_final = cv2.GaussianBlur(alpha_final.astype(np.float32), (5, 5), 0.8)

    # Un-cream semi-transparent edges so zero halo on warm cream cards
    edge = (alpha_final > 0.05) & (alpha_final < 0.88)
    denom = np.maximum(alpha_final[..., None], 0.25)
    rgb_decon = np.where(edge[..., None], np.clip((sub - (1.0 - alpha_final[..., None]) * bg_row) / denom, 0, 255), sub)

    # Tight crop to non-zero alpha!
    ys, xs = np.where(alpha_final > 0.12)
    if len(xs) > 25:
        pad = 4
        bx0, by0 = max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad)
        bx1, by1 = min(w_m, int(xs.max()) + 1 + pad), min(h_m, int(ys.max()) + 1 + pad)
        rgb_decon = rgb_decon[by0:by1, bx0:bx1]
        alpha_final = alpha_final[by0:by1, bx0:bx1]

    pil_rgb = Image.fromarray(np.clip(rgb_decon, 0, 255).astype(np.uint8), "RGB")
    # Upscale 1.6x with Lanczos + crisp vibrance/sharpness so huge V3 illustrations are razor-sharp!
    nw, nh = int(round(pil_rgb.width * 1.6)), int(round(pil_rgb.height * 1.6))
    pil_rgb = pil_rgb.resize((nw, nh), Image.Resampling.LANCZOS)
    pil_rgb = ImageEnhance.Color(ImageEnhance.Contrast(ImageEnhance.Sharpness(pil_rgb).enhance(1.28)).enhance(1.06)).enhance(1.12)
    a_up = cv2.resize((np.clip(alpha_final, 0, 1) * 255.0).astype(np.uint8), (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    return Image.fromarray(np.dstack([np.asarray(pil_rgb), a_up]), "RGBA")


def main():
    # 1. Inspect DSC09580..DSC09612 in Ảnh AV Biển to identify AV Protein & Collamela upright stick sachets!
    stick_cands = sorted(glob.glob(os.path.join(AV_BIEN, "DSC0958*.jpg")) + glob.glob(os.path.join(AV_BIEN, "DSC0959*.jpg")) + glob.glob(os.path.join(AV_BIEN, "DSC0960*.jpg")))
    if stick_cands:
        cols = 6
        rows = (len(stick_cands) + cols - 1) // cols
        sh_im = Image.new("RGB", (cols * 260, rows * 280), (24, 26, 28))
        dr = ImageDraw.Draw(sh_im)
        for i, p in enumerate(stick_cands):
            im = Image.open(p).convert("RGB")
            im.thumbnail((240, 240))
            x, y = (i % cols) * 260 + 10, (i // cols) * 280 + 8
            sh_im.paste(im, (x, y))
            dr.text((x, y + 250), os.path.basename(p), fill=(255, 230, 100))
        sh_im.save(os.path.join(AUDIT_DIR, "av_sticks_scan.jpg"), quality=88)
        print("Saved av_sticks_scan.jpg!", flush=True)

    # 2. Extract backdrops + 104 clean 3D illustrations from the 26 PSDs on Z:
    fin_root = os.path.join(DRIVE_PROJ, "Final_Deliverables")
    for sp in POSTERS_26:
        code = sp["code"]
        brand_dir = "01_An_Vuong_Pharma_8_Thiet_Ke" if sp["brand_group"] == "AN_VUONG" else "02_Hang_Thu_Pharma_18_Thiet_Ke"
        prefix = "AVPM" if sp["brand_group"] == "AN_VUONG" else "HTPM"
        psd_p = os.path.join(fin_root, brand_dir, sp["product_folder"], f"261122 {prefix} {sp['file_title']}.psd")
        bg_out = os.path.join(BG_DIR, f"{code}_bg.png")
        c4_out = os.path.join(ILL_DIR, f"{code}_c4.png")
        if os.path.exists(bg_out) and os.path.exists(c4_out):
            continue
        with open(psd_p, "rb") as f:
            psd = pytoshop.read(f)
            layers = {l.name: l for l in nested_layers.psd_to_nested_layers(psd)}
            l1 = layer_to_rgba(layers["01_Nen_Studio_3D_AI"])
            Image.fromarray(l1[:, :, :3], "RGB").save(bg_out)

            l2 = layer_to_rgba(layers["02_Khung_The_Bento_Va_Minh_Hoa_3D"])
            for ci in range(4):
                ill = extract_clean_illustration_from_card(l2, sp["layout"], ci)
                ill.save(os.path.join(ILL_DIR, f"{code}_c{ci+1}.png"))
        print(f"Extracted bg + 4 tight illustrations for {code}", flush=True)

    # 3. Prepare Logos + Ultra-Crisp 2200px Studio Product Cutouts from Z:
    av_logo_src = os.path.join(AV_TLH, "Logo AN Vượng Pharma Xanh Vàng.png")
    av_im = Image.open(av_logo_src).convert("RGBA")
    arr = np.array(av_im, dtype=np.float32)
    rgb = arr[:, :, :3]
    lum = rgb.max(axis=2)
    alpha = np.clip((lum - 14.0) / 42.0, 0.0, 1.0)
    rgb_clean = np.clip(rgb / np.maximum(alpha[:, :, None], 0.18), 0.0, 255.0)
    r, g, b = rgb_clean[:, :, 0], rgb_clean[:, :, 1], rgb_clean[:, :, 2]
    is_gold = (r > 135) & (g > 95) & ((r - b) > 45)
    r_lux = np.where(is_gold, np.clip(r * 1.14 + 20, 0, 255), 252.0)
    g_lux = np.where(is_gold, np.clip(g * 1.12 + 16, 0, 255), 254.0)
    b_lux = np.where(is_gold, np.clip(b * 1.02 + 6, 0, 255), 248.0)
    ys, xs = np.where(alpha > 0.08)
    av_logo_dark = Image.fromarray(np.dstack([r_lux, g_lux, b_lux, alpha * 255.0]).astype(np.uint8), "RGBA").crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
    av_logo_dark.save(os.path.join(CUT_DIR, "logo_an_vuong_on_dark.png"))

    ht_logo_src = os.path.join(HT_PROD, "Logo & Ảnh Mẫu Thương Hiệu", "ht_logo_official.png")
    shutil.copy2(ht_logo_src, os.path.join(CUT_DIR, "logo_hang_thu.png"))

    isnet = ISNetCutout()

    def make_cutout(src_path, crop_rel=None, max_side=2200, unwhite=225.0):
        im = Image.open(src_path)
        if im.mode == "RGBA":
            amin, amax = im.getchannel("A").getextrema()
            if amin < 20 and amax > 235:
                im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                arr_c = np.array(im)
                ys_c, xs_c = np.where(arr_c[:, :, 3] > 35)
                if len(xs_c) > 0:
                    im = im.crop((max(0, xs_c.min()-4), max(0, ys_c.min()-4), min(im.width, xs_c.max()+5), min(im.height, ys_c.max()+5)))
                return im
        rgb_i = im.convert("RGB")
        if crop_rel is not None:
            w_i, h_i = rgb_i.size
            x0, y0, x1, y1 = crop_rel
            rgb_i = rgb_i.crop((int(w_i * x0), int(h_i * y0), int(w_i * x1), int(h_i * y1)))
        rgb_i.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        rgb_i = ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb_i).enhance(1.22)).enhance(1.05)
        cut = isnet.remove_bg(rgb_i, trim_transparent=True)
        arr_o = np.array(cut, dtype=np.float32)
        a = np.clip((arr_o[:, :, 3] / 255.0 - 0.08) / 0.86, 0.0, 1.0)
        edge = (a > 0.04) & (a < 0.90)
        rgb_u = np.where(edge[..., None], np.clip((arr_o[:, :, :3] - (1.0 - a[..., None]) * unwhite) / np.maximum(a[..., None], 0.25), 0, 255), arr_o[:, :, :3])
        # Keep significant components
        mb = (a > 0.16).astype(np.uint8)
        nl, lb, st, _ = cv2.connectedComponentsWithStats(mb, connectivity=8)
        if nl > 2:
            mxa = int(st[1:, cv2.CC_STAT_AREA].max())
            kp = np.zeros_like(mb, dtype=np.float32)
            for idx in range(1, nl):
                if st[idx, cv2.CC_STAT_AREA] >= mxa * 0.025:
                    kp[lb == idx] = 1.0
            a = a * np.clip(cv2.GaussianBlur(kp, (5, 5), 0.9) * 1.15, 0.0, 1.0)
        out_im = Image.fromarray(np.dstack([rgb_u, a * 255.0]).astype(np.uint8), "RGBA")
        arr_f = np.array(out_im)
        ys_f, xs_f = np.where(arr_f[:, :, 3] > 35)
        if len(xs_f) > 0:
            out_im = out_im.crop((max(0, xs_f.min()-4), max(0, ys_f.min()-4), min(out_im.width, xs_f.max()+5), min(out_im.height, ys_f.max()+5)))
        return out_im

    JOBS = [
        ("av01_protein_a", os.path.join(AV_BIEN, "DSC09523.jpg"), (0.25, 0.08, 0.76, 0.94), 195.0),
        ("av01_protein_b", os.path.join(AV_BIEN, "DSC09608.jpg"), (0.28, 0.14, 0.74, 0.92), 195.0),
        ("av02_bojomi_a",  os.path.join(AV_BIEN, "DSC09547.jpg"), (0.24, 0.10, 0.76, 0.92), 195.0),
        ("av02_bojomi_b",  os.path.join(AV_BIEN, "DSC09536.jpg"), (0.28, 0.08, 0.74, 0.94), 195.0),
        ("av02_bojomi_stick", os.path.join(AV_BIEN, "DSC09587.jpg"), (0.35, 0.06, 0.66, 0.95), 190.0),
        ("av03_collamela_a", os.path.join(AV_BIEN, "DSC09558.jpg"), (0.14, 0.16, 0.80, 0.92), 205.0),
        ("av03_collamela_b", os.path.join(AV_BIEN, "DSC09577.jpg"), (0.26, 0.14, 0.76, 0.90), 200.0),
        ("av04_curcumilk_a", os.path.join(AV_BIEN, "DSC09557.jpg"), (0.20, 0.08, 0.76, 0.92), 195.0),
        ("av04_curcumilk_b", os.path.join(AV_BIEN, "DSC09530.jpg"), (0.24, 0.10, 0.74, 0.93), 195.0),
        ("av04_curcumilk_stick", os.path.join(AV_BIEN, "DSC09588.jpg"), (0.35, 0.05, 0.65, 0.96), 190.0),
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
    for name, spath, crel, unw in JOBS:
        out_p = os.path.join(CUT_DIR, f"{name}.png")
        if not os.path.exists(out_p):
            c_im = make_cutout(spath, crel, 2200, unw)
            c_im.save(out_p)
            print(f"Cutout saved: {name}.png -> {c_im.size}", flush=True)

    print("ALL V3 ASSETS EXTRACTED & PREPARED!", flush=True)


if __name__ == "__main__":
    main()
