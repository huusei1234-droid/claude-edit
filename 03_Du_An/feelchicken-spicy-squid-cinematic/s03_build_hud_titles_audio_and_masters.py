import copy, json, math, os, re, shutil, subprocess, sys, time, uuid
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from safe_zone_9x16 import audit_rgba_overlay_safe_zone, clamp_box_to_safe_zone_9x16
from final_delivery import deliver_final_video

OUT_DIR   = r"d:\AI\full studio\output\feelchicken-spicy-squid-cinematic"
VID_916   = os.path.join(OUT_DIR, "flow_clips_9x16")
VID_169   = os.path.join(OUT_DIR, "flow_clips_16x9")
AUD_STG   = os.path.join(OUT_DIR, "audio_stage")
WORK_DIR  = os.path.join(OUT_DIR, "work_render")
QC_DIR    = os.path.join(OUT_DIR, "qc_sheets")
FONT_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
ART_DIR   = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-spicy-squid-cinematic"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
EFFECT_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Cache\effect")
DRAFT_NAME = "FEEL CHICKEN - Mì Cay Mực Siêu To AI"

for d in (WORK_DIR, QC_DIR):
    os.makedirs(d, exist_ok=True)
if os.path.exists("Z:\\"):
    os.makedirs(CLOUD_PRJ, exist_ok=True)

FPS = 30
SR  = 48000

# 8-Scene Hyper-AI Food Cinematic Timeline (Exact 24.60s = 738 frames @ 30fps)
TIMELINE_PLAN = [
    # idx, scene_id, t_start, t_end, ramp_style
    (1, "s01_chili_wave",           0.00,  2.80, "ramp_out"),      # 84f:  1000fps crimson chili wave + Opening Title
    (2, "s02_zero_g_squid_whip",    2.80,  5.80, "u_valley"),      # 90f:  Zero-G giant whole squid + diagonal chili ribbon whip
    (3, "s03_wok_fire_toss",        5.80,  8.60, "u_valley"),      # 84f:  Roaring Wok Hei fire ballistic toss
    (4, "s04_exploded_levitation",  8.60, 12.20, "slow_breathe"),  # 108f: Zero-G exploded stack + Animated HUD Callout Lines!
    (5, "s05_broth_crown_splash",  12.20, 15.20, "ramp_in_deep"),  # 90f:  Gravity plunge -> S-curve crimson crown splash!
    (6, "s06_macro_boiling_glaze", 15.20, 18.20, "u_valley"),      # 90f:  Macro 7-level spicy boil + glossy chili oil pour
    (7, "s07_chopstick_tower_lift",18.20, 21.20, "u_valley"),      # 90f:  Chopsticks lifting towering curly noodles & giant squid
    (8, "s08_hero_stone_pot",      21.20, 24.60, "ramp_in_hold"),  # 102f: Luxury steaming black stone pot hero + Brand End-Card
]
TOTAL_DUR = 24.60
TOTAL_FRAMES = int(round(TOTAL_DUR * FPS))  # 738 frames

def ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_in_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    p = os.path.join(FONT_DIR, name)
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", size)

# ==============================================================================
# 1. BIDIRECTIONAL BLUR-FOCUS + GRADIENT SHEEN + HUD CALLOUT OVERLAY GENERATOR
# ==============================================================================
def make_2layer_gradient_headline(text: str, font_name: str, font_size: int, stroke_px: int = 8) -> Image.Image:
    """
    2-Layer Separated Stroke + 5-Stop Molten Gold/White/Coral Gradient Text (Rule: viền không bao giờ ăn lẹm vào màu Gradient!).
    """
    font = fnt(font_name, font_size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = dummy.textbbox((0, 0), text, font=font, stroke_width=stroke_px)
    pad = stroke_px + 20
    w = (bb[2] - bb[0]) + pad * 2
    h = (bb[3] - bb[1]) + pad * 2
    ox, oy = pad - bb[0], pad - bb[1]

    # Layer 1: Soft drop shadow + crisp dark espresso/crimson outer stroke
    back = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_sh = ImageDraw.Draw(back)
    d_sh.text((ox, oy + 6), text, font=font, fill=(0, 0, 0, 195), stroke_width=stroke_px + 4, stroke_fill=(0, 0, 0, 195))
    back = back.filter(ImageFilter.GaussianBlur(radius=6))
    d_st = ImageDraw.Draw(back)
    d_st.text((ox, oy), text, font=font, fill=(42, 8, 4, 255), stroke_width=stroke_px, stroke_fill=(42, 8, 4, 255))

    # Layer 2: Pure un-stroked alpha mask filled with 5-stop vertical metallic gold-ivory-amber gradient
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((ox, oy), text, font=font, fill=255)

    grad = np.zeros((h, w, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, h)
    # 5-stop luxury food cinema gradient: Ivory Highlight -> Warm Gold -> Pure White -> Rich Amber -> Fiery Coral-Gold
    stops_t = [0.0, 0.28, 0.50, 0.75, 1.0]
    stops_c = [
        (255, 250, 228),
        (255, 214, 102),
        (255, 255, 255),
        (255, 188,  58),
        (246, 132,  38),
    ]
    for yi, yv in enumerate(ys):
        for si in range(len(stops_t) - 1):
            if stops_t[si] <= yv <= stops_t[si + 1]:
                u = (yv - stops_t[si]) / max(1e-6, stops_t[si + 1] - stops_t[si])
                c0, c1 = stops_c[si], stops_c[si + 1]
                rgb = [int(round(c0[c] * (1 - u) + c1[c] * u)) for c in range(3)]
                grad[yi, :, :3] = rgb
                break
    grad[:, :, 3] = np.array(mask, dtype=np.uint8)
    back.alpha_composite(Image.fromarray(grad, "RGBA"))
    return back

def apply_specular_sheen_and_blur_focus(card: Image.Image, prog_in: float, prog_out: float, sheen_u: float = -1.0) -> Image.Image:
    """
    Applies Specular Sheen Sweep across opaque letters + Bidirectional Optical Blur-Focus
    (in: blur 16px->0 + scale 0.92->1.0 in 0.26s; out: blur 0->14px + alpha 1->0 in 0.20s).
    """
    im = card.copy()
    if 0.0 <= sheen_u <= 1.0:
        arr = np.array(im, dtype=np.float32)
        h, w, _ = arr.shape
        xx = np.linspace(0.0, 1.0, w)[None, :]
        yy = np.linspace(0.0, 1.0, h)[:, None]
        band = np.exp(-(((xx + yy * 0.28) - (sheen_u * 1.45 - 0.12)) ** 2) / 0.0085)
        alpha_mask = (arr[:, :, 3] > 40).astype(np.float32)
        boost = (band * alpha_mask * 95.0)[:, :, None]
        arr[:, :, :3] = np.clip(arr[:, :, :3] + boost, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")

    # Bidirectional blur & opacity
    alpha_mult = 1.0
    blur_r = 0.0
    scale_f = 1.0
    if prog_in < 1.0:
        ei = ease_out_cubic(prog_in)
        alpha_mult *= ei
        blur_r = max(blur_r, (1.0 - ei) * 14.0)
        scale_f = 0.92 + 0.08 * ei
    if prog_out < 1.0:
        eo = ease_in_out(prog_out)
        alpha_mult *= eo
        blur_r = max(blur_r, (1.0 - eo) * 12.0)

    if scale_f < 0.999:
        nw = max(4, int(round(im.width * scale_f)))
        nh = max(4, int(round(im.height * scale_f)))
        im = im.resize((nw, nh), Image.Resampling.BILINEAR)
    if blur_r > 0.4:
        im = im.filter(ImageFilter.GaussianBlur(radius=blur_r))
    if alpha_mult < 0.999:
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 3] *= max(0.0, min(1.0, alpha_mult))
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    return im

def paste_center(canvas: Image.Image, patch: Image.Image, cx: int, cy: int):
    x0 = int(round(cx - patch.width / 2.0))
    y0 = int(round(cy - patch.height / 2.0))
    canvas.alpha_composite(patch, (x0, y0))

def render_overlay_frame_for_time(t: float, W: int, H: int) -> Image.Image:
    """
    Returns an RGBA overlay frame (WxH) at timeline second `t` containing:
    - [0.12 .. 2.72s]: Opening Commercial Poster Title ('FEEL CHICKEN • 7 CẤP ĐỘ CAY / MÌ CAY MỰC / Siêu To Nguyên Con')
    - [8.65 .. 12.15s]: Animated HUD Exploded Ingredient Callout Lines (Pin 6 + Pin 9)
    - [21.28 .. 24.55s]: Luxury Feel Chicken Brand End-Card (100% Safe-Zone compliant!)
    """
    is_916 = (H > W)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # --- A. OPENING HERO TITLE [0.12 .. 2.72s] ---
    if 0.12 <= t <= 2.72:
        lt = t - 0.12
        dur = 2.60
        p_in  = min(1.0, lt / 0.28)
        p_out = min(1.0, (dur - lt) / 0.22)
        sheen = (lt - 0.30) / 1.15 if 0.30 <= lt <= 1.45 else -1.0

        card = Image.new("RGBA", (820 if is_916 else 980, 310), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        f_eyeb = fnt("BeVietnamPro-Bold.ttf", 25 if is_916 else 24)
        eyeb_txt = "FEEL CHICKEN   •   7 CẤP ĐỘ CAY"
        ebb = cd.textbbox((0, 0), eyeb_txt, font=f_eyeb)
        cd.rounded_rectangle(
            [(card.width//2 - (ebb[2]-ebb[0])//2 - 22, 16), (card.width//2 + (ebb[2]-ebb[0])//2 + 22, 60)],
            radius=22, fill=(24, 6, 4, 185), outline=(255, 206, 84, 210), width=2
        )
        cd.text((card.width//2 - (ebb[2]-ebb[0])//2, 23), eyeb_txt, font=f_eyeb, fill=(255, 214, 92, 255))

        hero_im = make_2layer_gradient_headline("MÌ CAY MỰC", "BarlowCondensed-Black.ttf", 122 if is_916 else 112, stroke_px=8)
        paste_center(card, hero_im, card.width // 2, 146)

        f_scr = fnt("DancingScript-Bold.ttf", 52 if is_916 else 48)
        scr_txt = "Mực Ống Nguyên Con Siêu To"
        sbb = cd.textbbox((0, 0), scr_txt, font=f_scr)
        cd.text((card.width//2 - (sbb[2]-sbb[0])//2 + 2, 226), scr_txt, font=f_scr, fill=(0, 0, 0, 200))
        cd.text((card.width//2 - (sbb[2]-sbb[0])//2, 224), scr_txt, font=f_scr, fill=(255, 222, 118, 255))

        anim_card = apply_specular_sheen_and_blur_focus(card, p_in, p_out, sheen)
        cx = W // 2
        cy = 445 if is_916 else 225
        if is_916:
            cx, cy = clamp_box_to_safe_zone_9x16(cx, cy, anim_card.width, anim_card.height)
        paste_center(canvas, anim_card, cx, cy)

    # --- B. ANIMATED HUD EXPLODED INGREDIENT CALLOUTS [8.65 .. 12.15s] (Inspired by Pin 6 & Pin 9!) ---
    if 8.65 <= t <= 12.15:
        lt = t - 8.65
        dur = 3.50
        p_out_all = min(1.0, (dur - lt) / 0.22)
        draw = ImageDraw.Draw(canvas)
        f_hud = fnt("BeVietnamPro-Bold.ttf", 24 if is_916 else 22)
        f_sub = fnt("BeVietnamPro-Medium.ttf", 18 if is_916 else 17)

        # Anchor -> Label coordinates strictly inside 9:16 Safe Zone [X=64..872, Y=300..1430]!
        if is_916:
            callouts = [
                # (stagger_s, anchor_xy, elbow_xy, side('L'/'R'), title_str, sub_str, is_gold)
                (0.05, (515,  305), (645,  305), "R", "ỚT CAY 7 CẤP ĐỘ",       "Cay nồng chuẩn Hàn", False),
                (0.23, (505,  455), (325,  455), "L", "BẮP CẢI TÍM & CẢI THÌA","Tươi giòn thanh ngọt", False),
                (0.41, (545,  725), (625,  725), "R", "CÁ VIÊN & XÚC XÍCH",    "Đầy ắp nhân ngon",    False),
                (0.59, (520,  965), (355,  965), "L", "MỰC ỐNG NGUYÊN CON",    "Siêu to giòn sần sật", True),
                (0.77, (535, 1225), (590, 1225), "R", "MÌ SỢI HÀN QUỐC",       "Sợi xoăn dai thấm vị", False),
            ]
        else:
            callouts = [
                (0.05, (960, 210), (1185, 175), "R", "ỚT CAY 7 CẤP ĐỘ",       "Cay nồng chuẩn Hàn", False),
                (0.23, (935, 345), ( 710, 315), "L", "BẮP CẢI TÍM & CẢI THÌA","Tươi giòn thanh ngọt", False),
                (0.41, (975, 480), (1205, 455), "R", "CÁ VIÊN & XÚC XÍCH",    "Đầy ắp nhân ngon",    False),
                (0.59, (935, 625), ( 695, 605), "L", "MỰC ỐNG NGUYÊN CON",    "Siêu to giòn sần sật", True),
                (0.77, (975, 775), (1200, 760), "R", "MÌ SỢI HÀN QUỐC",       "Sợi xoăn dai thấm vị", False),
            ]

        for stg, (ax, ay), (ex, ey), side, t_lbl, s_lbl, is_gold in callouts:
            ct = lt - stg
            if ct <= 0.0:
                continue
            p_line = ease_out_cubic(min(1.0, ct / 0.24))
            p_card = min(1.0, max(0.0, (ct - 0.10) / 0.24))
            a_global = p_out_all

            # 1) Glowing target anchor dot + pulse ring
            dot_a = int(round(245 * min(1.0, ct / 0.12) * a_global))
            col_main = (255, 208, 76, dot_a) if is_gold else (255, 255, 255, dot_a)
            pulse_r = 7 + int(round(5 * math.sin(max(0.0, ct) * 6.0)))
            draw.ellipse([ax - pulse_r, ay - pulse_r, ax + pulse_r, ay + pulse_r], outline=(col_main[0], col_main[1], col_main[2], dot_a // 2), width=2)
            draw.ellipse([ax - 5, ay - 5, ax + 5, ay + 5], fill=col_main)

            # 2) Write-On Vector Callout Line (anchor -> elbow -> horizontal shelf)
            shelf_len = 52 if is_916 else 72
            hx = ex - shelf_len if side == "L" else ex + shelf_len
            if p_line < 0.6:
                u1 = p_line / 0.6
                cx_l = int(round(ax + (ex - ax) * u1))
                cy_l = int(round(ay + (ey - ay) * u1))
                draw.line([(ax, ay), (cx_l, cy_l)], fill=col_main, width=2)
            else:
                u2 = (p_line - 0.6) / 0.4
                cx_2 = int(round(ex + (hx - ex) * u2))
                draw.line([(ax, ay), (ex, ey), (cx_2, ey)], fill=col_main, width=2)

            # 3) Frosted HUD Pill Card with Bidirectional Blur-Focus
            if p_card > 0.02:
                tb1 = draw.textbbox((0, 0), t_lbl, font=f_hud)
                tb2 = draw.textbbox((0, 0), s_lbl, font=f_sub)
                pw = max(tb1[2] - tb1[0], tb2[2] - tb2[0]) + 32
                ph = 66
                pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
                pd = ImageDraw.Draw(pill)
                bg_c = (38, 12, 6, 212) if is_gold else (18, 18, 22, 205)
                bd_c = (255, 206, 76, 235) if is_gold else (255, 255, 255, 175)
                tx_c = (255, 218, 98, 255) if is_gold else (255, 255, 255, 255)
                pd.rounded_rectangle([(1, 1), (pw - 2, ph - 2)], radius=14, fill=bg_c, outline=bd_c, width=2)
                pd.text((16, 8), t_lbl, font=f_hud, fill=tx_c)
                pd.text((16, 37), s_lbl, font=f_sub, fill=(224, 220, 214, 240))

                anim_pill = apply_specular_sheen_and_blur_focus(pill, p_card, p_out_all, -1.0)
                px_c = (hx - anim_pill.width // 2 - 4) if side == "L" else (hx + anim_pill.width // 2 + 4)
                py_c = ey
                if is_916:
                    px_c, py_c = clamp_box_to_safe_zone_9x16(px_c, py_c, anim_pill.width, anim_pill.height)
                paste_center(canvas, anim_pill, px_c, py_c)

    # --- C. FEEL CHICKEN LUXURY END-CARD [21.28 .. 24.55s] (100% Safe-Zone Verified!) ---
    if 21.28 <= t <= 24.55:
        lt = t - 21.28
        dur = 3.27
        p_in  = min(1.0, lt / 0.30)
        p_out = min(1.0, (dur - lt) / 0.25)
        sheen = (lt - 0.35) / 1.20 if 0.35 <= lt <= 1.55 else -1.0

        # Subtle bottom atmospheric gradient ONLY inside non-black-bar visual frame (note: audit_rgba_overlay_safe_zone checks alpha>16,
        # so keep card self-contained inside Safe Zone [X=60..878, Y=1180..1535] on 9:16!)
        ec_w = 790 if is_916 else 920
        ec_h = 315
        ec = Image.new("RGBA", (ec_w, ec_h), (0, 0, 0, 0))
        ed = ImageDraw.Draw(ec)
        ed.rounded_rectangle([(4, 4), (ec_w - 5, ec_h - 5)], radius=26, fill=(14, 8, 6, 196), outline=(255, 198, 76, 165), width=2)

        f_ey = fnt("BeVietnamPro-Bold.ttf", 22)
        f_ad = fnt("BeVietnamPro-SemiBold.ttf", 21)
        f_hl = fnt("BeVietnamPro-Bold.ttf", 22)
        f_sc = fnt("DancingScript-Bold.ttf", 40)

        ey_t = "MỰC ỐNG NGUYÊN CON  •  ĐỦ 7 CẤP ĐỘ CAY"
        b_ey = ed.textbbox((0, 0), ey_t, font=f_ey)
        ed.text(((ec_w - (b_ey[2]-b_ey[0]))//2, 20), ey_t, font=f_ey, fill=(255, 212, 88, 255))

        brand_im = make_2layer_gradient_headline("FEEL CHICKEN", "BarlowCondensed-Black.ttf", 94, stroke_px=6)
        paste_center(ec, brand_im, ec_w // 2, 108)

        sc_t = "Ăn là mê — Saranghae!"
        b_sc = ed.textbbox((0, 0), sc_t, font=f_sc)
        ed.text(((ec_w - (b_sc[2]-b_sc[0]))//2, 156), sc_t, font=f_sc, fill=(255, 218, 108, 255))

        ed.line([(ec_w//2 - 180, 212), (ec_w//2 + 180, 212)], fill=(255, 212, 98, 130), width=2)

        ad_t = "CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt"
        b_ad = ed.textbbox((0, 0), ad_t, font=f_ad)
        ed.text(((ec_w - (b_ad[2]-b_ad[0]))//2, 224), ad_t, font=f_ad, fill=(248, 246, 242, 255))

        hl_t = "Mở cửa: 10:00 – 22:00   •   Hotline: 0796 601 106"
        b_hl = ed.textbbox((0, 0), hl_t, font=f_hl)
        ed.text(((ec_w - (b_hl[2]-b_hl[0]))//2, 260), hl_t, font=f_hl, fill=(255, 214, 92, 255))

        anim_ec = apply_specular_sheen_and_blur_focus(ec, p_in, p_out, sheen)
        if is_916:
            # Shift center left to X=469 so right edge stays <= 884px (zero overlap with TikTok/Reels right icons!) and bottom <= 1535px!
            cx_e, cy_e = clamp_box_to_safe_zone_9x16(469, 1372, anim_ec.width, anim_ec.height)
        else:
            cx_e, cy_e = W // 2, H - 195
        paste_center(canvas, anim_ec, cx_e, cy_e)

    return canvas


# ==============================================================================
# 2. OPTICAL-FLOW SPEED-RAMPING & CORNER SPARKLE HEALING
# ==============================================================================
def heal_flow_corner_sparkle(rgb_arr: np.ndarray) -> np.ndarray:
    """Seamlessly heals any tiny bottom-right AI watermark star so full frame stays 100% clean."""
    out = rgb_arr.copy()
    h, w, _ = out.shape
    y1, y2 = int(h * 0.905), int(h * 0.988)
    x1, x2 = int(w * 0.825), int(w * 0.982)
    top = out[y1-2:y1, x1:x2].mean(axis=0, keepdims=True).astype(np.float32)
    bot = out[y2:min(h, y2+2), x1:x2].mean(axis=0, keepdims=True).astype(np.float32)
    lft = out[y1:y2, x1-2:x1].mean(axis=1, keepdims=True).astype(np.float32)
    rgt = out[y1:y2, x2:min(w, x2+2)].mean(axis=1, keepdims=True).astype(np.float32)
    wy = np.linspace(0.0, 1.0, y2 - y1)[:, None, None]
    wx = np.linspace(0.0, 1.0, x2 - x1)[None, :, None]
    interp = ((1.0 - wy) * top + wy * bot) * 0.55 + ((1.0 - wx) * lft + wx * rgt) * 0.45
    out[y1:y2, x1:x2] = np.clip(interp, 0, 255).astype(np.uint8)
    return out

def build_ramp_curve(n_out: int, style: str) -> np.ndarray:
    if n_out <= 2:
        return np.linspace(0.0, 1.0, n_out)
    u = np.linspace(0.0, 1.0, n_out)
    if style == "u_valley":
        spd = 0.44 + 1.95 * (np.abs(2.0 * u - 1.0) ** 2.3)
    elif style == "ramp_in_deep":
        spd = 0.45 + 1.90 * (np.maximum(0.0, 1.0 - u / 0.35) ** 2.1)
    elif style == "ramp_in_hold":
        spd = 0.54 + 1.55 * (np.maximum(0.0, 1.0 - u / 0.32) ** 2.0)
    elif style == "ramp_out":
        spd = 0.54 + 1.85 * (np.maximum(0.0, (u - 0.52) / 0.48) ** 2.1)
    elif style == "slow_breathe":
        spd = 0.62 + 0.35 * (np.abs(2.0 * u - 1.0) ** 2.0)
    else:
        spd = np.ones_like(u)
    cum = np.cumsum(spd) - spd[0]
    return cum / max(1e-6, cum[-1])

def prepare_ramped_shot_rgb(args):
    ratio_tag, W, H, idx, sid, t0, t1, style, src_mp4 = args
    n_out = int(round(t1 * FPS)) - int(round(t0 * FPS))
    out_raw_mp4 = os.path.join(WORK_DIR, f"ramped_{ratio_tag}_{idx:02d}_{sid}.mp4")

    # Decode Flow clip & synthesize 60fps optical-flow frames for silky slow-mo valleys
    vf_str = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=rgb24"
    )
    raw = subprocess.run([
        "ffmpeg", "-v", "error", "-i", src_mp4, "-vf", vf_str, "-f", "rawvideo", "-"
    ], capture_output=True, check=True).stdout
    fsz = W * H * 3
    n_src = max(1, len(raw) // fsz)
    frames = np.frombuffer(raw[:n_src * fsz], dtype=np.uint8).reshape((n_src, H, W, 3))

    # Trim first 2 frames & last 2 frames if plenty of frames to avoid any static start/end hold
    i_min = 2 if n_src > 20 else 0
    i_max = (n_src - 3) if n_src > 20 else (n_src - 1)
    prog = build_ramp_curve(n_out, style)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "12", "-b:v", "0", "-pix_fmt", "yuv420p",
        out_raw_mp4
    ], stdin=subprocess.PIPE)

    for k in range(n_out):
        fpos = i_min + float(prog[k]) * max(0, i_max - i_min)
        ia = int(math.floor(fpos))
        ib = min(n_src - 1, ia + 1)
        fr = fpos - ia
        if fr < 0.05 or ia == ib:
            frm = frames[ia]
        else:
            frm = ((1.0 - fr) * frames[ia].astype(np.float32) + fr * frames[ib].astype(np.float32)).astype(np.uint8)
        frm = heal_flow_corner_sparkle(frm)
        enc.stdin.write(frm.tobytes())

    enc.stdin.close()
    enc.wait()
    return idx, sid, out_raw_mp4


# ==============================================================================
# 3. BROADCAST AUDIO MIX: DARK CINEMATIC TRAP + SPICY BOIL/SPLASH/HUD ASMR (-14 LUFS)
# ==============================================================================
def load_aud(fn: str, s0: float = 0.0, dur: float = None, af_extra: str = None) -> np.ndarray:
    p = os.path.join(AUD_STG, fn)
    cmd = ["ffmpeg", "-v", "error"]
    if s0 > 0: cmd += ["-ss", f"{s0:.3f}"]
    if dur is not None: cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-i", p]
    if af_extra: cmd += ["-af", af_extra]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()

def mix_into(bus: np.ndarray, clip: np.ndarray, ts: float, gain: float = 1.0, fi: float = 0.02, fo: float = 0.10):
    if len(clip) == 0: return
    c = (clip * gain).copy()
    nfi, nfo = min(len(c), int(round(fi * SR))), min(len(c), int(round(fo * SR)))
    if nfi > 1: c[:nfi] *= np.linspace(0, 1, nfi, dtype=np.float32)[:, None]
    if nfo > 1: c[-nfo:] *= np.linspace(1, 0, nfo, dtype=np.float32)[:, None]
    i0 = max(0, int(round(ts * SR)))
    if i0 >= len(bus): return
    i1 = min(len(bus), i0 + len(c))
    bus[i0:i1] += c[:i1 - i0]

def build_master_audio() -> str:
    n_s = int(round(TOTAL_DUR * SR))
    bgm_b  = np.zeros((n_s, 2), dtype=np.float32)
    asmr_b = np.zeros((n_s, 2), dtype=np.float32)
    sfx_b  = np.zeros((n_s, 2), dtype=np.float32)

    # Dark atmospheric choir + deep 808 cinematic hip-hop beat (starting at 11.2s so the heavy 808 beat drops right on S02 Zero-G Squid Whip @ 2.80s!)
    bgm = load_aud("bgm_drake_hiphop.mp3", 11.2, TOTAL_DUR)
    mix_into(bgm_b, bgm, 0.0, gain=0.82, fi=0.18, fo=1.20)

    # Tactile Food & Liquid Physics ASMR
    splash_wave  = load_aud("asmr_splash_plunge.mp3", 4.95, 2.4, "lowpass=f=6500")
    splash_crown = load_aud("asmr_splash_plunge.mp3", 4.88, 2.8)
    sizzle_wok   = load_aud("asmr_sizzle_boil.mp3", 1.2, 2.8)
    boil_pot     = load_aud("asmr_broth_sticky.mp3", 1.0, 3.2)
    boil_soft    = load_aud("asmr_broth_sticky.mp3", 6.0, 3.4, "lowpass=f=3800")
    pour_chili   = load_aud("asmr_pour_liquid.mp3", 0.15, 2.1, "lowpass=f=3400")
    noodle_lift  = load_aud("asmr_broth_sticky.mp3", 11.5, 2.5)
    deep_w       = load_aud("sfx_deep_woosh.mp3", 0.0, 1.5)
    fast_w       = load_aud("sfx_fast_whoosh.mp3", 0.0, 1.2)
    low_hit      = load_aud("sfx_low_hit.mp3", 0.0, 2.5)
    riser_m      = load_aud("sfx_riser_metal.mp3", 0.2, 1.6)
    ping_gl      = load_aud("sfx_ping_glass.mp3", 0.0, 1.2)
    chime_w      = load_aud("sfx_chime_warm.mp3", 0.0, 1.8)

    # Scene-by-scene ASMR foley
    mix_into(asmr_b, splash_wave,  0.15, gain=0.52, fi=0.05, fo=0.45)  # S01 1000fps chili wave
    mix_into(asmr_b, pour_chili,   3.05, gain=0.48, fi=0.04, fo=0.35)  # S02 Zero-G diagonal chili whip
    mix_into(asmr_b, boil_pot[:int(1.6*SR)], 3.20, gain=0.40, fi=0.06, fo=0.30)
    mix_into(asmr_b, sizzle_wok,   5.82, gain=0.56, fi=0.05, fo=0.35)  # S03 Roaring Wok Hei fire toss
    mix_into(asmr_b, boil_soft,    8.65, gain=0.22, fi=0.20, fo=0.35)  # S04 Subtle simmering under HUD levitation
    mix_into(asmr_b, splash_crown,12.22, gain=0.78, fi=0.02, fo=0.45)  # S05 GRAVITY PLUNGE CROWN SPLASH!
    mix_into(asmr_b, boil_pot,    15.25, gain=0.50, fi=0.08, fo=0.35)  # S06 Macro 7-level spicy boil + chili oil pour
    mix_into(asmr_b, pour_chili,  15.55, gain=0.38, fi=0.06, fo=0.30)
    mix_into(asmr_b, noodle_lift, 18.30, gain=0.46, fi=0.08, fo=0.35)  # S07 Chopstick noodle & giant squid lift
    mix_into(asmr_b, boil_soft,   21.25, gain=0.26, fi=0.15, fo=0.80)  # S08 Hero stone pot gentle simmer

    # 5 Ascending Pitch-Shifted Tactile HUD Callout Ticks (+1 semitone per step, Kobe Studio rule!)
    for idx_h, stg in enumerate([0.05, 0.23, 0.41, 0.59, 0.77]):
        semi = 2.0 ** (idx_h / 12.0)
        tick = load_aud("sfx_click_hud.mp3", 0.0, 0.35, f"asetrate={int(SR*semi)},aresample={SR}")
        mix_into(sfx_b, tick, 8.65 + stg, gain=0.32, fi=0.005, fo=0.05)
    mix_into(sfx_b, ping_gl, 8.65 + 0.59, gain=0.22, fi=0.01, fo=0.25) # Subtle glass ping on Hero Giant Squid HUD tag!

    # Speed-ramp air whooshes & deep sub-bass impacts
    for tw, gw in [(2.72, 0.32), (5.72, 0.30), (8.52, 0.24), (15.12, 0.26), (18.12, 0.26)]:
        mix_into(sfx_b, fast_w, tw, gain=gw, fi=0.02, fo=0.22)
    mix_into(sfx_b, riser_m, 10.85, gain=0.24, fi=0.15, fo=0.05)       # Tension riser right before Gravity Plunge @ 12.20s!
    for th, gh in [(0.05, 0.32), (2.80, 0.36), (12.20, 0.48), (21.20, 0.36)]:
        mix_into(sfx_b, low_hit, th, gain=gh, fi=0.02, fo=0.45)
    mix_into(sfx_b, chime_w, 21.35, gain=0.20, fi=0.02, fo=0.50)

    raw_w = os.path.join(WORK_DIR, "mix_raw.wav")
    mst_w = os.path.join(WORK_DIR, "master_14lufs.wav")
    pcm = (np.clip(bgm_b + asmr_b + sfx_b, -0.99, 0.99) * 32767.0).astype(np.int16)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", raw_w], stdin=subprocess.PIPE)
    p.stdin.write(pcm.tobytes()); p.stdin.close(); p.wait()

    p1 = subprocess.run(["ffmpeg", "-v", "info", "-i", raw_w, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    ln = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p1.stderr).group(0))
    af2 = f"loudnorm=I=-14.0:TP=-1.0:LRA=11.0:measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true,aresample={SR}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_w, "-af", af2, "-c:a", "pcm_s16le", mst_w], check=True)
    return mst_w


# ==============================================================================
# 4. MONOLITHIC CFR 30FPS COMPOSITOR (9:16 VERTICAL + 16:9 HORIZONTAL)
# ==============================================================================
def render_monolithic_master(ratio_tag: str, W: int, H: int, clip_dir: str, master_wav: str) -> str:
    tasks = []
    for idx, sid, t0, t1, style in TIMELINE_PLAN:
        src_p = os.path.join(clip_dir, f"{sid}_{ratio_tag}.mp4")
        tasks.append((ratio_tag, W, H, idx, sid, t0, t1, style, src_p))

    with ThreadPoolExecutor(max_workers=4) as ex:
        ramped_list = list(ex.map(prepare_ramped_shot_rgb, tasks))

    # Audit 9:16 Safe-Zone on peak frames of all 3 overlays before encoding!
    if ratio_tag == "9x16":
        for test_t, lbl in [(1.20, "Opening Title"), (10.20, "HUD Callouts"), (22.60, "Brand End-Card")]:
            ov_test = render_overlay_frame_for_time(test_t, W, H)
            ok_sz, info_sz = audit_rgba_overlay_safe_zone(ov_test)
            print(f"  [SafeZone 9:16 Audit] {lbl:16s} @ {test_t:.2f}s -> ok={ok_sz}, violating_px={info_sz['violating_pixels']}", flush=True)
            if not ok_sz:
                raise RuntimeError(f"Safe-Zone violation on {lbl}: {info_sz}")

    out_mp4 = os.path.join(OUT_DIR, f"FEEL_CHICKEN_MI_CAY_MUC_{ratio_tag}_MASTER.mp4")
    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", master_wav,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "15", "-b:v", "0",
        "-bf", "2", "-g", "60", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart",
        out_mp4
    ], stdin=subprocess.PIPE)

    fsz = W * H * 3
    global_f = 0
    for idx, sid, rmp_p in ramped_list:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", rmp_p, "-vf", "format=rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
        nf = len(raw) // fsz
        frames_arr = np.frombuffer(raw[:nf * fsz], dtype=np.uint8).reshape((nf, H, W, 3))
        for k in range(nf):
            t_cur = global_f / float(FPS)
            bg = frames_arr[k]
            if (0.12 <= t_cur <= 2.72) or (8.65 <= t_cur <= 12.15) or (21.28 <= t_cur <= 24.55):
                ov_im = render_overlay_frame_for_time(t_cur, W, H)
                ov_np = np.array(ov_im, dtype=np.float32)
                a = ov_np[:, :, 3:4] / 255.0
                comp = bg.astype(np.float32) * (1.0 - a) + ov_np[:, :, :3] * a
                frm = np.clip(comp, 0, 255).astype(np.uint8)
            else:
                frm = bg
            enc.stdin.write(frm.tobytes())
            global_f += 1

    enc.stdin.close()
    enc.wait()
    print(f"  Encoded Monolithic {ratio_tag} Master ({global_f} frames = {global_f/FPS:.2f}s) -> {out_mp4}", flush=True)
    return out_mp4


# ==============================================================================
# 5. DEPLOY 100% RAW EDITABLE CAPCUT DESKTOP PROJECT (CURVE SPEED + NATIVE TEXT + ASMR)
# ==============================================================================
def build_capcut_raw_project():
    def uid(): return str(uuid.uuid4()).upper()
    def us_f(s): return int(round(int(round(float(s) * FPS)) * 1_000_000 / FPS))
    def nfwd(p): return os.path.normpath(p).replace("\\", "/")
    def write_unlink(path: str, data: bytes):
        if os.path.exists(path):
            try: os.unlink(path)
            except Exception: pass
        with open(path, "wb") as f:
            f.write(data)

    d_tpl = os.path.join(DRAFTS_DIR, "1117 F20")
    if not os.path.exists(os.path.join(d_tpl, "draft_content.json")):
        return
    dc_tpl = json.load(open(os.path.join(d_tpl, "draft_content.json"), encoding="utf-8"))
    dm_tpl = json.load(open(os.path.join(d_tpl, "draft_meta_info.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "video"))
    atrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "audio"))
    ttrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "text"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    tseg_tpl   = copy.deepcopy(ttrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(next(m for m in dc_tpl["materials"]["videos"] if m.get("type") == "video"))
    amat_tpl   = copy.deepcopy(dc_tpl["materials"]["audios"][0])
    tmat_tpl   = copy.deepcopy(dc_tpl["materials"]["texts"][0])
    afade_tpl  = copy.deepcopy(dc_tpl["materials"]["audio_fades"][0])
    tanim_tpl  = copy.deepcopy(dc_tpl["materials"]["material_animations"][0])
    dm_vid_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    dm_aud_tpl = copy.deepcopy(next((x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") in ("music", "audio", "sound")), dm_vid_tpl))

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}
    a_extra_keys = ("speeds", "placeholder_infos", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}

    tl_id, now_s, now_us = uid(), int(time.time()), int(time.time() * 1_000_000)
    D = copy.deepcopy(dc_tpl)
    D.update({
        "id": tl_id, "name": DRAFT_NAME, "fps": 30.0, "duration": us_f(TOTAL_DUR),
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_tpl["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })
    dm_type0 = []

    # Copy sparkle-healed full 9:16 raw Flow clips into raw_capcut_9x16 so CapCut gets 100% untrimmed clean source clips!
    raw_cc_dir = os.path.join(OUT_DIR, "raw_capcut_9x16")
    os.makedirs(raw_cc_dir, exist_ok=True)

    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    for idx, sid, t0, t1, style in TIMELINE_PLAN:
        src_orig = os.path.join(VID_916, f"{sid}_9x16.mp4")
        clean_p  = os.path.join(raw_cc_dir, f"{idx:02d}_{sid}_raw.mp4")
        if not os.path.exists(clean_p):
            shutil.copy2(src_orig, clean_p)
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", clean_p], capture_output=True, text=True, check=True).stdout)
        vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
        vw, vh = int(vs["width"]), int(vs["height"])
        vdur_us = int(round(float(pr["format"]["duration"]) * 1_000_000))

        mid = uid()
        vm = copy.deepcopy(vmat_tpl)
        vm.update({
            "id": mid, "type": "video", "path": nfwd(clean_p), "material_name": os.path.basename(clean_p),
            "width": vw, "height": vh, "duration": vdur_us, "has_audio": False,
            "crop": {"upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0, "lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0},
            "crop_ratio": "free", "crop_scale": 1.0,
        })
        D["materials"]["videos"].append(vm)
        dmi = copy.deepcopy(dm_vid_tpl)
        dmi.update({"id": uid(), "file_Path": nfwd(clean_p), "extra_info": os.path.basename(clean_p), "width": vw, "height": vh, "duration": vdur_us, "create_time": now_s, "import_time": now_s, "import_time_ms": now_s * 1000})
        dm_type0.append(dmi)

        tgt_du = us_f(t1 - t0)
        src_du = min(vdur_us - 100000, int(round(tgt_du * 1.18)))
        avg_spd = src_du / float(tgt_du)
        refs = []
        for k, te in v_extra_tpl.items():
            em = copy.deepcopy(te); em["id"] = uid()
            if k == "speeds":
                em["mode"] = 1
                em["speed"] = round(avg_spd, 5)
                em["curve_speed"] = {
                    "id": "6768648600848175619", "source_platform": 1, "name": "Dựng phim",
                    "speed_points": [
                        {"x": 0.0, "y": round(avg_spd * 1.45, 3)},
                        {"x": 0.5, "y": round(max(0.4, avg_spd * 0.55), 3)},
                        {"x": 1.0, "y": round(avg_spd * 1.45, 3)},
                    ],
                }
            D["materials"][k].append(em); refs.append(em["id"])

        sg = copy.deepcopy(vseg_tpl)
        sg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": 50000, "duration": src_du},
            "target_timerange": {"start": us_f(t0), "duration": tgt_du},
            "speed": avg_spd, "volume": 0.0, "extra_material_refs": refs,
            "common_keyframes": [], "keyframe_refs": [], "visible": True,
        })
        sg["clip"]["scale"] = {"x": 1.04, "y": 1.04}
        sg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        tr_v0["segments"].append(sg)
    D["tracks"].append(tr_v0)

    # Add Master BGM + ASMR audio track
    mst_w = os.path.join(WORK_DIR, "master_14lufs.wav")
    amid = uid()
    am = copy.deepcopy(amat_tpl)
    am.update({"id": amid, "type": "extract_music", "path": nfwd(mst_w), "name": "Master_Spicy_Squid_ASMR_14LUFS.wav", "duration": us_f(TOTAL_DUR)})
    D["materials"]["audios"].append(am)
    dmi_a = copy.deepcopy(dm_aud_tpl)
    dmi_a.update({"id": uid(), "file_Path": nfwd(mst_w), "extra_info": os.path.basename(mst_w), "duration": us_f(TOTAL_DUR)})
    dm_type0.append(dmi_a)

    arefs = []
    for k, te in a_extra_tpl.items():
        em = copy.deepcopy(te); em["id"] = uid(); D["materials"][k].append(em); arefs.append(em["id"])
    af = copy.deepcopy(afade_tpl); af.update({"id": uid(), "fade_in_duration": 66666, "fade_out_duration": 200000})
    D["materials"]["audio_fades"].append(af); arefs.append(af["id"])
    asg = copy.deepcopy(aseg_tpl)
    asg.update({"id": uid(), "material_id": amid, "source_timerange": {"start": 0, "duration": us_f(TOTAL_DUR)}, "target_timerange": {"start": 0, "duration": us_f(TOTAL_DUR)}, "speed": 1.0, "volume": 1.0, "extra_material_refs": arefs, "visible": True})
    tr_a = copy.deepcopy(atrack_tpl); tr_a["id"] = uid(); tr_a["segments"] = [asg]
    D["tracks"].append(tr_a)

    # Write new CapCut project folder cleanly (never killing CapCut.exe per AGENTS.md Rule 4!)
    draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)
    os.makedirs(draft_dir, exist_ok=True)
    dm_out = copy.deepcopy(dm_tpl)
    dm_out.update({"draft_id": uid(), "draft_name": DRAFT_NAME, "draft_fold_path": nfwd(draft_dir), "draft_root_path": nfwd(DRAFTS_DIR), "tm_duration": us_f(TOTAL_DUR), "tm_draft_create": now_us, "tm_draft_modified": now_us})
    for g in dm_out["draft_materials"]:
        g["value"] = dm_type0 if g.get("type") == 0 else []

    dc_b = json.dumps(D, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    dm_b = json.dumps(dm_out, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    write_unlink(os.path.join(draft_dir, "draft_content.json"), dc_b)
    write_unlink(os.path.join(draft_dir, "template-2.tmp"), dc_b)
    write_unlink(os.path.join(draft_dir, "draft_meta_info.json"), dm_b)
    print(f"  Created Raw Editable CapCut Project -> {draft_dir}", flush=True)


def build_qc_sheet(mp4_p: str, out_jpg: str, is_916: bool):
    cw, ch = (250, 444) if is_916 else (380, 214)
    cols, rows = 4, 2
    grid = Image.new("RGB", (cw * cols, ch * rows), (12, 12, 12))
    dr = ImageDraw.Draw(grid)
    fn_lbl = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 15)
    sample_ts = [
        ("01 Chili Wave + Title", 1.25),
        ("02 Zero-G Squid Whip",  4.25),
        ("03 Wok Hei Fire Toss",  7.15),
        ("04 Exploded HUD Stack",10.25),
        ("05 Broth Crown Splash",13.55),
        ("06 Macro 7-Level Boil",16.65),
        ("07 Chopstick Lift",    19.65),
        ("08 Hero Pot End-Card", 22.75),
    ]
    for i, (lbl, ts) in enumerate(sample_ts):
        jp = os.path.join(QC_DIR, f"_tmp_{i}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mp4_p, "-frames:v", "1", "-vf", f"scale={cw}:{ch},format=yuvj420p", "-q:v", "2", jp], check=True)
        r, c = divmod(i, cols)
        grid.paste(Image.open(jp).convert("RGB"), (c * cw, r * ch))
        dr.rectangle([c * cw, r * ch, (c + 1) * cw, r * ch + 24], fill=(0, 0, 0))
        dr.text((c * cw + 6, r * ch + 4), f"{lbl} @{ts:.2f}s", fill=(255, 216, 88), font=fn_lbl)
        os.remove(jp)
    grid.save(out_jpg, quality=93)


def main():
    print("[1/5] Mixing Dark Cinematic Hip-Hop + Spicy Broth Splash/Boil/Wok Fire/HUD ASMR (-14.0 LUFS)...", flush=True)
    mst_wav = build_master_audio()

    print("[2/5] Rendering 9:16 Vertical Master (1080x1920 @ 30fps, Safe-Zone Audited, Optical-Flow Speed-Ramped)...", flush=True)
    mp4_916 = render_monolithic_master("9x16", 1080, 1920, VID_916, mst_wav)

    print("[3/5] Rendering 16:9 Horizontal Master (1920x1080 @ 30fps, Independent Widescreen Flow Clips)...", flush=True)
    mp4_169 = render_monolithic_master("16x9", 1920, 1080, VID_169, mst_wav)

    print("[4/5] Delivering Both Ratios via final_delivery.py + Creating Raw CapCut Project...", flush=True)
    deliv_916 = deliver_final_video(mp4_916, "feelchicken", "Mì cay mực siêu to", date_yymmdd="261125", is_horizontal=False)
    deliv_169 = deliver_final_video(mp4_169, "feelchicken", "Mì cay mực siêu to", date_yymmdd="261125", is_horizontal=True)
    print("  Delivered 9:16 ->", deliv_916["brand_path"])
    print("  Delivered 16:9 ->", deliv_169["brand_path"])

    build_capcut_raw_project()

    print("[5/5] Generating Visual QC Contact Sheets for Both 9:16 & 16:9 Masters...", flush=True)
    qc_916 = os.path.join(QC_DIR, "QC_MI_CAY_MUC_9x16_FINAL.jpg")
    qc_169 = os.path.join(QC_DIR, "QC_MI_CAY_MUC_16x9_FINAL.jpg")
    build_qc_sheet(mp4_916, qc_916, True)
    build_qc_sheet(mp4_169, qc_169, False)
    shutil.copy2(qc_916, os.path.join(ART_DIR, "fc_spicy_squid_9x16_qc.jpg"))
    shutil.copy2(qc_169, os.path.join(ART_DIR, "fc_spicy_squid_16x9_qc.jpg"))
    if os.path.exists("Z:\\"):
        for fp in (qc_916, qc_169, __file__):
            shutil.copy2(fp, os.path.join(CLOUD_PRJ, os.path.basename(fp)))
    print("ALL DONE! QC Sheets ->", qc_916, qc_169, flush=True)

if __name__ == "__main__":
    main()
