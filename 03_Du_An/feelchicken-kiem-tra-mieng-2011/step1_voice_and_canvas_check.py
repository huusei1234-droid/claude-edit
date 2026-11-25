import os, sys, json, time, subprocess, urllib.request
import numpy as np
from faster_whisper import WhisperModel

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
VOICE_DIR = os.path.join(PROJ_DIR, "voice")
os.makedirs(VOICE_DIR, exist_ok=True)

# 1. Inspect current Canvas state without navigating away
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv
st = cv.call("canvas_get_state", {}).get("result", {})
print("=== CURRENT CANVAS ===", st.get("projectId"), st.get("title"), flush=True)
for n in st.get("nodes", []):
    print("  node:", n.get("id"), n.get("type"), repr(n.get("title")), str(n.get("metadata", {}))[:180], flush=True)

# 2. Extract ultra-clean reference WAV of Anh Khang from C3942.MP4 [2.22s .. 11.06s] (wireless mic CH_R)
c3942 = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC\16-11-2026\Thư mục mới\C3942.MP4"
ref_wav = os.path.join(VOICE_DIR, "ref_anh_khang_clean.wav")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-ss", "2.22", "-to", "11.06", "-i", c3942,
    "-af", "pan=mono|c0=c1,highpass=f=85,lowpass=f=14000,loudnorm=I=-16:TP=-1.5:LRA=9",
    "-ar", "24000", "-ac", "1", ref_wav
], check=True)
print("Saved ref_anh_khang_clean.wav:", os.path.getsize(ref_wav), "bytes", flush=True)

ref_text = "Có ai như Khang không? Hồi xưa khi mà đi học á, nghe đến chữ kiểm tra miệng là run cầm cập. Còn bây giờ á, mà nghe đến ba chữ kiểm tra miệng là thấy bồi hồi ghê luôn á!"

# 3. Check if ANH KHANG FEEL CHICKEN profile already exists in VoiceStudio (:3900), otherwise create via multipart POST /profiles
with urllib.request.urlopen("http://127.0.0.1:3900/profiles", timeout=10) as r:
    profiles = json.loads(r.read().decode("utf-8"))

prof_id = None
for p in profiles:
    if p.get("name") == "ANH KHANG FEEL CHICKEN":
        prof_id = p["id"]
        break

if not prof_id:
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    parts = []
    def add_field(name, val):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n".encode("utf-8"))
    add_field("name", "ANH KHANG FEEL CHICKEN")
    add_field("ref_text", ref_text)
    add_field("language", "English")
    add_field("kind", "clone")
    wav_bytes = open(ref_wav, "rb").read()
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"ref_audio\"; filename=\"ref_anh_khang.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode("utf-8")
        + wav_bytes + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    req = urllib.request.Request(
        "http://127.0.0.1:3900/profiles",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        created = json.loads(resp.read().decode("utf-8"))
        prof_id = created["id"]
        print("Created VoiceStudio profile ANH KHANG FEEL CHICKEN ->", prof_id, flush=True)
else:
    print("Using existing VoiceStudio profile ANH KHANG FEEL CHICKEN ->", prof_id, flush=True)

# 4. Synthesize the 2 lines (3 seeds each, pick cleanest verified by Whisper!)
LINES = {
    "line_prog_full": (
        "Hai mươi tháng mười một sắp tới rồi, Phiu Chích Kình muốn đưa mọi người trở về một chút ký ức học trò, với chương trình: Kiểm tra miệng, trả lời đúng, nhận quà ngay!",
        ["mười một", "ký ức", "học trò", "kiểm tra miệng", "trả lời đúng", "nhận quà ngay"]
    ),
    "line_prog_tail": (
        "Kiểm tra miệng! Trả lời đúng, nhận quà ngay!",
        ["kiểm tra miệng", "trả lời đúng", "nhận quà ngay"]
    ),
    "line_outro": (
        "Hai mươi tháng mười một này! Rủ hội bạn đến ôn lại kiến thức, xem ai còn xứng đáng danh hiệu học sinh giỏi nào!",
        ["mười một", "hội bạn", "kiến thức", "xứng đáng", "học sinh giỏi"]
    ),
}

wm = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
chosen = {}

for key, (tts_text, must_have) in LINES.items():
    best_path = None
    best_score = -1
    best_words = []
    best_dur = 0.0
    for attempt, seed in enumerate([101, 202, 303], 1):
        raw_out = os.path.join(VOICE_DIR, f"{key}_raw_{attempt}.wav")
        trim_out = os.path.join(VOICE_DIR, f"{key}_trim_{attempt}.wav")
        payload = json.dumps({
            "model": "omnivoice",
            "voice": prof_id,
            "input": tts_text,
            "response_format": "wav",
            "speed": 1.03,
            "num_step": 32,
            "guidance_scale": 2.0,
            "seed": seed,
            "denoise": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:3900/v1/audio/speech",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=300) as resp:
            open(raw_out, "wb").write(resp.read())

        # Trim leading/trailing silence + normalize to match Anh Khang's real mic (-16 LUFS, 48kHz mono)
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", raw_out,
            "-af", "silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.04,areverse,silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.06,areverse,highpass=f=85,loudnorm=I=-16:TP=-1.5:LRA=9",
            "-ar", "48000", "-ac", "1", trim_out
        ], check=True)

        pr = json.loads(subprocess.check_output(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", trim_out]).decode("utf-8"))
        dur = float(pr["format"]["duration"])

        segs, _ = wm.transcribe(trim_out, language="vi", word_timestamps=True, vad_filter=False, condition_on_previous_text=False)
        segs = list(segs)
        full_txt = " ".join(s.text.strip() for s in segs).lower()
        words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in (s.words or [])]
        hits = sum(1 for kw in must_have if kw in full_txt)
        print(f"  [{key} try {attempt} | {time.time()-t0:.1f}s | dur={dur:.2f}s | hits={hits}/{len(must_have)}] -> {full_txt}", flush=True)

        if hits > best_score:
            best_score = hits
            best_path = trim_out
            best_words = words
            best_dur = dur
        if hits == len(must_have):
            break

    final_wav = os.path.join(VOICE_DIR, f"{key}_best.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", best_path, "-c", "copy", final_wav], check=True)
    chosen[key] = {"wav": final_wav, "dur": round(best_dur, 3), "hits": best_score, "words": best_words}
    print(f"==> SELECTED {key}: {final_wav} (dur={best_dur:.2f}s, hits={best_score})", flush=True)

with open(os.path.join(VOICE_DIR, "cloned_lines_meta.json"), "w", encoding="utf-8") as f:
    json.dump({"profile_id": prof_id, "lines": chosen}, f, ensure_ascii=False, indent=2)
print("ALL CLONED VOICE LINES READY!", flush=True)
