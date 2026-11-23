import copy, json, math, os, shutil, subprocess, sys, time, uuid, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

V4_DIR     = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v4_clean_master")
V3_DIR     = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v3_pro")
V2_DIR     = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117")
OUT_ROOT   = Path(r"d:\AI\full studio\output\f20-set-qua-2011")
AROLL_V4   = V4_DIR / "aroll_v4"
BROLL_V3   = V3_DIR / "brolls_v3"
VID_V3     = V3_DIR / "videos_v3"
VID_V4     = V4_DIR / "videos_v4"
SFX_DIR    = V2_DIR / "sfx_v2"
BAK_DIR    = OUT_ROOT / "capcut_backup"
DRAFTS_DIR = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
FONT_DIR   = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")

W, H, FPS, SR = 1080, 1920, 30, 48000
DRAFT_NAME  = "F20_SetQua_2011_V4_Clean"
PLACEHOLDER = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"

# Clean Agency Kinetic Fonts (NO ugly rectangular caption boxes!)
F_SUB_REG  = ImageFont.truetype(str(FONT_DIR / "Montserrat-ExtraBold.ttf"), 40)
F_SUB_HL   = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 44)
F_HOOK_TOP = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 25)
F_HOOK_BIG = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 48)
F_END_BIG  = ImageFont.truetype(str(FONT_DIR / "Montserrat-Black.ttf"), 42)
F_END_MED  = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 27)
F_END_SM   = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-SemiBold.ttf"), 22)

F20_LOGO = Image.open(V3_DIR / "refs_clean" / "f20_logo_official.png").convert("RGBA")

# ==============================================================================
# 1. COMPLETE BALANCED SHOT SCHEDULE (Zero Dizzy Zoom, Zero Repeated Clips,
#    100% Frame-Locked Lip-Sync on Every Live Chi Oanh Shot!)
# ==============================================================================
SHOTS = [
    # Panoramic real gift-set intro (0.00 - 2.60s): Shot 1 = wide sets, Shot 2 = Wide Chi Oanh behind all 104 gift sets!
    {"t0": 0.00,    "t1": 1.25,    "src": BROLL_V3 / "intro_01_gimbal_sets.mp4",  "ss": 0.00, "live": False},
    {"t0": 1.25,    "t1": 2.60,    "src": AROLL_V4 / "b00_wide_oanh_104sets.mp4", "ss": 0.00, "live": False},

    # b01_open_live (2.60 - 22.5333s): Live Chi Oanh behind 104 gift sets (2.60-11.78s) + Nha Trang B-rolls!
    {"t0": 2.60,    "t1": 11.78,   "src": AROLL_V4 / "b01_open_live.mp4",         "ss": 0.00, "live": True},
    {"t0": 11.78,   "t1": 14.20,   "src": BROLL_V3 / "real_anh_hau_handover.mp4", "ss": 0.20, "live": False},
    {"t0": 14.20,   "t1": 18.28,   "src": VID_V3   / "V3_vid15_anh_hau.mp4",      "ss": 0.00, "live": False},
    {"t0": 18.28,   "t1": 22.5333, "src": BROLL_V3 / "real_13sets_team.mp4",      "ss": 0.20, "live": False},

    # b02_hanoi_tts (22.5333 - 25.70s) + b03_hcmc_tong_real (25.70 - 34.8667s)
    {"t0": 22.5333, "t1": 25.70,   "src": BROLL_V3 / "real_hanoi_carton.mp4",     "ss": 0.20, "live": False},
    {"t0": 25.70,   "t1": 29.78,   "src": BROLL_V3 / "real_hcmc_suv.mp4",         "ss": 0.20, "live": False},
    {"t0": 29.78,   "t1": 34.8667, "src": BROLL_V3 / "pov_gimbal_104_sets.mp4",   "ss": 0.00, "live": False},

    # b04_pov_real (34.8667 - 39.1667s): Continuous panoramic POV of 104 sets
    {"t0": 34.8667, "t1": 39.1667, "src": BROLL_V3 / "pov_long_104_sets.mp4",     "ss": 0.30, "live": False},

    # b05_intro_set_live (39.1667 - 44.0333s): Live Chi Oanh centered at x=540!
    {"t0": 39.1667, "t1": 44.0333, "src": AROLL_V4 / "b05_intro_set_live.mp4",    "ss": 0.00, "live": True},

    # b06_4items_real (44.0333 - 85.10s): 100% Real Chi Oanh Voice across 11 unique full-screen 9:16 product videos!
    {"t0": 44.0333, "t1": 48.15,   "src": VID_V4   / "V4_vid01_hero_giftset.mp4", "ss": 0.00, "live": False},
    {"t0": 48.15,   "t1": 50.55,   "src": VID_V3   / "V3_vid02_skanest_box.mp4",  "ss": 0.00, "live": False},
    {"t0": 50.55,   "t1": 56.55,   "src": VID_V3   / "V3_vid03_to_yen_pure.mp4",  "ss": 0.00, "live": False},
    {"t0": 56.55,   "t1": 58.75,   "src": VID_V3   / "V3_vid04_tao_do_dtht.mp4",  "ss": 0.00, "live": False},
    {"t0": 58.75,   "t1": 60.52,   "src": VID_V3   / "V3_vid05_ky_tu_duong_phen.mp4", "ss": 0.00, "live": False},
    {"t0": 60.52,   "t1": 63.86,   "src": VID_V4   / "V4_vid02_two_jars_even.mp4","ss": 0.00, "live": False},
    {"t0": 63.86,   "t1": 66.40,   "src": VID_V3   / "V3_vid06_hu_say_gion.mp4",  "ss": 0.00, "live": False},
    {"t0": 66.40,   "t1": 68.75,   "src": VID_V3   / "V3_vid07_hu_say_me.mp4",    "ss": 0.00, "live": False},
    {"t0": 68.75,   "t1": 74.85,   "src": VID_V3   / "V3_vid08_banh_thuyen.mp4",  "ss": 0.00, "live": False},
    {"t0": 74.85,   "t1": 79.95,   "src": VID_V3   / "V3_vid09_kep_hat.mp4",      "ss": 0.00, "live": False},
    {"t0": 79.95,   "t1": 85.10,   "src": VID_V4   / "V4_vid03_24_thanh_hat.mp4", "ss": 0.00, "live": False},

    # b07_camnang_live (85.10 - 102.60s): Full-screen luxury Yen box -> Live Lip-Synced Chi Oanh holding Cam Nang!
    {"t0": 85.10,   "t1": 92.20,   "src": VID_V4   / "V4_vid04_yen_gia_tri_nhat.mp4", "ss": 0.00, "live": False},
    {"t0": 92.20,   "t1": 102.60,  "src": AROLL_V4 / "b07_camnang_live.mp4",      "ss": 7.10, "live": True},

    # b08_chungyen_tts (102.60 - 105.80s): Steaming porcelain bird's nest pot!
    {"t0": 102.60,  "t1": 105.80,  "src": VID_V3   / "V3_vid10_chung_yen.mp4",    "ss": 0.00, "live": False},

    # b09_giomica_quai_live (105.80 - 125.2667s): Mica Basket (once!) -> Live Lip-Synced Chi Oanh Handle -> Real Flower Macro -> Real Beige Bow Macro!
    {"t0": 105.80,  "t1": 112.65,  "src": VID_V3   / "V3_vid13_gio_mica_real.mp4","ss": 0.00, "live": False},
    {"t0": 112.65,  "t1": 117.95,  "src": AROLL_V4 / "b09_giomica_quai_live.mp4", "ss": 6.85, "live": True},
    {"t0": 117.95,  "t1": 122.00,  "src": VID_V4   / "V4_vid05_hoa_diem_nhan.mp4","ss": 0.00, "live": False},
    {"t0": 122.00,  "t1": 125.2667,"src": VID_V3   / "V3_vid14_quai_no_macro.mp4","ss": 0.00, "live": False},

    # b10_sx_live (125.2667 - 134.2667s): Live Chi Oanh -> Factory Packing 1 & 2
    {"t0": 125.2667,"t1": 130.35,  "src": AROLL_V4 / "b10_sx_live.mp4",           "ss": 0.00, "live": True},
    {"t0": 130.35,  "t1": 132.35,  "src": BROLL_V3 / "real_factory_pack1.mp4",    "ss": 0.30, "live": False},
    {"t0": 132.35,  "t1": 134.2667,"src": BROLL_V3 / "real_factory_pack2.mp4",    "ss": 0.30, "live": False},

    # b11_cta_live (134.2667 - 148.2667s): Live Lip-Synced Chi Oanh centered at x=540 + Official End-Card (148.2667 - 150.8667s)
    {"t0": 134.2667,"t1": 148.2667,"src": AROLL_V4 / "b11_cta_live.mp4",          "ss": 0.00, "live": True},
    {"t0": 148.2667,"t1": 150.8667,"src": "OFFICIAL_ENDCARD_V4",                  "ss": 0.00, "live": False},
]


# ==============================================================================
# 2. ANIMATED KINETIC SUBTITLE CARDS (Centered x=540, Box-Free, Smooth Motion!)
#    Locked to Whisper large-v3-turbo word timestamps on 01_Voice_V4_Master.wav
# ==============================================================================
SUBTITLES = [
    (2.62,   7.35,  [[("Hôm nay bên Oanh chuẩn bị", False)],
                     [("104 SET QUÀ", True), ("cho khách đặt", False)]]),
    (7.42,   9.52,  [[("để làm", False), ("QUÀ BIẾU TẶNG", True)],
                     [("thầy cô giáo", False)]]),
    (9.56,  11.68,  [[("nhân dịp tri ân", False)],
                     [("NGÀY 20 THÁNG 11", True)]]),

    (11.82, 14.15,  [[("Ở", False), ("NHA TRANG", True)],
                     [("có 02 khách hàng:", False)]]),
    (14.20, 18.20,  [[("1 là", False), ("ANH HẬU", True)],
                     [("ĐĂNG KHOA EDU •", False), ("77 SET", True)]]),
    (18.30, 22.45,  [[("2 là nhóm", False), ("HỘI PHỤ HUYNH", True)],
                     [("đặt", False), ("13 SET QUÀ", True)]]),

    (22.56, 25.64,  [[("Khách thứ 3 ở", False), ("HÀ NỘI", True)],
                     [("đặt", False), ("10 SET QUÀ", True)]]),
    (25.74, 29.72,  [[("và một bạn ở", False), ("TP. HỒ CHÍ MINH", True)],
                     [("đặt", False), ("04 SET QUÀ", True)]]),
    (29.82, 34.78,  [[("Tổng sáng nay chuẩn bị", False)],
                     [("ĐỦ 104 SET QUÀ", True), ("nha!", False)]]),

    (34.86, 39.02,  [[("Đây là những", False), ("SET QUÀ", True)],
                     [("bên Oanh", False), ("chuẩn bị xong", True), ("ạ!", False)]]),

    (39.18, 43.92,  [[("Bây giờ Oanh giới thiệu", False)],
                     [("01 SET QUÀ", True), ("cho mọi người xem!", False)]]),

    (44.08, 48.10,  [[("Một", False), ("SET QUÀ TẶNG", True), ("như thế này", False)],
                     [("bên trong sẽ gồm có:", False)]]),
    (48.16, 50.48,  [[("Đầu tiên là", False)],
                     [("01 SET YẾN SÀO", True)]]),
    (50.56, 54.15,  [[("gồm", False), ("01 TỔ YẾN TINH CHẾ", True)],
                     [("sợi dài • dòng", False), ("TIÊU CHUẨN", True)]]),
    (54.45, 56.50,  [[("kèm theo đầy đủ", False)],
                     [("NGUYÊN LIỆU CHƯNG", True)]]),
    (56.58, 58.70,  [[("gồm có:", False), ("TÁO ĐỎ", True)],
                     [("và", False), ("ĐÔNG TRÙNG HẠ THẢO", True)]]),
    (58.76, 60.48,  [[("cùng", False), ("KỶ TỬ", True)],
                     [("và", False), ("01 HỘP ĐƯỜNG PHÈN", True)]]),

    (60.56, 63.82,  [[("Thứ 2 là", False), ("02 HỘP RONG BIỂN", True)],
                     [("sấy giòn", False), ("TUỆ TÂM", True)]]),
    (63.88, 66.36,  [[("01 hộp", False), ("RONG BIỂN SẤY GIÒN", True)],
                     [("vị", False), ("CAY NHẸ", True)]]),
    (66.44, 68.68,  [[("và 01 hộp", False), ("RONG BIỂN SẤY MÈ", True)],
                     [("vị", False), ("KHÔNG CAY", True)]]),

    (68.80, 74.76,  [[("Thứ 3 là 01 gói", False), ("BÁNH THUYỀN", True)],
                     [("mix hạt dinh dưỡng", False), ("250G", True)]]),
    (74.90, 79.90,  [[("Thứ 4 là 01 gói", False)],
                     [("RONG BIỂN KẸP HẠT 500G", True)]]),
    (80.00, 85.00,  [[("bên trong có", False), ("22 – 24 THANH", True)],
                     [("bánh hạt dinh dưỡng", True), ("nhé!", False)]]),

    (85.26, 91.95,  [[("Giá trị nhất là", False), ("TỔ YẾN TINH CHẾ", True)],
                     [("dòng tiêu chuẩn", False), ("SỢI DÀI", True)]]),
    (92.28, 98.55,  [[("kèm theo", False), ("01 TỜ CẨM NANG", True)],
                     [("sử dụng yến sào", False)]]),
    (98.78, 102.45, [[("nêu rõ", False)],
                     [("CÔNG DỤNG CỦA YẾN SÀO", True)]]),
    (102.62,105.72, [[("và hướng dẫn", False)],
                     [("CHƯNG YẾN ĐÚNG CÁCH", True)]]),

    (106.10,112.60, [[("Tất cả xếp trong", False), ("GIỎ ĐỰNG QUÀ", True)],
                     [("chất liệu", False), ("MICA TRONG SUỐT", True)]]),
    (112.72,117.88, [[("Bên trên có", False), ("QUAI XÁCH DA", True)],
                     [("MÀU ĐỎ ĐÔ", True), ("rất sang trọng!", False)]]),
    (118.00,121.94, [[("thiết kế thêm", False)],
                     [("BÔNG HOA ĐIỂM NHẤN", True)]]),
    (122.04,125.18, [[("và một chiếc", False), ("NƠ MÀU BE", True)],
                     [("rất xinh xắn như thế này!", False)]]),

    (125.28,130.30, [[("Sản phẩm trong set đều do", False)],
                     [("BÊN OANH TRỰC TIẾP SẢN XUẤT", True)]]),
    (130.40,134.16, [[("yên tâm về", False)],
                     [("CHẤT LƯỢNG & GIÁ CẢ", True), ("nhé!", False)]]),

    (134.28,139.75, [[("Cảm ơn quý anh chị tin tưởng", False)],
                     [("đặt hàng của", False), ("THỰC PHẨM F20", True)]]),
    (139.88,143.90, [[("Anh chị có nhu cầu đặt", False)],
                     [("SET QUÀ TẶNG", True)]]),
    (143.96,148.14, [[("dịp lễ", False), ("20 THÁNG 11", True)],
                     [("hãy", False), ("INBOX NGAY", True), ("cho Oanh nhé!", False)]]),
]


# ==============================================================================
# 3. CURATED, DEDUPLICATED SFX SCHEDULE (Min 2.3s cooldown, ZERO overlap!)
# ==============================================================================
def build_clean_sfx_events():
    raw_candidates = [
        (0.08,   "magic_reveal", 0.28),
        (2.58,   "whoosh_tvc",   0.22),
        (4.80,   "ting_quick",   0.20),
        (11.78,  "deep_swish",   0.22),
        (14.20,  "shutter",      0.20),
        (18.28,  "whoosh_pip",   0.20),
        (22.53,  "whoosh_tvc",   0.20),
        (25.70,  "deep_swish",   0.20),
        (29.78,  "ting_quick",   0.20),
        (34.86,  "magic_reveal", 0.25),
        (39.16,  "swoosh_soft",  0.18),
        (44.03,  "shine_accent", 0.24),
        (48.15,  "whoosh_tvc",   0.20),
        (50.55,  "star_sparkle", 0.22),
        (56.55,  "bubble_in",    0.24),
        (58.75,  "pop_soft",     0.20),
        (60.52,  "whoosh_tvc",   0.22),
        (63.86,  "pop_tvc",      0.20),
        (66.40,  "ting_quick",   0.18),
        (68.75,  "deep_swish",   0.22),
        (74.85,  "whoosh_tvc",   0.22),
        (79.95,  "pop_tvc",      0.20),
        (85.10,  "shine_accent", 0.24),
        (92.20,  "swoosh_soft",  0.18),
        (102.60, "magic_reveal", 0.24),
        (105.80, "whoosh_tvc",   0.22),
        (112.65, "swoosh_soft",  0.18),
        (117.95, "ting_quick",   0.20),
        (122.00, "star_sparkle", 0.22),
        (125.26, "swoosh_soft",  0.18),
        (130.35, "whoosh_pip",   0.20),
        (134.26, "swoosh_soft",  0.18),
        (148.26, "magic_reveal", 0.28),
    ]
    clean = []
    last_t = -10.0
    last_key = ""
    for ts, key, vol in sorted(raw_candidates):
        if ts - last_t >= 2.15 and key != last_key:
            clean.append((ts, key, vol))
            last_t = ts
            last_key = key
    return clean


# ==============================================================================
# 4. NATURAL FORWARD VIDEO READER (Slice-Only + LRU Cache < 500MB RAM, Zero Swap!)
# ==============================================================================
class ForwardClipReader:
    def __init__(self, mp4_path, ss=0.0, max_dur=15.0):
        self.path = str(mp4_path)
        self.ss = float(ss)
        self.max_dur = float(max_dur)
        self.frames = None

    def load(self):
        if self.frames is not None:
            return
        cmd = ["ffmpeg", "-v", "error"]
        if self.ss > 0.05:
            cmd += ["-ss", f"{self.ss:.3f}"]
        cmd += [
            "-t", f"{self.max_dur + 0.5:.3f}", "-i", self.path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,fps=30",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        raw = proc.stdout.read()
        proc.wait()
        n = len(raw) // (W * H * 3)
        self.frames = np.frombuffer(raw[:n * W * H * 3], dtype=np.uint8).reshape((n, H, W, 3))

    def get_frame(self, local_t, needed_dur, is_live=False):
        self.load()
        n = len(self.frames)
        if n == 0:
            return Image.new("RGB", (W, H), (12, 42, 20))
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
        blended = (self.frames[i0].astype(np.float32) * (1.0 - frac) + self.frames[i1].astype(np.float32) * frac).astype(np.uint8)
        return Image.fromarray(blended)

READERS = {}
READER_ORDER = []
def get_reader(p, ss=0.0, dur=6.0):
    k = (str(p), round(float(ss), 2), round(float(dur), 2))
    if k not in READERS:
        if len(READER_ORDER) >= 2:
            old_k = READER_ORDER.pop(0)
            READERS.pop(old_k, None)
        READERS[k] = ForwardClipReader(p, ss=ss, max_dur=dur)
        READER_ORDER.append(k)
    return READERS[k]


# ==============================================================================
# 5. KINETIC BOX-FREE TYPOGRAPHY ENGINE (Smooth Word-by-Word Pop & Glide!)
# ==============================================================================
WORD_CACHE = {}
def render_word_sprite(text, style_mode, is_gold_font=False):
    # style_mode: "white", "active_white", "gold", "active_gold"
    key = (text, style_mode, is_gold_font)
    if key in WORD_CACHE:
        return WORD_CACHE[key]

    fnt = F_SUB_HL if is_gold_font else F_SUB_REG
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dummy.textbbox((0, 0), text, font=fnt, stroke_width=3)
    pad = 10
    tw = (bb[2] - bb[0]) + pad * 2
    th = (bb[3] - bb[1]) + pad * 2
    ox, oy = -bb[0] + pad, -bb[1] + pad

    base = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    # Soft ambient drop-glow so text reads cleanly over bright white plastic WITHOUT any rectangular box!
    glow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((ox, oy + 3), text, font=fnt, fill=(0, 0, 0, 185), stroke_width=6, stroke_fill=(0, 0, 0, 175))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4.2)))

    # Crisp 2.5px dark charcoal outline
    ImageDraw.Draw(base).text((ox, oy), text, font=fnt, fill=(14, 22, 16, 255), stroke_width=3, stroke_fill=(10, 18, 12, 248))

    # Top pure fill (2-Layer Gradient for Gold, Crisp White / Warm Ivory for Regular)
    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).text((ox, oy), text, font=fnt, fill=255)

    if style_mode in ("white", "active_white"):
        col = (255, 255, 255, 255) if style_mode == "white" else (255, 250, 218, 255)
        fill_im = Image.new("RGBA", (tw, th), col)
        fill_im.putalpha(mask)
        base.alpha_composite(fill_im)
    else:
        grad = np.zeros((th, tw, 4), dtype=np.uint8)
        ys = np.linspace(0.0, 1.0, th)[:, None]
        if style_mode == "active_gold":
            c_top = np.array([255, 253, 220])
            c_mid = np.array([255, 224, 72])
            c_bot = np.array([255, 176, 18])
        else:
            c_top = np.array([255, 248, 190])
            c_mid = np.array([255, 212, 52])
            c_bot = np.array([242, 158, 12])
        rgb = np.where(ys < 0.52, c_top + (c_mid - c_top) * (ys / 0.52), c_mid + (c_bot - c_mid) * ((ys - 0.52) / 0.48))
        grad[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)[:, None, :]
        grad[:, :, 3] = np.array(mask)
        base.alpha_composite(Image.fromarray(grad, "RGBA"))

    adv = fnt.getlength(text)
    WORD_CACHE[key] = (base, ox, oy, adv)
    return WORD_CACHE[key]


def render_kinetic_subtitle(t, st0, st1, lines):
    dur = max(0.2, st1 - st0)
    prog = (t - st0) / dur  # 0.0 -> 1.0 across phrase

    # Count total chunks so active highlight sweeps smoothly word-by-word across the phrase!
    total_chunks = sum(len(ln) for ln in lines)
    active_float = prog * total_chunks

    space_w = 19.0
    gold_pad = 5.0
    line_h = 60
    canvas_w, canvas_h = 1440, len(lines) * line_h + 68
    layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    max_static_w = 0.0
    chunk_global_idx = 0
    for li, ln in enumerate(lines):
        # Measure static line width so horizontal centering & scaling have ZERO frame-to-frame jitter!
        measured = []
        cur_x = 0.0
        for ci, (txt, is_gold) in enumerate(ln):
            if ci > 0:
                prev_gold = ln[ci - 1][1]
                cur_x += space_w + (gold_pad if (is_gold or prev_gold) else 0.0)
            dist = active_float - (chunk_global_idx + 0.35)
            is_active_now = -0.35 <= dist <= 0.65
            if is_gold:
                mode = "active_gold" if is_active_now else "gold"
            else:
                mode = "active_white" if is_active_now else "white"
            spr, ox, oy, static_adv = render_word_sprite(txt, mode, is_gold_font=is_gold)

            # Smooth spring pop on currently spoken chunk!
            pop_s = 1.0
            dy_w = 0.0
            if -0.30 <= dist <= 0.55:
                bell = math.cos((dist - 0.125) / 0.425 * math.pi * 0.5)
                bell = max(0.0, bell)
                pop_s = 1.0 + (0.065 if is_gold else 0.035) * bell
                dy_w = -5.0 * bell
            elif dist < -0.30:
                dy_w = 3.0 * min(1.0, (-0.30 - dist))

            measured.append((cur_x, spr, ox, oy, static_adv, pop_s, dy_w, is_gold))
            cur_x += static_adv
            chunk_global_idx += 1

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

    # Strict TikTok Safe-Zone Width Cap: max 720px centered at x=540 -> x = 180..900 (0.0px jitter & 100% symmetrical!)
    if max_static_w + 24.0 > 720.0:
        sc = 720.0 / (max_static_w + 24.0)
        nw = int(round(canvas_w * sc))
        nh = int(round(canvas_h * sc))
        layer = layer.resize((nw, nh), Image.Resampling.LANCZOS)

    # Crop symmetrical 1080px-wide strip centered on layer.width // 2 so compositing at x = 540 - w//2 never clips!
    cx_l = layer.width // 2
    half_keep = min(cx_l, 520)
    layer = layer.crop((cx_l - half_keep, 0, cx_l + half_keep, layer.height))

    # Smooth phrase entrance & exit glide!
    u_in = min(1.0, max(0.0, (t - st0) / 0.16))
    u_out = min(1.0, max(0.0, (st1 - t) / 0.14))
    vis = min(u_in, u_out)
    ease = 1.0 - (1.0 - vis) ** 3
    if ease < 0.99:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda a: int(a * ease)))
    y_glide = int(round((1.0 - ease) * 16))
    return layer, y_glide


def render_endcard_v4(t, shot_t0):
    dt = t - shot_t0
    dur = 2.60
    f_hero = get_reader(VID_V4 / "V4_vid01_hero_giftset.mp4", ss=0.0, dur=dur).get_frame(dt, dur)
    bg = f_hero.resize((270, 480), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(16)).resize((W, H), Image.Resampling.BILINEAR).convert("RGBA")

    grad = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    grad[:, :, 0] = (8 + 6 * ys).astype(np.uint8)
    grad[:, :, 1] = (52 - 14 * ys).astype(np.uint8)
    grad[:, :, 2] = (22 - 6 * ys).astype(np.uint8)
    grad[:, :, 3] = 206
    bg.alpha_composite(Image.fromarray(grad, "RGBA"))

    u = min(1.0, max(0.0, dt / 0.35))
    ease = 1.0 - (1.0 - u) ** 3

    # Symmetrical dead-center x = 540 layout (within x = 180..900 -> 100% centered AND 100% TikTok safe!)
    logo_sz = 156
    lg = F20_LOGO.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
    bg.alpha_composite(lg, (540 - logo_sz // 2, int(round(185 + (1.0 - ease) * 24))))

    # Rounded hero gift set card centered at x=540
    pw, ph = 460, 590
    hcrop = f_hero.crop((150, 260, 930, 1420)).resize((pw, ph), Image.Resampling.BICUBIC).convert("RGBA")
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, fill=255)
    card = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    card.paste(hcrop, (0, 0), mask)
    ImageDraw.Draw(card).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, outline=(255, 220, 102, 240), width=3)
    bg.alpha_composite(card, (540 - pw // 2, int(round(375 + (1.0 - ease) * 28))))

    d = ImageDraw.Draw(bg)
    for txt_s, fnt_s, col_s, yy_s in [
        ("THỰC PHẨM F20 × SKA NEST", F_END_BIG, (255, 226, 98, 255), 1005),
        ("SET QUÀ TẶNG TRI ÂN 20/11", F_END_MED, (255, 255, 255, 250), 1068),
    ]:
        bb = d.textbbox((0, 0), txt_s, font=fnt_s)
        d.text((540 - (bb[2] - bb[0]) // 2, yy_s), txt_s, font=fnt_s, fill=col_s, stroke_width=2, stroke_fill=(8, 24, 12, 220))

    # Symmetrical Contact Box centered at x = 540 (x = 180 .. 900 -> width = 720px, 100% centered & TikTok safe!)
    d.rounded_rectangle([180, 1138, 900, 1335], radius=24, fill=(12, 68, 30, 225), outline=(146, 232, 78, 200), width=2)
    for txt_c, col_c, fnt_c, yy_c in [
        ("Hotline: 0979 512 289 • 0706 001 626", (255, 232, 114, 255), F_END_MED, 1158),
        ("Website: thucphamf20.com", (232, 255, 228, 255), F_END_SM, 1212),
        ("17/3 Điện Biên Phủ, Vĩnh Hoà, Nha Trang", (228, 245, 230, 245), F_END_SM, 1258),
    ]:
        bc = d.textbbox((0, 0), txt_c, font=fnt_c)
        d.text((540 - (bc[2] - bc[0]) // 2, yy_c), txt_c, font=fnt_c, fill=col_c)

    return bg.convert("RGB")


def render_frame_v4(fi):
    t = fi / FPS
    shot = SHOTS[-1]
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            shot = s
            break

    if shot["src"] == "OFFICIAL_ENDCARD_V4":
        base = render_endcard_v4(t, shot["t0"])
    else:
        local_t = t - shot["t0"]
        dur_s = shot["t1"] - shot["t0"]
        base = get_reader(shot["src"], ss=shot["ss"], dur=dur_s).get_frame(local_t, dur_s, is_live=shot["live"])

    canvas = base.convert("RGBA")

    # Clean box-free Opening Title (0.15s - 2.45s) centered at x=540!
    if 0.15 <= t <= 2.45:
        vis = min(1.0, (t - 0.15) / 0.22, (2.45 - t) / 0.22)
        if vis > 0.02:
            s1, ox1, oy1, _ = render_word_sprite("THỰC PHẨM F20 × SKA NEST", "white", is_gold_font=False)
            s2, ox2, oy2, _ = render_word_sprite("104 SET QUÀ TRI ÂN 20/11", "active_gold", is_gold_font=True)
            dy = int(round((1.0 - vis) * 16))
            for spr, yy in [(s1, 1305 + dy), (s2, 1368 + dy)]:
                sp = spr if vis >= 0.99 else spr.copy()
                if vis < 0.99:
                    sp.putalpha(sp.getchannel("A").point(lambda a: int(a * vis)))
                canvas.alpha_composite(sp, (540 - sp.width // 2, yy))

    # Animated Word-by-Word Kinetic Subtitle centered dead-on x = 540 (cy = 1385)!
    for st0, st1, lines in SUBTITLES:
        if st0 <= t <= st1:
            sub_im, y_gl = render_kinetic_subtitle(t, st0, st1, lines)
            # Center around x = 540!
            canvas.alpha_composite(sub_im, (540 - sub_im.width // 2, 1385 - sub_im.height // 2 + y_gl))
            break

    return canvas.convert("RGB")


# ==============================================================================
# 6. MIX MASTER -14.0 LUFS AUDIO (Exact 1117 Full Song + Deduplicated SFX!)
# ==============================================================================
def decode_stereo(path, dur_limit=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if dur_limit:
        cmd += ["-t", f"{dur_limit:.4f}"]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def mix_master_v4(total_dur):
    n_tot = int(round(total_dur * SR))
    voice = decode_stereo(V4_DIR / "01_Voice_V4_Master.wav", total_dur)
    if len(voice) < n_tot:
        voice = np.vstack([voice, np.zeros((n_tot - len(voice), 2), dtype=np.float32)])
    voice = voice[:n_tot]

    bgm_full = V4_DIR / "02_BGM_1117_Original_Full_160s.mp3"
    bgm = decode_stereo(bgm_full, total_dur)
    if len(bgm) < n_tot:
        bgm = np.vstack([bgm, np.zeros((n_tot - len(bgm), 2), dtype=np.float32)])
    bgm = bgm[:n_tot]
    # Smooth fade-in 0.5s & fade-out 1.8s on BGM
    fi_b, fo_b = int(0.5 * SR), int(1.8 * SR)
    bgm[:fi_b] *= np.linspace(0.0, 1.0, fi_b, dtype=np.float32)[:, None]
    bgm[-fo_b:] *= np.linspace(1.0, 0.0, fo_b, dtype=np.float32)[:, None]

    # Smooth dynamic ducking: 0.44 on Intro & End-Card, 0.19 under Chi Oanh's voice so speech is crystal-clear!
    win = int(0.05 * SR)
    n_w = n_tot // win
    v_rms = np.sqrt(np.mean(voice[:n_w * win].reshape(n_w, win, 2) ** 2, axis=(1, 2)))
    speaking = (v_rms > 0.010).astype(np.float32)
    duck_u = np.clip(np.convolve(speaking, np.ones(14, dtype=np.float32) / 14.0, mode="same") * 1.85, 0.0, 1.0)
    duck_u = np.convolve(duck_u, np.ones(10, dtype=np.float32) / 10.0, mode="same")
    gain_w = 0.44 * (1.0 - duck_u) + 0.19 * duck_u
    gain_s = np.interp(np.linspace(0, n_w - 1, n_tot), np.arange(n_w), gain_w).astype(np.float32)[:, None]

    sfx_bank = {}
    for mp3 in SFX_DIR.glob("*.mp3"):
        arr = decode_stereo(mp3)
        pk = float(np.max(np.abs(arr))) if len(arr) else 1.0
        if pk > 1e-4:
            arr = arr / pk
        sfx_bank[mp3.stem] = arr

    sfx_events = build_clean_sfx_events()
    sfx_bus = np.zeros((n_tot, 2), dtype=np.float32)
    for ts, key, vol in sfx_events:
        if key in sfx_bank:
            sp = sfx_bank[key]
            i0 = int(round(ts * SR))
            if 0 <= i0 < n_tot:
                i1 = min(n_tot, i0 + len(sp))
                sfx_bus[i0:i1] += sp[:i1 - i0] * float(vol)
    print(f"Mixed {len(sfx_events)} deduplicated, non-overlapping SFX accents!", flush=True)

    mix = voice * 1.25 + bgm * gain_s + np.clip(sfx_bus, -0.45, 0.45)
    pre_w = V4_DIR / "_v4_pre_mix.wav"
    pcm = (np.clip(mix * 0.78, -0.99, 0.99) * 32767.0).astype(np.int16)
    with wave.open(str(pre_w), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    m4a = V4_DIR / "03_Master_V4_14LUFS.m4a"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(pre_w),
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0",
        "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k", str(m4a)
    ], check=True)
    pre_w.unlink(missing_ok=True)

    eb = subprocess.run(["ffmpeg", "-nostats", "-i", str(m4a), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    lufs_str = next((ln.strip() for ln in eb.stderr.splitlines() if "I:" in ln and "LUFS" in ln), "-14.0 LUFS")
    print("V4 Master Loudness:", lufs_str, flush=True)
    return m4a, lufs_str


# ==============================================================================
# 7. BUILD CLEAN SOURCE-ONLY CAPCUT DRAFT ("chỉ cần source gốc thôi không cần thêm chữ nhạc gì vào hết")
# ==============================================================================
def uid():
    return str(uuid.uuid4()).upper()

def us(sec):
    return int(round(float(sec) * 30.0) * 1_000_000 // 30)

def probe_dur_s(p):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def build_clean_source_only_capcut(tl_v4):
    stage_dir = V4_DIR / DRAFT_NAME
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    vid_sub = stage_dir / "video"
    aud_sub = stage_dir / "audio"
    vid_sub.mkdir(parents=True, exist_ok=True)
    aud_sub.mkdir(parents=True, exist_ok=True)

    # Render clean video segment for End-Card without text/music? Wait: user asked for ONLY clean sources in CapCut ("chỉ cần source gốc thôi không cần thêm chữ nhạc gì vào hết"),
    # so let's include all 32 clean video shots (0.00 -> 148.27s) + clean Voiceover track ONLY — ZERO text tracks, ZERO music, ZERO SFX!
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

    voice_end_s = float(tl_v4["voice_end"])
    tot_us = us(voice_end_s)
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

    # Track 0: Clean Edited Video Sources ONLY (Zero zoom keyframes, Zero text, Zero transitions!)
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    for s in SHOTS:
        if s["src"] == "OFFICIAL_ENDCARD_V4":
            continue
        mid, mdur = add_vid(s["src"])
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

    # Track 1: Clean Synced Original Voiceover Segments ONLY (NO music, NO SFX, NO text!)
    tr_vo = copy.deepcopy(atrack_tpl); tr_vo["id"] = uid(); tr_vo["segments"] = []
    for blk in tl_v4["blocks"]:
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

    shutil.copy2(V4_DIR / "kfs_v4" / "V4_kf01_hero_giftset.jpg", stage_dir / "draft_cover.jpg")
    donor_dir = DRAFTS_DIR / "FEEL_CHICKEN_KiemTraMieng_2011_Kute"
    if not donor_dir.exists():
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
        print("  -> Deployed Clean Source-Only CapCut Draft to:", dst_folder, flush=True)

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
    tl_v4 = json.loads((V4_DIR / "timeline_v4_master.json").read_text(encoding="utf-8"))
    total_frames = int(tl_v4["total_frames"])
    total_dur = float(tl_v4["total_dur"])

    if "--test" in sys.argv:
        # Render 16 critical frames covering every single user point!
        test_ts = [
            1.0,    # Crisp opening gift sets
            1.9,    # Wide Chi Oanh behind all 104 gift sets in opening!
            4.8,    # Opening live Chi Oanh behind 104 gift sets (centered!)
            16.5,   # Anh Hau 77 sets + clean box-free kinetic subtitle!
            36.8,   # Long POV 104 sets
            41.2,   # Live Chi Oanh intro (centered!)
            45.8,   # Fix Image 1: V4_vid01_hero_giftset (authentic F20 20/11 basket!)
            53.0,   # Pure To Yen
            62.2,   # Fix Image 2: V4_vid02_two_jars_even (equal height, full-screen, no boxes!)
            71.5,   # Banh Thuyen 250g
            82.5,   # Fix Image 3: V4_vid03_24_thanh_hat (24 bars on bamboo tray, no glove!)
            88.5,   # Fix Image 4: V4_vid04_yen_gia_tri_nhat (full-screen crimson-gold box!)
            96.5,   # Fix Image 5: Live Lip-Synced Chi Oanh holding Cam Nang (centered!)
            115.0,  # Live Lip-Synced Chi Oanh holding basket & showing handle (centered!)
            119.8,  # Fix Image 6: Dedicated flower macro V4_vid05_hoa_diem_nhan (zero repeat!)
            149.6,  # Symmetrical x=540 End-Card!
        ]
        grid = Image.new("RGB", (270 * 4, 480 * 4))
        for i, ts in enumerate(test_ts):
            fr = render_frame_v4(int(round(ts * FPS)))
            th = fr.resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(th)
            d.line([(135, 0), (135, 480)], fill=(0, 255, 120), width=1)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(255, 230, 0))
            grid.paste(th, ((i % 4) * 270, (i // 4) * 480))
        grid.save(V4_DIR / "v4_test_grid_16.jpg", quality=93)
        print("Saved v4_test_grid_16.jpg!")
    else:
        vid_only = V4_DIR / "_v4_video_only.mp4"
        proc = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", str(vid_only)
        ], stdin=subprocess.PIPE)
        for fi in range(total_frames):
            fr = render_frame_v4(fi)
            proc.stdin.write(fr.tobytes())
            if fi % 300 == 0 or fi == total_frames - 1:
                print(f"Rendered {fi+1}/{total_frames} frames ({(fi+1)/total_frames*100:.1f}%)", flush=True)
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(f"FFmpeg video encode failed: {rc}")

        m4a, lufs_str = mix_master_v4(total_dur)
        final_local = V4_DIR / "F20_SET_QUA_2011_V4_FINAL.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", str(vid_only), "-i", str(m4a),
            "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", str(final_local)
        ], check=True)

        # Export Final MP4 to Google Drive + TLH + D:\XUẤT CAPCUT
        for dp in [
            r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\F20_SET_QUA_2011_FINAL.mp4",
            r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\f20-set-qua-2011_FINAL.mp4",
            r"D:\XUẤT CAPCUT\F20_SET_QUA_2011_FINAL.mp4",
        ]:
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(final_local, dp)
            print("  -> Exported Master MP4 to:", dp, flush=True)

        # Build Clean Source-Only CapCut Draft!
        build_clean_source_only_capcut(tl_v4)

        # Build 20-Frame Final QC Sheet & Sync Project Archive to Drive!
        qc_ts = [1.0, 4.8, 13.5, 16.5, 20.0, 27.5, 36.8, 41.2, 45.8, 49.2, 53.0, 57.0, 62.2, 65.0, 71.5, 82.5, 88.5, 96.5, 115.0, 149.6]
        sheet = Image.new("RGB", (270 * 5, 480 * 4))
        tmp = V4_DIR / "_tmp_qcf.jpg"
        for i, ts in enumerate(qc_ts):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(final_local), "-frames:v", "1", str(tmp)], check=True)
            im = Image.open(tmp).resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(255, 230, 0))
            sheet.paste(im, ((i % 5) * 270, (i // 5) * 480))
        tmp.unlink(missing_ok=True)
        qc_path = V4_DIR / "qc_v4_final_20frames.jpg"
        sheet.save(qc_path, quality=93)

        arch = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011")
        arch.mkdir(parents=True, exist_ok=True)
        for sf in [qc_path, V4_DIR / "timeline_v4_master.json", V4_DIR / "v4_step1_build_real_voice_and_centered_aroll.py", V4_DIR / "v4_step2_gen_5_new_videos.py", V4_DIR / "v4_step3_render_master_and_clean_capcut.py"]:
            if sf.exists():
                shutil.copy2(sf, arch / sf.name)
        print("ALL V4 DELIVERABLES COMPLETED!", flush=True)
