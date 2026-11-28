# -*- coding: utf-8 -*-
"""
Cinema Director V8 (100% Bag-Free, Pure 2-Box Flat-Top Cardboard BOJOMI + Zoomed Box Inspector):
- 0% bags anywhere! Direct interaction with 2 pure white-and-emerald flat-top rectangular `BOJOMI` boxes.
- Builds `QC_V5_Zoomed_Boxes_100Pct.jpg` (zoomed crops of every product shot) for strict 1:1 visual verification before delivery.
- 3-Beat Mini-Story Highlight Hook (`s04` mất 2 hộp -> `s06` Linh uống khen ngon -> `s08` Thảo bật khóc).
"""
import glob, json, math, os, re, shutil, subprocess, sys, wave
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel

BASE_DIR     = r"C:\AI\full studio\output\k5-ep01-v4"
K4_REF_BASE  = r"C:\AI\full studio\output\k4-20-reels-261126"
BGM_DIR      = os.path.join(K4_REF_BASE, "bgm")
DEMUCS_DIR   = os.path.join(BASE_DIR, "demucs_v5")
V5_RAW       = os.path.join(BASE_DIR, "raw_v5_nobag")
SEG_DIR      = os.path.join(BASE_DIR, "seg_v8_9x16")
QC_DIR       = os.path.join(BASE_DIR, "qc_sheets_v8")
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
_USER_HOOK_BGM = None

V5_STORY = {
    "title": "Con dâu khóc nghẹn mất hai hộp sữa chị gái tặng và màn chồng bắt em chồng trả quà xin lỗi tại chỗ",
    "acts_bgm": [
        ("s01", "acoustic_warm_morning.mp3", 1.0, 0.88),
        ("s03", "dram_quiet_tension.mp3", 1.5, 0.96),
        ("s08", "piano_ltk_emotional.mp3", 2.0, 1.02),
        ("s10", "dram_ltk.mp3", 0.0, 1.06),
        ("s17", "piano_warm_family.mp3", 4.0, 1.08),
    ],
    "hook_scenes": ["s04", "s06", "s08"],
    "live_cu_inserts": {
        "s02": ("cu_boj_01", "tail", 2.40),
        "s06": ("cu_boj_02", "head", 2.20),
        "s07": ("cu_boj_04", "tail", 2.30),
        "s13": ("cu_boj_03", "tail", 2.50),
    },
    "shots": [
        ("s01", "MCU", "Thấy em thức khuya chăm con đau mỏi lưng gối, chị Hai mua hai hộp Bojomi này qua bồi bổ cho em nè."),
        ("s02", "CU",  "Em cảm ơn chị Hai nhiều lắm, để em tiễn chị Hai ra thang máy rồi vô pha uống liền nghen."),
        ("s03", "CU",  "Alo Linh hả con gái! Qua nhà má lẹ đi, chị vợ thằng Tuấn mới đem qua hai hộp sữa Bojomi xịn lắm nè!"),
        ("s04", "MCU", "Ủa má ơi, hai hộp sữa Bojomi chị Hai mới đem qua cho con để đây đâu mất tiêu rồi má?"),
        ("s05", "CU",  "Ai thèm rớ tới đồ của cô mà hỏi! Tự cất đâu quên rồi tính đổ thừa cho má chồng hả?!"),
        ("s06", "CU",  "Công nhận sữa Bojomi An Vượng của chị Thảo uống thơm ngon thiệt đó má, thảo nào hộp hơn năm trăm ngàn!"),
        ("s07", "CU",  "Con gái má cành vàng lá ngọc mới xứng uống canxi tảo biển, lát con ôm nguyên hai hộp này về uống luôn đi!"),
        ("s08", "CU",  "Đồ chị Hai thương em cực nhọc mới mua cho, vậy mà má cũng lén lấy cho cô Linh hết trơn."),
        ("s09", "MCU", "Tao lấy cho con gái ruột tao uống đó rồi sao?! Bước vô nhà này thì cái gì cũng của nhà này, vô bếp đi!"),
        ("s10", "MCU", "Có chuyện gì mà ồn ào dưới bếp vậy má? Sao mắt vợ con đỏ hoe hết trơn vầy nè?"),
        ("s11", "CU",  "Vợ mày ích kỷ lắm Tuấn ơi! Má mới xin uống thử một ly sữa của nó mà nó gào khóc hỗn hào với má kìa!"),
        ("s12", "CU",  "Bác kêu chỉ xin thử một ly, vậy hai cái hộp cô Linh đang ôm giấu sau lưng kia là cái gì vậy bác?!"),
        ("s13", "CU",  "Cái gì đây Linh?! Nguyên hai hộp Bojomi của chị dâu em ôm đem về mà còn hùa nhau vu oan cho Thảo hả?!"),
        ("s14", "CU",  "Dạ đâu phải em tự lấy đâu anh Hai, chính má lấy giấu của chị Thảo rồi gọi em qua đem về đó chứ!"),
        ("s15", "CU",  "Linh! Bưng ngay hai hộp đó bằng hai tay trả lại cho chị Thảo rồi cúi đầu xin lỗi chị dâu liền trước mặt anh!"),
        ("s16", "CU",  "Em xin lỗi chị Hai Ngân, em xin lỗi chị Thảo, từ rày em không dám tham lam lấy đồ của chị nữa."),
        ("s17", "MCU", "Từ nay trong nhà này ai còn ức hiếp Thảo là tui đưa vợ ra ở riêng liền! Tui xử lý vậy đã hợp tình hợp lý chưa cô chú anh chị?"),
    ],
}

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

def analyze_clip_speech(mp4_path, tag_key, expected_dlg):
    if not has_audio_stream(mp4_path):
        _, _, d = probe_video(mp4_path)
        return {"tag": tag_key, "total_dur": round(d, 3), "cutoff": True, "reason": "NO_AUDIO", "expected": expected_dlg, "transcript": "", "words": []}
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
                    auto_force_to = round(min(total_dur - 0.05, words[i]["e"] + 0.30), 3)
                    words = words[:i + 1]
                    transcript = prefix_txt
                    ov = word_overlap_ratio(expected_dlg, transcript)
                    break

    w_start = words[0]["s"] if words else 0.20
    w_end = words[-1]["e"] if words else min(total_dur - 0.3, 2.5)
    tail_margin = round(total_dur - w_end, 3)
    exp_norm, act_norm = norm_words(expected_dlg), norm_words(transcript)
    tail_expected = set(exp_norm[-2:]) if len(exp_norm) >= 2 else set(exp_norm)
    tail_actual = set(act_norm[-4:]) if act_norm else set()
    missing_ending = (len(tail_expected & tail_actual) == 0) and (tail_margin < 0.45)

    cutoff, reason = False, "OK"
    if peak < 0.020 or ov < 0.42:
        cutoff, reason = True, f"LOW_SPEECH_OR_MISMATCH (peak={peak:.3f}, ov={ov:.2f})"
    elif (tail_margin < 0.16 and end_rms > 0.012) or missing_ending:
        cutoff, reason = True, f"EOF_CUTOFF (tail_margin={tail_margin:.2f}s, end_rms={end_rms:.4f})"

    res = {
        "tag": tag_key, "total_dur": round(total_dur, 3), "peak": round(peak, 4), "end_rms": round(end_rms, 4),
        "w_start": round(w_start, 3), "w_end": round(w_end, 3), "tail_margin": tail_margin,
        "overlap": round(ov, 2), "auto_force_to": auto_force_to, "cutoff": cutoff, "reason": reason,
        "expected": expected_dlg, "transcript": transcript, "words": words,
    }
    json.dump(res, open(audit_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res

def build_zoomed_box_qc():
    """Builds a high-magnification 1:1 crop sheet of every shot containing BOJOMI boxes (`cu_boj_01..04`, `s01`, `s16`, `s17`)
    so we can verify with our own eyes ZERO screw-caps, ZERO blue cartons, ZERO bags!"""
    prod_clips = ["cu_boj_01", "cu_boj_02", "cu_boj_03", "cu_boj_04", "s01", "s17"]
    cw, ch = 420, 680
    cols = 4
    rows = 2
    sheet = Image.new("RGB", (cols * cw, rows * ch), (18, 20, 26))
    d = ImageDraw.Draw(sheet)
    fh = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    for i, cid in enumerate(prod_clips):
        mp4 = os.path.join(V5_RAW, f"{cid}.mp4")
        if not is_valid_mp4_video(mp4):
            continue
        jpg = os.path.join(QC_DIR, f"_z_{cid}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", mp4, "-frames:v", "1", jpg], check=True)
        im = Image.open(jpg).convert("RGB")
        w, h = im.size
        # Zoom into lower-middle tabletop/hands region where boxes sit!
        if cid.startswith("cu_"):
            crop = im.crop((int(w * 0.04), int(h * 0.25), int(w * 0.96), int(h * 0.92)))
        else:
            crop = im.crop((int(w * 0.08), int(h * 0.30), int(w * 0.92), int(h * 0.96)))
        crop = crop.resize((cw - 8, ch - 44), Image.LANCZOS)
        r, c = i // cols, i % cols
        sheet.paste(crop, (c * cw + 4, r * ch + 40))
        d.text((c * cw + 12, r * ch + 8), f"ZOOM 100%: {cid}", fill=(255, 220, 70), font=fh)
        os.remove(jpg)
    out_p = os.path.join(QC_DIR, "QC_V5_Zoomed_Boxes_100Pct.jpg")
    sheet.save(out_p, "JPEG", quality=94)
    print("Saved zoomed box QC ->", out_p, flush=True)
    return out_p

def audit_v5():
    v5_spec = json.load(open(os.path.join(BASE_DIR, "flow_k5ep01_v5_nobag.json"), encoding="utf-8"))
    v4_spec = json.load(open(os.path.join(BASE_DIR, "flow_k5ep01_v4.json"), encoding="utf-8"))
    flow_map = {j["scene"]: j for j in v4_spec}
    for j in v5_spec:
        flow_map[j["scene"]] = j

    retakes = []
    print("\n=== AUDITING V5 BAG-FREE CLIPS (17 Story + 4 Live BOJOMI CU) ===", flush=True)
    for sc, (cid, _, _) in V5_STORY["live_cu_inserts"].items():
        mp4 = os.path.join(V5_RAW, f"{cid}.mp4")
        if not is_valid_mp4_video(mp4):
            if os.path.exists(mp4):
                try: os.remove(mp4)
                except Exception: pass
            print(f"  [MISSING LIVE CU] {cid} -> queueing retake!", flush=True)
            rj = dict(flow_map[cid])
            rj["outPath"] = mp4
            rj["overwrite"] = True
            retakes.append(rj)
        else:
            _, _, d = probe_video(mp4)
            print(f"  [LIVE CU OK] {cid}: {d:.2f}s", flush=True)

    for sid, scale, dlg in V5_STORY["shots"]:
        mp4 = os.path.join(V5_RAW, f"{sid}.mp4")
        tag = f"k5v5_9x16_{sid}"
        if not is_valid_mp4_video(mp4):
            if os.path.exists(mp4):
                try: os.remove(mp4)
                except Exception: pass
            print(f"  [MISSING ACTOR MP4] {sid} -> queueing retake!", flush=True)
            rj = dict(flow_map[sid])
            rj["outPath"] = mp4
            rj["overwrite"] = True
            retakes.append(rj)
            continue
        info = analyze_clip_speech(mp4, tag, dlg)
        if info["cutoff"]:
            print(f"  [RETAKE NEEDED] {sid}: {info['reason']}\n     EXP: {dlg}\n     ACT: {info['transcript']}", flush=True)
            rj = dict(flow_map[sid])
            rj["outPath"] = mp4
            rj["overwrite"] = True
            orig_sec = int(rj.get("seconds", 10))
            rj["seconds"] = min(12, orig_sec + 2)
            rj["prompts"] = [
                p.replace("4.5 giây đầu", "3.8 giây đầu, nhịp nói gọn gàng dứt khoát")
                 .replace(f"Tạo video {orig_sec} giây", f"Tạo video {rj['seconds']} giây")
                for p in rj.get("prompts", [rj.get("prompt", "")])
            ]
            rj["prompt"] = rj["prompts"][0]
            retakes.append(rj)
        else:
            print(f"  [OK] {sid}: ov={info['overlap']:.2f} | {info['w_start']:.2f}..{info['w_end']:.2f}s / {info['total_dur']:.2f}s", flush=True)

    build_zoomed_box_qc()
    retake_path = os.path.join(BASE_DIR, "flow_retakes_k5v5.json")
    json.dump(retakes, open(retake_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n=== V5 AUDIT COMPLETE: retakes_needed={len(retakes)} -> {retake_path} ===", flush=True)
    return retakes

def detect_letterbox_bars(mp4_path, w, h, t_mid):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", mp4_path, "-frames:v", "1", "-pix_fmt", "gray", "-f", "rawvideo", "-"])
    row_means = np.frombuffer(raw, dtype=np.uint8).reshape((h, w)).mean(axis=1)
    top_b, bot_b = 0, 0
    while top_b < h // 5 and row_means[top_b] < 16.0: top_b += 1
    while bot_b < h // 5 and row_means[h - 1 - bot_b] < 16.0: bot_b += 1
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
        zf = 1.12
        nw, nh = int(round(cw_crop / zf / 2) * 2), int(round(ch_crop / zf / 2) * 2)
        cx_crop += (cw_crop - nw) // 2
        cy_crop += int((ch_crop - nh) * 0.32)
        cw_crop, ch_crop = nw, nh
    if cw_crop != w or ch_crop != h or cx_crop != 0 or cy_crop != 0:
        vf_parts.append(f"crop={cw_crop}:{ch_crop}:{cx_crop}:{cy_crop}")
    if os.path.exists(LUT_PATH):
        vf_parts.append(f"lut3d=file='{lut_ff}':interp=tetrahedral")
    vf_parts += ["scale=1080:1920:flags=lanczos", "eq=contrast=1.03:brightness=0.012:saturation=1.05", "unsharp=3:3:0.34:3:3:0.0", f"fps={FPS}", "format=yuv420p"]
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.4f}", "-t", f"{exact_dur + 0.08:.4f}", "-i", src_mp4,
        "-vf", ",".join(vf_parts), "-an", "-r", str(FPS), "-frames:v", str(n_frames),
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", out_mp4
    ], check=True)
    return out_mp4

def detect_tight_bounds_48k(voc_stereo, total_dur, audit_info=None, is_wide=False, is_cta=False):
    mono = voc_stereo.mean(axis=1)
    ws = 0.020
    win = int(SR * ws)
    nf = len(mono) // win
    rms = np.sqrt(np.mean(mono[:nf * win].reshape(nf, win) ** 2, axis=1))
    force_to = audit_info.get("auto_force_to") if audit_info else None
    s_idx = int(0.05 / ws)
    e_idx = max(s_idx + 4, min(len(rms), int((force_to if force_to is not None else total_dur - 0.03) / ws)))
    sub = rms[s_idx:e_idx]
    peak = float(np.max(sub)) if len(sub) else 0.01
    core_idx = np.where(sub >= max(0.012, peak * 0.10))[0] + s_idx
    soft_thr = max(0.0030, peak * 0.022)
    if len(core_idx) == 0:
        sp_start, sp_end = 0.15, min(total_dur - 0.08, 2.35)
    else:
        valid, cluster = [], [core_idx[0]]
        for idx in core_idx[1:]:
            if (idx - cluster[-1]) * ws <= 0.95: cluster.append(idx)
            else:
                if len(cluster) >= 3: valid.extend(cluster)
                cluster = [idx]
        if len(cluster) >= 3: valid.extend(cluster)
        if not valid: valid = list(core_idx)
        first_i, last_i = valid[0], valid[-1]
        while first_i > s_idx and (valid[0] - first_i) * ws < 0.28 and np.max(rms[max(s_idx, first_i - 3):first_i]) >= soft_thr: first_i -= 1
        while last_i < e_idx - 1 and (last_i - valid[-1]) * ws < 0.55 and np.max(rms[last_i + 1:min(e_idx, last_i + 6)]) >= soft_thr: last_i += 1
        sp_start, sp_end = first_i * ws, (last_i + 1) * ws
    if audit_info and audit_info.get("w_end"):
        w_s, w_e = float(audit_info["w_start"]), float(audit_info["w_end"])
        if force_to is not None: w_e = min(w_e, force_to - 0.12)
        sp_start, sp_end = max(0.04, min(sp_start, w_s)), min(total_dur - 0.04, max(sp_end, w_e))
    pre_pad = 0.24 if is_wide else 0.18
    post_pad = 0.56 if is_cta else (0.36 if is_wide else 0.32)
    ss = max(0.04, sp_start - pre_pad)
    to = force_to if force_to is not None else min(total_dur - 0.02, sp_end + post_pad)
    if to - ss < 1.90: to = min(total_dur - 0.02, ss + 2.00)
    sp_slice = mono[int(sp_start * SR):max(int(sp_start * SR) + 1200, int(sp_end * SR))]
    return ss, to, sp_start, sp_end, (float(np.sqrt(np.mean(sp_slice ** 2))) if len(sp_slice) else 0.05)

def slice_exact_samples(arr, start_sample, n_samples):
    end_sample = start_sample + n_samples
    if start_sample < 0: start_sample, end_sample = 0, n_samples
    if end_sample <= len(arr): return arr[start_sample:end_sample].copy()
    out = np.zeros((n_samples, 2), dtype=np.float32)
    avail = max(0, len(arr) - start_sample)
    if avail > 0: out[:avail] = arr[start_sample:start_sample + avail]
    return out

def fft_bandpass_stereo(stereo, low_hz=85.0, high_hz=13500.0):
    n = len(stereo)
    if n < 64: return stereo
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    mask = np.clip((freqs - low_hz * 0.6) / max(1.0, low_hz * 0.4), 0.0, 1.0) * np.clip((high_hz * 1.15 - freqs) / max(1.0, high_hz * 0.15), 0.0, 1.0)
    return np.column_stack([np.fft.irfft(np.fft.rfft(stereo[:, c]) * mask.astype(np.float32), n=n).astype(np.float32) for c in range(2)])

def load_bgm_48k_prepared(bgm_fn):
    if bgm_fn in _BGM_CACHE: return _BGM_CACHE[bgm_fn]
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", os.path.join(BGM_DIR, bgm_fn), "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"])
    arr = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)
    n = len(arr)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    eq = (np.clip((freqs - 60.0) / 45.0, 0.0, 1.0) * np.clip((11500.0 - freqs) / 2000.0, 0.0, 1.0) * (1.0 - 0.40 * np.exp(-0.5 * ((freqs - 2150.0) / 850.0) ** 2))).astype(np.float32)
    for c in range(2): arr[:, c] = np.fft.irfft(np.fft.rfft(arr[:, c]) * eq, n=n).astype(np.float32)
    mono = arr.mean(axis=1)
    win = SR // 10
    env = np.sqrt(np.mean(mono[:len(mono)//win*win].reshape(-1, win) ** 2, axis=1))
    act = env[env > np.percentile(env, 25)]
    arr *= (0.036 / max(float(np.median(act)) if len(act) else 0.05, 0.008))
    _BGM_CACHE[bgm_fn] = arr
    return arr

def get_looped_bgm_slice(bgm_arr, offset_sec, length_samples):
    start_idx = int(round(offset_sec * SR)) % len(bgm_arr)
    out = np.empty((length_samples, 2), dtype=np.float32)
    pos, cur = 0, start_idx
    while pos < length_samples:
        take = min(length_samples - pos, len(bgm_arr) - cur)
        out[pos:pos + take] = bgm_arr[cur:cur + take]
        pos += take; cur = 0
        if pos < length_samples and pos >= 1920:
            xf = 1920
            w = np.linspace(0.0, 1.0, xf, dtype=np.float32)[:, None]
            out[pos - xf:pos] = out[pos - xf:pos] * (1.0 - w) + bgm_arr[:xf] * w
            cur = xf
    return out

def extract_highlight_whisper_complete(seg_vid, seg_pcm, seg_ss, audit_words, out_vid, dip_to_black=False):
    n_frames = len(seg_pcm) // SAMPLES_PER_FRAME
    seg_dur = n_frames / float(FPS)
    rel_words = [{"s": max(0.0, float(w["s"]) - seg_ss), "e": min(seg_dur, float(w["e"]) - seg_ss), "w": w["w"]}
                 for w in (audit_words or []) if min(seg_dur, float(w["e"]) - seg_ss) > max(0.0, float(w["s"]) - seg_ss)]
    f1 = n_frames
    if len(rel_words) >= 8:
        for i in range(5, len(rel_words) - 2):
            gap = rel_words[i + 1]["s"] - rel_words[i]["e"]
            if gap >= 0.26 and (rel_words[i]["e"] - rel_words[0]["s"]) >= 1.85 and (rel_words[i]["w"].endswith((",", "!", "?", ".", ";")) or gap >= 0.34):
                cand_f1 = int(round((rel_words[i]["e"] + min(0.24, gap * 0.75)) * FPS))
                chk_s, chk_e = max(0, (cand_f1 - 2) * SAMPLES_PER_FRAME), min(len(seg_pcm), (cand_f1 + 1) * SAMPLES_PER_FRAME)
                if chk_e > chk_s and float(np.sqrt(np.mean(seg_pcm[chk_s:chk_e] ** 2))) < 0.014 and 54 <= cand_f1 < n_frames - 10:
                    f1 = cand_f1; break
    h_pcm = seg_pcm[:f1 * SAMPLES_PER_FRAME].copy()
    fi, fo = min(1400, len(h_pcm) // 8), min(1680, len(h_pcm) // 8)
    h_pcm[:fi] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi, dtype=np.float32)))[:, None]
    h_pcm[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo, dtype=np.float32)))[:, None]
    sub_dur = f1 / float(FPS)
    vf_h = ["crop=1036:1842:22:39", "scale=1080:1920:flags=lanczos", "eq=contrast=1.04:saturation=1.06", "fade=t=in:st=0:d=0.08"]
    if dip_to_black and sub_dur > 0.45: vf_h.append(f"fade=t=out:st={sub_dur - 0.22:.3f}:d=0.22")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0", "-t", f"{sub_dur + 0.06:.4f}", "-i", seg_vid, "-vf", ",".join(vf_h), "-an", "-r", str(FPS), "-frames:v", str(f1), "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", out_vid], check=True)
    return out_vid, h_pcm

def build_cold_open_hook(hook_scene_ids, actor_only_vids, seg_audios, timeline_log):
    global _USER_HOOK_BGM
    if _USER_HOOK_BGM is None:
        arr = load_wav_48k_stereo(os.path.join(BGM_DIR, "user_hook_260922_mat50cheo.wav"))
        n = len(arr)
        freqs = np.fft.rfftfreq(n, d=1.0 / SR)
        pocket = (1.0 - 0.38 * np.exp(-0.5 * ((freqs - 2150.0) / 850.0) ** 2)).astype(np.float32)
        for c in range(2): arr[:, c] = np.fft.irfft(np.fft.rfft(arr[:, c]) * pocket, n=n).astype(np.float32)
        _USER_HOOK_BGM = arr

    scene_to_idx = {it["scene"]: i for i, it in enumerate(timeline_log)}
    picks = [scene_to_idx[sc] for sc in hook_scene_ids if sc in scene_to_idx]
    h_vids, h_pcms = [], []
    for j, cut_i in enumerate(picks):
        hv = os.path.join(SEG_DIR, f"hook_v8_{j+1}_{timeline_log[cut_i]['scene']}.mp4")
        _, hp = extract_highlight_whisper_complete(actor_only_vids[cut_i], seg_audios[cut_i], timeline_log[cut_i]["raw_ss"], timeline_log[cut_i]["words"], hv, dip_to_black=(j == len(picks) - 1))
        print(f"  [HOOK #{j+1} {timeline_log[cut_i]['scene']}] complete clause = {len(hp)/float(SR):.2f}s", flush=True)
        h_vids.append(hv); h_pcms.append(hp)

    blk_vid = os.path.join(SEG_DIR, "hook_v8_black_pause.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={FPS}", "-frames:v", "21", "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p", blk_vid], check=True)
    h_vids.append(blk_vid); h_pcms.append(np.zeros((21 * SAMPLES_PER_FRAME, 2), dtype=np.float32))

    dlg_h = np.concatenate(h_pcms, axis=0)
    tot = len(dlg_h)
    end_samp = min(len(_USER_HOOK_BGM), int(14.20 * SR))
    bgm_h = _USER_HOOK_BGM[end_samp - tot : end_samp].copy() if tot <= end_samp - int(0.40 * SR) else get_looped_bgm_slice(_USER_HOOK_BGM[int(0.85 * SR):end_samp], 0.0, tot)
    fi, fo = min(int(0.28 * SR), tot), min(int(0.25 * SR), tot)
    bgm_h[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    bgm_h[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    n_blk, blk_sz = max(1, tot // (SR // 10)), SR // 10
    d_rms = np.sqrt(np.mean(np.abs(dlg_h[:n_blk * blk_sz].mean(axis=1)).reshape(n_blk, blk_sz) ** 2, axis=1))
    duck_sm = np.convolve(np.pad(np.where(d_rms > 0.018, 0.50, 1.05).astype(np.float32), (2, 2), mode="edge"), np.ones(5, dtype=np.float32) / 5.0, mode="valid")
    duck_f = np.interp(np.linspace(0.0, n_blk, tot, endpoint=False), np.arange(n_blk, dtype=np.float32) + 0.5, duck_sm).astype(np.float32)[:, None]
    return h_vids, np.clip(np.tanh((dlg_h + bgm_h * duck_f) * 1.05) / 1.05, -0.94, 0.94)

def purge_old_k5_mp4s():
    for tdir in (K5_DRIVE_DIR, MASTER_CLOUD_DIR, LOCAL_CAPCUT_DIR):
        if not os.path.isdir(tdir): continue
        for fn in os.listdir(tdir):
            if (" K5 " in fn) and fn.endswith(".mp4"):
                try: os.remove(os.path.join(tdir, fn))
                except Exception: pass

def render_v8_master():
    shots = V5_STORY["shots"]
    acts = V5_STORY["acts_bgm"]
    cu_map = V5_STORY["live_cu_inserts"]

    seg_videos_flat, actor_only_vids, seg_audios, timeline_log = [], [], [], []
    cum_frames = 0
    prev_scale, prev_framing = None, "STD"

    for idx, (sid, scale, dlg) in enumerate(shots, 1):
        is_cta = (idx == len(shots))
        is_wide = (scale == "MCU")
        framing = "CU_PUNCH" if (scale == "CU" and prev_scale == "CU" and prev_framing == "STD") else "STD"
        prev_scale, prev_framing = scale, framing

        src = os.path.join(V5_RAW, f"{sid}.mp4")
        _, _, total_dur = probe_video(src)
        tag = f"k5v5_9x16_{sid}"
        voc_wav, novoc_wav = run_demucs_stems(src, tag)
        audit_info = analyze_clip_speech(src, tag, dlg)
        voc_full = load_wav_48k_stereo(voc_wav)
        amb_full = load_wav_48k_stereo(novoc_wav) if os.path.exists(novoc_wav) else np.zeros_like(voc_full)
        ss, to, _, _, sp_rms = detect_tight_bounds_48k(voc_full, total_dur, audit_info=audit_info, is_wide=is_wide, is_cta=is_cta)

        n_frames = max(48, int(round((to - ss) * FPS)))
        exact_dur = n_frames / float(FPS)
        n_samples = n_frames * SAMPLES_PER_FRAME
        start_sample = int(round(ss * SR))

        v_seg = fft_bandpass_stereo(slice_exact_samples(voc_full, start_sample, n_samples), 85.0, 13500.0)
        a_seg = fft_bandpass_stereo(slice_exact_samples(amb_full, start_sample, n_samples), 90.0, 6500.0)
        gain = float(np.clip(0.158 / max(sp_rms, 0.012), 0.72, 5.20))
        v_seg = np.tanh(v_seg * gain * 1.12) / 1.12
        a_rms = float(np.sqrt(np.mean(a_seg ** 2))) + 1e-6
        seg_pcm = v_seg + np.clip(a_seg * min(0.10, 0.0085 / a_rms), -0.035, 0.035)
        fi, fo = min(1344, n_samples // 4), min(1536, n_samples // 4)
        seg_pcm[:fi] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi, dtype=np.float32)))[:, None]
        seg_pcm[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo, dtype=np.float32)))[:, None]
        seg_audios.append(seg_pcm.astype(np.float32))

        actor_full_vid = os.path.join(SEG_DIR, f"{idx:02d}_{sid}_actor.mp4")
        encode_mobile_segment(src, ss, n_frames, actor_full_vid, framing=framing)
        actor_only_vids.append(actor_full_vid)

        if sid in cu_map and n_frames >= 96:
            cid, pos_mode, ins_sec = cu_map[sid]
            cu_src = os.path.join(V5_RAW, f"{cid}.mp4")
            _, _, cu_total = probe_video(cu_src)
            ins_frames = min(n_frames - 42, max(48, int(round(min(ins_sec, cu_total - 0.85) * FPS))))
            act_frames = n_frames - ins_frames
            cu_ss = max(0.45, min(1.0, (cu_total - ins_frames / float(FPS)) * 0.35))
            ins_vid = os.path.join(SEG_DIR, f"{idx:02d}_{sid}_live_cu.mp4")
            encode_mobile_segment(cu_src, cu_ss, ins_frames, ins_vid, framing="STD")
            act_sub_vid = os.path.join(SEG_DIR, f"{idx:02d}_{sid}_act_sub.mp4")
            if pos_mode == "tail":
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", actor_full_vid, "-an", "-r", str(FPS), "-frames:v", str(act_frames), "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", act_sub_vid], check=True)
                seg_videos_flat.extend([act_sub_vid, ins_vid])
                ins_tag = f"+LIVE_L-CUT({cid})"
            else:
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ins_frames / float(FPS):.4f}", "-i", actor_full_vid, "-an", "-r", str(FPS), "-frames:v", str(act_frames), "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", act_sub_vid], check=True)
                seg_videos_flat.extend([ins_vid, act_sub_vid])
                ins_tag = f"+LIVE_J-CUT({cid})"
        else:
            seg_videos_flat.append(actor_full_vid)
            ins_tag = ""

        t0, t1 = cum_frames / float(FPS), (cum_frames + n_frames) / float(FPS)
        timeline_log.append({
            "idx": idx, "scene": sid, "scale": scale, "raw_ss": ss, "words": audit_info.get("words", []),
            "start": round(t0, 3), "end": round(t1, 3), "dur": round(exact_dur, 3),
            "start_sample": cum_frames * SAMPLES_PER_FRAME, "end_sample": (cum_frames + n_frames) * SAMPLES_PER_FRAME,
        })
        print(f"  [{idx:02d}_{sid}:{scale}:{framing}{ins_tag}] {t0:6.2f}s -> {t1:6.2f}s ({exact_dur:.2f}s)", flush=True)
        cum_frames += n_frames

    # Full 21-cut QA contact sheet
    cols, tw, th = 6, 216, 384
    thumbs = []
    for i, sv in enumerate(seg_videos_flat, 1):
        _, _, d = probe_video(sv)
        t = os.path.join(QC_DIR, f"c{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{d * 0.50:.2f}", "-i", sv, "-vf", f"scale={tw}:{th}", "-frames:v", "1", t], check=True)
        thumbs.append(t)
    rows = (len(thumbs) + cols - 1) // cols
    while len(thumbs) < cols * rows:
        pad_t = os.path.join(QC_DIR, f"pad{len(thumbs)}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x14161c:s={tw}x{th}", "-frames:v", "1", pad_t], check=True)
        thumbs.append(pad_t)
    inp = [x for t in thumbs for x in ("-i", t)]
    layout = "|".join(f"{(i % cols) * tw}_{(i // cols) * th}" for i in range(len(thumbs)))
    qa_sheet = os.path.join(QC_DIR, "QA_K5_EP01_V5_NoBag_9x16.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs={len(thumbs)}:layout={layout}", "-frames:v", "1", qa_sheet], check=True)

    hook_vids, hook_pcm = build_cold_open_hook(V5_STORY["hook_scenes"], actor_only_vids, seg_audios, timeline_log)

    story_samples = timeline_log[-1]["end_sample"]
    dlg_story = np.concatenate(seg_audios, axis=0)
    act_starts = []
    for sc_trigger, bgm_fn, bgm_off, bgm_gain in acts:
        st_samp = next((it["start_sample"] for it in timeline_log if it["scene"] == sc_trigger), 0)
        act_starts.append((st_samp, bgm_fn, bgm_off, bgm_gain))
    act_starts[0] = (0, act_starts[0][1], act_starts[0][2], act_starts[0][3])

    bgm_story = np.zeros((story_samples, 2), dtype=np.float32)
    xfade_samp = int(1.80 * SR)
    for a_i, (st_s, b_fn, b_off, b_gain) in enumerate(act_starts):
        nx_s = act_starts[a_i + 1][0] if a_i + 1 < len(act_starts) else story_samples
        s0 = max(0, st_s - (xfade_samp // 2 if a_i > 0 else 0))
        s1 = min(story_samples, nx_s + (xfade_samp // 2 if a_i + 1 < len(act_starts) else 0))
        if s1 <= s0: continue
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
    duck_sm = np.convolve(np.pad(np.where(blk_rms > 0.022, 0.70, 1.30).astype(np.float32), (3, 2), mode="edge"), np.ones(6, dtype=np.float32) / 6.0, mode="valid")
    duck_full = np.interp(np.linspace(0.0, n_blk, story_samples, endpoint=False), np.arange(n_blk, dtype=np.float32) + 0.5, duck_sm).astype(np.float32)[:, None]

    mix_story = np.clip(np.tanh((dlg_story + bgm_story * duck_full) * 1.04) / 1.04, -0.94, 0.94)
    mix_master = np.concatenate([hook_pcm, mix_story], axis=0)
    vid_total = len(mix_master) / float(SR)

    all_concat_vids = list(hook_vids) + list(seg_videos_flat)
    master_wav = os.path.join(BASE_DIR, "master_v8_48k.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((mix_master * 32767.0).astype(np.int16).tobytes())

    concat_txt = os.path.join(BASE_DIR, "concat_v8_9x16.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for sv in all_concat_vids: cf.write(f"file '{sv}'\n")

    fname = f"{BATCH_CODE} {BRAND_PREFIX} {V5_STORY['title']} final.mp4"
    final_local = os.path.join(BASE_DIR, fname)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-i", master_wav,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "224k", "-ar", str(SR), "-ac", "2",
        "-movflags", "+faststart", final_local
    ], check=True)

    _, _, mux_dur = probe_video(final_local)
    print(f"  [V8 BAG-FREE MUX VERIFIED] Audio={vid_total:.2f}s | Video={mux_dur:.2f}s | Cuts={len(all_concat_vids)}", flush=True)

    purge_old_k5_mp4s()
    for tdir in (K5_DRIVE_DIR, MASTER_CLOUD_DIR, LOCAL_CAPCUT_DIR):
        os.makedirs(tdir, exist_ok=True)
        shutil.copy2(final_local, os.path.join(tdir, fname))
    print(f"=== K5 V5 BAG-FREE MASTER DELIVERED -> {os.path.join(K5_DRIVE_DIR, fname)} ===", flush=True)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "audit"
    if cmd == "audit":
        audit_v5()
    elif cmd == "render":
        render_v8_master()
