import copy, json, math, os, shutil, subprocess, sys, time, uuid, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT        = Path(r"d:\AI\full studio\output\f20-set-qua-2011")
V5         = OUT / "v5_master"
VOICE_V5   = V5 / "voice_v5"
V6         = OUT / "v6_master"
CLIPS_V6   = V6 / "clips_v6"
V3_DIR     = OUT / "v3_pro"
SFX_DIR    = OUT / "v2_1117" / "sfx_v2"
SFX_TH     = Path(r"d:\AI\full studio\phong-cach\talking-head\assets_dung_chung\sfx")
BAK_DIR    = OUT / "capcut_backup"
DRAFTS_DIR = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
FONT_DIR   = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")

W, H, FPS, SR = 1080, 1920, 30, 48000
DRAFT_SOURCE_ONLY = "F20_SetQua_2011_SourceOnly"
DRAFT_WITH_VOICE  = "F20_SetQua_2011_V6_Edit"
PLACEHOLDER = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"

F_SUB_REG  = ImageFont.truetype(str(FONT_DIR / "Montserrat-ExtraBold.ttf"), 40)
F_SUB_HL   = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 43)
F_HOOK_BIG = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 52)
F_PILL     = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 24)
F_PILL_SM  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 20)
F_END_BIG  = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 42)
F_END_MED  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 27)
F_END_SM   = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-SemiBold.ttf"), 22)

F20_LOGO = Image.open(V3_DIR / "refs_clean" / "f20_logo_official.png").convert("RGBA")

TL_V5 = json.loads((V5 / "timeline_v5_master.json").read_text(encoding="utf-8"))
BMAP  = {b["id"]: b for b in TL_V5["blocks"]}
def bt(bid): return float(BMAP[bid]["start"]), float(BMAP[bid]["end"])

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

# Exact 0.000s lip-sync timestamp for b06_24thanh_real_live (C3852 36.24..41.36s = last 5.12s of b06!)
t_24thanh_s = round(b06_e - 5.12, 4)

# ==============================================================================
# 1. DEFINITIVE V6 SHOT SCHEDULE (Fixes Image 1, 2, 3, 4 + WB Anti-Glare Vibrant!)
# ==============================================================================
SHOTS = [
    # 0.00 - 3.90s: 3-Shot Crisp Product Pan Intro
    {"t0": 0.00,   "t1": 1.30,   "src": CLIPS_V6 / "br_intro1_sunlit_sets.mp4", "ss": 0.0, "live": False},
    {"t0": 1.30,   "t1": 2.60,   "src": CLIPS_V6 / "br_intro2_long_table.mp4",  "ss": 0.0, "live": False},
    {"t0": 2.60,   "t1": b01_s,  "src": CLIPS_V6 / "br_intro3_shelf_tower.mp4", "ss": 0.0, "live": False},

    # b01_open_live: Live Centered Chi Oanh + Floating Gift Basket Overlay
    {"t0": b01_s,  "t1": b01_e,  "src": CLIPS_V6 / "b01_open_live.mp4",         "ss": 0.0, "live": True},

    # b02_nhatrang_real: Anh Hau 77 sets + Phu Huynh 13 sets
    {"t0": b02_s,        "t1": b02_s + 2.75, "src": CLIPS_V6 / "br_anh_hau_handover.mp4", "ss": 0.0, "live": False},
    {"t0": b02_s + 2.75, "t1": b02_s + 6.55, "src": CLIPS_V6 / "br_anh_hau_77sets.mp4",   "ss": 0.0, "live": False},
    {"t0": b02_s + 6.55, "t1": b02_e,        "src": CLIPS_V6 / "br_phu_huynh_13sets.mp4", "ss": 0.0, "live": False},

    # b03_ship_104_clean: Ha Noi 10 + TP.HCM 04 + Wide Chi Oanh Amidst 104 Sets
    {"t0": b03_s,        "t1": b03_s + 3.25, "src": CLIPS_V6 / "br_hanoi_carton.mp4",      "ss": 0.0, "live": False},
    {"t0": b03_s + 3.25, "t1": b03_s + 6.35, "src": CLIPS_V6 / "br_hcmc_suv.mp4",          "ss": 0.0, "live": False},
    {"t0": b03_s + 6.35, "t1": b03_s + 8.65, "src": CLIPS_V6 / "br_wide_oanh_row_104.mp4", "ss": 0.0, "live": False},
    {"t0": b03_s + 8.65, "t1": b03_e,        "src": CLIPS_V6 / "br_clean_row_104sets.mp4", "ss": 0.0, "live": False},

    # b04_wide_oanh_104_live & b05_intro_set_live
    {"t0": b04_s,  "t1": b04_e,  "src": CLIPS_V6 / "b04_wide_oanh_104_live.mp4","ss": 0.0, "live": True},
    {"t0": b05_s,  "t1": b05_e,  "src": CLIPS_V6 / "b05_intro_set_live.mp4",    "ss": 0.0, "live": True},

    # b06_4items_real_tight:
    # - Full basket (43.93 - 48.10s)
    # - FIX IMAGE 1: Full-bleed luxury SKA NEST round box (48.10 - 50.45s) + Full-bleed pure white To Yen Tinh Che (50.45 - 53.65s)!
    # - FIX IMAGE 2: Clean inside-basket (53.65 - 56.90s, zero ceiling glare!) + Full-bleed SKA NEST 4-compartment box (56.90 - 60.25s, zero cut-off inset!)
    # - Twin F20 Seaweed Jars -> Say Gion -> Say Me -> Banh Thuyen -> Kep Hat Pouch
    # - FIX IMAGE 3: Real Live Sony C3852 Chi Oanh holding gift basket & pointing to 22-24 bars + Real F20 Bars PIP!
    {"t0": b06_s,       "t1": 48.10,       "src": CLIPS_V6 / "br_basket_full_hero.mp4",    "ss": 0.0, "live": False},
    {"t0": 48.10,       "t1": 50.45,       "src": CLIPS_V6 / "prod_skanest_box_full.mp4",  "ss": 0.0, "live": False},
    {"t0": 50.45,       "t1": 53.65,       "src": CLIPS_V6 / "prod_to_yen_dedicated1.mp4", "ss": 0.0, "live": False},
    {"t0": 53.65,       "t1": 56.90,       "src": CLIPS_V6 / "br_inside_basket_clean.mp4", "ss": 0.0, "live": False},
    {"t0": 56.90,       "t1": 60.25,       "src": CLIPS_V6 / "prod_skanest_box_alt.mp4",   "ss": 0.0, "live": False},
    {"t0": 60.25,       "t1": 63.48,       "src": CLIPS_V6 / "prod_two_jars_even.mp4",     "ss": 0.0, "live": False},
    {"t0": 63.48,       "t1": 65.76,       "src": CLIPS_V6 / "prod_hu_say_gion.mp4",       "ss": 0.0, "live": False},
    {"t0": 65.76,       "t1": 68.05,       "src": CLIPS_V6 / "prod_hu_say_me.mp4",         "ss": 0.0, "live": False},
    {"t0": 68.05,       "t1": 72.76,       "src": CLIPS_V6 / "prod_banh_thuyen.mp4",       "ss": 0.0, "live": False},
    {"t0": 72.76,       "t1": t_24thanh_s, "src": CLIPS_V6 / "prod_kep_hat_pouch.mp4",     "ss": 0.0, "live": False},
    {"t0": t_24thanh_s, "t1": b06_e,       "src": CLIPS_V6 / "b06_24thanh_real_live.mp4",  "ss": 0.0, "live": True},

    # FIX IMAGE 4 (b07a_yen_giatri_real: 82.23 - 88.97s): Dedicated Full-Screen To Yen Tinh Che Soi Dai Sources ONLY!
    {"t0": b07a_s,        "t1": b07a_s + 3.45, "src": CLIPS_V6 / "prod_to_yen_soi_dai2.mp4",  "ss": 0.0, "live": False},
    {"t0": b07a_s + 3.45, "t1": b07a_e,        "src": CLIPS_V6 / "prod_skanest_box_full.mp4", "ss": 1.4, "live": False},

    # b07b_camnang_live + b08_chungyen_clean
    {"t0": b07b_s, "t1": b07b_e, "src": CLIPS_V6 / "b07b_camnang_live.mp4",     "ss": 0.0, "live": True},
    {"t0": b08_s,  "t1": b08_e,  "src": CLIPS_V6 / "prod_chung_yen.mp4",        "ss": 0.0, "live": False},

    # b09a_giomica_real + b09b_quai_da_live (Magnifying Loupe!) + b09c_hoa_no_real (1.00x Un-Zoomed!)
    {"t0": b09a_s, "t1": b09a_e, "src": CLIPS_V6 / "br_basket_full_hero.mp4",   "ss": 1.5, "live": False},
    {"t0": b09b_s, "t1": b09b_e, "src": CLIPS_V6 / "b09b_quai_da_live.mp4",     "ss": 0.0, "live": True},
    {"t0": b09c_s,        "t1": b09c_s + 2.65, "src": CLIPS_V6 / "br_basket_flower_bow.mp4", "ss": 0.0, "live": False},
    {"t0": b09c_s + 2.65, "t1": b09c_e,        "src": CLIPS_V6 / "br_basket_row_bow.mp4",    "ss": 0.0, "live": False},

    # b10a_sx_live + b10b_sx_yentam_real + b11 CTA + End-Card
    {"t0": b10a_s, "t1": b10a_e, "src": CLIPS_V6 / "b10a_sx_live.mp4",          "ss": 0.0, "live": True},
    {"t0": b10b_s, "t1": b10b_e, "src": CLIPS_V6 / "br_factory_pack1.mp4",      "ss": 0.0, "live": False},
    {"t0": b11a_s, "t1": b11a_e, "src": CLIPS_V6 / "b11a_cta_live1.mp4",        "ss": 0.0, "live": True},
    {"t0": b11b_s, "t1": b11b_e, "src": CLIPS_V6 / "br_wide_oanh_arms_104.mp4", "ss": 0.2, "live": False},
    {"t0": b11c_s, "t1": b11c_e, "src": CLIPS_V6 / "b11c_cta_inbox_live.mp4",   "ss": 0.0, "live": True},
    {"t0": b11c_e, "t1": tot_end,"src": "OFFICIAL_ENDCARD_V6",                  "ss": 0.0, "live": False},
]

# Smooth Face-Safe Floating Overlays on Live Chi Oanh Shots!
FLOATING_OVERLAYS = [
    {"t0": b01_s + 3.80, "t1": b01_e - 0.35, "src": CLIPS_V6 / "br_basket_flower_bow.mp4", "ss": 0.2,
     "cx": 228, "cy": 415, "pw": 290, "ph": 372, "crop": (160, 420, 920, 1520), "from_dir": -1, "label": "QUÀ BIẾU 20/11"},

    {"t0": b05_s + 0.95, "t1": b05_e - 0.30, "src": CLIPS_V6 / "br_inside_basket_clean.mp4", "ss": 0.2,
     "cx": 228, "cy": 415, "pw": 290, "ph": 372, "crop": (120, 320, 960, 1460), "from_dir": -1, "label": "04 MÓN TRONG SET"},

    # On b06_24thanh_real_live (Image 3): Real F20 Sandwiched Seaweed Bars PIP springs in beside Chi Oanh!
    {"t0": t_24thanh_s + 0.45, "t1": b06_e - 0.25, "src": CLIPS_V6 / "prod_kep_hat_real_bars.mp4", "ss": 0.2,
     "cx": 228, "cy": 418, "pw": 292, "ph": 376, "crop": (90, 220, 990, 1480), "from_dir": -1, "label": "22 – 24 THANH HẠT"},

    {"t0": b07b_s + 1.40, "t1": b07b_e - 0.35, "src": CLIPS_V6 / "prod_chung_yen.mp4", "ss": 0.2,
     "cx": 228, "cy": 420, "pw": 288, "ph": 360, "crop": (160, 420, 920, 1460), "from_dir": -1, "label": "CẨM NANG & CÔNG DỤNG"},

    {"t0": b10a_s + 1.05, "t1": b10a_e - 0.28, "src": CLIPS_V6 / "br_factory_pack1.mp4", "ss": 0.3,
     "cx": 838, "cy": 415, "pw": 288, "ph": 368, "crop": (160, 360, 920, 1460), "from_dir": +1, "label": "F20 TRỰC TIẾP SX"},

    {"t0": b11a_s + 1.20, "t1": b11a_e - 0.28, "src": CLIPS_V6 / "br_basket_full_hero.mp4", "ss": 0.5,
     "cx": 228, "cy": 418, "pw": 288, "ph": 370, "crop": (180, 460, 900, 1520), "from_dir": -1, "label": "ĐẶT SỈ & LẺ 20/11"},
]

INGREDIENT_PILLS = [
    (55.75, 60.15, "01 • TÁO ĐỎ",              (158, 22, 42, 238), (255, 224, 132), 285, 555),
    (56.75, 60.15, "02 • ĐÔNG TRÙNG HẠ THẢO",  (138, 74, 14, 238), (255, 232, 148), 755, 555),
    (58.10, 60.15, "03 • KỶ TỬ",               (168, 36, 24, 238), (255, 224, 132), 285, 1280),
    (58.90, 60.15, "04 • 01 HỘP ĐƯỜNG PHÈN",   ( 18, 78, 44, 238), (168, 245, 192), 755, 1280),
]

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

    (b06_s + 0.10, 48.05,  [[("Một", False), ("SET QUÀ TẶNG", True), ("như thế này", False)],
                            [("bên trong sẽ gồm có:", False)]]),
    (48.12,        50.38,  [[("Đầu tiên là", False)],
                            [("01 SET YẾN SÀO", True)]]),
    (50.45,        53.60,  [[("gồm", False), ("01 TỔ YẾN TINH CHẾ", True)],
                            [("sợi dài • dòng", False), ("TIÊU CHUẨN", True)]]),
    (53.70,        55.72,  [[("kèm theo đầy đủ", False)],
                            [("NGUYÊN LIỆU CHƯNG", True)]]),
    (55.78,        58.08,  [[("gồm có:", False), ("TÁO ĐỎ", True)],
                            [("và", False), ("ĐÔNG TRÙNG HẠ THẢO", True)]]),
    (58.15,        60.15,  [[("cùng", False), ("KỶ TỬ", True)],
                            [("và", False), ("01 HỘP ĐƯỜNG PHÈN", True)]]),

    (60.30,        63.40,  [[("Thứ 2 là", False), ("02 HỘP RONG BIỂN", True)],
                            [("sấy giòn", False), ("TUỆ TÂM", True)]]),
    (63.50,        65.70,  [[("01 hộp", False), ("RONG BIỂN SẤY GIÒN", True)],
                            [("vị", False), ("CAY NHẸ", True)]]),
    (65.80,        67.98,  [[("và 01 hộp", False), ("RONG BIỂN SẤY MÈ", True)],
                            [("vị", False), ("KHÔNG CAY", True)]]),

    (68.08,        72.68,  [[("Thứ 3 là 01 gói", False), ("BÁNH THUYỀN", True)],
                            [("mix hạt dinh dưỡng", False), ("250G", True)]]),
    (72.80,    t_24thanh_s-0.06, [[("Thứ 4 là 01 gói", False)],
                                  [("RONG BIỂN KẸP HẠT 500G", True)]]),
    (t_24thanh_s+0.06, b06_e-0.08, [[("bên trong có", False), ("22 – 24 THANH", True)],
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
# 2. VIDEO SLICE READER & OVERLAY / LOUPE / SUBTITLE ENGINES
# ==============================================================================
class SliceReader:
    def __init__(self, mp4_path, ss=0.0, max_dur=12.0):
        self.path = str(mp4_path)
        self.ss = float(ss)
        self.max_dur = float(max_dur)
        self.frames = None

    def load(self):
        if self.frames is not None:
            return
        cmd = ["ffmpeg", "-v", "error"]
        if self.ss > 0.04:
            cmd += ["-ss", f"{self.ss:.3f}"]
        cmd += ["-t", f"{self.max_dur + 0.5:.3f}", "-i", self.path, "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        raw = proc.stdout.read()
        proc.wait()
        n = len(raw) // (W * H * 3)
        self.frames = np.frombuffer(raw[:n * W * H * 3], dtype=np.uint8).reshape((n, H, W, 3))

    def get_frame(self, local_t, needed_dur, is_live=False):
        self.load()
        n = len(self.frames)
        if n == 0:
            return Image.new("RGB", (W, H), (18, 48, 26))
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

READERS, READER_ORDER = {}, []
def get_reader(p, ss=0.0, dur=6.0):
    k = (str(p), round(float(ss), 2), round(float(dur), 2))
    if k not in READERS:
        if len(READER_ORDER) >= 4:
            READERS.pop(READER_ORDER.pop(0), None)
        READERS[k] = SliceReader(p, ss=ss, max_dur=dur)
        READER_ORDER.append(k)
    return READERS[k]

def ease_out_back(u):
    u = max(0.0, min(1.0, u))
    c1 = 1.45
    return 1.0 + (c1 + 1.0) * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2)

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

    arr = np.array(cropped, dtype=np.float32)
    sheen_p = -0.3 + 1.6 * ((dt % 2.8) / 2.8)
    yy, xx = np.ogrid[0:ph, 0:pw]
    diag = (xx * 0.8 + yy * 0.45) / max(1.0, pw * 0.8 + ph * 0.45)
    sh_v = np.exp(-((diag - sheen_p) ** 2) / 0.008) * 26.0
    arr = np.clip(arr + sh_v[:, :, None], 0, 245).astype(np.uint8)

    pad = 18
    cw, ch = pw + pad * 2, ph + pad * 2 + 26
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    rad = 28
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
    if ov.get("label"):
        pil = get_pill_sprite(ov["label"], (14, 68, 32, 242), (255, 222, 112), small=True)
        card.alpha_composite(pil, (cw // 2 - pil.width // 2, pad + ph - pil.height // 2 - 2))

    if abs(sc_anim - 1.0) > 0.006:
        card = card.resize((max(4, int(round(cw * sc_anim))), max(4, int(round(ch * sc_anim)))), Image.Resampling.BICUBIC)
    if alpha_u < 0.99:
        card.putalpha(card.getchannel("A").point(lambda a: int(a * alpha_u)))

    slide_dx = int(round(ov["from_dir"] * (1.0 - quintic(u_in)) * 68))
    canvas.alpha_composite(card, (ov["cx"] - card.width // 2 + slide_dx, ov["cy"] - card.height // 2))


def draw_handle_magnifying_loupe(canvas, t):
    t0, t1 = b09b_s + 0.55, b09b_e - 0.18
    if not (t0 <= t <= t1):
        return
    dt, rem, dur = t - t0, t1 - t, t1 - t0
    u_in, u_out = min(1.0, max(0.0, dt / 0.36)), min(1.0, max(0.0, rem / 0.26))
    vis = quintic(min(u_in * 1.2, u_out))
    sc_l = ease_out_back(u_in) if rem > 0.26 else (0.75 + 0.25 * quintic(u_out))

    tx, ty = 392, 668
    lx, ly, diam = 238, 402, 312
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    line_prog = quintic(min(1.0, dt / 0.25))
    r_dot = int(round(16 * (1.0 + 0.14 * math.sin(dt * 6.5))))
    od.ellipse([tx - r_dot - 6, ty - r_dot - 6, tx + r_dot + 6, ty + r_dot + 6], outline=(255, 226, 108, int(155 * vis)), width=2)
    od.ellipse([tx - 8, ty - 8, tx + 8, ty + 8], fill=(255, 232, 118, int(250 * vis)), outline=(140, 18, 32, int(255 * vis)), width=2)
    ex = int(round(tx + (lx + 75 - tx) * line_prog))
    ey = int(round(ty + (ly + 115 - ty) * line_prog))
    od.line([(tx, ty), (ex, ey)], fill=(255, 228, 112, int(235 * vis)), width=4)

    fr_m = get_reader(CLIPS_V6 / "prod_quai_loupe.mp4", ss=0.0, dur=dur).get_frame(dt, dur, is_live=False)
    lens_crop = fr_m.crop((130, 660, 910, 1440)).resize((diam, diam), Image.Resampling.BICUBIC)

    pad = 42
    sw, sh_s = diam + pad * 2, diam + pad * 2 + 24
    sp = Image.new("RGBA", (sw, sh_s), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sp)
    cx_s, cy_s = sw // 2, pad + diam // 2
    ang = math.radians(48)
    hx0, hy0 = cx_s + int(math.cos(ang) * (diam // 2 - 4)), cy_s + int(math.sin(ang) * (diam // 2 - 4))
    hx1, hy1 = cx_s + int(math.cos(ang) * (diam // 2 + 46)), cy_s + int(math.sin(ang) * (diam // 2 + 46))
    sd.line([(hx0 + 3, hy0 + 5), (hx1 + 3, hy1 + 5)], fill=(0, 0, 0, 140), width=22)
    sd.line([(hx0, hy0), (hx1, hy1)], fill=(138, 22, 36, 255), width=20)
    sd.line([(hx0, hy0), (hx1, hy1)], fill=(255, 222, 114, 240), width=6)

    shadow = Image.new("RGBA", (sw, sh_s), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([pad, pad + 8, pad + diam, pad + 8 + diam], fill=(0, 0, 0, 165))
    sp.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8.0)))

    cmask = Image.new("L", (diam, diam), 0)
    ImageDraw.Draw(cmask).ellipse([0, 0, diam - 1, diam - 1], fill=255)
    lens_rgba = Image.new("RGBA", (sw, sh_s), (0, 0, 0, 0))
    lens_rgba.paste(lens_crop, (pad, pad), mask=cmask)
    gl = Image.new("RGBA", (diam, diam), (0, 0, 0, 0))
    ImageDraw.Draw(gl).arc([16, 16, diam - 16, diam - 16], start=198, end=262, fill=(255, 255, 255, 130), width=10)
    lens_rgba.alpha_composite(gl.filter(ImageFilter.GaussianBlur(1.5)), (pad, pad))
    sp.alpha_composite(lens_rgba)

    sd = ImageDraw.Draw(sp)
    sd.ellipse([pad - 4, pad - 4, pad + diam + 3, pad + diam + 3], outline=(168, 108, 22, 255), width=9)
    sd.ellipse([pad - 2, pad - 2, pad + diam + 1, pad + diam + 1], outline=(255, 232, 128, 255), width=5)

    tag = get_pill_sprite("QUAI DA ĐỎ ĐÔ", (138, 18, 36, 245), (255, 226, 118), small=True)
    sp.alpha_composite(tag, (cx_s - tag.width // 2, pad + diam - tag.height // 2 + 4))

    if abs(sc_l - 1.0) > 0.006:
        sp = sp.resize((max(8, int(round(sw * sc_l))), max(8, int(round(sh_s * sc_l)))), Image.Resampling.BICUBIC)
    if vis < 0.99:
        sp.putalpha(sp.getchannel("A").point(lambda a: int(a * vis)))

    overlay.alpha_composite(sp, (lx - sp.width // 2, ly - sp.height // 2))
    canvas.alpha_composite(overlay)


WORD_CACHE = {}
def render_word_sprite(text, style_mode, is_gold_font=False, custom_font=None):
    key = (text, style_mode, is_gold_font, id(custom_font) if custom_font else 0)
    if key in WORD_CACHE:
        return WORD_CACHE[key]
    fnt = custom_font if custom_font else (F_SUB_HL if is_gold_font else F_SUB_REG)
    sw_px = 4 if custom_font == F_HOOK_BIG else 3
    bb = ImageDraw.Draw(Image.new("RGBA", (8, 8))).textbbox((0, 0), text, font=fnt, stroke_width=sw_px)
    pad = 12
    tw, th = (bb[2] - bb[0]) + pad * 2, (bb[3] - bb[1]) + pad * 2
    ox, oy = -bb[0] + pad, -bb[1] + pad

    base = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    glow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((ox, oy + 3), text, font=fnt, fill=(0, 0, 0, 185), stroke_width=sw_px + 3, stroke_fill=(0, 0, 0, 175))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4.2)))
    ImageDraw.Draw(base).text((ox, oy), text, font=fnt, fill=(18, 22, 16, 255), stroke_width=sw_px, stroke_fill=(12, 18, 12, 248))

    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).text((ox, oy), text, font=fnt, fill=255)
    if style_mode in ("white", "active_white"):
        fi = Image.new("RGBA", (tw, th), (255, 255, 255, 255) if style_mode == "white" else (255, 250, 218, 255))
        fi.putalpha(mask)
        base.alpha_composite(fi)
    else:
        grad = np.zeros((th, tw, 4), dtype=np.uint8)
        ys = np.linspace(0.0, 1.0, th)
        stops_x = [0.0, 0.26, 0.52, 0.78, 1.0]
        stops_c = [(255, 254, 232), (255, 232, 108), (242, 172, 22), (255, 238, 152), (218, 132, 12)] if style_mode == "active_gold" else [(255, 249, 205), (255, 216, 68), (232, 154, 16), (255, 228, 128), (198, 118, 10)]
        for c in range(3):
            grad[:, :, c] = np.clip(np.interp(ys, stops_x, [s[c] for s in stops_c]), 0, 255).astype(np.uint8)[:, None]
        grad[:, :, 3] = np.array(mask)
        base.alpha_composite(Image.fromarray(grad, "RGBA"))

    WORD_CACHE[key] = (base, ox, oy, fnt.getlength(text))
    return WORD_CACHE[key]


def render_kinetic_subtitle(t, st0, st1, lines):
    dur = max(0.2, st1 - st0)
    active_float = ((t - st0) / dur) * sum(len(ln) for ln in lines)
    space_w, gold_pad, line_h = 19.0, 5.0, 60
    canvas_w, canvas_h = 1440, len(lines) * line_h + 68
    layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    max_static_w, chunk_idx = 0.0, 0
    for li, ln in enumerate(lines):
        measured, cur_x = [], 0.0
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
            dx, dy = int(round(start_x + rel_x - ox)), int(round(base_y - oy + dy_w + (0 if is_gold else 2)))
            if abs(pop_s - 1.0) > 0.006:
                sw, sh = max(1, int(round(spr.width * pop_s))), max(1, int(round(spr.height * pop_s)))
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

    u_in, u_out = min(1.0, max(0.0, (t - st0) / 0.16)), min(1.0, max(0.0, (st1 - t) / 0.14))
    ease = 1.0 - (1.0 - min(u_in, u_out)) ** 3
    if ease < 0.99:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda a: int(a * ease)))
    return layer, int(round((1.0 - ease) * 16))


def render_endcard_v6(t, shot_t0):
    dt = t - shot_t0
    dur = max(1.0, tot_end - shot_t0)
    f_hero = get_reader(CLIPS_V6 / "br_basket_flower_bow.mp4", ss=0.4, dur=dur).get_frame(dt, dur)
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


def render_frame_v6(fi):
    t = fi / FPS
    shot = SHOTS[-1]
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            shot = s
            break

    dur_s = shot["t1"] - shot["t0"]
    if shot["src"] == "OFFICIAL_ENDCARD_V6":
        base = render_endcard_v6(t, shot["t0"])
    else:
        base = get_reader(shot["src"], ss=shot["ss"], dur=dur_s).get_frame(t - shot["t0"], dur_s, is_live=shot["live"])

    canvas = base.convert("RGBA")

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

    for ov in FLOATING_OVERLAYS:
        if ov["t0"] <= t <= ov["t1"]:
            draw_floating_overlay_card(canvas, ov, t)

    draw_handle_magnifying_loupe(canvas, t)

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

    for st0, st1, lines in SUBTITLES:
        if st0 <= t <= st1:
            sub_im, y_gl = render_kinetic_subtitle(t, st0, st1, lines)
            canvas.alpha_composite(sub_im, (540 - sub_im.width // 2, 1405 - sub_im.height // 2 + y_gl))
            break

    return canvas.convert("RGB")


# ==============================================================================
# 3. BUILD TWO CAPCUT DRAFTS:
#    (A) F20_SetQua_2011_SourceOnly -> 1 SINGLE VIDEO TRACK ONLY ("chỉ toàn source thôi", audio baked right into the source MP4s!)
#    (B) F20_SetQua_2011_V6_Edit    -> Clean Video Track + Voice Track + Ukulele BGM Track
# ==============================================================================
def uid(): return str(uuid.uuid4()).upper()
def us(sec): return int(round(float(sec) * 30.0) * 1_000_000 // 30)
def probe_dur_s(p):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def build_two_capcut_drafts():
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

    vo_master_wav = V5 / "01_Voice_V5_Master.wav"
    tot_us = us(TL_V5["voice_end"])

    # --- DRAFT A: F20_SetQua_2011_SourceOnly (100% PURE SINGLE VIDEO SOURCE TRACK ONLY!) ---
    stage_a = V6 / DRAFT_SOURCE_ONLY
    if stage_a.exists():
        shutil.rmtree(stage_a)
    vid_a = stage_a / "video"
    vid_a.mkdir(parents=True, exist_ok=True)

    id_a = uid()
    Da = copy.deepcopy(orig_dc)
    Da.update({
        "id": id_a, "name": DRAFT_SOURCE_ONLY, "fps": 30.0, "duration": tot_us,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in orig_dc["materials"]}
    })

    tr_a0 = copy.deepcopy(vtrack_tpl); tr_a0["id"] = uid(); tr_a0["segments"] = []
    shot_idx = 0
    for s in SHOTS:
        if s["src"] == "OFFICIAL_ENDCARD_V6":
            continue
        shot_idx += 1
        t0, t1 = float(s["t0"]), float(s["t1"])
        dur_s  = t1 - t0
        fn_out = f"src_{shot_idx:02d}_{Path(s['src']).stem}.mp4"
        dst_mp4 = vid_a / fn_out

        # Slice exact WB-calibrated video + mux exact synced voice slice right into the source MP4 so 1 single track has picture + synced voice!
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{float(s['ss']):.4f}", "-t", f"{dur_s:.4f}", "-i", str(s["src"]),
            "-ss", f"{t0:.4f}", "-t", f"{dur_s:.4f}", "-i", str(vo_master_wav),
            "-map", "0:v:0", "-map", "1:a:0",
            "-vf", "tpad=stop_mode=clone:stop_duration=2.0,fps=30,format=yuv420p",
            "-af", f"afade=t=in:st=0:d=0.02,afade=t=out:st={max(0.01, dur_s-0.03):.4f}:d=0.03",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-c:a", "aac", "-b:a", "192k", "-shortest", str(dst_mp4)
        ], check=True)

        du = us(dur_s)
        mid = uid()
        vm = copy.deepcopy(vmat_tpl)
        vm.update({
            "id": mid, "local_material_id": str(uuid.uuid4()), "type": "video",
            "path": f"{PLACEHOLDER}/video/{fn_out}", "material_name": fn_out,
            "width": 1080, "height": 1920, "duration": du, "has_audio": True
        })
        Da["materials"]["videos"].append(vm)

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k in extra_keys:
            em = copy.deepcopy(v_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            Da["materials"][k].append(em); refs.append(em["id"])
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": 0, "duration": du},
            "target_timerange": {"start": us(t0), "duration": du},
            "speed": 1.0, "volume": 1.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": 0
        })
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["alpha"] = 1.0
        tr_a0["segments"].append(seg)
    Da["tracks"].append(tr_a0)

    # --- DRAFT B: F20_SetQua_2011_V6_Edit (Separate Video + Voice + Upbeat Ukulele BGM Tracks) ---
    stage_b = V6 / DRAFT_WITH_VOICE
    if stage_b.exists():
        shutil.rmtree(stage_b)
    shutil.copytree(stage_a, stage_b)
    aud_b = stage_b / "audio"
    aud_b.mkdir(parents=True, exist_ok=True)
    id_b = uid()
    Db = copy.deepcopy(Da)
    Db["id"] = id_b
    Db["name"] = DRAFT_WITH_VOICE
    for seg in Db["tracks"][0]["segments"]:
        seg["volume"] = 0.0

    # Add Voice + Upbeat Ukulele BGM tracks to Draft B
    tr_vo = copy.deepcopy(atrack_tpl); tr_vo["id"] = uid(); tr_vo["segments"] = []
    for blk in TL_V5["blocks"]:
        ap = Path(blk["wav_path"])
        shutil.copy2(ap, aud_b / ap.name)
        adur = us(probe_dur_s(aud_b / ap.name))
        du = min(adur, us(blk["dur"]))
        aid = uid()
        am = copy.deepcopy(amat_tpl)
        am.update({"id": aid, "local_material_id": str(uuid.uuid4()), "type": "sound", "name": blk["id"], "path": f"{PLACEHOLDER}/audio/{ap.name}", "duration": adur})
        Db["materials"]["audios"].append(am)
        aseg = copy.deepcopy(aseg_tpl)
        refs = []
        for k in a_extra_keys:
            em = copy.deepcopy(a_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            Db["materials"][k].append(em); refs.append(em["id"])
        aseg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": 0, "duration": du},
            "target_timerange": {"start": us(blk["start"]), "duration": du},
            "speed": 1.0, "volume": 1.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []
        })
        tr_vo["segments"].append(aseg)
    Db["tracks"].append(tr_vo)

    bgm_src = V5 / "02_BGM_Upbeat_Ukulele_Full.mp3"
    shutil.copy2(bgm_src, aud_b / bgm_src.name)
    bdur = us(probe_dur_s(aud_b / bgm_src.name))
    b_aid = uid()
    bam = copy.deepcopy(amat_tpl)
    bam.update({"id": b_aid, "local_material_id": str(uuid.uuid4()), "type": "music", "name": "Upbeat Ukulele", "path": f"{PLACEHOLDER}/audio/{bgm_src.name}", "duration": bdur})
    Db["materials"]["audios"].append(bam)
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = []
    bseg = copy.deepcopy(aseg_tpl)
    brefs = []
    for k in a_extra_keys:
        em = copy.deepcopy(a_extra_tpl[k]); em["id"] = uid()
        if k == "speeds": em["speed"] = 1.0
        Db["materials"][k].append(em); brefs.append(em["id"])
    bseg.update({
        "id": uid(), "material_id": b_aid,
        "source_timerange": {"start": 0, "duration": tot_us},
        "target_timerange": {"start": 0, "duration": tot_us},
        "speed": 1.0, "volume": 0.24, "last_nonzero_volume": 0.24,
        "extra_material_refs": brefs, "common_keyframes": [], "keyframe_refs": []
    })
    tr_bgm["segments"].append(bseg)
    Db["tracks"].append(tr_bgm)

    donor_dir = DRAFTS_DIR / "1117"
    rmi_path = DRAFTS_DIR / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8")) if rmi_path.exists() else {"all_draft_store": []}
    stores = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") not in (DRAFT_SOURCE_ONLY, DRAFT_WITH_VOICE)]
    new_entries = []

    for stg, d_obj, d_name, d_id in [(stage_a, Da, DRAFT_SOURCE_ONLY, id_a), (stage_b, Db, DRAFT_WITH_VOICE, id_b)]:
        dc_s = json.dumps(d_obj, ensure_ascii=False, separators=(",", ":"))
        for fn in ("draft_content.json", "draft_info.json", "template.tmp", "template-2.tmp"):
            (stg / fn).write_text(dc_s, encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.0", "-i", str(CLIPS_V6 / "br_basket_flower_bow.mp4"), "-frames:v", "1", str(stg / "draft_cover.jpg")], check=True)
        dmi = json.loads((donor_dir / "draft_meta_info.json").read_text(encoding="utf-8"))
        now_us = int(time.time() * 1_000_000)
        cap_dst = DRAFTS_DIR / d_name
        dmi.update({
            "draft_id": d_id, "draft_name": d_name,
            "draft_fold_path": str(cap_dst).replace("\\", "/"),
            "draft_root_path": str(DRAFTS_DIR), "draft_cover": "draft_cover.jpg",
            "tm_duration": tot_us, "tm_draft_create": now_us, "tm_draft_modified": now_us,
            "draft_materials": [{"type": t, "value": []} for t in (0, 1, 2, 3, 6, 7, 8)]
        })
        (stg / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        for aux in ("draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json"):
            if (donor_dir / aux).exists():
                shutil.copy2(donor_dir / aux, stg / aux)

        for dst_f in [
            str(cap_dst),
            rf"Z:\Máy tính khác\My Computer\Document HT Media\TLH\{d_name}",
            rf"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011\{d_name}",
        ]:
            if os.path.exists(dst_f):
                shutil.rmtree(dst_f)
            os.makedirs(os.path.dirname(dst_f), exist_ok=True)
            shutil.copytree(stg, dst_f)
            print("  -> Deployed CapCut Draft:", dst_f, flush=True)

        ent = copy.deepcopy(stores[0]) if stores else {}
        ent.update({
            "draft_cloud_last_action_download": False,
            "draft_cover": f"{cap_dst}/draft_cover.jpg".replace("\\", "/"),
            "draft_fold_path": str(cap_dst).replace("\\", "/"),
            "draft_id": d_id, "draft_is_invisible": False,
            "draft_json_file": f"{cap_dst}/draft_content.json".replace("\\", "/"),
            "draft_name": d_name, "draft_root_path": str(DRAFTS_DIR),
            "tm_draft_create": now_us, "tm_draft_modified": now_us + 2000, "tm_duration": tot_us,
        })
        new_entries.append(ent)

    rmi["all_draft_store"] = new_entries + stores
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Registered BOTH {DRAFT_SOURCE_ONLY} (#1) and {DRAFT_WITH_VOICE} (#2) in CapCut Desktop!", flush=True)


if __name__ == "__main__":
    total_frames = int(TL_V5["total_frames"])
    total_dur    = float(TL_V5["total_dur"])

    if "--test" in sys.argv:
        # Specifically test the 4 fixed images + WB anti-glare vibrant across Showroom & Classroom!
        test_ts = [
            0.8,           # Intro sunlit sets (WB anti-glare check!)
            2.0,           # Intro long table (WB anti-glare check!)
            9.5,           # Showroom Chi Oanh + Overlay 1 (neutral WB + rosy skin!)
            17.5,          # Classroom Anh Hau 77 sets (neutral white shirt!)
            49.2,          # FIX IMAGE 1a: Full-bleed SKA NEST round box!
            52.0,          # FIX IMAGE 1b: Full-bleed pure white To Yen Tinh Che!
            55.2,          # FIX IMAGE 2a: Inside basket (0% ceiling glare!)
            59.0,          # FIX IMAGE 2b: Full-bleed SKA NEST 4-compartment + 4 Ingredient Pills!
            62.0,          # Twin F20 seaweed jars
            79.5,          # FIX IMAGE 3: Real Live C3852 Chi Oanh + Real F20 Sandwiched Bars Overlay!
            84.0,          # FIX IMAGE 4a: Dedicated full-screen To Yen Tinh Che Soi Dai!
            87.2,          # FIX IMAGE 4b: Dedicated SKA NEST Bird's Nest round box!
            93.5,          # Live Chi Oanh booklet + Overlay
            110.2,         # Live Chi Oanh + 3D Gold Magnifying Loupe ("Kính lúp cái quai")!
            114.0,         # Un-zoomed full gift basket (flower + vibrant color, zero glare!)
            117.0,         # Un-zoomed gift baskets row (beige bows + zero table glare!)
        ]
        grid = Image.new("RGB", (270 * 4, 480 * 4))
        for i, ts in enumerate(test_ts):
            fr = render_frame_v6(int(round(ts * FPS)))
            th = fr.resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(th)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(255, 230, 0))
            grid.paste(th, ((i % 4) * 270, (i // 4) * 480))
        grid.save(V6 / "v6_test_grid_16.jpg", quality=93)
        print("Saved v6_test_grid_16.jpg!")
    else:
        vid_only = V6 / "_v6_video_only.mp4"
        proc = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", str(vid_only)
        ], stdin=subprocess.PIPE)
        for fi in range(total_frames):
            fr = render_frame_v6(fi)
            proc.stdin.write(fr.tobytes())
            if fi % 300 == 0 or fi == total_frames - 1:
                print(f"Rendered {fi+1}/{total_frames} frames ({(fi+1)/total_frames*100:.1f}%)", flush=True)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("FFmpeg encode failed")

        # Reuse -13.9 LUFS Master Audio from V5 (identical frame-locked timeline!)
        m4a = V5 / "03_Master_V5_14LUFS.m4a"
        final_local = V6 / "F20_SET_QUA_2011_V6_FINAL.mp4"
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
            print("  -> Exported V6 Master MP4 to:", dp, flush=True)

        build_two_capcut_drafts()

        qc_ts = [0.8, 2.0, 9.5, 17.5, 30.8, 36.2, 41.2, 45.8, 49.2, 52.0, 55.2, 59.0, 62.0, 70.2, 79.5, 84.0, 93.5, 110.2, 114.0, total_dur-1.4]
        sheet = Image.new("RGB", (270 * 5, 480 * 4))
        tmp = V6 / "_tmp_qcf.jpg"
        for i, ts in enumerate(qc_ts):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(final_local), "-frames:v", "1", str(tmp)], check=True)
            im = Image.open(tmp).resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(255, 230, 0))
            sheet.paste(im, ((i % 5) * 270, (i // 5) * 480))
        tmp.unlink(missing_ok=True)
        qc_path = V6 / "qc_v6_final_20frames.jpg"
        sheet.save(qc_path, quality=93)

        arch = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011")
        for sf in [qc_path, V6 / "v6_wb_and_4fixes_qc.jpg", V6 / "v6_step1_regrade_all_clips_wb_antiglare.py", V6 / "v6_step2_render_master_and_two_capcut_drafts.py"]:
            if sf.exists():
                shutil.copy2(sf, arch / sf.name)
        print("ALL V6 DELIVERABLES COMPLETED!", flush=True)
