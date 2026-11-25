import json, os, subprocess

PROJ_DIR  = r"d:\AI\full studio\output\htpm7-261121"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")

# Trim dead pre-roll (0.00..1.80s, frame 0..53) and post-roll (70.10..72.63s, frame 2103..2178)
# Exact kept range: frames 54..2102 inclusive -> 2049 frames = 68.300000s @ 30fps CFR!
F_START = 54
F_END   = 2103
N_KEEP  = F_END - F_START       # 2049 frames
T_SHIFT = F_START / 30.0        # 1.800000s
DUR_NEW = N_KEEP / 30.0         # 68.300000s

mc        = os.path.join(AROLL_DIR, "main_cut.mp4")
mc_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
matte_out = os.path.join(AROLL_DIR, "main_cut_matte.mp4")
mc_json   = os.path.join(AROLL_DIR, "main_cut.json")
clean_js  = os.path.join(AROLL_DIR, "main_cut_clean.json")

# Check if already trimmed
cur_cnt = int(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
    "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", mc_graded
], text=True).strip())

if cur_cnt != N_KEEP:
    print(f"[Trim] Slicing A-Roll, Graded & RVM Matte from {cur_cnt} frames -> {N_KEEP} frames ({DUR_NEW:.3f}s)...", flush=True)
    # 1. Trim main_cut.mp4 (video + audio)
    mc_tmp = mc + ".trim.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", mc,
        "-vf", f"select='between(n,{F_START},{F_END-1})',setpts=N/30/TB",
        "-af", f"atrim=start={T_SHIFT:.6f}:end={T_SHIFT + DUR_NEW:.6f},asetpts=PTS-STARTPTS",
        "-r", "30", "-fps_mode", "cfr",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        mc_tmp
    ], check=True)
    os.replace(mc_tmp, mc)

    # 2. Trim main_cut_graded.mp4
    gr_tmp = mc_graded + ".trim.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", mc_graded,
        "-vf", f"select='between(n,{F_START},{F_END-1})',setpts=N/30/TB",
        "-r", "30", "-fps_mode", "cfr", "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        gr_tmp
    ], check=True)
    os.replace(gr_tmp, mc_graded)

    # 3. Trim main_cut_matte.mp4
    mt_tmp = matte_out + ".trim.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", matte_out,
        "-vf", f"select='between(n,{F_START},{F_END-1})',setpts=N/30/TB",
        "-r", "30", "-fps_mode", "cfr", "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
        mt_tmp
    ], check=True)
    os.replace(mt_tmp, matte_out)

    # 4. Trim Demucs stems & orig_input.wav cleanly by T_SHIFT..T_SHIFT+DUR_NEW
    for wav_p in [
        os.path.join(STEMS_DIR, "orig_input.wav"),
        os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "vocals.wav"),
        os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "no_vocals.wav"),
    ]:
        if os.path.exists(wav_p):
            wt = wav_p + ".trim.wav"
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-i", wav_p,
                "-af", f"atrim=start={T_SHIFT:.6f}:end={T_SHIFT + DUR_NEW:.6f},asetpts=PTS-STARTPTS",
                wt
            ], check=True)
            os.replace(wt, wav_p)

for lbl, vp in [("main_cut", mc), ("graded", mc_graded), ("matte", matte_out)]:
    c = int(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", vp
    ], text=True).strip())
    print(f"  Verified {lbl}: {c} frames", flush=True)
    assert c == N_KEEP, f"Frame mismatch on {lbl}: {c} != {N_KEEP}"

# 5. Shift & proofread 100% of main_cut.json -> main_cut_clean.json
raw_tr = json.load(open(mc_json, "r", encoding="utf-8"))

# Exact word-level fixes indexed by raw start time (rounded to 2 decimals)
WORD_FIXES = {
    4.60:  None,     # keep
    2.50:  "30,",    # start=2.50
    4.34:  "nhăn!",  # punchy hook end "Sau 30, đừng chỉ soi nếp nhăn!"
    13.16: "mình.",
    15.10: "triệu",
    15.46: "đồng",
    18.48: "kem",
    19.52: "chống",
    21.42: "da.",
    26.30: "không?",
    27.78: "nào?",
    30.30: "không?",
    41.12: "triệu",
    41.68: "rồi",
    42.54: "luận:",
    43.60: "nội",
    43.82: "tiết,",
    55.60: "làn",
    61.68: "mình.",
    65.12: None,
    64.78: "Hằng.",
    69.14: "cần!",
}

clean_segs = []
for seg in raw_tr["segments"]:
    new_words = []
    raw_ws = seg.get("words", [])
    skip_next = False
    for idx_w, w in enumerate(raw_ws):
        if skip_next:
            skip_next = False
            continue
        rs = round(float(w["start"]), 2)
        re_t = round(float(w["end"]), 2)
        txt = w["word"].strip()

        # Merge "30" (63.26) + "còng," (63.62) -> "30+,"
        if rs == 63.26 and idx_w + 1 < len(raw_ws) and round(float(raw_ws[idx_w + 1]["start"]), 2) == 63.62:
            txt = "30+,"
            re_t = round(float(raw_ws[idx_w + 1]["end"]), 2)
            skip_next = True
        elif rs in WORD_FIXES and WORD_FIXES[rs] is not None:
            txt = WORD_FIXES[rs]

        ns = round(max(0.0, float(w["start"]) - T_SHIFT), 3)
        ne = round(min(DUR_NEW, float(re_t) - T_SHIFT), 3)
        if ne > ns:
            new_words.append({"start": ns, "end": ne, "word": txt})

    if new_words:
        clean_segs.append({
            "start": new_words[0]["start"],
            "end": new_words[-1]["end"],
            "text": " ".join(x["word"] for x in new_words),
            "words": new_words,
        })

out_tr = {"lang": "vi", "duration": DUR_NEW, "segments": clean_segs}
with open(clean_js, "w", encoding="utf-8") as f:
    json.dump(out_tr, f, ensure_ascii=False, indent=2)

with open(os.path.join(AROLL_DIR, "main_cut.txt"), "w", encoding="utf-8") as f:
    for s in clean_segs:
        f.write(f"[{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}\n")

print(f"\n=== CLEAN SHIFTED TRANSCRIPT ({len(clean_segs)} segments, {N_KEEP} frames = {DUR_NEW:.3f}s) ===")
for s in clean_segs:
    print(f"  [{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}")
