import copy, json, math, os, shutil, subprocess, time, uuid
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT_DIR   = r"d:\AI\full studio\output\feelchicken-food-cinematic"
SHOTS_V3  = os.path.join(OUT_DIR, "shots_v3_ungraded")
SHOTS_V5  = os.path.join(OUT_DIR, "shots_v5_ungraded")
SHOTS_V6  = os.path.join(OUT_DIR, "shots_v6_v4fixed")
VID_V5    = os.path.join(OUT_DIR, "ai_v5_flow_vs_muse")
RAW_V2    = os.path.join(OUT_DIR, "raw_v2")
TITLE_V4  = os.path.join(OUT_DIR, "titles_v4_sijonsonn")
AUDIO_V3  = os.path.join(OUT_DIR, "audio_v3")
CHK_V6    = os.path.join(OUT_DIR, "check_v6")
STAGE_V6  = os.path.join(OUT_DIR, "capcut_stage_v6")
ART_DIR   = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-food-cinematic"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_Food_Cinematic_Pro"
DRAFT_ID   = "F94A82E1-63D4-4B89-9E12-7745C280B3A9"

for d in (SHOTS_V6, CHK_V6, STAGE_V6):
    os.makedirs(d, exist_ok=True)
if os.path.exists("Z:\\"):
    os.makedirs(CLOUD_PRJ, exist_ok=True)

W, H = 1080, 1920
FPS = 30
DUR = 27.60
TOTAL_FRAMES = 828
BGM_LOCAL = os.path.join(RAW_V2, "BGM_Slow_Cook_Honey.mp3")

def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def build_speed_ramp_map(n_out: int, avail_src_s: float, mode: str) -> np.ndarray:
    u = np.linspace(0.0, 1.0, n_out)
    if mode == "ramp_mid":
        spd = 0.50 + 1.65 * ((2.0 * np.abs(u - 0.5)) ** 2.2)
    elif mode == "ramp_in":
        spd = 0.56 + 1.80 * (np.maximum(0.0, 1.0 - u / 0.32) ** 2.0)
    elif mode == "slow_pure":
        spd = np.full_like(u, 0.56)
    else:
        spd = np.full_like(u, 0.88)
    dt_src = spd / float(FPS)
    cum_t = np.cumsum(dt_src) - dt_src[0]
    max_allow = max(0.5, avail_src_s - 0.10)
    if cum_t[-1] > max_allow:
        cum_t *= (max_allow / cum_t[-1])
    return cum_t

def render_exact_frames_shot(src_p: str, out_p: str, n_out: int, s0: float, win_dur: float, rmode: str, z_end: float = 1.04, is_flow: bool = False, y_bias: float = 0.5):
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", src_p], capture_output=True, text=True, check=True)
    tot_src_dur = float(pr.stdout.strip() or 4.0)
    s0_safe = min(s0, max(0.0, tot_src_dur - 0.6))
    read_dur = min(win_dur, max(0.5, tot_src_dur - s0_safe))

    w_ov, h_ov = (1296, 2304) if is_flow else (1166, 2074)
    dec_fps = 60.0
    raw_bytes = subprocess.run([
        "ffmpeg", "-v", "error", "-ss", f"{s0_safe:.3f}", "-t", f"{read_dur:.3f}", "-i", src_p,
        "-vf", f"fps={int(dec_fps)},scale={w_ov}:{h_ov}:force_original_aspect_ratio=increase,crop={w_ov}:{h_ov},format=rgb24",
        "-f", "rawvideo", "-"
    ], capture_output=True, check=True).stdout
    frame_sz = w_ov * h_ov * 3
    n_src = max(1, len(raw_bytes) // frame_sz)
    src_frames = np.frombuffer(raw_bytes[:n_src * frame_sz], dtype=np.uint8).reshape((n_src, h_ov, w_ov, 3))
    cum_t = build_speed_ramp_map(n_out, (n_src - 1) / dec_fps, rmode)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "15", "-b:v", "0", "-pix_fmt", "yuv420p", out_p
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
        if is_flow:
            cw = int(round(W / z))
            ch = int(round(H / z))
            x0 = int(round((w_ov - cw) * 0.12))
            y0 = int(round((h_ov - ch) * 0.10))
        else:
            cw = int(round(w_ov / z))
            ch = int(round(h_ov / z))
            x0 = (w_ov - cw) // 2
            y0 = int(round((h_ov - ch) * y_bias))
        cropped = Image.fromarray(frm[y0:y0+ch, x0:x0+cw], "RGB").resize((W, H), Image.Resampling.BILINEAR)
        enc.stdin.write(cropped.tobytes())

    enc.stdin.close()
    enc.wait()

# Exact V4 15-Shot Structure (preserving ALL beloved V4 shots, timing, transitions, and OLD TEXT, replacing ONLY the 6 flagged clips!)
V6_PLAN = [
    # (idx, id, t0, t1, mode, params)
    (1,  "S01_stove_ignite",    0.00,  1.20, "keep_v4", "01_S01_stove_ignite.mp4"),
    # Fix Image 1: Real Sony 60fps dark-top egg crack into seasoned flour bowl (high contrast for 'FEEL CHICKEN / COOKING Time'!)
    (2,  "S02_real_egg_flour",  1.20,  2.80, "render",  (os.path.join(RAW_V2, "m02_egg_crack.MP4"), 1.65, 3.20, "ramp_mid", False, 0.15)),
    (3,  "S03_steel_whisk",     2.80,  4.00, "keep_v4", "03_S03_steel_whisk.mp4"),
    # Fix Image 2: Spotless Feel Chicken stainless commercial deep fryer on Google Flow (ZERO people/faces!)
    (4,  "S04_clean_fryer",     4.00,  5.20, "render",  (os.path.join(VID_V5, "SC02_clean_fryer_FLOW.mp4"), 0.12, 3.65, "ramp_in", True, 0.5)),
    # Fix Image 3: Realistic golden crispy lift in Feel Chicken's square wire basket on Google Flow (ZERO thick syrup!)
    (5,  "S05_crispy_lift",     5.20,  7.30, "render",  (os.path.join(VID_V5, "SC03_crispy_lift_FLOW.mp4"), 0.10, 3.75, "ramp_in", True, 0.5)),
    (6,  "S06_red_simmer",      7.30,  8.50, "keep_v4", "06_S06_red_simmer.mp4"),
    (7,  "S07_ai_wok_fire",     8.50, 10.80, "keep_v4", "07_S07_ai_wok_fire.mp4"),
    # Fix Image 4A & 4B: Real Sony A1 sauce-cup pour photos animated cleanly (A1_07833 Ruby Pour on Flow + A1_07871 Cheddar Pour on Muse!)
    (8,  "S08_real_ruby_pour", 10.80, 13.20, "render",  (os.path.join(VID_V5, "SC04_ruby_pour_FLOW.mp4"), 0.05, 3.80, "ramp_mid", True, 0.5)),
    (9,  "S09_real_cheese_pour",13.20, 15.60, "render", (os.path.join(VID_V5, "SC05_cheddar_pour_MUSE.mp4"), 0.08, 3.75, "ramp_mid", False, 0.5)),
    (10, "S10_sesame_black",   15.60, 16.90, "keep_v4", "10_S10_sesame_black.mp4"),
    # Fix Image 5: Real clear-glove chicken tear from user's Sony A1 photo A1_07983 (ZERO black gloves, ZERO cartoon smoke!)
    (11, "S11_real_clear_tear",16.90, 19.40, "render",  (os.path.join(VID_V5, "SC06_clear_tear_MUSE.mp4"), 0.08, 3.75, "ramp_in", False, 0.5)),
    (12, "S12_ai_jajang_up",   19.40, 21.40, "keep_v4", "12_S12_ai_jajang_up.mp4"),
    (13, "S13_tokbokki_mac",   21.40, 22.60, "keep_v4", "13_S13_tokbokki_mac.mp4"),
    # Fix Image 6: Real 5-flavor Gà Ngũ Vị platter optical push from A1_08995 (ZERO fake black-gloved hand!)
    (14, "S14_real_nguvi_hero",22.60, 24.60, "render",  (os.path.join(VID_V5, "SC07_nguvi_orbit_MUSE.mp4"), 0.08, 3.75, "ramp_in", False, 0.5)),
    (15, "S15_cs1_walkin",     24.60, 27.60, "keep_v4", "15_S15_cs1_walkin.mp4"),
]

def apply_v4_sijonsonn_transitions(base_in: str, base_out: str):
    dec = subprocess.Popen([
        "ffmpeg", "-v", "error", "-i", base_in,
        "-vf", f"fps={FPS},scale={W}:{H},format=rgb24", "-f", "rawvideo", "-"
    ], stdout=subprocess.PIPE)
    raw_all = dec.stdout.read()
    dec.wait()
    fsz = W * H * 3
    nf = min(TOTAL_FRAMES, len(raw_all) // fsz)
    frames = np.frombuffer(raw_all[:nf * fsz], dtype=np.uint8).reshape((nf, H, W, 3)).copy()

    # Transition 1: B&W Monochrome Beat-Flash at f = 322..330 (10.80s)
    for k, fi in enumerate(range(322, 330)):
        if 0 <= fi < nf:
            f_rgb = frames[fi].astype(np.float32)
            luma = (0.299 * f_rgb[:, :, 0] + 0.587 * f_rgb[:, :, 1] + 0.114 * f_rgb[:, :, 2])[:, :, None]
            bw = np.clip((luma - 128.0) * 1.18 + 128.0, 0, 255)
            mix = 1.0 if k < 5 else (1.0 - (k - 4) / 3.0)
            frames[fi] = np.clip(f_rgb * (1.0 - mix) + bw * mix, 0, 255).astype(np.uint8)

    # Transition 2: 3-Column Vertical Shutter-Slice Whip at cut f = 507 (16.90s)
    snap_A = frames[506].copy()
    snap_B = frames[507].copy()
    ker_len = 26
    def vblur(arr):
        pad = np.pad(arr.astype(np.float32), ((ker_len//2, ker_len//2), (0, 0), (0, 0)), mode="edge")
        csum = np.cumsum(pad, axis=0)
        return np.clip((csum[ker_len:] - csum[:-ker_len]) / ker_len, 0, 255).astype(np.uint8)
    blur_A, blur_B = vblur(snap_A), vblur(snap_B)

    col_w = W // 3
    t_len = 9
    for idx_t, fi in enumerate(range(503, 503 + t_len)):
        p = (idx_t + 1) / (t_len + 1)
        comp = np.zeros((H, W, 3), dtype=np.uint8)
        for col in range(3):
            x0, x1 = col * col_w, (W if col == 2 else (col + 1) * col_w)
            p_col = np.clip((p - col * 0.08) / 0.84, 0.0, 1.0)
            ec = ease_io(p_col)
            use_blur = 0.12 < p_col < 0.88
            srcA = blur_A if use_blur else frames[min(506, fi)]
            srcB = blur_B if use_blur else frames[max(507, fi)]
            split_y = int(round(ec * H))
            if col % 2 == 0:
                if split_y > 0: comp[:split_y, x0:x1] = srcB[H - split_y:, x0:x1]
                if split_y < H: comp[split_y:, x0:x1] = srcA[:H - split_y, x0:x1]
            else:
                if split_y > 0: comp[H - split_y:, x0:x1] = srcB[:split_y, x0:x1]
                if split_y < H: comp[:H - split_y, x0:x1] = srcA[split_y:, x0:x1]
            if col > 0:
                comp[:, x0:x0+2] = (comp[:, x0:x0+2].astype(np.float32) * 0.35).astype(np.uint8)
        frames[fi] = comp

    # Transition 3: Warm Analog Film-Burn Flash across cut f = 674..684 (22.60s)
    yy = np.linspace(-1.0, 1.0, H)[:, None]
    xx = np.linspace(-1.0, 1.0, W)[None, :]
    burn_mask = np.exp(-((xx + 0.35)**2 * 1.4 + (yy - 0.10)**2 * 1.1))
    burn_rgb = np.zeros((H, W, 3), dtype=np.float32)
    burn_rgb[:, :, 0], burn_rgb[:, :, 1], burn_rgb[:, :, 2] = 255.0, 128.0, 24.0
    for idx_b, fi in enumerate(range(674, 684)):
        u = (idx_b + 0.5) / 10.0
        strength = math.sin(math.pi * u) ** 2.0 * 0.78
        a_burn = (burn_mask * strength)[:, :, None]
        f_orig = frames[fi].astype(np.float32)
        scr = 255.0 - (255.0 - f_orig) * (255.0 - burn_rgb * a_burn) / 255.0
        frames[fi] = np.clip(scr, 0, 255).astype(np.uint8)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "15", "-b:v", "0", "-pix_fmt", "yuv420p", base_out
    ], stdin=subprocess.PIPE)
    for frm in frames:
        enc.stdin.write(frm.tobytes())
    enc.stdin.close()
    enc.wait()

def main():
    print("[1/4] Assembling V4 Timeline + Surgical Fixes ONLY on the Flagged Clips...", flush=True)
    manifest = []
    for idx, sid, t0, t1, mode, param in V6_PLAN:
        n_out = int(round(t1 * FPS)) - int(round(t0 * FPS))
        out_p = os.path.join(SHOTS_V6, f"{idx:02d}_{sid}.mp4")
        if mode == "keep_v4":
            # Re-encode to identical h264_nvenc stream params so concat -c copy is 100% seamless!
            v4_src = os.path.join(SHOTS_V3, param)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", v4_src, "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "15", "-b:v", "0", "-pix_fmt", "yuv420p", "-r", "30", out_p], check=True)
        else:
            src_p, s0, wdur, rmode, is_fl, y_b = param
            render_exact_frames_shot(src_p, out_p, n_out, s0, wdur, rmode, 1.04, is_fl, y_b)
        manifest.append({"index": idx, "id": sid, "start": t0, "end": t1, "path": out_p, "frames": n_out})

    concat_txt = os.path.join(OUT_DIR, "concat_v6.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for m in manifest:
            f.write(f"file '{m['path'].replace(chr(92), '/')}'\n")
    base_raw = os.path.join(OUT_DIR, "_base_v6_ungraded.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", base_raw], check=True)

    print("[2/4] Weaving Exact V4 @sijonsonn Transitions + Restoring Exact V4 'COOKING Time' Typography...", flush=True)
    base_tr = os.path.join(OUT_DIR, "_base_v6_transitions.mp4")
    apply_v4_sijonsonn_transitions(base_raw, base_tr)

    # RESTORE 100% OF V4'S EXACT BELOVED TYPOGRAPHY ('FEEL CHICKEN / COOKING Time', editorial footer, V4 End-Card)!
    title_list = [
        ("V4_T01_sijonsonn_opening.mov", 0.10, 4.00),
        ("V4_T02_editorial_footer.mov",  0.20, 24.45),
        ("V4_T03_endcard.mov",           24.60, 27.60),
    ]
    mst_v4 = os.path.join(AUDIO_V3, "master_v4_14lufs.wav")

    inputs = ["-i", base_tr] + [x for fn, _, _ in title_list for x in ("-i", os.path.join(TITLE_V4, fn))] + ["-i", mst_v4]
    fc_parts = ["[0:v]format=yuva420p[bg0];"]
    prev = "bg0"
    for idx, (fn, ts0, ts1) in enumerate(title_list):
        fc_parts.append(f"[{1+idx}:v]setpts=PTS+{ts0:.3f}/TB[t{idx}];[{prev}][t{idx}]overlay=0:0:eof_action=pass:enable='between(t,{ts0:.3f},{ts1:.3f})'[bg{idx+1}];")
        prev = f"bg{idx+1}"
    fc_parts.append(f"[{prev}]trim=0:{DUR:.2f},setpts=PTS-STARTPTS,format=yuv420p[vout]")

    final_local = os.path.join(OUT_DIR, "FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error"] + inputs + [
            "-filter_complex", "".join(fc_parts),
            "-map", "[vout]", "-map", "4:a",
            "-t", f"{DUR:.2f}", "-r", "30",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "15", "-b:v", "0", "-pix_fmt", "yuv420p",
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
        if dp.startswith("Z:") and not os.path.exists("Z:\\"):
            continue
        shutil.copy2(final_local, dp)
        print("  Synced ->", dp, flush=True)

    print("[3/4] Updating CapCut Pro Draft with V6 Surgical Shots + Restored V4 'COOKING Time' Titles...", flush=True)
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

    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    cur_u = 0
    for m in manifest:
        sg = mk_vseg(m["path"], cur_u / 1e6, m["frames"] / FPS, ridx=0)
        sg["target_timerange"]["start"] = cur_u
        tr_v0["segments"].append(sg)
        cur_u += sg["target_timerange"]["duration"]
    D["tracks"].append(tr_v0)

    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid()
    tr_v1["segments"] = [
        mk_vseg(os.path.join(TITLE_V4, "V4_T01_sijonsonn_opening.mov"), 0.10, 3.90, ridx=100),
        mk_vseg(os.path.join(TITLE_V4, "V4_T03_endcard.mov"),           24.60, 3.00, ridx=100),
    ]
    D["tracks"].append(tr_v1)

    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid()
    tr_v2["segments"] = [mk_vseg(os.path.join(TITLE_V4, "V4_T02_editorial_footer.mov"), 0.20, 24.25, ridx=110)]
    D["tracks"].append(tr_v2)

    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid()
    tr_bgm["segments"] = [mk_aseg(BGM_LOCAL, 0.0, DUR, 6.0, vol=0.90, fi=150000, fo=800000)]
    D["tracks"].append(tr_bgm)

    tr_asmr = copy.deepcopy(atrack_tpl); tr_asmr["id"] = uid()
    tr_asmr["segments"] = [mk_aseg(os.path.join(AUDIO_V3, "stem_asmr_v3.wav"), 0.0, DUR, 0.0, vol=1.0)]
    D["tracks"].append(tr_asmr)

    tr_sfx = copy.deepcopy(atrack_tpl); tr_sfx["id"] = uid()
    tr_sfx["segments"] = [mk_aseg(os.path.join(AUDIO_V3, "stem_sfx_v3.wav"), 0.0, DUR, 0.0, vol=1.0)]
    D["tracks"].append(tr_sfx)
    D["duration"] = cur_u

    stage_dir = os.path.join(STAGE_V6, DRAFT_NAME)
    if os.path.exists(stage_dir): shutil.rmtree(stage_dir)
    os.makedirs(os.path.join(stage_dir, "Timelines", tl_id, "common_attachment"), exist_ok=True)
    os.makedirs(os.path.join(stage_dir, "common_attachment"), exist_ok=True)

    print("[4/4] Extracting 12-Frame QC Sheet of V6 (V4 + Surgical Fixes + Restored Old Text)...", flush=True)
    pts = [
        (0.85,  "00:00.8 | [V4] Stove + Old COOKING Time"),
        (2.10,  "00:02.1 | [FIXED] Real Egg & Flour + Text"),
        (4.55,  "00:04.5 | [FIXED] Clean Feel Fryer (0 Nguoi)"),
        (6.25,  "00:06.2 | [FIXED] Realistic Crispy Lift"),
        (9.60,  "00:09.6 | [V4] Blue-Flame Wok Toss"),
        (10.85, "00:10.8 | [V4] B&W Beat-Flash Transition"),
        (12.00, "00:12.0 | [FIXED] Real A1_07833 Ruby Pour"),
        (14.40, "00:14.4 | [FIXED] Real A1_07871 Cheese Pour"),
        (16.90, "00:16.9 | [V4] 3-Col Shutter-Slice Whip"),
        (18.20, "00:18.2 | [FIXED] Real Clear-Glove Tear"),
        (23.60, "00:23.6 | [FIXED] Real 5-Flavor Platter"),
        (26.20, "00:26.2 | [V4] CS1 Walk-In + Old End-Card"),
    ]
    W_C, H_C = 320, 568
    sheet = Image.new("RGB", (W_C * 4, H_C * 3), (10, 10, 10))
    dr = ImageDraw.Draw(sheet)
    fnt = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 14)
    cover_saved = False
    for i, (ts, lbl) in enumerate(pts):
        jp = os.path.join(CHK_V6, f"fv6_{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", final_local, "-frames:v", "1", "-vf", f"scale={W_C}:{H_C},format=yuvj420p", "-q:v", "2", jp], check=True)
        if i == 10 and not cover_saved:
            shutil.copy2(jp, os.path.join(stage_dir, "draft_cover.jpg"))
            shutil.copy2(jp, os.path.join(stage_dir, "Timelines", tl_id, "draft_cover.jpg"))
            cover_saved = True
        ri, ci = divmod(i, 4)
        x, y = ci * W_C, ri * H_C
        sheet.paste(Image.open(jp).convert("RGB"), (x, y))
        dr.rectangle([x, y, x + W_C, y + 24], fill=(0, 0, 0))
        dr.text((x + 6, y + 5), lbl, fill=(244, 196, 82), font=fnt)
        os.remove(jp)

    for qp in [
        os.path.join(CHK_V6, "FINAL_V6_SURGICAL_12FRAMES_QC.jpg"),
        os.path.join(ART_DIR, "fc_food_cinematic_v6_surgical_preview.jpg"),
        os.path.join(CLOUD_PRJ, "FINAL_V6_SURGICAL_12FRAMES_QC.jpg"),
    ]:
        if qp.startswith("Z:") and not os.path.exists("Z:\\"):
            continue
        sheet.save(qp, quality=92)

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

    if os.path.exists("Z:\\"):
        shutil.copy2(__file__, os.path.join(CLOUD_PRJ, os.path.basename(__file__)))
    print("V6 SURGICAL FIX ON V4 COMPLETE!", flush=True)

if __name__ == "__main__":
    main()
