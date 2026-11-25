import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm-ddvs-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media_v2")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

FONTS_TVC_DIR      = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_ROMANCE_CURS  = os.path.join(FONTS_TVC_DIR, "DancingScript-Bold.ttf")   # Condensed 0.83x = 1:1 match with Romance VIP box!
FONT_BRAND_SERIF   = r"C:\Windows\Fonts\timesbd.ttf"
FONT_SANS_BOLD     = os.path.join(FONTS_TVC_DIR, "BeVietnamPro-Bold.ttf")
FONT_SANS_XBOLD    = os.path.join(FONTS_TVC_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_EDIT_ITALIC   = os.path.join(FONTS_TVC_DIR, "PlayfairDisplay-BoldItalic.ttf")
FONT_CAP           = r"C:\Windows\Fonts\palabi.ttf"
FONT_SUB           = os.path.join(FONTS_TVC_DIR, "BeVietnamPro-Medium.ttf")

# Exact sampled colors from physical Romance VIP box (REAL_ROMANCE_VIP_BOX_BOTTLE.png)
ROMANCE_MAROON = (102, 14, 18)   # Left side of "Romance" script
ROMANCE_SCARLET= (212, 24, 28)   # Right side of "Romance" script & rose petals
ROMANCE_GOLD   = (224, 178, 104)
HANGTHU_GREEN1 = (24,  156, 88)
HANGTHU_GREEN2 = (14,  118, 64)

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

def smooth_env(t, t0, t1, d_in=0.46, d_out=0.42):
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
    c = cx_src - (target_w * 0.5) * inv_s
    f = cy_src - (target_h * 0.5) * inv_s
    im = Image.fromarray(rgb_arr, "RGB")
    return im.transform((target_w, target_h), Image.Transform.AFFINE, (inv_s, 0.0, c, 0.0, inv_s, f), resample=Image.Resampling.BICUBIC)

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
# 2. TEXT & 1:1 PACKAGING-MATCHED ROMANCE VIP LOGO RENDERER
# ======================================================================
_sprite_cache = {}
def render_pro_text_sprite(text, font_path, size, top_col, bot_col=None, stroke_col=(255, 255, 255), stroke_w=6, glow_col=None, glow_rad=8, shadow_alpha=90, extrude_col=None, horiz_grad=False, condense_x=1.0):
    bot_col = bot_col or top_col
    key = ("pro", text, font_path, int(round(size)), top_col, bot_col, stroke_col, stroke_w, glow_col, int(round(glow_rad)), shadow_alpha, extrude_col, horiz_grad, round(condense_x, 2))
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
    if horiz_grad:
        gg = np.clip((np.arange(cw, dtype=np.float32) - pad) / max(1.0, float(tw)), 0.0, 1.0)[None, :]
    else:
        gg = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)[:, None]
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.uint8)
    for c in range(3):
        grad_rgb[:, :, c] = np.clip(top_col[c] * (1.0 - gg) + bot_col[c] * gg, 0, 255).astype(np.uint8)
    fill_im = Image.fromarray(np.dstack([grad_rgb, (arr_m * 255.0).astype(np.uint8)]), "RGBA")
    base = Image.alpha_composite(base, fill_im)

    if abs(condense_x - 1.0) > 0.01:
        nw = max(4, int(round(cw * condense_x)))
        base = base.resize((nw, ch), Image.Resampling.LANCZOS)

    if len(_sprite_cache) > 750:
        _sprite_cache.clear()
    _sprite_cache[key] = base
    return base

def render_vip_starburst_badge(diam=64):
    """Exact 18-point crimson starburst 'VIP' seal matching REAL_ROMANCE_VIP_BOX_BOTTLE.png!"""
    key = ("vip_starburst", diam)
    if key in _sprite_cache:
        return _sprite_cache[key]
    S = diam + 16
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cc = S * 0.5
    r_out = diam * 0.5
    r_in  = diam * 0.38
    pts = []
    n_pts = 18
    for i in range(n_pts * 2):
        ang = math.pi * i / n_pts - math.pi * 0.5
        r = r_out if (i % 2 == 0) else r_in
        pts.append((cc + r * math.cos(ang), cc + r * math.sin(ang)))
    d.polygon(pts, fill=(148, 22, 24, 255), outline=(255, 255, 255, 235))
    sp_v = render_pro_text_sprite("VIP", FONT_SANS_XBOLD, max(14, int(diam * 0.34)), (255, 255, 255), stroke_w=0, shadow_alpha=0)
    paste_subpixel(im, sp_v, cc, cc, scale=1.0)
    _sprite_cache[key] = im
    return im

_glass_tag_cache = {}
def get_glass_tag_sprite(label_txt, accent_rgb=(212, 24, 28)):
    k = (label_txt, accent_rgb)
    if k in _glass_tag_cache:
        return _glass_tag_cache[k]
    sp = render_pro_text_sprite(label_txt, FONT_SANS_BOLD, 22, (255, 255, 255), stroke_w=0, shadow_alpha=40)
    sp_c = sp.crop(sp.getbbox())
    pw = min(1010, sp_c.width + 62)
    ph = 48
    tag = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle([8, 8, 8 + pw, 8 + ph], radius=24, fill=(24, 22, 32, 176), outline=(255, 255, 255, 215), width=2)
    td.ellipse([22, 8 + ph // 2 - 5, 32, 8 + ph // 2 + 5], fill=(*accent_rgb, 255))
    paste_subpixel(tag, sp_c, 8 + pw * 0.5 + 8, 8 + ph * 0.5, scale=1.0, opacity=1.0)
    _glass_tag_cache[k] = tag
    return tag

def draw_animated_glass_tag(canvas_im, label_txt, cx, cy, t, st, en, accent_rgb=(212, 24, 28)):
    """Every top label pill has explicit smooth Entrance AND Exit animation (slide + scale + optical blur + fade)!"""
    if not label_txt or t <= st or t >= en:
        return
    d_in, d_out = 0.34, 0.32
    u_in  = ease_out_quart(min(1.0, (t - st) / d_in))
    u_out = quintic_smooth(min(1.0, (en - t) / d_out))
    op = min(quintic_smooth(min(1.0, (t - st) / 0.28)), u_out)
    if op <= 0.01:
        return
    dy = (1.0 - u_in) * (-20.0) - (1.0 - u_out) * 16.0
    sc = (0.92 + 0.08 * u_in) * (0.94 + 0.06 * u_out)
    bl = (1.0 - u_in) * 3.0 + (1.0 - u_out) * 2.5
    tag = get_glass_tag_sprite(label_txt, accent_rgb)
    paste_subpixel(canvas_im, tag, cx, cy + dy, scale=sc, opacity=op, blur_px=bl)

# ======================================================================
# 3. FIVE DISTINCT, VARIED OVERLAY PRESENTATION STYLES (NO REPETITION!)
# ======================================================================
_feather_mask_cache = {}
def get_soft_arch_mask(vw, vh, feather_bot=115):
    k = (vw, vh, feather_bot)
    if k not in _feather_mask_cache:
        yy = np.arange(vh, dtype=np.float32)[:, None]
        u = np.clip((vh - yy) / float(feather_bot), 0.0, 1.0)
        alpha = np.ones((vh, vw), dtype=np.float32) * (u * u * (3.0 - 2.0 * u))
        _feather_mask_cache[k] = Image.fromarray((alpha * 255.0).astype(np.uint8), "L")
    return _feather_mask_cache[k]

def compose_muse_product_stage(vf_rgb, vw, vh, zoom=1.0):
    """Frames 100% of the wide 16:9 Muse product video in the upper safe zone (y=86..668) over soft ambient glow so neither the top pill tag nor the speaker's head ever touches the product!"""
    amb = fit_cover_subpixel(vf_rgb, vw, vh, zoom=1.06).filter(ImageFilter.GaussianBlur(radius=22))
    amb_np = np.clip(np.array(amb, dtype=np.float32) * 0.92 + 16.0, 0, 255)
    fg_h = int(round(vw * 9.0 / 16.0))
    fg_im = fit_cover_subpixel(vf_rgb, vw, fg_h, zoom=zoom)
    fg_np = np.array(fg_im, dtype=np.float32)
    y0 = 84
    yy = np.arange(fg_h, dtype=np.float32)[:, None]
    f_top = np.clip(yy / 42.0, 0.0, 1.0)
    f_bot = np.clip((fg_h - yy) / 56.0, 0.0, 1.0)
    m = (f_top * f_top * (3.0 - 2.0 * f_top)) * (f_bot * f_bot * (3.0 - 2.0 * f_bot))
    m = m[:, :, None]
    y1 = min(vh, y0 + fg_h)
    h_use = y1 - y0
    amb_np[y0:y1] = amb_np[y0:y1] * (1.0 - m[:h_use]) + fg_np[:h_use] * m[:h_use]
    return Image.fromarray(np.clip(amb_np, 0, 255).astype(np.uint8), "RGB")

def style1_fullbleed_soft_cinema(canvas_im, vf_rgb, t, st, en, tag_txt=None, accent_rgb=(212, 24, 28), zoom_from=1.06, zoom_to=1.00, product_safe=False):
    """STYLE 1: Seamless 1080px full-bleed upper cinema melting softly behind speaker."""
    env = smooth_env(t, st, en, d_in=0.42 if st > 0.2 else 0.12, d_out=0.44)
    if env <= 0.005:
        return
    u = quintic_smooth((t - st) / max(0.2, en - st))
    z = zoom_from + (zoom_to - zoom_from) * u
    vw, vh = 1080, 915
    if product_safe:
        crop = compose_muse_product_stage(vf_rgb, vw, vh, zoom=z).convert("RGBA")
    else:
        crop = fit_cover_subpixel(vf_rgb, vw, vh, zoom=z).convert("RGBA")
    mask = get_soft_arch_mask(vw, vh, feather_bot=120)
    arr = np.array(crop)
    arr[:, :, 3] = (np.array(mask, dtype=np.float32) * env).astype(np.uint8)
    glide_y = (1.0 - env) * (-24.0) if st > 0.2 else 0.0
    paste_subpixel(canvas_im, Image.fromarray(arr, "RGBA"), 540.0, 457.5 + glide_y, scale=1.0, opacity=1.0)
    if tag_txt:
        draw_animated_glass_tag(canvas_im, tag_txt, 540.0, 56.0, t, st, en, accent_rgb=accent_rgb)

def style2_diagonal_wipe_dual_scene(canvas_im, vf1_rgb, vf2_rgb, t, st, t_split, en):
    """STYLE 2: Sleek pearl-gold cinema frame + 103-degree feathered diagonal wipe!"""
    env = smooth_env(t, st, en, d_in=0.46, d_out=0.42)
    if env <= 0.005:
        return
    vw, vh = 1020, 820
    u1 = quintic_smooth((t - st) / max(0.2, en - st))
    im1 = fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.02 + 0.05 * u1, pan_x=-0.015 * u1)

    if t <= t_split - 0.35:
        blended = np.array(im1)
    elif t >= t_split + 0.35:
        u2 = quintic_smooth((t - (t_split - 0.35)) / max(0.2, en - t_split + 0.35))
        im2 = fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.02 - 0.02 * u2, pan_x=0.09)
        blended = np.array(im2)
    else:
        u_w = quintic_smooth((t - (t_split - 0.35)) / 0.70)
        u2 = quintic_smooth((t - (t_split - 0.35)) / max(0.2, en - t_split + 0.35))
        im2 = fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.02 - 0.02 * u2, pan_x=0.09)
        yy, xx = np.ogrid[0:vh, 0:vw]
        proj = xx.astype(np.float32) + yy.astype(np.float32) * 0.23
        max_p = vw + vh * 0.23
        edge = -130.0 + (max_p + 260.0) * u_w
        w_mask = np.clip((edge - proj) / 120.0 + 0.5, 0.0, 1.0)
        w_mask = (w_mask * w_mask * (3.0 - 2.0 * w_mask))[:, :, None]
        blended = np.clip(np.array(im1, dtype=np.float32) * (1.0 - w_mask) + np.array(im2, dtype=np.float32) * w_mask, 0, 255).astype(np.uint8)

    rad = 40
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
    ImageDraw.Draw(card).rounded_rectangle([20, 18, 20 + vw - 1, 18 + vh - 1], radius=rad, outline=(255, 244, 232, 215), width=2)

    paste_subpixel(canvas_im, card, 540.0 + (1.0 - env) * (-42.0), 452.0, scale=0.96 + 0.04 * env, opacity=env)
    draw_animated_glass_tag(canvas_im, "SINH HOẠT THIẾU THOẢI MÁI", 540.0, 68.0, t, st, t_split - 0.02, accent_rgb=(228, 72, 98))
    draw_animated_glass_tag(canvas_im, "SAI LẦM RỬA QUÁ NHIỀU LẦN TRONG NGÀY", 540.0, 68.0, t, t_split + 0.02, en, accent_rgb=(228, 72, 98))

def style3_glassmorphic_editorial_morph(canvas_im, bg_room_rgb, vf1_rgb, vf2_rgb, t, st, t_morph, en):
    """STYLE 3: Frosted glassmorphism outer bezel + optical cross-dissolve!"""
    env = smooth_env(t, st, en, d_in=0.48, d_out=0.44)
    if env <= 0.005:
        return
    vw, vh = 984, 776
    pad_g = 22
    gw, gh = vw + pad_g * 2, vh + pad_g * 2

    u_all = quintic_smooth((t - st) / max(0.2, en - st))
    if t <= t_morph - 0.35:
        v_arr = np.array(fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.01 + 0.06 * u_all))
    elif t >= t_morph + 0.35:
        u2 = quintic_smooth((t - (t_morph - 0.35)) / max(0.2, en - t_morph + 0.35))
        v_arr = np.array(fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.05 - 0.04 * u2))
    else:
        um = quintic_smooth((t - (t_morph - 0.35)) / 0.70)
        a1 = np.array(fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.04 + 0.04 * um), dtype=np.float32)
        a2 = np.array(fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.07 - 0.03 * um), dtype=np.float32)
        v_arr = np.clip(a1 * (1.0 - um) + a2 * um, 0, 255).astype(np.uint8)

    cw, ch = gw + 40, gh + 40
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 24, 20 + gw, 24 + gh], radius=48, fill=(16, 24, 38, 82))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    glass = Image.fromarray(bg_room_rgb[25:25 + gh, 26:26 + gw], "RGB").filter(ImageFilter.GaussianBlur(radius=16)).convert("RGBA")
    glass = Image.alpha_composite(glass, Image.new("RGBA", (gw, gh), (255, 255, 255, 122)))
    gmask = Image.new("L", (gw, gh), 0)
    ImageDraw.Draw(gmask).rounded_rectangle([0, 0, gw - 1, gh - 1], radius=48, fill=255)
    glayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    glayer.paste(glass, (20, 20), mask=gmask)
    card = Image.alpha_composite(card, glayer)
    ImageDraw.Draw(card).rounded_rectangle([20, 20, 20 + gw - 1, 20 + gh - 1], radius=48, outline=(255, 255, 255, 230), width=2)

    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=32, fill=255)
    vlayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vlayer.paste(Image.fromarray(v_arr, "RGB"), (20 + pad_g, 20 + pad_g), mask=vmask)
    card = Image.alpha_composite(card, vlayer)

    float_y = math.sin((t - st) * 1.4) * 4.0
    paste_subpixel(canvas_im, card, 540.0, 452.0 + (1.0 - env) * 28.0 + float_y, scale=0.95 + 0.05 * env, opacity=env)
    draw_animated_glass_tag(canvas_im, "MÔI TRƯỜNG ĐANG MẤT CÂN BẰNG", 540.0, 74.0, t, st, t_morph - 0.02, accent_rgb=(56, 162, 232))
    draw_animated_glass_tag(canvas_im, "TẨY RỬA MẠNH LÀM SUY GIẢM LỢI KHUẨN", 540.0, 74.0, t, t_morph + 0.02, en, accent_rgb=(56, 162, 232))

def style4_staggered_dual_pip(canvas_im, vf_left_rgb, vf_right_rgb, t, st1, st2, en):
    """STYLE 4: Editorial 2-Panel Asymmetric Staggered Collage (Microbe Growth + Recurring Discomfort)."""
    env_out = quintic_smooth((en - t) / 0.42) if (en - t) < 0.42 else 1.0
    if t <= st1 or t >= en or env_out <= 0.005:
        return

    def make_pip(v_rgb, pw, ph, zoom_v):
        im = fit_cover_subpixel(v_rgb, pw, ph, zoom=zoom_v)
        cw, ch = pw + 36, ph + 36
        c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([18, 22, 18 + pw, 22 + ph], radius=32, fill=(14, 22, 34, 98))
        c = Image.alpha_composite(c, sh.filter(ImageFilter.GaussianBlur(radius=11)))
        rm = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, fill=255)
        al = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        al.paste(im, (18, 16), mask=rm)
        c = Image.alpha_composite(c, al)
        ImageDraw.Draw(c).rounded_rectangle([18, 16, 18 + pw - 1, 16 + ph - 1], radius=32, outline=(255, 255, 255, 225), width=3)
        return c

    u1 = ease_out_quart(min(1.0, (t - st1) / 0.55))
    z1 = 1.02 + 0.05 * quintic_smooth((t - st1) / max(0.2, en - st1))
    p1 = make_pip(vf_left_rgb, 680, 480, z1)
    u2_shift = quintic_smooth((t - st2) / 0.55) if t >= st2 else 0.0
    cx1 = 445.0 - 72.0 * u2_shift - (1.0 - u1) * 55.0
    cy1 = 315.0 - 18.0 * u2_shift
    paste_subpixel(canvas_im, p1, cx1, cy1, scale=0.92 + 0.08 * u1, opacity=u1 * env_out)

    if t >= st2:
        u2 = ease_out_quart(min(1.0, (t - st2) / 0.55))
        z2 = 1.06 - 0.05 * quintic_smooth((t - st2) / max(0.2, en - st2))
        p2 = make_pip(vf_right_rgb, 610, 440, z2)
        cx2 = 715.0 + (1.0 - u2) * 60.0
        cy2 = 625.0 + (1.0 - u2) * 30.0
        paste_subpixel(canvas_im, p2, cx2, cy2, scale=0.90 + 0.10 * u2, opacity=u2 * env_out)

    draw_animated_glass_tag(canvas_im, "HẠI KHUẨN CÓ ĐIỀU KIỆN PHÁT TRIỂN", 540.0, 64.0, t, st1, st2 - 0.02, accent_rgb=(235, 118, 68))
    draw_animated_glass_tag(canvas_im, "DỄ TÁI ĐI TÁI LẠI DÙ VỆ SINH KỸ", 540.0, 64.0, t, st2 + 0.02, en, accent_rgb=(235, 118, 68))

def style5_luxury_silk_showcase(canvas_im, vf_rgb, t, st, en, tag_txt=None):
    """STYLE 5: Panoramic arched luxury frame with champagne-gold hairline & full 16:9 Muse product framing!"""
    env = smooth_env(t, st, en, d_in=0.45, d_out=0.42)
    if env <= 0.005:
        return
    vw, vh = 1036, 845
    u = quintic_smooth((t - st) / max(0.2, en - st))
    im = compose_muse_product_stage(vf_rgb, vw, vh, zoom=1.00 + 0.03 * u).convert("RGBA")

    yy, xx = np.ogrid[0:vh, 0:vw]
    diag = (xx.astype(np.float32) * 0.8 + yy.astype(np.float32) * 0.45) / (vw * 0.8 + vh * 0.45)
    sweep_pos = -0.25 + 1.50 * quintic_smooth(min(1.0, ((t - st) % 4.8) / 2.6))
    sheen = np.exp(-((diag - sweep_pos) ** 2) / 0.008) * 36.0
    arr = np.array(im, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + sheen * 1.1, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + sheen * 0.95, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + sheen * 0.85, 0, 255)

    cw, ch = vw + 36, vh + 40
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 22, 18 + vw, 22 + vh], radius=46, fill=(55, 22, 36, 82))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    rm = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=46, fill=255)
    al = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    al.paste(Image.fromarray(arr.astype(np.uint8), "RGBA"), (18, 16), mask=rm)
    card = Image.alpha_composite(card, al)
    ImageDraw.Draw(card).rounded_rectangle([18, 16, 18 + vw - 1, 16 + vh - 1], radius=46, outline=(*ROMANCE_GOLD, 238), width=3)

    paste_subpixel(canvas_im, card, 540.0, 452.0 + (1.0 - env) * (-22.0), scale=0.96 + 0.04 * env, opacity=env)
    if tag_txt:
        draw_animated_glass_tag(canvas_im, tag_txt, 540.0, 68.0, t, st, en, accent_rgb=ROMANCE_SCARLET)

# ======================================================================
# 4. SHIMMERING IRIDESCENT 3D PEARL BUBBLES (IMAGE 5 UPGRADE!)
# ======================================================================
_bubble_cache = {}
def get_iridescent_bubble_sprite(label, diam, tint_rgb, text_rgb=(98, 14, 24)):
    key = (label, diam, tint_rgb, text_rgb)
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

    rim = np.power(np.clip(dist, 0.0, 1.0), 2.6)
    caustic_bot = np.clip(dy * 0.65 + 0.35, 0.0, 1.0) * np.exp(-((dist - 0.82) ** 2) / 0.035)
    spec_top = np.exp(-(((dx + 0.34) ** 2 + (dy + 0.38) ** 2) / 0.045))
    spec_pin = np.exp(-(((dx + 0.44) ** 2 + (dy + 0.46) ** 2) / 0.008))

    rgba = np.zeros((S, S, 4), dtype=np.float32)
    rgba[:, :, 0] = 248 * (1.0 - rim * 0.36) + tint_rgb[0] * (rim * 0.36) + 45 * caustic_bot + 90 * spec_top
    rgba[:, :, 1] = 246 * (1.0 - rim * 0.36) + tint_rgb[1] * (rim * 0.36) + 38 * caustic_bot + 90 * spec_top
    rgba[:, :, 2] = 252 * (1.0 - rim * 0.36) + tint_rgb[2] * (rim * 0.36) + 42 * caustic_bot + 90 * spec_top

    alpha = (0.36 + 0.54 * rim + 0.30 * caustic_bot + 0.52 * spec_top + 0.65 * spec_pin) * 255.0
    edge_aa = np.clip((1.0 - dist) * r * 0.85, 0.0, 1.0)
    rgba[:, :, 3] = np.where(inside, np.clip(alpha, 0, 246) * edge_aa, 0.0)

    bim = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")
    aura = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(aura).ellipse([int(c - r), int(c - r), int(c + r), int(c + r)], outline=(*tint_rgb, 135), width=4)
    bim = Image.alpha_composite(aura.filter(ImageFilter.GaussianBlur(radius=5)), bim)

    lines = label.split("\n")
    fsz = 26 if max(len(x) for x in lines) <= 9 else 22
    line_sps = [
        render_pro_text_sprite(ln, FONT_SANS_XBOLD, fsz, text_rgb, stroke_col=(255, 255, 255), stroke_w=5, shadow_alpha=40)
        for ln in lines
    ]
    line_step = 30.0
    cur_y = c - (len(line_sps) - 1) * line_step * 0.5
    for sp in line_sps:
        paste_subpixel(bim, sp, c, cur_y, scale=1.0, opacity=1.0)
        cur_y += line_step

    _bubble_cache[key] = bim
    return bim

def draw_shimmering_product_bubbles(canvas_im, t_now):
    """
    Renders luminous iridescent 3D crystal-pearl bubbles rising gracefully around BOTH product showcases:
    - 42.20 - 46.72s (White Probiotic Cream Stage): Acid Lactic, Độ pH Sinh Lý, Hệ Lợi Khuẩn, Cân Bằng Êm Dịu
    - 47.40 - 57.08s (Romance VIP Luxury Stage): Cúc La Mã, Cam Thảo, Khỏe Bên Trong, Đẹp Bên Ngoài
    """
    spans = [
        (42.20, 46.72, (16, 98, 58), [
            (42.30, "Viên Đặt\nHằng Thu", 136, (132, 232, 182), 124.0, 235.0, 0.0),
            (43.65, "Acid\nLactic",       134, (148, 215, 255), 956.0, 228.0, 1.2),
            (44.80, "Độ pH\nSinh Lý",     138, (255, 208, 142), 124.0, 565.0, 2.4),
            (45.55, "Lợi Khuẩn\nTự Nhiên",138, (142, 236, 205), 956.0, 558.0, 3.6),
        ]),
        (47.40, 57.08, (112, 14, 24), [
            (47.50, "Cúc\nLa Mã",         136, (255, 212, 132), 126.0, 245.0, 0.4),
            (48.62, "Cam\nThảo",          134, (148, 234, 186), 954.0, 238.0, 1.6),
            (53.40, "Khỏe Từ\nBên Trong", 140, (255, 168, 198), 130.0, 545.0, 2.8),
            (55.45, "Đẹp Từ\nBên Ngoài",  140, (255, 192, 152), 950.0, 538.0, 4.0),
        ]),
    ]
    for s_st, s_en, txt_col, bubbles in spans:
        if s_st <= t_now < s_en:
            u_out_b = quintic_smooth(min(1.0, (s_en - t_now) / 0.42))

            micro_layer = Image.new("RGBA", (W, 920), (0, 0, 0, 0))
            md = ImageDraw.Draw(micro_layer)
            for mi in range(12):
                phase = (t_now * (0.26 + (mi % 4) * 0.05) + mi * 0.37) % 1.0
                mx = 95.0 + (mi * 71.0) % 890.0 + math.sin(t_now * 1.8 + mi) * 12.0
                my = 840.0 - phase * 740.0
                mr = 4 + (mi % 3) * 3
                ma = int(125 * math.sin(phase * math.pi) * u_out_b)
                if ma > 8:
                    md.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 250, 253, ma), outline=(255, 255, 255, min(255, ma + 40)))
            canvas_im.alpha_composite(micro_layer, dest=(0, 0))

            for st_b, lbl, diam, tint, tx, ty, seed in bubbles:
                if t_now < st_b:
                    continue
                dt = t_now - st_b
                u_rise = ease_out_quart(min(1.0, dt / 0.72))
                u_in_b = quintic_smooth(min(1.0, dt / 0.32))
                op = u_in_b * u_out_b
                bx = tx + math.sin(dt * 1.55 + seed) * 6.5
                by = ty + (1.0 - u_rise) * 110.0 - (1.0 - u_out_b) * 28.0 + math.cos(dt * 1.35 + seed) * 6.0
                sc = (0.62 + 0.38 * u_rise) * (0.88 + 0.12 * u_out_b) * (1.0 + 0.02 * math.sin(dt * 2.2 + seed))
                bl = (1.0 - u_in_b) * 2.5 + (1.0 - u_out_b) * 2.5
                bsp = get_iridescent_bubble_sprite(lbl, diam, tint, text_rgb=txt_col)
                paste_subpixel(canvas_im, bsp, bx, by, scale=sc, opacity=op, blur_px=bl)
            break

# ======================================================================
# 5. AUTHENTIC PACKAGING-MATCHED BRAND HEADER CARDS (IMAGE 7 UPGRADE!)
# ======================================================================
_brand_card_cache = {}
def get_authentic_ddvs_brand_card(mode_key):
    if mode_key in _brand_card_cache:
        return _brand_card_cache[mode_key]

    pw, ph = 976, 262
    cw, ch = pw + 44, ph + 44
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([22, 26, 22 + pw, 26 + ph], radius=48, fill=(48, 18, 28, 82))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, pw, dtype=np.float32)[None, :]
    center_lift = np.exp(-(xx * xx * 1.3 + (yy - 0.35) ** 2 * 2.0))
    bg = np.zeros((ph, pw, 3), dtype=np.uint8)

    if mode_key == "bridge1":
        # Clean luxury Pearl-Ivory & Emerald-Gold Hằng Thu consultation card
        bg[:, :, 0] = np.clip(242 + 12 * center_lift, 0, 255).astype(np.uint8)
        bg[:, :, 1] = np.clip(248 + 7 * center_lift, 0, 255).astype(np.uint8)
        bg[:, :, 2] = np.clip(244 + 9 * center_lift, 0, 255).astype(np.uint8)
        bg_im = Image.fromarray(bg, "RGB").convert("RGBA")
        rib = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rib)
        rd.line([(-20, 35), (210, ph + 20)], fill=(115, 198, 152, 125), width=4)
        rd.line([(pw + 20, 35), (pw - 210, ph + 20)], fill=(115, 198, 152, 125), width=4)
        bg_im = Image.alpha_composite(bg_im, rib)

        rmask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=46, fill=255)
        blayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        blayer.paste(bg_im, (22, 20), mask=rmask)
        card = Image.alpha_composite(card, blayer)
        ImageDraw.Draw(card).rounded_rectangle([22, 20, 22 + pw - 1, 20 + ph - 1], radius=46, outline=(255, 255, 255, 248), width=4)
        ImageDraw.Draw(card).rounded_rectangle([26, 24, 18 + pw, 16 + ph], radius=42, outline=(*ROMANCE_GOLD, 195), width=2)

        sp_top = render_pro_text_sprite("GIẢI PHÁP CHĂM SÓC CHUYÊN BIỆT", FONT_BRAND_SERIF, 24, (28, 52, 38), stroke_w=0, shadow_alpha=0)
        sp_mid = render_pro_text_sprite("LÀM SẠCH & CÂN BẰNG", FONT_BRAND_SERIF, 62, HANGTHU_GREEN1, HANGTHU_GREEN2, stroke_col=(255, 255, 255), stroke_w=3, shadow_alpha=30)
        sp_bot = render_pro_text_sprite("BẢO VỆ HỆ VI SINH & ĐỘ pH TỰ NHIÊN", FONT_SANS_BOLD, 28, (165, 22, 36), stroke_w=0, shadow_alpha=0)
        paste_subpixel(card, sp_top, cw * 0.5, 20 + 44,  scale=1.0)
        paste_subpixel(card, sp_mid, cw * 0.5, 20 + 124, scale=1.0)
        ImageDraw.Draw(card).line([(cw // 2 - 230, 20 + 178), (cw // 2 + 230, 20 + 178)], fill=(32, 148, 88, 165), width=2)
        paste_subpixel(card, sp_bot, cw * 0.5, 20 + 216, scale=1.0)
    else:
        # 1:1 Physical Romance VIP Packaging Match: Crisp Porcelain-Ivory upper + Velvet Crimson accent + Condensed Cursive "Romance" + Starburst "VIP"!
        bg[:, :, 0] = np.clip(250 + 5 * center_lift, 0, 255).astype(np.uint8)
        bg[:, :, 1] = np.clip(242 + 10 * center_lift, 0, 255).astype(np.uint8)
        bg[:, :, 2] = np.clip(244 + 8 * center_lift, 0, 255).astype(np.uint8)
        bg_im = Image.fromarray(bg, "RGB").convert("RGBA")
        rib = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rib)
        rd.line([(-20, 35), (215, ph + 20)], fill=(212, 42, 56, 115), width=4)
        rd.line([(25, 0), (265, ph + 20)], fill=(235, 182, 118, 145), width=2)
        rd.line([(pw + 20, 35), (pw - 215, ph + 20)], fill=(212, 42, 56, 115), width=4)
        rd.line([(pw - 25, 0), (pw - 265, ph + 20)], fill=(235, 182, 118, 145), width=2)
        bg_im = Image.alpha_composite(bg_im, rib)

        rmask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=46, fill=255)
        blayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        blayer.paste(bg_im, (22, 20), mask=rmask)
        card = Image.alpha_composite(card, blayer)
        ImageDraw.Draw(card).rounded_rectangle([22, 20, 22 + pw - 1, 20 + ph - 1], radius=46, outline=(255, 255, 255, 248), width=4)
        ImageDraw.Draw(card).rounded_rectangle([26, 24, 18 + pw, 16 + ph], radius=42, outline=(195, 28, 34, 185), width=2)

        sp_top = render_pro_text_sprite("BỘ ĐÔI HẰNG THU  •  HẠN CHẾ TÁI PHÁT", FONT_BRAND_SERIF, 24, (45, 16, 20), stroke_w=0, shadow_alpha=0)
        # Exact condensed cursive "Romance" (burgundy -> scarlet horizontal gradient) + 18-point crimson "VIP" starburst!
        sp_rom = render_pro_text_sprite(
            "Romance", FONT_ROMANCE_CURS, 108,
            ROMANCE_MAROON, ROMANCE_SCARLET,
            stroke_col=(255, 255, 255), stroke_w=4,
            shadow_alpha=35, horiz_grad=True, condense_x=0.83
        )
        vip_b = render_vip_starburst_badge(64)
        sp_bot = render_pro_text_sprite("KHỎE TỪ BÊN TRONG  •  ĐẸP TỪ BÊN NGOÀI", FONT_BRAND_SERIF, 30, (178, 18, 24), stroke_w=0, shadow_alpha=0)

        paste_subpixel(card, sp_top, cw * 0.5, 20 + 40, scale=1.0)
        paste_subpixel(card, sp_rom, cw * 0.5 - 28, 20 + 122, scale=1.0)
        paste_subpixel(card, vip_b,  cw * 0.5 + (sp_rom.width * 0.5) - 24, 20 + 92, scale=1.0)
        ImageDraw.Draw(card).line([(cw // 2 - 235, 20 + 182), (cw // 2 + 235, 20 + 182)], fill=(195, 28, 34, 165), width=2)
        paste_subpixel(card, sp_bot, cw * 0.5, 20 + 218, scale=1.0)

    _brand_card_cache[mode_key] = card
    return card

# ======================================================================
# 6. BUTTER-SMOOTH CAMERA ZOOM & PACKAGING-MATCHED CAPTIONS
# ======================================================================
ZOOM_KEYS = [
    (0.00, 1.010),
    (3.45, 1.042),
    (8.55, 1.020),
    (13.68, 1.048),
    (19.20, 1.024),
    (24.52, 1.050),
    (34.20, 1.022),
    (40.18, 1.048),
    (46.78, 1.022),
    (52.74, 1.048),
    (57.16, 1.020),
    (60.48, 1.045),
    (67.64, 1.015),
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

def load_captions_ddvs_v2():
    """
    Semantic Readable Phrase Chunker (1.6s - 3.1s per phrase, 5-9 words balanced across 1-2 lines).
    Eliminates 1-2 word <1.0s flashes so viewers always have comfortable time to read every phrase!
    """
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and (w["start"] + w["end"]) * 0.5 >= 3.40
    ]

    # Step 1: Build semantic phrases of 5..9 words (breaking cleanly at punctuation or pauses >= 0.42s)
    phrases = []
    cur_p = []
    for i, w in enumerate(words):
        txt, ws, we = w
        if cur_p:
            gap = ws - cur_p[-1][2]
            prev_txt = cur_p[-1][0]
            dur_so_far = cur_p[-1][2] - cur_p[0][1]
            # Break on sentence/clause boundary once we have >= 4 words or >= 1.35s, or cap at 8 words
            if gap >= 0.45 or (re.search(r"[.?!…;:]$", prev_txt) and len(cur_p) >= 3):
                phrases.append(cur_p); cur_p = []
            elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 4 or dur_so_far >= 1.45):
                phrases.append(cur_p); cur_p = []
            elif len(cur_p) >= 8 or sum(len(x[0]) + 1 for x in cur_p) + len(txt) > 38:
                phrases.append(cur_p); cur_p = []
        cur_p.append(w)
    if cur_p:
        phrases.append(cur_p)

    # Merge any tiny <= 2-word orphan phrase into an adjacent phrase if close in time (< 0.55s)
    merged = []
    for p in phrases:
        if merged and len(p) <= 2 and (p[0][1] - merged[-1][-1][2]) < 0.50 and len(merged[-1]) + len(p) <= 9:
            merged[-1].extend(p)
        else:
            merged.append(p)

    # Step 2: Balance each phrase cleanly into 1 or 2 visual lines
    def split_balanced_lines(p):
        total_chars = sum(len(x[0]) + 1 for x in p) - 1
        if len(p) <= 4 and total_chars <= 20:
            return [p]
        best_k = max(1, len(p) // 2)
        best_diff = 9999
        for k in range(1, len(p)):
            c1 = sum(len(x[0]) + 1 for x in p[:k]) - 1
            c2 = sum(len(x[0]) + 1 for x in p[k:]) - 1
            diff = abs(c1 - c2) + (6 if max(c1, c2) > 23 else 0)
            if diff < best_diff:
                best_diff = diff
                best_k = k
        return [p[:best_k], p[best_k:]]

    GOLD_WORDS = {"cân", "bằng", "bằng.", "lợi", "khuẩn", "Acid", "Lactic", "pH", "Cúc", "La", "Mã", "Cam", "Thảo,", "tự", "nhiên,"}
    ROSE_WORDS = {"sai", "lầm", "mất", "tẩy", "rửa", "mạnh,", "viêm,", "viêm", "tái", "lại", "khỏe", "đẹp", "phát,"}

    cap_groups = []
    for i, p in enumerate(merged):
        t0 = max(3.40, p[0][1] - 0.06)
        last_end = p[-1][2]
        nxt_start = merged[i + 1][0][1] if i + 1 < len(merged) else 67.50
        # Hold subtitle comfortably after last word (up to +0.85s across pauses, leaving a clean 0.04s handoff!)
        min_hold = max(last_end + 0.42, t0 + 1.55)
        t1 = min(nxt_start - 0.04, max(min_hold, last_end + 0.65))
        if t1 <= last_end + 0.12:
            t1 = min(nxt_start - 0.02, last_end + 0.25)
        cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced_lines(p)})
    return cap_groups, GOLD_WORDS, ROSE_WORDS

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
    tail_from = None
    if "--tail-from" in sys.argv:
        tail_from = int(sys.argv[sys.argv.index("--tail-from") + 1])
    test_frames = {
        int(round(ts * FPS))
        for ts in [2.35, 5.80, 11.20, 16.50, 29.80, 37.00, 45.80, 54.80, 65.50]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vkeys = (
        ["ddvs_v2_natural_harmony"]
        if tail_from is not None else [
            "ddvs_v2_hook", "ddvs_v2_discomfort", "ddvs_v2_overwash",
            "ddvs_v2_ph_imbalance", "ddvs_v2_harsh_strip",
            "ddvs_v2_microbe_recur", "ddvs_v2_tired_worry",
            "ddvs_v2_viendat_hydrogel", "ddvs_v2_romance_luxury",
            "ddvs_v2_natural_harmony"
        ]
    )
    clips = {}
    for vk in vkeys:
        vp = os.path.join(MEDIA_DIR, f"{vk}.mp4")
        if os.path.exists(vp):
            clips[vk] = load_vid_frames_wh(vp, 1280, 720)
            print(f"Loaded {vk}: {len(clips[vk])} frames")
        else:
            print(f"WARNING missing {vp}")

    cap_groups, GOLD_WORDS, ROSE_WORDS = load_captions_ddvs_v2()

    legal_sp = render_pro_text_sprite(
        "Sản phẩm hỗ trợ chăm sóc & vệ sinh chuyên biệt • Đọc kỹ hướng dẫn sử dụng trước khi dùng",
        FONT_SUB, 20, (250, 248, 250), stroke_col=(28, 18, 28), stroke_w=3, shadow_alpha=0
    )

    # Pre-build crisp unclipped Romance VIP • Hằng Thu Closing Ribbon Card!
    cta_w, cta_h = 968, 74
    cta_card_cached = Image.new("RGBA", (cta_w + 24, cta_h + 24), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cta_card_cached)
    cd.rounded_rectangle([12, 14, 12 + cta_w, 14 + cta_h], radius=37, fill=(48, 12, 24, 92))
    cta_card_cached = cta_card_cached.filter(ImageFilter.GaussianBlur(radius=6))
    cd = ImageDraw.Draw(cta_card_cached)
    cd.rounded_rectangle([12, 10, 12 + cta_w, 10 + cta_h], radius=37, fill=(252, 244, 246, 250), outline=(255, 255, 255, 248), width=3)
    cd.rounded_rectangle([15, 13, 9 + cta_w, 7 + cta_h], radius=34, outline=(195, 28, 34, 175), width=1)

    sp_c1 = render_pro_text_sprite("Bộ đôi", FONT_SANS_BOLD, 25, (42, 18, 24), stroke_w=0, shadow_alpha=0)
    sp_c2 = render_pro_text_sprite("Romance", FONT_ROMANCE_CURS, 46, ROMANCE_MAROON, ROMANCE_SCARLET, stroke_w=0, shadow_alpha=0, horiz_grad=True, condense_x=0.84)
    vip_sm = render_vip_starburst_badge(34)
    sp_c3 = render_pro_text_sprite("& Viên Đặt Hằng Thu  •  Cân bằng tự nhiên", FONT_SANS_BOLD, 24, (42, 18, 24), stroke_w=0, shadow_alpha=0)
    sp_c1 = sp_c1.crop(sp_c1.getbbox())
    sp_c2 = sp_c2.crop(sp_c2.getbbox())
    vip_sm = vip_sm.crop(vip_sm.getbbox())
    sp_c3 = sp_c3.crop(sp_c3.getbbox())
    g1, g2, g3 = 10, 4, 10
    tot_cw = sp_c1.width + g1 + sp_c2.width + g2 + vip_sm.width + g3 + sp_c3.width
    sx0 = 12 + (cta_w - tot_cw) * 0.5
    cy0 = 10 + cta_h * 0.5
    paste_subpixel(cta_card_cached, sp_c1, sx0 + sp_c1.width * 0.5,                                              cy0, scale=1.0)
    paste_subpixel(cta_card_cached, sp_c2, sx0 + sp_c1.width + g1 + sp_c2.width * 0.5,                           cy0 - 1, scale=1.0)
    paste_subpixel(cta_card_cached, vip_sm,sx0 + sp_c1.width + g1 + sp_c2.width + g2 + vip_sm.width * 0.5,       cy0 - 6, scale=1.0)
    paste_subpixel(cta_card_cached, sp_c3, sx0 + sp_c1.width + g1 + sp_c2.width + g2 + vip_sm.width + g3 + sp_c3.width * 0.5, cy0, scale=1.0)

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_ddvs_v2_pro_video_only.mp4")
    tail_vid_out = os.path.join(PROJ_DIR, "_ddvs_v2_tail_patch.mp4")
    target_vid_out = tail_vid_out if tail_from is not None else raw_vid_out
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            target_vid_out
        ], stdin=subprocess.PIPE)

    yy_g, xx_g = np.ogrid[0:H, 0:W]
    desk_mask      = np.clip((yy_g.astype(np.float32) - 1345.0) / 55.0, 0.0, 1.0)
    left_box_guard = np.clip((305.0 - xx_g.astype(np.float32)) / 50.0, 0.0, 1.0) * np.clip((yy_g.astype(np.float32) - 1065.0) / 55.0, 0.0, 1.0)
    static_fg_guard = np.maximum(desk_mask, left_box_guard)

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
        if tail_from is not None and frame_idx < tail_from:
            frame_idx += 1
            continue

        rgb = polish_bright_frame(rgb_raw)
        matte = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W)).astype(np.float32) / 255.0
        t = frame_idx / FPS

        # 1. Subpixel-Smooth Camera Zoom!
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
        # 2. FIVE VARIED, CONTEXTUAL VIDEO OVERLAY STYLES BEHIND SPEAKER!
        # ==================================================================
        if 0.00 <= t <= 3.42:
            # STYLE 1: Seamless Full-Bleed Soft Cinema Hook (Speaker Hesitating Over Harsh Cleanser!)
            vf = get_clip_frame(clips, "ddvs_v2_hook", t)
            style1_fullbleed_soft_cinema(comp_im, vf, t, 0.00, 3.42, tag_txt="KHÍ HƯ CÓ MÙI • ĐỪNG CHỈ RỬA THẬT MẠNH", accent_rgb=ROMANCE_SCARLET, zoom_from=1.06, zoom_to=1.00)
            need_fg_recomp = True

        elif 3.45 <= t <= 13.64:
            # STYLE 2: Diagonal Wipe Dual-Scene (Office Discomfort -> Repeated Overwashing at Sink!)
            vf1 = get_clip_frame(clips, "ddvs_v2_discomfort", t - 3.45)
            vf2 = get_clip_frame(clips, "ddvs_v2_overwash", max(0.0, t - 8.20))
            style2_diagonal_wipe_dual_scene(comp_im, vf1, vf2, t, 3.45, 8.55, 13.64)
            need_fg_recomp = True

        elif 13.68 <= t <= 24.50:
            # STYLE 3: Frosted Glassmorphism Frame + Optical Morph (pH Imbalance -> Harsh Foam Stripping Flora!)
            vf1 = get_clip_frame(clips, "ddvs_v2_ph_imbalance", t - 13.68)
            vf2 = get_clip_frame(clips, "ddvs_v2_harsh_strip", max(0.0, t - 18.85))
            style3_glassmorphic_editorial_morph(comp_im, fg_rgb, vf1, vf2, t, 13.68, 19.20, 24.50)
            need_fg_recomp = True

        elif 24.52 <= t <= 34.16:
            # STYLE 4: Staggered 2-Panel Split Collage (Microbe Growth + Speaker Tired of Recurring Discomfort!)
            vf1 = get_clip_frame(clips, "ddvs_v2_microbe_recur", t - 24.52)
            vf2 = get_clip_frame(clips, "ddvs_v2_tired_worry", max(0.0, t - 27.80))
            style4_staggered_dual_pip(comp_im, vf1, vf2, t, 24.52, 27.80, 34.16)
            need_fg_recomp = True

        elif 34.20 <= t <= 40.15:
            # Editorial Brand Bridge Card #1 over soft sunlit bokeh studio backdrop (explicit Entrance + Exit!)
            u_in_b1  = ease_out_quart(min(1.0, (t - 34.20) / 0.42))
            u_out_b1 = quintic_smooth(min(1.0, (40.15 - t) / 0.38))
            op_b1    = min(quintic_smooth(min(1.0, (t - 34.20) / 0.34)), u_out_b1)
            if op_b1 > 0.01:
                vf_bg = get_clip_frame(clips, "ddvs_v2_natural_harmony", t - 34.20)
                bg_blur = np.array(Image.fromarray(vf_bg, "RGB").filter(ImageFilter.GaussianBlur(radius=22)))
                bg_soft = np.clip(bg_blur.astype(np.float32) * 0.75 + 64.0, 0, 255).astype(np.uint8)
                style1_fullbleed_soft_cinema(comp_im, bg_soft, t, 34.20, 40.15, tag_txt=None, zoom_from=1.02, zoom_to=1.00)
                bcard = get_authentic_ddvs_brand_card("bridge1")
                dy_b1 = (1.0 - u_in_b1) * 24.0 - (1.0 - u_out_b1) * 18.0
                sc_b1 = (0.93 + 0.07 * u_in_b1) * (0.94 + 0.06 * u_out_b1)
                bl_b1 = (1.0 - u_in_b1) * 3.5 + (1.0 - u_out_b1) * 3.0
                paste_subpixel(comp_im, bcard, 540.0, 445.0 + dy_b1, scale=sc_b1, opacity=op_b1, blur_px=bl_b1)
                need_fg_recomp = True

        elif 40.18 <= t <= 46.75:
            # STYLE 1B: Muse Luxury Commercial Video — Authentic Green Hằng Thu Boxes on Probiotic Cream!
            vf = get_clip_frame(clips, "ddvs_v2_viendat_hydrogel", t - 40.18)
            style1_fullbleed_soft_cinema(comp_im, vf, t, 40.18, 46.75, tag_txt="VIÊN ĐẶT PHỤ KHOA HẰNG THU • ĐỘ pH SINH LÝ", accent_rgb=HANGTHU_GREEN1, zoom_from=1.00, zoom_to=1.03, product_safe=True)
            need_fg_recomp = True

        elif 46.78 <= t <= 57.14:
            # STYLE 5: Muse Luxury Commercial Video — Authentic Romance VIP Box & Bottle on Botanical Pedestal!
            vf = get_clip_frame(clips, "ddvs_v2_romance_luxury", t - 46.78)
            style5_luxury_silk_showcase(comp_im, vf, t, 46.78, 57.14, tag_txt="DUNG DỊCH VỆ SINH ROMANCE VIP • HẰNG THU")
            need_fg_recomp = True

        elif 57.16 <= t <= 60.46:
            # 1:1 Physical Packaging-Matched Romance VIP Brand Header Card (explicit Entrance + Exit!)
            u_in_b2  = ease_out_quart(min(1.0, (t - 57.16) / 0.42))
            u_out_b2 = quintic_smooth(min(1.0, (60.46 - t) / 0.36))
            op_b2    = min(quintic_smooth(min(1.0, (t - 57.16) / 0.34)), u_out_b2)
            if op_b2 > 0.01:
                vf_bg2 = get_clip_frame(clips, "ddvs_v2_romance_luxury", t - 57.16)
                bg_blur2 = np.array(Image.fromarray(vf_bg2, "RGB").filter(ImageFilter.GaussianBlur(radius=24)))
                bg_soft2 = np.clip(bg_blur2.astype(np.float32) * 0.72 + np.array([72.0, 64.0, 66.0], dtype=np.float32), 0, 255).astype(np.uint8)
                style1_fullbleed_soft_cinema(comp_im, bg_soft2, t, 57.16, 60.46, tag_txt=None, zoom_from=1.02, zoom_to=1.00)
                bcard = get_authentic_ddvs_brand_card("romance_vip")
                dy_b2 = (1.0 - u_in_b2) * 24.0 - (1.0 - u_out_b2) * 18.0
                sc_b2 = (0.93 + 0.07 * u_in_b2) * (0.94 + 0.06 * u_out_b2)
                bl_b2 = (1.0 - u_in_b2) * 3.5 + (1.0 - u_out_b2) * 3.0
                paste_subpixel(comp_im, bcard, 540.0, 445.0 + dy_b2, scale=sc_b2, opacity=op_b2, blur_px=bl_b2)
                need_fg_recomp = True

        elif 60.48 <= t <= 67.55:
            # STYLE 1C: Full-Bleed Sunlit Natural Harmony Finale (Speaker Smiling Confidently by Chamomile Window!)
            vf = get_clip_frame(clips, "ddvs_v2_natural_harmony", t - 60.48)
            style1_fullbleed_soft_cinema(comp_im, vf, t, 60.48, 67.55, tag_txt="LẤY LẠI THẾ CÂN BẰNG MỘT CÁCH TỰ NHIÊN", accent_rgb=HANGTHU_GREEN1, zoom_from=1.05, zoom_to=1.00)
            need_fg_recomp = True

        # Re-composite Real Pharmacist + Desk + All Held/Table Product Boxes cleanly in FRONT!
        if need_fg_recomp:
            fg_alpha = np.maximum(m_arr, static_fg_guard)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 3. Shimmering Iridescent 3D Crystal-Pearl Bubbles Rising Around Both Products!
        draw_shimmering_product_bubbles(comp_im, t)

        # 4. Refined Editorial Hook Typography on Dark Blazer (0.06 - 3.36s, Explicit Entrance AND Exit!)
        if 0.06 <= t <= 3.36:
            u_hk_out = quintic_smooth(min(1.0, (3.36 - t) / 0.34))
            dy_out   = -(1.0 - u_hk_out) * 16.0
            sc_out   = 0.94 + 0.06 * u_hk_out
            bl_out   = (1.0 - u_hk_out) * 3.0
            if t >= 0.06:
                u1 = ease_out_quart(min(1.0, (t - 0.06) / 0.36))
                sp1 = render_pro_text_sprite("Khí hư có mùi khó chịu...", FONT_SANS_BOLD, 42, (255, 255, 255), (242, 236, 244), stroke_col=(18, 24, 38), stroke_w=6)
                paste_subpixel(comp_im, sp1, 540.0, 1104.0 + (1.0 - u1) * 18.0 + dy_out, scale=(0.93 + 0.07 * u1) * sc_out, opacity=u1 * u_hk_out, blur_px=(1.0 - u1) * 2.5 + bl_out)
            if t >= 1.30:
                u2 = ease_out_quart(min(1.0, (t - 1.30) / 0.38))
                sp2 = render_pro_text_sprite("ĐỪNG CHỈ", FONT_SANS_XBOLD, 64, (255, 218, 128), (242, 178, 72), stroke_col=(24, 18, 32), stroke_w=7, glow_col=(255, 198, 92), glow_rad=8)
                paste_subpixel(comp_im, sp2, 285.0, 1206.0 + (1.0 - u2) * 20.0 + dy_out, scale=(0.92 + 0.08 * u2) * sc_out, opacity=u2 * u_hk_out, blur_px=(1.0 - u2) * 2.5 + bl_out)
            if t >= 2.04:
                u3 = ease_out_quart(min(1.0, (t - 2.04) / 0.40))
                sp3 = render_pro_text_sprite("rửa thật sạch!", FONT_EDIT_ITALIC, 62, (255, 178, 204), (245, 132, 172), stroke_col=(24, 18, 32), stroke_w=6)
                paste_subpixel(comp_im, sp3, 742.0, 1208.0 + (1.0 - u3) * 20.0 + dy_out, scale=(0.92 + 0.08 * u3) * sc_out, opacity=u3 * u_hk_out, blur_px=(1.0 - u3) * 2.5 + bl_out)

        # 5. Full-Phrase Readable Chest Captions (Comfortable Hold + Entrance Animation + Active-Word Highlight + Exit Animation!)
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in  = t - g["t0"]
                dt_out = g["t1"] - t
                u_g_out = quintic_smooth(min(1.0, dt_out / 0.26))
                dy_g_out = -(1.0 - u_g_out) * 14.0
                sc_g_out = 0.94 + 0.06 * u_g_out
                bl_g_out = (1.0 - u_g_out) * 2.5

                has_left_box = (t >= 16.8)
                x_center = 626.0 if has_left_box else 540.0
                min_x    = 292.0 if has_left_box else 48.0
                max_w_ok = (1036.0 - min_x)
                cap_sz_base = 53.0 if has_left_box else 57.0
                y_base = 1104.0 if len(g["lines"]) >= 2 else 1134.0
                lh = 64.0
                gap = 21.0

                for li, ln in enumerate(g["lines"]):
                    # Stagger line 2 entrance slightly (0.06s) for silky editorial motion!
                    u_ln_in = ease_out_quart(min(1.0, max(0.0, dt_in - li * 0.06) / 0.28))
                    op_ln   = quintic_smooth(min(1.0, max(0.0, dt_in - li * 0.06) / 0.22)) * u_g_out
                    if op_ln <= 0.01:
                        continue
                    dy_ln = (1.0 - u_ln_in) * 18.0 + dy_g_out
                    bl_ln = (1.0 - u_ln_in) * 3.0 + bl_g_out
                    sc_ln = (0.93 + 0.07 * u_ln_in) * sc_g_out

                    word_renders = []
                    total_w = 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        # Smooth karaoke pulse while word is actively spoken
                        is_active = (ws - 0.05) <= t <= (we + 0.22)
                        act_pulse = 1.055 if is_active else 1.0
                        if wtxt == "Romance":
                            sp = render_pro_text_sprite(
                                wtxt, FONT_ROMANCE_CURS, cap_sz_base * 1.38,
                                ROMANCE_MAROON, ROMANCE_SCARLET,
                                stroke_col=(255, 250, 248), stroke_w=6,
                                glow_col=(255, 185, 195), glow_rad=8, shadow_alpha=95,
                                horiz_grad=True, condense_x=0.84
                            )
                            adv = sp.width - 52.0
                        elif wtxt in ("VIP", "Hằng", "Thu", "Thu."):
                            sp = render_pro_text_sprite(
                                wtxt, FONT_BRAND_SERIF, cap_sz_base * 1.12,
                                ROMANCE_SCARLET, (165, 10, 18),
                                stroke_col=(255, 250, 248), stroke_w=6,
                                glow_col=(255, 195, 205), glow_rad=8, shadow_alpha=95
                            )
                            adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_BRAND_SERIF, cap_sz_base * 1.12))
                        else:
                            is_gold = wtxt in GOLD_WORDS
                            is_rose = wtxt in ROSE_WORDS
                            k = 1.10 if (is_gold or is_rose) else 1.0
                            sz_use = cap_sz_base * k
                            if is_gold:
                                col = (255, 232, 108) if is_active else (255, 218, 96)
                            elif is_rose:
                                col = (255, 172, 204) if is_active else (252, 154, 190)
                            else:
                                col = (255, 255, 255) if is_active else (238, 250, 246)
                            sp = render_pro_text_sprite(
                                wtxt, FONT_CAP, sz_use,
                                col, stroke_col=(14, 20, 34), stroke_w=5,
                                glow_col=col, glow_rad=(8 if is_active else 5), shadow_alpha=88
                            )
                            adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_CAP, sz_use))
                        word_renders.append((wtxt, ws, we, sp, adv, act_pulse))
                        total_w += adv + (gap if wi > 0 else 0.0)

                    # Auto-scale line smoothly if wider than safe Box-Free chest zone!
                    fit_k = min(1.0, max_w_ok / max(1.0, total_w))
                    eff_total_w = total_w * fit_k
                    cur_x = max(min_x, min(1038.0 - eff_total_w, x_center - eff_total_w * 0.5))
                    cur_y = y_base + li * lh + dy_ln

                    for wtxt, ws, we, sp, adv, act_pulse in word_renders:
                        eff_adv = adv * fit_k
                        wcx = cur_x + eff_adv * 0.5
                        paste_subpixel(
                            comp_im, sp, wcx, cur_y,
                            scale=sc_ln * fit_k * act_pulse,
                            opacity=op_ln,
                            blur_px=bl_ln
                        )
                        cur_x += eff_adv + gap * fit_k
                break

        # 6. Packaging-Matched Romance VIP • Hằng Thu Closing Ribbon (62.30 - 67.48s — Explicit Entrance & Exit!)
        if 62.30 <= t <= 67.48:
            u_c_in  = ease_out_quart(min(1.0, (t - 62.30) / 0.40))
            u_c_out = quintic_smooth(min(1.0, (67.48 - t) / 0.36))
            op_c    = min(quintic_smooth(min(1.0, (t - 62.30) / 0.30)), u_c_out)
            dy_c    = (1.0 - u_c_in) * 18.0 + (1.0 - u_c_out) * 14.0
            sc_c    = (0.94 + 0.06 * u_c_in) * (0.95 + 0.05 * u_c_out)
            bl_c    = (1.0 - u_c_in) * 2.5 + (1.0 - u_c_out) * 2.5
            paste_subpixel(comp_im, cta_card_cached, 540.0, 1812.0 + dy_c, scale=sc_c, opacity=op_c, blur_px=bl_c)

        # 7. Subtle Legal Disclaimer Bar at Bottom
        bar_bot = Image.new("RGBA", (W, 46), (26, 16, 24, 148))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 46))
        paste_subpixel(comp_im, legal_sp, 540.0, H - 23.0, scale=1.0, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"ddvs_v2_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/2028 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close()
        writer.wait()
    reader_a.close()
    reader_m.stdout.close()
    reader_m.wait()

    if tail_from is not None and not test_mode:
        merged_tmp = os.path.join(PROJ_DIR, "_ddvs_v2_merged_tmp.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", raw_vid_out, "-i", tail_vid_out,
            "-filter_complex", f"[0:v]trim=start_frame=0:end_frame={tail_from},setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[vout]",
            "-map", "[vout]", "-r", "30", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            merged_tmp
        ], check=True)
        os.replace(merged_tmp, raw_vid_out)
        print(f"Patched tail from frame {tail_from} -> {frame_idx} into {raw_vid_out}!")

    if test_mode and test_saved:
        imgs = [Image.open(p).resize((360, 640), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (360 * 3, 640 * 3))
        for i, im in enumerate(imgs[:9]):
            grid.paste(im, ((i % 3) * 360, (i // 3) * 640))
        gp = os.path.join(CHECK_DIR, "ddvs_v2_pro_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved ddvs_v2_pro_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM DDVS V2 Pro video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
