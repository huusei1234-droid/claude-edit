import concurrent.futures, json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm7-261121"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll_v2")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
FONTS_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
KOBE_MOV  = os.path.join(PROJ_DIR, "kobe_overlays_v2.mov")
PREV_DL_MASTER = os.path.join(PROJ_DIR, "_master_dl_video_only.mp4")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
TOTAL_FRAMES = 1796  # 59.867s exact (stumble-free + Official FB CTA)

FONT_SUB_MAIN = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_CARD_LBL = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")

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

CAM_KEYFRAMES = [
    ( 0.00, 1.000, 0.000,  0.000, 0.35),
    ( 0.12, 1.022, 0.000,  0.000, 2.15),
    ( 2.38, 1.148, 0.004,  0.026, 0.46),
    ( 2.95, 1.176, 0.006,  0.030, 7.10),
    (10.24, 1.000, 0.000,  0.000, 0.44),
    (13.60, 1.046, 0.003,  0.006, 0.52),
    (29.48, 1.020, 0.000,  0.002, 0.48),
    (33.50, 1.062, 0.004,  0.010, 0.50),
    (38.90, 1.024, 0.000,  0.003, 0.28),  # Clean angle shift right across stumble removal @ 38.90s!
    (40.40, 1.056, 0.003,  0.008, 0.50),
    (52.52, 1.066, 0.004,  0.010, 0.50),  # Return from Full Kobe Stage #2: Official Facebook CTA!
    (55.60, 1.030, 0.000,  0.004, 0.65),
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

def apply_riser_optical_transition(comp_im, t, center_t=10.48, half_w=0.18):
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
    return Image.fromarray(np.clip(mix + bloom, 0.0, 255.0).astype(np.uint8), "RGB").convert("RGBA")

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
    f_t = get_font(FONT_CARD_LBL, 19)
    f_m = get_font(FONT_CARD_LBL, 21)
    dm = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bt = dm.textbbox((0, 0), tag_txt, font=f_t)
    bm = dm.textbbox((0, 0), main_txt, font=f_m)
    wt = bt[2] - bt[0] + 24
    wm = bm[2] - bm[0]
    pw, ph, pad = wt + wm + 42, 48, 8
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=24, fill=(255, 255, 255, 248), outline=(255, 255, 255, 255), width=2)
    d.rounded_rectangle([pad + 10, pad + 7, pad + 10 + wt, pad + ph - 7], radius=17, fill=(*accent_rgb, 255))
    d.text((pad + 22 - bt[0], pad + 24 - (bt[1] + bt[3]) * 0.5), tag_txt, font=f_t, fill=(255, 255, 255, 255))
    d.text((pad + 20 + wt - bm[0], pad + 24 - (bm[1] + bm[3]) * 0.5), main_txt, font=f_m, fill=(20, 20, 28, 255))
    _pill_cache[k] = im
    return im

def draw_kobe_flow_video_card(canvas_im, vf_rgb, t, st, en, cx, cy, pw, ph, tag_txt, main_txt, accent_rgb=(54, 86, 251), u_zoom=0.5):
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
        ry = int(30 * (0.28 + 0.72 * ur))
        al = int(225 * (1.0 - ur))
        if al > 4 and rx > 10 and ry > 4:
            rp = Image.new("RGBA", (rx * 2 + 16, ry * 2 + 16), (0, 0, 0, 0))
            ImageDraw.Draw(rp).ellipse([8, 8, rx * 2 + 8, ry * 2 + 8], outline=(*accent_rgb, al), width=3)
            paste_centered_rgba(canvas_im, rp, cx, cy + ph * 0.49)

    float_y = math.sin(t * 2.3) * 4.5

    pad = 20
    cw, ch = pw + pad * 2, ph + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + pw, pad + ph + 12], radius=32, fill=(18, 28, 68, 108))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    vis_im = fit_cover_subpixel(vf_rgb, pw, ph, zoom=1.02 + 0.05 * u_zoom)
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
        cx, cy + float_y + (1.0 - u_in) * (-84.0) - (1.0 - u_out) * 18.0,
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

    sub = fg_rgb[275:995, 185:905]
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

    paste_centered_rgba(canvas_im, card, cx, cy + math.sin(t * 2.1) * 3.5, scale=0.92 + 0.08 * op_sh, opacity=op_sh)

_sub_cache = {}
def render_thin_grad_word(text, size, palette="pearl", stroke_w=5):
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
    sa[:, :, 3] = np.clip(sb * 170.0, 0, 255).astype(np.uint8)
    base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(14, 18, 34, 248), stroke_width=stroke_w, stroke_fill=(14, 18, 34, 248))
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
        if 17.90 <= tc <= 29.48:
            return False
        if 44.20 <= tc <= 52.52:
            return False
        return True

    words = [
        [w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
        for seg in tr["segments"] for w in seg["words"]
        if w["word"].strip() and is_sub_allowed((w["start"] + w["end"]) * 0.5)
    ]

    COMPOUNDS = {
        ("nếp", "nhăn!"), ("nếp", "nhăn,"), ("nếp", "nhăn"), ("phụ", "nữ"),
        ("mỗi", "ngày"), ("cơ", "thể"), ("triệu", "đồng"), ("kem", "dưỡng,"),
        ("chống", "nắng,"), ("chăm", "sóc,"), ("chăm", "da."), ("tuổi", "30,"),
        ("thay", "đổi"), ("triệu", "chứng"), ("lập", "tức"), ("kết", "luận:"),
        ("nội", "tiết,"), ("lão", "hóa."), ("dấu", "hiệu"), ("bất", "thường"),
        ("kéo", "dài,"), ("kiểm", "tra"), ("chị", "em"),
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
                if re.search(r"[.?!…;:]$", prev_txt) or gap >= 0.35:
                    phrases.append(cur_p); cur_p = []
                elif re.search(r"[,]$", prev_txt) and (len(cur_p) >= 3 or dur_so_far >= 1.05):
                    phrases.append(cur_p); cur_p = []
                elif len(cur_p) >= 7 and prev_low not in {"rất", "một", "những", "các", "có", "đang"}:
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
                elif p[k][0][:1].isupper() and p[k][0].lower() not in {"hằng", "hằng.", "hằng,"}:
                    p[k][0] = p[k][0][0].lower() + p[k][0][1:]

    def split_balanced(p):
        tot_c = sum(len(x[0]) + 1 for x in p) - 1
        if len(p) <= 4 and tot_c <= 21:
            return [p]
        bk, bd = max(1, len(p) // 2), 9999
        for k in range(1, len(p)):
            c1 = sum(len(x[0]) + 1 for x in p[:k]) - 1
            c2 = sum(len(x[0]) + 1 for x in p[k:]) - 1
            d = abs(c1 - c2) + (6 if max(c1, c2) > 22 else 0)
            if d < bd:
                bd, bk = d, k
        return [p[:bk], p[bk:]]

    ROSE_W    = {"nhăn", "skincare", "serum", "nội", "tiết", "lão", "hóa", "30+"}
    COBALT_W  = {"30", "kiểm", "tra", "hiểu", "follow"}
    EMERALD_W = {"cơ", "thể", "khỏe", "đẹp", "cần"}

    cap_groups = []
    for i, p in enumerate(phrases):
        t0 = max(0.02, p[0][1] - 0.03)
        last_end = p[-1][2]
        nxt_s = phrases[i + 1][0][1] if i + 1 < len(phrases) else 59.80
        t1 = min(nxt_s - 0.05, last_end + 0.45)
        if t0 < 17.88 and t1 > 17.88:
            t1 = min(t1, 17.88)
        if t0 < 44.18 and t1 > 44.18:
            t1 = min(t1, 44.18)
        if t1 > t0 + 0.18:
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

SEQ_W1 = [
    (18.00, 21.75, "sk_01a_cycle_calendar",    "TÍN HIỆU #1",   "CHU KỲ KINH CÓ ĐỀU KHÔNG?",    (201, 24, 96), 4.5),
    (21.75, 25.45, "sk_01b_sleep_fatigue",     "TÍN HIỆU #2-3", "GIẤC NGỦ & CƠ THỂ MỆT MỎI?",   ( 54, 86, 251), 3.8),
    (25.45, 29.38, "sk_01c_mood_discomfort",   "TÍN HIỆU #4-5", "TÂM TRẠNG & KHÓ CHỊU PHỤ KHOA",(220, 38, 38), 4.2),
]
SEQ_W2 = [
    (29.58, 34.10, "sk_02a_age30_changes",     "TUỔI 30+",      "MỖI CƠ THỂ THAY ĐỔI KHÁC NHAU",( 11, 138, 92), 4.6),
    (34.10, 38.80, "sk_02b_no_self_panic",     "BÌNH TĨNH",     "ĐỪNG VỘI TỰ KẾT LUẬN LO SỢ!",  (201, 24, 96), 4.8),
]
SEQ_W3 = [
    (44.30, 47.38, "sk_03a_beyond_skin",       "KHÔNG CHỈ DA",  "ĐẸP TỪ GỐC SỨC KHỎE BÊN TRONG",(201, 24, 96), 3.4),
    (47.38, 50.00, "sk_03b_healthy_confident", "NỘI LỰC",       "KHỎE MẠNH & TỰ TIN MỖI NGÀY",  ( 11, 138, 92), 3.4),
    (50.00, 52.42, "sk_03c_comfortable_body",  "TRỌN VẸN",      "THOẢI MÁI TRONG CƠ THỂ MÌNH",  ( 54, 86, 251), 3.4),
]

def eval_multi_clip_window(clips, seq_items, t):
    active_idx = 0
    for idx, it in enumerate(seq_items):
        if t >= it[0]:
            active_idx = idx
    sub_st, sub_en, ck, tag, main_lbl, acc, clip_span = seq_items[active_idx]
    dur = max(0.5, sub_en - sub_st)
    t_rel = max(0.0, t - sub_st)
    vf = get_clip_frame_smooth(clips, ck, t_rel, target_span=max(dur, clip_span))
    if active_idx > 0 and t_rel < 0.24:
        prev_st, prev_en, prev_ck, _, _, _, prev_span = seq_items[active_idx - 1]
        prev_vf = get_clip_frame_smooth(clips, prev_ck, max(0.0, t - prev_st), target_span=max(prev_en - prev_st, prev_span))
        w = quintic_smooth(t_rel / 0.24)
        vf = np.clip(prev_vf.astype(np.float32) * (1.0 - w) + vf.astype(np.float32) * w, 0, 255).astype(np.uint8)
    u_zoom = septic_smooth(clamp01(t_rel / dur))
    return vf, tag, main_lbl, acc, u_zoom

VID_KEYS = [
    ("sk_01a_cycle_calendar",    1024, 576),
    ("sk_01b_sleep_fatigue",     1024, 576),
    ("sk_01c_mood_discomfort",   1024, 576),
    ("sk_02a_age30_changes",     1024, 576),
    ("sk_02b_no_self_panic",     1024, 576),
    ("sk_03a_beyond_skin",       1024, 576),
    ("sk_03b_healthy_confident", 1024, 576),
    ("sk_03c_comfortable_body",  1024, 576),
]

def compose_single_frame(frame_idx, rgb_raw, matte_raw, kobe_rgba, clips, cap_groups, ROSE_W, COBALT_W, EMERALD_W):
    t = frame_idx / FPS

    z_cam, px_cam, py_cam = eval_camera_rig(t)
    if abs(z_cam - 1.0) < 1e-4 and abs(px_cam) < 1e-4 and abs(py_cam) < 1e-4:
        fg_rgb = rgb_raw
        m_top  = matte_raw[:400]
    else:
        fg_im  = fit_cover_subpixel(rgb_raw, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam)
        fg_rgb = np.array(fg_im)
        if kobe_rgba is not None and kobe_rgba[:385, :, 3].max() > 0:
            m_rgb = np.repeat(matte_raw[:, :, None], 3, axis=2)
            m_top = np.array(fit_cover_subpixel(m_rgb, W, H, zoom=z_cam, pan_x=px_cam, pan_y=py_cam).convert("L"))[:400]
        else:
            m_top = matte_raw[:400]

    is_full_kobe_stage = (17.92 <= t <= 29.46) or (44.22 <= t <= 52.50)

    if not is_full_kobe_stage:
        comp_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")

        if kobe_rgba is not None and kobe_rgba[:385, :, 3].max() > 0:
            comp_im.alpha_composite(Image.fromarray(kobe_rgba[:385], "RGBA"), dest=(0, 0))
            crown_rgba = np.dstack([fg_rgb[:400], m_top])
            comp_im.alpha_composite(Image.fromarray(crown_rgba, "RGBA"), dest=(0, 0))

        # Lower-Left AI Video Card ONLY on Section 4 (29.52..38.84s); Section 7 (52.54..59.84s) displays Full-Width Official Facebook CTA Stage!
        if 29.52 <= t < 38.84:
            vf2, tg2, mn2, ac2, uz2 = eval_multi_clip_window(clips, SEQ_W2, t)
            draw_kobe_flow_video_card(comp_im, vf2, t, 29.58, 38.80, 324.0, 1332.0, 600, 462, tg2, mn2, accent_rgb=ac2, u_zoom=uz2)

        if kobe_rgba is not None and kobe_rgba[385:1600, :, 3].max() > 0:
            comp_im.alpha_composite(Image.fromarray(kobe_rgba[385:1600], "RGBA"), dest=(0, 385))
    else:
        comp_im = Image.fromarray(fg_rgb, "RGB").convert("RGBA")
        if kobe_rgba is not None and kobe_rgba[:, :, 3].max() > 0:
            comp_im.alpha_composite(Image.fromarray(kobe_rgba, "RGBA"), dest=(0, 0))

        if 17.92 <= t <= 29.46:
            vf1, tg1, mn1, ac1, uz1 = eval_multi_clip_window(clips, SEQ_W1, t)
            draw_kobe_flow_video_card(comp_im, vf1, t, 18.00, 29.38, 540.0, 386.0, 948, 392, tg1, mn1, accent_rgb=ac1, u_zoom=uz1)
            draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 17.92, 29.46, cx=540.0, cy=1482.0, diam=416)
        elif 44.22 <= t <= 52.50:
            vf3, tg3, mn3, ac3, uz3 = eval_multi_clip_window(clips, SEQ_W3, t)
            draw_kobe_flow_video_card(comp_im, vf3, t, 44.30, 52.42, 540.0, 386.0, 948, 392, tg3, mn3, accent_rgb=ac3, u_zoom=uz3)
            draw_kobe_416_iris_circle_pip(comp_im, rgb_raw, t, 44.22, 52.50, cx=540.0, cy=1482.0, diam=416)

    if not is_full_kobe_stage:
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                dt_in, dt_out = t - g["t0"], g["t1"] - t
                raw_si  = clamp01(dt_in / 0.20)
                raw_so  = clamp01(dt_out / 0.16)
                u_in    = ease_out_back_soft(raw_si, overshoot=1.05)
                u_out   = septic_smooth(raw_so)
                op_g    = min(quintic_smooth(clamp01(dt_in / 0.14)), u_out)
                sig_sub = (1.0 - quintic_smooth(raw_si)) * 3.8 + (1.0 - u_out) * 3.2
                if op_g <= 0.01:
                    break
                min_x, max_x, x_center = 54.0, 1026.0, 540.0
                cap_sz = 46.0
                y_base = 1602.0 if len(g["lines"]) >= 2 else 1630.0
                lh, gap = 66.0, 14.0

                line_infos = []
                max_eff_w = 0.0
                for li, ln in enumerate(g["lines"]):
                    word_renders, total_w = [], 0.0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_act = (ws - 0.04 <= t <= we + 0.18)
                        pulse  = 1.06 if is_act else 1.00
                        wlow   = wtxt.lower().rstrip(",.?!:;")
                        pal = "rose_satin" if wlow in ROSE_W else ("cobalt" if wlow in COBALT_W else ("emerald" if wlow in EMERALD_W else ("gold" if is_act else "pearl")))
                        sp_w = render_thin_grad_word(wtxt, cap_sz, palette=pal, stroke_w=5)
                        adv  = ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_SUB_MAIN, cap_sz)) + 3.0
                        word_renders.append((sp_w, adv, pulse))
                        total_w += adv + (gap if wi > 0 else 0.0)
                    fit_k = min(1.0, (max_x - min_x) / max(1.0, total_w))
                    eff_tot = total_w * fit_k
                    max_eff_w = max(max_eff_w, eff_tot)
                    line_infos.append((li, word_renders, fit_k, eff_tot))

                bg_w = int(min(1036.0, max_eff_w + 68.0))
                bg_h = int(len(line_infos) * 68 + 38)
                bg_cy = y_base + (len(line_infos) - 1) * lh * 0.5 + (1.0 - u_in) * 12.0
                bg_im = Image.new("RGBA", (bg_w, bg_h), (0, 0, 0, 0))
                ImageDraw.Draw(bg_im).rounded_rectangle([0, 0, bg_w - 1, bg_h - 1], radius=28, fill=(14, 19, 38, 106))
                paste_centered_rgba(comp_im, bg_im, x_center, bg_cy, scale=0.96 + 0.04 * u_in, opacity=op_g)

                for li, word_renders, fit_k, eff_tot in line_infos:
                    cur_x = x_center - eff_tot * 0.5
                    cur_y = y_base + li * lh + (1.0 - u_in) * 12.0
                    for sp_w, adv, pulse in word_renders:
                        eff_adv = adv * fit_k
                        paste_centered_rgba(comp_im, sp_w, cur_x + eff_adv * 0.5, cur_y, scale=fit_k * pulse, opacity=op_g, blur_sigma=sig_sub)
                        cur_x += eff_adv + gap * fit_k
                break

    comp_im = apply_riser_optical_transition(comp_im, t, center_t=10.48, half_w=0.18)
    return comp_im

def render_chunk(args):
    c_idx, f_start, f_end = args
    n_frames = f_end - f_start
    ss_sec = f"{f_start / FPS:.6f}"
    chunk_mp4 = os.path.join(PROJ_DIR, f"_v2_chunk_{c_idx:02d}.mp4")

    cam_a_path = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    mat_a_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    clips = {ck: load_vid_frames_wh(os.path.join(MEDIA_DIR, f"{ck}.mp4"), vw, vh) for ck, vw, vh in VID_KEYS}
    cap_groups, ROSE_W, COBALT_W, EMERALD_W = load_captions_clean()

    pa = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", cam_a_path, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    ma = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", mat_a_path, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "gray",  "-"], stdout=subprocess.PIPE)
    pk = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", KOBE_MOV,   "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgba",  "-"], stdout=subprocess.PIPE)

    writer = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        chunk_mp4
    ], stdin=subprocess.PIPE)

    prev_matte = np.zeros((H, W), dtype=np.uint8)
    prev_kobe  = None
    for li in range(n_frames):
        ba  = pa.stdout.read(W * H * 3)
        bma = ma.stdout.read(W * H)
        bk  = pk.stdout.read(W * H * 4)
        if len(ba) < W * H * 3:
            break
        rgb_a   = np.frombuffer(ba,  dtype=np.uint8).reshape((H, W, 3))
        matte_a = np.frombuffer(bma, dtype=np.uint8).reshape((H, W)) if len(bma) == W * H else prev_matte
        prev_matte = matte_a
        kobe_r  = np.frombuffer(bk,  dtype=np.uint8).reshape((H, W, 4)) if len(bk) == W * H * 4 else prev_kobe
        prev_kobe = kobe_r

        comp_im = compose_single_frame(f_start + li, rgb_a, matte_a, kobe_r, clips, cap_groups, ROSE_W, COBALT_W, EMERALD_W)
        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())

    writer.stdin.close(); writer.wait()
    for p in (pa, ma, pk):
        p.stdout.close(); p.wait()
    print(f"[Chunk {c_idx}] Done frames {f_start}..{f_end - 1}", flush=True)
    return chunk_mp4

def run_test_grid():
    clips = {ck: load_vid_frames_wh(os.path.join(MEDIA_DIR, f"{ck}.mp4"), vw, vh) for ck, vw, vh in VID_KEYS}
    cap_groups, ROSE_W, COBALT_W, EMERALD_W = load_captions_clean()
    cam_a_path = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    mat_a_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    # Focus test grid especially around 38.0..41.5s (stumble removal) and 53.0..58.5s (Official Facebook Follow CTA)!
    ts_list = [37.50, 38.60, 39.20, 40.00, 42.00, 46.50, 50.80, 53.30, 54.60, 54.90, 56.50, 58.80]
    imgs_t = []
    for ts in ts_list:
        f_idx = int(round(ts * FPS))
        ss = f"{f_idx / FPS:.6f}"
        def grab(p, pfmt, nbytes, shape):
            raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", p, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", pfmt, "-"])
            return np.frombuffer(raw[:nbytes], dtype=np.uint8).reshape(shape)
        ra = grab(cam_a_path, "rgb24", W*H*3, (H, W, 3))
        ma = grab(mat_a_path, "gray",  W*H,   (H, W))
        kr = grab(KOBE_MOV,   "rgba",  W*H*4, (H, W, 4))
        comp_im = compose_single_frame(f_idx, ra, ma, kr, clips, cap_groups, ROSE_W, COBALT_W, EMERALD_W)
        im_r = comp_im.convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(im_r)
        d.rounded_rectangle([8, 8, 108, 38], radius=8, fill=(14, 18, 30))
        d.text((16, 14), f"t={ts:.2f}s", fill=(255, 220, 80))
        imgs_t.append(im_r)

    grid = Image.new("RGB", (270 * 6, 480 * 2))
    for i, im in enumerate(imgs_t):
        grid.paste(im, ((i % 6) * 270, (i // 6) * 480))
    gp = os.path.join(CHECK_DIR, "htpm7_v2_fb_test_grid.jpg")
    grid.save(gp, quality=93)
    print("Saved 12-panel V2 FB CTA test grid:", gp, flush=True)

def main():
    if "--test" in sys.argv:
        run_test_grid()
        return

    t0 = time.time()
    # Reuse exact identical prefix frames 0..1019 (0.000s..34.000s) from _master_dl_video_only.mp4!
    F_REUSE = 1020
    prefix_mp4 = os.path.join(PROJ_DIR, "_v2_prefix_0_1019.mp4")
    if os.path.exists(PREV_DL_MASTER):
        print(f"[FastPrefix] Extracting identical frames 0..{F_REUSE-1} from previous master...", flush=True)
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", PREV_DL_MASTER,
            "-frames:v", str(F_REUSE), "-r", "30", "-fps_mode", "cfr", "-an",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
            prefix_mp4
        ], check=True)
        rem = TOTAL_FRAMES - F_REUSE
        N_WORKERS = 4
        step = math.ceil(rem / N_WORKERS)
        tasks = [(i, F_REUSE + i * step, min(TOTAL_FRAMES, F_REUSE + (i + 1) * step)) for i in range(N_WORKERS) if F_REUSE + i * step < TOTAL_FRAMES]
        print(f"[HTPM7-V2 FastRender] Rendering ONLY modified tail {rem} frames ({F_REUSE}..{TOTAL_FRAMES-1}) across {len(tasks)} GPU workers...", flush=True)
        with concurrent.futures.ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            tail_chunks = list(ex.map(render_chunk, tasks))
        all_chunks = [prefix_mp4] + tail_chunks
    else:
        N_WORKERS = 4
        step = math.ceil(TOTAL_FRAMES / N_WORKERS)
        tasks = [(i, i * step, min(TOTAL_FRAMES, (i + 1) * step)) for i in range(N_WORKERS) if i * step < TOTAL_FRAMES]
        with concurrent.futures.ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            all_chunks = list(ex.map(render_chunk, tasks))

    list_txt = os.path.join(PROJ_DIR, "_v2_chunks.txt")
    with open(list_txt, "w", encoding="utf-8") as f:
        for cf in all_chunks:
            f.write("file '" + cf.replace("\\", "/") + "'\n")

    raw_vid_out = os.path.join(PROJ_DIR, "_master_v2_video_only.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", raw_vid_out], check=True)
    for cf in all_chunks + [list_txt]:
        if os.path.exists(cf):
            os.remove(cf)
    print(f"[HTPM7-V2 FastRender] ALL {TOTAL_FRAMES} FRAMES READY IN {time.time() - t0:.1f}s!", flush=True)

if __name__ == "__main__":
    main()
