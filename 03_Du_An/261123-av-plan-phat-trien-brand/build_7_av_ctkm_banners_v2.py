# -*- coding: utf-8 -*-
"""
AN VƯỢNG PHARMA × DROPPII 8TH ANNIVERSARY — V2 FLAGSHIP LUXURY STUDIO ENGINE
- Completely redesigned Art Direction: Imperial Botanical Emerald (#053322) × Brushed 24K Champagne Gold (#E5B95C) × Ruby Velvet (#9E0E1C)
- 100% Grounded 2-Tier Calacatta Gold Marble Choreography (ZERO boxes floating on top of tilted boxes!)
- ZERO Windows Emojis — 100% Bespoke Vector SVG Luxury Icons
- Clean 8K Official Logo Extraction + Repaired Crisp Box Bottom Edges
- Exports 7 Master .JPGs (1600x1600 & 1600x2000, sRGB ICC, Q=98) + 7 Editable 4-Layer .PSDs + QC Sheet
"""
import base64, io, math, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import packbits
import pytoshop
import pytoshop.codecs
pytoshop.codecs.packbits = packbits
from pytoshop.user import nested_layers
from pytoshop import enums

PROJ_DIR    = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand"
STAGE_DIR   = os.path.join(PROJ_DIR, "assets_stage_v2")
CUT_V2_DIR  = os.path.join(PROJ_DIR, "assets_cutouts_v2")
LOGO_ORIG   = r"G:\Other computers\My Computer\Document HT Media\TLH\An vượng\Logo AN Vượng Pharma Xanh Vàng.png"
FONTS_DIR   = r"C:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi"

HTML_DIR    = os.path.join(PROJ_DIR, "tmp_html_banners_v2")
OUT_BANNERS = os.path.join(PROJ_DIR, "01_Bo_6_Banner_CTKM_23_30_11_Va_The_Len_Don")
OUT_PSD     = os.path.join(OUT_BANNERS, "File_PSD_Chinh_Sua_Da_Layer")
AUDIT_DIR   = os.path.join(PROJ_DIR, "audit")

for d in (HTML_DIR, OUT_BANNERS, OUT_PSD, AUDIT_DIR):
    os.makedirs(d, exist_ok=True)

SRGB_PROFILE = ImageCms.createProfile("sRGB")
SRGB_BYTES   = ImageCms.ImageCmsProfile(SRGB_PROFILE).tobytes()

LEGAL_TPBS = "Thực phẩm bổ sung. Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh."

def find_browser_exe() -> str:
    for c in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ]:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("No Chromium browser found!")

BROWSER_EXE = find_browser_exe()

def image_to_data_uri(im: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    im.save(buf, format=fmt)
    mime = "image/png" if fmt.upper() == "PNG" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def prepare_clean_logo(src_path: str) -> Image.Image:
    """Extracts crisp 8K An Vượng Pharma logo from white background with zero color halo."""
    im = Image.open(src_path).convert("RGBA")
    arr = np.array(im, dtype=np.float32)
    rgb = arr[:, :, :3]
    # Check if already transparent
    if arr[:, :, 3].min() < 15:
        ys, xs = np.where(arr[:, :, 3] > 20)
        return im.crop((max(0, xs.min() - 6), max(0, ys.min() - 6), min(im.width, xs.max() + 7), min(im.height, ys.max() + 7)))
    # White background matting
    whiteness = rgb.min(axis=2)
    dist_from_white = 255.0 - whiteness
    # Also preserve warm gold highlights that have high R/G but lower B
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    signal = np.maximum(dist_from_white, chroma * 1.35)
    alpha = np.clip((signal - 12.0) / 38.0, 0.0, 1.0)
    denom = np.maximum(alpha[:, :, None], 0.28)
    rgb_unwhite = np.clip((rgb - (1.0 - alpha[:, :, None]) * 255.0) / denom, 0.0, 255.0)
    out = np.dstack([rgb_unwhite, alpha * 255.0]).astype(np.uint8)
    res = Image.fromarray(out, "RGBA")
    ys, xs = np.where(out[:, :, 3] > 20)
    return res.crop((max(0, int(xs.min()) - 8), max(0, int(ys.min()) - 8), min(res.width, int(xs.max()) + 9), min(res.height, int(ys.max()) + 9)))

def tight_crop_rgba(im: Image.Image, alpha_thresh: int = 40, pad: int = 4) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    ys, xs = np.where(arr[:, :, 3] > alpha_thresh)
    if len(xs) == 0:
        return im.convert("RGBA")
    return im.convert("RGBA").crop((
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(im.width, int(xs.max()) + 1 + pad),
        min(im.height, int(ys.max()) + 1 + pad),
    ))

def fix_collamela_box(im: Image.Image) -> Image.Image:
    """Repairs the slight sand-notch along the bottom-right dark-green base of Collamela 3/4 box so it sits 100% flat."""
    im = tight_crop_rgba(im, alpha_thresh=45, pad=4)
    arr = np.array(im).copy()
    h, w = arr.shape[:2]
    # Find front bottom corner (lowest point in x: 12%..32%) and right bottom corner (lowest point in x: 88%..99%)
    a = arr[:, :, 3] > 160
    x_front_band = range(int(w * 0.14), int(w * 0.28))
    best_fx, best_fy = int(w * 0.19), int(h * 0.985)
    max_y = 0
    for x in x_front_band:
        ys = np.where(a[:, x])[0]
        if len(ys) and ys[-1] > max_y:
            max_y = int(ys[-1])
            best_fx, best_fy = x, max_y

    x_right_band = range(int(w * 0.90), int(w * 0.99))
    best_rx, best_ry = int(w * 0.96), int(h * 0.87)
    for x in reversed(list(x_right_band)):
        ys = np.where(a[:, x])[0]
        if len(ys) > 30:
            best_rx, best_ry = x, int(ys[-1])
            break

    # Fill any notched pixels above the straight line connecting (best_fx, best_fy) -> (best_rx, best_ry)
    for x in range(best_fx, best_rx + 1):
        t = (x - best_fx) / max(1, (best_rx - best_fx))
        target_y = int(round(best_fy * (1.0 - t) + best_ry * t))
        ys = np.where(a[:, x])[0]
        if len(ys) == 0:
            continue
        cur_bottom = int(ys[-1])
        if cur_bottom < target_y and (target_y - cur_bottom) < int(h * 0.10):
            # Sample clean dark-emerald color slightly above cur_bottom
            sample_y = max(0, cur_bottom - 10)
            sample_rgb = arr[sample_y, x, :3]
            for fill_y in range(max(0, cur_bottom - 2), min(h, target_y + 1)):
                arr[fill_y, x, :3] = sample_rgb
                arr[fill_y, x, 3] = 255
    # Smooth alpha along the repaired bottom edge
    a_blur = cv2.GaussianBlur(arr[:, :, 3], (3, 3), 0.6)
    arr[int(h * 0.84):, :, 3] = np.where(arr[int(h * 0.84):, :, 3] > 200, 255, a_blur[int(h * 0.84):, :])
    return Image.fromarray(arr, "RGBA")

def polish_box(im: Image.Image) -> Image.Image:
    im = tight_crop_rgba(im, alpha_thresh=42, pad=4)
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b))
    # Subtle warm studio polish so white cardboard matches warm champagne lighting
    rgb = ImageEnhance.Brightness(rgb).enhance(1.04)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
    rgb = ImageEnhance.Color(rgb).enhance(1.04)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.16)
    r2, g2, b2 = rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))

def build_collamela_10goi_box(collamela_clean: Image.Image) -> Image.Image:
    """Creates crisp Collamela 10-sachet (40g) gift box from the repaired 20-sachet box."""
    im = collamela_clean.copy()
    w, h = im.size
    arr = np.array(im)
    x0, y0, x1, y1 = int(w * 0.75), int(h * 0.72), int(w * 0.96), int(h * 0.89)
    sub = arr[y0:y1, x0:x1]
    ymask = (sub[:, :, 3] > 200) & (sub[:, :, 0] > 165) & (sub[:, :, 1] > 140) & (sub[:, :, 2] < 125)
    ys, xs = np.where(ymask)
    if len(xs) > 90:
        bx0 = x0 + int(xs.min()) - 4
        by0 = y0 + int(ys.min()) - 4
        bx1 = x0 + int(xs.max()) + 4
        by1 = y0 + int(ys.max()) + 4
        draw = ImageDraw.Draw(im)
        bw, bh = bx1 - bx0, by1 - by0
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=max(6, bw // 14), fill=(9, 58, 36, 255), outline=(232, 194, 92, 255), width=max(3, bw // 38))
        top_h = int(bh * 0.45)
        draw.rounded_rectangle([bx0 + 3, by0 + 3, bx1 - 3, by0 + top_h], radius=max(4, bw // 18), fill=(238, 202, 96, 255))
        f_top = ImageFont.truetype(os.path.join(FONTS_DIR.replace("/", os.sep), "Montserrat-ExtraBold.ttf"), max(14, int(bh * 0.23)))
        f_bot = ImageFont.truetype(os.path.join(FONTS_DIR.replace("/", os.sep), "Montserrat-Bold.ttf"), max(14, int(bh * 0.27)))
        draw.text((bx0 + bw // 2, by0 + top_h // 2 + 1), "10 gói x 4g", fill=(8, 46, 28, 255), font=f_top, anchor="mm")
        draw.text((bx0 + bw // 2, by0 + top_h + (bh - top_h) // 2), "40 g", fill=(248, 224, 132, 255), font=f_bot, anchor="mm")
    return im

def load_all_boxes() -> dict:
    bojomi_34_p = os.path.join(PROJ_DIR, "Daily_Work", "Ngay_01_2411", "video_03_bojomi", "07_HyperFrames_Project", "assets", "images", "box_main.png")
    colla_34_p  = os.path.join(PROJ_DIR, "Daily_Work", "Ngay_01_2411", "video_04_collamela", "07_HyperFrames_Project", "assets", "images", "box_main.png")

    colla_fixed = polish_box(fix_collamela_box(Image.open(colla_34_p)))
    return {
        "protein":       polish_box(Image.open(os.path.join(CUT_V2_DIR, "av01_protein_a.png"))),
        "protein_fr":    polish_box(Image.open(os.path.join(CUT_V2_DIR, "av01_protein_b.png"))),
        "bojomi":        polish_box(Image.open(bojomi_34_p)),
        "bojomi_hero":   polish_box(Image.open(os.path.join(CUT_V2_DIR, "av02_bojomi_a.png"))),
        "bojomi_stick":  polish_box(Image.open(os.path.join(CUT_V2_DIR, "av02_bojomi_stick.png"))),
        "collamela":     colla_fixed,
        "collamela_hero": polish_box(Image.open(os.path.join(CUT_V2_DIR, "av03_collamela_a.png"))),
        "colla10":       build_collamela_10goi_box(colla_fixed),
        "curcumilk":     polish_box(Image.open(os.path.join(CUT_V2_DIR, "av04_curcumilk_b.png"))),
        "curcumilk_hero": polish_box(Image.open(os.path.join(CUT_V2_DIR, "av04_curcumilk_a.png"))),
    }

def draw_gift_pedestal_glow(layer: Image.Image, cx: int, bottom_y: int, box_h: int):
    """Subtle warm champagne spotlight halo behind the VIP Gift Box — grounded directly on real Calacatta marble!"""
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    rad = int(box_h * 0.68)
    cy = bottom_y - int(box_h * 0.52)
    for step in range(8, 0, -1):
        r = int(rad * (step / 8.0))
        alpha = int(26 * (1.0 - step / 9.0))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 230, 150, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    layer.alpha_composite(glow)

def paste_box_studio(layer: Image.Image, box_im: Image.Image, cx: int, bottom_y: int, target_h: int,
                     shadow_alpha: int = 135, reflect: bool = True, warm_rim: bool = True) -> tuple:
    """Places a product cutout with realistic marble reflection, tight contact AO shadow, and warm rim light."""
    scale = target_h / box_im.height
    nw, nh = max(12, int(round(box_im.width * scale))), max(12, int(round(target_h)))
    im = box_im.resize((nw, nh), Image.Resampling.LANCZOS)

    if warm_rim:
        # Delicate champagne rim glow on outer 2px edge so box blends into studio light
        arr = np.array(im, dtype=np.float32)
        a_u8 = arr[:, :, 3].astype(np.uint8)
        inner = cv2.erode(a_u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
        rim = np.clip((a_u8.astype(np.float32) - inner.astype(np.float32)) / 255.0, 0.0, 1.0)
        rim = cv2.GaussianBlur(rim, (5, 5), 1.0) * 0.26
        arr[:, :, 0] = np.clip(arr[:, :, 0] + rim * 52.0, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + rim * 42.0, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + rim * 18.0, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")

    x0 = int(round(cx - nw / 2))
    y0 = int(round(bottom_y - nh))

    # 1. Subtle glossy marble reflection
    if reflect:
        ref = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        ref_h = min(nh // 5, 68)
        ref = ref.crop((0, 0, nw, ref_h))
        r_arr = np.array(ref, dtype=np.float32)
        grad = np.linspace(0.16, 0.0, ref_h, dtype=np.float32)[:, None]
        r_arr[:, :, 3] = np.clip(r_arr[:, :, 3] * grad, 0, 255)
        ref_im = Image.fromarray(r_arr.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(2.4))
        layer.alpha_composite(ref_im, (x0, bottom_y - 4))

    # 2. Dual-pass Grounded Contact AO + Soft Cast Shadow (warm umber-emerald tone, NOT cold blue!)
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh, "RGBA")
    ell_w = int(nw * 0.90)
    ell_h = max(16, int(nw * 0.13))
    d.ellipse([cx - ell_w // 2, bottom_y - ell_h // 2 + 1, cx + ell_w // 2, bottom_y + ell_h // 2 + 5],
              fill=(38, 28, 12, shadow_alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    # Tight contact crease right under box base
    sh_tight = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    dt = ImageDraw.Draw(sh_tight, "RGBA")
    cw = int(nw * 0.76)
    ch = max(8, int(nw * 0.055))
    dt.ellipse([cx - cw // 2, bottom_y - ch // 2, cx + cw // 2, bottom_y + ch // 2 + 2],
               fill=(22, 16, 6, min(215, shadow_alpha + 55)))
    sh_tight = sh_tight.filter(ImageFilter.GaussianBlur(4.2))
    layer.alpha_composite(sh)
    layer.alpha_composite(sh_tight)

    # 3. Crisp product box
    layer.alpha_composite(im, (x0, y0))
    return (x0, y0, x0 + nw, y0 + nh)

def build_mini_combo_thumb_uri(boxes: dict, keys_list: list, gift_key: str) -> str:
    """Renders a crisp transparent mini packshot thumbnail for Banner 07's 6-Combo Reference Grid!"""
    tw, th = 220, 168
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    n = len(keys_list)
    if n == 1:
        paste_box_studio(canvas, boxes[keys_list[0]], 74, 154, 134, shadow_alpha=95, reflect=False)
    elif n == 2:
        paste_box_studio(canvas, boxes[keys_list[0]], 54, 148, 122, shadow_alpha=85, reflect=False)
        paste_box_studio(canvas, boxes[keys_list[1]], 104, 156, 126, shadow_alpha=95, reflect=False)
    else:
        xs = np.linspace(38, 118, n)
        for idx, k in enumerate(keys_list):
            by = 144 if idx % 2 == 0 else 156
            paste_box_studio(canvas, boxes[k], int(xs[idx]), by, 108, shadow_alpha=80, reflect=False)
    # Mini gift box on right with small ruby '+' badge
    paste_box_studio(canvas, boxes[gift_key], 178, 156, 118, shadow_alpha=95, reflect=False)
    d = ImageDraw.Draw(canvas, "RGBA")
    d.ellipse([126, 84, 152, 110], fill=(178, 18, 32, 255), outline=(252, 224, 138, 255), width=2)
    f_plus = ImageFont.truetype(os.path.join(FONTS_DIR.replace("/", os.sep), "Montserrat-Black.ttf"), 18)
    d.text((139, 97), "+", fill=(255, 255, 255, 255), font=f_plus, anchor="mm")
    return image_to_data_uri(canvas, "PNG")

def render_html_to_rgba(html_path: str, out_png: str, w: int, h: int) -> Image.Image:
    raw_png = out_png.replace(".png", "_2x.png")
    cmd = [
        BROWSER_EXE,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        "--force-device-scale-factor=2",
        "--default-background-color=00000000",
        f"--screenshot={raw_png}",
        f"file:///{html_path.replace(os.sep, '/')}",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(raw_png).convert("RGBA")
    if im.size != (w, h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    im.save(out_png)
    try:
        os.remove(raw_png)
    except OSError:
        pass
    return im

def save_multilayer_psd(layers_named: list, out_psd_path: str, w: int, h: int):
    psd_layers = []
    for name, im_rgba in reversed(layers_named):
        arr = np.array(im_rgba.convert("RGBA"), dtype=np.uint8)
        channels = {0: arr[:, :, 0], 1: arr[:, :, 1], 2: arr[:, :, 2], -1: arr[:, :, 3]}
        psd_layers.append(
            nested_layers.Image(
                name=name, visible=True, opacity=255, group_id=0,
                blend_mode=enums.BlendMode.normal,
                top=0, left=0, bottom=h, right=w, channels=channels,
            )
        )
    psd = nested_layers.nested_layers_to_psd(
        psd_layers, color_mode=enums.ColorMode.rgb, size=(w, h), compression=enums.Compression.rle,
    )
    with open(out_psd_path, "wb") as f:
        psd.write(f)

def font_faces_css() -> str:
    return f"""
    @font-face {{ font-family: 'MontBlack'; src: url('file:///{FONTS_DIR}/Montserrat-Black.ttf'); font-weight: 900; }}
    @font-face {{ font-family: 'MontEB'; src: url('file:///{FONTS_DIR}/Montserrat-ExtraBold.ttf'); font-weight: 800; }}
    @font-face {{ font-family: 'MontBold'; src: url('file:///{FONTS_DIR}/Montserrat-Bold.ttf'); font-weight: 700; }}
    @font-face {{ font-family: 'BeVNExtra'; src: url('file:///{FONTS_DIR}/BeVietnamPro-ExtraBold.ttf'); font-weight: 800; }}
    @font-face {{ font-family: 'BeVNBold'; src: url('file:///{FONTS_DIR}/BeVietnamPro-Bold.ttf'); font-weight: 700; }}
    @font-face {{ font-family: 'BeVNSemi'; src: url('file:///{FONTS_DIR}/BeVietnamPro-SemiBold.ttf'); font-weight: 600; }}
    @font-face {{ font-family: 'PlayfairEB'; src: url('file:///{FONTS_DIR}/PlayfairDisplay-BoldItalic.ttf'); font-weight: 700; font-style: italic; }}
    @font-face {{ font-family: 'PlayfairBold'; src: url('file:///{FONTS_DIR}/PlayfairDisplay-ExtraBold.ttf'); font-weight: 800; }}
    @font-face {{ font-family: 'FrauncesBlk'; src: url('file:///{FONTS_DIR}/Fraunces-Black.ttf'); font-weight: 900; }}
    """

# =============================================================================
# BESPOKE LUXURY VECTOR SVG ICONS (0% WINDOWS EMOJIS!)
# =============================================================================
SVG_CALENDAR = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="16" rx="3" stroke="#C9962B" stroke-width="2.2"/><path d="M3 10H21" stroke="#C9962B" stroke-width="2.2"/><path d="M8 3V6M16 3V6" stroke="#063D28" stroke-width="2.2" stroke-linecap="round"/><circle cx="8.5" cy="14.5" r="1.4" fill="#063D28"/><circle cx="12" cy="14.5" r="1.4" fill="#063D28"/><circle cx="15.5" cy="14.5" r="1.4" fill="#B81222"/></svg>"""
SVG_GIFT_CROWN = """<svg width="26" height="26" viewBox="0 0 24 24" fill="none"><rect x="3" y="10" width="18" height="11" rx="2" fill="#FFF3C4" fill-opacity="0.18" stroke="#FFE394" stroke-width="2"/><path d="M2 7.5C2 6.67 2.67 6 3.5 6H20.5C21.33 6 22 6.67 22 7.5V10H2V7.5Z" fill="#FFE394"/><path d="M12 6V21" stroke="#FFE394" stroke-width="2.2"/><path d="M12 6C9.5 6 7.5 4.6 7.5 3.2C7.5 2.1 8.6 1.5 9.8 2.1C10.9 2.6 11.6 4.4 12 6ZM12 6C14.5 6 16.5 4.6 16.5 3.2C16.5 2.1 15.4 1.5 14.2 2.1C13.1 2.6 12.4 4.4 12 6Z" stroke="#FFE394" stroke-width="2" stroke-linejoin="round"/></svg>"""
SVG_SPARK = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="#E5B95C"/></svg>"""
SVG_CHECK_GOLD = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#E8BF62"/><path d="M7.5 12.3L10.5 15.3L16.8 9" stroke="#053322" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

# =============================================================================
# 6 VERIFIED CTKM BANNERS — GROUNDED 2-TIER CALACATTA MARBLE CHOREOGRAPHY
# Upper Marble Tier surface: Y = 1148 | Lower Marble Tier surface: Y = 1258
# =============================================================================
CTKM_BANNERS = [
    {
        "id": "CTKM_01",
        "filename": "261123 AVPM CTKM 01 - Combo 4 San Pham Tang Collamela 20 Goi",
        "badge_left": "MUA COMBO 4 SP",
        "headline_html": """
            <div class="combo-grid-4">
              <div class="cg-item">""" + SVG_CHECK_GOLD + """<span>01 Hộp AV Protein</span></div>
              <div class="cg-item">""" + SVG_CHECK_GOLD + """<span>01 Hộp Sữa BOJOMI</span></div>
              <div class="cg-item">""" + SVG_CHECK_GOLD + """<span>01 Collamela (20 gói)</span></div>
              <div class="cg-item">""" + SVG_CHECK_GOLD + """<span>01 Curcumilk Phyto</span></div>
            </div>
        """,
        "pillar_strip": ["Đạm Thực Vật 22g", "Canxi Tảo Biển D3K2", "Collagen Tripeptide", "Nghệ Phytosome"],
        "boxes": [
            # Upper Marble Tier (Y=1148, h=472 -> top=676, brand title ends Y=888) — 100% grounded on marble!
            ("protein_fr",     365, 1148, 472, 115, False),
            ("bojomi",         680, 1148, 472, 115, False),
            # Lower Marble Tier (Y=1268, h=368 -> top=900) — sits cleanly below back-row brand titles!
            ("collamela",      255, 1266, 366, 145, True),
            ("curcumilk",      535, 1268, 374, 145, True),
            ("bojomi_stick",   775, 1266, 330, 130, True),
        ],
        "plus_pos": (952, 990),
        "gift_box": ("collamela", 1235, 1252, 468, 150, True),
        "gift_name": "01 HỘP COLLAMELA",
        "gift_subtag": "HỘP QUÀ 20 GÓI × 4G",
        "gift_value": "920.000đ",
        "price_label": "TRỌN BỘ COMBO 4 SẢN PHẨM",
        "price_val": "2.440.000đ",
        "save_val": "920.000đ",
        "thumb_keys": (["protein_fr", "bojomi", "curcumilk"], "collamela"),
    },
    {
        "id": "CTKM_02",
        "filename": "261123 AVPM CTKM 02 - Mua 5 Hop AV Protein Tang 1 Bojomi",
        "badge_left": "MUA <b>05</b> HỘP",
        "headline_html": """
            <div class="hl-stack">
              <div class="hl-sub">Đạm Thực Vật Thuần Khiết • 22g Protein/Khẩu Phần</div>
              <div class="hl-main">AV PROTEIN <span class="hl-chip">Hộp 20 gói × 15g</span></div>
            </div>
        """,
        "pillar_strip": None,
        "boxes": [
            # Upper Marble Tier (Y=1148, h=488 -> top=660, 'AV PROTEIN' title ends Y=882)
            ("protein_fr", 365, 1148, 488, 115, False),
            ("protein_fr", 648, 1148, 488, 115, False),
            # Lower Marble Tier (Y=1268, h=376 -> top=892) — ALL 5 'AV PROTEIN' titles 100% readable & grounded!
            ("protein",    232, 1262, 376, 140, True),
            ("protein",    778, 1262, 376, 140, True),
            ("protein_fr", 506, 1268, 386, 150, True),
        ],
        "plus_pos": (958, 990),
        "gift_box": ("bojomi", 1235, 1252, 478, 150, True),
        "gift_name": "01 HỘP SỮA BOJOMI",
        "gift_subtag": "HỘP QUÀ 14 GÓI × 20G",
        "gift_value": "520.000đ",
        "price_label": "TỔNG COMBO 05 HỘP AV PROTEIN",
        "price_val": "1.750.000đ",
        "save_val": "520.000đ",
        "thumb_keys": (["protein_fr", "protein"], "bojomi"),
    },
    {
        "id": "CTKM_03",
        "filename": "261123 AVPM CTKM 03 - Mua 3 Hop Bojomi Tang 1 Bojomi",
        "badge_left": "MUA <b>03</b> HỘP",
        "headline_html": """
            <div class="hl-stack">
              <div class="hl-sub">Ngũ Cốc Dinh Dưỡng Xương Khớp • Canxi Tảo Biển & D3K2</div>
              <div class="hl-main">BOJOMI <span class="hl-chip">Hộp 14 gói × 20g</span></div>
            </div>
        """,
        "pillar_strip": None,
        "boxes": [
            # Wide Hero Trio — 2 flanked on Upper Marble Tier + 1 center front on Lower Marble Tier
            ("bojomi",      298, 1148, 455, 115, False),
            ("bojomi",      722, 1148, 455, 115, False),
            ("bojomi_hero", 510, 1266, 435, 150, True),
        ],
        "plus_pos": (955, 990),
        "gift_box": ("bojomi", 1235, 1252, 478, 150, True),
        "gift_name": "01 HỘP SỮA BOJOMI",
        "gift_subtag": "TỔNG NHẬN ĐỦ 04 HỘP",
        "gift_value": "520.000đ",
        "price_label": "TỔNG COMBO 03 HỘP BOJOMI",
        "price_val": "1.560.000đ",
        "save_val": "520.000đ",
        "thumb_keys": (["bojomi_hero", "bojomi"], "bojomi"),
    },
    {
        "id": "CTKM_04",
        "filename": "261123 AVPM CTKM 04 - Mua 4 Hop Curcumilk Phyto Tang 1 Curcumilk",
        "badge_left": "MUA <b>04</b> HỘP",
        "headline_html": """
            <div class="hl-stack">
              <div class="hl-sub">Sữa Nghệ Công Nghệ Curcumin Phytosome • Êm Dịu Dạ Dày</div>
              <div class="hl-main">CURCUMILK PHYTO <span class="hl-chip">14 gói × 15g</span></div>
            </div>
        """,
        "pillar_strip": None,
        "boxes": [
            # 2 Upper Marble Tier (Y=1148, h=485 -> top=663) + 2 Lower Marble Tier (Y=1268, h=376 -> top=892)
            ("curcumilk",      365, 1148, 485, 115, False),
            ("curcumilk",      682, 1148, 485, 115, False),
            ("curcumilk",      258, 1264, 376, 140, True),
            ("curcumilk_hero", 575, 1268, 386, 150, True),
        ],
        "plus_pos": (952, 990),
        "gift_box": ("curcumilk", 1235, 1252, 478, 150, True),
        "gift_name": "01 HỘP CURCUMILK",
        "gift_subtag": "TỔNG NHẬN ĐỦ 05 HỘP",
        "gift_value": "650.000đ",
        "price_label": "TỔNG COMBO 04 HỘP CURCUMILK",
        "price_val": "2.600.000đ",
        "save_val": "650.000đ",
        "thumb_keys": (["curcumilk_hero", "curcumilk"], "curcumilk"),
    },
    {
        "id": "CTKM_05",
        "filename": "261123 AVPM CTKM 05 - Mua 2 Hop Collamela 20 Goi Tang 1 Hop 10 Goi",
        "badge_left": "MUA <b>02</b> HỘP",
        "headline_html": """
            <div class="hl-stack">
              <div class="hl-sub">Tinh Chất Dưỡng Sáng & Đàn Hồi Làn Da • Collagen Tripeptide</div>
              <div class="hl-main">COLLAMELA <span class="hl-chip">Hộp 20 gói × 4g</span></div>
            </div>
        """,
        "pillar_strip": None,
        "boxes": [
            # Wide Asymmetric Duo — BOTH Collamela boxes grounded & 100% readable!
            ("collamela",      675, 1148, 455, 120, False),
            ("collamela_hero", 335, 1264, 462, 150, True),
        ],
        "plus_pos": (955, 990),
        "gift_box": ("colla10", 1235, 1252, 422, 150, True),
        "gift_name": "01 COLLAMELA 10 GÓI",
        "gift_subtag": "HỘP QUÀ 10 GÓI × 4G (40G)",
        "gift_value": "480.000đ",
        "price_label": "TỔNG COMBO 02 HỘP COLLAMELA (20 GÓI)",
        "price_val": "1.840.000đ",
        "save_val": "480.000đ",
        "thumb_keys": (["collamela_hero", "collamela"], "colla10"),
    },
    {
        "id": "CTKM_06",
        "filename": "261123 AVPM CTKM 06 - Combo 2 Bojomi 2 Curcumilk Tang 1 Bojomi",
        "badge_left": "MUA COMBO",
        "headline_html": """
            <div class="hl-stack">
              <div class="hl-sub">Bộ Đôi Chăm Sóc Hệ Xương Khớp & Tiêu Hóa Khỏe Mạnh</div>
              <div class="hl-main sm">02 HỘP BOJOMI + 02 HỘP CURCUMILK PHYTO</div>
            </div>
        """,
        "pillar_strip": None,
        "boxes": [
            # 2 Bojomi on Upper Marble Tier (Y=1148, h=485) + 2 Curcumilk on Lower Marble Tier (Y=1268, h=376)
            ("bojomi",         365, 1148, 485, 115, False),
            ("bojomi",         682, 1148, 485, 115, False),
            ("curcumilk",      258, 1264, 376, 140, True),
            ("curcumilk_hero", 575, 1268, 386, 150, True),
        ],
        "plus_pos": (952, 990),
        "gift_box": ("bojomi", 1235, 1252, 478, 150, True),
        "gift_name": "01 HỘP SỮA BOJOMI",
        "gift_subtag": "HỘP QUÀ 14 GÓI × 20G",
        "gift_value": "520.000đ",
        "price_label": "COMBO 02 BOJOMI + 02 CURCUMILK",
        "price_val": "2.340.000đ",
        "save_val": "520.000đ",
        "thumb_keys": (["bojomi", "curcumilk"], "bojomi"),
    },
]

def build_ctkm_html(spec: dict, logo_uri: str, gift_bbox: tuple, pass_mode: str) -> str:
    gx0, gy0, gx1, gy1 = gift_bbox
    gcx = (gx0 + gx1) // 2
    px, py = spec["plus_pos"]
    is_decor = (pass_mode == "decor")
    decor_vis = "visible" if is_decor else "hidden"
    text_vis  = "hidden"  if is_decor else "visible"

    pillars_html = ""
    if spec.get("pillar_strip"):
        chips = "".join([
            f'<div class="p-chip"><span class="p-dot"></span><span>{t}</span></div>'
            for t in spec["pillar_strip"]
        ])
        pillars_html = f'<div class="pillar-strip" style="visibility:{text_vis}">{chips}</div>'

    gift_header_top = max(515, gy0 - 122)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<style>
{font_faces_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1600px; height: 1600px; overflow: hidden;
  background: transparent; position: relative;
  font-family: 'BeVNBold', sans-serif;
  -webkit-font-smoothing: antialiased;
}}

/* ---- 1. ROYAL CO-BRAND MEDALLION CREST (TOP ARCH CROWN) ---- */
.cobrand-plaque-bg {{
  position: absolute; top: 20px; left: 455px; width: 690px; height: 102px;
  background: linear-gradient(180deg, #FFFEFA 0%, #FBF3E0 100%);
  border: 3px solid #D9AB4E; border-radius: 51px;
  box-shadow: 0 12px 30px rgba(3, 28, 18, 0.34), inset 0 2px 0 #FFFFFF, 0 0 0 5px rgba(229,185,92,0.18);
  visibility: {decor_vis};
}}
.cobrand-plaque-txt {{
  position: absolute; top: 20px; left: 455px; width: 690px; height: 102px;
  display: flex; align-items: center; justify-content: center; gap: 26px; padding: 0 34px;
  visibility: {text_vis};
}}
.av-logo-img {{ height: 76px; width: auto; display: block; }}
.crest-sep {{
  width: 2px; height: 54px;
  background: linear-gradient(180deg, transparent, #C9962E, transparent);
}}
.droppii-lockup {{
  display: flex; align-items: center;
  font-family: 'MontBlack', sans-serif; font-size: 58px; letter-spacing: -2px;
  color: #1046BE; line-height: 1;
}}
.droppii-dot {{
  display: inline-block; width: 13px; height: 13px; border-radius: 50%;
  background: linear-gradient(135deg, #FF7B2E, #E32929);
  margin-left: 3px; transform: translateY(-16px);
}}

/* ---- 2. ANNIVERSARY GALA LOCKUP (CLEAN SUNLIT ARCH INTERIOR) ---- */
.gala-backdrop-glow {{
  position: absolute; top: 162px; left: 260px; right: 260px; height: 175px;
  background: radial-gradient(ellipse at center, rgba(255,252,243,0.92) 0%, rgba(255,250,236,0.68) 52%, rgba(255,250,236,0.0) 80%);
  pointer-events: none;
  visibility: {decor_vis};
}}
.gala-header {{
  position: absolute; top: 176px; left: 0; right: 0;
  display: flex; flex-direction: column; align-items: center;
  visibility: {text_vis};
}}
.gala-kicker {{
  display: inline-flex; align-items: center; gap: 10px;
  font-family: 'BeVNExtra', sans-serif; font-size: 20px; letter-spacing: 2.8px;
  color: #7D530B; text-transform: uppercase;
  background: rgba(255, 250, 235, 0.85);
  border: 1.5px solid rgba(212, 164, 66, 0.65);
  padding: 5px 22px; border-radius: 999px;
  margin-bottom: 4px;
}}
.gala-title-row {{
  display: flex; align-items: baseline; justify-content: center; gap: 16px;
}}
.gala-script {{
  font-family: 'PlayfairEB', serif; font-size: 82px; line-height: 1.05;
  color: #063B27;
  text-shadow: 0 2px 0 rgba(255,255,255,0.9), 0 8px 22px rgba(6,59,39,0.14);
}}
.eight-3d-wrap {{
  position: relative; display: inline-flex; align-items: baseline; margin: 0 2px;
}}
.eight-3d-shadow {{
  position: absolute; left: 0; top: 4px;
  font-family: 'FrauncesBlk', serif; font-size: 126px; line-height: 0.92;
  color: #7A4B08;
  -webkit-text-stroke: 7px #FFFDF7;
  filter: drop-shadow(0 8px 16px rgba(108,65,8,0.28));
}}
.eight-3d-gold {{
  position: relative; z-index: 2;
  font-family: 'FrauncesBlk', serif; font-size: 126px; line-height: 0.92;
  background: linear-gradient(180deg, #FFF7C8 0%, #F2C55A 34%, #B57610 66%, #FCE08B 86%, #8C5606 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.gala-tuoi {{
  font-family: 'PlayfairBold', serif; font-size: 52px; color: #063B27;
  letter-spacing: 0.5px; text-transform: uppercase;
  text-shadow: 0 2px 0 rgba(255,255,255,0.9);
}}

/* ---- 3. IMPERIAL EMERALD & 24K GOLD OFFER PLAQUE ---- */
.offer-plaque-bg {{
  position: absolute; top: 342px; left: 175px; right: 175px; height: 136px;
  background: linear-gradient(135deg, #042B1C 0%, #094A32 50%, #042B1C 100%);
  border: 3px solid #E5B95C; border-radius: 26px;
  box-shadow: 0 18px 38px rgba(4, 38, 25, 0.26), inset 0 0 0 3px rgba(255, 236, 178, 0.16);
  visibility: {decor_vis};
}}
.offer-plaque-inner-line {{
  position: absolute; inset: 7px; border: 1px solid rgba(232, 193, 106, 0.42); border-radius: 20px;
}}
.offer-plaque-txt {{
  position: absolute; top: 342px; left: 175px; right: 175px; height: 136px;
  display: flex; align-items: center; padding: 0 24px; gap: 26px;
  visibility: {text_vis};
}}
.offer-gold-tag {{
  height: 96px; min-width: 305px; padding: 0 28px; border-radius: 18px;
  background: linear-gradient(180deg, #FFF4C6 0%, #ECC05B 52%, #C99126 100%);
  border: 2px solid #FFF8DC;
  box-shadow: 0 8px 18px rgba(0,0,0,0.28);
  display: flex; align-items: center; justify-content: center; gap: 10px;
  font-family: 'MontBlack', sans-serif; font-size: 38px; color: #04291A;
  letter-spacing: -0.5px; white-space: nowrap; flex-shrink: 0;
}}
.offer-gold-tag b {{
  font-size: 64px; color: #9E0C19; line-height: 0.9;
  text-shadow: 0 2px 0 rgba(255,255,255,0.65);
}}
.hl-stack {{ display: flex; flex-direction: column; justify-content: center; gap: 5px; flex: 1; }}
.hl-sub {{
  font-family: 'BeVNSemi', sans-serif; font-size: 22px; color: #F5DC96; letter-spacing: 0.3px;
}}
.hl-main {{
  font-family: 'MontBlack', sans-serif; font-size: 48px; color: #FFFFFF;
  letter-spacing: -0.5px; line-height: 1.05; display: flex; align-items: center; gap: 16px;
  text-shadow: 0 3px 10px rgba(0,0,0,0.32);
}}
.hl-main.sm {{ font-size: 35px; letter-spacing: -0.3px; }}
.hl-chip {{
  font-family: 'BeVNBold', sans-serif; font-size: 21px; color: #FFE8A3;
  background: rgba(255,255,255,0.12); border: 1.5px solid rgba(235,196,104,0.65);
  padding: 6px 16px; border-radius: 999px; font-weight: 700;
}}

.combo-grid-4 {{
  flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 10px 24px;
}}
.cg-item {{
  display: flex; align-items: center; gap: 10px;
  font-family: 'BeVNBold', sans-serif; font-size: 24px; color: #FFFDF6;
}}

/* Optional subtle 4-pillar strip right below plaque on CTKM 01 */
.pillar-strip {{
  position: absolute; top: 490px; left: 205px; right: 205px;
  display: flex; align-items: center; justify-content: center; gap: 14px;
}}
.p-chip {{
  background: rgba(255, 252, 243, 0.92); border: 1.5px solid #D9B056;
  padding: 6px 16px; border-radius: 999px;
  display: flex; align-items: center; gap: 8px;
  font-family: 'BeVNBold', sans-serif; font-size: 18px; color: #063B27;
  box-shadow: 0 4px 12px rgba(6,59,39,0.08);
}}
.p-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #C89224; }}

/* ---- 4. 24K GOLD CONNECTOR '+' MEDALLION ---- */
.plus-medallion {{
  position: absolute; left: {px - 42}px; top: {py - 42}px; width: 84px; height: 84px;
  border-radius: 50%;
  background: linear-gradient(145deg, #FFF3C2 0%, #DFAD42 55%, #9E6A10 100%);
  padding: 5px;
  box-shadow: 0 12px 26px rgba(65, 42, 6, 0.32), 0 0 0 4px rgba(255,250,235,0.75);
  visibility: {decor_vis};
}}
.plus-inner {{
  width: 100%; height: 100%; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #0D5D3E, #042E1E);
  border: 2px solid #FCE296;
  display: flex; align-items: center; justify-content: center;
}}
.plus-txt {{
  position: absolute; left: {px - 42}px; top: {py - 44}px; width: 84px; height: 84px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'MontBlack', sans-serif; font-size: 52px; color: #FFE89E;
  text-shadow: 0 2px 6px rgba(0,0,0,0.45);
  visibility: {text_vis};
}}

/* ---- 5. VIP GIFT CROWN BADGE & SEAL ON RIGHT PEDESTAL ---- */
.gift-crown-bg {{
  position: absolute; left: {gcx - 168}px; top: {gift_header_top}px; width: 336px; height: 96px;
  background: linear-gradient(145deg, #B81222 0%, #7C0813 100%);
  border: 3px solid #F3CF75; border-radius: 22px;
  box-shadow: 0 14px 28px rgba(98, 6, 15, 0.36), inset 0 1px 0 rgba(255,255,255,0.35);
  visibility: {decor_vis};
}}
.gift-crown-txt {{
  position: absolute; left: {gcx - 168}px; top: {gift_header_top}px; width: 336px; height: 96px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px;
  visibility: {text_vis};
}}
.gc-top {{
  display: flex; align-items: center; gap: 8px;
  font-family: 'MontBlack', sans-serif; font-size: 30px; letter-spacing: 1.5px; color: #FFF7D6;
  text-shadow: 0 2px 6px rgba(60,0,6,0.5);
}}
.gc-sub {{
  font-family: 'BeVNBold', sans-serif; font-size: 19px; color: #FFE08C; letter-spacing: 0.6px;
}}

/* Gift Value Luxury Seal (cleanly anchored bottom-right of gift box) */
.gift-seal-bg {{
  position: absolute; left: {min(1292, gx1 - 115)}px; top: {gy1 - 148}px; width: 238px; height: 104px;
  background: linear-gradient(145deg, #A80E1C 0%, #6E0610 100%);
  border: 3px solid #F5D47E; border-radius: 20px;
  box-shadow: 0 12px 26px rgba(70, 4, 10, 0.44), inset 0 0 0 2px rgba(255,235,175,0.22);
  visibility: {decor_vis};
}}
.gift-seal-txt {{
  position: absolute; left: {min(1292, gx1 - 115)}px; top: {gy1 - 148}px; width: 238px; height: 104px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  visibility: {text_vis};
}}
.gs-lbl {{ font-family: 'BeVNBold', sans-serif; font-size: 20px; color: #FCE08D; text-transform: uppercase; letter-spacing: 1.2px; }}
.gs-val {{ font-family: 'MontBlack', sans-serif; font-size: 38px; color: #FFFFFF; line-height: 1.08; text-shadow: 0 2px 8px rgba(0,0,0,0.45); }}

/* Gift Spec Base Pill */
.gift-spec-bg {{
  position: absolute; left: {gcx - 164}px; top: {gy1 + 8}px; width: 328px; height: 38px;
  background: linear-gradient(90deg, #042E1E, #094D33, #042E1E);
  border: 2px solid #E5B95C; border-radius: 999px;
  box-shadow: 0 6px 14px rgba(0,0,0,0.28);
  visibility: {decor_vis};
}}
.gift-spec-txt {{
  position: absolute; left: {gcx - 164}px; top: {gy1 + 8}px; width: 328px; height: 38px;
  display: flex; align-items: center; justify-content: center; white-space: nowrap;
  font-family: 'BeVNExtra', sans-serif; font-size: 18px; color: #FFF3C4; letter-spacing: 0.5px;
  visibility: {text_vis};
}}

/* ---- 6. UNIFIED ROYAL PRICE & SAVINGS PLINTH (FLOOR ZONE Y=1374..1526) ---- */
.plinth-wrap-bg {{
  position: absolute; top: 1374px; left: 88px; right: 88px; height: 150px;
  background: linear-gradient(180deg, #FFFEFA 0%, #F7EED8 100%);
  border: 3.5px solid #D9AB4E; border-radius: 28px;
  box-shadow: 0 18px 38px rgba(3, 28, 18, 0.36), inset 0 2px 0 #FFFFFF;
  display: flex; overflow: hidden;
  visibility: {decor_vis};
}}
.plinth-left-bg {{ flex: 1; }}
.plinth-right-bg {{
  width: 450px;
  background: linear-gradient(145deg, #B51221 0%, #780812 100%);
  border-left: 4px solid #E5B95C;
}}

.plinth-wrap-txt {{
  position: absolute; top: 1374px; left: 88px; right: 88px; height: 150px;
  display: flex; align-items: stretch;
  visibility: {text_vis};
}}
.plinth-left-txt {{
  flex: 1; padding: 0 38px;
  display: flex; align-items: center; justify-content: space-between; gap: 22px;
}}
.pl-meta {{ display: flex; flex-direction: column; gap: 10px; }}
.pl-title {{
  font-family: 'BeVNExtra', sans-serif; font-size: 25px; color: #063B27;
  letter-spacing: 0.4px;
}}
.pl-date {{
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(6, 59, 39, 0.08); border: 1.5px solid rgba(6, 59, 39, 0.22);
  padding: 6px 16px; border-radius: 999px; width: fit-content;
  font-family: 'BeVNBold', sans-serif; font-size: 20px; color: #073B27;
}}
.pl-price {{
  font-family: 'MontBlack', sans-serif; font-size: 76px; color: #053824;
  letter-spacing: -2px; line-height: 1;
  text-shadow: 0 2px 0 #FFFFFF;
}}

.plinth-right-txt {{
  width: 450px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
}}
.pr-lbl {{
  display: flex; align-items: center; gap: 8px;
  font-family: 'BeVNExtra', sans-serif; font-size: 24px; color: #FFE394;
  letter-spacing: 1.2px; text-transform: uppercase;
}}
.pr-val {{
  font-family: 'MontBlack', sans-serif; font-size: 64px; color: #FFFFFF;
  letter-spacing: -1.5px; line-height: 1.02;
  text-shadow: 0 4px 12px rgba(55, 0, 6, 0.48);
}}

/* ---- 7. LEGAL FOOTER ---- */
.legal-bg {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 52px;
  background: linear-gradient(90deg, #032216 0%, #073D28 50%, #032216 100%);
  border-top: 2px solid #D9AB4E;
  visibility: {decor_vis};
}}
.legal-txt {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 52px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'BeVNSemi', sans-serif; font-size: 20.5px; color: #F7EED8; letter-spacing: 0.2px;
  visibility: {text_vis};
}}
</style>
</head>
<body>
  <div class="cobrand-plaque-bg"></div>
  <div class="cobrand-plaque-txt">
    <img class="av-logo-img" src="{logo_uri}" />
    <div class="crest-sep"></div>
    <div class="droppii-lockup">droppii<span class="droppii-dot"></span></div>
  </div>

  <div class="gala-backdrop-glow"></div>
  <div class="gala-header">
    <div class="gala-kicker">{SVG_SPARK}<span>ĐẠI TIỆC KỶ NIỆM • 23/11 – 30/11/2026</span>{SVG_SPARK}</div>
    <div class="gala-title-row">
      <span class="gala-script">Mừng Sinh Nhật</span>
      <span class="eight-3d-wrap">
        <span class="eight-3d-shadow">8</span>
        <span class="eight-3d-gold">8</span>
      </span>
      <span class="gala-tuoi">Tuổi</span>
    </div>
  </div>

  <div class="offer-plaque-bg"><div class="offer-plaque-inner-line"></div></div>
  <div class="offer-plaque-txt">
    <div class="offer-gold-tag">{spec["badge_left"]}</div>
    {spec["headline_html"]}
  </div>

  {pillars_html}

  <div class="plus-medallion"><div class="plus-inner"></div></div>
  <div class="plus-txt">+</div>

  <div class="gift-crown-bg"></div>
  <div class="gift-crown-txt">
    <div class="gc-top">{SVG_GIFT_CROWN}<span>TẶNG NGAY 0Đ</span></div>
    <div class="gc-sub">{spec["gift_name"]}</div>
  </div>

  <div class="gift-seal-bg"></div>
  <div class="gift-seal-txt">
    <div class="gs-lbl">Trị giá quà tặng</div>
    <div class="gs-val">{spec["gift_value"]}</div>
  </div>

  <div class="gift-spec-bg"></div>
  <div class="gift-spec-txt">{spec["gift_subtag"]}</div>

  <div class="plinth-wrap-bg">
    <div class="plinth-left-bg"></div>
    <div class="plinth-right-bg"></div>
  </div>
  <div class="plinth-wrap-txt">
    <div class="plinth-left-txt">
      <div class="pl-meta">
        <div class="pl-title">{spec["price_label"]}</div>
        <div class="pl-date">{SVG_CALENDAR}<span>Từ 23/11 đến hết 30/11/2026</span></div>
      </div>
      <div class="pl-price">{spec["price_val"]}</div>
    </div>
    <div class="plinth-right-txt">
      <div class="pr-lbl">Tiết kiệm ngay</div>
      <div class="pr-val">{spec["save_val"]}</div>
    </div>
  </div>

  <div class="legal-bg"></div>
  <div class="legal-txt">{LEGAL_TPBS} • Áp dụng khi chọn đúng Mã Combo trên App Droppii.</div>
</body>
</html>"""

def render_ctkm_banner(spec: dict, stage_bg: Image.Image, boxes: dict, logo_uri: str) -> dict:
    W, H = 1600, 1600
    cid = spec["id"]

    # Layer 1: Luxury 2-Tier Marble & Imperial Emerald Stage
    l1_bg = stage_bg.resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")

    # Layer 2: Grounded 2-Tier Studio Packshots + VIP Gift Pedestal
    l2_prod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gkey, gcx, gby, gth, gsha, grefl = spec["gift_box"]
    draw_gift_pedestal_glow(l2_prod, gcx, gby, gth)

    for key, cx, by, th, sha, refl in spec["boxes"]:
        paste_box_studio(l2_prod, boxes[key], cx, by, th, shadow_alpha=sha, reflect=refl)
    gift_bbox = paste_box_studio(l2_prod, boxes[gkey], gcx, gby, gth, shadow_alpha=gsha, reflect=grefl)

    # Layer 3: Plaques, Plinths, Seals & Frames
    h_dec = os.path.join(HTML_DIR, f"{cid}_decor.html")
    p_dec = os.path.join(HTML_DIR, f"{cid}_decor.png")
    with open(h_dec, "w", encoding="utf-8") as f:
        f.write(build_ctkm_html(spec, logo_uri, gift_bbox, "decor"))
    l3_dec = render_html_to_rgba(h_dec, p_dec, W, H)

    # Layer 4: Crisp Typography, Logos & Vector Icons
    h_txt = os.path.join(HTML_DIR, f"{cid}_text.html")
    p_txt = os.path.join(HTML_DIR, f"{cid}_text.png")
    with open(h_txt, "w", encoding="utf-8") as f:
        f.write(build_ctkm_html(spec, logo_uri, gift_bbox, "text"))
    l4_txt = render_html_to_rgba(h_txt, p_txt, W, H)

    comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    comp.alpha_composite(l1_bg)
    comp.alpha_composite(l2_prod)
    comp.alpha_composite(l3_dec)
    comp.alpha_composite(l4_txt)

    final_rgb = ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.05)
    jpg_path = os.path.join(OUT_BANNERS, f"{spec['filename']}.jpg")
    psd_path = os.path.join(OUT_PSD, f"{spec['filename']}.psd")
    final_rgb.save(jpg_path, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES)
    save_multilayer_psd([
        ("01_San_Khau_Ngoc_Luc_Bao_3D", l1_bg),
        ("02_San_Pham_2_Tang_Cam_Thach", l2_prod),
        ("03_Khung_Bang_Gia_Va_Huy_Hieu", l3_dec),
        ("04_Logo_Chu_Gia_Va_Phap_Ly", l4_txt),
    ], psd_path, W, H)
    print(f"[DONE V2] {cid} -> {os.path.basename(jpg_path)}", flush=True)
    return {"id": cid, "jpg": jpg_path, "psd": psd_path}

# =============================================================================
# BANNER 07: LUXURY VISUAL PARTNER HANDBOOK — 3 STEPS + 6-COMBO PACKSHOT GRID
# =============================================================================
SVG_STEP1_APP = """<svg width="42" height="42" viewBox="0 0 24 24" fill="none"><rect x="6" y="2" width="12" height="20" rx="3" stroke="#FFE394" stroke-width="2"/><path d="M10 18H14" stroke="#FFE394" stroke-width="2" stroke-linecap="round"/><path d="M9.5 9.5L11.2 11.2L14.8 7.6" stroke="#FFE394" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
SVG_STEP2_GIFT = """<svg width="42" height="42" viewBox="0 0 24 24" fill="none"><rect x="3" y="10" width="18" height="11" rx="2" stroke="#FFE394" stroke-width="2"/><path d="M2 7H22V10H2V7Z" stroke="#FFE394" stroke-width="2"/><path d="M12 7V21" stroke="#FFE394" stroke-width="2"/><path d="M12 7C9.5 7 8 5.5 8 4C8 2.8 9.2 2.2 10.4 3C11.3 3.6 12 5.5 12 7ZM12 7C14.5 7 16 5.5 16 4C16 2.8 14.8 2.2 13.6 3C12.7 3.6 12 5.5 12 7Z" stroke="#FFE394" stroke-width="2"/></svg>"""
SVG_STEP3_SHIELD = """<svg width="42" height="42" viewBox="0 0 24 24" fill="none"><path d="M12 2.5L4.5 5.8V11.4C4.5 16.3 7.7 20.7 12 22C16.3 20.7 19.5 16.3 19.5 11.4V5.8L12 2.5Z" stroke="#FFE394" stroke-width="2"/><path d="M8.8 12.2L11.1 14.5L15.6 9.8" stroke="#FFE394" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
SVG_PHONE_GOLD = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M6.6 10.8C8.1 13.7 10.3 15.9 13.2 17.4L15.4 15.2C15.7 14.9 16.1 14.8 16.4 15C17.5 15.4 18.7 15.6 20 15.6C20.6 15.6 21 16 21 16.6V20C21 20.6 20.6 21 20 21C10.6 21 3 13.4 3 4C3 3.4 3.4 3 4 3H7.5C8.1 3 8.5 3.4 8.5 4C8.5 5.2 8.7 6.4 9.1 7.6C9.2 7.9 9.1 8.3 8.8 8.6L6.6 10.8Z" fill="#F5D378"/></svg>"""

def build_guide_card_html(logo_uri: str, combo_cards_data: list, pass_mode: str) -> str:
    is_decor = (pass_mode == "decor")
    decor_vis = "visible" if is_decor else "hidden"
    text_vis  = "hidden"  if is_decor else "visible"

    cards_bg_html = "".join(['<div class="mc-card-bg"></div>' for _ in combo_cards_data])
    cards_txt_html = ""
    for c in combo_cards_data:
        cards_txt_html += f"""
        <div class="mc-card-txt">
          <img class="mc-thumb" src="{c['thumb_uri']}" />
          <div class="mc-info">
            <div class="mc-name">{c['title']}</div>
            <div class="mc-price">{c['price']}</div>
            <div class="mc-gift">{c['gift']}</div>
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<style>
{font_faces_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1600px; height: 2000px; overflow: hidden;
  background: transparent; position: relative;
  font-family: 'BeVNBold', sans-serif;
  -webkit-font-smoothing: antialiased;
}}

/* ---- TOP HEADER (SITS CLEANLY ON IMPERIAL EMERALD SILK ARCH) ---- */
.hdr-overlay-bg {{
  position: absolute; top: 0; left: 0; right: 0; height: 325px;
  background: linear-gradient(180deg, rgba(3,34,22,0.72) 0%, rgba(5,48,31,0.52) 72%, rgba(5,48,31,0.0) 100%);
  visibility: {decor_vis};
}}
.hdr-wrap {{
  position: absolute; top: 24px; left: 68px; right: 68px;
  display: flex; flex-direction: column; align-items: center; gap: 18px;
  visibility: {text_vis};
}}
.hdr-top-bar {{
  width: 100%; display: flex; align-items: center; justify-content: space-between;
}}
.brand-pill {{
  background: linear-gradient(180deg, #FFFEFA, #FBF2DD);
  border: 2.5px solid #DFB153; border-radius: 999px;
  padding: 8px 26px; display: flex; align-items: center; gap: 18px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.28);
}}
.brand-pill img {{ height: 58px; width: auto; }}
.bp-sep {{ width: 2px; height: 40px; background: #D5A441; }}
.bp-drop {{ font-family: 'MontBlack', sans-serif; font-size: 44px; letter-spacing: -1.5px; color: #1046BE; line-height: 1; }}
.bp-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #F0482A; margin-left: 2px; transform: translateY(-12px); }}

.partner-tag {{
  background: linear-gradient(135deg, #B81222, #7A0813);
  border: 2.5px solid #F3CF76; border-radius: 999px;
  padding: 12px 28px; color: #FFF7D8;
  font-family: 'BeVNExtra', sans-serif; font-size: 21px; letter-spacing: 1px;
  box-shadow: 0 10px 22px rgba(90, 5, 12, 0.35);
}}
.hdr-h1 {{
  font-family: 'MontBlack', sans-serif; font-size: 58px; letter-spacing: -0.5px; line-height: 1.14;
  background: linear-gradient(180deg, #FFFCE6 0%, #F7D77E 55%, #D9A132 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.42));
  text-align: center; margin-top: 4px;
}}
.hdr-sub {{
  font-family: 'BeVNSemi', sans-serif; font-size: 26px; color: #FFFFFF;
  background: rgba(4, 42, 27, 0.78); border: 1.5px solid rgba(232, 192, 102, 0.58);
  padding: 8px 28px; border-radius: 999px;
}}

/* ---- 3 LUXURY TIMELINE STEP CARDS (Y=358..1052) ---- */
.steps-bg-col {{
  position: absolute; top: 358px; left: 68px; right: 68px;
  display: flex; flex-direction: column; gap: 22px;
  visibility: {decor_vis};
}}
.st-card-bg {{
  height: 212px; border-radius: 26px;
  background: linear-gradient(180deg, #FFFFFF 0%, #FDF9F0 100%);
  border: 2.5px solid #DEC884; border-left: 10px solid #085438;
  box-shadow: 0 14px 30px rgba(6, 48, 32, 0.10);
}}
.st-card-bg.ruby {{
  border-color: #E8B4B8; border-left: 10px solid #B51221;
  background: linear-gradient(180deg, #FFFFFF 0%, #FFF7F7 100%);
}}

.steps-txt-col {{
  position: absolute; top: 358px; left: 68px; right: 68px;
  display: flex; flex-direction: column; gap: 22px;
  visibility: {text_vis};
}}
.st-card-row {{
  height: 212px; padding: 22px 34px; display: flex; align-items: center; gap: 28px;
}}
.st-badge {{
  width: 126px; height: 146px; border-radius: 22px; flex-shrink: 0;
  background: linear-gradient(150deg, #0B5E3F 0%, #042E1E 100%);
  border: 3px solid #EAC063;
  box-shadow: 0 10px 22px rgba(4, 46, 30, 0.24);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
}}
.st-badge.ruby {{
  background: linear-gradient(150deg, #BD1424 0%, #780711 100%);
  border-color: #F6D580;
}}
.sb-step {{ font-family: 'BeVNExtra', sans-serif; font-size: 19px; color: #FCE192; letter-spacing: 1.5px; }}
.sb-num {{ font-family: 'MontBlack', sans-serif; font-size: 44px; color: #FFFFFF; line-height: 1; }}
.st-copy {{ flex: 1; }}
.st-h3 {{ font-family: 'MontBlack', sans-serif; font-size: 32px; color: #053824; margin-bottom: 8px; letter-spacing: -0.3px; }}
.st-h3.ruby {{ color: #A60E1B; }}
.st-p {{ font-family: 'BeVNSemi', sans-serif; font-size: 25.5px; color: #243830; line-height: 1.38; }}
.st-p b {{ font-family: 'BeVNExtra', sans-serif; color: #B2101E; }}
.st-p em {{ font-style: normal; font-family: 'BeVNExtra', sans-serif; color: #08583B; }}

/* ---- 6-COMBO VISUAL CATALOG GRID (2x3 WITH REAL PACKSHOT THUMBNAILS!) ---- */
.cat-hdr-bg {{
  position: absolute; top: 1068px; left: 68px; right: 68px; height: 68px;
  background: linear-gradient(90deg, #042E1E 0%, #0A563A 50%, #042E1E 100%);
  border: 2.5px solid #E5B95C; border-radius: 20px;
  box-shadow: 0 10px 24px rgba(4, 40, 26, 0.18);
  visibility: {decor_vis};
}}
.cat-hdr-txt {{
  position: absolute; top: 1068px; left: 68px; right: 68px; height: 68px;
  display: flex; align-items: center; justify-content: center; gap: 14px;
  font-family: 'MontBlack', sans-serif; font-size: 27px; color: #FFF4C6; letter-spacing: 0.6px;
  visibility: {text_vis};
}}

.mc-grid-bg {{
  position: absolute; top: 1154px; left: 68px; right: 68px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px 24px;
  visibility: {decor_vis};
}}
.mc-card-bg {{
  height: 218px; border-radius: 24px;
  background: linear-gradient(180deg, #FFFFFF 0%, #FBF6EA 100%);
  border: 2.5px solid #DFBE72;
  box-shadow: 0 10px 24px rgba(6, 48, 32, 0.10);
}}

.mc-grid-txt {{
  position: absolute; top: 1154px; left: 68px; right: 68px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px 24px;
  visibility: {text_vis};
}}
.mc-card-txt {{
  height: 218px; padding: 14px 22px 14px 14px;
  display: flex; align-items: center; gap: 16px;
}}
.mc-thumb {{ width: 215px; height: 164px; object-fit: contain; flex-shrink: 0; }}
.mc-info {{ flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 8px; }}
.mc-name {{ font-family: 'BeVNExtra', sans-serif; font-size: 23.5px; color: #053824; line-height: 1.22; }}
.mc-price {{ font-family: 'MontBlack', sans-serif; font-size: 34px; color: #0B43B8; letter-spacing: -0.8px; line-height: 1.05; }}
.mc-gift {{
  display: inline-flex; align-items: center; width: fit-content;
  background: linear-gradient(135deg, #B81222, #820914);
  color: #FFF7D8; border: 1.5px solid #F2CC72;
  font-family: 'BeVNBold', sans-serif; font-size: 19px;
  padding: 6px 14px; border-radius: 10px;
}}

/* ---- FOOTER (SITS ON BOTTOM EMERALD SILK BAND Y=1868..2000) ---- */
.ftr-bg {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 122px;
  background: linear-gradient(90deg, #032216 0%, #07422B 50%, #032216 100%);
  border-top: 3.5px solid #E5B95C;
  visibility: {decor_vis};
}}
.ftr-txt {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 122px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;
  visibility: {text_vis};
}}
.ftr-hot {{
  display: flex; align-items: center; gap: 10px;
  font-family: 'BeVNExtra', sans-serif; font-size: 26px; color: #FCE294;
}}
.ftr-leg {{ font-family: 'BeVNSemi', sans-serif; font-size: 21px; color: #EBF5EF; }}
</style>
</head>
<body>
  <div class="hdr-overlay-bg"></div>
  <div class="hdr-wrap">
    <div class="hdr-top-bar">
      <div class="brand-pill">
        <img src="{logo_uri}" />
        <div class="bp-sep"></div>
        <div class="bp-drop">droppii<span class="bp-dot"></span></div>
      </div>
      <div class="partner-tag">LƯU Ý QUAN TRỌNG CHO ĐỐI TÁC DROPPII</div>
    </div>
    <div class="hdr-h1">QUY TRÌNH 3 BƯỚC LÊN ĐƠN COMBO</div>
    <div class="hdr-sub">Chống đặt nhầm mã lẻ — Đảm bảo nhận đủ 100% quà tặng 0đ (23/11 – 30/11/2026)</div>
  </div>

  <div class="steps-bg-col">
    <div class="st-card-bg"></div>
    <div class="st-card-bg"></div>
    <div class="st-card-bg ruby"></div>
  </div>
  <div class="steps-txt-col">
    <div class="st-card-row">
      <div class="st-badge">{SVG_STEP1_APP}<span class="sb-step">BƯỚC</span><span class="sb-num">01</span></div>
      <div class="st-copy">
        <div class="st-h3">CHỌN ĐÚNG MÃ COMBO KHUYẾN MÃI TRÊN APP</div>
        <div class="st-p">Mở App Droppii → vào mục <em>Khuyến mãi / Combo An Vượng Pharma</em> chọn đúng mã Combo. <b>KHÔNG tự bấm cộng từng hộp lẻ</b> vì hệ thống sẽ không tự gắn quà!</div>
      </div>
    </div>
    <div class="st-card-row">
      <div class="st-badge">{SVG_STEP2_GIFT}<span class="sb-step">BƯỚC</span><span class="sb-num">02</span></div>
      <div class="st-copy">
        <div class="st-h3">KIỂM TRA DÒNG QUÀ TẶNG (0Đ) TRONG GIỎ HÀNG</div>
        <div class="st-p">Trước khi thanh toán, kiểm tra trong giỏ hàng phải hiện rõ <em>sản phẩm quà tặng đi kèm (giá 0đ)</em> khớp đúng 1 trong 6 gói Combo bên dưới.</div>
      </div>
    </div>
    <div class="st-card-row">
      <div class="st-badge ruby">{SVG_STEP3_SHIELD}<span class="sb-step">BƯỚC</span><span class="sb-num">03</span></div>
      <div class="st-copy">
        <div class="st-h3 ruby">RÀ SOÁT 2 GIÂY TRƯỚC KHI XÁC NHẬN ĐƠN</div>
        <div class="st-p">Đơn đã tạo trên hệ thống Droppii <b>không thể tự đổi sang mã Combo</b>. Nếu chưa thấy quà 0đ, hãy <em>nhắn ngay nhóm Hỗ trợ An Vượng Pharma</em> để được xử lý tức thì!</div>
      </div>
    </div>
  </div>

  <div class="cat-hdr-bg"></div>
  <div class="cat-hdr-txt">{SVG_SPARK}<span>TRA CỨU NHANH 6 GÓI COMBO CHÍNH HÃNG (23/11 – 30/11/2026)</span>{SVG_SPARK}</div>

  <div class="mc-grid-bg">{cards_bg_html}</div>
  <div class="mc-grid-txt">{cards_txt_html}</div>

  <div class="ftr-bg"></div>
  <div class="ftr-txt">
    <div class="ftr-hot">{SVG_PHONE_GOLD}<span>Hotline hỗ trợ Đối tác An Vượng Pharma: 0867 399 268 • Website: anvuongpharma.vn</span></div>
    <div class="ftr-leg">{LEGAL_TPBS}</div>
  </div>
</body>
</html>"""

def render_guide_card(guide_bg: Image.Image, boxes: dict, logo_uri: str) -> dict:
    W, H = 1600, 2000
    l1_bg = guide_bg.resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")

    combo_cards_data = [
        {"title": "Combo Đủ 4 Sản Phẩm Chủ Lực", "price": "2.440.000đ", "gift": "Tặng 01 Collamela 20 gói (920K)", "thumb_uri": build_mini_combo_thumb_uri(boxes, ["protein_fr", "bojomi", "curcumilk"], "collamela")},
        {"title": "Mua 05 Hộp Đạm AV Protein", "price": "1.750.000đ", "gift": "Tặng 01 Hộp Bojomi (520K)", "thumb_uri": build_mini_combo_thumb_uri(boxes, ["protein_fr", "protein"], "bojomi")},
        {"title": "Mua 03 Hộp Xương Khớp Bojomi", "price": "1.560.000đ", "gift": "Tặng 01 Hộp Bojomi (520K)", "thumb_uri": build_mini_combo_thumb_uri(boxes, ["bojomi_hero", "bojomi"], "bojomi")},
        {"title": "Mua 04 Hộp Curcumilk Phyto", "price": "2.600.000đ", "gift": "Tặng 01 Curcumilk (650K)", "thumb_uri": build_mini_combo_thumb_uri(boxes, ["curcumilk_hero", "curcumilk"], "curcumilk")},
        {"title": "Mua 02 Hộp Collamela (20 gói)", "price": "1.840.000đ", "gift": "Tặng 01 Collamela 10 gói (480K)", "thumb_uri": build_mini_combo_thumb_uri(boxes, ["collamela_hero", "collamela"], "colla10")},
        {"title": "Combo 02 Bojomi + 02 Curcumilk", "price": "2.340.000đ", "gift": "Tặng 01 Hộp Bojomi (520K)", "thumb_uri": build_mini_combo_thumb_uri(boxes, ["bojomi", "curcumilk"], "bojomi")},
    ]

    h_dec = os.path.join(HTML_DIR, "GUIDE_07_decor.html")
    p_dec = os.path.join(HTML_DIR, "GUIDE_07_decor.png")
    with open(h_dec, "w", encoding="utf-8") as f:
        f.write(build_guide_card_html(logo_uri, combo_cards_data, "decor"))
    l2_dec = render_html_to_rgba(h_dec, p_dec, W, H)

    h_txt = os.path.join(HTML_DIR, "GUIDE_07_text.html")
    p_txt = os.path.join(HTML_DIR, "GUIDE_07_text.png")
    with open(h_txt, "w", encoding="utf-8") as f:
        f.write(build_guide_card_html(logo_uri, combo_cards_data, "text"))
    l3_txt = render_html_to_rgba(h_txt, p_txt, W, H)

    comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    comp.alpha_composite(l1_bg)
    comp.alpha_composite(l2_dec)
    comp.alpha_composite(l3_txt)

    fname = "261123 AVPM 07 - The Huong Dan 3 Buoc Len Don Combo Droppii"
    jpg_path = os.path.join(OUT_BANNERS, f"{fname}.jpg")
    psd_path = os.path.join(OUT_PSD, f"{fname}.psd")
    ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.04).save(jpg_path, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES)
    save_multilayer_psd([
        ("01_Nen_Lua_Ngoc_Luc_Bao_3D", l1_bg),
        ("02_Khung_The_3_Buoc_Va_6_O", l2_dec),
        ("03_Logo_Hinh_Combo_Va_Chu", l3_txt),
    ], psd_path, W, H)
    print(f"[DONE V2] GUIDE_07 -> {os.path.basename(jpg_path)}", flush=True)
    return {"id": "GUIDE_07", "jpg": jpg_path, "psd": psd_path}

def build_qc_sheet(results: list) -> str:
    cols, rows = 4, 2
    cw, ch = 600, 680
    sheet = Image.new("RGB", (cols * cw, rows * ch), (12, 26, 20))
    draw = ImageDraw.Draw(sheet)
    f_lbl = ImageFont.truetype(os.path.join(FONTS_DIR.replace("/", os.sep), "BeVietnamPro-Bold.ttf"), 20)
    for i, r in enumerate(results):
        im = Image.open(r["jpg"]).convert("RGB")
        im.thumbnail((cw - 28, ch - 64), Image.Resampling.LANCZOS)
        x = (i % cols) * cw + (cw - im.width) // 2
        y = (i // cols) * ch + 14
        sheet.paste(im, (x, y))
        draw.text(((i % cols) * cw + 18, (i // cols) * ch + ch - 40), f"{r['id']} • {os.path.basename(r['jpg'])[:44]}", fill=(246, 214, 122), font=f_lbl)
    qc_path = os.path.join(AUDIT_DIR, "QC_7_Banners_CTKM_Va_Huong_Dan.jpg")
    sheet.save(qc_path, "JPEG", quality=95, subsampling=0, icc_profile=SRGB_BYTES)
    print(f"[QC SHEET V2] Saved -> {qc_path}")
    return qc_path

def sync_all_destinations(qc_path: str):
    sync_targets = [
        # 1. Master Cloud Project Folder
        (OUT_BANNERS, r"G:\My Drive\AI_Full_Studio\03_Du_An\261123-av-plan-phat-trien-brand\01_Bo_6_Banner_CTKM_23_30_11_Va_The_Len_Don"),
        # 2. Brand Deliverable Folder on Company Sync
        (OUT_BANNERS, r"G:\Other computers\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261123 - Bộ Banner CTKM 23-30.11 & Content 30 Ngày An Vượng Pharma\01_Bo_6_Banner_CTKM_23_30_11_Va_The_Len_Don"),
    ]
    for src, dst in sync_targets:
        parent = os.path.dirname(dst)
        if os.path.exists(parent):
            os.makedirs(dst, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print("Synced folder ->", dst)

    # Also update QC_7_Banners_CTKM_Va_Huong_Dan.jpg wherever it exists
    qc_targets = [
        r"G:\My Drive\AI_Full_Studio\03_Du_An\261123-av-plan-phat-trien-brand\audit\QC_7_Banners_CTKM_Va_Huong_Dan.jpg",
        r"G:\Other computers\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261123 - Bộ Banner CTKM 23-30.11 & Content 30 Ngày An Vượng Pharma\QC_7_Banners_CTKM_Va_Huong_Dan.jpg",
    ]
    # Check if there is any folder in G:\My Drive\dự án ngoài\An Vượng containing 261123 AVPM
    av_ext = r"G:\My Drive\dự án ngoài\An Vượng"
    if os.path.exists(av_ext):
        for dp, dn, fn in os.walk(av_ext):
            if any("261123 AVPM" in f for f in fn):
                for f in os.listdir(OUT_BANNERS):
                    sf = os.path.join(OUT_BANNERS, f)
                    df = os.path.join(dp, f)
                    if os.path.isfile(sf):
                        shutil.copy2(sf, df)
                if os.path.exists(os.path.join(dp, "File_PSD_Chinh_Sua_Da_Layer")):
                    shutil.copytree(OUT_PSD, os.path.join(dp, "File_PSD_Chinh_Sua_Da_Layer"), dirs_exist_ok=True)
                if any("QC_7_Banners" in f for f in fn):
                    shutil.copy2(qc_path, os.path.join(dp, "QC_7_Banners_CTKM_Va_Huong_Dan.jpg"))
                print("Synced external An Vượng folder ->", dp)

    for qt in qc_targets:
        if os.path.exists(os.path.dirname(qt)):
            shutil.copy2(qc_path, qt)
            print("Synced QC ->", qt)

if __name__ == "__main__":
    stage_p = os.path.join(STAGE_DIR, "bg_stage_emerald_champagne_v2.png")
    guide_p = os.path.join(STAGE_DIR, "bg_guide_royal_emerald_v2.png")
    stage_bg = Image.open(stage_p)
    guide_bg = Image.open(guide_p)

    clean_logo = prepare_clean_logo(LOGO_ORIG)
    logo_uri = image_to_data_uri(clean_logo, "PNG")
    boxes = load_all_boxes()

    results = []
    for sp in CTKM_BANNERS:
        results.append(render_ctkm_banner(sp, stage_bg, boxes, logo_uri))
    results.append(render_guide_card(guide_bg, boxes, logo_uri))
    qc_p = build_qc_sheet(results)
    sync_all_destinations(qc_p)
    # Also copy script backup
    shutil.copy2(__file__, os.path.join(PROJ_DIR, "build_7_av_ctkm_banners.py"))
    print("=== ALL 7 LUXURY V2 BANNERS + 7 PSDs + SYNC COMPLETE ===")
