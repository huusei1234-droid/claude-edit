import json, os

OUT = r"d:\AI\full studio\output\f20-set-qua-2011"

# 43 Proofread, Frame-Synced Continuous Subtitles (Text Sub) with Keyword Highlights!
SUBTITLES = [
    (  0.14,   2.28, "Đây là những set quà bên Oanh",                  ["set quà", "Oanh"]),
    (  2.28,   4.72, "đã chuẩn bị đóng sẵn ngày hôm nay ạ",            ["đóng sẵn"]),
    (  4.95,   7.91, "Bây giờ Oanh sẽ giới thiệu 1 set quà",           ["1 set quà"]),
    (  7.91,   9.80, "của bên Oanh cho mọi người cùng xem nhé!",       ["cùng xem nhé!"]),
    (  9.95,  12.71, "Một set quà tặng như thế này thì",               ["set quà tặng"]),
    ( 12.71,  15.95, "bên trong sẽ gồm có 1 set yến sào",              ["1 set yến sào"]),
    ( 15.95,  18.75, "gồm 1 tổ yến sào tinh chế sợi dài",              ["tổ yến sào tinh chế", "sợi dài"]),
    ( 18.75,  21.47, "dòng tiêu chuẩn kèm nguyên liệu chưng:",         ["nguyên liệu chưng:"]),
    ( 21.47,  23.55, "Táo đỏ, đông trùng hạ thảo,",                    ["Táo đỏ,", "đông trùng hạ thảo,"]),
    ( 23.65,  25.38, "kỷ tử và 1 hộp đường phèn.",                     ["kỷ tử", "đường phèn."]),
    ( 25.45,  28.69, "Thứ 2 là sẽ có 2 hộp rong biển sấy giòn:",       ["Thứ 2", "2 hộp rong biển sấy giòn:"]),
    ( 28.75,  31.38, "1 hộp là rong biển sấy giòn cay nhẹ",            ["sấy giòn cay nhẹ"]),
    ( 31.45,  33.65, "và 1 hộp là rong biển sấy mè không cay.",        ["sấy mè không cay."]),
    ( 34.25,  36.65, "Và thứ 3 là sẽ có cho mình",                     ["thứ 3"]),
    ( 36.65,  39.65, "1 gói bánh thuyền mix hạt dinh dưỡng 250g.",     ["bánh thuyền mix hạt", "250g."]),
    ( 40.05,  42.69, "Và thứ 4 là sẽ có cho mình",                     ["thứ 4"]),
    ( 42.69,  44.82, "1 gói rong biển kẹp hạt 500g.",                  ["rong biển kẹp hạt", "500g."]),
    ( 44.88,  47.49, "Túi như thế này thì sẽ có từ 22",                ["từ 22"]),
    ( 47.49,  49.90, "đến 24 thanh bánh hạt dinh dưỡng nha!",          ["24 thanh bánh hạt"]),
    ( 49.96,  52.39, "Các sản phẩm sẽ được bên Oanh xếp",              ["bên Oanh xếp"]),
    ( 52.39,  55.25, "trong 1 giỏ đựng quà chất liệu mica",            ["giỏ đựng quà", "mica"]),
    ( 55.25,  56.75, "trong suốt như thế này nha mọi người.",          ["trong suốt"]),
    ( 56.95,  59.87, "Ở bên trên sẽ có quai xách bằng da",             ["quai xách bằng da"]),
    ( 59.87,  61.80, "màu đỏ đô rất là sang trọng.",                   ["màu đỏ đô", "sang trọng."]),
    ( 61.88,  64.95, "Mình có thiết kế thêm một vài bông hoa",         ["vài bông hoa"]),
    ( 64.95,  66.75, "tạo điểm nhấn và một chiếc nơ",                  ["điểm nhấn", "chiếc nơ"]),
    ( 66.75,  68.86, "màu be rất là xinh xắn như thế này.",            ["màu be", "xinh xắn"]),
    ( 68.92,  71.75, "Giá trị nhất của set quà ngày hôm nay",          ["Giá trị nhất"]),
    ( 71.75,  74.31, "đó là set 1 tổ yến sào tinh chế",                ["1 tổ yến sào tinh chế"]),
    ( 74.31,  76.72, "tiêu chuẩn cao cấp của Yến Sào SKA NEST.",       ["cao cấp", "Yến Sào SKA NEST."]),
    ( 76.80,  79.61, "Trong set quà này bên Oanh chuẩn bị thêm",       ["chuẩn bị thêm"]),
    ( 79.61,  82.76, "cho mọi người 1 tờ cẩm nang sử dụng yến sào.",   ["cẩm nang sử dụng yến sào."]),
    ( 82.84,  85.30, "Mọi người xem được công dụng của yến sào,",      ["công dụng của yến sào,"]),
    ( 85.38,  88.05, "và thứ hai nữa là có hướng dẫn",                 ["hướng dẫn"]),
    ( 88.05,  90.20, "chưng yến đúng cách cho mọi người luôn nhé!",    ["chưng yến đúng cách"]),
    ( 90.28,  93.05, "Đặc biệt các sản phẩm trong set quà này",        ["Đặc biệt"]),
    ( 93.05,  95.04, "đều do bên Oanh trực tiếp sản xuất,",            ["trực tiếp sản xuất,"]),
    ( 95.10,  98.42, "nên mọi người yên tâm về chất lượng & giá cả nhé!", ["yên tâm", "chất lượng & giá cả"]),
    ( 98.70, 101.21, "Oanh xin gửi lời cảm ơn tới quý anh chị",        ["lời cảm ơn", "quý anh chị"]),
    (101.21, 103.88, "đã tin tưởng đặt hàng của Thực Phẩm F20.",       ["tin tưởng", "Thực Phẩm F20."]),
    (103.95, 106.92, "Nếu anh chị còn có nhu cầu đặt hàng,",           ["nhu cầu đặt hàng,"]),
    (107.00, 109.25, "đặt set quà biếu tặng nhân dịp",                 ["set quà biếu tặng"]),
    (109.25, 112.30, "lễ 20/11 thì hãy inbox ngay cho Oanh nhé!",      ["lễ 20/11", "inbox ngay"]),
]

# Dual-Tier Top Brand Titles (Staggered Tier 1 Gold #FFD400 + Tier 2 White #FFFFFF delayed 0.28s)
TOP_TITLES = [
    # Hook 3-part opening (0.06s -> 4.25s)
    {"t0": 0.06, "t1": 4.22, "tier1": "QUÀ TẶNG TRI ÂN 20/11",          "tier2": "SET QUÀ 4 MÓN TRONG 1 GIỎ MICA",       "hook": True},
    # Intro speaker badge
    {"t0": 4.45, "t1": 9.70, "tier1": "THỰC PHẨM F20 × SKA NEST",       "tier2": "Chị Oanh giới thiệu chi tiết Set Quà 20/11", "hook": False},
    # 4 Items
    {"t0": 10.30, "t1": 15.80, "tier1": "MÓN 01/04 • SET YẾN SÀO",      "tier2": "Tổ yến tinh chế sợi dài tiêu chuẩn",    "hook": False},
    {"t0": 15.90, "t1": 25.30, "tier1": "YẾN SÀO SKA NEST KHÁNH HÒA",   "tier2": "Kèm Táo đỏ • Đông trùng • Kỷ tử • Đường phèn", "hook": False},
    {"t0": 25.45, "t1": 33.55, "tier1": "MÓN 02/04 • 2 HỘP RONG BIỂN",  "tier2": "01 Sấy Giòn Cay Nhẹ • 01 Sấy Mè Không Cay", "hook": False},
    {"t0": 33.75, "t1": 39.70, "tier1": "MÓN 03/04 • BÁNH THUYỀN HẠT",  "tier2": "Gói 250g Mix Hạt Dinh Dưỡng Giòn Bùi",  "hook": False},
    {"t0": 40.05, "t1": 49.85, "tier1": "MÓN 04/04 • RONG BIỂN KẸP HẠT","tier2": "Túi lớn 500g • 22 – 24 thanh dinh dưỡng", "hook": False},
    # Packaging design
    {"t0": 50.00, "t1": 56.75, "tier1": "GIỎ QUÀ MICA TRONG SUỐT",      "tier2": "Khoe trọn vẻ đẹp chỉn chu của 4 món quà", "hook": False},
    {"t0": 56.90, "t1": 61.75, "tier1": "QUAI XÁCH DA ĐỎ ĐÔ",           "tier2": "Chắc tay • Tôn nét sang trọng & lịch sự", "hook": False},
    {"t0": 61.85, "t1": 68.80, "tier1": "HOA ĐIỂM NHẤN & NƠ MÀU BE",    "tier2": "Thiết kế tinh tế, trang nhã dịp tri ân", "hook": False},
    # Core value + Guidebook + Factory + CTA
    {"t0": 68.95, "t1": 76.68, "tier1": "TRÁI TIM GIÁ TRỊ CỦA SET QUÀ", "tier2": "Tổ Yến Tinh Chế Cao Cấp SKA NEST",      "hook": False},
    {"t0": 76.80, "t1": 90.18, "tier1": "TẶNG KÈM CẨM NANG YẾN SÀO",    "tier2": "Xem công dụng & Cách chưng yến đúng chuẩn", "hook": False},
    {"t0": 90.30, "t1": 98.45, "tier1": "F20 TRỰC TIẾP SẢN XUẤT",       "tier2": "Cam kết Chất Lượng & Giá Tận Xưởng",    "hook": False},
    {"t0": 98.65, 105.75: None, "t1": 105.75, "tier1": "TRI ÂN QUÝ KHÁCH HÀNG", "tier2": "Tin chọn Set Quà Thực Phẩm F20", "hook": False},
    {"t0": 105.85, "t1": 112.35, "tier1": "ĐẶT QUÀ 20/11 • INBOX NGAY", "tier2": "Zalo/Hotline: 0706.001.626 - 0979.512.289", "hook": False},
]
for d in TOP_TITLES:
    d.pop(None, None)

data = {"subtitles": SUBTITLES, "top_titles": TOP_TITLES}
json.dump(data, open(os.path.join(OUT, "subtitles_and_titles.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Saved {len(SUBTITLES)} proofread subtitles and {len(TOP_TITLES)} dual-tier titles!")
