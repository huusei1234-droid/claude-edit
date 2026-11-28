import concurrent.futures, copy, json, math, os, re, shutil, subprocess, sys, time, uuid
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"d:\AI\full studio\output\htpm5-261121")
import render_htpm5_master as h5
import mix_htpm5_final as m5

BATCH_DIR  = r"d:\AI\full studio\output\htpm-batch-261123"
KB06_DIR   = os.path.join(BATCH_DIR, "kb06")
AROLL_DIR  = os.path.join(KB06_DIR, "aroll_11x")
MEDIA_DIR  = os.path.join(KB06_DIR, "media")
STEMS_DIR  = os.path.join(KB06_DIR, "audio_stems_11x")
CHECK_DIR  = os.path.join(KB06_DIR, "check_11x")
os.makedirs(CHECK_DIR, exist_ok=True)

FONTS_DIR     = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_SUB_MAIN = os.path.join(FONTS_DIR, "AsapCondensed-Bold.ttf")
RISER_01_LOCAL= os.path.join(BATCH_DIR, "riser_01_local.mp3")
TOKYO_BGM     = r"D:\AI\full studio\phong-cach\talking-head\assets_dung_chung\bgm\tokyo_drift_remix.mp3"

DRAFT_DIR     = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\HTPM")
RMI_PATH      = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json")

FINAL_FN      = "261123 HTPM sai lầm lấy chồng rồi để bản thân lại sau final.mp4"
BRAND_OUT     = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma"
D_OUT         = r"D:\XUẤT CAPCUT\hằng thu pharma"
MASTER_OUT    = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final"
DRIVE_PROJ    = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-kb06-261123-co-chong-roi"
ART_DIR       = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8"

W, H, FPS, SR = 1080, 1920, 30.0, 48000

# Exact 1.1x CapCut timeline constants (1.0x timestamps divided by 1.1!)
HOOK_Q_END  = 2.84 / 1.1   # 2.582s
RISER_T     = 11.55 / 1.1  # 10.500s
FULL_STAGES = [
    (17.56 / 1.1, 26.72 / 1.1),  # 15.964s .. 24.291s (8.33s -> s2_busy_chores 6.83s @ 0.83x single-pass!)
    (37.28 / 1.1, 44.86 / 1.1),  # 33.891s .. 40.782s (6.89s -> s4_selflove_glow 6.77s @ 0.98x single-pass!)
]
HIDE_KOBE_WINDOWS = [
    (44.86 / 1.1, 49.70 / 1.1),  # 40.782s .. 45.182s: Clean expressive close-up on Chị Hằng's punchline!
]
BROLL_SLOTS = [
    (11.62 / 1.1, 17.46 / 1.1, "s1_before_wed",     "lower", "TRƯỚC CƯỚI", "CHĂM DA • TÓC • QUẦN ÁO ĐẸP",         (201, 24, 96), -0.02),
    (16.04,       24.22,       "s2_busy_chores",    "full",  "SAU CƯỚI",   "LO TOAN CẢ NHÀ • BẢN THÂN ĐỂ MAI",    (229, 72, 59), -0.02),
    (26.82 / 1.1, 32.55 / 1.1, "s3_mirror_realize", "lower", "NHÌN LẠI",   "ĐÃ RẤT LÂU BỎ QUÊN CHÍNH MÌNH",       ( 54, 86, 251), -0.02),
    (33.96,       40.72,       "s4_selflove_glow",  "full",  "YÊU MÌNH",   "PHỤ NỮ KHỎE ĐẸP • TỰ TIN HẠNH PHÚC",  ( 11,138, 92), -0.02),
]
# Calibrated face crop on 1.06x CapCut frame (from cover_ruler.jpg: hair crown y=485, chin y=905, shoulders y=1135)
PIP_BOX     = [455, 1135, 185, 865]
CROWN_CUT_Y = 545

CAM_KFS = [
    (0.00,               1.000, 0.000,  0.000, 0.32),
    (0.10,               1.022, 0.000, -0.003, max(0.8, HOOK_Q_END - 0.12)),
    (HOOK_Q_END,         1.155, 0.000, -0.015, 0.44),   # Post-Hook Zoom-In right after reading Hook!
    (HOOK_Q_END + 0.48,  1.182, 0.000, -0.018, 7.20),   # Continuous living creep during Hook!
    (RISER_T - 0.42,     1.000, 0.000,  0.000, 0.44),   # SFX Riser climax -> Zoom back to 1.000x Normal Frame!
    (RISER_T + 2.90,     1.022, 0.000, -0.003, 3.20),
    (26.74 / 1.1,        1.000, 0.000,  0.000, 0.45),
    (32.70 / 1.1,        1.076, 0.000, -0.008, 0.48),
    (44.90 / 1.1,        1.058, 0.000, -0.006, 0.45),
    (49.70 / 1.1,        1.028, 0.000, -0.003, 0.48),
    (53.20 / 1.1,        1.074, 0.000, -0.008, 0.50),
]

def eval_cam(t):
    zc, pxc, pyc = CAM_KFS[0][1], CAM_KFS[0][2], CAM_KFS[0][3]
    for tk, zk, pxk, pyk, dk in CAM_KFS[1:]:
        if t >= tk:
            u = h5.septic_smooth(h5.clamp01((t - tk) / max(0.18, dk)))
            zc += (zk - zc) * u; pxc += (pxk - pxc) * u; pyc += (pyk - pyc) * u
    return zc, pxc, pyc

def load_kb06_captions(clean_json_path, max_dur):
    tr = json.load(open(clean_json_path, encoding="utf-8"))
    def allowed(tc):
        return not any(s0 - 0.04 <= tc <= s1 + 0.02 for s0, s1 in FULL_STAGES)
    words = [[w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
             for seg in tr["segments"] for w in seg.get("words", [])
             if w["word"].strip() and allowed((w["start"] + w["end"]) * 0.5)]
    phrases, cur = [], []
    for w in words:
        if cur:
            gap = w[1] - cur[-1][2]
            pt  = cur[-1][0]
            if re.search(r"[.?!…;:]$", pt) or gap >= 0.35 or (re.search(r"[,]$", pt) and len(cur) >= 4) or len(cur) >= 7:
                phrases.append(cur); cur = []
        cur.append(w)
    if cur: phrases.append(cur)
    for p in phrases:
        if p:
            p[0][0] = h5.cap_first_char(p[0][0])
            for k in range(1, len(p)):
                if re.search(r"[.?!:]$", p[k - 1][0]): p[k][0] = h5.cap_first_char(p[k][0])
                elif p[k][0][:1].isupper() and p[k][0].lower().strip("\"',.") not in {"hằng"}:
                    p[k][0] = p[k][0][0].lower() + p[k][0][1:]
    def split_b(p):
        if len(p) <= 5 and (sum(len(x[0]) + 1 for x in p) - 1) <= 23: return [p]
        bk = max(1, len(p) // 2)
        return [p[:bk], p[bk:]]
    groups = []
    for i, p in enumerate(phrases):
        t0  = p[0][1] - 0.03
        nxt = phrases[i + 1][0][1] if i + 1 < len(phrases) else max_dur - 0.15
        t1  = min(nxt - 0.04, p[-1][2] + 0.42)
        for s0, _ in FULL_STAGES:
            if t0 < s0 - 0.04 and t1 > s0 - 0.04: t1 = s0 - 0.04
        if t1 > t0 + 0.15:
            groups.append({"t0": t0, "t1": t1, "lines": split_b(p)})
    return groups

def ensure_kobe_11x_mov(n_fr):
    src_mov = os.path.join(KB06_DIR, "kobe_overlays.mov")
    dst_mov = os.path.join(AROLL_DIR, "kobe_overlays_11x.mov")
    if not os.path.exists(dst_mov):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", src_mov,
            "-vf", "setpts=PTS/1.1", "-r", "30", "-fps_mode", "cfr", "-frames:v", str(n_fr),
            "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
            dst_mov
        ], check=True)
    return dst_mov

def chunk_worker(args):
    c_idx, f_start, f_end, emit_cc_ov = args
    n_frames = f_end - f_start
    t_s, t_e = f_start / FPS, f_end / FPS
    chunk_mp4 = os.path.join(AROLL_DIR, f"_chunk_{c_idx:02d}.mp4")
    ov_mov    = os.path.join(AROLL_DIR, f"_ov_{c_idx:02d}.mov")

    clips = {
        sn: h5.load_vid_frames_wh(os.path.join(MEDIA_DIR, f"{sn}.mp4"), 1024, 576)
        for bs0, bs1, sn, _, _, _, _, _ in BROLL_SLOTS
        if not (bs1 + 0.3 < t_s or bs0 - 0.3 > t_e)
    }
    cap_groups = load_kb06_captions(os.path.join(AROLL_DIR, "main_cut_clean.json"), (f_end + 600) / FPS)
    ROSE_W    = {"cưới", "chồng", "sai", "lầm", "ích", "kỷ", "quên"}
    COBALT_W  = {"tiền", "điện", "chợ", "lo", "nhà"}
    EMERALD_W = {"khỏe", "đẹp", "hạnh", "phúc", "chăm", "yêu", "mình"}

    pa = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t_s:.6f}", "-i", os.path.join(AROLL_DIR, "main_cut_graded.mp4"), "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    pm = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t_s:.6f}", "-i", os.path.join(AROLL_DIR, "main_cut_matte.mp4"),  "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    pk = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t_s:.6f}", "-i", os.path.join(AROLL_DIR, "kobe_overlays_11x.mov"), "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)

    wr = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-threads", "3", "-pix_fmt", "yuv420p", chunk_mp4], stdin=subprocess.PIPE)
    wo = None
    if emit_cc_ov:
        wo = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-threads", "3", ov_mov], stdin=subprocess.PIPE)

    for li in range(n_frames):
        ba, bm, bk = pa.stdout.read(W * H * 3), pm.stdout.read(W * H), pk.stdout.read(W * H * 4)
        if len(ba) < W * H * 3 or len(bm) < W * H: break
        rgb_raw   = np.frombuffer(ba, np.uint8).reshape((H, W, 3))
        matte_raw = np.frombuffer(bm, np.uint8).reshape((H, W))
        kobe_rgba = np.frombuffer(bk, np.uint8).reshape((H, W, 4)) if len(bk) == W * H * 4 else None
        t = (f_start + li) / FPS

        zc, pxc, pyc = eval_cam(t)
        if abs(zc - 1.0) < 1e-4 and abs(pxc) < 1e-4 and abs(pyc) < 1e-4:
            fg_rgb, m_top = rgb_raw, matte_raw[:CROWN_CUT_Y + 20]
        else:
            fg_rgb = np.array(h5.fit_cover_subpixel(rgb_raw, W, H, zoom=zc, pan_x=pxc, pan_y=pyc))
            if kobe_rgba is not None and kobe_rgba[:465, :, 3].max() > 0:
                m_rgb = np.repeat(matte_raw[:, :, None], 3, axis=2)
                m_top = np.array(h5.fit_cover_subpixel(m_rgb, W, H, zoom=zc, pan_x=pxc, pan_y=pyc).convert("L"))[:CROWN_CUT_Y + 20]
            else:
                m_top = matte_raw[:CROWN_CUT_Y + 20]

        in_full = next(((s0, s1) for s0, s1 in FULL_STAGES if s0 <= t <= s1), None)
        hide_kb = any(h0 <= t <= h1 for h0, h1 in HIDE_KOBE_WINDOWS)
        if hide_kb:
            kobe_rgba = None
        ov_im   = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        if not in_full:
            # 1. Crown-Hugging Top Header shifted down +30px (or +42px in Hook zoom) so 100% of text sits cleanly right above hair crown!
            dy_top = 42 if t < RISER_T else 30
            if kobe_rgba is not None and kobe_rgba[:465, :, 3].max() > 0:
                top_slice = kobe_rgba[:465].copy()
                ov_im.alpha_composite(Image.fromarray(top_slice, "RGBA"), dest=(0, dy_top))

            # 2. Lower Stage + Single-Pass Non-Looping AI B-Roll Card (y=1052..1464 for clean Safe-Zone subtitle clearance!)
            for bs0, bs1, sn, mode, tg, mn, ac, py in BROLL_SLOTS:
                if mode == "lower" and bs0 <= t <= bs1:
                    vf = h5.get_clip_frame_single_pass(clips, sn, t - bs0, bs1 - bs0)
                    h5.draw_kobe_flow_video_card(ov_im, vf, t, bs0, bs1, 324.0, 1258.0, 596, 404, tg, mn, accent_rgb=ac, pan_y=py)

            if kobe_rgba is not None and kobe_rgba[1050:1555, :, 3].max() > 0:
                ov_im.alpha_composite(Image.fromarray(kobe_rgba[1050:1555], "RGBA"), dest=(0, 1012))

            # 3. Eye-Level Safe-Zone Subtitles centered at x=540 (max_w=676 -> x in [202..878] < 884px, y=1488..1542 <= 1545px!)
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    dt_in, dt_out = t - g["t0"], g["t1"] - t
                    u_in  = h5.ease_out_back_soft(h5.clamp01(dt_in / 0.20), overshoot=1.05)
                    u_out = h5.septic_smooth(h5.clamp01(dt_out / 0.16))
                    op_g  = min(h5.quintic_smooth(h5.clamp01(dt_in / 0.14)), u_out)
                    if op_g <= 0.01: break
                    cap_sz, lh, gap = 49.0, 54.0, 11.0
                    y_base = 1488.0 if len(g["lines"]) >= 2 else 1512.0
                    x_center, max_w = 540.0, 676.0
                    for l_i, ln in enumerate(g["lines"]):
                        wrs, tot_w = [], 0.0
                        for wi, (wtxt, ws, we) in enumerate(ln):
                            is_act = (ws - 0.04 <= t <= we + 0.18)
                            wlow = wtxt.lower().rstrip(",.?!:;\"")
                            pal = "rose_satin" if wlow in ROSE_W else ("cobalt" if wlow in COBALT_W else ("emerald" if wlow in EMERALD_W else ("gold" if is_act else "pearl")))
                            sp = h5.render_thin_grad_word(wtxt, cap_sz, palette=pal, stroke_w=2)
                            adv = ImageDraw.Draw(ov_im).textlength(wtxt, font=h5.get_font(FONT_SUB_MAIN, cap_sz)) + 2.0
                            wrs.append((sp, adv, 1.06 if is_act else 1.00))
                            tot_w += adv + (gap if wi > 0 else 0.0)
                        fk = min(1.0, max_w / max(1.0, tot_w))
                        cx_w = x_center - (tot_w * fk) * 0.5
                        cy_w = y_base + l_i * lh + (1.0 - u_in) * 11.0
                        for sp, adv, pls in wrs:
                            ea = adv * fk
                            h5.paste_centered_rgba(ov_im, sp, cx_w + ea * 0.5, cy_w, scale=fk * pls, opacity=op_g)
                            cx_w += ea + gap * fk
                    break

            comp_im = Image.alpha_composite(Image.fromarray(fg_rgb, "RGB").convert("RGBA"), ov_im)
            if abs(t - RISER_T) <= 0.18:
                comp_im = h5.apply_riser_optical_transition(comp_im, t, center_t=RISER_T, half_w=0.18)
        else:
            s0_f, s1_f = in_full
            if kobe_rgba is not None and kobe_rgba[:, :, 3].max() > 0:
                ov_im.alpha_composite(Image.fromarray(kobe_rgba, "RGBA"), dest=(0, 0))
            for bs0, bs1, sn, mode, tg, mn, ac, py in BROLL_SLOTS:
                if mode == "full" and bs0 <= t <= bs1:
                    vf = h5.get_clip_frame_single_pass(clips, sn, t - bs0, bs1 - bs0)
                    h5.draw_kobe_flow_video_card(ov_im, vf, t, bs0, bs1, 540.0, 390.0, 948, 396, tg, mn, accent_rgb=ac, pan_y=py)

            # 416px Iris Circle PiP centered at (476, 1340) — 100% Safe Zone (bottom=1548, right=684 < 884!)
            sub_face = rgb_raw[PIP_BOX[0]:PIP_BOX[1], PIP_BOX[2]:PIP_BOX[3]]
            u_op = h5.quintic_smooth(h5.clamp01((t - s0_f) / 0.22))
            u_cl = h5.quintic_smooth(h5.clamp01((s1_f - t) / 0.20))
            ir_u = min(u_op, u_cl)
            op_s = h5.clamp01(min((t - s0_f) / 0.12, (s1_f - t) / 0.12))
            if op_s > 0.01:
                diam, pad = 396, 34
                cw = diam + pad * 2
                card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
                sh = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
                ImageDraw.Draw(sh).ellipse([pad - 4, pad + 14, pad + diam + 4, pad + diam + 22], fill=(45, 62, 140, 68))
                card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=14)))
                d = ImageDraw.Draw(card)
                pr_r = int(round(6.0 + 5.0 * (0.5 + 0.5 * math.sin((t - s0_f) * 3.4))))
                ha_a = int(round(135 - 55 * (0.5 + 0.5 * math.sin((t - s0_f) * 3.4))))
                d.ellipse([pad - pr_r, pad - pr_r, pad + diam - 1 + pr_r, pad + diam - 1 + pr_r], outline=(143, 162, 247, ha_a), width=3)
                d.ellipse([pad, pad, pad + diam - 1, pad + diam - 1], fill=(206, 216, 250, 255))
                if ir_u > 0.01:
                    ri = max(2.0, (diam * 0.5) * ir_u); ci = diam * 0.5
                    imk = Image.new("L", (diam, diam), 0)
                    ImageDraw.Draw(imk).ellipse([ci - ri, ci - ri, ci + ri, ci + ri], fill=255)
                    vl = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
                    vl.paste(h5.fit_cover_subpixel(sub_face, diam, diam, zoom=1.04), (pad, pad), mask=imk)
                    card = Image.alpha_composite(card, vl)
                d = ImageDraw.Draw(card)
                d.ellipse([pad - 5, pad - 5, pad + diam + 4, pad + diam + 4], outline=(143, 162, 247, 255), width=4)
                d.ellipse([pad - 1, pad - 1, pad + diam, pad + diam], outline=(255, 255, 255, 255), width=9)
                h5.paste_centered_rgba(ov_im, card, 540.0, 1344.0 + math.sin((t - s0_f) * 2.2) * 3.5 * ir_u, scale=0.92 + 0.08 * op_s, opacity=op_s)

            comp_im = Image.alpha_composite(Image.fromarray(fg_rgb, "RGB").convert("RGBA"), ov_im)

        wr.stdin.write(np.array(comp_im.convert("RGB"), np.uint8).tobytes())
        if wo is not None:
            wo.stdin.write(np.array(ov_im, np.uint8).tobytes())

    wr.stdin.close(); wr.wait()
    if wo is not None:
        wo.stdin.close(); wo.wait()
    for p in (pa, pm, pk): p.stdout.close(); p.wait()
    return c_idx, chunk_mp4, ov_mov

def mix_kb06_audio_and_sfx(vid_dur):
    N = int(round(vid_dur * SR))
    voc_wav = os.path.join(STEMS_DIR, "htdemucs", "mc_input", "vocals.wav")
    voc = m5.decode_stereo_f32(voc_wav, dur_limit=vid_dur, af="highpass=f=75,acompressor=threshold=-18dB:ratio=2.2:attack=10:release=140:makeup=2dB")
    voc = np.vstack([voc, np.zeros((max(0, N - len(voc)), 2), np.float32)])[:N]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vp = np.vstack([voc, np.zeros((n_hops * hop - N, 2), np.float32)])
    vo_rms = np.sqrt(np.mean(vp.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.016).astype(np.float32)

    sp_samples = np.repeat(speaking > 0.5, hop)[:N]
    cur_rms = float(np.sqrt(np.mean(voc[sp_samples] ** 2))) if np.any(sp_samples) else float(np.sqrt(np.mean(voc ** 2)))
    if cur_rms > 1e-4:
        voc *= (0.168 / cur_rms)

    # User's exact BGM from CapCut HTPM: tokyo_drift_remix.mp3 starting at 60.30s, gently ducked (-16.2 dB below Voice!)
    eq_af = f"atrim=60.30:{60.30 + vid_dur + 3.0:.2f},asetpts=PTS-STARTPTS,highpass=f=85,equalizer=f=1800:t=q:w=1.25:g=-4.5,lowpass=f=11500"
    bgm = m5.decode_stereo_f32(TOKYO_BGM, af=eq_af)
    bgm = np.vstack([bgm, np.zeros((max(0, N - len(bgm)), 2), np.float32)])[:N]
    br = float(np.sqrt(np.mean(bgm ** 2)))
    if br > 1e-5:
        bgm *= (0.115 / br)
    sp_dil = np.zeros_like(speaking)
    for ih in range(n_hops):
        if speaking[ih] > 0.5: sp_dil[max(0, ih - 12):min(n_hops, ih + 22)] = 1.0
    w_sm = np.hanning(35).astype(np.float32); w_sm /= np.sum(w_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), w_sm, mode="valid")[:n_hops]
    duck_hop = 0.30 * (1.0 - sp_sm) + 0.175 * sp_sm
    duck_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, duck_hop).astype(np.float32)
    t_ax = np.arange(N, dtype=np.float32) / SR
    end_fd = np.clip((vid_dur - t_ax) / 0.80, 0.0, 1.0)[:, None]
    bgm_bus = bgm * duck_env[:, None] * end_fd

    bank = m5.load_sfx_bank()
    # Override hook_riser with exact authentic "Riser - Âm thanh dồn lên chuyển cảnh 01.mp3" from HTPM!
    if os.path.exists(RISER_01_LOCAL):
        r_arr = m5.decode_stereo_f32(RISER_01_LOCAL, af="atrim=1.65:3.10,asetpts=PTS-STARTPTS,highpass=f=120,equalizer=f=2800:t=q:w=1.10:g=-2.5,lowpass=f=12500")
        n_in, n_out = int(0.18 * SR), int(0.035 * SR)
        r_arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        r_arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(r_arr)))
        if pk > 1e-5: r_arr /= pk
        bank["hook_riser"] = (r_arr, int(np.argmax(np.max(np.abs(r_arr), axis=1))))

    sfx_bus = np.zeros((N, 2), np.float32)
    m5.stamp(sfx_bus, bank, "airy_whoosh", 0.08, -10.8)
    m5.stamp(sfx_bus, bank, "pop_clean",   0.20, -11.2, speaking_hops=speaking)
    m5.stamp(sfx_bus, bank, "swoosh_up",   HOOK_Q_END + 0.06, -10.2)

    # Exact Post-Hook SFX Riser Climax at t = 10.500s!
    m5.stamp(sfx_bus, bank, "hook_riser",   RISER_T, -7.5, align_peak=True, speaking_hops=None)
    m5.stamp(sfx_bus, bank, "shimmer_rise", RISER_T, -10.2, align_peak=True, speaking_hops=None)
    m5.stamp(sfx_bus, bank, "airy_whoosh",  RISER_T + 0.01, -9.8, align_peak=True, speaking_hops=None)
    m5.stamp(sfx_bus, bank, "pop_round",    RISER_T + 0.14, -11.4, speaking_hops=speaking)

    for k, (bs0, bs1, _, _, _, _, _, _) in enumerate(BROLL_SLOTS):
        m5.stamp(sfx_bus, bank, "airy_whoosh", bs0 - 0.10, -10.8)
        m5.stamp(sfx_bus, bank, "pop_clean",   bs0 + 0.20, -11.2, semitones=k * 1.1, speaking_hops=speaking)
        m5.stamp(sfx_bus, bank, "soft_whoosh", bs1 - 0.10, -11.0)
    for s0_f, s1_f in FULL_STAGES:
        m5.stamp(sfx_bus, bank, "click_picon", s0_f + 1.1, -12.0, speaking_hops=speaking)
        m5.stamp(sfx_bus, bank, "ping_glass",  s1_f - 1.1, -12.6, align_peak=False, speaking_hops=speaking)

    sfx_only_wav = os.path.join(STEMS_DIR, "sfx_bus_for_capcut.wav")
    m5.save_wav_16(sfx_only_wav, sfx_bus)

    mix_wav  = os.path.join(STEMS_DIR, "mix_pre.wav")
    norm_wav = os.path.join(STEMS_DIR, "mix_14lufs.wav")
    m5.save_wav_16(mix_wav, voc + bgm_bus + sfx_bus)
    p1 = subprocess.run(["ffmpeg", "-y", "-i", mix_wav, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    mj = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p1.stderr)
    if mj:
        st = json.loads(mj.group(0))
        af2 = f"loudnorm=I=-14.0:TP=-1.0:LRA=9:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"
    else:
        af2 = "loudnorm=I=-14.0:TP=-1.0:LRA=9"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mix_wav, "-af", af2, "-ar", str(SR), "-ac", "2", norm_wav], check=True)
    return norm_wav, sfx_only_wav

def update_capcut_htpm_project(ov_master_mov, sfx_wav, total_dur_s):
    if (DRAFT_DIR / ".locked").exists():
        print("[CapCut] HTPM is currently open (.locked exists) -> skipping in-place draft write to protect open session.", flush=True)
        return
    dc_path = DRAFT_DIR / "draft_content.json"
    bak_one = DRAFT_DIR / "draft_content.json.before_ai_merge"
    if not bak_one.exists():
        shutil.copy2(dc_path, bak_one)

    D = json.loads(dc_path.read_text(encoding="utf-8"))
    total_u = int(round(total_dur_s * 1_000_000))
    src_s0_u  = 1_360_000
    src_dur_u = int(round(total_u * 1.1))
    D["duration"] = total_u

    # 1. Track 0: Keep 100% of user's color grade & figure skin-smoothing extra_material_refs, trim cleanly to [1.36s..58.10s] @ 1.1x!
    tr0 = D["tracks"][0]
    seg0 = tr0["segments"][0]
    seg0["source_timerange"] = {"start": src_s0_u, "duration": src_dur_u}
    seg0["target_timerange"] = {"start": 0, "duration": total_u}

    # Add Post-Hook Zoom-In -> Riser Zoom-Out keyframes on Track 0 (around base scale=1.06, tx=-0.05956, ty=-0.060)
    def mk_kf(prop, pts):
        return {
            "id": str(uuid.uuid4()).upper(),
            "keyframe_list": [
                {
                    "id": str(uuid.uuid4()).upper(),
                    "curveType": "Line",
                    "graphID": "",
                    "left_control": {"x": 0.0, "y": 0.0},
                    "right_control": {"x": 0.0, "y": 0.0},
                    "time_offset": int(round(ts * 1_000_000)),
                    "values": [float(val)],
                }
                for ts, val in pts
            ],
            "material_id": "",
            "property_type": prop,
        }

    kf_pts_sc = [
        (0.00, 1.06),
        (HOOK_Q_END, 1.06),
        (HOOK_Q_END + 0.44, 1.06 * 1.155),
        (RISER_T - 0.42, 1.06 * 1.182),
        (RISER_T + 0.02, 1.06),
    ]
    seg0["common_keyframes"] = [mk_kf("KFTypeScaleX", kf_pts_sc), mk_kf("KFTypeScaleY", kf_pts_sc)]

    # 2. Add ProRes 4444 Transparent Master Overlay on Video Track 1!
    ov_fwd = str(Path(ov_master_mov)).replace("\\", "/")
    ov_vid_id = "AA112306-BEEF-4c06-9A01-000000000001"
    ov_spd_id = "AA112306-BEEF-4c06-9A01-000000000002"
    ov_scm_id = "AA112306-BEEF-4c06-9A01-000000000003"
    ov_vs_id  = "AA112306-BEEF-4c06-9A01-000000000004"

    D["materials"]["videos"] = [v for v in D["materials"]["videos"] if v["id"] != ov_vid_id]
    v_tpl = copy.deepcopy(D["materials"]["videos"][0])
    v_tpl.update({
        "id": ov_vid_id,
        "path": ov_fwd,
        "material_name": Path(ov_master_mov).name,
        "duration": total_u,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "crop": {"upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0, "lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0},
        "crop_ratio": "free",
        "crop_scale": 1.0,
    })
    D["materials"]["videos"].append(v_tpl)

    D["materials"]["speeds"] = [s for s in D["materials"]["speeds"] if s["id"] != ov_spd_id] + [{"id": ov_spd_id, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None}]
    D["materials"]["sound_channel_mappings"] = [s for s in D["materials"]["sound_channel_mappings"] if s["id"] != ov_scm_id] + [{"id": ov_scm_id, "type": "", "audio_channel_mapping": 0, "is_config_open": False}]
    D["materials"]["vocal_separations"] = [s for s in D["materials"]["vocal_separations"] if s["id"] != ov_vs_id] + [{"id": ov_vs_id, "type": "vocal_separation", "choice": 0, "removed_sounds": [], "time_range": None, "production_path": "", "final_algorithm": "", "enter_from": ""}]

    ov_seg = copy.deepcopy(seg0)
    ov_seg.update({
        "id": "AA112306-BEEF-4c06-9A01-000000000005",
        "material_id": ov_vid_id,
        "source_timerange": {"start": 0, "duration": total_u},
        "target_timerange": {"start": 0, "duration": total_u},
        "speed": 1.0,
        "volume": 0.0,
        "extra_material_refs": [ov_spd_id, ov_scm_id, ov_vs_id],
        "common_keyframes": [],
        "clip": {
            "alpha": 1.0,
            "flip": {"horizontal": False, "vertical": False},
            "rotation": 0.0,
            "scale": {"x": 1.0, "y": 1.0},
            "transform": {"x": 0.0, "y": 0.0},
        },
        "render_index": 1,
    })
    ov_track = {"attribute": 0, "flag": 2, "id": "AA112306-BEEF-4c06-9A01-000000000006", "is_default_name": True, "name": "", "segments": [ov_seg], "type": "video"}

    # 3. Audio Tracks: Keep Tokyo Drift BGM gently lowered (vol=0.125) + Full Riser & Micro-SFX bus!
    aud_tracks = [t for t in D["tracks"] if t["type"] == "audio"]
    if aud_tracks:
        bgm_tr = aud_tracks[0]
        bgm_tr["segments"][0]["target_timerange"] = {"start": 0, "duration": total_u}
        bgm_tr["segments"][0]["source_timerange"]["duration"] = total_u
        bgm_tr["segments"][0]["volume"] = 0.125

    sfx_fwd = str(Path(sfx_wav)).replace("\\", "/")
    sfx_aud_id = "AA112306-BEEF-4c06-9A01-000000000011"
    sfx_spd_id = "AA112306-BEEF-4c06-9A01-000000000012"
    D["materials"]["audios"] = [a for a in D["materials"]["audios"] if a["id"] != sfx_aud_id]
    a_tpl = copy.deepcopy(D["materials"]["audios"][0])
    a_tpl.update({"id": sfx_aud_id, "path": sfx_fwd, "name": Path(sfx_wav).name, "duration": total_u})
    D["materials"]["audios"].append(a_tpl)
    D["materials"]["speeds"] = [s for s in D["materials"]["speeds"] if s["id"] != sfx_spd_id] + [{"id": sfx_spd_id, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None}]

    sfx_tr = copy.deepcopy(aud_tracks[0])
    sfx_tr["id"] = "AA112306-BEEF-4c06-9A01-000000000013"
    sfx_seg = sfx_tr["segments"][0]
    sfx_seg.update({
        "id": "AA112306-BEEF-4c06-9A01-000000000014",
        "material_id": sfx_aud_id,
        "source_timerange": {"start": 0, "duration": total_u},
        "target_timerange": {"start": 0, "duration": total_u},
        "speed": 1.0,
        "volume": 1.0,
        "extra_material_refs": [sfx_spd_id],
    })

    D["tracks"] = [tr0, ov_track] + ([aud_tracks[0]] if aud_tracks else []) + [sfx_tr]

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    pj = json.loads((DRAFT_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id = pj.get("main_timeline_id") or "003289D0-6091-4c61-B3EC-89D6241E7275"
    tl_sub = DRAFT_DIR / "Timelines" / tl_id
    for p_out in [DRAFT_DIR / "draft_content.json", DRAFT_DIR / "template-2.tmp", tl_sub / "draft_content.json", tl_sub / "template-2.tmp"]:
        if p_out.exists():
            p_out.unlink()
        p_out.write_bytes(dc_bytes)

    now_us = int(time.time() * 1_000_000)
    dmi_p = DRAFT_DIR / "draft_meta_info.json"
    if dmi_p.exists():
        dmi = json.loads(dmi_p.read_text(encoding="utf-8"))
        dmi["tm_duration"] = total_u
        dmi["tm_draft_modified"] = now_us
        dmi_p.write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")
    if RMI_PATH.exists():
        rmi = json.loads(RMI_PATH.read_text(encoding="utf-8"))
        for ent in rmi.get("all_draft_store", []):
            if ent.get("draft_name") == "HTPM" and "com.lveditor.draft" in str(ent.get("draft_fold_path", "")):
                ent["tm_duration"] = total_u
                ent["tm_draft_modified"] = now_us
        RMI_PATH.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")
    print("[CapCut] Updated HTPM draft in-place with 100% original color/skin grade + Kobe overlay + Riser SFX!", flush=True)

def main():
    t0 = time.time()
    mc_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    pr = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames:format=duration", "-of", "json", mc_graded], text=True))
    n_fr    = int(pr["streams"][0]["nb_read_frames"])
    vid_dur = float(pr["format"]["duration"])
    ensure_kobe_11x_mov(n_fr)

    step = (n_fr + 3) // 4
    tasks = [(i, i * step, min(n_fr, (i + 1) * step), False) for i in range(4) if i * step < min(n_fr, (i + 1) * step)]
    print(f"[KB06] Compositing {n_fr} frames ({vid_dur:.2f}s @ 1.1x) across 4 workers...", flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as ex:
        res = sorted(list(ex.map(chunk_worker, tasks)), key=lambda x: x[0])

    vlist = os.path.join(AROLL_DIR, "_vlist.txt")
    open(vlist, "w", encoding="utf-8").write("".join("file '" + cp.replace("\\", "/") + "'\n" for _, cp, _ in res))

    raw_vid = os.path.join(AROLL_DIR, "_master_video_only.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", vlist, "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p", raw_vid], check=True)
    for _, cp, _ in res:
        try: os.remove(cp)
        except OSError: pass

    norm_wav, sfx_wav = mix_kb06_audio_and_sfx(vid_dur)
    local_final = os.path.join(KB06_DIR, FINAL_FN)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_vid, "-i", norm_wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", local_final], check=True)

    err_c = subprocess.run(["ffmpeg", "-v", "error", "-i", local_final, "-f", "null", "-"], capture_output=True, text=True)
    assert err_c.stderr.strip() == "", f"Decode error: {err_c.stderr}"

    # 20-panel QC Sheet
    sheet = Image.new("RGB", (270 * 5, 480 * 4), (16, 20, 32))
    fnt = ImageFont.truetype(FONT_SUB_MAIN, 22)
    key_ts = [0.8, 2.2, 3.2, 6.5, 10.50, 11.8, 14.2, 16.8, 20.0, 23.0, 25.4, 28.0, 30.8, 34.8, 37.5, 41.5, 44.2, 46.5, 48.8, 50.6]
    for idx, ts in enumerate(key_ts):
        ts = min(vid_dur - 0.25, ts)
        tj = os.path.join(CHECK_DIR, f"_q_{idx}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", local_final, "-frames:v", "1", "-q:v", "2", tj], check=True)
        im = Image.open(tj).convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(im); d.rounded_rectangle([8, 8, 112, 38], radius=10, fill=(14, 18, 30))
        d.text((16, 10), f"{ts:05.2f}s", font=fnt, fill=(255, 214, 84))
        sheet.paste(im, ((idx % 5) * 270, (idx // 5) * 480)); os.remove(tj)
    sh_p = os.path.join(ART_DIR, "kb06_261123_sheet.jpg")
    sheet.save(sh_p, quality=92)

    for dst in [
        os.path.join(BRAND_OUT, FINAL_FN),
        os.path.join(D_OUT, FINAL_FN),
        os.path.join(MASTER_OUT, FINAL_FN),
        os.path.join(ART_DIR, "HTPM_261123_KB06_FINAL.mp4"),
    ]:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(local_final, dst)
            print("EXPORTED_FINAL ->", dst, flush=True)
        except Exception as e:
            print("Copy warn:", dst, e, flush=True)

    try:
        os.makedirs(DRIVE_PROJ, exist_ok=True)
        shutil.copy2(__file__, os.path.join(DRIVE_PROJ, "render_kb06_htpm_final.py"))
        shutil.copy2(sh_p, os.path.join(DRIVE_PROJ, "kb06_261123_sheet.jpg"))
        shutil.copy2(os.path.join(AROLL_DIR, "main_cut_clean.json"), os.path.join(DRIVE_PROJ, "main_cut_clean.json"))
    except Exception as e:
        print("Drive archive warn:", e, flush=True)

    print(f"KB06_ALL_COMPLETE in {time.time() - t0:.1f}s!", flush=True)

if __name__ == "__main__":
    main()
