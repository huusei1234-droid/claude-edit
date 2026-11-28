import copy, json, math, os, re, shutil, subprocess, sys, time, uuid
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from safe_zone_9x16 import audit_rgba_overlay_safe_zone

OUT_DIR   = r"d:\AI\full studio\output\feelchicken-spicy-squid-cinematic"
FLOW_916  = os.path.join(OUT_DIR, "flow_clips_9x16")
FLOW_169  = os.path.join(OUT_DIR, "flow_clips_16x9")
MUSE_916  = os.path.join(OUT_DIR, "muse_clips_9x16")
MUSE_169  = os.path.join(OUT_DIR, "muse_clips_16x9")
V2_CLIPS  = os.path.join(OUT_DIR, "v2_macro_wide_clips")
AUD_STG   = os.path.join(OUT_DIR, "audio_stage")
WORK_V2   = os.path.join(OUT_DIR, "work_v2_cinema")
QC_DIR    = os.path.join(OUT_DIR, "qc_sheets")
FONT_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
ART_DIR   = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-spicy-squid-cinematic"
DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
EFFECT_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Cache\effect")

os.makedirs(WORK_V2, exist_ok=True)
os.makedirs(QC_DIR, exist_ok=True)

FPS = 30
SR  = 48000
TOTAL_FRAMES = 720
TOTAL_DUR = TOTAL_FRAMES / float(FPS)  # Exact 24.000s

# ==============================================================================
# 1. EXACT 12-SHOT BEAT-SYNCED DIRECTOR'S CUT PLAN
#    - Strict CẬN <-> TOÀN alternation on EVERY cut!
#    - Every cut frame [46, 98, 164, 216, 282, 334, 400, 452, 518, 570, 636] is an exact detected kick/snare hit!
#    - Selective Speed-Ramping: ONLY 4 climax shots (#3, #5, #9, #11 on the 4 heavy 808 drops!) have speed-ramps;
#      the other 8 shots use clean constant speed (steady slow glide or crisp fast rhythm) for natural contrast!
# ==============================================================================
DIRECTORS_PLAN = [
    # (idx, shot_id, scale_tag, f_in, f_out, speed_mode, bank, base_name)
    (1,  "01_WIDE_Flame_Intro",     "TOÀN",       0,  46, "const_0.85", "v2",   "m00_wide_dark_flame_intro"),
    (2,  "02_ECU_Chili_Oil",        "CẬN ĐẶC TẢ",46,  98, "const_1.15", "v2",   "m01_ecu_chili_oil_spice"),
    (3,  "03_WIDE_ZeroG_Squid",     "TOÀN",      98, 164, "RAMP_DROP",  "muse", "s02_zero_g_squid_whip"),      # 808 DROP #1 @ 3.267s!
    (4,  "04_ECU_Squid_Rings",      "CẬN ĐẶC TẢ",164,216, "const_0.80", "v2",   "m02_ecu_squid_rings_glaze"),
    (5,  "05_WIDE_Wok_Fire",        "TOÀN",     216, 282, "RAMP_WHIP",  "flow", "s03_wok_fire_toss"),          # 808 DROP #2 @ 7.200s!
    (6,  "06_ECU_Boiling_Ramen",    "CẬN ĐẶC TẢ",282,334, "const_1.15", "v2",   "m03_ecu_boiling_ramen_bubbles"),
    (7,  "07_WIDE_Exploded_Stack",  "TOÀN",     334, 400, "const_0.75", "flow", "s04_exploded_levitation"),    # 808 DROP #3 @ 11.133s!
    (8,  "08_CU_Crimson_Wave",      "CẬN",      400, 452, "const_1.25", "muse", "s01_chili_wave"),
    (9,  "09_WIDE_Crown_Splash",    "TOÀN",     452, 518, "RAMP_DROP",  "flow", "s05_broth_crown_splash"),     # 808 DROP #4 @ 15.067s!
    (10, "10_ECU_Tentacles_Boil",   "CẬN ĐẶC TẢ",518,570, "const_0.82", "muse", "s06_macro_boiling_glaze"),
    (11, "11_MED_Chopstick_Lift",   "TRUNG-TOÀN",570,636, "RAMP_LIFT",  "flow", "s07_chopstick_tower_lift"),   # 808 DROP #5 @ 19.000s!
    (12, "12_WIDE_Hero_Pot_Outro",  "TOÀN",     636, 720, "const_0.78", "flow", "s08_hero_stone_pot"),
]

def resolve_clip_path(bank: str, base_name: str, is_916: bool) -> str:
    if bank == "v2":
        suf = "9x16" if is_916 else "16x9"
        return os.path.join(V2_CLIPS, f"{base_name}_{suf}.mp4")
    if bank == "muse":
        d = MUSE_916 if is_916 else MUSE_169
        suf = "9x16_muse" if is_916 else "16x9_muse"
        return os.path.join(d, f"{base_name}_{suf}.mp4")
    d = FLOW_916 if is_916 else FLOW_169
    suf = "9x16" if is_916 else "16x9"
    return os.path.join(d, f"{base_name}_{suf}.mp4")

def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    p = os.path.join(FONT_DIR, name)
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    win_f = os.path.join(r"C:\Windows\Fonts", name)
    if os.path.exists(win_f):
        return ImageFont.truetype(win_f, size)
    return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", size)

def ease_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_io(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

# ==============================================================================
# 2. PURE FLAT SINGLE-COLOR STROKE-FREE CENTERED CINEMA TYPOGRAPHY
#    - 100% 1 Single Color (#F7F5F0 Pure Warm Cinema White)
#    - ZERO stroke (stroke_width = 0), ZERO gradient, ZERO boxes/borders!
#    - 100% Locked Dead-Center at (W // 2, H // 2)!
# ==============================================================================
CINEMA_WHITE = (247, 245, 240)

def draw_tracked_centered(draw: ImageDraw.ImageDraw, cx: int, cy: int, text: str, font: ImageFont.FreeTypeFont, tracking: int, alpha: int):
    if alpha <= 2:
        return
    chars = list(text)
    widths = [draw.textlength(ch, font=font) for ch in chars]
    total_w = sum(widths) + tracking * max(0, len(chars) - 1)
    bb = draw.textbbox((0, 0), text, font=font)
    th = bb[3] - bb[1]
    x = cx - total_w / 2.0
    y = cy - th / 2.0 - bb[1]
    col = (CINEMA_WHITE[0], CINEMA_WHITE[1], CINEMA_WHITE[2], max(0, min(255, int(alpha))))
    for ch, cw in zip(chars, widths):
        draw.text((x, y), ch, font=font, fill=col)  # ZERO stroke!
        x += cw + tracking

def render_pure_flat_centered_title_rgba(t: float, W: int, H: int) -> tuple[Image.Image | None, float]:
    """
    Returns (rgba_overlay_or_None, bg_dim_factor_0_to_1).
     bg_dim_factor gently lowers exposure across the WHOLE frame (no ugly box!) so pure flat 1-color white text
    reads with crisp A24 / Netflix Chef's Table cinema contrast dead-center at (W//2, H//2)!
    """
    is_916 = (H > W)
    cx, cy = W // 2, H // 2  # EXACT DEAD-CENTER OF FRAME!

    # A. OPENING CENTERED CINEMA TITLE: [0.10s .. 1.48s] (Shot 01 Wide Dark Flame)
    if 0.10 <= t <= 1.48:
        lt = t - 0.10
        dur = 1.38
        pin = ease_out(min(1.0, lt / 0.26))
        pout = ease_io(min(1.0, (dur - lt) / 0.22))
        vis = pin * pout

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        f_eyeb = fnt("BeVietnamPro-Medium.ttf", 20 if is_916 else 22)
        f_main = fnt("BarlowCondensed-Bold.ttf", 104 if is_916 else 112)
        f_sub  = fnt("BeVietnamPro-Medium.ttf", 21 if is_916 else 22)

        dy = int(round((1.0 - pin) * 12))
        draw_tracked_centered(dr, cx, cy - 82 + dy, "FEEL CHICKEN", f_eyeb, 8, int(215 * vis))
        draw_tracked_centered(dr, cx, cy +  2 + dy, "MÌ CAY MỰC",  f_main, 5, int(255 * vis))
        draw_tracked_centered(dr, cx, cy + 84 + dy, "KHỔNG LỒ  •  250G – 300G", f_sub, 4, int(220 * vis))

        blur_px = max((1.0 - pin) * 10.0, (1.0 - pout) * 8.0)
        if blur_px > 0.5:
            layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_px))
        return layer, 0.22 * vis

    # B. CLOSING CENTERED CINEMA END-CARD: [21.35s .. 23.92s] (Shot 12 Wide Hero Pot)
    if 21.35 <= t <= 23.92:
        lt = t - 21.35
        dur = 2.57
        pin1 = ease_out(min(1.0, lt / 0.32))
        pin2 = ease_out(min(1.0, max(0.0, (lt - 0.14) / 0.32)))
        pout = ease_io(min(1.0, (dur - lt) / 0.28))

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        f_eyeb = fnt("BeVietnamPro-Medium.ttf", 19 if is_916 else 21)
        f_main = fnt("BarlowCondensed-Bold.ttf", 96 if is_916 else 104)
        f_mid  = fnt("BeVietnamPro-SemiBold.ttf", 22 if is_916 else 24)
        f_addr = fnt("BeVietnamPro-Medium.ttf", 18 if is_916 else 20)

        dy1 = int(round((1.0 - pin1) * 12))
        dy2 = int(round((1.0 - pin2) * 10))

        # Keep width compact (<= 650px on 9:16) so dead-center X=540 stays 100% inside Safe-Zone [54..884]!
        draw_tracked_centered(dr, cx, cy - 102 + dy1, "MÌ CAY MỰC KHỔNG LỒ  •  250G – 300G", f_eyeb, 3, int(215 * pin1 * pout))
        draw_tracked_centered(dr, cx, cy -  18 + dy1, "FEEL CHICKEN", f_main, 6, int(255 * pin1 * pout))

        # Minimal 1px flat white hairline
        hl_a = int(145 * pin2 * pout)
        if hl_a > 4:
            dr.line([(cx - 48, cy + 44 + dy2), (cx + 48, cy + 44 + dy2)], fill=(247, 245, 240, hl_a), width=1)

        draw_tracked_centered(dr, cx, cy +  74 + dy2, "GIÁ RA MẮT 99K  •  ĐỦ 7 CẤP ĐỘ CAY", f_mid, 2, int(242 * pin2 * pout))
        draw_tracked_centered(dr, cx, cy + 112 + dy2, "38 NGUYỄN ĐÌNH CHIỂU  •  35 TRẦN HỮU DUYỆT", f_addr, 1, int(205 * pin2 * pout))
        draw_tracked_centered(dr, cx, cy + 144 + dy2, "10:00 – 22:00   •   0796 601 106", f_addr, 2, int(205 * pin2 * pout))

        blur_px = max((1.0 - pin1) * 9.0, (1.0 - pout) * 8.0)
        if blur_px > 0.5:
            layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_px))
        # Smooth full-frame optical dim (ZERO rectangle box!) so pure flat white text pops cleanly
        return layer, 0.44 * pin1 * pout

    return None, 0.0


# ==============================================================================
# 3. SELECTIVE SPEED-RAMP vs CONSTANT SPEED RENDERER
# ==============================================================================
def heal_corner(rgb_arr: np.ndarray) -> np.ndarray:
    out = rgb_arr.copy()
    h, w, _ = out.shape
    y1, y2 = int(h * 0.910), int(h * 0.988)
    x1, x2 = int(w * 0.835), int(w * 0.985)
    top = out[y1-2:y1, x1:x2].mean(axis=0, keepdims=True).astype(np.float32)
    bot = out[y2:min(h, y2+2), x1:x2].mean(axis=0, keepdims=True).astype(np.float32)
    lft = out[y1:y2, x1-2:x1].mean(axis=1, keepdims=True).astype(np.float32)
    rgt = out[y1:y2, x2:min(w, x2+2)].mean(axis=1, keepdims=True).astype(np.float32)
    wy = np.linspace(0.0, 1.0, y2 - y1)[:, None, None]
    wx = np.linspace(0.0, 1.0, x2 - x1)[None, :, None]
    out[y1:y2, x1:x2] = np.clip(((1.0 - wy) * top + wy * bot) * 0.55 + ((1.0 - wx) * lft + wx * rgt) * 0.45, 0, 255).astype(np.uint8)
    return out

def sample_curve(n_out: int, speed_mode: str, n_src: int, src_fps: float) -> np.ndarray:
    """
    - For 'const_X.XX': strictly LINEAR constant speed (no speed ramp!) — natural steady pacing!
    - For 'RAMP_*': genuine dramatic Whip-Fast -> Slow-Mo Freeze -> Whip-Fast speed-ramp!
    """
    max_idx = max(1.0, float(n_src - 3))
    start_idx = 2.0 if n_src > 16 else 0.0
    avail = max(1.0, max_idx - start_idx)

    if speed_mode.startswith("const_"):
        spd_val = float(speed_mode.split("_")[1])
        # Linear constant step: spd_val * (src_fps / FPS) source frames per output frame
        step = spd_val * (src_fps / float(FPS))
        span = min(avail, step * max(1, n_out - 1))
        # Center the window on the juiciest middle part of the source clip
        s0 = start_idx + max(0.0, (avail - span) * 0.35)
        return np.linspace(s0, s0 + span, n_out)

    u = np.linspace(0.0, 1.0, n_out)
    if speed_mode == "RAMP_DROP":
        # Fast whip in (2.4x) -> Sudden deep 0.38x slow-motion hold right after the beat drop -> Fast whip out (2.1x)
        inst = 0.38 + 2.15 * (np.abs(2.0 * u - 0.88) ** 2.4)
    elif speed_mode == "RAMP_WHIP":
        inst = 0.42 + 2.05 * (np.abs(2.0 * u - 1.0) ** 2.3)
    elif speed_mode == "RAMP_LIFT":
        # Energetic lift in (2.15x) -> Luscious slow-mo hold (0.45x) on steaming squid & noodles
        inst = 0.45 + 1.85 * (np.maximum(0.0, 1.0 - u / 0.38) ** 2.1)
    else:
        inst = np.ones_like(u)

    cum = np.cumsum(inst) - inst[0]
    norm = cum / max(1e-6, cum[-1])
    return start_idx + norm * avail

def render_shot_v2(args):
    rtag, W, H, idx, sid, scale_tag, f_in, f_out, speed_mode, src_mp4 = args
    n_out = f_out - f_in
    out_p = os.path.join(WORK_V2, f"shot_{rtag}_{idx:02d}_{sid}.mp4")
    is_ramped = speed_mode.startswith("RAMP_")

    # Only run 60fps optical-flow minterpolate on the 4 RAMPED shots (fast & silky slow-mo);
    # keep the 8 constant-speed shots crisp & natural without unnecessary interpolation!
    dec_fps = 60.0 if is_ramped else 30.0
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if is_ramped:
        vf += ",minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    else:
        vf += ",fps=30"
    vf += ",format=rgb24"

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src_mp4, "-vf", vf, "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fsz = W * H * 3
    n_src = max(1, len(raw) // fsz)
    frames = np.frombuffer(raw[:n_src * fsz], dtype=np.uint8).reshape((n_src, H, W, 3))
    f_positions = sample_curve(n_out, speed_mode, n_src, dec_fps)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "12", "-b:v", "0", "-pix_fmt", "yuv420p", out_p
    ], stdin=subprocess.PIPE)

    for k in range(n_out):
        fp = min(n_src - 1.001, max(0.0, float(f_positions[k])))
        ia = int(math.floor(fp))
        ib = min(n_src - 1, ia + 1)
        fr = fp - ia
        if fr < 0.05 or ia == ib:
            frm = frames[ia]
        else:
            frm = ((1.0 - fr) * frames[ia].astype(np.float32) + fr * frames[ib].astype(np.float32)).astype(np.uint8)
        frm = heal_corner(frm)
        enc.stdin.write(frm.tobytes())

    enc.stdin.close()
    enc.wait()
    return idx, out_p


# ==============================================================================
# 4. BEAT-LOCKED AUDIO MIX (-14.0 LUFS)
# ==============================================================================
def load_aud(fn: str, s0: float = 0.0, dur: float = None, af_extra: str = None) -> np.ndarray:
    p = os.path.join(AUD_STG, fn)
    cmd = ["ffmpeg", "-v", "error"]
    if s0 > 0: cmd += ["-ss", f"{s0:.3f}"]
    if dur is not None: cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-i", p]
    if af_extra: cmd += ["-af", af_extra]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()

def mix_into(bus: np.ndarray, clip: np.ndarray, ts: float, gain: float = 1.0, fi: float = 0.02, fo: float = 0.10):
    if len(clip) == 0: return
    c = (clip * gain).copy()
    nfi, nfo = min(len(c), int(round(fi * SR))), min(len(c), int(round(fo * SR)))
    if nfi > 1: c[:nfi] *= np.linspace(0, 1, nfi, dtype=np.float32)[:, None]
    if nfo > 1: c[-nfo:] *= np.linspace(1, 0, nfo, dtype=np.float32)[:, None]
    i0 = max(0, int(round(ts * SR)))
    if i0 >= len(bus): return
    i1 = min(len(bus), i0 + len(c))
    bus[i0:i1] += c[:i1 - i0]

def build_v2_beat_audio() -> str:
    n_s = int(round(TOTAL_DUR * SR))
    bgm_b  = np.zeros((n_s, 2), dtype=np.float32)
    asmr_b = np.zeros((n_s, 2), dtype=np.float32)
    sfx_b  = np.zeros((n_s, 2), dtype=np.float32)

    # Exact same start_s = 11.2s used in beat detection so every cut frame [46, 98, 164, 216, 282, 334, 400, 452, 518, 570, 636] is 0ms locked!
    bgm = load_aud("bgm_drake_hiphop.mp3", 11.2, TOTAL_DUR)
    mix_into(bgm_b, bgm, 0.0, gain=0.86, fi=0.12, fo=1.10)

    sizzle_wok   = load_aud("asmr_sizzle_boil.mp3", 1.2, 2.2)
    boil_pot     = load_aud("asmr_broth_sticky.mp3", 1.0, 2.0)
    boil_ramen   = load_aud("asmr_broth_sticky.mp3", 6.5, 1.8)
    splash_crown = load_aud("asmr_splash_plunge.mp3", 4.88, 2.3)
    pour_glaze   = load_aud("asmr_pour_liquid.mp3", 0.15, 1.8, "lowpass=f=3200")
    noodle_lift  = load_aud("asmr_broth_sticky.mp3", 11.5, 2.2)
    fast_w       = load_aud("sfx_fast_whoosh.mp3", 0.0, 1.0)
    deep_w       = load_aud("sfx_deep_woosh.mp3", 0.0, 1.2)
    low_hit      = load_aud("sfx_low_hit.mp3", 0.0, 2.2)

    # Tactile ASMR synced to exact cut frames
    mix_into(asmr_b, sizzle_wok[:int(1.4*SR)],  0.05, gain=0.32, fi=0.05, fo=0.25)  # 01 Wide dark flame
    mix_into(asmr_b, pour_glaze,              46/30,  gain=0.40, fi=0.04, fo=0.25)  # 02 ECU chili oil
    mix_into(asmr_b, boil_pot[:int(1.8*SR)],  98/30,  gain=0.38, fi=0.04, fo=0.30)  # 03 Zero-G squid glaze
    mix_into(asmr_b, pour_glaze[:int(1.5*SR)],164/30, gain=0.36, fi=0.05, fo=0.25)  # 04 ECU squid rings drip
    mix_into(asmr_b, sizzle_wok,             216/30,  gain=0.55, fi=0.04, fo=0.30)  # 05 Wide Wok Hei fire
    mix_into(asmr_b, boil_ramen,             282/30,  gain=0.44, fi=0.05, fo=0.25)  # 06 ECU boiling ramen
    mix_into(asmr_b, splash_crown[:int(1.6*SR)],400/30,gain=0.38,fi=0.04, fo=0.25)  # 08 CU crimson wave
    mix_into(asmr_b, splash_crown,           452/30,  gain=0.76, fi=0.02, fo=0.40)  # 09 WIDE CROWN SPLASH DROP!
    mix_into(asmr_b, boil_pot,               518/30,  gain=0.46, fi=0.05, fo=0.25)  # 10 ECU boiling tentacles
    mix_into(asmr_b, noodle_lift,            570/30,  gain=0.48, fi=0.06, fo=0.30)  # 11 Hero chopstick lift
    mix_into(asmr_b, boil_ramen[:int(2.0*SR)],636/30, gain=0.22, fi=0.15, fo=0.80)  # 12 Hero pot simmer

    # Speed-ramp air whooshes ONLY on the 4 Speed-Ramped climax cuts (#3, #5, #9, #11) -> clean, impactful, zero clutter!
    for f_cut, gw in [(98, 0.34), (216, 0.32), (452, 0.38), (570, 0.30)]:
        mix_into(sfx_b, fast_w, (f_cut - 3) / 30.0, gain=gw, fi=0.02, fo=0.20)
        mix_into(sfx_b, low_hit, f_cut / 30.0, gain=0.32, fi=0.01, fo=0.40)
    mix_into(sfx_b, deep_w, (636 - 3) / 30.0, gain=0.22, fi=0.03, fo=0.30)

    raw_w = os.path.join(WORK_V2, "v2_mix_raw.wav")
    mst_w = os.path.join(WORK_V2, "v2_master_14lufs.wav")
    pcm = (np.clip(bgm_b + asmr_b + sfx_b, -0.99, 0.99) * 32767.0).astype(np.int16)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", raw_w], stdin=subprocess.PIPE)
    p.stdin.write(pcm.tobytes()); p.stdin.close(); p.wait()

    p1 = subprocess.run(["ffmpeg", "-v", "info", "-i", raw_w, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    ln = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p1.stderr).group(0))
    af2 = f"loudnorm=I=-14.0:TP=-1.0:LRA=11.0:measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true,aresample={SR}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_w, "-af", af2, "-c:a", "pcm_s16le", mst_w], check=True)
    return mst_w


# ==============================================================================
# 5. MONOLITHIC COMPOSITOR WITH BEAT TRANSITIONS + CENTERED FLAT 1-COLOR TITLES
# ==============================================================================
def render_directors_cut_master(is_916: bool, mst_wav: str) -> str:
    rtag = "9x16" if is_916 else "16x9"
    W, H = (1080, 1920) if is_916 else (1920, 1080)

    # Audit Safe-Zone on 9:16 pure flat centered titles (zero violating pixels!)
    if is_916:
        for ts, lbl in [(0.75, "Opening Centered Title"), (22.60, "Closing Centered End-Card")]:
            ov, _ = render_pure_flat_centered_title_rgba(ts, W, H)
            ok_sz, inf = audit_rgba_overlay_safe_zone(ov)
            print(f"  [SafeZone 9:16 Audit] {lbl:26s} -> ok={ok_sz}, violating_px={inf['violating_pixels']}", flush=True)
            if not ok_sz:
                raise RuntimeError(f"Safe-Zone violation on {lbl}: {inf}")

    shot_tasks = []
    for idx, sid, scale_tag, f_in, f_out, speed_mode, bank, base_name in DIRECTORS_PLAN:
        src_p = resolve_clip_path(bank, base_name, is_916)
        shot_tasks.append((rtag, W, H, idx, sid, scale_tag, f_in, f_out, speed_mode, src_p))

    with ThreadPoolExecutor(max_workers=4) as pool:
        shot_files = sorted(list(pool.map(render_shot_v2, shot_tasks)), key=lambda x: x[0])

    # Load all 720 frames into continuous sequence to apply 2 subtle @sijonsonn Beat-Transitions on Drop #1 (f=98) & Drop #4 (f=452)
    fsz = W * H * 3
    chunks = []
    for _, sp in shot_files:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sp, "-vf", "format=rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
        nf = len(raw) // fsz
        chunks.append(np.frombuffer(raw[:nf * fsz], dtype=np.uint8).reshape((nf, H, W, 3)))
    all_frames = np.concatenate(chunks, axis=0).copy()

    # Beat-Transition 1 @ f=98 (3.267s 808 Drop #1): 5-frame Monochrome Contrast Snap -> pops back to rich red!
    for k, fi in enumerate(range(97, 102)):
        f_rgb = all_frames[fi].astype(np.float32)
        luma = (0.299 * f_rgb[:, :, 0] + 0.587 * f_rgb[:, :, 1] + 0.114 * f_rgb[:, :, 2])[:, :, None]
        bw = np.clip((luma - 128.0) * 1.22 + 128.0, 0, 255)
        mix = 1.0 if k < 3 else (1.0 - (k - 2) / 3.0)
        all_frames[fi] = np.clip(f_rgb * (1.0 - mix) + bw * mix, 0, 255).astype(np.uint8)

    # Beat-Transition 2 @ f=452 (15.067s 808 Drop #4 into Crown Splash): 7-frame 3-Column Vertical Shutter-Whip!
    snap_A, snap_B = all_frames[451].copy(), all_frames[452].copy()
    col_w = W // 3
    for idx_t, fi in enumerate(range(449, 456)):
        p = (idx_t + 1) / 8.0
        comp = np.zeros((H, W, 3), dtype=np.uint8)
        for col in range(3):
            x0, x1 = col * col_w, (W if col == 2 else (col + 1) * col_w)
            ec = ease_io(np.clip((p - col * 0.08) / 0.84, 0.0, 1.0))
            srcA, srcB = all_frames[min(451, fi)], all_frames[max(452, fi)]
            sy = int(round(ec * H))
            if col % 2 == 0:
                if sy > 0: comp[:sy, x0:x1] = srcB[H - sy:, x0:x1]
                if sy < H: comp[sy:, x0:x1] = srcA[:H - sy, x0:x1]
            else:
                if sy > 0: comp[H - sy:, x0:x1] = srcB[:sy, x0:x1]
                if sy < H: comp[:H - sy, x0:x1] = srcA[sy:, x0:x1]
        all_frames[fi] = comp

    out_mp4 = os.path.join(OUT_DIR, f"FEEL_CHICKEN_MI_CAY_MUC_V2_CINEMA_{rtag}.mp4")
    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", mst_wav,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "15", "-b:v", "0",
        "-bf", "2", "-g", "60", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart", out_mp4
    ], stdin=subprocess.PIPE)

    for fi in range(len(all_frames)):
        t_cur = fi / float(FPS)
        bg = all_frames[fi]
        ov, dim = render_pure_flat_centered_title_rgba(t_cur, W, H)
        if ov is not None:
            bg_f = bg.astype(np.float32) * (1.0 - dim)
            ov_np = np.array(ov, dtype=np.float32)
            a = ov_np[:, :, 3:4] / 255.0
            frm = np.clip(bg_f * (1.0 - a) + ov_np[:, :, :3] * a, 0, 255).astype(np.uint8)
        else:
            frm = bg
        enc.stdin.write(frm.tobytes())

    enc.stdin.close()
    enc.wait()
    print(f"  Encoded V2 Director's Cut {rtag} ({len(all_frames)}f = {len(all_frames)/FPS:.2f}s) -> {out_mp4}", flush=True)
    return out_mp4


# ==============================================================================
# 6. RAW EDITABLE CAPCUT PROJECT (SELECTIVE SPEED-RAMP + FLAT 1-COLOR CENTERED TEXT)
# ==============================================================================
def build_v2_capcut_project(mst_wav: str):
    DRAFT_V2 = "FEEL CHICKEN - Mì Cay Mực Siêu To AI"
    def uid(): return str(uuid.uuid4()).upper()
    def us_f(s): return int(round(int(round(float(s) * FPS)) * 1_000_000 / FPS))
    def nfwd(p): return os.path.normpath(p).replace("\\", "/")
    def write_unlink(path: str, data: bytes):
        if os.path.exists(path):
            try: os.unlink(path)
            except Exception: pass
        with open(path, "wb") as f:
            f.write(data)

    d_tpl = os.path.join(DRAFTS_DIR, "1117 F20")
    if not os.path.exists(os.path.join(d_tpl, "draft_content.json")):
        return
    dc_tpl = json.load(open(os.path.join(d_tpl, "draft_content.json"), encoding="utf-8"))
    dm_tpl = json.load(open(os.path.join(d_tpl, "draft_meta_info.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "video"))
    atrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "audio"))
    ttrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "text"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    tseg_tpl   = copy.deepcopy(ttrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(next(m for m in dc_tpl["materials"]["videos"] if m.get("type") == "video"))
    amat_tpl   = copy.deepcopy(dc_tpl["materials"]["audios"][0])
    tmat_tpl   = copy.deepcopy(dc_tpl["materials"]["texts"][0])
    afade_tpl  = copy.deepcopy(dc_tpl["materials"]["audio_fades"][0])
    tanim_tpl  = copy.deepcopy(dc_tpl["materials"]["material_animations"][0])
    dm_vid_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    dm_aud_tpl = copy.deepcopy(next((x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") in ("music", "audio", "sound")), dm_vid_tpl))

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}
    a_extra_keys = ("speeds", "placeholder_infos", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}

    tl_id, now_s, now_us = uid(), int(time.time()), int(time.time() * 1_000_000)
    D = copy.deepcopy(dc_tpl)
    D.update({
        "id": tl_id, "name": DRAFT_V2, "fps": 30.0, "duration": us_f(TOTAL_DUR),
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_tpl["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })
    dm_type0 = []

    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    for idx, sid, scale_tag, f_in, f_out, speed_mode, bank, base_name in DIRECTORS_PLAN:
        clean_p = resolve_clip_path(bank, base_name, True)
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", clean_p], capture_output=True, text=True, check=True).stdout)
        vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
        vw, vh = int(vs["width"]), int(vs["height"])
        vdur_us = int(round(float(pr["format"]["duration"]) * 1_000_000))

        mid = uid()
        vm = copy.deepcopy(vmat_tpl)
        vm.update({
            "id": mid, "type": "video", "path": nfwd(clean_p), "material_name": os.path.basename(clean_p),
            "width": vw, "height": vh, "duration": vdur_us, "has_audio": False,
            "crop": {"upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0, "lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0},
            "crop_ratio": "free", "crop_scale": 1.0,
        })
        D["materials"]["videos"].append(vm)
        dmi = copy.deepcopy(dm_vid_tpl)
        dmi.update({"id": uid(), "file_Path": nfwd(clean_p), "extra_info": os.path.basename(clean_p), "width": vw, "height": vh, "duration": vdur_us, "create_time": now_s, "import_time": now_s, "import_time_ms": now_s * 1000})
        dm_type0.append(dmi)

        tgt_du = int(round((f_out - f_in) * 1_000_000 / FPS))
        tgt_st = int(round(f_in * 1_000_000 / FPS))
        is_ramped = speed_mode.startswith("RAMP_")
        base_spd = 1.25 if is_ramped else float(speed_mode.split("_")[1])
        src_du = min(vdur_us - 100000, int(round(tgt_du * base_spd)))
        eff_spd = src_du / float(tgt_du)

        refs = []
        for k, te in v_extra_tpl.items():
            em = copy.deepcopy(te); em["id"] = uid()
            if k == "speeds":
                if is_ramped:
                    # ONLY attach Curve Speed ('Dựng phim') to the 4 Speed-Ramped climax clips!
                    em["mode"] = 1
                    em["speed"] = round(eff_spd, 5)
                    em["curve_speed"] = {
                        "id": "6768648600848175619", "source_platform": 1, "name": "Dựng phim",
                        "speed_points": [
                            {"x": 0.0, "y": round(eff_spd * 1.65, 3)},
                            {"x": 0.45, "y": round(max(0.38, eff_spd * 0.45), 3)},
                            {"x": 1.0, "y": round(eff_spd * 1.55, 3)},
                        ],
                    }
                else:
                    # Constant speed (mode=0) on the 8 steady/rhythm clips!
                    em["mode"] = 0
                    em["speed"] = round(eff_spd, 5)
                    em["curve_speed"] = None
            D["materials"][k].append(em); refs.append(em["id"])

        sg = copy.deepcopy(vseg_tpl)
        sg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": 50000, "duration": src_du},
            "target_timerange": {"start": tgt_st, "duration": tgt_du},
            "speed": eff_spd, "volume": 0.0, "extra_material_refs": refs,
            "common_keyframes": [], "keyframe_refs": [], "visible": True,
        })
        sg["clip"]["scale"] = {"x": 1.04, "y": 1.04}
        sg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        tr_v0["segments"].append(sg)
    D["tracks"].append(tr_v0)

    # Native CapCut Flat 1-Color Stroke-Free Centered Text Layers (x=0.0, y=0.0 dead center, check_flag=7, strokes=[])!
    F_OSW = ("7182504807289065985", nfwd(os.path.join(EFFECT_DIR, "7182504807289065985/0a5333de6f4d592cb2d2390d68b31efb/Oswald-Bold.ttf")))
    F_MON = ("7517455788122705168", nfwd(os.path.join(EFFECT_DIR, "7517455788122705168/91d28cfa5e7db054f4872f1ae2417ac2/Montserrat-Bold.otf")))
    ANIM_IN  = nfwd(os.path.join(EFFECT_DIR, "7648937403646004500/495e55b3bcd1f6420b6e4b1b44ed1fc8"))
    ANIM_OUT = nfwd(os.path.join(EFFECT_DIR, "6798320902548230669/c6f05ce62355b537be762550040bfc08"))

    def mk_flat_center_tseg(txt, st_s, du_s, fpair, sz, py):
        tid, aid = uid(), uid()
        anim = copy.deepcopy(tanim_tpl)
        anim.update({"id": aid, "type": "sticker_animation", "multi_language_current": "none", "animations": [
            {"anim_adjust_params": None, "category_id": "", "category_name": "Vào", "duration": 266666, "id": "7648937403646004500", "material_type": "sticker", "name": "Chữ mờ dần hiện vào", "panel": "", "path": ANIM_IN, "platform": "all", "request_id": "", "resource_id": "7648937403646004500", "start": 0, "type": "in"},
            {"anim_adjust_params": None, "category_id": "", "category_name": "Ra",  "duration": 266666, "id": "6798320902548230669", "material_type": "sticker", "name": "Mờ dần", "panel": "", "path": ANIM_OUT, "platform": "all", "request_id": "", "resource_id": "6798320902548230669", "start": max(0, us_f(du_s) - 266666), "type": "out"},
        ]})
        D["materials"]["material_animations"].append(anim)
        cobj = {"text": txt, "styles": [{"fill": {"content": {"render_type": "solid", "solid": {"color": [0.968, 0.960, 0.941]}}}, "font": {"path": fpair[1], "id": fpair[0]}, "strokes": [], "size": float(sz), "useLetterColor": True, "range": [0, len(txt)]}]}
        tm = copy.deepcopy(tmat_tpl)
        tm.update({"id": tid, "type": "text", "recognize_text": txt, "content": json.dumps(cobj, ensure_ascii=False), "check_flag": 7, "background_style": 0, "has_shadow": False, "font_id": fpair[0], "font_path": fpair[1], "font_size": float(sz), "text_color": "#F7F5F0", "strokes": [], "words": {"start_time": [], "end_time": [], "text": []}, "current_words": {"start_time": [], "end_time": [], "text": []}})
        D["materials"]["texts"].append(tm)
        sg = copy.deepcopy(tseg_tpl)
        sg.update({"id": uid(), "material_id": tid, "source_timerange": None, "target_timerange": {"start": us_f(st_s), "duration": us_f(du_s)}, "extra_material_refs": [aid], "render_index": 14010, "visible": True})
        sg["clip"]["transform"] = {"x": 0.0, "y": float(py)}
        sg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        return sg

    for tsegs in [
        [mk_flat_center_tseg("FEEL CHICKEN", 0.10, 1.38, F_MON, 5.5, 0.09), mk_flat_center_tseg("MÌ CAY MỰC KHỔNG LỒ • 250G–300G", 21.35, 2.57, F_MON, 5.2, 0.11)],
        [mk_flat_center_tseg("MÌ CAY MỰC",  0.10, 1.38, F_OSW, 18.0, 0.0), mk_flat_center_tseg("FEEL CHICKEN", 21.35, 2.57, F_OSW, 17.0, 0.02)],
        [mk_flat_center_tseg("KHỔNG LỒ • 250G – 300G", 0.10, 1.38, F_MON, 5.5, -0.09), mk_flat_center_tseg("GIÁ RA MẮT 99K • ĐỦ 7 CẤP ĐỘ CAY\n38 Nguyễn Đình Chiểu • 35 Trần Hữu Duyệt • 0796 601 106", 21.48, 2.44, F_MON, 5.0, -0.10)],
    ]:
        tt = copy.deepcopy(ttrack_tpl); tt["id"] = uid(); tt["flag"] = 0; tt["segments"] = tsegs
        D["tracks"].append(tt)

    # Master beat-synced audio track
    amid = uid()
    am = copy.deepcopy(amat_tpl)
    am.update({"id": amid, "type": "extract_music", "path": nfwd(mst_wav), "name": "V2_DirectorsCut_BeatAudio_14LUFS.wav", "duration": us_f(TOTAL_DUR)})
    D["materials"]["audios"].append(am)
    dmi_a = copy.deepcopy(dm_aud_tpl)
    dmi_a.update({"id": uid(), "file_Path": nfwd(mst_wav), "extra_info": os.path.basename(mst_wav), "duration": us_f(TOTAL_DUR)})
    dm_type0.append(dmi_a)
    arefs = []
    for k, te in a_extra_tpl.items():
        em = copy.deepcopy(te); em["id"] = uid(); D["materials"][k].append(em); arefs.append(em["id"])
    af = copy.deepcopy(afade_tpl); af.update({"id": uid(), "fade_in_duration": 66666, "fade_out_duration": 200000})
    D["materials"]["audio_fades"].append(af); arefs.append(af["id"])
    asg = copy.deepcopy(aseg_tpl)
    asg.update({"id": uid(), "material_id": amid, "source_timerange": {"start": 0, "duration": us_f(TOTAL_DUR)}, "target_timerange": {"start": 0, "duration": us_f(TOTAL_DUR)}, "speed": 1.0, "volume": 1.0, "extra_material_refs": arefs, "visible": True})
    tr_a = copy.deepcopy(atrack_tpl); tr_a["id"] = uid(); tr_a["segments"] = [asg]
    D["tracks"].append(tr_a)

    draft_dir = os.path.join(DRAFTS_DIR, DRAFT_V2)
    os.makedirs(draft_dir, exist_ok=True)
    dm_out = copy.deepcopy(dm_tpl)
    dm_out.update({"draft_id": uid(), "draft_name": DRAFT_V2, "draft_fold_path": nfwd(draft_dir), "draft_root_path": nfwd(DRAFTS_DIR), "tm_duration": us_f(TOTAL_DUR), "tm_draft_create": now_us, "tm_draft_modified": now_us})
    for g in dm_out["draft_materials"]:
        g["value"] = dm_type0 if g.get("type") == 0 else []

    dc_b = json.dumps(D, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    dm_b = json.dumps(dm_out, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    write_unlink(os.path.join(draft_dir, "draft_content.json"), dc_b)
    write_unlink(os.path.join(draft_dir, "template-2.tmp"), dc_b)
    write_unlink(os.path.join(draft_dir, "draft_meta_info.json"), dm_b)
    print(f"  Updated Raw Editable CapCut Project -> {draft_dir}", flush=True)


def build_12shot_qc_sheet(mp4_p: str, out_jpg: str, is_916: bool):
    cw, ch = (220, 391) if is_916 else (360, 202)
    cols, rows = 4, 3
    grid = Image.new("RGB", (cw * cols, ch * rows), (10, 10, 10))
    dr = ImageDraw.Draw(grid)
    fn_lbl = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 13)
    for i, (idx, sid, scale_tag, f_in, f_out, speed_mode, _, _) in enumerate(DIRECTORS_PLAN):
        ts = ((f_in + f_out) / 2.0) / 30.0
        if idx == 1: ts = 0.75
        if idx == 12: ts = 22.65
        jp = os.path.join(QC_DIR, f"_v2qc_{i}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mp4_p, "-frames:v", "1", "-vf", f"scale={cw}:{ch},format=yuvj420p", "-q:v", "2", jp], check=True)
        r, c = divmod(i, cols)
        grid.paste(Image.open(jp).convert("RGB"), (c * cw, r * ch))
        dr.rectangle([c * cw, r * ch, (c + 1) * cw, r * ch + 22], fill=(0, 0, 0))
        spd_lbl = "RAMP" if speed_mode.startswith("RAMP") else "STEADY"
        col_lbl = (255, 195, 75) if spd_lbl == "RAMP" else (140, 245, 170)
        dr.text((c * cw + 5, r * ch + 4), f"{idx:02d} [{scale_tag}] {spd_lbl} @{ts:.1f}s", fill=col_lbl, font=fn_lbl)
        os.remove(jp)
    grid.save(out_jpg, quality=93)


def main():
    print("[1/5] Building Beat-Locked Audio Mix (-14.0 LUFS)...", flush=True)
    mst_wav = build_v2_beat_audio()

    print("[2/5] Rendering 9:16 Director's Cut (Cận-Toàn Alternating + Selective Speed-Ramp + Flat 1-Color Centered Text)...", flush=True)
    mp4_916 = render_directors_cut_master(True, mst_wav)

    print("[3/5] Rendering 16:9 Director's Cut...", flush=True)
    mp4_169 = render_directors_cut_master(False, mst_wav)

    print("[4/5] Syncing Final MP4s & Updating Raw Editable CapCut Project...", flush=True)
    fname = "261126 Feel Chicken Mì cay mực khổng lồ final.mp4"
    for src, dsts in [
        (mp4_916, [
            os.path.join(r"D:\XUẤT CAPCUT", fname),
            os.path.join(r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN", fname),
            os.path.join(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final", fname),
        ]),
        (mp4_169, [
            os.path.join(r"D:\XUẤT CAPCUT\Ngang", fname),
            os.path.join(r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\Ngang", fname),
            os.path.join(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\Ngang", fname),
        ]),
    ]:
        for d in dsts:
            if d.startswith("Z:") and not os.path.exists("Z:\\"):
                continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(src, d)
            print(f"  Delivered ({os.path.getsize(d)/1e6:.2f} MB) -> {d}", flush=True)

    build_v2_capcut_project(mst_wav)

    print("[5/5] Generating 12-Shot Cận-Toàn Visual QC Contact Sheets...", flush=True)
    qc_916 = os.path.join(QC_DIR, "QC_V2_DIRECTORS_CUT_9x16.jpg")
    qc_169 = os.path.join(QC_DIR, "QC_V2_DIRECTORS_CUT_16x9.jpg")
    build_12shot_qc_sheet(mp4_916, qc_916, True)
    build_12shot_qc_sheet(mp4_169, qc_169, False)
    shutil.copyfile(qc_916, os.path.join(ART_DIR, "fc_squid_v2_directors_cut_9x16_qc.jpg"))
    shutil.copyfile(qc_169, os.path.join(ART_DIR, "fc_squid_v2_directors_cut_16x9_qc.jpg"))
    if os.path.exists("Z:\\"):
        os.makedirs(CLOUD_PRJ, exist_ok=True)
        for fp in (qc_916, qc_169, __file__):
            shutil.copyfile(fp, os.path.join(CLOUD_PRJ, os.path.basename(fp)))
    print("V2 DIRECTOR'S CUT ALL DONE!", flush=True)

if __name__ == "__main__":
    main()
