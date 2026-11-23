import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm-261120"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
FONTS_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
KOBE_MOV  = os.path.join(PROJ_DIR, "kobe_overlays.mov")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
TOTAL_FRAMES = 3327  # 110.92s

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
# 1. PURPOSEFUL CAMERA KEYFRAME RIG (0% jitter, emphasizes key leadership lines!)
# ======================================================================
CAM_KEYFRAMES = [
    (  0.00, 1.000, 0.000,  0.000, 0.35),
    (  0.20, 1.052, 0.000, -0.006, 0.55),  # Hook question opening
    (  8.15, 1.078, 0.000, -0.010, 0.50),  # "Làm sao để đội nhóm chủ động đăng bài mà không cần phải nhắc?"
    ( 11.18, 1.000, 0.000,  0.000, 0.58),  # Wide for Overload Trap
    ( 20.80, 1.066, 0.000, -0.008, 0.54),  # "Càng nhắc chị càng mệt, đội nhóm càng phụ thuộc!"
    ( 28.95, 1.088, 0.000, -0.012, 0.48),  # Thesis punch-in: "Một leader giỏi tạo ra sự chủ động!"
    ( 33.15, 1.038, 0.000, -0.005, 0.56),  # "Muốn đội nhóm chủ động, đừng chỉ giao việc..."
    ( 51.40, 1.068, 0.000, -0.008, 0.50),  # Return from Full Kobe Stage #1: "Leader dẫn dắt bằng chính hành động!"
    ( 58.62, 1.000, 0.000,  0.000, 0.55),  # Steady wide for 3 Mirror Habits (1-2-3)
    ( 70.84, 1.090, 0.000, -0.012, 0.48),  # Golden Law punch-in: "Đội nhóm sẽ làm theo những gì leader làm!"
    ( 76.60, 1.036, 0.000, -0.004, 0.56),  # Reflection setup
    ( 82.40, 1.084, 0.000, -0.010, 0.50),  # "Mình đã trở thành tấm gương để các bạn muốn làm theo chưa?"
    ( 98.10, 1.035, 0.000, -0.004, 0.52),  # Return from Full Kobe Stage #2
    (101.26, 1.078, 0.000, -0.010, 0.54),  # Climax: "Một leader biết truyền cảm hứng sẽ tạo ra đội nhóm tự hành động!"
    (105.40, 1.042, 0.000, -0.005, 0.60),  # Graceful warm closing ("Đó mới là cách xây dựng hệ thống bền vững, em nhá!")
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
# 2. KOBE FLOW VIDEO CARD + RIPPLE + 416px IRIS CIRCLE PIP
# ======================================================================
_pill_cache = {}
def make_kobe_card_pill(tag_txt, main_txt, accent_rgb=(54, 86, 251)):
    k = (tag_txt, main_txt, accent_rgb)
    if k in _pill_cache:
        return _pill_cache[k]
    f_t = get_font(FONT_CARD_LBL, 20)
    f_m = get_font(FONT_CARD_LBL, 24)
    dm = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bt = dm.textbbox((0, 0), tag_txt, font=f_t)
    bm = dm.textbbox((0, 0), main_txt, font=f_m)
    wt = bt[2] - bt[0] + 26
    wm = bm[2] - bm[0]
    pw, ph, pad = wt + wm + 44, 50, 8
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=25, fill=(255, 255, 255, 248), outline=(255, 255, 255, 255), width=2)
    d.rounded_rectangle([pad + 11, pad + 8, pad + 11 + wt, pad + ph - 8], radius=17, fill=(*accent_rgb, 255))
    d.text((pad + 24 - bt[0], pad + 25 - (bt[1] + bt[3]) * 0.5), tag_txt, font=f_t, fill=(255, 255, 255, 255))
    d.text((pad + 22 + wt - bm[0], pad + 25 - (bm[1] + bm[3]) * 0.5), main_txt, font=f_m, fill=(20, 20, 28, 255))
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
    vis_im = fit_cover_subpixel(vf_rgb, pw, ph, zoom=1.12 + 0.05 * u_z, pan_x=-0.02, pan_y=-0.02)
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

    paste_centered_rgba(
        canvas_im, card,
        cx, cy + (1.0 - u_in) * (-88.0) - (1.0 - u_out) * 18.0,
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

    # Calibrated to outdoor HTPM.mp4 (crown y=315, face y=400..730, collar y=730..985)
    sub = fg_rgb[275:995, 175:895]
    im_face = fit_cover_subpixel(sub, diam, diam, zoom=1.03)

    pad = 34
    cw = diam + pad * 2
    card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad - 4, pad + 16, pad + diam + 4, pad + diam + 24], fill=(45, 62, 140, 68))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=16)))

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

    d = ImageDraw.Draw(card)
    d.ellipse([pad - 5, pad - 5, pad + diam + 4, pad + diam + 4], outline=(143, 162, 247, 255), width=4)
    d.ellipse([pad - 1, pad - 1, pad + diam, pad + diam], outline=(255, 255, 255, 255), width=9)

    paste_centered_rgba(canvas_im, card, cx, cy, scale=0.92 + 0.08 * op_sh, opacity=op_sh)

# ======================================================================
# 3. SENTENCE-CASE THIN-STROKE (2px) SUBTITLES AT y=1716..1782 (Below Lower Stage!)
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
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (12, 16, 30)
    sa[:, :, 3] = np.clip(sb * 165.0, 0, 255).astype(np.uint8)
    base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(16, 20, 34, 242), stroke_width=stroke_w, stroke_fill=(16, 20, 34, 242))
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
        if 38.28 <= tc <= 51.38:
            return False
        if 86.36 <= tc <= 98.08:
            return False
        return True

    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and is_sub_allowed((w["start"] + w["end"]) * 0.5)
    ]

    COMPOUNDS = {
        ("đội", "nhóm"), ("đăng", "bài"), ("đăng", "bài,"), ("im", "lặng,"),
        ("chủ", "động"), ("chủ", "động,"), ("chủ", "động."), ("trải", "qua,"),
        ("phụ", "thuộc."), ("phụ", "thuộc,"), ("nhận", "ra"), ("giao", "việc,"),
        ("vì", "sao"), ("đều", "đặn"), ("khách", "hàng"), ("nền", "tảng"),
        ("lâu", "dài."), ("ý", "nghĩa"), ("tự", "giác"), ("chia", "sẻ"),
        ("đội", "ngũ:"), ("dẫn", "dắt"), ("lời", "nói,"), ("hành", "động"),
        ("hành", "động."), ("học", "hỏi,"), ("cố", "gắng,"), ("tấm", "gương"),
        ("kỷ", "luật,"), ("kỷ", "luật."), ("nhiệt", "huyết,"), ("động", "lực."),
        ("nhắc", "việc"), ("cảm", "hứng"), ("hệ", "thống"), ("bền", "vững,"),
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
            if (prev_low, txt.lower()) not in COMPOUNDS and (prev_low, wlow) not in COMPOUNDS:
                if re.search(r"[.?!…;:]$", prev_txt) or gap >= 0.40:
                    phrases.append(cur_p); cur_p = []
                elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 3 or dur_so_far >= 1.05):
                    phrases.append(cur_p); cur_p = []
                elif len(cur_p) >= 8 and prev_low not in {"rất", "một", "những", "các", "có", "sự", "biết"}:
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
                elif p[k][0][:1].isupper() and p[k][0].lower() not in {"hằng", "hằng,"}:
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

    ROSE_W    = {"phụ", "thuộc", "mệt", "hứng", "gương"}
    COBALT_W  = {"leader", "hành", "động", "đăng", "video", "học"}
    EMERALD_W = {"chủ", "tự", "giác", "bền", "vững"}

    cap_groups = []
    for i, p in enumerate(phrases):
        t0 = p[0][1] - 0.03
        last_end = p[-1][2]
        nxt_s = phrases[i + 1][0][1] if i + 1 < len(phrases) else 110.50
        t1 = min(nxt_s - 0.05, last_end + 0.45)
        if t0 < 38.26:
            t1 = min(t1, 38.26)
        if t0 < 86.34 and t1 > 86.34:
            t1 = min(t1, 86.34)
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

def get_clip_frame_smooth(clips, key, t_rel, target_span=3.8):
    arr_list = clips.get(key)
    if not arr_list:
        return np.full((576, 1024, 3), 240, dtype=np.uint8)
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
        for ts in [7.20, 22.80, 32.20, 46.20, 56.20, 65.80, 73.50, 84.00, 94.60, 106.20, 108.50, 3.00]
    }
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    if not os.path.exists(aroll_path):
        aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    vid_keys = [
        ("ld_01_tired_reminding",        1024, 576),
        ("ld_02_consistent_posting",     1024, 576),
        ("ld_03_leader_filming_example", 1024, 576),
        ("ld_04_proactive_team_system",  1024, 576),
    ]
    clips = {}
    for ck, vw, vh in vid_keys:
        vp = os.path.join(MEDIA_DIR, f"{ck}.mp4")
        if os.path.exists(vp):
            clips[ck] = load_vid_frames_wh(vp, vw, vh)
            print(f"[HTPM261120] Loaded {ck}: {len(clips[ck])} frames", flush=True)
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
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    frame_idx = 0
    while True:
        rgb_raw = reader_a.read()
        mbuf    = reader_m.stdout.read(W * H)
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
        t = frame_idx / FPS

        z_cam, px_cam, py_cam = eval_camera_rig(t)
        if abs(z_cam - 1.0) < 1e-4 and abs(px_cam) < 1e-4 and abs(py_cam) < 1e-4:
            fg_rgb = rgb_raw
            m_arr  = matte_raw.astype(np.float32) / 255.0
        else:
            fg_im  = fit_cover_subpixel(rgb_raw, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam)
            m_rgb  = np.repeat(matte_raw[:, :, None], 3, axis=2)
            m_im   = fit_cover_subpixel(m_rgb, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam).convert("L")
            fg_rgb = np.array(fg_im)
            m_arr  = np.array(m_im, dtype=np.float32) / 255.0

        is_full_kobe_stage = (38.30 <= t <= 51.36) or (86.38 <= t <= 98.06)

        if not is_full_kobe_stage:
            # ==============================================================
            # MODE A: OUTDOOR TALKING HEAD + BEHIND-HEAD TITLE + LOWER KOBE STAGE
            # ==============================================================
            base_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

            # 1. Behind-Head Top Banner (y < 395) tucked behind RVM hair crown!
            if kobe_rgba is not None:
                upper_kobe = kobe_rgba.copy()
                upper_kobe[395:, :, 3] = 0
                if upper_kobe[:, :, 3].max() > 0:
                    base_im = Image.alpha_composite(base_im, Image.fromarray(upper_kobe, "RGBA"))
                    # Re-composite person RVM crown in front of behind-head title!
                    crown_alpha = np.zeros((H, W), dtype=np.float32)
                    crown_alpha[:420] = m_arr[:420]
                    base_im = Image.alpha_composite(base_im, Image.fromarray(np.dstack([fg_rgb, (crown_alpha * 255.0).astype(np.uint8)]), "RGBA"))

            comp_im = base_im

            # 2. Lower Left Google Flow Ingredients Video Cards (paired with Right Kobe SaaS Cards!)
            if 11.36 <= t < 28.58:
                vf = get_clip_frame_smooth(clips, "ld_01_tired_reminding", (t - 11.36) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(comp_im, vf, t, 11.38, 28.56, 330.0, 1395.0, 608, 496, "BẪY CŨ", "NHẮC VIỆC MỖI NGÀY • KIỆT SỨC", accent_rgb=(229, 72, 59))

            if 70.86 <= t < 76.54:
                vf = get_clip_frame_smooth(clips, "ld_03_leader_filming_example", (t - 70.86) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(comp_im, vf, t, 70.88, 76.50, 328.0, 1395.0, 604, 496, "LÀM GƯƠNG", "LEADER QUAY & ĐĂNG MỖI NGÀY", accent_rgb=(54, 86, 251))

            # 3. Foreground Lower Kobe Interactive Stage (y >= 395)
            if kobe_rgba is not None:
                lower_kobe = kobe_rgba.copy()
                lower_kobe[:395, :, 3] = 0
                if lower_kobe[:, :, 3].max() > 0:
                    comp_im = Image.alpha_composite(comp_im, Image.fromarray(lower_kobe, "RGBA"))
        else:
            # ==============================================================
            # MODE B: FULL 9:16 KOBE DOT-GRID UI + FLOW VIDEO + 416px IRIS PIP!
            # ==============================================================
            comp_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")
            if kobe_rgba is not None and kobe_rgba[:, :, 3].max() > 0:
                comp_im = Image.alpha_composite(comp_im, Image.fromarray(kobe_rgba, "RGBA"))

            if 38.30 <= t <= 51.36:
                vf2 = get_clip_frame_smooth(clips, "ld_02_consistent_posting", (t - 38.30) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(comp_im, vf2, t, 38.44, 51.24, 540.0, 390.0, 948, 396, "90 NGÀY", "XUẤT HIỆN ĐỀU ĐẶN • KHÁCH NHỚ TÊN", accent_rgb=(54, 86, 251))
                draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 38.30, 51.36, cx=540.0, cy=1482.0, diam=416)
            elif 86.38 <= t <= 98.06:
                vf4 = get_clip_frame_smooth(clips, "ld_04_proactive_team_system", (t - 86.38) % 3.8, target_span=3.8)
                draw_kobe_flow_video_card(comp_im, vf4, t, 86.50, 97.94, 540.0, 390.0, 948, 396, "CỘNG HƯỞNG", "ĐỘI NHÓM CHỦ ĐỘNG & NHIỆT HUYẾT", accent_rgb=(11, 138, 92))
                draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 86.38, 98.06, cx=540.0, cy=1482.0, diam=416)

        # ==============================================================
        # 4. CLEAN SENTENCE-CASE SUBTITLES AT y=1716..1780 (Zero Overlap!)
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
                    y_base = 1714.0 if len(g["lines"]) >= 2 else 1744.0
                    lh, gap = 60.0, 12.0

                    for li, ln in enumerate(g["lines"]):
                        word_renders, total_w = [], 0.0
                        for wi, (wtxt, ws, we) in enumerate(ln):
                            is_act = (ws - 0.04 <= t <= we + 0.18)
                            pulse  = 1.06 if is_act else 1.00
                            wlow   = wtxt.lower().rstrip(",.?!:;")
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

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"test_261120_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 450 == 0:
            el = time.time() - t_start
            print(f"  [HTPM261120] Rendered {frame_idx}/{TOTAL_FRAMES} frames ({frame_idx / el:.1f} fps)", flush=True)

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
        gp = os.path.join(CHECK_DIR, "htpm261120_kobe_test_grid.jpg")
        grid.save(gp, quality=93)
        print("Saved 12-panel Kobe test grid:", gp, flush=True)
    else:
        print(f"Done HTPM 261120 Master video: {frame_idx} frames in {time.time() - t_start:.1f}s", flush=True)

if __name__ == "__main__":
    main()
