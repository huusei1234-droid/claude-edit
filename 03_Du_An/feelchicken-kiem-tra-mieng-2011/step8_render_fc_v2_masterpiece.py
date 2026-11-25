import json, math, os, re, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
LOGO_PATH = r"Z:\Máy tính khác\My Computer\feel chicken\logo feel tn.png"
POSTER_2011_PATH = r"Z:\Máy tính khác\My Computer\feel chicken\Bai_Dang_Thang_11\20_11_Kiem_Tra_Mieng\Poster_20_11_Kiem_Tra_Mieng_Full_1x1.png"
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0

sys.path.insert(0, PROJ_DIR)
from step3b_render_fc_kute import (
    COL_CORAL_5, COL_GOLD_5, COL_MINT_5, COL_CREAM_5,
    FONT_BUBBLE, FONT_POP, FONT_SANS_XB, FONT_SANS_B,
    GOLD_KEYWORDS, CORAL_KEYWORDS, POP_EMPHASIS,
    clamp01, smoothstep, ease_out_cubic, ease_out_back, smooth_env,
    polish_sunny_frame, get_font, get_text_sprite, paste_centered,
    load_stickers, get_sticker_badge, draw_confetti_burst,
    draw_kawaii_frame_border, draw_behind_speaker_card, draw_pill_banner,
    build_caption_groups, load_all_frames_rgb, load_all_frames_gray
)

def fit_cover_target(rgb_arr, target_w, target_h, zoom=1.0, cx_px=540.0, cy_px=960.0, shake_xy=(0.0, 0.0), angle_deg=0.0):
    """Smoothly zooms & pans any frame so source pixel (cx_px, cy_px) lands near screen center, with optional camera shake & Dutch tilt!"""
    sh, sw = rgb_arr.shape[:2]
    base_sc = max(target_w / float(sw), target_h / float(sh))
    sc = base_sc * max(1.0, float(zoom))
    nw = max(target_w, int(round(sw * sc)))
    nh = max(target_h, int(round(sh * sc)))
    im = Image.fromarray(rgb_arr, "RGB").resize((nw, nh), Image.Resampling.BILINEAR)

    # Map (cx_px, cy_px) in 1080x1920 reference space into resized (nw, nh)
    rx = (cx_px / float(target_w)) * nw
    ry = (cy_px / float(target_h)) * nh
    x0 = int(round(rx - target_w * 0.5 - shake_xy[0]))
    y0 = int(round(ry - target_h * 0.5 - shake_xy[1]))
    x0 = max(0, min(nw - target_w, x0))
    y0 = max(0, min(nh - target_h, y0))
    cropped = im.crop((x0, y0, x0 + target_w, y0 + target_h))
    if abs(angle_deg) > 0.15:
        # Slight oversize rotate so corners never show black
        ov = cropped.resize((int(target_w * 1.06), int(target_h * 1.06)), Image.Resampling.BILINEAR)
        ov = ov.rotate(angle_deg, resample=Image.Resampling.BILINEAR)
        ox = (ov.width - target_w) // 2
        oy = (ov.height - target_h) // 2
        cropped = ov.crop((ox, oy, ox + target_w, oy + target_h))
    return cropped

def eval_kf_curve(t, keyframes):
    """Piecewise smoothstep keyframe evaluator: keyframes = [(t0, val0), (t1, val1), ...]"""
    if t <= keyframes[0][0]:
        return keyframes[0][1]
    if t >= keyframes[-1][0]:
        return keyframes[-1][1]
    for i in range(len(keyframes) - 1):
        t0, v0 = keyframes[i]
        t1, v1 = keyframes[i + 1]
        if t0 <= t <= t1:
            u = smoothstep((t - t0) / max(0.01, t1 - t0))
            return v0 + (v1 - v0) * u
    return keyframes[-1][1]

def draw_spiky_impact_badge(canvas_im, text, cx, cy, scale=1.0, opacity=1.0):
    """Manga/variety-show table-slap starburst badge ('RẦM!!') — placed strictly on counter wood!"""
    if opacity <= 0.01 or scale <= 0.02:
        return
    S = 320
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    c = S // 2
    pts_outer, pts_inner = [], []
    n_spikes = 14
    for i in range(n_spikes * 2):
        ang = math.radians(i * (180.0 / n_spikes))
        r_o = (138 if i % 2 == 0 else 86)
        r_i = (124 if i % 2 == 0 else 74)
        pts_outer.append((c + r_o * math.cos(ang), c + r_o * math.sin(ang) * 0.72))
        pts_inner.append((c + r_i * math.cos(ang), c + r_i * math.sin(ang) * 0.72))
    dr.polygon(pts_outer, fill=(255, 255, 255, 250))
    dr.polygon(pts_inner, fill=(242, 42, 68, 252), outline=(255, 218, 64, 255))
    sp = get_text_sprite(text, FONT_POP, 56, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=8, inner_stroke=(48, 16, 22), inner_w=4)
    paste_centered(im, sp, c, c, angle=-8.0)
    paste_centered(canvas_im, im, cx, cy, scale=scale, opacity=opacity)

def draw_tiktok_pov_text(canvas_im, lines, cy_top, opacity=1.0):
    """Renders authentic viral Vietnamese TikTok POV meme caption (crisp white + thick black stroke, Image 3 style)!"""
    if opacity <= 0.01:
        return
    lh = 64
    for i, ln in enumerate(lines):
        sp = get_text_sprite(
            ln, FONT_SANS_XB, 44,
            [(255, 255, 255)] * 5,
            outer_stroke=(12, 12, 16), outer_w=10,
            inner_stroke=(12, 12, 16), inner_w=5,
            glow_col=None, glow_rad=0, shadow_alpha=120
        )
        sc = min(1.0, 990.0 / max(1.0, sp.width))
        paste_centered(canvas_im, sp, 540, cy_top + i * lh, scale=sc, opacity=opacity)

def build_festive_2011_hero_banner(logo_clean, stickers):
    """Pre-renders a gorgeous festive Kawaii 20/11 Calendar Hero Banner for Image 4 ('20/11 sắp tới rồi!')"""
    bw, bh = 988, 456
    card = Image.new("RGBA", (bw + 40, bh + 56), (0, 0, 0, 0))
    sh = Image.new("RGBA", (bw + 40, bh + 56), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 32, 20 + bw, 32 + bh], radius=58, fill=(44, 18, 24, 96))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=12)))
    dr = ImageDraw.Draw(card)

    # Outer white sticker border + coral-pink festive calendar frame + warm cream paper
    dr.rounded_rectangle([10, 18, 30 + bw, 38 + bh], radius=62, fill=(255, 255, 255, 255))
    dr.rounded_rectangle([18, 26, 22 + bw, 30 + bh], radius=54, fill=(238, 56, 84, 255))
    dr.rounded_rectangle([30, 86, 10 + bw, 18 + bh], radius=44, fill=(255, 250, 240, 255), outline=(255, 210, 96, 255), width=4)

    # Cute spiral notebook calendar rings across top bar!
    for rx in range(110, bw - 50, 110):
        dr.rounded_rectangle([rx - 10, 4, rx + 10, 44], radius=9, fill=(255, 244, 214, 255), outline=(186, 42, 64, 255), width=3)
        dr.ellipse([rx - 9, 34, rx + 9, 52], fill=(168, 28, 50, 255))

    cx = (bw + 40) // 2
    sp_top = get_text_sprite("★ CHÀO MỪNG NGÀY NHÀ GIÁO VIỆT NAM ★", FONT_SANS_XB, 26, COL_GOLD_5, outer_w=0, inner_stroke=(92, 16, 28), inner_w=3, shadow_alpha=40)
    paste_centered(card, sp_top, cx, 57, scale=min(1.0, (bw - 80) / max(1.0, sp_top.width)))

    sp_2011 = get_text_sprite("20/11 SẮP TỚI RỒI!", FONT_POP, 84, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=12, inner_stroke=(62, 18, 28), inner_w=5, glow_col=(255, 196, 88), glow_rad=10)
    paste_centered(card, sp_2011, cx, 205, scale=min(1.0, (bw - 70) / max(1.0, sp_2011.width)))

    # Warm gold-mint ribbon pill inside calendar
    dr.rounded_rectangle([86, 292, bw - 46, 362], radius=34, fill=(36, 104, 78, 255), outline=(255, 216, 88, 255), width=4)
    sp_mid = get_text_sprite("FEEL CHICKEN ĐƯA BẠN VỀ KÝ ỨC HỌC TRÒ!", FONT_SANS_XB, 28, COL_GOLD_5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(card, sp_mid, cx, 327, scale=min(1.0, (bw - 170) / max(1.0, sp_mid.width)))

    sp_bot = get_text_sprite("Sẵn sàng lên bảng ôn bài nhận quà cực xịn nha!", FONT_BUBBLE, 34, [(86, 34, 42)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(card, sp_bot, cx, 412, scale=min(1.0, (bw - 90) / max(1.0, sp_bot.width)))
    return card

def main():
    t_start = time.time()
    test_mode = "--test" in sys.argv

    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    total_frames = tm["total_frames"]
    cap_groups = build_caption_groups(tm["words"])

    print("Loading A-rolls, RVM mattes & V2 Feel Chicken scenes...", flush=True)
    v_s1   = load_all_frames_rgb(os.path.join(AROLL_DIR, "s1_skit.mp4"), W, H)
    v_s2   = load_all_frames_rgb(os.path.join(AROLL_DIR, "s2_table.mp4"), W, H)
    v_s3_d = load_all_frames_rgb(os.path.join(AROLL_DIR, "s3_c3948_dolly.mp4"), W, H)
    v_s5   = load_all_frames_rgb(os.path.join(AROLL_DIR, "s5_gifts.mp4"), W, H)
    m_s5   = load_all_frames_gray(os.path.join(AROLL_DIR, "s5_gifts_matte.mp4"), W, H)
    v_s6_w = load_all_frames_rgb(os.path.join(AROLL_DIR, "s6a_fc_wide_c9640.mp4"), W, H)
    v_s6b  = load_all_frames_rgb(os.path.join(AROLL_DIR, "s6_thumbs.mp4"), W, H)
    b_jar_shake = load_all_frames_rgb(os.path.join(AROLL_DIR, "broll_jar_shake.mp4"), W, H)

    # New V2 9:16 Vertical Videos!
    v_meme_pray  = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v2_meme_pray_vid.mp4"), W, H)
    v_quiz_fcbg  = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v2_quiz_fcbg_vid.mp4"), W, H)
    v_outro_wide = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v2_outro_fcwide_vid.mp4"), W, H)

    # Food 16:9 showcase videos for Scene 5
    v_cheese = load_all_frames_rgb(os.path.join(MEDIA_DIR, "MUSE_fc_cheese_pour.mp4"), 1280, 720)
    v_feast  = load_all_frames_rgb(os.path.join(MEDIA_DIR, "MUSE_fc_feast_table.mp4"), 1280, 720)

    banner_bg_p = os.path.join(MEDIA_DIR, "FC_v2_banner_2011_bg.png")
    banner_bg_im = Image.open(banner_bg_p).convert("RGB").resize((W, H), Image.Resampling.LANCZOS) if os.path.exists(banner_bg_p) else Image.new("RGB", (W, H), (255, 240, 228))

    stickers = load_stickers()
    logo_clean = stickers["logo_fc"].copy()
    logo_clean.thumbnail((260, 260), Image.Resampling.LANCZOS)
    hero_2011_card = build_festive_2011_hero_banner(logo_clean, stickers)

    yy_g, xx_g = np.ogrid[0:H, 0:W]
    s5_lower_guard = np.clip((yy_g.astype(np.float32) - 1180.0) / 75.0, 0.0, 1.0)

    # 12 key QA frames spanning every single user request (including Scene 5)!
    test_times = [1.48, 4.25, 6.20, 8.80, 9.48, 11.10, 12.60, 15.60, 26.50, 31.50, 35.50, 41.50]
    test_fset = {min(total_frames - 1, int(round(ts * FPS))) for ts in test_times}
    test_saved = []

    raw_vid_out = os.path.join(PROJ_DIR, "_fc_kute_v2_video_only.mp4")
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
        cap_y_base = 1480

        # ======================================================================
        # SCENE 1: OPENING SKIT — TABLE SLAP IMPACT + THÀNH CLUELESS ZOOM (0.00..5.00s)
        # ======================================================================
        if fi < segs["s1_skit"]["f1"]:
            lf = min(len(v_s1) - 1, fi - segs["s1_skit"]["f0"])
            rgb = polish_sunny_frame(v_s1[lf])
            show_captions = False

            if t < 1.41:
                # Approach counter smoothly
                z1 = 1.01 + 0.05 * smoothstep(t / 1.41)
                comp_im = fit_cover_target(rgb, W, H, zoom=z1, cx_px=540, cy_px=960).convert("RGBA")
            elif t < 3.08:
                # 1.41s: KHANG SLAPS THE WOODEN COUNTER + POINTS AT THÀNH!
                dt_slap = t - 1.41
                z_punch = 1.18 - 0.06 * smoothstep(min(1.0, dt_slap / 0.90))
                decay = math.exp(-dt_slap * 11.5)
                sh_x = math.sin(dt_slap * 96.0) * 26.0 * decay
                sh_y = math.cos(dt_slap * 118.0) * 20.0 * decay
                comp_im = fit_cover_target(rgb, W, H, zoom=z_punch, cx_px=615, cy_px=920, shake_xy=(sh_x, sh_y)).convert("RGBA")

                # Impact flash on slap (first 4 frames)
                if dt_slap < 0.14:
                    fl_a = int(68 * (1.0 - dt_slap / 0.14))
                    comp_im = Image.alpha_composite(comp_im, Image.new("RGBA", (W, H), (255, 245, 220, fl_a)))

                # Spiky "RẦM!!" badge right on the wooden counter (y=1110, 100% Face-Safe!)
                env_ram = smooth_env(t, 1.41, 2.05, 0.05, 0.20)
                if env_ram > 0.01:
                    u_r = ease_out_back(min(1.0, dt_slap / 0.18), s=1.45)
                    draw_spiky_impact_badge(comp_im, "RẦM!!", 685, 1115, scale=0.75 + 0.28 * u_r, opacity=env_ram)
                    draw_confetti_burst(comp_im, 685, 1060, t, 1.42, 120)
            else:
                # 3.08..5.00s: COMEDY CRASH-ZOOM + CREEPING MEME ZOOM INTO THÀNH'S CLUELESS FACE!
                dt_z = t - 3.08
                if dt_z < 0.34:
                    uz = ease_out_cubic(dt_z / 0.34)
                    z_th = 1.12 + (1.92 - 1.12) * uz
                    cx_th = 615.0 + (808.0 - 615.0) * uz
                    cy_th = 920.0 + (895.0 - 920.0) * uz
                    ang_th = 1.9 * uz
                else:
                    uz2 = smoothstep((dt_z - 0.34) / 1.58)
                    z_th = 1.92 + (2.18 - 1.92) * uz2
                    cx_th, cy_th, ang_th = 808.0, 895.0, 1.9
                comp_im = fit_cover_target(rgb, W, H, zoom=z_th, cx_px=cx_th, cy_px=cy_th, angle_deg=ang_th).convert("RGBA")

                # Subtle comedic vignette focusing on Thành's bewildered expression
                vig = np.zeros((H, W, 4), dtype=np.uint8)
                ry = (np.arange(H, dtype=np.float32)[:, None] - 930.0) / 960.0
                rx = (np.arange(W, dtype=np.float32)[None, :] - 540.0) / 540.0
                rr = np.clip((rx * rx + ry * ry - 0.35) / 0.85, 0.0, 1.0)
                vig[:, :, 3] = (rr * 95.0 * min(1.0, dt_z / 0.30)).astype(np.uint8)
                comp_im = Image.alpha_composite(comp_im, Image.fromarray(vig, "RGBA"))

                # Floating "?  ?  ?" marks ABOVE Thành's hair (y=360..430, ZERO face overlap!)
                for qi, (qt0, qx, qy, qang) in enumerate([
                    (3.16, 355, 425, -14.0),
                    (3.30, 540, 365,   2.0),
                    (3.44, 725, 425,  14.0),
                ]):
                    if t >= qt0:
                        dq = t - qt0
                        uq = ease_out_back(min(1.0, dq / 0.22), s=1.35)
                        wob = math.sin(t * 7.5 + qi * 1.8) * 6.0
                        sp_q = get_text_sprite("?", FONT_POP, 88 if qi == 1 else 74, COL_GOLD_5 if qi == 1 else COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(48, 18, 24), inner_w=4)
                        paste_centered(comp_im, sp_q, qx, qy + math.sin(t * 5.0 + qi) * 6.0, scale=0.75 + 0.25 * uq, opacity=min(1.0, (5.0 - t) / 0.16), angle=qang + wob)

                # Thành's shivering bubble WAY DOWN on his chest/shirt (y=1515 — 100% Face-Safe!)
                env_b2 = smooth_env(t, 3.85, 4.96, 0.15, 0.16)
                if env_b2 > 0.01:
                    ub2 = ease_out_back(min(1.0, (t - 3.85) / 0.22))
                    jx = math.sin(t * 48.0) * 4.5
                    jy = math.cos(t * 40.0) * 2.5
                    sw_w, sw_h = 540, 126
                    sbub = Image.new("RGBA", (sw_w + 24, sw_h + 24), (0, 0, 0, 0))
                    sd = ImageDraw.Draw(sbub)
                    sd.rounded_rectangle([6, 6, 18 + sw_w, 18 + sw_h], radius=48, fill=(255, 255, 255, 255))
                    sd.rounded_rectangle([12, 12, 12 + sw_w, 12 + sw_h], radius=42, fill=(32, 44, 66, 244), outline=(102, 206, 255, 255), width=5)
                    sp_em = get_text_sprite("Em... em... ơ kìa?!", FONT_BUBBLE, 46, COL_MINT_5, outer_stroke=(24, 32, 48), outer_w=6, inner_w=3)
                    paste_centered(sbub, sp_em, (sw_w + 24) // 2, (sw_h + 24) // 2, scale=min(1.0, (sw_w - 28) / max(1.0, sp_em.width)))
                    paste_centered(comp_im, sbub, 540 + jx, 1515 + jy, scale=0.84 + 0.16 * ub2, opacity=env_b2)

            # Top header pill (only during 0.12..3.05s before Thành crash-zoom)
            env_hdr = smooth_env(t, 0.12, 3.06, 0.20, 0.16)
            if env_hdr > 0.01:
                draw_pill_banner(comp_im, "LỚP HỌC FEEL CHICKEN • 20/11", 540, 108, (232, 48, 72), COL_GOLD_5, fsz=29, scale=0.92 + 0.08 * env_hdr, opacity=env_hdr)

            # Anh Khang's Speech Bubble HIGH in clean ceiling space (y=278, disappears cleanly at 3.12s!)
            env_b1 = smooth_env(t, 1.40, 3.12, 0.14, 0.16)
            if env_b1 > 0.01:
                ub1 = ease_out_back(min(1.0, (t - 1.40) / 0.24))
                bw, bh = 840, 198
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
        # SCENE 2: KHANG DYNAMIC KEYFRAME ZOOM + STANDALONE "KIỂM TRA MIỆNG" + POV MEME VIDEO (5.00..14.03s)
        # ======================================================================
        elif fi < segs["s2_table"]["f1"]:
            t_pov_cut = 9.98  # Right after "run cầm cập!", cut to hilarious POV praying classroom video!

            if t < t_pov_cut:
                lf = min(len(v_s2) - 1, fi - segs["s2_table"]["f0"])
                rgb = polish_sunny_frame(v_s2[lf])

                # Dynamic Keyframe Zoom In/Out centered on Khang (cx=540, cy=1140 in s2_table so zooming in moves Khang UP into clean center and NEVER under bottom text!)
                z_k = eval_kf_curve(t, [
                    (5.00, 1.18),
                    (6.38, 1.02),
                    (8.48, 1.15),
                    (8.66, 1.32),
                    (9.98, 1.36),
                ])
                cy_k = eval_kf_curve(t, [(5.00, 1140.0), (6.38, 980.0), (8.48, 1120.0), (8.66, 1180.0), (9.98, 1185.0)])
                jit_shiver = (math.sin(t * 58.0) * 5.5, math.cos(t * 46.0) * 2.5) if (9.30 <= t <= 9.94) else (0.0, 0.0)
                comp_im = fit_cover_target(rgb, W, H, zoom=z_k, cx_px=540, cy_px=cy_k, shake_xy=jit_shiver).convert("RGBA")

                # Lower-Only Face-Safe Captions (y=1565..1640, 450px+ below Khang's face!)
                cap_y_base = 1565
                if t >= 8.56:
                    # STANDALONE GIANT "KIỂM TRA MIỆNG" + "RUN CẦM CẬP!!" (separated, huge, 0% face overlap!)
                    show_captions = False
                    dt_ktm = t - 8.56
                    u_ktm = ease_out_back(min(1.0, dt_ktm / 0.24), s=1.35)
                    sp_ktm = get_text_sprite(
                        "KIỂM TRA MIỆNG", FONT_POP, 96, COL_GOLD_5,
                        outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(54, 18, 24), inner_w=5,
                        glow_col=(255, 206, 68), glow_rad=12, sheen_prog=dt_ktm * 0.85
                    )
                    paste_centered(comp_im, sp_ktm, 540, 1495, scale=min(1.0, 990.0 / max(1.0, sp_ktm.width)) * (0.82 + 0.18 * u_ktm))

                    if t >= 9.28:
                        dt_run = t - 9.28
                        u_run = ease_out_back(min(1.0, dt_run / 0.20), s=1.40)
                        rx_j = math.sin(t * 62.0) * 6.0
                        sp_run = get_text_sprite(
                            "RUN CẦM CẬP!!", FONT_BUBBLE, 74, COL_CORAL_5,
                            outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(54, 18, 24), inner_w=4
                        )
                        paste_centered(comp_im, sp_run, 540 + rx_j, 1645, scale=0.84 + 0.16 * u_run)
            else:
                # 9.98..14.03s: HILARIOUS CLASSROOM PRAYING MEME VIDEO + TIKTOK POV CAPTION (Image 3 style!)
                dt_m = t - t_pov_cut
                idx_m = int(dt_m * FPS) % len(v_meme_pray)
                rgb_m = polish_sunny_frame(v_meme_pray[idx_m])
                z_m = 1.02 + 0.08 * smoothstep(dt_m / 4.05)
                comp_im = fit_cover_target(rgb_m, W, H, zoom=z_m, cx_px=540, cy_px=960).convert("RGBA")
                show_captions = False

                # Top subtle dark gradient for crisp POV text legibility without hiding faces!
                top_g = np.zeros((H, W, 4), dtype=np.uint8)
                yg = np.clip(1.0 - np.arange(H, dtype=np.float32) / 480.0, 0.0, 1.0)
                top_g[:, :, 3] = (yg * 105.0).astype(np.uint8)[:, None]
                comp_im = Image.alpha_composite(comp_im, Image.fromarray(top_g, "RGBA"))

                env_pov = smooth_env(t, t_pov_cut + 0.05, 13.98, 0.18, 0.18)
                draw_tiktok_pov_text(comp_im, [
                    "POV: Cô giáo kiểm tra miệng đến",
                    "đứa thứ 5 rồi vẫn chưa có dấu",
                    "hiệu dừng lại",
                ], cy_top=175, opacity=env_pov)

                # Bottom speech emphasis: standalone "KIỂM TRA MIỆNG" when spoken at 12.00..13.95s!
                if 10.05 <= t < 11.98:
                    sp_b0 = get_text_sprite("Còn bây giờ nghe đến ba chữ...", FONT_BUBBLE, 48, COL_CREAM_5, outer_stroke=(32, 14, 18), outer_w=8, inner_w=4)
                    paste_centered(comp_im, sp_b0, 540, 1595, scale=min(1.0, 960.0 / max(1.0, sp_b0.width)))
                elif t >= 11.98:
                    dt_k2 = t - 11.98
                    uk2 = ease_out_back(min(1.0, dt_k2 / 0.24), s=1.32)
                    sp_ktm2 = get_text_sprite(
                        "KIỂM TRA MIỆNG", FONT_POP, 90, COL_GOLD_5,
                        outer_stroke=(255, 255, 255), outer_w=12, inner_stroke=(54, 18, 24), inner_w=5,
                        glow_col=(255, 206, 68), glow_rad=10, sheen_prog=dt_k2 * 0.75
                    )
                    paste_centered(comp_im, sp_ktm2, 540, 1485, scale=min(1.0, 980.0 / max(1.0, sp_ktm2.width)) * (0.84 + 0.16 * uk2))
                    if t >= 12.72:
                        sp_bh = get_text_sprite("thấy BỒI HỒI GHÊ luôn á!", FONT_BUBBLE, 56, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=9, inner_w=4)
                        paste_centered(comp_im, sp_bh, 540, 1615, scale=min(1.0, 940.0 / max(1.0, sp_bh.width)))

        # ======================================================================
        # SCENE 3: FESTIVE 20/11 HERO BANNER (IMAGE 4) + STANDALONE "KIỂM TRA MIỆNG" CHALKBOARD (14.03..22.63s)
        # ======================================================================
        elif fi < segs["s3_program"]["f1"]:
            s3_t0 = segs["s3_program"]["t0"]
            t_board = s3_t0 + 4.72  # 18.75s right as "với chương trình KIỂM TRA MIỆNG..." starts!

            if t < t_board:
                dt_3a = t - s3_t0
                # Warm festive kawaii 20/11 background + real Feel Chicken C3948 storefront / question-jar card below!
                bg_arr = np.array(banner_bg_im)
                comp_im = fit_cover_target(bg_arr, W, H, zoom=1.02 + 0.05 * (dt_3a / 4.72)).convert("RGBA")

                # Lower live video window (14.03..16.45s: C3948 Feel Chicken storefront dolly, 16.45..18.75s: shaking question jar)
                if t < s3_t0 + 2.42:
                    idx_d = min(len(v_s3_d) - 1, int(dt_3a * FPS))
                    sub_rgb = polish_sunny_frame(v_s3_d[idx_d])
                else:
                    idx_j = min(len(b_jar_shake) - 1, int((t - (s3_t0 + 2.42)) * 1.15 * FPS))
                    sub_rgb = polish_sunny_frame(b_jar_shake[idx_j])

                draw_behind_speaker_card(comp_im, sub_rgb, t, s3_t0 + 0.04, t_board + 0.10, None, (238, 56, 84), cy_pos=1095, vh=660)

                # Festive 20/11 Spiral Calendar Hero Banner at Top (y=360, zero face occlusion!)
                u_ban = ease_out_back(min(1.0, dt_3a / 0.36), s=1.24)
                paste_centered(comp_im, hero_2011_card, 540, 355, scale=0.84 + 0.16 * u_ban)

                b_p = get_sticker_badge(stickers, "FC_st_prof_chick", 195, (255, 198, 62))
                b_s = get_sticker_badge(stickers, "FC_st_score10", 195, (255, 112, 146))
                paste_centered(comp_im, b_p, 138, 665 + math.sin(t * 3.6) * 5.0, scale=0.80 + 0.20 * u_ban, angle=-7.0)
                paste_centered(comp_im, b_s, 942, 665 + math.cos(t * 3.6) * 5.0, scale=0.80 + 0.20 * u_ban, angle=7.0)
                draw_confetti_burst(comp_im, 138, 665, t, s3_t0 + 0.14, 92)
                draw_confetti_burst(comp_im, 942, 665, t, s3_t0 + 0.24, 92)
                cap_y_base = 1525
            else:
                # 18.75..22.63s: HERO KAWAII CHALKBOARD WITH HUGE STANDALONE "KIỂM TRA MIỆNG"!
                dt_c = t - t_board
                bg_im = fit_cover_target(np.array(banner_bg_im), W, H, zoom=1.06).filter(ImageFilter.GaussianBlur(radius=6)).convert("RGBA")
                comp_im = Image.alpha_composite(bg_im, Image.new("RGBA", (W, H), (255, 238, 224, 52)))
                show_captions = False

                u_c = ease_out_back(min(1.0, dt_c / 0.36), s=1.28)
                bw, bh = 984, 730
                board = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
                sh = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rounded_rectangle([20, 28, 20 + bw, 28 + bh], radius=64, fill=(38, 18, 22, 110))
                board = Image.alpha_composite(board, sh.filter(ImageFilter.GaussianBlur(radius=14)))
                bd = ImageDraw.Draw(board)
                bd.rounded_rectangle([10, 10, 30 + bw, 30 + bh], radius=68, fill=(255, 255, 255, 255))
                bd.rounded_rectangle([20, 20, 20 + bw, 20 + bh], radius=58, fill=(242, 168, 96, 255))
                bd.rounded_rectangle([38, 38, 2 + bw, 2 + bh], radius=44, fill=(30, 92, 68, 255), outline=(255, 245, 215, 195), width=3)

                # Dedicated golden highlight frame isolating "KIỂM TRA MIỆNG" big & standalone!
                bd.rounded_rectangle([68, 178, bw - 28, 368], radius=36, fill=(22, 70, 52, 255), outline=(255, 216, 84, 245), width=5)

                cx_b = (bw + 40) // 2
                sp_sub0 = get_text_sprite("★ MINIGAME ĐẶC BIỆT NGÀY 20/11 ★", FONT_SANS_XB, 30, COL_MINT_5, outer_w=0, inner_w=3)
                sp_main = get_text_sprite("KIỂM TRA MIỆNG", FONT_POP, 100, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(58, 24, 18), inner_w=5, glow_col=(255, 212, 75), glow_rad=14, sheen_prog=dt_c * 0.65)
                sp_sub1 = get_text_sprite("TRẢ LỜI ĐÚNG", FONT_BUBBLE, 66, COL_CREAM_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(236, 48, 76), inner_w=4)
                sp_sub2 = get_text_sprite("NHẬN QUÀ NGAY!", FONT_POP, 74, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(68, 18, 28), inner_w=4, sheen_prog=(dt_c - 0.35) * 0.75)

                paste_centered(board, sp_sub0, cx_b, 118)
                paste_centered(board, sp_main, cx_b, 273, scale=min(1.0, (bw - 120) / max(1.0, sp_main.width)))
                paste_centered(board, sp_sub1, cx_b, 465)
                paste_centered(board, sp_sub2, cx_b, 595, scale=min(1.0, (bw - 90) / max(1.0, sp_sub2.width)))

                paste_centered(comp_im, board, 540, 910, scale=0.84 + 0.16 * u_c)
                cloud_m = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
                ImageDraw.Draw(cloud_m).ellipse([28, 28, 272, 272], fill=(255, 252, 244, 252), outline=(242, 168, 96, 255), width=6)
                paste_centered(cloud_m, logo_clean, 150, 150, scale=0.92)
                paste_centered(comp_im, cloud_m, 540, 490, scale=0.84 + 0.16 * u_c)

                b_l = get_sticker_badge(stickers, "FC_st_prof_chick", 225, (255, 198, 62))
                b_r = get_sticker_badge(stickers, "FC_st_gift_chicken", 225, (255, 98, 126))
                paste_centered(comp_im, b_l, 185, 1435, scale=0.78 + 0.22 * u_c, angle=-7.0)
                paste_centered(comp_im, b_r, 895, 1435, scale=0.78 + 0.22 * u_c, angle=7.0)
                draw_confetti_burst(comp_im, 185, 1435, t, t_board + 0.08, 96)
                draw_confetti_burst(comp_im, 895, 1435, t, t_board + 0.16, 96)

        # ======================================================================
        # SCENE 4: STUDENTS IN REAL FEEL CHICKEN NEON BG (IMAGE 5+6) + FACE-SAFE QUIZ CARDS (22.63..28.87s)
        # ======================================================================
        elif fi < segs["s4_questions"]["f1"]:
            s4_t0 = segs["s4_questions"]["t0"]
            s4_t1 = segs["s4_questions"]["t1"]
            dt_4 = t - s4_t0
            idx_q = int(dt_4 * FPS) % len(v_quiz_fcbg)
            rgb_q = polish_sunny_frame(v_quiz_fcbg[idx_q])
            # Shift frame slightly downward (cy_px=860) if needed so students sit comfortably in lower half while neon wall stays visible!
            comp_im = fit_cover_target(rgb_q, W, H, zoom=1.03 + 0.05 * smoothstep(dt_4 / 6.23), cx_px=540, cy_px=930).convert("RGBA")

            top_grad = np.zeros((H, W, 4), dtype=np.uint8)
            yg = np.clip(1.0 - np.arange(H, dtype=np.float32) / 760.0, 0.0, 1.0)
            top_grad[:, :, 0] = 24; top_grad[:, :, 1] = 14; top_grad[:, :, 2] = 20
            top_grad[:, :, 3] = (yg * 88.0).astype(np.uint8)[:, None]
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(top_grad, "RGBA"))

            draw_pill_banner(comp_im, "100 CÂU HỎI HỌC ĐƯỜNG & ĐỐ MẸO", 470, 96, (236, 56, 84), COL_GOLD_5, fsz=27)
            b_bulb = get_sticker_badge(stickers, "FC_st_riddle_bulb", 155, (255, 206, 68))
            paste_centered(comp_im, b_bulb, 955, 108, angle=6.0 + math.sin(t * 4.0) * 3.5)

            # Sequential 1-by-1 Carousel Quiz Cards at cy=290 (y=195..385) so the glowing FEEL CHICKEN neon sign (y=520..1100) AND all 3 students' faces (y=1115..1420) stay 100% VISIBLE!
            quiz_cards = [
                (s4_t0 + 0.12, s4_t0 + 2.15, "CẤP ĐỘ DỄ #01",      "Ngày Nhà giáo VN là ngày nào?",      "20/11",     (52, 188, 148), -1),
                (s4_t0 + 2.15, s4_t0 + 4.18, "NGỮ VĂN #41",         "Ai là tác giả tác phẩm Lão Hạc?",    "Nam Cao",   (245, 142, 54), +1),
                (s4_t0 + 4.18, s4_t1 - 0.04, "ĐỐ MẸO LẮT LÉO #100", "Gà 1 chân 2kg, đứng 2 chân mấy kg?", "Vẫn 2 kg!", (238, 58, 92),  -1),
            ]
            for q_t0, q_t1, q_tag, q_txt, q_ans, q_col, q_side in quiz_cards:
                if q_t0 <= t < q_t1:
                    dt_qc = t - q_t0
                    uq = ease_out_back(min(1.0, dt_qc / 0.28), s=1.24)
                    opq = min(1.0, dt_qc / 0.12) * (smoothstep((q_t1 - t) / 0.16) if (q_t1 - t) < 0.16 else 1.0)
                    qw, qh = 972, 186
                    qc = Image.new("RGBA", (qw + 28, qh + 28), (0, 0, 0, 0))
                    qd = ImageDraw.Draw(qc)
                    qd.rounded_rectangle([8, 8, 20 + qw, 20 + qh], radius=44, fill=(255, 255, 255, 254))
                    qd.rounded_rectangle([14, 14, 14 + qw, 14 + qh], radius=38, fill=(255, 250, 244, 250), outline=(*q_col, 248), width=5)
                    qd.rounded_rectangle([34, 26, 342, 70], radius=21, fill=(*q_col, 255))
                    sp_tg = get_text_sprite(q_tag, FONT_SANS_XB, 23, COL_CREAM_5, outer_w=0, inner_w=0, shadow_alpha=0)
                    paste_centered(qc, sp_tg, 188, 48)
                    qd.rounded_rectangle([685, 24, 956, 74], radius=24, fill=(255, 226, 92, 255), outline=(*q_col, 255), width=3)
                    sp_an = get_text_sprite("Đáp án: " + q_ans, FONT_SANS_XB, 24, [(65, 24, 28)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
                    paste_centered(qc, sp_an, 820, 49, scale=min(1.0, 246.0 / max(1.0, sp_an.width)))
                    sp_qq = get_text_sprite(q_txt, FONT_BUBBLE, 40, [(52, 24, 32)] * 5, outer_stroke=(255, 255, 255), outer_w=4, inner_w=0, shadow_alpha=0)
                    paste_centered(qc, sp_qq, (qw + 28) // 2, 134, scale=min(1.0, (qw - 48) / max(1.0, sp_qq.width)))
                    sx_q = 540 + q_side * (1.0 - min(1.0, uq)) * 90.0
                    paste_centered(comp_im, qc, sx_q, 295, scale=0.86 + 0.14 * uq, opacity=opq)

            cap_y_base = 1715

        # ======================================================================
        # SCENE 5: DYNAMIC KEYFRAME ZOOM ON KHANG + FOOD SHOWCASE (28.87..37.57s)
        # ======================================================================
        elif fi < segs["s5_gifts"]["f1"]:
            lf = min(len(v_s5) - 1, fi - segs["s5_gifts"]["f0"])
            s5_t0 = segs["s5_gifts"]["t0"]
            s5_t1 = segs["s5_gifts"]["t1"]

            rgb = polish_sunny_frame(v_s5[lf])
            matte = m_s5[min(len(m_s5) - 1, lf)]

            # Dynamic Keyframe Zoom In/Out on Khang so Scene 5 feels energetic & alive!
            z_5 = eval_kf_curve(t, [
                (s5_t0,        1.02),
                (s5_t0 + 2.20, 1.15),
                (s5_t0 + 3.45, 1.18),
                (s5_t0 + 3.70, 1.04),
                (s5_t0 + 6.50, 1.12),
                (s5_t1,        1.18),
            ])
            fg_im = fit_cover_target(rgb, W, H, zoom=z_5, cx_px=540, cy_px=900)
            fg_rgb = np.array(fg_im)
            m_im = fit_cover_target(np.dstack([matte * 255] * 3).astype(np.uint8), W, H, zoom=z_5, cx_px=540, cy_px=900)
            m_arr = np.array(m_im)[:, :, 0].astype(np.float32) / 255.0

            comp_im = fg_im.convert("RGBA")
            t_food_switch = s5_t0 + 3.45
            if t < t_food_switch:
                vf_rgb = v_cheese[int((t - s5_t0) * FPS) % len(v_cheese)]
                draw_behind_speaker_card(comp_im, vf_rgb, t, s5_t0 + 0.06, t_food_switch + 0.15, "TOÀN QUÀ NGON TỪ FEEL CHICKEN!", (238, 54, 80), cy_pos=390, vh=580)
            else:
                vf_rgb = v_feast[int((t - t_food_switch) * FPS) % len(v_feast)]
                draw_behind_speaker_card(comp_im, vf_rgb, t, t_food_switch - 0.10, s5_t1 - 0.06, "ÁP DỤNG MỌI NGƯỜI NGÀY 20/11!", (242, 134, 52), cy_pos=390, vh=580)

            fg_alpha = np.maximum(m_arr, s5_lower_guard * m_arr)
            comp_im = Image.alpha_composite(comp_im, Image.fromarray(np.dstack([fg_rgb, (fg_alpha * 255.0).astype(np.uint8)]), "RGBA"))

            # Captions cleanly at y=1415 (over Khang's shorts/legs, 600px below his face!)
            cap_y_base = 1415

        # ======================================================================
        # SCENE 6A: REAL WIDE FEEL CHICKEN SOURCE + NEW STUDENT SQUAD IN FEEL CHICKEN (IMAGE 7) (37.57..43.53s)
        # ======================================================================
        elif fi < segs["s6a_outro"]["f1"]:
            s6a_t0 = segs["s6a_outro"]["t0"]
            s6a_t1 = segs["s6a_outro"]["t1"]
            t_sw6 = s6a_t0 + 2.20  # 39.77s: First 2.2s real wide Feel Chicken restaurant source, then 3.76s lively student squad in Feel Chicken!

            if t < t_sw6:
                idx_w = min(len(v_s6_w) - 1, int((t - s6a_t0) * FPS))
                rgb_w = polish_sunny_frame(v_s6_w[idx_w])
                comp_im = fit_cover_target(rgb_w, W, H, zoom=1.02 + 0.06 * ((t - s6a_t0) / 2.20), cx_px=540, cy_px=960).convert("RGBA")
            else:
                dt_o = t - t_sw6
                idx_o = int(dt_o * FPS) % len(v_outro_wide)
                rgb_o = polish_sunny_frame(v_outro_wide[idx_o])
                comp_im = fit_cover_target(rgb_o, W, H, zoom=1.02 + 0.06 * (dt_o / 3.76), cx_px=540, cy_px=940).convert("RGBA")

            # Sleek Top-Header "HỌC SINH GIỎI" Honor Card strictly in y=85..365 (100% ABOVE ALL FACES!)
            env_cert = smooth_env(t, s6a_t0 + 0.16, s6a_t1 - 0.08, 0.24, 0.22)
            if env_cert > 0.01:
                uc = ease_out_back(min(1.0, (t - (s6a_t0 + 0.16)) / 0.34))
                cw_c, ch_c = 956, 266
                cert = Image.new("RGBA", (cw_c + 32, ch_c + 32), (0, 0, 0, 0))
                cd = ImageDraw.Draw(cert)
                cd.rounded_rectangle([14, 20, 14 + cw_c, 20 + ch_c], radius=46, fill=(42, 18, 24, 92))
                cert = cert.filter(ImageFilter.GaussianBlur(radius=8))
                cd = ImageDraw.Draw(cert)
                cd.rounded_rectangle([8, 8, 24 + cw_c, 24 + ch_c], radius=50, fill=(255, 255, 255, 255))
                cd.rounded_rectangle([16, 16, 16 + cw_c, 16 + ch_c], radius=42, fill=(255, 248, 232, 248), outline=(238, 54, 80, 255), width=6)
                cd.rounded_rectangle([28, 28, 4 + cw_c, 4 + ch_c], radius=32, outline=(255, 198, 68, 245), width=3)

                sp_c1 = get_text_sprite("★ DANH HIỆU CAO QUÝ 20/11 ★", FONT_SANS_XB, 25, [(228, 48, 74)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
                sp_c2 = get_text_sprite("HỌC SINH GIỎI", FONT_POP, 76, COL_GOLD_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(58, 20, 26), inner_w=4, sheen_prog=(t - s6a_t0) * 0.60)
                sp_c3 = get_text_sprite("RỦ HỘI BẠN ĐẾN FEEL CHICKEN SĂN QUÀ NGAY!", FONT_SANS_XB, 24, [(64, 28, 34)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)

                paste_centered(cert, sp_c1, (cw_c + 32) // 2, 62)
                paste_centered(cert, sp_c2, (cw_c + 32) // 2, 148, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c2.width)))
                paste_centered(cert, sp_c3, (cw_c + 32) // 2, 230, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c3.width)))
                paste_centered(comp_im, cert, 540, 225, scale=0.84 + 0.16 * uc, opacity=env_cert)

                b_tr = get_sticker_badge(stickers, "FC_st_trophy_star", 155, (255, 204, 62))
                b_ch = get_sticker_badge(stickers, "FC_st_cheers_cups", 155, (255, 112, 146))
                paste_centered(comp_im, b_tr, 108, 225, scale=0.82 + 0.18 * uc, opacity=env_cert, angle=-7.0)
                paste_centered(comp_im, b_ch, 972, 225, scale=0.82 + 0.18 * uc, opacity=env_cert, angle=7.0)

            cap_y_base = 1710

        # ======================================================================
        # SCENE 6B: ANH KHANG TWO THUMBS UP + BRAND END-CARD (43.53..45.83s)
        # ======================================================================
        else:
            s6b_t0 = segs["s6b_thumbs"]["t0"]
            lf = min(len(v_s6b) - 1, fi - segs["s6b_thumbs"]["f0"])
            dt_e = t - s6b_t0
            rgb = polish_sunny_frame(v_s6b[lf])
            comp_im = fit_cover_target(rgb, W, H, zoom=1.01 + 0.10 * smoothstep(dt_e / 2.30), cx_px=540, cy_px=920).convert("RGBA")

            ue = ease_out_back(min(1.0, dt_e / 0.32))
            paste_centered(comp_im, logo_clean, 540, 195, scale=0.82 + 0.18 * ue)
            sp_go = get_text_sprite("ĐẾN FEEL CHICKEN NGAY!", FONT_POP, 66, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(196, 28, 52), inner_w=5, sheen_prog=dt_e * 0.8)
            paste_centered(comp_im, sp_go, 540, 385, scale=min(1.0, 980.0 / max(1.0, sp_go.width)) * (0.85 + 0.15 * ue))

            ew, eh = 992, 232
            ec = Image.new("RGBA", (ew + 28, eh + 28), (0, 0, 0, 0))
            ed = ImageDraw.Draw(ec)
            ed.rounded_rectangle([8, 8, 20 + ew, 20 + eh], radius=48, fill=(255, 255, 255, 255))
            ed.rounded_rectangle([14, 14, 14 + ew, 14 + eh], radius=42, fill=(218, 36, 62, 252))
            sp_a1 = get_text_sprite("CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt", FONT_SANS_XB, 29, COL_CREAM_5, outer_w=0, inner_w=3)
            sp_a2 = get_text_sprite("Mở cửa: 10:00 – 22:00  •  Hotline: 0796 601 106", FONT_SANS_XB, 31, COL_GOLD_5, outer_w=0, inner_w=3)
            paste_centered(ec, sp_a1, (ew + 28) // 2, 84, scale=min(1.0, (ew - 40) / max(1.0, sp_a1.width)))
            paste_centered(ec, sp_a2, (ew + 28) // 2, 164, scale=min(1.0, (ew - 40) / max(1.0, sp_a2.width)))
            paste_centered(comp_im, ec, 540, 1700, scale=0.88 + 0.12 * ue)
            show_captions = False

        # ======================================================================
        # FACE-SAFE WORD-BY-WORD KAWAII CAPTIONS
        # ======================================================================
        if show_captions:
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    op_g = smoothstep((g["t1"] - t) / 0.16) if (g["t1"] - t) < 0.16 else 1.0
                    y_start = cap_y_base if len(g["lines"]) >= 2 else cap_y_base + 34
                    lh = 74
                    gap = 15
                    for li, ln in enumerate(g["lines"]):
                        w_items = []
                        tot_w = 0
                        for wi, (wtxt, ws, we) in enumerate(ln):
                            is_g = wtxt in GOLD_KEYWORDS
                            is_c = wtxt in CORAL_KEYWORDS
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

        draw_kawaii_frame_border(comp_im, t)

        if test_mode:
            tp = os.path.join(CHECK_DIR, f"fc_v2_test_{len(test_saved):02d}.jpg")
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
        grid = Image.new("RGB", (tw * cols, th * rows), (24, 20, 24))
        for i, (ts, tp) in enumerate(test_saved[:12]):
            im = Image.open(tp).resize((tw, th), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 110, 26], fill=(0, 0, 0))
            d.text((8, 6), f"t={ts:.2f}s", fill=(255, 230, 80))
            grid.paste(im, ((i % cols) * tw, (i // cols) * th))
        gp = os.path.join(CHECK_DIR, "fc_v2_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved 12-frame V2 QA grid:", gp, flush=True)
    else:
        print(f"Finished rendering {total_frames} V2 frames -> {raw_vid_out} in {time.time()-t_start:.1f}s", flush=True)

if __name__ == "__main__":
    main()
