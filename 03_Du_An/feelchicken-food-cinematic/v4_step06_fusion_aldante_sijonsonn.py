import copy, json, math, os, re, shutil, subprocess, time, uuid
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR   = r"d:\AI\full studio\output\feelchicken-food-cinematic"
SHOTS_V3  = os.path.join(OUT_DIR, "shots_v3_ungraded")
TITLE_V4  = os.path.join(OUT_DIR, "titles_v4_sijonsonn")
AUDIO_V3  = os.path.join(OUT_DIR, "audio_v3")
RAW_V2    = os.path.join(OUT_DIR, "raw_v2")
SFX_V1    = os.path.join(OUT_DIR, "raw_cache", "sfx")
SFX_V2    = os.path.join(RAW_V2, "sfx")
CHK_V4    = os.path.join(OUT_DIR, "check_v4")
STAGE_V4  = os.path.join(OUT_DIR, "capcut_stage_v4")
FONTS_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
ART_DIR   = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-food-cinematic"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_Food_Cinematic_Pro"
DRAFT_ID   = "F94A82E1-63D4-4B89-9E12-7745C280B3A9"

for d in (TITLE_V4, CHK_V4, STAGE_V4, CLOUD_PRJ):
    os.makedirs(d, exist_ok=True)

W, H = 1080, 1920
FPS = 30
DUR = 27.60
TOTAL_FRAMES = int(round(DUR * FPS)) # 828 frames

def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def draw_tracked_rgba(text, font_file, size, tracking=0, color=(255, 255, 255), sh_blur=18, sh_op=0.45):
    fp = os.path.join(FONTS_DIR, font_file)
    font = ImageFont.truetype(fp, size)
    dd = ImageDraw.Draw(Image.new("L", (10, 10)))
    chars = list(text)
    advs = [dd.textlength(c, font=font) for c in chars]
    tw = int(round(sum(advs) + tracking * max(0, len(chars) - 1)))
    bb = dd.textbbox((0, 0), text, font=font)
    th = bb[3] - bb[1]
    pad = 48
    bw, bh = tw + pad * 2, th + pad * 2
    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    cx = float(pad)
    for c, a in zip(chars, advs):
        md.text((int(round(cx)), pad - bb[1]), c, font=font, fill=255)
        cx += a + tracking

    sh = mask.filter(ImageFilter.GaussianBlur(sh_blur))
    sh_a = np.clip(np.array(sh, dtype=np.float32) * sh_op, 0, 255).astype(np.uint8)
    sh_im = Image.fromarray(np.dstack([np.zeros_like(sh_a)]*3 + [sh_a]), "RGBA")

    fg = np.zeros((bh, bw, 4), dtype=np.uint8)
    fg[:, :, :3] = color
    fg[:, :, 3]  = np.array(mask, dtype=np.uint8)

    out = Image.new("RGBA", (bw, bh + 6), (0, 0, 0, 0))
    out.alpha_composite(sh_im, (0, 4))
    out.alpha_composite(Image.fromarray(fg, "RGBA"), (0, 0))
    return out

def paste_c(canvas, im, cx, cy, alpha=1.0, dy=0.0, scale=1.0):
    if alpha <= 0.01: return
    layer = im
    if abs(scale - 1.0) > 0.004:
        nw, nh = max(2, int(round(layer.width * scale))), max(2, int(round(layer.height * scale)))
        layer = layer.resize((nw, nh), Image.LANCZOS)
    if alpha < 0.995:
        arr = np.array(layer, dtype=np.float32)
        arr[:, :, 3] *= alpha
        layer = Image.fromarray(arr.astype(np.uint8), "RGBA")
    canvas.alpha_composite(layer, (int(round(cx - layer.width/2)), int(round(cy - layer.height/2 + dy))))

# ==============================================================================
# 1. RENDER @sijonsonn SIGNATURE TYPOGRAPHY OVERLAYS (PRORES 4444 ALPHA)
# ==============================================================================
def render_sijonsonn_titles():
    amber_gold = (244, 186, 62)   # Warm editorial golden-amber (#F4BA3E) from step_87_shot_1.png!
    pure_white = (250, 248, 244)  # Crisp cinema off-white
    muted_gray = (205, 202, 196)  # Subtle editorial footer gray

    if all(os.path.exists(os.path.join(TITLE_V4, fn)) for fn in ("V4_T01_sijonsonn_opening.mov", "V4_T02_editorial_footer.mov", "V4_T03_endcard.mov")):
        return [
            ("V4_T01_sijonsonn_opening.mov", 0.10, 4.00),
            ("V4_T02_editorial_footer.mov",  0.20, 24.45),
            ("V4_T03_endcard.mov",           24.60, 27.60),
        ]

    # A) Opening Centered 3-Layer Hero Title (0.10s - 4.00s across S01-S03, just like step_87_shot_1.png!)
    #    Layer 1: 'FEEL CHICKEN' (warm amber-gold tracked uppercase)
    #    Layer 2: 'COOKING' (heavy condensed bold white AsapCondensed-Black)
    #    Layer 3: 'Time' (flowing golden-amber cursive script overlapping center of COOKING!)
    eyebrow_im = draw_tracked_rgba("FEEL CHICKEN", "Montserrat-ExtraBold.ttf", 34, tracking=7, color=amber_gold, sh_blur=14, sh_op=0.55)
    main_im    = draw_tracked_rgba("COOKING",      "AsapCondensed-Black.ttf", 168, tracking=10, color=pure_white, sh_blur=22, sh_op=0.55)
    script_im  = draw_tracked_rgba("Time",         "GreatVibes-Regular.ttf",  108, tracking=0,  color=amber_gold, sh_blur=14, sh_op=0.62)

    t0_open, t1_open = 0.10, 4.00
    nf_open = int(round((t1_open - t0_open) * FPS))
    mov_open = os.path.join(TITLE_V4, "V4_T01_sijonsonn_opening.mov")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_open], stdin=subprocess.PIPE)
    for fi in range(nf_open):
        t = fi / FPS
        dur = t1_open - t0_open
        fo = ease_io((dur - t) / 0.42) if (dur - t) < 0.42 else 1.0
        frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        p_main = ease_out(t / 0.42)
        p_eyeb = ease_out((t - 0.10) / 0.40)
        p_scrp = ease_out((t - 0.22) / 0.45)

        yc = 930
        paste_c(frm, main_im,    W//2, yc,      p_main * fo, scale=0.94 + 0.06 * p_main)
        paste_c(frm, eyebrow_im, W//2, yc - 86, p_eyeb * fo, dy=(1.0 - p_eyeb) * 10)
        paste_c(frm, script_im,  W//2, yc + 18, p_scrp * fo, scale=0.90 + 0.10 * p_scrp)
        p.stdin.write(frm.tobytes())
    p.stdin.close(); p.wait()

    # B) Subtle Persistent Editorial Footer ('Feel Chicken  |  38 Nguyễn Đình Chiểu' from 0.20s to 24.40s)
    footer_im = draw_tracked_rgba("Feel Chicken  |  38 Nguyễn Đình Chiểu", "Inter-Medium.ttf", 23, tracking=2, color=muted_gray, sh_blur=10, sh_op=0.55)
    t0_ft, t1_ft = 0.20, 24.45
    nf_ft = int(round((t1_ft - t0_ft) * FPS))
    mov_ft = os.path.join(TITLE_V4, "V4_T02_editorial_footer.mov")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_ft], stdin=subprocess.PIPE)
    for fi in range(nf_ft):
        t = fi / FPS
        dur = t1_ft - t0_ft
        a = ease_io(min(t / 0.5, 1.0)) * (ease_io((dur - t) / 0.4) if (dur - t) < 0.4 else 1.0) * 0.72
        frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        paste_c(frm, footer_im, W//2, 1785, a)
        p.stdin.write(frm.tobytes())
    p.stdin.close(); p.wait()

    # C) Matching Editorial End-Card over New CS1 Walk-In DJI_0312_D (24.60s - 27.60s)
    end_eyeb = draw_tracked_rgba("KOREAN FRIED CHICKEN", "Montserrat-Bold.ttf", 26, tracking=6, color=amber_gold, sh_blur=14, sh_op=0.60)
    end_main = draw_tracked_rgba("FEEL CHICKEN", "AsapCondensed-Black.ttf", 124, tracking=8, color=pure_white, sh_blur=20, sh_op=0.60)
    end_scrp = draw_tracked_rgba("Ăn là mê", "GreatVibes-Regular.ttf", 78, tracking=0, color=amber_gold, sh_blur=14, sh_op=0.62)
    end_addr = draw_tracked_rgba("38 NGUYỄN ĐÌNH CHIỂU  •  NHA TRANG", "BeVietnamPro-SemiBold.ttf", 28, tracking=2, color=pure_white, sh_blur=14, sh_op=0.65)
    end_info = draw_tracked_rgba("10:00 – 22:00   •   0979 233 139", "BeVietnamPro-Medium.ttf", 25, tracking=2, color=(228, 226, 220), sh_blur=14, sh_op=0.65)

    sc_np = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, H - 1160)
    sc_np[1160:, :, 3] = np.clip((ys ** 1.3) * 195.0, 0, 255).astype(np.uint8)[:, None]
    sc_im = Image.fromarray(sc_np, "RGBA")

    t0_end, t1_end = 24.60, 27.60
    nf_end = int(round((t1_end - t0_end) * FPS))
    mov_end = os.path.join(TITLE_V4, "V4_T03_endcard.mov")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_end], stdin=subprocess.PIPE)
    for fi in range(nf_end):
        t = fi / FPS
        dur = t1_end - t0_end
        fo = ease_io((dur - t) / 0.35) if (dur - t) < 0.35 else 1.0
        frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sa = ease_io(min(t / 0.45, 1.0)) * fo
        if sa > 0.02:
            arr = np.array(sc_im, dtype=np.float32); arr[:, :, 3] *= sa
            frm.alpha_composite(Image.fromarray(arr.astype(np.uint8), "RGBA"))

        p1 = ease_out((t - 0.06) / 0.44)
        p2 = ease_out((t - 0.22) / 0.44)
        paste_c(frm, end_eyeb, W//2, 1345, p1 * fo, dy=(1.0 - p1)*10)
        paste_c(frm, end_main, W//2, 1430, p1 * fo, scale=0.95 + 0.05*p1)
        paste_c(frm, end_scrp, W//2, 1495, p2 * fo)
        paste_c(frm, end_addr, W//2, 1595, p2 * fo, dy=(1.0 - p2)*10)
        paste_c(frm, end_info, W//2, 1648, p2 * fo * 0.92, dy=(1.0 - p2)*10)
        p.stdin.write(frm.tobytes())
    p.stdin.close(); p.wait()

    return [
        ("V4_T01_sijonsonn_opening.mov", t0_open, t1_open),
        ("V4_T02_editorial_footer.mov",  t0_ft,   t1_ft),
        ("V4_T03_endcard.mov",           t0_end,  t1_end),
    ]

# ==============================================================================
# 2. APPLY THE 3 SIGNATURE @sijonsonn TRANSITIONS DIRECTLY ON CUT BOUNDARIES!
#    (ZERO global color grading on shots - 100% original natural colors preserved!)
# ==============================================================================
def build_transitioned_video(base_v3_mp4: str, out_base_v4_mp4: str):
    """
    Streams the 828 ungraded frames of _base_v3_ungraded.mp4 and weaves in @sijonsonn's 3 signature transitions:
    1) Frame 324 (10.80s - S07->S08 Ruby Glaze Hit): 6-frame B&W Monochrome Beat-Flash Snap -> pops into rich natural ruby color!
    2) Frame 507 (16.90s - S10->S11 Crispy Steam Tear, matching step_87_shot_10.png!): 9-frame 3-Column Vertical Shutter-Slice Whip with vertical motion blur!
    3) Frame 678 (22.60s - S13->S14 Hero Drumstick Steam Lift): 9-frame Warm Analog Film-Burn Flash!
    """
    dec = subprocess.Popen([
        "ffmpeg", "-v", "error", "-i", base_v3_mp4,
        "-vf", f"fps={FPS},scale={W}:{H},format=rgb24", "-f", "rawvideo", "-"
    ], stdout=subprocess.PIPE)
    raw_all = dec.stdout.read()
    dec.wait()
    fsz = W * H * 3
    nf = min(TOTAL_FRAMES, len(raw_all) // fsz)
    frames = np.frombuffer(raw_all[:nf * fsz], dtype=np.uint8).reshape((nf, H, W, 3)).copy()

    # --- Transition 1: B&W Monochrome Beat-Flash at f = 324..330 (10.80s..11.00s) ---
    for k, fi in enumerate(range(322, 330)):
        if 0 <= fi < nf:
            f_rgb = frames[fi].astype(np.float32)
            luma = (0.299 * f_rgb[:, :, 0] + 0.587 * f_rgb[:, :, 1] + 0.114 * f_rgb[:, :, 2])[:, :, None]
            # High-contrast B&W snap on beat, snapping 100% back to vivid natural color at fi=330!
            bw = np.clip((luma - 128.0) * 1.18 + 128.0, 0, 255)
            mix = 1.0 if k < 5 else (1.0 - (k - 4) / 3.0)
            frames[fi] = np.clip(f_rgb * (1.0 - mix) + bw * mix, 0, 255).astype(np.uint8)

    # --- Transition 2: 3-Column Vertical Shutter-Slice Whip at cut f = 507 (16.90s, matching step_87_shot_10.png!) ---
    # Blend outgoing clip A (frames around 506) and incoming clip B (frames around 507) across fi = 503..511!
    snap_A = frames[506].copy()
    snap_B = frames[507].copy()
    # Add vertical motion-blur versions of A & B for authentic shutter-whip feel!
    ker_len = 26
    def vblur(arr):
        pad = np.pad(arr.astype(np.float32), ((ker_len//2, ker_len//2), (0, 0), (0, 0)), mode="edge")
        csum = np.cumsum(pad, axis=0)
        return np.clip((csum[ker_len:] - csum[:-ker_len]) / ker_len, 0, 255).astype(np.uint8)
    blur_A = vblur(snap_A)
    blur_B = vblur(snap_B)

    col_w = W // 3 # 360px per column (3 columns exact like step_87_shot_10.png!)
    t_len = 9
    for idx_t, fi in enumerate(range(503, 503 + t_len)):
        p = (idx_t + 1) / (t_len + 1)
        ep = ease_io(p)
        comp = np.zeros((H, W, 3), dtype=np.uint8)
        for col in range(3):
            x0, x1 = col * col_w, (W if col == 2 else (col + 1) * col_w)
            # Staggered vertical whip: col 0 slides DOWN, col 1 slides UP, col 2 slides DOWN!
            p_col = np.clip((p - col * 0.08) / 0.84, 0.0, 1.0)
            ec = ease_io(p_col)
            use_blur = 0.12 < p_col < 0.88
            srcA = blur_A if use_blur else frames[min(506, fi)]
            srcB = blur_B if use_blur else frames[max(507, fi)]
            split_y = int(round(ec * H))
            if col % 2 == 0:
                # Incoming B slides DOWN from top
                if split_y > 0:
                    comp[:split_y, x0:x1] = srcB[H - split_y:, x0:x1]
                if split_y < H:
                    comp[split_y:, x0:x1] = srcA[:H - split_y, x0:x1]
            else:
                # Incoming B slides UP from bottom
                if split_y > 0:
                    comp[H - split_y:, x0:x1] = srcB[:split_y, x0:x1]
                if split_y < H:
                    comp[:H - split_y, x0:x1] = srcA[split_y:, x0:x1]
            # Crisp thin dark shutter seam line like step_87_shot_10.png
            if col > 0:
                comp[:, x0:x0+2] = (comp[:, x0:x0+2].astype(np.float32) * 0.35).astype(np.uint8)
        frames[fi] = comp

    # --- Transition 3: Warm Analog Film-Burn Flash ONLY across cut f = 675..683 (22.50..22.77s) ---
    yy = np.linspace(-1.0, 1.0, H)[:, None]
    xx = np.linspace(-1.0, 1.0, W)[None, :]
    burn_mask = np.exp(-((xx + 0.35)**2 * 1.4 + (yy - 0.10)**2 * 1.1))
    burn_rgb = np.zeros((H, W, 3), dtype=np.float32)
    burn_rgb[:, :, 0] = 255.0
    burn_rgb[:, :, 1] = 128.0
    burn_rgb[:, :, 2] = 24.0
    for idx_b, fi in enumerate(range(674, 684)):
        # Bell curve peaking right at cut frame 678 (22.60s), 0 outside!
        u = (idx_b + 0.5) / 10.0
        strength = math.sin(math.pi * u) ** 2.0 * 0.78
        a_burn = (burn_mask * strength)[:, :, None]
        f_orig = frames[fi].astype(np.float32)
        # Screen blend strictly in float RGB!
        scr = 255.0 - (255.0 - f_orig) * (255.0 - burn_rgb * a_burn) / 255.0
        frames[fi] = np.clip(scr, 0, 255).astype(np.uint8)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out_base_v4_mp4
    ], stdin=subprocess.PIPE)
    for frm in frames:
        enc.stdin.write(frm.tobytes())
    enc.stdin.close()
    enc.wait()

def main():
    print("[1/4] Rendering @sijonsonn 'FEEL CHICKEN / COOKING Time' 3-Layer Hero Title + Editorial Footer + End-Card...")
    title_list = render_sijonsonn_titles()

    print("[2/4] Weaving @sijonsonn's 3 Signature Transitions (B&W Beat Flash, 3-Col Vertical Shutter-Slice, Analog Film-Burn)...")
    base_v3 = os.path.join(OUT_DIR, "_base_v3_ungraded.mp4")
    base_v4 = os.path.join(OUT_DIR, "_base_v4_sijonsonn_transitions.mp4")
    build_transitioned_video(base_v3, base_v4)

    # Add subtle camera shutter/whip SFX at the 3 signature transitions into master audio!
    SR = 48000
    N_S = int(round(DUR * SR))
    mst_v3 = os.path.join(AUDIO_V3, "master_v3_14lufs.wav")
    raw_v3 = os.path.join(AUDIO_V3, "mix_v3_raw.wav")
    r_aud = subprocess.run(["ffmpeg", "-v", "error", "-i", raw_v3, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    mix_arr = np.frombuffer(r_aud.stdout, dtype=np.float32).reshape(-1, 2).copy()[:N_S]

    fw_p = os.path.join(SFX_V1, "sfx_fast_whoosh.mp3")
    if os.path.exists(fw_p):
        fw = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-t", "1.2", "-i", fw_p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2)
        for ts_tr, gn in [(10.76, 0.30), (16.78, 0.42), (22.48, 0.34)]:
            i0 = int(round(ts_tr * SR))
            i1 = min(N_S, i0 + len(fw))
            mix_arr[i0:i1] += fw[:i1 - i0] * gn

    raw_v4 = os.path.join(AUDIO_V3, "mix_v4_raw.wav")
    mst_v4 = os.path.join(AUDIO_V3, "master_v4_14lufs.wav")
    pcm = (np.clip(mix_arr, -0.99, 0.99) * 32767.0).astype(np.int16)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", raw_v4], stdin=subprocess.PIPE)
    p.stdin.write(pcm.tobytes()); p.stdin.close(); p.wait()

    p1 = subprocess.run(["ffmpeg", "-v", "info", "-i", raw_v4, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    ln = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p1.stderr).group(0))
    af2 = f"loudnorm=I=-14.0:TP=-1.0:LRA=11.0:measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true,aresample={SR}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_v4, "-af", af2, "-c:a", "pcm_s16le", mst_v4], check=True)

    print("[3/4] Encoding Final V4 Fusion Master MP4 + Syncing to All 3 Folders...")
    inputs = ["-i", base_v4]
    for fn, _, _ in title_list:
        inputs += ["-i", os.path.join(TITLE_V4, fn)]
    inputs += ["-i", mst_v4]

    fc_parts = ["[0:v]format=yuva420p[bg0];"]
    prev = "bg0"
    for idx, (fn, ts0, ts1) in enumerate(title_list):
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

    print("[4/4] Updating CapCut Pro Draft with V4 Sijonsonn Title Overlays + Extracting 12-Frame QC Sheet...")
    # Update CapCut Pro Draft Track V1 with the new V4 Sijonsonn Title MOVs while keeping Track V0 as the 15 separate ungraded clips!
    local_draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)
    dc_path = os.path.join(local_draft_dir, "draft_content.json")
    dm_path = os.path.join(local_draft_dir, "draft_meta_info.json")
    if os.path.exists(dc_path):
        D = json.load(open(dc_path, encoding="utf-8"))
        M = json.load(open(dm_path, encoding="utf-8"))
        vmat_tpl = copy.deepcopy(D["materials"]["videos"][0])
        vseg_tpl = copy.deepcopy(D["tracks"][0]["segments"][0])
        dm_vid_tpl = copy.deepcopy(M["draft_materials"][0]["value"][0])
        now_s, now_us = int(time.time()), int(time.time() * 1_000_000)

        def uid(): return str(uuid.uuid4()).upper()
        def us_f(s): return int(round(int(round(float(s)*FPS)) * 1_000_000 / FPS))
        def nfwd(p): return os.path.normpath(p).replace("\\", "/")

        new_t_segs = []
        for fn, ts0, ts1 in title_list:
            tp = os.path.join(TITLE_V4, fn)
            fwd = nfwd(tp)
            du_u = us_f(ts1 - ts0)
            mid, lmid = uid(), str(uuid.uuid4())
            vm = copy.deepcopy(vmat_tpl)
            vm.update({"id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid, "type": "video", "path": fwd, "material_name": fn, "width": 1080, "height": 1920, "duration": du_u, "has_audio": False})
            D["materials"]["videos"].append(vm)
            dme = copy.deepcopy(dm_vid_tpl)
            dme.update({"id": lmid, "file_Path": fwd, "extra_info": fn, "duration": du_u, "width": 1080, "height": 1920, "metetype": "video", "item_source": 1, "create_time": now_s, "import_time": now_s, "import_time_ms": now_us})
            M["draft_materials"][0]["value"].append(dme)

            sg = copy.deepcopy(vseg_tpl)
            sg.update({"id": uid(), "material_id": mid, "source_timerange": {"start": 0, "duration": du_u}, "target_timerange": {"start": us_f(ts0), "duration": du_u}, "render_index": 100})
            new_t_segs.append(sg)

        # Put V4_T01 & V4_T03 on Track V1 (no overlap: 0.10-4.00 & 24.60-27.60) and V4_T02 footer on Track V2!
        tr_t1 = copy.deepcopy(D["tracks"][1]); tr_t1["id"] = uid(); tr_t1["segments"] = [new_t_segs[0], new_t_segs[2]]
        tr_t2 = copy.deepcopy(D["tracks"][1]); tr_t2["id"] = uid(); tr_t2["segments"] = [new_t_segs[1]]
        D["tracks"] = [D["tracks"][0], tr_t1, tr_t2] + D["tracks"][2:]

        dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
        open(dc_path, "wb").write(dc_bytes)
        open(os.path.join(local_draft_dir, "template-2.tmp"), "wb").write(dc_bytes)
        tl_dir = os.path.join(local_draft_dir, "Timelines", D["id"])
        if os.path.exists(tl_dir):
            open(os.path.join(tl_dir, "draft_content.json"), "wb").write(dc_bytes)
            open(os.path.join(tl_dir, "template-2.tmp"), "wb").write(dc_bytes)
        json.dump(M, open(dm_path, "w", encoding="utf-8"), ensure_ascii=False)

    # Extract 12-frame QC sheet showing the Opening COOKING Time lockup, B&W flash, 3-Col Shutter Whip, Film-Burn, AI Hero shots & CS1 Walk-in!
    pts = [
        (0.85,  "00:00.8 | Sijonsonn COOKING Time Title"),
        (2.10,  "00:02.1 | Title Hold + AI Flour Cloud"),
        (4.55,  "00:04.5 | AI Sizzling Oil Plunge"),
        (6.25,  "00:06.2 | AI Dripping Crispy Lift"),
        (9.60,  "00:09.6 | AI Blue-Flame Wok Toss"),
        (10.85, "00:10.8 | B&W Beat-Flash Transition!"),
        (12.20, "00:12.2 | AI Ruby Glaze & Sesame"),
        (14.40, "00:14.4 | AI Molten Cheddar Pour"),
        (16.90, "00:16.9 | 3-Col Shutter-Slice Whip!"),
        (18.20, "00:18.2 | AI Steaming Crispy Tear"),
        (23.60, "00:23.6 | AI Hero Drumstick Steam"),
        (26.20, "00:26.2 | New CS1 Walk-In + End-Card"),
    ]
    W_C, H_C = 320, 568
    sheet = Image.new("RGB", (W_C * 4, H_C * 3), (10, 10, 10))
    dr = ImageDraw.Draw(sheet)
    for i, (ts, lbl) in enumerate(pts):
        jp = os.path.join(CHK_V4, f"fv4_{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", final_local, "-frames:v", "1", "-vf", f"scale={W_C}:{H_C},format=yuvj420p", "-q:v", "2", jp], check=True)
        ri, ci = divmod(i, 4)
        x, y = ci * W_C, ri * H_C
        sheet.paste(Image.open(jp).convert("RGB"), (x, y))
        dr.rectangle([x, y, x + W_C, y + 24], fill=(0, 0, 0))
        dr.text((x + 6, y + 5), lbl, fill=(244, 196, 82))
        os.remove(jp)

    qc_local = os.path.join(CHK_V4, "FINAL_V4_FUSION_12FRAMES_QC.jpg")
    qc_art   = os.path.join(ART_DIR, "fc_food_cinematic_v4_fusion_preview.jpg")
    sheet.save(qc_local, quality=92)
    shutil.copy2(qc_local, qc_art)
    shutil.copy2(qc_local, os.path.join(CLOUD_PRJ, "FINAL_V4_FUSION_12FRAMES_QC.jpg"))
    print("V4 AL-DANTE x SIJONSONN FUSION COMPLETE!")

if __name__ == "__main__":
    main()
