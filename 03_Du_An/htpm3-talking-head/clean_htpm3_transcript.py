import json, os

PROJ  = r"d:\AI\full studio\output\htpm3-talking-head"
AROLL = os.path.join(PROJ, "aroll")

tr = json.load(open(os.path.join(AROLL, "main_cut.json"), encoding="utf-8"))

# Exact word-by-word medical & brand spellcheck preserving original Whisper timestamps!
# Segment 0: "Viêm phụ khoa, hết rồi, tại sao vẫn quay lại?"
s0 = tr["segments"][0]["words"]
s0[0]["word"] = "Viêm"
s0[-1]["word"] = "lại?"
tr["segments"][0]["text"] = "Viêm phụ khoa, hết rồi, tại sao vẫn quay lại?"

# Segment 1: "Có rất nhiều chị em nhắn cho Hằng rằng, em vừa điều trị xong được vài tuần thì lại ngứa và khí hư bất thường."
s1 = tr["segments"][1]["words"]
for w in s1:
    if w["word"].strip() == "khỉ":
        w["word"] = "khí"
s1[-1]["word"] = "thường."
tr["segments"][1]["text"] = "Có rất nhiều chị em nhắn cho Hằng rằng, em vừa điều trị xong được vài tuần thì lại ngứa và khí hư bất thường."

# Segment 2: "...sau khi hết triệu chứng, môi trường vùng kín vẫn chưa được thực sự phục hồi."
s2 = tr["segments"][2]["words"]
for w in s2:
    if w["word"].strip() == "triều":
        w["word"] = "triệu"
s2[-1]["word"] = "hồi."
tr["segments"][2]["text"] = "Nguyên nhân đôi khi không phải nằm ở việc điều trị chưa đủ, mà là sau khi hết triệu chứng, môi trường vùng kín vẫn chưa được thực sự phục hồi."

# Segment 3: "Nếu độ pH còn mất cân bằng hoặc niêm mạc vẫn nhạy cảm, nấm và vi khuẩn rất dễ phát triển trở lại."
# Original words[0..4]: "Nếu"(17.84-18.3), "đồ"(18.3-18.5), "bé"(18.5-18.62), "hạt"(18.62-18.78), "còn"(18.78-19.02)
# Merge "bé" + "hạt" -> "pH" (18.50 - 18.78) and "đồ" -> "độ"!
s3_old = tr["segments"][3]["words"]
s3_new = []
i = 0
while i < len(s3_old):
    w = dict(s3_old[i])
    wt = w["word"].strip()
    if wt == "đồ":
        w["word"] = "độ"
        s3_new.append(w)
    elif wt == "bé" and i + 1 < len(s3_old) and s3_old[i + 1]["word"].strip() == "hạt":
        s3_new.append({"start": w["start"], "end": s3_old[i + 1]["end"], "word": "pH", "p": 0.99})
        i += 2
        continue
    elif wt == "băng":
        w["word"] = "bằng"
        s3_new.append(w)
    elif wt == "miêm":
        w["word"] = "niêm"
        s3_new.append(w)
    elif wt == "bạc":
        w["word"] = "mạc"
        s3_new.append(w)
    else:
        s3_new.append(w)
    i += 1
s3_new[-1]["word"] = "lại."
tr["segments"][3]["words"] = s3_new
tr["segments"][3]["text"] = "Nếu độ pH còn mất cân bằng hoặc niêm mạc vẫn nhạy cảm, nấm và vi khuẩn rất dễ phát triển trở lại."

# Segment 4: "...Acid Lactic để hỗ trợ cân bằng pH kết hợp với Niacinamide và Glycerin"
s4 = tr["segments"][4]["words"]
for w in s4:
    if w["word"].strip() == "Latic":
        w["word"] = "Lactic"
tr["segments"][4]["text"] = "Đó là lý do vì sao Hằng thường ưu tiên các sản phẩm có Acid Lactic để hỗ trợ cân bằng pH kết hợp với Niacinamide và Glycerin"

# Segment 5: "giúp duy trì độ ẩm, cùng Cam Thảo và Cúc La Mã hỗ trợ làm dịu niêm mạc."
s5 = tr["segments"][5]["words"]
for idx, w in enumerate(s5):
    wt = w["word"].strip()
    if wt == "đồ": w["word"] = "độ"
    elif wt == "ẩm": w["word"] = "ẩm,"
    elif wt == "cam": w["word"] = "Cam"
    elif wt == "thảo": w["word"] = "Thảo"
    elif wt == "cúc": w["word"] = "Cúc"
    elif wt == "la": w["word"] = "La"
    elif wt == "mã": w["word"] = "Mã"
    elif wt == "hạng": w["word"] = "mạc."
tr["segments"][5]["text"] = "giúp duy trì độ ẩm, cùng Cam Thảo và Cúc La Mã hỗ trợ làm dịu niêm mạc."

# Segment 6: "Viên đặt phụ khoa Hằng Thu được xây dựng theo hướng chăm sóc vùng kín một cách nhẹ nhàng như vậy."
s6 = tr["segments"][6]["words"]
for w in s6:
    wt = w["word"].strip()
    if wt == "phù": w["word"] = "phụ"
    elif wt == "qua": w["word"] = "khoa"
    elif wt == "vung": w["word"] = "vùng"
    elif wt == "kì": w["word"] = "kín"
s6[-1]["word"] = "vậy."
tr["segments"][6]["text"] = "Viên đặt phụ khoa Hằng Thu được xây dựng theo hướng chăm sóc vùng kín một cách nhẹ nhàng như vậy."

# Segment 7: "Điều trị rất quan trọng, nhưng chăm sóc đúng sau đó mới là chìa khóa giúp hạn chế tái phát chị em nhé!"
s7 = tr["segments"][7]["words"]
for w in s7:
    wt = w["word"].strip()
    if wt == "trì": w["word"] = "trị"
    elif wt == "trọng": w["word"] = "trọng,"
    elif wt == "chia": w["word"] = "chìa"
    elif wt == "hàn": w["word"] = "hạn"
    elif wt == "tài": w["word"] = "tái"
    elif wt == "pháp": w["word"] = "phát"
    elif wt == "nhé": w["word"] = "nhé!"
tr["segments"][7]["text"] = "Điều trị rất quan trọng, nhưng chăm sóc đúng sau đó mới là chìa khóa giúp hạn chế tái phát chị em nhé!"

out_p = os.path.join(AROLL, "main_cut_clean.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(tr, f, ensure_ascii=False, indent=2)

for idx, s in enumerate(tr["segments"]):
    ws = " ".join(w["word"] for w in s["words"])
    print(f"Seg {idx} [{s['start']:5.2f}-{s['end']:5.2f}]: {ws}")
