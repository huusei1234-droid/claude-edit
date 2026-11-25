import json, math, os, re, subprocess, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR   = r"d:\AI\full studio\output\htpm3-kobe"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
OV4K_DIR   = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k"
FONTS_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
KOBE_MOV   = os.path.join(PROJ_DIR, "kobe_overlays.mov")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
TOTAL_FRAMES = 2367  # 78.92s

FONT_SUB_MAIN = os.path.join(FONTS_DIR, "AsapCondensed-Bold.ttf")
FONT_CARD_LBL = os.path.join(FONTS_DIR, "AsapCondensed-ExtraBold.ttf")

GRAD_PALETTES = {
    "gold": [
        (0.00, (255, 254, 245)),
        (0.30, (255, 228, 134)),
        (0.58, (230, 166,  44)),
        (1.00, (192, 124,  20)),
    ],
    "rose_satin": [
        (0.00, (255, 240, 248)),
        (0.35, (244,  76, 152)),
        (0.70, (201,  24,  96)),
        (1.00, (164,  16,  78)),
    ],
    "cobalt": [
        (0.00, (240, 246, 255)),
        (0.38, ( 88, 122, 255)),
        (0.72, ( 54,  86, 251)),
        (1.00, ( 32,  58, 198)),
    ],
    "emerald": [
        (0.00, (238, 255, 248)),
        (0.38, ( 56, 206, 152)),
        (0.72, ( 14, 152, 102)),
        (1.00, ( 10, 118,  78)),
    ],
    "coral": [
        (0.00, (255, 242, 238)),
        (0.40, (250, 112,  96)),
        (0.75, (236,  72,  58)),
        (1.00, (186,  42,  30)),
    ],
    "pearl": [
        (0.00, (255, 255, 255)),
        (0.55, (250, 252, 255)),
        (1.00, (240, 245, 255)),
    ],
}

_font_cache = {}
def get_font(path, size):
    k = (path, max(10, int(round(size))))
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, k[1])
    return _font_cache[k]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def quintic_smooth(u):
    u = clamp01(u)
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

def septic_smooth(u):
    u = clamp01(u)
    u4 = u * u * u * u
    return u4 * (35.0 + u * (-84.0 + u * (70.0 - 20.0 * u)))

def ease_out_back_soft(u, overshoot=1.06):
    u = clamp01(u) - 1.0
    return 1.0 + u * u * ((overshoot + 1.0) * u + overshoot)

# ======================================================================
# 1. PURPOSEFUL CAMERA KEYFRAME RIG (Box-Safe: max zoom 1.085 keeps all 4 desk boxes visible!)
# ======================================================================
CAM_KEYFRAMES = [
    ( 0.00, 1.000, 0.000,  0.000, 0.35),
    ( 0.12, 1.072, 0.000, -0.010, 0.52),  # Hook punch-in: "Có 5 sản phẩm mà nếu là phụ nữ sau tuổi 25..."
    ( 2.80, 1.000, 0.000,  0.000, 0.55),  # Wide for 5 Drop-Bounce Kobe Step Cards (2.85 - 6.74s)
    ( 6.80, 1.045, 0.000, -0.006, 0.58),  # Gentle push-in for SP1 Endocrine Balance
    (10.82, 1.082, 0.000, -0.012, 0.54),  # Emphasis zoom: "Một cơ thể khỏe mạnh thường bắt đầu từ sự cân bằng"
    (13.88, 1.000, 0.000,  0.000, 0.56),  # Wide for SP1B Flow Video + Energy Bar
    (20.98, 1.052, 0.000, -0.007, 0.55),  # SP2A: "Thứ hai là sản phẩm chăm sóc phụ khoa..."
    (23.72, 1.086, 0.000, -0.012, 0.48),  # Emphasis punch-in: "...đừng đợi đến khi có cảm giác khó chịu mới quan tâm!"
    (26.38, 1.000, 0.000,  0.000, 0.54),  # Wide for SP2B Flow Comfort Card
    (36.48, 1.000, 0.000,  0.000, 0.45),  # Return from SP3A Full Kobe Stage
    (37.15, 1.076, 0.000, -0.010, 0.58),  # Emphasis zoom: "Quan trọng là lựa chọn sản phẩm phù hợp & dùng đúng cách"
    (42.50, 1.000, 0.000,  0.000, 0.54),  # Wide for SP4A Inner Skin Flow Video + White Skin Cutout
    (48.55, 1.048, 0.000, -0.006, 0.56),  # Mid push-in under 1🔗2🔗3🔗4 Kobe Chain Cards
    (60.56, 1.058, 0.000, -0.008, 0.52),  # Return from SP5A Full Kobe Stage: "Việc bổ sung hợp lý theo tư vấn chuyên gia..."
    (65.96, 1.092, 0.000, -0.014, 0.52),  # Strong emphasis punch-in: "Đừng đợi cơ thể phát tín hiệu quá rõ mới bắt đầu chăm sóc!"
    (71.34, 1.042, 0.000, -0.006, 0.60),  # Graceful finale frame keeping all 4 real desk boxes prominent!
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

def paste_centered_rgba(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0, blur_sigma=0.0):
    if opacity <= 0.005 or scale <= 0.02:
        return
    im = sprite_im
    if abs(scale - 1.0) > 0.008:
        nw = max(4, int(round(im.width * scale)))
        nh = max(4, int(round(im.height * scale)))
        im = im.resize((nw, nh), Image.Resampling.BICUBIC)
    if blur_sigma >= 0.25:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(12.0, blur_sigma)))
    if opacity < 0.995:
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 3] *= clamp01(opacity)
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    dx = int(round(cx - im.width * 0.5))
    dy = int(round(cy - im.height * 0.5))
    x0, y0 = max(0, dx), max(0, dy)
    x1, y1 = min(canvas_im.width, dx + im.width), min(canvas_im.height, dy + im.height)
    if x1 > x0 and y1 > y0:
        canvas_im.alpha_composite(im.crop((x0 - dx, y0 - dy, x1 - dx, y1 - dy)), dest=(x0, y0))

# ======================================================================
# 2. KOBE SAAS VIDEO CARD + LANDING RIPPLE + THREAD-LINE + 416px IRIS CIRCLE PIP
# ======================================================================
_pill_cache = {}
def make_kobe_card_pill(tag_txt, main_txt, accent_rgb=(54, 86, 251)):
    k = (tag_txt, main_txt, accent_rgb)
    if k in _pill_cache:
        return _pill_cache[k]
    f_t = get_font(FONT_CARD_LBL, 20)
    f_m = get_font(FONT_CARD_LBL, 25)
    dm = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bt = dm.textbbox((0, 0), tag_txt, font=f_t)
    bm = dm.textbbox((0, 0), main_txt, font=f_m)
    wt = bt[2] - bt[0] + 26
    wm = bm[2] - bm[0]
    pw, ph, pad = wt + wm + 44, 52, 8
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=26, fill=(255, 255, 255, 248), outline=(255, 255, 255, 255), width=2)
    d.rounded_rectangle([pad + 12, pad + 9, pad + 12 + wt, pad + ph - 9], radius=17, fill=(*accent_rgb, 255))
    d.text((pad + 25 - bt[0], pad + 26 - (bt[1] + bt[3]) * 0.5), tag_txt, font=f_t, fill=(255, 255, 255, 255))
    d.text((pad + 24 + wt - bm[0], pad + 26 - (bm[1] + bm[3]) * 0.5), main_txt, font=f_m, fill=(20, 20, 28, 255))
    _pill_cache[k] = im
    return im

def draw_kobe_flow_video_card(canvas_im, vf_rgb, t, st, en, cx, cy, pw, ph, tag_txt, main_txt, accent_rgb=(54, 86, 251)):
    if t <= st or t >= en:
        return
    raw_in  = clamp01((t - st) / 0.28)
    raw_out = clamp01((en - t) / 0.22)
    u_in    = ease_out_back_soft(raw_in, overshoot=1.06)
    u_out   = septic_smooth(raw_out)
    op      = min(quintic_smooth(min(1.0, raw_in * 1.45)), u_out)
    sig     = (1.0 - quintic_smooth(raw_in)) * 6.0 + (1.0 - u_out) * 5.0
    if op <= 0.01:
        return

    # Landing Ripple Ring at exact touchdown (st + 0.24s)
    dt_r = t - (st + 0.24)
    if 0.0 <= dt_r <= 0.28:
        ur = quintic_smooth(clamp01(dt_r / 0.28))
        rx = int(pw * 0.42 * (0.28 + 1.05 * ur))
        ry = int(34 * (0.28 + 0.72 * ur))
        al = int(225 * (1.0 - ur))
        if al > 4 and rx > 10 and ry > 4:
            rp = Image.new("RGBA", (rx * 2 + 16, ry * 2 + 16), (0, 0, 0, 0))
            ImageDraw.Draw(rp).ellipse([8, 8, rx * 2 + 8, ry * 2 + 8], outline=(*accent_rgb, al), width=3)
            paste_centered_rgba(canvas_im, rp, cx, cy + ph * 0.49)

    pad = 20
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + pw, pad + ph + 12], radius=34, fill=(24, 36, 96, 98))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    u_z = septic_smooth(clamp01((t - st) / max(0.8, en - st)))
    vis_im = fit_cover_subpixel(vf_rgb, pw, ph, zoom=1.02 + 0.05 * u_z)
    rmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=34, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(vis_im, (pad, pad), mask=rmask)
    card = Image.alpha_composite(card, vl)

    pill = make_kobe_card_pill(tag_txt, main_txt, accent_rgb=accent_rgb)
    card.alpha_composite(pill, dest=(pad + 14, pad + 12))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=34, outline=(255, 255, 255, 252), width=5)
    d.rounded_rectangle([pad + 5, pad + 5, pad + pw - 6, pad + ph - 6], radius=29, outline=(*accent_rgb, 185), width=2)

    paste_centered_rgba(
        canvas_im, card,
        cx, cy + (1.0 - u_in) * (-95.0) - (1.0 - u_out) * 18.0,
        scale=(0.92 + 0.08 * u_in) * (0.95 + 0.05 * u_out),
        opacity=op, blur_sigma=sig
    )

def draw_kobe_416_iris_circle_pip(canvas_im, fg_rgb, t, st, en, cx=540.0, cy=1482.0, diam=416):
    """
    EXACT KOBE STUDIO VARIANT B BOTTOM CIRCLE PIP (PHONG-CACH.md line 40 & CHUYEN-DONG-LOP-PHU-VA-SFX.md #1):
    - Diameter: 416px (r=208px) centered at (540, 1482)
    - Double border: 8px #FFFFFF inner + 3px #8FA2F7 outer + soft shadow 0 18px 42px rgba(45,62,140,0.18)
    - Iris Circle Wipe: opens in 0.22s (circle 0%->100% over #CED8FA shutter) and closes in 0.20s!
    """
    if t < st or t > en:
        return
    u_open  = quintic_smooth(clamp01((t - st) / 0.22))
    u_close = quintic_smooth(clamp01((en - t) / 0.20))
    iris_u  = min(u_open, u_close)
    op_sh   = clamp01(min((t - st) / 0.12, (en - t) / 0.12))
    if op_sh <= 0.01:
        return

    # Crop centered around Pharmacist Hang's face & upper shoulders (x=190..890, y=580..1280)
    sub = fg_rgb[575:1295, 180:900]
    im_face = fit_cover_subpixel(sub, diam, diam, zoom=1.03)

    pad = 34
    cw = diam + pad * 2
    card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad - 4, pad + 16, pad + diam + 4, pad + diam + 24], fill=(45, 62, 140, 68))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=16)))

    # Neutral periwinkle shutter disc (#CED8FA)
    d = ImageDraw.Draw(card)
    d.ellipse([pad, pad, pad + diam - 1, pad + diam - 1], fill=(206, 216, 250, 255))

    if iris_u > 0.01:
        r_i = max(2.0, (diam * 0.5) * iris_u)
        c_i = diam * 0.5
        imask = Image.new("L", (diam, diam), 0)
        ImageDraw.Draw(imask).ellipse([c_i - r_i, c_i - r_i, c_i + r_i, c_i + r_i], fill=255)
        vl = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
        vl.paste(im_face, (pad, pad), mask=imask)
        card = Image.alpha_composite(card, vl)

    # Outer 3px #8FA2F7 + Inner 8px #FFFFFF double ring
    d = ImageDraw.Draw(card)
    d.ellipse([pad - 5, pad - 5, pad + diam + 4, pad + diam + 4], outline=(143, 162, 247, 255), width=4)
    d.ellipse([pad - 1, pad - 1, pad + diam, pad + diam], outline=(255, 255, 255, 255), width=9)

    paste_centered_rgba(canvas_im, card, cx, cy, scale=0.92 + 0.08 * op_sh, opacity=op_sh)

# ======================================================================
# 3. BOX-SAFE & FACE-SAFE SENTENCE-CASE SUBTITLES (y=1278..1340 on blazer!)
# ======================================================================
_sub_cache = {}
def render_thin_grad_word(text, size, palette="pearl", stroke_w=2):
    k = (text, int(round(size)), palette, stroke_w)
    if k in _sub_cache:
        return _sub_cache[k]
    font = get_font(FONT_SUB_MAIN, size)
    dm = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dm.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw, th = max(4, bb[2] - bb[0]), max(4, bb[3] - bb[1])
    pad = 16
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bb[0], pad - bb[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sm = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(sm).text((ox + 1, oy + 3), text, font=font, fill=255, stroke_width=stroke_w + 1, stroke_fill=255)
    sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5.0)), dtype=np.float32) / 255.0
    sa = np.zeros((ch, cw, 4), dtype=np.uint8)
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (14, 18, 34)
    sa[:, :, 3] = np.clip(sb * 150.0, 0, 255).astype(np.uint8)
    base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(18, 22, 36, 236), stroke_width=stroke_w, stroke_fill=(18, 22, 36, 236))
    base = Image.alpha_composite(base, st_im)

    mask_im = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), text, font=font, fill=255)
    arr_m = np.array(mask_im, dtype=np.float32) / 255.0
    ys_on = np.where(arr_m.max(axis=1) > 0.15)[0]
    y_min = float(ys_on[0]) if len(ys_on) else float(pad)
    y_max = float(ys_on[-1]) if len(ys_on) else float(ch - pad)
    u_y = np.clip((np.arange(ch, dtype=np.float32) - y_min) / max(1.0, y_max - y_min), 0.0, 1.0)

    stops = GRAD_PALETTES.get(palette, GRAD_PALETTES["pearl"])
    pos_arr = np.array([p for p, _ in stops], dtype=np.float32)
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.float32)
    for c in range(3):
        val_arr = np.array([col[c] for _, col in stops], dtype=np.float32)
        grad_rgb[:, :, c] = np.interp(u_y, pos_arr, val_arr)[:, None]
    fill_rgba = np.dstack([np.clip(grad_rgb, 0, 255).astype(np.uint8), (arr_m * 255.0).astype(np.uint8)])
    base = Image.alpha_composite(base, Image.fromarray(fill_rgba, "RGBA"))
    _sub_cache[k] = base
    return base

def cap_first_char(s):
    return (s[0].upper() + s[1:]) if s else s

def load_captions_clean():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    # Omit karaoke subtitles during Full Kobe 9:16 Stages (30.80-36.48s & 53.86-60.56s) AND Chest Pill moments (1.25-2.62s & 67.80-71.10s)!
    def is_sub_allowed(tc):
        if tc < 2.85:
            return False
        if 30.78 <= tc <= 36.50:
            return False
        if 53.84 <= tc <= 60.56:
            return False
        if 67.78 <= tc <= 71.25:
            return False
        return True

    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and is_sub_allowed((w["start"] + w["end"]) * 0.5)
    ]

    COMPOUNDS = {
        ("sản", "phẩm"), ("phụ", "nữ"), ("tìm", "hiểu"), ("chăm", "sóc"),
        ("sức", "khỏe"), ("sắc", "đẹp"), ("bên", "trong"), ("thứ", "nhất"),
        ("hỗ", "trợ"), ("điều", "hòa"), ("chu", "kỳ"), ("nội", "tiết"),
        ("tiết", "tố"), ("cơ", "thể"), ("khỏe", "mạnh"), ("bắt", "đầu"),
        ("cân", "bằng"), ("chị", "em"), ("cảm", "thấy"), ("năng", "lượng"),
        ("tự", "tin"), ("cuộc", "sống"), ("hàng", "ngày"), ("thứ", "hai"),
        ("phụ", "khoa"), ("cảm", "giác"), ("khó", "chịu"), ("quan", "tâm"),
        ("đúng", "cách"), ("mỗi", "ngày"), ("duy", "trì"), ("thoải", "mái"),
        ("quan", "trọng"), ("lựa", "chọn"), ("phù", "hợp"), ("môi", "trường"),
        ("sinh", "lý"), ("tự", "nhiên"), ("thứ", "tư"), ("làn", "da"),
        ("mỹ", "phẩm"), ("phụ", "thuộc"), ("dinh", "dưỡng"), ("giấc", "ngủ"),
        ("chống", "nắng"), ("bổ", "sung"), ("hợp", "lý"), ("tư", "vấn"),
        ("chuyên", "gia"), ("hoạt", "động"), ("hiệu", "quả"), ("khách", "hàng"),
        ("thông", "minh"), ("đầu", "tư"), ("nền", "tảng"),
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
                elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 3 or dur_so_far >= 1.10):
                    phrases.append(cur_p); cur_p = []
                elif len(cur_p) >= 8 and prev_low not in {"rất", "một", "những", "các", "có", "sự"}:
                    phrases.append(cur_p); cur_p = []
        cur_p.append(w)
    if cur_p:
        phrases.append(cur_p)

    for p in phrases:
        if p:
            p[0][0] = cap_first_char(p[0][0])
            for k in range(1, len(p)):
                if re.search(r"[.?!:]$", p[k - 1][0]):
                    p[k][0] = cap_first_char(p[k][0])
                elif p[k][0][:1].isupper():
                    p[k][0] = p[k][0][0].lower() + p[k][0][1:]

    def split_balanced(p):
        tot_c = sum(len(x[0]) + 1 for x in p) - 1
        if len(p) <= 5 and tot_c <= 24:
            return [p]
        bk, bd = max(1, len(p) // 2), 9999
        for k in range(1, len(p)):
            c1 = sum(len(x[0]) + 1 for x in p[:k]) - 1
            c2 = sum(len(x[0]) + 1 for x in p[k:]) - 1
            d = abs(c1 - c2) + (6 if max(c1, c2) > 25 else 0)
            if d < bd:
                bd, bk = d, k
        return [p[:bk], p[bk:]]

    ROSE_W    = {"nội", "tiết", "chu", "kỳ", "sắc", "đẹp", "da"}
    COBALT_W  = {"phụ", "khoa,", "sinh", "lý", "chuyên", "gia,", "thông", "minh"}
    EMERALD_W = {"cân", "bằng,", "khỏe", "mạnh", "thoải", "mái", "tự", "tin", "dinh", "dưỡng,", "nền", "tảng"}

    cap_groups = []
    for i, p in enumerate(phrases):
        t0 = p[0][1] - 0.03
        last_end = p[-1][2]
        nxt_s = phrases[i + 1][0][1] if i + 1 < len(phrases) else 78.80
        t1 = min(nxt_s - 0.05, last_end + 0.45)
        if 30.78 - t0 > 0.1:
            t1 = min(t1, 30.76) if t0 < 30.76 else t1
        if 53.84 - t0 > 0.1:
            t1 = min(t1, 53.82) if t0 < 53.82 else t1
        if 67.78 - t0 > 0.1:
            t1 = min(t1, 67.75) if t0 < 67.75 else t1
        if t1 > t0 + 0.18:
            cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced(p)})
    return cap_groups, ROSE_W, COBALT_W, EMERALD_W

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
        return np.full((640, 1024, 3), 240, dtype=np.uint8)
    n = len(arr_list)
    if n == 1:
        return arr_list[0]
    u = clamp01(t_rel / max(0.5, target_span))
    pos = u * (n - 1)
    i0 = int(math.floor(pos))
    i1 = min(n - 1, i0 + 1)
    frac = pos - i0
    return arr_list[i0] if frac < 0.02 else np.clip(arr_list[i0].astype(np.float32) * (1.0 - frac) + arr_list[i1].astype(np.float32) * frac, 0, 255).astype(np.uint8)

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {
        int(round(ts * FPS))
        for ts in [1.60, 4.80, 11.80, 17.50, 24.40, 28.50, 33.40, 45.20, 52.40, 58.20, 69.00, 76.80]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    if not os.path.exists(aroll_path):
        aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vid_keys = [
        ("p3_01_endocrine_energy", 1024, 576),
        ("p3_02_feminine_comfort", 1024, 576),
        ("p3_03_inner_skin_glow",  1024, 576),
        ("p3_04_vitamin_vitality", 1024, 576),
    ]
    clips = {}
    for ck, vw, vh in vid_keys:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if os.path.exists(vp):
            clips[ck] = load_vid_frames_wh(vp, vw, vh)
            print(f"[HTPM3] Loaded {ck}: {len(clips[ck])} frames")
        else:
            raise FileNotFoundError(f"Missing Flow clip: {vp}")

    cap_groups, ROSE_W, COBALT_W, EMERALD_W = load_captions_clean()

    reader_a    = VideoReader(aroll_path)
    reader_m    = subprocess.Popen(["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    reader_kobe = RgbaVideoReader(KOBE_MOV)

    raw_vid_out = os.path.join(PROJ_DIR, "_master_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    # Desk-Box Guard: protects 100% of all 4 real HTPM product boxes at y >= 1445!
    yy_g = np.arange(H, dtype=np.float32)[:, None]
    desk_box_guard = np.clip((yy_g - 1435.0) / 55.0, 0.0, 1.0)
    wall_y_grad = np.linspace(231.0, 222.0, 835, dtype=np.float32)[:, None]
    wall_clean_patch = np.dstack([wall_y_grad - 2.0, wall_y_grad, wall_y_grad + 5.0])  # exact studio ivory wall

    def clean_upper_wall_signage(rgb_in, matte_u8):
        out = rgb_in.copy()
        top = out[:835].astype(np.float32)
        r, g, b = top[:, :, 0], top[:, :, 1], top[:, :, 2]
        not_plant  = (g - np.maximum(r, b)) < 10.0
        red_sign   = (r - g > 22.0) & (r > 130.0) & not_plant
        blue_sign  = (b - r > 20.0) & (b > 90.0)  & not_plant
        raw_mask   = (red_sign | blue_sign).astype(np.float32)
        feathered  = np.clip(gaussian_filter(raw_mask, sigma=6.5) * 2.8, 0.0, 1.0)
        y_taper    = np.clip((830.0 - np.arange(835, dtype=np.float32)) / 35.0, 0.0, 1.0)[:, None]
        person_m   = (matte_u8[:835].astype(np.float32) / 255.0)
        w_rep      = (feathered * y_taper * (1.0 - np.clip(person_m * 1.4, 0.0, 1.0)))[:, :, None]
        out[:835]  = np.clip(top * (1.0 - w_rep) + wall_clean_patch * w_rep, 0, 255).astype(np.uint8)
        return out

    frame_idx = 0
    while True:
        rgb_raw = reader_a.read()
        mbuf = reader_m.stdout.read(W * H)
        if rgb_raw is None or len(mbuf) < W * H:
            break
        if test_mode and frame_idx not in test_frames:
            reader_kobe.skip()
            frame_idx += 1
            if frame_idx > max(test_frames):
                break
            continue

        kobe_rgba = reader_kobe.read()
        matte_raw = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W))
        rgb_raw   = clean_upper_wall_signage(rgb_raw, matte_raw)
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

        is_full_kobe_stage = (30.80 <= t <= 36.48) or (53.86 <= t <= 60.56)

        if not is_full_kobe_stage:
            # ==============================================================
            # MODE A: TALKING HEAD + BEHIND-HEAD KOBE STAGE + DESK BOX GUARD
            # ==============================================================
            base_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

            # 1. Left-side Google Flow Ingredients Video Cards (paired with right-side Kobe SaaS cards!)
            if 13.92 <= t < 20.92:
                vf = get_clip_frame_smooth(clips, "p3_01_endocrine_energy", (t - 13.92) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(base_im, vf, t, 13.94, 20.90, 344.0, 343.0, 616, 588, "01", "NỘI TIẾT CÂN BẰNG • TRÀN NĂNG LƯỢNG", accent_rgb=(54, 86, 251))

            if 26.40 <= t < 30.76:
                vf = get_clip_frame_smooth(clips, "p3_02_feminine_comfort", (t - 26.40) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(base_im, vf, t, 26.42, 30.74, 344.0, 343.0, 616, 588, "02", "CHĂM SÓC ĐÚNG • THOẢI MÁI & TỰ TIN", accent_rgb=(11, 138, 92))

            if 42.52 <= t < 48.52:
                vf = get_clip_frame_smooth(clips, "p3_03_inner_skin_glow", (t - 42.52) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(base_im, vf, t, 42.54, 48.50, 344.0, 343.0, 616, 588, "04", "LÀN DA KHỎE RẠNG RỠ TỪ BÊN TRONG", accent_rgb=(201, 24, 96))

            # 2. Composite Upper Kobe HyperFrames Stage (y < 1040) BEHIND Pharmacist Hang's RVM hair crown!
            if kobe_rgba is not None:
                upper_kobe = kobe_rgba.copy()
                upper_kobe[1040:, :, 3] = 0
                if upper_kobe[:, :, 3].max() > 0:
                    base_im = Image.alpha_composite(base_im, Image.fromarray(upper_kobe, "RGBA"))

            # 3. Re-composite Pharmacist Hang + ALL 4 REAL DESK BOXES in foreground!
            fg_alpha = np.maximum(m_arr, desk_box_guard)
            comp_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

            # 4. Composite Foreground Kobe Chest Pill Stickers (y >= 1040, safely above boxes!)
            if kobe_rgba is not None:
                lower_kobe = kobe_rgba.copy()
                lower_kobe[:1040, :, 3] = 0
                if lower_kobe[:, :, 3].max() > 0:
                    comp_im = Image.alpha_composite(comp_im, Image.fromarray(lower_kobe, "RGBA"))
        else:
            # ==============================================================
            # MODE B: FULL-SCREEN KOBE LIGHT PASTEL DOT-GRID + 416px IRIS PIP!
            # ==============================================================
            comp_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")
            if kobe_rgba is not None and kobe_rgba[:, :, 3].max() > 0:
                comp_im = Image.alpha_composite(comp_im, Image.fromarray(kobe_rgba, "RGBA"))

            if 53.86 <= t <= 60.56:
                vf_vit = get_clip_frame_smooth(clips, "p3_04_vitamin_vitality", (t - 53.86) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(comp_im, vf_vit, t, 53.94, 60.48, 540.0, 474.0, 944, 476, "05", "VITAMIN TỔNG HỢP & DƯỠNG CHẤT THIẾT YẾU", accent_rgb=(54, 86, 251))

            if 30.80 <= t <= 36.48:
                draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 30.80, 36.48, cx=540.0, cy=1482.0, diam=416)
            elif 53.86 <= t <= 60.56:
                draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 53.86, 60.56, cx=540.0, cy=1482.0, diam=416)

        # ==============================================================
        # 5. BOX-SAFE & FACE-SAFE SENTENCE-CASE SUBTITLES (y=1276..1336)
        #    Sits cleanly on cream blazer ABOVE all 4 real desk boxes (y=1455)!
        # ==============================================================
        if not is_full_kobe_stage:
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    dt_in, dt_out = t - g["t0"], g["t1"] - t
                    u_in  = ease_out_back_soft(clamp01(dt_in / 0.20), overshoot=1.05)
                    u_out = septic_smooth(clamp01(dt_out / 0.16))
                    op_g  = min(quintic_smooth(clamp01(dt_in / 0.14)), u_out)
                    if op_g <= 0.01:
                        break
                    min_x, max_x, x_center = 54.0, 1026.0, 540.0
                    cap_sz = 50.0
                    y_base = 1272.0 if len(g["lines"]) >= 2 else 1304.0
                    lh, gap = 60.0, 12.0

                    for li, ln in enumerate(g["lines"]):
                        word_renders, total_w = [], 0.0
                        for wi, (wtxt, ws, we) in enumerate(ln):
                            is_act = (ws - 0.04 <= t <= we + 0.18)
                            pulse  = 1.06 if is_act else 1.00
                            wlow   = wtxt.lower().rstrip(",.?!:;")
                            if wlow in ROSE_W:
                                pal = "rose_satin"
                            elif wlow in COBALT_W:
                                pal = "cobalt"
                            elif wlow in EMERALD_W:
                                pal = "emerald"
                            else:
                                pal = "gold" if is_act else "pearl"
                            sp_w = render_thin_grad_word(wtxt, cap_sz, palette=pal, stroke_w=2)
                            adv  = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_SUB_MAIN, cap_sz)) + 2.0
                            word_renders.append((sp_w, adv, pulse))
                            total_w += adv + (gap if wi > 0 else 0.0)

                        fit_k = min(1.0, (max_x - min_x) / max(1.0, total_w))
                        eff_tot = total_w * fit_k
                        cur_x = x_center - eff_tot * 0.5
                        cur_y = y_base + li * lh + (1.0 - u_in) * 12.0
                        for sp_w, adv, pulse in word_renders:
                            eff_adv = adv * fit_k
                            paste_centered_rgba(comp_im, sp_w, cur_x + eff_adv * 0.5, cur_y, scale=fit_k * pulse, opacity=op_g)
                            cur_x += eff_adv + gap * fit_k
                    break

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"test_htpm3_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  [HTPM3] Rendered {frame_idx}/{TOTAL_FRAMES} frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close(); writer.wait()
    reader_a.close()
    reader_m.stdout.close(); reader_m.wait()
    reader_kobe.close()

    if test_mode and test_saved:
        imgs_t = [Image.open(p).resize((270, 480), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (270 * 6, 480 * 2))
        for i, im in enumerate(imgs_t[:12]):
            grid.paste(im, ((i % 6) * 270, (i // 6) * 480))
        gp = os.path.join(CHECK_DIR, "htpm3_kobe_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved 12-panel Kobe test grid:", gp)
    else:
        print(f"Done HTPM3 Kobe Talking Head Master video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
