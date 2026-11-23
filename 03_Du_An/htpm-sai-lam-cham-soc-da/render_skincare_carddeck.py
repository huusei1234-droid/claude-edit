import json, math, os, re, subprocess, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter1d
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

FONTS_DIR      = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_MONTS_BLK = os.path.join(FONTS_DIR, "Montserrat-Black.ttf")
FONT_BE_XBOLD  = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_BE_BOLD   = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")
FONT_BE_MED    = os.path.join(FONTS_DIR, "BeVietnamPro-Medium.ttf")

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
        (0.68, (220, 238, 232)),
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
    """C2-continuous velocity & acceleration: zero jerk at both ends!"""
    u = clamp01(u)
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

def septic_smooth(u):
    """C3-continuous ultra-silky curve (-20u^7 + 70u^6 - 84u^5 + 35u^4): zero snap even in jolt!"""
    u = clamp01(u)
    u4 = u * u * u * u
    return u4 * (35.0 + u * (-84.0 + u * (70.0 - 20.0 * u)))

def ease_out_back_soft(u, overshoot=1.10):
    u = clamp01(u) - 1.0
    return 1.0 + u * u * ((overshoot + 1.0) * u + overshoot)

def ae_in_out(t, st, en, d_in=0.52, d_out=0.46, overshoot=1.08):
    if t <= st or t >= en:
        return 0.0, 0.0, 0.0, 0.0
    raw_in  = clamp01((t - st) / max(0.06, d_in))
    raw_out = clamp01((en - t) / max(0.06, d_out))
    u_in    = ease_out_back_soft(raw_in, overshoot=overshoot)
    u_out   = septic_smooth(raw_out)
    op      = min(quintic_smooth(min(1.0, raw_in * 1.25)), u_out)
    sigma   = (1.0 - quintic_smooth(raw_in)) * 3.8 + (1.0 - u_out) * 3.4
    return u_in, u_out, op, sigma

# ======================================================================
# 1. CONTINUOUS 3D PERSPECTIVE + DIRECTIONAL SHUTTER MOTION BLUR ENGINE
#    (ZERO discrete threshold pops — 100% continuous floating-point!)
# ======================================================================
def _solve_homography_8(src_pts, dst_pts):
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

def paste_3d_smooth(canvas_im, sprite_im, cx, cy, scale=1.0, rx_deg=0.0, ry_deg=0.0, rz_deg=0.0, opacity=1.0, dof_sigma=0.0, mb_dx=0.0, dim=1.0, focal=1420.0):
    """
    Always uses continuous 3D PERSPECTIVE homography (zero AFFINE/PERSPECTIVE mode-switch jump!),
    continuous SciPy Gaussian DOF, and 180-degree shutter horizontal motion blur!
    """
    if opacity <= 0.005 or scale <= 0.02:
        return

    sw, sh = sprite_im.size
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
    proj_x = cx + (rot[:, 0] * focal) / np.maximum(220.0, focal + rot[:, 2])
    proj_y = cy + (rot[:, 1] * focal) / np.maximum(220.0, focal + rot[:, 2])

    pad_m = int(math.ceil(abs(mb_dx) * 0.6 + dof_sigma * 2.5 + 6))
    x0 = int(math.floor(proj_x.min())) - pad_m
    y0 = int(math.floor(proj_y.min())) - pad_m
    x1 = int(math.ceil(proj_x.max())) + pad_m
    y1 = int(math.ceil(proj_y.max())) + pad_m
    out_w, out_h = max(8, x1 - x0), max(8, y1 - y0)

    dst_pts = [(float(proj_x[i] - x0), float(proj_y[i] - y0)) for i in range(4)]
    src_pts = [(0.0, 0.0), (float(sw), 0.0), (float(sw), float(sh)), (0.0, float(sh))]
    coeffs = _solve_homography_8(src_pts, dst_pts)
    warped = sprite_im.transform((out_w, out_h), Image.Transform.PERSPECTIVE, coeffs, resample=Image.Resampling.BICUBIC)

    arr = np.array(warped, dtype=np.float32)
    # Premultiply alpha before continuous blur so edges never halo dark!
    a_norm = arr[:, :, 3:4] / 255.0
    arr[:, :, 0:3] *= a_norm * float(dim)

    # 180-degree shutter horizontal motion blur during card pushes!
    k_mb = int(round(abs(mb_dx) * 0.55))
    if k_mb >= 2:
        arr = uniform_filter1d(arr, size=min(28, k_mb), axis=1, mode="constant", cval=0.0)

    # Continuous floating-point optical DOF / transition blur (down to 0.12px, zero snap!)
    if dof_sigma >= 0.12:
        arr = gaussian_filter(arr, sigma=(min(8.0, dof_sigma), min(8.0, dof_sigma), 0.0), mode="constant", cval=0.0)

    # Un-premultiply cleanly & apply opacity
    a_out = np.clip(arr[:, :, 3:4] * clamp01(opacity), 0.0, 255.0)
    rgb_out = np.where(arr[:, :, 3:4] > 1.0, arr[:, :, 0:3] / np.maximum(1e-3, arr[:, :, 3:4] / 255.0), 0.0)
    final_rgba = np.concatenate([np.clip(rgb_out, 0, 255), a_out], axis=2).astype(np.uint8)
    warped_im = Image.fromarray(final_rgba, "RGBA")

    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(canvas_im.width, x0 + out_w), min(canvas_im.height, y0 + out_h)
    if dx1 > dx0 and dy1 > dy0:
        canvas_im.alpha_composite(warped_im.crop((dx0 - x0, dy0 - y0, dx1 - x0, dy1 - y0)), dest=(dx0, dy0))

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
# 2. 5-STOP GRADIENT TYPOGRAPHY + DARK OUTER STROKE FOR WHITE BLAZER!
# ======================================================================
_grad_sprite_cache = {}
def render_5stop_grad_sprite(text, font_path, size, palette="gold", stroke_col=(14, 18, 30), stroke_w=6, extrude_col=(8, 10, 20), extrude_dy=3, shadow_alpha=105, glow_alpha=45):
    key = (text, font_path, int(round(size)), palette, stroke_col, stroke_w, extrude_col, extrude_dy, shadow_alpha, glow_alpha)
    if key in _grad_sprite_cache:
        return _grad_sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw, th = max(4, bbox[2] - bbox[0]), max(4, bbox[3] - bbox[1])
    pad = int(stroke_w + 26)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    stops = GRAD_PALETTES.get(palette, GRAD_PALETTES["gold"])
    mid_col = stops[len(stops) // 2][1]

    if glow_alpha > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(1, stroke_w // 2), stroke_fill=255)
        gb = np.array(gm.filter(ImageFilter.GaussianBlur(radius=8.5)), dtype=np.float32) / 255.0
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0], ga[:, :, 1], ga[:, :, 2] = mid_col
        ga[:, :, 3] = np.clip(gb * glow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 6), text, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=6.5)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (10, 14, 26)
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    if extrude_dy > 0 and extrude_col is not None:
        ex = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(ex).text((ox + 1, oy + extrude_dy), text, font=font, fill=(*extrude_col, 248), stroke_width=stroke_w, stroke_fill=(*extrude_col, 248))
        base = Image.alpha_composite(base, ex)

    if stroke_w > 0 and stroke_col is not None:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        base = Image.alpha_composite(base, st_im)

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

    if len(_grad_sprite_cache) > 950:
        _grad_sprite_cache.clear()
    _grad_sprite_cache[key] = (base, arr_m)
    return base, arr_m

def apply_sheen_sweep(sprite_tuple, sheen_phase):
    base, arr_m = sprite_tuple
    if sheen_phase < -0.25 or sheen_phase > 1.25:
        return base
    ch, cw = arr_m.shape
    yy, xx = np.ogrid[0:ch, 0:cw]
    diag = (xx.astype(np.float32) * 0.90 + yy.astype(np.float32) * 0.42) / max(1.0, cw * 0.90 + ch * 0.42)
    band = np.exp(-((diag - sheen_phase) ** 2) / 0.0055) * 190.0 * arr_m
    if band.max() < 3.0:
        return base
    out = np.array(base, dtype=np.float32)
    out[:, :, 0] = np.clip(out[:, :, 0] + band, 0, 255)
    out[:, :, 1] = np.clip(out[:, :, 1] + band * 0.98, 0, 255)
    out[:, :, 2] = np.clip(out[:, :, 2] + band * 0.94, 0, 255)
    return Image.fromarray(out.astype(np.uint8), "RGBA")

# ======================================================================
# 3. LUXURY PLAYING-CARD BUILDER & 3D CARD-FAN / PUSH-CAROUSEL ENGINE!
#    ("xuất hiện 1 lúc rồi xếp như lá bài, rồi đẩy qua lại theo thứ tự")
# ======================================================================
_card_frame_shell_cache = {}
def get_playing_card_shell(w, h, idx_str, title_str, palette="gold", rim_rgb=(252, 225, 129)):
    """Pre-builds the rounded playing-card shadow, border, top-left index badge ('01') & header bar!"""
    k = (w, h, idx_str, title_str, palette, rim_rgb)
    if k in _card_frame_shell_cache:
        return _card_frame_shell_cache[k]
    pad = 24
    cw, ch = w + pad * 2, h + pad * 2
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius=34, fill=(8, 12, 24, 128))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=14))

    rmask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=255)

    # Top dark-glass header strip + index pill + title
    overlay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    hdr = Image.new("RGBA", (w, 86), (0, 0, 0, 0))
    vy = np.linspace(1.0, 0.0, 86, dtype=np.float32)[:, None]
    ha = np.zeros((86, w, 4), dtype=np.uint8)
    ha[:, :, 0], ha[:, :, 1], ha[:, :, 2] = (12, 16, 28)
    ha[:, :, 3] = (vy * 212.0).astype(np.uint8)
    hdr = Image.fromarray(ha, "RGBA")
    overlay.paste(hdr, (pad, pad), mask=rmask.crop((0, 0, w, 86)))

    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius=34, outline=(*rim_rgb, 242), width=3)
    d.rounded_rectangle([pad + 5, pad + 5, pad + w - 6, pad + h - 6], radius=29, outline=(255, 255, 255, 110), width=1)

    # Playing-card corner index badge (e.g. "01")
    d.rounded_rectangle([pad + 16, pad + 14, pad + 78, pad + 56], radius=16, fill=(20, 26, 42, 235), outline=(*rim_rgb, 220), width=2)
    sp_idx, _ = render_5stop_grad_sprite(idx_str, FONT_MONTS_BLK, 24, palette=palette, stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
    sp_ic = sp_idx.crop(sp_idx.getbbox())
    overlay.alpha_composite(sp_ic, dest=(pad + 47 - sp_ic.width // 2, pad + 35 - sp_ic.height // 2))

    sp_t, _ = render_5stop_grad_sprite(title_str, FONT_BE_XBOLD, 22, palette="pearl", stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=60, glow_alpha=0)
    sp_tc = sp_t.crop(sp_t.getbbox())
    max_tw = w - 108
    if sp_tc.width > max_tw:
        nh = max(12, int(round(sp_tc.height * (max_tw / float(sp_tc.width)))))
        sp_tc = sp_tc.resize((max_tw, nh), Image.Resampling.LANCZOS)
    overlay.alpha_composite(sp_tc, dest=(pad + 90, pad + 35 - sp_tc.height // 2))

    _card_frame_shell_cache[k] = (sh, rmask, overlay, pad)
    return _card_frame_shell_cache[k]

def build_live_playing_card(vf_rgb, w, h, idx_str, title_str, palette="gold", rim_rgb=(252, 225, 129), zoom=1.02):
    sh, rmask, overlay, pad = get_playing_card_shell(w, h, idx_str, title_str, palette, rim_rgb)
    cw, ch = sh.size
    card = sh.copy()
    crop = fit_cover_subpixel(vf_rgb, w, h, zoom=zoom)
    vlay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vlay.paste(crop, (pad, pad), mask=rmask)
    card = Image.alpha_composite(card, vlay)
    card = Image.alpha_composite(card, overlay)
    return card

_text_card_cache = {}
def build_graphic_overview_card(w, h, idx_str, title_big, sub_txt, palette="gold", rim_rgb=(252, 225, 129)):
    """Sleek 3D dark-sapphire playing card for the 3-Mistake Overview Fan (3.0-5.8s)!"""
    k = (w, h, idx_str, title_big, sub_txt, palette)
    if k in _text_card_cache:
        return _text_card_cache[k]
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    lift = np.exp(-(xx * xx * 1.1 + (yy - 0.35) ** 2 * 1.6))
    bg = np.zeros((h, w, 3), dtype=np.uint8)
    bg[:, :, 0] = np.clip(18 + 26 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 1] = np.clip(26 + 34 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 2] = np.clip(44 + 48 * lift, 0, 255).astype(np.uint8)
    card = build_live_playing_card(bg, w, h, idx_str, "SAI LẦM", palette=palette, rim_rgb=rim_rgb, zoom=1.0)
    cw, ch = card.size
    sp_num, _ = render_5stop_grad_sprite(idx_str, FONT_MONTS_BLK, 78, palette=palette, stroke_col=(10, 14, 24), stroke_w=6, extrude_dy=4, shadow_alpha=90, glow_alpha=55)
    paste_3d_smooth(card, sp_num, cw * 0.5, ch * 0.43, scale=1.0)
    for li, ln in enumerate(title_big.split("\n")):
        sp_l, _ = render_5stop_grad_sprite(ln, FONT_BE_XBOLD, 25, palette="pearl", stroke_col=(10, 14, 24), stroke_w=5, extrude_dy=2, shadow_alpha=75, glow_alpha=0)
        paste_3d_smooth(card, sp_l, cw * 0.5, ch * 0.69 + li * 35, scale=1.0)
    _text_card_cache[k] = card
    return card

def eval_deck_focus(t, focus_schedule, push_dur=0.62):
    """
    Computes continuous floating-point focus index f(t) and instantaneous push velocity df/dt!
    focus_schedule: list of (t_switch, target_index_or_'fan')
      - If target is None ('fan'): returns None (pure symmetric playing-card fan showcase!)
    """
    if not focus_schedule or focus_schedule[0][1] is None and (len(focus_schedule) == 1 or t < focus_schedule[1][0]):
        return None, 0.0
    # Find latest active focus transitions
    cur_val = float(focus_schedule[0][1] or 0.0)
    vel = 0.0
    for idx in range(1, len(focus_schedule)):
        ts, targ = focus_schedule[idx]
        prev_targ = focus_schedule[idx - 1][1]
        if prev_targ is None:
            if t >= ts:
                cur_val = float(targ)
            continue
        if t >= ts:
            u = clamp01((t - ts) / push_dur)
            sm = septic_smooth(u)
            # Derivative of septic_smooth for real velocity motion blur!
            if 0.001 < u < 0.999:
                du = 140.0 * (u ** 3) * ((1.0 - u) ** 3) / push_dur
                vel = (float(targ) - float(prev_targ)) * du
            cur_val = float(prev_targ) + (float(targ) - float(prev_targ)) * sm
    return cur_val, vel

def render_3d_playing_card_deck(canvas_im, card_sprites, t, st, en, focus_schedule, fan_hold_until=None, refan_window=None, cy_base=425.0):
    """
    Signature After Effects 3D Playing-Card Fan & Sequential Push-Carousel!
    1. Enters smoothly from depth & fans out symmetrically like playing cards ("xuất hiện 1 lúc rồi xếp như lá bài").
    2. Smoothly pushes/shuffles left & right along curved 3D depth arcs in exact script order ("đẩy qua lại theo thứ tự").
    3. Can smoothly re-fan to show the full hand (`refan_window`) and push again!
    4. Gathers & glides out smoothly at `en` ("chuyển động in out mượt mà").
    """
    if t <= st or t >= en:
        return
    K = len(card_sprites)
    d_in, d_out = 0.64, 0.54
    raw_in  = clamp01((t - st) / d_in)
    raw_out = clamp01((en - t) / d_out)
    u_in    = ease_out_back_soft(raw_in, overshoot=1.09)
    u_out   = septic_smooth(raw_out)
    op_deck = min(quintic_smooth(min(1.0, raw_in * 1.30)), u_out)
    if op_deck <= 0.008:
        return

    # Blend between initial Symmetric Playing-Card Fan (w_car=0) and Active Push-Carousel (w_car=1)!
    if fan_hold_until is None:
        w_car = 0.0
    else:
        w_car = septic_smooth(clamp01((t - fan_hold_until) / 0.64))
        if refan_window is not None:
            rf0, rf1 = refan_window
            u_rf_in  = septic_smooth(clamp01((t - rf0) / 0.62))
            u_rf_out = septic_smooth(clamp01((t - rf1) / 0.62))
            w_car *= (1.0 - (u_rf_in - u_rf_out))

    foc_idx, foc_vel = eval_deck_focus(t, focus_schedule, push_dur=0.64)
    if foc_idx is None:
        foc_idx = (K - 1) * 0.5

    draw_queue = []
    mid_k = (K - 1) * 0.5
    is_pure_fan = (fan_hold_until is None)
    spread_fan = 288.0 if is_pure_fan else (262.0 if K == 3 else 198.0)
    fan_base_sc = 0.85 if is_pure_fan else (0.62 if K == 3 else 0.55)

    for i in range(K):
        # A. Pure Symmetric Playing-Card Fan Pose (like holding a fanned hand of playing cards!)
        s_fan = i - mid_k
        fx = 540.0 + s_fan * spread_fan * u_in
        fy = cy_base + (4.0 if is_pure_fan else 12.0) + abs(s_fan) * (28.0 if is_pure_fan else 32.0) + (1.0 - u_in) * 95.0
        f_sc = fan_base_sc * (0.82 + 0.18 * u_in)
        f_ry = -s_fan * (13.0 if K == 3 else 10.5) * u_in
        f_rz = s_fan * (8.2 if K == 3 else 6.2) * u_in
        f_rx = (1.0 - u_in) * 14.0
        f_dim = 0.98
        f_dof = 0.0
        f_z   = (10.0 - abs(s_fan) * 6.0) if not is_pure_fan else (i * 2.0)

        # B. Active Sequential Push-Carousel Pose (focused card Front-Center, others fanned left & right!)
        rel = float(i) - foc_idx
        abs_r = abs(rel)
        # 3D orbital swing arc during swap so cards physically pass around each other in Z-space!
        swap_arc = math.sin(clamp01(abs_r) * math.pi) if abs_r < 1.0 else 0.0
        cx_car = 540.0 + rel * (228.0 if K == 3 else 182.0) + (-36.0 if rel < 0 else 36.0) * swap_arc * 0.45
        cy_car = cy_base - 8.0 + min(2.2, abs_r) * 34.0 - swap_arc * 16.0
        sc_car = 0.97 - min(1.0, abs_r) * 0.22 - max(0.0, abs_r - 1.0) * 0.05
        ry_car = -max(-22.0, min(22.0, rel * 16.5))
        rz_car = max(-10.5, min(10.5, rel * 6.8))
        rx_car = -1.5 * (1.0 - min(1.0, abs_r))
        dim_car = 1.00 - min(1.0, abs_r) * 0.24
        dof_car = min(1.0, abs_r) * 1.75
        z_car   = 100.0 * math.cos(min(1.5, abs_r)) - abs_r * 25.0

        # Interpolate seamlessly between Fan Showcase & Push-Carousel, plus smooth Exit Collapse!
        px = (fx * (1.0 - w_car) + cx_car * w_car) * u_out + 540.0 * (1.0 - u_out)
        py = (fy * (1.0 - w_car) + cy_car * w_car) - (1.0 - u_out) * 48.0 + math.sin(t * 1.7 + i) * 3.0
        psc = (f_sc * (1.0 - w_car) + sc_car * w_car) * (0.88 + 0.12 * u_out)
        pry = (f_ry * (1.0 - w_car) + ry_car * w_car) * u_out
        prz = (f_rz * (1.0 - w_car) + rz_car * w_car) * u_out
        prx = (f_rx * (1.0 - w_car) + rx_car * w_car) + (1.0 - u_out) * 10.0
        pdim = f_dim * (1.0 - w_car) + dim_car * w_car
        pdof = f_dof * (1.0 - w_car) + dof_car * w_car + (1.0 - quintic_smooth(raw_in)) * 3.2 + (1.0 - u_out) * 3.2
        pz   = f_z * (1.0 - w_car) + z_car * w_car
        mb_x = -foc_vel * 220.0 * w_car / FPS

        draw_queue.append((pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x))

    # Paint back-to-front by continuous Z-depth so front card ALWAYS cleanly overlaps side cards!
    draw_queue.sort(key=lambda x: x[0])
    for pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x in draw_queue:
        paste_3d_smooth(
            canvas_im, card_sprites[i], px, py,
            scale=psc, rx_deg=prx, ry_deg=pry, rz_deg=prz,
            opacity=op_deck, dof_sigma=pdof, mb_dx=mb_x, dim=pdim
        )

# ======================================================================
# 4. KINETIC EMPHASIS BANNERS, PILLS & OPTICAL CUTAWAY TRANSITION
# ======================================================================
_badge_cache = {}
def get_3d_pill(label_txt, palette="gold", font_sz=25, dot_rgb=(252, 225, 129)):
    k = (label_txt, palette, font_sz, dot_rgb)
    if k in _badge_cache:
        return _badge_cache[k]
    sp, _ = render_5stop_grad_sprite(label_txt, FONT_BE_XBOLD, font_sz, palette=palette, stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=2, shadow_alpha=45, glow_alpha=30)
    sp_c = sp.crop(sp.getbbox())
    pw = min(1010, sp_c.width + 76)
    ph = max(56, sp_c.height + 22)
    pad = 18
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 6, pad + pw, pad + ph + 6], radius=ph // 2, fill=(8, 12, 24, 108))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=8)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=ph // 2, fill=(18, 22, 36, 224), outline=(255, 246, 224, 232), width=2)
    cy = pad + ph // 2
    d.ellipse([pad + 20, cy - 6, pad + 32, cy + 6], fill=(*dot_rgb, 255))
    im.alpha_composite(sp_c, dest=(int(pad + pw * 0.5 + 10 - sp_c.width * 0.5), int(cy - sp_c.height * 0.5)))
    _badge_cache[k] = im
    return im

_emph_card_cache = {}
def get_emphasis_banner_card(kicker, headline, subline, pal_h="gold"):
    k = (kicker, headline, subline, pal_h)
    if k in _emph_card_cache:
        return _emph_card_cache[k]
    pw, ph = 944, 248
    pad = 26
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + pw, pad + ph + 10], radius=42, fill=(10, 14, 26, 115))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, pw, dtype=np.float32)[None, :]
    lift = np.exp(-(xx * xx * 1.2 + (yy - 0.35) ** 2 * 1.8))
    bg = np.zeros((ph, pw, 3), dtype=np.uint8)
    bg[:, :, 0] = np.clip(18 + 24 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 1] = np.clip(24 + 30 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 2] = np.clip(40 + 42 * lift, 0, 255).astype(np.uint8)
    rm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=42, fill=255)
    bl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bl.paste(Image.fromarray(bg, "RGB"), (pad, pad), mask=rm)
    card = Image.alpha_composite(card, bl)
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=42, outline=(252, 225, 129, 236), width=3)

    sz_h = 50 if len(headline) <= 19 else (42 if len(headline) <= 24 else 35)
    s1, _ = render_5stop_grad_sprite(kicker, FONT_BE_XBOLD, 24, palette="coral" if "SAI LẦM" in kicker else "emerald", stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=50, glow_alpha=25)
    s2, _ = render_5stop_grad_sprite(headline, FONT_MONTS_BLK, sz_h, palette=pal_h, stroke_col=(10, 14, 24), stroke_w=6, extrude_dy=3, shadow_alpha=90, glow_alpha=55)
    s3, _ = render_5stop_grad_sprite(subline, FONT_BE_BOLD, 24, palette="pearl", stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=45, glow_alpha=0)
    paste_3d_smooth(card, s1, cw * 0.5, pad + 44)
    paste_3d_smooth(card, s2, cw * 0.5, pad + 120)
    ImageDraw.Draw(card).line([(cw // 2 - 240, pad + 172), (cw // 2 + 240, pad + 172)], fill=(252, 225, 129, 145), width=2)
    paste_3d_smooth(card, s3, cw * 0.5, pad + 206)
    _emph_card_cache[k] = card
    return card

def optical_soft_transition(base_rgba_im, cutaway_rgba_im, u_cut):
    if u_cut <= 0.004:
        return base_rgba_im
    if u_cut >= 0.996:
        return cutaway_rgba_im
    bell = math.sin(u_cut * math.pi)
    rad = bell * 8.5
    b_im = base_rgba_im.filter(ImageFilter.GaussianBlur(radius=rad * u_cut)) if rad * u_cut >= 0.4 else base_rgba_im
    c_im = cutaway_rgba_im.filter(ImageFilter.GaussianBlur(radius=rad * (1.0 - u_cut))) if rad * (1.0 - u_cut) >= 0.4 else cutaway_rgba_im
    mix = np.array(b_im, dtype=np.float32) * (1.0 - u_cut) + np.array(c_im, dtype=np.float32) * u_cut
    bloom = bell * 14.0
    mix[:, :, 0:3] = np.clip(mix[:, :, 0:3] + bloom, 0, 255)
    mix[:, :, 3] = 255.0
    return Image.fromarray(mix.astype(np.uint8), "RGBA")

# ======================================================================
# 5. CAMERA ZOOM & READABLE SEMANTIC PHRASE SUBTITLES
# ======================================================================
ZOOM_KEYS = [
    (0.00, 1.045),
    (2.90, 1.020),
    (5.86, 1.062),   # Emphasis #1 close-up
    (8.10, 1.022),
    (30.12, 1.062),  # Emphasis #2 close-up
    (33.10, 1.022),
    (49.08, 1.062),  # Emphasis #3 close-up
    (53.50, 1.022),
    (67.88, 1.060),  # Core takeaway close-up
    (74.50, 1.028),
    (80.75, 1.012),
]

def get_butter_zoom(t):
    if t <= ZOOM_KEYS[0][0]:
        return ZOOM_KEYS[0][1]
    for i in range(1, len(ZOOM_KEYS)):
        t0, z0 = ZOOM_KEYS[i - 1]
        t1, z1 = ZOOM_KEYS[i]
        if t <= t1:
            u = septic_smooth(min(1.0, (t - t0) / min(0.95, max(0.40, (t1 - t0) * 0.45))))
            return z0 + (z1 - z0) * u
    return ZOOM_KEYS[-1][1]

def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.96) * 1.015, 0.0, 1.0)
    return (
        np.clip(y * 255.0 * 1.012, 0, 255).astype(np.uint8),
        np.clip(y * 255.0 * 1.005, 0, 255).astype(np.uint8),
        np.clip(y * 255.0 * 0.996, 0, 255).astype(np.uint8),
    )
BRIGHT_LUT = _build_bright_lut()

def polish_bright_frame(rgb):
    out = np.empty_like(rgb)
    out[:, :, 0] = BRIGHT_LUT[0][rgb[:, :, 0]]
    out[:, :, 1] = BRIGHT_LUT[1][rgb[:, :, 1]]
    out[:, :, 2] = BRIGHT_LUT[2][rgb[:, :, 2]]
    return out

def load_captions_skincare():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and (w["start"] + w["end"]) * 0.5 >= 1.80
    ]

    phrases, cur_p = [], []
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
        if (
            merged
            and len(p) <= 2
            and not re.search(r"[.?!…]$", merged[-1][-1][0])
            and (p[0][1] - merged[-1][-1][2]) < 0.45
            and len(merged[-1]) + len(p) <= 9
        ):
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

    GOLD_W    = {"3", "Hằng,", "Hằng", "màng", "trăm", "triệu", "1–2", "nền", "tảng", "hiệu", "quả"}
    CORAL_W   = {"sai", "lầm", "quá", "mức.", "mạnh,", "tổn", "thương.", "bóng", "nhờn", "xu", "hướng.", "kích", "ứng", "thức", "ngọt"}
    EMERALD_W = {"bảo", "vệ", "độ", "ẩm", "dầu,", "khô,", "hỗn", "hợp", "nhạy", "cảm", "thói", "quen", "phù", "hợp"}

    cap_groups = []
    for i, p in enumerate(merged):
        t0 = max(1.80, p[0][1] - 0.05)
        last_end = p[-1][2]
        nxt_s = merged[i + 1][0][1] if i + 1 < len(merged) else 80.60
        min_hold = max(last_end + 0.42, t0 + 1.55)
        t1 = min(nxt_s - 0.04, max(min_hold, last_end + 0.65))
        if t1 <= last_end + 0.12:
            t1 = min(nxt_s - 0.02, last_end + 0.25)
        cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced(p)})
    return cap_groups, GOLD_W, CORAL_W, EMERALD_W

class VideoReader:
    def __init__(self, path):
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    def read(self):
        buf = self.proc.stdout.read(W * H * 3)
        return None if len(buf) < W * H * 3 else np.frombuffer(buf, dtype=np.uint8).reshape((H, W, 3))
    def close(self):
        self.proc.stdout.close(); self.proc.wait()

def load_vid_frames_wh(path, vw, vh):
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={vw}:{vh}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    frames, nb = [], vw * vh * 3
    while True:
        b = proc.stdout.read(nb)
        if len(b) < nb:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)))
    proc.stdout.close(); proc.wait()
    return frames

def get_clip_frame_smooth(clips, key, t_rel, target_span=6.0):
    """Smooth continuous frame-interpolated playback (stretches smoothly across target_span with ZERO sudden reversal!)"""
    arr_list = clips.get(key)
    if not arr_list:
        return np.full((640, 960, 3), 235, dtype=np.uint8)
    n = len(arr_list)
    if n == 1:
        return arr_list[0]
    u = clamp01(t_rel / max(0.5, target_span))
    pos = u * (n - 1)
    i0 = int(math.floor(pos))
    i1 = min(n - 1, i0 + 1)
    frac = pos - i0
    if frac < 0.02:
        return arr_list[i0]
    return np.clip(arr_list[i0].astype(np.float32) * (1.0 - frac) + arr_list[i1].astype(np.float32) * frac, 0, 255).astype(np.uint8)

def make_live_speaker_pip(fg_rgb, pw=248, ph=330):
    sub = fg_rgb[540:1420, 210:870]
    im = fit_cover_subpixel(sub, pw, ph, zoom=1.02)
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
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=34, outline=(252, 225, 129, 240), width=3)
    return card

# ======================================================================
# 6. MAIN RENDER LOOP (2,422 FRAMES = 80.73s)
# ======================================================================
def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [1.10, 4.40, 8.85, 18.60, 40.35, 45.20, 54.15, 64.90, 73.50]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vid_keys = [
        ("c1_overwash_foam",    960, 640),
        ("c2_barrier_damaged",  960, 640),
        ("c3_oily_dehydrated",  960, 640),
        ("c4_viral_trend_buy",  960, 640),
        ("c5_cosmetic_vanity",  960, 640),
        ("c6_late_night_2am",   960, 640),
        ("c7_junkfood_lowwater",960, 640),
        ("c8_healthy_routine",  1080, 1920),
    ]
    clips = {}
    for ck, vw, vh in vid_keys:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if os.path.exists(vp):
            clips[ck] = load_vid_frames_wh(vp, vw, vh)
            print(f"Loaded {ck}: {len(clips[ck])} frames")
        else:
            print(f"WARNING missing {vp}")

    st_imgs = {}
    for sfn in ["st_01_oily", "st_02_dry", "st_03_combo", "st_04_sensitive"]:
        sp = os.path.join(MEDIA_DIR, f"{sfn}.jpg")
        st_imgs[sfn] = np.array(Image.open(sp).convert("RGB")) if os.path.exists(sp) else np.full((640, 960, 3), 210, dtype=np.uint8)

    # Pre-build the 3 Overview Playing Cards (2.95 - 5.82s) — sleek 332x476 so all 3 fanned cards are 100% readable!
    ov_cards = [
        build_graphic_overview_card(332, 476, "01", "LÀM SẠCH\nQUÁ MỨC", "", palette="coral", rim_rgb=(255, 175, 128)),
        build_graphic_overview_card(332, 476, "02", "CHẠY THEO\nXU HƯỚNG", "", palette="rose_satin", rim_rgb=(255, 178, 218)),
        build_graphic_overview_card(332, 476, "03", "QUÊN CHĂM\nBÊN TRONG", "", palette="gold", rim_rgb=(252, 225, 129)),
    ]

    cap_groups, GOLD_W, CORAL_W, EMERALD_W = load_captions_skincare()
    legal_sp, _ = render_5stop_grad_sprite(
        "Chia sẻ kiến thức chăm sóc da khoa học cùng Hằng Thu • Lắng nghe & thấu hiểu làn da của bạn",
        FONT_BE_MED, 18, palette="pearl", stroke_col=(14, 18, 28), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0
    )
    cta_ribbon = get_3d_pill("Chăm Sóc Da Đúng Nền Tảng  •  Khỏe Bên Trong & Đẹp Bên Ngoài", palette="gold", font_sz=23, dot_rgb=(92, 224, 181))

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)

    raw_vid_out = os.path.join(PROJ_DIR, "_skincare_carddeck_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    yy_g = np.arange(H, dtype=np.float32)[:, None]
    desk_mask = np.clip((yy_g - 1370.0) / 55.0, 0.0, 1.0)

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

        z = get_butter_zoom(t)
        fg_im = fit_cover_subpixel(rgb, W, H, zoom=z, pan_y=-0.03 * (z - 1.0))
        m_rgb = np.repeat((matte * 255.0).astype(np.uint8)[:, :, None], 3, axis=2)
        m_im  = fit_cover_subpixel(m_rgb, W, H, zoom=z, pan_y=-0.03 * (z - 1.0)).convert("L")
        fg_rgb = np.array(fg_im)
        m_arr  = np.array(m_im, dtype=np.float32) / 255.0

        base_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

        # ==================================================================
        # 1. BEHIND-SPEAKER 3D PLAYING-CARD DECKS & EMPHASIS CALLOUTS!
        # ==================================================================
        # A. 3-Card Overview Playing-Card Fan ("có 3 sai lầm phổ biến", 2.95 - 5.82s)
        if 2.95 <= t < 5.82:
            render_3d_playing_card_deck(
                base_im, ov_cards, t, 2.95, 5.82,
                focus_schedule=[(2.95, None)], fan_hold_until=None, cy_base=435.0
            )

        # B. Direct Source + Emphasis Banner #1 ("Đầu tiên, đó là làm sạch quá mức", 5.86 - 8.12s)
        if 5.84 <= t < 8.16:
            ui, uo, op, sig = ae_in_out(t, 5.86, 8.12, d_in=0.44, d_out=0.38, overshoot=1.12)
            ec1 = get_emphasis_banner_card("SAI LẦM PHỔ BIẾN #1", "LÀM SẠCH QUÁ MỨC", "RỬA MẶT NHIỀU LẦN & TẨY RỬA MẠNH", pal_h="coral")
            paste_3d_smooth(base_im, ec1, 540.0, 395.0 + (1.0 - ui) * (-34.0) - (1.0 - uo) * 20.0, scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), rx_deg=(1.0 - ui) * 10.0, opacity=op, dof_sigma=sig)

        # C. DECK #1 (8.08 - 30.08s): 3 Photorealistic Cards Fan Out Together -> Push 01 -> Push 02 -> Push 03!
        if 8.08 <= t < 30.08:
            f1 = get_clip_frame_smooth(clips, "c1_overwash_foam",   max(0.0, t - 8.08),  target_span=7.0)
            f2 = get_clip_frame_smooth(clips, "c2_barrier_damaged", max(0.0, t - 14.10), target_span=7.0)
            f3 = get_clip_frame_smooth(clips, "c3_oily_dehydrated", max(0.0, t - 20.40), target_span=9.8)
            deck1 = [
                build_live_playing_card(f1, 740, 520, "01", "RỬA MẶT QUÁ NHIỀU LẦN", "sapphire", (136, 215, 255)),
                build_live_playing_card(f2, 740, 520, "02", "TỔN THƯƠNG MÀNG BẢO VỆ DA", "coral", (255, 165, 122)),
                build_live_playing_card(f3, 740, 520, "03", "MẤT NƯỚC • BÓNG NHỜN BÙ TRỪ", "gold", (252, 225, 129)),
            ]
            render_3d_playing_card_deck(
                base_im, deck1, t, 8.08, 30.08,
                focus_schedule=[(8.08, 0), (14.35, 1), (20.62, 2)],
                fan_hold_until=9.15, cy_base=425.0
            )

        # D. Direct Source + Emphasis Banner #2 ("Sai lầm thứ 2 đó chính là chạy theo xu hướng", 30.10 - 33.08s)
        if 30.10 <= t < 33.12:
            ui, uo, op, sig = ae_in_out(t, 30.12, 33.08, d_in=0.44, d_out=0.38, overshoot=1.12)
            ec2 = get_emphasis_banner_card("SAI LẦM PHỔ BIẾN #2", "CHẠY THEO XU HƯỚNG", "MUA THEO LỜI KHEN • CHƯA HIỂU RÕ LOẠI DA", pal_h="rose_satin")
            paste_3d_smooth(base_im, ec2, 540.0, 395.0 + (1.0 - ui) * (-34.0) - (1.0 - uo) * 20.0, scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), rx_deg=(1.0 - ui) * 10.0, opacity=op, dof_sigma=sig)

        # E. Editorial Single 3D Documentary Card ("thấy sản phẩm nhiều người khen mua về dùng", 33.06 - 39.20s)
        if 33.06 <= t < 39.20:
            ui, uo, op, sig = ae_in_out(t, 33.08, 39.18, d_in=0.52, d_out=0.42, overshoot=1.09)
            f4 = get_clip_frame_smooth(clips, "c4_viral_trend_buy", t - 33.08, target_span=6.1)
            c_tr = build_live_playing_card(f4, 840, 575, "02", "MUA MỸ PHẨM THEO TREND MÀ QUÊN LOẠI DA", "rose_satin", (255, 182, 218))
            paste_3d_smooth(
                base_im, c_tr, 540.0 + (1.0 - ui) * 65.0, 425.0 + math.sin(t * 1.5) * 4.0,
                scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo),
                rx_deg=-1.8, ry_deg=5.0 + (1.0 - ui) * 12.0 - (1.0 - uo) * 10.0,
                opacity=op, dof_sigma=sig
            )

        # F. DECK #2 (39.20 - 49.06s): 4-CARD PLAYING-CARD FAN -> PUSH 01..04 -> RE-FAN ALL 4 -> PUSH TO 04 ON "KÍCH ỨNG"!
        if 39.20 <= t < 49.06:
            z_kb = 1.01 + 0.05 * ((t - 39.20) / 9.8)
            deck2 = [
                build_live_playing_card(st_imgs["st_01_oily"],      680, 490, "01", "DA DẦU • DƯ BÃ NHỜN",         "gold",     (252, 225, 129), zoom=z_kb),
                build_live_playing_card(st_imgs["st_02_dry"],       680, 490, "02", "DA KHÔ • THIẾU ẨM CĂNG RÁT",  "sapphire", (136, 215, 255), zoom=z_kb),
                build_live_playing_card(st_imgs["st_03_combo"],     680, 490, "03", "DA HỖN HỢP • DẦU T-ZONE",     "emerald",  ( 92, 224, 181), zoom=z_kb),
                build_live_playing_card(st_imgs["st_04_sensitive"], 680, 490, "04", "DA NHẠY CẢM • DỄ KÍCH ỨNG",   "coral",    (255, 165, 122), zoom=z_kb),
            ]
            render_3d_playing_card_deck(
                base_im, deck2, t, 39.20, 49.06,
                focus_schedule=[(39.20, 0), (40.94, 1), (41.72, 2), (42.64, 3)],
                fan_hold_until=39.92, refan_window=(43.95, 47.45), cy_base=425.0
            )

        # G. Direct Source + Emphasis Banner #3 ("Sai lầm cuối cùng là chỉ chăm sóc bên ngoài mà quên bên trong", 49.06 - 53.50s)
        if 49.06 <= t < 53.52:
            ui, uo, op, sig = ae_in_out(t, 49.08, 53.48, d_in=0.46, d_out=0.40, overshoot=1.12)
            ec3 = get_emphasis_banner_card("SAI LẦM PHỔ BIẾN #3", "QUÊN CHĂM BÊN TRONG", "CHỈ BÔI MỸ PHẨM BÊN NGOÀI • BỎ QUA LỐI SỐNG", pal_h="gold")
            paste_3d_smooth(base_im, ec3, 540.0, 395.0 + (1.0 - ui) * (-34.0) - (1.0 - uo) * 20.0, scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), rx_deg=(1.0 - ui) * 10.0, opacity=op, dof_sigma=sig)

        # H. DECK #3 (53.48 - 67.86s): 3 Lifestyle Cards Fan Out -> 01 Cosmetics -> 02 1-2 AM -> 03 Sugar -> PUSH BACK TO 01 Cosmetics (63.35s)!
        if 53.48 <= t < 67.86:
            f5 = get_clip_frame_smooth(clips, "c5_cosmetic_vanity",   max(0.0, t - 53.48), target_span=14.4)
            f6 = get_clip_frame_smooth(clips, "c6_late_night_2am",    max(0.0, t - 56.80), target_span=5.5)
            f7 = get_clip_frame_smooth(clips, "c7_junkfood_lowwater", max(0.0, t - 59.60), target_span=8.2)
            deck3 = [
                build_live_playing_card(f5, 740, 520, "01", "TRĂM TRIỆU MỸ PHẨM ĐẮT TIỀN", "gold",     (252, 225, 129)),
                build_live_playing_card(f6, 740, 520, "02", "THỨC KHUYA ĐẾN 1–2 GIỜ SÁNG",  "sapphire", (136, 215, 255)),
                build_live_playing_card(f7, 740, 520, "03", "ÍT NƯỚC • NHIỀU ĐỒ NGỌT & ĐỒ NHANH", "coral", (255, 165, 122)),
            ]
            render_3d_playing_card_deck(
                base_im, deck3, t, 53.48, 67.86,
                focus_schedule=[(53.48, 0), (56.92, 1), (59.70, 2), (63.35, 0)],
                fan_hold_until=54.45, cy_base=425.0
            )

        # I. Direct Source + Core Takeaway Card ("Đừng cố tìm 1 sản phẩm giải quyết mọi vấn đề", 67.88 - 71.50s)
        if 67.86 <= t < 71.54:
            ui, uo, op, sig = ae_in_out(t, 67.88, 71.50, d_in=0.46, d_out=0.40, overshoot=1.12)
            ec4 = get_emphasis_banner_card("NGUYÊN TẮC CỐT LÕI", "ĐỔI THÓI QUEN TỪ GỐC", "KHÔNG CÓ 1 MỸ PHẨM GIẢI QUYẾT MỌI VẤN ĐỀ", pal_h="emerald")
            paste_3d_smooth(base_im, ec4, 540.0, 395.0 + (1.0 - ui) * (-34.0) - (1.0 - uo) * 20.0, scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), rx_deg=(1.0 - ui) * 10.0, opacity=op, dof_sigma=sig)

        # J. Finale Summary Card Behind Speaker (76.35 - 80.70s)
        if t >= 76.30:
            ui, uo, op, sig = ae_in_out(t, 76.35, 80.68, d_in=0.50, d_out=0.38, overshoot=1.10)
            ec5 = get_emphasis_banner_card("KHI NỀN TẢNG ĐÃ ĐÚNG", "DA KHỎE ĐẸP BỀN VỮNG", "CHỌN ĐÚNG SẢN PHẨM • PHÁT HUY TỐI ĐA HIỆU QUẢ", pal_h="gold")
            paste_3d_smooth(base_im, ec5, 540.0, 390.0 + (1.0 - ui) * (-30.0), scale=0.90 + 0.10 * ui, rx_deg=(1.0 - ui) * 8.0, opacity=op, dof_sigma=sig)

        # ==================================================================
        # 2. RE-COMPOSITE PHARMACIST + DESK CLEANLY IN FOREGROUND!
        # ==================================================================
        fg_alpha = np.maximum(m_arr, desk_mask)
        comp_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # ==================================================================
        # 3. FOREGROUND PUNCHY EMPHASIS CALLOUT BADGES AT KEY VOCAL STRESSES!
        #    ("có text chỗ những chỗ nhấn nhá đầy đủ sfx")
        # ==================================================================
        emph_pills = [
            ( 3.20,  5.76, "3 SAI LẦM PHỔ BIẾN NHẤT",        "gold",       540.0,  70.0),
            (18.05, 20.55, "HỎNG MÀNG BẢO VỆ TỰ NHIÊN!",     "coral",      540.0,  68.0),
            (27.35, 30.02, "KHÔ BÊN TRONG • BÓNG NHỜN NGOÀI","gold",       540.0,  68.0),
            (43.65, 48.98, "NHU CẦU MỖI LOẠI DA KHÁC HẲN!",  "rose_satin", 540.0,  68.0),
            (57.20, 59.62, "THỨC KHUYA 1:00 – 2:00 SÁNG!",   "sapphire",   540.0,  68.0),
            (64.25, 67.80, "MỸ PHẨM ĐẮT CŨNG KHÓ HIỆU QUẢ!", "coral",      540.0,  68.0),
        ]
        for est, een, etxt, epal, ecx, ecy in emph_pills:
            if est <= t < een:
                ui_e, uo_e, op_e, sig_e = ae_in_out(t, est, een, d_in=0.38, d_out=0.34, overshoot=1.14)
                ep = get_3d_pill(etxt, palette=epal, font_sz=22)
                paste_3d_smooth(
                    comp_im, ep, ecx, ecy + (1.0 - ui_e) * (-24.0) - (1.0 - uo_e) * 16.0,
                    scale=(0.88 + 0.12 * ui_e) * (0.94 + 0.06 * uo_e), rx_deg=(1.0 - ui_e) * 12.0,
                    opacity=op_e, dof_sigma=sig_e
                )

        # ==================================================================
        # 4. FULL-SCREEN 9:16 REALISTIC HEALTHY HABITS CUTAWAY (71.50 - 76.45s)
        # ==================================================================
        in_cutaway = False
        if 71.25 <= t <= 76.68:
            u_in_c  = septic_smooth(clamp01((t - 71.25) / 0.54))
            u_out_c = septic_smooth(clamp01((76.68 - t) / 0.54))
            u_cut = min(u_in_c, u_out_c)
            if u_cut > 0.005:
                in_cutaway = (u_cut > 0.5)
                vf_h = get_clip_frame_smooth(clips, "c8_healthy_routine", max(0.0, t - 71.25), target_span=5.4)
                cut_im = fit_cover_subpixel(vf_h, W, H, zoom=1.00 + 0.03 * clamp01((t - 71.25) / 5.4)).convert("RGBA")
                vy = np.linspace(0.0, 1.0, 560, dtype=np.float32)[:, None]
                va = np.zeros((560, W, 4), dtype=np.uint8)
                va[:, :, 0], va[:, :, 1], va[:, :, 2] = (10, 18, 26)
                va[:, :, 3] = (vy * vy * 190.0).astype(np.uint8)
                cut_im.alpha_composite(Image.fromarray(va, "RGBA"), dest=(0, H - 560))

                ui_h, uo_h, op_h, sig_h = ae_in_out(t, 71.50, 76.45, d_in=0.45, d_out=0.38)
                if op_h > 0.01:
                    hdr_h = get_emphasis_banner_card("BẮT ĐẦU TỪ CHÍNH MÌNH", "THAY ĐỔI THÓI QUEN ĐÚNG", "NGỦ ĐỦ GIẤC • UỐNG ĐỦ NƯỚC • LÀM SẠCH DỊU NHẸ", pal_h="emerald")
                    paste_3d_smooth(cut_im, hdr_h, 540.0, 235.0 + (1.0 - ui_h) * (-28.0), scale=0.88 + 0.12 * ui_h, rx_deg=2.5, opacity=op_h, dof_sigma=sig_h)
                    pip = make_live_speaker_pip(fg_rgb, 246, 328)
                    paste_3d_smooth(cut_im, pip, 895.0 + (1.0 - ui_h) * 50.0, 1615.0, scale=0.88 + 0.12 * ui_h, ry_deg=-8.0, rz_deg=1.5, opacity=op_h, dof_sigma=sig_h)
                comp_im = optical_soft_transition(comp_im, cut_im, u_cut)

        # ==================================================================
        # 5. HOOK TYPOGRAPHY ON WHITE BLAZER (0.04 - 1.80s, Dark Stroke!)
        # ==================================================================
        if 0.04 <= t <= 1.80:
            _, u_ho, op_ho, sig_ho = ae_in_out(t, 0.04, 1.80, d_in=0.32, d_out=0.30)
            sheen_hk = -0.2 + 1.45 * clamp01((t - 0.15) / 1.4)
            ui1, _, op1, sig1 = ae_in_out(t, 0.04, 1.80, d_in=0.34, d_out=0.30, overshoot=1.14)
            sp_h1 = apply_sheen_sweep(
                render_5stop_grad_sprite("NHỮNG SAI LẦM", FONT_MONTS_BLK, 62, palette="coral", stroke_col=(14, 18, 30), stroke_w=8, extrude_col=(8, 10, 18), extrude_dy=4, shadow_alpha=115, glow_alpha=55),
                sheen_hk
            )
            paste_3d_smooth(comp_im, sp_h1, 540.0, 1105.0 + (1.0 - ui1) * 24.0 - (1.0 - u_ho) * 14.0, scale=(0.88 + 0.12 * ui1) * (0.94 + 0.06 * u_ho), rx_deg=(1.0 - ui1) * 12.0, opacity=op1, dof_sigma=max(sig1, sig_ho))
            if t >= 0.72:
                ui2, _, op2, sig2 = ae_in_out(t, 0.72, 1.80, d_in=0.34, d_out=0.30, overshoot=1.14)
                sp_h2 = apply_sheen_sweep(
                    render_5stop_grad_sprite("KHI CHĂM SÓC DA!", FONT_BE_XBOLD, 52, palette="gold", stroke_col=(14, 18, 30), stroke_w=8, extrude_col=(8, 10, 18), extrude_dy=4, shadow_alpha=115, glow_alpha=55),
                    -0.2 + 1.45 * clamp01((t - 0.80) / 0.9)
                )
                paste_3d_smooth(comp_im, sp_h2, 540.0, 1202.0 + (1.0 - ui2) * 22.0 - (1.0 - u_ho) * 14.0, scale=(0.88 + 0.12 * ui2) * (0.94 + 0.06 * u_ho), rx_deg=(1.0 - ui2) * 12.0, opacity=op2, dof_sigma=max(sig2, sig_ho))

        # ==================================================================
        # 6. HIGH-CONTRAST 5-STOP GRADIENT SUBTITLES OVER WHITE BLAZER!
        # ==================================================================
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in  = t - g["t0"]
                dt_out = g["t1"] - t
                u_g_out  = septic_smooth(min(1.0, dt_out / 0.18))
                dy_g_out = -(1.0 - septic_smooth(min(1.0, dt_out / 0.24))) * 12.0
                sc_g_out = 0.94 + 0.06 * septic_smooth(min(1.0, dt_out / 0.24))
                sig_out  = (1.0 - u_g_out) * 1.1

                if in_cutaway:
                    min_x, max_x, x_center = 42.0, 748.0, 395.0
                    cap_sz_base = 46.0
                    y_base = 1545.0 if len(g["lines"]) >= 2 else 1575.0
                    lh = 58.0
                else:
                    min_x, max_x, x_center = 48.0, 1032.0, 540.0
                    cap_sz_base = 54.0
                    y_base = 1135.0 if len(g["lines"]) >= 2 else 1165.0
                    lh = 64.0

                max_w_ok = max_x - min_x
                gap = 19.0
                sheen_sub = -0.25 + 1.50 * (((t - g["t0"]) % 2.4) / 1.8)

                for li, ln in enumerate(g["lines"]):
                    raw_ln  = clamp01(max(0.0, dt_in - li * 0.04) / 0.24)
                    raw_op  = clamp01(max(0.0, dt_in - li * 0.04) / 0.15)
                    u_ln_in = ease_out_back_soft(raw_ln, overshoot=1.08)
                    op_ln   = quintic_smooth(raw_op) * u_g_out
                    if op_ln <= 0.008:
                        continue
                    dy_ln  = (1.0 - u_ln_in) * 16.0 + dy_g_out
                    sig_ln = (1.0 - quintic_smooth(raw_op)) * 1.2 + sig_out
                    sc_ln  = (0.93 + 0.07 * u_ln_in) * sc_g_out

                    word_renders, total_w = [], 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_active = (ws - 0.05) <= t <= (we + 0.22)
                        act_pulse = 1.055 if is_active else 1.0
                        if wtxt in GOLD_W:
                            pal, f_use, k = "gold", FONT_BE_XBOLD, 1.05
                        elif wtxt in CORAL_W:
                            pal, f_use, k = "coral", FONT_BE_XBOLD, 1.05
                        elif wtxt in EMERALD_W:
                            pal, f_use, k = "emerald", FONT_BE_XBOLD, 1.05
                        else:
                            pal, f_use, k = ("gold" if is_active else "pearl"), FONT_BE_BOLD, 1.0

                        sz_use = cap_sz_base * k
                        # Thick 7px deep midnight stroke + drop shadow so text is 100% razor-sharp over her bright white blazer!
                        sp_tup = render_5stop_grad_sprite(
                            wtxt, f_use, sz_use, palette=pal,
                            stroke_col=(12, 16, 28), stroke_w=7,
                            extrude_col=(6, 10, 18), extrude_dy=3,
                            shadow_alpha=110, glow_alpha=(45 if pal != "pearl" else 0)
                        )
                        sp_im = apply_sheen_sweep(sp_tup, sheen_sub) if pal != "pearl" else sp_tup[0]
                        adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(f_use, sz_use)) + 5.0
                        word_renders.append((sp_im, adv, act_pulse))
                        total_w += adv + (gap if wi > 0 else 0.0)

                    fit_k = min(1.0, max_w_ok / max(1.0, total_w))
                    eff_tot = total_w * fit_k
                    cur_x = max(min_x, min(max_x - eff_tot, x_center - eff_tot * 0.5))
                    cur_y = y_base + li * lh + dy_ln

                    for sp_im, adv, act_pulse in word_renders:
                        eff_adv = adv * fit_k
                        paste_3d_smooth(comp_im, sp_im, cur_x + eff_adv * 0.5, cur_y, scale=sc_ln * fit_k * act_pulse, opacity=op_ln, dof_sigma=sig_ln)
                        cur_x += eff_adv + gap * fit_k
                break

        # 7. Closing Ribbon (76.60 - 80.62s) + Legal Bar
        if 76.60 <= t <= 80.62:
            ui_c, uo_c, op_c, sig_c = ae_in_out(t, 76.60, 80.62, d_in=0.45, d_out=0.38)
            paste_3d_smooth(comp_im, cta_ribbon, 540.0, 1806.0 + (1.0 - ui_c) * 22.0 + (1.0 - uo_c) * 14.0, scale=(0.90 + 0.10 * ui_c) * (0.94 + 0.06 * uo_c), opacity=op_c, dof_sigma=sig_c)

        bar_bot = Image.new("RGBA", (W, 44), (14, 18, 28, 160))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 44))
        paste_3d_smooth(comp_im, legal_sp, 540.0, H - 22.0, scale=1.0, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"skincare_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/2422 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close(); writer.wait()
    reader_a.close()
    reader_m.stdout.close(); reader_m.wait()

    if test_mode and test_saved:
        imgs = [Image.open(p).resize((360, 640), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (360 * 3, 640 * 3))
        for i, im in enumerate(imgs[:9]):
            grid.paste(im, ((i % 3) * 360, (i // 3) * 640))
        gp = os.path.join(CHECK_DIR, "skincare_carddeck_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved skincare_carddeck_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM Skincare Card-Deck video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
