import copy, json, math, os, re, shutil, subprocess, sys, time, uuid
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR    = r"d:\AI\full studio\output\feelchicken-food-cinematic"
AI_DIR     = os.path.join(OUT_DIR, "ai_v3_clips")
REF_DIR    = os.path.join(OUT_DIR, "refs_v3_real_dishes")
RAW_V2     = os.path.join(OUT_DIR, "raw_v2")
RAW_V1     = os.path.join(OUT_DIR, "raw_cache")
SFX_V1     = os.path.join(RAW_V1, "sfx")
SFX_V2     = os.path.join(RAW_V2, "sfx")
SHOTS_V3   = os.path.join(OUT_DIR, "shots_v3_ungraded")
TITLE_V3   = os.path.join(OUT_DIR, "titles_v3_alpha")
AUDIO_V3   = os.path.join(OUT_DIR, "audio_v3")
CHK_V3     = os.path.join(OUT_DIR, "check_v3")
STAGE_V3   = os.path.join(OUT_DIR, "capcut_stage_v3")
FONTS_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
ART_DIR    = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ  = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-food-cinematic"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_Food_Cinematic_Pro"
DRAFT_ID   = "F94A82E1-63D4-4B89-9E12-7745C280B3A9"

for d in (SHOTS_V3, TITLE_V3, AUDIO_V3, CHK_V3, STAGE_V3, CLOUD_PRJ):
    os.makedirs(d, exist_ok=True)

W, H = 1080, 1920
FPS = 30
SR  = 48000
DUR = 27.60
N_SAMPLES = int(round(DUR * SR))

# Stage Slow Cook Honey (AL Dante / Sevdaliza dark sensual trip-hop twin!)
BGM_LOCAL = os.path.join(RAW_V2, "BGM_Slow_Cook_Honey.mp3")
if not os.path.exists(BGM_LOCAL):
    for root, _, files in os.walk(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"):
        if "Slow Cook Honey (2p39s).mp3" in files:
            shutil.copy2(os.path.join(root, "Slow Cook Honey (2p39s).mp3"), BGM_LOCAL)
            break

# ==============================================================================
# 1. TRUE SPEED-RAMP ENGINE (NHANH -> CHẬM -> NHANH, ZERO COLOR GRADING!)
# ==============================================================================
# Ramp modes:
#   'ramp_mid' : Fast entry (2.1x) -> Deep Slow-Mo hero center (0.52x) -> Fast exit (1.9x)
#   'ramp_in'  : Fast whip-in (2.3x) -> Sustained Slow-Mo reveal (0.62x)
#   'slow_pure': Pure silky slow-motion (0.60x)
#   'steady'   : Smooth gimbal walk-in (0.88x)
# Each tuple: (id, tl_start, tl_end, folder, filename, src_start, src_window_dur, ramp_mode, zoom_end)
# Every AI clip is locked strictly to its verified 100% pure food-art window (zero AI faces, zero empty tail)!
V3_SHOTS = [
    # Act 1: Ignition, Flour Cloud & Golden Oil Plunge (0.00 - 7.30s)
    ("S01_stove_ignite",   0.00,  1.20, RAW_V2,  "m01_stove_knob.MP4",             1.55, 1.80, "ramp_in",   1.05),
    ("S02_ai_flour_cloud", 1.20,  2.80, AI_DIR,  "FC_AI01_flour_plunge.mp4",       0.15, 1.72, "ramp_mid",  1.04),
    ("S03_steel_whisk",    2.80,  4.00, RAW_V2,  "m03b_whisk_top.MP4",             1.30, 1.90, "ramp_mid",  1.05),
    ("S04_ai_oil_plunge",  4.00,  5.20, AI_DIR,  "FC_AI01_flour_plunge.mp4",       2.12, 0.78, "slow_pure", 1.04),
    ("S05_ai_golden_lift", 5.20,  7.30, AI_DIR,  "FC_AI02_golden_fry_lift.mp4",    0.12, 2.25, "ramp_in",   1.04),

    # Act 2: Simmering Pan, Flaming Wok Toss & Signature Glaze Pours (7.30 - 15.60s)
    ("S06_red_simmer",     7.30,  8.50, RAW_V2,  "m11_pan_red_simmer.MP4",         3.10, 1.90, "ramp_mid",  1.05),
    ("S07_ai_wok_fire",    8.50, 10.80, AI_DIR,  "FC_AI03_wok_fire_glaze.mp4",     0.45, 2.95, "ramp_mid",  1.04),
    ("S08_ai_ruby_pour",  10.80, 13.20, AI_DIR,  "FC_AI04_ruby_sauce_pour.mp4",    0.15, 3.55, "ramp_mid",  1.04),
    ("S09_ai_cheddar",    13.20, 15.60, AI_DIR,  "FC_AI05_cheddar_velvet.mp4",     0.15, 3.55, "ramp_mid",  1.04),

    # Act 3: Slow-Mo Sesame Rain, Steaming Crispy Tear & Korean Noodles/Tokbokki (15.60 - 24.60s)
    ("S10_sesame_black",  15.60, 16.90, RAW_V2,  "m18_sesame_black.MP4",           1.75, 1.60, "slow_pure", 1.04),
    ("S11_ai_steam_tear", 16.90, 19.40, AI_DIR,  "FC_AI06_crispy_steam_tear.mp4",  0.15, 3.55, "ramp_in",   1.04),
    ("S12_ai_jajang_up",  19.40, 21.40, AI_DIR,  "FC_AI07_jajang_steam_lift.mp4",  0.10, 2.20, "ramp_mid",  1.04),
    ("S13_tokbokki_mac",  21.40, 22.60, RAW_V2,  "m23_tokbokki_lift.MP4",         21.60, 2.00, "ramp_mid",  1.05),
    ("S14_ai_hero_steam", 22.60, 24.60, AI_DIR,  "FC_AI08_hero_drumstick_lift.mp4",0.10, 2.30, "ramp_in",   1.04),

    # Act 4: New CS1 Storefront Gimbal Walk-In (DJI_0312_D.MP4 - 100% Ungraded Natural Color!)
    ("S15_cs1_walkin",    24.60, 27.60, REF_DIR, "DJI_20251201150558_0312_D.MP4",  4.35, 3.40, "steady",    1.02),
]

def build_speed_ramp_map(n_out: int, avail_src_s: float, src_fps: float, mode: str) -> np.ndarray:
    """
    Computes exact source frame indices for each output frame [0..n_out-1] using smooth cosine speed-ramping!
    Guarantees monotonic smooth motion (fast -> slow -> fast) within available source duration.
    """
    u = np.linspace(0.0, 1.0, n_out)
    if mode == "ramp_mid":
        # Fast (2.2x) at edges, deep slow-mo (0.50x) in center [0.28..0.72]
        spd = 0.50 + 1.65 * (np.cos(np.pi * (u - 0.5)) ** 0 == 0) # dummy init
        spd = 0.50 + 1.65 * ((2.0 * np.abs(u - 0.5)) ** 2.2)
    elif mode == "ramp_in":
        # Fast whip entry (2.35x) for first 25% -> silky 0.56x slow-mo hold!
        spd = 0.56 + 1.80 * (np.maximum(0.0, 1.0 - u / 0.32) ** 2.0)
    elif mode == "slow_pure":
        spd = np.full_like(u, 0.56)
    else:
        spd = np.full_like(u, 0.88)

    # Integrate instantaneous speed (in source seconds per output frame)
    dt_src = spd / float(FPS)
    cum_t = np.cumsum(dt_src) - dt_src[0]
    # Scale smoothly if cum_t[-1] exceeds avail_src_s * 0.94 so we never run out of source frames!
    max_allow = max(0.5, avail_src_s - 0.12)
    if cum_t[-1] > max_allow:
        cum_t *= (max_allow / cum_t[-1])
    return cum_t

def render_ungraded_speedramp_shot(idx_s):
    idx, (sid, t0, t1, fld, fn, s0, win_dur, rmode, z_end) = idx_s
    f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    n_out = f1 - f0
    src_p = os.path.join(fld, fn)
    out_p = os.path.join(SHOTS_V3, f"{idx+1:02d}_{sid}.mp4")

    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", src_p], capture_output=True, text=True, check=True)
    tot_src_dur = float(pr.stdout.strip() or 4.0)
    s0_safe = min(s0, max(0.0, tot_src_dur - 0.6))
    read_dur = min(win_dur, max(0.5, tot_src_dur - s0_safe))

    # Decode ONLY the verified clean window at 60fps RGB24 (ZERO COLOR GRADING!) at 1166x2074 for smooth sub-pixel push-in!
    W_OV, H_OV = 1166, 2074
    dec_fps = 60.0
    dec_cmd = [
        "ffmpeg", "-v", "error", "-ss", f"{s0_safe:.3f}", "-t", f"{read_dur:.3f}", "-i", src_p,
        "-vf", f"fps={int(dec_fps)},scale={W_OV}:{H_OV}:force_original_aspect_ratio=increase,crop={W_OV}:{H_OV},format=rgb24",
        "-f", "rawvideo", "-"
    ]
    raw_bytes = subprocess.run(dec_cmd, capture_output=True, check=True).stdout
    frame_sz = W_OV * H_OV * 3
    n_src = max(1, len(raw_bytes) // frame_sz)
    src_frames = np.frombuffer(raw_bytes[:n_src * frame_sz], dtype=np.uint8).reshape((n_src, H_OV, W_OV, 3))

    cum_t = build_speed_ramp_map(n_out, (n_src - 1) / dec_fps, dec_fps, rmode)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out_p
    ], stdin=subprocess.PIPE)

    for i in range(n_out):
        # Smooth optical frame blend on fractional 60fps index for buttery speed-ramps!
        f_pos = min(n_src - 1.001, max(0.0, cum_t[i] * dec_fps))
        ia = int(math.floor(f_pos))
        ib = min(n_src - 1, ia + 1)
        frac = f_pos - ia
        if frac < 0.05 or ia == ib:
            frm = src_frames[ia]
        else:
            frm = ((1.0 - frac) * src_frames[ia].astype(np.float32) + frac * src_frames[ib].astype(np.float32)).astype(np.uint8)

        # Subtle kinetic camera push matching the speed-ramp!
        prog = i / max(1, n_out - 1)
        z = 1.0 + (z_end - 1.0) * prog
        cw = int(round(W_OV / z))
        ch = int(round(H_OV / z))
        x0 = (W_OV - cw) // 2
        y0 = (H_OV - ch) // 2
        cropped = Image.fromarray(frm[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.BILINEAR)
        enc.stdin.write(cropped.tobytes())

    enc.stdin.close()
    enc.wait()
    return {"index": idx + 1, "id": sid, "start": t0, "end": t1, "src": fn, "path": out_p, "frames": n_out}

# ==============================================================================
# 2. ULTRA-MINIMAL SINGLE-COLOR WHITE CINEMA TYPOGRAPHY (SPARSE AL DANTE STYLE)
# ==============================================================================
CINE_WHITE = (247, 245, 240)

def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def make_single_color_text(text, font_name, size, tracking=0, color=CINE_WHITE):
    fp = os.path.join(FONTS_DIR, font_name)
    font = ImageFont.truetype(fp, size)
    dd = ImageDraw.Draw(Image.new("L", (10, 10)))
    chars = list(text)
    advs = [dd.textlength(c, font=font) for c in chars]
    tw = int(round(sum(advs) + tracking * max(0, len(chars) - 1)))
    bb = dd.textbbox((0, 0), text, font=font)
    th = bb[3] - bb[1]
    pad = 44
    bw, bh = tw + pad * 2, th + pad * 2
    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    cx = float(pad)
    for c, a in zip(chars, advs):
        md.text((int(round(cx)), pad - bb[1]), c, font=font, fill=255)
        cx += a + tracking

    sh = mask.filter(ImageFilter.GaussianBlur(18))
    sh_a = np.clip(np.array(sh, dtype=np.float32) * 0.48, 0, 255).astype(np.uint8)
    sh_im = Image.fromarray(np.dstack([np.zeros_like(sh_a)]*3 + [sh_a]), "RGBA")

    fg_np = np.zeros((bh, bw, 4), dtype=np.uint8)
    fg_np[:, :, :3] = color
    fg_np[:, :, 3] = np.array(mask, dtype=np.uint8)

    out = Image.new("RGBA", (bw, bh + 6), (0, 0, 0, 0))
    out.alpha_composite(sh_im, (0, 4))
    out.alpha_composite(Image.fromarray(fg_np, "RGBA"), (0, 0))
    return out

def paste_c(canvas, im, cx, cy, alpha=1.0, dy=0.0):
    if alpha <= 0.01: return
    layer = im
    if alpha < 0.995:
        arr = np.array(layer, dtype=np.float32)
        arr[:, :, 3] *= alpha
        layer = Image.fromarray(arr.astype(np.uint8), "RGBA")
    canvas.alpha_composite(layer, (int(round(cx - layer.width/2)), int(round(cy - layer.height/2 + dy))))

TITLE_V3_SPECS = [
    ("V3_T01_intro",   0.20,  2.75, "FEEL CHICKEN",       "Nghệ Thuật Gà Rán Hàn Quốc", 380, True),
    ("V3_T02_crispy",  5.25,  7.25, "GIÒN RỤM NÓNG HỔI",  "Chiên vàng chuẩn nhiệt",    1610, False),
    ("V3_T03_glaze",  10.85, 14.20, "ĐẪM SỐT NGŨ VỊ",     "Nấu chậm trên lửa hồng",    1610, False),
    ("V3_T04_taste",  19.45, 22.45, "TRỌN VỊ HÀN QUỐC",   "Gà ngũ vị  •  Mì đen  •  Tokbokki", 1610, False),
]

def render_all_v3_titles():
    out_list = []
    for cid, ts0, ts1, h_txt, s_txt, yc, is_intro in TITLE_V3_SPECS:
        dur = ts1 - ts0
        nf = int(round(dur * FPS))
        h_im = make_single_color_text(h_txt, "Montserrat-Black.ttf" if is_intro else "PlayfairDisplay-Bold.ttf", 68 if is_intro else 58, tracking=6 if is_intro else 3)
        s_im = make_single_color_text(s_txt, "Montserrat-Medium.ttf" if not os.path.exists(os.path.join(FONTS_DIR,"Inter-Medium.ttf")) else "BeVietnamPro-Medium.ttf", 25 if is_intro else 27, tracking=3 if is_intro else 2, color=(230, 228, 222))
        mov_p = os.path.join(TITLE_V3, f"{cid}.mov")
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_p], stdin=subprocess.PIPE)
        for fi in range(nf):
            t = fi / FPS
            fo = ease_io((dur - t) / 0.40) if (dur - t) < 0.40 else 1.0
            frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            a1 = ease_out(t / 0.42) * fo
            a2 = ease_out((t - 0.16) / 0.42) * fo
            paste_c(frm, h_im, W//2, yc, a1, dy=(1.0 - ease_out(t/0.42))*12)
            paste_c(frm, s_im, W//2, yc + 64, a2 * 0.90, dy=(1.0 - ease_out((t-0.16)/0.42))*10)
            p.stdin.write(frm.tobytes())
        p.stdin.close(); p.wait()
        out_list.append((f"{cid}.mov", ts0, ts1))

    # Minimalist Single-Color White End-Card (24.60 - 27.60s over DJI_0312_D.MP4 walk-in!)
    cid = "V3_T05_endcard"
    ts0, ts1 = 24.60, 27.60
    dur = ts1 - ts0
    nf = int(round(dur * FPS))
    b_im = make_single_color_text("FEEL CHICKEN", "Montserrat-Black.ttf", 74, tracking=7)
    a_im = make_single_color_text("38 NGUYỄN ĐÌNH CHIỂU  •  NHA TRANG", "BeVietnamPro-SemiBold.ttf", 28, tracking=2)
    i_im = make_single_color_text("10:00 – 22:00   •   0979 233 139", "BeVietnamPro-Medium.ttf", 25, tracking=2, color=(225, 223, 218))
    rule = Image.new("RGBA", (140, 8), (0, 0, 0, 0))
    ImageDraw.Draw(rule).line([(10, 4), (130, 4)], fill=(247, 245, 240, 160), width=2)

    # Subtle bottom gradient scrim ONLY behind text at bottom so DJI_0312 storefront stays natural & ungraded!
    sc_np = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, H - 1220)
    sc_np[1220:, :, 3] = np.clip((ys ** 1.35) * 185.0, 0, 255).astype(np.uint8)[:, None]
    sc_im = Image.fromarray(sc_np, "RGBA")

    mov_p = os.path.join(TITLE_V3, f"{cid}.mov")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_p], stdin=subprocess.PIPE)
    for fi in range(nf):
        t = fi / FPS
        fo = ease_io((dur - t) / 0.35) if (dur - t) < 0.35 else 1.0
        frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sa = ease_io(min(t / 0.45, 1.0)) * fo
        if sa > 0.02:
            arr = np.array(sc_im, dtype=np.float32); arr[:, :, 3] *= sa
            frm.alpha_composite(Image.fromarray(arr.astype(np.uint8), "RGBA"))
        p1 = ease_out((t - 0.08) / 0.45)
        p2 = ease_out((t - 0.24) / 0.45)
        paste_c(frm, b_im, W//2, 1445, p1 * fo, dy=(1.0 - p1)*14)
        paste_c(frm, rule, W//2, 1515, p2 * fo)
        paste_c(frm, a_im, W//2, 1568, p2 * fo, dy=(1.0 - p2)*10)
        paste_c(frm, i_im, W//2, 1622, p2 * fo * 0.92, dy=(1.0 - p2)*10)
        p.stdin.write(frm.tobytes())
    p.stdin.close(); p.wait()
    out_list.append((f"{cid}.mov", ts0, ts1))
    return out_list

def load_st(path, s0=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error"]
    if s0 > 0: cmd += ["-ss", f"{s0:.3f}"]
    if dur is not None: cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2).copy()

def mix_c(bus, clip, ts, gain=1.0, fi=0.03, fo=0.12):
    c = (clip * gain).copy()
    nfi, nfo = min(len(c), int(fi*SR)), min(len(c), int(fo*SR))
    if nfi > 1: c[:nfi] *= np.linspace(0, 1, nfi, dtype=np.float32)[:, None]
    if nfo > 1: c[-nfo:] *= np.linspace(1, 0, nfo, dtype=np.float32)[:, None]
    i0 = max(0, int(round(ts * SR)))
    if i0 >= len(bus): return
    i1 = min(len(bus), i0 + len(c))
    bus[i0:i1] += c[:i1 - i0]

def save_w(path, arr):
    pcm = (np.clip(arr, -0.99, 0.99) * 32767.0).astype(np.int16)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", path], stdin=subprocess.PIPE)
    p.stdin.write(pcm.tobytes()); p.stdin.close(); p.wait()

def main():
    print("[1/5] Rendering 14 Speed-Ramped UNGRADED (0% Color Filter) 1080x1920@30fps Cinema Shots...")
    with ThreadPoolExecutor(max_workers=4) as ex:
        manifest = list(ex.map(render_ungraded_speedramp_shot, enumerate(V3_SHOTS)))
    json.dump(manifest, open(os.path.join(OUT_DIR, "shots_v3_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("[2/5] Rendering 5 Minimalist Single-Color White Cinema Titles...")
    title_list = render_all_v3_titles()

    print("[3/5] Mixing AL-Dante Dark Trip-Hop ('Slow Cook Honey') + Tactile Cooking ASMR (-14.0 LUFS)...")
    bgm_b  = np.zeros((N_SAMPLES, 2), dtype=np.float32)
    asmr_b = np.zeros((N_SAMPLES, 2), dtype=np.float32)
    sfx_b  = np.zeros((N_SAMPLES, 2), dtype=np.float32)

    # Start Slow Cook Honey at 6.0s so the massive sensual sub-bass bloom at 21s lands right at 15.0s (Crispy Tear & Hero Climax)!
    bgm_raw = load_st(BGM_LOCAL, 6.0, DUR)
    mix_c(bgm_b, bgm_raw, 0.0, gain=0.90, fi=0.15, fo=0.80)

    gas_ig  = load_st(os.path.join(SFX_V2, "sfx_gas_ignite.mp3"), 0.0, 2.0)
    fry_oil = load_st(os.path.join(SFX_V1, "asmr_frying_pan.mp3"), 1.0, 10.0)
    pour_l  = load_st(os.path.join(SFX_V1, "asmr_liquid_pour.mp3"), 0.1, 2.0)
    sticky  = load_st(os.path.join(SFX_V1, "asmr_sauce_sticky.mp3"), 1.5, 2.5)
    crunch  = load_st(os.path.join(SFX_V1, "asmr_crispy_crunch.mp3"), 0.0, 1.8)
    low_hit = load_st(os.path.join(SFX_V1, "sfx_whoosh_low_hit.mp3"), 0.0, 2.5)
    deep_w  = load_st(os.path.join(SFX_V1, "sfx_deep_woosh.mp3"), 0.0, 1.8)

    # Tactile close-up AL Dante cooking foley synced to speed-ramp impacts!
    mix_c(asmr_b, gas_ig,                   0.08, gain=0.55, fi=0.02, fo=0.30) # S01 Stove ignite
    mix_c(asmr_b, fry_oil[:int(3.1*SR)],    4.02, gain=0.50, fi=0.05, fo=0.40) # S04-S05 Oil plunge & golden lift
    mix_c(asmr_b, fry_oil[int(5.0*SR):int(8.3*SR)], 7.35, gain=0.42, fi=0.10, fo=0.45) # S06-S07 Simmer & Wok fire
    mix_c(asmr_b, pour_l[:int(1.8*SR)],    10.90, gain=0.44, fi=0.05, fo=0.30) # S08 Ruby glaze pour
    mix_c(asmr_b, sticky[:int(1.8*SR)],    13.30, gain=0.34, fi=0.10, fo=0.35) # S09 Molten cheddar
    mix_c(asmr_b, crunch,                  17.10, gain=0.78, fi=0.02, fo=0.25) # S11 Crispy steam tear!
    mix_c(asmr_b, sticky[:int(1.5*SR)],    19.50, gain=0.28, fi=0.10, fo=0.30) # S12 Glossy Jajang lift

    # Subtle speed-ramp air whooshes & sub-bass impacts
    for wt in [1.16, 3.96, 8.46, 13.16, 16.86, 22.56]:
        mix_c(sfx_b, deep_w, wt, gain=0.28, fi=0.02, fo=0.25)
    for ht in [8.50, 15.60, 24.58]:
        mix_c(sfx_b, low_hit, ht, gain=0.38, fi=0.02, fo=0.40)

    raw_mix = os.path.join(AUDIO_V3, "mix_v3_raw.wav")
    mst_wav = os.path.join(AUDIO_V3, "master_v3_14lufs.wav")
    save_w(raw_mix, bgm_b + asmr_b + sfx_b)

    p1 = subprocess.run(["ffmpeg", "-v", "info", "-i", raw_mix, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    ln = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p1.stderr).group(0))
    af2 = f"loudnorm=I=-14.0:TP=-1.0:LRA=11.0:measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true,aresample={SR}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_mix, "-af", af2, "-c:a", "pcm_s16le", mst_wav], check=True)

    print("[4/5] Compositing UNGRADED Speed-Ramped Master MP4 + Syncing to All 3 Folders...")
    concat_txt = os.path.join(OUT_DIR, "concat_v3.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for m in manifest:
            p_fwd = m["path"].replace("\\", "/")
            f.write(f"file '{p_fwd}'\n")
    base_mp4 = os.path.join(OUT_DIR, "_base_v3_ungraded.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", base_mp4], check=True)

    inputs = ["-i", base_mp4]
    for t_fn, _, _ in title_list:
        inputs += ["-i", os.path.join(TITLE_V3, t_fn)]
    inputs += ["-i", mst_wav]

    # ZERO color filters, ZERO noise, ZERO LUTs! Pure clean overlay of single-color white titles!
    fc_parts = ["[0:v]format=yuva420p[bg0];"]
    prev = "bg0"
    for idx, (t_fn, ts0, ts1) in enumerate(title_list):
        in_i = 1 + idx
        nxt = f"bg{idx+1}"
        fc_parts.append(f"[{in_i}:v]setpts=PTS+{ts0:.3f}/TB[t{idx}];[{prev}][t{idx}]overlay=0:0:eof_action=pass:enable='between(t,{ts0:.3f},{ts1:.3f})'[{nxt}];")
        prev = nxt
    fc_parts.append(f"[{prev}]trim=0:{DUR:.2f},setpts=PTS-STARTPTS,format=yuv420p[vout]")

    final_local = os.path.join(OUT_DIR, "FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4")
    aud_idx = 1 + len(title_list)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error"] + inputs + [
            "-filter_complex", "".join(fc_parts),
            "-map", "[vout]", "-map", f"{aud_idx}:a",
            "-t", f"{DUR:.2f}", "-r", "30",
            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart",
            final_local
        ],
        check=True
    )

    for dp in [
        r"D:\XUẤT CAPCUT\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
        r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
        r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
    ]:
        shutil.copy2(final_local, dp)
        print("  Synced ->", dp)

    print("[5/5] Deploying UNGRADED CapCut Pro Draft + 12-Frame QC Sheet...")
    def uid(): return str(uuid.uuid4()).upper()
    def us_f(s): return int(round(int(round(float(s)*FPS)) * 1_000_000 / FPS))
    def nfwd(p): return os.path.normpath(p).replace("\\", "/")

    d_tpl = os.path.join(DRAFTS_DIR, "FEEL_CHICKEN_2011_Full_Layers_V6")
    if not os.path.exists(os.path.join(d_tpl, "draft_content.json")):
        d_tpl = os.path.join(DRAFTS_DIR, "F20 vd 1")
    dc_tpl = json.load(open(os.path.join(d_tpl, "draft_content.json"), encoding="utf-8"))
    dm_tpl = json.load(open(os.path.join(d_tpl, "draft_meta_info.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(dc_tpl["tracks"][0])
    atrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "audio"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(next(m for m in dc_tpl["materials"]["videos"] if m.get("type") == "video"))
    amat_tpl   = copy.deepcopy(dc_tpl["materials"]["audios"][0])
    afade_tpl  = copy.deepcopy(dc_tpl["materials"]["audio_fades"][0])
    dm_vid_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    dm_aud_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") in ("music","audio","sound")) if any(x.get("metetype") in ("music","audio","sound") for g in dm_tpl["draft_materials"] for x in g.get("value",[])) else dm_vid_tpl)

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}
    a_extra_keys = ("speeds", "placeholder_infos", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}

    tl_id, now_s, now_us = uid(), int(time.time()), int(time.time() * 1_000_000)
    D = copy.deepcopy(dc_tpl)
    D.update({
        "id": tl_id, "name": DRAFT_NAME, "fps": 30.0, "duration": 0,
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_tpl["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })
    mat_cache, dm_type0, ref_bytes = {}, [], 0

    def reg_vid(path):
        nonlocal ref_bytes
        fwd = nfwd(path)
        if fwd in mat_cache: return mat_cache[fwd]
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
        du_u = max(33333, us_f(float(r.stdout.strip() or 1.0)))
        mid, lmid, fn = uid(), str(uuid.uuid4()), os.path.basename(path)
        m = copy.deepcopy(vmat_tpl)
        m.update({"id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid, "type": "video", "path": fwd, "media_path": "", "local_id": "", "material_name": fn, "width": 1080, "height": 1920, "duration": du_u, "has_audio": False})
        dme = copy.deepcopy(dm_vid_tpl)
        dme.update({"id": lmid, "file_Path": fwd, "extra_info": fn, "duration": du_u, "width": 1080, "height": 1920, "metetype": "video", "item_source": 1, "create_time": now_s, "import_time": now_s, "import_time_ms": now_us, "roughcut_time_range": {"start": 0, "duration": du_u}, "sub_time_range": {"start": -1, "duration": -1}})
        D["materials"]["videos"].append(m); dm_type0.append(dme); ref_bytes += os.path.getsize(path)
        mat_cache[fwd] = (mid, du_u)
        return mid, du_u

    def reg_aud(path):
        nonlocal ref_bytes
        fwd = nfwd(path)
        if fwd in mat_cache: return mat_cache[fwd]
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
        du_u = max(33333, us_f(float(r.stdout.strip() or 1.0)))
        mid, lmid, fn = uid(), str(uuid.uuid4()), os.path.basename(path)
        m = copy.deepcopy(amat_tpl)
        m.update({"id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid, "type": "extract_music", "name": os.path.splitext(fn)[0], "path": fwd, "duration": du_u, "music_id": "", "effect_id": "", "resource_id": "", "source_platform": 0})
        dme = copy.deepcopy(dm_aud_tpl)
        dme.update({"id": lmid, "file_Path": fwd, "extra_info": fn, "duration": du_u, "width": 0, "height": 0, "metetype": "music", "item_source": 1, "create_time": now_s, "import_time": now_s, "import_time_ms": now_us})
        D["materials"]["audios"].append(m); dm_type0.append(dme); ref_bytes += os.path.getsize(path)
        mat_cache[fwd] = (mid, du_u)
        return mid, du_u

    def mk_vseg(path, tl_s, dur_s, ridx=0):
        mid, mdu = reg_vid(path)
        du_u = min(us_f(dur_s), mdu)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, te in v_extra_tpl.items():
            em = copy.deepcopy(te); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        seg.update({"id": uid(), "material_id": mid, "source_timerange": {"start": 0, "duration": du_u}, "target_timerange": {"start": us_f(tl_s), "duration": du_u}, "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0, "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": ridx, "track_render_index": 0, "visible": True})
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}; seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}; seg["clip"]["alpha"] = 1.0; seg["clip"]["rotation"] = 0.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        return seg

    def mk_aseg(path, tl_s, dur_s, src_s=0.0, vol=1.0, fi=40000, fo=120000):
        mid, mdu = reg_aud(path)
        st_u = us_f(src_s)
        du_u = min(us_f(dur_s), max(33333, mdu - st_u))
        seg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, te in a_extra_tpl.items():
            em = copy.deepcopy(te); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        af = copy.deepcopy(afade_tpl); af.update({"id": uid(), "fade_in_duration": min(du_u//3, fi), "fade_out_duration": min(du_u//3, fo)})
        D["materials"]["audio_fades"].append(af); refs.append(af["id"])
        seg.update({"id": uid(), "material_id": mid, "source_timerange": {"start": st_u, "duration": du_u}, "target_timerange": {"start": us_f(tl_s), "duration": du_u}, "speed": 1.0, "volume": float(vol), "last_nonzero_volume": float(max(0.05, vol)), "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": 0, "track_render_index": 1, "visible": True})
        return seg

    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    cur_u = 0
    for m in manifest:
        sg = mk_vseg(m["path"], cur_u / 1e6, m["frames"] / FPS, ridx=0)
        sg["target_timerange"]["start"] = cur_u
        tr_v0["segments"].append(sg)
        cur_u += sg["target_timerange"]["duration"]
    D["tracks"].append(tr_v0)

    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid()
    tr_v1["segments"] = [mk_vseg(os.path.join(TITLE_V3, fn), ts0, ts1 - ts0, ridx=100) for fn, ts0, ts1 in title_list]
    D["tracks"].append(tr_v1)

    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid()
    tr_bgm["segments"] = [mk_aseg(BGM_LOCAL, 0.0, DUR, 6.0, vol=0.90, fi=150000, fo=800000)]
    D["tracks"].append(tr_bgm)

    save_w(os.path.join(AUDIO_V3, "stem_asmr_v3.wav"), asmr_b)
    save_w(os.path.join(AUDIO_V3, "stem_sfx_v3.wav"),  sfx_b)

    tr_asmr = copy.deepcopy(atrack_tpl); tr_asmr["id"] = uid()
    tr_asmr["segments"] = [mk_aseg(os.path.join(AUDIO_V3, "stem_asmr_v3.wav"), 0.0, DUR, 0.0, vol=1.0)]
    D["tracks"].append(tr_asmr)

    tr_sfx = copy.deepcopy(atrack_tpl); tr_sfx["id"] = uid()
    tr_sfx["segments"] = [mk_aseg(os.path.join(AUDIO_V3, "stem_sfx_v3.wav"), 0.0, DUR, 0.0, vol=1.0)]
    D["tracks"].append(tr_sfx)
    D["duration"] = cur_u

    stage_dir = os.path.join(STAGE_V3, DRAFT_NAME)
    if os.path.exists(stage_dir): shutil.rmtree(stage_dir)
    os.makedirs(os.path.join(stage_dir, "Timelines", tl_id, "common_attachment"), exist_ok=True)
    os.makedirs(os.path.join(stage_dir, "common_attachment"), exist_ok=True)

    # Extract 12-frame Final Master Contact Sheet
    pts = [
        (0.65,  "00:00.6 | Stove Ignite + Minimal Title"),
        (2.05,  "00:02.0 | AI Flour Cloud Toss"),
        (4.55,  "00:04.5 | AI Sizzling Oil Plunge"),
        (6.25,  "00:06.2 | AI Dripping Crispy Lift"),
        (9.60,  "00:09.6 | AI Blue-Flame Wok Toss"),
        (12.00, "00:12.0 | AI Ruby Glaze & Sesame"),
        (14.40, "00:14.4 | AI Molten Cheddar Pour"),
        (16.25, "00:16.2 | Slow-Mo Sesame on Black"),
        (18.15, "00:18.1 | AI Steaming Crispy Tear"),
        (20.40, "00:20.4 | AI Steaming Jajang Lift"),
        (23.60, "00:23.6 | AI Hero Drumstick Steam"),
        (26.10, "00:26.1 | New CS1 Walk-In (0312_D)"),
    ]
    W_C, H_C = 320, 568
    sheet = Image.new("RGB", (W_C * 4, H_C * 3), (10, 10, 10))
    dr = ImageDraw.Draw(sheet)
    cover_saved = False
    for i, (ts, lbl) in enumerate(pts):
        jp = os.path.join(CHK_V3, f"fin_v3_{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", final_local, "-frames:v", "1", "-vf", f"scale={W_C}:{H_C},format=yuvj420p", "-q:v", "2", jp], check=True)
        if i == 10 and not cover_saved:
            shutil.copy2(jp, os.path.join(stage_dir, "draft_cover.jpg"))
            shutil.copy2(jp, os.path.join(stage_dir, "Timelines", tl_id, "draft_cover.jpg"))
            cover_saved = True
        ri, ci = divmod(i, 4)
        x, y = ci * W_C, ri * H_C
        sheet.paste(Image.open(jp).convert("RGB"), (x, y))
        dr.rectangle([x, y, x + W_C, y + 24], fill=(0, 0, 0))
        dr.text((x + 6, y + 5), lbl, fill=(242, 240, 235))
        os.remove(jp)

    qc_local = os.path.join(CHK_V3, "FINAL_V3_ALDANTE_12FRAMES_QC.jpg")
    qc_art   = os.path.join(ART_DIR, "fc_food_cinematic_v3_preview.jpg")
    sheet.save(qc_local, quality=92)
    shutil.copy2(qc_local, qc_art)
    shutil.copy2(qc_local, os.path.join(CLOUD_PRJ, "FINAL_V3_ALDANTE_12FRAMES_QC.jpg"))

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for p_dc in [os.path.join(stage_dir, "draft_content.json"), os.path.join(stage_dir, "template-2.tmp"),
                 os.path.join(stage_dir, "Timelines", tl_id, "draft_content.json"), os.path.join(stage_dir, "Timelines", tl_id, "template-2.tmp")]:
        open(p_dc, "wb").write(dc_bytes)

    open(os.path.join(stage_dir, "draft_settings"), "w", encoding="utf-8").write(f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=360\nreal_edit_keys=24\n")
    open(os.path.join(stage_dir, "key_value.json"), "w", encoding="utf-8").write("{}")
    open(os.path.join(stage_dir, "draft_biz_config.json"), "w", encoding="utf-8").write("")
    for aux in ["draft_agency_config.json", "performance_opt_info.json", "timeline_layout.json", "attachment_pc_common.json"]:
        sp = os.path.join(d_tpl, aux)
        if os.path.isfile(sp): shutil.copy2(sp, os.path.join(stage_dir, aux))
    for cad in [os.path.join(stage_dir, "common_attachment"), os.path.join(stage_dir, "Timelines", tl_id, "common_attachment")]:
        open(os.path.join(cad, "attachment_pc_timeline.json"), "w", encoding="utf-8").write('{"reference_lines_config":{"horizontal_lines":[],"is_lock":false,"is_visible":false,"vertical_lines":[]},"safe_area_type":0}')
        open(os.path.join(cad, "attachment_action_scene.json"), "w", encoding="utf-8").write('{"action_scene":{"removed_segments":[],"segment_infos":[]}}')
    json.dump({"draft_materials": [], "draft_virtual_store": [{"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "material_color_tag": "", "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]}, {"type": 1, "value": []}]}, open(os.path.join(stage_dir, "draft_virtual_store.json"), "w", encoding="utf-8"))
    json.dump({"config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False}, "create_time": now_us, "id": tl_id, "main_timeline_id": tl_id, "timelines": [{"create_time": now_us, "id": tl_id, "is_marked_delete": False, "name": "Dòng thời gian 01", "update_time": now_us}], "update_time": now_us, "version": 0}, open(os.path.join(stage_dir, "Timelines", "project.json"), "w", encoding="utf-8"), ensure_ascii=False)

    local_draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)
    M = copy.deepcopy(dm_tpl)
    M.update({"draft_id": DRAFT_ID, "draft_name": DRAFT_NAME, "draft_fold_path": nfwd(local_draft_dir), "draft_root_path": nfwd(DRAFTS_DIR), "draft_cover": "draft_cover.jpg", "draft_new_version": "164.0.0", "tm_duration": cur_u, "tm_draft_create": now_us, "tm_draft_modified": now_us, "draft_timeline_materials_size_": ref_bytes, "cloud_draft_cover": False, "cloud_draft_sync": False, "draft_materials": [{"type": 0, "value": dm_type0}, {"type": 1, "value": []}, {"type": 2, "value": []}, {"type": 3, "value": []}, {"type": 6, "value": []}, {"type": 7, "value": []}, {"type": 8, "value": []}]})
    json.dump(M, open(os.path.join(stage_dir, "draft_meta_info.json"), "w", encoding="utf-8"), ensure_ascii=False)

    if os.path.exists(local_draft_dir): shutil.rmtree(local_draft_dir)
    shutil.copytree(stage_dir, local_draft_dir)

    rm_path = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    rm = json.load(open(rm_path, encoding="utf-8"))
    stores = [s for s in rm.get("all_draft_store", []) if s.get("draft_name") != DRAFT_NAME and s.get("draft_id") != DRAFT_ID]
    te = copy.deepcopy(stores[0])
    te.update({"cloud_draft_cover": False, "cloud_draft_sync": False, "draft_cover": nfwd(local_draft_dir) + "/draft_cover.jpg", "draft_fold_path": nfwd(local_draft_dir), "draft_id": DRAFT_ID, "draft_json_file": nfwd(local_draft_dir) + "/draft_content.json", "draft_name": DRAFT_NAME, "draft_new_version": "164.0.0", "draft_root_path": nfwd(DRAFTS_DIR), "draft_timeline_materials_size": ref_bytes, "streaming_edit_draft_ready": True, "tm_draft_create": now_us, "tm_draft_modified": now_us, "tm_draft_removed": 0, "tm_duration": cur_u})
    rm["all_draft_store"] = [te] + stores
    json.dump(rm, open(rm_path, "w", encoding="utf-8"), ensure_ascii=False)
    print("V3 AL DANTE SPEED-RAMP MASTER & UNGRADED CAPCUT DRAFT COMPLETE!")

if __name__ == "__main__":
    main()
