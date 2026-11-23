import copy, json, math, os, re, shutil, subprocess, time, uuid, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems_v2")
os.makedirs(STEMS_DIR, exist_ok=True)

HF_SFX_DIR      = r"d:\AI\full studio\.agents\skills\media-use\audio\assets\sfx"
STUDIO_SFX_DIR  = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"
TLH_BGM_DIR     = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"
TLH_SFX_DIR     = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
DRAFTS_DIR      = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")

RAW_VID      = os.path.join(PROJ_DIR, "_htpm_lt_v2_video_only.mp4")
MAIN_CUT     = os.path.join(AROLL_DIR, "main_cut.mp4")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "htpm_lt_plus_talking_head_final.mp4")
DRIVE_FINAL1 = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_LT_PLUS_TALKING_HEAD_FINAL.mp4"
DRIVE_FINAL2 = r"Z:\Drive của tôi\HTPM_LT_PLUS_TALKING_HEAD_FINAL.mp4"
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\HTPM_LT_PLUS_TALKING_HEAD_FINAL.mp4"
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

# 100% Professional Commercial TVC + HyperFrames SFX Palette (ZERO cartoon/comedy sounds!)
SFX_SPECS = {
    # HyperFrames Official Bundled SFX (media-use/audio/assets/sfx):
    "hf_whoosh_cine":  (os.path.join(HF_SFX_DIR, "whoosh-cinematic.mp3"), 0.00, 1.10, "lowpass=f=9500"),
    "hf_whoosh":       (os.path.join(HF_SFX_DIR, "whoosh.mp3"),           0.00, 0.65, "lowpass=f=9000"),
    "hf_whoosh_short": (os.path.join(HF_SFX_DIR, "whoosh-short.mp3"),     0.00, 0.42, "lowpass=f=8500"),
    "hf_riser":        (os.path.join(HF_SFX_DIR, "riser.mp3"),            0.00, 1.35, "lowpass=f=10000"),
    "hf_sparkle":      (os.path.join(HF_SFX_DIR, "sparkle.mp3"),          0.00, 1.50, "highpass=f=600"),
    "hf_chime":        (os.path.join(HF_SFX_DIR, "chime.mp3"),            0.00, 1.40, None),
    "hf_ping":         (os.path.join(HF_SFX_DIR, "ping.mp3"),             0.00, 0.90, "lowpass=f=7500"),
    # User's TLH Folder — Strictly Clean Commercial TVC Transitions & Subtle Aquatic Texture:
    "tlh_whoosh_tvc":  (tlh_sfx("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"), 0.02, 0.58, None),
    "tlh_swoosh":      (tlh_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"), 0.02, 0.44, None),
    "tlh_slide_soft":  (tlh_sfx("Slide - Tiếng trượt chữ ngang mượt.mp3"),     0.05, 0.62, "lowpass=f=6500"),
    "tlh_water_silk":  (tlh_sfx("Đời Thường & ASMR - 水声75 (2s).mp3"),        0.10, 0.95, "highpass=f=280,lowpass=f=5800"),
    # Luxury Studio Shimmer:
    "st_shimmer":      (os.path.join(STUDIO_SFX_DIR, "sfx_crystal_shimmer.mp3"), 0.00, 1.65, None),
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
        n_in = min(len(arr) // 4, int(0.012 * SR))
        n_out = min(len(arr) // 3, int(0.055 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
    print(f"Loaded {len(bank)} Agency-Grade HyperFrames + TLH TVC SFX instruments.")
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
    dur_j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. Warm, Clear Pharmacist Voiceover (-14 LUFS)
    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3350:t=q:w=1.2:g=1.5,loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # 2. 2-Half BGM Selected Directly from User's TLH\Edit\01_Nhạc Nền (BGM)!
    # Half 1 (0..30.8s): Soft Piano Inspiration01 (warm empathetic medical reassurance)
    # Half 2 (30.8..59.2s): Corporate Medicine (clean, uplifting, trustworthy pharmaceutical commercial!)
    bgm1_path = os.path.join(TLH_BGM_DIR, r"04_Piano - Buồn - Sâu Lắng - Cảm Xúc\Soft Piano Inspiration01 (4p26s).mp3")
    bgm2_path = os.path.join(TLH_BGM_DIR, r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Corporate Medicine (2p22s).mp3")

    bgm_eq = "highpass=f=85,equalizer=f=2150:t=q:w=1.25:g=-4.5,lowpass=f=12000,loudnorm=I=-14:TP=-1.5:LRA=9"
    # Skip any leading silence so music flows immediately from 0.0s
    b1_raw = decode_stereo_f32(bgm1_path, ss=2.5, dur_limit=40.0, af=bgm_eq)
    b2_raw = decode_stereo_f32(bgm2_path, ss=4.0, dur_limit=40.0, af=bgm_eq)
    b1 = np.tile(b1_raw, ((N // len(b1_raw)) + 2, 1))[:N]
    b2 = np.tile(b2_raw, ((N // len(b2_raw)) + 2, 1))[:N]

    t_axis = np.arange(N, dtype=np.float32) / SR
    # Silky 2.6s crossfade at 29.6s -> 32.2s as LT PLUS Hằng Thu enters!
    xfade = np.clip((t_axis - 29.6) / 2.6, 0.0, 1.0)
    xfade = xfade * xfade * (3.0 - 2.0 * xfade)
    bgm = b1 * (1.0 - xfade[:, None]) + b2 * xfade[:, None]

    # Smooth Lookahead Speech-Envelope Dynamic Ducking (0.26 under speech; swells gently to 0.46 on pauses & finale)
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

    # 3. Refined, Subtle, Broadcast-Grade SFX (HyperFrames + TLH Commercial TVC)
    bank = load_sfx_bank()
    sfx_trans   = np.zeros((N, 2), dtype=np.float32)
    sfx_shimmer = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    # A. Subtle Editorial Hook Opening (0.08 - 2.35s)
    cues += stamp(sfx_trans,   bank, "hf_whoosh_cine",  0.10, -13.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "tlh_swoosh",      1.12, -13.0, pan=-0.15)
    cues += stamp(sfx_trans,   bank, "hf_whoosh_short", 1.52, -14.0, pan=+0.15)
    cues += stamp(sfx_shimmer, bank, "hf_chime",        2.32, -15.5, pan=0.0, align_peak=False)

    # B. Multi-Style Overlay Scene Transitions (Silky & Understated!)
    # Style 2: Office Discomfort (3.98s) -> Diagonal Wipe into Evening Bedroom (7.15s)
    cues += stamp(sfx_trans, bank, "tlh_whoosh_tvc",  4.02, -11.5, pan=-0.12)
    cues += stamp(sfx_trans, bank, "hf_whoosh",       7.12, -12.0, pan=+0.12)

    # Bridge #1 ("HIỂU ĐÚNG" 10.76s)
    cues += stamp(sfx_shimmer, bank, "hf_chime",      10.80, -13.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "tlh_swoosh",    10.82, -13.0, pan=0.0)

    # Style 3: Glassmorphism 3D Cells (12.95s) -> Optical Morph into Doctor Reassuring Patient (17.05s)
    cues += stamp(sfx_trans,   bank, "hf_whoosh_cine",13.00, -12.0, pan=0.0)
    cues += stamp(sfx_shimmer, bank, "hf_sparkle",    17.05, -14.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "tlh_swoosh",    17.06, -12.5, pan=0.0)

    # Style 4: Staggered Dual-Panel Split Collage (23.20s Doctor + 26.75s Lab Microscope)
    cues += stamp(sfx_trans, bank, "tlh_whoosh_tvc",  23.24, -11.8, pan=-0.20)
    cues += stamp(sfx_trans, bank, "hf_whoosh_short", 26.78, -12.0, pan=+0.22)

    # Style 1B: LT PLUS Hằng Thu Glossy White Probiotic Cream Reveal (30.84s)
    cues += stamp(sfx_trans,   bank, "hf_riser",       29.85, -15.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "hf_whoosh_cine", 30.88, -11.0, pan=0.0)
    cues += stamp(sfx_shimmer, bank, "st_shimmer",     30.92, -12.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_shimmer, bank, "tlh_water_silk", 31.10, -18.5, pan=0.0, align_peak=False)

    # 6 Rising Iridescent Pearl Herb Bubbles (33.66..37.70s) — delicate harmonic glass & silky water!
    bubble_times = [
        (33.66, -0.28), (34.68, +0.28), (35.12, -0.30),
        (36.16, +0.30), (37.00, -0.25), (37.70, +0.25)
    ]
    for idx_b, (bt, bpan) in enumerate(bubble_times):
        cues += stamp(sfx_trans,   bank, "tlh_slide_soft", bt + 0.04, -15.5, pan=bpan)
        cues += stamp(sfx_shimmer, bank, "hf_ping",        bt + 0.12, -16.0, pan=bpan, align_peak=False)
        if idx_b in (0, 3):
            cues += stamp(sfx_shimmer, bank, "tlh_water_silk", bt + 0.05, -19.5, pan=bpan, align_peak=False)
    cues += stamp(sfx_shimmer, bank, "hf_sparkle", 38.45, -13.5, pan=0.0, align_peak=False)

    # Bridge #2 (41.60s) -> Style 5 Luxury Sunlit Silk & Crystal Pedestal LT PLUS Showcase (45.88s)
    cues += stamp(sfx_trans,   bank, "tlh_swoosh",     41.64, -12.8, pan=0.0)
    cues += stamp(sfx_trans,   bank, "hf_riser",       44.95, -15.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans,   bank, "hf_whoosh_cine", 45.90, -11.2, pan=0.0)
    cues += stamp(sfx_shimmer, bank, "st_shimmer",     45.95, -11.5, pan=0.0, align_peak=False)

    # Closing Authentic LT PLUS HẰNG THU Brand Finale (50.20s & CTA 53.95s)
    cues += stamp(sfx_trans,   bank, "tlh_whoosh_tvc", 50.24, -12.0, pan=0.0)
    cues += stamp(sfx_shimmer, bank, "hf_chime",       50.28, -13.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_shimmer, bank, "hf_sparkle",     54.00, -13.2, pan=0.0, align_peak=False)

    print(f"Stamped {cues} refined Agency HyperFrames + TLH TVC SFX cues across {vid_dur:.2f}s!")

    sfx_trans   = (np.tanh(sfx_trans * 0.95) / 0.95) * 0.85
    sfx_shimmer = (np.tanh(sfx_shimmer * 0.95) / 0.95) * 0.85

    vo_wav      = os.path.join(STEMS_DIR, "01_Voice_Master.wav")
    bgm_wav     = os.path.join(STEMS_DIR, "02_BGM_TLH_2Half_Pro.wav")
    trans_wav   = os.path.join(STEMS_DIR, "03_SFX_HyperFrames_Transitions.wav")
    shimmer_wav = os.path.join(STEMS_DIR, "04_SFX_Luxury_Shimmers_TLH.wav")
    mix_wav     = os.path.join(STEMS_DIR, "full_mix_v2_pre_lufs.wav")

    save_wav_16(vo_wav, vo)
    save_wav_16(bgm_wav, bgm)
    save_wav_16(trans_wav, sfx_trans)
    save_wav_16(shimmer_wav, sfx_shimmer)

    full_mix = vo + bgm + sfx_trans + sfx_shimmer
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)
    save_wav_16(mix_wav, full_mix)

    pre_mov = os.path.join(PROJ_DIR, "_htpm_lt_v2_pre_lufs.mov")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", RAW_VID, "-i", mix_wav,
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "pcm_s16le", pre_mov
    ], check=True)

    # 2-pass EBU R128 loudnorm -> exact -14.0 LUFS!
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
    print("Saved Local Final:", LOCAL_FINAL)

    for dp in [DRIVE_FINAL1, DRIVE_FINAL2, LOCAL_EXPORT]:
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copy2(LOCAL_FINAL, dp)
        print("Exported copy:", dp)

    shutil.copy2(
        r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\Montserrat-Bold.ttf",
        os.path.join(CHECK_DIR, "_f.ttf")
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", LOCAL_FINAL,
        "-vf", "fps=1/2.96,scale=270:480,drawtext=fontfile=_f.ttf:text='%{pts\\:hms}':fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.65:x=8:y=8,tile=5x4",
        "-frames:v", "1", os.path.join(CHECK_DIR, "v3_sheet.jpg")
    ], cwd=CHECK_DIR, check=True)

    return vid_dur, vo_wav, bgm_wav, trans_wav, shimmer_wav

def find_donor_draft():
    for name in os.listdir(DRAFTS_DIR):
        if name == "HTPM_LT_PLUS_TalkingHead_Cute_Final":
            continue
        p = os.path.join(DRAFTS_DIR, name)
        dc = os.path.join(p, "draft_content.json")
        dm = os.path.join(p, "draft_meta_info.json")
        if os.path.isfile(dc) and os.path.isfile(dm):
            try:
                j = json.load(open(dc, encoding="utf-8"))
                t_types = {tr.get("type") for tr in j.get("tracks", []) if tr.get("segments")}
                if "video" in t_types and "audio" in t_types:
                    return p
            except Exception:
                pass
    raise RuntimeError("No valid CapCut donor draft found!")

def build_capcut_draft(vid_dur, vo_wav, bgm_wav, trans_wav, shimmer_wav):
    tpl_dir = find_donor_draft()
    out_name = "HTPM_LT_PLUS_TalkingHead_Pro_Final"
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

    vm = copy.deepcopy(vmat_tpl)
    mid_v = uid()
    vm.update({
        "id": mid_v, "type": "video", "path": LOCAL_FINAL.replace("\\", "/"),
        "material_name": "htpm_lt_plus_talking_head_final.mp4",
        "width": 1080, "height": 1920, "duration": total_us, "has_audio": True
    })
    D["materials"]["videos"].append(vm)

    scene_cuts = [
        (0.00, 3.98), (3.98, 7.15), (7.15, 10.76), (10.76, 12.95),
        (12.95, 17.05), (17.05, 23.20), (23.20, 26.75), (26.75, 30.84),
        (30.84, 41.60), (41.60, 45.88), (45.88, 50.20), (50.20, vid_dur)
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

    for aname, apath in [
        ("01_Voice_Master", vo_wav),
        ("02_BGM_TLH_2Half_Pro", bgm_wav),
        ("03_SFX_HyperFrames_Transitions", trans_wav),
        ("04_SFX_Luxury_Shimmers_TLH", shimmer_wav),
    ]:
        am = copy.deepcopy(amat_tpl); aid = uid()
        am.update({"id": aid, "type": "extract_music", "name": aname, "path": apath.replace("\\", "/"), "duration": total_us})
        D["materials"]["audios"].append(am)
        atr = copy.deepcopy(atrack_tpl); atr["id"] = uid(); atr["segments"] = []
        aseg = copy.deepcopy(aseg_tpl); arefs = []
        for k in a_extra_keys:
            em = copy.deepcopy(amat_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); arefs.append(em["id"])
        aseg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": 0, "duration": total_us},
            "target_timerange": {"start": 0, "duration": total_us},
            "speed": 1.0, "volume": 1.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": arefs, "common_keyframes": [], "keyframe_refs": []
        })
        atr["segments"].append(aseg)
        D["tracks"].append(atr)

    os.makedirs(out_dir, exist_ok=True)
    for aux in ["draft_settings", "draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json", "timeline_layout.json"]:
        sp = os.path.join(tpl_dir, aux)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(out_dir, aux))

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.60", "-i", LOCAL_FINAL, "-frames:v", "1", os.path.join(out_dir, "draft_cover.jpg")], check=True)
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
    print("Created CapCut Multi-Track Pro Draft:", out_dir)

    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for fn in ["job.json", "gen_v2_pro_assets.py", "render_v2_pro.py", "mix_v2_pro.py", "report.md"]:
        fp = os.path.join(PROJ_DIR, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    for fn, src_dir in [("main_cut_clean.json", AROLL_DIR), ("v3_sheet.jpg", CHECK_DIR), ("v2_videos_qc.jpg", CHECK_DIR), ("v2_pro_test_grid.jpg", CHECK_DIR)]:
        fp = os.path.join(src_dir, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    print("Synced V2 Pro archive to Google Drive:", DRIVE_PROJ)

if __name__ == "__main__":
    vd, vo_w, bgm_w, tr_w, sh_w = build_audio_and_export()
    build_capcut_draft(vd, vo_w, bgm_w, tr_w, sh_w)
