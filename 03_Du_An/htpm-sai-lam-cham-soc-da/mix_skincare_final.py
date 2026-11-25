import json, math, os, re, shutil, subprocess, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
os.makedirs(STEMS_DIR, exist_ok=True)

TLH_BGM_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"
TLH_SFX_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"

RAW_VID      = os.path.join(PROJ_DIR, "_skincare_carddeck_video_only.mp4")
MAIN_CUT     = os.path.join(AROLL_DIR, "main_cut.mp4")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "htpm_sai_lam_cham_soc_da_final.mp4")
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\HTPM_SAI_LAM_CHAM_SOC_DA_FINAL.mp4"
DRIVE_FINAL  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_SAI_LAM_CHAM_SOC_DA_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-sai-lam-cham-soc-da"
ARTIFACT_MP4 = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\HTPM_SAI_LAM_CHAM_SOC_DA_FINAL.mp4"

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
    "chan_hook":    (tlh_sfx("Drama - Tiếng nhạc chốt ngắn (Chan).mp3"),                           0.02, 1.85, "lowpass=f=8500"),
    "card_swipe":   (tlh_sfx("Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3"), 0.04, 0.52, VO_POCKET_EQ),
    "card_slide":   (tlh_sfx("Slide - Tiếng trượt chữ ngang mượt.mp3"),                            0.04, 0.54, "lowpass=f=6800"),
    "whoosh_tvc":   (tlh_sfx("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"),                         0.06, 0.54, VO_POCKET_EQ),
    "whoosh_scene": (tlh_sfx("Whoosh - Lướt chuyển cảnh cơ bản.mp3"),                              0.22, 0.62, VO_POCKET_EQ),
    "swoosh_light": (tlh_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),                         0.08, 0.39, VO_POCKET_EQ),
    "whoosh_pip":   (tlh_sfx("Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP).mp3"),               0.04, 0.28, VO_POCKET_EQ),
    "pop_soft":     (tlh_sfx("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),                                 0.03, 0.27, VO_POCKET_EQ),
    "notif_subtle": (tlh_sfx("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"),            0.10, 0.42, VO_POCKET_EQ),
    "ting_clean":   (tlh_sfx("Ting - Chuông Ting nhanh gọn.mp3"),                                  0.00, 0.72, "equalizer=f=2800:t=q:w=1.2:g=-4.0,lowpass=f=8800"),
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
    print(f"Loaded {len(bank)} curated TLH Edit SFX instruments.")
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

    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3350:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    bgm1_path = os.path.join(TLH_BGM_DIR, r"03_Spa - Thư Giãn - Chữa Lành - Thiên Nhiên\A warm piano solo, a healing solfeggio(1387534) (1p52s).mp3")
    bgm2_path = os.path.join(TLH_BGM_DIR, r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Calm Inspirational Background (4p24s).mp3")
    if not os.path.exists(bgm1_path):
        bgm1_path = os.path.join(TLH_BGM_DIR, r"04_Piano - Buồn - Sâu Lắng - Cảm Xúc\Soft Piano Inspiration01 (4p26s).mp3")
    if not os.path.exists(bgm2_path):
        bgm2_path = os.path.join(TLH_BGM_DIR, r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Corporate Medicine (2p22s).mp3")

    bgm_eq = "highpass=f=85,equalizer=f=2150:t=q:w=1.25:g=-4.8,lowpass=f=12000,loudnorm=I=-14:TP=-1.5:LRA=9"
    b1_raw = decode_stereo_f32(bgm1_path, ss=2.0, dur_limit=72.0, af=bgm_eq)
    b2_raw = decode_stereo_f32(bgm2_path, ss=3.5, dur_limit=30.0, af=bgm_eq)
    b1 = np.tile(b1_raw, ((N // len(b1_raw)) + 2, 1))[:N]
    b2 = np.tile(b2_raw, ((N // len(b2_raw)) + 2, 1))[:N]

    t_axis = np.arange(N, dtype=np.float32) / SR
    xfade = np.clip((t_axis - 67.2) / 2.4, 0.0, 1.0)
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
            sp_dil[max(0, i_h - 20):min(n_hops, i_h + 28)] = 1.0
    win_sm = np.hanning(43).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (21, 21), mode="edge"), win_sm, mode="valid")[:n_hops]
    gain_hop = 0.44 * (1.0 - sp_sm) + 0.255 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)
    bgm_env *= np.clip(t_axis / 0.8, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 1.8, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    # Full Synchronized Card-Fan, Card-Push & Emphasis Text SFX Choreography!
    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    # 1. Hook (0.04 - 1.80s) + 3-Card Overview Playing-Card Fan (2.95 - 5.82s)
    cues += stamp(sfx_bus, bank, "chan_hook",    0.06, -14.8, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "swoosh_light", 0.74, -17.5, pan=+0.15)
    cues += stamp(sfx_bus, bank, "card_swipe",   3.02, -16.8, pan=-0.22)
    cues += stamp(sfx_bus, bank, "card_slide",   3.18, -17.2, pan=0.0)
    cues += stamp(sfx_bus, bank, "pop_soft",     3.32, -18.2, pan=+0.22, align_peak=False)

    # 2. Mistake #1 Banner (5.88s) + Deck #1 Fan-In (8.12s) + Push #1 (14.38s) + Emphasis (18.08s) + Push #2 (20.65s) + Emphasis (27.38s)
    cues += stamp(sfx_bus, bank, "whoosh_tvc",   5.90, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",   5.96, -19.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "card_swipe",   8.14, -16.8, pan=-0.18)
    cues += stamp(sfx_bus, bank, "card_slide",   8.98, -17.5, pan=0.0)
    cues += stamp(sfx_bus, bank, "card_swipe",  14.42, -16.8, pan=-0.15)
    cues += stamp(sfx_bus, bank, "notif_subtle",18.08, -18.8, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "card_swipe",  20.68, -16.8, pan=+0.15)
    cues += stamp(sfx_bus, bank, "pop_soft",    27.38, -18.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "swoosh_light",29.85, -17.8, pan=0.0)

    # 3. Mistake #2 Banner (30.14s) + Trend Card (33.12s) + 4-Skin-Type Rapid Playing-Card Fan Shuffle (39.25 - 49.05s)!
    cues += stamp(sfx_bus, bank, "whoosh_tvc",  30.16, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",  30.22, -19.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "whoosh_pip",  33.14, -17.2, pan=+0.15)
    cues += stamp(sfx_bus, bank, "card_swipe",  39.26, -16.8, pan=-0.24)
    cues += stamp(sfx_bus, bank, "card_slide",  39.96, -17.4, pan=-0.16)
    cues += stamp(sfx_bus, bank, "card_slide",  40.98, -17.0, pan=-0.06)
    cues += stamp(sfx_bus, bank, "card_slide",  41.76, -17.0, pan=+0.08)
    cues += stamp(sfx_bus, bank, "card_swipe",  42.68, -16.8, pan=+0.22)
    cues += stamp(sfx_bus, bank, "notif_subtle",43.68, -18.8, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "card_slide",  44.02, -17.5, pan=0.0)
    cues += stamp(sfx_bus, bank, "card_swipe",  47.50, -17.0, pan=+0.18)
    cues += stamp(sfx_bus, bank, "swoosh_light",48.85, -17.8, pan=0.0)

    # 4. Mistake #3 Banner (49.10s) + Deck #3 Fan-In (53.52s) + Push 01 (54.48s) + Push 1-2 AM (56.95s) + Push Sugar (59.72s) + Push Back 01 (63.40s)
    cues += stamp(sfx_bus, bank, "whoosh_tvc",  49.12, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",  49.18, -19.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "card_swipe",  53.54, -16.8, pan=-0.18)
    cues += stamp(sfx_bus, bank, "card_slide",  54.48, -17.5, pan=-0.10)
    cues += stamp(sfx_bus, bank, "card_swipe",  56.96, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "pop_soft",    57.22, -18.8, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "card_swipe",  59.74, -16.8, pan=+0.18)
    cues += stamp(sfx_bus, bank, "card_slide",  63.42, -16.9, pan=-0.16)
    cues += stamp(sfx_bus, bank, "notif_subtle",64.28, -18.6, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "swoosh_light",67.65, -17.8, pan=0.0)

    # 5. Core Takeaway (67.90s) + Healthy Cutaway (71.38s) + Finale Summary & Closing Ribbon (76.38s)
    cues += stamp(sfx_bus, bank, "whoosh_tvc",  67.92, -16.8, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",  67.98, -19.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "whoosh_scene",71.40, -17.0, pan=0.0)
    cues += stamp(sfx_bus, bank, "swoosh_light",76.38, -17.2, pan=0.0)
    cues += stamp(sfx_bus, bank, "ting_clean",  76.46, -19.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_bus, bank, "notif_subtle",76.70, -19.5, pan=0.0, align_peak=False)

    print(f"Stamped {cues} synchronized Card-Fan, Card-Push & Emphasis SFX cues across {vid_dur:.2f}s!")

    sfx_bus = (np.tanh(sfx_bus * 0.95) / 0.95) * 0.84
    full_mix = vo + bgm + sfx_bus
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)

    mix_wav = os.path.join(STEMS_DIR, "full_mix_pre_lufs.wav")
    save_wav_16(mix_wav, full_mix)

    pre_mov = os.path.join(PROJ_DIR, "_skincare_pre_lufs.mov")
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
    for fn in ["clean_skincare_transcript.py", "gen_skincare_assets.py", "render_skincare_carddeck.py", "mix_skincare_final.py"]:
        fp = os.path.join(PROJ_DIR, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    shutil.copy2(os.path.join(AROLL_DIR, "main_cut_clean.json"), os.path.join(DRIVE_PROJ, "main_cut_clean.json"))
    shutil.copy2(os.path.join(CHECK_DIR, "v3_sheet.jpg"), os.path.join(DRIVE_PROJ, "check", "v3_sheet.jpg"))
    print("Synced project archive to:", DRIVE_PROJ)

if __name__ == "__main__":
    main()
