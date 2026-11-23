import json, math, os, re, shutil, subprocess, time, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT        = r"d:\AI\full studio\output\f20-set-qua-2011"
MEDIA      = os.path.join(OUT, "capcut_media")
CHECK      = os.path.join(OUT, "check_final")
os.makedirs(CHECK, exist_ok=True)

W, H = 1080, 1920
FPS  = 30.0
SR   = 48000

FONTS_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
F_XBOLD    = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
F_BOLD     = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")
F_OSWALD   = os.path.join(FONTS_DIR, "Oswald-Bold.ttf")

_fc = {}
def gf(p, sz):
    k = (p, max(10, int(round(sz))))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(p, k[1])
    return _fc[k]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def ease_out_quart(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 4.0

# Fast cached RGBA sprite generator for Top Dual-Tier Titles & Bottom Keyword-Highlighted Subtitles
_sp_cache = {}
def get_title_sprite(t1_txt, t2_txt, is_hook=False):
    k = ("top", t1_txt, t2_txt, is_hook)
    if k in _sp_cache:
        return _sp_cache[k]
    im = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f1 = gf(F_OSWALD if is_hook else F_XBOLD, 56 if is_hook else 40)
    f2 = gf(F_BOLD, 34 if is_hook else 27)

    bb1 = d.textbbox((0, 0), t1_txt, font=f1, stroke_width=4)
    w1, h1 = bb1[2] - bb1[0], bb1[3] - bb1[1]
    pw1, ph1 = w1 + 52, h1 + 26
    x1 = (W - pw1) // 2
    y1 = 58
    d.rounded_rectangle([x1, y1, x1 + pw1, y1 + ph1], radius=ph1 // 2, fill=(28, 8, 14, 198), outline=(252, 218, 118, 235), width=3)
    d.text(((W - w1) * 0.5 - bb1[0], y1 + (ph1 - h1) * 0.5 - bb1[1]), t1_txt, font=f1, fill=(255, 218, 45, 255), stroke_width=4, stroke_fill=(20, 6, 10, 255))

    bb2 = d.textbbox((0, 0), t2_txt, font=f2, stroke_width=4)
    w2, h2 = bb2[2] - bb2[0], bb2[3] - bb2[1]
    y2 = y1 + ph1 + 14
    d.text(((W - w2) * 0.5 - bb2[0] + 2, y2 - bb2[1] + 2), t2_txt, font=f2, fill=(0, 0, 0, 190))
    d.text(((W - w2) * 0.5 - bb2[0], y2 - bb2[1]), t2_txt, font=f2, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(18, 8, 12, 255))
    _sp_cache[k] = im
    return im

def get_sub_sprite(txt, kws):
    k = ("sub", txt, tuple(kws))
    if k in _sp_cache:
        return _sp_cache[k]
    fnt = gf(F_XBOLD, 37)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    # Wrap into 1 or 2 balanced lines if width > 930px
    bb_all = dummy.textbbox((0, 0), txt, font=fnt, stroke_width=5)
    if (bb_all[2] - bb_all[0]) <= 920:
        lines = [txt]
    else:
        words = txt.split(" ")
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    im = Image.new("RGBA", (W, 240), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Measure box
    lws = [d.textbbox((0, 0), ln, font=fnt, stroke_width=5) for ln in lines]
    max_w = max(b[2] - b[0] for b in lws)
    tot_h = len(lines) * 56
    bx0 = (W - (max_w + 54)) // 2
    by0 = 30
    d.rounded_rectangle([bx0, by0, bx0 + max_w + 54, by0 + tot_h + 28], radius=26, fill=(18, 8, 12, 168))

    # Determine highlighted character indices in full joined text
    full_join = "\n".join(lines)
    hi_mask = [False] * len(full_join)
    for kw in kws:
        st_i = 0
        while True:
            idx = full_join.lower().find(kw.lower(), st_i)
            if idx < 0:
                break
            for c_i in range(idx, min(len(full_join), idx + len(kw))):
                hi_mask[c_i] = True
            st_i = idx + len(kw)

    char_offset = 0
    for li, ln in enumerate(lines):
        # Split line into tokens with spaces preserved
        bb_ln = d.textbbox((0, 0), ln, font=fnt)
        lw = bb_ln[2] - bb_ln[0]
        cx = (W - lw) * 0.5
        cy = by0 + 14 + li * 56 - bb_ln[1]
        # Draw word by word for clean coloring
        parts = re.findall(r"\S+|\s+", ln)
        pos_in_ln = 0
        for pt in parts:
            adv = d.textlength(pt, font=fnt)
            if not pt.isspace():
                g_idx = char_offset + pos_in_ln
                is_gold = any(hi_mask[g_idx:min(len(hi_mask), g_idx + len(pt))])
                col = (255, 220, 48, 255) if is_gold else (255, 255, 255, 255)
                d.text((cx + 2, cy + 3), pt, font=fnt, fill=(0, 0, 0, 185))
                d.text((cx, cy), pt, font=fnt, fill=col, stroke_width=4, stroke_fill=(16, 6, 10, 255))
            cx += adv
            pos_in_ln += len(pt)
        char_offset += len(ln) + 1

    _sp_cache[k] = im
    return im

def decode_stereo_48k(path, ss=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.4f}", "-i", path]
    if dur is not None:
        cmd += ["-t", f"{dur:.4f}"]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def main():
    t0_wall = time.time()
    sub_data = json.load(open(os.path.join(OUT, "subtitles_and_titles.json"), encoding="utf-8"))
    aud_man  = json.load(open(os.path.join(OUT, "audio_assets_manifest.json"), encoding="utf-8"))
    TOTAL_DUR = 112.433333
    N_FRAMES  = 3373

    # 1. Build base composite video (Track 0 Clean A-Roll + Track 1 17 B-Rolls/Showcases + Track 2 PIPs) via FFmpeg fast C-level overlay,
    # then pipe into Python ONLY to stamp crisp Top Titles & Bottom Subtitles at 90+ fps!
    broll_overlays = [
        (  1.45,   2.85, "broll_01_dolly_sets.mp4"),
        (  2.85,   4.35, "broll_02_rotating_tower.mp4"),
        ( 15.95,  25.35, "showcase_01_yensao_ingredients.mp4"),
        ( 28.55,  33.65, "showcase_02_rongbien_doi.mp4"),
        ( 35.80,  39.70, "showcase_03_banhthuyen_250g.mp4"),
        ( 42.20,  46.60, "showcase_04_rongbien_kephat_500g.mp4"),
        ( 50.00,  52.30, "broll_03_arrange_table.mp4"),
        ( 52.30,  54.65, "broll_04_mica_sunlit.mp4"),
        ( 57.20,  61.75, "broll_05_quai_da_macro.mp4"),
        ( 63.20,  67.20, "broll_06_hoa_no_macro.mp4"),
        ( 71.75,  76.72, "showcase_05_to_yen_cao_cap.mp4"),
        ( 80.40,  85.10, "broll_08_cam_nang_close.mp4"),
        ( 93.10,  95.00, "broll_09_factory_pack1.mp4"),
        ( 95.00,  96.80, "broll_10_factory_carton.mp4"),
        ( 96.80,  98.50, "broll_11_delivery_car.mp4"),
        (101.35, 105.20, "broll_12_handover_gift.mp4"),
        (105.85, 112.433333, "showcase_06_outro_endcard.mp4"),
    ]

    # Pre-load B-roll frame arrays ONLY when needed on the fly to keep RAM low & speed blazing fast!
    reader_a = subprocess.Popen([
        "ffmpeg", "-v", "error", "-i", os.path.join(MEDIA, "00_Clean_ARoll_Full.mp4"),
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ], stdout=subprocess.PIPE)

    raw_vid_out = os.path.join(OUT, "_f20_v5_video_only.mp4")
    writer = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "h264_nvenc", "-cq", "18", "-preset", "p4", "-pix_fmt", "yuv420p", raw_vid_out
    ], stdin=subprocess.PIPE)

    # Active B-roll stream helper
    cur_ov_idx = -1
    cur_ov_proc = None

    for fi in range(N_FRAMES):
        buf = reader_a.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        t = fi / FPS
        rgb = np.frombuffer(buf, dtype=np.uint8).reshape((H, W, 3)).copy()

        # Check if t falls in a B-roll / Showcase window
        ov_match = -1
        for oi, (ot0, ot1, _) in enumerate(broll_overlays):
            if ot0 <= t < ot1:
                ov_match = oi
                break
        if ov_match != cur_ov_idx:
            if cur_ov_proc is not None:
                cur_ov_proc.stdout.close(); cur_ov_proc.wait(); cur_ov_proc = None
            cur_ov_idx = ov_match
            if cur_ov_idx >= 0:
                cur_ov_proc = subprocess.Popen([
                    "ffmpeg", "-v", "error", "-i", os.path.join(MEDIA, broll_overlays[cur_ov_idx][2]),
                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
                ], stdout=subprocess.PIPE)

        if cur_ov_proc is not None:
            obuf = cur_ov_proc.stdout.read(W * H * 3)
            if len(obuf) == W * H * 3:
                ov_rgb = np.frombuffer(obuf, dtype=np.uint8).reshape((H, W, 3))
                ot0, ot1, _ = broll_overlays[cur_ov_idx]
                # Smooth 0.22s crossfade in/out at overlay edges
                alpha = 1.0
                if (t - ot0) < 0.22 and ot0 > 0.5:
                    alpha = clamp01((t - ot0) / 0.22)
                elif (ot1 - t) < 0.22 and ot1 < 112.0:
                    alpha = clamp01((ot1 - t) / 0.22)
                if alpha >= 0.99:
                    rgb = ov_rgb.copy()
                else:
                    rgb = np.clip(rgb.astype(np.float32) * (1.0 - alpha) + ov_rgb.astype(np.float32) * alpha, 0, 255).astype(np.uint8)

        im = Image.fromarray(rgb, "RGB").convert("RGBA")

        # Stamp Top Dual-Tier Brand Title
        for item in sub_data["top_titles"]:
            if item["t0"] <= t < item["t1"]:
                sp_t = get_title_sprite(item["tier1"], item["tier2"], item.get("hook", False))
                op_t = min(clamp01((t - item["t0"]) / 0.25), clamp01((item["t1"] - t) / 0.25))
                if op_t < 0.99:
                    a = np.array(sp_t); a[:, :, 3] = (a[:, :, 3].astype(np.float32) * op_t).astype(np.uint8)
                    im.alpha_composite(Image.fromarray(a, "RGBA"), dest=(0, 0))
                else:
                    im.alpha_composite(sp_t, dest=(0, 0))
                break

        # Stamp Bottom Continuous Spoken Subtitle (Text Sub)
        for st_s, en_s, txt, kws in sub_data["subtitles"]:
            if st_s <= t < en_s:
                sp_s = get_sub_sprite(txt, kws)
                op_s = min(clamp01((t - st_s) / 0.16), clamp01((en_s - t) / 0.16))
                if op_s < 0.99:
                    a = np.array(sp_s); a[:, :, 3] = (a[:, :, 3].astype(np.float32) * op_s).astype(np.uint8)
                    im.alpha_composite(Image.fromarray(a, "RGBA"), dest=(0, 1425))
                else:
                    im.alpha_composite(sp_s, dest=(0, 1425))
                break

        writer.stdin.write(np.array(im.convert("RGB"), dtype=np.uint8).tobytes())
        if (fi + 1) % 600 == 0:
            print(f"  Composited {fi+1}/{N_FRAMES} frames ({(fi+1)/(time.time()-t0_wall):.1f} fps)", flush=True)

    if cur_ov_proc is not None:
        cur_ov_proc.stdout.close(); cur_ov_proc.wait()
    reader_a.stdout.close(); reader_a.wait()
    writer.stdin.close(); writer.wait()
    print(f"Video composite finished in {time.time()-t0_wall:.1f}s!")

    # 2. Mix Master Audio (Clean Voice + Dynamic Ducking BGM + All 85 SFX Cues -> 2-Pass -14.0 LUFS!)
    N_SAMP = int(round(TOTAL_DUR * SR))
    vo  = decode_stereo_48k(os.path.join(MEDIA, "01_Voice_Clean_Master.wav"), 0.0, TOTAL_DUR)
    vo  = np.vstack([vo, np.zeros((max(0, N_SAMP - len(vo)), 2), dtype=np.float32)])[:N_SAMP] * 1.15

    bgm = decode_stereo_48k(aud_man["bgm"], 0.0, TOTAL_DUR)
    bgm = np.vstack([bgm, np.zeros((max(0, N_SAMP - len(bgm)), 2), dtype=np.float32)])[:N_SAMP]
    # Smooth speech-aware sidechain ducking envelope
    hop = 480
    nh = (N_SAMP + hop - 1) // hop
    vp = np.vstack([vo, np.zeros((nh * hop - N_SAMP, 2), dtype=np.float32)])
    vrms = np.sqrt(np.mean(vp.reshape((nh, hop, 2)) ** 2, axis=(1, 2)))
    sp_flag = (vrms > 0.020).astype(np.float32)
    sp_dil = np.zeros_like(sp_flag)
    for ih in range(nh):
        if sp_flag[ih] > 0.5:
            sp_dil[max(0, ih - 20):min(nh, ih + 28)] = 1.0
    w_sm = np.hanning(41).astype(np.float32); w_sm /= np.sum(w_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (20, 20), mode="edge"), w_sm, mode="valid")[:nh]
    g_hop = 0.48 * (1.0 - sp_sm) + 0.26 * sp_sm
    b_env = np.interp(np.arange(N_SAMP, dtype=np.float32), np.arange(nh, dtype=np.float32) * hop, g_hop).astype(np.float32)
    bgm *= b_env[:, None]

    # Stamp all SFX cues from step5
    sfx_bus = np.zeros((N_SAMP, 2), dtype=np.float32)
    sfx_wavs = {k: decode_stereo_48k(v["path"]) for k, v in aud_man["sfx"].items()}
    # Import exact cue lists from step5 logic
    all_cues = [
        (0.04, "magic_reveal", 0.34), (0.08, "typewriter", 0.28), (0.36, "pop_tvc", 0.32),
        (1.42, "whoosh_tvc", 0.30), (2.82, "shutter", 0.28), (4.48, "whoosh_pip", 0.26), (4.75, "deep_woosh", 0.30),
        (10.28, "whoosh_tvc", 0.28), (10.32, "pop_tvc", 0.28), (11.78, "whoosh_pip", 0.26),
        (14.80, "riser_metal", 0.20), (15.92, "magic_reveal", 0.32), (15.96, "ting_quick", 0.28),
        (20.65, "swoosh_soft", 0.26), (21.48, "pop_tvc", 0.30), (22.38, "pop_soft", 0.30),
        (23.68, "pop_tvc", 0.30), (24.45, "ting_quick", 0.28), (25.32, "whoosh_tvc", 0.26),
        (25.48, "pop_tvc", 0.28), (28.50, "deep_woosh", 0.30), (28.70, "shutter", 0.25),
        (28.82, "pop_soft", 0.28), (31.32, "ting_quick", 0.28), (33.62, "swoosh_soft", 0.25),
        (33.78, "pop_tvc", 0.28), (35.76, "whoosh_tvc", 0.30), (35.95, "shutter", 0.24),
        (36.12, "ting_quick", 0.26), (39.68, "swoosh_soft", 0.24), (40.08, "pop_tvc", 0.28),
        (42.16, "whoosh_tvc", 0.30), (42.35, "shutter", 0.24), (42.48, "pop_soft", 0.28),
        (44.58, "ting_quick", 0.30), (46.82, "whoosh_pip", 0.26), (49.95, "deep_woosh", 0.30),
        (50.04, "notif_bell", 0.28), (52.26, "whoosh_tvc", 0.26), (54.62, "swoosh_soft", 0.24),
        (56.92, "pop_tvc", 0.28), (57.16, "whoosh_tvc", 0.30), (61.88, "ting_quick", 0.28),
        (63.16, "whoosh_tvc", 0.28), (68.85, "star_sparkle", 0.30), (70.60, "riser_metal", 0.20),
        (71.72, "magic_reveal", 0.35), (72.10, "ting_quick", 0.30), (76.70, "whoosh_tvc", 0.26),
        (76.84, "notif_bell", 0.28), (80.36, "whoosh_tvc", 0.26), (85.40, "ting_quick", 0.28),
        (85.42, "whoosh_pip", 0.25), (90.26, "deep_woosh", 0.30), (90.34, "notif_bell", 0.28),
        (93.06, "whoosh_tvc", 0.28), (94.96, "swoosh_soft", 0.26), (95.15, "ting_quick", 0.26),
        (96.76, "whoosh_tvc", 0.28), (98.56, "star_sparkle", 0.28), (98.70, "pop_tvc", 0.26),
        (101.32, "whoosh_tvc", 0.28), (105.80, "magic_reveal", 0.34), (106.10, "notif_bell", 0.34),
        (109.25, "ting_quick", 0.32)
    ]
    for idx_s, (st_s, _, _, _) in enumerate(sub_data["subtitles"]):
        if idx_s % 2 == 0:
            all_cues.append((st_s + 0.02, "pop_telop", 0.14))

    for ts, skey, g in all_cues:
        if skey not in sfx_wavs:
            continue
        clip = sfx_wavs[skey]
        i0 = int(round(ts * SR))
        i1 = min(N_SAMP, i0 + len(clip))
        if i1 > i0 and i0 >= 0:
            sfx_bus[i0:i1] += clip[:i1 - i0] * g

    mix = vo + bgm + np.tanh(sfx_bus) * 0.85
    pk = float(np.max(np.abs(mix)))
    if pk > 0.96:
        mix *= (0.96 / pk)

    mix_wav = os.path.join(OUT, "_f20_v5_pre_lufs.wav")
    with wave.open(mix_wav, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(mix, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())

    # 2-pass loudnorm -> -14.0 LUFS
    p1 = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", mix_wav,
        "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"
    ], stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{\s*\"input_i\".*?\}", p1.stderr, re.S)
    if m:
        st_j = json.loads(m.group(0))
        af_str = (
            f"loudnorm=I=-14:TP=-1:LRA=11:"
            f"measured_I={st_j['input_i']}:measured_TP={st_j['input_tp']}:"
            f"measured_LRA={st_j['input_lra']}:measured_thresh={st_j['input_thresh']}:"
            f"offset={st_j['target_offset']}:linear=true"
        )
        print("2-pass loudnorm:", st_j["input_i"], "-> -14.0 LUFS")
    else:
        af_str = "loudnorm=I=-14:TP=-1:LRA=11"

    local_final = os.path.join(OUT, "F20_SET_QUA_2011_FINAL.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", raw_vid_out, "-i", mix_wav,
        "-map", "0:v", "-map", "1:a", "-c:v", "copy",
        "-af", af_str, "-ar", "48000", "-c:a", "aac", "-b:a", "256k", local_final
    ], check=True)
    print("Exported Master MP4:", local_final)

    # Copy Final MP4 to TLH folder, D:\XUẤT CAPCUT, and Master Google Drive 04_Videos_Final!
    targets = [
        r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\f20-set-qua-2011_v5_FINAL.mp4",
        r"D:\XUẤT CAPCUT\F20_SET_QUA_2011_FINAL.mp4",
        r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\F20_SET_QUA_2011_FINAL.mp4",
    ]
    for tp in targets:
        os.makedirs(os.path.dirname(tp), exist_ok=True)
        shutil.copy2(local_final, tp)
        print("Synced Final MP4 ->", tp)

    # Generate 20-frame Contact Sheet for Visual QC!
    frames_qc = []
    fnt_qc = ImageFont.load_default()
    for qi in range(20):
        ts_q = min(111.5, 1.0 + qi * 5.65)
        fp_q = os.path.join(CHECK, f"q_{qi:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts_q:.2f}", "-i", local_final, "-frames:v", "1", "-vf", "scale=270:480", fp_q], check=True)
        im_q = Image.open(fp_q).convert("RGB")
        dr_q = ImageDraw.Draw(im_q)
        dr_q.rectangle([6, 6, 108, 28], fill=(0, 0, 0))
        dr_q.text((10, 9), f"{int(ts_q)//60:02d}:{int(ts_q)%60:02d} ({ts_q:.1f}s)", fill=(255, 230, 0), font=fnt_qc)
        frames_qc.append(im_q)
    sheet_qc = Image.new("RGB", (270 * 5, 480 * 4))
    for i, im_q in enumerate(frames_qc):
        sheet_qc.paste(im_q, ((i % 5) * 270, (i // 5) * 480))
    qc_sheet_path = os.path.join(CHECK, "qc_final_sheet.jpg")
    sheet_qc.save(qc_sheet_path, quality=90)
    print("Saved QC sheet:", qc_sheet_path)

if __name__ == "__main__":
    main()
