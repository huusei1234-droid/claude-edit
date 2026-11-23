import json, os

PROJ  = r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da"
AROLL = os.path.join(PROJ, "aroll")

tr = json.load(open(os.path.join(AROLL, "main_cut.json"), encoding="utf-8"))

# Exact word-level fixes preserving every Whisper timestamp!
def fix_seg_words(seg_idx, replacements, full_text):
    ws = tr["segments"][seg_idx]["words"]
    for idx_or_old, new_w in replacements:
        if isinstance(idx_or_old, int):
            ws[idx_or_old]["word"] = new_w
        else:
            for w in ws:
                if w["word"].strip() == idx_or_old:
                    w["word"] = new_w
    tr["segments"][seg_idx]["text"] = full_text

fix_seg_words(0, [(-1, "da!")], "Những sai lầm khi chăm sóc da!")
fix_seg_words(1, [(-1, "phải.")], "Theo kinh nghiệm của Hằng, có 3 sai lầm phổ biến mà rất nhiều người đang mắc phải.")
fix_seg_words(2, [(-1, "mức.")], "Đầu tiên, đó là làm sạch quá mức.")
fix_seg_words(3, [("mùn", "mụn.")], "Nhiều bạn nghĩ rằng, da dầu là phải rửa mặt thật nhiều lần trong ngày thì mới sạch và hạn chế nổi mụn.")
fix_seg_words(4, [(-1, "mạnh,")], "Nhưng thực tế, khi mình rửa mặt quá nhiều hoặc sử dụng sản phẩm làm sạch quá mạnh,")
fix_seg_words(5, [("lập", "lớp"), ("mang", "màng"), (-1, "thương.")], "thì lớp màng bảo vệ tự nhiên của da sẽ bị tổn thương.")
fix_seg_words(6, [("nhơn", "nhờn"), ("bu", "bù"), ("mắt", "mất.")], "Da sẽ mất nước, mất độ ẩm và tuyến bã nhờn lại hoạt động mạnh mẽ hơn để bù lại lượng dầu đã mất.")
fix_seg_words(7, [(4, "lại"), ("bỏng", "bóng"), ("nhau", "nhờn"), (-1, "ngoài.")], "Kết quả là da lại khô bên trong nhưng lại càng bóng nhờn bên ngoài.")
fix_seg_words(8, [("chảy", "chạy"), (-1, "hướng.")], "Sai lầm thứ 2 đó chính là chạy theo xu hướng.")
fix_seg_words(9, [(-1, "dùng,")], "Chỉ cần thấy một sản phẩm được nhiều người khen là lập tức mua về dùng,")
fix_seg_words(10, [("loài", "loại"), (-1, "không.")], "mà không biết sản phẩm đó có phù hợp với loại da của mình hay không.")
fix_seg_words(11, [("giàu,", "dầu,"), ("hồn", "hỗn"), ("nhảy", "nhạy"), (-1, "nhau.")], "Da dầu, da khô, da hỗn hợp hay da nhạy cảm sẽ có nhu cầu hoàn toàn khác nhau.")
fix_seg_words(12, [(-1, "khác.")], "Có những sản phẩm rất tốt với người này nhưng lại kích ứng cho người khác.")
fix_seg_words(13, [(-1, "trong.")], "Và sai lầm cuối cùng là chỉ chăm sóc bên ngoài mà quên mất bên trong.")
fix_seg_words(14, [(0, "Hằng"), ("đông", "đồng"), ("trong", "cho"), (-1, "phẩm,")], "Hằng gặp rất nhiều chị em đầu tư hàng trăm triệu đồng cho mỹ phẩm,")

# Merge "1" + "-2" -> "1–2" in segment 15
s15 = tr["segments"][15]["words"]
s15_new = []
k = 0
while k < len(s15):
    if s15[k]["word"].strip() == "1" and k + 1 < len(s15) and s15[k + 1]["word"].strip() == "-2":
        s15_new.append({"start": s15[k]["start"], "end": s15[k + 1]["end"], "word": "1–2", "p": 0.99})
        k += 2
        continue
    s15_new.append(dict(s15[k]))
    k += 1
s15_new[-1]["word"] = "sáng,"
tr["segments"][15]["words"] = s15_new
tr["segments"][15]["text"] = "nhưng lại thường xuyên thức đến 1–2 giờ sáng,"

fix_seg_words(16, [(-1, "nhanh.")], "uống rất ít nước, ăn nhiều đồ ngọt và thức ăn nhanh.")
fix_seg_words(17, [("hình", "trường"), (-1, "đâu,")], "Trong trường hợp đó thì dù mỹ phẩm tốt đến đâu,")
fix_seg_words(18, [(-1, "muốn.")], "cũng rất khó mang lại hiệu quả như mong muốn.")

# Fix "tim" -> "tìm" and split/fix "Lanza" -> "làn da." in segment 19!
s19 = tr["segments"][19]["words"]
s19_new = []
for w in s19:
    wt = w["word"].strip()
    if wt == "tim":
        w2 = dict(w); w2["word"] = "tìm"; s19_new.append(w2)
    elif wt == "Lanza":
        mid = round((w["start"] + w["end"]) * 0.5, 3)
        s19_new.append({"start": w["start"], "end": mid, "word": "làn", "p": 0.99})
        s19_new.append({"start": mid, "end": w["end"], "word": "da.", "p": 0.99})
    else:
        s19_new.append(dict(w))
tr["segments"][19]["words"] = s19_new
tr["segments"][19]["text"] = "Đừng cố tìm một sản phẩm có thể giải quyết mọi vấn đề của làn da."

fix_seg_words(20, [(-1, "mình.")], "Hãy bắt đầu bằng việc thay đổi những thói quen chưa đúng của chính mình.")
fix_seg_words(21, [(-1, "đúng,")], "Khi nền tảng chăm sóc đã đúng,")
fix_seg_words(22, [(-1, "nhiều!")], "việc lựa chọn sản phẩm phù hợp sẽ trở nên hiệu quả hơn rất nhiều!")

out_p = os.path.join(AROLL, "main_cut_clean.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(tr, f, ensure_ascii=False, indent=2)

for idx, s in enumerate(tr["segments"]):
    print(f"[{idx:02d}] {s['start']:5.2f}-{s['end']:5.2f}: {' '.join(w['word'] for w in s['words'])}")
