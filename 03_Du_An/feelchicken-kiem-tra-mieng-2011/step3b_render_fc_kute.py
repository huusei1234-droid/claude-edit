import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
LOGO_PATH = r"Z:\Máy tính khác\My Computer\feel chicken\logo feel tn.png"
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

FONTS_DIR   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_BUBBLE = os.path.join(FONTS_DIR, "Baloo2-ExtraBold.ttf")
FONT_POP    = os.path.join(FONTS_DIR, "PaytoneOne-Regular.ttf")
FONT_SANS_XB= os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_SANS_B = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")
FONT_SCRIPT = os.path.join(FONTS_DIR, "DancingScript-Bold.ttf")

# Korean Kawaii Feel Chicken Brand Palette
COL_CORAL_5  = [(255, 132, 152), (255, 86, 112), (238, 42, 68), (255, 95, 78), (255, 156, 128)]
COL_GOLD_5   = [(255, 250, 190), (255, 224, 92), (255, 186, 36), (255, 218, 84), (255, 248, 178)]
COL_MINT_5   = [(210, 255, 242), (112, 238, 198), (46, 198, 152), (96, 232, 188), (200, 255, 238)]
COL_CREAM_5  = [(255, 255, 255), (255, 248, 232), (255, 236, 198), (255, 248, 232), (255, 255, 255)]
COL_CHOCO    = (54, 24, 28)
COL_CORAL_DK = (196, 28, 52)

_font_cache = {}
def get_font(path, size):
    key = (path, max(10, int(round(size))))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, key[1])
    return _font_cache[key]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def smoothstep(u):
    u = clamp01(u)
    return u * u * (3.0 - 2.0 * u)

def ease_out_cubic(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 3.0

def ease_out_back(u, s=1.32):
    u = clamp01(u) - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0

def smooth_env(t, t0, t1, d_in=0.26, d_out=0.24):
    if t <= t0 or t >= t1:
        return 0.0
    ai = ease_out_cubic((t - t0) / max(0.04, d_in)) if (t - t0) < d_in else 1.0
    ao = smoothstep((t1 - t) / max(0.04, d_out)) if (t1 - t) < d_out else 1.0
    return min(ai, ao)

def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.95) * 1.02, 0.0, 1.0)
    lr = np.clip(y * 255.0 * 1.018, 0, 255).astype(np.uint8)
    lg = np.clip(y * 255.0 * 1.006, 0, 255).astype(np.uint8)
    lb = np.clip(y * 255.0 * 0.996, 0, 255).astype(np.uint8)
    return lr, lg, lb

BRIGHT_LUT = _build_bright_lut()

def polish_sunny_frame(rgb):
    out = np.empty_like(rgb)
    out[:, :, 0] = BRIGHT_LUT[0][rgb[:, :, 0]]
    out[:, :, 1] = BRIGHT_LUT[1][rgb[:, :, 1]]
    out[:, :, 2] = BRIGHT_LUT[2][rgb[:, :, 2]]
    return out

def fit_cover(rgb_arr, target_w, target_h, zoom=1.0, cy_bias=0.5):
    sh, sw = rgb_arr.shape[:2]
    scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    nw = max(target_w, int(round(sw * scale)))
    nh = max(target_h, int(round(sh * scale)))
    im = Image.fromarray(rgb_arr, "RGB").resize((nw, nh), Image.Resampling.BILINEAR)
    x0 = (nw - target_w) // 2
    y0 = max(0, min(nh - target_h, int(round((nh - target_h) * cy_bias))))
    return im.crop((x0, y0, x0 + target_w, y0 + target_h))

# ==============================================================================
# 2-LAYER SEPARATED STROKE + 5-STOP GRADIENT + SPECULAR SHEEN TYPOGRAPHY ENGINE
# ==============================================================================
_text_cache = {}
def render_5stop_kawaii_base(text, font_path, size, stops5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(54, 24, 28), inner_w=4, glow_col=None, glow_rad=8, shadow_alpha=95):
    key = (text, font_path, int(round(size)), tuple(stops5), outer_stroke, outer_w, inner_stroke, inner_w, glow_col, glow_rad, shadow_alpha)
    if key in _text_cache:
        return _text_cache[key]

    font = get_font(font_path, size)
    max_sw = max(outer_w, inner_w)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=max_sw)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(max(glow_rad * 2.4, 10) + max_sw + 14)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    # LAYER 1 (.grad-back): Soft Glow + Drop Shadow + Outer White Sticker Stroke + Inner Dark Rim
    back = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    if glow_col and glow_rad > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(1, outer_w // 2), stroke_fill=255)
        gb = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad)), dtype=np.float32)
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0], ga[:, :, 1], ga[:, :, 2] = glow_col
        ga[:, :, 3] = np.clip(gb * 0.68, 0, 255).astype(np.uint8)
        back = Image.alpha_composite(back, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 3, oy + 6), text, font=font, fill=255, stroke_width=max_sw, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5.5)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (36, 18, 24)
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        back = Image.alpha_composite(back, Image.fromarray(sa, "RGBA"))

    if outer_w > 0 and outer_stroke is not None:
        os_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(os_im).text((ox, oy), text, font=font, fill=(*outer_stroke, 255), stroke_width=outer_w, stroke_fill=(*outer_stroke, 255))
        back = Image.alpha_composite(back, os_im)

    if inner_w > 0 and inner_stroke is not None:
        is_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(is_im).text((ox, oy), text, font=font, fill=(*inner_stroke, 255), stroke_width=inner_w, stroke_fill=(*inner_stroke, 255))
        back = Image.alpha_composite(back, is_im)

    # LAYER 2 (.grad-front): Pure Un-encroached 5-Stop Gradient Face
    face_mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(face_mask).text((ox, oy), text, font=font, fill=255)
    m_arr = np.array(face_mask, dtype=np.float32) / 255.0

    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)
    stops_pos = np.array([0.0, 0.28, 0.52, 0.76, 1.0], dtype=np.float32)
    stops_arr = np.array(stops5, dtype=np.float32)
    grad_1d = np.zeros((ch, 3), dtype=np.uint8)
    for c in range(3):
        grad_1d[:, c] = np.clip(np.interp(yy, stops_pos, stops_arr[:, c]), 0, 255).astype(np.uint8)
    grad_rgb = np.broadcast_to(grad_1d[:, None, :], (ch, cw, 3)).copy()
    front = Image.fromarray(np.dstack([grad_rgb, (m_arr * 255.0).astype(np.uint8)]), "RGBA")
    comp = Image.alpha_composite(back, front)

    if len(_text_cache) > 800:
        _text_cache.clear()
    _text_cache[key] = (comp, m_arr)
    return comp, m_arr

def get_text_sprite(text, font_path, size, stops5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(54, 24, 28), inner_w=4, glow_col=None, glow_rad=8, shadow_alpha=95, sheen_prog=None):
    comp, m_arr = render_5stop_kawaii_base(text, font_path, size, stops5, outer_stroke, outer_w, inner_stroke, inner_w, glow_col, glow_rad, shadow_alpha)
    if sheen_prog is None or sheen_prog < -0.2 or sheen_prog > 1.2:
        return comp
    ch, cw = m_arr.shape
    xx = np.linspace(0.0, 1.0, cw, dtype=np.float32)[None, :]
    yy = np.linspace(0.0, 1.0, ch, dtype=np.float32)[:, None]
    diag = xx * 0.82 + yy * 0.18
    center = -0.15 + sheen_prog * 1.30
    band = np.exp(-((diag - center) ** 2) / (2.0 * (0.055 ** 2)))
    alpha_s = np.clip(band * m_arr * 215.0, 0, 255).astype(np.uint8)
    sheen_im = Image.fromarray(np.dstack([np.full((ch, cw), 255, np.uint8), np.full((ch, cw), 252, np.uint8), np.full((ch, cw), 230, np.uint8), alpha_s]), "RGBA")
    return Image.alpha_composite(comp, sheen_im)

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
        im = im.filter(ImageFilter.GaussianBlur(radius=min(10.0, blur_px)))
    if opacity < 0.995:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")
    px = int(round(cx - im.width / 2.0))
    py = int(round(cy - im.height / 2.0))
    canvas_im.alpha_composite(im, dest=(px, py))

# ==============================================================================
# KAWAII STICKER BADGES, CONFETTI, DOODLES & UI CARDS
# ==============================================================================
_badge_cache = {}
def load_stickers():
    keys = ["FC_st_prof_chick", "FC_st_score10", "FC_st_riddle_bulb", "FC_st_gift_chicken", "FC_st_trophy_star", "FC_st_cheers_cups"]
    out = {}
    for k in keys:
        p = os.path.join(MEDIA_DIR, f"{k}.png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA")
            arr = np.array(im)
            non_white = (arr[:, :, 0] < 245) | (arr[:, :, 1] < 245) | (arr[:, :, 2] < 245)
            ys, xs = np.where(non_white)
            if len(xs) > 100:
                pad_c = int(im.width * 0.05)
                x0, x1 = max(0, int(xs.min()) - pad_c), min(im.width, int(xs.max()) + pad_c)
                y0, y1 = max(0, int(ys.min()) - pad_c), min(im.height, int(ys.max()) + pad_c)
                side = max(x1 - x0, y1 - y0)
                cx_c, cy_c = (x0 + x1) // 2, (y0 + y1) // 2
                hx = side // 2
                im = im.crop((max(0, cx_c - hx), max(0, cy_c - hx), min(im.width, cx_c + hx), min(im.height, cy_c + hx)))
            out[k] = im
    # Fallback to Feel Chicken official logo if any missing
    logo_im = Image.open(LOGO_PATH).convert("RGBA")
    out["logo_fc"] = logo_im
    for k in keys:
        if k not in out:
            out[k] = logo_im
    return out

def get_sticker_badge(stickers, key, size_px, accent_rgb):
    ck = (key, size_px, accent_rgb)
    if ck in _badge_cache:
        return _badge_cache[ck]
    S = size_px
    pad = int(round(S * 0.08))
    cs = S - pad * 2
    rad = int(round(cs * 0.28))

    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 7, pad + cs, pad + cs + 7], radius=rad, fill=(48, 22, 28, 86))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(radius=8)))

    ImageDraw.Draw(base).rounded_rectangle([pad - 6, pad - 6, pad + cs + 5, pad + cs + 5], radius=rad + 6, fill=(255, 255, 255, 255))
    rmask = Image.new("L", (cs, cs), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, cs - 1, cs - 1], radius=rad, fill=255)

    src_im = stickers[key].convert("RGBA")
    white_bg = Image.new("RGBA", src_im.size, (255, 250, 244, 255))
    white_bg.alpha_composite(src_im)
    art = white_bg.convert("RGB").resize((cs, cs), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.paste(art, (pad, pad), mask=rmask)
    base = Image.alpha_composite(base, layer)

    ImageDraw.Draw(base).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=(*accent_rgb, 242), width=5)
    # Cute 4-point sparkle star in top-right corner
    sx, sy, sr = pad + cs - 10, pad + 12, 14
    ImageDraw.Draw(base).polygon([
        (sx, sy - sr), (sx + 4, sy - 4), (sx + sr, sy), (sx + 4, sy + 4),
        (sx, sy + sr), (sx - 4, sy + 4), (sx - sr, sy), (sx - 4, sy - 4)
    ], fill=(255, 214, 64, 255), outline=(255, 255, 255, 255))

    _badge_cache[ck] = base
    return base

def draw_confetti_burst(canvas_im, cx, cy, t_now, t0, diam=96):
    dt = t_now - t0
    if dt < 0 or dt > 0.52:
        return
    u = dt / 0.52
    e = ease_out_cubic(u)
    op = smoothstep(1.0 - u)
    r = int(round(diam * 0.48 * (0.52 + 1.18 * e)))
    sz = r * 2 + 64
    bim = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    dr = ImageDraw.Draw(bim)
    cc = sz // 2
    dr.ellipse([cc - r, cc - r, cc + r, cc + r], outline=(255, 108, 136, int(230 * op)), width=max(2, int(5 * (1.0 - 0.6 * u))))
    cols = [(255, 96, 128), (255, 212, 68), (72, 222, 176), (102, 186, 255), (255, 148, 92), (196, 136, 255)]
    for i, col in enumerate(cols):
        ang = math.radians(i * 60.0 + 30.0 * u)
        dist = r * 1.20
        dx = cc + int(dist * math.cos(ang))
        dy = cc + int(dist * math.sin(ang))
        dot_r = max(2, int(8 * (1.0 - 0.45 * u)))
        dr.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill=(*col, int(248 * op)))
    canvas_im.alpha_composite(bim, dest=(int(cx - cc), int(cy - cc)))

def draw_kawaii_frame_border(canvas_im, t):
    """Subtle pastel corner sparkles & warm frame accents so every shot feels cohesive and kute!"""
    dr = ImageDraw.Draw(canvas_im)
    # Soft outer rounded frame stroke
    dr.rounded_rectangle([14, 14, W - 15, H - 15], radius=44, outline=(255, 255, 255, 92), width=4)
    # Floating tiny pastel stars at top corners
    for idx, (sx, sy, col) in enumerate([(56, 68, (255, 220, 88)), (1024, 68, (255, 128, 156))]):
        sr = int(11 + 3 * math.sin(t * 3.6 + idx * 1.7))
        dr.polygon([
            (sx, sy - sr), (sx + 3, sy - 3), (sx + sr, sy), (sx + 3, sy + 3),
            (sx, sy + sr), (sx - 3, sy + 3), (sx - sr, sy), (sx - 3, sy - 3)
        ], fill=(*col, 215))

def draw_behind_speaker_card(canvas_im, vid_rgb, t_now, st, en, ribbon_txt, accent_col=(242, 74, 98), cy_pos=435, vh=740):
    env = smooth_env(t_now, st, en, d_in=0.34, d_out=0.30)
    if env <= 0.01:
        return
    dt = t_now - st
    dur = max(0.2, en - st)
    vw = 1016
    z_v = 1.02 + 0.06 * smoothstep(dt / dur)
    crop_im = fit_cover(vid_rgb, vw, vh, zoom=z_v).convert("RGBA")

    rad = 52
    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=rad, fill=255)

    cw, ch = vw + 36, vh + 56
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 28, 18 + vw, 28 + vh], radius=rad, fill=(45, 20, 28, 82))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=11)))

    ImageDraw.Draw(card).rounded_rectangle([8, 14, 28 + vw, 34 + vh], radius=rad + 10, fill=(255, 255, 255, 252))
    art = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    art.paste(crop_im, (18, 24), mask=vmask)
    card = Image.alpha_composite(card, art)
    ImageDraw.Draw(card).rounded_rectangle([18, 24, 18 + vw - 1, 24 + vh - 1], radius=rad, outline=(*accent_col, 242), width=6)

    if ribbon_txt:
        sp_r = get_text_sprite(ribbon_txt, FONT_SANS_XB, 29, COL_CREAM_5, outer_stroke=None, outer_w=0, inner_stroke=None, inner_w=0, shadow_alpha=45)
        pw = min(960, sp_r.width + 54)
        ph = 58
        px1 = (cw - pw) // 2
        py1 = 2
        ImageDraw.Draw(card).rounded_rectangle([px1 - 5, py1 - 4, px1 + pw + 5, py1 + ph + 4], radius=30, fill=(255, 255, 255, 255))
        ImageDraw.Draw(card).rounded_rectangle([px1, py1, px1 + pw, py1 + ph], radius=28, fill=(*accent_col, 255))
        paste_centered(card, sp_r, cw // 2, py1 + ph // 2, scale=min(1.0, (pw - 26) / max(1.0, sp_r.width - 16)))

    glide_y = (1.0 - env) * (-32.0)
    paste_centered(canvas_im, card, 540, cy_pos + glide_y, scale=0.95 + 0.05 * env, opacity=env)

def draw_pill_banner(canvas_im, text, cx, cy, bg_rgb, text_stops=COL_CREAM_5, fsz=32, scale=1.0, opacity=1.0):
    sp = get_text_sprite(text, FONT_SANS_XB, fsz, text_stops, outer_stroke=None, outer_w=0, inner_stroke=(48, 20, 26), inner_w=3, shadow_alpha=45)
    pw = min(1010, sp.width + 58)
    ph = max(66, sp.height + 16)
    cw, ch = pw + 28, ph + 28
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([14, 18, 14 + pw, 18 + ph], radius=ph // 2, fill=(42, 18, 24, 78))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=6)))
    dr = ImageDraw.Draw(card)
    dr.rounded_rectangle([8, 8, 20 + pw, 20 + ph], radius=ph // 2 + 6, fill=(255, 255, 255, 255))
    dr.rounded_rectangle([14, 14, 14 + pw, 14 + ph], radius=ph // 2, fill=(*bg_rgb, 250))
    paste_centered(card, sp, cw // 2, ch // 2, scale=min(1.0, (pw - 32) / max(1.0, sp.width - 14)))
    paste_centered(canvas_im, card, cx, cy, scale=scale, opacity=opacity)

def build_caption_groups(words):
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
        txt = w["w"].strip()
        if not txt:
            continue
        if prev is not None and (w["s"] - prev["e"]) >= 0.34:
            flush_group()
        if line and (len(line) >= 4 or sum(len(x[0]) + 1 for x in line) + len(txt) > 18):
            flush_line()
        if len(cur) >= 2 and not line:
            flush_group()
        line.append([txt, w["s"], w["e"]])
        prev = w
        if re.search(r"[.,?!:;]$", txt):
            flush_group()
    flush_group()

    out = []
    for i, g in enumerate(groups):
        last_e = g[-1][-1][2]
        nxt_s = groups[i + 1][0][0][1] if i + 1 < len(groups) else last_e + 0.55
        t1 = min(nxt_s, last_e + 0.42) if (nxt_s - last_e) > 0.50 else nxt_s
        out.append({"t0": g[0][0][1], "t1": t1, "lines": g})
    return out

GOLD_KEYWORDS = {
    "Khang", "kiểm", "tra", "miệng", "KIỂM", "TRA", "MIỆNG", "20/11", "20/11!",
    "quà", "ngon", "HỌC", "SINH", "GIỎI", "chinh", "phục!"
}
CORAL_KEYWORDS = {
    "Feel", "Chicken", "run", "cầm", "cập!", "bồi", "hồi",
    "TRẢ", "LỜI", "ĐÚNG,", "NHẬN", "QUÀ", "NGAY!", "lắt", "léo"
}
POP_EMPHASIS = {"Khang", "cập!", "MIỆNG", "NGAY!", "20/11", "20/11!", "ngon", "GIỎI", "Chicken"}

def load_all_frames_rgb(path, vw, vh):
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={vw}:{vh}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE
    )
    frames = []
    nb = vw * vh * 3
    while True:
        b = proc.stdout.read(nb)
        if len(b) < nb:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)))
    proc.stdout.close()
    proc.wait()
    return frames

def load_all_frames_gray(path, vw, vh):
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={vw}:{vh}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )
    frames = []
    nb = vw * vh
    while True:
        b = proc.stdout.read(nb)
        if len(b) < nb:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw)).astype(np.float32) / 255.0)
    proc.stdout.close()
    proc.wait()
    return frames

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv

    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    total_frames = tm["total_frames"]
    cap_groups = build_caption_groups(tm["words"])

    # Load video sources into RAM cleanly (short segments, super fast random/indexed access!)
    print("Loading A-rolls, RVM mattes & B-rolls...", flush=True)
    v_s1 = load_all_frames_rgb(os.path.join(AROLL_DIR, "s1_skit.mp4"), W, H)
    v_s2 = load_all_frames_rgb(os.path.join(AROLL_DIR, "s2_table.mp4"), W, H)
    m_s2 = load_all_frames_gray(os.path.join(AROLL_DIR, "s2_table_matte.mp4"), W, H)
    v_s5 = load_all_frames_rgb(os.path.join(AROLL_DIR, "s5_gifts.mp4"), W, H)
    m_s5 = load_all_frames_gray(os.path.join(AROLL_DIR, "s5_gifts_matte.mp4"), W, H)
    v_s6b= load_all_frames_rgb(os.path.join(AROLL_DIR, "s6_thumbs.mp4"), W, H)

    b_jar_cut   = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_jar_cut.mp4"), W, H)
    b_jar_shake = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_jar_shake.mp4"), W, H)
    b_jar_pick  = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_jar_pick.mp4"), W, H)

    muse_vids = {}
    for mk in ["MUSE_fc_classroom", "MUSE_fc_cheese_pour", "MUSE_fc_feast_table", "MUSE_fc_friends_party"]:
        mp = os.path.join(MEDIA_DIR, f"{mk}.mp4")
        if os.path.exists(mp):
            muse_vids[mk] = load_all_frames_rgb(mp, 1280, 720)
        else:
            print("WARNING fallback for missing Muse video:", mk)
            muse_vids[mk] = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_jar_shake.mp4"), 1280, 720)

    stickers = load_stickers()
    logo_clean = stickers["logo_fc"].copy()
    logo_clean.thumbnail((280, 280), Image.Resampling.LANCZOS)

    # Static foreground table/body guards for RVM compositing
    yy_g, xx_g = np.ogrid[0:H, 0:W]
    s2_table_guard = np.clip((yy_g.astype(np.float32) - 1490.0) / 55.0, 0.0, 1.0) * np.clip((xx_g.astype(np.float32) - 310.0) / 70.0, 0.0, 1.0)
    s5_lower_guard = np.clip((yy_g.astype(np.float32) - 1180.0) / 75.0, 0.0, 1.0)

    test_times = [2.60, 4.25, 7.20, 11.80, 15.20, 21.00, 26.80, 31.50, 41.20, 44.60]
    test_fset = {min(total_frames - 1, int(round(ts * FPS))) for ts in test_times}
    test_saved = []

    raw_vid_out = os.path.join(PROJ_DIR, "_fc_kute_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    for fi in range(total_frames):
        if test_mode and fi not in test_fset:
            continue

        t = fi / FPS
        show_captions = True
        cap_y_base = 1360

        # ======================================================================
        # SCENE 1: OPENING SKIT (0.00 .. 5.00s)
        # ======================================================================
        if fi < segs["s1_skit"]["f1"]:
            lf = min(len(v_s1) - 1, fi - segs["s1_skit"]["f0"])
            u_s1 = lf / max(1.0, segs["s1_skit"]["f1"] - 1.0)
            rgb = polish_sunny_frame(v_s1[lf])
            comp_im = fit_cover(rgb, W, H, zoom=1.01 + 0.065 * smoothstep(u_s1)).convert("RGBA")
            show_captions = False

            # Cute Classroom Header Pill
            env_hdr = smooth_env(t, 0.12, 4.88, 0.22, 0.22)
            if env_hdr > 0.01:
                draw_pill_banner(comp_im, "LỚP HỌC FEEL CHICKEN • 20/11", 540, 132, (232, 48, 72), COL_GOLD_5, fsz=31, scale=0.92 + 0.08 * env_hdr, opacity=env_hdr)

            # Anh Khang's Kawaii Comic Speech Bubble ("THÀNH! LÊN BẢNG KIỂM TRA MIỆNG!")
            env_b1 = smooth_env(t, 1.35, 4.88, 0.20, 0.22)
            if env_b1 > 0.01:
                ub1 = ease_out_back(min(1.0, (t - 1.35) / 0.30))
                bw, bh = 790, 215
                bub = Image.new("RGBA", (bw + 32, bh + 54), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bub)
                bd.rounded_rectangle([18, 22, 18 + bw, 22 + bh], radius=54, fill=(45, 18, 24, 80))
                bub = bub.filter(ImageFilter.GaussianBlur(radius=6))
                bd = ImageDraw.Draw(bub)
                bd.rounded_rectangle([12, 12, 20 + bw, 20 + bh], radius=56, fill=(255, 255, 255, 255))
                bd.rounded_rectangle([18, 18, 14 + bw, 14 + bh], radius=50, fill=(255, 249, 238, 252), outline=(238, 56, 82, 255), width=6)
                # Speech tail pointing down-left toward Anh Khang
                bd.polygon([(210, 14 + bh), (265, 14 + bh), (185, 46 + bh)], fill=(255, 249, 238, 255), outline=(238, 56, 82, 255))

                sp_k1 = get_text_sprite("THÀNH ƠI!!", FONT_BUBBLE, 54, COL_CORAL_5, outer_w=8, inner_w=4)
                sp_k2 = get_text_sprite("LÊN BẢNG KIỂM TRA MIỆNG!", FONT_BUBBLE, 48, COL_GOLD_5, outer_w=8, inner_w=4, sheen_prog=(t - 1.5) * 0.7)
                paste_centered(bub, sp_k1, (bw + 32) // 2, 74)
                paste_centered(bub, sp_k2, (bw + 32) // 2, 152, scale=min(1.0, (bw - 42) / max(1.0, sp_k2.width)))
                paste_centered(comp_im, bub, 595, 385, scale=0.80 + 0.20 * ub1, opacity=env_b1, angle=-1.5)

                st_chick = get_sticker_badge(stickers, "FC_st_prof_chick", 205, (255, 196, 56))
                paste_centered(comp_im, st_chick, 138, 375, scale=0.75 + 0.25 * ub1, opacity=env_b1, angle=-6.0 + math.sin(t * 4.0) * 3.0)
                draw_confetti_burst(comp_im, 138, 375, t, 1.40, 88)

            # Staff Thành's Shivering Kawaii Bubble ("Em... em...")
            env_b2 = smooth_env(t, 3.55, 4.94, 0.16, 0.18)
            if env_b2 > 0.01:
                ub2 = ease_out_back(min(1.0, (t - 3.55) / 0.24))
                jit_x = math.sin(t * 46.0) * 5.0
                jit_y = math.cos(t * 38.0) * 3.0
                sw_w, sw_h = 430, 128
                sbub = Image.new("RGBA", (sw_w + 24, sw_h + 24), (0, 0, 0, 0))
                sd = ImageDraw.Draw(sbub)
                sd.rounded_rectangle([8, 8, 16 + sw_w, 16 + sw_h], radius=46, fill=(255, 255, 255, 252), outline=(88, 186, 250, 255), width=5)
                sp_em = get_text_sprite("Em... em... run quá!", FONT_BUBBLE, 42, COL_MINT_5, outer_w=7, inner_w=4)
                paste_centered(sbub, sp_em, (sw_w + 24) // 2, (sw_h + 24) // 2, scale=min(1.0, (sw_w - 24) / max(1.0, sp_em.width)))
                paste_centered(comp_im, sbub, 765 + jit_x, 835 + jit_y, scale=0.82 + 0.18 * ub2, opacity=env_b2, angle=2.0)

                # Cute animated anime sweat drops above Thành's head
                drop_im = Image.new("RGBA", (90, 90), (0, 0, 0, 0))
                dd = ImageDraw.Draw(drop_im)
                dy_off = int(((t - 3.55) * 45.0) % 24.0)
                dd.polygon([(30, 10 + dy_off), (16, 42 + dy_off), (44, 42 + dy_off)], fill=(110, 205, 255, 235))
                dd.ellipse([16, 32 + dy_off, 44, 58 + dy_off], fill=(110, 205, 255, 235), outline=(255, 255, 255, 255), width=2)
                paste_centered(comp_im, drop_im, 915, 935, opacity=env_b2)

        # ======================================================================
        # SCENE 2: ANH KHANG AT TABLE — SCHOOL MEMORY (5.00 .. 14.03s)
        # ======================================================================
        elif fi < segs["s2_table"]["f1"]:
            lf = min(len(v_s2) - 1, fi - segs["s2_table"]["f0"])
            lt = t - segs["s2_table"]["t0"]
            rgb = polish_sunny_frame(v_s2[lf])
            matte = m_s2[min(len(m_s2) - 1, lf)]
            z = 1.01 + 0.045 * math.sin(lt * 0.35)
            fg_im = fit_cover(rgb, W, H, zoom=z)
            fg_rgb = np.array(fg_im)
            m_im = fit_cover(np.dstack([matte * 255] * 3).astype(np.uint8), W, H, zoom=z)
            m_arr = np.array(m_im)[:, :, 0].astype(np.float32) / 255.0

            comp_im = fg_im.convert("RGBA")
            cap_y_base = 1325

            # First half (5.00 .. 9.55s): Keep glowing Feel Chicken neon sign visible + pop cute badges on sides!
            env_st1 = smooth_env(t, 5.25, 9.45, 0.24, 0.24)
            if env_st1 > 0.01:
                u_s = ease_out_back(min(1.0, (t - 5.25) / 0.34))
                b_sc10 = get_sticker_badge(stickers, "FC_st_score10", 215, (255, 118, 148))
                paste_centered(comp_im, b_sc10, 165, 1035 + math.sin(t * 3.0) * 5.0, scale=0.76 + 0.24 * u_s, opacity=env_st1, angle=-6.0)
                draw_confetti_burst(comp_im, 165, 1035, t, 5.30, 84)

            # Playful "RUN CẦM CẬP!" badge right when he says it (8.35 .. 9.55s)
            env_run = smooth_env(t, 8.30, 9.55, 0.16, 0.20)
            if env_run > 0.01:
                sp_run = get_text_sprite("RUN CẦM CẬP!!", FONT_BUBBLE, 52, COL_CORAL_5, outer_w=9, inner_w=4)
                paste_centered(comp_im, sp_run, 825 + math.sin(t * 48.0) * 4.0, 1035, scale=0.88 + 0.12 * env_run, opacity=env_run, angle=5.5)

            # Second half (9.62 .. 13.98s): Warm Sunlit 20/11 Classroom Muse Video BEHIND Anh Khang!
            st_cls, en_cls = 9.62, 13.98
            if st_cls <= t <= en_cls:
                vframes = muse_vids["MUSE_fc_classroom"]
                vf_rgb = vframes[int((t - st_cls) * FPS) % len(vframes)]
                draw_behind_speaker_card(comp_im, vf_rgb, t, st_cls, en_cls, "KÝ ỨC TUỔI HỌC TRÒ BỒI HỒI 20/11", (245, 132, 68), cy_pos=505, vh=820)
                fg_alpha = np.maximum(m_arr, s2_table_guard)
                comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

                env_st2 = smooth_env(t, 9.85, 13.90, 0.24, 0.24)
                if env_st2 > 0.01:
                    b_prof = get_sticker_badge(stickers, "FC_st_prof_chick", 215, (255, 196, 58))
                    paste_centered(comp_im, b_prof, 165, 1495 + math.cos(t * 2.8) * 5.0, scale=0.85 + 0.15 * env_st2, opacity=env_st2, angle=-4.0)

        # ======================================================================
        # SCENE 3: PROGRAM ANNOUNCEMENT — 3 WAVE-PACING BEATS (14.03 .. 22.63s)
        # ======================================================================
        elif fi < segs["s3_program"]["f1"]:
            s3_t0 = segs["s3_program"]["t0"]
            s3_t1 = segs["s3_program"]["t1"]
            t_cut1 = s3_t0 + 2.55  # 16.58s
            t_cut2 = s3_t0 + 5.38  # 19.41s

            if t < t_cut1:
                # Beat 3A: Real staff cutting 100 question slips at Feel Chicken!
                idx_b = min(len(b_jar_cut) - 1, int((t - s3_t0) * 1.35 * FPS))
                rgb = polish_sunny_frame(b_jar_cut[idx_b])
                comp_im = fit_cover(rgb, W, H, zoom=1.02 + 0.06 * ((t - s3_t0) / 2.55)).convert("RGBA")
                draw_pill_banner(comp_im, "CHÀO ĐÓN NGÀY NHÀ GIÁO 20/11", 540, 148, (236, 54, 82), COL_GOLD_5, fsz=31)
                b_p = get_sticker_badge(stickers, "FC_st_prof_chick", 215, (255, 198, 62))
                paste_centered(comp_im, b_p, 175, 345, angle=-5.0 + math.sin(t * 3.5) * 3.0)
                cap_y_base = 1455
            elif t < t_cut2:
                # Beat 3B: Real staff shaking the Feel Chicken question jar!
                idx_b = min(len(b_jar_shake) - 1, int((t - t_cut1) * 1.15 * FPS))
                rgb = polish_sunny_frame(b_jar_shake[idx_b])
                comp_im = fit_cover(rgb, W, H, zoom=1.01 + 0.07 * ((t - t_cut1) / 2.83)).convert("RGBA")
                draw_pill_banner(comp_im, "HŨ CÂU HỎI KÝ ỨC HỌC TRÒ", 540, 148, (245, 132, 58), COL_CREAM_5, fsz=31)
                b_s = get_sticker_badge(stickers, "FC_st_score10", 215, (255, 112, 146))
                paste_centered(comp_im, b_s, 895, 345, angle=5.5 + math.cos(t * 3.5) * 3.0)
                cap_y_base = 1455
            else:
                # Beat 3C: HERO KAWAII 3D CHALKBOARD PROGRAM CARD ("KIỂM TRA MIỆNG - TRẢ LỜI ĐÚNG, NHẬN QUÀ NGAY!")
                vframes = muse_vids["MUSE_fc_classroom"]
                vf_rgb = vframes[int((t - t_cut2) * FPS) % len(vframes)]
                bg_im = fit_cover(vf_rgb, W, H, zoom=1.06).filter(ImageFilter.GaussianBlur(radius=10)).convert("RGBA")
                # Warm pastel sunlit tint overlay
                tint = Image.new("RGBA", (W, H), (255, 236, 224, 62))
                comp_im = Image.alpha_composite(bg_im, tint)
                show_captions = False

                dt_c = t - t_cut2
                u_c = ease_out_back(min(1.0, dt_c / 0.38), s=1.28)

                # Giant Kawaii Green School Chalkboard with Wooden Pastel Frame
                bw, bh = 976, 690
                board = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
                sh = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rounded_rectangle([20, 28, 20 + bw, 28 + bh], radius=64, fill=(38, 18, 22, 110))
                board = Image.alpha_composite(board, sh.filter(ImageFilter.GaussianBlur(radius=14)))
                bd = ImageDraw.Draw(board)
                bd.rounded_rectangle([10, 10, 30 + bw, 30 + bh], radius=68, fill=(255, 255, 255, 255))
                bd.rounded_rectangle([20, 20, 20 + bw, 20 + bh], radius=58, fill=(242, 168, 96, 255))
                bd.rounded_rectangle([38, 38, 2 + bw, 2 + bh], radius=44, fill=(34, 96, 72, 255), outline=(255, 245, 215, 190), width=3)

                # Cute chalk header + 5-stop Gold Bling Title + Coral Pill CTA
                sp_sub0 = get_text_sprite("CHƯƠNG TRÌNH ĐẶC BIỆT 20/11", FONT_SANS_XB, 31, COL_MINT_5, outer_w=0, inner_w=3)
                sp_main = get_text_sprite("KIỂM TRA MIỆNG", FONT_POP, 92, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=12, inner_stroke=(58, 24, 18), inner_w=5, glow_col=(255, 210, 75), glow_rad=12, sheen_prog=dt_c * 0.65)
                sp_sub1 = get_text_sprite("TRẢ LỜI ĐÚNG", FONT_BUBBLE, 66, COL_CREAM_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(236, 48, 76), inner_w=4)
                sp_sub2 = get_text_sprite("NHẬN QUÀ NGAY!", FONT_BUBBLE, 74, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(68, 18, 28), inner_w=4, sheen_prog=(dt_c - 0.35) * 0.75)

                cx_b = (bw + 40) // 2
                paste_centered(board, sp_sub0, cx_b, 125)
                paste_centered(board, sp_main, cx_b, 275, scale=min(1.0, (bw - 80) / max(1.0, sp_main.width)))
                paste_centered(board, sp_sub1, cx_b, 435)
                paste_centered(board, sp_sub2, cx_b, 555, scale=min(1.0, (bw - 90) / max(1.0, sp_sub2.width)))

                paste_centered(comp_im, board, 540, 890, scale=0.82 + 0.18 * u_c)
                # Perched white sticker cloud behind Feel Chicken mascot on top rim of chalkboard
                cloud_m = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
                ImageDraw.Draw(cloud_m).ellipse([30, 30, 290, 290], fill=(255, 252, 244, 252), outline=(242, 168, 96, 255), width=6)
                paste_centered(cloud_m, logo_clean, 160, 160, scale=0.92)
                paste_centered(comp_im, cloud_m, 540, 495, scale=0.84 + 0.16 * u_c)

                b_l = get_sticker_badge(stickers, "FC_st_prof_chick", 235, (255, 198, 62))
                b_r = get_sticker_badge(stickers, "FC_st_gift_chicken", 235, (255, 98, 126))
                paste_centered(comp_im, b_l, 185, 1385, scale=0.75 + 0.25 * u_c, angle=-7.0)
                paste_centered(comp_im, b_r, 895, 1385, scale=0.75 + 0.25 * u_c, angle=7.0)
                draw_confetti_burst(comp_im, 185, 1385, t, t_cut2 + 0.08, 96)
                draw_confetti_burst(comp_im, 895, 1385, t, t_cut2 + 0.16, 96)

        # ======================================================================
        # SCENE 4: 100 SCHOOL & RIDDLE QUESTIONS (.DOCX POP-UP CARDS!) (22.63 .. 28.87s)
        # ======================================================================
        elif fi < segs["s4_questions"]["f1"]:
            s4_t0 = segs["s4_questions"]["t0"]
            s4_t1 = segs["s4_questions"]["t1"]
            t_mid4 = s4_t0 + 3.35  # 25.98s

            if t < t_mid4:
                idx_p = min(len(b_jar_pick) - 1, int((t - s4_t0) * 1.15 * FPS))
                comp_im = fit_cover(polish_sunny_frame(b_jar_pick[idx_p]), W, H, zoom=1.02 + 0.05 * ((t - s4_t0) / 3.35)).convert("RGBA")
            else:
                vframes = muse_vids["MUSE_fc_friends_party"]
                vf_rgb = vframes[int((t - t_mid4) * FPS) % len(vframes)]
                comp_im = fit_cover(polish_sunny_frame(vf_rgb), W, H, zoom=1.04 + 0.04 * ((t - t_mid4) / 2.88)).convert("RGBA")

            # Soft dark-warm top vignette so the 3 quiz cards read with 100% contrast
            top_grad = np.zeros((H, W, 4), dtype=np.uint8)
            yg = np.clip(1.0 - np.arange(H, dtype=np.float32) / 1150.0, 0.0, 1.0)
            top_grad[:, :, 0] = 28; top_grad[:, :, 1] = 16; top_grad[:, :, 2] = 24
            top_grad[:, :, 3] = (yg * 105.0).astype(np.uint8)[:, None]
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(top_grad, "RGBA"))

            draw_pill_banner(comp_im, "100 CÂU HỎI HỌC ĐƯỜNG & ĐỐ MẸO", 465, 136, (236, 56, 84), COL_GOLD_5, fsz=29)
            b_bulb = get_sticker_badge(stickers, "FC_st_riddle_bulb", 195, (255, 206, 68))
            paste_centered(comp_im, b_bulb, 935, 152, angle=6.0 + math.sin(t * 4.0) * 3.5)

            quiz_cards = [
                (s4_t0 + 0.22, "CẤP ĐỘ DỄ #01",     "Ngày Nhà giáo VN là ngày nào?",          "20/11",     (52, 188, 148), 355, -1),
                (s4_t0 + 1.55, "NGỮ VĂN #41",        "Ai là tác giả tác phẩm Lão Hạc?",        "Nam Cao",   (245, 142, 54), 605, +1),
                (s4_t0 + 2.95, "ĐỐ MẸO LẮT LÉO #100","Gà 1 chân 2kg, đứng 2 chân mấy kg?",     "Vẫn 2 kg!", (238, 58, 92),  855, -1),
            ]
            out_f4 = smoothstep((s4_t1 - t) / 0.25) if (s4_t1 - t) < 0.25 else 1.0
            for q_t0, q_tag, q_txt, q_ans, q_col, q_cy, q_side in quiz_cards:
                if t >= q_t0:
                    dt_q = t - q_t0
                    uq = ease_out_back(min(1.0, dt_q / 0.34), s=1.22)
                    opq = min(1.0, dt_q / 0.14) * out_f4
                    qw, qh = 964, 202
                    qc = Image.new("RGBA", (qw + 28, qh + 28), (0, 0, 0, 0))
                    qd = ImageDraw.Draw(qc)
                    qd.rounded_rectangle([14, 18, 14 + qw, 18 + qh], radius=44, fill=(35, 16, 22, 85))
                    qc = qc.filter(ImageFilter.GaussianBlur(radius=5))
                    qd = ImageDraw.Draw(qc)
                    qd.rounded_rectangle([8, 8, 20 + qw, 20 + qh], radius=48, fill=(255, 255, 255, 255))
                    qd.rounded_rectangle([14, 14, 14 + qw, 14 + qh], radius=42, fill=(255, 250, 244, 250), outline=(*q_col, 245), width=5)

                    # Tag badge top-left inside card
                    qd.rounded_rectangle([36, 30, 345, 76], radius=22, fill=(*q_col, 255))
                    sp_tg = get_text_sprite(q_tag, FONT_SANS_XB, 23, COL_CREAM_5, outer_w=0, inner_w=0, shadow_alpha=0)
                    paste_centered(qc, sp_tg, 190, 53)

                    # Answer pill top-right inside card
                    qd.rounded_rectangle([685, 28, 952, 82], radius=26, fill=(255, 226, 92, 255), outline=(*q_col, 255), width=3)
                    sp_an = get_text_sprite("Đáp án: " + q_ans, FONT_SANS_XB, 25, [(65, 24, 28)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
                    paste_centered(qc, sp_an, 818, 55, scale=min(1.0, 240.0 / max(1.0, sp_an.width)))

                    # Question line
                    sp_qq = get_text_sprite(q_txt, FONT_BUBBLE, 41, [(52, 24, 32)] * 5, outer_stroke=(255, 255, 255), outer_w=4, inner_w=0, shadow_alpha=0)
                    paste_centered(qc, sp_qq, (qw + 28) // 2, 142, scale=min(1.0, (qw - 56) / max(1.0, sp_qq.width)))

                    sx_q = 540 + q_side * (1.0 - min(1.0, uq)) * 85.0
                    paste_centered(comp_im, qc, sx_q, q_cy, scale=0.86 + 0.14 * uq, opacity=opq)

            cap_y_base = 1445

        # ======================================================================
        # SCENE 5: REAL GIFTS & PROGRAM DATES — ANH KHANG + FOOD SHOWCASE (28.87 .. 37.57s)
        # ======================================================================
        elif fi < segs["s5_gifts"]["f1"]:
            lf = min(len(v_s5) - 1, fi - segs["s5_gifts"]["f0"])
            s5_t0 = segs["s5_gifts"]["t0"]
            s5_t1 = segs["s5_gifts"]["t1"]
            lt = t - s5_t0

            rgb = polish_sunny_frame(v_s5[lf])
            matte = m_s5[min(len(m_s5) - 1, lf)]
            z = 1.02 + 0.04 * smoothstep(lt / 8.70)
            fg_im = fit_cover(rgb, W, H, zoom=z)
            fg_rgb = np.array(fg_im)
            m_im = fit_cover(np.dstack([matte * 255] * 3).astype(np.uint8), W, H, zoom=z)
            m_arr = np.array(m_im)[:, :, 0].astype(np.float32) / 255.0

            comp_im = fg_im.convert("RGBA")

            t_food_switch = s5_t0 + 3.45  # right between "quà ngon thôi nha!" and "Chương trình áp dụng..."
            if t < t_food_switch:
                vframes = muse_vids["MUSE_fc_cheese_pour"]
                vf_rgb = vframes[int((t - s5_t0) * FPS) % len(vframes)]
                draw_behind_speaker_card(comp_im, vf_rgb, t, s5_t0 + 0.06, t_food_switch + 0.15, "TOÀN QUÀ NGON TỪ FEEL CHICKEN!", (238, 54, 80), cy_pos=415, vh=630)
            else:
                vframes = muse_vids["MUSE_fc_feast_table"]
                vf_rgb = vframes[int((t - t_food_switch) * FPS) % len(vframes)]
                draw_behind_speaker_card(comp_im, vf_rgb, t, t_food_switch - 0.10, s5_t1 - 0.06, "ÁP DỤNG ĐẾN HẾT NGÀY 20/11!", (242, 134, 52), cy_pos=415, vh=630)

            # Composite real Anh Khang cleanly in FRONT!
            fg_alpha = np.maximum(m_arr, s5_lower_guard * m_arr)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

            # Cute Gift Chicken Sticker & Date Pill
            env_g1 = smooth_env(t, s5_t0 + 0.20, t_food_switch, 0.22, 0.22)
            if env_g1 > 0.01:
                b_gift = get_sticker_badge(stickers, "FC_st_gift_chicken", 225, (255, 102, 128))
                paste_centered(comp_im, b_gift, 178, 1525 + math.sin(t * 3.2) * 5.0, scale=0.82 + 0.18 * env_g1, opacity=env_g1, angle=-5.0)
                draw_confetti_burst(comp_im, 178, 1525, t, s5_t0 + 0.25, 92)

            env_g2 = smooth_env(t, t_food_switch + 0.10, s5_t1 - 0.10, 0.24, 0.24)
            if env_g2 > 0.01:
                draw_pill_banner(comp_im, "TẤT CẢ MỌI NGƯỜI • ĐẾN HẾT 20/11", 540, 1655, (236, 48, 76), COL_GOLD_5, fsz=30, scale=0.92 + 0.08 * env_g2, opacity=env_g2)

            cap_y_base = 1175

        # ======================================================================
        # SCENE 6A: TAG FRIENDS & "HỌC SINH GIỎI" CERTIFICATE (37.57 .. 43.53s)
        # ======================================================================
        elif fi < segs["s6a_outro"]["f1"]:
            s6a_t0 = segs["s6a_outro"]["t0"]
            s6a_t1 = segs["s6a_outro"]["t1"]
            vframes = muse_vids["MUSE_fc_friends_party"]
            vf_rgb = vframes[int((t - s6a_t0) * FPS) % len(vframes)]
            comp_im = fit_cover(polish_sunny_frame(vf_rgb), W, H, zoom=1.02 + 0.07 * ((t - s6a_t0) / 5.97)).convert("RGBA")

            # Cute "GIẤY KHEN HỌC SINH GIỎI FEEL CHICKEN" Card popping at upper-top (y=415)
            env_cert = smooth_env(t, s6a_t0 + 0.25, s6a_t1 - 0.08, 0.28, 0.24)
            if env_cert > 0.01:
                uc = ease_out_back(min(1.0, (t - (s6a_t0 + 0.25)) / 0.36))
                cw_c, ch_c = 940, 420
                cert = Image.new("RGBA", (cw_c + 36, ch_c + 36), (0, 0, 0, 0))
                cd = ImageDraw.Draw(cert)
                cd.rounded_rectangle([18, 24, 18 + cw_c, 24 + ch_c], radius=52, fill=(42, 18, 24, 92))
                cert = cert.filter(ImageFilter.GaussianBlur(radius=9))
                cd = ImageDraw.Draw(cert)
                cd.rounded_rectangle([10, 10, 26 + cw_c, 26 + ch_c], radius=56, fill=(255, 255, 255, 255))
                cd.rounded_rectangle([18, 18, 18 + cw_c, 18 + ch_c], radius=48, fill=(255, 248, 232, 250), outline=(238, 54, 80, 255), width=7)
                cd.rounded_rectangle([34, 34, 2 + cw_c, 2 + ch_c], radius=36, outline=(255, 198, 68, 245), width=4)

                sp_c1 = get_text_sprite("DANH HIỆU CAO QUÝ 20/11", FONT_SANS_XB, 29, [(228, 48, 74)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
                sp_c2 = get_text_sprite("HỌC SINH GIỎI", FONT_POP, 84, COL_GOLD_5, outer_stroke=(236, 48, 76), outer_w=11, inner_stroke=(58, 20, 26), inner_w=4, sheen_prog=(t - s6a_t0) * 0.55)
                sp_c3 = get_text_sprite("RỦ HỘI BẠN CÙNG SĂN QUÀ FEEL CHICKEN!", FONT_SANS_XB, 28, [(64, 28, 34)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)

                paste_centered(cert, sp_c1, (cw_c + 36) // 2, 92)
                paste_centered(cert, sp_c2, (cw_c + 36) // 2, 218, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c2.width)))
                paste_centered(cert, sp_c3, (cw_c + 36) // 2, 342, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c3.width)))
                paste_centered(comp_im, cert, 540, 395, scale=0.84 + 0.16 * uc, opacity=env_cert)

                b_tr = get_sticker_badge(stickers, "FC_st_trophy_star", 215, (255, 204, 62))
                b_ch = get_sticker_badge(stickers, "FC_st_cheers_cups", 215, (255, 112, 146))
                paste_centered(comp_im, b_tr, 175, 1085 + math.sin(t * 3.4) * 5.0, scale=0.80 + 0.20 * uc, opacity=env_cert, angle=-6.0)
                paste_centered(comp_im, b_ch, 905, 1085 + math.cos(t * 3.4) * 5.0, scale=0.80 + 0.20 * uc, opacity=env_cert, angle=6.0)
                draw_confetti_burst(comp_im, 175, 1085, t, s6a_t0 + 0.35, 92)
                draw_confetti_burst(comp_im, 905, 1085, t, s6a_t0 + 0.45, 92)

            cap_y_base = 1415

        # ======================================================================
        # SCENE 6B: REAL ANH KHANG TWO THUMBS UP + BRAND END-CARD (43.53 .. 45.83s)
        # ======================================================================
        else:
            s6b_t0 = segs["s6b_thumbs"]["t0"]
            lf = min(len(v_s6b) - 1, fi - segs["s6b_thumbs"]["f0"])
            dt_e = t - s6b_t0
            rgb = polish_sunny_frame(v_s6b[lf])
            comp_im = fit_cover(rgb, W, H, zoom=1.01 + 0.05 * smoothstep(dt_e / 2.30)).convert("RGBA")

            ue = ease_out_back(min(1.0, dt_e / 0.32))
            paste_centered(comp_im, logo_clean, 540, 220, scale=0.82 + 0.18 * ue)
            sp_go = get_text_sprite("ĐẾN FEEL CHICKEN NGAY!", FONT_POP, 68, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(196, 28, 52), inner_w=5, sheen_prog=dt_e * 0.8)
            paste_centered(comp_im, sp_go, 540, 425, scale=min(1.0, 980.0 / max(1.0, sp_go.width)) * (0.85 + 0.15 * ue))

            # Brand Address & Hotline End-Card at Bottom (clear of Anh Khang's face & thumbs!)
            ew, eh = 992, 236
            ec = Image.new("RGBA", (ew + 28, eh + 28), (0, 0, 0, 0))
            ed = ImageDraw.Draw(ec)
            ed.rounded_rectangle([14, 18, 14 + ew, 18 + eh], radius=44, fill=(32, 14, 20, 95))
            ec = ec.filter(ImageFilter.GaussianBlur(radius=6))
            ed = ImageDraw.Draw(ec)
            ed.rounded_rectangle([8, 8, 20 + ew, 20 + eh], radius=48, fill=(255, 255, 255, 255))
            ed.rounded_rectangle([14, 14, 14 + ew, 14 + eh], radius=42, fill=(218, 36, 62, 250))

            sp_a1 = get_text_sprite("CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt", FONT_SANS_XB, 29, COL_CREAM_5, outer_w=0, inner_w=3)
            sp_a2 = get_text_sprite("Mở cửa: 10:00 – 22:00  •  Hotline: 0796 601 106", FONT_SANS_XB, 31, COL_GOLD_5, outer_w=0, inner_w=3)
            paste_centered(ec, sp_a1, (ew + 28) // 2, 86, scale=min(1.0, (ew - 40) / max(1.0, sp_a1.width)))
            paste_centered(ec, sp_a2, (ew + 28) // 2, 166, scale=min(1.0, (ew - 40) / max(1.0, sp_a2.width)))
            paste_centered(comp_im, ec, 540, 1690, scale=0.88 + 0.12 * ue)
            show_captions = False

        # ======================================================================
        # GLOBAL KAWAII WORD-BY-WORD PUFFY GRADIENT CAPTIONS
        # ======================================================================
        if show_captions:
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    op_g = smoothstep((g["t1"] - t) / 0.16) if (g["t1"] - t) < 0.16 else 1.0
                    y_start = cap_y_base if len(g["lines"]) >= 2 else cap_y_base + 34
                    lh = 76
                    gap = 16
                    for li, ln in enumerate(g["lines"]):
                        w_items = []
                        tot_w = 0
                        for wi, (wtxt, ws, we) in enumerate(ln):
                            is_g = wtxt in GOLD_KEYWORDS
                            is_c = wtxt in CORAL_KEYWORDS
                            k_sc = 1.14 if (is_g or is_c) else 1.0
                            stops = COL_GOLD_5 if is_g else (COL_CORAL_5 if is_c else COL_CREAM_5)
                            glow_c = (255, 208, 68) if is_g else ((255, 96, 126) if is_c else None)
                            fsz = 56.0 * k_sc
                            sp = get_text_sprite(wtxt, FONT_BUBBLE, fsz, stops, outer_stroke=(255, 255, 255), outer_w=8, inner_stroke=(44, 18, 24), inner_w=5, glow_col=glow_c, glow_rad=7 if glow_c else 0, shadow_alpha=90)
                            adv = int(ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_BUBBLE, fsz))) + 6
                            w_items.append((wtxt, ws, sp, adv))
                            tot_w += adv + (gap if wi > 0 else 0)

                        cur_x = max(48, min(W - 48 - tot_w, 540 - tot_w // 2))
                        cur_y = y_start + li * lh
                        for wtxt, ws, sp, adv in w_items:
                            if t >= ws - 0.02:
                                dt_w = max(0.0, t - ws)
                                u_w = ease_out_back(min(1.0, dt_w / 0.20), s=1.25)
                                wy = cur_y + (1.0 - min(1.0, u_w)) * 18.0
                                wcx = cur_x + adv // 2
                                paste_centered(comp_im, sp, wcx, wy, scale=0.88 + 0.12 * u_w, opacity=op_g * min(1.0, (dt_w + 0.03) / 0.09))
                                if wtxt in POP_EMPHASIS and 0.04 <= dt_w <= 0.36:
                                    u_p = (dt_w - 0.04) / 0.32
                                    paste_centered(comp_im, sp, wcx, cur_y, scale=1.0 + 0.55 * ease_out_cubic(u_p), opacity=op_g * (1.0 - u_p) * 0.38)
                            cur_x += adv + gap
                    break

        # Global subtle Kawaii corner sparkles & frame border
        draw_kawaii_frame_border(comp_im, t)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"fc_test_{len(test_saved):02d}.jpg")
            comp_im.convert("RGB").save(tp, quality=92)
            test_saved.append((t, tp))
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        if (fi + 1) % 250 == 0:
            el = time.time() - t_start
            print(f"  Rendered {fi+1}/{total_frames} frames ({(fi+1)/el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close()
        writer.wait()

    if test_mode and test_saved:
        cols, rows = 5, 2
        tw, th = 324, 576
        grid = Image.new("RGB", (tw * cols, th * rows), (24, 20, 24))
        for i, (ts, tp) in enumerate(test_saved[:10]):
            im = Image.open(tp).resize((tw, th), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 110, 28], fill=(0, 0, 0))
            d.text((8, 6), f"t={ts:.2f}s", fill=(255, 230, 80))
            grid.paste(im, ((i % cols) * tw, (i // cols) * th))
        gp = os.path.join(CHECK_DIR, "fc_kute_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved 10-frame test grid:", gp, flush=True)
    else:
        print(f"Finished rendering {total_frames} frames -> {raw_vid_out} in {time.time()-t_start:.1f}s", flush=True)

if __name__ == "__main__":
    main()
