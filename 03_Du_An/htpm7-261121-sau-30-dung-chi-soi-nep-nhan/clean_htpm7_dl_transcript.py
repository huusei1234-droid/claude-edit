import json, os

PROJ_DIR  = r"d:\AI\full studio\output\htpm7-261121"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll_dl")
in_js     = os.path.join(AROLL_DIR, "vocals_whisper.json")
out_js    = os.path.join(AROLL_DIR, "main_cut_clean.json")

tr = json.load(open(in_js, "r", encoding="utf-8"))

# Fix Segment 0 opening words (0.00..3.66s) verified on isolated 4.2s clip:
# "Sau 30, đừng chỉ soi nếp nhăn! Sau 30 tuổi,"
seg0_head = [
    {"start": 0.00, "end": 0.42, "word": "Sau"},
    {"start": 0.42, "end": 0.68, "word": "30,"},
    {"start": 1.02, "end": 1.38, "word": "đừng"},
    {"start": 1.38, "end": 1.60, "word": "chỉ"},
    {"start": 1.60, "end": 1.86, "word": "soi"},
    {"start": 1.86, "end": 2.10, "word": "nếp"},
    {"start": 2.10, "end": 2.36, "word": "nhăn!"},
    {"start": 2.54, "end": 3.04, "word": "Sau"},
    {"start": 3.04, "end": 3.24, "word": "30"},
    {"start": 3.24, "end": 3.66, "word": "tuổi,"},
]
rest_seg0 = [w for w in tr["segments"][0]["words"] if float(w["start"]) >= 3.70]
tr["segments"][0]["words"] = seg0_head + rest_seg0

WORD_FIXES = {
    10.12: "mình.",
    11.88: "triệu",
    12.20: "đồng",
    17.62: "da.",
    21.12: "không?",
    22.48: "nào?",
    24.78: "không?",
    26.64: "không?",
    29.20: "không?",
    33.08: "nhau.",
    34.60: "triệu",
    35.08: "rồi",
    35.88: "luận:",
    36.84: "nội",
    37.04: "tiết,",
    38.34: "hóa.",
    41.10: "trước.",
    44.90: "cần.",
    47.76: "làn",
    48.10: "đẹp.",
    53.26: "mình.",
    56.08: "Hằng.",
    56.38: "Hằng",
    60.06: "cần!",
}

clean_segs = []
for seg in tr["segments"]:
    ws = seg.get("words", [])
    new_ws = []
    skip_next = False
    for i, w in enumerate(ws):
        if skip_next:
            skip_next = False
            continue
        rs = round(float(w["start"]), 2)
        re_t = round(float(w["end"]), 2)
        tok = w["word"].strip()
        if tok == "xoay":
            tok = "soi"
        if tok == "thương" and i > 0 and ws[i - 1]["word"].strip() == "bất":
            tok = "thường"
        # Merge "30" (54.72) + "còng," (55.04) -> "30+,"
        if 54.65 <= rs <= 54.80 and i + 1 < len(ws) and ws[i + 1]["word"].strip().startswith("còng"):
            tok = "30+,"
            re_t = round(float(ws[i + 1]["end"]), 2)
            skip_next = True
        else:
            for k_ts, rep_w in WORD_FIXES.items():
                if abs(rs - k_ts) <= 0.06:
                    tok = rep_w
                    break
        if tok:
            new_ws.append({"start": round(float(w["start"]), 3), "end": round(re_t, 3), "word": tok})
    if new_ws:
        clean_segs.append({
            "start": new_ws[0]["start"],
            "end": new_ws[-1]["end"],
            "text": " ".join(x["word"] for x in new_ws),
            "words": new_ws,
        })

out = {"lang": "vi", "duration": 60.90, "segments": clean_segs}
with open(out_js, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"=== CLEAN DOWNLOADS TRANSCRIPT ({len(clean_segs)} segments, 60.900s) ===")
for s in clean_segs:
    print(f"  [{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}")
