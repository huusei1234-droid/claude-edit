# -*- coding: utf-8 -*-
"""
V3 FLAGSHIP "CHỊ HẰNG SUPER-CLEAR" INFOGRAPHIC & 4-LAYER PSD ENGINE (26 DESIGNS):
- Hero Product + Upright Sachet/Bottle scaled UP (+40% to +65% larger), crisp studio lighting, standing on a REAL sunlit 3D stone/marble podium!
- Massive 3D Gold Headlines (110px–152px, 2-line stacked giant titles in Layout B for long names — ZERO tiny text!).
- Exact Chị Hằng Bento Architecture in Layout A (Card 03 starts at x=282px revealing 3D stone podium & botanical leaves, compact square cards with ZERO empty dead space!).
- Tight-cropped 3D illustrations (+75% larger inside cards) + Golden Highlight Pill behind big 46–50px dosages + 30–32px Bold body copy!
- Outputs 1600x2000 sRGB Master .JPG + Editable 4-Layer .PSD for all 26 designs.
"""
import base64, math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageEnhance, ImageFilter
import packbits
import pytoshop
import pytoshop.codecs
pytoshop.codecs.packbits = packbits
from pytoshop.user import nested_layers
from pytoshop import enums

V3_DIR = r"d:\AI\full studio\projects\av_htpm_26_posters_v3"
sys.path.insert(0, V3_DIR)
from step3_product_catalog_26_designs import POSTERS_26, THEMES

BG_DIR = os.path.join(V3_DIR, "assets", "backdrops")
ILL_DIR = os.path.join(V3_DIR, "assets", "illusts")
CUT_DIR = os.path.join(V3_DIR, "assets", "cutouts")
HTML_DIR = os.path.join(V3_DIR, "html_passes")
OUT_ROOT = os.path.join(V3_DIR, "Final_Deliverables")
AUDIT_DIR = os.path.join(V3_DIR, "audit")

for d in (HTML_DIR, OUT_ROOT, AUDIT_DIR):
    os.makedirs(d, exist_ok=True)

FONTS_DIR = r"d:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi"
W, H = 1600, 2000

SRGB_PROFILE = ImageCms.createProfile("sRGB")
SRGB_BYTES = ImageCms.ImageCmsProfile(SRGB_PROFILE).tobytes()


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


def file_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")


def tight_crop_rgba(im: Image.Image, alpha_thresh: int = 42, pad: int = 3) -> Image.Image:
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > alpha_thresh)
    if len(xs) == 0:
        return im
    return im.crop((
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(im.width, int(xs.max()) + 1 + pad),
        min(im.height, int(ys.max()) + 1 + pad),
    ))


def draw_3d_gold_ribbons_and_leaves(canvas: Image.Image, theme_key: str, layout: str):
    """Adds subtle 3D flowing champagne-gold silk ribbons & lush corner botanical depth like Chị Hằng's sample."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov, "RGBA")

    # Top-right flowing 3D champagne-gold ribbon arc
    pts_top = []
    for t in np.linspace(0, 1, 60):
        x = int(1120 + 520 * t)
        y = int(-15 + 105 * math.sin(t * 2.3) - 25 * t)
        pts_top.append((x, y))
    for w_rib, col in [(30, (175, 128, 34, 150)), (20, (242, 204, 102, 210)), (9, (255, 245, 198, 225))]:
        d.line(pts_top, fill=col, width=w_rib, joint="curve")

    # Bottom-left flowing 3D champagne-gold ribbon (especially visible in Layout A's open left podium corner!)
    pts_bot = []
    for t in np.linspace(0, 1, 60):
        x = int(-20 + 340 * t)
        y = int(1510 + 90 * math.sin(t * 2.8) + 250 * t)
        pts_bot.append((x, y))
    for w_rib, col in [(34, (165, 118, 28, 175)), (22, (238, 196, 92, 225)), (10, (255, 244, 194, 240))]:
        d.line(pts_bot, fill=col, width=w_rib, joint="curve")

    ov = ov.filter(ImageFilter.GaussianBlur(0.8))
    canvas.alpha_composite(ov)


def draw_sunlit_3d_stone_podium(canvas: Image.Image, theme_key: str, layout: str):
    """
    Renders a crisp, tactile, sunlit 3D beveled Travertine Stone / Luxury Marble Podium
    underneath the Hero Product so the product NEVER floats in dark shadow!
    """
    pod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(pod, "RGBA")

    rng = np.random.default_rng(42)
    is_warm_stone = theme_key in ("av_emerald", "ht_jade", "ht_obsidian")

    if layout == "A":
        # Sculpted 3D angled stone slab spanning left stage x=-15..704, raised top surface y=984..1158 so boxes + pills sit squarely on stone!
        top_poly = [(-15, 1036), (492, 984), (704, 1072), (220, 1158)]
        left_face = [(-15, 1036), (220, 1158), (220, 1278), (-15, 1158)]
        right_face = [(220, 1158), (704, 1072), (704, 1188), (220, 1278)]
    else:
        # Top-Right 3D podium slab x=865..1615, top surface y=754..858
        top_poly = [(868, 804), (1245, 752), (1615, 798), (1248, 858)]
        left_face = [(868, 804), (1248, 858), (1248, 910), (868, 856)]
        right_face = [(1248, 858), (1615, 798), (1615, 856), (1248, 910)]

    if is_warm_stone:
        c_top = (232, 212, 178, 248)
        c_left = (158, 132, 98, 250)
        c_right = (118, 96, 68, 250)
        c_rim = (255, 242, 206, 235)
    else:
        c_top = (246, 234, 224, 248)
        c_left = (188, 156, 146, 250)
        c_right = (145, 112, 106, 250)
        c_rim = (255, 245, 215, 240)

    # Soft ground shadow under podium
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh, "RGBA")
    ds.polygon([(x, y + 26) for (x, y) in left_face + right_face], fill=(0, 0, 0, 155))
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    canvas.alpha_composite(sh)

    d.polygon(left_face, fill=c_left)
    d.polygon(right_face, fill=c_right)
    d.polygon(top_poly, fill=c_top)

    # Add realistic organic stone/marble travertine texture strictly inside podium polygons!
    pod_arr = np.array(pod, dtype=np.float32)
    alpha_m = pod_arr[:, :, 3] > 10
    if alpha_m.any():
        noise_fine = cv2.GaussianBlur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (0, 0), 1.4)
        noise_fine = cv2.resize(noise_fine, (W, H), interpolation=cv2.INTER_LINEAR)
        noise_vein = cv2.GaussianBlur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), (0, 0), 2.5)
        noise_vein = cv2.resize(noise_vein, (W, H), interpolation=cv2.INTER_CUBIC)
        tex = (noise_fine * 8.5 + np.sin(noise_vein * 5.0) * 7.5)[..., None]
        pod_arr[:, :, :3] = np.where(alpha_m[..., None], np.clip(pod_arr[:, :, :3] + tex, 0, 255), pod_arr[:, :, :3])

    pod = Image.fromarray(pod_arr.astype(np.uint8), "RGBA")
    d2 = ImageDraw.Draw(pod, "RGBA")
    # Crisp sunlit gold-ivory bevel catchlight along front-top edges of podium!
    d2.line([top_poly[0], top_poly[3], top_poly[2]], fill=c_rim, width=4)
    d2.line([top_poly[3], left_face[2]], fill=(255, 236, 188, 155), width=3)
    canvas.alpha_composite(pod)


def build_layer1_backdrop_v3(spec: dict, theme: dict) -> Image.Image:
    bg_path = os.path.join(BG_DIR, f"{spec['code']}_bg.png")
    im = Image.open(bg_path).convert("RGB")
    # Restore vibrant studio jewel-tone richness & contrast (undo yesterday's dull grey veil!)
    im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.16)).enhance(1.22)
    arr = np.array(im, dtype=np.float32)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ny, nx = yy / H, xx / W

    # Bright warm golden studio spotlight behind Hero Product so packaging pops 100%!
    if spec["layout"] == "A":
        spot = np.exp(-(((nx - 0.22) / 0.24) ** 2 + ((ny - 0.36) / 0.22) ** 2))
    else:
        spot = np.exp(-(((nx - 0.78) / 0.23) ** 2 + ((ny - 0.24) / 0.20) ** 2))

    gold_light = np.array([255.0, 234.0, 165.0], dtype=np.float32)
    arr = np.clip(arr + spot[:, :, None] * gold_light[None, None, :] * 0.24, 0, 255).astype(np.uint8)
    out = Image.fromarray(arr, "RGB").convert("RGBA")

    draw_3d_gold_ribbons_and_leaves(out, spec["theme"], spec["layout"])
    draw_sunlit_3d_stone_podium(out, spec["theme"], spec["layout"])
    return out


def build_layer3_product_v3(spec: dict) -> Image.Image:
    """
    SUPER-SIZED COMMANDING HERO PRODUCT (+42% to +62% larger than yesterday!),
    paired with upright stick sachets where available, crystal-clear label legibility,
    grounded firmly on the sunlit 3D stone/marble podium!
    """
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cut = tight_crop_rgba(Image.open(os.path.join(CUT_DIR, spec["cutout"])).convert("RGBA"))

    # Pair single upright boxes with upright stick sachets!
    stick_file = spec.get("extra_stick")
    if stick_file and os.path.exists(os.path.join(CUT_DIR, stick_file)):
        stick = tight_crop_rgba(Image.open(os.path.join(CUT_DIR, stick_file)).convert("RGBA"))
        bh = cut.height
        sh = int(bh * 0.82)
        sw = int(round(stick.width * (sh / stick.height)))
        stick_r = stick.resize((sw, sh), Image.Resampling.LANCZOS)
        combo_w = cut.width + int(sw * 0.62)
        combo = Image.new("RGBA", (combo_w, bh + 18), (0, 0, 0, 0))
        combo.alpha_composite(cut, dest=(0, 0))
        st_alpha = stick_r.split()[3]
        st_sh = Image.new("RGBA", stick_r.size, (0, 0, 0, 0))
        st_sh.putalpha(st_alpha.point(lambda p: int(p * 0.55)))
        st_sh = st_sh.filter(ImageFilter.GaussianBlur(15))
        combo.alpha_composite(st_sh, dest=(cut.width - int(sw * 0.44), bh - sh + 14))
        combo.alpha_composite(stick_r, dest=(cut.width - int(sw * 0.39), bh - sh + 10))
        cut = tight_crop_rgba(combo)

    aspect = cut.width / max(1.0, float(cut.height))
    if spec["layout"] == "A":
        # MASSIVE Left Hero Stage: allow 3D overlap to x=718 so wide combos (box + bottle/stick) stay TALL & HUGE!
        max_w = 716 if aspect > 0.92 else 684
        max_h = 895
        cx = 356 if aspect > 0.92 else 344
        bottom_y = 1134
    else:
        # MASSIVE Top-Right Hero Stage: x=868..1592 (up to 724px wide x 818px tall!)
        max_w = 724 if aspect > 0.92 else 690
        max_h = 818
        cx = 1236
        bottom_y = 838

    scale = min(max_w / cut.width, max_h / cut.height)
    nw, nh = int(round(cut.width * scale)), int(round(cut.height * scale))
    prod = cut.resize((nw, nh), Image.Resampling.LANCZOS)

    # Studio Packaging Clarity Polish so every small letter on the box/bottle pops razor-sharp!
    r, g, b, a = prod.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Brightness(rgb).enhance(1.08)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.07)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.5, percent=135, threshold=2))
    prod = Image.merge("RGBA", (*rgb.split(), a))

    px = max(6, min(W - nw - 6, cx - nw // 2))
    py = max(14, bottom_y - nh)
    eff_bottom = py + nh

    # Crisp Realistic Contact Shadows on the Sunlit 3D Podium
    sh_cast = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh_cast).ellipse([px - int(nw * 0.06), eff_bottom - 26, px + int(nw * 1.06), eff_bottom + 28], fill=(18, 12, 6, 155))
    sh_cast = sh_cast.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(sh_cast)

    sh_ao = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh_ao).ellipse([px + int(nw * 0.06), eff_bottom - 12, px + int(nw * 0.94), eff_bottom + 10], fill=(10, 6, 2, 225))
    sh_ao = sh_ao.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(sh_ao)

    # Subtle golden rim-halo behind product
    glow_mask = Image.new("L", (nw + 64, nh + 64), 0)
    glow_mask.paste(a, (32, 32))
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(20))
    glow_gold = Image.new("RGBA", (nw + 64, nh + 64), (255, 236, 168, 0))
    glow_gold.putalpha(glow_mask.point(lambda v: int(v * 0.42)))
    canvas.alpha_composite(glow_gold, dest=(max(0, px - 32), max(0, py - 32)))

    canvas.alpha_composite(prod, dest=(px, py))
    return canvas


def split_title_for_layout_b(title: str) -> list[str]:
    """Splits long product titles (>= 12 chars) into 2 massive balanced lines for Layout B so text is HUGE!"""
    words = title.strip().split()
    if len(title) <= 11 or len(words) <= 1:
        return [title]
    # Find word split closest to half character length
    best_idx = 1
    best_diff = 999
    for i in range(1, len(words)):
        l1 = " ".join(words[:i])
        l2 = " ".join(words[i:])
        diff = abs(len(l1) - len(l2))
        if diff < best_diff:
            best_diff = diff
            best_idx = i
    return [" ".join(words[:best_idx]), " ".join(words[best_idx:])]


def build_title_svg(spec: dict, theme: dict) -> tuple[str, int]:
    g0, g1, g2, g3, g4 = theme["gold_grad"]
    title = spec["title"]
    layout = spec["layout"]

    if layout == "A":
        box_w = 1156
        n = len(title)
        fs = 148 if n <= 10 else (130 if n <= 13 else (112 if n <= 16 else 98))
        est_w = n * fs * 0.66
        fit = f' textLength="{int(box_w * 0.95)}" lengthAdjust="spacingAndGlyphs"' if est_w > box_w * 0.95 else ""
        svg_h = 152
        svg = f'''<svg class="title-svg only-text" viewBox="0 0 {box_w} {svg_h}" preserveAspectRatio="xMidYMid meet">
            <defs>
                <linearGradient id="gold3d" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#FFFDF2"/>
                    <stop offset="30%" stop-color="{g1}"/>
                    <stop offset="62%" stop-color="{g2}"/>
                    <stop offset="82%" stop-color="{g3}"/>
                    <stop offset="100%" stop-color="{g4}"/>
                </linearGradient>
                <filter id="dshadow" x="-10%" y="-10%" width="130%" height="145%">
                    <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000000" flood-opacity="0.72"/>
                </filter>
            </defs>
            <text x="{box_w // 2}" y="122" text-anchor="middle"
                  font-family="TitleHeavy" font-weight="900" font-size="{fs}"{fit}
                  fill="url(#gold3d)" stroke="{theme['accent_dark']}" stroke-width="8"
                  paint-order="stroke fill" stroke-linejoin="round" filter="url(#dshadow)">{title}</text>
        </svg>'''
        return svg, svg_h
    else:
        box_w = 842
        lines = split_title_for_layout_b(title)
        if len(lines) == 1:
            n = len(lines[0])
            fs = 142 if n <= 8 else (128 if n <= 11 else 112)
            est_w = n * fs * 0.66
            fit = f' textLength="{int(box_w * 0.97)}" lengthAdjust="spacingAndGlyphs"' if est_w > box_w * 0.97 else ""
            svg_h = 152
            text_els = f'''<text x="4" y="122" text-anchor="start"
                  font-family="TitleHeavy" font-weight="900" font-size="{fs}"{fit}
                  fill="url(#gold3d)" stroke="{theme['accent_dark']}" stroke-width="8"
                  paint-order="stroke fill" stroke-linejoin="round" filter="url(#dshadow)">{lines[0]}</text>'''
        else:
            max_n = max(len(lines[0]), len(lines[1]))
            fs = 118 if max_n <= 9 else (108 if max_n <= 11 else 96)
            svg_h = 236
            els = []
            for idx, ln in enumerate(lines):
                est_w = len(ln) * fs * 0.66
                fit = f' textLength="{int(box_w * 0.97)}" lengthAdjust="spacingAndGlyphs"' if est_w > box_w * 0.97 else ""
                y_pos = 102 if idx == 0 else 216
                els.append(f'''<text x="4" y="{y_pos}" text-anchor="start"
                      font-family="TitleHeavy" font-weight="900" font-size="{fs}"{fit}
                      fill="url(#gold3d)" stroke="{theme['accent_dark']}" stroke-width="8"
                      paint-order="stroke fill" stroke-linejoin="round" filter="url(#dshadow)">{ln}</text>''')
            text_els = "\n".join(els)

        svg = f'''<svg class="title-svg only-text" style="height:{svg_h}px" viewBox="0 0 {box_w} {svg_h}" preserveAspectRatio="xMinYMid meet">
            <defs>
                <linearGradient id="gold3d" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#FFFDF2"/>
                    <stop offset="30%" stop-color="{g1}"/>
                    <stop offset="62%" stop-color="{g2}"/>
                    <stop offset="82%" stop-color="{g3}"/>
                    <stop offset="100%" stop-color="{g4}"/>
                </linearGradient>
                <filter id="dshadow" x="-10%" y="-10%" width="130%" height="145%">
                    <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000000" flood-opacity="0.72"/>
                </filter>
            </defs>
            {text_els}
        </svg>'''
        return svg, svg_h


def build_html_v3(spec: dict, theme: dict, card_uris: list, logo_uri: str, pass_mode: str) -> str:
    show_cards = (pass_mode == "cards")
    show_text = (pass_mode == "text")

    g0, g1, g2, g3, g4 = theme["gold_grad"]
    title_svg, title_h = build_title_svg(spec, theme)

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
                <div class="ht-brand-sub">Tinh Hoa Thảo Dược Việt</div>
            </div>
        </div>'''

    cards_html_A = ""
    for i, (num, c_title, c_metric, c_desc) in enumerate(spec["cards"]):
        q_uri = card_uris[i]
        mlen = len(c_metric)
        if i < 2:
            m_fs = 42 if mlen <= 11 else (34 if mlen <= 16 else 29.5)
        else:
            m_fs = 46 if mlen <= 13 else (40 if mlen <= 18 else 35)
        cards_html_A += f'''
        <div class="bento-card card-{i+1}">
            <div class="num-pill"><span class="only-text">{num}</span></div>
            <div class="card-inner">
                <div class="card-head only-text">{c_title}</div>
                <div class="card-illust-wrap only-cards">
                    <img src="{q_uri}" class="card-illust" />
                </div>
                <div class="card-copy">
                    <div class="metric-pill"><span class="card-metric only-text" style="font-size:{m_fs}px">{c_metric}</span></div>
                    <div class="card-desc only-text">{c_desc}</div>
                </div>
            </div>
        </div>'''

    cards_html_B = ""
    for i, (num, c_title, c_metric, c_desc) in enumerate(spec["cards"]):
        q_uri = card_uris[i]
        mlen = len(c_metric)
        mb_fs = 34 if mlen <= 15 else (30 if mlen <= 19 else 27)
        cards_html_B += f'''
        <div class="bento-card card-{i+1}">
            <div class="num-pill"><span class="only-text">{num}</span></div>
            <div class="card-inner">
                <div class="card-illust-wrap only-cards">
                    <img src="{q_uri}" class="card-illust" />
                </div>
                <div class="card-copy">
                    <div class="card-head-inline only-text">{c_title}</div>
                    <div class="metric-pill-b"><span class="card-metric-b only-text" style="font-size:{mb_fs}px">{c_metric}</span></div>
                    <div class="card-desc-b only-text">{c_desc}</div>
                </div>
            </div>
        </div>'''

    # Adjust Layout B subtitle sizes slightly when 2-line giant title is active so zero vertical collision occurs!
    is_2line_b = (spec["layout"] == "B" and title_h > 180)
    sub1_b_fs = "33px" if is_2line_b else "38px"
    sub2_b_fs = "26px" if is_2line_b else "29px"
    hdr_b_top = "172px" if is_2line_b else "208px"

    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<style>
@font-face {{ font-family: 'TitleHeavy'; src: url('file:///{FONTS_DIR}/Montserrat-Black.ttf'); font-weight: 900; }}
@font-face {{ font-family: 'VNExtra'; src: url('file:///{FONTS_DIR}/BeVietnamPro-ExtraBold.ttf'); font-weight: 800; }}
@font-face {{ font-family: 'VNBold'; src: url('file:///{FONTS_DIR}/BeVietnamPro-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: 'VNSemi'; src: url('file:///{FONTS_DIR}/BeVietnamPro-SemiBold.ttf'); font-weight: 600; }}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
    width: {W}px; height: {H}px; overflow: hidden;
    background: transparent !important;
    font-family: 'VNBold', sans-serif;
    -webkit-font-smoothing: antialiased;
}}

.only-cards {{ visibility: {'visible' if show_cards else 'hidden'}; }}
.only-text  {{ visibility: {'visible' if show_text else 'hidden'}; }}

.canvas {{ position: relative; width: {W}px; height: {H}px; }}

/* BRAND LOGO — CRISP & PROMINENT */
.brand-av {{
    position: absolute; left: 24px; top: 18px; width: 396px; height: 222px;
    display: flex; align-items: center; justify-content: flex-start;
}}
.layout-B .brand-av {{
    top: 16px; height: 152px;
}}
.av-logo-img {{
    max-width: 386px; max-height: 214px; object-fit: contain;
    filter: drop-shadow(0 6px 16px rgba(0,0,0,0.65));
}}
.layout-B .av-logo-img {{
    max-width: 340px; max-height: 146px;
}}
.brand-ht {{
    position: absolute; left: 22px; top: 24px;
    display: flex; align-items: center; gap: 11px;
    padding: 8px 18px 8px 10px;
    border-radius: 60px;
    background: {'rgba(255,252,242,0.16)' if show_cards else 'transparent'};
    border: {'2.5px solid rgba(250,216,132,0.72)' if show_cards else '2.5px solid transparent'};
}}
.ht-logo-img {{
    width: 76px; height: 76px; object-fit: contain;
    visibility: {'visible' if show_text else 'hidden'};
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.55));
}}
.ht-brand-txt {{ visibility: {'visible' if show_text else 'hidden'}; }}
.ht-brand-name {{
    font-family: 'VNExtra'; font-size: 23.5px; letter-spacing: 0.4px;
    color: #FFF9DE; text-shadow: 0 3px 10px rgba(0,0,0,0.65);
}}
.ht-brand-sub {{
    font-family: 'VNBold'; font-size: 16.5px; color: #FFE59E; margin-top: 2px;
}}

/* HERO HEADLINE & SUBTITLE — CHỊ HẰNG MASSIVE CLARITY */
.hero-header-A {{
    position: absolute; left: 418px; right: 24px; top: 18px;
    text-align: center;
}}
.hero-header-B {{
    position: absolute; left: 32px; width: 842px; top: {hdr_b_top};
    text-align: left;
}}
.title-svg {{
    width: 100%; height: 152px; overflow: visible; display: block;
}}
.sub-1 {{
    font-family: 'VNExtra'; font-size: 38.5px; line-height: 1.20;
    color: #FFFFFF; text-shadow: 0 3px 14px rgba(0,0,0,0.82);
    margin-top: 2px; text-wrap: balance;
}}
.sub-2 {{
    font-family: 'VNBold'; font-size: 29.5px; line-height: 1.24;
    color: #FFECA8; text-shadow: 0 2px 12px rgba(0,0,0,0.78);
    margin-top: 5px; text-wrap: balance;
}}
.layout-B .sub-1 {{ font-size: {sub1_b_fs}; margin-top: 6px; }}
.layout-B .sub-2 {{ font-size: {sub2_b_fs}; margin-top: 6px; }}

/* SECTION HIGHLIGHT BANNER — BOLD GOLD DOUBLE-GLOW */
.sec-banner-A {{
    position: absolute; left: 696px; right: 28px; top: 312px; height: 144px;
    border-radius: 28px;
    background: {theme['pill_bg'] if show_cards else 'transparent'};
    border: {'3.5px solid #F7D77E' if show_cards else '3.5px solid transparent'};
    box-shadow: {'0 16px 32px rgba(0,0,0,0.46), inset 0 2px 0 rgba(255,255,255,0.34)' if show_cards else 'none'};
    display: flex; align-items: center; justify-content: center; gap: 22px; padding: 0 22px;
}}
.sec-banner-B {{
    position: absolute; left: 28px; width: 846px; top: 676px; height: 144px;
    border-radius: 28px;
    background: {theme['pill_bg'] if show_cards else 'transparent'};
    border: {'3.5px solid #F7D77E' if show_cards else '3.5px solid transparent'};
    box-shadow: {'0 16px 32px rgba(0,0,0,0.46), inset 0 2px 0 rgba(255,255,255,0.34)' if show_cards else 'none'};
    display: flex; align-items: center; justify-content: flex-start; gap: 24px; padding: 0 28px;
}}
.sec-big-num {{
    font-family: 'TitleHeavy'; font-size: 124px; line-height: 0.92;
    background: linear-gradient(180deg, #FFFDF0 0%, {g1} 38%, {g2} 75%, {g4} 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 5px 10px rgba(0,0,0,0.55));
}}
.sec-l1 {{
    font-family: 'VNExtra'; font-size: 42px; letter-spacing: 0.5px;
    color: #FFFFFF; line-height: 1.10; text-transform: uppercase;
    text-shadow: 0 3px 10px rgba(0,0,0,0.55);
}}
.sec-l2 {{
    font-family: 'VNExtra'; font-size: 25.5px; letter-spacing: 0.4px;
    color: #FFEAA2; margin-top: 5px; text-transform: uppercase;
}}

/* BENTO CARDS — BRIGHT CREAM WITH RICH GOLD BORDER & ZERO DEAD SPACE */
.bento-card {{
    position: absolute;
    border-radius: 30px;
    background: {'linear-gradient(180deg, #FFFEFB 0%, #FCF3DE 100%)' if show_cards else 'transparent'};
    border: {'3.5px solid #F3CC6E' if show_cards else '3.5px solid transparent'};
    box-shadow: {'0 18px 38px rgba(0,0,0,0.42), inset 0 2px 0 #FFFFFF' if show_cards else 'none'};
}}
.num-pill {{
    position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
    min-width: 82px; height: 54px; padding: 0 20px;
    border-radius: 28px;
    background: {theme['num_bg'] if show_cards else 'transparent'};
    border: {'2.5px solid #F8DA86' if show_cards else '2.5px solid transparent'};
    box-shadow: {'0 5px 12px rgba(0,0,0,0.28)' if show_cards else 'none'};
    display: flex; align-items: center; justify-content: center;
    font-family: 'VNExtra'; font-size: 31px; color: #FFFFFF; letter-spacing: 0.8px;
    z-index: 5;
}}

/* LAYOUT A: CHỊ HẰNG EXACT COMPACT ZERO-GAP BENTO GRID */
.layout-A .card-1 {{ left: 696px; width: 426px; top: 478px; height: 668px; }}
.layout-A .card-2 {{ left: 1144px; width: 428px; top: 478px; height: 668px; }}
.layout-A .card-3 {{ left: 282px; width: 632px; top: 1170px; height: 648px; }}
.layout-A .card-4 {{ left: 938px; width: 634px; top: 1170px; height: 648px; }}

.layout-A .card-inner {{
    width: 100%; height: 100%; padding: 70px 14px 22px 14px;
    display: flex; flex-direction: column; align-items: center; justify-content: space-between;
    text-align: center;
}}
.layout-A .card-3 .card-inner, .layout-A .card-4 .card-inner {{
    padding: 70px 20px 22px 20px;
}}
.layout-A .card-head {{
    font-family: 'VNExtra'; font-size: 34px; line-height: 1.13;
    color: #0E1B14; text-transform: uppercase;
    min-height: 74px; display: flex; align-items: center; justify-content: center;
    text-wrap: balance; letter-spacing: -0.2px;
}}
.layout-A .card-3 .card-head, .layout-A .card-4 .card-head {{
    font-size: 38px; min-height: 52px;
}}
.layout-A .card-1 .card-illust-wrap, .layout-A .card-2 .card-illust-wrap {{
    width: 392px; height: 294px;
    background: {'radial-gradient(circle, rgba(248,220,142,0.42) 0%, rgba(255,253,248,0) 70%)' if show_cards else 'transparent'};
    display: flex; align-items: center; justify-content: center;
}}
.layout-A .card-3 .card-illust-wrap, .layout-A .card-4 .card-illust-wrap {{
    width: 532px; height: 312px;
    background: {'radial-gradient(circle, rgba(248,220,142,0.42) 0%, rgba(255,253,248,0) 70%)' if show_cards else 'transparent'};
    display: flex; align-items: center; justify-content: center;
}}
.card-illust {{
    width: 97%; height: 97%; object-fit: contain;
}}
.layout-A .card-copy {{
    width: 100%; display: flex; flex-direction: column; align-items: center;
}}
.metric-pill {{
    width: 95%; padding: 7px 12px; border-radius: 36px; margin-bottom: 8px;
    background: {'linear-gradient(90deg, rgba(248,222,145,0.18) 0%, rgba(245,208,108,0.68) 50%, rgba(248,222,145,0.18) 100%)' if show_cards else 'transparent'};
    display: flex; align-items: center; justify-content: center;
}}
.layout-A .card-metric {{
    font-family: 'VNExtra'; font-size: 42px; line-height: 1.12; white-space: nowrap;
    color: {theme['title_ink']}; letter-spacing: -0.3px;
}}
.layout-A .card-desc {{
    font-family: 'VNBold'; font-size: 27px; line-height: 1.23;
    color: #1A1917; max-width: 400px; text-wrap: balance;
}}
.layout-A .card-3 .card-desc, .layout-A .card-4 .card-desc {{
    font-size: 30px; line-height: 1.24; max-width: 592px;
}}

/* LAYOUT B: FULL-PACKED 2x2 CARDS WITH HUGE ILLUSTRATIONS & LARGE BOLD TEXT */
.layout-B .card-1 {{ left: 28px;  width: 758px; top: 854px;  height: 472px; }}
.layout-B .card-2 {{ left: 814px; width: 758px; top: 854px;  height: 472px; }}
.layout-B .card-3 {{ left: 28px;  width: 758px; top: 1350px; height: 472px; }}
.layout-B .card-4 {{ left: 814px; width: 758px; top: 1350px; height: 472px; }}
.layout-B .num-pill {{ top: -24px; left: 56px; transform: none; }}

.layout-B .card-inner {{
    width: 100%; height: 100%; padding: 24px 20px 18px 14px;
    display: grid; grid-template-columns: 312px 1fr; gap: 16px; align-items: center;
}}
.layout-B .card-illust-wrap {{
    grid-column: 1; grid-row: 1 / span 2;
    width: 308px; height: 422px;
    border-radius: 24px;
    background: {'radial-gradient(circle, rgba(246,216,136,0.44) 0%, rgba(255,253,248,0) 74%)' if show_cards else 'transparent'};
    display: flex; align-items: center; justify-content: center;
}}
.layout-B .card-copy {{
    grid-column: 2; grid-row: 1 / span 2;
    text-align: left; display: flex; flex-direction: column; justify-content: center; gap: 8px;
}}
.layout-B .card-head-inline {{
    font-family: 'VNExtra'; font-size: 37px; line-height: 1.13;
    color: #0E1B14; text-transform: uppercase;
    text-wrap: balance; letter-spacing: -0.2px;
}}
.metric-pill-b {{
    display: inline-flex; align-self: flex-start;
    padding: 7px 22px; border-radius: 34px;
    background: {'linear-gradient(90deg, rgba(244,205,102,0.68) 0%, rgba(248,224,152,0.34) 100%)' if show_cards else 'transparent'};
}}
.card-metric-b {{
    font-family: 'VNExtra'; font-size: 34px; line-height: 1.12; white-space: nowrap; color: {theme['title_ink']};
}}
.card-desc-b {{
    font-family: 'VNBold'; font-size: 29px; line-height: 1.26; color: #1A1917; text-wrap: balance;
}}

/* FOOTER BAR — HIGH-CONTRAST & CLEAR */
.footer-bar {{
    position: absolute; left: 28px; right: 28px; bottom: 22px; height: 134px;
    border-radius: 28px;
    background: {'linear-gradient(180deg, #FFFEFB 0%, #FAF0DD 100%)' if show_cards else 'transparent'};
    border: {'3px solid #F3CC6E' if show_cards else '3px solid transparent'};
    box-shadow: {'0 12px 26px rgba(0,0,0,0.36)' if show_cards else 'none'};
    display: grid; grid-template-columns: 1.25fr 176px 1.0fr; align-items: center;
    padding: 0 22px; gap: 16px;
}}
.ft-left {{ display: flex; align-items: center; gap: 15px; }}
.ft-badge-icon {{
    width: 72px; height: 72px; border-radius: 50%; flex-shrink: 0;
    background: {theme['num_bg'] if show_cards else 'transparent'};
    display: flex; align-items: center; justify-content: center;
}}
.ft-usage {{
    font-family: 'VNExtra'; font-size: 24.5px; line-height: 1.24; color: #141815;
}}
.ft-mid {{
    display: flex; align-items: center; justify-content: center; gap: 8px;
    border-left: {'2.5px solid rgba(130,110,70,0.34)' if show_cards else 'none'};
    border-right: {'2.5px solid rgba(130,110,70,0.34)' if show_cards else 'none'};
    height: 86px;
}}
.ft-legal {{
    font-family: 'VNSemi'; font-size: 20.5px; font-style: italic; line-height: 1.26;
    color: #2B2722; padding-left: 4px;
}}
</style>
</head>
<body>
<div class="canvas layout-{spec['layout']}">
    {brand_html}

    <div class="hero-header-{spec['layout']}">
        {title_svg}
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
                <svg class="only-text" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#FFF6D1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>
                </svg>
            </div>
            <div class="ft-usage only-text">{spec['usage_text']}</div>
        </div>
        <div class="ft-mid only-text">
            <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="{theme['title_ink']}" stroke-width="2.4" stroke-linecap="round"><path d="M3 11h18a8 8 0 0 1-8 8h-2a8 8 0 0 1-8-8Z"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <span style="color:#8C7A5B;font-weight:900;font-size:22px;">+</span>
            <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="{theme['title_ink']}" stroke-width="2.4" stroke-linecap="round"><circle cx="12" cy="5" r="2"/><path d="m7 20 3-6 2 2 3-5"/><path d="m6 12 4-3 4 2 4-2"/></svg>
            <span style="color:#8C7A5B;font-weight:900;font-size:22px;">+</span>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="{theme['title_ink']}" stroke-width="2.4" stroke-linecap="round"><path d="M7 3h10l-1.5 18h-7L7 3Z"/><path d="M6 8h12"/></svg>
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


def render_one_poster_v3(spec: dict, write_psd: bool = True) -> dict:
    code = spec["code"]
    theme = THEMES[spec["theme"]]
    logo_file = "logo_an_vuong_on_dark.png" if spec["brand_group"] == "AN_VUONG" else "logo_hang_thu.png"
    logo_uri = file_to_data_uri(os.path.join(CUT_DIR, logo_file))
    card_uris = [file_to_data_uri(os.path.join(ILL_DIR, f"{code}_c{i+1}.png")) for i in range(4)]

    l1_bg = build_layer1_backdrop_v3(spec, theme)

    html_cards = os.path.join(HTML_DIR, f"{code}_cards.html")
    png_cards  = os.path.join(HTML_DIR, f"{code}_cards.png")
    with open(html_cards, "w", encoding="utf-8") as f:
        f.write(build_html_v3(spec, theme, card_uris, logo_uri, "cards"))
    l2_cards = render_html_to_rgba(html_cards, png_cards)

    l3_prod = build_layer3_product_v3(spec)

    html_txt = os.path.join(HTML_DIR, f"{code}_text.html")
    png_txt  = os.path.join(HTML_DIR, f"{code}_text.png")
    with open(html_txt, "w", encoding="utf-8") as f:
        f.write(build_html_v3(spec, theme, card_uris, logo_uri, "text"))
    l4_txt = render_html_to_rgba(html_txt, png_txt)

    comp = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    comp.alpha_composite(l1_bg)
    comp.alpha_composite(l2_cards)
    comp.alpha_composite(l3_prod)
    comp.alpha_composite(l4_txt)

    final_rgb = ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.10)

    brand_dir = "01_An_Vuong_Pharma_8_Thiet_Ke" if spec["brand_group"] == "AN_VUONG" else "02_Hang_Thu_Pharma_18_Thiet_Ke"
    prod_out_dir = os.path.join(OUT_ROOT, brand_dir, spec["product_folder"])
    os.makedirs(prod_out_dir, exist_ok=True)

    prefix = "AVPM" if spec["brand_group"] == "AN_VUONG" else "HTPM"
    base_name = f"261122 {prefix} {spec['file_title']}"
    jpg_path = os.path.join(prod_out_dir, f"{base_name}.jpg")
    psd_path = os.path.join(prod_out_dir, f"{base_name}.psd")

    final_rgb.save(jpg_path, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES)
    if write_psd:
        save_4layer_psd(
            [
                ("01_Nen_Studio_Va_Buc_Da_3D", l1_bg),
                ("02_Khung_The_Bento_Va_Minh_Hoa_3D", l2_cards),
                ("03_San_Pham_Chinh_Hang_Co_Lon", l3_prod),
                ("04_Logo_Va_Chu_To_Ro_Gold_3D", l4_txt),
            ],
            psd_path,
        )
    print(f"[DONE V3] {code} -> {os.path.basename(jpg_path)}", flush=True)
    return {"code": code, "jpg": jpg_path, "psd": psd_path}


if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor, as_completed
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_psd = "--no-psd" in sys.argv[1:]
    targets = [s for s in POSTERS_26 if (not args or s["code"] in args)]
    print(f"Rendering {len(targets)} V3 CHỊ-HẰNG-STANDARD poster(s) in parallel...", flush=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(render_one_poster_v3, sp, not no_psd) for sp in targets]
        for f in as_completed(futs):
            f.result()
    print("V3 RENDER COMPLETE!", flush=True)
