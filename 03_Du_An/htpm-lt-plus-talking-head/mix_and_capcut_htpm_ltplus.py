import copy, json, math, os, re, shutil, subprocess, time, uuid, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
os.makedirs(STEMS_DIR, exist_ok=True)

SKILL_AUDIO_DIR = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"
TLH_SFX_DIR     = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
DRAFTS_DIR      = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")

RAW_VID      = os.path.join(PROJ_DIR, "_htpm_lt_video_only.mp4")
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
def tlh_path(fname):
    return TLH_INDEX.get(fname, os.path.join(TLH_SFX_DIR, fname))

SFX_SPECS = {
    # From User's TLH SFX Folder:
    "tlh_star_open": (tlh_path("Mở cảnh - Tiếng chuông sao lung linh.mp3"), 0.00, 1.80, None),
    "tlh_pop1":      (tlh_path("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"), 0.00, 0.38, None),
    "tlh_pop2":      (tlh_path("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"), 0.00, 0.32, None),
    "tlh_boing":     (tlh_path("Hoạt hình - Lò xo nảy Boing Boing.mp3"), 0.00, 0.55, "lowpass=f=3600"),
    "tlh_ting":      (tlh_path("Ting - Chuông Ting nảy ý tưởng.mp3"), 0.00, 1.20, None),
    "tlh_notif":     (tlh_path("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"), 0.00, 0.55, None),
    "tlh_slide_up":  (tlh_path("Slide - Tiếng trượt chữ bay lên.mp3"), 0.15, 0.75, "highpass=f=180"),
    "tlh_slide_h":   (tlh_path("Slide - Tiếng trượt chữ ngang mượt.mp3"), 0.05, 0.65, None),
    "tlh_swoosh":    (tlh_path("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"), 0.02, 0.42, None),
    "tlh_whoosh_tvc":(tlh_path("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"), 0.02, 0.55, None),
    "tlh_plip":      (tlh_path("UI - Tiếng chạm màn hình cảm ứng Plip Plip.mp3"), 0.02, 0.45, None),
    # From Skill Studio SFX Folder:
    "sk_pop":        (os.path.join(SKILL_AUDIO_DIR, "sfx_pop_clean.mp3"), 0.00, 0.45, None),
    "sk_sparkle":    (os.path.join(SKILL_AUDIO_DIR, "sfx_sparkle_shine.mp3"), 0.00, 1.50, None),
    "sk_shimmer":    (os.path.join(SKILL_AUDIO_DIR, "sfx_crystal_shimmer.mp3"), 0.00, 1.60, None),
    "sk_chime":      (os.path.join(SKILL_AUDIO_DIR, "sfx_chime_warm.mp3"), 0.00, 1.40, None),
    "sk_click":      (os.path.join(SKILL_AUDIO_DIR, "sfx_click_soft.mp3"), 0.02, 0.12, "highpass=f=400"),
    "sk_whoosh":     (os.path.join(SKILL_AUDIO_DIR, "sfx_whoosh_soft.mp3"), 0.00, 0.55, None),
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
        n_in = min(len(arr) // 4, int(0.006 * SR))
        n_out = min(len(arr) // 3, int(0.035 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
    print(f"Loaded {len(bank)} curated Cute TLH + Skill SFX instruments.")
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
    from render_htpm_ltplus_cute import BEHIND_VID_SPANS, CUTE_HEADLINES, STICKER_PLACES, load_captions_htpmlt

    dur_j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(dur_j["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. Warm, Clear Pharmacist Voiceover (-14 LUFS)
    vo = decode_stereo_f32(MAIN_CUT, dur_limit=vid_dur, af="highpass=f=80,equalizer=f=3400:t=q:w=1.2:g=1.6,loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # 2. 2-Half C-Major Cute BGM (Warm Fretless 0..30.6s -> Bright Cheerful Riley 30.6..59.2s when LT PLUS enters!)
    bgm_eq = "highpass=f=85,equalizer=f=2100:t=q:w=1.25:g=-4.2,lowpass=f=12500,loudnorm=I=-14:TP=-1.5:LRA=9"
    b1_raw = decode_stereo_f32(os.path.join(SKILL_AUDIO_DIR, "bgm_warm_fretless.mp3"), af=bgm_eq)
    b2_raw = decode_stereo_f32(os.path.join(SKILL_AUDIO_DIR, "bgm_bright_riley.mp3"), af=bgm_eq)
    b1 = np.tile(b1_raw, ((N // len(b1_raw)) + 2, 1))[:N]
    b2 = np.tile(b2_raw, ((N // len(b2_raw)) + 2, 1))[:N]

    t_axis = np.arange(N, dtype=np.float32) / SR
    xfade = np.clip((t_axis - 29.8) / 2.0, 0.0, 1.0)
    xfade = xfade * xfade * (3.0 - 2.0 * xfade)
    bgm = b1 * (1.0 - xfade[:, None]) + b2 * xfade[:, None]

    # Lookahead Speech-Envelope Dynamic Ducking
    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.022).astype(np.float32)

    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 20):min(n_hops, i_h + 28)] = 1.0
    win_sm = np.hanning(39).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (19, 19), mode="edge"), win_sm, mode="valid")[:n_hops]
    gain_hop = 0.48 * (1.0 - sp_sm) + 0.285 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)
    bgm_env *= np.clip(t_axis / 0.7, 0.0, 1.0) * np.clip((vid_dur - t_axis) / 1.8, 0.0, 1.0)
    bgm *= bgm_env[:, None]

    # 3. Balanced Cute TLH + Skill SFX Mix
    bank = load_sfx_bank()
    sfx_trans = np.zeros((N, 2), dtype=np.float32)
    sfx_cute  = np.zeros((N, 2), dtype=np.float32)
    cues = 0

    # A. Cute Hook Opening & Bouncy Typography (0.06 - 3.78s)
    cues += stamp(sfx_trans, bank, "tlh_star_open", 0.06, -9.5,  pan=0.0, align_peak=False)
    cues += stamp(sfx_cute,  bank, "tlh_pop2",      0.10, -7.8,  pan=0.0)
    cues += stamp(sfx_cute,  bank, "tlh_boing",     1.08, -11.5, pan=-0.20, align_peak=False)
    cues += stamp(sfx_cute,  bank, "tlh_pop1",      1.48, -7.2,  pan=+0.22)
    cues += stamp(sfx_trans, bank, "tlh_swoosh",    2.28, -9.0,  pan=0.0)

    # B. All 8 Cute ChatGPT 3D Stickers (Overhead Rainbow Arc + Body Stickers)
    for idx_s, (skey, t0, t1, cx, cy, sz, rot, _) in enumerate(STICKER_PLACES):
        pan_s = (cx - 540.0) / 680.0
        if cy < 400:
            cues += stamp(sfx_cute, bank, "tlh_pop1", t0 + 0.06, -6.5, pan=pan_s)
        else:
            cues += stamp(sfx_cute, bank, "tlh_slide_up", t0 + 0.08, -11.5, pan=pan_s, align_peak=False)
            pk = "tlh_notif" if idx_s % 2 == 0 else "sk_pop"
            cues += stamp(sfx_cute, bank, pk, t0 + 0.12, -7.8, pan=pan_s)

    # C. Dynamic Behind-Speaker Video Windows Entering & Exiting Smoothly
    for idx_v, (st, en, vkey, _, _) in enumerate(BEHIND_VID_SPANS):
        w_in = "tlh_whoosh_tvc" if idx_v % 2 == 0 else "sk_whoosh"
        cues += stamp(sfx_trans, bank, w_in, st + 0.08, -7.8, pan=0.0)
        if vkey.startswith("ltplus_real"):
            cues += stamp(sfx_trans, bank, "sk_sparkle", st + 0.12, -8.6, pan=0.0, align_peak=False)
        cues += stamp(sfx_trans, bank, "tlh_swoosh", en - 0.04, -9.8, pan=0.0)

    # D. 6 Cute Symmetric Ingredient Pills Popping Left/Right (33.68..37.72s)
    pill_cues = [
        (33.68, -0.32), (34.70, +0.32), (35.14, -0.32),
        (36.18, +0.32), (37.02, -0.32), (37.72, +0.32)
    ]
    for idx_p, (pt, ppan) in enumerate(pill_cues):
        cues += stamp(sfx_cute, bank, "tlh_slide_h", pt + 0.04, -10.8, pan=ppan)
        cues += stamp(sfx_cute, bank, "tlh_pop1" if idx_p % 2 == 0 else "tlh_plip", pt + 0.08, -7.8, pan=ppan)
    cues += stamp(sfx_cute, bank, "tlh_ting", 38.65, -9.2, pan=0.0, align_peak=False)

    # E. Cute Overhead Headlines & Finale CTA Sparkle
    for _, t0, t1, _, _, _ in CUTE_HEADLINES:
        cues += stamp(sfx_cute, bank, "sk_chime", t0 + 0.05, -9.0, pan=0.0, align_peak=False)
        cues += stamp(sfx_cute, bank, "tlh_pop2", t0 + 0.06, -8.0, pan=0.0)
    cues += stamp(sfx_trans, bank, "sk_shimmer", 54.00, -8.5, pan=0.0, align_peak=False)

    # F. Subtle Soft Phrase-Opening Ticks & Emphasis Word Pops
    cap_groups, _, _, STROKE_UP_WORDS = load_captions_htpmlt()
    last_t = -1.0
    for g in cap_groups:
        g_t0 = g["t0"]
        if (g_t0 - last_t) >= 0.85:
            cues += stamp(sfx_cute, bank, "sk_click", g_t0 + 0.02, -16.5, pan=0.0)
            last_t = g_t0
        for ln in g["lines"]:
            for wtxt, ws, we in ln:
                if wtxt in STROKE_UP_WORDS:
                    cues += stamp(sfx_cute, bank, "tlh_pop2", ws + 0.03, -8.5, pan=0.0)

    print(f"Stamped {cues} balanced Cute TLH + Skill SFX cues across {vid_dur:.2f}s!")

    sfx_trans = (np.tanh(sfx_trans * 0.95) / 0.95) * 0.85
    sfx_cute  = (np.tanh(sfx_cute * 0.95) / 0.95) * 0.85

    vo_wav    = os.path.join(STEMS_DIR, "01_Voice_Master.wav")
    bgm_wav   = os.path.join(STEMS_DIR, "02_BGM_Cute_2Half.wav")
    trans_wav = os.path.join(STEMS_DIR, "03_SFX_Transitions_Sparkles.wav")
    cute_wav  = os.path.join(STEMS_DIR, "04_SFX_Cute_Pops_TLH.wav")
    mix_wav   = os.path.join(STEMS_DIR, "full_mix_pre_lufs.wav")

    save_wav_16(vo_wav, vo)
    save_wav_16(bgm_wav, bgm)
    save_wav_16(trans_wav, sfx_trans)
    save_wav_16(cute_wav, sfx_cute)

    full_mix = vo + bgm + sfx_trans + sfx_cute
    pk_m = float(np.max(np.abs(full_mix)))
    if pk_m > 0.96:
        full_mix *= (0.96 / pk_m)
    save_wav_16(mix_wav, full_mix)

    pre_mov = os.path.join(PROJ_DIR, "_htpm_lt_pre_lufs.mov")
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
        r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf",
        os.path.join(CHECK_DIR, "_f.otf")
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", LOCAL_FINAL,
        "-vf", "fps=1/2.96,scale=270:480,drawtext=fontfile=_f.otf:text='%{pts\\:hms}':fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.65:x=8:y=8,tile=5x4",
        "-frames:v", "1", os.path.join(CHECK_DIR, "v3_sheet.jpg")
    ], cwd=CHECK_DIR, check=True)

    return vid_dur, vo_wav, bgm_wav, trans_wav, cute_wav

def find_donor_draft():
    preferred = ["HTPM_AV_TalkingHead_Cute_Final", "LT_PLUS_HangThu_TalkingHead_Final"]
    for name in preferred:
        p = os.path.join(DRAFTS_DIR, name)
        if os.path.isfile(os.path.join(p, "draft_content.json")) and os.path.isfile(os.path.join(p, "draft_meta_info.json")):
            return p
    for name in os.listdir(DRAFTS_DIR):
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

def build_capcut_draft(vid_dur, vo_wav, bgm_wav, trans_wav, cute_wav):
    tpl_dir = find_donor_draft()
    out_name = "HTPM_LT_PLUS_TalkingHead_Cute_Final"
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
        (0.00, 3.98), (3.98, 10.82), (10.82, 13.06), (13.06, 23.22),
        (23.22, 30.84), (30.84, 33.68), (33.68, 41.62), (41.62, 45.92),
        (45.92, 50.18), (50.18, vid_dur)
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
        ("02_BGM_Cute_2Half", bgm_wav),
        ("03_SFX_Transitions_Sparkles", trans_wav),
        ("04_SFX_Cute_Pops_TLH", cute_wav),
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

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.45", "-i", LOCAL_FINAL, "-frames:v", "1", os.path.join(out_dir, "draft_cover.jpg")], check=True)
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
    print("Created CapCut Multi-Track Draft:", out_dir)

    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for fn in ["job.json", "prep_aroll_ltplus.py", "gen_htpm_ltplus_assets.py", "render_htpm_ltplus_cute.py", "mix_and_capcut_htpm_ltplus.py", "report.md"]:
        fp = os.path.join(PROJ_DIR, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    for fn, src_dir in [("main_cut_clean.json", AROLL_DIR), ("main_cut_clean.txt", AROLL_DIR), ("v3_sheet.jpg", CHECK_DIR), ("icons_qc.jpg", CHECK_DIR), ("brolls_qc.jpg", CHECK_DIR)]:
        fp = os.path.join(src_dir, fn)
        if os.path.exists(fp):
            shutil.copy2(fp, os.path.join(DRIVE_PROJ, fn))
    print("Synced project archive to Google Drive:", DRIVE_PROJ)

if __name__ == "__main__":
    vd, vo_w, bgm_w, tr_w, cu_w = build_audio_and_export()
    build_capcut_draft(vd, vo_w, bgm_w, tr_w, cu_w)
