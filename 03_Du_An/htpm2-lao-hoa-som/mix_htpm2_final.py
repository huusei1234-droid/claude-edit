import json, math, os, re, shutil, subprocess, wave
import numpy as np

PROJ_DIR     = r"d:\AI\full studio\output\htpm2-flow"
AROLL_DIR    = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR    = os.path.join(PROJ_DIR, "check")
STEMS_DIR    = os.path.join(PROJ_DIR, "audio_stems")
os.makedirs(STEMS_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

TLH_SFX_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
SAAS_SFX_DIR = r"d:\AI\full studio\phong-cach\saas-animation\audio\sfx"
STUDIO_SFX_D = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"
BGM_DIR      = r"d:\AI\full studio\phong-cach\talking-head\assets_dung_chung\bgm"

RAW_VID      = os.path.join(PROJ_DIR, "_master_video_only.mp4")
MAIN_CUT     = os.path.join(AROLL_DIR, "main_cut.mp4")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "htpm_lao_hoa_som_final.mp4")
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\HTPM_LAO_HOA_SOM_FINAL.mp4"
DRIVE_FINAL  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_LAO_HOA_SOM_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm2-lao-hoa-som"
ARTIFACT_MP4 = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\HTPM_LAO_HOA_SOM_FINAL.mp4"

SR = 48000

def build_sfx_index():
    idx = {}
    for base in (TLH_SFX_DIR, SAAS_SFX_DIR, STUDIO_SFX_D):
        if os.path.exists(base):
            for r, _, files in os.walk(base):
                for fn in files:
                    idx[fn] = os.path.join(r, fn)
    return idx

SFX_IDX = build_sfx_index()
def find_sfx(fname):
    return SFX_IDX.get(fname, os.path.join(STUDIO_SFX_D, fname))

TACTILE_EQ = "highpass=f=140,equalizer=f=2400:t=q:w=1.25:g=-3.5,lowpass=f=13500"
AIRY_EQ    = "highpass=f=180,equalizer=f=2650:t=q:w=1.20:g=-4.5,lowpass=f=9000"

SFX_SPECS = {
    "airy_whoosh":  (find_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),                                  0.06, 0.34, AIRY_EQ),
    "soft_whoosh":  (find_sfx("sfx_whoosh_soft.mp3"),                                                        0.02, 0.32, AIRY_EQ),
    "swoosh_up":    (find_sfx("swoosh_up_b.wav"),                                                            0.00, 0.30, AIRY_EQ),
    "whoosh_pip":   (find_sfx("Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP).mp3"),                        0.03, 0.24, AIRY_EQ),
    "pop_clean":    (find_sfx("sfx_pop_clean.mp3"),                                                          0.00, 0.16, TACTILE_EQ),
    "pop_tvc":      (find_sfx("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),                                          0.02, 0.18, TACTILE_EQ),
    "pop_round":    (find_sfx("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"),                                   0.02, 0.18, TACTILE_EQ),
    "pop_bubble":   (find_sfx("Pop & Bong Bóng - Pukutsu (water bubbles air) (1s).mp3"),                     0.02, 0.22, TACTILE_EQ),
    "click_soft":   (find_sfx("sfx_click_soft.mp3"),                                                         0.00, 0.12, TACTILE_EQ),
    "click_picon":  (find_sfx("Click & Máy Chữ - Enter click select sound (picon)(890908) (1s).mp3"),        0.02, 0.20, TACTILE_EQ),
    "card_deal":    (find_sfx("Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3"), 0.02, 0.42, TACTILE_EQ),
    "paper_slide":  (find_sfx("Hoạt Hình & Hài - 01 Paper slide (1s).mp3"),                                  0.02, 0.34, TACTILE_EQ),
    "page_swipe":   (find_sfx("Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3"),    0.04, 0.40, TACTILE_EQ),
    "cutter_snip":  (find_sfx("Đời Thường & ASMR - Cut paper with a cutter 03(1487879) (1s).mp3"),           0.04, 0.28, TACTILE_EQ),
    "tick_gauge":   (find_sfx("tick_b.wav"),                                                                 0.00, 0.09, TACTILE_EQ),
    "ping_glass":   (find_sfx("sfx_ping_glass.mp3"),                                                         0.00, 0.52, TACTILE_EQ),
    "idea_ting":    (find_sfx("Ting - Chuông Ting nảy ý tưởng.mp3"),                                         0.00, 0.55, TACTILE_EQ),
    "notif_subtle": (find_sfx("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"),                     0.08, 0.40, TACTILE_EQ),
}

def decode_stereo_f32(path, dur_limit=None, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
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

def pitch_shift_semitones(arr, semitones: float):
    if abs(semitones) < 0.05:
        return arr
    factor = 2.0 ** (semitones / 12.0)
    new_len = max(16, int(round(len(arr) / factor)))
    x_old = np.linspace(0.0, 1.0, len(arr), dtype=np.float32)
    x_new = np.linspace(0.0, 1.0, new_len, dtype=np.float32)
    out = np.zeros((new_len, 2), dtype=np.float32)
    out[:, 0] = np.interp(x_new, x_old, arr[:, 0])
    out[:, 1] = np.interp(x_new, x_old, arr[:, 1])
    return out

def load_sfx_bank():
    bank = {}
    for key, (path, t0, t1, extra_af) in SFX_SPECS.items():
        if not path or not os.path.exists(path):
            continue
        af_parts = [f"atrim={t0:.3f}:{t1:.3f}", "asetpts=PTS-STARTPTS"]
        if extra_af:
            af_parts.append(extra_af)
        try:
            arr = decode_stereo_f32(path, af=",".join(af_parts))
        except Exception:
            continue
        if len(arr) < 48:
            continue
        n_in  = min(len(arr) // 5, int(0.008 * SR))
        n_out = min(len(arr) // 3, int(0.045 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
    print(f"[HTPM2 SFX] Loaded {len(bank)}/{len(SFX_SPECS)} tactile micro-SFX:", sorted(bank.keys()))
    return bank

def snap_to_speech(t_sec, speaking_hops, hop=480, max_shift_s=0.18):
    h_idx = min(len(speaking_hops) - 1, max(0, int(round(t_sec * SR / hop))))
    if speaking_hops[h_idx] > 0.5:
        return t_sec
    max_h = int(round(max_shift_s * SR / hop))
    for dh in range(1, max_h + 1):
        for cand in (h_idx + dh, h_idx - dh):
            if 0 <= cand < len(speaking_hops) and speaking_hops[cand] > 0.5:
                return (cand * hop) / float(SR)
    return t_sec

def stamp(bus, bank, key, target_sec, db_below_vo, semitones=0.0, pan=0.0, align_peak=True, speaking_hops=None):
    if key not in bank:
        return 0
    if speaking_hops is not None:
        target_sec = snap_to_speech(target_sec, speaking_hops)
    base_clip, _ = bank[key]
    clip = pitch_shift_semitones(base_clip, semitones)
    pk_idx = int(np.argmax(np.max(np.abs(clip), axis=1)))
    abs_db = -5.5 + float(db_below_vo)
    gain = 10.0 ** (abs_db / 20.0)
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

def loop_to_len(arr, n):
    if len(arr) >= n:
        return arr[:n].copy()
    reps = (n + len(arr) - 1) // len(arr)
    return np.tile(arr, (reps, 1))[:n].copy()

def main():
    dur_j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3250:t=q:w=1.15:g=1.6,loudnorm=I=-13.8:TP=-1.0:LRA=8")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # 2-Half C-Major BGM (-14.5 dB below Voice per Kobe Studio Gain Staging!)
    bgm_eq = "highpass=f=75,equalizer=f=1950:t=q:w=1.30:g=-5.0,loudnorm=I=-15.5:TP=-1.5:LRA=9"
    b1 = loop_to_len(decode_stereo_f32(os.path.join(BGM_DIR, "bgm_warm_fretless.mp3"), af=bgm_eq), N)
    b2 = loop_to_len(decode_stereo_f32(os.path.join(BGM_DIR, "bgm_bright_riley.mp3"), af=bgm_eq), N)
    t_axis = np.arange(N, dtype=np.float32) / SR
    w_b2 = np.clip((t_axis - 65.0) / 1.8, 0.0, 1.0)
    bgm = b1 * (1.0 - w_b2)[:, None] + b2 * w_b2[:, None]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.020).astype(np.float32)
    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 14):min(n_hops, i_h + 22)] = 1.0
    win_sm = np.hanning(35).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), win_sm, mode="valid")[:n_hops]
    gain_hop = 0.42 * (1.0 - sp_sm) + 0.235 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)
    bgm_env *= np.clip(t_axis / 0.35, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 1.5, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    # ==================================================================
    # KOBE STUDIO TACTILE MICRO-SFX CHOREOGRAPHY (HTPM2: Lão Hóa Sớm)
    # ==================================================================
    # 1. Hook RGB Prism (0.08s) + Question Wipe (1.94s)
    cues += stamp(sfx_bus, bank, "airy_whoosh",  0.10, -10.8)
    cues += stamp(sfx_bus, bank, "pop_clean",    0.20, -11.2, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "click_picon",  1.96, -12.8, speaking_hops=speaking)

    # 2. Age 25 Mirror Cinema Window Drop-Bounce + Landing Ripple (6.18s -> land 6.43s)
    cues += stamp(sfx_bus, bank, "click_soft",   6.12, -13.2, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "airy_whoosh",  6.18 - 0.11, -11.2, pan=-0.12)
    cues += stamp(sfx_bus, bank, "pop_tvc",      6.43, -11.0, speaking_hops=speaking)

    # 3A. Animated 25+ Tuổi Collagen & Elastin Decline Curve Riffle!
    cues += stamp(sfx_bus, bank, "swoosh_up",   13.28 - 0.10, -11.2)
    for k in range(5):
        cues += stamp(sfx_bus, bank, "tick_gauge", 13.68 + k * 0.14, -13.0, semitones=-k * 0.8, pan=-0.16 + k * 0.08)
    cues += stamp(sfx_bus, bank, "pop_round",   14.22, -11.6, speaking_hops=speaking)

    # 3B. 3D Collagen Fiber Window Drop-Bounce + Ripple (18.38s -> land 18.63s)
    cues += stamp(sfx_bus, bank, "whoosh_pip",  18.38 - 0.11, -11.4, pan=+0.12)
    cues += stamp(sfx_bus, bank, "pop_bubble",  18.63, -11.5, speaking_hops=speaking)

    # 4A. 4-Habit Frosted Pearl Bento Escalating Drop-Bounce (+1.2 semitone per tile!)
    for k, dt in enumerate([23.32, 23.41, 23.50, 23.59]):
        cues += stamp(sfx_bus, bank, "pop_clean", dt, -11.4, semitones=k * 1.2, pan=-0.24 + k * 0.16, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "notif_subtle",23.78, -13.2, align_peak=False, speaking_hops=speaking)

    # 4B. Late-Night Stress Window (27.48s) + Rapid Aging Marker Snip & Punch-In (32.30s)
    cues += stamp(sfx_bus, bank, "airy_whoosh", 27.48 - 0.11, -11.4)
    cues += stamp(sfx_bus, bank, "pop_tvc",     27.73, -11.5, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "soft_whoosh", 32.12 - 0.11, -10.8)
    cues += stamp(sfx_bus, bank, "cutter_snip", 32.34, -11.6, speaking_hops=speaking)

    # 5. 4-Card 3D Playing-Card Fan Deal + Thread-Line Escalating Carousel Slides!
    cues += stamp(sfx_bus, bank, "card_deal",   35.18, -11.2, pan=-0.18, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "pop_clean",   35.49, -11.8, semitones=0.0, speaking_hops=speaking)
    # Card 2 (42.76s)
    cues += stamp(sfx_bus, bank, "airy_whoosh", 42.76 - 0.12, -11.4, pan=-0.06)
    cues += stamp(sfx_bus, bank, "paper_slide", 42.78, -11.2, semitones=+1.0, pan=-0.04, speaking_hops=speaking)
    # Card 3 (49.10s)
    cues += stamp(sfx_bus, bank, "airy_whoosh", 49.10 - 0.12, -11.4, pan=+0.06)
    cues += stamp(sfx_bus, bank, "page_swipe",  49.12, -11.2, semitones=+2.0, pan=+0.08, speaking_hops=speaking)
    # Card 4 (55.42s) + Ping!
    cues += stamp(sfx_bus, bank, "airy_whoosh", 55.42 - 0.12, -11.4, pan=+0.16)
    cues += stamp(sfx_bus, bank, "paper_slide", 55.44, -11.2, semitones=+3.0, pan=+0.18, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "ping_glass",  55.82, -13.0, align_peak=False, speaking_hops=speaking)

    # 6A. Empowering Good News Hero Word-Spring (65.94s)
    cues += stamp(sfx_bus, bank, "soft_whoosh", 65.88 - 0.11, -10.8)
    for k in range(3):
        cues += stamp(sfx_bus, bank, "pop_tvc", 66.16 + k * 0.14, -12.2, semitones=k * 1.5, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "idea_ting",   66.72, -12.8, align_peak=False, speaking_hops=speaking)

    # 6B. Radiant Skin Cutaway + Iris Circle PiP Open (77.48s) & Close (87.58s)
    cues += stamp(sfx_bus, bank, "soft_whoosh", 77.48 - 0.11, -10.8)
    cues += stamp(sfx_bus, bank, "pop_round",   77.72, -11.8, pan=+0.22, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "airy_whoosh", 87.58 - 0.11, -11.2, pan=+0.15)

    # 7. Finale 3-Tick Checkmarks (+1.5 semitone climb!) + CTA Pill
    for k, dt in enumerate([90.06, 95.03, 98.33]):
        cues += stamp(sfx_bus, bank, "click_picon", dt, -12.4, semitones=k * 1.5, speaking_hops=speaking)
        cues += stamp(sfx_bus, bank, "ping_glass",  dt + 0.08, -13.0, semitones=k * 1.5, align_peak=False, speaking_hops=speaking)
    cues += stamp(sfx_bus, bank, "notif_subtle", 93.66, -13.0, align_peak=False, speaking_hops=speaking)

    print(f"[HTPM2 SFX] Placed {cues} tactile micro-SFX cues (0 noisy whooshes, 100% speech-locked).")

    raw_mix = vo + bgm + sfx_bus
    mix_wav = os.path.join(STEMS_DIR, "mix_pre_loudnorm.wav")
    norm_wav = os.path.join(STEMS_DIR, "mix_14lufs.wav")
    save_wav_16(mix_wav, raw_mix)

    p1 = subprocess.run(
        ["ffmpeg", "-y", "-i", mix_wav, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=9:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True
    )
    m_j = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p1.stderr)
    if m_j:
        st = json.loads(m_j.group(0))
        af2 = (
            f"loudnorm=I=-14.0:TP=-1.0:LRA=9:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
            f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"
        )
    else:
        af2 = "loudnorm=I=-14.0:TP=-1.0:LRA=9"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mix_wav, "-af", af2, "-ar", str(SR), "-ac", "2", norm_wav], check=True)

    os.makedirs(os.path.dirname(LOCAL_EXPORT), exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", RAW_VID, "-i", norm_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
        LOCAL_FINAL
    ], check=True)

    for dst in (LOCAL_EXPORT, DRIVE_FINAL, ARTIFACT_MP4):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(LOCAL_FINAL, dst)
        print("[HTPM2] Exported ->", dst)

    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for f_src in (
        os.path.join(AROLL_DIR, "main_cut_clean.json"),
        os.path.join(PROJ_DIR, "render_htpm2_master.py"),
        os.path.join(PROJ_DIR, "mix_htpm2_final.py"),
    ):
        if os.path.exists(f_src):
            shutil.copy2(f_src, os.path.join(DRIVE_PROJ, os.path.basename(f_src)))

if __name__ == "__main__":
    main()
