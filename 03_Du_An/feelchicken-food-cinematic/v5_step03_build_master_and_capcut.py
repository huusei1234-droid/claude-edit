import copy, json, math, os, re, shutil, subprocess, sys, time, uuid
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

OUT_DIR    = r"d:\AI\full studio\output\feelchicken-food-cinematic"
VID_V5     = os.path.join(OUT_DIR, "ai_v5_flow_vs_muse")
REF_DIR    = os.path.join(OUT_DIR, "refs_v3_real_dishes")
RAW_V2     = os.path.join(OUT_DIR, "raw_v2")
RAW_V1     = os.path.join(OUT_DIR, "raw_cache")
SFX_V1     = os.path.join(RAW_V1, "sfx")
SFX_V2     = os.path.join(RAW_V2, "sfx")
SHOTS_V5   = os.path.join(OUT_DIR, "shots_v5_ungraded")
TITLE_V5   = os.path.join(OUT_DIR, "titles_v5_signboard")
AUDIO_V5   = os.path.join(OUT_DIR, "audio_v5")
CHK_V5     = os.path.join(OUT_DIR, "check_v5")
STAGE_V5   = os.path.join(OUT_DIR, "capcut_stage_v5")
ART_DIR    = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ  = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-food-cinematic"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_Food_Cinematic_Pro"
DRAFT_ID   = "F94A82E1-63D4-4B89-9E12-7745C280B3A9"

for d in (SHOTS_V5, TITLE_V5, AUDIO_V5, CHK_V5, STAGE_V5, CLOUD_PRJ):
    os.makedirs(d, exist_ok=True)

W, H = 1080, 1920
FPS = 30
SR  = 48000
DUR = 27.60
N_SAMPLES = int(round(DUR * SR))
BGM_LOCAL = os.path.join(RAW_V2, "BGM_Slow_Cook_Honey.mp3")

# ==============================================================================
# 16 VERIFIED HYPER-REALISTIC SHOTS (FLOW + MUSE + REAL SONY 60FPS, 0% COLOR GRADE!)
# ==============================================================================
# Tuple: (id, tl_start, tl_end, folder, filename, src_start, src_window_dur, ramp_mode, zoom_end, overscan_w, overscan_h)
# Note: Google Flow 720p downloads use overscan 1230x2186 (1.14x) so center crop cleanly trims the tiny corner badge!
V5_SHOTS = [
    # Act 1: Ignition, Clean Stainless Flour Bowl, Clean Feel Chicken Fryer & Crispy Basket Lift (0.00 - 7.35s)
    ("S01_stove_ignite",      0.00,  1.20, RAW_V2,  "m01_stove_knob.MP4",             1.55, 1.80, "ramp_in",   1.05, 1166, 2074),
    ("S02_flour_bowl_flow",   1.20,  2.75, VID_V5,  "SC01_flour_bowl_FLOW.mp4",       0.12, 3.60, "ramp_mid",  1.04, 1296, 2304),
    ("S03_steel_whisk",       2.75,  3.90, RAW_V2,  "m03b_whisk_top.MP4",             1.30, 1.90, "ramp_mid",  1.05, 1166, 2074),
    ("S04_clean_fryer_flow",  3.90,  5.45, VID_V5,  "SC02_clean_fryer_FLOW.mp4",      0.10, 3.70, "ramp_in",   1.04, 1296, 2304),
    ("S05_crispy_lift_flow",  5.45,  7.35, VID_V5,  "SC03_crispy_lift_FLOW.mp4",      0.10, 3.75, "ramp_in",   1.04, 1296, 2304),

    # Act 2: Simmering Korean Sauces & Authentic Real-Photo Sauce Cup Pours (7.35 - 16.00s)
    ("S06_red_sauce_simmer",  7.35,  8.65, RAW_V2,  "m11_pan_red_simmer.MP4",         3.10, 1.90, "ramp_mid",  1.05, 1166, 2074),
    ("S07_cheese_velvet_pan", 8.65, 10.10, RAW_V2,  "m12_pan_cheese_vel.MP4",         1.20, 2.00, "ramp_mid",  1.05, 1166, 2074),
    ("S08_ruby_pour_flow",   10.10, 12.35, VID_V5,  "SC04_ruby_pour_FLOW.mp4",        0.05, 3.80, "ramp_mid",  1.04, 1296, 2304),
    ("S09_cheddar_pour_muse",12.35, 14.60, VID_V5,  "SC05_cheddar_pour_MUSE.mp4",     0.08, 3.75, "ramp_mid",  1.04, 1166, 2074),
    ("S10_real_sesame_glaze",14.60, 16.00, RAW_V2,  "m19_sesame_plate.MP4",           1.00, 1.90, "slow_pure", 1.04, 1166, 2074),

    # Act 3: Authentic Clear-Glove Tear, Korean Noodles/Tokbokki & 5-Flavor Platter (16.00 - 24.60s)
    ("S11_clear_tear_muse",  16.00, 18.45, VID_V5,  "SC06_clear_tear_MUSE.mp4",       0.08, 3.75, "ramp_in",   1.04, 1166, 2074),
    ("S12_real_jajang_lift", 18.45, 20.15, RAW_V2,  "m25_jajang_lift.MP4",            1.15, 2.30, "ramp_mid",  1.05, 1166, 2074),
    ("S13_real_tokbokki",    20.15, 21.60, RAW_V2,  "m23_tokbokki_lift.MP4",         21.60, 2.10, "ramp_mid",  1.05, 1166, 2074),
    ("S14_nguvi_orbit_muse", 21.60, 23.25, VID_V5,  "SC07_nguvi_orbit_MUSE.mp4",      0.08, 3.75, "ramp_in",   1.04, 1166, 2074),
    ("S15_real_hero_glide",  23.25, 24.60, RAW_V2,  "m27_hero_macro1.MOV",            0.60, 2.00, "slow_pure", 1.04, 1166, 2074),

    # Act 4: CS1 Storefront Gimbal Walk-In + Signboard End-Card (24.60 - 27.60s)
    ("S16_cs1_walkin",       24.60, 27.60, REF_DIR, "DJI_20251201150558_0312_D.MP4",  4.35, 3.40, "steady",    1.02, 1120, 1992),
]

def build_speed_ramp_map(n_out: int, avail_src_s: float, mode: str) -> np.ndarray:
    u = np.linspace(0.0, 1.0, n_out)
    if mode == "ramp_mid":
        spd = 0.52 + 1.60 * ((2.0 * np.abs(u - 0.5)) ** 2.2)
    elif mode == "ramp_in":
        spd = 0.56 + 1.75 * (np.maximum(0.0, 1.0 - u / 0.32) ** 2.0)
    elif mode == "slow_pure":
        spd = np.full_like(u, 0.58)
    else:
        spd = np.full_like(u, 0.88)

    dt_src = spd / float(FPS)
    cum_t = np.cumsum(dt_src) - dt_src[0]
    max_allow = max(0.5, avail_src_s - 0.10)
    if cum_t[-1] > max_allow:
        cum_t *= (max_allow / cum_t[-1])
    return cum_t

def render_ungraded_shot(idx_s):
    idx, (sid, t0, t1, fld, fn, s0, win_dur, rmode, z_end, w_ov, h_ov) = idx_s
    f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    n_out = f1 - f0
    src_p = os.path.join(fld, fn)
    out_p = os.path.join(SHOTS_V5, f"{idx+1:02d}_{sid}.mp4")

    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", src_p], capture_output=True, text=True, check=True)
    tot_src_dur = float(pr.stdout.strip() or 4.0)
    s0_safe = min(s0, max(0.0, tot_src_dur - 0.6))
    read_dur = min(win_dur, max(0.5, tot_src_dur - s0_safe))

    dec_fps = 60.0
    dec_cmd = [
        "ffmpeg", "-v", "error", "-ss", f"{s0_safe:.3f}", "-t", f"{read_dur:.3f}", "-i", src_p,
        "-vf", f"fps={int(dec_fps)},scale={w_ov}:{h_ov}:force_original_aspect_ratio=increase,crop={w_ov}:{h_ov},format=rgb24",
        "-f", "rawvideo", "-"
    ]
    raw_bytes = subprocess.run(dec_cmd, capture_output=True, check=True).stdout
    frame_sz = w_ov * h_ov * 3
    n_src = max(1, len(raw_bytes) // frame_sz)
    src_frames = np.frombuffer(raw_bytes[:n_src * frame_sz], dtype=np.uint8).reshape((n_src, h_ov, w_ov, 3))

    cum_t = build_speed_ramp_map(n_out, (n_src - 1) / dec_fps, rmode)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p", out_p
    ], stdin=subprocess.PIPE)

    for i in range(n_out):
        f_pos = min(n_src - 1.001, max(0.0, cum_t[i] * dec_fps))
        ia = int(math.floor(f_pos))
        ib = min(n_src - 1, ia + 1)
        frac = f_pos - ia
        if frac < 0.05 or ia == ib:
            frm = src_frames[ia]
        else:
            frm = ((1.0 - frac) * src_frames[ia].astype(np.float32) + frac * src_frames[ib].astype(np.float32)).astype(np.uint8)

        prog = i / max(1, n_out - 1)
        z = 1.0 + (z_end - 1.0) * prog
        cw = int(round(w_ov / z))
        ch = int(round(h_ov / z))
        if fn.endswith("_FLOW.mp4"):
            # Anchor toward upper-left (18% top/left, 82% bottom/right) so 100% of Flow's bottom-right corner mark is outside frame!
            x0 = int(round((w_ov - cw) * 0.18))
            y0 = int(round((h_ov - ch) * 0.14))
        else:
            x0 = (w_ov - cw) // 2
            y0 = (h_ov - ch) // 2
        cropped = Image.fromarray(frm[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
        enc.stdin.write(cropped.tobytes())

    enc.stdin.close()
    enc.wait()
    return {"index": idx + 1, "id": sid, "start": t0, "end": t1, "src": fn, "path": out_p, "frames": n_out}

def load_st(path, s0=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error"]
    if s0 > 0: cmd += ["-ss", f"{s0:.3f}"]
    if dur is not None: cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2).copy()

def mix_c(bus, clip, ts, gain=1.0, fi=0.03, fo=0.12):
    c = (clip * gain).copy()
    nfi, nfo = min(len(c), int(fi*SR)), min(len(c), int(fo*SR))
    if nfi > 1: c[:nfi] *= np.linspace(0, 1, nfi, dtype=np.float32)[:, None]
    if nfo > 1: c[-nfo:] *= np.linspace(1, 0, nfo, dtype=np.float32)[:, None]
    i0 = max(0, int(round(ts * SR)))
    if i0 >= len(bus): return
    i1 = min(len(bus), i0 + len(c))
    bus[i0:i1] += c[:i1 - i0]

def save_w(path, arr):
    pcm = (np.clip(arr, -0.99, 0.99) * 32767.0).astype(np.int16)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", path], stdin=subprocess.PIPE)
    p.stdin.write(pcm.tobytes()); p.stdin.close(); p.wait()

def main():
    print("[1/5] Rendering 16 Speed-Ramped UNGRADED (0% Color Filter) Shots via RTX 3060 h264_nvenc...", flush=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        manifest = list(ex.map(render_ungraded_shot, enumerate(V5_SHOTS)))
    json.dump(manifest, open(os.path.join(OUT_DIR, "shots_v5_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    title_list = [
        ("V5_T01_signboard_opening.mov", 0.15, 3.85),
        ("V5_T02_signboard_footer.mov",  0.25, 24.40),
        ("V5_T03_signboard_endcard.mov", 24.60, 27.60),
    ]

    print("[2/5] Mixing Cinematic BGM ('Slow Cook Honey') + Authentic Tactile Cooking ASMR (-14.0 LUFS)...", flush=True)
    bgm_b  = np.zeros((N_SAMPLES, 2), dtype=np.float32)
    asmr_b = np.zeros((N_SAMPLES, 2), dtype=np.float32)
    sfx_b  = np.zeros((N_SAMPLES, 2), dtype=np.float32)

    bgm_raw = load_st(BGM_LOCAL, 6.0, DUR)
    mix_c(bgm_b, bgm_raw, 0.0, gain=0.90, fi=0.15, fo=0.80)

    gas_ig  = load_st(os.path.join(SFX_V2, "sfx_gas_ignite.mp3"), 0.0, 2.0)
    fry_oil = load_st(os.path.join(SFX_V1, "asmr_frying_pan.mp3"), 1.0, 10.0)
    pour_l  = load_st(os.path.join(SFX_V1, "asmr_liquid_pour.mp3"), 0.1, 2.0)
    sticky  = load_st(os.path.join(SFX_V1, "asmr_sauce_sticky.mp3"), 1.5, 2.5)
    crunch  = load_st(os.path.join(SFX_V1, "asmr_crispy_crunch.mp3"), 0.0, 1.8)
    deep_w  = load_st(os.path.join(SFX_V1, "sfx_deep_woosh.mp3"), 0.0, 1.6)

    mix_c(asmr_b, gas_ig,                           0.08, gain=0.52, fi=0.02, fo=0.30) # S01 Stove ignite
    mix_c(asmr_b, fry_oil[:int(3.3*SR)],            3.92, gain=0.52, fi=0.06, fo=0.45) # S04-S05 Clean fryer & crispy lift
    mix_c(asmr_b, fry_oil[int(5.0*SR):int(7.6*SR)], 7.38, gain=0.36, fi=0.10, fo=0.40) # S06-S07 Sauce simmer
    mix_c(asmr_b, pour_l[:int(1.9*SR)],            10.18, gain=0.44, fi=0.05, fo=0.30) # S08 Ruby sauce cup pour
    mix_c(asmr_b, sticky[:int(1.9*SR)],            12.42, gain=0.34, fi=0.10, fo=0.35) # S09 Cheddar sauce cup pour
    mix_c(asmr_b, crunch,                          16.18, gain=0.76, fi=0.02, fo=0.25) # S11 Clear-glove crispy tear
    mix_c(asmr_b, sticky[:int(1.5*SR)],            18.55, gain=0.26, fi=0.10, fo=0.30) # S12 Real Jajangmyeon lift

    # Soft airy transitions (-19dB gentle level per clean SFX rule)
    for wt in [1.12, 3.82, 7.28, 10.02, 15.92, 21.52, 24.52]:
        mix_c(sfx_b, deep_w, wt, gain=0.18, fi=0.03, fo=0.25)

    raw_mix = os.path.join(AUDIO_V5, "mix_v5_raw.wav")
    mst_wav = os.path.join(AUDIO_V5, "master_v5_14lufs.wav")
    save_w(raw_mix, bgm_b + asmr_b + sfx_b)
    save_w(os.path.join(AUDIO_V5, "stem_asmr_v5.wav"), asmr_b)
    save_w(os.path.join(AUDIO_V5, "stem_sfx_v5.wav"),  sfx_b)

    p1 = subprocess.run(["ffmpeg", "-v", "info", "-i", raw_mix, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    ln = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p1.stderr).group(0))
    af2 = f"loudnorm=I=-14.0:TP=-1.0:LRA=11.0:measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true,aresample={SR}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_mix, "-af", af2, "-c:a", "pcm_s16le", mst_wav], check=True)

    # Verify integrated loudness
    p_ver = subprocess.run(["ffmpeg", "-v", "info", "-i", mst_wav, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    ln_ver = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p_ver.stderr).group(0))
    print(f"  Verified Master Audio Loudness: I = {ln_ver['input_i']} LUFS, TP = {ln_ver['input_tp']} dBTP", flush=True)

    print("[3/5] Compositing UNGRADED V5 Master MP4 via h264_nvenc + Syncing to All 3 Locations...", flush=True)
    concat_txt = os.path.join(OUT_DIR, "concat_v5.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for m in manifest:
            f.write(f"file '{m['path'].replace(chr(92), '/')}'\n")
    base_mp4 = os.path.join(OUT_DIR, "_base_v5_ungraded.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", base_mp4], check=True)

    inputs = ["-i", base_mp4]
    for t_fn, _, _ in title_list:
        inputs += ["-i", os.path.join(TITLE_V5, t_fn)]
    inputs += ["-i", mst_wav]

    # 100% ZERO COLOR GRADING / ZERO LUT / ZERO B&W OR FILM BURN TINT!
    fc_parts = ["[0:v]format=yuva420p[bg0];"]
    prev = "bg0"
    for idx, (t_fn, ts0, ts1) in enumerate(title_list):
        in_i = 1 + idx
        nxt = f"bg{idx+1}"
        fc_parts.append(f"[{in_i}:v]setpts=PTS+{ts0:.3f}/TB[t{idx}];[{prev}][t{idx}]overlay=0:0:eof_action=pass:enable='between(t,{ts0:.3f},{ts1:.3f})'[{nxt}];")
        prev = nxt
    fc_parts.append(f"[{prev}]trim=0:{DUR:.2f},setpts=PTS-STARTPTS,format=yuv420p[vout]")

    final_local = os.path.join(OUT_DIR, "FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4")
    aud_idx = 1 + len(title_list)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error"] + inputs + [
            "-filter_complex", "".join(fc_parts),
            "-map", "[vout]", "-map", f"{aud_idx}:a",
            "-t", f"{DUR:.2f}", "-r", "30",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart",
            final_local
        ],
        check=True
    )

    for dp in [
        r"D:\XUẤT CAPCUT\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
        r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
        r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
    ]:
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copy2(final_local, dp)
        print("  Synced ->", dp, flush=True)

    print("[4/5] Deploying Multi-Track UNGRADED CapCut Pro Draft ('FEEL_CHICKEN_Food_Cinematic_Pro')...", flush=True)
    def uid(): return str(uuid.uuid4()).upper()
    def us_f(s): return int(round(int(round(float(s)*FPS)) * 1_000_000 / FPS))
    def nfwd(p): return os.path.normpath(p).replace("\\", "/")

    d_tpl = os.path.join(DRAFTS_DIR, "FEEL_CHICKEN_2011_Full_Layers_V6")
    if not os.path.exists(os.path.join(d_tpl, "draft_content.json")):
        d_tpl = os.path.join(DRAFTS_DIR, "F20 vd 1")
    dc_tpl = json.load(open(os.path.join(d_tpl, "draft_content.json"), encoding="utf-8"))
    dm_tpl = json.load(open(os.path.join(d_tpl, "draft_meta_info.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(dc_tpl["tracks"][0])
    atrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "audio"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(next(m for m in dc_tpl["materials"]["videos"] if m.get("type") == "video"))
    amat_tpl   = copy.deepcopy(dc_tpl["materials"]["audios"][0])
    afade_tpl  = copy.deepcopy(dc_tpl["materials"]["audio_fades"][0])
    dm_vid_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    dm_aud_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") in ("music","audio","sound")) if any(x.get("metetype") in ("music","audio","sound") for g in dm_tpl["draft_materials"] for x in g.get("value",[])) else dm_vid_tpl)

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}
    a_extra_keys = ("speeds", "placeholder_infos", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}

    tl_id, now_s, now_us = uid(), int(time.time()), int(time.time() * 1_000_000)
    D = copy.deepcopy(dc_tpl)
    D.update({
        "id": tl_id, "name": DRAFT_NAME, "fps": 30.0, "duration": 0,
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_tpl["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })
    mat_cache, dm_type0, ref_bytes = {}, [], 0

    def reg_vid(path):
        nonlocal ref_bytes
        fwd = nfwd(path)
        if fwd in mat_cache: return mat_cache[fwd]
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
        du_u = max(33333, us_f(float(r.stdout.strip() or 1.0)))
        mid, lmid, fn = uid(), str(uuid.uuid4()), os.path.basename(path)
        m = copy.deepcopy(vmat_tpl)
        m.update({"id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid, "type": "video", "path": fwd, "media_path": "", "local_id": "", "material_name": fn, "width": 1080, "height": 1920, "duration": du_u, "has_audio": False})
        dme = copy.deepcopy(dm_vid_tpl)
        dme.update({"id": lmid, "file_Path": fwd, "extra_info": fn, "duration": du_u, "width": 1080, "height": 1920, "metetype": "video", "item_source": 1, "create_time": now_s, "import_time": now_s, "import_time_ms": now_us, "roughcut_time_range": {"start": 0, "duration": du_u}, "sub_time_range": {"start": -1, "duration": -1}})
        D["materials"]["videos"].append(m); dm_type0.append(dme); ref_bytes += os.path.getsize(path)
        mat_cache[fwd] = (mid, du_u)
        return mid, du_u

    def reg_aud(path):
        nonlocal ref_bytes
        fwd = nfwd(path)
        if fwd in mat_cache: return mat_cache[fwd]
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
        du_u = max(33333, us_f(float(r.stdout.strip() or 1.0)))
        mid, lmid, fn = uid(), str(uuid.uuid4()), os.path.basename(path)
        m = copy.deepcopy(amat_tpl)
        m.update({"id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid, "type": "extract_music", "name": os.path.splitext(fn)[0], "path": fwd, "duration": du_u, "music_id": "", "effect_id": "", "resource_id": "", "source_platform": 0})
        dme = copy.deepcopy(dm_aud_tpl)
        dme.update({"id": lmid, "file_Path": fwd, "extra_info": fn, "duration": du_u, "width": 0, "height": 0, "metetype": "music", "item_source": 1, "create_time": now_s, "import_time": now_s, "import_time_ms": now_us})
        D["materials"]["audios"].append(m); dm_type0.append(dme); ref_bytes += os.path.getsize(path)
        mat_cache[fwd] = (mid, du_u)
        return mid, du_u

    def mk_vseg(path, tl_s, dur_s, ridx=0):
        mid, mdu = reg_vid(path)
        du_u = min(us_f(dur_s), mdu)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, te in v_extra_tpl.items():
            em = copy.deepcopy(te); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        seg.update({"id": uid(), "material_id": mid, "source_timerange": {"start": 0, "duration": du_u}, "target_timerange": {"start": us_f(tl_s), "duration": du_u}, "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0, "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": ridx, "track_render_index": 0, "visible": True})
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}; seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}; seg["clip"]["alpha"] = 1.0; seg["clip"]["rotation"] = 0.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        return seg

    def mk_aseg(path, tl_s, dur_s, src_s=0.0, vol=1.0, fi=40000, fo=120000):
        mid, mdu = reg_aud(path)
        st_u = us_f(src_s)
        du_u = min(us_f(dur_s), max(33333, mdu - st_u))
        seg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, te in a_extra_tpl.items():
            em = copy.deepcopy(te); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        af = copy.deepcopy(afade_tpl); af.update({"id": uid(), "fade_in_duration": min(du_u//3, fi), "fade_out_duration": min(du_u//3, fo)})
        D["materials"]["audio_fades"].append(af); refs.append(af["id"])
        seg.update({"id": uid(), "material_id": mid, "source_timerange": {"start": st_u, "duration": du_u}, "target_timerange": {"start": us_f(tl_s), "duration": du_u}, "speed": 1.0, "volume": float(vol), "last_nonzero_volume": float(max(0.05, vol)), "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": 0, "track_render_index": 1, "visible": True})
        return seg

    # Track V0: 16 Ungraded Speed-Ramped Shots (0 gaps, 0 overlaps!)
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    cur_u = 0
    for m in manifest:
        sg = mk_vseg(m["path"], cur_u / 1e6, m["frames"] / FPS, ridx=0)
        sg["target_timerange"]["start"] = cur_u
        tr_v0["segments"].append(sg)
        cur_u += sg["target_timerange"]["duration"]
    D["tracks"].append(tr_v0)

    # Track V1: Opening & End-Card Signboard Overlays (non-overlapping: 0.15-3.85s & 24.60-27.60s)
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid()
    tr_v1["segments"] = [
        mk_vseg(os.path.join(TITLE_V5, "V5_T01_signboard_opening.mov"), 0.15, 3.70, ridx=100),
        mk_vseg(os.path.join(TITLE_V5, "V5_T03_signboard_endcard.mov"), 24.60, 3.00, ridx=100),
    ]
    D["tracks"].append(tr_v1)

    # Track V2: Subtle Signboard Footer (0.25-24.40s)
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid()
    tr_v2["segments"] = [mk_vseg(os.path.join(TITLE_V5, "V5_T02_signboard_footer.mov"), 0.25, 24.15, ridx=110)]
    D["tracks"].append(tr_v2)

    # Audio Tracks: BGM + Cooking ASMR + Clean Micro-SFX
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid()
    tr_bgm["segments"] = [mk_aseg(BGM_LOCAL, 0.0, DUR, 6.0, vol=0.90, fi=150000, fo=800000)]
    D["tracks"].append(tr_bgm)

    tr_asmr = copy.deepcopy(atrack_tpl); tr_asmr["id"] = uid()
    tr_asmr["segments"] = [mk_aseg(os.path.join(AUDIO_V5, "stem_asmr_v5.wav"), 0.0, DUR, 0.0, vol=1.0)]
    D["tracks"].append(tr_asmr)

    tr_sfx = copy.deepcopy(atrack_tpl); tr_sfx["id"] = uid()
    tr_sfx["segments"] = [mk_aseg(os.path.join(AUDIO_V5, "stem_sfx_v5.wav"), 0.0, DUR, 0.0, vol=1.0)]
    D["tracks"].append(tr_sfx)
    D["duration"] = cur_u

    stage_dir = os.path.join(STAGE_V5, DRAFT_NAME)
    if os.path.exists(stage_dir): shutil.rmtree(stage_dir)
    os.makedirs(os.path.join(stage_dir, "Timelines", tl_id, "common_attachment"), exist_ok=True)
    os.makedirs(os.path.join(stage_dir, "common_attachment"), exist_ok=True)

    print("[5/5] Extracting 12-Frame Master V5 QC Contact Sheet...", flush=True)
    pts = [
        (0.70,  "00:00.7 | Stove Ignite + Signboard Title"),
        (1.95,  "00:01.9 | [FLOW] Clean Stainless Flour"),
        (3.30,  "00:03.3 | [SONY] Steel Whisk Batter"),
        (4.70,  "00:04.7 | [FLOW] Clean Fryer (0 People!)"),
        (6.35,  "00:06.3 | [FLOW] Realistic Crispy Lift"),
        (9.35,  "00:09.3 | [SONY] Velvet Cheese Pan"),
        (11.20, "00:11.2 | [FLOW] Real A1_07833 Ruby Pour"),
        (13.45, "00:13.4 | [MUSE] Real A1_07871 Cheese Pour"),
        (15.30, "00:15.3 | [SONY] Toasted Sesame Glaze"),
        (17.25, "00:17.2 | [MUSE] Real Clear-Glove Tear"),
        (22.40, "00:22.4 | [MUSE] Real 5-Flavor Platter"),
        (26.10, "00:26.1 | CS1 Walk-In + Signboard Text"),
    ]
    W_C, H_C = 320, 568
    sheet = Image.new("RGB", (W_C * 4, H_C * 3), (10, 10, 10))
    dr = ImageDraw.Draw(sheet)
    fnt = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 15)
    cover_saved = False
    for i, (ts, lbl) in enumerate(pts):
        jp = os.path.join(CHK_V5, f"fv5_{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", final_local, "-frames:v", "1", "-vf", f"scale={W_C}:{H_C},format=yuvj420p", "-q:v", "2", jp], check=True)
        if i == 10 and not cover_saved:
            shutil.copy2(jp, os.path.join(stage_dir, "draft_cover.jpg"))
            shutil.copy2(jp, os.path.join(stage_dir, "Timelines", tl_id, "draft_cover.jpg"))
            cover_saved = True
        ri, ci = divmod(i, 4)
        x, y = ci * W_C, ri * H_C
        sheet.paste(Image.open(jp).convert("RGB"), (x, y))
        dr.rectangle([x, y, x + W_C, y + 26], fill=(0, 0, 0))
        dr.text((x + 6, y + 5), lbl, fill=(248, 246, 240), font=fnt)
        os.remove(jp)

    qc_local = os.path.join(CHK_V5, "FINAL_V5_AUTHENTIC_12FRAMES_QC.jpg")
    qc_art   = os.path.join(ART_DIR, "fc_food_cinematic_v5_authentic_preview.jpg")
    cmp_src  = os.path.join(CHK_V5, "FLOW_VS_MUSE_COMPARISON_FINAL.jpg")
    cmp_art  = os.path.join(ART_DIR, "fc_flow_vs_muse_comparison.jpg")
    sheet.save(qc_local, quality=92)
    shutil.copy2(qc_local, qc_art)
    shutil.copy2(qc_local, os.path.join(CLOUD_PRJ, "FINAL_V5_AUTHENTIC_12FRAMES_QC.jpg"))
    if os.path.exists(cmp_src):
        shutil.copy2(cmp_src, cmp_art)
        shutil.copy2(cmp_src, os.path.join(CLOUD_PRJ, "FLOW_VS_MUSE_COMPARISON_FINAL.jpg"))

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for p_dc in [os.path.join(stage_dir, "draft_content.json"), os.path.join(stage_dir, "template-2.tmp"),
                 os.path.join(stage_dir, "Timelines", tl_id, "draft_content.json"), os.path.join(stage_dir, "Timelines", tl_id, "template-2.tmp")]:
        open(p_dc, "wb").write(dc_bytes)

    open(os.path.join(stage_dir, "draft_settings"), "w", encoding="utf-8").write(f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=360\nreal_edit_keys=24\n")
    open(os.path.join(stage_dir, "key_value.json"), "w", encoding="utf-8").write("{}")
    open(os.path.join(stage_dir, "draft_biz_config.json"), "w", encoding="utf-8").write("")
    for aux in ["draft_agency_config.json", "performance_opt_info.json", "timeline_layout.json", "attachment_pc_common.json"]:
        sp = os.path.join(d_tpl, aux)
        if os.path.isfile(sp): shutil.copy2(sp, os.path.join(stage_dir, aux))
    for cad in [os.path.join(stage_dir, "common_attachment"), os.path.join(stage_dir, "Timelines", tl_id, "common_attachment")]:
        open(os.path.join(cad, "attachment_pc_timeline.json"), "w", encoding="utf-8").write('{"reference_lines_config":{"horizontal_lines":[],"is_lock":false,"is_visible":false,"vertical_lines":[]},"safe_area_type":0}')
        open(os.path.join(cad, "attachment_action_scene.json"), "w", encoding="utf-8").write('{"action_scene":{"removed_segments":[],"segment_infos":[]}}')
    json.dump({"draft_materials": [], "draft_virtual_store": [{"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "material_color_tag": "", "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]}, {"type": 1, "value": []}]}, open(os.path.join(stage_dir, "draft_virtual_store.json"), "w", encoding="utf-8"))
    json.dump({"config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False}, "create_time": now_us, "id": tl_id, "main_timeline_id": tl_id, "timelines": [{"create_time": now_us, "id": tl_id, "is_marked_delete": False, "name": "Dòng thời gian 01", "update_time": now_us}], "update_time": now_us, "version": 0}, open(os.path.join(stage_dir, "Timelines", "project.json"), "w", encoding="utf-8"), ensure_ascii=False)

    local_draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)
    M = copy.deepcopy(dm_tpl)
    M.update({"draft_id": DRAFT_ID, "draft_name": DRAFT_NAME, "draft_fold_path": nfwd(local_draft_dir), "draft_root_path": nfwd(DRAFTS_DIR), "draft_cover": "draft_cover.jpg", "draft_new_version": "164.0.0", "tm_duration": cur_u, "tm_draft_create": now_us, "tm_draft_modified": now_us, "draft_timeline_materials_size_": ref_bytes, "cloud_draft_cover": False, "cloud_draft_sync": False, "draft_materials": [{"type": 0, "value": dm_type0}, {"type": 1, "value": []}, {"type": 2, "value": []}, {"type": 3, "value": []}, {"type": 6, "value": []}, {"type": 7, "value": []}, {"type": 8, "value": []}]})
    json.dump(M, open(os.path.join(stage_dir, "draft_meta_info.json"), "w", encoding="utf-8"), ensure_ascii=False)

    if os.path.exists(local_draft_dir): shutil.rmtree(local_draft_dir)
    shutil.copytree(stage_dir, local_draft_dir)

    rm_path = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    rm = json.load(open(rm_path, encoding="utf-8"))
    stores = [s for s in rm.get("all_draft_store", []) if s.get("draft_name") != DRAFT_NAME and s.get("draft_id") != DRAFT_ID]
    te = copy.deepcopy(stores[0])
    te.update({"cloud_draft_cover": False, "cloud_draft_sync": False, "draft_cover": nfwd(local_draft_dir) + "/draft_cover.jpg", "draft_fold_path": nfwd(local_draft_dir), "draft_id": DRAFT_ID, "draft_json_file": nfwd(local_draft_dir) + "/draft_content.json", "draft_name": DRAFT_NAME, "draft_new_version": "164.0.0", "draft_root_path": nfwd(DRAFTS_DIR), "draft_timeline_materials_size": ref_bytes, "streaming_edit_draft_ready": True, "tm_draft_create": now_us, "tm_draft_modified": now_us, "tm_draft_removed": 0, "tm_duration": cur_u})
    rm["all_draft_store"] = [te] + stores
    json.dump(rm, open(rm_path, "w", encoding="utf-8"), ensure_ascii=False)

    # Sync build scripts & manifest to Cloud Project Archive
    for sp in [__file__, os.path.join(OUT_DIR, "v5_step01b_gen_flow_vs_muse_videos.py"), os.path.join(OUT_DIR, "v5_step02_signboard_titles.py"), os.path.join(OUT_DIR, "shots_v5_manifest.json")]:
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(CLOUD_PRJ, os.path.basename(sp)))

    print("V5 AUTHENTIC FLOW + MUSE + SONY 60FPS MASTER & CAPCUT PRO DRAFT COMPLETE!", flush=True)

if __name__ == "__main__":
    main()
