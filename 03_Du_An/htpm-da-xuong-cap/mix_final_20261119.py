import json, math, os, re, shutil, subprocess, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\htpm-20261119"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
os.makedirs(STEMS_DIR, exist_ok=True)

TLH_SFX_DIR   = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
BGM_DIR       = r"d:\AI\full studio\phong-cach\talking-head\assets_dung_chung\bgm"
STUDIO_SFX_D  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"

RAW_VID      = os.path.join(PROJ_DIR, "_master_video_only.mp4")
MAIN_CUT     = os.path.join(AROLL_DIR, "main_cut.mp4")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "htpm_da_xuong_cap_final.mp4")
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\HTPM_DA_XUONG_CAP_FINAL.mp4"
DRIVE_FINAL  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_DA_XUONG_CAP_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-da-xuong-cap"
ARTIFACT_MP4 = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\HTPM_DA_XUONG_CAP_FINAL.mp4"

SR = 48000

def build_sfx_index():
    idx = {}
    for base in (TLH_SFX_DIR, STUDIO_SFX_D):
        if os.path.exists(base):
            for r, _, files in os.walk(base):
                for fn in files:
                    idx[fn] = os.path.join(r, fn)
    return idx

SFX_IDX = build_sfx_index()
def find_sfx(fname):
    return SFX_IDX.get(fname, os.path.join(STUDIO_SFX_D, fname))

VO_POCKET_EQ = "equalizer=f=2650:t=q:w=1.15:g=-4.5,lowpass=f=9200"

SFX_SPECS = {
    "whoosh_tvc":   (find_sfx("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"),                               0.06, 0.52, VO_POCKET_EQ),
    "whoosh_scene": (find_sfx("Whoosh - Lướt chuyển cảnh cơ bản.mp3"),                                    0.20, 0.60, VO_POCKET_EQ),
    "swoosh_light": (find_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),                               0.08, 0.39, VO_POCKET_EQ),
    "whoosh_pip":   (find_sfx("Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP).mp3"),                     0.04, 0.28, VO_POCKET_EQ),
    "card_swipe":   (find_sfx("Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3"), 0.04, 0.52, VO_POCKET_EQ),
    "card_slide":   (find_sfx("Slide - Tiếng trượt chữ ngang mượt.mp3"),                                  0.04, 0.54, "lowpass=f=6800"),
    "pop_soft":     (find_sfx("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),                                       0.03, 0.27, VO_POCKET_EQ),
    "notif_subtle": (find_sfx("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"),                  0.10, 0.42, VO_POCKET_EQ),
    "ting_clean":   (find_sfx("Ting - Chuông Ting nhanh gọn.mp3"),                                        0.00, 0.70, "equalizer=f=2800:t=q:w=1.2:g=-4.0,lowpass=f=8800"),
    "shimmer":      (find_sfx("sfx_crystal_shimmer.mp3"),                                                 0.00, 0.85, VO_POCKET_EQ),
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
            continue
        af_parts = [f"atrim={t0:.3f}:{t1:.3f}", "asetpts=PTS-STARTPTS"]
        if extra_af:
            af_parts.append(extra_af)
        arr = decode_stereo_f32(path, af=",".join(af_parts))
        if len(arr) < 64:
            continue
        n_in = min(len(arr) // 4, int(0.015 * SR))
        n_out = min(len(arr) // 3, int(0.080 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
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

def loop_to_len(arr, n):
    if len(arr) >= n:
        return arr[:n].copy()
    reps = (n + len(arr) - 1) // len(arr)
    return np.tile(arr, (reps, 1))[:n].copy()

def main():
    dur_j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3250:t=q:w=1.15:g=1.6,loudnorm=I=-13.6:TP=-1.0:LRA=8")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # 2-Half C-Major BGM (Warm Fretless 0-30.3s -> Smooth 1.8s Crossfade -> Bright Riley 30.3-76.44s)
    bgm_eq = "highpass=f=75,equalizer=f=1950:t=q:w=1.30:g=-5.0,loudnorm=I=-15:TP=-1.5:LRA=9"
    b1 = loop_to_len(decode_stereo_f32(os.path.join(BGM_DIR, "bgm_warm_fretless.mp3"), af=bgm_eq), N)
    b2 = loop_to_len(decode_stereo_f32(os.path.join(BGM_DIR, "bgm_bright_riley.mp3"), af=bgm_eq), N)
    t_axis = np.arange(N, dtype=np.float32) / SR
    w_b2 = np.clip((t_axis - 29.4) / 1.8, 0.0, 1.0)
    bgm = b1 * (1.0 - w_b2)[:, None] + b2 * w_b2[:, None]

    # Dynamic Sidechain Ducking
    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.022).astype(np.float32)
    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 14):min(n_hops, i_h + 22)] = 1.0
    win_sm = np.hanning(35).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), win_sm, mode="valid")[:n_hops]
    gain_hop = 0.48 * (1.0 - sp_sm) + 0.275 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)
    bgm_env *= np.clip(t_axis / 0.35, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 1.5, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    # Clean, refined TVC SFX cues (never harsh or comical!)
    cues += stamp(sfx_bus, bank, "whoosh_tvc",   0.38, -18.0, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",   0.46, -20.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "whoosh_pip",   2.92, -18.2, pan=-0.16)
    cues += stamp(sfx_bus, bank, "card_slide",   3.06, -18.5, pan=+0.16)
    cues += stamp(sfx_bus, bank, "swoosh_light", 8.98, -18.4, pan=0.0)

    # 4-Card Symptom Deck
    cues += stamp(sfx_bus, bank, "card_swipe",  14.04, -17.8, pan=-0.20)
    cues += stamp(sfx_bus, bank, "card_slide",  15.34, -18.4, pan=-0.08)
    cues += stamp(sfx_bus, bank, "card_slide",  16.44, -18.4, pan=+0.08)
    cues += stamp(sfx_bus, bank, "card_swipe",  17.56, -17.8, pan=+0.18)
    cues += stamp(sfx_bus, bank, "notif_subtle",17.86, -19.8, pan=0.0, align_peak=False)

    # Key Thesis Punch-In (25.38s & 30.32s)
    cues += stamp(sfx_bus, bank, "swoosh_light",25.38, -18.4, pan=0.0)
    cues += stamp(sfx_bus, bank, "whoosh_tvc",  30.34, -17.6, pan=0.0)
    cues += stamp(sfx_bus, bank, "shimmer",     30.95, -20.2, pan=0.0, align_peak=False)

    # 4-Card Holistic Factors + White Skin Open Box
    cues += stamp(sfx_bus, bank, "card_swipe",  36.84, -17.8, pan=-0.20)
    cues += stamp(sfx_bus, bank, "shimmer",     37.10, -20.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "card_slide",  38.60, -18.4, pan=-0.08)
    cues += stamp(sfx_bus, bank, "card_slide",  40.38, -18.4, pan=+0.08)
    cues += stamp(sfx_bus, bank, "card_swipe",  42.98, -18.0, pan=+0.18)

    # Warning & Health Mirror
    cues += stamp(sfx_bus, bank, "whoosh_tvc",  46.18, -18.0, pan=0.0)
    cues += stamp(sfx_bus, bank, "notif_subtle",46.62, -19.8, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "swoosh_light",52.34, -18.4, pan=0.0)

    # 3-Card Lifestyle Deck + Reflection Punch-In
    cues += stamp(sfx_bus, bank, "card_swipe",  56.20, -18.0, pan=-0.18)
    cues += stamp(sfx_bus, bank, "card_slide",  58.02, -18.4, pan=0.0)
    cues += stamp(sfx_bus, bank, "card_slide",  59.28, -18.4, pan=+0.18)
    cues += stamp(sfx_bus, bank, "whoosh_tvc",  60.50, -17.8, pan=0.0)

    # Multi-Angle White Skin Cutaway + Finale Checklist
    cues += stamp(sfx_bus, bank, "whoosh_scene",63.62, -17.5, pan=0.0)
    cues += stamp(sfx_bus, bank, "shimmer",     64.05, -20.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "whoosh_pip",  68.90, -18.2, pan=-0.18)
    cues += stamp(sfx_bus, bank, "whoosh_pip",  69.26, -18.2, pan=+0.18)
    cues += stamp(sfx_bus, bank, "whoosh_tvc",  71.96, -17.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",  72.16, -20.0, pan=-0.15, align_peak=False)
    cues += stamp(sfx_bus, bank, "pop_soft",    73.26, -19.5, pan=0.0,   align_peak=False)
    cues += stamp(sfx_bus, bank, "notif_subtle",74.40, -19.8, pan=+0.15, align_peak=False)

    print(f"Stamped {cues} subtle luxury SFX cues across {vid_dur:.2f}s!")

    sfx_bus = (np.tanh(sfx_bus * 0.95) / 0.95) * 0.78
    full_mix = vo + bgm + sfx_bus
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)

    mix_wav = os.path.join(STEMS_DIR, "full_mix_pre_lufs.wav")
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
        print("2-pass loudnorm:", st_j["input_i"], "-> -14.0 LUFS")
    else:
        af_str = "loudnorm=I=-14:TP=-1:LRA=11"

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_mov,
        "-c:v", "copy", "-af", af_str, "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
        LOCAL_FINAL
    ], check=True)
    if os.path.exists(pre_mov):
        os.remove(pre_mov)

    # Single clean local export (NO CapCut draft!)
    os.makedirs(os.path.dirname(LOCAL_EXPORT), exist_ok=True)
    shutil.copy2(LOCAL_FINAL, LOCAL_EXPORT)
    print("Exported single local Final MP4:", LOCAL_EXPORT)

    if os.path.exists(os.path.dirname(DRIVE_FINAL)):
        shutil.copy2(LOCAL_FINAL, DRIVE_FINAL)
        print("Synced Cloud Final:", DRIVE_FINAL)

    if os.path.exists(os.path.dirname(ARTIFACT_MP4)):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", LOCAL_FINAL,
            "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "copy", "-movflags", "+faststart", ARTIFACT_MP4
        ], check=True)

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", LOCAL_FINAL,
        "-vf", f"fps=20/{vid_dur:.2f},scale=270:480,tile=5x4",
        "-frames:v", "1", "-q:v", "2", os.path.join(CHECK_DIR, "v3_sheet.jpg")
    ], check=True)

    os.makedirs(os.path.join(DRIVE_PROJ, "check"), exist_ok=True)
    os.makedirs(os.path.join(DRIVE_PROJ, "hf_fcp_ae_text"), exist_ok=True)
    for fn in ["clean_transcript_20261119.py", "build_whiteskin_showcase.py", "render_master_20261119.py", "mix_final_20261119.py"]:
        fp = os.path.join(PROJ_DIR, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    hf_idx = os.path.join(PROJ_DIR, "hf_fcp_ae_text", "index.html")
    if os.path.exists(hf_idx):
        shutil.copy2(hf_idx, os.path.join(DRIVE_PROJ, "hf_fcp_ae_text", "index.html"))
    shutil.copy2(os.path.join(AROLL_DIR, "main_cut_clean.json"), os.path.join(DRIVE_PROJ, "main_cut_clean.json"))
    shutil.copy2(os.path.join(CHECK_DIR, "v3_sheet.jpg"), os.path.join(DRIVE_PROJ, "check", "v3_sheet.jpg"))
    print("Synced project archive to:", DRIVE_PROJ)

if __name__ == "__main__":
    main()
