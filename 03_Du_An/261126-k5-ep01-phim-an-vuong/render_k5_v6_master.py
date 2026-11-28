# -*- coding: utf-8 -*-
"""
Cinema Director V9 (`render_k5_v6_master.py` — K5 Tập 01 V6 Master):
1. 0% Fake White Boxes: Only scenes carrying `pr_2bojomi_nobag_1x1.jpg` show the 2 real `BOJOMI` boxes (`cu_boj_01..04`, `s01`, `s03`, `s10b`, `s17`). All other scenes enforce 100% clean empty tabletops.
2. Complete Physical Story Logic:
   - `s10`: Tuấn & Chị Hai Ngân return home seeing Thảo in tears.
   - `s10b`: Linh hears Tuấn, panics, grabs the 2 real `BOJOMI` boxes off the table and hides them behind her back at the corner cabinet!
   - `s11`: Bà Hạnh lies ("Má mới xin uống thử một ly...").
   - `s12`: Chị Hai Ngân spots Linh hiding something behind her back at the corner cabinet and points!
   - `s12b`: WIDE DYNAMIC GROUP SHOT — Tuấn & Thảo rush rapidly across the room to Linh's corner catching her red-handed!
   - `cu_boj_03` + `s13`: Tuấn pulls & sets the 2 real `BOJOMI` boxes onto the table and confronts Linh!
3. Dynamic Shot Scale Variety: Interleaves lively Wide/Medium-Long (`WS`/`MLS`) blocking shots (`s01`, `s03`, `s04`, `s09`, `s10`, `s10b`, `s12b`, `s17`) with `MCU` and emotional `CU`.
4. Clean Source First + Surgical Whisper De-Stutter Guard:
   - `audit` rejects any take with word repetitions (`1-gram..4-gram`), missing words, or EOF cutoffs so Flow re-shoots clean source.
   - `render` ALSO runs surgical zero-crossing de-stutter splicing (`remove_word_stutters_av`) if any residual micro-stutter exists, guaranteeing 0.0% word repetition!
5. Writes `timeline_cuts_v6.json` covering 100% of all cuts (Hook + Story + Live CU) for `video_qc_gate.py` & `video-qc-auditor` sign-off BEFORE delivery!
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel

BASE_DIR     = r"C:\AI\full studio\output\k5-ep01-v4"
K4_REF_BASE  = r"C:\AI\full studio\output\k4-20-reels-261126"
BGM_DIR      = os.path.join(K4_REF_BASE, "bgm")
DEMUCS_DIR   = os.path.join(BASE_DIR, "demucs_v6")
V6_RAW       = os.path.join(BASE_DIR, "raw_v6_master")
SEG_DIR      = os.path.join(BASE_DIR, "seg_v9_9x16")
QC_DIR       = os.path.join(BASE_DIR, "qc_sheets_v9")
DEMUCS_PY    = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
LUT_PATH     = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"

K5_DRIVE_DIR      = r"G:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K5 - Phim An Vượng"
MASTER_CLOUD_DIR  = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR  = r"C:\XUẤT CAPCUT\K5 - Phim An Vượng"
PROJECT_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\03_Du_An\261126-k5-ep01-phim-an-vuong"

BATCH_CODE = "261127"
BRAND_PREFIX = "K5"
SR = 48000
FPS = 30
SAMPLES_PER_FRAME = SR // FPS

for d in (DEMUCS_DIR, SEG_DIR, QC_DIR, PROJECT_CLOUD_DIR):
    os.makedirs(d, exist_ok=True)

_WHISPER = None
_BGM_CACHE = {}

V6_STORY = {
    "title": "Con dâu khóc nghẹn mất hai hộp sữa chị gái tặng và màn chồng bắt em chồng trả quà xin lỗi tại chỗ",
    "acts_bgm": [
        ("s01",  "acoustic_warm_morning.mp3", 1.0, 0.86),
        ("s03",  "dram_quiet_tension.mp3",    1.5, 0.94),
        ("s08",  "piano_ltk_emotional.mp3",   2.0, 1.02),
        ("s10",  "dram_ltk.mp3",              0.0, 1.06),
        ("s17",  "piano_warm_family.mp3",     4.0, 1.06),
    ],
    "hook_scenes": ["s04", "s06", "s08"],
    "live_cu_inserts": {
        "s02":  ("cu_boj_01", "tail", 2.30),
        "s06":  ("cu_boj_02", "head", 2.10),
        "s07":  ("cu_boj_04", "tail", 2.20),
        "s12b": ("cu_boj_03", "tail", 2.40),
    },
    "shots": [
        ("s01",  "MLS", "Thấy em thức khuya chăm con đau mỏi lưng gối, chị Hai mua hai hộp Bojomi này qua bồi bổ cho em nè."),
        ("s02",  "CU",  "Em cảm ơn chị Hai nhiều lắm, để em tiễn chị Hai ra thang máy rồi vô pha uống liền nghen."),
        ("s03",  "WS",  "Alo Linh hả con gái! Qua nhà má lẹ lên con, chị vợ thằng Tuấn mới đem qua hai hộp Bojomi xịn lắm nè!"),
        ("s04",  "WS",  "Ủa má ơi, hai hộp sữa Bojomi chị Hai mới đem qua cho con để đây đâu mất tiêu rồi má?"),
        ("s05",  "CU",  "Ai thèm rớ tới đồ của cô mà hỏi! Tự cất đâu quên rồi tính đổ thừa cho má chồng hả?!"),
        ("s06",  "MCU", "Công nhận sữa hạt Bojomi của chị Thảo uống thơm thanh thiệt đó má, thảo nào một hộp hơn năm trăm ngàn!"),
        ("s07",  "CU",  "Con gái má cành vàng lá ngọc mới xứng uống canxi tảo biển, lát con đem nguyên hai hộp đó về uống luôn đi!"),
        ("s08",  "CU",  "Đồ chị Hai thương em cực nhọc mới mua cho, vậy mà má cũng lén lấy cho cô Linh hết trơn."),
        ("s09",  "WS",  "Tao lấy cho con gái ruột tao uống đó rồi sao?! Bước vô nhà này thì cái gì cũng của nhà này, vô bếp đi!"),
        ("s10",  "MLS", "Có chuyện gì mà ồn ào dưới bếp vậy má? Sao mắt vợ con đỏ hoe hết trơn vầy nè?"),
        ("s10b", "MLS", "Chết rồi, anh Hai về bất thình lình, phải lén giấu hai hộp này ra sau lưng mới được!"),
        ("s11",  "CU",  "Vợ mày ích kỷ lắm Tuấn ơi! Má mới xin uống thử một ly mà nó gào khóc hỗn hào với má kìa!"),
        ("s12",  "MCU", "Bác kêu chỉ xin thử một ly, vậy cô Linh đang nép góc tủ lén giấu cái gì sau lưng kia vậy bác?!"),
        ("s12b", "WS",  "Đứng lại đó Linh! Đưa ngay cái thứ em đang lén giấu sau lưng ra đây cho anh coi!"),
        ("s13",  "MCU", "Cái gì đây Linh?! Nguyên hai hộp Bojomi của chị dâu em lén giấu đem về mà còn hùa nhau vu oan cho Thảo hả?!"),
        ("s14",  "CU",  "Dạ đâu phải em tự lấy đâu anh Hai, chính má lấy giấu của chị Thảo rồi gọi em qua đem về đó chứ!"),
        ("s15",  "CU",  "Linh! Bưng ngay hai hộp đó bằng hai tay trả lại cho chị Thảo rồi cúi đầu xin lỗi chị dâu liền trước mặt anh!"),
        ("s16",  "MCU", "Em xin lỗi chị Hai Ngân, em xin lỗi chị Thảo, từ nay em không dám tham lam lấy đồ của chị nữa."),
        ("s17",  "WS",  "Từ nay trong nhà này ai còn ức hiếp Thảo là tui đưa vợ ra ở riêng ngay! Tui xử lý vậy đã hợp tình hợp lý chưa cô chú anh chị?"),
    ],
}

ALLOWED_1GRAM = {"từ", "đều", "luôn", "rất", "lăm", "nhiều", "ngày", "đời", "người", "ai", "cười", "khóc", "vừa"}


def get_whisper():
    global _WHISPER
    if _WHISPER is None:
        _WHISPER = WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)
    return _WHISPER


def norm_words(s):
    return [w for w in re.sub(r"[^\w\s]", " ", s.lower()).split() if len(w) > 1]


def word_overlap_ratio(expected, actual):
    ew, aw = set(norm_words(expected)), set(norm_words(actual))
    return 1.0 if not ew else len(ew & aw) / float(len(ew))


def detect_word_stutters(words: list) -> list:
    """Returns list of duplicate word-index ranges `(dup_start_idx, dup_end_idx, phrase)` for adjacent 1..4-gram repeats."""
    norm = [re.sub(r"[^\w]", "", w["w"].lower()) for w in words]
    dups = []
    used = set()
    for n in (4, 3, 2):
        for k in range(len(norm) - 2 * n + 1):
            if any(i in used for i in range(k, k + 2 * n)):
                continue
            if all(norm[k:k + n]) and norm[k:k + n] == norm[k + n:k + 2 * n]:
                if words[k + n]["s"] - words[k + n - 1]["e"] <= 1.80:
                    dups.append((k + n, k + 2 * n - 1, " ".join(x["w"] for x in words[k + n:k + 2 * n])))
                    used.update(range(k, k + 2 * n))
    for k in range(len(norm) - 1):
        if k in used or (k + 1) in used:
            continue
        if norm[k] and len(norm[k]) >= 2 and norm[k] == norm[k + 1] and norm[k] not in ALLOWED_1GRAM:
            if words[k + 1]["s"] - words[k]["e"] <= 1.50:
                dups.append((k + 1, k + 1, words[k + 1]["w"]))
                used.update([k, k + 1])
    dups.sort(key=lambda x: x[0])
    return dups


def is_valid_mp4_video(p):
    if not os.path.exists(p) or os.path.getsize(p) < 80000:
        return False
    try:
        with open(p, "rb") as f:
            if f.read(12)[4:8] != b"ftyp":
                return False
        j = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name:format=duration", "-of", "json", p
        ]).decode("utf-8"))
        return j["streams"][0].get("codec_name") in ("h264", "hevc", "vp9", "av1") and float(j["format"]["duration"]) >= 2.0
    except Exception:
        return False


def probe_video(p):
    j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration", "-of", "json", p
    ]).decode("utf-8"))
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])


def has_audio_stream(p):
    try:
        j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_type", "-of", "json", p]).decode("utf-8"))
        return len(j.get("streams", [])) > 0
    except Exception:
        return False


def run_demucs_stems(mp4_path, tag_key):
    out_voc = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    out_nov = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "no_vocals.wav")
    if os.path.exists(out_voc) and os.path.getsize(out_voc) > 20000 and os.path.getmtime(out_voc) >= os.path.getmtime(mp4_path) and os.path.exists(out_nov):
        return out_voc, out_nov
    raw_wav = os.path.join(DEMUCS_DIR, f"{tag_key}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", "44100", raw_wav], check=True)
    rc = subprocess.run([DEMUCS_PY, "-m", "demucs.separate", "-n", "htdemucs", "--two-stems=vocals", "-d", "cuda", "-o", DEMUCS_DIR, raw_wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    if rc != 0:
        subprocess.run([DEMUCS_PY, "-m", "demucs.separate", "-n", "htdemucs", "--two-stems=vocals", "-d", "cpu", "-o", DEMUCS_DIR, raw_wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    shutil.copy2(os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "vocals.wav"), out_voc)
    return out_voc, out_nov


def load_wav_48k_stereo(wav_path):
    with wave.open(wav_path, "rb") as wf:
        sr, nch = wf.getframerate(), wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    pcm = np.column_stack([pcm, pcm]) if nch == 1 else pcm.reshape(-1, nch)[:, :2]
    if sr != SR:
        n_out = int(round(len(pcm) * SR / float(sr)))
        xo = np.linspace(0.0, 1.0, len(pcm), endpoint=False)
        xn = np.linspace(0.0, 1.0, n_out, endpoint=False)
        pcm = np.column_stack([np.interp(xn, xo, pcm[:, 0]).astype(np.float32), np.interp(xn, xo, pcm[:, 1]).astype(np.float32)])
    return pcm


def analyze_clip_speech(mp4_path, tag_key, expected_dlg, strict_stutter_retake=True):
    if not has_audio_stream(mp4_path):
        _, _, d = probe_video(mp4_path)
        return {"tag": tag_key, "total_dur": round(d, 3), "cutoff": True, "reason": "NO_AUDIO", "expected": expected_dlg, "transcript": "", "words": [], "stutters": []}
    voc_wav, _ = run_demucs_stems(mp4_path, tag_key)
    audit_json = os.path.join(DEMUCS_DIR, f"{tag_key}_audit.json")
    if os.path.exists(audit_json) and os.path.getmtime(audit_json) >= os.path.getmtime(mp4_path):
        cached = json.load(open(audit_json, encoding="utf-8"))
        if "stutters" in cached:
            return cached

    _, _, total_dur = probe_video(mp4_path)
    voc_st = load_wav_48k_stereo(voc_wav)
    mono = voc_st.mean(axis=1)
    ws = 0.020
    win = int(SR * ws)
    nf = len(mono) // win
    rms = np.sqrt(np.mean(mono[:nf * win].reshape(nf, win) ** 2, axis=1))
    peak = float(np.max(rms[3:])) if len(rms) > 3 else 0.0
    end_rms = float(np.mean(rms[-7:])) if len(rms) >= 7 else 0.0

    segs, _ = get_whisper().transcribe(voc_wav, language="vi", word_timestamps=True, vad_filter=False, beam_size=2)
    words = [{"s": round(float(w.start), 3), "e": round(float(w.end), 3), "w": w.word.strip()} for s in segs for w in (s.words or []) if w.word.strip()]
    transcript = " ".join(w["w"] for w in words)
    ov = word_overlap_ratio(expected_dlg, transcript)

    auto_force_to = None
    if len(words) >= 5 and expected_dlg:
        for i in range(3, len(words) - 1):
            if words[i + 1]["s"] - words[i]["e"] >= 0.72:
                prefix_txt = " ".join(x["w"] for x in words[:i + 1])
                tail_txt = " ".join(x["w"] for x in words[i + 1:])
                if word_overlap_ratio(expected_dlg, prefix_txt) >= 0.72 and len(norm_words(tail_txt)) <= 5:
                    auto_force_to = round(min(total_dur - 0.05, words[i]["e"] + 0.28), 3)
                    words = words[:i + 1]
                    transcript = prefix_txt
                    ov = word_overlap_ratio(expected_dlg, transcript)
                    break

    stutters = detect_word_stutters(words)
    w_start = words[0]["s"] if words else 0.20
    w_end = words[-1]["e"] if words else min(total_dur - 0.3, 2.5)
    tail_margin = round(total_dur - w_end, 3)
    exp_norm, act_norm = norm_words(expected_dlg), norm_words(transcript)
    tail_expected = set(exp_norm[-2:]) if len(exp_norm) >= 2 else set(exp_norm)
    tail_actual = set(act_norm[-4:]) if act_norm else set()
    missing_ending = (len(tail_expected & tail_actual) == 0) and (tail_margin < 0.45)

    cutoff, reason = False, "OK"
    if peak < 0.020 or ov < 0.56:
        cutoff, reason = True, f"LOW_SPEECH_OR_MISMATCH (peak={peak:.3f}, ov={ov:.2f})"
    elif (tail_margin < 0.16 and end_rms > 0.012) or missing_ending:
        cutoff, reason = True, f"EOF_CUTOFF (tail_margin={tail_margin:.2f}s, end_rms={end_rms:.4f})"
    elif strict_stutter_retake and len(stutters) > 0:
        cutoff, reason = True, f"WORD_STUTTER ({[s[2] for s in stutters]})"

    res = {
        "tag": tag_key, "total_dur": round(total_dur, 3), "peak": round(peak, 4), "end_rms": round(end_rms, 4),
        "w_start": round(w_start, 3), "w_end": round(w_end, 3), "tail_margin": tail_margin,
        "overlap": round(ov, 2), "auto_force_to": auto_force_to, "stutters": stutters,
        "cutoff": cutoff, "reason": reason,
        "expected": expected_dlg, "transcript": transcript, "words": words,
    }
    json.dump(res, open(audit_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


def surgically_destutter_raw_mp4(mp4_path: str, words: list, stutters: list) -> bool:
    """If a clip still has minor word stutter(s) after retake attempts, surgically slices out
    the repeated word span(s) at breath valleys on both video and audio so 0% stutter remains!"""
    if not stutters:
        return False
    _, _, total_dur = probe_video(mp4_path)
    cut_ranges = []
    for i0, i1, phrase in stutters:
        # Cut from end of previous word (+20ms breath) to start of word after duplicate (-15ms)
        prev_e = words[i0 - 1]["e"] if i0 > 0 else words[i0]["s"]
        next_s = words[i1 + 1]["s"] if (i1 + 1) < len(words) else (words[i1]["e"] + 0.04)
        c0 = round(max(0.0, prev_e + 0.02), 3)
        c1 = round(min(total_dur, max(c0 + 0.12, next_s - 0.015)), 3)
        cut_ranges.append((c0, c1, phrase))

    keep_spans = []
    cur = 0.0
    for c0, c1, _ in cut_ranges:
        if c0 - cur >= 0.15:
            keep_spans.append((cur, c0))
        cur = max(cur, c1)
    if total_dur - cur >= 0.15:
        keep_spans.append((cur, total_dur))

    if len(keep_spans) <= 1 and not cut_ranges:
        return False

    tmp_out = mp4_path + ".destut.mp4"
    vf_parts, af_parts, concat_in = [], [], []
    for idx, (ks, ke) in enumerate(keep_spans):
        vf_parts.append(f"[0:v]trim=start={ks:.3f}:end={ke:.3f},setpts=PTS-STARTPTS[v{idx}]")
        af_parts.append(f"[0:a]atrim=start={ks:.3f}:end={ke:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.015,afade=t=out:st={max(0.0, ke - ks - 0.018):.3f}:d=0.015[a{idx}]")
        concat_in.append(f"[v{idx}][a{idx}]")

    fc = ";".join(vf_parts + af_parts) + ";" + "".join(concat_in) + f"concat=n={len(keep_spans)}:v=1:a=1[vout][aout]"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", mp4_path,
        "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "224k", tmp_out
    ], check=True)
    shutil.move(tmp_out, mp4_path)
    print(f"  [SURGICAL DE-STUTTER] Cut repeated spans {cut_ranges} -> {os.path.basename(mp4_path)}", flush=True)
    return True


def audit_v6(allow_surgical_destutter=False):
    v6_spec = json.load(open(os.path.join(BASE_DIR, "flow_k5ep01_v6_master.json"), encoding="utf-8"))
    v5_spec = json.load(open(os.path.join(BASE_DIR, "flow_k5ep01_v5_nobag.json"), encoding="utf-8"))
    v4_spec = json.load(open(os.path.join(BASE_DIR, "flow_k5ep01_v4.json"), encoding="utf-8"))
    flow_map = {}
    for sp in (v4_spec, v5_spec, v6_spec):
        for j in sp:
            flow_map[j["scene"]] = j

    retakes = []
    print("\n=== AUDITING V6 MASTER CLIPS (19 Story + 4 Live BOJOMI CU) ===", flush=True)
    for sc, (cid, _, _) in V6_STORY["live_cu_inserts"].items():
        mp4 = os.path.join(V6_RAW, f"{cid}.mp4")
        if not is_valid_mp4_video(mp4):
            print(f"  [MISSING LIVE CU] {cid} -> queueing retake!", flush=True)
            rj = dict(flow_map[cid])
            rj["outPath"] = mp4
            rj["overwrite"] = True
            retakes.append(rj)
        else:
            _, _, d = probe_video(mp4)
            print(f"  [LIVE CU OK] {cid}: {d:.2f}s", flush=True)

    for sid, scale, dlg in V6_STORY["shots"]:
        mp4 = os.path.join(V6_RAW, f"{sid}.mp4")
        tag = f"k5v6_9x16_{sid}"
        if not is_valid_mp4_video(mp4):
            if os.path.exists(mp4):
                try:
                    os.remove(mp4)
                except Exception:
                    pass
            print(f"  [MISSING ACTOR MP4] {sid} ({scale}) -> queueing!", flush=True)
            rj = dict(flow_map[sid])
            rj["outPath"] = mp4
            rj["overwrite"] = True
            retakes.append(rj)
            continue

        info = analyze_clip_speech(mp4, tag, dlg, strict_stutter_retake=True)
        if info["cutoff"] and allow_surgical_destutter and info["reason"].startswith("WORD_STUTTER") and info.get("stutters"):
            # Try surgical de-stutter when allowed on final retry pass
            if surgically_destutter_raw_mp4(mp4, info["words"], info["stutters"]):
                # Clear cached demucs/audit so it re-verifies cleanly
                for f in glob.glob(os.path.join(DEMUCS_DIR, f"{tag}*")):
                    if os.path.isfile(f):
                        os.remove(f)
                shutil.rmtree(os.path.join(DEMUCS_DIR, "htdemucs", tag), ignore_errors=True)
                info = analyze_clip_speech(mp4, tag, dlg, strict_stutter_retake=True)

        if info["cutoff"]:
            print(f"  [RETAKE NEEDED] {sid} ({scale}): {info['reason']}\n     EXP: {dlg}\n     ACT: {info['transcript']}", flush=True)
            rj = dict(flow_map[sid])
            rj["outPath"] = mp4
            rj["overwrite"] = True
            retakes.append(rj)
        else:
            print(f"  [OK] {sid:4s} ({scale:3s}): ov={info['overlap']:.2f} | stutters=0 | {info['w_start']:.2f}..{info['w_end']:.2f}s / {info['total_dur']:.2f}s", flush=True)

    retake_path = os.path.join(BASE_DIR, "flow_retakes_k5v6.json")
    json.dump(retakes, open(retake_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n=== V6 AUDIT COMPLETE: retakes_needed={len(retakes)} -> {retake_path} ===", flush=True)
    return retakes


def detect_letterbox_bars(mp4_path, w, h, t_mid):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", mp4_path, "-frames:v", "1", "-pix_fmt", "gray", "-f", "rawvideo", "-"])
    row_means = np.frombuffer(raw, dtype=np.uint8).reshape((h, w)).mean(axis=1)
    top_b, bot_b = 0, 0
    while top_b < h // 5 and row_means[top_b] < 16.0:
        top_b += 1
    while bot_b < h // 5 and row_means[h - 1 - bot_b] < 16.0:
        bot_b += 1
    return (((top_b + 1) // 2) * 2 if top_b >= 4 else 0), (((bot_b + 1) // 2) * 2 if bot_b >= 4 else 0)


def encode_mobile_segment(src_mp4, ss, n_frames, out_mp4, framing="STD"):
    w, h, _ = probe_video(src_mp4)
    exact_dur = n_frames / float(FPS)
    target_ar = 9.0 / 16.0
    lut_ff = LUT_PATH.replace("\\", "/").replace(":", "\\:")
    vf_parts = []
    if w == 720 and h == 1280:
        vf_parts.append("delogo=x=570:y=1130:w=62:h=62")
    top_b, bot_b = detect_letterbox_bars(src_mp4, w, h, ss + exact_dur * 0.5)
    ch_crop = h - top_b - bot_b
    cw_crop, cx_crop, cy_crop = w, 0, top_b
    cur_ar = cw_crop / float(ch_crop)
    if cur_ar > target_ar + 0.005:
        new_w = (int(round(ch_crop * target_ar)) // 2) * 2
        cx_crop += (cw_crop - new_w) // 2
        cw_crop = new_w
    elif cur_ar < target_ar - 0.005:
        new_h = (int(round(cw_crop / target_ar)) // 2) * 2
        cy_crop += (ch_crop - new_h) // 2
        ch_crop = new_h

    # IMPORTANT: Wide/Medium-Long shots (`WS`/`MLS` -> framing="WIDE") keep 100% full wide field-of-view!
    if framing == "CU_PUNCH":
        zw = (int(round(cw_crop * 0.90)) // 2) * 2
        zh = (int(round(ch_crop * 0.90)) // 2) * 2
        cx_crop += (cw_crop - zw) // 2
        cy_crop += int(round((ch_crop - zh) * 0.24))
        cw_crop, ch_crop = zw, zh

    if cw_crop != w or ch_crop != h or cx_crop != 0 or cy_crop != 0:
        vf_parts.append(f"crop={cw_crop}:{ch_crop}:{cx_crop}:{cy_crop}")
    vf_parts.extend([
        "scale=1080:1920:flags=lanczos",
        f"lut3d=file='{lut_ff}':interp=trilinear",
        "eq=contrast=1.03:saturation=1.05:brightness=0.01",
        "unsharp=3:3:0.35:3:3:0.0",
        f"fps={FPS}",
        "format=yuv420p",
    ])
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.4f}", "-i", src_mp4,
        "-frames:v", str(n_frames), "-an", "-vf", ",".join(vf_parts),
        "-c:v", "libx264", "-preset", "medium", "-crf", "17",
        "-video_track_timescale", "15360", out_mp4
    ], check=True)


def load_bgm_48k_prepared(bgm_filename):
    if bgm_filename in _BGM_CACHE:
        return _BGM_CACHE[bgm_filename]
    src = os.path.join(BGM_DIR, bgm_filename)
    prep_wav = os.path.join(DEMUCS_DIR, f"bgm48_{os.path.splitext(bgm_filename)[0]}.wav")
    if not os.path.exists(prep_wav):
        af = "highpass=f=55,lowpass=f=12500,equalizer=f=1800:t=q:w=1.1:g=-4.5,loudnorm=I=-28.5:TP=-3.0:LRA=8.0"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vn", "-af", af, "-ac", "2", "-ar", str(SR), prep_wav], check=True)
    _BGM_CACHE[bgm_filename] = load_wav_48k_stereo(prep_wav)
    return _BGM_CACHE[bgm_filename]


def get_looped_bgm_slice(bgm_pcm, start_sec, needed_samples):
    pos = int(round(start_sec * SR)) % len(bgm_pcm)
    chunks, rem = [], needed_samples
    xf = int(1.5 * SR)
    while rem > 0:
        take = min(rem, len(bgm_pcm) - pos)
        part = bgm_pcm[pos:pos + take].copy()
        if chunks and len(part) > xf and len(chunks[-1]) > xf:
            t = np.linspace(0.0, 1.0, xf, dtype=np.float32)[:, None]
            chunks[-1][-xf:] = chunks[-1][-xf:] * (1.0 - t) + part[:xf] * t
            part = part[xf:]
        chunks.append(part)
        rem -= len(part)
        pos = (pos + take) % len(bgm_pcm)
    return np.concatenate(chunks, axis=0)[:needed_samples]


def extract_highlight_whisper_complete(src_seg_mp4, src_dlg_pcm, clip_words, ss_trim, min_sec=2.60, max_sec=5.40):
    total_frames = int(round(len(src_dlg_pcm) / float(SAMPLES_PER_FRAME)))
    total_dur = total_frames / float(FPS)
    rel_words = [{"s": round(w["s"] - ss_trim, 3), "e": round(w["e"] - ss_trim, 3), "w": w["w"]} for w in clip_words if w["e"] > ss_trim + 0.05]
    chosen_dur = total_dur
    if total_dur > max_sec and len(rel_words) >= 4:
        best_cut = None
        for idx in range(2, len(rel_words) - 1):
            w_cur, w_nxt = rel_words[idx], rel_words[idx + 1]
            gap = w_nxt["s"] - w_cur["e"]
            has_punct = any(p in w_cur["w"] for p in (",", ".", "!", "?", ";", ":"))
            cand_t = w_cur["e"] + min(0.18, gap * 0.65)
            if min_sec <= cand_t <= max_sec and (gap >= 0.26 or (has_punct and gap >= 0.16)):
                best_cut = cand_t
        chosen_dur = best_cut if best_cut is not None else total_dur

    n_frames = max(int(FPS * 2.0), min(total_frames, int(round(chosen_dur * FPS))))
    n_samples = n_frames * SAMPLES_PER_FRAME
    return src_seg_mp4, n_frames, src_dlg_pcm[:n_samples].copy()


def build_cold_open_hook(hook_scenes, actor_only_vids, seg_audios, timeline_log):
    sc_map = {}
    for idx, it in enumerate(timeline_log):
        sc_map[it["scene"]] = (actor_only_vids[idx], seg_audios[idx], it["words"], it["ss"])

    hook_vids, hook_auds, hook_cuts_meta = [], [], []
    cur_t = 0.0
    for h_i, sc in enumerate(hook_scenes):
        src_v, src_a, c_words, ss_trim = sc_map[sc]
        _, n_f, pcm = extract_highlight_whisper_complete(src_v, src_a, c_words, ss_trim, min_sec=2.60, max_sec=5.40)
        hv = os.path.join(SEG_DIR, f"00_hook_{h_i + 1:02d}_{sc}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", src_v, "-frames:v", str(n_f), "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
            "-video_track_timescale", "15360", hv
        ], check=True)
        fi = min(int(0.04 * SR), len(pcm) // 6)
        fo = min(int(0.10 * SR), len(pcm) // 5)
        pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        pcm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
        dur_s = n_f / float(FPS)
        print(f"  [HOOK #{h_i + 1} {sc}] complete clause = {dur_s:.2f}s", flush=True)
        hook_vids.append(hv)
        hook_auds.append(pcm)
        hook_cuts_meta.append({"start": round(cur_t, 3), "end": round(cur_t + dur_s, 3), "label": f"hook_{sc}"})
        cur_t += dur_s

    flash_frames = 8
    flash_dur = flash_frames / float(FPS)
    flash_v = os.path.join(SEG_DIR, "00_hook_99_flash.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x121010:s=1080x1920:r={FPS}",
        "-frames:v", str(flash_frames), "-vf", "format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-video_track_timescale", "15360", flash_v
    ], check=True)
    hook_vids.append(flash_v)
    hook_auds.append(np.zeros((flash_frames * SAMPLES_PER_FRAME, 2), dtype=np.float32))
    hook_cuts_meta.append({"start": round(cur_t, 3), "end": round(cur_t + flash_dur, 3), "label": "hook_flash"})
    cur_t += flash_dur

    dlg_hook = np.concatenate(hook_auds, axis=0)
    total_hook = len(dlg_hook)
    t_bgm = get_looped_bgm_slice(load_bgm_48k_prepared("dram_ltk.mp3"), 1.0, total_hook) * 0.92

    blk = SR // 10
    n_blk = total_hook // blk
    blk_rms = np.sqrt(np.mean(np.abs(dlg_hook[:n_blk * blk].mean(axis=1)).reshape(n_blk, blk) ** 2, axis=1))
    duck_sm = np.convolve(np.pad(np.where(blk_rms > 0.022, 0.58, 1.15).astype(np.float32), (2, 2), mode="edge"), np.ones(5, dtype=np.float32) / 5.0, mode="valid")
    duck_full = np.interp(np.linspace(0.0, n_blk, total_hook, endpoint=False), np.arange(n_blk, dtype=np.float32) + 0.5, duck_sm).astype(np.float32)[:, None]

    mix_h = dlg_hook + t_bgm * duck_full
    fo_all = int(0.24 * SR)
    mix_h[-fo_all:] *= np.linspace(1.0, 0.0, fo_all, dtype=np.float32)[:, None]
    return hook_vids, np.clip(np.tanh(mix_h * 1.05) / 1.05, -0.94, 0.94), hook_cuts_meta, round(cur_t, 3)


def render_v9_master():
    retakes = audit_v6(allow_surgical_destutter=True)
    if retakes:
        raise RuntimeError(f"ABORT: {len(retakes)} clips still failed V6 audit!")

    for old_f in glob.glob(os.path.join(SEG_DIR, "*.mp4")):
        os.remove(old_f)

    shots = V6_STORY["shots"]
    live_inserts = V6_STORY["live_cu_inserts"]
    seg_videos_flat, actor_only_vids, seg_audios, timeline_log = [], [], [], []
    story_cuts_meta = []
    cur_samples = 0

    for idx, (sid, scale, dlg) in enumerate(shots):
        raw_mp4 = os.path.join(V6_RAW, f"{sid}.mp4")
        tag = f"k5v6_9x16_{sid}"
        info = analyze_clip_speech(raw_mp4, tag, dlg, strict_stutter_retake=True)
        voc_wav, nov_wav = run_demucs_stems(raw_mp4, tag)
        voc_pcm = load_wav_48k_stereo(voc_wav)
        nov_pcm = load_wav_48k_stereo(nov_wav)
        total_dur = info["total_dur"]

        if sid in ("s03", "s10b", "s12b"):
            ss = 0.06
        else:
            ss = max(0.0, info["w_start"] - (0.34 if idx == 0 else 0.14))
        ee = info["auto_force_to"] if info.get("auto_force_to") else min(total_dur, info["w_end"] + (0.75 if idx == len(shots) - 1 else 0.24))
        if ee - ss < 2.10:
            ee = min(total_dur, ss + 2.20)
        n_frames = max(45, int(round((ee - ss) * FPS)))
        if ss + n_frames / float(FPS) > total_dur:
            n_frames = int(math.floor((total_dur - ss) * FPS))
        n_samples = n_frames * SAMPLES_PER_FRAME

        # Framing: preserve 100% wide field-of-view on WS/MLS, alternate subtle punch on tight CU
        if scale in ("WS", "MLS"):
            framing = "WIDE"
        elif scale == "CU" and (idx % 2 == 0):
            framing = "CU_PUNCH"
        else:
            framing = "STD"

        act_full_mp4 = os.path.join(SEG_DIR, f"actor_{idx + 1:02d}_{sid}.mp4")
        encode_mobile_segment(raw_mp4, ss, n_frames, act_full_mp4, framing=framing)
        actor_only_vids.append(act_full_mp4)

        cur_sec_before = cur_samples / float(SR)
        if sid in live_inserts:
            cu_id, mode, ins_sec = live_inserts[sid]
            cu_raw = os.path.join(V6_RAW, f"{cu_id}.mp4")
            _, _, cu_total = probe_video(cu_raw)
            ins_frames = min(int(round(ins_sec * FPS)), int(math.floor((cu_total - 0.30) * FPS)), n_frames - 36)
            rem_frames = n_frames - ins_frames
            cu_ss = max(0.15, (cu_total - ins_frames / float(FPS)) * 0.40)

            if mode == "tail":
                p1_mp4 = os.path.join(SEG_DIR, f"{idx + 1:02d}a_{sid}.mp4")
                p2_mp4 = os.path.join(SEG_DIR, f"{idx + 1:02d}b_{cu_id}_live.mp4")
                encode_mobile_segment(raw_mp4, ss, rem_frames, p1_mp4, framing=framing)
                encode_mobile_segment(cu_raw, cu_ss, ins_frames, p2_mp4, framing="STD")
                seg_videos_flat.extend([p1_mp4, p2_mp4])
                d1 = rem_frames / float(FPS)
                d2 = ins_frames / float(FPS)
                story_cuts_meta.append({"start": round(cur_sec_before, 3), "end": round(cur_sec_before + d1, 3), "label": sid})
                story_cuts_meta.append({"start": round(cur_sec_before + d1, 3), "end": round(cur_sec_before + d1 + d2, 3), "label": cu_id})
            else:
                p1_mp4 = os.path.join(SEG_DIR, f"{idx + 1:02d}a_{cu_id}_live.mp4")
                p2_mp4 = os.path.join(SEG_DIR, f"{idx + 1:02d}b_{sid}.mp4")
                encode_mobile_segment(cu_raw, cu_ss, ins_frames, p1_mp4, framing="STD")
                encode_mobile_segment(raw_mp4, ss + ins_frames / float(FPS), rem_frames, p2_mp4, framing=framing)
                seg_videos_flat.extend([p1_mp4, p2_mp4])
                d1 = ins_frames / float(FPS)
                d2 = rem_frames / float(FPS)
                story_cuts_meta.append({"start": round(cur_sec_before, 3), "end": round(cur_sec_before + d1, 3), "label": cu_id})
                story_cuts_meta.append({"start": round(cur_sec_before + d1, 3), "end": round(cur_sec_before + d1 + d2, 3), "label": sid})
        else:
            seg_videos_flat.append(act_full_mp4)
            d_full = n_frames / float(FPS)
            story_cuts_meta.append({"start": round(cur_sec_before, 3), "end": round(cur_sec_before + d_full, 3), "label": sid})

        s0 = int(round(ss * SR))
        v_sl = voc_pcm[s0:s0 + n_samples]
        n_sl = nov_pcm[s0:s0 + n_samples]
        if len(v_sl) < n_samples:
            v_sl = np.vstack([v_sl, np.zeros((n_samples - len(v_sl), 2), dtype=np.float32)])
        if len(n_sl) < n_samples:
            n_sl = np.vstack([n_sl, np.zeros((n_samples - len(n_sl), 2), dtype=np.float32)])

        p98 = float(np.percentile(np.abs(v_sl), 98.5))
        gain = min(2.35, max(0.85, 0.34 / p98)) if p98 > 0.012 else 1.0
        dlg_clean = v_sl * gain + n_sl * 0.045
        fi = min(int(0.04 * SR), n_samples // 6)
        fo = min(int(0.06 * SR), n_samples // 6)
        dlg_clean[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        dlg_clean[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
        seg_audios.append(dlg_clean)

        t0_s = cur_samples / float(SR)
        t1_s = (cur_samples + n_samples) / float(SR)
        timeline_log.append({
            "scene": sid, "scale": scale, "ss": round(ss, 3), "words": info["words"],
            "start_sample": cur_samples, "end_sample": cur_samples + n_samples,
        })
        print(f"  [{idx + 1:02d}_{sid}:{scale}:{framing}] {t0_s:6.2f}s -> {t1_s:6.2f}s ({t1_s - t0_s:.2f}s)", flush=True)
        cur_samples += n_samples

    hook_vids, hook_pcm, hook_cuts_meta, hook_dur_sec = build_cold_open_hook(
        V6_STORY["hook_scenes"], actor_only_vids, seg_audios, timeline_log
    )

    # Build complete 100%-cuts timeline JSON (Hook + Story + Live CU) for `video_qc_gate.py`
    all_cuts_json_list = list(hook_cuts_meta)
    for sc_it in story_cuts_meta:
        all_cuts_json_list.append({
            "start": round(hook_dur_sec + sc_it["start"], 3),
            "end": round(hook_dur_sec + sc_it["end"], 3),
            "label": sc_it["label"],
        })
    cuts_json_path = os.path.join(BASE_DIR, "timeline_cuts_v6.json")
    json.dump(all_cuts_json_list, open(cuts_json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    story_samples = timeline_log[-1]["end_sample"]
    dlg_story = np.concatenate(seg_audios, axis=0)
    act_starts = []
    for sc_trigger, bgm_fn, bgm_off, bgm_gain in V6_STORY["acts_bgm"]:
        st_samp = next((it["start_sample"] for it in timeline_log if it["scene"] == sc_trigger), 0)
        act_starts.append((st_samp, bgm_fn, bgm_off, bgm_gain))
    act_starts[0] = (0, act_starts[0][1], act_starts[0][2], act_starts[0][3])

    bgm_story = np.zeros((story_samples, 2), dtype=np.float32)
    xfade_samp = int(1.80 * SR)
    for a_i, (st_s, b_fn, b_off, b_gain) in enumerate(act_starts):
        nx_s = act_starts[a_i + 1][0] if a_i + 1 < len(act_starts) else story_samples
        s0 = max(0, st_s - (xfade_samp // 2 if a_i > 0 else 0))
        s1 = min(story_samples, nx_s + (xfade_samp // 2 if a_i + 1 < len(act_starts) else 0))
        if s1 <= s0:
            continue
        piece = get_looped_bgm_slice(load_bgm_48k_prepared(b_fn), b_off, s1 - s0) * float(b_gain)
        if a_i > 0:
            fi_l = min(xfade_samp, len(piece))
            piece[:fi_l] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi_l, dtype=np.float32)))[:, None]
        else:
            fi_l = min(int(0.65 * SR), len(piece))
            piece[:fi_l] *= np.linspace(0.0, 1.0, fi_l, dtype=np.float32)[:, None]
        if a_i + 1 < len(act_starts):
            fo_l = min(xfade_samp, len(piece))
            piece[-fo_l:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo_l, dtype=np.float32)))[:, None]
        else:
            fo_l = min(int(2.10 * SR), len(piece))
            piece[-fo_l:] *= np.linspace(1.0, 0.0, fo_l, dtype=np.float32)[:, None]
        bgm_story[s0:s1] += piece

    blk = SR // 10
    n_blk = story_samples // blk
    blk_rms = np.sqrt(np.mean(np.abs(dlg_story[:n_blk * blk].mean(axis=1)).reshape(n_blk, blk) ** 2, axis=1))
    duck_sm = np.convolve(np.pad(np.where(blk_rms > 0.022, 0.68, 1.28).astype(np.float32), (3, 2), mode="edge"), np.ones(6, dtype=np.float32) / 6.0, mode="valid")
    duck_full = np.interp(np.linspace(0.0, n_blk, story_samples, endpoint=False), np.arange(n_blk, dtype=np.float32) + 0.5, duck_sm).astype(np.float32)[:, None]

    mix_story = np.clip(np.tanh((dlg_story + bgm_story * duck_full) * 1.04) / 1.04, -0.94, 0.94)
    mix_master = np.concatenate([hook_pcm, mix_story], axis=0)
    vid_total = len(mix_master) / float(SR)

    all_concat_vids = list(hook_vids) + list(seg_videos_flat)
    master_wav = os.path.join(BASE_DIR, "master_v9_48k.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix_master * 32767.0).astype(np.int16).tobytes())

    concat_txt = os.path.join(BASE_DIR, "concat_v9_9x16.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for sv in all_concat_vids:
            cf.write(f"file '{sv}'\n")

    fname = f"{BATCH_CODE} {BRAND_PREFIX} {V6_STORY['title']} final.mp4"
    final_local = os.path.join(BASE_DIR, fname)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-i", master_wav,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "224k", "-ar", str(SR), "-ac", "2",
        "-movflags", "+faststart", final_local
    ], check=True)

    _, _, mux_dur = probe_video(final_local)
    print(f"  [V9 MASTER RENDERED LOCALLY — AWAITING VIDEO QC GATE!] Audio={vid_total:.2f}s | Video={mux_dur:.2f}s | Cuts={len(all_concat_vids)} | HookEnd={hook_dur_sec:.2f}s", flush=True)
    print(f"  Local Candidate -> {final_local}", flush=True)
    print(f"  Cuts JSON       -> {cuts_json_path}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "audit"
    if cmd == "audit":
        audit_v6(allow_surgical_destutter=False)
    elif cmd == "audit_destutter":
        audit_v6(allow_surgical_destutter=True)
    elif cmd == "render":
        render_v9_master()
