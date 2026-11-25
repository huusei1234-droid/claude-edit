import json, os

AROLL = r"d:\AI\full studio\output\htpm-ddvs-2\aroll"
src = os.path.join(AROLL, "main_cut.json")
dst = os.path.join(AROLL, "main_cut_clean.json")

d = json.load(open(src, encoding="utf-8"))

# Word-level exact replacements by (segment_idx, word_idx) or exact token fixes
SEG_FIXES = {
    0: {7: "sóc!"},
    1: {11: "ngày."},
    2: {7: "tìm", 12: "ngứa,", 19: "thường."},
    3: {10: "bằng,", 12: "vi", 19: "hơn."},
    4: {3: "trị", 9: "hơn."},
    5: {4: "rằng:", 5: "phòng", 12: "trị."},
    6: {1: "vậy,", 25: "nhau."},
    7: {4: "hằng", 15: "dịu", 18: "Romance VIP."},
    8: {12: "hội,", 13: "Vitamin", 14: "E,"},
    9: {0: "kết", 3: "Collagen", 11: "dịu", 12: "nhẹ,"},
    10: {0: "hỗ", 11: "và", 17: "thoáng,", 19: "chịu."},  # "đồ bế hạt" handled specially below!
    11: {3: "kín", 18: "chịu,"},
    12: {0: "thì", 8: "Viên", 10: "phụ", 12: "Hằng", 13: "Thu", 15: "nha."},
    13: {5: "Acid", 6: "Lactic,", 9: "nữ", 13: "chiết", 14: "xuất", 23: "khác,"},
    14: {12: "Niacinamide", 14: "Glycerin,"},
    15: {2: "dịu,", 13: "kín."},
    16: {5: "bộ", 14: "diện."},
    17: {10: "ngày."},
    18: {16: "hồi."},
    19: {14: "nhất."},
    20: {2: "vùng", 3: "kín", 16: "sống,"},
    21: {0: "mà", 12: "dài."},
}

for si, seg in enumerate(d["segments"]):
    wlist = seg["words"]
    if si in SEG_FIXES:
        for wi, new_w in SEG_FIXES[si].items():
            if wi < len(wlist):
                wlist[wi]["word"] = new_w

    # Collapse 3-word "đồ bế hạt" / "đồ bé hạt" into 2-word "độ" + "pH"
    new_words = []
    i = 0
    while i < len(wlist):
        if (
            i + 2 < len(wlist)
            and wlist[i]["word"] == "đồ"
            and wlist[i + 1]["word"] in ("bế", "bé")
            and wlist[i + 2]["word"] == "hạt"
        ):
            new_words.append({"start": wlist[i]["start"], "end": wlist[i]["end"], "word": "độ", "p": 0.99})
            new_words.append({"start": wlist[i + 1]["start"], "end": wlist[i + 2]["end"], "word": "pH", "p": 0.99})
            i += 3
        else:
            new_words.append(wlist[i])
            i += 1

    # Also split "Romance VIP." into "Romance" + "VIP." so each word spaces naturally!
    final_words = []
    for w in new_words:
        if w["word"] == "Romance VIP.":
            mid = round((w["start"] + w["end"]) * 0.5, 3)
            final_words.append({"start": w["start"], "end": mid, "word": "Romance", "p": 0.99})
            final_words.append({"start": mid, "end": w["end"], "word": "VIP.", "p": 0.99})
        else:
            final_words.append(w)

    seg["words"] = final_words
    seg["text"] = " ".join(w["word"] for w in final_words)

with open(dst, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

for si, seg in enumerate(d["segments"]):
    print(f"{si:02d} [{seg['start']:6.2f}-{seg['end']:6.2f}] {seg['text']}")
