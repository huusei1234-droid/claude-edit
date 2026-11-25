import json, os

AROLL = r"d:\AI\full studio\output\htpm-20261119\aroll"
raw = json.load(open(os.path.join(AROLL, "main_cut.json"), encoding="utf-8"))

# Flatten all words for exact timestamp-preserving spellcheck
words = []
for seg in raw["segments"]:
    for w in seg["words"]:
        words.append({"start": round(w["start"], 3), "end": round(w["end"], 3), "word": w["word"].strip(), "p": w.get("p", 1.0)})

for i, w in enumerate(words):
    t = w["start"]
    txt = w["word"]
    if 6.25 <= t <= 6.55 and txt == "sửa":
        w["word"] = "sữa"
    elif 6.45 <= t <= 6.68 and txt == "đồ":
        w["word"] = "rửa"
    elif 9.85 <= t <= 10.15 and txt == "đổ":
        w["word"] = "đổi"
    elif 11.80 <= t <= 12.10 and txt == "là":
        w["word"] = "làn"
    elif 14.70 <= t <= 15.10 and txt.startswith("mùn"):
        w["word"] = "mụn,"
    elif 15.85 <= t <= 16.25 and txt.startswith("rạp"):
        w["word"] = "ráp,"
    elif 27.40 <= t <= 27.75 and txt == "phẩm":
        w["word"] = "phẩm."
    elif 29.95 <= t <= 30.35 and txt == "nhỏ":
        w["word"] = "nhỏ."
    elif 31.50 <= t <= 31.88 and txt == "trực":
        w["word"] = "trước"
    elif 31.80 <= t <= 32.10 and txt == "hiện":
        w["word"] = "hết"
    elif 32.80 <= t <= 33.22 and txt == "khỏe":
        w["word"] = "khỏe."
    elif 36.55 <= t <= 36.88 and txt == "tố":
        w["word"] = "tố:"
    elif 37.30 <= t <= 37.60 and txt == "nồi":
        w["word"] = "nội"
    elif 37.50 <= t <= 37.82 and txt == "tiệt":
        w["word"] = "tiết"
    elif 38.65 <= t <= 38.92 and txt == "đồ":
        w["word"] = "độ"
    elif 39.90 <= t <= 40.35 and txt == "ngủ":
        w["word"] = "ngủ,"
    elif 42.65 <= t <= 43.02 and txt == "sống":
        w["word"] = "sống,"
    elif 42.95 <= t <= 43.65 and txt == "Tiêu":
        w["word"] = "tia"
    elif 43.60 <= t <= 43.98 and txt == "vê":
        w["word"] = "UV"
    elif 45.80 <= t <= 46.10 and txt == "ngày":
        w["word"] = "ngày."
    elif 49.20 <= t <= 49.50 and txt == "đó":
        w["word"] = "đó,"
    elif 52.00 <= t <= 52.32 and txt == "vững":
        w["word"] = "vững."
    elif 55.90 <= t <= 56.20 and txt == "vậy":
        w["word"] = "vậy."
    elif 60.15 <= t <= 60.50 and txt == "bằng":
        w["word"] = "bằng,"
    elif 63.15 <= t <= 63.62 and txt == "tiên":
        w["word"] = "tiên."
    elif 66.25 <= t <= 66.65 and txt == "tốt":
        w["word"] = "tốt,"
    elif 69.85 <= t <= 70.18 and txt == "đâu":
        w["word"] = "đâu,"
    elif 71.65 <= t <= 71.98 and txt == "đâu":
        w["word"] = "đâu."
    elif 75.90 <= t <= 76.30 and txt == "quả":
        w["word"] = "quả."

clean_obj = {
    "lang": "vi",
    "duration": raw["duration"],
    "segments": [{"start": words[0]["start"], "end": words[-1]["end"], "text": " ".join(w["word"] for w in words), "words": words}]
}
out_p = os.path.join(AROLL, "main_cut_clean.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(clean_obj, f, ensure_ascii=False, indent=2)
print("Saved clean transcript:", clean_obj["segments"][0]["text"])
