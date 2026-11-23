# -*- coding: utf-8 -*-
"""
Step 4 (V2 — SUPER-SIZED HERO PRODUCT & HIGH-IMPACT LARGE TYPOGRAPHY):
Flagship Retina (3200x4000 -> 1600x2000) Commercial Infographic Renderer
+ 4-Layer Editable Adobe Photoshop .PSD Exporter for ALL 26 Designs (An Vượng Pharma & Hằng Thu Pharma).
"""
import base64, io, json, math, os, shutil, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import packbits
import pytoshop
import pytoshop.codecs
pytoshop.codecs.packbits = packbits
from pytoshop.user import nested_layers
from pytoshop import enums

sys.path.insert(0, r"d:\AI\full studio\projects\av_htpm_26_posters_2211")
from step3_product_catalog_26_designs import POSTERS_26, THEMES

PROJ = r"d:\AI\full studio\projects\av_htpm_26_posters_2211"
CUT_DIR = os.path.join(PROJ, "assets", "cutouts")
ART_DIR = os.path.join(PROJ, "assets", "ai_art")
QUAD_CACHE = os.path.join(PROJ, "assets", "quad_crops")
HTML_DIR = os.path.join(PROJ, "html_passes")
OUT_ROOT = os.path.join(PROJ, "Final_Deliverables")
AUDIT_DIR = os.path.join(PROJ, "audit")

for d in (QUAD_CACHE, HTML_DIR, OUT_ROOT, AUDIT_DIR):
    os.makedirs(d, exist_ok=True)

FONTS_DIR = r"d:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi"
W, H = 1600, 2000

SRGB_PROFILE = ImageCms.createProfile("sRGB")
SRGB_BYTES = ImageCms.ImageCmsProfile(SRGB_PROFILE).tobytes()

def find_browser_exe() -> str:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("No Chromium browser found for Retina rendering!")

BROWSER_EXE = find_browser_exe()

def file_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")

def tight_crop_rgba(im: Image.Image, alpha_thresh: int = 38, pad: int = 4) -> Image.Image:
    """Tightly trims faint shadow fringes so 100% of bounding box goes to solid hero packaging."""
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > alpha_thresh)
    if len(xs) == 0:
        return im
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(im.width, int(xs.max()) + 1 + pad)
    y1 = min(im.height, int(ys.max()) + 1 + pad)
    return im.crop((x0, y0, x1, y1))

def extract_4_quadrants_uris(quad_filename: str) -> list:
    src_path = os.path.join(ART_DIR, quad_filename)
    im = Image.open(src_path).convert("RGB")
    qw, qh = im.width // 2, im.height // 2
    boxes = [
        (0, 0, qw, qh),
        (qw, 0, im.width, qh),
        (0, qh, qw, im.height),
        (qw, qh, im.width, im.height),
    ]
    uris = []
    base = os.path.splitext(quad_filename)[0]
    for idx, (x0, y0, x1, y1) in enumerate(boxes):
        cache_p = os.path.join(QUAD_CACHE, f"{base}_q{idx+1}.png")
        if os.path.exists(cache_p):
            uris.append(file_to_data_uri(cache_p))
            continue
        sub = im.crop((x0, y0, x1, y1))
        sw, sh = sub.size
        mx, my = int(sw * 0.03), int(sh * 0.03)
        sub = sub.crop((mx, my, sw - mx, sh - my))
        arr = np.array(sub, dtype=np.float32)

        corners = np.concatenate([
            arr[:12, :12].reshape(-1, 3),
            arr[:12, -12:].reshape(-1, 3),
            arr[-12:, :12].reshape(-1, 3),
            arr[-12:, -12:].reshape(-1, 3),
        ], axis=0)
        bg_col = np.median(corners, axis=0)
        dist = np.linalg.norm(arr - bg_col[None, None, :], axis=2)

        ys, xs = np.where(dist > 18.0)
        if len(xs) > 100:
            pad = int(max(sub.size) * 0.04)
            bx0 = max(0, int(xs.min()) - pad)
            by0 = max(0, int(ys.min()) - pad)
            bx1 = min(sub.width, int(xs.max()) + 1 + pad)
            by1 = min(sub.height, int(ys.max()) + 1 + pad)
            sub = sub.crop((bx0, by0, bx1, by1))
            arr = np.array(sub, dtype=np.float32)
            dist = np.linalg.norm(arr - bg_col[None, None, :], axis=2)

        alpha = np.clip((dist - 7.5) / 18.0, 0.0, 1.0)
        mask_u8 = (alpha > 0.32).astype(np.uint8) * 255
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        closed = cv2.morphologyEx(mask_u8, cv2.MORPH_CLOSE, k)
        eroded = cv2.erode(closed, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
        alpha = np.maximum(alpha, (eroded / 255.0) * 0.98)
        alpha = cv2.GaussianBlur(alpha.astype(np.float32), (5, 5), 0.85)

        qh_cur, qw_cur = alpha.shape
        yy_q, xx_q = np.mgrid[0:qh_cur, 0:qw_cur].astype(np.float32)
        dx_edge = np.minimum(xx_q, qw_cur - 1 - xx_q) / max(1.0, qw_cur * 0.09)
        dy_edge = np.minimum(yy_q, qh_cur - 1 - yy_q) / max(1.0, qh_cur * 0.09)
        border_fade = np.clip(np.minimum(dx_edge, dy_edge), 0.0, 1.0)
        alpha = alpha * border_fade

        pil_rgb = ImageEnhance.Contrast(ImageEnhance.Color(ImageEnhance.Sharpness(sub).enhance(1.22)).enhance(1.08)).enhance(1.04)
        rgba = np.dstack([np.array(pil_rgb), np.clip(alpha * 255.0, 0, 255).astype(np.uint8)])
        out_q = Image.fromarray(rgba, "RGBA")
        out_q.save(cache_p)
        uris.append(file_to_data_uri(cache_p))
    return uris

def resolve_4_card_uris(spec: dict) -> list:
    if spec.get("quad_picks"):
        out = []
        cache_by_sheet = {}
        for sheet_name, q_idx in spec["quad_picks"]:
            if sheet_name not in cache_by_sheet:
                cache_by_sheet[sheet_name] = extract_4_quadrants_uris(sheet_name)
            out.append(cache_by_sheet[sheet_name][q_idx])
        return out
    return extract_4_quadrants_uris(spec["quad_art"])

def build_layer1_backdrop(spec: dict, theme: dict) -> Image.Image:
    bg_path = os.path.join(ART_DIR, spec["bg_art"])
    im = Image.open(bg_path).convert("RGB")
    if spec.get("mirror_bg"):
        im = ImageOps.mirror(im)
    scale = max(W / im.width, H / im.height)
    nw, nh = int(round(im.width * scale)), int(round(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = (nw - W) // 2
    oy = int((nh - H) * (0.82 if spec["layout"] == "A" else 0.35))
    im = im.crop((ox, oy, ox + W, oy + H))

    arr = np.array(im, dtype=np.float32)
    hex_top = theme["bg_top"].lstrip("#")
    tint = np.array([int(hex_top[0:2], 16), int(hex_top[2:4], 16), int(hex_top[4:6], 16)], dtype=np.float32)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ny, nx = yy / H, xx / W

    if spec["layout"] == "A":
        podium_glow = np.exp(-(((nx - 0.22) / 0.24) ** 2 + ((ny - 0.39) / 0.22) ** 2))
        veil = np.clip(0.46 - 0.36 * podium_glow + 0.22 * (ny > 0.56) * ((ny - 0.56) / 0.44), 0.08, 0.70)
        header_mask = np.clip((0.22 - ny) / 0.22, 0.0, 1.0) * np.clip((nx - 0.24) / 0.25, 0.0, 1.0) * 0.36
        veil = np.clip(veil + header_mask, 0.08, 0.75)
        spot = np.exp(-(((nx - 0.22) / 0.21) ** 2 + ((ny - 0.38) / 0.18) ** 2))
    else:
        podium_glow = np.exp(-(((nx - 0.78) / 0.23) ** 2 + ((ny - 0.23) / 0.21) ** 2))
        veil = np.clip(0.50 - 0.38 * podium_glow + 0.20 * np.clip((ny - 0.39) / 0.61, 0.0, 1.0), 0.10, 0.73)
        spot = np.exp(-(((nx - 0.79) / 0.21) ** 2 + ((ny - 0.23) / 0.18) ** 2))

    blended = arr * (1.0 - veil[:, :, None]) + tint[None, None, :] * veil[:, :, None]
    gold_rgb = np.array([255.0, 220.0, 132.0], dtype=np.float32)
    blended = np.clip(blended + spot[:, :, None] * gold_rgb[None, None, :] * 0.18, 0, 255).astype(np.uint8)
    return Image.fromarray(blended, "RGB").convert("RGBA")

def build_layer3_product(spec: dict) -> Image.Image:
    """Layer 3 (1600x2000 RGBA): COMMANDING HERO-SCALE Real Studio Product Cutout (+35% to +48% larger!)."""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cut = tight_crop_rgba(Image.open(os.path.join(CUT_DIR, spec["cutout"])).convert("RGBA"))

    if spec.get("extra_stick"):
        stick = tight_crop_rgba(Image.open(os.path.join(CUT_DIR, spec["extra_stick"])).convert("RGBA"))
        bh = cut.height
        sh = int(bh * 0.80)
        sw = int(round(stick.width * (sh / stick.height)))
        stick_r = stick.resize((sw, sh), Image.Resampling.LANCZOS)
        combo_w = cut.width + int(sw * 0.58)
        combo = Image.new("RGBA", (combo_w, bh + 14), (0, 0, 0, 0))
        combo.alpha_composite(cut, dest=(0, 0))
        st_alpha = stick_r.split()[3]
        st_sh = Image.new("RGBA", stick_r.size, (0, 0, 0, 0))
        st_sh.putalpha(st_alpha.point(lambda p: int(p * 0.48)))
        st_sh = st_sh.filter(ImageFilter.GaussianBlur(14))
        combo.alpha_composite(st_sh, dest=(cut.width - int(sw * 0.44), bh - sh + 12))
        combo.alpha_composite(stick_r, dest=(cut.width - int(sw * 0.40), bh - sh + 8))
        cut = tight_crop_rgba(combo)

    aspect = cut.width / max(1.0, float(cut.height))
    if spec["layout"] == "A":
        # Left Hero Stage: x=14..686 (up to 668px wide x 835px tall!)
        # For wide horizontal combos (aspect > 1.15), allow slight 3D overlap to x=695 so boxes stay HUGE!
        max_w = 676 if aspect > 1.05 else 652
        max_h = 835
        cx = 350 if aspect > 1.05 else 346
        bottom_y = 1098
    else:
        # Top-Right Hero Stage: x=900..1586 (up to 678px wide x 740px tall!)
        max_w = 678 if aspect > 1.05 else 648
        max_h = 742
        cx = 1244
        bottom_y = 758

    scale = min(max_w / cut.width, max_h / cut.height)
    nw, nh = int(round(cut.width * scale)), int(round(cut.height * scale))
    prod = cut.resize((nw, nh), Image.Resampling.LANCZOS)

    r, g, b, a = prod.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Brightness(rgb).enhance(1.09)
    rgb = ImageEnhance.Contrast(ImageEnhance.Sharpness(rgb).enhance(1.26)).enhance(1.05)
    prod = Image.merge("RGBA", (*rgb.split(), a))

    px = max(8, min(W - nw - 8, cx - nw // 2))
    py = max(14, bottom_y - nh)
    eff_bottom = py + nh

    # Multi-pass Realistic Studio Contact Shadow & Floor Grounding
    floor_sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(floor_sh).ellipse([px - int(nw * 0.12), eff_bottom - 28, px + int(nw * 1.12), eff_bottom + 36], fill=(8, 12, 8, 145))
    floor_sh = floor_sh.filter(ImageFilter.GaussianBlur(26))
    canvas.alpha_composite(floor_sh)

    ao_wide = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ao_wide).ellipse([px + int(nw * 0.04), eff_bottom - 18, px + int(nw * 0.96), eff_bottom + 16], fill=(12, 8, 4, 190))
    ao_wide = ao_wide.filter(ImageFilter.GaussianBlur(13))
    canvas.alpha_composite(ao_wide)

    ao_tight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ao_tight).ellipse([px + int(nw * 0.10), eff_bottom - 9, px + int(nw * 0.90), eff_bottom + 6], fill=(6, 4, 2, 235))
    ao_tight = ao_tight.filter(ImageFilter.GaussianBlur(4))
    canvas.alpha_composite(ao_tight)

    # Warm golden rim-glow behind hero product silhouette
    glow = Image.new("RGBA", (nw + 64, nh + 64), (0, 0, 0, 0))
    glow_mask = Image.new("L", (nw + 64, nh + 64), 0)
    glow_mask.paste(a, (32, 32))
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(20))
    glow_gold = Image.new("RGBA", (nw + 64, nh + 64), (255, 228, 145, 0))
    glow_gold.putalpha(glow_mask.point(lambda v: int(v * 0.38)))
    canvas.alpha_composite(glow_gold, dest=(max(0, px - 32), max(0, py - 32)))

    canvas.alpha_composite(prod, dest=(px, py))
    return canvas

def compute_title_svg_attrs(title: str, layout: str):
    """Computes massive, non-clipping headline font-size & optional textLength auto-fit."""
    box_w = 1106 if layout == "A" else 862
    n = len(title)
    if layout == "A":
        fs = 116 if n <= 9 else (106 if n <= 12 else (92 if n <= 15 else 82))
    else:
        fs = 106 if n <= 9 else (94 if n <= 12 else (80 if n <= 15 else 70))
    # Estimate rendered pixel width (~0.66 * fs per uppercase glyph in Montserrat-Black)
    est_w = n * fs * 0.67
    extra_attr = f' textLength="{int(box_w * 0.96)}" lengthAdjust="spacingAndGlyphs"' if est_w > box_w * 0.96 else ""
    return box_w, fs, extra_attr

def build_html_for_pass(spec: dict, theme: dict, quad_uris: list, logo_uri: str, pass_mode: str) -> str:
    show_cards = (pass_mode == "cards")
    show_text = (pass_mode == "text")

    g0, g1, g2, g3, g4 = theme["gold_grad"]
    svg_w, title_fs, title_fit_attr = compute_title_svg_attrs(spec["title"], spec["layout"])

    if spec["brand_group"] == "AN_VUONG":
        brand_html = f'''
        <div class="brand-av">
            <img src="{logo_uri}" class="av-logo-img only-text" />
        </div>'''
    else:
        brand_html = f'''
        <div class="brand-ht">
            <img src="{logo_uri}" class="ht-logo-img" />
            <div class="ht-brand-txt">
                <div class="ht-brand-name">HẰNG THU PHARMA</div>
                <div class="ht-brand-sub">Tinh Hoa Thảo Dược Việt • Chính Hãng</div>
            </div>
        </div>'''

    cards_html_A = ""
    for i, (num, c_title, c_metric, c_desc) in enumerate(spec["cards"]):
        q_uri = quad_uris[i]
        cards_html_A += f'''
        <div class="bento-card card-{i+1}">
            <div class="num-pill"><span class="only-text">{num}</span></div>
            <div class="card-inner">
                <div class="card-head only-text">{c_title}</div>
                <div class="card-illust-wrap only-cards">
                    <img src="{q_uri}" class="card-illust" />
                </div>
                <div class="card-copy only-text">
                    <div class="card-metric">{c_metric}</div>
                    <div class="card-desc">{c_desc}</div>
                </div>
            </div>
        </div>'''

    cards_html_B = ""
    for i, (num, c_title, c_metric, c_desc) in enumerate(spec["cards"]):
        q_uri = quad_uris[i]
        cards_html_B += f'''
        <div class="bento-card card-{i+1}">
            <div class="num-pill"><span class="only-text">{num}</span></div>
            <div class="card-inner">
                <div class="card-illust-wrap only-cards">
                    <img src="{q_uri}" class="card-illust" />
                </div>
                <div class="card-copy only-text">
                    <div class="card-head-inline">{c_title}</div>
                    <div class="card-metric">{c_metric}</div>
                    <div class="card-desc">{c_desc}</div>
                </div>
            </div>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<style>
@font-face {{ font-family: 'TitleHeavy'; src: url('file:///{FONTS_DIR}/Montserrat-Black.ttf'); font-weight: 900; }}
@font-face {{ font-family: 'VNExtra'; src: url('file:///{FONTS_DIR}/BeVietnamPro-ExtraBold.ttf'); font-weight: 800; }}
@font-face {{ font-family: 'VNBold'; src: url('file:///{FONTS_DIR}/BeVietnamPro-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: 'VNSemi'; src: url('file:///{FONTS_DIR}/BeVietnamPro-SemiBold.ttf'); font-weight: 600; }}
@font-face {{ font-family: 'VNMed'; src: url('file:///{FONTS_DIR}/BeVietnamPro-Medium.ttf'); font-weight: 500; }}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
    width: {W}px; height: {H}px; overflow: hidden;
    background: transparent !important;
    font-family: 'VNSemi', 'VNMed', sans-serif;
    -webkit-font-smoothing: antialiased;
}}

.only-cards {{ visibility: {'visible' if show_cards else 'hidden'}; }}
.only-text  {{ visibility: {'visible' if show_text else 'hidden'}; }}

.canvas {{ position: relative; width: {W}px; height: {H}px; }}

/* BRAND LOGO BLOCK — LARGER & CRISPER */
.brand-av {{
    position: absolute; left: 34px; top: 24px; width: 410px; height: 226px;
    display: flex; align-items: center; justify-content: flex-start;
}}
.layout-B .brand-av {{
    top: 22px; height: 158px;
}}
.av-logo-img {{
    max-width: 395px; max-height: 215px; object-fit: contain;
    filter: drop-shadow(0 6px 18px rgba(0,0,0,0.58));
}}
.layout-B .av-logo-img {{
    max-width: 330px; max-height: 152px;
}}
.brand-ht {{
    position: absolute; left: 36px; top: 34px;
    display: flex; align-items: center; gap: 18px;
    padding: 12px 28px 12px 14px;
    border-radius: 68px;
    background: {'rgba(255,253,246,0.14)' if show_cards else 'transparent'};
    border: {'2px solid rgba(248,214,130,0.58)' if show_cards else '2px solid transparent'};
}}
.ht-logo-img {{
    width: 88px; height: 88px; object-fit: contain;
    visibility: {'visible' if show_text else 'hidden'};
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.48));
}}
.ht-brand-txt {{ visibility: {'visible' if show_text else 'hidden'}; }}
.ht-brand-name {{
    font-family: 'VNExtra'; font-size: 29px; letter-spacing: 0.8px;
    color: #FFF7D6; text-shadow: 0 2px 8px rgba(0,0,0,0.58);
}}
.ht-brand-sub {{
    font-family: 'VNBold'; font-size: 18.5px; color: #F9E2A2; margin-top: 2px;
}}

/* HERO HEADLINE & SUBTITLE — SUPER-SIZED */
.hero-header-A {{
    position: absolute; left: 460px; right: 34px; top: 26px;
    text-align: center;
}}
.hero-header-B {{
    position: absolute; left: 38px; width: 862px; top: 188px;
    text-align: left;
}}
.kicker-pill {{
    display: inline-block;
    padding: 8px 24px; border-radius: 42px;
    background: {'rgba(255, 244, 198, 0.16)' if show_cards else 'transparent'};
    border: {'1.8px solid rgba(246, 208, 118, 0.68)' if show_cards else '1.8px solid transparent'};
    margin-bottom: 6px;
}}
.kicker-txt {{
    font-family: 'VNExtra'; font-size: 20.5px; letter-spacing: 0.9px;
    color: #FFEAAC; text-transform: uppercase;
}}
.title-svg {{
    width: 100%; height: 126px; overflow: visible; display: block;
}}
.layout-B .title-svg {{
    height: 118px;
}}
.sub-1 {{
    font-family: 'VNExtra'; font-size: 33px; line-height: 1.24;
    color: #FFFFFF; text-shadow: 0 3px 14px rgba(0,0,0,0.72);
    margin-top: 2px; text-wrap: balance;
}}
.sub-2 {{
    font-family: 'VNBold'; font-size: 27px; line-height: 1.28;
    color: #FDEBB8; text-shadow: 0 2px 12px rgba(0,0,0,0.68);
    margin-top: 4px; text-wrap: balance;
}}
.layout-B .sub-1 {{ font-size: 31.5px; }}
.layout-B .sub-2 {{ font-size: 25.5px; }}

/* SECTION HIGHLIGHT BANNER — BIGGER & BOLDER */
.sec-banner-A {{
    position: absolute; left: 692px; right: 34px; top: 318px; height: 130px;
    border-radius: 26px;
    background: {theme['pill_bg'] if show_cards else 'transparent'};
    border: {'3px solid ' + theme['card_border'] if show_cards else '3px solid transparent'};
    box-shadow: {'0 14px 30px rgba(0,0,0,0.42), inset 0 1.5px 0 rgba(255,255,255,0.28)' if show_cards else 'none'};
    display: flex; align-items: center; justify-content: center; gap: 22px; padding: 0 24px;
}}
.sec-banner-B {{
    position: absolute; left: 36px; width: 862px; top: 594px; height: 132px;
    border-radius: 26px;
    background: {theme['pill_bg'] if show_cards else 'transparent'};
    border: {'3px solid ' + theme['card_border'] if show_cards else '3px solid transparent'};
    box-shadow: {'0 14px 30px rgba(0,0,0,0.42), inset 0 1.5px 0 rgba(255,255,255,0.28)' if show_cards else 'none'};
    display: flex; align-items: center; justify-content: flex-start; gap: 24px; padding: 0 30px;
}}
.sec-big-num {{
    font-family: 'TitleHeavy'; font-size: 104px; line-height: 0.95;
    background: linear-gradient(180deg, {g0} 0%, {g1} 35%, {g2} 72%, {g4} 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.50));
}}
.sec-l1 {{
    font-family: 'VNExtra'; font-size: 38px; letter-spacing: 0.6px;
    color: #FFE9A4; line-height: 1.12; text-transform: uppercase;
    text-shadow: 0 2px 8px rgba(0,0,0,0.50);
}}
.sec-l2 {{
    font-family: 'VNBold'; font-size: 22.5px; letter-spacing: 0.4px;
    color: #FFFFFF; margin-top: 5px; text-transform: uppercase;
}}

/* BENTO CARDS COMMON */
.bento-card {{
    position: absolute;
    border-radius: 28px;
    background: {'linear-gradient(180deg, #FFFDF9 0%, #FBF2DF 100%)' if show_cards else 'transparent'};
    border: {'3px solid ' + theme['card_border'] if show_cards else '3px solid transparent'};
    box-shadow: {'0 18px 38px rgba(0,0,0,0.38), inset 0 2px 0 #FFFFFF' if show_cards else 'none'};
}}
.num-pill {{
    position: absolute; top: -26px; left: 50%; transform: translateX(-50%);
    min-width: 90px; height: 50px; padding: 0 24px;
    border-radius: 26px;
    background: {theme['num_bg'] if show_cards else 'transparent'};
    border: {'2.5px solid #F7D882' if show_cards else '2.5px solid transparent'};
    box-shadow: {'0 6px 14px rgba(0,0,0,0.32)' if show_cards else 'none'};
    display: flex; align-items: center; justify-content: center;
    font-family: 'VNExtra'; font-size: 28px; color: #FFF8DC; letter-spacing: 1px;
    z-index: 5;
}}

/* LAYOUT A: ASYMMETRIC 4-CARD BENTO — PACKED WITH BIG BOLD TEXT */
.layout-A .card-1 {{ left: 692px; width: 426px; top: 482px; height: 638px; }}
.layout-A .card-2 {{ left: 1140px; width: 426px; top: 482px; height: 638px; }}
.layout-A .card-3 {{ left: 34px;  width: 752px; top: 1158px; height: 646px; }}
.layout-A .card-4 {{ left: 814px; width: 752px; top: 1158px; height: 646px; }}

.layout-A .card-inner {{
    width: 100%; height: 100%; padding: 32px 16px 18px 16px;
    display: flex; flex-direction: column; align-items: center; justify-content: space-between;
    text-align: center;
}}
.layout-A .card-3 .card-inner, .layout-A .card-4 .card-inner {{
    padding: 32px 26px 20px 26px;
}}
.layout-A .card-head {{
    font-family: 'VNExtra'; font-size: 30.5px; line-height: 1.16;
    color: {theme['title_ink']}; text-transform: uppercase;
    min-height: 70px; display: flex; align-items: center; justify-content: center;
    text-wrap: balance;
}}
.layout-A .card-3 .card-head, .layout-A .card-4 .card-head {{
    font-size: 35px; min-height: 54px;
}}
.layout-A .card-1 .card-illust-wrap, .layout-A .card-2 .card-illust-wrap {{
    width: 355px; height: 285px; display: flex; align-items: center; justify-content: center;
}}
.layout-A .card-3 .card-illust-wrap, .layout-A .card-4 .card-illust-wrap {{
    width: 475px; height: 305px; display: flex; align-items: center; justify-content: center;
}}
.card-illust {{
    max-width: 100%; max-height: 100%; object-fit: contain;
    filter: drop-shadow(0 10px 16px rgba(60, 38, 10, 0.18));
}}
.layout-A .card-metric {{
    font-family: 'VNExtra'; font-size: 42px; line-height: 1.12;
    color: {theme['metric_ink']}; margin-bottom: 6px;
}}
.layout-A .card-3 .card-metric, .layout-A .card-4 .card-metric {{
    font-size: 44px;
}}
.layout-A .card-desc {{
    font-family: 'VNBold'; font-size: 24px; line-height: 1.28;
    color: #1F1D1A; max-width: 398px; text-wrap: balance;
}}
.layout-A .card-3 .card-desc, .layout-A .card-4 .card-desc {{
    font-size: 26.5px; line-height: 1.30; max-width: 695px;
}}

/* LAYOUT B: ROYAL SPLIT SHOWCASE + 2x2 HORIZONTAL BENTO CARDS — BIGGER TEXT */
.layout-B .card-1 {{ left: 34px;  width: 752px; top: 778px;  height: 492px; }}
.layout-B .card-2 {{ left: 814px; width: 752px; top: 778px;  height: 492px; }}
.layout-B .card-3 {{ left: 34px;  width: 752px; top: 1312px; height: 492px; }}
.layout-B .card-4 {{ left: 814px; width: 752px; top: 1312px; height: 492px; }}
.layout-B .num-pill {{ left: 64px; transform: none; }}

.layout-B .card-inner {{
    width: 100%; height: 100%; padding: 28px 24px 22px 18px;
    display: grid; grid-template-columns: 280px 1fr; gap: 18px; align-items: center;
}}
.layout-B .card-illust-wrap {{
    grid-column: 1; grid-row: 1 / span 2;
    width: 276px; height: 412px;
    border-radius: 22px;
    background: {'radial-gradient(circle, rgba(248,225,162,0.36) 0%, rgba(255,253,248,0) 72%)' if show_cards else 'transparent'};
    display: flex; align-items: center; justify-content: center;
}}
.layout-B .card-copy {{
    grid-column: 2; grid-row: 1 / span 2;
    text-align: left; display: flex; flex-direction: column; justify-content: center;
}}
.layout-B .card-head-inline {{
    font-family: 'VNExtra'; font-size: 33.5px; line-height: 1.16;
    color: {theme['title_ink']}; text-transform: uppercase; margin-bottom: 10px;
    text-wrap: balance;
}}
.layout-B .card-metric {{
    display: inline-block; align-self: flex-start;
    padding: 7px 20px; border-radius: 32px;
    background: {'rgba(235, 193, 96, 0.30)' if show_text else 'transparent'};
    font-family: 'VNExtra'; font-size: 29.5px; color: {theme['metric_ink']};
    margin-bottom: 12px;
}}
.layout-B .card-desc {{
    font-family: 'VNBold'; font-size: 25.5px; line-height: 1.32; color: #1F1D1A; text-wrap: balance;
}}

/* FOOTER BAR — LARGER READABLE TYPE */
.footer-bar {{
    position: absolute; left: 34px; right: 34px; bottom: 26px; height: 138px;
    border-radius: 26px;
    background: {'linear-gradient(180deg, #FFFDF9 0%, #F9EFE0 100%)' if show_cards else 'transparent'};
    border: {'2.5px solid ' + theme['card_border'] if show_cards else '2.5px solid transparent'};
    box-shadow: {'0 12px 26px rgba(0,0,0,0.34)' if show_cards else 'none'};
    display: grid; grid-template-columns: 1.2fr 172px 1.05fr; align-items: center;
    padding: 0 24px; gap: 16px;
}}
.ft-left {{ display: flex; align-items: center; gap: 16px; }}
.ft-badge-icon {{
    width: 68px; height: 68px; border-radius: 50%; flex-shrink: 0;
    background: {theme['num_bg'] if show_cards else 'transparent'};
    display: flex; align-items: center; justify-content: center;
}}
.ft-usage {{
    font-family: 'VNExtra'; font-size: 22.5px; line-height: 1.28; color: #181C19;
}}
.ft-mid {{
    display: flex; align-items: center; justify-content: center; gap: 8px;
    border-left: {'2px solid rgba(140,120,80,0.30)' if show_cards else 'none'};
    border-right: {'2px solid rgba(140,120,80,0.30)' if show_cards else 'none'};
    height: 84px;
}}
.ft-legal {{
    font-family: 'VNSemi'; font-size: 19.5px; font-style: italic; line-height: 1.30;
    color: #3B3630; padding-left: 4px;
}}
</style>
</head>
<body>
<div class="canvas layout-{spec['layout']}">
    {brand_html}

    <div class="hero-header-{spec['layout']}">
        <div class="kicker-pill"><span class="kicker-txt only-text">{spec['kicker']}</span></div>
        <svg class="title-svg only-text" viewBox="0 0 {svg_w} 130" preserveAspectRatio="{'xMidYMid meet' if spec['layout']=='A' else 'xMinYMid meet'}">
            <defs>
                <linearGradient id="gold3d" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="{g0}"/>
                    <stop offset="28%" stop-color="{g1}"/>
                    <stop offset="58%" stop-color="{g2}"/>
                    <stop offset="78%" stop-color="{g3}"/>
                    <stop offset="100%" stop-color="{g4}"/>
                </linearGradient>
                <filter id="dshadow" x="-10%" y="-10%" width="130%" height="140%">
                    <feDropShadow dx="0" dy="7" stdDeviation="6" flood-color="#000000" flood-opacity="0.68"/>
                </filter>
            </defs>
            <text x="{svg_w // 2 if spec['layout']=='A' else '4'}" y="102"
                  text-anchor="{'middle' if spec['layout']=='A' else 'start'}"
                  font-family="TitleHeavy" font-weight="900" font-size="{title_fs}"{title_fit_attr}
                  fill="url(#gold3d)" stroke="{theme['accent_dark']}" stroke-width="12"
                  paint-order="stroke fill" stroke-linejoin="round" filter="url(#dshadow)">{spec['title']}</text>
        </svg>
        <div class="sub-1 only-text">{spec['subtitle_1']}</div>
        <div class="sub-2 only-text">{spec['subtitle_2']}</div>
    </div>

    <div class="sec-banner-{spec['layout']}">
        <div class="sec-big-num only-text">{spec['badge_num']}</div>
        <div class="only-text" style="text-align:left;">
            <div class="sec-l1">{spec['badge_l1']}</div>
            <div class="sec-l2">{spec['badge_l2']}</div>
        </div>
    </div>

    {cards_html_A if spec['layout'] == 'A' else cards_html_B}

    <div class="footer-bar">
        <div class="ft-left">
            <div class="ft-badge-icon">
                <svg class="only-text" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#FFF6D1" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>
                </svg>
            </div>
            <div class="ft-usage only-text">{spec['usage_text']}</div>
        </div>
        <div class="ft-mid only-text">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="{theme['title_ink']}" stroke-width="2.2" stroke-linecap="round"><path d="M3 11h18a8 8 0 0 1-8 8h-2a8 8 0 0 1-8-8Z"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <span style="color:#9E8C6C;font-weight:800;">+</span>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="{theme['title_ink']}" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="5" r="2"/><path d="m7 20 3-6 2 2 3-5"/><path d="m6 12 4-3 4 2 4-2"/></svg>
            <span style="color:#9E8C6C;font-weight:800;">+</span>
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="{theme['title_ink']}" stroke-width="2.2" stroke-linecap="round"><path d="M7 3h10l-1.5 18h-7L7 3Z"/><path d="M6 8h12"/></svg>
        </div>
        <div class="ft-legal only-text">{spec['disclaimer']}</div>
    </div>
</div>
</body>
</html>'''

def render_html_to_rgba(html_path: str, out_png: str) -> Image.Image:
    raw_png = out_png.replace(".png", "_2x.png")
    cmd = [
        BROWSER_EXE,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={W},{H}",
        "--force-device-scale-factor=2",
        "--default-background-color=00000000",
        f"--screenshot={raw_png}",
        f"file:///{html_path.replace(os.sep, '/')}",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(raw_png).convert("RGBA")
    if im.size != (W, H):
        im = im.resize((W, H), Image.Resampling.LANCZOS)
    im.save(out_png)
    try:
        os.remove(raw_png)
    except OSError:
        pass
    return im

def save_4layer_psd(layers_named: list, out_psd_path: str):
    psd_layers = []
    for name, im_rgba in reversed(layers_named):
        arr = np.array(im_rgba, dtype=np.uint8)
        channels = {
            0: arr[:, :, 0],
            1: arr[:, :, 1],
            2: arr[:, :, 2],
            -1: arr[:, :, 3],
        }
        psd_layers.append(
            nested_layers.Image(
                name=name,
                visible=True,
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
    with open(out_psd_path, "wb") as f:
        psd.write(f)

def render_one_poster(spec: dict) -> dict:
    code = spec["code"]
    theme = THEMES[spec["theme"]]
    logo_file = "logo_an_vuong_on_dark.png" if spec["brand_group"] == "AN_VUONG" else "logo_hang_thu.png"
    logo_uri = file_to_data_uri(os.path.join(CUT_DIR, logo_file))
    quad_uris = resolve_4_card_uris(spec)

    l1_bg = build_layer1_backdrop(spec, theme)

    html_cards = os.path.join(HTML_DIR, f"{code}_cards.html")
    png_cards  = os.path.join(HTML_DIR, f"{code}_cards.png")
    with open(html_cards, "w", encoding="utf-8") as f:
        f.write(build_html_for_pass(spec, theme, quad_uris, logo_uri, "cards"))
    l2_cards = render_html_to_rgba(html_cards, png_cards)

    l3_prod = build_layer3_product(spec)

    html_txt = os.path.join(HTML_DIR, f"{code}_text.html")
    png_txt  = os.path.join(HTML_DIR, f"{code}_text.png")
    with open(html_txt, "w", encoding="utf-8") as f:
        f.write(build_html_for_pass(spec, theme, quad_uris, logo_uri, "text"))
    l4_txt = render_html_to_rgba(html_txt, png_txt)

    # Notice Layer 3 (Hero Product) sits ABOVE Layer 2 (Cards) so super-sized products pop in true 3D depth, while Layer 4 (Text) stays crisp on top!
    comp = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    comp.alpha_composite(l1_bg)
    comp.alpha_composite(l2_cards)
    comp.alpha_composite(l3_prod)
    comp.alpha_composite(l4_txt)

    final_rgb = comp.convert("RGB")
    final_rgb = ImageEnhance.Sharpness(final_rgb).enhance(1.09)

    brand_dir = "01_An_Vuong_Pharma_8_Thiet_Ke" if spec["brand_group"] == "AN_VUONG" else "02_Hang_Thu_Pharma_18_Thiet_Ke"
    prod_out_dir = os.path.join(OUT_ROOT, brand_dir, spec["product_folder"])
    os.makedirs(prod_out_dir, exist_ok=True)

    prefix = "AVPM" if spec["brand_group"] == "AN_VUONG" else "HTPM"
    base_name = f"261122 {prefix} {spec['file_title']}"
    jpg_path = os.path.join(prod_out_dir, f"{base_name}.jpg")
    psd_path = os.path.join(prod_out_dir, f"{base_name}.psd")

    final_rgb.save(jpg_path, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES)
    save_4layer_psd(
        [
            ("01_Nen_Studio_3D_AI", l1_bg),
            ("02_Khung_The_Bento_Va_Minh_Hoa_3D", l2_cards),
            ("03_San_Pham_Chinh_Hang_Cutout", l3_prod),
            ("04_Logo_Va_Chu_Tieu_De_Gold_3D", l4_txt),
        ],
        psd_path,
    )
    print(f"[DONE V2] {code} -> {os.path.basename(jpg_path)} + .psd", flush=True)
    return {"code": code, "jpg": jpg_path, "psd": psd_path}

if __name__ == "__main__":
    only_codes = sys.argv[1:]
    targets = [s for s in POSTERS_26 if (not only_codes or s["code"] in only_codes)]
    print(f"Rendering {len(targets)} V2 SUPER-SIZED poster(s)...", flush=True)
    for sp in targets:
        render_one_poster(sp)
    print("ALL V2 POSTERS + 4-LAYER PSDs COMPLETED!", flush=True)
