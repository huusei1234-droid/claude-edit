import json, math, os, re, shutil, subprocess, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\htpm-tokyo"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
os.makedirs(STEMS_DIR, exist_ok=True)

TLH_SFX_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
TOKYO_BGM    = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\07_Sôi Động - EDM - Remix - Trend TikTok\Dj Kantik - Teriyaki Boyz - Tokyo Drift & Sean Paul - Temperature (Remix).mp3"
TOKYO_FALLBK = os.path.join(AROLL_DIR, "tokyo_bgm.mp3")

RAW_VID      = os.path.join(PROJ_DIR, "_tokyo_master_video_only.mp4")
MAIN_CUT     = os.path.join(AROLL_DIR, "main_cut.mp4")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "htpm_tokyo_final.mp4")
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\HTPM_FINAL.mp4"
DRIVE_FINAL  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-tokyo"
ARTIFACT_MP4 = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\HTPM_FINAL.mp4"

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

VO_POCKET_EQ = "equalizer=f=2650:t=q:w=1.15:g=-4.5,lowpass=f=9200"

SFX_SPECS = {
    "card_swipe":   (tlh_sfx("Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3"), 0.04, 0.52, VO_POCKET_EQ),
    "card_slide":   (tlh_sfx("Slide - Tiếng trượt chữ ngang mượt.mp3"),                                  0.04, 0.54, "lowpass=f=6800"),
    "whoosh_tvc":   (tlh_sfx("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"),                               0.06, 0.54, VO_POCKET_EQ),
    "whoosh_scene": (tlh_sfx("Whoosh - Lướt chuyển cảnh cơ bản.mp3"),                                    0.22, 0.62, VO_POCKET_EQ),
    "swoosh_light": (tlh_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),                               0.08, 0.39, VO_POCKET_EQ),
    "whoosh_pip":   (tlh_sfx("Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP).mp3"),                     0.04, 0.28, VO_POCKET_EQ),
    "pop_soft":     (tlh_sfx("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),                                       0.03, 0.27, VO_POCKET_EQ),
    "notif_subtle": (tlh_sfx("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"),                  0.10, 0.42, VO_POCKET_EQ),
    "ting_clean":   (tlh_sfx("Ting - Chuông Ting nhanh gọn.mp3"),                                        0.00, 0.72, "equalizer=f=2800:t=q:w=1.2:g=-4.0,lowpass=f=8800"),
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

def main():
    dur_j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # Crisp pharmacist voiceover (+1.8dB presence lift at 3.3kHz)
    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3300:t=q:w=1.15:g=1.8,loudnorm=I=-13.6:TP=-1.0:LRA=8")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # Exact Tokyo Drift Remix from TLH\Edit starting at EXACT 29.00s ("bắt đầu từ giây thứ 29 của bài nhạc")!
    bgm_src = TOKYO_BGM if os.path.exists(TOKYO_BGM) else TOKYO_FALLBK
    print(f"Using Tokyo Drift BGM from {bgm_src} starting at 29.00s!", flush=True)
    # Carve a clean vocal pocket (-5.8dB around 1.8-3.2kHz) while preserving the punchy Tokyo Drift sub-bass & synth groove!
    bgm_eq = "equalizer=f=2250:t=q:w=1.35:g=-5.8,equalizer=f=95:t=q:w=1.1:g=1.2,loudnorm=I=-14:TP=-1.5:LRA=9"
    bgm_raw = decode_stereo_f32(bgm_src, ss=29.000, dur_limit=vid_dur + 2.0, af=bgm_eq)
    bgm = np.vstack([bgm_raw, np.zeros((max(0, N - len(bgm_raw)), 2), dtype=np.float32)])[:N]

    # Dynamic Sidechain Ducking: keeps Tokyo Drift groove energetic (~0.32 under speech, lifting to ~0.56 on beat drops & pauses!)
    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.024).astype(np.float32)

    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 14):min(n_hops, i_h + 22)] = 1.0
    win_sm = np.hanning(35).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), win_sm, mode="valid")[:n_hops]
    gain_hop = 0.54 * (1.0 - sp_sm) + 0.305 * sp_sm
    t_axis = np.arange(N, dtype=np.float32) / SR
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)
    # Clean fade-in (0.25s so 29.0s Tokyo Drift beat hits immediately!) & smooth 1.4s outro fade
    bgm_env *= np.clip(t_axis / 0.25, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 1.4, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    # Synchronized Beat & Motion SFX (clean, tactile, never clashing with Tokyo Drift beat!)
    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    cues += stamp(sfx_bus, bank, "whoosh_tvc",   0.44, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",   0.50, -19.2, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "whoosh_pip",   2.86, -17.2, pan=-0.18)
    cues += stamp(sfx_bus, bank, "card_slide",   3.00, -17.5, pan=+0.18)

    cues += stamp(sfx_bus, bank, "card_swipe",   5.76, -16.8, pan=-0.20)
    cues += stamp(sfx_bus, bank, "card_slide",   6.55, -17.4, pan=0.0)
    cues += stamp(sfx_bus, bank, "card_swipe",   8.64, -16.8, pan=-0.10)
    cues += stamp(sfx_bus, bank, "card_swipe",  11.38, -16.8, pan=+0.15)
    cues += stamp(sfx_bus, bank, "notif_subtle",14.55, -18.5, pan=0.0, align_peak=False)

    cues += stamp(sfx_bus, bank, "whoosh_tvc",  16.08, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",  16.15, -19.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "whoosh_pip",  20.52, -17.2, pan=-0.22)
    cues += stamp(sfx_bus, bank, "whoosh_pip",  21.36, -17.2, pan=+0.22)

    cues += stamp(sfx_bus, bank, "swoosh_light",25.22, -17.5, pan=0.0)
    cues += stamp(sfx_bus, bank, "pop_soft",    25.90, -18.4, pan=-0.28, align_peak=False)
    cues += stamp(sfx_bus, bank, "pop_soft",    27.02, -18.4, pan=-0.10, align_peak=False)
    cues += stamp(sfx_bus, bank, "pop_soft",    28.64, -18.4, pan=+0.10, align_peak=False)
    cues += stamp(sfx_bus, bank, "notif_subtle",29.50, -18.6, pan=+0.28, align_peak=False)

    cues += stamp(sfx_bus, bank, "whoosh_scene",30.24, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "swoosh_light",33.20, -17.2, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",  33.42, -19.0, pan=-0.15, align_peak=False)
    cues += stamp(sfx_bus, bank, "pop_soft",    34.90, -18.5, pan=0.0,   align_peak=False)
    cues += stamp(sfx_bus, bank, "notif_subtle",35.92, -18.8, pan=+0.15, align_peak=False)

    print(f"Stamped {cues} synchronized SFX cues over Tokyo Drift (29.0s) across {vid_dur:.2f}s!")

    sfx_bus = (np.tanh(sfx_bus * 0.95) / 0.95) * 0.80
    full_mix = vo + bgm + sfx_bus
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)

    mix_wav = os.path.join(STEMS_DIR, "full_mix_pre_lufs.wav")
    save_wav_16(mix_wav, full_mix)

    pre_mov = os.path.join(PROJ_DIR, "_tokyo_pre_lufs.mov")
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
    for fn in ["clean_tokyo_transcript.py", "gen_tokyo_assets.py", "render_tokyo_master.py", "mix_tokyo_final.py"]:
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
