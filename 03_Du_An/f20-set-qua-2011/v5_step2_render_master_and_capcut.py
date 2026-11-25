import copy, json, math, os, shutil, subprocess, sys, time, uuid, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT        = Path(r"d:\AI\full studio\output\f20-set-qua-2011")
V5         = OUT / "v5_master"
CLIPS_V5   = V5 / "clips_v5"
VOICE_V5   = V5 / "voice_v5"
V3_DIR     = OUT / "v3_pro"
VID_V3     = V3_DIR / "videos_v3"
VID_V4     = OUT / "v4_clean_master" / "videos_v4"
SFX_DIR    = OUT / "v2_1117" / "sfx_v2"
SFX_TH     = Path(r"d:\AI\full studio\phong-cach\talking-head\assets_dung_chung\sfx")
BAK_DIR    = OUT / "capcut_backup"
DRAFTS_DIR = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
FONT_DIR   = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")

W, H, FPS, SR = 1080, 1920, 30, 48000
DRAFT_NAME  = "F20_SetQua_2011_V5_Clean"
PLACEHOLDER = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"

# Typography from Studio 39 Vietnamese Fonts & Gradient Pack (AE_FONTS_VA_GRADIENT.md)
F_SUB_REG   = ImageFont.truetype(str(FONT_DIR / "Montserrat-ExtraBold.ttf"), 40)
F_SUB_HL    = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 43)
F_HOOK_BIG  = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 52)
F_HOOK_SUB  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 27)
F_PILL      = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 24)
F_PILL_SM   = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 20)
F_END_BIG   = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 42)
F_END_MED   = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 27)
F_END_SM    = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-SemiBold.ttf"), 22)

F20_LOGO = Image.open(V3_DIR / "refs_clean" / "f20_logo_official.png").convert("RGBA")

# Load exact frame-locked timeline_v5_master.json
TL_V5 = json.loads((V5 / "timeline_v5_master.json").read_text(encoding="utf-8"))
BMAP  = {b["id"]: b for b in TL_V5["blocks"]}

def bt(bid):
    return float(BMAP[bid]["start"]), float(BMAP[bid]["end"])

# ==============================================================================
# 1. COMPLETE SHOT SCHEDULE (Steady 1.00x Natural Motion, Zero Camera Lens,
#    100% Real Packaged Basket/Box, Un-Zoomed Flower & Beige Bow!)
# ==============================================================================
b01_s, b01_e   = bt("b01_open_live")
b02_s, b02_e   = bt("b02_nhatrang_real")
b03_s, b03_e   = bt("b03_ship_104_clean")
b04_s, b04_e   = bt("b04_wide_oanh_104_live")
b05_s, b05_e   = bt("b05_intro_set_live")
b06_s, b06_e   = bt("b06_4items_real_tight")
b07a_s, b07a_e = bt("b07a_yen_giatri_real")
b07b_s, b07b_e = bt("b07b_camnang_live")
b08_s, b08_e   = bt("b08_chungyen_clean")
b09a_s, b09a_e = bt("b09a_giomica_real")
b09b_s, b09b_e = bt("b09b_quai_da_live")
b09c_s, b09c_e = bt("b09c_hoa_no_real")
b10a_s, b10a_e = bt("b10a_sx_live")
b10b_s, b10b_e = bt("b10b_sx_yentam_real")
b11a_s, b11a_e = bt("b11a_cta_live1")
b11b_s, b11b_e = bt("b11b_cta_2011_real")
b11c_s, b11c_e = bt("b11c_cta_inbox_live")
tot_end        = float(TL_V5["total_dur"])

SHOTS = [
    # 0.00 - 3.90s: 3-Shot Pure Product Pan Intro ("mấy giây đầu là cảnh lia sản phẩm mà???")
    {"t0": 0.00,   "t1": 1.30,   "src": CLIPS_V5 / "br_intro1_sunlit_sets.mp4", "ss": 0.0, "live": False},
    {"t0": 1.30,   "t1": 2.60,   "src": CLIPS_V5 / "br_intro2_long_table.mp4",  "ss": 0.0, "live": False},
    {"t0": 2.60,   "t1": b01_s,  "src": CLIPS_V5 / "br_intro3_shelf_tower.mp4", "ss": 0.0, "live": False},

    # b01_open_live (3.90 - 13.10s): Live Chi Oanh centered at x=540 + Floating Gift Overlay!
    {"t0": b01_s,  "t1": b01_e,  "src": CLIPS_V5 / "b01_open_live.mp4",         "ss": 0.0, "live": True},

    # b02_nhatrang_real (13.10 - 23.40s): Real Sony Anh Hau Handover (77 sets) + Phu Huynh (13 sets)
    {"t0": b02_s,        "t1": b02_s + 2.75, "src": CLIPS_V5 / "br_anh_hau_handover.mp4", "ss": 0.0, "live": False},
    {"t0": b02_s + 2.75, "t1": b02_s + 6.55, "src": CLIPS_V5 / "br_anh_hau_77sets.mp4",   "ss": 0.0, "live": False},
    {"t0": b02_s + 6.55, "t1": b02_e,        "src": CLIPS_V5 / "br_phu_huynh_13sets.mp4", "ss": 0.0, "live": False},

    # b03_ship_104_clean (23.40 - 34.20s): Ha Noi + TP.HCM + Wide Chi Oanh Amidst 104 Sets (ZERO Camera Lens!)
    {"t0": b03_s,        "t1": b03_s + 3.25, "src": CLIPS_V5 / "br_hanoi_carton.mp4",      "ss": 0.0, "live": False},
    {"t0": b03_s + 3.25, "t1": b03_s + 6.35, "src": CLIPS_V5 / "br_hcmc_suv.mp4",          "ss": 0.0, "live": False},
    {"t0": b03_s + 6.35, "t1": b03_s + 8.65, "src": CLIPS_V5 / "br_wide_oanh_row_104.mp4", "ss": 0.0, "live": False},
    {"t0": b03_s + 8.65, "t1": b03_e,        "src": CLIPS_V5 / "br_clean_row_104sets.mp4", "ss": 0.0, "live": False},

    # b04_wide_oanh_104_live (34.20 - 38.87s): Live Wide Chi Oanh Standing Center With Open Arms Amidst 104 Sets!
    {"t0": b04_s,  "t1": b04_e,  "src": CLIPS_V5 / "b04_wide_oanh_104_live.mp4","ss": 0.0, "live": True},

    # b05_intro_set_live (38.87 - 43.93s): Live Chi Oanh Centered + Floating Inside-Basket Overlay!
    {"t0": b05_s,  "t1": b05_e,  "src": CLIPS_V5 / "b05_intro_set_live.mp4",    "ss": 0.0, "live": True},

    # b06_4items_real_tight (43.93 - 82.23s): 100% Real Packaged Basket & SKA NEST Box + Harmonized Product Showcases (ZERO Bad Zoom!)
    {"t0": b06_s,         "t1": 48.20, "src": CLIPS_V5 / "br_basket_full_hero.mp4",     "ss": 0.0, "live": False},
    {"t0": 48.20,         "t1": 53.80, "src": "COMPOSITE_SKANEST_HERO",                 "ss": 0.0, "live": False},
    {"t0": 53.80,         "t1": 60.25, "src": CLIPS_V5 / "br_inside_basket_real.mp4",   "ss": 0.0, "live": False},
    {"t0": 60.25,         "t1": 63.48, "src": VID_V4   / "V4_vid02_two_jars_even.mp4",  "ss": 0.0, "live": False, "warm_match": True},
    {"t0": 63.48,         "t1": 65.76, "src": VID_V3   / "V3_vid06_hu_say_gion.mp4",    "ss": 0.2, "live": False, "warm_match": True},
    {"t0": 65.76,         "t1": 68.05, "src": VID_V3   / "V3_vid07_hu_say_me.mp4",      "ss": 0.2, "live": False, "warm_match": True},
    {"t0": 68.05,         "t1": 72.76, "src": VID_V3   / "V3_vid08_banh_thuyen.mp4",    "ss": 0.0, "live": False, "warm_match": True},
    {"t0": 72.76,         "t1": 77.22, "src": VID_V3   / "V3_vid09_kep_hat.mp4",        "ss": 0.0, "live": False, "warm_match": True},
    {"t0": 77.22,         "t1": b06_e, "src": VID_V4   / "V4_vid03_24_thanh_hat.mp4",   "ss": 0.0, "live": False, "warm_match": True},

    # b07a_yen_giatri_real (82.23 - 88.97s): Shelf Pan + Large Centered Real SKA NEST Showcase Overlay (NO fake red velvet box!)
    {"t0": b07a_s, "t1": b07a_e, "src": CLIPS_V5 / "br_shelf_sets_pan.mp4",     "ss": 0.0, "live": False},

    # b07b_camnang_live (88.97 - 98.00s): Live Centered Chi Oanh Holding Blue Booklet + Floating Booklet Close-Up Overlay!
    {"t0": b07b_s, "t1": b07b_e, "src": CLIPS_V5 / "b07b_camnang_live.mp4",     "ss": 0.0, "live": True},

    # b08_chungyen_clean (98.00 - 101.20s): Warm Porcelain Bird's Nest Bowl
    {"t0": b08_s,  "t1": b08_e,  "src": VID_V3   / "V3_vid10_chung_yen.mp4",    "ss": 0.0, "live": False, "warm_match": True},

    # b09a_giomica_real (101.20 - 107.43s): Clean Un-Zoomed Full Mica Gift Basket
    {"t0": b09a_s, "t1": b09a_e, "src": CLIPS_V5 / "br_basket_full_hero.mp4",   "ss": 1.5, "live": False},

    # b09b_quai_da_live (107.43 - 112.87s): Live Centered Chi Oanh + 3D Circular Magnifying Glass Loupe ("KÍNH LÚP CÁI QUAI")!
    {"t0": b09b_s, "t1": b09b_e, "src": CLIPS_V5 / "b09b_quai_da_live.mp4",     "ss": 0.0, "live": True},

    # b09c_hoa_no_real (112.87 - 118.57s): Full Gift Basket Shots at 1.00x ZERO ZOOM ("lấy cảnh cái gói quà là tự thấy hoa rồi, không zoom lên. image 9 cũng vậy k đc zoom nha")!
    {"t0": b09c_s,        "t1": b09c_s + 2.65, "src": CLIPS_V5 / "br_basket_flower_bow.mp4", "ss": 0.0, "live": False},
    {"t0": b09c_s + 2.65, "t1": b09c_e,        "src": CLIPS_V5 / "br_basket_row_bow.mp4",    "ss": 0.0, "live": False},

    # b10a_sx_live & b10b_sx_yentam_real (118.57 - 126.77s)
    {"t0": b10a_s, "t1": b10a_e, "src": CLIPS_V5 / "b10a_sx_live.mp4",          "ss": 0.0, "live": True},
    {"t0": b10b_s, "t1": b10b_e, "src": CLIPS_V5 / "br_factory_pack1.mp4",      "ss": 0.0, "live": False},

    # b11a_cta_live1 + b11b_cta_2011_real + b11c_cta_inbox_live + Official End-Card
    {"t0": b11a_s, "t1": b11a_e, "src": CLIPS_V5 / "b11a_cta_live1.mp4",        "ss": 0.0, "live": True},
    {"t0": b11b_s, "t1": b11b_e, "src": CLIPS_V5 / "br_wide_oanh_arms_104.mp4", "ss": 0.2, "live": False},
    {"t0": b11c_s, "t1": b11c_e, "src": CLIPS_V5 / "b11c_cta_inbox_live.mp4",   "ss": 0.0, "live": True},
    {"t0": b11c_e, "t1": tot_end,"src": "OFFICIAL_ENDCARD_V5",                  "ss": 0.0, "live": False},
]


# ==============================================================================
# 2. ANIMATED FLOATING OVERLAYS ("LỚP PHỦ NHẢY LÊN TRÊN CHỊ OANH") & CALLOUTS
# ==============================================================================
FLOATING_OVERLAYS = [
    # 1. On b01_open_live: Gift basket PIP springs in on top-left while Chi Oanh speaks!
    {"t0": b01_s + 3.80, "t1": b01_e - 0.35, "src": CLIPS_V5 / "br_basket_flower_bow.mp4", "ss": 0.2,
     "cx": 228, "cy": 415, "pw": 292, "ph": 376, "crop": (160, 420, 920, 1520), "from_dir": -1, "label": "QUÀ BIẾU 20/11"},

    # 2. On b05_intro_set_live: Inside-basket PIP springs in on top-left!
    {"t0": b05_s + 0.95, "t1": b05_e - 0.30, "src": CLIPS_V5 / "br_inside_basket_real.mp4", "ss": 0.4,
     "cx": 228, "cy": 415, "pw": 292, "ph": 376, "crop": (120, 320, 960, 1460), "from_dir": -1, "label": "04 MÓN TRONG SET"},

    # 3. On b06 (53.80-60.25s, inside basket real): Packaged SKA NEST 4-compartment box inset on top-right!
    {"t0": 54.05, "t1": 60.10, "src": CLIPS_V5 / "real_skanest_round_box.mp4", "ss": 0.2,
     "cx": 798, "cy": 388, "pw": 318, "ph": 330, "crop": (70, 310, 1010, 1320), "from_dir": +1, "label": "ĐỦ NGUYÊN LIỆU CHƯNG"},

    # 4. On b07a_yen_giatri_real: Large Centered Authentic F20 Gift Basket & SKA NEST Showcase over sunlit shelf pan!
    {"t0": b07a_s + 0.25, "t1": b07a_e - 0.25, "src": VID_V4 / "V4_vid01_hero_giftset.mp4", "ss": 0.2,
     "cx": 540, "cy": 690, "pw": 650, "ph": 710, "crop": (150, 300, 930, 1420), "from_dir": 0, "label": "TỔ YẾN SỢI DÀI • SKA NEST"},

    # 5. On b07b_camnang_live: Tight close-up on Blue Booklet & Steaming Yen PIP (NO duplicate face!)
    {"t0": b07b_s + 1.40, "t1": b07b_e - 0.35, "src": VID_V3 / "V3_vid10_chung_yen.mp4", "ss": 0.2,
     "cx": 228, "cy": 420, "pw": 288, "ph": 360, "crop": (160, 420, 920, 1460), "from_dir": -1, "label": "CẨM NANG & CÔNG DỤNG"},

    # 6. On b10a_sx_live: Factory packing PIP springs in on top-right while Chi Oanh speaks!
    {"t0": b10a_s + 1.05, "t1": b10a_e - 0.28, "src": CLIPS_V5 / "br_factory_pack1.mp4", "ss": 0.3,
     "cx": 838, "cy": 415, "pw": 288, "ph": 370, "crop": (160, 360, 920, 1460), "from_dir": +1, "label": "F20 TRỰC TIẾP SX"},

    # 7. On b11a_cta_live1: Sunlit gift basket PIP springs in on top-left during Thank-You!
    {"t0": b11a_s + 1.20, "t1": b11a_e - 0.28, "src": CLIPS_V5 / "br_basket_full_hero.mp4", "ss": 0.5,
     "cx": 228, "cy": 418, "pw": 288, "ph": 372, "crop": (180, 460, 900, 1520), "from_dir": -1, "label": "ĐẶT SỈ & LẺ 20/11"},
]

# 4 Authentic Packaged Ingredient Callout Pills (55.85s - 60.15s over real inside-basket + SKA NEST box!)
INGREDIENT_PILLS = [
    (55.85, 60.15, "01 • TÁO ĐỎ",              (158, 22, 42, 238), (255, 224, 132), 295, 1085),
    (56.80, 60.15, "02 • ĐÔNG TRÙNG HẠ THẢO",  (138, 74, 14, 238), (255, 232, 148), 755, 1085),
    (58.15, 60.15, "03 • KỶ TỬ",               (168, 36, 24, 238), (255, 224, 132), 295, 1172),
    (58.90, 60.15, "04 • 01 HỘP ĐƯỜNG PHÈN",   ( 18, 78, 44, 238), (168, 245, 192), 755, 1172),
]


# ==============================================================================
# 3. KINETIC SUBTITLES (Locked to Stumble-Free V5 Whisper Word Timestamps!)
# ==============================================================================
SUBTITLES = [
    (b01_s + 0.05,  8.65,  [[("Hôm nay bên Oanh chuẩn bị", False)],
                            [("104 SET QUÀ", True), ("cho khách đặt", False)]]),
    (8.72,         10.82,  [[("để làm", False), ("QUÀ BIẾU TẶNG", True)],
                            [("thầy cô giáo", False)]]),
    (10.88,    b01_e-0.05, [[("nhân dịp tri ân", False)],
                            [("NGÀY 20 THÁNG 11", True)]]),

    (b02_s + 0.08, 15.75,  [[("Ở", False), ("NHA TRANG", True)],
                            [("có 02 khách hàng:", False)]]),
    (15.82,        19.55,  [[("1 là", False), ("ANH HẬU", True)],
                            [("ĐĂNG KHOA EDU •", False), ("77 SET", True)]]),
    (19.68,    b02_e-0.06, [[("2 là nhóm", False), ("HỘI PHỤ HUYNH", True)],
                            [("đặt", False), ("13 SET QUÀ", True)]]),

    (b03_s + 0.05, 26.58,  [[("Khách thứ 3 ở", False), ("HÀ NỘI", True)],
                            [("đặt", False), ("10 SET QUÀ", True)]]),
    (26.68,        29.66,  [[("và một bạn ở", False), ("TP. HỒ CHÍ MINH", True)],
                            [("đặt", False), ("04 SET QUÀ", True)]]),
    (29.74,    b03_e-0.08, [[("Tổng sáng nay bên Oanh chuẩn bị", False)],
                            [("ĐỦ 104 SET QUÀ", True), ("nha!", False)]]),

    (b04_s + 0.10, b04_e-0.08, [[("Đây là những", False), ("SET QUÀ", True)],
                                [("bên Oanh", False), ("chuẩn bị xong", True), ("sáng nay!", False)]]),

    (b05_s + 0.12, b05_e-0.08, [[("Bây giờ Oanh giới thiệu", False)],
                                [("01 SET QUÀ", True), ("cho mọi người xem!", False)]]),

    (b06_s + 0.10, 48.12,  [[("Một", False), ("SET QUÀ TẶNG", True), ("như thế này", False)],
                            [("bên trong sẽ gồm có:", False)]]),
    (48.20,        50.35,  [[("Đầu tiên là", False)],
                            [("01 SET YẾN SÀO", True)]]),
    (50.42,        53.72,  [[("gồm", False), ("01 TỔ YẾN TINH CHẾ", True)],
                            [("sợi dài • dòng", False), ("TIÊU CHUẨN", True)]]),
    (53.85,        55.82,  [[("kèm theo đầy đủ", False)],
                            [("NGUYÊN LIỆU CHƯNG", True)]]),
    (55.88,        58.12,  [[("gồm có:", False), ("TÁO ĐỎ", True)],
                            [("và", False), ("ĐÔNG TRÙNG HẠ THẢO", True)]]),
    (58.18,        60.15,  [[("cùng", False), ("KỶ TỬ", True)],
                            [("và", False), ("01 HỘP ĐƯỜNG PHÈN", True)]]),

    (60.30,        63.40,  [[("Thứ 2 là", False), ("02 HỘP RONG BIỂN", True)],
                            [("sấy giòn", False), ("TUỆ TÂM", True)]]),
    (63.50,        65.70,  [[("01 hộp", False), ("RONG BIỂN SẤY GIÒN", True)],
                            [("vị", False), ("CAY NHẸ", True)]]),
    (65.80,        67.98,  [[("và 01 hộp", False), ("RONG BIỂN SẤY MÈ", True)],
                            [("vị", False), ("KHÔNG CAY", True)]]),

    (68.08,        72.68,  [[("Thứ 3 là 01 gói", False), ("BÁNH THUYỀN", True)],
                            [("mix hạt dinh dưỡng", False), ("250G", True)]]),
    (72.80,        77.12,  [[("Thứ 4 là 01 gói", False)],
                            [("RONG BIỂN KẸP HẠT 500G", True)]]),
    (77.26,    b06_e-0.08, [[("bên trong có", False), ("22 – 24 THANH", True)],
                            [("bánh hạt dinh dưỡng", True), ("nhé!", False)]]),

    (b07a_s + 0.12,b07a_e-0.08,[[("Giá trị nhất là", False), ("TỔ YẾN TINH CHẾ", True)],
                                [("dòng tiêu chuẩn", False), ("SỢI DÀI", True)]]),
    (b07b_s + 0.08, 94.22, [[("Bên Oanh chuẩn bị thêm", False)],
                            [("01 TỜ CẨM NANG", True), ("sử dụng yến sào", False)]]),
    (94.30,    b07b_e-0.06,[[("nêu rõ", False)],
                            [("CÔNG DỤNG CỦA YẾN SÀO", True)]]),
    (b08_s + 0.06, b08_e-0.06, [[("và hướng dẫn", False)],
                                [("CHƯNG YẾN ĐÚNG CÁCH", True)]]),

    (b09a_s + 0.08,b09a_e-0.08,[[("Tất cả xếp trong", False), ("GIỎ ĐỰNG QUÀ", True)],
                                [("chất liệu", False), ("MICA TRONG SUỐT", True)]]),
    (b09b_s + 0.08,b09b_e-0.08,[[("Bên trên có", False), ("QUAI XÁCH DA", True)],
                                [("MÀU ĐỎ ĐÔ", True), ("rất sang trọng!", False)]]),
    (b09c_s + 0.06,b09c_s+2.58,[[("Có thiết kế thêm", False)],
                                [("BÔNG HOA ĐIỂM NHẤN", True)]]),
    (b09c_s + 2.66,b09c_e-0.06,[[("và một chiếc", False), ("NƠ MÀU BE", True)],
                                [("rất xinh xắn như thế này!", False)]]),

    (b10a_s + 0.08,b10a_e-0.06,[[("Sản phẩm trong set đều do", False)],
                                [("BÊN OANH TRỰC TIẾP SẢN XUẤT", True)]]),
    (b10b_s + 0.06,b10b_e-0.06,[[("yên tâm về", False)],
                                [("CHẤT LƯỢNG & GIÁ CẢ", True), ("nhé!", False)]]),

    (b11a_s + 0.08,b11a_e-0.08,[[("Cảm ơn quý anh chị tin tưởng", False)],
                                [("đặt hàng của", False), ("THỰC PHẨM F20", True)]]),
    (b11b_s + 0.08,b11b_s+3.00,[[("Anh chị có nhu cầu", False)],
                                [("ĐẶT SET QUÀ TẶNG", True)]]),
    (b11b_s + 3.06,b11b_e-0.06,[[("làm quà biếu tặng dịp lễ", False)],
                                [("20 THÁNG 11", True)]]),
    (b11c_s + 0.05,b11c_e-0.06,[[("hãy", False), ("INBOX NGAY", True), ("cho Oanh nhé!", False)]]),
]


# ==============================================================================
# 4. VIDEO SLICE READER (Low-RAM LRU + Steady 1.00x Forward Playback + Warm Match)
# ==============================================================================
class SliceReader:
    def __init__(self, mp4_path, ss=0.0, max_dur=12.0, warm_match=False, native_size=False):
        self.path = str(mp4_path)
        self.ss = float(ss)
        self.max_dur = float(max_dur)
        self.warm_match = warm_match
        self.native_size = native_size
        self.frames = None
        self.w = W
        self.h = H

    def load(self):
        if self.frames is not None:
            return
        cmd = ["ffmpeg", "-v", "error"]
        if self.ss > 0.04:
            cmd += ["-ss", f"{self.ss:.3f}"]
        vf_parts = []
        if not self.native_size:
            vf_parts.append("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:(ih-1920)/2")
        if self.warm_match:
            vf_parts.append("eq=brightness=0.025:contrast=1.03:saturation=1.06:gamma=0.96")
        vf_parts.append("fps=30")
        cmd += ["-t", f"{self.max_dur + 0.5:.3f}", "-i", self.path, "-vf", ",".join(vf_parts), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        raw = proc.stdout.read()
        proc.wait()
        n = len(raw) // (self.w * self.h * 3)
        self.frames = np.frombuffer(raw[:n * self.w * self.h * 3], dtype=np.uint8).reshape((n, self.h, self.w, 3))

    def get_frame(self, local_t, needed_dur, is_live=False):
        self.load()
        n = len(self.frames)
        if n == 0:
            return Image.new("RGB", (self.w, self.h), (18, 48, 26))
        if is_live:
            idx = max(0, min(n - 1, int(round(local_t * FPS))))
            return Image.fromarray(self.frames[idx])
        avail_s = max(0.2, (n - 1) / FPS)
        rate = min(1.0, avail_s / max(0.2, needed_dur))
        pos_f = local_t * rate * FPS
        i0 = max(0, min(n - 1, int(math.floor(pos_f))))
        i1 = max(0, min(n - 1, i0 + 1))
        frac = pos_f - math.floor(pos_f)
        if i0 == i1 or frac < 0.02:
            return Image.fromarray(self.frames[i0])
        bl = (self.frames[i0].astype(np.float32) * (1.0 - frac) + self.frames[i1].astype(np.float32) * frac).astype(np.uint8)
        return Image.fromarray(bl)

READERS = {}
READER_ORDER = []
def get_reader(p, ss=0.0, dur=6.0, warm_match=False):
    k = (str(p), round(float(ss), 2), round(float(dur), 2), bool(warm_match))
    if k not in READERS:
        if len(READER_ORDER) >= 4:
            old_k = READER_ORDER.pop(0)
            READERS.pop(old_k, None)
        READERS[k] = SliceReader(p, ss=ss, max_dur=dur, warm_match=warm_match)
        READER_ORDER.append(k)
    return READERS[k]


# ==============================================================================
# 5. LUXURY FLOATING OVERLAYS, 3D GOLD LOUPE ("KÍNH LÚP CÁI QUAI"), & TYPOGRAPHY
# ==============================================================================
def ease_out_back(u):
    u = max(0.0, min(1.0, u))
    c1 = 1.45
    c3 = c1 + 1.0
    return 1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2)

def quintic(u):
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

PILL_CACHE = {}
def get_pill_sprite(text, bg_rgba, border_rgb, small=False):
    k = (text, bg_rgba, border_rgb, small)
    if k in PILL_CACHE:
        return PILL_CACHE[k]
    fnt = F_PILL_SM if small else F_PILL
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = d0.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pw, ph = tw + (34 if small else 46), (40 if small else 52)
    im = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
    sh = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([8, 11, 8 + pw, 11 + ph], radius=ph // 2, fill=(0, 0, 0, 125))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4.5)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 7, 8 + pw, 7 + ph], radius=ph // 2, fill=bg_rgba, outline=(*border_rgb, 245), width=2)
    d.text((8 + (pw - tw) // 2 - bb[0], 7 + (ph - th) // 2 - bb[1]), text, font=fnt, fill=(255, 250, 232, 255))
    PILL_CACHE[k] = im
    return im

def draw_floating_overlay_card(canvas, ov, t):
    dt = t - ov["t0"]
    rem = ov["t1"] - t
    dur = ov["t1"] - ov["t0"]
    u_in = min(1.0, max(0.0, dt / 0.34))
    u_out = min(1.0, max(0.0, rem / 0.28))
    if min(u_in, u_out) <= 0.01:
        return

    sc_anim = ease_out_back(u_in) if rem > 0.28 else (0.86 + 0.14 * quintic(u_out))
    alpha_u = quintic(min(u_in * 1.25, u_out))

    fr = get_reader(ov["src"], ss=ov["ss"], dur=dur).get_frame(dt, dur, is_live=False)
    x0, y0, x1, y1 = ov["crop"]
    pw, ph = ov["pw"], ov["ph"]
    cropped = fr.crop((x0, y0, x1, y1)).resize((pw, ph), Image.Resampling.BICUBIC)

    # Diagonal specular sheen across overlay card!
    arr = np.array(cropped, dtype=np.float32)
    sheen_p = -0.3 + 1.6 * ((dt % 2.8) / 2.8)
    yy, xx = np.ogrid[0:ph, 0:pw]
    diag = (xx * 0.8 + yy * 0.45) / max(1.0, pw * 0.8 + ph * 0.45)
    sh_v = np.exp(-((diag - sheen_p) ** 2) / 0.008) * 32.0
    arr = np.clip(arr + sh_v[:, :, None], 0, 255).astype(np.uint8)

    pad = 18
    cw, ch = pw + pad * 2, ph + pad * 2 + 26
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    rad = 28
    # Soft drop shadow
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 6, pad + pw, pad + 6 + ph], radius=rad, fill=(0, 0, 0, 150))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6.5)))

    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=rad, fill=255)
    inner = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    inner.paste(Image.fromarray(arr, "RGB"), (pad, pad), mask=mask)
    card.alpha_composite(inner)

    d = ImageDraw.Draw(card)
    d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=rad, outline=(255, 224, 112, 248), width=3)
    d.rounded_rectangle([pad + 5, pad + 5, pad + pw - 6, pad + ph - 6], radius=max(10, rad - 5), outline=(255, 250, 228, 120), width=1)

    if ov.get("label"):
        pil = get_pill_sprite(ov["label"], (14, 68, 32, 242), (255, 222, 112), small=True)
        card.alpha_composite(pil, (cw // 2 - pil.width // 2, pad + ph - pil.height // 2 - 2))

    if abs(sc_anim - 1.0) > 0.006:
        nw = max(4, int(round(cw * sc_anim)))
        nh = max(4, int(round(ch * sc_anim)))
        card = card.resize((nw, nh), Image.Resampling.BICUBIC)
    if alpha_u < 0.99:
        card.putalpha(card.getchannel("A").point(lambda a: int(a * alpha_u)))

    slide_dx = int(round(ov["from_dir"] * (1.0 - quintic(u_in)) * 68))
    slide_dy = int(round((1.0 - quintic(u_in)) * 28)) if ov["from_dir"] == 0 else 0
    canvas.alpha_composite(card, (ov["cx"] - card.width // 2 + slide_dx, ov["cy"] - card.height // 2 + slide_dy))


def draw_handle_magnifying_loupe(canvas, t):
    # Active during b09b_quai_da_live ("Ở bên trên sẽ có cái quai xách bằng da màu đỏ đô rất sang trọng ạ")
    t0 = b09b_s + 0.55
    t1 = b09b_e - 0.18
    if not (t0 <= t <= t1):
        return
    dt = t - t0
    rem = t1 - t
    dur = t1 - t0
    u_in = min(1.0, max(0.0, dt / 0.36))
    u_out = min(1.0, max(0.0, rem / 0.26))
    vis = quintic(min(u_in * 1.2, u_out))
    sc_l = ease_out_back(u_in) if rem > 0.26 else (0.75 + 0.25 * quintic(u_out))

    # Target point on actual crimson leather handle in Chi Oanh's hand: (392, 668)
    tx, ty = 392, 668
    # Circular Magnifying Glass Loupe center (Face-Safe & TikTok Top-Safe!): (238, 402), diameter = 312px
    lx, ly = 238, 402
    diam = 312

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # 1. Animated Golden Target Ring + Trim-Path Leader Line from real handle -> Loupe!
    line_prog = quintic(min(1.0, dt / 0.25))
    pulse = 1.0 + 0.14 * math.sin(dt * 6.5)
    r_dot = int(round(16 * pulse))
    od.ellipse([tx - r_dot - 6, ty - r_dot - 6, tx + r_dot + 6, ty + r_dot + 6], outline=(255, 226, 108, int(155 * vis)), width=2)
    od.ellipse([tx - 8, ty - 8, tx + 8, ty + 8], fill=(255, 232, 118, int(250 * vis)), outline=(140, 18, 32, int(255 * vis)), width=2)
    ex = int(round(tx + (lx + 75 - tx) * line_prog))
    ey = int(round(ty + (ly + 115 - ty) * line_prog))
    od.line([(tx, ty), (ex, ey)], fill=(255, 228, 112, int(235 * vis)), width=4)

    # 2. Build 3D Champagne-Gold Magnifying Glass Sprite!
    fr_m = get_reader(VID_V3 / "V3_vid14_quai_no_macro.mp4", ss=0.2, dur=dur, warm_match=True).get_frame(dt, dur, is_live=False)
    # Crop directly onto the crimson stitched leather handle arch (steady 1.00x inside the loupe!)
    lens_crop = fr_m.crop((130, 660, 910, 1440)).resize((diam, diam), Image.Resampling.BICUBIC)

    pad = 42
    sw, sh_s = diam + pad * 2, diam + pad * 2 + 24
    sp = Image.new("RGBA", (sw, sh_s), (0, 0, 0, 0))

    # Drop shadow + Magnifier Handle Stub at bottom-right (42 deg)
    sd = ImageDraw.Draw(sp)
    cx_s, cy_s = sw // 2, pad + diam // 2
    # Magnifying glass handle bar!
    ang = math.radians(48)
    hx0 = cx_s + int(math.cos(ang) * (diam // 2 - 4))
    hy0 = cy_s + int(math.sin(ang) * (diam // 2 - 4))
    hx1 = cx_s + int(math.cos(ang) * (diam // 2 + 46))
    hy1 = cy_s + int(math.sin(ang) * (diam // 2 + 46))
    sd.line([(hx0 + 3, hy0 + 5), (hx1 + 3, hy1 + 5)], fill=(0, 0, 0, 140), width=22)
    sd.line([(hx0, hy0), (hx1, hy1)], fill=(138, 22, 36, 255), width=20)
    sd.line([(hx0, hy0), (hx1, hy1)], fill=(255, 222, 114, 240), width=6)

    shadow = Image.new("RGBA", (sw, sh_s), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([pad, pad + 8, pad + diam, pad + 8 + diam], fill=(0, 0, 0, 165))
    sp.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8.0)))

    # Circular lens mask
    cmask = Image.new("L", (diam, diam), 0)
    ImageDraw.Draw(cmask).ellipse([0, 0, diam - 1, diam - 1], fill=255)
    lens_rgba = Image.new("RGBA", (sw, sh_s), (0, 0, 0, 0))
    lens_rgba.paste(lens_crop, (pad, pad), mask=cmask)

    # Subtle curved glass highlight reflection at top-left of lens!
    gl = Image.new("RGBA", (diam, diam), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.arc([16, 16, diam - 16, diam - 16], start=198, end=262, fill=(255, 255, 255, 135), width=10)
    gd.arc([28, 28, diam - 28, diam - 28], start=204, end=252, fill=(255, 255, 255, 70), width=5)
    gl = gl.filter(ImageFilter.GaussianBlur(1.5))
    lens_rgba.alpha_composite(gl, (pad, pad))
    sp.alpha_composite(lens_rgba)

    # 3D Double Metallic Champagne-Gold Rim
    sd = ImageDraw.Draw(sp)
    sd.ellipse([pad - 4, pad - 4, pad + diam + 3, pad + diam + 3], outline=(168, 108, 22, 255), width=9)
    sd.ellipse([pad - 2, pad - 2, pad + diam + 1, pad + diam + 1], outline=(255, 232, 128, 255), width=5)
    sd.ellipse([pad + 4, pad + 4, pad + diam - 5, pad + diam - 5], outline=(255, 252, 232, 165), width=2)

    # Mini pill label anchored cleanly under the magnifying glass
    tag = get_pill_sprite("QUAI DA ĐỎ ĐÔ", (138, 18, 36, 245), (255, 226, 118), small=True)
    sp.alpha_composite(tag, (cx_s - tag.width // 2, pad + diam - tag.height // 2 + 4))

    if abs(sc_l - 1.0) > 0.006:
        nw = max(8, int(round(sw * sc_l)))
        nh = max(8, int(round(sh_s * sc_l)))
        sp = sp.resize((nw, nh), Image.Resampling.BICUBIC)
    if vis < 0.99:
        sp.putalpha(sp.getchannel("A").point(lambda a: int(a * vis)))

    overlay.alpha_composite(sp, (lx - sp.width // 2, ly - sp.height // 2))
    canvas.alpha_composite(overlay)


# ==============================================================================
# 6. COMPOSITE SCENES (SKA NEST Hero & Festive End-Card) + KINETIC SUBTITLES
# ==============================================================================
def render_composite_skanest_hero(t, shot_t0, dur):
    dt = t - shot_t0
    bg_f = get_reader(CLIPS_V5 / "br_basket_full_hero.mp4", ss=0.8, dur=dur).get_frame(dt, dur)
    bg = bg_f.resize((270, 480), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.Resampling.BILINEAR).convert("RGBA")
    bg.alpha_composite(Image.new("RGBA", (W, H), (24, 14, 8, 86)))

    # Centered steady 1.00x Real Packaged SKA NEST Round Box Card (ZERO ugly zoom!)
    f_ska = get_reader(CLIPS_V5 / "real_skanest_round_box.mp4", ss=0.0, dur=dur).get_frame(dt, dur)
    pw, ph = 790, 820
    crop_s = f_ska.crop((40, 270, 1040, 1350)).resize((pw, ph), Image.Resampling.BICUBIC)

    u = quintic(min(1.0, dt / 0.35))
    pad = 22
    card = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + pw, pad + 8 + ph], radius=38, fill=(0, 0, 0, 155))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8.0)))
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=38, fill=255)
    inner = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    inner.paste(crop_s, (pad, pad), mask=mask)
    card.alpha_composite(inner)
    ImageDraw.Draw(card).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=38, outline=(255, 224, 114, 248), width=4)

    bg.alpha_composite(card, (540 - card.width // 2, int(round(325 + (1.0 - u) * 26))))
    pil = get_pill_sprite("YẾN SÀO CAO CẤP SKA NEST • NGUYÊN TỔ SỢI DÀI", (138, 18, 34, 242), (255, 226, 118), small=False)
    bg.alpha_composite(pil, (540 - pil.width // 2, 1152))
    return bg.convert("RGB")


WORD_CACHE = {}
def render_word_sprite(text, style_mode, is_gold_font=False, custom_font=None):
    key = (text, style_mode, is_gold_font, id(custom_font) if custom_font else 0)
    if key in WORD_CACHE:
        return WORD_CACHE[key]
    fnt = custom_font if custom_font else (F_SUB_HL if is_gold_font else F_SUB_REG)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    sw_px = 4 if custom_font == F_HOOK_BIG else 3
    bb = dummy.textbbox((0, 0), text, font=fnt, stroke_width=sw_px)
    pad = 12
    tw, th = (bb[2] - bb[0]) + pad * 2, (bb[3] - bb[1]) + pad * 2
    ox, oy = -bb[0] + pad, -bb[1] + pad

    base = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    glow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((ox, oy + 3), text, font=fnt, fill=(0, 0, 0, 185), stroke_width=sw_px + 3, stroke_fill=(0, 0, 0, 175))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4.2)))

    # Layer 1 (.grad-back): Outer dark stroke so stroke NEVER eats into gradient!
    ImageDraw.Draw(base).text((ox, oy), text, font=fnt, fill=(18, 22, 16, 255), stroke_width=sw_px, stroke_fill=(12, 18, 12, 248))

    # Layer 2 (.grad-front): 5-Stop Champagne Gold Gradient or Crisp White/Ivory
    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).text((ox, oy), text, font=fnt, fill=255)
    if style_mode in ("white", "active_white"):
        col = (255, 255, 255, 255) if style_mode == "white" else (255, 250, 218, 255)
        fi = Image.new("RGBA", (tw, th), col)
        fi.putalpha(mask)
        base.alpha_composite(fi)
    else:
        grad = np.zeros((th, tw, 4), dtype=np.uint8)
        ys = np.linspace(0.0, 1.0, th)
        stops_x = [0.0, 0.26, 0.52, 0.78, 1.0]
        if style_mode == "active_gold":
            stops_c = [(255, 254, 232), (255, 232, 108), (242, 172, 22), (255, 238, 152), (218, 132, 12)]
        else:
            stops_c = [(255, 249, 205), (255, 216, 68), (232, 154, 16), (255, 228, 128), (198, 118, 10)]
        for c in range(3):
            line_c = np.interp(ys, stops_x, [s[c] for s in stops_c])
            grad[:, :, c] = np.clip(line_c, 0, 255).astype(np.uint8)[:, None]
        grad[:, :, 3] = np.array(mask)
        base.alpha_composite(Image.fromarray(grad, "RGBA"))

    adv = fnt.getlength(text)
    WORD_CACHE[key] = (base, ox, oy, adv)
    return WORD_CACHE[key]


def render_kinetic_subtitle(t, st0, st1, lines):
    dur = max(0.2, st1 - st0)
    prog = (t - st0) / dur
    total_chunks = sum(len(ln) for ln in lines)
    active_float = prog * total_chunks

    space_w = 19.0
    gold_pad = 5.0
    line_h = 60
    canvas_w, canvas_h = 1440, len(lines) * line_h + 68
    layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    max_static_w = 0.0
    chunk_idx = 0
    for li, ln in enumerate(lines):
        measured = []
        cur_x = 0.0
        for ci, (txt, is_gold) in enumerate(ln):
            if ci > 0:
                cur_x += space_w + (gold_pad if (is_gold or ln[ci - 1][1]) else 0.0)
            dist = active_float - (chunk_idx + 0.35)
            is_act = -0.35 <= dist <= 0.65
            mode = ("active_gold" if is_act else "gold") if is_gold else ("active_white" if is_act else "white")
            spr, ox, oy, static_adv = render_word_sprite(txt, mode, is_gold_font=is_gold)

            pop_s, dy_w = 1.0, 0.0
            if -0.30 <= dist <= 0.55:
                bell = max(0.0, math.cos((dist - 0.125) / 0.425 * math.pi * 0.5))
                pop_s = 1.0 + (0.065 if is_gold else 0.035) * bell
                dy_w = -5.0 * bell
            elif dist < -0.30:
                dy_w = 3.0 * min(1.0, (-0.30 - dist))

            measured.append((cur_x, spr, ox, oy, static_adv, pop_s, dy_w, is_gold))
            cur_x += static_adv
            chunk_idx += 1

        max_static_w = max(max_static_w, cur_x)
        start_x = (canvas_w - cur_x) / 2.0
        base_y = 34 + li * line_h
        for rel_x, spr, ox, oy, static_adv, pop_s, dy_w, is_gold in measured:
            draw_im = spr
            dx = int(round(start_x + rel_x - ox))
            dy = int(round(base_y - oy + dy_w + (0 if is_gold else 2)))
            if abs(pop_s - 1.0) > 0.006:
                sw = max(1, int(round(spr.width * pop_s)))
                sh = max(1, int(round(spr.height * pop_s)))
                draw_im = spr.resize((sw, sh), Image.Resampling.BICUBIC)
                dx -= (sw - spr.width) // 2
                dy -= (sh - spr.height) // 2
            layer.alpha_composite(draw_im, (max(0, dx), max(0, dy)))

    if max_static_w + 24.0 > 720.0:
        sc = 720.0 / (max_static_w + 24.0)
        layer = layer.resize((int(round(canvas_w * sc)), int(round(canvas_h * sc))), Image.Resampling.LANCZOS)

    cx_l = layer.width // 2
    hk = min(cx_l, 520)
    layer = layer.crop((cx_l - hk, 0, cx_l + hk, layer.height))

    u_in = min(1.0, max(0.0, (t - st0) / 0.16))
    u_out = min(1.0, max(0.0, (st1 - t) / 0.14))
    ease = 1.0 - (1.0 - min(u_in, u_out)) ** 3
    if ease < 0.99:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda a: int(a * ease)))
    return layer, int(round((1.0 - ease) * 16))


def render_endcard_v5(t, shot_t0):
    dt = t - shot_t0
    dur = max(1.0, tot_end - shot_t0)
    f_hero = get_reader(CLIPS_V5 / "br_basket_flower_bow.mp4", ss=0.4, dur=dur).get_frame(dt, dur)
    bg = f_hero.resize((270, 480), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.Resampling.BILINEAR).convert("RGBA")
    bg.alpha_composite(Image.new("RGBA", (W, H), (14, 48, 22, 182)))

    ease = quintic(min(1.0, dt / 0.38))
    lg = F20_LOGO.resize((152, 152), Image.Resampling.LANCZOS)
    bg.alpha_composite(lg, (540 - 76, int(round(175 + (1.0 - ease) * 24))))

    pw, ph = 460, 575
    hcrop = f_hero.crop((170, 380, 910, 1480)).resize((pw, ph), Image.Resampling.BICUBIC).convert("RGBA")
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, fill=255)
    card = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    card.paste(hcrop, (0, 0), mask)
    ImageDraw.Draw(card).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, outline=(255, 224, 108, 245), width=3)
    bg.alpha_composite(card, (540 - pw // 2, int(round(355 + (1.0 - ease) * 28))))

    d = ImageDraw.Draw(bg)
    for txt_s, fnt_s, col_s, yy_s in [
        ("THỰC PHẨM F20 × SKA NEST", F_END_BIG, (255, 228, 102, 255), 965),
        ("SET QUÀ TẶNG TRI ÂN 20/11", F_END_MED, (255, 255, 255, 250), 1026),
    ]:
        bb = d.textbbox((0, 0), txt_s, font=fnt_s)
        d.text((540 - (bb[2] - bb[0]) // 2, yy_s), txt_s, font=fnt_s, fill=col_s, stroke_width=2, stroke_fill=(8, 24, 12, 220))

    d.rounded_rectangle([175, 1095, 905, 1325], radius=24, fill=(12, 68, 30, 232), outline=(255, 222, 108, 215), width=2)
    for txt_c, col_c, fnt_c, yy_c in [
        ("Hotline/Zalo: 0979 512 289 • 0706 001 626", (255, 234, 118, 255), F_END_MED, 1118),
        ("CS1: 149 Trần Nhật Duật, TP. Nha Trang", (236, 255, 236, 255), F_END_SM, 1176),
        ("CS2: 17/3 Điện Biên Phủ, Vĩnh Hoà, Nha Trang", (236, 255, 236, 250), F_END_SM, 1218),
        ("Website: thucphamf20.com", (182, 248, 148, 255), F_END_SM, 1260),
    ]:
        bc = d.textbbox((0, 0), txt_c, font=fnt_c)
        d.text((540 - (bc[2] - bc[0]) // 2, yy_c), txt_c, font=fnt_c, fill=col_c)

    return bg.convert("RGB")


def render_frame_v5(fi):
    t = fi / FPS
    shot = SHOTS[-1]
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            shot = s
            break

    dur_s = shot["t1"] - shot["t0"]
    if shot["src"] == "COMPOSITE_SKANEST_HERO":
        base = render_composite_skanest_hero(t, shot["t0"], dur_s)
    elif shot["src"] == "OFFICIAL_ENDCARD_V5":
        base = render_endcard_v5(t, shot["t0"])
    else:
        base = get_reader(shot["src"], ss=shot["ss"], dur=dur_s, warm_match=shot.get("warm_match", False)).get_frame(t - shot["t0"], dur_s, is_live=shot["live"])

    canvas = base.convert("RGBA")

    # 1. Opening 5-Stop Gold Gradient Hook Title over 3-Shot Product Pan (0.15 - 3.72s)!
    if 0.15 <= t <= 3.72:
        vis = min(1.0, (t - 0.15) / 0.25, (3.72 - t) / 0.25)
        if vis > 0.02:
            ease = quintic(vis)
            s_top = get_pill_sprite("THỰC PHẨM F20  ×  YẾN SÀO SKA NEST", (14, 68, 32, 238), (255, 224, 114), small=False)
            s_big, _, _, _ = render_word_sprite("SET QUÀ TRI ÂN 20/11", "active_gold", is_gold_font=True, custom_font=F_HOOK_BIG)
            dy = int(round((1.0 - ease) * 20))
            for sp, yy in [(s_top, 1268 + dy), (s_big, 1336 + dy)]:
                im_s = sp if ease >= 0.99 else sp.copy()
                if ease < 0.99:
                    im_s.putalpha(im_s.getchannel("A").point(lambda a: int(a * ease)))
                canvas.alpha_composite(im_s, (540 - im_s.width // 2, yy))

    # 2. Animated Floating PIP Overlays ("lâu lâu cho nhảy lớp phủ lên trên chị Oanh chứ")
    for ov in FLOATING_OVERLAYS:
        if ov["t0"] <= t <= ov["t1"]:
            draw_floating_overlay_card(canvas, ov, t)

    # 3. 3D Champagne-Gold Circular Magnifying Glass Loupe ("KÍNH LÚP CÁI QUAI"!)
    draw_handle_magnifying_loupe(canvas, t)

    # 4. Authentic Packaged Ingredient Callout Pills (55.85 - 60.15s)
    for p_t0, p_t1, p_txt, p_bg, p_bd, px, py in INGREDIENT_PILLS:
        if p_t0 <= t <= p_t1:
            u_in = min(1.0, (t - p_t0) / 0.26)
            u_out = min(1.0, (p_t1 - t) / 0.22)
            vis = quintic(min(u_in * 1.2, u_out))
            ps = get_pill_sprite(p_txt, p_bg, p_bd, small=True)
            if vis < 0.99:
                ps = ps.copy()
                ps.putalpha(ps.getchannel("A").point(lambda a: int(a * vis)))
            canvas.alpha_composite(ps, (px - ps.width // 2, py - ps.height // 2 + int(round((1.0 - quintic(u_in)) * 18))))

    # 5. Box-Free Centered Animated Kinetic Subtitles (cy = 1405, x = 180..900)!
    for st0, st1, lines in SUBTITLES:
        if st0 <= t <= st1:
            sub_im, y_gl = render_kinetic_subtitle(t, st0, st1, lines)
            canvas.alpha_composite(sub_im, (540 - sub_im.width // 2, 1405 - sub_im.height // 2 + y_gl))
            break

    return canvas.convert("RGB")


# ==============================================================================
# 7. CHEERFUL UPBEAT UKULELE BGM + DEDUPLICATED OVERLAY/SCENE SFX MIX (-14 LUFS)
# ==============================================================================
def decode_stereo(path, dur_limit=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if dur_limit:
        cmd += ["-t", f"{dur_limit:.4f}"]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def build_v5_sfx_events():
    cands = [
        (0.08,         "magic_reveal", 0.28),
        (1.30,         "whoosh_soft",  0.18),
        (2.60,         "whoosh_soft",  0.18),
        (b01_s,        "whoosh_tvc",   0.22),
        (b01_s + 3.80, "pop_clean",    0.24),   # Overlay 1 in
        (b01_e - 0.35, "whoosh_soft",  0.16),   # Overlay 1 out
        (b02_s,        "whoosh_tvc",   0.20),
        (b02_s + 2.75, "shutter",      0.20),
        (b02_s + 6.55, "whoosh_soft",  0.18),
        (b03_s,        "whoosh_tvc",   0.20),
        (b03_s + 6.35, "magic_reveal", 0.22),
        (b04_s,        "chime_warm",   0.22),
        (b05_s + 0.95, "pop_clean",    0.24),   # Overlay 2 in
        (b06_s,        "shine_accent", 0.24),
        (48.20,        "magic_reveal", 0.24),
        (54.05,        "pop_clean",    0.24),   # Overlay 3 in
        (55.85,        "ping_glass",   0.20),
        (58.15,        "pop_soft",     0.18),
        (60.25,        "whoosh_tvc",   0.20),
        (63.48,        "pop_clean",    0.20),
        (68.05,        "whoosh_tvc",   0.20),
        (72.76,        "whoosh_soft",  0.20),
        (77.22,        "pop_clean",    0.20),
        (b07a_s + 0.25,"shine_accent", 0.24),   # Overlay 4 in
        (b07b_s + 1.50,"pop_clean",    0.24),   # Overlay 5 in
        (b08_s,        "magic_reveal", 0.22),
        (b09a_s,       "whoosh_tvc",   0.20),
        (b09b_s + 0.55,"ping_glass",   0.26),   # Magnifying Glass Loupe IN!
        (b09b_e - 0.22,"whoosh_soft",  0.18),   # Magnifying Glass Loupe OUT!
        (b09c_s + 2.65,"chime_warm",   0.20),
        (b10a_s + 1.05,"pop_clean",    0.24),   # Overlay 6 in
        (b11a_s + 1.20,"pop_clean",    0.24),   # Overlay 7 in
        (b11c_e,       "magic_reveal", 0.28),   # End-Card
    ]
    clean = []
    last_t, last_k = -10.0, ""
    for ts, k, v in sorted(cands):
        if ts - last_t >= 1.85 and k != last_k:
            clean.append((ts, k, v))
            last_t, last_k = ts, k
    return clean

def mix_master_v5(total_dur):
    n_tot = int(round(total_dur * SR))
    voice = decode_stereo(V5 / "01_Voice_V5_Master.wav", total_dur)
    if len(voice) < n_tot:
        voice = np.vstack([voice, np.zeros((n_tot - len(voice), 2), dtype=np.float32)])
    voice = voice[:n_tot]

    # Cheerful Upbeat Ukulele from TLH folder with EQ Voice Pocket (-3.5dB @ 2.2kHz so speech cuts through cleanly!)
    uku_eq = V5 / "_uku_pocket.wav"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-t", f"{total_dur:.4f}", "-i", str(V5 / "02_BGM_Upbeat_Ukulele_Full.mp3"),
        "-af", "highpass=f=75,equalizer=f=2200:t=q:w=1.2:g=-3.8",
        "-ar", str(SR), "-ac", "2", str(uku_eq)
    ], check=True)
    bgm = decode_stereo(uku_eq, total_dur)[:n_tot]
    uku_eq.unlink(missing_ok=True)
    if len(bgm) < n_tot:
        bgm = np.vstack([bgm, np.zeros((n_tot - len(bgm), 2), dtype=np.float32)])

    fi_b, fo_b = int(0.45 * SR), int(1.80 * SR)
    bgm[:fi_b] *= np.linspace(0.0, 1.0, fi_b, dtype=np.float32)[:, None]
    bgm[-fo_b:] *= np.linspace(1.0, 0.0, fo_b, dtype=np.float32)[:, None]

    # Smooth sidechain ducking: 0.42 on Intro & End-Card, 0.17 under Chi Oanh's voice!
    win = int(0.05 * SR)
    n_w = n_tot // win
    v_rms = np.sqrt(np.mean(voice[:n_w * win].reshape(n_w, win, 2) ** 2, axis=(1, 2)))
    sp_mask = (v_rms > 0.010).astype(np.float32)
    duck = np.convolve(np.clip(np.convolve(sp_mask, np.ones(14, dtype=np.float32) / 14.0, mode="same") * 1.85, 0.0, 1.0), np.ones(10, dtype=np.float32) / 10.0, mode="same")
    gain_s = np.interp(np.linspace(0, n_w - 1, n_tot), np.arange(n_w), 0.42 * (1.0 - duck) + 0.17 * duck).astype(np.float32)[:, None]

    # Load clean studio SFX bank from both SFX_TH (talking-head studio sfx) and SFX_DIR
    sfx_bank = {}
    for folder in [SFX_DIR, SFX_TH]:
        if folder.exists():
            for f in folder.glob("*.mp3"):
                a = decode_stereo(f)
                pk = float(np.max(np.abs(a))) if len(a) else 1.0
                key = f.stem.replace("sfx_", "")
                sfx_bank[key] = a / max(1e-4, pk)
                sfx_bank[f.stem] = a / max(1e-4, pk)

    sfx_ev = build_v5_sfx_events()
    sfx_bus = np.zeros((n_tot, 2), dtype=np.float32)
    for ts, key, vol in sfx_ev:
        sp = sfx_bank[key] if key in sfx_bank else sfx_bank.get("pop_tvc")
        if sp is not None:
            i0 = int(round(ts * SR))
            if 0 <= i0 < n_tot:
                i1 = min(n_tot, i0 + len(sp))
                sfx_bus[i0:i1] += sp[:i1 - i0] * float(vol)
    print(f"Mixed Upbeat Ukulele BGM + {len(sfx_ev)} clean overlay/scene SFX accents!", flush=True)

    mix = voice * 1.28 + bgm * gain_s + np.clip(sfx_bus, -0.45, 0.45)
    pre_w = V5 / "_v5_pre.wav"
    with wave.open(str(pre_w), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(mix * 0.78, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())

    m4a = V5 / "03_Master_V5_14LUFS.m4a"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(pre_w),
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=10.0",
        "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k", str(m4a)
    ], check=True)
    pre_w.unlink(missing_ok=True)
    eb = subprocess.run(["ffmpeg", "-nostats", "-i", str(m4a), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    lsum = [ln.strip() for ln in eb.stderr.splitlines() if "I:" in ln and "LUFS" in ln][-1]
    print("V5 Integrated Loudness:", lsum, flush=True)
    return m4a


# ==============================================================================
# 8. CLEAN SOURCE-ONLY CAPCUT DRAFT ("còn capcut thì chỉ cần source gốc thôi không cần thêm chữ nhạc gì vào hết")
# ==============================================================================
def uid(): return str(uuid.uuid4()).upper()
def us(sec): return int(round(float(sec) * 30.0) * 1_000_000 // 30)
def probe_dur_s(p):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def build_clean_capcut_v5():
    stage_dir = V5 / DRAFT_NAME
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    vid_sub, aud_sub = stage_dir / "video", stage_dir / "audio"
    vid_sub.mkdir(parents=True, exist_ok=True)
    aud_sub.mkdir(parents=True, exist_ok=True)

    # Render Composite SKA NEST clean source clip so CapCut Track 0 has zero gaps!
    ska_comp_mp4 = CLIPS_V5 / "clean_skanest_showcase.mp4"
    if not ska_comp_mp4.exists():
        nf = int(round((53.80 - 48.20) * FPS))
        p = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", str(ska_comp_mp4)
        ], stdin=subprocess.PIPE)
        for i in range(nf):
            fr = get_reader(CLIPS_V5 / "real_skanest_round_box.mp4", ss=0.0, dur=5.6).get_frame(i / FPS, 5.6)
            p.stdin.write(fr.tobytes())
        p.stdin.close(); p.wait()

    orig_dc = json.loads((BAK_DIR / "draft_content.json.orig").read_text(encoding="utf-8"))
    vtrack_tpl = copy.deepcopy(orig_dc["tracks"][0])
    vseg_tpl   = copy.deepcopy(orig_dc["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(orig_dc["materials"]["videos"][0])
    atrack_tpl = copy.deepcopy(orig_dc["tracks"][1])
    aseg_tpl   = copy.deepcopy(orig_dc["tracks"][1]["segments"][0])
    amat_tpl   = copy.deepcopy(orig_dc["materials"]["audios"][0])

    extra_keys   = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in orig_dc["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in extra_keys}
    a_extra_keys = tuple(k for k in extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in orig_dc["materials"].get(k, [])))
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in orig_dc["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys}

    tot_us = us(TL_V5["voice_end"])
    draft_id = uid()
    D = copy.deepcopy(orig_dc)
    D.update({
        "id": draft_id, "name": DRAFT_NAME, "fps": 30.0, "duration": tot_us,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in orig_dc["materials"]}
    })
    for k in ("texts", "common_mask", "transitions", "material_animations", "audio_fades", "videos", "audios"):
        D["materials"].setdefault(k, [])

    vmat_cache = {}
    def add_vid(src_path):
        ap = os.path.abspath(str(src_path))
        fn = os.path.basename(ap)
        if ap in vmat_cache:
            return vmat_cache[ap]
        dst_p = vid_sub / fn
        if not dst_p.exists():
            shutil.copy2(ap, dst_p)
        dur_u = us(probe_dur_s(dst_p))
        vm = copy.deepcopy(vmat_tpl)
        mid = uid()
        vm.update({
            "id": mid, "local_material_id": str(uuid.uuid4()), "type": "video",
            "path": f"{PLACEHOLDER}/video/{fn}", "material_name": fn,
            "width": 1080, "height": 1920, "duration": dur_u, "has_audio": True
        })
        D["materials"]["videos"].append(vm)
        vmat_cache[ap] = (mid, dur_u)
        return mid, dur_u

    # Track 0: Clean Color-Harmonized & Centered Video Sources ONLY (Zero text, Zero music, Zero SFX!)
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    for s in SHOTS:
        if s["src"] == "OFFICIAL_ENDCARD_V5":
            continue
        sp = ska_comp_mp4 if s["src"] == "COMPOSITE_SKANEST_HERO" else s["src"]
        mid, mdur = add_vid(sp)
        du = us(s["t1"] - s["t0"])
        ss_u = us(s["ss"])
        spd = 1.0
        src_du = du
        if not s["live"] and (mdur - ss_u) < du:
            ss_u = 0
            spd = max(0.55, round((mdur / float(du)) * 0.97, 3))
            src_du = min(mdur, int(round(du * spd)))

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k in extra_keys:
            em = copy.deepcopy(v_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = float(spd)
            D["materials"][k].append(em); refs.append(em["id"])

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": ss_u, "duration": src_du},
            "target_timerange": {"start": us(s["t0"]), "duration": du},
            "speed": float(spd), "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": 0
        })
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["alpha"] = 1.0
        tr_v0["segments"].append(seg)
    D["tracks"].append(tr_v0)

    # Track 1: Clean Stumble-Free Synced Voiceover Segments ONLY!
    tr_vo = copy.deepcopy(atrack_tpl); tr_vo["id"] = uid(); tr_vo["segments"] = []
    for blk in TL_V5["blocks"]:
        ap = os.path.abspath(blk["wav_path"])
        fn = os.path.basename(ap)
        dst_a = aud_sub / fn
        if not dst_a.exists():
            shutil.copy2(ap, dst_a)
        adur = us(probe_dur_s(dst_a))
        du = min(adur, us(blk["dur"]))

        am = copy.deepcopy(amat_tpl)
        aid = uid()
        am.update({"id": aid, "local_material_id": str(uuid.uuid4()), "type": "sound", "name": blk["id"], "path": f"{PLACEHOLDER}/audio/{fn}", "duration": adur})
        D["materials"]["audios"].append(am)

        aseg = copy.deepcopy(aseg_tpl)
        refs = []
        for k in a_extra_keys:
            em = copy.deepcopy(a_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        fid = uid()
        D["materials"]["audio_fades"].append({"id": fid, "type": "audio_fade", "fade_in_duration": 25000, "fade_out_duration": 40000, "fade_type": 0})
        refs.append(fid)
        aseg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": 0, "duration": du},
            "target_timerange": {"start": us(blk["start"]), "duration": du},
            "speed": 1.0, "volume": 1.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []
        })
        tr_vo["segments"].append(aseg)
    D["tracks"].append(tr_vo)

    dc_json = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    for fn in ("draft_content.json", "draft_info.json", "template.tmp", "template-2.tmp"):
        (stage_dir / fn).write_text(dc_json, encoding="utf-8")

    # Cover thumbnail
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.0", "-i", str(CLIPS_V5 / "br_basket_flower_bow.mp4"), "-frames:v", "1", str(stage_dir / "draft_cover.jpg")], check=True)
    donor_dir = DRAFTS_DIR / "1117"
    dmi = json.loads((donor_dir / "draft_meta_info.json").read_text(encoding="utf-8"))
    now_us = int(time.time() * 1_000_000)
    cap_dst = DRAFTS_DIR / DRAFT_NAME

    dmi.update({
        "draft_id": draft_id, "draft_name": DRAFT_NAME,
        "draft_fold_path": str(cap_dst).replace("\\", "/"),
        "draft_root_path": str(DRAFTS_DIR), "draft_cover": "draft_cover.jpg",
        "tm_duration": tot_us, "tm_draft_create": now_us, "tm_draft_modified": now_us,
        "draft_materials": [{"type": t, "value": []} for t in (0, 1, 2, 3, 6, 7, 8)]
    })
    (stage_dir / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for aux in ("draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json"):
        sp = donor_dir / aux
        if sp.exists():
            shutil.copy2(sp, stage_dir / aux)

    for dst_folder in [
        str(cap_dst),
        rf"Z:\Máy tính khác\My Computer\Document HT Media\TLH\{DRAFT_NAME}",
        rf"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011\{DRAFT_NAME}",
    ]:
        if os.path.exists(dst_folder):
            shutil.rmtree(dst_folder)
        os.makedirs(os.path.dirname(dst_folder), exist_ok=True)
        shutil.copytree(stage_dir, dst_folder)
        print("  -> Deployed Clean Source-Only CapCut Draft:", dst_folder, flush=True)

    rmi_path = DRAFTS_DIR / "root_meta_info.json"
    if rmi_path.exists():
        rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
        stores = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_NAME]
        entry = copy.deepcopy(stores[0]) if stores else {}
        entry.update({
            "draft_cloud_last_action_download": False,
            "draft_cover": f"{cap_dst}/draft_cover.jpg".replace("\\", "/"),
            "draft_fold_path": str(cap_dst).replace("\\", "/"),
            "draft_id": draft_id, "draft_is_invisible": False,
            "draft_json_file": f"{cap_dst}/draft_content.json".replace("\\", "/"),
            "draft_name": DRAFT_NAME, "draft_root_path": str(DRAFTS_DIR),
            "tm_draft_create": now_us, "tm_draft_modified": now_us + 1000, "tm_duration": tot_us,
        })
        rmi["all_draft_store"] = [entry] + stores
        rmi_path.write_text(json.dumps(rmi, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"Registered {DRAFT_NAME} at #1 in CapCut Desktop!", flush=True)


if __name__ == "__main__":
    total_frames = int(TL_V5["total_frames"])
    total_dur    = float(TL_V5["total_dur"])

    if "--test" in sys.argv:
        test_ts = [
            0.8,           # Intro shot 1: sunlit gift sets pan (NO Chi Oanh yet!)
            2.0,           # Intro shot 2: long table 104 gift sets pan
            9.5,           # Live centered Chi Oanh (b01) + Floating Gift Basket Overlay 1!
            17.5,          # Harmonized Anh Hau 77 sets handover
            30.8,          # Fix Image 1: Wide Chi Oanh amidst 104 sets (ZERO camera lens!)
            36.2,          # Live Wide Chi Oanh standing with open arms amidst 104 sets!
            41.2,          # Live centered Chi Oanh (b05) + Floating Inside-Basket Overlay 2!
            50.8,          # Fix Image 2: Steady 1.00x Real Packaged SKA NEST Box Showcase!
            59.2,          # Fix Image 3 & 4: Real Inside-Basket + SKA NEST 4-compartment Overlay + 4 Ingredient Pills!
            62.0,          # Equal-height twin F20 seaweed jars
            85.5,          # Fix Image 5: Shelf pan + Centered Real SKA NEST Showcase (NO fake red velvet box!)
            93.5,          # Live centered Chi Oanh holding booklet + Floating Booklet Close-Up Overlay 5!
            110.2,         # Fix Image 5/6/7: Centered Chi Oanh + 3D Circular Magnifying Glass Loupe ("KÍNH LÚP CÁI QUAI")!
            114.0,         # Fix Image 6: Un-zoomed full gift basket naturally showing crimson flower accent!
            117.0,         # Fix Image 9: Un-zoomed full gift basket naturally showing beige organza bow!
            total_dur-1.4, # Festive F20 x SKA NEST End-Card!
        ]
        grid = Image.new("RGB", (270 * 4, 480 * 4))
        for i, ts in enumerate(test_ts):
            fr = render_frame_v5(int(round(ts * FPS)))
            th = fr.resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(th)
            d.line([(135, 0), (135, 480)], fill=(0, 255, 110), width=1)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(255, 230, 0))
            grid.paste(th, ((i % 4) * 270, (i // 4) * 480))
        grid.save(V5 / "v5_test_grid_16.jpg", quality=93)
        print("Saved v5_test_grid_16.jpg!")
    else:
        vid_only = V5 / "_v5_video_only.mp4"
        if "--mux-only" not in sys.argv or not vid_only.exists():
            proc = subprocess.Popen([
                "ffmpeg", "-y", "-v", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", str(vid_only)
            ], stdin=subprocess.PIPE)
            for fi in range(total_frames):
                fr = render_frame_v5(fi)
                proc.stdin.write(fr.tobytes())
                if fi % 300 == 0 or fi == total_frames - 1:
                    print(f"Rendered {fi+1}/{total_frames} frames ({(fi+1)/total_frames*100:.1f}%)", flush=True)
            proc.stdin.close()
            rc = proc.wait()
            if rc != 0:
                raise RuntimeError(f"FFmpeg encode failed: {rc}")
        else:
            print("Reusing completed 4,300-frame _v5_video_only.mp4!", flush=True)

        m4a = mix_master_v5(total_dur)
        final_local = V5 / "F20_SET_QUA_2011_V5_FINAL.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", str(vid_only), "-i", str(m4a),
            "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", str(final_local)
        ], check=True)

        for dp in [
            r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\F20_SET_QUA_2011_FINAL.mp4",
            r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\f20-set-qua-2011_FINAL.mp4",
            r"D:\XUẤT CAPCUT\F20_SET_QUA_2011_FINAL.mp4",
        ]:
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(final_local, dp)
            print("  -> Exported V5 Master MP4 to:", dp, flush=True)

        build_clean_capcut_v5()

        qc_ts = [0.8, 2.0, 9.5, 17.5, 21.5, 28.0, 30.8, 36.2, 41.2, 45.8, 50.8, 59.2, 62.0, 70.2, 79.5, 85.5, 93.5, 110.2, 114.0, total_dur-1.4]
        sheet = Image.new("RGB", (270 * 5, 480 * 4))
        tmp = V5 / "_tmp_qcf.jpg"
        for i, ts in enumerate(qc_ts):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(final_local), "-frames:v", "1", str(tmp)], check=True)
            im = Image.open(tmp).resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(255, 230, 0))
            sheet.paste(im, ((i % 5) * 270, (i // 5) * 480))
        tmp.unlink(missing_ok=True)
        qc_path = V5 / "qc_v5_final_20frames.jpg"
        sheet.save(qc_path, quality=93)

        arch = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011")
        arch.mkdir(parents=True, exist_ok=True)
        for sf in [qc_path, V5 / "v5_color_and_centering_qc.jpg", V5 / "timeline_v5_master.json", V5 / "v5_step1_build_clean_voice_and_harmonized_clips.py", V5 / "v5_step2_render_master_and_capcut.py"]:
            if sf.exists():
                shutil.copy2(sf, arch / sf.name)
        print("ALL V5 DELIVERABLES COMPLETED!", flush=True)
