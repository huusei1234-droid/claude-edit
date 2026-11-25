import concurrent.futures, json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"C:\AI\full studio\output\htpm-kb05-261123"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
FONTS_DIR = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
KOBE_MOV  = os.path.join(PROJ_DIR, "kobe_overlays.mov")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
TOTAL_FRAMES = 2100  # 70.000s

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
# 1. PURPOSEFUL CAMERA RIG + POST-HOOK ZOOM-IN -> 12.24s RISER NORMAL-FRAME TRANSITION!
#    Also hides surgical jump-cuts at 2.533s, 6.933s, 36.867s, and 47.367s cleanly!
# ======================================================================
CAM_KEYFRAMES = [
    ( 0.000, 1.000, 0.000,  0.000, 0.25),
    ( 0.120, 1.024, 0.000, -0.003, 2.30),  # Normal frame during Hook "Đừng để chuyện vợ chồng thành áp lực!"
    ( 2.533, 1.136, 0.000, -0.014, 0.03),  # Crisp 2-cam punch-in right after Hook (hides Cut #1 seamlessly!)
    ( 2.620, 1.160, 0.000, -0.016, 4.25),  # Living forward creep across 2.62..6.90s
    ( 6.933, 1.216, 0.000, -0.021, 0.03),  # Crisp step-in on "nhưng khoảng cách..." (hides Cut #2 seamlessly!)
    ( 7.020, 1.236, 0.000, -0.023, 4.70),  # Slow dramatic push across "...vì một chuyện chẳng ai dám nói."
    (11.780, 1.000, 0.000,  0.000, 0.48),  # 12.24s SFX Riser climax -> Smooth zoom-out back to 1.000x Normal Frame!
    (13.200, 1.022, 0.000, -0.003, 3.10),  # Normal frame breathing before Full Kobe Stage #1
    (26.400, 1.000, 0.000,  0.000, 0.45),  # Return from Full Kobe Stage #1
    (29.800, 1.055, 0.000, -0.007, 0.60),  # "Chồng nghĩ vợ không còn yêu mình..."
    (34.500, 1.088, 0.000, -0.011, 0.50),  # "...rồi cả hai cùng tổn thương."
    (36.867, 1.018, 0.000, -0.002, 0.03),  # Crisp angle reset on Cut #3 ("Hằng muốn chị em hiểu...")
    (38.400, 1.048, 0.000, -0.006, 8.80),  # Gentle push on health & quality of life
    (47.367, 1.115, 0.000, -0.014, 0.03),  # Crisp punch-in on Cut #4 ("Và cũng đừng vội đổ lỗi cho người kia!")
    (62.640, 1.032, 0.000, -0.004, 0.45),  # Return from Full Kobe Stage #2
    (66.400, 1.076, 0.000, -0.010, 0.55),  # Warm closing CTA: 'comment "Vợ chồng"!'
]

def eval_camera_rig(t):
    z_cur, px_cur, py_cur = CAM_KEYFRAMES[0][1], CAM_KEYFRAMES[0][2], CAM_KEYFRAMES[0][3]
    for i in range(1, len(CAM_KEYFRAMES)):
        tk, zk, pxk, pyk, dur_k = CAM_KEYFRAMES[i]
        if t >= tk:
            if dur_k <= 0.05:
                u = 1.0
            else:
                u = septic_smooth(clamp01((t - tk) / dur_k))
            z_cur  += (zk  - z_cur)  * u
            px_cur += (pxk - px_cur) * u
            py_cur += (pyk - py_cur) * u
    return z_cur, px_cur, py_cur

def apply_riser_optical_transition(comp_im, t, center_t=12.24, half_w=0.18):
    dt = abs(t - center_t)
    if dt >= half_w:
        return comp_im
    bell = math.cos((dt / half_w) * (math.pi * 0.5)) ** 2
    if bell <= 0.02:
        return comp_im
    rgb = comp_im.convert("RGB")
    if bell > 0.12:
        bl = rgb.filter(ImageFilter.GaussianBlur(radius=4.2 * bell))
        arr_c = np.array(rgb, dtype=np.float32)
        arr_b = np.array(bl, dtype=np.float32)
        mix = arr_c * (1.0 - 0.52 * bell) + arr_b * (0.52 * bell)
    else:
        mix = np.array(rgb, dtype=np.float32)
    bloom = np.array([34.0, 31.0, 24.0], dtype=np.float32) * bell
    out_rgb = np.clip(mix + bloom, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out_rgb, "RGB").convert("RGBA")

def fit_cover_subpixel(rgb_arr, target_w, target_h, zoom=1.0, pan_x=0.0, pan_y=0.0):
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    inv_s = 1.0 / base_scale
    half_w_s = (target_w * 0.5) * inv_s
    half_h_s = (target_h * 0.5) * inv_s
    cx_src = max(half_w_s, min(sw - half_w_s, sw * 0.5 + pan_x * sw))
    cy_src = max(half_h_s, min(sh - half_h_s, sh * 0.5 + pan_y * sh))
    return Image.fromarray(rgb_arr, "RGB").transform(
        (target_w, target_h),
        Image.Transform.AFFINE,
        (inv_s, 0.0, cx_src - half_w_s, 0.0, inv_s, cy_src - half_h_s),
        resample=Image.Resampling.BICUBIC,
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

_pill_cache = {}
def make_kobe_card_pill(tag_txt, main_txt, accent_rgb=(54, 86, 251)):
    k = (tag_txt, main_txt, accent_rgb)
    if k in _pill_cache:
        return _pill_cache[k]
    f_t = get_font(FONT_CARD_LBL, 20)
    f_m = get_font(FONT_CARD_LBL, 22)
    dm = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bt = dm.textbbox((0, 0), tag_txt, font=f_t)
    bm = dm.textbbox((0, 0), main_txt, font=f_m)
    wt = bt[2] - bt[0] + 24
    wm = bm[2] - bm[0]
    pw, ph, pad = wt + wm + 40, 48, 8
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=24, fill=(255, 255, 255, 248), outline=(255, 255, 255, 255), width=2)
    d.rounded_rectangle([pad + 10, pad + 7, pad + 10 + wt, pad + ph - 7], radius=17, fill=(*accent_rgb, 255))
    d.text((pad + 22 - bt[0], pad + 24 - (bt[1] + bt[3]) * 0.5), tag_txt, font=f_t, fill=(255, 255, 255, 255))
    d.text((pad + 20 + wt - bm[0], pad + 24 - (bm[1] + bm[3]) * 0.5), main_txt, font=f_m, fill=(20, 20, 28, 255))
    _pill_cache[k] = im
    return im

def draw_kobe_flow_video_card(canvas_im, vf_rgb, t, st, en, cx, cy, pw, ph, tag_txt, main_txt, accent_rgb=(54, 86, 251), pan_y=-0.02):
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

    dt_r = t - (st + 0.24)
    if 0.0 <= dt_r <= 0.28:
        ur = quintic_smooth(clamp01(dt_r / 0.28))
        rx = int(pw * 0.42 * (0.28 + 1.05 * ur))
        ry = int(32 * (0.28 + 0.72 * ur))
        al = int(225 * (1.0 - ur))
        if al > 4 and rx > 10 and ry > 4:
            rp = Image.new("RGBA", (rx * 2 + 16, ry * 2 + 16), (0, 0, 0, 0))
            ImageDraw.Draw(rp).ellipse([8, 8, rx * 2 + 8, ry * 2 + 8], outline=(*accent_rgb, al), width=3)
            paste_centered_rgba(canvas_im, rp, cx, cy + ph * 0.49)

    pad = 20
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + pw, pad + ph + 12], radius=32, fill=(18, 28, 68, 108))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    u_z = septic_smooth(clamp01((t - st) / max(0.8, en - st)))
    vis_im = fit_cover_subpixel(vf_rgb, pw, ph, zoom=1.06 + 0.05 * u_z, pan_x=0.0, pan_y=pan_y)

    sheen_phase = ((t - st) % 2.8) / 1.05
    if 0.0 <= sheen_phase <= 1.0:
        vis_rgba = vis_im.convert("RGBA")
        sh_ov = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        sx = int(-pw * 0.35 + (pw * 1.70) * quintic_smooth(sheen_phase))
        ImageDraw.Draw(sh_ov).polygon(
            [(sx, 0), (sx + 110, 0), (sx - 70, ph), (sx - 180, ph)],
            fill=(255, 255, 255, 48)
        )
        vis_im = Image.alpha_composite(vis_rgba, sh_ov.filter(ImageFilter.GaussianBlur(radius=14))).convert("RGB")

    rmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(vis_im, (pad, pad), mask=rmask)
    card = Image.alpha_composite(card, vl)

    pill = make_kobe_card_pill(tag_txt, main_txt, accent_rgb=accent_rgb)
    card.alpha_composite(pill, dest=(pad + 14, pad + 12))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=32, outline=(255, 255, 255, 252), width=5)
    d.rounded_rectangle([pad + 5, pad + 5, pad + pw - 6, pad + ph - 6], radius=27, outline=(*accent_rgb, 185), width=2)

    live_bob = math.sin((t - st) * 2.35) * 5.5 * clamp01((t - st - 0.28) / 0.25)
    paste_centered_rgba(
        canvas_im, card,
        cx, cy + (1.0 - u_in) * (-88.0) - (1.0 - u_out) * 18.0 + live_bob,
        scale=(0.92 + 0.08 * u_in) * (0.95 + 0.05 * u_out),
        opacity=op, blur_sigma=sig
    )

def draw_kobe_416_iris_circle_pip(canvas_im, fg_rgb, t, st, en, cx=540.0, cy=1482.0, diam=416):
    if t < st or t > en:
        return
    u_open  = quintic_smooth(clamp01((t - st) / 0.22))
    u_close = quintic_smooth(clamp01((en - t) / 0.20))
    iris_u  = min(u_open, u_close)
    op_sh   = clamp01(min((t - st) / 0.12, (en - t) / 0.12))
    if op_sh <= 0.01:
        return

    # Calibrated to KB05 ruler_frame.jpg (crown y=430, face y=500..785, mic & coral dress y=785..1130)
    sub = fg_rgb[410:1130, 195:915]
    im_face = fit_cover_subpixel(sub, diam, diam, zoom=1.04)

    pad = 38
    cw = diam + pad * 2
    card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad - 4, pad + 16, pad + diam + 4, pad + diam + 24], fill=(45, 62, 140, 68))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=16)))

    d = ImageDraw.Draw(card)
    pulse_r = int(round(6.0 + 5.0 * (0.5 + 0.5 * math.sin((t - st) * 3.4))))
    halo_al = int(round(135 - 55 * (0.5 + 0.5 * math.sin((t - st) * 3.4))))
    d.ellipse([pad - pulse_r, pad - pulse_r, pad + diam - 1 + pulse_r, pad + diam - 1 + pulse_r], outline=(143, 162, 247, halo_al), width=3)
    d.ellipse([pad, pad, pad + diam - 1, pad + diam - 1], fill=(206, 216, 250, 255))

    if iris_u > 0.01:
        r_i = max(2.0, (diam * 0.5) * iris_u)
        c_i = diam * 0.5
        imask = Image.new("L", (diam, diam), 0)
        ImageDraw.Draw(imask).ellipse([c_i - r_i, c_i - r_i, c_i + r_i, c_i + r_i], fill=255)
        vl = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
        vl.paste(im_face, (pad, pad), mask=imask)
        card = Image.alpha_composite(card, vl)

    d = ImageDraw.Draw(card)
    d.ellipse([pad - 5, pad - 5, pad + diam + 4, pad + diam + 4], outline=(143, 162, 247, 255), width=4)
    d.ellipse([pad - 1, pad - 1, pad + diam, pad + diam], outline=(255, 255, 255, 255), width=9)

    live_bob = math.sin((t - st) * 2.2) * 3.5 * iris_u
    paste_centered_rgba(canvas_im, card, cx, cy + live_bob, scale=0.92 + 0.08 * op_sh, opacity=op_sh)

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
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (12, 16, 30)
    sa[:, :, 3] = np.clip(sb * 185.0, 0, 255).astype(np.uint8)
    base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(16, 20, 34, 248), stroke_width=stroke_w, stroke_fill=(16, 20, 34, 248))
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

    def is_sub_allowed(tc):
        if 16.46 <= tc <= 26.38:
            return False
        if 49.58 <= tc <= 62.60:
            return False
        return True

    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and is_sub_allowed((w["start"] + w["end"]) * 0.5)
    ]

    COMPOUNDS = {
        ("vợ", "chồng"), ("vợ", "chồng!"), ("áp", "lực!"), ("hôn", "nhân"),
        ("thứ", "ba"), ("cãi", "nhau"), ("khoảng", "cách"), ("dám", "nói."),
        ("thay", "đổi"), ("đời", "sống"), ("im", "lặng."), ("yêu", "mình,"),
        ("thương", "mình,"), ("tổn", "thương."), ("sức", "khỏe"), ("chất", "lượng"),
        ("cuộc", "sống."), ("xấu", "hổ,"), ("tự", "trách"), ("đổ", "lỗi"),
        ("phụ", "nữ"), ("ngại", "nói"), ("lấy", "chồng,"), ("\"vợ", "chồng\"!"),
    }

    phrases, cur_p = [], []
    for w in words:
        txt, ws, we = w
        wlow = txt.lower().rstrip(",.?!:;\"")
        if cur_p:
            gap = ws - cur_p[-1][2]
            prev_txt = cur_p[-1][0]
            dur_so_far = cur_p[-1][2] - cur_p[0][1]
            prev_low = prev_txt.lower().rstrip(",.?!:;\"")
            if (prev_low, txt.lower()) not in COMPOUNDS and (prev_low, wlow) not in COMPOUNDS:
                if re.search(r"[.?!…;:]$", prev_txt) or gap >= 0.38:
                    phrases.append(cur_p); cur_p = []
                elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 3 or dur_so_far >= 1.00):
                    phrases.append(cur_p); cur_p = []
                elif len(cur_p) >= 8 and prev_low not in {"rất", "một", "những", "các", "có", "sự", "chỉ"}:
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
                elif p[k][0][:1].isupper() and p[k][0].lower().strip("\"',.!") not in {"hằng", "vợ"}:
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

    ROSE_W    = {"áp", "lực", "xa", "im", "lặng", "tổn", "thương", "xấu", "hổ"}
    COBALT_W  = {"vợ", "chồng", "yêu", "hiểu", "trách", "lỗi"}
    EMERALD_W = {"khỏe", "sống", "series", "comment"}

    cap_groups = []
    for i, p in enumerate(phrases):
        t0 = max(0.0, p[0][1] - 0.03)
        last_end = p[-1][2]
        nxt_s = phrases[i + 1][0][1] if i + 1 < len(phrases) else 69.90
        t1 = min(nxt_s - 0.05, last_end + 0.45)
        if t0 < 16.44 and t1 > 16.44:
            t1 = min(t1, 16.44)
        if t0 < 49.56 and t1 > 49.56:
            t1 = min(t1, 49.56)
        if t1 > t0 + 0.16:
            cap_groups.append({"t0": t0, "t1": t1, "lines": split_balanced(p)})
    return cap_groups, ROSE_W, COBALT_W, EMERALD_W

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

def get_clip_frame_pingpong(clips, key, t_rel, cycle_s=3.8):
    arr_list = clips.get(key)
    if not arr_list:
        return np.full((576, 1024, 3), 240, dtype=np.uint8)
    n = len(arr_list)
    if n == 1:
        return arr_list[0]
    # Smooth ping-pong (0->1->0) so 9s slots never jump-loop!
    raw_u = (t_rel / max(0.8, cycle_s)) % 2.0
    u = raw_u if raw_u <= 1.0 else (2.0 - raw_u)
    pos = clamp01(u) * (n - 1)
    i0 = int(math.floor(pos))
    i1 = min(n - 1, i0 + 1)
    frac = pos - i0
    return arr_list[i0] if frac < 0.02 else np.clip(arr_list[i0].astype(np.float32) * (1.0 - frac) + arr_list[i1].astype(np.float32) * frac, 0, 255).astype(np.uint8)

def composite_single_frame(rgb_raw, matte_raw, kobe_rgba, t, clips, cap_groups, ROSE_W, COBALT_W, EMERALD_W):
    z_cam, px_cam, py_cam = eval_camera_rig(t)
    if abs(z_cam - 1.0) < 1e-4 and abs(px_cam) < 1e-4 and abs(py_cam) < 1e-4:
        fg_rgb = rgb_raw
        m_top  = matte_raw[:450]
    else:
        fg_im  = fit_cover_subpixel(rgb_raw, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam)
        fg_rgb = np.array(fg_im)
        if kobe_rgba is not None and kobe_rgba[:430, :, 3].max() > 0:
            m_rgb = np.repeat(matte_raw[:, :, None], 3, axis=2)
            m_top = np.array(fit_cover_subpixel(m_rgb, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam).convert("L"))[:450]
        else:
            m_top = matte_raw[:450]

    is_full_kobe_stage = (16.48 <= t <= 26.38) or (49.60 <= t <= 62.60)

    if not is_full_kobe_stage:
        comp_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

        # 1. Zero-Clip SVG Behind-Head Top Banner (rows 0..430) + RVM Hair Crown in front
        if kobe_rgba is not None and kobe_rgba[:430, :, 3].max() > 0:
            comp_im.alpha_composite(Image.fromarray(kobe_rgba[:430], "RGBA"), dest=(0, 0))
            crown_rgba = np.dstack([fg_rgb[:450], m_top])
            comp_im.alpha_composite(Image.fromarray(crown_rgba, "RGBA"), dest=(0, 0))

        # 2. Lower-Left Reference-Locked 2.5D Cinema Cards (paired with Right Living Kobe Cards!)
        if 3.00 <= t < 12.08:
            vf1 = get_clip_frame_pingpong(clips, "kb05_01_silent_distance", t - 3.00, cycle_s=4.5)
            draw_kobe_flow_video_card(comp_im, vf1, t, 3.02, 12.04, 324.0, 1444.0, 596, 476, "KHOẢNG CÁCH", "KHÔNG CÃI LỚN • NGÀY MỘT XA", accent_rgb=(225, 29, 72))
        elif 29.76 <= t < 36.78:
            vf3 = get_clip_frame_pingpong(clips, "kb05_03_silent_back_to_back", t - 29.76, cycle_s=3.8)
            draw_kobe_flow_video_card(comp_im, vf3, t, 29.78, 36.74, 324.0, 1444.0, 596, 476, "IM LẶNG", "HIỂU LẦM • CẢ HAI TỔN THƯƠNG", accent_rgb=(201, 24, 96))

        # 3. Lower Kobe Interactive Stage (rows 1155..1745)
        if kobe_rgba is not None and kobe_rgba[1155:1745, :, 3].max() > 0:
            comp_im.alpha_composite(Image.fromarray(kobe_rgba[1155:1745], "RGBA"), dest=(0, 1155))

        # 4. Post-Hook SFX Riser Optical Transition Pulse at t = 12.24s!
        if 12.06 <= t <= 12.42:
            comp_im = apply_riser_optical_transition(comp_im, t, center_t=12.24, half_w=0.18)
    else:
        comp_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")
        if kobe_rgba is not None and kobe_rgba[:, :, 3].max() > 0:
            comp_im.alpha_composite(Image.fromarray(kobe_rgba, "RGBA"), dest=(0, 0))

        if 16.48 <= t <= 26.38:
            vf2 = get_clip_frame_pingpong(clips, "kb05_02_tired_stress", t - 16.48, cycle_s=4.5)
            draw_kobe_flow_video_card(comp_im, vf2, t, 16.58, 26.26, 540.0, 390.0, 948, 396, "ÁP LỰC NGẦM", "MỆT MỎI • STRESS • KÉM THOẢI MÁI", accent_rgb=(201, 24, 96), pan_y=-0.04)
            draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 16.48, 26.38, cx=540.0, cy=1482.0, diam=416)
        elif 49.60 <= t <= 62.60:
            vf4 = get_clip_frame_pingpong(clips, "kb05_04_open_heart_talk", t - 49.60, cycle_s=4.8)
            draw_kobe_flow_video_card(comp_im, vf4, t, 49.72, 62.48, 540.0, 390.0, 948, 396, "THẤU HIỂU", "CHIA SẺ ĐÚNG CÁCH • GẦN NHAU HƠN", accent_rgb=(11, 138, 92), pan_y=-0.04)
            draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 49.60, 62.60, cx=540.0, cy=1482.0, diam=416)

    # 5. Clean Sentence-Case Thin-Stroke Subtitles at y=1756..1814 (Zero Overlap!)
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
                y_base = 1756.0 if len(g["lines"]) >= 2 else 1780.0
                lh, gap = 58.0, 12.0

                for li, ln in enumerate(g["lines"]):
                    word_renders, total_w = [], 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_act = (ws - 0.04 <= t <= we + 0.18)
                        pulse  = 1.06 if is_act else 1.00
                        wlow   = wtxt.lower().strip("\"',.?!:;")
                        pal = "rose_satin" if wlow in ROSE_W else ("cobalt" if wlow in COBALT_W else ("emerald" if wlow in EMERALD_W else ("gold" if is_act else "pearl")))
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

    return comp_im

VID_KEYS = [
    ("kb05_01_silent_distance",     1024, 576),
    ("kb05_02_tired_stress",        1024, 576),
    ("kb05_03_silent_back_to_back", 1024, 576),
    ("kb05_04_open_heart_talk",     1024, 576),
]

def render_chunk_worker(args):
    c_idx, f_start, f_end = args
    n_frames = f_end - f_start
    ss_sec = f"{f_start / FPS:.6f}"
    chunk_mp4 = os.path.join(PROJ_DIR, f"_chunk_{c_idx:02d}.mp4")

    aroll_path = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    clips = {ck: load_vid_frames_wh(os.path.join(MEDIA_DIR, f"{ck}.mp4"), vw, vh) for ck, vw, vh in VID_KEYS}
    cap_groups, ROSE_W, COBALT_W, EMERALD_W = load_captions_clean()

    proc_a = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", aroll_path, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    proc_m = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", matte_path, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    proc_k = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", KOBE_MOV,   "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)

    writer = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-threads", "3", "-pix_fmt", "yuv420p",
        chunk_mp4
    ], stdin=subprocess.PIPE)

    rendered = 0
    for local_i in range(n_frames):
        buf_a = proc_a.stdout.read(W * H * 3)
        buf_m = proc_m.stdout.read(W * H)
        buf_k = proc_k.stdout.read(W * H * 4)
        if len(buf_a) < W * H * 3 or len(buf_m) < W * H:
            break
        rgb_raw   = np.frombuffer(buf_a, dtype=np.uint8).reshape((H, W, 3))
        matte_raw = np.frombuffer(buf_m, dtype=np.uint8).reshape((H, W))
        kobe_rgba = np.frombuffer(buf_k, dtype=np.uint8).reshape((H, W, 4)) if len(buf_k) == W * H * 4 else None
        t = (f_start + local_i) / FPS

        comp_im = composite_single_frame(rgb_raw, matte_raw, kobe_rgba, t, clips, cap_groups, ROSE_W, COBALT_W, EMERALD_W)
        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        rendered += 1

    writer.stdin.close(); writer.wait()
    proc_a.stdout.close(); proc_a.wait()
    proc_m.stdout.close(); proc_m.wait()
    proc_k.stdout.close(); proc_k.wait()
    return c_idx, rendered, chunk_mp4

def run_test_mode():
    aroll_path = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")
    clips = {ck: load_vid_frames_wh(os.path.join(MEDIA_DIR, f"{ck}.mp4"), vw, vh) for ck, vw, vh in VID_KEYS}
    cap_groups, ROSE_W, COBALT_W, EMERALD_W = load_captions_clean()

    test_ts = [1.20, 3.80, 9.80, 12.24, 14.20, 23.60, 27.80, 34.80, 41.20, 48.00, 56.50, 68.50]
    saved_paths = []

    for idx_t, ts in enumerate(test_ts):
        ss = f"{ts:.4f}"
        ba = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", aroll_path, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        bm = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", matte_path, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
        bk = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", KOBE_MOV,   "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgba", "-"])
        rgb_raw   = np.frombuffer(ba, dtype=np.uint8).reshape((H, W, 3))
        matte_raw = np.frombuffer(bm, dtype=np.uint8).reshape((H, W))
        kobe_rgba = np.frombuffer(bk, dtype=np.uint8).reshape((H, W, 4))
        comp_im = composite_single_frame(rgb_raw, matte_raw, kobe_rgba, ts, clips, cap_groups, ROSE_W, COBALT_W, EMERALD_W)
        tp = os.path.join(CHECK_DIR, f"test_kb05_{idx_t:02d}_{ts:.2f}s.png")
        comp_im.convert("RGB").save(tp)
        saved_paths.append(tp)

    # Save 100% full-res top-banner crops of ALL 4 SVG Headlines to prove 0% clipping & 0% stroke blobs!
    crop_stack = Image.new("RGB", (1080, 360 * 4))
    for ci, src_i in enumerate([0, 7, 8, 11]):  # 1.20s, 34.80s, 41.20s, 68.50s
        im_full = Image.open(saved_paths[src_i])
        crop_stack.paste(im_full.crop((0, 30, 1080, 390)), (0, ci * 360))
    crop_path = os.path.join(CHECK_DIR, "kb05_svg_titles_100pct_crop.png")
    crop_stack.save(crop_path)

    imgs_t = [Image.open(p).resize((270, 480), Image.Resampling.LANCZOS) for p in saved_paths]
    grid = Image.new("RGB", (270 * 6, 480 * 2))
    for i, im in enumerate(imgs_t[:12]):
        grid.paste(im, ((i % 6) * 270, (i // 6) * 480))
    gp = os.path.join(CHECK_DIR, "kb05_test_grid.jpg")
    grid.save(gp, quality=94)
    print("Saved 12-panel test grid:", gp, flush=True)
    print("Saved 100% SVG title crop:", crop_path, flush=True)

def main():
    if "--test" in sys.argv:
        run_test_mode()
        return

    t0 = time.time()
    for ck, _, _ in VID_KEYS:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if not os.path.exists(vp):
            raise FileNotFoundError(f"Missing required B-roll video clip: {vp}")

    n_workers = 6
    step = (TOTAL_FRAMES + n_workers - 1) // n_workers
    tasks = []
    for i in range(n_workers):
        fs = i * step
        fe = min(TOTAL_FRAMES, (i + 1) * step)
        if fs < fe:
            tasks.append((i, fs, fe))

    print(f"[KB05-6W] Launching {len(tasks)} parallel workers across {TOTAL_FRAMES} frames...", flush=True)
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as ex:
        for res in ex.map(render_chunk_worker, tasks):
            c_idx, cnt, cp = res
            print(f"  [Worker {c_idx}] Finished {cnt} frames ({time.time() - t0:.1f}s)", flush=True)
            results.append(res)

    results.sort(key=lambda x: x[0])
    concat_txt = os.path.join(PROJ_DIR, "_chunks_list.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for _, _, cp in results:
            p_clean = cp.replace("\\", "/")
            f.write(f"file '{p_clean}'\n")

    raw_vid_out = os.path.join(PROJ_DIR, "_master_video_only.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p",
        raw_vid_out
    ], check=True)

    for _, _, cp in results:
        try:
            os.remove(cp)
        except OSError:
            pass
    print(f"[KB05-6W] Master video assembled via GPU h264_nvenc in {time.time() - t0:.1f}s -> {raw_vid_out}", flush=True)

if __name__ == "__main__":
    main()
