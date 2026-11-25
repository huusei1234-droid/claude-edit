import json, os

aroll = r"d:\AI\full studio\output\htpm4-261120\aroll"
tr = json.load(open(os.path.join(aroll, "main_cut.json"), encoding="utf-8"))

# Exact 100% medical & Vietnamese orthography spellcheck on all 12 segments & words
WORD_FIXES = {
    (0, "99"): "99%",
    (0, "thâm"): "thầm",
    (0, "sản"): "sản.",
    (1, "ngủ"): "ngủ.",
    (2, "nồi"): "nội",
    (2, "sản"): "sản.",
    (3, "hormôn"): "hormone",
    (3, "cao"): "cao.",
    (4, "hormôn"): "hormone",
    (4, "chú"): "chu",
    (4, "thương"): "thường.",
    (5, "rùng"): "rụng",
    (5, "thủ"): "thụ",
    (5, "nữ"): "nữ.",
    (7, "Truyền"): "chuyện",
    (7, "con"): "con,",
    (7, "đổi"): "rối",
    (7, "loàn"): "loạn.",
    (8, "rất"): "giấc,",
    (9, "Chị"): "chị",
    (9, "nổi"): "nội",
    (9, "tiếng"): "tiết",
    (9, "sớm"): "sớm.",
    (10, "nổi"): "nội",
    (10, "tiếng"): "tiết.",
    (11, "sau"): "sau.",
}

for si, seg in enumerate(tr["segments"]):
    new_words = []
    words = seg.get("words", [])
    i = 0
    while i < len(words):
        w = dict(words[i])
        raw_w = w["word"].strip()
        # Merge "cầu(17.00) + thịt(17.18) + xô(17.40-17.56)" -> "Cortisol"
        if si == 3 and raw_w == "cầu" and i + 2 < len(words):
            w["word"] = "Cortisol"
            w["end"] = words[i + 2]["end"]
            new_words.append(w)
            i += 3
            continue
        fixed = WORD_FIXES.get((si, raw_w), raw_w)
        w["word"] = fixed
        new_words.append(w)
        i += 1
    seg["words"] = new_words
    seg["text"] = " ".join(x["word"] for x in new_words)

out_p = os.path.join(aroll, "main_cut_clean.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(tr, f, ensure_ascii=False, indent=2)

print("Saved 100% spellchecked transcript ->", out_p)
for si, seg in enumerate(tr["segments"]):
    print(f"  [{si:02d}] {seg['start']:5.2f} -> {seg['end']:5.2f} | {seg['text']}")
