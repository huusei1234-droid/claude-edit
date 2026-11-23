import os, sys, json, wave, subprocess
import numpy as np
from faster_whisper import WhisperModel

V2_DIR = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"
AROLL_DIR = os.path.join(V2_DIR, "aroll_1117_clips")
INTRO_DIR = os.path.join(V2_DIR, "intro_clips")
os.makedirs(AROLL_DIR, exist_ok=True)
os.makedirs(INTRO_DIR, exist_ok=True)

P1117 = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1117\video"
F20_ROOT = r"Z:\Máy tính khác\My Computer\F20\video gốc\261116"

# 1. Build 3-shot Panoramic Opening Montage (0.00s - 4.20s = 4.20s, exact 126 frames @ 30fps)
INTRO_SPECS = [
    ("intro_01_wide_showroom.mp4",
     os.path.join(F20_ROOT, r"Chi Oanh\ngang\DJI_20261116092144_0075_D.MP4"),
     1.00, 44,  # 44 frames = 1.4667s
     "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.03:contrast=1.06:saturation=1.12,fps=30,format=yuv420p"),
    ("intro_02_wide_dangkhoa.mp4",
     os.path.join(F20_ROOT, r"Chi Oanh\dọc\C3910.MP4"),
     0.60, 42,  # 42 frames = 1.4000s
     "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.02:contrast=1.06:saturation=1.12,fps=30,format=yuv420p"),
    ("intro_03_wide_cabinet.mp4",
     os.path.join(P1117, "IOS_ALBUM@A9919460-A931-4E9B-8ECE-6032B8D5AACA_L0_001@1794917744000.mp4"),
     0.80, 40,  # 40 frames = 1.3333s (44+42+40 = 126 frames = 4.2000s!)
     "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.02:contrast=1.06:saturation=1.10,fps=30,format=yuv420p"),
]

intro_manifest = []
t_cur = 0.0
for fn, src_p, ss, n_frames, vf in INTRO_SPECS:
    dur = round(n_frames / 30.0, 6)
    dst_p = os.path.join(INTRO_DIR, fn)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.3f}", "-i", src_p,
        "-frames:v", str(n_frames),
        "-vf", vf,
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        dst_p
    ], check=True)
    intro_manifest.append({
        "id": fn.replace(".mp4", ""),
        "path": dst_p,
        "start": round(t_cur, 4),
        "end": round(t_cur + dur, 4),
        "dur": round(dur, 4),
        "frames": n_frames,
    })
    t_cur += dur
print(f"Built 3-shot Panoramic Intro: {t_cur:.4f}s (126 frames)")

# 2. Exact 1117 Voice Splices (Seg [02] -> [03] -> [04] -> [05] -> [06] -> [07] -> [08] -> [09])
RAW_MAP = {it["seg_idx"]: it for it in json.load(open(os.path.join(V2_DIR, "voice_1117_raw_manifest.json"), encoding="utf-8"))}

# Tuple: (clip_name, seg_idx, local_start_s, local_end_s, note)
VOICE_SPLICES = [
    ("aroll_01_seg02a", 2,  0.00, 21.86, "104 set quà -> Nha Trang Anh Hậu 77 set -> Phụ huynh 13 set -> KH thứ 3"),
    ("aroll_02_seg02b", 2, 22.83, 34.86, "Giáo viên Hà Nội 10 set + TP.HCM 4 set -> Tổng 104 set quà"),
    ("aroll_03_seg03",  3,  0.00,  4.30, "Đây là những set quà bên Oanh đã chuẩn bị xong sáng hôm nay ạ"),
    ("aroll_04_seg04",  4,  0.00,  4.86, "Bây giờ Oanh sẽ giới thiệu 1 set quà cho mọi người cùng xem nhé"),
    ("aroll_05_seg05a", 5,  0.72, 10.14, "Món 1a: 1 set yến sào - 1 tổ yến sào tinh chế sợi dài dòng tiêu chuẩn"),
    ("aroll_06_seg05b", 5, 10.72, 25.10, "Món 1b (Táo đỏ, ĐTHT, Kỷ tử, Đường phèn) + Món 2 (2 hộp rong biển)"),
    ("aroll_07_seg05c", 5, 25.56, 31.10, "Món 3: 1 gói bánh thuyền mix hạt dinh dưỡng 250g"),
    ("aroll_08_seg05d", 5, 31.42, 41.45, "Món 4: 1 gói rong biển kẹp hạt 500g (22-24 thanh bánh hạt)"),
    ("aroll_09_seg06a", 6,  0.24,  7.47, "Sản phẩm giá trị nhất là set 1 tổ yến sào tinh chế dòng tiêu chuẩn sợi dài"),
    ("aroll_10_seg06b", 6,  8.20, 18.13, "Chuẩn bị thêm 1 tờ cẩm nang sử dụng yến sào + công dụng"),
    ("aroll_11_seg06c", 6, 18.74, 21.48, "Hướng dẫn cách chưng yến đúng cách cho mọi người nhé"),
    ("aroll_12_seg07",  7,  0.48, 19.72, "Xếp trong giỏ mica trong suốt + quai da đỏ đô + hoa & nơ màu be"),
    ("aroll_13_seg08",  8,  0.00,  9.04, "Trực tiếp sản xuất -> yên tâm chất lượng & giá cả"),
    ("aroll_14_seg09",  9,  3.12, 16.78, "Cảm ơn quý anh chị đã tin tưởng Thực Phẩm F20 + CTA inbox 20/11"),
]

SR = 48000
aroll_manifest = []
audio_chunks = [np.zeros((int(round(t_cur * SR)), 2), dtype=np.float32)]  # 4.20s silent intro for voice stem

for cname, sidx, l0, l1, note in VOICE_SPLICES:
    info = RAW_MAP[sidx]
    vp = info["video_path"]
    abs_ss = info["src_in"] + l0
    raw_dur = l1 - l0
    n_frames = max(1, int(round(raw_dur * 30.0)))
    exact_dur = n_frames / 30.0
    n_samples = int(round(exact_dur * SR))

    out_vp = os.path.join(AROLL_DIR, f"{cname}.mp4")
    # Cut exact video frames upright 1080x1920 @ 30fps with warm clean portrait color polish
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{abs_ss:.4f}", "-i", vp,
        "-frames:v", str(n_frames),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.015:contrast=1.04:saturation=1.08,fps=30,format=yuv420p",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        out_vp
    ], check=True)

    # Extract exact stereo f32le audio from original clip with studio voice clarity EQ
    raw_pcm = subprocess.check_output([
        "ffmpeg", "-v", "error",
        "-ss", f"{abs_ss:.4f}", "-i", vp,
        "-t", f"{exact_dur + 0.05:.4f}",
        "-af", "highpass=f=85,equalizer=f=240:t=q:w=1.2:g=-2.0,equalizer=f=3200:t=q:w=1.1:g=2.2,acompressor=threshold=-18dB:ratio=2.6:attack=8:release=110:makeup=2.5dB,alimiter=limit=0.92",
        "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"
    ])
    arr = np.frombuffer(raw_pcm, dtype=np.float32).reshape((-1, 2)).copy()
    if len(arr) < n_samples:
        pad = np.zeros((n_samples - len(arr), 2), dtype=np.float32)
        arr = np.vstack([arr, pad])
    else:
        arr = arr[:n_samples]

    # Micro-fade 33ms in / 55ms out to eliminate 100% of splice clicks/pops!
    fi = min(int(0.033 * SR), len(arr) // 4)
    fo = min(int(0.055 * SR), len(arr) // 4)
    arr[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

    # Also save individual per-clip WAV for CapCut Checkerboard Voice Tracks!
    clip_wav = os.path.join(AROLL_DIR, f"{cname}.wav")
    pcm16 = (np.clip(arr, -0.99, 0.99) * 32767.0).astype(np.int16)
    with wave.open(clip_wav, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    audio_chunks.append(arr)
    aroll_manifest.append({
        "id": cname,
        "seg_idx": sidx,
        "video_path": out_vp,
        "wav_path": clip_wav,
        "start": round(t_cur, 4),
        "end": round(t_cur + exact_dur, 4),
        "dur": round(exact_dur, 4),
        "frames": n_frames,
        "note": note,
    })
    print(f"  {cname}: [{t_cur:6.2f}s -> {t_cur + exact_dur:6.2f}s] ({exact_dur:5.2f}s) | {note}")
    t_cur += exact_dur

# Add 2.20s (66 frames) End-Card tail
OUTRO_FRAMES = 66
OUTRO_DUR = OUTRO_FRAMES / 30.0
audio_chunks.append(np.zeros((int(round(OUTRO_DUR * SR)), 2), dtype=np.float32))
total_dur = round(t_cur + OUTRO_DUR, 4)
total_frames = 126 + sum(x["frames"] for x in aroll_manifest) + OUTRO_FRAMES
print(f"Total Master Timeline: {total_dur:.4f}s ({total_frames} frames @ 30fps)")

master_voice = np.vstack(audio_chunks)
master_wav_path = os.path.join(V2_DIR, "01_Voice_1117_Master.wav")
with wave.open(master_wav_path, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((np.clip(master_voice, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())
print("Saved", master_wav_path)

# 3. Transcribe 01_Voice_1117_Master.wav with faster-whisper large-v3-turbo for exact timeline word timestamps!
print("Running faster-whisper large-v3-turbo on 01_Voice_1117_Master.wav...")
model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
segs, info = model.transcribe(master_wav_path, language="vi", word_timestamps=True, vad_filter=True)

words_all = []
segs_all = []
for s in segs:
    sw = []
    for w in (s.words or []):
        wd = {"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word.strip(), "p": round(w.probability, 3)}
        if wd["word"]:
            sw.append(wd)
            words_all.append(wd)
    segs_all.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": sw})

timeline_data = {
    "fps": 30,
    "total_frames": total_frames,
    "total_dur": total_dur,
    "intro_dur": 4.2,
    "voice_end": round(t_cur, 4),
    "outro_dur": round(OUTRO_DUR, 4),
    "intro_clips": intro_manifest,
    "aroll_clips": aroll_manifest,
    "whisper_segments": segs_all,
    "whisper_words": words_all,
}
json.dump(timeline_data, open(os.path.join(V2_DIR, "timeline_1117_master.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Saved timeline_1117_master.json with {len(words_all)} words across {len(segs_all)} segments!")
