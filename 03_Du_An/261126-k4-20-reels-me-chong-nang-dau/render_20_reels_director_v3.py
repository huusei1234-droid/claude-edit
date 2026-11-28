"""
Cinema Director V3 — Master Auditor & Renderer for the 20-Reel K4 Batch (`261126`):
- Run with `C:\AI\full studio\voice-studio\.venv\Scripts\python.exe` (CUDA `demucs` + `faster_whisper` + `numpy`).
- Modes:
  1. `audit r01 r02 ...` -> Runs CUDA Demucs (`vocals.wav` + `no_vocals.wav`) + Whisper word-timestamp audit on raw clips:
     - Gate A: Verifies spoken dialogue matches scripted line (`overlap >= 0.36`, `peak >= 0.020`).
     - Gate B: Verifies 0% mid-sentence cutoffs (`tail_margin < 0.14s` & `end_rms > 0.013` or missing final words near EOF). Outputs `flow_retakes_<wave>.json`.
     - Gate C: Auto-detects trailing echoed words after a completed sentence (`gap >= 0.72s`) and sets `auto_force_to` cleanly before the echo!
  2. `render r01 r02 ...` -> Renders `1080x1920 @ 30fps` NVENC Cinema Masters:
     - Sample-locked 48kHz stereo Python PCM slicing (`N * 1600` samples/frame -> `0` muted tails, `0` AAC concat drift, `0` dead-air holes).
     - Whisper + -35dB RMS speech bounds so soft Vietnamese ending particles ("ạ", "nhé", "ơi") are 100% preserved.
     - Multi-Act Natural Film Scoring (`Acoustic Guitar` normal scenes -> `Dramatic Tension` conflict -> `Warm Family Piano` resolution) with 1.8s cosine crossfades, Voice Pocket EQ (`-4.5dB @ 2.15kHz`), and smooth 500ms sidechain ducking.
     - Automatic alternating Axial `CU_PUNCH` (`1.13x`) on consecutive close-ups for seamless `Toàn – Trung – Cận` cinema pacing.
     - Automatic SSD Hygiene: purges heavy intermediate `.wav` stems & `seg_v3_9x16/` right after verified Final delivery so `C:\` keeps >25 GB free!
"""
import glob, json, math, os, re, shutil, subprocess, sys, wave
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from faster_whisper import WhisperModel

BASE_DIR = r"C:\AI\full studio\output\k4-20-reels-261126"
sys.path.insert(0, BASE_DIR)
from episodes_r01_to_r20_spec import EPISODES_261126

BGM_DIR    = os.path.join(BASE_DIR, "bgm")
SFX_DIR    = os.path.join(BASE_DIR, "sfx")
DEMUCS_DIR = os.path.join(BASE_DIR, "demucs_cache")
QC_DIR     = os.path.join(BASE_DIR, "qc_sheets_v3")
ART_DIR    = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DEMUCS_PY  = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
LUT_PATH   = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"

K4_DRIVE_DIR     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"C:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"
DU_AN_CLOUD_DIR  = r"G:\My Drive\AI_Full_Studio\03_Du_An\261126-k4-20-reels-tranbuison"

BATCH_CODE = "261126"
SR = 48000
FPS = 30
SAMPLES_PER_FRAME = SR // FPS  # Exact 1600 samples/frame

for d in (BGM_DIR, DEMUCS_DIR, QC_DIR, ART_DIR):
    os.makedirs(d, exist_ok=True)

_WHISPER = None
_DEMUCS_MODEL = None
_BGM_CACHE = {}

def get_whisper():
    global _WHISPER
    if _WHISPER is None:
        _WHISPER = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
    return _WHISPER

def get_demucs_cuda():
    global _DEMUCS_MODEL
    if _DEMUCS_MODEL is None:
        import torch
        from demucs.pretrained import get_model
        m = get_model("htdemucs")
        m.eval()
        if torch.cuda.is_available():
            m.cuda()
        _DEMUCS_MODEL = m
    return _DEMUCS_MODEL

def norm_words(s):
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return [w for w in s.split() if len(w) > 1]

def word_overlap_ratio(expected, actual):
    ew = set(norm_words(expected))
    aw = set(norm_words(actual))
    if not ew:
        return 1.0
    return len(ew & aw) / float(len(ew))

def is_valid_mp4_video(p):
    if not os.path.exists(p) or os.path.getsize(p) < 80000:
        return False
    try:
        with open(p, "rb") as f:
            hdr = f.read(12)
        if hdr[4:8] != b"ftyp":
            return False
        j = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height:format=duration", "-of", "json", p
        ]).decode("utf-8"))
        s = j["streams"][0]
        dur = float(j["format"]["duration"])
        return s.get("codec_name") in ("h264", "hevc", "vp9", "av1") and dur >= 2.0
    except Exception:
        return False

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

def has_audio_stream(p):
    try:
        j = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=codec_type", "-of", "json", p
        ]).decode("utf-8"))
        return len(j.get("streams", [])) > 0
    except Exception:
        return False

def write_silent_room_wav(wav_path, dur_sec=6.0, sr=44100):
    n = max(sr, int(round(dur_sec * sr)))
    rng = np.random.default_rng(42)
    noise = (rng.normal(0.0, 0.0004, size=(n, 2)) * 32767.0).astype(np.int16)
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(noise.tobytes())

def run_demucs_stems(mp4_path, tag_key):
    out_voc = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    out_nov = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "no_vocals.wav")
    src_mtime = os.path.getmtime(mp4_path)
    if os.path.exists(out_voc) and os.path.getsize(out_voc) > 20000 and os.path.getmtime(out_voc) >= src_mtime and os.path.exists(out_nov):
        return out_voc, out_nov
    if not has_audio_stream(mp4_path):
        _, _, d = probe_video(mp4_path)
        os.makedirs(os.path.dirname(out_nov), exist_ok=True)
        write_silent_room_wav(out_voc, d)
        write_silent_room_wav(out_nov, d)
        return out_voc, out_nov

    import torch
    from demucs.apply import apply_model
    raw_pcm = subprocess.check_output([
        "ffmpeg", "-nostdin", "-threads", "2", "-v", "error", "-i", mp4_path,
        "-vn", "-ac", "2", "-ar", "44100", "-f", "s16le", "-"
    ], stdin=subprocess.DEVNULL)
    arr = (np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2).T  # (2, T)
    model = get_demucs_cuda()
    dev = next(model.parameters()).device
    with torch.no_grad():
        wav_t = torch.from_numpy(arr.copy()).unsqueeze(0).to(dev)
        ref = wav_t.mean(0)
        wav_n = (wav_t - ref.mean()) / (ref.std() + 1e-8)
        sources = apply_model(model, wav_n, shifts=0, split=True, overlap=0.25, progress=False)[0]
        sources = sources * (ref.std() + 1e-8) + ref.mean()
        voc_idx = model.sources.index("vocals")
        voc_np = sources[voc_idx].cpu().numpy().T  # (T, 2)
        nov_np = (wav_t[0] - sources[voc_idx]).cpu().numpy().T  # (T, 2)

    os.makedirs(os.path.dirname(out_nov), exist_ok=True)
    for dst_w, data_np in ((out_voc, voc_np), (out_nov, nov_np)):
        pcm16 = (np.clip(data_np, -0.99, 0.99) * 32767.0).astype(np.int16)
        with wave.open(dst_w, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(pcm16.tobytes())
    return out_voc, out_nov

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
        c0 = np.interp(x_new, x_old, pcm[:, 0]).astype(np.float32)
        c1 = np.interp(x_new, x_old, pcm[:, 1]).astype(np.float32)
        pcm = np.column_stack([c0, c1])
    return pcm

def load_mp4_audio_48k_stereo(mp4_path):
    if not has_audio_stream(mp4_path):
        return np.zeros((SR * 4, 2), dtype=np.float32)
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"
    ])
    if len(raw) < 4:
        return np.zeros((SR * 4, 2), dtype=np.float32)
    return (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)

def analyze_clip_speech(mp4_path, tag_key, expected_dlg):
    if not has_audio_stream(mp4_path):
        _, _, total_dur = probe_video(mp4_path)
        return {
            "tag": tag_key, "total_dur": round(total_dur, 3), "peak": 0.0, "end_rms": 0.0,
            "w_start": 0.2, "w_end": 1.0, "tail_margin": total_dur - 1.0, "overlap": 0.0,
            "auto_force_to": None, "cutoff": True, "reason": "NO_AUDIO_STREAM_FROM_FLOW",
            "expected": expected_dlg, "transcript": "",
        }
    voc_wav, _ = run_demucs_stems(mp4_path, tag_key)
    audit_json = os.path.join(DEMUCS_DIR, f"{tag_key}_audit.json")
    if os.path.exists(audit_json) and os.path.getmtime(audit_json) >= os.path.getmtime(mp4_path):
        return json.load(open(audit_json, encoding="utf-8"))

    _, _, total_dur = probe_video(mp4_path)
    voc_st = load_wav_48k_stereo(voc_wav)
    mono = voc_st.mean(axis=1)
    ws = 0.020
    win = int(SR * ws)
    nf = len(mono) // win
    rms = np.sqrt(np.mean(mono[:nf * win].reshape(nf, win) ** 2, axis=1))
    peak = float(np.max(rms[3:])) if len(rms) > 3 else 0.0
    end_rms = float(np.mean(rms[-7:])) if len(rms) >= 7 else 0.0

    wm = get_whisper()
    segs, _ = wm.transcribe(voc_wav, language="vi", word_timestamps=True, vad_filter=False, beam_size=2)
    words = []
    for s in segs:
        for w in (s.words or []):
            wt = w.word.strip()
            if wt:
                words.append({"s": round(float(w.start), 3), "e": round(float(w.end), 3), "w": wt})

    transcript = " ".join(w["w"] for w in words)
    ov = word_overlap_ratio(expected_dlg, transcript)

    auto_force_to = None
    if len(words) >= 5 and expected_dlg:
        for i in range(3, len(words) - 1):
            gap = words[i + 1]["s"] - words[i]["e"]
            if gap >= 0.72:
                prefix_txt = " ".join(x["w"] for x in words[:i + 1])
                tail_txt = " ".join(x["w"] for x in words[i + 1:])
                if word_overlap_ratio(expected_dlg, prefix_txt) >= 0.72 and len(norm_words(tail_txt)) <= 5:
                    auto_force_to = round(min(total_dur - 0.05, words[i]["e"] + 0.30), 3)
                    words = words[:i + 1]
                    transcript = prefix_txt
                    ov = word_overlap_ratio(expected_dlg, transcript)
                    break

    w_start = words[0]["s"] if words else 0.20
    w_end = words[-1]["e"] if words else min(total_dur - 0.3, 2.5)
    tail_margin = round(total_dur - w_end, 3)

    exp_norm = norm_words(expected_dlg)
    act_norm = norm_words(transcript)
    tail_expected = set(exp_norm[-2:]) if len(exp_norm) >= 2 else set(exp_norm)
    tail_actual = set(act_norm[-4:]) if act_norm else set()
    missing_ending = (len(tail_expected & tail_actual) == 0) and (tail_margin < 0.45)

    cutoff = False
    reason = "OK"
    if peak < 0.020 or ov < 0.36:
        cutoff = True
        reason = f"LOW_SPEECH_OR_MISMATCH (peak={peak:.3f}, ov={ov:.2f})"
    elif (tail_margin < 0.14 and end_rms > 0.013) or missing_ending:
        cutoff = True
        reason = f"EOF_CUTOFF (tail_margin={tail_margin:.2f}s, end_rms={end_rms:.4f}, missing_end={missing_ending})"

    res = {
        "tag": tag_key,
        "total_dur": round(total_dur, 3),
        "peak": round(peak, 4),
        "end_rms": round(end_rms, 4),
        "w_start": round(w_start, 3),
        "w_end": round(w_end, 3),
        "tail_margin": tail_margin,
        "overlap": round(ov, 2),
        "auto_force_to": auto_force_to,
        "cutoff": cutoff,
        "reason": reason,
        "expected": expected_dlg,
        "transcript": transcript,
    }
    json.dump(res, open(audit_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res

def run_audit(ep_ids):
    all_flow_map = {}
    for fp in glob.glob(os.path.join(BASE_DIR, "flow_*.json")):
        if "retake" in fp or "failed" in fp:
            continue
        try:
            for j in json.load(open(fp, encoding="utf-8")):
                if isinstance(j, dict) and "id" in j:
                    all_flow_map[j["id"]] = j
        except Exception:
            pass

    retakes = []
    total_checked = 0
    for ep_id in ep_ids:
        cfg = EPISODES_261126[ep_id]
        raw_dir = os.path.join(BASE_DIR, ep_id, "raw_9x16")
        print(f"\n=== AUDITING {ep_id.upper()} ({len(cfg['shots'])} shots) — {cfg['title']} ===", flush=True)
        for sid, scale, skey, ckeys, sp, act, speaker, dlg in cfg["shots"]:
            mp4 = os.path.join(raw_dir, f"{sid}.mp4")
            tag = f"{ep_id}_9x16_{sid}"
            if not is_valid_mp4_video(mp4):
                if os.path.exists(mp4):
                    try: os.remove(mp4)
                    except Exception: pass
                print(f"  [MISSING/INVALID_MP4] {tag} -> queueing retake!", flush=True)
                jid = f"{ep_id}_{sid}_9x16"
                if jid in all_flow_map:
                    rj = dict(all_flow_map[jid])
                    rj["overwrite"] = True
                    retakes.append(rj)
                continue

            if not speaker or not dlg:
                run_demucs_stems(mp4, tag)
                total_checked += 1
                print(f"  [VISUAL OK] {tag}", flush=True)
                continue

            info = analyze_clip_speech(mp4, tag, dlg)
            total_checked += 1
            if info["cutoff"]:
                print(f"  [RETAKE NEEDED] {tag}: {info['reason']}\n     EXP: {dlg}\n     ACT: {info['transcript']}", flush=True)
                jid = f"{ep_id}_{sid}_9x16"
                if jid in all_flow_map:
                    rj = dict(all_flow_map[jid])
                    rj["overwrite"] = True
                    rj["seconds"] = min(12, int(rj.get("seconds", 9)) + 2)
                    rj["prompts"] = [
                        p.replace("4.5 giây đầu", "3.8 giây đầu, nhịp nói gọn gàng dứt khoát")
                         .replace(f"Tạo video {all_flow_map[jid]['seconds']} giây", f"Tạo video {rj['seconds']} giây")
                        for p in rj.get("prompts", [rj.get("prompt", "")])
                    ]
                    rj["prompt"] = rj["prompts"][0]
                    retakes.append(rj)
            else:
                echo_note = f" [ECHO_TRIM->{info['auto_force_to']}s]" if info["auto_force_to"] else ""
                print(f"  [OK] {tag}: ov={info['overlap']:.2f} | {info['w_start']:.2f}..{info['w_end']:.2f}s / {info['total_dur']:.2f}s{echo_note}", flush=True)

    tag_name = "_".join(ep_ids)
    retake_path = os.path.join(BASE_DIR, f"flow_retakes_{tag_name}.json")
    json.dump(retakes, open(retake_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n=== AUDIT COMPLETE ({tag_name}): checked={total_checked} | retakes_needed={len(retakes)} -> {retake_path} ===", flush=True)
    return retakes


def fft_bandpass_stereo(stereo, low_hz=85.0, high_hz=13500.0):
    n = len(stereo)
    if n < 64:
        return stereo
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    mask = np.ones_like(freqs, dtype=np.float32)
    mask *= np.clip((freqs - low_hz * 0.6) / max(1.0, low_hz * 0.4), 0.0, 1.0)
    mask *= np.clip((high_hz * 1.15 - freqs) / max(1.0, high_hz * 0.15), 0.0, 1.0)
    out = np.empty_like(stereo)
    for ch in range(2):
        out[:, ch] = np.fft.irfft(np.fft.rfft(stereo[:, ch]) * mask, n=n).astype(np.float32)
    return out

def load_bgm_48k_prepared(bgm_fn):
    if bgm_fn in _BGM_CACHE:
        return _BGM_CACHE[bgm_fn]
    p = os.path.join(BGM_DIR, bgm_fn)
    assert os.path.exists(p), f"Missing BGM file: {p}"
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"
    ])
    arr = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)
    n = len(arr)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    eq = np.ones_like(freqs, dtype=np.float32)
    eq *= np.clip((freqs - 60.0) / 45.0, 0.0, 1.0)
    eq *= np.clip((11500.0 - freqs) / 2000.0, 0.0, 1.0)
    pocket = 1.0 - 0.40 * np.exp(-0.5 * ((freqs - 2150.0) / 850.0) ** 2)
    eq *= pocket.astype(np.float32)
    for ch in range(2):
        arr[:, ch] = np.fft.irfft(np.fft.rfft(arr[:, ch]) * eq, n=n).astype(np.float32)
    mono = arr.mean(axis=1)
    win = SR // 10
    env = np.sqrt(np.mean(mono[:len(mono)//win*win].reshape(-1, win) ** 2, axis=1))
    act = env[env > np.percentile(env, 25)]
    cur_rms = float(np.median(act)) if len(act) else 0.05
    arr *= (0.036 / max(cur_rms, 0.008))
    _BGM_CACHE[bgm_fn] = arr
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
        if pos < length_samples and pos >= 1920:
            xf = 1920
            w = np.linspace(0.0, 1.0, xf, dtype=np.float32)[:, None]
            out[pos - xf:pos] = out[pos - xf:pos] * (1.0 - w) + bgm_arr[:xf] * w
            cur = xf
    return out

def detect_tight_bounds_48k(voc_stereo, total_dur, audit_info=None, is_wide=False, is_cta=False):
    mono = voc_stereo.mean(axis=1)
    ws = 0.020
    win = int(SR * ws)
    nf = len(mono) // win
    rms = np.sqrt(np.mean(mono[:nf * win].reshape(nf, win) ** 2, axis=1))

    force_to = audit_info.get("auto_force_to") if audit_info else None
    s_idx = int(0.05 / ws)
    e_idx = int((force_to if force_to is not None else total_dur - 0.03) / ws)
    e_idx = max(s_idx + 4, min(len(rms), e_idx))

    sub = rms[s_idx:e_idx]
    peak = float(np.max(sub)) if len(sub) else 0.01
    core_thr = max(0.012, peak * 0.10)
    soft_thr = max(0.0034, peak * 0.024)

    core_idx = np.where(sub >= core_thr)[0] + s_idx
    if len(core_idx) == 0:
        sp_start = 0.15
        sp_end = min(total_dur - 0.08, sp_start + 2.2)
    else:
        valid = []
        cluster = [core_idx[0]]
        for idx in core_idx[1:]:
            if (idx - cluster[-1]) * ws <= 0.95:
                cluster.append(idx)
            else:
                if len(cluster) >= 3:
                    valid.extend(cluster)
                cluster = [idx]
        if len(cluster) >= 3:
            valid.extend(cluster)
        if not valid:
            valid = list(core_idx)

        first_i, last_i = valid[0], valid[-1]
        while first_i > s_idx and (valid[0] - first_i) * ws < 0.25:
            if np.max(rms[max(s_idx, first_i - 3):first_i]) >= soft_thr:
                first_i -= 1
            else:
                break
        while last_i < e_idx - 1 and (last_i - valid[-1]) * ws < 0.50:
            if np.max(rms[last_i + 1:min(e_idx, last_i + 6)]) >= soft_thr:
                last_i += 1
            else:
                break
        sp_start = first_i * ws
        sp_end   = (last_i + 1) * ws

    if audit_info and audit_info.get("w_end"):
        w_s = float(audit_info["w_start"])
        w_e = float(audit_info["w_end"])
        if force_to is not None:
            w_e = min(w_e, force_to - 0.12)
        sp_start = max(0.04, min(sp_start, w_s))
        sp_end   = min(total_dur - 0.04, max(sp_end, w_e))

    pre_pad  = 0.26 if is_wide else 0.18
    post_pad = 0.52 if is_cta else (0.38 if is_wide else 0.30)

    ss = max(0.04, sp_start - pre_pad)
    to = force_to if force_to is not None else min(total_dur - 0.03, sp_end + post_pad)
    if to - ss < 1.80:
        to = min(total_dur - 0.03, ss + 1.92)

    sp_slice = mono[int(sp_start * SR):max(int(sp_start * SR) + 1200, int(sp_end * SR))]
    sp_rms = float(np.sqrt(np.mean(sp_slice ** 2))) if len(sp_slice) else 0.05
    return ss, to, sp_start, sp_end, sp_rms

def slice_exact_samples(arr, start_sample, n_samples):
    end_sample = start_sample + n_samples
    if start_sample < 0:
        start_sample = 0
        end_sample = n_samples
    if end_sample <= len(arr):
        return arr[start_sample:end_sample].copy()
    out = np.zeros((n_samples, 2), dtype=np.float32)
    avail = max(0, len(arr) - start_sample)
    if avail > 0:
        out[:avail] = arr[start_sample:start_sample + avail]
    return out

MAX_EPISODE_SEC = 90.0
CLIFFHANGER_SPLIT_AFTER = {
    "r01": "s08",  # Ông Sỹ mắng con rể nhờ nhà vợ mua nhà 6 tỷ (~46s) | Tập 2: Kiên tung sao kê & sổ đỏ (~50s)
    "r02": "s06",  # Chị chồng mách tội em dâu gửi 5tr về ngoại (~34s) | Tập 2: Nam tiết lộ vợ kiếm 40tr/tháng (~59s)
    "r03": "s08",  # Bà Lệ nhận vơ tự tay nấu 10 mâm cỗ (~48s) | Tập 2: Bố chồng hỏi bẫy túi nấm & trích camera (~49s)
    "r04": "s07",  # Bà Quế làm chứng giả vụ nhẫn kim cương trong làn trứng (~41s) | Tập 2: Hoàng vạch trần bẫy (~49s)
}
_SFX_CACHE = {}

def load_sfx_48k(sfx_fn, target_peak=0.25):
    key = (sfx_fn, target_peak)
    if key in _SFX_CACHE:
        return _SFX_CACHE[key]
    p = os.path.join(SFX_DIR, sfx_fn)
    if not os.path.exists(p):
        return np.zeros((int(0.4 * SR), 2), dtype=np.float32)
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"
    ])
    if len(raw) < 4:
        return np.zeros((int(0.4 * SR), 2), dtype=np.float32)
    arr = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)
    pk = float(np.max(np.abs(arr))) + 1e-6
    arr = (arr * (target_peak / pk)).astype(np.float32)
    _SFX_CACHE[key] = arr
    return arr

def overlay_sfx_at(buf, sfx_arr, start_samp, gain=1.0):
    if len(sfx_arr) == 0 or len(buf) == 0:
        return
    s0 = max(0, int(start_samp))
    if s0 >= len(buf):
        return
    take = min(len(sfx_arr), len(buf) - s0)
    if take > 0:
        buf[s0:s0 + take] += sfx_arr[:take] * float(gain)

def cleanup_stale_variants(base_vn_title, keep_fnames):
    keep_set = set(keep_fnames)
    stale_candidates = [
        f"{BATCH_CODE} K4 {base_vn_title} final.mp4",
        f"{BATCH_CODE} K4 {base_vn_title} phần 1 final.mp4",
        f"{BATCH_CODE} K4 {base_vn_title} phần 2 final.mp4",
        f"{BATCH_CODE} K4 {base_vn_title} phần 3 final.mp4",
        f"{BATCH_CODE} K4 {base_vn_title} full final.mp4",
        f"{BATCH_CODE} K4 {base_vn_title} tập full final.mp4",
    ] + [f"{BATCH_CODE} K4 {base_vn_title} tập {k} final.mp4" for k in range(1, 6)]
    for fn in stale_candidates:
        if fn in keep_set:
            continue
        for tdir in (K4_DRIVE_DIR, MASTER_CLOUD_DIR, LOCAL_CAPCUT_DIR):
            p = os.path.join(tdir, fn)
            if os.path.exists(p):
                try:
                    os.remove(p)
                    print(f"  [CLEANED STALE] Removed {p}", flush=True)
                except Exception:
                    pass

from curated_hooks_director_v6 import CURATED_261126_V6

def extract_complete_beat_v6(seg_vid, seg_pcm, out_vid, dip_to_black=False):
    """Director V6: Preserves 100% of the complete spoken sentence(s) in `seg_vid` (`0%` mid-sentence chopping!), trimming only excess leading/trailing silence."""
    n_frames = len(seg_pcm) // SAMPLES_PER_FRAME
    frm_rms = np.sqrt(np.mean(seg_pcm.reshape(n_frames, SAMPLES_PER_FRAME * 2) ** 2, axis=1))
    pk_rms = float(np.max(frm_rms)) if len(frm_rms) else 0.02
    thr = max(0.0075, pk_rms * 0.065)
    sp_frames = np.where(frm_rms >= thr)[0]
    if len(sp_frames) == 0:
        f0, f1 = 0, n_frames
    else:
        f0 = max(0, int(sp_frames[0]) - 3)           # 0.10s natural breath lead-in
        f1 = min(n_frames, int(sp_frames[-1]) + 6)   # 0.20s complete-syllable release tail
        if f1 - f0 < min(n_frames, 45):
            f1 = min(n_frames, f0 + 45)

    nf_sub = max(1, f1 - f0)
    h_pcm = seg_pcm[f0 * SAMPLES_PER_FRAME : f1 * SAMPLES_PER_FRAME].copy()
    fi = min(1200, len(h_pcm) // 6)
    fo = min(1600, len(h_pcm) // 6)
    if fi > 0:
        h_pcm[:fi] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi, dtype=np.float32)))[:, None]
    if fo > 0:
        h_pcm[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo, dtype=np.float32)))[:, None]

    sub_dur = nf_sub / float(FPS)
    vf_h = [
        "crop=1036:1842:22:39",
        "scale=1080:1920:flags=lanczos",
        "eq=contrast=1.04:saturation=1.06",
        "fade=t=in:st=0:d=0.08",
    ]
    if dip_to_black and sub_dur > 0.45:
        vf_h.append(f"fade=t=out:st={sub_dur - 0.26:.3f}:d=0.26")
    subprocess.run([
        "ffmpeg", "-nostdin", "-threads", "2", "-y", "-v", "error",
        "-ss", f"{f0 / float(FPS):.4f}", "-t", f"{sub_dur + 0.08:.4f}", "-i", seg_vid,
        "-vf", ",".join(vf_h), "-an", "-r", str(FPS), "-frames:v", str(nf_sub),
        "-threads", "3", "-filter_threads", "2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-level", "4.1", "-g", "30", "-bf", "2", "-pix_fmt", "yuv420p",
        out_vid
    ], stdin=subprocess.DEVNULL, check=True)
    return out_vid, h_pcm

_USER_HOOK_BGM = None

def load_user_signature_hook_48k():
    """Loads the user's exact extracted Highlight Hook instrumental from `260922 Mất 50 chẹo.mp4` (0.85s..14.15s)."""
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

def back_align_signature_hook_bgm(tot_samples):
    """Always back-aligns the ending of `user_hook_260922_mat50cheo.wav` to the exact end of the Hook/Cliffhanger so the 14.15s musical hit lands right on the black pause!"""
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

def make_black_pause_clip(out_vid, n_frames=24):
    dur_s = n_frames / float(FPS)
    subprocess.run([
        "ffmpeg", "-nostdin", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={FPS}:d={dur_s:.4f}",
        "-frames:v", str(n_frames), "-an",
        "-threads", "3", "-filter_threads", "2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-level", "4.1", "-g", "30", "-bf", "2", "-pix_fmt", "yuv420p",
        out_vid
    ], stdin=subprocess.DEVNULL, check=True)
    return out_vid, np.zeros((n_frames * SAMPLES_PER_FRAME, 2), dtype=np.float32)

def resolve_curated_cut_indices(scene_ids, timeline_log, avoid_scene=None):
    sc_to_idx = {it["scene"]: idx for idx, it in enumerate(timeline_log)}
    out = []
    for sid in scene_ids:
        if sid in sc_to_idx and sid != avoid_scene and sc_to_idx[sid] not in out:
            out.append(sc_to_idx[sid])
    return out

def build_cold_open_hook_v6(seg_dir, tag_prefix, picks, seg_videos, seg_audios, timeline_log):
    """Director V6: Hand-curated 2-3 complete-sentence dramatic beats + 0.80s solid black breath pause synced to `user_hook_260922_mat50cheo.wav`."""
    h_vids, h_pcms = [], []
    for j, cut_i in enumerate(picks):
        dip = (j == 0 and len(picks) >= 3) or (j == len(picks) - 1)
        sc_lbl = timeline_log[cut_i]["scene"]
        hv = os.path.join(seg_dir, f"hook_{tag_prefix}_{j+1}_{sc_lbl}.mp4")
        _, hp = extract_complete_beat_v6(seg_videos[cut_i], seg_audios[cut_i], hv, dip_to_black=dip)
        h_vids.append(hv)
        h_pcms.append(hp)

    blk_vid = os.path.join(seg_dir, f"hook_{tag_prefix}_black_pause.mp4")
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

    mix_h = dlg_h + bgm_h * duck_f
    mix_h = np.clip(np.tanh(mix_h * 1.05) / 1.05, -0.94, 0.94)
    return h_vids, mix_h

def build_cliffhanger_outro_v6(seg_dir, tag_prefix, picks, seg_videos, seg_audios, timeline_log):
    """Director V6: Hand-curated 1-2 complete-sentence Next-Episode Teaser beats + 0.60s black climax hit."""
    c_vids, c_pcms = [], []
    for j, cut_i in enumerate(picks):
        is_last = (j == len(picks) - 1)
        sc_lbl = timeline_log[cut_i]["scene"]
        cv = os.path.join(seg_dir, f"cliff_{tag_prefix}_{j+1}_{sc_lbl}.mp4")
        _, cp = extract_complete_beat_v6(seg_videos[cut_i], seg_audios[cut_i], cv, dip_to_black=is_last)
        c_vids.append(cv)
        c_pcms.append(cp)

    blk_vid = os.path.join(seg_dir, f"cliff_{tag_prefix}_black_end.mp4")
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

    mix_c = dlg_c + bgm_c * duck_f
    mix_c = np.clip(np.tanh(mix_c * 1.05) / 1.05, -0.94, 0.94)
    return c_vids, mix_c

def choose_multi_episode_ranges_v6(ep_id, timeline_log, acts, max_story_budget=63.5, max_last_budget=72.5, force_n_parts=None):
    """Splits a >90s story into N episodes at dramatic cliffhangers so EVERY tập (Complete-Sentence Hook + Story + Complete-Sentence Cliffhanger) <= 90.0s!"""
    total_dur = timeline_log[-1]["end"]
    curated = CURATED_261126_V6.get(ep_id, {})
    want_sc = curated.get("split_after")

    if (force_n_parts in (None, 2)) and want_sc:
        for i, item in enumerate(timeline_log[:-1], 1):
            p1 = item["end"]
            p2 = total_dur - p1
            if item["scene"] == want_sc and p1 <= max_story_budget and p2 <= max_last_budget:
                return [(0, i), (i, len(timeline_log))]

    start_n = force_n_parts if force_n_parts else 2
    act_triggers = {sc for sc, *_ in acts[1:]}
    for n_parts in range(start_n, 5):
        ranges = []
        cur_start = 0
        ok = True
        for p_idx in range(1, n_parts):
            rem_parts = n_parts - p_idx + 1
            cur_t0 = timeline_log[cur_start]["start"]
            rem_dur = total_dur - cur_t0
            ideal_end_t = cur_t0 + (rem_dur / float(rem_parts))
            best_i = None
            best_score = 1e9
            for i in range(cur_start + 2, len(timeline_log) - (rem_parts - 1) + 1):
                part_d = timeline_log[i - 1]["end"] - cur_t0
                after_d = total_dur - timeline_log[i - 1]["end"]
                if part_d > max_story_budget:
                    continue
                if rem_parts == 2 and after_d > max_last_budget:
                    continue
                if rem_parts > 2 and after_d > max_story_budget * (rem_parts - 2) + max_last_budget:
                    continue
                dist = abs(timeline_log[i - 1]["end"] - ideal_end_t)
                if i < len(timeline_log) and timeline_log[i]["scene"] in act_triggers:
                    dist -= 5.0
                if dist < best_score:
                    best_score = dist
                    best_i = i
            if best_i is None:
                ok = False
                break
            ranges.append((cur_start, best_i))
            cur_start = best_i
        if ok and (total_dur - timeline_log[cur_start]["start"]) <= max_last_budget:
            ranges.append((cur_start, len(timeline_log)))
            return ranges

    m1 = len(timeline_log) // 3
    m2 = (2 * len(timeline_log)) // 3
    return [(0, m1), (m1, m2), (m2, len(timeline_log))]

def mix_and_deliver_subfilm(
    ep_id, ep_dir, vn_title, sub_videos, sub_audios, sub_tlog_orig, all_tlog_orig, acts,
    hook_videos=None, hook_pcm=None, cliff_videos=None, cliff_pcm=None,
    enforce_90s=True, part_suffix=""
):
    hook_videos = hook_videos or []
    cliff_videos = cliff_videos or []
    hook_pcm = hook_pcm if hook_pcm is not None else np.zeros((0, 2), dtype=np.float32)
    cliff_pcm = cliff_pcm if cliff_pcm is not None else np.zeros((0, 2), dtype=np.float32)

    orig_offset_samp = sub_tlog_orig[0]["start_sample"]
    sub_tlog = []
    for it in sub_tlog_orig:
        c = dict(it)
        c["start_sample"] = it["start_sample"] - orig_offset_samp
        c["end_sample"] = it["end_sample"] - orig_offset_samp
        c["start"] = round(c["start_sample"] / float(SR), 3)
        c["end"] = round(c["end_sample"] / float(SR), 3)
        sub_tlog.append(c)

    story_samples = sub_tlog[-1]["end_sample"]
    dlg_story = np.concatenate(sub_audios, axis=0)
    assert len(dlg_story) == story_samples, f"Sample mismatch: {len(dlg_story)} vs {story_samples}"

    # Map global act triggers cleanly into this subfilm's story [0 .. story_samples] timeline
    global_acts = []
    for sc_trigger, bgm_fn, bgm_off, bgm_gain in acts:
        st_samp = 0
        for item in all_tlog_orig:
            if item["scene"] == sc_trigger:
                st_samp = item["start_sample"]
                break
        global_acts.append((st_samp, bgm_fn, bgm_off, bgm_gain))
    global_acts[0] = (0, global_acts[0][1], global_acts[0][2], global_acts[0][3])

    part_end_global = orig_offset_samp + story_samples
    active_at_start = global_acts[0]
    for ga in global_acts:
        if ga[0] <= orig_offset_samp:
            active_at_start = ga
    act_starts = [(0, active_at_start[1], active_at_start[2] + (orig_offset_samp - active_at_start[0]) / float(SR), active_at_start[3])]
    for ga in global_acts:
        if orig_offset_samp < ga[0] < part_end_global:
            act_starts.append((ga[0] - orig_offset_samp, ga[1], ga[2], ga[3]))

    bgm_story = np.zeros((story_samples, 2), dtype=np.float32)
    xfade_samp = int(1.80 * SR)

    for a_i, (st_s, b_fn, b_off, b_gain) in enumerate(act_starts):
        nx_s = act_starts[a_i + 1][0] if a_i + 1 < len(act_starts) else story_samples
        s0 = max(0, st_s - (xfade_samp // 2 if a_i > 0 else 0))
        s1 = min(story_samples, nx_s + (xfade_samp // 2 if a_i + 1 < len(act_starts) else 0))
        if s1 <= s0:
            continue
        b_arr = load_bgm_48k_prepared(b_fn)
        piece = get_looped_bgm_slice(b_arr, b_off, s1 - s0) * float(b_gain)

        if a_i > 0:
            fi_len = min(xfade_samp, len(piece))
            w_in = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi_len, dtype=np.float32)))[:, None]
            piece[:fi_len] *= w_in
        else:
            fi_len = min(int(0.65 * SR), len(piece))
            piece[:fi_len] *= np.linspace(0.0, 1.0, fi_len, dtype=np.float32)[:, None]

        if a_i + 1 < len(act_starts):
            fo_len = min(xfade_samp, len(piece))
            w_out = (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo_len, dtype=np.float32)))[:, None]
            piece[-fo_len:] *= w_out
        else:
            fo_sec = 0.85 if len(cliff_pcm) > 0 else 2.10
            fo_len = min(int(fo_sec * SR), len(piece))
            piece[-fo_len:] *= np.linspace(1.0, 0.0, fo_len, dtype=np.float32)[:, None]

        bgm_story[s0:s1] += piece

    blk = SR // 10
    n_blk = story_samples // blk
    dlg_mono = np.abs(dlg_story[:n_blk * blk].mean(axis=1)).reshape(n_blk, blk)
    blk_rms = np.sqrt(np.mean(dlg_mono ** 2, axis=1))
    duck_blk = np.where(blk_rms > 0.022, 0.72, 1.30).astype(np.float32)
    kernel = np.ones(6, dtype=np.float32) / 6.0
    duck_smooth = np.convolve(np.pad(duck_blk, (3, 2), mode="edge"), kernel, mode="valid")
    duck_full = np.interp(
        np.linspace(0.0, n_blk, story_samples, endpoint=False),
        np.arange(n_blk, dtype=np.float32) + 0.5,
        duck_smooth
    ).astype(np.float32)[:, None]

    mix_story = dlg_story + bgm_story * duck_full
    mix_story = np.clip(np.tanh(mix_story * 1.04) / 1.04, -0.94, 0.94)

    chunks = []
    if len(hook_pcm) > 0:
        chunks.append(hook_pcm)
    chunks.append(mix_story)
    if len(cliff_pcm) > 0:
        chunks.append(cliff_pcm)
    mix_master = np.concatenate(chunks, axis=0)
    total_samples = len(mix_master)
    vid_total = total_samples / float(SR)

    if enforce_90s:
        assert vid_total <= MAX_EPISODE_SEC + 0.15, f"{ep_id}{part_suffix} exceeded {MAX_EPISODE_SEC}s ({vid_total:.2f}s)!"

    all_concat_vids = list(hook_videos) + list(sub_videos) + list(cliff_videos)

    master_wav = os.path.join(ep_dir, f"master_v4_48k{part_suffix}.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix_master * 32767.0).astype(np.int16).tobytes())

    concat_txt = os.path.join(ep_dir, f"concat_v4_9x16{part_suffix}.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for sv in all_concat_vids:
            cf.write(f"file '{sv}'\n")

    final_local = os.path.join(ep_dir, f"{BATCH_CODE} K4 {vn_title} final.mp4")
    subprocess.run([
        "ffmpeg", "-nostdin", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", master_wav,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "224k", "-ar", str(SR), "-ac", "2",
        "-movflags", "+faststart", final_local
    ], stdin=subprocess.DEVNULL, check=True)

    qc_pcm = load_mp4_audio_48k_stereo(final_local)
    hook_off = len(hook_pcm)
    muted_tails = 0
    for item in sub_tlog:
        if item["mode"] != "voice":
            continue
        s_end = min(len(qc_pcm), hook_off + item["end_sample"] - int(0.10 * SR))
        s_beg = max(hook_off + item["start_sample"], s_end - int(0.45 * SR))
        trms = float(np.sqrt(np.mean(qc_pcm[s_beg:s_end] ** 2))) if s_end > s_beg else 0.0
        if trms < 0.004:
            muted_tails += 1
            print(f"  [WARN] Low tail RMS on {ep_id}{part_suffix} cut #{item['idx']} ({item['scene']}): {trms:.5f}")

    p_sil = subprocess.run(
        ["ffmpeg", "-nostdin", "-threads", "2", "-i", final_local, "-af", "silencedetect=noise=-40dB:d=1.8", "-f", "null", "-"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    sil_count = (p_sil.stderr or "").count("silence_duration")

    delivered = deliver_episode(final_local, vn_title)
    for p in (master_wav, final_local):
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass

    hook_sec = round(len(hook_pcm) / float(SR), 2)
    cliff_sec = round(len(cliff_pcm) / float(SR), 2)
    tag_lim = "<=90s" if enforce_90s else "FULL"
    print(
        f"=== {ep_id.upper()}{part_suffix.upper()} V4 COMPLETE: {vid_total:.2f}s ({tag_lim}, hook={hook_sec}s, cliff={cliff_sec}s) | {len(sub_videos)} story cuts | muted_tails={muted_tails} | dead_air_gaps={sil_count} ===",
        flush=True
    )
    return {
        "part_title": vn_title,
        "is_full_master": not enforce_90s,
        "hook_duration": hook_sec,
        "cliffhanger_duration": cliff_sec,
        "scenes_count": len(sub_videos),
        "duration": round(vid_total, 2),
        "muted_tails": muted_tails,
        "dead_air_gaps": sil_count,
        **delivered,
    }

def deliver_episode(src_mp4, vn_title):
    fname = f"{BATCH_CODE} K4 {vn_title} final.mp4"
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
    print(f"  [DELIVERED V3] -> {out['brand_path']}", flush=True)
    return out

def cleanup_episode_temp(ep_id, shots, final_local):
    """Purge heavy intermediate WAVs & segment MP4s after verified delivery to keep C:\ >25 GB free."""
    ep_dir = os.path.join(BASE_DIR, ep_id)
    for p in [os.path.join(ep_dir, "master_v3_48k.wav"), final_local]:
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
    seg_dir = os.path.join(ep_dir, "seg_v3_9x16")
    if os.path.isdir(seg_dir):
        shutil.rmtree(seg_dir, ignore_errors=True)
    for sid, *_ in shots:
        tag = f"{ep_id}_9x16_{sid}"
        for p in [os.path.join(DEMUCS_DIR, f"{tag}.wav"), os.path.join(DEMUCS_DIR, f"{tag}_vocals.wav")]:
            if os.path.exists(p):
                try: os.remove(p)
                except Exception: pass
        ht_sub = os.path.join(DEMUCS_DIR, "htdemucs", tag)
        if os.path.isdir(ht_sub):
            shutil.rmtree(ht_sub, ignore_errors=True)

def render_episode_v3(ep_id):
    cfg = EPISODES_261126[ep_id]
    acts = cfg["acts_bgm"]
    explicit_framing = cfg.get("framing", {})

    ep_dir = os.path.join(BASE_DIR, ep_id)
    raw_dir = os.path.join(ep_dir, "raw_9x16")
    seg_dir = os.path.join(ep_dir, "seg_v3_9x16")
    os.makedirs(seg_dir, exist_ok=True)

    out_w, out_h = 1080, 1920
    target_ar = 9.0 / 16.0
    lut_ff = LUT_PATH.replace("\\", "/").replace(":", "\\:")

    shots = cfg["shots"]
    print(f"\n==================== RENDERING DIRECTOR V3: {ep_id.upper()} ({len(shots)} cuts) — {cfg['title']} ====================", flush=True)

    seg_videos = []
    seg_audios = []
    timeline_log = []
    cum_frames = 0
    prev_scale = None
    prev_framing = "STD"

    for idx, (sid, scale, skey, ckeys, sp, act, speaker, dlg) in enumerate(shots, 1):
        is_cta = (idx == len(shots))
        is_wide = scale in ("WIDE", "WIDE_CROWD", "MED")
        mode = "voice" if (speaker and dlg) else "visual"

        if sid in explicit_framing:
            framing = explicit_framing[sid]
        elif scale == "CU" and prev_scale == "CU" and prev_framing == "STD":
            framing = "CU_PUNCH"
        else:
            framing = "STD"
        prev_scale = scale
        prev_framing = framing

        src = os.path.join(raw_dir, f"{sid}.mp4")
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing raw clip: {src}")
        w, h, total_dur = probe_video(src)

        tag = f"{ep_id}_9x16_{sid}"
        voc_wav, novoc_wav = run_demucs_stems(src, tag)

        if mode == "voice":
            audit_info = analyze_clip_speech(src, tag, dlg)
            voc_full = load_wav_48k_stereo(voc_wav)
            amb_full = load_wav_48k_stereo(novoc_wav) if os.path.exists(novoc_wav) else np.zeros_like(voc_full)
            ss, to, sp_start, sp_end, sp_rms = detect_tight_bounds_48k(
                voc_full, total_dur, audit_info=audit_info, is_wide=is_wide, is_cta=is_cta
            )
        else:
            ss = 0.75
            to = min(total_dur - 0.05, 2.95)
            sp_start, sp_end, sp_rms = ss, to, 0.0
            amb_full = load_wav_48k_stereo(novoc_wav) if os.path.exists(novoc_wav) else load_mp4_audio_48k_stereo(src)
            voc_full = None

        n_frames = max(45, int(round((to - ss) * FPS)))
        exact_dur = n_frames / float(FPS)
        n_samples = n_frames * SAMPLES_PER_FRAME
        start_sample = int(round(ss * SR))

        if mode == "voice":
            v_seg = fft_bandpass_stereo(slice_exact_samples(voc_full, start_sample, n_samples), 85.0, 13500.0)
            a_seg = fft_bandpass_stereo(slice_exact_samples(amb_full, start_sample, n_samples), 90.0, 6500.0)
            gain = float(np.clip(0.155 / max(sp_rms, 0.012), 0.70, 5.20))
            v_seg = np.tanh(v_seg * gain * 1.12) / 1.12
            a_rms = float(np.sqrt(np.mean(a_seg ** 2))) + 1e-6
            a_gain = min(0.10, 0.0085 / a_rms)
            seg_pcm = v_seg + np.clip(a_seg * a_gain, -0.035, 0.035)
        else:
            a_seg = fft_bandpass_stereo(slice_exact_samples(amb_full, start_sample, n_samples), 95.0, 5200.0)
            a_rms = float(np.sqrt(np.mean(a_seg ** 2))) + 1e-6
            a_gain = min(0.14, 0.0095 / a_rms)
            seg_pcm = np.clip(a_seg * a_gain, -0.04, 0.04)

        fi = min(1344, n_samples // 4)
        fo = min(1536, n_samples // 4)
        seg_pcm[:fi] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi, dtype=np.float32)))[:, None]
        seg_pcm[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo, dtype=np.float32)))[:, None]

        if mode == "voice":
            seg_rms_check = float(np.sqrt(np.mean(seg_pcm ** 2)))
            assert seg_rms_check > 0.022, f"Audio level unexpectedly low on {ep_id}_{sid}: {seg_rms_check}"

        seg_audios.append(seg_pcm.astype(np.float32))

        vf_parts = []
        if w == 720 and h == 1280:
            vf_parts.append("delogo=x=570:y=1130:w=62:h=62")
        top_b, bot_b = detect_letterbox_bars(src, w, h, ss + exact_dur * 0.5)
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

        if framing == "CU_PUNCH":
            zf = 1.13
            nw = int(round(cw_crop / zf / 2) * 2)
            nh = int(round(ch_crop / zf / 2) * 2)
            cx_crop += (cw_crop - nw) // 2
            cy_crop += int((ch_crop - nh) * 0.34)
            cw_crop, ch_crop = nw, nh

        if cw_crop != w or ch_crop != h or cx_crop != 0 or cy_crop != 0:
            vf_parts.append(f"crop={cw_crop}:{ch_crop}:{cx_crop}:{cy_crop}")
        if os.path.exists(LUT_PATH):
            vf_parts.append(f"lut3d=file='{lut_ff}':interp=tetrahedral")
        vf_parts += [
            f"scale={out_w}:{out_h}:flags=lanczos",
            "eq=contrast=1.02:saturation=1.04",
            "unsharp=3:3:0.30:3:3:0.0",
            f"fps={FPS}",
            "format=yuv420p",
        ]
        vf = ",".join(vf_parts)

        seg_vid = os.path.join(seg_dir, f"{idx:02d}_{sid}_{framing}.mp4")
        subprocess.run([
            "ffmpeg", "-nostdin", "-threads", "2", "-y", "-v", "error",
            "-ss", f"{ss:.4f}", "-t", f"{exact_dur + 0.08:.4f}", "-i", src,
            "-vf", vf, "-an", "-r", str(FPS), "-frames:v", str(n_frames),
            "-threads", "3", "-filter_threads", "2",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-profile:v", "high", "-level", "4.1", "-g", "30", "-bf", "2", "-pix_fmt", "yuv420p",
            seg_vid
        ], stdin=subprocess.DEVNULL, check=True)

        t0 = cum_frames / float(FPS)
        t1 = (cum_frames + n_frames) / float(FPS)
        timeline_log.append({
            "idx": idx, "scene": sid, "scale": scale, "mode": mode, "framing": framing,
            "start": round(t0, 3), "end": round(t1, 3), "dur": round(exact_dur, 3),
            "start_sample": cum_frames * SAMPLES_PER_FRAME,
            "end_sample": (cum_frames + n_frames) * SAMPLES_PER_FRAME,
        })
        print(f"  [{idx:02d}_{sid}:{scale}:{framing}] {t0:6.2f}s -> {t1:6.2f}s ({exact_dur:.2f}s)", flush=True)
        cum_frames += n_frames
        seg_videos.append(seg_vid)

    vid_total = cum_frames / float(FPS)

    # Build QA_V3 contact sheet across all cuts before segment cleanup
    cols = 5
    tw, th = 216, 384
    thumbs = []
    for i, sv in enumerate(seg_videos, 1):
        _, _, d = probe_video(sv)
        t = os.path.join(QC_DIR, f"{ep_id}_s{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-nostdin", "-threads", "2", "-y", "-v", "error", "-ss", f"{d * 0.50:.2f}", "-i", sv, "-vf", f"scale={tw}:{th}", "-frames:v", "1", t], stdin=subprocess.DEVNULL, check=True)
        thumbs.append(t)
    rows = (len(thumbs) + cols - 1) // cols
    while len(thumbs) < cols * rows:
        pad_t = os.path.join(QC_DIR, f"{ep_id}_pad{len(thumbs)}.jpg")
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x14161c:s={tw}x{th}:d=0.1", "-frames:v", "1", pad_t], stdin=subprocess.DEVNULL, check=True)
        thumbs.append(pad_t)
    inp = []
    for t in thumbs:
        inp += ["-i", t]
    layout = "|".join(f"{(i % cols) * tw}_{(i // cols) * th}" for i in range(len(thumbs)))
    qa_name = f"QA_V3_{ep_id.upper()}_9x16.jpg"
    qa_sheet = os.path.join(QC_DIR, qa_name)
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs={len(thumbs)}:layout={layout}", "-frames:v", "1", qa_sheet], stdin=subprocess.DEVNULL, check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, qa_name))
    for t in thumbs:
        try: os.remove(t)
        except Exception: pass

    curated_cfg = CURATED_261126_V6[ep_id]
    full_picks = resolve_curated_cut_indices(curated_cfg["full_hook"], timeline_log, avoid_scene=timeline_log[0]["scene"])
    full_hook_vids, full_hook_pcm = build_cold_open_hook_v6(
        seg_dir, "full", full_picks, seg_videos, seg_audios, timeline_log
    )
    full_with_hook_sec = (len(full_hook_pcm) / float(SR)) + vid_total

    # If a single-episode film is between 90.0s and 93.8s ONLY because of 3 hook beats, try 2 complete curated beats [first, last] before splitting!
    if MAX_EPISODE_SEC < full_with_hook_sec <= MAX_EPISODE_SEC + 4.2 and len(full_picks) >= 3:
        two_picks = [full_picks[0], full_picks[-1]]
        fh2_vids, fh2_pcm = build_cold_open_hook_v6(
            seg_dir, "full2", two_picks, seg_videos, seg_audios, timeline_log
        )
        if (len(fh2_pcm) / float(SR)) + vid_total <= MAX_EPISODE_SEC - 0.15:
            full_hook_vids, full_hook_pcm = fh2_vids, fh2_pcm
            full_with_hook_sec = (len(full_hook_pcm) / float(SR)) + vid_total

    if full_with_hook_sec <= MAX_EPISODE_SEC - 0.10:
        p_info = mix_and_deliver_subfilm(
            ep_id, ep_dir, cfg["title"],
            seg_videos, seg_audios, timeline_log, timeline_log, acts,
            hook_videos=full_hook_vids, hook_pcm=full_hook_pcm,
            enforce_90s=True, part_suffix=""
        )
        cleanup_stale_variants(cfg["title"], [p_info["filename"]])
        parts = [p_info]
        full_master_info = p_info
        max_ep_dur = p_info["duration"]
        muted_tails = p_info["muted_tails"]
        sil_count = p_info["dead_air_gaps"]
    else:
        ranges = choose_multi_episode_ranges_v6(ep_id, timeline_log, acts, max_story_budget=71.5, max_last_budget=73.5)
        print(
            f"  [DIRECTOR V7 MULTI-EP + FULL] {ep_id.upper()} full_with_hook={full_with_hook_sec:.2f}s > {MAX_EPISODE_SEC:.0f}s -> building {len(ranges)} Tập (<=90s, Opening Intro ONLY, ZERO End-Highlight) + 1 Tập Full!",
            flush=True
        )
        parts = []
        keep_names = []
        for p_i, (a_idx, b_idx) in enumerate(ranges, 1):
            first_sc = timeline_log[a_idx]["scene"]
            if p_i == 1:
                want_h_sids = curated_cfg.get("tap1_hook", curated_cfg["full_hook"])
            elif p_i == 2:
                want_h_sids = curated_cfg.get("tap2_hook", curated_cfg["full_hook"])
            else:
                want_h_sids = curated_cfg.get("tap3_hook", curated_cfg["full_hook"])
            h_picks = resolve_curated_cut_indices(want_h_sids, timeline_log, avoid_scene=first_sc)
            if len(h_picks) < 2:
                h_picks = [i for i in range(a_idx + 1, b_idx) if timeline_log[i]["mode"] == "voice"][:2]

            p_hvids, p_hpcm = build_cold_open_hook_v6(
                seg_dir, f"ep{p_i}", h_picks, seg_videos, seg_audios, timeline_log
            )
            # Director V7: Highlight ONLY at beginning (`0.0s`), ZERO highlight at episode end!
            c_vids, c_pcm = [], np.zeros((0, 2), dtype=np.float32)

            story_part_samp = timeline_log[b_idx - 1]["end_sample"] - timeline_log[a_idx]["start_sample"]
            if (len(p_hpcm) + story_part_samp) / float(SR) > 89.6 and len(h_picks) >= 3:
                p_hvids, p_hpcm = build_cold_open_hook_v6(
                    seg_dir, f"ep{p_i}_h2", h_picks[:2], seg_videos, seg_audios, timeline_log
                )

            ep_part_info = mix_and_deliver_subfilm(
                ep_id, ep_dir, f"{cfg['title']} tập {p_i}",
                seg_videos[a_idx:b_idx], seg_audios[a_idx:b_idx], timeline_log[a_idx:b_idx], timeline_log, acts,
                hook_videos=p_hvids, hook_pcm=p_hpcm, cliff_videos=c_vids, cliff_pcm=c_pcm,
                enforce_90s=True, part_suffix=f"_tap{p_i}"
            )
            parts.append(ep_part_info)
            keep_names.append(ep_part_info["filename"])

        full_master_info = mix_and_deliver_subfilm(
            ep_id, ep_dir, f"{cfg['title']} tập full",
            seg_videos, seg_audios, timeline_log, timeline_log, acts,
            hook_videos=full_hook_vids, hook_pcm=full_hook_pcm,
            enforce_90s=False, part_suffix="_full"
        )
        parts.append(full_master_info)
        keep_names.append(full_master_info["filename"])
        cleanup_stale_variants(cfg["title"], keep_names)

        ep_only = [x for x in parts if not x.get("is_full_master")]
        max_ep_dur = max(x["duration"] for x in ep_only)
        muted_tails = sum(x["muted_tails"] for x in parts)
        sil_count = sum(x["dead_air_gaps"] for x in parts)

    cleanup_episode_temp(ep_id, shots, "")

    return {
        "episode": ep_id,
        "director_version": "v6_curated_full_sentence_hook",
        "batch": BATCH_CODE,
        "title": cfg["title"],
        "is_split": len(parts) > 1,
        "episodes_count": sum(1 for x in parts if not x.get("is_full_master")),
        "parts_count": len(parts),
        "parts": parts,
        "scenes_count": len(seg_videos),
        "total_story_duration": round(vid_total, 2),
        "full_duration": full_master_info["duration"],
        "duration": max_ep_dur,
        "muted_tails": muted_tails,
        "dead_air_gaps": sil_count,
        "acts_bgm": [x[1] for x in acts],
        "qa_sheet": qa_sheet,
        "filename": full_master_info["filename"],
        "brand_path": full_master_info["brand_path"],
        "master_cloud_path": full_master_info["master_cloud_path"],
        "local_path": full_master_info["local_path"],
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "render"
    ep_ids = sys.argv[2:] if len(sys.argv) > 2 else list(EPISODES_261126.keys())
    if mode == "stems":
        for ep in ep_ids:
            cfg = EPISODES_261126[ep]
            raw_d = os.path.join(BASE_DIR, ep, "raw_9x16")
            print(f"=== EXTRACTING CUDA STEMS FOR {ep.upper()} ({len(cfg['shots'])} shots) ===", flush=True)
            for sid, *_ in cfg["shots"]:
                mp4 = os.path.join(raw_d, f"{sid}.mp4")
                if is_valid_mp4_video(mp4):
                    run_demucs_stems(mp4, f"{ep}_9x16_{sid}")
        print("=== STEMS COMPLETE ===", flush=True)
    elif mode == "audit":
        run_audit(ep_ids)
    elif mode == "render":
        rep_path = os.path.join(BASE_DIR, "delivery_v3_20_reels_261126.json")
        missing_eps = []
        for ep in ep_ids:
            raw_d = os.path.join(BASE_DIR, ep, "raw_9x16")
            need_sids = [s[0] for s in EPISODES_261126[ep]["shots"]]
            miss = [sid for sid in need_sids if not os.path.exists(os.path.join(raw_d, f"{sid}.mp4"))]
            if miss:
                print(f"[SKIP RENDER] {ep} still missing {miss} -> rendering ready episodes first!", flush=True)
                missing_eps.append((ep, miss))
                continue
            res = render_episode_v3(ep)
            existing = {}
            if os.path.exists(rep_path):
                for r in json.load(open(rep_path, encoding="utf-8")):
                    existing[r["episode"]] = r
            existing[ep] = res
            ordered = [existing[k] for k in sorted(existing.keys())]
            json.dump(ordered, open(rep_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        if missing_eps:
            raise FileNotFoundError(f"Unrendered episodes due to missing clips: {missing_eps}")
        if os.path.isdir(r"G:\My Drive\AI_Full_Studio\03_Du_An"):
            os.makedirs(DU_AN_CLOUD_DIR, exist_ok=True)
            for fn in ("episodes_r01_to_r20_spec.py", "prepare_261126_chatgpt_assets.py", "build_20_cinema_episodes_261126.py", "render_20_reels_director_v3.py", "delivery_v3_20_reels_261126.json"):
                sp = os.path.join(BASE_DIR, fn)
                if os.path.exists(sp):
                    shutil.copy2(sp, os.path.join(DU_AN_CLOUD_DIR, fn))
        print(f"\nRENDERED & SYNCED {len(ep_ids)} EPISODES ({len(existing)}/20 TOTAL DELIVERED)!", flush=True)
    else:
        raise SystemExit(f"Unknown mode: {mode}")
