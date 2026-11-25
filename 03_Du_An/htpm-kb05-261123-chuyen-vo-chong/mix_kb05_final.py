import json, math, os, re, shutil, subprocess, sys, wave
import numpy as np

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
import final_delivery as fd

PROJ_DIR     = r"C:\AI\full studio\output\htpm-kb05-261123"
AROLL_DIR    = os.path.join(PROJ_DIR, "aroll")
STEMS_DIR    = os.path.join(PROJ_DIR, "audio_stems")
os.makedirs(STEMS_DIR, exist_ok=True)

TLH_SFX_DIR  = r"G:\Other computers\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
SAAS_SFX_DIR = r"C:\AI\full studio\phong-cach\saas-animation\audio\sfx"
STUDIO_SFX_D = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"

RAW_VID      = os.path.join(PROJ_DIR, "_master_video_only.mp4")
VOICE_WAV    = os.path.join(STEMS_DIR, "clean_voice_48k.wav")
FINAL_NAME   = "261123 HTPM đừng để chuyện vợ chồng thành áp lực final.mp4"
LOCAL_FINAL  = os.path.join(PROJ_DIR, FINAL_NAME)
DEST_ARTIFACT= r"C:\Users\001\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\HTPM_261123_DUNG_DE_CHUYEN_VO_CHONG_THANH_AP_LUC_FINAL.mp4"
DRIVE_PROJ   = r"G:\My Drive\AI_Full_Studio\03_Du_An\htpm-kb05-261123-chuyen-vo-chong"

SR = 48000

def build_sfx_index():
    idx = {}
    for base in (STUDIO_SFX_D, SAAS_SFX_DIR, TLH_SFX_DIR):
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
RISER_EQ   = "highpass=f=120,equalizer=f=2800:t=q:w=1.10:g=-2.5,lowpass=f=12500"

SFX_SPECS = {
    "hook_riser":   (find_sfx("Riser - Âm thanh dồn lên chuyển cảnh 01.mp3"),                                1.65, 3.10, RISER_EQ),
    "shimmer_rise": (find_sfx("SFX - Metallic Reverse Rise (1s).mp3"),                                       0.55, 1.80, RISER_EQ),
    "airy_whoosh":  (find_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),                                  0.06, 0.34, AIRY_EQ),
    "soft_whoosh":  (find_sfx("sfx_whoosh_soft.mp3"),                                                        0.02, 0.32, AIRY_EQ),
    "swoosh_up":    (find_sfx("swoosh_up_a.wav"),                                                            0.00, 0.30, AIRY_EQ),
    "pop_clean":    (find_sfx("sfx_pop_clean.mp3"),                                                          0.00, 0.16, TACTILE_EQ),
    "pop_tvc":      (find_sfx("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),                                          0.02, 0.18, TACTILE_EQ),
    "pop_round":    (find_sfx("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"),                                   0.02, 0.18, TACTILE_EQ),
    "click_soft":   (find_sfx("sfx_click_soft.mp3"),                                                         0.00, 0.12, TACTILE_EQ),
    "click_picon":  (find_sfx("Click & Máy Chữ - Enter click select sound (picon)(890908) (1s).mp3"),        0.02, 0.20, TACTILE_EQ),
    "card_deal":    (find_sfx("Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3"), 0.02, 0.42, TACTILE_EQ),
    "ping_glass":   (find_sfx("sfx_ping_glass.mp3"),                                                         0.00, 0.52, TACTILE_EQ),
    "chime_warm":   (find_sfx("sfx_chime_warm.mp3"),                                                         0.00, 0.60, TACTILE_EQ),
    "notif_cta":    (find_sfx("sfx_notification_cta.mp3"),                                                   0.00, 0.48, TACTILE_EQ),
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

def loop_to_len(arr, n):
    if len(arr) >= n:
        return arr[:n].copy()
    reps = (n + len(arr) - 1) // len(arr)
    return np.tile(arr, (reps, 1))[:n].copy()

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
        is_riser = key in ("hook_riser", "shimmer_rise")
        n_in  = int(0.18 * SR) if is_riser else min(len(arr) // 5, int(0.008 * SR))
        n_out = int(0.035 * SR) if is_riser else min(len(arr) // 3, int(0.045 * SR))
        if n_in > 2 and n_in < len(arr):
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2 and n_out < len(arr):
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
    print(f"[KB05 SFX] Loaded {len(bank)}/{len(SFX_SPECS)} SFX cues.", flush=True)
    return bank

def snap_to_speech(t_sec, speaking_hops, hop=480, max_shift_s=0.14):
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

def main():
    dur_j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. Studio Voice Polish (removes outdoor wind rumble <145Hz + warm clarity EQ + gentle compression)
    vo_af = "highpass=f=145:poles=2,equalizer=f=260:t=q:w=1.1:g=1.8,equalizer=f=3200:t=q:w=1.2:g=2.2,acompressor=threshold=-19dB:ratio=2.6:attack=8:release=90"
    vo = decode_stereo_f32(VOICE_WAV, dur_limit=vid_dur, af=vo_af)
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.018).astype(np.float32)

    sp_samples = np.repeat(speaking > 0.5, hop)[:N]
    cur_sp_rms = float(np.sqrt(np.mean(vo[sp_samples] ** 2))) if np.any(sp_samples) else float(np.sqrt(np.mean(vo ** 2)))
    if cur_sp_rms > 1e-4:
        vo *= (0.168 / cur_sp_rms)

    # 2. Gentle Warm 2-Half C-Major BGM (since KB05 is raw camera audio with 0 baked-in BGM!):
    #    -16.5 dB below voice during speech (~0.025 RMS) with EQ Voice Pocket & sidechain ducking!
    bgm_eq = "highpass=f=80,equalizer=f=1850:t=q:w=1.25:g=-5.0,lowpass=f=11000"
    bgm1 = loop_to_len(decode_stereo_f32(os.path.join(STUDIO_SFX_D, "bgm_warm_fretless.mp3"), af=bgm_eq), N)
    bgm2 = loop_to_len(decode_stereo_f32(os.path.join(STUDIO_SFX_D, "bgm_bright_riley.mp3"),  af=bgm_eq), N)
    for b_arr in (bgm1, bgm2):
        br = float(np.sqrt(np.mean(b_arr ** 2)))
        if br > 1e-5:
            b_arr *= (0.10 / br)

    # Smooth 1.8s emotional crossfade at 36.85s ("Hằng muốn chị em hiểu...")
    t_axis = np.arange(N, dtype=np.float32) / SR
    xfade = np.clip((t_axis - 36.0) / 1.8, 0.0, 1.0)[:, None]
    bgm_raw = bgm1 * (1.0 - xfade) + bgm2 * xfade

    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 10):min(n_hops, i_h + 18)] = 1.0
    win_sm = np.hanning(35).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), win_sm, mode="valid")[:n_hops]

    # Soft & non-intrusive: 0.21x (-17.2 dB under voice) while speaking, 0.34x in brief pauses!
    bgm_gain_hop = 0.34 * (1.0 - sp_sm) + 0.21 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, bgm_gain_hop)[:, None]
    end_fade = np.clip((vid_dur - t_axis) / 0.65, 0.0, 1.0)[:, None]
    bgm = bgm_raw * bgm_env * end_fade

    # 3. Hook Zoom-In + Exact 12.24s SFX Riser + Kobe Tactile Micro-SFX
    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    c = 0

    # Hook & Silent Distance (0.06 - 12.24s)
    c += stamp(sfx_bus, bank, "airy_whoosh", 0.08, -10.8)
    c += stamp(sfx_bus, bank, "pop_clean",   0.20, -11.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "swoosh_up",   2.53, -10.4)  # Post-Hook Zoom-In!
    c += stamp(sfx_bus, bank, "pop_tvc",     3.38, -11.6, pan=-0.16, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "click_soft",  5.14, -12.0, pan=0.16, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "soft_whoosh", 6.93, -11.0)
    c += stamp(sfx_bus, bank, "notif_cta",   9.72, -12.4, align_peak=False, speaking_hops=speaking)

    # *** EXACT 12.24s SFX RISER CLIMAX -> RETURN TO 1.00x NORMAL FRAME ***
    c += stamp(sfx_bus, bank, "hook_riser",   12.24, -7.8, align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "shimmer_rise", 12.24, -10.4, align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "airy_whoosh",  12.25, -9.8,  align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "pop_round",    12.40, -11.4, speaking_hops=speaking)

    # Full Kobe Stage #1 (16.48 - 26.38s): 4 Drop-Bounce Symptom Cards
    c += stamp(sfx_bus, bank, "airy_whoosh", 16.48 - 0.10, -10.6)
    for k, bt in enumerate([16.94, 18.80, 20.62, 22.92]):
        c += stamp(sfx_bus, bank, "pop_clean",   bt, -11.2, semitones=k * 1.2, pan=-0.24 + k * 0.16, speaking_hops=speaking)
        if k > 0:
            c += stamp(sfx_bus, bank, "click_picon", bt + 0.08, -12.6, semitones=k * 1.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "soft_whoosh", 26.36 - 0.10, -10.8)

    # Silence Trap & Mutual Hurt (26.42 - 36.82s)
    c += stamp(sfx_bus, bank, "pop_tvc",     26.68, -11.4, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "airy_whoosh", 29.76 - 0.10, -10.8)
    c += stamp(sfx_bus, bank, "click_soft",  30.00, -12.0, pan=-0.18, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "click_soft",  32.06, -12.0, pan=0.18, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "ping_glass",  34.62, -12.6, align_peak=False, speaking_hops=speaking)

    # Healthy Mindset & 3 Don'ts (36.86 - 49.58s)
    c += stamp(sfx_bus, bank, "soft_whoosh", 36.90 - 0.08, -11.0)
    c += stamp(sfx_bus, bank, "chime_warm",  38.48, -12.6, align_peak=False, speaking_hops=speaking)
    for k, bt in enumerate([44.86, 46.00, 47.48]):
        c += stamp(sfx_bus, bank, "pop_tvc", bt, -11.6, semitones=k * 1.4, speaking_hops=speaking)

    # Full Kobe Stage #2 (49.60 - 62.60s): 3 Closeness Steps
    c += stamp(sfx_bus, bank, "airy_whoosh", 49.60 - 0.10, -10.6)
    for k, bt in enumerate([49.95, 51.55, 55.75]):
        c += stamp(sfx_bus, bank, "pop_clean", bt, -11.2, semitones=k * 1.5, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "chime_warm",  58.58, -12.6, align_peak=False, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "soft_whoosh", 62.58 - 0.10, -10.8)

    # Series CTA Finale (62.64 - 69.98s)
    c += stamp(sfx_bus, bank, "card_deal",   62.82, -11.4, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_round",   63.50, -11.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "click_picon", 68.15, -11.6, semitones=1.8, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "chime_warm",  68.25, -12.4, align_peak=False, speaking_hops=speaking)

    print(f"[KB05 SFX] Placed {c} cues (Voice Polish + -17dB Warm BGM + Exact 12.24s Riser + Tactile SFX).", flush=True)

    raw_mix = vo * end_fade + bgm + sfx_bus
    mix_wav  = os.path.join(STEMS_DIR, "mix_pre_loudnorm.wav")
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

    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", RAW_VID, "-i", norm_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
        LOCAL_FINAL
    ], check=True)

    # Deliver via upgraded multi-PC final_delivery.py (G:\Other computers\...\K6 - Hằng Thu Pharma + Master Cloud + Local Backup!)
    res_deliv = fd.deliver_final_video(
        LOCAL_FINAL,
        brand_key="htpm",
        vietnamese_title="đừng để chuyện vợ chồng thành áp lực",
        date_yymmdd="261123",
        is_horizontal=False,
    )
    print("[KB05 DELIVERED]", json.dumps(res_deliv, ensure_ascii=False), flush=True)

    os.makedirs(os.path.dirname(DEST_ARTIFACT), exist_ok=True)
    shutil.copy2(LOCAL_FINAL, DEST_ARTIFACT)

    try:
        os.makedirs(DRIVE_PROJ, exist_ok=True)
        for fn_s in ("build_kb05_cinema_brolls.py", "render_kb05_master.py", "mix_kb05_final.py"):
            sp = os.path.join(PROJ_DIR, fn_s)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(DRIVE_PROJ, fn_s))
        shutil.copy2(os.path.join(AROLL_DIR, "main_cut_clean.json"), os.path.join(DRIVE_PROJ, "main_cut_clean.json"))
    except Exception as e:
        print("[KB05 Drive Sync Warning]", e, flush=True)

if __name__ == "__main__":
    main()
