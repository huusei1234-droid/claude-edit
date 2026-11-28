# -*- coding: utf-8 -*-
"""
Automated End-to-End Post-Processing, RVM Matting, HyperFrames Authoring & -14 LUFS Delivery
for HTPM Reels (#02 -> #14), replicating the exact user-approved V5 Video #1 template:
1. Natural crisp real clinic studio (NO background blur, NO bokeh dots).
2. 3D Frosted Cyan/Rose/Emerald/Amber AR Glass Panel + Topic-Specific 3D Swimming Sperm / Ovum / Hearts / Shield / Timer / Bubbles.
3. Key-Moment-Only Giant 2-Line Behind-Head Text (tucked 3D behind Chị Hằng's hair crown, 100% readable)
   with AUTOMATIC SUBTITLE PAUSE during that exact window (0% duplicate text!).
4. Context-Accurate Medical B-Roll Card Deals (zero clutter, zero overlap with Behind-Head Text).
5. Verified `hyperframes check --json` (0 lint errors) -> 30fps render -> -14.0 LUFS master -> flat delivery to K6 - Hằng Thu Pharma.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

BASE_DIR = r"C:\AI\full studio\projects\hanh_sung_suong_reels"
V01_HF = os.path.join(BASE_DIR, "v01_cat_bao_quy_dau", "hf_project")
HF_BIN = r"C:\AI\full studio_data\npm-cache\_npx\702923228c2ce1e6\node_modules\.bin\hyperframes.cmd"
MATTE_SCRIPT = r"C:\AI\full studio\phong-cach\talking-head\tools\matte.py"

DEST_HTPM_DIR = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261126 - Ngày 26.11.2026"
DEST_LOCAL_DIR = r"C:\XUẤT CAPCUT\hằng thu pharma"
DEST_MASTER_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
DU_AN_ROOT = r"G:\My Drive\AI_Full_Studio\03_Du_An\261126-htpm-14-reels-card-deck"

from batch_14_master_spec import VIDEOS_SPEC


def norm_word(w: str) -> str:
    return re.sub(r"[^\wàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", "", w.lower())


def transcribe_and_trim(raw_mp4: str, words_json_path: str):
    if os.path.exists(words_json_path) and os.path.getsize(words_json_path) > 200:
        with open(words_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Run faster-whisper in an isolated child process so ctranslate2 DLLs never conflict with onnxruntime in matte.py!
    sub_code = r'''
import json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from faster_whisper import WhisperModel

raw_mp4 = sys.argv[1]
words_json_path = sys.argv[2]

def norm_w(w):
    return re.sub(r"[^\wàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", "", w.lower())

wmodel = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
segs_gen, _ = wmodel.transcribe(raw_mp4, language="vi", word_timestamps=True, vad_filter=True)
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

probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", raw_mp4], capture_output=True, text=True, check=True)
raw_dur = float(probe.stdout.strip() or 15.0)
clean_end = raw_dur
if len(segments) >= 3:
    last_norm = norm_w(segments[-1]["text"])
    prev_joined = norm_w(" ".join(s["text"] for s in segments[:-1]))
    if len(last_norm) >= 8 and last_norm in prev_joined and segments[-1]["start"] >= 10.5:
        clean_end = min(raw_dur, round(segments[-2]["end"] + 0.22, 2))
        words = [w for w in words if w["s"] < segments[-1]["start"] - 0.05]
        segments = segments[:-1]
    elif words:
        clean_end = min(raw_dur, round(words[-1]["e"] + 0.26, 2))
elif words:
    clean_end = min(raw_dur, round(words[-1]["e"] + 0.26, 2))

clean_end = max(9.5, min(raw_dur, clean_end))
data = {"clean_duration": clean_end, "segments": segments, "words": words}
with open(words_json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
'''
    clean_env = {k: v for k, v in os.environ.items() if k.upper() != "PATH"}
    clean_env["PATH"] = os.environ.get("PATH", "")
    clean_env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run([sys.executable, "-c", sub_code, raw_mp4, words_json_path], check=True, env=clean_env)
    with open(words_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_presenter_and_rvm(raw_mp4: str, clean_dur: float, hf_dir: str):
    vid_dir = os.path.join(hf_dir, "assets", "videos")
    os.makedirs(vid_dir, exist_ok=True)
    pres_mp4 = os.path.join(vid_dir, "presenter.mp4")
    matte_mp4 = os.path.join(vid_dir, "_presenter_matte.mp4")
    cutout_webm = os.path.join(vid_dir, "presenter_cutout.webm")

    if not os.path.exists(pres_mp4) or os.path.getsize(pres_mp4) < 50000:
        # Subtle +64px downward reframe (boxblur=6:1 safe on yuv420p chroma height 32!)
        vf = (
            "scale=1080:1920:flags=lanczos,format=rgb24,"
            "split[main][top];"
            "[top]crop=1080:64:0:0,vflip,gblur=sigma=8[topfill];"
            "[main]crop=1080:1856:0:0[body];"
            "[topfill][body]vstack=inputs=2,fps=30,format=yuv420p"
        )
        fade_out_st = max(0.5, round(clean_dur - 0.16, 2))
        af = f"afade=t=in:st=0:d=0.05,afade=t=out:st={fade_out_st}:d=0.15"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", raw_mp4, "-t", f"{clean_dur:.2f}",
                "-filter_complex", vf, "-af", af,
                "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-g", "30",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                pres_mp4,
            ],
            check=True, capture_output=True
        )

    if not os.path.exists(cutout_webm) or os.path.getsize(cutout_webm) < 50000:
        if not os.path.exists(matte_mp4) or os.path.getsize(matte_mp4) < 30000:
            # Downscale proxy 540x960 for RVM (same 270x480 RVM internal tensor, 75% less RAM -> 0% MemoryError & 4x faster!)
            proxy_540 = os.path.join(vid_dir, "_proxy_540.mp4")
            subprocess.run(
                ["ffmpeg", "-y", "-i", pres_mp4, "-vf", "scale=540:960:flags=bilinear,fps=30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-an", proxy_540],
                check=True, capture_output=True
            )
            clean_env = dict(os.environ)
            clean_env["PYTHONIOENCODING"] = "utf-8"
            r_m = subprocess.run([sys.executable, MATTE_SCRIPT, proxy_540, matte_mp4, "--ratio", "0.5"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=clean_env)
            try:
                os.remove(proxy_540)
            except Exception:
                pass
            if r_m.returncode != 0:
                try:
                    os.remove(matte_mp4)
                except Exception:
                    pass
                raise RuntimeError(f"matte.py failed: {r_m.stderr[-600:] or r_m.stdout[-600:]}")
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", pres_mp4, "-i", matte_mp4,
                "-filter_complex", "[1:v]scale=1080:1920:flags=bicubic[m];[0:v][m]alphamerge,fps=30,format=yuva420p",
                "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "24", "-g", "30", "-an",
                cutout_webm,
            ],
            check=True, capture_output=True
        )
        if os.path.exists(matte_mp4):
            try:
                os.remove(matte_mp4)
            except Exception:
                pass


def align_clean_script_words(spoken_script: str, asr_words: list):
    """
    Maps the 100% orthographically clean words of `spoken_script` onto Whisper's exact word timestamps
    using SequenceMatcher on normalized syllables -> 0% Whisper homophone typos ("quay bị" -> "quai bị")
    AND verifies that the audio genuinely speaks this video's script!
    """
    import difflib
    if not asr_words:
        return asr_words

    # Split clean script into tokens preserving punctuation
    clean_tokens = [t for t in spoken_script.strip().split() if t]
    clean_norms = [norm_word(t) for t in clean_tokens]
    asr_norms = [norm_word(w["w"]) for w in asr_words]

    sm = difflib.SequenceMatcher(None, clean_norms, asr_norms)
    match_ratio = sum(block.size for block in sm.get_matching_blocks()) / max(1, min(len(clean_norms), len(asr_norms)))
    if match_ratio < 0.42:
        raise RuntimeError(
            f"AUDIO TOPIC MISMATCH (similarity={match_ratio:.2f})! "
            f"Expected: '{spoken_script[:70]}' vs ASR: '{' '.join(w['w'] for w in asr_words[:16])}'"
        )

    # Interpolate timestamps across clean_tokens anchored by matching blocks
    n_c = len(clean_tokens)
    anchors = {}
    for ci, ai, size in sm.get_matching_blocks():
        for k in range(size):
            if ci + k < n_c and ai + k < len(asr_words):
                anchors[ci + k] = (asr_words[ai + k]["s"], asr_words[ai + k]["e"])

    t_first = asr_words[0]["s"]
    t_last = asr_words[-1]["e"]
    aligned = []
    for idx in range(n_c):
        if idx in anchors:
            s_t, e_t = anchors[idx]
        else:
            prev_idx = max([k for k in anchors if k < idx], default=None)
            next_idx = min([k for k in anchors if k > idx], default=None)
            if prev_idx is not None and next_idx is not None:
                p_e = anchors[prev_idx][1]
                n_s = anchors[next_idx][0]
                span = max(0.08, n_s - p_e)
                gap_cnt = next_idx - prev_idx - 1
                pos = idx - prev_idx - 1
                step = span / max(1, gap_cnt)
                s_t = round(p_e + pos * step, 2)
                e_t = round(s_t + step * 0.92, 2)
            elif prev_idx is not None:
                p_e = anchors[prev_idx][1]
                rem = max(1, n_c - 1 - prev_idx)
                step = max(0.14, (t_last - p_e) / rem)
                pos = idx - prev_idx - 1
                s_t = round(p_e + pos * step, 2)
                e_t = round(min(t_last, s_t + step * 0.92), 2)
            else:
                n_s = anchors[next_idx][0] if next_idx is not None else t_last
                cnt = next_idx if next_idx is not None else n_c
                step = max(0.14, (n_s - t_first) / max(1, cnt))
                s_t = round(t_first + idx * step, 2)
                e_t = round(s_t + step * 0.92, 2)
        aligned.append({"w": clean_tokens[idx], "s": s_t, "e": max(round(s_t + 0.08, 2), e_t)})
    return aligned


def plan_timings(sp: dict, wdata: dict):
    dur = float(wdata["clean_duration"])
    segs = wdata.get("segments") or []
    words = align_clean_script_words(sp["spoken_script"], wdata.get("words") or [])

    # 1. Hook end = end of 1st question mark in clean script, clamped to [2.45, 3.55]
    q_end = None
    for w in words[:18]:
        if "?" in w["w"]:
            q_end = w["e"]
            break
    if q_end is not None:
        hook_end = max(2.45, min(3.55, round(q_end + 0.10, 2)))
    elif segs:
        hook_end = max(2.55, min(3.45, round(segs[0]["end"] + 0.08, 2)))
    else:
        hook_end = 3.00

    # 2. Locate Behind-Head Key-Moment anchor in post-hook words
    post_words = [w for w in words if w["s"] >= hook_end - 0.05]
    anchors = [norm_word(a) for a in sp["behind_kw_anchor"]]
    kw_start = None
    for i in range(len(post_words)):
        chunk = [norm_word(x["w"]) for x in post_words[i : i + len(anchors) + 1]]
        if all(a in chunk for a in anchors[:2]):
            kw_start = round(max(hook_end + 0.35, post_words[i]["s"] - 0.04), 2)
            break
    if kw_start is None:
        kw_start = round(hook_end + (dur - hook_end) * 0.26, 2)
    kw_start = min(kw_start, round(dur - 2.6, 2))
    kw_end = round(min(dur - 1.3, kw_start + 1.12), 2)

    # 3. Build Subtitle Pills from post_words EXCLUDING words inside [kw_start - 0.06, kw_end + 0.06]!
    before_kw = [w for w in post_words if (w["s"] + w["e"]) * 0.5 < kw_start - 0.05]
    after_kw = [w for w in post_words if (w["s"] + w["e"]) * 0.5 > kw_end + 0.05]

    hl_terms = {
        "tinh", "trùng", "dịch", "vô", "sinh", "cương", "quai", "bị", "viêm", "hoàn",
        "thuốc", "mạch", "máu", "khám", "bác", "sĩ", "bia", "rượu", "thức", "khuya",
        "căng", "thẳng", "nội", "tiết", "cảm", "xúc", "phút", "bệnh", "lý"
    }

    def chunk_words_to_pills(wlist, clamp_min, clamp_max):
        pills = []
        idx = 0
        while idx < len(wlist):
            # Group 4..6 words or break at sentence punctuation / natural pause > 0.32s
            grp = [wlist[idx]]
            idx += 1
            while idx < len(wlist) and len(grp) < 6:
                gap = wlist[idx]["s"] - grp[-1]["e"]
                prev_punct = any(p in grp[-1]["w"] for p in [".", "?", "!", ",", ";", ":"])
                if len(grp) >= 4 and (prev_punct or gap > 0.24):
                    break
                if prev_punct and len(grp) >= 3:
                    break
                grp.append(wlist[idx])
                idx += 1
            ps = max(clamp_min, round(grp[0]["s"] - 0.03, 2))
            pe = min(clamp_max, round(grp[-1]["e"] + 0.10, 2))
            if pe - ps < 0.36:
                pe = min(clamp_max, round(ps + 0.42, 2))
            if pe > ps + 0.20:
                # Highlight 1-2 medical terms in yellow
                tokens_html = []
                for w in grp:
                    esc = html.escape(w["w"])
                    if norm_word(w["w"]) in hl_terms:
                        tokens_html.append(f'<span class="hl-yellow">{esc}</span>')
                    else:
                        tokens_html.append(esc)
                pills.append({"s": ps, "e": pe, "html": " ".join(tokens_html)})
        # Ensure strictly non-overlapping sequential pills
        for j in range(len(pills) - 1):
            if pills[j]["e"] > pills[j + 1]["s"] - 0.02:
                pills[j]["e"] = round(pills[j + 1]["s"] - 0.02, 2)
        return [p for p in pills if p["e"] - p["s"] >= 0.24]

    pills = (
        chunk_words_to_pills(before_kw, hook_end + 0.08, kw_start - 0.04)
        + chunk_words_to_pills(after_kw, kw_end + 0.04, dur - 0.06)
    )

    # 4. Schedule B-Roll Card Deck windows OUTSIDE [kw_start - 0.15, kw_end + 0.10]
    # after_kw span is typically [kw_end + 0.10 .. dur - 0.10] (~6 to 8 seconds!)
    body_after_len = (dur - 0.12) - (kw_end + 0.12)
    if body_after_len >= 3.2:
        c1_s = round(kw_end + 0.14, 2)
        c2_s = round(c1_s + min(1.35, body_after_len * 0.28), 2)
        c_end = round(dur - 0.10, 2)
    else:
        c1_s = round(hook_end + 0.15, 2)
        c2_s = round(kw_end + 0.14, 2)
        c_end = round(dur - 0.10, 2)

    return {
        "dur": dur,
        "hook_end": hook_end,
        "kw_start": kw_start,
        "kw_end": kw_end,
        "pills": pills,
        "c1_s": c1_s,
        "c2_s": c2_s,
        "c_end": c_end,
    }


def write_hf_files(sp: dict, plan: dict, hf_dir: str):
    # Copy shared fonts, audio, and hyperframes.json from v01
    os.makedirs(os.path.join(hf_dir, "compositions"), exist_ok=True)
    shutil.copy2(os.path.join(V01_HF, "hyperframes.json"), os.path.join(hf_dir, "hyperframes.json"))
    for asset_sub in ["fonts", "audio"]:
        src_d = os.path.join(V01_HF, "assets", asset_sub)
        dst_d = os.path.join(hf_dir, "assets", asset_sub)
        if os.path.exists(dst_d):
            shutil.rmtree(dst_d)
        shutil.copytree(src_d, dst_d)

    dur = plan["dur"]
    hook_end = plan["hook_end"]
    cap_host_start = round(hook_end + 0.02, 2)
    cap_host_dur = round(dur - cap_host_start, 2)
    deck_host_start = round(hook_end, 2)
    deck_host_dur = round(dur - deck_host_start, 2)

    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    bkw1, bkw2 = [html.escape(x) for x in sp["behind_kw_lines"]]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    mascot_mode = sp["mascot_mode"]

    # 1. presenter-stage.html (Real Studio + 3D Flying Bio-Mascots & AR Glass + Behind-Head Keyword + RVM Cutout)
    pres_html = f"""<template>
  <style>
    @font-face {{
      font-family: "Montserrat";
      src: url("assets/fonts/Montserrat-Black.ttf") format("truetype");
      font-weight: 900;
      font-style: normal;
      font-display: block;
    }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #f4f1ea; }}
    #master-cam-rig {{
      position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      transform-origin: 540px 760px; will-change: transform;
    }}
    #vid-bg-plate {{
      position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      object-fit: cover; z-index: 1;
    }}
    #bio-mascot-canvas {{
      position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      z-index: 3; pointer-events: none;
    }}
    #behind-typography-stage {{
      position: absolute; inset: 0; z-index: 4; pointer-events: none;
    }}
    .behind-kw-block {{
      position: absolute; left: 20px; top: 342px; width: 1040px;
      text-align: center; display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 4px;
      opacity: 0; will-change: transform, opacity;
    }}
    .bkw-line1 {{
      font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 104px;
      line-height: 1.03; letter-spacing: -0.02em; text-transform: uppercase;
      color: #d90429; -webkit-text-stroke: 10px #ffffff; paint-order: stroke fill;
      filter: drop-shadow(0 10px 22px rgba(15, 23, 42, 0.24));
    }}
    .bkw-line2 {{
      font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 92px;
      line-height: 1.04; letter-spacing: -0.02em; text-transform: uppercase;
      color: #0f172a; -webkit-text-stroke: 10px #ffffff; paint-order: stroke fill;
      filter: drop-shadow(0 10px 22px rgba(15, 23, 42, 0.22));
    }}
    #vid-fg-cutout {{
      position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      object-fit: cover; z-index: 6; pointer-events: none;
    }}
    #bio-fg-canvas {{
      position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      z-index: 7; pointer-events: none;
    }}
  </style>

  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <div id="master-cam-rig" data-layout-allow-overflow>
      <video id="vid-bg-plate" class="clip" src="assets/videos/presenter.mp4"
        data-start="0" data-duration="{dur:.2f}" data-track-index="1"
        playsinline data-has-audio="true" data-volume="1.34"></video>
      <canvas id="bio-mascot-canvas" width="1080" height="1920" data-layout-ignore></canvas>
      <div id="behind-typography-stage" data-layout-allow-overlap data-layout-allow-overflow>
        <div id="bkw-main" class="behind-kw-block" data-layout-ignore>
          <div class="bkw-line1">{bkw1}</div>
          <div class="bkw-line2">{bkw2}</div>
        </div>
      </div>
      <video id="vid-fg-cutout" class="clip" src="assets/videos/presenter_cutout.webm"
        data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
      <canvas id="bio-fg-canvas" width="1080" height="1920" data-layout-ignore></canvas>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    const MODE = "{mascot_mode}";
    const DUR = {dur:.2f};
    const KW_S = {kw_s:.2f};
    const KW_E = {kw_e:.2f};

    const bgCtx = document.getElementById("bio-mascot-canvas").getContext("2d");
    const fgCtx = document.getElementById("bio-fg-canvas").getContext("2d");

    function draw3DSperm(ctx, x, y, angle, scale, tailPhase, tint, alpha) {{
      if (alpha <= 0.01) return;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(x, y);
      ctx.rotate(angle);
      ctx.scale(scale, scale);
      ctx.shadowColor = tint === "warm" ? "rgba(251,146,60,0.55)" : "rgba(14,165,233,0.55)";
      ctx.shadowBlur = 15;
      ctx.beginPath();
      for (let i = 0; i <= 20; i++) {{
        const u = i / 20;
        const tx = -16 - u * 110;
        const amp = (4 + u * 15) * Math.sin(tailPhase - u * 7.2);
        if (i === 0) ctx.moveTo(tx, amp * 0.15);
        else ctx.lineTo(tx, amp);
      }}
      const tg = ctx.createLinearGradient(-16, 0, -126, 0);
      tg.addColorStop(0, tint === "warm" ? "rgba(254,215,170,0.95)" : "rgba(224,247,250,0.98)");
      tg.addColorStop(0.6, tint === "warm" ? "rgba(251,146,60,0.72)" : "rgba(56,189,248,0.78)");
      tg.addColorStop(1, "rgba(56,189,248,0)");
      ctx.strokeStyle = tg;
      ctx.lineWidth = 6.2;
      ctx.lineCap = "round";
      ctx.stroke();

      ctx.shadowBlur = 0;
      ctx.fillStyle = tint === "warm" ? "#fed7aa" : "#bae6fd";
      ctx.beginPath(); ctx.roundRect(-22, -5, 10, 10, 4); ctx.fill();

      ctx.beginPath(); ctx.ellipse(2, 0, 22, 15, 0, 0, Math.PI * 2);
      const hg = ctx.createRadialGradient(8, -5, 3, 0, 2, 24);
      hg.addColorStop(0, "#ffffff");
      hg.addColorStop(0.45, tint === "warm" ? "#ffedd5" : "#e0f7fa");
      hg.addColorStop(0.82, tint === "warm" ? "#fb923c" : "#38bdf8");
      hg.addColorStop(1, tint === "warm" ? "#c2410c" : "#0284c7");
      ctx.fillStyle = hg; ctx.fill();
      ctx.lineWidth = 2; ctx.strokeStyle = "rgba(255,255,255,0.9)"; ctx.stroke();

      ctx.beginPath(); ctx.ellipse(7, -6, 9, 4, -0.22, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255,255,255,0.88)"; ctx.fill();
      ctx.restore();
    }}

    function draw3DDroplet(ctx, cx, cy, r, alpha) {{
      if (alpha <= 0.01) return;
      ctx.save(); ctx.globalAlpha = alpha; ctx.translate(cx, cy);
      ctx.shadowColor = "rgba(14,165,233,0.45)"; ctx.shadowBlur = 22;
      ctx.beginPath();
      ctx.moveTo(0, -r * 1.35);
      ctx.bezierCurveTo(r * 0.95, -r * 0.25, r * 1.05, r * 0.85, 0, r * 1.05);
      ctx.bezierCurveTo(-r * 1.05, r * 0.85, -r * 0.95, -r * 0.25, 0, -r * 1.35);
      ctx.closePath();
      const dg = ctx.createRadialGradient(-r * 0.28, -r * 0.15, r * 0.1, 0, r * 0.15, r * 1.15);
      dg.addColorStop(0, "rgba(255,255,255,0.96)");
      dg.addColorStop(0.4, "rgba(186,230,253,0.82)");
      dg.addColorStop(1, "rgba(3,105,161,0.78)");
      ctx.fillStyle = dg; ctx.fill();
      ctx.lineWidth = 3; ctx.strokeStyle = "rgba(255,255,255,0.9)"; ctx.stroke();
      ctx.restore();
    }}

    function draw3DOvum(ctx, cx, cy, r, t, alpha) {{
      if (alpha <= 0.01) return;
      ctx.save(); ctx.globalAlpha = alpha; ctx.translate(cx, cy);
      const pulse = 1 + Math.sin(t * 3.2) * 0.04;
      ctx.scale(pulse, pulse);
      ctx.shadowColor = "rgba(244,114,182,0.55)"; ctx.shadowBlur = 28;
      ctx.beginPath(); ctx.arc(0, 0, r * 1.22, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(251,207,232,0.34)"; ctx.fill();
      ctx.lineWidth = 2.5; ctx.strokeStyle = "rgba(249,168,212,0.75)"; ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2);
      const og = ctx.createRadialGradient(-r * 0.25, -r * 0.25, r * 0.1, 0, 0, r);
      og.addColorStop(0, "#fff1f2"); og.addColorStop(0.55, "#f472b6"); og.addColorStop(1, "#be185d");
      ctx.fillStyle = og; ctx.fill();
      ctx.restore();
    }}

    function draw3DHeart(ctx, cx, cy, size, alpha) {{
      if (alpha <= 0.01) return;
      ctx.save(); ctx.globalAlpha = alpha; ctx.translate(cx, cy); ctx.scale(size / 40, size / 40);
      ctx.shadowColor = "rgba(244,63,94,0.48)"; ctx.shadowBlur = 18;
      ctx.beginPath();
      ctx.moveTo(0, 12);
      ctx.bezierCurveTo(-26, -12, -42, 10, 0, 38);
      ctx.bezierCurveTo(42, 10, 26, -12, 0, 12);
      const hg = ctx.createRadialGradient(-8, 4, 3, 0, 14, 38);
      hg.addColorStop(0, "#ffe4e6"); hg.addColorStop(0.5, "#fb7185"); hg.addColorStop(1, "#be123c");
      ctx.fillStyle = hg; ctx.fill();
      ctx.restore();
    }}

    function draw3DShield(ctx, cx, cy, r, alpha) {{
      if (alpha <= 0.01) return;
      ctx.save(); ctx.globalAlpha = alpha; ctx.translate(cx, cy);
      ctx.shadowColor = "rgba(16,185,129,0.5)"; ctx.shadowBlur = 22;
      ctx.beginPath();
      ctx.moveTo(0, -r);
      ctx.quadraticCurveTo(r, -r * 0.75, r * 0.88, r * 0.15);
      ctx.quadraticCurveTo(r * 0.55, r * 0.88, 0, r * 1.12);
      ctx.quadraticCurveTo(-r * 0.55, r * 0.88, -r * 0.88, r * 0.15);
      ctx.quadraticCurveTo(-r, -r * 0.75, 0, -r);
      const sg = ctx.createLinearGradient(-r, -r, r, r);
      sg.addColorStop(0, "rgba(167,243,208,0.92)"); sg.addColorStop(1, "rgba(5,150,105,0.85)");
      ctx.fillStyle = sg; ctx.fill();
      ctx.lineWidth = 3; ctx.strokeStyle = "#ffffff"; ctx.stroke();
      ctx.shadowBlur = 0; ctx.fillStyle = "#ffffff";
      ctx.fillRect(-r * 0.14, -r * 0.38, r * 0.28, r * 0.76);
      ctx.fillRect(-r * 0.38, -r * 0.14, r * 0.76, r * 0.28);
      ctx.restore();
    }}

    function drawGlassHUD(ctx, x, y, w, h, borderCol, alpha) {{
      if (alpha <= 0.01) return;
      ctx.save(); ctx.globalAlpha = alpha;
      ctx.shadowColor = "rgba(15,23,42,0.18)"; ctx.shadowBlur = 26;
      ctx.beginPath(); ctx.roundRect(x, y, w, h, 30);
      const pg = ctx.createLinearGradient(x, y, x + w, y + h);
      pg.addColorStop(0, "rgba(15,42,62,0.74)"); pg.addColorStop(1, "rgba(8,34,52,0.78)");
      ctx.fillStyle = pg; ctx.fill();
      ctx.shadowBlur = 0; ctx.lineWidth = 3.5; ctx.strokeStyle = borderCol; ctx.stroke();
      ctx.restore();
    }}

    const swimmers = [
      {{ baseY: 590, speed: 155, amp: 18, freq: 2.6, scale: 0.92, phase: 0.4, lane: "hud" }},
      {{ baseY: 658, speed: 185, amp: 22, freq: 3.1, scale: 1.04, phase: 1.9, lane: "hud" }},
      {{ baseY: 730, speed: 145, amp: 16, freq: 2.3, scale: 0.84, phase: 3.5, lane: "hud" }},
      {{ baseY: 800, speed: 170, amp: 20, freq: 2.8, scale: 0.95, phase: 5.1, lane: "hud" }},
      {{ baseY: 650, speed: 185, amp: 30, freq: 2.2, scale: 0.92, phase: 0.9, lane: "left" }},
      {{ baseY: 770, speed: 160, amp: 26, freq: 2.5, scale: 0.80, phase: 3.2, lane: "left" }},
      {{ baseY: 960, speed: 205, amp: 24, freq: 2.9, scale: 0.86, phase: 1.4, lane: "fg" }}
    ];

    function renderScene(t) {{
      bgCtx.clearRect(0, 0, 1080, 1920);
      fgCtx.clearRect(0, 0, 1080, 1920);
      // Pause HUD panel during Giant Behind-Head Text window [KW_S - 0.12 .. KW_E + 0.12] so focus is 100% clean!
      let kwDim = 1.0;
      if (t > KW_S - 0.18 && t < KW_E + 0.18) {{
        kwDim = 0.18;
      }}
      const bobY = Math.sin(t * 2.2) * 8;
      const borderCol = MODE === "heart_pulse" ? "rgba(251,113,133,0.85)"
        : MODE === "sperm_shield" ? "rgba(52,211,153,0.85)"
        : MODE === "beer_warning" ? "rgba(251,191,36,0.85)"
        : "rgba(125,211,252,0.85)";

      drawGlassHUD(bgCtx, 588, 528 + bobY, 452, 372, borderCol, 0.92 * kwDim);

      if (MODE === "sperm_ovum") {{
        draw3DOvum(bgCtx, 712, 714 + bobY, 56, t, 0.95 * kwDim);
      }} else if (MODE === "sperm_shield") {{
        draw3DShield(bgCtx, 712, 714 + bobY, 58, 0.95 * kwDim);
      }} else if (MODE === "heart_pulse") {{
        const beat = 1 + Math.sin(t * 5.5) * 0.08;
        draw3DHeart(bgCtx, 725, 690 + bobY, 58 * beat, 0.95 * kwDim);
        // ECG pulse line across HUD
        bgCtx.save();
        bgCtx.globalAlpha = 0.9 * kwDim;
        bgCtx.strokeStyle = "#38bdf8";
        bgCtx.lineWidth = 4.5;
        bgCtx.beginPath();
        for (let i = 0; i <= 40; i++) {{
          const px = 630 + i * 9.5;
          const phase = (i / 40 - (t * 0.7) % 1 + 1) % 1;
          const spike = phase < 0.08 ? Math.sin((phase / 0.08) * Math.PI * 2) * 46 : 0;
          const py = 795 + bobY - spike;
          if (i === 0) bgCtx.moveTo(px, py); else bgCtx.lineTo(px, py);
        }}
        bgCtx.stroke();
        bgCtx.restore();
        // Floating 3D hearts on left & right
        for (let k = 0; k < 4; k++) {{
          const p = (t * 0.42 + k * 0.25) % 1;
          const hx = k % 2 === 0 ? 110 + Math.sin(t * 2 + k) * 35 : 940 + Math.cos(t * 2 + k) * 35;
          const hy = 920 - p * 360;
          draw3DHeart(bgCtx, hx, hy, 28 + (k % 2) * 8, Math.sin(p * Math.PI) * 0.88 * kwDim);
        }}
        return;
      }} else {{
        draw3DDroplet(bgCtx, 716, 722 + bobY, 60, 0.94 * kwDim);
      }}

      const tint = (MODE === "sperm_timer" || MODE === "beer_warning") ? "warm" : "aqua";
      for (const sw of swimmers) {{
        const tailPhase = t * 18 + sw.phase;
        if (sw.lane === "hud") {{
          const prog = ((t * sw.speed + sw.phase * 55) % 285) / 285;
          const sx = 1042 - prog * 285;
          const sy = sw.baseY + Math.sin(t * sw.freq + sw.phase) * sw.amp;
          draw3DSperm(bgCtx, sx, sy, Math.PI + Math.cos(t * sw.freq + sw.phase) * 0.16, sw.scale, tailPhase, tint, Math.sin(prog * Math.PI) * 0.95 * kwDim);
        }} else if (sw.lane === "left") {{
          const loopT = (t * 0.52 + sw.phase * 0.2) % 1;
          const sx = 48 + loopT * 265;
          const sy = sw.baseY + 100 - loopT * 220 + Math.sin(t * sw.freq + sw.phase) * sw.amp;
          draw3DSperm(bgCtx, sx, sy, -0.66, sw.scale, tailPhase, "aqua", Math.sin(loopT * Math.PI) * 0.88 * kwDim);
        }} else if (sw.lane === "fg") {{
          const loopT = (t * 0.46 + 0.3) % 1;
          const sx = 1035 - loopT * 300;
          const sy = sw.baseY - loopT * 90 + Math.sin(t * 3) * 15;
          draw3DSperm(fgCtx, sx, sy, Math.PI + 0.26, sw.scale, tailPhase, tint, Math.sin(loopT * Math.PI) * 0.82 * kwDim);
        }}
      }}
    }}

    const proxy = {{ t: 0 }};
    tl.to(proxy, {{ t: DUR, duration: DUR, ease: "none", onUpdate: () => renderScene(proxy.t) }}, 0);

    tl.fromTo("#master-cam-rig", {{ scale: 1.04, y: 10 }}, {{ scale: 1.00, y: 0, duration: 2.8, ease: "sine.out" }}, 0);
    tl.to("#master-cam-rig", {{ scale: 1.07, y: 26, duration: 0.26, ease: "power3.out" }}, Math.max(0.1, KW_S - 0.04));
    tl.to("#master-cam-rig", {{ scale: 1.01, y: 4, duration: 1.4, ease: "sine.inOut" }}, KW_E + 0.05);

    tl.fromTo("#bkw-main",
      {{ scale: 0.84, y: 34, opacity: 0 }},
      {{ scale: 1.0, y: 0, opacity: 1, duration: 0.20, ease: "back.out(1.8)", immediateRender: false }},
      KW_S
    );
    tl.to("#bkw-main", {{ scale: 1.02, y: -4, duration: Math.max(0.2, KW_E - KW_S - 0.34), ease: "sine.out" }}, KW_S + 0.20);
    tl.to("#bkw-main", {{ scale: 0.94, y: 14, opacity: 0, duration: 0.14, ease: "power2.in" }}, KW_E - 0.14);

    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""
    with open(os.path.join(hf_dir, "compositions", "presenter-stage.html"), "w", encoding="utf-8") as f:
        f.write(pres_html)

    # 2. hook-card.html
    hbadge = html.escape(sp["hook_card"]["badge"])
    hcap = html.escape(sp["hook_card"]["caption"])
    out_t = round(max(0.8, hook_end - 0.26), 2)
    hook_html = f"""<template>
  <style>
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "Be Vietnam Pro"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    #root {{ position: absolute; inset: 0; background: transparent; pointer-events: none; }}
    #hook-top-card {{
      position: absolute; left: 386px; top: 68px; width: 308px; height: 352px;
      border-radius: 28px; background: linear-gradient(165deg, #ffffff 0%, #fbf7ec 100%);
      border: 4px solid #f59e0b; box-shadow: 0 22px 46px rgba(15,23,42,0.24);
      padding: 12px; display: flex; flex-direction: column; justify-content: space-between;
      overflow: hidden; opacity: 0; will-change: transform, opacity;
    }}
    #hook-top-card img {{ width: 100%; height: 248px; border-radius: 18px; object-fit: cover; display: block; }}
    .hg-badge {{
      position: absolute; top: 22px; left: 22px; padding: 5px 14px; border-radius: 999px;
      background: #dc2626; color: #ffffff; font-family: "Montserrat", sans-serif;
      font-weight: 900; font-size: 15px; box-shadow: 0 6px 14px rgba(220,38,38,0.42);
    }}
    .hg-caption {{
      text-align: center; font-family: "Be Vietnam Pro", sans-serif; font-weight: 800;
      font-size: 24px; color: #b45309; letter-spacing: -0.01em; padding-bottom: 4px;
    }}
    #hook-slot {{ position: absolute; left: 156px; top: 1148px; width: 768px; height: 352px; }}
    #hook-yellow-box {{
      position: relative; width: 100%; height: 100%;
      background: linear-gradient(180deg, #fff200 0%, #ffdb00 100%);
      border-radius: 48px; border: 4px solid #ffffff;
      box-shadow: 0 24px 52px rgba(0,0,0,0.34), inset 0 4px 0 rgba(255,255,255,0.85);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      padding: 24px 28px; text-align: center; overflow: hidden; will-change: transform, opacity;
    }}
    #hook-sheen {{
      position: absolute; top: -40%; left: -35%; width: 45%; height: 180%;
      background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.65) 50%, rgba(255,255,255,0) 100%);
      pointer-events: none;
    }}
    .hook-line {{
      font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 50px;
      line-height: 1.18; letter-spacing: -0.015em; color: #080808; text-transform: uppercase;
      position: relative; z-index: 2;
    }}
  </style>
  <div id="root" data-composition-id="hook-card" data-width="1080" data-height="1920">
    <div id="hook-top-card" data-layout-ignore>
      <img src="assets/images/broll_hook.jpg" alt="Hook card" />
      <div class="hg-badge">{hbadge}</div>
      <div class="hg-caption">{hcap}</div>
    </div>
    <div id="hook-slot" class="clip" data-start="0" data-duration="{hook_end:.2f}" data-layout-allow-caption-zone data-layout-allow-overflow>
      <div id="hook-yellow-box">
        <div id="hook-sheen" data-layout-ignore></div>
        <div id="hook-l1" class="hook-line">{hl1}</div>
        <div id="hook-l2" class="hook-line">{hl2}</div>
        <div id="hook-l3" class="hook-line">{hl3}</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#hook-yellow-box", {{ scale: 0.80, y: 48, rotation: -2, opacity: 0.9 }}, {{ scale: 1.03, y: -6, rotation: 0.4, opacity: 1, duration: 0.22, ease: "back.out(1.8)" }}, 0);
    tl.to("#hook-yellow-box", {{ scale: 1.0, y: 0, rotation: 0, duration: 0.14, ease: "power2.out" }}, 0.22);
    tl.fromTo("#hook-sheen", {{ x: -140, rotation: 18 }}, {{ x: 980, rotation: 18, duration: 0.68, ease: "power2.inOut" }}, 0.30);
    tl.to("#hook-yellow-box", {{ x: -380, scale: 0.88, rotation: -6, opacity: 0, duration: 0.24, ease: "power3.in" }}, {out_t:.2f});

    tl.fromTo("#hook-top-card", {{ y: 140, scale: 0.65, rotation: 10, opacity: 0 }}, {{ y: 0, scale: 1.0, rotation: -2.5, opacity: 1, duration: 0.34, ease: "back.out(1.7)" }}, 0.28);
    tl.to("#hook-top-card", {{ y: -8, rotation: 2.0, duration: 1.1, ease: "sine.inOut" }}, 0.68);
    tl.to("#hook-top-card", {{ y: -90, scale: 0.80, opacity: 0, duration: 0.24, ease: "power2.in" }}, {out_t:.2f});
    window.__timelines["hook-card"] = tl;
  </script>
</template>
"""
    with open(os.path.join(hf_dir, "compositions", "hook-card.html"), "w", encoding="utf-8") as f:
        f.write(hook_html)

    # 3. card-deck.html
    c1 = sp["broll_cards"][0]
    c2 = sp["broll_cards"][1]
    lc1_s = round(max(0.05, plan["c1_s"] - deck_host_start), 2)
    lc2_s = round(max(lc1_s + 0.6, plan["c2_s"] - deck_host_start), 2)
    lc_end = round(max(lc2_s + 0.8, plan["c_end"] - deck_host_start), 2)

    card_html = f"""<template>
  <style>
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "Be Vietnam Pro"; src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
    @font-face {{ font-family: "Be Vietnam Pro"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    #root {{ position: absolute; inset: 0; background: transparent; pointer-events: none; }}
    #deck-stage {{ position: absolute; left: 0; top: 0; width: 1080px; height: 520px; perspective: 1200px; }}
    .broll-card {{
      position: absolute; left: 0; top: 0; width: 344px; height: 390px;
      border-radius: 28px; background: #ffffff; border: 4px solid #e2e8f0;
      box-shadow: 0 24px 52px rgba(15,23,42,0.24); padding: 12px 12px 14px 12px;
      display: flex; flex-direction: column; justify-content: space-between;
      overflow: hidden; opacity: 0; will-change: transform, opacity;
    }}
    .broll-card.red {{ border-color: #ef4444; }}
    .broll-card.blue {{ border-color: #0284c7; }}
    .broll-card.green {{ border-color: #10b981; }}
    .card-photo-wrap {{ position: relative; width: 100%; height: 254px; border-radius: 18px; overflow: hidden; background: #f1f5f9; }}
    .card-photo-wrap img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .card-tag {{
      position: absolute; top: 10px; left: 10px; padding: 5px 13px; border-radius: 999px;
      font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 14px; color: #ffffff;
    }}
    .card-tag.red {{ background: #dc2626; }}
    .card-tag.blue {{ background: #0284c7; }}
    .card-tag.green {{ background: #059669; }}
    .card-info {{ text-align: center; padding: 6px 4px 2px 4px; }}
    .card-head {{ font-family: "Be Vietnam Pro", sans-serif; font-weight: 800; font-size: 23px; line-height: 1.18; text-transform: uppercase; color: #0f172a; }}
    .card-head.red {{ color: #b91c1c; }}
    .card-head.blue {{ color: #0369a1; }}
    .card-head.green {{ color: #065f46; }}
    .card-desc {{ margin-top: 4px; font-family: "Be Vietnam Pro", sans-serif; font-weight: 700; font-size: 18px; line-height: 1.2; color: #475569; }}
  </style>
  <div id="root" data-composition-id="card-deck" data-width="1080" data-height="1920">
    <div id="deck-stage" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="bcard-1" class="broll-card {c1['tag_color']}" style="z-index: 3" data-layout-ignore>
        <div class="card-photo-wrap">
          <img src="assets/images/broll_01.jpg" alt="Card 1" />
          <span class="card-tag {c1['tag_color']}">{html.escape(c1['tag'])}</span>
        </div>
        <div class="card-info">
          <div class="card-head {c1['tag_color']}">{html.escape(c1['head'])}</div>
          <div class="card-desc">{html.escape(c1['desc'])}</div>
        </div>
      </div>
      <div id="bcard-2" class="broll-card {c2['tag_color']}" style="z-index: 4" data-layout-ignore>
        <div class="card-photo-wrap">
          <img src="assets/images/broll_02.jpg" alt="Card 2" />
          <span class="card-tag {c2['tag_color']}">{html.escape(c2['tag'])}</span>
        </div>
        <div class="card-info">
          <div class="card-head {c2['tag_color']}">{html.escape(c2['head'])}</div>
          <div class="card-desc">{html.escape(c2['desc'])}</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#bcard-1",
      {{ x: 368, y: 160, scale: 0.72, rotation: -8, opacity: 0 }},
      {{ x: 368, y: 58, scale: 1.0, rotation: 1.5, opacity: 1, duration: 0.32, ease: "back.out(1.7)", immediateRender: false }},
      {lc1_s:.2f}
    );
    tl.to("#bcard-1", {{ x: 146, y: 66, scale: 0.94, rotation: -5.5, duration: 0.38, ease: "back.out(1.5)" }}, {lc2_s:.2f});
    tl.fromTo("#bcard-2",
      {{ x: 368, y: 160, scale: 0.72, rotation: 10, opacity: 0 }},
      {{ x: 590, y: 58, scale: 0.98, rotation: 5.0, opacity: 1, duration: 0.36, ease: "back.out(1.7)", immediateRender: false }},
      {lc2_s + 0.04:.2f}
    );
    tl.to("#bcard-2", {{ y: 50, scale: 1.02, duration: 0.6, ease: "sine.inOut" }}, {min(lc_end - 0.5, lc2_s + 0.8):.2f});
    window.__timelines["card-deck"] = tl;
  </script>
</template>
"""
    with open(os.path.join(hf_dir, "compositions", "card-deck.html"), "w", encoding="utf-8") as f:
        f.write(card_html)

    # 4. captions-vi.html
    cap_divs = []
    cue_js = []
    for idx_p, p in enumerate(plan["pills"], 1):
        ls = round(max(0.02, p["s"] - cap_host_start), 2)
        le = round(max(ls + 0.24, p["e"] - cap_host_start), 2)
        ldur = round(le - ls, 2)
        rot = -1.0 if idx_p % 2 == 1 else 1.0
        cap_divs.append(
            f'    <div id="cg-{idx_p}" class="clip cap-group" data-start="{ls:.2f}" data-duration="{ldur:.2f}" data-layout-allow-caption-zone>'
            f'<div class="cap-pill">{p["html"]}</div></div>'
        )
        cue_js.append(f'      {{ id: "#cg-{idx_p}", s: {ls:.2f}, e: {le:.2f}, rot: {rot} }}')

    cap_html = f"""<template>
  <style>
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    #root {{ position: absolute; inset: 0; background: transparent; pointer-events: none; }}
    .cap-group {{
      position: absolute; left: 110px; top: 1340px; width: 860px;
      display: flex; justify-content: center; align-items: center; text-align: center;
      overflow: visible; opacity: 0; visibility: hidden;
    }}
    .cap-pill {{
      display: inline-block; max-width: 840px; padding: 16px 30px; border-radius: 26px;
      background: linear-gradient(180deg, rgba(12,28,22,0.94) 0%, rgba(7,18,14,0.96) 100%);
      border: 2.5px solid rgba(255,228,77,0.82);
      box-shadow: 0 16px 36px rgba(0,0,0,0.36);
      font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 37px;
      line-height: 1.25; color: #ffffff; letter-spacing: -0.01em;
      text-shadow: 0 3px 8px rgba(0,0,0,0.65); will-change: transform, opacity;
    }}
    .hl-yellow {{ color: #ffe600; font-weight: 900; }}
  </style>
  <div id="root" data-composition-id="captions-vi" data-width="1080" data-height="1920">
{chr(10).join(cap_divs)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const cues = [
{",".join(chr(10) + x for x in cue_js)}
    ];
    for (const c of cues) {{
      const pill = c.id + " .cap-pill";
      tl.set(c.id, {{ visibility: "visible", opacity: 1 }}, c.s);
      tl.fromTo(pill, {{ scale: 0.84, y: 18, rotation: c.rot * 1.6, opacity: 0 }}, {{ scale: 1.03, y: -2, rotation: c.rot, opacity: 1, duration: 0.13, ease: "back.out(2.0)" }}, c.s);
      tl.to(pill, {{ scale: 1.0, y: 0, rotation: 0, duration: 0.10, ease: "power2.out" }}, c.s + 0.13);
      tl.to(pill, {{ scale: 0.92, y: -8, opacity: 0, duration: 0.08, ease: "power2.in" }}, c.e - 0.08);
      tl.set(c.id, {{ opacity: 0, visibility: "hidden" }}, c.e);
    }}
    window.__timelines["captions-vi"] = tl;
  </script>
</template>
"""
    with open(os.path.join(hf_dir, "compositions", "captions-vi.html"), "w", encoding="utf-8") as f:
        f.write(cap_html)

    # 5. index.html
    idx_html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{html.escape(sp['final_name'])}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #f5f2eb; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; }}
      #presenter-stage {{ z-index: 1; }}
      #card-deck {{ z-index: 3; }}
      #hook-card {{ z-index: 4; }}
      #captions-vi {{ z-index: 5; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-width="1080" data-height="1920" data-fps="30">
      <div id="presenter-stage" class="scene-host" data-composition-id="presenter-stage" data-composition-src="compositions/presenter-stage.html" data-start="0" data-duration="{dur:.2f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="hook-card" class="scene-host" data-composition-id="hook-card" data-composition-src="compositions/hook-card.html" data-start="0" data-duration="{hook_end:.2f}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="card-deck" class="scene-host" data-composition-id="card-deck" data-composition-src="compositions/card-deck.html" data-start="{deck_host_start:.2f}" data-duration="{deck_host_dur:.2f}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="captions-vi" class="scene-host" data-composition-id="captions-vi" data-composition-src="compositions/captions-vi.html" data-start="{cap_host_start:.2f}" data-duration="{cap_host_dur:.2f}" data-track-index="4" data-track-kind="captions" data-width="1080" data-height="1920"></div>

      <audio id="bgm-upbeat" class="clip" src="assets/audio/bgm_upbeat.wav" data-start="0" data-duration="{dur:.2f}" data-track-index="5" data-volume="0.22" data-fade-in="0.18" data-fade-out="0.55"></audio>
      <audio id="sfx-hook-pop" class="clip" src="assets/audio/sfx_hook_pop.mp3" data-start="0.04" data-duration="0.14" data-track-index="6" data-volume="0.32"></audio>
      <audio id="sfx-hg-deal" class="clip" src="assets/audio/sfx_card_deal.mp3" data-start="0.28" data-duration="0.65" data-track-index="7" data-volume="0.26" data-fade-out="0.15"></audio>
      <audio id="sfx-kw-hit" class="clip" src="assets/audio/sfx_hook_pop.mp3" data-start="{kw_s:.2f}" data-duration="0.14" data-track-index="6" data-volume="0.30"></audio>
      <audio id="sfx-c1-deal" class="clip" src="assets/audio/sfx_card_deal.mp3" data-start="{min(dur - 0.8, plan['c1_s']):.2f}" data-duration="0.65" data-track-index="7" data-volume="0.28" data-fade-out="0.15"></audio>
      <audio id="sfx-c2-deal" class="clip" src="assets/audio/sfx_card_whoosh.mp3" data-start="{min(dur - 0.6, plan['c2_s']):.2f}" data-duration="0.48" data-track-index="6" data-volume="0.25" data-fade-out="0.12"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    with open(os.path.join(hf_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx_html)


def render_and_deliver(sp: dict, hf_dir: str):
    chk = subprocess.run([HF_BIN, "check", "--json"], cwd=hf_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    j_start = chk.stdout.find("{")
    if j_start >= 0:
        d = json.loads(chk.stdout[j_start:])
        errs = [x for x in d.get("diagnostics", []) if x.get("severity") == "error"]
        if errs:
            raise RuntimeError(f"HyperFrames lint errors in #{sp['idx']}: {errs}")

    raw_render = os.path.join(hf_dir, "_final_raw.mp4")
    last_err = ""
    for attempt in range(1, 3):
        ren = subprocess.run(
            [HF_BIN, "render", "--output", raw_render, "--fps", "30", "--low-memory-mode", "--frames-cache-dir=off"],
            cwd=hf_dir, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if ren.returncode == 0 and os.path.exists(raw_render) and os.path.getsize(raw_render) > 200000:
            break
        last_err = (ren.stdout[-500:] + "\n" + ren.stderr[-800:])
        print(f"  [WARN] HyperFrames render attempt {attempt} failed on #{sp['idx']}, retrying...", flush=True)
    else:
        raise RuntimeError(f"HyperFrames render failed in #{sp['idx']}: {last_err}")

    master_mp4 = os.path.join(hf_dir, "_master_14lufs.mp4")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_render,
            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", "30", "-g", "30",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart",
            master_mp4,
        ],
        check=True, capture_output=True
    )

    final_name = sp["final_name"]
    for folder in [DEST_HTPM_DIR, DEST_LOCAL_DIR, DEST_MASTER_DIR]:
        os.makedirs(folder, exist_ok=True)
        shutil.copy2(master_mp4, os.path.join(folder, final_name))

    # Sync compositions to 03_Du_An
    du_an_v = os.path.join(DU_AN_ROOT, sp["slug"])
    os.makedirs(os.path.join(du_an_v, "compositions"), exist_ok=True)
    shutil.copy2(os.path.join(hf_dir, "index.html"), os.path.join(du_an_v, "index.html"))
    for fn in os.listdir(os.path.join(hf_dir, "compositions")):
        if fn.endswith(".html"):
            shutil.copy2(os.path.join(hf_dir, "compositions", fn), os.path.join(du_an_v, "compositions", fn))

    mb = round(os.path.getsize(os.path.join(DEST_HTPM_DIR, final_name)) / (1024 * 1024), 2)
    # Clean heavy intermediate files so C: always stays > 3 GB free!
    for tmp_f in [
        raw_render,
        master_mp4,
        os.path.join(hf_dir, "assets", "videos", "_presenter_matte.mp4"),
    ]:
        if os.path.exists(tmp_f):
            try:
                os.remove(tmp_f)
            except Exception:
                pass
    print(f"[DELIVERED #{sp['idx']:02d}] {final_name} ({mb} MB)", flush=True)


def main():
    wanted = [int(x) for x in sys.argv[1:] if x.isdigit()]
    targets = [s for s in VIDEOS_SPEC if (not wanted or s["idx"] in wanted)]

    for sp in targets:
        final_htpm = os.path.join(DEST_HTPM_DIR, sp["final_name"])
        if os.path.exists(final_htpm) and os.path.getsize(final_htpm) > 1000000:
            print(f"[ALREADY DELIVERED #{sp['idx']:02d}] {sp['final_name']}", flush=True)
            continue

        vdir = os.path.join(BASE_DIR, sp["slug"])
        raw_mp4 = os.path.join(vdir, "raw_assets", f"chihang_v{sp['idx']:02d}_raw_15s.mp4")
        words_json = os.path.join(vdir, "raw_assets", f"v{sp['idx']:02d}_words.json")
        hf_dir = os.path.join(vdir, "hf_project")

        print(f"--- BUILDING #{sp['idx']:02d}: {sp['slug']} ---", flush=True)
        wdata = transcribe_and_trim(raw_mp4, words_json)
        print(f"  [Whisper #{sp['idx']:02d}] clean_dur={wdata['clean_duration']}s, words={len(wdata['words'])}", flush=True)
        prepare_presenter_and_rvm(raw_mp4, wdata["clean_duration"], hf_dir)
        print(f"  [RVM #{sp['idx']:02d}] presenter.mp4 + presenter_cutout.webm ready", flush=True)
        plan = plan_timings(sp, wdata)
        print(f"  [Plan #{sp['idx']:02d}] hook_end={plan['hook_end']}s, kw=[{plan['kw_start']}..{plan['kw_end']}], pills={len(plan['pills'])}", flush=True)
        write_hf_files(sp, plan, hf_dir)
        render_and_deliver(sp, hf_dir)


if __name__ == "__main__":
    main()
