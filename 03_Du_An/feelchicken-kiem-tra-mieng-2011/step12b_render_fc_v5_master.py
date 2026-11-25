import json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

sys.path.insert(0, PROJ_DIR)
from step3b_render_fc_kute import (
    COL_CORAL_5, COL_GOLD_5, COL_MINT_5, COL_CREAM_5,
    FONT_BUBBLE, FONT_POP, FONT_SANS_XB,
    GOLD_KEYWORDS, CORAL_KEYWORDS, POP_EMPHASIS,
    clamp01, smoothstep, ease_out_cubic, ease_out_back, smooth_env,
    polish_sunny_frame, get_font, get_text_sprite, paste_centered,
    load_stickers, get_sticker_badge, draw_confetti_burst,
    draw_pill_banner, build_caption_groups, load_all_frames_rgb
)
from step8_render_fc_v2_masterpiece import (
    fit_cover_target, draw_spiky_impact_badge, draw_tiktok_pov_text
)
from step10b_render_fc_v3 import (
    step_zoom, draw_firework_explosion, build_clean_modern_2011_header, make_stacking_quiz_card
)
from step11a_render_fc_v4_master import (
    load_all_frames_gray, fit_cover_gray, draw_four_star,
    DIM_WALL_IM, GLOW_HALO_IM, draw_behind_head_orbital_overlay, draw_bouncy_callout_pill
)

def draw_kawaii_heart(draw, cx, cy, sz, col_rgba, outline_rgba=None):
    pts = []
    for i in range(40):
        th = (2.0 * math.pi * i) / 40.0
        xh = 16.0 * (math.sin(th) ** 3)
        yh = -(13.0 * math.cos(th) - 5.0 * math.cos(2 * th) - 2.0 * math.cos(3 * th) - math.cos(4 * th))
        pts.append((cx + xh * (sz / 16.0), cy + yh * (sz / 16.0)))
    draw.polygon(pts, fill=col_rgba, outline=outline_rgba)

def build_ultra_kute_storefront_card():
    """Ultra-Kute Korean Kawaii Cloud/Sticker Address Card for Scene 6C ('cho image 3 kute hơn'!)"""
    cw, ch = 964, 286
    pad_x, pad_y = 44, 58
    W_c, H_c = cw + pad_x * 2, ch + pad_y * 2
    card = Image.new("RGBA", (W_c, H_c), (0, 0, 0, 0))

    # Soft warm candy drop-shadow
    sh = Image.new("RGBA", (W_c, H_c), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad_x, pad_y + 12, pad_x + cw, pad_y + ch + 12], radius=68, fill=(92, 24, 42, 115))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))
    dr = ImageDraw.Draw(card)

    # Scalloped cute cloud bumps along top & bottom edges for ultra-Kute pastry/sticker feel!
    for bx in range(pad_x + 95, pad_x + cw - 65, 110):
        dr.ellipse([bx - 42, pad_y - 16, bx + 42, pad_y + 44], fill=(255, 255, 255, 255))
        dr.ellipse([bx - 35, pad_y - 9,  bx + 35, pad_y + 38], fill=(255, 112, 146, 255))

    # Outer thick white sticker border + Candy Pink frame + Creamy Milk-Tea inner body!
    dr.rounded_rectangle([pad_x - 10, pad_y - 10, pad_x + cw + 10, pad_y + ch + 10], radius=74, fill=(255, 255, 255, 255))
    dr.rounded_rectangle([pad_x, pad_y, pad_x + cw, pad_y + ch], radius=66, fill=(255, 106, 142, 255))
    dr.rounded_rectangle([pad_x + 14, pad_y + 14, pad_x + cw - 14, pad_y + ch - 14], radius=54, fill=(255, 250, 240, 255), outline=(255, 214, 92, 255), width=5)

    # Cute stitched dashed inner border
    ix0, iy0, ix1, iy1 = pad_x + 28, pad_y + 28, pad_x + cw - 28, pad_y + ch - 28
    for sx_d in range(ix0 + 36, ix1 - 36, 34):
        dr.line([(sx_d, iy0), (sx_d + 16, iy0)], fill=(255, 168, 188, 210), width=3)
        dr.line([(sx_d, iy1), (sx_d + 16, iy1)], fill=(255, 168, 188, 210), width=3)

    cx = W_c // 2

    # Cute Top Ribbon Pill popping out at the top!
    rw, rh = 550, 58
    dr.rounded_rectangle([cx - rw // 2 - 5, pad_y - 26 - 5, cx + rw // 2 + 5, pad_y + rh - 26 + 5], radius=34, fill=(255, 255, 255, 255))
    dr.rounded_rectangle([cx - rw // 2, pad_y - 26, cx + rw // 2, pad_y + rh - 26], radius=30, fill=(238, 52, 88, 255), outline=(255, 224, 96, 255), width=3)
    sp_rib = get_text_sprite("HẸN GẶP BẠN TẠI QUÁN NHA!", FONT_BUBBLE, 28, COL_GOLD_5, outer_stroke=(88, 18, 32), outer_w=4, inner_w=2, shadow_alpha=0)
    paste_centered(card, sp_rib, cx, pad_y + rh // 2 - 26, scale=min(1.0, (rw - 48) / max(1.0, sp_rib.width)))

    # Cute hearts on ribbon ends
    draw_kawaii_heart(dr, cx - rw // 2 + 26, pad_y + 3, 11, (255, 226, 102, 255))
    draw_kawaii_heart(dr, cx + rw // 2 - 26, pad_y + 3, 11, (255, 226, 102, 255))

    # Row 1: Pastel Strawberry Pill for Address ("38 Nguyễn Đình Chiểu • Nha Trang")
    r1_y = pad_y + 108
    dr.rounded_rectangle([pad_x + 48, r1_y - 40, pad_x + cw - 48, r1_y + 40], radius=40, fill=(255, 234, 240, 255), outline=(255, 136, 164, 255), width=4)
    # Cute pin tag on left
    dr.rounded_rectangle([pad_x + 58, r1_y - 31, pad_x + 216, r1_y + 31], radius=31, fill=(242, 64, 98, 255))
    sp_pin = get_text_sprite("ĐỊA CHỈ", FONT_BUBBLE, 26, COL_CREAM_5, outer_w=0, inner_w=2, shadow_alpha=0)
    paste_centered(card, sp_pin, pad_x + 137, r1_y)

    sp_addr = get_text_sprite("38 Nguyễn Đình Chiểu • Nha Trang", FONT_BUBBLE, 38, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=7, inner_stroke=(72, 20, 32), inner_w=3, shadow_alpha=0)
    paste_centered(card, sp_addr, pad_x + 562, r1_y, scale=min(1.0, 650.0 / max(1.0, sp_addr.width)))

    # Row 2: Two adorable side-by-side Candy Pills (Mint Hours + Honey-Gold Hotline!)
    r2_y = pad_y + 206
    # Left Mint Pill: Hours
    dr.rounded_rectangle([pad_x + 48, r2_y - 36, cx - 10, r2_y + 36], radius=36, fill=(226, 250, 238, 255), outline=(62, 192, 146, 255), width=4)
    sp_hr = get_text_sprite("10:00 – 22:00", FONT_POP, 33, [(34, 128, 92)] * 5, outer_stroke=(255, 255, 255), outer_w=6, inner_w=0, shadow_alpha=0)
    sp_hr_lbl = get_text_sprite("MỞ CỬA:", FONT_BUBBLE, 24, [(42, 142, 104)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(card, sp_hr_lbl, pad_x + 132, r2_y)
    paste_centered(card, sp_hr, pad_x + 332, r2_y, scale=min(1.0, 235.0 / max(1.0, sp_hr.width)))

    # Right Honey-Gold Pill: Hotline
    dr.rounded_rectangle([cx + 10, r2_y - 36, pad_x + cw - 48, r2_y + 36], radius=36, fill=(255, 244, 206, 255), outline=(246, 178, 54, 255), width=4)
    sp_hl_lbl = get_text_sprite("HOTLINE:", FONT_BUBBLE, 24, [(188, 92, 24)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    sp_hl = get_text_sprite("0979 233 139", FONT_POP, 33, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=6, inner_stroke=(82, 22, 32), inner_w=2, shadow_alpha=0)
    paste_centered(card, sp_hl_lbl, cx + 92, r2_y)
    paste_centered(card, sp_hl, cx + 292, r2_y, scale=min(1.0, 240.0 / max(1.0, sp_hl.width)))

    # Sparkles & cute hearts on corners
    draw_four_star(dr, pad_x + 28, pad_y + 34, 16, (255, 226, 88, 255))
    draw_four_star(dr, pad_x + cw - 28, pad_y + 34, 16, (255, 226, 88, 255))
    return card

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv

    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v5.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    total_frames = tm["total_frames"]
    cap_groups = build_caption_groups(tm["words"])

    print("Loading V5 User-Color-Graded & User-Keyed Clips + Kawaii Teachers 20/11 Animation...", flush=True)
    # 100% User-Color-Graded & User-Keyed clips from CapCut V4 project (DO NOT apply polish_sunny_frame to these!)
    v_s1          = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s1_skit.mp4"), W, H)
    v_s2          = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s2_table.mp4"), W, H)
    v_s3_c1381    = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s3_c1381.mp4"), W, H)
    v_s3_c1385    = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s3_c1385.mp4"), W, H)
    v_jar_shake   = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s4_jar_shake.mp4"), W, H)
    v_jar_draw    = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s4_jar_draw.mp4"), W, H)
    v_s5a_khang   = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s5a_khang.mp4"), W, H)
    m_s5a_gray    = load_all_frames_gray(os.path.join(AROLL_DIR, "v5_cc_s5a_matte.mp4"), W, H)
    v_s5b_c1395   = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s5b_c1395.mp4"), W, H)
    v_s5b_0327    = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s5b_0327.mp4"), W, H)
    v_s5b_0339    = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s5b_0339.mp4"), W, H)
    v_s5c_khang   = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s5c_khang.mp4"), W, H)
    m_s5c_gray    = load_all_frames_gray(os.path.join(AROLL_DIR, "v5_cc_s5c_matte.mp4"), W, H)
    v_s6a_6494    = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s6a_6494.mp4"), W, H)
    v_s6a_6495    = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s6a_6495.mp4"), W, H)
    v_s6b_thumbs  = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s6b_thumbs.mp4"), W, H)
    v_s6c_front   = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s6c_storefront.mp4"), W, H)

    # Canvas animated scenes (including NEW Kawaii Cartoon Teachers & Students 20/11 Banner!)
    v_meme_pray   = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v2_meme_pray_vid.mp4"), W, H)
    v_vn_nost     = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v4_vn_nostalgia_vid.mp4"), W, H)
    v_kute_tch    = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v5_kute_teachers_2011_vid.mp4"), W, H)
    v_cs1_crowd   = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v4_cs1_crowded_static_vid.mp4"), W, H)

    ref_neon_im = Image.open(os.path.join(MEDIA_DIR, "ref_fc_bg_neon_9x16.jpg")).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    dark_neon_bg = Image.alpha_composite(
        ref_neon_im.filter(ImageFilter.GaussianBlur(radius=14)).convert("RGBA"),
        Image.new("RGBA", (W, H), (22, 12, 18, 128))
    )

    stickers = load_stickers()
    logo_clean = stickers["logo_fc"].copy()
    logo_clean.thumbnail((260, 260), Image.Resampling.LANCZOS)
    header_2011    = build_clean_modern_2011_header(logo_clean)
    kute_addr_card = build_ultra_kute_storefront_card()

    quiz_stack_specs = [
        (3.32, "LỊCH SỬ #01",        "Ngày Nhà giáo Việt Nam là ngày nào?",          "Đáp án: 20/11",         (44, 182, 142), 1535, -3.0),
        (3.70, "NGỮ VĂN #41",         "Ai là tác giả tác phẩm Lão Hạc?",              "Đáp án: Nam Cao",       (242, 136, 48), 1270, +2.6),
        (4.08, "ĐỊA LÝ #18",          "Đường nào ở Nha Trang có Feel Chicken ngon?",  "38 Nguyễn Đình Chiểu!", (56, 152, 232), 1005, -2.4),
        (4.46, "TOÁN HỌC #55",        "1 + 1 bằng mấy khi đi ăn cùng hội bạn thân?",  "Gấp đôi niềm vui!",     (168, 92, 232),  740, +2.8),
        (4.84, "HÓA HỌC VUI #72",     "Chất gì làm gà rán Feel Chicken gây nghiện?",   "Sốt Hàn Quốc!",         (236, 78, 138),  475, -2.0),
        (5.22, "ĐỐ MẸO LẮT LÉO #100", "Gà 1 chân nặng 2kg, đứng 2 chân mấy kg?",      "Vẫn 2 kg nha!!",        (232, 42, 68),  1015, +1.5),
    ]
    quiz_card_sprites = [
        (off, make_stacking_quiz_card(tg, tx, an, col, qw=966 if idx == 5 else 936, qh=248 if idx == 5 else 218), cy, ang)
        for idx, (off, tg, tx, an, col, cy, ang) in enumerate(quiz_stack_specs)
    ]

    test_times = [
        1.46,   # S1: CapCut-graded C3938 slap
        5.30,   # S2: CapCut-graded C3942 centered Khang
        12.75,  # S2C: Emotional Vietnamese students nostalgia
        14.60,  # NEW IMAGE 2 FIX: Adorable Kawaii Cartoon Teachers & Students 20/11 Animation Banner!
        17.30,  # S3A: User-graded & user-keyed C1385 tokbokki
        23.00,  # S4A: User-graded Jar Shake
        24.85,  # S4B: User-graded Jar Draw
        29.15,  # S5A: User-graded & user-keyed C3956 + CÓ QUÀ!!
        34.40,  # S5C: User-graded & user-keyed C3956 + Behind-head animated 3D text!
        41.80,  # S6A: User-graded IMG_6495 crispy bite + jumping texts!
        43.60,  # S6B: User-graded & user-keyed C3957 thumbs up!
        47.20,  # NEW IMAGE 3 FIX: User-graded & user-keyed 3.90s CS1 Storefront + ULTRA-KUTE Kawaii Address Card!
    ]
    test_fset = {min(total_frames - 1, int(round(ts * FPS))) for ts in test_times}
    test_saved = []

    raw_vid_out = os.path.join(PROJ_DIR, "_fc_kute_v5_video_only.mp4")
    writer = None
    if not test_mode:
        writer = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            raw_vid_out
        ], stdin=subprocess.PIPE)

    for fi in range(total_frames):
        if test_mode and fi not in test_fset:
            continue

        t = fi / FPS
        show_captions = True
        cap_y_base = 1525

        # ======================================================================
        # SCENE 1: USER-GRADED C3938 — TABLE SLAP + THÀNH ZOOM (0.00..4.57s)
        # ======================================================================
        if fi < segs["s1_skit"]["f1"]:
            lf = min(len(v_s1) - 1, fi - segs["s1_skit"]["f0"])
            rgb = v_s1[lf]
            show_captions = False

            if t < 1.41:
                comp_im = fit_cover_target(rgb, W, H, zoom=1.02, cx_px=520, cy_px=960).convert("RGBA")
            elif t < 3.06:
                dt_slap = t - 1.41
                z_punch = step_zoom(t, 1.02, [(1.41, 1.16, 0.12)])
                decay = math.exp(-dt_slap * 12.0)
                sh_x = math.sin(dt_slap * 96.0) * 24.0 * decay
                sh_y = math.cos(dt_slap * 118.0) * 18.0 * decay
                comp_im = fit_cover_target(rgb, W, H, zoom=z_punch, cx_px=575, cy_px=920, shake_xy=(sh_x, sh_y)).convert("RGBA")

                if dt_slap < 0.12:
                    fl_a = int(65 * (1.0 - dt_slap / 0.12))
                    comp_im = Image.alpha_composite(comp_im, Image.new("RGBA", (W, H), (255, 245, 220, fl_a)))

                env_ram = smooth_env(t, 1.41, 2.02, 0.05, 0.18)
                if env_ram > 0.01:
                    u_r = ease_out_back(min(1.0, dt_slap / 0.18), s=1.45)
                    draw_spiky_impact_badge(comp_im, "RẦM!!", 695, 1115, scale=0.75 + 0.28 * u_r, opacity=env_ram)
                    draw_confetti_burst(comp_im, 695, 1060, t, 1.42, 120)
            else:
                dt_z = t - 3.06
                s1_end = segs["s1_skit"]["t1"]
                if dt_z < 0.30:
                    uz = ease_out_cubic(dt_z / 0.30)
                    z_th  = 1.16 + (1.98 - 1.16) * uz
                    cx_th = 575.0 + (808.0 - 575.0) * uz
                    cy_th = 920.0 + (895.0 - 920.0) * uz
                    ang_th = 1.8 * uz
                else:
                    uz2 = smoothstep((dt_z - 0.30) / max(0.2, (s1_end - 3.36)))
                    z_th = 1.98 + (2.15 - 1.98) * uz2
                    cx_th, cy_th, ang_th = 808.0, 895.0, 1.8
                comp_im = fit_cover_target(rgb, W, H, zoom=z_th, cx_px=cx_th, cy_px=cy_th, angle_deg=ang_th).convert("RGBA")

                for qi, (qt0, qx, qy, qang) in enumerate([
                    (3.14, 355, 425, -14.0),
                    (3.26, 540, 365,   2.0),
                    (3.38, 725, 425,  14.0),
                ]):
                    if t >= qt0:
                        uq = ease_out_back(min(1.0, (t - qt0) / 0.20), s=1.35)
                        wob = math.sin(t * 7.5 + qi * 1.8) * 6.0
                        sp_q = get_text_sprite("?", FONT_POP, 88 if qi == 1 else 74, COL_GOLD_5 if qi == 1 else COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(48, 18, 24), inner_w=4)
                        paste_centered(comp_im, sp_q, qx, qy + math.sin(t * 5.0 + qi) * 6.0, scale=0.75 + 0.25 * uq, opacity=min(1.0, (s1_end - t) / 0.14), angle=qang + wob)

                env_b2 = smooth_env(t, 3.72, s1_end - 0.03, 0.14, 0.12)
                if env_b2 > 0.01:
                    ub2 = ease_out_back(min(1.0, (t - 3.72) / 0.20))
                    jx = math.sin(t * 48.0) * 4.5
                    sw_w, sw_h = 540, 124
                    sbub = Image.new("RGBA", (sw_w + 24, sw_h + 24), (0, 0, 0, 0))
                    sd = ImageDraw.Draw(sbub)
                    sd.rounded_rectangle([6, 6, 18 + sw_w, 18 + sw_h], radius=48, fill=(255, 255, 255, 255))
                    sd.rounded_rectangle([12, 12, 12 + sw_w, 12 + sw_h], radius=42, fill=(32, 44, 66, 244), outline=(102, 206, 255, 255), width=5)
                    sp_em = get_text_sprite("Em... em... ơ kìa?!", FONT_BUBBLE, 46, COL_MINT_5, outer_stroke=(24, 32, 48), outer_w=6, inner_w=3)
                    paste_centered(sbub, sp_em, (sw_w + 24) // 2, (sw_h + 24) // 2, scale=min(1.0, (sw_w - 28) / max(1.0, sp_em.width)))
                    paste_centered(comp_im, sbub, 540 + jx, 1515, scale=0.84 + 0.16 * ub2, opacity=env_b2)

            env_hdr = smooth_env(t, 0.10, 3.02, 0.18, 0.14)
            if env_hdr > 0.01:
                draw_pill_banner(comp_im, "LỚP HỌC FEEL CHICKEN • 20/11", 540, 102, (232, 48, 72), COL_GOLD_5, fsz=29, scale=0.92 + 0.08 * env_hdr, opacity=env_hdr)

            env_b1 = smooth_env(t, 1.40, 3.04, 0.14, 0.14)
            if env_b1 > 0.01:
                ub1 = ease_out_back(min(1.0, (t - 1.40) / 0.24))
                bw, bh = 840, 196
                bub = Image.new("RGBA", (bw + 32, bh + 48), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bub)
                bd.rounded_rectangle([12, 12, 20 + bw, 20 + bh], radius=50, fill=(255, 255, 255, 255))
                bd.rounded_rectangle([18, 18, 14 + bw, 14 + bh], radius=44, fill=(255, 249, 238, 252), outline=(238, 56, 82, 255), width=6)
                bd.polygon([(250, 14 + bh), (305, 14 + bh), (235, 42 + bh)], fill=(255, 249, 238, 255), outline=(238, 56, 82, 255))
                sp_k1 = get_text_sprite("THÀNH ƠI!!", FONT_BUBBLE, 50, COL_CORAL_5, outer_w=8, inner_w=4)
                sp_k2 = get_text_sprite("LÊN BẢNG KIỂM TRA MIỆNG!", FONT_POP, 46, COL_GOLD_5, outer_w=8, inner_w=4, sheen_prog=(t - 1.5) * 0.8)
                paste_centered(bub, sp_k1, (bw + 32) // 2, 68)
                paste_centered(bub, sp_k2, (bw + 32) // 2, 142, scale=min(1.0, (bw - 44) / max(1.0, sp_k2.width)))
                paste_centered(comp_im, bub, 540, 312, scale=0.82 + 0.18 * ub1, opacity=env_b1, angle=-1.2)

        # ======================================================================
        # SCENE 2: USER-GRADED C3942 -> POV PRAYING -> VIETNAMESE STUDENTS NOSTALGIA (4.57..13.47s)
        # ======================================================================
        elif fi < segs["s2_table"]["f1"]:
            s2_t0 = segs["s2_table"]["t0"]
            lf = min(len(v_s2) - 1, fi - segs["s2_table"]["f0"])
            rgb_k = v_s2[lf]

            t_pov_in  = s2_t0 + 1.53
            t_pov_out = s2_t0 + 4.91
            t_nost_in = s2_t0 + 6.95

            if t < t_pov_in:
                z_k = step_zoom(t, 1.12, [(s2_t0 + 0.80, 1.18, 0.18)])
                comp_im = fit_cover_target(rgb_k, W, H, zoom=z_k, cx_px=594, cy_px=1120).convert("RGBA")
                cap_y_base = 1560

            elif t < t_pov_out:
                dt_m = t - t_pov_in
                idx_m = int(dt_m * FPS) % len(v_meme_pray)
                rgb_m = polish_sunny_frame(v_meme_pray[idx_m])
                z_m = step_zoom(t, 1.01, [(s2_t0 + 3.48, 1.12, 0.18)])
                sh_r = (math.sin(t * 62.0) * 5.0, 0.0) if t >= (s2_t0 + 4.20) else (0.0, 0.0)
                comp_im = fit_cover_target(rgb_m, W, H, zoom=z_m, cx_px=540, cy_px=960, shake_xy=sh_r).convert("RGBA")
                show_captions = False

                top_g = np.zeros((H, W, 4), dtype=np.uint8)
                yg = np.clip(1.0 - np.arange(H, dtype=np.float32) / 470.0, 0.0, 1.0)
                top_g[:, :, 3] = (yg * 108.0).astype(np.uint8)[:, None]
                comp_im = Image.alpha_composite(comp_im, Image.fromarray(top_g, "RGBA"))

                draw_tiktok_pov_text(comp_im, [
                    "POV: Cô giáo kiểm tra miệng đến",
                    "đứa thứ 5 rồi vẫn chưa có dấu",
                    "hiệu dừng lại",
                ], cy_top=170, opacity=smooth_env(t, t_pov_in + 0.04, t_pov_out - 0.04, 0.14, 0.14))

                t_ktm1 = s2_t0 + 3.48
                t_rung = s2_t0 + 4.20
                if t < t_ktm1:
                    sp_s = get_text_sprite("Hồi xưa đi học nghe đến chữ...", FONT_BUBBLE, 48, COL_CREAM_5, outer_stroke=(32, 14, 18), outer_w=8, inner_w=4)
                    paste_centered(comp_im, sp_s, 540, 1600, scale=min(1.0, 960.0 / max(1.0, sp_s.width)))
                else:
                    dt_k1 = t - t_ktm1
                    uk1 = ease_out_back(min(1.0, dt_k1 / 0.22), s=1.34)
                    sp_ktm1 = get_text_sprite(
                        "KIỂM TRA MIỆNG", FONT_POP, 96, COL_GOLD_5,
                        outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(54, 18, 24), inner_w=5,
                        glow_col=(255, 206, 68), glow_rad=12, sheen_prog=dt_k1 * 0.85
                    )
                    paste_centered(comp_im, sp_ktm1, 540, 1485, scale=min(1.0, 990.0 / max(1.0, sp_ktm1.width)) * (0.82 + 0.18 * uk1))
                    if t >= t_rung:
                        ur = ease_out_back(min(1.0, (t - t_rung) / 0.18), s=1.38)
                        sp_rung = get_text_sprite(
                            "RUNG CẦM CẬP!!", FONT_BUBBLE, 76, COL_CORAL_5,
                            outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(54, 18, 24), inner_w=4
                        )
                        paste_centered(comp_im, sp_rung, 540 + math.sin(t * 64.0) * 6.0, 1640, scale=0.84 + 0.16 * ur)

            else:
                t_ktm2 = s2_t0 + 6.90
                t_bh_w = s2_t0 + 7.68
                khang_im = fit_cover_target(rgb_k, W, H, zoom=1.12, cx_px=594, cy_px=1120).convert("RGBA")

                if t >= t_nost_in:
                    u_mem = smoothstep(min(1.0, (t - t_nost_in) / 0.28))
                    idx_vn = int((t - t_nost_in) * FPS) % len(v_vn_nost)
                    mem_im = fit_cover_target(polish_sunny_frame(v_vn_nost[idx_vn]), W, H, zoom=1.01, cx_px=540, cy_px=960).convert("RGBA")
                    mem_im = Image.alpha_composite(mem_im, Image.new("RGBA", (W, H), (255, 226, 175, 26)))
                    comp_im = Image.blend(khang_im, mem_im, u_mem)
                    draw_pill_banner(comp_im, "KÝ ỨC HỌC TRÒ BỒI HỒI 20/11", 540, 138, (238, 126, 52), COL_CREAM_5, fsz=29, opacity=u_mem)
                else:
                    comp_im = khang_im

                if t < t_ktm2:
                    cap_y_base = 1565
                else:
                    show_captions = False
                    dt_k2 = t - t_ktm2
                    uk2 = ease_out_back(min(1.0, dt_k2 / 0.22), s=1.32)
                    sp_ktm2 = get_text_sprite(
                        "KIỂM TRA MIỆNG", FONT_POP, 90, COL_GOLD_5,
                        outer_stroke=(255, 255, 255), outer_w=12, inner_stroke=(54, 18, 24), inner_w=5,
                        glow_col=(255, 206, 68), glow_rad=10, sheen_prog=dt_k2 * 0.75
                    )
                    paste_centered(comp_im, sp_ktm2, 540, 1525, scale=min(1.0, 960.0 / max(1.0, sp_ktm2.width)) * (0.84 + 0.16 * uk2))
                    if t >= t_bh_w:
                        ubh = ease_out_back(min(1.0, (t - t_bh_w) / 0.22))
                        sp_bh = get_text_sprite("thấy BỒI HỒI GHÊ luôn á!", FONT_BUBBLE, 58, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(54, 18, 24), inner_w=4)
                        paste_centered(comp_im, sp_bh, 540, 1665, scale=min(1.0, 950.0 / max(1.0, sp_bh.width)) * (0.85 + 0.15 * ubh))

        # ======================================================================
        # SCENE 3: NEW KAWAII CARTOON TEACHERS & STUDENTS 20/11 BANNER [IMAGE 2 FIX] + USER-GRADED CS1 FOOD + FIREWORKS CHALKBOARD (13.47..21.97s)
        # ======================================================================
        elif fi < segs["s3_program"]["f1"]:
            s3_t0 = segs["s3_program"]["t0"]
            t_board = s3_t0 + 4.68

            if t < t_board:
                dt_3a = t - s3_t0
                if dt_3a < 2.34:
                    # NEW IMAGE 2 FIX: Adorable Kawaii Cartoon Vietnamese Teachers & Students 20/11 Animation Banner!
                    idx_t = int(dt_3a * FPS) % len(v_kute_tch)
                    comp_im = fit_cover_target(v_kute_tch[idx_t], W, H, zoom=1.10, cx_px=540, cy_px=965).convert("RGBA")
                    # Cute floating Kawaii hearts & stars around the cartoon teachers!
                    ov_k = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    dk = ImageDraw.Draw(ov_k)
                    for hi, (hx, hy0, hsz) in enumerate([(125, 520, 16), (955, 495, 18), (155, 1380, 15), (925, 1360, 17)]):
                        hy = hy0 + math.sin(t * 3.6 + hi * 1.4) * 18.0
                        draw_kawaii_heart(dk, hx, hy, hsz, (255, 122, 156, 225), outline_rgba=(255, 255, 255, 240))
                    comp_im.alpha_composite(ov_k)
                elif dt_3a < 3.51:
                    idx_b = min(len(v_s3_c1381) - 1, int((dt_3a - 2.34) * FPS))
                    comp_im = Image.fromarray(v_s3_c1381[idx_b], "RGB").convert("RGBA")
                else:
                    # User-graded AND user-keyed C1385 (sc=1.0446, tr=(0, -0.0444))!
                    idx_b = min(len(v_s3_c1385) - 1, int((dt_3a - 3.51) * FPS))
                    comp_im = Image.fromarray(v_s3_c1385[idx_b], "RGB").convert("RGBA")

                u_h = ease_out_back(min(1.0, dt_3a / 0.32), s=1.22)
                paste_centered(comp_im, header_2011, 540, 215, scale=0.86 + 0.14 * u_h)
                cap_y_base = 1605
            else:
                dt_c = t - t_board
                comp_im = dark_neon_bg.copy()
                show_captions = False

                draw_firework_explosion(comp_im, 215, 310, t, t_board + 0.12, radius_max=260, main_col=(255, 218, 68), alt_col=(255, 92, 132))
                draw_firework_explosion(comp_im, 865, 285, t, t_board + 0.34, radius_max=275, main_col=(88, 238, 192), alt_col=(255, 214, 72))
                draw_firework_explosion(comp_im, 540, 215, t, t_board + 0.72, radius_max=300, main_col=(255, 112, 148), alt_col=(110, 205, 255))
                draw_firework_explosion(comp_im, 235, 1520, t, t_board + 1.25, radius_max=240, main_col=(255, 218, 68), alt_col=(88, 238, 192))
                draw_firework_explosion(comp_im, 855, 1500, t, t_board + 1.65, radius_max=250, main_col=(255, 96, 128), alt_col=(255, 224, 88))
                draw_firework_explosion(comp_im, 540, 260, t, t_board + 2.25, radius_max=290, main_col=(255, 218, 68), alt_col=(255, 92, 132))

                u_c = ease_out_back(min(1.0, dt_c / 0.34), s=1.28)
                bw, bh = 984, 720
                board = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
                sh = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rounded_rectangle([20, 28, 20 + bw, 28 + bh], radius=64, fill=(10, 6, 10, 145))
                board = Image.alpha_composite(board, sh.filter(ImageFilter.GaussianBlur(radius=14)))
                bd = ImageDraw.Draw(board)
                bd.rounded_rectangle([10, 10, 30 + bw, 30 + bh], radius=68, fill=(255, 255, 255, 255))
                bd.rounded_rectangle([20, 20, 20 + bw, 20 + bh], radius=58, fill=(242, 168, 96, 255))
                bd.rounded_rectangle([38, 38, 2 + bw, 2 + bh], radius=44, fill=(26, 88, 64, 255), outline=(255, 245, 215, 205), width=3)
                bd.rounded_rectangle([68, 175, bw - 28, 365], radius=36, fill=(18, 64, 46, 255), outline=(255, 216, 84, 250), width=5)

                cx_b = (bw + 40) // 2
                sp_sub0 = get_text_sprite("★ MINIGAME ĐẶC BIỆT NGÀY 20/11 ★", FONT_SANS_XB, 30, COL_MINT_5, outer_w=0, inner_w=3)
                sp_main = get_text_sprite("KIỂM TRA MIỆNG", FONT_POP, 100, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(58, 24, 18), inner_w=5, glow_col=(255, 212, 75), glow_rad=14, sheen_prog=dt_c * 0.65)
                sp_sub1 = get_text_sprite("TRẢ LỜI ĐÚNG", FONT_BUBBLE, 66, COL_CREAM_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(236, 48, 76), inner_w=4)
                sp_sub2 = get_text_sprite("NHẬN QUÀ NGAY!", FONT_POP, 74, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(68, 18, 28), inner_w=4, sheen_prog=(dt_c - 0.35) * 0.75)

                paste_centered(board, sp_sub0, cx_b, 116)
                paste_centered(board, sp_main, cx_b, 270, scale=min(1.0, (bw - 120) / max(1.0, sp_main.width)))
                paste_centered(board, sp_sub1, cx_b, 462)
                paste_centered(board, sp_sub2, cx_b, 592, scale=min(1.0, (bw - 90) / max(1.0, sp_sub2.width)))

                paste_centered(comp_im, board, 540, 945, scale=0.84 + 0.16 * u_c)
                cloud_m = Image.new("RGBA", (290, 290), (0, 0, 0, 0))
                ImageDraw.Draw(cloud_m).ellipse([26, 26, 264, 264], fill=(255, 252, 244, 255), outline=(242, 168, 96, 255), width=6)
                paste_centered(cloud_m, logo_clean, 145, 145, scale=0.90)
                paste_centered(comp_im, cloud_m, 540, 530, scale=0.84 + 0.16 * u_c)

        # ======================================================================
        # SCENE 4: USER-GRADED QUESTION-JAR SOURCES + 6 QUIZ CARDS BURSTING OUT! (21.97..27.93s)
        # ======================================================================
        elif fi < segs["s4_questions"]["f1"]:
            s4_t0 = segs["s4_questions"]["t0"]
            s4_t1 = segs["s4_questions"]["t1"]
            dt_4 = t - s4_t0

            if dt_4 < 2.13:
                idx_js = min(len(v_jar_shake) - 1, int(dt_4 * FPS))
                comp_im = fit_cover_target(v_jar_shake[idx_js], W, H, zoom=1.01, cx_px=540, cy_px=960).convert("RGBA")
                draw_pill_banner(comp_im, "HŨ BỐC THĂM CÂU HỎI 20/11", 540, 118, (232, 42, 68), COL_GOLD_5, fsz=30)
            else:
                dt_draw = dt_4 - 2.13
                idx_jd = min(len(v_jar_draw) - 1, int(dt_draw * FPS))
                comp_im = fit_cover_target(v_jar_draw[idx_jd], W, H, zoom=1.08, cx_px=480, cy_px=980).convert("RGBA")
                draw_pill_banner(comp_im, "100 CÂU HỎI HỌC ĐƯỜNG & ĐỐ MẸO", 540, 118, (232, 42, 68), COL_GOLD_5, fsz=29)

            out_f4 = smoothstep((s4_t1 - t) / 0.16) if (s4_t1 - t) < 0.16 else 1.0
            for q_off, q_spr, q_cy, q_ang in quiz_card_sprites:
                if dt_4 >= q_off:
                    dq = dt_4 - q_off
                    uq = ease_out_back(min(1.0, dq / 0.22), s=1.34)
                    pop_y = q_cy + (1.0 - min(1.0, uq)) * 140.0
                    paste_centered(comp_im, q_spr, 540, pop_y, scale=0.78 + 0.22 * uq, opacity=min(1.0, dq / 0.09) * out_f4, angle=q_ang)
                    draw_confetti_burst(comp_im, 540, q_cy, dt_4, q_off + 0.03, 110)

            cap_y_base = 1725

        # ======================================================================
        # SCENE 5: USER-GRADED & USER-KEYED C3956 + BEHIND-HEAD ANIMATED TEXT + USER-GRADED CS1 FOOD (27.93..36.83s)
        # ======================================================================
        elif fi < segs["s5_gifts"]["f1"]:
            s5_t0 = segs["s5_gifts"]["t0"]
            t_co_qua   = s5_t0 + 0.88
            t_food_in  = s5_t0 + 1.56
            t_food_out = s5_t0 + 4.92
            t_2011_hit = s5_t0 + 7.72

            if t < t_food_in:
                # Seg 07: User-graded & user-keyed (sc=1.1099, tr=(-0.1099, 0))!
                lf_a = min(len(v_s5a_khang) - 1, fi - segs["s5_gifts"]["f0"])
                z_5a = step_zoom(t, 1.00, [(t_co_qua, 1.07, 0.16)])
                bg_im  = fit_cover_target(v_s5a_khang[lf_a], W, H, zoom=z_5a, cx_px=540, cy_px=960)
                fg_msk = fit_cover_gray(m_s5a_gray[min(len(m_s5a_gray) - 1, lf_a)], W, H, zoom=z_5a, cx_px=540, cy_px=960).filter(ImageFilter.GaussianBlur(radius=1.2))

                bg_soft = bg_im.filter(ImageFilter.GaussianBlur(radius=3.2)).convert("RGBA")
                bg_soft = Image.alpha_composite(bg_soft, DIM_WALL_IM)
                bg_soft = Image.alpha_composite(bg_soft, GLOW_HALO_IM)
                draw_behind_head_orbital_overlay(bg_soft, t, cx=540, cy=695, env=1.0)

                sp_bh0 = get_text_sprite("SĂN QUÀ CỰC ĐỈNH", FONT_POP, 88, COL_MINT_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(36, 18, 24), inner_w=5, sheen_prog=(t - s5_t0) * 0.9)
                paste_centered(bg_soft, sp_bh0, 540, 415, scale=min(1.0, 960.0 / max(1.0, sp_bh0.width)))

                comp_im = Image.composite(bg_im.convert("RGBA"), bg_soft, fg_msk)
                show_captions = False

                if t < t_co_qua:
                    sp_tld = get_text_sprite("Trả lời đúng...", FONT_BUBBLE, 62, COL_CREAM_5, outer_stroke=(36, 14, 20), outer_w=9, inner_w=4)
                    paste_centered(comp_im, sp_tld, 540, 1520)
                else:
                    dcq = t - t_co_qua
                    ucq = ease_out_back(min(1.0, dcq / 0.18), s=1.45)
                    sp_cq = get_text_sprite(
                        "CÓ QUÀ!!", FONT_POP, 122, COL_GOLD_5,
                        outer_stroke=(255, 255, 255), outer_w=15, inner_stroke=(196, 24, 52), inner_w=6,
                        glow_col=(255, 212, 68), glow_rad=15, sheen_prog=dcq * 1.05
                    )
                    paste_centered(comp_im, sp_cq, 540, 1520, scale=0.80 + 0.20 * ucq)
                    b_gf = get_sticker_badge(stickers, "FC_st_gift_chicken", 180, (255, 102, 128))
                    paste_centered(comp_im, b_gf, 865, 1300, scale=0.78 + 0.22 * ucq, angle=8.0)
                    draw_confetti_burst(comp_im, 540, 1440, t, t_co_qua + 0.04, 145)

            elif t < t_food_out:
                # Seg 08, 09, 10: User-graded CS1 close-up food shots!
                dt_f = t - t_food_in
                if dt_f < 1.12:
                    idx_f = min(len(v_s5b_c1395) - 1, int(dt_f * FPS))
                    comp_im = fit_cover_target(v_s5b_c1395[idx_f], W, H, zoom=1.02, cx_px=540, cy_px=960).convert("RGBA")
                    draw_bouncy_callout_pill(comp_im, "8 MIẾNG GÀ ĐẪM SỐT!!", 540, 1365, (226, 38, 66), COL_GOLD_5, t, t_food_in + 0.05, fsz=44, base_ang=-2.0)
                elif dt_f < 2.24:
                    idx_f = min(len(v_s5b_0327) - 1, int((dt_f - 1.12) * FPS))
                    comp_im = fit_cover_target(v_s5b_0327[idx_f], W, H, zoom=1.02, cx_px=540, cy_px=960).convert("RGBA")
                    draw_bouncy_callout_pill(comp_im, "GÀ SỐT HÀN QUỐC CỰC NGON!!", 540, 1365, (238, 118, 38), COL_CREAM_5, t, t_food_in + 1.16, fsz=42, base_ang=+2.0)
                else:
                    idx_f = min(len(v_s5b_0339) - 1, int((dt_f - 2.24) * FPS))
                    comp_im = fit_cover_target(v_s5b_0339[idx_f], W, H, zoom=1.02, cx_px=540, cy_px=960).convert("RGBA")
                    draw_bouncy_callout_pill(comp_im, "TOKBOKKI • SALAD • KHOAI CHIÊN!", 540, 1365, (42, 168, 128), COL_GOLD_5, t, t_food_in + 2.28, fsz=40, base_ang=-1.8)

                draw_pill_banner(comp_im, "TOÀN QUÀ NGON TẠI CƠ SỞ 1!", 540, 122, (228, 38, 64), COL_GOLD_5, fsz=30)
                cap_y_base = 1565

            else:
                # Seg 11: User-graded & user-keyed (sc=1.0747, tr=(-0.0769, 0)) + Behind-Head Animated Text!
                dt_5c = t - t_food_out
                lf_c  = min(len(v_s5c_khang) - 1, max(0, int(round(dt_5c * FPS))))
                z_5b  = step_zoom(t, 1.00, [(t_2011_hit, 1.07, 0.18)])
                bg_im  = fit_cover_target(v_s5c_khang[lf_c], W, H, zoom=z_5b, cx_px=540, cy_px=960)
                fg_msk = fit_cover_gray(m_s5c_gray[min(len(m_s5c_gray) - 1, lf_c)], W, H, zoom=z_5b, cx_px=540, cy_px=960).filter(ImageFilter.GaussianBlur(radius=1.2))

                bg_layer = bg_im.filter(ImageFilter.GaussianBlur(radius=3.5)).convert("RGBA")
                bg_layer = Image.alpha_composite(bg_layer, DIM_WALL_IM)
                bg_layer = Image.alpha_composite(bg_layer, GLOW_HALO_IM)
                draw_behind_head_orbital_overlay(bg_layer, t, cx=540, cy=710, env=1.0)

                bob_l = math.sin(t * 3.8) * 14.0
                bob_r = math.cos(t * 3.8) * 14.0
                b_l = get_sticker_badge(stickers, "FC_st_prof_chick", 172, (255, 198, 68))
                b_r = get_sticker_badge(stickers, "FC_st_score10", 172, (255, 108, 138))
                paste_centered(bg_layer, b_l, 185, 690 + bob_l, angle=-8.0 + math.sin(t * 2.5) * 4.0)
                paste_centered(bg_layer, b_r, 895, 690 + bob_r, angle=+8.0 - math.sin(t * 2.5) * 4.0)

                if t < t_2011_hit:
                    u_in = ease_out_back(min(1.0, dt_5c / 0.28), s=1.28)
                    sp_t1 = get_text_sprite("AI ĐẾN QUÁN", FONT_BUBBLE, 76, COL_CREAM_5, outer_stroke=(226, 38, 66), outer_w=11, inner_stroke=(48, 14, 22), inner_w=4)
                    sp_t2 = get_text_sprite("CŨNG CÓ QUÀ!", FONT_POP, 104, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(58, 18, 26), inner_w=5, glow_col=(255, 208, 68), glow_rad=12, sheen_prog=dt_5c * 0.75)
                    paste_centered(bg_layer, sp_t1, 540, 320 + (1.0 - min(1.0, u_in)) * -40.0, scale=0.84 + 0.16 * u_in)
                    paste_centered(bg_layer, sp_t2, 540, 465, scale=min(1.0, 980.0 / max(1.0, sp_t2.width)) * (0.84 + 0.16 * u_in))
                else:
                    dt_20 = t - t_2011_hit
                    u_20 = ease_out_back(min(1.0, dt_20 / 0.22), s=1.38)
                    draw_firework_explosion(bg_layer, 250, 330, t, t_2011_hit + 0.05, radius_max=230, main_col=(255, 218, 68), alt_col=(255, 92, 132))
                    draw_firework_explosion(bg_layer, 830, 320, t, t_2011_hit + 0.18, radius_max=230, main_col=(88, 238, 192), alt_col=(255, 214, 72))
                    sp_h1 = get_text_sprite("ÁP DỤNG ĐẾN HẾT", FONT_BUBBLE, 66, COL_MINT_5, outer_stroke=(36, 16, 22), outer_w=10, inner_w=4)
                    sp_h2 = get_text_sprite("NGÀY 20/11!", FONT_POP, 116, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=14, inner_stroke=(196, 24, 52), inner_w=6, glow_col=(255, 212, 68), glow_rad=14, sheen_prog=dt_20 * 1.1)
                    paste_centered(bg_layer, sp_h1, 540, 320, scale=0.85 + 0.15 * u_20)
                    paste_centered(bg_layer, sp_h2, 540, 465, scale=min(1.0, 980.0 / max(1.0, sp_h2.width)) * (0.82 + 0.18 * u_20))

                comp_im = Image.composite(bg_im.convert("RGBA"), bg_layer, fg_msk)
                draw_pill_banner(comp_im, "38 NGUYỄN ĐÌNH CHIỂU • NHA TRANG", 540, 118, (232, 42, 68), COL_GOLD_5, fsz=28)
                cap_y_base = 1545

        # ======================================================================
        # SCENE 6A: ZERO-ZOOM CROWDED CS1 + USER-GRADED CRISPY CHICKEN BITES WITH BOUNCING TEXTS! (36.83..42.77s)
        # ======================================================================
        elif fi < segs["s6a_outro"]["f1"]:
            s6a_t0 = segs["s6a_outro"]["t0"]
            s6a_t1 = segs["s6a_outro"]["t1"]
            dt_6 = t - s6a_t0
            t_b1 = s6a_t0 + 2.72
            t_b2 = s6a_t0 + 4.32

            if t < t_b1:
                idx_w = int(dt_6 * FPS) % len(v_cs1_crowd)
                rgb_w = polish_sunny_frame(v_cs1_crowd[idx_w])
                comp_im = Image.fromarray(rgb_w, "RGB").convert("RGBA")
            elif t < t_b2:
                idx_p = min(len(v_s6a_6494) - 1, int((t - t_b1) * FPS))
                comp_im = fit_cover_target(v_s6a_6494[idx_p], W, H, zoom=1.16, cx_px=440, cy_px=960).convert("RGBA")
                draw_bouncy_callout_pill(comp_im, "XÉ ĐÙI GÀ NÓNG HỔI!!", 330, 1210, (232, 42, 68), COL_GOLD_5, t, t_b1 + 0.06, fsz=40, base_ang=-5.5)
                draw_bouncy_callout_pill(comp_im, "THƠM NỨC MŨI!!", 780, 1345, (242, 128, 42), COL_CREAM_5, t, t_b1 + 0.42, fsz=40, base_ang=+5.5)
                draw_confetti_burst(comp_im, 330, 1210, t, t_b1 + 0.08, 120)
            else:
                idx_bt = min(len(v_s6a_6495) - 1, int((t - t_b2) * FPS))
                comp_im = fit_cover_target(v_s6a_6495[idx_bt], W, H, zoom=1.01, cx_px=540, cy_px=960).convert("RGBA")

                dt_bt = t - t_b2
                u_bt = ease_out_back(min(1.0, dt_bt / 0.18), s=1.55)
                jmp_y = -abs(math.sin(dt_bt * 11.5)) * 22.0
                sp_gion = get_text_sprite(
                    "GIÒN RỤM RỤM!!", FONT_POP, 88, COL_GOLD_5,
                    outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(198, 24, 52), inner_w=5,
                    glow_col=(255, 212, 68), glow_rad=12, sheen_prog=dt_bt * 1.2
                )
                draw_bouncy_callout_pill(comp_im, "ĐẪM SỐT HÀN!!", 255, 1185, (232, 42, 68), COL_CREAM_5, t, t_b2 + 0.10, fsz=38, base_ang=-6.5)
                draw_bouncy_callout_pill(comp_im, "ĂN LÀ MÊ!!", 835, 1200, (42, 174, 132), COL_GOLD_5, t, t_b2 + 0.28, fsz=40, base_ang=+6.5)
                paste_centered(comp_im, sp_gion, 540, 1385 + jmp_y, scale=min(1.0, 960.0 / max(1.0, sp_gion.width)) * (0.78 + 0.22 * u_bt), angle=-2.5 + math.sin(dt_bt * 9.0) * 2.5)
                draw_confetti_burst(comp_im, 540, 1350, t, t_b2 + 0.05, 140)

            env_cert = smooth_env(t, s6a_t0 + 0.12, s6a_t1 - 0.08, 0.22, 0.20)
            if env_cert > 0.01:
                uc = ease_out_back(min(1.0, (t - (s6a_t0 + 0.12)) / 0.30))
                cw_c, ch_c = 956, 236
                cert = Image.new("RGBA", (cw_c + 28, ch_c + 28), (0, 0, 0, 0))
                cd = ImageDraw.Draw(cert)
                cd.rounded_rectangle([8, 8, 20 + cw_c, 20 + ch_c], radius=46, fill=(255, 255, 255, 255))
                cd.rounded_rectangle([15, 15, 13 + cw_c, 13 + ch_c], radius=40, fill=(255, 249, 236, 248), outline=(232, 46, 74, 255), width=5)
                sp_c1 = get_text_sprite("★ DANH HIỆU CAO QUÝ 20/11 ★", FONT_SANS_XB, 23, [(224, 42, 68)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
                sp_c2 = get_text_sprite("HỌC SINH GIỎI", FONT_POP, 70, COL_GOLD_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(58, 20, 26), inner_w=4, sheen_prog=dt_6 * 0.6)
                sp_c3 = get_text_sprite("RỦ HỘI BẠN ĐẾN FEEL CHICKEN SĂN QUÀ NGAY!", FONT_SANS_XB, 23, [(58, 24, 30)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
                paste_centered(cert, sp_c1, (cw_c + 28) // 2, 54)
                paste_centered(cert, sp_c2, (cw_c + 28) // 2, 132, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c2.width)))
                paste_centered(cert, sp_c3, (cw_c + 28) // 2, 204, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c3.width)))
                paste_centered(comp_im, cert, 540, 198, scale=0.86 + 0.14 * uc, opacity=env_cert)

            cap_y_base = 1655

        # ======================================================================
        # SCENE 6B: USER-GRADED & USER-KEYED C3957 THUMBS UP! (42.77..44.57s)
        # ======================================================================
        elif fi < segs["s6b_thumbs"]["f1"]:
            s6b_t0 = segs["s6b_thumbs"]["t0"]
            lf = min(len(v_s6b_thumbs) - 1, fi - segs["s6b_thumbs"]["f0"])
            z_6b = step_zoom(t, 1.00, [(s6b_t0 + 0.95, 1.06, 0.18)])
            comp_im = fit_cover_target(v_s6b_thumbs[lf], W, H, zoom=z_6b, cx_px=540, cy_px=960).convert("RGBA")
            cap_y_base = 1560

        # ======================================================================
        # SCENE 6C: USER-GRADED & USER-KEYED 3.90s CS1 STOREFRONT + ULTRA-KUTE KAWAII END-CARD [IMAGE 3 FIX]! (44.57..48.47s)
        # ======================================================================
        else:
            s6c_t0 = segs["s6c_storefront"]["t0"]
            dt_e = t - s6c_t0
            lf = min(len(v_s6c_front) - 1, fi - segs["s6c_storefront"]["f0"])
            comp_im = Image.fromarray(v_s6c_front[lf], "RGB").convert("RGBA")
            show_captions = False

            draw_firework_explosion(comp_im, 235, 290, t, s6c_t0 + 0.12, radius_max=235, main_col=(255, 218, 68), alt_col=(255, 92, 132))
            draw_firework_explosion(comp_im, 845, 270, t, s6c_t0 + 0.34, radius_max=235, main_col=(88, 238, 192), alt_col=(255, 214, 72))
            draw_firework_explosion(comp_im, 540, 235, t, s6c_t0 + 1.85, radius_max=260, main_col=(255, 112, 148), alt_col=(255, 224, 88))

            ue = ease_out_back(min(1.0, dt_e / 0.32), s=1.28)
            paste_centered(comp_im, logo_clean, 540, 185, scale=0.84 + 0.16 * ue)
            sp_go = get_text_sprite("GHÉ FEEL CHICKEN NGAY!", FONT_POP, 66, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(196, 28, 52), inner_w=5, sheen_prog=dt_e * 0.75)
            paste_centered(comp_im, sp_go, 540, 365, scale=min(1.0, 980.0 / max(1.0, sp_go.width)) * (0.85 + 0.15 * ue))

            # ULTRA-KUTE Kawaii Cloud/Sticker Address Card + Chibi Mascots bobbing on top corners!
            card_bob = math.sin(dt_e * 4.2) * 5.0
            paste_centered(comp_im, kute_addr_card, 540, 1690 + card_bob, scale=0.84 + 0.16 * ue)

            m_left  = get_sticker_badge(stickers, "FC_st_prof_chick", 142, (255, 198, 68))
            m_right = get_sticker_badge(stickers, "FC_st_cheers_cups", 142, (255, 112, 146))
            paste_centered(comp_im, m_left,  118, 1545 + math.sin(dt_e * 5.5) * 8.0, scale=0.80 + 0.20 * ue, angle=-8.0 + math.sin(dt_e * 3.5) * 4.0)
            paste_centered(comp_im, m_right, 962, 1545 + math.cos(dt_e * 5.5) * 8.0, scale=0.80 + 0.20 * ue, angle=+8.0 - math.sin(dt_e * 3.5) * 4.0)

        # ======================================================================
        # FACE-SAFE KAWAII CAPTIONS
        # ======================================================================
        if show_captions:
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    op_g = smoothstep((g["t1"] - t) / 0.15) if (g["t1"] - t) < 0.15 else 1.0
                    y_start = cap_y_base if len(g["lines"]) >= 2 else cap_y_base + 34
                    lh = 74
                    gap = 15
                    for li, ln in enumerate(g["lines"]):
                        w_items = []
                        tot_w = 0
                        for wi, (wtxt, ws, we) in enumerate(ln):
                            is_g = wtxt in GOLD_KEYWORDS
                            is_c = wtxt in CORAL_KEYWORDS or wtxt == "rung"
                            k_sc = 1.14 if (is_g or is_c) else 1.0
                            stops = COL_GOLD_5 if is_g else (COL_CORAL_5 if is_c else COL_CREAM_5)
                            glow_c = (255, 208, 68) if is_g else ((255, 96, 126) if is_c else None)
                            fsz = 54.0 * k_sc
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
                                wy = cur_y + (1.0 - min(1.0, u_w)) * 16.0
                                wcx = cur_x + adv // 2
                                paste_centered(comp_im, sp, wcx, wy, scale=0.88 + 0.12 * u_w, opacity=op_g * min(1.0, (dt_w + 0.03) / 0.09))
                                if wtxt in POP_EMPHASIS and 0.04 <= dt_w <= 0.36:
                                    u_p = (dt_w - 0.04) / 0.32
                                    paste_centered(comp_im, sp, wcx, cur_y, scale=1.0 + 0.50 * ease_out_cubic(u_p), opacity=op_g * (1.0 - u_p) * 0.36)
                            cur_x += adv + gap
                    break

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"fc_v5_test_{len(test_saved):02d}.jpg")
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
        cols, rows = 6, 2
        tw, th = 270, 480
        grid = Image.new("RGB", (tw * cols, th * rows), (18, 16, 18))
        for i, (ts, tp) in enumerate(test_saved[:12]):
            im = Image.open(tp).resize((tw, th), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 110, 26], fill=(0, 0, 0))
            d.text((8, 6), f"t={ts:.2f}s", fill=(255, 230, 80))
            grid.paste(im, ((i % cols) * tw, (i // cols) * th))
        gp = os.path.join(CHECK_DIR, "fc_v5_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved 12-frame V5 QA grid:", gp, flush=True)
    else:
        print(f"Finished rendering {total_frames} V5 frames -> {raw_vid_out} in {time.time()-t_start:.1f}s", flush=True)

if __name__ == "__main__":
    main()
