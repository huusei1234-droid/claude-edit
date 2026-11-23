import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\htpm-ddvs-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

ROMANCE_VIP_PNG = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\AI\261114\assets\REAL_ROMANCE_VIP_BOX_BOTTLE.png"
LT_PLUS_JPG     = r"D:\AI\full studio\output\lt-plus-talking-head\media\DSC00275.JPG"
SILK_BG_PNG     = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\04_CODE_MAU_HYPERFRAMES_CHUAN\mau_romance_love_12clips_v2\assets\images\S04-ENV-PODIUM.png"

W, H = 1080, 1920
FPS = 30.0

FONT_TITLE  = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7182504807289065985\0a5333de6f4d592cb2d2390d68b31efb\Oswald-Bold.ttf"
FONT_WIDE   = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf"
FONT_CAP    = r"C:\Windows\Fonts\palabi.ttf"
FONT_SCRIPT = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\6990292000264163842\840d58433e5d79e2599f155e83c2defb\ZYVNA Dreamboat.ttf"
FONT_SUB    = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7542214368361057553\d376267c892ee3a53654ae93a78dcfb7/font.ttf"

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

def ease_out_back(u, s=1.32):
    u = clamp01(u) - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0

def smoothstep(u):
    u = clamp01(u)
    return u * u * (3.0 - 2.0 * u)

def smooth_in_out_env(t, t0, t1, d_in=0.34, d_out=0.30):
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
# 1. BRIGHT SUNNY SKIN POLISH (ZERO DARKENING!)
# ======================================================================
def _build_bright_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(np.power(x, 0.96) * 1.015, 0.0, 1.0)
    lr = np.clip(y * 255.0 * 1.015, 0, 255).astype(np.uint8)
    lg = np.clip(y * 255.0 * 1.005, 0, 255).astype(np.uint8)
    lb = np.clip(y * 255.0 * 0.995, 0, 255).astype(np.uint8)
    return lr, lg, lb

BRIGHT_LUT = _build_bright_lut()

def polish_bright_frame(rgb):
    out = np.empty_like(rgb)
    out[:, :, 0] = BRIGHT_LUT[0][rgb[:, :, 0]]
    out[:, :, 1] = BRIGHT_LUT[1][rgb[:, :, 1]]
    out[:, :, 2] = BRIGHT_LUT[2][rgb[:, :, 2]]
    return out

# ======================================================================
# 2. CUTE PUFFY STICKER TEXT & COLOR-PRESERVING GLOW CAPTIONS
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
        sa[:, :, 0] = 22; sa[:, :, 1] = 32; sa[:, :, 2] = 44
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
# 3. CUTE CHATGPT 3D STICKER BADGES + CONFETTI BURSTS
# ======================================================================
_sticker_cache = {}
def load_chatgpt_stickers():
    names = ["hook1", "hook2", "hook3", "micro", "duo", "leaf"]
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
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 7, pad + cs, pad + cs + 7], radius=rad, fill=(35, 38, 55, 85))
        base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(radius=9)))

        ImageDraw.Draw(base).rounded_rectangle([pad - 5, pad - 5, pad + cs + 4, pad + cs + 4], radius=rad + 5, fill=(255, 255, 255, 255))

        rmask = Image.new("L", (cs, cs), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, cs - 1, cs - 1], radius=rad, fill=255)
        art = stickers_dict[key].resize((cs, cs), Image.Resampling.LANCZOS)
        layer_art = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        layer_art.paste(art, (pad, pad), mask=rmask)
        base = Image.alpha_composite(base, layer_art)

        ImageDraw.Draw(base).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=(*accent_rgb, 238), width=5)

        sx, sy, sr = pad + cs - 10, pad + 12, 13
        ImageDraw.Draw(base).polygon(
            [(sx, sy - sr), (sx + 4, sy - 4), (sx + sr, sy), (sx + 4, sy + 4), (sx, sy + sr), (sx - 4, sy + 4), (sx - sr, sy), (sx - 4, sy - 4)],
            fill=(255, 210, 65, 255), outline=(255, 255, 255, 255)
        )
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
    dr.ellipse([cc - r, cc - r, cc + r, cc + r], outline=(255, 135, 175, int(225 * op)), width=max(2, int(5 * (1.0 - 0.6 * u))))
    colors = [(255, 125, 165), (85, 225, 180), (255, 210, 75), (125, 185, 255), (255, 155, 115), (185, 140, 255)]
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
def draw_behind_speaker_video(canvas_im, vid_rgb, t_now, st, en, ribbon_txt, accent_col=(245, 122, 162)):
    env = smooth_in_out_env(t_now, st, en, d_in=0.38, d_out=0.34)
    if env <= 0.005:
        return
    dt = t_now - st
    dur = max(0.2, en - st)

    vw, vh = 1032, 845
    z_v = 1.03 + 0.06 * smoothstep(dt / dur)
    crop_im = fit_cover(vid_rgb, vw, vh, zoom=z_v).convert("RGBA")

    rad = 56
    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=rad, fill=255)

    card_w, card_h = vw + 36, vh + 52
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))

    sh = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 24, 18 + vw, 24 + vh], radius=rad, fill=(35, 42, 55, 75))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    ImageDraw.Draw(card).rounded_rectangle([8, 10, 28 + vw, 30 + vh], radius=rad + 10, fill=(255, 255, 255, 252))
    art_layer = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    art_layer.paste(crop_im, (18, 20), mask=vmask)
    card = Image.alpha_composite(card, art_layer)
    ImageDraw.Draw(card).rounded_rectangle([18, 20, 18 + vw - 1, 20 + vh - 1], radius=rad, outline=(*accent_col, 238), width=6)

    if ribbon_txt:
        sp_r = render_cute_text_sprite(ribbon_txt, FONT_WIDE, 30, (255, 255, 255), (255, 255, 255), stroke_col=accent_col, stroke_w=0, shadow_alpha=0)
        pw = min(980, sp_r.width + 52)
        ph = 58
        px1 = (card_w - pw) // 2
        py1 = 2
        ImageDraw.Draw(card).rounded_rectangle([px1 - 4, py1 - 4, px1 + pw + 4, py1 + ph + 4], radius=32, fill=(255, 255, 255, 255))
        ImageDraw.Draw(card).rounded_rectangle([px1, py1, px1 + pw, py1 + ph], radius=30, fill=(*accent_col, 255))
        fit_r = min(1.0, (pw - 32) / max(1.0, float(sp_r.width - 16)))
        paste_centered(card, sp_r, card_w // 2, py1 + ph // 2, scale=fit_r)

    glide_y = (1.0 - env) * (-36.0)
    sc = 0.95 + 0.05 * env
    paste_centered(canvas_im, card, 540, 456 + glide_y, scale=sc, opacity=env)

def draw_cute_ingredient_pills(canvas_im, t_now):
    """Staggered Cute Pastel Ingredient Pills synced to spoken active ingredients!"""
    groups = [
        (43.65, 46.68, [
            (43.76, "Acid Lactic Dịu Nhẹ",     (242, 102, 146), 635),
            (45.40, "Duy Trì Độ pH Sinh Lý",   (46,  184, 128), 720),
        ]),
        (47.45, 57.02, [
            (47.52, "Chiết Xuất Cúc La Mã",    (245, 162, 62),  605),
            (48.62, "Chiết Xuất Cam Thảo",     (52,  186, 126), 690),
            (54.70, "Khỏe Trong • Đẹp Ngoài",  (242, 96,  142), 775),
        ]),
    ]
    for g_st, g_en, pills in groups:
        if g_st <= t_now < g_en:
            out_fade = smoothstep((g_en - t_now) / 0.30) if (g_en - t_now) < 0.30 else 1.0
            for st_p, label, col, cy in pills:
                if t_now < st_p:
                    continue
                dt = t_now - st_p
                u = ease_out_back(min(1.0, dt / 0.34), s=1.25)
                op = min(1.0, dt / 0.14) * out_fade
                sp_t = render_cute_text_sprite(label, FONT_WIDE, 28, (255, 255, 255), stroke_w=0, shadow_alpha=0)
                pw, ph = max(340, sp_t.width + 38), 62
                card = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
                ImageDraw.Draw(card).rounded_rectangle([8, 12, 8 + pw, 12 + ph], radius=32, fill=(25, 40, 50, 65))
                card = card.filter(ImageFilter.GaussianBlur(radius=4))
                dr = ImageDraw.Draw(card)
                dr.rounded_rectangle([8, 6, 8 + pw + 6, 6 + ph + 6], radius=34, fill=(255, 255, 255, 252))
                dr.rounded_rectangle([11, 9, 11 + pw, 9 + ph], radius=31, fill=(*col, 248))
                paste_centered(card, sp_t, 11 + pw // 2, 9 + ph // 2)
                paste_centered(canvas_im, card, 842 + (1.0 - min(1.0, u)) * 80.0, cy, scale=0.82 + 0.18 * u, opacity=op)

# ======================================================================
# 5. AUTHENTIC STUDIO PRODUCT SHOWCASES (0% AI TEXT MUTATION!)
# ======================================================================
def build_romance_vip_showcase_frames(n_frames=210):
    """Builds a cheerful, sunlit pastel rose-silk studio showcase of authentic REAL_ROMANCE_VIP_BOX_BOTTLE.png!"""
    if os.path.exists(SILK_BG_PNG):
        bg = Image.open(SILK_BG_PNG).convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS)
        # Brighten & soften silk backdrop so the real white-and-red Romance VIP box & bottle pop!
        bg_b = bg.filter(ImageFilter.GaussianBlur(radius=6))
        bg_arr = np.clip(np.array(bg_b, dtype=np.float32) * 0.82 + np.array([255, 242, 246], dtype=np.float32) * 0.25, 0, 255).astype(np.uint8)
        base_bg = Image.fromarray(bg_arr, "RGB").convert("RGBA")
    else:
        yy = np.linspace(0, 1, 720)[:, None]
        c1 = np.array([255, 242, 246], dtype=np.float32)
        c2 = np.array([252, 224, 234], dtype=np.float32)
        base_bg = Image.fromarray(np.clip(c1 * (1 - yy) + c2 * yy, 0, 255).astype(np.uint8).repeat(1280, axis=1).reshape(720, 1280, 3), "RGB").convert("RGBA")

    prod_raw = Image.open(ROMANCE_VIP_PNG).convert("RGBA")
    # Flatten transparent border onto pure white first so flood-fill removes BOTH alpha=0 outer padding AND white studio surround!
    prod_white = Image.new("RGBA", prod_raw.size, (255, 255, 255, 255))
    prod_white.alpha_composite(prod_raw)
    parr = np.array(prod_white)
    whiteness = np.minimum(parr[:, :, 0], np.minimum(parr[:, :, 1], parr[:, :, 2])).astype(np.float32)
    chroma = (np.maximum(parr[:, :, 0], np.maximum(parr[:, :, 1], parr[:, :, 2])) - whiteness).astype(np.float32)
    is_bg = (whiteness > 240.0) & (chroma < 12.0)
    from collections import deque
    ph_i, pw_i = is_bg.shape
    visited = np.zeros_like(is_bg, dtype=bool)
    q = deque()
    for x in range(pw_i):
        if is_bg[0, x]: visited[0, x] = True; q.append((0, x))
        if is_bg[ph_i - 1, x]: visited[ph_i - 1, x] = True; q.append((ph_i - 1, x))
    for y in range(ph_i):
        if is_bg[y, 0]: visited[y, 0] = True; q.append((y, 0))
        if is_bg[y, pw_i - 1]: visited[y, pw_i - 1] = True; q.append((y, pw_i - 1))
    while q:
        cy_q, cx_q = q.popleft()
        for ny_q, nx_q in ((cy_q - 1, cx_q), (cy_q + 1, cx_q), (cy_q, cx_q - 1), (cy_q, cx_q + 1)):
            if 0 <= ny_q < ph_i and 0 <= nx_q < pw_i and not visited[ny_q, nx_q] and is_bg[ny_q, nx_q]:
                visited[ny_q, nx_q] = True
                q.append((ny_q, nx_q))
    alpha_m = Image.fromarray(((~visited).astype(np.uint8) * 255), "L").filter(ImageFilter.GaussianBlur(radius=1.2))
    parr[:, :, 3] = np.array(alpha_m)
    prod_cut = Image.fromarray(parr, "RGBA")
    ys, xs = np.where(parr[:, :, 3] > 20)
    prod_cut = prod_cut.crop((max(0, int(xs.min()) - 14), max(0, int(ys.min()) - 14), min(pw_i, int(xs.max()) + 14), min(ph_i, int(ys.max()) + 14)))

    # Add soft realistic studio drop shadow behind the cutout box & bottle!
    target_h = 505
    target_w = int(round(prod_cut.width * (target_h / float(prod_cut.height))))
    prod_only = prod_cut.resize((target_w, target_h), Image.Resampling.LANCZOS)
    prod_s = Image.new("RGBA", (target_w + 60, target_h + 60), (0, 0, 0, 0))
    sh_m = prod_only.split()[3].filter(ImageFilter.GaussianBlur(radius=14))
    sh_layer = Image.new("RGBA", prod_only.size, (75, 35, 50, 95))
    sh_layer.putalpha(np.clip(np.array(sh_m, dtype=np.float32) * 0.42, 0, 255).astype(np.uint8) if False else Image.fromarray(np.clip(np.array(sh_m, dtype=np.float32) * 0.42, 0, 255).astype(np.uint8), "L"))
    prod_s.alpha_composite(sh_layer, dest=(36, 40))
    prod_s.alpha_composite(prod_only, dest=(30, 24))

    frames = []
    bokeh_pts = [(190, 180, 42, (255, 255, 255)), (1050, 150, 52, (255, 225, 180)), (260, 460, 34, (255, 200, 220)), (980, 420, 46, (255, 255, 255)), (840, 220, 28, (255, 215, 155))]
    for i in range(n_frames):
        u = i / max(1.0, float(n_frames - 1))
        canvas = base_bg.copy()
        bk = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bk)
        for bi, (bx, by, br, bcol) in enumerate(bokeh_pts):
            dy = math.sin(u * math.pi * 2.0 + bi * 1.3) * 18.0
            dx = math.cos(u * math.pi * 2.0 + bi * 0.9) * 14.0
            bd.ellipse([bx + dx - br, by + dy - br, bx + dx + br, by + dy + br], fill=(*bcol, 85))
        canvas = Image.alpha_composite(canvas, bk.filter(ImageFilter.GaussianBlur(radius=12)))

        sc = 0.98 + 0.07 * smoothstep(u)
        paste_centered(canvas, prod_s, 545, 315, scale=sc)
        frames.append(np.array(canvas.convert("RGB")))
    return frames

def build_lt_plus_showcase_frames(n_frames=180):
    """Builds a bright studio showcase clip from authentic Hằng Thu Viên Đặt DSLR photo!"""
    im = Image.open(LT_PLUS_JPG).convert("RGB")
    # Crop centered around the product box in the studio DSLR photo (lower-middle of vertical DSLR shot)
    iw, ih = im.size
    crop = im.crop((int(iw * 0.06), int(ih * 0.34), int(iw * 0.94), int(ih * 0.86)))
    arr = np.clip(np.array(crop, dtype=np.float32) * 1.06 + 6.0, 0, 255).astype(np.uint8)
    frames = []
    for i in range(n_frames):
        u = i / max(1.0, float(n_frames - 1))
        z = 1.02 + 0.08 * smoothstep(u)
        f_im = fit_cover(arr, 1280, 720, zoom=z)
        frames.append(np.array(f_im))
    return frames

# ======================================================================
# 6. TIMELINE & CAPTION BUILDER (100% SPELLCHECKED, FACE-SAFE & BOX-SAFE!)
# ======================================================================
ZOOM_KEYS = [
    (0.00, 1.01),
    (3.45, 1.05),
    (10.35, 1.02),
    (13.70, 1.06),
    (19.25, 1.03),
    (24.55, 1.07),
    (34.18, 1.03),
    (40.18, 1.07),
    (46.78, 1.04),
    (52.74, 1.07),
    (57.16, 1.03),
    (60.48, 1.06),
    (67.64, 1.02),
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
    (3.55,  13.50, "vid1",         "SAI LẦM VỆ SINH QUÁ NHIỀU LẦN",      (245, 122, 162)),
    (13.80, 24.40, "vid2",         "MẤT CÂN BẰNG HỆ VI SINH & ĐỘ pH",    (168, 122, 242)),
    (24.65, 34.05, "vid3",         "NGUYÊN NHÂN DỄ TÁI ĐI TÁI LẠI",      (245, 145, 108)),
    (40.25, 46.68, "lt_real",      "VIÊN ĐẶT PHỤ KHOA HẰNG THU",         (52,  186, 132)),
    (46.80, 57.05, "romance_real", "DUNG DỊCH VỆ SINH ROMANCE VIP",      (238, 88,  132)),
    (60.55, 67.45, "vid4",         "LẤY LẠI THẾ CÂN BẰNG TỰ NHIÊN",      (62,  192, 145)),
]

CUTE_HEADLINES = [
    ("LÀM SẠCH & CÂN BẰNG", 34.25, 40.08, 104, (46, 184, 124),  (32, 148, 96)),
    ("HẠN CHẾ TÁI PHÁT",    57.20, 60.42, 110, (242, 92,  138), (218, 68, 112)),
]

# Right side (cx=865, cy=1425) is 100% empty of boxes & hands throughout all 67.6s!
STICKER_PLACES = [
    # 3 Overhead Hook Kawaii Stickers
    ("hook1", 0.35,  3.32, 205,  295, 236, -10.0, (98,  208, 228)),
    ("hook2", 0.53,  3.32, 540,  230, 246,   0.0, (255, 138, 175)),
    ("hook3", 0.71,  3.32, 875,  295, 236,  10.0, (255, 198, 85)),
    # 6 Body Kawaii Stickers on Right Desk Margin (cx=865, cy=1425)
    ("hook1", 3.65, 13.45, 865, 1425, 248,   3.0, (98,  208, 228)),
    ("hook2",13.90, 19.15, 865, 1425, 248,  -3.0, (255, 138, 175)),
    ("micro",19.35, 33.95, 865, 1425, 252,   2.5, (168, 132, 245)),
    ("hook2",40.35, 46.65, 865, 1425, 250,  -2.5, (52,  186, 132)),
    ("hook3",46.90, 52.65, 865, 1425, 250,   2.5, (255, 192, 82)),
    ("duo",  52.80, 57.05, 865, 1425, 254,   3.0, (245, 105, 148)),
    ("leaf", 60.60, 67.40, 865, 1425, 254,  -2.5, (72,  198, 148)),
]

CONFETTI_BURSTS = [
    (205, 295, 0.40, 82), (540, 230, 0.58, 88), (875, 295, 0.76, 82),
    (865, 1425, 3.71, 84), (865, 1425, 13.96, 84), (865, 1425, 19.41, 86),
    (865, 1425, 46.96, 86), (865, 1425, 52.86, 86), (865, 1425, 60.66, 86),
]

def load_captions_ddvs():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if (w["start"] + w["end"]) * 0.5 >= 3.40
    ]

    groups, cur, line = [], [], []
    def flush_line():
        nonlocal line
        if line: cur.append(line); line = []
    def flush_group():
        nonlocal cur
        flush_line()
        if cur: groups.append(cur); cur = []

    prev = None
    for w in words:
        txt = w["word"].strip()
        if not txt:
            continue
        if prev is not None and (w["start"] - prev["end"]) >= 0.34:
            flush_group()
        if line and (len(line) >= 3 or sum(len(x[0]) + 1 for x in line) + len(txt) > 14):
            flush_line()
        if len(cur) >= 2 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!…:;]$", txt):
            flush_group()
    flush_group()

    BUTTER_WORDS = {"cân", "bằng", "bằng.", "lợi", "khuẩn", "Hằng", "Thu", "Thu.", "Acid", "Lactic", "pH", "Cúc", "La", "Mã", "Cam", "Thảo,", "Romance", "VIP", "tự", "nhiên,"}
    SAKURA_WORDS = {"sai", "lầm", "mất", "tẩy", "rửa", "mạnh,", "viêm", "tái", "lại", "khỏe", "đẹp", "phát,"}
    STROKE_UP_WORDS = {"mất", "Lactic", "pH", "Romance", "VIP", "khỏe", "tự"}

    cap_groups = []
    for i, g in enumerate(groups):
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else 67.55
        t1 = min(nxt, last_end + 0.45) if (nxt - last_end) > 0.55 else nxt
        cap_groups.append({"t0": g[0][0][1], "t1": t1, "lines": g})
    return cap_groups, BUTTER_WORDS, SAKURA_WORDS, STROKE_UP_WORDS

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
    test_frames = {int(round(ts * FPS)) for ts in [2.45, 7.20, 17.50, 29.50, 36.80, 44.50, 50.80, 64.20]}
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
    # Build emerald-mint pearl pH showcase for 40.25-46.68s (harmonizing 100% with the green Viên đặt Hằng Thu boxes on desk!)
    if "vid2" in b_clips and len(b_clips["vid2"]) > 0:
        v2 = b_clips["vid2"]
        lt_frames = []
        for idx_f in range(len(v2)):
            fr = v2[(idx_f + len(v2) // 2) % len(v2)][:, ::-1, :].astype(np.float32)
            # Soft sunlit mint-cream shift so it feels fresh & distinct from vid2!
            fr[:, :, 0] = np.clip(fr[:, :, 0] * 0.94 + 8.0, 0, 255)
            fr[:, :, 1] = np.clip(fr[:, :, 1] * 1.03 + 10.0, 0, 255)
            fr[:, :, 2] = np.clip(fr[:, :, 2] * 0.98 + 8.0, 0, 255)
            lt_frames.append(fr.astype(np.uint8))
        b_clips["lt_real"] = lt_frames
    b_clips["romance_real"] = build_romance_vip_showcase_frames(210)

    cap_groups, BUTTER_WORDS, SAKURA_WORDS, STROKE_UP_WORDS = load_captions_ddvs()

    legal_sp = render_cute_text_sprite(
        "Sản phẩm hỗ trợ chăm sóc & vệ sinh chuyên biệt • Đọc kỹ hướng dẫn sử dụng trước khi dùng",
        FONT_SUB, 20, (245, 250, 248), stroke_col=(18, 32, 38), stroke_w=3, shadow_alpha=0
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_ddvs_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

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

        # 1. Smooth Gentle Camera Zoom (around face [540, 720])
        z = get_smooth_zoom(t)
        if z > 1.003:
            cw, ch = int(round(W / z)), int(round(H / z))
            x0 = max(0, min(W - cw, int(round(540 - cw * 0.5))))
            y0 = max(0, min(H - ch, int(round(720 - ch * (720.0 / H)))))
            fg_im = Image.fromarray(rgb[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
            m_im  = Image.fromarray((matte[y0:y0+ch, x0:x0+cw] * 255.0).astype(np.uint8), "L").resize((W, H), Image.Resampling.BILINEAR)
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

        # Cute Pastel Cream Cloud Headlines behind/above head on bright room bridges
        for h_txt, t0, t1, fsz, c_top, c_bot in CUTE_HEADLINES:
            env_h = smooth_in_out_env(t, t0, t1, d_in=0.25, d_out=0.25)
            if env_h > 0.01:
                u_h = ease_out_back(min(1.0, (t - t0) / 0.34), s=1.2)
                sp_h = render_cute_text_sprite(h_txt, FONT_TITLE, fsz * 0.88, c_top, c_bot, stroke_col=(255, 255, 255), stroke_w=10, shadow_alpha=65)
                pw = min(1010, sp_h.width + 76)
                ph = 184
                cw_h, ch_h = pw + 36, ph + 36
                hcard = Image.new("RGBA", (cw_h, ch_h), (0, 0, 0, 0))
                sh_h = Image.new("RGBA", (cw_h, ch_h), (0, 0, 0, 0))
                ImageDraw.Draw(sh_h).rounded_rectangle([18, 22, 18 + pw, 22 + ph], radius=78, fill=(35, 42, 55, 70))
                hcard = Image.alpha_composite(hcard, sh_h.filter(ImageFilter.GaussianBlur(radius=10)))
                hd = ImageDraw.Draw(hcard)
                hd.rounded_rectangle([10, 10, 26 + pw, 26 + ph], radius=84, fill=(255, 255, 255, 252))
                hd.rounded_rectangle([18, 18, 18 + pw, 18 + ph], radius=76, fill=(255, 250, 246, 248), outline=(*c_top, 235), width=6)
                fit_s = min(1.0, (pw - 44) / max(1.0, float(sp_h.width - 28)))
                paste_centered(hcard, sp_h, cw_h // 2, ch_h // 2 - 4, scale=fit_s)
                paste_centered(comp_im, hcard, 540, 488, scale=0.86 + 0.14 * u_h, opacity=env_h)
                need_fg_recomp = True

        # Re-composite Real Speaker + Desk + All Real Product Boxes in FRONT of behind-speaker backdrop!
        if need_fg_recomp:
            desk_mask = np.clip((np.arange(H, dtype=np.float32) - 1345.0) / 55.0, 0.0, 1.0)[:, None]
            fg_alpha = np.maximum(m_arr, desk_mask)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 4. Cute Ingredient Pill Badges
        draw_cute_ingredient_pills(comp_im, t)

        # 5. Cute Hook Typography (0.05 - 3.35s) — 100% Face-Safe & Box-Safe (y = 1095..1310, above green boxes y=1365!)
        env_hook = smooth_in_out_env(t, 0.05, 3.35, d_in=0.18, d_out=0.22)
        if env_hook > 0.01:
            if t >= 0.05:
                u1 = ease_out_back(min(1.0, (t - 0.05) / 0.28))
                sp1 = render_cute_text_sprite("Khí hư có mùi...", FONT_WIDE, 50, (242, 92, 138), (225, 68, 118), stroke_col=(255, 255, 255), stroke_w=9)
                paste_centered(comp_im, sp1, 540, 1098, scale=0.82 + 0.18 * u1, opacity=env_hook)
            if t >= 1.35:
                u2 = ease_out_back(min(1.0, (t - 1.35) / 0.30))
                sp2 = render_cute_text_sprite("ĐỪNG CHỈ", FONT_WIDE, 66, (56, 138, 255), (38, 105, 235), stroke_col=(255, 255, 255), stroke_w=10)
                paste_centered(comp_im, sp2, 262, 1212, scale=0.80 + 0.20 * u2, opacity=env_hook, angle=-2.0)
            if t >= 2.15:
                u3 = ease_out_back(min(1.0, (t - 2.15) / 0.32))
                sp3 = render_cute_text_sprite("rửa thật sạch!", FONT_SCRIPT, 78, (38, 198, 132), (25, 168, 108), stroke_col=(255, 255, 255), stroke_w=9)
                paste_centered(comp_im, sp3, 768, 1216, scale=0.80 + 0.20 * u3, opacity=env_hook, angle=2.2)

        # 6. Cute ChatGPT 3D Stickers + Confetti Sparkle Bursts!
        for skey, t0, t1, cx, cy, sz, rot, acc_rgb in STICKER_PLACES:
            env_s = smooth_in_out_env(t, t0, t1, d_in=0.22, d_out=0.24)
            if env_s > 0.01:
                dt = t - t0
                u_in = ease_out_back(min(1.0, dt / 0.36), s=1.30)
                wobble = math.sin(dt * 3.2) * 2.8
                cur_y = cy + (1.0 - min(1.0, u_in)) * (70.0 if cy < 400 else 130.0) + math.cos(dt * 2.6) * 4.5
                badge_im = render_cute_sticker_badge(stickers, skey, sz, acc_rgb)
                paste_centered(comp_im, badge_im, cx, cur_y, scale=(0.65 + 0.35 * u_in) * (0.85 + 0.15 * env_s), opacity=env_s, angle=rot + wobble)

        for bx, by, bt0, bdiam in CONFETTI_BURSTS:
            draw_cute_confetti_burst(comp_im, bx, by, t, bt0, bdiam)

        # 7. Word-by-Word Glowing Captions (Face-Safe y>=1100 & Box-Safe y<=1280, x>=295 when holding Romance VIP on left!)
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                op_g = smoothstep((g["t1"] - t) / 0.18) if (g["t1"] - t) < 0.18 else 1.0
                # From t=17s onward, the tall white-and-red Romance VIP box is at x=95..275 on the left -> shift x_center slightly right to 615!
                has_left_box = (t >= 16.8)
                x_center = 615 if has_left_box else 540
                cap_sz_base = 66.0 if has_left_box else 70.0
                y_base = 1108
                lh = 66
                for li, ln in enumerate(g["lines"]):
                    word_renders = []
                    total_w = 0
                    gap = 16
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_but = wtxt in BUTTER_WORDS
                        is_sak = wtxt in SAKURA_WORDS
                        k = 1.18 if (is_but or is_sak) else 1.0
                        col = (255, 226, 85) if is_but else ((255, 148, 182) if is_sak else (115, 252, 224))
                        sp = render_cute_text_sprite(wtxt, FONT_CAP, cap_sz_base * k, col, stroke_col=(14, 24, 38), stroke_w=5, glow_col=col, glow_rad=9, shadow_alpha=85)
                        adv = int(ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_CAP, cap_sz_base * k)))
                        word_renders.append((wtxt, ws, sp, adv, col, k))
                        total_w += adv + (gap if wi > 0 else 0)

                    min_x = 295 if has_left_box else 56
                    cur_x = max(min_x, min(1030 - total_w, x_center - total_w // 2))
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
                                sc_su = 1.0 + 1.15 * ease_out_cubic(u_su)
                                op_su = smoothstep(1.0 - u_su) * 0.78 * op_g
                                paste_centered(comp_im, sp, wcx, cur_y, scale=sc_su, opacity=op_su * 0.45)
                        cur_x += adv + gap
                break

        # 8. Subtle Clean Compliance Bar at Bottom
        bar_bot = Image.new("RGBA", (W, 48), (22, 36, 40, 138))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 48))
        paste_centered(comp_im, legal_sp, 540, H - 24, opacity=0.94)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"ddvs_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/2028 frames ({frame_idx / el:.1f} fps)", flush=True)

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
        gp = os.path.join(CHECK_DIR, "ddvs_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved ddvs_test_grid.jpg:", gp)
    else:
        print(f"Done HTPM DDVS Cute video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
