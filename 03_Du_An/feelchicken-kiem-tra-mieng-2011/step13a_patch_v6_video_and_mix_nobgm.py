import json, math, os, shutil, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")

V5_RAW_VID   = os.path.join(PROJ_DIR, "_fc_kute_v5_video_only.mp4")
V6_RAW_VID   = os.path.join(PROJ_DIR, "_fc_kute_v6_video_only.mp4")
VO_MASTER    = os.path.join(STEMS_DIR, "01_Voice_Master_V5.wav")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4")
DRIVE_FINAL  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
FC_FINAL_DIR = r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-kiem-tra-mieng-2011"

W, H = 1080, 1920
FPS = 30.0
SR = 48000

sys.path.insert(0, PROJ_DIR)
from step3b_render_fc_kute import (
    COL_CORAL_5, COL_GOLD_5, COL_CREAM_5,
    FONT_BUBBLE, FONT_POP,
    GOLD_KEYWORDS, CORAL_KEYWORDS, POP_EMPHASIS,
    smoothstep, ease_out_cubic, ease_out_back, smooth_env,
    polish_sunny_frame, get_font, get_text_sprite, paste_centered,
    draw_pill_banner, build_caption_groups, load_all_frames_rgb
)
from step8_render_fc_v2_masterpiece import fit_cover_target, draw_tiktok_pov_text
from step10b_render_fc_v3 import step_zoom
from step10c_mix_and_export_fc_v3 import decode_stereo_f32, save_wav_16, load_sfx_bank, stamp

def render_s2_patch(nostalgia_vid_path):
    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v5.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    cap_groups = build_caption_groups(tm["words"])

    v_s2        = load_all_frames_rgb(os.path.join(AROLL_DIR, "v5_cc_s2_table.mp4"), W, H)
    v_meme_pray = load_all_frames_rgb(os.path.join(MEDIA_DIR, "FC_v2_meme_pray_vid.mp4"), W, H)
    v_vn_real   = load_all_frames_rgb(nostalgia_vid_path, W, H)

    f0 = segs["s2_table"]["f0"]
    f1 = segs["s2_table"]["f1"]
    s2_t0 = segs["s2_table"]["t0"]

    out_frames = []
    for fi in range(f0, f1):
        t = fi / FPS
        show_captions = True
        cap_y_base = 1560
        lf = min(len(v_s2) - 1, fi - f0)
        rgb_k = v_s2[lf]

        t_pov_in  = s2_t0 + 1.53
        t_pov_out = s2_t0 + 4.91
        t_nost_in = s2_t0 + 6.95

        if t < t_pov_in:
            z_k = step_zoom(t, 1.12, [(s2_t0 + 0.80, 1.18, 0.18)])
            comp_im = fit_cover_target(rgb_k, W, H, zoom=z_k, cx_px=594, cy_px=1120).convert("RGBA")
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
                u_mem = smoothstep(min(1.0, (t - t_nost_in) / 0.24))
                idx_vn = int((t - t_nost_in) * FPS) % len(v_vn_real)
                # Keep authentic raw phone camera colors — NO golden AI tint!
                mem_im = fit_cover_target(v_vn_real[idx_vn], W, H, zoom=1.01, cx_px=540, cy_px=960).convert("RGBA")
                comp_im = Image.blend(khang_im, mem_im, u_mem)
                draw_pill_banner(comp_im, "KÝ ỨC TUỔI HỌC TRÒ 20/11", 540, 138, (232, 48, 76), COL_GOLD_5, fsz=29, opacity=u_mem)
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

        if show_captions:
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    op_g = smoothstep((g["t1"] - t) / 0.15) if (g["t1"] - t) < 0.15 else 1.0
                    y_start = cap_y_base if len(g["lines"]) >= 2 else cap_y_base + 34
                    lh, gap = 74, 15
                    for li, ln in enumerate(g["lines"]):
                        w_items, tot_w = [], 0
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
        out_frames.append(np.array(comp_im.convert("RGB"), dtype=np.uint8))

    # Save QA preview frame at t=12.75s
    qa_im = Image.fromarray(out_frames[min(len(out_frames) - 1, int(round((12.75 - s2_t0) * FPS)))])
    qa_im.save(os.path.join(CHECK_DIR, "v6_new_image3_preview.jpg"), quality=92)
    return f0, f1, out_frames

def splice_and_mix_nobgm(nostalgia_vid_path):
    t0 = time.time()
    f0, f1, s2_frames = render_s2_patch(nostalgia_vid_path)
    print(f"Rendered {len(s2_frames)} patched Scene 2 frames in {time.time()-t0:.1f}s!", flush=True)

    # Stream V5_RAW_VID frames and replace [f0..f1) cleanly into V6_RAW_VID!
    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v5.json"), encoding="utf-8"))
    total_frames = tm["total_frames"]
    segs = {s["id"]: s for s in tm["segments"]}
    vid_dur = float(tm["total_dur"])

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", V5_RAW_VID, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", V6_RAW_VID
    ], stdin=subprocess.PIPE)

    fbytes = W * H * 3
    for fi in range(total_frames):
        buf = dec.stdout.read(fbytes)
        if f0 <= fi < f1:
            enc.stdin.write(s2_frames[fi - f0].tobytes())
        else:
            enc.stdin.write(buf)
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()
    print(f"Spliced full {total_frames}-frame V6 video -> {V6_RAW_VID} in {time.time()-t0:.1f}s!", flush=True)

    # MIX CLEAN VOICEOVER + STUDIO SFX ONLY (ZERO OLD BGM — "chỉ cần tắt nhạc kia là được"!)
    N = int(round(vid_dur * SR))
    vo = decode_stereo_f32(VO_MASTER, dur_limit=vid_dur, af="loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    bank = load_sfx_bank()
    sfx = np.zeros((N, 2), dtype=np.float32)

    s2_0  = segs["s2_table"]["t0"]
    s3_0  = segs["s3_program"]["t0"]
    s4_0  = segs["s4_questions"]["t0"]
    s5_0  = segs["s5_gifts"]["t0"]
    s6a_0 = segs["s6a_outro"]["t0"]
    s6b_0 = segs["s6b_thumbs"]["t0"]
    s6c_0 = segs["s6c_storefront"]["t0"]

    cues = [
        ("tlh_star_open", 0.12, -14.5, 0.00, False),
        ("tlh_slap_crisp",1.41,  -7.2, +0.10, True),
        ("tlh_thud_wood", 1.41,  -7.8, +0.08, True),
        ("tlh_whip_turn", 3.06,  -9.5, +0.15, True),
        ("tlh_vine_boom", 3.10, -11.5,  0.00, True),
        ("tlh_crickets",  3.18, -15.0,  0.00, False),
        ("tlh_plip",      3.16, -12.5, -0.20, True),
        ("tlh_plip",      3.28, -12.0,  0.00, True),
        ("tlh_boing",     3.40, -11.5, +0.20, True),

        ("tlh_whoosh_tvc",s2_0,        -13.0, 0.00, True),
        ("tlh_whip_turn", s2_0 + 1.53, -10.8, 0.00, True),
        ("tlh_pop1",      s2_0 + 3.48, -10.8, 0.00, True),
        ("tlh_boing",     s2_0 + 4.20, -11.0,+0.10, True),
        ("sk_whoosh",     s2_0 + 4.91, -13.0, 0.00, True),
        ("sk_shimmer",    s2_0 + 6.95, -12.2, 0.00, False),
        ("tlh_pop1",      s2_0 + 6.90, -11.8, 0.00, True),

        ("tlh_star_open", s3_0 + 0.05, -12.5, 0.00, False),
        ("sk_sparkle",    s3_0 + 0.25, -13.5, 0.00, False),
        ("tlh_swoosh",    s3_0 + 2.34, -13.2, 0.00, True),
        ("tlh_swoosh",    s3_0 + 3.51, -13.2, 0.00, True),
        ("tlh_whoosh_tvc",s3_0 + 4.68, -11.2, 0.00, True),
        ("tlh_fireworks", s3_0 + 4.72, -11.8, 0.00, False),
        ("tlh_yay_kids",  s3_0 + 4.82,  -9.8,-0.10, False),
        ("tlh_wow_anime", s3_0 + 6.15, -11.2,+0.15, False),
        ("sk_sparkle",    s3_0 + 4.78, -12.5, 0.00, False),

        ("sk_whoosh",     s4_0 + 0.04, -13.0, 0.00, True),
        ("tlh_swoosh",    s4_0 + 2.13, -12.5, 0.00, True),
        ("tlh_pop1",      s4_0 + 3.32, -11.2,-0.20, True),
        ("tlh_pop2",      s4_0 + 3.70, -11.2,+0.20, True),
        ("tlh_pop1",      s4_0 + 4.08, -11.2,-0.15, True),
        ("tlh_notif",     s4_0 + 4.46, -11.2,+0.15, True),
        ("tlh_pop2",      s4_0 + 4.84, -11.0,-0.10, True),
        ("tlh_boing",     s4_0 + 5.22, -10.5, 0.00, True),

        ("tlh_whoosh_tvc",s5_0 + 0.04, -13.0, 0.00, True),
        ("tlh_ting",      s5_0 + 0.88, -10.2, 0.00, True),
        ("tlh_yeah_cheer",s5_0 + 0.92, -12.5,+0.10, False),
        ("sk_whoosh",     s5_0 + 1.56, -12.8, 0.00, True),
        ("tlh_pop1",      s5_0 + 1.62, -12.2,-0.10, True),
        ("tlh_swoosh",    s5_0 + 2.68, -13.2,+0.10, True),
        ("tlh_pop2",      s5_0 + 2.74, -12.2,+0.10, True),
        ("tlh_swoosh",    s5_0 + 3.80, -13.2,-0.10, True),
        ("tlh_pop1",      s5_0 + 3.86, -12.2,-0.10, True),
        ("sk_whoosh",     s5_0 + 4.92, -12.8, 0.00, True),
        ("sk_sparkle",    s5_0 + 4.98, -13.5, 0.00, False),
        ("tlh_ting",      s5_0 + 7.72, -11.0, 0.00, True),

        ("tlh_whoosh_tvc",s6a_0 + 0.04, -13.0, 0.00, True),
        ("sk_shimmer",    s6a_0 + 0.16, -13.5, 0.00, False),
        ("tlh_swoosh",    s6a_0 + 2.72, -12.8, 0.00, True),
        ("tlh_pop1",      s6a_0 + 2.78, -11.5,-0.15, True),
        ("tlh_pop2",      s6a_0 + 3.24, -11.8,+0.15, True),
        ("tlh_swoosh",    s6a_0 + 4.32, -12.5, 0.00, True),
        ("tlh_boing",     s6a_0 + 4.38, -10.8, 0.00, True),
        ("tlh_wow_anime", s6a_0 + 4.55, -11.8,+0.15, False),
        ("tlh_pop1",      s6b_0 + 0.04, -12.5, 0.00, True),
        ("tlh_whoosh_tvc",s6c_0 + 0.02, -11.8, 0.00, True),
        ("tlh_star_open", s6c_0 + 0.08, -12.0, 0.00, False),
        ("tlh_yay_kids",  s6c_0 + 0.18, -12.2, 0.00, False),
        ("tlh_pop1",      s6c_0 + 0.25, -12.0, 0.00, True),
        ("sk_sparkle",    s6c_0 + 1.85, -13.0, 0.00, False),
    ]
    for k, ts, db, pan, ap in cues:
        stamp(sfx, bank, k, ts, db, pan=pan, align_peak=ap)

    # Pure Voiceover + SFX ONLY (NO BGM!) + soft peak limiter at -1.0 dBTP
    vo_sfx = vo * 0.96 + sfx * 0.88
    raw_mix_p = os.path.join(STEMS_DIR, "_raw_mix_v6_nobgm.wav")
    save_wav_16(raw_mix_p, vo_sfx)

    master_wav = os.path.join(STEMS_DIR, "04_Final_VO_SFX_NoBGM_V6.wav")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", raw_mix_p,
        "-af", "alimiter=limit=0.891:attack=5:release=50",
        "-ar", "48000", "-ac", "2", master_wav
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", V6_RAW_VID, "-i", master_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-movflags", "+faststart", LOCAL_FINAL
    ], check=True)

    for dst in (DRIVE_FINAL, FC_FINAL_DIR, LOCAL_EXPORT):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            shutil.copy2(LOCAL_FINAL, dst)
            print("Synced V6 No-BGM Final MP4 ->", dst, flush=True)
        except PermissionError:
            alt = dst.replace("_FINAL.mp4", "_FINAL_V6_NoBGM.mp4")
            shutil.copy2(LOCAL_FINAL, alt)
            print("File open in CapCut, saved sibling ->", alt, flush=True)

if __name__ == "__main__":
    splice_and_mix_nobgm(sys.argv[1])
