import json, math, os, re, shutil, subprocess, wave
import numpy as np
from PIL import Image

PROJ_DIR     = r"d:\AI\full studio\output\htpm6-261121"
AROLL_DIR    = os.path.join(PROJ_DIR, "aroll")
STEMS_DIR    = os.path.join(PROJ_DIR, "audio_stems")
CHECK_DIR    = os.path.join(PROJ_DIR, "check")
os.makedirs(STEMS_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

TLH_SFX_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
SAAS_SFX_DIR = r"d:\AI\full studio\phong-cach\saas-animation\audio\sfx"
STUDIO_SFX_D = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"

RAW_VID      = os.path.join(PROJ_DIR, "_master_video_only.mp4")
FINAL_NAME   = "261121 HTPM 40 tuổi đầu tư gì lời nhất final.mp4"
LOCAL_FINAL  = os.path.join(PROJ_DIR, FINAL_NAME)

DEST_BRAND   = rf"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\{FINAL_NAME}"
DEST_D_BACKUP= rf"D:\XUẤT CAPCUT\hằng thu pharma\{FINAL_NAME}"
DEST_MASTER  = rf"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\{FINAL_NAME}"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm6-261121-40-tuoi-dau-tu"

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
    print(f"[HTPM6 SFX] Loaded {len(bank)}/{len(SFX_SPECS)} SFX cues (including Hook Riser).", flush=True)
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

def build_final_qc_sheet(vid_path, out_jpg):
    cols, rows = 5, 4
    tw, th = 216, 384
    sheet = Image.new("RGB", (cols * tw, rows * th))
    for idx in range(cols * rows):
        ts = 0.85 + idx * (66.6 / (cols * rows - 1))
        raw = subprocess.check_output([
            "ffmpeg", "-v", "error", "-ss", f"{ts:.3f}", "-i", vid_path,
            "-frames:v", "1", "-vf", f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ])
        im = Image.fromarray(np.frombuffer(raw[:tw * th * 3], dtype=np.uint8).reshape((th, tw, 3)), "RGB")
        sheet.paste(im, ((idx % cols) * tw, (idx // cols) * th))
    sheet.save(out_jpg, quality=92)
    print(f"[HTPM6 QC] Saved 20-panel final sheet -> {out_jpg}", flush=True)

def main():
    dur_j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. AI Stem Rebalance (Demucs htdemucs):
    # Preserve 100% centered original voice clarity while lowering baked-in BGM (-7.1 dB during speech / -4.7 dB in pauses) — NO competing BGM!
    demucs_dir = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input")
    voc_wav = os.path.join(demucs_dir, "vocals.wav")
    bgm_wav = os.path.join(demucs_dir, "no_vocals.wav")

    voc = decode_stereo_f32(voc_wav, dur_limit=vid_dur, af="highpass=f=65")
    acc = decode_stereo_f32(bgm_wav, dur_limit=vid_dur)
    voc = np.vstack([voc, np.zeros((max(0, N - len(voc)), 2), dtype=np.float32)])[:N]
    acc = np.vstack([acc, np.zeros((max(0, N - len(acc)), 2), dtype=np.float32)])[:N]

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

    acc_gain_hop = 0.58 * (1.0 - sp_sm) + 0.44 * sp_sm
    acc_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, acc_gain_hop).astype(np.float32)
    t_axis = np.arange(N, dtype=np.float32) / SR
    end_fade = np.clip((vid_dur - t_axis) / 0.55, 0.0, 1.0)[:, None]
    vo = (voc + acc * acc_env[:, None]) * end_fade
    sp_samples = np.repeat(speaking > 0.5, hop)[:N]
    cur_sp_rms = float(np.sqrt(np.mean(vo[sp_samples] ** 2))) if np.any(sp_samples) else float(np.sqrt(np.mean(vo ** 2)))
    if cur_sp_rms > 1e-4:
        vo *= (0.165 / cur_sp_rms)

    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    c = 0

    # ==================================================================
    # 2. HOOK ZOOM-IN + EXACT 8.55s SFX RISER + KOBE TACTILE MICRO-SFX
    # ==================================================================
    # 1. Hook Question & 100M Choice (0.06 - 8.55s)
    c += stamp(sfx_bus, bank, "airy_whoosh", 0.08, -10.8)
    c += stamp(sfx_bus, bank, "pop_clean",   0.20, -11.2, speaking_hops=speaking)
    # Post-Hook Zoom-In right after "lời nhất?" at 2.68s -> 2.86s
    c += stamp(sfx_bus, bank, "swoosh_up",   2.74, -10.4)
    c += stamp(sfx_bus, bank, "soft_whoosh", 2.84, -11.2)
    c += stamp(sfx_bus, bank, "pop_tvc",     3.84, -11.4, pan=-0.18, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "notif_subtle",7.24, -12.0, align_peak=False, speaking_hops=speaking)

    # *** POST-HOOK SFX RISER CLIMAX AT EXACT t = 8.55s -> Cut to Cam B 1.00x Normal Frame! ***
    c += stamp(sfx_bus, bank, "hook_riser",   8.55, -7.8, align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "shimmer_rise", 8.55, -10.2, align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "airy_whoosh",  8.56, -9.8,  align_peak=True, speaking_hops=None)
    c += stamp(sfx_bus, bank, "pop_round",    8.72, -11.4, speaking_hops=speaking)

    # 2. Post-Riser Truth on Cam B -> Cam A (8.58 - 16.08s)
    c += stamp(sfx_bus, bank, "click_soft",   9.14, -12.2, pan=-0.16, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_clean",   13.84, -11.4, pan=0.16, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "idea_ting",   13.96, -12.8, align_peak=False, speaking_hops=speaking)

    # 3. Full Kobe 9:16 Stage #1 (16.12 - 26.36s): 3 Drop-Bounce Ripple Cards + Multi-Cam PiP!
    c += stamp(sfx_bus, bank, "airy_whoosh", 16.12 - 0.10, -10.6)
    for k, bt in enumerate([16.65, 19.45, 22.95]):
        c += stamp(sfx_bus, bank, "pop_clean",   bt, -11.2, semitones=k * 1.2, pan=-0.22 + k * 0.22, speaking_hops=speaking)
        if k > 0:
            c += stamp(sfx_bus, bank, "click_picon", bt + 0.08, -12.6, semitones=k * 1.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "soft_whoosh", 26.34 - 0.10, -10.8)

    # 4. Six Core Investments (26.40 - 35.58s): 6 Ascending Checklist Items!
    c += stamp(sfx_bus, bank, "pop_tvc",     26.58, -11.4, speaking_hops=speaking)
    for k, bt in enumerate([29.48, 30.88, 31.85, 32.80, 33.78, 35.08]):
        c += stamp(sfx_bus, bank, "click_soft", bt, -11.8, semitones=k * 1.0, pan=0.18, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "idea_ting",   35.14, -12.6, align_peak=False, speaking_hops=speaking)

    # 5. Three Compounding Benefits (35.60 - 45.54s): Energy, Work, Smart Choices!
    c += stamp(sfx_bus, bank, "airy_whoosh", 35.60 - 0.10, -10.8)
    for k, bt in enumerate([36.45, 39.40, 42.10]):
        c += stamp(sfx_bus, bank, "pop_tvc", bt, -11.4, semitones=k * 1.3, pan=-0.20 + k * 0.20, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "cutter_snip", 42.18, -11.4, speaking_hops=speaking)

    # 6. Full Kobe 9:16 Stage #2 (45.58 - 56.68s): Love Your Body Early + PiP!
    c += stamp(sfx_bus, bank, "airy_whoosh", 45.58 - 0.10, -10.6)
    c += stamp(sfx_bus, bank, "pop_clean",   46.84, -11.2, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "click_picon", 51.24, -11.8, semitones=1.5, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "ping_glass",  51.36, -12.6, align_peak=False, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "soft_whoosh", 56.66 - 0.10, -10.8)

    # 7. Finale CTA (56.72 - 68.76s): Age 30-40+ Follow Hằng!
    c += stamp(sfx_bus, bank, "card_deal",   56.92, -11.4, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "pop_round",   57.64, -11.8, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "click_picon", 63.84, -11.8, semitones=1.8, speaking_hops=speaking)
    c += stamp(sfx_bus, bank, "idea_ting",   63.96, -12.4, align_peak=False, speaking_hops=speaking)

    print(f"[HTPM6 SFX] Placed {c} cues (Demucs -7.1dB BGM + Exact 8.55s Hook Riser + Tactile Micro-SFX).", flush=True)

    raw_mix = vo + sfx_bus
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

    build_final_qc_sheet(LOCAL_FINAL, os.path.join(CHECK_DIR, "htpm6_final_sheet.jpg"))

    for dst in (DEST_BRAND, DEST_D_BACKUP, DEST_MASTER):
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(LOCAL_FINAL, dst)
            print("[HTPM6] Exported ->", dst, flush=True)
        except Exception as e:
            print("[HTPM6] Copy warning:", dst, e, flush=True)

    try:
        os.makedirs(DRIVE_PROJ, exist_ok=True)
        for fn_s in (
            "prep_htpm6.py",
            "conform_cam_b.py",
            "clean_htpm6_transcript.py",
            "gen_htpm6_flow_videos.py",
            "render_htpm6_master.py",
            "mix_htpm6_final.py",
            "report.md",
        ):
            sp = os.path.join(PROJ_DIR, fn_s)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(DRIVE_PROJ, fn_s))
        shutil.copy2(os.path.join(AROLL_DIR, "main_cut_clean.json"), os.path.join(DRIVE_PROJ, "main_cut_clean.json"))
        shutil.copy2(
            os.path.join(PROJ_DIR, "hf_kobe_stage", "index.html"),
            os.path.join(DRIVE_PROJ, "hf_kobe_stage_index.html"),
        )
        for qf in ("multicam_sync_sheet.jpg", "flow_htpm6_all11_qc.jpg", "htpm6_final_sheet.jpg"):
            qp = os.path.join(CHECK_DIR, qf)
            if os.path.exists(qp):
                shutil.copy2(qp, os.path.join(DRIVE_PROJ, qf))
    except Exception as e:
        print("[HTPM6] Drive project sync warning:", e, flush=True)

if __name__ == "__main__":
    main()
