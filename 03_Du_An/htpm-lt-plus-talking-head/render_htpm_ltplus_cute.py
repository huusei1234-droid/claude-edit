import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR   = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
PHOTOS_DIR = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\Ảnh"
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

FONT_TITLE  = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7182504807289065985\0a5333de6f4d592cb2d2390d68b31efb\Oswald-Bold.ttf"
FONT_WIDE   = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf"
FONT_CAP    = r"C:\Windows\Fonts\palabi.ttf"
FONT_SCRIPT = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\6990292000264163842\840d58433e5d79e2599f155e83c2defb\ZYVNA Dreamboat.ttf"
FONT_SUB    = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7542214368361057553\d376267c892ee3a53654ae93a78dcfb7\font.ttf"

_font_cache = {}
def get_font(path, size):
    key = (path, max(10, int(round(size))))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, key[1])
    return _font_cache[key]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def ease_out_cubic(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 3.0

def ease_out_back(u, s=1.35):
    u = clamp01(u) - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0

def smoothstep(u):
    u = clamp01(u)
    return u * u * (3.0 - 2.0 * u)

def smooth_in_out_env(t, t0, t1, d_in=0.32, d_out=0.28):
    if t <= t0 or t >= t1:
        return 0.0
    a_in = ease_out_cubic((t - t0) / max(0.04, d_in)) if (t - t0) < d_in else 1.0
    a_out = smoothstep((t1 - t) / max(0.04, d_out)) if (t1 - t) < d_out else 1.0
    return min(a_in, a_out)

def fit_cover(rgb_arr, target_w, target_h, zoom=1.0):
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    nw = max(target_w, int(round(sw * base_scale)))
    nh = max(target_h, int(round(sh * base_scale)))
    im = Image.fromarray(rgb_arr, "RGB").resize((nw, nh), Image.Resampling.BILINEAR)
    x0 = (nw - target_w) // 2
    y0 = (nh - target_h) // 2
    return im.crop((x0, y0, x0 + target_w, y0 + target_h))

# ======================================================================
# 1. BRIGHT SUNNY COLOR POLISH (ZERO DARKENING!)
# ======================================================================
def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.96) * 1.015, 0.0, 1.0)
    lr = np.clip(y * 255.0 * 1.016, 0, 255).astype(np.uint8)
    lg = np.clip(y * 255.0 * 1.005, 0, 255).astype(np.uint8)
    lb = np.clip(y * 255.0 * 0.996, 0, 255).astype(np.uint8)
    return lr, lg, lb

BRIGHT_LUT = _build_bright_lut()

def polish_bright_frame(rgb):
    out = np.empty_like(rgb)
    out[:, :, 0] = BRIGHT_LUT[0][rgb[:, :, 0]]
    out[:, :, 1] = BRIGHT_LUT[1][rgb[:, :, 1]]
    out[:, :, 2] = BRIGHT_LUT[2][rgb[:, :, 2]]
    return out

# ======================================================================
# 2. CUTE PUFFY STICKER TEXT & GLOWING CHEST CAPTIONS
# ======================================================================
_sprite_cache = {}
def render_cute_text_sprite(text, font_path, size, top_col, bot_col=None, stroke_col=(255, 255, 255), stroke_w=8, glow_col=None, glow_rad=10, shadow_alpha=95):
    bot_col = bot_col or top_col
    key = ("cute", text, font_path, int(round(size)), top_col, bot_col, stroke_col, stroke_w, glow_col, int(round(glow_rad)), shadow_alpha)
    if key in _sprite_cache:
        return _sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(max(glow_rad * 2.8, 12) + stroke_w + 16)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    if glow_col and glow_rad > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(0, stroke_w // 2), stroke_fill=255)
        g1 = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad * 0.8)), dtype=np.float32)
        g2 = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad * 2.0)), dtype=np.float32)
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0] = glow_col[0]; ga[:, :, 1] = glow_col[1]; ga[:, :, 2] = glow_col[2]
        ga[:, :, 3] = np.clip(g1 * 0.70 + g2 * 0.42, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 3, oy + 6), text, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)
        sm_b = np.array(sm.filter(ImageFilter.GaussianBlur(radius=6)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0] = 28; sa[:, :, 1] = 32; sa[:, :, 2] = 48
        sa[:, :, 3] = np.clip(sm_b * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    if stroke_w > 0 and stroke_col is not None:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        base = Image.alpha_composite(base, st_im)

    mask_im = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), text, font=font, fill=255)
    arr_m = np.array(mask_im, dtype=np.float32) / 255.0
    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)[:, None]
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.uint8)
    for c in range(3):
        grad_rgb[:, :, c] = np.clip(top_col[c] * (1.0 - yy) + bot_col[c] * yy, 0, 255).astype(np.uint8)
    fill_im = Image.fromarray(np.dstack([grad_rgb, (arr_m * 255.0).astype(np.uint8)]), "RGBA")
    base = Image.alpha_composite(base, fill_im)

    if len(_sprite_cache) > 650:
        _sprite_cache.clear()
    _sprite_cache[key] = base
    return base

def paste_centered(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0, angle=0.0, blur_px=0.0):
    if opacity <= 0.01 or scale <= 0.02:
        return
    im = sprite_im
    if abs(scale - 1.0) > 0.008:
        nw = max(2, int(round(im.width * scale)))
        nh = max(2, int(round(im.height * scale)))
        im = im.resize((nw, nh), Image.Resampling.BILINEAR)
    if abs(angle) > 0.15:
        im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    if blur_px >= 0.6:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(12.0, blur_px)))
    if opacity < 0.995:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")
    px = int(round(cx - im.width / 2.0))
    py = int(round(cy - im.height / 2.0))
    canvas_im.alpha_composite(im, dest=(px, py))

# ======================================================================
# 3. CUTE CHATGPT 3D STICKER CARDS + CONFETTI SPARKLE BURSTS
# ======================================================================
_sticker_cache = {}
def load_chatgpt_stickers():
    names = ["hook1", "hook2", "hook3", "micro", "herbs", "cta"]
    out = {}
    for k in names:
        p = os.path.join(MEDIA_DIR, f"{k}.png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA")
            arr = np.array(im)
            non_white = (arr[:, :, 0] < 246) | (arr[:, :, 1] < 246) | (arr[:, :, 2] < 246)
            ys, xs = np.where(non_white)
            if len(xs) > 100:
                pad_c = int(im.width * 0.06)
                x0, x1 = max(0, int(xs.min()) - pad_c), min(im.width, int(xs.max()) + pad_c)
                y0, y1 = max(0, int(ys.min()) - pad_c), min(im.height, int(ys.max()) + pad_c)
                side = max(x1 - x0, y1 - y0)
                cx_c, cy_c = (x0 + x1) // 2, (y0 + y1) // 2
                hx = side // 2
                im = im.crop((max(0, cx_c - hx), max(0, cy_c - hx), min(im.width, cx_c + hx), min(im.height, cy_c + hx)))
            out[k] = im
    for k in names:
        if k not in out and out:
            out[k] = next(iter(out.values()))
    return out

def render_cute_sticker_badge(stickers_dict, key, size_px, accent_rgb):
    S = size_px
    ckey = (key, S, accent_rgb)
    if ckey not in _sticker_cache:
        pad = int(round(S * 0.09))
        cs = S - pad * 2
        rad = int(round(cs * 0.26))

        base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 7, pad + cs, pad + cs + 7], radius=rad, fill=(45, 30, 50, 82))
        sh = sh.filter(ImageFilter.GaussianBlur(radius=9))
        base = Image.alpha_composite(base, sh)

        ImageDraw.Draw(base).rounded_rectangle([pad - 5, pad - 5, pad + cs + 4, pad + cs + 4], radius=rad + 5, fill=(255, 255, 255, 255))

        rmask = Image.new("L", (cs, cs), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, cs - 1, cs - 1], radius=rad, fill=255)
        art_src = stickers_dict[key].convert("RGB")
        art = art_src.resize((cs, cs), Image.Resampling.LANCZOS)
        layer_art = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        layer_art.paste(art, (pad, pad), mask=rmask)
        base = Image.alpha_composite(base, layer_art)

        ImageDraw.Draw(base).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=(*accent_rgb, 238), width=5)

        sx, sy, sr = pad + cs - 10, pad + 12, 13
        d = ImageDraw.Draw(base)
        d.polygon([
            (sx, sy - sr), (sx + 4, sy - 4), (sx + sr, sy), (sx + 4, sy + 4),
            (sx, sy + sr), (sx - 4, sy + 4), (sx - sr, sy), (sx - 4, sy - 4)
        ], fill=(255, 210, 65, 255), outline=(255, 255, 255, 255))
        _sticker_cache[ckey] = base

    return _sticker_cache[ckey]

def draw_cute_confetti_burst(canvas_im, cx, cy, t_now, t0, diam=84):
    dt = t_now - t0
    if dt < 0 or dt > 0.48:
        return
    u = dt / 0.48
    e = ease_out_cubic(u)
    op = smoothstep(1.0 - u)
    r = int(round(diam * 0.45 * (0.55 + 1.15 * e)))
    sz = r * 2 + 60
    bim = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    dr = ImageDraw.Draw(bim)
    cc = sz // 2
    dr.ellipse([cc - r, cc - r, cc + r, cc + r], outline=(255, 130, 170, int(225 * op)), width=max(2, int(5 * (1.0 - 0.6 * u))))
    colors = [(255, 118, 162), (75, 220, 175), (255, 210, 75), (105, 185, 255), (255, 155, 115), (185, 140, 255)]
    for i, col in enumerate(colors):
        ang = math.radians(i * 60.0 + 25.0 * u)
        dist = r * 1.18
        dx = cc + int(dist * math.cos(ang))
        dy = cc + int(dist * math.sin(ang))
        dot_r = max(2, int(7 * (1.0 - 0.5 * u)))
        dr.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill=(*col, int(245 * op)))
    canvas_im.alpha_composite(bim, dest=(int(cx - cc), int(cy - cc)))

# ======================================================================
# 4. DYNAMIC VIDEO BACKDROP BEHIND SPEAKER (T.behind, ZERO DARKENING!)
# ======================================================================
def draw_behind_speaker_video(canvas_im, vid_rgb, t_now, st, en, ribbon_txt, accent_col=(245, 108, 148)):
    env = smooth_in_out_env(t_now, st, en, d_in=0.36, d_out=0.32)
    if env <= 0.005:
        return
    dt = t_now - st
    dur = max(0.2, en - st)

    vw, vh = 1032, 845
    z_v = 1.03 + 0.055 * smoothstep(dt / dur)
    crop_im = fit_cover(vid_rgb, vw, vh, zoom=z_v).convert("RGBA")

    rad = 56
    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=rad, fill=255)

    card_w, card_h = vw + 36, vh + 52
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))

    sh = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 24, 18 + vw, 24 + vh], radius=rad, fill=(45, 30, 50, 72))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=12))
    card = Image.alpha_composite(card, sh)

    ImageDraw.Draw(card).rounded_rectangle([8, 10, 28 + vw, 30 + vh], radius=rad + 10, fill=(255, 255, 255, 252))
    art_layer = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    art_layer.paste(crop_im, (18, 20), mask=vmask)
    card = Image.alpha_composite(card, art_layer)
    ImageDraw.Draw(card).rounded_rectangle([18, 20, 18 + vw - 1, 20 + vh - 1], radius=rad, outline=(*accent_col, 240), width=6)

    if ribbon_txt:
        sp_r = render_cute_text_sprite(ribbon_txt, FONT_WIDE, 30, (255, 255, 255), (255, 255, 255), stroke_col=accent_col, stroke_w=0, shadow_alpha=0)
        pw = min(980, sp_r.width + 52)
        ph = 58
        px1 = (card_w - pw) // 2
        py1 = 2
        ImageDraw.Draw(card).rounded_rectangle([px1 - 4, py1 - 4, px1 + pw + 4, py1 + ph + 4], radius=30, fill=(255, 255, 255, 255))
        ImageDraw.Draw(card).rounded_rectangle([px1, py1, px1 + pw, py1 + ph], radius=28, fill=(*accent_col, 255))
        fit_r = min(1.0, (pw - 30) / max(1.0, float(sp_r.width - 20)))
        paste_centered(card, sp_r, card_w // 2, py1 + ph // 2, scale=fit_r)

    glide_y = (1.0 - env) * (-34.0)
    sc = 0.95 + 0.05 * env
    paste_centered(canvas_im, card, 540, 458 + glide_y, scale=sc, opacity=env)

def draw_cute_ingredient_pills(canvas_im, t_now):
    """
    At 33.65s - 41.35s while listing the 6 botanical & pH ingredients of LT PLUS Hằng Thu,
    6 adorable pastel pill badges pop in symmetrically on left & right (100% Face-Safe & Box-Safe!).
    """
    t_end = 41.35
    if t_now < 33.62 or t_now >= t_end:
        return
    pills = [
        (33.68, "Hoàng Bá",      (245, 156, 62),  188, 760, -1),
        (34.70, "Ích Mẫu",       (245, 102, 146), 892, 760, +1),
        (35.14, "Kim Ngân Hoa",  (250, 128, 92),  188, 846, -1),
        (36.18, "Trà Xanh",      (48,  188, 124), 892, 846, +1),
        (37.02, "Trầu Không",    (44,  174, 156), 188, 932, -1),
        (37.72, "Acid Lactic",   (72,  162, 248), 892, 932, +1),
    ]
    out_fade = smoothstep((t_end - t_now) / 0.30) if (t_end - t_now) < 0.30 else 1.0
    for st_p, label, col, cx, cy, side in pills:
        if t_now < st_p:
            continue
        dt = t_now - st_p
        u = ease_out_back(min(1.0, dt / 0.34), s=1.25)
        op = min(1.0, dt / 0.14) * out_fade
        sp_t = render_cute_text_sprite(label, FONT_WIDE, 29, (255, 255, 255), stroke_w=0, shadow_alpha=0)
        pw, ph = max(292, sp_t.width + 38), 62
        card = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
        dr = ImageDraw.Draw(card)
        dr.rounded_rectangle([8, 12, 8 + pw, 12 + ph], radius=32, fill=(35, 30, 48, 65))
        card = card.filter(ImageFilter.GaussianBlur(radius=4))
        dr = ImageDraw.Draw(card)
        dr.rounded_rectangle([8, 6, 8 + pw + 6, 6 + ph + 6], radius=34, fill=(255, 255, 255, 252))
        dr.rounded_rectangle([11, 9, 11 + pw, 9 + ph], radius=31, fill=(*col, 248))
        paste_centered(card, sp_t, 11 + pw // 2, 9 + ph // 2)
        slide_x = cx + side * (1.0 - min(1.0, u)) * 68.0
        paste_centered(canvas_im, card, slide_x, cy, scale=0.82 + 0.18 * u, opacity=op)

# ======================================================================
# 5. TIMELINE, PRODUCT SHOWCASE & CAPTION BUILDER
# ======================================================================
ZOOM_KEYS = [
    (0.00, 1.01),
    (3.98, 1.05),
    (10.82, 1.02),
    (13.06, 1.06),
    (17.00, 1.03),
    (23.22, 1.07),
    (30.84, 1.03),
    (33.68, 1.06),
    (41.62, 1.02),
    (45.92, 1.06),
    (50.18, 1.03),
    (53.96, 1.06),
    (59.18, 1.02),
]

def get_smooth_zoom(t):
    cur = ZOOM_KEYS[0][1]
    for i in range(len(ZOOM_KEYS)):
        t0, z1 = ZOOM_KEYS[i]
        if t < t0:
            break
        z0 = ZOOM_KEYS[i - 1][1] if i > 0 else z1
        u = smoothstep(min(1.0, (t - t0) / 0.45))
        cur = z0 + (z1 - z0) * u
    return cur

BEHIND_VID_SPANS = [
    (3.98,  10.60, "vid1",        "SINH HOẠT & DẤU HIỆU CẦN LƯU Ý",      (250, 118, 156)),
    (13.05, 22.95, "vid2",        "LỘ TUYẾN ≠ NHIỄM TRÙNG / UNG THƯ",    (88,  176, 246)),
    (23.30, 30.72, "vid3",        "BÁC SĨ ĐÁNH GIÁ ĐÚNG NGUYÊN NHÂN",    (58,  194, 148)),
    (30.88, 33.58, "ltplus_real", "VIÊN ĐẶT PHỤ KHOA LT PLUS HẰNG THU",  (242, 92,  140)),
    (33.65, 41.52, "vid4",        "CÔNG THỨC 6 THÀNH PHẦN CHỌN LỌC",     (52,  186, 128)),
    (45.92, 50.12, "ltplus_real2","LT PLUS NHÀ HẰNG THU CHÍNH HÃNG",     (242, 92,  140)),
]

CUTE_HEADLINES = [
    ("HIỂU ĐÚNG TRƯỚC TIÊN", 10.75, 12.95, 102, (245, 98, 142),  (222, 68, 116)),
    ("HỖ TRỢ ĐÚNG CÁCH",     41.65, 45.82, 106, (52,  186, 128), (34,  152, 102)),
    ("NHẮN LT PLUS NGAY",    50.22, 58.95, 108, (245, 98, 142),  (222, 68, 116)),
]

STICKER_PLACES = [
    # 3 Overhead Hook Kawaii Stickers (Rainbow Arc)
    ("hook1", 0.42,  3.75, 205,  290, 236, -10.0, (255, 138, 172)),
    ("hook2", 0.60,  3.75, 540,  225, 246,   0.0, (98,  208, 242)),
    ("hook3", 0.78,  3.75, 875,  290, 236,  10.0, (88,  212, 162)),
    # Body Kawaii Stickers on clean left desk/plant zone (100% clear of right-side pink LT PLUS box!)
    ("hook2", 4.10, 10.50, 202, 1435, 244,  -3.0, (98,  208, 242)),
    ("micro",13.20, 22.85, 202, 1435, 248,   2.8, (168, 142, 250)),
    ("hook3",23.45, 30.65, 202, 1435, 248,  -2.5, (88,  212, 162)),
    ("herbs",33.75, 41.42, 202, 1435, 252,   2.8, (76,  198, 138)),
    ("cta",  50.32, 58.95, 202, 1435, 254,  -2.5, (255, 118, 158)),
]

CONFETTI_BURSTS = [
    (205, 290, 0.47, 82), (540, 225, 0.65, 88), (875, 290, 0.83, 82),
    (202, 1435, 4.16, 84), (202, 1435, 13.26, 84), (202, 1435, 23.51, 84),
    (202, 1435, 33.81, 86), (202, 1435, 50.38, 88),
]

def load_captions_htpmlt():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    # Skip Hook (0..3.78s) since Hook has custom 3-line kawaii typography
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if (w["start"] + w["end"]) * 0.5 >= 3.85
    ]

    groups, cur, line = [], [], []
    def flush_line():
        nonlocal line
        if line:
            cur.append(line)
            line = []
    def flush_group():
        nonlocal cur
        flush_line()
        if cur:
            groups.append(cur)
            cur = []

    prev = None
    for w in words:
        txt = w["word"].strip()
        if not txt:
            continue
        if prev is not None and (w["start"] - prev["end"]) >= 0.34:
            flush_group()
        if line and (len(line) >= 3 or sum(len(x[0]) + 1 for x in line) + len(txt) > 15):
            flush_line()
        if len(cur) >= 2 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!…:;]$", txt):
            flush_group()
    flush_group()

    BUTTER_WORDS = {
        "hiểu", "đúng,", "đúng", "tế", "bào", "tuyến", "bác", "sĩ", "nguyên", "nhân,",
        "LT", "PLUS", "LT PLUS", "Hoàng", "Bá,", "Ích", "Mẫu,", "Kim", "Ngân", "Hoa,",
        "Trà", "Xanh,", "Trầu", "Không", "Acid", "Lactic.", "hiệu", "quả", "kỹ"
    }
    SAKURA_WORDS = {
        "Khí", "hư", "không", "phải", "ung", "thư.", "phiền", "toái,",
        "Hằng", "Thu,", "hỗ", "trợ", "phụ", "khoa,", "Nhắn"
    }
    STROKE_UP_WORDS = {"đúng,", "LT", "PLUS", "LT PLUS", "Hoàng", "Lactic.", "Nhắn"}

    cap_groups = []
    for i, g in enumerate(groups):
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else 59.05
        t1 = min(nxt, last_end + 0.45) if (nxt - last_end) > 0.55 else nxt
        cap_groups.append({"t0": g[0][0][1], "t1": t1, "lines": g})
    return cap_groups, BUTTER_WORDS, SAKURA_WORDS, STROKE_UP_WORDS

def build_ltplus_real_showcase_frames(n_frames=135, variant=1):
    """
    Builds a bright, airy 1280x720 high-key sakura-blush studio showcase directly from the
    authentic 4K RGBA LT PLUS Hằng Thu studio cutouts (4.png, 6.png, 2.png) — 0% AI text distortion!
     Positioned cleanly in upper y=35..520 of the 1280x720 canvas so the Pharmacist's head at the
    bottom never hides the LT PLUS HẰNG THU brand logo!
    """
    box_closed = Image.open(os.path.join(PHOTOS_DIR, "4.png")).convert("RGBA")
    box_open   = Image.open(os.path.join(PHOTOS_DIR, "6.png")).convert("RGBA")
    bottle     = Image.open(os.path.join(PHOTOS_DIR, "2.png")).convert("RGBA")

    box_closed.thumbnail((560, 440), Image.Resampling.LANCZOS)
    box_open.thumbnail((360, 470), Image.Resampling.LANCZOS)
    bottle.thumbnail((235, 360), Image.Resampling.LANCZOS)

    # Pre-build airy pastel sakura-cream studio stage background (1280x720)
    vw, vh = 1280, 720
    yy = np.linspace(0.0, 1.0, vh, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, vw, dtype=np.float32)[None, :]
    rad_glow = np.exp(-(xx * xx * 1.2 + (yy - 0.36) ** 2 * 2.8))
    bg = np.zeros((vh, vw, 3), dtype=np.uint8)
    bg[:, :, 0] = np.clip(253 + 2 * rad_glow, 0, 255).astype(np.uint8)
    bg[:, :, 1] = np.clip(234 + 19 * rad_glow - 8 * yy, 0, 255).astype(np.uint8)
    bg[:, :, 2] = np.clip(242 + 12 * rad_glow - 5 * yy, 0, 255).astype(np.uint8)
    bg_base = Image.fromarray(bg, "RGB").convert("RGBA")

    # Soft studio podium reflection arc
    pod = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pod)
    pd.ellipse([180, 435, 1100, 610], fill=(255, 255, 255, 175), outline=(255, 195, 215, 210), width=4)
    pod = pod.filter(ImageFilter.GaussianBlur(radius=3))
    bg_base = Image.alpha_composite(bg_base, pod)

    frames = []
    for i in range(n_frames):
        u = i / max(1.0, float(n_frames - 1))
        s = smoothstep(u)
        canvas = bg_base.copy()

        # Soft floating pastel bokeh orbs
        bok = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bok)
        for bi, (bx0, by0, br, bcol) in enumerate([
            (150, 160, 42, (255, 165, 195, 85)),
            (1120, 150, 48, (255, 215, 130, 85)),
            (210, 410, 32, (135, 225, 195, 80)),
            (1080, 390, 36, (255, 155, 190, 85)),
        ]):
            ox = bx0 + int(math.sin(u * math.pi * 2 + bi) * 18)
            oy = by0 + int(math.cos(u * math.pi * 2 + bi * 1.3) * 14)
            bd.ellipse([ox - br, oy - br, ox + br, oy + br], fill=bcol)
        bok = bok.filter(ImageFilter.GaussianBlur(radius=8))
        canvas = Image.alpha_composite(canvas, bok)

        if variant == 1:
            # Closed Pink Box left-center + Bottle right-center (100% inside 1032x845 safe zone!)
            paste_centered(canvas, box_closed, 515 - int(8 * s), 278, scale=0.82 + 0.05 * s)
            paste_centered(canvas, bottle,     835 + int(8 * s), 296, scale=0.83 + 0.06 * s)
        else:
            # Trio hero: Open Magnetic Box + Closed Box + Bottle (100% inside 1032x845 safe zone!)
            paste_centered(canvas, box_open,   380 - int(6 * s), 268, scale=0.73 + 0.04 * s)
            paste_centered(canvas, box_closed, 668,              284, scale=0.73 + 0.05 * s)
            paste_centered(canvas, bottle,     918 + int(6 * s), 298, scale=0.76 + 0.05 * s)

        frames.append(np.array(canvas.convert("RGB")))
    return frames

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
    frames = []
    nbytes = vw * vh * 3
    while True:
        b = proc.stdout.read(nbytes)
        if len(b) < nbytes:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)))
    proc.stdout.close()
    proc.wait()
    return frames

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    test_frames = {int(round(ts * FPS)) for ts in [1.45, 6.50, 15.50, 26.50, 32.00, 38.20, 47.80, 55.20]}
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    stickers = load_chatgpt_stickers()
    print("Loaded Cute ChatGPT stickers:", list(stickers.keys()))

    b_clips = {}
    for vk in ["vid1", "vid2", "vid3", "vid4"]:
        vp = os.path.join(MEDIA_DIR, f"{vk}.mp4")
        if os.path.exists(vp):
            b_clips[vk] = load_vid_frames_wh(vp, 1280, 720)
    b_clips["ltplus_real"]  = build_ltplus_real_showcase_frames(95, variant=1)
    b_clips["ltplus_real2"] = build_ltplus_real_showcase_frames(135, variant=2)

    cap_groups, BUTTER_WORDS, SAKURA_WORDS, STROKE_UP_WORDS = load_captions_htpmlt()

    legal_sp = render_cute_text_sprite(
        "Sản phẩm chăm sóc phụ khoa • Đọc kỹ hướng dẫn sử dụng trước khi dùng",
        FONT_SUB, 21, (250, 248, 250), stroke_col=(32, 22, 36), stroke_w=3, shadow_alpha=0
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_htpm_lt_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    yy_g, xx_g = np.ogrid[0:H, 0:W]
    desk_mask  = np.clip((yy_g.astype(np.float32) - 1455.0) / 55.0, 0.0, 1.0)
    plant_mask = np.clip((225.0 - xx_g.astype(np.float32)) / 65.0, 0.0, 1.0) * np.clip((yy_g.astype(np.float32) - 960.0) / 80.0, 0.0, 1.0)
    box_protect = np.clip((xx_g.astype(np.float32) - 540.0) / 60.0, 0.0, 1.0) * np.clip((yy_g.astype(np.float32) - 1215.0) / 55.0, 0.0, 1.0)
    static_fg_guard = np.maximum(desk_mask, np.maximum(plant_mask * 0.92, box_protect))

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

        # 1. Smooth Gentle Camera Zoom around face [540, 740]
        z = get_smooth_zoom(t)
        if z > 1.003:
            cw, ch = int(round(W / z)), int(round(H / z))
            x0 = max(0, min(W - cw, int(round(540 - cw * 0.5))))
            y0 = max(0, min(H - ch, int(round(740 - ch * (740.0 / H)))))
            fg_im = Image.fromarray(rgb[y0:y0 + ch, x0:x0 + cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
            m_im  = Image.fromarray((matte[y0:y0 + ch, x0:x0 + cw] * 255.0).astype(np.uint8), "L").resize((W, H), Image.Resampling.BILINEAR)
            fg_rgb = np.array(fg_im)
            m_arr  = np.array(m_im, dtype=np.float32) / 255.0
        else:
            fg_im = Image.fromarray(rgb, "RGB")
            fg_rgb = rgb
            m_arr = matte

        # 2. 100% BRIGHT NATURAL ROOM BASE (ZERO DARKENING!)
        comp_im = fg_im.convert("RGBA")

        # 3. Dynamic Video Footage Placed BEHIND the Pharmacist (T.behind)!
        need_fg_recomp = False
        for st, en, vkey, rib_txt, acc_col in BEHIND_VID_SPANS:
            if st <= t <= en and vkey in b_clips and len(b_clips[vkey]) > 0:
                vframes = b_clips[vkey]
                vf_rgb = vframes[int((t - st) * FPS) % len(vframes)]
                draw_behind_speaker_video(comp_im, vf_rgb, t, st, en, rib_txt, acc_col)
                need_fg_recomp = True
                break

        # Cute Puffy Sticker Headlines inside Pastel Cream Cloud Pill on bridges
        for h_txt, t0, t1, fsz, c_top, c_bot in CUTE_HEADLINES:
            env_h = smooth_in_out_env(t, t0, t1, d_in=0.25, d_out=0.25)
            if env_h > 0.01:
                u_h = ease_out_back(min(1.0, (t - t0) / 0.34), s=1.2)
                sp_h = render_cute_text_sprite(h_txt, FONT_TITLE, fsz * 0.88, c_top, c_bot, stroke_col=(255, 255, 255), stroke_w=10, shadow_alpha=65)
                pw = min(1018, sp_h.width + 82)
                ph = 212
                cw_h, ch_h = pw + 36, ph + 36
                hcard = Image.new("RGBA", (cw_h, ch_h), (0, 0, 0, 0))
                sh_h = Image.new("RGBA", (cw_h, ch_h), (0, 0, 0, 0))
                ImageDraw.Draw(sh_h).rounded_rectangle([18, 22, 18 + pw, 22 + ph], radius=86, fill=(45, 30, 50, 70))
                hcard = Image.alpha_composite(hcard, sh_h.filter(ImageFilter.GaussianBlur(radius=10)))
                hd = ImageDraw.Draw(hcard)
                hd.rounded_rectangle([10, 10, 26 + pw, 26 + ph], radius=92, fill=(255, 255, 255, 252))
                hd.rounded_rectangle([18, 18, 18 + pw, 18 + ph], radius=84, fill=(255, 248, 251, 248), outline=(*c_top, 235), width=6)
                fit_s = min(1.0, (pw - 44) / max(1.0, float(sp_h.width - 28)))
                paste_centered(hcard, sp_h, cw_h // 2, ch_h // 2 - 4, scale=fit_s)
                paste_centered(comp_im, hcard, 540, 512, scale=0.86 + 0.14 * u_h, opacity=env_h)
                need_fg_recomp = True

        # Composite real Pharmacist + Desk + Left Plant + Held Pink LT PLUS Box cleanly in FRONT!
        if need_fg_recomp:
            fg_alpha = np.maximum(m_arr, static_fg_guard)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 4. 6 Cute Symmetric Ingredient Pill Badges (33.65 - 41.35s)
        draw_cute_ingredient_pills(comp_im, t)

        # 5. Cute Moderation-Safe Hook Typography (0.06 - 3.78s)
        env_hook = smooth_in_out_env(t, 0.06, 3.78, d_in=0.18, d_out=0.25)
        if env_hook > 0.01:
            if t >= 0.06:
                u1 = ease_out_back(min(1.0, (t - 0.06) / 0.30))
                sp1 = render_cute_text_sprite("Nghe kết luận lộ tuyến...", FONT_WIDE, 46, (56, 138, 255), (38, 105, 235), stroke_col=(255, 255, 255), stroke_w=8)
                paste_centered(comp_im, sp1, 515, 1105, scale=0.82 + 0.18 * u1, opacity=env_hook)
            if t >= 1.05:
                u2 = ease_out_back(min(1.0, (t - 1.05) / 0.32))
                sp2 = render_cute_text_sprite("LO LẮNG", FONT_WIDE, 78, (255, 88, 132), (245, 125, 108), stroke_col=(255, 255, 255), stroke_w=10)
                paste_centered(comp_im, sp2, 285, 1218, scale=0.80 + 0.20 * u2, opacity=env_hook, angle=-2.0)
            if t >= 1.45:
                u3 = ease_out_back(min(1.0, (t - 1.45) / 0.34))
                sp3 = render_cute_text_sprite("từ đâu?", FONT_SCRIPT, 92, (38, 198, 132), (25, 168, 105), stroke_col=(255, 255, 255), stroke_w=9)
                paste_centered(comp_im, sp3, 710, 1222, scale=0.80 + 0.20 * u3, opacity=env_hook, angle=2.2)
            if t >= 2.25:
                u4 = ease_out_cubic(min(1.0, (t - 2.25) / 0.28))
                sp4 = render_cute_text_sprite("Hiểu đúng trước tiên cùng Dược sĩ!", FONT_CAP, 46, (255, 232, 115), (255, 205, 75), stroke_col=(22, 28, 48), stroke_w=6)
                paste_centered(comp_im, sp4, 485, 1332, scale=0.90 + 0.10 * u4, opacity=env_hook * u4)

        # 6. Cute ChatGPT 3D Stickers + Confetti Sparkle Bursts!
        for skey, t0, t1, cx, cy, sz, rot, acc_rgb in STICKER_PLACES:
            env_s = smooth_in_out_env(t, t0, t1, d_in=0.22, d_out=0.24)
            if env_s > 0.01:
                dt = t - t0
                u_in = ease_out_back(min(1.0, dt / 0.36), s=1.30)
                wobble = math.sin(dt * 3.2) * 2.8
                cur_y = cy + (1.0 - min(1.0, u_in)) * (70.0 if cy < 400 else 120.0) + math.cos(dt * 2.6) * 4.5
                badge_im = render_cute_sticker_badge(stickers, skey, sz, acc_rgb)
                paste_centered(comp_im, badge_im, cx, cur_y, scale=(0.65 + 0.35 * u_in) * (0.85 + 0.15 * env_s), opacity=env_s, angle=rot + wobble)

        for bx, by, bt0, bdiam in CONFETTI_BURSTS:
            draw_cute_confetti_burst(comp_im, bx, by, t, bt0, bdiam)

        # 7. Word-by-Word Glowing Chest Captions (100% Face-Safe >=1085 & Box-Safe <=1215!)
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                op_g = smoothstep((g["t1"] - t) / 0.18) if (g["t1"] - t) < 0.18 else 1.0
                x_center = 485
                cap_sz_base = 64.0
                y_base = 1118 if len(g["lines"]) >= 2 else 1146
                lh = 64
                gap = 16
                for li, ln in enumerate(g["lines"]):
                    word_renders = []
                    total_w = 0
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_but = wtxt in BUTTER_WORDS
                        is_sak = wtxt in SAKURA_WORDS
                        k = 1.16 if (is_but or is_sak) else 1.0
                        col = (255, 228, 88) if is_but else ((255, 145, 185) if is_sak else (118, 252, 226))
                        sp = render_cute_text_sprite(wtxt, FONT_CAP, cap_sz_base * k, col, stroke_col=(14, 22, 38), stroke_w=5, glow_col=col, glow_rad=9, shadow_alpha=85)
                        adv = int(ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_CAP, cap_sz_base * k)))
                        word_renders.append((wtxt, ws, sp, adv, col, k))
                        total_w += adv + (gap if wi > 0 else 0)

                    cur_x = max(54, min(1018 - total_w, x_center - total_w // 2))
                    cur_y = y_base + li * lh
                    for wtxt, ws, sp, adv, col, k in word_renders:
                        if t >= ws:
                            dt_w = t - ws
                            u_w = ease_out_cubic(min(1.0, dt_w / 0.20))
                            wy = cur_y + (1.0 - u_w) * 20.0
                            blur_w = (1.0 - u_w) * 5.5
                            wcx = cur_x + adv // 2
                            paste_centered(comp_im, sp, wcx, wy, scale=0.92 + 0.08 * u_w, opacity=op_g * min(1.0, dt_w / 0.09), blur_px=blur_w)

                            if wtxt in STROKE_UP_WORDS and 0.08 <= dt_w <= 0.44:
                                u_su = (dt_w - 0.08) / 0.36
                                sc_su = 1.0 + 1.12 * ease_out_cubic(u_su)
                                op_su = smoothstep(1.0 - u_su) * 0.76 * op_g
                                paste_centered(comp_im, sp, wcx, cur_y, scale=sc_su, opacity=op_su * 0.44)
                        cur_x += adv + gap
                break

        # 8. Closing CTA Pill Banner at Left-Bottom during Finale (53.95 - 59.05s, clear of pink box!)
        env_end = smooth_in_out_env(t, 53.95, 59.05, d_in=0.28, d_out=0.28)
        if env_end > 0.01:
            sp_cta = render_cute_text_sprite("Nhắn \"LT PLUS\" nhận tư vấn chi tiết!", FONT_WIDE, 32, (255, 255, 255), stroke_col=(228, 72, 122), stroke_w=7, shadow_alpha=85)
            paste_centered(comp_im, sp_cta, 540, 1735, scale=0.94 + 0.06 * env_end, opacity=env_end)

        # 9. Subtle Moderation-Safe Legal Disclaimer Bar at Bottom
        bar_bot = Image.new("RGBA", (W, 48), (38, 22, 34, 142))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 48))
        paste_centered(comp_im, legal_sp, 540, H - 24, opacity=0.95)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"htpm_lt_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/1775 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close()
        writer.wait()
    reader_a.close()
    reader_m.stdout.close()
    reader_m.wait()

    if test_mode and test_saved:
        imgs = [Image.open(p).resize((360, 640), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (360 * 4, 640 * 2))
        for i, im in enumerate(imgs[:8]):
            grid.paste(im, ((i % 4) * 360, (i // 4) * 640))
        gp = os.path.join(CHECK_DIR, "htpm_lt_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved htpm_lt_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM LT PLUS Cute video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
