import glob, json, os, subprocess
from faster_whisper import WhisperModel

SRC_DIR = r"D:\tải về"
OUT_DIR = r"d:\AI\full studio\output\k4-5-videos-261122\source_analysis"
videos = sorted(glob.glob(os.path.join(SRC_DIR, "*.mp4")))

model = WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)
print("Loaded faster-whisper-large-v3-turbo-ct2 on CPU int8 (12 threads)!", flush=True)

summary = []
for idx, vpath in enumerate(videos, 1):
    vname = os.path.basename(vpath)
    tag = f"v{idx:02d}"
    wav_path = os.path.join(OUT_DIR, f"{tag}.wav")
    sheet = os.path.join(OUT_DIR, f"{tag}_sheet.jpg")
    pr = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration", "-of", "json", vpath
    ]).decode("utf-8"))
    dur = float(pr["format"]["duration"])
    print(f"\n=== [{tag}] {vname} ({dur:.1f}s) ===", flush=True)
    segments, _ = model.transcribe(wav_path, language="vi", vad_filter=True, beam_size=2)
    segs = []
    for s in segments:
        line = f"[{s.start:6.2f}s -> {s.end:6.2f}s] {s.text.strip()}"
        print(" ", line, flush=True)
        segs.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
    summary.append({
        "id": tag,
        "filename": vname,
        "duration": round(dur, 2),
        "sheet": sheet,
        "segments": segs,
    })

out_json = os.path.join(OUT_DIR, "transcripts_5_videos.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"\nALL 5 VIDEOS TRANSCRIBED -> {out_json}", flush=True)
