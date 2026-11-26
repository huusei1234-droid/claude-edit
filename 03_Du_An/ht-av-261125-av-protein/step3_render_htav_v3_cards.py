import concurrent.futures, json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
from safe_zone_9x16 import is_box_safe_9x16

PROJ_DIR   = r"C:\AI\full studio\output\ht-av-261125"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
CUTOUT_DIR = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\assets_cutouts_v2"
FONTS_DIR  = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
TOTAL_FRAMES = 1487  # 49.567s

FONT_TITLE  = os.path.join(FONTS_DIR, "Oswald-Bold.ttf")
FONT_BLACK  = os.path.join(FONTS_DIR, "AsapCondensed-Black.ttf")
FONT_EBOLD  = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_BOLD   = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")
FONT_SERIF  = os.path.join(FONTS_DIR, "PlayfairDisplay-BoldItalic.ttf")
FONT_SCRIPT = os.path.join(FONTS_DIR, "DancingScript-Bold.ttf")

# Safe-zone constants (TikTok x Reels 9:16 strict bounds)
# Upper half (Y = 250..860): X in [54..1024]
# Lower half (Y = 860..1545): X in [54..884] -> safe lower center X = 469!
SAFE_LOW_CX = 468

_font_cache = {}
def get_font(path, size):
    k = (path, max(10, int(round(size))))
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, k[1])
    return _font_cache[k]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def smoothstep(u):
    u = clamp01(u)
    return u * u * (3.0 - 2.0 * u)

def quintic(u):
    u = clamp01(u)
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

def ease_out_cubic(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 3.0

def ease_out_back(u, overshoot=1.10):
    u = clamp01(u) - 1.0
    return 1.0 + u * u * ((overshoot + 1.0) * u + overshoot)

def smooth_in_out_env(t, t0, t1, d_in=0.36, d_out=0.32):
    if t <= t0 or t >= t1:
        return 0.0
    a_in = quintic((t - t0) / max(0.05, d_in)) if (t - t0) < d_in else 1.0
    a_out = quintic((t1 - t) / max(0.05, d_out)) if (t1 - t) < d_out else 1.0
    return min(a_in, a_out)

def fit_cover(rgb_arr, target_w, target_h, zoom=1.0):
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    nw = max(target_w, int(round(sw * base_scale)))
    nh = max(target_h, int(round(sh * base_scale)))
    im = Image.fromarray(rgb_arr, "RGB").resize((nw, nh), Image.Resampling.BICUBIC)
    x0 = (nw - target_w) // 2
    y0 = (nh - target_h) // 2
    return im.crop((x0, y0, x0 + target_w, y0 + target_h))

def _build_stage_canvas():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1.0 - 0.52 * (((xx - 540.0) / 660.0) ** 2 + ((yy - 920.0) / 1120.0) ** 2), 0.30, 1.0)
    # Rich An Vuong Emerald-Obsidian Luxury Card Table Backdrop
    bbg = np.zeros((H, W, 3), dtype=np.uint8)
    bbg[:, :, 0] = (14 * vig).astype(np.uint8)
    bbg[:, :, 1] = (34 * vig).astype(np.uint8)
    bbg[:, :, 2] = (26 * vig).astype(np.uint8)
    im = Image.fromarray(bbg, "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    # Subtle gold filigree card-table arcs
    d.ellipse([540 - 620, 880 - 620, 540 + 620, 880 + 620], outline=(245, 208, 115, 28), width=2)
    d.ellipse([540 - 460, 880 - 460, 540 + 460, 880 + 460], outline=(82, 214, 158, 24), width=2)
    # Corner ambient warm glow
    fl = np.exp(-((xx / 380.0) ** 2 + (yy / 420.0) ** 2)) + np.exp(-(((W - xx) / 380.0) ** 2 + (yy / 420.0) ** 2))
    fl_rgba = np.zeros((H, W, 4), dtype=np.uint8)
    fl_rgba[:, :, 0] = 255; fl_rgba[:, :, 1] = 232; fl_rgba[:, :, 2] = 175
    fl_rgba[:, :, 3] = np.clip(fl * 65.0, 0, 90).astype(np.uint8)
    return Image.alpha_composite(im, Image.fromarray(fl_rgba, "RGBA")), Image.fromarray(fl_rgba, "RGBA")

STAGE_BG_IM, RINGS_FLARE_IM = _build_stage_canvas()

_sprite_cache = {}
def render_glow_text_sprite(text, font_path, size, top_col, bot_col=None, glow_col=None, glow_rad=12, stroke_col=None, stroke_w=0):
    bot_col = bot_col or top_col
    glow_col = glow_col or top_col
    key = (text, font_path, int(round(size)), top_col, bot_col, glow_col, glow_rad, stroke_col, stroke_w)
    if key in _sprite_cache:
        return _sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(glow_rad * 2.6 + stroke_w + 14)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    mask_im = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), text, font=font, fill=255)
    arr_m = np.array(mask_im, dtype=np.float32) / 255.0
    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)[:, None]
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.uint8)
    for c in range(3):
        grad_rgb[:, :, c] = np.clip(top_col[c] * (1.0 - yy) + bot_col[c] * yy, 0, 255).astype(np.uint8)
    fill_im = Image.fromarray(np.dstack([grad_rgb, (arr_m * 255.0).astype(np.uint8)]), "RGBA")

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    if glow_rad > 0:
        g1_a = mask_im.filter(ImageFilter.GaussianBlur(radius=glow_rad * 0.75))
        g2_a = mask_im.filter(ImageFilter.GaussianBlur(radius=glow_rad * 1.85))
        g_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
        g_arr[:, :, 0] = glow_col[0]; g_arr[:, :, 1] = glow_col[1]; g_arr[:, :, 2] = glow_col[2]
        g_arr[:, :, 3] = np.clip(np.array(g1_a, dtype=np.float32) * 0.62 + np.array(g2_a, dtype=np.float32) * 0.38, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(g_arr, "RGBA"))

    sh_a = mask_im.filter(ImageFilter.GaussianBlur(radius=5))
    sh_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
    sh_arr[:, :, 3] = (np.array(sh_a, dtype=np.float32) * 0.78).astype(np.uint8)
    sh_im.paste(Image.fromarray(sh_arr, "RGBA"), (3, 5))
    base = Image.alpha_composite(base, sh_im)

    if stroke_w > 0 and stroke_col is not None:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        base = Image.alpha_composite(base, st_im)

    base = Image.alpha_composite(base, fill_im)
    if len(_sprite_cache) > 700:
        _sprite_cache.clear()
    _sprite_cache[key] = base
    return base

def paste_centered(canvas_im, sprite_im, cx, cy, scale_x=1.0, scale_y=None, opacity=1.0, angle=0.0, blur_px=0.0, sweep_prog=None):
    if scale_y is None:
        scale_y = scale_x
    if opacity <= 0.01 or scale_x <= 0.02 or scale_y <= 0.02:
        return
    im = sprite_im
    if sweep_prog is not None and -0.1 <= sweep_prog <= 1.1:
        arr = np.array(im).copy()
        sh, sw = arr.shape[:2]
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        diag = (xx + yy * 0.42) / max(1.0, (sw + sh * 0.42))
        band = np.exp(-((diag - sweep_prog) / 0.085) ** 2)
        af = arr[:, :, 3:4].astype(np.float32) / 255.0
        arr[:, :, :3] = np.clip(arr[:, :, :3].astype(np.float32) + 155.0 * band[:, :, None] * af, 0, 255).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    if abs(scale_x - 1.0) > 0.006 or abs(scale_y - 1.0) > 0.006:
        nw = max(3, int(round(im.width * scale_x)))
        nh = max(3, int(round(im.height * scale_y)))
        im = im.resize((nw, nh), Image.Resampling.BICUBIC)
    if abs(angle) > 0.12:
        im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    if blur_px >= 0.5:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(14.0, blur_px)))
    if opacity < 0.995:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    dx = int(round(cx - im.width / 2.0))
    dy = int(round(cy - im.height / 2.0))
    x0, y0 = max(0, dx), max(0, dy)
    x1, y1 = min(canvas_im.width, dx + im.width), min(canvas_im.height, dy + im.height)
    if x1 > x0 and y1 > y0:
        canvas_im.alpha_composite(im.crop((x0 - dx, y0 - dy, x1 - dx, y1 - dy)), dest=(x0, y0))

# ======================================================================
# VECTOR SUIT SYMBOLS & LUXURY PLAYING-CARD GENERATOR (5 CARD STYLES!)
# ======================================================================
def draw_suit_icon(draw, suit, cx, cy, r, col):
    if suit == "diamond":
        draw.polygon([(cx, cy - r), (cx + r * 0.78, cy), (cx, cy + r), (cx - r * 0.78, cy)], fill=col)
    elif suit == "star":
        pts = []
        for i in range(8):
            rr = r if i % 2 == 0 else r * 0.40
            a = math.radians(i * 45 - 90)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        draw.polygon(pts, fill=col)
    elif suit == "bolt":
        pts = [(cx + r*0.15, cy - r), (cx - r*0.55, cy + r*0.08), (cx - r*0.05, cy + r*0.08),
               (cx - r*0.22, cy + r), (cx + r*0.55, cy - r*0.10), (cx + r*0.05, cy - r*0.10)]
        draw.polygon(pts, fill=col)
    else:  # leaf / emerald emblem
        draw.ellipse([cx - r*0.65, cy - r*0.85, cx + r*0.65, cy + r*0.55], fill=col)
        draw.rectangle([cx - max(1, int(r*0.14)), cy + r*0.25, cx + max(1, int(r*0.14)), cy + r], fill=col)

_card_cache = {}
def make_luxury_playing_card(w, h, rank_txt, suit, theme, title_txt, sub_txt, badge_txt=None, big_val=None):
    """
    Creates an ornate collector Playing Card (Ivory-Gold, Crimson-Warning, or Royal-Emerald-Gold)
    with corner rank+suit indices, double filigree frame, and crisp Vietnamese typography!
    """
    key = (w, h, rank_txt, suit, theme, title_txt, sub_txt, badge_txt, big_val)
    if key in _card_cache:
        return _card_cache[key]

    pad = 22
    cw, ch = w + pad * 2, h + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    # Soft physical drop-shadow
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 2, pad + 12, pad + w + 2, pad + h + 12], radius=30, fill=(6, 14, 12, 165))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=11)))

    d = ImageDraw.Draw(card)
    if theme == "crimson":
        bg_fill   = (255, 246, 247, 252)
        rim_outer = (225,  58,  76, 255)
        rim_inner = (244, 165, 175, 210)
        acc_col   = (202,  28,  52, 255)
        txt_col   = ( 28,  18,  24, 255)
        sub_col   = (118,  42,  54, 255)
    elif theme == "gold_ace":
        bg_fill   = ( 16,  48,  36, 252)
        rim_outer = (255, 214,  92, 255)
        rim_inner = (232, 176,  56, 210)
        acc_col   = (255, 222, 102, 255)
        txt_col   = (255, 252, 240, 255)
        sub_col   = (168, 242, 208, 255)
    elif theme == "emerald":
        bg_fill   = (244, 253, 248, 252)
        rim_outer = ( 18, 152,  98, 255)
        rim_inner = (134, 224, 184, 220)
        acc_col   = ( 12, 128,  82, 255)
        txt_col   = ( 16,  32,  26, 255)
        sub_col   = ( 42,  96,  74, 255)
    else:  # ivory_gold
        bg_fill   = (255, 252, 244, 252)
        rim_outer = (224, 168,  48, 255)
        rim_inner = (242, 212, 138, 220)
        acc_col   = (188, 122,  14, 255)
        txt_col   = ( 22,  24,  30, 255)
        sub_col   = ( 86,  72,  48, 255)

    x0, y0, x1, y1 = pad, pad, pad + w - 1, pad + h - 1
    d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=bg_fill, outline=(255, 255, 255, 255), width=4)
    d.rounded_rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], radius=24, outline=rim_outer, width=3)
    d.rounded_rectangle([x0 + 11, y0 + 11, x1 - 11, y1 - 11], radius=19, outline=rim_inner, width=2)

    # Top-left & Bottom-right Playing-Card Corner Indices
    f_rk = get_font(FONT_BLACK, max(20, int(h * 0.095)))
    d.text((x0 + 18, y0 + 13), rank_txt, font=f_rk, fill=acc_col)
    draw_suit_icon(d, suit, x0 + 27, y0 + 18 + int(h * 0.115), max(7, int(h * 0.036)), acc_col)
    draw_suit_icon(d, suit, x1 - 27, y1 - 22, max(7, int(h * 0.036)), acc_col)

    cx_c = pad + w * 0.5
    cur_y = y0 + int(h * 0.20)

    if badge_txt:
        fb = get_font(FONT_BOLD, max(16, int(h * 0.068)))
        bb = d.textbbox((0, 0), badge_txt, font=fb)
        bw, bh = (bb[2] - bb[0]) + 26, (bb[3] - bb[1]) + 12
        d.rounded_rectangle([cx_c - bw*0.5, cur_y - bh*0.5, cx_c + bw*0.5, cur_y + bh*0.5], radius=bh//2, fill=acc_col)
        pill_fg = (16, 36, 26, 255) if theme == "gold_ace" else (255, 255, 255, 255)
        d.text((cx_c - (bb[2]-bb[0])*0.5 - bb[0], cur_y - (bb[1]+bb[3])*0.5), badge_txt, font=fb, fill=pill_fg)
        cur_y += bh * 0.5 + int(h * 0.11)

    if big_val:
        fv = get_font(FONT_BLACK, max(30, int(h * 0.19)))
        # Auto fit width
        while fv.size > 22 and (d.textbbox((0, 0), big_val, font=fv)[2] > w - 44):
            fv = get_font(FONT_BLACK, fv.size - 3)
        bv = d.textbbox((0, 0), big_val, font=fv)
        d.text((cx_c - (bv[2]-bv[0])*0.5 - bv[0], cur_y - (bv[1]+bv[3])*0.5), big_val, font=fv, fill=acc_col)
        cur_y += (bv[3] - bv[1]) * 0.5 + int(h * 0.13)

    # Multi-line Main Title (bold, high-contrast mobile readability!)
    title_base_sz = max(24, int(h * 0.135)) if not big_val else max(21, int(h * 0.105))
    for line_t in title_txt.split("\n"):
        ft = get_font(FONT_EBOLD, title_base_sz)
        while ft.size > 17 and (d.textbbox((0, 0), line_t, font=ft)[2] > w - 34):
            ft = get_font(FONT_EBOLD, ft.size - 2)
        bt = d.textbbox((0, 0), line_t, font=ft)
        d.text((cx_c - (bt[2]-bt[0])*0.5 - bt[0], cur_y - (bt[1]+bt[3])*0.5), line_t, font=ft, fill=txt_col)
        cur_y += (bt[3] - bt[1]) + 8

    if sub_txt:
        cur_y += 5
        sub_base_sz = max(18, int(h * 0.088)) if not big_val else max(16, int(h * 0.072))
        for line_s in sub_txt.split("\n"):
            fs = get_font(FONT_BOLD, sub_base_sz)
            while fs.size > 14 and (d.textbbox((0, 0), line_s, font=fs)[2] > w - 34):
                fs = get_font(FONT_BOLD, fs.size - 2)
            bs = d.textbbox((0, 0), line_s, font=fs)
            d.text((cx_c - (bs[2]-bs[0])*0.5 - bs[0], cur_y - (bs[1]+bs[3])*0.5), line_s, font=fs, fill=sub_col)
            cur_y += (bs[3] - bs[1]) + 5

    _card_cache[key] = card
    return card

def make_card_back(w, h):
    """Ornate An Vuong Emerald & Gold Foil Playing-Card Back for 3D 180-deg Card Flip!"""
    key = ("BACK", w, h)
    if key in _card_cache:
        return _card_cache[key]
    pad = 22
    cw, ch = w + pad * 2, h + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 2, pad + 12, pad + w + 2, pad + h + 12], radius=30, fill=(6, 14, 12, 165))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=11)))

    d = ImageDraw.Draw(card)
    x0, y0, x1, y1 = pad, pad, pad + w - 1, pad + h - 1
    d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=(14, 52, 38, 255), outline=(255, 232, 152, 255), width=5)
    d.rounded_rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], radius=20, outline=(232, 182, 72, 235), width=3)
    # Diamond lattice filigree on card back
    step = 28
    for gx in range(x0 + 24, x1 - 20, step):
        for gy in range(y0 + 24, y1 - 20, step):
            draw_suit_icon(d, "diamond", gx, gy, 5, (245, 204, 98, 72))
    cx_c, cy_c = pad + w * 0.5, pad + h * 0.5
    d.ellipse([cx_c - 64, cy_c - 64, cx_c + 64, cy_c + 64], fill=(10, 38, 28, 255), outline=(255, 216, 102, 255), width=4)
    draw_suit_icon(d, "star", cx_c, cy_c - 12, 24, (255, 222, 110, 255))
    fb = get_font(FONT_BLACK, 24)
    bb = d.textbbox((0, 0), "AV PROTEIN", font=fb)
    d.text((cx_c - (bb[2]-bb[0])*0.5 - bb[0], cy_c + 22), "AV PROTEIN", font=fb, fill=(255, 236, 168, 255))
    _card_cache[key] = card
    return card

def make_video_playing_card(vf_rgb, w, h, rank_txt, suit, theme, top_pill_txt, footer_txt, zoom=1.03):
    """Large Illustrated Video Playing Card (frames live AI B-Roll inside an ornate playing card!)."""
    pad = 24
    cw, ch = w + pad * 2, h + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 2, pad + 14, pad + w + 2, pad + h + 14], radius=34, fill=(4, 10, 8, 185))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=13)))

    is_warn = (theme == "crimson")
    bg_c    = (255, 248, 248, 255) if is_warn else (250, 254, 251, 255)
    rim_c   = (224,  54,  72, 255) if is_warn else (238, 188,  68, 255)
    acc_c   = (198,  26,  48, 255) if is_warn else ( 14, 126,  80, 255)

    d = ImageDraw.Draw(card)
    x0, y0, x1, y1 = pad, pad, pad + w - 1, pad + h - 1
    d.rounded_rectangle([x0, y0, x1, y1], radius=32, fill=bg_c, outline=(255, 255, 255, 255), width=5)
    d.rounded_rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], radius=27, outline=rim_c, width=3)

    # Top bar inside card: Corner Rank + Suit + Pill Header
    f_rk = get_font(FONT_BLACK, 30)
    d.text((x0 + 20, y0 + 14), rank_txt, font=f_rk, fill=acc_c)
    draw_suit_icon(d, suit, x0 + 68, y0 + 31, 11, acc_c)

    fp = get_font(FONT_EBOLD, 22)
    bp = d.textbbox((0, 0), top_pill_txt, font=fp)
    pw = (bp[2] - bp[0]) + 32
    d.rounded_rectangle([x1 - 18 - pw, y0 + 13, x1 - 18, y0 + 51], radius=19, fill=acc_c)
    d.text((x1 - 18 - pw + 16 - bp[0], y0 + 32 - (bp[1] + bp[3]) * 0.5), top_pill_txt, font=fp, fill=(255, 255, 255, 255))

    # Framed live video window inside card
    vx, vy = x0 + 16, y0 + 60
    vw, vh = w - 32, h - 128
    vis = fit_cover(vf_rgb, vw, vh, zoom=zoom).convert("RGBA")
    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=20, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(vis, (vx, vy), mask=vmask)
    card = Image.alpha_composite(card, vl)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([vx, vy, vx + vw - 1, vy + vh - 1], radius=20, outline=rim_c, width=2)

    # Footer caption inside playing card
    ff = get_font(FONT_EBOLD, 25)
    while ff.size > 18 and (d.textbbox((0, 0), footer_txt, font=ff)[2] > w - 42):
        ff = get_font(FONT_EBOLD, ff.size - 2)
    bf = d.textbbox((0, 0), footer_txt, font=ff)
    fy = y1 - 34
    d.text((pad + w * 0.5 - (bf[2] - bf[0]) * 0.5 - bf[0], fy - (bf[1] + bf[3]) * 0.5), footer_txt, font=ff, fill=(20, 24, 28, 255))
    return card

def draw_landing_ripple(canvas_im, cx, cy, dt, dur=0.28, rx_max=150, ry_max=28, col=(255, 220, 110)):
    if dt < 0.0 or dt > dur:
        return
    u = quintic(dt / dur)
    rx = int(rx_max * (0.28 + 0.85 * u))
    ry = int(ry_max * (0.28 + 0.72 * u))
    al = int(220 * (1.0 - u))
    if al > 5 and rx > 8 and ry > 4:
        rp = Image.new("RGBA", (rx * 2 + 16, ry * 2 + 16), (0, 0, 0, 0))
        ImageDraw.Draw(rp).ellipse([8, 8, rx * 2 + 8, ry * 2 + 8], outline=(*col, al), width=3)
        paste_centered(canvas_im, rp, cx, cy)

def draw_orbital_rings_bg(canvas_im, prod_thumb, t_now, t0, t1):
    env = smooth_in_out_env(t_now, t0, t1, d_in=0.45, d_out=0.40)
    if env <= 0.01:
        return
    dt = t_now - t0
    dur = max(0.2, t1 - t0)
    sc = 0.92 + 0.08 * ease_out_cubic(min(1.0, dt / 0.50))
    rot_deg = 36.0 * (dt / dur)
    cx, cy = 540, 660

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    R1, R2 = int(495 * sc), int(380 * sc)
    dr.ellipse([cx - R1, cy - R1, cx + R1, cy + R1], outline=(165, 248, 210, int(150 * env)), width=3)
    dr.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=(255, 220, 120, int(105 * env)), width=2)

    suits = ["leaf", "star", "diamond", "bolt", "leaf"]
    for i, st_s in enumerate(suits):
        a_rad = math.radians(-162.0 + i * (144.0 / 4.0) + rot_deg * 0.65)
        ix, iy = cx + int(R1 * math.cos(a_rad)), cy + int(R1 * math.sin(a_rad))
        dr.ellipse([ix - 34, iy - 34, ix + 34, iy + 34], fill=(16, 48, 36, int(225 * env)), outline=(255, 224, 122, int(210 * env)), width=3)
        draw_suit_icon(dr, st_s, ix, iy, 15, (255, 224, 118, int(235 * env)))

    if env > 0.18:
        fl_arr = np.array(RINGS_FLARE_IM)
        fl_arr[:, :, 3] = (fl_arr[:, :, 3].astype(np.float32) * env).astype(np.uint8)
        layer = Image.alpha_composite(layer, Image.fromarray(fl_arr, "RGBA"))
    canvas_im.alpha_composite(layer)

# ======================================================================
# CAMERA ZOOM & TALKING-HEAD-V3 ANIMATION DIM WINDOWS
# ======================================================================
ZOOM_KEYS = [
    ( 0.00, 1.00),
    ( 2.82, 1.06),  # Hook emphasis "mà 10 giờ đã buồn ngủ rũ rượi!"
    ( 5.10, 1.02),
    (13.10, 1.05),
    (16.15, 1.09),  # "nó đang KHÁT ĐẠM SẠCH!"
    (19.10, 1.02),  # Cut #1 reset cleanly -> "Thay vì nhịn sáng..."
    (23.30, 1.05),  # Holding real AV Protein box + 2 sticks!
    (27.00, 1.07),  # "22,05g đạm thực vật"
    (37.38, 1.06),  # Return from Full-Screen Riffle Stage -> "nhẹ bụng mà no êm tới trưa!"
    (39.67, 1.02),  # Cut #3 reset -> "Gửi ngay video này cho đồng nghiệp..."
    (43.77, 1.08),  # Cut #4 -> "Muốn nhận thực đơn bữa sáng 30 giây đủ đạm..."
    (49.56, 1.04),
]

def get_smooth_zoom(t):
    if t <= ZOOM_KEYS[0][0]:
        return ZOOM_KEYS[0][1]
    for i in range(len(ZOOM_KEYS) - 1):
        t0, z0 = ZOOM_KEYS[i]
        t1, z1 = ZOOM_KEYS[i + 1]
        if t0 <= t <= t1:
            span = max(0.08, min(0.55, (t1 - t0) * 0.45))
            u = smoothstep((t - t0) / span)
            return z0 + (z1 - z0) * u
    return ZOOM_KEYS[-1][1]

ANIM_DIM_WINDOWS = [
    ( 0.04,  4.92),  # Hook + 3-Card Overhead Arc Deal
    ( 5.15,  6.65),  # "CẢNH BÁO 1"
    (14.90, 19.06),  # "KHÁT ĐẠM SẠCH" + 3-Card Hand Fan
    (19.14, 31.52),  # "GIẢI PHÁP 2" + Orbital Rings + "22,05G ĐẠM SẠCH" + 3D Flip Card
    (37.40, 39.62),  # "NO ÊM TỚI TRƯA"
    (43.80, 46.66),  # Orbital Rings + "THỰC ĐƠN 30 GIÂY"
]

def get_bg_dim(t):
    v = 0.0
    for w0, w1 in ANIM_DIM_WINDOWS:
        v = max(v, smooth_in_out_env(t, w0, w1, d_in=0.42, d_out=0.38))
    return v

# ======================================================================
# SUBTITLES (100% FACE-SAFE, BOX-SAFE & TIKTOK/REELS SAFE ZONE!)
# ======================================================================
def load_captions_htav():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut_clean.json"), encoding="utf-8"))
    # Skip word subtitles during Hook multi-font title (0..4.92s) and Full-Screen Card Deck stages
    skip_spans = [
        ( 0.00,  4.94),
        ( 6.68, 13.06),
        (31.54, 37.34),
        (46.68, 49.60),
    ]
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if not any(a <= (w["start"] + w["end"]) * 0.5 <= b for a, b in skip_spans)
    ]

    groups, cur, line = [], [], []
    def flush_line():
        nonlocal line
        if line:
            cur.append(line); line = []
    def flush_group():
        nonlocal cur
        flush_line()
        if cur:
            groups.append(cur); cur = []

    prev = None
    for w in words:
        txt = w["word"].strip()
        if not txt:
            continue
        if prev is not None and (w["start"] - prev["end"]) >= 0.36:
            flush_group()
        if line and (len(line) >= 4 or sum(len(x[0]) + 1 for x in line) + len(txt) > 18):
            flush_line()
        if len(cur) >= 2 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!:;]$", txt):
            flush_group()
    flush_group()

    GOLD_W = {"30", "giây,", "giây", "2", "AV", "Protein", "22,05g", "1.632mg", "L-Leucine", "10", "PROTEIN"}
    EMER_W = {"đạm", "sạch,", "năng", "lượng", "nuôi", "cơ!", "đậu", "Hà", "Lan", "gạo,", "no", "êm", "trưa!"}
    ROSE_W = {"tinh", "bột,", "nhịn", "ăn", "đại", "ngáp", "dài"}
    STROKE_W = {"Protein", "22,05g", "sạch,", "trưa!", "10"}

    cap_groups = []
    for i, g in enumerate(groups):
        t0 = g[0][0][1]
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else 46.65
        t1 = min(nxt, last_end + 0.42) if (nxt - last_end) > 0.50 else nxt
        # Clamp before full-screen stages
        for sa, sb in skip_spans:
            if t0 < sa < t1:
                t1 = sa
        if t1 > t0 + 0.12:
            cap_groups.append({"t0": t0, "t1": t1, "lines": g})
    return cap_groups, GOLD_W, EMER_W, ROSE_W, STROKE_W

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

def sample_clip_pingpong(arr_list, t_rel, rate=1.0):
    if not arr_list:
        return np.zeros((540, 960, 3), dtype=np.uint8)
    n = len(arr_list)
    if n == 1:
        return arr_list[0]
    pos = t_rel * FPS * rate
    cyc = 2 * (n - 1)
    m = pos % cyc
    if m > (n - 1):
        m = cyc - m
    i0 = int(math.floor(m))
    i1 = min(n - 1, i0 + 1)
    f = m - i0
    return arr_list[i0] if f < 0.02 else np.clip(arr_list[i0].astype(np.float32)*(1.0-f) + arr_list[i1].astype(np.float32)*f, 0, 255).astype(np.uint8)

def load_static_assets():
    p_a = Image.open(os.path.join(CUTOUT_DIR, "av01_protein_a.png")).convert("RGBA")
    p_b = Image.open(os.path.join(CUTOUT_DIR, "av01_protein_b.png")).convert("RGBA")
    lg  = Image.open(os.path.join(CUTOUT_DIR, "logo_an_vuong_on_dark.png")).convert("RGBA")
    p_a.thumbnail((420, 520), Image.Resampling.LANCZOS)
    p_b.thumbnail((420, 520), Image.Resampling.LANCZOS)
    lg.thumbnail((250, 120), Image.Resampling.LANCZOS)
    return {"box_a": p_a, "box_b": p_b, "logo_dark": lg}

# Precomputed foreground desk + real AV Protein box protection grid (keep real desk & box bright when bg dims!)
_YY_G, _XX_G = np.ogrid[0:H, 0:W]
_DESK_LINE = np.clip((np.arange(H, dtype=np.float32) - 1600.0) / 55.0, 0.0, 1.0)[:, None]
_DESK_BOX  = np.exp(-((np.maximum(0.0, np.abs(_XX_G - 650.0) - 250.0)) / 46.0) ** 2) * \
             np.clip((_YY_G - 1290.0) / 50.0, 0.0, 1.0) * np.clip((1780.0 - _YY_G) / 45.0, 0.0, 1.0)

def compose_frame(frame_idx, rgb, matte_u8, clips, assets, cap_data):
    cap_groups, GOLD_W, EMER_W, ROSE_W, STROKE_W = cap_data
    t = frame_idx / FPS
    matte = matte_u8.astype(np.float32) / 255.0

    # 1. Smooth Camera Zoom (Talking-Head-v3)
    z = get_smooth_zoom(t)
    if z > 1.003:
        cw, ch = int(round(W / z)), int(round(H / z))
        x0 = max(0, min(W - cw, int(round(540 - cw * 0.5))))
        y0 = max(0, min(H - ch, int(round(690 - ch * (690.0 / H)))))
        frame_im = Image.fromarray(rgb[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
        matte_im = Image.fromarray(matte_u8[y0:y0+ch, x0:x0+cw], "L").resize((W, H), Image.Resampling.BILINEAR)
        fg_rgb = np.array(frame_im)
        m_arr  = np.array(matte_im, dtype=np.float32) / 255.0
    else:
        frame_im = Image.fromarray(rgb, "RGB")
        fg_rgb = rgb
        m_arr  = matte

    # 2. Talking-Head-v3 Real Office Room + Smooth Dimming on Behind-Head Animations!
    dim = get_bg_dim(t)
    if dim <= 0.005:
        comp_im = frame_im.convert("RGBA")
    else:
        bg_soft = frame_im.filter(ImageFilter.GaussianBlur(radius=5.0 * dim)) if dim > 0.08 else frame_im
        bg_arr = np.array(bg_soft, dtype=np.float32)
        bg_f = 1.0 - 0.76 * dim
        bg_dim = np.zeros_like(bg_arr)
        bg_dim[:, :, 0] = bg_arr[:, :, 0] * bg_f * (1.0 - 0.10 * dim)
        bg_dim[:, :, 1] = bg_arr[:, :, 1] * bg_f * (1.0 + 0.02 * dim)
        bg_dim[:, :, 2] = bg_arr[:, :, 2] * bg_f * (1.0 - 0.06 * dim)
        comp_im = Image.fromarray(np.clip(bg_dim, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

        # Behind-head Orbital Rings
        draw_orbital_rings_bg(comp_im, assets["box_b"], t, 23.30, 31.50)
        draw_orbital_rings_bg(comp_im, assets["box_b"], t, 43.80, 46.65)

        # Behind-head Numbers (CẢNH BÁO 1 / GIẢI PHÁP 2) — strictly Y >= 260!
        for lbl, dig, t0, t1 in [("CẢNH BÁO", "1", 5.15, 6.64), ("GIẢI PHÁP", "2", 19.14, 23.25)]:
            env_n = smooth_in_out_env(t, t0, t1, d_in=0.32, d_out=0.28)
            if env_n > 0.01:
                dt = t - t0
                u_n = ease_out_cubic(min(1.0, dt / 0.36))
                sp_l = render_glow_text_sprite(lbl, FONT_TITLE, 92, (162, 252, 212), (72, 214, 152), glow_col=(52, 198, 136), glow_rad=12)
                paste_centered(comp_im, sp_l, 265, 375 + (1.0 - env_n) * 18.0, scale_x=0.88 + 0.12 * u_n, opacity=env_n)
                sp_d = render_glow_text_sprite(dig, FONT_SERIF, 360, (255, 228, 112), (235, 168, 42), glow_col=(255, 200, 75), glow_rad=18, stroke_col=(255, 250, 235), stroke_w=6)
                paste_centered(comp_im, sp_d, 790, 470 + (1.0 - env_n) * 18.0, scale_x=0.85 + 0.15 * u_n, opacity=env_n, angle=-8.0 * (1.0 - u_n))

        # Behind-head Giant Keywords (Y = 420 -> top >= 335 >= 250 Safe Zone!)
        KEYWORDS = [
            ("KHÁT ĐẠM SẠCH",   14.95, 19.04, 136, (255, 232, 115), (242, 174,  42)),
            ("22,05G ĐẠM SẠCH", 23.32, 31.50, 128, (152, 255, 214), ( 48, 208, 144)),
            ("NO ÊM TỚI TRƯA",  37.42, 39.60, 134, (255, 232, 118), (245, 178,  48)),
            ("BỮA SÁNG 30 GIÂY",43.82, 46.64, 124, (162, 252, 216), ( 62, 214, 152)),
        ]
        for kw, t0, t1, fsz, ct, cb in KEYWORDS:
            env_k = smooth_in_out_env(t, t0, t1, d_in=0.36, d_out=0.32)
            if env_k > 0.01:
                dt = t - t0
                sw_p = (dt / max(0.3, t1 - t0)) * 1.25 - 0.10
                sp_k = render_glow_text_sprite(kw, FONT_TITLE, fsz, ct, cb, glow_col=ct, glow_rad=12)
                paste_centered(comp_im, sp_k, 540, 425 + (1.0 - env_k) * 20.0, scale_x=0.90 + 0.10 * ease_out_cubic(min(1.0, dt / 0.36)), opacity=env_k, sweep_prog=sw_p)

        # Composite real Chi Hang + desk & real AV Protein box cleanly in front!
        fg_alpha = np.maximum(m_arr, np.maximum(_DESK_LINE, _DESK_BOX * 0.94))
        fg_lit = np.clip(fg_rgb.astype(np.float32) * (1.0 - 0.04 * dim), 0, 255).astype(np.uint8)
        comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_lit, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

    # ==================================================================
    # CARD STYLE #1 (0.32 - 4.90s): 3-CARD OVERHEAD ARC DEAL + HOOK TYPOGRAPHY
    # Upper zone Y = 258..480, X = 75..1005; Lower Hook text X = 60..876, Y = 1040..1325
    # ==================================================================
    env_hk = smooth_in_out_env(t, 0.05, 4.90, d_in=0.30, d_out=0.32)
    if env_hk > 0.01:
        arc_specs = [
            (0.32, 226, 376, -8.5, "01", "diamond", "ivory",    "ĂN NO CĂNG",   "7h30 Sáng"),
            (0.50, 540, 354,  0.0, "02", "bolt",    "crimson",  "10H NGÁP NGỦ", "Rũ rượi!"),
            (0.68, 854, 376,  8.5, "03", "star",    "gold_ace", "TỤT PIN SỚM",  "Đói cồn cào"),
        ]
        for st_c, cx_c, cy_c, ang_c, rk, st_i, thm, tt, sb in arc_specs:
            if t >= st_c:
                dt_c = t - st_c
                u_c  = ease_out_back(min(1.0, dt_c / 0.34), 1.12)
                card_im = make_luxury_playing_card(244, 178, rk, st_i, thm, tt, sb)
                paste_centered(
                    comp_im, card_im,
                    cx_c, cy_c + (1.0 - u_c) * (-70.0) + math.sin(t * 2.6 + cx_c * 0.01) * 3.5,
                    scale_x=(0.86 + 0.14 * clamp01(dt_c / 0.28)),
                    opacity=env_hk * clamp01(dt_c / 0.18),
                    angle=ang_c,
                    blur_px=(1.0 - clamp01(dt_c / 0.22)) * 8.0,
                )
                draw_landing_ripple(comp_im, cx_c, cy_c + 86, dt_c - 0.22, rx_max=95, ry_max=18)

        # Front Face-Safe & Box-Safe Hook Typography (strictly X in [62..876], Y in [1035..1320]!)
        if t >= 0.06:
            u1 = ease_out_cubic(min(1.0, (t - 0.06) / 0.34))
            s1 = render_glow_text_sprite("Ăn sáng no căng", FONT_EBOLD, 52, (165, 250, 232), (82, 214, 178), glow_col=(48, 190, 145), glow_rad=10, stroke_col=(10, 26, 20), stroke_w=4)
            paste_centered(comp_im, s1, SAFE_LOW_CX, 1068 + (1.0 - u1) * 20.0, scale_x=0.88 + 0.12 * u1, opacity=env_hk * u1)
        if t >= 0.52:
            u2 = ease_out_back(min(1.0, (t - 0.52) / 0.36), 1.10)
            s2a = render_glow_text_sprite("10 GIỜ", FONT_BLACK, 88, (255, 234, 108), (235, 152, 28), glow_col=(255, 185, 45), glow_rad=13, stroke_col=(24, 16, 8), stroke_w=5)
            paste_centered(comp_im, s2a, 235, 1168 + (1.0 - u2) * 22.0, scale_x=0.86 + 0.14 * clamp01((t - 0.52)/0.30), opacity=env_hk)
        if t >= 0.78:
            u3 = ease_out_back(min(1.0, (t - 0.78) / 0.38), 1.10)
            s2b = render_glow_text_sprite("Ngáp Rũ Rượi?", FONT_EBOLD, 60, (255, 168, 182), (228, 56, 84), glow_col=(228, 65, 92), glow_rad=12, stroke_col=(28, 10, 16), stroke_w=5)
            paste_centered(comp_im, s2b, 612, 1170 + (1.0 - u3) * 22.0, scale_x=0.86 + 0.14 * clamp01((t - 0.78)/0.30), opacity=env_hk)
        if t >= 2.82:
            u4 = ease_out_cubic(min(1.0, (t - 2.82) / 0.32))
            s3 = render_glow_text_sprite("Bẫy đường huyết từ bữa sáng tinh bột!", FONT_BOLD, 34, (255, 252, 240), (210, 248, 228), glow_col=(28, 148, 98), glow_rad=8, stroke_col=(12, 24, 20), stroke_w=4)
            paste_centered(comp_im, s3, SAFE_LOW_CX, 1265 + (1.0 - u4) * 16.0, scale_x=0.92 + 0.08 * u4, opacity=env_hk * u4)

    # ==================================================================
    # CARD STYLE #3 (14.88 - 19.04s): 3-CARD HAND FAN SPREAD (XÒE QUẠT 3 LÁ BÀI!)
    # Strictly inside lower safe zone X = [68..862] <= 884, Y = [1080..1525] <= 1545!
    # ==================================================================
    env_fan = smooth_in_out_env(t, 14.88, 19.04, d_in=0.34, d_out=0.30)
    if env_fan > 0.01:
        dt_f = t - 14.88
        u_open = ease_out_back(min(1.0, dt_f / 0.52), 1.08)
        # Left card (-13 deg), Right card (+13 deg), Center Hero Gold Ace on top (0 deg, lifted!)
        c_left  = make_luxury_playing_card(224, 298, "10", "diamond", "crimson",  "DƯ TINH BỘT", "Nhanh đói\nTụt năng lượng", badge_txt="✕ KHÔNG CẦN")
        c_right = make_luxury_playing_card(224, 298, "K",  "leaf",    "emerald",  "NUÔI KHỐI CƠ", "Giữ sức bền\nTỉnh táo lâu", badge_txt="⚡ BỀN BỈ")
        c_ace   = make_luxury_playing_card(240, 322, "A",  "star",    "gold_ace", "ĐẠM SẠCH",     "Cơ thể đang\nkhát mỗi sáng!", badge_txt="★ CHÌA KHÓA")

        paste_centered(comp_im, c_left,  456 - 224 * u_open, 1342 + 16 * u_open, scale_x=0.90 + 0.10*env_fan, opacity=env_fan, angle=-15.5 * u_open, blur_px=(1.0-env_fan)*6.0)
        paste_centered(comp_im, c_right, 456 + 224 * u_open, 1342 + 16 * u_open, scale_x=0.90 + 0.10*env_fan, opacity=env_fan, angle=+15.5 * u_open, blur_px=(1.0-env_fan)*6.0)
        ace_lift = 26.0 * smoothstep((t - 16.10) / 0.35) if t > 16.10 else 0.0
        sw_ace = ((t - 16.15) / 1.4) if 16.15 <= t <= 17.75 else None
        paste_centered(comp_im, c_ace,   456, 1312 - ace_lift + math.sin(t * 2.8) * 3.5, scale_x=0.92 + 0.08*env_fan + (0.04 if ace_lift > 1 else 0.0), opacity=env_fan, angle=0.0, sweep_prog=sw_ace)

    # ==================================================================
    # CARD STYLE #4A (25.25 - 31.50s): 3D HORIZONTAL CARD FLIP (180 DEG!)
    # Placed at LEFT Safe Zone (cx=224, cy=1285, X=72..376) -> 0% overlap with real held AV PROTEIN box!
    # ==================================================================
    env_flp = smooth_in_out_env(t, 25.25, 31.50, d_in=0.34, d_out=0.30)
    if env_flp > 0.01:
        # 0..0.75s shows Emerald-Gold Foil Back, then flips 180 deg across t=26.05..26.75s to Front Ace!
        u_flip = quintic(clamp01((t - 26.05) / 0.68))
        theta  = u_flip * math.pi
        cos_t  = math.cos(theta)
        sx_3d  = max(0.04, abs(cos_t))
        if cos_t >= 0.0:
            c_3d = make_card_back(284, 386)
            sw_f = None
        else:
            c_3d = make_luxury_playing_card(284, 386, "A", "leaf", "emerald", "ĐẠM THỰC VẬT\nĐẬU HÀ LAN & GẠO", "Pha 30 giây • 2 gói", badge_txt="AV PROTEIN", big_val="22,05g")
            sw_f = clamp01((t - 26.75) / 1.10) if t <= 27.95 else None
        paste_centered(
            comp_im, c_3d,
            222, 1285 + math.sin(t * 2.4) * 4.0 + (1.0 - env_flp) * 35.0,
            scale_x=sx_3d * (0.92 + 0.08 * env_flp),
            scale_y=(0.92 + 0.08 * env_flp) * (1.0 + 0.05 * math.sin(theta)),
            opacity=env_flp,
            blur_px=(1.0 - env_flp) * 6.0,
            sweep_prog=sw_f,
        )

    # Small Share/10AM Mini Playing Card during real CTA (40.10 - 46.55s) at Left Safe Zone!
    env_sh = smooth_in_out_env(t, 40.10, 46.55, d_in=0.34, d_out=0.28)
    if env_sh > 0.01:
        c_sh = make_luxury_playing_card(268, 336, "K", "star", "gold_ace", "THỰC ĐƠN\n30s ĐỦ ĐẠM", "Tỉnh táo suốt sáng\nKhông ngáp lúc 10h!", badge_txt="QUÀ TẶNG")
        paste_centered(comp_im, c_sh, 214, 1315 + math.sin(t * 2.5) * 3.5, scale_x=0.90 + 0.10 * env_sh, opacity=env_sh, angle=-2.5)

    # ==================================================================
    # TALKING-HEAD-V3 WORD-BY-WORD CAPTIONS (100% SAFE ZONE X=58..878, Y=1085..1195!)
    # ==================================================================
    for g in cap_groups:
        if g["t0"] <= t < g["t1"]:
            op_g = smoothstep((g["t1"] - t) / 0.22) if (g["t1"] - t) < 0.22 else 1.0
            # Shift lower-chest caption center slightly left to SAFE_LOW_CX=468 when lines are wide so X_right <= 880 ALWAYS!
            # Wait: during 14.9..19.0s (3-card fan at Y=1130..1510), place caption cleanly at Y=955..1025 right above the fan!
            if 14.80 <= t <= 19.05:
                y_base = 948
            elif 25.20 <= t <= 31.55 or 40.05 <= t <= 46.60:
                # Left card occupies X=72..376, so center captions cleanly in X=385..876 (cx=630) OR above at Y=995!
                # Placing at Y=995 (cx=468, X=62..874) keeps 0% overlap with BOTH face (chin y<=810), left card (y>=1075), AND held box (y>=1250)!
                y_base = 985
            else:
                y_base = 1115
            lh, gap = 64, 15
            max_w_allowed = 816  # 468 +- 408 => [60..876] <= 884px!

            for li, ln in enumerate(g["lines"]):
                w_renders, tot_w = [], 0
                for wi, (wtxt, ws, we) in enumerate(ln):
                    is_hi = (wtxt in GOLD_W or wtxt in EMER_W or wtxt in ROSE_W)
                    k_sz  = 1.14 if is_hi else 1.0
                    if wtxt in GOLD_W:
                        ct, cb = (255, 236, 112), (238, 165, 34)
                    elif wtxt in EMER_W:
                        ct, cb = (158, 255, 214), (48, 212, 148)
                    elif wtxt in ROSE_W:
                        ct, cb = (255, 176, 188), (235, 72, 98)
                    else:
                        ct, cb = (255, 255, 255), (232, 244, 238)
                    sp = render_glow_text_sprite(wtxt, FONT_EBOLD, 50 * k_sz, ct, cb, glow_col=ct, glow_rad=9, stroke_col=(10, 20, 16), stroke_w=5)
                    adv = int(ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_EBOLD, 50 * k_sz))) + 4
                    w_renders.append((wtxt, ws, sp, adv, ct))
                    tot_w += adv + (gap if wi > 0 else 0)

                fit_k = min(1.0, max_w_allowed / max(1.0, float(tot_w)))
                eff_tot = tot_w * fit_k
                cur_x = SAFE_LOW_CX - eff_tot * 0.5
                cur_y = y_base + li * lh
                for wtxt, ws, sp, adv, ct in w_renders:
                    eff_adv = adv * fit_k
                    if t >= ws - 0.02:
                        dt_w = max(0.0, t - ws)
                        u_w  = ease_out_cubic(min(1.0, dt_w / 0.22))
                        wcx  = cur_x + eff_adv * 0.5
                        paste_centered(comp_im, sp, wcx, cur_y + (1.0 - u_w) * 16.0, scale_x=fit_k * (0.92 + 0.08 * u_w), opacity=op_g * u_w, blur_px=(1.0 - u_w) * 4.5)
                        if wtxt in STROKE_W and 0.05 <= dt_w <= 0.42:
                            u_su = (dt_w - 0.05) / 0.37
                            sp_su = render_glow_text_sprite(wtxt, FONT_EBOLD, 50 * 1.14, (255, 255, 255), glow_col=ct, glow_rad=6, stroke_col=(255, 245, 200), stroke_w=3)
                            paste_centered(comp_im, sp_su, wcx, cur_y, scale_x=fit_k * (1.0 + 0.45 * ease_out_cubic(u_su)), opacity=op_g * (1.0 - u_su) * 0.55)
                    cur_x += eff_adv + gap * fit_k
            break

    # ==================================================================
    # CARD STYLE #2 (6.65 - 13.06s): FULL-SCREEN DUAL-CARD DIAGONAL CLASH!
    # Covers 100% of main screen! Upper card Y=268..778; Lower card X=68..868, Y=968..1508!
    # ==================================================================
    env_s2 = smooth_in_out_env(t, 6.65, 13.06, d_in=0.36, d_out=0.34)
    if env_s2 > 0.005:
        stage2 = STAGE_BG_IM.copy()
        dt2 = t - 6.65

        # Top Playing Card: High-Carb Breakfast -> Blood Sugar Spike
        vf_top = sample_clip_pingpong(clips["av01"], dt2, rate=0.95)
        u_t1 = ease_out_back(min(1.0, dt2 / 0.42), 1.08)
        c_top = make_video_playing_card(
            vf_top, 860, 468, "Q", "diamond", "ivory",
            "07:30 • BỮA SÁNG TINH BỘT",
            "Đường huyết TĂNG VỌT cực nhanh!",
            zoom=1.02 + 0.05 * smoothstep(dt2 / 6.4),
        )
        paste_centered(stage2, c_top, 538, 522 - (1.0 - u_t1) * 48.0, scale_x=0.94 + 0.06 * u_t1, opacity=1.0, angle=1.1)

        # Center Animated Blood-Sugar Spike & Crash Ribbon (Y=808..922, X=66..870 <= 884!)
        rib = Image.new("RGBA", (804, 108), (0, 0, 0, 0))
        dr = ImageDraw.Draw(rib)
        dr.rounded_rectangle([0, 0, 803, 107], radius=28, fill=(12, 28, 22, 244), outline=(255, 214, 102, 230), width=3)
        prog_curve = clamp01((t - 6.95) / 4.20)
        curve_pts = [
            (28, 80), (88, 74), (152, 20), (204, 16), (258, 48), (318, 86), (368, 92)
        ]
        n_vis = max(2, int(round(prog_curve * len(curve_pts))))
        dr.line(curve_pts[:n_vis], fill=(255, 92, 108, 255) if t >= 9.4 else (255, 214, 92, 255), width=6)
        cx_dot, cy_dot = curve_pts[n_vis - 1]
        dr.ellipse([cx_dot - 8, cy_dot - 8, cx_dot + 8, cy_dot + 8], fill=(255, 255, 255, 255))
        f_rb1 = get_font(FONT_EBOLD, 23)
        f_rb2 = get_font(FONT_BOLD, 19)
        lbl_rb = "SAU 2 TIẾNG: TỤT DỐC SÂU!" if t >= 9.45 else "ĐƯỜNG HUYẾT VỌT LÊN ĐỈNH!"
        col_rb = (255, 132, 145, 255) if t >= 9.45 else (255, 228, 118, 255)
        dr.text((396, 22), "BIỂU ĐỒ ĐƯỜNG HUYẾT BUỔI SÁNG", font=f_rb2, fill=(172, 238, 206, 255))
        dr.text((396, 54), lbl_rb, font=f_rb1, fill=col_rb)
        paste_centered(stage2, rib, SAFE_LOW_CX, 868)

        # Bottom Playing Card: 10 AM Crash (X = 468 +- 388 = [80..856] <= 884, Y = 1238 +- 248 = [990..1486] <= 1545!)
        vf_bot = sample_clip_pingpong(clips["av02"], max(0.0, t - 6.65), rate=0.95)
        dt_b = max(0.0, t - 7.15)
        u_b1 = ease_out_back(min(1.0, dt_b / 0.46), 1.08)
        c_bot = make_video_playing_card(
            vf_bot, 764, 468, "K", "bolt", "crimson",
            "10:00 • CHỈ SAU 2 TIẾNG",
            "TỤT DỐC KHÔNG PHANH • Ngáp rũ rượi!",
            zoom=1.07 - 0.05 * smoothstep(dt2 / 6.4),
        )
        paste_centered(stage2, c_bot, SAFE_LOW_CX, 1242 + (1.0 - u_b1) * 56.0, scale_x=0.93 + 0.07 * clamp01(dt_b / 0.36), opacity=clamp01(dt_b / 0.22), angle=-1.1)

        if env_s2 >= 0.995:
            comp_im = stage2
        else:
            arr_s = np.array(stage2)
            arr_s[:, :, 3] = (arr_s[:, :, 3].astype(np.float32) * env_s2).astype(np.uint8)
            comp_im.alpha_composite(Image.fromarray(arr_s, "RGBA"))

    # ==================================================================
    # CARD STYLE #4B (31.52 - 37.36s): FULL-SCREEN RAPID RIFFLE CASCADE + 3D HERO ACE!
    # COVERS 100% OF VOICE STUDIO CLONED "thêm 1.632mg L-Leucine, giữ khối cơ săn chắc"!
    # ==================================================================
    env_s4 = smooth_in_out_env(t, 31.52, 37.36, d_in=0.30, d_out=0.34)
    if env_s4 > 0.005:
        stage4 = STAGE_BG_IM.copy()
        dt4 = t - 31.52

        # Upper Cinema Playing Card: crossfades smoothly from av03 (Pea & Rice Shake) -> av04 (Toned Vitality)!
        vf_3 = sample_clip_pingpong(clips["av03"], dt4, rate=0.95)
        vf_4 = sample_clip_pingpong(clips["av04"], max(0.0, t - 34.20), rate=0.95)
        w_cf = smoothstep((t - 34.30) / 0.48) if t >= 34.30 else 0.0
        vf_mix = np.clip(vf_3.astype(np.float32) * (1.0 - w_cf) + vf_4.astype(np.float32) * w_cf, 0, 255).astype(np.uint8)

        pill_4 = "GIỮ KHỐI CƠ SĂN CHẮC" if t >= 34.60 else "CÔNG THỨC ĐẠM THỰC VẬT SẠCH"
        foot_4 = "Săn chắc cơ • Nhẹ bụng • No êm tới trưa!" if t >= 34.60 else "Đậu Hà Lan & Gạo + Hoạt chất khóa cơ L-Leucine"
        c_up4 = make_video_playing_card(vf_mix, 872, 464, "A", "star", "ivory", pill_4, foot_4, zoom=1.02 + 0.05 * smoothstep(dt4 / 5.8))
        paste_centered(stage4, c_up4, 538, 520, scale_x=0.96 + 0.04 * ease_out_cubic(min(1.0, dt4 / 0.35)))

        # Lower Rapid Riffle Card Stack (X = [60..585]) + Real Studio Cutout Box av01_protein_b.png (X = [575..876] <= 884!)
        riffle_cards = [
            (0.08, 258, 1065, -5.0, "01", "leaf",    "emerald",  "2 GÓI • 30 GIÂY", "Pha nhanh gọn mỗi sáng",  "TIỆN LỢI",   None),
            (0.24, 286, 1135,  3.2, "02", "diamond", "ivory",    "22,05G ĐẠM SẠCH", "Từ Đậu Hà Lan & Gạo",     "ĐẠM THỰC VẬT", None),
        ]
        for st_r, rx_c, ry_c, rang, rrk, rst, rth, rtt, rsb, rbd, rbv in riffle_cards:
            if dt4 >= st_r:
                ur = ease_out_back(min(1.0, (dt4 - st_r) / 0.30), 1.10)
                rc = make_luxury_playing_card(360, 210, rrk, rst, rth, rtt, rsb, badge_txt=rbd, big_val=rbv)
                paste_centered(stage4, rc, rx_c - (1.0 - ur) * 120.0, ry_c, scale_x=0.92 + 0.08 * clamp01((dt4-st_r)/0.25), opacity=clamp01((dt4-st_r)/0.16), angle=rang)

        # Hero Gold-Foil Ace Card flipping open at dt4 = 0.42s (31.94s -> exact start of "thêm 1.632mg L-Leucine"!)
        if dt4 >= 0.40:
             dt_hero = dt4 - 0.40
             u_hf = quintic(clamp01(dt_hero / 0.52))
             th_h = u_hf * math.pi
             cs_h = math.cos(th_h)
             if cs_h >= 0.0:
                 hero_c = make_card_back(456, 372)
                 sw_h = None
             else:
                 sub_h = "Giữ khối cơ săn chắc bền bỉ!" if t >= 34.80 else "Công tắc kích hoạt nuôi cơ!"
                 hero_c = make_luxury_playing_card(
                     456, 372, "A", "star", "gold_ace",
                     "L-LEUCINE CHUẨN", sub_h,
                     badge_txt="★ HOẠT CHẤT VÀNG", big_val="1.632 MG",
                 )
                 sw_h = ((dt_hero - 0.55) / 1.35) % 1.3 if dt_hero > 0.55 else None
             paste_centered(
                 stage4, hero_c,
                 304, 1308 + math.sin(t * 2.6) * 4.0,
                 scale_x=max(0.05, abs(cs_h)),
                 scale_y=1.0 + 0.04 * math.sin(th_h),
                 opacity=clamp01(dt_hero / 0.15),
                 sweep_prog=sw_h,
             )
             draw_landing_ripple(stage4, 304, 1495, dt_hero - 0.48, rx_max=170, ry_max=26)

        # Real Studio Cutout AV Protein Box on right side of safe zone (cx=720, cy=1245 -> X in [566..874] <= 884, Y in [1015..1475] <= 1545!)
        box_im = assets["box_b"]
        u_bx = ease_out_back(min(1.0, dt4 / 0.45), 1.08)
        paste_centered(stage4, box_im, 720, 1245 + math.sin(t * 2.2) * 5.0 + (1.0 - u_bx) * 45.0, scale_x=0.73 * (0.90 + 0.10 * clamp01(dt4 / 0.35)), opacity=clamp01(dt4 / 0.22))

        if env_s4 >= 0.995:
            comp_im = stage4
        else:
            arr_s4 = np.array(stage4)
            arr_s4[:, :, 3] = (arr_s4[:, :, 3].astype(np.float32) * env_s4).astype(np.uint8)
            comp_im.alpha_composite(Image.fromarray(arr_s4, "RGBA"))

    # ==================================================================
    # CARD STYLE #5 (46.66 - 49.567s): ROYAL CARD TABLE & CTA END-CARD DEAL!
    # COVERS 100% OF VOICE STUDIO CLONED "nhắn chữ PROTEIN bên dưới!"
    # Strictly inside Safe Zone: Upper Y>=258, Lower X in [62..878] <= 884, Y <= 1538!
    # ==================================================================
    env_s5 = smooth_in_out_env(t, 46.66, 49.65, d_in=0.28, d_out=0.05)
    if env_s5 > 0.005:
        stage5 = STAGE_BG_IM.copy()
        dt5 = t - 46.66

        # Official An Vuong Logo + Gold Headline (Y = 262..435)
        paste_centered(stage5, assets["logo_dark"], 540, 306, scale_x=0.88)
        sp_eh = render_glow_text_sprite("THỰC ĐƠN BỮA SÁNG 30 GIÂY ĐỦ ĐẠM", FONT_BLACK, 52, (255, 236, 118), (236, 168, 42), glow_col=(255, 195, 60), glow_rad=10, stroke_col=(10, 24, 18), stroke_w=4)
        paste_centered(stage5, sp_eh, 540, 404, scale_x=0.94 + 0.06 * ease_out_cubic(min(1.0, dt5 / 0.32)))

        # Unobstructed Royal Spread: Left Card (X=76..328, Y=492..828), Center Real Box (cx=540, Y=535..1065), Right Card (X=752..1004, Y=492..828 < 860!)
        u_d5 = ease_out_back(min(1.0, dt5 / 0.42), 1.10)
        c5_l = make_luxury_playing_card(248, 318, "A", "leaf", "emerald", "ĐẠM ĐẬU & GẠO", "No êm • Nhẹ bụng", badge_txt="2 GÓI 30s", big_val="22,05g")
        c5_r = make_luxury_playing_card(248, 318, "K", "star", "ivory",   "GIỮ CƠ CHẮC",   "Tỉnh táo tới trưa", badge_txt="L-LEUCINE", big_val="1.632mg")
        paste_centered(stage5, c5_l, 200, 658 + (1.0 - u_d5) * 36.0, scale_x=0.94, angle=-8.5)
        paste_centered(stage5, c5_r, 880, 658 + (1.0 - u_d5) * 36.0, scale_x=0.94, angle=+8.5)

        # Center Hero Real Studio Cutout av01_protein_b.png + subtle 3/4 companion av01_protein_a.png cleanly in middle!
        paste_centered(stage5, assets["box_a"], 452, 818 + math.sin(t * 2.4) * 4.0, scale_x=0.72 * clamp01(dt5 / 0.25))
        paste_centered(stage5, assets["box_b"], 606, 836 + math.sin(t * 2.4 + 0.8) * 4.0, scale_x=0.76 * clamp01(dt5 / 0.28))

        # Lower CTA Royal Action Card (cx=468, w=788, h=276 -> X in [74..862] <= 884, Y in [1156..1432] <= 1545!)
        pulse_cta = 1.0 + 0.024 * math.sin(dt5 * 7.5)
        cta_card = make_luxury_playing_card(
            788, 276, "A", "star", "gold_ace",
            'NHẮN CHỮ "PROTEIN"\nBÊN DƯỚI NGAY!',
            "Nhận miễn phí Thực Đơn Bữa Sáng 30 Giây Đủ Đạm",
            badge_txt="★ BÌNH LUẬN NHẬN THỰC ĐƠN ★",
        )
        sw_cta = (dt5 / 1.15) % 1.35
        paste_centered(stage5, cta_card, SAFE_LOW_CX, 1296, scale_x=pulse_cta * clamp01(dt5 / 0.24), sweep_prog=sw_cta)

        # Legal disclaimer cleanly inside Safe Zone (Y = 1496..1532 <= 1545, X in [68..868] <= 884!)
        sp_leg = render_glow_text_sprite(
            "Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh",
            FONT_BOLD, 20, (218, 238, 226), glow_rad=0, stroke_col=(8, 18, 14), stroke_w=3
        )
        paste_centered(stage5, sp_leg, SAFE_LOW_CX, 1514, opacity=0.92)

        if env_s5 >= 0.995:
            comp_im = stage5
        else:
            arr_s5 = np.array(stage5)
            arr_s5[:, :, 3] = (arr_s5[:, :, 3].astype(np.float32) * env_s5).astype(np.uint8)
            comp_im.alpha_composite(Image.fromarray(arr_s5, "RGBA"))
    else:
        # Subtle compliant disclaimer inside Safe Zone at Y=1518 (X in [68..868] <= 884, Y <= 1542!)
        sp_leg = render_glow_text_sprite(
            "Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh",
            FONT_BOLD, 19, (232, 242, 236), glow_rad=0, stroke_col=(10, 18, 15), stroke_w=3
        )
        paste_centered(comp_im, sp_leg, SAFE_LOW_CX, 1520, opacity=0.82)

    return comp_im

def render_chunk(args):
    c_idx, f_start, f_end = args
    n_frames = f_end - f_start
    ss_sec = f"{f_start / FPS:.6f}"
    chunk_mp4 = os.path.join(PROJ_DIR, f"_v3_chunk_{c_idx:02d}.mp4")

    vid_p = os.path.join(AROLL_DIR, "edited_graded.mp4")
    mat_p = os.path.join(AROLL_DIR, "edited_matte.mp4")

    clips = {
        "av01": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_01_carb_spike.mp4"),     960, 540),
        "av02": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_02_10am_sleepy.mp4"),    960, 540),
        "av03": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_03_pea_rice_shake.mp4"), 960, 540),
        "av04": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_04_toned_vitality.mp4"), 960, 540),
    }
    assets = load_static_assets()
    cap_data = load_captions_htav()

    pv = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", vid_p, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    pm = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", mat_p, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "gray",  "-"], stdout=subprocess.PIPE)

    writer = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
        chunk_mp4
    ], stdin=subprocess.PIPE)

    for li in range(n_frames):
        bv = pv.stdout.read(W * H * 3)
        bm = pm.stdout.read(W * H)
        if len(bv) < W * H * 3 or len(bm) < W * H:
            break
        rgb = np.frombuffer(bv, dtype=np.uint8).reshape((H, W, 3))
        mat = np.frombuffer(bm, dtype=np.uint8).reshape((H, W))
        im_out = compose_frame(f_start + li, rgb, mat, clips, assets, cap_data)
        writer.stdin.write(np.array(im_out.convert("RGB"), dtype=np.uint8).tobytes())

    writer.stdin.close(); writer.wait()
    pv.stdout.close(); pv.wait()
    pm.stdout.close(); pm.wait()
    print(f"[Chunk {c_idx}] Rendered frames {f_start}..{f_end - 1}", flush=True)
    return chunk_mp4

def run_test_grid():
    # Audit key bounding boxes against safe_zone_9x16!
    key_boxes = [
        ("Hook Arc Left",    226-122, 376-89, 226+122, 376+89),
        ("Hook Arc Right",   854-122, 376-89, 854+122, 376+89),
        ("Hook Title Lower", 468-400, 1040,   468+400, 1310),
        ("DualCard Top",     538-430, 522-234,538+430, 522+234),
        ("DualCard Bottom",  468-382, 1242-234,468+382,1242+234),
        ("Fan Spread",       445-330, 1130,   445+330, 1505),
        ("3D Flip Card",     222-142, 1285-193,222+142,1285+193),
        ("Riffle Hero Ace",  304-228, 1308-186,304+228,1308+186),
        ("Riffle Real Box",  720-154, 1245-190,720+154,1245+190),
        ("EndCard CTA",      468-390, 1308-128,468+390,1308+128),
        ("Legal Strip",      468-400, 1500,   468+400, 1538),
    ]
    for bname, x1, y1, x2, y2 in key_boxes:
        ok, reasons = is_box_safe_9x16(x1, y1, x2, y2)
        print(f"  [SafeZone {bname:18s}] {'PASS' if ok else 'FAIL'} {reasons}")
        assert ok, f"Safe zone violation on {bname}: {reasons}"

    clips = {
        "av01": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_01_carb_spike.mp4"),     960, 540),
        "av02": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_02_10am_sleepy.mp4"),    960, 540),
        "av03": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_03_pea_rice_shake.mp4"), 960, 540),
        "av04": load_vid_frames_wh(os.path.join(MEDIA_DIR, "av_04_toned_vitality.mp4"), 960, 540),
    }
    assets = load_static_assets()
    cap_data = load_captions_htav()
    vid_p = os.path.join(AROLL_DIR, "edited_graded.mp4")
    mat_p = os.path.join(AROLL_DIR, "edited_matte.mp4")

    ts_list = [1.40, 3.40, 5.80, 8.20, 11.20, 16.80, 21.00, 26.25, 28.50, 33.40, 38.40, 47.80]
    grid = Image.new("RGB", (270 * 6, 480 * 2))
    f_lbl = get_font(FONT_BOLD, 20)
    for i, ts in enumerate(ts_list):
        f_idx = int(round(ts * FPS))
        ss = f"{f_idx / FPS:.6f}"
        rv = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", vid_p, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        rm = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", mat_p, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray",  "-"])
        rgb = np.frombuffer(rv[:W*H*3], dtype=np.uint8).reshape((H, W, 3))
        mat = np.frombuffer(rm[:W*H],   dtype=np.uint8).reshape((H, W))
        im_c = compose_frame(f_idx, rgb, mat, clips, assets, cap_data).convert("RGB")
        # Draw subtle cyan safe-zone reference outline ONLY on test grid so we visually verify 100% margin!
        im_sm = im_c.resize((270, 480), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(im_sm)
        d.rectangle([8, 8, 108, 36], fill=(10, 18, 14))
        d.text((15, 10), f"{ts:05.2f}s", font=f_lbl, fill=(255, 224, 92))
        grid.paste(im_sm, ((i % 6) * 270, (i // 6) * 480))

    gp = os.path.join(CHECK_DIR, "v3_cards_test_grid.jpg")
    grid.save(gp, quality=94)
    print("Saved 12-panel Playing-Card + Talking-Head v3 test grid ->", gp, flush=True)

def main():
    if "--test" in sys.argv:
        run_test_grid()
        return
    t0 = time.time()
    N_WORKERS = 4  # NVENC typically allows up to 5-8 concurrent sessions on RTX 4070!
    step = math.ceil(TOTAL_FRAMES / N_WORKERS)
    tasks = [(i, i * step, min(TOTAL_FRAMES, (i + 1) * step)) for i in range(N_WORKERS) if i * step < TOTAL_FRAMES]
    print(f"[HT-AV Master] Rendering {TOTAL_FRAMES} frames across {len(tasks)} GPU workers...", flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        chunks = list(ex.map(render_chunk, tasks))

    lst = os.path.join(PROJ_DIR, "_v3_chunks.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for cf in chunks:
            f.write("file '" + cf.replace("\\", "/") + "'\n")
    out_v = os.path.join(PROJ_DIR, "_v3_video_only.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out_v], check=True)
    for cf in chunks + [lst]:
        if os.path.exists(cf):
            os.remove(cf)
    print(f"[HT-AV Master] ALL {TOTAL_FRAMES} FRAMES RENDERED IN {time.time() - t0:.1f}s -> {out_v}", flush=True)

if __name__ == "__main__":
    main()
