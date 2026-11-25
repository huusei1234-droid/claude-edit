import glob, json, os, subprocess, sys

# Add torch/lib and nvidia/*/bin to PATH & DLL search dirs before importing faster_whisper
site_pkgs = os.path.join(sys.prefix, "Lib", "site-packages")
extra_bins = glob.glob(os.path.join(site_pkgs, "nvidia", "*", "bin")) + [os.path.join(site_pkgs, "torch", "lib")]
for b in extra_bins:
    if os.path.isdir(b):
        os.environ["PATH"] = b + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(b)
            except Exception:
                pass

from faster_whisper import WhisperModel

SRC_DIR = r"D:\tải về"
OUT_DIR = r"d:\AI\full studio\output\k4-5-videos-261122\source_analysis"
os.makedirs(OUT_DIR, exist_ok=True)

videos = sorted(glob.glob(os.path.join(SRC_DIR, "*.mp4")))
print(f"Found {len(videos)} videos in {SRC_DIR}", flush=True)

# Extract 8-frame contact sheets + 16kHz wavs first
meta_list = []
for idx, vpath in enumerate(videos, 1):
    vname = os.path.basename(vpath)
    tag = f"v{idx:02d}"
    pr = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration", "-of", "json", vpath
    ]).decode("utf-8"))
    w = int(pr["streams"][0]["width"])
    h = int(pr["streams"][0]["height"])
    dur = float(pr["format"]["duration"])

    wav_path = os.path.join(OUT_DIR, f"{tag}.wav")
    if not os.path.exists(wav_path):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vpath, "-vn", "-ac", "1", "-ar", "16000", wav_path], check=True)

    sheet = os.path.join(OUT_DIR, f"{tag}_sheet.jpg")
    if not os.path.exists(sheet):
        thumbs = []
        for fi in range(8):
            ts = max(0.5, min(dur - 0.5, dur * (fi + 0.5) / 8.0))
            tp = os.path.join(OUT_DIR, f"{tag}_f{fi+1}.jpg")
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", vpath,
                "-vf", "scale=270:480:force_original_aspect_ratio=decrease,pad=270:480:(ow-iw)/2:(oh-ih)/2",
                "-frames:v", "1", tp
            ], check=True)
            thumbs.append(tp)
        inp = []
        for tp in thumbs:
            inp += ["-i", tp]
        layout = "|".join(f"{(i%4)*270}_{(i//4)*480}" for i in range(8))
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs=8:layout={layout}", "-frames:v", "1", sheet],
            check=True
        )
    print(f"Prepared {tag}: {dur:.2f}s ({w}x{h}) -> {sheet}", flush=True)
    meta_list.append((tag, vname, w, h, dur, wav_path, sheet))

def try_load_model():
    for mname in ["deepdml/faster-whisper-large-v3-turbo-ct2", "large-v3-turbo", "medium"]:
        for dev, ctype in [("cuda", "float16"), ("cpu", "int8")]:
            try:
                m = WhisperModel(mname, device=dev, compute_type=ctype, cpu_threads=8)
                # Smoke test 1st wav if cuda to verify cudnn dlls work
                if dev == "cuda":
                    segs, _ = m.transcribe(meta_list[-1][5], language="vi", vad_filter=True, beam_size=1)
                    list(segs)
                print(f"Loaded Whisper '{mname}' on {dev} ({ctype})!", flush=True)
                return m
            except Exception as e:
                print(f"Skip {mname} on {dev}: {e}", flush=True)
    raise RuntimeError("No Whisper model could be loaded!")

model = try_load_model()

summary = []
for tag, vname, w, h, dur, wav_path, sheet in meta_list:
    print(f"\n=== [{tag}] {vname} ({dur:.1f}s) ===", flush=True)
    segments, _ = model.transcribe(wav_path, language="vi", vad_filter=True, beam_size=4)
    segs = []
    for s in segments:
        line = f"[{s.start:6.2f}s -> {s.end:6.2f}s] {s.text.strip()}"
        print(" ", line, flush=True)
        segs.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
    summary.append({
        "id": tag,
        "filename": vname,
        "width": w,
        "height": h,
        "duration": round(dur, 2),
        "sheet": sheet,
        "segments": segs,
    })

out_json = os.path.join(OUT_DIR, "transcripts_5_videos.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"\nALL 5 VIDEOS TRANSCRIBED -> {out_json}", flush=True)
