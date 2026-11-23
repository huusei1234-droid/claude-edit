import copy, json, math, os, re, shutil, subprocess, time, uuid, wave
import numpy as np

PROJ_DIR = r"d:\AI\full studio\output\av-protein-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems_v4")
os.makedirs(STEMS_DIR, exist_ok=True)

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
RAW_VID    = os.path.join(PROJ_DIR, "_v4_video_only.mp4")
MAIN_CUT   = os.path.join(AROLL_DIR, "main_cut.mp4")
MIX_PRE    = os.path.join(PROJ_DIR, "_v4_mixed_pre_lufs.mp4")
FINAL_V4   = os.path.join(PROJ_DIR, "bojomi_talking_head_v4_final.mp4")
FINAL_ALIAS= os.path.join(PROJ_DIR, "bojomi_final.mp4")
DRIVE_FINAL= r"Z:\Drive của tôi\BOJOMI_TALKING_HEAD_FINAL.mp4"

SR = 48000

# Verified real Studio & CapCut SFX bank on user's machine with measured peak timestamps!
SFX_BANK_SPECS = {
    # key: (path, trim_start_s, trim_end_s, extra_af)
    "pop_telop":    (r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\d3b74afaf571dd3056bd7e9996a683cc.mp3", 0.02, 0.16, None),
    "pop_chu":      (r"D:\Edit\Sound Effect\Pop - chữ.mp3", 0.00, 0.36, None),
    "poyoi":        (r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\7224007c5bf7718eb196280273c309e0.mp3", 0.04, 0.42, None),
    "deep_woosh":   (r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\270677b49d33e1e347819050db9ee915.mp3", 0.18, 1.55, None),
    "short_wosh":   (r"D:\Edit\Sound Effect\Short wosh - chữ.mp3", 0.02, 0.32, None),
    "swoosh5":      (r"D:\Edit\Sound Effect\SWOOSH chữ #5.mp3", 0.06, 0.40, None),
    "slide_up":     (r"D:\Edit\Sound Effect\slide up.mp3", 0.22, 0.78, "highpass=f=180"),
    "slide_ngang":  (r"D:\Edit\Sound Effect\slide ngang.mp3", 0.08, 0.62, None),
    "shutter":      (r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\66c35a8a836911a52824fcd5c8cb016a.mp3", 0.04, 0.52, None),
    "shutter3":     (r"D:\Edit\Sound Effect\tiếng chụp hình 3.mp3", 0.21, 0.68, None),
    "tick_clean":   (r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx\sfx_click_soft.mp3", 0.03, 0.12, "highpass=f=400"),
    "mouse_tick":   (r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\25b5bc6c42f453173fbf056859eec22b.mp3", 0.26, 0.43, "highpass=f=500"),
    "noitifi":      (r"D:\Edit\Sound Effect\Noitifi - chữ.mp3", 0.10, 0.47, None),
    "correct_ding": (r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\2f2a43f99ec1030b4daf2991ab817829.mp3", 0.00, 1.15, None),
    "magic_reveal": (r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\229f88e6452098f686f43df9309b1acc.mp3", 0.02, 1.85, None),
    "riser_metal":  (r"D:\Edit\Sound Effect\SFX - Riser Metallic (Transition) - YouTube.mp3", 1.35, 3.32, None),
    "riser_clean":  (r"D:\Edit\Sound Effect\riser.mp3", 1.30, 3.40, None),
    "warm_hit":     (r"D:\Edit\SFX LÊ TUẤN KHANG\le tuan khang\Tiếng Nổ impact căng căng.mp3", 0.16, 1.55, "lowpass=f=2400"),
}

def decode_stereo_f32(path, dur_limit=None, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if dur_limit:
        cmd += ["-t", f"{dur_limit:.3f}"]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    arr = np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()
    return arr

def save_wav_16(path, stereo_arr):
    clipped = np.clip(stereo_arr, -0.99, 0.99)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

def load_normalized_sfx_bank():
    bank = {}
    for key, (path, t0, t1, extra_af) in SFX_BANK_SPECS.items():
        if not os.path.exists(path):
            print("WARNING missing SFX:", key, path)
            continue
        af_parts = [f"atrim={t0:.3f}:{t1:.3f}", "asetpts=PTS-STARTPTS"]
        if extra_af:
            af_parts.append(extra_af)
        arr = decode_stereo_f32(path, af=",".join(af_parts))
        if len(arr) < 64:
            continue
        # Smooth anti-click micro-fades (6ms in, 35ms out)
        n_in = min(len(arr) // 4, int(0.006 * SR))
        n_out = min(len(arr) // 3, int(0.035 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        # Peak-normalize to 0.0 dBFS (max abs = 1.0) so every dB setting is 100% true & consistent!
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        # Record exact sample index of peak inside trimmed clip!
        mono_env = np.max(np.abs(arr), axis=1)
        pk_idx = int(np.argmax(mono_env))
        bank[key] = (arr, pk_idx)
    print(f"Loaded & peak-normalized {len(bank)} studio SFX instruments.")
    return bank

def stamp_sfx(bus, bank, key, target_sec, db, pan=0.0, align_peak=True):
    """
    Stamps peak-normalized SFX onto stereo bus (N, 2) with exact peak alignment & stereo pan!
    pan in [-1.0 (left) .. +1.0 (right)]
    """
    if key not in bank:
        return
    clip, pk_idx = bank[key]
    gain = 10.0 ** (db / 20.0)
    # Equal-power stereo pan
    angle = (max(-1.0, min(1.0, pan)) + 1.0) * (math.pi / 4.0)
    g_l = gain * math.cos(angle) * 1.4142
    g_r = gain * math.sin(angle) * 1.4142

    start_idx = int(round(target_sec * SR)) - (pk_idx if align_peak else 0)
    end_idx = start_idx + len(clip)

    b_s = max(0, start_idx)
    b_e = min(len(bus), end_idx)
    if b_e <= b_s:
        return
    c_s = b_s - start_idx
    c_e = c_s + (b_e - b_s)
    seg = clip[c_s:c_e]
    bus[b_s:b_e, 0] += seg[:, 0] * g_l
    bus[b_s:b_e, 1] += seg[:, 1] * g_r

def build_master_sound_and_video():
    from render_th_v4 import load_timeline_v4, NUMBERS, KEYWORDS, TILE_PLACES, LOGO_BAR_SPAN, RINGS_SPANS

    dur_j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. Decode & Studio-Polish Pharmacist Voiceover (-14 LUFS clean vocal presence)
    vo_af = "highpass=f=80,equalizer=f=3400:t=q:w=1.2:g=1.8,loudnorm=I=-14:TP=-1.2:LRA=9"
    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af=vo_af)
    if len(vo) < N:
        vo = np.vstack([vo, np.zeros((N - len(vo), 2), dtype=np.float32)])
    else:
        vo = vo[:N]

    # 2. Decode 2-Half C-Major Broadcast BGM Normalized to -14 LUFS + Vocal Pocket EQ + Lookahead Dynamic Ducking!
    #    - Part 1 (0.0 - 34.4s, context/problem): Warm Acoustic Fretless (C-Major)
    #    - Part 2 (34.4 - 66.4s, BOJOMI solution & CTA): Bright Uplifting Riley (C-Major), 2.0s smooth crossfade!
    bgm_eq = "highpass=f=90,equalizer=f=2200:t=q:w=1.25:g=-4.2,lowpass=f=12500,loudnorm=I=-14:TP=-1.5:LRA=9"
    bgm1_src = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx\bgm_warm_fretless.mp3"
    bgm2_src = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx\bgm_bright_riley.mp3"
    b1_raw = decode_stereo_f32(bgm1_src, af=bgm_eq)
    b2_raw = decode_stereo_f32(bgm2_src, af=bgm_eq)

    b1 = np.tile(b1_raw, ((N // len(b1_raw)) + 2, 1))[:N]
    b2 = np.tile(b2_raw, ((N // len(b2_raw)) + 2, 1))[:N]

    t_axis = np.arange(N, dtype=np.float32) / SR
    # Smooth 2.0s crossfade at 34.36s ("Với sản phẩm Bojomi của An Vượng...")
    xfade = np.clip((t_axis - 33.36) / 2.0, 0.0, 1.0)
    xfade = xfade * xfade * (3.0 - 2.0 * xfade)
    bgm = b1 * (1.0 - xfade[:, None]) + b2 * xfade[:, None]

    broll_spans, cap_groups, GOLD_WORDS, ORCHID_WORDS, STROKE_UP_WORDS = load_timeline_v4()

    # Lookahead Speech Activity Detector (10ms windows) -> true CapCut Pro Dynamic Ducking!
    # Speech active: BGM = 0.28 (-11.0 dB below -14 LUFS voice = ~ -25.0 LUFS, warm & clearly audible!)
    # Speech pause / B-roll / Intro / Outro: BGM swells smoothly to 0.46 (-6.7 dB = ~ -20.7 LUFS),
    # ducking 0.20s BEFORE the next spoken word begins!
    hop = 480  # 10ms at 48kHz
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.022).astype(np.float32)

    # Expand speaking mask 200ms earlier (lookahead) & 280ms after so BGM never pumps between syllables
    k_pre, k_post = 20, 28
    sp_dilated = np.zeros_like(speaking)
    for idx_h in range(n_hops):
        if speaking[idx_h] > 0.5:
            sp_dilated[max(0, idx_h - k_pre):min(n_hops, idx_h + k_post)] = 1.0

    # Smooth envelope with 380ms Gaussian-like moving average
    win_sm = np.hanning(39).astype(np.float32)
    win_sm /= np.sum(win_sm)
    sp_smooth = np.convolve(np.pad(sp_dilated, (19, 19), mode="edge"), win_sm, mode="valid")[:n_hops]

    gain_hop = 0.46 * (1.0 - sp_smooth) + 0.285 * sp_smooth
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)

    # Extra gentle +1.5 dB musical lift during visual 3D B-Roll cards (still keeping voice crystal clear!)
    for st, en, _, _, _ in broll_spans:
        w_br = np.clip(np.minimum((t_axis - st) / 0.45, (en - t_axis) / 0.45), 0.0, 1.0)
        bgm_env *= (1.0 + 0.18 * w_br)

    # Smooth 0.8s fade-in at 0:00 and 1.8s fade-out at end
    bgm_env *= np.clip(t_axis / 0.8, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 1.8, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    # 3. Build 2 Rich Stereo SFX Stems (125+ Precision Peak-Aligned Cues!)
    bank = load_normalized_sfx_bank()
    sfx_trans = np.zeros((N, 2), dtype=np.float32)  # Risers, Whooshes, Warm Hits, Shimmers
    sfx_ui    = np.zeros((N, 2), dtype=np.float32)  # Pops, Shutters, Slides, Caption Clicks

    cue_count = 0

    # Layer A: Hook 3.5s Signature Cues
    stamp_sfx(sfx_trans, bank, "short_wosh",   0.08, -6.5, pan=0.0);  cue_count += 1
    stamp_sfx(sfx_trans, bank, "magic_reveal", 0.12, -9.5, pan=0.0, align_peak=False); cue_count += 1
    stamp_sfx(sfx_ui,    bank, "pop_chu",      0.35, -6.2, pan=-0.25); cue_count += 1
    stamp_sfx(sfx_ui,    bank, "poyoi",        0.57, -6.8, pan=+0.25); cue_count += 1
    stamp_sfx(sfx_trans, bank, "swoosh5",      1.74, -8.0, pan=0.0);  cue_count += 1

    # Layer B: 3 Overhead Hook Tiles (Left -> Center -> Right stereo pop!) + 6 Body Flying Neon Tiles
    for idx_t, (ikey, t0, t1, cx, cy, sz, rot) in enumerate(TILE_PLACES):
        pan_t = (cx - 540.0) / 680.0
        if cy < 400:
            # Overhead 3 Hook tiles: crisp CapCut Pop Telop!
            stamp_sfx(sfx_ui, bank, "pop_telop", t0 + 0.06, -4.8, pan=pan_t); cue_count += 1
        else:
            # Body Neon Tiles flying up + burst shockwave!
            stamp_sfx(sfx_ui, bank, "slide_up", t0 + 0.12, -10.5, pan=pan_t, align_peak=False); cue_count += 1
            ding_k = "noitifi" if idx_t % 2 == 0 else "pop_chu"
            stamp_sfx(sfx_ui, bank, ding_k, t0 + 0.14, -6.8, pan=pan_t); cue_count += 1

    # Layer C: Tension Risers Climbing RIGHT INTO Major Beats + Warm Authoritative Hits on 1 / 2 / 3!
    riser_targets = [3.55, 17.96, 29.04, 34.36, 42.35, 59.30]
    for idx_r, rt in enumerate(riser_targets):
        r_key = "riser_metal" if idx_r % 2 == 0 else "riser_clean"
        stamp_sfx(sfx_trans, bank, r_key, rt, -8.2, pan=0.0, align_peak=True); cue_count += 1

    for lbl, dig, t0, t1 in NUMBERS:
        stamp_sfx(sfx_trans, bank, "warm_hit",     t0 + 0.04, -7.8, pan=0.0);   cue_count += 1
        stamp_sfx(sfx_ui,    bank, "correct_ding", t0 + 0.08, -7.8, pan=+0.22); cue_count += 1
        stamp_sfx(sfx_trans, bank, "short_wosh",   t0 + 0.02, -7.2, pan=-0.20); cue_count += 1

    # Layer D: All 12 Giant Behind-Head Keywords -> Crisp Analog Camera Shutter + Airy Swoosh (like video mẫu.mov!)
    for idx_k, (kw_txt, t0, t1, _, _, _) in enumerate(KEYWORDS):
        sh_key = "shutter" if idx_k % 2 == 0 else "shutter3"
        stamp_sfx(sfx_ui, bank, sh_key, t0 + 0.05, -7.8, pan=0.0); cue_count += 1
        if idx_k % 3 == 1:
            stamp_sfx(sfx_trans, bank, "swoosh5", t0 + 0.04, -9.2, pan=0.0); cue_count += 1

    # Layer E: Frosted Glass Bar Slide + 4 Rapid Micro-Pops (39.54s)
    lb0 = LOGO_BAR_SPAN[0]
    stamp_sfx(sfx_ui, bank, "slide_ngang", lb0 + 0.08, -7.2, pan=0.0); cue_count += 1
    for i_p in range(4):
        stamp_sfx(sfx_ui, bank, "pop_telop", lb0 + 0.10 + i_p * 0.08, -9.2, pan=-0.3 + i_p * 0.2); cue_count += 1

    # Layer F: 4 Dual 3D B-Roll Card Entry & Exit Cinema Whooshes
    for st, en, _, _, _ in broll_spans:
        stamp_sfx(sfx_trans, bank, "deep_woosh", st + 0.04, -5.8, pan=0.0); cue_count += 1
        stamp_sfx(sfx_ui,    bank, "pop_telop",  st + 0.20, -8.8, pan=0.0); cue_count += 1
        stamp_sfx(sfx_trans, bank, "swoosh5",    en - 0.02, -7.8, pan=0.0); cue_count += 1

    # Layer G: Orbital Rings Shimmer Reveals (42.35s & 59.30s) + Finale Gentle Swell
    for r0, r1 in RINGS_SPANS:
        stamp_sfx(sfx_trans, bank, "magic_reveal", r0 + 0.02, -6.5, pan=0.0, align_peak=False); cue_count += 1
        stamp_sfx(sfx_trans, bank, "deep_woosh",   r0 + 0.04, -6.8, pan=0.0); cue_count += 1
    stamp_sfx(sfx_trans, bank, "riser_clean", vid_dur - 0.55, -9.5, pan=0.0, align_peak=True); cue_count += 1

    # Layer H: Tactile Rhythmic Caption Micro-Clicks (exact video mẫu.mov formula, never masking speech!)
    last_click_t = -1.0
    rng = np.random.default_rng(2026)
    for g in cap_groups:
        for li, ln in enumerate(g["lines"]):
            for wi, (wtxt, ws, we) in enumerate(ln):
                if wtxt in STROKE_UP_WORDS:
                    stamp_sfx(sfx_ui, bank, "pop_telop", ws + 0.03, -7.2, pan=0.0); cue_count += 1
                    stamp_sfx(sfx_ui, bank, "correct_ding", ws + 0.06, -9.5, pan=0.0); cue_count += 1
                    last_click_t = ws
                elif wi == 0 and (ws - last_click_t) >= 0.26:
                    # Subtle rhythmic mechanical tick on each new stacked line!
                    tk = "tick_clean" if (li % 2 == 0) else "mouse_tick"
                    human_db = -15.8 + float(rng.uniform(-0.8, 0.8))
                    stamp_sfx(sfx_ui, bank, tk, ws + 0.02, human_db, pan=float(rng.uniform(-0.12, 0.12))); cue_count += 1
                    last_click_t = ws

    print(f"Stamped {cue_count} sample-accurate stereo SFX cues across {vid_dur:.2f}s!")

    # Soft limiter & harmonious studio trim on SFX buses so Voice + BGM + SFX sit in ideal balance
    sfx_trans = (np.tanh(sfx_trans * 0.95) / 0.95) * 0.86
    sfx_ui    = (np.tanh(sfx_ui * 0.95) / 0.95) * 0.86

    # Save clean multi-track stems for CapCut Desktop!
    vo_wav    = os.path.join(STEMS_DIR, "01_Voice_Master.wav")
    bgm_wav   = os.path.join(STEMS_DIR, "02_BGM_Ducked.wav")
    trans_wav = os.path.join(STEMS_DIR, "03_SFX_Transitions_Risers.wav")
    ui_wav    = os.path.join(STEMS_DIR, "04_SFX_Pops_Shutters_Ticks.wav")
    mix_wav   = os.path.join(STEMS_DIR, "full_mix_pre_lufs.wav")

    save_wav_16(vo_wav, vo)
    save_wav_16(bgm_wav, bgm)
    save_wav_16(trans_wav, sfx_trans)
    save_wav_16(ui_wav, sfx_ui)

    full_mix = vo + bgm + sfx_trans + sfx_ui
    # Gentle soft-knee safety ceiling before 2-pass EBU R128 loudnorm
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)
    save_wav_16(mix_wav, full_mix)

    # Mux video + pre-LUFS mix
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", RAW_VID, "-i", mix_wav,
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "pcm_s16le",
        MIX_PRE.replace(".mp4", ".mov")
    ], check=True)

    # 2-pass EBU R128 loudnorm -> exact -14.0 LUFS!
    p1 = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", MIX_PRE.replace(".mp4", ".mov"),
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
        "ffmpeg", "-y", "-v", "error", "-i", MIX_PRE.replace(".mp4", ".mov"),
        "-c:v", "copy", "-af", af_str, "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
        FINAL_V4
    ], check=True)
    shutil.copy2(FINAL_V4, FINAL_ALIAS)
    if os.path.exists( os.path.dirname(DRIVE_FINAL) ):
        shutil.copy2(FINAL_V4, DRIVE_FINAL)
        print("Exported directly to Google Drive:", DRIVE_FINAL)
    if os.path.exists(MIX_PRE.replace(".mp4", ".mov")):
        os.remove(MIX_PRE.replace(".mp4", ".mov"))
    print("Saved FINAL V4 Master:", FINAL_V4)

    # Generate 20-frame timestamped QC sheet
    shutil.copy2(
        r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf",
        os.path.join(CHECK_DIR, "_f.otf")
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL_V4,
        "-vf", "fps=1/3.3,scale=270:480,drawtext=fontfile=_f.otf:text='%{pts\\:hms}':fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.65:x=8:y=8,tile=5x4",
        "-frames:v", "1", os.path.join(CHECK_DIR, "v4_sheet.jpg")
    ], cwd=CHECK_DIR, check=True)

    return vid_dur, vo_wav, bgm_wav, trans_wav, ui_wav

def build_capcut_v4_multitrack(vid_dur, vo_wav, bgm_wav, trans_wav, ui_wav):
    tpl_dir = os.path.join(DRAFTS_DIR, "LT PLUS HẰNG THU - Video Mẫu")
    out_name = "BOJOMI_AnVuong_TalkingHead_v4_Master"
    out_dir = os.path.join(DRAFTS_DIR, out_name)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    T = json.load(open(os.path.join(tpl_dir, "draft_content.json"), encoding="utf-8"))
    TM = json.load(open(os.path.join(tpl_dir, "draft_meta_info.json"), encoding="utf-8"))
    def uid(): return str(uuid.uuid4()).upper()
    def us(sec): return int(round(sec * 30.0) / 30.0 * 1_000_000)

    vseg_tpl = next(s for tr in T["tracks"] if tr["type"] == "video" for s in tr["segments"])
    extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    tmat_tpl = {k: next(x for x in T["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"]) for k in extra_keys}
    vmat_tpl = next(x for x in T["materials"]["videos"] if x["id"] == vseg_tpl["material_id"])
    vtrack_tpl = next(tr for tr in T["tracks"] if tr["type"] == "video")

    aseg_tpl = next(s for tr in T["tracks"] if tr["type"] == "audio" for s in tr["segments"])
    amat_tpl = next(x for x in T["materials"]["audios"] if x["id"] == aseg_tpl["material_id"])
    atrack_tpl = next(tr for tr in T["tracks"] if tr["type"] == "audio")
    a_extra_keys = tuple(k for k in extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in T["materials"].get(k, [])))
    amat_extra_tpl = {k: next(x for x in T["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"]) for k in a_extra_keys}

    D = copy.deepcopy(T)
    draft_id = uid()
    total_us = us(vid_dur)
    D.update({
        "id": draft_id, "name": out_name, "fps": 30.0, "duration": total_us,
        "tracks": [], "materials": {k: [] for k in T["materials"]},
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None}
    })

    # Video Track 0 (muted video stream so user can independently control the 4 stems below in CapCut!)
    vm = copy.deepcopy(vmat_tpl)
    mid_v = uid()
    vm.update({
        "id": mid_v, "type": "video", "path": FINAL_V4.replace("\\", "/"),
        "material_name": "bojomi_talking_head_v4_final.mp4",
        "width": 1080, "height": 1920, "duration": total_us, "has_audio": True
    })
    D["materials"]["videos"].append(vm)

    scene_cuts = [
        (0.00, 3.55), (3.55, 9.15), (9.15, 17.96), (17.96, 25.02),
        (25.02, 28.92), (28.92, 36.05), (36.05, 39.48), (39.48, 42.34),
        (42.34, 54.35), (54.35, 59.18), (59.18, vid_dur)
    ]
    tr0 = copy.deepcopy(vtrack_tpl); tr0["id"] = uid(); tr0["segments"] = []
    for s0, s1 in scene_cuts:
        dur_u = us(s1 - s0)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k in extra_keys:
            em = copy.deepcopy(tmat_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        seg.update({
            "id": uid(), "material_id": mid_v,
            "source_timerange": {"start": us(s0), "duration": dur_u},
            "target_timerange": {"start": us(s0), "duration": dur_u},
            "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": 0
        })
        tr0["segments"].append(seg)
    D["tracks"].append(tr0)

    # 4 Dedicated Multi-Track Audio Stems (Voice, BGM, SFX Transitions/Risers, SFX Pops/Ticks)
    audio_stems = [
        ("01_Voice_Master", vo_wav, 1.0),
        ("02_BGM_Ducked", bgm_wav, 1.0),
        ("03_SFX_Transitions_Risers", trans_wav, 1.0),
        ("04_SFX_Pops_Shutters_Ticks", ui_wav, 1.0),
    ]
    for aname, apath, avol in audio_stems:
        am = copy.deepcopy(amat_tpl)
        aid = uid()
        am.update({
            "id": aid, "type": "extract_music", "name": aname,
            "path": apath.replace("\\", "/"), "duration": total_us
        })
        D["materials"]["audios"].append(am)

        atr = copy.deepcopy(atrack_tpl); atr["id"] = uid(); atr["segments"] = []
        aseg = copy.deepcopy(aseg_tpl)
        arefs = []
        for k in a_extra_keys:
            em = copy.deepcopy(amat_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); arefs.append(em["id"])
        aseg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": 0, "duration": total_us},
            "target_timerange": {"start": 0, "duration": total_us},
            "speed": 1.0, "volume": avol, "last_nonzero_volume": avol,
            "extra_material_refs": arefs, "common_keyframes": [], "keyframe_refs": []
        })
        atr["segments"].append(aseg)
        D["tracks"].append(atr)

    os.makedirs(out_dir, exist_ok=True)
    for aux in ["draft_settings", "draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json", "timeline_layout.json"]:
        sp = os.path.join(tpl_dir, aux)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(out_dir, aux))

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.35", "-i", FINAL_V4, "-frames:v", "1", os.path.join(out_dir, "draft_cover.jpg")], check=True)
    with open(os.path.join(out_dir, "draft_content.json"), "w", encoding="utf-8") as f:
        json.dump(D, f, ensure_ascii=False)

    tl_root = os.path.join(out_dir, "Timelines")
    tl_id = uid()
    tl_sub = os.path.join(tl_root, tl_id)
    os.makedirs(tl_sub, exist_ok=True)
    shutil.copy2(os.path.join(out_dir, "draft_content.json"), os.path.join(tl_sub, "draft_content.json"))
    shutil.copy2(os.path.join(out_dir, "draft_cover.jpg"), os.path.join(tl_sub, "draft_cover.jpg"))

    tp_src = os.path.join(tpl_dir, "Timelines", "project.json")
    if os.path.isfile(tp_src):
        tp = json.load(open(tp_src, encoding="utf-8"))
        now_us = int(time.time() * 1_000_000)
        tp["id"] = uid(); tp["create_time"] = now_us; tp["update_time"] = now_us; tp["main_timeline_id"] = tl_id
        if tp.get("timelines"):
            tp["timelines"] = [tp["timelines"][0]]
            tp["timelines"][0]["id"] = tl_id
            tp["timelines"][0]["create_time"] = now_us; tp["timelines"][0]["update_time"] = now_us
        with open(os.path.join(tl_root, "project.json"), "w", encoding="utf-8") as f:
            json.dump(tp, f, ensure_ascii=False)

    now_us = int(time.time() * 1_000_000)
    M = copy.deepcopy(TM)
    M.update({
        "draft_id": draft_id, "draft_name": out_name,
        "draft_fold_path": out_dir.replace("\\", "/"),
        "draft_root_path": DRAFTS_DIR.replace("\\", "/"),
        "draft_cover": "draft_cover.jpg", "tm_duration": total_us,
        "tm_draft_create": now_us, "tm_draft_modified": now_us, "draft_timeline_materials_size_": 0
    })
    with open(os.path.join(out_dir, "draft_meta_info.json"), "w", encoding="utf-8") as f:
        json.dump(M, f, ensure_ascii=False)
    print("Created Multi-Track CapCut v4 Master Draft:", out_dir)

if __name__ == "__main__":
    vd, vo_w, bgm_w, tr_w, ui_w = build_master_sound_and_video()
    build_capcut_v4_multitrack(vd, vo_w, bgm_w, tr_w, ui_w)
