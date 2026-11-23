import json, math, os, re, subprocess, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter1d
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm-ddvs-2"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

FONTS_DIR        = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_SERIF_HERO  = os.path.join(FONTS_DIR, "PlayfairDisplay-ExtraBold.ttf")
FONT_SERIF_BOLD  = os.path.join(FONTS_DIR, "PlayfairDisplay-Bold.ttf")
FONT_SERIF_ITAL  = os.path.join(FONTS_DIR, "PlayfairDisplay-BoldItalic.ttf")
FONT_DISPLAY     = os.path.join(FONTS_DIR, "PaytoneOne-Regular.ttf")
FONT_MONTS_BLK   = os.path.join(FONTS_DIR, "Montserrat-Black.ttf")
FONT_CONDENSED   = os.path.join(FONTS_DIR, "Oswald-Bold.ttf")
FONT_SCRIPT      = os.path.join(FONTS_DIR, "DancingScript-Bold.ttf")
FONT_SUB_MAIN    = os.path.join(FONTS_DIR, "PlusJakartaSans-ExtraBold.ttf")
FONT_SUB_BOLD    = os.path.join(FONTS_DIR, "PlusJakartaSans-Bold.ttf")
FONT_BE_MED      = os.path.join(FONTS_DIR, "BeVietnamPro-Medium.ttf")

GRAD_PALETTES = {
    "gold": [
        (0.00, (255, 253, 240)),
        (0.25, (252, 224, 126)),
        (0.52, (214, 145,  38)),
        (0.76, (255, 236, 170)),
        (1.00, (152,  92,  12)),
    ],
    "rose_satin": [
        (0.00, (255, 236, 246)),
        (0.25, (252, 122, 188)),
        (0.52, (206,  24, 114)),
        (0.76, (255, 172, 218)),
        (1.00, (132,  10,  72)),
    ],
    "emerald": [
        (0.00, (236, 255, 248)),
        (0.25, ( 96, 230, 184)),
        (0.52, ( 14, 154, 106)),
        (0.76, (168, 248, 218)),
        (1.00, (  6,  88,  60)),
    ],
    "sapphire": [
        (0.00, (238, 250, 255)),
        (0.25, (112, 214, 255)),
        (0.52, ( 16, 108, 232)),
        (0.76, (172, 232, 255)),
        (1.00, (  8,  56, 136)),
    ],
    "coral": [
        (0.00, (255, 244, 232)),
        (0.25, (255, 156,  92)),
        (0.52, (228,  66,  36)),
        (0.76, (255, 198, 158)),
        (1.00, (142,  26,  10)),
    ],
    "pearl": [
        (0.00, (255, 255, 255)),
        (0.38, (246, 250, 252)),
        (0.70, (224, 234, 242)),
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

def ease_out_back_soft(u, overshoot=1.10):
    u = clamp01(u) - 1.0
    return 1.0 + u * u * ((overshoot + 1.0) * u + overshoot)

def ae_in_out(t, st, en, d_in=0.48, d_out=0.42, overshoot=1.10):
    if t <= st or t >= en:
        return 0.0, 0.0, 0.0, 0.0
    raw_in  = clamp01((t - st) / max(0.06, d_in))
    raw_out = clamp01((en - t) / max(0.06, d_out))
    u_in    = ease_out_back_soft(raw_in, overshoot=overshoot)
    u_out   = septic_smooth(raw_out)
    op      = min(quintic_smooth(min(1.0, raw_in * 1.35)), u_out)
    sigma   = (1.0 - quintic_smooth(raw_in)) * 3.2 + (1.0 - u_out) * 2.8
    return u_in, u_out, op, sigma

# ======================================================================
# 1. CONTINUOUS 3D PERSPECTIVE + SHUTTER MOTION BLUR + OPTICAL DOF ENGINE
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

def fit_cover_subpixel(rgb_arr, target_w, target_h, zoom=1.0, pan_x=0.0, pan_y=0.0):
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    inv_s = 1.0 / base_scale
    cx_src = sw * 0.5 + pan_x * sw
    cy_src = sh * 0.5 + pan_y * sh
    # Clamp crop bounds gently so camera pan never exposes black edges!
    half_w_s = (target_w * 0.5) * inv_s
    half_h_s = (target_h * 0.5) * inv_s
    cx_src = max(half_w_s, min(sw - half_w_s, cx_src))
    cy_src = max(half_h_s, min(sh - half_h_s, cy_src))
    c = cx_src - half_w_s
    f = cy_src - half_h_s
    return Image.fromarray(rgb_arr, "RGB").transform(
        (target_w, target_h), Image.Transform.AFFINE, (inv_s, 0.0, c, 0.0, inv_s, f), resample=Image.Resampling.BICUBIC
    )

# ======================================================================
# 2. MULTI-AXIS SPEAKER EMPHASIS CAMERA KEYFRAME ENGINE!
#    ("nhớ có key farme những điểm nhấn khi mẫu đọc")
# ======================================================================
# (time_sec, zoom, pan_x, pan_y, transition_dur_sec)
CAM_KEYFRAMES = [
    ( 0.00, 1.072,  0.008, -0.015, 0.45),  # Energetic Hook close-up: "Đừng đợi đến khi viêm mới chăm sóc!"
    ( 2.18, 1.016,  0.000,  0.000, 0.55),  # Pull out for Diagonal Comparison
    ( 5.28, 1.022,  0.000,  0.000, 0.55),  # Wide studio for 3-Card Fan
    ( 7.82, 1.082,  0.016, -0.018, 0.42),  # KEYFRAME PUNCH #1: "khi đã ngứa, có mùi hoặc khí hư bất thường!"
    (10.15, 1.022,  0.000,  0.000, 0.56),  # Pull out for Card 02 push
    (15.12, 1.052,  0.010, -0.010, 0.48),  # Subtle push: "điều trị mất nhiều thời gian hơn"
    (17.72, 1.112,  0.020, -0.024, 0.44),  # KEYFRAME PUNCH #2 (Philosophy Close-Up): "phòng ngừa thì luôn dễ hơn điều trị!"
    (20.94, 1.018,  0.000,  0.000, 0.56),  # Pull out for 2-Column Bento Comparison
    (25.15, 1.088,  0.014, -0.018, 0.40),  # KEYFRAME PUNCH #3: "là 2 việc hoàn toàn khác nhau!"
    (27.00, 1.094, -0.024,  0.008, 0.50),  # KEYFRAME PRODUCT PAN #4: Frame her lifting Romance VIP!
    (31.62, 1.024, -0.006,  0.000, 0.58),  # Clean medium shot for 4 Botanical Liquid-Glass Orbs
    (41.05, 1.076, -0.008, -0.012, 0.46),  # KEYFRAME PUNCH #5: "duy trì độ pH sinh lý, khử mùi, khô thoáng!"
    (45.65, 1.028,  0.004, -0.006, 0.52),  # Reset for Symptom Triage
    (47.68, 1.084,  0.016, -0.016, 0.40),  # KEYFRAME PUNCH #6: "ngứa, khí hư bất thường hay mùi khó chịu!"
    (50.28, 1.096, -0.024,  0.008, 0.48),  # KEYFRAME PRODUCT PAN #7: Frame her lifting green Viên Đặt Hằng Thu!
    (53.62, 1.024, -0.006,  0.000, 0.58),  # Clean frame for 4-Active Pharmaceutical Deck
    (65.54, 1.082,  0.012, -0.014, 0.44),  # KEYFRAME PUNCH #8: "làm dịu, dưỡng ẩm & chăm sóc niêm mạc!"
    (68.72, 1.092, -0.016,  0.006, 0.46),  # KEYFRAME DUAL-HOLD #9: "đây là bộ đôi chăm sóc toàn diện!"
    (72.80, 1.026, -0.008,  0.000, 0.55),  # Wide frame showing BOTH held boxes + Left/Right Synergy Brackets
    (86.78, 1.095,  0.016, -0.018, 0.50),  # KEYFRAME FINALE #10: "nền tảng cho sức khỏe và hạnh phúc lâu dài!"
    (91.15, 1.042,  0.008, -0.008, 0.80),
]

def eval_camera_rig(t):
    z_cur, px_cur, py_cur = CAM_KEYFRAMES[0][1], CAM_KEYFRAMES[0][2], CAM_KEYFRAMES[0][3]
    for i in range(1, len(CAM_KEYFRAMES)):
        tk, zk, pxk, pyk, dur_k = CAM_KEYFRAMES[i]
        if t >= tk:
            u = septic_smooth(clamp01((t - tk) / max(0.20, dur_k)))
            z_cur  = z_cur  + (zk  - z_cur)  * u
            px_cur = px_cur + (pxk - px_cur) * u
            py_cur = py_cur + (pyk - py_cur) * u
    # Add ultra-subtle cinema camera breathing (+0.004) so holds feel alive
    z_cur += 0.004 * math.sin(t * 1.35)
    return z_cur, px_cur, py_cur

# ======================================================================
# 3. 5-STOP GRADIENT TYPOGRAPHY + 4-POINT BLING SPARKLES (tvc-qc-san-pham)
# ======================================================================
_grad_sprite_cache = {}
def render_5stop_grad_sprite(text, font_path, size, palette="gold", stroke_col=(12, 16, 28), stroke_w=6, extrude_col=(6, 10, 20), extrude_dy=3, shadow_alpha=105, glow_alpha=45):
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
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=6.0)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (8, 12, 24)
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

    if len(_grad_sprite_cache) > 1050:
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

_sparkle_sprite = None
def get_4pt_sparkle_sprite():
    global _sparkle_sprite
    if _sparkle_sprite is not None:
        return _sparkle_sprite
    S = 96
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S * 0.5
    pts = []
    for k in range(8):
        ang = k * (math.pi / 4.0)
        r = 40.0 if k % 2 == 0 else 7.5
        pts.append((c + r * math.cos(ang), c + r * math.sin(ang)))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon(pts, fill=(255, 232, 148, 220))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(radius=5.5)))
    ImageDraw.Draw(im).polygon(pts, fill=(255, 252, 238, 255))
    _sparkle_sprite = im
    return im

def draw_bling_sparkles(canvas_im, centers, t_local, opacity=1.0):
    sp = get_4pt_sparkle_sprite()
    for idx, (sx, sy, sc_max) in enumerate(centers):
        ph = (t_local * 2.2 + idx * 0.37) % 1.6
        if ph < 1.15:
            u = math.sin((ph / 1.15) * math.pi)
            paste_3d_smooth(canvas_im, sp, sx, sy, scale=sc_max * (0.25 + 0.75 * u), rz_deg=ph * 32.0, opacity=opacity * u)

# ======================================================================
# 4. DIVERSE OVERLAY SYSTEMS ("lớp phủ sử dụng đa dạng các loại")
# ======================================================================

# --- OVERLAY SYSTEM A: Diagonal Angled Split-Glass Duo (CapCut Line-Mask Style) ---
def render_diagonal_split_duo(canvas_im, vf_left, vf_right, t, st, en):
    ui, uo, op, sig = ae_in_out(t, st, en, d_in=0.52, d_out=0.44, overshoot=1.08)
    if op <= 0.008:
        return
    pw, ph = 948, 464
    pad = 24
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + pw, pad + ph + 10], radius=38, fill=(8, 12, 24, 122))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    # Staggered entry of left & right diagonal halves! (pan_x shifts subject cleanly into each half!)
    u_l = ease_out_back_soft(clamp01((t - st) / 0.48), 1.06)
    u_r = ease_out_back_soft(clamp01((t - st - 0.14) / 0.48), 1.06)
    im_l = fit_cover_subpixel(vf_left,  pw, ph, zoom=1.06, pan_x=+0.15 + (1.0 - u_l) * (+0.07))
    im_r = fit_cover_subpixel(vf_right, pw, ph, zoom=1.06, pan_x=-0.18 + (1.0 - u_r) * (-0.07))

    yy, xx = np.ogrid[0:ph, 0:pw]
    # 103-degree CapCut Pro Editor diagonal split mask with smooth feather!
    diag_dist = (xx.astype(np.float32) - pw * 0.50) + (yy.astype(np.float32) - ph * 0.50) * 0.23
    w_right = np.clip((diag_dist + 16.0) / 32.0, 0.0, 1.0)[:, :, None]
    comp_rgb = (np.array(im_l, dtype=np.float32) * (1.0 - w_right) + np.array(im_r, dtype=np.float32) * w_right).astype(np.uint8)

    # Top & bottom subtle glass header gradient
    rmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=38, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(Image.fromarray(comp_rgb, "RGB"), (pad, pad), mask=rmask)
    card = Image.alpha_composite(card, vl)

    d = ImageDraw.Draw(card)
    # Glowing gold diagonal divider line + luxury frame border
    x_top = pad + pw * 0.50 - (-ph * 0.50) * 0.23
    x_bot = pad + pw * 0.50 - (+ph * 0.50) * 0.23
    d.line([(x_top, pad + 3), (x_bot, pad + ph - 3)], fill=(255, 232, 152, 245), width=4)
    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=38, outline=(252, 225, 129, 242), width=3)

    # Left & Right Glass Tags + Center "≈" Gold Emblem
    for lx, ltxt, lpal in [(pad + 225, "CHĂM SÓC LÀN DA", "pearl"), (pad + pw - 235, "VÙNG KÍN MỖI NGÀY", "rose_satin")]:
        d.rounded_rectangle([lx - 175, pad + 16, lx + 175, pad + 62], radius=23, fill=(14, 18, 32, 218), outline=(252, 225, 129, 195), width=2)
        sp, _ = render_5stop_grad_sprite(ltxt, FONT_SUB_MAIN, 21, palette=lpal, stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
        paste_3d_smooth(card, sp, lx, pad + 39)

    cx_m, cy_m = pad + pw * 0.5, pad + ph * 0.52
    d.ellipse([cx_m - 36, cy_m - 36, cx_m + 36, cy_m + 36], fill=(18, 22, 38, 238), outline=(252, 225, 129, 250), width=3)
    sp_eq, _ = render_5stop_grad_sprite("≈", FONT_SERIF_HERO, 40, palette="gold", stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
    paste_3d_smooth(card, sp_eq, cx_m, cy_m - 2)

    paste_3d_smooth(canvas_im, card, 540.0, 325.0 + (1.0 - ui) * (-30.0) - (1.0 - uo) * 20.0, scale=(0.90 + 0.10 * ui) * (0.94 + 0.06 * uo), rx_deg=(1.0 - ui) * 9.0, opacity=op, dof_sigma=sig)

# --- OVERLAY SYSTEM B: 3D Playing-Card Fan & Sequential Push-Carousel ---
_card_shell_cache = {}
def get_playing_card_shell(w, h, idx_str, title_str, palette="gold", rim_rgb=(252, 225, 129)):
    k = (w, h, idx_str, title_str, palette, rim_rgb)
    if k in _card_shell_cache:
        return _card_shell_cache[k]
    pad = 24
    cw, ch = w + pad * 2, h + pad * 2
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius=34, fill=(8, 12, 24, 126))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=14))
    rmask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=255)

    overlay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vy = np.linspace(1.0, 0.0, 86, dtype=np.float32)[:, None]
    ha = np.zeros((86, w, 4), dtype=np.uint8)
    ha[:, :, 0], ha[:, :, 1], ha[:, :, 2] = (12, 16, 28)
    ha[:, :, 3] = (vy * 214.0).astype(np.uint8)
    overlay.paste(Image.fromarray(ha, "RGBA"), (pad, pad), mask=rmask.crop((0, 0, w, 86)))

    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius=34, outline=(*rim_rgb, 242), width=3)
    d.rounded_rectangle([pad + 5, pad + 5, pad + w - 6, pad + h - 6], radius=29, outline=(255, 255, 255, 108), width=1)
    d.rounded_rectangle([pad + 16, pad + 14, pad + 78, pad + 56], radius=16, fill=(20, 26, 42, 236), outline=(*rim_rgb, 224), width=2)
    sp_idx, _ = render_5stop_grad_sprite(idx_str, FONT_MONTS_BLK, 24, palette=palette, stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
    sp_ic = sp_idx.crop(sp_idx.getbbox())
    overlay.alpha_composite(sp_ic, dest=(pad + 47 - sp_ic.width // 2, pad + 35 - sp_ic.height // 2))

    sp_t, _ = render_5stop_grad_sprite(title_str, FONT_SUB_MAIN, 22, palette="pearl", stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=60, glow_alpha=0)
    sp_tc = sp_t.crop(sp_t.getbbox())
    max_tw = w - 108
    if sp_tc.width > max_tw:
        nh = max(12, int(round(sp_tc.height * (max_tw / float(sp_tc.width)))))
        sp_tc = sp_tc.resize((max_tw, nh), Image.Resampling.LANCZOS)
    overlay.alpha_composite(sp_tc, dest=(pad + 90, pad + 35 - sp_tc.height // 2))
    _card_shell_cache[k] = (sh, rmask, overlay, pad)
    return _card_shell_cache[k]

def build_live_playing_card(vf_rgb, w, h, idx_str, title_str, palette="gold", rim_rgb=(252, 225, 129), zoom=1.02):
    sh, rmask, overlay, pad = get_playing_card_shell(w, h, idx_str, title_str, palette, rim_rgb)
    card = sh.copy()
    vlay = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    vlay.paste(fit_cover_subpixel(vf_rgb, w, h, zoom=zoom), (pad, pad), mask=rmask)
    return Image.alpha_composite(Image.alpha_composite(card, vlay), overlay)

def eval_deck_focus(t, focus_schedule, push_dur=0.64):
    cur_val = float(focus_schedule[0][1])
    vel = 0.0
    for idx in range(1, len(focus_schedule)):
        ts, targ = focus_schedule[idx]
        prev_targ = focus_schedule[idx - 1][1]
        if t >= ts:
            u = clamp01((t - ts) / push_dur)
            sm = septic_smooth(u)
            if 0.001 < u < 0.999:
                vel = (float(targ) - float(prev_targ)) * 140.0 * (u ** 3) * ((1.0 - u) ** 3) / push_dur
            cur_val = float(prev_targ) + (float(targ) - float(prev_targ)) * sm
    return cur_val, vel

def render_3d_playing_card_deck(canvas_im, card_sprites, t, st, en, focus_schedule, fan_hold_until=None, refan_from=None, cy_base=365.0):
    if t <= st or t >= en:
        return
    K = len(card_sprites)
    raw_in  = clamp01((t - st) / 0.62)
    raw_out = clamp01((en - t) / 0.52)
    u_in    = ease_out_back_soft(raw_in, overshoot=1.09)
    u_out   = septic_smooth(raw_out)
    op_deck = min(quintic_smooth(min(1.0, raw_in * 1.32)), u_out)
    if op_deck <= 0.008:
        return

    w_car = septic_smooth(clamp01((t - fan_hold_until) / 0.62)) if fan_hold_until is not None else 0.0
    if refan_from is not None and t >= refan_from:
        w_car *= (1.0 - septic_smooth(clamp01((t - refan_from) / 0.62)))

    foc_idx, foc_vel = eval_deck_focus(t, focus_schedule, push_dur=0.64)
    mid_k = (K - 1) * 0.5
    spread_fan = 262.0 if K == 3 else 198.0
    fan_sc = 0.62 if K == 3 else 0.55

    draw_queue = []
    for i in range(K):
        s_fan = i - mid_k
        fx = 540.0 + s_fan * spread_fan * u_in
        fy = cy_base + 10.0 + abs(s_fan) * 30.0 + (1.0 - u_in) * 85.0
        f_sc = fan_sc * (0.82 + 0.18 * u_in)
        f_ry = -s_fan * (13.0 if K == 3 else 10.5) * u_in
        f_rz = s_fan * (8.0 if K == 3 else 6.2) * u_in
        f_rx = (1.0 - u_in) * 12.0
        f_z  = 10.0 - abs(s_fan) * 6.0

        rel = float(i) - foc_idx
        abs_r = abs(rel)
        swap_arc = math.sin(clamp01(abs_r) * math.pi) if abs_r < 1.0 else 0.0
        cx_car = 540.0 + rel * (228.0 if K == 3 else 182.0) + (-34.0 if rel < 0 else 34.0) * swap_arc * 0.45
        cy_car = cy_base - 8.0 + min(2.2, abs_r) * 32.0 - swap_arc * 14.0
        sc_car = 0.96 - min(1.0, abs_r) * 0.22 - max(0.0, abs_r - 1.0) * 0.05
        ry_car = -max(-22.0, min(22.0, rel * 16.0))
        rz_car = max(-10.0, min(10.0, rel * 6.5))
        rx_car = -1.5 * (1.0 - min(1.0, abs_r))
        dim_car = 1.00 - min(1.0, abs_r) * 0.24
        dof_car = min(1.0, abs_r) * 1.7
        z_car   = 100.0 * math.cos(min(1.5, abs_r)) - abs_r * 25.0

        px = (fx * (1.0 - w_car) + cx_car * w_car) * u_out + 540.0 * (1.0 - u_out)
        py = (fy * (1.0 - w_car) + cy_car * w_car) - (1.0 - u_out) * 42.0 + math.sin(t * 1.7 + i) * 3.0
        psc = (f_sc * (1.0 - w_car) + sc_car * w_car) * (0.88 + 0.12 * u_out)
        pry = (f_ry * (1.0 - w_car) + ry_car * w_car) * u_out
        prz = (f_rz * (1.0 - w_car) + rz_car * w_car) * u_out
        prx = (f_rx * (1.0 - w_car) + rx_car * w_car) + (1.0 - u_out) * 10.0
        pdim = 0.98 * (1.0 - w_car) + dim_car * w_car
        pdof = dof_car * w_car + (1.0 - quintic_smooth(raw_in)) * 3.0 + (1.0 - u_out) * 3.0
        pz   = f_z * (1.0 - w_car) + z_car * w_car
        mb_x = -foc_vel * 220.0 * w_car / FPS
        draw_queue.append((pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x))

    draw_queue.sort(key=lambda x: x[0])
    for pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x in draw_queue:
        paste_3d_smooth(canvas_im, card_sprites[i], px, py, scale=psc, rx_deg=prx, ry_deg=pry, rz_deg=prz, opacity=op_deck, dof_sigma=pdof, mb_dx=mb_x, dim=pdim)

# --- OVERLAY SYSTEM C: Asymmetric 2-Column Bento Product Role Comparison ---
_bento_cache = {}
def get_bento_role_cards(rv_cut, vd_cut):
    if "pair" in _bento_cache:
        return _bento_cache["pair"]
    cards = []
    specs = [
        ("01 • HẰNG NGÀY", "LÀM SẠCH +\nGIỮ ĐỘ pH", "Dịu nhẹ mỗi ngày", "rose_satin", (255, 168, 214), rv_cut, (46, 20, 36)),
        ("02 • KHI MẤT CÂN BẰNG", "CHĂM SÓC +\nPHỤC HỒI SÂU", "Khi ngứa • khí hư • mùi", "emerald", (96, 230, 184), vd_cut, (16, 40, 34)),
    ]
    for tag, title_2l, sub, pal, rim, cut_im, tint in specs:
        pw, ph, pad = 446, 430, 22
        cw, ch = pw + pad * 2, ph + pad * 2
        c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + pw, pad + ph + 10], radius=36, fill=(8, 12, 24, 120))
        c = Image.alpha_composite(c, sh.filter(ImageFilter.GaussianBlur(radius=12)))

        yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
        bg = np.zeros((ph, pw, 4), dtype=np.uint8)
        bg[:, :, 0] = np.clip(tint[0] + (1.0 - yy[:, 0]) * 18, 0, 255)[:, None]
        bg[:, :, 1] = np.clip(tint[1] + (1.0 - yy[:, 0]) * 20, 0, 255)[:, None]
        bg[:, :, 2] = np.clip(tint[2] + (1.0 - yy[:, 0]) * 26, 0, 255)[:, None]
        bg[:, :, 3] = 232
        rm = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=36, fill=255)
        bl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        bl.paste(Image.fromarray(bg, "RGBA"), (pad, pad), mask=rm)
        c = Image.alpha_composite(c, bl)
        ImageDraw.Draw(c).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=36, outline=(*rim, 240), width=3)

        sp_tag, _ = render_5stop_grad_sprite(tag, FONT_CONDENSED, 23, palette=pal, stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
        paste_3d_smooth(c, sp_tag, cw * 0.5, pad + 34)

        # Miniature real product cutout in center!
        if cut_im is not None:
            th_im = cut_im.copy()
            th_im.thumbnail((230, 175), Image.Resampling.LANCZOS)
            c.alpha_composite(th_im, dest=(int(cw * 0.5 - th_im.width * 0.5), pad + 148 - th_im.height // 2))

        for li, ln in enumerate(title_2l.split("\n")):
            sp_h, _ = render_5stop_grad_sprite(ln, FONT_SERIF_HERO, 31, palette=pal, stroke_col=(10, 14, 24), stroke_w=5, extrude_dy=2, shadow_alpha=70, glow_alpha=35)
            paste_3d_smooth(c, sp_h, cw * 0.5, pad + 266 + li * 40)
        sp_s, _ = render_5stop_grad_sprite(sub, FONT_SERIF_ITAL, 23, palette="pearl", stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=40, glow_alpha=0)
        paste_3d_smooth(c, sp_s, cw * 0.5, pad + 378)
        cards.append(c)
    _bento_cache["pair"] = cards
    return cards

def render_bento_comparison_duo(canvas_im, rv_cut, vd_cut, t, st, en):
    if t <= st or t >= en:
        return
    c_left, c_right = get_bento_role_cards(rv_cut, vd_cut)
    ui1, uo1, op1, sig1 = ae_in_out(t, st, en, d_in=0.50, d_out=0.42, overshoot=1.10)
    paste_3d_smooth(canvas_im, c_left, 286.0 - (1.0 - ui1) * 70.0, 325.0 + math.sin(t * 1.6) * 3.0, scale=(0.88 + 0.12 * ui1) * (0.94 + 0.06 * uo1), ry_deg=8.0, rz_deg=-1.8, opacity=op1, dof_sigma=sig1)

    if t >= st + 1.10:
        ui2, uo2, op2, sig2 = ae_in_out(t, st + 1.10, en, d_in=0.50, d_out=0.42, overshoot=1.10)
        paste_3d_smooth(canvas_im, c_right, 794.0 + (1.0 - ui2) * 70.0, 325.0 + math.sin(t * 1.6 + 1.4) * 3.0, scale=(0.88 + 0.12 * ui2) * (0.94 + 0.06 * uo2), ry_deg=-8.0, rz_deg=1.8, opacity=op2, dof_sigma=sig2)

# --- OVERLAY SYSTEM D: Apple Liquid-Glass 4-Botanical Orbital Arc ---
_orb_cache = {}
def get_liquid_glass_orb(img_rgb, label_top, label_sub, palette="gold", rim_rgb=(252, 225, 129)):
    k = (label_top, label_sub, palette)
    if k in _orb_cache:
        return _orb_cache[k]
    ow, oh, pad = 224, 258, 18
    cw, ch = ow + pad * 2, oh + pad * 2
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + ow, pad + oh + 8], radius=44, fill=(10, 14, 26, 118))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    # Frosted Liquid Glass Card + Circular Macro Photo Window
    d_bg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(d_bg)
    d.rounded_rectangle([pad, pad, pad + ow, pad + oh], radius=44, fill=(18, 24, 38, 222), outline=(*rim_rgb, 242), width=3)
    d.rounded_rectangle([pad + 5, pad + 5, pad + ow - 5, pad + oh - 5], radius=39, outline=(255, 255, 255, 95), width=1)
    im = Image.alpha_composite(im, d_bg)

    # Circular macro botanical lens at top!
    diam = 144
    cmask = Image.new("L", (diam, diam), 0)
    ImageDraw.Draw(cmask).ellipse([0, 0, diam - 1, diam - 1], fill=255)
    crop = fit_cover_subpixel(img_rgb, diam, diam, zoom=1.05)
    im.paste(crop, (pad + (ow - diam) // 2, pad + 16), mask=cmask)
    ImageDraw.Draw(im).ellipse([pad + (ow - diam) // 2, pad + 16, pad + (ow + diam) // 2, pad + 16 + diam], outline=(*rim_rgb, 235), width=3)

    sp1, _ = render_5stop_grad_sprite(label_top, FONT_SERIF_HERO, 22, palette=palette, stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=45, glow_alpha=20)
    sp2, _ = render_5stop_grad_sprite(label_sub, FONT_BE_MED, 17, palette="pearl", stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
    paste_3d_smooth(im, sp1, cw * 0.5, pad + 190)
    paste_3d_smooth(im, sp2, cw * 0.5, pad + 225)
    _orb_cache[k] = im
    return im

def render_botanical_orbital_arc(canvas_im, bot_imgs, t, st, en):
    if t <= st or t >= en:
        return
    _, u_out, op_all, _ = ae_in_out(t, st, en, d_in=0.40, d_out=0.44)
    if op_all <= 0.008:
        return

    # Subtle golden constellation arc connecting the 4 botanical pods!
    arc_im = Image.new("RGBA", (W, 620), (0, 0, 0, 0))
    da = ImageDraw.Draw(arc_im)
    da.arc([75, 195, 1005, 680], start=198, end=342, fill=(252, 225, 129, int(135 * op_all)), width=3)
    canvas_im.alpha_composite(arc_im, dest=(0, 0))

    specs = [
        (32.65, 152.0, 355.0, -8.0,  bot_imgs["bot_01_rose"],          "HOA HỒNG",  "Tinh chất dịu thơm",   "rose_satin", (255, 168, 214)),
        (33.85, 410.0, 272.0, -2.5,  bot_imgs["bot_02_greentea"],      "TRÀ XANH",  "Làm sạch thanh mát",   "emerald",    ( 96, 230, 184)),
        (34.72, 670.0, 272.0, +2.5,  bot_imgs["bot_03_aloe"],          "LÔ HỘI",    "Cấp ẩm làm dịu",       "emerald",    (140, 242, 204)),
        (35.42, 928.0, 355.0, +8.0,  bot_imgs["bot_04_vitE_collagen"], "VITAMIN E", "+ Collagen thực vật",  "gold",       (252, 225, 129)),
    ]
    for t_cue, cx, cy, rz, rgb_b, l1, l2, pal, rim in specs:
        if t >= t_cue:
            ui, uo, op, sig = ae_in_out(t, t_cue, en, d_in=0.46, d_out=0.42, overshoot=1.14)
            orb = get_liquid_glass_orb(rgb_b, l1, l2, palette=pal, rim_rgb=rim)
            bob = math.sin(t * 2.0 + cx * 0.01) * 4.5
            paste_3d_smooth(canvas_im, orb, cx, cy + bob + (1.0 - ui) * 42.0 - (1.0 - uo) * 24.0, scale=(0.76 + 0.24 * ui) * (0.92 + 0.08 * uo), rz_deg=rz * ui, ry_deg=-rz * 1.4, opacity=op, dof_sigma=sig)

# --- OVERLAY SYSTEM E: Animated Physiological pH 3.8-4.5 Gauge + Staggered 3-Tick Checklist ---
_chk_row_cache = {}
def get_checklist_row_sprite(text, palette="emerald"):
    if (text, palette) in _chk_row_cache:
        return _chk_row_cache[(text, palette)]
    pw, ph, pad = 820, 74, 14
    cw, ch = pw + pad * 2, ph + pad * 2
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 5, pad + pw, pad + ph + 5], radius=37, fill=(8, 12, 24, 105))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=7)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=37, fill=(16, 24, 38, 226), outline=(96, 230, 184, 228), width=2)
    d.ellipse([pad + 14, pad + 11, pad + 66, pad + 63], fill=(14, 150, 104, 255), outline=(220, 255, 242, 240), width=2)
    # 2x supersampled crisp vector checkmark!
    ck_hi = Image.new("RGBA", (104, 104), (0, 0, 0, 0))
    ImageDraw.Draw(ck_hi).line([(26, 54), (45, 73), (80, 33)], fill=(255, 255, 255, 255), width=11, joint="curve")
    im.alpha_composite(ck_hi.resize((52, 52), Image.Resampling.LANCZOS), dest=(pad + 14, pad + 11))
    sp_tx, _ = render_5stop_grad_sprite(text, FONT_SUB_MAIN, 26, palette=palette, stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=50, glow_alpha=20)
    sp_c = sp_tx.crop(sp_tx.getbbox())
    im.alpha_composite(sp_c, dest=(pad + 86, int(pad + ph * 0.5 - sp_c.height * 0.5)))
    _chk_row_cache[(text, palette)] = im
    return im

def render_ph_gauge_and_checklist(canvas_im, t, st, en):
    ui, uo, op, sig = ae_in_out(t, st, en, d_in=0.46, d_out=0.42, overshoot=1.08)
    if op <= 0.008:
        return
    # 1. Animated Physiological pH 3.8 - 4.5 Spectrum Meter at y = 155
    gw, gh, pad = 860, 138, 20
    gc = Image.new("RGBA", (gw + pad * 2, gh + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(gc)
    d.rounded_rectangle([pad, pad, pad + gw, pad + gh], radius=34, fill=(16, 22, 36, 232), outline=(252, 225, 129, 235), width=3)
    sp_lbl, _ = render_5stop_grad_sprite("ĐỘ pH SINH LÝ LÝ TƯỞNG: 3.8 – 4.5", FONT_SERIF_BOLD, 25, palette="gold", stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=45, glow_alpha=25)
    paste_3d_smooth(gc, sp_lbl, pad + gw * 0.5, pad + 36)

    # Colorimetric bar (Coral -> Gold -> Emerald Ideal Zone -> Sapphire)
    bx0, by0, bw, bh = pad + 54, pad + 78, gw - 108, 26
    bar_arr = np.zeros((bh, bw, 4), dtype=np.uint8)
    ux = np.linspace(0.0, 1.0, bw, dtype=np.float32)
    bar_arr[:, :, 0] = np.interp(ux, [0.0, 0.30, 0.48, 0.72, 1.0], [235, 92,  24, 110,  52]).astype(np.uint8)[None, :]
    bar_arr[:, :, 1] = np.interp(ux, [0.0, 0.30, 0.48, 0.72, 1.0], [ 95, 228, 195, 205, 125]).astype(np.uint8)[None, :]
    bar_arr[:, :, 2] = np.interp(ux, [0.0, 0.30, 0.48, 0.72, 1.0], [ 75, 168, 138, 245, 235]).astype(np.uint8)[None, :]
    bar_arr[:, :, 3] = 255
    bmask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(bmask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=13, fill=255)
    gc.paste(Image.fromarray(bar_arr, "RGBA"), (bx0, by0), mask=bmask)
    # Highlight bracket on ideal 3.8-4.5 zone (ux = 0.30 .. 0.54)
    zx0, zx1 = int(bx0 + bw * 0.28), int(bx0 + bw * 0.56)
    d.rounded_rectangle([zx0, by0 - 5, zx1, by0 + bh + 5], radius=14, outline=(255, 250, 210, 255), width=3)
    # Animated needle gliding from 0.78 -> locking into 0.42!
    u_needle = septic_smooth(clamp01((t - st - 0.15) / 0.95))
    nx = int(bx0 + bw * (0.78 + (0.42 - 0.78) * u_needle))
    d.polygon([(nx, by0 - 2), (nx - 11, by0 - 18), (nx + 11, by0 - 18)], fill=(255, 238, 152, 255))
    d.ellipse([nx - 11, by0 + bh // 2 - 11, nx + 11, by0 + bh // 2 + 11], fill=(255, 255, 255, 255), outline=(14, 150, 104, 255), width=4)

    paste_3d_smooth(canvas_im, gc, 540.0, 152.0 + (1.0 - ui) * (-26.0), scale=(0.90 + 0.10 * ui) * (0.94 + 0.06 * uo), opacity=op, dof_sigma=sig)

    # 2. Staggered 3-Tick Benefit Checklist Rows
    rows = [
        (41.00, "Duy trì độ pH sinh lý ổn định",          "emerald"),
        (42.48, "Khử mùi nhẹ nhàng • Thanh sạch tự nhiên","gold"),
        (44.05, "Cảm giác khô thoáng & dễ chịu suốt ngày","pearl"),
    ]
    for idx, (tc, rtxt, rpal) in enumerate(rows):
        if t >= tc:
            uir, uor, opr, sigr = ae_in_out(t, tc, en, d_in=0.40, d_out=0.38, overshoot=1.12)
            rsp = get_checklist_row_sprite(rtxt, palette=rpal)
            paste_3d_smooth(canvas_im, rsp, 540.0 + (1.0 - uir) * 55.0, 292.0 + idx * 88.0, scale=(0.90 + 0.10 * uir) * (0.94 + 0.06 * uor), opacity=opr, dof_sigma=sigr)

# --- OVERLAY SYSTEM F: Floating Synergy Dual Callout Brackets (72.8 - 79.7s) ---
def render_synergy_dual_brackets(canvas_im, t, st, en):
    specs = [
        (72.80, 275.0, 345.0, "ROMANCE VIP",       "LÀM SẠCH +\nBẢO VỆ MỖI NGÀY",   "rose_satin", (255, 168, 214)),
        (75.44, 805.0, 345.0, "VIÊN ĐẶT HẰNG THU", "CHĂM SÓC +\nPHỤC HỒI CHUYÊN SÂU","emerald",   ( 96, 230, 184)),
    ]
    for tc, cx, cy, kicker, body, pal, rim in specs:
        if tc <= t < en:
            ui, uo, op, sig = ae_in_out(t, tc, en, d_in=0.46, d_out=0.40, overshoot=1.12)
            pw, ph, pad = 436, 238, 20
            cw, ch = pw + pad * 2, ph + pad * 2
            c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            d = ImageDraw.Draw(c)
            d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=34, fill=(16, 22, 36, 230), outline=(*rim, 242), width=3)
            s1, _ = render_5stop_grad_sprite(kicker, FONT_CONDENSED, 24, palette=pal, stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
            paste_3d_smooth(c, s1, cw * 0.5, pad + 38)
            d.line([(pad + 48, pad + 68), (pad + pw - 48, pad + 68)], fill=(*rim, 150), width=2)
            for li, ln in enumerate(body.split("\n")):
                sb, _ = render_5stop_grad_sprite(ln, FONT_SERIF_HERO, 29, palette="pearl" if li == 0 else pal, stroke_col=(10, 14, 24), stroke_w=5, extrude_dy=2, shadow_alpha=65, glow_alpha=25)
                paste_3d_smooth(c, sb, cw * 0.5, pad + 118 + li * 44)
            paste_3d_smooth(canvas_im, c, cx, cy + (1.0 - ui) * (-30.0) + math.sin(t * 1.8 + cx) * 3.0, scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), ry_deg=(7.0 if cx < 540 else -7.0), opacity=op, dof_sigma=sig)

# ======================================================================
# 5. DIVERSE EMPHASIS TYPOGRAPHY WIDGETS ("text nhấn cũng vậy. fort chữ đẹp mắt")
# ======================================================================

# --- EMPHASIS WIDGET 1: Editorial Serif + Display Bling Lockup (Fraunces-Black + Playfair BoldItalic) ---
_ed_lockup_cache = {}
def get_editorial_bling_banner(lead_italic, hero_line1, hero_line2, sub_tag, pal_hero="gold"):
    k = (lead_italic, hero_line1, hero_line2, sub_tag, pal_hero)
    if k in _ed_lockup_cache:
        return _ed_lockup_cache[k]
    pw, ph, pad = 952, (288 if hero_line2 else 238), 26
    cw, ch = pw + pad * 2, ph + pad * 2
    c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + pw, pad + ph + 10], radius=42, fill=(8, 12, 24, 122))
    c = Image.alpha_composite(c, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    yy = np.linspace(0.0, 1.0, ph, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, pw, dtype=np.float32)[None, :]
    lift = np.exp(-(xx * xx * 1.1 + (yy - 0.35) ** 2 * 1.7))
    bg = np.zeros((ph, pw, 4), dtype=np.uint8)
    bg[:, :, 0] = np.clip(18 + 26 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 1] = np.clip(22 + 30 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 2] = np.clip(38 + 44 * lift, 0, 255).astype(np.uint8)
    bg[:, :, 3] = 236
    rm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=42, fill=255)
    bl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bl.paste(Image.fromarray(bg, "RGBA"), (pad, pad), mask=rm)
    c = Image.alpha_composite(c, bl)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=42, outline=(252, 225, 129, 242), width=3)
    d.rounded_rectangle([pad + 6, pad + 6, pad + pw - 7, pad + ph - 7], radius=36, outline=(255, 255, 255, 85), width=1)

    s_lead, _ = render_5stop_grad_sprite(lead_italic, FONT_SERIF_ITAL, 28, palette="pearl", stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=50, glow_alpha=0)
    paste_3d_smooth(c, s_lead, cw * 0.5, pad + 44)

    sz1 = 48 if len(hero_line1) <= 20 else 40
    sh1, _ = render_5stop_grad_sprite(hero_line1, FONT_SERIF_HERO, sz1, palette=pal_hero, stroke_col=(10, 14, 24), stroke_w=6, extrude_dy=3, shadow_alpha=90, glow_alpha=55)
    paste_3d_smooth(c, sh1, cw * 0.5, pad + 114)

    if hero_line2:
        sh2, _ = render_5stop_grad_sprite(hero_line2, FONT_SERIF_HERO, 44, palette=pal_hero, stroke_col=(10, 14, 24), stroke_w=6, extrude_dy=3, shadow_alpha=90, glow_alpha=55)
        paste_3d_smooth(c, sh2, cw * 0.5, pad + 172)
        y_line, y_sub = pad + 218, pad + 250
    else:
        y_line, y_sub = pad + 166, pad + 200

    d.line([(cw // 2 - 230, y_line), (cw // 2 + 230, y_line)], fill=(252, 225, 129, 155), width=2)
    ssub, _ = render_5stop_grad_sprite(sub_tag, FONT_SUB_BOLD, 21, palette="pearl", stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=40, glow_alpha=0)
    paste_3d_smooth(c, ssub, cw * 0.5, y_sub)
    _ed_lockup_cache[k] = c
    return c

# --- EMPHASIS WIDGET 2: Condensed Architectural Stamp Ribbon (Oswald-Bold + Gold Frame) ---
_stamp_cache = {}
def get_angled_stamp_ribbon(icon_char, main_txt, palette="coral", rim_rgb=(255, 165, 122)):
    k = (icon_char, main_txt, palette)
    if k in _stamp_cache:
        return _stamp_cache[k]
    sp_m, _ = render_5stop_grad_sprite(main_txt, FONT_CONDENSED, 32, palette=palette, stroke_col=(10, 14, 24), stroke_w=5, extrude_dy=2, shadow_alpha=55, glow_alpha=30)
    smc = sp_m.crop(sp_m.getbbox())
    pw, ph, pad = min(980, smc.width + 116), 72, 16
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad + 5, pad + pw, pad + ph + 5], radius=22, fill=(8, 12, 24, 115))
    im = im.filter(ImageFilter.GaussianBlur(radius=5))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=22, fill=(18, 22, 36, 236), outline=(*rim_rgb, 245), width=3)
    d.ellipse([pad + 14, pad + 12, pad + 62, pad + 60], fill=(*rim_rgb, 45), outline=(*rim_rgb, 240), width=2)
    sp_i, _ = render_5stop_grad_sprite(icon_char, FONT_MONTS_BLK, 26, palette=palette, stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0)
    paste_3d_smooth(im, sp_i, pad + 38, pad + 36)
    im.alpha_composite(smc, dest=(pad + 78, int(pad + ph * 0.5 - smc.height * 0.5)))
    _stamp_cache[k] = im
    return im

# --- EMPHASIS WIDGET 3: Handwritten Script + Serif Luxury Header (DancingScript + Fraunces) ---
_script_hdr_cache = {}
def get_script_editorial_header(script_line, serif_line, sub_line):
    k = (script_line, serif_line, sub_line)
    if k in _script_hdr_cache:
        return _script_hdr_cache[k]
    pw, ph, pad = 936, 246, 24
    cw, ch = pw + pad * 2, ph + pad * 2
    c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=40, fill=(22, 18, 30, 212), outline=(252, 225, 129, 235), width=3)
    s1, _ = render_5stop_grad_sprite(script_line, FONT_SCRIPT, 46, palette="gold", stroke_col=(12, 14, 24), stroke_w=5, extrude_dy=2, shadow_alpha=60, glow_alpha=35)
    s2, _ = render_5stop_grad_sprite(serif_line, FONT_SERIF_HERO, 38, palette="rose_satin", stroke_col=(12, 14, 24), stroke_w=5, extrude_dy=2, shadow_alpha=75, glow_alpha=40)
    s3, _ = render_5stop_grad_sprite(sub_line, FONT_SUB_BOLD, 21, palette="pearl", stroke_col=(12, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=40, glow_alpha=0)
    paste_3d_smooth(c, s1, cw * 0.5, pad + 52)
    paste_3d_smooth(c, s2, cw * 0.5, pad + 132)
    d.line([(cw // 2 - 210, pad + 178), (cw // 2 + 210, pad + 178)], fill=(252, 225, 129, 145), width=2)
    paste_3d_smooth(c, s3, cw * 0.5, pad + 208)
    _script_hdr_cache[k] = c
    return c

# --- EMPHASIS WIDGET 4: Liquid-Glass Top Callout Pill ---
_pill_cache = {}
def get_liquid_pill(label_txt, palette="gold", font_path=FONT_SUB_MAIN, font_sz=23, dot_rgb=(252, 225, 129)):
    k = (label_txt, palette, font_path, font_sz, dot_rgb)
    if k in _pill_cache:
        return _pill_cache[k]
    sp, _ = render_5stop_grad_sprite(label_txt, font_path, font_sz, palette=palette, stroke_col=(10, 14, 24), stroke_w=4, extrude_dy=1, shadow_alpha=45, glow_alpha=25)
    spc = sp.crop(sp.getbbox())
    pw, ph, pad = min(1010, spc.width + 78), max(56, spc.height + 22), 16
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=ph // 2, fill=(16, 22, 36, 228), outline=(255, 244, 218, 232), width=2)
    cy = pad + ph // 2
    d.ellipse([pad + 20, cy - 6, pad + 32, cy + 6], fill=(*dot_rgb, 255))
    im.alpha_composite(spc, dest=(int(pad + pw * 0.5 + 10 - spc.width * 0.5), int(cy - spc.height * 0.5)))
    _pill_cache[k] = im
    return im

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
    mix[:, :, 0:3] = np.clip(mix[:, :, 0:3] + bell * 14.0, 0, 255)
    mix[:, :, 3] = 255.0
    return Image.fromarray(mix.astype(np.uint8), "RGBA")

def make_live_speaker_pip(fg_rgb, pw=236, ph=312):
    sub = fg_rgb[520:1420, 230:890]
    im = fit_cover_subpixel(sub, pw, ph, zoom=1.02)
    pad = 16
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + pw, pad + ph + 8], radius=32, fill=(10, 14, 24, 122))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=9)))
    rm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(im, (pad, pad), mask=rm)
    card = Image.alpha_composite(card, vl)
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=32, outline=(252, 225, 129, 242), width=3)
    return card

# ======================================================================
# 6. BRIGHT COLOR GRADE & LUXURY MULTI-FONT SUBTITLES (100% BOX-SAFE!)
# ======================================================================
def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.96) * 1.016, 0.0, 1.0)
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

def load_captions_ddvs2():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and (w["start"] + w["end"]) * 0.5 >= 2.16
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
            elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 4 or dur_so_far >= 1.35):
                phrases.append(cur_p); cur_p = []
            elif len(cur_p) >= 8 or sum(len(x[0]) + 1 for x in cur_p) + len(txt) > 35:
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

    GOLD_W    = {"Hằng,", "Hằng", "phòng", "ngừa", "2", "Vitamin", "E,", "Collagen", "pH", "pH,", "Thu", "bộ", "đôi", "toàn", "diện.", "hạnh", "phúc"}
    ROSE_W    = {"Romance", "VIP.", "hoa", "hồng,", "dịu", "nhẹ,", "yêu", "thương", "tự", "tin"}
    EMERALD_W = {"lô", "hội,", "trà", "xanh,", "sinh", "lý,", "khô", "thoáng,", "Viên", "đặt", "Acid", "Lactic,", "hoàng", "cung,", "cam", "thảo", "Niacinamide", "Glycerin,", "phục", "hồi.", "khỏe", "mạnh"}
    CORAL_W   = {"viêm", "ngứa,", "mùi", "khí", "hư", "mất", "nấm", "điều", "trị", "trị."}

    cap_groups = []
    for i, p in enumerate(merged):
        t0 = max(2.16, p[0][1] - 0.05)
        last_end = p[-1][2]
        nxt_s = merged[i + 1][0][1] if i + 1 < len(merged) else 91.00
        min_hold = max(last_end + 0.42, t0 + 1.55)
        t1 = min(nxt_s - 0.04, max(min_hold, last_end + 0.65))
        if t1 <= last_end + 0.12:
            t1 = min(nxt_s - 0.02, last_end + 0.25)
        cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced(p)})
    return cap_groups, GOLD_W, ROSE_W, EMERALD_W, CORAL_W

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
# 7. MAIN COMPOSITING LOOP (2,732 FRAMES = 91.09s)
# ======================================================================
def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [1.10, 3.80, 11.40, 19.20, 24.40, 36.20, 44.50, 58.60, 76.60, 83.20, 88.80, 29.80]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vid_keys = [
        ("m1_skincare_daily",       960, 540),
        ("m2_delayed_worry",        960, 640),
        ("m3_ph_microbe_lab",       960, 640),
        ("m4_long_treatment",       960, 640),
        ("p1_romance_vip_showcase", 1280, 720),
        ("p2_viendat_exact_showcase",1280, 720),
        ("m5_duo_exact_synergy",    1280, 720),
        ("m6_radiant_confidence_916",1080, 1920),
    ]
    clips = {}
    for ck, vw, vh in vid_keys:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if os.path.exists(vp):
            clips[ck] = load_vid_frames_wh(vp, vw, vh)
            print(f"Loaded {ck}: {len(clips[ck])} frames")
        else:
            print(f"WARNING missing {vp}")

    imgs = {}
    for ifn in ["bot_01_rose", "bot_02_greentea", "bot_03_aloe", "bot_04_vitE_collagen",
                "act_01_lactic", "act_02_trinhnu", "act_03_licorice", "act_04_niacin_glycerin"]:
        ip = os.path.join(MEDIA_DIR, f"{ifn}.jpg")
        imgs[ifn] = np.array(Image.open(ip).convert("RGB")) if os.path.exists(ip) else np.full((640, 960, 3), 215, dtype=np.uint8)

    rv_cut = Image.open(os.path.join(MEDIA_DIR, "cutout_romance_vip.png")).convert("RGBA") if os.path.exists(os.path.join(MEDIA_DIR, "cutout_romance_vip.png")) else None
    vd_cut = Image.open(os.path.join(MEDIA_DIR, "cutout_viendat_exact.png")).convert("RGBA") if os.path.exists(os.path.join(MEDIA_DIR, "cutout_viendat_exact.png")) else None

    cap_groups, GOLD_W, ROSE_W, EMERALD_W, CORAL_W = load_captions_ddvs2()

    # Pre-build bottom mahogany soft scrim for 100% Box-Safe subtitle clarity!
    scrim_h = 330
    sy = np.linspace(0.0, 1.0, scrim_h, dtype=np.float32)[:, None]
    sa = np.zeros((scrim_h, W, 4), dtype=np.uint8)
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (10, 12, 20)
    sa[:, :, 3] = (np.power(sy, 1.5) * 158.0).astype(np.uint8)
    bot_scrim = Image.fromarray(sa, "RGBA")

    legal_sp, _ = render_5stop_grad_sprite(
        "Sản phẩm hỗ trợ chăm sóc & vệ sinh chuyên biệt Hằng Thu Pharma • Đọc kỹ hướng dẫn sử dụng trước khi dùng",
        FONT_BE_MED, 17, palette="pearl", stroke_col=(10, 14, 24), stroke_w=3, extrude_dy=0, shadow_alpha=0, glow_alpha=0
    )
    cta_ribbon = get_liquid_pill("Romance VIP + Viên Đặt Phụ Khoa Hằng Thu  •  Bộ Đôi Chăm Sóc Toàn Diện", palette="gold", font_path=FONT_SERIF_BOLD, font_sz=22, dot_rgb=(96, 230, 184))

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)

    raw_vid_out = os.path.join(PROJ_DIR, "_ddvs2_master_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    yy_g = np.arange(H, dtype=np.float32)[:, None]
    # Keep everything below y=880 (her hands, held product boxes & desk boxes) 100% opaque in foreground!
    lower_body_box_guard = np.clip((yy_g - 865.0) / 55.0, 0.0, 1.0)

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
        matte_raw = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W))
        t = frame_idx / FPS

        # Multi-axis Camera Rig Keyframes!
        z_cam, px_cam, py_cam = eval_camera_rig(t)
        fg_im = fit_cover_subpixel(rgb, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam)
        m_rgb = np.repeat(matte_raw[:, :, None], 3, axis=2)
        m_im  = fit_cover_subpixel(m_rgb, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam).convert("L")
        fg_rgb = np.array(fg_im)
        m_arr  = np.array(m_im, dtype=np.float32) / 255.0

        base_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

        # ==================================================================
        # 1. BEHIND-SPEAKER DIVERSE OVERLAY SYSTEMS (7 DISTINCT TYPES!)
        # ==================================================================
        # TYPE 1 (2.18 - 5.24s): Diagonal Angled Split-Glass Duo ("Giống như làn da, vùng kín cần chăm sóc mỗi ngày")
        if 2.16 <= t < 5.26:
            vf_l = get_clip_frame_smooth(clips, "m1_skincare_daily", t - 2.16, target_span=3.1)
            vf_r = get_clip_frame_smooth(clips, "p1_romance_vip_showcase", t - 2.16, target_span=3.1)
            render_diagonal_split_duo(base_im, vf_l, vf_r, t, 2.18, 5.24)

        # TYPE 2 (5.28 - 17.68s): 3D Playing-Card Fan & Sequential Push-Carousel (3 Warning Cards)
        if 5.28 <= t < 17.68:
            w1 = get_clip_frame_smooth(clips, "m2_delayed_worry",  max(0.0, t - 5.28),  target_span=5.0)
            w2 = get_clip_frame_smooth(clips, "m3_ph_microbe_lab", max(0.0, t - 9.90),  target_span=5.4)
            w3 = get_clip_frame_smooth(clips, "m4_long_treatment", max(0.0, t - 14.90), target_span=3.0)
            deck_warn = [
                build_live_playing_card(w1, 720, 490, "01", "CHỈ LO KHI ĐÃ NGỨA • CÓ MÙI",     "coral",    (255, 165, 122)),
                build_live_playing_card(w2, 720, 490, "02", "MẤT CÂN BẰNG • VI KHUẨN & NẤM",  "sapphire", (136, 215, 255)),
                build_live_playing_card(w3, 720, 490, "03", "ĐIỀU TRỊ MẤT NHIỀU THỜI GIAN",    "gold",     (252, 225, 129)),
            ]
            render_3d_playing_card_deck(
                base_im, deck_warn, t, 5.28, 17.68,
                focus_schedule=[(5.28, 0), (10.12, 1), (15.14, 2)],
                fan_hold_until=6.22, cy_base=365.0
            )

        # EMPHASIS LOCKUP #1 (17.72 - 20.92s): Editorial Bling Quote ("Phòng ngừa luôn dễ hơn điều trị!")
        if 17.70 <= t < 20.94:
            ui, uo, op, sig = ae_in_out(t, 17.72, 20.92, d_in=0.44, d_out=0.38, overshoot=1.12)
            eb_phil = get_editorial_bling_banner("Quan niệm chăm sóc khoa học", "PHÒNG NGỪA LUÔN DỄ HƠN", "ĐIỀU TRỊ!", "CHỦ ĐỘNG BẢO VỆ MỖI NGÀY TỪ SỚM", pal_hero="gold")
            paste_3d_smooth(base_im, eb_phil, 540.0, 345.0 + (1.0 - ui) * (-30.0), scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), rx_deg=(1.0 - ui) * 10.0, opacity=op, dof_sigma=sig)
            draw_bling_sparkles(base_im, [(155, 250, 0.72), (925, 265, 0.78), (885, 425, 0.65)], t - 17.72, opacity=op)

        # TYPE 3 (20.94 - 26.94s): Asymmetric 2-Column Luxury Bento Comparison
        if 20.94 <= t < 26.94:
            render_bento_comparison_duo(base_im, rv_cut, vd_cut, t, 20.94, 26.94)

        # Brief Lead Card (26.96 - 28.65s) before Romance VIP Cutaway
        if 26.96 <= t < 28.80:
            ui, uo, op, sig = ae_in_out(t, 26.98, 28.75, d_in=0.38, d_out=0.32, overshoot=1.10)
            eb_rv = get_editorial_bling_banner("Giải pháp chăm sóc hằng ngày", "DUNG DỊCH VỆ SINH ROMANCE VIP", "", "DỊU NHẸ • TỰ NHIÊN • CHUẨN pH SINH LÝ", pal_hero="rose_satin")
            paste_3d_smooth(base_im, eb_rv, 540.0, 335.0 + (1.0 - ui) * (-26.0), scale=0.90 + 0.10 * ui, opacity=op, dof_sigma=sig)

        # TYPE 4B (31.60 - 40.14s): Apple Liquid-Glass 4-Botanical Orbital Arc!
        if 31.60 <= t < 40.14:
            render_botanical_orbital_arc(base_im, imgs, t, 31.60, 40.14)

        # TYPE 5 (40.16 - 45.62s): Animated Physiological pH 3.8-4.5 Gauge + Staggered 3-Tick Checklist!
        if 40.16 <= t < 45.62:
            render_ph_gauge_and_checklist(base_im, t, 40.16, 45.62)

        # Symptom Triage Banner (45.64 - 50.35s): Architectural Warning Lockup
        if 45.64 <= t < 50.38:
            ui, uo, op, sig = ae_in_out(t, 45.66, 50.34, d_in=0.44, d_out=0.38, overshoot=1.10)
            eb_sym = get_editorial_bling_banner("Khi vùng kín có dấu hiệu mất cân bằng", "NGỨA • KHÍ HƯ BẤT THƯỜNG", "MÙI KHÓ CHỊU", "CẦN KẾT HỢP CHĂM SÓC & PHỤC HỒI CHUYÊN SÂU", pal_hero="coral")
            paste_3d_smooth(base_im, eb_sym, 540.0, 340.0 + (1.0 - ui) * (-28.0), scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), opacity=op, dof_sigma=sig)

        # TYPE 6B (53.58 - 68.68s): 4-Active Pharmaceutical Playing-Card Fan -> Push 01..04 -> Re-Fan All 4!
        if 53.58 <= t < 68.68:
            z_kb = 1.01 + 0.05 * ((t - 53.58) / 15.1)
            deck_act = [
                build_live_playing_card(imgs["act_01_lactic"],          680, 470, "01", "ACID LACTIC • CÂN BẰNG pH",      "sapphire", (136, 215, 255), zoom=z_kb),
                build_live_playing_card(imgs["act_02_trinhnu"],         680, 470, "02", "TRINH NỮ HOÀNG CUNG",            "emerald",  ( 96, 230, 184), zoom=z_kb),
                build_live_playing_card(imgs["act_03_licorice"],        680, 470, "03", "CHIẾT XUẤT CAM THẢO DỊU DA",     "gold",     (252, 225, 129), zoom=z_kb),
                build_live_playing_card(imgs["act_04_niacin_glycerin"], 680, 470, "04", "NIACINAMIDE & GLYCERIN DƯỠNG ẨM","rose_satin",(255, 168, 214), zoom=z_kb),
            ]
            render_3d_playing_card_deck(
                base_im, deck_act, t, 53.58, 68.68,
                focus_schedule=[(53.58, 0), (56.68, 1), (57.96, 2), (63.55, 3)],
                fan_hold_until=54.62, refan_from=65.58, cy_base=365.0
            )

        # TYPE 7A (68.70 - 72.78s): Wide 3D Cinema Card of Exact Dual-Product Muse Video!
        if 68.70 <= t < 72.78:
            ui, uo, op, sig = ae_in_out(t, 68.72, 72.76, d_in=0.48, d_out=0.40, overshoot=1.10)
            vf_duo = get_clip_frame_smooth(clips, "m5_duo_exact_synergy", t - 68.70, target_span=4.1)
            c_duo = build_live_playing_card(vf_duo, 860, 484, "HT", "BỘ ĐÔI CHĂM SÓC VÙNG KÍN TOÀN DIỆN • HẰNG THU", "gold", (252, 225, 129))
            paste_3d_smooth(base_im, c_duo, 540.0, 350.0 + (1.0 - ui) * (-30.0), scale=(0.88 + 0.12 * ui) * (0.94 + 0.06 * uo), rx_deg=(1.0 - ui) * 8.0, opacity=op, dof_sigma=sig)

        # TYPE 7B (72.80 - 79.68s): Floating Left/Right Synergy Brackets above her two hands holding both real boxes!
        if 72.80 <= t < 79.68:
            render_synergy_dual_brackets(base_im, t, 72.80, 79.68)

        # TYPE 7D (86.75 - 91.06s): Luxury Editorial Bling Finale Lockup + 4-Point Sparkles!
        if t >= 86.72:
            ui, uo, op, sig = ae_in_out(t, 86.75, 91.04, d_in=0.50, d_out=0.38, overshoot=1.10)
            eb_fin = get_editorial_bling_banner("Nền tảng vững chắc cho phái đẹp", "SỨC KHỎE VÀ HẠNH PHÚC", "LÂU DÀI!", "CHĂM SÓC KHOA HỌC CÙNG HẰNG THU PHARMA", pal_hero="gold")
            paste_3d_smooth(base_im, eb_fin, 540.0, 345.0 + (1.0 - ui) * (-28.0), scale=0.90 + 0.10 * ui, rx_deg=(1.0 - ui) * 8.0, opacity=op, dof_sigma=sig)
            draw_bling_sparkles(base_im, [(148, 250, 0.78), (932, 260, 0.82), (205, 435, 0.65), (885, 428, 0.72)], t - 86.75, opacity=op)

        # ==================================================================
        # 2. RE-COMPOSITE PHARMACIST + HELD BOXES + DESK BOXES IN FOREGROUND!
        # ==================================================================
        fg_alpha = np.maximum(m_arr, lower_body_box_guard)
        comp_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # ==================================================================
        # 3. FOREGROUND DIVERSE EMPHASIS TYPOGRAPHY WIDGETS!
        #    ("text nhấn cũng vậy. fort chữ đẹp mắt")
        # ==================================================================
        # A. Opening Editorial Serif + Bling Hook Lockup (0.04 - 2.16s)
        if 0.04 <= t <= 2.16:
            ui_h, uo_h, op_h, sig_h = ae_in_out(t, 0.04, 2.16, d_in=0.34, d_out=0.28, overshoot=1.14)
            sheen_hk = -0.2 + 1.45 * clamp01((t - 0.12) / 1.5)
            sp_lead = render_5stop_grad_sprite("Đừng đợi đến khi viêm", FONT_SERIF_ITAL, 44, palette="pearl", stroke_col=(12, 16, 28), stroke_w=6, extrude_dy=2, shadow_alpha=95, glow_alpha=0)[0]
            paste_3d_smooth(comp_im, sp_lead, 540.0, 295.0 + (1.0 - ui_h) * (-24.0), scale=(0.88 + 0.12 * ui_h) * (0.94 + 0.06 * uo_h), opacity=op_h, dof_sigma=sig_h)
            if t >= 0.68:
                ui2, _, op2, sig2 = ae_in_out(t, 0.68, 2.16, d_in=0.34, d_out=0.28, overshoot=1.16)
                sp_main = apply_sheen_sweep(
                    render_5stop_grad_sprite("MỚI CHĂM SÓC!", FONT_SERIF_HERO, 68, palette="gold", stroke_col=(12, 16, 28), stroke_w=8, extrude_col=(6, 10, 18), extrude_dy=4, shadow_alpha=115, glow_alpha=65),
                    sheen_hk
                )
                paste_3d_smooth(comp_im, sp_main, 540.0, 382.0 + (1.0 - ui2) * 24.0, scale=(0.86 + 0.14 * ui2) * (0.94 + 0.06 * uo_h), rx_deg=(1.0 - ui2) * 12.0, opacity=op2, dof_sigma=max(sig2, sig_h))
                draw_bling_sparkles(comp_im, [(215, 345, 0.78), (868, 355, 0.85)], t - 0.68, opacity=op2)

        # B. Tilted Condensed Architectural Stamp Ribbons on Key Vocal Contrasts!
        stamp_cues = [
            ( 7.82, 10.05, "!", "CHỜ ĐẾN KHI NGỨA • CÓ MÙI • KHÍ HƯ!", "coral",   (255, 165, 122), 540.0,  66.0, -1.5),
            (25.12, 26.92, "≠", "2 VIỆC HOÀN TOÀN KHÁC NHAU!",         "gold",    (252, 225, 129), 540.0, 566.0, -2.0),
            (38.60, 40.12, "+", "LÀM SẠCH DỊU NHẸ • KHÔNG GÂY KHÔ RÁT","rose_satin",(255, 168, 214), 540.0,  66.0,  0.0),
            (61.45, 65.48, "pH","CÂN BẰNG ĐỘ pH • NIACINAMIDE & GLYCERIN","sapphire",(136, 215, 255),540.0,  66.0,  0.0),
            (65.56, 68.62, "+", "LÀM DỊU • DƯỠNG ẨM • BẢO VỆ NIÊM MẠC", "emerald", ( 96, 230, 184), 540.0,  66.0,  0.0),
        ]
        for cst, cen, cico, ctxt, cpal, crim, ccx, ccy, crz in stamp_cues:
            if cst <= t < cen:
                uic, uoc, opc, sigc = ae_in_out(t, cst, cen, d_in=0.34, d_out=0.30, overshoot=1.15)
                stm = get_angled_stamp_ribbon(cico, ctxt, palette=cpal, rim_rgb=crim)
                paste_3d_smooth(comp_im, stm, ccx, ccy + (1.0 - uic) * (-22.0), scale=(0.86 + 0.14 * uic) * (0.94 + 0.06 * uoc), rz_deg=crz, opacity=opc, dof_sigma=sigc)

        # ==================================================================
        # 4. INTERLEAVED OPTICAL BLOOM LUXURY CUTAWAYS + LIVE 3D SPEAKER PIP!
        # ==================================================================
        in_cutaway = False
        cutaways = [
            # Cutaway 1: Exact Romance VIP Luxury Showcase (28.60 - 31.58s)
            (28.55, 31.60, "p1_romance_vip_showcase", "daily_product"),
            # Cutaway 2: Exact Viên Đặt Phụ Khoa Hằng Thu Hộp 10 Viên Showcase (50.32 - 53.56s)
            (50.30, 53.58, "p2_viendat_exact_showcase", "deep_product"),
            # Cutaway 3: Full 9:16 Radiant Woman Lifestyle Cutaway (79.90 - 86.72s)
            (79.88, 86.74, "m6_radiant_confidence_916", "lifestyle_916"),
        ]
        for cst, cen, ckey, cmode in cutaways:
            if cst <= t <= cen:
                u_in_c  = septic_smooth(clamp01((t - cst) / 0.48))
                u_out_c = septic_smooth(clamp01((cen - t) / 0.48))
                u_cut = min(u_in_c, u_out_c)
                if u_cut > 0.005:
                    in_cutaway = (u_cut > 0.5)
                    vf_c = get_clip_frame_smooth(clips, ckey, max(0.0, t - cst), target_span=(cen - cst))
                    if cmode == "lifestyle_916":
                        cut_im = fit_cover_subpixel(vf_c, W, H, zoom=1.01 + 0.03 * clamp01((t - cst) / (cen - cst))).convert("RGBA")
                        ui_s, _, op_s, sig_s = ae_in_out(t, cst + 0.22, cen - 0.18, d_in=0.45, d_out=0.38)
                        shdr = get_script_editorial_header("Phụ nữ mình ơi...", "YÊU THƯƠNG TỪ ĐIỀU NHỎ NHẤT", "TỰ TIN • KHỎE MẠNH • RẠNG RỠ MỖI NGÀY")
                        paste_3d_smooth(cut_im, shdr, 540.0, 228.0 + (1.0 - ui_s) * (-26.0), scale=0.90 + 0.10 * ui_s, opacity=op_s, dof_sigma=sig_s)
                    else:
                        # Luxury Product Showcase Stage: crisp 16:9 product showcase hero card on upper 62% + blurred matching studio backdrop!
                        bg_blur = fit_cover_subpixel(vf_c, W, H, zoom=1.18).filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
                        dark_ov = Image.new("RGBA", (W, H), (12, 14, 24, 92))
                        cut_im = Image.alpha_composite(bg_blur, dark_ov)
                        ui_p, _, op_p, sig_p = ae_in_out(t, cst + 0.15, cen - 0.12, d_in=0.42, d_out=0.34, overshoot=1.08)
                        if cmode == "daily_product":
                            pcard = build_live_playing_card(vf_c, 984, 620, "01", "DUNG DỊCH VỆ SINH PHỤ NỮ ROMANCE VIP • HẰNG THU", "rose_satin", (255, 172, 218), zoom=1.01)
                            btag  = get_editorial_bling_banner("Chăm sóc dịu nhẹ mỗi ngày", "ROMANCE VIP", "", "HOA HỒNG • TRÀ XANH • LÔ HỘI • VITAMIN E & COLLAGEN", pal_hero="rose_satin")
                        else:
                            pcard = build_live_playing_card(vf_c, 984, 620, "02", "VIÊN ĐẶT PHỤ KHOA HẰNG THU • HỘP 10 VIÊN", "emerald", (96, 230, 184), zoom=1.01)
                            btag  = get_editorial_bling_banner("Chăm sóc & phục hồi chuyên sâu", "VIÊN ĐẶT HẰNG THU", "", "ACID LACTIC • TRINH NỮ HOÀNG CUNG • CAM THẢO", pal_hero="emerald")
                        paste_3d_smooth(cut_im, btag,  540.0, 235.0 + (1.0 - ui_p) * (-24.0), scale=0.90 + 0.10 * ui_p, opacity=op_p, dof_sigma=sig_p)
                        paste_3d_smooth(cut_im, pcard, 540.0, 765.0 + (1.0 - ui_p) * 28.0,    scale=0.92 + 0.08 * ui_p, rx_deg=2.0, opacity=op_p, dof_sigma=sig_p)

                    pip = make_live_speaker_pip(fg_rgb, 232, 306)
                    paste_3d_smooth(cut_im, pip, 902.0, 1435.0, scale=0.96, ry_deg=-8.0, rz_deg=1.5, opacity=min(1.0, u_cut * 1.25))
                    comp_im = optical_soft_transition(comp_im, cut_im, u_cut)
                break

        # ==================================================================
        # 5. 100% BOX-SAFE MULTI-FONT KEYFRAMED SUBTITLES (y = 1668..1738)
        # ==================================================================
        comp_im.alpha_composite(bot_scrim, dest=(0, H - scrim_h))

        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in  = t - g["t0"]
                dt_out = g["t1"] - t
                u_g_out  = septic_smooth(min(1.0, dt_out / 0.18))
                dy_g_out = -(1.0 - septic_smooth(min(1.0, dt_out / 0.24))) * 12.0
                sc_g_out = 0.94 + 0.06 * septic_smooth(min(1.0, dt_out / 0.24))
                sig_out  = (1.0 - u_g_out) * 1.1

                min_x, max_x, x_center = 44.0, 1036.0, 540.0
                cap_sz_base = 50.0
                y_base = 1672.0 if len(g["lines"]) >= 2 else 1706.0
                lh = 64.0
                max_w_ok = max_x - min_x
                gap = 18.0
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
                        # Smooth vocal-stress scale keyframe pop right when speaker pronounces this word!
                        if ws - 0.04 <= t <= we + 0.22:
                            u_wp = clamp01((t - (ws - 0.04)) / 0.14)
                            act_pulse = 1.0 + 0.095 * math.sin(min(1.0, u_wp) * (math.pi * 0.65))
                            is_active = True
                        else:
                            act_pulse = 1.0
                            is_active = False

                        # Luxury Multi-Font Pairing: Fraunces-Bold for highlighted keywords + PlusJakartaSans-ExtraBold for crisp body!
                        if wtxt in GOLD_W:
                            pal, f_use, k = "gold", FONT_SERIF_BOLD, 1.08
                        elif wtxt in ROSE_W:
                            pal, f_use, k = "rose_satin", FONT_SERIF_BOLD, 1.08
                        elif wtxt in EMERALD_W:
                            pal, f_use, k = "emerald", FONT_SERIF_BOLD, 1.07
                        elif wtxt in CORAL_W:
                            pal, f_use, k = "coral", FONT_SUB_MAIN, 1.06
                        else:
                            pal, f_use, k = ("gold" if is_active else "pearl"), FONT_SUB_BOLD, 1.0

                        sz_use = cap_sz_base * k
                        sp_tup = render_5stop_grad_sprite(
                            wtxt, f_use, sz_use, palette=pal,
                            stroke_col=(10, 14, 24), stroke_w=7,
                            extrude_col=(6, 8, 16), extrude_dy=3,
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

        # 6. Closing Brand Ribbon (87.0 - 91.0s) + Legal Bar
        if 87.00 <= t <= 91.02:
            ui_c, uo_c, op_c, sig_c = ae_in_out(t, 87.00, 91.02, d_in=0.45, d_out=0.36)
            paste_3d_smooth(comp_im, cta_ribbon, 540.0, 1824.0 + (1.0 - ui_c) * 18.0, scale=(0.90 + 0.10 * ui_c) * (0.94 + 0.06 * uo_c), opacity=op_c, dof_sigma=sig_c)

        bar_bot = Image.new("RGBA", (W, 42), (10, 14, 24, 185))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 42))
        paste_3d_smooth(comp_im, legal_sp, 540.0, H - 21.0, scale=1.0, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"ddvs2_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/2732 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close(); writer.wait()
    reader_a.close()
    reader_m.stdout.close(); reader_m.wait()

    if test_mode and test_saved:
        imgs_t = [Image.open(p).resize((300, 533), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (300 * 4, 533 * 3))
        for i, im in enumerate(imgs_t[:12]):
            grid.paste(im, ((i % 4) * 300, (i // 4) * 533))
        gp = os.path.join(CHECK_DIR, "ddvs2_master_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved 12-panel ddvs2_master_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM DDVS 2 Master video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
