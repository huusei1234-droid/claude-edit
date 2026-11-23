import json, math, os, re, subprocess, sys, time
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

def ease_out_expo(u):
    """Snappy After Effects 'snap' curve (fast launch, smooth brake, zero jerk)"""
    u = clamp01(u)
    return 1.0 if u >= 0.999 else 1.0 - math.pow(2.0, -8.5 * u)

def smoothstep(u):
    u = clamp01(u)
    return u * u * (3.0 - 2.0 * u)

def smooth_in_out_env(t, t0, t1, d_in=0.22, d_out=0.20):
    if t <= t0 or t >= t1:
        return 0.0
    a_in = ease_out_cubic((t - t0) / max(0.03, d_in)) if (t - t0) < d_in else 1.0
    a_out = smoothstep((t1 - t) / max(0.03, d_out)) if (t1 - t) < d_out else 1.0
    return min(a_in, a_out)

def fit_cover(rgb_arr, target_w, target_h, zoom=1.0):
    """100% locked aspect ratio center-crop — ZERO stretching/squishing!"""
    sh, sw = rgb_arr.shape[:2]
    base_scale = max(target_w / float(sw), target_h / float(sh)) * zoom
    nw = max(target_w, int(round(sw * base_scale)))
    nh = max(target_h, int(round(sh * base_scale)))
    resized = np.array(Image.fromarray(rgb_arr, "RGB").resize((nw, nh), Image.Resampling.BILINEAR))
    x0 = (nw - target_w) // 2
    y0 = (nh - target_h) // 2
    return resized[y0:y0 + target_h, x0:x0 + target_w]

# ======================================================================
# 1. CINEMA COLOR GRADE & STATIC STUDIO TEXTURES
# ======================================================================
def _build_grade_and_statics():
    # LUT for subtle warm contrast cinema grade on A-roll
    x = np.arange(256, dtype=np.float32) / 255.0
    # Gentle S-curve contrast + lifted shadows
    s = np.clip((x - 0.035) / (0.955 - 0.035), 0.0, 1.0)
    s = np.power(s, 0.94)
    s = s * 0.88 + (s * s * (3.0 - 2.0 * s)) * 0.12
    lut_r = np.clip(s * 255.0 * 1.018, 0, 255).astype(np.uint8)
    lut_g = np.clip(s * 255.0 * 1.002, 0, 255).astype(np.uint8)
    lut_b = np.clip(s * 255.0 * 0.985, 0, 255).astype(np.uint8)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # Soft 22% cinema edge vignette for normal A-roll
    r2 = ((xx - 540.0) / 680.0) ** 2 + ((yy - 760.0) / 1150.0) ** 2
    aroll_vig = np.clip(1.0 - 0.22 * r2, 0.72, 1.0)[:, :, None].astype(np.float32)

    # Dark textured grain floor for T.brollCard (matches video mẫu #2a2a2c + Noise + CC Vignette)
    rng = np.random.default_rng(42)
    noise = rng.normal(0.0, 5.5, (H, W, 1)).astype(np.float32)
    b_vig = np.clip(1.0 - 0.55 * (((xx - 540.0) / 620.0) ** 2 + ((yy - 960.0) / 1060.0) ** 2), 0.30, 1.0)[:, :, None]
    base_broll = np.zeros((H, W, 3), dtype=np.float32)
    base_broll[:, :, 0] = 30.0
    base_broll[:, :, 1] = 33.0
    base_broll[:, :, 2] = 38.0
    broll_bg_arr = np.clip(base_broll * b_vig + noise, 0, 255).astype(np.uint8)
    broll_bg_im = Image.fromarray(broll_bg_arr, "RGB").convert("RGBA")

    # Deep midnight radial studio backdrop for T.ringsBg (#232c52 -> #04050b + top corner flares)
    rr = np.sqrt(((xx - 540.0) / 620.0) ** 2 + ((yy - 720.0) / 960.0) ** 2)
    t_rad = np.clip(rr, 0.0, 1.0)
    rings_bg = np.zeros((H, W, 4), dtype=np.uint8)
    rings_bg[:, :, 0] = np.clip(35.0 * (1.0 - t_rad) + 5.0 * t_rad, 0, 255).astype(np.uint8)
    rings_bg[:, :, 1] = np.clip(46.0 * (1.0 - t_rad) + 7.0 * t_rad, 0, 255).astype(np.uint8)
    rings_bg[:, :, 2] = np.clip(86.0 * (1.0 - t_rad) + 14.0 * t_rad, 0, 255).astype(np.uint8)
    rings_bg[:, :, 3] = 255
    rings_bg_im = Image.fromarray(rings_bg, "RGBA")

    # Crisp white top-left & top-right volumetric corner flares (exact T.ringsBg Flare_L / Flare_R)
    fl_im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dfl = ImageDraw.Draw(fl_im)
    dfl.polygon([(-180, -180), (430, -180), (-180, 520)], fill=(255, 255, 255, 215))
    dfl.polygon([(W + 180, -180), (W - 430, -180), (W + 180, 520)], fill=(255, 255, 255, 215))
    fl_im = fl_im.filter(ImageFilter.GaussianBlur(radius=95))

    # Soft feathered chest caption contrast cushion (makes cyan/gold/pink glow pop 100% over striped shirt)
    cush = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cush).ellipse([130, 1000, 950, 1340], fill=(4, 8, 14, 118))
    cush = cush.filter(ImageFilter.GaussianBlur(radius=68))

    return (lut_r, lut_g, lut_b), aroll_vig, broll_bg_im, rings_bg_im, fl_im, cush

LUTS, AROLL_VIG, BROLL_BG_IM, RINGS_BG_IM, RINGS_FLARE_IM, CAP_CUSHION_IM = _build_grade_and_statics()

def grade_aroll(rgb):
    out = np.empty_like(rgb)
    out[:, :, 0] = LUTS[0][rgb[:, :, 0]]
    out[:, :, 1] = LUTS[1][rgb[:, :, 1]]
    out[:, :, 2] = LUTS[2][rgb[:, :, 2]]
    # Subtle vibrance boost (+14%)
    f = out.astype(np.float32)
    lum = (0.299 * f[:, :, 0] + 0.587 * f[:, :, 1] + 0.114 * f[:, :, 2])[:, :, None]
    f = lum + (f - lum) * 1.14
    f = f * AROLL_VIG
    return np.clip(f, 0, 255).astype(np.uint8)

# ======================================================================
# 2. SUPERSAMPLED NEON VECTOR ICONS & DARK OBSIDIAN TILES (T.tile)
# ======================================================================
def _make_neon_vector_icons():
    """
    Renders 6 bespoke 4x-supersampled glowing neon line-art icons (exact DaVinci/AE 'icon effect' look
    from video mẫu.mov: cyan #55f2ff + violet/mint dual glow on transparent background) + white silhouette
    versions for T.ringsBg orbital satellites!
    """
    SS = 640  # drawn at 640x640, scaled cleanly
    icons_neon = {}
    icons_white = {}

    specs = ["height", "meal", "algae", "factors", "d3k2", "cta", "bojomi"]
    for kind in specs:
        cyan_m = Image.new("L", (SS, SS), 0)
        acc_m  = Image.new("L", (SS, SS), 0)
        dc = ImageDraw.Draw(cyan_m)
        da = ImageDraw.Draw(acc_m)
        lw = 22

        if kind == "height":
            # Vertical ruler + upward growth arrow + bone emblem
            dc.rounded_rectangle([125, 95, 275, 545], radius=30, outline=255, width=lw)
            for ytick in range(160, 505, 62):
                tlen = 70 if ((ytick - 160) // 62) % 2 == 0 else 44
                dc.line([(125, ytick), (125 + tlen, ytick)], fill=255, width=16)
            da.line([(435, 515), (435, 130)], fill=255, width=26)
            da.line([(340, 235), (435, 125), (530, 235)], fill=255, width=26)
            for sx, sy, sr in [(510, 405, 34), (345, 355, 24)]:
                da.line([(sx - sr, sy), (sx + sr, sy)], fill=255, width=14)
                da.line([(sx, sy - sr), (sx, sy + sr)], fill=255, width=14)

        elif kind == "meal":
            dc.arc([95, 205, 495, 530], start=0, end=180, fill=255, width=lw)
            dc.line([(95, 368), (495, 368)], fill=255, width=lw)
            dc.line([(210, 530), (380, 530)], fill=255, width=lw)
            dc.arc([165, 265, 295, 368], start=180, end=360, fill=255, width=18)
            dc.arc([280, 255, 425, 368], start=180, end=360, fill=255, width=18)
            f_q = get_font(FONT_WIDE, 265)
            da.text((385, 70), "?", font=f_q, fill=255)

        elif kind == "algae":
            dc.ellipse([115, 125, 525, 535], outline=255, width=16)
            da.line([(320, 500), (320, 205)], fill=255, width=22)
            da.line([(320, 390), (200, 265)], fill=255, width=20)
            da.line([(245, 310), (195, 195)], fill=255, width=18)
            da.line([(320, 350), (445, 235)], fill=255, width=20)
            da.line([(395, 280), (450, 180)], fill=255, width=18)
            f_ca = get_font(FONT_WIDE, 112)
            dc.text((242, 382), "Ca", font=f_ca, fill=255)

        elif kind == "factors":
            dc.rounded_rectangle([135, 105, 505, 545], radius=44, outline=255, width=lw)
            dc.rounded_rectangle([235, 74, 405, 145], radius=22, outline=255, width=18)
            for ry in [235, 345, 455]:
                da.line([(190, ry), (225, ry + 32), (285, ry - 30)], fill=255, width=20)
                dc.line([(315, ry), (450, ry)], fill=255, width=18)

        elif kind == "d3k2":
            dc.regular_polygon((260, 380, 130), n_sides=6, rotation=30, outline=255, width=lw)
            f_k2 = get_font(FONT_WIDE, 98)
            dc.text((192, 326), "K2", font=f_k2, fill=255)
            da.ellipse([360, 115, 505, 260], outline=255, width=20)
            for a_deg in range(0, 360, 45):
                ar = math.radians(a_deg)
                da.line([
                    (432 + int(88 * math.cos(ar)), 188 + int(88 * math.sin(ar))),
                    (432 + int(118 * math.cos(ar)), 188 + int(118 * math.sin(ar)))
                ], fill=255, width=15)

        elif kind == "cta":
            dc.rounded_rectangle([105, 130, 525, 455], radius=62, outline=255, width=lw)
            dc.polygon([(205, 455), (175, 540), (295, 455)], outline=255, width=lw)
            da.line([(225, 295), (295, 365), (430, 220)], fill=255, width=28)

        elif kind == "bojomi":
            # Premium BOJOMI hexagonal pharma crest + mug + Ca/D3/K2 crown
            da.regular_polygon((320, 320, 225), n_sides=6, rotation=0, outline=255, width=22)
            dc.rounded_rectangle([195, 285, 425, 455], radius=45, outline=255, width=20)
            dc.arc([395, 315, 480, 420], start=-90, end=90, fill=255, width=18)
            f_bj = get_font(FONT_TITLE, 96)
            da.text((182, 165), "BOJOMI", font=f_bj, fill=255)

        # Compose dual-glow neon icon (Cyan #55f2ff + Violet-Mint accent #ffd859 / #c47aff)
        comp = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
        for mask_l, core_col, glow_col in [
            (cyan_m, (165, 250, 255), (45, 215, 255)),
            (acc_m,  (255, 238, 165), (185, 105, 255)),
        ]:
            g_wide = np.array(mask_l.filter(ImageFilter.GaussianBlur(radius=28)), dtype=np.float32)
            g_mid  = np.array(mask_l.filter(ImageFilter.GaussianBlur(radius=10)), dtype=np.float32)
            core   = np.array(mask_l, dtype=np.float32)

            layer = np.zeros((SS, SS, 4), dtype=np.uint8)
            layer[:, :, 0] = glow_col[0]
            layer[:, :, 1] = glow_col[1]
            layer[:, :, 2] = glow_col[2]
            layer[:, :, 3] = np.clip(g_wide * 0.65 + g_mid * 0.95, 0, 255).astype(np.uint8)
            comp = Image.alpha_composite(comp, Image.fromarray(layer, "RGBA"))

            clayer = np.zeros((SS, SS, 4), dtype=np.uint8)
            clayer[:, :, 0] = core_col[0]
            clayer[:, :, 1] = core_col[1]
            clayer[:, :, 2] = core_col[2]
            clayer[:, :, 3] = np.clip(core, 0, 255).astype(np.uint8)
            comp = Image.alpha_composite(comp, Image.fromarray(clayer, "RGBA"))

        icons_neon[kind] = comp

        # Crisp white neon line-art version for T.ringsBg orbital satellites
        comb_m = Image.fromarray(np.maximum(np.array(cyan_m), np.array(acc_m)), "L")
        gw = np.array(comb_m.filter(ImageFilter.GaussianBlur(radius=12)), dtype=np.float32)
        cw = np.array(comb_m, dtype=np.float32)
        wlayer = np.zeros((SS, SS, 4), dtype=np.uint8)
        wlayer[:, :, :3] = 255
        wlayer[:, :, 3] = np.clip(cw + gw * 0.55, 0, 255).astype(np.uint8)
        icons_white[kind] = Image.fromarray(wlayer, "RGBA")

    # Also load authentic BOJOMI 3D box with transparent background
    pack_im = Image.open(os.path.join(MEDIA_DIR, "packshot_c08_clean.png")).convert("RGBA")
    # Remove light studio card background around the 3D box if opaque
    parr = np.array(pack_im)
    icons_neon["pack"] = pack_im
    return icons_neon, icons_white

NEON_ICONS, WHITE_ICONS = _make_neon_vector_icons()

_tile_base_cache = {}
def render_obsidian_neon_tile(icon_key, size_px, t_sec):
    """
    Exact replica of After Effects T.tile ('icon effect.setting') from video mẫu.mov:
    - Dark obsidian squircle (#0f1219) with glowing violet-cyan radial corner aura
    - Crisp glowing border (#8d42ff / #3ee8d5)
    - Continuous 20% perimeter EdgeSweep comet orbiting every 4.5s
    - Supersampled glowing neon vector icon inside
    """
    S = size_px
    if (icon_key, S) not in _tile_base_cache:
        pad = int(round(S * 0.08))
        cs = S - pad * 2
        rad = int(round(cs * 0.23))

        rmask = Image.new("L", (cs, cs), 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, cs - 1, cs - 1], radius=rad, fill=255)

        # Dark obsidian fill + bottom-right radial purple/cyan glow (exact T.rampIn)
        yy, xx = np.mgrid[0:cs, 0:cs].astype(np.float32)
        dist = np.sqrt(((xx - cs * 0.88) / (cs * 0.78)) ** 2 + ((yy - cs * 0.88) / (cs * 0.78)) ** 2)
        glow_f = np.clip(1.0 - dist, 0.0, 1.0) ** 1.6
        card_rgb = np.zeros((cs, cs, 3), dtype=np.uint8)
        card_rgb[:, :, 0] = np.clip(14.0 + 108.0 * glow_f, 0, 255).astype(np.uint8)
        card_rgb[:, :, 1] = np.clip(17.0 + 32.0 * glow_f, 0, 255).astype(np.uint8)
        card_rgb[:, :, 2] = np.clip(25.0 + 195.0 * glow_f, 0, 255).astype(np.uint8)

        base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        # Outer ambient drop shadow + neon aura
        sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad - 2, pad + 4, pad + cs + 2, pad + cs + 8], radius=rad, fill=(0, 0, 0, 185))
        ImageDraw.Draw(sh).rounded_rectangle([pad - 2, pad - 2, pad + cs + 2, pad + cs + 2], radius=rad + 2, outline=(138, 68, 255, 155), width=5)
        sh = sh.filter(ImageFilter.GaussianBlur(radius=8))
        base = Image.alpha_composite(base, sh)

        card_rgba = Image.fromarray(np.dstack([card_rgb, np.array(rmask)]), "RGBA")
        cl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        cl.paste(card_rgba, (pad, pad))
        base = Image.alpha_composite(base, cl)

        # Icon inside
        ic_sz = int(round(cs * 0.78))
        ic_im = NEON_ICONS[icon_key].resize((ic_sz, ic_sz), Image.Resampling.LANCZOS)
        ipx = (S - ic_sz) // 2
        if icon_key == "pack":
            # Rounded mask for packshot card
            pm = Image.new("L", (ic_sz, ic_sz), 0)
            ImageDraw.Draw(pm).rounded_rectangle([4, 4, ic_sz - 5, ic_sz - 5], radius=int(ic_sz * 0.16), fill=255)
            base.paste(ic_im, (ipx, ipx), mask=pm)
        else:
            base.alpha_composite(ic_im, dest=(ipx, ipx))

        # Crisp neon border
        ImageDraw.Draw(base).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=(152, 82, 255, 220), width=4)

        border_mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(border_mask).rounded_rectangle([pad, pad, pad + cs - 1, pad + cs - 1], radius=rad, outline=255, width=6)
        _tile_base_cache[(icon_key, S)] = (base, np.array(border_mask, dtype=np.float32) / 255.0, cs)

    base, bm_arr, cs = _tile_base_cache[(icon_key, S)]
    out = base.copy()
    ang = (t_sec / 4.2) * 2.0 * math.pi
    sx = S * 0.5 + (cs * 0.50) * math.cos(ang)
    sy = S * 0.5 + (cs * 0.50) * math.sin(ang)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    spot = np.exp(-(((xx - sx) ** 2 + (yy - sy) ** 2) / (2.0 * (S * 0.20) ** 2)))
    sw_rgba = np.zeros((S, S, 4), dtype=np.uint8)
    sw_rgba[:, :, 0] = 235; sw_rgba[:, :, 1] = 220; sw_rgba[:, :, 2] = 255
    sw_rgba[:, :, 3] = np.clip(bm_arr * spot * 255.0, 0, 255).astype(np.uint8)
    out = Image.alpha_composite(out, Image.fromarray(sw_rgba, "RGBA").filter(ImageFilter.GaussianBlur(radius=1.8)))
    return out

# ======================================================================
# 3. TRUE 3D PERSPECTIVE B-ROLL CARD (Exact T.brollCard from video mẫu.mov)
# ======================================================================
def _find_persp_coeffs(dst_pts, src_pts):
    """Solves 8-parameter perspective coefficients mapping dst (W,H) -> src (cw,ch) for PIL C-transform"""
    matrix = []
    for p1, p2 in zip(dst_pts, src_pts):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(src_pts, dtype=np.float64).reshape(8)
    return np.linalg.solve(A, B).tolist()

def warp_3d_card(card_rgba, dst_cx, dst_cy, rot_x_deg, rot_y_deg, rot_z_deg, scale=1.0, focal=1450.0):
    """
    Projects an aspect-locked RGBA image in true 3D camera space onto (W, H) canvas!
    - Zero aspect-ratio squishing (true pinhole camera homography K * R * [X, Y, Z])!
    """
    ch, cw = card_rgba.shape[:2] if isinstance(card_rgba, np.ndarray) else (card_rgba.height, card_rgba.width)
    hw, hh = (cw * 0.5) * scale, (ch * 0.5) * scale
    pts_3d = np.array([
        [-hw, -hh, 0.0],
        [ hw, -hh, 0.0],
        [ hw,  hh, 0.0],
        [-hw,  hh, 0.0],
    ], dtype=np.float64)

    rx, ry, rz = math.radians(rot_x_deg), math.radians(rot_y_deg), math.radians(rot_z_deg)
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]], dtype=np.float64)
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]], dtype=np.float64)
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]], dtype=np.float64)
    R = Rz @ Ry @ Rx

    dst_pts = []
    for p in pts_3d:
        pr = R @ p
        z = focal + pr[2]
        px = dst_cx + (pr[0] * focal) / z
        py = dst_cy + (pr[1] * focal) / z
        dst_pts.append((px, py))
    src_pts = [(0.0, 0.0), (float(cw - 1), 0.0), (float(cw - 1), float(ch - 1)), (0.0, float(ch - 1))]
    coeffs = _find_persp_coeffs(dst_pts, src_pts)
    im_src = Image.fromarray(card_rgba, "RGBA") if isinstance(card_rgba, np.ndarray) else card_rgba
    return im_src.transform((W, H), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BILINEAR)

def render_true_3d_broll(base_rgba, top_rgb, bot_rgb, t_now, st, en, tag_text):
    """
    Exact replica of After Effects T.brollCard in video mẫu.mov (see L_cmp.jpg col 5):
    - Smooth 7-frame ease-in / 7-frame ease-out transition
    - Bottom clip: Large true-3D angled plane (rotX=+9, rotY=-7, rotZ=-3) across lower canvas, 0% stretch!
    - Top clip: Floating rounded 3D card (860x720, r=68, rotX=+5, rotY=-5, rotZ=-2) overlapping in front (z=-250),
      casting a deep 3D drop shadow onto the bottom plane, snapping 0.86 -> 1.05 -> 1.09!
    """
    env = smooth_in_out_env(t_now, st, en, d_in=0.24, d_out=0.22)
    if env <= 0.005:
        return base_rgba

    dt = t_now - st
    dur = max(0.2, en - st)
    scene = BROLL_BG_IM.copy()

    # 1. Bottom 3D angled plane — dramatic diagonal 3D camera sweep matching L_cmp.jpg col 5 (0% stretch!)
    bw, bh = 1280, 960
    z_bot = 1.02 + 0.07 * (dt / dur)
    bot_crop = fit_cover(bot_rgb, bw, bh, zoom=z_bot)
    bot_rgba = np.dstack([bot_crop, np.full((bh, bw), 255, dtype=np.uint8)])
    bot_rgba[0:6, :, :3] = np.clip(bot_rgba[0:6, :, :3].astype(np.int32) + 70, 0, 255).astype(np.uint8)
    bot_rgba[-5:, :, :3] = np.clip(bot_rgba[-5:, :, :3].astype(np.int32) + 45, 0, 255).astype(np.uint8)

    sc_b = 1.05 + 0.06 * smoothstep(dt / dur)
    sh_b = np.zeros((bh, bw, 4), dtype=np.uint8); sh_b[:, :, 3] = 195
    scene.alpha_composite(warp_3d_card(sh_b, dst_cx=555, dst_cy=1335, rot_x_deg=14.0, rot_y_deg=-12.0, rot_z_deg=-13.5, scale=sc_b, focal=1200.0).filter(ImageFilter.GaussianBlur(radius=26)))
    bot_warped_im = warp_3d_card(bot_rgba, dst_cx=545, dst_cy=1305, rot_x_deg=14.0, rot_y_deg=-12.0, rot_z_deg=-13.5, scale=sc_b, focal=1200.0)
    scene.alpha_composite(bot_warped_im)

    # 2. Top Floating Rounded 3D Card overlapping upper edge of bottom plane (z=-250 depth!)
    tw, th = 850, 710
    z_top = 1.06 - 0.05 * (dt / dur)
    top_crop = fit_cover(top_rgb, tw, th, zoom=z_top)
    tmask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(tmask).rounded_rectangle([0, 0, tw - 1, th - 1], radius=68, fill=255)
    tcard_im = Image.fromarray(np.dstack([top_crop, np.array(tmask)]), "RGBA")
    ImageDraw.Draw(tcard_im).rounded_rectangle([1, 1, tw - 2, th - 2], radius=68, outline=(255, 255, 255, 115), width=3)

    if dt < 8 * F:
        sc_t = 0.86 + 0.18 * ease_out_expo(dt / (8 * F))
    else:
        sc_t = 1.04 + 0.05 * ((dt - 8 * F) / max(0.1, dur - 8 * F))

    sh_src = np.zeros((th, tw, 4), dtype=np.uint8)
    sh_src[:, :, 3] = (np.array(tmask, dtype=np.float32) * 0.88).astype(np.uint8)
    sh_im = warp_3d_card(sh_src, dst_cx=565, dst_cy=535, rot_x_deg=7.5, rot_y_deg=-8.0, rot_z_deg=-4.5, scale=sc_t, focal=1250.0).filter(ImageFilter.GaussianBlur(radius=32))
    scene.alpha_composite(sh_im)

    top_warped_im = warp_3d_card(tcard_im, dst_cx=548, dst_cy=490, rot_x_deg=7.5, rot_y_deg=-8.0, rot_z_deg=-4.5, scale=sc_t, focal=1250.0)
    scene.alpha_composite(top_warped_im)

    # Pure clean 3D B-Roll like video mẫu.mov (no cluttering bottom text over footage!)
    if env >= 0.995:
        return scene
    arr = np.array(scene)
    arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * env).astype(np.uint8)
    out = base_rgba.copy()
    out.alpha_composite(Image.fromarray(arr, "RGBA"))
    return out

# ======================================================================
# 4. TYPOGRAPHY, GLOW, LIGHT SWEEP, BURSTS, RINGS & LIGHT LEAKS
# ======================================================================
_sprite_cache = {}
def render_glow_text_sprite(text, font_path, size, top_col, bot_col=None, glow_col=None, glow_rad=14, stroke_col=None, stroke_w=0, no_fill=False):
    bot_col = bot_col or top_col
    glow_col = glow_col or top_col
    key = (text, font_path, int(round(size)), top_col, bot_col, glow_col, int(round(glow_rad)), stroke_col, stroke_w, no_fill)
    if key in _sprite_cache:
        return _sprite_cache[key]

    font = get_font(font_path, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = int(glow_rad * 3.2 + stroke_w + 18)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    mask_im = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_im).text((ox, oy), text, font=font, fill=255)

    base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    # Color-preserving dual Drop-Shadow Glow (exact T.glow in th-lib.jsx!)
    if glow_rad > 0:
        src_m = mask_im
        if no_fill and stroke_w > 0:
            src_m = Image.new("L", (cw, ch), 0)
            ImageDraw.Draw(src_m).text((ox, oy), text, font=font, fill=0, stroke_width=stroke_w, stroke_fill=255)
        g1 = np.array(src_m.filter(ImageFilter.GaussianBlur(radius=max(1.0, glow_rad * 0.75))), dtype=np.float32)
        g2 = np.array(src_m.filter(ImageFilter.GaussianBlur(radius=max(2.0, glow_rad * 2.2))), dtype=np.float32)
        g_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
        g_arr[:, :, 0] = glow_col[0]; g_arr[:, :, 1] = glow_col[1]; g_arr[:, :, 2] = glow_col[2]
        g_arr[:, :, 3] = np.clip(g1 * 0.82 + g2 * 0.52, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(g_arr, "RGBA"))

    if not no_fill:
        # Soft depth drop shadow
        sh_a = mask_im.filter(ImageFilter.GaussianBlur(radius=7))
        sh_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sh_arr = np.zeros((ch, cw, 4), dtype=np.uint8)
        sh_arr[:, :, 3] = (np.array(sh_a, dtype=np.float32) * 0.72).astype(np.uint8)
        sh_im.paste(Image.fromarray(sh_arr, "RGBA"), (4, 7))
        base = Image.alpha_composite(base, sh_im)

        arr_m = np.array(mask_im, dtype=np.float32) / 255.0
        yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)[:, None]
        grad_rgb = np.zeros((ch, cw, 3), dtype=np.uint8)
        for c in range(3):
            grad_rgb[:, :, c] = np.clip(top_col[c] * (1.0 - yy) + bot_col[c] * yy, 0, 255).astype(np.uint8)
        fill_im = Image.fromarray(np.dstack([grad_rgb, (arr_m * 255.0).astype(np.uint8)]), "RGBA")
        base = Image.alpha_composite(base, fill_im)

    if stroke_w > 0 and stroke_col is not None:
        st_only = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(st_only).text((ox, oy), text, font=font, fill=(0, 0, 0, 0) if no_fill else (*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
        st_arr = np.array(st_only)
        inner = mask_im.filter(ImageFilter.MinFilter(3))
        st_arr[:, :, 3] = np.clip(st_arr[:, :, 3].astype(np.int32) - np.array(inner, dtype=np.int32), 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(st_arr, "RGBA"))

    if len(_sprite_cache) > 550:
        _sprite_cache.clear()
    _sprite_cache[key] = (base, mask_im)
    return base, mask_im

def paste_centered(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0, angle=0.0, blur_px=0.0, vblur_px=0.0, sweep_prog=None):
    if opacity <= 0.01 or scale <= 0.02:
        return
    im = sprite_im
    if sweep_prog is not None and -0.1 <= sweep_prog <= 1.1:
        arr = np.array(im).copy()
        sh, sw = arr.shape[:2]
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        diag = (xx + yy * 0.42) / max(1.0, sw + sh * 0.42)
        band = np.exp(-((diag - sweep_prog) / 0.085) ** 2)
        af = arr[:, :, 3:4].astype(np.float32) / 255.0
        arr[:, :, :3] = np.clip(arr[:, :, :3].astype(np.float32) + 185.0 * band[:, :, None] * af, 0, 255).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    if abs(scale - 1.0) > 0.008:
        nw = max(2, int(round(im.width * scale)))
        nh = max(2, int(round(im.height * scale)))
        im = im.resize((nw, nh), Image.Resampling.BILINEAR)
    if abs(angle) > 0.15:
        im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    if vblur_px >= 1.5:
        # Fast vertical motion-blur box filter in numpy!
        ksz = min(29, max(3, int(round(vblur_px)) | 1))
        arr = np.array(im, dtype=np.float32)
        pad_v = ksz // 2
        padded = np.pad(arr, ((pad_v, pad_v), (0, 0), (0, 0)), mode="edge")
        csum = np.cumsum(padded, axis=0)
        csum = np.vstack([np.zeros((1, arr.shape[1], 4), dtype=np.float32), csum])
        blurred = (csum[ksz:ksz + arr.shape[0]] - csum[:arr.shape[0]]) / float(ksz)
        im = Image.fromarray(np.clip(blurred, 0, 255).astype(np.uint8), "RGBA")
    elif blur_px >= 0.6:
        im = im.filter(ImageFilter.GaussianBlur(radius=min(14.0, blur_px)))
    if opacity < 0.995:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        im = Image.fromarray(arr, "RGBA")

    px = int(round(cx - im.width / 2.0))
    py = int(round(cy - im.height / 2.0))
    canvas_im.alpha_composite(im, dest=(px, py))

def draw_burst(canvas_im, cx, cy, t_now, t0, diam=72):
    dt = t_now - t0
    if dt < 0 or dt > 0.40:
        return
    u = dt / 0.40
    sc = 0.60 + 1.30 * ease_out_expo(u)
    op = 1.0 if u < 0.35 else smoothstep((1.0 - u) / 0.65)
    r = int(round(diam * 0.5 * sc))
    sw = max(2, int(round(6 * (1.0 - 0.55 * u))))
    sz = r * 2 + 20
    bim = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    ImageDraw.Draw(bim).ellipse([10, 10, sz - 10, sz - 10], outline=(255, 255, 255, int(245 * op)), width=sw)
    canvas_im.alpha_composite(bim, dest=(int(cx - sz // 2), int(cy - sz // 2)))

def draw_electric_bolt(canvas_im, t_now, t0):
    """Subtle crisp neon electric arc behind Giant Digit 1/2/3 (exact T.number Bolt in th-lib.jsx)"""
    dt = t_now - t0
    if dt < 3 * F or dt > 16 * F:
        return
    # Flicker pattern from th-lib.jsx line 189: [0, 1, 0.3, 1, 0]
    f_idx = dt / F
    if f_idx < 5: op = (f_idx - 3) / 2.0
    elif f_idx < 8: op = 1.0 - 0.7 * ((f_idx - 5) / 3.0)
    elif f_idx < 10: op = 0.3 + 0.7 * ((f_idx - 8) / 2.0)
    else: op = max(0.0, 1.0 - (f_idx - 10) / 6.0)
    if op <= 0.02:
        return

    bolt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pts = [(805, 70), (865, 220), (830, 255), (900, 435), (870, 465), (935, 635)]
    ImageDraw.Draw(bolt).line(pts, fill=(130, 245, 255, int(220 * op)), width=12)
    bolt = bolt.filter(ImageFilter.GaussianBlur(radius=10))
    ImageDraw.Draw(bolt).line(pts, fill=(230, 255, 255, int(250 * op)), width=5)
    canvas_im.alpha_composite(bolt)

def draw_rings_bg_v4(canvas_im, t_now, t0, t1):
    """
    Exact replica of T.ringsBg from video mẫu.mov (see ref_sheet_01.jpg 18.000 - 21.333):
    - Deep midnight radial gradient (#232c52 -> #04050b)
    - 2 concentric crisp white rings + 5 crisp white neon vector icons & mini gear circles rotating 0 -> 38 deg
    - Soft white volumetric corner flares + 4-frame opening flash!
    """
    env = smooth_in_out_env(t_now, t0, t1, d_in=0.22, d_out=0.30)
    if env <= 0.01:
        return
    dt = t_now - t0
    dur = max(0.2, t1 - t0)
    sc = 1.22 - 0.22 * ease_out_expo(min(1.0, dt / (10 * F)))
    rot_deg = 38.0 * (dt / dur)
    cx, cy = 540, 720

    layer = RINGS_BG_IM.copy()
    dr = ImageDraw.Draw(layer)
    R1 = int(round(555 * sc))
    R2 = int(round(432 * sc))
    dr.ellipse([cx - R1, cy - R1, cx + R1, cy + R1], outline=(255, 255, 255, 175), width=3)
    dr.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=(255, 255, 255, 92), width=2)

    sat_keys = ["height", "algae", "d3k2", "factors", "cta"]
    for i, k in enumerate(sat_keys):
        a_deg = -155.0 + i * (170.0 / 4.0) + rot_deg
        a_rad = math.radians(a_deg)
        ix = cx + int(round(R1 * math.cos(a_rad)))
        iy = cy + int(round(R1 * math.sin(a_rad)))
        ic = WHITE_ICONS[k].resize((112, 112), Image.Resampling.BILINEAR)
        paste_centered(layer, ic, ix, iy, angle=rot_deg * 0.4)

        # Mini orbital gear ring on inner orbit (exact Gear_i in th-lib.jsx line 357)
        ga = a_rad + 0.38
        gx = cx + int(round(R2 * math.cos(ga)))
        gy = cy + int(round(R2 * math.sin(ga)))
        dr.ellipse([gx - 11, gy - 11, gx + 11, gy + 11], outline=(255, 255, 255, 215), width=4)

    layer = Image.alpha_composite(layer, RINGS_FLARE_IM)

    # 4-frame opening cinema flash (exact Flash in th-lib.jsx line 368)
    if 0.0 <= dt <= 5 * F:
        f_op = int(165 * max(0.0, 1.0 - dt / (5 * F)))
        layer = Image.alpha_composite(layer, Image.new("RGBA", (W, H), (255, 255, 255, f_op)))

    if env < 0.995:
        arr = np.array(layer)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * env).astype(np.uint8)
        layer = Image.fromarray(arr, "RGBA")
    canvas_im.alpha_composite(layer)

def draw_frosted_logo_bar(canvas_im, t_now, t0, t1):
    """Exact T.logoBar from video mẫu.mov (ref_sheet_01.jpg 07.333 - 08.667) at chest/desk y=1325"""
    env = smooth_in_out_env(t_now, t0, t1, d_in=0.16, d_out=0.20)
    if env <= 0.01:
        return
    dt = t_now - t0
    dur = max(0.2, t1 - t0)
    if dt < 0.30:
        ox = 320.0 * (1.0 - ease_out_expo(dt / 0.30))
    else:
        ox = -28.0 * ((dt - 0.30) / max(0.1, dur - 0.30))

    bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bx1, by1, bx2, by2 = int(65 + ox), 1525, int(1015 + ox), 1785
    # Frosted glass pill below speaker's hands holding BOJOMI box!
    ImageDraw.Draw(bar).rounded_rectangle([bx1, by1, bx2, by2], radius=58, fill=(18, 24, 38, int(155 * env)), outline=(185, 225, 255, int(165 * env)), width=3)

    items = [
        ("algae",   -315, 162),
        ("d3k2",    -125, 162),
        ("bojomi",    75, 218),
        ("height",   285, 162),
    ]
    cx_b = 540 + ox
    cy_b = 1655
    for k, dx, sz in items:
        tile = render_obsidian_neon_tile(k, sz, t_now)
        paste_centered(bar, tile, cx_b + dx, cy_b, opacity=env)
    canvas_im.alpha_composite(bar)

def apply_light_leak(canvas_im, t_now, leak_times):
    """Soft warm golden/cyan optical light leak (Screen blend, 0.46s, zero harsh glitch!)"""
    for lt, side in leak_times:
        dt = t_now - lt
        if -0.08 <= dt <= 0.40:
            u = (dt + 0.08) / 0.48
            op = math.sin(u * math.pi) * 0.62
            if op <= 0.02:
                continue
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            lx = (180.0 + u * 420.0) if side > 0 else (900.0 - u * 420.0)
            ly = 380.0 + u * 350.0
            g1 = np.exp(-(((xx - lx) / 380.0) ** 2 + ((yy - ly) / 560.0) ** 2))
            g2 = np.exp(-(((xx - (W - lx)) / 420.0) ** 2 + ((yy - (ly + 480.0)) / 620.0) ** 2))
            arr = np.array(canvas_im, dtype=np.float32)
            add_r = (255.0 * g1 + 90.0 * g2) * op
            add_g = (175.0 * g1 + 235.0 * g2) * op
            add_b = (85.0 * g1 + 255.0 * g2) * op
            # True Screen blend: 255 - (255 - A)*(255 - B)/255
            for c_i, add_c in enumerate([add_r, add_g, add_b]):
                b_c = np.clip(add_c, 0.0, 255.0)
                arr[:, :, c_i] = 255.0 - (255.0 - arr[:, :, c_i]) * (255.0 - b_c) / 255.0
            return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    return canvas_im

# ======================================================================
# 5. TIMELINE DATA — HIGH-DENSITY CINEMA PACING (Every 2-3s a fresh beat!)
# ======================================================================
ZOOM_BEATS = [
    (0.00, 1.02),
    (2.10, 1.08),
    (3.55, 1.02),
    (9.58, 1.14),   # Punch-in on "Băn khoăn?"
    (12.80, 1.04),  # Normal warm room
    (15.00, 1.09),  # "Mong con phát triển khỏe mạnh"
    (17.96, 1.16),  # LƯU Ý 1 punch-in!
    (20.15, 1.08),  # 3 YẾU TỐ
    (22.35, 1.13),  # ĐỘ TUỔI
    (29.04, 1.17),  # LƯU Ý 2 punch-in!
    (31.20, 1.09),  # CHIỀU CAO
    (34.36, 1.16),  # ĐIỂM 3 — BOJOMI!
    (39.54, 1.07),  # HIỆP ĐỒNG + LogoBar
    (42.35, 1.14),  # Orbital Rings + 418mg CANXI
    (46.10, 1.08),  # TẢO BIỂN ĐỎ
    (49.02, 1.14),  # 779 IU D3
    (51.65, 1.08),  # 170mcg K2
    (59.30, 1.15),  # CTA NHẮN NGAY
    (62.10, 1.08),  # ĐỐI CHIẾU
]

def get_snappy_zoom(t):
    """Crisp 7-frame (0.23s) cubic snap-ease on zoom changes + gentle micro-drift!"""
    cur_z = ZOOM_BEATS[0][1]
    for i in range(len(ZOOM_BEATS)):
        t0, z1 = ZOOM_BEATS[i]
        if t < t0:
            break
        z0 = ZOOM_BEATS[i - 1][1] if i > 0 else z1
        u = ease_out_cubic(min(1.0, (t - t0) / 0.24))
        cur_z = z0 + (z1 - z0) * u
    return cur_z

NUMBERS = [
    ("LƯU Ý", "1", 17.96, 20.10),
    ("LƯU Ý", "2", 29.04, 31.18),
    ("ĐIỂM",  "3", 34.36, 36.02),
]

# High-cadence single-line giant behind-head keywords at y=335 (hair overlaps bottom 15% = true 3D depth!)
KEYWORDS = [
    ("BĂN KHOĂN?",   9.58,  11.15, 205, (145, 125, 255), (235, 228, 255)),
    ("DINH DƯỠNG",  11.15,  12.75, 200, (92,  247, 224), (235, 255, 250)),
    ("3 YẾU TỐ",    20.12,  22.30, 225, (145, 125, 255), (238, 232, 255)),
    ("ĐỘ TUỔI",     22.30,  24.65, 225, (255, 215, 80),  (255, 248, 220)),
    ("CHIỀU CAO",   31.18,  34.25, 215, (92,  247, 224), (235, 255, 250)),
    ("HIỆP ĐỒNG",   39.54,  42.32, 210, (145, 125, 255), (238, 232, 255)),
    ("418mg CANXI", 42.35,  46.10, 185, (92,  247, 224), (240, 255, 252)),
    ("TẢO BIỂN ĐỎ", 46.10,  49.02, 188, (255, 215, 80),  (255, 248, 220)),
    ("779 IU D3",   49.02,  51.65, 210, (145, 125, 255), (238, 232, 255)),
    ("170mcg K2",   51.65,  54.25, 205, (92,  247, 224), (240, 255, 252)),
    ("NHẮN NGAY",   59.30,  62.10, 210, (255, 215, 80),  (255, 248, 220)),
    ("ĐỐI CHIẾU",   62.10,  66.20, 210, (145, 125, 255), (238, 232, 255)),
]

TILE_PLACES = [
    # 3 Overhead Hook Neon Tiles (-12, 0, +12 deg)
    ("height",  0.72,  3.38, 200,  305, 248, -12.0),
    ("meal",    0.88,  3.38, 540,  245, 256,   0.0),
    ("algae",   1.04,  3.38, 880,  305, 248,  12.0),
    # Body Obsidian Neon Tiles flying up with motion blur + corner bursts!
    ("meal",    9.65, 12.70, 235, 1360, 268,  -3.0),
    ("factors",20.15, 24.60, 845, 1360, 275,   2.0),
    ("height", 31.22, 34.20, 235, 1360, 268,  -2.0),
    ("algae",  42.45, 48.95, 845, 1360, 275,   2.0),
    ("d3k2",   49.08, 54.20, 235, 1360, 275,  -2.0),
    ("cta",    59.40, 66.15, 845, 1360, 275,   0.0),
]

BURSTS = [
    (200, 305, 0.80, 68), (540, 245, 0.96, 74), (880, 305, 1.12, 68),
    (325, 1275, 9.78, 64), (145, 1440, 9.95, 50),
    (755, 1270, 20.28, 66), (935, 1445, 20.46, 52),
    (325, 1275, 31.35, 64),
    (755, 1270, 42.58, 66), (935, 1445, 42.76, 52),
    (325, 1275, 49.20, 66),
    (755, 1270, 59.54, 66), (935, 1445, 59.72, 52),
]

RINGS_SPANS = [
    (42.35, 54.25),
    (59.30, 66.20),
]

LOGO_BAR_SPAN = (39.54, 42.32)

LEAKS = [
    (0.92,  1),
    (3.50, -1),
    (17.94, 1),
    (24.98,-1),
    (34.34, 1),
    (42.32,-1),
    (59.28, 1),
]

# Auto-compute background darkening windows from ALL behind/major animation spans!
# Guarantees 0% chance of giant text ever colliding with bright white wall text,
# while returning 100% smoothly to normal bright room during plain speaking segments!
def compute_bg_dim(t):
    spans = [(0.04, 3.42)]
    for _, _, t0, t1 in NUMBERS: spans.append((t0 - 0.15, t1 + 0.15))
    for _, t0, t1, _, _, _ in KEYWORDS: spans.append((t0 - 0.15, t1 + 0.15))
    spans.append((LOGO_BAR_SPAN[0] - 0.15, LOGO_BAR_SPAN[1] + 0.15))
    for t0, t1 in RINGS_SPANS: spans.append((t0 - 0.15, t1 + 0.15))
    val = 0.0
    for w0, w1 in spans:
        val = max(val, smooth_in_out_env(t, w0, w1, d_in=0.38, d_out=0.38))
    return val

def load_timeline_v4():
    tr = json.load(open(os.path.join(AROLL_DIR, "main_cut.json"), encoding="utf-8"))
    broll_spans = [
        (3.55,  9.15, "c02_meal",  "c02_study", "BỮA ĂN THẤT THƯỜNG • LỊCH HỌC DÀY ĐẶC"),
        (25.02, 28.92,"c05_bone",  "c05_vitd",  "BỔ SUNG CANXI & VITAMIN D3 CHO XƯƠNG"),
        (36.05, 39.48,"c06_algae", "c05_bone",  "BOJOMI AN VƯỢNG • CANXI TỪ TẢO BIỂN ĐỎ"),
        (54.35, 59.18,"c09_cup",   "c09_grains","1 GÓI TIỆN LỢI • ĐỦ VI CHẤT MỖI NGÀY"),
    ]
    # Also skip captions during LogoBar so chest stays super clean!
    skip_ranges = [(0.0, 3.45), (39.50, 42.30)] + [(s[0] + 0.10, s[1] - 0.10) for s in broll_spans]
    words = [
        w for seg in tr["segments"] for w in seg["words"]
        if not any(a <= (w["start"] + w["end"]) * 0.5 <= b for a, b in skip_ranges)
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
        if not txt: continue
        if prev is not None and (w["start"] - prev["end"]) >= 0.34:
            flush_group()
        # Tight 1-2 words per line (max 11 chars) just like Foodtage T.captions!
        if line and (len(line) >= 2 or sum(len(x[0]) + 1 for x in line) + len(txt) > 12):
            flush_line()
        if len(cur) >= 3 and not line:
            flush_group()
        line.append([txt, round(w["start"], 3), round(w["end"], 3)])
        prev = w
        if re.search(r"[.,?!…:;]$", txt):
            flush_group()
    flush_group()

    GOLD_WORDS = {"dưỡng", "khỏe", "mạnh", "chế", "tuổi", "Bojomi", "Vượng", "tảo", "biển", "418mg", "779", "170mcg", "MK7"}
    ORCHID_WORDS = {"băn", "khoăn", "không", "cao", "hơn", "D3,", "K2,", "collagen", "nhắn", "quyết", "định"}
    STROKE_UP_WORDS = {"khỏe", "Bojomi", "418mg", "779", "170mcg", "nhắn"}

    cap_groups = []
    for i, g in enumerate(groups):
        last_end = g[-1][-1][2]
        nxt = groups[i + 1][0][0][1] if i + 1 < len(groups) else 66.40
        t1 = min(nxt, last_end + 0.42) if (nxt - last_end) > 0.55 else nxt
        cap_groups.append({"t0": g[0][0][1], "t1": t1, "lines": g})
    return broll_spans, cap_groups, GOLD_WORDS, ORCHID_WORDS, STROKE_UP_WORDS

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

def load_clip_frames(path):
    frames = []
    r = VideoReader(path)
    while True:
        f = r.read()
        if f is None: break
        frames.append(f)
    r.close()
    return frames

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv
    # 8 representative frames matching every visual archetype in video mẫu.mov!
    test_frames = {int(round(ts * FPS)) for ts in [1.35, 5.80, 14.20, 18.70, 21.00, 37.50, 40.80, 44.50]}
    test_saved = []

    aroll_path = os.path.join(AROLL_DIR, "main_cut.mp4")
    matte_path = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

    print("Loading 7 distinct 1080x1920 B-roll clips...")
    broll_clips = {
        "c02_meal":   load_clip_frames(os.path.join(MEDIA_DIR, "broll_c02_meal.mp4")),
        "c02_study":  load_clip_frames(os.path.join(MEDIA_DIR, "broll_c02.mp4")),
        "c05_bone":   load_clip_frames(os.path.join(MEDIA_DIR, "broll_c05.mp4")),
        "c05_vitd":   load_clip_frames(os.path.join(MEDIA_DIR, "broll_c05_vitd.mp4")),
        "c06_algae":  load_clip_frames(os.path.join(MEDIA_DIR, "broll_c06.mp4")),
        "c09_cup":    load_clip_frames(os.path.join(MEDIA_DIR, "broll_c09.mp4")),
        "c09_grains": load_clip_frames(os.path.join(MEDIA_DIR, "broll_c09_grains.mp4")),
    }

    broll_spans, cap_groups, GOLD_WORDS, ORCHID_WORDS, STROKE_UP_WORDS = load_timeline_v4()

    legal_sp, _ = render_glow_text_sprite(
        "Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh",
        FONT_SUB, 21, (225, 232, 238), glow_rad=0
    )

    reader_a = VideoReader(aroll_path)
    reader_m = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", matte_path, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE
    )

    raw_vid_out = os.path.join(PROJ_DIR, "_v4_video_only.mp4")
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

        rgb = grade_aroll(rgb_raw)
        matte = np.frombuffer(mbuf, dtype=np.uint8).reshape((H, W)).astype(np.float32) / 255.0
        t = frame_idx / FPS

        # 1. Snappy Smooth Camera Zoom around speaker face [540, 660]
        z = get_snappy_zoom(t)
        if z > 1.003:
            cw, ch = int(round(W / z)), int(round(H / z))
            x0 = max(0, min(W - cw, int(round(540 - cw * 0.5))))
            y0 = max(0, min(H - ch, int(round(660 - ch * (660.0 / H)))))
            fg_im = Image.fromarray(rgb[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
            m_im  = Image.fromarray((matte[y0:y0+ch, x0:x0+cw] * 255.0).astype(np.uint8), "L").resize((W, H), Image.Resampling.BILINEAR)
            fg_rgb = np.array(fg_im)
            m_arr  = np.array(m_im, dtype=np.float32) / 255.0
        else:
            fg_im = Image.fromarray(rgb, "RGB")
            fg_rgb = rgb
            m_arr = matte

        # 2. Normal Room Background vs Deep Cinema Bokeh Darkening when Animations Appear!
        dim = compute_bg_dim(t)
        if dim <= 0.005:
            comp_im = fg_im.convert("RGBA")
        else:
            # Fast lens bokeh defocus (downscale 6x -> blur -> upscale) melts wall text 100% cleanly!
            small_bg = fg_im.resize((180, 320), Image.Resampling.BILINEAR)
            small_blur = small_bg.filter(ImageFilter.GaussianBlur(radius=max(0.8, 7.5 * dim)))
            bg_bokeh = np.array(small_blur.resize((W, H), Image.Resampling.BILINEAR), dtype=np.float32)

            # Deep 88% cinema darkening with subtle midnight-indigo studio falloff so neon glows POP!
            bg_factor = 1.0 - 0.88 * dim
            bg_dark = np.zeros_like(bg_bokeh)
            bg_dark[:, :, 0] = bg_bokeh[:, :, 0] * bg_factor * (1.0 - 0.18 * dim)
            bg_dark[:, :, 1] = bg_bokeh[:, :, 1] * bg_factor * (1.0 - 0.08 * dim)
            bg_dark[:, :, 2] = bg_bokeh[:, :, 2] * bg_factor + 14.0 * dim
            comp_im = Image.fromarray(np.clip(bg_dark, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

            # Layer A (lowest behind speaker): Orbital Rings (T.ringsBg) — placed BELOW keywords per trap #24!
            for r0, r1 in RINGS_SPANS:
                draw_rings_bg_v4(comp_im, t, r0, r1)

            # Layer B (behind speaker): Giant Neon Numbers 1 / 2 / 3 + Electric Bolt (tucked behind head/shoulder!)
            for lbl, dig, t0, t1 in NUMBERS:
                env_n = smooth_in_out_env(t, t0, t1, d_in=0.16, d_out=0.18)
                if env_n > 0.01:
                    dt = t - t0
                    u_l = ease_out_expo(min(1.0, dt / (6 * F)))
                    sc_l = 1.36 - 0.36 * u_l
                    sp_l, _ = render_glow_text_sprite(lbl, FONT_TITLE, 155, (75, 165, 255), (35, 95, 255), glow_col=(45, 130, 255), glow_rad=18)
                    paste_centered(comp_im, sp_l, 270, 355, scale=sc_l, opacity=env_n)

                    if dt >= 2 * F:
                        dt_d = dt - 2 * F
                        u_d = ease_out_expo(min(1.0, dt_d / (8 * F)))
                        sc_d = 1.45 - 0.45 * u_d - 0.04 * (dt_d / max(0.2, t1 - t0))
                        rot_d = -13.0 * (1.0 - u_d)
                        sp_d, _ = render_glow_text_sprite(
                            dig, FONT_CAP, 900, (165, 135, 255), (95, 225, 255),
                            glow_col=(95, 245, 255), glow_rad=28, stroke_col=(175, 252, 255), stroke_w=11
                        )
                        paste_centered(comp_im, sp_d, 760, 545, scale=sc_d, opacity=env_n, angle=rot_d)
                        draw_electric_bolt(comp_im, t, t0)

            # Layer C (tucked behind crown of hair cy=550 so black hair overlaps bottom ~20% above forehead = TRUE 3D DEPTH!):
            for kw_txt, t0, t1, fsz, c_top, c_bot in KEYWORDS:
                env_k = smooth_in_out_env(t, t0, t1, d_in=0.15, d_out=0.15)
                if env_k > 0.01:
                    dt = t - t0
                    u_k = ease_out_expo(min(1.0, dt / (6 * F)))
                    sp_k, _ = render_glow_text_sprite(kw_txt, FONT_TITLE, int(fsz * 1.06), c_top, c_bot, glow_col=c_top, glow_rad=16)
                    fit_k = min(1.0, 980.0 / max(1.0, float(sp_k.width - 70)))
                    sc_k = (1.26 - 0.26 * u_k) * fit_k
                    sw_p = (dt / max(0.3, t1 - t0)) * 1.25 - 0.12
                    paste_centered(comp_im, sp_k, 540, 550, scale=sc_k, opacity=env_k, sweep_prog=sw_p)

            # Layer D: Foreground Speaker + Real BOJOMI Desk Box (crisp RVM composite!)
            desk_line = np.clip((np.arange(H, dtype=np.float32) - 1505.0) / 52.0, 0.0, 1.0)[:, None]
            yy_b, xx_b = np.ogrid[0:H, 0:W]
            box_mask = np.exp(-((np.maximum(0.0, np.abs(xx_b - 680.0) - 185.0)) / 40.0) ** 2) * \
                       np.clip((yy_b - 1265.0) / 42.0, 0.0, 1.0) * np.clip((1560.0 - yy_b) / 40.0, 0.0, 1.0)
            fg_alpha = np.maximum(m_arr, np.maximum(desk_line, box_mask * 0.96))
            fg_lit = np.clip(fg_rgb.astype(np.float32) * (1.0 - 0.04 * dim), 0, 255).astype(np.uint8)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_lit, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

        # 3. Front Hook Typography (0.06 - 3.40s) — Snappy 6-frame punchIn like video mẫu.mov!
        env_hook = smooth_in_out_env(t, 0.06, 3.40, d_in=0.10, d_out=0.22)
        if env_hook > 0.01:
            comp_im = Image.alpha_composite(comp_im, CAP_CUSHION_IM)
            if t >= 0.06:
                u1 = ease_out_expo(min(1.0, (t - 0.06) / (7 * F)))
                sp_h1, _ = render_glow_text_sprite("Muốn con", FONT_WIDE, 92, (95, 175, 255), (35, 95, 255), glow_col=(55, 135, 255), glow_rad=16)
                paste_centered(comp_im, sp_h1, 540, 1055, scale=1.42 - 0.42 * u1, opacity=env_hook * min(1.0, (t - 0.06) / (2.5 * F)))
            if t >= 0.34:
                u2 = ease_out_expo(min(1.0, (t - 0.34) / (7 * F)))
                sp_h2, _ = render_glow_text_sprite("CAO", FONT_WIDE, 172, (255, 145, 55), (255, 55, 45), glow_col=(255, 95, 45), glow_rad=20)
                paste_centered(comp_im, sp_h2, 315, 1215, scale=1.50 - 0.50 * u2, opacity=env_hook * min(1.0, (t - 0.34) / (2.5 * F)))
            if t >= 0.56:
                u3 = ease_out_expo(min(1.0, (t - 0.56) / (7 * F)))
                sp_h3, _ = render_glow_text_sprite("Lớn!", FONT_SCRIPT, 182, (85, 255, 135), (35, 235, 95), glow_col=(65, 255, 115), glow_rad=24, stroke_col=(225, 255, 232), stroke_w=3)
                paste_centered(comp_im, sp_h3, 715, 1240, scale=1.40 - 0.40 * u3, opacity=env_hook * min(1.0, (t - 0.56) / (2.5 * F)))
            if t >= 1.72:
                u4 = ease_out_expo(min(1.0, (t - 1.72) / (7 * F)))
                sp_h4, _ = render_glow_text_sprite("Đã quan tâm bữa ăn hằng ngày?", FONT_CAP, 54, (240, 255, 252), (92, 247, 224), glow_col=(92, 247, 224), glow_rad=12)
                paste_centered(comp_im, sp_h4, 540, 1380, scale=1.18 - 0.18 * u4, opacity=env_hook * u4)

        # 4. Dark Obsidian Neon Tiles (T.tile + T.placeTile: 15-frame fly-up + motion blur!) + Bursts
        for ikey, t0, t1, cx, cy, sz, rot in TILE_PLACES:
            env_t = smooth_in_out_env(t, t0, t1, d_in=0.12, d_out=0.18)
            if env_t > 0.01:
                dt = t - t0
                u_pos = ease_out_expo(min(1.0, dt / (14 * F)))
                u_scl = ease_out_expo(min(1.0, dt / (10 * F)))
                fly_dist = 110.0 if cy < 400 else 240.0
                cur_y = cy + (1.0 - u_pos) * fly_dist
                cur_sc = (0.62 + 0.38 * u_scl) * (0.85 + 0.15 * env_t)
                v_blur = (1.0 - u_pos) * 18.0
                tile_im = render_obsidian_neon_tile(ikey, sz, t)
                paste_centered(comp_im, tile_im, cx, cur_y, scale=cur_sc, opacity=env_t, angle=rot, vblur_px=v_blur)

        for bx, by, bt0, bdiam in BURSTS:
            draw_burst(comp_im, bx, by, t, bt0, bdiam)

        # 5. Frosted Glass Bar (39.54 - 42.32s)
        draw_frosted_logo_bar(comp_im, t, LOGO_BAR_SPAN[0], LOGO_BAR_SPAN[1])

        # 6. Large, High-Contrast Glowing Captions (T.captions + true T.strokeUp outline burst!)
        for g in cap_groups:
            if g["t0"] <= t < g["t1"]:
                op_g = smoothstep((g["t1"] - t) / 0.14) if (g["t1"] - t) < 0.14 else 1.0
                # Subtle soft dark chest cushion so glowing cyan/gold/orchid text is 100% crisp!
                cush_arr = np.array(CAP_CUSHION_IM)
                cush_arr[:, :, 3] = (cush_arr[:, :, 3].astype(np.float32) * op_g).astype(np.uint8)
                comp_im.alpha_composite(Image.fromarray(cush_arr, "RGBA"))

                n_lines = len(g["lines"])
                y_base = 1085 if n_lines == 3 else (1115 if n_lines == 2 else 1145)
                lh = 78
                for li, ln in enumerate(g["lines"]):
                    word_renders = []
                    total_w = 0
                    gap = 20
                    for wi, (wtxt, ws, we) in enumerate(ln):
                        is_gold = wtxt in GOLD_WORDS
                        is_orch = wtxt in ORCHID_WORDS
                        k = 1.24 if (is_gold or is_orch) else 1.0
                        col = (255, 224, 75) if is_gold else ((222, 105, 255) if is_orch else (92, 247, 224))
                        sp, _ = render_glow_text_sprite(wtxt, FONT_CAP, 84 * k, col, glow_col=col, glow_rad=14)
                        adv = int(ImageDraw.Draw(comp_im).textlength(wtxt, font=get_font(FONT_CAP, 84 * k)))
                        word_renders.append((wtxt, ws, sp, adv, col, k))
                        total_w += adv + (gap if wi > 0 else 0)

                    cur_x = 540 - total_w // 2
                    cur_y = y_base + li * lh
                    for wtxt, ws, sp, adv, col, k in word_renders:
                        if t >= ws:
                            dt_w = t - ws
                            # Snappy 5-frame pop-up + blurIn (exact th-lib.jsx line 216!)
                            u_w = ease_out_expo(min(1.0, dt_w / (6 * F)))
                            wy = cur_y + (1.0 - u_w) * 28.0
                            blur_w = (1.0 - u_w) * 10.0
                            wcx = cur_x + adv // 2
                            paste_centered(comp_im, sp, wcx, wy, scale=0.94 + 0.06 * u_w, opacity=op_g * min(1.0, dt_w / (2.5 * F)), blur_px=blur_w)

                            # True Stroke Up outline shockwave (100% -> 240% hollow glowing outline!)
                            if wtxt in STROKE_UP_WORDS and (5 * F) <= dt_w <= (15 * F):
                                u_su = (dt_w - 5 * F) / (10 * F)
                                sc_su = 1.0 + 1.40 * (u_su ** 1.35)
                                op_su = smoothstep(1.0 - u_su) * 0.90 * op_g
                                sp_su, _ = render_glow_text_sprite(
                                    wtxt, FONT_CAP, 84 * k, col, glow_col=col, glow_rad=12,
                                    stroke_col=(220, 255, 248), stroke_w=4, no_fill=True
                                )
                                paste_centered(comp_im, sp_su, wcx, cur_y, scale=sc_su, opacity=op_su)
                        cur_x += adv + gap
                break

        # 7. True 3D Perspective Overlapping Split B-Roll Cards (0% stretch!)
        for st, en, top_k, bot_k, tag_txt in broll_spans:
            if st <= t <= en:
                dt = t - st
                tc = broll_clips[top_k]
                bc = broll_clips[bot_k]
                top_f = tc[min(len(tc) - 1, int(dt * FPS))]
                bot_f = bc[min(len(bc) - 1, int(dt * FPS))]
                comp_im = render_true_3d_broll(comp_im, top_f, bot_f, t, st, en, tag_txt)
                break

        # 8. Soft Warm Cinema Light Leaks (T.leaks Screen blend)
        comp_im = apply_light_leak(comp_im, t, LEAKS)

        # 9. Subtle Legal Bar at bottom
        bar_bot = Image.new("RGBA", (W, 50), (4, 8, 12, 145))
        comp_im.alpha_composite(bar_bot, dest=(0, H - 50))
        paste_centered(comp_im, legal_sp, 540, H - 25, opacity=0.88)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"v4_test_{len(test_saved):02d}.png")
            comp_im.convert("RGB").save(tp)
            test_saved.append(tp)
            frame_idx += 1
            continue

        writer.stdin.write(np.array(comp_im.convert("RGB"), dtype=np.uint8).tobytes())
        frame_idx += 1
        if frame_idx % 300 == 0:
            el = time.time() - t_start
            print(f"  Rendered {frame_idx}/1992 frames ({frame_idx / el:.1f} fps)", flush=True)

    if writer:
        writer.stdin.close()
        writer.wait()
    reader_a.close()
    reader_m.stdout.close()
    reader_m.wait()

    if test_mode and test_saved:
        # Build 4x2 high-res test comparison grid
        imgs = [Image.open(p).resize((360, 640), Image.Resampling.LANCZOS) for p in test_saved]
        grid = Image.new("RGB", (360 * 4, 640 * 2))
        for i, im in enumerate(imgs[:8]):
            grid.paste(im, ((i % 4) * 360, (i // 4) * 640))
        gp = os.path.join(CHECK_DIR, "v4_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved v4_test_grid.jpg:", gp)
    else:
        print(f"Done v4 video: {frame_idx} frames in {time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
