import json, os, re

PROJ = r"d:\AI\full studio\output\htpm6-261121"
in_p  = os.path.join(PROJ, "aroll", "main_cut.json")
out_p = os.path.join(PROJ, "aroll", "main_cut_clean.json")

tr = json.load(open(in_p, "r", encoding="utf-8"))

# Exact contextual word-level corrections verified against spoken audio of HTPM.mp4
for seg in tr["segments"]:
    ws = seg.get("words", [])
    for i, w in enumerate(ws):
        tok = w["word"].strip()
        ts  = round(w["start"], 2)
        # 7.66s: "Hằng sẽ có mua tuổi hiệu" -> "Hằng sẽ không mua túi hiệu."
        if 7.55 <= ts <= 7.75 and tok == "có":
            w["word"] = " không"
        if tok in ("tuổi", "tuổi,") and i + 1 < len(ws) and ws[i + 1]["word"].strip().startswith("hiệu"):
            w["word"] = " túi"
        # 11.12-11.36s: "trưởng thanh," -> "trưởng thành,"
        if tok.startswith("thanh") and i > 0 and ws[i - 1]["word"].strip() == "trưởng":
            w["word"] = " thành,"
        # 16.66-16.84s: "Một trực tuổi đẹp" -> "Một chiếc túi đẹp"
        if 16.55 <= ts <= 16.75 and tok == "trực":
            w["word"] = " chiếc"
        if 16.75 <= ts <= 16.95 and tok == "tuổi":
            w["word"] = " túi"
        # 19.46-19.70s: "một bồ quân áo đẹp" -> "một bộ quần áo đẹp"
        if 19.35 <= ts <= 19.58 and tok == "bồ":
            w["word"] = " bộ"
        if 19.58 <= ts <= 19.82 and tok == "quân":
            w["word"] = " quần"
        # 22.94s: "một lập trang điểm đẹp" -> "một lớp trang điểm đẹp"
        if 22.80 <= ts <= 23.05 and tok == "lập":
            w["word"] = " lớp"
        # 34.18s: "sức khỏe phù khoa," -> "sức khỏe phụ khoa,"
        if 34.05 <= ts <= 34.30 and tok == "phù":
            w["word"] = " phụ"
        # 45.16s: "trên mạng tiến dắt" -> "trên mạng dẫn dắt."
        if 45.05 <= ts <= 45.28 and tok == "tiến":
            w["word"] = " dẫn"
        if 45.28 <= ts <= 45.50 and tok == "dắt":
            w["word"] = " dắt."
        # 55.92s & 58.08s: "đồ tuổi" -> "độ tuổi"
        if tok == "đồ" and i + 1 < len(ws) and ws[i + 1]["word"].strip().startswith("tuổi"):
            w["word"] = " độ"
        # 57.92s: "đang đồ tuổi" -> "đang ở độ tuổi"
        if 57.85 <= ts <= 58.00 and tok == "đang":
            w["word"] = " đang ở"
        # 58.50-59.50s: "30 -40 còng," -> "30 - 40+,"
        if 58.80 <= ts <= 59.05 and tok == "-40":
            w["word"] = "-40+"
        if 59.30 <= ts <= 59.65 and tok.startswith("còng"):
            w["word"] = ""
        # 62.60-63.50s: verbal stumble "có những người, có những điều" -> drop stumble so subtitle reads cleanly "có những điều phụ nữ càng biết sớm"
        if 62.55 <= ts <= 63.55 and tok in ("có", "những", "người,"):
            w["word"] = ""
        # Punctuation polish on end of sentences
        if 35.30 <= ts <= 35.50 and tok == "thức":
            w["word"] = " thức."
        if 38.60 <= ts <= 38.80 and tok == "đình":
            w["word"] = " đình."
        if 41.10 <= ts <= 41.35 and tok == "hơn":
            w["word"] = " hơn."
        if 50.25 <= ts <= 50.45 and tok == "nó":
            w["word"] = " nó."
        if 67.60 <= ts <= 67.85 and tok == "đấy":
            w["word"] = " đấy!"

    seg["words"] = [w for w in ws if w["word"].strip()]
    seg["text"] = " ".join(w["word"].strip() for w in seg["words"])

tr["segments"] = [s for s in tr["segments"] if s["words"]]
json.dump(tr, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("=== CLEANED VERBATIM TRANSCRIPT ===")
for s in tr["segments"]:
    print(f"[{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}")
