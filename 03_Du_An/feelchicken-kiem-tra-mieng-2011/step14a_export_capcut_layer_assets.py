import json, math, os, subprocess, sys, time, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ_DIR   = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
STEMS_DIR  = os.path.join(PROJ_DIR, "audio_stems")
LAYERS_DIR = os.path.join(PROJ_DIR, "capcut_layers_v6")
os.makedirs(LAYERS_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30.0
SR  = 48000

sys.path.insert(0, PROJ_DIR)
from step3b_render_fc_kute import (
    COL_CORAL_5, COL_GOLD_5, COL_MINT_5, COL_CREAM_5,
    FONT_BUBBLE, FONT_POP, FONT_SANS_XB,
    GOLD_KEYWORDS, CORAL_KEYWORDS,
    ease_out_back, get_font, get_text_sprite, paste_centered,
    load_stickers, get_sticker_badge, draw_pill_banner,
    build_caption_groups, load_all_frames_rgb
)
from step8_render_fc_v2_masterpiece import (
    fit_cover_target, draw_spiky_impact_badge, draw_tiktok_pov_text
)
from step10b_render_fc_v3 import (
    draw_firework_explosion, build_clean_modern_2011_header, make_stacking_quiz_card
)
from step11a_render_fc_v4_master import (
    load_all_frames_gray, DIM_WALL_IM, GLOW_HALO_IM,
    draw_behind_head_orbital_overlay, draw_bouncy_callout_pill
)
from step12b_render_fc_v5_master import (
    draw_kawaii_heart, build_ultra_kute_storefront_card
)

def save_png(im, fname):
    p = os.path.join(LAYERS_DIR, fname)
    im.save(p)
    return p

def write_prores4444_alpha(fname, n_frames, render_fn):
    out_p = os.path.join(LAYERS_DIR, fname)
    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-an", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
        out_p
    ], stdin=subprocess.PIPE)
    for fi in range(n_frames):
        rgba = render_fn(fi)
        enc.stdin.write(np.array(rgba, dtype=np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"  Exported ProRes 4444 Alpha ({n_frames:3d}f) -> {fname}", flush=True)
    return out_p

def main():
    t0 = time.time()
    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v5.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    cap_groups = build_caption_groups(tm["words"])
    stickers = load_stickers()
    logo_clean = stickers["logo_fc"].copy()
    logo_clean.thumbnail((260, 260), Image.Resampling.LANCZOS)

    print("1. Exporting crisp 1080x1920 RGBA PNG Overlay Layers...", flush=True)

    # Dark neon background for Scene 3B chalkboard
    ref_neon_im = Image.open(os.path.join(MEDIA_DIR, "ref_fc_bg_neon_9x16.jpg")).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    dark_neon_bg = Image.alpha_composite(
        ref_neon_im.filter(ImageFilter.GaussianBlur(radius=14)).convert("RGBA"),
        Image.new("RGBA", (W, H), (22, 12, 18, 128))
    )
    save_png(dark_neon_bg, "bg_dark_neon_cs1.png")

    # Scene 1 PNG overlays
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_pill_banner(im, "LỚP HỌC FEEL CHICKEN • 20/11", 540, 102, (232, 48, 72), COL_GOLD_5, fsz=29)
    save_png(im, "ov_s1_hdr.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bw, bh = 840, 196
    bub = Image.new("RGBA", (bw + 32, bh + 48), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bub)
    bd.rounded_rectangle([12, 12, 20 + bw, 20 + bh], radius=50, fill=(255, 255, 255, 255))
    bd.rounded_rectangle([18, 18, 14 + bw, 14 + bh], radius=44, fill=(255, 249, 238, 252), outline=(238, 56, 82, 255), width=6)
    bd.polygon([(250, 14 + bh), (305, 14 + bh), (235, 42 + bh)], fill=(255, 249, 238, 255), outline=(238, 56, 82, 255))
    sp_k1 = get_text_sprite("THÀNH ƠI!!", FONT_BUBBLE, 50, COL_CORAL_5, outer_w=8, inner_w=4)
    sp_k2 = get_text_sprite("LÊN BẢNG KIỂM TRA MIỆNG!", FONT_POP, 46, COL_GOLD_5, outer_w=8, inner_w=4)
    paste_centered(bub, sp_k1, (bw + 32) // 2, 68)
    paste_centered(bub, sp_k2, (bw + 32) // 2, 142, scale=min(1.0, (bw - 44) / max(1.0, sp_k2.width)))
    paste_centered(im, bub, 540, 312, angle=-1.2)
    save_png(im, "ov_s1_bub_khang.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_spiky_impact_badge(im, "RẦM!!", 695, 1115, scale=1.0)
    save_png(im, "ov_s1_ram.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for qi, (qx, qy, qang) in enumerate([(355, 425, -14.0), (540, 365, 2.0), (725, 425, 14.0)]):
        sp_q = get_text_sprite("?", FONT_POP, 88 if qi == 1 else 74, COL_GOLD_5 if qi == 1 else COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(48, 18, 24), inner_w=4)
        paste_centered(im, sp_q, qx, qy, angle=qang)
    save_png(im, "ov_s1_qmarks.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sw_w, sw_h = 540, 124
    sbub = Image.new("RGBA", (sw_w + 24, sw_h + 24), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sbub)
    sd.rounded_rectangle([6, 6, 18 + sw_w, 18 + sw_h], radius=48, fill=(255, 255, 255, 255))
    sd.rounded_rectangle([12, 12, 12 + sw_w, 12 + sw_h], radius=42, fill=(32, 44, 66, 244), outline=(102, 206, 255, 255), width=5)
    sp_em = get_text_sprite("Em... em... ơ kìa?!", FONT_BUBBLE, 46, COL_MINT_5, outer_stroke=(24, 32, 48), outer_w=6, inner_w=3)
    paste_centered(sbub, sp_em, (sw_w + 24) // 2, (sw_h + 24) // 2, scale=min(1.0, (sw_w - 28) / max(1.0, sp_em.width)))
    paste_centered(im, sbub, 540, 1515)
    save_png(im, "ov_s1_bub_thanh.png")

    # Scene 2 PNG overlays
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    top_g = np.zeros((H, W, 4), dtype=np.uint8)
    yg = np.clip(1.0 - np.arange(H, dtype=np.float32) / 470.0, 0.0, 1.0)
    top_g[:, :, 3] = (yg * 105.0).astype(np.uint8)[:, None]
    im = Image.alpha_composite(im, Image.fromarray(top_g, "RGBA"))
    draw_tiktok_pov_text(im, ["POV: Cô giáo kiểm tra miệng đến", "đứa thứ 5 rồi vẫn chưa có dấu", "hiệu dừng lại"], cy_top=170)
    save_png(im, "ov_s2_pov.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sp_s = get_text_sprite("Hồi xưa đi học nghe đến chữ...", FONT_BUBBLE, 48, COL_CREAM_5, outer_stroke=(32, 14, 18), outer_w=8, inner_w=4)
    paste_centered(im, sp_s, 540, 1600, scale=min(1.0, 960.0 / max(1.0, sp_s.width)))
    save_png(im, "ov_s2_hoixua.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sp_ktm1 = get_text_sprite("KIỂM TRA MIỆNG", FONT_POP, 96, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(54, 18, 24), inner_w=5, glow_col=(255, 206, 68), glow_rad=12)
    paste_centered(im, sp_ktm1, 540, 1485, scale=min(1.0, 990.0 / max(1.0, sp_ktm1.width)))
    save_png(im, "ov_s2_ktm1.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sp_rung = get_text_sprite("RUNG CẦM CẬP!!", FONT_BUBBLE, 76, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(54, 18, 24), inner_w=4)
    paste_centered(im, sp_rung, 540, 1640)
    save_png(im, "ov_s2_rung.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_pill_banner(im, "KÝ ỨC TUỔI HỌC TRÒ 20/11", 540, 138, (232, 48, 76), COL_GOLD_5, fsz=29)
    save_png(im, "ov_s2_nost_hdr.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sp_ktm2 = get_text_sprite("KIỂM TRA MIỆNG", FONT_POP, 90, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=12, inner_stroke=(54, 18, 24), inner_w=5, glow_col=(255, 206, 68), glow_rad=10)
    paste_centered(im, sp_ktm2, 540, 1525, scale=min(1.0, 960.0 / max(1.0, sp_ktm2.width)))
    save_png(im, "ov_s2_ktm2.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sp_bh = get_text_sprite("thấy BỒI HỒI GHÊ luôn á!", FONT_BUBBLE, 58, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=10, inner_stroke=(54, 18, 24), inner_w=4)
    paste_centered(im, sp_bh, 540, 1665, scale=min(1.0, 950.0 / max(1.0, sp_bh.width)))
    save_png(im, "ov_s2_boihoi.png")

    # Scene 3 PNG overlays
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_centered(im, build_clean_modern_2011_header(logo_clean), 540, 215)
    save_png(im, "ov_s3a_header_2011.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
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
    paste_centered(board, get_text_sprite("★ MINIGAME ĐẶC BIỆT NGÀY 20/11 ★", FONT_SANS_XB, 30, COL_MINT_5, outer_w=0, inner_w=3), cx_b, 116)
    sp_m3 = get_text_sprite("KIỂM TRA MIỆNG", FONT_POP, 100, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(58, 24, 18), inner_w=5, glow_col=(255, 212, 75), glow_rad=14)
    paste_centered(board, sp_m3, cx_b, 270, scale=min(1.0, (bw - 120) / max(1.0, sp_m3.width)))
    paste_centered(board, get_text_sprite("TRẢ LỜI ĐÚNG", FONT_BUBBLE, 66, COL_CREAM_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(236, 48, 76), inner_w=4), cx_b, 462)
    sp_s32 = get_text_sprite("NHẬN QUÀ NGAY!", FONT_POP, 74, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(68, 18, 28), inner_w=4)
    paste_centered(board, sp_s32, cx_b, 592, scale=min(1.0, (bw - 90) / max(1.0, sp_s32.width)))
    paste_centered(im, board, 540, 945)
    cloud_m = Image.new("RGBA", (290, 290), (0, 0, 0, 0))
    ImageDraw.Draw(cloud_m).ellipse([26, 26, 264, 264], fill=(255, 252, 244, 255), outline=(242, 168, 96, 255), width=6)
    paste_centered(cloud_m, logo_clean, 145, 145, scale=0.90)
    paste_centered(im, cloud_m, 540, 530)
    save_png(im, "ov_s3b_chalkboard.png")

    # Scene 4 PNG overlays (2 headers + 6 individual Quiz Cards!)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_pill_banner(im, "HŨ BỐC THĂM CÂU HỎI 20/11", 540, 118, (232, 42, 68), COL_GOLD_5, fsz=30)
    save_png(im, "ov_s4_hdr_jar.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_pill_banner(im, "100 CÂU HỎI HỌC ĐƯỜNG & ĐỐ MẸO", 540, 118, (232, 42, 68), COL_GOLD_5, fsz=29)
    save_png(im, "ov_s4_hdr_100.png")

    quiz_stack_specs = [
        ("LỊCH SỬ #01",        "Ngày Nhà giáo Việt Nam là ngày nào?",          "Đáp án: 20/11",         (44, 182, 142), 1535, -3.0),
        ("NGỮ VĂN #41",         "Ai là tác giả tác phẩm Lão Hạc?",              "Đáp án: Nam Cao",       (242, 136, 48), 1270, +2.6),
        ("ĐỊA LÝ #18",          "Đường nào ở Nha Trang có Feel Chicken ngon?",  "38 Nguyễn Đình Chiểu!", (56, 152, 232), 1005, -2.4),
        ("TOÁN HỌC #55",        "1 + 1 bằng mấy khi đi ăn cùng hội bạn thân?",  "Gấp đôi niềm vui!",     (168, 92, 232),  740, +2.8),
        ("HÓA HỌC VUI #72",     "Chất gì làm gà rán Feel Chicken gây nghiện?",   "Sốt Hàn Quốc!",         (236, 78, 138),  475, -2.0),
        ("ĐỐ MẸO LẮT LÉO #100", "Gà 1 chân nặng 2kg, đứng 2 chân mấy kg?",      "Vẫn 2 kg nha!!",        (232, 42, 68),  1015, +1.5),
    ]
    for idx, (tg, tx, an, col, cy, ang) in enumerate(quiz_stack_specs):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        qspr = make_stacking_quiz_card(tg, tx, an, col, qw=966 if idx == 5 else 936, qh=248 if idx == 5 else 218)
        paste_centered(im, qspr, 540, cy, angle=ang)
        save_png(im, f"ov_quiz_card_{idx+1:02d}.png")

    # Scene 5 PNG overlays
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_centered(im, get_text_sprite("Trả lời đúng...", FONT_BUBBLE, 62, COL_CREAM_5, outer_stroke=(36, 14, 20), outer_w=9, inner_w=4), 540, 1520)
    save_png(im, "ov_s5a_tld.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sp_cq = get_text_sprite("CÓ QUÀ!!", FONT_POP, 122, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=15, inner_stroke=(196, 24, 52), inner_w=6, glow_col=(255, 212, 68), glow_rad=15)
    paste_centered(im, sp_cq, 540, 1520)
    paste_centered(im, get_sticker_badge(stickers, "FC_st_gift_chicken", 180, (255, 102, 128)), 865, 1300, angle=8.0)
    save_png(im, "ov_s5a_coqua.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_pill_banner(im, "TOÀN QUÀ NGON TẠI CƠ SỞ 1!", 540, 122, (228, 38, 64), COL_GOLD_5, fsz=30)
    save_png(im, "ov_s5b_hdr.png")

    for pidx, (ptxt, pcol, pts, pfsz, pang) in enumerate([
        ("8 MIẾNG GÀ ĐẪM SỐT!!",          (226, 38, 66),  COL_GOLD_5,  44, -2.0),
        ("GÀ SỐT HÀN QUỐC CỰC NGON!!",    (238, 118, 38), COL_CREAM_5, 42, +2.0),
        ("TOKBOKKI • SALAD • KHOAI CHIÊN!",(42, 168, 128),COL_GOLD_5,  40, -1.8),
    ], 1):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_bouncy_callout_pill(im, ptxt, 540, 1365, pcol, pts, 0.5, 0.0, fsz=pfsz, base_ang=pang)
        save_png(im, f"ov_s5b_pill{pidx}.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_pill_banner(im, "38 NGUYỄN ĐÌNH CHIỂU • NHA TRANG", 540, 118, (232, 42, 68), COL_GOLD_5, fsz=28)
    save_png(im, "ov_s5c_hdr.png")

    # Scene 6 PNG overlays
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cw_c, ch_c = 956, 236
    cert = Image.new("RGBA", (cw_c + 28, ch_c + 28), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cert)
    cd.rounded_rectangle([8, 8, 20 + cw_c, 20 + ch_c], radius=46, fill=(255, 255, 255, 255))
    cd.rounded_rectangle([15, 15, 13 + cw_c, 13 + ch_c], radius=40, fill=(255, 249, 236, 248), outline=(232, 46, 74, 255), width=5)
    paste_centered(cert, get_text_sprite("★ DANH HIỆU CAO QUÝ 20/11 ★", FONT_SANS_XB, 23, [(224, 42, 68)] * 5, outer_w=0, inner_w=0, shadow_alpha=0), (cw_c + 28) // 2, 54)
    sp_c2 = get_text_sprite("HỌC SINH GIỎI", FONT_POP, 70, COL_GOLD_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(58, 20, 26), inner_w=4)
    paste_centered(cert, sp_c2, (cw_c + 28) // 2, 132, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c2.width)))
    sp_c3 = get_text_sprite("RỦ HỘI BẠN ĐẾN FEEL CHICKEN SĂN QUÀ NGAY!", FONT_SANS_XB, 23, [(58, 24, 30)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(cert, sp_c3, (cw_c + 28) // 2, 204, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c3.width)))
    paste_centered(im, cert, 540, 198)
    save_png(im, "ov_s6a_cert.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_bouncy_callout_pill(im, "XÉ ĐÙI GÀ NÓNG HỔI!!", 330, 1210, (232, 42, 68), COL_GOLD_5, 0.5, 0.0, fsz=40, base_ang=-5.5)
    draw_bouncy_callout_pill(im, "THƠM NỨC MŨI!!", 780, 1345, (242, 128, 42), COL_CREAM_5, 0.5, 0.0, fsz=40, base_ang=+5.5)
    save_png(im, "ov_s6a_pull_callouts.png")

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_centered(im, logo_clean, 540, 185)
    sp_go = get_text_sprite("GHÉ FEEL CHICKEN NGAY!", FONT_POP, 66, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(196, 28, 52), inner_w=5)
    paste_centered(im, sp_go, 540, 365, scale=min(1.0, 980.0 / max(1.0, sp_go.width)))
    save_png(im, "ov_s6c_top_logo_cta.png")

    # Export Individual Kawaii Subtitle Phrase PNGs (for all active spoken caption windows!)
    sub_manifest = []
    # Windows where custom hero typography replaces standard captions:
    hero_windows = [
        (0.0, 4.567),
        (6.097, 9.477),
        (11.467, 13.467),
        (18.147, 21.967),
        (27.933, 29.493),
        (44.567, 49.0),
    ]
    for gi, g in enumerate(cap_groups):
        gt0, gt1 = g["t0"], g["t1"]
        # Clip against hero windows so subtitles never collide with hero cards!
        s_t, e_t = gt0, gt1
        skip = False
        for hw0, hw1 in hero_windows:
            if s_t >= hw0 and e_t <= hw1:
                skip = True
                break
            if hw0 < s_t < hw1:
                s_t = hw1
            if hw0 < e_t < hw1:
                e_t = hw0
        if skip or (e_t - s_t) < 0.18:
            continue

        # Choose scene-appropriate Y
        mid_t = (s_t + e_t) * 0.5
        if mid_t < 13.47:
            cy_b = 1560
        elif mid_t < 21.97:
            cy_b = 1605
        elif mid_t < 27.93:
            cy_b = 1725
        elif mid_t < 36.83:
            cy_b = 1555
        elif mid_t < 42.77:
            cy_b = 1655
        else:
            cy_b = 1560

        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        y_start = cy_b if len(g["lines"]) >= 2 else cy_b + 34
        lh, gap = 74, 15
        raw_txt_lines = []
        for li, ln in enumerate(g["lines"]):
            raw_txt_lines.append(" ".join(w[0] for w in ln))
            w_items, tot_w = [], 0
            for wi, (wtxt, ws, we) in enumerate(ln):
                is_g = wtxt in GOLD_KEYWORDS
                is_c = wtxt in CORAL_KEYWORDS or wtxt == "rung"
                k_sc = 1.14 if (is_g or is_c) else 1.0
                stops = COL_GOLD_5 if is_g else (COL_CORAL_5 if is_c else COL_CREAM_5)
                glow_c = (255, 208, 68) if is_g else ((255, 96, 126) if is_c else None)
                fsz = 54.0 * k_sc
                sp = get_text_sprite(wtxt, FONT_BUBBLE, fsz, stops, outer_stroke=(255, 255, 255), outer_w=8, inner_stroke=(44, 18, 24), inner_w=5, glow_col=glow_c, glow_rad=7 if glow_c else 0, shadow_alpha=90)
                adv = int(ImageDraw.Draw(im).textlength(wtxt, font=get_font(FONT_BUBBLE, fsz))) + 6
                w_items.append((sp, adv))
                tot_w += adv + (gap if wi > 0 else 0)
            cur_x = max(48, min(W - 48 - tot_w, 540 - tot_w // 2))
            cur_y = y_start + li * lh
            for sp, adv in w_items:
                paste_centered(im, sp, cur_x + adv // 2, cur_y)
                cur_x += adv + gap

        fn_sub = f"ov_sub_{gi:02d}.png"
        save_png(im, fn_sub)
        sub_manifest.append({"file": fn_sub, "t0": round(s_t, 3), "t1": round(e_t, 3), "text": "\n".join(raw_txt_lines)})

    json.dump(sub_manifest, open(os.path.join(LAYERS_DIR, "subtitles_manifest.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"  Exported {len(sub_manifest)} individual Kawaii subtitle PNGs!", flush=True)

    # --------------------------------------------------------------------------
    # 2. Export Animated ProRes 4444 Alpha (.mov) Video Overlays!
    # --------------------------------------------------------------------------
    print("2. Exporting ProRes 4444 Alpha (.mov) Video Overlays & RVM Cutouts...", flush=True)

    # 2A & 2B: RVM Foreground Cutouts of Anh Khang (Scene 5A: 47f, Scene 5C: 119f)
    v_s5a = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s5a_khang.mp4"), W, H)
    m_s5a = load_all_frames_gray(os.path.join(AROLL_DIR, "v5_cc_s5a_matte.mp4"), W, H)
    def rf_fg5a(fi):
        rgb = Image.fromarray(v_s5a[min(len(v_s5a)-1, fi)], "RGB")
        alf = Image.fromarray(m_s5a[min(len(m_s5a)-1, fi)], "L").filter(ImageFilter.GaussianBlur(radius=1.1))
        rgba = rgb.convert("RGBA")
        rgba.putalpha(alf)
        return rgba
    write_prores4444_alpha("fg_s5a_khang_cutout.mov", 47, rf_fg5a)

    v_s5c = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s5c_khang.mp4"), W, H)
    m_s5c = load_all_frames_gray(os.path.join(AROLL_DIR, "v5_cc_s5c_matte.mp4"), W, H)
    def rf_fg5c(fi):
        rgb = Image.fromarray(v_s5c[min(len(v_s5c)-1, fi)], "RGB")
        alf = Image.fromarray(m_s5c[min(len(m_s5c)-1, fi)], "L").filter(ImageFilter.GaussianBlur(radius=1.1))
        rgba = rgb.convert("RGBA")
        rgba.putalpha(alf)
        return rgba
    write_prores4444_alpha("fg_s5c_khang_cutout.mov", 119, rf_fg5c)

    # 2C: Scene 5A Behind-Head Aura + Orbital Rings + "SĂN QUÀ CỰC ĐỈNH" (47f)
    def rf_bh5a(fi):
        t = segs["s5_gifts"]["t0"] + fi / FPS
        ov = Image.alpha_composite(DIM_WALL_IM.copy(), GLOW_HALO_IM)
        draw_behind_head_orbital_overlay(ov, t, cx=540, cy=695, env=1.0)
        sp = get_text_sprite("SĂN QUÀ CỰC ĐỈNH", FONT_POP, 88, COL_MINT_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(36, 18, 24), inner_w=5, sheen_prog=(fi / FPS) * 0.9)
        paste_centered(ov, sp, 540, 415, scale=min(1.0, 960.0 / max(1.0, sp.width)))
        return ov
    write_prores4444_alpha("ov_s5a_behind_head_aura.mov", 47, rf_bh5a)

    # 2D: Scene 5C Behind-Head Aura + Orbital Rings + Bobbing Badges + Animated 3D Typography + Fireworks (119f)
    b_l = get_sticker_badge(stickers, "FC_st_prof_chick", 172, (255, 198, 68))
    b_r = get_sticker_badge(stickers, "FC_st_score10", 172, (255, 108, 138))
    def rf_bh5c(fi):
        t_start_5c = segs["s5_gifts"]["t0"] + 4.92
        t = t_start_5c + fi / FPS
        dt_5c = fi / FPS
        t_2011_hit = segs["s5_gifts"]["t0"] + 7.72
        ov = Image.alpha_composite(DIM_WALL_IM.copy(), GLOW_HALO_IM)
        draw_behind_head_orbital_overlay(ov, t, cx=540, cy=710, env=1.0)
        paste_centered(ov, b_l, 185, 690 + math.sin(t * 3.8) * 14.0, angle=-8.0 + math.sin(t * 2.5) * 4.0)
        paste_centered(ov, b_r, 895, 690 + math.cos(t * 3.8) * 14.0, angle=+8.0 - math.sin(t * 2.5) * 4.0)
        if t < t_2011_hit:
            u_in = ease_out_back(min(1.0, dt_5c / 0.28), s=1.28)
            sp_t1 = get_text_sprite("AI ĐẾN QUÁN", FONT_BUBBLE, 76, COL_CREAM_5, outer_stroke=(226, 38, 66), outer_w=11, inner_stroke=(48, 14, 22), inner_w=4)
            sp_t2 = get_text_sprite("CŨNG CÓ QUÀ!", FONT_POP, 104, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(58, 18, 26), inner_w=5, glow_col=(255, 208, 68), glow_rad=12, sheen_prog=dt_5c * 0.75)
            paste_centered(ov, sp_t1, 540, 320 + (1.0 - min(1.0, u_in)) * -40.0, scale=0.84 + 0.16 * u_in)
            paste_centered(ov, sp_t2, 540, 465, scale=min(1.0, 980.0 / max(1.0, sp_t2.width)) * (0.84 + 0.16 * u_in))
        else:
            dt_20 = t - t_2011_hit
            u_20 = ease_out_back(min(1.0, dt_20 / 0.22), s=1.38)
            draw_firework_explosion(ov, 250, 330, t, t_2011_hit + 0.05, radius_max=230, main_col=(255, 218, 68), alt_col=(255, 92, 132))
            draw_firework_explosion(ov, 830, 320, t, t_2011_hit + 0.18, radius_max=230, main_col=(88, 238, 192), alt_col=(255, 214, 72))
            sp_h1 = get_text_sprite("ÁP DỤNG ĐẾN HẾT", FONT_BUBBLE, 66, COL_MINT_5, outer_stroke=(36, 16, 22), outer_w=10, inner_w=4)
            sp_h2 = get_text_sprite("NGÀY 20/11!", FONT_POP, 116, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=14, inner_stroke=(196, 24, 52), inner_w=6, glow_col=(255, 212, 68), glow_rad=14, sheen_prog=dt_20 * 1.1)
            paste_centered(ov, sp_h1, 540, 320, scale=0.85 + 0.15 * u_20)
            paste_centered(ov, sp_h2, 540, 465, scale=min(1.0, 980.0 / max(1.0, sp_h2.width)) * (0.82 + 0.18 * u_20))
        return ov
    write_prores4444_alpha("ov_s5c_behind_head_aura.mov", 119, rf_bh5c)

    # 2E: Scene 3A Floating Kawaii Hearts (70f)
    def rf_hearts(fi):
        t = fi / FPS
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dk = ImageDraw.Draw(ov)
        for hi, (hx, hy0, hsz) in enumerate([(125, 520, 16), (955, 495, 18), (155, 1380, 15), (925, 1360, 17)]):
            draw_kawaii_heart(dk, hx, hy0 + math.sin(t * 3.6 + hi * 1.4) * 18.0, hsz, (255, 122, 156, 225), outline_rgba=(255, 255, 255, 240))
        return ov
    write_prores4444_alpha("ov_s3a_kawaii_hearts.mov", 70, rf_hearts)

    # 2F: Scene 3B Celebratory Fireworks (114f)
    def rf_fw3b(fi):
        t = fi / FPS
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_firework_explosion(ov, 215, 310, t, 0.12, radius_max=260, main_col=(255, 218, 68), alt_col=(255, 92, 132))
        draw_firework_explosion(ov, 865, 285, t, 0.34, radius_max=275, main_col=(88, 238, 192), alt_col=(255, 214, 72))
        draw_firework_explosion(ov, 540, 215, t, 0.72, radius_max=300, main_col=(255, 112, 148), alt_col=(110, 205, 255))
        draw_firework_explosion(ov, 235, 1520, t, 1.25, radius_max=240, main_col=(255, 218, 68), alt_col=(88, 238, 192))
        draw_firework_explosion(ov, 855, 1500, t, 1.65, radius_max=250, main_col=(255, 96, 128), alt_col=(255, 224, 88))
        draw_firework_explosion(ov, 540, 260, t, 2.25, radius_max=290, main_col=(255, 218, 68), alt_col=(255, 92, 132))
        return ov
    write_prores4444_alpha("ov_s3b_fireworks.mov", 114, rf_fw3b)

    # 2G: Scene 6A Energetic Bouncing Crispy Bite Texts (49f)
    def rf_bite(fi):
        dt = fi / FPS
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        u_bt = ease_out_back(min(1.0, dt / 0.18), s=1.55)
        jmp_y = -abs(math.sin(dt * 11.5)) * 22.0
        sp_g = get_text_sprite("GIÒN RỤM RỤM!!", FONT_POP, 88, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=13, inner_stroke=(198, 24, 52), inner_w=5, glow_col=(255, 212, 68), glow_rad=12, sheen_prog=dt * 1.2)
        draw_bouncy_callout_pill(ov, "ĐẪM SỐT HÀN!!", 255, 1185, (232, 42, 68), COL_CREAM_5, dt, 0.10, fsz=38, base_ang=-6.5)
        draw_bouncy_callout_pill(ov, "ĂN LÀ MÊ!!", 835, 1200, (42, 174, 132), COL_GOLD_5, dt, 0.28, fsz=40, base_ang=+6.5)
        paste_centered(ov, sp_g, 540, 1385 + jmp_y, scale=min(1.0, 960.0 / max(1.0, sp_g.width)) * (0.78 + 0.22 * u_bt), angle=-2.5 + math.sin(dt * 9.0) * 2.5)
        return ov
    write_prores4444_alpha("ov_s6a_bite_gionrum.mov", 49, rf_bite)

    # 2H: Scene 6C Fireworks + Ultra-Kute Kawaii Cloud/Sticker Address Card (117f)
    kute_card = build_ultra_kute_storefront_card()
    m_left    = get_sticker_badge(stickers, "FC_st_prof_chick", 142, (255, 198, 68))
    m_right   = get_sticker_badge(stickers, "FC_st_cheers_cups", 142, (255, 112, 146))
    def rf_s6c_fw(fi):
        dt = fi / FPS
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_firework_explosion(ov, 235, 290, dt, 0.12, radius_max=235, main_col=(255, 218, 68), alt_col=(255, 92, 132))
        draw_firework_explosion(ov, 845, 270, dt, 0.34, radius_max=235, main_col=(88, 238, 192), alt_col=(255, 214, 72))
        draw_firework_explosion(ov, 540, 235, dt, 1.85, radius_max=260, main_col=(255, 112, 148), alt_col=(255, 224, 88))
        return ov
    write_prores4444_alpha("ov_s6c_fireworks.mov", 117, rf_s6c_fw)

    def rf_s6c_card(fi):
        dt = fi / FPS
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ue = ease_out_back(min(1.0, dt / 0.32), s=1.28)
        paste_centered(ov, kute_card, 540, 1690 + math.sin(dt * 4.2) * 5.0, scale=0.84 + 0.16 * ue)
        paste_centered(ov, m_left,  118, 1545 + math.sin(dt * 5.5) * 8.0, scale=0.80 + 0.20 * ue, angle=-8.0 + math.sin(dt * 3.5) * 4.0)
        paste_centered(ov, m_right, 962, 1545 + math.cos(dt * 5.5) * 8.0, scale=0.80 + 0.20 * ue, angle=+8.0 - math.sin(dt * 3.5) * 4.0)
        return ov
    write_prores4444_alpha("ov_s6c_kute_endcard.mov", 117, rf_s6c_card)

    # --------------------------------------------------------------------------
    # 3. Export Clean Per-Segment Voiceover Stems from 01_Voice_Master_V5.wav!
    # --------------------------------------------------------------------------
    print("3. Exporting clean per-segment Voiceover WAV stems...", flush=True)
    vo5_p = os.path.join(STEMS_DIR, "01_Voice_Master_V5.wav")
    with wave.open(vo5_p, "rb") as wf:
        vo_pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).reshape((-1, 2))

    for s in tm["segments"]:
        sid = s["id"]
        if sid == "s6c_storefront":
            continue
        i0 = int(round(s["t0"] * SR))
        i1 = int(round(s["t1"] * SR))
        sub_pcm = vo_pcm[i0:i1]
        wp = os.path.join(LAYERS_DIR, f"vo_{sid}.wav")
        with wave.open(wp, "wb") as wf:
            wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes(sub_pcm.tobytes())

    print(f"DONE exporting all CapCut V6 Layer Assets in {time.time()-t0:.1f}s!", flush=True)

if __name__ == "__main__":
    main()
