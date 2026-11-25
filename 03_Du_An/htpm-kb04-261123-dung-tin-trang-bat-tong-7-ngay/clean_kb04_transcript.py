import json, os, subprocess

PROJ_DIR  = r"C:\AI\full studio\output\htpm-kb04-261123"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")

# Grab crisp open-eyed warm smile frame at t=20.40s from graded A-Roll for AI speaker anchor!
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-ss", "20.40",
    "-i", os.path.join(AROLL_DIR, "main_cut_graded.mp4"),
    "-frames:v", "1", os.path.join(AROLL_DIR, "speaker_ref.png")
], check=True)

raw = json.load(open(os.path.join(AROLL_DIR, "main_cut.json"), encoding="utf-8"))
all_w = []
for s in raw["segments"]:
    for w in s["words"]:
        all_w.append([round(float(w["start"]), 2), round(float(w["end"]), 2), w["word"].strip()])

# Exact token-level proofreading map by start timestamp
EXACT_MAP = {
    2.44:  "ngày!",
    10.78: "táo!",
    12.62: "chuyện",
    19.54: "tự",
    20.00: "hơn.",
    21.04: "chính",
    22.00: "thật",
    26.64: "mức.",
    28.20: "ngày,",
    30.04: "tông,",
    31.24: "chống",
    31.50: "nắng,",
    32.46: "trắng,",
    33.70: "thích!",
    37.04: "tắc.",
    40.08: "tố:",
    41.04: "truyền,",
    42.06: "nắng,",
    43.06: "ngủ,",
    43.44: "dinh",
    44.10: "dưỡng,",
    44.46: "stress,",
    44.94: "lối",
    46.20: "và",
    46.92: "da.",
    47.98: "cũng",
    48.64: "White",
    49.00: "Skin,",
    49.36: "nhưng",
    54.78: "thần",
    55.04: "tốc.",
    56.24: "thành",
    56.50: "phần,",
    57.54: "mục",
    58.16: "dụng,",
    58.50: "hiểu",
    60.62: "gì.",
    62.02: "nhất:",
    62.18: "đừng",
    64.54: "nhanh!",
    66.14: "Hằng",
    66.90: "về",
    69.68: "đáng",
    70.58: "giác,",
    71.72: "\"NÓI",
    72.32: "THẬT\"!",
}

cleaned_words = []
i = 0
while i < len(all_w):
    st, en, txt = all_w[i]
    # Merge "3", "đến", "4" (29.36..30.04) -> "3-4"
    if st == 29.36 and i + 2 < len(all_w) and all_w[i + 1][2] == "đến":
        cleaned_words.append({"start": 29.36, "end": all_w[i + 2][1], "word": "3-4"})
        i += 3
        continue
    # Fix 68.88..69.68 ("Nếu", "như", "thế", "nào") -> single "nào" (69.12..69.66)
    if st == 68.88 and txt == "Nếu":
        cleaned_words.append({"start": 69.12, "end": 69.66, "word": "nào"})
        i += 4
        continue
    if st in EXACT_MAP:
        txt = EXACT_MAP[st]
    cleaned_words.append({"start": st, "end": en, "word": txt})
    i += 1

# Group back into clean sentence segments
segs, cur = [], []
for w in cleaned_words:
    cur.append(w)
    if w["word"].endswith((".", "!", "?", ":")):
        segs.append({
            "start": cur[0]["start"],
            "end": cur[-1]["end"],
            "text": " ".join(x["word"] for x in cur),
            "words": cur,
        })
        cur = []
if cur:
    segs.append({
        "start": cur[0]["start"],
        "end": cur[-1]["end"],
        "text": " ".join(x["word"] for x in cur),
        "words": cur,
    })

out = {"lang": "vi", "duration": 73.467, "segments": segs}
with open(os.path.join(AROLL_DIR, "main_cut_clean.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

for s in segs:
    print(f"[{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}")
