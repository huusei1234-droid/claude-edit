import os
import sys
import json
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

PROJ = r"d:\AI\full studio\projects\winhair-cs2-tvc"
SCRATCH = os.path.join(PROJ, "scratch_media")
Z_RAW_DIR = os.path.join(SCRATCH, "z_raw")
VID_OUT_DIR = os.path.join(PROJ, "assets", "video")

PDIR = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\TVC WinHair CS2 - ban Reels_v2 (1)-sao chép (1)"
DC_PATH = os.path.join(PDIR, "Timelines", "C8D29776-5FFB-4dd3-8698-E26DA5C9C410", "draft_content.json")
LOCAL_MAT_VID = os.path.join(PDIR, "materials", "video")
LOCAL_FINAL = os.path.join(SCRATCH, "raw_final.mp4")

with open(DC_PATH, "r", encoding="utf-8") as f:
    dc = json.load(f)

mats = dc["materials"]
videos_map = {v["id"]: v for v in mats.get("videos", [])}
speeds_map = {s["id"]: s for s in mats.get("speeds", [])}

def resolve_local_video_path(raw_p):
    if not raw_p:
        return ""
    if "##_draftpath_placeholder_" in raw_p:
        suffix = raw_p.split("_placeholder_")[-1].split("##")[-1].lstrip("\\/")
        raw_p = os.path.join(PDIR, suffix)
    raw_p = os.path.normpath(raw_p)
    if raw_p.upper().startswith("Z:"):
        bname = os.path.basename(raw_p)
        cand1 = os.path.join(LOCAL_MAT_VID, bname)
        cand2 = os.path.join(Z_RAW_DIR, bname)
        if os.path.exists(cand1):
            return cand1
        if os.path.exists(cand2):
            return cand2
    return raw_p

t0 = time.time()
print("=== STEP 1: Fast 1-Pass Extraction of 480x270 Color Reference Thumbnails ===")
ref_thumbs = np.zeros((9492, 270, 480, 3), dtype=np.uint8)
p_ref = subprocess.Popen([
    "ffmpeg", "-hwaccel", "cuda", "-i", LOCAL_FINAL,
    "-vf", "scale=480:270,fps=30",
    "-frames:v", "9492", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
frame_bytes_sm = 480 * 270 * 3
for i in range(9492):
    buf = p_ref.stdout.read(frame_bytes_sm)
    if len(buf) == frame_bytes_sm:
        ref_thumbs[i] = np.frombuffer(buf, dtype=np.uint8).reshape(270, 480, 3)
    elif i > 0:
        ref_thumbs[i] = ref_thumbs[i - 1]
p_ref.stdout.close()
p_ref.wait()
print(f"  Loaded 9,492 color-reference thumbnails in {time.time()-t0:.2f}s!")

print("=== STEP 2: Building Exact 9,492-Frame Pure Raw Camera Schedule ===")
t0_segs = []
for idx, seg in enumerate(dc["tracks"][0]["segments"]):
    st = seg["target_timerange"]["start"] / 1e6
    dur = seg["target_timerange"]["duration"] / 1e6
    src_st = seg["source_timerange"]["start"] / 1e6
    spd = 1.0
    for r in seg.get("extra_material_refs", []):
        if r in speeds_map:
            spd = speeds_map[r].get("speed", 1.0)
    clip_cfg = seg.get("clip") or {}
    sx = (clip_cfg.get("scale") or {}).get("x", 1.0)
    sy = (clip_cfg.get("scale") or {}).get("y", 1.0)
    tx = (clip_cfg.get("transform") or {}).get("x", 0.0)
    ty = (clip_cfg.get("transform") or {}).get("y", 0.0)
    v = videos_map.get(seg["material_id"], {})
    vp = resolve_local_video_path(v.get("path", ""))

    force_nb = False
    if idx == 30:
        vp = os.path.join(LOCAL_MAT_VID, "6CC0942E-5C01-474f-9D00-0CF6283B951E_260929 tvc (56).MP4")
        src_st, spd, sx, sy, tx, ty = 0.0, 0.70, 1.0, 1.0, 0.0, 0.0
        force_nb = True
    elif idx == 37 or not vp or not os.path.exists(vp):
        vp = os.path.join(LOCAL_MAT_VID, "260929 tvc dji  (24).MP4")
        src_st, spd, sx, sy, tx, ty = 5.60, 0.80, 1.0, 1.0, 0.0, 0.0
        force_nb = True

    t0_segs.append({
        "id": f"T0_{idx:03d}", "start": st, "end": st + dur,
        "src_start": src_st, "speed": spd, "path": vp,
        "sx": sx, "sy": sy, "tx": tx, "ty": ty, "force_nb": force_nb
    })

broll_segs = []
for tidx, allowed_idxs in [(1, [1, 2, 3, 4, 5, 6]), (3, [2, 3])]:
    for idx in allowed_idxs:
        seg = dc["tracks"][tidx]["segments"][idx]
        st = seg["target_timerange"]["start"] / 1e6
        dur = seg["target_timerange"]["duration"] / 1e6
        src_st = seg["source_timerange"]["start"] / 1e6
        spd = 1.0
        for r in seg.get("extra_material_refs", []):
            if r in speeds_map:
                spd = speeds_map[r].get("speed", 1.0)
        vp = resolve_local_video_path(videos_map[seg["material_id"]]["path"])
        broll_segs.append({
            "id": f"T{tidx}_{idx:03d}", "start": st, "end": st + dur,
            "src_start": src_st, "speed": spd, "path": vp,
            "sx": 1.0, "sy": 1.0, "tx": 0.0, "ty": 0.0, "force_nb": False
        })

TOTAL_FRAMES = 9492
frame_plan = []
t0_ptr = 0
for fidx in range(TOTAL_FRAMES):
    t = (fidx + 0.5) / 30.0
    chosen = None
    for br in broll_segs:
        if br["start"] <= t < br["end"]:
            chosen = br
            break
    if chosen is None:
        while t0_ptr < len(t0_segs) - 1 and t >= t0_segs[t0_ptr]["end"]:
            t0_ptr += 1
        chosen = t0_segs[t0_ptr]
    frame_plan.append(chosen)

# Group into contiguous frame runs
runs = []
f = 0
while f < TOTAL_FRAMES:
    seg = frame_plan[f]
    f_end = f + 1
    while f_end < TOTAL_FRAMES and frame_plan[f_end]["id"] == seg["id"]:
        f_end += 1
    t_run_start = f / 30.0
    src_t0 = seg["src_start"] + max(0.0, t_run_start - seg["start"]) * seg["speed"]
    runs.append((len(runs), f, f_end, seg, src_t0))
    f = f_end

print(f"  Built {len(runs)} contiguous pure-raw camera runs totaling {sum(r[2]-r[1] for r in runs)} frames!")

def make_warm_default_lut():
    x = np.arange(256, dtype=np.float32) / 255.0
    y = np.clip(((x ** 0.95) - 0.5) * 1.05 + 0.515, 0.0, 1.0) * 255.0
    lut = np.zeros((1, 256, 3), dtype=np.uint8)
    lut[0, :, 0] = np.clip(y * 0.98, 0, 255).astype(np.uint8)
    lut[0, :, 1] = np.clip(y * 1.00, 0, 255).astype(np.uint8)
    lut[0, :, 2] = np.clip(y * 1.02, 0, 255).astype(np.uint8)
    return lut

DEFAULT_LUT = make_warm_default_lut()
IDENTITY_LUT = np.tile(np.arange(256, dtype=np.uint8)[None, :, None], (1, 1, 3))
QUANTILES = np.array([0, 1, 3, 7, 15, 25, 40, 50, 60, 75, 85, 93, 97, 99, 100], dtype=np.float32)

def warp_pan_zoom(frame_bgr, sx, sy, tx, ty):
    if abs(sx - 1.0) < 0.005 and abs(sy - 1.0) < 0.005 and abs(tx) < 0.005 and abs(ty) < 0.005:
        return frame_bgr
    H, W = 1080, 1920
    nw = max(W, int(round(W * sx))) if sx >= 1.0 else max(1, int(round(W * sx)))
    nh = max(H, int(round(H * sy))) if sy >= 1.0 else max(1, int(round(H * sy)))
    resized = cv2.resize(frame_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
    cx = int(round(W / 2 + tx * (W / 2) - nw / 2))
    cy = int(round(H / 2 - ty * (H / 2) - nh / 2))
    if nw >= W:
        cx = min(0, max(W - nw, cx))
    if nh >= H:
        cy = min(0, max(H - nh, cy))
    canvas = np.zeros((H, W, 3), dtype=np.uint8)
    x0_d, y0_d = max(0, cx), max(0, cy)
    x1_d, y1_d = min(W, cx + nw), min(H, cy + nh)
    if x1_d > x0_d and y1_d > y0_d:
        canvas[y0_d:y1_d, x0_d:x1_d] = resized[y0_d - cy:y1_d - cy, x0_d - cx:x1_d - cx]
    return canvas

def fit_lut_from_thumb(raw_1080, ref_thumb_270, is_endcard=False):
    raw_sm = cv2.resize(raw_1080, (480, 270), interpolation=cv2.INTER_AREA)
    y1 = 200 if is_endcard else 130  # 20..130 in 270p == 80..520 in 1080p (100% above CapCut text!)
    r_patch = raw_sm[20:y1, 40:440].astype(np.float32)
    f_patch = ref_thumb_270[20:y1, 40:440].astype(np.float32)
    rl = r_patch.mean(axis=2).reshape(-1)
    fl = f_patch.mean(axis=2).reshape(-1)
    rl_c, fl_c = rl - rl.mean(), fl - fl.mean()
    corr = float(np.dot(rl_c, fl_c) / ((np.linalg.norm(rl_c) * np.linalg.norm(fl_c)) + 1e-9))
    if corr < 0.74:
        return None
    lut = np.zeros((1, 256, 3), dtype=np.uint8)
    xs = np.arange(256, dtype=np.float32)
    kernel = np.array([1, 2, 3, 2, 1], dtype=np.float32) / 9.0
    for c in range(3):
        qr = np.percentile(r_patch[:, :, c], QUANTILES)
        qf = np.percentile(f_patch[:, :, c], QUANTILES)
        qr_u, idx_u = np.unique(np.round(qr, 2), return_index=True)
        qf_u = np.maximum.accumulate(qf[idx_u])
        if len(qr_u) < 4:
            lut[0, :, c] = DEFAULT_LUT[0, :, c]
            continue
        curve = np.interp(xs, qr_u, qf_u)
        smooth = np.convolve(np.pad(curve, (2, 2), mode="edge"), kernel, mode="valid")
        lut[0, :, c] = np.round(np.maximum.accumulate(np.clip(smooth, 0, 255))).astype(np.uint8)
    return lut

# Encode each run in parallel to temporary fast lossless-ish NVENC MP4 chunks in scratch_media/runs_v2, then concat -c copy!
runs_dir = os.path.join(SCRATCH, "runs_v2")
os.makedirs(runs_dir, exist_ok=True)
FRAME_BYTES = 1920 * 1080 * 3

def process_run(run_tuple):
    ridx, f_st, f_en, seg, src_t0 = run_tuple
    n_need = f_en - f_st
    out_mp4 = os.path.join(runs_dir, f"run_{ridx:03d}.mp4")
    spd = seg["speed"]
    read_dur = (n_need / 30.0) * spd + 0.50

    vf = f"setpts=(PTS-STARTPTS)/{spd:.6f},fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
    dec = subprocess.Popen([
        "ffmpeg", "-ss", f"{src_t0:.4f}", "-t", f"{read_dur:.4f}", "-i", seg["path"],
        "-vf", vf, "-frames:v", str(n_need), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    frames = []
    while len(frames) < n_need:
        buf = dec.stdout.read(FRAME_BYTES)
        if len(buf) < FRAME_BYTES:
            break
        frm = np.frombuffer(buf, dtype=np.uint8).reshape(1080, 1920, 3)
        frm = warp_pan_zoom(frm, seg["sx"], seg["sy"], seg["tx"], seg["ty"])
        frames.append(frm)
    dec.stdout.close()
    dec.wait()

    if not frames:
        frames = [np.zeros((1080, 1920, 3), dtype=np.uint8)]
    while len(frames) < n_need:
        frames.append(frames[-1])

    # Fit static color LUT on the middle frame of this run!
    bname = os.path.basename(seg["path"])
    if "Partículas" in bname:
        lut = IDENTITY_LUT
    elif seg["force_nb"]:
        # Fit from adjacent clean segment frame if same camera family or use warm salon grade
        lut = DEFAULT_LUT
    else:
        mid_local = len(frames) // 2
        mid_global = min(9491, f_st + mid_local)
        lut = fit_lut_from_thumb(frames[mid_local], ref_thumbs[mid_global], is_endcard=(mid_global > 9230))
        if lut is None:
            lut = DEFAULT_LUT

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30", "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "17", "-b:v", "0",
        "-g", "15", "-bf", "0", "-pix_fmt", "yuv420p", out_mp4
    ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for frm in frames:
        enc.stdin.write(cv2.LUT(frm, lut).tobytes())
    enc.stdin.close()
    enc.wait()
    return ridx, n_need, out_mp4

print(f"=== STEP 3: Parallel Decoding, Color-Matching & NVENC Encoding {len(runs)} Pure-Raw Runs ===")
t_par = time.time()
done_runs = 0
results = [None] * len(runs)
# Note: RTX 3060 consumer driver supports up to 5 concurrent NVENC sessions simultaneously -> use max_workers=4!
with ThreadPoolExecutor(max_workers=4) as ex:
    for ridx, n_need, out_mp4 in ex.map(process_run, runs):
        results[ridx] = out_mp4
        done_runs += 1
        if done_runs % 25 == 0 or done_runs == len(runs):
            print(f"  Completed {done_runs}/{len(runs)} runs ({time.time()-t_par:.1f}s)...")

concat_txt = os.path.join(runs_dir, "concat_list.txt")
with open(concat_txt, "w", encoding="utf-8") as f:
    for mp4_p in results:
        safe_p = mp4_p.replace("\\", "/")
        f.write(f"file '{safe_p}'\n")

clean_vid_dst = os.path.join(VID_OUT_DIR, "clean_base_1080p.mp4")
tmp_vid_dst = os.path.join(VID_OUT_DIR, "clean_base_1080p_v2_final.mp4")
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
    "-c", "copy", "-movflags", "+faststart", tmp_vid_dst
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.replace(tmp_vid_dst, clean_vid_dst)

# Verify exact frame count and duration via ffprobe!
probe = subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0",
    "-count_packets", "-show_entries", "stream=nb_read_packets,duration",
    "-of", "csv=p=0", clean_vid_dst
], text=True).strip()
print(f"=== ALL DONE in {time.time()-t0:.1f}s! clean_base_1080p.mp4 ({os.path.getsize(clean_vid_dst)/(1024*1024):.1f} MB) | ffprobe={probe} ===")
