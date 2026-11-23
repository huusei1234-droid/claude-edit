import json, math, os, re, subprocess, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter1d
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR   = r"d:\AI\full studio\output\htpm-tokyo"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
OV4K_DIR   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k"
FONTS_DIR  = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FCP_MOV    = os.path.join(PROJ_DIR, "fcp_ae_overlays.mov")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

# Curated Harmonious Vietnamese Font System
FONT_HERO_SANS   = os.path.join(FONTS_DIR, "Montserrat-Black.ttf")
FONT_SUB_UNIFIED = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_SUB_SEMI    = os.path.join(FONTS_DIR, "BeVietnamPro-SemiBold.ttf")
FONT_CONDENSED   = os.path.join(FONTS_DIR, "Oswald-Bold.ttf")
FONT_BE_MED      = os.path.join(FONTS_DIR, "BeVietnamPro-Medium.ttf")

# Bright, High-Luminance Luxury 5-Stop Gradient Palettes
GRAD_PALETTES = {
    "gold": [
        (0.00, (255, 254, 244)),
        (0.26, (255, 230, 138)),
        (0.52, (226, 158,  42)),
        (0.78, (255, 240, 178)),
        (1.00, (176, 110,  18)),
    ],
    "rose_satin": [
        (0.00, (255, 242, 249)),
        (0.26, (255, 138, 198)),
        (0.52, (232,  46, 134)),
        (0.78, (255, 182, 222)),
        (1.00, (172,  20,  94)),
    ],
    "emerald": [
        (0.00, (242, 255, 250)),
        (0.26, (118, 242, 198)),
        (0.52, ( 26, 184, 130)),
        (0.78, (178, 252, 226)),
        (1.00, ( 14, 122,  84)),
    ],
    "sapphire": [
        (0.00, (242, 252, 255)),
        (0.26, (132, 224, 255)),
        (0.52, ( 38, 146, 248)),
        (0.78, (186, 238, 255)),
        (1.00, ( 18,  92, 186)),
    ],
    "coral": [
        (0.00, (255, 248, 238)),
        (0.26, (255, 174, 112)),
        (0.52, (244,  88,  52)),
        (0.78, (255, 208, 170)),
        (1.00, (178,  42,  18)),
    ],
    "pearl": [
        (0.00, (255, 255, 255)),
        (0.45, (248, 251, 255)),
        (0.75, (232, 240, 248)),
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

def septic_smooth(u):
    u = clamp01(u)
    u4 = u * u * u * u
    return u4 * (35.0 + u * (-84.0 + u * (70.0 - 20.0 * u)))

def ease_out_back_soft(u, overshoot=1.08):
    u = clamp01(u) - 1.0
    return 1.0 + u * u * ((overshoot + 1.0) * u + overshoot)

def ae_in_out(t, st, en, d_in=0.44, d_out=0.38, overshoot=1.08):
    if t <= st or t >= en:
        return 0.0, 0.0, 0.0, 0.0
    raw_in  = clamp01((t - st) / max(0.06, d_in))
    raw_out = clamp01((en - t) / max(0.06, d_out))
    u_in    = ease_out_back_soft(raw_in, overshoot=overshoot)
    u_out   = septic_smooth(raw_out)
    op      = min(quintic_smooth(min(1.0, raw_in * 1.38)), u_out)
    sigma   = (1.0 - quintic_smooth(raw_in)) * 3.0 + (1.0 - u_out) * 2.6
    return u_in, u_out, op, sigma

# ======================================================================
# 1. 3D PERSPECTIVE + SHUTTER MOTION BLUR + SCREEN VIDEO OVERLAY ENGINE
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
    if opacity <= 0.005 or scale <= 0.02:
        return
    sw, sh = sprite_im.size
    rx, ry, rz = math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg)
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
    x0, y0 = int(math.floor(proj_x.min())) - pad_m, int(math.floor(proj_y.min())) - pad_m
    x1, y1 = int(math.ceil(proj_x.max())) + pad_m, int(math.ceil(proj_y.max())) + pad_m
    out_w, out_h = max(8, x1 - x0), max(8, y1 - y0)

    dst_pts = [(float(proj_x[i] - x0), float(proj_y[i] - y0)) for i in range(4)]
    src_pts = [(0.0, 0.0), (float(sw), 0.0), (float(sw), float(sh)), (0.0, float(sh))]
    coeffs = _solve_homography_8(src_pts, dst_pts)
    warped = sprite_im.transform((out_w, out_h), Image.Transform.PERSPECTIVE, coeffs, resample=Image.Resampling.BICUBIC)

    arr = np.array(warped, dtype=np.float32)
    a_norm = arr[:, :, 3:4] / 255.0
    arr[:, :, 0:3] *= a_norm * float(dim)

    k_mb = int(round(abs(mb_dx) * 0.55))
    if k_mb >= 2:
        arr = uniform_filter1d(arr, size=min(26, k_mb), axis=1, mode="constant", cval=0.0)
    if dof_sigma >= 0.12:
        arr = gaussian_filter(arr, sigma=(min(7.5, dof_sigma), min(7.5, dof_sigma), 0.0), mode="constant", cval=0.0)

    a_out = np.clip(arr[:, :, 3:4] * clamp01(opacity), 0.0, 255.0)
    rgb_out = np.where(arr[:, :, 3:4] > 1.0, arr[:, :, 0:3] / np.maximum(1e-3, arr[:, :, 3:4] / 255.0), 0.0)
    warped_im = Image.fromarray(np.concatenate([np.clip(rgb_out, 0, 255), a_out], axis=2).astype(np.uint8), "RGBA")

    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(canvas_im.width, x0 + out_w), min(canvas_im.height, y0 + out_h)
    if dx1 > dx0 and dy1 > dy0:
        canvas_im.alpha_composite(warped_im.crop((dx0 - x0, dy0 - y0, dx1 - x0, dy1 - y0)), dest=(dx0, dy0))

def blend_screen_overlay(rgba_im, ov_rgb, strength=0.28):
    if strength <= 0.008 or ov_rgb is None:
        return rgba_im
    base = np.array(rgba_im, dtype=np.float32)
    ov = ov_rgb.astype(np.float32) * float(strength)
    scr = 255.0 - ((255.0 - base[:, :, 0:3]) * (255.0 - ov)) / 255.0
    base[:, :, 0:3] = np.clip(scr, 0, 255)
    return Image.fromarray(base.astype(np.uint8), "RGBA")

def fit_cover_subpixel(rgb_arr, target_w, target_h, zoom=1.0, pan_x=0.0, pan_y=0.0):
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    inv_s = 1.0 / base_scale
    half_w_s = (target_w * 0.5) * inv_s
    half_h_s = (target_h * 0.5) * inv_s
    cx_src = max(half_w_s, min(sw - half_w_s, sw * 0.5 + pan_x * sw))
    cy_src = max(half_h_s, min(sh - half_h_s, sh * 0.5 + pan_y * sh))
    return Image.fromarray(rgb_arr, "RGB").transform(
        (target_w, target_h), Image.Transform.AFFINE, (inv_s, 0.0, cx_src - half_w_s, 0.0, inv_s, cy_src - half_h_s), resample=Image.Resampling.BICUBIC
    )

# ======================================================================
# 2. 2-LAYER LUXURY 3D BEVEL + 5-STOP GRADIENT TYPOGRAPHY ENGINE
#    (Used for Word-by-Word Subtitles & Card Labels)
# ======================================================================
_grad_sprite_cache = {}
def render_luxury_grad_text(text, font_path, size, palette="gold", style="dark_bevel", stroke_w=6, shadow_alpha=125):
    eff_sw = max(3, min(stroke_w, int(round(size * 0.125))))
    key = (text, font_path, int(round(size)), palette, eff_sw, shadow_alpha)
    if key in _grad_sprite_cache:
        return _grad_sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=eff_sw)
    tw, th = max(4, bbox[2] - bbox[0]), max(4, bbox[3] - bbox[1])
    pad = int(eff_sw + 24)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    stops = GRAD_PALETTES.get(palette, GRAD_PALETTES["gold"])
    mid_col = stops[len(stops) // 2][1]

    if palette != "pearl" and size >= 26:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(1, eff_sw // 2), stroke_fill=255)
        gb = np.array(gm.filter(ImageFilter.GaussianBlur(radius=7.5)), dtype=np.float32) / 255.0
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0], ga[:, :, 1], ga[:, :, 2] = mid_col
        ga[:, :, 3] = np.clip(gb * 42.0, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 6), text, font=font, fill=255, stroke_width=eff_sw, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5.8)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (10, 12, 22)
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    ex_dy = 3 if size >= 38 else (2 if size >= 24 else 1)
    ex_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(ex_im).text((ox + 1, oy + ex_dy), text, font=font, fill=(8, 10, 18, 248), stroke_width=eff_sw, stroke_fill=(8, 10, 18, 248))
    base = Image.alpha_composite(base, ex_im)

    st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(16, 18, 30, 255), stroke_width=eff_sw, stroke_fill=(16, 18, 30, 255))
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
    band = np.exp(-((diag - sheen_phase) ** 2) / 0.0050) * 95.0 * arr_m
    if band.max() < 2.5:
        return base
    out = np.array(base, dtype=np.float32)
    out[:, :, 0] = np.clip(out[:, :, 0] + band, 0, 255)
    out[:, :, 1] = np.clip(out[:, :, 1] + band * 0.98, 0, 255)
    out[:, :, 2] = np.clip(out[:, :, 2] + band * 0.94, 0, 255)
    return Image.fromarray(out.astype(np.uint8), "RGBA")

# ======================================================================
# 3. ROCK-STEADY MULTI-STYLE OVERLAY CARDS (ZERO SINE WOBBLE!)
# ======================================================================
def render_diagonal_split_card(canvas_im, vf_l, vf_r, t, st, en):
    ui, uo, op, sig = ae_in_out(t, st, en, d_in=0.46, d_out=0.38, overshoot=1.08)
    if op <= 0.008:
        return
    pw, ph, pad = 948, 444, 24
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + pw, pad + ph + 10], radius=38, fill=(10, 12, 24, 126))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=13)))

    u_l = septic_smooth(clamp01((t - st) / 0.48))
    u_r = septic_smooth(clamp01((t - st - 0.12) / 0.48))
    im_l = fit_cover_subpixel(vf_l, pw, ph, zoom=1.06, pan_x=+0.14 + (1.0 - u_l) * 0.05)
    im_r = fit_cover_subpixel(vf_r, pw, ph, zoom=1.06, pan_x=-0.14 - (1.0 - u_r) * 0.05)

    yy, xx = np.ogrid[0:ph, 0:pw]
    diag = (xx.astype(np.float32) - pw * 0.50) + (yy.astype(np.float32) - ph * 0.50) * 0.23
    w_r = np.clip((diag + 16.0) / 32.0, 0.0, 1.0)[:, :, None]
    comp_rgb = (np.array(im_l, dtype=np.float32) * (1.0 - w_r) + np.array(im_r, dtype=np.float32) * w_r).astype(np.uint8)

    rmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=38, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(Image.fromarray(comp_rgb, "RGB"), (pad, pad), mask=rmask)
    card = Image.alpha_composite(card, vl)

    d = ImageDraw.Draw(card)
    x_top = pad + pw * 0.50 - (-ph * 0.50) * 0.23
    x_bot = pad + pw * 0.50 - (+ph * 0.50) * 0.23
    d.line([(x_top, pad + 3), (x_bot, pad + ph - 3)], fill=(255, 232, 152, 248), width=4)
    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=38, outline=(252, 225, 129, 242), width=3)

    for lx, ltxt, lpal in [(pad + 230, "BẤT TIỆN SINH HOẠT", "pearl"), (pad + pw - 235, "TỔN THƯƠNG NIÊM MẠC", "coral")]:
        d.rounded_rectangle([lx - 185, pad + 16, lx + 185, pad + 62], radius=23, fill=(18, 16, 30, 224), outline=(252, 225, 129, 200), width=2)
        sp, _ = render_luxury_grad_text(ltxt, FONT_SUB_UNIFIED, 20, palette=lpal, style="dark_bevel", stroke_w=4, shadow_alpha=40)
        paste_3d_smooth(card, sp, lx, pad + 39)

    paste_3d_smooth(
        canvas_im, card,
        540.0, 392.0 + (1.0 - ui) * (-26.0) - (1.0 - uo) * 18.0,
        scale=(0.90 + 0.10 * ui) * (0.94 + 0.06 * uo),
        rx_deg=(1.0 - ui) * 7.0, opacity=op, dof_sigma=sig
    )

_card_shell_cache = {}
def build_live_playing_card(vf_rgb, w, h, idx_str, title_str, palette="gold", rim_rgb=(252, 225, 129), zoom=1.02):
    k = (w, h, idx_str, title_str, palette, rim_rgb)
    if k not in _card_shell_cache:
        pad = 24
        cw, ch = w + pad * 2, h + pad * 2
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius=34, fill=(10, 12, 24, 128))
        sh = sh.filter(ImageFilter.GaussianBlur(radius=14))
        rmask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=255)

        overlay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        vy = np.linspace(1.0, 0.0, 86, dtype=np.float32)[:, None]
        ha = np.zeros((86, w, 4), dtype=np.uint8)
        ha[:, :, 0], ha[:, :, 1], ha[:, :, 2] = (14, 16, 28)
        ha[:, :, 3] = (vy * 218.0).astype(np.uint8)
        overlay.paste(Image.fromarray(ha, "RGBA"), (pad, pad), mask=rmask.crop((0, 0, w, 86)))

        d = ImageDraw.Draw(overlay)
        d.rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius=34, outline=(*rim_rgb, 245), width=3)
        d.rounded_rectangle([pad + 5, pad + 5, pad + w - 6, pad + h - 6], radius=29, outline=(255, 255, 255, 110), width=1)
        d.rounded_rectangle([pad + 16, pad + 14, pad + 78, pad + 56], radius=16, fill=(22, 20, 38, 238), outline=(*rim_rgb, 228), width=2)
        sp_idx, _ = render_luxury_grad_text(idx_str, FONT_HERO_SANS, 23, palette=palette, style="dark_bevel", stroke_w=3, shadow_alpha=0)
        sp_ic = sp_idx.crop(sp_idx.getbbox())
        overlay.alpha_composite(sp_ic, dest=(pad + 47 - sp_ic.width // 2, pad + 35 - sp_ic.height // 2))

        sp_t, _ = render_luxury_grad_text(title_str, FONT_SUB_UNIFIED, 21, palette="pearl", style="dark_bevel", stroke_w=4, shadow_alpha=60)
        sp_tc = sp_t.crop(sp_t.getbbox())
        max_tw = w - 108
        if sp_tc.width > max_tw:
            nh = max(12, int(round(sp_tc.height * (max_tw / float(sp_tc.width)))))
            sp_tc = sp_tc.resize((max_tw, nh), Image.Resampling.LANCZOS)
        overlay.alpha_composite(sp_tc, dest=(pad + 90, pad + 35 - sp_tc.height // 2))
        _card_shell_cache[k] = (sh, rmask, overlay, pad)

    sh, rmask, overlay, pad = _card_shell_cache[k]
    card = sh.copy()
    vlay = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    vlay.paste(fit_cover_subpixel(vf_rgb, w, h, zoom=zoom), (pad, pad), mask=rmask)
    return Image.alpha_composite(Image.alpha_composite(card, vlay), overlay)

def render_3d_playing_card_deck(canvas_im, card_sprites, t, st, en, focus_schedule, fan_hold_until=None, cy_base=408.0):
    if t <= st or t >= en:
        return
    K = len(card_sprites)
    raw_in  = clamp01((t - st) / 0.56)
    raw_out = clamp01((en - t) / 0.46)
    u_in    = ease_out_back_soft(raw_in, overshoot=1.07)
    u_out   = septic_smooth(raw_out)
    op_deck = min(quintic_smooth(min(1.0, raw_in * 1.35)), u_out)
    if op_deck <= 0.008:
        return

    w_car = septic_smooth(clamp01((t - fan_hold_until) / 0.58)) if fan_hold_until is not None else 0.0
    cur_val, vel = float(focus_schedule[0][1]), 0.0
    for idx in range(1, len(focus_schedule)):
        ts, targ = focus_schedule[idx]
        prev_t = focus_schedule[idx - 1][1]
        if t >= ts:
            u = clamp01((t - ts) / 0.58)
            sm = septic_smooth(u)
            if 0.001 < u < 0.999:
                vel = (float(targ) - float(prev_t)) * 140.0 * (u ** 3) * ((1.0 - u) ** 3) / 0.58
            cur_val = float(prev_t) + (float(targ) - float(prev_t)) * sm

    mid_k = (K - 1) * 0.5
    draw_queue = []
    for i in range(K):
        s_fan = i - mid_k
        fx = 540.0 + s_fan * 262.0 * u_in
        fy = cy_base + 8.0 + abs(s_fan) * 28.0 + (1.0 - u_in) * 70.0
        f_sc = 0.62 * (0.82 + 0.18 * u_in)
        f_ry, f_rz, f_rx = -s_fan * 13.0 * u_in, s_fan * 8.0 * u_in, (1.0 - u_in) * 10.0
        f_z = 10.0 - abs(s_fan) * 6.0

        rel = float(i) - cur_val
        abs_r = abs(rel)
        swap_arc = math.sin(clamp01(abs_r) * math.pi) if abs_r < 1.0 else 0.0
        cx_car = 540.0 + rel * 228.0 + (-34.0 if rel < 0 else 34.0) * swap_arc * 0.45
        cy_car = cy_base - 6.0 + min(2.2, abs_r) * 30.0 - swap_arc * 12.0
        sc_car = 0.94 - min(1.0, abs_r) * 0.22 - max(0.0, abs_r - 1.0) * 0.05
        ry_car = -max(-22.0, min(22.0, rel * 16.0))
        rz_car = max(-10.0, min(10.0, rel * 6.5))
        rx_car = -1.2 * (1.0 - min(1.0, abs_r))
        dim_car = 1.00 - min(1.0, abs_r) * 0.24
        dof_car = min(1.0, abs_r) * 1.7
        z_car   = 100.0 * math.cos(min(1.5, abs_r)) - abs_r * 25.0

        px = (fx * (1.0 - w_car) + cx_car * w_car) * u_out + 540.0 * (1.0 - u_out)
        py = (fy * (1.0 - w_car) + cy_car * w_car) - (1.0 - u_out) * 36.0
        psc = (f_sc * (1.0 - w_car) + sc_car * w_car) * (0.88 + 0.12 * u_out)
        pry = (f_ry * (1.0 - w_car) + ry_car * w_car) * u_out
        prz = (f_rz * (1.0 - w_car) + rz_car * w_car) * u_out
        prx = (f_rx * (1.0 - w_car) + rx_car * w_car) + (1.0 - u_out) * 8.0
        pdim = 0.98 * (1.0 - w_car) + dim_car * w_car
        pdof = dof_car * w_car + (1.0 - quintic_smooth(raw_in)) * 2.8 + (1.0 - u_out) * 2.8
        pz   = f_z * (1.0 - w_car) + z_car * w_car
        mb_x = -vel * 220.0 * w_car / FPS
        draw_queue.append((pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x))

    draw_queue.sort(key=lambda x: x[0])
    for pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x in draw_queue:
        paste_3d_smooth(canvas_im, card_sprites[i], px, py, scale=psc, rx_deg=prx, ry_deg=pry, rz_deg=prz, opacity=op_deck, dof_sigma=pdof, mb_dx=mb_x, dim=pdim)

def render_hydration_mucosal_bento(canvas_im, vd_cut, t, st, en):
    if t <= st or t >= en:
        return
    ui1, uo1, op1, sig1 = ae_in_out(t, st, en, d_in=0.45, d_out=0.38, overshoot=1.08)
    pw, ph, pad = 446, 396, 20
    cw, ch = pw + pad * 2, ph + pad * 2
    c1 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(c1)
    d1.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=36, fill=(16, 28, 42, 232), outline=(112, 214, 255, 242), width=3)
    s_t1, _ = render_luxury_grad_text("01 • CẤP ẨM SÂU", FONT_CONDENSED, 23, palette="sapphire", style="dark_bevel", stroke_w=3, shadow_alpha=0)
    paste_3d_smooth(c1, s_t1, cw * 0.5, pad + 34)
    u_hyd = septic_smooth(clamp01((t - st - 0.10) / 1.4))
    pct = int(round(35 + 61 * u_hyd))
    gx, gy, gr = cw // 2, pad + 144, 66
    d1.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(10, 20, 34, 240), outline=(65, 130, 180, 140), width=6)
    d1.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=-90, end=int(-90 + 360 * (pct / 100.0)), fill=(104, 218, 255, 255), width=9)
    sp_p, _ = render_luxury_grad_text(f"{pct}%", FONT_HERO_SANS, 38, palette="sapphire", style="dark_bevel", stroke_w=5, shadow_alpha=50)
    paste_3d_smooth(c1, sp_p, gx, gy)
    for li, ln in enumerate(["DUY TRÌ", "ĐỘ ẨM TỰ NHIÊN"]):
        sh, _ = render_luxury_grad_text(ln, FONT_HERO_SANS, 27, palette="sapphire" if li == 1 else "pearl", style="dark_bevel", stroke_w=5, shadow_alpha=60)
        paste_3d_smooth(c1, sh, cw * 0.5, pad + 260 + li * 40)
    paste_3d_smooth(canvas_im, c1, 286.0 - (1.0 - ui1) * 60.0, 388.0, scale=(0.88 + 0.12 * ui1) * (0.94 + 0.06 * uo1), ry_deg=7.5, rz_deg=-1.2, opacity=op1, dof_sigma=sig1)

    if t >= st + 0.82:
        ui2, uo2, op2, sig2 = ae_in_out(t, st + 0.82, en, d_in=0.45, d_out=0.38, overshoot=1.08)
        c2 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(c2)
        d2.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=36, fill=(14, 34, 28, 232), outline=(92, 224, 181, 242), width=3)
        s_t2, _ = render_luxury_grad_text("02 • BẢO VỆ TỪ GỐC", FONT_CONDENSED, 23, palette="emerald", style="dark_bevel", stroke_w=3, shadow_alpha=0)
        paste_3d_smooth(c2, s_t2, cw * 0.5, pad + 34)
        if vd_cut is not None:
            th_im = vd_cut.copy()
            th_im.thumbnail((232, 152), Image.Resampling.LANCZOS)
            c2.alpha_composite(th_im, dest=(int(cw * 0.5 - th_im.width * 0.5), pad + 144 - th_im.height // 2))
        for li, ln in enumerate(["HỖ TRỢ PHỤC HỒI", "NIÊM MẠC"]):
            sh2, _ = render_luxury_grad_text(ln, FONT_HERO_SANS, 27, palette="emerald" if li == 1 else "pearl", style="dark_bevel", stroke_w=5, shadow_alpha=60)
            paste_3d_smooth(c2, sh2, cw * 0.5, pad + 260 + li * 40)
        paste_3d_smooth(canvas_im, c2, 794.0 + (1.0 - ui2) * 60.0, 388.0, scale=(0.88 + 0.12 * ui2) * (0.94 + 0.06 * uo2), ry_deg=-7.5, rz_deg=1.2, opacity=op2, dof_sigma=sig2)

_orb_cache = {}
def get_ing_orb(img_rgb, l1, l2, palette, rim):
    k = (l1, l2, palette)
    if k in _orb_cache:
        return _orb_cache[k]
    ow, oh, pad = 224, 254, 18
    cw, ch = ow + pad * 2, oh + pad * 2
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + ow, pad + oh + 8], radius=44, fill=(10, 14, 26, 118))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + ow, pad + oh], radius=44, fill=(18, 22, 36, 228), outline=(*rim, 245), width=3)
    diam = 140
    cmask = Image.new("L", (diam, diam), 0)
    ImageDraw.Draw(cmask).ellipse([0, 0, diam - 1, diam - 1], fill=255)
    im.paste(fit_cover_subpixel(img_rgb, diam, diam, zoom=1.05), (pad + (ow - diam) // 2, pad + 16), mask=cmask)
    ImageDraw.Draw(im).ellipse([pad + (ow - diam) // 2, pad + 16, pad + (ow + diam) // 2, pad + 16 + diam], outline=(*rim, 238), width=3)
    sp1, _ = render_luxury_grad_text(l1, FONT_HERO_SANS, 21, palette=palette, style="dark_bevel", stroke_w=4, shadow_alpha=45)
    sp2, _ = render_luxury_grad_text(l2, FONT_BE_MED, 17, palette="pearl", style="dark_bevel", stroke_w=3, shadow_alpha=0)
    paste_3d_smooth(im, sp1, cw * 0.5, pad + 186)
    paste_3d_smooth(im, sp2, cw * 0.5, pad + 221)
    _orb_cache[k] = im
    return im

def render_4_ingredients_arc(canvas_im, imgs, t, st, en):
    if t <= st or t >= en:
        return
    _, _, op_all, _ = ae_in_out(t, st, en, d_in=0.35, d_out=0.38)
    arc_im = Image.new("RGBA", (W, 660), (0, 0, 0, 0))
    ImageDraw.Draw(arc_im).arc([75, 245, 1005, 720], start=198, end=342, fill=(252, 225, 129, int(145 * op_all)), width=3)
    canvas_im.alpha_composite(arc_im, dest=(0, 0))

    specs = [
        (25.88, 152.0, 412.0, -7.5, imgs["ing_01_glycerin"],    "GLYCERIN",    "Giữ ẩm chuyên sâu", "sapphire",  (104, 210, 255)),
        (27.00, 410.0, 326.0, -2.5, imgs["ing_02_niacinamide"], "NIACINAMIDE", "Làm dịu niêm mạc",  "rose_satin",(249, 106, 181)),
        (28.62, 670.0, 326.0, +2.5, imgs["ing_03_chamomile"],   "CÚC LA MÃ",   "Kháng khuẩn êm dịu","gold",      (252, 225, 129)),
        (29.48, 928.0, 412.0, +7.5, imgs["ing_04_licorice"],    "CAM THẢO",    "Thảo dược lành tính","emerald",  ( 92, 224, 181)),
    ]
    for tc, cx, cy, rz, rgb_i, l1, l2, pal, rim in specs:
        if t >= tc:
            ui, uo, op, sig = ae_in_out(t, tc, en, d_in=0.40, d_out=0.34, overshoot=1.10)
            orb = get_ing_orb(rgb_i, l1, l2, pal, rim)
            paste_3d_smooth(canvas_im, orb, cx, cy + (1.0 - ui) * 36.0, scale=(0.78 + 0.22 * ui) * (0.92 + 0.08 * uo), rz_deg=rz * ui, ry_deg=-rz * 1.3, opacity=op, dof_sigma=sig)

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
    mix[:, :, 0:3] = np.clip(mix[:, :, 0:3] + bell * 16.0, 0, 255)
    mix[:, :, 3] = 255.0
    return Image.fromarray(mix.astype(np.uint8), "RGBA")

def make_live_speaker_pip(fg_rgb, pw=232, ph=306):
    sub = fg_rgb[610:1510, 230:890]
    im = fit_cover_subpixel(sub, pw, ph, zoom=1.02)
    pad = 16
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    rm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(im, (pad, pad), mask=rm)
    card = Image.alpha_composite(card, vl)
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=32, outline=(246, 207, 101, 245), width=3)
    return card

# ======================================================================
# 4. UNIFIED BE VIETNAM PRO EXTRABOLD SUBTITLES (100% BOX-SAFE!)
# ======================================================================
def load_captions_tokyo():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and (w["start"] + w["end"]) * 0.5 >= 2.75
    ]

    phrases, cur_p = [], []
    for w in words:
        txt, ws, we = w
        if cur_p:
            gap = ws - cur_p[-1][2]
            prev_txt = cur_p[-1][0]
            dur_so_far = cur_p[-1][2] - cur_p[0][1]
            if gap >= 0.40 or (re.search(r"[.?!…;:]$", prev_txt) and len(cur_p) >= 3):
                phrases.append(cur_p); cur_p = []
            elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 4 or dur_so_far >= 1.35):
                phrases.append(cur_p); cur_p = []
            elif len(cur_p) >= 7 or sum(len(x[0]) + 1 for x in cur_p) + len(txt) > 33:
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
            and len(merged[-1]) + len(p) <= 8
        ):
            merged[-1].extend(p)
        else:
            merged.append(p)

    def split_balanced(p):
        tot_c = sum(len(x[0]) + 1 for x in p) - 1
        if len(p) <= 4 and tot_c <= 19:
            return [p]
        bk, bd = max(1, len(p) // 2), 9999
        for k in range(1, len(p)):
            c1 = sum(len(x[0]) + 1 for x in p[:k]) - 1
            c2 = sum(len(x[0]) + 1 for x in p[k:]) - 1
            d = abs(c1 - c2) + (6 if max(c1, c2) > 21 else 0)
            if d < bd:
                bd, bk = d, k
        return [p[:bk], p[bk:]]

    ROSE_W    = {"khô", "khô,", "rát", "Hằng", "Thu.", "Niacinamide"}
    CORAL_W   = {"suy", "yếu.", "vi", "khuẩn", "nấm", "viêm", "nhiễm."}
    EMERALD_W = {"hàng", "rào", "bảo", "vệ", "phục", "hồi", "cúc", "La", "Mã", "cam", "thảo", "Viên", "đặt", "khỏe", "mạnh", "cân", "bằng"}
    SAPPHIRE_W= {"độ", "ẩm", "Glycerin,"}

    cap_groups = []
    for i, p in enumerate(merged):
        t0 = max(2.75, p[0][1] - 0.05)
        last_end = p[-1][2]
        nxt_s = merged[i + 1][0][1] if i + 1 < len(merged) else 37.72
        if nxt_s - last_end <= 0.95:
            t1 = nxt_s - 0.03
        else:
            t1 = min(nxt_s - 0.04, max(last_end + 0.65, t0 + 1.55))
        cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced(p)})
    return cap_groups, ROSE_W, CORAL_W, EMERALD_W, SAPPHIRE_W

class VideoReader:
    def __init__(self, path):
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    def read(self):
        buf = self.proc.stdout.read(W * H * 3)
        return None if len(buf) < W * H * 3 else np.frombuffer(buf, dtype=np.uint8).reshape((H, W, 3))
    def close(self):
        self.proc.stdout.close(); self.proc.wait()

class RgbaVideoReader:
    def __init__(self, path):
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
    def read(self):
        buf = self.proc.stdout.read(W * H * 4)
        return None if len(buf) < W * H * 4 else np.frombuffer(buf, dtype=np.uint8).reshape((H, W, 4))
    def skip(self):
        self.proc.stdout.read(W * H * 4)
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

# ======================================================================
# 5. MAIN RENDER LOOP (1,134 FRAMES = 37.80s — 100% ROCK-STEADY + FCP/AE OVERLAYS!)
# ======================================================================
def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [0.95, 4.10, 7.20, 9.50, 15.00, 17.80, 22.80, 29.70, 31.50]
    }
    if test_mode:
        test_frames.add(int(round(36.40 * FPS)))
    test_saved = []

    if not os.path.exists(FCP_MOV):
        raise FileNotFoundError(f"Missing HyperFrames FCP/AE ProRes 4444 overlay: {FCP_MOV}")

    aroll_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    aroll_path = aroll_graded if os.path.exists(aroll_graded) else os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vid_keys = [
        ("c0_daily_discomfort",       960, 640),
        ("c1_dry_mucosa_macro",       960, 640),
        ("c2_weak_barrier_shield",    960, 640),
        ("c3_microbe_invasion",       960, 640),
        ("p_viendat_exact_showcase", 1280, 720),
    ]
    clips = {}
    for ck, vw, vh in vid_keys:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if os.path.exists(vp):
            clips[ck] = load_vid_frames_wh(vp, vw, vh)
            print(f"Loaded {ck}: {len(clips[ck])} frames")

    ov_bokeh   = load_vid_frames_wh(os.path.join(OV4K_DIR, "01_Golden_Dust_Bokeh_9x16.mp4"), W, H) if os.path.exists(os.path.join(OV4K_DIR, "01_Golden_Dust_Bokeh_9x16.mp4")) else []
    ov_flare   = load_vid_frames_wh(os.path.join(OV4K_DIR, "04_Anamorphic_Gold_Rose_Flare_9x16.mp4"), W, H) if os.path.exists(os.path.join(OV4K_DIR, "04_Anamorphic_Gold_Rose_Flare_9x16.mp4")) else []
    ov_sparkle = load_vid_frames_wh(os.path.join(OV4K_DIR, "05_Soft_Pearl_Sparkles_Bling_9x16.mp4"), W, H) if os.path.exists(os.path.join(OV4K_DIR, "05_Soft_Pearl_Sparkles_Bling_9x16.mp4")) else []

    imgs = {}
    for ifn in ["ing_01_glycerin", "ing_02_niacinamide", "ing_03_chamomile", "ing_04_licorice"]:
        ip = os.path.join(MEDIA_DIR, f"{ifn}.jpg")
        imgs[ifn] = np.array(Image.open(ip).convert("RGB")) if os.path.exists(ip) else np.full((640, 960, 3), 215, dtype=np.uint8)

    vd_cut = Image.open(os.path.join(MEDIA_DIR, "cutout_viendat_exact.png")).convert("RGBA") if os.path.exists(os.path.join(MEDIA_DIR, "cutout_viendat_exact.png")) else None
    cap_groups, ROSE_W, CORAL_W, EMERALD_W, SAPPHIRE_W = load_captions_tokyo()

    scrim_h = 330
    sy = np.linspace(0.0, 1.0, scrim_h, dtype=np.float32)[:, None]
    sa = np.zeros((scrim_h, W, 4), dtype=np.uint8)
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (12, 10, 20)
    sa[:, :, 3] = (np.power(sy, 1.5) * 158.0).astype(np.uint8)
    bot_scrim = Image.fromarray(sa, "RGBA")

    legal_sp, _ = render_luxury_grad_text(
        "Thực phẩm/Sản phẩm hỗ trợ chăm sóc chuyên biệt Hằng Thu Pharma • Không phải là thuốc & không thay thế thuốc chữa bệnh",
        FONT_BE_MED, 16, palette="pearl", style="dark_bevel", stroke_w=3, shadow_alpha=0
    )

    reader_a   = VideoReader(aroll_path)
    reader_m   = subprocess.Popen(["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    reader_fcp = RgbaVideoReader(FCP_MOV)

    raw_vid_out = os.path.join(PROJ_DIR, "_tokyo_master_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    yy_g = np.arange(H, dtype=np.float32)[:, None]
    lower_body_box_guard = np.clip((yy_g - 865.0) / 55.0, 0.0, 1.0)

    frame_idx = 0
    while True:
        rgb_raw = reader_a.read()
        mbuf = reader_m.stdout.read(W * H)
        if rgb_raw is None or len(mbuf) < W * H:
            break
        if test_mode and frame_idx not in test_frames:
            reader_fcp.skip()
            frame_idx += 1
            if frame_idx > max(test_frames):
                break
            continue

        fcp_rgba = reader_fcp.read()
        matte_raw = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W))
        t = frame_idx / FPS

        # 100% ROCK-STEADY PIXEL-EXACT STUDIO LOCK (ZERO ZOOM PUMPING / ZERO PAN JITTER!)
        fg_rgb = rgb_raw
        m_arr  = matte_raw.astype(np.float32) / 255.0
        base_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

        if ov_bokeh and ((16.0 <= t <= 20.5) or (33.1 <= t <= 37.8)):
            base_im = blend_screen_overlay(base_im, ov_bokeh[frame_idx % len(ov_bokeh)], strength=0.24)

        # ==================================================================
        # 1. BEHIND-SPEAKER MULTI-STYLE VISUAL OVERLAYS (ROCK-STEADY!)
        # ==================================================================
        if 2.82 <= t < 5.72:
            vf_l = get_clip_frame_smooth(clips, "c0_daily_discomfort", t - 2.82, target_span=2.9)
            vf_r = get_clip_frame_smooth(clips, "c1_dry_mucosa_macro", t - 2.82, target_span=2.9)
            render_diagonal_split_card(base_im, vf_l, vf_r, t, 2.84, 5.70)

        if 5.72 <= t < 16.04:
            f1 = get_clip_frame_smooth(clips, "c1_dry_mucosa_macro",    max(0.0, t - 5.72),  target_span=3.2)
            f2 = get_clip_frame_smooth(clips, "c2_weak_barrier_shield", max(0.0, t - 8.50),  target_span=3.2)
            f3 = get_clip_frame_smooth(clips, "c3_microbe_invasion",    max(0.0, t - 11.20), target_span=4.9)
            deck = [
                build_live_playing_card(f1, 720, 484, "01", "NIÊM MẠC KHÔ • MẤT ĐỘ ẨM",       "rose_satin", (249, 106, 181)),
                build_live_playing_card(f2, 720, 484, "02", "SUY YẾU HÀNG RÀO BẢO VỆ TỰ NHIÊN","gold",       (252, 225, 129)),
                build_live_playing_card(f3, 720, 484, "03", "VI KHUẨN & NẤM DỄ XÂM NHẬP",     "coral",      (255, 159,  90)),
            ]
            render_3d_playing_card_deck(
                base_im, deck, t, 5.72, 16.04,
                focus_schedule=[(5.72, 0), (8.60, 1), (11.35, 2)],
                fan_hold_until=6.52, cy_base=408.0
            )

        if 20.48 <= t < 25.18:
            render_hydration_mucosal_bento(base_im, vd_cut, t, 20.48, 25.18)

        if 25.18 <= t < 30.26:
            render_4_ingredients_arc(base_im, imgs, t, 25.18, 30.26)

        # ==================================================================
        # 2. RE-COMPOSITE PHARMACIST + HELD BOX + DESK BOXES IN FOREGROUND!
        # ==================================================================
        fg_alpha = np.maximum(m_arr, lower_body_box_guard)
        comp_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # ==================================================================
        # 3. EXACT VIÊN ĐẶT PHỤ KHOA HẰNG THU CUTAWAY (30.20 - 33.22s)
        # ==================================================================
        if 30.20 <= t <= 33.22:
            u_in_c  = septic_smooth(clamp01((t - 30.20) / 0.44))
            u_out_c = septic_smooth(clamp01((33.22 - t) / 0.44))
            u_cut = min(u_in_c, u_out_c)
            if u_cut > 0.005:
                vf_p = get_clip_frame_smooth(clips, "p_viendat_exact_showcase", max(0.0, t - 30.20), target_span=3.02)
                bg_blur = fit_cover_subpixel(vf_p, W, H, zoom=1.18).filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
                cut_im = Image.alpha_composite(bg_blur, Image.new("RGBA", (W, H), (10, 16, 22, 92)))
                ui_p, _, op_p, sig_p = ae_in_out(t, 30.30, 33.10, d_in=0.38, d_out=0.32, overshoot=1.06)
                pcard = build_live_playing_card(vf_p, 984, 620, "HT", "VIÊN ĐẶT PHỤ KHOA HẰNG THU • HỘP 10 VIÊN CHÍNH HÃNG", "emerald", (92, 224, 181), zoom=1.01)
                paste_3d_smooth(cut_im, pcard, 540.0, 710.0 + (1.0 - ui_p) * 22.0, scale=0.92 + 0.08 * ui_p, rx_deg=1.5, opacity=op_p, dof_sigma=sig_p)
                if ov_sparkle:
                    cut_im = blend_screen_overlay(cut_im, ov_sparkle[frame_idx % len(ov_sparkle)], strength=0.28)
                pip = make_live_speaker_pip(fg_rgb, 232, 306)
                paste_3d_smooth(cut_im, pip, 902.0, 1410.0, scale=0.96, ry_deg=-7.5, rz_deg=1.2, opacity=min(1.0, u_cut * 1.25))
                comp_im = optical_soft_transition(comp_im, cut_im, u_cut)

        # ==================================================================
        # 4. COMPOSITE GENUINE HYPERFRAMES FINAL CUT PRO & AFTER EFFECTS ALPHA LAYER!
        # ==================================================================
        comp_im.alpha_composite(bot_scrim, dest=(0, H - scrim_h))

        if fcp_rgba is not None and fcp_rgba[:, :, 3].max() > 0:
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(fcp_rgba, "RGBA"))

        if ov_flare:
            flare_str = 0.0
            for t_fl in (0.48, 30.22, 33.20):
                if abs(t - t_fl) < 0.45:
                    flare_str = max(flare_str, 0.34 * math.cos((t - t_fl) / 0.45 * (math.pi * 0.5)))
            if flare_str > 0.01:
                comp_im = blend_screen_overlay(comp_im, ov_flare[frame_idx % len(ov_flare)], strength=flare_str)

        # ==================================================================
        # 5. UNIFIED BE VIETNAM PRO EXTRABOLD SUBTITLES (100% BOX-SAFE y=1672)
        # ==================================================================
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in  = t - g["t0"]
                dt_out = g["t1"] - t
                u_g_out  = septic_smooth(min(1.0, dt_out / 0.18))
                dy_g_out = -(1.0 - septic_smooth(min(1.0, dt_out / 0.24))) * 12.0
                sc_g_out = 0.94 + 0.06 * septic_smooth(min(1.0, dt_out / 0.24))
                sig_out  = (1.0 - u_g_out) * 1.1

                min_x, max_x, x_center = 44.0, 1036.0, 540.0
                cap_sz_base = 52.0
                y_base = 1672.0 if len(g["lines"]) >= 2 else 1706.0
                lh = 66.0
                max_w_ok = max_x - min_x
                gap = 18.0
                sheen_sub = -0.25 + 1.50 * (((t - g["t0"]) % 2.2) / 1.6)

                for li, ln in enumerate(g["lines"]):
                    raw_ln  = clamp01(max(0.0, dt_in - li * 0.04) / 0.22)
                    raw_op  = clamp01(max(0.0, dt_in - li * 0.04) / 0.14)
                    u_ln_in = ease_out_back_soft(raw_ln, overshoot=1.07)
                    op_ln   = quintic_smooth(raw_op) * u_g_out
                    if op_ln <= 0.008:
                        continue
                    dy_ln  = (1.0 - u_ln_in) * 16.0 + dy_g_out
                    sig_ln = (1.0 - quintic_smooth(raw_op)) * 1.1 + sig_out
                    sc_ln  = (0.93 + 0.07 * u_ln_in) * sc_g_out

                    word_renders, total_w = [], 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        if ws - 0.04 <= t <= we + 0.22:
                            u_wp = clamp01((t - (ws - 0.04)) / 0.14)
                            act_pulse = 1.0 + 0.095 * math.sin(min(1.0, u_wp) * (math.pi * 0.65))
                            is_active = True
                        else:
                            act_pulse = 1.0
                            is_active = False

                        if wtxt in ROSE_W:
                            pal, st_mode = "rose_satin", "dark_bevel"
                        elif wtxt in CORAL_W:
                            pal, st_mode = "coral", "dark_bevel"
                        elif wtxt in EMERALD_W:
                            pal, st_mode = "emerald", "dark_bevel"
                        elif wtxt in SAPPHIRE_W:
                            pal, st_mode = "sapphire", "dark_bevel"
                        else:
                            pal, st_mode = ("gold" if is_active else "pearl"), "dark_bevel"

                        sp_tup = render_luxury_grad_text(
                            wtxt, FONT_SUB_UNIFIED, cap_sz_base, palette=pal, style=st_mode, stroke_w=7, shadow_alpha=125
                        )
                        sp_im = apply_sheen_sweep(sp_tup, sheen_sub) if pal != "pearl" else sp_tup[0]
                        adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_SUB_UNIFIED, cap_sz_base)) + 6.0
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

        bar_bot = Image.new("RGBA", (W, 40), (10, 12, 22, 188))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 40))
        paste_3d_smooth(comp_im, legal_sp, 540.0, H - 20.0, scale=1.0, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"tokyo_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 200 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/1134 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close(); writer.wait()
    reader_a.close()
    reader_m.stdout.close(); reader_m.wait()
    reader_fcp.close()

    if test_mode and test_saved:
        imgs_t = [Image.open(p).resize((300, 533), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (300 * 5, 533 * 2))
        for i, im in enumerate(imgs_t[:10]):
            grid.paste(im, ((i % 5) * 300, (i // 5) * 533))
        gp = os.path.join(CHECK_DIR, "tokyo_master_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved 10-panel tokyo_master_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM Tokyo Master video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
