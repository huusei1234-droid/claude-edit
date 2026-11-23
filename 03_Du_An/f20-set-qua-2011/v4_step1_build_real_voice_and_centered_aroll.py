import json, os, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from faster_whisper import WhisperModel

P1117_VID = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1117\video")
V3_DIR    = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v3_pro")
V4_DIR    = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v4_clean_master")
AROLL_V4  = V4_DIR / "aroll_v4"
VOICE_V4  = V4_DIR / "voice_v4"
AROLL_V4.mkdir(parents=True, exist_ok=True)
VOICE_V4.mkdir(parents=True, exist_ok=True)

SR, FPS = 48000, 30

def find_1117(prefix):
    for f in P1117_VID.glob("*.mp4"):
        if prefix in f.name:
            return f
    raise FileNotFoundError(prefix)

# Verify exact word split in s03_ship_tts.wav & s11_cam_nang.wav from V3 timeline_v3_pro.json:
# In s03_ship_tts (started at 22.5667s): "Khách(22.54) ... 10(25.00) set(25.20) quà(25.56)" -> local 0.00..3.15s!
# In s11_cam_nang (started at 80.30s): "và(88.80) hướng(88.98) dẫn(89.26) ... nhé(91.72)" -> local 8.46..11.65s!

BLOCKS_SPEC = [
    # (id, mode, src_file, ss, dur, vf_crop)
    ("b01_open_live",        "live", find_1117("39C59B8C"), 4.00, 19.9333, "scale=1252:2226,crop=1080:1920:0:150"),
    ("b02_hanoi_tts",        "tts",  V3_DIR / "voice_clips" / "s03_ship_tts.wav", 0.00, 3.1667, None),
    ("b03_hcmc_tong_real",   "real_vo", find_1117("39C59B8C"), 29.60, 9.1667, "scale=1252:2226,crop=1080:1920:0:150"),
    ("b04_pov_real",         "real_vo", find_1117("354004BC"), 3.47,  4.3000, "scale=1210:2150,crop=1080:1920:0:115"),
    ("b05_intro_set_live",   "live", find_1117("5172C35D"), 2.67,  4.8667, "scale=1140:2026,crop=1080:1920:10:53"),
    ("b06_4items_real",      "live", find_1117("FEDD2C68"), 0.35, 41.0667, "scale=1188:2112,crop=1080:1920:0:96"),
    ("b07_camnang_live",     "live", find_1117("C70C0450"), 2.00, 17.5000, "scale=1124:1998,crop=1080:1920:14:39"),
    ("b08_chungyen_tts",     "tts",  V3_DIR / "voice_clips" / "s11_cam_nang.wav", 8.46, 3.2000, None),
    ("b09_giomica_quai_live","live", find_1117("F2465DBE"), 1.95, 19.4667, "scale=1210:2150,crop=1080:1920:0:115"),
    ("b10_sx_live",          "live", find_1117("5C663422"), 2.53,  9.0000, "scale=1252:2226,crop=1080:1920:0:150"),
    ("b11_cta_live",         "live", find_1117("A9530997"), 5.10, 14.0000, "scale=1252:2226,crop=1080:1920:172:150"),
]

INTRO_DUR = 2.6000   # 78 frames (2 crisp real panoramic shots of F20 gift sets before Chi Oanh speaks!)
OUTRO_DUR = 2.6000   # 78 frames (clean F20 End-Card)

cur_t = INTRO_DUR
blocks_out = []
master_audio = [np.zeros((int(round(INTRO_DUR * SR)), 2), dtype=np.float32)]

for bid, mode, src_p, ss, dur, vf_crop in BLOCKS_SPEC:
    frames = int(round(dur * FPS))
    exact_dur = frames / FPS
    n_samp = int(round(exact_dur * SR))

    wav_out = VOICE_V4 / f"{bid}.wav"
    vid_out = (AROLL_V4 / f"{bid}.mp4") if vf_crop else None

    # Extract & loudness-match voice (with gentle studio highpass + presence clarity + -16.5 LUFS)
    af = "highpass=f=85,afftdn=nf=-24,equalizer=f=3200:width_type=o:width=1.5:g=1.8,loudnorm=I=-16.5:TP=-1.5:LRA=9.0" if mode != "tts" else "loudnorm=I=-16.5:TP=-1.5:LRA=9.0"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.4f}", "-t", f"{exact_dur:.4f}", "-i", str(src_p),
        "-af", af, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(wav_out)
    ], check=True)

    # Read PCM, pad/trim to exact sample count, apply 25ms/40ms anti-click micro-fades
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav_out), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"])
    arr = np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()
    if len(arr) < n_samp:
        arr = np.vstack([arr, np.zeros((n_samp - len(arr), 2), dtype=np.float32)])
    arr = arr[:n_samp]
    fi_n, fo_n = int(0.025 * SR), int(0.040 * SR)
    arr[:fi_n] *= np.linspace(0.0, 1.0, fi_n, dtype=np.float32)[:, None]
    arr[-fo_n:] *= np.linspace(1.0, 0.0, fo_n, dtype=np.float32)[:, None]

    # Overwrite exact frame-locked WAV (so CapCut clean draft has 100% frame-accurate synced audio too!)
    pcm16 = (np.clip(arr, -0.98, 0.98) * 32767.0).astype(np.int16)
    with wave.open(str(wav_out), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())
    master_audio.append(arr)

    # Extract horizontally re-centered 1080x1920 @ 30fps video WITH its exact synced audio baked in too!
    if vid_out:
        vf_full = f"{vf_crop},eq=brightness=0.015:contrast=1.04:saturation=1.08,fps=30,format=yuv420p"
        tmp_v = AROLL_V4 / f"_v_{bid}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{ss:.4f}", "-t", f"{exact_dur:.4f}", "-i", str(src_p),
            "-vf", vf_full, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "16", str(tmp_v)
        ], check=True)
        # Mux exact frame-locked wav_out into vid_out so every live Chi Oanh MP4 has 100% synced audio!
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_v), "-i", str(wav_out),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(vid_out)
        ], check=True)
        tmp_v.unlink(missing_ok=True)

    blocks_out.append({
        "id": bid, "mode": mode,
        "video_path": str(vid_out) if vid_out else None,
        "wav_path": str(wav_out),
        "start": round(cur_t, 4),
        "end": round(cur_t + exact_dur, 4),
        "dur": round(exact_dur, 4),
        "frames": frames,
    })
    print(f"Prepared {bid:22s} [{cur_t:6.2f} - {cur_t+exact_dur:6.2f}s] ({mode})", flush=True)
    cur_t += exact_dur

voice_end = cur_t
total_dur = round(voice_end + OUTRO_DUR, 4)
total_frames = int(round(total_dur * FPS))
master_audio.append(np.zeros((int(round(OUTRO_DUR * SR)), 2), dtype=np.float32))

full_vo = np.vstack(master_audio)
vo_master_p = V4_DIR / "01_Voice_V4_Master.wav"
pcm_all = (np.clip(full_vo, -0.98, 0.98) * 32767.0).astype(np.int16)
with wave.open(str(vo_master_p), "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(pcm_all.tobytes())

# Build visual centering verification sheet of all 7 live Chi Oanh clips with x=540 green centerline!
live_vids = [b for b in blocks_out if b["mode"] == "live" and b["video_path"]]
sheet = Image.new("RGB", (240 * len(live_vids), 426))
tmp_j = V4_DIR / "_tmp_c.jpg"
for i, b in enumerate(live_vids):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", b["video_path"], "-frames:v", "1", str(tmp_j)], check=True)
    im = Image.open(tmp_j).resize((240, 426))
    d = ImageDraw.Draw(im)
    d.line([(120, 0), (120, 426)], fill=(0, 255, 120), width=2)
    d.rectangle([4, 4, 195, 24], fill=(0, 0, 0))
    d.text((8, 7), b["id"], fill=(255, 230, 0))
    sheet.paste(im, (i * 240, 0))
tmp_j.unlink(missing_ok=True)
sheet.save(V4_DIR / "v4_aroll_centered_verify.jpg", quality=92)

# Run Whisper large-v3-turbo word-timestamp alignment on 01_Voice_V4_Master.wav!
print("Running Whisper large-v3-turbo word-level alignment on 01_Voice_V4_Master.wav...", flush=True)
wmodel = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
segs, _ = wmodel.transcribe(str(vo_master_p), language="vi", word_timestamps=True, beam_size=5)
w_segs = []
for s in segs:
    w_segs.append({
        "start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(),
        "words": [{"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word.strip(), "p": round(w.probability, 3)} for w in (s.words or [])]
    })

tl_v4 = {
    "fps": FPS, "intro_dur": INTRO_DUR, "voice_end": round(voice_end, 4),
    "outro_dur": OUTRO_DUR, "total_dur": total_dur, "total_frames": total_frames,
    "real_voice_ratio": round(1.0 - (3.1667 + 3.2000) / (voice_end - INTRO_DUR), 4),
    "blocks": blocks_out,
    "whisper_segments": w_segs,
}
(V4_DIR / "timeline_v4_master.json").write_text(json.dumps(tl_v4, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"DONE! Total duration={total_dur:.2f}s ({total_frames} frames), Real Chi Oanh Voice = {tl_v4['real_voice_ratio']*100:.1f}%!")
