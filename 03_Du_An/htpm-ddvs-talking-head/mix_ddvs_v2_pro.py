import copy, json, math, os, re, shutil, subprocess, time, uuid, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\htpm-ddvs-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems_v2")
os.makedirs(STEMS_DIR, exist_ok=True)

TLH_BGM_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"
TLH_SFX_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
DRAFTS_DIR   = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")

RAW_VID      = os.path.join(PROJ_DIR, "_ddvs_v2_pro_video_only.mp4")
MAIN_CUT     = os.path.join(AROLL_DIR, "main_cut.mp4")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "htpm_ddvs_talking_head_final.mp4")
DRIVE_FINAL1 = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_DDVS_TALKING_HEAD_FINAL.mp4"
DRIVE_FINAL2 = r"Z:\Drive của tôi\HTPM_DDVS_TALKING_HEAD_FINAL.mp4"
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\HTPM_DDVS_TALKING_HEAD_FINAL.mp4"
DOWNLOAD_OUT = r"C:\Users\Hang thu\Downloads\HTPM_DDVS_TALKING_HEAD_FINAL.mp4"
ARTIFACT_MP4 = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\HTPM_DDVS_TALKING_HEAD_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-ddvs-talking-head"

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

# 100% Curated From User's TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX) — Soft, Natural, Never Noisy!
VO_POCKET_EQ = "equalizer=f=2650:t=q:w=1.15:g=-4.5,lowpass=f=9200"

SFX_SPECS = {
    # Opening Hook "Chan" cue requested by user ("thay bằng sfx chan"):
    "chan_hook":     (tlh_sfx("Drama - Tiếng nhạc chốt ngắn (Chan).mp3"),                0.02, 1.85, "lowpass=f=8500"),
    # Clean, Soft CapCut/TVC Transitions & Text Motion from TLH\Edit:
    "whoosh_tvc":    (tlh_sfx("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"),              0.06, 0.54, VO_POCKET_EQ),
    "whoosh_scene":  (tlh_sfx("Whoosh - Lướt chuyển cảnh cơ bản.mp3"),                   0.22, 0.62, VO_POCKET_EQ),
    "swoosh_light":  (tlh_sfx("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),              0.08, 0.39, VO_POCKET_EQ),
    "whoosh_pip":    (tlh_sfx("Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP).mp3"),    0.04, 0.28, VO_POCKET_EQ),
    "slide_soft":    (tlh_sfx("Slide - Tiếng trượt chữ ngang mượt.mp3"),                 0.05, 0.55, "lowpass=f=6000"),
    # Delicate, Low-Volume UI / Bubble / Reveal Accents (replaces noisy crystal shimmer!):
    "pop_soft":      (tlh_sfx("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),                      0.03, 0.27, VO_POCKET_EQ),
    "pop_tvc":       (tlh_sfx("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"),               0.00, 0.24, VO_POCKET_EQ),
    "notif_subtle":  (tlh_sfx("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"), 0.10, 0.42, VO_POCKET_EQ),
    "ting_clean":    (tlh_sfx("Ting - Chuông Ting nhanh gọn.mp3"),                       0.00, 0.72, "equalizer=f=2800:t=q:w=1.2:g=-4.0,lowpass=f=8800"),
    "magic_soft":    (tlh_sfx("Mở cảnh - Âm thanh tỏa sáng sang trọng (Magic Reveal).mp3"), 0.14, 1.45, "highpass=f=350,equalizer=f=2600:t=q:w=1.1:g=-5.5,lowpass=f=8500"),
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

def build_audio_and_export():
    dur_j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. Warm, Clear Pharmacist Voiceover (-14 LUFS, prominent & crystal clear)
    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3350:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # 2. 2-Half BGM Selected Directly from User's TLH\Edit\01_Nhạc Nền (BGM)
    bgm1_path = os.path.join(TLH_BGM_DIR, r"03_Spa - Thư Giãn - Chữa Lành - Thiên Nhiên\A warm piano solo, a healing solfeggio(1387534) (1p52s).mp3")
    bgm2_path = os.path.join(TLH_BGM_DIR, r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Calm Inspirational Background (4p24s).mp3")
    if not os.path.exists(bgm1_path):
        bgm1_path = os.path.join(TLH_BGM_DIR, r"04_Piano - Buồn - Sâu Lắng - Cảm Xúc\Soft Piano Inspiration01 (4p26s).mp3")
    if not os.path.exists(bgm2_path):
        bgm2_path = os.path.join(TLH_BGM_DIR, r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Corporate Medicine (2p22s).mp3")

    bgm_eq = "highpass=f=85,equalizer=f=2150:t=q:w=1.25:g=-4.8,lowpass=f=12000,loudnorm=I=-14:TP=-1.5:LRA=9"
    b1_raw = decode_stereo_f32(bgm1_path, ss=2.0, dur_limit=45.0, af=bgm_eq)
    b2_raw = decode_stereo_f32(bgm2_path, ss=3.5, dur_limit=45.0, af=bgm_eq)
    b1 = np.tile(b1_raw, ((N // len(b1_raw)) + 2, 1))[:N]
    b2 = np.tile(b2_raw, ((N // len(b2_raw)) + 2, 1))[:N]

    t_axis = np.arange(N, dtype=np.float32) / SR
    xfade = np.clip((t_axis - 38.8) / 2.6, 0.0, 1.0)
    xfade = xfade * xfade * (3.0 - 2.0 * xfade)
    bgm = b1 * (1.0 - xfade[:, None]) + b2 * xfade[:, None]

    # Smooth Lookahead Speech-Envelope Dynamic Ducking
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

    # 3. Clean, Subtle TLH\Edit SFX Choreography (Chan Hook + Soft -17dB..-20dB Accents!)
    bank = load_sfx_bank()
    sfx_trans = np.zeros((N, 2), dtype=np.float32)
    sfx_ui    = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    # A. Opening Hook (0.08s: Clean "Chan" cue instead of goofy whooshes! + gentle text swoosh at 1.32s & 2.08s)
    cues += stamp(sfx_ui,    bank, "chan_hook",    0.10, -14.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_ui,    bank, "swoosh_light", 1.32, -17.5, pan=-0.15)
    cues += stamp(sfx_ui,    bank, "pop_soft",     2.06, -18.0, pan=+0.15)

    # B. Style 2 Diagonal Wipe Cinema (3.48s entry + 8.55s 103-degree diagonal wipe)
    cues += stamp(sfx_trans, bank, "whoosh_tvc",   3.50, -16.8, pan=-0.10)
    cues += stamp(sfx_trans, bank, "whoosh_scene", 8.55, -16.8, pan=+0.10)

    # C. Style 3 Frosted Glassmorphism + Optical Morph (13.70s entry + 19.20s morph)
    cues += stamp(sfx_trans, bank, "whoosh_tvc",   13.72, -17.0, pan=0.0)
    cues += stamp(sfx_ui,    bank, "notif_subtle", 13.80, -19.0, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans, bank, "swoosh_light", 19.20, -17.2, pan=0.0)

    # D. Style 4 Staggered 2-Panel Collage (24.55s Panel 1 + 27.82s Panel 2)
    cues += stamp(sfx_trans, bank, "whoosh_pip",   24.56, -17.0, pan=-0.20)
    cues += stamp(sfx_trans, bank, "whoosh_pip",   27.84, -17.0, pan=+0.20)

    # E. Editorial Brand Bridge #1 (34.22s)
    cues += stamp(sfx_trans, bank, "whoosh_tvc",   34.24, -17.2, pan=0.0)
    cues += stamp(sfx_ui,    bank, "ting_clean",   34.30, -19.2, pan=0.0, align_peak=False)

    # F. Product 1 — Hằng Thu Viên Đặt Showcase (40.20s — QUIET, SOFT, NEVER NOISY!)
    cues += stamp(sfx_trans, bank, "whoosh_tvc",   40.22, -17.5, pan=0.0)
    cues += stamp(sfx_ui,    bank, "magic_soft",   40.28, -20.2, pan=0.0, align_peak=False)
    for bi, (bt, bpan) in enumerate([(42.30, -0.22), (43.65, +0.22), (44.80, -0.22), (45.55, +0.22)]):
        cues += stamp(sfx_ui, bank, "pop_soft" if bi % 2 == 0 else "notif_subtle", bt + 0.06, -19.8, pan=bpan, align_peak=False)

    # G. Product 2 — Romance VIP Showcase (46.80s — QUIET, REFINED, NEVER NOISY!)
    cues += stamp(sfx_trans, bank, "whoosh_tvc",   46.82, -17.5, pan=0.0)
    cues += stamp(sfx_ui,    bank, "magic_soft",   46.88, -20.2, pan=0.0, align_peak=False)
    for bi, (bt, bpan) in enumerate([(47.50, -0.22), (48.62, +0.22), (53.40, -0.22), (55.45, +0.22)]):
        cues += stamp(sfx_ui, bank, "notif_subtle" if bi % 2 == 0 else "pop_soft", bt + 0.06, -19.8, pan=bpan, align_peak=False)

    # H. Romance VIP Brand Card (57.18s) + Finale (60.50s) + Closing Ribbon (62.35s — WHISPER-SOFT!)
    cues += stamp(sfx_trans, bank, "whoosh_tvc",   57.20, -17.5, pan=0.0)
    cues += stamp(sfx_ui,    bank, "ting_clean",   57.26, -19.5, pan=0.0, align_peak=False)
    cues += stamp(sfx_trans, bank, "swoosh_light", 60.50, -17.8, pan=0.0)
    cues += stamp(sfx_ui,    bank, "notif_subtle", 62.35, -19.8, pan=0.0, align_peak=False)

    print(f"Stamped {cues} balanced TLH Edit SFX cues across {vid_dur:.2f}s!")

    sfx_trans = (np.tanh(sfx_trans * 0.95) / 0.95) * 0.82
    sfx_ui    = (np.tanh(sfx_ui * 0.95) / 0.95) * 0.82

    vo_wav    = os.path.join(STEMS_DIR, "01_Voice_Master.wav")
    bgm_wav   = os.path.join(STEMS_DIR, "02_BGM_TLH_2Half.wav")
    trans_wav = os.path.join(STEMS_DIR, "03_SFX_TLH_Transitions.wav")
    ui_wav    = os.path.join(STEMS_DIR, "04_SFX_TLH_Chan_Pop_Ting.wav")
    mix_wav   = os.path.join(STEMS_DIR, "full_mix_pre_lufs.wav")

    save_wav_16(vo_wav, vo)
    save_wav_16(bgm_wav, bgm)
    save_wav_16(trans_wav, sfx_trans)
    save_wav_16(ui_wav, sfx_ui)

    full_mix = vo + bgm + sfx_trans + sfx_ui
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)
    save_wav_16(mix_wav, full_mix)

    pre_mov = os.path.join(PROJ_DIR, "_ddvs_v2_pre_lufs.mov")
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
    print("Saved Local Final:", LOCAL_FINAL)

    for dp in [DRIVE_FINAL1, DRIVE_FINAL2, LOCAL_EXPORT, DOWNLOAD_OUT]:
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copy2(LOCAL_FINAL, dp)
        print("Exported Final:", dp)

    # Also update faststart webview preview inside artifact dir!
    if os.path.exists(os.path.dirname(ARTIFACT_MP4)):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", LOCAL_FINAL,
            "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "copy", "-movflags", "+faststart", ARTIFACT_MP4
        ], check=True)

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", LOCAL_FINAL,
        "-vf", "fps=20/67.6,scale=270:480,tile=5x4",
        "-frames:v", "1", "-q:v", "2", os.path.join(CHECK_DIR, "v3_sheet.jpg")
    ], check=True)

    return vid_dur, vo_wav, bgm_wav, trans_wav, ui_wav

def build_capcut_draft(vid_dur, vo_wav, bgm_wav, trans_wav, ui_wav):
    tpl_dir = os.path.join(DRAFTS_DIR, "LT_PLUS_HangThu_TalkingHead_Final")
    out_name = "HTPM_DDVS_TalkingHead_V2_Pro"
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
        "material_name": "htpm_ddvs_talking_head_final.mp4",
        "width": 1080, "height": 1920, "duration": total_us, "has_audio": True
    })
    D["materials"]["videos"].append(vm)

    scene_cuts = [
        (0.00, 3.45), (3.45, 8.55), (8.55, 13.68), (13.68, 19.20), (19.20, 24.52),
        (24.52, 34.20), (34.20, 40.18), (40.18, 46.78), (46.78, 57.16), (57.16, 60.48), (60.48, vid_dur)
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
        ("02_BGM_TLH_2Half", bgm_wav),
        ("03_SFX_TLH_Transitions", trans_wav),
        ("04_SFX_TLH_Chan_Pop_Ting", ui_wav),
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

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "48.0", "-i", LOCAL_FINAL, "-frames:v", "1", os.path.join(out_dir, "draft_cover.jpg")], check=True)
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
    print("Created CapCut Multi-Track V2 Pro Draft:", out_dir)

    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for fn in ["job.json", "render_ddvs_v2_pro.py", "mix_ddvs_v2_pro.py", "report.md"]:
        fp = os.path.join(PROJ_DIR, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    os.makedirs(os.path.join(DRIVE_PROJ, "check"), exist_ok=True)
    for fn, src_dir in [("main_cut_clean.json", AROLL_DIR), ("v3_sheet.jpg", CHECK_DIR)]:
        fp = os.path.join(src_dir, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, "check" if src_dir == CHECK_DIR else "", fn))
    print("Synced project archive to Google Drive:", DRIVE_PROJ)

if __name__ == "__main__":
    vd, vo_w, bgm_w, tr_w, ui_w = build_audio_and_export()
    build_capcut_draft(vd, vo_w, bgm_w, tr_w, ui_w)
