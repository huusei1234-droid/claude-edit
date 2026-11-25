import json, math, os, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

V3_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v3_pro")
AROLL_DIR = V3_DIR / "aroll_v3"
BROLL_DIR = V3_DIR / "brolls_v3"
VID_DIR = V3_DIR / "videos_v3"
REF_DIR = V3_DIR / "refs_clean"
FONT_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")

W, H, FPS = 1080, 1920, 30
TOTAL_FRAMES = 4017  # 133.90s @ 30fps

# Load fonts once
F_REG = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 36)
F_HL  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 39)
F_TAG = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 24)
F_TAG_SUB = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-SemiBold.ttf"), 20)
F_BADGE_MAIN = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 27)
F_BADGE_SUB  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 21)
F_HOOK_BIG = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 50)
F_HOOK_SUB = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 28)
F_END_BIG  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 44)
F_END_MED  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 28)
F_END_SM   = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-SemiBold.ttf"), 23)

F20_LOGO = Image.open(REF_DIR / "f20_logo_official.png").convert("RGBA")

# ==============================================================================
# 1. MASTER SHOT LIST (35 Dynamic Centered Cuts across 133.90s = 4017 frames)
# ==============================================================================
SHOTS = [
    # Opening 3-shot panoramic showcase of gift sets (0.00 - 3.90s)
    {"t0": 0.00,  "t1": 1.30,  "src": BROLL_DIR / "intro_01_gimbal_sets.mp4",  "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "magic_reveal"},
    {"t0": 1.30,  "t1": 2.60,  "src": BROLL_DIR / "intro_02_rows_sets.mp4",    "ss": 0.0, "zoom": (1.04, 1.00), "sfx_in": "whoosh_tvc"},
    {"t0": 2.60,  "t1": 3.90,  "src": BROLL_DIR / "intro_03_shelf_sets.mp4",   "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},

    # Live Chi Oanh Opening (3.90 - 13.1333s) with beat-synced zoom keyframes
    {"t0": 3.90,  "t1": 13.1333, "src": AROLL_DIR / "s01_open_live.mp4",       "ss": 0.0, "zoom": "aroll_s01",  "sfx_in": "swoosh_soft"},

    # Nha Trang customers: Anh Hau 77 sets + Phu huynh 13 sets (13.1333 - 22.5667s)
    {"t0": 13.1333, "t1": 16.25, "src": BROLL_DIR / "real_anh_hau_handover.mp4", "ss": 0.2, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},
    {"t0": 16.25,   "t1": 19.55, "src": VID_DIR / "V3_vid15_anh_hau.mp4",        "ss": 0.0, "zoom": (1.00, 1.04), "sfx_in": "shutter"},
    {"t0": 19.55,   "t1": 22.5667, "src": BROLL_DIR / "real_13sets_team.mp4",    "ss": 0.2, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},

    # Ha Noi 10 sets + TP.HCM 4 sets + Tong 104 sets (22.5667 - 33.3667s)
    {"t0": 22.5667, "t1": 25.85, "src": BROLL_DIR / "real_hanoi_carton.mp4",   "ss": 0.2, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},
    {"t0": 25.85,   "t1": 29.15, "src": BROLL_DIR / "real_hcmc_suv.mp4",       "ss": 0.2, "zoom": (1.04, 1.00), "sfx_in": "whoosh_tvc"},
    {"t0": 29.15,   "t1": 33.3667, "src": BROLL_DIR / "pov_gimbal_104_sets.mp4", "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "riser_open"},

    # Fix Image 3: Continuous long panoramic POV shot showing massive quantity of 104 sets (33.3667 - 39.30s)
    {"t0": 33.3667, "t1": 39.30, "src": BROLL_DIR / "pov_long_104_sets.mp4",   "ss": 0.2, "zoom": (1.00, 1.04), "sfx_in": "magic_reveal"},

    # Live Chi Oanh Intro to 1 Set Qua (39.30 - 44.1667s)
    {"t0": 39.30,   "t1": 44.1667, "src": AROLL_DIR / "s05_intro_live.mp4",    "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "swoosh_soft"},

    # Fix Image 4, 5, 6: Dynamic Multi-Shot Cuts for Set Qua + SKA NEST + To Yen + 4 Ingredients! (44.1667 - 58.1333s)
    {"t0": 44.1667, "t1": 46.30, "src": VID_DIR / "V3_vid01_set_qua_hero.mp4", "ss": 0.0, "zoom": (1.00, 1.04), "sfx_in": "magic_reveal"},
    {"t0": 46.30,   "t1": 49.55, "src": VID_DIR / "V3_vid02_skanest_box.mp4",  "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},
    {"t0": 49.55,   "t1": 53.95, "src": VID_DIR / "V3_vid03_to_yen_pure.mp4",  "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "shine_accent"},
    {"t0": 53.95,   "t1": 56.15, "src": VID_DIR / "V3_vid04_tao_do_dtht.mp4",  "ss": 0.0, "zoom": (1.00, 1.04), "sfx_in": "bubble_in"},
    {"t0": 56.15,   "t1": 58.1333, "src": VID_DIR / "V3_vid05_ky_tu_duong_phen.mp4", "ss": 0.0, "zoom": (1.00, 1.04), "sfx_in": "bubble_in"},

    # Fix Image 7 & 8: Centered Dual Moving Jars -> Centered Single Jar Say Gion -> Centered Single Jar Say Me! (58.1333 - 66.60s)
    {"t0": 58.1333, "t1": 61.15, "src": "DUAL_SEAWEED_JARS",                   "ss": 0.0, "zoom": (1.00, 1.00), "sfx_in": "whoosh_pip"},
    {"t0": 61.15,   "t1": 63.80, "src": VID_DIR / "V3_vid06_hu_say_gion.mp4",  "ss": 0.3, "zoom": (1.00, 1.05), "sfx_in": "pop_tvc"},
    {"t0": 63.80,   "t1": 66.60, "src": VID_DIR / "V3_vid07_hu_say_me.mp4",    "ss": 0.3, "zoom": (1.00, 1.05), "sfx_in": "pop_tvc"},

    # Fix Image 9: Centered AI Video of Banh Thuyen Mix Hat 250g (66.60 - 72.00s)
    {"t0": 66.60,   "t1": 72.00, "src": VID_DIR / "V3_vid08_banh_thuyen.mp4",  "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},

    # Fix Image 10: Centered AI Video of Rong Bien Kep Hat 500g -> Artisan 22-24 Bars Close-up! (72.00 - 80.30s)
    {"t0": 72.00,   "t1": 75.75, "src": VID_DIR / "V3_vid09_kep_hat.mp4",      "ss": 0.0, "zoom": (1.00, 1.04), "sfx_in": "whoosh_tvc"},
    {"t0": 75.75,   "t1": 80.30, "src": VID_DIR / "V3_vid12_kep_hat_bars.mp4", "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "pop_tvc"},

    # Fix Image 11: Framed Luxury Bird's Nest Showcase -> Chi Oanh Holding Cam Nang -> Steaming Stew Pot & Booklet! (80.30 - 92.2333s)
    {"t0": 80.30,   "t1": 85.05, "src": "FRAMED_YEN_HERO",                     "ss": 0.0, "zoom": (1.00, 1.00), "sfx_in": "shine_accent"},
    {"t0": 85.05,   "t1": 88.70, "src": BROLL_DIR / "cam_nang_hold_clean.mp4", "ss": 1.0, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},
    {"t0": 88.70,   "t1": 92.2333, "src": VID_DIR / "V3_vid10_chung_yen.mp4",  "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "magic_reveal"},

    # Transparent Mica Basket + Fix Image 12: Live Chi Oanh on Handle + Real Floral & Beige Bow Macro Zoom! (92.2333 - 108.70s)
    {"t0": 92.2333, "t1": 97.6333, "src": VID_DIR / "V3_vid13_gio_mica_real.mp4", "ss": 0.0, "zoom": (1.00, 1.04), "sfx_in": "whoosh_tvc"},
    {"t0": 97.6333, "t1": 102.8667, "src": AROLL_DIR / "s13_quai_live.mp4",       "ss": 0.0, "zoom": (1.00, 1.04), "sfx_in": "swoosh_soft", "pip": "HANDLE_ZOOM_PIP"},
    {"t0": 102.8667,"t1": 105.75,   "src": VID_DIR / "V3_vid13_gio_mica_real.mp4","ss": 1.2, "zoom": (1.08, 1.15), "sfx_in": "pop_tvc"},
    {"t0": 105.75,  "t1": 108.70,   "src": VID_DIR / "V3_vid14_quai_no_macro.mp4","ss": 0.0, "zoom": (1.00, 1.07), "sfx_in": "shine_accent"},

    # Direct F20 Manufacturing Live + Packing B-Roll (108.70 - 117.7333s)
    {"t0": 108.70,  "t1": 113.75, "src": AROLL_DIR / "s15_sx_live.mp4",        "ss": 0.0, "zoom": (1.00, 1.05), "sfx_in": "swoosh_soft"},
    {"t0": 113.75,  "t1": 115.80, "src": BROLL_DIR / "real_factory_pack1.mp4", "ss": 0.3, "zoom": (1.00, 1.05), "sfx_in": "whoosh_tvc"},
    {"t0": 115.80,  "t1": 117.7333, "src": BROLL_DIR / "real_factory_pack2.mp4","ss": 0.3, "zoom": (1.04, 1.00), "sfx_in": "whoosh_tvc"},

    # Live Chi Oanh Thank-You & 20/11 CTA + Official F20 Brand End-Card (117.7333 - 133.90s)
    {"t0": 117.7333,"t1": 130.60, "src": AROLL_DIR / "s16_cta_live.mp4",       "ss": 0.0, "zoom": "aroll_s16",  "sfx_in": "swoosh_soft", "pip": "CTA_GIFT_PIP"},
    {"t0": 130.60,  "t1": 133.90, "src": "OFFICIAL_F20_ENDCARD",               "ss": 0.0, "zoom": (1.00, 1.00), "sfx_in": "magic_reveal"},
]

# ==============================================================================
# 2. MINIMAL F20 EMERALD-GLASS SECTION HEADERS (Replaces ugly brown Image 2 pill!)
#    Strict TikTok Top Safe Zone: cy = 186, x within 110..910
# ==============================================================================
TOP_TAGS = [
    (3.95,  12.90, "TRI ÂN NGÀY NHÀ GIÁO 20/11", "Chuẩn Bị 104 Set Quà Sáng Nay"),
    (13.20, 22.40, "KHÁCH ĐẶT TẠI NHA TRANG",   "Đăng Khoa Edu (77 Set) • Phụ Huynh (13 Set)"),
    (22.65, 33.20, "GIAO ĐI HÀ NỘI & TP.HCM",   "Hà Nội (10 Set) • TP.HCM (04 Set)"),
    (33.45, 39.10, "TOÀN CẢNH 104 SET QUÀ F20", "Hoàn Thiện Chỉn Chu • Đúng Hẹn"),
    (44.25, 58.00, "MÓN 01/04 • YẾN SÀO SKA NEST", "Tổ Yến Sợi Dài & 04 Nguyên Liệu Chưng"),
    (58.20, 66.45, "MÓN 02/04 • 02 HỘP RONG BIỂN F20", "01 Sấy Giòn Cay Nhẹ • 01 Sấy Mè Không Cay"),
    (66.70, 71.85, "MÓN 03/04 • BÁNH THUYỀN MIX HẠT", "Gói 250g • Giòn Rụm Giàu Dưỡng Chất"),
    (72.10, 80.15, "MÓN 04/04 • RONG BIỂN KẸP HẠT", "Gói Lớn 500g • 22 – 24 Thanh Hạt"),
    (80.40, 92.05, "TẶNG KÈM CẨM NANG YẾN SÀO", "Công Dụng & Hướng Dẫn Chưng Đúng Cách"),
    (92.35, 108.50,"GIỎ QUÀ MICA SANG TRỌNG",   "Quai Da Đỏ Đô • Hoa Điểm Nhấn & Nơ Màu Be"),
    (108.85,117.55,"THỰC PHẨM F20 TRỰC TIẾP SẢN XUẤT", "An Tâm Chất Lượng • Giá Tận Xưởng"),
]

# ==============================================================================
# 3. INTEGRATED PRODUCT PEDESTAL BADGES (Fixes Image 8 disconnected floating label!)
#    Anchored directly at the lower pedestal of centered products (cx=508, cy=1255)
# ==============================================================================
PRODUCT_BADGES = [
    (46.40, 49.45, "SET YẾN SÀO CAO CẤP SKA NEST", "Nha Trang – Khánh Hòa"),
    (49.65, 53.85, "01 TỔ YẾN SÀO TINH CHẾ",       "Dòng Tiêu Chuẩn • Nguyên Tổ Sợi Dài"),
    (54.00, 56.08, "TÁO ĐỎ & ĐÔNG TRÙNG HẠ THẢO",  "Nguyên Liệu Chưng Đi Kèm"),
    (56.20, 58.05, "KỶ TỬ & 01 HỘP ĐƯỜNG PHÈN",   "Trọn Vị Thanh Ngọt Bổ Dưỡng"),
    (61.22, 63.72, "01 HỘP RONG BIỂN SẤY GIÒN",   "Tuệ Tâm F20 • Vị Cay Nhẹ Thơm Ngon"),
    (63.88, 66.50, "01 HỘP RONG BIỂN SẤY MÈ",     "Tuệ Tâm F20 • Vị Không Cay Dễ Ăn"),
    (66.75, 71.88, "BÁNH THUYỀN MIX HẠT • 250G",  "Hạnh Nhân • Hạt Điều • Bí Xanh • Mật Ong"),
    (72.12, 75.65, "RONG BIỂN KẸP HẠT • GÓI 500G","Thực Phẩm F20 • Nhẹ Calo Giàu Dưỡng Chất"),
    (75.85, 80.18, "GỒM 22 – 24 THANH HẠT",        "Giòn Rụm • Đóng Gói Từng Thanh Tiện Lợi"),
    (88.80, 92.10, "CHƯNG YẾN ĐÚNG CÁCH",         "Giữ Trọn Vi Chất & Sợi Yến Dai Ngon"),
]

# ==============================================================================
# 4. UNIFIED NATURAL-SPACING SUBTITLES ("Text Sub" inside TikTok Safe Zone!)
#    Each card: (t0, t1, [ [ (chunk, style), ... ], [ (chunk, style), ... ] ])
#    style: "reg" (White), "gold" (2-layer Gold Sheen), "green" (F20 Mint-Lime)
# ==============================================================================
SUBTITLES = [
    (3.92,  7.15,  [[("Hôm nay bên Oanh chuẩn bị", "reg")],
                    [("104 SET QUÀ", "gold"), ("cho khách đặt", "reg")]]),
    (7.20,  10.75, [[("làm", "reg"), ("quà biếu tặng", "gold"), ("thầy cô giáo", "reg")]]),
    (10.80, 13.08, [[("nhân dịp tri ân ngày", "reg"), ("20 THÁNG 11", "gold")]]),

    (13.18, 15.05, [[("Ở", "reg"), ("Nha Trang", "green"), ("có 02 khách hàng:", "reg")]]),
    (15.10, 19.35, [[("1 là", "reg"), ("ANH HẬU", "gold"), ("tại Trung tâm", "reg")],
                    [("Luyện thi", "reg"), ("ĐĂNG KHOA EDU", "gold"), ("đặt", "reg"), ("77 SET", "green")]]),
    (19.50, 22.48, [[("2 là nhóm", "reg"), ("HỘI PHỤ HUYNH", "gold")],
                    [("đặt", "reg"), ("13 SET QUÀ", "green")]]),

    (22.58, 25.78, [[("Khách thứ 3 là giáo viên ở", "reg"), ("HÀ NỘI", "gold")],
                    [("đặt", "reg"), ("10 SET QUÀ", "green")]]),
    (25.85, 29.05, [[("và một bạn ở", "reg"), ("TP. HỒ CHÍ MINH", "gold")],
                    [("đặt", "reg"), ("04 SET QUÀ", "green")]]),
    (29.18, 33.25, [[("Tổng sáng nay bên Oanh chuẩn bị đủ", "reg")],
                    [("104 SET QUÀ", "gold"), ("nha mọi người!", "reg")]]),

    (33.40, 39.15, [[("Đây là toàn bộ", "reg"), ("SET QUÀ", "gold"), ("bên Oanh", "reg")],
                    [("đã", "reg"), ("hoàn thiện chỉn chu", "green"), ("sáng nay ạ!", "reg")]]),

    (39.38, 44.08, [[("Bây giờ Oanh sẽ giới thiệu", "reg"), ("01 SET QUÀ", "gold")],
                    [("của bên Oanh cho mọi người xem nhé!", "reg")]]),

    (44.18, 46.22, [[("Một", "reg"), ("set quà tặng sang trọng", "gold"), ("như thế này", "reg")]]),
    (46.28, 49.48, [[("đầu tiên gồm", "reg"), ("01 SET YẾN SÀO CAO CẤP", "gold")]]),
    (49.55, 52.35, [[("có", "reg"), ("01 TỔ YẾN SÀO TINH CHẾ", "gold")],
                    [("sợi dài • dòng", "reg"), ("TIÊU CHUẨN", "green")]]),

    (52.45, 56.08, [[("Kèm nguyên liệu chưng:", "reg"), ("TÁO ĐỎ", "gold")],
                    [("và", "reg"), ("ĐÔNG TRÙNG HẠ THẢO", "gold")]]),
    (56.14, 58.08, [[("cùng", "reg"), ("KỶ TỬ", "gold"), ("và", "reg"), ("01 HỘP ĐƯỜNG PHÈN", "green")]]),

    (58.18, 61.10, [[("Thứ 2 là", "reg"), ("02 HỘP RONG BIỂN", "gold")],
                    [("sấy giòn", "reg"), ("TUỆ TÂM F20", "green")]]),
    (61.18, 63.74, [[("01 hộp", "reg"), ("RONG BIỂN SẤY GIÒN", "gold")],
                    [("vị cay nhẹ", "green"), ("thơm ngon", "reg")]]),
    (63.82, 66.52, [[("và 01 hộp", "reg"), ("RONG BIỂN SẤY MÈ", "gold")],
                    [("vị không cay", "green"), ("rất dễ ăn!", "reg")]]),

    (66.65, 69.85, [[("Thứ 3 là 01 gói", "reg"), ("BÁNH THUYỀN MIX HẠT", "gold")]]),
    (69.90, 71.92, [[("dinh dưỡng", "reg"), ("250G", "gold"), ("•", "reg"), ("giòn rụm bổ dưỡng", "green")]]),

    (72.06, 75.65, [[("Thứ 4 là gói lớn", "reg"), ("RONG BIỂN KẸP HẠT", "gold")],
                    [("trọng lượng", "reg"), ("500G", "green")]]),
    (75.75, 80.18, [[("bên trong gồm từ", "reg"), ("22 ĐẾN 24 THANH", "gold")],
                    [("bánh hạt dinh dưỡng", "green"), ("nha mọi người!", "reg")]]),

    (80.32, 85.00, [[("Giá trị nhất là", "reg"), ("TỔ YẾN TINH CHẾ", "gold")],
                    [("dòng tiêu chuẩn", "reg"), ("SỢI DÀI", "green")]]),
    (85.08, 88.65, [[("được kèm theo", "reg"), ("01 TỜ CẨM NANG", "gold")],
                    [("nêu rõ", "reg"), ("công dụng của yến sào", "green")]]),
    (88.72, 92.15, [[("và hướng dẫn", "reg"), ("CHƯNG YẾN ĐÚNG CÁCH", "gold")],
                    [("cho mọi người nhé!", "reg")]]),

    (92.26, 97.52, [[("Tất cả xếp khéo léo trong", "reg"), ("GIỎ QUÀ MICA", "gold")],
                    [("trong suốt", "green"), ("rất đẹp mắt!", "reg")]]),

    (97.68, 102.78,[[("Bên trên có", "reg"), ("QUAI XÁCH BẰNG DA", "gold")],
                    [("màu đỏ đô", "gold"), ("rất là sang trọng!", "reg")]]),
    (102.88,105.70,[[("Thiết kế thêm vài", "reg"), ("BÔNG HOA ĐIỂM NHẤN", "gold")]]),
    (105.76,108.60,[[("và một", "reg"), ("CHIẾC NƠ MÀU BE", "gold")],
                    [("rất xinh xắn như thế này!", "reg")]]),

    (108.85,113.70,[[("Đặc biệt sản phẩm đều do", "reg"), ("BÊN OANH", "green")],
                    [("TRỰC TIẾP SẢN XUẤT", "gold")]]),
    (113.80,117.65,[[("nên mọi người yên tâm về", "reg")],
                    [("CHẤT LƯỢNG", "green"), ("và", "reg"), ("GIÁ CẢ", "gold"), ("nhé!", "reg")]]),

    (117.80,123.05,[[("Cảm ơn quý anh chị đã tin tưởng", "reg")],
                    [("lựa chọn", "reg"), ("THỰC PHẨM F20", "green")]]),
    (123.18,127.85,[[("Anh chị có nhu cầu đặt", "reg"), ("SET QUÀ TẶNG", "gold")]]),
    (127.90,130.55,[[("dịp lễ", "reg"), ("20 THÁNG 11", "gold"), ("hãy", "reg"), ("INBOX NGAY", "green"), ("nhé!", "reg")]]),
]


# ==============================================================================
# 5. FRAME CACHE & VIDEO DECODER HELPERS
# ==============================================================================
class ClipReader:
    def __init__(self, mp4_path):
        self.path = str(mp4_path)
        res = subprocess.run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,nb_frames,duration",
            "-of", "json", self.path
        ], capture_output=True, text=True, check=True)
        st = json.loads(res.stdout)["streams"][0]
        self.dur = float(st.get("duration") or 5.0)
        self.frames = None

    def load_all(self):
        if self.frames is not None:
            return
        proc = subprocess.Popen([
            "ffmpeg", "-v", "error", "-i", self.path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,fps=30",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ], stdout=subprocess.PIPE)
        raw = proc.stdout.read()
        proc.wait()
        n = len(raw) // (W * H * 3)
        arr = np.frombuffer(raw[:n * W * H * 3], dtype=np.uint8).reshape((n, H, W, 3))
        self.frames = arr

    def get_frame(self, local_t):
        self.load_all()
        n = len(self.frames)
        if n == 0:
            return Image.new("RGB", (W, H), (14, 48, 22))
        # Smooth ping-pong loop if clip is shorter than segment!
        idx_raw = int(round(local_t * FPS))
        cycle = 2 * n - 2 if n > 2 else n
        pos = idx_raw % max(1, cycle)
        idx = pos if pos < n else cycle - pos
        idx = max(0, min(n - 1, idx))
        return Image.fromarray(self.frames[idx])


READERS = {}
def get_reader(p):
    k = str(p)
    if k not in READERS:
        READERS[k] = ClipReader(p)
    return READERS[k]


def apply_symmetric_zoom(im, z):
    if abs(z - 1.0) < 0.0015:
        return im
    cw = int(round(W / z))
    ch = int(round(H / z))
    x0 = (W - cw) // 2
    y0 = (H - ch) // 2
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.Resampling.BILINEAR)


# ==============================================================================
# 6. TYPOGRAPHY & OVERLAY CACHES (2-Layer Gradient + Natural Word Spacing)
# ==============================================================================
GRAD_CACHE = {}
def render_gradient_word(text, style):
    key = (text, style)
    if key in GRAD_CACHE:
        return GRAD_CACHE[key]
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dummy.textbbox((0, 0), text, font=F_HL, stroke_width=3)
    pad = 6
    tw = (bb[2] - bb[0]) + pad * 2
    th = (bb[3] - bb[1]) + pad * 2
    ox = -bb[0] + pad
    oy = -bb[1] + pad

    # Layer 1: Soft drop shadow + crisp thin 2.5px dark forest stroke (NEVER thick 8px!)
    base = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sh = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((ox + 1, oy + 3), text, font=F_HL, fill=(0, 0, 0, 155), stroke_width=3, stroke_fill=(0, 0, 0, 155))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2)))
    ImageDraw.Draw(base).text((ox, oy), text, font=F_HL, fill=(12, 34, 18, 255), stroke_width=3, stroke_fill=(10, 28, 15, 246))

    # Layer 2: Pure un-eaten Gradient Fill on top!
    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).text((ox, oy), text, font=F_HL, fill=255)

    grad = np.zeros((th, tw, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, th)[:, None]
    if style == "gold":
        # 3-stop Champagne -> Gold -> Warm Amber
        c_top = np.array([255, 249, 196])
        c_mid = np.array([255, 214, 58])
        c_bot = np.array([245, 162, 18])
    else:
        # F20 Brand Mint-Gold -> Fresh Leaf Green
        c_top = np.array([238, 255, 188])
        c_mid = np.array([142, 236, 62])
        c_bot = np.array([58, 188, 68])

    rgb = np.where(
        ys < 0.52,
        c_top + (c_mid - c_top) * (ys / 0.52),
        c_mid + (c_bot - c_mid) * ((ys - 0.52) / 0.48),
    )
    grad[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)[:, None, :]
    grad[:, :, 3] = np.array(mask)
    base.alpha_composite(Image.fromarray(grad, "RGBA"))

    adv_w = F_HL.getlength(text)
    GRAD_CACHE[key] = (base, ox, oy, adv_w)
    return GRAD_CACHE[key]


REG_CACHE = {}
def render_reg_word(text):
    if text in REG_CACHE:
        return REG_CACHE[text]
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dummy.textbbox((0, 0), text, font=F_REG, stroke_width=2)
    pad = 5
    tw = (bb[2] - bb[0]) + pad * 2
    th = (bb[3] - bb[1]) + pad * 2
    ox = -bb[0] + pad
    oy = -bb[1] + pad

    base = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sh = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((ox + 1, oy + 2), text, font=F_REG, fill=(0, 0, 0, 145), stroke_width=2, stroke_fill=(0, 0, 0, 145))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.8)))
    ImageDraw.Draw(base).text((ox, oy), text, font=F_REG, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(10, 28, 16, 238))
    adv_w = F_REG.getlength(text)
    REG_CACHE[text] = (base, ox, oy, adv_w)
    return REG_CACHE[text]


SUB_CARD_CACHE = {}
def build_subtitle_card(sub_idx, lines, hl_pop=1.0):
    # Quantize hl_pop to 2 decimals for speed
    qpop = round(hl_pop, 2)
    ckey = (sub_idx, qpop)
    if ckey in SUB_CARD_CACHE:
        return SUB_CARD_CACHE[ckey]

    space_w = F_REG.getlength(" ")  # ~10px natural single space!
    line_layouts = []
    max_line_w = 0.0

    for line in lines:
        items = []
        cur_x = 0.0
        for idx_c, (chunk_txt, st) in enumerate(line):
            if idx_c > 0:
                cur_x += space_w
            if st == "reg":
                im_w, ox, oy, adv = render_reg_word(chunk_txt)
                items.append((cur_x, im_w, ox, oy, adv, False))
                cur_x += adv
            else:
                im_w, ox, oy, adv = render_gradient_word(chunk_txt, st)
                items.append((cur_x, im_w, ox, oy, adv, True))
                cur_x += adv
        line_layouts.append((cur_x, items))
        max_line_w = max(max_line_w, cur_x)

    line_h = 54
    total_h = len(lines) * line_h
    card_w = int(math.ceil(max_line_w)) + 64
    card_h = total_h + 34

    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    # Sleek subtle frosted dark-emerald glass backing for 100% contrast on bright gift bags without heavy strokes!
    cd.rounded_rectangle([4, 4, card_w - 5, card_h - 5], radius=22, fill=(8, 26, 15, 148), outline=(142, 232, 74, 82), width=1)

    for li, (lw, items) in enumerate(line_layouts):
        start_x = (card_w - lw) / 2.0
        baseline_y = 20 + li * line_h
        for rel_x, im_w, ox, oy, adv, is_hl in items:
            draw_im = im_w
            dx = int(round(start_x + rel_x - ox))
            dy = int(round(baseline_y - oy + (0 if is_hl else 2)))
            if is_hl and abs(qpop - 1.0) > 0.005:
                sw = max(1, int(round(im_w.width * qpop)))
                sh = max(1, int(round(im_w.height * qpop)))
                draw_im = im_w.resize((sw, sh), Image.Resampling.BICUBIC)
                dx -= (sw - im_w.width) // 2
                dy -= (sh - im_w.height) // 2
            card.alpha_composite(draw_im, (max(0, dx), max(0, dy)))

    # Strict TikTok Safe-Zone Width Cap: max_w = 770px so centered at cx=506 -> x=121..891 (100% clear of right TikTok icons x>=935!)
    if card.width > 770:
        sc = 770.0 / card.width
        card = card.resize((770, int(round(card.height * sc))), Image.Resampling.LANCZOS)

    SUB_CARD_CACHE[ckey] = card
    return card


TAG_CACHE = {}
def get_top_tag_card(title, sub):
    key = (title, sub)
    if key in TAG_CACHE:
        return TAG_CACHE[key]
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    b1 = d0.textbbox((0, 0), title, font=F_TAG)
    b2 = d0.textbbox((0, 0), sub, font=F_TAG_SUB)
    w1, w2 = b1[2] - b1[0], b2[2] - b2[0]
    cw = min(760, max(w1 + 92, w2 + 72))
    ch = 84

    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    # Soft ambient shadow
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([6, 8, cw - 6, ch - 4], radius=24, fill=(0, 0, 0, 115))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4.0)))

    cd = ImageDraw.Draw(card)
    # Minimal F20 Emerald-Glass editorial tag (NO thick borders, NO cartoonish outlines!)
    cd.rounded_rectangle([4, 4, cw - 5, ch - 8], radius=24, fill=(10, 56, 26, 208), outline=(146, 232, 78, 175), width=2)
    # Official mini circular F20 logo badge on left
    logo_sm = F20_LOGO.resize((48, 48), Image.Resampling.LANCZOS)
    card.alpha_composite(logo_sm, (18, 16))

    tx_center = 68 + (cw - 82) // 2
    cd.text((tx_center - w1 // 2, 13), title, font=F_TAG, fill=(255, 226, 102, 255))
    cd.text((tx_center - w2 // 2, 45), sub, font=F_TAG_SUB, fill=(236, 252, 238, 245))
    TAG_CACHE[key] = card
    return card


BADGE_CACHE = {}
def get_pedestal_badge(title, sub):
    key = (title, sub)
    if key in BADGE_CACHE:
        return BADGE_CACHE[key]
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    b1 = d0.textbbox((0, 0), title, font=F_BADGE_MAIN)
    b2 = d0.textbbox((0, 0), sub, font=F_BADGE_SUB)
    w1, w2 = b1[2] - b1[0], b2[2] - b2[0]
    cw = min(730, max(w1, w2) + 64)
    ch = 82

    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([6, 8, cw - 6, ch - 4], radius=20, fill=(0, 0, 0, 125))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3.5)))

    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([4, 4, cw - 5, ch - 7], radius=20, fill=(12, 64, 28, 224), outline=(255, 216, 92, 210), width=2)
    # Subtle gold accent bar on top center
    cd.rounded_rectangle([cw // 2 - 42, 4, cw // 2 + 42, 8], radius=2, fill=(255, 218, 96, 255))
    cd.text(((cw - w1) // 2, 13), title, font=F_BADGE_MAIN, fill=(255, 232, 118, 255))
    cd.text(((cw - w2) // 2, 46), sub, font=F_BADGE_SUB, fill=(242, 255, 242, 250))
    BADGE_CACHE[key] = card
    return card


def make_rounded_pip(frame_rgb, pw, ph, radius=30, border_rgb=(255, 220, 108)):
    im = frame_rgb.resize((pw, ph), Image.Resampling.BICUBIC).convert("RGBA")
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=radius, fill=255)
    out = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
    sh = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([12, 15, 12 + pw, 15 + ph], radius=radius, fill=(0, 0, 0, 145))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5.0)))
    clipped = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    clipped.paste(im, (0, 0), mask)
    out.alpha_composite(clipped, (12, 10))
    ImageDraw.Draw(out).rounded_rectangle([12, 10, 12 + pw - 1, 10 + ph - 1], radius=radius, outline=border_rgb + (240,), width=3)
    return out


# ==============================================================================
# 7. SPECIAL COMPOSITE SCENES (Dual Moving Jars, Framed Yen Showcase, Opening Hook, End-Card)
# ==============================================================================
def render_dual_seaweed_jars(t, shot_t0):
    dt = t - shot_t0
    f_gion = get_reader(VID_DIR / "V3_vid06_hu_say_gion.mp4").get_frame(dt)
    f_me   = get_reader(VID_DIR / "V3_vid07_hu_say_me.mp4").get_frame(dt)

    # Soft blurred emerald-warm studio backdrop from f_gion
    bg = f_gion.resize((270, 480), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.Resampling.BILINEAR)
    bg_rgba = bg.convert("RGBA")
    tint = Image.new("RGBA", (W, H), (8, 38, 18, 118))
    bg_rgba.alpha_composite(tint)

    # Symmetric Twin Moving Cards centered around x = 540! (Left cx=292, Right cx=788; each 436x730 -> total span x=74..1006, symmetrically centered at 540!)
    cw, ch = 432, 720
    # Crop central jar area from each 1080x1920 video so each jar fills its card crisply & dead-center!
    c_gion = f_gion.crop((190, 420, 890, 1585))
    c_me   = f_me.crop((190, 420, 890, 1585))

    card_l = make_rounded_pip(c_gion, cw, ch, radius=32, border_rgb=(146, 232, 78))
    card_r = make_rounded_pip(c_me,   cw, ch, radius=32, border_rgb=(255, 220, 102))

    # Smooth staggered spring slide-in (0.00s and 0.16s)
    u_l = min(1.0, max(0.0, dt / 0.28))
    u_r = min(1.0, max(0.0, (dt - 0.14) / 0.28))
    ease_l = 1.0 - (1.0 - u_l) ** 3
    ease_r = 1.0 - (1.0 - u_r) ** 3

    yl = int(round(470 + (1.0 - ease_l) * 70))
    yr = int(round(470 + (1.0 - ease_r) * 70))
    bg_rgba.alpha_composite(card_l, (292 - card_l.width // 2, yl))
    if dt >= 0.08:
        bg_rgba.alpha_composite(card_r, (788 - card_r.width // 2, yr))

    # Neat mini labels anchored directly to the bottom edge of each card!
    d = ImageDraw.Draw(bg_rgba)
    for cx_b, yy_b, lbl in [(292, yl + ch - 26, "SẤY GIÒN • CAY NHẸ"), (788, yr + ch - 26, "SẤY MÈ • KHÔNG CAY")]:
        if cx_b == 788 and dt < 0.14:
            continue
        bb = d.textbbox((0, 0), lbl, font=F_BADGE_SUB)
        bw = bb[2] - bb[0] + 36
        d.rounded_rectangle([cx_b - bw // 2, yy_b, cx_b + bw // 2, yy_b + 42], radius=14, fill=(10, 58, 26, 238), outline=(255, 220, 102, 220), width=2)
        d.text((cx_b - (bb[2] - bb[0]) // 2, yy_b + 8), lbl, font=F_BADGE_SUB, fill=(255, 244, 172, 255))

    return bg_rgba.convert("RGB")


def render_framed_yen_hero(t, shot_t0):
    dt = t - shot_t0
    f_yen = get_reader(VID_DIR / "V3_vid03_to_yen_pure.mp4").get_frame(dt + 0.8)
    f_box = get_reader(VID_DIR / "V3_vid02_skanest_box.mp4").get_frame(dt + 0.5)

    bg = f_box.resize((270, 480), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(16)).resize((W, H), Image.Resampling.BILINEAR).convert("RGBA")
    bg.alpha_composite(Image.new("RGBA", (W, H), (28, 18, 6, 98)))

    # Main luxury rounded frame centered at x=540 showing zoomed pure white long-strand bird's nest!
    z = 1.12 + 0.05 * min(1.0, dt / 4.7)
    yen_zoom = apply_symmetric_zoom(f_yen, z).crop((80, 380, 1000, 1520))
    main_card = make_rounded_pip(yen_zoom, 780, 860, radius=38, border_rgb=(255, 220, 108))
    bg.alpha_composite(main_card, (540 - main_card.width // 2, 340))

    # Sleek floating circular/rounded SKA NEST seal inset at top-right of the card (inside safe zone x<=905!)
    box_crop = f_box.crop((160, 420, 920, 1420))
    mini = make_rounded_pip(box_crop, 250, 290, radius=26, border_rgb=(255, 232, 138))
    u = min(1.0, max(0.0, (dt - 0.20) / 0.30))
    ease = 1.0 - (1.0 - u) ** 3
    if u > 0.02:
        bg.alpha_composite(mini, (635, int(round(295 + (1.0 - ease) * 40))))

    return bg.convert("RGB")


def render_official_endcard(t, shot_t0):
    dt = t - shot_t0
    f_hero = get_reader(VID_DIR / "V3_vid01_set_qua_hero.mp4").get_frame(dt)
    bg = f_hero.resize((270, 480), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(18)).resize((W, H), Image.Resampling.BILINEAR).convert("RGBA")
    # Deep F20 Forest-Emerald luxury gradient overlay
    grad = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    grad[:, :, 0] = (8 + 6 * ys).astype(np.uint8)
    grad[:, :, 1] = (54 - 16 * ys).astype(np.uint8)
    grad[:, :, 2] = (24 - 8 * ys).astype(np.uint8)
    grad[:, :, 3] = 205
    bg.alpha_composite(Image.fromarray(grad, "RGBA"))

    u = min(1.0, dt / 0.40)
    ease = 1.0 - (1.0 - u) ** 3

    # Official F20 Circular Logo at top-center inside TikTok safe zone (cx=508, y=190)
    logo_sz = 164
    lg = F20_LOGO.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
    bg.alpha_composite(lg, (508 - logo_sz // 2, int(round(190 + (1.0 - ease) * 30))))

    # Centered framed moving Hero Gift Basket in the middle (cx=508, y=385..1015)
    hero_crop = f_hero.crop((140, 320, 940, 1480))
    hcard = make_rounded_pip(hero_crop, 480, 620, radius=34, border_rgb=(255, 220, 102))
    bg.alpha_composite(hcard, (508 - hcard.width // 2, int(round(385 + (1.0 - ease) * 35))))

    # Crisp Brand Typography & Official F20 Contact Info inside TikTok Safe Zone (y=1050..1440, x=116..900)!
    d = ImageDraw.Draw(bg)
    t1 = "THỰC PHẨM F20 × SKA NEST"
    b1 = d.textbbox((0, 0), t1, font=F_END_BIG)
    d.text((508 - (b1[2] - b1[0]) // 2, 1055), t1, font=F_END_BIG, fill=(255, 228, 104, 255), stroke_width=2, stroke_fill=(8, 28, 14, 240))

    t2 = "SET QUÀ TẶNG TRI ÂN 20/11 SANG TRỌNG"
    b2 = d.textbbox((0, 0), t2, font=F_END_MED)
    d.text((508 - (b2[2] - b2[0]) // 2, 1118), t2, font=F_END_MED, fill=(255, 255, 255, 250))

    # Official Contact Card (Hotline + Website + Nha Trang Address — strictly within x=116..900!)
    d.rounded_rectangle([116, 1185, 900, 1385], radius=24, fill=(12, 72, 32, 228), outline=(146, 232, 78, 210), width=2)
    lines_c = [
        ("Hotline / Zalo: 0979 512 289 • 0706 001 626", (255, 232, 114, 255), F_END_MED, 1204),
        ("Website: thucphamf20.com", (232, 255, 228, 255), F_END_SM, 1258),
        ("Đ/c: 17/3 Điện Biên Phủ, P. Vĩnh Hoà, TP. Nha Trang", (228, 245, 230, 245), F_END_SM, 1304),
    ]
    for txt_c, col_c, fnt_c, yy_c in lines_c:
        bc = d.textbbox((0, 0), txt_c, font=fnt_c)
        d.text((508 - (bc[2] - bc[0]) // 2, yy_c), txt_c, font=fnt_c, fill=col_c)

    return bg.convert("RGB")


# ==============================================================================
# 8. FRAME COMPOSITOR (Rhythm Zoom + Smooth PIPs + TikTok Safe Typography)
# ==============================================================================
def compute_shot_zoom(shot, t):
    zspec = shot["zoom"]
    dt = t - shot["t0"]
    dur = max(0.05, shot["t1"] - shot["t0"])
    u = min(1.0, max(0.0, dt / dur))
    smooth_u = u * u * (3.0 - 2.0 * u)

    if isinstance(zspec, tuple):
        return zspec[0] + (zspec[1] - zspec[0]) * smooth_u

    if zspec == "aroll_s01":
        # Keyframe zoom-in on "104 set quà" (5.5s..7.2s) -> zoom-out -> zoom-in on "20 tháng 11" (11.6s..13.1s)!
        if t < 5.40:
            return 1.00 + 0.03 * ((t - 3.90) / 1.50)
        elif t < 7.20:
            p = min(1.0, (t - 5.40) / 0.35)
            return 1.03 + 0.055 * (p * p * (3 - 2 * p))
        elif t < 11.40:
            p = min(1.0, (t - 7.20) / 1.20)
            return 1.085 - 0.065 * (p * p * (3 - 2 * p))
        else:
            p = min(1.0, (t - 11.40) / 0.45)
            return 1.02 + 0.06 * (p * p * (3 - 2 * p))

    if zspec == "aroll_s16":
        # Smooth rhythm zoom on "THỰC PHẨM F20" (121.8s) and "INBOX NGAY" (128.5s)
        if t < 121.5:
            return 1.00 + 0.04 * ((t - 117.73) / 3.77)
        elif t < 125.0:
            return 1.04 - 0.03 * ((t - 121.5) / 3.5)
        else:
            p = min(1.0, (t - 125.0) / 2.5)
            return 1.01 + 0.055 * (p * p * (3 - 2 * p))

    return 1.0


def render_frame(fi):
    t = fi / FPS
    shot = SHOTS[-1]
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            shot = s
            break

    src = shot["src"]
    if src == "DUAL_SEAWEED_JARS":
        base_rgb = render_dual_seaweed_jars(t, shot["t0"])
    elif src == "FRAMED_YEN_HERO":
        base_rgb = render_framed_yen_hero(t, shot["t0"])
    elif src == "OFFICIAL_F20_ENDCARD":
        base_rgb = render_official_endcard(t, shot["t0"])
    else:
        local_t = shot["ss"] + (t - shot["t0"])
        base_rgb = get_reader(src).get_frame(local_t)
        z = compute_shot_zoom(shot, t)
        base_rgb = apply_symmetric_zoom(base_rgb, z)

    canvas = base_rgb.convert("RGBA")

    # Opening Brand Hook Card (0.15s - 3.75s) inside TikTok Safe Zone!
    if 0.15 <= t <= 3.75:
        alpha_k = min(1.0, (t - 0.15) / 0.25, (3.75 - t) / 0.25)
        if alpha_k > 0.02:
            hk = Image.new("RGBA", (780, 215), (0, 0, 0, 0))
            hd = ImageDraw.Draw(hk)
            hd.rounded_rectangle([4, 4, 775, 210], radius=28, fill=(8, 48, 22, int(216 * alpha_k)), outline=(255, 220, 102, int(230 * alpha_k)), width=2)
            lg = F20_LOGO.resize((66, 66), Image.Resampling.LANCZOS)
            hk.alpha_composite(lg, (26, 24))
            hd.text((108, 22), "THỰC PHẨM F20 × SKA NEST", font=F_TAG, fill=(166, 244, 102, int(255 * alpha_k)))
            hd.text((108, 54), "CHUẨN BỊ 104 SET QUÀ", font=F_HOOK_BIG, fill=(255, 228, 98, int(255 * alpha_k)), stroke_width=2, stroke_fill=(8, 28, 14, int(240 * alpha_k)))
            hd.text((108, 126), "Tri Ân Thầy Cô Ngày Nhà Giáo 20/11", font=F_HOOK_SUB, fill=(255, 255, 255, int(250 * alpha_k)))
            # Center inside TikTok horizontal safe zone (cx=506 -> x=116..896!)
            canvas.alpha_composite(hk, (506 - hk.width // 2, 1260))

    # Smooth Rounded Framed PIP Overlays (Face-Safe on LEFT side x=88 so Chi Oanh's face is 100% clear!)
    pip_mode = shot.get("pip")
    if pip_mode == "HANDLE_ZOOM_PIP" and 98.55 <= t <= 102.75:
        # While Chi Oanh speaks live on camera (face on right x=570..830), zoom smoothly into the real handle on top-left (x=88, y=252) right above the basket!
        u_in = min(1.0, (t - 98.55) / 0.28)
        u_out = min(1.0, (102.75 - t) / 0.25)
        ease = 1.0 - (1.0 - min(u_in, u_out)) ** 3
        f_hdl = get_reader(VID_DIR / "V3_vid14_quai_no_macro.mp4").get_frame(t - 98.55)
        hdl_crop = apply_symmetric_zoom(f_hdl, 1.0 + 0.08 * ((t - 98.55) / 4.2)).crop((140, 360, 940, 1560))
        pw, ph = int(round(300 * (0.85 + 0.15 * ease))), int(round(375 * (0.85 + 0.15 * ease)))
        pcard = make_rounded_pip(hdl_crop, pw, ph, radius=28, border_rgb=(255, 218, 102))
        canvas.alpha_composite(pcard, (88, 252))

    elif pip_mode == "CTA_GIFT_PIP" and 123.30 <= t <= 130.35:
        u_in = min(1.0, (t - 123.30) / 0.30)
        u_out = min(1.0, (130.35 - t) / 0.28)
        ease = 1.0 - (1.0 - min(u_in, u_out)) ** 3
        f_g = get_reader(VID_DIR / "V3_vid01_set_qua_hero.mp4").get_frame(t - 123.30)
        g_crop = f_g.crop((140, 320, 940, 1480))
        pw, ph = int(round(275 * (0.86 + 0.14 * ease))), int(round(355 * (0.86 + 0.14 * ease)))
        pcard = make_rounded_pip(g_crop, pw, ph, radius=26, border_rgb=(146, 232, 78))
        canvas.alpha_composite(pcard, (88, 860))

    # Top Minimal F20 Emerald-Glass Tag (cy=186, cx=508 -> 100% inside TikTok Safe Zone!)
    for tt0, tt1, t_title, t_sub in TOP_TAGS:
        if tt0 <= t <= tt1:
            tcard = get_top_tag_card(t_title, t_sub)
            u_in = min(1.0, (t - tt0) / 0.22)
            u_out = min(1.0, (tt1 - t) / 0.22)
            dy = int(round((1.0 - min(u_in, u_out)) * -22))
            if min(u_in, u_out) < 0.99:
                tc = tcard.copy()
                tc.putalpha(tc.getchannel("A").point(lambda a: int(a * min(u_in, u_out))))
            else:
                tc = tcard
            canvas.alpha_composite(tc, (508 - tc.width // 2, 148 + dy))
            break

    # Integrated Product Pedestal Badge (anchored right at lower base of centered product: cy=1255, cx=508!)
    for bt0, bt1, b_title, b_sub in PRODUCT_BADGES:
        if bt0 <= t <= bt1:
            bcard = get_pedestal_badge(b_title, b_sub)
            u_in = min(1.0, (t - bt0) / 0.20)
            u_out = min(1.0, (bt1 - t) / 0.20)
            vis = min(u_in, u_out)
            dy = int(round((1.0 - vis) * 16))
            bc = bcard if vis >= 0.99 else bcard.copy()
            if vis < 0.99:
                bc.putalpha(bc.getchannel("A").point(lambda a: int(a * vis)))
            canvas.alpha_composite(bc, (508 - bc.width // 2, 1218 + dy))
            break

    # Unified Single-Baseline Subtitle Card (cy=1398, cx=506 -> x within 121..891, y within 1335..1470: 100% TikTok-Safe!)
    for si, (st0, st1, lines) in enumerate(SUBTITLES):
        if st0 <= t <= st1:
            dt_s = t - st0
            # Subtle lively pop on highlighted words during first 0.18s!
            hl_pop = 1.0 + 0.09 * max(0.0, 1.0 - dt_s / 0.18)
            scard = build_subtitle_card(si, lines, hl_pop=hl_pop)
            u_in = min(1.0, dt_s / 0.14)
            u_out = min(1.0, (st1 - t) / 0.14)
            vis = min(u_in, u_out)
            dy = int(round((1.0 - vis) * 14))
            sc = scard if vis >= 0.99 else scard.copy()
            if vis < 0.99:
                sc.putalpha(sc.getchannel("A").point(lambda a: int(a * vis)))
            canvas.alpha_composite(sc, (506 - sc.width // 2, 1396 - sc.height // 2 + dy))
            break

    return canvas.convert("RGB")


def export_edl_json():
    # Export complete Edit Decision List + SFX In/Out schedule for v3_step4_mix_and_capcut.py!
    sfx_events = []
    for s in SHOTS:
        sfx_events.append({"t": round(s["t0"], 3), "sfx": s["sfx_in"], "vol": 0.42, "role": "scene_in"})
    for bt0, bt1, _, _ in PRODUCT_BADGES:
        sfx_events.append({"t": round(bt0, 3), "sfx": "pop_soft", "vol": 0.34, "role": "badge_in"})
        sfx_events.append({"t": round(max(bt0 + 0.3, bt1 - 0.12), 3), "sfx": "swoosh_out", "vol": 0.24, "role": "badge_out"})
    for si, (st0, st1, lines) in enumerate(SUBTITLES):
        has_hl = any(st != "reg" for ln in lines for _, st in ln)
        sfx_events.append({"t": round(st0, 3), "sfx": "ting_quick" if (has_hl and si % 3 == 0) else "pop_telop", "vol": 0.28, "role": "text_in"})
        sfx_events.append({"t": round(max(st0 + 0.3, st1 - 0.10), 3), "sfx": "swoosh_soft", "vol": 0.20, "role": "text_out"})

    # Add PIP in/out SFX
    sfx_events.append({"t": 98.55,  "sfx": "whoosh_pip", "vol": 0.38, "role": "pip_in"})
    sfx_events.append({"t": 102.60, "sfx": "swoosh_out", "vol": 0.26, "role": "pip_out"})
    sfx_events.append({"t": 123.30, "sfx": "whoosh_pip", "vol": 0.36, "role": "pip_in"})
    sfx_events.append({"t": 130.20, "sfx": "swoosh_out", "vol": 0.25, "role": "pip_out"})

    edl = {
        "fps": FPS, "width": W, "height": H, "total_frames": TOTAL_FRAMES, "total_dur": 133.90,
        "shots": [
            {"t0": s["t0"], "t1": s["t1"], "src": str(s["src"]), "ss": s["ss"], "zoom": str(s["zoom"]), "sfx_in": s["sfx_in"], "pip": s.get("pip")}
            for s in SHOTS
        ],
        "top_tags": [{"t0": a, "t1": b, "title": c, "sub": d} for a, b, c, d in TOP_TAGS],
        "product_badges": [{"t0": a, "t1": b, "title": c, "sub": d} for a, b, c, d in PRODUCT_BADGES],
        "subtitles": [
            {
                "t0": st0, "t1": st1,
                "plain_lines": [" ".join(ch for ch, _ in ln) for ln in lines],
                "lines": lines,
            }
            for st0, st1, lines in SUBTITLES
        ],
        "sfx_events": sorted(sfx_events, key=lambda x: x["t"]),
    }
    (V3_DIR / "timeline_v3_capcut_events.json").write_text(json.dumps(edl, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    export_edl_json()
    if "--test" in sys.argv:
        # Render 16 key critique timestamps + TikTok Safe-Zone Proof Sheet!
        test_times = [
            1.20,   # Opening panoramic sets + Hook
            6.10,   # Live Chi Oanh 104 set qua
            16.80,  # Image 1 & 2 Fix: Anh Hau Dang Khoa Edu (natural spacing + sleek F20 header!)
            35.50,  # Image 3 Fix: Continuous long POV 104 sets
            45.20,  # Image 4 Fix: Centered AI Hero Mica Gift Set
            48.00,  # Image 5 Fix: Centered moving SKA NEST round box
            51.00,  # Image 6A Fix: Pure long-strand To Yen
            55.00,  # Image 6B Fix: Tao Do & Dong Trung Ha Thao
            57.10,  # Image 6C Fix: Ky Tu & Duong Phen
            59.60,  # Image 7 Fix: Centered Dual Moving Jars
            65.10,  # Image 8 Fix: Centered Single Jar Say Me + Integrated Pedestal Badge!
            68.80,  # Image 9 Fix: Seamless AI Banh Thuyen 250g
            73.80,  # Image 10A Fix: Seamless AI Rong Bien Kep Hat 500g
            90.20,  # Image 11 Fix: Steaming Chung Yen Pot & Booklet
            100.20, # Image 12A Fix: Live Chi Oanh speaking on handle + Smooth Zoom PIP!
            132.00, # Official F20 Brand End-Card!
        ]
        cols, rows = 4, 4
        grid = Image.new("RGB", (270 * cols, 480 * rows))
        safe_grid = Image.new("RGB", (540 * 2, 960 * 2))

        for idx, ts in enumerate(test_times):
            fr = render_frame(int(round(ts * FPS)))
            thumb = fr.resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(thumb)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(255, 230, 0))
            grid.paste(thumb, ((idx % cols) * 270, (idx // cols) * 480))

            # Draw TikTok Safe-Zone UI overlay on 4 critical frames (16.8s, 65.1s, 100.2s, 132.0s)
            if ts in (16.80, 65.10, 100.20, 132.00):
                s_idx = [16.80, 65.10, 100.20, 132.00].index(ts)
                ov = fr.convert("RGBA")
                ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ud = ImageDraw.Draw(ui)
                # TikTok Top Bar (y=0..130)
                ud.rectangle([0, 0, W, 130], fill=(255, 40, 40, 80))
                # TikTok Right Action Column (x=935..1080, y=760..1620)
                ud.rectangle([935, 760, W, 1620], fill=(255, 40, 40, 95))
                # TikTok Bottom Caption / Username / Progress UI (y=1510..1920)
                ud.rectangle([0, 1510, W, H], fill=(255, 40, 40, 95))
                # Safe green boundary box
                ud.rectangle([80, 135, 930, 1505], outline=(0, 255, 120, 230), width=4)
                ov.alpha_composite(ui)
                safe_grid.paste(ov.convert("RGB").resize((540, 960), Image.Resampling.LANCZOS), ((s_idx % 2) * 540, (s_idx // 2) * 960))

        grid.save(V3_DIR / "v3_test_grid_16.jpg", quality=93)
        safe_grid.save(V3_DIR / "v3_tiktok_safezone_proof.jpg", quality=93)
        print("Saved v3_test_grid_16.jpg & v3_tiktok_safezone_proof.jpg!")
    else:
        out_vid = V3_DIR / "v3_video_only_master.mp4"
        proc = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
            str(out_vid)
        ], stdin=subprocess.PIPE)
        for fi in range(TOTAL_FRAMES):
            fr = render_frame(fi)
            proc.stdin.write(fr.tobytes())
            if fi % 300 == 0 or fi == TOTAL_FRAMES - 1:
                print(f"Rendered {fi+1}/{TOTAL_FRAMES} frames ({(fi+1)/TOTAL_FRAMES*100:.1f}%)", flush=True)
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(f"FFmpeg exited with {rc}")
        print(f"Saved master video stream -> {out_vid}")
