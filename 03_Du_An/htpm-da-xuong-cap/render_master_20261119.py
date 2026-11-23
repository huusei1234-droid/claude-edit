import json, math, os, re, subprocess, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter1d
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR   = r"d:\AI\full studio\output\htpm-20261119"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
OV4K_DIR   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k"
FONTS_DIR  = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FCP_MOV    = os.path.join(PROJ_DIR, "fcp_ae_overlays.mov")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

# Upgraded Clean Luxury Editorial Font System ("kiếm font chữ khác phù hợp hơn, viền mảnh")
FONT_SUB_MAIN  = os.path.join(FONTS_DIR, "PlusJakartaSans-Bold.ttf")
FONT_CARD_LBL  = os.path.join(FONTS_DIR, "PlusJakartaSans-ExtraBold.ttf")
FONT_HERO_SANS = os.path.join(FONTS_DIR, "Montserrat-Bold.ttf")
FONT_CONDENSED = os.path.join(FONTS_DIR, "Oswald-SemiBold.ttf")
FONT_LEGAL     = os.path.join(FONTS_DIR, "PlusJakartaSans-SemiBold.ttf")

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

def ae_in_out(t, st, en, d_in=0.44, d_out=0.38, overshoot=1.07):
    if t <= st or t >= en:
        return 0.0, 0.0, 0.0, 0.0
    raw_in  = clamp01((t - st) / max(0.06, d_in))
    raw_out = clamp01((en - t) / max(0.06, d_out))
    u_in    = ease_out_back_soft(raw_in, overshoot=overshoot)
    u_out   = septic_smooth(raw_out)
    op      = min(quintic_smooth(min(1.0, raw_in * 1.38)), u_out)
    sigma   = (1.0 - quintic_smooth(raw_in)) * 2.8 + (1.0 - u_out) * 2.4
    return u_in, u_out, op, sigma

# ======================================================================
# 1. PURPOSEFUL CAMERA KEYFRAME RIG ("key frame ra vô để nhấn nhá những câu nhấn")
#    Zero sine oscillation — 100% rock-steady holds between smooth septic zoom transitions!
# ======================================================================
CAM_KEYFRAMES = [
    ( 0.00, 1.000,  0.000,  0.000, 0.35),
    ( 0.12, 1.095,  0.000, -0.015, 0.55),  # Hook punch-in: "Tại sao da càng ngày càng xuống cấp?"
    ( 2.36, 1.000,  0.000,  0.000, 0.58),  # Pull out wide for Extra-Large Overlays (2.90 - 21.05s)
    (21.12, 1.052,  0.000, -0.008, 0.62),  # Gentle push-in: "Thật ra đây là tình trạng chị gặp rất nhiều..."
    (27.68, 1.115,  0.000, -0.018, 0.56),  # Emphasis punch-in: "Nhưng thực tế mỹ phẩm chỉ là một phần rất nhỏ. Một làn da đẹp trước hết phải là một làn da khỏe!"
    (33.28, 1.048,  0.000, -0.008, 0.62),  # Ease mid-shot: "Mà để khỏe thì da phải chịu được ảnh hưởng của nhiều yếu tố:"
    (36.32, 1.000,  0.000,  0.000, 0.56),  # Pull out wide for Large 4-Factor & White Skin Carousel (36.80 - 46.08s)
    (46.08, 1.110,  0.000, -0.017, 0.58),  # Emphasis punch-in: "Nếu chỉ chăm chăm thay mỹ phẩm... rất khó để cải thiện bền vững."
    (52.28, 1.062,  0.000, -0.010, 0.60),  # Mid reframe: "Chị luôn nói với mọi người rằng da cũng giống như sức khỏe của mình vậy."
    (55.65, 1.000,  0.000,  0.000, 0.55),  # Pull out wide for Large 3-Card Lifestyle Bento (56.16 - 60.45s)
    (60.44, 1.102,  0.000, -0.016, 0.54),  # Emphasis punch-in: "Thì làn da sẽ là nơi phản ánh điều đó đầu tiên!"
    (68.60, 1.000,  0.000,  0.000, 0.50),  # Wide return from cutaway for Dual Real-Photo Bento (68.86 - 71.90s)
    (71.90, 1.108,  0.000, -0.017, 0.58),  # Finale punch-in: "Khi giải quyết đúng nguyên nhân thì việc chăm sóc da mới trở nên thật sự hiệu quả."
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

# ======================================================================
# 2. 3D PERSPECTIVE + MOTION BLUR + SCREEN OVERLAY ENGINE
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

def blend_screen_overlay(rgba_im, ov_rgb, strength=0.26):
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
# 3. REFINED THIN-STROKE LUXURY GRADIENT TYPOGRAPHY ("viền mảnh thanh thoát")
# ======================================================================
_thin_text_cache = {}
def render_clean_grad_text(text, font_path, size, palette="pearl", stroke_w=2, shadow_alpha=135):
    """
    Ultra-sleek 2-Layer Thin-Stroke + Soft Ambient Drop-Shadow + 5-Stop Gradient Fill!
    Uses a refined 1.5–2.5px dark hairline outline (ZERO thick cartoon border!) so Plus Jakarta Sans
    looks effortless, modern, and razor-sharp over both dark wood and white blazer.
    """
    eff_sw = max(1, min(stroke_w, 3))
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

    # Soft diffused ambient drop shadow for high contrast without heavy border
    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 1, oy + 4), text, font=font, fill=255, stroke_width=eff_sw + 1, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=6.0)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (8, 10, 18)
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    # Hairline thin dark rim (2px max!)
    if eff_sw > 0:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(14, 16, 26, 226), stroke_width=eff_sw, stroke_fill=(14, 16, 26, 226))
        base = Image.alpha_composite(base, st_im)

    # Interior 5-stop gradient fill
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

    if len(_thin_text_cache) > 1200:
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

# ======================================================================
# 4. EXTRA-LARGE MULTI-STYLE OVERLAY SYSTEMS ("cái lớp phủ to hơn xíu")
# ======================================================================
def make_diagonal_split_rgb(vf_l, vf_r, pw, ph, u_l=1.0, u_r=1.0):
    im_l = fit_cover_subpixel(vf_l, pw, ph, zoom=1.06, pan_x=+0.12 + (1.0 - u_l) * 0.05)
    im_r = fit_cover_subpixel(vf_r, pw, ph, zoom=1.06, pan_x=-0.12 - (1.0 - u_r) * 0.05)
    yy, xx = np.ogrid[0:ph, 0:pw]
    diag = (xx.astype(np.float32) - pw * 0.50) + (yy.astype(np.float32) - ph * 0.50) * 0.22
    w_r = np.clip((diag + 16.0) / 32.0, 0.0, 1.0)[:, :, None]
    return (np.array(im_l, dtype=np.float32) * (1.0 - w_r) + np.array(im_r, dtype=np.float32) * w_r).astype(np.uint8)

def render_large_cinema_window(canvas_im, vf_l, vf_r, t, st, en, lbl_l, lbl_r="", pal_l="pearl", pal_r="coral", cy=442.0):
    """Extra-Large 1016x616 Cinema Window (94% of screen width!)"""
    ui, uo, op, sig = ae_in_out(t, st, en, d_in=0.46, d_out=0.38, overshoot=1.07)
    if op <= 0.008:
        return
    pw, ph, pad = 1016, 616, 22
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + pw, pad + ph + 12], radius=40, fill=(10, 12, 24, 134))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    if vf_r is not None:
        u_l = septic_smooth(clamp01((t - st) / 0.48))
        u_r = septic_smooth(clamp01((t - st - 0.12) / 0.48))
        comp_rgb = make_diagonal_split_rgb(vf_l, vf_r, pw, ph, u_l, u_r)
        vis_im = Image.fromarray(comp_rgb, "RGB")
    else:
        u_z = septic_smooth(clamp01((t - st) / max(0.8, en - st)))
        vis_im = fit_cover_subpixel(vf_l, pw, ph, zoom=1.02 + 0.05 * u_z)

    rmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=40, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(vis_im, (pad, pad), mask=rmask)
    card = Image.alpha_composite(card, vl)

    d = ImageDraw.Draw(card)
    if vf_r is not None:
        x_top = pad + pw * 0.50 - (-ph * 0.50) * 0.22
        x_bot = pad + pw * 0.50 - (+ph * 0.50) * 0.22
        d.line([(x_top, pad + 3), (x_bot, pad + ph - 3)], fill=(255, 232, 152, 248), width=4)
        for lx, ltxt, lpal in [(pad + 252, lbl_l, pal_l), (pad + pw - 252, lbl_r, pal_r)]:
            d.rounded_rectangle([lx - 212, pad + 18, lx + 212, pad + 66], radius=24, fill=(16, 18, 32, 226), outline=(252, 225, 129, 205), width=2)
            sp, _ = render_clean_grad_text(ltxt, FONT_CARD_LBL, 20, palette=lpal, stroke_w=2, shadow_alpha=45)
            paste_3d_smooth(card, sp, lx, pad + 42)
    else:
        d.rounded_rectangle([pad + 24, pad + 18, pad + 560, pad + 68], radius=25, fill=(16, 18, 32, 228), outline=(255, 174, 112, 215), width=2)
        sp, _ = render_clean_grad_text(lbl_l, FONT_CARD_LBL, 21, palette=pal_l, stroke_w=2, shadow_alpha=45)
        paste_3d_smooth(card, sp, pad + 292, pad + 43)

    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=40, outline=(252, 225, 129, 244), width=3)
    paste_3d_smooth(
        canvas_im, card,
        540.0, cy + (1.0 - ui) * (-26.0) - (1.0 - uo) * 18.0,
        scale=(0.91 + 0.09 * ui) * (0.94 + 0.06 * uo),
        rx_deg=(1.0 - ui) * 6.5, opacity=op, dof_sigma=sig
    )

_card_shell_cache = {}
def build_large_playing_card(vf_rgb, w, h, idx_str, title_str, palette="gold", rim_rgb=(252, 225, 129), zoom=1.02):
    k = (w, h, idx_str, title_str, palette, rim_rgb)
    if k not in _card_shell_cache:
        pad = 24
        cw, ch = w + pad * 2, h + pad * 2
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius=36, fill=(10, 12, 24, 132))
        sh = sh.filter(ImageFilter.GaussianBlur(radius=14))
        rmask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, w - 1, h - 1], radius=36, fill=255)

        overlay = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        vy = np.linspace(1.0, 0.0, 92, dtype=np.float32)[:, None]
        ha = np.zeros((92, w, 4), dtype=np.uint8)
        ha[:, :, 0], ha[:, :, 1], ha[:, :, 2] = (14, 16, 28)
        ha[:, :, 3] = (vy * 222.0).astype(np.uint8)
        overlay.paste(Image.fromarray(ha, "RGBA"), (pad, pad), mask=rmask.crop((0, 0, w, 92)))

        d = ImageDraw.Draw(overlay)
        d.rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius=36, outline=(*rim_rgb, 245), width=3)
        d.rounded_rectangle([pad + 5, pad + 5, pad + w - 6, pad + h - 6], radius=31, outline=(255, 255, 255, 110), width=1)
        d.rounded_rectangle([pad + 18, pad + 16, pad + 82, pad + 58], radius=16, fill=(22, 20, 38, 238), outline=(*rim_rgb, 228), width=2)
        sp_idx, _ = render_clean_grad_text(idx_str, FONT_HERO_SANS, 23, palette=palette, stroke_w=2, shadow_alpha=0)
        sp_ic = sp_idx.crop(sp_idx.getbbox())
        overlay.alpha_composite(sp_ic, dest=(pad + 50 - sp_ic.width // 2, pad + 37 - sp_ic.height // 2))

        sp_t, _ = render_clean_grad_text(title_str, FONT_CARD_LBL, 22, palette="pearl", stroke_w=2, shadow_alpha=65)
        sp_tc = sp_t.crop(sp_t.getbbox())
        max_tw = w - 114
        if sp_tc.width > max_tw:
            nh = max(12, int(round(sp_tc.height * (max_tw / float(sp_tc.width)))))
            sp_tc = sp_tc.resize((max_tw, nh), Image.Resampling.LANCZOS)
        overlay.alpha_composite(sp_tc, dest=(pad + 96, pad + 37 - sp_tc.height // 2))
        _card_shell_cache[k] = (sh, rmask, overlay, pad)

    sh, rmask, overlay, pad = _card_shell_cache[k]
    card = sh.copy()
    vlay = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    vlay.paste(fit_cover_subpixel(vf_rgb, w, h, zoom=zoom), (pad, pad), mask=rmask)
    return Image.alpha_composite(Image.alpha_composite(card, vlay), overlay)

def render_3d_playing_card_deck(canvas_im, card_sprites, t, st, en, focus_schedule, fan_hold_until=None, cy_base=446.0):
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
        # LARGER focused card scale = 0.98 on 864x576 -> 847px wide!
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

    draw_queue.sort(key=lambda x: x[0])
    for pz, i, px, py, psc, prx, pry, prz, pdim, pdof, mb_x in draw_queue:
        paste_3d_smooth(canvas_im, card_sprites[i], px, py, scale=psc, rx_deg=prx, ry_deg=pry, rz_deg=prz, opacity=op_deck, dof_sigma=pdof, mb_dx=mb_x, dim=pdim)

def render_large_dual_product_bento(canvas_im, cut_open, cut_caps, t, st, en):
    """Extra-Large Dual Real-Photo Product & Root-Cause Bento (496x500 x 2 = 1016px total span!)"""
    if t <= st or t >= en:
        return
    pw, ph, pad = 496, 500, 20
    cw, ch = pw + pad * 2, ph + pad * 2

    ui1, uo1, op1, sig1 = ae_in_out(t, st, en, d_in=0.44, d_out=0.36, overshoot=1.07)
    c1 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(c1)
    d1.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=38, fill=(14, 24, 42, 236), outline=(132, 224, 255, 244), width=3)
    s_t1, _ = render_clean_grad_text("01 • THẤU HIỂU LÀN DA", FONT_CONDENSED, 24, palette="sapphire", stroke_w=2, shadow_alpha=0)
    paste_3d_smooth(c1, s_t1, cw * 0.5, pad + 38)
    if cut_open is not None:
        th1 = cut_open.copy()
        th1.thumbnail((370, 245), Image.Resampling.LANCZOS)
        c1.alpha_composite(th1, dest=(int(cw * 0.5 - th1.width * 0.5), pad + 195 - th1.height // 2))
    for li, ln in enumerate(["TÌM ĐÚNG VẤN ĐỀ", "& NGUYÊN NHÂN GỐC"]):
        sh1, _ = render_clean_grad_text(ln, FONT_HERO_SANS, 26, palette="sapphire" if li == 1 else "pearl", stroke_w=2, shadow_alpha=65)
        paste_3d_smooth(c1, sh1, cw * 0.5, pad + 365 + li * 42)
    paste_3d_smooth(canvas_im, c1, 276.0 - (1.0 - ui1) * 58.0, 442.0, scale=(0.90 + 0.10 * ui1) * (0.94 + 0.06 * uo1), ry_deg=6.5, rz_deg=-1.0, opacity=op1, dof_sigma=sig1)

    if t >= st + 0.35:
        ui2, uo2, op2, sig2 = ae_in_out(t, st + 0.35, en, d_in=0.44, d_out=0.36, overshoot=1.07)
        c2 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(c2)
        d2.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=38, fill=(14, 30, 32, 236), outline=(118, 242, 198, 244), width=3)
        s_t2, _ = render_clean_grad_text("02 • NUÔI DƯỠNG BÊN TRONG", FONT_CONDENSED, 24, palette="emerald", stroke_w=2, shadow_alpha=0)
        paste_3d_smooth(c2, s_t2, cw * 0.5, pad + 38)
        if cut_caps is not None:
            th2 = cut_caps.copy()
            th2.thumbnail((370, 245), Image.Resampling.LANCZOS)
            c2.alpha_composite(th2, dest=(int(cw * 0.5 - th2.width * 0.5), pad + 195 - th2.height // 2))
        for li, ln in enumerate(["ĐIỀU HÒA NỘI TIẾT", "LEGEND WHITE SKIN"]):
            sh2, _ = render_clean_grad_text(ln, FONT_HERO_SANS, 26, palette="gold" if li == 1 else "pearl", stroke_w=2, shadow_alpha=65)
            paste_3d_smooth(c2, sh2, cw * 0.5, pad + 365 + li * 42)
        paste_3d_smooth(canvas_im, c2, 804.0 + (1.0 - ui2) * 58.0, 442.0, scale=(0.90 + 0.10 * ui2) * (0.94 + 0.06 * uo2), ry_deg=-6.5, rz_deg=1.0, opacity=op2, dof_sigma=sig2)

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

def make_live_speaker_pip(fg_rgb, pw=244, ph=322):
    sub = fg_rgb[580:1480, 230:890]
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
# 5. SENTENCE-CASE + THIN-STROKE PLUS JAKARTA SANS SUBTITLES ("Viết hoa mỗi câu")
# ======================================================================
def cap_first_char(s):
    if not s:
        return s
    return s[0].upper() + s[1:]

def load_captions_clean():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and (w["start"] + w["end"]) * 0.5 >= 2.35
    ]

    CLAUSE_STARTERS = {
        "từ", "thậm", "nhưng", "có", "thật", "khi", "mọi", "một", "mà",
        "như", "hoặc", "tia", "nếu", "thì", "chị", "vì", "mình", "và"
    }

    phrases, cur_p = [], []
    for i, w in enumerate(words):
        txt, ws, we = w
        wlow = txt.lower().rstrip(",.?!:;")
        if cur_p:
            gap = ws - cur_p[-1][2]
            prev_txt = cur_p[-1][0]
            dur_so_far = cur_p[-1][2] - cur_p[0][1]
            prev_low = prev_txt.lower().rstrip(",.?!:;")
            # Never split inside compound pairs like "sản phẩm", "khác nhau", "chăm sóc", "làn da", "mỹ phẩm", "nguyên nhân"
            is_compound = (prev_low, wlow) in {
                ("sản", "phẩm"), ("khác", "nhau"), ("chăm", "sóc"), ("làn", "da"),
                ("mỹ", "phẩm"), ("nguyên", "nhân"), ("tình", "trạng"), ("nội", "tiết"),
                ("tiết", "tố"), ("môi", "trường"), ("sức", "khỏe"), ("bền", "vững"),
                ("cân", "bằng"), ("hiệu", "quả"), ("xuống", "cấp"), ("sữa", "rửa"), ("rửa", "mặt"),
                ("ảnh", "hưởng"), ("điều", "đó"), ("của", "mình"), ("chăm", "chăm"), ("thật", "sự")
            }
            if not is_compound:
                if re.search(r"[.?!…;:]$", prev_txt) or gap >= 0.38:
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
            merged
            and len(p) <= 2
            and not re.search(r"[.?!…:]$", merged[-1][-1][0])
            and (p[0][1] - merged[-1][-1][2]) < 0.35
            and len(merged[-1]) + len(p) <= 8
        ):
            merged[-1].extend(p)
        else:
            merged.append(p)

    # ENFORCE "Viết hoa mỗi câu": Capitalize ONLY the first word of EVERY subtitle clause/sentence (keep proper nouns/acronyms like UV)!
    for p in merged:
        if p:
            p[0][0] = cap_first_char(p[0][0])
            for k in range(1, len(p)):
                if re.search(r"[.?!:]$", p[k - 1][0]):
                    p[k][0] = cap_first_char(p[k][0])
                elif p[k][0] not in {"UV"} and p[k][0][:1].isupper():
                    p[k][0] = p[k][0][0].lower() + p[k][0][1:]

    def split_balanced(p):
        tot_c = sum(len(x[0]) + 1 for x in p) - 1
        if len(p) <= 4 and tot_c <= 21:
            return [p]
        bk, bd = max(1, len(p) // 2), 9999
        for k in range(1, len(p)):
            c1 = sum(len(x[0]) + 1 for x in p[:k]) - 1
            c2 = sum(len(x[0]) + 1 for x in p[k:]) - 1
            d = abs(c1 - c2) + (6 if max(c1, c2) > 23 else 0)
            if d < bd:
                bd, bk = d, k
        return [p[:bk], p[bk:]]

    ROSE_W     = {"da", "đẹp", "serum", "toner,", "kem", "dưỡng,"}
    CORAL_W    = {"xuống", "cấp", "cấp?", "mụn,", "khô", "ráp,", "xỉn", "màu,", "thức", "khuya", "căng", "thẳng", "stress", "UV"}
    EMERALD_W  = {"khỏe", "khỏe.", "bền", "vững.", "cân", "bằng,", "hiệu", "quả."}
    SAPPHIRE_W = {"nội", "tiết", "tố,", "giấc", "ngủ,", "nguyên", "nhân"}

    cap_groups = []
    for i, p in enumerate(merged):
        t0 = max(2.38, p[0][1] - 0.04)
        last_end = p[-1][2]
        nxt_s = merged[i + 1][0][1] if i + 1 < len(merged) else 76.35
        if nxt_s - last_end <= 0.95:
            t1 = nxt_s - 0.05
        else:
            t1 = min(nxt_s - 0.06, max(last_end + 0.65, t0 + 1.55))
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

def get_clip_frame_smooth(clips, key, t_rel, target_span=5.0):
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
# 6. MAIN RENDER LOOP (2,293 FRAMES = 76.44s)
# ======================================================================
def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [1.10, 6.20, 11.40, 18.40, 32.50, 37.60, 48.20, 58.60, 66.20]
    }
    if test_mode:
        test_frames.add(int(round(74.80 * FPS)))
    test_saved = []

    if not os.path.exists(FCP_MOV):
        raise FileNotFoundError(f"Missing HyperFrames overlay: {FCP_MOV}")

    aroll_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    aroll_path = aroll_graded if os.path.exists(aroll_graded) else os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vid_keys = [
        ("b01_skincare_steps",        1024, 640),
        ("b02_many_products",         1024, 640),
        ("b03_vanity_sigh",           1024, 640),
        ("b04_acne_redness",           960, 640),
        ("b05_dull_skin",              960, 640),
        ("b06_late_night_2am",         960, 640),
        ("b07_healthy_meal",           960, 640),
        ("b08_morning_water",          960, 640),
        ("b09_work_stress",            960, 640),
        ("b10_sunlight_uv",            960, 640),
        ("b11_unbalanced_diet",        960, 640),
        ("prod_ws_01_openbox",        1280, 720),
        ("prod_ws_02_multi_showcase", 1280, 720),
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

    dry_img = np.array(Image.open(os.path.join(MEDIA_DIR, "st_02_dry.jpg")).convert("RGB")) if os.path.exists(os.path.join(MEDIA_DIR, "st_02_dry.jpg")) else np.full((640, 960, 3), 215, dtype=np.uint8)
    cut_open = Image.open(os.path.join(MEDIA_DIR, "ws_cut_open.png")).convert("RGBA") if os.path.exists(os.path.join(MEDIA_DIR, "ws_cut_open.png")) else None
    cut_caps = Image.open(os.path.join(MEDIA_DIR, "ws_cut_caps.png")).convert("RGBA") if os.path.exists(os.path.join(MEDIA_DIR, "ws_cut_caps.png")) else None

    cap_groups, ROSE_W, CORAL_W, EMERALD_W, SAPPHIRE_W = load_captions_clean()

    scrim_h = 370
    sy = np.linspace(0.0, 1.0, scrim_h, dtype=np.float32)[:, None]
    sa = np.zeros((scrim_h, W, 4), dtype=np.uint8)
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (10, 12, 20)
    sa[:, :, 3] = (np.power(sy, 1.35) * 172.0).astype(np.uint8)
    bot_scrim = Image.fromarray(sa, "RGBA")

    legal_sp, _ = render_clean_grad_text(
        "Thực phẩm bảo vệ sức khỏe Hằng Thu Pharma • Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh",
        FONT_LEGAL, 16, palette="pearl", stroke_w=1, shadow_alpha=60
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

        # Purposeful Emphasis Keyframe Camera Rig (smooth ease-in/out on emphasis sentences, 0% jitter!)
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

        if ov_bokeh and ((27.6 <= t <= 36.7) or (46.0 <= t <= 56.1) or (71.8 <= t <= 76.4)):
            base_im = blend_screen_overlay(base_im, ov_bokeh[frame_idx % len(ov_bokeh)], strength=0.22)

        # ==================================================================
        # 1. EXTRA-LARGE BEHIND-SPEAKER MULTI-STYLE VISUAL OVERLAYS
        # ==================================================================
        # Scene 1A (2.88 - 8.95s): Extra-Large Diagonal Split Cinema Window (1016x616)
        if 2.88 <= t < 8.95:
            vf_l = get_clip_frame_smooth(clips, "b01_skincare_steps", t - 2.88, target_span=6.07)
            vf_r = get_clip_frame_smooth(clips, "b02_many_products",  t - 2.88, target_span=6.07)
            render_large_cinema_window(base_im, vf_l, vf_r, t, 2.90, 8.94, "SỮA RỬA MẶT • TONER • SERUM", "KEM DƯỠNG • ĐẦU TƯ NHIỀU", pal_l="sapphire", pal_r="gold", cy=442.0)

        # Scene 1B (8.95 - 13.86s): Extra-Large Single Cinema Window (1016x616)
        if 8.95 <= t < 13.86:
            vf_v = get_clip_frame_smooth(clips, "b03_vanity_sigh", t - 8.95, target_span=4.91)
            render_large_cinema_window(base_im, vf_v, None, t, 8.96, 13.85, "ĐỔI NHIỀU MỸ PHẨM NHƯNG VẪN THẤT VỌNG", pal_l="coral", cy=442.0)

        # Scene 2 (14.00 - 21.05s): Large 4-Card 3D Playing-Card Deck (864x576 per card!)
        if 14.00 <= t < 21.05:
            f_acne = get_clip_frame_smooth(clips, "b04_acne_redness",   max(0.0, t - 14.00), target_span=3.5)
            f_dry  = np.array(fit_cover_subpixel(dry_img, 960, 640, zoom=1.02 + 0.05 * clamp01((t - 15.0) / 3.0)))
            f_dull = get_clip_frame_smooth(clips, "b05_dull_skin",      max(0.0, t - 16.00), target_span=3.5)
            f_2am  = get_clip_frame_smooth(clips, "b06_late_night_2am", max(0.0, t - 17.30), target_span=3.8)
            deck_s2 = [
                build_large_playing_card(f_acne, 864, 576, "01", "CÓ LÚC NỔI MỤN & KÍCH ỨNG",           "coral",      (255, 159,  90)),
                build_large_playing_card(f_dry,  864, 576, "02", "CÓ LÚC BỀ MẶT DA KHÔ RÁP",            "gold",       (252, 225, 129)),
                build_large_playing_card(f_dull, 864, 576, "03", "CÓ LÚC DA XỈN MÀU, KÉM SỨC SỐNG",     "rose_satin", (249, 106, 181)),
                build_large_playing_card(f_2am,  864, 576, "04", "THỨC KHUYA VÀI HÔM • DA XUỐNG CẤP RÕ","sapphire",   (132, 224, 255)),
            ]
            render_3d_playing_card_deck(
                base_im, deck_s2, t, 14.00, 21.05,
                focus_schedule=[(14.00, 0), (15.32, 1), (16.42, 2), (17.56, 3)],
                fan_hold_until=14.52, cy_base=446.0
            )

        # Scene 4 (36.80 - 46.08s): Large 4-Card Holistic Factors + Real LEGEND White Skin Showcase #1!
        if 36.80 <= t < 46.08:
            f_ws1  = get_clip_frame_smooth(clips, "prod_ws_01_openbox", max(0.0, t - 36.80), target_span=4.5)
            f_meal = make_diagonal_split_rgb(
                get_clip_frame_smooth(clips, "b07_healthy_meal",  max(0.0, t - 38.40), target_span=3.2),
                get_clip_frame_smooth(clips, "b08_morning_water", max(0.0, t - 38.40), target_span=3.2),
                864, 576
            )
            f_str  = get_clip_frame_smooth(clips, "b09_work_stress", max(0.0, t - 40.20), target_span=3.5)
            f_uv   = make_diagonal_split_rgb(
                get_clip_frame_smooth(clips, "b10_sunlight_uv",    max(0.0, t - 42.80), target_span=3.5),
                get_clip_frame_smooth(clips, "b01_skincare_steps", max(0.0, t - 42.80), target_span=3.5),
                864, 576
            )
            deck_s4 = [
                build_large_playing_card(f_ws1,  864, 576, "01", "NỘI TIẾT TỐ BÊN TRONG • WHITE SKIN",   "sapphire", (132, 224, 255)),
                build_large_playing_card(f_meal, 864, 576, "02", "CHẾ ĐỘ ĂN UỐNG & GIẤC NGỦ KHOA HỌC",   "emerald",  (118, 242, 198)),
                build_large_playing_card(f_str,  864, 576, "03", "CĂNG THẲNG & ÁP LỰC KÉO DÀI",          "coral",    (255, 174, 112)),
                build_large_playing_card(f_uv,   864, 576, "04", "MÔI TRƯỜNG SỐNG, TIA UV & CHĂM SÓC DA","gold",     (252, 225, 129)),
            ]
            render_3d_playing_card_deck(
                base_im, deck_s4, t, 36.80, 46.08,
                focus_schedule=[(36.80, 0), (38.58, 1), (40.35, 2), (42.95, 3)],
                fan_hold_until=37.25, cy_base=446.0
            )

        # Scene 6A (56.16 - 60.45s): Large 3-Card Lifestyle Imbalance Deck (856x568)
        if 56.16 <= t < 60.45:
            f_l1 = get_clip_frame_smooth(clips, "b06_late_night_2am",  max(0.0, t - 56.16), target_span=4.2)
            f_l2 = get_clip_frame_smooth(clips, "b09_work_stress",     max(0.0, t - 57.50), target_span=3.2)
            f_l3 = get_clip_frame_smooth(clips, "b11_unbalanced_diet", max(0.0, t - 58.80), target_span=2.5)
            deck_s6 = [
                build_large_playing_card(f_l1, 856, 568, "01", "CƠ THỂ THIẾU NGỦ KÉO DÀI",     "sapphire", (132, 224, 255)),
                build_large_playing_card(f_l2, 856, 568, "02", "THƯỜNG XUYÊN STRESS, MỆT MỎI",  "coral",    (255, 174, 112)),
                build_large_playing_card(f_l3, 856, 568, "03", "ĂN UỐNG THIẾU CÂN BẰNG DƯỠNG CHẤT","gold",  (252, 225, 129)),
            ]
            render_3d_playing_card_deck(
                base_im, deck_s6, t, 56.16, 60.45,
                focus_schedule=[(56.16, 0), (58.00, 1), (59.25, 2)],
                fan_hold_until=56.60, cy_base=444.0
            )

        # Scene 7B (68.86 - 71.90s): Extra-Large Dual Real-Photo Cutout Bento (1016px total span!)
        if 68.86 <= t < 71.90:
            render_large_dual_product_bento(base_im, cut_open, cut_caps, t, 68.88, 71.88)

        # ==================================================================
        # 2. RE-COMPOSITE PHARMACIST IN FOREGROUND!
        # ==================================================================
        fg_alpha = np.maximum(m_arr, lower_desk_guard)
        comp_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # ==================================================================
        # 3. MULTI-ANGLE REAL-PHOTO LEGEND WHITE SKIN CUTAWAY (63.58 - 68.86s)
        # ==================================================================
        if 63.58 <= t <= 68.86:
            u_in_c  = septic_smooth(clamp01((t - 63.58) / 0.44))
            u_out_c = septic_smooth(clamp01((68.86 - t) / 0.44))
            u_cut = min(u_in_c, u_out_c)
            if u_cut > 0.005:
                vf_p = get_clip_frame_smooth(clips, "prod_ws_02_multi_showcase", max(0.0, t - 63.58), target_span=5.28)
                bg_blur = fit_cover_subpixel(vf_p, W, H, zoom=1.18).filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
                cut_im = Image.alpha_composite(bg_blur, Image.new("RGBA", (W, H), (10, 18, 32, 92)))
                ui_p, _, op_p, sig_p = ae_in_out(t, 63.66, 68.76, d_in=0.38, d_out=0.32, overshoot=1.06)
                pcard = build_large_playing_card(vf_p, 1016, 660, "HT", "VIÊN UỐNG TRẮNG DA, ĐIỀU HÒA NỘI TIẾT LEGEND WHITE SKIN", "sapphire", (132, 224, 255), zoom=1.01)
                paste_3d_smooth(cut_im, pcard, 540.0, 718.0 + (1.0 - ui_p) * 22.0, scale=0.93 + 0.07 * ui_p, rx_deg=1.2, opacity=op_p, dof_sigma=sig_p)
                if ov_sparkle:
                    cut_im = blend_screen_overlay(cut_im, ov_sparkle[frame_idx % len(ov_sparkle)], strength=0.26)
                pip = make_live_speaker_pip(fg_rgb, 244, 322)
                paste_3d_smooth(cut_im, pip, 896.0, 1395.0, scale=0.96, ry_deg=-7.5, rz_deg=1.2, opacity=min(1.0, u_cut * 1.25))
                comp_im = optical_soft_transition(comp_im, cut_im, u_cut)

        # ==================================================================
        # 4. COMPOSITE HYPERFRAMES FINAL CUT PRO & AFTER EFFECTS ALPHA LAYER!
        # ==================================================================
        comp_im.alpha_composite(bot_scrim, dest=(0, H - scrim_h))

        if fcp_rgba is not None and fcp_rgba[:, :, 3].max() > 0:
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(fcp_rgba, "RGBA"))

        if ov_flare:
            flare_str = 0.0
            for t_fl in (0.42, 30.34, 63.60, 68.84, 71.95):
                if abs(t - t_fl) < 0.44:
                    flare_str = max(flare_str, 0.30 * math.cos((t - t_fl) / 0.44 * (math.pi * 0.5)))
            if flare_str > 0.01:
                comp_im = blend_screen_overlay(comp_im, ov_flare[frame_idx % len(ov_flare)], strength=flare_str)

        # ==================================================================
        # 5. THIN-STROKE + SENTENCE-CASE PLUS JAKARTA SANS SUBTITLES (y=1668)
        # ==================================================================
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in  = t - g["t0"]
                dt_out = g["t1"] - t
                u_g_out  = septic_smooth(min(1.0, dt_out / 0.18))
                dy_g_out = -(1.0 - septic_smooth(min(1.0, dt_out / 0.24))) * 10.0
                sc_g_out = 0.95 + 0.05 * septic_smooth(min(1.0, dt_out / 0.24))
                sig_out  = (1.0 - u_g_out) * 1.0

                min_x, max_x, x_center = 48.0, 1032.0, 540.0
                cap_sz_base = 48.0
                y_base = 1668.0 if len(g["lines"]) >= 2 else 1702.0
                lh = 62.0
                max_w_ok = max_x - min_x
                gap = 14.0
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
                            act_pulse = 1.0
                            is_active = False

                        wlow = wtxt.lower()
                        if wtxt in ROSE_W or wlow in ROSE_W:
                            pal = "rose_satin"
                        elif wtxt in CORAL_W or wlow in CORAL_W:
                            pal = "coral"
                        elif wtxt in EMERALD_W or wlow in EMERALD_W:
                            pal = "emerald"
                        elif wtxt in SAPPHIRE_W or wlow in SAPPHIRE_W:
                            pal = "sapphire"
                        else:
                            pal = "gold" if is_active else "pearl"

                        # Thin refined 2px hairline outline ("viền mảnh thanh thoát")!
                        sp_tup = render_clean_grad_text(
                            wtxt, FONT_SUB_MAIN, cap_sz_base, palette=pal, stroke_w=2, shadow_alpha=140
                        )
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
            tp = os.path.join(CHECK_DIR, f"test20261119_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 250 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/2293 frames ({frame_idx / el:.1f} fps)", flush=True)

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
        gp = os.path.join(CHECK_DIR, "master_20261119_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved 10-panel master_20261119_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM Da Xuống Cấp Master video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
