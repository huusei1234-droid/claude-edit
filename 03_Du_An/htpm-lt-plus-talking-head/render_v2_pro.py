import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

PROJ_DIR   = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media_v2")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
PHOTOS_DIR = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\Ảnh"
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

# Exact Brand & Editorial Typography
FONT_BRAND_SERIF = r"C:\Windows\Fonts\timesbd.ttf"  # 1:1 match with physical LT PLUS HẰNG THU box!
FONT_SANS_BOLD   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-Bold.ttf"
FONT_SANS_XBOLD  = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-ExtraBold.ttf"
FONT_EDIT_ITALIC = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\PlayfairDisplay-BoldItalic.ttf"
FONT_CAP         = r"C:\Windows\Fonts\palabi.ttf"
FONT_SUB         = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-Medium.ttf"

# Exact sampled brand colors from 4.png (LT PLUS HẰNG THU box)
BRAND_RED_TOP  = (242, 6, 16)
BRAND_RED_BOT  = (198, 0, 10)
BRAND_EXTRUDE  = (58, 4, 10)
BRAND_PINK_BG1 = (253, 224, 237)
BRAND_PINK_BG2 = (248, 198, 221)
BRAND_GOLD     = (228, 182, 108)

_font_cache = {}
def get_font(path, size):
    key = (path, max(10, int(round(size))))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, key[1])
    return _font_cache[key]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def quintic_smooth(u):
    """C2-continuous velocity & acceleration smoothstep: zero jerk, butter-smooth keyframes!"""
    u = clamp01(u)
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

def ease_out_quart(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 4.0

def smooth_env(t, t0, t1, d_in=0.48, d_out=0.42):
    if t <= t0 or t >= t1:
        return 0.0
    a_in = quintic_smooth((t - t0) / max(0.05, d_in)) if (t - t0) < d_in else 1.0
    a_out = quintic_smooth((t1 - t) / max(0.05, d_out)) if (t1 - t) < d_out else 1.0
    return min(a_in, a_out)

def fit_cover_subpixel(rgb_arr, target_w, target_h, zoom=1.0, pan_x=0.0, pan_y=0.0):
    """Subpixel-smooth affine crop/scale with BICUBIC filtering — 0% integer-pixel stepping jitter!"""
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    inv_s = 1.0 / base_scale
    cx_src = sw * 0.5 + pan_x * sw
    cy_src = sh * 0.5 + pan_y * sh
    a = inv_s
    c = cx_src - (target_w * 0.5) * inv_s
    e = inv_s
    f = cy_src - (target_h * 0.5) * inv_s
    im = Image.fromarray(rgb_arr, "RGB")
    return im.transform((target_w, target_h), Image.Transform.AFFINE, (a, 0.0, c, 0.0, e, f), resample=Image.Resampling.BICUBIC)

def paste_subpixel(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0, blur_px=0.0):
    """True floating-point subpixel sprite placement via BICUBIC affine transform (zero 1px snapping!)."""
    if opacity <= 0.008 or scale <= 0.02:
        return
    im = sprite_im
    if blur_px >= 0.55:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(10.0, blur_px)))

    sw, sh = im.size
    out_w = int(math.ceil(sw * scale)) + 6
    out_h = int(math.ceil(sh * scale)) + 6
    x0 = int(math.floor(cx - out_w * 0.5))
    y0 = int(math.floor(cy - out_h * 0.5))

    sub_cx = cx - x0
    sub_cy = cy - y0
    inv_s = 1.0 / scale
    c_off = sw * 0.5 - sub_cx * inv_s
    f_off = sh * 0.5 - sub_cy * inv_s

    transformed = im.transform(
        (out_w, out_h),
        Image.Transform.AFFINE,
        (inv_s, 0.0, c_off, 0.0, inv_s, f_off),
        resample=Image.Resampling.BICUBIC
    )
    if opacity < 0.996:
        arr = np.array(transformed)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        transformed = Image.fromarray(arr, "RGBA")

    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(canvas_im.width, x0 + out_w), min(canvas_im.height, y0 + out_h)
    if dx1 > dx0 and dy1 > dy0:
        crop_box = (dx0 - x0, dy0 - y0, dx1 - x0, dy1 - y0)
        canvas_im.alpha_composite(transformed.crop(crop_box), dest=(dx0, dy0))

# ======================================================================
# 1. BRIGHT NATURAL COLOR POLISH (ZERO DARKENING!)
# ======================================================================
def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.96) * 1.015, 0.0, 1.0)
    lr = np.clip(y * 255.0 * 1.015, 0, 255).astype(np.uint8)
    lg = np.clip(y * 255.0 * 1.005, 0, 255).astype(np.uint8)
    lb = np.clip(y * 255.0 * 0.996, 0, 255).astype(np.uint8)
    return lr, lg, lb

BRIGHT_LUT = _build_bright_lut()

def polish_bright_frame(rgb):
    out = np.empty_like(rgb)
    out[:, :, 0] = BRIGHT_LUT[0][rgb[:, :, 0]]
    out[:, :, 1] = BRIGHT_LUT[1][rgb[:, :, 1]]
    out[:, :, 2] = BRIGHT_LUT[2][rgb[:, :, 2]]
    return out

# ======================================================================
# 2. TEXT & BRAND LOGO SPRITE RENDERER
# ======================================================================
_sprite_cache = {}
def render_pro_text_sprite(text, font_path, size, top_col, bot_col=None, stroke_col=(255, 255, 255), stroke_w=6, glow_col=None, glow_rad=8, shadow_alpha=90, extrude_col=None):
    bot_col = bot_col or top_col
    key = ("pro", text, font_path, int(round(size)), top_col, bot_col, stroke_col, stroke_w, glow_col, int(round(glow_rad)), shadow_alpha, extrude_col)
    if key in _sprite_cache:
        return _sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(max(glow_rad * 2.6, 12) + stroke_w + 16)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    if glow_col and glow_rad > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(0, stroke_w // 2), stroke_fill=255)
        g1 = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad * 0.8)), dtype=np.float32)
        g2 = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad * 1.9)), dtype=np.float32)
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0] = glow_col[0]; ga[:, :, 1] = glow_col[1]; ga[:, :, 2] = glow_col[2]
        ga[:, :, 3] = np.clip(g1 * 0.65 + g2 * 0.38, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 5), text, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)
        sm_b = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5.5)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0] = 18; sa[:, :, 1] = 20; sa[:, :, 2] = 32
        sa[:, :, 3] = np.clip(sm_b * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    if stroke_w > 0 and stroke_col is not None:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        base = Image.alpha_composite(base, st_im)

    if extrude_col is not None:
        ex_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(ex_im).text((ox + 2, oy + 2), text, font=font, fill=(*extrude_col, 235))
        base = Image.alpha_composite(base, ex_im)

    mask_im = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), text, font=font, fill=255)
    arr_m = np.array(mask_im, dtype=np.float32) / 255.0
    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)[:, None]
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.uint8)
    for c in range(3):
        grad_rgb[:, :, c] = np.clip(top_col[c] * (1.0 - yy) + bot_col[c] * yy, 0, 255).astype(np.uint8)
    fill_im = Image.fromarray(np.dstack([grad_rgb, (arr_m * 255.0).astype(np.uint8)]), "RGBA")
    base = Image.alpha_composite(base, fill_im)

    if len(_sprite_cache) > 700:
        _sprite_cache.clear()
    _sprite_cache[key] = base
    return base

def draw_minimal_glass_tag(canvas_im, label_txt, cx, cy, accent_rgb=(220, 38, 68), opacity=1.0):
    if not label_txt or opacity <= 0.01:
        return
    sp = render_pro_text_sprite(label_txt, FONT_SANS_BOLD, 24, (255, 255, 255), stroke_w=0, shadow_alpha=40)
    pw, ph = sp.width + 44, 46
    tag = Image.new("RGBA", (pw + 12, ph + 12), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle([6, 6, 6 + pw, 6 + ph], radius=23, fill=(24, 22, 32, 168), outline=(255, 255, 255, 195), width=2)
    td.ellipse([18, 6 + ph // 2 - 5, 28, 6 + ph // 2 + 5], fill=(*accent_rgb, 255))
    paste_subpixel(tag, sp, 6 + pw * 0.5 + 8, 6 + ph * 0.5, scale=1.0, opacity=1.0)
    paste_subpixel(canvas_im, tag, cx, cy, scale=1.0, opacity=opacity)

# ======================================================================
# 3. AUTHENTIC 4K RGBA LT PLUS PRODUCT STUDIO GROUPS (0% AI MUTATION!)
# ======================================================================
_real_prod_cache = {}
def get_real_product_overlay(mode="hydrogel"):
    """
    Pre-composites the 100% authentic 4K RGBA LT PLUS HẰNG THU box (4.png), open magnetic box (6.png),
    and 15-tablet bottle (2.png) with realistic glossy mirror reflection & dual-layer contact shadow
    so they sit like real studio photography on top of the living animated Flow stages!
    """
    if mode in _real_prod_cache:
        return _real_prod_cache[mode]

    cw, ch = 1080, 900
    layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    box_closed = Image.open(os.path.join(PHOTOS_DIR, "4.png")).convert("RGBA")
    box_open   = Image.open(os.path.join(PHOTOS_DIR, "6.png")).convert("RGBA")
    bottle     = Image.open(os.path.join(PHOTOS_DIR, "2.png")).convert("RGBA")

    def place_item(item_rgba, cx, base_y, target_h, refl_alpha=0.25):
        sc = target_h / float(item_rgba.height)
        nw, nh = int(round(item_rgba.width * sc)), int(round(item_rgba.height * sc))
        it = item_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
        px = int(round(cx - nw / 2.0))
        py = int(round(base_y - nh))

        # Glossy surface reflection
        refl = it.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        refl_arr = np.array(refl, dtype=np.float32)
        fade_h = min(nh, int(nh * 0.42))
        fade = np.zeros((nh, 1), dtype=np.float32)
        fade[:fade_h, 0] = np.linspace(refl_alpha, 0.0, fade_h) ** 1.6
        refl_arr[:, :, 3] *= fade
        refl_im = Image.fromarray(np.clip(refl_arr, 0, 255).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(radius=3.2))
        layer.alpha_composite(refl_im, dest=(px, base_y - 5))

        # Soft ambient + tight contact occlusion shadows
        sh = Image.new("RGBA", (nw + 80, 68), (0, 0, 0, 0))
        sh_col = (85, 68, 82, 78) if mode == "hydrogel" else (105, 58, 76, 88)
        ImageDraw.Draw(sh).ellipse([26, 20, nw + 54, 52], fill=sh_col)
        layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(radius=11)), dest=(px - 40, base_y - 36))

        sh_t = Image.new("RGBA", (nw + 40, 34), (0, 0, 0, 0))
        ImageDraw.Draw(sh_t).ellipse([20, 11, nw + 20, 24], fill=(55, 34, 46, 122))
        layer.alpha_composite(sh_t.filter(ImageFilter.GaussianBlur(radius=3.5)), dest=(px - 20, base_y - 19))

        # Crisp authentic packaging with subtle studio lift
        it_rgb = ImageEnhance.Brightness(it.convert("RGB")).enhance(1.03)
        it_clean = Image.fromarray(np.dstack([np.array(it_rgb), np.array(it)[:, :, 3]]), "RGBA")
        layer.alpha_composite(it_clean, dest=(px, py))

    if mode == "hydrogel":
        # Centered between the left & right rising pearl herb bubbles (x=310..770, above head y<=565!)
        place_item(box_closed, 455, 548, 335, refl_alpha=0.28)
        place_item(bottle,     705, 556, 272, refl_alpha=0.28)
    else:
        # Luxury trio hero on the sunlit pearl-crystal pedestal (x=130..950, above head y<=560!)
        place_item(box_open,   275, 548, 415, refl_alpha=0.24)
        place_item(box_closed, 595, 544, 325, refl_alpha=0.24)
        place_item(bottle,     858, 554, 272, refl_alpha=0.24)

    _real_prod_cache[mode] = layer
    return layer

# ======================================================================
# 4. FIVE DISTINCT, VARIED OVERLAY PRESENTATION STYLES (NO REPETITIVE BOX!)
# ======================================================================
_feather_mask_cache = {}
def get_soft_arch_mask(vw, vh, feather_bot=115, top_rad=0):
    k = (vw, vh, feather_bot, top_rad)
    if k not in _feather_mask_cache:
        yy = np.arange(vh, dtype=np.float32)[:, None]
        alpha = np.ones((vh, vw), dtype=np.float32)
        if feather_bot > 0:
            u = np.clip((vh - yy) / float(feather_bot), 0.0, 1.0)
            alpha *= u * u * (3.0 - 2.0 * u)
        m = Image.fromarray((alpha * 255.0).astype(np.uint8), "L")
        if top_rad > 0:
            rm = Image.new("L", (vw, vh), 0)
            ImageDraw.Draw(rm).rounded_rectangle([0, 0, vw - 1, vh + top_rad], radius=top_rad, fill=255)
            m = Image.fromarray(np.minimum(np.array(m), np.array(rm)), "L")
        _feather_mask_cache[k] = m
    return _feather_mask_cache[k]

def draw_soft_ambient_backdrop(canvas_im, bg_rgb, opacity=1.0, blur_rad=18, tint_rgba=(255, 246, 250, 92)):
    """Covers the distracting cropped orange/blue wall text cleanly on PIP & Brand Card scenes!"""
    if opacity <= 0.005:
        return
    vw, vh = 1080, 915
    im = fit_cover_subpixel(bg_rgb, vw, vh, zoom=1.04).filter(ImageFilter.GaussianBlur(radius=blur_rad)).convert("RGBA")
    if tint_rgba:
        im = Image.alpha_composite(im, Image.new("RGBA", (vw, vh), tint_rgba))
    mask = get_soft_arch_mask(vw, vh, feather_bot=125)
    arr = np.array(im)
    arr[:, :, 3] = (np.array(mask, dtype=np.float32) * clamp01(opacity)).astype(np.uint8)
    paste_subpixel(canvas_im, Image.fromarray(arr, "RGBA"), 540.0, 457.5, scale=1.0, opacity=1.0)

def style1_fullbleed_soft_cinema(canvas_im, vf_rgb, t, st, en, tag_txt=None, zoom_from=1.05, zoom_to=1.00, pan_y=0.0, real_prod_mode=None):
    """
    STYLE 1 (Hook 0..3.96s & Glossy White Probiotic Hydrogel Stage 30.84..41.55s):
    Seamless 1080px full-bleed upper cinema melting softly behind the speaker (ZERO box frame!).
    """
    env = smooth_env(t, st, en, d_in=0.45 if st > 0.2 else 0.10, d_out=0.45)
    if env <= 0.005:
        return
    u = quintic_smooth((t - st) / max(0.2, en - st))
    z = zoom_from + (zoom_to - zoom_from) * u
    vw, vh = 1080, 915
    crop = fit_cover_subpixel(vf_rgb, vw, vh, zoom=z, pan_y=pan_y).convert("RGBA")

    if real_prod_mode:
        prod_layer = get_real_product_overlay(real_prod_mode)
        paste_subpixel(crop, prod_layer, 540.0, 450.0, scale=0.97 + 0.045 * u, opacity=1.0)

    mask = get_soft_arch_mask(vw, vh, feather_bot=120, top_rad=0)
    arr = np.array(crop)
    arr[:, :, 3] = (np.array(mask, dtype=np.float32) * env).astype(np.uint8)
    glide_y = (1.0 - env) * (-22.0) if st > 0.2 else 0.0
    paste_subpixel(canvas_im, Image.fromarray(arr, "RGBA"), 540.0, 457.5 + glide_y, scale=1.0, opacity=1.0)
    if tag_txt:
        draw_minimal_glass_tag(canvas_im, tag_txt, 540.0, 58.0, accent_rgb=(238, 42, 82), opacity=env)

def style2_diagonal_wipe_dual_scene(canvas_im, amb_rgb, vf1_rgb, vf2_rgb, t, st, t_split, en):
    """
    STYLE 2 (3.98..10.75s — Exact Speaker in Office Discomfort -> Evening Worried Smartphone):
    Sleek thin-rimmed floating cinema frame with a smooth 103-degree feathered diagonal wipe at t_split!
    """
    env = smooth_env(t, st, en, d_in=0.48, d_out=0.42)
    if env <= 0.005:
        return
    draw_soft_ambient_backdrop(canvas_im, amb_rgb, opacity=env * 0.96, blur_rad=22, tint_rgba=(250, 246, 248, 95))

    vw, vh = 1024, 816
    u1 = quintic_smooth((t - st) / max(0.2, en - st))
    im1 = fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.01 + 0.045 * u1, pan_y=-0.02)

    if t <= t_split - 0.38:
        blended = np.array(im1)
    elif t >= t_split + 0.38:
        u2 = quintic_smooth((t - (t_split - 0.38)) / max(0.2, en - t_split + 0.38))
        im2 = fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.05 - 0.04 * u2, pan_y=-0.02)
        blended = np.array(im2)
    else:
        u_w = quintic_smooth((t - (t_split - 0.38)) / 0.76)
        u2 = quintic_smooth((t - (t_split - 0.38)) / max(0.2, en - t_split + 0.38))
        im2 = fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.05 - 0.04 * u2, pan_y=-0.02)
        yy, xx = np.ogrid[0:vh, 0:vw]
        proj = xx.astype(np.float32) + yy.astype(np.float32) * 0.23
        max_p = vw + vh * 0.23
        edge = -130.0 + (max_p + 260.0) * u_w
        w_mask = np.clip((edge - proj) / 120.0 + 0.5, 0.0, 1.0)
        w_mask = (w_mask * w_mask * (3.0 - 2.0 * w_mask))[:, :, None]
        blended = np.clip(np.array(im1, dtype=np.float32) * (1.0 - w_mask) + np.array(im2, dtype=np.float32) * w_mask, 0, 255).astype(np.uint8)

    rad = 38
    cw, ch = vw + 40, vh + 44
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 24, 20 + vw, 24 + vh], radius=rad, fill=(18, 20, 32, 88))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=13)))

    rmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=rad, fill=255)
    art = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    art.paste(Image.fromarray(blended, "RGB"), (20, 18), mask=rmask)
    card = Image.alpha_composite(card, art)
    ImageDraw.Draw(card).rounded_rectangle([20, 18, 20 + vw - 1, 18 + vh - 1], radius=rad, outline=(255, 244, 232, 220), width=2)

    glide_x = (1.0 - env) * (-36.0)
    paste_subpixel(canvas_im, card, 540.0 + glide_x, 452.0, scale=0.96 + 0.04 * env, opacity=env)
    lbl = "SINH HOẠT THIẾU THOẢI MÁI" if t < t_split else "LO LẮNG TÌNH TRẠNG NGHIÊM TRỌNG HƠN"
    draw_minimal_glass_tag(canvas_im, lbl, 540.0, 64.0, accent_rgb=(235, 85, 115), opacity=env)

def style3_glassmorphic_editorial_morph(canvas_im, amb_rgb, vf1_rgb, vf2_rgb, t, st, t_morph, en):
    """
    STYLE 3 (12.95..23.18s — 3D Epithelial Cells -> Doctor Reassuring Exact Speaker):
    Frosted glassmorphism outer bezel + optical cross-dissolve!
    """
    env = smooth_env(t, st, en, d_in=0.50, d_out=0.45)
    if env <= 0.005:
        return
    draw_soft_ambient_backdrop(canvas_im, amb_rgb, opacity=env * 0.96, blur_rad=22, tint_rgba=(242, 248, 252, 95))

    vw, vh = 984, 776
    pad_g = 20
    gw, gh = vw + pad_g * 2, vh + pad_g * 2

    u_all = quintic_smooth((t - st) / max(0.2, en - st))
    if t <= t_morph - 0.38:
        v_arr = np.array(fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.01 + 0.05 * u_all))
    elif t >= t_morph + 0.38:
        u2 = quintic_smooth((t - (t_morph - 0.38)) / max(0.2, en - t_morph + 0.38))
        v_arr = np.array(fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.04 - 0.035 * u2, pan_y=-0.02))
    else:
        um = quintic_smooth((t - (t_morph - 0.38)) / 0.76)
        a1 = np.array(fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.04 + 0.03 * um), dtype=np.float32)
        a2 = np.array(fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.05 - 0.02 * um, pan_y=-0.02), dtype=np.float32)
        v_arr = np.clip(a1 * (1.0 - um) + a2 * um, 0, 255).astype(np.uint8)

    cw, ch = gw + 40, gh + 40
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 24, 20 + gw, 24 + gh], radius=46, fill=(16, 24, 38, 82))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=13)))

    glass = Image.new("RGBA", (gw, gh), (255, 255, 255, 168))
    gmask = Image.new("L", (gw, gh), 0)
    ImageDraw.Draw(gmask).rounded_rectangle([0, 0, gw - 1, gh - 1], radius=46, fill=255)
    glayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    glayer.paste(glass, (20, 20), mask=gmask)
    card = Image.alpha_composite(card, glayer)
    ImageDraw.Draw(card).rounded_rectangle([20, 20, 20 + gw - 1, 20 + gh - 1], radius=46, outline=(255, 255, 255, 238), width=2)

    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=32, fill=255)
    vlayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vlayer.paste(Image.fromarray(v_arr, "RGB"), (20 + pad_g, 20 + pad_g), mask=vmask)
    card = Image.alpha_composite(card, vlayer)

    float_y = math.sin((t - st) * 1.3) * 3.5
    paste_subpixel(canvas_im, card, 540.0, 452.0 + (1.0 - env) * 24.0 + float_y, scale=0.96 + 0.04 * env, opacity=env)
    lbl = "TẾ BÀO TUYẾN HIỆN DIỆN MẶT NGOÀI" if t < t_morph else "KHÔNG ĐỒNG NGHĨA NHIỄM TRÙNG / UNG THƯ"
    draw_minimal_glass_tag(canvas_im, lbl, 540.0, 72.0, accent_rgb=(56, 168, 235), opacity=env)

def style4_staggered_dual_pip(canvas_im, amb_rgb, vf_left_rgb, vf_right_rgb, t, st1, st2, en):
    """
    STYLE 4 (23.20..30.82s — Doctor Consultation + Optical Lab Microscope):
    Editorial 2-Panel Asymmetric Staggered Collage over clean frosted clinic mist (0% wall text bleed!).
    """
    env_all = smooth_env(t, st1, en, d_in=0.45, d_out=0.42)
    if env_all <= 0.005:
        return
    draw_soft_ambient_backdrop(canvas_im, amb_rgb, opacity=env_all, blur_rad=24, tint_rgba=(240, 248, 250, 125))

    env_out = quintic_smooth((en - t) / 0.42) if (en - t) < 0.42 else 1.0

    def make_pip(v_rgb, pw, ph, zoom_v):
        im = fit_cover_subpixel(v_rgb, pw, ph, zoom=zoom_v)
        cw, ch = pw + 36, ph + 36
        c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([18, 22, 18 + pw, 22 + ph], radius=30, fill=(14, 22, 34, 96))
        c = Image.alpha_composite(c, sh.filter(ImageFilter.GaussianBlur(radius=11)))
        rm = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=30, fill=255)
        al = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        al.paste(im, (18, 16), mask=rm)
        c = Image.alpha_composite(c, al)
        ImageDraw.Draw(c).rounded_rectangle([18, 16, 18 + pw - 1, 16 + ph - 1], radius=30, outline=(255, 255, 255, 235), width=3)
        return c

    u1 = ease_out_quart(min(1.0, (t - st1) / 0.55))
    z1 = 1.02 + 0.045 * quintic_smooth((t - st1) / max(0.2, en - st1))
    p1 = make_pip(vf_left_rgb, 690, 470, z1)
    u2_shift = quintic_smooth((t - st2) / 0.55) if t >= st2 else 0.0
    cx1 = 448.0 - 70.0 * u2_shift - (1.0 - u1) * 48.0
    cy1 = 330.0 - 20.0 * u2_shift
    paste_subpixel(canvas_im, p1, cx1, cy1, scale=0.93 + 0.07 * u1, opacity=u1 * env_out)

    if t >= st2:
        u2 = ease_out_quart(min(1.0, (t - st2) / 0.55))
        z2 = 1.05 - 0.04 * quintic_smooth((t - st2) / max(0.2, en - st2))
        p2 = make_pip(vf_right_rgb, 620, 435, z2)
        cx2 = 712.0 + (1.0 - u2) * 52.0
        cy2 = 625.0 + (1.0 - u2) * 26.0
        paste_subpixel(canvas_im, p2, cx2, cy2, scale=0.91 + 0.09 * u2, opacity=u2 * env_out)

    lbl = "BÁC SĨ ĐÁNH GIÁ NGUYÊN NHÂN" if t < st2 else "LOẠI TRỪ NHIỄM TRÙNG & BẤT THƯỜNG"
    draw_minimal_glass_tag(canvas_im, lbl, 540.0, 58.0, accent_rgb=(42, 185, 148), opacity=min(u1, env_out))

def style5_luxury_silk_showcase(canvas_im, vf_stage_rgb, t, st, en):
    """
    STYLE 5 (45.88..50.16s — Living Sunlit Blush Silk Stage + Real 4K RGBA LT PLUS Trio!):
    Panoramic arched luxury showcase with champagne-gold hairline & sweeping optical light sheen!
    """
    env = smooth_env(t, st, en, d_in=0.45, d_out=0.40)
    if env <= 0.005:
        return
    draw_soft_ambient_backdrop(canvas_im, vf_stage_rgb, opacity=env, blur_rad=20, tint_rgba=(255, 238, 245, 75))

    vw, vh = 1036, 845
    u = quintic_smooth((t - st) / max(0.2, en - st))
    im = fit_cover_subpixel(vf_stage_rgb, vw, vh, zoom=1.00 + 0.045 * u).convert("RGBA")

    # Composite the 100% REAL 4K RGBA Open Magnetic Box + Closed Box + Bottle onto the living silk stage!
    prod_layer = get_real_product_overlay("luxury")
    paste_subpixel(im, prod_layer, vw * 0.5, 442.0, scale=0.95 + 0.045 * u, opacity=1.0)

    # Subtle diagonal golden light-sheen sweep across the luxury showcase
    yy, xx = np.ogrid[0:vh, 0:vw]
    diag = (xx.astype(np.float32) * 0.8 + yy.astype(np.float32) * 0.45) / (vw * 0.8 + vh * 0.45)
    sweep_pos = -0.25 + 1.50 * quintic_smooth(min(1.0, (t - st) / 2.6))
    sheen = np.exp(-((diag - sweep_pos) ** 2) / 0.008) * 34.0
    arr = np.array(im, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + sheen * 1.1, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + sheen * 0.95, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + sheen * 0.85, 0, 255)

    cw, ch = vw + 36, vh + 40
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 22, 18 + vw, 22 + vh], radius=44, fill=(55, 22, 36, 84))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    rm = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=44, fill=255)
    al = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    al.paste(Image.fromarray(arr.astype(np.uint8), "RGBA"), (18, 16), mask=rm)
    card = Image.alpha_composite(card, al)
    ImageDraw.Draw(card).rounded_rectangle([18, 16, 18 + vw - 1, 16 + vh - 1], radius=44, outline=(*BRAND_GOLD, 238), width=3)

    paste_subpixel(canvas_im, card, 540.0, 452.0 + (1.0 - env) * (-22.0), scale=0.96 + 0.04 * env, opacity=env)
    draw_minimal_glass_tag(canvas_im, "VIÊN ĐẶT LT PLUS NHÀ HẰNG THU CHÍNH HÃNG", 540.0, 58.0, accent_rgb=(228, 32, 68), opacity=env)

# ======================================================================
# 5. SHIMMERING IRIDESCENT PEARL BUBBLES FOR 6 HERBS (IMAGE 5 UPGRADE!)
# ======================================================================
_bubble_cache = {}
def get_iridescent_bubble_sprite(label, diam, tint_rgb):
    key = (label, diam, tint_rgb)
    if key in _bubble_cache:
        return _bubble_cache[key]

    S = diam + 36
    c = S * 0.5
    r = diam * 0.5
    yy, xx = np.ogrid[0:S, 0:S]
    dx = (xx.astype(np.float32) - c) / r
    dy = (yy.astype(np.float32) - c) / r
    dist2 = dx * dx + dy * dy
    inside = dist2 <= 1.0
    dist = np.sqrt(np.maximum(0.0, dist2))

    rim = np.power(np.clip(dist, 0.0, 1.0), 2.5)
    caustic_bot = np.clip(dy * 0.65 + 0.35, 0.0, 1.0) * np.exp(-((dist - 0.82) ** 2) / 0.035)
    spec_top = np.exp(-(((dx + 0.34) ** 2 + (dy + 0.38) ** 2) / 0.045))
    spec_pin = np.exp(-(((dx + 0.44) ** 2 + (dy + 0.46) ** 2) / 0.008))

    rgba = np.zeros((S, S, 4), dtype=np.float32)
    rgba[:, :, 0] = 250 * (1.0 - rim * 0.36) + tint_rgb[0] * (rim * 0.36) + 45 * caustic_bot + 90 * spec_top
    rgba[:, :, 1] = 246 * (1.0 - rim * 0.36) + tint_rgb[1] * (rim * 0.36) + 38 * caustic_bot + 90 * spec_top
    rgba[:, :, 2] = 253 * (1.0 - rim * 0.36) + tint_rgb[2] * (rim * 0.36) + 42 * caustic_bot + 90 * spec_top

    alpha = (0.38 + 0.54 * rim + 0.30 * caustic_bot + 0.52 * spec_top + 0.65 * spec_pin) * 255.0
    edge_aa = np.clip((1.0 - dist) * r * 0.85, 0.0, 1.0)
    rgba[:, :, 3] = np.where(inside, np.clip(alpha, 0, 248) * edge_aa, 0.0)

    bim = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")

    aura = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(aura).ellipse([int(c - r), int(c - r), int(c + r), int(c + r)], outline=(*tint_rgb, 145), width=4)
    bim = Image.alpha_composite(aura.filter(ImageFilter.GaussianBlur(radius=5)), bim)

    # Snug, tightly centered botanical name inside the pearl bubble!
    lines = label.split("\n")
    fsz = 25 if len(lines) == 1 else 23
    line_sps = [
        render_pro_text_sprite(ln, FONT_SANS_XBOLD, fsz, (142, 12, 38), (96, 6, 24), stroke_col=(255, 255, 255), stroke_w=5, shadow_alpha=40)
        for ln in lines
    ]
    if len(line_sps) == 1:
        paste_subpixel(bim, line_sps[0], c, c, scale=1.0, opacity=1.0)
    else:
        paste_subpixel(bim, line_sps[0], c, c - 15.0, scale=1.0, opacity=1.0)
        paste_subpixel(bim, line_sps[1], c, c + 15.0, scale=1.0, opacity=1.0)

    _bubble_cache[key] = bim
    return bim

def draw_shimmering_herb_bubbles(canvas_im, t_now):
    t_end = 41.48
    if t_now < 33.60 or t_now >= t_end:
        return

    out_fade = quintic_smooth((t_end - t_now) / 0.48) if (t_end - t_now) < 0.48 else 1.0
    bubbles = [
        (33.66, "Hoàng Bá",      162, (255, 196, 125), 148.0, 255.0, 0.0),
        (34.68, "Ích Mẫu",       158, (255, 158, 192), 932.0, 255.0, 1.1),
        (35.12, "Kim Ngân\nHoa", 168, (255, 212, 138), 138.0, 490.0, 2.2),
        (36.16, "Trà Xanh",      158, (142, 236, 188), 942.0, 490.0, 3.3),
        (37.00, "Trầu Không",    164, (135, 228, 212), 182.0, 725.0, 4.4),
        (37.70, "Acid\nLactic",  162, (152, 208, 255), 898.0, 725.0, 5.5),
    ]

    micro_layer = Image.new("RGBA", (W, 920), (0, 0, 0, 0))
    md = ImageDraw.Draw(micro_layer)
    for mi in range(14):
        phase = (t_now * (0.26 + (mi % 4) * 0.06) + mi * 0.37) % 1.0
        mx = 95.0 + (mi * 71.0) % 890.0 + math.sin(t_now * 1.8 + mi) * 14.0
        my = 840.0 - phase * 740.0
        mr = 5 + (mi % 4) * 3
        ma = int(155 * math.sin(phase * math.pi) * out_fade)
        if ma > 8:
            md.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 250, 253, ma), outline=(255, 255, 255, min(255, ma + 40)))
    canvas_im.alpha_composite(micro_layer, dest=(0, 0))

    for st_b, lbl, diam, tint, tx, ty, seed in bubbles:
        if t_now < st_b:
            continue
        dt = t_now - st_b
        u_rise = ease_out_quart(min(1.0, dt / 0.85))
        op = quintic_smooth(min(1.0, dt / 0.32)) * out_fade
        bx = tx + math.sin(dt * 1.65 + seed) * 8.5
        by = ty + (1.0 - u_rise) * 135.0 + math.cos(dt * 1.35 + seed) * 7.0
        sc = (0.55 + 0.45 * u_rise) * (1.0 + 0.025 * math.sin(dt * 2.4 + seed))
        bsp = get_iridescent_bubble_sprite(lbl, diam, tint)
        paste_subpixel(canvas_im, bsp, bx, by, scale=sc, opacity=op)

# ======================================================================
# 6. AUTHENTIC LT PLUS HẰNG THU BRAND HEADER CARD (IMAGE 7 EXACT MATCH!)
# ======================================================================
_brand_card_cache = {}
def get_authentic_brand_card(mode_key, title_top, main_line, sub_line):
    if mode_key in _brand_card_cache:
        return _brand_card_cache[mode_key]

    pw, ph = 976, 262
    cw, ch = pw + 44, ph + 44
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([22, 26, 22 + pw, 26 + ph], radius=48, fill=(58, 18, 32, 85))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, pw, dtype=np.float32)[None, :]
    center_lift = np.exp(-(xx * xx * 1.4 + (yy - 0.35) ** 2 * 2.2))
    bg = np.zeros((ph, pw, 3), dtype=np.uint8)
    bg[:, :, 0] = np.clip(BRAND_PINK_BG2[0] + 7 * center_lift, 0, 255).astype(np.uint8)
    bg[:, :, 1] = np.clip(BRAND_PINK_BG2[1] + 28 * center_lift, 0, 255).astype(np.uint8)
    bg[:, :, 2] = np.clip(BRAND_PINK_BG2[2] + 18 * center_lift, 0, 255).astype(np.uint8)
    bg_im = Image.fromarray(bg, "RGB").convert("RGBA")

    rib = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rib)
    rd.line([(-20, 35), (210, ph + 20)], fill=(235, 172, 118, 145), width=4)
    rd.line([(25, 0), (265, ph + 20)], fill=(255, 240, 220, 160), width=2)
    rd.line([(pw + 20, 35), (pw - 210, ph + 20)], fill=(235, 172, 118, 145), width=4)
    rd.line([(pw - 25, 0), (pw - 265, ph + 20)], fill=(255, 240, 220, 160), width=2)
    bg_im = Image.alpha_composite(bg_im, rib)

    rmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=46, fill=255)
    blayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    blayer.paste(bg_im, (22, 20), mask=rmask)
    card = Image.alpha_composite(card, blayer)
    ImageDraw.Draw(card).rounded_rectangle([22, 20, 22 + pw - 1, 20 + ph - 1], radius=46, outline=(255, 255, 255, 248), width=4)
    ImageDraw.Draw(card).rounded_rectangle([26, 24, 18 + pw, 16 + ph], radius=42, outline=(*BRAND_GOLD, 205), width=2)

    sp_top = render_pro_text_sprite(title_top, FONT_BRAND_SERIF, 25, (38, 14, 20), stroke_w=0, shadow_alpha=0)
    sp_mid = render_pro_text_sprite(main_line, FONT_BRAND_SERIF, 86, BRAND_RED_TOP, BRAND_RED_BOT, stroke_col=(255, 245, 248), stroke_w=3, shadow_alpha=35, extrude_col=BRAND_EXTRUDE)
    sp_bot = render_pro_text_sprite(sub_line,  FONT_BRAND_SERIF, 36, (212, 6, 16), (182, 0, 10), stroke_w=0, shadow_alpha=0, extrude_col=(65, 8, 14))

    paste_subpixel(card, sp_top, cw * 0.5, 20 + 42,  scale=1.0, opacity=1.0)
    paste_subpixel(card, sp_mid, cw * 0.5, 20 + 122, scale=1.0, opacity=1.0)
    ImageDraw.Draw(card).line([(cw // 2 - 230, 20 + 178), (cw // 2 + 230, 20 + 178)], fill=(215, 28, 48, 175), width=2)
    paste_subpixel(card, sp_bot, cw * 0.5, 20 + 216, scale=1.0, opacity=1.0)

    _brand_card_cache[mode_key] = card
    return card

# ======================================================================
# 7. SMOOTH CAMERA CURVE & WORD-BY-WORD CAPTIONS
# ======================================================================
ZOOM_KEYS = [
    (0.00, 1.010),
    (3.98, 1.042),
    (10.80, 1.018),
    (13.00, 1.048),
    (17.05, 1.025),
    (23.22, 1.052),
    (30.84, 1.022),
    (33.68, 1.048),
    (41.62, 1.018),
    (45.92, 1.048),
    (50.18, 1.022),
    (53.96, 1.046),
    (59.18, 1.015),
]

def get_butter_zoom(t):
    if t <= ZOOM_KEYS[0][0]:
        return ZOOM_KEYS[0][1]
    for i in range(1, len(ZOOM_KEYS)):
        t0, z0 = ZOOM_KEYS[i - 1]
        t1, z1 = ZOOM_KEYS[i]
        if t <= t1:
            u = quintic_smooth(min(1.0, (t - t0) / min(0.95, max(0.35, (t1 - t0) * 0.45))))
            return z0 + (z1 - z0) * u
    return ZOOM_KEYS[-1][1]

def load_captions_v2():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if (w["start"] + w["end"]) * 0.5 >= 3.85
    ]

    groups, cur, line = [], [], []
    def flush_line():
        nonlocal line
        if line:
            cur.append(line); line = []
    def flush_group():
        nonlocal cur
        flush_line()
        if cur:
            groups.append(cur); cur = []

    prev = None
    for w in words:
        txt = w["word"].strip()
        if not txt:
            continue
        if prev is not None and (w["start"] - prev["end"]) >= 0.34:
            flush_group()
        if line and (len(line) >= 3 or sum(len(x[0]) + 1 for x in line) + len(txt) > 15):
            flush_line()
        if len(cur) >= 2 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!…:;]$", txt):
            flush_group()
    flush_group()

    BRAND_WORDS = {"LT", "PLUS", "LT PLUS", "Hằng", "Thu,"}
    GOLD_WORDS = {
        "hiểu", "đúng,", "đúng", "tế", "bào", "tuyến", "bác", "sĩ", "nguyên", "nhân,",
        "Hoàng", "Bá,", "Ích", "Mẫu,", "Kim", "Ngân", "Hoa,",
        "Trà", "Xanh,", "Trầu", "Không", "Acid", "Lactic.", "hiệu", "quả", "kỹ"
    }
    ROSE_WORDS = {
        "Khí", "hư", "không", "phải", "ung", "thư.", "phiền", "toái,",
        "hỗ", "trợ", "phụ", "khoa,", "Nhắn"
    }

    cap_groups = []
    for i, g in enumerate(groups):
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else 59.05
        t1 = min(nxt, last_end + 0.45) if (nxt - last_end) > 0.55 else nxt
        cap_groups.append({"t0": g[0][0][1], "t1": t1, "lines": g})
    return cap_groups, BRAND_WORDS, GOLD_WORDS, ROSE_WORDS

class VideoReader:
    def __init__(self, path):
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE
        )
    def read(self):
        buf = self.proc.stdout.read(W * H * 3)
        return None if len(buf) < W * H * 3 else np.frombuffer(buf, dtype=np.uint8).reshape((H, W, 3))
    def close(self):
        self.proc.stdout.close()
        self.proc.wait()

def load_vid_frames_wh(path, vw, vh):
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={vw}:{vh}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE
    )
    frames = []
    nbytes = vw * vh * 3
    while True:
        b = proc.stdout.read(nbytes)
        if len(b) < nbytes:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)))
    proc.stdout.close()
    proc.wait()
    return frames

def get_clip_frame(clips, key, t_rel):
    arr_list = clips.get(key)
    if not arr_list:
        return np.full((720, 1280, 3), 245, dtype=np.uint8)
    n = len(arr_list)
    idx_raw = int(max(0.0, t_rel) * FPS)
    cycle = 2 * (n - 1) if n > 2 else 1
    pos = idx_raw % cycle
    idx = pos if pos < n else cycle - pos
    return arr_list[min(n - 1, max(0, idx))]

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [1.60, 5.50, 8.80, 15.20, 19.80, 28.20, 38.20, 48.00, 55.20]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vkeys = [
        "v2_hook", "v2_discomfort1", "v2_discomfort2",
        "v2_med_cells", "v2_reassure",
        "v2_doctor_eval", "v2_lab_micro",
        "v2_stage_hydrogel", "v2_stage_luxury"
    ]
    clips = {}
    for vk in vkeys:
        vp = os.path.join(MEDIA_DIR, f"{vk}.mp4")
        if os.path.exists(vp):
            clips[vk] = load_vid_frames_wh(vp, 1280, 720)
            print(f"Loaded {vk}: {len(clips[vk])} frames")
        else:
            print(f"WARNING missing {vp}")

    cap_groups, BRAND_WORDS, GOLD_WORDS, ROSE_WORDS = load_captions_v2()

    legal_sp = render_pro_text_sprite(
        "Sản phẩm chăm sóc phụ khoa • Đọc kỹ hướng dẫn sử dụng trước khi dùng",
        FONT_SUB, 20, (250, 248, 250), stroke_col=(28, 18, 28), stroke_w=3, shadow_alpha=0
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_htpm_lt_v2_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    yy_g, xx_g = np.ogrid[0:H, 0:W]
    desk_mask   = np.clip((yy_g.astype(np.float32) - 1455.0) / 55.0, 0.0, 1.0)
    plant_mask  = np.clip((225.0 - xx_g.astype(np.float32)) / 65.0, 0.0, 1.0) * np.clip((yy_g.astype(np.float32) - 960.0) / 80.0, 0.0, 1.0)
    box_protect = np.clip((xx_g.astype(np.float32) - 540.0) / 60.0, 0.0, 1.0) * np.clip((yy_g.astype(np.float32) - 1215.0) / 55.0, 0.0, 1.0)
    static_fg_guard = np.maximum(desk_mask, np.maximum(plant_mask * 0.92, box_protect))

    frame_idx = 0
    while True:
        rgb_raw = reader_a.read()
        mbuf = reader_m.stdout.read(W * H)
        if rgb_raw is None or len(mbuf) < W * H:
            break
        if test_mode and frame_idx not in test_frames:
            frame_idx += 1
            if frame_idx > max(test_frames):
                break
            continue

        rgb = polish_bright_frame(rgb_raw)
        matte = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W)).astype(np.float32) / 255.0
        t = frame_idx / FPS

        # 1. Subpixel-Smooth Camera Zoom on A-Roll!
        z = get_butter_zoom(t)
        if z > 1.002:
            fg_im = fit_cover_subpixel(rgb, W, H, zoom=z, pan_y=-0.04 * (z - 1.0))
            m_rgb = np.repeat((matte * 255.0).astype(np.uint8)[:, :, None], 3, axis=2)
            m_im  = fit_cover_subpixel(m_rgb, W, H, zoom=z, pan_y=-0.04 * (z - 1.0)).convert("L")
            fg_rgb = np.array(fg_im)
            m_arr  = np.array(m_im, dtype=np.float32) / 255.0
        else:
            fg_im = Image.fromarray(rgb, "RGB")
            fg_rgb = rgb
            m_arr = matte

        comp_im = fg_im.convert("RGBA")
        need_fg_recomp = False

        # ==================================================================
        # 2. MULTI-STYLE CONTEXTUAL VIDEO OVERLAYS BEHIND SPEAKER
        # ==================================================================
        if 0.00 <= t <= 3.96:
            # STYLE 1: Seamless Full-Bleed Soft Cinema Hook (Exact Speaker Holding Checkup Report!)
            vf = get_clip_frame(clips, "v2_hook", t)
            style1_fullbleed_soft_cinema(comp_im, vf, t, 0.00, 3.96, tag_txt="TÂM LÝ KHI NGHE KẾT LUẬN LỘ TUYẾN", zoom_from=1.05, zoom_to=1.00, pan_y=-0.02)
            need_fg_recomp = True

        elif 3.98 <= t <= 10.75:
            # STYLE 2: Diagonal Wipe Dual-Scene (Exact Speaker Office Discomfort -> Evening Worried Smartphone)
            vf1 = get_clip_frame(clips, "v2_discomfort1", t - 3.98)
            vf2 = get_clip_frame(clips, "v2_discomfort2", max(0.0, t - 6.80))
            style2_diagonal_wipe_dual_scene(comp_im, vf1, vf1, vf2, t, 3.98, 7.15, 10.75)
            need_fg_recomp = True

        elif 10.76 <= t <= 12.94:
            # Editorial Bridge Card #1 over soft sunlit studio mist
            env_b1 = smooth_env(t, 10.76, 12.94, d_in=0.35, d_out=0.32)
            if env_b1 > 0.01:
                amb = get_clip_frame(clips, "v2_stage_hydrogel", t - 10.76)
                draw_soft_ambient_backdrop(comp_im, amb, opacity=env_b1, blur_rad=20, tint_rgba=(255, 246, 250, 95))
                bcard = get_authentic_brand_card("bridge1", "TƯ VẤN CHUYÊN KHOA", "HIỂU ĐÚNG", "ĐỂ KHÔNG HOANG MANG")
                paste_subpixel(comp_im, bcard, 540.0, 445.0 + (1.0 - env_b1) * (-22.0), scale=0.94 + 0.06 * env_b1, opacity=env_b1)
                need_fg_recomp = True

        elif 12.95 <= t <= 23.18:
            # STYLE 3: Frosted Glassmorphism Frame + Optical Morph (3D Epithelial Cells -> Doctor Reassuring Exact Speaker)
            vf1 = get_clip_frame(clips, "v2_med_cells", t - 12.95)
            vf2 = get_clip_frame(clips, "v2_reassure", max(0.0, t - 16.70))
            amb = vf1 if t < 17.05 else vf2
            style3_glassmorphic_editorial_morph(comp_im, amb, vf1, vf2, t, 12.95, 17.05, 23.18)
            need_fg_recomp = True

        elif 23.20 <= t <= 30.82:
            # STYLE 4: Staggered Dual-Panel Split Collage (Doctor Evaluation + Optical Lab Microscope)
            vf_doc = get_clip_frame(clips, "v2_reassure" if "v2_doctor_eval" not in clips else "v2_doctor_eval", t - 23.20)
            vf_lab = get_clip_frame(clips, "v2_lab_micro", max(0.0, t - 26.75))
            style4_staggered_dual_pip(comp_im, vf_doc, vf_doc, vf_lab, t, 23.20, 26.75, 30.82)
            need_fg_recomp = True

        elif 30.84 <= t <= 41.55:
            # STYLE 1B: Living Glossy White Probiotic Cream Stage + Real 4K RGBA LT PLUS Box & Bottle!
            vf = get_clip_frame(clips, "v2_stage_hydrogel", t - 30.84)
            style1_fullbleed_soft_cinema(
                comp_im, vf, t, 30.84, 41.55,
                tag_txt="VIÊN ĐẶT PHỤ KHOA LT PLUS HẰNG THU",
                zoom_from=1.00, zoom_to=1.045, real_prod_mode="hydrogel"
            )
            need_fg_recomp = True

        elif 41.60 <= t <= 45.86:
            # Editorial Bridge Card #2 over soft sunlit silk mist
            env_b2 = smooth_env(t, 41.60, 45.86, d_in=0.38, d_out=0.35)
            if env_b2 > 0.01:
                amb = get_clip_frame(clips, "v2_stage_luxury", t - 41.60)
                draw_soft_ambient_backdrop(comp_im, amb, opacity=env_b2, blur_rad=18, tint_rgba=(255, 240, 246, 85))
                bcard = get_authentic_brand_card("bridge2", "CHĂM SÓC ĐÚNG CÁCH", "LT PLUS", "HỖ TRỢ HIỆU QUẢ & AN TÂM")
                paste_subpixel(comp_im, bcard, 540.0, 445.0 + (1.0 - env_b2) * (-22.0), scale=0.94 + 0.06 * env_b2, opacity=env_b2)
                need_fg_recomp = True

        elif 45.88 <= t <= 50.16:
            # STYLE 5: Living Sunlit Blush Silk Stage + Real 4K RGBA Open Magnetic Box, Box & Bottle!
            vf = get_clip_frame(clips, "v2_stage_luxury", t - 45.88)
            style5_luxury_silk_showcase(comp_im, vf, t, 45.88, 50.16)
            need_fg_recomp = True

        elif 50.20 <= t <= 59.17:
            # Authentic Packaging-Matched LT PLUS HẰNG THU Brand Finale Header over soft sunlit silk mist!
            env_fin = smooth_env(t, 50.20, 59.17, d_in=0.45, d_out=0.25)
            if env_fin > 0.01:
                amb = get_clip_frame(clips, "v2_stage_luxury", t - 50.20)
                draw_soft_ambient_backdrop(comp_im, amb, opacity=env_fin, blur_rad=18, tint_rgba=(255, 238, 246, 82))
                bcard = get_authentic_brand_card("finale", "VIÊN ĐẶT PHỤ KHOA", "LT PLUS", "HẰNG THU  •  NHẮN TIN TƯ VẤN NGAY")
                paste_subpixel(comp_im, bcard, 540.0, 445.0 + (1.0 - env_fin) * (-24.0), scale=0.94 + 0.06 * env_fin, opacity=env_fin)
                need_fg_recomp = True

        # Composite real RVM Pharmacist + Desk + Left Plant + Held Pink LT PLUS Box cleanly in FRONT!
        if need_fg_recomp:
            fg_alpha = np.maximum(m_arr, static_fg_guard)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 3. 6 Shimmering Iridescent Crystal-Pearl Herb Bubbles rising around LT PLUS (33.65 - 41.48s)
        draw_shimmering_herb_bubbles(comp_im, t)

        # 4. Refined Editorial Hook Typography on Dark Blouse (0.08 - 3.80s, 100% Moderation-Safe!)
        env_hk = smooth_env(t, 0.08, 3.80, d_in=0.25, d_out=0.30)
        if env_hk > 0.01:
            if t >= 0.08:
                u1 = ease_out_quart(min(1.0, (t - 0.08) / 0.42))
                sp1 = render_pro_text_sprite("Nghe kết luận lộ tuyến...", FONT_SANS_BOLD, 42, (255, 255, 255), (235, 242, 255), stroke_col=(18, 28, 48), stroke_w=6)
                paste_subpixel(comp_im, sp1, 505.0, 1108.0 + (1.0 - u1) * 20.0, scale=0.94 + 0.06 * u1, opacity=env_hk * u1)
            if t >= 1.10:
                u2 = ease_out_quart(min(1.0, (t - 1.10) / 0.45))
                sp2 = render_pro_text_sprite("LO LẮNG", FONT_SANS_XBOLD, 70, (255, 218, 128), (242, 178, 72), stroke_col=(24, 18, 32), stroke_w=7, glow_col=(255, 198, 92), glow_rad=8)
                paste_subpixel(comp_im, sp2, 295.0, 1208.0 + (1.0 - u2) * 22.0, scale=0.93 + 0.07 * u2, opacity=env_hk * u2)
            if t >= 1.50:
                u3 = ease_out_quart(min(1.0, (t - 1.50) / 0.45))
                sp3 = render_pro_text_sprite("bắt đầu từ đâu?", FONT_EDIT_ITALIC, 58, (255, 182, 208), (248, 138, 175), stroke_col=(24, 18, 32), stroke_w=6)
                paste_subpixel(comp_im, sp3, 725.0, 1210.0 + (1.0 - u3) * 22.0, scale=0.93 + 0.07 * u3, opacity=env_hk * u3)
            if t >= 2.30:
                u4 = ease_out_quart(min(1.0, (t - 2.30) / 0.42))
                sp4 = render_pro_text_sprite("Cùng Dược sĩ hiểu đúng trước tiên", FONT_SANS_BOLD, 34, (158, 248, 224), (118, 228, 198), stroke_col=(14, 24, 34), stroke_w=5)
                paste_subpixel(comp_im, sp4, 495.0, 1304.0 + (1.0 - u4) * 16.0, scale=0.95 + 0.05 * u4, opacity=env_hk * u4)

        # 5. Word-by-Word Glowing Chest Captions (Exact Brand Red Serif on "LT PLUS"!)
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                op_g = quintic_smooth((g["t1"] - t) / 0.22) if (g["t1"] - t) < 0.22 else 1.0
                x_center = 485.0
                cap_sz_base = 62.0
                y_base = 1118.0 if len(g["lines"]) >= 2 else 1146.0
                lh = 64.0
                gap = 16.0
                for li, ln in enumerate(g["lines"]):
                    word_renders = []
                    total_w = 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_brand = wtxt in BRAND_WORDS
                        is_gold  = wtxt in GOLD_WORDS
                        is_rose  = wtxt in ROSE_WORDS
                        if is_brand:
                            f_use = FONT_BRAND_SERIF
                            sz_use = cap_sz_base * 1.14
                            sp = render_pro_text_sprite(
                                wtxt, f_use, sz_use,
                                BRAND_RED_TOP, BRAND_RED_BOT,
                                stroke_col=(255, 248, 244), stroke_w=6,
                                glow_col=(255, 195, 210), glow_rad=8, shadow_alpha=95
                            )
                        else:
                            f_use = FONT_CAP
                            k = 1.14 if (is_gold or is_rose) else 1.0
                            sz_use = cap_sz_base * k
                            col = (255, 228, 102) if is_gold else ((255, 162, 196) if is_rose else (238, 252, 248))
                            sp = render_pro_text_sprite(
                                wtxt, f_use, sz_use,
                                col, stroke_col=(14, 20, 34), stroke_w=5,
                                glow_col=col, glow_rad=7, shadow_alpha=88
                            )
                        adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(f_use, sz_use))
                        word_renders.append((wtxt, ws, sp, adv, is_brand))
                        total_w += adv + (gap if wi > 0 else 0.0)

                    cur_x = max(54.0, min(1018.0 - total_w, x_center - total_w * 0.5))
                    cur_y = y_base + li * lh
                    for wtxt, ws, sp, adv, is_brand in word_renders:
                        if t >= ws:
                            dt_w = t - ws
                            u_w = ease_out_quart(min(1.0, dt_w / 0.26))
                            wy = cur_y + (1.0 - u_w) * 16.0
                            blur_w = (1.0 - u_w) * 4.0
                            wcx = cur_x + adv * 0.5
                            paste_subpixel(
                                comp_im, sp, wcx, wy,
                                scale=0.94 + 0.06 * u_w,
                                opacity=op_g * quintic_smooth(min(1.0, dt_w / 0.11)),
                                blur_px=blur_w
                            )
                        cur_x += adv + gap
                break

        # 6. Authentic Brand-Matched Bottom CTA Pill (53.95 - 59.05s)
        env_end = smooth_env(t, 53.95, 59.05, d_in=0.38, d_out=0.32)
        if env_end > 0.01:
            cta_w, cta_h = 760, 68
            cta_card = Image.new("RGBA", (cta_w + 24, cta_h + 24), (0, 0, 0, 0))
            cd = ImageDraw.Draw(cta_card)
            cd.rounded_rectangle([12, 14, 12 + cta_w, 14 + cta_h], radius=34, fill=(48, 12, 24, 90))
            cta_card = cta_card.filter(ImageFilter.GaussianBlur(radius=6))
            cd = ImageDraw.Draw(cta_card)
            cd.rounded_rectangle([12, 10, 12 + cta_w, 10 + cta_h], radius=34, fill=(*BRAND_PINK_BG1, 250), outline=(255, 255, 255, 245), width=3)
            sp_c1 = render_pro_text_sprite("Nhắn ", FONT_SANS_BOLD, 30, (48, 18, 28), stroke_w=0, shadow_alpha=0)
            sp_c2 = render_pro_text_sprite("LT PLUS", FONT_BRAND_SERIF, 36, BRAND_RED_TOP, BRAND_RED_BOT, stroke_col=(255, 255, 255), stroke_w=2, shadow_alpha=0, extrude_col=BRAND_EXTRUDE)
            sp_c3 = render_pro_text_sprite(" nhận thông tin chi tiết", FONT_SANS_BOLD, 30, (48, 18, 28), stroke_w=0, shadow_alpha=0)
            w1, w2, w3 = sp_c1.width - 56, sp_c2.width - 56, sp_c3.width - 56
            tot_cw = w1 + w2 + w3
            sx0 = 12 + (cta_w - tot_cw) * 0.5
            paste_subpixel(cta_card, sp_c1, sx0 + w1 * 0.5,            10 + cta_h * 0.5, scale=1.0)
            paste_subpixel(cta_card, sp_c2, sx0 + w1 + w2 * 0.5,       10 + cta_h * 0.5 - 1, scale=1.0)
            paste_subpixel(cta_card, sp_c3, sx0 + w1 + w2 + w3 * 0.5,  10 + cta_h * 0.5, scale=1.0)
            paste_subpixel(comp_im, cta_card, 540.0, 1732.0 + (1.0 - env_end) * 14.0, scale=0.95 + 0.05 * env_end, opacity=env_end)

        # 7. Subtle Legal Disclaimer Bar at Bottom
        bar_bot = Image.new("RGBA", (W, 46), (26, 16, 24, 148))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 46))
        paste_subpixel(comp_im, legal_sp, 540.0, H - 23.0, scale=1.0, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"v2_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/1775 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close()
        writer.wait()
    reader_a.close()
    reader_m.stdout.close()
    reader_m.wait()

    if test_mode and test_saved:
        imgs = [Image.open(p).resize((360, 640), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (360 * 3, 640 * 3))
        for i, im in enumerate(imgs[:9]):
            grid.paste(im, ((i % 3) * 360, (i // 3) * 640))
        gp = os.path.join(CHECK_DIR, "v2_pro_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved v2_pro_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM LT PLUS V2 Pro video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
