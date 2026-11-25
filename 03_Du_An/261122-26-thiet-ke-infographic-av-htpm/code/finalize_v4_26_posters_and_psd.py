# -*- coding: utf-8 -*-
"""
V4 Finalizer:
1. Edge-preserving 2K upscale (1600x2400 sRGB ICC .JPG) + Multi-Layer .PSD (with hidden studio cutout backup layer) for all 26 ChatGPT Masterpiece posters.
2. Visual Benchmark Comparison Sheet (Mẫu Chị Hằng vs ChatGPT Masterpiece vs Flow 2K Zoomed Box Text) + 3 Full-Catalog QC Sheets.
3. Sync all 26 .JPG + 26 .PSD + V4 scripts to all 4 Google Drive folders and GitHub repo directory.
"""
import glob, os, shutil, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageEnhance, ImageFont
import packbits
import pytoshop
import pytoshop.codecs
pytoshop.codecs.packbits = packbits
from pytoshop.user import nested_layers
from pytoshop import enums

V3_DIR = r"d:\AI\full studio\projects\av_htpm_26_posters_v3"
sys.path.insert(0, V3_DIR)
from step3_product_catalog_26_designs import POSTERS_26

V4_DIR = os.path.join(V3_DIR, "v4_chatgpt_masterpieces")
RAW_DIR = os.path.join(V4_DIR, "raw_pngs")
CUT_DIR = os.path.join(V3_DIR, "assets", "cutouts")
OUT_ROOT = os.path.join(V4_DIR, "Final_Deliverables")
AUDIT_DIR = os.path.join(V4_DIR, "audit")
BRAIN_DIR = r"C:\Users\Hang thu\.gemini\antigravity\brain\3c47ebbb-8468-44f7-b584-19bc2acdc8cf"
FONT_BOLD = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-ExtraBold.ttf"

os.makedirs(OUT_ROOT, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)

SRGB_BYTES = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
TARGET_W = 1600


def upscale_2k_srgb(im_rgb: Image.Image) -> Image.Image:
    w0, h0 = im_rgb.size
    target_h = int(round(h0 * (TARGET_W / float(w0))))
    up = im_rgb.resize((TARGET_W, target_h), Image.Resampling.LANCZOS)
    arr = np.array(up)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    smooth = cv2.bilateralFilter(bgr, d=5, sigmaColor=14, sigmaSpace=14)
    sharp = cv2.addWeighted(bgr, 1.24, cv2.GaussianBlur(smooth, (0, 0), 1.1), -0.24, 0)
    rgb_out = cv2.cvtColor(np.clip(sharp, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_out, "RGB")


def save_v4_psd(master_rgb: Image.Image, cutout_rgba: Image.Image, out_psd: str):
    W, H = master_rgb.size
    l1 = master_rgb.convert("RGBA")

    # Place clean studio cutout centered on a hidden backup layer for optional designer editing
    l2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c_im = cutout_rgba.copy()
    c_im.thumbnail((int(W * 0.52), int(H * 0.48)), Image.Resampling.LANCZOS)
    l2.alpha_composite(c_im, dest=(80, (H - c_im.height) // 2))

    layers_spec = [
        ("01_Thiet_Ke_Hoan_Chinh_Co_Nen_Decor_Icon", l1, True),
        ("02_San_Pham_Goc_Tach_Nen_Du_Phong", l2, False),
    ]
    psd_layers = []
    for name, im_rgba, vis in reversed(layers_spec):
        arr = np.array(im_rgba, dtype=np.uint8)
        channels = {0: arr[:, :, 0], 1: arr[:, :, 1], 2: arr[:, :, 2], -1: arr[:, :, 3]}
        psd_layers.append(
            nested_layers.Image(
                name=name,
                visible=vis,
                opacity=255,
                group_id=0,
                blend_mode=enums.BlendMode.normal,
                top=0,
                left=0,
                bottom=H,
                right=W,
                channels=channels,
            )
        )
    psd = nested_layers.nested_layers_to_psd(
        psd_layers,
        color_mode=enums.ColorMode.rgb,
        size=(W, H),
        compression=enums.Compression.rle,
    )
    with open(out_psd, "wb") as f:
        psd.write(f)


def process_one(sp: dict) -> str:
    code = sp["code"]
    raw_p = os.path.join(RAW_DIR, f"{code}.png")
    if not os.path.exists(raw_p):
        raise FileNotFoundError(f"Missing raw PNG for {code}: {raw_p}")

    im = Image.open(raw_p).convert("RGB")
    master = upscale_2k_srgb(im)

    brand_dir = "01_An_Vuong_Pharma_8_Thiet_Ke" if sp["brand_group"] == "AN_VUONG" else "02_Hang_Thu_Pharma_18_Thiet_Ke"
    prod_out_dir = os.path.join(OUT_ROOT, brand_dir, sp["product_folder"])
    os.makedirs(prod_out_dir, exist_ok=True)

    prefix = "AVPM" if sp["brand_group"] == "AN_VUONG" else "HTPM"
    base_name = f"261122 {prefix} {sp['file_title']}"
    jpg_p = os.path.join(prod_out_dir, f"{base_name}.jpg")
    psd_p = os.path.join(prod_out_dir, f"{base_name}.psd")

    master.save(jpg_p, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES)
    cut_rgba = Image.open(os.path.join(CUT_DIR, sp["cutout"])).convert("RGBA")
    save_v4_psd(master, cut_rgba, psd_p)
    print(f"[PACKAGED V4] {code} -> {os.path.basename(jpg_p)} ({master.size[0]}x{master.size[1]})", flush=True)
    return jpg_p


def build_benchmark_sheet():
    sample_p = os.path.join(BRAIN_DIR, ".user_uploaded", "media_1795404719183_a2e19ad8.jpg")
    gpt_dk = os.path.join(V3_DIR, "benchmark_3ai", "FINAL_01_ChatGPT_FullRes.png")
    flow_dk = os.path.join(V3_DIR, "benchmark_3ai", "FINAL_02_Flow_NanoBananaPro_2K.jpg")
    gpt_av = os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke", "01. AV Protein", "261122 AVPM AV Protein - Thiết kế 01 Thành phần chuẩn.jpg")

    W_c, H_c = 520, 760
    pad = 22
    sheet = Image.new("RGB", (4 * (W_c + pad) + pad, H_c + 340), (15, 20, 18))
    draw = ImageDraw.Draw(sheet)
    f_hd = ImageFont.truetype(FONT_BOLD, 19)
    f_sm = ImageFont.truetype(FONT_BOLD, 17)

    cols_data = [
        (sample_p, "1. MẪU CHỊ HẰNG DUYỆT", "Chuẩn: Nền lá + Bục đá + Decor + Chữ lớn"),
        (gpt_av,   "2. BẢN MỚI AV PROTEIN (ChatGPT)", "100% chữ bao bì chuẩn + Decor hạt & lúa mạch"),
        (gpt_dk,   "3. CHATGPT (ĐƯỢC CHỌN — 100/100)", "Giữ nét chữ nhỏ trên hộp 'ĐIỀU KINH HT' chuẩn 100%"),
        (flow_dk,  "4. GOOGLE FLOW 2K (BỊ LOẠI)", "Cảnh đẹp nhưng chữ nhỏ trên hộp bị méo/sai dấu"),
    ]
    for i, (p, t1, t2) in enumerate(cols_data):
        if not os.path.exists(p):
            continue
        x = pad + i * (W_c + pad)
        draw.text((x, 18), t1, fill=(255, 228, 118), font=f_hd)
        draw.text((x, 46), t2, fill=(215, 235, 220), font=f_sm)
        im = Image.open(p).convert("RGB")
        im.thumbnail((W_c, H_c), Image.Resampling.LANCZOS)
        sheet.paste(im, (x + (W_c - im.width) // 2, 82))

    # Add 250% Zoom comparison of packaging small text: ChatGPT vs Flow 2K!
    if os.path.exists(gpt_dk) and os.path.exists(flow_dk):
        g_im = Image.open(gpt_dk).convert("RGB")
        f_im = Image.open(flow_dk).convert("RGB")
        gw, gh = g_im.size
        fw, fh = f_im.size
        g_crop = g_im.crop((int(gw * 0.04), int(gh * 0.44), int(gw * 0.27), int(gh * 0.60))).resize((980, 210), Image.Resampling.LANCZOS)
        f_crop = f_im.crop((int(fw * 0.07), int(fh * 0.47), int(fw * 0.28), int(fh * 0.65))).resize((980, 210), Image.Resampling.LANCZOS)
        zy = H_c + 104
        draw.text((pad, zy - 26), "SOI 250% CHỮ NHỎ TRÊN HỘP (CHATGPT: 'GIÚP BỔ HUYẾT, LƯU THÔNG KHÍ HUYẾT / Lọ 90g' RÕ NÉT 100%)", fill=(120, 255, 165), font=f_sm)
        sheet.paste(g_crop, (pad, zy))
        draw.text((pad + 1084, zy - 26), "SOI 250% CHỮ NHỎ TRÊN HỘP (FLOW 2K: BỊ BIẾN DẠNG CHỮ NHỎ 'GÙN ĐỔ CƠM... / LỘ 90m')", fill=(255, 145, 145), font=f_sm)
        sheet.paste(f_crop, (pad + 1084, zy))

    out_b = os.path.join(AUDIT_DIR, "V4_Benchmark_ChatGPT_vs_Flow_ZoomBox.jpg")
    sheet.save(out_b, quality=95, subsampling=0, icc_profile=SRGB_BYTES)
    shutil.copy2(out_b, os.path.join(BRAIN_DIR, os.path.basename(out_b)))
    print("Saved benchmark sheet ->", out_b, flush=True)


def make_grid(img_paths: list, cols: int, thumb_w: int, thumb_h: int, out_path: str):
    rows = (len(img_paths) + cols - 1) // cols
    pad = 22
    lbl_h = 52
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (thumb_h + lbl_h + pad) + pad), (15, 20, 18))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_BOLD, 18)
    for idx, p in enumerate(img_paths):
        im = Image.open(p).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        r, c = idx // cols, idx % cols
        x = pad + c * (thumb_w + pad) + (thumb_w - im.width) // 2
        y = pad + r * (thumb_h + lbl_h + pad)
        sheet.paste(im, (x, y))
        title = os.path.splitext(os.path.basename(p))[0].replace("261122 ", "")
        draw.text((pad + c * (thumb_w + pad), y + thumb_h + 10), title[:48], fill=(255, 228, 130), font=font)
    sheet.save(out_path, quality=94, subsampling=0, icc_profile=SRGB_BYTES)
    shutil.copy2(out_path, os.path.join(BRAIN_DIR, os.path.basename(out_path)))
    print("Saved QC grid ->", out_path, flush=True)


def sync_all():
    av_src = os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke")
    ht_src = os.path.join(OUT_ROOT, "02_Hang_Thu_Pharma_18_Thiet_Ke")
    targets = [
        (av_src, r"Z:\Máy tính khác\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261122 - Bộ 8 Thiết Kế Infographic An Vượng Pharma"),
        (av_src, r"Z:\Drive của tôi\dự án ngoài\An Vượng\261122 - Bộ 8 Thiết Kế Infographic An Vượng Pharma"),
        (ht_src, r"Z:\Máy tính khác\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261122 - Bộ 18 Thiết Kế Infographic Hằng Thu Pharma"),
        (OUT_ROOT, r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\261122-26-thiet-ke-infographic-av-htpm\Final_Deliverables"),
    ]
    for src, dst in targets:
        os.makedirs(dst, exist_ok=True)
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print("Synced ->", dst, flush=True)

    for code_dst in [
        r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\261122-26-thiet-ke-infographic-av-htpm\code",
        r"d:\AI\full studio\edit\canvas-tools\posters_26_av_htpm",
    ]:
        os.makedirs(code_dst, exist_ok=True)
        for ext in ("*.py", "*.js"):
            for f in glob.glob(os.path.join(V3_DIR, ext)):
                if not os.path.basename(f).startswith("_"):
                    shutil.copy2(f, os.path.join(code_dst, os.path.basename(f)))
        print("Synced code ->", code_dst, flush=True)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = [pool.submit(process_one, sp) for sp in POSTERS_26]
        for ft in as_completed(futs):
            ft.result()

    av_jpgs = sorted(glob.glob(os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke", "**", "*.jpg"), recursive=True))
    ht_jpgs = sorted(glob.glob(os.path.join(OUT_ROOT, "02_Hang_Thu_Pharma_18_Thiet_Ke", "**", "*.jpg"), recursive=True))

    build_benchmark_sheet()
    make_grid(av_jpgs, cols=4, thumb_w=460, thumb_h=690, out_path=os.path.join(AUDIT_DIR, "V4_QC_01_An_Vuong_8_Masterpieces.jpg"))
    make_grid(ht_jpgs[:9], cols=3, thumb_w=460, thumb_h=690, out_path=os.path.join(AUDIT_DIR, "V4_QC_02_Hang_Thu_Part1_9Masterpieces.jpg"))
    make_grid(ht_jpgs[9:], cols=3, thumb_w=460, thumb_h=690, out_path=os.path.join(AUDIT_DIR, "V4_QC_03_Hang_Thu_Part2_9Masterpieces.jpg"))

    # Copy 4 full-size showcase posters to BRAIN_DIR for 100% zoom carousel inspection
    for pick in (av_jpgs[0], av_jpgs[2], ht_jpgs[0], ht_jpgs[10]):
        shutil.copy2(pick, os.path.join(BRAIN_DIR, "V4_" + os.path.basename(pick)))

    sync_all()
    print("ALL 26 V4 CHATGPT MASTERPIECE POSTERS + PSDs SYNCED!", flush=True)
