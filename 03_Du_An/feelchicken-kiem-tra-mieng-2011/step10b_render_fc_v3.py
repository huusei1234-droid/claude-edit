import json, math, os, re, subprocess, sys, time
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

def step_zoom(t, base_z, steps):
    """Disciplined Pro-Editor Step Keyframe Zoom: holds steady, executes crisp 0.18s ease-out push-in ONLY on exact spoken keyword hits!
    steps = [(t_hit, target_z, ramp_dur), ...]"""
    cur_z = base_z
    for t_hit, z_to, ramp in steps:
        if t >= t_hit:
            u = ease_out_cubic(min(1.0, (t - t_hit) / max(0.05, ramp)))
            cur_z = cur_z + (z_to - cur_z) * u
    return cur_z

def draw_firework_explosion(canvas_im, cx, cy, t_now, t_burst, radius_max=280, main_col=(255, 216, 68), alt_col=(255, 92, 132)):
    """Festive multi-ray celebratory firework explosion with glowing sparks & trailing stars!"""
    dt = t_now - t_burst
    if dt < -0.22 or dt > 1.25:
        return
    bim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(bim)

    if dt < 0.0:
        # Rising golden rocket trail before burst!
        u_up = (dt + 0.22) / 0.22
        ry = int(cy + (1.0 - ease_out_cubic(u_up)) * 340.0)
        for k in range(6):
            ty = ry + k * 16
            al = int(220 * (1.0 - k / 6.0))
            dr.ellipse([cx - 5, ty - 5, cx + 5, ty + 5], fill=(255, 235, 130, al))
        canvas_im.alpha_composite(bim)
        return

    u = dt / 1.25
    e = ease_out_cubic(min(1.0, dt / 0.65))
    fade = smoothstep(1.0 - max(0.0, (u - 0.35) / 0.65))

    # Central warm flash on burst
    if dt < 0.22:
        fr = int(125 * (1.0 - dt / 0.22))
        fa = int(195 * (1.0 - dt / 0.22))
        dr.ellipse([cx - fr, cy - fr, cx + fr, cy + fr], fill=(255, 250, 210, fa))

    n_rays = 28
    for i in range(n_rays):
        ang = (2.0 * math.pi * i) / n_rays + (0.11 if i % 2 else 0.0)
        r_scale = 1.0 if i % 3 == 0 else (0.78 if i % 3 == 1 else 0.56)
        dist = radius_max * r_scale * e
        grav = 56.0 * (u * u)
        x1 = cx + math.cos(ang) * dist
        y1 = cy + math.sin(ang) * dist + grav
        x0 = cx + math.cos(ang) * (dist * max(0.18, u * 0.65))
        y0 = cy + math.sin(ang) * (dist * max(0.18, u * 0.65)) + grav * 0.62

        col = main_col if i % 2 == 0 else alt_col
        al = int(255 * fade)
        dr.line([(x0, y0), (x1, y1)], fill=(*col, al), width=max(3, int(7 * fade)))
        sr = max(4, int(10 * fade))
        dr.ellipse([x1 - sr - 4, y1 - sr - 4, x1 + sr + 4, y1 + sr + 4], fill=(*col, int(al * 0.62)))
        dr.ellipse([x1 - sr, y1 - sr, x1 + sr, y1 + sr], fill=(255, 255, 240, al))

    canvas_im.alpha_composite(bim)

def build_clean_modern_2011_header(logo_clean):
    """Sleek, modern Korean-commercial 20/11 Header Card (NO tacky AI flowers, compact top header so full-screen real source shines!)"""
    bw, bh = 996, 268
    card = Image.new("RGBA", (bw + 32, bh + 36), (0, 0, 0, 0))
    sh = Image.new("RGBA", (bw + 32, bh + 36), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([16, 22, 16 + bw, 22 + bh], radius=46, fill=(24, 10, 14, 110))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=9)))
    dr = ImageDraw.Draw(card)

    dr.rounded_rectangle([8, 10, 24 + bw, 26 + bh], radius=50, fill=(255, 255, 255, 255))
    dr.rounded_rectangle([15, 17, 17 + bw, 19 + bh], radius=44, fill=(222, 34, 60, 252))
    dr.rounded_rectangle([27, 68, 5 + bw, 7 + bh], radius=34, fill=(255, 251, 242, 255), outline=(255, 206, 72, 255), width=4)

    cx = (bw + 32) // 2
    sp_top = get_text_sprite("★ CHÀO MỪNG NGÀY NHÀ GIÁO VIỆT NAM ★", FONT_SANS_XB, 24, COL_GOLD_5, outer_w=0, inner_stroke=(90, 14, 24), inner_w=3, shadow_alpha=35)
    paste_centered(card, sp_top, cx, 42, scale=min(1.0, (bw - 80) / max(1.0, sp_top.width)))

    # Logo left + Giant 20/11 SẮP TỚI RỒI! right-center
    lg = logo_clean.copy()
    lg.thumbnail((156, 156), Image.Resampling.LANCZOS)
    paste_centered(card, lg, 128, 168)

    sp_main = get_text_sprite("20/11 SẮP TỚI RỒI!", FONT_POP, 72, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(58, 18, 26), inner_w=4)
    paste_centered(card, sp_main, 578, 142, scale=min(1.0, 740.0 / max(1.0, sp_main.width)))

    sp_sub = get_text_sprite("TRỞ VỀ KÝ ỨC HỌC TRÒ CÙNG FEEL CHICKEN!", FONT_SANS_XB, 25, [(36, 98, 72)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(card, sp_sub, 578, 224, scale=min(1.0, 740.0 / max(1.0, sp_sub.width)))
    return card

def make_stacking_quiz_card(q_tag, q_txt, q_ans, q_col, qw=940, qh=224):
    """Large bold playful Quiz Card designed to stack & fill the screen sequentially!"""
    qc = Image.new("RGBA", (qw + 36, qh + 36), (0, 0, 0, 0))
    sh = Image.new("RGBA", (qw + 36, qh + 36), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([18, 24, 18 + qw, 24 + qh], radius=44, fill=(22, 10, 16, 125))
    qc = Image.alpha_composite(qc, sh.filter(ImageFilter.GaussianBlur(radius=9)))
    qd = ImageDraw.Draw(qc)
    qd.rounded_rectangle([10, 10, 26 + qw, 26 + qh], radius=48, fill=(255, 255, 255, 255))
    qd.rounded_rectangle([18, 18, 18 + qw, 18 + qh], radius=42, fill=(255, 251, 244, 255), outline=(*q_col, 255), width=6)

    qd.rounded_rectangle([38, 32, 368, 82], radius=24, fill=(*q_col, 255))
    sp_tg = get_text_sprite(q_tag, FONT_SANS_XB, 24, COL_CREAM_5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(qc, sp_tg, 203, 57, scale=min(1.0, 304.0 / max(1.0, sp_tg.width)))

    qd.rounded_rectangle([650, 30, qw - 8, 84], radius=26, fill=(255, 224, 82, 255), outline=(*q_col, 255), width=3)
    sp_an = get_text_sprite(q_ans, FONT_SANS_XB, 25, [(62, 22, 26)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(qc, sp_an, (650 + qw - 8) // 2, 57, scale=min(1.0, (qw - 676) / max(1.0, sp_an.width)))

    sp_qq = get_text_sprite(q_txt, FONT_BUBBLE, 44, [(46, 20, 28)] * 5, outer_stroke=(255, 255, 255), outer_w=4, inner_w=0, shadow_alpha=0)
    paste_centered(qc, sp_qq, (qw + 36) // 2, 154, scale=min(1.0, (qw - 48) / max(1.0, sp_qq.width)))
    return qc

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv

    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v3.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    total_frames = tm["total_frames"]
    cap_groups = build_caption_groups(tm["words"])

    print("Loading V3 tight A-rolls & 100% clean Feel Chicken B-rolls...", flush=True)
    v_s1   = load_all_frames_rgb(os.path.join(AROLL_DIR, "s1_skit_v3.mp4"), W, H)
    v_s2   = load_all_frames_rgb(os.path.join(AROLL_DIR, "s2_table_v3.mp4"), W, H)
    v_s5   = load_all_frames_rgb(os.path.join(AROLL_DIR, "s5_gifts_v3.mp4"), W, H)
    v_s6b  = load_all_frames_rgb(os.path.join(AROLL_DIR, "s6b_thumbs_v3.mp4"), W, H)

    # Real Feel Chicken B-rolls (100% pure Sony/iPhone raw camera files — zero split-wipe artifacts!)
    b_luu_stu   = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_c9598_order.mp4"), W, H)
    b_c9616_tbl = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_c9616_table.mp4"), W, H)
    b_c9604_srv = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_c9604_serve.mp4"), W, H)
    b_c3490_plt = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_c3490_platter.mp4"), W, H)
    b_6494_pull = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_img6494_pull.mp4"), W, H)
    b_6495_bite = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_img6495_bite.mp4"), W, H)
    b_c3471_frt = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_c9596_front.mp4"), W, H)

    # Canvas scenes
    v_meme_pray  = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v2_meme_pray_vid.mp4"), W, H)
    v_classroom  = load_all_frames_rgb(os.path.join(MEDIA_DIR, "MUSE_fc_classroom.mp4"), 1280, 720)
    v_quiz_fcbg  = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v2_quiz_fcbg_vid.mp4"), W, H)
    v_outro_wide = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v3_outro_wide_vid.mp4"), W, H)

    ref_neon_im = Image.open(os.path.join(MEDIA_DIR, "ref_fc_bg_neon_9x16.jpg")).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    dark_neon_bg = Image.alpha_composite(
        ref_neon_im.filter(ImageFilter.GaussianBlur(radius=14)).convert("RGBA"),
        Image.new("RGBA", (W, H), (22, 12, 18, 128))
    )

    stickers = load_stickers()
    logo_clean = stickers["logo_fc"].copy()
    logo_clean.thumbnail((260, 260), Image.Resampling.LANCZOS)
    header_2011 = build_clean_modern_2011_header(logo_clean)

    # Pre-render 6 playful Quiz Cards that pop up & stack filling the screen in Scene 4!
    quiz_stack_specs = [
        (0.65, "LỊCH SỬ #01",        "Ngày Nhà giáo Việt Nam là ngày nào?",         "Đáp án: 20/11",    (44, 182, 142), 1535, -3.0),
        (1.30, "NGỮ VĂN #41",         "Ai là tác giả tác phẩm Lão Hạc?",             "Đáp án: Nam Cao",  (242, 136, 48), 1270, +2.6),
        (1.95, "ĐỊA LÝ #18",          "Thành phố biển nào có Feel Chicken siêu ngon?","Nha Trang!",      (56, 152, 232), 1005, -2.4),
        (2.60, "TOÁN HỌC #55",        "1 + 1 bằng mấy khi đi ăn cùng hội bạn thân?", "Gấp đôi niềm vui!",(168, 92, 232),  740, +2.8),
        (3.25, "HÓA HỌC VUI #72",     "Chất gì làm gà rán Feel Chicken gây nghiện?",  "Sốt Hàn Quốc!",    (236, 78, 138),  475, -2.0),
        (3.92, "ĐỐ MẸO LẮT LÉO #100", "Gà 1 chân nặng 2kg, đứng 2 chân mấy kg?",     "Vẫn 2 kg nha!!",   (232, 42, 68),  1015, +1.5),
    ]
    quiz_card_sprites = [
        (off, make_stacking_quiz_card(tg, tx, an, col, qw=966 if idx == 5 else 936, qh=248 if idx == 5 else 218), cy, ang)
        for idx, (off, tg, tx, an, col, cy, ang) in enumerate(quiz_stack_specs)
    ]

    # 12 QA test timestamps covering all 14 user notes!
    test_times = [
        1.46, 4.10,               # S1 slap & Thành zoom
        8.85, 12.80,              # S2 POV "RUNG CẦM CẬP!!" & nostalgic "BỒI HỒI"
        15.00, 17.00, 19.60,      # S3 clean big real B-roll frames + Fireworks chalkboard
        26.60,                    # S4 quiz cards stacking & filling screen
        29.15, 31.40,             # S5 standalone "CÓ QUÀ!!" + full-screen real food
        38.00, 45.60              # S6A wide natural students / crispy bite + S6C real storefront
    ]
    test_fset = {min(total_frames - 1, int(round(ts * FPS))) for ts in test_times}
    test_saved = []

    raw_vid_out = os.path.join(PROJ_DIR, "_fc_kute_v3_video_only.mp4")
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
        cap_y_base = 1520

        # ======================================================================
        # SCENE 1: OPENING SKIT — TABLE SLAP + THÀNH CLUELESS ZOOM (0.00..4.57s, TIGHT!)
        # ======================================================================
        if fi < segs["s1_skit"]["f1"]:
            lf = min(len(v_s1) - 1, fi - segs["s1_skit"]["f0"])
            rgb = polish_sunny_frame(v_s1[lf])
            show_captions = False

            if t < 1.41:
                comp_im = fit_cover_target(rgb, W, H, zoom=1.01, cx_px=540, cy_px=960).convert("RGBA")
            elif t < 3.06:
                dt_slap = t - 1.41
                z_punch = step_zoom(t, 1.01, [(1.41, 1.16, 0.12)])
                decay = math.exp(-dt_slap * 12.0)
                sh_x = math.sin(dt_slap * 96.0) * 24.0 * decay
                sh_y = math.cos(dt_slap * 118.0) * 18.0 * decay
                comp_im = fit_cover_target(rgb, W, H, zoom=z_punch, cx_px=615, cy_px=920, shake_xy=(sh_x, sh_y)).convert("RGBA")

                if dt_slap < 0.12:
                    fl_a = int(65 * (1.0 - dt_slap / 0.12))
                    comp_im = Image.alpha_composite(comp_im, Image.new("RGBA", (W, H), (255, 245, 220, fl_a)))

                env_ram = smooth_env(t, 1.41, 2.02, 0.05, 0.18)
                if env_ram > 0.01:
                    u_r = ease_out_back(min(1.0, dt_slap / 0.18), s=1.45)
                    draw_spiky_impact_badge(comp_im, "RẦM!!", 685, 1115, scale=0.75 + 0.28 * u_r, opacity=env_ram)
                    draw_confetti_burst(comp_im, 685, 1060, t, 1.42, 120)
            else:
                dt_z = t - 3.06
                s1_end = segs["s1_skit"]["t1"]
                if dt_z < 0.30:
                    uz = ease_out_cubic(dt_z / 0.30)
                    z_th = 1.16 + (1.96 - 1.16) * uz
                    cx_th = 615.0 + (808.0 - 615.0) * uz
                    cy_th = 920.0 + (895.0 - 920.0) * uz
                    ang_th = 1.8 * uz
                else:
                    uz2 = smoothstep((dt_z - 0.30) / max(0.2, (s1_end - 3.36)))
                    z_th = 1.96 + (2.16 - 1.96) * uz2
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
        # SCENE 2: KHANG -> POV PRAYING MEME ("RUNG CẦM CẬP!!") -> NOSTALGIC "BỒI HỒI" (4.57..13.47s)
        # ======================================================================
        elif fi < segs["s2_table"]["f1"]:
            s2_t0 = segs["s2_table"]["t0"]
            s2_t1 = segs["s2_table"]["t1"]
            lf = min(len(v_s2) - 1, fi - segs["s2_table"]["f0"])
            rgb_k = polish_sunny_frame(v_s2[lf])

            # Exact speech windows in s2_table (shifted by s2_t0 - 2.22):
            # 4.57..6.10s: "Có ai như Khang không?" -> Khang steady
            # 6.10..9.48s: "Hồi xưa khi mà đi học á, nghe đến chữ KIỂM TRA MIỆNG là RUNG CẦM CẬP!" -> POV Praying Classroom Video!
            # 9.48..12.30s: "Còn bây giờ á, mà nghe đến ba chữ KIỂM TRA MIỆNG..." -> Khang smiling fondly (step zoom on KIỂM TRA MIỆNG at 11.42s!)
            # 12.30..13.47s: "...là thấy BỒI HỒI GHÊ luôn á!" -> Warm sunlit nostalgic school classroom memory ("bồi hồi là lúc nhớ lại mà"!)
            t_pov_in  = s2_t0 + 1.53  # 6.10s
            t_pov_out = s2_t0 + 4.91  # 9.48s
            t_nost_in = s2_t0 + 7.68  # 12.25s

            if t < t_pov_in:
                # Steady framing, crisp keyword step push-in on "Khang" (s2_t0 + 0.80s)
                z_k = step_zoom(t, 1.01, [(s2_t0 + 0.80, 1.10, 0.18)])
                comp_im = fit_cover_target(rgb_k, W, H, zoom=z_k, cx_px=540, cy_px=1080).convert("RGBA")
                cap_y_base = 1560

            elif t < t_pov_out:
                # HILARIOUS CLASSROOM PRAYING BOYS VIDEO + POV + "KIỂM TRA MIỆNG" + "RUNG CẦM CẬP!!"
                dt_m = t - t_pov_in
                idx_m = int(dt_m * FPS) % len(v_meme_pray)
                rgb_m = polish_sunny_frame(v_meme_pray[idx_m])
                # Steady frame, then crisp step push-in right on "KIỂM TRA MIỆNG" (s2_t0 + 3.48s = 8.05s)!
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

                t_ktm1 = s2_t0 + 3.48  # 8.05s ("kiểm tra miệng")
                t_rung = s2_t0 + 4.20  # 8.77s ("rung cầm cập!")
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
                # 9.48..13.47s: PRESENT DAY FOND NOSTALGIA ("Còn bây giờ nghe đến ba chữ KIỂM TRA MIỆNG là thấy BỒI HỒI GHÊ luôn á!")
                t_ktm2 = s2_t0 + 6.90  # 11.47s ("kiểm tra miệng")
                z_k2 = step_zoom(t, 1.02, [(t_ktm2, 1.18, 0.18)])
                khang_im = fit_cover_target(rgb_k, W, H, zoom=z_k2, cx_px=540, cy_px=1120).convert("RGBA")

                if t >= t_nost_in:
                    # Cross-dissolve into warm sunlit nostalgic school classroom memory right on "thấy bồi hồi ghê luôn á!"
                    u_mem = smoothstep(min(1.0, (t - t_nost_in) / 0.26))
                    idx_cl = int((t - t_nost_in) * FPS) % len(v_classroom)
                    mem_im = fit_cover_target(polish_sunny_frame(v_classroom[idx_cl]), W, H, zoom=1.02 + 0.04 * u_mem).convert("RGBA")
                    # Warm golden nostalgia glow tint
                    mem_im = Image.alpha_composite(mem_im, Image.new("RGBA", (W, H), (255, 224, 175, 38)))
                    comp_im = Image.blend(khang_im, mem_im, u_mem)
                    draw_pill_banner(comp_im, "KÝ ỨC HỌC TRÒ BỒI HỒI 20/11", 540, 155, (238, 126, 52), COL_CREAM_5, fsz=29, opacity=u_mem)
                else:
                    comp_im = khang_im

                if t < t_ktm2:
                    cap_y_base = 1565
                else:
                    show_captions = False
                    dt_k2 = t - t_ktm2
                    uk2 = ease_out_back(min(1.0, dt_k2 / 0.22), s=1.32)
                    sp_ktm2 = get_text_sprite(
                        "KIỂM TRA MIỆNG", FONT_POP, 94, COL_GOLD_5,
                        outer_stroke=(255, 255, 255), outer_w=12, inner_stroke=(54, 18, 24), inner_w=5,
                        glow_col=(255, 206, 68), glow_rad=10, sheen_prog=dt_k2 * 0.75
                    )
                    paste_centered(comp_im, sp_ktm2, 540, 1485, scale=min(1.0, 980.0 / max(1.0, sp_ktm2.width)) * (0.84 + 0.16 * uk2))
                    if t >= t_nost_in:
                        ubh = ease_out_back(min(1.0, (t - t_nost_in) / 0.22))
                        sp_bh = get_text_sprite("thấy BỒI HỒI GHÊ luôn á!", FONT_BUBBLE, 60, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(54, 18, 24), inner_w=4)
                        paste_centered(comp_im, sp_bh, 540, 1630, scale=min(1.0, 960.0 / max(1.0, sp_bh.width)) * (0.85 + 0.15 * ubh))

        # ======================================================================
        # SCENE 3: FULL-SCREEN REAL FEEL CHICKEN + CLEAN MODERN 20/11 HEADER + FIREWORKS CHALKBOARD (13.47..21.97s)
        # ======================================================================
        elif fi < segs["s3_program"]["f1"]:
            s3_t0 = segs["s3_program"]["t0"]
            t_board = s3_t0 + 4.68  # right on "với chương trình KIỂM TRA MIỆNG..."

            if t < t_board:
                dt_3a = t - s3_t0
                # NO Khang, NO ugly AI flowers! Full-screen sharp real Feel Chicken dining room & feast table!
                if dt_3a < 2.34:
                    idx_b = min(len(b_luu_stu) - 1, int(dt_3a * FPS))
                    rgb_b = polish_sunny_frame(b_luu_stu[idx_b])
                    comp_im = fit_cover_target(rgb_b, W, H, zoom=1.01 + 0.04 * (dt_3a / 2.34)).convert("RGBA")
                else:
                    dt_b2 = dt_3a - 2.34
                    idx_b = min(len(b_c9616_tbl) - 1, int(dt_b2 * FPS))
                    rgb_b = polish_sunny_frame(b_c9616_tbl[idx_b])
                    comp_im = fit_cover_target(rgb_b, W, H, zoom=1.01 + 0.04 * (dt_b2 / 2.34)).convert("RGBA")

                u_h = ease_out_back(min(1.0, dt_3a / 0.32), s=1.22)
                paste_centered(comp_im, header_2011, 540, 215, scale=0.86 + 0.14 * u_h)
                cap_y_base = 1605
            else:
                # CELEBRATORY FIREWORKS + CHALKBOARD HERO REVEAL ("KIỂM TRA MIỆNG – TRẢ LỜI ĐÚNG, NHẬN QUÀ NGAY!")
                dt_c = t - t_board
                comp_im = dark_neon_bg.copy()
                show_captions = False

                # Multiple colorful celebratory fireworks bursting behind & above the chalkboard!
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
        # SCENE 4: 6 QUIZ QUESTIONS POPPING UP SEQUENTIALLY & STACKING TO FILL SCREEN (21.97..27.93s, TIGHT!)
        # ======================================================================
        elif fi < segs["s4_questions"]["f1"]:
            s4_t0 = segs["s4_questions"]["t0"]
            s4_t1 = segs["s4_questions"]["t1"]
            dt_4 = t - s4_t0
            idx_q = int(dt_4 * FPS) % len(v_quiz_fcbg)
            rgb_q = polish_sunny_frame(v_quiz_fcbg[idx_q])
            comp_im = fit_cover_target(rgb_q, W, H, zoom=1.02 + 0.04 * (dt_4 / 5.97), cx_px=540, cy_px=930).convert("RGBA")

            draw_pill_banner(comp_im, "100 CÂU HỎI HỌC ĐƯỜNG & ĐỐ MẸO", 540, 112, (232, 42, 68), COL_GOLD_5, fsz=29)

            out_f4 = smoothstep((s4_t1 - t) / 0.18) if (s4_t1 - t) < 0.18 else 1.0
            for q_off, q_spr, q_cy, q_ang in quiz_card_sprites:
                if dt_4 >= q_off:
                    dq = dt_4 - q_off
                    uq = ease_out_back(min(1.0, dq / 0.24), s=1.32)
                    pop_y = q_cy + (1.0 - min(1.0, uq)) * 120.0
                    paste_centered(comp_im, q_spr, 540, pop_y, scale=0.80 + 0.20 * uq, opacity=min(1.0, dq / 0.10) * out_f4, angle=q_ang)
                    draw_confetti_burst(comp_im, 540, q_cy, dt_4, q_off + 0.03, 110)

            cap_y_base = 1725

        # ======================================================================
        # SCENE 5: STANDALONE "CÓ QUÀ!!" + FULL-SCREEN REAL FOOD + FULL "20/11" SPEECH (27.93..36.83s)
        # ======================================================================
        elif fi < segs["s5_gifts"]["f1"]:
            s5_t0 = segs["s5_gifts"]["t0"]
            s5_t1 = segs["s5_gifts"]["t1"]
            dt_5  = t - s5_t0
            lf = min(len(v_s5) - 1, fi - segs["s5_gifts"]["f0"])
            rgb_5 = polish_sunny_frame(v_s5[lf])

            # 0.00..1.56s: Khang "Trả lời đúng — CÓ QUÀ!!" (standalone huge CÓ QUÀ!! + step push-in!)
            # 1.56..4.67s: Full-screen crystal-clear REAL Feel Chicken food (C9604 combo table + C3490 4-flavor crispy platter — NO AI cheese blob!)
            # 4.67..8.90s: Khang full-screen "mọi người khi đến Feel Chicken từ ngày hôm nay cho đến hết ngày 20/11!" (step push-in on 20/11!)
            t_co_qua   = s5_t0 + 0.88
            t_food_in  = s5_t0 + 1.56
            t_food_mid = s5_t0 + 3.11
            t_food_out = s5_t0 + 4.67
            t_2011_hit = s5_t0 + 7.92

            if t < t_food_in:
                z_5a = step_zoom(t, 1.01, [(t_co_qua, 1.16, 0.16)])
                comp_im = fit_cover_target(rgb_5, W, H, zoom=z_5a, cx_px=540, cy_px=880).convert("RGBA")
                show_captions = False
                if t < t_co_qua:
                    sp_tld = get_text_sprite("Trả lời đúng...", FONT_BUBBLE, 60, COL_CREAM_5, outer_stroke=(36, 14, 20), outer_w=9, inner_w=4)
                    paste_centered(comp_im, sp_tld, 540, 1510)
                else:
                    dcq = t - t_co_qua
                    ucq = ease_out_back(min(1.0, dcq / 0.18), s=1.45)
                    sp_cq = get_text_sprite(
                        "CÓ QUÀ!!", FONT_POP, 120, COL_GOLD_5,
                        outer_stroke=(255, 255, 255), outer_w=15, inner_stroke=(196, 24, 52), inner_w=6,
                        glow_col=(255, 212, 68), glow_rad=15, sheen_prog=dcq * 1.05
                    )
                    paste_centered(comp_im, sp_cq, 540, 1515, scale=0.80 + 0.20 * ucq)
                    b_gf = get_sticker_badge(stickers, "FC_st_gift_chicken", 185, (255, 102, 128))
                    paste_centered(comp_im, b_gf, 855, 1315, scale=0.78 + 0.22 * ucq, angle=8.0)
                    draw_confetti_burst(comp_im, 540, 1440, t, t_co_qua + 0.04, 145)

            elif t < t_food_out:
                if t < t_food_mid:
                    idx_f = min(len(b_c9604_srv) - 1, int((t - t_food_in) * FPS))
                    rgb_f = polish_sunny_frame(b_c9604_srv[idx_f])
                    comp_im = fit_cover_target(rgb_f, W, H, zoom=1.01 + 0.05 * ((t - t_food_in) / 1.55)).convert("RGBA")
                else:
                    idx_f = min(len(b_c3490_plt) - 1, int((t - t_food_mid) * FPS))
                    rgb_f = polish_sunny_frame(b_c3490_plt[idx_f])
                    comp_im = fit_cover_target(rgb_f, W, H, zoom=1.01 + 0.05 * ((t - t_food_mid) / 1.56)).convert("RGBA")
                draw_pill_banner(comp_im, "TOÀN QUÀ NGON TỪ FEEL CHICKEN!", 540, 128, (228, 38, 64), COL_GOLD_5, fsz=30)
                cap_y_base = 1560

            else:
                z_5b = step_zoom(t, 1.01, [(t_2011_hit, 1.15, 0.18)])
                comp_im = fit_cover_target(rgb_5, W, H, zoom=z_5b, cx_px=540, cy_px=880).convert("RGBA")
                draw_pill_banner(comp_im, "ÁP DỤNG TẤT CẢ MỌI NGƯỜI • ĐẾN HẾT 20/11!", 540, 128, (238, 124, 42), COL_CREAM_5, fsz=28)
                cap_y_base = 1530

        # ======================================================================
        # SCENE 6A: WIDER REALISTIC STUDENT GROUP + REAL CLOSE-UP CRISPY CHICKEN BITES (36.83..42.73s)
        # ======================================================================
        elif fi < segs["s6a_outro"]["f1"]:
            s6a_t0 = segs["s6a_outro"]["t0"]
            s6a_t1 = segs["s6a_outro"]["t1"]
            dt_6 = t - s6a_t0
            t_b1 = s6a_t0 + 2.45
            t_b2 = s6a_t0 + 4.20

            if t < t_b1:
                idx_w = int(dt_6 * FPS) % len(v_outro_wide)
                rgb_w = polish_sunny_frame(v_outro_wide[idx_w])
                comp_im = fit_cover_target(rgb_w, W, H, zoom=1.01 + 0.04 * (dt_6 / 2.45)).convert("RGBA")
            elif t < t_b2:
                idx_p = min(len(b_6494_pull) - 1, int((t - t_b1) * FPS))
                rgb_p = polish_sunny_frame(b_6494_pull[idx_p])
                comp_im = fit_cover_target(rgb_p, W, H, zoom=1.01 + 0.05 * ((t - t_b1) / 1.75)).convert("RGBA")
            else:
                idx_bt = min(len(b_6495_bite) - 1, int((t - t_b2) * FPS))
                rgb_bt = polish_sunny_frame(b_6495_bite[idx_bt])
                comp_im = fit_cover_target(rgb_bt, W, H, zoom=1.01 + 0.05 * ((t - t_b2) / 1.70)).convert("RGBA")

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

            cap_y_base = 1650

        # ======================================================================
        # SCENE 6B: KHANG THUMBS UP ("Đến với Feel Chicken ngay thôi!") -> IMMEDIATE CUT!
        # ======================================================================
        elif fi < segs["s6b_thumbs"]["f1"]:
            s6b_t0 = segs["s6b_thumbs"]["t0"]
            lf = min(len(v_s6b) - 1, fi - segs["s6b_thumbs"]["f0"])
            dt_6b = t - s6b_t0
            rgb_6b = polish_sunny_frame(v_s6b[lf])
            z_6b = step_zoom(t, 1.01, [(s6b_t0 + 0.95, 1.12, 0.18)])
            comp_im = fit_cover_target(rgb_6b, W, H, zoom=z_6b, cx_px=540, cy_px=920).convert("RGBA")
            cap_y_base = 1560

        # ======================================================================
        # SCENE 6C: REAL FEEL CHICKEN STOREFRONT EXTERIOR SHOT FROM FILE GỐC + END-CARD!
        # ======================================================================
        else:
            s6c_t0 = segs["s6c_storefront"]["t0"]
            dt_e = t - s6c_t0
            lf = min(len(b_c3471_frt) - 1, fi - segs["s6c_storefront"]["f0"])
            rgb_fr = polish_sunny_frame(b_c3471_frt[lf])
            comp_im = fit_cover_target(rgb_fr, W, H, zoom=1.01 + 0.05 * smoothstep(dt_e / 2.40)).convert("RGBA")
            show_captions = False

            # Celebratory firework burst over storefront!
            draw_firework_explosion(comp_im, 240, 290, t, s6c_t0 + 0.12, radius_max=230, main_col=(255, 218, 68), alt_col=(255, 92, 132))
            draw_firework_explosion(comp_im, 840, 270, t, s6c_t0 + 0.32, radius_max=230, main_col=(88, 238, 192), alt_col=(255, 214, 72))

            ue = ease_out_back(min(1.0, dt_e / 0.30))
            paste_centered(comp_im, logo_clean, 540, 205, scale=0.84 + 0.16 * ue)
            sp_go = get_text_sprite("GHÉ FEEL CHICKEN NGAY!", FONT_POP, 66, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(196, 28, 52), inner_w=5, sheen_prog=dt_e * 0.8)
            paste_centered(comp_im, sp_go, 540, 390, scale=min(1.0, 980.0 / max(1.0, sp_go.width)) * (0.85 + 0.15 * ue))

            ew, eh = 992, 232
            ec = Image.new("RGBA", (ew + 28, eh + 28), (0, 0, 0, 0))
            ed = ImageDraw.Draw(ec)
            ed.rounded_rectangle([8, 8, 20 + ew, 20 + eh], radius=48, fill=(255, 255, 255, 255))
            ed.rounded_rectangle([14, 14, 14 + ew, 14 + eh], radius=42, fill=(218, 36, 62, 252))
            sp_a1 = get_text_sprite("CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt", FONT_SANS_XB, 29, COL_CREAM_5, outer_w=0, inner_w=3)
            sp_a2 = get_text_sprite("Mở cửa: 10:00 – 22:00  •  Hotline: 0796 601 106", FONT_SANS_XB, 31, COL_GOLD_5, outer_w=0, inner_w=3)
            paste_centered(ec, sp_a1, (ew + 28) // 2, 84, scale=min(1.0, (ew - 40) / max(1.0, sp_a1.width)))
            paste_centered(ec, sp_a2, (ew + 28) // 2, 164, scale=min(1.0, (ew - 40) / max(1.0, sp_a2.width)))
            paste_centered(comp_im, ec, 540, 1705, scale=0.88 + 0.12 * ue)

        # ======================================================================
        # FACE-SAFE KAWAII CAPTIONS (ZERO OUTER WHITE BORDER ON SCREEN!)
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
            tp = os.path.join(CHECK_DIR, f"fc_v3_test_{len(test_saved):02d}.jpg")
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
        gp = os.path.join(CHECK_DIR, "fc_v3_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved 12-frame V3 QA grid:", gp, flush=True)
    else:
        print(f"Finished rendering {total_frames} V3 frames -> {raw_vid_out} in {time.time()-t_start:.1f}s", flush=True)

if __name__ == "__main__":
    main()
