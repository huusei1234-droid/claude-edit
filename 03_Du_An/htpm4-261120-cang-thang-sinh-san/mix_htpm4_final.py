import json, math, os, re, shutil, subprocess, wave
import numpy as np

PROJ_DIR     = r"d:\AI\full studio\output\htpm4-261120"
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
FINAL_NAME   = "261120 HTPM căng thẳng kéo dài ảnh hưởng sinh sản final.mp4"
LOCAL_FINAL  = os.path.join(PROJ_DIR, FINAL_NAME)

DEST_BRAND   = rf"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\{FINAL_NAME}"
DEST_D_BACKUP= rf"D:\XUẤT CAPCUT\hằng thu pharma\{FINAL_NAME}"
DEST_MASTER  = rf"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\{FINAL_NAME}"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm4-261120-cang-thang-sinh-san"

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
    "swoosh_up":    (find_sfx("swoosh_up_a.wav"),                                                            0.00, 0.30, AIRY_EQ),
    "pop_clean":    (find_sfx("sfx_pop_clean.mp3"),                                                          0.00, 0.16, TACTILE_EQ),
    "pop_tvc":      (find_sfx("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),                                          0.02, 0.18, TACTILE_EQ),
    "pop_round":    (find_sfx("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"),                                   0.02, 0.18, TACTILE_EQ),
    "click_soft":   (find_sfx("sfx_click_soft.mp3"),                                                         0.00, 0.12, TACTILE_EQ),
    "click_picon":  (find_sfx("Click & Máy Chữ - Enter click select sound (picon)(890908) (1s).mp3"),        0.02, 0.20, TACTILE_EQ),
    "cutter_snip":  (find_sfx("Đời Thường & ASMR - Cut paper with a cutter 03(1487879) (1s).mp3"),           0.04, 0.28, TACTILE_EQ),
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
    print(f"[HTPM4 SFX] Loaded {len(bank)}/{len(SFX_SPECS)} tactile micro-SFX.", flush=True)
    return bank

def snap_to_speech(t_sec, speaking_hops, hop=480, max_shift_s=0.16):
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

    # 1. Studio-Isolated Mono-Centered Vocal via htdemucs (eliminates 100% raw embedded music/noise & fixes Left-only mic!)
    demucs_vocals = os.path.join(STEMS_DIR, "_demucs", "htdemucs", "_raw_src", "vocals.wav")
    if not os.path.exists(demucs_vocals):
        raw_in = os.path.join(STEMS_DIR, "_raw_src.wav")
        out_d  = os.path.join(STEMS_DIR, "_demucs")
        os.makedirs(out_d, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", MAIN_CUT, "-ar", "44100", "-ac", "2", raw_in], check=True)
        subprocess.run([r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe", "-m", "demucs.separate", "--two-stems", "vocals", "-n", "htdemucs", "-o", out_d, raw_in], check=True)

    # Extract clean Left handheld mic channel (c0) and center identically across Left & Right (L == R)!
    vo = decode_stereo_f32(
        demucs_vocals,
        dur_limit=vid_dur,
        af="pan=stereo|c0=c0|c1=c0,highpass=f=85,afftdn=nf=-25,equalizer=f=3100:t=q:w=1.2:g=1.4,loudnorm=I=-13.8:TP=-1.0:LRA=8"
    )
    fade_s = int(49.02 * SR)
    fade_e = min(N, int(49.26 * SR))
    if fade_e > fade_s:
        vo[fade_s:fade_e] *= np.linspace(1.0, 0.0, fade_e - fade_s, dtype=np.float32)[:, None]
        vo[fade_e:] = 0.0
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # 2. Silky 2-Half C-Major BGM (-15.8 dB smoothly tucked under clean centered Voice)
    bgm_eq = "highpass=f=75,equalizer=f=1950:t=q:w=1.30:g=-5.5,loudnorm=I=-16.0:TP=-1.5:LRA=9"
    b1 = loop_to_len(decode_stereo_f32(os.path.join(BGM_DIR, "bgm_warm_fretless.mp3"), af=bgm_eq), N)
    b2 = loop_to_len(decode_stereo_f32(os.path.join(BGM_DIR, "bgm_bright_riley.mp3"), af=bgm_eq), N)
    t_axis = np.arange(N, dtype=np.float32) / SR
    w_b2 = np.clip((t_axis - 33.0) / 1.6, 0.0, 1.0)
    bgm = b1 * (1.0 - w_b2)[:, None] + b2 * w_b2[:, None]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.018).astype(np.float32)
    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 14):min(n_hops, i_h + 24)] = 1.0
    win_sm = np.hanning(35).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), win_sm, mode="valid")[:n_hops]
    gain_hop = 0.31 * (1.0 - sp_sm) + 0.165 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)
    bgm_env *= np.clip(t_axis / 0.40, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 1.35, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    c = 0

    # ==================================================================
    # REFINED SUBTLE TACTILE MICRO-SFX (-13.2 to -14.8 dB below Voice, zero clutter!)
    # ==================================================================
    # 1. Hook (0.06 - 8.80s)
    c += stamp(sfx_bus, bank, "airy_whoosh", 0.08, -13.4)
    c += stamp(sfx_bus, bank, "pop_clean",   1.74, -13.6, pan=-0.08, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_clean",   5.50, -13.6, semitones=1.2, pan=+0.08, speaking_hops=speaking)

    # 2. Cortisol Spike (8.86 - 18.28s)
    c += stamp(sfx_bus, bank, "soft_whoosh", 8.92 - 0.11, -13.5)
    c += stamp(sfx_bus, bank, "pop_clean",   10.22, -14.0, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_clean",   13.57, -14.0, semitones=1.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_clean",   16.97, -13.8, semitones=2.4, speaking_hops=speaking)

    # 3. Full Kobe 9:16 Stage #1 (18.32 - 27.92s)
    c += stamp(sfx_bus, bank, "airy_whoosh", 18.32 - 0.11, -13.2)
    for k, bt in enumerate([21.67, 24.27, 26.04]):
        c += stamp(sfx_bus, bank, "pop_clean", bt, -13.6, semitones=k * 1.2, pan=-0.10 + k * 0.10, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "ping_glass",  26.60, -14.6, align_peak=False, speaking_hops=speaking)

    # 4. Vicious Anxiety Loop (27.96 - 33.60s)
    c += stamp(sfx_bus, bank, "soft_whoosh", 27.96 - 0.11, -13.5)
    c += stamp(sfx_bus, bank, "pop_round",   28.52, -13.8, pan=-0.08, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_round",   31.88, -13.8, semitones=1.2, pan=+0.08, speaking_hops=speaking)

    # 5. Full Kobe 9:16 Stage #2 (33.64 - 40.72s)
    c += stamp(sfx_bus, bank, "airy_whoosh", 33.64 - 0.11, -13.2)
    for k, bt in enumerate([34.82, 37.62, 39.36]):
        c += stamp(sfx_bus, bank, "click_soft", bt, -14.0, semitones=k * 1.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "idea_ting",   39.85, -14.6, align_peak=False, speaking_hops=speaking)

    # 6. Finale Foundation (40.76 - 49.26s)
    c += stamp(sfx_bus, bank, "soft_whoosh", 40.76 - 0.11, -13.5)
    c += stamp(sfx_bus, bank, "pop_clean",   44.58, -13.8, semitones=1.0, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "ping_glass",  46.68, -14.5, align_peak=False, speaking_hops=speaking)

    print(f"[HTPM4 SFX] Stamped {c} clean subtle micro-SFX cues across {vid_dur:.2f}s!", flush=True)

    sfx_bus = (np.tanh(sfx_bus * 0.95) / 0.95) * 0.80

    vo_wav  = os.path.join(STEMS_DIR, "01_Voice_Outdoor_Master.wav")
    bgm_wav = os.path.join(STEMS_DIR, "02_BGM_CMajor_2Half.wav")
    sfx_wav = os.path.join(STEMS_DIR, "03_SFX_Kobe_Tactile.wav")
    mix_wav = os.path.join(STEMS_DIR, "full_mix_pre_lufs.wav")
    save_wav_16(vo_wav, vo)
    save_wav_16(bgm_wav, bgm)
    save_wav_16(sfx_wav, sfx_bus)

    full_mix = vo + bgm + sfx_bus
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)
    save_wav_16(mix_wav, full_mix)

    pre_mov = os.path.join(PROJ_DIR, "_pre_lufs.mov")
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
        print("2-pass loudnorm:", st_j["input_i"], "-> -14.0 LUFS", flush=True)
    else:
        af_str = "loudnorm=I=-14:TP=-1:LRA=11"

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_mov,
        "-c:v", "copy", "-af", af_str, "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
        LOCAL_FINAL
    ], check=True)
    if os.path.exists(pre_mov):
        os.remove(pre_mov)
    print("Saved Local Final:", LOCAL_FINAL, flush=True)

    # Build 20-frame Contact Sheet
    shutil.copy2(
        r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\Montserrat-Bold.ttf",
        os.path.join(CHECK_DIR, "_f.ttf")
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", LOCAL_FINAL,
        "-vf", "fps=20/49.3,scale=270:480,drawtext=fontfile=_f.ttf:text='%{pts\\:hms}':fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.65:x=8:y=8,tile=5x4",
        "-frames:v", "1", os.path.join(CHECK_DIR, "htpm4_final_sheet.jpg")
    ], cwd=CHECK_DIR, check=True)

    # Deliver to ALL mandatory official destinations (Zero CapCut Draft!)
    for dst in (DEST_BRAND, DEST_D_BACKUP, DEST_MASTER):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(LOCAL_FINAL, dst)
        print("DELIVERED ->", dst, flush=True)

    # Sync full project archive to 03_Du_An
    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for fn in ("clean_htpm4_transcript.py", "gen_htpm4_flow_videos.py", "render_htpm4_master.py", "mix_htpm4_final.py", "report.md"):
        fp = os.path.join(PROJ_DIR, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    shutil.copy2(os.path.join(PROJ_DIR, "hf_kobe_stage", "index.html"), os.path.join(DRIVE_PROJ, "kobe_stage_index.html"))
    for fn, sdir in (("main_cut_clean.json", AROLL_DIR), ("htpm4_final_sheet.jpg", CHECK_DIR), ("flow_htpm4_qc.jpg", CHECK_DIR), ("htpm4_kobe_test_grid.jpg", CHECK_DIR)):
        fp = os.path.join(sdir, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    print("SYNCED PROJECT ARCHIVE ->", DRIVE_PROJ, flush=True)

if __name__ == "__main__":
    main()
