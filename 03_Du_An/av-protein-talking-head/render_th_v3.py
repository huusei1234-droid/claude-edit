import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR = r"d:\AI\full studio\output\av-protein-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
F = 1.0 / FPS

FONT_TITLE  = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7182504807289065985\0a5333de6f4d592cb2d2390d68b31efb\Oswald-Bold.ttf"
FONT_WIDE   = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf"
FONT_CAP    = r"C:\Windows\Fonts\palabi.ttf"
FONT_SCRIPT = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\6990292000264163842\840d58433e5d79e2599f155e83c2defb\ZYVNA Dreamboat.ttf"
FONT_SUB    = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7542214368361057553\d376267c892ee3a53654ae93a78dcfb7/font.ttf"

_font_cache = {}
def get_font(path, size):
    key = (path, int(round(size)))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, max(10, int(round(size))))
    return _font_cache[key]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def ease_out_cubic(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 3.0

def ease_in_cubic(u):
    u = clamp01(u)
    return u ** 3.0

def smoothstep(u):
    u = clamp01(u)
    return u * u * (3.0 - 2.0 * u)

def smooth_in_out_env(t, t0, t1, d_in=0.42, d_out=0.36):
    """Smooth keyframe envelope (0 -> 1 -> 0) with cubic ease-in-out!"""
    if t <= t0 or t >= t1:
        return 0.0
    a_in = smoothstep((t - t0) / max(0.05, d_in)) if (t - t0) < d_in else 1.0
    a_out = smoothstep((t1 - t) / max(0.05, d_out)) if (t1 - t) < d_out else 1.0
    return min(a_in, a_out)

def fit_cover(rgb_arr, target_w, target_h, zoom=1.0):
    """Aspect-ratio locked center-crop: 0% stretching or distortion EVER!"""
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    nw = max(target_w, int(round(sw * base_scale)))
    nh = max(target_h, int(round(sh * base_scale)))
    im = Image.fromarray(rgb_arr, "RGB").resize((nw, nh), Image.Resampling.BILINEAR)
    x0 = (nw - target_w) // 2
    y0 = (nh - target_h) // 2
    return im.crop((x0, y0, x0 + target_w, y0 + target_h))

# Precompute dark vignette canvas for B-roll split cards & top flares for rings
def _build_static_helpers():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1.0 - 0.50 * (((xx - 540.0) / 640.0) ** 2 + ((yy - 960.0) / 1080.0) ** 2), 0.35, 1.0)
    bbg = np.zeros((H, W, 3), dtype=np.uint8)
    bbg[:, :, 0] = (16 * vig).astype(np.uint8)
    bbg[:, :, 1] = (26 * vig).astype(np.uint8)
    bbg[:, :, 2] = (25 * vig).astype(np.uint8)
    broll_bg_im = Image.fromarray(bbg, "RGB").convert("RGBA")

    fl = np.exp(-((xx / 340.0) ** 2 + (yy / 360.0) ** 2)) + np.exp(-(((W - xx) / 340.0) ** 2 + (yy / 360.0) ** 2))
    fl_rgba = np.zeros((H, W, 4), dtype=np.uint8)
    fl_rgba[:, :, 0] = 220; fl_rgba[:, :, 1] = 255; fl_rgba[:, :, 2] = 245
    fl_rgba[:, :, 3] = np.clip(fl * 75.0, 0, 100).astype(np.uint8)
    flare_im = Image.fromarray(fl_rgba, "RGBA")
    return broll_bg_im, flare_im

BROLL_BG_IM, RINGS_FLARE_IM = _build_static_helpers()

_sprite_cache = {}
def render_glow_text_sprite(text, font_path, size, top_col, bot_col=None, glow_col=None, glow_rad=14, stroke_col=None, stroke_w=0):
    bot_col = bot_col or top_col
    glow_col = glow_col or top_col
    key = (text, font_path, int(round(size)), top_col, bot_col, glow_col, glow_rad, stroke_col, stroke_w)
    if key in _sprite_cache:
        return _sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(glow_rad * 3 + stroke_w + 16)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    mask_im = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), text, font=font, fill=255)

    arr_m = np.array(mask_im, dtype=np.float32) / 255.0
    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)[:, None]
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.uint8)
    for c in range(3):
        grad_rgb[:, :, c] = np.clip(top_col[c] * (1.0 - yy) + bot_col[c] * yy, 0, 255).astype(np.uint8)
    fill_im = Image.fromarray(np.dstack([grad_rgb, (arr_m * 255.0).astype(np.uint8)]), "RGBA")

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    if glow_rad > 0:
        g1_a = mask_im.filter(ImageFilter.GaussianBlur(radius=glow_rad * 0.8))
        g2_a = mask_im.filter(ImageFilter.GaussianBlur(radius=glow_rad * 2.1))
        g_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
        g_arr[:, :, 0] = glow_col[0]; g_arr[:, :, 1] = glow_col[1]; g_arr[:, :, 2] = glow_col[2]
        g_arr[:, :, 3] = np.clip(np.array(g1_a, dtype=np.float32) * 0.72 + np.array(g2_a, dtype=np.float32) * 0.45, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(g_arr, "RGBA"))

    sh_a = mask_im.filter(ImageFilter.GaussianBlur(radius=6))
    sh_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
    sh_arr[:, :, 3] = (np.array(sh_a, dtype=np.float32) * 0.65).astype(np.uint8)
    sh_im.paste(Image.fromarray(sh_arr, "RGBA"), (4, 6))
    base = Image.alpha_composite(base, sh_im)
    base = Image.alpha_composite(base, fill_im)

    if stroke_w > 0 and stroke_col is not None:
        st_only = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_only).text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        st_arr = np.array(st_only)
        inner = mask_im.filter(ImageFilter.MinFilter(3))
        st_arr[:, :, 3] = np.clip(st_arr[:, :, 3].astype(np.int32) - np.array(inner, dtype=np.int32), 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(st_arr, "RGBA"))

    if len(_sprite_cache) > 450:
        _sprite_cache.clear()
    _sprite_cache[key] = (base, mask_im)
    return base, mask_im

def paste_centered(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0, angle=0.0, blur_px=0.0, sweep_prog=None):
    if opacity <= 0.01 or scale <= 0.02:
        return
    im = sprite_im
    if sweep_prog is not None and 0.0 <= sweep_prog <= 1.0:
        arr = np.array(im).copy()
        sh, sw = arr.shape[:2]
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        diag = (xx + yy * 0.45) / (sw + sh * 0.45)
        band = np.exp(-((diag - sweep_prog) / 0.09) ** 2)
        alpha_f = (arr[:, :, 3:4].astype(np.float32) / 255.0)
        arr[:, :, :3] = np.clip(arr[:, :, :3].astype(np.float32) + 170.0 * band[:, :, None] * alpha_f, 0, 255).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    if abs(scale - 1.0) > 0.008:
        nw = max(2, int(round(im.width * scale)))
        nh = max(2, int(round(im.height * scale)))
        im = im.resize((nw, nh), Image.Resampling.BILINEAR)
    if abs(angle) > 0.15:
        im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    if blur_px >= 0.6:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(14.0, blur_px)))
    if opacity < 0.995:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    px = int(round(cx - im.width / 2.0))
    py = int(round(cy - im.height / 2.0))
    canvas_im.alpha_composite(im, dest=(px, py))

ICON_FILES = {
    "hook1": os.path.join(MEDIA_DIR, "hook_01_clean.png"),
    "hook2": os.path.join(MEDIA_DIR, "hook_02_clean.png"),
    "c04":   os.path.join(MEDIA_DIR, "icon_c04_clean.png"),
    "c07":   os.path.join(MEDIA_DIR, "icon_c07_clean.png"),
    "c08":   os.path.join(MEDIA_DIR, "icon_c08_clean.png"),
    "pack":  os.path.join(MEDIA_DIR, "packshot_c08_clean.png"),
}
ICON_IMS = {k: Image.open(v).convert("RGBA") for k, v in ICON_FILES.items()}

def render_tile_frame(icon_key, size_px, t_sec):
    S = size_px
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pad = 14
    cs = S - pad * 2
    rad = int(cs * 0.22)

    rmask = Image.new("L", (cs, cs), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, cs - 1, cs - 1], radius=rad, fill=255)

    ic_resized = ICON_IMS[icon_key].resize((cs, cs), Image.Resampling.LANCZOS)
    glow_bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow_bg).rounded_rectangle([pad - 3, pad - 3, pad + cs + 2, pad + cs + 2], radius=rad + 3, outline=(62, 235, 190, 210), width=5)
    glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(radius=6))
    im = Image.alpha_composite(im, glow_bg)

    card_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    card_layer.paste(ic_resized, (pad, pad), mask=rmask)
    im = Image.alpha_composite(im, card_layer)

    ImageDraw.Draw(im).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=(45, 210, 175, 190), width=4)

    ang = (t_sec / 3.5) * 2.0 * math.pi
    sx = S / 2.0 + (cs * 0.48) * math.cos(ang)
    sy = S / 2.0 + (cs * 0.48) * math.sin(ang)
    border_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(border_mask).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=255, width=6)
    bm_arr = np.array(border_mask, dtype=np.float32) / 255.0
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    spot = np.exp(-(((xx - sx) ** 2 + (yy - sy) ** 2) / (2.0 * (S * 0.18) ** 2)))
    sweep_rgba = np.zeros((S, S, 4), dtype=np.uint8)
    sweep_rgba[:, :, 0] = 255; sweep_rgba[:, :, 1] = 245; sweep_rgba[:, :, 2] = 175
    sweep_rgba[:, :, 3] = np.clip(bm_arr * spot * 255.0, 0, 255).astype(np.uint8)
    im = Image.alpha_composite(im, Image.fromarray(sweep_rgba, "RGBA").filter(ImageFilter.GaussianBlur(radius=2)))
    return im

def draw_burst(canvas_im, cx, cy, t_now, t0, diam=74):
    dt = t_now - t0
    if dt < 0 or dt > 0.45:
        return
    u = dt / 0.45
    sc = 0.60 + 1.25 * ease_out_cubic(u)
    op = smoothstep(1.0 - u)
    r = int(round(diam * 0.5 * sc))
    sw = max(2, int(round(6 * (1.0 - 0.6 * u))))
    sz = r * 2 + 20
    bim = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    ImageDraw.Draw(bim).ellipse([10, 10, sz - 10, sz - 10], outline=(255, 255, 255, int(230 * op)), width=sw)
    canvas_im.alpha_composite(bim, dest=(int(cx - sz // 2), int(cy - sz // 2)))

def draw_rings_bg(canvas_im, t_now, t0, t1):
    env = smooth_in_out_env(t_now, t0, t1, d_in=0.50, d_out=0.45)
    if env <= 0.01:
        return
    dt = t_now - t0
    dur = max(0.2, t1 - t0)
    sc = 0.92 + 0.08 * ease_out_cubic(min(1.0, dt / 0.55))
    rot_deg = 36.0 * (dt / dur)
    cx, cy = 540, 680

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    R1 = int(525 * sc)
    R2 = int(405 * sc)
    dr.ellipse([cx - R1, cy - R1, cx + R1, cy + R1], outline=(255, 255, 255, int(155 * env)), width=3)
    dr.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=(140, 255, 225, int(95 * env)), width=2)

    keys = ["hook1", "c04", "c08", "c07", "hook2"]
    for i, k in enumerate(keys):
        a_deg = -165.0 + i * (150.0 / 4.0) + rot_deg * 0.65
        a_rad = math.radians(a_deg)
        ix = cx + int(R1 * math.cos(a_rad))
        iy = cy + int(R1 * math.sin(a_rad))
        mini = ICON_IMS[k].resize((80, 80), Image.Resampling.BILINEAR)
        mm = Image.new("L", (80, 80), 0)
        ImageDraw.Draw(mm).ellipse([2, 2, 77, 77], fill=int(225 * env))
        layer.paste(mini, (ix - 40, iy - 40), mask=mm)
        dr.ellipse([ix - 41, iy - 41, ix + 41, iy + 41], outline=(255, 255, 255, int(195 * env)), width=3)

        ga = a_rad + 0.32
        gx = cx + int(R2 * math.cos(ga))
        gy = cy + int(R2 * math.sin(ga))
        dr.ellipse([gx - 10, gy - 10, gx + 10, gy + 10], outline=(255, 240, 170, int(195 * env)), width=4)

    if env > 0.2:
        fl_arr = np.array(RINGS_FLARE_IM)
        fl_arr[:, :, 3] = (fl_arr[:, :, 3].astype(np.float32) * env).astype(np.uint8)
        layer = Image.alpha_composite(layer, Image.fromarray(fl_arr, "RGBA"))

    canvas_im.alpha_composite(layer)

def render_split_broll_v3(base_rgba, top_rgb, bot_rgb, t_now, st, en, badge_small, badge_big):
    """
    Distortion-Free Dual Split B-Roll Card with Smooth Keyframe Glide & Crossfade!
    - Uses fit_cover() -> 100% locked aspect ratio, ZERO stretching/squishing!
    - Smooth 0.42s ease-in-out entry & exit over base video!
    """
    env = smooth_in_out_env(t_now, st, en, d_in=0.42, d_out=0.40)
    if env <= 0.005:
        return base_rgba

    dt = t_now - st
    dur = max(0.2, en - st)
    card_layer = BROLL_BG_IM.copy()

    # Smooth subtle Ken Burns zoom on both distinct video clips (1.02 -> 1.09)
    z_top = 1.02 + 0.07 * smoothstep(dt / dur)
    z_bot = 1.08 - 0.06 * smoothstep(dt / dur)

    cw, ch = 920, 720
    # Top Card (slides smoothly down 36px -> 0 on enter, glides softly)
    top_crop = fit_cover(top_rgb, cw, ch, zoom=z_top).convert("RGBA")
    tmask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(tmask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=54, fill=255)
    tcard = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    tcard.paste(top_crop, (0, 0), mask=tmask)
    ImageDraw.Draw(tcard).rounded_rectangle([1, 1, cw - 2, ch - 2], radius=54, outline=(130, 255, 220, 225), width=5)

    # Bottom Card (distinct 2nd video! Slides smoothly up -36px -> 0 on enter)
    bot_crop = fit_cover(bot_rgb, cw, ch, zoom=z_bot).convert("RGBA")
    bcard = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bcard.paste(bot_crop, (0, 0), mask=tmask)
    ImageDraw.Draw(bcard).rounded_rectangle([1, 1, cw - 2, ch - 2], radius=54, outline=(255, 225, 130, 195), width=4)

    # Drop shadows
    sh_card = Image.new("RGBA", (cw + 60, ch + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh_card).rounded_rectangle([30, 34, 30 + cw, 34 + ch], radius=54, fill=(0, 0, 0, 165))
    sh_card = sh_card.filter(ImageFilter.GaussianBlur(radius=18))

    glide = (1.0 - env) * 42.0
    sc_card = 0.94 + 0.06 * env

    # Place Bottom Card at cy = 1415 + glide, slight -1.1 deg editorial tilt (zero perspective stretch!)
    paste_centered(card_layer, sh_card, 540, 1420 + glide, scale=sc_card, opacity=1.0, angle=-1.1)
    paste_centered(card_layer, bcard,   540, 1415 + glide, scale=sc_card, opacity=1.0, angle=-1.1)

    # Place Top Card at cy = 485 - glide, slight +1.1 deg editorial tilt
    paste_centered(card_layer, sh_card, 540, 492 - glide, scale=sc_card, opacity=1.0, angle=1.1)
    paste_centered(card_layer, tcard,   540, 485 - glide, scale=sc_card, opacity=1.0, angle=1.1)

    # Center Pill Title between the two cards (y = 950)
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([85, 882, 995, 1018], radius=40, fill=(8, 34, 26, 238), outline=(105, 245, 205, 225), width=3)
    card_layer = Image.alpha_composite(card_layer, pill)

    sp1, _ = render_glow_text_sprite(badge_small, FONT_WIDE, 26, (195, 255, 235), glow_rad=6)
    sp2, _ = render_glow_text_sprite(badge_big, FONT_WIDE, 39, (255, 222, 65), (255, 185, 20), glow_col=(255, 195, 40), glow_rad=10)
    paste_centered(card_layer, sp1, 540, 918, scale=sc_card, opacity=1.0)
    paste_centered(card_layer, sp2, 540, 972, scale=sc_card, opacity=1.0)

    if env >= 0.995:
        return card_layer
    arr = np.array(card_layer)
    arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * env).astype(np.uint8)
    out = base_rgba.copy()
    out.alpha_composite(Image.fromarray(arr, "RGBA"))
    return out

def draw_synergy_bar(canvas_im, t_now, t0, t1):
    env = smooth_in_out_env(t_now, t0, t1, d_in=0.45, d_out=0.38)
    if env <= 0.01:
        return
    dt = t_now - t0
    dur = max(0.2, t1 - t0)
    ox = 180.0 * (1.0 - ease_out_cubic(min(1.0, dt / 0.48))) - 18.0 * (dt / dur)

    bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(bar)
    bx1, by1, bx2, by2 = int(75 + ox), 1565, int(1005 + ox), 1790
    dr.rounded_rectangle([bx1, by1, bx2, by2], radius=52, fill=(10, 32, 26, int(205 * env)), outline=(145, 255, 225, int(210 * env)), width=3)

    items = [
        ("c08", "TẢO BIỂN", -310, 130),
        ("pack", "BOJOMI", -95, 164),
        ("c07", "D3 + K2", 125, 130),
        ("hook1", "COLLAGEN", 315, 130),
    ]
    cx_base = 540 + ox
    for k, lbl, dx, sz in items:
        ic = ICON_IMS[k].resize((sz, sz), Image.Resampling.BILINEAR)
        rm = Image.new("L", (sz, sz), 0)
        ImageDraw.Draw(rm).rounded_rectangle([0, 0, sz - 1, sz - 1], radius=int(sz * 0.22), fill=int(255 * env))
        px = int(cx_base + dx - sz // 2)
        py = 1660 - sz // 2
        bar.paste(ic, (px, py), mask=rm)
        ImageDraw.Draw(bar).rounded_rectangle([px, py, px + sz - 1, py + sz - 1], radius=int(sz * 0.22), outline=(255, 230, 120, int(215 * env)), width=3)
        sp, _ = render_glow_text_sprite(lbl, FONT_WIDE, 22 if sz < 155 else 26, (255, 255, 255) if sz < 155 else (255, 220, 60), glow_rad=5)
        paste_centered(bar, sp, cx_base + dx, py + sz + 22, opacity=env)

    canvas_im.alpha_composite(bar)

# ======================================================================
# SMOOTH CAMERA ZOOM & BACKGROUND DIMMING ENVELOPES
# ======================================================================
ZOOM_KEYS = [
    (0.00, 1.00),
    (3.40, 1.04),
    (9.58, 1.09),
    (15.00, 1.02),
    (18.00, 1.08),
    (24.50, 1.02),
    (29.04, 1.09),
    (34.36, 1.11),
    (39.54, 1.04),
    (42.34, 1.09),
    (49.10, 1.04),
    (59.30, 1.09),
    (66.43, 1.03),
]

def get_smooth_zoom(t):
    """Smooth cubic interpolation between zoom keyframes — zero sudden jumps!"""
    if t <= ZOOM_KEYS[0][0]:
        return ZOOM_KEYS[0][1]
    for i in range(len(ZOOM_KEYS) - 1):
        t0, z0 = ZOOM_KEYS[i]
        t1, z1 = ZOOM_KEYS[i + 1]
        if t0 <= t <= t1:
            # Smooth transition over 0.70s at the start of each segment, then gentle drift
            trans_dur = min(0.75, (t1 - t0) * 0.5)
            u = smoothstep((t - t0) / max(0.1, trans_dur))
            return z0 + (z1 - z0) * u
    return ZOOM_KEYS[-1][1]

# Windows where visual animations appear on top of / behind speaker -> smoothly darken room background!
# Between these windows (e.g. 14.9-18.0s, 24.1-25.0s, 33.8-34.4s, etc.), room returns smoothly to 100% normal!
ANIM_DIM_WINDOWS = [
    (0.05, 3.42),    # Hook animation + 3 overhead tiles
    (9.58, 12.60),   # Keyword "BĂN KHOĂN?" + tile
    (17.95, 24.20),  # "LƯU Ý 1" + "3 YẾU TỐ" + c04 tile
    (29.04, 34.25),  # "LƯU Ý 2" + "CHIỀU CAO"
    (34.36, 36.10),  # "ĐIỂM SÁNG 3" (Bojomi An Vượng)
    (39.54, 54.30),  # "HIỆP ĐỒNG" + Synergy Bar + Orbital Rings + "418mg CANXI" + "D3 & K2 MK7"
    (59.30, 66.20),  # CTA Orbital Rings + "ĐỐI CHIẾU" + tile
]

def get_bg_dim(t):
    """Returns 0.0 (100% normal bright room) -> 1.0 (smoothly darkened background so animation pops!)"""
    val = 0.0
    for w0, w1 in ANIM_DIM_WINDOWS:
        val = max(val, smooth_in_out_env(t, w0, w1, d_in=0.50, d_out=0.50))
    return val

def load_timeline_v3():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut.json"), encoding="utf-8"))
    # 4 Split B-Roll Card spans mapped to exact timestamps in user's 66.43s main_cut.mp4!
    broll_spans = [
        # (start, end, top_clip_key, bot_clip_key, small_label, big_title)
        (3.55, 9.15,  "c02_meal", "c02_study", "THỰC TRẠNG SINH HOẠT", "ĂN THẤT THƯỜNG • LỊCH HỌC KÍN"),
        (25.02, 28.92, "c05_bone", "c05_vitd",  "DƯỠNG CHẤT CHO XƯƠNG", "CANXI & VITAMIN D QUAN TRỌNG"),
        (36.05, 39.48, "c06_algae", "c05_bone", "BOJOMI AN VƯỢNG",      "NGUỒN CANXI TỪ TẢO BIỂN ĐỎ"),
        (54.35, 59.18, "c09_cup",  "c09_grains","TIỆN LỢI MỖI NGÀY",    "1 GÓI • ĐỦ DINH DƯỠNG CHO XƯƠNG"),
    ]
    # Keep 0.25s margin so B-roll crossfades cleanly without overlapping captions
    skip_ranges = [(0.0, 3.45)] + [(s[0] + 0.15, s[1] - 0.15) for s in broll_spans]
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if not any(a <= (w["start"] + w["end"]) * 0.5 <= b for a, b in skip_ranges)
    ]

    groups, cur, line = [], [], []
    def flush_line():
        nonlocal line
        if line: cur.append(line); line = []
    def flush_group():
        nonlocal cur
        flush_line()
        if cur: groups.append(cur); cur = []

    prev = None
    for w in words:
        txt = w["word"].strip()
        if not txt: continue
        if prev is not None and (w["start"] - prev["end"]) >= 0.36:
            flush_group()
        if line and (len(line) >= 3 or sum(len(x[0]) + 1 for x in line) + len(txt) > 15):
            flush_line()
        if len(cur) >= 3 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!…:;]$", txt):
            flush_group()
    flush_group()

    GOLD_WORDS = {"dưỡng", "khỏe", "mạnh", "chế", "tuổi", "nhu", "Bojomi", "Vượng", "tảo", "biển", "418mg", "779", "170mcg", "MK7"}
    PINK_WORDS = {"băn", "khoăn", "không", "cao", "hơn", "D3,", "K2,", "collagen", "nhắn", "quyết", "định"}
    STROKE_UP_WORDS = {"Bojomi", "418mg", "779", "170mcg", "nhắn"}

    cap_groups = []
    for i, g in enumerate(groups):
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else 66.40
        t1 = min(nxt, last_end + 0.45) if (nxt - last_end) > 0.6 else nxt
        cap_groups.append({"t0": g[0][0][1], "t1": t1, "lines": g})
    return broll_spans, cap_groups, GOLD_WORDS, PINK_WORDS, STROKE_UP_WORDS

class VideoReader:
    def __init__(self, path):
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE
        )
    def read(self):
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            return None
        return np.frombuffer(buf, dtype=np.uint8).reshape((H, W, 3))
    def close(self):
        self.proc.stdout.close()
        self.proc.wait()

def load_clip_frames(path):
    frames = []
    r = VideoReader(path)
    while True:
        f = r.read()
        if f is None: break
        frames.append(f)
    r.close()
    return frames

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {int(round(ts * FPS)) for ts in [1.4, 6.0, 16.5, 21.8, 26.8, 41.0, 46.5, 56.8]}
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    print("Loading 7 distinct 1080x1920 B-roll clips into RAM...")
    broll_clips = {
        "c02_meal":   load_clip_frames(os.path.join(MEDIA_DIR, "broll_c02_meal.mp4")),
        "c02_study":  load_clip_frames(os.path.join(MEDIA_DIR, "broll_c02.mp4")),
        "c05_bone":   load_clip_frames(os.path.join(MEDIA_DIR, "broll_c05.mp4")),
        "c05_vitd":   load_clip_frames(os.path.join(MEDIA_DIR, "broll_c05_vitd.mp4")),
        "c06_algae":  load_clip_frames(os.path.join(MEDIA_DIR, "broll_c06.mp4")),
        "c09_cup":    load_clip_frames(os.path.join(MEDIA_DIR, "broll_c09.mp4")),
        "c09_grains": load_clip_frames(os.path.join(MEDIA_DIR, "broll_c09_grains.mp4")),
    }

    broll_spans, cap_groups, GOLD_WORDS, PINK_WORDS, STROKE_UP_WORDS = load_timeline_v3()

    NUMBERS = [
        ("LƯU Ý", "1", 17.96, 20.10),
        ("LƯU Ý", "2", 29.04, 31.15),
        ("ĐIỂM SÁNG", "3", 34.36, 36.02),
    ]
    KEYWORDS = [
        ("BĂN KHOĂN?", 9.58, 12.55, 185, (255, 232, 135), (255, 255, 255)),
        ("3 YẾU TỐ", 20.15, 24.18, 195, (255, 218, 75), (255, 248, 215)),
        ("CHIỀU CAO", 31.20, 34.25, 190, (125, 248, 235), (240, 255, 255)),
        ("HIỆP ĐỒNG", 39.54, 42.30, 185, (255, 220, 85), (255, 250, 220)),
        ("418mg CANXI", 42.35, 48.85, 160, (115, 255, 205), (245, 255, 250)),
        ("D3 & K2 MK7", 49.05, 54.25, 162, (255, 215, 70), (255, 250, 225)),
        ("ĐỐI CHIẾU", 61.30, 66.15, 185, (120, 250, 220), (255, 255, 255)),
    ]
    TILE_PLACES = [
        ("hook1", 0.70, 3.38, 215, 310, 215, -10.0),
        ("hook2", 0.88, 3.38, 540, 245, 225, 0.0),
        ("c08",   1.06, 3.38, 865, 310, 215, 10.0),
        ("c04",   20.15, 24.18, 865, 1365, 238, 0.0),
        ("c08",   42.45, 48.85, 865, 1365, 235, -2.0),
        ("pack",  49.05, 54.25, 865, 1365, 242, 2.0),
        ("c07",   59.40, 66.15, 865, 1365, 235, 0.0),
    ]
    BURSTS = [
        (215, 310, 0.78, 68), (540, 245, 0.96, 74), (865, 310, 1.14, 68),
        (865, 1365, 20.25, 76), (865, 1365, 42.55, 76), (865, 1365, 49.15, 76), (865, 1365, 59.50, 76),
    ]

    legal_sp, _ = render_glow_text_sprite(
        "Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh",
        FONT_SUB, 22, (230, 238, 235), glow_rad=0
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_v3_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    frame_idx = 0
    while True:
        rgb = reader_a.read()
        mbuf = reader_m.stdout.read(W * H)
        if rgb is None or len(mbuf) < W * H:
            break
        if test_mode and frame_idx not in test_frames:
            frame_idx += 1
            if frame_idx > max(test_frames):
                break
            continue

        matte = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W)).astype(np.float32) / 255.0
        t = frame_idx / FPS

        # 1. Smooth Camera Zoom on the original normal video + matte!
        z = get_smooth_zoom(t)
        if z > 1.003:
            cw, ch = int(round(W / z)), int(round(H / z))
            x0 = max(0, min(W - cw, int(round(540 - cw * 0.5))))
            y0 = max(0, min(H - ch, int(round(680 - ch * (680.0 / H)))))
            frame_im = Image.fromarray(rgb[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
            matte_im = Image.fromarray((matte[y0:y0+ch, x0:x0+cw] * 255.0).astype(np.uint8), "L").resize((W, H), Image.Resampling.BILINEAR)
            fg_rgb = np.array(frame_im)
            m_arr = np.array(matte_im, dtype=np.float32) / 255.0
        else:
            frame_im = Image.fromarray(rgb, "RGB")
            fg_rgb = rgb
            m_arr = matte

        # 2. Normal video background vs Smooth Darkening when Animation appears!
        dim = get_bg_dim(t)
        if dim <= 0.005:
            # 100% NORMAL ORIGINAL VIDEO (as requested: "những cảnh có mẫu thì để nền của video bình thường")!
            comp_im = frame_im.convert("RGBA")
        else:
            # Smoothly darken & gently soften background behind speaker so animations POP vividly!
            bg_soft = frame_im.filter(ImageFilter.GaussianBlur(radius=5.0 * dim)) if dim > 0.08 else frame_im
            bg_arr = np.array(bg_soft, dtype=np.float32)
            # Darken background down to 26% brightness with a rich dark-emerald cinema tint at peak dim
            bg_factor = 1.0 - 0.74 * dim
            bg_dimmed = np.zeros_like(bg_arr)
            bg_dimmed[:, :, 0] = bg_arr[:, :, 0] * bg_factor * (1.0 - 0.15 * dim)
            bg_dimmed[:, :, 1] = bg_arr[:, :, 1] * bg_factor
            bg_dimmed[:, :, 2] = bg_arr[:, :, 2] * bg_factor * (1.0 - 0.05 * dim)
            comp_im = Image.fromarray(np.clip(bg_dimmed, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

            # Behind-speaker animations (Orbital Rings, Numbers 1/2/3, Giant Keywords)!
            draw_rings_bg(comp_im, t, 42.35, 54.25)
            draw_rings_bg(comp_im, t, 59.30, 66.20)

            for lbl, dig, t0, t1 in NUMBERS:
                env_n = smooth_in_out_env(t, t0, t1, d_in=0.38, d_out=0.35)
                if env_n > 0.01:
                    dt = t - t0
                    sc_l = 0.88 + 0.12 * ease_out_cubic(min(1.0, dt / 0.38))
                    gy_l = (1.0 - env_n) * 20.0
                    sp_l, _ = render_glow_text_sprite(lbl, FONT_TITLE, 108, (85, 205, 255), (35, 130, 255), glow_col=(45, 165, 255), glow_rad=14)
                    paste_centered(comp_im, sp_l, 240, 355 + gy_l, scale=sc_l, opacity=env_n)

                    if dt >= 0.06:
                        dt_d = dt - 0.06
                        u_d = ease_out_cubic(min(1.0, dt_d / 0.44))
                        sc_d = 0.84 + 0.16 * u_d
                        rot_d = -10.0 * (1.0 - u_d)
                        sp_d, _ = render_glow_text_sprite(dig, FONT_CAP, 530, (255, 220, 95), (145, 255, 225), glow_col=(95, 245, 225), glow_rad=22, stroke_col=(220, 255, 250), stroke_w=8)
                        paste_centered(comp_im, sp_d, 770, 545 + gy_l, scale=sc_d, opacity=env_n, angle=rot_d)

            for kw_txt, t0, t1, fsz, c_top, c_bot in KEYWORDS:
                env_k = smooth_in_out_env(t, t0, t1, d_in=0.40, d_out=0.36)
                if env_k > 0.01:
                    dt = t - t0
                    sc_k = 0.90 + 0.10 * ease_out_cubic(min(1.0, dt / 0.40))
                    gy_k = (1.0 - env_k) * 22.0
                    sw_p = (dt / max(0.3, t1 - t0)) * 1.25 - 0.12
                    sp_k, _ = render_glow_text_sprite(kw_txt, FONT_TITLE, fsz + 14, c_top, c_bot, glow_col=c_top, glow_rad=12)
                    paste_centered(comp_im, sp_k, 540, 445 + gy_k, scale=sc_k, opacity=env_k, sweep_prog=sw_p)

            # Composite real speaker + real desk BOJOMI box smoothly in front of behind-head animations!
            desk_line = np.clip((np.arange(H, dtype=np.float32) - 1505.0) / 55.0, 0.0, 1.0)[:, None]
            yy_box, xx_box = np.ogrid[0:H, 0:W]
            box_mask = np.exp(-((np.maximum(0.0, np.abs(xx_box - 680.0) - 185.0)) / 42.0) ** 2) * \
                       np.clip((yy_box - 1265.0) / 45.0, 0.0, 1.0) * np.clip((1560.0 - yy_box) / 40.0, 0.0, 1.0)
            fg_alpha = np.maximum(m_arr, np.maximum(desk_line, box_mask * 0.96))
            # Speaker dims slightly (only 8% at peak dim) so chest glowing captions also pop cleanly!
            fg_lit = np.clip(fg_rgb.astype(np.float32) * (1.0 - 0.08 * dim), 0, 255).astype(np.uint8)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_lit, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 3. Front Hook Animation (0.05 - 3.40s) with smooth ease-in-out keyframes!
        env_hook = smooth_in_out_env(t, 0.05, 3.40, d_in=0.35, d_out=0.35)
        if env_hook > 0.01:
            if t >= 0.05:
                u1 = ease_out_cubic(min(1.0, (t - 0.05) / 0.36))
                sp_h1, _ = render_glow_text_sprite("Muốn con", FONT_WIDE, 78, (95, 225, 255), (35, 130, 255), glow_col=(55, 175, 255), glow_rad=14)
                paste_centered(comp_im, sp_h1, 540, 1105 + (1.0 - u1) * 24.0, scale=0.86 + 0.14 * u1, opacity=env_hook * u1)
            if t >= 0.38:
                u2 = ease_out_cubic(min(1.0, (t - 0.38) / 0.38))
                sp_h2, _ = render_glow_text_sprite("CAO", FONT_WIDE, 142, (255, 225, 65), (255, 115, 35), glow_col=(255, 165, 40), glow_rad=18)
                paste_centered(comp_im, sp_h2, 335, 1235 + (1.0 - u2) * 28.0, scale=0.84 + 0.16 * u2, opacity=env_hook * u2)
            if t >= 0.56:
                u3 = ease_out_cubic(min(1.0, (t - 0.56) / 0.40))
                sp_h3, _ = render_glow_text_sprite("Lớn!", FONT_SCRIPT, 150, (110, 255, 175), (45, 235, 145), glow_col=(75, 255, 165), glow_rad=20, stroke_col=(225, 255, 238), stroke_w=2)
                paste_centered(comp_im, sp_h3, 705, 1245 + (1.0 - u3) * 28.0, scale=0.84 + 0.16 * u3, opacity=env_hook * u3)
            if t >= 1.75:
                u4 = ease_out_cubic(min(1.0, (t - 1.75) / 0.36))
                sp_h4, _ = render_glow_text_sprite("Đã quan tâm bữa ăn hằng ngày?", FONT_CAP, 52, (255, 255, 255), (165, 255, 235), glow_col=(92, 247, 224), glow_rad=12)
                paste_centered(comp_im, sp_h4, 540, 1368 + (1.0 - u4) * 20.0, scale=0.90 + 0.10 * u4, opacity=env_hook * u4)

        # 4. Smooth Floating Icon Tiles + Bursts
        for ikey, t0, t1, cx, cy, sz, rot in TILE_PLACES:
            env_t = smooth_in_out_env(t, t0, t1, d_in=0.42, d_out=0.36)
            if env_t > 0.01:
                dt = t - t0
                u_in = ease_out_cubic(min(1.0, dt / 0.45))
                cur_y = cy + (1.0 - u_in) * (85.0 if cy < 400 else 150.0) - (1.0 - env_t) * (0.0 if dt < 0.5 else 24.0)
                cur_sc = 0.75 + 0.25 * env_t
                tile_im = render_tile_frame(ikey, sz, t)
                paste_centered(comp_im, tile_im, cx, cur_y, scale=cur_sc, opacity=env_t, angle=rot)

        for bx, by, bt0, bdiam in BURSTS:
            draw_burst(comp_im, bx, by, t, bt0, bdiam)

        # 5. Smooth Synergy Frosted Glass Bar (39.54 - 42.30s)
        draw_synergy_bar(comp_im, t, 39.54, 42.30)

        # 6. Word-by-Word Glowing Captions (smooth 8-frame glide-in & 8-frame fade-out!)
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                op_g = smoothstep((g["t1"] - t) / 0.26) if (g["t1"] - t) < 0.26 else 1.0
                y_base = 1140
                lh = 68
                for li, ln in enumerate(g["lines"]):
                    word_renders = []
                    total_w = 0
                    gap = 18
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        k = 1.22 if (wtxt in GOLD_WORDS or wtxt in PINK_WORDS) else 1.0
                        col = (255, 222, 70) if wtxt in GOLD_WORDS else ((255, 145, 205) if wtxt in PINK_WORDS else (92, 247, 224))
                        sp, _ = render_glow_text_sprite(wtxt, FONT_CAP, 65 * k, col, glow_col=col, glow_rad=12)
                        adv = int(ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_CAP, 65 * k)))
                        word_renders.append((wtxt, ws, sp, adv, col, k))
                        total_w += adv + (gap if wi > 0 else 0)

                    cur_x = 540 - total_w // 2
                    cur_y = y_base + li * lh
                    for wtxt, ws, sp, adv, col, k in word_renders:
                        if t >= ws:
                            dt_w = t - ws
                            u_w = ease_out_cubic(min(1.0, dt_w / 0.26))
                            wy = cur_y + (1.0 - u_w) * 22.0
                            blur_w = (1.0 - u_w) * 6.0
                            wcx = cur_x + adv // 2
                            paste_centered(comp_im, sp, wcx, wy, scale=0.92 + 0.08 * u_w, opacity=op_g * u_w, blur_px=blur_w)

                            if wtxt in STROKE_UP_WORDS and 0.08 <= dt_w <= 0.48:
                                u_su = (dt_w - 0.08) / 0.40
                                sc_su = 1.0 + 1.15 * ease_out_cubic(u_su)
                                op_su = smoothstep(1.0 - u_su) * 0.80 * op_g
                                sp_su, _ = render_glow_text_sprite(wtxt, FONT_CAP, 65 * k, (0, 0, 0), glow_col=col, glow_rad=8, stroke_col=(230, 255, 248), stroke_w=3)
                                paste_centered(comp_im, sp_su, wcx, cur_y, scale=sc_su, opacity=op_su)
                        cur_x += adv + gap
                break

        # 7. Smooth Crossfading Dual-Layer Split B-Roll Cards (2 distinct clips per card, 0% distortion!)
        for st, en, top_k, bot_k, b_sm, b_bg in broll_spans:
            if st <= t <= en:
                dt = t - st
                tc = broll_clips[top_k]
                bc = broll_clips[bot_k]
                top_f = tc[min(len(tc) - 1, int(dt * FPS))]
                bot_f = bc[min(len(bc) - 1, int(dt * FPS))]
                comp_im = render_split_broll_v3(comp_im, top_f, bot_f, t, st, en, b_sm, b_bg)
                break

        # 8. Subtle Legal Bar at bottom
        bar_bot = Image.new("RGBA", (W, 54), (5, 14, 12, 160))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 54))
        paste_centered(comp_im, legal_sp, 540, H - 27, opacity=0.90)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"v3_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/1993 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close()
        writer.wait()
    reader_a.close()
    reader_m.stdout.close()
    reader_m.wait()
    print(f"Done v3 video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
