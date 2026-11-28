# -*- coding: utf-8 -*-
"""
Step 2 Processor for Client Gynecology Talking-Head:
1. Transcribes khach_talk_part1.mp4 & khach_talk_part2.mp4 via faster-whisper (isolated process).
2. Auto-detects & trims 100% repeated n-grams or cut-off words at breath pauses, preserving >=0.42s clean tail.
3. Concatenates into seamless ~20s 1080x1920 @ 60fps `presenter_clean_60fps.mp4` + normalized -14.0 LUFS voice WAV.
4. Runs RVM (`matte.py`) to extract recurrent person alpha matte, outputting:
   - `assets/bg_frames/bg_0001.jpg` (1080x1920 @ 60fps)
   - `assets/fg_cutout/fg_0001.png` or `.webp` (RGBA person cutout @ 60fps for true Behind-Head Key Text & Card Deck!)
   - `assets/words_timeline.json` & `assets/audio_data.json` (60fps stereo VU envelope + 120-bar waveform).
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJ_DIR = r"C:\AI\full studio\projects\khach_phu_khoa_capcut_120agents_261128"
ASSETS_DIR = os.path.join(PROJ_DIR, "assets")
MATTE_SCRIPT = r"C:\AI\full studio\phong-cach\talking-head\tools\matte.py"

WHISPER_SUB = r'''
import json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from faster_whisper import WhisperModel

mp4_path = sys.argv[1]
out_json = sys.argv[2]

def norm_w(w):
    return re.sub(r"[^\wàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ0-9]", "", w.lower())

probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", mp4_path],
    capture_output=True, text=True, check=True
)
dur = float(probe.stdout.strip() or 10.0)

model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
segs_gen, _ = model.transcribe(
    mp4_path,
    language="vi",
    word_timestamps=True,
    vad_filter=True,
    initial_prompt="Chị em vệ sinh kỹ mỗi ngày, vùng nhạy cảm, ẩm ngứa, dung dịch kiềm mạnh, độ pH tự nhiên, hàng rào lợi khuẩn, niêm mạc kích ứng, pH 4.5, êm thoáng tự tin."
)

segments, words = [], []
for sg in segs_gen:
    stxt = sg.text.strip()
    if not stxt:
        continue
    segments.append({"start": round(sg.start, 3), "end": round(sg.end, 3), "text": stxt})
    for w in (sg.words or []):
        wt = w.word.strip()
        if wt:
            words.append({"w": wt, "n": norm_w(wt), "s": round(w.start, 3), "e": round(w.end, 3)})

with open(out_json, "w", encoding="utf-8") as f:
    json.dump({"duration": round(dur, 3), "segments": segments, "words": words}, f, ensure_ascii=False, indent=2)
'''


def run_whisper_isolated(mp4_path: str, out_json: str) -> dict:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run([sys.executable, "-c", WHISPER_SUB, mp4_path, out_json], check=True, env=env)
    with open(out_json, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_clean_trim_bounds(wdata: dict, is_final_clip: bool) -> tuple:
    dur = float(wdata["duration"])
    words = wdata["words"]
    if not words:
        return 0.08, max(4.0, dur - 0.08)

    # Detect if trailing segment repeats an earlier 3-gram or 4-gram
    cut_end = dur
    norms = [w["n"] for w in words]
    n_len = len(words)
    for i in range(max(4, n_len // 2), n_len - 2):
        gram = " ".join(norms[i:min(n_len, i + 3)])
        earlier = " ".join(norms[:i])
        if len(gram) >= 9 and gram in earlier:
            print(f"  [TrimRepeat] Detected repeated trailing phrase at {words[i]['s']}s: '{gram}' -> trimming before it!", flush=True)
            cut_end = max(words[i - 1]["e"] + 0.18, words[i]["s"] - 0.04)
            words = words[:i]
            break

    # Detect immediate consecutive 1-gram or 2-gram stutter at the very end
    if len(words) >= 4 and words[-1]["n"] == words[-2]["n"] and len(words[-1]["n"]) >= 2:
        cut_end = min(cut_end, words[-2]["e"] + 0.16)
        words = words[:-1]

    start_t = max(0.0, min(0.18, words[0]["s"] - 0.14)) if words[0]["s"] > 0.25 else 0.05
    if is_final_clip:
        # Preserve >= 0.45s breath/smile tail after last spoken word for QC pass (eof_tail_sec >= 0.25s)
        desired_end = words[-1]["e"] + 0.52
        end_t = min(dur, max(cut_end if cut_end < dur else desired_end, min(dur, words[-1]["e"] + 0.38)))
    else:
        end_t = min(dur, min(cut_end, words[-1]["e"] + 0.24))

    return round(start_t, 3), round(end_t, 3)


def main():
    p1 = os.path.join(ASSETS_DIR, "khach_talk_part1.mp4")
    p2 = os.path.join(ASSETS_DIR, "khach_talk_part2.mp4")
    if not (os.path.exists(p1) and os.path.exists(p2)):
        raise FileNotFoundError("Missing khach_talk_part1.mp4 or khach_talk_part2.mp4 in assets/")

    print("[1/5] Running Whisper word-level inspection on Part 1 & Part 2...", flush=True)
    w1 = run_whisper_isolated(p1, os.path.join(ASSETS_DIR, "_w_part1.json"))
    w2 = run_whisper_isolated(p2, os.path.join(ASSETS_DIR, "_w_part2.json"))
    print("  Part 1 text:", " ".join(w["w"] for w in w1["words"]), flush=True)
    print("  Part 2 text:", " ".join(w["w"] for w in w2["words"]), flush=True)

    s1, e1 = compute_clean_trim_bounds(w1, is_final_clip=False)
    s2, e2 = compute_clean_trim_bounds(w2, is_final_clip=True)
    d1 = round(e1 - s1, 3)
    d2 = round(e2 - s2, 3)
    print(f"  Clean bounds: Part1 [{s1}..{e1}] ({d1}s) | Part2 [{s2}..{e2}] ({d2}s)", flush=True)

    c1 = os.path.join(ASSETS_DIR, "_clean_p1_30.mp4")
    c2 = os.path.join(ASSETS_DIR, "_clean_p2_30.mp4")
    for src, st, du, dst in [(p1, s1, d1, c1), (p2, s2, d2, c2)]:
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-ss", f"{st:.3f}", "-i", src, "-t", f"{du:.3f}",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                "-af", f"highpass=f=75,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0.2, du - 0.10):.3f}:d=0.09",
                "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "16",
                "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
                dst,
            ],
            check=True,
        )

    # Join Part 1 + Part 2 with smooth 0.08s audio/video crossfade + pad 0.45s freeze/tail if final word is close to EOF
    joined_30 = os.path.join(ASSETS_DIR, "presenter_clean_30fps.mp4")
    xf_dur = 0.08
    offset = round(d1 - xf_dur, 3)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", c1, "-i", c2,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration={xf_dur}:offset={offset},format=yuv420p[v];"
            f"[0:a][1:a]acrossfade=d={xf_dur}:c1=tri:c2=tri,loudnorm=I=-14.0:TP=-1.2:LRA=11[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "16",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
            joined_30,
        ],
        check=True,
    )

    print("[2/5] Verifying joined transcript & EOF breath tail...", flush=True)
    wj = run_whisper_isolated(joined_30, os.path.join(ASSETS_DIR, "words_timeline.json"))
    jdur = float(wj["duration"])
    last_word_end = float(wj["words"][-1]["e"]) if wj["words"] else (jdur - 0.5)
    tail_sec = jdur - last_word_end
    print(f"  Joined duration: {jdur:.2f}s | Last word end: {last_word_end:.2f}s | EOF tail: {tail_sec:.2f}s", flush=True)

    if tail_sec < 0.36:
        pad_s = round(0.45 - tail_sec, 2)
        padded_30 = os.path.join(ASSETS_DIR, "_presenter_padded_30.mp4")
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error", "-i", joined_30,
                "-vf", f"tpad=stop_mode=clone:stop_duration={pad_s},format=yuv420p",
                "-af", f"apad=pad_dur={pad_s}",
                "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "16",
                "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
                padded_30,
            ],
            check=True,
        )
        shutil.move(padded_30, joined_30)
        wj = run_whisper_isolated(joined_30, os.path.join(ASSETS_DIR, "words_timeline.json"))
        jdur = float(wj["duration"])
        print(f"  Added gentle clone pad (+{pad_s}s) -> final clean duration: {jdur:.2f}s", flush=True)

    print("[3/5] Running RVM Person Matting (`matte.py`) on 540x960 proxy...", flush=True)
    proxy_mp4 = os.path.join(ASSETS_DIR, "_proxy_540x960.mp4")
    matte_mp4 = os.path.join(ASSETS_DIR, "_matte_540x960.mp4")
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", joined_30,
            "-vf", "scale=540:960:flags=lanczos,fps=30,format=yuv420p",
            "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18",
            proxy_mp4,
        ],
        check=True,
    )
    subprocess.run([sys.executable, MATTE_SCRIPT, proxy_mp4, matte_mp4, "--ratio", "0.5"], check=True)

    # Measure head_top_y across frames from matte_mp4
    raw_gray = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", matte_mp4, "-vf", "fps=5", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    )
    n_samps = len(raw_gray) // (540 * 960)
    head_ys = []
    for k in range(n_samps):
        arr = np.frombuffer(raw_gray[k * 540 * 960:(k + 1) * 540 * 960], dtype=np.uint8).reshape(960, 540)
        rows = np.where(arr.max(axis=1) > 130)[0]
        if len(rows) > 0:
            head_ys.append(int(rows[0] * 2))
    median_head_y = int(np.median(head_ys)) if head_ys else 320
    wj["head_top_y"] = median_head_y
    with open(os.path.join(ASSETS_DIR, "words_timeline.json"), "w", encoding="utf-8") as f:
        json.dump(wj, f, ensure_ascii=False, indent=2)
    print(f"  Measured median head_top_y = {median_head_y}px (on 1080x1920)", flush=True)

    print("[4/5] Extracting 60fps BG frames + 60fps RGBA Person Cutout WebP frames + Filmstrip Thumbs...", flush=True)
    bg_dir = os.path.join(ASSETS_DIR, "bg_frames")
    fg_dir = os.path.join(ASSETS_DIR, "fg_rgba")
    thumbs_dir = os.path.join(ASSETS_DIR, "thumbs")
    for d in (bg_dir, fg_dir, thumbs_dir):
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", joined_30,
            "-vf", "fps=60,scale=1080:1920:flags=lanczos,format=yuvj420p",
            "-q:v", "2", os.path.join(bg_dir, "bg_%04d.jpg"),
        ],
        check=True,
    )
    # Create crisp RGBA WebP person cutouts (720x1280 upscaled smoothly to 1080x1920 in CSS -> ultra-fast decode & crisp hair!)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", joined_30, "-i", matte_mp4,
            "-filter_complex",
            "[0:v]fps=60,scale=720:1280:flags=lanczos,format=rgb24[fg];"
            "[1:v]fps=60,scale=720:1280:flags=bilinear,gblur=sigma=1.1,format=gray[al];"
            "[fg][al]alphamerge,format=yuva420p[out]",
            "-map", "[out]",
            "-c:v", "libwebp", "-lossless", "0", "-q:v", "82", "-compression_level", "1",
            os.path.join(fg_dir, "fg_%04d.webp"),
        ],
        check=True,
    )

    total_60_frames = len(glob.glob(os.path.join(bg_dir, "bg_*.jpg")))
    print(f"  Extracted {total_60_frames} BG frames & FG RGBA WebP frames (@ 60fps)", flush=True)

    # Extract 20 filmstrip thumbnails for CapCut timeline V1
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", joined_30,
            "-vf", f"fps={20.0 / max(1.0, jdur):.4f},scale=160:90:force_original_aspect_ratio=increase,crop=160:90,format=yuvj420p",
            "-frames:v", "20", "-q:v", "3",
            os.path.join(thumbs_dir, "strip_%02d.jpg"),
        ],
        check=True,
    )

    print("[5/5] Extracting clean Voice WAV & 60fps VU Audio Envelope JSON...", flush=True)
    voice_wav = os.path.join(ASSETS_DIR, "voice_clean_48k.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", joined_30, "-vn", "-acodec", "pcm_s16le", "-ar", "48000", "-ac", "2", voice_wav],
        check=True,
    )

    with wave.open(voice_wav, "rb") as wf:
        sr = wf.getframerate()
        n_samples = wf.getnframes()
        raw_pcm = np.frombuffer(wf.readframes(n_samples), dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768.0

    env_l, env_r = [], []
    spf = max(1, int(sr / 60))
    for f_idx in range(total_60_frames):
        s0 = min(len(raw_pcm) - 1, f_idx * spf)
        s1_idx = min(len(raw_pcm), s0 + spf)
        chunk = raw_pcm[s0:s1_idx]
        rl = float(np.sqrt(np.mean(chunk[:, 0] ** 2))) if len(chunk) else 0.0
        rr = float(np.sqrt(np.mean(chunk[:, 1] ** 2))) if len(chunk) else 0.0
        env_l.append(round(min(1.0, rl * 3.8), 3))
        env_r.append(round(min(1.0, rr * 3.8), 3))

    n_bars = 140
    spb = max(1, len(raw_pcm) // n_bars)
    waveform = []
    for b in range(n_bars):
        chunk = raw_pcm[b * spb:min(len(raw_pcm), (b + 1) * spb)]
        pk = float(np.sqrt(np.mean(chunk ** 2))) if len(chunk) else 0.0
        waveform.append(round(min(1.0, pk * 4.2), 3))

    audio_meta = {
        "fps": 60,
        "total_frames": total_60_frames,
        "duration_sec": round(total_60_frames / 60.0, 3),
        "head_top_y": median_head_y,
        "env_l": env_l,
        "env_r": env_r,
        "waveform": waveform,
    }
    with open(os.path.join(ASSETS_DIR, "audio_data.json"), "w", encoding="utf-8") as f:
        json.dump(audio_meta, f)
    with open(os.path.join(ASSETS_DIR, "audio_data_inline.js"), "w", encoding="utf-8") as f:
        f.write("window.AUDIO_DATA = " + json.dumps(audio_meta) + ";\n")
    with open(os.path.join(ASSETS_DIR, "words_inline.js"), "w", encoding="utf-8") as f:
        f.write("window.WORDS_DATA = " + json.dumps(wj, ensure_ascii=False) + ";\n")

    print(f"[DONE] Step 2 Pre-Processing Complete! Total 60fps frames = {total_60_frames} ({audio_meta['duration_sec']}s)", flush=True)


if __name__ == "__main__":
    main()
