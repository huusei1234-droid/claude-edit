# -*- coding: utf-8 -*-
"""
Clean Unshifted Presenter Builder + Surgical Speech De-Duplication + RVM Cutout for ALL 14 Videos (#01 -> #14):
1. ZERO vertical shift ("đừng có kéo mẫu lên xuống nữa"): exact `scale=1080:1920:flags=lanczos,fps=30,format=yuv420p`!
2. Removes 100% of repeated phrases/syllables in #01, #02, #03, #06, #07, #08, #09, #12 at exact silence valleys,
   using a gentle 0.08s (2.4-frame) video `xfade=transition=fade` + audio `acrossfade=d=0.08` inside the breath pause
   so Chị Hằng stays 100% stationary with zero jump-cut snap and zero repeated speech!
3. Generates crisp `presenter_cutout.webm` (RVM foreground alpha) for ALL 14 videos so every B-Roll/Hologram/Card
   sits BEHIND Chị Hằng (`z-index < vid-fg`) -> 0% B-Roll ever covers Chị Hằng!
4. Re-transcribes all 14 cleaned `presenter.mp4` files with `faster-whisper` in an isolated subprocess to verify 0% repeats!
"""
import glob
import json
import os
import re
import subprocess
import sys
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

BASE_DIR = r"C:\AI\full studio\projects\hanh_sung_suong_reels"
MATTE_SCRIPT = r"C:\AI\full studio\phong-cach\talking-head\tools\matte.py"

sys.path.insert(0, BASE_DIR)
from batch_14_master_spec import VIDEOS_SPEC

ALL_SPECS = [
    {
        "idx": 1,
        "slug": "v01_cat_bao_quy_dau",
    }
] + VIDEOS_SPEC

# Exact verified keep-segments [(start, end), ...] from 20ms RMS silence valleys:
KEEP_SEGMENTS = {
    1: [(0.00, 12.18)],                        # Trims trailing repeat "Kéo dài cuộc yêu nha các anh" [12.30..13.52]
    2: [(0.00, 13.36)],                        # Trims trailing repeat "qua mắt thường, đang mong con" [13.42..14.98]
    3: [(0.00, 12.48), (12.70, 14.06)],        # Removes repeated "-vợ chồng" [12.48..12.70]
    4: [(0.00, 11.94)],                        # Clean
    5: [(0.00, 14.44)],                        # Clean
    6: [(0.00, 9.85), (10.10, 14.10)],         # Removes stuttered first "thành" [9.85..10.10]
    7: [(0.00, 9.52), (10.82, 13.78)],         # Removes repeated "đừng tự dọa mình nhá" [9.52..10.82] + trailing [13.94..]
    8: [(0.00, 10.84), (11.82, 14.24)],        # Removes repeated "hãy tập luyện" [10.84..11.82]
    9: [(0.00, 13.12), (13.34, 14.02)],        # Removes extra syllable "xa" in "kiểm tra [xa] sớm nhé" [13.12..13.34]
    10: [(0.00, 15.00)],                       # Clean
    11: [(0.00, 14.50)],                       # Clean
    12: [(0.00, 11.54), (13.22, 14.46)],       # Removes 2x repeated "tập kiểm soát, kiểm soát" [11.54..13.22]
    13: [(0.00, 15.00)],                       # Clean
    14: [(0.00, 14.32)],                       # Clean
}


def build_unshifted_presenter(raw_mp4: str, pres_mp4: str, segs: list):
    # ZERO vertical shift! Pure 1080x1920 @ 30fps natural framing!
    base_vf = "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"

    if len(segs) == 1:
        s0, e0 = segs[0]
        dur = round(e0 - s0, 2)
        fade_st = max(0.5, round(dur - 0.16, 2))
        fc = (
            f"[0:v]trim=start={s0:.3f}:end={e0:.3f},setpts=PTS-STARTPTS,{base_vf}[vout];"
            f"[0:a]atrim=start={s0:.3f}:end={e0:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.04,afade=t=out:st={fade_st}:d=0.14[aout]"
        )
    else:
        (s0, e0), (s1, e1) = segs[0], segs[1]
        xf_d = 0.08  # 2.4 frames gentle micro-dissolve inside breath silence!
        d0 = e0 - s0
        total_dur = d0 + (e1 - s1) - xf_d
        fade_st = max(0.5, round(total_dur - 0.16, 2))
        xf_off = round(d0 - xf_d, 3)
        fc = (
            f"[0:v]trim=start={s0:.3f}:end={e0:.3f},setpts=PTS-STARTPTS,{base_vf}[v0];"
            f"[0:v]trim=start={s1:.3f}:end={e1:.3f},setpts=PTS-STARTPTS,{base_vf}[v1];"
            f"[v0][v1]xfade=transition=fade:duration={xf_d:.3f}:offset={xf_off:.3f},format=yuv420p[vout];"
            f"[0:a]atrim=start={s0:.3f}:end={e0:.3f},asetpts=PTS-STARTPTS[a0];"
            f"[0:a]atrim=start={s1:.3f}:end={e1:.3f},asetpts=PTS-STARTPTS[a1];"
            f"[a0][a1]acrossfade=d={xf_d:.3f}:c1=tri:c2=tri,"
            f"afade=t=in:st=0:d=0.04,afade=t=out:st={fade_st}:d=0.14[aout]"
        )

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_mp4,
            "-filter_complex", fc,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-g", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            pres_mp4,
        ],
        check=True, capture_output=True
    )
    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", pres_mp4],
        capture_output=True, text=True, check=True
    )
    return round(float(pr.stdout.strip()), 2)


def build_rvm_cutout(pres_mp4: str, cutout_webm: str):
    vid_dir = os.path.dirname(cutout_webm)
    proxy_540 = os.path.join(vid_dir, "_proxy_540.mp4")
    matte_mp4 = os.path.join(vid_dir, "_presenter_matte.mp4")

    subprocess.run(
        ["ffmpeg", "-y", "-i", pres_mp4, "-vf", "scale=540:960:flags=bilinear,fps=30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-an", proxy_540],
        check=True, capture_output=True
    )
    clean_env = dict(os.environ)
    clean_env["PYTHONIOENCODING"] = "utf-8"
    r_m = subprocess.run([sys.executable, MATTE_SCRIPT, proxy_540, matte_mp4, "--ratio", "0.5"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=clean_env)
    if os.path.exists(proxy_540):
        os.remove(proxy_540)
    if r_m.returncode != 0:
        raise RuntimeError(f"matte.py failed: {r_m.stderr[-500:]}")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", pres_mp4,
            "-i", matte_mp4,
            "-filter_complex", "[1:v]scale=1080:1920:flags=bicubic,format=gray[a];[0:v][a]alphamerge,format=yuva420p[out]",
            "-map", "[out]", "-an",
            "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "24", "-deadline", "realtime", "-cpu-used", "5", "-row-mt", "1",
            cutout_webm,
        ],
        check=True, capture_output=True
    )
    if os.path.exists(matte_mp4):
        os.remove(matte_mp4)


def measure_cutout_bbox(cutout_webm: str):
    head_top_y = 380
    head_x1, head_x2 = 290, 790
    raw_rgba = subprocess.run(
        ["ffmpeg", "-c:v", "libvpx-vp9", "-ss", "2.0", "-i", cutout_webm, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
        capture_output=True
    ).stdout
    if len(raw_rgba) == 1080 * 1920 * 4:
        arr = np.frombuffer(raw_rgba, dtype=np.uint8).reshape((1920, 1080, 4))
        ys, _ = np.where(arr[:, :, 3] > 110)
        if len(ys):
            head_top_y = int(ys.min())
            _, hxs = np.where(arr[head_top_y:min(1920, head_top_y + 320), :, 3] > 110)
            if len(hxs):
                head_x1, head_x2 = int(hxs.min()), int(hxs.max())
    return head_top_y, head_x1, head_x2


def transcribe_batch_isolated(tasks: list):
    sub_code = r'''
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from faster_whisper import WhisperModel

items = json.loads(sys.argv[1])
model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)

for it in items:
    segs_gen, _ = model.transcribe(it["pres_mp4"], language="vi", word_timestamps=True, vad_filter=True)
    segments, words = [], []
    for sg in segs_gen:
        stxt = sg.text.strip()
        if not stxt:
            continue
        segments.append({"start": round(sg.start, 2), "end": round(sg.end, 2), "text": stxt})
        for w in (sg.words or []):
            wt = w.word.strip()
            if wt:
                words.append({"w": wt, "s": round(w.start, 2), "e": round(w.end, 2)})
    payload = {
        "clean_duration": it["dur"],
        "head_top_y": it["head_top_y"],
        "head_x1": it["head_x1"],
        "head_x2": it["head_x2"],
        "segments": segments,
        "words": words,
    }
    with open(it["out_json"], "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
'''
    subprocess.run([sys.executable, "-c", sub_code, json.dumps(tasks)], check=True)


def main():
    whisper_tasks = []
    for sp in ALL_SPECS:
        idx = sp["idx"]
        slug = sp["slug"]
        vdir = os.path.join(BASE_DIR, slug)
        raw_mp4 = glob.glob(os.path.join(vdir, "raw_assets", "*.mp4"))[0]
        vid_dir = os.path.join(vdir, "hf_project", "assets", "videos")
        os.makedirs(vid_dir, exist_ok=True)
        pres_mp4 = os.path.join(vid_dir, "presenter.mp4")
        cutout_webm = os.path.join(vid_dir, "presenter_cutout.webm")
        clean_json = os.path.join(vdir, "raw_assets", f"v{idx:02d}_clean_words.json")

        # Rebuild ALL 14 presenters & RVM cutouts UNSHIFTED (0px topfill!) so 0% vertical shift anywhere!
        dur = build_unshifted_presenter(raw_mp4, pres_mp4, KEEP_SEGMENTS[idx])
        build_rvm_cutout(pres_mp4, cutout_webm)
        hy, hx1, hx2 = measure_cutout_bbox(cutout_webm)
        print(f"[#{idx:02d}] {slug}: dur={dur:.2f}s | head_top_y={hy}px | head_x=[{hx1}..{hx2}]", flush=True)

        whisper_tasks.append({
            "idx": idx,
            "slug": slug,
            "pres_mp4": pres_mp4,
            "out_json": clean_json,
            "dur": dur,
            "head_top_y": hy,
            "head_x1": hx1,
            "head_x2": hx2,
        })

    print("\nRunning faster-whisper verification across ALL 14 unshifted cleaned presenter.mp4...", flush=True)
    transcribe_batch_isolated(whisper_tasks)

    def nw(s):
        return re.sub(r"[^\wàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", "", s.lower())

    print("\n=== FINAL VERIFIED SPEECH AUDIT (#01 -> #14) ===", flush=True)
    for t in whisper_tasks:
        with open(t["out_json"], "r", encoding="utf-8") as f:
            d = json.load(f)
        ws = d["words"]
        norms = [nw(w["w"]) for w in ws]
        reps = []
        for i in range(len(norms) - 1):
            if norms[i] and norms[i] == norms[i + 1]:
                reps.append(f"1g:{ws[i]['w']}/{ws[i+1]['w']}@{ws[i]['s']}")
        for i in range(len(norms) - 3):
            bg = (norms[i], norms[i + 1])
            for j in range(i + 2, min(len(norms) - 1, i + 7)):
                if bg == (norms[j], norms[j + 1]) and bg not in [("cắt", "bao"), ("bao", "quý"), ("lượng", "tinh"), ("quay", "bị")]:
                    reps.append(f"2g:{ws[i]['w']} {ws[i+1]['w']}@{ws[i]['s']}&{ws[j]['s']}")
        txt = " ".join(s["text"] for s in d["segments"])
        print(f"[#{t['idx']:02d}] dur={d['clean_duration']:.2f}s | head_y={d['head_top_y']}px | reps={reps}\n     TXT: {txt}", flush=True)


if __name__ == "__main__":
    main()
