import json, math, os, re, subprocess, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter1d
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR   = r"d:\AI\full studio\output\htpm2-flow"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
OV4K_DIR   = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k"
FONTS_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FCP_MOV    = os.path.join(PROJ_DIR, "fcp_ae_overlays.mov")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
TOTAL_FRAMES = 3073  # 102.45s

FONT_SUB_MAIN  = os.path.join(FONTS_DIR, "AsapCondensed-Bold.ttf")
FONT_CARD_LBL  = os.path.join(FONTS_DIR, "AsapCondensed-ExtraBold.ttf")
FONT_HERO_SANS = os.path.join(FONTS_DIR, "AsapCondensed-Black.ttf")
FONT_LEGAL     = os.path.join(FONTS_DIR, "AsapCondensed-SemiBold.ttf")

GRAD_PALETTES = {
    "gold": [
        (0.00, (255, 254, 245)),
        (0.28, (255, 232, 146)),
        (0.55, (234, 174,  58)),
        (0.80, (255, 242, 184)),
        (1.00, (198, 132,  28)),
    ],
    "rose_satin": [
        (0.00, (255, 244, 250)),
        (0.28, (255, 152, 206)),
        (0.55, (238,  68, 148)),
        (0.80, (255, 192, 226)),
        (1.00, (188,  34, 108)),
    ],
    "emerald": [
        (0.00, (244, 255, 250)),
        (0.28, (132, 246, 206)),
        (0.55, ( 38, 196, 142)),
        (0.80, (186, 252, 230)),
        (1.00, ( 22, 142,  98)),
    ],
    "sapphire": [
        (0.00, (244, 252, 255)),
        (0.28, (144, 228, 255)),
        (0.55, ( 52, 162, 252)),
        (0.80, (194, 240, 255)),
        (1.00, ( 28, 112, 204)),
    ],
    "coral": [
        (0.00, (255, 248, 240)),
        (0.28, (255, 184, 126)),
        (0.55, (248, 102,  66)),
        (0.80, (255, 214, 180)),
        (1.00, (194,  56,  28)),
    ],
    "pearl": [
        (0.00, (255, 255, 255)),
        (0.50, (248, 251, 255)),
        (1.00, (238, 244, 252)),
    ],
}

BADGE_THEMES = {
    "sapphire": ((236, 244, 255, 255), ( 24,  88, 212, 255), (132, 216, 255)),
    "gold":     ((255, 248, 226, 255), (168,  98,  12, 255), (252, 220, 122)),
    "emerald":  ((232, 252, 244, 255), ( 14, 124,  84, 255), (118, 242, 198)),
    "coral":    ((255, 238, 230, 255), (192,  58,  24, 255), (255, 168, 112)),
    "rose":     ((255, 238, 246, 255), (186,  28, 102, 255), (255, 146, 202)),
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

def ease_out_back_soft(u, overshoot=1.07):
    u = clamp01(u) - 1.0
    return 1.0 + u * u * ((overshoot + 1.0) * u + overshoot)

def ae_in_out(t, st, en, d_in=0.28, d_out=0.22, overshoot=1.06):
    """
    Bidirectional Optical Blur-Focus + Drop-Bounce (~6% overshoot):
    In (0.28s): blur(5.2 -> 0) + scale(0.92 -> 1.06 -> 1.00)
    Out (0.22s): blur(0 -> 4.6) + opacity(1.0 -> 0.0) — zero abrupt pop-off!
    """
    if t <= st or t >= en:
        return 0.0, 0.0, 0.0, 0.0
    raw_in  = clamp01((t - st) / max(0.06, d_in))
    raw_out = clamp01((en - t) / max(0.06, d_out))
    u_in    = ease_out_back_soft(raw_in, overshoot=overshoot)
    u_out   = septic_smooth(raw_out)
    op      = min(quintic_smooth(min(1.0, raw_in * 1.45)), u_out)
    sigma   = (1.0 - quintic_smooth(raw_in)) * 5.2 + (1.0 - u_out) * 4.6
    return u_in, u_out, op, sigma


def draw_landing_ripple_ring(canvas_im, cx, y_foot, t, t_land, rim_rgb=(255, 146, 202), max_rx=430.0, max_ry=42.0):
    dt = t - t_land
    if dt < 0.0 or dt > 0.30:
        return
    u = clamp01(dt / 0.28)
    op = (1.0 - quintic_smooth(u)) * 0.86
    if op <= 0.02:
        return
    rx = max_rx * (0.24 + 1.08 * quintic_smooth(u))
    ry = max_ry * (0.24 + 0.76 * quintic_smooth(u))
    rw, rh = int(rx * 2 + 24), int(ry * 2 + 24)
    rim = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
    d = ImageDraw.Draw(rim)
    al = int(round(255.0 * op))
    d.ellipse([12, 12, rw - 13, rh - 13], outline=(*rim_rgb, al), width=3)
    rim = rim.filter(ImageFilter.GaussianBlur(radius=1.2))
    dx, dy = int(round(cx - rw * 0.5)), int(round(y_foot - rh * 0.5))
    x0, y0 = max(0, dx), max(0, dy)
    x1, y1 = min(canvas_im.width, dx + rw), min(canvas_im.height, dy + rh)
    if x1 > x0 and y1 > y0:
        canvas_im.alpha_composite(rim.crop((x0 - dx, y0 - dy, x1 - dx, y1 - dy)), dest=(x0, y0))


def draw_thread_line_lead(canvas_im, t, t_shift, y_line=448.0, color_rgb=(255, 146, 202)):
    dt = t - (t_shift - 0.15)
    if dt < 0.0 or dt > 0.38:
        return
    u_head = quintic_smooth(clamp01(dt / 0.22))
    u_tail = quintic_smooth(clamp01((dt - 0.12) / 0.24))
    x_start = 860.0 - 640.0 * u_head
    x_end   = 860.0 - 640.0 * u_tail
    if x_end - x_start < 8.0:
        return
    op = (1.0 - clamp01((dt - 0.24) / 0.14)) * 0.90
    bar = Image.new("RGBA", (W, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(bar)
    d.line([(x_start, 18), (x_end, 18)], fill=(*color_rgb, int(255 * op)), width=5)
    d.ellipse([x_start - 7, 11, x_start + 7, 25], fill=(255, 255, 255, int(255 * op)))
    bar = bar.filter(ImageFilter.GaussianBlur(radius=1.4))
    canvas_im.alpha_composite(bar, dest=(0, int(round(y_line - 18))))

# ======================================================================
# 1. PURPOSEFUL CAMERA KEYFRAME RIG (HTPM2: Lão Hóa Sớm — 102.45s)
#    0% jitter, smooth septic zoom in/out synced to emphasis sentences!
# ======================================================================
CAM_KEYFRAMES = [
    (  0.00, 1.000, 0.000,  0.000, 0.35),
    (  0.10, 1.102, 0.000, -0.016, 0.52),  # Hook punch-in: "Dấu hiệu lão hóa sớm!"
    (  1.88, 1.046, 0.000, -0.007, 0.58),  # Question reframe: "Lão hóa da là phải ngoài 35 hay 40 tuổi mới lo?"
    (  5.78, 1.000, 0.000,  0.000, 0.56),  # Pull out wide for Age 25 Mirror Cinema Window (6.12 - 13.15s)
    ( 13.24, 1.096, 0.000, -0.015, 0.58),  # Emphasis push-in under 25+ Collagen Decline Curve (13.26 - 18.25s)
    ( 18.25, 1.000, 0.000,  0.000, 0.56),  # Pull out wide for 3D Collagen Fiber Window (18.35 - 22.98s)
    ( 23.06, 1.058, 0.000, -0.009, 0.55),  # Mid push-in under 4-Habit Frosted Pearl Bento (23.10 - 27.32s)
    ( 27.36, 1.000, 0.000,  0.000, 0.54),  # Wide for Late-Night Stress Cinema Window (27.45 - 32.10s)
    ( 32.12, 1.115, 0.000, -0.018, 0.52),  # Strong emphasis punch-in: "Thì quá trình lão hóa sẽ đến nhanh hơn rất là nhiều!"
    ( 34.92, 1.000, 0.000,  0.000, 0.58),  # Pull out wide for 4-Card 3D Playing-Card Deck (35.20 - 65.78s)
    ( 65.88, 1.112, 0.000, -0.017, 0.58),  # Empowering punch-in: "Phát hiện sớm & chăm sóc đúng cách -> làm chậm lại!"
    ( 72.70, 1.052, 0.000, -0.008, 0.60),  # Mid reframe: "Mục tiêu của việc chăm sóc da không phải là chống già..."
    ( 77.38, 1.000, 0.000,  0.000, 0.50),  # Cutaway transition (77.42 - 87.65s)
    ( 87.72, 1.102, 0.000, -0.016, 0.62),  # Finale punch-in: "Và lão hóa là điều không ai tránh được, nhưng hoàn toàn làm chậm nó!"
]

def eval_camera_rig(t):
    z_cur, px_cur, py_cur = CAM_KEYFRAMES[0][1], CAM_KEYFRAMES[0][2], CAM_KEYFRAMES[0][3]
    for i in range(1, len(CAM_KEYFRAMES)):
        tk, zk, pxk, pyk, dur_k = CAM_KEYFRAMES[i]
        if t >= tk:
            u = septic_smooth(clamp01((t - tk) / max(0.20, dur_k)))
            z_cur  += (zk  - z_cur)  * u
            px_cur += (pxk - px_cur) * u
            py_cur += (pyk - py_cur) * u
    return z_cur, px_cur, py_cur

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

def blend_screen_overlay(rgba_im, ov_rgb, strength=0.24):
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

_thin_text_cache = {}
def render_clean_grad_text(text, font_path, size, palette="pearl", stroke_w=2, shadow_alpha=135):
    eff_sw = max(0, min(stroke_w, 3))
    key = (text, font_path, int(round(size)), palette, eff_sw, shadow_alpha)
    if key in _thin_text_cache:
        return _thin_text_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=eff_sw)
    tw, th = max(4, bbox[2] - bbox[0]), max(4, bbox[3] - bbox[1])
    pad = 20
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    stops = GRAD_PALETTES.get(palette, GRAD_PALETTES["pearl"])

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 1, oy + 4), text, font=font, fill=255, stroke_width=eff_sw + 1, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=6.0)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (8, 10, 18)
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    if eff_sw > 0:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(14, 16, 26, 228), stroke_width=eff_sw, stroke_fill=(14, 16, 26, 228))
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

    if len(_thin_text_cache) > 1400:
        _thin_text_cache.clear()
    _thin_text_cache[key] = (base, arr_m)
    return base, arr_m

def apply_sheen_sweep(sprite_tuple, sheen_phase):
    base, arr_m = sprite_tuple
    if sheen_phase < -0.25 or sheen_phase > 1.25:
        return base
    ch, cw = arr_m.shape
    yy, xx = np.ogrid[0:ch, 0:cw]
    diag = (xx.astype(np.float32) * 0.90 + yy.astype(np.float32) * 0.42) / max(1.0, cw * 0.90 + ch * 0.42)
    band = np.exp(-((diag - sheen_phase) ** 2) / 0.0055) * 82.0 * arr_m
    if band.max() < 2.5:
        return base
    out = np.array(base, dtype=np.float32)
    out[:, :, 0] = np.clip(out[:, :, 0] + band, 0, 255)
    out[:, :, 1] = np.clip(out[:, :, 1] + band * 0.98, 0, 255)
    out[:, :, 2] = np.clip(out[:, :, 2] + band * 0.94, 0, 255)
    return Image.fromarray(out.astype(np.uint8), "RGBA")

_pearl_pill_cache = {}
def make_frosted_pearl_pill(tag_txt, main_txt, theme="rose", max_w=780):
    k = (tag_txt, main_txt, theme, max_w)
    if k in _pearl_pill_cache:
        return _pearl_pill_cache[k]
    bg_tag, fg_tag, _ = BADGE_THEMES.get(theme, BADGE_THEMES["rose"])
    f_tag  = get_font(FONT_CARD_LBL, 20)
    f_main = get_font(FONT_CARD_LBL, 26)
    dm = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tb_t = dm.textbbox((0, 0), tag_txt, font=f_tag) if tag_txt else (0, 0, 0, 0)
    tb_m = dm.textbbox((0, 0), main_txt, font=f_main)
    wt = (tb_t[2] - tb_t[0] + 28) if tag_txt else 0
    wm = tb_m[2] - tb_m[0]
    pw = min(max_w, wt + wm + (48 if tag_txt else 40))
    ph = 56
    pad = 10
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 5, pad + pw, pad + ph + 5], radius=28, fill=(12, 18, 38, 92))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=28, fill=(252, 253, 255, 246), outline=(255, 255, 255, 255), width=2)
    cur_x = pad + 16
    if tag_txt:
        d.rounded_rectangle([cur_x, pad + 10, cur_x + wt, pad + ph - 10], radius=18, fill=bg_tag)
        d.text((cur_x + 14 - tb_t[0], pad + 28 - (tb_t[1] + tb_t[3]) * 0.5), tag_txt, font=f_tag, fill=fg_tag)
        cur_x += wt + 14
    d.text((cur_x - tb_m[0], pad + 28 - (tb_m[1] + tb_m[3]) * 0.5), main_txt, font=f_main, fill=(22, 24, 34, 255))
    _pearl_pill_cache[k] = im
    return im

def make_diagonal_split_rgb(vf_l, vf_r, pw, ph, u_l=1.0, u_r=1.0):
    im_l = fit_cover_subpixel(vf_l, pw, ph, zoom=1.05, pan_x=+0.10 + (1.0 - u_l) * 0.05)
    im_r = fit_cover_subpixel(vf_r, pw, ph, zoom=1.05, pan_x=-0.10 - (1.0 - u_r) * 0.05)
    yy, xx = np.ogrid[0:ph, 0:pw]
    diag = (xx.astype(np.float32) - pw * 0.50) + (yy.astype(np.float32) - ph * 0.50) * 0.22
    w_r = np.clip((diag + 16.0) / 32.0, 0.0, 1.0)[:, :, None]
    return (np.array(im_l, dtype=np.float32) * (1.0 - w_r) + np.array(im_r, dtype=np.float32) * w_r).astype(np.uint8)

def render_large_cinema_window(canvas_im, vf_l, vf_r, t, st, en, tag_l, lbl_l, tag_r="", lbl_r="", theme_l="rose", theme_r="gold", cy=446.0, ph=596):
    ui, uo, op, sig = ae_in_out(t, st, en, d_in=0.46, d_out=0.38, overshoot=1.07)
    if op <= 0.008:
        return
    pw, pad = 1016, 22
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 14, pad + pw, pad + ph + 14], radius=42, fill=(10, 14, 28, 138))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    if vf_r is not None:
        u_l = septic_smooth(clamp01((t - st) / 0.48))
        u_r = septic_smooth(clamp01((t - st - 0.12) / 0.48))
        vis_im = Image.fromarray(make_diagonal_split_rgb(vf_l, vf_r, pw, ph, u_l, u_r), "RGB")
    else:
        u_z = septic_smooth(clamp01((t - st) / max(0.8, en - st)))
        vis_im = fit_cover_subpixel(vf_l, pw, ph, zoom=1.02 + 0.05 * u_z)

    rmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=42, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(vis_im, (pad, pad), mask=rmask)
    card = Image.alpha_composite(card, vl)

    _, _, rim_rgb = BADGE_THEMES.get(theme_l, BADGE_THEMES["rose"])
    d = ImageDraw.Draw(card)
    if vf_r is not None:
        x_top = pad + pw * 0.50 - (-ph * 0.50) * 0.22
        x_bot = pad + pw * 0.50 - (+ph * 0.50) * 0.22
        d.line([(x_top, pad + 4), (x_bot, pad + ph - 4)], fill=(255, 255, 255, 245), width=4)
        p1 = make_frosted_pearl_pill(tag_l, lbl_l, theme=theme_l, max_w=465)
        p2 = make_frosted_pearl_pill(tag_r, lbl_r, theme=theme_r, max_w=465)
        card.alpha_composite(p1, dest=(pad + 18, pad + 14))
        card.alpha_composite(p2, dest=(pad + pw - p2.width - 18, pad + ph - p2.height - 14))
    else:
        p1 = make_frosted_pearl_pill(tag_l, lbl_l, theme=theme_l, max_w=760)
        card.alpha_composite(p1, dest=(pad + 20, pad + 16))

    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=42, outline=(255, 255, 255, 248), width=4)
    d.rounded_rectangle([pad + 5, pad + 5, pad + pw - 6, pad + ph - 6], radius=37, outline=(*rim_rgb, 185), width=2)
    draw_landing_ripple_ring(canvas_im, 540.0, cy + ph * 0.49, t, st + 0.25, rim_rgb=rim_rgb)
    paste_3d_smooth(
        canvas_im, card,
        540.0, cy + (1.0 - ui) * (-72.0) - (1.0 - uo) * 18.0,
        scale=(0.92 + 0.08 * ui) * (0.94 + 0.06 * uo),
        rx_deg=(1.0 - ui) * 6.5, opacity=op, dof_sigma=sig
    )

_card_shell_cache = {}
def build_large_playing_card(vf_rgb, w, h, idx_str, title_str, theme="rose", zoom=1.02, pan_y=0.0):
    k = (w, h, idx_str, title_str, theme)
    if k not in _card_shell_cache:
        _, _, rim_rgb = BADGE_THEMES.get(theme, BADGE_THEMES["rose"])
        pad = 24
        cw, ch = w + pad * 2, h + pad * 2
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius=38, fill=(10, 12, 24, 136))
        sh = sh.filter(ImageFilter.GaussianBlur(radius=14))
        rmask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, w - 1, h - 1], radius=38, fill=255)

        overlay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        pill = make_frosted_pearl_pill(idx_str, title_str, theme=theme, max_w=w - 36)
        overlay.alpha_composite(pill, dest=(pad + 18, pad + 12))
        d = ImageDraw.Draw(overlay)
        d.rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius=38, outline=(255, 255, 255, 248), width=4)
        d.rounded_rectangle([pad + 5, pad + 5, pad + w - 6, pad + h - 6], radius=33, outline=(*rim_rgb, 195), width=2)
        _card_shell_cache[k] = (sh, rmask, overlay, pad)

    sh, rmask, overlay, pad = _card_shell_cache[k]
    card = sh.copy()
    vlay = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    eff_pan_y = pan_y if abs(pan_y) > 1e-4 else (-0.21 if vf_rgb.shape[0] > vf_rgb.shape[1] else 0.0)
    vlay.paste(fit_cover_subpixel(vf_rgb, w, h, zoom=zoom, pan_y=eff_pan_y), (pad, pad), mask=rmask)
    return Image.alpha_composite(Image.alpha_composite(card, vlay), overlay)

def render_3d_playing_card_deck(canvas_im, card_sprites, t, st, en, focus_schedule, fan_hold_until=None, cy_base=448.0):
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

    w_car = septic_smooth(clamp01((t - fan_hold_until) / 0.56)) if fan_hold_until is not None else 1.0
    cur_val, vel = float(focus_schedule[0][1]), 0.0
    for idx in range(1, len(focus_schedule)):
        ts, targ = focus_schedule[idx]
        prev_t = focus_schedule[idx - 1][1]
        if t >= ts:
            u = clamp01((t - ts) / 0.56)
            sm = septic_smooth(u)
            if 0.001 < u < 0.999:
                vel = (float(targ) - float(prev_t)) * 140.0 * (u ** 3) * ((1.0 - u) ** 3) / 0.56
            cur_val = float(prev_t) + (float(targ) - float(prev_t)) * sm

    mid_k = (K - 1) * 0.5
    fan_step = 215.0 if K >= 4 else 258.0
    draw_queue = []
    for i in range(K):
        s_fan = i - mid_k
        fx = 540.0 + s_fan * fan_step * u_in
        fy = cy_base + 8.0 + abs(s_fan) * 26.0 + (1.0 - u_in) * 68.0
        f_sc = (0.58 if K >= 4 else 0.64) * (0.82 + 0.18 * u_in)
        f_ry, f_rz, f_rx = -s_fan * 12.0 * u_in, s_fan * 7.5 * u_in, (1.0 - u_in) * 9.0
        f_z = 10.0 - abs(s_fan) * 6.0

        rel = float(i) - cur_val
        abs_r = abs(rel)
        swap_arc = math.sin(clamp01(abs_r) * math.pi) if abs_r < 1.0 else 0.0
        cx_car = 540.0 + rel * 245.0 + (-36.0 if rel < 0 else 36.0) * swap_arc * 0.45
        cy_car = cy_base - 6.0 + min(2.2, abs_r) * 28.0 - swap_arc * 12.0
        sc_car = 0.98 - min(1.0, abs_r) * 0.24 - max(0.0, abs_r - 1.0) * 0.05
        ry_car = -max(-22.0, min(22.0, rel * 15.0))
        rz_car = max(-10.0, min(10.0, rel * 6.0))
        rx_car = -1.0 * (1.0 - min(1.0, abs_r))
        dim_car = 1.00 - min(1.0, abs_r) * 0.25
        dof_car = min(1.0, abs_r) * 1.8
        z_car   = 100.0 * math.cos(min(1.5, abs_r)) - abs_r * 25.0

        px = (fx * (1.0 - w_car) + cx_car * w_car) * u_out + 540.0 * (1.0 - u_out)
        py = (fy * (1.0 - w_car) + cy_car * w_car) - (1.0 - u_out) * 34.0
        psc = (f_sc * (1.0 - w_car) + sc_car * w_car) * (0.88 + 0.12 * u_out)
        pry = (f_ry * (1.0 - w_car) + ry_car * w_car) * u_out
        prz = (f_rz * (1.0 - w_car) + rz_car * w_car) * u_out
        prx = (f_rx * (1.0 - w_car) + rx_car * w_car) + (1.0 - u_out) * 8.0
        pdim = 0.98 * (1.0 - w_car) + dim_car * w_car
        pdof = dof_car * w_car + (1.0 - quintic_smooth(raw_in)) * 2.6 + (1.0 - u_out) * 2.6
        pz   = f_z * (1.0 - w_car) + z_car * w_car
        mb_x = -vel * 220.0 * w_car / FPS
        draw_queue.append((pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x))

    draw_landing_ripple_ring(canvas_im, 540.0, cy_base + 292.0, t, st + 0.34, rim_rgb=(255, 146, 202))
    for idx_s in range(1, len(focus_schedule)):
        draw_thread_line_lead(canvas_im, t, focus_schedule[idx_s][0], y_line=cy_base)
    draw_queue.sort(key=lambda x: x[0])
    for pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x in draw_queue:
        paste_3d_smooth(canvas_im, card_sprites[i], px, py, scale=psc, rx_deg=prx, ry_deg=pry, rz_deg=prz, opacity=op_deck, dof_sigma=pdof, mb_dx=mb_x, dim=pdim)

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

def make_iris_circle_pip(fg_rgb, diam=288, iris_prog=1.0):
    sub = fg_rgb[560:1420, 220:880]
    im = fit_cover_subpixel(sub, diam, diam, zoom=1.04)
    pad = 18
    cw = diam + pad * 2
    card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad, pad + 8, pad + diam, pad + diam + 8], fill=(8, 14, 28, 138))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=10)))
    d = ImageDraw.Draw(card)
    d.ellipse([pad, pad, pad + diam - 1, pad + diam - 1], fill=(238, 214, 236, 245))
    r_iris = max(2.0, (diam * 0.5) * clamp01(iris_prog))
    cx_i = diam * 0.5
    imask = Image.new("L", (diam, diam), 0)
    ImageDraw.Draw(imask).ellipse([cx_i - r_iris, cx_i - r_iris, cx_i + r_iris, cx_i + r_iris], fill=255)
    vl = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    vl.paste(im, (pad, pad), mask=imask)
    card = Image.alpha_composite(card, vl)
    d = ImageDraw.Draw(card)
    d.ellipse([pad, pad, pad + diam - 1, pad + diam - 1], outline=(255, 255, 255, 250), width=5)
    d.ellipse([pad + 5, pad + 5, pad + diam - 6, pad + diam - 6], outline=(255, 146, 202, 220), width=2)
    return card

def cap_first_char(s):
    return (s[0].upper() + s[1:]) if s else s

def load_captions_clean():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and (w["start"] + w["end"]) * 0.5 >= 6.02
    ]

    CLAUSE_STARTERS = {
        "nhưng", "thực", "từ", "nếu", "thì", "có", "đó", "khi", "tiếp",
        "dù", "nhiều", "hoặc", "ngoài", "và", "mà", "vậy", "chị"
    }
    COMPOUNDS = {
        ("lão", "hóa"), ("xuống", "cấp"), ("nếp", "nhăn"), ("căng", "bóng"),
        ("quá", "trình"), ("thời", "điểm"), ("sản", "sinh"), ("cơ", "thể"),
        ("sinh", "hoạt"), ("khoa", "học"), ("thức", "khuya"), ("thường", "xuyên"),
        ("căng", "thẳng"), ("tiếp", "xúc"), ("ánh", "nắng"), ("chống", "nắng"),
        ("ăn", "uống"), ("thiếu", "chất"), ("hút", "thuốc"), ("rượu", "bia"),
        ("dấu", "hiệu"), ("nhận", "biết"), ("đầu", "tiên"), ("căng", "mịn"),
        ("cảm", "thấy"), ("xỉn", "màu"), ("sức", "sống"), ("chăm", "sóc"),
        ("chị", "em"), ("chân", "lông"), ("chảy", "xệ"), ("vùng", "má"),
        ("xuất", "hiện"), ("li", "ti"), ("khóe", "mắt"), ("khóe", "miệng"),
        ("vết", "thâm"), ("phục", "hồi"), ("kích", "ứng"), ("nổi", "mụn"),
        ("khả", "năng"), ("tái", "tạo"), ("giảm", "dần"), ("đáng", "mừng"),
        ("phát", "hiện"), ("đúng", "cách"), ("hoàn", "toàn"), ("mục", "tiêu"),
        ("chống", "già"), ("thời", "gian"), ("làn", "da"), ("khỏe", "mạnh"),
        ("duy", "trì"), ("đàn", "hồi"), ("tươi", "tắn"), ("giai", "đoạn"),
        ("cuộc", "sống"), ("bên", "trong"), ("tự", "tin"), ("độ", "tuổi"),
        ("nguyên", "tắc"), ("đơn", "giản"), ("hiệu", "quả"), ("rạng", "rỡ"),
    }

    phrases, cur_p = [], []
    for w in words:
        txt, ws, we = w
        wlow = txt.lower().rstrip(",.?!:;")
        if cur_p:
            gap = ws - cur_p[-1][2]
            prev_txt = cur_p[-1][0]
            dur_so_far = cur_p[-1][2] - cur_p[0][1]
            prev_low = prev_txt.lower().rstrip(",.?!:;")
            if (prev_low, wlow) not in COMPOUNDS:
                if re.search(r"[.?!…;:]$", prev_txt) or gap >= 0.40:
                    phrases.append(cur_p); cur_p = []
                elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 3 or dur_so_far >= 1.15):
                    phrases.append(cur_p); cur_p = []
                elif wlow in CLAUSE_STARTERS and len(cur_p) >= 5:
                    phrases.append(cur_p); cur_p = []
                elif len(cur_p) >= 9 and prev_low not in {"rất", "một", "những", "các", "đang", "sẽ", "vẫn", "không"}:
                    phrases.append(cur_p); cur_p = []
        cur_p.append(w)
    if cur_p:
        phrases.append(cur_p)

    merged = []
    for p in phrases:
        if (
            merged and len(p) <= 2
            and not re.search(r"[.?!…:]$", merged[-1][-1][0])
            and (p[0][1] - merged[-1][-1][2]) < 0.35
            and len(merged[-1]) + len(p) <= 8
        ):
            merged[-1].extend(p)
        else:
            merged.append(p)

    PROPER_NOUNS = {"Hằng", "Thu", "Collagen", "Elastin", "UV"}
    for p in merged:
        if p:
            p[0][0] = cap_first_char(p[0][0])
            for k in range(1, len(p)):
                if re.search(r"[.?!:]$", p[k - 1][0]):
                    p[k][0] = cap_first_char(p[k][0])
                elif p[k][0].rstrip(",.?!:;") not in PROPER_NOUNS and p[k][0][:1].isupper():
                    p[k][0] = p[k][0][0].lower() + p[k][0][1:]

    def split_balanced(p):
        tot_c = sum(len(x[0]) + 1 for x in p) - 1
        if len(p) <= 5 and tot_c <= 25:
            return [p]
        bk, bd = max(1, len(p) // 2), 9999
        for k in range(1, len(p)):
            c1 = sum(len(x[0]) + 1 for x in p[:k]) - 1
            c2 = sum(len(x[0]) + 1 for x in p[k:]) - 1
            d = abs(c1 - c2) + (6 if max(c1, c2) > 26 else 0)
            if d < bd:
                bd, bk = d, k
        return [p[:bk], p[bk:]]

    ROSE_W    = {"collagen", "elastin", "căng", "bóng", "mịn", "tươi", "tắn", "rạng", "rỡ"}
    CORAL_W   = {"lão", "hóa", "xuống", "cấp,", "nhăn,", "nhăn", "khô", "sần", "xỉn", "chảy", "xệ", "thâm", "mụn"}
    EMERALD_W = {"khỏe", "mạnh,", "đàn", "hồi,", "tự", "tin", "chậm", "lại.", "hiệu", "quả"}

    cap_groups = []
    for i, p in enumerate(merged):
        t0 = max(6.05, p[0][1] - 0.04)
        last_end = p[-1][2]
        nxt_s = merged[i + 1][0][1] if i + 1 < len(merged) else 102.30
        t1 = (nxt_s - 0.05) if (nxt_s - last_end <= 0.95) else min(nxt_s - 0.06, max(last_end + 0.65, t0 + 1.55))
        cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced(p)})
    return cap_groups, ROSE_W, CORAL_W, EMERALD_W

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

def get_clip_frame_smooth(clips, key, t_rel, target_span=4.5):
    arr_list = clips.get(key)
    if not arr_list:
        return np.full((640, 1024, 3), 235, dtype=np.uint8)
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

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [2.80, 9.20, 15.60, 20.50, 25.00, 29.80, 38.50, 58.50, 70.00, 82.00]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    if not os.path.exists(aroll_path):
        aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vid_keys = [
        ("lh_01_mirror_age25",        1152, 648),
        ("lh_02_dry_skin_cream",       720, 1280),
        ("lh_03_fine_lines_dull",      720, 1280),
        ("lh_04_collagen_renewal_3d", 1152, 648),
        ("lh_05_late_night_stress",   1152, 648),
        ("lh_06_healthy_glow_habits", 1152, 648),
    ]
    clips = {}
    for ck, vw, vh in vid_keys:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if os.path.exists(vp):
            clips[ck] = load_vid_frames_wh(vp, vw, vh)
            print(f"[HTPM2] Loaded {ck}: {len(clips[ck])} frames")
        else:
            raise FileNotFoundError(f"Missing referenced Flow clip: {vp}")

    ov_bokeh   = load_vid_frames_wh(os.path.join(OV4K_DIR, "01_Golden_Dust_Bokeh_9x16.mp4"), W, H) if os.path.exists(os.path.join(OV4K_DIR, "01_Golden_Dust_Bokeh_9x16.mp4")) else []
    ov_flare   = load_vid_frames_wh(os.path.join(OV4K_DIR, "04_Anamorphic_Gold_Rose_Flare_9x16.mp4"), W, H) if os.path.exists(os.path.join(OV4K_DIR, "04_Anamorphic_Gold_Rose_Flare_9x16.mp4")) else []
    ov_sparkle = load_vid_frames_wh(os.path.join(OV4K_DIR, "05_Soft_Pearl_Sparkles_Bling_9x16.mp4"), W, H) if os.path.exists(os.path.join(OV4K_DIR, "05_Soft_Pearl_Sparkles_Bling_9x16.mp4")) else []

    cap_groups, ROSE_W, CORAL_W, EMERALD_W = load_captions_clean()

    scrim_h = 370
    sy = np.linspace(0.0, 1.0, scrim_h, dtype=np.float32)[:, None]
    sa = np.zeros((scrim_h, W, 4), dtype=np.uint8)
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (10, 12, 20)
    sa[:, :, 3] = (np.power(sy, 1.35) * 168.0).astype(np.uint8)
    bot_scrim = Image.fromarray(sa, "RGBA")

    legal_sp, _ = render_clean_grad_text(
        "Chia sẻ bí quyết chăm sóc & bảo vệ làn da khoa học cùng Dược sĩ Hằng Thu Pharma",
        FONT_LEGAL, 18, palette="pearl", stroke_w=1, shadow_alpha=60
    )

    reader_a   = VideoReader(aroll_path)
    reader_m   = subprocess.Popen(["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    reader_fcp = RgbaVideoReader(FCP_MOV)

    raw_vid_out = os.path.join(PROJ_DIR, "_master_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    yy_g = np.arange(H, dtype=np.float32)[:, None]
    lower_desk_guard = np.clip((yy_g - 1480.0) / 70.0, 0.0, 1.0)

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

        z_cam, px_cam, py_cam = eval_camera_rig(t)
        if abs(z_cam - 1.0) < 1e-4 and abs(px_cam) < 1e-4 and abs(py_cam) < 1e-4:
            fg_rgb = rgb_raw
            m_arr  = matte_raw.astype(np.float32) / 255.0
        else:
            fg_im = fit_cover_subpixel(rgb_raw, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam)
            m_rgb = np.repeat(matte_raw[:, :, None], 3, axis=2)
            m_im  = fit_cover_subpixel(m_rgb, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam).convert("L")
            fg_rgb = np.array(fg_im)
            m_arr  = np.array(m_im, dtype=np.float32) / 255.0

        base_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

        if ov_bokeh and ((13.2 <= t <= 18.3) or (65.9 <= t <= 77.4) or (87.7 <= t <= 102.4)):
            base_im = blend_screen_overlay(base_im, ov_bokeh[frame_idx % len(ov_bokeh)], strength=0.20)

        # 1. BEHIND-SPEAKER INGREDIENTS-REFERENCED FLOW WINDOWS & 3D PLAYING-CARD DECK
        if 6.15 <= t < 13.12:
            vf = get_clip_frame_smooth(clips, "lh_01_mirror_age25", t - 6.15, target_span=6.97)
            render_large_cinema_window(base_im, vf, None, t, 6.18, 13.10, "TUỔI 25+", "NẾP NHĂN SỚM & DA KÉM CĂNG BÓNG HƠN TRƯỚC", theme_l="rose", cy=446.0)

        if 18.35 <= t < 22.98:
            vf = get_clip_frame_smooth(clips, "lh_04_collagen_renewal_3d", t - 18.35, target_span=4.63)
            render_large_cinema_window(base_im, vf, None, t, 18.38, 22.96, "SINH HỌC DA", "MẠNG LƯỚI COLLAGEN & ELASTIN GIẢM DẦN MỖI NĂM", theme_l="gold", cy=446.0)

        if 27.45 <= t < 32.12:
            vf_raw = get_clip_frame_smooth(clips, "lh_05_late_night_stress", t - 27.45, target_span=4.67)
            vf = np.array(fit_cover_subpixel(vf_raw, 1152, 648, zoom=1.10, pan_x=-0.03, pan_y=-0.03))
            render_large_cinema_window(base_im, vf, None, t, 27.48, 32.10, "THÓI QUEN XẤU", "THỨC KHUYA • CĂNG THẲNG • THIẾU CHỐNG NẮNG", theme_l="coral", cy=462.0, ph=568)

        if 35.15 <= t < 65.76:
            f_c1 = get_clip_frame_smooth(clips, "lh_02_dry_skin_cream",  max(0.0, t - 35.15) % 4.6, target_span=4.6)
            f_c2 = get_clip_frame_smooth(clips, "lh_03_fine_lines_dull", max(0.0, t - 42.60) % 4.6, target_span=4.6)
            f_c3 = make_diagonal_split_rgb(
                np.array(fit_cover_subpixel(get_clip_frame_smooth(clips, "lh_01_mirror_age25",    max(0.0, t - 48.80) % 4.8, target_span=4.8), 864, 576, zoom=1.04)),
                np.array(fit_cover_subpixel(get_clip_frame_smooth(clips, "lh_03_fine_lines_dull", max(0.0, t - 48.80) % 4.6, target_span=4.6), 864, 576, zoom=1.02, pan_y=-0.21)),
                864, 576
            )
            f_c4 = get_clip_frame_smooth(clips, "lh_04_collagen_renewal_3d", max(0.0, t - 55.20) % 4.6, target_span=4.6)
            deck_aging = [
                build_large_playing_card(f_c1, 864, 576, "DẤU HIỆU 01", "DA KÉM CĂNG MỊN, KHÔ & SẦN HƠN TRƯỚC",        theme="rose"),
                build_large_playing_card(f_c2, 864, 576, "DẤU HIỆU 02", "DA XỈN MÀU, KÉM TƯƠI DÙ VẪN CHĂM SÓC ĐỀU",   theme="coral"),
                build_large_playing_card(f_c3, 864, 576, "DẤU HIỆU 03", "LỖ CHÂN LÔNG TO & NẾP NHĂN LI TI KHÓE MẮT",   theme="gold"),
                build_large_playing_card(f_c4, 864, 576, "DẤU HIỆU 04", "THÂM MỤN LÂU MỜ • TỐC ĐỘ TÁI TẠO DA GIẢM DẦN", theme="sapphire"),
            ]
            render_3d_playing_card_deck(
                base_im, deck_aging, t, 35.15, 65.76,
                focus_schedule=[(35.15, 0), (42.76, 1), (49.10, 2), (55.42, 3)],
                fan_hold_until=36.45, cy_base=450.0
            )

        # 2. RE-COMPOSITE PHARMACIST IN FOREGROUND
        fg_alpha = np.maximum(m_arr, lower_desk_guard)
        comp_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 3. HEALTHY ELASTIC SKIN FULL-SCREEN LUXURY CUTAWAY (77.42 - 87.65s)
        if 77.42 <= t <= 87.65:
            u_in_c  = septic_smooth(clamp01((t - 77.42) / 0.46))
            u_out_c = septic_smooth(clamp01((87.65 - t) / 0.46))
            u_cut = min(u_in_c, u_out_c)
            if u_cut > 0.005:
                vf_g = get_clip_frame_smooth(clips, "lh_06_healthy_glow_habits", max(0.0, t - 77.42) % 5.2, target_span=5.2)
                bg_blur = fit_cover_subpixel(vf_g, W, H, zoom=1.18).filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
                cut_im = Image.alpha_composite(bg_blur, Image.new("RGBA", (W, H), (14, 14, 28, 90)))
                ui_p, _, op_p, sig_p = ae_in_out(t, 77.50, 87.55, d_in=0.38, d_out=0.34, overshoot=1.06)
                pcard = build_large_playing_card(vf_g, 1016, 650, "CHĂM ĐÚNG", "NUÔI DƯỠNG DA KHỎE TỪ GỐC • TỰ TIN MỌI ĐỘ TUỔI", theme="emerald", zoom=1.02)
                paste_3d_smooth(cut_im, pcard, 540.0, 722.0 + (1.0 - ui_p) * 22.0, scale=0.93 + 0.07 * ui_p, rx_deg=1.2, opacity=op_p, dof_sigma=sig_p)
                if ov_sparkle:
                    cut_im = blend_screen_overlay(cut_im, ov_sparkle[frame_idx % len(ov_sparkle)], strength=0.24)
                iris_in  = quintic_smooth(clamp01((t - 77.48) / 0.24))
                iris_out = quintic_smooth(clamp01((87.58 - t) / 0.22))
                pip = make_iris_circle_pip(fg_rgb, 288, iris_prog=min(iris_in, iris_out))
                paste_3d_smooth(cut_im, pip, 876.0, 1402.0, scale=0.90 + 0.10 * min(iris_in, iris_out), opacity=min(1.0, u_cut * 1.35))
                comp_im = optical_soft_transition(comp_im, cut_im, u_cut)

        # 4. COMPOSITE HYPERFRAMES FCP/AE ALPHA LAYER
        comp_im.alpha_composite(bot_scrim, dest=(0, H - scrim_h))
        if fcp_rgba is not None and fcp_rgba[:, :, 3].max() > 0:
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(fcp_rgba, "RGBA"))

        if ov_flare:
            flare_str = 0.0
            for t_fl in (0.14, 13.30, 35.18, 65.96, 77.46, 87.76):
                if abs(t - t_fl) < 0.44:
                    flare_str = max(flare_str, 0.28 * math.cos((t - t_fl) / 0.44 * (math.pi * 0.5)))
            if flare_str > 0.01:
                comp_im = blend_screen_overlay(comp_im, ov_flare[frame_idx % len(ov_flare)], strength=flare_str)

        # 5. SENTENCE-CASE + THIN-STROKE ASAP CONDENSED SUBTITLES
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in, dt_out = t - g["t0"], g["t1"] - t
                u_g_out  = septic_smooth(min(1.0, dt_out / 0.18))
                dy_g_out = -(1.0 - septic_smooth(min(1.0, dt_out / 0.24))) * 10.0
                sc_g_out = 0.95 + 0.05 * septic_smooth(min(1.0, dt_out / 0.24))
                sig_out  = (1.0 - u_g_out) * 1.0

                min_x, max_x, x_center = 48.0, 1032.0, 540.0
                cap_sz_base = 52.0
                y_base = 1666.0 if len(g["lines"]) >= 2 else 1700.0
                lh, max_w_ok, gap = 64.0, max_x - min_x, 13.0
                sheen_sub = -0.25 + 1.50 * (((t - g["t0"]) % 2.4) / 1.7)

                for li, ln in enumerate(g["lines"]):
                    raw_ln  = clamp01(max(0.0, dt_in - li * 0.04) / 0.22)
                    raw_op  = clamp01(max(0.0, dt_in - li * 0.04) / 0.14)
                    u_ln_in = ease_out_back_soft(raw_ln, overshoot=1.06)
                    op_ln   = quintic_smooth(raw_op) * u_g_out
                    if op_ln <= 0.008:
                        continue
                    dy_ln  = (1.0 - u_ln_in) * 14.0 + dy_g_out
                    sig_ln = (1.0 - quintic_smooth(raw_op)) * 1.0 + sig_out
                    sc_ln  = (0.94 + 0.06 * u_ln_in) * sc_g_out

                    word_renders, total_w = [], 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        if ws - 0.04 <= t <= we + 0.20:
                            u_wp = clamp01((t - (ws - 0.04)) / 0.14)
                            act_pulse = 1.0 + 0.075 * math.sin(min(1.0, u_wp) * (math.pi * 0.65))
                            is_active = True
                        else:
                            act_pulse, is_active = 1.0, False

                        wlow = wtxt.lower().rstrip(",.?!:;")
                        if wlow in ROSE_W:
                            pal = "rose_satin"
                        elif wlow in CORAL_W:
                            pal = "coral"
                        elif wlow in EMERALD_W:
                            pal = "emerald"
                        else:
                            pal = "gold" if is_active else "pearl"

                        sp_tup = render_clean_grad_text(wtxt, FONT_SUB_MAIN, cap_sz_base, palette=pal, stroke_w=2, shadow_alpha=140)
                        sp_im = apply_sheen_sweep(sp_tup, sheen_sub) if pal != "pearl" else sp_tup[0]
                        adv = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_SUB_MAIN, cap_sz_base)) + 2.0
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

        bar_bot = Image.new("RGBA", (W, 38), (10, 12, 22, 186))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 38))
        paste_3d_smooth(comp_im, legal_sp, 540.0, H - 19.0, scale=1.0, opacity=0.94)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"test_htpm2_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  [HTPM2] Rendered {frame_idx}/{TOTAL_FRAMES} frames ({frame_idx / el:.1f} fps)", flush=True)

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
        gp = os.path.join(CHECK_DIR, "htpm2_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved HTPM2 test grid:", gp)
    else:
        print(f"Done HTPM2 Lao Hoa Som Master video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
