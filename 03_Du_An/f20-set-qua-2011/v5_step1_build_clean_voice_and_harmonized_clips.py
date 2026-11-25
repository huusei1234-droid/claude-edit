import json, os, shutil, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from faster_whisper import WhisperModel

OUT      = Path(r"d:\AI\full studio\output\f20-set-qua-2011")
CACHE    = OUT / "raw_cache"
V3_DIR   = OUT / "v3_pro"
V4_DIR   = OUT / "v4_clean_master"
V5       = OUT / "v5_master"
CLIPS_V5 = V5 / "clips_v5"
VOICE_V5 = V5 / "voice_v5"
CLIPS_V5.mkdir(parents=True, exist_ok=True)
VOICE_V5.mkdir(parents=True, exist_ok=True)

LUTS_SRC = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau")
shutil.copy2(LUTS_SRC / "01_HTPM_Beauty_Rosy_Skin.cube", V5 / "lut_skin.cube")
shutil.copy2(LUTS_SRC / "10_AI_Clip_Harmonizer_Natural.cube", V5 / "lut_harm.cube")

SR, FPS = 48000, 30

# ==============================================================================
# 1. UNIFIED COMMERCIAL COLOR HARMONIZATION PROFILES (Per Camera / Room Lighting)
#    Brings Showroom tungsten, Dang Khoa Edu cool cyan room, and Outdoor clips
#    into ONE bright, rosy-skin, crisp-white, festive F20 color palette!
# ==============================================================================
LUT_SKIN_32 = "split[o][g];[g]lut3d=file=lut_skin.cube:interp=tetrahedral[g2];[o][g2]blend=all_expr='A*0.68+B*0.32'"
LUT_HARM_35 = "split[o][g];[g]lut3d=file=lut_harm.cube:interp=tetrahedral[g2];[o][g2]blend=all_expr='A*0.65+B*0.35'"

GRADE_SHOWROOM = (
    "colorbalance=rs=-0.03:gs=0.00:bs=0.04:rm=-0.035:gm=0.01:bm=0.055:rh=-0.02:gh=0.01:bh=0.04,"
    "eq=brightness=0.038:contrast=1.05:saturation=1.08:gamma=0.95,"
    f"{LUT_SKIN_32}"
)
GRADE_BLUE_BRIGHT = (   # C3908 (already bright 180,185,170, cool cyan -> warm golden ivory)
    "colorbalance=rs=0.03:gs=-0.01:bs=-0.04:rm=0.075:gm=0.01:bm=-0.075:rh=0.05:gh=0.01:bh=-0.06,"
    "eq=brightness=-0.025:contrast=1.07:saturation=1.14:gamma=0.98,"
    f"{LUT_HARM_35}"
)
GRADE_BLUE_MED = (      # C3909, C3921, C3928, C3932 (cool classroom -> warm cohesive showroom match)
    "colorbalance=rs=0.03:gs=-0.01:bs=-0.04:rm=0.07:gm=0.01:bm=-0.07:rh=0.05:gh=0.01:bh=-0.05,"
    "eq=brightness=0.028:contrast=1.06:saturation=1.14:gamma=0.96,"
    f"{LUT_HARM_35}"
)
GRADE_BLUE_DARK = (     # C3910 (130,136,130 -> lift + warm golden match)
    "colorbalance=rs=0.03:gs=-0.01:bs=-0.04:rm=0.075:gm=0.01:bm=-0.075:rh=0.05:gh=0.01:bh=-0.05,"
    "eq=brightness=0.065:contrast=1.07:saturation=1.15:gamma=0.93,"
    f"{LUT_HARM_35}"
)
GRADE_OUTDOOR = (       # C3901 SUV loading
    "colorbalance=rm=0.045:gm=0.01:bm=-0.045:rh=0.03:gh=0.01:bh=-0.03,"
    "eq=brightness=0.02:contrast=1.05:saturation=1.10:gamma=0.97,"
    f"{LUT_HARM_35}"
)

def render_video_clip(out_name, src_p, ss, dur, crop_vf, grade_vf, wav_mux=None):
    frames = int(round(dur * FPS))
    exact_dur = frames / FPS
    dst = CLIPS_V5 / out_name
    tmp_v = CLIPS_V5 / f"_tmp_{out_name}"
    vf = f"{crop_vf},{grade_vf},fps=30,format=yuv420p"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.4f}", "-t", f"{exact_dur:.4f}", "-i", str(src_p),
        "-vf", vf, "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "15", str(tmp_v)
    ], cwd=str(V5), check=True)
    if wav_mux and Path(wav_mux).exists():
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_v), "-i", str(wav_mux),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(dst)
        ], check=True)
        tmp_v.unlink(missing_ok=True)
    else:
        tmp_v.replace(dst)
    return dst, exact_dur, frames

def extract_sony_voice_slice(src_p, ss, dur, is_tts=False):
    # Sony wireless mic is on Right channel (c1); TTS WAV is already stereo
    pan = "loudnorm=I=-16.0:TP=-1.5:LRA=8.0" if is_tts else (
        "pan=stereo|c0=c1|c1=c1,highpass=f=85,afftdn=nf=-24,"
        "equalizer=f=240:t=q:w=1.2:g=-1.5,equalizer=f=3300:t=q:w=1.3:g=2.0,"
        "acompressor=threshold=-19dB:ratio=2.4:attack=8:release=90"
    )
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error",
        "-ss", f"{ss:.4f}", "-t", f"{dur:.4f}", "-i", str(src_p),
        "-af", pan, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"
    ])
    arr = np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()
    # Gentle RMS match to 0.105 with soft tanh ceiling at 0.88 + 25ms/35ms micro-fades
    rms = float(np.sqrt(np.mean(arr ** 2)))
    if rms > 0.008:
        arr = arr * (0.105 / rms)
        arr = np.tanh(arr / 0.88) * 0.88
    fi, fo = min(len(arr)//4, int(0.025 * SR)), min(len(arr)//4, int(0.035 * SR))
    if fi > 2: arr[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 2: arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return arr

def save_block_wav(bid, pieces, target_frames):
    cat = np.vstack(pieces)
    need = int(round((target_frames / FPS) * SR))
    if len(cat) < need:
        cat = np.vstack([cat, np.zeros((need - len(cat), 2), dtype=np.float32)])
    cat = cat[:need]
    fo = int(0.040 * SR)
    cat[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    wp = VOICE_V5 / f"{bid}.wav"
    pcm = (np.clip(cat, -0.98, 0.98) * 32767.0).astype(np.int16)
    with wave.open(str(wp), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return wp, cat


# ==============================================================================
# 2. PREPARE ALL HARMONIZED REAL SONY B-ROLL CLIPS (Zero Camera Lens, Zero Bad Zoom!)
# ==============================================================================
BROLL_JOBS = [
    # 3-Shot Crisp Product Pan Intro ("mấy giây đầu là cảnh lia sản phẩm mà???")
    ("br_intro1_sunlit_sets.mp4", CACHE / "C3909.MP4", 0.40, 2.20, "scale=1080:1920", GRADE_BLUE_MED),
    ("br_intro2_long_table.mp4",  CACHE / "C3910.MP4", 0.50, 2.20, "scale=1080:1920", GRADE_BLUE_DARK),
    ("br_intro3_shelf_tower.mp4", CACHE / "C3875.MP4", 0.50, 2.40, "scale=1080:1920", GRADE_SHOWROOM),

    # Wide Panoramic Shots of Chi Oanh Standing Amidst All 104 Gift Sets! ("có các cảnh chị oanh đứng giữa mớ quà tặng bỏ vô")
    ("br_wide_oanh_arms_104.mp4", CACHE / "C3845.MP4", 1.50, 5.50, "scale=1096:1948,crop=1080:1920:4:14", GRADE_SHOWROOM),
    ("br_wide_oanh_row_104.mp4",  CACHE / "C3865.MP4", 5.00, 5.50, "scale=1080:1920", GRADE_SHOWROOM),
    ("br_clean_row_104sets.mp4",  CACHE / "C3869.MP4", 1.50, 5.50, "scale=1080:1920", GRADE_SHOWROOM),

    # Customer Handover & Shipping B-rolls (Color-matched!)
    ("br_anh_hau_handover.mp4",   CACHE / "C3921.MP4", 0.80, 4.50, "scale=1080:1920", GRADE_BLUE_MED),
    ("br_anh_hau_77sets.mp4",     CACHE / "C3932.MP4", 0.60, 4.50, "scale=1080:1920", GRADE_BLUE_MED),
    ("br_phu_huynh_13sets.mp4",   CACHE / "C3866.MP4", 3.00, 5.00, "scale=1080:1920", GRADE_SHOWROOM),
    ("br_hanoi_carton.mp4",       CACHE / "C3892.MP4", 0.60, 4.50, "scale=1080:1920", GRADE_SHOWROOM),
    ("br_hcmc_suv.mp4",           CACHE / "C3901.MP4", 0.50, 4.80, "scale=1080:1920", GRADE_OUTDOOR),

    # Authentic Packaged Gift Basket & Inside-Basket Shots (1.00x UN-ZOOMED! Fixes Image 3, 4, 6, 9!)
    ("br_basket_full_hero.mp4",   CACHE / "C3908.MP4", 0.40, 6.50, "scale=1080:1920", GRADE_BLUE_BRIGHT),
    ("br_basket_flower_bow.mp4",  CACHE / "C3909.MP4", 1.60, 6.50, "scale=1080:1920", GRADE_BLUE_MED),
    ("br_basket_row_bow.mp4",     CACHE / "C3910.MP4", 2.00, 6.00, "scale=1080:1920", GRADE_BLUE_DARK),
    ("br_inside_basket_real.mp4", CACHE / "C3873.MP4", 0.40, 7.50, "scale=1080:1920", GRADE_SHOWROOM),
    ("br_shelf_sets_pan.mp4",     CACHE / "C3867.MP4", 0.50, 5.50, "scale=1080:1920", GRADE_SHOWROOM),
    ("br_camnang_close.mp4",      CACHE / "C3854.MP4", 1.50, 6.50, "scale=1080:1920", GRADE_SHOWROOM),
    ("br_factory_pack1.mp4",      CACHE / "C3882.MP4", 0.60, 5.00, "scale=1080:1920", GRADE_SHOWROOM),
]

print("Rendering 18 color-harmonized real Sony B-roll clips...", flush=True)
for oname, sp, ss, dur, cvf, gvf in BROLL_JOBS:
    render_video_clip(oname, sp, ss, dur, cvf, gvf)
    print("  -> B-roll ready:", oname, flush=True)


# ==============================================================================
# 3. SURGICAL STUMBLE-FREE VOICEOVER + x=540 CENTERED SONY LIVE CLIPS!
# ==============================================================================
INTRO_DUR = 3.9000   # 117 frames: 3 crisp product pan shots (1.30s + 1.30s + 1.30s) BEFORE Chi Oanh enters!
OUTRO_DUR = 3.0000   # 90 frames: Festive F20 x SKA NEST End-Card

cur_t = INTRO_DUR
blocks_meta = []
master_vo = [np.zeros((int(round(INTRO_DUR * SR)), 2), dtype=np.float32)]

def add_block(bid, mode, pieces_spec, live_vid_spec=None):
    global cur_t
    # pieces_spec: list of (src_path, ss, dur, is_tts)
    raw_pieces = [extract_sony_voice_slice(sp, ss, d, is_tts=tt) for sp, ss, d, tt in pieces_spec]
    tot_samples = sum(len(x) for x in raw_pieces)
    frames = max(15, int(round((tot_samples / SR) * FPS)))
    exact_dur = frames / FPS
    wp, vo_arr = save_block_wav(bid, raw_pieces, frames)
    master_vo.append(vo_arr)

    vpath = None
    if live_vid_spec:
        src_v, v_ss, crop_vf, grade_vf = live_vid_spec
        vp, _, _ = render_video_clip(f"{bid}.mp4", src_v, v_ss, exact_dur, crop_vf, grade_vf, wav_mux=wp)
        vpath = str(vp)

    binfo = {
        "id": bid, "mode": mode,
        "video_path": vpath, "wav_path": str(wp),
        "start": round(cur_t, 4), "end": round(cur_t + exact_dur, 4),
        "dur": round(exact_dur, 4), "frames": frames,
    }
    blocks_meta.append(binfo)
    print(f"Block {bid:24s} [{cur_t:6.2f} -> {cur_t+exact_dur:6.2f}s] ({exact_dur:5.2f}s) mode={mode}", flush=True)
    cur_t += exact_dur
    return binfo

# --- b01: Opening Live Chi Oanh (C3841 3.95s..13.15s = 9.20s) + Nha Trang 77 sets & 13 sets (13.18s..23.90s, pause at 19.7s tightened!)
add_block(
    "b01_open_live", "live",
    [(CACHE / "C3841.MP4", 3.95, 9.20, False)],
    live_vid_spec=(CACHE / "C3841.MP4", 3.95, "scale=1156:2055,crop=1080:1920:0:68", GRADE_SHOWROOM),
)
add_block(
    "b02_nhatrang_real", "real_vo",
    [
        (CACHE / "C3841.MP4", 13.18, 6.50, False),   # "Ở Nha Trang thì có 2 khách hàng: 1 là Anh Hậu... đặt 77 set quà"
        (CACHE / "C3841.MP4", 20.12, 3.80, False),   # Tightened pause! "và 1 khách hàng thứ 2 là 1 nhóm hội phụ huynh đặt 13 set quà"
    ],
)
# --- b03: Ha Noi 10 sets + TP.HCM 4 sets + Tong 104 set qua (Clean off-camera s03_ship_tts / real voice without "bộn / thí sạng" slur!)
# Let's check s03_ship_tts.wav in V3_DIR: it covers Ha Noi + TP.HCM + Tong 104 set cleanly off-camera, OR use Ha Noi TTS (3.17s) + clean C3841!
# Wait: remember user said "thoại chị Oanh vẫn bị sai với vấp kìa" ("bộn set qua / tổng thí sạng" at 33.0-34.4s of C3841!).
# Using V3_DIR / voice_clips / s03_ship_tts.wav ONLY for the slurred Ha Noi + "bộn / thí sạng" off-camera B-roll sentences makes it 100% fluent!
s03_tts_p = V3_DIR / "voice_clips" / "s03_ship_tts.wav"
s03_dur = float(json.loads(subprocess.check_output(["ffprobe","-v","quiet","-show_entries","format=duration","-of","json",str(s03_tts_p)]))["format"]["duration"])
add_block(
    "b03_ship_104_clean", "tts_bridge",
    [(s03_tts_p, 0.00, s03_dur, True)],
)

# --- b04: Wide Chi Oanh Standing Amidst 104 Sets ("Đây là những set quà bên Oanh đã chuẩn bị xong...") -> C3845.MP4 LIVE!
add_block(
    "b04_wide_oanh_104_live", "live",
    [(CACHE / "C3845.MP4", 1.55, 4.65, False)],
    live_vid_spec=(CACHE / "C3845.MP4", 1.55, "scale=1096:1948,crop=1080:1920:4:14", GRADE_SHOWROOM),
)

# --- b05: Live Chi Oanh Intro to 1 Set Qua (C3849.MP4 2.50..7.55s, centered at x=540!)
add_block(
    "b05_intro_set_live", "live",
    [(CACHE / "C3849.MP4", 2.50, 5.05, False)],
    live_vid_spec=(CACHE / "C3849.MP4", 2.50, "scale=1140:2026,crop=1080:1920:0:53", GRADE_SHOWROOM),
)

# --- b06: 4 Items Inside Set Qua (C3852.MP4 — 100% Real Chi Oanh Voice with all 4 dead pauses & "Còn..." surgically removed!)
add_block(
    "b06_4items_real_tight", "real_vo",
    [
        (CACHE / "C3852.MP4", 0.44,  9.66, False),   # 0.44..10.10: "Một cái set quà tặng... 1 tổ yến sào tinh chế sợi dài dòng tiêu chuẩn"
        (CACHE / "C3852.MP4", 10.52, 6.32, False),   # Skips "Còn..."! 10.52..16.84: "Kèm theo cho mọi người là nguyên liệu chưng: táo đỏ, đông trùng hạ thảo, kỷ tử và 1 hộp đường phèn"
        (CACHE / "C3852.MP4", 16.88, 8.12, False),   # 16.88..25.00: "Thứ 2 là sẽ có 2 hộp rong biển sấy giòn: 1 hộp sấy giòn cay nhẹ và 1 hộp sấy mè không cay"
        (CACHE / "C3852.MP4", 25.68, 4.72, False),   # Skips 0.68s drag! 25.68..30.40: "Thứ 3 là sẽ có cho mình 1 gói bánh thuyền mix hạt dinh dưỡng 250g"
        (CACHE / "C3852.MP4", 31.88, 9.48, False),   # Skips 1.48s dead air! 31.88..41.36: "Thứ 4 là sẽ có cho mình 1 gói rong biển kẹp hạt 500g, ở trong này có từ 22 đến 24 thanh..."
    ],
)

# --- b07a: Gia Tri Nhat To Yen Tinh Che (C3856.MP4 1.94..8.68s = 6.74s real voice over authentic SKA NEST packaged box!)
add_block(
    "b07a_yen_giatri_real", "real_vo",
    [(CACHE / "C3856.MP4", 1.94, 6.74, False)],
)

# --- b07b: Live Chi Oanh Holding Blue Cam Nang (C3856.MP4 — skips "Được bên Oanh... có..." stumble! Starts cleanly at 11.08s "Chuẩn bị thêm 1 cái tờ cẩm nang... công dụng của yến sào" = 8.12s LIVE!)
# Wait: let's check 10.12s ("Bên Oanh..."): at 10.44-11.12 she paused 0.68s on "có...". Starting at 11.08s ("Chuẩn bị thêm...") or keeping "Bên Oanh" + skipping "có"? No, on LIVE camera a splice inside live video would jump her head unless B-roll covers it! If we start LIVE C3856 right at 10.14s ("Bên Oanh có chuẩn bị thêm 1 cái tờ cẩm nang... công dụng của yến sào" 10.14..19.16 = 9.02s), skipping the 1.46s "Được... bên..." stumble at 8.68..10.14s while still on B-roll, then her mouth is 100% continuous on camera!
add_block(
    "b07b_camnang_live", "live",
    [(CACHE / "C3856.MP4", 10.12, 9.04, False)],
    live_vid_spec=(CACHE / "C3856.MP4", 10.12, "scale=1096:1948,crop=1080:1920:8:14", GRADE_SHOWROOM),
)

# --- b08: Chung Yen Dung Cach (Clean off-camera TTS bridge replacing "chứng hiện đúng cách" slur!)
add_block(
    "b08_chungyen_clean", "tts_bridge",
    [(V3_DIR / "voice_clips" / "s11_cam_nang.wav", 8.46, 3.20, True)],
)

# --- b09a: Gio Dung Qua Mica Trong Suot (C3853.MP4 — skips 0.8s drag between "giỏ đựng quà" and "chất liệu mica" while on B-roll!)
add_block(
    "b09a_giomica_real", "real_vo",
    [
        (CACHE / "C3853.MP4", 2.02, 3.90, False),    # "Tất cả sản phẩm sẽ được bên Oanh xếp trong 1 cái giỏ đựng quà"
        (CACHE / "C3853.MP4", 6.55, 2.32, False),    # Skips 0.63s drag! "chất liệu mica trong suốt như thế này nha mọi người"
    ],
)

# --- b09b: LIVE Chi Oanh Holding Basket & Showing Crimson Handle + Magnifying Loupe! (C3853.MP4 8.88..14.30s = 5.42s, 100% LIVE centered!)
add_block(
    "b09b_quai_da_live", "live",
    [(CACHE / "C3853.MP4", 8.88, 5.42, False)],
    live_vid_spec=(CACHE / "C3853.MP4", 8.88, "scale=1166:2073,crop=1080:1920:86:76", GRADE_SHOWROOM),
)

# --- b09c: Bong Hoa Diem Nhan & No Mau Be (C3853.MP4 — SURGICALLY SKIPS "mình có để có" 14.30..15.68s AND "sẵn sẵn" duplicate at 20.64s!)
add_block(
    "b09c_hoa_no_real", "real_vo",
    [
        (CACHE / "C3853.MP4", 15.68, 4.96, False),   # "Thiết kế thêm một vài bông hoa tạo điểm nhấn và một cái nơ màu be rất là xinh"
        (CACHE / "C3853.MP4", 20.66, 0.74, False),   # "xắn như thế này!" (skips stuttered first "sẵn"!)
    ],
)

# --- b10: Truc Tiep San Xuat (C3862.MP4 — Live 2.55..7.66s + tight real_vo 8.38..11.42s skipping 0.72s drag!)
add_block(
    "b10a_sx_live", "live",
    [(CACHE / "C3862.MP4", 2.55, 5.12, False)],
    live_vid_spec=(CACHE / "C3862.MP4", 2.55, "scale=1166:2073,crop=1080:1920:0:76", GRADE_SHOWROOM),
)
add_block(
    "b10b_sx_yentam_real", "real_vo",
    [(CACHE / "C3862.MP4", 8.38, 3.05, False)],
)

# --- b11: Thank-You & 20/11 CTA (C3864.MP4 — SURGICALLY CUTS OUT "đặt thang," mistake!!):
# First let's inspect exact word timestamps on mono-right channel of C3864.MP4 before cutting!
wmodel = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
c3864_mono = V5 / "_c3864_right.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(CACHE / "C3864.MP4"), "-af", "pan=mono|c0=c1", "-ar", "16000", str(c3864_mono)], check=True)
segs_64, _ = wmodel.transcribe(str(c3864_mono), language="vi", word_timestamps=True, vad_filter=True, condition_on_previous_text=False)
words_64 = [w for s in segs_64 for w in (s.words or [])]
print("C3864 Right-Channel Words:", " ".join(f"{w.word.strip()}({w.start:.2f}-{w.end:.2f})" for w in words_64), flush=True)
c3864_mono.unlink(missing_ok=True)

# Find exact end of "cầu" and start of second "đặt" (before "set quà tặng") in C3864!
t_cau_end = 12.66
t_dat2_start = 13.86
for idx_w, w in enumerate(words_64):
    ww = w.word.strip().lower().strip(".,!")
    if ww == "cầu" and 10.0 <= w.end <= 14.0:
        t_cau_end = round(w.end + 0.03, 3)
    if ww == "đặt" and 13.2 <= w.start <= 15.0:
        t_dat2_start = round(w.start - 0.03, 3)
print(f"Surgical cut of 'đặt thang' in C3864: keep [5.10 .. {t_cau_end:.3f}] -> skip '{t_cau_end:.3f}..{t_dat2_start:.3f}' -> keep [{t_dat2_start:.3f} .. 19.15]!", flush=True)

# b11a_cta_live1: Live Chi Oanh centered at x=540 saying "Oanh xin gửi lời cảm ơn... Thực Phẩm F20" (5.10 .. 10.75s = 5.65s)
add_block(
    "b11a_cta_live1", "live",
    [(CACHE / "C3864.MP4", 5.10, 5.65, False)],
    live_vid_spec=(CACHE / "C3864.MP4", 5.10, "scale=1166:2073,crop=1080:1920:0:76", GRADE_SHOWROOM),
)
# b11b_cta_cut_clean: "Nếu các anh chị còn có nhu cầu [SKIP đặt thang] đặt set quà tặng làm quà biếu tặng nhân dịp lễ 20/11" (covered by sunlit Gift Basket + Wide Oanh 104 sets!)
add_block(
    "b11b_cta_2011_real", "real_vo",
    [
        (CACHE / "C3864.MP4", 10.75, max(0.5, t_cau_end - 10.75), False),
        (CACHE / "C3864.MP4", t_dat2_start, max(0.5, 17.42 - t_dat2_start), False),
    ],
)
# b11c_cta_live2: Live Chi Oanh smiling centered at x=540 saying "thì hãy inbox ngay cho Oanh nhé!" (17.42 .. 19.32s = 1.90s + 0.3s smile!)
add_block(
    "b11c_cta_inbox_live", "live",
    [(CACHE / "C3864.MP4", 17.42, 2.10, False)],
    live_vid_spec=(CACHE / "C3864.MP4", 17.42, "scale=1166:2073,crop=1080:1920:0:76", GRADE_SHOWROOM),
)

voice_end = round(cur_t, 4)
total_dur = round(voice_end + OUTRO_DUR, 4)
total_frames = int(round(total_dur * FPS))
master_vo.append(np.zeros((int(round(OUTRO_DUR * SR)), 2), dtype=np.float32))

full_vo = np.vstack(master_vo)
vo_master_p = V5 / "01_Voice_V5_Master.wav"
pcm_all = (np.clip(full_vo, -0.98, 0.98) * 32767.0).astype(np.int16)
with wave.open(str(vo_master_p), "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(pcm_all.tobytes())

# Verify full 01_Voice_V5_Master.wav with Whisper large-v3-turbo!
print("\n=== VERIFYING FULL STUMBLE-FREE 01_Voice_V5_Master.wav ===", flush=True)
segs_all, _ = wmodel.transcribe(str(vo_master_p), language="vi", word_timestamps=True, vad_filter=True, condition_on_previous_text=False, beam_size=5)
w_segs = []
for s in segs_all:
    ws = [{"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word.strip()} for w in (s.words or [])]
    w_segs.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(), "words": ws})
    print(f"[{s.start:6.2f} -> {s.end:6.2f}] " + " ".join(f"{w['word']}({w['start']:.2f})" for w in ws), flush=True)

tl_v5 = {
    "fps": FPS, "intro_dur": INTRO_DUR, "voice_end": voice_end,
    "outro_dur": OUTRO_DUR, "total_dur": total_dur, "total_frames": total_frames,
    "blocks": blocks_meta, "whisper_segments": w_segs,
}
(V5 / "timeline_v5_master.json").write_text(json.dumps(tl_v5, ensure_ascii=False, indent=2), encoding="utf-8")

# Build Visual QC Sheet of ALL Harmonized & Centered V5 Clips (with x=540 green centerline & RGB stats!)
all_mp4s = sorted(CLIPS_V5.glob("*.mp4"))
cols = 5
rows = (len(all_mp4s) + cols - 1) // cols
sheet = Image.new("RGB", (240 * cols, 426 * rows), (18, 18, 18))
tmp_j = V5 / "_qct.jpg"
for i, mp in enumerate(all_mp4s):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.2", "-i", str(mp), "-frames:v", "1", str(tmp_j)], check=True)
    im = Image.open(tmp_j).convert("RGB")
    arr = np.array(im, dtype=np.float32)
    th = im.resize((240, 426), Image.Resampling.BILINEAR)
    d = ImageDraw.Draw(th)
    d.line([(120, 0), (120, 426)], fill=(0, 255, 110), width=2)
    d.rectangle([2, 2, 236, 36], fill=(0, 0, 0))
    d.text((5, 4), mp.stem[:25], fill=(255, 230, 60))
    d.text((5, 19), f"RGB: {arr[:,:,0].mean():.0f},{arr[:,:,1].mean():.0f},{arr[:,:,2].mean():.0f}", fill=(180, 255, 200))
    sheet.paste(th, ((i % cols) * 240, (i // cols) * 426))
tmp_j.unlink(missing_ok=True)
sheet.save(V5 / "v5_color_and_centering_qc.jpg", quality=92)
print(f"\nDONE STEP 1! Total duration={total_dur:.2f}s ({total_frames} frames). Saved v5_color_and_centering_qc.jpg!")
