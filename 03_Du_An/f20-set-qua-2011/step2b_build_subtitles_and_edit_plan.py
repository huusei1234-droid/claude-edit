import os, json

V2_DIR = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"

# 100% Proofread Vietnamese Subtitles synced to exact Whisper word timestamps in timeline_1117_master.json!
# Each entry: (start, end, line1, line2, [(emph_substr, "gold"|"ruby", pop_time), ...])
RAW_SUBS = [
    # Seg [02]a: 104 set quà -> Nha Trang 77 set & 13 set
    ( 4.20,  7.34, "Hôm nay bên Oanh đang chuẩn bị",        "104 SET QUÀ",                    [("104 SET QUÀ", "gold", 5.84)]),
    ( 7.36, 10.50, "cho các khách hàng đặt làm",            "QUÀ BIẾU TẶNG",                  [("QUÀ BIẾU TẶNG", "ruby", 9.88)]),
    (10.52, 13.28, "thầy cô giáo nhân dịp tri ân",          "NGÀY 20 THÁNG 11 ạ!",            [("NGÀY 20 THÁNG 11", "gold", 12.06)]),
    (13.40, 16.08, "Ở NHA TRANG thì có",                    "02 KHÁCH HÀNG:",                 [("NHA TRANG", "gold", 13.84), ("02 KHÁCH HÀNG:", "ruby", 14.70)]),
    (16.10, 18.52, "1 là ANH HẬU tại Trung tâm",            "Luyện Thi ĐĂNG KHOA EDU",        [("ANH HẬU", "gold", 16.30), ("ĐĂNG KHOA EDU", "gold", 17.90)]),
    (18.54, 19.82, "đặt số lượng lớn",                      "77 SET QUÀ!",                    [("77 SET QUÀ!", "gold", 18.86)]),
    (19.84, 22.64, "Khách thứ 2 là nhóm",                   "HỘI PHỤ HUYNH",                  [("HỘI PHỤ HUYNH", "gold", 21.94)]),
    (22.66, 24.06, "đặt thêm",                              "13 SET QUÀ!",                    [("13 SET QUÀ!", "ruby", 23.12)]),
    # Seg [02]a -> [02]b: Hà Nội 10 set & TP.HCM 4 set & Tổng 104 set
    (24.08, 27.86, "Khách thứ 3 là 1 bạn giáo viên",        "ở HÀ NỘI",                       [("HÀ NỘI", "gold", 27.48)]),
    (27.88, 28.80, "đặt ủng hộ",                            "10 SET QUÀ!",                    [("10 SET QUÀ!", "gold", 28.12)]),
    (28.82, 31.72, "Và 1 bạn ở tại",                        "TP. HỒ CHÍ MINH",                [("TP. HỒ CHÍ MINH", "gold", 30.38)]),
    (31.74, 32.88, "đặt thêm là",                           "04 SET QUÀ!",                    [("04 SET QUÀ!", "ruby", 32.24)]),
    (32.90, 35.52, "Tổng sáng ngày hôm nay",                "bên mình chuẩn bị",              [("Tổng sáng", "gold", 32.90)]),
    (35.54, 37.94, "trọn vẹn",                              "104 SET QUÀ nha mọi người!",     [("104 SET QUÀ", "gold", 35.80)]),
    # Seg [03] & [04]
    (38.10, 42.30, "Đây là những SET QUÀ bên Oanh",         "đã chuẩn bị xong sáng nay ạ!",   [("SET QUÀ", "gold", 39.16), ("chuẩn bị xong", "ruby", 40.26)]),
    (42.50, 45.20, "Bây giờ Oanh sẽ GIỚI THIỆU",            "01 SET QUÀ chi tiết",            [("GIỚI THIỆU", "gold", 43.68), ("01 SET QUÀ", "ruby", 44.48)]),
    (45.22, 47.18, "của bên Oanh cho mọi người",            "CÙNG XEM NHÉ!",                  [("CÙNG XEM NHÉ!", "gold", 46.36)]),
    # Seg [05]: 4 Món trong Set Quà
    (47.30, 50.98, "Một set quà tặng như thế này",          "bên trong sẽ gồm có:",           [("set quà tặng", "gold", 47.70)]),
    (51.02, 53.64, "Đầu tiên là",                           "01 SET YẾN SÀO CAO CẤP",         [("01 SET YẾN SÀO CAO CẤP", "gold", 51.62)]),
    (53.66, 56.62, "gồm 01 TỔ YẾN SÀO TINH CHẾ",            "sợi dài • dòng TIÊU CHUẨN",      [("01 TỔ YẾN SÀO TINH CHẾ", "gold", 53.90), ("TIÊU CHUẨN", "ruby", 56.08)]),
    (56.68, 58.88, "kèm theo cho mọi người đầy đủ",         "NGUYÊN LIỆU CHƯNG:",             [("NGUYÊN LIỆU CHƯNG:", "gold", 58.20)]),
    (58.90, 61.16, "TÁO ĐỎ • ĐÔNG TRÙNG HẠ THẢO",          "",                               [("TÁO ĐỎ", "ruby", 58.90), ("ĐÔNG TRÙNG HẠ THẢO", "gold", 59.88)]),
    (61.18, 62.78, "KỶ TỬ &",                               "01 HỘP ĐƯỜNG PHÈN!",             [("KỶ TỬ", "ruby", 61.20), ("01 HỘP ĐƯỜNG PHÈN!", "gold", 61.90)]),
    (62.82, 66.10, "Thứ 2 là sẽ có",                        "02 HỘP RONG BIỂN SẤY GIÒN",      [("02 HỘP RONG BIỂN SẤY GIÒN", "gold", 64.26)]),
    (66.12, 68.68, "01 hộp RONG BIỂN SẤY GIÒN",             "vị CAY NHẸ thơm ngon",           [("RONG BIỂN SẤY GIÒN", "gold", 66.86), ("CAY NHẸ", "ruby", 68.00)]),
    (68.70, 70.92, "và 01 hộp RONG BIỂN SẤY MÈ",            "vị KHÔNG CAY dễ ăn!",            [("RONG BIỂN SẤY MÈ", "gold", 69.46), ("KHÔNG CAY", "gold", 70.48)]),
    (71.00, 73.58, "Và thứ 3 sẽ có cho mình",               "01 GÓI BÁNH THUYỀN",             [("01 GÓI BÁNH THUYỀN", "gold", 73.10)]),
    (73.60, 76.48, "MIX HẠT DINH DƯỠNG",                    "trọng lượng 250G!",              [("MIX HẠT DINH DƯỠNG", "gold", 74.22), ("250G!", "ruby", 75.28)]),
    (76.60, 79.66, "Và thứ 4 sẽ có cho mình",               "01 GÓI LỚN",                     [("01 GÓI LỚN", "gold", 79.04)]),
    (79.68, 81.48, "RONG BIỂN KẸP HẠT",                     "trọng lượng 500G!",              [("RONG BIỂN KẸP HẠT", "gold", 79.70), ("500G!", "ruby", 80.56)]),
    (81.50, 84.84, "Ở trong này sẽ có từ",                  "22 ĐẾN 24 THANH",                [("22 ĐẾN 24 THANH", "gold", 83.32)]),
    (84.86, 86.50, "BÁNH HẠT DINH DƯỠNG",                   "nha mọi người!",                 [("BÁNH HẠT DINH DƯỠNG", "gold", 84.88)]),
    # Seg [06]: Sản phẩm giá trị nhất + Cẩm nang sử dụng
    (86.65, 89.66, "Sản phẩm GIÁ TRỊ NHẤT",                 "trong set quà ngày hôm nay",     [("GIÁ TRỊ NHẤT", "ruby", 87.70)]),
    (89.68, 93.35, "đó là set 01 TỔ YẾN SÀO TINH CHẾ",      "dòng tiêu chuẩn SỢI DÀI",        [("01 TỔ YẾN SÀO TINH CHẾ", "gold", 90.48), ("SỢI DÀI", "gold", 92.78)]),
    (93.86, 96.72, "được bên Oanh chuẩn bị thêm",           "01 TỜ CẨM NANG",                 [("01 TỜ CẨM NANG", "gold", 95.82)]),
    (96.74, 99.28, "SỬ DỤNG YẾN SÀO",                       "chu đáo cho mọi người!",         [("SỬ DỤNG YẾN SÀO", "gold", 97.70)]),
    (99.32,103.04, "Trong này có đầy đủ",                   "CÔNG DỤNG CỦA YẾN SÀO",          [("CÔNG DỤNG CỦA YẾN SÀO", "gold", 101.12)]),
    (103.10,106.42,"và HƯỚNG DẪN CHƯNG YẾN",                "ĐÚNG CÁCH cho mọi người nhé!",   [("HƯỚNG DẪN CHƯNG YẾN", "gold", 103.58), ("ĐÚNG CÁCH", "ruby", 105.22)]),
    # Seg [07]: Giỏ Mica + Quai Da Đỏ Đô + Hoa & Nơ Màu Be
    (106.55,110.22,"Các sản phẩm được bên Oanh xếp",        "trong GIỎ ĐỰNG QUÀ",             [("GIỎ ĐỰNG QUÀ", "gold", 109.36)]),
    (110.24,113.14,"chất liệu MICA TRONG SUỐT",             "như thế này nha mọi người!",     [("MICA TRONG SUỐT", "gold", 111.42)]),
    (113.18,116.64,"Ở bên trên sẽ có",                      "QUAI XÁCH BẰNG DA",              [("QUAI XÁCH BẰNG DA", "gold", 115.10)]),
    (116.66,118.26,"MÀU ĐỎ ĐÔ",                             "rất là SANG TRỌNG!",             [("MÀU ĐỎ ĐÔ", "ruby", 117.16), ("SANG TRỌNG!", "gold", 117.82)]),
    (118.30,122.44,"Thiết kế thêm vài BÔNG HOA",            "tạo ĐIỂM NHẤN tinh tế",          [("BÔNG HOA", "ruby", 121.30), ("ĐIỂM NHẤN", "gold", 122.06)]),
    (122.48,125.68,"và 1 chiếc NƠ MÀU BE",                  "rất là XINH XẮN như thế này!",   [("NƠ MÀU BE", "gold", 123.20), ("XINH XẮN", "ruby", 124.76)]),
    # Seg [08]: Trực tiếp sản xuất
    (125.80,129.10,"Đặc biệt các sản phẩm trong set",       "đều do bên Oanh",                [("Đặc biệt", "ruby", 125.80)]),
    (129.12,131.66,"TRỰC TIẾP SẢN XUẤT",                    "tại xưởng chuẩn sạch",           [("TRỰC TIẾP SẢN XUẤT", "gold", 129.96)]),
    (131.68,134.68,"nên mọi người cứ YÊN TÂM",              "về CHẤT LƯỢNG & GIÁ CẢ nhé!",    [("YÊN TÂM", "gold", 132.54), ("CHẤT LƯỢNG & GIÁ CẢ", "ruby", 133.24)]),
    # Seg [09]: Cảm ơn & CTA 20/11
    (134.80,137.84,"Oanh xin gửi LỜI CẢM ƠN",               "tới quý anh chị đã TIN TƯỞNG",   [("LỜI CẢM ƠN", "gold", 135.48), ("TIN TƯỞNG", "ruby", 137.34)]),
    (137.86,139.96,"và lựa chọn đặt hàng của",              "THỰC PHẨM F20!",                 [("THỰC PHẨM F20!", "gold", 139.08)]),
    (140.00,144.08,"Anh chị còn nhu cầu ĐẶT HÀNG",          "SET QUÀ TẶNG cao cấp",           [("ĐẶT HÀNG", "gold", 142.16), ("SET QUÀ TẶNG", "ruby", 143.36)]),
    (144.10,146.76,"biếu tặng nhân dịp",                    "LỄ TRI ÂN 20/11",                [("LỄ TRI ÂN 20/11", "gold", 145.76)]),
    (146.78,148.45,"hãy INBOX NGAY",                        "cho Oanh nhé!",                  [("INBOX NGAY", "ruby", 147.26)]),
]

# Top 2-Tier Luxury Brand Headers (with staggered T2 entry + In & Out SFX!)
TOP_HEADERS = [
    {"start":  0.15, "end":  4.05, "t1": "104 SET QUÀ TRI ÂN 20/11",         "t2": "Thực Phẩm F20 × Yến Sào SKA NEST",          "sfx_in": "magic_reveal", "sfx_out": "swoosh_out"},
    {"start":  4.40, "end": 13.10, "t1": "ĐƠN HÀNG SÁNG NAY • 104 SET QUÀ",  "t2": "Quà Biếu Tri Ân Thầy Cô Giáo 20/11",        "sfx_in": "whoosh_tvc",   "sfx_out": "swoosh_out"},
    {"start": 16.10, "end": 20.10, "t1": "ANH HẬU • ĐĂNG KHOA EDU",          "t2": "Nha Trang • Đặt 77 Set Quà Tri Ân",         "sfx_in": "notif_bell",   "sfx_out": "swoosh_out"},
    {"start": 20.30, "end": 24.15, "t1": "HỘI PHỤ HUYNH • NHA TRANG",        "t2": "Đặt 13 Set Quà Biếu Thầy Cô",               "sfx_in": "pop_tvc",      "sfx_out": "swoosh_out"},
    {"start": 24.40, "end": 32.95, "t1": "SHIP TOÀN QUỐC • HÀ NỘI & TP.HCM", "t2": "Giáo Viên Hà Nội 10 Set • TP.HCM 04 Set",   "sfx_in": "whoosh_tvc",   "sfx_out": "swoosh_out"},
    {"start": 33.20, "end": 42.20, "t1": "HOÀN THIỆN 104 SET QUÀ SÁNG NAY",  "t2": "Chỉn Chu • Sang Trọng • Đúng Hẹn",          "sfx_in": "shine_accent", "sfx_out": "swoosh_out"},
    {"start": 51.40, "end": 63.05, "t1": "MÓN 01/04 • TỔ YẾN SÀO TINH CHẾ",  "t2": "Nguyên Tổ Sợi Dài + 04 Nguyên Liệu Chưng",  "sfx_in": "magic_reveal", "sfx_out": "fairy_out"},
    {"start": 63.15, "end": 71.05, "t1": "MÓN 02/04 • 02 HỘP RONG BIỂN F20", "t2": "01 Sấy Giòn Cay Nhẹ • 01 Sấy Mè Không Cay", "sfx_in": "whoosh_tvc",   "sfx_out": "swoosh_out"},
    {"start": 71.18, "end": 76.65, "t1": "MÓN 03/04 • BÁNH THUYỀN MIX HẠT",  "t2": "Gói 250g • Giòn Thơm Giàu Dinh Dưỡng",      "sfx_in": "whoosh_tvc",   "sfx_out": "swoosh_out"},
    {"start": 76.80, "end": 86.65, "t1": "MÓN 04/04 • RONG BIỂN KẸP HẠT",    "t2": "Gói Lớn 500g • 22 – 24 Thanh Hạt",          "sfx_in": "whoosh_tvc",   "sfx_out": "swoosh_out"},
    {"start": 87.00, "end":106.45, "t1": "YẾN SÀO SKA NEST • GIÁ TRỊ NHẤT",  "t2": "Tặng Kèm Cẩm Nang Công Dụng & Cách Chưng",  "sfx_in": "shine_accent", "sfx_out": "swoosh_out"},
    {"start":106.80, "end":125.75, "t1": "GIỎ QUÀ MICA SANG TRỌNG",          "t2": "Quai Da Đỏ Đô • Hoa Điểm Nhấn & Nơ Màu Be", "sfx_in": "whoosh_tvc",   "sfx_out": "swoosh_out"},
    {"start":126.05, "end":134.85, "t1": "THỰC PHẨM F20 TRỰC TIẾP SẢN XUẤT", "t2": "Cam Kết Chất Lượng Chuẩn & Giá Gốc Tận Xưởng","sfx_in": "notif_bell", "sfx_out": "swoosh_out"},
]

# Rhythm Camera Zoom Keyframe Pulses (zoom in on emphasis word -> hold -> zoom out smoothly!)
# Tuple: (t_in_start, t_peak, t_hold_end, t_out_end, peak_scale)
RHYTHM_ZOOMS = [
    ( 5.65,  6.05,  6.85,  7.75, 1.090),  # "104 SET QUÀ"
    (11.90, 12.30, 12.95, 13.55, 1.080),  # "20 THÁNG 11"
    (14.55, 14.90, 15.50, 16.05, 1.075),  # "02 KHÁCH HÀNG"
    (18.65, 19.00, 19.65, 20.15, 1.095),  # "77 SET QUÀ"
    (20.90, 21.30, 21.85, 22.30, 1.070),  # "KHÁCH THỨ 2"
    (35.55, 35.95, 36.95, 37.80, 1.095),  # "104 SET QUÀ"
    (43.55, 44.00, 44.85, 45.75, 1.085),  # "GIỚI THIỆU 01 SET QUÀ"
    (87.50, 87.95, 88.90, 89.85, 1.090),  # "GIÁ TRỊ NHẤT"
    (101.00,101.45,102.35,103.15, 1.075), # "CÔNG DỤNG YẾN SÀO"
    (108.80,109.25,110.05,110.75, 1.080), # "GIỎ ĐỰNG QUÀ"
    (119.30,119.80,120.75,121.55, 1.075), # "THIẾT KẾ THÊM HOA"
    (126.00,126.45,127.40,128.40, 1.080), # "ĐẶC BIỆT"
    (135.30,135.75,136.85,137.80, 1.075), # "LỜI CẢM ƠN"
    (138.90,139.30,139.95,140.45, 1.095), # "THỰC PHẨM F20"
    (145.60,146.00,146.75,147.55, 1.090), # "LỄ 20/11 - INBOX NGAY"
]

# Verify strict monotonicity of subtitle intervals
subs_out = []
for i, (s0, s1, l1, l2, ems) in enumerate(RAW_SUBS):
    if i > 0 and s0 < subs_out[-1]["end"]:
        subs_out[-1]["end"] = round(s0 - 0.02, 3)
    subs_out.append({
        "idx": i,
        "start": round(s0, 3),
        "end": round(s1, 3),
        "line1": l1,
        "line2": l2,
        "emphasis": [{"text": e[0], "style": e[1], "t_pop": round(e[2], 3)} for e in ems],
    })

plan = {
    "subtitles": subs_out,
    "top_headers": TOP_HEADERS,
    "rhythm_zooms": RHYTHM_ZOOMS,
}
out_p = os.path.join(V2_DIR, "subtitles_v2_plan.json")
json.dump(plan, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Saved {out_p}: {len(subs_out)} subtitles, {len(TOP_HEADERS)} top headers, {len(RHYTHM_ZOOMS)} rhythm zoom beats!")
