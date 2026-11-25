import copy, json, math, os, re, shutil, subprocess, time, uuid, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems_v3")
os.makedirs(STEMS_DIR, exist_ok=True)

TLH_BGM_DIR = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"
TLH_SFX_DIR = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
DRAFTS_DIR  = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")

RAW_VID      = os.path.join(PROJ_DIR, "_htpm_lt_v3_video_only.mp4")
MAIN_CUT     = os.path.join(AROLL_DIR, "main_cut.mp4")
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\HTPM_LT_PLUS_TALKING_HEAD_FINAL.mp4"
DRIVE_FINAL1 = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_LT_PLUS_TALKING_HEAD_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-lt-plus-talking-head"

SR = 48000

def build_tlh_index():
    idx = {}
    if os.path.exists(TLH_SFX_DIR):
        for r, _, files in os.walk(TLH_SFX_DIR):
            for fn in files:
                idx[fn] = os.path.join(r, fn)
    return idx

TLH_INDEX = build_tlh_index()
def tlh_sfx(fname):
    return TLH_INDEX.get(fname, os.path.join(TLH_SFX_DIR, fname))

# 100% Curated From User's TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX) — Natural, Luxury, Commercial TVC Grade!
SFX_SPECS = {
    "tlh_magic_lux":     (tlh_sfx("Mở cảnh - Âm thanh tỏa sáng sang trọng (Magic Reveal).mp3"), 0.05, 2.40, "lowpass=f=11000"),
    "tlh_whoosh_tvc":    (tlh_sfx("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"),                 0.00, 0.62, None),
    "tlh_whoosh_pip":    (tlh_sfx("Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP).mp3"),       0.00, 0.48, None),
    "tlh_deep_swish":    (tlh_sfx("Whoosh - Deep Swish Transiiton 2 (1s).mp3"),                 0.05, 1.15, "lowpass=f=7500"),
    "tlh_swoosh_soft":   (tlh_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),                 0.00, 0.42, None),
    "tlh_swoosh_reverb": (tlh_sfx("Whoosh - Swoosh 2 Long Reverb (4s).mp3"),                    0.05, 2.20, "lowpass=f=8500"),
    "tlh_bubble_water":  (tlh_sfx("Pop & Bong Bóng - Pukutsu (water bubbles air) (1s).mp3"),    0.00, 0.40, "lowpass=f=5200"),
    "tlh_telop_low":     (tlh_sfx("Pop & Bong Bóng - Pop (lower) telop sound etc (1s).mp3"),    0.00, 0.15, "lowpass=f=4200"),
    "tlh_shine_01":      (tlh_sfx("Lấp Lánh & Phép Thuật - Shine_01 (3s).mp3"),                 0.02, 2.10, "highpass=f=500,lowpass=f=11500"),
    "tlh_fairy_dust":    (tlh_sfx("Lấp Lánh & Phép Thuật - Magic Fairy Dust Sound Effect (6s).mp3"), 0.10, 2.80, "highpass=f=600,lowpass=f=11000"),
    "tlh_notif_fine":    (tlh_sfx("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"),    0.00, 0.46, "lowpass=f=8500"),
    "tlh_riser_cine":    (tlh_sfx("Nổ Impact & Kịch Tính - Cinematic Riser Abrupt Stop 7 (3s).mp3"), 0.20, 2.15, "lowpass=f=7800"),
}

def decode_stereo_f32(path, ss=None, dur_limit=None, af=None):
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    cmd += ["-i", path]
    if dur_limit:
        cmd += ["-t", f"{dur_limit:.3f}"]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def save_wav_16(path, stereo_arr):
    clipped = np.clip(stereo_arr, -0.99, 0.99)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

def load_sfx_bank():
    bank = {}
    for key, (path, t0, t1, extra_af) in SFX_SPECS.items():
        if not os.path.exists(path):
            print("WARNING missing SFX:", key, path)
            continue
        af_parts = [f"atrim={t0:.3f}:{t1:.3f}", "asetpts=PTS-STARTPTS"]
        if extra_af:
            af_parts.append(extra_af)
        arr = decode_stereo_f32(path, af=",".join(af_parts))
        if len(arr) < 64:
            continue
        n_in = min(len(arr) // 4, int(0.015 * SR))
        n_out = min(len(arr) // 3, int(0.070 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
    print(f"Loaded {len(bank)} curated TLH Edit commercial SFX instruments.")
    return bank

def stamp(bus, bank, key, target_sec, db, pan=0.0, align_peak=True):
    if key not in bank:
        return 0
    clip, pk_idx = bank[key]
    gain = 10.0 ** (db / 20.0)
    ang = (max(-1.0, min(1.0, pan)) + 1.0) * (math.pi / 4.0)
    g_l = gain * math.cos(ang) * 1.4142
    g_r = gain * math.sin(ang) * 1.4142

    s_idx = int(round(target_sec * SR)) - (pk_idx if align_peak else 0)
    e_idx = s_idx + len(clip)
    bs, be = max(0, s_idx), min(len(bus), e_idx)
    if be <= bs:
        return 0
    cs = bs - s_idx
    seg = clip[cs:cs + (be - bs)]
    bus[bs:be, 0] += seg[:, 0] * g_l
    bus[bs:be, 1] += seg[:, 1] * g_r
    return 1

def build_audio_and_export():
    from render_v3_muse_master import load_captions_v3_readable

    dur_j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. Warm, Clear Pharmacist Voiceover (-14 LUFS)
    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3350:t=q:w=1.2:g=1.5,loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # 2. 2-Half BGM from User's TLH\Edit\01_Nhạc Nền (BGM)
    bgm1_path = os.path.join(TLH_BGM_DIR, r"04_Piano - Buồn - Sâu Lắng - Cảm Xúc\Soft Piano Inspiration01 (4p26s).mp3")
    bgm2_path = os.path.join(TLH_BGM_DIR, r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Corporate Medicine (2p22s).mp3")

    bgm_eq = "highpass=f=85,equalizer=f=2150:t=q:w=1.25:g=-4.5,lowpass=f=12000,loudnorm=I=-14:TP=-1.5:LRA=9"
    b1_raw = decode_stereo_f32(bgm1_path, ss=2.5, dur_limit=40.0, af=bgm_eq)
    b2_raw = decode_stereo_f32(bgm2_path, ss=4.0, dur_limit=40.0, af=bgm_eq)
    b1 = np.tile(b1_raw, ((N // len(b1_raw)) + 2, 1))[:N]
    b2 = np.tile(b2_raw, ((N // len(b2_raw)) + 2, 1))[:N]

    t_axis = np.arange(N, dtype=np.float32) / SR
    xfade = np.clip((t_axis - 29.6) / 2.6, 0.0, 1.0)
    xfade = xfade * xfade * (3.0 - 2.0 * xfade)
    bgm = b1 * (1.0 - xfade[:, None]) + b2 * xfade[:, None]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.022).astype(np.float32)

    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 22):min(n_hops, i_h + 30)] = 1.0
    win_sm = np.hanning(45).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (22, 22), mode="edge"), win_sm, mode="valid")[:n_hops]
    gain_hop = 0.46 * (1.0 - sp_sm) + 0.265 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)
    bgm_env *= np.clip(t_axis / 0.8, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 2.0, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    # 3. Hand-Picked TLH Edit SFX (Smooth, Subtle, Commercial TVC Polish!)
    bank = load_sfx_bank()
    sfx_trans   = np.zeros((N, 2), dtype=np.float32)
    sfx_sparkle = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    # A. Hook Opening & Text Entrance/Exit (0.08 - 3.85s)
    cues += stamp(sfx_sparkle, bank, "tlh_magic_lux",   0.08, -14.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "tlh_whoosh_pip",  0.98, -14.0, pan=-0.16)
    cues += stamp(sfx_trans,   bank, "tlh_swoosh_soft", 1.38, -14.5, pan=+0.16)
    cues += stamp(sfx_trans,   bank, "tlh_telop_low",   2.18, -16.5, pan=0.0)

    # B. Multi-Video Scene Transitions (Silky TVC Whooshes & Deep Swishes from TLH!)
    cues += stamp(sfx_trans,   bank, "tlh_whoosh_tvc",    3.98, -12.2, pan=-0.10)   # Enter Disc1
    cues += stamp(sfx_trans,   bank, "tlh_deep_swish",    7.18, -13.0, pan=+0.12)   # Diagonal Wipe -> Disc2
    cues += stamp(sfx_trans,   bank, "tlh_swoosh_reverb", 10.82,-14.5, pan=0.0, align_peak=False)  # Glassmorphic 3D Cells
    cues += stamp(sfx_trans,   bank, "tlh_whoosh_tvc",    17.05,-12.8, pan=0.0)     # Optical Morph -> Doctor Reassure
    cues += stamp(sfx_sparkle, bank, "tlh_shine_01",      17.15,-16.5, pan=+0.10, align_peak=False)
    cues += stamp(sfx_trans,   bank, "tlh_whoosh_tvc",    23.20,-12.5, pan=-0.20)   # PIP 1: Doctor Eval
    cues += stamp(sfx_trans,   bank, "tlh_whoosh_pip",    26.78,-12.8, pan=+0.22)   # PIP 2: Lab Microscope

    # C. LT PLUS Hằng Thu Muse Product Video #1 (Hydrogel Stage + 6 Rising Water-Pearl Herb Bubbles!)
    cues += stamp(sfx_trans,   bank, "tlh_riser_cine",    29.30,-17.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "tlh_deep_swish",    30.84,-11.8, pan=0.0)
    cues += stamp(sfx_sparkle, bank, "tlh_magic_lux",     30.90,-13.8, pan=0.0, align_peak=False)

    # Gentle organic water-bubble sound (Pukutsu) + subtle telop touch on the 6 rising herbal bubbles!
    bubble_cues = [
        (33.66, -0.28), (34.68, +0.28), (35.12, -0.30),
        (36.16, +0.30), (37.00, -0.25), (37.70, +0.25)
    ]
    for bt, bpan in bubble_cues:
        cues += stamp(sfx_sparkle, bank, "tlh_bubble_water", bt + 0.08, -14.2, pan=bpan)
        cues += stamp(sfx_trans,   bank, "tlh_telop_low",    bt + 0.04, -18.0, pan=bpan)
    cues += stamp(sfx_sparkle, bank, "tlh_fairy_dust", 38.20, -15.5, pan=0.0, align_peak=False)

    # D. Muse Product Video #2 (Open Magnetic Box 41.55s) & #3 (Luxury Blush Silk Trio 45.88s) & #4 (Finale 50.20s)
    cues += stamp(sfx_trans,   bank, "tlh_whoosh_tvc",    41.58,-12.5, pan=0.0)
    cues += stamp(sfx_sparkle, bank, "tlh_shine_01",      41.68,-16.0, pan=0.0, align_peak=False)

    cues += stamp(sfx_trans,   bank, "tlh_riser_cine",    44.40,-18.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "tlh_deep_swish",    45.88,-11.8, pan=0.0)
    cues += stamp(sfx_sparkle, bank, "tlh_fairy_dust",    45.95,-14.0, pan=0.0, align_peak=False)

    cues += stamp(sfx_trans,   bank, "tlh_swoosh_reverb", 50.22,-14.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_sparkle, bank, "tlh_shine_01",      50.32,-15.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_sparkle, bank, "tlh_notif_fine",    53.92,-13.5, pan=0.0)

    # E. Ultra-Subtle, Soft Phrase Entrance Touch on Key Brand Mentions ("LT PLUS") Only!
    cap_groups, BRAND_WORDS, _, _ = load_captions_v3_readable()
    for g in cap_groups:
        for ln in g["lines"]:
            for wtxt, ws, _ in ln:
                if wtxt in ("LT", "LT PLUS"):
                    cues += stamp(sfx_trans, bank, "tlh_telop_low", ws + 0.02, -17.5, pan=0.0)

    print(f"Stamped {cues} curated TLH Edit commercial SFX cues across {vid_dur:.2f}s!")

    sfx_trans   = (np.tanh(sfx_trans * 0.95) / 0.95) * 0.85
    sfx_sparkle = (np.tanh(sfx_sparkle * 0.95) / 0.95) * 0.85

    vo_wav      = os.path.join(STEMS_DIR, "01_Voice_Master.wav")
    bgm_wav     = os.path.join(STEMS_DIR, "02_BGM_TLH_2Half_Pro.wav")
    trans_wav   = os.path.join(STEMS_DIR, "03_SFX_TLH_Commercial_Whoosh.wav")
    sparkle_wav = os.path.join(STEMS_DIR, "04_SFX_TLH_Bubbles_Luxury_Shine.wav")
    mix_wav     = os.path.join(STEMS_DIR, "full_mix_v3_pre_lufs.wav")

    save_wav_16(vo_wav, vo)
    save_wav_16(bgm_wav, bgm)
    save_wav_16(trans_wav, sfx_trans)
    save_wav_16(sparkle_wav, sfx_sparkle)

    full_mix = vo + bgm + sfx_trans + sfx_sparkle
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)
    save_wav_16(mix_wav, full_mix)

    pre_mov = os.path.join(PROJ_DIR, "_htpm_lt_v3_pre_lufs.mov")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", RAW_VID, "-i", mix_wav,
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "pcm_s16le", pre_mov
    ], check=True)

    p1 = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", pre_mov,
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

    os.makedirs(os.path.dirname(LOCAL_EXPORT), exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_mov,
        "-c:v", "copy", "-af", af_str, "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
        LOCAL_EXPORT
    ], check=True)
    if os.path.exists(pre_mov):
        os.remove(pre_mov)
    print("Saved Single Local Final:", LOCAL_EXPORT)

    os.makedirs(os.path.dirname(DRIVE_FINAL1), exist_ok=True)
    shutil.copy2(LOCAL_EXPORT, DRIVE_FINAL1)
    print("Synced Master Cloud Final:", DRIVE_FINAL1)

    shutil.copy2(
        r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\Montserrat-Bold.ttf",
        os.path.join(CHECK_DIR, "_f.ttf")
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", LOCAL_EXPORT,
        "-vf", "fps=1/2.96,scale=270:480,drawtext=fontfile=_f.ttf:text='%{pts\\:hms}':fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.65:x=8:y=8,tile=5x4",
        "-frames:v", "1", os.path.join(CHECK_DIR, "v3_sheet.jpg")
    ], cwd=CHECK_DIR, check=True)

    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for fn in ["job.json", "gen_v3_muse_all_videos.py", "render_v3_muse_master.py", "mix_v3_muse_master.py", "report.md"]:
        fp = os.path.join(PROJ_DIR, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    for fn, src_dir in [("main_cut_clean.json", AROLL_DIR), ("v3_sheet.jpg", CHECK_DIR), ("v3_muse_videos_qc.jpg", CHECK_DIR), ("v3_muse_master_grid.jpg", CHECK_DIR)]:
        fp = os.path.join(src_dir, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    print("Synced V3 Muse Master archive to Google Drive:", DRIVE_PROJ)

if __name__ == "__main__":
    build_audio_and_export()
