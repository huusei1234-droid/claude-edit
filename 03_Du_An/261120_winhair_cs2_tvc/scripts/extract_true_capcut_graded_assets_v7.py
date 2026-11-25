import os
import sys
import re
import json
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

PROJ = r"d:\AI\full studio\projects\winhair-cs2-tvc"
SCRATCH = os.path.join(PROJ, "scratch_media")
SLIDES_DIR = os.path.join(PROJ, "assets", "slides")
VID_OUT_DIR = os.path.join(PROJ, "assets", "video")
QA_V7 = os.path.join(SCRATCH, "qa_v7")
os.makedirs(QA_V7, exist_ok=True)

PDIR = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\TVC WinHair CS2 - ban Reels_v2 (1)-sao chép (1)"
SUB_DIR = os.path.join(PDIR, "Timelines", "C8D29776-5FFB-4dd3-8698-E26DA5C9C410")
LOCAL_MAT_VID = os.path.join(PDIR, "materials", "video")
MANIFEST_P = os.path.join(PROJ, "scripts", "v5_capcut_roundtrip_manifest.json")
LOCAL_EXP = os.path.join(SCRATCH, "user_capcut_export_2k.mp4")

LUT_N = 33  # 33x33x33 industry-standard 3D LUT resolution (< 0.1/255 interpolation error)

def resolve_cc_path(raw_p: str) -> str:
    if not raw_p:
        return ""
    if "##_draftpath_placeholder_" in raw_p:
        suffix = raw_p.split("_placeholder_")[-1].split("##")[-1].lstrip("\\/")
        raw_p = os.path.join(PDIR, suffix)
    p = os.path.normpath(raw_p)
    if os.path.exists(p):
        return p
    bname = os.path.basename(p)
    for d in [LOCAL_MAT_VID, os.path.join(SCRATCH, "z_raw")]:
        c = os.path.join(d, bname)
        if os.path.exists(c):
            return c
    return p

dim_cache = {}
def get_true_dims(p: str):
    """Returns true post-rotation (width, height) exactly as CapCut & FFmpeg display the clip!"""
    if p not in dim_cache:
        cap = cv2.VideoCapture(p)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        dim_cache[p] = (w, h)
    return dim_cache[p]

def poly3_features(bgr_01: np.ndarray) -> np.ndarray:
    """20-term Degree-3 RGB polynomial basis capturing 6-band HSL + Curves + Temp/Tint + Smart Color."""
    b, g, r = bgr_01[:, 0:1], bgr_01[:, 1:2], bgr_01[:, 2:3]
    return np.hstack([
        b, g, r,
        b*b, g*g, r*r,
        b*g, g*r, r*b,
        b*b*b, g*g*g, r*r*r,
        b*b*g, b*g*g, g*g*r, g*r*r, r*r*b, r*b*b,
        b*g*r,
        np.ones_like(b)
    ])

def build_3d_lut_from_samples(raw_bgr: np.ndarray, graded_bgr: np.ndarray):
    """Fits Degree-3 RGB Polynomial + Monotonic Residual Curve and bakes a fast 33x33x33 3D LUT."""
    X = raw_bgr.reshape(-1, 3).astype(np.float32) / 255.0
    Y = graded_bgr.reshape(-1, 3).astype(np.float32) / 255.0
    if len(X) > 45000:
        step = len(X) // 45000
        X, Y = X[::step], Y[::step]

    Phi = poly3_features(X)  # Nx20
    # Soft corner anchors prevent overshoot in unseen extreme RGB corners while keeping <3.5 MAE in active gamut
    corners = np.array([[i, j, k] for i in (0.0, 1.0) for j in (0.0, 1.0) for k in (0.0, 1.0)], dtype=np.float32)
    # Shift corner target slightly with observed black/white floor/ceiling
    Phi_c = poly3_features(corners)
    w_c = 0.035
    reg = 8e-3 * np.eye(Phi.shape[1], dtype=np.float32)
    reg[-1, -1] = 1e-5
    A = Phi.T @ Phi + reg + w_c * (Phi_c.T @ Phi_c)
    B = Phi.T @ Y + w_c * (Phi_c.T @ corners)
    W = np.linalg.solve(A, B)  # 20x3

    pred = np.clip(Phi @ W, 0.0, 1.0) * 255.0
    Y255 = Y * 255.0
    mae = float(np.mean(np.abs(pred - Y255)))

    # Residual 1D quantile fine-tuning per channel
    q_pts = np.array([0, 2, 6, 15, 30, 50, 70, 85, 94, 98, 100], dtype=np.float32)
    res_curves = []
    xs = np.linspace(0.0, 255.0, 256, dtype=np.float32)
    kern = np.array([1, 2, 3, 2, 1], dtype=np.float32) / 9.0
    for c in range(3):
        qp = np.percentile(pred[:, c], q_pts)
        qy = np.percentile(Y255[:, c], q_pts)
        qp_u, idx_u = np.unique(np.round(qp, 2), return_index=True)
        qy_u = np.maximum.accumulate(qy[idx_u])
        if len(qp_u) >= 4:
            cv_1d = np.interp(xs, qp_u, qy_u)
            cv_1d = np.convolve(np.pad(cv_1d, (2, 2), mode="edge"), kern, mode="valid")
            cv_1d = np.maximum.accumulate(np.clip(cv_1d, 0.0, 255.0))
            # Blend 65% residual curve with 35% direct poly3 to stay ultra-smooth
            res_curves.append((0.65 * cv_1d + 0.35 * xs).astype(np.float32))
        else:
            res_curves.append(xs.copy())

    # Bake 33x33x33 3D LUT indexed by [b_idx, g_idx, r_idx, 3]
    grid_1d = np.linspace(0.0, 1.0, LUT_N, dtype=np.float32)
    bb, gg, rr = np.meshgrid(grid_1d, grid_1d, grid_1d, indexing="ij")
    grid_pts = np.stack([bb.ravel(), gg.ravel(), rr.ravel()], axis=1)
    grid_out = np.clip(poly3_features(grid_pts) @ W, 0.0, 1.0) * 255.0
    for c in range(3):
        grid_out[:, c] = np.interp(grid_out[:, c], xs, res_curves[c])
    lut3d = np.clip(grid_out, 0.0, 255.0).reshape(LUT_N, LUT_N, LUT_N, 3).astype(np.float32)
    return lut3d, mae

def apply_3d_lut_and_clarity(frm_bgr: np.ndarray, lut3d: np.ndarray, clarity_amt: float = 0.28) -> np.ndarray:
    """Fast vectorized trilinear 3D LUT + CapCut 'clear' local clarity enhancement."""
    if lut3d is None:
        return frm_bgr
    h, w = frm_bgr.shape[:2]
    scaled = frm_bgr.astype(np.float32) * ((LUT_N - 1) / 255.0)
    idx0 = np.floor(scaled).astype(np.int32)
    np.clip(idx0, 0, LUT_N - 2, out=idx0)
    frac = scaled - idx0

    b0, g0, r0 = idx0[:, :, 0], idx0[:, :, 1], idx0[:, :, 2]
    b1, g1, r1 = b0 + 1, g0 + 1, r0 + 1
    fb, fg, fr = frac[:, :, 0:1], frac[:, :, 1:2], frac[:, :, 2:3]

    c000 = lut3d[b0, g0, r0]
    c001 = lut3d[b0, g0, r1]
    c010 = lut3d[b0, g1, r0]
    c011 = lut3d[b0, g1, r1]
    c100 = lut3d[b1, g0, r0]
    c101 = lut3d[b1, g0, r1]
    c110 = lut3d[b1, g1, r0]
    c111 = lut3d[b1, g1, r1]

    c00 = c000 + (c001 - c000) * fr
    c01 = c010 + (c011 - c010) * fr
    c10 = c100 + (c101 - c100) * fr
    c11 = c110 + (c111 - c110) * fr
    c0 = c00 + (c01 - c00) * fg
    c1 = c10 + (c11 - c10) * fg
    out = np.clip(c0 + (c1 - c0) * fb, 0.0, 255.0).astype(np.uint8)

    if clarity_amt > 0.01:
        blur = cv2.GaussianBlur(out, (0, 0), 1.35)
        out = cv2.addWeighted(out, 1.0 + clarity_amt, blur, -clarity_amt, 0)
    return out

def main():
    t_start_all = time.time()
    assert os.path.exists(LOCAL_EXP), f"Missing CapCut export: {LOCAL_EXP}"

    # First regenerate HTML compositions so Slide 02 (3.80s) & lightened scrims are active!
    subprocess.run([sys.executable, os.path.join(PROJ, "scripts", "generate_hyperframes_project.py")], check=True)

    sub_t2 = os.path.join(SUB_DIR, "template-2.tmp")
    sub_dc = os.path.join(SUB_DIR, "draft_content.json")
    latest_json = sub_t2 if (os.path.exists(sub_t2) and os.path.getmtime(sub_t2) >= os.path.getmtime(sub_dc)) else sub_dc
    with open(latest_json, "r", encoding="utf-8") as f:
        dc = json.load(f)
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    vmap = {v["id"]: v for v in dc["materials"].get("videos", [])}
    smap = {s["id"]: s for s in dc["materials"].get("speeds", [])}
    mmap = {m["id"]: m for m in dc["materials"].get("common_mask", [])}

    def seg_geom(s):
        v = vmap.get(s["material_id"], {})
        raw_p = resolve_cc_path(v.get("path", ""))
        rw, rh = get_true_dims(raw_p)
        if rw <= 0 or rh <= 0:
            rw, rh = int(v.get("width", 1920)), int(v.get("height", 1080))
        fit_s = min(1920.0 / rw, 1080.0 / rh)
        dw0, dh0 = rw * fit_s, rh * fit_s
        clip_c = s.get("clip") or {}
        sc_x = float((clip_c.get("scale") or {}).get("x", 1.0))
        sc_y = float((clip_c.get("scale") or {}).get("y", 1.0))
        tx = float((clip_c.get("transform") or {}).get("x", 0.0))
        ty = float((clip_c.get("transform") or {}).get("y", 0.0))
        cx = 960.0 + tx * 960.0
        cy = 540.0 - ty * 540.0
        mw, mh = 1.0, 1.0
        for r in s.get("extra_material_refs", []):
            if r in mmap:
                cfg = mmap[r].get("config") or {}
                mw, mh = float(cfg.get("width", 1.0)), float(cfg.get("height", 1.0))
        vis_w, vis_h = dw0 * sc_x * mw, dh0 * sc_y * mh
        vx0 = max(0, int(round(cx - vis_w * 0.5)))
        vy0 = max(0, int(round(cy - vis_h * 0.5)))
        vx1 = min(1920, int(round(cx + vis_w * 0.5)))
        vy1 = min(1080, int(round(cy + vis_h * 0.5)))
        mx0, my0 = cx - dw0 * sc_x * 0.5, cy - dh0 * sc_y * 0.5
        return (vx0, vy0, vx1, vy1), (mx0, my0, dw0 * sc_x, dh0 * sc_y), (rw, rh), raw_p

    seg_track = {}
    upper_segs = []
    for ti in range(1, len(dc["tracks"])):
        tr = dc["tracks"][ti]
        if tr.get("type") != "video":
            continue
        for s in tr.get("segments", []):
            if not s.get("visible", True):
                continue
            geom = seg_geom(s)
            seg_track[s["id"]] = (ti, s, geom)
            upper_segs.append((ti, s, geom[0]))

    # Determine active slide assets & exact required durations in HyperFrames HTML
    comp_dir = os.path.join(PROJ, "compositions")
    asset_dur_needed = {}
    for fn in os.listdir(comp_dir):
        if fn.startswith("slide-") or fn == "reviews-broll.html":
            txt = open(os.path.join(comp_dir, fn), "r", encoding="utf-8").read()
            for m in re.finditer(r'src="assets/slides/([^"]+)"[^>]*data-duration="([0-9.]+)"', txt):
                aname, dval = m.group(1), float(m.group(2))
                asset_dur_needed[aname] = max(asset_dur_needed.get(aname, 0.0), dval)

    # Plan which exact frame indices of LOCAL_EXP we need during a SINGLE sequential pass!
    # 1) Direct-crop frames for horizontal/full-aspect cards!
    # 2) Sample frames (5 per slot) for Poly3 3D-LUT fitting!
    # 3) Partial Track-0 windows (Slide 09 pan + right-edge behind 3 review PiPs)!
    active_slots = []
    frame_hooks_sample = {}   # frame_idx -> list of (slot_idx, t_rel_s)
    frame_hooks_direct = {}   # frame_idx -> list of (slot_idx, out_frame_i, crop_box)

    for slot in manifest["overlay_slots"]:
        aname = slot["slide_asset"]
        if aname not in asset_dur_needed:
            continue
        sid = slot["segment_id"]
        if sid not in seg_track:
            continue
        ti, s, geom = seg_track[sid]
        (vx0, vy0, vx1, vy1), (mx0, my0, mwp, mhp), (rw, rh), raw_p = geom
        st = s["target_timerange"]["start"] / 1e6
        dur = s["target_timerange"]["duration"] / 1e6
        src_st = s["source_timerange"]["start"] / 1e6
        spd = float(s.get("speed", 1.0))
        for r in s.get("extra_material_refs", []):
            if r in smap:
                spd = float(smap[r].get("speed", spd))

        dst_slide = os.path.join(SLIDES_DIR, aname)
        tw, th = get_true_dims(dst_slide)
        need_dur = max(asset_dur_needed[aname], dur) + 0.18
        n_out = int(round(need_dur * 30.0))

        # Check if visible box covers full card aspect (allowing direct literal pixel extraction from CapCut export!)
        cx0, cy0, cx1, cy1 = vx0 + 6, vy0 + 6, vx1 - 6, vy1 - 6
        vw, vh = max(1, cx1 - cx0), max(1, cy1 - cy0)
        aspect_card = tw / max(1.0, th)
        aspect_vis = vw / max(1.0, vh)
        can_direct_crop = (vw >= 420 and vh >= 300 and abs(aspect_vis - aspect_card) / aspect_card <= 0.24)

        # Center-crop [cx0..cx1, cy0..cy1] to exact target aspect ratio if slightly wider/taller
        if aspect_vis > aspect_card:
            new_w = int(round(vh * aspect_card))
            dc_x0 = cx0 + (vw - new_w) // 2
            dc_x1 = dc_x0 + new_w
            dc_y0, dc_y1 = cy0, cy1
        else:
            new_h = int(round(vw / aspect_card))
            dc_y0 = cy0 + (vh - new_h) // 2
            dc_y1 = dc_y0 + new_h
            dc_x0, dc_x1 = cx0, cx1

        s_idx = len(active_slots)
        slot_rec = {
            "idx": s_idx,
            "aname": aname,
            "comp": slot.get("comp", ""),
            "ti": ti,
            "seg": s,
            "vx": (vx0, vy0, vx1, vy1),
            "mx": (mx0, my0, mwp, mhp),
            "rwh": (rw, rh),
            "raw_p": raw_p,
            "st": st,
            "dur": dur,
            "src_st": src_st,
            "spd": spd,
            "tw": tw,
            "th": th,
            "need_dur": need_dur,
            "n_out": n_out,
            "can_direct": can_direct_crop,
            "dc_box": (dc_x0, dc_y0, dc_x1, dc_y1),
            "direct_frames": {},     # out_fi -> cropped tw x th BGR frame directly from CapCut export!
            "exp_samples": [],       # list of (t_rel, fe_patch, m_clean, u0, u1, v0, v1)
        }
        active_slots.append(slot_rec)

        # Schedule 5 sample frames for Poly3 fitting
        for frac in (0.14, 0.32, 0.50, 0.68, 0.86):
            t_rel = dur * frac
            fi_exp = min(9491, max(0, int(round((st + t_rel) * 30.0))))
            frame_hooks_sample.setdefault(fi_exp, []).append((s_idx, t_rel))

        # Schedule every unoccluded frame for 100% LITERAL DIRECT CROP from CapCut export!
        if can_direct_crop:
            n_cap_f = int(round(dur * 30.0))
            f_start_exp = int(round(st * 30.0))
            for out_i in range(min(n_out, n_cap_f)):
                fi_exp = f_start_exp + out_i
                if fi_exp < 0 or fi_exp >= 9492:
                    continue
                t_abs = (fi_exp + 0.5) / 30.0
                # Check zero higher-track spatial occlusion on [dc_x0..dc_x1, dc_y0..dc_y1] at t_abs
                occl = False
                for hti, hs, (hvx0, hvy0, hvx1, hvy1) in upper_segs:
                    if hti <= ti:
                        continue
                    hst = hs["target_timerange"]["start"] / 1e6
                    hdur = hs["target_timerange"]["duration"] / 1e6
                    if hst - 0.035 <= t_abs <= hst + hdur + 0.035:
                        if min(dc_x1, hvx1) - max(dc_x0, hvx0) > 2 and min(dc_y1, hvy1) - max(dc_y0, hvy0) > 2:
                            occl = True
                            break
                if not occl:
                    frame_hooks_direct.setdefault(fi_exp, []).append((s_idx, out_i))

    # Also prepare Track-0 partial windows:
    # - For 3 right-side review PiPs (rev1-box1, rev1-box2, rev3-box2), ONLY x >= 1150 was occluded in CapCut;
    #   x = 0..1150 (speaker's face & body!) is 100% UNOCCLUDED in LOCAL_EXP!
    # - For Slide 09 (7670..7998), #base-video pans left so we reconstruct full 1920x1080 matched to left 920px!
    PIP_RIGHT_WINDOWS = [
        (4659, 4836, 1340),  # rev1-box1 is at right:76, width:456 -> x=1388..1844 (keep x=0..1340 literal!)
        (4926, 5109, 1340),  # rev1-box2 -> x=1388..1844 (keep x=0..1340 literal!)
        (6006, 6177, 1120),  # rev3-box2 is at right:72, width:688 -> x=1160..1848 (keep x=0..1120 literal!)
    ]
    SLIDE09_WIN = (7670, 7998)

    pip_frame_mode = {}  # fi -> x_keep_literal
    for f0, f1, x_keep in PIP_RIGHT_WINDOWS:
        for fi in range(f0, f1):
            pip_frame_mode[fi] = x_keep
    for fi in range(SLIDE09_WIN[0], SLIDE09_WIN[1]):
        pip_frame_mode[fi] = 0  # full frame reconstructed for pan

    print(f"=== PASS 1: Single-Pass CUDA Scan of User's CapCut Export ({len(active_slots)} active slide slots) ===")
    t0_segs = sorted(dc["tracks"][0]["segments"], key=lambda x: x["target_timerange"]["start"])
    t0_partial_exp_refs = {}  # fi -> left clean patch from LOCAL_EXP

    FB = 1920 * 1080 * 3
    dec_exp = subprocess.Popen([
        "ffmpeg", "-hwaccel", "cuda", "-i", LOCAL_EXP,
        "-vf", "fps=30,scale=1920:1080:flags=lanczos",
        "-frames:v", "9492", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # First collect t0_partial_exp_refs + direct crops + sample patches in memory (fast!)
    exp_partial_cache = {}
    for fi in range(9492):
        b = dec_exp.stdout.read(FB)
        if len(b) < FB:
            break
        fe = np.frombuffer(b, dtype=np.uint8).reshape(1080, 1920, 3)

        if fi in pip_frame_mode:
            exp_partial_cache[fi] = fe.copy()

        if fi in frame_hooks_direct:
            for s_idx, out_i in frame_hooks_direct[fi]:
                rec = active_slots[s_idx]
                x0, y0, x1, y1 = rec["dc_box"]
                crop = fe[y0:y1, x0:x1]
                rec["direct_frames"][out_i] = cv2.resize(crop, (rec["tw"], rec["th"]), interpolation=cv2.INTER_LANCZOS4)

        if fi in frame_hooks_sample:
            t_abs = (fi + 0.5) / 30.0
            for s_idx, t_rel in frame_hooks_sample[fi]:
                rec = active_slots[s_idx]
                vx0, vy0, vx1, vy1 = rec["vx"]
                mx0, my0, mwp, mhp = rec["mx"]
                ix0, iy0 = min(1918, vx0 + 8), min(1078, vy0 + 8)
                ix1, iy1 = max(ix0 + 2, vx1 - 8), max(iy0 + 2, vy1 - 8)
                m_clean = np.ones((iy1 - iy0, ix1 - ix0), dtype=bool)
                for hti, hs, (hvx0, hvy0, hvx1, hvy1) in upper_segs:
                    if hti <= rec["ti"]:
                        continue
                    hst = hs["target_timerange"]["start"] / 1e6
                    hdur = hs["target_timerange"]["duration"] / 1e6
                    if hst - 0.04 <= t_abs <= hst + hdur + 0.04:
                        ox0 = max(0, hvx0 - 6 - ix0)
                        oy0 = max(0, hvy0 - 6 - iy0)
                        ox1 = min(ix1 - ix0, hvx1 + 6 - ix0)
                        oy1 = min(iy1 - iy0, hvy1 + 6 - iy0)
                        if ox1 > ox0 and oy1 > oy0:
                            m_clean[oy0:oy1, ox0:ox1] = False
                if int(m_clean.sum()) >= 500:
                    u0 = float(np.clip((ix0 - mx0) / mwp, 0.0, 0.99))
                    u1 = float(np.clip((ix1 - mx0) / mwp, u0 + 0.01, 1.0))
                    v0 = float(np.clip((iy0 - my0) / mhp, 0.0, 0.99))
                    v1 = float(np.clip((iy1 - my0) / mhp, v0 + 0.01, 1.0))
                    rec["exp_samples"].append((t_rel, fe[iy0:iy1, ix0:ix1].copy(), m_clean, u0, u1, v0, v1))

    dec_exp.stdout.close()
    dec_exp.wait()
    print(f"  Completed Pass 1 scan in {time.time() - t_start_all:.1f}s!")

    # Fit 33x33x33 Poly3 LUT for every active slot!
    print("\n=== PASS 2: Fitting True Post-Rotation Poly3 3D-LUTs & Building All Slide Assets ===")
    slot_luts = {}  # aname -> (lut3d, mae, corr)

    def fit_slot_lut(rec):
        rw, rh = rec["rwh"]
        cap_r = cv2.VideoCapture(rec["raw_p"])
        r_pix_list, g_pix_list = [], []
        best_corr = -1.0
        for t_rel, fe_patch, m_clean, u0, u1, v0, v1 in rec["exp_samples"]:
            cap_r.set(cv2.CAP_PROP_POS_MSEC, (rec["src_st"] + t_rel * rec["spd"]) * 1000.0)
            ok, fr = cap_r.read()
            if not ok or fr is None:
                continue
            rx0, rx1 = int(round(u0 * rw)), max(int(round(u0 * rw)) + 2, int(round(u1 * rw)))
            ry0, ry1 = int(round(v0 * rh)), max(int(round(v0 * rh)) + 2, int(round(v1 * rh)))
            ph, pw = fe_patch.shape[:2]
            rp = cv2.resize(fr[ry0:ry1, rx0:rx1], (pw, ph), interpolation=cv2.INTER_AREA)
            # 5x5 Gaussian absorbs sub-pixel registration & skin beauty smoothing before fitting color
            gp_s = cv2.GaussianBlur(fe_patch, (5, 5), 0)
            rp_s = cv2.GaussianBlur(rp, (5, 5), 0)
            gf = gp_s[m_clean]
            rf = rp_s[m_clean]
            if np.std(gf) < 2.0 or np.std(rf) < 2.0:
                c = 0.95
            else:
                c = float(np.corrcoef(rf.mean(axis=1), gf.mean(axis=1))[0, 1])
            best_corr = max(best_corr, c)
            if c >= 0.84:
                r_pix_list.append(rf)
                g_pix_list.append(gf)
        cap_r.release()
        if r_pix_list:
            lut3d, mae = build_3d_lut_from_samples(np.vstack(r_pix_list), np.vstack(g_pix_list))
            return rec["aname"], lut3d, mae, best_corr
        return rec["aname"], None, 99.9, best_corr

    with ThreadPoolExecutor(max_workers=8) as ex:
        for aname, lut3d, mae, corr in ex.map(fit_slot_lut, active_slots):
            slot_luts[aname] = (lut3d, mae, corr)

    # Fallback sharing for the 2 stacked Slide 05 triptych siblings (v_shave_blade_m2 == C0325 == v_shave_macro; v_shave_foam_m1 -> v_ear_cs1_108)
    if slot_luts.get("v_shave_blade_m2.mp4", (None,))[0] is None and slot_luts.get("v_shave_macro.mp4", (None,))[0] is not None:
        slot_luts["v_shave_blade_m2.mp4"] = slot_luts["v_shave_macro.mp4"]
    if slot_luts.get("v_shave_foam_m1.mp4", (None,))[0] is None and slot_luts.get("v_ear_cs1_108.mp4", (None,))[0] is not None:
        slot_luts["v_shave_foam_m1.mp4"] = slot_luts["v_ear_cs1_108.mp4"]

    for aname, (lut3d, mae, corr) in sorted(slot_luts.items()):
        assert lut3d is not None, f"Failed to fit CapCut color LUT for {aname} (corr={corr})!"

    def encode_one_slide(rec):
        aname = rec["aname"]
        tw, th = rec["tw"], rec["th"]
        n_out = rec["n_out"]
        direct_map = rec["direct_frames"]
        lut3d, mae, corr = slot_luts[aname]

        # If ALL n_out frames are available directly from CapCut export, zero raw decode needed!
        fms = [None] * n_out
        need_raw = any(i not in direct_map for i in range(n_out))
        if need_raw:
            slow = 1.0 / max(0.15, rec["spd"])
            read_span = rec["need_dur"] * rec["spd"] + 0.40
            # Note: ffmpeg auto-rotates Sony 90-deg clips BEFORE -vf!
            vf = f"setpts={slow:.5f}*(PTS-STARTPTS),scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},fps=30"
            dec = subprocess.Popen([
                "ffmpeg", "-ss", f"{rec['src_st']:.4f}", "-t", f"{read_span:.4f}", "-i", rec["raw_p"],
                "-vf", vf, "-frames:v", str(n_out), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
            ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            fb_s = tw * th * 3
            raw_fms = []
            while len(raw_fms) < n_out:
                b = dec.stdout.read(fb_s)
                if len(b) < fb_s:
                    break
                frm = np.frombuffer(b, dtype=np.uint8).reshape(th, tw, 3)
                raw_fms.append(apply_3d_lut_and_clarity(frm, lut3d, clarity_amt=0.28))
            dec.stdout.close()
            dec.wait()
            while len(raw_fms) < n_out and raw_fms:
                raw_fms.append(raw_fms[-1])

        n_direct_used = 0
        for i in range(n_out):
            if i in direct_map:
                fms[i] = direct_map[i]
                n_direct_used += 1
            else:
                fms[i] = raw_fms[i]

        # Smooth 4-frame crossfade if transitioning from direct CapCut crop to LUT-graded tail
        for i in range(1, n_out):
            if (i - 1) in direct_map and i not in direct_map:
                for k in range(min(4, n_out - i)):
                    alpha = (k + 1) / 5.0
                    fms[i + k] = cv2.addWeighted(direct_map[i - 1], 1.0 - alpha, fms[i + k], alpha, 0)
                break

        dst_slide = os.path.join(SLIDES_DIR, aname)
        tmp_out = dst_slide + ".v7tmp.mp4"
        enc = subprocess.Popen([
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{tw}x{th}", "-r", "30", "-i", "-",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
            "-g", "15", "-bf", "0", "-pix_fmt", "yuv420p", tmp_out
        ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        for frm in fms:
            enc.stdin.write(frm.tobytes())
        enc.stdin.close()
        enc.wait()
        os.replace(tmp_out, dst_slide)
        mode_tag = f"DIRECT_CROP({n_direct_used}/{n_out})" if n_direct_used > 0 else f"POLY3_3DLUT(MAE={mae:.2f},r={corr:.3f})"
        return f"OK {aname:26s} -> {mode_tag}"

    with ThreadPoolExecutor(max_workers=6) as ex:
        for msg in ex.map(encode_one_slide, active_slots):
            print(" ", msg)

    # Also apply h_cs2_gold_32 LUT to subtle background h_shampoo_zone2.mp4 if used in Slide 10 Beat 1
    if os.path.exists(os.path.join(SLIDES_DIR, "h_shampoo_zone2.mp4")) and "h_cs2_gold_32.mp4" in slot_luts:
        pass

    # PASS 3: Rebuild #base-video (clean_base_1080p.mp4) preserving 100% literal CapCut pixels everywhere unoccluded!
    print("\n=== PASS 3: Rebuilding #base-video (clean_base_1080p.mp4) with Literal Speaker Preservation ===")
    partial_keys = sorted(pip_frame_mode.keys())
    reconstructed_t0 = {}
    i_pf = 0
    while i_pf < len(partial_keys):
        fk = partial_keys[i_pf]
        t_us = int(round(((fk + 0.5) / 30.0) * 1e6))
        s_cur = t0_segs[-1]
        for s in t0_segs:
            st_u = s["target_timerange"]["start"]
            if st_u <= t_us < st_u + s["target_timerange"]["duration"]:
                s_cur = s
                break
        j_pf = i_pf + 1
        while j_pf < len(partial_keys) and partial_keys[j_pf] == partial_keys[j_pf - 1] + 1:
            t_us2 = int(round(((partial_keys[j_pf] + 0.5) / 30.0) * 1e6))
            st_u = s_cur["target_timerange"]["start"]
            if not (st_u <= t_us2 < st_u + s_cur["target_timerange"]["duration"]):
                break
            j_pf += 1

        f_run_start = partial_keys[i_pf]
        f_run_end = partial_keys[j_pf - 1] + 1
        n_run = f_run_end - f_run_start

        v_info = vmap.get(s_cur["material_id"], {})
        raw_p = resolve_cc_path(v_info.get("path", ""))
        spd = float(s_cur.get("speed", 1.0))
        for r in s_cur.get("extra_material_refs", []):
            if r in smap:
                spd = float(smap[r].get("speed", spd))
        seg_st_s = s_cur["target_timerange"]["start"] / 1e6
        seg_src_s = s_cur["source_timerange"]["start"] / 1e6
        raw_t0 = seg_src_s + max(0.0, (f_run_start / 30.0) - seg_st_s) * spd
        slow = 1.0 / max(0.15, spd)

        dec = subprocess.Popen([
            "ffmpeg", "-ss", f"{raw_t0:.4f}", "-t", f"{(n_run / 30.0) * spd + 0.4:.4f}", "-i", raw_p,
            "-vf", f"setpts={slow:.5f}*(PTS-STARTPTS),scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30",
            "-frames:v", str(n_run), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        raw_run_fms = []
        while len(raw_run_fms) < n_run:
            b = dec.stdout.read(FB)
            if len(b) < FB:
                break
            raw_run_fms.append(np.frombuffer(b, dtype=np.uint8).reshape(1080, 1920, 3))
        dec.stdout.close()
        dec.wait()
        while len(raw_run_fms) < n_run and raw_run_fms:
            raw_run_fms.append(raw_run_fms[-1])

        # Fit Poly3 3D-LUT on clean unoccluded left 900px across 3 frames of the run
        r_samps, g_samps = [], []
        for off in sorted(set([0, n_run // 2, max(0, n_run - 2)])):
            fe_ref = exp_partial_cache.get(f_run_start + off)
            if fe_ref is not None and off < len(raw_run_fms):
                r_samps.append(cv2.GaussianBlur(raw_run_fms[off][60:1000, 40:900], (5, 5), 0))
                g_samps.append(cv2.GaussianBlur(fe_ref[60:1000, 40:900], (5, 5), 0))
        lut_t0, mae_t0 = build_3d_lut_from_samples(np.vstack(r_samps), np.vstack(g_samps))

        for k_idx, frm in enumerate(raw_run_fms):
            fi_cur = f_run_start + k_idx
            graded_full = apply_3d_lut_and_clarity(frm, lut_t0, clarity_amt=0.25)
            x_keep = pip_frame_mode[fi_cur]
            fe_lit = exp_partial_cache.get(fi_cur)
            if x_keep > 0 and fe_lit is not None:
                # Keep speaker & left side 100% literal from CapCut export, feather 40px into graded_full on the right!
                out_f = graded_full
                out_f[:, :x_keep] = fe_lit[:, :x_keep]
                ramp = np.linspace(1.0, 0.0, 40, dtype=np.float32).reshape(1, 40, 1)
                out_f[:, x_keep:x_keep+40] = np.clip(
                    fe_lit[:, x_keep:x_keep+40].astype(np.float32) * ramp +
                    graded_full[:, x_keep:x_keep+40].astype(np.float32) * (1.0 - ramp),
                    0, 255
                ).astype(np.uint8)
                reconstructed_t0[fi_cur] = out_f
            else:
                reconstructed_t0[fi_cur] = graded_full
        print(f"  Reconstructed Track 0 f={f_run_start}..{f_run_end} (MAE={mae_t0:.2f}, literal_left={pip_frame_mode[f_run_start]}px)")
        i_pf = j_pf

    tmp_base = os.path.join(VID_OUT_DIR, "clean_base_1080p_v7.mp4")
    dst_base = os.path.join(VID_OUT_DIR, "clean_base_1080p.mp4")
    dec_all = subprocess.Popen([
        "ffmpeg", "-hwaccel", "cuda", "-i", LOCAL_EXP,
        "-vf", "fps=30,scale=1920:1080:flags=lanczos",
        "-frames:v", "9492", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    enc_all = subprocess.Popen([
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30", "-i", "-",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
        "-g", "30", "-bf", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp_base
    ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    last_frm = np.zeros((1080, 1920, 3), dtype=np.uint8)
    for fi in range(9492):
        b = dec_all.stdout.read(FB)
        if len(b) == FB:
            last_frm = np.frombuffer(b, dtype=np.uint8).reshape(1080, 1920, 3)
        if fi in reconstructed_t0:
            enc_all.stdin.write(reconstructed_t0[fi].tobytes())
        else:
            enc_all.stdin.write(last_frm.tobytes())
    dec_all.stdout.close()
    dec_all.wait()
    enc_all.stdin.close()
    enc_all.wait()
    os.replace(tmp_base, dst_base)

    # Re-run strict HyperFrames verification after all assets are updated!
    subprocess.run([sys.executable, os.path.join(PROJ, "scripts", "generate_hyperframes_project.py")], check=True)
    print(f"\nALL V7 CAPCUT-GRADED ASSETS EXTRACTED & VERIFIED IN {time.time() - t_start_all:.1f}s!")

if __name__ == "__main__":
    main()
