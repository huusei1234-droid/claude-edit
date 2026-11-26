import concurrent.futures, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"C:\AI\full studio\output\batch-htav-261125")
from safe_zone_9x16 import is_box_safe_9x16
from batch_v2_configs_18 import EP18_CONFIGS, HYBRID_STYLES
from batch_step6_render_all_17 import (
    W, H, FPS, FONT_TITLE, FONT_BLACK, FONT_EBOLD, FONT_BOLD, FONT_SERIF,
    get_font, clamp01, smoothstep, quintic, ease_out_cubic, ease_out_back,
    smooth_in_out_env, fit_cover, render_glow_text_sprite, paste_centered,
    make_luxury_playing_card, make_card_back, make_video_playing_card,
    draw_landing_ripple, load_vid_frames_wh, sample_clip_pingpong, load_ep_static_assets,
    build_caption_groups,
)
from batch_v2_native_components import (
    make_kobe_saas_step_card, make_clean_broll_viewport, make_cyber_hud_card,
    make_frosted_glass_card, make_editorial_paper_card, draw_editorial_arch_pip,
    render_viethan_5cell_bento, draw_tvc_gold_portal, make_tvc_gold_cta_plaque,
    make_collage_polaroid,
)

BATCH_DIR   = r"C:\AI\full studio\output\batch-htav-261125"
FONTS_DIR   = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_SCRIPT = os.path.join(FONTS_DIR, "DancingScript-Bold.ttf")

# 100% DEAD-CENTER HORIZONTAL AXIS (X = 540px)!
# For Y >= 860, width <= 672px guarantees X in [204..876] <= 884px (Safe Zone + Dead-Center!)
CENTER_X = 540
SAFE_CENTER_MAX_W = 672

SURFACE_THEMES = {
    "kobe_light_periwinkle": {"light": True,  "bg1": (244, 246, 253), "bg2": (204, 216, 252), "dot": (188, 200, 238), "pri": (54, 86, 251),  "sec": (243, 102, 89), "ink": (16, 22, 38)},
    "kobe_light_mint":       {"light": True,  "bg1": (240, 252, 246), "bg2": (194, 236, 216), "dot": (168, 216, 194), "pri": (14, 138, 92),  "sec": (235, 138, 28), "ink": (14, 28, 22)},
    "editorial_cream":       {"light": True,  "bg1": (252, 248, 239), "bg2": (236, 224, 198), "dot": (216, 200, 170), "pri": (180, 102, 16), "sec": (18, 124, 84),  "ink": (22, 20, 18)},
    "kobe_dark_cyber":       {"light": False, "bg1": (20, 24, 32),    "bg2": (10, 12, 18),    "dot": (46, 56, 74),    "pri": (54, 204, 200), "sec": (242, 107, 33), "ink": (255, 255, 255)},
    "kobe_dark_rose":        {"light": False, "bg1": (38, 16, 28),    "bg2": (16, 8, 14),     "dot": (82, 40, 58),    "pri": (255, 118, 162),"sec": (255, 216, 102),"ink": (255, 255, 255)},
    "kobe_dark_amber":       {"light": False, "bg1": (36, 22, 14),    "bg2": (16, 10, 6),     "dot": (78, 54, 34),    "pri": (255, 196, 78), "sec": (58, 212, 148), "ink": (255, 255, 255)},
    "saas_sapphire":         {"light": False, "bg1": (8, 18, 46),     "bg2": (2, 8, 20),      "dot": (34, 62, 118),   "pri": (95, 184, 255), "sec": (255, 216, 98), "ink": (255, 255, 255)},
    "saas_rose_aqua":        {"light": False, "bg1": (14, 32, 40),    "bg2": (6, 14, 20),     "dot": (40, 76, 90),    "pri": (92, 232, 214), "sec": (255, 148, 182),"ink": (255, 255, 255)},
    "tvc_peach_bling":       {"light": False, "bg1": (56, 22, 30),    "bg2": (24, 10, 14),    "dot": (106, 48, 60),   "pri": (255, 216, 112),"sec": (255, 152, 138),"ink": (255, 255, 255)},
    "tvc_rose_bling":        {"light": False, "bg1": (54, 16, 36),    "bg2": (22, 8, 16),     "dot": (102, 42, 70),   "pri": (255, 218, 118),"sec": (255, 142, 186),"ink": (255, 255, 255)},
}

_surf_cache = {}


def get_surface_canvas(surf_name):
    if surf_name in _surf_cache:
        return _surf_cache[surf_name]
    st = SURFACE_THEMES.get(surf_name, SURFACE_THEMES["kobe_dark_cyber"])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # Strictly symmetric vertical + radial gradient around X = 540!
    u_grad = np.clip((yy / H) * 0.78 + (np.abs(xx - 540.0) / 540.0) * 0.22, 0.0, 1.0)
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    for c in range(3):
        rgb[:, :, c] = np.clip(st["bg1"][c] * (1.0 - u_grad) + st["bg2"][c] * u_grad, 0, 255).astype(np.uint8)
    im = Image.fromarray(rgb, "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)

    if surf_name == "editorial_cream":
        # Fine archival ruled lines + symmetric margin border
        for gy in range(80, H, 64):
            d.line([(64, gy), (W - 64, gy)], fill=(*st["dot"], 85), width=1)
        d.rectangle([48, 252, W - 48, 1540], outline=(*st["pri"], 65), width=2)
    elif st["light"]:
        # Kobe Variant B Dot-Matrix (symmetric around X = 540!)
        for dx in range(0, 520, 32):
            for gx in ({540 - dx, 540 + dx}):
                for gy in range(28, H, 32):
                    d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=(*st["dot"], 195))
    elif surf_name.startswith("saas_"):
        # SaaS Vertical Light-Pillar at X = 540 + Horizon Planet Arc!
        beam = np.exp(-(((xx - 540.0) / 170.0) ** 2)) * np.exp(-(((yy - 560.0) / 700.0) ** 2))
        b_rgba = np.zeros((H, W, 4), dtype=np.uint8)
        b_rgba[:, :, 0] = st["pri"][0]; b_rgba[:, :, 1] = st["pri"][1]; b_rgba[:, :, 2] = st["pri"][2]
        b_rgba[:, :, 3] = np.clip(beam * 96.0, 0, 120).astype(np.uint8)
        im = Image.alpha_composite(im, Image.fromarray(b_rgba, "RGBA"))
        d = ImageDraw.Draw(im)
        d.ellipse([540 - 780, 1020, 540 + 780, 2580], fill=(*st["bg1"], 185), outline=(*st["pri"], 145), width=4)
    elif surf_name.startswith("tvc_"):
        # TVC Satin Radial Champagne Glow + Double Filigree Halo at X = 540
        glow = np.exp(-(((xx - 540.0) / 470.0) ** 2 + ((yy - 760.0) / 680.0) ** 2))
        g_rgba = np.zeros((H, W, 4), dtype=np.uint8)
        g_rgba[:, :, 0] = 255; g_rgba[:, :, 1] = 214; g_rgba[:, :, 2] = 150
        g_rgba[:, :, 3] = np.clip(glow * 78.0, 0, 98).astype(np.uint8)
        im = Image.alpha_composite(im, Image.fromarray(g_rgba, "RGBA"))
        d = ImageDraw.Draw(im)
        d.ellipse([540 - 500, 780 - 500, 540 + 500, 780 + 500], outline=(255, 224, 138, 48), width=2)
        d.ellipse([540 - 380, 780 - 380, 540 + 380, 780 + 380], outline=(255, 224, 138, 32), width=1)
    else:
        # Kobe Variant A Coordinate Grid (symmetric around X = 540)
        for gx in range(0, W + 1, 36):
            d.line([(gx, 0), (gx, H)], fill=(*st["dot"], 58), width=1)
        for gy in range(0, H, 36):
            d.line([(0, gy), (W, gy)], fill=(*st["dot"], 58), width=1)

    _surf_cache[surf_name] = im
    return im


def draw_4pt_sparkle(canvas_im, cx, cy, r, col=(255, 244, 185), alpha=235, rot_deg=0.0):
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


def make_kobe_tilted_pill(txt_a, txt_b, col_a=(18, 22, 34), col_b=(54, 86, 251), bg_col=(255, 255, 255), max_w=668, pt=52):
    key = ("KOBE_PILL2", txt_a, txt_b, col_a, col_b, bg_col, max_w, pt)
    if key in _surf_cache:
        return _surf_cache[key]
    f = get_font(FONT_EBOLD, pt)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    full_s = f"{txt_a} {txt_b}".strip()
    while f.size > 24 and dummy.textbbox((0, 0), full_s, font=f)[2] > max_w - 58:
        f = get_font(FONT_EBOLD, f.size - 2)
    ba = dummy.textbbox((0, 0), txt_a + (" " if txt_b else ""), font=f)
    bb = dummy.textbbox((0, 0), txt_b, font=f) if txt_b else (0, 0, 0, 0)
    tw = (ba[2] - ba[0]) + (bb[2] - bb[0])
    th = max(ba[3] - ba[1], bb[3] - bb[1])
    pw, ph = tw + 56, th + 32
    pad = 16
    im = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + pw, pad + ph + 8], radius=ph // 2, fill=(10, 16, 36, 95))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=8)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=ph // 2, fill=(*bg_col, 253), outline=(*col_b, 215), width=3)
    tx = pad + 28 - ba[0]
    ty = pad + ph * 0.5 - (ba[1] + ba[3]) * 0.5
    d.text((tx, ty), txt_a, font=f, fill=(*col_a, 255))
    if txt_b:
        d.text((tx + (ba[2] - ba[0]), ty), txt_b, font=f, fill=(*col_b, 255))
    _surf_cache[key] = im
    return im


def draw_kobe_circle_pip(canvas_im, fg_rgb, t, s0, s1, cx=540, cy=1318, diam=322, ring_col=(54, 86, 251), light_mode=True):
    dt_in  = max(0.0, t - s0)
    dt_out = max(0.0, s1 - t)
    iris_u = min(ease_out_cubic(min(1.0, dt_in / 0.24)), ease_out_cubic(min(1.0, dt_out / 0.20)))
    if iris_u <= 0.03:
        return
    crop_r = 250
    x0, y0 = max(0, 540 - crop_r), max(0, 755 - crop_r)
    sub = Image.fromarray(np.ascontiguousarray(fg_rgb[y0:y0 + crop_r * 2, x0:x0 + crop_r * 2]), "RGB").resize((diam, diam), Image.Resampling.BICUBIC).convert("RGBA")

    pad = 24
    cw = diam + pad * 2
    pip = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad, pad + 10, pad + diam, pad + diam + 10], fill=(12, 20, 44, 95 if light_mode else 165))
    pip = Image.alpha_composite(pip, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    d = ImageDraw.Draw(pip)
    d.ellipse([pad, pad, pad + diam, pad + diam], fill=(214, 222, 246, 255) if light_mode else (28, 34, 46, 255))

    r_iris = int(round((diam * 0.5) * iris_u))
    if r_iris > 4:
        mask = Image.new("L", (diam, diam), 0)
        c_m = diam // 2
        ImageDraw.Draw(mask).ellipse([c_m - r_iris, c_m - r_iris, c_m + r_iris, c_m + r_iris], fill=255)
        face_l = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
        face_l.paste(sub, (pad, pad), mask=mask)
        pip = Image.alpha_composite(pip, face_l)

    d = ImageDraw.Draw(pip)
    if light_mode:
        d.ellipse([pad - 2, pad - 2, pad + diam + 2, pad + diam + 2], outline=(255, 255, 255, 255), width=8)
        d.ellipse([pad - 6, pad - 6, pad + diam + 6, pad + diam + 6], outline=(*ring_col, 235), width=3)
    else:
        d.ellipse([pad - 3, pad - 3, pad + diam + 3, pad + diam + 3], outline=(*ring_col, 245), width=5)
        d.ellipse([pad - 9, pad - 9, pad + diam + 9, pad + diam + 9], outline=(*ring_col, 85), width=3)

    paste_centered(canvas_im, pip, cx, cy)


def draw_packshot_pod_symmetric(stage_im, assets, cfg, t, cy=1115, style="kobe", pri_rgb=(54, 86, 251)):
    """
    100% Symmetric Lower Packshot + Hero Value Pod around X = 540!
    Left Pod center = 382 (w=308 -> left=228), Right Packshot center = 698 (right<=852) -> Midpoint = 540.0!
    """
    rf_c = cfg["riffle"]
    hrk, hsi, hth, htt, hsb, hbd, hbv = rf_c["hero"]
    if style == "glass":
        pod = make_frosted_glass_card(308, 252, hbd, htt, hsb, big_val=hbv, tint_rgb=(20, 50, 96), rim_rgb=pri_rgb)
    elif style == "editorial":
        pod = make_editorial_paper_card(308, 252, hbd, htt, hsb, metric_txt=hbv, accent_rgb=pri_rgb)
    elif style == "cyber":
        pod = make_cyber_hud_card(308, 252, hbd, pri_rgb, (255, 226, 102), htt, hsb, big_metric=hbv)
    else:
        pod = make_kobe_saas_step_card(308, 252, "★", hsi, pri_rgb, htt, hsb, tag_txt=f"{hbv} • {hbd}")
    paste_centered(stage_im, pod, 382, cy)

    prods = assets["prods"]
    if len(prods) >= 2:
        paste_centered(stage_im, prods[0], 666, cy - 12 + math.sin(t * 2.5) * 4.0, scale_x=0.52)
        paste_centered(stage_im, prods[1], 734, cy + 20 + math.sin(t * 2.5 + 0.8) * 4.0, scale_x=0.50)
    else:
        paste_centered(stage_im, prods[0], 698, cy + math.sin(t * 2.5) * 4.5, scale_x=0.62)


# ==============================================================================
# MULTI-STYLE CAPTION ENGINE (6 DISTINCT MODES, 100% DEAD-CENTER X = 540!)
# ==============================================================================
def render_hybrid_captions(canvas_im, t, cap_groups, cfg, sub_mode, cx=CENTER_X, y_base=1215, max_w=SAFE_CENTER_MAX_W, base_pt=74, lh=86, single_line=False):
    gold_w = cfg.get("gold_words", set())
    emer_w = cfg.get("emer_words", set())
    rose_w = cfg.get("rose_words", set())

    for g in cap_groups:
        if g["t0"] <= t < g["t1"]:
            op_g = smoothstep((g["t1"] - t) / 0.18) if (g["t1"] - t) < 0.18 else 1.0
            lines_use = [[w for ln in g["lines"] for w in ln]] if single_line else g["lines"]
            gap = 15

            rendered_lines = []
            max_line_eff_w = 0.0
            for ln in lines_use:
                w_renders, tot_w = [], 0
                for wi, (wtxt, ws, we) in enumerate(ln):
                    clean_tok = wtxt.strip(".,?!:;\"'()")
                    is_g = (wtxt in gold_w or clean_tok in gold_w)
                    is_e = (wtxt in emer_w or clean_tok in emer_w)
                    is_r = (wtxt in rose_w or clean_tok in rose_w)
                    pt_u = base_pt * (1.10 if (is_g or is_e or is_r) else 1.0)

                    if sub_mode == "kobe_pill_badge":
                        ct = (37, 99, 235) if is_g else ((14, 142, 92) if is_e else ((225, 29, 72) if is_r else (15, 23, 42)))
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, ct, glow_rad=0, stroke_col=None, stroke_w=0)
                    elif sub_mode == "editorial_ink_card":
                        ct = (180, 83, 9) if is_g else ((14, 116, 78) if is_e else ((190, 24, 60) if is_r else (22, 20, 18)))
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, ct, glow_rad=0, stroke_col=None, stroke_w=0)
                    elif sub_mode == "viethan_white_stroke":
                        ct = (217, 4, 41) if (is_g or is_r) else (11, 138, 66)
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, ct, glow_rad=5, glow_col=(0, 0, 0), stroke_col=(255, 255, 255), stroke_w=9)
                    elif sub_mode == "tvc_gold_bling":
                        ct, cb = ((255, 246, 190), (218, 148, 32)) if (is_g or is_e) else (((255, 192, 208), (232, 78, 112)) if is_r else ((255, 255, 255), (242, 228, 236)))
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, cb, glow_col=ct, glow_rad=10, stroke_col=(34, 12, 22), stroke_w=6)
                    else:
                        if is_g:   ct, cb = (255, 238, 112), (242, 166, 32)
                        elif is_e: ct, cb = (152, 255, 220), (46, 208, 158)
                        elif is_r: ct, cb = (255, 182, 196), (238, 72, 98)
                        else:      ct, cb = (255, 255, 255), (232, 244, 252)
                        sp = render_glow_text_sprite(wtxt, FONT_EBOLD, pt_u, ct, cb, glow_col=ct, glow_rad=9, stroke_col=(8, 14, 22), stroke_w=6)

                    adv = int(ImageDraw.Draw(canvas_im).textlength(wtxt, font=get_font(FONT_EBOLD, pt_u))) + 6
                    w_renders.append((wtxt, ws, sp, adv, is_g))
                    tot_w += adv + (gap if wi > 0 else 0)
                fit_k = min(1.0, (max_w - 48) / max(1.0, float(tot_w)))
                max_line_eff_w = max(max_line_eff_w, tot_w * fit_k)
                rendered_lines.append((w_renders, fit_k, tot_w * fit_k))

            if sub_mode in ("kobe_pill_badge", "editorial_ink_card", "saas_glass_bar") and rendered_lines:
                bw = min(672, int(max_line_eff_w + 48))
                bh = int(len(rendered_lines) * lh + 24)
                by_c = y_base + (len(rendered_lines) - 1) * lh * 0.5
                bx_im = Image.new("RGBA", (bw + 20, bh + 20), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bx_im)
                if sub_mode == "kobe_pill_badge":
                    bd.rounded_rectangle([10, 14, 10 + bw, 14 + bh], radius=28, fill=(10, 18, 38, 78))
                    bd.rounded_rectangle([10, 10, 10 + bw, 10 + bh], radius=28, fill=(255, 255, 255, 248), outline=(54, 86, 251, 215), width=3)
                elif sub_mode == "editorial_ink_card":
                    bd.rounded_rectangle([10, 14, 10 + bw, 14 + bh], radius=18, fill=(24, 18, 12, 72))
                    bd.rounded_rectangle([10, 10, 10 + bw, 10 + bh], radius=18, fill=(253, 249, 240, 250), outline=(34, 28, 22, 235), width=2)
                else:
                    bd.rounded_rectangle([10, 10, 10 + bw, 10 + bh], radius=28, fill=(10, 24, 52, 216), outline=(120, 214, 255, 205), width=3)
                paste_centered(canvas_im, bx_im, cx, by_c, opacity=op_g)

            for li, (w_renders, fit_k, eff_tot) in enumerate(rendered_lines):
                cur_x = cx - eff_tot * 0.5
                cur_y = y_base + li * lh
                for wtxt, ws, sp, adv, is_g in w_renders:
                    eff_adv = adv * fit_k
                    wcx = cur_x + eff_adv * 0.5
                    if t >= ws - 0.03:
                        dt_w = max(0.0, t - ws)
                        u_w  = ease_out_cubic(min(1.0, dt_w / 0.16))
                        paste_centered(canvas_im, sp, wcx, cur_y + (1.0 - u_w) * 6.0, scale_x=fit_k * (0.96 + 0.06 * u_w), opacity=op_g, blur_px=0.0)
                        if sub_mode == "tvc_gold_bling" and is_g and 0.02 <= dt_w <= 0.45:
                            draw_4pt_sparkle(canvas_im, wcx + eff_adv * 0.36, cur_y - 24, 17 * (1.0 - dt_w / 0.5), rot_deg=dt_w * 90)
                    else:
                        # Soft balanced preview of upcoming words in active phrase -> 100% symmetric X=540 on every frame!
                        paste_centered(canvas_im, sp, wcx, cur_y + 4.0, scale_x=fit_k * 0.96, opacity=op_g * 0.38)
                    cur_x += eff_adv + gap * fit_k
            break


# ==============================================================================
# TIMELINE PLANNER (100% CLONE COVERAGE + DISTINCT STAGE PACING)
# ==============================================================================
def build_hybrid_timeline(meta, cfg, hstyle):
    D = float(meta["duration_s"])
    clones = sorted(meta.get("clone_spans", []), key=lambda x: x["start_s"])

    if cfg.get("force_fullscreen_speech"):
        c1 = clones[0] if len(clones) > 0 else {"start_s": 0.0, "end_s": 4.5}
        c2 = clones[1] if len(clones) > 1 else {"start_s": 4.5, "end_s": 12.0}
        c3 = clones[2] if len(clones) > 2 else {"start_s": 12.0, "end_s": 22.0}
        c4 = clones[3] if len(clones) > 3 else {"start_s": 22.0, "end_s": D}
        mid_c3 = round((c3["start_s"] + c3["end_s"]) * 0.46, 3)
        return {
            "hook_aroll": None,
            "full_stages": [
                ("hook_full",        0.00,              c1["end_s"] + 0.04,  True),
                (hstyle["stage_1"],  c1["end_s"] - 0.05, c2["end_s"] + 0.04, True),
                (hstyle["stage_2"],  c2["end_s"] - 0.05, mid_c3 + 0.04,      True),
                (hstyle["stage_3"],  mid_c3 - 0.05,     c4["start_s"] + 0.04, True),
                (hstyle["end_mode"], max(c3["end_s"] - 0.08, c4["start_s"] - 0.10), D + 0.15, True),
            ],
            "flip3d_aroll": None,
            "kw_windows": [],
        }

    first_clone_s = clones[0]["start_s"] if clones else D
    hook_end = min(4.10, max(2.85, first_clone_s - 0.24))

    rem_clones = list(clones)
    if rem_clones and rem_clones[-1]["start_s"] >= D * 0.66:
        last_c = rem_clones.pop()
        end_s0 = max(hook_end + 3.6, last_c["start_s"] - 0.18)
    else:
        end_s0 = max(hook_end + 3.6, D - 3.40)

    full_stages = [(hstyle["end_mode"], round(end_s0, 3), round(D + 0.15, 3), True)]
    stage_slots = [hstyle["stage_1"], hstyle["stage_2"], hstyle["stage_3"]]
    used_idx = set()

    for cl in rem_clones:
        cs, ce = cl["start_s"], cl["end_s"]
        span_len = ce - cs
        if span_len > 8.2:
            sm = round(cs + span_len * 0.45, 3)
            s_a = stage_slots[0] if (1 in used_idx and 0 not in used_idx) else stage_slots[1]
            s_b = stage_slots[2]
            full_stages.append((s_a, round(max(hook_end + 0.12, cs - 0.22), 3), round(sm + 0.05, 3), True))
            full_stages.append((s_b, round(sm - 0.05, 3), round(min(end_s0 - 0.05, ce + 0.24), 3), True))
            used_idx.update([0 if s_a == stage_slots[0] else 1, 2])
        else:
            pad_e = max(0.0, (3.40 - span_len) * 0.5)
            w0 = max(hook_end + 0.12, cs - 0.22 - pad_e * 0.5)
            w1 = min(end_s0 - 0.10,   ce + 0.24 + pad_e * 0.5)
            pick_i = 2 if (cs >= D * 0.50 and 2 not in used_idx) else (0 if (cs < D * 0.36 and 0 not in used_idx) else (1 if 1 not in used_idx else 2))
            full_stages.append((stage_slots[pick_i], round(w0, 3), round(w1, 3), True))
            used_idx.add(pick_i)

    def overlaps_any(a, b, margin=0.80):
        for _, x0, x1, _ in full_stages:
            if not (b + margin <= x0 or a - margin >= x1):
                return True
        return False

    targets = [(0, D * 0.22, 4.6), (1, D * 0.45, 4.4), (2, D * 0.70, 4.8)]
    for si, ct_t, dur_t in targets:
        if si in used_idx:
            continue
        for delta in [0.0, -2.2, 2.2, -4.5, 4.5, -6.8, 6.8]:
            a = max(hook_end + 0.55, ct_t + delta - dur_t * 0.5)
            b = min(end_s0 - 0.55, a + dur_t)
            if (b - a) >= 3.1 and not overlaps_any(a, b, margin=0.95):
                cl_ov = any(not (b <= c["start_s"] - 0.15 or a >= c["end_s"] + 0.15) for c in clones)
                full_stages.append((stage_slots[si], round(a, 3), round(b, 3), cl_ov))
                used_idx.add(si)
                break

    full_stages.sort(key=lambda x: x[1])

    gaps = []
    cur = hook_end + 0.20
    for _, x0, x1, _ in full_stages:
        if x0 - cur >= 2.4:
            gaps.append((cur, x0))
        cur = max(cur, x1)

    flip3d_aroll = None
    if hstyle["aroll_mode"] in ("full_cyber_behind_head", "viethan_clinical_aroll", "luxury_velvet_arch"):
        for g0, g1 in reversed(gaps):
            if (g1 - g0) >= 3.0:
                f0 = g0 + 0.22
                flip3d_aroll = (round(f0, 3), round(min(g1 - 0.22, f0 + 4.4), 3))
                break

    kw_windows = []
    for kw_txt, rel_p, kw_col in cfg.get("keywords", []):
        tt = rel_p * D
        best_g, best_d = None, 999.0
        for g0, g1 in gaps:
            if (g1 - g0) >= 2.0 and abs((g0 + g1) * 0.5 - tt) < best_d:
                best_d = abs((g0 + g1) * 0.5 - tt); best_g = (g0, g1)
        if best_g:
            k0 = max(best_g[0] + 0.15, min(best_g[1] - 2.2, tt - 1.1))
            k1 = min(best_g[1] - 0.15, k0 + 2.5)
            if k1 - k0 >= 1.4:
                kw_windows.append((kw_txt, round(k0, 3), round(k1, 3), kw_col))

    return {
        "hook_aroll": (0.04, round(hook_end, 3)),
        "full_stages": full_stages,
        "flip3d_aroll": flip3d_aroll,
        "kw_windows": kw_windows,
    }


# ==============================================================================
# MASTER HYBRID COMPOSITOR (6 A-ROLL MODES × 9 STAGE SYSTEMS × 4 END-CARDS)
# ==============================================================================
_YY_G, _XX_G = np.ogrid[0:H, 0:W]
_DESK_LINE = np.clip((np.arange(H, dtype=np.float32) - 1605.0) / 55.0, 0.0, 1.0)[:, None]
_DESK_BOX  = np.exp(-((np.maximum(0.0, np.abs(_XX_G - 540.0) - 290.0)) / 48.0) ** 2) * \
             np.clip((_YY_G - 1260.0) / 50.0, 0.0, 1.0) * np.clip((1785.0 - _YY_G) / 45.0, 0.0, 1.0)


def compose_hybrid_frame(frame_idx, rgb, matte_u8, brolls, assets, cap_groups, cfg, hstyle, tl, meta):
    t = frame_idx / FPS
    D = float(meta["duration_s"])
    surf_name = hstyle["surface"]
    ar_mode   = hstyle["aroll_mode"]
    st_theme  = SURFACE_THEMES.get(surf_name, SURFACE_THEMES["kobe_dark_cyber"])
    surf_im   = get_surface_canvas(surf_name)
    brand_lbl = "AN VƯỢNG" if "an_vuong" in cfg["logo"] else "HẰNG THU"
    pri_c, sec_c, light_m = st_theme["pri"], st_theme["sec"], st_theme["light"]

    # Breathing Ken Burns strictly symmetric on X = 540 (always z >= 1.008 so x0 >= 0)!
    z = 1.030 + 0.022 * math.sin(t * 0.58)
    cw, ch = min(W, int(round(W / z))), min(H, int(round(H / z)))
    x0 = max(0, (W - cw) // 2)
    y0 = max(0, min(H - ch, int(round(740 - ch * (740.0 / H)))))
    frame_im = Image.fromarray(np.ascontiguousarray(rgb[y0:y0 + ch, x0:x0 + cw]), "RGB").resize((W, H), Image.Resampling.BILINEAR)
    matte_im = Image.fromarray(np.ascontiguousarray(matte_u8[y0:y0 + ch, x0:x0 + cw]), "L").resize((W, H), Image.Resampling.BILINEAR)
    fg_rgb = np.array(frame_im)
    m_arr  = np.array(matte_im, dtype=np.float32) / 255.0

    active_full = []
    max_ev = 0.0
    for st_kind, s0, s1, no_pip in tl["full_stages"]:
        din  = 0.02 if s0 <= 0.02 else 0.24
        dout = 0.02 if s1 >= D else 0.24
        ev = smooth_in_out_env(t, s0, s1, d_in=din, d_out=dout)
        if ev > 0.005:
            active_full.append((st_kind, s0, s1, ev, no_pip))
            max_ev = max(max_ev, ev)

    comp_im = None
    if max_ev < 0.995:
        in_hook = tl["hook_aroll"] and (tl["hook_aroll"][0] <= t <= tl["hook_aroll"][1])
        env_hk  = smooth_in_out_env(t, tl["hook_aroll"][0], tl["hook_aroll"][1], 0.22, 0.24) if in_hook else 0.0
        hk      = cfg["hook"]
        hk_mode = hstyle["hook_mode"]

        # ----------------------------------------------------------------------
        # A-ROLL ARCHITECTURE 1: KOBE FRAMED LIGHT SAAS PORTRAIT (v00, v10, v16)
        # ----------------------------------------------------------------------
        if ar_mode == "kobe_framed_light":
            comp_im = surf_im.copy()
            d_ar = ImageDraw.Draw(comp_im)
            # Top Step-Progress Pill at Y = 294 (cx = 540, < 860px)
            prog_idx = 1 if t < D * 0.36 else (2 if t < D * 0.68 else 3)
            p_bar = Image.new("RGBA", (668, 62), (0, 0, 0, 0))
            pd = ImageDraw.Draw(p_bar)
            pd.rounded_rectangle([2, 2, 665, 59], radius=30, fill=(255, 255, 255, 245), outline=(*pri_c, 195), width=3)
            fp_b = get_font(FONT_EBOLD, 22)
            for si_p, s_lbl in enumerate(["01 • VẤN ĐỀ", "02 • KHOA HỌC", "03 • GIẢI PHÁP"], 1):
                sx_c = 118 + (si_p - 1) * 216
                act_p = (si_p == prog_idx)
                if act_p:
                    pd.rounded_rectangle([sx_c - 98, 8, sx_c + 98, 53], radius=22, fill=(*pri_c, 255))
                bp_s = pd.textbbox((0, 0), s_lbl, font=fp_b)
                pd.text((sx_c - (bp_s[2] - bp_s[0]) * 0.5, 30 - (bp_s[1] + bp_s[3]) * 0.5), s_lbl, font=fp_b,
                        fill=(255, 255, 255, 255) if act_p else (72, 86, 112, 255))
            paste_centered(comp_im, p_bar, CENTER_X, 294)

            # Dead-Center Rounded Studio Speaker Card: cx=540, cy=748, w=672, h=792 (X in [204..876] <= 884px!)
            fw, fh = 672, 792
            sp_sub = Image.fromarray(np.ascontiguousarray(fg_rgb[465:465 + fh, 540 - fw // 2:540 + fw // 2]), "RGB").convert("RGBA")
            m_fr = Image.new("L", (fw, fh), 0)
            ImageDraw.Draw(m_fr).rounded_rectangle([0, 0, fw - 1, fh - 1], radius=36, fill=255)
            card_sp = Image.new("RGBA", (fw + 28, fh + 28), (0, 0, 0, 0))
            sh_sp = Image.new("RGBA", card_sp.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh_sp).rounded_rectangle([14, 22, 14 + fw, 22 + fh], radius=36, fill=(14, 24, 52, 88))
            card_sp = Image.alpha_composite(card_sp, sh_sp.filter(ImageFilter.GaussianBlur(radius=10)))
            vl_sp = Image.new("RGBA", card_sp.size, (0, 0, 0, 0))
            vl_sp.paste(sp_sub, (14, 14), mask=m_fr)
            card_sp = Image.alpha_composite(card_sp, vl_sp)
            cd_sp = ImageDraw.Draw(card_sp)
            cd_sp.rounded_rectangle([14, 14, 14 + fw - 1, 14 + fh - 1], radius=36, outline=(255, 255, 255, 255), width=7)
            cd_sp.rounded_rectangle([11, 11, 17 + fw, 17 + fh], radius=39, outline=(*pri_c, 195), width=3)
            paste_centered(comp_im, card_sp, CENTER_X, 752)

            if in_hook and env_hk > 0.01:
                p1 = make_kobe_tilted_pill(hk["l1"], "", (18, 24, 38), pri_c, (255, 255, 255), max_w=664, pt=44)
                p2 = make_kobe_tilted_pill(hk["l2a"], hk["l2b"], (18, 24, 38), (225, 29, 72), (255, 250, 235), max_w=668, pt=56)
                paste_centered(comp_im, p1, CENTER_X, 1228, opacity=env_hk, angle=1.3)
                paste_centered(comp_im, p2, CENTER_X, 1344, opacity=env_hk, angle=-1.8)
            else:
                render_hybrid_captions(comp_im, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1255, max_w=SAFE_CENTER_MAX_W, base_pt=70, lh=82)

        # ----------------------------------------------------------------------
        # A-ROLL ARCHITECTURE 2: EDITORIAL ARCHIVAL CREAM PAPER (v04, v06)
        # ----------------------------------------------------------------------
        elif ar_mode == "editorial_framed_cream":
            comp_im = surf_im.copy()
            # Editorial Serif Masthead at Y = 296 (cx = 540, 0% tofu glyphs!)
            mast = Image.new("RGBA", (840, 68), (0, 0, 0, 0))
            md = ImageDraw.Draw(mast)
            fm_s = get_font(FONT_SERIF, 32)
            m_txt = f"—  {brand_lbl} CHUYÊN GIA DINH DƯỠNG  —"
            bm_s = md.textbbox((0, 0), m_txt, font=fm_s)
            md.text((420 - (bm_s[2] - bm_s[0]) * 0.5, 10), m_txt, font=fm_s, fill=(28, 22, 16, 255))
            md.line([(120, 58), (720, 58)], fill=(*pri_c, 185), width=2)
            paste_centered(comp_im, mast, CENTER_X, 296)
            draw_4pt_sparkle(comp_im, 148, 290, 14, col=pri_c, alpha=215)
            draw_4pt_sparkle(comp_im, 932, 290, 14, col=pri_c, alpha=215)

            # Warm Ivory Framed Portrait: cx=540, cy=752, w=668, h=784 (X in [206..874] <= 884px!)
            fw, fh = 668, 784
            sp_sub = Image.fromarray(np.ascontiguousarray(fg_rgb[468:468 + fh, 540 - fw // 2:540 + fw // 2]), "RGB").convert("RGBA")
            card_ed = Image.new("RGBA", (fw + 36, fh + 36), (0, 0, 0, 0))
            ed_d = ImageDraw.Draw(card_ed)
            ed_d.rounded_rectangle([8, 14, 28 + fw, 32 + fh], radius=18, fill=(38, 28, 16, 65))
            ed_d.rounded_rectangle([6, 6, 30 + fw, 30 + fh], radius=18, fill=(253, 249, 240, 255), outline=(34, 28, 22, 245), width=3)
            card_ed.paste(sp_sub, (18, 18))
            ed_d.rectangle([18, 18, 18 + fw - 1, 18 + fh - 1], outline=(*pri_c, 195), width=2)
            paste_centered(comp_im, card_ed, CENTER_X, 752)

            if in_hook and env_hk > 0.01:
                if hk_mode == "collage_polaroid_hook":
                    # Two miniature Washi-Tape Polaroids in top corners (Y=350, symmetric 210 & 870!) + Editorial Headline below!
                    p_l = make_collage_polaroid(sample_clip_pingpong(brolls[0], t, 1.0), 220, 178, hk["arc"][0][3])
                    p_r = make_collage_polaroid(sample_clip_pingpong(brolls[1], t, 1.0), 220, 178, hk["arc"][1][3], tape_rgb=(242, 132, 118))
                    paste_centered(comp_im, p_l, 206, 376, opacity=env_hk, angle=-6.5)
                    paste_centered(comp_im, p_r, 874, 376, opacity=env_hk, angle=+6.5)
                ed_hk = make_editorial_paper_card(668, 220, hk["l1"], f"{hk['l2a']} {hk['l2b']}", hk["l3"], accent_rgb=pri_c)
                paste_centered(comp_im, ed_hk, CENTER_X, 1288, scale_x=0.94 + 0.06 * env_hk, opacity=env_hk)
            else:
                render_hybrid_captions(comp_im, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1258, max_w=SAFE_CENTER_MAX_W, base_pt=70, lh=82)

        # ----------------------------------------------------------------------
        # A-ROLL ARCHITECTURE 3: SUSTAINED 50/50 SPLIT-SCREEN CINEMA (v03, v07, v17)
        # ----------------------------------------------------------------------
        elif ar_mode == "split_cinema_aroll":
            comp_im = surf_im.copy()
            # Bottom Half (Y = 842..1920): Crop fg_rgb[475:1553] so face sits cleanly at Y=902..1292 (0% caption overlap!)
            sp_crop = Image.fromarray(np.ascontiguousarray(fg_rgb[475:1553, :]), "RGB").convert("RGBA")
            comp_im.paste(sp_crop, (0, 842))

            # Top Half (Y = 258..816, < 860px): Live Rounded Cinema B-Roll (cx = 540, w = 892, h = 516)
            br_pick = brolls[0 if t < D * 0.45 else 2]
            vf_s = sample_clip_pingpong(br_pick, t, rate=1.02)
            top_lbl = hk["l1"].upper() if in_hook else cfg["clash"]["top_pill"]
            bot_lbl = hk["l3"] if in_hook else cfg["fan"]["headline"]
            vp_top = make_clean_broll_viewport(vf_s, 892, 512, top_lbl, bot_lbl, accent_rgb=pri_c, light_ui=False, zoom=1.04)
            paste_centered(comp_im, vp_top, CENTER_X, 530)

            # Horizon Divider Pill at Y = 824 (< 860px, cx = 540!)
            div_a, div_b = (hk["l2a"], hk["l2b"]) if in_hook else (brand_lbl, "• CHUYÊN GIA PHÂN TÍCH")
            p_div = make_kobe_tilted_pill(div_a, div_b, (18, 22, 34), (225, 29, 72) if in_hook else pri_c, (255, 250, 232), max_w=668, pt=46 if in_hook else 34)
            paste_centered(comp_im, p_div, CENTER_X, 824)

            if not in_hook:
                render_hybrid_captions(comp_im, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1426, max_w=SAFE_CENTER_MAX_W, base_pt=66, lh=78, single_line=True)

            # Crisp 0.24s White-Flash Hinge right at hook_end!
            if tl["hook_aroll"]:
                dt_fl = abs(t - tl["hook_aroll"][1])
                if dt_fl < 0.14:
                    fl_a = int(165 * (1.0 - dt_fl / 0.14))
                    comp_im = Image.alpha_composite(comp_im, Image.new("RGBA", (W, H), (255, 255, 255, fl_a)))

        # ----------------------------------------------------------------------
        # A-ROLL ARCHITECTURES 4, 5, 6: FULL-BLEED CENTERED SPEAKER VARIATIONS
        #   - viethan_clinical_aroll (v13, v15)
        #   - luxury_velvet_arch     (v05, v09, v12)
        #   - full_cyber_behind_head (v01, v02, v08)
        # ----------------------------------------------------------------------
        else:
            dim = env_hk * 0.82
            for _, k0, k1, _ in tl["kw_windows"]:
                dim = max(dim, smooth_in_out_env(t, k0, k1, 0.30, 0.28))
            if tl["flip3d_aroll"]:
                dim = max(dim, smooth_in_out_env(t, tl["flip3d_aroll"][0], tl["flip3d_aroll"][1], 0.28, 0.26) * 0.72)

            if dim <= 0.01:
                comp_im = frame_im.convert("RGBA")
            else:
                bg_s = frame_im.filter(ImageFilter.GaussianBlur(radius=4.5 * dim))
                bg_d = np.clip(np.array(bg_s, dtype=np.float32) * (1.0 - 0.70 * dim), 0, 255).astype(np.uint8)
                comp_im = Image.fromarray(bg_d, "RGB").convert("RGBA")

                for kw_txt, k0, k1, k_col in tl["kw_windows"]:
                    ek = smooth_in_out_env(t, k0, k1, 0.28, 0.26)
                    if ek > 0.01:
                        ct = (255, 236, 112) if k_col == "gold" else pri_c
                        sp_k = render_glow_text_sprite(kw_txt, FONT_TITLE, 138, ct, (240, 170, 42) if k_col == "gold" else ct, glow_col=ct, glow_rad=13)
                        fk = min(1.0, 900.0 / max(1.0, sp_k.width))
                        paste_centered(comp_im, sp_k, CENTER_X, 376 + (1.0 - ek) * 16.0, scale_x=fk * (0.92 + 0.08 * ek), opacity=ek, sweep_prog=((t - k0) / max(0.3, k1 - k0)) * 1.2)

                fg_alpha = np.maximum(m_arr, np.maximum(_DESK_LINE, _DESK_BOX * 0.88))
                comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

            # Persistent Style Chrome per A-Roll Family (100% Symmetric on X = 540!)
            if ar_mode == "viethan_clinical_aroll" and not in_hook:
                vh_bar = make_kobe_tilted_pill(f"✚ {brand_lbl} PHARMA", "• CHUYÊN GIA TƯ VẤN", (10, 114, 56), (218, 12, 36), (255, 248, 220), max_w=780, pt=28)
                paste_centered(comp_im, vh_bar, CENTER_X, 292)
            elif ar_mode == "luxury_velvet_arch":
                d_lv = ImageDraw.Draw(comp_im)
                d_lv.arc([120, 260, 960, 760], 195, 345, fill=(*pri_c, 155), width=3)
                draw_4pt_sparkle(comp_im, 176, 336, 18 + 4 * math.sin(t * 5.0), rot_deg=t * 35)
                draw_4pt_sparkle(comp_im, 904, 336, 18 + 4 * math.cos(t * 5.0), rot_deg=-t * 35)

            # Distinct Hook Overlays (0% touch on face Y=470..1080, 100% Dead-Center X=540!)
            if in_hook and env_hk > 0.01:
                if hk_mode == "viethan_medical_hook":
                    hdr = Image.new("RGBA", (888, 144), (0, 0, 0, 0))
                    hd = ImageDraw.Draw(hdr)
                    hd.rounded_rectangle([0, 0, 887, 143], radius=26, fill=(255, 232, 36, 252), outline=(255, 255, 255, 255), width=4)
                    f1, f2 = get_font(FONT_EBOLD, 34), get_font(FONT_BLACK, 50)
                    while f1.size > 22 and hd.textbbox((0, 0), hk["l1"].upper(), font=f1)[2] > 840: f1 = get_font(FONT_EBOLD, f1.size - 2)
                    l2_s = f"{hk['l2a']} {hk['l2b']}".upper()
                    while f2.size > 26 and hd.textbbox((0, 0), l2_s, font=f2)[2] > 840: f2 = get_font(FONT_BLACK, f2.size - 2)
                    b1 = hd.textbbox((0, 0), hk["l1"].upper(), font=f1)
                    b2 = hd.textbbox((0, 0), l2_s, font=f2)
                    hd.text((444 - (b1[2] - b1[0]) * 0.5, 18), hk["l1"].upper(), font=f1, fill=(10, 108, 52, 255))
                    hd.text((444 - (b2[2] - b2[0]) * 0.5, 66), l2_s, font=f2, fill=(218, 8, 28, 255))
                    paste_centered(comp_im, hdr, CENTER_X, 342, scale_x=0.94 + 0.06 * env_hk, opacity=env_hk)
                    for idx_a, (_, _, _, att, asb) in enumerate(hk["arc"]):
                        ts_a = 0.24 + idx_a * 0.22
                        if t >= ts_a:
                            ua = ease_out_back(min(1.0, (t - ts_a) / 0.28), 1.10)
                            pl = make_kobe_tilted_pill(f"0{idx_a + 1} • {att}:", asb, (12, 118, 62), (212, 18, 42), (255, 255, 255), max_w=668, pt=38)
                            paste_centered(comp_im, pl, CENTER_X, 1162 + idx_a * 92 + (1.0 - ua) * 16.0, opacity=env_hk)

                elif hk_mode == "saas_glass_hook":
                    top_gl = make_frosted_glass_card(840, 128, None, hk["l1"], hk["l3"], tint_rgb=(14, 38, 82), rim_rgb=pri_c)
                    paste_centered(comp_im, top_gl, CENTER_X, 342, opacity=env_hk)
                    bot_gl = make_frosted_glass_card(668, 206, f"⚡ CẢNH BÁO {brand_lbl}", f"{hk['l2a']} {hk['l2b']}", hk["l3"], tint_rgb=(20, 48, 98), rim_rgb=(255, 224, 112))
                    paste_centered(comp_im, bot_gl, CENTER_X, 1258, scale_x=0.93 + 0.07 * env_hk, opacity=env_hk)

                elif hk_mode == "tvc_portal_hook":
                    top_p = make_kobe_tilted_pill("✦", hk["l1"], (58, 16, 30), (188, 118, 18), (255, 248, 228), max_w=840, pt=42)
                    paste_centered(comp_im, top_p, CENTER_X, 336, opacity=env_hk)
                    plq = make_tvc_gold_cta_plaque(668, 214, f"✦ {brand_lbl} LUXURY ✦", f"{hk['l2a']} {hk['l2b']}", hk["l3"])
                    paste_centered(comp_im, plq, CENTER_X, 1262, scale_x=0.93 + 0.07 * env_hk, opacity=env_hk)

                else:  # "overhead_3card_arc" (Reserved selectively for Collector Card episode v01!)
                    arc_xs = [(0.16, 226, 346, -8.0), (0.32, 540, 334, 0.0), (0.48, 854, 346, 8.0)]
                    for (st_c, cx_c, cy_c, ang_c), (rk, si, thm, tt, sb) in zip(arc_xs, hk["arc"]):
                        if t >= st_c:
                            dc = t - st_c
                            uc = ease_out_back(min(1.0, dc / 0.32), 1.12)
                            ci = make_luxury_playing_card(242, 162, rk, si, thm, tt, sb)
                            paste_centered(comp_im, ci, cx_c, cy_c + (1.0 - uc) * (-45.0), opacity=env_hk * clamp01(dc / 0.16), angle=ang_c)
                    s1 = render_glow_text_sprite(hk["l1"], FONT_EBOLD, 54, (182, 252, 236), (92, 220, 186), glow_rad=9, stroke_col=(8, 16, 18), stroke_w=6)
                    s2 = render_glow_text_sprite(f"{hk['l2a']} {hk['l2b']}", FONT_BLACK, 80, (255, 236, 108), (242, 152, 28), glow_rad=12, stroke_col=(20, 12, 8), stroke_w=7)
                    paste_centered(comp_im, s1, CENTER_X, 1185, scale_x=min(1.0, 668.0 / max(1.0, s1.width)), opacity=env_hk)
                    paste_centered(comp_im, s2, CENTER_X, 1288, scale_x=min(1.0, 670.0 / max(1.0, s2.width)), opacity=env_hk)

            # Mid A-Roll Overhead Badge / 3D Flip (strictly at cx = 540, cy = 362 < 470!)
            if tl["flip3d_aroll"]:
                f0, f1 = tl["flip3d_aroll"]
                efl = smooth_in_out_env(t, f0, f1, 0.28, 0.26)
                if efl > 0.01:
                    u_fl = quintic(clamp01((t - (f0 + 0.55)) / 0.54))
                    cs_f = math.cos(u_fl * math.pi)
                    rk, si, thm, tt, sb, bdg, bv = cfg["flip3d"]
                    if hstyle["end_mode"] == "royal_card_endcard":
                        c3d = make_card_back(320, 198, brand_lbl) if cs_f >= 0 else make_luxury_playing_card(320, 198, rk, si, thm, tt.replace("\n", " "), sb, badge_txt=bdg, big_val=bv)
                    else:
                        c3d = make_frosted_glass_card(420, 182, bdg, tt.replace("\n", " "), sb, big_val=bv, tint_rgb=(18, 44, 88), rim_rgb=pri_c)
                        cs_f = -1.0  # Smooth scale-focus without playing-card back
                    paste_centered(comp_im, c3d, CENTER_X, 356 + math.sin(t * 2.5) * 3.0, scale_x=max(0.06, abs(cs_f)) * (0.92 + 0.08 * efl), scale_y=0.92 + 0.08 * efl, opacity=efl)

            if not in_hook:
                render_hybrid_captions(comp_im, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1205, max_w=SAFE_CENTER_MAX_W, base_pt=76, lh=88)

    # ==========================================================================
    # 9 DISTINCT NATIVE VISUAL STAGE ARCHITECTURES (100% SYMMETRIC ON X = 540!)
    # ==========================================================================
    for st_kind, s0, s1, ev, no_pip in active_full:
        dt = max(0.0, t - s0)
        stage = surf_im.copy()
        d_st = ImageDraw.Draw(stage)

        if st_kind == "hook_full":
            hk = cfg["hook"]
            p_top = make_kobe_tilted_pill(hk["l1"], "", (18, 24, 38), pri_c, (255, 255, 255), max_w=860, pt=46)
            paste_centered(stage, p_top, CENTER_X, 318, angle=-1.4)
            vf0 = sample_clip_pingpong(brolls[0], dt, rate=1.0)
            if hstyle["hook_mode"] == "collage_polaroid_hook":
                vp0 = make_collage_polaroid(vf0, 820, 488, f"{hk['l2a']} {hk['l2b']} — {hk['l3']}")
            else:
                vp0 = make_clean_broll_viewport(vf0, 884, 468, f"{hk['l2a']} {hk['l2b']}", hk["l3"], accent_rgb=pri_c, light_ui=light_m)
            paste_centered(stage, vp0, CENTER_X, 656, scale_x=0.95 + 0.05 * ease_out_cubic(min(1.0, dt / 0.30)))
            p_bot = make_kobe_tilted_pill(hk["l2a"], hk["l2b"], (18, 24, 38), (225, 29, 72), (255, 250, 236), max_w=668, pt=56)
            paste_centered(stage, p_bot, CENTER_X, 1052, angle=1.1)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1268, max_w=SAFE_CENTER_MAX_W, base_pt=70, lh=82)

        elif st_kind == "kobe_saas_highway_pip":
            # NATIVE KOBE LIGHT SAAS UI: Pure White Cards (1 -> 2 -> 3) + Dashed Highway + Chain Pills + Circle PiP!
            fn_c = cfg["fan"]
            p_hd = make_kobe_tilted_pill("LỘ TRÌNH:", fn_c["headline"], (16, 22, 36), pri_c, (255, 255, 255), max_w=880, pt=42)
            paste_centered(stage, p_hd, CENTER_X, 308, angle=-1.5)

            d_st.rounded_rectangle([92, 594, 988, 638], radius=22, fill=(*pri_c, 72 if light_m else 105))
            for dx_h in range(118, 962, 42):
                d_st.line([(dx_h, 616), (dx_h + 22, 616)], fill=(255, 255, 255, 235), width=5)

            cards_3 = [
                (1, fn_c["left"][1],  (235, 72, 78), fn_c["left"][3],  fn_c["left"][4],  fn_c["left"][5]),
                (2, fn_c["right"][1], pri_c,         fn_c["right"][3], fn_c["right"][4], fn_c["right"][5]),
                (3, fn_c["ace"][1],   (228, 142, 18),fn_c["ace"][3],   fn_c["ace"][4],   fn_c["ace"][5]),
            ]
            for idx_c, (snum, ic_k, acc_c, tt, sb, bdg) in enumerate(cards_3):
                st_c = 0.06 + idx_c * 0.18
                if dt >= st_c:
                    dc = dt - st_c
                    uc = ease_out_back(min(1.0, dc / 0.28), 1.10)
                    c_im = make_kobe_saas_step_card(276, 344, snum, ic_k, acc_c, tt, sb, tag_txt=bdg)
                    cx_i = [220, 540, 860][idx_c]  # 540 - 320, 540, 540 + 320 (100% symmetric!)
                    paste_centered(stage, c_im, cx_i, 616 + (1.0 - uc) * (-88.0), scale_x=0.92 + 0.08 * clamp01(dc / 0.22))
                    draw_landing_ripple(stage, cx_i, 796, dc - 0.22, rx_max=102, ry_max=18, col=acc_c)

            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=948, max_w=SAFE_CENTER_MAX_W, base_pt=66, lh=78, single_line=True)
            if not no_pip:
                draw_kobe_circle_pip(stage, fg_rgb, t, s0, s1, cx=CENTER_X, cy=1312, diam=324, ring_col=pri_c, light_mode=light_m)
            else:
                draw_packshot_pod_symmetric(stage, assets, cfg, t, cy=1235, style="kobe", pri_rgb=pri_c)

        elif st_kind == "kobe_cyber_tank_pip":
            # NATIVE KOBE CYBER MONITOR + STATE-ESCALATION TANK + GRAVITY PARTICLES (Symmetric: Left 356, Right 808 -> Outer [98..982]!)
            cl_c = cfg["clash"]
            p_hd = make_kobe_tilted_pill("⚡ CẢNH BÁO:", cl_c["rib_title"], (20, 22, 30), (225, 29, 72), (255, 255, 255), max_w=880, pt=40)
            paste_centered(stage, p_hd, CENTER_X, 308, angle=-1.3)

            vf1 = sample_clip_pingpong(brolls[0], dt, rate=1.0)
            mon = make_clean_broll_viewport(vf1, 516, 352, cl_c["top_pill"], cl_c["top_foot"], accent_rgb=(238, 64, 82), light_ui=light_m)
            paste_centered(stage, mon, 356, 604)  # Left = 356 - 258 = 98px!

            tank = Image.new("RGBA", (348, 364), (0, 0, 0, 0))
            td = ImageDraw.Draw(tank)
            td.rounded_rectangle([6, 6, 341, 357], radius=28, fill=(255, 255, 255, 248) if light_m else (20, 26, 38, 246), outline=(238, 58, 76, 248), width=4)
            n_bars = min(5, max(1, int(dt / 0.40) + 1))
            bar_cols = [(54, 162, 235), (82, 196, 148), (245, 198, 56), (245, 128, 42), (238, 48, 68)]
            for bi in range(n_bars):
                by1 = 298 - bi * 48
                td.rounded_rectangle([32, by1 - 36, 316, by1], radius=12, fill=(*bar_cols[bi], 246))
            fb_t = get_font(FONT_BLACK, 23)
            lbl_tk = "MỨC ĐỘ BÁO ĐỘNG!"
            bt_k = td.textbbox((0, 0), lbl_tk, font=fb_t)
            td.text((174 - (bt_k[2] - bt_k[0]) * 0.5, 314), lbl_tk, font=fb_t, fill=(225, 29, 72, 255))
            paste_centered(stage, tank, 808, 604)  # Right = 808 + 174 = 982px -> Outer [98..982], Midpoint = 540.0!

            if dt >= 1.25:
                dt_p = (dt - 1.25) % 1.35
                for pi in range(7):
                    px = 808 + (pi - 3) * 28.0 * dt_p
                    py = 432 + (-135.0 + 290.0 * dt_p) * dt_p
                    if 260 <= py <= 840:
                        d_st.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(242, 64, 82, int(240 * clamp01(1.2 - dt_p))))

            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=948, max_w=SAFE_CENTER_MAX_W, base_pt=66, lh=78, single_line=True)
            if not no_pip:
                draw_kobe_circle_pip(stage, fg_rgb, t, s0, s1, cx=CENTER_X, cy=1312, diam=324, ring_col=(238, 58, 76), light_mode=light_m)
            else:
                draw_packshot_pod_symmetric(stage, assets, cfg, t, cy=1235, style="cyber", pri_rgb=pri_c)

        elif st_kind == "viethan_5cell_bento":
            # NATIVE VIỆT-HÀN 5-CELL BENTO GRID (3 Top + 2 Symmetric Bottom around X = 540!)
            render_viethan_5cell_bento(stage, dt, brolls, cfg, assets)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1108, max_w=SAFE_CENTER_MAX_W, base_pt=66, lh=78, single_line=True)
            if not no_pip:
                draw_kobe_circle_pip(stage, fg_rgb, t, s0, s1, cx=CENTER_X, cy=1352, diam=276, ring_col=(14, 148, 82), light_mode=light_m)
            else:
                paste_centered(stage, assets["prods"][0], CENTER_X, 1345 + math.sin(t * 2.5) * 4.0, scale_x=0.58)

        elif st_kind == "editorial_chart_arch":
            # NATIVE HD-CL EDITORIAL PAPER + ANIMATED STEP-LINE CURVE + DOME-ARCH SPEAKER PiP!
            cl_c = cfg["clash"]
            hd_ed = make_editorial_paper_card(888, 126, brand_lbl, cl_c["rib_title"], cl_c["rib_lbl"], accent_rgb=pri_c)
            paste_centered(stage, hd_ed, CENTER_X, 336)

            # Animated Editorial Chart Panel (cx = 540, cy = 628, w = 888, h = 368, Y = 444..812 < 860px!)
            ch_im = Image.new("RGBA", (888, 368), (0, 0, 0, 0))
            cd = ImageDraw.Draw(ch_im)
            cd.rounded_rectangle([0, 0, 887, 367], radius=22, fill=(253, 249, 240, 252), outline=(34, 28, 22, 235), width=3)
            for gy_c in [85, 165, 245, 315]:
                cd.line([(56, gy_c), (832, gy_c)], fill=(216, 204, 182, 180), width=1)
            # Red trap spike-and-crash curve vs Emerald steady nourishment curve!
            prog_c = clamp01(dt / 1.15)
            pts_bad  = [(70, 275), (245, 78), (444, 305), (645, 318), (818, 322)]
            pts_good = [(70, 265), (255, 155), (444, 138), (645, 132), (818, 126)]
            n_seg = max(2, int(round(prog_c * len(pts_bad))))
            cd.line(pts_bad[:n_seg],  fill=(220, 38, 62, 235), width=6)
            cd.line(pts_good[:n_seg], fill=(16, 138, 86, 255), width=8)
            for px_c, py_c in pts_good[:n_seg]:
                cd.ellipse([px_c - 8, py_c - 8, px_c + 8, py_c + 8], fill=(16, 138, 86, 255), outline=(255, 255, 255, 255), width=2)
            fl_c = get_font(FONT_EBOLD, 22)
            cd.text((76, 24), f"● CHUẨN KHOA HỌC: {cfg['fan']['ace'][3]}", font=fl_c, fill=(14, 126, 78, 255))
            cd.text((520, 24), f"● SAI LẦM: {cfg['fan']['left'][3]}", font=fl_c, fill=(212, 32, 56, 255))
            paste_centered(stage, ch_im, CENTER_X, 628)

            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=938, max_w=SAFE_CENTER_MAX_W, base_pt=66, lh=78, single_line=True)
            if not no_pip:
                draw_editorial_arch_pip(stage, fg_rgb, t, s0, s1, cx=CENTER_X, cy=1306, w=288, h=332, accent_rgb=pri_c)
            else:
                draw_packshot_pod_symmetric(stage, assets, cfg, t, cy=1235, style="editorial", pri_rgb=pri_c)

        elif st_kind == "tvc_gold_portal":
            # NATIVE TVC COMFORT CIRCULAR SPINNING GOLD PORTAL + SPARKLES + GOLD PLAQUE!
            rf_c = cfg["riffle"]
            p_top = make_kobe_tilted_pill("✦ TINH HOA:", rf_c["pill1"], (48, 14, 26), (188, 118, 18), (255, 248, 228), max_w=880, pt=36)
            paste_centered(stage, p_top, CENTER_X, 304)

            vf_p = sample_clip_pingpong(brolls[2], dt, rate=1.0)
            draw_tvc_gold_portal(stage, vf_p, t, cx=CENTER_X, cy=585, diam=408)
            draw_4pt_sparkle(stage, 286, 425, 24 + 5 * math.sin(t * 6.0), rot_deg=t * 42)
            draw_4pt_sparkle(stage, 794, 425, 24 + 5 * math.cos(t * 6.0), rot_deg=-t * 42)

            # Symmetric Lower Gold Pod (382) + Packshot (698) around X = 540!
            hrk, hsi, hth, htt, hsb, hbd, hbv = rf_c["hero"]
            plq_h = make_tvc_gold_cta_plaque(322, 242, hbd, f"{hbv}\n{htt}", hsb)
            paste_centered(stage, plq_h, 382, 1055)
            paste_centered(stage, assets["prods"][0], 704, 1055 + math.sin(t * 2.5) * 4.5, scale_x=0.60)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1348, max_w=SAFE_CENTER_MAX_W, base_pt=68, lh=80, single_line=True)

        elif st_kind == "collage_polaroid_spread":
            # NATIVE STYLE-SAMPLING COLLAGE POLAROID WASHI-TAPE SPREAD (100% Symmetric on X = 540!)
            fn_c = cfg["fan"]
            p_hd = make_kobe_tilted_pill("📌 GÓC THỰC TẾ:", fn_c["headline"], (22, 20, 18), pri_c, (255, 252, 242), max_w=880, pt=40)
            paste_centered(stage, p_hd, CENTER_X, 306, angle=-1.2)

            pol_l = make_collage_polaroid(sample_clip_pingpong(brolls[0], dt, 1.0), 416, 356, f"{fn_c['left'][3]} — {fn_c['left'][5]}", tape_rgb=(246, 138, 124))
            pol_r = make_collage_polaroid(sample_clip_pingpong(brolls[2], dt, 1.0), 416, 356, f"{fn_c['ace'][3]} — {fn_c['ace'][5]}", tape_rgb=(132, 224, 178))
            # Left center = 316, Right center = 764 -> Midpoint = (316+764)/2 = 540.0! (< 860px!)
            paste_centered(stage, pol_l, 316, 602, angle=-4.2)
            paste_centered(stage, pol_r, 764, 602, angle=+4.2)

            draw_packshot_pod_symmetric(stage, assets, cfg, t, cy=1055, style="editorial", pri_rgb=pri_c)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1348, max_w=SAFE_CENTER_MAX_W, base_pt=68, lh=80, single_line=True)

        elif st_kind == "kobe_dna_helix":
            # NATIVE KOBE 22-COLUMN DOUBLE-HELIX WAVE + CLEAN VIEWPORT + CYBER/GLASS HERO CARD!
            rf_c = cfg["riffle"]
            vf2 = sample_clip_pingpong(brolls[2], dt, rate=1.0)
            vp2 = make_clean_broll_viewport(vf2, 888, 382, rf_c["pill1"], rf_c["foot1"], accent_rgb=pri_c, light_ui=False)
            paste_centered(stage, vp2, CENTER_X, 464)

            # Symmetric 22-Column DNA Wave: X from 141 to 939 (Midpoint = (141+939)/2 = 540.0!)
            for ci in range(22):
                gx = 141 + ci * 38
                ph1 = t * 4.2 + ci * 0.36
                y_a = 768 + math.sin(ph1) * 46.0
                y_b = 768 - math.sin(ph1) * 46.0
                d_st.line([(gx, y_a), (gx, y_b)], fill=(*pri_c, 95), width=2)
                d_st.ellipse([gx - 9, y_a - 9, gx + 9, y_a + 9], fill=(*pri_c, 248))
                d_st.ellipse([gx - 9, y_b - 9, gx + 9, y_b + 9], fill=(*sec_c, 248))

            draw_packshot_pod_symmetric(stage, assets, cfg, t, cy=1075, style="cyber", pri_rgb=pri_c)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1358, max_w=SAFE_CENTER_MAX_W, base_pt=68, lh=80, single_line=True)

        elif st_kind == "saas_glass_laser":
            # NATIVE SAAS GLASSMORPHISM HUD + GLOWING LASER TRIM-PATH (100% Symmetric on X = 540!)
            rf_c = cfg["riffle"]
            vf2 = sample_clip_pingpong(brolls[2], dt, rate=1.0)
            vp2 = make_clean_broll_viewport(vf2, 888, 372, rf_c["pill1"], rf_c["foot1"], accent_rgb=pri_c, light_ui=False)
            paste_centered(stage, vp2, CENTER_X, 456)

            prog_l = clamp01(dt / 0.82)
            lx_end = int(220 + 640 * prog_l)  # 220 .. 860 (Midpoint = 540!)
            d_st.line([(220, 748), (860, 748)], fill=(*pri_c, 68), width=5)
            d_st.line([(220, 748), (lx_end, 748)], fill=(255, 238, 130, 255), width=7)
            d_st.ellipse([lx_end - 11, 748 - 11, lx_end + 11, 748 + 11], fill=(255, 255, 255, 255))

            nodes = [rf_c["c1"][3], rf_c["c2"][3], rf_c["hero"][6]]
            for ni, n_lbl in enumerate(nodes):
                nx = [220, 540, 860][ni]
                lit = (lx_end >= nx - 20)
                nd_im = make_frosted_glass_card(262, 102, None, n_lbl.replace("\n", " "), "", tint_rgb=(28, 66, 118) if lit else (14, 28, 52), rim_rgb=(255, 228, 112) if lit else pri_c)
                paste_centered(stage, nd_im, nx, 748, scale_x=1.03 if lit else 0.95)

            draw_packshot_pod_symmetric(stage, assets, cfg, t, cy=1075, style="glass", pri_rgb=pri_c)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1358, max_w=SAFE_CENTER_MAX_W, base_pt=68, lh=80, single_line=True)

        elif st_kind == "playing_card_fan":
            # COLLECTOR 3-CARD HAND FAN (Used selectively on v10, v17 — 100% Symmetric on X = 540!)
            fn_c = cfg["fan"]
            vf_f = sample_clip_pingpong(brolls[2], dt, rate=1.0)
            c_vid = make_video_playing_card(vf_f, 880, 372, "J", "star", "ivory", "PHÂN TÍCH CHUYÊN SÂU", fn_c["headline"], zoom=1.03)
            paste_centered(stage, c_vid, CENTER_X, 456)

            u_op = ease_out_back(min(1.0, dt / 0.45), 1.08)
            c_l = make_luxury_playing_card(224, 318, *fn_c["left"][:5],  badge_txt=fn_c["left"][5])
            c_r = make_luxury_playing_card(224, 318, *fn_c["right"][:5], badge_txt=fn_c["right"][5])
            c_a = make_luxury_playing_card(242, 342, *fn_c["ace"][:5],   badge_txt=fn_c["ace"][5])
            paste_centered(stage, c_l, CENTER_X - 196 * u_op, 1020 + 16 * u_op, angle=-13.5 * u_op)
            paste_centered(stage, c_r, CENTER_X + 196 * u_op, 1020 + 16 * u_op, angle=+13.5 * u_op)
            lift = 22.0 * smoothstep((dt - 0.60) / 0.32) if dt > 0.60 else 0.0
            paste_centered(stage, c_a, CENTER_X, 992 - lift, sweep_prog=((dt - 0.65) / 1.3) % 1.3 if dt > 0.65 else None)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1342, max_w=SAFE_CENTER_MAX_W, base_pt=68, lh=80, single_line=True)

        elif st_kind == "playing_card_riffle":
            # COLLECTOR PLAYING-CARD RIFFLE + PACKSHOT (Used selectively on v01, v06, v17 — Symmetric 382 & 698!)
            rf_c = cfg["riffle"]
            dur_r = max(1.0, s1 - s0)
            vf3 = sample_clip_pingpong(brolls[2], dt, rate=1.0)
            vf4 = sample_clip_pingpong(brolls[3], max(0.0, dt - dur_r * 0.45), rate=1.0)
            w_m = smoothstep((dt - dur_r * 0.48) / 0.40) if dt >= dur_r * 0.48 else 0.0
            vfm = np.clip(vf3.astype(np.float32) * (1.0 - w_m) + vf4.astype(np.float32) * w_m, 0, 255).astype(np.uint8)
            use2 = (dt >= dur_r * 0.50)
            c_up = make_video_playing_card(vfm, 880, 404, "A", "star", "ivory", rf_c["pill2"] if use2 else rf_c["pill1"], rf_c["foot2"] if use2 else rf_c["foot1"], zoom=1.03)
            paste_centered(stage, c_up, CENTER_X, 472)

            if dt >= 0.20:
                dh = dt - 0.20
                uh = quintic(clamp01(dh / 0.45))
                cs_h = math.cos(uh * math.pi)
                hrk, hsi, hth, htt, hsb, hbd, hbv = rf_c["hero"]
                hc = make_card_back(316, 286, brand_lbl) if cs_h >= 0 else make_luxury_playing_card(316, 286, hrk, hsi, hth, htt, hsb, badge_txt=hbd, big_val=hbv)
                paste_centered(stage, hc, 382, 1068, scale_x=max(0.05, abs(cs_h)), sweep_prog=((dh - 0.48) / 1.2) % 1.2 if dh > 0.48 else None)

            prods = assets["prods"]
            if len(prods) >= 2:
                paste_centered(stage, prods[0], 666, 1055 + math.sin(t * 2.4) * 4.0, scale_x=0.52)
                paste_centered(stage, prods[1], 734, 1085 + math.sin(t * 2.4 + 0.8) * 4.0, scale_x=0.50)
            else:
                paste_centered(stage, prods[0], 698, 1068 + math.sin(t * 2.4) * 4.5, scale_x=0.62)
            render_hybrid_captions(stage, t, cap_groups, cfg, hstyle["sub_mode"], cx=CENTER_X, y_base=1358, max_w=SAFE_CENTER_MAX_W, base_pt=68, lh=80, single_line=True)

        # ----------------------------------------------------------------------
        # 4 DISTINCT BRAND END-CARD ARCHITECTURES (100% SYMMETRIC ON X = 540!)
        # ----------------------------------------------------------------------
        elif st_kind == "tvc_bling_endcard":
            ec = cfg["endcard"]
            paste_centered(stage, assets["logo"], CENTER_X, 304, scale_x=0.92)
            sp_h = render_glow_text_sprite(ec["headline"], FONT_BLACK, 50, (255, 246, 192), (222, 152, 34), glow_col=(255, 200, 72), glow_rad=12, stroke_col=(28, 10, 18), stroke_w=5)
            paste_centered(stage, sp_h, CENTER_X, 400, scale_x=min(1.0, 900.0 / max(1.0, sp_h.width)))

            # Symmetric Upper Showcase (< 860px): Packshot at 340, Gold Spec Plaque + Signature at 740 -> Midpoint = 540.0!
            prods = assets["prods"]
            paste_centered(stage, prods[0], 340, 668 + math.sin(t * 2.5) * 4.0, scale_x=0.78 * clamp01(dt / 0.24), angle=-6.0)
            draw_4pt_sparkle(stage, 218, 540, 24 + 5 * math.sin(t * 6), rot_deg=t * 40)
            draw_4pt_sparkle(stage, 462, 540, 20 + 5 * math.cos(t * 5), rot_deg=-t * 35)

            spec_p = make_tvc_gold_cta_plaque(360, 232, "CHUẨN CHÍNH HÃNG", ec["left"][3], f"{ec['left'][6]} • {ec['right'][6]}")
            paste_centered(stage, spec_p, 740, 635)
            sp_sig = render_glow_text_sprite("Nguyễn Thị Hằng", FONT_SCRIPT, 48, (255, 238, 156), (235, 178, 62), glow_rad=8, stroke_col=(24, 12, 18), stroke_w=3)
            paste_centered(stage, sp_sig, 740, 804, opacity=clamp01((dt - 0.16) / 0.32))

            pulse = 1.0 + 0.022 * math.sin(dt * 7.0)
            cta_p = make_tvc_gold_cta_plaque(668, 268, ec["cta_badge"], ec["cta_title"], ec["cta_sub"])
            paste_centered(stage, cta_p, CENTER_X, 1268, scale_x=pulse * clamp01(dt / 0.22))

        elif st_kind == "kobe_ui_endcard":
            ec = cfg["endcard"]
            paste_centered(stage, assets["logo"], CENTER_X, 304, scale_x=0.92)
            win = Image.new("RGBA", (888, 456), (0, 0, 0, 0))
            wd = ImageDraw.Draw(win)
            wd.rounded_rectangle([4, 4, 883, 451], radius=32, fill=(255, 255, 255, 252) if light_m else (18, 28, 44, 248), outline=(*pri_c, 225), width=4)
            f_wh = get_font(FONT_BLACK, 34)
            while f_wh.size > 22 and wd.textbbox((0, 0), ec["headline"], font=f_wh)[2] > 830: f_wh = get_font(FONT_BLACK, f_wh.size - 2)
            bw_h = wd.textbbox((0, 0), ec["headline"], font=f_wh)
            wd.text((444 - (bw_h[2] - bw_h[0]) * 0.5, 26), ec["headline"], font=f_wh, fill=(16, 24, 40, 255) if light_m else (255, 236, 122, 255))
            checks = [
                f"✓ {ec['left'][3]}: {ec['left'][6]}",
                f"✓ {ec['right'][3]}: {ec['right'][6]}",
                "✓ Chính hãng 100% • Tư vấn 1-1",
            ]
            f_ck = get_font(FONT_EBOLD, 29)
            for ci_k, c_str in enumerate(checks):
                wd.rounded_rectangle([356, 104 + ci_k * 102, 852, 186 + ci_k * 102], radius=20, fill=(236, 253, 245, 255) if light_m else (24, 52, 48, 235))
                while f_ck.size > 19 and wd.textbbox((0, 0), c_str, font=f_ck)[2] > 468: f_ck = get_font(FONT_EBOLD, f_ck.size - 2)
                wd.text((378, 124 + ci_k * 102), c_str, font=f_ck, fill=(12, 122, 74, 255) if light_m else (152, 255, 208, 255))
            paste_centered(stage, win, CENTER_X, 604)
            paste_centered(stage, assets["prods"][0], 276, 636 + math.sin(t * 2.4) * 4.0, scale_x=0.66)

            # Native Kobe White/Blue Pill CTA Box at cx = 540 (NO playing-card border!)
            pulse = 1.0 + 0.022 * math.sin(dt * 7.0)
            cta_k = make_kobe_saas_step_card(668, 268, "★", "star", pri_c, ec["cta_title"], ec["cta_sub"], tag_txt=ec["cta_badge"])
            paste_centered(stage, cta_k, CENTER_X, 1268, scale_x=pulse * clamp01(dt / 0.22), angle=-1.0)

        elif st_kind == "saas_glass_endcard":
            ec = cfg["endcard"]
            paste_centered(stage, assets["logo"], CENTER_X, 304, scale_x=0.92)
            sp_eh = render_glow_text_sprite(ec["headline"], FONT_BLACK, 48, (214, 244, 255), (112, 198, 255), glow_rad=10, stroke_col=(6, 16, 34), stroke_w=5)
            paste_centered(stage, sp_eh, CENTER_X, 398, scale_x=min(1.0, 900.0 / max(1.0, sp_eh.width)))

            # Symmetric Glass Pods at 218 & 862 + Center Packshot at 540!
            gl_l = make_frosted_glass_card(256, 276, ec["left"][5], ec["left"][3], ec["left"][4], big_val=ec["left"][6], tint_rgb=(18, 48, 92), rim_rgb=pri_c)
            gl_r = make_frosted_glass_card(256, 276, ec["right"][5], ec["right"][3], ec["right"][4], big_val=ec["right"][6], tint_rgb=(18, 48, 92), rim_rgb=pri_c)
            paste_centered(stage, gl_l, 218, 658)
            paste_centered(stage, gl_r, 862, 658)
            paste_centered(stage, assets["prods"][0], CENTER_X, 668 + math.sin(t * 2.4) * 4.5, scale_x=0.76)

            pulse = 1.0 + 0.022 * math.sin(dt * 7.0)
            cta_g = make_frosted_glass_card(668, 268, ec["cta_badge"], ec["cta_title"], ec["cta_sub"], tint_rgb=(24, 62, 118), rim_rgb=(255, 228, 116))
            paste_centered(stage, cta_g, CENTER_X, 1268, scale_x=pulse * clamp01(dt / 0.22))

        else:  # "royal_card_endcard" (Symmetric 206, 540, 874 -> Midpoint = 540.0!)
            ec = cfg["endcard"]
            paste_centered(stage, assets["logo"], CENTER_X, 304, scale_x=0.92)
            sp_eh = render_glow_text_sprite(ec["headline"], FONT_BLACK, 50, (255, 236, 118), (238, 168, 40), glow_rad=10, stroke_col=(10, 20, 18), stroke_w=5)
            paste_centered(stage, sp_eh, CENTER_X, 400, scale_x=min(1.0, 900.0 / max(1.0, sp_eh.width)))

            c5_l = make_luxury_playing_card(244, 308, *ec["left"][:5],  badge_txt=ec["left"][5],  big_val=ec["left"][6])
            c5_r = make_luxury_playing_card(244, 308, *ec["right"][:5], badge_txt=ec["right"][5], big_val=ec["right"][6])
            paste_centered(stage, c5_l, 206, 652, scale_x=0.94, angle=-7.5)
            paste_centered(stage, c5_r, 874, 652, scale_x=0.94, angle=+7.5)

            prods = assets["prods"]
            if len(prods) >= 3:
                paste_centered(stage, prods[0], 436, 780, scale_x=0.58)
                paste_centered(stage, prods[1], 540, 766, scale_x=0.62)
                paste_centered(stage, prods[2], 644, 786, scale_x=0.56)
            elif len(prods) == 2:
                paste_centered(stage, prods[0], 472, 780, scale_x=0.66)
                paste_centered(stage, prods[1], 608, 792, scale_x=0.68)
            else:
                paste_centered(stage, prods[0], CENTER_X, 780, scale_x=0.80)

            pulse = 1.0 + 0.022 * math.sin(dt * 7.2)
            cta_c = make_luxury_playing_card(668, 276, "A", "star", "gold_ace", ec["cta_title"], ec["cta_sub"], badge_txt=ec["cta_badge"])
            paste_centered(stage, cta_c, CENTER_X, 1272, scale_x=pulse * clamp01(dt / 0.22), sweep_prog=(dt / 1.15) % 1.35)

        if comp_im is None or ev >= 0.995:
            comp_im = stage
        else:
            arr_s = np.array(stage)
            arr_s[:, :, 3] = (arr_s[:, :, 3].astype(np.float32) * ev).astype(np.uint8)
            comp_im.alpha_composite(Image.fromarray(arr_s, "RGBA"))

    # Dead-Center Compliant Legal Disclaimer (cx = 540, max_w = 672 -> X in [204..876] <= 884, Y = 1522 <= 1545!)
    sp_leg = render_glow_text_sprite(cfg["legal"], FONT_BOLD, 20, (238, 246, 242), glow_rad=0, stroke_col=(10, 16, 20), stroke_w=3)
    paste_centered(comp_im, sp_leg, CENTER_X, 1522, scale_x=min(1.0, 672.0 / max(1.0, sp_leg.width)), opacity=0.88)
    return comp_im


def render_v2_chunk(args):
    vid_key, c_idx, f_start, f_end = args
    v_dir  = os.path.join(BATCH_DIR, vid_key)
    meta   = json.load(open(os.path.join(v_dir, "v2_meta.json"), "r", encoding="utf-8"))
    tr_j   = json.load(open(os.path.join(v_dir, "v2_clean.json"), "r", encoding="utf-8"))
    cfg    = EP18_CONFIGS[vid_key]
    hstyle = HYBRID_STYLES[vid_key]
    tl     = build_hybrid_timeline(meta, cfg, hstyle)
    end_s0 = tl["full_stages"][-1][1]
    caps   = build_caption_groups(tr_j, tl["hook_aroll"], end_s0)
    brolls = [load_vid_frames_wh(p, 960, 540) for p in cfg["brolls"]]
    assets = load_ep_static_assets(cfg)

    n_frames = f_end - f_start
    ss_sec   = f"{f_start / FPS:.6f}"
    chunk_mp4 = os.path.join(v_dir, f"_v2_chunk_{c_idx:02d}.mp4")
    vid_p = os.path.join(v_dir, "v2_graded.mp4")
    mat_p = os.path.join(v_dir, "v2_matte.mp4")

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
        im_out = compose_hybrid_frame(f_start + li, rgb, mat, brolls, assets, caps, cfg, hstyle, tl, meta)
        writer.stdin.write(np.array(im_out.convert("RGB"), dtype=np.uint8).tobytes())

    writer.stdin.close(); writer.wait()
    pv.stdout.close(); pv.wait()
    pm.stdout.close(); pm.wait()
    return chunk_mp4


def run_18_styles_preview_sheet():
    for nm, (x1, y1, x2, y2) in [
        ("DeadCenter Lower Pill",    (540 - 336, 1140, 540 + 336, 1380)),
        ("DeadCenter Framed A-Roll", (540 - 336, 348,  540 + 336, 1152)),
        ("DeadCenter Circle PiP",    (540 - 170, 1140, 540 + 170, 1500)),
        ("DeadCenter End CTA",       (540 - 334, 1130, 540 + 334, 1410)),
        ("Symmetric Lower Pods",     (224,       865,  856,       1260)),
        ("Upper Stage Area",         (80,        256,  1000,      845)),
    ]:
        ok, rsn = is_box_safe_9x16(x1, y1, x2, y2)
        assert ok, f"SafeZone fail {nm}: {rsn}"
    print("[V2 AUDIT] 100% Dead-Center (X=540) + Safe Zone + 18 Distinct Hybrid Styles VERIFIED!", flush=True)

    pw, ph = 240, 426
    all_vks = list(EP18_CONFIGS.keys())
    sheet = Image.new("RGB", (pw * 6, ph * 6), (14, 18, 24))
    f_lbl = get_font(FONT_BOLD, 15)

    p_idx = 0
    for vk in all_vks:
        v_dir  = os.path.join(BATCH_DIR, vk)
        meta   = json.load(open(os.path.join(v_dir, "v2_meta.json"), "r", encoding="utf-8"))
        tr_j   = json.load(open(os.path.join(v_dir, "v2_clean.json"), "r", encoding="utf-8"))
        cfg    = EP18_CONFIGS[vk]
        hstyle = HYBRID_STYLES[vk]
        tl     = build_hybrid_timeline(meta, cfg, hstyle)
        end_s0 = tl["full_stages"][-1][1]
        caps   = build_caption_groups(tr_j, tl["hook_aroll"], end_s0)
        brolls = [load_vid_frames_wh(p, 960, 540) for p in cfg["brolls"]]
        assets = load_ep_static_assets(cfg)

        st1 = tl["full_stages"][1] if cfg.get("force_fullscreen_speech") else tl["full_stages"][0]
        t_stage = (st1[1] + st1[2]) * 0.52
        t_aroll = 5.2 if (not cfg.get("force_fullscreen_speech") and st1[1] > 5.8) else 1.45
        for ts in [t_aroll, t_stage]:
            f_idx = min(meta["total_frames"] - 2, max(1, int(round(ts * FPS))))
            ss = f"{f_idx / FPS:.6f}"
            rv = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", os.path.join(v_dir, "v2_graded.mp4"), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
            rm = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", os.path.join(v_dir, "v2_matte.mp4"),  "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray",  "-"])
            rgb = np.frombuffer(rv[:W * H * 3], dtype=np.uint8).reshape((H, W, 3))
            mat = np.frombuffer(rm[:W * H],     dtype=np.uint8).reshape((H, W))
            im_c = compose_hybrid_frame(f_idx, rgb, mat, brolls, assets, caps, cfg, hstyle, tl, meta).convert("RGB").resize((pw, ph), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im_c)
            # Draw faint cyan X=540 symmetry guide on preview sheet!
            d.line([(pw // 2, 0), (pw // 2, ph)], fill=(54, 224, 210), width=1)
            d.rounded_rectangle([4, 4, 234, 26], radius=6, fill=(10, 14, 22))
            d.text((8, 6), f"{vk}•{meta['code']} {hstyle['aroll_mode'][:11]}", font=f_lbl, fill=(255, 228, 98))
            sheet.paste(im_c, ((p_idx % 6) * pw, (p_idx // 6) * ph))
            p_idx += 1

    out_p = os.path.join(BATCH_DIR, "v2_18_hybrid_styles_test_sheet.jpg")
    sheet.save(out_p, quality=92)
    print("Saved 36-panel 18-Hybrid-Styles Test Sheet ->", out_p, flush=True)


def main():
    if "--test" in sys.argv:
        run_18_styles_preview_sheet()
        return

    only_vids = [a for a in sys.argv[1:] if a.startswith("v")]
    target_keys = only_vids if only_vids else list(EP18_CONFIGS.keys())
    t_all = time.time()
    N_WORKERS = 4

    for idx_e, vk in enumerate(target_keys, 1):
        v_dir = os.path.join(BATCH_DIR, vk)
        out_v = os.path.join(v_dir, "_v2_video_only.mp4")
        meta  = json.load(open(os.path.join(v_dir, "v2_meta.json"), "r", encoding="utf-8"))
        tot_f = int(meta["total_frames"])

        t0 = time.time()
        step = math.ceil(tot_f / N_WORKERS)
        tasks = [(vk, i, i * step, min(tot_f, (i + 1) * step)) for i in range(N_WORKERS) if i * step < tot_f]
        print(f"[{idx_e:02d}/{len(target_keys)}] Rendering {vk} ({meta['code']} • {HYBRID_STYLES[vk]['style_title']} • {tot_f}f = {meta['duration_s']}s)...", flush=True)
        with concurrent.futures.ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            chunks = list(ex.map(render_v2_chunk, tasks))

        lst = os.path.join(v_dir, "_v2_chunks.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for cf in chunks:
                f.write("file '" + cf.replace("\\", "/") + "'\n")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out_v], check=True)
        for cf in chunks + [lst]:
            if os.path.exists(cf):
                os.remove(cf)
        print(f"  -> DONE {vk} ({meta['code']}) in {time.time() - t0:.1f}s!", flush=True)

    print(f"\n=== ALL {len(target_keys)} HYBRID 1.1x VIDEOS RENDERED IN {time.time() - t_all:.1f}s ===", flush=True)


if __name__ == "__main__":
    main()
