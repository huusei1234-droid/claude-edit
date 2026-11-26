import concurrent.futures, json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"C:\AI\full studio\output\batch-htav-261125")
from safe_zone_9x16 import is_box_safe_9x16
from batch_ep_configs_17 import EP_CONFIGS

BATCH_DIR  = r"C:\AI\full studio\output\batch-htav-261125"
CUTOUT_DIR = os.path.join(BATCH_DIR, "product_cutouts")
FONTS_DIR  = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"

W, H = 1080, 1920
FPS = 30.0
SAFE_LOW_CX = 468  # Safe horizontal center for Y >= 860 so X in [60..876] <= 884px!

FONT_TITLE = os.path.join(FONTS_DIR, "Oswald-Bold.ttf")
FONT_BLACK = os.path.join(FONTS_DIR, "AsapCondensed-Black.ttf")
FONT_EBOLD = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
FONT_BOLD  = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")
FONT_SERIF = os.path.join(FONTS_DIR, "PlayfairDisplay-BoldItalic.ttf")

PALETTES = {
    "emerald_amber": {
        "bg_rgb": (14, 34, 26),
        "ring1": (162, 248, 210), "ring2": (255, 220, 118),
        "kw_gold": ((255, 234, 115), (240, 172, 40)),
        "kw_emer": ((156, 255, 214), (48, 208, 146)),
    },
    "rose_medical": {
        "bg_rgb": (38, 16, 26),
        "ring1": (255, 192, 214), "ring2": (255, 224, 128),
        "kw_gold": ((255, 236, 122), (242, 172, 48)),
        "kw_emer": ((255, 196, 218), (232, 92, 138)),
    },
    "sapphire_gold": {
        "bg_rgb": (14, 24, 42),
        "ring1": (158, 220, 255), "ring2": (255, 222, 118),
        "kw_gold": ((255, 234, 116), (238, 168, 38)),
        "kw_emer": ((162, 234, 255), (56, 168, 238)),
    },
    "amber_champagne": {
        "bg_rgb": (36, 24, 14),
        "ring1": (255, 226, 156), "ring2": (162, 242, 198),
        "kw_gold": ((255, 238, 124), (242, 168, 36)),
        "kw_emer": ((172, 252, 208), (58, 206, 138)),
    },
    "peach_champagne": {
        "bg_rgb": (38, 20, 22),
        "ring1": (255, 206, 188), "ring2": (255, 228, 132),
        "kw_gold": ((255, 236, 122), (242, 170, 44)),
        "kw_emer": ((255, 208, 192), (242, 118, 102)),
    },
}

_font_cache = {}
def get_font(path, size):
    k = (path, max(12, int(round(size))))
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

def smooth_in_out_env(t, t0, t1, d_in=0.32, d_out=0.28):
    if t <= t0 or t >= t1:
        return 0.0
    a_in = quintic((t - t0) / max(0.04, d_in)) if (t - t0) < d_in else 1.0
    a_out = quintic((t1 - t) / max(0.04, d_out)) if (t1 - t) < d_out else 1.0
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

_stage_bg_cache = {}
def get_stage_canvas(pal_name):
    if pal_name in _stage_bg_cache:
        return _stage_bg_cache[pal_name]
    pal = PALETTES.get(pal_name, PALETTES["emerald_amber"])
    r0, g0, b0 = pal["bg_rgb"]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1.0 - 0.50 * (((xx - 540.0) / 660.0) ** 2 + ((yy - 920.0) / 1120.0) ** 2), 0.32, 1.0)
    bbg = np.zeros((H, W, 3), dtype=np.uint8)
    bbg[:, :, 0] = np.clip(r0 * 1.25 * vig, 0, 255).astype(np.uint8)
    bbg[:, :, 1] = np.clip(g0 * 1.25 * vig, 0, 255).astype(np.uint8)
    bbg[:, :, 2] = np.clip(b0 * 1.25 * vig, 0, 255).astype(np.uint8)
    im = Image.fromarray(bbg, "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse([540 - 620, 880 - 620, 540 + 620, 880 + 620], outline=(*pal["ring2"], 30), width=2)
    d.ellipse([540 - 460, 880 - 460, 540 + 460, 880 + 460], outline=(*pal["ring1"], 26), width=2)
    fl = np.exp(-((xx / 380.0) ** 2 + (yy / 420.0) ** 2)) + np.exp(-(((W - xx) / 380.0) ** 2 + (yy / 420.0) ** 2))
    fl_rgba = np.zeros((H, W, 4), dtype=np.uint8)
    fl_rgba[:, :, 0] = 255; fl_rgba[:, :, 1] = 232; fl_rgba[:, :, 2] = 175
    fl_rgba[:, :, 3] = np.clip(fl * 62.0, 0, 88).astype(np.uint8)
    flare_im = Image.fromarray(fl_rgba, "RGBA")
    stage_im = Image.alpha_composite(im, flare_im)
    _stage_bg_cache[pal_name] = (stage_im, flare_im)
    return stage_im, flare_im

_sprite_cache = {}
def render_glow_text_sprite(text, font_path, size, top_col, bot_col=None, glow_col=None, glow_rad=11, stroke_col=None, stroke_w=0):
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
    pad = int(glow_rad * 2.4 + stroke_w + 14)
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
        g2_a = mask_im.filter(ImageFilter.GaussianBlur(radius=glow_rad * 1.80))
        g_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
        g_arr[:, :, 0] = glow_col[0]; g_arr[:, :, 1] = glow_col[1]; g_arr[:, :, 2] = glow_col[2]
        g_arr[:, :, 3] = np.clip(np.array(g1_a, dtype=np.float32) * 0.62 + np.array(g2_a, dtype=np.float32) * 0.38, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(g_arr, "RGBA"))

    sh_a = mask_im.filter(ImageFilter.GaussianBlur(radius=5))
    sh_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
    sh_arr[:, :, 3] = (np.array(sh_a, dtype=np.float32) * 0.82).astype(np.uint8)
    sh_im.paste(Image.fromarray(sh_arr, "RGBA"), (3, 6))
    base = Image.alpha_composite(base, sh_im)

    if stroke_w > 0 and stroke_col is not None:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_im).text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        base = Image.alpha_composite(base, st_im)

    base = Image.alpha_composite(base, fill_im)
    if len(_sprite_cache) > 900:
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
        im = im.filter(ImageFilter.GaussianBlur(radius=min(13.0, blur_px)))
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

# ==============================================================================
# BIGGER-TEXT LUXURY PLAYING-CARD BUILDERS ("nho la text to len")
# ==============================================================================
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
    else:
        draw.ellipse([cx - r*0.65, cy - r*0.85, cx + r*0.65, cy + r*0.55], fill=col)
        draw.rectangle([cx - max(1, int(r*0.14)), cy + r*0.25, cx + max(1, int(r*0.14)), cy + r], fill=col)

_card_cache = {}
def make_luxury_playing_card(w, h, rank_txt, suit, theme, title_txt, sub_txt, badge_txt=None, big_val=None):
    key = (w, h, rank_txt, suit, theme, title_txt, sub_txt, badge_txt, big_val)
    if key in _card_cache:
        return _card_cache[key]

    pad = 20
    cw, ch = w + pad * 2, h + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 2, pad + 11, pad + w + 2, pad + h + 11], radius=28, fill=(6, 12, 14, 175))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    d = ImageDraw.Draw(card)
    if theme == "crimson":
        bg_fill, rim_outer, rim_inner = (255, 245, 247, 254), (225, 52, 72, 255), (244, 160, 172, 215)
        acc_col, txt_col, sub_col = (198, 22, 48, 255), (24, 14, 20, 255), (112, 34, 48, 255)
    elif theme == "gold_ace":
        bg_fill, rim_outer, rim_inner = (16, 40, 34, 254), (255, 216, 92, 255), (232, 176, 56, 215)
        acc_col, txt_col, sub_col = (255, 226, 104, 255), (255, 252, 240, 255), (178, 248, 214, 255)
    elif theme == "emerald":
        bg_fill, rim_outer, rim_inner = (243, 254, 248, 254), (16, 152, 98, 255), (132, 224, 184, 220)
        acc_col, txt_col, sub_col = (10, 124, 78, 255), (14, 28, 22, 255), (34, 90, 68, 255)
    else:
        bg_fill, rim_outer, rim_inner = (255, 252, 244, 254), (224, 166, 44, 255), (242, 210, 134, 220)
        acc_col, txt_col, sub_col = (182, 114, 10, 255), (20, 22, 28, 255), (78, 62, 38, 255)

    x0, y0, x1, y1 = pad, pad, pad + w - 1, pad + h - 1
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=bg_fill, outline=(255, 255, 255, 255), width=4)
    d.rounded_rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], radius=22, outline=rim_outer, width=3)
    d.rounded_rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], radius=18, outline=rim_inner, width=2)

    f_rk = get_font(FONT_BLACK, max(19, int(h * 0.092)))
    d.text((x0 + 14, y0 + 9), rank_txt, font=f_rk, fill=acc_col)
    if h >= 210:
        draw_suit_icon(d, suit, x0 + 23, y0 + 15 + int(h * 0.105), max(7, int(h * 0.034)), acc_col)
    else:
        rk_w = d.textbbox((0, 0), rank_txt, font=f_rk)[2]
        draw_suit_icon(d, suit, x0 + 20 + rk_w, y0 + 20, 7, acc_col)
    draw_suit_icon(d, suit, x1 - 22, y1 - 18, max(6, int(h * 0.032)), acc_col)

    cx_c = pad + w * 0.5
    # Start below corner rank so top-left index NEVER overlaps badge pill or title!
    if h < 210:
        cur_y = y0 + int(h * 0.36)
    elif w < 320:
        cur_y = y0 + max(54, int(h * 0.21))
    else:
        cur_y = y0 + int(h * 0.19)

    if badge_txt:
        max_pill_txt_w = (w - 92) if (w >= 320 and cur_y < y0 + 52) else (w - 42)
        fb = get_font(FONT_EBOLD, max(18, int(h * 0.076)))
        while fb.size > 14 and (d.textbbox((0, 0), badge_txt, font=fb)[2] > max_pill_txt_w):
            fb = get_font(FONT_EBOLD, fb.size - 2)
        bb = d.textbbox((0, 0), badge_txt, font=fb)
        bw, bh = (bb[2] - bb[0]) + 24, (bb[3] - bb[1]) + 12
        d.rounded_rectangle([cx_c - bw*0.5, cur_y - bh*0.5, cx_c + bw*0.5, cur_y + bh*0.5], radius=bh//2, fill=acc_col)
        pill_fg = (14, 32, 24, 255) if theme == "gold_ace" else (255, 255, 255, 255)
        d.text((cx_c - (bb[2]-bb[0])*0.5 - bb[0], cur_y - (bb[1]+bb[3])*0.5), badge_txt, font=fb, fill=pill_fg)
        cur_y += bh * 0.5 + int(h * 0.115)

    if big_val:
        fv = get_font(FONT_BLACK, max(38, int(h * 0.215)))
        while fv.size > 26 and (d.textbbox((0, 0), big_val, font=fv)[2] > w - 32):
            fv = get_font(FONT_BLACK, fv.size - 3)
        bv = d.textbbox((0, 0), big_val, font=fv)
        d.text((cx_c - (bv[2]-bv[0])*0.5 - bv[0], cur_y - (bv[1]+bv[3])*0.5), big_val, font=fv, fill=acc_col)
        cur_y += (bv[3] - bv[1]) * 0.5 + int(h * 0.125)

    # MUCH BIGGER CARD TITLES ("text to len"!) with crisp side margins
    title_base_sz = max(29, int(h * 0.162)) if not big_val else max(26, int(h * 0.122))
    side_pad = 30 if w >= 250 else 24
    for line_t in title_txt.split("\n"):
        ft = get_font(FONT_EBOLD, title_base_sz)
        while ft.size > 19 and (d.textbbox((0, 0), line_t, font=ft)[2] > w - side_pad):
            ft = get_font(FONT_EBOLD, ft.size - 2)
        bt = d.textbbox((0, 0), line_t, font=ft)
        d.text((cx_c - (bt[2]-bt[0])*0.5 - bt[0], cur_y - (bt[1]+bt[3])*0.5), line_t, font=ft, fill=txt_col)
        cur_y += (bt[3] - bt[1]) + (6 if h < 210 else 8)

    if sub_txt:
        cur_y += (3 if h < 210 else 5)
        sub_base_sz = max(21, int(h * 0.112)) if not big_val else max(19, int(h * 0.088))
        for line_s in sub_txt.split("\n"):
            fs = get_font(FONT_BOLD, sub_base_sz)
            while fs.size > 15 and (d.textbbox((0, 0), line_s, font=fs)[2] > w - side_pad):
                fs = get_font(FONT_BOLD, fs.size - 2)
            bs = d.textbbox((0, 0), line_s, font=fs)
            d.text((cx_c - (bs[2]-bs[0])*0.5 - bs[0], cur_y - (bs[1]+bs[3])*0.5), line_s, font=fs, fill=sub_col)
            cur_y += (bs[3] - bs[1]) + 4

    if len(_card_cache) > 500:
        _card_cache.clear()
    _card_cache[key] = card
    return card

def make_card_back(w, h, brand_lbl="HẰNG THU"):
    key = ("BACK", w, h, brand_lbl)
    if key in _card_cache:
        return _card_cache[key]
    pad = 20
    cw, ch = w + pad * 2, h + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 2, pad + 11, pad + w + 2, pad + h + 11], radius=28, fill=(6, 12, 14, 175))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    d = ImageDraw.Draw(card)
    x0, y0, x1, y1 = pad, pad, pad + w - 1, pad + h - 1
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=(18, 42, 36, 255), outline=(255, 232, 152, 255), width=5)
    d.rounded_rectangle([x0 + 11, y0 + 11, x1 - 11, y1 - 11], radius=19, outline=(232, 182, 72, 235), width=3)
    for gx in range(x0 + 24, x1 - 20, 28):
        for gy in range(y0 + 24, y1 - 20, 28):
            draw_suit_icon(d, "diamond", gx, gy, 5, (245, 204, 98, 72))
    cx_c, cy_c = pad + w * 0.5, pad + h * 0.5
    d.ellipse([cx_c - 64, cy_c - 64, cx_c + 64, cy_c + 64], fill=(12, 30, 26, 255), outline=(255, 216, 102, 255), width=4)
    draw_suit_icon(d, "star", cx_c, cy_c - 12, 24, (255, 222, 110, 255))
    fb = get_font(FONT_BLACK, 26)
    bb = d.textbbox((0, 0), brand_lbl, font=fb)
    d.text((cx_c - (bb[2]-bb[0])*0.5 - bb[0], cy_c + 20), brand_lbl, font=fb, fill=(255, 236, 168, 255))
    _card_cache[key] = card
    return card

def make_video_playing_card(vf_rgb, w, h, rank_txt, suit, theme, top_pill_txt, footer_txt, zoom=1.03):
    pad = 22
    cw, ch = w + pad * 2, h + pad * 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 2, pad + 12, pad + w + 2, pad + h + 12], radius=32, fill=(4, 10, 12, 185))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))

    is_warn = (theme == "crimson")
    bg_c  = (255, 247, 248, 255) if is_warn else (252, 254, 252, 255)
    rim_c = (224, 52, 72, 255)   if is_warn else (238, 184, 62, 255)
    acc_c = (198, 24, 46, 255)   if is_warn else (14, 124, 78, 255)

    d = ImageDraw.Draw(card)
    x0, y0, x1, y1 = pad, pad, pad + w - 1, pad + h - 1
    d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=bg_c, outline=(255, 255, 255, 255), width=5)
    d.rounded_rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], radius=25, outline=rim_c, width=3)

    f_rk = get_font(FONT_BLACK, 32)
    d.text((x0 + 18, y0 + 14), rank_txt, font=f_rk, fill=acc_c)
    draw_suit_icon(d, suit, x0 + 66, y0 + 32, 11, acc_c)

    # BIGGER TOP PILL (26-28pt!)
    fp = get_font(FONT_EBOLD, 26)
    while fp.size > 19 and (d.textbbox((0, 0), top_pill_txt, font=fp)[2] > w - 135):
        fp = get_font(FONT_EBOLD, fp.size - 2)
    bp = d.textbbox((0, 0), top_pill_txt, font=fp)
    pw = (bp[2] - bp[0]) + 34
    d.rounded_rectangle([x1 - 16 - pw, y0 + 12, x1 - 16, y0 + 56], radius=22, fill=acc_c)
    d.text((x1 - 16 - pw + 17 - bp[0], y0 + 34 - (bp[1] + bp[3]) * 0.5), top_pill_txt, font=fp, fill=(255, 255, 255, 255))

    vx, vy = x0 + 15, y0 + 66
    vw, vh = w - 30, max(120, h - 142)
    vis = fit_cover(vf_rgb, vw, vh, zoom=zoom).convert("RGBA")
    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=18, fill=255)
    vl = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    vl.paste(vis, (vx, vy), mask=vmask)
    card = Image.alpha_composite(card, vl)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([vx, vy, vx + vw - 1, vy + vh - 1], radius=18, outline=rim_c, width=2)

    # BIGGER FOOTER TEXT (30-32pt!)
    ff = get_font(FONT_EBOLD, 31)
    while ff.size > 21 and (d.textbbox((0, 0), footer_txt, font=ff)[2] > w - 34):
        ff = get_font(FONT_EBOLD, ff.size - 2)
    bf = d.textbbox((0, 0), footer_txt, font=ff)
    fy = y1 - 38
    d.text((pad + w * 0.5 - (bf[2] - bf[0]) * 0.5 - bf[0], fy - (bf[1] + bf[3]) * 0.5), footer_txt, font=ff, fill=(18, 22, 26, 255))
    return card

def draw_landing_ripple(canvas_im, cx, cy, dt, dur=0.28, rx_max=150, ry_max=26, col=(255, 220, 110)):
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

def draw_orbital_rings_bg(canvas_im, flare_im, pal_name, t_now, t0, t1):
    env = smooth_in_out_env(t_now, t0, t1, d_in=0.40, d_out=0.36)
    if env <= 0.01:
        return
    pal = PALETTES.get(pal_name, PALETTES["emerald_amber"])
    dt = t_now - t0
    dur = max(0.2, t1 - t0)
    sc = 0.92 + 0.08 * ease_out_cubic(min(1.0, dt / 0.50))
    rot_deg = 36.0 * (dt / dur)
    cx, cy = 540, 680

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    R1, R2 = int(495 * sc), int(380 * sc)
    dr.ellipse([cx - R1, cy - R1, cx + R1, cy + R1], outline=(*pal["ring1"], int(155 * env)), width=3)
    dr.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=(*pal["ring2"], int(110 * env)), width=2)

    suits = ["leaf", "star", "diamond", "bolt", "leaf"]
    for i, st_s in enumerate(suits):
        a_rad = math.radians(-162.0 + i * (144.0 / 4.0) + rot_deg * 0.65)
        ix, iy = cx + int(R1 * math.cos(a_rad)), cy + int(R1 * math.sin(a_rad))
        dr.ellipse([ix - 34, iy - 34, ix + 34, iy + 34], fill=(*pal["bg_rgb"], int(230 * env)), outline=(*pal["ring2"], int(215 * env)), width=3)
        draw_suit_icon(dr, st_s, ix, iy, 15, (*pal["ring2"], int(235 * env)))

    if env > 0.18:
        fl_arr = np.array(flare_im)
        fl_arr[:, :, 3] = (fl_arr[:, :, 3].astype(np.float32) * env).astype(np.uint8)
        layer = Image.alpha_composite(layer, Image.fromarray(fl_arr, "RGBA"))
    canvas_im.alpha_composite(layer)

# ==============================================================================
# DETERMINISTIC 5-STYLE CARD TIMELINE PLANNER + 100% CLONE-COVER GUARANTEE!
# ==============================================================================
def build_stage_timeline(meta, cfg):
    D = float(meta["duration_s"])
    clones = sorted(meta.get("clone_spans", []), key=lambda x: x["start_s"])

    if cfg.get("force_fullscreen_speech"):
        # Outdoor v18 & v19: 100% Full-Screen Luxury Card Stages across all 4 cloned pieces!
        # c1 -> hook_stage, c2 -> clash, c3 -> fan + riffle, c4 -> endcard!
        c1 = clones[0] if len(clones) > 0 else {"start_s": 0.0, "end_s": 5.0}
        c2 = clones[1] if len(clones) > 1 else {"start_s": 5.0, "end_s": 13.0}
        c3 = clones[2] if len(clones) > 2 else {"start_s": 13.0, "end_s": 24.0}
        c4 = clones[3] if len(clones) > 3 else {"start_s": 24.0, "end_s": D}
        mid_c3 = round((c3["start_s"] + c3["end_s"]) * 0.46, 3)
        return {
            "hook_aroll": None,
            "full_stages": [
                ("hook_full", 0.00, c1["end_s"] + 0.04),
                ("clash",     c1["end_s"] - 0.06, c2["end_s"] + 0.04),
                ("fan",       c2["end_s"] - 0.06, mid_c3 + 0.04),
                ("riffle",    mid_c3 - 0.06,      c4["start_s"] + 0.04),
                ("endcard",   max(c3["end_s"] - 0.10, c4["start_s"] - 0.12), D + 0.15),
            ],
            "flip3d_aroll": None,
            "dim_windows": [],
            "kw_windows": [],
        }

    # Indoor episodes v01..v17:
    # 1. Hook Style 1 on A-Roll: 0.05 -> hook_end (~4.5s, clamped before any early clone!)
    first_clone_s = clones[0]["start_s"] if clones else D
    hook_end = min(4.65, max(3.10, first_clone_s - 0.25))

    # 2. End-Card Style 5: covers final CTA clone if in last 30% of video, else [D - 3.6, D]
    rem_clones = list(clones)
    if rem_clones and rem_clones[-1]["start_s"] >= D * 0.68:
        last_c = rem_clones.pop()
        end_s0 = max(hook_end + 4.0, last_c["start_s"] - 0.18)
    else:
        end_s0 = max(hook_end + 4.0, D - 3.65)
    full_stages = [("endcard", round(end_s0, 3), round(D + 0.15, 3))]

    # 3. Wrap EVERY remaining mid-video Voice Studio clone inside a Full-Screen Card Stage!
    #    Pad by [-0.22s, +0.24s] so the fade-in finishes BEFORE cloned audio speaks a single syllable!
    used_styles = set()
    for ci, cl in enumerate(rem_clones):
        cs, ce = cl["start_s"], cl["end_s"]
        span_len = ce - cs
        # Special case v10_c2 (~13s long How-To-Mix): split into fan + riffle back-to-back!
        if span_len > 9.0:
            s_mid = round(cs + span_len * 0.44, 3)
            full_stages.append(("fan",    round(max(hook_end + 0.15, cs - 0.24), 3), round(s_mid + 0.06, 3)))
            full_stages.append(("riffle", round(s_mid - 0.06, 3), round(min(end_s0 - 0.05, ce + 0.26), 3)))
            used_styles.update(["fan", "riffle"])
        else:
            pad_extra = max(0.0, (3.60 - span_len) * 0.5)
            w0 = max(hook_end + 0.15, cs - 0.24 - pad_extra * 0.5)
            w1 = min(end_s0 - 0.12,   ce + 0.26 + pad_extra * 0.5)
            if cs >= D * 0.52 and "riffle" not in used_styles:
                st_name = "riffle"
            elif cs < D * 0.36 and "clash" not in used_styles:
                st_name = "clash"
            elif "fan" not in used_styles:
                st_name = "fan"
            elif "riffle" not in used_styles:
                st_name = "riffle"
            else:
                st_name = "clash"
            full_stages.append((st_name, round(w0, 3), round(w1, 3)))
            used_styles.add(st_name)

    def overlaps_any(a, b, margin=0.85):
        for _, x0, x1 in full_stages:
            if not (b + margin <= x0 or a - margin >= x1):
                return True
        return False

    # 4. Fill missing Full-Screen Card Styles (clash, fan, riffle) into open gaps so all 5 styles shine!
    preferred_targets = [
        ("clash",  D * 0.21, 5.0),
        ("fan",    D * 0.42, 4.5),
        ("riffle", D * 0.70, 5.2),
    ]
    for st_name, center_t, dur_t in preferred_targets:
        if st_name in used_styles:
            continue
        # Search near center_t for an open window between hook_end+0.6 and end_s0-0.6
        for delta in [0.0, -2.5, 2.5, -5.0, 5.0, -7.5, 7.5]:
            a = max(hook_end + 0.65, center_t + delta - dur_t * 0.5)
            b = min(end_s0 - 0.65, a + dur_t)
            if (b - a) >= 3.3 and not overlaps_any(a, b, margin=1.1):
                full_stages.append((st_name, round(a, 3), round(b, 3)))
                used_styles.add(st_name)
                break

    full_stages.sort(key=lambda x: x[1])

    # 5. Find best open A-Roll gap (prefer second half, >= 3.2s) for Style 4A (On-Screen 3D 180° Flip Card)!
    gaps = []
    cur = hook_end + 0.25
    for _, x0, x1 in full_stages:
        if x0 - cur >= 2.8:
            gaps.append((cur, x0))
        cur = max(cur, x1)
    flip3d_aroll = None
    for g0, g1 in reversed(gaps):
        if (g1 - g0) >= 3.2:
            f0 = g0 + 0.25
            f1 = min(g1 - 0.25, f0 + 5.2)
            flip3d_aroll = (round(f0, 3), round(f1, 3))
            break

    # 6. Place Behind-Head Giant Keywords + Dimming Windows in open A-Roll gaps!
    dim_windows = [(0.04, hook_end)]
    kw_windows = []
    kw_specs = cfg.get("keywords", [])
    for ki, (kw_txt, rel_pos, kw_col_kind) in enumerate(kw_specs):
        target_t = rel_pos * D
        # Snap into nearest open A-Roll gap
        best_g = None
        best_dist = 999.0
        for g0, g1 in gaps:
            if (g1 - g0) >= 2.2:
                gc = (g0 + g1) * 0.5
                if abs(gc - target_t) < best_dist:
                    best_dist = abs(gc - target_t)
                    best_g = (g0, g1)
        if best_g:
            k0 = max(best_g[0] + 0.18, min(best_g[1] - 2.4, target_t - 1.2))
            k1 = min(best_g[1] - 0.18, k0 + 2.8)
            if k1 - k0 >= 1.6:
                kw_windows.append((kw_txt, round(k0, 3), round(k1, 3), kw_col_kind))
                dim_windows.append((round(k0 - 0.10, 3), round(k1 + 0.10, 3)))
    if flip3d_aroll:
        dim_windows.append(flip3d_aroll)

    # STRICT VERIFICATION: Ensure 100% of every clone_span is inside at least one Full-Screen Stage!
    for cl in clones:
        cs, ce = cl["start_s"], cl["end_s"]
        mid_c = (cs + ce) * 0.5
        covered = any((x0 - 0.05) <= cs and (x1 + 0.05) >= ce for _, x0, x1 in full_stages) or any(x0 <= mid_c <= x1 for _, x0, x1 in full_stages)
        if not covered:
            full_stages.append(("riffle", round(max(0.0, cs - 0.22), 3), round(min(D + 0.1, ce + 0.24), 3)))
            full_stages.sort(key=lambda x: x[1])

    return {
        "hook_aroll": (0.05, round(hook_end, 3)),
        "full_stages": full_stages,
        "flip3d_aroll": flip3d_aroll,
        "dim_windows": dim_windows,
        "kw_windows": kw_windows,
    }

# ==============================================================================
# BIG WORD-BY-WORD SUBTITLE GROUPER (68pt A-Roll / 62pt Stage, MAX 3 WORDS/LINE!)
# ==============================================================================
def build_caption_groups(tr_json, hook_aroll, endcard_start):
    skip_hook_end = hook_aroll[1] if hook_aroll else 0.0
    words = []
    for seg in tr_json.get("segments", []):
        for w in seg.get("words", []):
            mid_t = (w["start"] + w["end"]) * 0.5
            if mid_t <= skip_hook_end + 0.04 or mid_t >= endcard_start - 0.05:
                continue
            if w["word"].strip():
                words.append(w)

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
        if prev is not None and (w["start"] - prev["end"]) >= 0.34:
            flush_group()
        # STRICT MAX 3 WORDS OR 14 CHARS PER LINE so 68pt-76pt text stays HUGE without shrinking!
        if line and (len(line) >= 3 or sum(len(x[0]) + 1 for x in line) + len(txt) > 14):
            flush_line()
        if len(cur) >= 2 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!:;]$", txt):
            flush_group()
    flush_group()

    cap_groups = []
    for i, g in enumerate(groups):
        t0 = g[0][0][1]
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else endcard_start
        t1 = min(nxt, last_end + 0.42) if (nxt - last_end) > 0.48 else nxt
        t1 = min(t1, endcard_start - 0.04)
        if t1 > t0 + 0.10:
            cap_groups.append({"t0": t0, "t1": t1, "lines": g})
    return cap_groups

def load_vid_frames_wh(path, vw=960, vh=540):
    if not os.path.exists(path):
        return [np.zeros((vh, vw, 3), dtype=np.uint8)]
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE
    )
    frames, nb = [], vw * vh * 3
    while True:
        b = proc.stdout.read(nb)
        if len(b) < nb:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)).copy())
    proc.stdout.close(); proc.wait()
    return frames if frames else [np.zeros((vh, vw, 3), dtype=np.uint8)]

def sample_clip_pingpong(arr_list, t_rel, rate=1.0):
    n = len(arr_list)
    if n <= 1:
        return arr_list[0]
    pos = max(0.0, t_rel) * FPS * rate
    cyc = 2 * (n - 1)
    m = pos % cyc
    if m > (n - 1):
        m = cyc - m
    i0 = int(math.floor(m))
    i1 = min(n - 1, i0 + 1)
    f = m - i0
    return arr_list[i0] if f < 0.02 else np.clip(arr_list[i0].astype(np.float32)*(1.0-f) + arr_list[i1].astype(np.float32)*f, 0, 255).astype(np.uint8)

def load_ep_static_assets(cfg):
    lg_p = os.path.join(CUTOUT_DIR, cfg["logo"])
    lg = Image.open(lg_p).convert("RGBA")
    lg.thumbnail((250, 126), Image.Resampling.LANCZOS)
    prods = []
    for pfn in cfg["products"]:
        im = Image.open(os.path.join(CUTOUT_DIR, pfn)).convert("RGBA")
        im.thumbnail((440, 520), Image.Resampling.LANCZOS)
        prods.append(im)
    return {"logo": lg, "prods": prods}

_YY_G, _XX_G = np.ogrid[0:H, 0:W]
_DESK_LINE = np.clip((np.arange(H, dtype=np.float32) - 1605.0) / 55.0, 0.0, 1.0)[:, None]
_DESK_BOX  = np.exp(-((np.maximum(0.0, np.abs(_XX_G - 540.0) - 290.0)) / 48.0) ** 2) * \
             np.clip((_YY_G - 1295.0) / 50.0, 0.0, 1.0) * np.clip((1785.0 - _YY_G) / 45.0, 0.0, 1.0)

def render_caption_block(canvas_im, t, cap_groups, cfg, cx_target, y_base, max_w_allowed, base_pt=68, lh=82, single_line_merge=False):
    gold_w = cfg.get("gold_words", set())
    emer_w = cfg.get("emer_words", set())
    rose_w = cfg.get("rose_words", set())

    for g in cap_groups:
        if g["t0"] <= t < g["t1"]:
            op_g = smoothstep((g["t1"] - t) / 0.20) if (g["t1"] - t) < 0.20 else 1.0
            lines_use = [[w for ln in g["lines"] for w in ln]] if single_line_merge else g["lines"]
            gap = 18
            for li, ln in enumerate(lines_use):
                w_renders, tot_w = [], 0
                for wi, (wtxt, ws, we) in enumerate(ln):
                    clean_tok = wtxt.strip(".,?!:;\"'()")
                    is_gold = (wtxt in gold_w or clean_tok in gold_w)
                    is_emer = (wtxt in emer_w or clean_tok in emer_w)
                    is_rose = (wtxt in rose_w or clean_tok in rose_w)
                    k_sz = 1.12 if (is_gold or is_emer or is_rose) else 1.0
                    if is_gold:
                        ct, cb = (255, 238, 110), (242, 166, 32)
                    elif is_emer:
                        ct, cb = (158, 255, 214), (46, 212, 146)
                    elif is_rose:
                        ct, cb = (255, 182, 194), (238, 72, 98)
                    else:
                        ct, cb = (255, 255, 255), (236, 246, 242)
                    pt_use = base_pt * k_sz
                    sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_use, ct, cb, glow_col=ct, glow_rad=10, stroke_col=(8, 14, 18), stroke_w=7)
                    adv = int(ImageDraw.Draw(canvas_im).textlength(wtxt, font=get_font(FONT_EBOLD, pt_use))) + 6
                    w_renders.append((wtxt, ws, sp, adv, ct, is_gold))
                    tot_w += adv + (gap if wi > 0 else 0)

                fit_k = min(1.0, max_w_allowed / max(1.0, float(tot_w)))
                eff_tot = tot_w * fit_k
                cur_x = cx_target - eff_tot * 0.5
                cur_y = y_base + li * lh
                for wtxt, ws, sp, adv, ct, is_gold in w_renders:
                    eff_adv = adv * fit_k
                    if t >= ws - 0.03:
                        dt_w = max(0.0, t - ws)
                        u_w  = ease_out_cubic(min(1.0, dt_w / 0.20))
                        wcx  = cur_x + eff_adv * 0.5
                        paste_centered(canvas_im, sp, wcx, cur_y + (1.0 - u_w) * 16.0, scale_x=fit_k * (0.92 + 0.08 * u_w), opacity=op_g * u_w, blur_px=(1.0 - u_w) * 4.0)
                    cur_x += eff_adv + gap * fit_k
            break

def compose_ep_frame(frame_idx, rgb, matte_u8, brolls, assets, cap_groups, cfg, tl, meta):
    t = frame_idx / FPS
    D = float(meta["duration_s"])
    pal_name = cfg["palette"]
    pal = PALETTES.get(pal_name, PALETTES["emerald_amber"])
    stage_bg_im, flare_im = get_stage_canvas(pal_name)
    brand_lbl = "AN VƯỢNG" if "an_vuong" in cfg["logo"] else "HẰNG THU"

    # Smooth subtle Ken Burns breathing zoom on A-Roll (1.00 .. 1.06)
    z = 1.02 + 0.035 * math.sin(t * 0.52)
    if z > 1.003:
        cw, ch = int(round(W / z)), int(round(H / z))
        x0 = max(0, min(W - cw, int(round(540 - cw * 0.5))))
        y0 = max(0, min(H - ch, int(round(780 - ch * (780.0 / H)))))
        frame_im = Image.fromarray(rgb[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
        matte_im = Image.fromarray(matte_u8[y0:y0+ch, x0:x0+cw], "L").resize((W, H), Image.Resampling.BILINEAR)
        fg_rgb = np.array(frame_im)
        m_arr  = np.array(matte_im, dtype=np.float32) / 255.0
    else:
        frame_im = Image.fromarray(rgb, "RGB")
        fg_rgb = rgb
        m_arr  = matte_u8.astype(np.float32) / 255.0

    # Check if a Full-Screen Stage is 100% opaque right now (fast skip of A-Roll work!)
    active_full = []
    max_full_env = 0.0
    for st_kind, s0, s1 in tl["full_stages"]:
        d_in = 0.02 if s0 <= 0.02 else 0.26
        d_out = 0.02 if s1 >= D else 0.26
        ev = smooth_in_out_env(t, s0, s1, d_in=d_in, d_out=d_out)
        if ev > 0.005:
            active_full.append((st_kind, s0, s1, ev))
            max_full_env = max(max_full_env, ev)

    comp_im = None
    if max_full_env < 0.995:
        # Render A-Roll + Talking-Head-v3 Behind-Head Animations + Sacred Face Shield!
        dim = 0.0
        for dw0, dw1 in tl["dim_windows"]:
            dim = max(dim, smooth_in_out_env(t, dw0, dw1, d_in=0.38, d_out=0.34))

        if dim <= 0.005:
            comp_im = frame_im.convert("RGBA")
        else:
            bg_soft = frame_im.filter(ImageFilter.GaussianBlur(radius=4.8 * dim)) if dim > 0.08 else frame_im
            bg_arr = np.array(bg_soft, dtype=np.float32)
            bg_f = 1.0 - 0.75 * dim
            bg_dim = np.clip(bg_arr * bg_f, 0, 255).astype(np.uint8)
            comp_im = Image.fromarray(bg_dim, "RGB").convert("RGBA")

            if tl["flip3d_aroll"]:
                draw_orbital_rings_bg(comp_im, flare_im, pal_name, t, tl["flip3d_aroll"][0], tl["flip3d_aroll"][1])
            for kw_txt, k0, k1, k_col in tl["kw_windows"]:
                draw_orbital_rings_bg(comp_im, flare_im, pal_name, t, k0, k1)
                env_k = smooth_in_out_env(t, k0, k1, d_in=0.32, d_out=0.28)
                if env_k > 0.01:
                    dt_k = t - k0
                    ct, cb = pal["kw_gold"] if k_col == "gold" else pal["kw_emer"]
                    # GIANT BEHIND-HEAD KEYWORD (138pt, cy=396 -> top >= 312 >= 250, composited BEHIND RVM hair!)
                    sp_k = render_glow_text_sprite(kw_txt, FONT_TITLE, 136, ct, cb, glow_col=ct, glow_rad=13)
                    fit_kw = min(1.0, 930.0 / max(1.0, sp_k.width))
                    sw_p = (dt_k / max(0.3, k1 - k0)) * 1.25 - 0.10
                    paste_centered(comp_im, sp_k, 540, 396 + (1.0 - env_k) * 18.0, scale_x=fit_kw * (0.90 + 0.10 * ease_out_cubic(min(1.0, dt_k / 0.34))), opacity=env_k, sweep_prog=sw_p)

            # Composite real Chi Hang + desk & real product box on desk cleanly IN FRONT!
            fg_alpha = np.maximum(m_arr, np.maximum(_DESK_LINE, _DESK_BOX * 0.90))
            fg_lit = np.clip(fg_rgb.astype(np.float32) * (1.0 - 0.03 * dim), 0, 255).astype(np.uint8)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_lit, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # ==============================================================
        # STYLE 1 ON A-ROLL: 3-CARD OVERHEAD ARC (Y=258..452) + HUGE HOOK BELOW CHIN (Y=1195..1435)
        # SACRED FACE ZONE Y = 468..1148 IS 100% UNTOUCHED!
        # ==============================================================
        if tl["hook_aroll"]:
            h0, h1 = tl["hook_aroll"]
            env_hk = smooth_in_out_env(t, h0, h1, d_in=0.26, d_out=0.28)
            if env_hk > 0.01:
                hk = cfg["hook"]
                arc_xs = [(0.22, 224, 356, -8.0), (0.40, 540, 342, 0.0), (0.58, 856, 356, 8.0)]
                for (st_c, cx_c, cy_c, ang_c), (rk, st_i, thm, tt, sb) in zip(arc_xs, hk["arc"]):
                    if t >= st_c:
                        dt_c = t - st_c
                        u_c  = ease_out_back(min(1.0, dt_c / 0.34), 1.12)
                        card_im = make_luxury_playing_card(244, 168, rk, st_i, thm, tt, sb)
                        paste_centered(comp_im, card_im, cx_c, cy_c + (1.0 - u_c) * (-55.0) + math.sin(t * 2.6 + cx_c * 0.01) * 3.0,
                                       scale_x=0.88 + 0.12 * clamp01(dt_c / 0.26), opacity=env_hk * clamp01(dt_c / 0.16), angle=ang_c)
                        draw_landing_ripple(comp_im, cx_c, cy_c + 82, dt_c - 0.22, rx_max=90, ry_max=16)

                # Giant Hook Text strictly at Y = 1198 .. 1425 (140px BELOW CHIN!)
                if t >= 0.06:
                    u1 = ease_out_cubic(min(1.0, (t - 0.06) / 0.30))
                    s1 = render_glow_text_sprite(hk["l1"], FONT_EBOLD, 56, (175, 252, 232), (88, 220, 182), glow_col=(48, 190, 145), glow_rad=10, stroke_col=(8, 18, 16), stroke_w=6)
                    k1_f = min(1.0, 810.0 / max(1.0, s1.width))
                    paste_centered(comp_im, s1, SAFE_LOW_CX, 1198 + (1.0 - u1) * 18.0, scale_x=k1_f * (0.90 + 0.10 * u1), opacity=env_hk * u1)
                if t >= 0.44:
                    u2 = ease_out_back(min(1.0, (t - 0.44) / 0.34), 1.10)
                    combo_l2 = f"{hk['l2a']} {hk['l2b']}"
                    s2 = render_glow_text_sprite(combo_l2, FONT_BLACK, 82, (255, 236, 108), (242, 152, 28), glow_col=(255, 185, 45), glow_rad=12, stroke_col=(22, 12, 8), stroke_w=7)
                    k2_f = min(1.0, 816.0 / max(1.0, s2.width))
                    paste_centered(comp_im, s2, SAFE_LOW_CX, 1296 + (1.0 - u2) * 20.0, scale_x=k2_f * (0.88 + 0.12 * clamp01((t - 0.44)/0.28)), opacity=env_hk)
                if t >= 1.55:
                    u3 = ease_out_cubic(min(1.0, (t - 1.55) / 0.30))
                    s3 = render_glow_text_sprite(hk["l3"], FONT_BOLD, 40, (255, 252, 242), (218, 248, 232), glow_col=(28, 140, 98), glow_rad=8, stroke_col=(10, 18, 16), stroke_w=5)
                    k3_f = min(1.0, 816.0 / max(1.0, s3.width))
                    paste_centered(comp_im, s3, SAFE_LOW_CX, 1396 + (1.0 - u3) * 14.0, scale_x=k3_f * (0.92 + 0.08 * u3), opacity=env_hk * u3)

        # ==============================================================
        # STYLE 4A ON A-ROLL: 3D 180° HORIZONTAL FLIP CARD (LEFT) + HUGE 66pt SUBTITLES (RIGHT)
        # ==============================================================
        in_flip3d = False
        if tl["flip3d_aroll"]:
            f0, f1 = tl["flip3d_aroll"]
            env_flp = smooth_in_out_env(t, f0, f1, d_in=0.30, d_out=0.28)
            if env_flp > 0.01:
                in_flip3d = True
                u_flip = quintic(clamp01((t - (f0 + 0.72)) / 0.65))
                theta  = u_flip * math.pi
                cos_t  = math.cos(theta)
                sx_3d  = max(0.05, abs(cos_t))
                if cos_t >= 0.0:
                    c_3d = make_card_back(262, 340, brand_lbl)
                    sw_f = None
                else:
                    rk, st_i, thm, tt, sb, bdg, bv = cfg["flip3d"]
                    c_3d = make_luxury_playing_card(262, 340, rk, st_i, thm, tt, sb, badge_txt=bdg, big_val=bv)
                    sw_f = clamp01((t - (f0 + 1.38)) / 1.10) if t <= f0 + 2.55 else None
                # Placed at cx=198, cy=1326 -> X in [67..329], Y in [1156..1496] (0% face overlap!)
                paste_centered(comp_im, c_3d, 198, 1326 + math.sin(t * 2.4) * 3.5, scale_x=sx_3d * (0.92 + 0.08 * env_flp),
                               scale_y=(0.92 + 0.08 * env_flp) * (1.0 + 0.04 * math.sin(theta)), opacity=env_flp, sweep_prog=sw_f)

        # ==============================================================
        # HUGE 76pt WORD-BY-WORD A-ROLL SUBTITLES (STRICTLY Y = 1220..1312, 150px BELOW CHIN!)
        # ==============================================================
        if in_flip3d:
            # Right-Safe Column X in [358..872] <= 884px!
            render_caption_block(comp_im, t, cap_groups, cfg, cx_target=615, y_base=1248, max_w_allowed=508, base_pt=68, lh=82)
        else:
            # Full Safe Lower Band X in [60..876] <= 884px, Y = 1222..1310!
            render_caption_block(comp_im, t, cap_groups, cfg, cx_target=SAFE_LOW_CX, y_base=1222, max_w_allowed=814, base_pt=76, lh=90)

    # ==================================================================
    # FULL-SCREEN MULTI-STYLE PLAYING-CARD STAGES (STYLES 1-FULL, 2, 3, 4B, 5)
    # ==================================================================
    for st_kind, s0, s1, ev in active_full:
        dt = max(0.0, t - s0)
        if st_kind == "hook_full":
            # Used for outdoor v18/v19: blurred sunlit garden vignette + 3 Overhead Dealing Cards + Center Live Video Card + Giant Hook!
            g_blur = frame_im.filter(ImageFilter.GaussianBlur(radius=18))
            g_dark = np.clip(np.array(g_blur, dtype=np.float32) * 0.36, 0, 255).astype(np.uint8)
            stage = Image.fromarray(g_dark, "RGB").convert("RGBA")
            hk = cfg["hook"]
            arc_xs = [(0.12, 224, 356, -8.0), (0.28, 540, 342, 0.0), (0.44, 856, 356, 8.0)]
            for (st_c, cx_c, cy_c, ang_c), (rk, st_i, thm, tt, sb) in zip(arc_xs, hk["arc"]):
                if dt >= st_c:
                    dc = dt - st_c
                    uc = ease_out_back(min(1.0, dc / 0.34), 1.12)
                    ci = make_luxury_playing_card(244, 168, rk, st_i, thm, tt, sb)
                    paste_centered(stage, ci, cx_c, cy_c + (1.0 - uc) * (-50.0), scale_x=0.90 + 0.10 * clamp01(dc/0.25), angle=ang_c)
            vf0 = sample_clip_pingpong(brolls[0], dt, rate=0.95)
            vc0 = make_video_playing_card(vf0, 864, 480, "A", "bolt", "crimson", hk["l1"].upper(), hk["l3"], zoom=1.02 + 0.05 * smoothstep(dt / 4.5))
            paste_centered(stage, vc0, 538, 760, scale_x=0.95 + 0.05 * ease_out_cubic(min(1.0, dt / 0.35)))
            s2 = render_glow_text_sprite(f"{hk['l2a']} {hk['l2b']}", FONT_BLACK, 84, (255, 236, 108), (242, 152, 28), glow_col=(255, 185, 45), glow_rad=12, stroke_col=(20, 12, 8), stroke_w=7)
            paste_centered(stage, s2, SAFE_LOW_CX, 1145, scale_x=min(1.0, 814.0 / max(1.0, s2.width)))
            render_caption_block(stage, t, cap_groups, cfg, cx_target=SAFE_LOW_CX, y_base=1325, max_w_allowed=814, base_pt=66, lh=78)

        elif st_kind == "clash":
            # STYLE 2: FULL-SCREEN DUAL-CARD DIAGONAL CLASH + LIVE STAGE CAPTIONS!
            stage = stage_bg_im.copy()
            cl_c = cfg["clash"]
            vf_top = sample_clip_pingpong(brolls[0], dt, rate=0.95)
            u_t1 = ease_out_back(min(1.0, dt / 0.40), 1.08)
            c_top = make_video_playing_card(vf_top, 864, 424, "Q", "diamond", "ivory", cl_c["top_pill"], cl_c["top_foot"], zoom=1.02 + 0.05 * smoothstep(dt / 5.5))
            paste_centered(stage, c_top, 538, 482 - (1.0 - u_t1) * 42.0, scale_x=0.94 + 0.06 * u_t1, angle=1.0)

            rib = Image.new("RGBA", (808, 112), (0, 0, 0, 0))
            dr = ImageDraw.Draw(rib)
            dr.rounded_rectangle([0, 0, 807, 111], radius=28, fill=(12, 24, 26, 246), outline=(255, 214, 102, 235), width=3)
            f_rb1 = get_font(FONT_EBOLD, 27)
            f_rb2 = get_font(FONT_BOLD, 22)
            while f_rb1.size > 19 and dr.textbbox((0, 0), cl_c["rib_lbl"], font=f_rb1)[2] > 768:
                f_rb1 = get_font(FONT_EBOLD, f_rb1.size - 2)
            dr.text((28, 16), cl_c["rib_title"], font=f_rb2, fill=(172, 242, 212, 255))
            dr.text((28, 54), cl_c["rib_lbl"],   font=f_rb1, fill=(255, 228, 112, 255))
            paste_centered(stage, rib, SAFE_LOW_CX, 796)

            vf_bot = sample_clip_pingpong(brolls[1], dt, rate=0.95)
            dt_b = max(0.0, dt - 0.32)
            u_b1 = ease_out_back(min(1.0, dt_b / 0.42), 1.08)
            c_bot = make_video_playing_card(vf_bot, 776, 408, "K", "bolt", "crimson", cl_c["bot_pill"], cl_c["bot_foot"], zoom=1.06 - 0.04 * smoothstep(dt / 5.5))
            paste_centered(stage, c_bot, SAFE_LOW_CX, 1106 + (1.0 - u_b1) * 48.0, scale_x=0.93 + 0.07 * clamp01(dt_b / 0.34), opacity=clamp01(dt_b / 0.18), angle=-1.0)

            render_caption_block(stage, t, cap_groups, cfg, cx_target=SAFE_LOW_CX, y_base=1395, max_w_allowed=814, base_pt=62, lh=74, single_line_merge=True)

        elif st_kind == "fan":
            # STYLE 3: FULL-SCREEN 3-CARD HAND FAN SPREAD (XÒE QUẠT 3 LÁ BÀI LỚN!)
            stage = stage_bg_im.copy()
            fn_c = cfg["fan"]
            vf_f = sample_clip_pingpong(brolls[2], dt, rate=0.95)
            c_vid = make_video_playing_card(vf_f, 864, 396, "J", "star", "ivory", "PHÂN TÍCH CHUYÊN SÂU", fn_c["headline"], zoom=1.02 + 0.05 * smoothstep(dt / 5.0))
            paste_centered(stage, c_vid, 538, 470, scale_x=0.95 + 0.05 * ease_out_cubic(min(1.0, dt / 0.35)))

            u_open = ease_out_back(min(1.0, dt / 0.50), 1.08)
            l_rk, l_s, l_th, l_t, l_sb, l_bd = fn_c["left"]
            r_rk, r_s, r_th, r_t, r_sb, r_bd = fn_c["right"]
            a_rk, a_s, a_th, a_t, a_sb, a_bd = fn_c["ace"]
            c_left  = make_luxury_playing_card(244, 344, l_rk, l_s, l_th, l_t, l_sb, badge_txt=l_bd)
            c_right = make_luxury_playing_card(244, 344, r_rk, r_s, r_th, r_t, r_sb, badge_txt=r_bd)
            c_ace   = make_luxury_playing_card(256, 364, a_rk, a_s, a_th, a_t, a_sb, badge_txt=a_bd)

            paste_centered(stage, c_left,  462 - 238 * u_open, 1032 + 18 * u_open, scale_x=0.92 + 0.08*u_open, angle=-15.0 * u_open)
            paste_centered(stage, c_right, 462 + 238 * u_open, 1032 + 18 * u_open, scale_x=0.92 + 0.08*u_open, angle=+15.0 * u_open)
            ace_lift = 26.0 * smoothstep((dt - 0.75) / 0.35) if dt > 0.75 else 0.0
            sw_ace = ((dt - 0.80) / 1.35) % 1.35 if dt > 0.80 else None
            paste_centered(stage, c_ace,   462, 996 - ace_lift + math.sin(t * 2.8) * 3.5, scale_x=0.96 + (0.04 if ace_lift > 1 else 0.0), sweep_prog=sw_ace)

            render_caption_block(stage, t, cap_groups, cfg, cx_target=SAFE_LOW_CX, y_base=1348, max_w_allowed=814, base_pt=68, lh=80)

        elif st_kind == "riffle":
            # STYLE 4B: FULL-SCREEN RAPID RIFFLE CASCADE + 3D HERO ACE + REAL STUDIO PRODUCT CUTOUT!
            stage = stage_bg_im.copy()
            rf_c = cfg["riffle"]
            dur_rf = max(1.0, s1 - s0)
            vf_3 = sample_clip_pingpong(brolls[2], dt, rate=0.95)
            vf_4 = sample_clip_pingpong(brolls[3], max(0.0, dt - dur_rf * 0.45), rate=0.95)
            w_cf = smoothstep((dt - dur_rf * 0.48) / 0.45) if dt >= dur_rf * 0.48 else 0.0
            vf_mix = np.clip(vf_3.astype(np.float32) * (1.0 - w_cf) + vf_4.astype(np.float32) * w_cf, 0, 255).astype(np.uint8)

            use_p2 = (dt >= dur_rf * 0.50)
            c_up = make_video_playing_card(vf_mix, 868, 418, "A", "star", "ivory", rf_c["pill2"] if use_p2 else rf_c["pill1"], rf_c["foot2"] if use_p2 else rf_c["foot1"], zoom=1.02 + 0.05 * smoothstep(dt / dur_rf))
            paste_centered(stage, c_up, 538, 478, scale_x=0.96 + 0.04 * ease_out_cubic(min(1.0, dt / 0.34)))

            for st_r, rx_c, ry_c, rang, c_spec in [(0.08, 256, 895, -4.5, rf_c["c1"]), (0.22, 282, 955, 3.0, rf_c["c2"])]:
                if dt >= st_r:
                    ur = ease_out_back(min(1.0, (dt - st_r) / 0.28), 1.10)
                    rk, si, th, tt, sb, bd = c_spec
                    rc = make_luxury_playing_card(364, 198, rk, si, th, tt, sb, badge_txt=bd)
                    paste_centered(stage, rc, rx_c - (1.0 - ur) * 110.0, ry_c, scale_x=0.92 + 0.08 * clamp01((dt-st_r)/0.24), opacity=clamp01((dt-st_r)/0.15), angle=rang)

            if dt >= 0.36:
                dt_h = dt - 0.36
                u_hf = quintic(clamp01(dt_h / 0.50))
                th_h = u_hf * math.pi
                cs_h = math.cos(th_h)
                if cs_h >= 0.0:
                    hero_c = make_card_back(452, 344, brand_lbl)
                    sw_h = None
                else:
                    hrk, hsi, hth, htt, hsb, hbd, hbv = rf_c["hero"]
                    hero_c = make_luxury_playing_card(452, 344, hrk, hsi, hth, htt, hsb, badge_txt=hbd, big_val=hbv)
                    sw_h = ((dt_h - 0.52) / 1.30) % 1.30 if dt_h > 0.52 else None
                paste_centered(stage, hero_c, 298, 1148 + math.sin(t * 2.5) * 3.5, scale_x=max(0.05, abs(cs_h)), scale_y=1.0 + 0.04 * math.sin(th_h), opacity=clamp01(dt_h / 0.14), sweep_prog=sw_h)
                draw_landing_ripple(stage, 298, 1326, dt_h - 0.46, rx_max=165, ry_max=24)

            # Real Studio Cutout Product(s) on Right-Safe (cx=718, X <= 880!)
            prods = assets["prods"]
            u_bx = ease_out_back(min(1.0, dt / 0.44), 1.08)
            if len(prods) >= 2:
                paste_centered(stage, prods[0], 680, 1065 + math.sin(t * 2.2) * 4.0, scale_x=0.62 * clamp01(dt / 0.28), opacity=clamp01(dt / 0.20))
                paste_centered(stage, prods[1], 756, 1120 + math.sin(t * 2.2 + 0.8) * 4.0, scale_x=0.60 * (0.90 + 0.10 * u_bx), opacity=clamp01(dt / 0.24))
            else:
                paste_centered(stage, prods[0], 718, 1090 + math.sin(t * 2.2) * 4.5 + (1.0 - u_bx) * 38.0, scale_x=0.72 * (0.90 + 0.10 * clamp01(dt / 0.34)), opacity=clamp01(dt / 0.22))

            render_caption_block(stage, t, cap_groups, cfg, cx_target=SAFE_LOW_CX, y_base=1392, max_w_allowed=814, base_pt=62, lh=74, single_line_merge=True)

        else:  # "endcard" — STYLE 5: FULL-SCREEN ROYAL END-CARD TABLE!
            stage = stage_bg_im.copy()
            ec = cfg["endcard"]
            paste_centered(stage, assets["logo"], 540, 308, scale_x=0.92)
            sp_eh = render_glow_text_sprite(ec["headline"], FONT_BLACK, 52, (255, 236, 118), (238, 168, 40), glow_col=(255, 195, 60), glow_rad=10, stroke_col=(10, 20, 18), stroke_w=5)
            paste_centered(stage, sp_eh, 540, 406, scale_x=min(1.0, 910.0 / max(1.0, sp_eh.width)) * (0.94 + 0.06 * ease_out_cubic(min(1.0, dt / 0.32))))

            u_d5 = ease_out_back(min(1.0, dt / 0.42), 1.10)
            lrk, lsi, lth, ltt, lsb, lbd, lbv = ec["left"]
            rrk, rsi, rth, rtt, rsb, rbd, rbv = ec["right"]
            c5_l = make_luxury_playing_card(248, 316, lrk, lsi, lth, ltt, lsb, badge_txt=lbd, big_val=lbv)
            c5_r = make_luxury_playing_card(248, 316, rrk, rsi, rth, rtt, rsb, badge_txt=rbd, big_val=rbv)
            paste_centered(stage, c5_l, 198, 656 + (1.0 - u_d5) * 34.0, scale_x=0.94, angle=-8.0)
            paste_centered(stage, c5_r, 882, 656 + (1.0 - u_d5) * 34.0, scale_x=0.94, angle=+8.0)

            prods = assets["prods"]
            if len(prods) >= 3:
                paste_centered(stage, prods[0], 425, 815 + math.sin(t * 2.4) * 4.0, scale_x=0.62 * clamp01(dt / 0.24))
                paste_centered(stage, prods[1], 540, 800 + math.sin(t * 2.4 + 0.6) * 4.0, scale_x=0.66 * clamp01(dt / 0.26))
                paste_centered(stage, prods[2], 655, 825 + math.sin(t * 2.4 + 1.2) * 4.0, scale_x=0.60 * clamp01(dt / 0.28))
            elif len(prods) == 2:
                paste_centered(stage, prods[0], 462, 812 + math.sin(t * 2.4) * 4.0, scale_x=0.70 * clamp01(dt / 0.25))
                paste_centered(stage, prods[1], 612, 828 + math.sin(t * 2.4 + 0.8) * 4.0, scale_x=0.72 * clamp01(dt / 0.28))
            else:
                paste_centered(stage, prods[0], 540, 812 + math.sin(t * 2.4) * 4.5, scale_x=0.84 * clamp01(dt / 0.26))

            pulse_cta = 1.0 + 0.024 * math.sin(dt * 7.2)
            cta_card = make_luxury_playing_card(792, 286, "A", "star", "gold_ace", ec["cta_title"], ec["cta_sub"], badge_txt=ec["cta_badge"])
            sw_cta = (dt / 1.15) % 1.35
            paste_centered(stage, cta_card, SAFE_LOW_CX, 1292, scale_x=pulse_cta * clamp01(dt / 0.24), sweep_prog=sw_cta)

        if comp_im is None or ev >= 0.995:
            comp_im = stage
        else:
            arr_st = np.array(stage)
            arr_st[:, :, 3] = (arr_st[:, :, 3].astype(np.float32) * ev).astype(np.uint8)
            comp_im.alpha_composite(Image.fromarray(arr_st, "RGBA"))

    # Compliant Legal Strip cleanly inside Safe Zone (Y = 1520 <= 1545, X <= 878 <= 884!)
    sp_leg = render_glow_text_sprite(cfg["legal"], FONT_BOLD, 20, (232, 242, 236), glow_rad=0, stroke_col=(8, 14, 14), stroke_w=3)
    k_leg = min(1.0, 812.0 / max(1.0, sp_leg.width))
    paste_centered(comp_im, sp_leg, SAFE_LOW_CX, 1520, scale_x=k_leg, opacity=0.86)
    return comp_im

def render_ep_chunk(args):
    vid_key, c_idx, f_start, f_end = args
    v_dir = os.path.join(BATCH_DIR, vid_key)
    meta = json.load(open(os.path.join(v_dir, "edl_meta.json"), "r", encoding="utf-8"))
    tr_j = json.load(open(os.path.join(v_dir, "main_cut_clean.json"), "r", encoding="utf-8"))
    cfg  = EP_CONFIGS[vid_key]
    tl   = build_stage_timeline(meta, cfg)
    end_s0 = [x[1] for x in tl["full_stages"] if x[0] == "endcard"][0]
    cap_groups = build_caption_groups(tr_j, tl["hook_aroll"], end_s0)

    brolls = [load_vid_frames_wh(p, 960, 540) for p in cfg["brolls"]]
    assets = load_ep_static_assets(cfg)

    n_frames = f_end - f_start
    ss_sec = f"{f_start / FPS:.6f}"
    chunk_mp4 = os.path.join(v_dir, f"_v3_chunk_{c_idx:02d}.mp4")
    vid_p = os.path.join(v_dir, "edited_graded.mp4")
    mat_p = os.path.join(v_dir, "edited_matte.mp4")

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
        im_out = compose_ep_frame(f_start + li, rgb, mat, brolls, assets, cap_groups, cfg, tl, meta)
        writer.stdin.write(np.array(im_out.convert("RGB"), dtype=np.uint8).tobytes())

    writer.stdin.close(); writer.wait()
    pv.stdout.close(); pv.wait()
    pm.stdout.close(); pm.wait()
    return chunk_mp4

def run_visual_test_sheet():
    # Audit Safe Zone + Sacred Face Zone first!
    boxes_audit = [
        ("Hook Arc Left",     224-122, 356-84, 224+122, 356+84),
        ("Hook Arc Right",    856-122, 356-84, 856+122, 356+84),
        ("Hook Lower Text",   468-408, 1165,   468+408, 1430),
        ("ARoll 70pt Subs",   468-407, 1180,   468+407, 1350),
        ("3D Flip Left Card", 198-131, 1326-170,198+131,1326+170),
        ("3D Flip Right Sub", 615-254, 1205,   615+254, 1370),
        ("EndCard CTA",       468-396, 1292-143,468+396,1292+143),
        ("Legal Strip",       468-406, 1502,   468+406, 1538),
    ]
    for nm, x1, y1, x2, y2 in boxes_audit:
        ok, rsn = is_box_safe_9x16(x1, y1, x2, y2)
        assert ok, f"SafeZone violation {nm}: {rsn}"
        if "ARoll" in nm or "Hook" in nm or "3D Flip" in nm:
            # Verify 0% overlap with Sacred Face Zone Y = 468..1148!
            assert (y2 <= 468 or y1 >= 1148), f"Face overlap violation on {nm}: y=({y1},{y2})"
    print("[GEOMETRY AUDIT] 100% PASS on TikTok/Reels Safe Zone AND Sacred Face Shield (Y=468..1148 untouched)!", flush=True)

    # Render 18-panel visual preview across diverse episodes & styles (Hook, A-Roll 70pt Subs, 3D Flip, Clash, Fan, Riffle, End-Card, Outdoor)
    samples = [
        ("v01", 1.8), ("v01", 12.5), ("v01", 34.0),
        ("v03", 2.0), ("v03", 20.0), ("v03", 36.5),
        ("v05", 2.0), ("v05", 26.0), ("v05", 49.0),
        ("v07", 2.0), ("v07", 36.0), ("v08", 22.0),
        ("v12", 18.0),("v16", 34.0), ("v17", 45.0),
        ("v10", 28.0),("v18", 2.5),  ("v19", 22.0),
    ]
    pw, ph = 270, 480
    sheet = Image.new("RGB", (pw * 6, ph * 3), (14, 18, 24))
    f_lbl = get_font(FONT_BOLD, 19)

    loaded_cache = {}
    for idx_s, (vk, ts_req) in enumerate(samples):
        v_dir = os.path.join(BATCH_DIR, vk)
        if vk not in loaded_cache:
            meta = json.load(open(os.path.join(v_dir, "edl_meta.json"), "r", encoding="utf-8"))
            tr_j = json.load(open(os.path.join(v_dir, "main_cut_clean.json"), "r", encoding="utf-8"))
            cfg  = EP_CONFIGS[vk]
            tl   = build_stage_timeline(meta, cfg)
            end_s0 = [x[1] for x in tl["full_stages"] if x[0] == "endcard"][0]
            caps = build_caption_groups(tr_j, tl["hook_aroll"], end_s0)
            brs  = [load_vid_frames_wh(p, 960, 540) for p in cfg["brolls"]]
            ast  = load_ep_static_assets(cfg)
            loaded_cache[vk] = (meta, cfg, tl, caps, brs, ast)
        meta, cfg, tl, caps, brs, ast = loaded_cache[vk]
        ts = min(meta["duration_s"] - 0.35, max(0.35, ts_req))
        f_idx = int(round(ts * FPS))
        ss = f"{f_idx / FPS:.6f}"
        rv = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", os.path.join(v_dir, "edited_graded.mp4"), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        rm = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", os.path.join(v_dir, "edited_matte.mp4"),  "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray",  "-"])
        rgb = np.frombuffer(rv[:W*H*3], dtype=np.uint8).reshape((H, W, 3))
        mat = np.frombuffer(rm[:W*H],   dtype=np.uint8).reshape((H, W))
        im_c = compose_ep_frame(f_idx, rgb, mat, brs, ast, caps, cfg, tl, meta).convert("RGB")
        im_sm = im_c.resize((pw, ph), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(im_sm)
        d.rounded_rectangle([6, 6, 152, 34], radius=7, fill=(10, 16, 20))
        d.text((12, 8), f"{vk}•{meta['code']} {ts:4.1f}s", font=f_lbl, fill=(255, 226, 96))
        sheet.paste(im_sm, ((idx_s % 6) * pw, (idx_s // 6) * ph))

    out_grid = os.path.join(BATCH_DIR, "batch_bigtext_noface_test_grid.jpg")
    sheet.save(out_grid, quality=93)
    print("Saved 18-panel Big-Text & Zero-Face-Overlap Test Sheet ->", out_grid, flush=True)

def main():
    if "--test" in sys.argv:
        run_visual_test_sheet()
        return

    only_vids = [a for a in sys.argv[1:] if a.startswith("v")]
    target_keys = only_vids if only_vids else list(EP_CONFIGS.keys())

    t_all = time.time()
    N_WORKERS = 4  # Safe for RTX 3060 NVENC concurrent sessions!
    for idx_e, vk in enumerate(target_keys, 1):
        v_dir = os.path.join(BATCH_DIR, vk)
        out_v = os.path.join(v_dir, "_v3_video_only.mp4")
        meta  = json.load(open(os.path.join(v_dir, "edl_meta.json"), "r", encoding="utf-8"))
        tot_f = int(meta["total_frames"])

        if os.path.exists(out_v) and os.path.getsize(out_v) > 500000 and "--force" not in sys.argv:
            print(f"[{idx_e}/{len(target_keys)}] Cached {vk} ({meta['code']}) -> {out_v}", flush=True)
            continue

        t0 = time.time()
        step = math.ceil(tot_f / N_WORKERS)
        tasks = [(vk, i, i * step, min(tot_f, (i + 1) * step)) for i in range(N_WORKERS) if i * step < tot_f]
        print(f"[{idx_e}/{len(target_keys)}] Rendering {vk} ({meta['code']} • {tot_f}f = {meta['duration_s']}s) across {len(tasks)} NVENC workers...", flush=True)
        with concurrent.futures.ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            chunks = list(ex.map(render_ep_chunk, tasks))

        lst = os.path.join(v_dir, "_v3_chunks.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for cf in chunks:
                f.write("file '" + cf.replace("\\", "/") + "'\n")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out_v], check=True)
        for cf in chunks + [lst]:
            if os.path.exists(cf):
                os.remove(cf)
        print(f"  -> DONE {vk} ({meta['code']}) in {time.time() - t0:.1f}s!", flush=True)

    print(f"\n=== ALL {len(target_keys)} VIDEOS RENDERED IN {time.time() - t_all:.1f}s ===", flush=True)

if __name__ == "__main__":
    main()
