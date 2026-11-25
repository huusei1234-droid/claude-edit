import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm3-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

FONTS_DIR       = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_MONTS_BLK  = os.path.join(FONTS_DIR, "Montserrat-Black.ttf")
FONT_FRAUNCES   = os.path.join(FONTS_DIR, "Fraunces-Black.ttf")
FONT_PLAYFAIR   = os.path.join(FONTS_DIR, "PlayfairDisplay-ExtraBold.ttf")
FONT_PLAYFAIR_I = os.path.join(FONTS_DIR, "PlayfairDisplay-BoldItalic.ttf")
FONT_BE_XBOLD   = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_BE_BOLD    = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")
FONT_BE_MED     = os.path.join(FONTS_DIR, "BeVietnamPro-Medium.ttf")

# ======================================================================
# 1. FIVE-STOP LUXURY GRADIENT PALETTES (FROM gradient-text-presets.css)
# ======================================================================
GRAD_PALETTES = {
    "gold": [
        (0.00, (255, 253, 242)),
        (0.25, (252, 225, 129)),
        (0.52, (214, 146,  40)),
        (0.76, (255, 235, 168)),
        (1.00, (154,  94,  12)),
    ],
    "rose_satin": [
        (0.00, (255, 230, 243)),
        (0.24, (249, 106, 181)),
        (0.52, (200,  18, 110)),
        (0.76, (255, 158, 210)),
        (1.00, (125,   8,  69)),
    ],
    "emerald": [
        (0.00, (234, 255, 248)),
        (0.25, ( 92, 224, 181)),
        (0.52, ( 13, 150, 104)),
        (0.76, (162, 245, 216)),
        (1.00, (  6,  86,  60)),
    ],
    "sapphire": [
        (0.00, (237, 250, 255)),
        (0.25, (104, 210, 255)),
        (0.52, ( 11,  99, 229)),
        (0.76, (166, 229, 255)),
        (1.00, (  7,  52, 130)),
    ],
    "coral": [
        (0.00, (255, 245, 232)),
        (0.25, (255, 159,  90)),
        (0.52, (230,  68,  34)),
        (0.76, (255, 200, 158)),
        (1.00, (140,  27,   8)),
    ],
    "pearl": [
        (0.00, (255, 255, 255)),
        (0.35, (244, 252, 249)),
        (0.68, (218, 238, 231)),
        (1.00, (255, 255, 255)),
    ],
}

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

def ease_out_expo(u):
    u = clamp01(u)
    return 1.0 if u >= 0.999 else 1.0 - math.pow(2.0, -10.0 * u)

def ease_out_back(u, overshoot=1.28):
    """After Effects signature spring settle curve!"""
    u = clamp01(u) - 1.0
    return 1.0 + u * u * ((overshoot + 1.0) * u + overshoot)

def ae_in_out(t, st, en, d_in=0.46, d_out=0.40, overshoot=1.18):
    """Returns (u_in_spring, u_out_smooth, opacity, blur_px) for After Effects layer motion!"""
    if t <= st or t >= en:
        return 0.0, 0.0, 0.0, 0.0
    raw_in  = clamp01((t - st) / max(0.05, d_in))
    raw_out = clamp01((en - t) / max(0.05, d_out))
    u_in    = ease_out_back(raw_in, overshoot=overshoot)
    u_out   = quintic_smooth(raw_out)
    op      = min(quintic_smooth(min(1.0, raw_in * 1.35)), u_out)
    blur_px = (1.0 - quintic_smooth(raw_in)) * 4.2 + (1.0 - u_out) * 3.6
    return u_in, u_out, op, blur_px

# ======================================================================
# 2. TRUE 3D PERSPECTIVE HOMOGRAPHY ENGINE (AFTER EFFECTS 3D LAYER!)
# ======================================================================
def _solve_homography_8(src_pts, dst_pts):
    """Computes 8 PIL.Image.Transform.PERSPECTIVE coefficients mapping dst -> src."""
    A = np.zeros((8, 8), dtype=np.float64)
    B = np.zeros(8, dtype=np.float64)
    for i in range(4):
        dx, dy = dst_pts[i]
        sx, sy = src_pts[i]
        A[2 * i]     = [dx, dy, 1.0, 0.0, 0.0, 0.0, -dx * sx, -dy * sx]
        A[2 * i + 1] = [0.0, 0.0, 0.0, dx, dy, 1.0, -dx * sy, -dy * sy]
        B[2 * i]     = sx
        B[2 * i + 1] = sy
    return tuple(np.linalg.solve(A, B).tolist())

def paste_3d_layer(canvas_im, sprite_im, cx, cy, scale=1.0, rx_deg=0.0, ry_deg=0.0, rz_deg=0.0, opacity=1.0, blur_px=0.0, focal=1350.0):
    """
    Renders any RGBA sprite as a true 3D layer in camera space (rotateX, rotateY, rotateZ, subpixel scale & position)!
    Falls back to fast subpixel affine when rx_deg == ry_deg == rz_deg == 0.
    """
    if opacity <= 0.008 or scale <= 0.02:
        return
    im = sprite_im
    if blur_px >= 0.55:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(10.0, blur_px)))

    sw, sh = im.size
    if abs(rx_deg) < 0.08 and abs(ry_deg) < 0.08 and abs(rz_deg) < 0.08:
        out_w = int(math.ceil(sw * scale)) + 6
        out_h = int(math.ceil(sh * scale)) + 6
        x0 = int(math.floor(cx - out_w * 0.5))
        y0 = int(math.floor(cy - out_h * 0.5))
        inv_s = 1.0 / scale
        c_off = sw * 0.5 - (cx - x0) * inv_s
        f_off = sh * 0.5 - (cy - y0) * inv_s
        warped = im.transform((out_w, out_h), Image.Transform.AFFINE, (inv_s, 0.0, c_off, 0.0, inv_s, f_off), resample=Image.Resampling.BICUBIC)
    else:
        rx = math.radians(rx_deg)
        ry = math.radians(ry_deg)
        rz = math.radians(rz_deg)
        Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]], dtype=np.float64)
        Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]], dtype=np.float64)
        Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]], dtype=np.float64)
        Rmat = Rz @ Ry @ Rx

        hw, hh = sw * 0.5 * scale, sh * 0.5 * scale
        corners_3d = np.array([[-hw, -hh, 0.0], [hw, -hh, 0.0], [hw, hh, 0.0], [-hw, hh, 0.0]], dtype=np.float64)
        rot = corners_3d @ Rmat.T
        proj_x = cx + (rot[:, 0] * focal) / np.maximum(200.0, focal + rot[:, 2])
        proj_y = cy + (rot[:, 1] * focal) / np.maximum(200.0, focal + rot[:, 2])

        x0 = int(math.floor(proj_x.min())) - 4
        y0 = int(math.floor(proj_y.min())) - 4
        x1 = int(math.ceil(proj_x.max())) + 4
        y1 = int(math.ceil(proj_y.max())) + 4
        out_w, out_h = max(8, x1 - x0), max(8, y1 - y0)

        dst_pts = [(float(proj_x[i] - x0), float(proj_y[i] - y0)) for i in range(4)]
        src_pts = [(0.0, 0.0), (float(sw), 0.0), (float(sw), float(sh)), (0.0, float(sh))]
        coeffs = _solve_homography_8(src_pts, dst_pts)
        warped = im.transform((out_w, out_h), Image.Transform.PERSPECTIVE, coeffs, resample=Image.Resampling.BICUBIC)

    if opacity < 0.996:
        arr = np.array(warped)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        warped = Image.fromarray(arr, "RGBA")

    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(canvas_im.width, x0 + warped.width), min(canvas_im.height, y0 + warped.height)
    if dx1 > dx0 and dy1 > dy0:
        canvas_im.alpha_composite(warped.crop((dx0 - x0, dy0 - y0, dx1 - x0, dy1 - y0)), dest=(dx0, dy0))

def fit_cover_subpixel(rgb_arr, target_w, target_h, zoom=1.0, pan_x=0.0, pan_y=0.0):
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    inv_s = 1.0 / base_scale
    cx_src = sw * 0.5 + pan_x * sw
    cy_src = sh * 0.5 + pan_y * sh
    c = cx_src - (target_w * 0.5) * inv_s
    f = cy_src - (target_h * 0.5) * inv_s
    return Image.fromarray(rgb_arr, "RGB").transform(
        (target_w, target_h), Image.Transform.AFFINE, (inv_s, 0.0, c, 0.0, inv_s, f), resample=Image.Resampling.BICUBIC
    )

# ======================================================================
# 3. 5-STOP GRADIENT TYPOGRAPHY + 2-LAYER STROKE + SPECULAR SHEEN SWEEP
# ======================================================================
_grad_sprite_cache = {}
def render_5stop_grad_sprite(text, font_path, size, palette="gold", stroke_col=(18, 22, 34), stroke_w=6, extrude_col=(10, 14, 24), extrude_dy=3, shadow_alpha=95, glow_alpha=55):
    """
    Implements the exact 2-layer architecture from gradient-text-presets.css:
      - Layer 1 (.grad-back): Drop shadow + 3D depth extrusion + crisp outer stroke (never eats into gradient!)
      - Layer 2 (.grad-front): 5-stop metallic/satin linear gradient fill!
    """
    key = (text, font_path, int(round(size)), palette, stroke_col, stroke_w, extrude_col, extrude_dy, shadow_alpha, glow_alpha)
    if key in _grad_sprite_cache:
        return _grad_sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(stroke_w + 26)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    stops = GRAD_PALETTES.get(palette, GRAD_PALETTES["gold"])
    mid_col = stops[len(stops) // 2][1]

    if glow_alpha > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(1, stroke_w // 2), stroke_fill=255)
        gb = np.array(gm.filter(ImageFilter.GaussianBlur(radius=9.0)), dtype=np.float32) / 255.0
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0], ga[:, :, 1], ga[:, :, 2] = mid_col
        ga[:, :, 3] = np.clip(gb * glow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 6), text, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=6.0)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (12, 16, 28)
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    # 3D extruded rim + outer stroke (.grad-back)
    if extrude_dy > 0 and extrude_col is not None:
        ex = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(ex).text((ox + 1, oy + extrude_dy), text, font=font, fill=(*extrude_col, 245), stroke_width=stroke_w, stroke_fill=(*extrude_col, 245))
        base = Image.alpha_composite(base, ex)

    if stroke_w > 0 and stroke_col is not None:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        base = Image.alpha_composite(base, st_im)

    # Pure glyph interior (.grad-front) with 5-stop interpolated vertical gradient!
    mask_im = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), text, font=font, fill=255)
    arr_m = np.array(mask_im, dtype=np.float32) / 255.0

    ys_on = np.where(arr_m.max(axis=1) > 0.15)[0]
    y_min = float(ys_on[0]) if len(ys_on) else float(pad)
    y_max = float(ys_on[-1]) if len(ys_on) else float(ch - pad)
    u_y = np.clip((np.arange(ch, dtype=np.float32) - y_min) / max(1.0, y_max - y_min), 0.0, 1.0)

    pos_arr = np.array([p for p, _ in stops], dtype=np.float32)
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.float32)
    for c in range(3):
        val_arr = np.array([col[c] for _, col in stops], dtype=np.float32)
        grad_rgb[:, :, c] = np.interp(u_y, pos_arr, val_arr)[:, None]

    fill_rgba = np.dstack([np.clip(grad_rgb, 0, 255).astype(np.uint8), (arr_m * 255.0).astype(np.uint8)])
    base = Image.alpha_composite(base, Image.fromarray(fill_rgba, "RGBA"))

    if len(_grad_sprite_cache) > 850:
        _grad_sprite_cache.clear()
    _grad_sprite_cache[key] = (base, arr_m)
    return base, arr_m

def apply_sheen_sweep(sprite_tuple, sheen_phase):
    """Applies a 115-degree animated specular light sweep ONLY across the glyph interior!"""
    base, arr_m = sprite_tuple
    if sheen_phase < -0.25 or sheen_phase > 1.25:
        return base
    ch, cw = arr_m.shape
    yy, xx = np.ogrid[0:ch, 0:cw]
    diag = (xx.astype(np.float32) * 0.90 + yy.astype(np.float32) * 0.42) / max(1.0, cw * 0.90 + ch * 0.42)
    band = np.exp(-((diag - sheen_phase) ** 2) / 0.0055) * 195.0 * arr_m
    if band.max() < 3.0:
        return base
    out = np.array(base, dtype=np.float32)
    out[:, :, 0] = np.clip(out[:, :, 0] + band, 0, 255)
    out[:, :, 1] = np.clip(out[:, :, 1] + band * 0.98, 0, 255)
    out[:, :, 2] = np.clip(out[:, :, 2] + band * 0.94, 0, 255)
    return Image.fromarray(out.astype(np.uint8), "RGBA")

# ======================================================================
# 4. 3D STACKED GLASS CARDS, BACKPLATES & BADGES (MULTI-LAYER DEPTH!)
# ======================================================================
_glass_backplate_cache = {}
def get_3d_glass_backplate(w, h, radius=42, tint_rgb=(255, 238, 246), alpha_fill=95, rim_rgb=(255, 255, 255)):
    k = (w, h, radius, tint_rgb, alpha_fill, rim_rgb)
    if k in _glass_backplate_cache:
        return _glass_backplate_cache[k]
    pad = 28
    cw, ch = w + pad * 2, h + pad * 2
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius=radius, fill=(14, 18, 34, 88))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    body = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([pad, pad, pad + w, pad + h], radius=radius, fill=(*tint_rgb, alpha_fill), outline=(*rim_rgb, 215), width=3)
    d.rounded_rectangle([pad + 5, pad + 5, pad + w - 5, pad + h - 5], radius=max(8, radius - 5), outline=(255, 255, 255, 95), width=1)
    im = Image.alpha_composite(im, body)
    _glass_backplate_cache[k] = im
    return im

def make_3d_video_card(vf_rgb, w, h, radius=38, rim_rgb=(255, 245, 225), sheen_u=-1.0, zoom=1.02, pan_x=0.0):
    crop = fit_cover_subpixel(vf_rgb, w, h, zoom=zoom, pan_x=pan_x)
    arr = np.array(crop, dtype=np.float32)
    if 0.0 <= sheen_u <= 1.0:
        yy, xx = np.ogrid[0:h, 0:w]
        diag = (xx.astype(np.float32) * 0.85 + yy.astype(np.float32) * 0.45) / (w * 0.85 + h * 0.45)
        pos = -0.2 + 1.4 * sheen_u
        sh_b = np.exp(-((diag - pos) ** 2) / 0.009) * 34.0
        arr = np.clip(arr + sh_b[:, :, None], 0, 255)

    pad = 26
    cw, ch = w + pad * 2, h + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius=radius, fill=(10, 16, 28, 108))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=13)))

    rm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    vlay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vlay.paste(Image.fromarray(arr.astype(np.uint8), "RGB"), (pad, pad), mask=rm)
    card = Image.alpha_composite(card, vlay)
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius=radius, outline=(*rim_rgb, 238), width=3)
    return card

_badge_3d_cache = {}
def get_3d_gradient_pill_badge(label_txt, palette="gold", font_sz=26, dark_glass=True, dot_rgb=(92, 224, 181)):
    k = (label_txt, palette, font_sz, dark_glass, dot_rgb)
    if k in _badge_3d_cache:
        return _badge_3d_cache[k]
    sp, _ = render_5stop_grad_sprite(
        label_txt, FONT_BE_XBOLD, font_sz, palette=palette,
        stroke_col=(12, 16, 26) if dark_glass else (255, 255, 255),
        stroke_w=4 if dark_glass else 5, extrude_dy=2, shadow_alpha=45, glow_alpha=35
    )
    sp_c = sp.crop(sp.getbbox())
    pw = min(1010, sp_c.width + 76)
    ph = max(56, sp_c.height + 22)
    pad = 18
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 6, pad + pw, pad + ph + 6], radius=ph // 2, fill=(12, 16, 28, 92))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=8)))

    d = ImageDraw.Draw(im)
    bg_fill = (20, 24, 38, 212) if dark_glass else (250, 252, 250, 238)
    rim_col = (255, 248, 230, 228) if dark_glass else (92, 215, 168, 235)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=ph // 2, fill=bg_fill, outline=rim_col, width=2)
    cy = pad + ph // 2
    d.ellipse([pad + 20, cy - 6, pad + 32, cy + 6], fill=(*dot_rgb, 255))
    paste_3d_layer(im, sp_c, pad + pw * 0.5 + 10, cy, scale=1.0)
    _badge_3d_cache[k] = im
    return im

_orbit_ring_cache = None
def get_3d_orbital_ring():
    global _orbit_ring_cache
    if _orbit_ring_cache is not None:
        return _orbit_ring_cache
    rw, rh = 860, 340
    im = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([24, 24, rw - 24, rh - 24], outline=(252, 225, 129, 175), width=5)
    d.ellipse([48, 44, rw - 48, rh - 44], outline=(92, 224, 181, 135), width=3)
    glow = im.filter(ImageFilter.GaussianBlur(radius=9))
    _orbit_ring_cache = Image.alpha_composite(glow, im)
    return _orbit_ring_cache

_brand_card_3d_cache = {}
def get_3d_luxury_brand_card(line1, line2, line3, pal2="emerald"):
    k = (line1, line2, line3, pal2)
    if k in _brand_card_3d_cache:
        return _brand_card_3d_cache[k]
    pw, ph = 948, 268
    pad = 26
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + pw, pad + ph + 10], radius=46, fill=(14, 24, 22, 96))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, pw, dtype=np.float32)[None, :]
    lift = np.exp(-(xx * xx * 1.2 + (yy - 0.35) ** 2 * 1.8))
    bg = np.zeros((ph, pw, 3), dtype=np.uint8)
    bg[:, :, 0] = np.clip(22 + 24 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 1] = np.clip(42 + 38 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 2] = np.clip(36 + 30 * lift, 0, 255).astype(np.uint8)
    bg_im = Image.fromarray(bg, "RGB").convert("RGBA")

    rib = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rib)
    rd.line([(-20, 40), (220, ph + 20)], fill=(252, 225, 129, 95), width=3)
    rd.line([(pw + 20, 40), (pw - 220, ph + 20)], fill=(92, 224, 181, 95), width=3)
    bg_im = Image.alpha_composite(bg_im, rib)

    rm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=46, fill=255)
    bl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bl.paste(bg_im, (pad, pad), mask=rm)
    card = Image.alpha_composite(card, bl)
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=46, outline=(252, 225, 129, 232), width=3)
    ImageDraw.Draw(card).rounded_rectangle([pad + 6, pad + 6, pad + pw - 7, pad + ph - 7], radius=40, outline=(92, 224, 181, 140), width=1)

    sz2 = 52 if len(line2) <= 18 else 41
    s1, _ = render_5stop_grad_sprite(line1, FONT_BE_BOLD, 24, palette="pearl", stroke_col=(10, 18, 16), stroke_w=3, extrude_dy=0, shadow_alpha=40, glow_alpha=0)
    s2, _ = render_5stop_grad_sprite(line2, FONT_MONTS_BLK, sz2, palette=pal2, stroke_col=(10, 18, 16), stroke_w=6, extrude_dy=3, shadow_alpha=85, glow_alpha=55)
    s3, _ = render_5stop_grad_sprite(line3, FONT_BE_XBOLD, 26, palette="gold", stroke_col=(10, 18, 16), stroke_w=4, extrude_dy=1, shadow_alpha=50, glow_alpha=25)

    paste_3d_layer(card, s1, cw * 0.5, pad + 48)
    paste_3d_layer(card, s2, cw * 0.5, pad + 128)
    ImageDraw.Draw(card).line([(cw // 2 - 250, pad + 184), (cw // 2 + 250, pad + 184)], fill=(252, 225, 129, 155), width=2)
    paste_3d_layer(card, s3, cw * 0.5, pad + 220)
    _brand_card_3d_cache[k] = card
    return card

# ======================================================================
# 5. BRIGHT SOURCE WALL CLEANUP & SMOOTH OPTICAL TRANSITION HELPERS
# ======================================================================
def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.95) * 1.018, 0.0, 1.0)
    return (
        np.clip(y * 255.0 * 1.014, 0, 255).astype(np.uint8),
        np.clip(y * 255.0 * 1.006, 0, 255).astype(np.uint8),
        np.clip(y * 255.0 * 0.996, 0, 255).astype(np.uint8),
    )
BRIGHT_LUT = _build_bright_lut()

def polish_bright_frame(rgb):
    out = np.empty_like(rgb)
    out[:, :, 0] = BRIGHT_LUT[0][rgb[:, :, 0]]
    out[:, :, 1] = BRIGHT_LUT[1][rgb[:, :, 1]]
    out[:, :, 2] = BRIGHT_LUT[2][rgb[:, :, 2]]
    return out

_wall_clean_mask = None
def clean_studio_source_backdrop(fg_rgb):
    """Keeps 100% of the real room's bright lighting, green plant, chair & desk while softly diffusing ONLY the cropped red/blue wall letters (y=0..760) into a clean studio cream backdrop!"""
    global _wall_clean_mask
    if _wall_clean_mask is None:
        yy = np.arange(H, dtype=np.float32)[:, None]
        u = np.clip((765.0 - yy) / 145.0, 0.0, 1.0)
        _wall_clean_mask = (u * u * (3.0 - 2.0 * u))[:, :, None]

    top_patch = Image.fromarray(fg_rgb[0:820, :], "RGB").filter(ImageFilter.GaussianBlur(radius=42))
    tp_np = np.array(top_patch, dtype=np.float32)
    lum = tp_np[:, :, 0:1] * 0.30 + tp_np[:, :, 1:2] * 0.59 + tp_np[:, :, 2:3] * 0.11
    cream = np.concatenate([lum * 0.32 + 168.0, lum * 0.32 + 167.0, lum * 0.31 + 164.0], axis=2)
    out = fg_rgb.astype(np.float32).copy()
    out[0:820] = out[0:820] * (1.0 - _wall_clean_mask[0:820]) + cream * _wall_clean_mask[0:820]
    return np.clip(out, 0, 255).astype(np.uint8)

def optical_soft_transition(base_rgba_im, cutaway_rgba_im, u_cut):
    """
    Smooth After Effects Optical Focus + Warm Luma-Bloom Cross-Dissolve (NEVER harsh!):
    u_cut in [0..1]: 0 = 100% base, 1 = 100% cutaway.
    """
    if u_cut <= 0.004:
        return base_rgba_im
    if u_cut >= 0.996:
        return cutaway_rgba_im
    bell = math.sin(u_cut * math.pi)
    rad = bell * 9.5
    b_im = base_rgba_im.filter(ImageFilter.GaussianBlur(radius=rad * u_cut)) if rad * u_cut >= 0.6 else base_rgba_im
    c_im = cutaway_rgba_im.filter(ImageFilter.GaussianBlur(radius=rad * (1.0 - u_cut))) if rad * (1.0 - u_cut) >= 0.6 else cutaway_rgba_im
    a_b = np.array(b_im, dtype=np.float32)
    a_c = np.array(c_im, dtype=np.float32)
    mix = a_b * (1.0 - u_cut) + a_c * u_cut
    # Subtle warm champagne optical bloom (+18 max, never blinding white!)
    bloom = bell * 18.0
    mix[:, :, 0] = np.clip(mix[:, :, 0] + bloom * 1.05, 0, 255)
    mix[:, :, 1] = np.clip(mix[:, :, 1] + bloom * 1.00, 0, 255)
    mix[:, :, 2] = np.clip(mix[:, :, 2] + bloom * 0.88, 0, 255)
    mix[:, :, 3] = 255.0
    return Image.fromarray(mix.astype(np.uint8), "RGBA")

# ======================================================================
# 6. CAMERA ZOOM & SEMANTIC 5-STOP GRADIENT SUBTITLES
# ======================================================================
ZOOM_KEYS = [
    (0.00, 1.048),
    (3.32, 1.020),
    (9.22, 1.068),   # Direct Source close-up as she raises finger!
    (13.55, 1.030),
    (17.75, 1.022),
    (24.30, 1.062),  # Direct Source close-up as she presents Hằng Thu box!
    (31.10, 1.024),
    (39.28, 1.045),
    (44.15, 1.032),
    (51.45, 1.012),
]

def get_butter_zoom(t):
    if t <= ZOOM_KEYS[0][0]:
        return ZOOM_KEYS[0][1]
    for i in range(1, len(ZOOM_KEYS)):
        t0, z0 = ZOOM_KEYS[i - 1]
        t1, z1 = ZOOM_KEYS[i]
        if t <= t1:
            u = quintic_smooth(min(1.0, (t - t0) / min(0.90, max(0.35, (t1 - t0) * 0.45))))
            return z0 + (z1 - z0) * u
    return ZOOM_KEYS[-1][1]

def load_captions_htpm3():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and (w["start"] + w["end"]) * 0.5 >= 3.30
    ]

    phrases = []
    cur_p = []
    for w in words:
        txt, ws, we = w
        if cur_p:
            gap = ws - cur_p[-1][2]
            prev_txt = cur_p[-1][0]
            dur_so_far = cur_p[-1][2] - cur_p[0][1]
            if gap >= 0.42 or (re.search(r"[.?!…;:]$", prev_txt) and len(cur_p) >= 3):
                phrases.append(cur_p); cur_p = []
            elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 4 or dur_so_far >= 1.40):
                phrases.append(cur_p); cur_p = []
            elif len(cur_p) >= 8 or sum(len(x[0]) + 1 for x in cur_p) + len(txt) > 36:
                phrases.append(cur_p); cur_p = []
        cur_p.append(w)
    if cur_p:
        phrases.append(cur_p)

    merged = []
    for p in phrases:
        if merged and len(p) <= 2 and (p[0][1] - merged[-1][-1][2]) < 0.50 and len(merged[-1]) + len(p) <= 9:
            merged[-1].extend(p)
        else:
            merged.append(p)

    def split_balanced(p):
        tot_c = sum(len(x[0]) + 1 for x in p) - 1
        if len(p) <= 4 and tot_c <= 20:
            return [p]
        bk, bd = max(1, len(p) // 2), 9999
        for k in range(1, len(p)):
            c1 = sum(len(x[0]) + 1 for x in p[:k]) - 1
            c2 = sum(len(x[0]) + 1 for x in p[k:]) - 1
            d = abs(c1 - c2) + (6 if max(c1, c2) > 22 else 0)
            if d < bd:
                bd, bk = d, k
        return [p[:bk], p[bk:]]

    GOLD_W    = {"Hằng", "Thu", "Acid", "Lactic", "Niacinamide", "Glycerin", "chìa", "khóa"}
    EMERALD_W = {"phục", "hồi.", "hồi", "cân", "bằng", "pH", "ẩm,", "Cam", "Thảo", "Cúc", "La", "Mã", "dịu", "nhẹ", "nhàng"}
    ROSE_W    = {"ngứa", "khí", "hư", "bất", "thường.", "nhạy", "cảm,", "nấm", "khuẩn", "hạn", "chế", "tái", "phát"}

    cap_groups = []
    for i, p in enumerate(merged):
        t0 = max(3.32, p[0][1] - 0.05)
        last_end = p[-1][2]
        nxt_s = merged[i + 1][0][1] if i + 1 < len(merged) else 51.30
        min_hold = max(last_end + 0.42, t0 + 1.55)
        t1 = min(nxt_s - 0.04, max(min_hold, last_end + 0.65))
        if t1 <= last_end + 0.12:
            t1 = min(nxt_s - 0.02, last_end + 0.25)
        cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced(p)})
    return cap_groups, GOLD_W, EMERALD_W, ROSE_W

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
    frames, nb = [], vw * vh * 3
    while True:
        b = proc.stdout.read(nb)
        if len(b) < nb:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)))
    proc.stdout.close()
    proc.wait()
    return frames

def get_clip_frame(clips, key, t_rel):
    arr_list = clips.get(key)
    if not arr_list:
        return np.full((720, 1280, 3), 240, dtype=np.uint8)
    n = len(arr_list)
    idx_raw = int(max(0.0, t_rel) * FPS)
    cycle = 2 * (n - 1) if n > 2 else 1
    pos = idx_raw % cycle
    idx = pos if pos < n else cycle - pos
    return arr_list[min(n - 1, max(0, idx))]

def make_live_speaker_pip(fg_rgb, clean_bg_rgb, m_arr, pw=256, ph=340):
    """Creates a sleek 3D glass-rimmed Picture-in-Picture portrait of the live Pharmacist over clean studio background!"""
    a = m_arr[540:1420, 210:870, None]
    comp_sub = np.clip(clean_bg_rgb[540:1420, 210:870] * (1.0 - a) + fg_rgb[540:1420, 210:870] * a, 0, 255).astype(np.uint8)
    im = fit_cover_subpixel(comp_sub, pw, ph, zoom=1.02)
    pad = 18
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + pw, pad + ph + 8], radius=34, fill=(10, 16, 26, 118))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=10)))
    rm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=34, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(im, (pad, pad), mask=rm)
    card = Image.alpha_composite(card, vl)
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=34, outline=(92, 224, 181, 240), width=3)
    return card

# ======================================================================
# 7. MAIN AFTER-EFFECTS 3D COMPOSITOR LOOP (1,543 FRAMES @ 30FPS)
# ======================================================================
def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [2.30, 6.20, 12.10, 15.60, 21.80, 28.20, 36.90, 41.80, 48.20]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    clip_specs = [
        ("htpm3_recur_worry",          1280, 720),
        ("htpm3_barrier_vertical",     1080, 1920),
        ("htpm3_ph_barrier",           1280, 720),
        ("htpm3_microbe_grow",         1280, 720),
        ("htpm3_botanical_serum",      1280, 720),
        ("htpm3_viendat_wide",         1280, 720),
        ("htpm3_viendat_vertical_hero",1080, 1920),
        ("htpm3_harmony_bg",           1280, 720),
    ]
    clips = {}
    for ck, cw_k, ch_k in clip_specs:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if os.path.exists(vp):
            clips[ck] = load_vid_frames_wh(vp, cw_k, ch_k)
            print(f"Loaded {ck}: {len(clips[ck])} frames ({cw_k}x{ch_k})")
        else:
            print(f"WARNING missing {vp}")

    cap_groups, GOLD_W, EMERALD_W, ROSE_W = load_captions_htpm3()
    legal_sp, _ = render_5stop_grad_sprite(
        "Sản phẩm hỗ trợ chăm sóc chuyên biệt • Đọc kỹ hướng dẫn sử dụng trước khi dùng",
        FONT_BE_MED, 19, palette="pearl", stroke_col=(16, 20, 28), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0
    )

    # Pre-build crisp Closing Ribbon with 5-stop Emerald & Gold Gradient!
    cta_card = get_3d_gradient_pill_badge(
        "Viên Đặt Phụ Khoa Hằng Thu  •  Phục hồi & Cân bằng pH tự nhiên",
        palette="gold", font_sz=24, dark_glass=True, dot_rgb=(92, 224, 181)
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)

    raw_vid_out = os.path.join(PROJ_DIR, "_htpm3_ae3d_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    yy_g, xx_g = np.ogrid[0:H, 0:W]
    desk_mask = np.clip((yy_g.astype(np.float32) - 1355.0) / 55.0, 0.0, 1.0)
    hand_box_guard = np.clip((380.0 - xx_g.astype(np.float32)) / 55.0, 0.0, 1.0) * np.clip((yy_g.astype(np.float32) - 1150.0) / 55.0, 0.0, 1.0)

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

        # 1. Subpixel-Smooth Camera Zoom on Pharmacist A-Roll
        z = get_butter_zoom(t)
        fg_im = fit_cover_subpixel(rgb, W, H, zoom=z, pan_y=-0.035 * (z - 1.0))
        m_rgb = np.repeat((matte * 255.0).astype(np.uint8)[:, :, None], 3, axis=2)
        m_im  = fit_cover_subpixel(m_rgb, W, H, zoom=z, pan_y=-0.035 * (z - 1.0)).convert("L")
        fg_rgb = np.array(fg_im)
        m_arr  = np.array(m_im, dtype=np.float32) / 255.0

        # Preserve 100% crisp authentic Direct Source room ("lồng source trực tiếp"!)
        clean_bg_rgb = fg_rgb
        base_im = Image.fromarray(clean_bg_rgb, "RGB").convert("RGBA")

        # ==================================================================
        # 2. INTERLEAVED DIRECT SOURCE × 3D STACKED OVERLAYS BEHIND SPEAKER
        # ==================================================================
        # SCENE 1 (0.00 - 3.32s): DIRECT SOURCE + 3D ORBITAL HALO & STACKED 3D GLASS BADGES BEHIND SPEAKER!
        if 0.00 <= t < 3.35:
            u_in, u_out, op, bl = ae_in_out(t, 0.04, 3.34, d_in=0.42, d_out=0.38)
            if op > 0.01:
                orb = get_3d_orbital_ring()
                paste_3d_layer(base_im, orb, 540.0, 560.0, scale=0.92 + 0.08 * u_in, rx_deg=18.0, ry_deg=math.sin(t * 1.6) * 8.0, rz_deg=-6.0 + t * 5.0, opacity=op * 0.85, blur_px=bl)
                b_left  = get_3d_gradient_pill_badge("ĐIỀU TRỊ XONG", palette="emerald", font_sz=24)
                b_right = get_3d_gradient_pill_badge("SAO VẪN TÁI LẠI?", palette="rose_satin", font_sz=24, dot_rgb=(249, 106, 181))
                paste_3d_layer(base_im, b_left,  250.0 - (1.0 - u_in) * 55.0, 385.0 + math.sin(t * 2.0) * 6.0, scale=0.88 + 0.12 * u_in, ry_deg=11.0, rz_deg=-2.5, opacity=op, blur_px=bl)
                if t >= 0.45:
                    u2_i, u2_o, op2, bl2 = ae_in_out(t, 0.45, 3.34, d_in=0.42, d_out=0.38)
                    paste_3d_layer(base_im, b_right, 825.0 + (1.0 - u2_i) * 55.0, 315.0 + math.cos(t * 2.0) * 6.0, scale=0.88 + 0.12 * u2_i, ry_deg=-11.0, rz_deg=2.5, opacity=op2, blur_px=bl2)

        # SCENE 2 (3.32 - 9.24s): 3D STACKED PARALLAX OVERLAY #1 (Backplate + Tilted Video Card + Floating 3D Badge!)
        if 3.28 <= t < 9.28:
            u_in, u_out, op, bl = ae_in_out(t, 3.30, 9.24, d_in=0.50, d_out=0.44, overshoot=1.16)
            if op > 0.01:
                vf = get_clip_frame(clips, "htpm3_recur_worry", t - 3.30)
                # Plane -2: Tilted Frosted Rose-Sapphire 3D Glass Backplate
                bp = get_3d_glass_backplate(950, 680, radius=42, tint_rgb=(245, 228, 240), alpha_fill=105, rim_rgb=(255, 198, 224))
                paste_3d_layer(
                    base_im, bp, 520.0 - (1.0 - u_in) * 65.0, 445.0 + (1.0 - u_out) * (-24.0),
                    scale=0.90 + 0.10 * u_in, rx_deg=2.5, ry_deg=-8.5 + (1.0 - u_in) * (-8.0), rz_deg=-1.8, opacity=op * 0.90, blur_px=bl
                )
                # Plane -1: Primary 3D Perspective Cinema Card with Specular Sweep
                sheen_u = ((t - 3.5) % 4.2) / 2.2
                vcard = make_3d_video_card(vf, 940, 670, radius=38, rim_rgb=(255, 244, 228), sheen_u=sheen_u, zoom=1.01 + 0.04 * ((t - 3.3) / 6.0))
                paste_3d_layer(
                    base_im, vcard, 548.0 + (1.0 - u_in) * 70.0, 428.0 + math.sin(t * 1.4) * 4.5,
                    scale=(0.88 + 0.12 * u_in) * (0.94 + 0.06 * u_out),
                    rx_deg=-2.0, ry_deg=5.5 + (1.0 - u_in) * 11.0 - (1.0 - u_out) * 9.0, rz_deg=0.8,
                    opacity=op, blur_px=bl
                )

        # SCENE 3 (9.22 - 13.70s): DIRECT SOURCE A-ROLL CLOSE-UP + STAGGERED 3D KINETIC GRADIENT CARDS!
        if 9.20 <= t < 13.80:
            u_in1, u_out1, op1, bl1 = ae_in_out(t, 9.28, 13.68, d_in=0.45, d_out=0.40)
            if op1 > 0.01:
                orb = get_3d_orbital_ring()
                paste_3d_layer(base_im, orb, 540.0, 470.0, scale=0.96, rx_deg=15.0, ry_deg=-7.0, rz_deg=t * 4.5, opacity=op1 * 0.65, blur_px=bl1)
                c1 = get_3d_gradient_pill_badge("ĐIỀU TRỊ CHƯA ĐỦ?", palette="coral", font_sz=27, dot_rgb=(255, 159, 90))
                paste_3d_layer(
                    base_im, c1, 340.0 - (1.0 - u_in1) * 60.0, 158.0 + math.sin(t * 1.8) * 5.0,
                    scale=0.90 + 0.10 * u_in1, ry_deg=9.5 + (1.0 - u_in1) * 10.0, rz_deg=-1.5, opacity=op1, blur_px=bl1
                )
            if t >= 11.35:
                u_in2, u_out2, op2, bl2 = ae_in_out(t, 11.35, 13.72, d_in=0.45, d_out=0.38, overshoot=1.24)
                c2 = get_3d_luxury_brand_card(
                    "NGUYÊN NHÂN CỐT LÕI SAU ĐIỀU TRỊ",
                    "CHƯA PHỤC HỒI",
                    "HỆ VI SINH & HÀNG RÀO BẢO VỆ TỰ NHIÊN",
                    pal2="emerald"
                )
                paste_3d_layer(
                    base_im, c2, 540.0, 412.0 + (1.0 - u_in2) * 38.0 - (1.0 - u_out2) * 22.0,
                    scale=(0.86 + 0.14 * u_in2) * (0.94 + 0.06 * u_out2),
                    rx_deg=(1.0 - u_in2) * 8.0, ry_deg=-4.5 + (1.0 - u_in2) * (-9.0),
                    opacity=op2, blur_px=bl2
                )

        # SCENE 5 (17.70 - 24.32s): 2-CARD ASYMMETRIC 3D PERSPECTIVE PARALLAX STACK BEHIND SPEAKER!
        if 17.65 <= t < 24.34:
            u1_i, u1_o, op1, bl1 = ae_in_out(t, 17.72, 24.30, d_in=0.50, d_out=0.42)
            if op1 > 0.01:
                vf_a = get_clip_frame(clips, "htpm3_ph_barrier", t - 17.72)
                card_a = make_3d_video_card(vf_a, 690, 480, radius=34, rim_rgb=(166, 229, 255), sheen_u=((t - 17.8) % 4.0) / 2.2)
                shift_a = quintic_smooth(clamp01((t - 20.60) / 0.55))
                paste_3d_layer(
                    base_im, card_a,
                    430.0 - 75.0 * shift_a - (1.0 - u1_i) * 70.0,
                    295.0 - 18.0 * shift_a + math.sin(t * 1.5) * 4.0,
                    scale=(0.88 + 0.12 * u1_i) * (0.95 + 0.05 * u1_o),
                    rx_deg=2.0, ry_deg=7.5 + (1.0 - u1_i) * 10.0, rz_deg=-1.5,
                    opacity=op1, blur_px=bl1
                )
            if t >= 20.60:
                u2_i, u2_o, op2, bl2 = ae_in_out(t, 20.60, 24.30, d_in=0.50, d_out=0.42, overshoot=1.22)
                vf_b = get_clip_frame(clips, "htpm3_microbe_grow", t - 20.60)
                card_b = make_3d_video_card(vf_b, 640, 450, radius=34, rim_rgb=(255, 185, 148), sheen_u=((t - 20.8) % 3.8) / 2.0)
                paste_3d_layer(
                    base_im, card_b,
                    705.0 + (1.0 - u2_i) * 75.0,
                    590.0 + (1.0 - u2_i) * 40.0 + math.cos(t * 1.6) * 4.5,
                    scale=(0.86 + 0.14 * u2_i) * (0.94 + 0.06 * u2_o),
                    rx_deg=-2.5, ry_deg=-7.5 - (1.0 - u2_i) * 11.0, rz_deg=1.4,
                    opacity=op2, blur_px=bl2
                )

        # SCENE 6 (24.30 - 31.12s): DIRECT SOURCE A-ROLL + 3D LAYERED ACID LACTIC CARD & FLOATING CAPSULES!
        if 24.28 <= t < 31.15:
            ui, uo, op, bl = ae_in_out(t, 24.32, 31.10, d_in=0.48, d_out=0.42, overshoot=1.20)
            if op > 0.01:
                orb = get_3d_orbital_ring()
                paste_3d_layer(base_im, orb, 540.0, 420.0, scale=1.0, rx_deg=16.0, ry_deg=6.0, rz_deg=-t * 5.0, opacity=op * 0.78, blur_px=bl)
                ac_card = get_3d_luxury_brand_card(
                    "THÀNH PHẦN CHỦ ĐẠO ƯU TIÊN",
                    "ACID LACTIC",
                    "HỖ TRỢ DUY TRÌ & CÂN BẰNG ĐỘ pH SINH LÝ",
                    pal2="gold"
                )
                paste_3d_layer(
                    base_im, ac_card, 540.0, 360.0 + (1.0 - ui) * (-36.0) - (1.0 - uo) * 22.0,
                    scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo),
                    rx_deg=-2.0 + (1.0 - ui) * 8.0, ry_deg=4.5 * math.sin((t - 24.3) * 0.9),
                    opacity=op, blur_px=bl
                )
                if t >= 28.10:
                    ui_p, uo_p, op_p, bl_p = ae_in_out(t, 28.10, 31.10, d_in=0.42, d_out=0.38)
                    b_ph = get_3d_gradient_pill_badge("CÂN BẰNG pH TỰ NHIÊN", palette="emerald", font_sz=24)
                    paste_3d_layer(base_im, b_ph, 755.0 + (1.0 - ui_p) * 50.0, 565.0, scale=0.90 + 0.10 * ui_p, ry_deg=-8.0, opacity=op_p, blur_px=bl_p)

        # SCENE 7 (31.10 - 39.32s): 3D STACKED BOTANICAL ESSENCE SHOWCASE BEHIND SPEAKER!
        if 31.08 <= t < 39.35:
            ui, uo, op, bl = ae_in_out(t, 31.12, 39.30, d_in=0.50, d_out=0.44, overshoot=1.16)
            if op > 0.01:
                vf_bot = get_clip_frame(clips, "htpm3_botanical_serum", t - 31.12)
                bp_e = get_3d_glass_backplate(960, 690, radius=44, tint_rgb=(218, 250, 236), alpha_fill=105, rim_rgb=(132, 238, 194))
                paste_3d_layer(base_im, bp_e, 558.0 + (1.0 - ui) * 60.0, 448.0, scale=0.90 + 0.10 * ui, rx_deg=2.0, ry_deg=7.5, rz_deg=1.5, opacity=op * 0.88, blur_px=bl)
                vcard_b = make_3d_video_card(vf_bot, 948, 675, radius=40, rim_rgb=(252, 225, 129), sheen_u=((t - 31.3) % 4.4) / 2.3)
                paste_3d_layer(
                    base_im, vcard_b, 534.0 - (1.0 - ui) * 65.0, 428.0 + math.sin(t * 1.4) * 4.0,
                    scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo),
                    rx_deg=-1.8, ry_deg=-5.0 - (1.0 - ui) * 10.0, rz_deg=-0.6,
                    opacity=op, blur_px=bl
                )

        # SCENE 9 (44.10 - 51.45s): SUNLIT CHAMOMILE FINALE + 3D STACKED KEYWORD END-CARD!
        if t >= 44.08:
            ui, uo, op, bl = ae_in_out(t, 44.12, 51.42, d_in=0.52, d_out=0.40, overshoot=1.15)
            if op > 0.01:
                vf_fin = get_clip_frame(clips, "htpm3_botanical_serum", t - 44.12 + 2.0)
                fin_card = make_3d_video_card(vf_fin, 980, 720, radius=42, rim_rgb=(252, 225, 129), sheen_u=((t - 44.4) % 4.5) / 2.2, zoom=1.06)
                paste_3d_layer(base_im, fin_card, 540.0, 430.0 + (1.0 - ui) * (-28.0), scale=0.92 + 0.08 * ui, ry_deg=3.0 * math.sin(t * 0.8), opacity=op * 0.92, blur_px=bl + 2.5)
                if t >= 45.60:
                    ui_k, uo_k, op_k, bl_k = ae_in_out(t, 45.60, 51.38, d_in=0.48, d_out=0.40, overshoot=1.20)
                    end_c = get_3d_luxury_brand_card(
                        "CHĂM SÓC ĐÚNG SAU ĐIỀU TRỊ",
                        "HẠN CHẾ TÁI PHÁT",
                        "VIÊN ĐẶT PHỤ KHOA HẰNG THU • DỊU NHẸ TỰ NHIÊN",
                        pal2="gold"
                    )
                    paste_3d_layer(
                        base_im, end_c, 540.0, 385.0 + (1.0 - ui_k) * 32.0 - (1.0 - uo_k) * 18.0,
                        scale=(0.88 + 0.12 * ui_k) * (0.95 + 0.05 * uo_k),
                        rx_deg=(1.0 - ui_k) * 7.0, ry_deg=-3.5 * math.cos((t - 45.6) * 1.1),
                        opacity=op_k, blur_px=bl_k
                    )

        # ==================================================================
        # 3. RE-COMPOSITE PHARMACIST + DESK + HELD GREEN BOX IN FOREGROUND!
        # ==================================================================
        fg_guard = np.maximum(desk_mask, hand_box_guard if t >= 12.5 else 0.0)
        fg_alpha = np.maximum(m_arr, fg_guard)
        comp_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # Foreground Floating 3D Ingredient Capsules in Scene 7 (in front of video card, clear of face!)
        if 31.85 <= t < 39.25:
            ing_specs = [
                (31.90, "Niacinamide", "gold",    205.0, 240.0,  9.0),
                (33.00, "Glycerin",    "sapphire",875.0, 235.0, -9.0),
                (35.85, "Cam Thảo",    "emerald", 195.0, 585.0,  8.5),
                (36.70, "Cúc La Mã",   "gold",    880.0, 578.0, -8.5),
            ]
            for st_i, lbl_i, pal_i, ix, iy, iry in ing_specs:
                if t >= st_i:
                    ui_i, uo_i, op_i, bl_i = ae_in_out(t, st_i, 39.22, d_in=0.42, d_out=0.38, overshoot=1.24)
                    b_ing = get_3d_gradient_pill_badge(lbl_i, palette=pal_i, font_sz=25)
                    paste_3d_layer(
                        comp_im, b_ing,
                        ix + (1.0 - ui_i) * (-45.0 if ix < 540 else 45.0),
                        iy + math.sin((t - st_i) * 2.1) * 6.0 - (1.0 - uo_i) * 20.0,
                        scale=(0.84 + 0.16 * ui_i) * (0.92 + 0.08 * uo_i),
                        ry_deg=iry, opacity=op_i, blur_px=bl_i
                    )

        # Top Animated 3D Context Pills on Overlay Scenes (each with explicit In & Out!)
        top_pills = [
            (3.36,   9.20, "TÁI PHÁT NGỨA & KHÍ HƯ SAU VÀI TUẦN", "coral",   (255, 159, 90)),
            (17.78, 20.56, "ĐỘ pH MẤT CÂN BẰNG • NIÊM MẠC NHẠY CẢM", "sapphire",(104, 210, 255)),
            (20.64, 24.26, "NẤM & VI KHUẨN DỄ PHÁT TRIỂN TRỞ LẠI",   "coral",   (255, 159, 90)),
            (31.18, 39.24, "DƯỠNG ẨM & LÀM DỊU NIÊM MẠC TỰ NHIÊN",   "emerald", ( 92, 224, 181)),
            (44.20, 51.36, "CHÌA KHÓA HẠN CHẾ TÁI PHÁT BỀN VỮNG",    "gold",    (252, 225, 129)),
        ]
        for pst, pen, ptxt, ppal, pdot in top_pills:
            if pst <= t < pen:
                ui_t, uo_t, op_t, bl_t = ae_in_out(t, pst, pen, d_in=0.38, d_out=0.34, overshoot=1.16)
                tp_sp = get_3d_gradient_pill_badge(ptxt, palette=ppal, font_sz=21, dark_glass=True, dot_rgb=pdot)
                paste_3d_layer(
                    comp_im, tp_sp, 540.0, 68.0 + (1.0 - ui_t) * (-26.0) - (1.0 - uo_t) * 18.0,
                    scale=(0.90 + 0.10 * ui_t) * (0.94 + 0.06 * uo_t), rx_deg=(1.0 - ui_t) * 12.0,
                    opacity=op_t, blur_px=bl_t
                )

        # ==================================================================
        # 4. TWO FULL-SCREEN 9:16 IMMERSIVE CUTAWAYS WITH SOFT OPTICAL TRANSITIONS!
        #    ("lồng source trực tiếp với lớp phủ lên trên xen kẽ, chuyển cảnh không bị gắt")
        # ==================================================================
        in_cutaway = False
        # CUTAWAY #1 (13.60 - 17.75s): Full-Screen 9:16 3D Mucosal Barrier Visualization + 3D HUD + Live PIP!
        if 13.30 <= t <= 18.05:
            u_in_c  = quintic_smooth(clamp01((t - 13.30) / 0.52))
            u_out_c = quintic_smooth(clamp01((18.05 - t) / 0.52))
            u_cut = min(u_in_c, u_out_c)
            if u_cut > 0.005:
                in_cutaway = (u_cut > 0.5)
                vf_cut = get_clip_frame(clips, "htpm3_barrier_vertical", max(0.0, t - 13.30))
                cut_im = fit_cover_subpixel(vf_cut, W, H, zoom=1.01 + 0.04 * clamp01((t - 13.3) / 4.7)).convert("RGBA")
                # Subtle bottom gradient vignette so subtitles & 3D PIP pop cleanly
                vig = Image.new("RGBA", (W, 560), (0, 0, 0, 0))
                vy = np.linspace(0.0, 1.0, 560, dtype=np.float32)[:, None]
                va = np.zeros((560, W, 4), dtype=np.uint8)
                va[:, :, 0], va[:, :, 1], va[:, :, 2] = (10, 18, 30)
                va[:, :, 3] = (vy * vy * 188.0).astype(np.uint8)
                cut_im.alpha_composite(Image.fromarray(va, "RGBA"), dest=(0, H - 560))

                # 3D Stacked Header & Live Pharmacist PIP on the Full-Screen Cutaway
                ui_h, uo_h, op_h, bl_h = ae_in_out(t, 13.55, 17.85, d_in=0.45, d_out=0.38)
                if op_h > 0.01:
                    hdr = get_3d_luxury_brand_card(
                        "SAU KHI HẾT TRIỆU CHỨNG",
                        "MÔI TRƯỜNG CHƯA PHỤC HỒI",
                        "HÀNG RÀO NIÊM MẠC VẪN CÒN MỎNG & NHẠY CẢM",
                        pal2="sapphire"
                    )
                    paste_3d_layer(cut_im, hdr, 540.0, 245.0 + (1.0 - ui_h) * (-30.0), scale=0.88 + 0.12 * ui_h, rx_deg=3.0, ry_deg=-4.0, opacity=op_h, blur_px=bl_h)
                    pip = make_live_speaker_pip(fg_rgb, clean_bg_rgb, m_arr, 248, 332)
                    paste_3d_layer(cut_im, pip, 895.0 + (1.0 - ui_h) * 55.0, 1615.0, scale=0.88 + 0.12 * ui_h, ry_deg=-8.5, rz_deg=1.5, opacity=op_h, blur_px=bl_h)

                comp_im = optical_soft_transition(comp_im, cut_im, u_cut)

        # CUTAWAY #2 (39.25 - 44.18s): Full-Screen 9:16 Hero Muse Product Showcase (Exact Viên Đặt Hằng Thu Hộp 10 Viên)!
        if 39.00 <= t <= 44.42:
            u_in_c2  = quintic_smooth(clamp01((t - 39.00) / 0.52))
            u_out_c2 = quintic_smooth(clamp01((44.42 - t) / 0.52))
            u_cut2 = min(u_in_c2, u_out_c2)
            if u_cut2 > 0.005:
                in_cutaway = (u_cut2 > 0.5)
                vf_hero = get_clip_frame(clips, "htpm3_viendat_vertical_hero", max(0.0, t - 39.00))
                hero_im = fit_cover_subpixel(vf_hero, W, H, zoom=1.00 + 0.04 * clamp01((t - 39.0) / 5.4)).convert("RGBA")
                vy = np.linspace(0.0, 1.0, 560, dtype=np.float32)[:, None]
                va = np.zeros((560, W, 4), dtype=np.uint8)
                va[:, :, 0], va[:, :, 1], va[:, :, 2] = (8, 24, 18)
                va[:, :, 3] = (vy * vy * 192.0).astype(np.uint8)
                hero_im.alpha_composite(Image.fromarray(va, "RGBA"), dest=(0, H - 560))

                ui_p2, uo_p2, op_p2, bl_p2 = ae_in_out(t, 39.25, 44.18, d_in=0.46, d_out=0.38, overshoot=1.20)
                if op_p2 > 0.01:
                    hdr_p = get_3d_luxury_brand_card(
                        "GIẢI PHÁP CHĂM SÓC CHUYÊN BIỆT",
                        "VIÊN ĐẶT HẰNG THU",
                        "CHĂM SÓC VÙNG KÍN DỊU NHẸ • CÂN BẰNG TỰ NHIÊN",
                        pal2="emerald"
                    )
                    paste_3d_layer(hero_im, hdr_p, 540.0, 225.0 + (1.0 - ui_p2) * (-30.0), scale=0.88 + 0.12 * ui_p2, rx_deg=2.5, ry_deg=3.5, opacity=op_p2, blur_px=bl_p2)
                    b_f1 = get_3d_gradient_pill_badge("Dịu Nhẹ Lành Tính", palette="gold", font_sz=23)
                    b_f2 = get_3d_gradient_pill_badge("Hỗ Trợ Phục Hồi pH", palette="emerald", font_sz=23)
                    paste_3d_layer(hero_im, b_f1, 215.0 - (1.0 - ui_p2) * 45.0, 1285.0, scale=0.90 + 0.10 * ui_p2, ry_deg=9.0, opacity=op_p2, blur_px=bl_p2)
                    paste_3d_layer(hero_im, b_f2, 855.0 + (1.0 - ui_p2) * 45.0, 1285.0, scale=0.90 + 0.10 * ui_p2, ry_deg=-9.0, opacity=op_p2, blur_px=bl_p2)

                    pip2 = make_live_speaker_pip(fg_rgb, clean_bg_rgb, m_arr, 248, 332)
                    paste_3d_layer(hero_im, pip2, 895.0 + (1.0 - ui_p2) * 55.0, 1615.0, scale=0.88 + 0.12 * ui_p2, ry_deg=-8.5, rz_deg=1.5, opacity=op_p2, blur_px=bl_p2)

                comp_im = optical_soft_transition(comp_im, hero_im, u_cut2)

        # ==================================================================
        # 5. 5-STOP GRADIENT HOOK TYPOGRAPHY WITH SPECULAR SHEEN SWEEP (0.06-3.28s)
        # ==================================================================
        if 0.06 <= t <= 3.28:
            _, u_ho, op_ho, bl_ho = ae_in_out(t, 0.06, 3.28, d_in=0.35, d_out=0.34)
            sheen_hk = -0.2 + 1.45 * clamp01((t - 0.35) / 2.2)
            # Line 1: VIÊM PHỤ KHOA (Rose Satin 5-stop gradient!)
            ui1, _, op1, bl1 = ae_in_out(t, 0.06, 3.28, d_in=0.38, d_out=0.34, overshoot=1.22)
            sp_h1 = apply_sheen_sweep(
                render_5stop_grad_sprite("VIÊM PHỤ KHOA", FONT_MONTS_BLK, 62, palette="rose_satin", stroke_col=(255, 255, 255), stroke_w=7, extrude_col=(68, 8, 38), extrude_dy=4, shadow_alpha=105, glow_alpha=65),
                sheen_hk
            )
            paste_3d_layer(
                comp_im, sp_h1, 540.0, 1085.0 + (1.0 - ui1) * 24.0 - (1.0 - u_ho) * 16.0,
                scale=(0.88 + 0.12 * ui1) * (0.94 + 0.06 * u_ho), rx_deg=(1.0 - ui1) * 14.0,
                opacity=op1, blur_px=max(bl1, bl_ho)
            )
            # Line 2: HẾT RỒI... TẠI SAO VẪN QUAY LẠI? (Royal Champagne Gold 5-stop gradient!)
            if t >= 1.28:
                ui2, _, op2, bl2 = ae_in_out(t, 1.28, 3.28, d_in=0.40, d_out=0.34, overshoot=1.22)
                sp_h2 = apply_sheen_sweep(
                    render_5stop_grad_sprite("HẾT RỒI... SAO VẪN QUAY LẠI?", FONT_BE_XBOLD, 44, palette="gold", stroke_col=(16, 20, 32), stroke_w=7, extrude_col=(10, 12, 22), extrude_dy=3, shadow_alpha=105, glow_alpha=60),
                    -0.2 + 1.45 * clamp01((t - 1.40) / 1.65)
                )
                paste_3d_layer(
                    comp_im, sp_h2, 540.0, 1182.0 + (1.0 - ui2) * 24.0 - (1.0 - u_ho) * 16.0,
                    scale=(0.88 + 0.12 * ui2) * (0.94 + 0.06 * u_ho), rx_deg=(1.0 - ui2) * 12.0,
                    opacity=op2, blur_px=max(bl2, bl_ho)
                )

        # ==================================================================
        # 6. FULL-PHRASE 5-STOP GRADIENT SUBTITLES (ENTRANCE + ACTIVE PULSE + EXIT!)
        # ==================================================================
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in  = t - g["t0"]
                dt_out = g["t1"] - t
                u_g_out = quintic_smooth(min(1.0, dt_out / 0.26))
                dy_g_out = -(1.0 - u_g_out) * 14.0
                sc_g_out = 0.94 + 0.06 * u_g_out
                bl_g_out = (1.0 - u_g_out) * 2.6

                if in_cutaway:
                    # On Full-Screen 9:16 Cutaway: place subtitles cleanly on bottom-left clear of the right-side live PIP!
                    min_x, max_x, x_center = 42.0, 748.0, 395.0
                    cap_sz_base = 46.0
                    y_base = 1545.0 if len(g["lines"]) >= 2 else 1575.0
                    lh = 58.0
                else:
                    has_hand_box = (t >= 13.0)
                    min_x = 345.0 if has_hand_box else 48.0
                    max_x = 1042.0
                    x_center = 655.0 if has_hand_box else 540.0
                    cap_sz_base = 50.0 if has_hand_box else 55.0
                    y_base = 1098.0 if len(g["lines"]) >= 2 else 1128.0
                    lh = 62.0

                max_w_ok = max_x - min_x
                gap = 19.0
                sheen_sub = -0.25 + 1.50 * (((t - g["t0"]) % 2.4) / 1.8)

                for li, ln in enumerate(g["lines"]):
                    raw_ln_in = clamp01(max(0.0, dt_in - li * 0.06) / 0.28)
                    u_ln_in = ease_out_back(raw_ln_in, overshoot=1.14)
                    op_ln   = quintic_smooth(min(1.0, raw_ln_in * 1.35)) * u_g_out
                    if op_ln <= 0.01:
                        continue
                    dy_ln = (1.0 - u_ln_in) * 18.0 + dy_g_out
                    bl_ln = (1.0 - quintic_smooth(raw_ln_in)) * 3.0 + bl_g_out
                    sc_ln = (0.92 + 0.08 * u_ln_in) * sc_g_out

                    word_renders = []
                    total_w = 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_active = (ws - 0.05) <= t <= (we + 0.22)
                        act_pulse = 1.06 if is_active else 1.0

                        if wtxt in GOLD_W:
                            pal, f_use, k = "gold", FONT_BE_XBOLD, 1.06
                        elif wtxt in EMERALD_W:
                            pal, f_use, k = "emerald", FONT_BE_XBOLD, 1.05
                        elif wtxt in ROSE_W:
                            pal, f_use, k = "rose_satin", FONT_BE_XBOLD, 1.05
                        else:
                            pal, f_use, k = ("gold" if is_active else "pearl"), FONT_BE_BOLD, 1.0

                        sz_use = cap_sz_base * k
                        sp_tup = render_5stop_grad_sprite(
                            wtxt, f_use, sz_use, palette=pal,
                            stroke_col=(12, 16, 28), stroke_w=5,
                            extrude_col=(8, 12, 20), extrude_dy=2,
                            shadow_alpha=92, glow_alpha=(55 if (pal != "pearl" or is_active) else 20)
                        )
                        sp_im = apply_sheen_sweep(sp_tup, sheen_sub) if pal != "pearl" else sp_tup[0]
                        adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(f_use, sz_use)) + 4.0
                        word_renders.append((sp_im, adv, act_pulse))
                        total_w += adv + (gap if wi > 0 else 0.0)

                    fit_k = min(1.0, max_w_ok / max(1.0, total_w))
                    eff_tot = total_w * fit_k
                    cur_x = max(min_x, min(max_x - eff_tot, x_center - eff_tot * 0.5))
                    cur_y = y_base + li * lh + dy_ln

                    for sp_im, adv, act_pulse in word_renders:
                        eff_adv = adv * fit_k
                        paste_3d_layer(
                            comp_im, sp_im, cur_x + eff_adv * 0.5, cur_y,
                            scale=sc_ln * fit_k * act_pulse, opacity=op_ln, blur_px=bl_ln
                        )
                        cur_x += eff_adv + gap * fit_k
                break

        # 7. Closing 3D Gradient Ribbon (46.20 - 51.35s) + Subtle Disclaimer Bar
        if 46.20 <= t <= 51.35:
            ui_c, uo_c, op_c, bl_c = ae_in_out(t, 46.20, 51.35, d_in=0.44, d_out=0.38, overshoot=1.18)
            paste_3d_layer(
                comp_im, cta_card, 540.0, 1806.0 + (1.0 - ui_c) * 24.0 + (1.0 - uo_c) * 16.0,
                scale=(0.90 + 0.10 * ui_c) * (0.94 + 0.06 * uo_c), rx_deg=(1.0 - ui_c) * 12.0,
                opacity=op_c, blur_px=bl_c
            )

        bar_bot = Image.new("RGBA", (W, 44), (16, 20, 28, 155))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 44))
        paste_3d_layer(comp_im, legal_sp, 540.0, H - 22.0, scale=1.0, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"htpm3_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 250 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/1543 frames ({frame_idx / el:.1f} fps)", flush=True)

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
        gp = os.path.join(CHECK_DIR, "htpm3_ae3d_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved htpm3_ae3d_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM3 AE-3D video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
