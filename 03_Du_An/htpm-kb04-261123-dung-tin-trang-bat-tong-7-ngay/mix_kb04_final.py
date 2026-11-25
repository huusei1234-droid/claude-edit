import json, math, os, re, shutil, subprocess, wave
import numpy as np
from PIL import Image

PROJ_DIR     = r"C:\AI\full studio\output\htpm-kb04-261123"
AROLL_DIR    = os.path.join(PROJ_DIR, "aroll")
STEMS_DIR    = os.path.join(PROJ_DIR, "audio_stems")
CHECK_DIR    = os.path.join(PROJ_DIR, "check")
os.makedirs(STEMS_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

TLH_SFX_DIR  = r"G:\Other computers\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
SAAS_SFX_DIR = r"C:\AI\full studio\phong-cach\saas-animation\audio\sfx"
STUDIO_SFX_D = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"

RAW_VID      = os.path.join(PROJ_DIR, "_master_video_only.mp4")
FINAL_NAME   = "261123 HTPM đừng tin trắng bật tông sau 7 ngày final.mp4"
LOCAL_FINAL  = os.path.join(PROJ_DIR, FINAL_NAME)

DEST_BRAND   = rf"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\{FINAL_NAME}"
DEST_MASTER  = rf"G:\My Drive\AI_Full_Studio\04_Videos_Final\{FINAL_NAME}"
DEST_LOCAL_B = rf"C:\AI\XUAT_CAPCUT\hằng thu pharma\{FINAL_NAME}"
DRIVE_PROJ   = r"G:\My Drive\AI_Full_Studio\03_Du_An\htpm-kb04-261123-dung-tin-trang-bat-tong-7-ngay"

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
RISER_EQ   = "highpass=f=120,equalizer=f=2800:t=q:w=1.10:g=-2.5,lowpass=f=12500"
BGM_EQ     = "highpass=f=75,equalizer=f=1750:t=q:w=1.25:g=-4.5,lowpass=f=11500"

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
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
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
    print(f"[KB04 SFX] Loaded {len(bank)}/{len(SFX_SPECS)} Studio SFX cues.", flush=True)
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

def build_two_half_cmajor_bgm(N, vid_dur, sp_sm, hop):
    """
    Verified Demucs no_vocals RMS = -59.15 dBFS -> 100% pure mic with zero pre-baked BGM!
    Build 2-half C-Major BGM (bgm_warm_fretless -> 1.6s crossfade @ 40.38s -> bgm_bright_riley)
    with EQ Voice Pocket + Dynamic Sidechain Ducking (-14.8 dB below Voice during speech)!
    """
    bgm1_p = os.path.join(STUDIO_SFX_D, "bgm_warm_fretless.mp3")
    bgm2_p = os.path.join(STUDIO_SFX_D, "bgm_bright_riley.mp3")
    if not (os.path.exists(bgm1_p) and os.path.exists(bgm2_p)):
        return np.zeros((N, 2), dtype=np.float32)

    a1 = decode_stereo_f32(bgm1_p, af=BGM_EQ)
    a2 = decode_stereo_f32(bgm2_p, af=BGM_EQ)
    while len(a1) < N:
        a1 = np.vstack([a1, a1])
    while len(a2) < N:
        a2 = np.vstack([a2, a2])
    a1, a2 = a1[:N], a2[:N]

    for arr in (a1, a2):
        r = float(np.sqrt(np.mean(arr ** 2)))
        if r > 1e-5:
            arr *= (0.165 / r)

    t_ax = np.arange(N, dtype=np.float32) / SR
    xf_u = np.clip((t_ax - 39.60) / 1.60, 0.0, 1.0)[:, None]
    bgm = a1 * np.cos(xf_u * math.pi * 0.5) + a2 * np.sin(xf_u * math.pi * 0.5)

    duck_hop = 0.251 * (1.0 - sp_sm) + 0.182 * sp_sm
    duck_env = np.interp(np.arange(N, dtype=np.float32), np.arange(len(sp_sm), dtype=np.float32) * hop, duck_hop)[:, None]
    fade_in  = np.clip(t_ax / 0.35, 0.0, 1.0)[:, None]
    fade_out = np.clip((vid_dur - t_ax) / 0.85, 0.0, 1.0)[:, None]
    return bgm * duck_env * fade_in * fade_out

def build_final_qc_sheet(vid_path, out_jpg):
    cols, rows = 5, 4
    tw, th = 216, 384
    sheet = Image.new("RGB", (cols * tw, rows * th))
    for idx in range(cols * rows):
        ts = 0.80 + idx * (71.5 / (cols * rows - 1))
        raw = subprocess.check_output([
            "ffmpeg", "-v", "error", "-ss", f"{ts:.3f}", "-i", vid_path,
            "-frames:v", "1", "-vf", f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ])
        im = Image.fromarray(np.frombuffer(raw[:tw * th * 3], dtype=np.uint8).reshape((th, tw, 3)), "RGB")
        sheet.paste(im, ((idx % cols) * tw, (idx // cols) * th))
    sheet.save(out_jpg, quality=92)
    print(f"[KB04 QC] Saved 20-panel final sheet -> {out_jpg}", flush=True)

def main():
    dur_j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    voc_wav = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "vocals.wav")
    voc = decode_stereo_f32(voc_wav, dur_limit=vid_dur, af="highpass=f=65")
    voc = np.vstack([voc, np.zeros((max(0, N - len(voc)), 2), dtype=np.float32)])[:N]

    hop = 480
    n_hops = (N + hop - 1) // hop
    voc_pad = np.vstack([voc, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(voc_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.018).astype(np.float32)

    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 12):min(n_hops, i_h + 20)] = 1.0
    win_sm = np.hanning(35).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), win_sm, mode="valid")[:n_hops]

    t_axis = np.arange(N, dtype=np.float32) / SR
    vo = voc * np.clip((vid_dur - t_axis) / 0.50, 0.0, 1.0)[:, None]
    sp_samples = np.repeat(speaking > 0.5, hop)[:N]
    cur_sp_rms = float(np.sqrt(np.mean(vo[sp_samples] ** 2))) if np.any(sp_samples) else float(np.sqrt(np.mean(vo ** 2)))
    if cur_sp_rms > 1e-4:
        vo *= (0.165 / cur_sp_rms)

    bgm_bus = build_two_half_cmajor_bgm(N, vid_dur, sp_sm, hop)
    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    c = 0

    # 1. Hook & Ad Alert (0.06 - 11.80s)
    c += stamp(sfx_bus, bank, "airy_whoosh", 0.08, -10.8)
    c += stamp(sfx_bus, bank, "pop_clean",   0.20, -11.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "swoosh_up",   2.86, -10.4)
    c += stamp(sfx_bus, bank, "soft_whoosh", 3.00, -11.2)
    c += stamp(sfx_bus, bank, "pop_tvc",     4.84, -11.4, pan=-0.18, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "notif_subtle",8.48, -12.0, align_peak=False, speaking_hops=speaking)

    # *** POST-HOOK SFX RISER CLIMAX AT EXACT t = 11.80s! ***
    c += stamp(sfx_bus, bank, "hook_riser",   11.80, -7.8, align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "shimmer_rise", 11.80, -10.2, align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "airy_whoosh",  11.81, -9.8,  align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "pop_round",    11.98, -11.4, speaking_hops=speaking)

    # 2. Natural Desire vs Hype Trap (11.84 - 26.86s)
    c += stamp(sfx_bus, bank, "click_soft",  14.64, -12.2, pan=0.16, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "cutter_snip", 20.84, -11.4, pan=0.18, speaking_hops=speaking)

    # 3. Full Kobe 9:16 Stage #1 (26.90 - 40.34s): 4 Drop-Bounce Ripple Cards!
    c += stamp(sfx_bus, bank, "airy_whoosh", 26.90 - 0.10, -10.6)
    for k, bt in enumerate([27.37, 28.92, 30.67, 32.12]):
        c += stamp(sfx_bus, bank, "pop_clean",   bt, -11.2, semitones=k * 1.1, pan=-0.24 + k * 0.16, speaking_hops=speaking)
        if k > 0:
            c += stamp(sfx_bus, bank, "click_picon", bt + 0.08, -12.6, semitones=k * 1.1, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "idea_ting",   34.18, -12.4, align_peak=False, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "soft_whoosh", 40.32 - 0.10, -10.8)

    # 4. Seven Real Skin Factors (40.38 - 47.14s): 7 Escalating Tactile Clicks!
    for k, bt in enumerate([40.60, 41.54, 42.46, 43.48, 44.48, 45.04, 46.24]):
        c += stamp(sfx_bus, bank, "click_soft", bt, -11.8, semitones=k * 0.9, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "ping_glass",  46.30, -12.6, align_peak=False, speaking_hops=speaking)

    # 5. Legend White Skin Brand Honesty Showcase (47.18 - 55.26s)
    c += stamp(sfx_bus, bank, "airy_whoosh", 47.18 - 0.10, -10.8)
    c += stamp(sfx_bus, bank, "pop_round",   47.58, -11.4, pan=-0.20, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_tvc",     50.28, -11.4, pan=0.18, speaking_hops=speaking)

    # 6. Full Kobe 9:16 Stage #2 (55.30 - 64.84s): 3 Smart Rules + Never Trade Health!
    c += stamp(sfx_bus, bank, "airy_whoosh", 55.30 - 0.10, -10.6)
    c += stamp(sfx_bus, bank, "pop_clean",   55.94, -11.4, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_clean",   58.68, -11.4, semitones=1.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "click_picon", 62.14, -11.6, semitones=2.0, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "ping_glass",  62.24, -12.4, align_peak=False, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "soft_whoosh", 64.82 - 0.10, -10.8)

    # 7. Official Facebook CTA + Comment "NÓI THẬT" (64.88 - 73.42s)
    c += stamp(sfx_bus, bank, "card_deal",   65.12, -11.4, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "click_picon", 68.72, -11.4, semitones=1.5, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_round",   71.28, -11.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "idea_ting",   71.40, -12.2, align_peak=False, speaking_hops=speaking)

    print(f"[KB04 SFX] Placed {c} cues + 2-Half C-Major BGM + Exact 11.80s Hook Riser.", flush=True)

    raw_mix = vo + bgm_bus + sfx_bus
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

    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", RAW_VID, "-i", norm_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
        LOCAL_FINAL
    ], check=True)

    build_final_qc_sheet(LOCAL_FINAL, os.path.join(CHECK_DIR, "kb04_final_sheet.jpg"))

    for dst in (DEST_BRAND, DEST_MASTER, DEST_LOCAL_B):
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(LOCAL_FINAL, dst)
            print("[KB04] Exported ->", dst, flush=True)
        except Exception as e:
            print("[KB04] Copy warning:", dst, e, flush=True)

    try:
        os.makedirs(DRIVE_PROJ, exist_ok=True)
        for fn_s in (
            "prep_kb04.py",
            "clean_kb04_transcript.py",
            "gen_kb04_direct_drivers.js",
            "render_kb04_master.py",
            "mix_kb04_final.py",
            "report.md",
        ):
            sp = os.path.join(PROJ_DIR, fn_s)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(DRIVE_PROJ, fn_s))
        shutil.copy2(os.path.join(AROLL_DIR, "main_cut_clean.json"), os.path.join(DRIVE_PROJ, "main_cut_clean.json"))
        shutil.copy2(os.path.join(PROJ_DIR, "hf_kobe_stage", "index.html"), os.path.join(DRIVE_PROJ, "hf_kobe_stage_index.html"))
        for qf in ("raw_sheet.jpg", "kb04_test_grid.jpg", "kb04_final_sheet.jpg"):
            qp = os.path.join(CHECK_DIR, qf)
            if os.path.exists(qp):
                shutil.copy2(qp, os.path.join(DRIVE_PROJ, qf))
    except Exception as e:
        print("[KB04] Drive project sync warning:", e, flush=True)

if __name__ == "__main__":
    main()
