import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_V2  = os.path.join(PROJ_DIR, "media_v2")
MEDIA_V3  = os.path.join(PROJ_DIR, "media_v3")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

FONT_BRAND_SERIF = r"C:\Windows\Fonts\timesbd.ttf"  # 1:1 match with physical LT PLUS HẰNG THU box!
FONT_SANS_BOLD   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-Bold.ttf"
FONT_SANS_XBOLD  = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-ExtraBold.ttf"
FONT_EDIT_ITALIC = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\PlayfairDisplay-BoldItalic.ttf"
FONT_CAP         = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-Bold.ttf"
FONT_SUB         = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-Medium.ttf"

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
    u = clamp01(u)
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

def ease_out_quart(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 4.0

def text_in_out_anim(t, t0, t1, d_in=0.34, d_out=0.36, rise_in=18.0, drift_out=-13.0):
    """
    Universal Entrance + Exit Animation for EVERY text element!
    Returns (opacity, dy_offset, scale_mult, blur_px).
    """
    if t <= t0 or t >= t1:
        return 0.0, 0.0, 1.0, 0.0
    op = 1.0
    dy = 0.0
    sc = 1.0
    bl = 0.0
    if (t - t0) < d_in:
        u_in = ease_out_quart((t - t0) / max(0.04, d_in))
        op *= u_in
        dy += (1.0 - u_in) * rise_in
        sc *= (0.91 + 0.09 * u_in)
        bl = max(bl, (1.0 - u_in) * 4.2)
    if (t1 - t) < d_out:
        u_out = quintic_smooth((t1 - t) / max(0.04, d_out))
        op *= u_out
        dy += (1.0 - u_out) * drift_out
        sc *= (0.94 + 0.06 * u_out)
        bl = max(bl, (1.0 - u_out) * 3.6)
    return op, dy, sc, bl

def smooth_env(t, t0, t1, d_in=0.45, d_out=0.42):
    if t <= t0 or t >= t1:
        return 0.0
    a_in = quintic_smooth((t - t0) / max(0.05, d_in)) if (t - t0) < d_in else 1.0
    a_out = quintic_smooth((t1 - t) / max(0.05, d_out)) if (t1 - t) < d_out else 1.0
    return min(a_in, a_out)

def fit_cover_subpixel(rgb_arr, target_w, target_h, zoom=1.0, pan_x=0.0, pan_y=0.0):
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    inv_s = 1.0 / base_scale
    cx_src = sw * 0.5 + pan_x * sw
    cy_src = sh * 0.5 + pan_y * sh
    a = inv_s
    c = min(max(0.0, cx_src - (target_w * 0.5) * inv_s), max(0.0, float(sw) - target_w * inv_s))
    e = inv_s
    f = min(max(0.0, cy_src - (target_h * 0.5) * inv_s), max(0.0, float(sh) - target_h * inv_s))
    im = Image.fromarray(rgb_arr, "RGB")
    return im.transform((target_w, target_h), Image.Transform.AFFINE, (a, 0.0, c, 0.0, e, f), resample=Image.Resampling.BICUBIC)

def fit_wide_preserve_subpixel(rgb_arr, target_w, target_h, zoom=1.02, cy_offset=0.0):
    """Preserves full 16:9 horizontal width (zero left/right cropping of bottles or two-shots!) over a seamless living blurred video backdrop."""
    bg = fit_cover_subpixel(rgb_arr, target_w, target_h, zoom=1.06).filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
    sh, sw = rgb_arr.shape[:2]
    fg_scale = (target_w / float(sw)) * zoom
    fg_w = target_w
    fg_h = min(target_h, int(round(sh * fg_scale)))
    inv_s = 1.0 / fg_scale
    c = sw * 0.5 - (fg_w * 0.5) * inv_s
    f = sh * 0.5 - (fg_h * 0.5) * inv_s
    fg_im = Image.fromarray(rgb_arr, "RGB").transform((fg_w, fg_h), Image.Transform.AFFINE, (inv_s, 0.0, c, 0.0, inv_s, f), resample=Image.Resampling.BICUBIC)
    # Soft vertical feather so top/bottom blend seamlessly into the living backdrop
    yy = np.arange(fg_h, dtype=np.float32)
    fb = 46.0
    m_top = np.clip(yy / fb, 0.0, 1.0)
    m_bot = np.clip((fg_h - 1.0 - yy) / fb, 0.0, 1.0)
    m_v = np.minimum(m_top, m_bot)
    m_v = (m_v * m_v * (3.0 - 2.0 * m_v))[:, None]
    fg_rgba = Image.fromarray(np.dstack([np.array(fg_im), np.broadcast_to((m_v * 255.0).astype(np.uint8), (fg_h, fg_w))]), "RGBA")
    paste_subpixel(bg, fg_rgba, target_w * 0.5, target_h * 0.5 + cy_offset, scale=1.0, opacity=1.0)
    return bg.convert("RGB")

def paste_subpixel(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0, blur_px=0.0):
    if opacity <= 0.008 or scale <= 0.02:
        return
    im = sprite_im
    if blur_px >= 0.50:
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
# 1. BRIGHT POLISH + NATURAL EDGE-PRESERVING SMOOTH SKIN ON SPEAKER!
# ======================================================================
def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.95) * 1.018, 0.0, 1.0)
    lr = np.clip(y * 255.0 * 1.016, 0, 255).astype(np.uint8)
    lg = np.clip(y * 255.0 * 1.006, 0, 255).astype(np.uint8)
    lb = np.clip(y * 255.0 * 0.998, 0, 255).astype(np.uint8)
    return lr, lg, lb

BRIGHT_LUT = _build_bright_lut()

def beauty_polish_speaker(rgb_raw, matte_f32):
    """
    Applies bright studio color lift + edge-preserving porcelain skin smoothing on the
    speaker's face, neck & arms while keeping eyes, eyebrows, lips, hair & pink box 100% sharp!
    """
    rgb = np.empty_like(rgb_raw)
    rgb[:, :, 0] = BRIGHT_LUT[0][rgb_raw[:, :, 0]]
    rgb[:, :, 1] = BRIGHT_LUT[1][rgb_raw[:, :, 1]]
    rgb[:, :, 2] = BRIGHT_LUT[2][rgb_raw[:, :, 2]]

    # Crop ROI where speaker's skin appears (y=560..1680, x=60..1040) for fast processing
    roi = rgb[560:1680, 60:1040]
    m_roi = matte_f32[560:1680, 60:1040]
    roi_im = Image.fromarray(roi, "RGB")
    blur_arr = np.array(roi_im.filter(ImageFilter.GaussianBlur(radius=5.2)), dtype=np.float32)
    roi_f = roi.astype(np.float32)

    r, g, b = roi_f[:, :, 0], roi_f[:, :, 1], roi_f[:, :, 2]
    # Exclude pink box on lower right (pink box has high B close to R; human warm skin has R > G > B and G - B > 8)
    is_skin = (
        (m_roi > 0.45) &
        (r > 130.0) & (g > 92.0) & (b > 70.0) &
        ((r - b) > 22.0) & ((g - b) > 6.0)
    )
    # Edge preservation: zero smoothing on eyes, brows, lips, nostrils, pinstripes!
    diff = np.mean(np.abs(roi_f - blur_arr), axis=2)
    edge_preserve = np.clip(1.0 - (diff - 5.0) / 15.0, 0.0, 1.0)
    w_smooth = (is_skin.astype(np.float32) * edge_preserve * 0.58)[:, :, None]

    # Subtle rosy-porcelain glow (+2.2% soft lift on smoothed skin)
    smoothed = roi_f * (1.0 - w_smooth) + np.clip(blur_arr * 1.022, 0.0, 255.0) * w_smooth
    rgb[560:1680, 60:1040] = smoothed.astype(np.uint8)
    return rgb

# ======================================================================
# 2. TEXT & BRAND LOGO SPRITE RENDERER
# ======================================================================
_sprite_cache = {}
def render_pro_text_sprite(text, font_path, size, top_col, bot_col=None, stroke_col=(255, 255, 255), stroke_w=6, glow_col=None, glow_rad=8, shadow_alpha=90, extrude_col=None):
    bot_col = bot_col or top_col
    key = ("v3", text, font_path, int(round(size)), top_col, bot_col, stroke_col, stroke_w, glow_col, int(round(glow_rad)), shadow_alpha, extrude_col)
    if key in _sprite_cache:
        return _sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(max(glow_rad * 2.5, 10) + stroke_w + 14)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    if glow_col and glow_rad > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(0, stroke_w // 2), stroke_fill=255)
        g1 = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad * 0.8)), dtype=np.float32)
        g2 = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad * 1.8)), dtype=np.float32)
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0] = glow_col[0]; ga[:, :, 1] = glow_col[1]; ga[:, :, 2] = glow_col[2]
        ga[:, :, 3] = np.clip(g1 * 0.62 + g2 * 0.35, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 4), text, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)
        sm_b = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5.0)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0] = 14; sa[:, :, 1] = 18; sa[:, :, 2] = 30
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

    if len(_sprite_cache) > 800:
        _sprite_cache.clear()
    _sprite_cache[key] = base
    return base

def draw_animated_glass_tag(canvas_im, label_txt, t, t0, t1, cx=540.0, cy=58.0, accent_rgb=(228, 38, 72)):
    op, dy, sc, bl = text_in_out_anim(t, t0, t1, d_in=0.36, d_out=0.36, rise_in=-14.0, drift_out=-12.0)
    if not label_txt or op <= 0.01:
        return
    sp = render_pro_text_sprite(label_txt, FONT_SANS_BOLD, 23, (255, 255, 255), stroke_w=0, shadow_alpha=35)
    pw, ph = sp.width + 44, 46
    tag = Image.new("RGBA", (pw + 12, ph + 12), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle([6, 6, 6 + pw, 6 + ph], radius=23, fill=(22, 20, 30, 172), outline=(255, 255, 255, 198), width=2)
    td.ellipse([18, 6 + ph // 2 - 5, 28, 6 + ph // 2 + 5], fill=(*accent_rgb, 255))
    paste_subpixel(tag, sp, 6 + pw * 0.5 + 8, 6 + ph * 0.5, scale=1.0, opacity=1.0)
    paste_subpixel(canvas_im, tag, cx, cy + dy, scale=sc, opacity=op, blur_px=bl)

# ======================================================================
# 3. FIVE DISTINCT REAL-VIDEO OVERLAY STYLES (100% VIDEO, ZERO WALL GAPS!)
# ======================================================================
_feather_mask_cache = {}
def get_soft_arch_mask(vw, vh, feather_bot=115):
    k = (vw, vh, feather_bot)
    if k not in _feather_mask_cache:
        yy = np.arange(vh, dtype=np.float32)[:, None]
        alpha = np.ones((vh, vw), dtype=np.float32)
        if feather_bot > 0:
            u = np.clip((vh - yy) / float(feather_bot), 0.0, 1.0)
            alpha *= u * u * (3.0 - 2.0 * u)
        _feather_mask_cache[k] = Image.fromarray((alpha * 255.0).astype(np.uint8), "L")
    return _feather_mask_cache[k]

def draw_living_video_backdrop(canvas_im, vf_rgb, opacity=1.0, blur_rad=18, tint_rgba=(250, 244, 248, 78)):
    if opacity <= 0.005:
        return
    vw, vh = 1080, 920
    im = fit_cover_subpixel(vf_rgb, vw, vh, zoom=1.04).filter(ImageFilter.GaussianBlur(radius=blur_rad)).convert("RGBA")
    if tint_rgba:
        im = Image.alpha_composite(im, Image.new("RGBA", (vw, vh), tint_rgba))
    mask = get_soft_arch_mask(vw, vh, feather_bot=125)
    arr = np.array(im)
    arr[:, :, 3] = (np.array(mask, dtype=np.float32) * clamp01(opacity)).astype(np.uint8)
    paste_subpixel(canvas_im, Image.fromarray(arr, "RGBA"), 540.0, 460.0, scale=1.0, opacity=1.0)

def render_style1_fullbleed_video(canvas_im, vf_rgb, env, u_prog, zoom_from=1.04, zoom_to=1.00, pan_y=-0.015, preserve_wide=False, cy_offset=0.0):
    if env <= 0.005:
        return
    vw, vh = 1080, 920
    z = zoom_from + (zoom_to - zoom_from) * u_prog
    if preserve_wide:
        crop = fit_wide_preserve_subpixel(vf_rgb, vw, vh, zoom=z, cy_offset=cy_offset).convert("RGBA")
    else:
        crop = fit_cover_subpixel(vf_rgb, vw, vh, zoom=z, pan_y=pan_y).convert("RGBA")
    mask = get_soft_arch_mask(vw, vh, feather_bot=120)
    arr = np.array(crop)
    arr[:, :, 3] = (np.array(mask, dtype=np.float32) * clamp01(env)).astype(np.uint8)
    paste_subpixel(canvas_im, Image.fromarray(arr, "RGBA"), 540.0, 460.0, scale=1.0, opacity=1.0)

def render_style2_diagonal_wipe_videos(canvas_im, vf1_rgb, vf2_rgb, t, st, t_split, en, env):
    if env <= 0.005:
        return
    amb = vf1_rgb if t < t_split else vf2_rgb
    draw_living_video_backdrop(canvas_im, amb, opacity=env, blur_rad=20)

    vw, vh = 1024, 816
    u1 = quintic_smooth((t - st) / max(0.2, en - st))
    im1 = fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.01 + 0.04 * u1, pan_y=-0.015)

    if t <= t_split - 0.38:
        blended = np.array(im1)
    elif t >= t_split + 0.38:
        u2 = quintic_smooth((t - (t_split - 0.38)) / max(0.2, en - t_split + 0.38))
        im2 = fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.04 - 0.03 * u2, pan_y=-0.015)
        blended = np.array(im2)
    else:
        u_w = quintic_smooth((t - (t_split - 0.38)) / 0.76)
        im2 = fit_cover_subpixel(vf2_rgb, vw, vh, zoom=1.03, pan_y=-0.015)
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
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    rmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=rad, fill=255)
    art = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    art.paste(Image.fromarray(blended, "RGB"), (20, 18), mask=rmask)
    card = Image.alpha_composite(card, art)
    ImageDraw.Draw(card).rounded_rectangle([20, 18, 20 + vw - 1, 18 + vh - 1], radius=rad, outline=(255, 244, 232, 225), width=2)

    paste_subpixel(canvas_im, card, 540.0 + (1.0 - env) * (-34.0), 452.0, scale=0.96 + 0.04 * env, opacity=env)

def render_style3_glassmorphic_videos(canvas_im, vf1_rgb, vf2_rgb, t, st, t_morph, en, env):
    if env <= 0.005:
        return
    amb = vf1_rgb if t < t_morph else vf2_rgb
    draw_living_video_backdrop(canvas_im, amb, opacity=env, blur_rad=20, tint_rgba=(242, 248, 252, 85))

    vw, vh = 984, 776
    pad_g = 18
    gw, gh = vw + pad_g * 2, vh + pad_g * 2

    u_all = quintic_smooth((t - st) / max(0.2, en - st))
    if t <= t_morph - 0.38:
        v_arr = np.array(fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.01 + 0.04 * u_all))
    elif t >= t_morph + 0.38:
        u2 = quintic_smooth((t - (t_morph - 0.38)) / max(0.2, en - t_morph + 0.38))
        v_arr = np.array(fit_wide_preserve_subpixel(vf2_rgb, vw, vh, zoom=1.04 - 0.03 * u2, cy_offset=12.0))
    else:
        um = quintic_smooth((t - (t_morph - 0.38)) / 0.76)
        a1 = np.array(fit_cover_subpixel(vf1_rgb, vw, vh, zoom=1.03), dtype=np.float32)
        a2 = np.array(fit_wide_preserve_subpixel(vf2_rgb, vw, vh, zoom=1.03, cy_offset=12.0), dtype=np.float32)
        v_arr = np.clip(a1 * (1.0 - um) + a2 * um, 0, 255).astype(np.uint8)

    cw, ch = gw + 40, gh + 40
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 24, 20 + gw, 24 + gh], radius=44, fill=(16, 24, 38, 82))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    glass = Image.new("RGBA", (gw, gh), (255, 255, 255, 168))
    gmask = Image.new("L", (gw, gh), 0)
    ImageDraw.Draw(gmask).rounded_rectangle([0, 0, gw - 1, gh - 1], radius=44, fill=255)
    glayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    glayer.paste(glass, (20, 20), mask=gmask)
    card = Image.alpha_composite(card, glayer)
    ImageDraw.Draw(card).rounded_rectangle([20, 20, 20 + gw - 1, 20 + gh - 1], radius=44, outline=(255, 255, 255, 238), width=2)

    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=30, fill=255)
    vlayer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vlayer.paste(Image.fromarray(v_arr, "RGB"), (20 + pad_g, 20 + pad_g), mask=vmask)
    card = Image.alpha_composite(card, vlayer)

    paste_subpixel(canvas_im, card, 540.0, 452.0 + (1.0 - env) * 22.0 + math.sin((t - st) * 1.2) * 3.0, scale=0.96 + 0.04 * env, opacity=env)

def render_style4_staggered_dual_pip(canvas_im, vf_left_rgb, vf_right_rgb, t, st1, st2, en, env):
    if env <= 0.005:
        return
    draw_living_video_backdrop(canvas_im, vf_left_rgb, opacity=env, blur_rad=22, tint_rgba=(240, 248, 252, 110))

    def make_pip(v_rgb, pw, ph, zoom_v, pan_x=0.0):
        im = fit_cover_subpixel(v_rgb, pw, ph, zoom=zoom_v, pan_x=pan_x)
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
        ImageDraw.Draw(c).rounded_rectangle([18, 16, 18 + pw - 1, 16 + ph - 1], radius=30, outline=(255, 255, 255, 238), width=3)
        return c

    u1 = ease_out_quart(min(1.0, max(0.0, t - st1) / 0.50))
    p1 = make_pip(vf_left_rgb, 690, 470, 1.00, pan_x=0.22)
    u2_shift = quintic_smooth((t - st2) / 0.55) if t >= st2 else 0.0
    paste_subpixel(canvas_im, p1, 448.0 - 70.0 * u2_shift - (1.0 - u1) * 44.0, 332.0 - 20.0 * u2_shift, scale=0.93 + 0.07 * u1, opacity=u1 * env)

    if t >= st2:
        u2 = ease_out_quart(min(1.0, (t - st2) / 0.50))
        p2 = make_pip(vf_right_rgb, 620, 435, 1.03)
        paste_subpixel(canvas_im, p2, 712.0 + (1.0 - u2) * 50.0, 625.0 + (1.0 - u2) * 24.0, scale=0.91 + 0.09 * u2, opacity=u2 * env)

def render_style5_gold_rimmed_product_video(canvas_im, vf_rgb, t, st, en, env, radius=44, preserve_wide=False):
    if env <= 0.005:
        return
    draw_living_video_backdrop(canvas_im, vf_rgb, opacity=env, blur_rad=20, tint_rgba=(255, 238, 245, 72))

    vw, vh = 1036, 840
    u = quintic_smooth((t - st) / max(0.2, en - st))
    if preserve_wide:
        im = fit_wide_preserve_subpixel(vf_rgb, vw, vh, zoom=1.00 + 0.04 * u, cy_offset=8.0).convert("RGBA")
    else:
        im = fit_cover_subpixel(vf_rgb, vw, vh, zoom=1.00 + 0.04 * u).convert("RGBA")

    # Sweeping optical golden light sheen
    yy, xx = np.ogrid[0:vh, 0:vw]
    diag = (xx.astype(np.float32) * 0.8 + yy.astype(np.float32) * 0.45) / (vw * 0.8 + vh * 0.45)
    sweep_pos = -0.25 + 1.50 * quintic_smooth(min(1.0, max(0.0, t - st) / 2.6))
    sheen = np.exp(-((diag - sweep_pos) ** 2) / 0.008) * 32.0
    arr = np.array(im, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + sheen * 1.1, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + sheen * 0.95, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + sheen * 0.85, 0, 255)

    cw, ch = vw + 36, vh + 40
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 22, 18 + vw, 22 + vh], radius=radius, fill=(55, 22, 36, 84))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    rm = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=radius, fill=255)
    al = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    al.paste(Image.fromarray(arr.astype(np.uint8), "RGBA"), (18, 16), mask=rm)
    card = Image.alpha_composite(card, al)
    ImageDraw.Draw(card).rounded_rectangle([18, 16, 18 + vw - 1, 16 + vh - 1], radius=radius, outline=(*BRAND_GOLD, 240), width=3)

    paste_subpixel(canvas_im, card, 540.0, 452.0 + (1.0 - env) * (-20.0), scale=0.96 + 0.04 * env, opacity=env)

# ======================================================================
# 4. SHIMMERING IRIDESCENT PEARL BUBBLES (WITH IN & OUT ANIMATION!)
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

    bubbles = [
        (33.66, "Hoàng Bá",      156, (255, 196, 125), 132.0, 238.0, 0.0),
        (34.68, "Ích Mẫu",       152, (255, 158, 192), 948.0, 228.0, 1.1),
        (35.12, "Kim Ngân\nHoa", 162, (255, 212, 138), 124.0, 482.0, 2.2),
        (36.16, "Trà Xanh",      150, (142, 236, 188), 962.0, 412.0, 3.3),
        (37.00, "Trầu Không",    158, (135, 228, 212), 148.0, 725.0, 4.4),
        (37.70, "Acid\nLactic",  154, (152, 208, 255), 952.0, 752.0, 5.5),
    ]

    out_env = quintic_smooth((t_end - t_now) / 0.45) if (t_end - t_now) < 0.45 else 1.0
    micro_layer = Image.new("RGBA", (W, 920), (0, 0, 0, 0))
    md = ImageDraw.Draw(micro_layer)
    for mi in range(14):
        phase = (t_now * (0.26 + (mi % 4) * 0.06) + mi * 0.37) % 1.0
        mx = 95.0 + (mi * 71.0) % 890.0 + math.sin(t_now * 1.8 + mi) * 14.0
        my = 840.0 - phase * 740.0
        mr = 5 + (mi % 4) * 3
        ma = int(155 * math.sin(phase * math.pi) * out_env)
        if ma > 8:
            md.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 250, 253, ma), outline=(255, 255, 255, min(255, ma + 40)))
    canvas_im.alpha_composite(micro_layer, dest=(0, 0))

    for idx_b, (st_b, lbl, diam, tint, tx, ty, seed) in enumerate(bubbles):
        # Staggered exit too! Each bubble gracefully floats up & dissolves out at the end!
        en_b = t_end - (5 - idx_b) * 0.04
        if t_now < st_b or t_now >= en_b:
            continue
        op, dy_anim, sc_anim, bl_anim = text_in_out_anim(t_now, st_b, en_b, d_in=0.52, d_out=0.45, rise_in=115.0, drift_out=-42.0)
        dt = t_now - st_b
        bx = tx + math.sin(dt * 1.65 + seed) * 8.5
        by = ty + dy_anim + math.cos(dt * 1.35 + seed) * 7.0
        sc = sc_anim * (1.0 + 0.025 * math.sin(dt * 2.4 + seed))
        bsp = get_iridescent_bubble_sprite(lbl, diam, tint)
        paste_subpixel(canvas_im, bsp, bx, by, scale=sc, opacity=op, blur_px=bl_anim * 0.6)

# ======================================================================
# 5. TRANSLUCENT PACKAGING-MATCHED BRAND BADGE OVER REAL FINALE VIDEO!
# ======================================================================
_compact_badge = None
def get_compact_finale_brand_badge():
    global _compact_badge
    if _compact_badge is not None:
        return _compact_badge
    pw, ph = 860, 152
    cw, ch = pw + 36, ph + 36
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 22, 18 + pw, 22 + ph], radius=38, fill=(48, 14, 28, 88))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    bg = Image.new("RGBA", (pw, ph), (*BRAND_PINK_BG1, 232))
    rd = ImageDraw.Draw(bg)
    rd.line([(0, 20), (140, ph)], fill=(235, 172, 118, 135), width=3)
    rd.line([(pw, 20), (pw - 140, ph)], fill=(235, 172, 118, 135), width=3)
    rm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=36, fill=255)
    bl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bl.paste(bg, (18, 16), mask=rm)
    card = Image.alpha_composite(card, bl)
    ImageDraw.Draw(card).rounded_rectangle([18, 16, 18 + pw - 1, 16 + ph - 1], radius=36, outline=(255, 255, 255, 245), width=3)
    ImageDraw.Draw(card).rounded_rectangle([22, 20, 14 + pw, 12 + ph], radius=33, outline=(*BRAND_GOLD, 195), width=2)

    sp1 = render_pro_text_sprite("VIÊN ĐẶT PHỤ KHOA", FONT_BRAND_SERIF, 21, (42, 14, 20), stroke_w=0, shadow_alpha=0)
    sp2 = render_pro_text_sprite("LT PLUS HẰNG THU", FONT_BRAND_SERIF, 58, BRAND_RED_TOP, BRAND_RED_BOT, stroke_col=(255, 248, 250), stroke_w=3, shadow_alpha=30, extrude_col=BRAND_EXTRUDE)
    paste_subpixel(card, sp1, cw * 0.5, 16 + 34, scale=1.0, opacity=1.0)
    paste_subpixel(card, sp2, cw * 0.5, 16 + 98, scale=1.0, opacity=1.0)
    _compact_badge = card
    return card

# ======================================================================
# 6. COMFORTABLE READABLE SUBTITLES (1.8s - 3.4s HOLD + IN/OUT ANIMATION!)
# ======================================================================
def load_captions_v3_readable():
    """
    Groups words into comfortable, easy-to-read semantic phrases of 6..10 words (2 balanced lines),
    holding each phrase on screen for 1.8s..3.5s so the viewer NEVER misses a single word!
    """
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if (w["start"] + w["end"]) * 0.5 >= 3.85
    ]

    # Step 1: Build semantic phrases of 6..10 words, breaking only at natural pauses/punctuation when >= 5 words!
    raw_phrases = []
    cur = []
    for idx, w in enumerate(words):
        txt = w["word"].strip()
        if not txt:
            continue
        if cur:
            gap = w["start"] - cur[-1][2]
            dur_so_far = cur[-1][2] - cur[0][1]
            # Always flush at sentence end (.?!), or pause >= 0.42s with >= 4 words, or >= 9 words
            prev_punct = bool(re.search(r"[.?!]$", cur[-1][0]))
            comma_punct = bool(re.search(r"[,;:]$", cur[-1][0]))
            if prev_punct or (gap >= 0.42 and len(cur) >= 4) or (comma_punct and len(cur) >= 6) or len(cur) >= 9 or (dur_so_far >= 2.7 and len(cur) >= 6):
                raw_phrases.append(cur)
                cur = []
        cur.append([txt, round(w["start"], 3), round(w["end"], 3)])
    if cur:
        raw_phrases.append(cur)

    # Merge any tiny orphan phrase (< 4 words or < 1.3s) into its neighbor so NOTHING flashes fast,
    # UNLESS the previous phrase ended with a full sentence period/question mark!
    merged = []
    for p in raw_phrases:
        prev_ended_sent = bool(merged and re.search(r"[.?!]$", merged[-1][-1][0]))
        if merged and not prev_ended_sent and (len(p) < 4 or (p[-1][2] - p[0][1]) < 1.25) and len(merged[-1]) + len(p) <= 12:
            merged[-1].extend(p)
        else:
            merged.append(p)
    # Also check forward merge if first/middle phrase is short (only within same sentence!)
    final_phrases = []
    i = 0
    while i < len(merged):
        p = merged[i]
        ended_sent = bool(re.search(r"[.?!]$", p[-1][0]))
        if not ended_sent and (len(p) < 4 or (p[-1][2] - p[0][1]) < 1.35) and i + 1 < len(merged) and len(p) + len(merged[i + 1]) <= 11:
            final_phrases.append(p + merged[i + 1])
            i += 2
        else:
            final_phrases.append(p)
            i += 1

    # Split each phrase into 1 or 2 visually balanced lines!
    cap_groups = []
    for idx, p in enumerate(final_phrases):
        if len(p) <= 4 and sum(len(x[0]) for x in p) <= 18:
            lines = [p]
        else:
            # Find split point closest to 50% character length
            tot_chars = sum(len(x[0]) + 1 for x in p)
            best_k, best_diff = 1, 999
            acc = 0
            for k in range(1, len(p)):
                acc += len(p[k - 1][0]) + 1
                diff = abs(acc - tot_chars * 0.5)
                if diff < best_diff:
                    best_diff = diff
                    best_k = k
            lines = [p[:best_k], p[best_k:]]

        t0 = max(3.88, p[0][1] - 0.08)
        nxt_t0 = (final_phrases[idx + 1][0][1] - 0.08) if idx + 1 < len(final_phrases) else 59.08
        # Hold comfortably after last word (up to +0.65s if pause allows) without overlapping next group!
        t1 = min(nxt_t0 - 0.02, max(p[-1][2] + 0.42, t0 + 1.75))
        if t1 <= p[-1][2] + 0.18:
            t1 = min(nxt_t0, p[-1][2] + 0.22)
        cap_groups.append({"t0": round(t0, 3), "t1": round(t1, 3), "lines": lines})

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
    return cap_groups, BRAND_WORDS, GOLD_WORDS, ROSE_WORDS

ZOOM_KEYS = [
    (0.00, 1.010),
    (3.98, 1.040),
    (10.80, 1.018),
    (17.05, 1.045),
    (23.20, 1.022),
    (30.84, 1.046),
    (41.55, 1.020),
    (45.88, 1.046),
    (50.20, 1.022),
    (59.18, 1.012),
]

def get_butter_zoom(t):
    if t <= ZOOM_KEYS[0][0]:
        return ZOOM_KEYS[0][1]
    for i in range(1, len(ZOOM_KEYS)):
        t0, z0 = ZOOM_KEYS[i - 1]
        t1, z1 = ZOOM_KEYS[i]
        if t <= t1:
            u = quintic_smooth(min(1.0, (t - t0) / min(1.0, max(0.4, (t1 - t0) * 0.45))))
            return z0 + (z1 - z0) * u
    return ZOOM_KEYS[-1][1]

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
    dry_subs  = "--subs" in sys.argv

    cap_groups, BRAND_WORDS, GOLD_WORDS, ROSE_WORDS = load_captions_v3_readable()
    if dry_subs:
        print(f"Total readable subtitle groups: {len(cap_groups)}")
        for idx, g in enumerate(cap_groups):
            dur = g["t1"] - g["t0"]
            txt = " / ".join(" ".join(w[0] for w in ln) for ln in g["lines"])
            print(f"  [{idx:02d}] {g['t0']:5.2f}s -> {g['t1']:5.2f}s (dur={dur:4.2f}s) | {txt}")
        return

    test_frames = {
        int(round(ts * FPS))
        for ts in [1.60, 5.50, 8.80, 14.50, 19.80, 28.20, 38.20, 43.80, 48.00, 55.20]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    # Load all 9 REAL Muse Videos + 2 Medical/Lab Flow Videos!
    clip_paths = {
        "hook":          os.path.join(MEDIA_V3, "MUSE_char_hook.mp4"),
        "disc1":         os.path.join(MEDIA_V3, "MUSE_char_disc1.mp4"),
        "disc2":         os.path.join(MEDIA_V3, "MUSE_char_disc2.mp4"),
        "med_cells":     os.path.join(MEDIA_V2, "v2_med_cells.mp4"),
        "reassure":      os.path.join(MEDIA_V3, "MUSE_char_reassure.mp4"),
        "doc_eval":      os.path.join(MEDIA_V3, "MUSE_char_doc_eval.mp4"),
        "lab_micro":     os.path.join(MEDIA_V2, "v2_lab_micro.mp4"),
        "prod_hydrogel": os.path.join(MEDIA_V3, "MUSE_prod_hydrogel.mp4"),
        "prod_openbox":  os.path.join(MEDIA_V3, "MUSE_prod_openbox.mp4"),
        "prod_luxury":   os.path.join(MEDIA_V3, "MUSE_prod_luxury.mp4"),
        "prod_finale":   os.path.join(MEDIA_V3, "MUSE_prod_finale.mp4"),
    }
    clips = {}
    for k, vp in clip_paths.items():
        if os.path.exists(vp):
            clips[k] = load_vid_frames_wh(vp, 1280, 720)
            print(f"Loaded REAL video {k}: {len(clips[k])} frames")
        else:
            print(f"WARNING missing {vp}")

    legal_sp = render_pro_text_sprite(
        "Sản phẩm chăm sóc phụ khoa • Đọc kỹ hướng dẫn sử dụng trước khi dùng",
        FONT_SUB, 20, (250, 248, 250), stroke_col=(28, 18, 28), stroke_w=3, shadow_alpha=0
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_htpm_lt_v3_video_only.mp4")
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

        matte = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W)).astype(np.float32) / 255.0
        # Smooth radiant porcelain skin polish on speaker!
        rgb = beauty_polish_speaker(rgb_raw, matte)
        t = frame_idx / FPS

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

        # ==================================================================
        # OVERLAPPING 100% REAL AI VIDEO OVERLAYS (ZERO STATIC IMAGES, ZERO WALL FLASH!)
        # ==================================================================
        # 1. Hook (0.00 .. 4.30s)
        e_hk = 1.0 if t < 3.85 else quintic_smooth((4.30 - t) / 0.45)
        if e_hk > 0.005:
            u_hk = quintic_smooth(min(1.0, t / 4.0))
            render_style1_fullbleed_video(comp_im, get_clip_frame(clips, "hook", t), e_hk, u_hk, zoom_from=1.05, zoom_to=1.00)
            draw_animated_glass_tag(comp_im, "TÂM LÝ KHI NGHE KẾT LUẬN LỘ TUYẾN", t, 0.12, 3.92, accent_rgb=(238, 42, 82))

        # 2. Discomfort Dual Videos (3.85 .. 11.15s) — Style 2 Diagonal Wipe
        e_d = smooth_env(t, 3.85, 11.15, d_in=0.45, d_out=0.45)
        if e_d > 0.005:
            render_style2_diagonal_wipe_videos(
                comp_im,
                get_clip_frame(clips, "disc1", t - 3.85),
                get_clip_frame(clips, "disc2", max(0.0, t - 6.80)),
                t, 3.85, 7.18, 11.15, e_d
            )
            draw_animated_glass_tag(comp_im, "SINH HOẠT THIẾU THOẢI MÁI", t, 4.00, 7.12, accent_rgb=(235, 85, 115))
            draw_animated_glass_tag(comp_im, "LO LẮNG TÌNH TRẠNG NGHIÊM TRỌNG HƠN", t, 7.20, 10.75, accent_rgb=(235, 85, 115))

        # 3. Medical Understanding + Doctor Reassure Videos (10.70 .. 23.50s) — Style 3 Glassmorphism Morph
        e_m = smooth_env(t, 10.70, 23.50, d_in=0.45, d_out=0.45)
        if e_m > 0.005:
            render_style3_glassmorphic_videos(
                comp_im,
                get_clip_frame(clips, "med_cells", t - 10.70),
                get_clip_frame(clips, "reassure", max(0.0, t - 16.65)),
                t, 10.70, 17.05, 23.50, e_m
            )
            draw_animated_glass_tag(comp_im, "HIỂU ĐÚNG: TẾ BÀO TUYẾN HIỆN DIỆN MẶT NGOÀI", t, 10.85, 16.95, cy=72.0, accent_rgb=(56, 168, 235))
            draw_animated_glass_tag(comp_im, "KHÔNG ĐỒNG NGHĨA NHIỄM TRÙNG / UNG THƯ", t, 17.10, 23.15, cy=72.0, accent_rgb=(46, 188, 148))

        # 4. Staggered Dual-Panel PIP Videos (23.05 .. 31.15s) — Style 4 Doctor Eval + Lab Microscope
        e_p = smooth_env(t, 23.05, 31.15, d_in=0.45, d_out=0.45)
        if e_p > 0.005:
            render_style4_staggered_dual_pip(
                comp_im,
                get_clip_frame(clips, "doc_eval", t - 23.05),
                get_clip_frame(clips, "lab_micro", max(0.0, t - 26.75)),
                t, 23.05, 26.75, 31.15, e_p
            )
            draw_animated_glass_tag(comp_im, "BÁC SĨ ĐÁNH GIÁ NGUYÊN NHÂN", t, 23.22, 26.70, accent_rgb=(42, 185, 148))
            draw_animated_glass_tag(comp_im, "LOẠI TRỪ NHIỄM TRÙNG & BẤT THƯỜNG", t, 26.78, 30.80, accent_rgb=(42, 185, 148))

        # 5. Real Muse Product Video #1: Glossy White Probiotic Cream Stage (30.70 .. 41.85s) — Style 1B
        e_pr1 = smooth_env(t, 30.70, 41.85, d_in=0.45, d_out=0.45)
        if e_pr1 > 0.005:
            u_pr1 = quintic_smooth((t - 30.70) / (41.85 - 30.70))
            render_style1_fullbleed_video(comp_im, get_clip_frame(clips, "prod_hydrogel", t - 30.70), e_pr1, u_pr1, zoom_from=0.98, zoom_to=1.03, preserve_wide=True, cy_offset=10.0)
            draw_animated_glass_tag(comp_im, "VIÊN ĐẶT PHỤ KHOA LT PLUS HẰNG THU", t, 30.88, 41.50, accent_rgb=(238, 38, 72))

        # 6. Real Muse Product Video #2: Open Pink Magnetic Box Orbital Dolly (41.40 .. 46.15s) — Style 5A
        e_pr2 = smooth_env(t, 41.40, 46.15, d_in=0.45, d_out=0.45)
        if e_pr2 > 0.005:
            render_style5_gold_rimmed_product_video(comp_im, get_clip_frame(clips, "prod_openbox", t - 41.40), t, 41.40, 46.15, e_pr2, radius=38)
            draw_animated_glass_tag(comp_im, "HỖ TRỢ CHĂM SÓC ĐÚNG CÁCH & HIỆU QUẢ", t, 41.62, 45.82, accent_rgb=(228, 38, 72))

        # 7. Real Muse Product Video #3: Sunlit Blush Silk & Crystal Pedestal Trio (45.70 .. 50.45s) — Style 5B
        e_pr3 = smooth_env(t, 45.70, 50.45, d_in=0.45, d_out=0.45)
        if e_pr3 > 0.005:
            render_style5_gold_rimmed_product_video(comp_im, get_clip_frame(clips, "prod_luxury", t - 45.70), t, 45.70, 50.45, e_pr3, radius=46, preserve_wide=True)
            draw_animated_glass_tag(comp_im, "LT PLUS NHÀ HẰNG THU CHÍNH HÃNG", t, 45.92, 50.15, accent_rgb=(228, 38, 72))

        # 8. Real Muse Product Video #4: Finale Brand Showcase Video + Animated Brand Badge (50.00 .. 59.20s)
        e_pr4 = smooth_env(t, 50.00, 59.50, d_in=0.45, d_out=0.25)
        if e_pr4 > 0.005:
            u_pr4 = quintic_smooth((t - 50.00) / 9.20)
            render_style1_fullbleed_video(comp_im, get_clip_frame(clips, "prod_finale", t - 50.00), e_pr4, u_pr4, zoom_from=0.98, zoom_to=1.03, preserve_wide=True, cy_offset=58.0)
            # Compact Packaging-Matched LT PLUS HẰNG THU Badge with Entrance & Exit animation!
            op_bd, dy_bd, sc_bd, bl_bd = text_in_out_anim(t, 50.28, 59.05, d_in=0.45, d_out=0.42, rise_in=-22.0, drift_out=-16.0)
            if op_bd > 0.01:
                paste_subpixel(comp_im, get_compact_finale_brand_badge(), 540.0, 108.0 + dy_bd, scale=sc_bd * 0.94, opacity=op_bd, blur_px=bl_bd)

        # Composite real smooth-skin RVM Pharmacist + Desk + Left Plant + Held Pink Box cleanly in FRONT!
        fg_alpha = np.maximum(m_arr, static_fg_guard)
        comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 6 Shimmering Iridescent Crystal-Pearl Herb Bubbles (with In & Out animations!)
        draw_shimmering_herb_bubbles(comp_im, t)

        # Hook Typography (0.08 - 3.85s) — EVERY line has smooth Entrance AND smooth Exit animation!
        if 0.08 <= t <= 3.85:
            for h_txt, h_fnt, h_sz, c1, c2, st_c, st_w, hx, hy, t_in in [
                ("Nghe kết luận lộ tuyến...",        FONT_SANS_BOLD,   40, (255, 255, 255), (235, 242, 255), (18, 28, 48), 6, 505.0, 1108.0, 0.08),
                ("LO LẮNG",                          FONT_SANS_XBOLD,  68, (255, 218, 128), (242, 178, 72),  (24, 18, 32), 7, 295.0, 1206.0, 0.95),
                ("bắt đầu từ đâu?",                  FONT_EDIT_ITALIC, 56, (255, 182, 208), (248, 138, 175), (24, 18, 32), 6, 725.0, 1208.0, 1.35),
                ("Cùng Dược sĩ hiểu đúng trước tiên",FONT_SANS_BOLD,   33, (158, 248, 224), (118, 228, 198), (14, 24, 34), 5, 495.0, 1300.0, 2.15),
            ]:
                op_h, dy_h, sc_h, bl_h = text_in_out_anim(t, t_in, 3.85, d_in=0.36, d_out=0.38, rise_in=18.0, drift_out=-14.0)
                if op_h > 0.01:
                    sp_h = render_pro_text_sprite(h_txt, h_fnt, h_sz, c1, c2, stroke_col=st_c, stroke_w=st_w)
                    paste_subpixel(comp_im, sp_h, hx, hy + dy_h, scale=sc_h, opacity=op_h, blur_px=bl_h)

        # ==================================================================
        # READABLE PHRASE + KARAOKE HIGHLIGHT SUBTITLES (WITH IN & OUT ANIMATION!)
        # ==================================================================
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                op_grp, dy_grp, sc_grp, bl_grp = text_in_out_anim(t, g["t0"], g["t1"], d_in=0.32, d_out=0.36, rise_in=16.0, drift_out=-12.0)
                if op_grp <= 0.01:
                    break

                x_center = 492.0
                cap_sz_base = 44.0
                y_base = (1118.0 if len(g["lines"]) >= 2 else 1146.0) + dy_grp
                lh = 60.0
                gap = 13.0

                for li, ln in enumerate(g["lines"]):
                    items = []
                    total_w = 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_brand = wtxt in BRAND_WORDS
                        is_gold  = wtxt in GOLD_WORDS
                        is_rose  = wtxt in ROSE_WORDS
                        f_use = FONT_BRAND_SERIF if is_brand else FONT_CAP
                        sz_use = cap_sz_base * (1.16 if is_brand else (1.06 if (is_gold or is_rose) else 1.0))

                        # Base readable sprite (visible from phrase Entrance so viewer has full 2-3s reading time!)
                        sp_base = render_pro_text_sprite(
                            wtxt, f_use, sz_use,
                            (246, 250, 255), (228, 236, 246),
                            stroke_col=(14, 20, 34), stroke_w=5, shadow_alpha=80
                        )
                        # Active illuminated sprite when spoken!
                        if is_brand:
                            sp_act = render_pro_text_sprite(
                                wtxt, f_use, sz_use,
                                BRAND_RED_TOP, BRAND_RED_BOT,
                                stroke_col=(255, 248, 244), stroke_w=6,
                                glow_col=(255, 190, 208), glow_rad=8, shadow_alpha=92
                            )
                        else:
                            act_col = (255, 226, 96) if is_gold else ((255, 162, 198) if is_rose else (138, 252, 228))
                            sp_act = render_pro_text_sprite(
                                wtxt, f_use, sz_use,
                                act_col, stroke_col=(14, 20, 34), stroke_w=5,
                                glow_col=act_col, glow_rad=7, shadow_alpha=90
                            )
                        adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(f_use, sz_use))
                        items.append((wtxt, ws, sp_base, sp_act, adv))
                        total_w += adv + (gap if wi > 0 else 0.0)

                    cur_x = max(46.0, min(1034.0 - total_w, x_center - total_w * 0.5))
                    cur_y = y_base + li * lh
                    for wtxt, ws, sp_base, sp_act, adv in items:
                        wcx = cur_x + adv * 0.5
                        u_act = ease_out_quart(clamp01((t - ws + 0.04) / 0.22)) if t >= (ws - 0.04) else 0.0
                        if u_act <= 0.01:
                            paste_subpixel(comp_im, sp_base, wcx, cur_y, scale=sc_grp, opacity=op_grp * 0.90, blur_px=bl_grp)
                        elif u_act >= 0.99:
                            # Subtle gentle pulse right as word activates, then steady crisp hold!
                            dt_a = max(0.0, t - ws)
                            pop_k = 1.0 + 0.06 * math.sin(min(1.0, dt_a / 0.28) * math.pi)
                            paste_subpixel(comp_im, sp_act, wcx, cur_y - 2.0 * (pop_k - 1.0) * 15.0, scale=sc_grp * pop_k, opacity=op_grp, blur_px=bl_grp)
                        else:
                            paste_subpixel(comp_im, sp_base, wcx, cur_y, scale=sc_grp, opacity=op_grp * (1.0 - u_act) * 0.90, blur_px=bl_grp)
                            paste_subpixel(comp_im, sp_act,  wcx, cur_y - 2.0 * u_act, scale=sc_grp * (1.0 + 0.05 * u_act), opacity=op_grp * u_act, blur_px=bl_grp)
                        cur_x += adv + gap
                break

        # Authentic Brand-Matched Bottom CTA Pill (53.85 - 59.05s) — WITH Entrance & Exit Animation!
        op_cta, dy_cta, sc_cta, bl_cta = text_in_out_anim(t, 53.85, 59.05, d_in=0.42, d_out=0.40, rise_in=20.0, drift_out=14.0)
        if op_cta > 0.01:
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
            w1, w2, w3 = sp_c1.width - 48, sp_c2.width - 48, sp_c3.width - 48
            tot_cw = w1 + w2 + w3
            sx0 = 12 + (cta_w - tot_cw) * 0.5
            paste_subpixel(cta_card, sp_c1, sx0 + w1 * 0.5,            10 + cta_h * 0.5, scale=1.0)
            paste_subpixel(cta_card, sp_c2, sx0 + w1 + w2 * 0.5,       10 + cta_h * 0.5 - 1, scale=1.0)
            paste_subpixel(cta_card, sp_c3, sx0 + w1 + w2 + w3 * 0.5,  10 + cta_h * 0.5, scale=1.0)
            paste_subpixel(comp_im, cta_card, 540.0, 1732.0 + dy_cta, scale=sc_cta, opacity=op_cta, blur_px=bl_cta)

        # Subtle Legal Disclaimer Bar at Bottom
        bar_bot = Image.new("RGBA", (W, 46), (26, 16, 24, 148))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 46))
        paste_subpixel(comp_im, legal_sp, 540.0, H - 23.0, scale=1.0, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"v3_muse_test_{len(test_saved):02d}.png")
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
        cols = 5
        rows = (len(imgs) + cols - 1) // cols
        grid = Image.new("RGB", (360 * cols, 640 * rows))
        for i, im in enumerate(imgs):
            grid.paste(im, ((i % cols) * 360, (i // cols) * 640))
        gp = os.path.join(CHECK_DIR, "v3_muse_master_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved v3_muse_master_grid.jpg:", gp)
    else:
        print(f"Done HTPM LT PLUS V3 Muse Master video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
