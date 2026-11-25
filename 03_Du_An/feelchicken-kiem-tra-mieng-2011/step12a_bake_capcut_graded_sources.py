import json, os, subprocess, time, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
W, H = 1080, 1920
FPS = 30.0
SR = 48000

import sys
sys.path.insert(0, PROJ_DIR)
from capcut_color_engine import load_user_capcut_segments, apply_capcut_grade, COEF

def write_seg_cube_lut(seg_info, cube_path):
    """Bake exact CapCut FX + 8-band HSL (plus clip-specific Smart Color Adjust WB) into a 33x33x33 .cube 3D LUT in 5ms!"""
    fx = dict(seg_info["fx"])
    sca = fx.pop("smart_color_adjust", 0.0)
    fx.pop("clear", None)  # applied via FFmpeg unsharp

    # Sample 1 frame from the clip for exact Smart Color Adjust auto-WB
    wb_mult = np.ones(3, dtype=np.float32)
    if sca > 0.0:
        try:
            rb = subprocess.check_output([
                "ffmpeg", "-v", "error", "-ss", f"{seg_info['src_start'] + 0.3:.2f}",
                "-i", seg_info["path"], "-vf", "scale=90:160", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
            ])
            s_arr = np.frombuffer(rb, dtype=np.uint8).reshape((160, 90, 3)).astype(np.float32) / 255.0
            m_rgb = np.mean(s_arr, axis=(0, 1))
            gm    = float(np.mean(m_rgb)) + 1e-5
            wb_p  = np.clip(gm / (m_rgb + 1e-5), 0.88, 1.14)
            wb_mult = (1.0 + (wb_p - 1.0) * (sca * 0.42)).astype(np.float32)
        except Exception:
            pass
        fx["brightness"] = fx.get("brightness", 0.0) + sca * 0.16
        fx["saturation"] = fx.get("saturation", 0.0) + sca * 0.09

    N = 33
    vals = np.linspace(0.0, 1.0, N, dtype=np.float32)
    # .cube standard order: R changes fastest, then G, then B!
    bb, gg, rr = np.meshgrid(vals, vals, vals, indexing="ij")
    grid_f = np.stack([rr * wb_mult[0], gg * wb_mult[1], bb * wb_mult[2]], axis=-1)
    grid_u8 = np.clip(grid_f.reshape((N, N * N, 3)) * 255.0 + 0.5, 0, 255).astype(np.uint8)

    graded_u8 = apply_capcut_grade(grid_u8, fx, seg_info["hsl"], COEF)
    graded_f  = (graded_u8.astype(np.float32) / 255.0).reshape((-1, 3))

    lines = [f"TITLE \"CapCut_Seg_{seg_info['index']:02d}\"", f"LUT_3D_SIZE {N}"]
    lines += [f"{r:.5f} {g:.5f} {b:.5f}" for r, g, b in graded_f]
    open(cube_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def capcut_crop_vf(sx, tx, ty):
    s = max(1.0, float(sx))
    nw = max(W, int(round(W * s)) // 2 * 2)
    nh = max(H, int(round(H * s)) // 2 * 2)
    dx = tx * (W * 0.5)
    dy = -ty * (H * 0.5)
    x0 = max(0, min(nw - W, int(round((nw - W) * 0.5 - dx))))
    y0 = max(0, min(nh - H, int(round((nh - H) * 0.5 - dy))))
    return f"scale={nw}:{nh}:force_original_aspect_ratio=increase,crop={nw}:{nh},crop={W}:{H}:{x0}:{y0}"

def bake_graded_clip_fast(seg_info, out_name, dur_override=None, stabilize=False):
    src_p = seg_info["path"]
    ss    = seg_info["src_start"]
    dur   = dur_override if dur_override is not None else seg_info["src_dur"]
    sx, tx, ty = seg_info["scale_x"], seg_info["trans_x"], seg_info["trans_y"]
    clr   = seg_info["fx"].get("clear", 0.0)

    cube_rel = f"aroll/_lut_seg{seg_info['index']:02d}.cube"
    write_seg_cube_lut(seg_info, os.path.join(PROJ_DIR, cube_rel))

    vf_chain = [capcut_crop_vf(sx, tx, ty), "fps=30"]
    if stabilize:
        trf = f"aroll/_v5_stab_{seg_info['index']}.trf"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", src_p,
            "-vf", ",".join(vf_chain + [f"vidstabdetect=shakiness=5:accuracy=15:result={trf}"]),
            "-f", "null", "-"
        ], cwd=PROJ_DIR, check=True)
        vf_chain.append(f"vidstabtransform=input={trf}:smoothing=20:zoom=2")

    vf_chain.append(f"lut3d='{cube_rel}'")
    if clr > 0.01:
        amt = min(1.2, round(clr * 2.1, 3))
        vf_chain.append(f"unsharp=7:7:{amt}:7:7:0.0")
    vf_chain.append("format=yuv420p")

    out_p = os.path.join(AROLL_DIR, out_name)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", src_p,
        "-vf", ",".join(vf_chain),
        "-an", "-c:v", "libx264", "-crf", "13", "-preset", "fast", out_p
    ], cwd=PROJ_DIR, check=True)
    print(f"Baked [{seg_info['index']:02d}] -> {out_name} ({dur:.2f}s)", flush=True)

def bake_transformed_matte_fast(full_matte_path, sub_offset_s, dur_s, sx, tx, ty, out_name):
    vf = f"{capcut_crop_vf(sx, tx, ty)},fps=30,format=yuv420p"
    out_p = os.path.join(AROLL_DIR, out_name)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{sub_offset_s:.3f}", "-t", f"{dur_s:.3f}", "-i", full_matte_path,
        "-vf", vf, "-an", "-c:v", "libx264", "-crf", "13", "-preset", "fast", "-color_range", "pc", out_p
    ], check=True)
    print(f"Baked aligned matte -> {out_name}", flush=True)

def main():
    t0 = time.time()
    segs = load_user_capcut_segments()
    bake_graded_clip_fast(segs[0],  "v5_cc_s1_skit.mp4",        dur_override=4.567)
    bake_graded_clip_fast(segs[1],  "v5_cc_s2_table.mp4",       dur_override=8.900)
    bake_graded_clip_fast(segs[3],  "v5_cc_s3_c1381.mp4",       dur_override=1.500)
    bake_graded_clip_fast(segs[4],  "v5_cc_s3_c1385.mp4",       dur_override=1.500)
    bake_graded_clip_fast(segs[5],  "v5_cc_s4_jar_shake.mp4",   dur_override=2.150)
    bake_graded_clip_fast(segs[6],  "v5_cc_s4_jar_draw.mp4",    dur_override=3.850)
    bake_graded_clip_fast(segs[7],  "v5_cc_s5a_khang.mp4",      dur_override=1.600)
    bake_graded_clip_fast(segs[8],  "v5_cc_s5b_c1395.mp4",      dur_override=1.200)
    bake_graded_clip_fast(segs[9],  "v5_cc_s5b_0327.mp4",       dur_override=1.200)
    bake_graded_clip_fast(segs[10], "v5_cc_s5b_0339.mp4",       dur_override=1.200)
    bake_graded_clip_fast(segs[11], "v5_cc_s5c_khang.mp4",      dur_override=4.050)
    bake_graded_clip_fast(segs[12], "v5_cc_s6a_6494.mp4",       dur_override=1.650)
    bake_graded_clip_fast(segs[13], "v5_cc_s6a_6495.mp4",       dur_override=1.650)
    bake_graded_clip_fast(segs[14], "v5_cc_s6b_thumbs.mp4",     dur_override=1.800)
    bake_graded_clip_fast(segs[15], "v5_cc_s6c_storefront.mp4", dur_override=3.900, stabilize=True)

    full_m5 = os.path.join(AROLL_DIR, "s5_gifts_matte.mp4")
    bake_transformed_matte_fast(full_m5, max(0.0, segs[7]["src_start"] - 1.88),  1.600, segs[7]["scale_x"],  segs[7]["trans_x"],  segs[7]["trans_y"],  "v5_cc_s5a_matte.mp4")
    bake_transformed_matte_fast(full_m5, max(0.0, segs[11]["src_start"] - 1.88), 4.050, segs[11]["scale_x"], segs[11]["trans_x"], segs[11]["trans_y"], "v5_cc_s5c_matte.mp4")

    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v3.json"), encoding="utf-8"))
    for s in tm["segments"]:
        if s["id"] == "s6c_storefront":
            s["f1"] = s["f0"] + 117
            s["dur"] = 3.9000
            s["t1"] = round(s["f1"] / FPS, 4)
            tm["total_frames"] = s["f1"]
            tm["total_dur"] = s["t1"]
    json.dump(tm, open(os.path.join(PROJ_DIR, "timeline_master_v5.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    vo3_p = os.path.join(STEMS_DIR, "01_Voice_Master_V3.wav")
    vo5_p = os.path.join(STEMS_DIR, "01_Voice_Master_V5.wav")
    with wave.open(vo3_p, "rb") as wf:
        raw_pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).reshape((-1, 2))
    target_n = int(round(tm["total_dur"] * SR))
    pad_n = max(0, target_n - len(raw_pcm))
    out_pcm = np.vstack([raw_pcm, np.zeros((pad_n, 2), dtype=np.int16)])[:target_n]
    with wave.open(vo5_p, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(out_pcm.tobytes())

    print(f"ALL 15 CapCut-graded 3D-LUT clips baked in {time.time()-t0:.1f}s! V5 dur = {tm['total_dur']:.3f}s ({tm['total_frames']}f)", flush=True)

if __name__ == "__main__":
    main()
