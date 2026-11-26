import json, os

PROJ  = r"C:\AI\full studio\output\ht-av-261125"
AROLL = os.path.join(PROJ, "aroll")

tr = json.load(open(os.path.join(AROLL, "edited_raw_tr.json"), "r", encoding="utf-8"))

new_segs = []
for seg in tr["segments"]:
    ws = seg["words"]
    clean_w = []
    i = 0
    while i < len(ws):
        w = dict(ws[i])
        tok = w["word"].strip()
        st  = round(w["start"], 2)

        # Merge split tokens first
        if tok == "AV" and i + 1 < len(ws) and ws[i + 1]["word"].strip().lstrip("-").upper() == "PROTEIN":
            clean_w.append({"word": "AV", "start": w["start"], "end": w["end"]})
            clean_w.append({"word": "Protein", "start": ws[i + 1]["start"], "end": ws[i + 1]["end"]})
            i += 2
            continue
        if tok == "22" and i + 1 < len(ws) and "05" in ws[i + 1]["word"]:
            clean_w.append({"word": "22,05g", "start": w["start"], "end": ws[i + 1]["end"]})
            i += 2
            continue
        if tok == "1" and i + 1 < len(ws) and "632" in ws[i + 1]["word"]:
            clean_w.append({"word": "1.632mg", "start": w["start"], "end": ws[i + 1]["end"]})
            i += 2
            continue
        if tok == "L" and i + 1 < len(ws) and "leucine" in ws[i + 1]["word"].lower():
            clean_w.append({"word": "L-Leucine", "start": w["start"], "end": ws[i + 1]["end"]})
            i += 2
            continue

        # Exact word spelling fixes
        if tok == "căng":
            tok = "căng,"
        elif tok == "rời!":
            tok = "rượi!"
        elif tok == "bột" and st < 7.0:
            tok = "bột,"
        elif tok == "sạch" and 16.5 <= st <= 17.0:
            tok = "sạch,"
        elif tok == "nhìn" and 19.7 <= st <= 20.3:
            tok = "nhịn"
        elif tok == "đài" and 20.8 <= st <= 21.3:
            tok = "đại"
        elif tok == "gõi":
            tok = "gói"
        elif tok == "đàm" and 28.9 <= st <= 29.7:
            tok = "đạm"
        elif tok == "đầu" and 30.0 <= st <= 30.5:
            tok = "đậu"
        elif tok == "hãy" and 41.8 <= st <= 42.5:
            tok = "hay"
        elif tok == "ngạp":
            tok = "ngáp"
        elif tok == "đổ" and 46.1 <= st <= 46.7:
            tok = "đủ"
        elif tok == "đàm,":
            tok = "đạm,"

        clean_w.append({"word": tok, "start": w["start"], "end": w["end"]})
        i += 1

    new_segs.append({
        "start": clean_w[0]["start"],
        "end": clean_w[-1]["end"],
        "text": " ".join(x["word"] for x in clean_w),
        "words": clean_w,
    })

tr["segments"] = new_segs
out_p = os.path.join(AROLL, "main_cut_clean.json")
json.dump(tr, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("=== 100% PROOFREAD CLEAN TRANSCRIPT ===")
for s in new_segs:
    print(f"[{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}")
