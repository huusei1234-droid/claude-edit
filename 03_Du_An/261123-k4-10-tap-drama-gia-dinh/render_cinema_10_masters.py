"""
Cinema Director Master Renderer & 0% Cut-Off Auditor (`render_cinema_10_masters.py`):
- Run with `D:\AI\full studio\voice-studio\.venv\Scripts\python.exe` (has both CUDA `demucs` + `faster_whisper`).
- Modes:
  1. `audit ep01 ep02 ...` -> runs Demucs + Whisper word-timestamps + Deep -35dB RMS tail check on every clip, reporting any clip where speech was cut off near EOF (`tail_margin < 0.14s` & `end_rms > 0.014`).
  2. `render ep01 ep02 ...` -> renders frame-accurate `1080x1920 @ 30fps` NVENC Masters with `0.52s–0.65s` Cinema Breath Hold after the final syllable, seamless looped 2-Act BGM (`EQ Voice Pocket`), `3D LUT`, QA Contact Sheets, and delivers `261123 K4 <Tên phim> final.mp4` to all 3 destinations!
"""
import json, os, shutil, subprocess, sys, wave
import numpy as np
from faster_whisper import WhisperModel

sys.path.insert(0, r"d:\AI\full studio\output\k4-10-videos-261123")
from episodes_01_to_05_spec import EPISODES_01_05
from episodes_06_to_10_spec import EPISODES_06_10

ALL_EPISODES = {**EPISODES_01_05, **EPISODES_06_10}

BASE_DIR   = r"d:\AI\full studio\output\k4-10-videos-261123"
PREV_BGM   = r"d:\AI\full studio\output\k4-5-videos-261122\bgm"
BGM_DIR    = os.path.join(BASE_DIR, "bgm")
DEMUCS_DIR = os.path.join(BASE_DIR, "demucs_cache")
QC_DIR     = os.path.join(BASE_DIR, "qc_sheets")
ART_DIR    = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DEMUCS_PY  = r"D:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
LUT_PATH   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"

K4_DRIVE_DIR     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"D:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"
DU_AN_CLOUD_DIR  = r"G:\My Drive\AI_Full_Studio\03_Du_An\261123-k4-10-tap-drama-gia-dinh"

for d in (BGM_DIR, DEMUCS_DIR, QC_DIR):
    os.makedirs(d, exist_ok=True)

for bfn in os.listdir(PREV_BGM):
    sp = os.path.join(PREV_BGM, bfn)
    dp = os.path.join(BGM_DIR, bfn)
    if os.path.isfile(sp) and not os.path.exists(dp):
        shutil.copy2(sp, dp)

_WHISPER = None
def get_whisper():
    global _WHISPER
    if _WHISPER is None:
        _WHISPER = WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=10)
    return _WHISPER

def probe_video(p):
    j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration", "-of", "json", p
    ]).decode("utf-8"))
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])

def detect_letterbox_bars(mp4_path, w, h, t_mid):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", mp4_path,
        "-frames:v", "1", "-pix_fmt", "gray", "-f", "rawvideo", "-"
    ])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
    row_means = arr.mean(axis=1)
    top_b = 0
    while top_b < h // 5 and row_means[top_b] < 16.0:
        top_b += 1
    bot_b = 0
    while bot_b < h // 5 and row_means[h - 1 - bot_b] < 16.0:
        bot_b += 1
    top_b = ((top_b + 1) // 2) * 2 if top_b >= 4 else 0
    bot_b = ((bot_b + 1) // 2) * 2 if bot_b >= 4 else 0
    return top_b, bot_b

def run_demucs_vocals(mp4_path, tag_key):
    out_wav = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    src_mtime = os.path.getmtime(mp4_path)
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 20_000 and os.path.getmtime(out_wav) >= src_mtime:
        return out_wav
    raw_wav = os.path.join(DEMUCS_DIR, f"{tag_key}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", "44100", raw_wav], check=True)
    subprocess.run([
        DEMUCS_PY, "-m", "demucs.separate",
        "-n", "htdemucs", "--two-stems=vocals", "-d", "cuda",
        "-o", DEMUCS_DIR, raw_wav
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    sep_voc = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "vocals.wav")
    shutil.copy2(sep_voc, out_wav)
    return out_wav

def analyze_vocals_cinema(vocals_wav, total_dur, is_wide=False):
    cache_json = vocals_wav.replace("_vocals.wav", "_bounds.json")
    if os.path.exists(cache_json) and os.path.getmtime(cache_json) >= os.path.getmtime(vocals_wav):
        return json.load(open(cache_json, encoding="utf-8"))

    with wave.open(vocals_wav, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        pcm = pcm.reshape(-1, nch).mean(axis=1)

    win_sec = 0.020
    win = int(sr * win_sec)
    nf = len(pcm) // win
    if nf < 6:
        res = {"ss": 0.06, "to": max(2.2, total_dur - 0.05), "speech_end": total_dur - 0.5, "cutoff_risk": False, "transcript": ""}
        json.dump(res, open(cache_json, "w", encoding="utf-8"), ensure_ascii=False)
        return res

    rms = np.sqrt(np.mean(pcm[:nf * win].reshape(nf, win) ** 2, axis=1))
    min_idx = int(0.06 / win_sec)
    peak = float(np.max(rms[min_idx:])) if min_idx < len(rms) else float(np.max(rms))
    # Deep -35dB threshold so soft trailing Vietnamese syllables ("ạ", "nhé", "không") are NEVER chopped!
    thr = max(0.0026, peak * 0.018)
    active = np.where(rms[min_idx:] >= thr)[0] + min_idx
    if len(active) > 0:
        r_first = active[0] * win_sec
        r_last  = (active[-1] + 1) * win_sec
    else:
        r_first = 0.20
        r_last  = min(total_dur - 0.5, 3.0)

    # Whisper word-level timestamp verification
    wm = get_whisper()
    segs, _ = wm.transcribe(vocals_wav, language="vi", word_timestamps=True, vad_filter=False, beam_size=2)
    words = []
    texts = []
    for s in segs:
        if s.text.strip():
            texts.append(s.text.strip())
        for w in (s.words or []):
            words.append((float(w.start), float(w.end), w.word.strip()))

    if words:
        t_first = max(0.05, min(r_first, words[0][0]))
        t_last  = min(total_dur, max(r_last, words[-1][1]))
    else:
        t_first = r_first
        t_last  = r_last

    end_rms = float(np.mean(rms[-7:])) if len(rms) >= 7 else 0.0
    tail_margin = total_dur - t_last
    tr_full = " ".join(texts)
    hallucinated_silence = any(k in tr_full.lower() for k in ("subscribe", "ghiền mì gõ", "la la school")) or peak < 0.015
    cutoff_risk = bool((tail_margin < 0.13 and end_rms > max(0.014, peak * 0.08)) or hallucinated_silence)

    pre_pad  = 0.36 if is_wide else 0.20
    post_pad = 0.66 if is_wide else 0.54
    ss = max(0.05, t_first - pre_pad)
    to = min(total_dur - 0.03, t_last + post_pad)
    if to - ss < 2.6:
        to = min(total_dur - 0.03, ss + 2.8)

    res = {
        "ss": round(ss, 3),
        "to": round(to, 3),
        "speech_start": round(t_first, 3),
        "speech_end": round(t_last, 3),
        "total_dur": round(total_dur, 3),
        "tail_margin": round(tail_margin, 3),
        "end_rms": round(end_rms, 4),
        "cutoff_risk": cutoff_risk,
        "transcript": " ".join(texts),
    }
    json.dump(res, open(cache_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res

def audit_episodes(ep_ids):
    bad = []
    for ep_id in ep_ids:
        cfg = ALL_EPISODES[ep_id]
        raw_dir = os.path.join(BASE_DIR, ep_id, "raw_9x16")
        print(f"\n=== AUDITING SPEECH COMPLETION: {ep_id.upper()} ({len(cfg['shots'])} scenes) ===", flush=True)
        for sid, scale, skey, chars, sp, act, speaker, dlg in cfg["shots"]:
            mp4 = os.path.join(raw_dir, f"{sid}.mp4")
            if not os.path.exists(mp4):
                print(f"  [MISSING] {ep_id}_{sid}")
                bad.append({"ep": ep_id, "sid": sid, "reason": "missing"})
                continue
            if not speaker:
                continue
            _, _, tdur = probe_video(mp4)
            voc = run_demucs_vocals(mp4, f"{ep_id}_9x16_{sid}")
            info = analyze_vocals_cinema(voc, tdur, is_wide=scale in ("WIDE", "WIDE_CROWD", "MED"))
            flag = "⚠️ CUTOFF_RISK" if info["cutoff_risk"] else "OK"
            print(f"  [{sid}] {flag} | raw={tdur:.2f}s | speech={info['speech_start']:.2f}->{info['speech_end']:.2f}s (margin={info['tail_margin']:.2f}s) | '{info['transcript'][:65]}'", flush=True)
            if info["cutoff_risk"]:
                bad.append({"ep": ep_id, "sid": sid, "reason": "cutoff_risk", **info})
    out_p = os.path.join(BASE_DIR, "cutoff_audit_report.json")
    json.dump(bad, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n=== AUDIT SUMMARY: {len(bad)} flagged clips -> {out_p} ===", flush=True)
    return bad

def deliver_episode(src_mp4, vn_title):
    fname = f"261123 K4 {vn_title} final.mp4"
    targets = [
        ("brand_path", K4_DRIVE_DIR),
        ("master_cloud_path", MASTER_CLOUD_DIR),
        ("local_path", LOCAL_CAPCUT_DIR),
    ]
    out = {"filename": fname}
    for key, tdir in targets:
        os.makedirs(tdir, exist_ok=True)
        dst = os.path.join(tdir, fname)
        shutil.copy2(src_mp4, dst)
        out[key] = dst
    print(f"  [DELIVERED] -> {out['brand_path']}", flush=True)
    return out

def render_episode(ep_id):
    cfg = ALL_EPISODES[ep_id]
    out_w, out_h = 1080, 1920
    target_ar = 9.0 / 16.0

    ep_dir = os.path.join(BASE_DIR, ep_id)
    raw_dir = os.path.join(ep_dir, "raw_9x16")
    norm_dir = os.path.join(ep_dir, "norm_9x16")
    os.makedirs(norm_dir, exist_ok=True)

    print(f"\n==================== RENDERING CINEMA {ep_id.upper()} ({len(cfg['shots'])} scenes) — {cfg['title']} ====================", flush=True)
    norm_files = []
    timeline_log = []
    cum_t = 0.0
    lut_ff = LUT_PATH.replace("\\", "/").replace(":", "\\:")

    for idx, (sid, scale, skey, chars, sp, act, speaker, dlg) in enumerate(cfg["shots"], 1):
        src = os.path.join(raw_dir, f"{sid}.mp4")
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing raw clip: {src}")
        w, h, total_dur = probe_video(src)
        is_wide = scale in ("WIDE", "WIDE_CROWD", "MED")

        if speaker and dlg:
            voc_wav = run_demucs_vocals(src, f"{ep_id}_9x16_{sid}")
            info = analyze_vocals_cinema(voc_wav, total_dur, is_wide=is_wide)
            ss, to = info["ss"], info["to"]
        else:
            voc_wav = None
            ss = 0.15
            to = min(total_dur - 0.08, 4.05)

        dur = round(to - ss, 3)

        vf_parts = []
        if w == 720 and h == 1280:
            vf_parts.append("delogo=x=570:y=1130:w=62:h=62")
        top_b, bot_b = detect_letterbox_bars(src, w, h, (ss + to) * 0.5)
        ch_crop = h - top_b - bot_b
        cw_crop, cx_crop, cy_crop = w, 0, top_b
        cur_ar = cw_crop / float(max(1, ch_crop))
        if abs(cur_ar - target_ar) > 0.015:
            if cur_ar > target_ar:
                cw_crop = int(round(ch_crop * target_ar / 2) * 2)
                cx_crop = (w - cw_crop) // 2
            else:
                new_ch = int(round(cw_crop / target_ar / 2) * 2)
                cy_crop = top_b + (ch_crop - new_ch) // 2
                ch_crop = new_ch
        if cw_crop != w or ch_crop != h or cx_crop != 0 or cy_crop != 0:
            vf_parts.append(f"crop={cw_crop}:{ch_crop}:{cx_crop}:{cy_crop}")

        if os.path.exists(LUT_PATH):
            vf_parts.append(f"lut3d=file='{lut_ff}':interp=tetrahedral")
        vf_parts += [
            f"scale={out_w}:{out_h}:flags=lanczos",
            "eq=contrast=1.02:saturation=1.04",
            "unsharp=3:3:0.30:3:3:0.0",
            "fps=30",
            "format=yuv420p",
        ]
        vf = ",".join(vf_parts)

        dst = os.path.join(norm_dir, f"{idx:02d}_{sid}.mp4")
        fo_st = max(0.05, dur - 0.08)
        if voc_wav:
            af = (
                f"highpass=f=85,lowpass=f=13500,"
                f"loudnorm=I=-14.5:TP=-1.2:LRA=7,"
                f"afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.08"
            )
            # Output-side -ss AFTER -i guarantees frame-exact sync between H.264 video and PCM vocals!
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-i", src,
                "-i", voc_wav,
                "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}",
                "-vf", vf, "-af", af, "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", dst
            ], check=True)
        else:
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-i", src,
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}",
                "-vf", vf, "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", dst
            ], check=True)

        _, _, real_d = probe_video(dst)
        timeline_log.append({"scene": sid, "scale": scale, "start": round(cum_t, 2), "end": round(cum_t + real_d, 2), "dur": round(real_d, 2)})
        print(f"  [{idx:02d}_{sid}:{scale}] {cum_t:6.2f}s -> {cum_t + real_d:6.2f}s ({real_d:.2f}s)", flush=True)
        cum_t += real_d
        norm_files.append(dst)

    concat_txt = os.path.join(ep_dir, "concat_9x16.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for nf in norm_files:
            cf.write(f"file '{nf}'\n")

    vo_master = os.path.join(ep_dir, "vo_master_9x16.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", vo_master], check=True)
    _, _, vid_total = probe_video(vo_master)

    pivot_t = vid_total * 0.55
    for item in timeline_log:
        if item["scene"] == cfg["pivot_scene"]:
            pivot_t = item["start"]
            break
    outro_fo = max(1.0, vid_total - 2.2)

    b1_fn, b1_off, b1_vol = cfg["bgm_act1"]
    b2_fn, b2_off, b2_vol = cfg["bgm_act2"]
    b1_path = os.path.join(BGM_DIR, b1_fn)
    b2_path = os.path.join(BGM_DIR, b2_fn)

    b1_len = max(4.0, pivot_t + 1.0)
    b2_start = max(0.0, pivot_t - 0.4)
    b2_delay_ms = int(round(b2_start * 1000))
    b2_len = max(4.0, vid_total - b2_start + 1.0)

    fc_bgm = (
        f"[1:a]atrim={b1_off:.2f}:{b1_off + b1_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume={b1_vol:.2f},afade=t=in:st=0:d=0.6,afade=t=out:st={max(0.5, b1_len - 1.5):.3f}:d=1.5[b1];"
        f"[2:a]atrim={b2_off:.2f}:{b2_off + b2_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume={b2_vol:.2f},afade=t=in:st=0:d=1.2,adelay={b2_delay_ms}|{b2_delay_ms}[b2];"
        f"[b1][b2]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
        f"atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,"
        f"highpass=f=95,lowpass=f=9500,"
        f"equalizer=f=1500:t=q:w=1.2:g=-4.2,equalizer=f=2800:t=q:w=1.2:g=-4.2,"
        f"afade=t=out:st={outro_fo:.3f}:d=2.0[bgm_clean];"
        f"[0:a][bgm_clean]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.93[aout]"
    )

    final_local = os.path.join(ep_dir, f"261123 K4 {cfg['title']} final.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", vo_master,
        "-stream_loop", "-1", "-i", b1_path,
        "-stream_loop", "-1", "-i", b2_path,
        "-filter_complex", fc_bgm, "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "224k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", final_local
    ], check=True)

    # QA Contact Sheet
    cols = 5 if len(norm_files) >= 17 else 4
    tw, th = 216, 384
    thumbs = []
    for i, nf in enumerate(norm_files, 1):
        _, _, d = probe_video(nf)
        t = os.path.join(QC_DIR, f"{ep_id}_s{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{d*0.50:.2f}", "-i", nf, "-vf", f"scale={tw}:{th}", "-frames:v", "1", t], check=True)
        thumbs.append(t)
    rows = (len(thumbs) + cols - 1) // cols
    while len(thumbs) < cols * rows:
        pad_t = os.path.join(QC_DIR, f"{ep_id}_pad{len(thumbs)}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x14161c:s={tw}x{th}", "-frames:v", "1", pad_t], check=True)
        thumbs.append(pad_t)
    inp = []
    for t in thumbs:
        inp += ["-i", t]
    layout = "|".join(f"{(i%cols)*tw}_{(i//cols)*th}" for i in range(len(thumbs)))
    qa_sheet = os.path.join(QC_DIR, f"QA_{ep_id.upper()}_9x16.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs={len(thumbs)}:layout={layout}", "-frames:v", "1", qa_sheet], check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, f"QA_{ep_id.upper()}_9x16.jpg"))

    delivered = deliver_episode(final_local, cfg["title"])
    print(f"=== {ep_id.upper()} MASTER COMPLETE: {vid_total:.2f}s ({len(norm_files)} scenes) ===", flush=True)
    return {
        "episode": ep_id,
        "scenes_count": len(norm_files),
        "duration": round(vid_total, 2),
        "qa_sheet": qa_sheet,
        **delivered,
    }

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "render"
    if mode in ("audit", "render"):
        eps = sys.argv[2:] if len(sys.argv) > 2 else sorted(ALL_EPISODES.keys())
    else:
        eps = sys.argv[1:]
        mode = "render"

    if mode == "audit":
        audit_episodes(eps)
    else:
        out = [render_episode(ep) for ep in eps]
        rep = os.path.join(BASE_DIR, "delivery_10_episodes_report.json")
        existing = json.load(open(rep, encoding="utf-8")) if os.path.exists(rep) else []
        merged = {x["episode"]: x for x in existing}
        for item in out:
            merged[item["episode"]] = item
        json.dump(list(merged.values()), open(rep, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        if os.path.isdir(r"G:\My Drive\AI_Full_Studio\03_Du_An"):
            os.makedirs(DU_AN_CLOUD_DIR, exist_ok=True)
            for qfn in os.listdir(QC_DIR):
                if qfn.startswith("QA_EP"):
                    shutil.copy2(os.path.join(QC_DIR, qfn), os.path.join(DU_AN_CLOUD_DIR, qfn))
        print("RENDER BATCH COMPLETE!", flush=True)
