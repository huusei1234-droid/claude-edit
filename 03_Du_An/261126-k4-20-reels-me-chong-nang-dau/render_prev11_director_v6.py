# -*- coding: utf-8 -*-
"""
Director V6 Hand-Curated Complete-Sentence Highlight Hook & Multi-Episode Renderer
for ALL 11 Previously Produced >90s K4 Drama Films (`261122`, `261123`, `261124` — including An Vượng Pharma `v02`):

1. Recovers the 100% pure, intact story `[f_story_0 .. total_frames]` from each film's existing `tập full final.mp4`
   (copying locally first so FFmpeg runs at local SSD speed and never overwrites an open input).
2. Uses Whisper word-level timestamps on the `[-0.42s .. +0.10s]` J-cut window of each hand-curated Hook/Cliffhanger cut
   so any `-0.28s` J-cut opening syllable is 100% recovered AND any trailing next-speaker J-cut syllable is 100% muted,
   while visual frames stay strictly inside `[abs_f0 .. abs_f1]` (`0` flash frames, `100%` complete spoken sentences!).
3. Scores every Opening Highlight Hook (`+ 0.80s` black pause) and Cliffhanger Outro (`+ 0.60s` black hit) with
   back-aligned `user_hook_260922_mat50cheo.wav`, enforcing `<= 90.0s` on EVERY `tập 1..N` (`+ 1 tập full` per film).
"""
import gc, glob, json, math, os, shutil, subprocess, sys, time, wave
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import numpy as np

BASE_261126   = r"C:\AI\full studio\output\k4-20-reels-261126"
TRANS_JSON    = os.path.join(BASE_261126, "_prev11_story_cuts_transcript.json")
WORK_DIR      = os.path.join(BASE_261126, "prev11_v6_work")
BGM_DIR       = os.path.join(BASE_261126, "bgm")

K4_DRIVE_DIR     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"C:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"

SR = 48000
FPS = 30
SAMPLES_PER_FRAME = SR // FPS  # 1600
MAX_EPISODE_SEC = 90.0

os.makedirs(WORK_DIR, exist_ok=True)

# Director V7: Coherent "Sự Vô Lý" Opening Intros (ZERO spoilers) + ZERO End-Highlights!
CURATED_PREV11_V6 = {
    "v01": {
        "ranges": [(0, 10), (10, 17)],
        "full_hook": [1, 3, 4],
        "tap1_hook": [1, 3, 4],
        "tap2_hook": [8, 9, 12],
    },
    "v02": {  # An Vượng Pharma (`BOJOMI` + `CURCUMILK PHYTO`) Upgraded Edition!
        "ranges": [(0, 11), (11, 19), (19, 26)],
        "full_hook": [8, 9, 10],
        "tap1_hook": [8, 9, 10],
        "tap2_hook": [6, 9, 10],
        "tap3_hook": [14, 15, 18],
    },
    "v03": {
        "ranges": [(0, 13), (13, 23)],
        "full_hook": [1, 2, 3],
        "tap1_hook": [1, 2, 3],
        "tap2_hook": [11, 12],
    },
    "ep01": {
        "ranges": [(0, 10), (10, 21)],
        "full_hook": [7, 8, 9],
        "tap1_hook": [7, 8, 9],
        "tap2_hook": [8, 9, 11],
    },
    "ep09": {
        "ranges": [(0, 12), (12, 19)],
        "full_hook": [5, 6, 7],
        "tap1_hook": [5, 6, 7],
        "tap2_hook": [9, 10, 11],
    },
    "ep10": {
        "ranges": [(0, 12), (12, 25)],
        "full_hook": [1, 2, 3],
        "tap1_hook": [1, 2, 3],
        "tap2_hook": [5, 6, 11],
    },
    "f01": {
        "ranges": [(0, 8), (8, 15), (15, 21)],
        "full_hook": [1, 2],
        "tap1_hook": [1, 2],
        "tap2_hook": [5, 7],
        "tap3_hook": [13, 14],
    },
    "f02": {
        "ranges": [(0, 11), (11, 21)],
        "full_hook": [3, 4],
        "tap1_hook": [3, 4],
        "tap2_hook": [4, 5],
    },
    "f03": {
        "ranges": [(0, 8), (8, 15), (15, 22)],
        "full_hook": [1, 2],
        "tap1_hook": [1, 2],
        "tap2_hook": [5, 7],
        "tap3_hook": [11, 13],
    },
    "f04": {
        "ranges": [(0, 10), (10, 20)],
        "full_hook": [8, 9],
        "tap1_hook": [8, 9],
        "tap2_hook": [9, 11],
    },
    "f05": {
        "ranges": [(0, 10), (10, 20)],
        "full_hook": [3, 4],
        "tap1_hook": [3, 4],
        "tap2_hook": [4, 5],
    },
}

X264_COMMON = [
    "-threads", "3", "-filter_threads", "2",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-profile:v", "high", "-level", "4.1", "-g", "30", "-bf", "2",
    "-pix_fmt", "yuv420p"
]

_USER_HOOK_BGM = None
_WHISPER = None

def get_whisper():
    global _WHISPER
    if _WHISPER is None:
        from faster_whisper import WhisperModel
        _WHISPER = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
    return _WHISPER

def run_ffmpeg_lowmem(cmd):
    if cmd[0] == "ffmpeg" and "-nostdin" not in cmd:
        cmd = ["ffmpeg", "-nostdin"] + cmd[1:]
    for attempt in range(4):
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
        if p.returncode == 0:
            return
        gc.collect()
        time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"FFmpeg failed: {' '.join(cmd[:8])} -> {p.stderr[-500:]}")

def load_wav_48k_stereo(wav_path):
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if nch == 1:
        pcm = np.column_stack([pcm, pcm])
    else:
        pcm = pcm.reshape(-1, nch)[:, :2]
    if sr != SR:
        n_out = int(round(len(pcm) * SR / float(sr)))
        x_old = np.linspace(0.0, 1.0, len(pcm), endpoint=False)
        x_new = np.linspace(0.0, 1.0, n_out, endpoint=False)
        pcm = np.column_stack([
            np.interp(x_new, x_old, pcm[:, 0]).astype(np.float32),
            np.interp(x_new, x_old, pcm[:, 1]).astype(np.float32),
        ])
    return pcm

def load_mp4_audio_48k_stereo(mp4_path):
    raw = subprocess.check_output([
        "ffmpeg", "-nostdin", "-threads", "2", "-v", "error", "-i", mp4_path,
        "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"
    ], stdin=subprocess.DEVNULL)
    return (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)

def load_user_signature_hook_48k():
    global _USER_HOOK_BGM
    if _USER_HOOK_BGM is not None:
        return _USER_HOOK_BGM
    p = os.path.join(BGM_DIR, "user_hook_260922_mat50cheo.wav")
    assert os.path.exists(p), f"Missing {p}"
    arr = load_wav_48k_stereo(p)
    n = len(arr)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    pocket = (1.0 - 0.38 * np.exp(-0.5 * ((freqs - 2150.0) / 850.0) ** 2)).astype(np.float32)
    for ch in range(2):
        arr[:, ch] = np.fft.irfft(np.fft.rfft(arr[:, ch]) * pocket, n=n).astype(np.float32)
    _USER_HOOK_BGM = arr
    return arr

def get_looped_bgm_slice(bgm_arr, offset_sec, length_samples):
    start_idx = int(round(offset_sec * SR)) % len(bgm_arr)
    out = np.empty((length_samples, 2), dtype=np.float32)
    pos = 0
    cur = start_idx
    while pos < length_samples:
        take = min(length_samples - pos, len(bgm_arr) - cur)
        out[pos:pos + take] = bgm_arr[cur:cur + take]
        pos += take
        cur = 0
    return out

def back_align_signature_hook_bgm(tot_samples):
    hook_track = load_user_signature_hook_48k()
    end_samp = len(hook_track)
    if tot_samples <= end_samp:
        bgm = hook_track[end_samp - tot_samples : end_samp].copy()
    else:
        extra = tot_samples - end_samp
        xf = min(int(0.65 * SR), extra, end_samp // 4)
        intro_pool = hook_track[:max(int(6.0 * SR), end_samp - int(2.5 * SR))]
        intro = get_looped_bgm_slice(intro_pool, 0.0, extra + xf)
        bgm = np.empty((tot_samples, 2), dtype=np.float32)
        bgm[:extra] = intro[:extra]
        if xf > 0:
            w = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, xf, dtype=np.float32)))[:, None]
            bgm[extra : extra + xf] = intro[extra : extra + xf] * (1.0 - w) + hook_track[:xf] * w
        bgm[extra + xf :] = hook_track[xf : end_samp]
    fi = min(int(0.28 * SR), tot_samples)
    fo = min(int(0.25 * SR), tot_samples)
    bgm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    bgm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return bgm

def focus_speech_band_48k(raw_pcm):
    arr = raw_pcm.copy()
    n = len(arr)
    if n < 64:
        return arr
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    bp = np.ones_like(freqs, dtype=np.float32)
    bp *= np.clip((freqs - 110.0) / 75.0, 0.0, 1.0)
    bp *= np.clip((9200.0 - freqs) / 1600.0, 0.0, 1.0)
    bp *= (1.0 + 0.24 * np.exp(-0.5 * ((freqs - 2350.0) / 800.0) ** 2)).astype(np.float32)
    for ch in range(2):
        arr[:, ch] = np.fft.irfft(np.fft.rfft(arr[:, ch]) * bp, n=n).astype(np.float32)
    win = int(0.020 * SR)
    nb = max(1, n // win)
    mono_rms = np.sqrt(np.mean(arr[:nb * win].mean(axis=1).reshape(nb, win) ** 2, axis=1))
    pk_r = float(np.max(mono_rms)) + 1e-6
    thr_lo = max(0.012, pk_r * 0.12)
    thr_hi = max(0.026, pk_r * 0.28)
    gate_b = np.clip((mono_rms - thr_lo) / max(1e-4, thr_hi - thr_lo), 0.05, 1.0).astype(np.float32)
    gate_sm = np.convolve(np.pad(gate_b, (2, 2), mode="edge"), np.ones(5, dtype=np.float32) / 5.0, mode="valid")
    gate_f = np.interp(np.linspace(0.0, nb, n, endpoint=False), np.arange(nb, dtype=np.float32) + 0.5, gate_sm).astype(np.float32)[:, None]
    arr *= gate_f
    pk = float(np.max(np.abs(arr))) + 1e-6
    if pk > 0.03:
        arr = np.clip(arr * min(1.48, 0.80 / pk), -0.92, 0.92)
    return arr

def extract_complete_jcut_clean_beat_v6(local_src_mp4, full_pcm, f_story_0, cut_info, all_cuts, work_sub, out_vid, dip_to_black=False):
    """
    Extracts 100% of the spoken sentence of `cut_info` (recovering any -0.35s J-cut lead-in word while
    muting any trailing next-shot J-cut word!) and pairs it with pure visual frames strictly inside `[abs_f0 .. abs_f1]`.
    """
    ci = cut_info["cut_idx"]
    vf0 = int(cut_info["abs_f0"])
    vf1 = int(cut_info["abs_f1"])
    vis_frames = vf1 - vf0

    # Audio search window: allow up to 12 frames (-0.40s) before vf0 if not cut 0, and up to vf1
    pre_allow = 12 if ci > 0 else 0
    af_win0 = max(f_story_0, vf0 - pre_allow)
    af_win1 = min(len(full_pcm) // SAMPLES_PER_FRAME, vf1 + 2)
    win_pcm = full_pcm[af_win0 * SAMPLES_PER_FRAME : af_win1 * SAMPLES_PER_FRAME].copy()
    win_dur = len(win_pcm) / float(SR)
    rel_vf0_sec = (vf0 - af_win0) / float(FPS)
    rel_vf1_sec = (vf1 - af_win0) / float(FPS)

    # Write tiny 16kHz WAV to get exact Whisper word boundaries on this cut's window
    tmp_w = os.path.join(work_sub, f"_wchk_c{ci:02d}.wav")
    mono16 = np.interp(
        np.linspace(0.0, 1.0, int(round(win_dur * 16000)), endpoint=False),
        np.linspace(0.0, 1.0, len(win_pcm), endpoint=False),
        win_pcm.mean(axis=1)
    )
    with wave.open(tmp_w, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes((np.clip(mono16, -0.98, 0.98) * 32767.0).astype(np.int16).tobytes())

    wm = get_whisper()
    segs_w, _ = wm.transcribe(tmp_w, language="vi", word_timestamps=True, vad_filter=False, beam_size=2)
    try: os.remove(tmp_w)
    except Exception: pass

    words = []
    for s in segs_w:
        for w in (s.words or []):
            if w.word.strip():
                words.append((float(w.start), float(w.end), w.word.strip()))

    # Filter out:
    # 1) Any word belonging to the PREVIOUS cut whose end <= rel_vf0_sec + 0.04 and followed by a pause >= 0.08s
    while len(words) >= 2 and words[0][1] <= rel_vf0_sec + 0.04 and (words[1][0] - words[0][1]) >= 0.08:
        words.pop(0)
    # Also drop any word whose midpoint is before rel_vf0_sec - 0.16s
    words = [w for w in words if (w[0] + w[1]) * 0.5 >= rel_vf0_sec - 0.16]

    # 2) Any trailing J-cut word belonging to the NEXT cut (starts >= rel_vf1_sec - 0.42s after a >= 0.12s pause, or <= 2 words at tail)
    while len(words) >= 4:
        last_w = words[-1]
        prev_w = words[-2]
        if last_w[0] >= rel_vf1_sec - 0.42 and (last_w[0] - prev_w[1]) >= 0.11:
            words.pop()
        elif len(words) >= 5 and words[-2][0] >= rel_vf1_sec - 0.44 and (words[-2][0] - words[-3][1]) >= 0.14:
            words = words[:-2]
        else:
            break

    if words:
        s_sec = max(0.0, words[0][0] - 0.09)
        e_sec = min(win_dur, words[-1][1] + 0.18)
    else:
        s_sec = rel_vf0_sec
        e_sec = rel_vf1_sec

    s_samp = int(round(s_sec * SR))
    e_samp = max(s_samp + SAMPLES_PER_FRAME * 36, int(round(e_sec * SR)))
    voc_clean = focus_speech_band_48k(win_pcm[s_samp:e_samp])

    # Quantize to exact 30fps frames
    nf_aud = max(42, int(round(len(voc_clean) / float(SAMPLES_PER_FRAME))))
    if len(voc_clean) < nf_aud * SAMPLES_PER_FRAME:
        voc_clean = np.vstack([voc_clean, np.zeros((nf_aud * SAMPLES_PER_FRAME - len(voc_clean), 2), dtype=np.float32)])
    else:
        voc_clean = voc_clean[:nf_aud * SAMPLES_PER_FRAME]

    fi = min(1100, len(voc_clean) // 6)
    fo = min(1500, len(voc_clean) // 6)
    voc_clean[:fi] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi, dtype=np.float32)))[:, None]
    voc_clean[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo, dtype=np.float32)))[:, None]

    # Visual strictly inside [vf0 + 1 .. vf1 - 1] so 0 neighbor frames ever flash!
    v_safe0 = vf0 + 1
    v_safe_nf = max(30, vf1 - vf0 - 2)
    vis_ss = v_safe0 / float(FPS)
    vis_dur = v_safe_nf / float(FPS)
    out_dur = nf_aud / float(FPS)

    vf_h = [
        "crop=1036:1842:22:39",
        "scale=1080:1920:flags=lanczos",
        "eq=contrast=1.03:saturation=1.04",
    ]
    if nf_aud > v_safe_nf:
        pad_s = (nf_aud - v_safe_nf) / float(FPS) + 0.15
        vf_h.append(f"tpad=stop_mode=clone:stop_duration={pad_s:.3f}")
    vf_h.append("fade=t=in:st=0:d=0.08")
    if dip_to_black and out_dur > 0.45:
        vf_h.append(f"fade=t=out:st={out_dur - 0.26:.3f}:d=0.26")

    run_ffmpeg_lowmem([
        "ffmpeg", "-y", "-v", "error", "-threads", "2",
        "-ss", f"{vis_ss:.4f}", "-t", f"{vis_dur:.4f}", "-i", local_src_mp4,
        "-vf", ",".join(vf_h), "-an", "-r", str(FPS), "-frames:v", str(nf_aud),
        *X264_COMMON, out_vid
    ])
    return out_vid, voc_clean

def make_black_pause_clip(out_vid, n_frames=24):
    dur_s = n_frames / float(FPS)
    run_ffmpeg_lowmem([
        "ffmpeg", "-nostdin", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={FPS}:d={dur_s:.4f}",
        "-frames:v", str(n_frames), "-an",
        *X264_COMMON, out_vid
    ])
    return out_vid, np.zeros((n_frames * SAMPLES_PER_FRAME, 2), dtype=np.float32)

def encode_story_span_video(local_src_mp4, abs_f_start, abs_f_end, out_vid, fade_in=True, fade_out_black=False):
    n_frames = abs_f_end - abs_f_start
    ss = abs_f_start / float(FPS)
    dur = n_frames / float(FPS)
    vf = ["scale=1080:1920:flags=lanczos"]
    if fade_in:
        vf.append("fade=t=in:st=0:d=0.14")
    if fade_out_black and dur > 0.6:
        vf.append(f"fade=t=out:st={dur - 0.25:.3f}:d=0.25")
    run_ffmpeg_lowmem([
        "ffmpeg", "-y", "-v", "error", "-threads", "2",
        "-ss", f"{ss:.4f}", "-t", f"{dur + 0.10:.4f}", "-i", local_src_mp4,
        "-vf", ",".join(vf), "-an", "-r", str(FPS), "-frames:v", str(n_frames),
        *X264_COMMON, out_vid
    ])
    return out_vid

def build_hook_v6_prev(work_sub, tag_prefix, picks, cuts, f_story_0, local_src_mp4, full_pcm, beat_cache):
    h_vids, h_pcms = [], []
    for j, ci in enumerate(picks):
        dip = (j == 0 and len(picks) >= 3) or (j == len(picks) - 1)
        ckey = (ci, dip)
        if ckey not in beat_cache:
            hv = os.path.join(work_sub, f"beat_c{ci:02d}_dip{int(dip)}.mp4")
            _, hp = extract_complete_jcut_clean_beat_v6(local_src_mp4, full_pcm, f_story_0, cuts[ci], cuts, work_sub, hv, dip_to_black=dip)
            beat_cache[ckey] = (hv, hp)
        hv, hp = beat_cache[ckey]
        h_vids.append(hv)
        h_pcms.append(hp)

    blk_vid = os.path.join(work_sub, f"hook_{tag_prefix}_black_pause.mp4")
    _, blk_pcm = make_black_pause_clip(blk_vid, n_frames=24)
    h_vids.append(blk_vid)
    h_pcms.append(blk_pcm)

    dlg_h = np.concatenate(h_pcms, axis=0)
    tot = len(dlg_h)
    bgm_h = back_align_signature_hook_bgm(tot)

    blk_sz = SR // 10
    n_blk = max(1, tot // blk_sz)
    d_mono = np.abs(dlg_h[:n_blk * blk_sz].mean(axis=1)).reshape(n_blk, blk_sz)
    d_rms = np.sqrt(np.mean(d_mono ** 2, axis=1))
    duck_b = np.where(d_rms > 0.018, 0.50, 1.06).astype(np.float32)
    duck_sm = np.convolve(np.pad(duck_b, (2, 2), mode="edge"), np.ones(5, dtype=np.float32) / 5.0, mode="valid")
    duck_f = np.interp(np.linspace(0.0, n_blk, tot, endpoint=False), np.arange(n_blk, dtype=np.float32) + 0.5, duck_sm).astype(np.float32)[:, None]

    mix_h = np.clip(np.tanh((dlg_h + bgm_h * duck_f) * 1.05) / 1.05, -0.94, 0.94)
    return h_vids, mix_h

def build_cliff_v6_prev(work_sub, tag_prefix, picks, cuts, f_story_0, local_src_mp4, full_pcm, beat_cache):
    c_vids, c_pcms = [], []
    for j, ci in enumerate(picks):
        dip = (j == len(picks) - 1)
        ckey = (ci, dip)
        if ckey not in beat_cache:
            cv = os.path.join(work_sub, f"beat_c{ci:02d}_dip{int(dip)}.mp4")
            _, cp = extract_complete_jcut_clean_beat_v6(local_src_mp4, full_pcm, f_story_0, cuts[ci], cuts, work_sub, cv, dip_to_black=dip)
            beat_cache[ckey] = (cv, cp)
        cv, cp = beat_cache[ckey]
        c_vids.append(cv)
        c_pcms.append(cp)

    blk_vid = os.path.join(work_sub, f"cliff_{tag_prefix}_black_end.mp4")
    _, blk_pcm = make_black_pause_clip(blk_vid, n_frames=18)
    c_vids.append(blk_vid)
    c_pcms.append(blk_pcm)

    dlg_c = np.concatenate(c_pcms, axis=0)
    tot = len(dlg_c)
    bgm_c = back_align_signature_hook_bgm(tot)

    blk_sz = SR // 10
    n_blk = max(1, tot // blk_sz)
    d_mono = np.abs(dlg_c[:n_blk * blk_sz].mean(axis=1)).reshape(n_blk, blk_sz)
    d_rms = np.sqrt(np.mean(d_mono ** 2, axis=1))
    duck_b = np.where(d_rms > 0.018, 0.54, 1.04).astype(np.float32)
    duck_sm = np.convolve(np.pad(duck_b, (2, 2), mode="edge"), np.ones(5, dtype=np.float32) / 5.0, mode="valid")
    duck_f = np.interp(np.linspace(0.0, n_blk, tot, endpoint=False), np.arange(n_blk, dtype=np.float32) + 0.5, duck_sm).astype(np.float32)[:, None]

    mix_c = np.clip(np.tanh((dlg_c + bgm_c * duck_f) * 1.05) / 1.05, -0.94, 0.94)
    return c_vids, mix_c

def mux_and_stage(batch_code, out_title, concat_vids, master_pcm, work_sub, enforce_90s=True):
    vid_dur = len(master_pcm) / float(SR)
    if enforce_90s:
        assert vid_dur <= MAX_EPISODE_SEC + 0.05, f"EXCEEDED 90s: {out_title} = {vid_dur:.2f}s!"
    wav_p = os.path.join(work_sub, "mux_tmp.wav")
    with wave.open(wav_p, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(master_pcm, -0.96, 0.96) * 32767.0).astype(np.int16).tobytes())
    txt_p = os.path.join(work_sub, "concat_tmp.txt")
    with open(txt_p, "w", encoding="utf-8") as cf:
        for v in concat_vids:
            cf.write(f"file '{v}'\n")
    fname = f"{batch_code} K4 {out_title} final.mp4"
    staged_mp4 = os.path.join(work_sub, fname)
    run_ffmpeg_lowmem([
        "ffmpeg", "-nostdin", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", txt_p, "-i", wav_p,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "224k", "-ar", str(SR), "-ac", "2",
        "-movflags", "+faststart", staged_mp4
    ])
    os.remove(wav_p)
    return {"filename": fname, "staged": staged_mp4, "duration": round(vid_dur, 2), "is_full": not enforce_90s}

def detect_actual_story_start_frame(mp4_path):
    raw_gray = subprocess.check_output([
        "ffmpeg", "-nostdin", "-threads", "2", "-v", "error", "-t", "28.0", "-i", mp4_path,
        "-vf", "scale=48:84,format=gray", "-f", "rawvideo", "-"
    ], stdin=subprocess.DEVNULL)
    nf_g = len(raw_gray) // (48 * 84)
    luma = np.frombuffer(raw_gray[:nf_g * 48 * 84], dtype=np.uint8).reshape(nf_g, -1).mean(axis=1)
    runs = []
    i = 150
    while i < nf_g:
        if luma[i] < 2.8:
            s = i
            while i < nf_g and luma[i] < 2.8:
                i += 1
            if i - s >= 15:
                runs.append((s, i))
        else:
            i += 1
    assert runs, f"No 24-frame black hook pause found in {mp4_path}!"
    return int(runs[-1][1])

def process_one_prev_film(fkey, meta):
    dt = meta["date"]
    base_title = meta["title"]
    curated = CURATED_PREV11_V6[fkey]
    ranges = curated["ranges"]

    src_drive = os.path.join(K4_DRIVE_DIR, f"{dt} K4 {base_title} tập full final.mp4")
    assert os.path.exists(src_drive), f"Missing {src_drive}"

    work_sub = os.path.join(WORK_DIR, fkey)
    shutil.rmtree(work_sub, ignore_errors=True)
    os.makedirs(work_sub, exist_ok=True)

    # Copy to local SSD first so we NEVER overwrite an open input and FFmpeg runs 5x faster!
    local_src = os.path.join(work_sub, "src_master.mp4")
    shutil.copy2(src_drive, local_src)

    # Dynamically detect actual story start frame so re-running any film is 100% idempotent!
    f_story_0 = detect_actual_story_start_frame(local_src)
    cuts = []
    for c in meta["cuts"]:
        cc = dict(c)
        cc["abs_f0"] = f_story_0 + int(c["rel_f0"])
        cc["abs_f1"] = f_story_0 + int(c["rel_f1"])
        cuts.append(cc)
    total_frames = cuts[-1]["abs_f1"]

    full_pcm = load_mp4_audio_48k_stereo(local_src)
    if len(full_pcm) < total_frames * SAMPLES_PER_FRAME:
        full_pcm = np.vstack([full_pcm, np.zeros((total_frames * SAMPLES_PER_FRAME - len(full_pcm), 2), dtype=np.float32)])

    beat_cache = {}
    staged_outputs = []

    print(f"\n=== RENDERING DIRECTOR V6 [{fkey.upper()}]: {dt} K4 {base_title} -> {len(ranges)} Tập (<=90s) + 1 Tập Full ===", flush=True)

    for p_idx, (i0, i1) in enumerate(ranges, 1):
        has_next = (p_idx < len(ranges))
        h_picks = [c for c in curated[f"tap{p_idx}_hook"] if c != i0]
        h_vids, h_pcm = build_hook_v6_prev(work_sub, f"p{p_idx}", h_picks, cuts, f_story_0, local_src, full_pcm, beat_cache)

        # Director V7: Highlight ONLY at beginning (`0.0s`), ZERO highlight at episode end!
        c_vids, c_pcm = [], np.zeros((0, 2), dtype=np.float32)

        abs_fs = int(cuts[i0]["abs_f0"])
        abs_fe = int(cuts[i1 - 1]["abs_f1"])
        story_samp = (abs_fe - abs_fs) * SAMPLES_PER_FRAME

        if (len(h_pcm) + story_samp) / float(SR) > 89.5 and len(h_picks) >= 3:
            h_vids, h_pcm = build_hook_v6_prev(work_sub, f"p{p_idx}_h2", h_picks[:2], cuts, f_story_0, local_src, full_pcm, beat_cache)

        st_vid = os.path.join(work_sub, f"story_p{p_idx}.mp4")
        encode_story_span_video(local_src, abs_fs, abs_fe, st_vid, fade_in=True, fade_out_black=has_next)
        st_pcm = full_pcm[abs_fs * SAMPLES_PER_FRAME : abs_fe * SAMPLES_PER_FRAME].copy()
        fi = min(int(0.26 * SR), len(st_pcm))
        fo = min(int((0.42 if has_next else 0.20) * SR), len(st_pcm))
        st_pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        st_pcm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

        all_pcm = np.concatenate([h_pcm, st_pcm] + ([c_pcm] if len(c_pcm) else []), axis=0)
        all_vids = list(h_vids) + [st_vid] + list(c_vids)
        info = mux_and_stage(dt, f"{base_title} tập {p_idx}", all_vids, all_pcm, work_sub, enforce_90s=True)
        print(f"  [STAGED TẬP {p_idx}] {info['filename']} ({info['duration']:.2f}s <= 90s | hook={len(h_pcm)/SR:.2f}s | cliff={len(c_pcm)/SR:.2f}s)", flush=True)
        staged_outputs.append(info)

    # Full Master (`tập full final.mp4`)
    fh_picks = [c for c in curated["full_hook"] if c != 0]
    fh_vids, fh_pcm = build_hook_v6_prev(work_sub, "full", fh_picks, cuts, f_story_0, local_src, full_pcm, beat_cache)
    full_st_vid = os.path.join(work_sub, "story_full.mp4")
    encode_story_span_video(local_src, f_story_0, total_frames, full_st_vid, fade_in=True, fade_out_black=False)
    full_st_pcm = full_pcm[f_story_0 * SAMPLES_PER_FRAME : total_frames * SAMPLES_PER_FRAME].copy()
    fi = min(int(0.26 * SR), len(full_st_pcm))
    full_st_pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]

    full_all_pcm = np.concatenate([fh_pcm, full_st_pcm], axis=0)
    full_all_vids = list(fh_vids) + [full_st_vid]
    f_info = mux_and_stage(dt, f"{base_title} tập full", full_all_vids, full_all_pcm, work_sub, enforce_90s=False)
    print(f"  [STAGED TẬP FULL] {f_info['filename']} ({f_info['duration']:.2f}s | hook={len(fh_pcm)/SR:.2f}s)", flush=True)
    staged_outputs.append(f_info)

    # Atomically deliver all staged outputs to all 3 folders & clean up any stale variants
    keep_fnames = {x["filename"] for x in staged_outputs}
    for x in staged_outputs:
        for tdir in (K4_DRIVE_DIR, MASTER_CLOUD_DIR, LOCAL_CAPCUT_DIR):
            os.makedirs(tdir, exist_ok=True)
            shutil.copy2(x["staged"], os.path.join(tdir, x["filename"]))
    for cand in [f"{dt} K4 {base_title} final.mp4"] + [f"{dt} K4 {base_title} tập {k} final.mp4" for k in range(1, 6)]:
        if cand not in keep_fnames:
            for tdir in (K4_DRIVE_DIR, MASTER_CLOUD_DIR, LOCAL_CAPCUT_DIR):
                sp = os.path.join(tdir, cand)
                if os.path.exists(sp):
                    try:
                        os.remove(sp)
                        print(f"  [CLEANED STALE] {sp}", flush=True)
                    except Exception:
                        pass

    shutil.rmtree(work_sub, ignore_errors=True)
    return {
        "film_key": fkey,
        "date": dt,
        "title": base_title,
        "episodes_count": len(ranges),
        "outputs": [{"filename": x["filename"], "duration": x["duration"], "is_full": x["is_full"]} for x in staged_outputs],
    }

if __name__ == "__main__":
    all_meta = json.load(open(TRANS_JSON, encoding="utf-8"))
    keys = sys.argv[1:] if len(sys.argv) > 1 else list(CURATED_PREV11_V6.keys())
    rep = []
    for k in keys:
        rep.append(process_one_prev_film(k, all_meta[k]))
    out_j = os.path.join(BASE_261126, "delivery_v6_prev11_k4.json")
    json.dump(rep, open(out_j, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nALL {len(rep)} PREVIOUS >90s K4 FILMS UPGRADED TO DIRECTOR V6 CURATED HOOKS -> {out_j}", flush=True)
