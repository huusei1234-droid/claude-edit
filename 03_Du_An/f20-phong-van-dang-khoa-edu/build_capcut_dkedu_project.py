import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30.0

CC_ROOT     = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME  = "261121 F20 Phỏng Vấn Đăng Khoa Edu"
DRAFT_DIR   = CC_ROOT / DRAFT_NAME

# Verified template references (read-only!)
TPL_1117    = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work\backup_1117_F20_user_1644")
FC_V6_DIR   = CC_ROOT / "FEEL_CHICKEN_2011_Full_Layers_V6"
HTPM_DIR    = CC_ROOT / "HTPM"
WORK_1117   = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
CIRCLE_DIR  = WORK_1117 / "v7_assets" / "circle_overlays"
BANNER_MP4  = WORK_1117 / "v7_assets" / "outro_banner_f20_brand.mp4"

F20_261116  = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116")
AH_DIR      = F20_261116 / "Anh Hậu"
DOC_DIR     = F20_261116 / r"Chi Oanh\dọc"
BGM_PATH    = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc\Gentle acoustic guitar background music recommended for corporate VPs(1595921) (3p47s).mp3")
SFX_DIR     = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")

WORK        = Path(r"d:\AI\full studio\output\f20-phong-van-dang-khoa-edu")
WORK.mkdir(parents=True, exist_ok=True)

FULL_CROP_1_1 = {
    "upper_left_x": 0.0, "upper_left_y": 0.0,
    "upper_right_x": 1.0, "upper_right_y": 0.0,
    "lower_left_x": 0.0, "lower_left_y": 1.0,
    "lower_right_x": 1.0, "lower_right_y": 1.0,
}

COINY_FONT_ID   = "7482665772876156165"
COINY_FONT_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"
COL_RED   = [0.9254902005195618, 0.11372549086809158, 0.11372549086809158]
COL_WHITE = [1.0, 1.0, 1.0]

def uid() -> str:
    return str(uuid.uuid4()).upper()

def us(sec: float) -> int:
    f = int(round(float(sec) * FPS))
    return int(round(f * 1_000_000 / FPS))

def norm_fwd(p: Path) -> str:
    return os.path.normpath(str(p)).replace("\\", "/")

PROBE_CACHE = {}
def probe_media(path: Path):
    sp = str(path)
    if sp not in PROBE_CACHE:
        r = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,width,height:stream_side_data=rotation:format=duration",
            "-of", "json", sp
        ], capture_output=True, text=True, check=True)
        j = json.loads(r.stdout)
        vs = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
        has_aud = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
        w, h = int(vs.get("width") or 1080), int(vs.get("height") or 1920)
        for sd in vs.get("side_data_list", []) or []:
            if "rotation" in sd and abs(int(sd["rotation"])) in (90, 270):
                w, h = h, w
        dur = float(j.get("format", {}).get("duration", 0.0) or 0.0)
        PROBE_CACHE[sp] = (w, h, dur, has_aud)
    return PROBE_CACHE[sp]

def probe_audio_dur(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


# ==============================================================================
# 1. MASTER TRACK-0 CUTS (100% RAW ORIGINAL 9:16 + EAR-VERIFIED SPLICES!)
# (id, path, src_in, src_out, speed, vol_cc, speaker)
# ==============================================================================
TRACK0_SPEC = [
    # HỒI 1: Đứng trước cửa phòng ship hàng đến nơi -> Pan 77 set quà -> Bước vào bắt tay
    ("01_doorway",     AH_DIR / "C3925.MP4",   1.70,  14.35, 1.05, 1.15, "oanh"),
    ("02_room_pan",    DOC_DIR / "C3908.MP4",  0.80,   2.30, 1.00, 0.00, "broll"),
    ("03_handshake",   AH_DIR / "C3925.MP4",  18.75,  23.30, 1.00, 1.35, "both"),

    # HỒI 2: Phỏng vấn phần 1 — Lý do Đăng Khoa Edu chọn F20
    ("04_q1_oanh",     AH_DIR / "C3926.MP4",   5.75,  15.55, 1.05, 1.15, "oanh"),
    ("05_a1_reason",   AH_DIR / "C3926.MP4",  16.90,  22.95, 1.05, 1.80, "hau"),
    ("06_a1_quality",  AH_DIR / "C3926.MP4",  23.50,  33.80, 1.05, 1.80, "hau"),
    ("07a_a1_used",    AH_DIR / "C3926.MP4",  35.15,  45.20, 1.05, 1.80, "hau"),
    ("07b_a1_ngon",    AH_DIR / "C3926.MP4",  53.85,  56.10, 1.05, 1.80, "hau"),
    ("08_a1_handmade", AH_DIR / "C3926.MP4",  57.85,  69.05, 1.05, 1.80, "hau"),
    ("09_a1_seaweed",  AH_DIR / "C3926.MP4",  69.75,  79.85, 1.05, 1.80, "hau"),
    ("10_a1_energy",   AH_DIR / "C3926.MP4",  86.75,  98.10, 1.05, 1.80, "hau"),

    # HỒI 3: Phỏng vấn phần 2 — Cảm nhận khi cầm 77 set quà hoàn thiện trên tay
    ("11_q2_oanh",     AH_DIR / "C3926.MP4", 108.00, 116.50, 1.05, 1.15, "oanh"),
    ("12_a2_happy",    AH_DIR / "C3926.MP4", 133.20, 142.55, 1.05, 1.80, "hau"),
    ("13_a2_handle",   AH_DIR / "C3926.MP4", 143.15, 149.15, 1.05, 1.80, "hau"),
    ("14_a2_mica",     AH_DIR / "C3926.MP4", 150.20, 165.40, 1.05, 1.55, "both"),

    # HỒI 4: Phỏng vấn phần 3 — Tối giản tập trung chất lượng & điểm tên 4 món
    ("15_q3_consult",  AH_DIR / "C3926.MP4", 187.55, 198.90, 1.05, 1.15, "oanh"),
    ("16_a3_minimal",  AH_DIR / "C3926.MP4", 204.90, 212.80, 1.05, 1.80, "hau"),
    ("17_a3_4items",   AH_DIR / "C3926.MP4", 213.35, 233.35, 1.05, 1.80, "hau"),

    # HỒI 5: Chị Oanh tặng quà nhỏ (Hộp Quà Sách) & Anh Hậu cảm ơn sách
    ("18_gift_intro",  AH_DIR / "C3932.MP4",   2.60,  16.45, 1.05, 1.15, "oanh"),
    ("19_gift_give",   AH_DIR / "C3932.MP4",  47.65,  51.35, 1.05, 1.35, "both"),
    ("20_book1",       AH_DIR / "C3932.MP4",  63.80,  74.05, 1.05, 1.15, "oanh"),
    ("21_book2a",      AH_DIR / "C3932.MP4",  78.60,  84.70, 1.05, 1.15, "oanh"),
    ("22_book2b",      AH_DIR / "C3932.MP4",  91.40,  96.25, 1.05, 1.15, "oanh"),
    ("23_hau_thanks",  AH_DIR / "C3932.MP4", 122.40, 130.00, 1.05, 1.80, "hau"),

    # HỒI 6: Kết thúc — Lời cảm ơn & CTA liên hệ chị Oanh + Banner tone Logo F20
    ("24_oanh_cta",    DOC_DIR / "C3864.MP4",  5.15,  19.30, 1.05, 1.20, "oanh"),
    ("25_banner",      BANNER_MP4,             0.00,   3.00, 1.00, 0.00, "banner"),
]


def compute_timeline():
    cur_u = 0
    segs = {}
    seg_list = []
    for cid, path, sin, sout, spd, vol, spk in TRACK0_SPEC:
        dur_s = (sout - sin) / spd
        du_u = us(dur_s)
        item = {
            "id": cid, "path": str(path), "src_in": sin, "src_out": sout,
            "speed": spd, "vol": vol, "speaker": spk,
            "tl_start_u": cur_u, "tl_dur_u": du_u, "tl_end_u": cur_u + du_u,
            "tl_start": round(cur_u / 1e6, 4), "tl_end": round((cur_u + du_u) / 1e6, 4),
        }
        segs[cid] = item
        seg_list.append(item)
        cur_u += du_u
    return seg_list, segs, cur_u


def src_to_tl(seg: dict, src_t: float) -> float:
    clamped = max(seg["src_in"], min(seg["src_out"], src_t))
    return seg["tl_start"] + (clamped - seg["src_in"]) / seg["speed"]


def main():
    if DRAFT_DIR.exists() and (DRAFT_DIR / ".locked").exists():
        raise RuntimeError(f"{DRAFT_NAME} is currently locked in CapCut!")

    seg_list, S, total_u = compute_timeline()
    total_s = total_u / 1e6
    print(f"Computed Master Timeline: {len(seg_list)} Track-0 segments, total = {total_s:.2f}s ({int(total_s//60)}m {total_s%60:04.1f}s)")
    for it in seg_list:
        print(f"  {it['id']:15s} | {it['tl_start']:6.2f} -> {it['tl_end']:6.2f}s ({it['tl_dur_u']/1e6:5.2f}s) | {Path(it['path']).name}")

    # Helper to convert (seg_id, src_t0, src_t1) -> (tl_t0, tl_t1)
    def tmap(cid: str, s0: float, s1: float) -> tuple[float, float]:
        return (src_to_tl(S[cid], s0), src_to_tl(S[cid], s1))

    # ==========================================================================
    # 2. TRACK 1 — 100% RAW ORIGINAL VERTICAL 9:16 B-ROLLS (scale=1.0, pos=(0,0), 0 keyframes!)
    # ==========================================================================
    BROLL_SPEC = [
        # (tl_t0, tl_t1, path, src_in, speed, in_anim, out_anim, note)
        (*tmap("01_doorway", 4.60, 7.60),   DOC_DIR / "C3909.MP4", 1.50, 1.00, None, None, "Cận mượt 77 set quà trong phòng Đăng Khoa Edu"),
        (*tmap("01_doorway", 7.60, 10.10),  DOC_DIR / "C3914.MP4", 3.00, 1.00, None, None, "Nhân viên F20 bày trí set quà gọn gàng lên bàn"),
        (*tmap("06_a1_quality", 28.80, 32.80), DOC_DIR / "C3910.MP4", 1.00, 0.90, None, None, "Toàn cảnh dãy 77 set quà chất lượng tại Đăng Khoa Edu"),
        # Cover 07a -> 07b jump-cut smoothly with crisp bird's nest macro!
        (src_to_tl(S["07a_a1_used"], 42.60), src_to_tl(S["07b_a1_ngon"], 56.00), DOC_DIR / "C3867.MP4", 0.35, 0.85, None, None, "Cận tổ yến tinh chế SKANEST cao cấp"),
        (*tmap("08_a1_handmade", 60.50, 63.80), DOC_DIR / "C3869.MP4", 1.20, 1.00, None, None, "Hộp yến sào SKANEST làm thủ công không hóa chất"),
        # Cover 09 -> 10 jump-cut smoothly with Rong biển + Bánh thuyền!
        (src_to_tl(S["09_a1_seaweed"], 77.20), src_to_tl(S["09_a1_seaweed"], 79.85), DOC_DIR / "C3882.MP4", 0.60, 1.00, None, None, "Rong biển Tuệ Tâm tiện lợi"),
        (src_to_tl(S["10_a1_energy"], 86.75),  src_to_tl(S["10_a1_energy"], 89.60),  DOC_DIR / "C3887.MP4", 0.50, 1.00, None, None, "Bánh thuyền mix hạt tiếp năng lượng"),
        (*tmap("11_q2_oanh", 108.40, 111.80), AH_DIR / "C3922.MP4", 9.00, 1.00, None, None, "Anh Hậu & Chị Oanh xem thành phẩm set quà"),
        (*tmap("14_a2_mica", 153.20, 156.60), DOC_DIR / "C3873.MP4", 0.80, 0.85, None, None, "Cận túi giỏ Mica trong suốt khoe trọn 4 món"),
        (*tmap("15_q3_consult", 190.80, 194.20), DOC_DIR / "C3918.MP4", 0.80, 1.00, None, None, "Chị Oanh chăm chút từng set quà trên bàn"),
        # Cover 18_gift_intro -> 19_gift_give neatly
        (src_to_tl(S["18_gift_intro"], 14.00), src_to_tl(S["18_gift_intro"], 16.45), AH_DIR / "C3921.MP4", 1.00, 1.00, None, None, "Khoảnh khắc giao lưu thân tình tại Đăng Khoa Edu"),
        (*tmap("24_oanh_cta", 13.50, 16.50), DOC_DIR / "C3875.MP4", 2.00, 0.90, None, None, "Dãy set quà 20/11 F20 sẵn sàng giao ngay"),
    ]

    # ==========================================================================
    # 3. TRACKS 2..3 — CLEAN ROUND CIRCULAR PRODUCT OVERLAYS (1080x1920, 0% handle, 0% oval stretch!)
    # Placed at (X=0.0, Y=+0.28) cleanly centered on the sky-blue wall between Anh Hậu & Chị Oanh's heads!
    # ==========================================================================
    CIRCLE_SPEC = [
        # (tl_t0, tl_t1, png_name, px, py, sc)
        # During 07a: Anh Hậu mentions "bánh hạt, yến chưng tươi"
        (*tmap("07a_a1_used", 38.60, 42.50),    "circle_01_to_yen_a5.png",      +0.08, +0.34, 0.41),
        # During 09: Anh Hậu mentions "rong biển với lại bánh hạt"
        (*tmap("09_a1_seaweed", 70.60, 73.70),  "circle_02_2hop_rong_bien.png", +0.08, +0.34, 0.41),
        (*tmap("09_a1_seaweed", 73.85, 77.10),  "circle_03_banh_thuyen.png",    +0.08, +0.34, 0.41),
        # During 17_a3_4items: Anh Hậu points at all items inside the basket one by one!
        (*tmap("17_a3_4items", 213.60, 216.15), "circle_02_2hop_rong_bien.png", +0.08, +0.34, 0.41),
        (*tmap("17_a3_4items", 216.25, 219.50), "circle_01_to_yen_a5.png",      +0.08, +0.34, 0.41),
        (*tmap("17_a3_4items", 219.60, 222.95), "circle_08_duong_phen.png",     +0.08, +0.34, 0.41),
        (*tmap("17_a3_4items", 223.05, 226.85), "circle_03_banh_thuyen.png",    +0.08, +0.34, 0.41),
        (*tmap("17_a3_4items", 226.95, 230.40), "circle_04_kep_hat_500g.png",   +0.08, +0.34, 0.41),
    ]

    # ==========================================================================
    # 4. PROOFREAD NATIVE CAPCUT SUBTITLES (100% Vietnamese Diacritics, check_flag=15, Coiny!)
    # (tl_t0, tl_t1, text, is_highlight)  -> is_highlight: True=White fill + Red stroke, False=Red fill + White stroke
    # ==========================================================================
    SUBTITLES = [
        # Hồi 1
        (*tmap("01_doorway", 1.75, 4.55),  "Bên Oanh đã chuẩn bị xong 77 set quà", True),
        (*tmap("01_doorway", 4.60, 7.35),  "giao tới văn phòng Đăng Khoa Edu", False),
        (*tmap("01_doorway", 7.40, 10.10), "tại 23 Thái Nguyên rồi nhé mọi người!", False),
        (*tmap("01_doorway", 10.20, 14.25),"Giờ cùng Oanh vào giao quà cho anh Hậu nhé!", False),
        (*tmap("03_handshake", 18.85, 20.15),"Xin chào anh Hậu ạ!", False),
        (*tmap("03_handshake", 20.20, 23.15),"Chào em, chào Oanh F20!", True),

        # Hồi 2: Q1 Lý do chọn F20
        (*tmap("04_q1_oanh", 5.80, 8.55),  "Vì sao năm nay Đăng Khoa Edu", False),
        (*tmap("04_q1_oanh", 8.60, 11.45), "chọn sản phẩm của Thực phẩm F20", True),
        (*tmap("04_q1_oanh", 11.50, 15.45),"làm quà tri ân thầy cô dịp 20/11 ạ?", False),
        (*tmap("05_a1_reason", 16.95, 22.85),"Thầy cô Đăng Khoa Edu đã có nhiều\nđóng góp rất là tuyệt vời", False),
        (*tmap("06_a1_quality", 23.55, 28.10),"Hậu muốn gửi lời cảm ơn đến thầy cô,", False),
        (*tmap("06_a1_quality", 28.20, 33.70),"muốn có một chút quà — nhưng phải chất lượng!", True),
        (*tmap("07a_a1_used", 35.20, 39.20), "Ở F20, bản thân Hậu đã dùng rất nhiều rồi", False),
        (*tmap("07a_a1_used", 39.30, 45.15), "từ bánh hạt, yến cho đến yến chưng tươi...", False),
        (*tmap("07b_a1_ngon", 53.90, 56.05), "thấy rất là ngon!", True),
        (*tmap("08_a1_handmade", 57.90, 63.25),"F20 làm yến thủ công hết, không hóa chất!", True),
        (*tmap("08_a1_handmade", 63.40, 69.00),"Gia đình dùng, tặng bạn bè ai cũng khen!", False),
        (*tmap("09_a1_seaweed", 69.80, 73.10),"Đặc biệt rất thích rong biển và bánh hạt", True),
        (*tmap("09_a1_seaweed", 73.25, 79.80),"Giáo viên nhiều khi bận bịu không kịp ăn sáng,", False),
        (*tmap("10_a1_energy", 86.80, 91.45), "ăn 1–2 cái tiếp năng lượng rất là ngon!", False),
        (*tmap("10_a1_energy", 91.55, 98.05), "Rong biển và các loại hạt hoàn toàn thiên nhiên!", True),

        # Hồi 3: Q2 Cảm nhận cầm 77 set quà trên tay
        (*tmap("11_q2_oanh", 108.05, 111.20), "Hôm nay giao những set quà tới đây,", False),
        (*tmap("11_q2_oanh", 111.30, 116.45), "anh Hậu chia sẻ cảm nhận khi nhận quà nhé!", False),
        (*tmap("12_a2_happy", 133.25, 138.20),"77 set quà đã tới Đăng Khoa Edu,", True),
        (*tmap("12_a2_happy", 138.30, 142.50),"cầm trên tay cảm thấy rất là ưng ý!", False),
        (*tmap("13_a2_handle", 143.20, 149.10),"Có quai xách tiện tay, cũng dễ thương nữa!", False),
        (*tmap("14_a2_mica", 150.25, 152.75), "Phía dưới đây là mica hả em?", False),
        (*tmap("14_a2_mica", 152.85, 156.00), "Dạ túi giỏ đựng quà chất liệu mica trong ạ!", False),
        (*tmap("14_a2_mica", 156.10, 160.20), "Mica trong luôn — không giấu giếm gì hết!", True),
        (*tmap("14_a2_mica", 160.40, 165.35), "Show hết luôn — cái gì tốt mình khoe hết!", True),

        # Hồi 4: Q3 Tối giản chất lượng & 4 món
        (*tmap("15_q3_consult", 187.60, 193.55),"Anh Hậu nói muốn set quà tập trung chất lượng,", False),
        (*tmap("15_q3_consult", 193.65, 198.85),"thầy cô dùng bồi bổ sức khỏe và tiện lợi!", False),
        (*tmap("16_a3_minimal", 204.95, 209.60),"Toán học gọi là tối giản để tập trung chất lượng!", True),
        (*tmap("16_a3_minimal", 209.75, 212.75),"Cái gì đơn giản là nghệ thuật hết!", True),
        (*tmap("17_a3_4items", 213.45, 216.10), "Đây là rong biển nè,", False),
        (*tmap("17_a3_4items", 216.25, 219.45), "đây là yến sào cao cấp nè,", True),
        (*tmap("17_a3_4items", 219.60, 222.90), "hộp đường phèn nè,", False),
        (*tmap("17_a3_4items", 223.05, 226.80), "bánh thuyền mix hạt nè,", False),
        (*tmap("17_a3_4items", 226.95, 229.00), "rong biển kẹp hạt nè!", False),
        (*tmap("17_a3_4items", 229.10, 233.30), "Những món rất hợp với thầy cô giáo — tuyệt vời!", True),

        # Hồi 5: Tặng Hộp Quà Sách & Anh Hậu cảm ơn sách
        (*tmap("18_gift_intro", 2.70, 8.60),   "Hôm nay đến giao quà cho Đăng Khoa Edu,", False),
        (*tmap("18_gift_intro", 8.70, 16.35),  "F20 có món quà nhỏ tặng thầy Hậu dịp 20/11!", True),
        (*tmap("19_gift_give", 47.70, 49.55),  "Em xin gửi anh món quà nhỏ ạ!", False),
        (*tmap("19_gift_give", 49.65, 51.30),  "Cảm ơn Thực phẩm F20!", True),
        (*tmap("20_book1", 63.85, 67.20),      "Biết anh Hậu là người cực kỳ mê sách,", False),
        (*tmap("20_book1", 67.30, 74.00),      "F20 tặng anh cuốn 'Danh Nhân Thế Giới'!", True),
        (*tmap("21_book2a", 78.65, 84.65),     "Và quyển thứ 2 — vì anh còn là doanh nhân...", False),
        (*tmap("22_book2b", 91.45, 96.20),     "cuốn 'Toán Học Của Thịnh Vượng'!", True),
        (*tmap("23_hau_thanks", 122.50, 125.55),"Tuyệt vời! Cảm ơn Oanh và F20 rất nhiều!", True),
        (*tmap("23_hau_thanks", 125.70, 129.95),"Món quà tan chảy đó — siêu thích luôn!", True),

        # Hồi 6: Lời cảm ơn & CTA liên hệ chị Oanh
        (*tmap("24_oanh_cta", 5.20, 10.60),    "Oanh xin cảm ơn quý anh chị đã tin tưởng\nđặt hàng Thực phẩm F20!", False),
        (*tmap("24_oanh_cta", 10.75, 14.70),   "Anh chị cần đặt set quà tặng dịp lễ 20/11", False),
        (*tmap("24_oanh_cta", 14.80, 19.25),   "hãy inbox ngay cho Oanh nhé!", True),
    ]

    # ==========================================================================
    # 5. FLOATING CHAPTER / EMPHASIS HEADERS (White + Red Stroke, Y=+0.66 above heads, Safe Margins!)
    # ==========================================================================
    HEADERS = [
        # (tl_t0, tl_t1, text, px, py, size)
        (0.30,  4.80, "GIAO 77 SET QUÀ\nĐĂNG KHOA EDU",         0.00, +0.66, 12.2),
        (S["04_q1_oanh"]["tl_start"] + 0.2,  S["04_q1_oanh"]["tl_start"] + 4.8,  "01 • LÝ DO CHỌN F20",            0.00, +0.66, 12.8),
        (S["08_a1_handmade"]["tl_start"],    S["08_a1_handmade"]["tl_start"] + 5.2, "YẾN THỦ CÔNG\nKHÔNG HÓA CHẤT",  0.00, +0.66, 12.2),
        (S["11_q2_oanh"]["tl_start"] + 0.2,  S["11_q2_oanh"]["tl_start"] + 4.6,  "02 • CẢM NHẬN THÀNH PHẨM",       0.00, +0.66, 12.2),
        (src_to_tl(S["14_a2_mica"], 156.0),  S["14_a2_mica"]["tl_end"] - 0.2,    "GIỎ MICA TRONG\nSHOW HẾT!",      0.00, +0.66, 12.6),
        (S["16_a3_minimal"]["tl_start"],     S["16_a3_minimal"]["tl_end"],       "TỐI GIẢN\nTẬP TRUNG CHẤT LƯỢNG", 0.00, +0.66, 12.0),
        (S["18_gift_intro"]["tl_start"]+0.2, S["18_gift_intro"]["tl_start"]+5.2, "QUÀ TRI ÂN\nTHẦY HẬU 20/11",     0.00, +0.66, 12.4),
        (S["23_hau_thanks"]["tl_start"]+0.2, S["23_hau_thanks"]["tl_end"],       "MÓN QUÀ TAN CHẢY\nSIÊU THÍCH!",  0.00, +0.66, 12.2),
        (src_to_tl(S["24_oanh_cta"], 13.5),  S["24_oanh_cta"]["tl_end"] - 0.1,   "INBOX OANH NGAY\nĐẶT QUÀ 20/11", 0.00, +0.64, 12.2),
    ]

    # Auto-wrap any subtitle line > 27 chars into 2 balanced lines so 100% stay inside safe horizontal margins!
    def wrap_sub(text: str, max_chars: int = 27) -> str:
        if "\n" in text or len(text) <= max_chars:
            return text
        words = text.split()
        best_i, best_diff = 1, 999
        for i in range(1, len(words)):
            l1 = " ".join(words[:i])
            l2 = " ".join(words[i:])
            diff = abs(len(l1) - len(l2))
            if diff < best_diff:
                best_diff, best_i = diff, i
        return " ".join(words[:best_i]) + "\n" + " ".join(words[best_i:])

    SUBTITLES_CLEAN = []
    SUB_RAW = sorted(SUBTITLES, key=lambda x: x[0])
    for i, (t0, t1, tx, hl) in enumerate(SUB_RAW):
        # Smooth tiny < 0.28s gaps between consecutive lines so zero empty flash frames occur
        if i + 1 < len(SUB_RAW):
            nxt_t0 = SUB_RAW[i + 1][0]
            if 0.0 < (nxt_t0 - t1) <= 0.28:
                t1 = nxt_t0 - 0.034
            elif t1 > nxt_t0 - 0.034:
                t1 = max(t0 + 0.35, nxt_t0 - 0.034)
        SUBTITLES_CLEAN.append((t0, t1, wrap_sub(tx), hl))
    SUBTITLES = SUBTITLES_CLEAN

    # ==========================================================================
    # 6. EAR-VERIFIED LUXURY TACTILE SFX (-19..-21dB, vol=0.09..0.12)
    # ==========================================================================
    SFX_SPEC = [
        (0.25, "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                               "Air Mở Cảnh",      0.11, 0.7),
        (0.35, "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3",                          "Chuông Gió Mở",    0.09, 1.8),
        (S["02_room_pan"]["tl_start"], "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",       "Lướt Vào Phòng",   0.10, 0.6),
        (S["04_q1_oanh"]["tl_start"] + 0.15, "Whoosh - Fast Swoosh Pop 01 (1s).mp3",      "Mở Phần 01",       0.10, 0.6),
        (CIRCLE_SPEC[0][0], "Click & Máy Chữ - click (1s).mp3",                           "Circle Yến Sào",   0.11, 0.35),
        (S["08_a1_handmade"]["tl_start"], "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",    "Shine Thủ Công",   0.09, 0.9),
        (CIRCLE_SPEC[1][0], "Click & Máy Chữ - click (1s).mp3",                           "Circle Rong Biển", 0.11, 0.35),
        (CIRCLE_SPEC[2][0], "Click & Máy Chữ - click (1s).mp3",                           "Circle Bánh Thuyền",0.11, 0.35),
        (S["11_q2_oanh"]["tl_start"] + 0.15, "Whoosh - Fast Swoosh Pop 01 (1s).mp3",      "Mở Phần 02",       0.10, 0.6),
        (src_to_tl(S["14_a2_mica"], 156.0), "Ding - Tiếng chuông ngân trong trẻo.mp3",    "Ding Mica Trong",  0.10, 1.1),
        (S["16_a3_minimal"]["tl_start"], "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",     "Swoosh Tối Giản",  0.10, 0.6),
        # 5 circular badges pop cleanly as Anh Hậu names each item!
        (CIRCLE_SPEC[3][0], "Click & Máy Chữ - click (1s).mp3",                           "Món 1 Rong Biển",  0.11, 0.35),
        (CIRCLE_SPEC[4][0], "Click & Máy Chữ - click (1s).mp3",                           "Món 2 Yến Sào",    0.11, 0.35),
        (CIRCLE_SPEC[5][0], "Click & Máy Chữ - click (1s).mp3",                           "Món 3 Đường Phèn", 0.11, 0.35),
        (CIRCLE_SPEC[6][0], "Click & Máy Chữ - click (1s).mp3",                           "Món 4 Bánh Thuyền",0.11, 0.35),
        (CIRCLE_SPEC[7][0], "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3", "Món 5 Kẹp Hạt", 0.10, 1.0),
        # Gift box & thank you & CTA & Banner
        (S["18_gift_intro"]["tl_start"] + 0.15, "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3", "Mở Quà Tri Ân", 0.10, 0.6),
        (S["20_book1"]["tl_start"], "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3", "Lật Sách 1", 0.11, 0.7),
        (S["22_book2b"]["tl_start"], "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3", "Lật Sách 2", 0.11, 0.7),
        (S["23_hau_thanks"]["tl_start"], "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",     "Shine Cảm Ơn",     0.09, 0.9),
        (src_to_tl(S["24_oanh_cta"], 13.5), "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3", "Bell CTA", 0.10, 1.1),
        (S["25_banner"]["tl_start"] - 0.05, "Whoosh - Title Swoosh (1s).mp3",             "Swoosh Banner",    0.12, 0.8),
        (S["25_banner"]["tl_start"] + 0.10, "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3", "Chimes Banner", 0.11, 2.5),
    ]

    # Save unified manifest for both CapCut verification AND GPU Final MP4 Render!
    manifest = {
        "draft_name": DRAFT_NAME,
        "total_s": round(total_s, 4),
        "total_u": total_u,
        "track0": seg_list,
        "brolls": [
            {"t0": round(t0, 4), "t1": round(t1, 4), "path": str(p), "src_in": sin, "speed": spd, "in_anim": ia, "out_anim": oa, "note": nt}
            for t0, t1, p, sin, spd, ia, oa, nt in BROLL_SPEC
        ],
        "circles": [
            {"t0": round(t0, 4), "t1": round(t1, 4), "png": png, "path": str(CIRCLE_DIR / png), "px": px, "py": py, "sc": sc}
            for t0, t1, png, px, py, sc in CIRCLE_SPEC
        ],
        "subtitles": [
            {"t0": round(t0, 4), "t1": round(t1, 4), "text": tx, "highlight": hl}
            for t0, t1, tx, hl in SUBTITLES
        ],
        "headers": [
            {"t0": round(t0, 4), "t1": round(t1, 4), "text": tx, "px": px, "py": py, "size": sz}
            for t0, t1, tx, px, py, sz in HEADERS
        ],
        "bgm": {"path": str(BGM_PATH), "vol_cc": 0.22, "start_s": 0.0, "end_s": round(total_s, 4)},
        "sfx": [
            {"t0": round(t0, 4), "file": fn, "path": str(SFX_DIR / fn), "label": lbl, "vol_cc": vol, "max_dur": md}
            for t0, fn, lbl, vol, md in SFX_SPEC
        ],
    }
    (WORK / "project_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # ==========================================================================
    # BUILD CAPCUT DESKTOP PROJECT (`261121 F20 Phỏng Vấn Đăng Khoa Edu`)
    # ==========================================================================
    pj_tpl   = json.loads((TPL_1117 / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id_tpl = pj_tpl["main_timeline_id"]
    D        = json.loads((TPL_1117 / "Timelines" / tl_id_tpl / "draft_content.json").read_text(encoding="utf-8"))

    dc_fc    = json.loads((FC_V6_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dm_fc    = json.loads((FC_V6_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))
    dc_htpm  = json.loads((HTPM_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dm_htpm  = json.loads((HTPM_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))

    VIDEO_ANIMS = json.loads((WORK_1117 / "verified_video_anims.json").read_text(encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(D["tracks"][0])
    vseg_tpl   = copy.deepcopy(D["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(dc_htpm["materials"]["videos"][0])
    pmat_tpl   = copy.deepcopy(next(m for m in dc_fc["materials"]["videos"] if m.get("type") == "photo"))
    dm_vid_tpl = copy.deepcopy(dm_htpm["draft_materials"][0]["value"][0])
    dm_pho_tpl = copy.deepcopy(next(x for g in dm_fc["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "photo"))

    atrack_tpl = copy.deepcopy(next(tr for tr in D["tracks"] if tr["type"] == "audio"))
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl   = copy.deepcopy(D["materials"]["audios"][0])

    # Extract clean native text templates (`subtitle` + `text`) directly from 1117 F20 backup!
    tmap_tpl   = {t["id"]: t for t in D["materials"]["texts"]}
    sub_tr_tpl = copy.deepcopy(next(tr for tr in D["tracks"] if tr["type"] == "text" and any(tmap_tpl.get(s["material_id"], {}).get("type") == "subtitle" for s in tr["segments"])))
    txt_tr_tpl = copy.deepcopy(next(tr for tr in D["tracks"] if tr["type"] == "text" and any(tmap_tpl.get(s["material_id"], {}).get("type") == "text" for s in tr["segments"])))
    sub_seg_tpl = copy.deepcopy(next(s for s in sub_tr_tpl["segments"] if tmap_tpl.get(s["material_id"], {}).get("type") == "subtitle"))
    sub_mat_tpl = copy.deepcopy(tmap_tpl[sub_seg_tpl["material_id"]])
    txt_seg_tpl = copy.deepcopy(next(s for s in txt_tr_tpl["segments"] if tmap_tpl.get(s["material_id"], {}).get("type") == "text"))
    txt_mat_tpl = copy.deepcopy(tmap_tpl[txt_seg_tpl["material_id"]])

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {
        k: copy.deepcopy(next(x for x in D["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"]))
        for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in D["materials"].get(k, []))
    }
    a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {
        k: copy.deepcopy(next(x for x in D["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"]))
        for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in D["materials"].get(k, []))
    }

    # Clear all old materials cleanly so zero leftover 1117 F20 bloat remains!
    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = []

    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)
    vis_cache = {}
    new_dm_entries = []

    def register_visual(path: Path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing visual: {path}")
        fwd = norm_fwd(path)
        if fwd in vis_cache:
            return vis_cache[fwd]
        is_photo = path.suffix.lower() in (".png", ".jpg", ".jpeg")
        mid = uid()
        lmid = str(uuid.uuid4())
        if is_photo:
            with Image.open(path) as im:
                w, h = im.size
            assert (w, h) == (W, H), f"Photo overlay MUST be 1080x1920: {path.name} ({w}x{h})"
            dur_u = 10_800_000_000
            m = copy.deepcopy(pmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "photo", "path": fwd, "media_path": "", "local_id": "",
                "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": False,
                "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0,
            })
            dme = copy.deepcopy(dm_pho_tpl)
            dme.update({
                "id": lmid, "file_Path": fwd, "extra_info": path.name,
                "duration": 5_000_000, "width": w, "height": h,
                "metetype": "photo", "item_source": 1,
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
            })
        else:
            w, h, dur_s, has_aud = probe_media(path)
            assert h >= w, f"Video source MUST be native vertical 9:16: {path.name} ({w}x{h})"
            dur_u = max(33333, us(dur_s))
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd, "media_path": "", "local_id": "",
                "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud),
                "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0,
            })
            dme = copy.deepcopy(dm_vid_tpl)
            dme.update({
                "id": lmid, "file_Path": fwd, "extra_info": path.name,
                "duration": dur_u, "width": w, "height": h,
                "metetype": "video", "item_source": 1,
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
                "roughcut_time_range": {"start": 0, "duration": dur_u},
                "sub_time_range": {"start": -1, "duration": -1},
            })
        D["materials"]["videos"].append(m)
        new_dm_entries.append(dme)
        vis_cache[fwd] = (mid, dur_u, w, h, is_photo)
        return mid, dur_u, w, h, is_photo

    def make_video_seg(path: Path, tgt_st_u: int, tgt_du_u: int, src_in_s: float, spd: float, vol: float,
                       px: float = 0.0, py: float = 0.0, sc: float = 1.0,
                       in_anim: str | None = None, out_anim: str | None = None,
                       micro_fade: bool = False):
        mid, mat_dur_u, _, _, is_photo = register_visual(path)
        if is_photo:
            src_st_u, src_du_u, spd = 0, tgt_du_u, 1.0
        else:
            src_st_u = us(src_in_s)
            src_du_u = int(round(tgt_du_u * spd))
            if src_st_u + src_du_u > mat_dur_u:
                src_st_u = max(0, mat_dur_u - src_du_u)

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = round(spd, 4)
            D["materials"][k].append(em); refs.append(em["id"])

        if micro_fade and vol > 0.0:
            fid = uid()
            D["materials"].setdefault("audio_fades", []).append({
                "fade_in_duration": 33333, "fade_out_duration": 66666, "fade_type": 0, "id": fid, "type": "audio_fade"
            })
            refs.append(fid)

        anim_list = []
        if in_anim and in_anim in VIDEO_ANIMS["in"]:
            ai = copy.deepcopy(VIDEO_ANIMS["in"][in_anim])
            ai["start"] = 0
            ai["duration"] = min(180000, tgt_du_u // 4)
            anim_list.append(ai)
        if out_anim and out_anim in VIDEO_ANIMS["out"]:
            ao = copy.deepcopy(VIDEO_ANIMS["out"][out_anim])
            od = min(180000, tgt_du_u // 4)
            ao["duration"] = od
            ao["start"] = max(0, tgt_du_u - od)
            anim_list.append(ao)
        if anim_list:
            ma_id = uid()
            D["materials"].setdefault("material_animations", []).append({
                "animations": anim_list, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
            })
            refs.append(ma_id)

        seg["clip"]["scale"] = {"x": round(sc, 4), "y": round(sc, 4)}
        seg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        seg["clip"]["rotation"] = 0.0
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": int(src_st_u), "duration": int(src_du_u)},
            "target_timerange": {"start": int(tgt_st_u), "duration": int(tgt_du_u)},
            "speed": round(spd, 4), "volume": round(vol, 4), "last_nonzero_volume": round(max(vol, 1.0), 4),
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        return seg

    # Track 0 segments (100% untouched scale=1.0, pos=(0,0), micro-fade on every dialogue cut!)
    tr0_segs = [
        make_video_seg(
            Path(it["path"]), it["tl_start_u"], it["tl_dur_u"], it["src_in"], it["speed"], it["vol"],
            in_anim=("Rõ dần" if it["id"] == "25_banner" else None),
            micro_fade=(it["vol"] > 0.0)
        )
        for it in seg_list
    ]
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = tr0_segs

    # Track 1 B-Roll segments (100% raw 9:16, scale=1.0, pos=(0,0), 0 keyframes!)
    tr1_segs = [
        make_video_seg(Path(p), us(t0), us(t1) - us(t0), sin, spd, 0.0, in_anim=ia, out_anim=oa)
        for t0, t1, p, sin, spd, ia, oa, _ in BROLL_SPEC
    ]
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["segments"] = tr1_segs

    # Track 2 Clean Round Circular Product Overlays (1080x1920, FULL_CROP_1_1, 0% handle!)
    tr2_segs = [
        make_video_seg(CIRCLE_DIR / png, us(t0), us(t1) - us(t0), 0.0, 1.0, 0.0,
                       px=px, py=py, sc=sc, in_anim="Rõ dần", out_anim="Mờ dần")
        for t0, t1, png, px, py, sc in CIRCLE_SPEC
    ]
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["segments"] = tr2_segs

    # Native Editable Coiny Texts (Subtitles + Floating Headers, check_flag = 15!)
    def make_native_text(is_sub: bool, t0_s: float, t1_s: float, text: str, px: float, py: float, size: float,
                         fill_col: list, stroke_col: list, stroke_w: float):
        tid = uid()
        tm = copy.deepcopy(sub_mat_tpl if is_sub else txt_mat_tpl)
        cobj = json.loads(tm["content"])
        cobj["text"] = text
        st0 = copy.deepcopy(cobj["styles"][0])
        st0["range"] = [0, len(text)]
        st0["size"] = float(size)
        st0["font"] = {"path": COINY_FONT_PATH, "id": COINY_FONT_ID}
        st0["fill"] = {"content": {"render_type": "solid", "solid": {"color": fill_col}}}
        st0["strokes"] = [{"content": {"render_type": "solid", "solid": {"color": stroke_col}}, "width": float(stroke_w), "mode": 0}]
        cobj["styles"] = [st0]

        tm.update({
            "id": tid,
            "type": "subtitle" if is_sub else "text",
            "content": json.dumps(cobj, ensure_ascii=False),
            "recognize_text": text,
            "font_size": float(size),
            "font_path": COINY_FONT_PATH,
            "check_flag": 15,
            "background_style": 0,
            "has_shadow": False,
            "line_spacing": 0.02,
            "letter_spacing": 0.0,
        })
        D["materials"]["texts"].append(tm)

        sg = copy.deepcopy(sub_seg_tpl if is_sub else txt_seg_tpl)
        st_u = us(t0_s)
        du_u = max(us(0.35), us(t1_s) - st_u)
        sg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        sg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        sg["clip"]["rotation"] = 0.0
        sg["clip"]["alpha"] = 1.0
        sg.update({
            "id": uid(), "material_id": tid,
            "target_timerange": {"start": st_u, "duration": du_u},
            "source_timerange": None,
            "extra_material_refs": [], "common_keyframes": [], "keyframe_refs": [],
        })
        return sg

    # Prevent any cross-subtitle overlap cleanly
    sub_segs = []
    SUB_SORTED = sorted(SUBTITLES, key=lambda x: x[0])
    for i, (t0, t1, txt, hl) in enumerate(SUB_SORTED):
        if i + 1 < len(SUB_SORTED) and t1 > SUB_SORTED[i + 1][0] - 0.034:
            t1 = max(t0 + 0.35, SUB_SORTED[i + 1][0] - 0.034)
        if hl:
            sg = make_native_text(True, t0, t1, txt, 0.0, -0.58, 11.8, COL_WHITE, COL_RED, 0.065)
        else:
            sg = make_native_text(True, t0, t1, txt, 0.0, -0.58, 11.5, COL_RED, COL_WHITE, 0.060)
        sub_segs.append(sg)
    tr_sub = copy.deepcopy(sub_tr_tpl); tr_sub["id"] = uid(); tr_sub["segments"] = sub_segs

    hdr_segs = [
        make_native_text(False, t0, t1, txt, px, py, sz, COL_WHITE, COL_RED, 0.068)
        for t0, t1, txt, px, py, sz in sorted(HEADERS, key=lambda x: x[0])
    ]
    tr_hdr = copy.deepcopy(txt_tr_tpl); tr_hdr["id"] = uid(); tr_hdr["segments"] = hdr_segs

    # Audio Track 1: Warm Acoustic Corporate BGM (1 unbroken file, smooth 1.4s fade-out!)
    bgm_dur_u = us(probe_audio_dur(BGM_PATH))
    bgm_aid = uid()
    bgm_mat = copy.deepcopy(amat_tpl)
    bgm_mat.update({
        "id": bgm_aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
        "name": BGM_PATH.stem, "path": norm_fwd(BGM_PATH), "duration": bgm_dur_u, "type": "music",
    })
    D["materials"]["audios"].append(bgm_mat)

    bgm_seg = copy.deepcopy(aseg_tpl)
    bgm_refs = []
    for k, tpl_e in a_extra_tpl.items():
        em = copy.deepcopy(tpl_e); em["id"] = uid()
        if k == "speeds": em["speed"] = 1.0
        D["materials"][k].append(em); bgm_refs.append(em["id"])
    bgm_fade_id = uid()
    D["materials"].setdefault("audio_fades", []).append({
        "fade_in_duration": 400000, "fade_out_duration": 1400000, "fade_type": 0, "id": bgm_fade_id, "type": "audio_fade"
    })
    bgm_refs.append(bgm_fade_id)
    bgm_seg.update({
        "id": uid(), "material_id": bgm_aid,
        "source_timerange": {"start": us(2.0), "duration": min(total_u, bgm_dur_u - us(2.0))},
        "target_timerange": {"start": 0, "duration": min(total_u, bgm_dur_u - us(2.0))},
        "speed": 1.0, "volume": 0.22, "last_nonzero_volume": 0.22,
        "extra_material_refs": bgm_refs, "common_keyframes": [], "keyframe_refs": [],
    })
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = [bgm_seg]

    # Audio Tracks 2+: Ear-Verified Tactile SFX
    sfx_cache = {}
    sfx_lanes: list[list[dict]] = []
    for t0, fn, lbl, vol, mdur in sorted(SFX_SPEC, key=lambda x: x[0]):
        sp = SFX_DIR / fn
        if not sp.is_file():
            raise FileNotFoundError(f"Missing SFX: {sp}")
        fwd = norm_fwd(sp)
        if fwd not in sfx_cache:
            du_full = us(probe_audio_dur(sp))
            aid = uid()
            am = copy.deepcopy(amat_tpl)
            am.update({
                "id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
                "name": lbl, "path": fwd, "duration": du_full, "type": "sound",
            })
            D["materials"]["audios"].append(am)
            sfx_cache[fwd] = (aid, du_full)
        aid, du_full = sfx_cache[fwd]
        du = min(du_full, us(mdur))
        sg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, tpl_e in a_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        fid = uid()
        D["materials"].setdefault("audio_fades", []).append({
            "fade_in_duration": min(18000, du // 6), "fade_out_duration": min(120000, du // 3),
            "fade_type": 0, "id": fid, "type": "audio_fade",
        })
        refs.append(fid)
        st_u = max(0, us(t0))
        sg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": 0, "duration": du},
            "target_timerange": {"start": st_u, "duration": du},
            "speed": 1.0, "volume": vol, "last_nonzero_volume": vol,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        placed = False
        for ln in sfx_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                ln.append(sg); placed = True; break
        if not placed:
            sfx_lanes.append([sg])

    sfx_tracks = []
    for ln in sfx_lanes:
        ta = copy.deepcopy(atrack_tpl); ta["id"] = uid(); ta["segments"] = ln
        sfx_tracks.append(ta)

    # Assemble clean tracks
    D["id"] = uid()
    D["tracks"] = [tr_v0, tr_v1, tr_v2, tr_sub, tr_hdr, tr_bgm, *sfx_tracks]
    D["duration"] = total_u
    D["update_time"] = now_s
    D["create_time"] = now_s
    D["canvas_config"] = {"width": W, "height": H, "ratio": "9:16", "background": None}

    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video":
                s["render_index"] = ti
            elif tr["type"] == "text":
                s["render_index"] = 14000 + ti

    # Create fresh CapCut Draft Directory cleanly!
    if DRAFT_DIR.exists():
        shutil.rmtree(DRAFT_DIR)
    new_tl_id = uid()
    (DRAFT_DIR / "Timelines" / new_tl_id).mkdir(parents=True, exist_ok=True)
    for sub in ("adjust_mask", "matting", "qr_upload", "Resources", "subdraft", "common_attachment"):
        (DRAFT_DIR / sub).mkdir(exist_ok=True)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for tp in [
        DRAFT_DIR / "draft_content.json",
        DRAFT_DIR / "template-2.tmp",
        DRAFT_DIR / "Timelines" / new_tl_id / "draft_content.json",
        DRAFT_DIR / "Timelines" / new_tl_id / "template-2.tmp",
    ]:
        tp.write_bytes(dc_bytes)

    # Write draft_meta_info.json
    dmi = json.loads((TPL_1117 / "draft_meta_info.json").read_text(encoding="utf-8"))
    draft_uuid = uid()
    dmi["draft_id"] = draft_uuid
    dmi["draft_name"] = DRAFT_NAME
    dmi["draft_fold_path"] = norm_fwd(DRAFT_DIR)
    dmi["draft_root_path"] = norm_fwd(CC_ROOT)
    dmi["draft_timeline_materials_size_"] = 0
    dmi["tm_duration"] = total_u
    dmi["tm_draft_create"] = now_us
    dmi["tm_draft_modified"] = now_us
    for bucket in dmi.get("draft_materials", []):
        if bucket.get("type") == 0:
            bucket["value"] = new_dm_entries
        else:
            bucket["value"] = []
    (DRAFT_DIR / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    # Write Timelines/project.json + copy auxiliary meta files
    pj = copy.deepcopy(pj_tpl)
    pj["main_timeline_id"] = new_tl_id
    pj["create_time"] = now_us
    pj["update_time"] = now_us
    pj["timelines"] = [{
        "id": new_tl_id, "name": "Timeline 01", "create_time": now_us, "update_time": now_us, "is_deleted": False
    }]
    (DRAFT_DIR / "Timelines" / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    for aux in ("draft_agency_config.json", "draft_biz_config.json", "draft_settings", "draft_virtual_store.json", "key_value.json"):
        src_aux = TPL_1117 / aux
        if src_aux.exists():
            shutil.copy2(src_aux, DRAFT_DIR / aux)

    # Extract clean cover thumbnail from C3925 handshake!
    cover_jpg = DRAFT_DIR / "draft_cover.jpg"
    subprocess.run(["ffmpeg","-y","-v","error","-ss","21.2","-i",str(AH_DIR/"C3925.MP4"),"-frames:v","1","-update","1","-vf","scale=540:960",str(cover_jpg)], check=True)

    # Register cleanly in root_meta_info.json (without disturbing any other drafts!)
    rmi_path = CC_ROOT / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_NAME]
    tpl_entry = copy.deepcopy(next(x for x in store if x.get("draft_name") == "1117 F20"))
    tpl_entry.update({
        "draft_id": draft_uuid,
        "draft_name": DRAFT_NAME,
        "draft_fold_path": norm_fwd(DRAFT_DIR),
        "draft_json_file": norm_fwd(DRAFT_DIR / "draft_content.json"),
        "draft_cover": norm_fwd(cover_jpg),
        "draft_root_path": norm_fwd(CC_ROOT),
        "tm_duration": total_u,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
    })
    store.insert(0, tpl_entry)
    rmi["all_draft_store"] = store
    rmi["draft_ids"] = len(store)
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    # ==========================================================================
    # STRUCTURAL AUDIT + 12-FRAME VISUAL QC CONTACT SHEET!
    # ==========================================================================
    vmap = {v["id"]: v for v in D["materials"]["videos"]}
    for s in tr_v0["segments"] + tr_v1["segments"]:
        assert s["clip"]["scale"] == {"x": 1.0, "y": 1.0}, "Non-1.0 scale on raw video!"
        assert s["clip"]["transform"] == {"x": 0.0, "y": 0.0}, "Non-zero pan on raw video!"
        assert s["common_keyframes"] == [], "Unexpected keyframes on raw video!"
        assert vmap[s["material_id"]]["crop"] == FULL_CROP_1_1, "Crop bug detected!"
    for s in tr_v2["segments"]:
        vm = vmap[s["material_id"]]
        assert (vm["width"], vm["height"]) == (W, H), "Circle PNG not 1080x1920!"
        assert vm["crop"] == FULL_CROP_1_1, "Crop bug on circle!"
    for t in D["materials"]["texts"]:
        assert t["check_flag"] == 15, f"check_flag != 15 on {t['recognize_text']}"

    print("\n[PASS ALL STRUCTURAL CHECKS!]")
    print(f"  -> CapCut Draft created: {DRAFT_DIR}")
    print(f"  -> Track 0: {len(tr0_segs)} raw segments ({total_s:.2f}s)")
    print(f"  -> Track 1: {len(tr1_segs)} untouched 9:16 B-rolls (scale=1.0, pos=(0,0), 0 keyframes)")
    print(f"  -> Track 2: {len(tr2_segs)} clean round 1080x1920 circular badges (0% handle, 0% AI)")
    print(f"  -> Track 3+4: {len(sub_segs)} subtitles + {len(hdr_segs)} headers (100% Native Coiny, check_flag=15)")
    print(f"  -> Audio: 1 unbroken warm acoustic BGM + {len(SFX_SPEC)} ear-verified SFX")

    # Render 12-frame composite QC sheet directly from the CapCut JSON!
    qc_times = [
        1.8,                                      # Doorway intro + Header
        15.8,                                     # Handshake!
        21.0,                                     # Q1 Oanh + Chapter 01
        46.8,                                     # A1 Yến + Circle 01 on sky-blue wall!
        60.0,                                     # B-roll C3869 + YẾN THỦ CÔNG header
        70.8,                                     # A1 Rong biển + Circle 02!
        118.8,                                    # A2 Giỏ Mica Trong + Show Hết!
        142.0,                                    # A3 Tối giản + Header
        150.5,                                    # A3 4 items + Circle Yến Sào
        175.0,                                    # Gift box intro + Quà Tri Ân Thầy Hậu
        200.5,                                    # Anh Hậu cảm ơn sách (tan chảy siêu thích!)
        total_s - 1.2,                            # F20 Brand Closing Banner!
    ]
    fnt_sub = ImageFont.truetype(COINY_FONT_PATH, 46)
    fnt_hdr = ImageFont.truetype(COINY_FONT_PATH, 50)
    fnt_lbl = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 22)

    cols, rows = 4, 3
    tw, th = 360, 640
    sheet = Image.new("RGB", (cols * tw, rows * (th + 28)), (18, 20, 24))
    sdr = ImageDraw.Draw(sheet)

    def render_frame_at(t_s: float):
        tu = us(t_s)
        # Active video on Track 1 or Track 0
        active_seg = None
        for tr_v in (tr_v1, tr_v0):
            for s in tr_v["segments"]:
                st, du = s["target_timerange"]["start"], s["target_timerange"]["duration"]
                if st <= tu < st + du:
                    active_seg = s; break
            if active_seg: break
        vm = vmap[active_seg["material_id"]]
        src_t = (active_seg["source_timerange"]["start"] + (tu - active_seg["target_timerange"]["start"]) * active_seg["speed"]) / 1e6
        tmp_f = WORK / "_qc_tmp.jpg"
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{src_t:.3f}","-i",vm["path"],"-frames:v","1","-update","1","-vf",f"scale={W}:{H}",str(tmp_f)], check=True)
        canvas = Image.open(tmp_f).convert("RGBA")
        tmp_f.unlink()

        # Composite active Circle Overlay (Track 2)
        for s in tr_v2["segments"]:
            st, du = s["target_timerange"]["start"], s["target_timerange"]["duration"]
            if st <= tu < st + du:
                cm = vmap[s["material_id"]]
                ov = Image.open(cm["path"]).convert("RGBA")
                sc = s["clip"]["scale"]["x"]
                nw, nh = int(round(W * sc)), int(round(H * sc))
                ov = ov.resize((nw, nh), Image.Resampling.LANCZOS)
                cx = int(round((s["clip"]["transform"]["x"] + 1.0) * 0.5 * W))
                cy = int(round((1.0 - s["clip"]["transform"]["y"]) * 0.5 * H))
                canvas.alpha_composite(ov, (cx - nw // 2, cy - nh // 2))

        # Draw active Native Texts (Headers + Subtitles)
        tmap_all = {t["id"]: t for t in D["materials"]["texts"]}
        dr = ImageDraw.Draw(canvas)
        for tr_t, is_hdr in ((tr_hdr, True), (tr_sub, False)):
            for s in tr_t["segments"]:
                st, du = s["target_timerange"]["start"], s["target_timerange"]["duration"]
                if st <= tu < st + du:
                    tm = tmap_all[s["material_id"]]
                    txt = tm["recognize_text"]
                    cobj = json.loads(tm["content"])
                    fcol = tuple(int(round(c * 255)) for c in cobj["styles"][0]["fill"]["content"]["solid"]["color"])
                    scol = tuple(int(round(c * 255)) for c in cobj["styles"][0]["strokes"][0]["content"]["solid"]["color"])
                    cx = int(round((s["clip"]["transform"]["x"] + 1.0) * 0.5 * W))
                    cy = int(round((1.0 - s["clip"]["transform"]["y"]) * 0.5 * H))
                    fnt = fnt_hdr if is_hdr else fnt_sub
                    bb = dr.multiline_textbbox((0, 0), txt, font=fnt, stroke_width=7, align="center")
                    tw_t, th_t = bb[2] - bb[0], bb[3] - bb[1]
                    dr.multiline_text((cx - tw_t // 2, cy - th_t // 2), txt, font=fnt, fill=fcol,
                                      stroke_width=7, stroke_fill=scol, align="center")
        return canvas.convert("RGB").resize((tw, th), Image.Resampling.LANCZOS), Path(vm["path"]).name

    for idx, ts in enumerate(qc_times):
        img, src_nm = render_frame_at(ts)
        r, c = divmod(idx, cols)
        x0, y0 = c * tw, r * (th + 28)
        sheet.paste(img, (x0, y0 + 28))
        sdr.text((x0 + 6, y0 + 4), f"t={ts:05.1f}s | {src_nm[:20]}", font=fnt_lbl, fill=(240, 235, 160))

    qc_out = WORK / "qc_dkedu_master_12.jpg"
    sheet.save(qc_out, quality=90)
    print(f"  -> Saved 12-frame Visual Master QC Sheet: {qc_out}")


if __name__ == "__main__":
    main()
