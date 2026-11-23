import json, math, os, re, subprocess, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR = r"d:\AI\full studio\output\av-protein-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
F = 1.0 / FPS

# Verified 100% Vietnamese-glyph fonts on this machine
FONT_TITLE = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7182504807289065985\0a5333de6f4d592cb2d2390d68b31efb\Oswald-Bold.ttf"
FONT_WIDE  = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf"
FONT_CAP   = r"C:\Windows\Fonts\palabi.ttf"
FONT_SCRIPT = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\6990292000264163842\840d58433e5d79e2599f155e83c2defb\ZYVNA Dreamboat.ttf"
FONT_SUB   = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7542214368361057553\d376267c892ee3a53654ae93a78dcfb7\font.ttf"

_font_cache = {}
def get_font(path, size):
    key = (path, int(round(size)))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, max(10, int(round(size))))
    return _font_cache[key]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def ease_snap(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 3.6

def ease_out_back(u, s=1.25):
    u = clamp01(u) - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0

# Pre-build rich dark-emerald Pharmacist Studio Backdrop (replaces busy white/red/blue banner wall behind speaker!)
def build_studio_backdrop():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # Deep emerald-slate radial studio light behind head (540, 620)
    d2 = ((xx - 540.0) / 480.0) ** 2 + ((yy - 560.0) / 620.0) ** 2
    glow = np.exp(-d2 * 1.15)
    bg = np.zeros((H, W, 3), dtype=np.float32)
    bg[:, :, 0] = 9.0 + 18.0 * glow     # R
    bg[:, :, 1] = 22.0 + 56.0 * glow    # G
    bg[:, :, 2] = 26.0 + 52.0 * glow    # B

    # Warm vertical studio practical rim-light tube on left (homage to Foodtage warm neon bar!) & cool emerald rim bar on right
    tube_l = np.exp(-((xx - 68.0) / 14.0) ** 2) * np.exp(-((yy - 680.0) / 340.0) ** 4)
    halo_l = np.exp(-((xx - 68.0) / 75.0) ** 2) * np.exp(-((yy - 680.0) / 420.0) ** 2)
    bg[:, :, 0] += 245.0 * tube_l + 65.0 * halo_l
    bg[:, :, 1] += 155.0 * tube_l + 35.0 * halo_l
    bg[:, :, 2] += 45.0  * tube_l + 10.0 * halo_l

    tube_r = np.exp(-((xx - 1012.0) / 12.0) ** 2) * np.exp(-((yy - 640.0) / 320.0) ** 4)
    halo_r = np.exp(-((xx - 1012.0) / 70.0) ** 2) * np.exp(-((yy - 640.0) / 400.0) ** 2)
    bg[:, :, 0] += 55.0  * tube_r + 12.0 * halo_r
    bg[:, :, 1] += 230.0 * tube_r + 58.0 * halo_r
    bg[:, :, 2] += 195.0 * tube_r + 50.0 * halo_r

    return np.clip(bg, 0, 255).astype(np.uint8)

STUDIO_BG = build_studio_backdrop()

# Precompute static flares & B-roll dark vignette canvas once for 2.5x faster rendering!
def _build_static_layers():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # 1. Desk + Desk-BOJOMI-Box preservation mask (eliminates grey wall patch at x>790, y=1060..1510!)
    desk_line = np.clip((yy - 1505.0) / 55.0, 0.0, 1.0)
    box_zone_x = np.exp(-((np.maximum(0.0, np.abs(xx - 680.0) - 185.0)) / 42.0) ** 2)
    box_zone_y = np.clip((yy - 1265.0) / 45.0, 0.0, 1.0) * np.clip((1560.0 - yy) / 40.0, 0.0, 1.0)
    desk_mask = np.maximum(desk_line, box_zone_x * box_zone_y * 0.98)

    # 2. Top corner flares for T.ringsBg
    fl = np.exp(-((xx / 340.0) ** 2 + (yy / 360.0) ** 2)) + np.exp(-(((W - xx) / 340.0) ** 2 + (yy / 360.0) ** 2))
    fl_rgba = np.zeros((H, W, 4), dtype=np.uint8)
    fl_rgba[:, :, 0] = 220; fl_rgba[:, :, 1] = 255; fl_rgba[:, :, 2] = 245
    fl_rgba[:, :, 3] = np.clip(fl * 95.0, 0, 120).astype(np.uint8)
    flare_im = Image.fromarray(fl_rgba, "RGBA")

    # 3. Dark charcoal-emerald vignette canvas for T.brollCard
    vig = np.clip(1.0 - 0.55 * (((xx - 540.0) / 620.0) ** 2 + ((yy - 960.0) / 1050.0) ** 2), 0.35, 1.0)
    bbg = np.zeros((H, W, 3), dtype=np.uint8)
    bbg[:, :, 0] = (20 * vig).astype(np.uint8)
    bbg[:, :, 1] = (32 * vig).astype(np.uint8)
    bbg[:, :, 2] = (30 * vig).astype(np.uint8)
    broll_bg_im = Image.fromarray(bbg, "RGB").convert("RGBA")
    return desk_mask, flare_im, broll_bg_im

DESK_BLEND, RINGS_FLARE_IM, BROLL_BG_IM = _build_static_layers()

# Cache rendered text sprites so repeated frames are blazingly fast!
_sprite_cache = {}
def render_glow_text_sprite(text, font_path, size, top_col, bot_col=None, glow_col=None, glow_rad=14, stroke_col=None, stroke_w=0):
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
    pad = int(glow_rad * 3 + stroke_w + 16)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    # Alpha mask of glyph fill
    mask_im = Image.new("L", (cw, ch), 0)
    mdr = ImageDraw.Draw(mask_im)
    mdr.text((ox, oy), text, font=font, fill=255)

    # Vertical gradient fill
    arr_m = np.array(mask_im, dtype=np.float32) / 255.0
    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)[:, None]
    grad_rgb = np.zeros((ch, cw, 3), dtype=np.uint8)
    for c in range(3):
        grad_rgb[:, :, c] = np.clip(top_col[c] * (1.0 - yy) + bot_col[c] * yy, 0, 255).astype(np.uint8)
    fill_rgba = np.dstack([grad_rgb, (arr_m * 255.0).astype(np.uint8)])
    fill_im = Image.fromarray(fill_rgba, "RGBA")

    # Color-preserving Dual Drop Shadow Glow (T.glow rule from knowledge/07 #1: never white-out!)
    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    if glow_rad > 0:
        g1_a = mask_im.filter(ImageFilter.GaussianBlur(radius=glow_rad * 0.8))
        g2_a = mask_im.filter(ImageFilter.GaussianBlur(radius=glow_rad * 2.1))
        g_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
        g_arr[:, :, 0] = glow_col[0]
        g_arr[:, :, 1] = glow_col[1]
        g_arr[:, :, 2] = glow_col[2]
        a_comb = np.clip(np.array(g1_a, dtype=np.float32) * 0.72 + np.array(g2_a, dtype=np.float32) * 0.45, 0, 255).astype(np.uint8)
        g_arr[:, :, 3] = a_comb
        base = Image.alpha_composite(base, Image.fromarray(g_arr, "RGBA"))

    # Soft dark drop shadow for readability
    sh_a = mask_im.filter(ImageFilter.GaussianBlur(radius=6))
    sh_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
    sh_arr[:, :, 3] = (np.array(sh_a, dtype=np.float32) * 0.55).astype(np.uint8)
    sh_im.paste(Image.fromarray(sh_arr, "RGBA"), (4, 6))
    base = Image.alpha_composite(base, sh_im)

    base = Image.alpha_composite(base, fill_im)

    if stroke_w > 0 and stroke_col is not None:
        st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sdr = ImageDraw.Draw(st_im)
        sdr.text((ox, oy), text, font=font, fill=(0, 0, 0, 0), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        # Draw outline only where fill is not inner or strokeOver=True
        st_only = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sdr2 = ImageDraw.Draw(st_only)
        sdr2.text((ox, oy), text, font=font, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        # Subtract inner mask to leave pure border stroke over fill
        st_arr = np.array(st_only)
        inner = mask_im.filter(ImageFilter.MinFilter(3))
        st_arr[:, :, 3] = np.clip(st_arr[:, :, 3].astype(np.int32) - np.array(inner, dtype=np.int32), 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(st_arr, "RGBA"))

    if len(_sprite_cache) > 400:
        _sprite_cache.clear()
    _sprite_cache[key] = (base, mask_im)
    return base, mask_im

def paste_centered(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0, angle=0.0, blur_px=0.0, sweep_prog=None):
    if opacity <= 0.01 or scale <= 0.02:
        return
    im = sprite_im
    if sweep_prog is not None and 0.0 <= sweep_prog <= 1.0:
        # Animated diagonal CC Light Sweep across text alpha!
        arr = np.array(im).copy()
        sh, sw = arr.shape[:2]
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        diag = (xx + yy * 0.45) / (sw + sh * 0.45)
        band = np.exp(-((diag - sweep_prog) / 0.085) ** 2)
        alpha_f = (arr[:, :, 3:4].astype(np.float32) / 255.0)
        arr[:, :, :3] = np.clip(arr[:, :, :3].astype(np.float32) + 175.0 * band[:, :, None] * alpha_f, 0, 255).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    if abs(scale - 1.0) > 0.01:
        nw = max(2, int(round(im.width * scale)))
        nh = max(2, int(round(im.height * scale)))
        im = im.resize((nw, nh), Image.Resampling.BILINEAR)
    if abs(angle) > 0.2:
        im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    if blur_px >= 0.6:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(16.0, blur_px)))
    if opacity < 0.995:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    px = int(round(cx - im.width / 2.0))
    py = int(round(cy - im.height / 2.0))
    canvas_im.alpha_composite(im, dest=(px, py))

# Load & cache clean icon images for T.tile + T.ringsBg + T.logoBar
ICON_FILES = {
    "hook1": os.path.join(MEDIA_DIR, "hook_01_clean.png"),
    "hook2": os.path.join(MEDIA_DIR, "hook_02_clean.png"),
    "c04":   os.path.join(MEDIA_DIR, "icon_c04_clean.png"),
    "c07":   os.path.join(MEDIA_DIR, "icon_c07_clean.png"),
    "c08":   os.path.join(MEDIA_DIR, "icon_c08_clean.png"),
    "pack":  os.path.join(MEDIA_DIR, "packshot_c08_clean.png"),
}
ICON_IMS = {k: Image.open(v).convert("RGBA") for k, v in ICON_FILES.items()}

def render_tile_frame(icon_key, size_px, t_sec):
    """T.tile: Rounded 22% dark-emerald glass card + corner glow + animated EdgeSweep Trim-Path orbiting border!"""
    S = size_px
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pad = 14
    cs = S - pad * 2
    rad = int(cs * 0.22)

    # Rounded mask for inner icon card
    rmask = Image.new("L", (cs, cs), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, cs - 1, cs - 1], radius=rad, fill=255)

    ic_resized = ICON_IMS[icon_key].resize((cs, cs), Image.Resampling.LANCZOS)
    # Dark emerald-gold glass border glow behind card
    glow_bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gdr = ImageDraw.Draw(glow_bg)
    gdr.rounded_rectangle([pad - 3, pad - 3, pad + cs + 2, pad + cs + 2], radius=rad + 3, outline=(62, 235, 190, 210), width=5)
    glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(radius=6))
    im = Image.alpha_composite(im, glow_bg)

    card_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    card_layer.paste(ic_resized, (pad, pad), mask=rmask)
    im = Image.alpha_composite(im, card_layer)

    # Edge border + Orbiting bright EdgeSweep (6s per revolution like th-lib.jsx!)
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=(45, 210, 175, 190), width=4)

    # Compute orbiting bright sweep spotlight around border!
    ang = (t_sec / 3.5) * 2.0 * math.pi
    sx = S / 2.0 + (cs * 0.48) * math.cos(ang)
    sy = S / 2.0 + (cs * 0.48) * math.sin(ang)
    border_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(border_mask).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=255, width=6)
    bm_arr = np.array(border_mask, dtype=np.float32) / 255.0
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    spot = np.exp(-(((xx - sx) ** 2 + (yy - sy) ** 2) / (2.0 * (S * 0.18) ** 2)))
    sweep_rgba = np.zeros((S, S, 4), dtype=np.uint8)
    sweep_rgba[:, :, 0] = 255
    sweep_rgba[:, :, 1] = 245
    sweep_rgba[:, :, 2] = 175
    sweep_rgba[:, :, 3] = np.clip(bm_arr * spot * 255.0, 0, 255).astype(np.uint8)
    sweep_im = Image.fromarray(sweep_rgba, "RGBA").filter(ImageFilter.GaussianBlur(radius=2))
    im = Image.alpha_composite(im, sweep_im)
    return im

def draw_burst(canvas_im, cx, cy, t_now, t0, diam=74):
    """T.burst: expanding white ring 60% -> 190% over 0.4s"""
    dt = t_now - t0
    if dt < 0 or dt > 0.42:
        return
    u = dt / 0.42
    sc = 0.60 + 1.30 * ease_snap(u)
    op = 1.0 if u < 0.35 else (1.0 - (u - 0.35) / 0.65)
    r = int(round(diam * 0.5 * sc))
    sw = max(2, int(round(6 * (1.0 - 0.6 * u))))
    sz = r * 2 + 20
    bim = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    ImageDraw.Draw(bim).ellipse([10, 10, sz - 10, sz - 10], outline=(255, 255, 255, int(245 * clamp01(op))), width=sw)
    canvas_im.alpha_composite(bim, dest=(int(cx - sz // 2), int(cy - sz // 2)))

def draw_rings_bg(canvas_im, t_now, t0, t1):
    """T.ringsBg: Concentric white rings + orbiting icons + top flares BEHIND speaker!"""
    if not (t0 <= t_now <= t1):
        return
    dt = t_now - t0
    dur = max(0.1, t1 - t0)
    sc = 1.0 + 0.25 * (1.0 - ease_snap(min(1.0, dt / (10.0 * F))))
    rot_deg = 38.0 * (dt / dur)
    cx, cy = 540, 680

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    R1 = int(530 * sc)
    R2 = int(410 * sc)
    dr.ellipse([cx - R1, cy - R1, cx + R1, cy + R1], outline=(255, 255, 255, 145), width=3)
    dr.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=(140, 255, 225, 85), width=2)

    # 5 orbiting mini badges + gear circles along upper arc (-165 deg to -15 deg)
    keys = ["hook1", "c04", "c08", "c07", "hook2"]
    for i, k in enumerate(keys):
        a_deg = -165.0 + i * (150.0 / 4.0) + rot_deg * 0.65
        a_rad = math.radians(a_deg)
        ix = cx + int(R1 * math.cos(a_rad))
        iy = cy + int(R1 * math.sin(a_rad))
        mini = ICON_IMS[k].resize((82, 82), Image.Resampling.BILINEAR)
        mm = Image.new("L", (82, 82), 0)
        ImageDraw.Draw(mm).ellipse([2, 2, 79, 79], fill=215)
        layer.paste(mini, (ix - 41, iy - 41), mask=mm)
        dr.ellipse([ix - 42, iy - 42, ix + 42, iy + 42], outline=(255, 255, 255, 190), width=3)

        ga = a_rad + 0.32
        gx = cx + int(R2 * math.cos(ga))
        gy = cy + int(R2 * math.sin(ga))
        dr.ellipse([gx - 10, gy - 10, gx + 10, gy + 10], outline=(255, 240, 170, 200), width=4)

    layer = Image.alpha_composite(layer, RINGS_FLARE_IM)

    # 4-frame entry flash
    if dt < 4.0 * F:
        f_op = int(160 * (1.0 - dt / (4.0 * F)))
        layer = Image.alpha_composite(layer, Image.new("RGBA", (W, H), (255, 255, 255, f_op)))

    canvas_im.alpha_composite(layer)

def perspective_coeffs(pa, pb):
    """Compute 8-coeff perspective transform mapping pb -> pa for PIL Image.transform"""
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(pb, dtype=np.float64).reshape(8)
    res = np.linalg.solve(A, B)
    return tuple(res.tolist())

def render_broll_3d_card(top_rgb, bot_rgb, dt, dur, badge_small, badge_big):
    """T.brollCard: Dark grain vignette studio + 3D angled bottom visual + 3D tilted rounded top card!"""
    canvas = BROLL_BG_IM.copy()

    # 1. Bottom 3D tilted panel (like DaVinci timeline in Foodtage 12.0-14.7s!)
    z_bot = 1.0 + 0.06 * (dt / max(0.2, dur))
    bw, bh = int(980 * z_bot), int(860 * z_bot)
    bot_im = Image.fromarray(bot_rgb, "RGB").resize((1080, 1920), Image.Resampling.BILINEAR)
    # Crop central region of bottom source
    cy_src = 960
    bot_crop = bot_im.crop((0, max(0, cy_src - 460), 1080, min(1920, cy_src + 460))).resize((bw, bh), Image.Resampling.BILINEAR).convert("RGBA")
    bmask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(bmask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=42, fill=245)
    bot_card = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bot_card.paste(bot_crop, (0, 0), mask=bmask)
    ImageDraw.Draw(bot_card).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=42, outline=(90, 220, 185, 150), width=4)

    # 3D perspective quad on canvas for bottom panel (tilted X=8, Y=-6, Z=-3)
    dst_bot = [(55, 1060), (1035, 980), (1065, 1825), (25, 1885)]
    src_bot = [(0, 0), (bw, 0), (bw, bh), (0, bh)]
    coeffs_b = perspective_coeffs(dst_bot, src_bot)
    warped_bot = bot_card.transform((W, H), Image.Transform.PERSPECTIVE, coeffs_b, Image.Resampling.BILINEAR)
    canvas = Image.alpha_composite(canvas, warped_bot)

    # 2. Top 3D Rounded Card (860x720, r=68, snap scale 85% -> 106% -> 110% with deep shadow!)
    if dt < 8.0 * F:
        sc = 0.85 + 0.21 * ease_snap(dt / (8.0 * F))
    else:
        sc = 1.06 + 0.04 * ((dt - 8.0 * F) / max(0.2, dur))
    cw, ch = int(860 * sc), int(720 * sc)
    top_im = Image.fromarray(top_rgb, "RGB")
    # Center-crop 860:720 aspect from 1080x1920
    crop_h = int(1080 * (720.0 / 860.0))
    y_top = (1920 - crop_h) // 2
    top_crop = top_im.crop((0, y_top, 1080, y_top + crop_h)).resize((cw, ch), Image.Resampling.BILINEAR).convert("RGBA")
    tmask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(tmask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=64, fill=255)
    tcard = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    tcard.paste(top_crop, (0, 0), mask=tmask)
    ImageDraw.Draw(tcard).rounded_rectangle([1, 1, cw - 2, ch - 2], radius=64, outline=(130, 255, 220, 220), width=6)

    cx0, cy0 = 540, 505
    dx, dy = cw * 0.5, ch * 0.5
    # Subtle 3D tilt (rotY=-5, rotZ=-2)
    dst_top = [
        (cx0 - dx * 0.96, cy0 - dy * 0.94),
        (cx0 + dx * 1.02, cy0 - dy * 1.02),
        (cx0 + dx * 0.99, cy0 + dy * 0.96),
        (cx0 - dx * 1.01, cy0 + dy * 1.03),
    ]
    src_top = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
    coeffs_t = perspective_coeffs(dst_top, src_top)
    warped_top = tcard.transform((W, H), Image.Transform.PERSPECTIVE, coeffs_t, Image.Resampling.BILINEAR)

    # Drop shadow under top 3D card
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(p[0] + 14, p[1] + 28) for p in dst_top], fill=(0, 0, 0, 175))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=24))
    canvas = Image.alpha_composite(canvas, sh)
    canvas = Image.alpha_composite(canvas, warped_top)

    # Clean floating pill title between top and bottom 3D cards!
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdr = ImageDraw.Draw(pill)
    pdr.rounded_rectangle([95, 895, 985, 1035], radius=38, fill=(8, 34, 26, 225), outline=(100, 245, 205, 210), width=3)
    canvas = Image.alpha_composite(canvas, pill)

    sp1, _ = render_glow_text_sprite(badge_small, FONT_WIDE, 28, (195, 255, 235), glow_rad=6)
    sp2, _ = render_glow_text_sprite(badge_big, FONT_WIDE, 42, (255, 222, 65), (255, 185, 20), glow_col=(255, 195, 40), glow_rad=10)
    paste_centered(canvas, sp1, 540, 932, scale=1.0, opacity=1.0)
    paste_centered(canvas, sp2, 540, 986, scale=1.0, opacity=1.0)
    return canvas

def draw_synergy_bar(canvas_im, t_now, t0, t1):
    """T.logoBar: Frosted glass bar sliding from right at y=1310 with 4 synergy badges (BOJOMI center bigger!)"""
    if not (t0 <= t_now <= t1):
        return
    dt = t_now - t0
    dur = t1 - t0
    if dt < 0.30:
        ox = 320.0 * (1.0 - ease_snap(dt / 0.30))
    else:
        ox = -28.0 * ((dt - 0.30) / max(0.2, dur - 0.30))
    op = 1.0 if (t1 - t_now) > 3 * F else max(0.0, (t1 - t_now) / (3 * F))

    bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(bar)
    bx1, by1, bx2, by2 = int(75 + ox), 1565, int(1005 + ox), 1790
    dr.rounded_rectangle([bx1, by1, bx2, by2], radius=52, fill=(10, 32, 26, int(185 * op)), outline=(145, 255, 225, int(195 * op)), width=3)

    items = [
        ("c08", "TẢO BIỂN", -310, 132),
        ("pack", "BOJOMI", -95, 166),
        ("c07", "D3 + K2", 125, 132),
        ("hook1", "COLLAGEN", 315, 132),
    ]
    cx_base = 540 + ox
    for k, lbl, dx, sz in items:
        ic = ICON_IMS[k].resize((sz, sz), Image.Resampling.BILINEAR)
        rm = Image.new("L", (sz, sz), 0)
        ImageDraw.Draw(rm).rounded_rectangle([0, 0, sz - 1, sz - 1], radius=int(sz * 0.22), fill=int(255 * op))
        px = int(cx_base + dx - sz // 2)
        py = 1660 - sz // 2
        bar.paste(ic, (px, py), mask=rm)
        ImageDraw.Draw(bar).rounded_rectangle([px, py, px + sz - 1, py + sz - 1], radius=int(sz * 0.22), outline=(255, 230, 120, int(210 * op)), width=3)
        sp, _ = render_glow_text_sprite(lbl, FONT_WIDE, 22 if sz < 160 else 26, (255, 255, 255) if sz < 160 else (255, 220, 60), glow_rad=5)
        paste_centered(bar, sp, cx_base + dx, py + sz + 22, opacity=op)

    canvas_im.alpha_composite(bar)

def draw_light_leak(canvas_im, t_now, leak_times):
    """T.leaks: Clean warm golden-mint Screen light leak (0.45s), zero static/glitch!"""
    for lt in leak_times:
        dt = t_now - lt
        if 0.0 <= dt <= 0.45:
            u = dt / 0.45
            inten = math.sin(u * math.pi) * 0.68
            arr = np.array(canvas_im, dtype=np.float32)
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            cx = 220.0 + 640.0 * u
            cy = 480.0 + 350.0 * u
            blob = np.exp(-(((xx - cx) / 480.0) ** 2 + ((yy - cy) / 560.0) ** 2)) * inten
            leak_rgb = np.zeros((H, W, 3), dtype=np.float32)
            leak_rgb[:, :, 0] = 255.0 * blob
            leak_rgb[:, :, 1] = 215.0 * blob
            leak_rgb[:, :, 2] = 135.0 * blob
            # Screen blend: 255 - (255 - A)*(255 - B)/255
            a_rgb = arr[:, :, :3]
            arr[:, :, :3] = 255.0 - (255.0 - a_rgb) * (255.0 - leak_rgb) / 255.0
            canvas_im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA"))
            break

# ======================================================================
# BUILD DATA FROM TRANSCRIPT (matching examples/foodtage/build.jsx!)
# ======================================================================
def load_timeline_data():
    tr = json.load(open(os.path.join(AROLL_DIR, "aroll_direct.json"), encoding="utf-8"))
    broll_spans = [
        (3.55, 9.15, "c02", "THỰC TRẠNG SINH HOẠT", "ĂN THẤT THƯỜNG • LỊCH HỌC KÍN"),
        (24.94, 29.24, "c05", "DƯỠNG CHẤT CHO XƯƠNG", "CANXI & VITAMIN D QUAN TRỌNG"),
        (37.18, 40.35, "c06", "BOJOMI AN VƯỢNG", "NGUỒN CANXI TỪ TẢO BIỂN ĐỎ"),
        (57.40, 62.50, "c09", "TIỆN LỢI MỖI NGÀY", "1 GÓI • ĐỦ DINH DƯỠNG CHO XƯƠNG"),
    ]
    skip_ranges = [(0.0, 3.46)] + [(s[0], s[1]) for s in broll_spans]
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if not any(a <= (w["start"] + w["end"]) * 0.5 <= b for a, b in skip_ranges)
    ]

    # Group into Foodtage-style stacked 2-3 word lines (max 3 lines per group)
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
        if line and (len(line) >= 3 or sum(len(x[0]) + 1 for x in line) + len(txt) > 15):
            flush_line()
        if len(cur) >= 3 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!…:;]$", txt):
            flush_group()
    flush_group()

    # Auto-assign emphasis {k, col, stroke_up} on key medical/brand words!
    GOLD_WORDS = {"dưỡng", "khỏe", "mạnh", "chế", "tuổi", "nhu", "Bojomi", "Vượng.", "tảo", "biển", "418mg", "779", "170mcg", "MK7."}
    PINK_WORDS = {"băn", "khoăn,", "không", "cao", "hơn", "D3,", "K2", "collagen.", "nhắn", "quyết", "định"}
    STROKE_UP_WORDS = {"Bojomi", "418mg", "779", "170mcg", "nhắn"}

    cap_groups = []
    for i, g in enumerate(groups):
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else 70.10
        t1 = min(nxt, last_end + 0.45) if (nxt - last_end) > 0.6 else nxt
        cap_groups.append({"t0": g[0][0][1], "t1": t1, "lines": g})
    return broll_spans, cap_groups, GOLD_WORDS, PINK_WORDS, STROKE_UP_WORDS

def get_cam_zoom(t):
    # HOLD punch-zooms synced to topic transitions (just like D.zooms in build.jsx!)
    zooms = [
        (0.00, 1.00),
        (9.70, 1.12),
        (12.50, 1.05),
        (15.98, 1.10),
        (18.30, 1.16),
        (20.70, 1.07),
        (29.32, 1.16),
        (31.70, 1.08),
        (35.06, 1.18),
        (40.38, 1.08),
        (44.62, 1.14),
        (51.30, 1.06),
        (62.62, 1.15),
        (66.00, 1.07),
    ]
    z = 1.0
    for tz, val in zooms:
        if t >= tz:
            z = val
        else:
            break
    return z

class VideoReader:
    def __init__(self, path, total_frames=None):
        self.path = path
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE
        )
    def read(self):
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            return None
        return np.frombuffer(buf, dtype=np.uint8).reshape((H, W, 3))
    def close(self):
        self.proc.stdout.close()
        self.proc.wait()

def load_clip_frames(path):
    frames = []
    r = VideoReader(path)
    while True:
        f = r.read()
        if f is None:
            break
        frames.append(f)
    r.close()
    return frames

def main():
    t_start = time.time()
    aroll_path = os.path.join(AROLL_DIR, "aroll.mp4")
    matte_path = os.path.join(AROLL_DIR, "aroll_matte.mp4")

    print("Loading 4 B-roll clips into RAM for 3D card compositing...")
    broll_clips = {
        "c02": load_clip_frames(os.path.join(MEDIA_DIR, "broll_c02.mp4")),
        "c05": load_clip_frames(os.path.join(MEDIA_DIR, "broll_c05.mp4")),
        "c06": load_clip_frames(os.path.join(MEDIA_DIR, "broll_c06.mp4")),
        "c09": load_clip_frames(os.path.join(MEDIA_DIR, "broll_c09.mp4")),
    }
    pack_im_rgb = np.array(Image.open(os.path.join(MEDIA_DIR, "packshot_c08_clean.png")).convert("RGB").resize((W, H), Image.Resampling.LANCZOS))
    ref_collage_rgb = np.array(Image.open(r"D:\AI\full studio\canvas\exports\1_BOJOMI Packaging Reference Collage.png.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS))

    broll_spans, cap_groups, GOLD_WORDS, PINK_WORDS, STROKE_UP_WORDS = load_timeline_data()

    # T.number behind speaker: (label, digit, t0, t1)
    NUMBERS = [
        ("LƯU Ý", "1", 18.30, 20.60),
        ("LƯU Ý", "2", 29.32, 31.55),
        ("ĐIỂM SÁNG", "3", 35.06, 37.15),
    ]
    # T.keyword behind speaker's head (1 line, y=215 per knowledge/07 #23!)
    KEYWORDS = [
        ("BĂN KHOĂN?", 9.70, 12.45, 195, (255, 232, 135), (255, 255, 255)),
        ("KHỎE MẠNH", 15.98, 18.25, 195, (110, 255, 215), (235, 255, 250)),
        ("3 YẾU TỐ", 20.65, 24.85, 205, (255, 218, 75), (255, 248, 215)),
        ("CHIỀU CAO", 31.60, 34.95, 200, (125, 248, 235), (240, 255, 255)),
        ("HIỆP ĐỒNG", 40.42, 44.50, 195, (255, 220, 85), (255, 250, 220)),
        ("418mg CANXI", 44.62, 51.15, 160, (115, 255, 205), (245, 255, 250)),
        ("D3 & K2 MK7", 51.25, 57.32, 162, (255, 215, 70), (255, 250, 225)),
        ("ĐỐI CHIẾU", 65.50, 70.05, 195, (120, 250, 220), (255, 255, 255)),
    ]
    # T.placeTile placements: (icon_key, t0, t1, cx, cy, scale_px, rot_deg)
    TILE_PLACES = [
        # Hook 3-tile arc framing head!
        ("hook1", 0.85, 3.42, 215, 310, 215, -12.0),
        ("hook2", 1.00, 3.42, 540, 245, 225, 0.0),
        ("c08",   1.15, 3.42, 865, 310, 215, 12.0),
        # Body floating tiles at right-lower-chest (never covering desk BOJOMI box!)
        ("hook1", 12.50, 15.60, 865, 1365, 235, -3.0),
        ("c04",   20.65, 24.85, 865, 1365, 240, 0.0),
        ("c08",   44.80, 51.15, 865, 1365, 235, -2.0),
        ("pack",  51.25, 57.32, 865, 1365, 245, 2.0),
        ("c07",   62.80, 69.85, 865, 1365, 235, 0.0),
    ]
    BURSTS = [
        (215, 310, 0.92, 68), (540, 245, 1.07, 74), (865, 310, 1.22, 68),
        (865, 1365, 12.60, 78), (865, 1365, 20.75, 78),
        (865, 1365, 44.90, 78), (865, 1365, 51.35, 78), (865, 1365, 62.90, 78),
    ]
    LEAK_TIMES = [0.85, 3.52, 18.28, 24.92, 37.16, 44.60, 57.38, 62.60]

    legal_sp, _ = render_glow_text_sprite(
        "Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh",
        FONT_SUB, 22, (230, 238, 235), glow_rad=0
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_v2_video_only.mp4")
    writer = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
        raw_vid_out
    ], stdin=subprocess.PIPE)

    import sys
    test_mode = "--test" in sys.argv
    test_frames = {int(round(ts * FPS)) for ts in [1.4, 19.2, 22.0, 38.5, 42.2, 48.0]}
    test_saved = []

    frame_idx = 0
    while True:
        rgb = reader_a.read()
        mbuf = reader_m.stdout.read(W * H)
        if rgb is None or len(mbuf) < W * H:
            break
        if test_mode and frame_idx not in test_frames:
            frame_idx += 1
            if frame_idx > max(test_frames):
                break
            continue
        matte = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W)).astype(np.float32) / 255.0
        t = frame_idx / FPS

        # Check if inside a 3D B-Roll Card scene!
        active_br = None
        for st, en, key, b_sm, b_bg in broll_spans:
            if st <= t < en:
                active_br = (st, en, key, b_sm, b_bg)
                break

        if active_br is not None:
            st, en, key, b_sm, b_bg = active_br
            dt = t - st
            dur = en - st
            clips = broll_clips[key]
            top_f = clips[min(len(clips) - 1, int(dt * FPS))]
            if key == "c02":
                bot_f = clips[min(len(clips) - 1, int((dt * 0.7 + 1.0) * FPS))]
            elif key == "c05":
                bot_f = ref_collage_rgb
            elif key == "c06":
                c05_clips = broll_clips["c05"]
                bot_f = c05_clips[min(len(c05_clips) - 1, int(dt * FPS))]
            else:
                bot_f = pack_im_rgb
            comp_im = render_broll_3d_card(top_f, bot_f, dt, dur, b_sm, b_bg)
        else:
            # 1. Warm grade on A-roll person + desk
            graded = np.clip((rgb.astype(np.float32) - 14.0) * 1.09 + 12.0, 0, 255).astype(np.uint8)

            # 2. Apply Camera HOLD Punch-Zoom centered at (540, 680) to person, matte, and desk mask!
            z = get_cam_zoom(t)
            if z > 1.005:
                cw, ch = int(round(W / z)), int(round(H / z))
                x0 = max(0, min(W - cw, int(round(540 - cw * 0.5))))
                y0 = max(0, min(H - ch, int(round(680 - ch * (680.0 / H)))))
                fg_im = Image.fromarray(graded[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
                m_im  = Image.fromarray((matte[y0:y0+ch, x0:x0+cw] * 255.0).astype(np.uint8), "L").resize((W, H), Image.Resampling.BILINEAR)
                d_im  = Image.fromarray((DESK_BLEND[y0:y0+ch, x0:x0+cw] * 255.0).astype(np.uint8), "L").resize((W, H), Image.Resampling.BILINEAR)
                fg_arr = np.array(fg_im)
                m_arr = np.array(m_im, dtype=np.float32) / 255.0
                desk_blend_z = np.array(d_im, dtype=np.float32) / 255.0
            else:
                fg_arr = graded
                m_arr = matte
                desk_blend_z = DESK_BLEND

            # Combine RVM person matte + desk preservation mask so behind-head text sits behind head while real desk & BOJOMI box stay crisp!
            fg_alpha = np.maximum(m_arr, desk_blend_z)
            comp_im = Image.fromarray(STUDIO_BG, "RGB").convert("RGBA")

            # 3. T.ringsBg (BEHIND speaker!)
            draw_rings_bg(comp_im, t, 44.62, 57.32)
            draw_rings_bg(comp_im, t, 62.62, 70.10)

            # 4. T.behind: T.number ("1 / 2 / 3") & T.keyword TUCKED BEHIND speaker's crown/hair!
            for lbl, dig, t0, t1 in NUMBERS:
                if t0 <= t < t1:
                    dt = t - t0
                    op = 1.0 if (t1 - t) > 3 * F else (t1 - t) / (3 * F)
                    sc_l = 1.0 + 0.40 * (1.0 - ease_snap(min(1.0, dt / (5 * F))))
                    sp_l, _ = render_glow_text_sprite(lbl, FONT_TITLE, 110, (65, 195, 255), (30, 120, 255), glow_col=(45, 160, 255), glow_rad=14)
                    paste_centered(comp_im, sp_l, 240, 355, scale=sc_l, opacity=op)

                    if dt >= 2 * F:
                        dt_d = dt - 2 * F
                        sc_d = (1.0 + 0.50 * (1.0 - ease_snap(min(1.0, dt_d / (8 * F))))) * (1.0 - 0.05 * (dt_d / max(0.2, t1 - t0)))
                        rot_d = -14.0 * (1.0 - ease_snap(min(1.0, dt_d / (8 * F))))
                        sp_d, _ = render_glow_text_sprite(dig, FONT_CAP, 540, (255, 215, 90), (145, 255, 225), glow_col=(95, 245, 225), glow_rad=22, stroke_col=(215, 255, 250), stroke_w=8)
                        paste_centered(comp_im, sp_d, 770, 545, scale=sc_d, opacity=op, angle=rot_d)

            for kw_txt, t0, t1, fsz, c_top, c_bot in KEYWORDS:
                if t0 <= t < t1:
                    dt = t - t0
                    sc_k = 1.0 + 0.35 * (1.0 - ease_snap(min(1.0, dt / (5 * F))))
                    op = 1.0 if (t1 - t) > 3 * F else (t1 - t) / (3 * F)
                    sw_p = (dt / max(0.25, t1 - t0)) * 1.3 - 0.15
                    sp_k, _ = render_glow_text_sprite(kw_txt, FONT_TITLE, fsz + 14, c_top, c_bot, glow_col=c_top, glow_rad=12)
                    paste_centered(comp_im, sp_k, 540, 445, scale=sc_k, opacity=op, sweep_prog=sw_p)

            # 5. Composite FG_Person + Real Desk ON TOP of studio backdrop, rings, numbers, and behind-head keywords!
            fg_rgba = np.dstack([fg_arr, (fg_alpha * 255.0).astype(np.uint8)])
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(fg_rgba, "RGBA"))

            # 6. Front Layer: Hook B ("Muốn con / CAO LỚN / Bữa ăn hằng ngày?") on dark chest BELOW chin (100% Face-Safe!)
            if 0.05 <= t < 3.45:
                op_h = 1.0 if (3.45 - t) > 3 * F else (3.45 - t) / (3 * F)
                if t >= 0.05:
                    sc1 = 1.0 + 0.45 * (1.0 - ease_snap(min(1.0, (t - 0.05) / (6 * F))))
                    sp_h1, _ = render_glow_text_sprite("Muốn con", FONT_WIDE, 78, (95, 225, 255), (35, 130, 255), glow_col=(55, 175, 255), glow_rad=14)
                    paste_centered(comp_im, sp_h1, 540, 1105, scale=sc1, opacity=op_h)
                if t >= 0.42:
                    sc2 = 1.0 + 0.60 * (1.0 - ease_snap(min(1.0, (t - 0.42) / (6 * F))))
                    sp_h2, _ = render_glow_text_sprite("CAO", FONT_WIDE, 142, (255, 225, 65), (255, 115, 35), glow_col=(255, 165, 40), glow_rad=18)
                    paste_centered(comp_im, sp_h2, 335, 1235, scale=sc2, opacity=op_h)
                if t >= 0.62:
                    sc3 = 1.0 + 0.42 * (1.0 - ease_snap(min(1.0, (t - 0.62) / (6 * F))))
                    sp_h3, _ = render_glow_text_sprite("Lớn!", FONT_SCRIPT, 150, (110, 255, 175), (45, 235, 145), glow_col=(75, 255, 165), glow_rad=20, stroke_col=(225, 255, 238), stroke_w=2)
                    paste_centered(comp_im, sp_h3, 705, 1245, scale=sc3, opacity=op_h)
                if t >= 1.82:
                    sc4 = 1.0 + 0.30 * (1.0 - ease_snap(min(1.0, (t - 1.82) / (5 * F))))
                    sp_h4, _ = render_glow_text_sprite("Đã quan tâm bữa ăn hằng ngày?", FONT_CAP, 52, (255, 255, 255), (165, 255, 235), glow_col=(92, 247, 224), glow_rad=12)
                    paste_centered(comp_im, sp_h4, 540, 1368, scale=sc4, opacity=op_h)

            # 7. T.placeTile (Hook 3-tile arc + Body tiles with orbiting EdgeSweep!) + T.burst
            for ikey, t0, t1, cx, cy, sz, rot in TILE_PLACES:
                if t0 <= t < t1:
                    dt = t - t0
                    u_pos = ease_snap(min(1.0, dt / (13 * F)))
                    u_sc  = ease_snap(min(1.0, dt / (10 * F)))
                    cur_y = cy + (1.0 - u_pos) * (120.0 if cy < 400 else 220.0)
                    cur_sc = 0.60 + 0.40 * u_sc
                    op = min(1.0, dt / (3 * F)) * (1.0 if (t1 - t) > 3 * F else (t1 - t) / (3 * F))
                    tile_im = render_tile_frame(ikey, sz, t)
                    paste_centered(comp_im, tile_im, cx, cur_y, scale=cur_sc, opacity=op, angle=rot)

            for bx, by, bt0, bdiam in BURSTS:
                draw_burst(comp_im, bx, by, t, bt0, bdiam)

            # 8. T.logoBar sliding frosted glass synergy pill bar (40.38 - 44.50s)
            draw_synergy_bar(comp_im, t, 40.38, 44.50)

            # 9. T.captions: Word-by-word glowing stacked captions + T.strokeUp on dark chest (y=1140, 100% Face-Safe!)
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    op_g = 1.0 if (g["t1"] - t) > 2 * F else (g["t1"] - t) / (2 * F)
                    y_base = 1140
                    lh = 68
                    for li, ln in enumerate(g["lines"]):
                        # Measure line words to center horizontally
                        word_renders = []
                        total_w = 0
                        gap = 18
                        for wi, (wtxt, ws, we) in enumerate(ln):
                            k = 1.24 if (wtxt in GOLD_WORDS or wtxt in PINK_WORDS) else 1.0
                            if wtxt in GOLD_WORDS:
                                col = (255, 222, 70)
                            elif wtxt in PINK_WORDS:
                                col = (255, 145, 205)
                            else:
                                col = (92, 247, 224)
                            sp, _ = render_glow_text_sprite(wtxt, FONT_CAP, 66 * k, col, glow_col=col, glow_rad=12)
                            # Trim horizontal padding for accurate spacing
                            font_obj = get_font(FONT_CAP, 66 * k)
                            adv = int(ImageDraw.Draw(comp_im).textlength(wtxt, font=font_obj))
                            word_renders.append((wtxt, ws, sp, adv, col, k))
                            total_w += adv + (gap if wi > 0 else 0)

                        cur_x = 540 - total_w // 2
                        cur_y = y_base + li * lh
                        for wtxt, ws, sp, adv, col, k in word_renders:
                            if t >= ws:
                                dt_w = t - ws
                                u_w = ease_snap(min(1.0, dt_w / (5 * F)))
                                wy = cur_y + (1.0 - u_w) * 28.0
                                blur_w = (1.0 - u_w) * 7.5
                                wcx = cur_x + adv // 2
                                paste_centered(comp_im, sp, wcx, wy, scale=1.0, opacity=op_g, blur_px=blur_w)

                                # T.strokeUp expanding outline burst on hero words!
                                if wtxt in STROKE_UP_WORDS and 3 * F <= dt_w <= 14 * F:
                                    u_su = (dt_w - 3 * F) / (11 * F)
                                    sc_su = 1.0 + 1.35 * (u_su ** 1.4)
                                    op_su = (1.0 - u_su) * 0.85
                                    sp_su, _ = render_glow_text_sprite(wtxt, FONT_CAP, 66 * k, (0, 0, 0), glow_col=col, glow_rad=8, stroke_col=(230, 255, 248), stroke_w=3)
                                    paste_centered(comp_im, sp_su, wcx, cur_y, scale=sc_su, opacity=op_su)
                            cur_x += adv + gap
                    break

        # 10. Soft Light Leaks + Subtle Legal Bar at bottom
        draw_light_leak(comp_im, t, LEAK_TIMES)
        bar_bot = Image.new("RGBA", (W, 56), (5, 14, 12, 165))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 56))
        paste_centered(comp_im, legal_sp, 540, H - 28, opacity=0.90)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        out_rgb = np.array(comp_im.convert("RGB"), dtype=np.uint8)
        writer.stdin.write(out_rgb.tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/2103 frames ({frame_idx / el:.1f} fps)", flush=True)

    writer.stdin.close()
    writer.wait()
    reader_a.close()
    reader_m.stdout.close()
    reader_m.wait()
    print(f"Video track done: {frame_idx} frames in {time.time() - t_start:.1f}s -> {raw_vid_out}")

if __name__ == "__main__":
    main()
