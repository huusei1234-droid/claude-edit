import json, math, os, shutil, subprocess, time, wave
import numpy as np
from PIL import Image, ImageDraw

BATCH_DIR = r"C:\AI\full studio\output\batch-htav-261125"
V00_ROOT  = r"C:\AI\full studio\output\ht-av-261125"

SR = 48000
FPS = 30.0
SPEED = 1.10

# Explicit micro-stumble cuts discovered during word-by-word audit (on V1 timeline seconds)
EXPLICIT_CUTS = {
    "v02": [(15.96, 17.90)],  # Cut duplicate "Ba là bắt đầu,"
    "v09": [(37.88, 39.10)],  # Cut duplicate "giúp cấp ẩm,"
}

def read_f32_48k(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def apply_micro_fade(arr, fi_s=0.015, fo_s=0.018):
    out = arr.copy()
    fi = min(len(out) // 4, int(round(fi_s * SR)))
    fo = min(len(out) // 4, int(round(fo_s * SR)))
    if fi > 2:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 2:
        out[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return out

def prepare_v00_folder():
    v00_dir = os.path.join(BATCH_DIR, "v00")
    os.makedirs(v00_dir, exist_ok=True)
    for fn_src, fn_dst in [
        (os.path.join(V00_ROOT, "aroll", "edited_graded.mp4"), "edited_graded.mp4"),
        (os.path.join(V00_ROOT, "aroll", "edited_matte.mp4"),  "edited_matte.mp4"),
        (os.path.join(V00_ROOT, "audio_stems", "edited_voice_48k.wav"), "edited_voice_48k.wav"),
        (os.path.join(V00_ROOT, "aroll", "main_cut_clean.json"), "main_cut_clean.json"),
    ]:
        dst = os.path.join(v00_dir, fn_dst)
        if not os.path.exists(dst):
            shutil.copy2(fn_src, dst)
    edl0 = json.load(open(os.path.join(V00_ROOT, "aroll", "edl_htav.json"), "r", encoding="utf-8"))
    clones0 = []
    for e in edl0["edl"]:
        if e["kind"].startswith("clone"):
            clones0.append({
                "key": e["kind"],
                "label": e["label"],
                "start_s": e["out_start_s"],
                "end_s": e["out_end_s"],
                "display_text": "",
            })
    meta0 = {
        "vid_key": "v00",
        "idx": 0,
        "code": "AV01",
        "brand": "HTPM",
        "final_name": "261125 HTPM AV Protein bữa sáng 30 giây đủ đạm final.mp4",
        "total_frames": edl0["total_frames"],
        "duration_s": edl0["duration_s"],
        "clone_spans": clones0,
        "edl": edl0["edl"],
    }
    json.dump(meta0, open(os.path.join(v00_dir, "edl_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def main():
    t0 = time.time()
    prepare_v00_folder()
    centers = json.load(open(os.path.join(BATCH_DIR, "speaker_centers_18.json"), "r", encoding="utf-8"))

    all_vks = ["v00"] + [f"v{i:02d}" for i in [1,2,3,4,5,6,7,8,9,10,12,13,15,16,17,18,19]]
    qc_sheet = Image.new("RGB", (240 * 6, 426 * 3), (16, 20, 26))
    dr_s = ImageDraw.Draw(qc_sheet)

    for idx_v, vk in enumerate(all_vks):
        v_dir = os.path.join(BATCH_DIR, vk)
        meta1 = json.load(open(os.path.join(v_dir, "edl_meta.json"), "r", encoding="utf-8"))
        tr1   = json.load(open(os.path.join(v_dir, "main_cut_clean.json"), "r", encoding="utf-8"))
        vo1   = read_f32_48k(os.path.join(v_dir, "edited_voice_48k.wav"))
        tot_f1 = int(meta1["total_frames"])
        dur1   = tot_f1 / FPS

        # 1. Build cut list: explicit micro-stumble cuts + dead silence pauses > 0.36s!
        cuts = list(EXPLICIT_CUTS.get(vk, []))
        ws1 = [w for s in tr1["segments"] for w in s["words"]]
        for k in range(len(ws1) - 1):
            g_start = ws1[k]["end"]
            g_end   = ws1[k+1]["start"]
            if (g_end - g_start) > 0.36:
                # Check if middle of gap is genuinely silent in vo1
                s_chk0 = int((g_start + 0.08) * SR)
                s_chk1 = int((g_end - 0.08) * SR)
                if s_chk1 > s_chk0 + 1200:
                    rms_gap = float(np.sqrt(np.mean(vo1[s_chk0:s_chk1] ** 2)))
                    if rms_gap < 0.026:
                        cuts.append((round(g_start + 0.08, 3), round(g_end - 0.08, 3)))

        # Sort & merge cuts, snap to exact 30fps frames!
        cuts.sort()
        merged_cuts = []
        for ca, cb in cuts:
            fa = max(1, int(round(ca * FPS)))
            fb = min(tot_f1 - 2, int(round(cb * FPS)))
            if fb - fa >= 3:
                if merged_cuts and fa <= merged_cuts[-1][1] + 2:
                    merged_cuts[-1] = (merged_cuts[-1][0], max(merged_cuts[-1][1], fb))
                else:
                    merged_cuts.append((fa, fb))

        # Convert cuts to keep_frame_ranges [(sf, ef_exclusive), ...]
        keep_ranges = []
        cur_f = 0
        for fa, fb in merged_cuts:
            if fa > cur_f:
                keep_ranges.append((cur_f, fa))
            cur_f = fb
        if cur_f < tot_f1:
            keep_ranges.append((cur_f, tot_f1))

        kept_f1 = sum(b - a for a, b in keep_ranges)
        v2_frames = max(30, int(round(kept_f1 / SPEED)))
        v2_dur    = v2_frames / FPS

        # Time mapping function from V1 seconds -> V2 (trimmed + 1.10x) seconds!
        def map_time_v1_to_v2(t_sec):
            f_in = t_sec * FPS
            acc = 0.0
            for a, b in keep_ranges:
                if f_in <= a:
                    return round((acc / FPS) / SPEED, 3)
                elif f_in < b:
                    return round(((acc + (f_in - a)) / FPS) / SPEED, 3)
                else:
                    acc += (b - a)
            return round((acc / FPS) / SPEED, 3)

        # 2. Compute exact Dead-Center Crop (scale=1.18 -> 1274x2266, crop=1080x1920:xc:yc)
        #    Target: speaker head_cx -> exact X = 540.0px; speaker head_top -> exact Y = 545.0px!
        c_info = centers[vk]
        S_FAC = 1.18
        SW, SH = int(round(1080 * S_FAC)), int(round(1920 * S_FAC))  # 1274 x 2266
        # Slightly blend 70% head_cx + 30% body_cx so both head AND shoulders look dead-center!
        subj_cx = 0.72 * c_info["head_cx"] + 0.28 * c_info["body_cx"]
        xc = int(round(subj_cx * S_FAC - 540.0))
        xc = max(0, min(SW - 1080, xc))

        target_head_top = 535.0 if vk not in ("v18", "v19") else 520.0
        yc = int(round(c_info["head_top"] * S_FAC - target_head_top))
        yc = max(0, min(SH - 1920, yc))

        new_head_top = round(c_info["head_top"] * S_FAC - yc, 1)
        new_chin_y   = round(c_info["chin_y"]   * S_FAC - yc, 1)
        new_head_cx  = round(c_info["head_cx"]  * S_FAC - xc, 1)

        # 3. Render v2_graded.mp4 and v2_matte.mp4 (trimmed + centered + 1.10x @ 30fps CFR)!
        v1_graded = os.path.join(v_dir, "edited_graded.mp4")
        v1_matte  = os.path.join(v_dir, "edited_matte.mp4")
        v2_graded = os.path.join(v_dir, "v2_graded.mp4")
        v2_matte  = os.path.join(v_dir, "v2_matte.mp4")
        v2_voice  = os.path.join(v_dir, "v2_voice_48k.wav")

        sel_parts, sel_ins = [], []
        for i_r, (fa, fb) in enumerate(keep_ranges):
            sel_parts.append(f"[0:v]select='between(n,{fa},{fb-1})',setpts=N/30/TB[s{i_r}];")
            sel_ins.append(f"[s{i_r}]")
        fc_v = (
            "".join(sel_parts) + "".join(sel_ins)
            + f"concat=n={len(keep_ranges)}:v=1:a=0,"
            + f"scale={SW}:{SH}:flags=bicubic,crop=1080:1920:{xc}:{yc},"
            + f"setpts=PTS/{SPEED:.4f},fps=30[vout]"
        )

        for src_v, dst_v in [(v1_graded, v2_graded), (v1_matte, v2_matte)]:
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-i", src_v,
                "-filter_complex", fc_v, "-map", "[vout]",
                "-r", "30", "-fps_mode", "cfr", "-frames:v", str(v2_frames),
                "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
                dst_v
            ], check=True)

        # 4. Slice audio with 15ms micro-fades + WSOLA pitch-preserving atempo=1.10!
        a_chunks = []
        for fa, fb in keep_ranges:
            sa = int(round((fa / FPS) * SR))
            sb = int(round((fb / FPS) * SR))
            seg = vo1[sa:sb]
            if len(seg) > 0:
                a_chunks.append(apply_micro_fade(seg, 0.014, 0.016))
        vo_cat = np.vstack(a_chunks)
        tmp_cat = os.path.join(v_dir, "_v2_cat_pre110.wav")
        with wave.open(tmp_cat, "wb") as wf:
            wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes((np.clip(vo_cat, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())

        tmp_110 = os.path.join(v_dir, "_v2_110_raw.wav")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", tmp_cat,
            "-af", f"atempo={SPEED:.4f}", "-ar", str(SR), "-ac", "2", tmp_110
        ], check=True)
        os.remove(tmp_cat)

        vo_110 = read_f32_48k(tmp_110)
        os.remove(tmp_110)
        n_target = int(round(v2_dur * SR))
        if len(vo_110) < n_target:
            vo_110 = np.vstack([vo_110, np.zeros((n_target - len(vo_110), 2), dtype=np.float32)])
        else:
            vo_110 = vo_110[:n_target]
        with wave.open(v2_voice, "wb") as wf:
            wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes((np.clip(vo_110, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())

        # 5. Update clean word timestamps & clone_spans to exact V2 1.10x timeline!
        def is_cut_word(ws, we):
            mid = (ws + we) * 0.5 * FPS
            return any(fa <= mid < fb for fa, fb in merged_cuts)

        v2_segs = []
        for seg in tr1["segments"]:
            new_ws = []
            for w in seg["words"]:
                if is_cut_word(w["start"], w["end"]):
                    continue
                ns = map_time_v1_to_v2(w["start"])
                ne = max(round(ns + 0.08, 3), map_time_v1_to_v2(w["end"]))
                new_ws.append({"word": w["word"], "start": ns, "end": ne})
            if new_ws:
                v2_segs.append({
                    "start": new_ws[0]["start"],
                    "end": new_ws[-1]["end"],
                    "text": " ".join(x["word"] for x in new_ws),
                    "words": new_ws,
                })

        v2_clones = []
        for cl in meta1.get("clone_spans", []):
            v2_clones.append({
                **cl,
                "start_s": map_time_v1_to_v2(cl["start_s"]),
                "end_s":   map_time_v1_to_v2(cl["end_s"]),
            })

        v2_meta = {
            **meta1,
            "total_frames": v2_frames,
            "duration_s": round(v2_dur, 3),
            "speed_factor": SPEED,
            "centered_head_cx": new_head_cx,
            "centered_head_top": new_head_top,
            "centered_chin_y": new_chin_y,
            "clone_spans": v2_clones,
            "cuts_removed_v1_frames": merged_cuts,
        }
        json.dump(v2_meta, open(os.path.join(v_dir, "v2_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        json.dump({"lang": "vi", "duration": round(v2_dur, 3), "total_frames": v2_frames, "segments": v2_segs},
                  open(os.path.join(v_dir, "v2_clean.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

        # Grab mid A-Roll frame for Centering Verification Sheet (with cyan center line at X=540!)
        raw_f = subprocess.check_output([
            "ffmpeg", "-v", "error", "-ss", f"{min(v2_dur*0.25, 3.0):.2f}", "-i", v2_graded,
            "-frames:v", "1", "-vf", "scale=240:426", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ])
        im_p = Image.frombytes("RGB", (240, 426), raw_f)
        dp = ImageDraw.Draw(im_p)
        dp.line([(120, 0), (120, 426)], fill=(54, 224, 210), width=1)  # Exact X=540 center guide!
        dp.rectangle([4, 4, 175, 26], fill=(10, 16, 22))
        dp.text((8, 7), f"{vk}•{meta1['code']} {v2_dur:.1f}s cx={new_head_cx:.0f}", fill=(255, 228, 100))
        qc_sheet.paste(im_p, ((idx_v % 6) * 240, (idx_v // 6) * 426))

        print(f"[{idx_v+1:02d}/18] {vk} ({meta1['code']}): {dur1:.1f}s -> {v2_dur:.2f}s (1.1x + {len(merged_cuts)} cuts) | head_cx={new_head_cx:.1f}px | chin_y={new_chin_y:.1f}px", flush=True)

    out_qc = os.path.join(BATCH_DIR, "v2_18_centered_speakers.jpg")
    qc_sheet.save(out_qc, quality=92)
    print(f"\n=== ALL 18 VIDEOS CENTERED (X=540), STUMBLE-FREE & 1.10x READY IN {time.time()-t0:.1f}s -> {out_qc} ===", flush=True)

if __name__ == "__main__":
    main()
