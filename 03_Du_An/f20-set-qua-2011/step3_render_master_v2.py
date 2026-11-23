import os, sys, json, math, subprocess, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

V2_DIR   = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"
OUT_ROOT = r"d:\AI\full studio\output\f20-set-qua-2011"
FONT_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"

F_MONT_BLK = os.path.join(FONT_DIR, "Montserrat-Black.ttf")
F_BE_XBOLD = os.path.join(FONT_DIR, "BeVietnamPro-ExtraBold.ttf")
F_FRAUNCES = os.path.join(FONT_DIR, "Fraunces-Black.ttf")
F_PLAYFAIR = os.path.join(FONT_DIR, "PlayfairDisplay-ExtraBold.ttf")

W, H, FPS = 1080, 1920, 30

# ======================================================================
# 1. EASING & MATH HELPERS
# ======================================================================
def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else float(x))

def quintic_smooth(u):
    u = clamp01(u)
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

def ease_out_cubic(u):
    u = clamp01(u)
    inv = 1.0 - u
    return 1.0 - inv * inv * inv

def ease_out_back(u, s=1.55):
    u = clamp01(u) - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0

_font_cache = {}
def get_font(path, sz):
    k = (path, int(round(sz)))
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, int(round(sz)))
    return _font_cache[k]

def paste_rgba_centered(canvas_rgba, sprite_rgba, cx, cy, scale=1.0, opacity=1.0):
    if opacity <= 0.008 or scale <= 0.02:
        return
    sp = sprite_rgba
    if abs(scale - 1.0) > 0.012:
        nw = max(2, int(round(sp.width * scale)))
        nh = max(2, int(round(sp.height * scale)))
        sp = sp.resize((nw, nh), Image.Resampling.BICUBIC)
    if opacity < 0.992:
        r, g, b, a = sp.split()
        a = a.point(lambda v: int(v * opacity))
        sp = Image.merge("RGBA", (r, g, b, a))
    x0 = int(round(cx - sp.width * 0.5))
    y0 = int(round(cy - sp.height * 0.5))
    canvas_rgba.alpha_composite(sp, (x0, y0))

# ======================================================================
# 2. 5-STOP GRADIENT + 2-LAYER SEPARATED STROKE TEXT ENGINE
# ======================================================================
GRAD_STOPS = {
    "gold": [
        (0.00, (255, 252, 224)),
        (0.26, (255, 226, 102)),
        (0.52, (255, 182,   8)),
        (0.76, (255, 240, 172)),
        (1.00, (222, 136,   0)),
    ],
    "ruby": [
        (0.00, (255, 238, 242)),
        (0.28, (255, 118, 144)),
        (0.54, (226,  24,  62)),
        (0.78, (255, 152, 172)),
        (1.00, (162,  10,  38)),
    ],
    "white": [
        (0.00, (255, 255, 255)),
        (0.60, (252, 250, 246)),
        (1.00, (238, 232, 222)),
    ],
}

def eval_5stop_vertical(h, mode):
    stops = GRAD_STOPS[mode]
    yy = np.linspace(0.0, 1.0, max(2, h), dtype=np.float32)
    out = np.zeros((max(2, h), 3), dtype=np.float32)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        m = (yy >= p0) & (yy <= p1)
        u = np.clip((yy - p0) / max(1e-5, p1 - p0), 0.0, 1.0)[:, None]
        seg = np.array(c0, dtype=np.float32) * (1.0 - u) + np.array(c1, dtype=np.float32) * u
        out[m] = seg[m]
    return np.clip(out, 0, 255).astype(np.uint8)

_text_cache = {}
def render_2layer_grad_sprite(text, font_path, size, grad_mode="white", stroke_col=(24, 12, 8), stroke_w=7, glow_col=None, glow_rad=9, shadow_alpha=150):
    key = (text, font_path, int(size), grad_mode, stroke_col, stroke_w, glow_col, glow_rad, shadow_alpha)
    if key in _text_cache:
        return _text_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bb[2] - bb[0])
    th = max(4, bb[3] - bb[1])
    pad = int(max(glow_rad * 2.2 if glow_col else 8, 10) + stroke_w + 10)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bb[0], pad - bb[1]

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    # Layer 0: Soft Aura Glow (for emphasized keywords!)
    if glow_col and glow_rad > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(1, stroke_w // 2), stroke_fill=255)
        gb = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad)), dtype=np.float32)
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0] = glow_col[0]; ga[:, :, 1] = glow_col[1]; ga[:, :, 2] = glow_col[2]
        ga[:, :, 3] = np.clip(gb * 0.72, 0, 220).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(ga, "RGBA"))

    # Layer 1: Diffused Ground Shadow
    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 5), text, font=font, fill=255, stroke_width=stroke_w, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5.5)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0] = 10; sa[:, :, 1] = 6; sa[:, :, 2] = 4
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

    # Layer 2 (.grad-back): Separated Outer Stroke + 2px 3D Dark Extrusion so stroke NEVER eats into gradient!
    if stroke_w > 0:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st_im)
        sd.text((ox, oy + 2), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        sd.text((ox, oy),     text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        base = Image.alpha_composite(base, st_im)

    # Layer 3 (.grad-front): Pure 5-Stop Gradient Fill (zero stroke!)
    fm = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(fm).text((ox, oy), text, font=font, fill=255)
    f_arr = np.array(fm, dtype=np.uint8)
    grad_1d = eval_5stop_vertical(th, grad_mode)
    y_idx = np.clip(np.arange(ch) - pad, 0, th - 1)
    rgb = np.broadcast_to(grad_1d[y_idx, None, :], (ch, cw, 3)).copy()
    front = Image.fromarray(np.dstack([rgb, f_arr]), "RGBA")
    base = Image.alpha_composite(base, front)

    if len(_text_cache) > 1200:
        _text_cache.clear()
    _text_cache[key] = base
    return base

def apply_specular_sheen(sprite_rgba, sweep_u):
    """Applies live diagonal metallic sheen sweep across emphasized text sprite!"""
    if sweep_u <= -0.25 or sweep_u >= 1.25:
        return sprite_rgba
    arr = np.array(sprite_rgba, dtype=np.float32)
    ch, cw, _ = arr.shape
    yy, xx = np.ogrid[0:ch, 0:cw]
    diag = (xx * 0.82 + yy * 0.35) / max(1.0, cw * 0.82 + ch * 0.35)
    sheen = np.exp(-((diag - sweep_u) ** 2) / 0.012) * 68.0
    # Only brighten opaque interior pixels
    mask = (arr[:, :, 3] > 180).astype(np.float32)
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + sheen * mask, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")

# ======================================================================
# 3. 3D IRIDESCENT CRYSTAL BUBBLES FOR MÓN 1 BIRD'S NEST (IMAGE 2 FIX!)
# ======================================================================
_bubble_cache = {}
def draw_ingredient_emblem(im_rgba, cx, cy, kind):
    d = ImageDraw.Draw(im_rgba)
    if kind == "tao_do":
        # Glossy rich crimson jujube fruit pair
        d.ellipse([cx-28, cy-16, cx+4, cy+16], fill=(178, 22, 28, 248), outline=(255, 210, 190, 220), width=2)
        d.ellipse([cx-4, cy-14, cx+28, cy+18], fill=(198, 28, 34, 252), outline=(255, 225, 200, 230), width=2)
        d.ellipse([cx+2, cy-9, cx+14, cy-2], fill=(255, 195, 195, 190))
    elif kind == "dtht":
        # Golden Cordyceps militaris strands
        for dx, ang in [(-16, -8), (-5, -2), (6, 4), (16, 9)]:
            d.line([(cx+dx, cy+18), (cx+dx+ang//2, cy-16)], fill=(238, 152, 18, 250), width=6)
            d.ellipse([cx+dx+ang//2-4, cy-21, cx+dx+ang//2+4, cy-11], fill=(255, 208, 68, 255))
    elif kind == "ky_tu":
        # Cluster of bright coral-red goji berries + tiny green leaf
        d.polygon([(cx-6, cy-14), (cx-20, cy-22), (cx-14, cy-8)], fill=(46, 158, 62, 240))
        for bx, by in [(-14, 2), (0, -6), (14, 3), (-5, 11), (9, 12)]:
            d.ellipse([cx+bx-9, cy+by-6, cx+bx+9, cy+by+6], fill=(228, 44, 28, 252), outline=(255, 210, 180, 180), width=1)
    elif kind == "duong_phen":
        # Sparkling translucent rock sugar crystal cubes
        for bx, by, sz in [(-14, 2, 14), (8, -4, 15), (-2, 10, 13)]:
            pts = [(cx+bx, cy+by-sz), (cx+bx+sz, cy+by-3), (cx+bx+4, cy+by+sz), (cx+bx-sz, cy+by+3)]
            d.polygon(pts, fill=(242, 250, 255, 235), outline=(255, 236, 175, 255))
            d.line([pts[0], pts[2]], fill=(255, 255, 255, 220), width=2)

def get_crystal_bubble_sprite(label, kind, diam, tint_rgb):
    key = (label, kind, diam, tint_rgb)
    if key in _bubble_cache:
        return _bubble_cache[key]

    S = diam + 44
    c = S * 0.5
    r = diam * 0.5
    yy, xx = np.ogrid[0:S, 0:S]
    dx = (xx.astype(np.float32) - c) / r
    dy = (yy.astype(np.float32) - c) / r
    dist2 = dx * dx + dy * dy
    inside = dist2 <= 1.0
    dist = np.sqrt(np.maximum(0.0, dist2))

    rim = np.power(np.clip(dist, 0.0, 1.0), 2.3)
    caustic_bot = np.clip(dy * 0.65 + 0.35, 0.0, 1.0) * np.exp(-((dist - 0.82) ** 2) / 0.035)
    spec_top = np.exp(-(((dx + 0.34) ** 2 + (dy + 0.38) ** 2) / 0.042))
    spec_pin = np.exp(-(((dx + 0.44) ** 2 + (dy + 0.46) ** 2) / 0.008))

    # Warm translucent pearl interior so text & emblem have crystal-clear contrast over golden bird's nest!
    rgba = np.zeros((S, S, 4), dtype=np.float32)
    rgba[:, :, 0] = 38 * (1.0 - rim * 0.55) + tint_rgb[0] * (rim * 0.65) + 55 * caustic_bot + 130 * spec_top
    rgba[:, :, 1] = 24 * (1.0 - rim * 0.55) + tint_rgb[1] * (rim * 0.65) + 45 * caustic_bot + 128 * spec_top
    rgba[:, :, 2] = 18 * (1.0 - rim * 0.55) + tint_rgb[2] * (rim * 0.65) + 38 * caustic_bot + 125 * spec_top

    alpha = (0.52 + 0.42 * rim + 0.28 * caustic_bot + 0.48 * spec_top + 0.65 * spec_pin) * 255.0
    edge_aa = np.clip((1.0 - dist) * r * 0.85, 0.0, 1.0)
    rgba[:, :, 3] = np.where(inside, np.clip(alpha, 0, 248) * edge_aa, 0.0)

    bim = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")
    aura = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(aura).ellipse([int(c - r), int(c - r), int(c + r), int(c + r)], outline=(*tint_rgb, 185), width=4)
    bim = Image.alpha_composite(aura.filter(ImageFilter.GaussianBlur(radius=6)), bim)
    ImageDraw.Draw(bim).ellipse([int(c - r + 1), int(c - r + 1), int(c + r - 1), int(c + r - 1)], outline=(255, 248, 220, 215), width=2)

    # Miniature ingredient emblem in upper third of bubble
    draw_ingredient_emblem(bim, int(c), int(c - r * 0.42), kind)

    # Crisp 2-layer Gold/White text inside bubble
    lines = label.split("\n")
    fsz = 26 if len(lines) == 1 else 23
    sps = [render_2layer_grad_sprite(ln, F_MONT_BLK, fsz, "gold", stroke_col=(26, 12, 6), stroke_w=5, shadow_alpha=95) for ln in lines]
    if len(sps) == 1:
        paste_rgba_centered(bim, sps[0], c, c + 22, scale=1.0, opacity=1.0)
    else:
        paste_rgba_centered(bim, sps[0], c, c + 8,  scale=1.0, opacity=1.0)
        paste_rgba_centered(bim, sps[1], c, c + 38, scale=1.0, opacity=1.0)

    _bubble_cache[key] = bim
    return bim

def draw_birds_nest_bubbles(canvas_rgba, t):
    t_end = 63.10
    if t < 58.65 or t >= t_end:
        return
    # 4 floating crystal bubbles positioned around the central bird's nest (zero overlap!)
    specs = [
        (58.85, "TÁO ĐỎ",              "tao_do",     230, (255, 118, 112), 232.0,  475.0, 0.0),
        (59.82, "ĐÔNG TRÙNG\nHẠ THẢO", "dtht",       242, (255, 206,  92), 842.0,  475.0, 1.3),
        (61.12, "KỶ TỬ",               "ky_tu",      226, (255, 136, 102), 232.0, 1180.0, 2.5),
        (61.82, "01 HỘP\nĐƯỜNG PHÈN",  "duong_phen", 238, (185, 232, 255), 842.0, 1180.0, 3.7),
    ]
    u_out = quintic_smooth((t - (t_end - 0.42)) / 0.42) if t >= (t_end - 0.42) else 0.0
    op_out = 1.0 - u_out
    dy_out = -34.0 * u_out

    for t0, lbl, kind, diam, tint, bx, by, ph in specs:
        if t < t0:
            continue
        dt = t - t0
        u_in = min(1.0, dt / 0.44)
        sc = (0.25 + 0.75 * ease_out_back(u_in)) * (1.0 + 0.05 * u_out)
        op = ease_out_cubic(min(1.0, dt / 0.26)) * op_out
        rise_in = (1.0 - ease_out_cubic(u_in)) * 42.0
        bob_x = math.sin(dt * 2.3 + ph) * 6.0
        bob_y = math.cos(dt * 1.9 + ph) * 8.0
        sp = get_crystal_bubble_sprite(lbl, kind, diam, tint)
        paste_rgba_centered(canvas_rgba, sp, bx + bob_x, by + rise_in + bob_y + dy_out, scale=sc, opacity=op)

# ======================================================================
# 4. FLOATING CALLOUT PILLS (FOR MÓN 2 TWIN JARS & MÓN 3/4 WEIGHTS)
# ======================================================================
_pill_cache = {}
def get_luxury_callout_pill(txt, accent="gold"):
    k = (txt, accent)
    if k in _pill_cache:
        return _pill_cache[k]
    sp = render_2layer_grad_sprite(txt, F_MONT_BLK, 25, "gold" if accent == "gold" else "white", stroke_col=(18, 8, 6), stroke_w=4, shadow_alpha=60)
    pw, ph = sp.width + 48, 60
    im = Image.new("RGBA", (pw + 20, ph + 28), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bg_fill = (128, 16, 26, 228) if accent == "ruby" else (24, 58, 32, 228) if accent == "emerald" else (36, 20, 12, 228)
    border_c = (255, 214, 92, 248)
    d.rounded_rectangle([10, 8, 10 + pw, 8 + ph], radius=30, fill=bg_fill, outline=border_c, width=3)
    # Little downward pointer triangle
    cx = 10 + pw // 2
    d.polygon([(cx - 11, 8 + ph), (cx + 11, 8 + ph), (cx, 8 + ph + 13)], fill=border_c)
    paste_rgba_centered(im, sp, cx, 8 + ph * 0.5, scale=1.0, opacity=1.0)
    _pill_cache[k] = im
    return im

def draw_floating_callout(canvas_rgba, txt, accent, t, t0, t1, cx, cy):
    if t < t0 or t >= t1:
        return
    u_in = min(1.0, (t - t0) / 0.30)
    u_out = quintic_smooth((t - (t1 - 0.26)) / 0.26) if t >= (t1 - 0.26) else 0.0
    sc = (0.65 + 0.35 * ease_out_back(u_in)) * (1.0 - 0.08 * u_out)
    op = ease_out_cubic(u_in) * (1.0 - u_out)
    dy = (1.0 - ease_out_cubic(u_in)) * 18.0 - 12.0 * u_out + math.sin((t - t0) * 3.0) * 3.5
    pill = get_luxury_callout_pill(txt, accent)
    paste_rgba_centered(canvas_rgba, pill, cx, cy + dy, scale=sc, opacity=op)

# ======================================================================
# 5. TOP 2-TIER LUXURY BRAND HEADER & BOX-FREE EMPHASIZED SUBTITLES
# ======================================================================
_hdr_cache = {}
def get_header_t1_pill(t1_txt):
    if t1_txt in _hdr_cache:
        return _hdr_cache[t1_txt]
    sp = render_2layer_grad_sprite(t1_txt, F_MONT_BLK, 31, "gold", stroke_col=(24, 10, 6), stroke_w=5, shadow_alpha=80)
    pw, ph = min(1020, sp.width + 58), 64
    im = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, 8 + pw, 8 + ph], radius=32, fill=(38, 14, 16, 218), outline=(255, 212, 88, 240), width=3)
    sc_fit = min(1.0, (pw - 36) / max(1.0, sp.width))
    paste_rgba_centered(im, sp, 8 + pw * 0.5, 8 + ph * 0.5, scale=sc_fit, opacity=1.0)
    _hdr_cache[t1_txt] = im
    return im

def draw_top_headers(canvas_rgba, headers, t):
    for h in headers:
        s0, s1 = h["start"], h["end"]
        if s0 <= t < s1:
            u_in1 = min(1.0, (t - s0) / 0.32)
            u_out = quintic_smooth((t - (s1 - 0.30)) / 0.30) if t >= (s1 - 0.30) else 0.0
            op1 = ease_out_cubic(u_in1) * (1.0 - u_out)
            sc1 = 0.88 + 0.12 * ease_out_back(u_in1)
            dy1 = -(1.0 - ease_out_cubic(u_in1)) * 22.0 - 16.0 * u_out
            p1 = get_header_t1_pill(h["t1"])
            paste_rgba_centered(canvas_rgba, p1, 540.0, 122.0 + dy1, scale=sc1, opacity=op1)

            # Staggered Tier 2 (+0.22s!)
            if t >= s0 + 0.22 and h.get("t2"):
                u_in2 = min(1.0, (t - (s0 + 0.22)) / 0.30)
                op2 = ease_out_cubic(u_in2) * (1.0 - u_out)
                dy2 = (1.0 - ease_out_cubic(u_in2)) * 14.0 - 12.0 * u_out
                sp2 = render_2layer_grad_sprite(h["t2"], F_BE_XBOLD, 25, "white", stroke_col=(20, 10, 8), stroke_w=5, shadow_alpha=135)
                paste_rgba_centered(canvas_rgba, sp2, 540.0, 188.0 + dy2, scale=min(1.0, 980.0 / max(1.0, sp2.width)), opacity=op2)
            break

def split_line_into_emphasis_tokens(line_str, emph_list):
    """Splits a subtitle line into ordered chunks: [(chunk_text, emph_dict_or_None), ...]."""
    if not line_str:
        return []
    n = len(line_str)
    marks = [None] * n
    for em in emph_list:
        kw = em["text"]
        idx = line_str.lower().find(kw.lower())
        if idx >= 0:
            for k in range(idx, idx + len(kw)):
                marks[k] = em
    chunks = []
    cur_m = marks[0]
    s_i = 0
    for i in range(1, n):
        if marks[i] is not cur_m:
            chunks.append((line_str[s_i:i], cur_m))
            s_i = i
            cur_m = marks[i]
    chunks.append((line_str[s_i:n], cur_m))
    return chunks

def draw_upgraded_subtitles(canvas_rgba, subs, t):
    for sub in subs:
        s0, s1 = sub["start"], sub["end"]
        if not (s0 <= t < s1):
            continue
        # Phrase entrance & exit
        u_in = min(1.0, (t - s0) / 0.18)
        u_out = quintic_smooth((t - (s1 - 0.16)) / 0.16) if t >= (s1 - 0.16) else 0.0
        ph_op = ease_out_cubic(u_in) * (1.0 - u_out)
        ph_dy = (1.0 - ease_out_cubic(u_in)) * 18.0 - 10.0 * u_out
        ph_sc = 0.93 + 0.07 * ease_out_cubic(u_in)

        lines = [l for l in (sub["line1"], sub["line2"]) if l.strip()]
        base_ys = [1615.0] if len(lines) == 1 else [1575.0, 1652.0]

        for li, ln in enumerate(lines):
            chunks = split_line_into_emphasis_tokens(ln, sub["emphasis"])
            # Pre-render each chunk sprite & measure total line width
            rendered = []
            tot_w = 0.0
            for c_txt, em in chunks:
                if not c_txt:
                    continue
                lead_sp = 13.0 if c_txt.startswith(" ") else 0.0
                trail_sp = 13.0 if c_txt.endswith(" ") and len(c_txt.strip()) > 0 else 0.0
                core = c_txt.strip()
                if not core:
                    tot_w += 14.0
                    continue
                if em is None:
                    sp = render_2layer_grad_sprite(core, F_BE_XBOLD, 44, "white", stroke_col=(22, 11, 8), stroke_w=7, shadow_alpha=155)
                    dyn_sc = 1.0
                else:
                    st_mode = em["style"]
                    glow_c = (255, 196, 48) if st_mode == "gold" else (255, 68, 102)
                    sp = render_2layer_grad_sprite(core, F_MONT_BLK, 53, st_mode, stroke_col=(24, 10, 6), stroke_w=8, glow_col=glow_c, glow_rad=9, shadow_alpha=165)
                    # Dynamic elastic pop + specular sheen when word activates at t_pop!
                    dt_pop = t - em["t_pop"]
                    if dt_pop < 0.0:
                        dyn_sc = 0.96
                    elif dt_pop < 0.34:
                        # Elastic bounce 0.94 -> 1.15 -> 1.03!
                        p_u = dt_pop / 0.34
                        dyn_sc = 1.03 + 0.13 * math.sin(math.pi * p_u)
                        sp = apply_specular_sheen(sp, -0.2 + 1.4 * p_u)
                    else:
                        dyn_sc = 1.03
                        # Subtle secondary shimmer
                        if dt_pop < 1.10:
                            sp = apply_specular_sheen(sp, -0.2 + 1.4 * ((dt_pop - 0.34) / 0.76))
                # Account for sprite internal padding (~36px horizontal pad)
                vis_w = max(12.0, (sp.width - 34.0) * dyn_sc)
                tot_w += lead_sp + vis_w + trail_sp
                rendered.append((sp, dyn_sc, lead_sp, vis_w, trail_sp, em is not None))

            # Fit comfortably inside 1000px safe width
            line_fit = min(1.0, 990.0 / max(1.0, tot_w)) * ph_sc
            cur_x = 540.0 - (tot_w * line_fit) * 0.5
            cy_line = base_ys[li] + ph_dy

            # Draw normal chunks first, then emphasized chunks on top so glow/pop never clips!
            positions = []
            for sp, dyn_sc, lead_sp, vis_w, trail_sp, is_em in rendered:
                cur_x += lead_sp * line_fit
                cx_tok = cur_x + (vis_w * line_fit) * 0.5
                positions.append((sp, cx_tok, cy_line - (3.0 if is_em else 0.0), dyn_sc * line_fit, is_em))
                cur_x += (vis_w + trail_sp) * line_fit

            for sp, cx_t, cy_t, sc_t, is_em in positions:
                if not is_em:
                    paste_rgba_centered(canvas_rgba, sp, cx_t, cy_t, scale=sc_t, opacity=ph_op)
            for sp, cx_t, cy_t, sc_t, is_em in positions:
                if is_em:
                    paste_rgba_centered(canvas_rgba, sp, cx_t, cy_t, scale=sc_t, opacity=ph_op)
        break

# ======================================================================
# 6. LUXURY BRAND END-CARD (147.60s - 150.67s)
# ======================================================================
_endcard_base = None
def draw_brand_endcard(canvas_rgba, t):
    global _endcard_base
    if t < 147.60:
        return
    if _endcard_base is None:
        card = Image.new("RGBA", (960, 1080), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([20, 20, 940, 1060], radius=48, fill=(36, 10, 14, 236), outline=(255, 212, 92, 250), width=4)
        d.rounded_rectangle([36, 36, 924, 1044], radius=38, outline=(255, 212, 92, 95), width=2)

        s1 = render_2layer_grad_sprite("THỰC PHẨM F20", F_MONT_BLK, 56, "gold", stroke_col=(20, 8, 6), stroke_w=7)
        s2 = render_2layer_grad_sprite("× YẾN SÀO SKA NEST", F_PLAYFAIR, 42, "white", stroke_col=(20, 8, 6), stroke_w=6)
        s3 = render_2layer_grad_sprite("SET QUÀ TRI ÂN 20/11", F_MONT_BLK, 50, "ruby", stroke_col=(24, 8, 6), stroke_w=7, glow_col=(255, 80, 110), glow_rad=8)
        s4 = render_2layer_grad_sprite("Trực Tiếp Sản Xuất • Sang Trọng • Tận Tâm", F_BE_XBOLD, 28, "white", stroke_col=(18, 8, 6), stroke_w=5)
        s5 = render_2layer_grad_sprite("104+ Set Quà Giao Toàn Quốc Mỗi Ngày", F_BE_XBOLD, 27, "gold", stroke_col=(18, 8, 6), stroke_w=5)

        paste_rgba_centered(card, s1, 480, 175)
        paste_rgba_centered(card, s2, 480, 255)
        d.line([(160, 325), (800, 325)], fill=(255, 212, 92, 165), width=2)
        paste_rgba_centered(card, s3, 480, 415)
        paste_rgba_centered(card, s4, 480, 515)
        paste_rgba_centered(card, s5, 480, 580)

        # Golden CTA Button
        d.rounded_rectangle([110, 675, 850, 785], radius=55, fill=(214, 28, 42, 255), outline=(255, 224, 112, 255), width=4)
        s_cta = render_2layer_grad_sprite("INBOX ĐẶT HÀNG NGAY CHO OANH", F_MONT_BLK, 31, "gold", stroke_col=(24, 8, 6), stroke_w=5)
        paste_rgba_centered(card, s_cta, 480, 730)

        s_addr = render_2layer_grad_sprite("17/3 Điện Biên Phủ • P. Vĩnh Hòa • TP. Nha Trang", F_BE_XBOLD, 24, "white", stroke_col=(16, 8, 6), stroke_w=4)
        paste_rgba_centered(card, s_addr, 480, 885)
        s_hot  = render_2layer_grad_sprite("Cam Kết Chất Lượng & Giá Gốc Tận Xưởng", F_BE_XBOLD, 23, "gold", stroke_col=(16, 8, 6), stroke_w=4)
        paste_rgba_centered(card, s_hot, 480, 945)
        _endcard_base = card

    u = min(1.0, (t - 147.60) / 0.48)
    op = ease_out_cubic(u)
    sc = 0.88 + 0.12 * ease_out_back(u)
    # Darken background softly behind end-card
    dim = Image.new("RGBA", (W, H), (14, 6, 8, int(145 * op)))
    canvas_rgba.alpha_composite(dim)
    # Pulse CTA subtly
    pulse = 1.0 + 0.012 * math.sin((t - 147.60) * 5.0)
    paste_rgba_centered(canvas_rgba, _endcard_base, 540.0, 930.0 + (1.0 - ease_out_cubic(u)) * 40.0, scale=sc * pulse, opacity=op)

# ======================================================================
# 7. RHYTHM CAMERA ZOOM & STREAMING VIDEO CLIP DECODER
# ======================================================================
def eval_rhythm_zoom(t, zoom_beats):
    # Subtle continuous breathing + punchy zoom-in / zoom-out synced to spoken emphasis!
    z = 1.008 + 0.012 * (0.5 + 0.5 * math.sin(t * 0.75))
    for t0, tp, th_end, t1, pk in zoom_beats:
        if t0 <= t <= t1:
            if t < tp:
                u = ease_out_cubic((t - t0) / max(0.05, tp - t0))
                z = max(z, 1.01 + (pk - 1.01) * u)
            elif t <= th_end:
                z = max(z, pk)
            else:
                u = quintic_smooth((t - th_end) / max(0.05, t1 - th_end))
                z = max(z, pk + (1.012 - pk) * u)
    return z

class ClipFrameBank:
    """Loads compact 1080x1920 clips on demand with ping-pong loop so zero seam on long showcases!"""
    def __init__(self):
        self._loaded = {}

    def get_frame(self, path, local_t, speed=1.0, zoom=1.0, crop_flow_star=False):
        if path not in self._loaded:
            # Keep max 12 clips in RAM at once so sequential render decodes each clip ONLY ONCE!
            if len(self._loaded) >= 12:
                oldest = next(iter(self._loaded))
                del self._loaded[oldest]
            raw = subprocess.check_output([
                "ffmpeg", "-v", "error", "-i", path,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
            ])
            n_f = len(raw) // (W * H * 3)
            arr = np.frombuffer(raw[:n_f * W * H * 3], dtype=np.uint8).reshape((n_f, H, W, 3))
            self._loaded[path] = arr

        frames = self._loaded[path]
        n_f = len(frames)
        if n_f <= 1:
            im = Image.fromarray(frames[0], "RGB")
        else:
            f_pos = max(0.0, local_t * FPS * speed)
            # Ping-pong cycle (0 .. n_f-1 .. 0) so long 8-9s showcases NEVER hard-cut!
            cycle = 2 * (n_f - 1)
            m = int(round(f_pos)) % cycle
            idx = m if m < n_f else (cycle - m)
            im = Image.fromarray(frames[idx], "RGB")

        eff_z = max(zoom, 1.11) if crop_flow_star else zoom
        if abs(eff_z - 1.0) > 0.004:
            cw = int(round(W / eff_z))
            ch = int(round(H / eff_z))
            x0 = int(round((W - cw) * (0.35 if crop_flow_star else 0.50)))
            y0 = int(round((H - ch) * (0.18 if crop_flow_star else 0.38)))
            im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.Resampling.BILINEAR)
        return im

def build_visual_schedule(tl_data):
    """Returns ordered list of full-screen visual cuts covering 0.00s -> 150.67s (100% of speech splices covered!)"""
    VID_FLOW = os.path.join(V2_DIR, "flow_videos")
    BR_1117  = os.path.join(V2_DIR, "brolls_1117")
    BR_CAP   = os.path.join(OUT_ROOT, "capcut_media")

    def fv(name, fallback):
        p = os.path.join(VID_FLOW, f"{name}.mp4")
        return p if os.path.exists(p) else fallback

    v1_to_yen     = fv("OUT_f20_v1_full_to_yen",   os.path.join(BR_CAP, "showcase_01_yensao_ingredients.mp4"))
    v2_hai_rong   = fv("OUT_f20_v2_hai_rong_bien", os.path.join(BR_CAP, "broll_04_mica_sunlit.mp4"))
    v3_banh       = fv("OUT_f20_v3_banh_thuyen",   os.path.join(BR_CAP, "showcase_03_banhthuyen_250g.mp4"))
    v4_kep_hat    = fv("OUT_f20_v4_kep_hat",       os.path.join(BR_CAP, "showcase_04_rongbien_kephat_500g.mp4"))
    v5_skanest    = fv("OUT_f20_v5_skanest_box",   os.path.join(BR_CAP, "showcase_05_to_yen_cao_cap.mp4"))
    v6_gio_mica   = fv("OUT_f20_v6_gio_mica",      os.path.join(BR_CAP, "broll_04_mica_sunlit.mp4"))
    v7_anh_hau    = fv("OUT_f20_v7_anh_hau",       os.path.join(BR_CAP, "broll_12_handover_gift.mp4"))
    v8_showroom   = fv("OUT_f20_v8_showroom",      os.path.join(BR_1117, "br1117_03_wide_row.mp4"))

    # B-roll overlays (ordered non-overlapping intervals; anything outside uses the exact synced A-roll clip!)
    overlays = [
        # 1. Panoramic Opening Montage (0.00s - 4.20s)
        ( 0.00,  1.47, tl_data["intro_clips"][0]["path"], 1.00, 1.00, 1.05, "intro_wide_1"),
        ( 1.47,  2.87, tl_data["intro_clips"][1]["path"], 1.00, 1.05, 1.00, "intro_wide_2"),
        ( 2.87,  4.20, tl_data["intro_clips"][2]["path"], 1.00, 1.00, 1.06, "intro_wide_3"),
        # 2. Seg [02]: 104 set quà -> Anh Hậu 77 set -> Phụ huynh 13 set -> Hà Nội 10 set & TP.HCM 4 set (covers 26.07s splice!)
        ( 9.20, 13.35, os.path.join(BR_1117, "br1117_03_wide_row.mp4"),     0.90, 1.00, 1.06, "broll_2011_sets"),
        (16.10, 18.20, os.path.join(BR_CAP,  "broll_12_handover_gift.mp4"), 0.95, 1.00, 1.05, "broll_anh_hau_real"),
        (18.20, 20.15, v7_anh_hau,                                          0.90, 1.00, 1.05, "ai_anh_hau_77sets"),
        (22.10, 24.30, os.path.join(BR_1117, "br1117_01_ribbon_team.mp4"),  0.95, 1.00, 1.06, "broll_13sets_team"),
        (24.30, 28.85, os.path.join(BR_CAP,  "broll_10_factory_carton.mp4"),0.92, 1.00, 1.06, "broll_hanoi_carton_cutcover"),
        (28.85, 33.10, os.path.join(BR_CAP,  "broll_11_delivery_car.mp4"),  0.95, 1.05, 1.00, "broll_hcmc_suv"),
        # 3. Seg [02]->[03]->[04] (covers 38.10s & 42.40s splices!)
        (37.60, 40.50, v8_showroom,                                         0.88, 1.00, 1.05, "ai_showroom_104sets"),
        (40.50, 42.90, os.path.join(BR_1117, "br1117_08_arrange_sets.mp4"), 0.95, 1.04, 1.00, "broll_completed_sets"),
        # 4. Seg [04]->[05] Intro + ALL 4 PRODUCTS via Flow AI Videos! (covers 47.27s, 56.70s, 71.07s, 76.60s, 86.63s splices!)
        (46.80, 51.40, v6_gio_mica,                                         0.85, 1.00, 1.05, "flow_gio_mica_intro"),
        (51.40, 54.10, v5_skanest,                                          0.85, 1.00, 1.05, "flow_skanest_open"),
        (54.10, 63.10, v1_to_yen,                                           0.68, 1.00, 1.06, "flow_full_to_yen_bubbles"),
        (63.10, 71.15, v2_hai_rong,                                         0.72, 1.00, 1.06, "flow_hai_rong_bien"),
        (71.15, 76.75, v3_banh,                                             0.82, 1.00, 1.06, "flow_banh_thuyen_250g"),
        (76.75, 82.80, v4_kep_hat,                                          0.80, 1.00, 1.05, "flow_kep_hat_500g"),
        (82.80, 86.85, v4_kep_hat,                                          0.75, 1.12, 1.18, "flow_kep_hat_macro_24thanh"),
        # 5. Seg [06]: Giá trị nhất + Cẩm nang sử dụng yến sào (covers 93.87s, 103.80s, 106.53s splices!)
        (90.60, 95.60, v5_skanest,                                          0.82, 1.02, 1.08, "flow_skanest_hero"),
        (95.60,101.40, os.path.join(BR_CAP,  "broll_08_cam_nang_close.mp4"),0.92, 1.00, 1.06, "broll_cam_nang_blue"),
        (103.20,106.75,os.path.join(BR_1117, "br1117_06_bag_overhead.mp4"), 0.88, 1.00, 1.06, "broll_bag_overhead"),
        # 6. Seg [07]: Giỏ Mica + Quai Da Đỏ Đô + Hoa & Nơ Màu Be (covers 125.77s splice!)
        (110.80,114.60,os.path.join(BR_CAP,  "broll_04_mica_sunlit.mp4"),   0.90, 1.00, 1.06, "broll_mica_sunlit"),
        (114.60,118.60,os.path.join(BR_CAP,  "broll_05_quai_da_macro.mp4"), 0.85, 1.00, 1.07, "broll_quai_da_do_do"),
        (121.60,126.00,os.path.join(BR_CAP,  "broll_06_hoa_no_macro.mp4"),  0.85, 1.00, 1.07, "broll_hoa_no_mau_be"),
        # 7. Seg [08]: Trực tiếp sản xuất (covers 134.80s splice!)
        (129.60,132.40,os.path.join(BR_1117, "br1117_04_counter_pack.mp4"), 0.95, 1.00, 1.06, "broll_factory_counter"),
        (132.40,135.10,os.path.join(BR_CAP,  "broll_09_factory_pack1.mp4"), 0.95, 1.05, 1.00, "broll_factory_pack"),
        # 8. Seg [09] + Storefront + End-Card
        (140.40,144.60,os.path.join(BR_1117, "br1117_05_storefront.mp4"),   0.90, 1.00, 1.06, "broll_storefront_f20"),
        (147.60,150.70,os.path.join(BR_1117, "br1117_05_storefront.mp4"),   0.75, 1.06, 1.10, "endcard_backdrop"),
    ]
    return overlays

# Precomputed top/bottom soft vignette overlay for effortless text contrast without grey boxes!
_vig_overlay = None
def get_vignette_overlay():
    global _vig_overlay
    if _vig_overlay is None:
        yy = np.arange(H, dtype=np.float32)[:, None]
        top_a = np.clip((260.0 - yy) / 260.0, 0.0, 1.0) ** 1.6 * 88.0
        bot_a = np.clip((yy - 1340.0) / 580.0, 0.0, 1.0) ** 1.5 * 128.0
        alpha = np.broadcast_to(np.clip(top_a + bot_a, 0, 255).astype(np.uint8), (H, W))
        rgba = np.zeros((H, W, 4), dtype=np.uint8)
        rgba[:, :, 0] = 12; rgba[:, :, 1] = 6; rgba[:, :, 2] = 6
        rgba[:, :, 3] = alpha
        _vig_overlay = Image.fromarray(rgba, "RGBA")
    return _vig_overlay

def render_frame_at(t, tl_data, sub_plan, overlays, bank):
    # 1. Determine active visual clip (B-roll/Flow overlay or synced Chị Oanh A-roll!)
    bg_im = None
    for s0, s1, vp, spd, z0, z1, tag in overlays:
        if s0 <= t < s1:
            u = quintic_smooth((t - s0) / max(0.1, s1 - s0))
            z = z0 + (z1 - z0) * u
            # Also apply rhythm zoom pulse if on Anh Hậu / Showroom / Product punch!
            z_rhy = eval_rhythm_zoom(t, sub_plan["rhythm_zooms"])
            if z_rhy > 1.04 and "flow_hai_rong" not in tag and "flow_full_to_yen" not in tag:
                z = max(z, z_rhy)
            is_flow_gen = any(k in vp for k in ("OUT_f20_v1", "OUT_f20_v2", "OUT_f20_v3"))
            bg_im = bank.get_frame(vp, t - s0, speed=spd, zoom=z, crop_flow_star=is_flow_gen)
            if tag == "endcard_backdrop":
                bg_im = bg_im.filter(ImageFilter.GaussianBlur(radius=14))
            break

    if bg_im is None:
        # Synced Chị Oanh A-roll with Rhythm Camera Zoom!
        z_cam = eval_rhythm_zoom(t, sub_plan["rhythm_zooms"])
        for ac in tl_data["aroll_clips"]:
            if ac["start"] <= t < ac["end"] + 0.04:
                bg_im = bank.get_frame(ac["video_path"], max(0.0, t - ac["start"]), speed=1.0, zoom=z_cam)
                break
        if bg_im is None:
            bg_im = bank.get_frame(tl_data["aroll_clips"][-1]["video_path"], 0.0, speed=1.0, zoom=1.0)

    canvas = bg_im.convert("RGBA")
    canvas.alpha_composite(get_vignette_overlay())

    # 2. Top 2-Tier Brand Headers
    draw_top_headers(canvas, sub_plan["top_headers"], t)

    # 3. Special Overlays:
    # (A) Image 2 Upgrade: Full Bird's Nest + 4 Shimmering 3D Crystal Bubbles (58.85s - 63.10s)
    draw_birds_nest_bubbles(canvas, t)

    # (B) Image 3 Upgrade: Twin F20 Seaweed Jars Floating Callouts (ZERO overlapping cards!)
    draw_floating_callout(canvas, "01 HỘP SẤY GIÒN • VỊ CAY NHẸ",  "ruby",    t, 66.05, 68.68, 295.0, 625.0)
    draw_floating_callout(canvas, "01 HỘP SẤY MÈ • VỊ KHÔNG CAY", "emerald", t, 68.70, 71.08, 785.0, 625.0)

    # (C) Món 3 & Món 4 Weight / Quantity Callouts
    draw_floating_callout(canvas, "GÓI TIỆN LỢI 250G",              "gold",    t, 73.20, 76.60, 540.0, 515.0)
    draw_floating_callout(canvas, "GÓI LỚN 500G • 22–24 THANH HẠT", "gold",    t, 82.85, 86.70, 540.0, 490.0)

    # 4. Upgraded Box-Free Emphasized Subtitles
    draw_upgraded_subtitles(canvas, sub_plan["subtitles"], t)

    # 5. Luxury Brand End-Card (147.60s - 150.67s)
    draw_brand_endcard(canvas, t)

    return canvas.convert("RGB")

def main():
    tl_data  = json.load(open(os.path.join(V2_DIR, "timeline_1117_master.json"), encoding="utf-8"))
    sub_plan = json.load(open(os.path.join(V2_DIR, "subtitles_v2_plan.json"), encoding="utf-8"))
    overlays = build_visual_schedule(tl_data)
    bank     = ClipFrameBank()

    # Save visual schedule JSON so step4 CapCut Draft builder mirrors 100% of cuts & keyframes!
    json.dump({"overlays": overlays}, open(os.path.join(V2_DIR, "visual_schedule_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    if "--test" in sys.argv:
        test_ts = [0.80, 6.10, 19.05, 27.50, 36.10, 39.20, 48.50, 52.60,
                   59.40, 62.25, 67.40, 69.80, 74.50, 84.50, 116.80, 149.20]
        cols, rows = 4, 4
        tw, th = 270, 480
        grid = Image.new("RGB", (cols * tw, rows * th))
        t0 = time.time()
        for i, ts in enumerate(test_ts):
            im = render_frame_at(ts, tl_data, sub_plan, overlays, bank)
            # Save full-res key QA frames for Image 2 & Image 3 & Subtitles!
            if ts in (62.25, 67.40, 69.80, 6.10, 149.20):
                im.save(os.path.join(V2_DIR, f"qa_full_{ts:.2f}s.jpg"), quality=94)
            thumb = im.resize((tw, th), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(thumb)
            d.rectangle([4, 4, 110, 26], fill=(0, 0, 0))
            d.text((8, 8), f"t={ts:.2f}s", fill=(255, 230, 0))
            grid.paste(thumb, ((i % cols) * tw, (i // cols) * th))
        out_grid = os.path.join(V2_DIR, "v2_test_grid_16.jpg")
        grid.save(out_grid, quality=92)
        print(f"Rendered 16-frame test grid in {time.time()-t0:.1f}s -> {out_grid}")
        return

    total_frames = tl_data["total_frames"]
    out_raw_vid  = os.path.join(V2_DIR, "_f20_v2_video_only.mp4")
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
        out_raw_vid
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f_idx in range(total_frames):
        t = f_idx / float(FPS)
        im = render_frame_at(t, tl_data, sub_plan, overlays, bank)
        proc.stdin.write(im.tobytes())
        if (f_idx + 1) % 300 == 0 or f_idx == total_frames - 1:
            el = time.time() - t0
            fps_now = (f_idx + 1) / max(0.1, el)
            print(f"  Rendered {f_idx+1}/{total_frames} frames ({100*(f_idx+1)/total_frames:.1f}%) | {fps_now:.1f} fps", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg exited with {rc}")
    print(f"DONE! Saved {out_raw_vid} in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
