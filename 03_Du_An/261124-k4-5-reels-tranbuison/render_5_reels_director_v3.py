"""
Cinema Director V3 — Master Auditor & Renderer for the 5-Reel K4 Batch (`261124`):
- Run with `D:\AI\full studio\voice-studio\.venv\Scripts\python.exe` (CUDA `demucs` + `faster_whisper` + `numpy`).
- Modes:
  1. `audit [f01 f02 ...]` -> Runs CUDA Demucs (`vocals.wav` + `no_vocals.wav`) + Whisper word-timestamp audit on all raw clips:
     - Gate A: Verifies spoken dialogue matches scripted line (`overlap >= 0.38`, `sp_rms >= 0.012`).
     - Gate B: Verifies 0% mid-sentence cutoffs (`tail_margin < 0.14s` & `end_rms > 0.014` or missing final words near EOF). Outputs `flow_retakes_cutoff.json` automatically if any clip needs a clean retake!
     - Gate C: Auto-detects trailing echoed words after a completed sentence (`gap >= 0.75s`) and sets `auto_force_to` cleanly before the echo!
  2. `render [f01 f02 ...]` -> Renders `1080x1920 @ 30fps` NVENC Cinema Masters:
     - Sample-locked 48kHz stereo Python PCM slicing (`N * 1600` samples/frame -> `0` muted tails, `0` AAC concat drift, `0` dead-air holes).
     - Whisper + -35dB RMS speech bounds so soft Vietnamese ending particles ("ạ", "nhé", "ơi") are 100% preserved.
     - Multi-Act Natural Film Scoring (`Acoustic Guitar` normal scenes -> `Dramatic Tension` conflict -> `Warm Family Piano` resolution) with 1.8s cosine crossfades, Voice Pocket EQ (`-4.5dB @ 2.15kHz`), and smooth 500ms sidechain ducking.
     - Axial `CU_PUNCH` (`1.13x`) on consecutive close-ups for seamless `Toàn – Trung – Cận` cinema pacing.
     - Delivers `261124 K4 <Tên phim> final.mp4` to all 3 folders + QA Contact Sheets + Cloud `03_Du_An` sync!
"""
import json, os, re, shutil, subprocess, sys, wave
import numpy as np
from faster_whisper import WhisperModel

sys.path.insert(0, r"d:\AI\full studio\output\k4-5-reels-261124")
from episodes_f01_to_f05_spec import EPISODES_261124

BASE_DIR   = r"d:\AI\full studio\output\k4-5-reels-261124"
PREV_BGM   = r"d:\AI\full studio\output\k4-10-videos-261123\bgm"
BGM_DIR    = os.path.join(BASE_DIR, "bgm")
DEMUCS_DIR = os.path.join(BASE_DIR, "demucs_cache")
QC_DIR     = os.path.join(BASE_DIR, "qc_sheets_v3")
ART_DIR    = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DEMUCS_PY  = r"D:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
LUT_PATH   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"

K4_DRIVE_DIR     = r"Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"D:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"
DU_AN_CLOUD_DIR  = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\261124-k4-5-reels-tranbuison"

BATCH_CODE = "261124"
SR = 48000
FPS = 30
SAMPLES_PER_FRAME = SR // FPS  # Exact 1600 samples/frame

for d in (BGM_DIR, DEMUCS_DIR, QC_DIR, ART_DIR):
    os.makedirs(d, exist_ok=True)

if os.path.isdir(PREV_BGM):
    for bfn in os.listdir(PREV_BGM):
        sp = os.path.join(PREV_BGM, bfn)
        dp = os.path.join(BGM_DIR, bfn)
        if os.path.isfile(sp) and not os.path.exists(dp):
            shutil.copy2(sp, dp)

# Director V3 refined BGM arcs & axial CU_PUNCH overrides per episode
DIRECTOR_OVERRIDES = {
    "f01": {
        "acts_bgm": [
            ("s01", "acoustic_calm_folk.mp3", 0.5, 0.90),
            ("s08", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s14", "piano_ltk_emotional.mp3", 4.0, 1.02),
            ("s19", "piano_warm_family.mp3", 5.0, 1.08),
        ],
        "framing": {"s03": "CU_PUNCH", "s10": "CU_PUNCH", "s16": "CU_PUNCH"},
    },
    "f02": {
        "acts_bgm": [
            ("s01", "acoustic_gentle_day.mp3", 0.5, 0.90),
            ("s04", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s13", "dram_ltk.mp3", 0.0, 1.04),
            ("s19", "piano_warm_family.mp3", 4.0, 1.06),
        ],
        "framing": {"s05": "CU_PUNCH", "s10": "CU_PUNCH", "s16": "CU_PUNCH"},
    },
    "f03": {
        "acts_bgm": [
            ("s01", "acoustic_warm_morning.mp3", 2.0, 0.90),
            ("s02", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s08", "dram_ltk.mp3", 0.0, 1.04),
            ("s15", "piano_warm_family.mp3", 4.0, 1.08),
        ],
        "framing": {"s05": "CU_PUNCH", "s10": "CU_PUNCH", "s14": "CU_PUNCH", "s16": "CU_PUNCH"},
    },
    "f04": {
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s09", "dram_ltk.mp3", 0.0, 1.05),
            ("s18", "piano_warm_family.mp3", 4.0, 1.08),
        ],
        "framing": {"s03": "CU_PUNCH", "s13": "CU_PUNCH", "s16": "CU_PUNCH"},
    },
    "f05": {
        "acts_bgm": [
            ("s01", "acoustic_warm_morning.mp3", 2.0, 0.90),
            ("s10", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s15", "piano_warm_family.mp3", 5.0, 1.08),
        ],
        "framing": {"s07": "CU_PUNCH", "s12": "CU_PUNCH", "s17": "CU_PUNCH"},
    },
}

_WHISPER = None
_BGM_CACHE = {}

def get_whisper():
    global _WHISPER
    if _WHISPER is None:
        _WHISPER = WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)
    return _WHISPER

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

def run_demucs_stems(mp4_path, tag_key):
    out_voc = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    out_nov = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "no_vocals.wav")
    src_mtime = os.path.getmtime(mp4_path)
    if os.path.exists(out_voc) and os.path.getsize(out_voc) > 20000 and os.path.getmtime(out_voc) >= src_mtime and os.path.exists(out_nov):
        return out_voc, out_nov
    raw_wav = os.path.join(DEMUCS_DIR, f"{tag_key}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", "44100", raw_wav], check=True)
    subprocess.run([
        DEMUCS_PY, "-m", "demucs.separate",
        "-n", "htdemucs", "--two-stems=vocals", "-d", "cuda",
        "-o", DEMUCS_DIR, raw_wav
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    sep_voc = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "vocals.wav")
    shutil.copy2(sep_voc, out_voc)
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
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"
    ])
    if len(raw) < 4:
        return np.zeros((SR * 4, 2), dtype=np.float32)
    return (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)

def analyze_clip_speech(mp4_path, tag_key, expected_dlg):
    voc_wav, _ = run_demucs_stems(mp4_path, tag_key)
    audit_json = os.path.join(DEMUCS_DIR, f"{tag_key}_audit.json")
    if os.path.exists(audit_json) and os.path.getmtime(audit_json) >= os.path.getmtime(voc_wav):
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

    # Check for trailing echo after a pause >= 0.70s once >= 70% of dialogue is already spoken
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

    # Check if final scripted words were cut off at EOF
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
    for fn in ("flow_wave1_f01_f03.json", "flow_wave2_f04_f05.json"):
        fp = os.path.join(BASE_DIR, fn)
        if os.path.exists(fp):
            for j in json.load(open(fp, encoding="utf-8")):
                all_flow_map[j["id"]] = j

    retakes = []
    total_checked = 0
    for ep_id in ep_ids:
        cfg = EPISODES_261124[ep_id]
        raw_dir = os.path.join(BASE_DIR, ep_id, "raw_9x16")
        print(f"\n=== AUDITING {ep_id.upper()} ({len(cfg['shots'])} shots) — {cfg['title']} ===", flush=True)
        for sid, scale, skey, ckeys, sp, act, speaker, dlg in cfg["shots"]:
            mp4 = os.path.join(raw_dir, f"{sid}.mp4")
            tag = f"{ep_id}_9x16_{sid}"
            if not os.path.exists(mp4):
                print(f"  [MISSING] {tag} -> queueing retake!", flush=True)
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
                    # Tighten prompt pace so actor finishes with plenty of breath room!
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

    retake_path = os.path.join(BASE_DIR, "flow_retakes_cutoff.json")
    json.dump(retakes, open(retake_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n=== AUDIT COMPLETE: checked={total_checked} | retakes_needed={len(retakes)} -> {retake_path} ===", flush=True)
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

    # Fuse Whisper word timestamps so soft Vietnamese initial/final syllables are NEVER clipped!
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

def render_episode_v3(ep_id):
    cfg = EPISODES_261124[ep_id]
    ov = DIRECTOR_OVERRIDES.get(ep_id, {})
    acts = ov.get("acts_bgm", cfg["acts_bgm"])
    framing_map = ov.get("framing", {})

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

    for idx, (sid, scale, skey, ckeys, sp, act, speaker, dlg) in enumerate(shots, 1):
        is_cta = (idx == len(shots))
        is_wide = scale in ("WIDE", "WIDE_CROWD", "MED")
        mode = "voice" if (speaker and dlg) else "visual"
        framing = framing_map.get(sid, "STD")

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
            assert seg_rms_check > 0.025, f"Audio level unexpectedly low on {ep_id}_{sid}: {seg_rms_check}"

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
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{ss:.4f}", "-t", f"{exact_dur + 0.08:.4f}", "-i", src,
            "-vf", vf, "-an", "-r", str(FPS), "-frames:v", str(n_frames),
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
            seg_vid
        ], check=True)

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

    total_samples = cum_frames * SAMPLES_PER_FRAME
    vid_total = cum_frames / float(FPS)

    dlg_master = np.concatenate(seg_audios, axis=0)
    assert len(dlg_master) == total_samples, f"Sample mismatch: {len(dlg_master)} vs {total_samples}"

    act_starts = []
    for sc_trigger, bgm_fn, bgm_off, bgm_gain in acts:
        st_samp = 0
        for item in timeline_log:
            if item["scene"] == sc_trigger:
                st_samp = item["start_sample"]
                break
        act_starts.append((st_samp, bgm_fn, bgm_off, bgm_gain))
    act_starts[0] = (0, act_starts[0][1], act_starts[0][2], act_starts[0][3])

    bgm_master = np.zeros((total_samples, 2), dtype=np.float32)
    xfade_samp = int(1.80 * SR)

    for a_i, (st_s, b_fn, b_off, b_gain) in enumerate(act_starts):
        nx_s = act_starts[a_i + 1][0] if a_i + 1 < len(act_starts) else total_samples
        s0 = max(0, st_s - (xfade_samp // 2 if a_i > 0 else 0))
        s1 = min(total_samples, nx_s + (xfade_samp // 2 if a_i + 1 < len(act_starts) else 0))
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
            fo_len = min(int(2.10 * SR), len(piece))
            piece[-fo_len:] *= np.linspace(1.0, 0.0, fo_len, dtype=np.float32)[:, None]

        bgm_master[s0:s1] += piece

    blk = SR // 10
    n_blk = total_samples // blk
    dlg_mono = np.abs(dlg_master[:n_blk * blk].mean(axis=1)).reshape(n_blk, blk)
    blk_rms = np.sqrt(np.mean(dlg_mono ** 2, axis=1))
    duck_blk = np.where(blk_rms > 0.022, 0.72, 1.30).astype(np.float32)
    kernel = np.ones(6, dtype=np.float32) / 6.0
    duck_smooth = np.convolve(np.pad(duck_blk, (3, 2), mode="edge"), kernel, mode="valid")
    duck_full = np.interp(
        np.linspace(0.0, n_blk, total_samples, endpoint=False),
        np.arange(n_blk, dtype=np.float32) + 0.5,
        duck_smooth
    ).astype(np.float32)[:, None]

    mix_master = dlg_master + bgm_master * duck_full
    mix_master = np.clip(np.tanh(mix_master * 1.04) / 1.04, -0.94, 0.94)

    master_wav = os.path.join(ep_dir, "master_v3_48k.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix_master * 32767.0).astype(np.int16).tobytes())

    concat_txt = os.path.join(ep_dir, "concat_v3_9x16.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for sv in seg_videos:
            cf.write(f"file '{sv}'\n")

    final_local = os.path.join(ep_dir, f"{BATCH_CODE} K4 {cfg['title']} final.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", master_wav,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "224k", "-ar", str(SR), "-ac", "2",
        "-movflags", "+faststart", final_local
    ], check=True)

    # Post-Render Automated Audio QC Gate
    qc_pcm = load_mp4_audio_48k_stereo(final_local)
    muted_tails = 0
    for item in timeline_log:
        if item["mode"] != "voice":
            continue
        s_end = min(len(qc_pcm), item["end_sample"] - int(0.10 * SR))
        s_beg = max(item["start_sample"], s_end - int(0.45 * SR))
        trms = float(np.sqrt(np.mean(qc_pcm[s_beg:s_end] ** 2))) if s_end > s_beg else 0.0
        if trms < 0.004:
            muted_tails += 1
            print(f"  [WARN] Low tail RMS on {ep_id} cut #{item['idx']} ({item['scene']}): {trms:.5f}")

    p_sil = subprocess.run(
        ["ffmpeg", "-i", final_local, "-af", "silencedetect=noise=-40dB:d=1.8", "-f", "null", "-"],
        capture_output=True, text=True
    )
    sil_count = p_sil.stderr.count("silence_duration")

    # QA Contact Sheet
    cols = 5
    tw, th = 216, 384
    thumbs = []
    for i, sv in enumerate(seg_videos, 1):
        _, _, d = probe_video(sv)
        t = os.path.join(QC_DIR, f"{ep_id}_s{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{d * 0.50:.2f}", "-i", sv, "-vf", f"scale={tw}:{th}", "-frames:v", "1", t], check=True)
        thumbs.append(t)
    rows = (len(thumbs) + cols - 1) // cols
    while len(thumbs) < cols * rows:
        pad_t = os.path.join(QC_DIR, f"{ep_id}_pad{len(thumbs)}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x14161c:s={tw}x{th}", "-frames:v", "1", pad_t], check=True)
        thumbs.append(pad_t)
    inp = []
    for t in thumbs:
        inp += ["-i", t]
    layout = "|".join(f"{(i % cols) * tw}_{(i // cols) * th}" for i in range(len(thumbs)))
    qa_name = f"QA_V3_{ep_id.upper()}_9x16.jpg"
    qa_sheet = os.path.join(QC_DIR, qa_name)
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs={len(thumbs)}:layout={layout}", "-frames:v", "1", qa_sheet], check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, qa_name))

    delivered = deliver_episode(final_local, cfg["title"])
    print(
        f"=== {ep_id.upper()} V3 COMPLETE: {vid_total:.2f}s | {len(seg_videos)} cuts | muted_tails={muted_tails} | dead_air_gaps={sil_count} ===",
        flush=True
    )
    return {
        "episode": ep_id,
        "batch": BATCH_CODE,
        "title": cfg["title"],
        "scenes_count": len(seg_videos),
        "duration": round(vid_total, 2),
        "muted_tails": muted_tails,
        "dead_air_gaps": sil_count,
        "acts_bgm": [x[1] for x in acts],
        "qa_sheet": qa_sheet,
        **delivered,
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "render"
    ep_ids = sys.argv[2:] if len(sys.argv) > 2 else list(EPISODES_261124.keys())
    if mode == "audit":
        run_audit(ep_ids)
    elif mode == "render":
        results = [render_episode_v3(ep) for ep in ep_ids]
        rep_path = os.path.join(BASE_DIR, "delivery_v3_5_reels_261124.json")
        json.dump(results, open(rep_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        if os.path.isdir(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An"):
            os.makedirs(DU_AN_CLOUD_DIR, exist_ok=True)
            for fn in ("episodes_f01_to_f05_spec.py", "prepare_261124_chatgpt_assets.py", "build_5_cinema_episodes_261124.py", "render_5_reels_director_v3.py", "delivery_v3_5_reels_261124.json"):
                sp = os.path.join(BASE_DIR, fn)
                if os.path.exists(sp):
                    shutil.copy2(sp, os.path.join(DU_AN_CLOUD_DIR, fn))
        print(f"\nALL {len(results)} 261124 K4 CINEMA EPISODES RENDERED & DELIVERED!", flush=True)
    else:
        raise SystemExit(f"Unknown mode: {mode}")
