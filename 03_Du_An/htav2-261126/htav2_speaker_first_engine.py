import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"C:\AI\full studio\output\batch-htav-261125")

from batch_step6_render_all_17 import (
    W, H, FPS, FONT_TITLE, FONT_BLACK, FONT_EBOLD, FONT_BOLD, FONT_SERIF,
    get_font, clamp01, smoothstep, quintic, ease_out_cubic, ease_out_back,
    smooth_in_out_env, fit_cover, render_glow_text_sprite, paste_centered,
    make_luxury_playing_card, make_card_back, draw_landing_ripple,
)
from batch_v2_native_components import (
    make_kobe_saas_step_card, make_clean_broll_viewport,
    make_frosted_glass_card, make_editorial_paper_card,
    draw_tvc_gold_portal, make_collage_polaroid,
)

CENTER_X = 540
SAFE_LOW_MAX_W = 672  # X in [204..876] <= 884px AND 100% Dead-Center on X = 540!

_eng_cache = {}


def draw_4pt_star(canvas_im, cx, cy, r, col=(255, 244, 180), alpha=235, rot_deg=0.0):
    if r < 4 or alpha <= 5:
        return
    sz = int(r * 2.6)
    sp = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    c = sz * 0.5
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.20
        a = math.radians(i * 45 + rot_deg)
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=(*col, int(alpha)))
    paste_centered(canvas_im, sp, cx, cy)


# ==============================================================================
# 1. UNIFIED SIGNATURE BLACK-TEXT ON YELLOW-BG HOOK BANNER (ALL 14 VIDEOS!)
#    "và text hook là màu đen nền vàng đồng bộ các video sau này"
# ==============================================================================
def make_black_on_yellow_hook(line1_txt, line2_txt, brand_tag=None):
    key = ("YLW_BLK_HOOK_V3", line1_txt, line2_txt, brand_tag)
    if key in _eng_cache:
        return _eng_cache[key]

    dummy = ImageDraw.Draw(Image.new("RGBA", (16, 16)))
    l1 = str(line1_txt).strip().upper()
    l2 = str(line2_txt).strip().upper()

    f1 = get_font(FONT_EBOLD, 42)
    while f1.size > 26 and dummy.textbbox((0, 0), l1, font=f1)[2] > 836:
        f1 = get_font(FONT_EBOLD, f1.size - 2)

    f2 = get_font(FONT_BLACK, 58)
    while f2.size > 32 and dummy.textbbox((0, 0), l2, font=f2)[2] > 848:
        f2 = get_font(FONT_BLACK, f2.size - 2)

    b1 = dummy.textbbox((0, 0), l1, font=f1)
    b2 = dummy.textbbox((0, 0), l2, font=f2)
    tw = max(b1[2] - b1[0], b2[2] - b2[0])
    bw = min(908, max(620, int(tw + 76)))
    bh = int((b1[3] - b1[1]) + (b2[3] - b2[1]) + (56 if not brand_tag else 78))

    pad = 22
    im = Image.new("RGBA", (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + bw, pad + bh + 10], radius=30, fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    yy = np.linspace(0.0, 1.0, bh, dtype=np.float32)[:, None, None]
    c_top = np.array([[[255, 232, 56]]], dtype=np.float32)
    c_bot = np.array([[[255, 196, 0]]],  dtype=np.float32)
    y_rgb = np.clip(c_top * (1.0 - yy) + c_bot * yy, 0, 255).astype(np.uint8)
    body  = Image.fromarray(np.repeat(y_rgb, bw, axis=1), "RGB").convert("RGBA")
    mask  = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=30, fill=255)
    bl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bl.paste(body, (pad, pad), mask=mask)
    im = Image.alpha_composite(im, bl)

    d = ImageDraw.Draw(im)
    x0, y0 = pad, pad
    d.rounded_rectangle([x0, y0, x0 + bw - 1, y0 + bh - 1], radius=30, outline=(255, 255, 255, 255), width=5)
    d.rounded_rectangle([x0 + 7, y0 + 7, x0 + bw - 8, y0 + bh - 8], radius=24, outline=(18, 18, 20, 225), width=2)

    cy = y0 + 18
    if brand_tag:
        ftg = get_font(FONT_EBOLD, 19)
        btg = d.textbbox((0, 0), brand_tag.upper(), font=ftg)
        pw_t = (btg[2] - btg[0]) + 28
        tx0  = x0 + int((bw - pw_t) * 0.5)
        d.rounded_rectangle([tx0, cy - 2, tx0 + pw_t, cy + 28], radius=14, fill=(16, 16, 18, 245))
        d.text((tx0 + 14 - btg[0], cy + 13 - (btg[1] + btg[3]) * 0.5), brand_tag.upper(), font=ftg, fill=(255, 224, 48, 255))
        cy += 34

    tx1 = x0 + bw * 0.5 - (b1[2] - b1[0]) * 0.5 - b1[0]
    d.text((tx1, cy - b1[1]), l1, font=f1, fill=(20, 20, 22, 255))
    cy += (b1[3] - b1[1]) + 10

    tx2 = x0 + bw * 0.5 - (b2[2] - b2[0]) * 0.5 - b2[0]
    d.text((tx2, cy - b2[1] + 2), l2, font=f2, fill=(255, 255, 255, 165))
    d.text((tx2, cy - b2[1]),     l2, font=f2, fill=(10, 10, 12, 255))

    _eng_cache[key] = im
    return im


def make_yellow_pill_tag(txt, pt=34, max_w=780):
    key = ("YLW_TAG_V3", txt, pt, max_w)
    if key in _eng_cache:
        return _eng_cache[key]
    f = get_font(FONT_BLACK, pt)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    s = str(txt).strip()
    while f.size > 20 and dummy.textbbox((0, 0), s, font=f)[2] > max_w - 52:
        f = get_font(FONT_BLACK, f.size - 2)
    b = dummy.textbbox((0, 0), s, font=f)
    pw, ph = (b[2] - b[0]) + 52, (b[3] - b[1]) + 26
    pad = 14
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 6, pad + pw, pad + ph + 6], radius=ph // 2, fill=(0, 0, 0, 125))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=ph // 2, fill=(255, 214, 16, 252), outline=(255, 255, 255, 255), width=4)
    d.text((pad + 26 - b[0], pad + ph * 0.5 - (b[1] + b[3]) * 0.5), s, font=f, fill=(12, 12, 14, 255))
    _eng_cache[key] = im
    return im


# ==============================================================================
# 2. THREE DISTINCT 50/50 PUSH-DOWN SPLIT ARCHITECTURES (CHỊ HẰNG ON BOTTOM!)
#    A) split_dark_image1   (Dark Cyber Coordinate Grid + Live B-Roll — Image 1!)
#    B) split_kobe_pastel   (Light Pastel Dot-Matrix + White SaaS Window + Tilted Pill!)
#    C) split_editorial_chart (Warm Ivory Paper + Animated Dual-Curve Chart + B-Roll Inset!)
# ==============================================================================
def _get_split_bg(kind):
    key = ("SPLIT_HDR_BG", kind)
    if key in _eng_cache:
        return _eng_cache[key]
    if kind == "split_kobe_pastel":
        im = Image.new("RGBA", (W, 856), (238, 244, 254, 255))
        d = ImageDraw.Draw(im)
        for dx in range(0, 520, 32):
            for gx in ({540 - dx, 540 + dx}):
                for gy in range(24, 845, 32):
                    d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=(186, 200, 238, 210))
    elif kind == "split_editorial_chart":
        im = Image.new("RGBA", (W, 856), (251, 246, 235, 255))
        d = ImageDraw.Draw(im)
        for gy in range(60, 840, 56):
            d.line([(48, gy), (W - 48, gy)], fill=(218, 204, 178, 120), width=1)
        d.rectangle([42, 246, W - 42, 836], outline=(180, 108, 22, 110), width=2)
    else:  # "split_dark_image1"
        im = Image.new("RGBA", (W, 856), (16, 20, 28, 255))
        d = ImageDraw.Draw(im)
        for gx in range(0, W + 1, 36):
            d.line([(gx, 0), (gx, 856)], fill=(46, 56, 74, 72), width=1)
        for gy in range(0, 856, 36):
            d.line([(0, gy), (W, gy)], fill=(46, 56, 74, 72), width=1)
    _eng_cache[key] = im
    return im


def compose_push_down_split_varied(kind, frame_im, broll_rgb, t, w0, w1, cfg, brand_lbl, accent_rgb):
    u = smooth_in_out_env(t, w0, w1, 0.34, 0.34)
    if u <= 0.005:
        return frame_im.convert("RGBA"), 0.0

    dt = max(0.0, t - w0)
    comp = Image.new("RGBA", (W, H), (14, 18, 24, 255))
    shift_down = int(round(348.0 * u))
    comp.paste(frame_im.convert("RGBA"), (0, shift_down))

    hdr_y = int(round(-856 * (1.0 - u)))
    hdr = _get_split_bg(kind).copy()
    cl_c = cfg["clash"]

    if kind == "split_editorial_chart":
        # Warm Editorial Paper + Live Animated Dual Curve Chart + Mini Video Inset!
        ch_box = Image.new("RGBA", (896, 504), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch_box)
        cd.rounded_rectangle([0, 0, 895, 503], radius=24, fill=(255, 252, 244, 254), outline=(34, 28, 22, 235), width=3)
        ft_m = get_font(FONT_SERIF, 32)
        bt_m = cd.textbbox((0, 0), cl_c["rib_title"], font=ft_m)
        cd.text((448 - (bt_m[2] - bt_m[0]) * 0.5, 20), cl_c["rib_title"], font=ft_m, fill=(24, 20, 16, 255))
        for gy_c in [125, 225, 325, 415]:
            cd.line([(56, gy_c), (560, gy_c)], fill=(218, 206, 184, 190), width=1)
        prog_c = clamp01(dt / 1.25)
        pts_bad  = [(68, 370), (195, 118), (330, 398), (445, 412), (550, 418)]
        pts_good = [(68, 360), (195, 215), (330, 192), (445, 184), (550, 178)]
        ns = max(2, int(round(prog_c * len(pts_bad))))
        cd.line(pts_bad[:ns],  fill=(220, 38, 62, 240), width=6)
        cd.line(pts_good[:ns], fill=(14, 138, 86, 255), width=8)
        for px_c, py_c in pts_good[:ns]:
            cd.ellipse([px_c - 8, py_c - 8, px_c + 8, py_c + 8], fill=(14, 138, 86, 255), outline=(255, 255, 255, 255), width=2)
        fl_c = get_font(FONT_EBOLD, 20)
        cd.text((68, 76),  f"● CHUẨN: {cfg['fan']['ace'][3]}", font=fl_c, fill=(14, 126, 78, 255))
        cd.text((68, 444), f"● SAI LẦM: {cfg['fan']['left'][3]}", font=fl_c, fill=(212, 32, 56, 255))
        # Right inset live B-Roll inside Editorial Card
        vis_in = fit_cover(broll_rgb, 286, 364, 1.04).convert("RGBA")
        m_in = Image.new("L", (286, 364), 0)
        ImageDraw.Draw(m_in).rounded_rectangle([0, 0, 285, 363], radius=18, fill=255)
        ch_box.paste(vis_in, (584, 96), mask=m_in)
        cd.rounded_rectangle([584, 96, 869, 459], radius=18, outline=(180, 108, 22, 220), width=3)
        paste_centered(hdr, ch_box, CENTER_X, 530)
        div_col, div_bg, div_ink = (180, 108, 22), (253, 248, 236), (26, 20, 16)

    elif kind == "split_kobe_pastel":
        # Kobe Variant B Light Pastel UI Window (Browser Traffic Dots + Clean B-Roll + Tilted Pill!)
        vp = make_clean_broll_viewport(broll_rgb, 892, 496, cl_c["top_pill"], cl_c["top_foot"], accent_rgb=(54, 86, 251), light_ui=True, zoom=1.04)
        paste_centered(hdr, vp, CENTER_X, 532)
        div_col, div_bg, div_ink = (54, 86, 251), (255, 255, 255), (16, 22, 38)

    else:  # "split_dark_image1"
        vp = make_clean_broll_viewport(broll_rgb, 892, 506, cl_c["top_pill"], cl_c["top_foot"], accent_rgb=accent_rgb, light_ui=False, zoom=1.04)
        paste_centered(hdr, vp, CENTER_X, 530)
        div_col, div_bg, div_ink = accent_rgb, (255, 252, 240), (16, 24, 38)

    comp.paste(hdr, (0, hdr_y))

    div_pill = Image.new("RGBA", (664, 66), (0, 0, 0, 0))
    dd = ImageDraw.Draw(div_pill)
    dd.rounded_rectangle([2, 2, 661, 63], radius=31, fill=(*div_bg, 253), outline=(*div_col, 235), width=4)
    f_d = get_font(FONT_BLACK, 29)
    s_d = f"{brand_lbl}  •  CHUYÊN GIA PHÂN TÍCH"
    bd = dd.textbbox((0, 0), s_d, font=f_d)
    dd.text((332 - (bd[2] - bd[0]) * 0.5, 32 - (bd[1] + bd[3]) * 0.5), s_d, font=f_d, fill=(*div_ink, 255))
    paste_centered(comp, div_pill, CENTER_X, hdr_y + 826, angle=-1.2 if kind == "split_kobe_pastel" else 0.0)
    return comp, u


# ==============================================================================
# 3. FOUR DISTINCT BEHIND-HEAD RVM TECHNIQUES (CHỊ HẰNG SHARP IN FOREGROUND!)
#    A) bh_wide_broll      (Wide Feathered Live B-Roll Backdrop behind RVM head!)
#    B) bh_spinning_portal (TVC Circular Gold/Aqua Portal with Orbiting Pearls behind RVM head!)
#    C) bh_dual_polaroids  (2 Washi-Tape Live Polaroids Flanking behind RVM shoulders!)
#    D) bh_dna_keyword     (Kobe 22-Column Double-Helix Wave + Giant Metallic Keyword behind RVM head!)
# ==============================================================================
_BROLL_BACK_MASK = None
def _get_broll_backdrop_mask(w=956, h=690):
    global _BROLL_BACK_MASK
    if _BROLL_BACK_MASK is not None:
        return _BROLL_BACK_MASK
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=36, fill=255)
    arr = np.array(m, dtype=np.float32) * np.clip((h - np.arange(h, dtype=np.float32)) / 155.0, 0.0, 1.0)[:, None]
    _BROLL_BACK_MASK = Image.fromarray(arr.astype(np.uint8), "L")
    return _BROLL_BACK_MASK


def compose_behind_head_varied(kind, frame_im, fg_rgb, m_arr, desk_keep, brolls, t, w0, w1, cfg, accent_rgb):
    env = smooth_in_out_env(t, w0, w1, 0.28, 0.28)
    if env <= 0.01:
        return frame_im.convert("RGBA")
    dt = max(0.0, t - w0)

    bg_blur = frame_im.filter(ImageFilter.GaussianBlur(radius=4.5 * env))
    yy_w = np.clip((1160.0 - np.arange(H, dtype=np.float32)) / 340.0, 0.0, 1.0)[:, None, None]
    bg_arr = np.array(frame_im, dtype=np.float32) * (1.0 - env * yy_w * 0.60) + \
             np.array(bg_blur, dtype=np.float32) * (env * yy_w * 0.20)
    comp = Image.fromarray(np.clip(bg_arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    if kind == "bh_wide_broll":
        bw, bh = 956, 690
        br_rgb = brolls[1][int((dt * 30) % len(brolls[1]))]
        vis = fit_cover(br_rgb, bw, bh, 1.04 + 0.03 * math.sin(dt * 0.9)).convert("RGBA")
        v_arr = np.array(vis, dtype=np.float32); v_arr[:, :, :3] *= 0.88
        vis = Image.fromarray(np.clip(v_arr, 0, 255).astype(np.uint8), "RGBA")
        mask = _get_broll_backdrop_mask(bw, bh)
        if env < 0.995:
            mask = Image.fromarray((np.array(mask, dtype=np.float32) * env).astype(np.uint8), "L")
        br_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bx0, by0 = (W - bw) // 2, 256
        br_l.paste(vis, (bx0, by0), mask=mask)
        ImageDraw.Draw(br_l).rounded_rectangle([bx0, by0, bx0 + bw - 1, by0 + bh - 80], radius=36, outline=(*accent_rgb, int(215 * env)), width=4)
        comp = Image.alpha_composite(comp, br_l)
        top_tag = cfg["clash"]["bot_pill"]

    elif kind == "bh_spinning_portal":
        # Circular Spinning Gold/Rose Portal centered behind RVM Head (cx=540, cy=505, diam=448)!
        br_rgb = brolls[1][int((dt * 30) % len(brolls[1]))]
        pt_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_tvc_gold_portal(pt_layer, br_rgb, t, cx=CENTER_X, cy=505, diam=444)
        draw_4pt_star(pt_layer, 272, 375, 22 + 5 * math.sin(t * 5.5), rot_deg=t * 40)
        draw_4pt_star(pt_layer, 808, 375, 22 + 5 * math.cos(t * 5.5), rot_deg=-t * 40)
        if env < 0.995:
            pa = np.array(pt_layer); pa[:, :, 3] = (pa[:, :, 3].astype(np.float32) * env).astype(np.uint8)
            pt_layer = Image.fromarray(pa, "RGBA")
        comp = Image.alpha_composite(comp, pt_layer)
        top_tag = cfg["fan"]["headline"]

    elif kind == "bh_dual_polaroids":
        # Two Washi-Tape Live Polaroids flanking behind Chị Hằng's head & shoulders (cx=254 & cx=826, cy=468)!
        b0 = brolls[0][int((dt * 30) % len(brolls[0]))]
        b2 = brolls[2][int((dt * 30 + 12) % len(brolls[2]))]
        p_l = make_collage_polaroid(b0, 356, 308, cfg["fan"]["left"][3], tape_rgb=(246, 132, 118))
        p_r = make_collage_polaroid(b2, 356, 308, cfg["fan"]["ace"][3],  tape_rgb=(126, 226, 174))
        u_l = ease_out_back(min(1.0, dt / 0.30), 1.10)
        u_r = ease_out_back(min(1.0, max(0.0, dt - 0.16) / 0.30), 1.10)
        paste_centered(comp, p_l, 254, 468 + (1.0 - u_l) * (-45.0), opacity=env * clamp01(dt / 0.16), angle=-7.5)
        if dt >= 0.14:
            paste_centered(comp, p_r, 826, 468 + (1.0 - u_r) * (-45.0), opacity=env * clamp01((dt - 0.14) / 0.16), angle=+7.5)
        top_tag = cfg["clash"]["rib_title"]

    else:  # "bh_dna_keyword"
        # 22-Column Double-Helix Sine Wave + Giant Metallic Keyword behind RVM hair!
        dna_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(dna_l)
        for ci in range(22):
            gx = 141 + ci * 38
            ph1 = t * 4.2 + ci * 0.36
            ya, yb = 385 + math.sin(ph1) * 42.0, 385 - math.sin(ph1) * 42.0
            dd.line([(gx, ya), (gx, yb)], fill=(*accent_rgb, int(95 * env)), width=2)
            dd.ellipse([gx - 8, ya - 8, gx + 8, ya + 8], fill=(*accent_rgb, int(235 * env)))
            dd.ellipse([gx - 8, yb - 8, gx + 8, yb + 8], fill=(255, 224, 82, int(235 * env)))
        comp = Image.alpha_composite(comp, dna_l)
        kw_s = cfg["keywords"][0][0] if cfg.get("keywords") else cfg["fan"]["ace"][3]
        sp_kw = render_glow_text_sprite(kw_s.upper(), FONT_TITLE, 142, (255, 236, 98), (242, 162, 24), glow_col=(255, 210, 62), glow_rad=14, stroke_col=(10, 14, 20), stroke_w=6)
        fk = min(1.0, 916.0 / max(1.0, sp_kw.width))
        paste_centered(comp, sp_kw, CENTER_X, 456 + (1.0 - env) * 18.0, scale_x=fk * (0.93 + 0.07 * env), opacity=env, sweep_prog=(dt / max(0.4, w1 - w0)) * 1.25)
        top_tag = cfg["fan"]["headline"]

    # Foreground sharp RVM Chị Hằng + Desk ALWAYS in front!
    fg_a = np.maximum(m_arr, desk_keep)
    comp = Image.alpha_composite(comp, Image.fromarray(np.dstack([fg_rgb, (fg_a * 255.0).astype(np.uint8)]), "RGBA"))

    if top_tag:
        pl = make_yellow_pill_tag(top_tag, pt=29, max_w=820)
        paste_centered(comp, pl, CENTER_X, 286, opacity=env)
    return comp


# ==============================================================================
# 4. FIVE DISTINCT OVERHEAD INGREDIENT / MECHANISM ARCHITECTURES (Y = 262..485!)
#    A) ov_kobe_highway   (Dashed Road Bar + 1->2->3 White Kobe SaaS Cards!)
#    B) ov_collector_fan  (Fanned 10-K-A Luxury Playing Cards + 3D Ace Flip!)
#    C) ov_viethan_bento  (3 Rounded Live-Video Bento Cells with Medical Badges!)
#    D) ov_saas_laser     (Glowing Laser Trim-Path Shooting Across 3 Frosted Glass Pods!)
#    E) ov_warning_tank   (Stacked Checklist Pills + Live Rising 5-Bar Escalation Tank!)
# ==============================================================================
def draw_overhead_varied(canvas_im, kind, t, w0, w1, brolls, cfg, brand_lbl, accent_rgb):
    env = smooth_in_out_env(t, w0, w1, 0.24, 0.24)
    if env <= 0.01:
        return
    dt = max(0.0, t - w0)
    fn_c = cfg["fan"]
    rf_c = cfg["riffle"]
    items = [fn_c["left"], fn_c["right"], fn_c["ace"]]
    d_cv = ImageDraw.Draw(canvas_im)

    if kind == "ov_kobe_highway":
        # Dashed Highway Road across Y = 372 + 1->2->3 White Kobe SaaS Cards!
        d_cv.rounded_rectangle([88, 352, 992, 392], radius=20, fill=(*accent_rgb, int(135 * env)))
        for dx_h in range(114, 966, 40):
            d_cv.line([(dx_h, 372), (dx_h + 20, 372)], fill=(255, 255, 255, int(235 * env)), width=4)
        for i, it in enumerate(items):
            st_i = i * 0.16
            if dt >= st_i:
                di = dt - st_i
                u_i = ease_out_back(min(1.0, di / 0.28), 1.10)
                c_acc = (228, 58, 74) if i == 0 else (accent_rgb if i == 1 else (222, 142, 14))
                card = make_kobe_saas_step_card(282, 208, i + 1, it[1], c_acc, it[3], it[4], tag_txt=it[5])
                cx_i = [218, 540, 862][i]
                paste_centered(canvas_im, card, cx_i, 372 + (1.0 - u_i) * (-48.0), opacity=env * clamp01(di / 0.15))
                draw_landing_ripple(canvas_im, cx_i, 476, di - 0.22, rx_max=86, ry_max=13, col=c_acc)

    elif kind == "ov_collector_fan":
        # 3-Card Fanned Collector Playing Cards (-13°, 0°, +13°) + 3D 180° Ace Flip!
        u_op = ease_out_back(min(1.0, dt / 0.40), 1.08)
        c_l = make_luxury_playing_card(236, 214, *items[0][:5], badge_txt=items[0][5])
        c_r = make_luxury_playing_card(236, 214, *items[1][:5], badge_txt=items[1][5])
        paste_centered(canvas_im, c_l, CENTER_X - 248 * u_op, 376 + 10 * u_op, opacity=env, angle=-12.5 * u_op)
        paste_centered(canvas_im, c_r, CENTER_X + 248 * u_op, 376 + 10 * u_op, opacity=env, angle=+12.5 * u_op)
        u_fl = quintic(clamp01((dt - 0.28) / 0.46))
        cs_f = math.cos(u_fl * math.pi)
        c_a = make_card_back(252, 228, brand_lbl) if cs_f >= 0 else make_luxury_playing_card(252, 228, *items[2][:5], badge_txt=items[2][5])
        paste_centered(canvas_im, c_a, CENTER_X, 362, scale_x=max(0.06, abs(cs_f)), opacity=env, sweep_prog=((dt - 0.75) / 1.2) % 1.2 if dt > 0.75 else None)

    elif kind == "ov_viethan_bento":
        # 3 Rounded Live-Video Bento Cells Playing Simultaneously Above Chị Hằng!
        cxs = [214, 540, 866]
        cols_b = [(218, 22, 48), (14, 138, 76), (14, 138, 76)]
        for i in range(3):
            st_i = i * 0.14
            if dt >= st_i:
                ub = ease_out_back(min(1.0, (dt - st_i) / 0.26), 1.10)
                br_c = brolls[i % len(brolls)]
                frm = br_c[int((dt * 30 + i * 19) % len(br_c))]
                cw_b, ch_b = 292, 208
                vis = fit_cover(frm, cw_b, ch_b, 1.05).convert("RGBA")
                m_b = Image.new("L", (cw_b, ch_b), 0)
                ImageDraw.Draw(m_b).rounded_rectangle([0, 0, cw_b - 1, ch_b - 1], radius=22, fill=255)
                box = Image.new("RGBA", (cw_b + 10, ch_b + 10), (0, 0, 0, 0))
                box.paste(vis, (5, 5), mask=m_b)
                bd = ImageDraw.Draw(box)
                bd.rounded_rectangle([5, 5, cw_b + 4, ch_b + 4], radius=22, outline=(255, 255, 255, 255), width=4)
                bd.rounded_rectangle([12, ch_b - 44, cw_b - 2, ch_b - 2], radius=12, fill=(255, 255, 255, 246))
                fl = get_font(FONT_BLACK, 21)
                lbl_s = f"0{i+1}. {items[i][3].replace(chr(10), ' ')}"
                while fl.size > 13 and bd.textbbox((0, 0), lbl_s, font=fl)[2] > cw_b - 24:
                    fl = get_font(FONT_BLACK, fl.size - 1)
                bl_b = bd.textbbox((0, 0), lbl_s, font=fl)
                bd.text((5 + cw_b * 0.5 - (bl_b[2] - bl_b[0]) * 0.5, ch_b - 23 - (bl_b[1] + bl_b[3]) * 0.5), lbl_s, font=fl, fill=(*cols_b[i], 255))
                paste_centered(canvas_im, box, cxs[i], 370, scale_x=0.88 + 0.12 * ub, opacity=env)

    elif kind == "ov_saas_laser":
        # Glowing Golden Laser Trim-Path Shooting Across 3 Frosted Glass Dosage Pods!
        prog_l = clamp01(dt / 0.78)
        lx_end = int(218 + 644 * prog_l)
        d_cv.line([(218, 372), (862, 372)], fill=(*accent_rgb, int(85 * env)), width=5)
        d_cv.line([(218, 372), (lx_end, 372)], fill=(255, 236, 112, int(255 * env)), width=7)
        d_cv.ellipse([lx_end - 10, 372 - 10, lx_end + 10, 372 + 10], fill=(255, 255, 255, int(255 * env)))
        pods = [
            (rf_c["c1"][5], rf_c["c1"][3], rf_c["c1"][4]),
            (rf_c["c2"][5], rf_c["c2"][3], rf_c["c2"][4]),
            (rf_c["hero"][5], rf_c["hero"][6], rf_c["hero"][3]),
        ]
        for i, (bdg, tt, sb) in enumerate(pods):
            nx = [218, 540, 862][i]
            lit = (lx_end >= nx - 24)
            pod = make_frosted_glass_card(278, 198, bdg, tt.replace("\n", " "), sb,
                                          tint_rgb=(24, 58, 110) if lit else (12, 28, 54),
                                          rim_rgb=(255, 226, 98) if lit else accent_rgb)
            paste_centered(canvas_im, pod, nx, 372, scale_x=1.02 if lit else 0.94, opacity=env)

    else:  # "ov_warning_tank"
        # Left Stacked Checklist Pills (cx=368, w=540) + Right Rising 5-Bar Escalation Tank (cx=824, w=292)!
        # Outer bounds: [368-270 .. 824+146] = [98 .. 970] -> Midpoint = 534 ~ 540!
        for i in range(3):
            st_i = i * 0.16
            if dt >= st_i:
                pil = Image.new("RGBA", (544, 62), (0, 0, 0, 0))
                pd = ImageDraw.Draw(pil)
                c_p = (225, 38, 64) if i < 2 else (16, 148, 88)
                pd.rounded_rectangle([2, 2, 541, 59], radius=28, fill=(255, 255, 255, 248), outline=(*c_p, 235), width=3)
                fp = get_font(FONT_BLACK, 24)
                s_p = f"{'⚠' if i < 2 else '✓'}  {items[i][3]}: {items[i][4].splitlines()[0]}"
                while fp.size > 16 and pd.textbbox((0, 0), s_p, font=fp)[2] > 504:
                    fp = get_font(FONT_BLACK, fp.size - 1)
                bp = pd.textbbox((0, 0), s_p, font=fp)
                pd.text((22, 30 - (bp[1] + bp[3]) * 0.5), s_p, font=fp, fill=(*c_p, 255))
                paste_centered(canvas_im, pil, 372, 298 + i * 72, opacity=env)

        tank = Image.new("RGBA", (296, 222), (0, 0, 0, 0))
        td = ImageDraw.Draw(tank)
        td.rounded_rectangle([4, 4, 291, 217], radius=24, fill=(18, 24, 36, 246), outline=(242, 62, 82, 248), width=4)
        n_bars = min(5, max(1, int(dt / 0.36) + 1))
        b_cols = [(54, 162, 235), (82, 196, 148), (245, 198, 56), (245, 128, 42), (238, 48, 68)]
        for bi in range(n_bars):
            by1 = 178 - bi * 30
            td.rounded_rectangle([26, by1 - 22, 270, by1], radius=8, fill=(*b_cols[bi], 248))
        ftk = get_font(FONT_BLACK, 19)
        btk = td.textbbox((0, 0), "MỨC BÁO ĐỘNG!", font=ftk)
        td.text((148 - (btk[2] - btk[0]) * 0.5, 188), "MỨC BÁO ĐỘNG!", font=ftk, fill=(255, 218, 86, 255))
        paste_centered(canvas_im, tank, 822, 370, opacity=env)


# ==============================================================================
# 5. SURGICAL FULL-SCREEN B-ROLL + PACKSHOT (STRICTLY FOR 2.5-4s LIP-COVER!)
# ==============================================================================
def compose_fullscreen_lip_cover(broll_rgb, prods, t, s0, s1, badge_txt, title_txt, sub_txt, accent_rgb=(255, 214, 48)):
    dt = max(0.0, t - s0)
    vis = fit_cover(broll_rgb, W, H, 1.04 + 0.03 * math.sin(dt * 1.1)).convert("RGBA")
    arr = np.array(vis, dtype=np.float32)
    yy = np.arange(H, dtype=np.float32)
    top_v = np.clip((480.0 - yy) / 480.0, 0.0, 1.0) * 0.52
    bot_v = np.clip((yy - 820.0) / 720.0, 0.0, 1.0) * 0.78
    arr[:, :, :3] *= (1.0 - np.maximum(top_v, bot_v))[:, None, None]
    stage = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    if badge_txt:
        pl = make_yellow_pill_tag(badge_txt, pt=32, max_w=860)
        paste_centered(stage, pl, CENTER_X, 316)

    spec_card = make_frosted_glass_card(324, 248, "CHUẨN ĐỊNH LƯỢNG", title_txt, sub_txt, tint_rgb=(14, 34, 62), rim_rgb=accent_rgb)
    u_in = ease_out_back(min(1.0, dt / 0.28), 1.08)
    paste_centered(stage, spec_card, 382, 1025, scale_x=0.92 + 0.08 * u_in)

    if len(prods) >= 2:
        paste_centered(stage, prods[0], 668, 1012 + math.sin(t * 2.6) * 4.0, scale_x=0.54 * clamp01(dt / 0.22))
        paste_centered(stage, prods[1], 736, 1044 + math.sin(t * 2.6 + 0.8) * 4.0, scale_x=0.52 * clamp01(dt / 0.26))
    elif len(prods) == 1:
        paste_centered(stage, prods[0], 698, 1025 + math.sin(t * 2.6) * 4.5, scale_x=0.64 * clamp01(dt / 0.22))
    return stage


# ==============================================================================
# 6. SIX DISTINCT FACE-SAFE & BOX-SAFE SUBTITLE STYLES (X = 540, Y = 1122!)
# ==============================================================================
def render_speaker_subtitles(canvas_im, t, cap_groups, cfg, sub_style="glow_gold", cx=CENTER_X, y_base=1122, max_w=SAFE_LOW_MAX_W, base_pt=70, lh=80, single_line=False):
    gold_w = cfg.get("gold_words", set())
    emer_w = cfg.get("emer_words", set())
    rose_w = cfg.get("rose_words", set())

    for g in cap_groups:
        if g["t0"] <= t < g["t1"]:
            op_g = smoothstep((g["t1"] - t) / 0.16) if (g["t1"] - t) < 0.16 else 1.0
            lines_use = [[w for ln in g["lines"] for w in ln]] if single_line else g["lines"]
            gap = 14

            rendered_lines = []
            max_eff = 0.0
            for ln in lines_use:
                w_renders, tot_w = [], 0
                for wi, (wtxt, ws, we) in enumerate(ln):
                    clean_tok = wtxt.strip(".,?!:;\"'()")
                    is_g = (wtxt in gold_w or clean_tok in gold_w)
                    is_e = (wtxt in emer_w or clean_tok in emer_w)
                    is_r = (wtxt in rose_w or clean_tok in rose_w)
                    pt_u = base_pt * (1.10 if (is_g or is_e or is_r) else 1.0)

                    if sub_style == "kobe_white_pill":
                        ct = (37, 99, 235) if is_g else ((12, 138, 84) if is_e else ((220, 28, 66) if is_r else (15, 23, 42)))
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, ct, glow_rad=0, stroke_col=None, stroke_w=0)
                    elif sub_style == "warm_editorial":
                        ct = (180, 86, 10) if is_g else ((14, 118, 78) if is_e else ((192, 26, 58) if is_r else (24, 20, 16)))
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, ct, glow_rad=0, stroke_col=None, stroke_w=0)
                    elif sub_style == "viethan_stroke":
                        ct = (218, 8, 42) if (is_g or is_r) else (11, 138, 66)
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, ct, glow_rad=5, glow_col=(0, 0, 0), stroke_col=(255, 255, 255), stroke_w=9)
                    elif sub_style == "rose_bling":
                        ct, cb = ((255, 246, 186), (222, 152, 32)) if (is_g or is_e) else (((255, 192, 210), (235, 78, 118)) if is_r else ((255, 255, 255), (244, 230, 238)))
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, cb, glow_col=ct, glow_rad=9, stroke_col=(32, 12, 22), stroke_w=6)
                    elif sub_style == "frosted_glass":
                        if is_g:   ct, cb = (255, 236, 102), (245, 178, 28)
                        elif is_e: ct, cb = (148, 255, 216), (48, 212, 158)
                        elif is_r: ct, cb = (255, 178, 194), (238, 72, 98)
                        else:      ct, cb = (255, 255, 255), (235, 245, 255)
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, cb, glow_rad=6, glow_col=ct, stroke_col=(8, 14, 24), stroke_w=5)
                    else:  # "glow_gold"
                        if is_g:   ct, cb = (255, 238, 96),  (245, 172, 22)
                        elif is_e: ct, cb = (142, 255, 212), (42, 208, 152)
                        elif is_r: ct, cb = (255, 178, 192), (238, 68, 96)
                        else:      ct, cb = (255, 255, 255), (240, 246, 252)
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, cb, glow_col=(0, 0, 0), glow_rad=8, stroke_col=(10, 14, 20), stroke_w=7)

                    adv = int(ImageDraw.Draw(canvas_im).textlength(wtxt, font=get_font(FONT_EBOLD, pt_u))) + 6
                    w_renders.append((wtxt, ws, sp, adv, is_g))
                    tot_w += adv + (gap if wi > 0 else 0)
                fit_k = min(1.0, (max_w - 36) / max(1.0, float(tot_w)))
                max_eff = max(max_eff, tot_w * fit_k)
                rendered_lines.append((w_renders, fit_k, tot_w * fit_k))

            if sub_style in ("kobe_white_pill", "warm_editorial", "frosted_glass") and rendered_lines:
                bw = min(672, int(max_eff + 44))
                bh = int(len(rendered_lines) * lh + 20)
                by_c = y_base + (len(rendered_lines) - 1) * lh * 0.5
                bx = Image.new("RGBA", (bw + 16, bh + 16), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bx)
                if sub_style == "kobe_white_pill":
                    bd.rounded_rectangle([8, 12, 8 + bw, 12 + bh], radius=26, fill=(8, 14, 28, 88))
                    bd.rounded_rectangle([8, 8,  8 + bw, 8 + bh],  radius=26, fill=(255, 255, 255, 246), outline=(54, 86, 251, 225), width=3)
                elif sub_style == "warm_editorial":
                    bd.rounded_rectangle([8, 12, 8 + bw, 12 + bh], radius=16, fill=(28, 20, 12, 82))
                    bd.rounded_rectangle([8, 8,  8 + bw, 8 + bh],  radius=16, fill=(253, 248, 238, 248), outline=(180, 108, 22, 225), width=2)
                else:
                    bd.rounded_rectangle([8, 8, 8 + bw, 8 + bh], radius=26, fill=(10, 22, 44, 208), outline=(120, 218, 255, 198), width=3)
                paste_centered(canvas_im, bx, cx, by_c, opacity=op_g)

            for li, (w_renders, fit_k, eff_tot) in enumerate(rendered_lines):
                cur_x = cx - eff_tot * 0.5
                cur_y = y_base + li * lh
                for wtxt, ws, sp, adv, is_g in w_renders:
                    eff_adv = adv * fit_k
                    wcx = cur_x + eff_adv * 0.5
                    if t >= ws - 0.03:
                        dt_w = max(0.0, t - ws)
                        u_w  = ease_out_cubic(min(1.0, dt_w / 0.15))
                        paste_centered(canvas_im, sp, wcx, cur_y + (1.0 - u_w) * 5.0, scale_x=fit_k * (0.96 + 0.06 * u_w), opacity=op_g)
                        if sub_style == "rose_bling" and is_g and 0.02 <= dt_w <= 0.42:
                            draw_4pt_star(canvas_im, wcx + eff_adv * 0.36, cur_y - 22, 16 * (1.0 - dt_w / 0.45), rot_deg=dt_w * 90)
                    else:
                        paste_centered(canvas_im, sp, wcx, cur_y + 3.0, scale_x=fit_k * 0.96, opacity=op_g * 0.38)
                    cur_x += eff_adv + gap * fit_k
            break
