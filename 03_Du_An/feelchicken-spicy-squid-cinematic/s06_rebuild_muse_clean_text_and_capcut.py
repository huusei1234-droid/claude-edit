import copy, json, math, os, shutil, subprocess, sys, time, uuid
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from safe_zone_9x16 import audit_rgba_overlay_safe_zone, clamp_box_to_safe_zone_9x16

OUT_DIR   = r"d:\AI\full studio\output\feelchicken-spicy-squid-cinematic"
MUSE_916  = os.path.join(OUT_DIR, "muse_clips_9x16")
AUD_STG   = os.path.join(OUT_DIR, "audio_stage")
WORK_DIR  = os.path.join(OUT_DIR, "work_render")
QC_DIR    = os.path.join(OUT_DIR, "qc_sheets")
RAW_MUSE  = os.path.join(OUT_DIR, "RAW_MUSE_CAPCUT_1080x1920")
CLOUD_RAW = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC\261126_Mi_Cay_Muc_MUSE_Source_Goc"
FONT_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
ART_DIR   = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-spicy-squid-cinematic"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
EFFECT_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Cache\effect")

os.makedirs(RAW_MUSE, exist_ok=True)
if os.path.exists("Z:\\"):
    os.makedirs(CLOUD_RAW, exist_ok=True)

FPS = 30
W, H = 1080, 1920
TOTAL_DUR = 24.60

# EXACT 8-SCENE MUSE TIMELINE FROM s05_gen_muse_edition_all.py (UNCHANGED CUTS, CLIPS, RAMPS & AUDIO!)
TIMELINE_PLAN = [
    (1, "s01_chili_wave",            0.00,  2.80, "ramp_out",     "01_Muse_Song_Sup_Ot.mp4"),
    (2, "s02_zero_g_squid_whip",     2.80,  5.80, "u_valley",     "02_Muse_Muc_Bay_ZeroG.mp4"),
    (3, "s03_wok_fire_toss",         5.80,  8.60, "u_valley",     "03_Muse_Chao_Lua_WokHei.mp4"),
    (4, "s04_exploded_levitation",   8.60, 12.20, "slow_breathe", "04_Muse_Thap_Nguyen_Lieu.mp4"),
    (5, "s05_broth_crown_splash",   12.20, 15.20, "ramp_in_deep", "05_Muse_Bung_Vuong_Mien.mp4"),
    (6, "s06_macro_boiling_glaze",  15.20, 18.20, "u_valley",     "06_Muse_Sup_Soi_7_Cap_Do.mp4"),
    (7, "s07_chopstick_tower_lift", 18.20, 21.20, "u_valley",     "07_Muse_Dua_Gap_Mi_Muc.mp4"),
    (8, "s08_hero_stone_pot",       21.20, 24.60, "ramp_in_hold", "08_Muse_Tho_Mi_Hoan_Chinh.mp4"),
]

# Pure 1-color flat warm cinema ivory white (#F7F5F0) — ZERO stroke, ZERO gradient, ZERO box!
CINEMA_WHITE = (247, 245, 240)

def ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_in_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    p = os.path.join(FONT_DIR, name)
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", size)

def draw_tracked_line(draw: ImageDraw.ImageDraw, cx: int, cy: int, text: str, font: ImageFont.FreeTypeFont, tracking: float, alpha: int):
    advs = [font.getlength(ch) for ch in text]
    tot_w = sum(advs) + tracking * max(0, len(text) - 1)
    x = cx - tot_w / 2.0
    bb = font.getbbox("ÁẤẦẨẪẬĐMÌỰỔỒ09")
    y = cy - (bb[1] + bb[3]) / 2.0
    col = (*CINEMA_WHITE, max(0, min(255, int(round(alpha)))))
    for ch, adv in zip(text, advs):
        draw.text((x, y), ch, font=font, fill=col)  # 0 stroke, 0 shadow, 0 border!
        x += adv + tracking

def apply_optical_blur_focus(layer: Image.Image, p_in: float, p_out: float) -> Image.Image:
    a_m = 1.0
    b_r = 0.0
    sc  = 1.0
    if p_in < 1.0:
        ei = ease_out_cubic(p_in)
        a_m *= ei
        b_r = max(b_r, (1.0 - ei) * 14.0)
        sc  = 0.95 + 0.05 * ei
    if p_out < 1.0:
        eo = ease_in_out(p_out)
        a_m *= eo
        b_r = max(b_r, (1.0 - eo) * 11.0)
    im = layer
    if abs(sc - 1.0) > 0.002:
        nw, nh = max(4, int(round(im.width * sc))), max(4, int(round(im.height * sc)))
        rs = im.resize((nw, nh), Image.Resampling.BILINEAR)
        canvas = Image.new("RGBA", (im.width, im.height), (0, 0, 0, 0))
        canvas.alpha_composite(rs, ((im.width - nw) // 2, (im.height - nh) // 2))
        im = canvas
    if b_r > 0.35:
        im = im.filter(ImageFilter.GaussianBlur(radius=b_r))
    if a_m < 0.999:
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 3] *= max(0.0, min(1.0, a_m))
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    return im

def render_clean_muse_text_overlay(t: float) -> tuple[Image.Image, float]:
    """
    ONLY replaces the text on the original Muse 9:16 timeline:
    - [0.14 .. 2.70s]: Pure 1-color #F7F5F0 flat stroke-free DEAD-CENTER (540, 960) Opening Title
    - [8.65 .. 12.15s]: Clean 1-color #F7F5F0 borderless minimalist ingredient callouts (updated 'MỰC KHỔNG LỒ 250G–300G')
    - [21.28 .. 24.52s]: Pure 1-color #F7F5F0 flat stroke-free DEAD-CENTER (540, 960) Closing Brand Title ('GIÁ RA MẮT 99K/TÔ')
    Returns (rgba_overlay, center_exposure_dim_strength).
    """
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # A. OPENING TITLE — DEAD-CENTER (540, 960), 1-COLOR FLAT WHITE, ZERO STROKE, ZERO BOX
    if 0.14 <= t <= 2.70:
        lt, dur = t - 0.14, 2.56
        p_in  = min(1.0, lt / 0.28)
        p_out = min(1.0, (dur - lt) / 0.24)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        f_top  = fnt("BeVietnamPro-Medium.ttf", 21)
        f_main = fnt("BarlowCondensed-Bold.ttf", 80)
        f_sub  = fnt("BeVietnamPro-Medium.ttf", 21)

        draw_tracked_line(d, 540, 880, "FEEL CHICKEN", f_top, tracking=7.0, alpha=220)
        draw_tracked_line(d, 540, 958, "MÌ CAY MỰC KHỔNG LỒ", f_main, tracking=2.2, alpha=255)
        draw_tracked_line(d, 540, 1036, "SIZE MỰC 250G – 300G  •  7 CẤP ĐỘ CAY", f_sub, tracking=2.0, alpha=228)

        ov = apply_optical_blur_focus(lay, p_in, p_out)
        dim = 0.30 * min(p_in, p_out)
        return ov, dim

    # B. SCENE 04 EXPLODED INGREDIENT CALLOUTS — PURE 1-COLOR FLAT WHITE (ZERO BOXES, ZERO STROKES!)
    if 8.65 <= t <= 12.15:
        lt, dur = t - 8.65, 3.50
        p_out_all = min(1.0, (dur - lt) / 0.22)
        d = ImageDraw.Draw(ov)
        f_h = fnt("BeVietnamPro-SemiBold.ttf", 21)
        f_s = fnt("BeVietnamPro-Medium.ttf", 16)

        callouts = [
            (0.05, (515,  320), (630,  320), "R", "ỚT CAY 7 CẤP ĐỘ",        "Cay nồng chuẩn Hàn"),
            (0.23, (505,  465), (345,  465), "L", "BẮP CẢI TÍM & CẢI THÌA", "Tươi giòn thanh ngọt"),
            (0.41, (545,  725), (620,  725), "R", "CÁ VIÊN & XÚC XÍCH",     "Đầy ắp nhân ngon"),
            (0.59, (520,  965), (365,  965), "L", "MỰC KHỔNG LỒ 250G–300G", "Nguyên con giòn sần sật"),
            (0.77, (535, 1220), (595, 1220), "R", "MÌ SỢI HÀN QUỐC",        "Sợi xoăn dai thấm vị"),
        ]
        for stg, (ax, ay), (ex, ey), side, t_lbl, s_lbl in callouts:
            ct = lt - stg
            if ct <= 0.0:
                continue
            p_l = ease_out_cubic(min(1.0, ct / 0.24))
            p_c = ease_out_cubic(min(1.0, max(0.0, (ct - 0.08) / 0.24)))
            al_line = int(round(210 * min(1.0, ct / 0.14) * p_out_all))
            al_txt  = int(round(248 * p_c * p_out_all))
            al_sub  = int(round(195 * p_c * p_out_all))
            col_l = (*CINEMA_WHITE, al_line)

            d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=col_l)
            shelf = 38
            hx = ex - shelf if side == "L" else ex + shelf
            cx_l = int(round(ax + (hx - ax) * p_l))
            d.line([(ax, ay), (cx_l, ey)], fill=col_l, width=2)

            if p_c > 0.02:
                w1 = f_h.getlength(t_lbl)
                w2 = f_s.getlength(s_lbl)
                bw = max(w1, w2)
                tx0 = (hx - 10 - bw) if side == "L" else (hx + 10)
                tx0 = max(60.0, min(878.0 - bw, tx0))
                d.text((tx0, ey - 24), t_lbl, font=f_h, fill=(*CINEMA_WHITE, al_txt))
                d.text((tx0, ey + 3),  s_lbl, font=f_s, fill=(*CINEMA_WHITE, al_sub))
        return ov, 0.0

    # C. CLOSING BRAND END-CARD — DEAD-CENTER (540, 960), 1-COLOR FLAT WHITE, ZERO BOX, ZERO STROKE!
    if 21.28 <= t <= 24.52:
        lt, dur = t - 21.28, 3.24
        p_in  = min(1.0, lt / 0.30)
        p_out = min(1.0, (dur - lt) / 0.26)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)

        f_top  = fnt("BeVietnamPro-Medium.ttf", 21)
        f_main = fnt("BarlowCondensed-Bold.ttf", 104)
        f_prc  = fnt("BeVietnamPro-SemiBold.ttf", 25)
        f_adr  = fnt("BeVietnamPro-Medium.ttf", 19)

        draw_tracked_line(d, 540, 852, "MÌ CAY MỰC KHỔNG LỒ  •  250G – 300G", f_top, tracking=3.8, alpha=222)
        draw_tracked_line(d, 540, 938, "FEEL CHICKEN", f_main, tracking=5.5, alpha=255)
        draw_tracked_line(d, 540, 1024, "GIÁ RA MẮT 99K/TÔ  •  ĐỦ 7 CẤP ĐỘ CAY", f_prc, tracking=2.2, alpha=245)
        draw_tracked_line(d, 540, 1076, "38 NGUYỄN ĐÌNH CHIỂU  •  35 TRẦN HỮU DUYỆT", f_adr, tracking=1.5, alpha=212)
        draw_tracked_line(d, 540, 1108, "10:00 – 22:00   •   0796 601 106", f_adr, tracking=2.2, alpha=205)

        ov = apply_optical_blur_focus(lay, p_in, p_out)
        dim = 0.44 * min(p_in, p_out)
        return ov, dim

    return ov, 0.0


# ==============================================================================
# 1. RE-RENDER THE EXACT MUSE 9:16 FINAL MP4 (ONLY TEXT CHANGED!)
# ==============================================================================
print("[1/4] Rendering Updated MUSE 9:16 Final MP4 (100% Original Muse Video/Speed/Audio, ONLY Text Changed to Clean 1-Color Center Cinema)...", flush=True)

for test_t, lbl in [(1.25, "Opening Title"), (10.25, "HUD Callouts"), (22.75, "Closing Title")]:
    ov_t, _ = render_clean_muse_text_overlay(test_t)
    ok_sz, info_sz = audit_rgba_overlay_safe_zone(ov_t)
    print(f"  [SafeZone 9:16 Audit] {lbl:16s} @ {test_t:.2f}s -> ok={ok_sz}, violating_px={info_sz['violating_pixels']}", flush=True)
    if not ok_sz:
        raise RuntimeError(f"Safe-Zone violation on {lbl}: {info_sz}")

yy = (np.linspace(-1.0, 1.0, H, dtype=np.float32)[:, None]) / 0.42
xx = (np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]) / 0.85
center_feather = np.exp(-0.5 * (xx * xx + yy * yy))[:, :, None]

mst_wav = os.path.join(WORK_DIR, "master_14lufs.wav")
out_muse_mp4 = os.path.join(OUT_DIR, "FEEL_CHICKEN_MI_CAY_MUC_9x16_MUSE_CLEAN_TEXT_MASTER.mp4")

enc = subprocess.Popen([
    "ffmpeg", "-y", "-v", "error",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", mst_wav,
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "15", "-b:v", "0",
    "-bf", "2", "-g", "60", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
    "-shortest", "-movflags", "+faststart",
    out_muse_mp4
], stdin=subprocess.PIPE)

fsz = W * H * 3
global_f = 0
for idx, sid, t0, t1, style, _ in TIMELINE_PLAN:
    rmp_p = os.path.join(WORK_DIR, f"ramped_9x16_muse_{idx:02d}_{sid}.mp4")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", rmp_p, "-vf", "format=rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    nf = len(raw) // fsz
    frames_arr = np.frombuffer(raw[:nf * fsz], dtype=np.uint8).reshape((nf, H, W, 3))
    for k in range(nf):
        t_cur = global_f / float(FPS)
        bg = frames_arr[k]
        if (0.14 <= t_cur <= 2.70) or (8.65 <= t_cur <= 12.15) or (21.28 <= t_cur <= 24.52):
            ov_im, dim_str = render_clean_muse_text_overlay(t_cur)
            bg_f = bg.astype(np.float32)
            if dim_str > 0.001:
                bg_f = bg_f * (1.0 - dim_str * center_feather)
            ov_np = np.array(ov_im, dtype=np.float32)
            a = ov_np[:, :, 3:4] / 255.0
            frm = np.clip(bg_f * (1.0 - a) + ov_np[:, :, :3] * a, 0, 255).astype(np.uint8)
        else:
            frm = bg
        enc.stdin.write(frm.tobytes())
        global_f += 1

enc.stdin.close()
enc.wait()
print(f"  Encoded Updated Muse 9:16 Final ({global_f} frames = {global_f/FPS:.2f}s) -> {out_muse_mp4}", flush=True)

fname_muse = "261126 Feel Chicken Mì cay mực siêu to Muse final.mp4"
for dst in [
    os.path.join(r"D:\XUẤT CAPCUT", fname_muse),
    os.path.join(r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN", fname_muse),
    os.path.join(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final", fname_muse),
]:
    if dst.startswith("Z:") and not os.path.exists("Z:\\"):
        continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(out_muse_mp4, dst)
    print(f"  Delivered -> {dst}", flush=True)


# ==============================================================================
# 2. NORMALIZE ALL 8 FULL-LENGTH UNTRIMMED MUSE CLIPS TO TRUE 1080x1920 @ 30FPS
#    SO CAPCUT HAS 0% BLACK BARS & MATCHES MUSE FINAL MP4 1:1!
# ==============================================================================
print("[2/4] Staging all 8 full-length raw Muse clips (5s-10s untrimmed) at clean 1080x1920 @ 30fps...", flush=True)

def stage_muse_1080p_raw(src_mp4: str, dst_name: str) -> tuple[str, float]:
    dst_p = os.path.join(RAW_MUSE, dst_name)
    if not (os.path.exists(dst_p) and os.path.getsize(dst_p) > 200_000):
        raw = subprocess.run([
            "ffmpeg", "-v", "error", "-i", src_mp4,
            "-vf", "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=rgb24",
            "-f", "rawvideo", "-"
        ], capture_output=True, check=True).stdout
        nf = len(raw) // fsz
        frames = np.frombuffer(raw[:nf * fsz], dtype=np.uint8).reshape((nf, H, W, 3)).copy()
        y1, y2 = int(H * 0.905), int(H * 0.988)
        x1, x2 = int(W * 0.825), int(W * 0.982)
        wy = np.linspace(0.0, 1.0, y2 - y1)[:, None, None]
        wx = np.linspace(0.0, 1.0, x2 - x1)[None, :, None]
        for i in range(nf):
            out = frames[i]
            top = out[y1-2:y1, x1:x2].mean(axis=0, keepdims=True).astype(np.float32)
            bot = out[y2:min(H, y2+2), x1:x2].mean(axis=0, keepdims=True).astype(np.float32)
            lft = out[y1:y2, x1-2:x1].mean(axis=1, keepdims=True).astype(np.float32)
            rgt = out[y1:y2, x2:min(W, x2+2)].mean(axis=1, keepdims=True).astype(np.float32)
            out[y1:y2, x1:x2] = np.clip(((1.0 - wy) * top + wy * bot) * 0.55 + ((1.0 - wx) * lft + wx * rgt) * 0.45, 0, 255).astype(np.uint8)
        enc_r = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "14", "-b:v", "0", "-pix_fmt", "yuv420p", dst_p
        ], stdin=subprocess.PIPE)
        for frm in frames:
            enc_r.stdin.write(frm.tobytes())
        enc_r.stdin.close()
        enc_r.wait()
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_format", "-of", "json", dst_p], capture_output=True, text=True, check=True).stdout)
    dur_s = float(pr["format"]["duration"])
    if os.path.exists("Z:\\"):
        shutil.copyfile(dst_p, os.path.join(CLOUD_RAW, dst_name))
    return dst_p, dur_s

staged_muse = []
for idx, sid, t0, t1, style, dname in TIMELINE_PLAN:
    sp = os.path.join(MUSE_916, f"{sid}_9x16_muse.mp4")
    cp, dur_s = stage_muse_1080p_raw(sp, dname)
    staged_muse.append((idx, sid, t0, t1, style, cp, dur_s))


# ==============================================================================
# 3. BUILD 1:1 MATCHED EDITABLE MUSE CAPCUT PROJECT (EXACT 8 MUSE SHOTS + CURVE SPEED + EDITABLE 1-COLOR TEXT + RAW AUDIO)
# ==============================================================================
print("[3/4] Building 1:1 Matched Editable MUSE CapCut Desktop Project...", flush=True)

def uid(): return str(uuid.uuid4()).upper()
def us_f(s): return int(round(int(round(float(s) * FPS)) * 1_000_000 / FPS))
def nfwd(p): return os.path.normpath(p).replace("\\", "/")
def write_unlink(path: str, data: bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        try: os.unlink(path)
        except Exception: pass
    with open(path, "wb") as f:
        f.write(data)

def find_cached_font(fid: str):
    fdir = os.path.join(EFFECT_DIR, fid)
    for root, _, files in os.walk(fdir):
        for f in files:
            if f.lower().endswith((".ttf", ".otf")):
                return fid, nfwd(os.path.join(root, f))
    raise FileNotFoundError(fid)

FID_OSWALD, FP_OSWALD = find_cached_font("7182504807289065985")
FID_WORK,   FP_WORK   = find_cached_font("7200959526265164290")
FID_MONT,   FP_MONT   = find_cached_font("7517455788122705168")
ANIM_IN  = nfwd(os.path.join(EFFECT_DIR, "7648937403646004500/495e55b3bcd1f6420b6e4b1b44ed1fc8"))
ANIM_OUT = nfwd(os.path.join(EFFECT_DIR, "6798320902548230669/c6f05ce62355b537be762550040bfc08"))

def calc_muse_harmonic_curve(src_dur_s: float, tgt_dur_s: float, style: str):
    """Exact CapCut harmonic integral Curve Speed matching build_ramp_curve(style) in s03!"""
    if style == "u_valley":
        base = [(0.0, 2.35), (0.25, 1.35), (0.50, 0.46), (0.75, 1.35), (1.0, 2.35)]
    elif style == "ramp_in_deep":
        base = [(0.0, 2.35), (0.25, 1.15), (0.50, 0.48), (1.0, 0.48)]
    elif style == "ramp_in_hold":
        base = [(0.0, 2.05), (0.28, 0.95), (0.55, 0.54), (1.0, 0.54)]
    elif style == "ramp_out":
        base = [(0.0, 0.54), (0.52, 0.56), (0.78, 1.30), (1.0, 2.35)]
    else:  # slow_breathe
        base = [(0.0, 0.95), (0.50, 0.62), (1.0, 0.95)]

    inv_int = 0.0
    for (x0, y0), (x1, y1) in zip(base[:-1], base[1:]):
        dx = x1 - x0
        inv_int += (dx / y0) if abs(y1 - y0) < 1e-5 else (dx * math.log(y1 / y0) / (y1 - y0))
    k = inv_int * (src_dur_s / max(0.05, tgt_dur_s))
    pts = [{"x": round(x, 4), "y": round(max(0.25, min(8.0, y * k)), 4)} for x, y in base]
    return pts, round(src_dur_s / max(0.05, tgt_dur_s), 5)

v7_dir = os.path.join(DRAFTS_DIR, "FEEL CHICKEN - Food Cinematic V7")
dc_tpl = json.load(open(os.path.join(v7_dir, "draft_content.json"), encoding="utf-8"))
dm_tpl = json.load(open(os.path.join(v7_dir, "draft_meta_info.json"), encoding="utf-8"))

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
bright_eff_tpl = next((copy.deepcopy(e) for e in dc_tpl["materials"].get("effects", []) if e.get("type") == "brightness"), None)

dm_vid_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
dm_aud_tpl = copy.deepcopy(next((x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") in ("music", "audio", "sound")), dm_vid_tpl))

v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}
a_extra_keys = ("speeds", "placeholder_infos", "sound_channel_mappings", "vocal_separations")
a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}

DRAFT_MUSE_NEW = "261126 FEEL CHICKEN - Mì Cay Mực MUSE (Bản Gốc)"
DRAFT_MUSE_ID  = "A18E5C32-9F44-4B71-8D23-774519028364"
now_s, now_us  = int(time.time()), int(time.time() * 1_000_000)

D = copy.deepcopy(dc_tpl)
D.update({
    "id": uid(), "name": DRAFT_MUSE_NEW, "fps": 30.0, "duration": us_f(TOTAL_DUR),
    "version": 360000, "new_version": "193.0.0",
    "create_time": now_s, "update_time": now_s,
    "render_index_track_mode_on": True, "free_render_index_mode_on": False,
    "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
    "tracks": [], "materials": {k: [] for k in dc_tpl["materials"]},
    "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
})

mat_cache = {}
dm_type0 = []
total_bytes = 0

def reg_vid(p: str, dur_s: float):
    global total_bytes
    pn = nfwd(p)
    if pn in mat_cache: return mat_cache[pn]
    dur_us = int(round(dur_s * 1_000_000))
    mid = uid()
    vm = copy.deepcopy(vmat_tpl)
    vm.update({
        "id": mid, "type": "video", "path": pn, "material_name": os.path.basename(p),
        "width": 1080, "height": 1920, "duration": dur_us, "has_audio": False,
        "crop": {"upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0, "lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0},
        "crop_ratio": "free", "crop_scale": 1.0,
    })
    D["materials"]["videos"].append(vm)
    dmi = copy.deepcopy(dm_vid_tpl)
    dmi.update({"id": uid(), "file_Path": pn, "extra_info": os.path.basename(p), "width": 1080, "height": 1920, "duration": dur_us, "create_time": now_s, "import_time": now_s, "import_time_ms": now_s * 1000})
    dm_type0.append(dmi)
    total_bytes += os.path.getsize(p)
    mat_cache[pn] = (mid, dur_us)
    return mat_cache[pn]

def reg_aud(p: str):
    global total_bytes
    pn = nfwd(p)
    if pn in mat_cache: return mat_cache[pn]
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_format", "-of", "json", p], capture_output=True, text=True, check=True).stdout)
    dur_us = int(round(float(pr["format"]["duration"]) * 1_000_000))
    mid = uid()
    am = copy.deepcopy(amat_tpl)
    am.update({"id": mid, "type": "extract_music", "path": pn, "name": os.path.basename(p), "duration": dur_us})
    D["materials"]["audios"].append(am)
    dmi = copy.deepcopy(dm_aud_tpl)
    dmi.update({"id": uid(), "file_Path": pn, "extra_info": os.path.basename(p), "duration": dur_us, "create_time": now_s, "import_time": now_s, "import_time_ms": now_s * 1000})
    dm_type0.append(dmi)
    total_bytes += os.path.getsize(p)
    mat_cache[pn] = (mid, dur_us)
    return mat_cache[pn]

# TRACK 0: EXACT 8 MUSE RAW CLIPS (FULL 5s-10s SOURCE RANGE -> EXACT MUSE TIMELINE CUTS + CURVE SPEED!)
tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
for idx, sid, t0, t1, style, cp, dur_s in staged_muse:
    mid, vdur_us = reg_vid(cp, dur_s)
    tgt_du_s = t1 - t0
    span_s = max(0.5, dur_s - 0.10)  # Uses full 5s/10s clip [0.03s .. dur-0.07s] exactly like Muse Final MP4!
    pts, eff_spd = calc_muse_harmonic_curve(span_s, tgt_du_s, style)

    refs = []
    for k, te in v_extra_tpl.items():
        em = copy.deepcopy(te); em["id"] = uid()
        if k == "speeds":
            em["mode"] = 1
            em["speed"] = eff_spd
            em["curve_speed"] = {"id": "6768648600848175619", "source_platform": 1, "name": "Dựng phim", "speed_points": pts}
        D["materials"][k].append(em); refs.append(em["id"])

    enable_adj = False
    if bright_eff_tpl and idx in (1, 8):
        be = copy.deepcopy(bright_eff_tpl); be["id"] = uid()
        be["value"] = -0.14 if idx == 1 else -0.26
        D["materials"]["effects"].append(be); refs.append(be["id"])
        enable_adj = True

    sg = copy.deepcopy(vseg_tpl)
    sg.update({
        "id": uid(), "material_id": mid,
        "source_timerange": {"start": us_f(0.033), "duration": min(vdur_us - us_f(0.033), us_f(span_s))},
        "target_timerange": {"start": us_f(t0), "duration": us_f(tgt_du_s)},
        "speed": eff_spd, "volume": 0.0, "last_nonzero_volume": 1.0,
        "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        "enable_adjust": enable_adj, "enable_lut": False, "enable_color_curves": False, "enable_hsl": False,
        "render_index": 0, "track_render_index": 0, "visible": True,
    })
    sg["clip"] = {"alpha": 1.0, "flip": {"horizontal": False, "vertical": False}, "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0}, "transform": {"x": 0.0, "y": 0.0}}
    sg["uniform_scale"] = {"on": True, "value": 1.0}
    tr_v0["segments"].append(sg)
D["tracks"].append(tr_v0)

# TRACKS 1..5: NATIVE EDITABLE 1-COLOR FLAT CENTERED TEXT (OPENING + SCENE 04 CALLOUTS + CLOSING)
def mk_tseg(txt: str, st_s: float, du_s: float, fid: str, fp: str, ftitle: str, sz: float, px: float, py: float, let_sp: float = 0.05, align: int = 1, alpha_v: float = 1.0, ridx: int = 14010):
    tid, aid = uid(), uid()
    anim = copy.deepcopy(tanim_tpl)
    anim.update({"id": aid, "type": "sticker_animation", "multi_language_current": "none", "animations": [
        {"anim_adjust_params": None, "category_id": "", "category_name": "Vào", "duration": 266666, "id": "7648937403646004500", "material_type": "sticker", "name": "Chữ mờ dần hiện vào", "panel": "", "path": ANIM_IN, "platform": "all", "request_id": "", "resource_id": "7648937403646004500", "start": 0, "type": "in"},
        {"anim_adjust_params": None, "category_id": "", "category_name": "Ra",  "duration": 233333, "id": "6798320902548230669", "material_type": "sticker", "name": "Mờ dần", "panel": "", "path": ANIM_OUT, "platform": "all", "request_id": "", "resource_id": "6798320902548230669", "start": max(0, us_f(du_s) - 233333), "type": "out"},
    ]})
    D["materials"]["material_animations"].append(anim)
    cobj = {
        "text": txt,
        "styles": [{
            "fill": {"alpha": alpha_v, "content": {"render_type": "solid", "solid": {"alpha": alpha_v, "color": [0.968, 0.960, 0.941]}}},
            "font": {"id": fid, "path": fp},
            "strokes": [], "size": float(sz), "letterSpacing": float(let_sp), "useLetterColor": True, "range": [0, len(txt)],
        }]
    }
    tm = copy.deepcopy(tmat_tpl)
    tm.update({
        "id": tid, "type": "text", "recognize_text": txt, "content": json.dumps(cobj, ensure_ascii=False),
        "alignment": align, "check_flag": 7, "background_style": 0, "has_shadow": False,
        "font_id": fid, "font_path": fp, "font_title": ftitle, "font_size": float(sz),
        "letter_spacing": float(let_sp), "line_spacing": 0.06, "bold_width": 0.0,
        "preset_id": "", "preset_name": "", "style_name": "",
        "text_alpha": alpha_v, "text_color": "#F7F5F0", "strokes": [],
        "words": {"start_time": [], "end_time": [], "text": []}, "current_words": {"start_time": [], "end_time": [], "text": []},
    })
    D["materials"]["texts"].append(tm)
    sg = copy.deepcopy(tseg_tpl)
    sg.update({"id": uid(), "material_id": tid, "source_timerange": None, "target_timerange": {"start": us_f(st_s), "duration": us_f(du_s)}, "extra_material_refs": [aid], "render_index": ridx, "visible": True})
    sg["clip"] = {"alpha": alpha_v, "flip": {"horizontal": False, "vertical": False}, "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0}, "transform": {"x": float(px), "y": float(py)}}
    return sg

for tsegs in [
    [
        mk_tseg("FEEL CHICKEN",                        0.14, 2.56, FID_WORK,   FP_WORK,   "WorkSans-Medium", 4.6,  0.0,  0.105, let_sp=0.25, alpha_v=0.88, ridx=14010),
        mk_tseg("ỚT CAY 7 CẤP ĐỘ\nCay nồng chuẩn Hàn",  8.70, 3.45, FID_WORK,   FP_WORK,   "WorkSans-Medium", 4.2,  0.42, 0.660, let_sp=0.02, align=0, alpha_v=0.95, ridx=14010),
        mk_tseg("MÌ CAY MỰC KHỔNG LỒ  •  250G – 300G", 21.28, 3.24, FID_WORK,  FP_WORK,   "WorkSans-Medium", 4.5,  0.0,  0.125, let_sp=0.12, alpha_v=0.88, ridx=14010),
    ],
    [
        mk_tseg("MÌ CAY MỰC KHỔNG LỒ",                 0.14, 2.56, FID_OSWALD, FP_OSWALD, "Oswald-Bold",    10.4,  0.0,  0.002, let_sp=0.04, alpha_v=1.00, ridx=14020),
        mk_tseg("BẮP CẢI TÍM & CẢI THÌA\nTươi giòn",    8.88, 3.27, FID_WORK,   FP_WORK,   "WorkSans-Medium", 4.2, -0.44, 0.510, let_sp=0.02, align=2, alpha_v=0.95, ridx=14020),
        mk_tseg("FEEL CHICKEN",                       21.28, 3.24, FID_OSWALD, FP_OSWALD, "Oswald-Bold",    13.8,  0.0,  0.020, let_sp=0.07, alpha_v=1.00, ridx=14020),
    ],
    [
        mk_tseg("SIZE MỰC 250G – 300G  •  7 CẤP ĐỘ CAY",0.14, 2.56, FID_WORK,   FP_WORK,   "WorkSans-Medium", 4.6,  0.0, -0.095, let_sp=0.08, alpha_v=0.90, ridx=14030),
        mk_tseg("CÁ VIÊN & XÚC XÍCH\nĐầy ắp nhân ngon", 9.06, 3.09, FID_WORK,   FP_WORK,   "WorkSans-Medium", 4.2,  0.40, 0.240, let_sp=0.02, align=0, alpha_v=0.95, ridx=14030),
        mk_tseg("GIÁ RA MẮT 99K/TÔ  •  ĐỦ 7 CẤP ĐỘ CAY",21.40, 3.12, FID_MONT,  FP_MONT,   "Montserrat-Bold", 4.8,  0.0, -0.075, let_sp=0.05, alpha_v=0.96, ridx=14030),
    ],
    [
        mk_tseg("MỰC KHỔNG LỒ 250G–300G\nNguyên con giòn sần sật", 9.24, 2.91, FID_WORK, FP_WORK, "WorkSans-Medium", 4.3, -0.42, -0.010, let_sp=0.02, align=2, alpha_v=0.98, ridx=14040),
        mk_tseg("38 NGUYỄN ĐÌNH CHIỂU  •  35 TRẦN HỮU DUYỆT\n10:00 – 22:00   •   0796 601 106", 21.40, 3.12, FID_WORK, FP_WORK, "WorkSans-Medium", 4.2, 0.0, -0.148, let_sp=0.04, alpha_v=0.84, ridx=14040),
    ],
    [
        mk_tseg("MÌ SỢI HÀN QUỐC\nSợi xoăn dai thấm vị", 9.42, 2.73, FID_WORK,  FP_WORK,   "WorkSans-Medium", 4.2,  0.34, -0.270, let_sp=0.02, align=0, alpha_v=0.95, ridx=14050),
    ],
]:
    tt = copy.deepcopy(ttrack_tpl); tt["id"] = uid(); tt["flag"] = 0; tt["segments"] = tsegs
    D["tracks"].append(tt)

# TRACKS 6..10: EXACT ORIGINAL MUSE AUDIO STEMS (SEPARATE EDITABLE BGM + ASMR + SFX MATCHING build_master_audio()!)
AUDIO_RAW_MAP = {
    "bgm":    ("BGM_Dark_HipHop_Beat.mp3",   os.path.join(AUD_STG, "bgm_drake_hiphop.mp3")),
    "splash": ("ASMR_Bung_Song_Sup.mp3",     os.path.join(AUD_STG, "asmr_splash_plunge.mp3")),
    "sizzle": ("ASMR_Lua_Xao_Wok.mp3",       os.path.join(AUD_STG, "asmr_sizzle_boil.mp3")),
    "boil":   ("ASMR_Sup_Soi_Sung_Suc.mp3",  os.path.join(AUD_STG, "asmr_broth_sticky.mp3")),
    "pour":   ("ASMR_Dau_Ot_Roi.mp3",        os.path.join(AUD_STG, "asmr_pour_liquid.mp3")),
    "fastw":  ("SFX_Fast_Whoosh.mp3",        os.path.join(AUD_STG, "sfx_fast_whoosh.mp3")),
    "riser":  ("SFX_Riser_Truoc_Splash.mp3", os.path.join(AUD_STG, "sfx_riser_metal.mp3")),
    "lowhit": ("SFX_Bass_Drop_Hit.mp3",      os.path.join(AUD_STG, "sfx_low_hit.mp3")),
    "chime":  ("SFX_Chime_EndCard.mp3",      os.path.join(AUD_STG, "sfx_chime_warm.mp3")),
}
ap = {}
for k, (dn, sp) in AUDIO_RAW_MAP.items():
    dp = os.path.join(RAW_MUSE, dn)
    shutil.copyfile(sp, dp)
    ap[k] = dp

def mk_aseg(p: str, tl_s: float, dur_s: float, src_s: float = 0.0, vol: float = 1.0, fi: int = 33333, fo: int = 120000):
    mid, mdu = reg_aud(p)
    st_u = us_f(src_s)
    du_u = min(us_f(dur_s), max(33333, mdu - st_u))
    refs = []
    for k, te in a_extra_tpl.items():
        em = copy.deepcopy(te); em["id"] = uid()
        if k == "speeds": em["speed"] = 1.0
        D["materials"][k].append(em); refs.append(em["id"])
    af = copy.deepcopy(afade_tpl); af.update({"id": uid(), "fade_in_duration": min(du_u // 3, fi), "fade_out_duration": min(du_u // 3, fo)})
    D["materials"]["audio_fades"].append(af); refs.append(af["id"])
    sg = copy.deepcopy(aseg_tpl)
    sg.update({
        "id": uid(), "material_id": mid,
        "source_timerange": {"start": st_u, "duration": du_u},
        "target_timerange": {"start": us_f(tl_s), "duration": du_u},
        "speed": 1.0, "volume": float(vol), "last_nonzero_volume": float(max(0.05, vol)),
        "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        "render_index": 0, "track_render_index": 1, "visible": True,
    })
    return sg

for asegs in [
    [mk_aseg(ap["bgm"], 0.0, TOTAL_DUR, src_s=11.20, vol=0.82, fi=180000, fo=1200000)],
    [
        mk_aseg(ap["splash"],  0.15, 2.40, src_s=4.95, vol=0.52),
        mk_aseg(ap["pour"],    3.05, 2.10, src_s=0.15, vol=0.48),
        mk_aseg(ap["sizzle"],  5.82, 2.75, src_s=1.20, vol=0.56),
        mk_aseg(ap["boil"],    8.65, 3.40, src_s=6.00, vol=0.22),
        mk_aseg(ap["splash"], 12.22, 2.80, src_s=4.88, vol=0.78),
        mk_aseg(ap["boil"],   15.25, 2.90, src_s=1.00, vol=0.50),
        mk_aseg(ap["boil"],   18.30, 2.50, src_s=11.50, vol=0.46),
        mk_aseg(ap["boil"],   21.25, 3.20, src_s=6.00, vol=0.26, fo=800000),
    ],
    [
        mk_aseg(ap["boil"],    3.20, 1.60, src_s=1.00, vol=0.40),
        mk_aseg(ap["riser"],  10.85, 1.35, src_s=0.20, vol=0.24),
        mk_aseg(ap["pour"],   15.55, 2.10, src_s=0.15, vol=0.38),
        mk_aseg(ap["chime"],  21.35, 1.80, src_s=0.00, vol=0.20),
    ],
    [
        mk_aseg(ap["fastw"],  2.72, 1.10, src_s=0.0, vol=0.32),
        mk_aseg(ap["fastw"],  5.72, 1.10, src_s=0.0, vol=0.30),
        mk_aseg(ap["fastw"],  8.52, 1.10, src_s=0.0, vol=0.24),
        mk_aseg(ap["fastw"], 15.12, 1.10, src_s=0.0, vol=0.26),
        mk_aseg(ap["fastw"], 18.12, 1.10, src_s=0.0, vol=0.26),
    ],
    [
        mk_aseg(ap["lowhit"],  0.05, 2.40, src_s=0.0, vol=0.32),
        mk_aseg(ap["lowhit"],  2.80, 2.40, src_s=0.0, vol=0.36),
        mk_aseg(ap["lowhit"], 12.20, 2.40, src_s=0.0, vol=0.48),
        mk_aseg(ap["lowhit"], 21.20, 2.40, src_s=0.0, vol=0.36),
    ],
]:
    ta = copy.deepcopy(atrack_tpl); ta["id"] = uid(); ta["segments"] = asegs
    D["tracks"].append(ta)

# Write fresh uncached Muse CapCut folder + also update existing 'FEEL CHICKEN - Mì Cay Mực Siêu To MUSE'
cover_jpg = os.path.join(OUT_DIR, "_muse_cover.jpg")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.25", "-i", out_muse_mp4, "-frames:v", "1", "-vf", "scale=540:960,format=yuvj420p", "-q:v", "2", cover_jpg], check=True)

for dname, did in [
    (DRAFT_MUSE_NEW, DRAFT_MUSE_ID),
    ("FEEL CHICKEN - Mì Cay Mực Siêu To MUSE", "B84F2D19-6C3E-4A92-9E15-558291047361"),
]:
    ddir = os.path.join(DRAFTS_DIR, dname)
    os.makedirs(ddir, exist_ok=True)
    for fn in ("draft_agency_config.json", "draft_biz_config.json", "draft_settings", "draft_virtual_store.json", "performance_opt_info.json", "attachment_pc_common.json"):
        sp = os.path.join(v7_dir, fn)
        if os.path.isfile(sp):
            shutil.copyfile(sp, os.path.join(ddir, fn))
    if dname == DRAFT_MUSE_NEW and os.path.exists(os.path.join(ddir, "Timelines")):
        shutil.rmtree(os.path.join(ddir, "Timelines"), ignore_errors=True)

    D_cur = copy.deepcopy(D); D_cur["name"] = dname
    DM_cur = copy.deepcopy(dm_tpl)
    DM_cur.update({
        "draft_id": did, "draft_name": dname,
        "draft_fold_path": nfwd(ddir), "draft_root_path": nfwd(DRAFTS_DIR),
        "draft_cover": "draft_cover.jpg",
        "tm_duration": us_f(TOTAL_DUR), "tm_draft_create": now_us, "tm_draft_modified": now_us,
        "draft_timeline_materials_size": total_bytes,
    })
    for g in DM_cur["draft_materials"]:
        g["value"] = dm_type0 if g.get("type") == 0 else []

    dcb = json.dumps(D_cur, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    dmb = json.dumps(DM_cur, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    write_unlink(os.path.join(ddir, "draft_content.json"), dcb)
    write_unlink(os.path.join(ddir, "template-2.tmp"), dcb)
    write_unlink(os.path.join(ddir, "draft_meta_info.json"), dmb)
    shutil.copyfile(cover_jpg, os.path.join(ddir, "draft_cover.jpg"))

    tl_sub = os.path.join(ddir, "Timelines")
    if os.path.exists(tl_sub):
        for s in os.listdir(tl_sub):
            sd = os.path.join(tl_sub, s)
            if os.path.isdir(sd):
                write_unlink(os.path.join(sd, "draft_content.json"), dcb)
                write_unlink(os.path.join(sd, "template-2.tmp"), dcb)

rmi_p = os.path.join(DRAFTS_DIR, "root_meta_info.json")
if os.path.exists(rmi_p):
    rmi = json.load(open(rmi_p, encoding="utf-8"))
    stores = rmi.get("all_draft_store", [])
    tpl_e = copy.deepcopy(stores[0]) if stores else {}
    stores = [s for s in stores if s.get("draft_id") != DRAFT_MUSE_ID and s.get("draft_name") != DRAFT_MUSE_NEW]
    ddir_new = os.path.join(DRAFTS_DIR, DRAFT_MUSE_NEW)
    tpl_e.update({
        "draft_cover": nfwd(os.path.join(ddir_new, "draft_cover.jpg")),
        "draft_fold_path": nfwd(ddir_new),
        "draft_id": DRAFT_MUSE_ID,
        "draft_is_invisible": False,
        "draft_json_file": nfwd(os.path.join(ddir_new, "draft_content.json")),
        "draft_name": DRAFT_MUSE_NEW,
        "draft_root_path": nfwd(DRAFTS_DIR),
        "draft_timeline_materials_size": total_bytes,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "tm_draft_removed": 0,
        "tm_duration": us_f(TOTAL_DUR),
    })
    stores.insert(0, tpl_e)
    rmi["all_draft_store"] = stores
    rmi["draft_ids"] = len(stores)
    write_unlink(rmi_p, json.dumps(rmi, ensure_ascii=False, indent=2).encode("utf-8"))


# ==============================================================================
# 4. GENERATE 8-FRAME VISUAL QC SHEET FOR UPDATED MUSE 9:16 FINAL MP4
# ==============================================================================
print("[4/4] Building 8-Frame QC Sheet for Updated MUSE 9:16 Final MP4...", flush=True)
cw, ch = 260, 462
grid = Image.new("RGB", (cw * 4, ch * 2), (10, 10, 10))
dr = ImageDraw.Draw(grid)
fn_l = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 14)

sample_ts = [
    (1.25,  "01 Chili Wave + Center Title @1.25s"),
    (4.25,  "02 Zero-G Squid Whip @4.25s"),
    (7.15,  "03 Wok Hei Fire Toss @7.15s"),
    (10.25, "04 Exploded Stack 1-Color @10.25s"),
    (13.55, "05 Broth Crown Splash @13.55s"),
    (16.65, "06 Macro 7-Level Boil @16.65s"),
    (19.65, "07 Chopstick Lift @19.65s"),
    (22.75, "08 Hero Pot + Center Text @22.75s"),
]
for i, (ts, lbl) in enumerate(sample_ts):
    jp = os.path.join(QC_DIR, f"_mqc_{i}.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", out_muse_mp4, "-frames:v", "1", "-vf", f"scale={cw}:{ch},format=yuvj420p", "-q:v", "2", jp], check=True)
    r, c = divmod(i, 4)
    grid.paste(Image.open(jp).convert("RGB"), (c * cw, r * ch))
    dr.rectangle([c * cw, r * ch, (c + 1) * cw, r * ch + 24], fill=(0, 0, 0))
    dr.text((c * cw + 6, r * ch + 5), lbl, fill=(255, 226, 120), font=fn_l)
    os.remove(jp)

qc_out = os.path.join(QC_DIR, "QC_MI_CAY_MUC_MUSE_9x16_CLEAN_TEXT.jpg")
grid.save(qc_out, quality=93)
shutil.copyfile(qc_out, os.path.join(ART_DIR, "fc_spicy_squid_muse_9x16_qc.jpg"))
if os.path.exists("Z:\\"):
    shutil.copyfile(qc_out, os.path.join(CLOUD_PRJ, os.path.basename(qc_out)))
    shutil.copyfile(__file__, os.path.join(CLOUD_PRJ, os.path.basename(__file__)))
print("ALL DONE! QC ->", qc_out, flush=True)
