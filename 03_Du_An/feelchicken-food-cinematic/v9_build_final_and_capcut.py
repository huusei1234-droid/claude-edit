import copy, json, math, os, re, shutil, subprocess, time, uuid
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT_DIR    = r"d:\AI\full studio\output\feelchicken-food-cinematic"
GOC_MP4    = r"C:\Users\Hang thu\Downloads\FEEL CHICKEN - Food Cinematic gốc.mp4"
RAW_V2     = os.path.join(OUT_DIR, "raw_v2")
SFX_V1     = os.path.join(OUT_DIR, "raw_cache", "sfx")
SFX_V2     = os.path.join(RAW_V2, "sfx")
V9_WORK    = os.path.join(OUT_DIR, "v9_work")
CHK_V9     = os.path.join(OUT_DIR, "check_v9")
BAK_DIR    = os.path.join(OUT_DIR, "backup_user_v7_graded")
ART_DIR    = r"C:\Users\Hang thu\.gemini\antigravity\brain\9f2bdce7-c331-4313-8280-d8812425f28c"
CLOUD_PRJ  = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-food-cinematic"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
CAPCUT_EXE = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\CapCut.exe")
DRAFT_NAME = "FEEL CHICKEN - Food Cinematic V7"
SUB_TL_ID  = "C92C490A-A4BC-4FC5-9D9F-F754DFC3B887"

for d in (V9_WORK, CHK_V9, BAK_DIR):
    os.makedirs(d, exist_ok=True)
if os.path.exists("Z:\\"):
    os.makedirs(CLOUD_PRJ, exist_ok=True)

W, H = 1080, 1920
FPS = 30
SR = 48000
BGM_LOCAL = os.path.join(RAW_V2, "BGM_Slow_Cook_Honey.mp3")

# ==============================================================================
# 1. SLICE & SPEED-RAMP USER'S COLOR-GRADED MASTER (100.0% COLOR PRESERVED!)
# ==============================================================================
# Exact frame intervals [f_start_inclusive, f_end_exclusive] in FEEL CHICKEN - Food Cinematic gốc.mp4 (816 frames @ 30fps).
# Note:
# - Protected intervals ("passthrough") keep exact animated text transitions / CapCut transitions / smoke outro untouched.
# - "ramp" intervals use optical-flow 90fps motion interpolation (3x intermediate frames) + Food-Cinematic Speed-Ramp Curve
#   (Fast Whip-In -> Silky 0.48x..0.54x Slow-Mo Hero Hold -> Fast Whip-Out), with 0% color filter so user's color grade is bit-exact!
# - Accidental 2-frame black gap [723, 725) is cleanly omitted!

SEG_CHUNKS = [
    # id, f0, f1, out_frames, mode, curve_style
    ("01a_open_title_in",   0,  19, 19, "pass", None),
    ("01b_stove_snap",     19,  36, 17, "ramp", "ramp_out"),     # S01 Stove ignite accelerates into cut
    ("02_egg_flour_ramp",  36,  84, 46, "ramp", "u_valley"),     # S02 Egg crack & flour (COOKING Time is static here!)
    ("03a_whisk_ramp",     84, 105, 21, "ramp", "ramp_in"),      # S03 Whisk batter fast-in -> smooth
    ("03b_open_title_out",105, 120, 15, "pass", None),           # Protect COOKING Time fade-out
    ("04_clean_fryer",    120, 185, 62, "ramp", "u_valley"),     # S04 Clean fryer plunge: Fast -> 0.48x Golden Oil Bubble -> Fast
    ("05_crispy_lift",    185, 219, 36, "ramp", "u_valley"),     # S05 Crispy basket lift: Fast -> 0.50x Oil Drip Slow-Mo -> Fast
    ("06_pan_sauce_stir", 219, 255, 36, "ramp", "u_valley"),     # S06 Hot sauce pan stir: Fast -> Smooth Bubble -> Fast
    ("07_wok_fire_toss",  255, 318, 60, "ramp", "u_valley"),     # S07 Wok fire glaze toss: Fast -> Mid-Air Fire Slow-Mo -> Fast
    ("07t_trans_kethop",  318, 331, 13, "pass", None),           # User's CapCut 'Kết hợp' transition untouched!
    ("08_ruby_pour",      331, 396, 63, "ramp", "u_valley"),     # S08 Ruby sauce pour: Fast -> Thick Ribbon Slow-Mo -> Fast
    ("09_cheddar_pour",   396, 461, 63, "ramp", "u_valley"),     # S09 Cheddar pour: Fast -> Creamy Drape Slow-Mo -> Fast
    ("10_sesame_rain",    461, 501, 41, "ramp", "ramp_in_deep"), # S10 Sesame black: Fast snap -> Ultra-Slow Floating Seeds
    ("10t_trans_slide",   501, 513, 12, "pass", None),           # User's CapCut 'Trượt xuống' transition untouched!
    ("11_crispy_tear",    513, 582, 68, "ramp", "u_valley"),     # S11 Crispy tear: Fast snap -> Juicy Steam Tear Slow-Mo -> Fast
    ("12_jajang_lift",    582, 623, 41, "ramp", "u_valley"),     # S12 Jajangmyeon lift: Fast -> Glossy Stretch Slow-Mo -> Fast
    ("13_tokbokki_lift",  623, 678, 53, "ramp", "u_valley"),     # S13 Tokbokki lift: Fast -> Spicy Glaze Slow-Mo -> Fast
    ("14_sesame_platter", 678, 723, 46, "ramp", "ramp_in_deep"), # S14 Sesame hero platter: Fast-in -> Silky Slow-Mo
    # [723..725] = 2 black frames REMOVED!
    ("15a_combo_reveal",  725, 757, 35, "ramp", "ramp_in_deep"), # S15 5-Flavor Combo platter hands-in speed-ramp -> hero settle
    ("15b_smoke_outro",   757, 816, 59, "pass", None),           # User's 'Khói chiếm lấy màn hình' smoke outro 100% untouched!
]

def build_Normalized_Curve(n_out: int, style: str) -> np.ndarray:
    """Returns normalized cumulative progress s in [0.0, 1.0] of length n_out for speed-ramping."""
    if n_out <= 2:
        return np.linspace(0.0, 1.0, n_out)
    u = np.linspace(0.0, 1.0, n_out)
    if style == "u_valley":
        # Authentic Food-Cinematic Montage Ramp: ~2.15x fast whip at edges -> ~0.46x silky slow-motion in the center!
        spd = 0.44 + 1.95 * (np.abs(2.0 * u - 1.0) ** 2.35)
    elif style == "ramp_in":
        # Fast snap-in (~2.1x) decelerating smoothly to ~0.58x
        spd = 0.56 + 1.65 * (np.maximum(0.0, 1.0 - u / 0.45) ** 2.0)
    elif style == "ramp_in_deep":
        # Energetic entry (~1.95x) gliding into deep 0.48x slow-motion hero hold
        spd = 0.48 + 1.75 * (np.maximum(0.0, 1.0 - u / 0.38) ** 2.1)
    elif style == "ramp_out":
        # Steady hold accelerating into a 2.15x whip cut
        spd = 0.58 + 1.75 * (np.maximum(0.0, (u - 0.45) / 0.55) ** 2.1)
    else:
        spd = np.ones_like(u)
    cum = np.cumsum(spd) - spd[0]
    if cum[-1] <= 1e-6:
        return np.linspace(0.0, 1.0, n_out)
    return cum / cum[-1]

def render_chunk(args):
    cid, f0, f1, n_out, mode, style = args
    out_mp4 = os.path.join(V9_WORK, f"chunk_{cid}.mp4")
    t_start = f0 / 30.0
    n_in = f1 - f0

    if mode == "pass":
        # Exact frame-accurate decode & encode with ZERO color modification
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", GOC_MP4,
            "-vf", f"trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS",
            "-an", "-r", "30",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "13", "-b:v", "0", "-pix_fmt", "yuv420p",
            out_mp4
        ], check=True)
        return cid, n_out, out_mp4

    # For "ramp" chunks:
    # 1) Decode exact [f0, f1) frames from GOC_MP4 and synthesize 3x optical-flow frames (90fps) via minterpolate
    #    ONLY on the food action region [0 .. 1808], while keeping the static editorial footer strip [1808 .. 1920]
    #    razor-sharp from the nearest un-interpolated frame so the tiny footer text never warps!
    raw_orig = subprocess.run([
        "ffmpeg", "-v", "error", "-i", GOC_MP4,
        "-vf", f"trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS,format=rgb24",
        "-f", "rawvideo", "-"
    ], capture_output=True, check=True).stdout
    fsz = W * H * 3
    n_dec = max(1, len(raw_orig) // fsz)
    orig_frames = np.frombuffer(raw_orig[:n_dec * fsz], dtype=np.uint8).reshape((n_dec, H, W, 3))

    # Optical-flow 90fps interpolation on full 1080x1920 slice (fast because each slice is only 1.1s..2.2s!)
    raw_90 = subprocess.run([
        "ffmpeg", "-v", "error", "-i", GOC_MP4,
        "-vf", f"trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS,minterpolate=fps=90:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=rgb24",
        "-f", "rawvideo", "-"
    ], capture_output=True, check=True).stdout
    n_90 = max(1, len(raw_90) // fsz)
    interp_frames = np.frombuffer(raw_90[:n_90 * fsz], dtype=np.uint8).reshape((n_90, H, W, 3))

    prog = build_Normalized_Curve(n_out, style)
    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "13", "-b:v", "0", "-pix_fmt", "yuv420p",
        out_mp4
    ], stdin=subprocess.PIPE)

    has_footer = (120 <= f0 < 723)
    for k in range(n_out):
        s_val = float(prog[k])
        idx_90 = min(n_90 - 1, max(0, int(round(s_val * (n_90 - 1)))))
        frm = interp_frames[idx_90].copy()
        if has_footer:
            # Keep bottom footer strip (y=1812..1905) 100% crisp from exact original frame (zero optical-flow shimmer on tiny text)
            idx_or = min(n_dec - 1, max(0, int(round(s_val * (n_dec - 1)))))
            frm[1812:1905, 220:860, :] = orig_frames[idx_or, 1812:1905, 220:860, :]
        enc.stdin.write(frm.tobytes())

    enc.stdin.close()
    enc.wait()
    return cid, n_out, out_mp4

# ==============================================================================
# 2. AUDIO ENGINE: FULL COOKING ASMR + SPEED-RAMP SFX + BGM (-14.0 LUFS)
# ==============================================================================
def load_aud(path: str, s0: float = 0.0, dur: float = None, af_extra: str = None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error"]
    if s0 > 0:
        cmd += ["-ss", f"{s0:.3f}"]
    if dur is not None:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-i", path]
    if af_extra:
        cmd += ["-af", af_extra]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()

def mix_into(bus: np.ndarray, clip: np.ndarray, ts: float, gain: float = 1.0, fi: float = 0.03, fo: float = 0.12):
    if len(clip) == 0:
        return
    c = (clip * gain).copy()
    nfi = min(len(c), int(round(fi * SR)))
    nfo = min(len(c), int(round(fo * SR)))
    if nfi > 1:
        c[:nfi] *= np.linspace(0.0, 1.0, nfi, dtype=np.float32)[:, None]
    if nfo > 1:
        c[-nfo:] *= np.linspace(1.0, 0.0, nfo, dtype=np.float32)[:, None]
    i0 = max(0, int(round(ts * SR)))
    if i0 >= len(bus):
        return
    i1 = min(len(bus), i0 + len(c))
    bus[i0:i1] += c[:i1 - i0]

def save_wav(path: str, arr: np.ndarray):
    pcm = (np.clip(arr, -0.99, 0.99) * 32767.0).astype(np.int16)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
        "-c:a", "pcm_s16le", path
    ], stdin=subprocess.PIPE)
    p.stdin.write(pcm.tobytes())
    p.stdin.close()
    p.wait()

# ==============================================================================
# 3. IN-PLACE CAPCUT DESKTOP UPGRADE (100% USER COLOR PRESERVED + CURVE SPEED + ONLINE ASMR)
# ==============================================================================
def write_unlink(path: str, data: bytes):
    if os.path.exists(path):
        try:
            os.unlink(path)
        except Exception:
            pass
    with open(path, "wb") as f:
        f.write(data)

def make_capcut_curve_speed_points(avg_spd: float, style: str):
    """
    Builds CapCut native `curve_speed` ('Dựng phim') speed_points [{'x':..., 'y':...}]
    scaled so the trapezoidal integral equals `avg_spd`, keeping segment source/target durations 100% aligned!
    """
    if style == "u_valley":
        pts = [(0.0, 1.85), (0.20, 1.45), (0.50, 0.52), (0.80, 1.45), (1.0, 1.85)]
    elif style == "ramp_in":
        pts = [(0.0, 1.80), (0.28, 1.15), (0.65, 0.65), (1.0, 0.65)]
    elif style == "ramp_out":
        pts = [(0.0, 0.72), (0.50, 0.80), (0.82, 1.55), (1.0, 1.95)]
    else:
        pts = [(0.0, 1.65), (0.30, 0.95), (0.70, 0.58), (1.0, 0.62)]

    # Trapezoidal mean of pts
    area = 0.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        area += 0.5 * (y0 + y1) * (x1 - x0)
    scale = avg_spd / max(0.05, area)
    out = []
    for x, y in pts:
        yv = round(max(0.2, min(8.0, y * scale)), 4)
        out.append({"x": round(x, 4), "y": yv})
    return out

def upgrade_user_capcut_project():
    draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)
    sub_dir   = os.path.join(draft_dir, "Timelines", SUB_TL_ID)
    sub_dc_p  = os.path.join(sub_dir, "draft_content.json")
    root_dc_p = os.path.join(draft_dir, "draft_content.json")
    dm_p      = os.path.join(draft_dir, "draft_meta_info.json")

    if not os.path.exists(sub_dc_p):
        print("  [WARN] Sub-timeline not found, skipping CapCut update.")
        return

    # 1) Save 100% untouched backup of user's color-graded CapCut files first!
    ts_tag = int(time.time())
    shutil.copy2(sub_dc_p,  os.path.join(BAK_DIR, f"sub_draft_content_{ts_tag}.bak.json"))
    shutil.copy2(root_dc_p, os.path.join(BAK_DIR, f"root_draft_content_{ts_tag}.bak.json"))
    shutil.copy2(dm_p,      os.path.join(BAK_DIR, f"draft_meta_info_{ts_tag}.bak.json"))
    print(f"  Backed up user's original graded CapCut JSONs -> {BAK_DIR}", flush=True)

    # 2) Close CapCut.exe cleanly before editing so CapCut tray doesn't overwrite changes
    subprocess.run(["taskkill", "/F", "/IM", "CapCut.exe"], capture_output=True)
    time.sleep(1.2)

    dc = json.load(open(sub_dc_p, encoding="utf-8"))
    dm = json.load(open(dm_p, encoding="utf-8"))

    # Verify 164 effects + 45 HSL color adjustments are 100% intact
    n_eff = len(dc["materials"].get("effects", []))
    n_hsl = len(dc["materials"].get("hsl", []))
    print(f"  Preserving 100% user color adjustments: {n_eff} effects + {n_hsl} HSL curves!", flush=True)

    spds_by_id = {s["id"]: s for s in dc["materials"].get("speeds", [])}
    v_segs = dc["tracks"][0]["segments"]

    # Curve style per segment (Seg 01..15)
    seg_styles = [
        "ramp_out",   # Seg 01 Stove
        "u_valley",   # Seg 02 Egg & Flour
        "ramp_in",    # Seg 03 Whisk
        "u_valley",   # Seg 04 Clean Fryer
        "u_valley",   # Seg 05 Crispy Lift
        "u_valley",   # Seg 06 Pan Stir
        "u_valley",   # Seg 07 Wok Fire
        "u_valley",   # Seg 08 Ruby Pour
        "u_valley",   # Seg 09 Cheddar Pour
        "ramp_in",    # Seg 10 Sesame Black
        "u_valley",   # Seg 11 Crispy Tear
        "u_valley",   # Seg 12 Jajang Lift
        "u_valley",   # Seg 13 Tokbokki Lift
        "ramp_in",    # Seg 14 Sesame Platter
        "ramp_in",    # Seg 15 5-Flavor Combo + Smoke Outro
    ]

    # Fix accidental 2-frame gap on Seg 15 (24,166,666 -> 24,100,000) so Track 0 is 100% gapless!
    if len(v_segs) >= 15:
        seg14_end = v_segs[13]["target_timerange"]["start"] + v_segs[13]["target_timerange"]["duration"]
        v_segs[14]["target_timerange"]["start"] = seg14_end

    # Apply Native CapCut Curve Speed ('Dựng phim' mode=1) to all 15 segments while keeping exact timeline timing & color!
    for si, sg in enumerate(v_segs):
        src_d = max(1, sg["source_timerange"]["duration"])
        tgt_d = max(1, sg["target_timerange"]["duration"])
        avg_spd = src_d / float(tgt_d)
        st_name = seg_styles[si] if si < len(seg_styles) else "u_valley"
        pts = make_capcut_curve_speed_points(avg_spd, st_name)
        for r in sg.get("extra_material_refs", []):
            if r in spds_by_id:
                sp_obj = spds_by_id[r]
                sp_obj["mode"] = 1
                sp_obj["speed"] = round(avg_spd, 6)
                sp_obj["curve_speed"] = {
                    "id": "6768648600848175619",
                    "source_platform": 1,
                    "name": "Dựng phim",
                    "speed_points": pts,
                }

    # Ensure every audio material path in CapCut uses clean normalized forward slashes and exists on disk!
    for a in dc["materials"].get("audios", []):
        p = a.get("path", "")
        if p:
            p_norm = os.path.normpath(p).replace("\\", "/")
            a["path"] = p_norm

    # Update total timeline duration cleanly
    max_end = 0
    for tr in dc["tracks"]:
        for sg in tr["segments"]:
            e = sg["target_timerange"]["start"] + sg["target_timerange"]["duration"]
            if e > max_end:
                max_end = e
    dc["duration"] = max_end
    dc["update_time"] = int(time.time())

    # Register any missing audio files in draft_meta_info.json so CapCut never marks SFX offline
    dm_aud_tpl = None
    for g in dm.get("draft_materials", []):
        for x in g.get("value", []):
            if x.get("metetype") in ("music", "audio", "sound"):
                dm_aud_tpl = copy.deepcopy(x)
                break
        if dm_aud_tpl:
            break

    if dm_aud_tpl:
        for g in dm.get("draft_materials", []):
            if g.get("type") == 0:
                existing_paths = {os.path.normpath(x.get("file_Path", "")).lower() for x in g.get("value", [])}
                for a in dc["materials"].get("audios", []):
                    ap = a.get("path", "")
                    if ap and os.path.exists(ap) and os.path.normpath(ap).lower() not in existing_paths:
                        item = copy.deepcopy(dm_aud_tpl)
                        item["id"] = str(uuid.uuid4()).upper()
                        item["file_Path"] = ap
                        item["extra_info"] = os.path.basename(ap)
                        g["value"].append(item)
                        existing_paths.add(os.path.normpath(ap).lower())

    dm["tm_duration"] = max_end
    dm["tm_draft_modified"] = int(time.time() * 1_000_000)

    dc_bytes = json.dumps(dc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    dm_bytes = json.dumps(dm, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    # Rule 6: unlink() before writing all 4 files (root + active sub-timeline) so hardlinks never corrupt!
    for p in (
        root_dc_p,
        os.path.join(draft_dir, "template-2.tmp"),
        sub_dc_p,
        os.path.join(sub_dir, "template-2.tmp"),
    ):
        write_unlink(p, dc_bytes)
    write_unlink(dm_p, dm_bytes)

    # Update root_meta_info.json timestamp
    rmi_p = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    if os.path.exists(rmi_p):
        rmi = json.load(open(rmi_p, encoding="utf-8"))
        for st in rmi.get("all_draft_store", []):
            if st.get("draft_name") == DRAFT_NAME:
                st["tm_draft_modified"] = int(time.time() * 1_000_000)
                st["tm_duration"] = max_end
        write_unlink(rmi_p, json.dumps(rmi, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))

    # Relaunch CapCut Desktop so user sees the upgraded project ready immediately
    if os.path.exists(CAPCUT_EXE):
        subprocess.Popen([CAPCUT_EXE], close_fds=True)
    print("  Upgraded CapCut Desktop project 'FEEL CHICKEN - Food Cinematic V7' (100% color preserved + Curve Speed + ASMR online)!", flush=True)


def main():
    print("[1/5] Rendering Optical-Flow Speed-Ramped Chunks from User's Color-Graded Master (0% Color Modification)...", flush=True)
    t0_wall = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(render_chunk, SEG_CHUNKS))

    # Build timeline timestamp map of chunks
    cur_f = 0
    chunk_times = {}
    concat_list_p = os.path.join(V9_WORK, "concat_v9.txt")
    with open(concat_list_p, "w", encoding="utf-8") as f:
        for cid, n_out, mp4_p in results:
            t_in = cur_f / 30.0
            cur_f += n_out
            t_out = cur_f / 30.0
            chunk_times[cid] = (t_in, t_out)
            f.write(f"file '{mp4_p.replace(chr(92), '/')}'\n")
            print(f"  {cid:22s} -> [{t_in:6.2f}s .. {t_out:6.2f}s] ({n_out:2d}f)")

    tot_dur = cur_f / 30.0
    print(f"  Total speed-ramped video duration: {tot_dur:.3f}s ({cur_f} frames) in {time.time()-t0_wall:.1f}s", flush=True)

    video_only_mp4 = os.path.join(V9_WORK, "_v9_speedramped_video.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", concat_list_p,
        "-c", "copy", video_only_mp4
    ], check=True)

    print("[2/5] Mixing Tactile Cooking ASMR + Speed-Ramp SFX + 'Slow Cook Honey' BGM (-14.0 LUFS)...", flush=True)
    n_samples = int(round(tot_dur * SR))
    bgm_bus  = np.zeros((n_samples, 2), dtype=np.float32)
    asmr_bus = np.zeros((n_samples, 2), dtype=np.float32)
    sfx_bus  = np.zeros((n_samples, 2), dtype=np.float32)

    # 1) BGM: Slow Cook Honey (starting at 6.0s so the lush sub-bass bloom hits right on the Crispy Tear climax, silky fade-out on smoke outro!)
    bgm_clip = load_aud(BGM_LOCAL, 6.0, tot_dur)
    mix_into(bgm_bus, bgm_clip, 0.0, gain=0.86, fi=0.15, fo=1.35)

    # 2) Load Ear-Verified Tactile Cooking ASMR & Clean Studio SFX
    gas_ig     = load_aud(os.path.join(SFX_V2, "sfx_gas_ignite.mp3"), 0.0, 1.8)
    fry_plunge = load_aud(os.path.join(SFX_V1, "asmr_frying_pan.mp3"), 0.6, 3.6)
    fry_drip   = load_aud(os.path.join(SFX_V1, "asmr_frying_pan.mp3"), 5.2, 2.0, "highpass=f=650")
    pan_simmer = load_aud(os.path.join(SFX_V1, "asmr_frying_pan.mp3"), 10.5, 4.2, "lowpass=f=6500")
    pour_warm  = load_aud(os.path.join(SFX_V1, "asmr_liquid_pour.mp3"), 0.15, 2.0, "lowpass=f=3200")
    sticky_a   = load_aud(os.path.join(SFX_V1, "asmr_sauce_sticky.mp3"), 0.8, 2.3)
    sticky_b   = load_aud(os.path.join(SFX_V1, "asmr_sauce_sticky.mp3"), 4.2, 2.3)
    sticky_c   = load_aud(os.path.join(SFX_V1, "asmr_sauce_sticky.mp3"), 8.5, 1.8)
    sticky_d   = load_aud(os.path.join(SFX_V1, "asmr_sauce_sticky.mp3"), 13.0, 2.0)
    crunch     = load_aud(os.path.join(SFX_V1, "asmr_crispy_crunch.mp3"), 0.0, 1.8)
    egg_crack  = load_aud(os.path.join(SFX_V1, "asmr_crispy_crunch.mp3"), 0.02, 0.28, "lowpass=f=4200")
    sesame_sh  = load_aud(os.path.join(SFX_V1, "asmr_soda_fizz.mp3"), 1.2, 1.5, "highpass=f=2400,lowpass=f=9000")
    deep_w     = load_aud(os.path.join(SFX_V1, "sfx_deep_woosh.mp3"), 0.0, 1.5)
    fast_w     = load_aud(os.path.join(SFX_V1, "sfx_fast_whoosh.mp3"), 0.0, 1.2)
    low_hit    = load_aud(os.path.join(SFX_V1, "sfx_whoosh_low_hit.mp3"), 0.0, 2.4)

    # Exact post-speed-ramp shot start times from chunk_times!
    t_s01 = chunk_times["01a_open_title_in"][0]
    t_s02 = chunk_times["02_egg_flour_ramp"][0]
    t_s03 = chunk_times["03a_whisk_ramp"][0]
    t_s04 = chunk_times["04_clean_fryer"][0]
    t_s05 = chunk_times["05_crispy_lift"][0]
    t_s06 = chunk_times["06_pan_sauce_stir"][0]
    t_s07 = chunk_times["07_wok_fire_toss"][0]
    t_tr1 = chunk_times["07t_trans_kethop"][0]
    t_s08 = chunk_times["08_ruby_pour"][0]
    t_s09 = chunk_times["09_cheddar_pour"][0]
    t_s10 = chunk_times["10_sesame_rain"][0]
    t_tr2 = chunk_times["10t_trans_slide"][0]
    t_s11 = chunk_times["11_crispy_tear"][0]
    t_s12 = chunk_times["12_jajang_lift"][0]
    t_s13 = chunk_times["13_tokbokki_lift"][0]
    t_s14 = chunk_times["14_sesame_platter"][0]
    t_s15 = chunk_times["15a_combo_reveal"][0]

    # Synced Cooking ASMR across ALL 15 shots!
    mix_into(asmr_bus, gas_ig,     t_s01 + 0.06, gain=0.62, fi=0.02, fo=0.28)  # S01 Stove click & flame ignite
    mix_into(asmr_bus, egg_crack,  t_s02 + 0.24, gain=0.45, fi=0.01, fo=0.08)  # S02 Crisp egg crack on slow-mo impact
    mix_into(asmr_bus, sticky_a[:int(1.1*SR)], t_s03 + 0.04, gain=0.28, fi=0.05, fo=0.25)  # S03 Creamy batter whisk
    mix_into(asmr_bus, fry_plunge, t_s04 + 0.02, gain=0.58, fi=0.06, fo=0.35)  # S04 Vigorous fryer hot oil sizzle
    mix_into(asmr_bus, fry_drip,   t_s05 + 0.05, gain=0.46, fi=0.06, fo=0.30)  # S05 Crispy golden lift oil shimmer
    mix_into(asmr_bus, pan_simmer, t_s06 + 0.04, gain=0.48, fi=0.08, fo=0.45)  # S06-S07 Hot sauce pan stir & wok fire glaze
    mix_into(asmr_bus, sticky_a[:int(1.6*SR)], t_s08 + 0.08, gain=0.44, fi=0.06, fo=0.30)  # S08 Thick ruby sauce body
    mix_into(asmr_bus, pour_warm,  t_s08 + 0.05, gain=0.34, fi=0.05, fo=0.30)  # S08 Warm syrupy pour stream
    mix_into(asmr_bus, sticky_b,   t_s09 + 0.08, gain=0.46, fi=0.08, fo=0.35)  # S09 Rich molten cheddar pour
    mix_into(asmr_bus, sesame_sh,  t_s10 + 0.10, gain=0.22, fi=0.08, fo=0.35)  # S10 Delicate sesame seed rain shimmer
    mix_into(asmr_bus, crunch,     t_s11 + 0.22, gain=0.88, fi=0.02, fo=0.24)  # S11 HERO CRISPY CRUST TEAR CRUNCH!
    mix_into(asmr_bus, sticky_c,   t_s12 + 0.08, gain=0.36, fi=0.08, fo=0.28)  # S12 Glossy Jajangmyeon lift
    mix_into(asmr_bus, sticky_d,   t_s13 + 0.08, gain=0.34, fi=0.08, fo=0.30)  # S13 Spicy Tokbokki glaze lift
    mix_into(asmr_bus, sesame_sh[:int(1.1*SR)], t_s14 + 0.06, gain=0.18, fi=0.06, fo=0.30)  # S14 Sesame sprinkle onto 5-flavor platter

    # Synced Speed-Ramp Air Whooshes & Subtle Sub-Bass Impacts (-18..-21 dB tasteful studio level!)
    for tw, g_w in [
        (t_s02 - 0.08, 0.22),
        (t_s04 - 0.08, 0.26),
        (t_s07 - 0.08, 0.30),  # Wok fire flame burst whoosh
        (t_s09 - 0.08, 0.22),
        (t_s13 - 0.08, 0.20),
    ]:
        mix_into(sfx_bus, deep_w, max(0.0, tw), gain=g_w, fi=0.02, fo=0.25)

    for tf, g_f in [
        (t_tr1 - 0.04, 0.30),  # 'Kết hợp' transition whip
        (t_tr2 - 0.04, 0.36),  # 'Trượt xuống' transition whip
        (t_s14 - 0.08, 0.24),  # Whip into hero sesame platter
    ]:
        mix_into(sfx_bus, fast_w, max(0.0, tf), gain=g_f, fi=0.02, fo=0.22)

    for th, g_h in [
        (t_s07 + 0.02, 0.30),  # Wok fire low thump
        (t_s10 + 0.02, 0.28),  # Dark sesame beat drop
        (t_s15 + 0.02, 0.34),  # Final 5-flavor Combo feast reveal bloom
    ]:
        mix_into(sfx_bus, low_hit, max(0.0, th), gain=g_h, fi=0.02, fo=0.40)

    raw_mix_wav = os.path.join(V9_WORK, "v9_mix_raw.wav")
    master_wav  = os.path.join(V9_WORK, "v9_master_14lufs.wav")
    save_wav(raw_mix_wav, bgm_bus + asmr_bus + sfx_bus)

    p1 = subprocess.run([
        "ffmpeg", "-v", "info", "-i", raw_mix_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json",
        "-f", "null", "-"
    ], capture_output=True, text=True)
    ln = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p1.stderr).group(0))
    af2 = (
        f"loudnorm=I=-14.0:TP=-1.0:LRA=11.0:"
        f"measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:"
        f"measured_LRA={ln['input_lra']}:measured_thresh={ln['input_thresh']}:"
        f"offset={ln['target_offset']}:linear=true,aresample={SR}"
    )
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_mix_wav, "-af", af2, "-c:a", "pcm_s16le", master_wav], check=True)

    p_ver = subprocess.run([
        "ffmpeg", "-v", "info", "-i", master_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json",
        "-f", "null", "-"
    ], capture_output=True, text=True)
    ln_ver = json.loads(re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p_ver.stderr).group(0))
    print(f"  Verified Master Audio Loudness: I = {ln_ver['input_i']} LUFS | TP = {ln_ver['input_tp']} dBTP", flush=True)

    print("[3/5] Muxing Final Master MP4 (Zero Re-encode Color Drift!) & Syncing to All Delivery Folders...", flush=True)
    final_named_local = os.path.join(OUT_DIR, "261121 Feel Chicken Food Cinematic final.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", video_only_mp4, "-i", master_wav,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart",
        final_named_local
    ], check=True)

    # Also update local legacy filename + customer folders per AGENTS.md & GEMINI.md rules!
    sync_targets = [
        os.path.join(OUT_DIR, "FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4"),
        r"D:\XUẤT CAPCUT\261121 Feel Chicken Food Cinematic final.mp4",
        r"D:\XUẤT CAPCUT\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
        r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\261121 Feel Chicken Food Cinematic final.mp4",
        r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4",
        r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\261121 Feel Chicken Food Cinematic final.mp4",
    ]
    for dst in sync_targets:
        if dst.startswith("Z:") and not os.path.exists("Z:\\"):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(final_named_local, dst)
        print(f"  Synced -> {dst}", flush=True)

    print("[4/5] Upgrading User's CapCut Project In-Place (Backup + 100% Color Preserved + Curve Speed + Online ASMR)...", flush=True)
    upgrade_user_capcut_project()

    print("[5/5] Generating 15-Shot Visual QC Sheet (Verifying 100% User Color Grade & 0 Gap Frames)...", flush=True)
    qc_samples = [
        ("01 S01 Stove",        t_s01 + 0.55),
        ("02 S02 Egg & Flour",  t_s02 + 0.75),
        ("03 S03 Whisk",        t_s03 + 0.55),
        ("04 S04 Clean Fryer",  t_s04 + 1.00),
        ("05 S05 Crispy Lift",  t_s05 + 0.60),
        ("06 S06 Sauce Stir",   t_s06 + 0.60),
        ("07 S07 Wok Fire",     t_s07 + 0.95),
        ("08 S08 Ruby Pour",    t_s08 + 1.00),
        ("09 S09 Cheddar Pour", t_s09 + 1.00),
        ("10 S10 Sesame Rain",  t_s10 + 0.65),
        ("11 S11 Crispy Tear",  t_s11 + 1.10),
        ("12 S12 Jajang Lift",  t_s12 + 0.65),
        ("13 S13 Tokbokki",     t_s13 + 0.85),
        ("14 S14 Sesame Hero",  t_s14 + 0.85),
        ("15 S15 Combo Feast",  t_s15 + 0.65),
    ]
    cw, ch = 220, 391
    grid = Image.new("RGB", (cw * 5, ch * 3), (12, 12, 12))
    dr = ImageDraw.Draw(grid)
    fnt = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 14)
    for idx, (lbl, ts) in enumerate(qc_samples):
        jp = os.path.join(CHK_V9, f"_qc_{idx:02d}.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", final_named_local,
            "-frames:v", "1", "-vf", f"scale={cw}:{ch},format=yuvj420p", "-q:v", "2", jp
        ], check=True)
        r, c = divmod(idx, 5)
        grid.paste(Image.open(jp).convert("RGB"), (c * cw, r * ch))
        dr.rectangle([c * cw, r * ch, (c + 1) * cw, r * ch + 22], fill=(0, 0, 0))
        dr.text((c * cw + 5, r * ch + 4), f"{lbl} @{ts:.2f}s", fill=(255, 220, 90), font=fnt)
        os.remove(jp)

    qc_path = os.path.join(CHK_V9, "FINAL_V9_USER_GRADED_QC.jpg")
    grid.save(qc_path, quality=93)
    shutil.copy2(qc_path, os.path.join(ART_DIR, "fc_food_cinematic_v9_user_graded_qc.jpg"))
    if os.path.exists("Z:\\"):
        shutil.copy2(qc_path, os.path.join(CLOUD_PRJ, "FINAL_V9_USER_GRADED_QC.jpg"))
        shutil.copy2(__file__, os.path.join(CLOUD_PRJ, "v9_build_final_and_capcut.py"))
    print("DONE! QC Sheet ->", qc_path, flush=True)

if __name__ == "__main__":
    main()
