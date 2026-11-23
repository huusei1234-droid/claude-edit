import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30.0

CC_ROOT     = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME  = "261121 F20 Phỏng Vấn Đăng Khoa Edu"
DRAFT_DIR   = CC_ROOT / DRAFT_NAME

# Read user's ACTUAL FINISHED `1117 F20` (2026-11-19 20:21) as exact style & effect DNA source!
D1117_DIR   = CC_ROOT / "1117 F20"
WORK_1117   = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
CIRCLE_DIR  = WORK_1117 / "v7_assets" / "circle_overlays"
BANNER_MP4  = WORK_1117 / "v7_assets" / "outro_banner_f20_brand.mp4"  # 0% AI (pure studio gradient + real basket photo + official logos)

F20_261116  = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116")
AH_DIR      = F20_261116 / "Anh Hậu"
DOC_DIR     = F20_261116 / r"Chi Oanh\dọc"
DJI_DIR     = F20_261116 / r"Chi Oanh\dji"

BGM_F20     = Path(r"D:\AI\full studio\edit\nhạc nền\Nhạc Sáo Trúc Đàn Tranh Gốc F20 - Bản Dài Sạch Lỗi (2p13s).mp3")
SFX_DIR     = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")
CC_POP_SFX  = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\6238aa6c3491fbc9af81e0e8afcb5931.mp3")
CC_WSH_SFX  = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music\7785b04dd58d6f7a816e7d9744448ae5.mp3")

WORK        = Path(r"d:\AI\full studio\output\f20-phong-van-dang-khoa-edu")
ARCHIVE_DIR = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-phong-van-dang-khoa-edu")

FULL_CROP_1_1 = {
    "upper_left_x": 0.0, "upper_left_y": 0.0,
    "upper_right_x": 1.0, "upper_right_y": 0.0,
    "lower_left_x": 0.0, "lower_left_y": 1.0,
    "lower_right_x": 1.0, "lower_right_y": 1.0,
}

COINY_FONT_ID   = "7482665772876156165"
COINY_FONT_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"

# Exact colors from user's finalized 1117 F20!
COL_RED       = [0.9254902005195618, 0.11372549086809158, 0.11372549086809158]
COL_WHITE     = [1.0, 1.0, 1.0]
COL_F20_GREEN = [0.0, 0.70, 0.04]   # User's exact F20 Emerald Green from 1117 F20 Track 9!

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
# 1. TRACK 0 — MASTER DIALOGUE SPINE (100% RAW ORIGINAL 9:16, ZERO AI)
# (id, path, src_in, src_out, speed, vol_cc, add_ket_hop_transition_after)
# ==============================================================================
TRACK0_SPEC = [
    # HỒI 1: Cửa phòng báo ship hàng đến nơi -> Pan 77 set quà -> Bước vào bắt tay Anh Hậu
    ("01_doorway",     AH_DIR / "C3925.MP4",   1.70,  14.35, 1.05, 1.15, True),
    ("02_room_pan",    DOC_DIR / "C3908.MP4",  0.80,   2.30, 1.00, 0.00, False),
    ("03_handshake",   AH_DIR / "C3925.MP4",  18.75,  23.30, 1.00, 1.35, True),

    # HỒI 2: Phỏng vấn phần 1 — Lý do Đăng Khoa Edu chọn F20
    ("04_q1_oanh",     AH_DIR / "C3926.MP4",   5.75,  15.55, 1.05, 1.15, False),
    ("05_a1_reason",   AH_DIR / "C3926.MP4",  16.90,  22.95, 1.05, 1.80, False),
    ("06_a1_quality",  AH_DIR / "C3926.MP4",  23.50,  33.80, 1.05, 1.80, False),
    ("07a_a1_used",    AH_DIR / "C3926.MP4",  35.15,  45.20, 1.05, 1.80, False),
    ("07b_a1_ngon",    AH_DIR / "C3926.MP4",  53.85,  56.10, 1.05, 1.80, False),
    ("08_a1_handmade", AH_DIR / "C3926.MP4",  57.85,  69.05, 1.05, 1.80, False),
    ("09_a1_seaweed",  AH_DIR / "C3926.MP4",  69.75,  79.85, 1.05, 1.80, False),
    ("10_a1_energy",   AH_DIR / "C3926.MP4",  86.75,  98.10, 1.05, 1.80, False),

    # HỒI 3: Phỏng vấn phần 2 — Cảm nhận cầm 77 set quà hoàn thiện trên tay
    ("11_q2_oanh",     AH_DIR / "C3926.MP4", 108.00, 116.50, 1.05, 1.15, False),
    ("12_a2_happy",    AH_DIR / "C3926.MP4", 133.20, 142.55, 1.05, 1.80, False),
    ("13_a2_handle",   AH_DIR / "C3926.MP4", 143.15, 149.15, 1.05, 1.80, False),
    ("14_a2_mica",     AH_DIR / "C3926.MP4", 150.20, 165.40, 1.05, 1.55, False),

    # HỒI 4: Phỏng vấn phần 3 — Tối giản tập trung chất lượng & điểm tên 4 món
    ("15_q3_consult",  AH_DIR / "C3926.MP4", 187.55, 198.90, 1.05, 1.15, False),
    ("16_a3_minimal",  AH_DIR / "C3926.MP4", 204.90, 212.80, 1.05, 1.80, False),
    ("17_a3_4items",   AH_DIR / "C3926.MP4", 213.35, 233.35, 1.05, 1.80, True),

    # HỒI 5: Chị Oanh tặng quà nhỏ (Hộp Quà Sách) & Anh Hậu cảm ơn sách
    ("18_gift_intro",  AH_DIR / "C3932.MP4",   2.60,  16.45, 1.05, 1.15, False),
    ("19_gift_give",   AH_DIR / "C3932.MP4",  47.65,  51.35, 1.05, 1.35, False),
    ("20_book1",       AH_DIR / "C3932.MP4",  63.80,  74.05, 1.05, 1.15, False),
    ("21_book2a",      AH_DIR / "C3932.MP4",  78.60,  84.70, 1.05, 1.15, False),
    ("22_book2b",      AH_DIR / "C3932.MP4",  91.40,  96.25, 1.05, 1.15, False),
    ("23_hau_thanks",  AH_DIR / "C3932.MP4", 122.40, 130.00, 1.05, 1.80, True),

    # HỒI 6: Chị Oanh cảm ơn & CTA liên hệ đặt quà 20/11 + Banner kết F20 (0% AI, giống hệt 1117 F20!)
    ("24_oanh_cta",    DOC_DIR / "C3864.MP4",  5.15,  19.30, 1.05, 1.20, False),
]


def compute_timeline():
    cur_u = 0
    segs = {}
    seg_list = []
    for cid, path, sin, sout, spd, vol, has_tr in TRACK0_SPEC:
        dur_s = (sout - sin) / spd
        du_u = us(dur_s)
        item = {
            "id": cid, "path": str(path), "src_in": sin, "src_out": sout,
            "speed": spd, "vol": vol, "has_tr": has_tr,
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


def wrap_sub(text: str, max_chars: int = 27) -> str:
    if "\n" in text or len(text) <= max_chars:
        return text
    words = text.split()
    best_i, best_diff = 1, 999
    for i in range(1, len(words)):
        diff = abs(len(" ".join(words[:i])) - len(" ".join(words[i:])))
        if diff < best_diff:
            best_diff, best_i = diff, i
    return " ".join(words[:best_i]) + "\n" + " ".join(words[best_i:])


def main():
    if DRAFT_DIR.exists() and (DRAFT_DIR / ".locked").exists():
        raise RuntimeError(f"'{DRAFT_NAME}' is currently open/locked in CapCut! Please exit to CapCut Home Screen first.")

    # Load user's FINISHED 1117 F20 (2026-11-19 20:21) to clone exact templates, animations, filter & transitions!
    pj_1117 = json.loads((D1117_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
    sub_1117 = D1117_DIR / "Timelines" / pj_1117["main_timeline_id"]
    dc1117_p = sub_1117 / "template-2.tmp" if (sub_1117 / "template-2.tmp").exists() and (sub_1117 / "template-2.tmp").stat().st_mtime >= (sub_1117 / "draft_content.json").stat().st_mtime else sub_1117 / "draft_content.json"
    D1117 = json.loads(dc1117_p.read_text(encoding="utf-8"))
    D = copy.deepcopy(D1117)
    dm_1117 = json.loads((D1117_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))

    VIDEO_ANIMS   = json.loads((WORK_1117 / "verified_video_anims.json").read_text(encoding="utf-8"))
    COLOR_SLIDERS = json.loads((WORK_1117 / "native_color_sliders.json").read_text(encoding="utf-8"))

    # Extract user's EXACT Text Animation objects, Filter (`Sống động 2`) & Transition (`Kết hợp`) from 1117 F20!
    TEXT_ANIMS = {"in": {}, "out": {}, "loop": {}}
    for ma in D1117["materials"].get("material_animations", []):
        for a in ma.get("animations", []):
            if a.get("panel") == "text" or a.get("material_type") == "sticker" or a.get("name") in ("Mờ", "Mờ dần", "Trượt sang phải", "Trượt sang trái", "Chao đảo ngẫu nhiên", "Chữ mờ dần hiện vào"):
                tp, nm = a.get("type"), a.get("name")
                if tp in TEXT_ANIMS and nm and nm not in TEXT_ANIMS[tp]:
                    TEXT_ANIMS[tp][nm] = copy.deepcopy(a)

    KET_HOP_TPL = copy.deepcopy(next(tr for tr in D1117["materials"].get("transitions", []) if tr.get("name") == "Kết hợp"))
    FILTER_TRACK_TPL = copy.deepcopy(next(t for t in D1117["tracks"] if t.get("type") == "filter" and t.get("segments")))
    FILTER_MAT_TPL   = copy.deepcopy(next(e for e in D1117["materials"]["effects"] if e["id"] == FILTER_TRACK_TPL["segments"][0]["material_id"]))

    vtrack_tpl = copy.deepcopy(D1117["tracks"][0])
    vseg_tpl   = copy.deepcopy(D1117["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(next(m for m in D1117["materials"]["videos"] if m.get("type") == "video"))
    pmat_tpl   = copy.deepcopy(next(m for m in D1117["materials"]["videos"] if m.get("type") == "photo"))
    dm_all_1117 = [x for g in dm_1117.get("draft_materials", []) for x in g.get("value", [])]
    dm_vid_tpl = copy.deepcopy(next(x for x in dm_all_1117 if x.get("metetype") == "video"))
    dm_pho_tpl = copy.deepcopy(next((x for x in dm_all_1117 if x.get("metetype") == "photo"), dm_vid_tpl))

    atrack_tpl = copy.deepcopy(next(t for t in D1117["tracks"] if t.get("type") == "audio" and t.get("segments")))
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl   = copy.deepcopy(D1117["materials"]["audios"][0])

    tmap_1117   = {t["id"]: t for t in D1117["materials"]["texts"]}
    sub_tr_tpl  = copy.deepcopy(next(t for t in D1117["tracks"] if t.get("type") == "text" and t.get("segments") and tmap_1117.get(t["segments"][0]["material_id"], {}).get("type") == "subtitle"))
    txt_tr_tpl  = copy.deepcopy(next(t for t in D1117["tracks"] if t.get("type") == "text" and t.get("segments") and tmap_1117.get(t["segments"][0]["material_id"], {}).get("type") == "text"))
    sub_seg_tpl = copy.deepcopy(sub_tr_tpl["segments"][0])
    sub_mat_tpl = copy.deepcopy(tmap_1117[sub_seg_tpl["material_id"]])
    txt_seg_tpl = copy.deepcopy(txt_tr_tpl["segments"][0])
    txt_mat_tpl = copy.deepcopy(tmap_1117[txt_seg_tpl["material_id"]])

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {
        k: copy.deepcopy(next(x for x in D1117["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"]))
        for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in D1117["materials"].get(k, []))
    }
    a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {
        k: copy.deepcopy(next(x for x in D1117["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"]))
        for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in D1117["materials"].get(k, []))
    }

    # Reset materials cleanly
    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = []

    seg_list, S, speech_end_u = compute_timeline()
    banner_dur_u = us(2.60)
    total_u      = speech_end_u + banner_dur_u
    total_s      = total_u / 1e6
    speech_end_s = speech_end_u / 1e6

    def tmap(cid: str, s0: float, s1: float) -> tuple[float, float]:
        return (src_to_tl(S[cid], s0), src_to_tl(S[cid], s1))

    # ==========================================================================
    # 2. TRACK 1 — 18 CONTEXT-PERFECT RAW 9:16 B-ROLLS (100% REAL 261116 FOOTAGE, ZERO MISMATCHES!)
    #    Every single clip verified visually by our own eyes from broll_pool_vertical_sheet.jpg + extra_vertical_products_sheet.jpg!
    #    All untouched scale=1.0, pos=(0,0), 0 keyframes!
    # ==========================================================================
    BROLL_SPEC = [
        # (tl_t0, tl_t1, path, src_in, speed, in_anim, out_anim, is_dji, note)
        # Hồi 1: Giữ Chị Oanh trước cửa 3.05s mở đầu -> Bốc quà từ cốp xe (góc sạch không biển quán) -> Bày lên bàn tại ĐK Edu -> Pan 77 set quà!
        (*tmap("01_doorway", 4.90, 7.00),       DOC_DIR / "C3903.MP4",  18.00, 1.00, None, None, False, "Chị Oanh & nhân viên F20 chuyển 77 set quà từ xe"),
        (*tmap("01_doorway", 7.00, 8.95),       DOC_DIR / "C3914.MP4",   3.00, 1.00, None, None, False, "Nhân viên F20 bày 77 set quà lên bàn tại ĐK Edu"),
        (*tmap("01_doorway", 8.95, 10.60),      DOC_DIR / "C3909.MP4",   1.50, 1.00, None, None, False, "Pan mượt cận 77 set quà đã xếp sẵn tại ĐK Edu"),

        # Hồi 2 (Q1 Lý do chọn F20):
        (*tmap("05_a1_reason", 18.20, 21.40),   DOC_DIR / "C3910.MP4",   0.80, 0.90, None, None, False, "Toàn cảnh 77 set quà trên bàn Đăng Khoa Edu"),
        (*tmap("06_a1_quality", 28.50, 32.50),  AH_DIR  / "C3920.MP4",   1.20, 0.95, None, None, False, "Anh Hậu & Chị Oanh kiểm tra chất lượng từng set quà"),
        # Cover 07a -> 07b jump-cut smoothly with CRYSTAL-CLEAR DJI close-up of Set Quà (Yến Sào SKANEST + Rong Biển + Bánh Hạt!)
        (src_to_tl(S["07a_a1_used"], 42.20), src_to_tl(S["07b_a1_ngon"], 56.00),
         DJI_DIR / "DJI_20261116093228_0082_D.MP4", 2.00, 0.95, None, None, True, "Cận trực diện Set Quà: Tổ Yến SKANEST, Rong Biển, Bánh Hạt"),
        # "F20 làm yến thủ công hết, không hóa chất... gia đình dùng, tặng bạn bè cũng khen":
        (*tmap("08_a1_handmade", 60.80, 64.20), DOC_DIR / "C3866.MP4",   6.00, 1.00, None, None, False, "Đội ngũ F20 thắt nơ hoàn thiện từng set quà thủ công tỉ mỉ"),
        # Cover 09 -> 10 jump-cut ("rong biển với bánh hạt... không kịp ăn sáng, ăn 1-2 cái tiếp năng lượng") with REAL Rong Biển & Bánh Hạt close-up!
        (src_to_tl(S["09_a1_seaweed"], 77.20), src_to_tl(S["09_a1_seaweed"], 79.85),
         DJI_DIR / "DJI_20261116093322_0084_D.MP4", 48.00, 1.00, None, None, True, "Cận trực diện Rong Biển Kẹp Hạt & Hộp Rong Biển Tuệ Tâm"),
        (src_to_tl(S["10_a1_energy"], 86.75), src_to_tl(S["10_a1_energy"], 89.80),
         DOC_DIR / "C3873.MP4", 1.00, 0.90, None, None, False, "Cận dàn set quà đầy ắp rong biển, bánh thuyền, tổ yến"),

        # Hồi 3 (Q2 Cảm nhận 77 set quà trên tay):
        (*tmap("11_q2_oanh", 108.40, 112.00),   AH_DIR  / "C3922.MP4",   8.50, 1.00, None, None, False, "Anh Hậu & Chị Oanh nâng niu xem thành phẩm trước 77 set quà"),
        (*tmap("12_a2_happy", 134.50, 137.50),  DOC_DIR / "C3917.MP4",   1.50, 1.00, None, None, False, "77 set quà xếp hàng ngay ngắn trên thảm đỏ Đăng Khoa Edu"),
        # "chất liệu mica trong... nhìn thấy không giấu giếm gì hết, show hết luôn!":
        (*tmap("14_a2_mica", 153.20, 156.80),   DJI_DIR / "DJI_20261116093255_0083_D.MP4", 4.00, 0.95, None, None, True, "Cận xoay giỏ Mica trong suốt & quai xách da đỏ đô khoe trọn 4 món"),

        # Hồi 4 (Q3 Tối giản tập trung chất lượng):
        (*tmap("15_q3_consult", 188.60, 191.80),DJI_DIR / "DJI_20261116110956_0104_D.MP4", 0.60, 1.00, None, None, True, "Góc DJI Chị Oanh trực tiếp kiểm tra set quà tại ĐK Edu"),
        (*tmap("15_q3_consult", 191.80, 194.60),DOC_DIR / "C3918.MP4",   1.00, 1.00, None, None, False, "Chị Oanh chăm chút căn chỉnh ngay ngắn từng set quà"),

        # Hồi 5 (Tặng hộp quà sách 20/11):
        (src_to_tl(S["18_gift_intro"], 13.80), src_to_tl(S["18_gift_intro"], 16.45),
         AH_DIR / "C3921.MP4", 1.20, 1.00, None, None, False, "Anh Hậu & Chị Oanh trò chuyện thân tình trước khi trao quà sách"),

        # Hồi 6 (Chị Oanh cảm ơn & CTA đặt hàng + Banner F20 tone chuẩn 0% AI!):
        (*tmap("24_oanh_cta", 13.50, 17.20),    DOC_DIR / "C3875.MP4",   1.50, 0.90, "Rõ dần", "Mờ dần", False, "Dãy set quà 20/11 F20 sẵn sàng giao ngay"),
    ]

    # ==========================================================================
    # 3. TRACK 2 — CLEAN ROUND CIRCULAR PRODUCT OVERLAYS (`circle_*.png`, 1080x1920, 0% handle, 0% AI)
    #    Larger & clearer (sc=0.46..0.52) like user's finished 1117 F20, centered cleanly in open sky-blue gap (+0.08, +0.34)!
    # ==========================================================================
    CIRCLE_SPEC = [
        # (tl_t0, tl_t1, png_name, px, py, sc, mini_label)
        (*tmap("07a_a1_used",    38.60, 42.15), "circle_01_to_yen_a5.png",      +0.08, +0.43, 0.46, "YẾN SÀO SKANEST"),
        (*tmap("08_a1_handmade", 58.10, 60.75), "circle_01_to_yen_a5.png",      +0.08, +0.43, 0.46, "YẾN THỦ CÔNG 100%"),
        (*tmap("09_a1_seaweed",  70.50, 73.70), "circle_02_2hop_rong_bien.png", +0.08, +0.43, 0.46, "RONG BIỂN TUỆ TÂM"),
        (*tmap("09_a1_seaweed",  73.85, 77.10), "circle_03_banh_thuyen.png",    +0.08, +0.43, 0.46, "BÁNH THUYỀN MIX HẠT"),
        # 5 items named one-by-one by Anh Hậu while pointing inside the basket!
        (*tmap("17_a3_4items",  213.55, 216.15), "circle_02_2hop_rong_bien.png",+0.08, +0.43, 0.46, "01 • RONG BIỂN"),
        (*tmap("17_a3_4items",  216.25, 219.50), "circle_01_to_yen_a5.png",     +0.08, +0.43, 0.46, "02 • YẾN SÀO CAO CẤP"),
        (*tmap("17_a3_4items",  219.60, 222.95), "circle_08_duong_phen.png",    +0.08, +0.43, 0.46, "03 • ĐƯỜNG PHÈN"),
        (*tmap("17_a3_4items",  223.05, 226.85), "circle_03_banh_thuyen.png",   +0.08, +0.43, 0.46, "04 • BÁNH THUYỀN"),
        (*tmap("17_a3_4items",  226.95, 230.50), "circle_04_kep_hat_500g.png",  +0.08, +0.43, 0.46, "05 • RONG BIỂN KẸP HẠT"),
    ]

    # ==========================================================================
    # 4. NATIVE CAPCUT SUBTITLES (`Coiny`, Red + White stroke, check_flag=15 — identical to 1117 F20!)
    # ==========================================================================
    SUB_RAW = [
        (*tmap("01_doorway", 1.75, 4.55),  "Bên Oanh đã chuẩn bị xong 77 set quà", 12.2),
        (*tmap("01_doorway", 4.60, 7.35),  "giao tới văn phòng Đăng Khoa Edu", 11.8),
        (*tmap("01_doorway", 7.40, 10.10), "tại 23 Thái Nguyên rồi nhé mọi người!", 11.8),
        (*tmap("01_doorway", 10.20, 14.25),"Giờ cùng Oanh vào giao quà cho anh Hậu nhé!", 11.8),
        (*tmap("03_handshake", 18.85, 20.15),"Xin chào anh Hậu ạ!", 14.0),
        (*tmap("03_handshake", 20.20, 23.15),"Chào em, chào Oanh F20!", 14.5),

        (*tmap("04_q1_oanh", 5.80, 8.55),  "Vì sao năm nay Đăng Khoa Edu", 12.0),
        (*tmap("04_q1_oanh", 8.60, 11.45), "chọn sản phẩm của Thực phẩm F20", 12.2),
        (*tmap("04_q1_oanh", 11.50, 15.45),"làm quà tri ân thầy cô dịp 20/11 ạ?", 11.8),
        (*tmap("05_a1_reason", 16.95, 22.85),"Thầy cô Đăng Khoa Edu đã có nhiều\nđóng góp rất là tuyệt vời", 11.8),
        (*tmap("06_a1_quality", 23.55, 28.10),"Hậu muốn gửi lời cảm ơn đến thầy cô,", 11.8),
        (*tmap("06_a1_quality", 28.20, 33.70),"muốn có một chút quà — nhưng phải chất lượng!", 12.2),
        (*tmap("07a_a1_used", 35.20, 39.20), "Ở F20, bản thân Hậu đã dùng rất nhiều rồi", 11.8),
        (*tmap("07a_a1_used", 39.30, 45.15), "từ bánh hạt, yến cho đến yến chưng tươi...", 11.8),
        (*tmap("07b_a1_ngon", 53.90, 56.05), "thấy rất là ngon!", 14.5),
        (*tmap("08_a1_handmade", 57.90, 63.25),"F20 làm yến thủ công hết, không hóa chất!", 12.4),
        (*tmap("08_a1_handmade", 63.40, 69.00),"Gia đình dùng, tặng bạn bè ai cũng khen!", 11.8),
        (*tmap("09_a1_seaweed", 69.80, 73.10),"Đặc biệt rất thích rong biển và bánh hạt", 12.2),
        (*tmap("09_a1_seaweed", 73.25, 79.80),"Giáo viên nhiều khi bận bịu không kịp ăn sáng,", 11.8),
        (*tmap("10_a1_energy", 86.80, 91.45), "ăn 1–2 cái tiếp năng lượng rất là ngon!", 12.0),
        (*tmap("10_a1_energy", 91.55, 98.05), "Rong biển và các loại hạt hoàn toàn thiên nhiên!", 12.0),

        (*tmap("11_q2_oanh", 108.05, 111.20), "Hôm nay giao những set quà tới đây,", 11.8),
        (*tmap("11_q2_oanh", 111.30, 116.45), "anh Hậu chia sẻ cảm nhận khi nhận quà nhé!", 11.8),
        (*tmap("12_a2_happy", 133.25, 138.20),"77 set quà đã tới Đăng Khoa Edu,", 12.5),
        (*tmap("12_a2_happy", 138.30, 142.50),"cầm trên tay cảm thấy rất là ưng ý!", 12.5),
        (*tmap("13_a2_handle", 143.20, 149.10),"Có quai xách tiện tay, cũng dễ thương nữa!", 12.0),
        (*tmap("14_a2_mica", 150.25, 152.75), "Phía dưới đây là mica hả em?", 13.0),
        (*tmap("14_a2_mica", 152.85, 156.00), "Dạ túi giỏ đựng quà chất liệu mica trong ạ!", 11.8),
        (*tmap("14_a2_mica", 156.10, 160.20), "Mica trong luôn — không giấu giếm gì hết!", 12.5),
        (*tmap("14_a2_mica", 160.40, 165.35), "Show hết luôn — cái gì tốt mình khoe hết!", 12.5),

        (*tmap("15_q3_consult", 187.60, 193.55),"Anh Hậu nói muốn set quà tập trung chất lượng,", 11.8),
        (*tmap("15_q3_consult", 193.65, 198.85),"thầy cô dùng bồi bổ sức khỏe và tiện lợi!", 11.8),
        (*tmap("16_a3_minimal", 204.95, 209.60),"Toán học gọi là tối giản để tập trung chất lượng!", 12.2),
        (*tmap("16_a3_minimal", 209.75, 212.75),"Cái gì đơn giản là nghệ thuật hết!", 13.0),
        (*tmap("17_a3_4items", 213.45, 216.10), "Đây là rong biển nè,", 14.0),
        (*tmap("17_a3_4items", 216.25, 219.45), "đây là yến sào cao cấp nè,", 13.5),
        (*tmap("17_a3_4items", 219.60, 222.90), "hộp đường phèn nè,", 14.0),
        (*tmap("17_a3_4items", 223.05, 226.80), "bánh thuyền mix hạt nè,", 13.5),
        (*tmap("17_a3_4items", 226.95, 229.00), "rong biển kẹp hạt nè!", 14.0),
        (*tmap("17_a3_4items", 229.10, 233.30), "Những món rất hợp với thầy cô giáo — tuyệt vời!", 12.0),

        (*tmap("18_gift_intro", 2.70, 8.60),   "Hôm nay đến giao quà cho Đăng Khoa Edu,", 11.8),
        (*tmap("18_gift_intro", 8.70, 16.35),  "F20 có món quà nhỏ tặng thầy Hậu dịp 20/11!", 12.0),
        (*tmap("19_gift_give", 47.70, 49.55),  "Em xin gửi anh món quà nhỏ ạ!", 13.2),
        (*tmap("19_gift_give", 49.65, 51.30),  "Cảm ơn Thực phẩm F20!", 14.5),
        (*tmap("20_book1", 63.85, 67.20),      "Biết anh Hậu là người cực kỳ mê sách,", 12.0),
        (*tmap("20_book1", 67.30, 74.00),      "F20 tặng anh cuốn 'Danh Nhân Thế Giới'!", 12.2),
        (*tmap("21_book2a", 78.65, 84.65),     "Và quyển thứ 2 — vì anh còn là doanh nhân...", 11.8),
        (*tmap("22_book2b", 91.45, 96.20),     "cuốn 'Toán Học Của Thịnh Vượng'!", 13.0),
        (*tmap("23_hau_thanks", 122.50, 125.55),"Tuyệt vời! Cảm ơn Oanh và F20 rất nhiều!", 12.4),
        (*tmap("23_hau_thanks", 125.70, 129.95),"Món quà tan chảy đó — siêu thích luôn!", 13.0),

        (*tmap("24_oanh_cta", 5.20, 10.60),    "Oanh xin cảm ơn quý anh chị đã tin tưởng\nđặt hàng Thực phẩm F20!", 11.8),
        (*tmap("24_oanh_cta", 10.75, 14.70),   "Anh chị cần đặt set quà tặng dịp lễ 20/11", 12.0),
        (*tmap("24_oanh_cta", 14.80, 19.25),   "hãy inbox ngay cho Oanh nhé!", 14.2),
    ]

    # ==========================================================================
    # 5. FLOATING ACCENT & CHAPTER TITLES — CLONING USER'S EXACT `1117 F20` STYLE!
    #    - Opening Hero Title: White fill + Red stroke (`Mờ` / `Mờ dần`) + Sub-line F20 Emerald Green + White stroke!
    #    - All Section & Punchy Accent Titles: F20 EMERALD GREEN `[0.0, 0.70, 0.04]` + WHITE STROKE `[1, 1, 1]`
    #      with user's exact animations (`Mờ`, `Trượt sang phải`/`Trượt sang trái`, `Chao đảo ngẫu nhiên`, `Mờ dần`)!
    # ==========================================================================
    # (tl_t0, tl_t1, text, px, py, size, is_white_red, anim_in, anim_out, anim_loop)
    FLOATING_TEXTS = [
        (0.20, 4.40,  "GIAO 77 SET QUÀ 20/11",         0.00, +0.63, 13.8, True,  "Mờ",                  "Mờ dần", None),
        (0.45, 4.40,  "THỰC PHẨM F20 × ĐĂNG KHOA EDU", 0.00, +0.51,  9.6, False, "Chữ mờ dần hiện vào", "Mờ dần", None),
        (S["03_handshake"]["tl_start"] + 0.3, S["03_handshake"]["tl_end"],
         "Anh Hậu • ĐĂNG KHOA EDU",                    0.00, +0.52, 13.2, False, "Mờ",                  "Mờ dần", None),
        (S["04_q1_oanh"]["tl_start"] + 0.2,   S["04_q1_oanh"]["tl_start"] + 4.8,
         "01 • LÝ DO CHỌN F20",                        0.00, +0.51, 14.0, False, "Mờ",                  "Mờ dần", None),
        (S["06_a1_quality"]["tl_start"] + 4.2, S["06_a1_quality"]["tl_end"],
         "QUÀ PHẢI CHẤT LƯỢNG!",                      +0.18, +0.50, 13.6, False, "Trượt sang trái",     "Mờ dần", "Chao đảo ngẫu nhiên"),
        (S["08_a1_handmade"]["tl_start"] + 0.1, S["08_a1_handmade"]["tl_start"] + 5.2,
         "YẾN THỦ CÔNG • KHÔNG HÓA CHẤT",              0.00, +0.62, 12.2, False, "Mờ",                  "Mờ dần", None),
        (S["11_q2_oanh"]["tl_start"] + 0.2,   S["11_q2_oanh"]["tl_start"] + 4.6,
         "02 • CẢM NHẬN THÀNH PHẨM",                   0.00, +0.51, 13.6, False, "Mờ",                  "Mờ dần", None),
        (S["12_a2_happy"]["tl_start"] + 0.2,  S["12_a2_happy"]["tl_start"] + 4.5,
         "77 SET QUÀ • RẤT ƯNG Ý!",                   -0.16, +0.51, 13.6, False, "Trượt sang phải",     "Mờ dần", "Chao đảo ngẫu nhiên"),
        (src_to_tl(S["14_a2_mica"], 156.0),   S["14_a2_mica"]["tl_end"] - 0.1,
         "GIỎ MICA TRONG • SHOW HẾT!",                 0.00, +0.51, 13.2, False, "Mờ",                  "Mờ dần", "Chao đảo ngẫu nhiên"),
        (S["16_a3_minimal"]["tl_start"],      S["16_a3_minimal"]["tl_end"],
         "TỐI GIẢN • TẬP TRUNG CHẤT LƯỢNG",            0.00, +0.51, 11.8, False, "Mờ",                  "Mờ dần", None),
        (S["18_gift_intro"]["tl_start"] + 0.2, S["18_gift_intro"]["tl_start"] + 5.2,
         "QUÀ TRI ÂN THẦY HẬU 20/11",                  0.00, +0.51, 13.2, False, "Mờ",                  "Mờ dần", None),
        (S["20_book1"]["tl_start"] + 3.2,     S["20_book1"]["tl_end"],
         "DANH NHÂN THẾ GIỚI",                         0.00, +0.51, 13.6, False, "Trượt sang trái",     "Mờ dần", None),
        (S["22_book2b"]["tl_start"] + 0.2,    S["22_book2b"]["tl_end"],
         "TOÁN HỌC CỦA THỊNH VƯỢNG",                   0.00, +0.51, 13.0, False, "Trượt sang phải",     "Mờ dần", None),
        (S["23_hau_thanks"]["tl_start"] + 0.2, S["23_hau_thanks"]["tl_end"],
         "MÓN QUÀ TAN CHẢY • SIÊU THÍCH!",             0.00, +0.51, 12.8, False, "Mờ",                  "Mờ dần", "Chao đảo ngẫu nhiên"),
        (src_to_tl(S["24_oanh_cta"], 13.5),   S["24_oanh_cta"]["tl_end"] - 0.1,
         "INBOX OANH NGAY!",                          +0.20, +0.46, 14.2, False, "Trượt sang trái",     "Mờ dần", "Chao đảo ngẫu nhiên"),
    ]
    # Also add clean mini F20 Green+White labels right underneath each circular product badge (100% on sky-blue wall)!
    for t0, t1, _, px, py, _, mlbl in CIRCLE_SPEC:
        FLOATING_TEXTS.append((t0, t1, mlbl, px, py - 0.21, 9.8, False, "Chữ mờ dần hiện vào", "Mờ dần", None))

    # ==========================================================================
    # BUILD MATERIALS & TRACKS
    # ==========================================================================
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

    def attach_dji_sliders(refs: list[str]):
        D["materials"].setdefault("effects", [])
        for stype, sval in [("temperature", 0.14), ("saturation", 0.18), ("contrast", 0.09), ("brightness", 0.03)]:
            ef = copy.deepcopy(COLOR_SLIDERS[stype])
            ef["id"] = uid()
            ef["value"] = float(sval)
            D["materials"]["effects"].append(ef)
            refs.append(ef["id"])

    def make_video_seg(path: Path, tgt_st_u: int, tgt_du_u: int, src_in_s: float, spd: float, vol: float,
                       px: float = 0.0, py: float = 0.0, sc: float = 1.0,
                       in_anim: str | None = None, out_anim: str | None = None,
                       is_dji: bool = False, micro_fade: bool = False, add_ket_hop: bool = False):
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

        if is_dji:
            attach_dji_sliders(refs)

        if micro_fade and vol > 0.0:
            fid = uid()
            D["materials"].setdefault("audio_fades", []).append({
                "fade_in_duration": 33333, "fade_out_duration": 66666, "fade_type": 0, "id": fid, "type": "audio_fade"
            })
            refs.append(fid)

        if add_ket_hop:
            tr_obj = copy.deepcopy(KET_HOP_TPL)
            tr_obj["id"] = uid()
            tr_obj["duration"] = 400000
            D["materials"].setdefault("transitions", []).append(tr_obj)
            refs.append(tr_obj["id"])

        anim_list = []
        if in_anim and in_anim in VIDEO_ANIMS["in"]:
            ai = copy.deepcopy(VIDEO_ANIMS["in"][in_anim])
            ai["start"] = 0
            ai["duration"] = min(200000, tgt_du_u // 4)
            anim_list.append(ai)
        if out_anim and out_anim in VIDEO_ANIMS["out"]:
            ao = copy.deepcopy(VIDEO_ANIMS["out"][out_anim])
            od = min(200000, tgt_du_u // 4)
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

    # Track 0: Main Dialogue Spine (`25` cuts, untouched `scale=1.0`, `Kết hợp` transitions at big shifts!)
    tr0_segs = [
        make_video_seg(
            Path(it["path"]), it["tl_start_u"], it["tl_dur_u"], it["src_in"], it["speed"], it["vol"],
            micro_fade=(it["vol"] > 0.0), add_ket_hop=it["has_tr"]
        )
        for it in seg_list
    ]
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["flag"] = 0; tr_v0["segments"] = tr0_segs

    # Track 1: 16 Context-Perfect Raw 9:16 B-Rolls + Unified F20 Brand Closing Banner (0% AI, matching 1117 F20!)
    tr1_segs = [
        make_video_seg(Path(p), us(t0), us(t1) - us(t0), sin, spd, 0.0, in_anim=ia, out_anim=oa, is_dji=is_dji)
        for t0, t1, p, sin, spd, ia, oa, is_dji, _ in BROLL_SPEC
    ]
    tr1_segs.append(
        make_video_seg(BANNER_MP4, speech_end_u, banner_dur_u, 0.0, 1.0, 0.0,
                       px=0.0, py=-0.05, sc=1.05, in_anim="Rõ dần")
    )
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["flag"] = 2; tr_v1["segments"] = tr1_segs

    # Track 2: 9 Clean Round Circular Product Overlays (`1080x1920`, `FULL_CROP_1_1`, `0%` handle, `0%` AI!)
    tr2_segs = [
        make_video_seg(CIRCLE_DIR / png, us(t0), us(t1) - us(t0), 0.0, 1.0, 0.0,
                       px=px, py=py, sc=sc, in_anim="Rõ dần", out_anim="Mờ dần")
        for t0, t1, png, px, py, sc, _ in CIRCLE_SPEC
    ]
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["flag"] = 2; tr_v2["segments"] = tr2_segs

    # Native Editable Coiny Texts (Subtitles + Floating F20 Green/White Texts with User's exact 1117 F20 animations!)
    def make_native_text(is_sub: bool, t0_s: float, t1_s: float, text: str, px: float, py: float, size: float,
                         fill_col: list, stroke_col: list, stroke_w: float,
                         in_nm: str | None = None, out_nm: str | None = None, loop_nm: str | None = None):
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
            "group_id": "",
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

        st_u = us(t0_s)
        du_u = max(us(0.35), us(t1_s) - st_u)
        refs = []
        anim_list = []
        if in_nm and in_nm in TEXT_ANIMS["in"]:
            ai = copy.deepcopy(TEXT_ANIMS["in"][in_nm])
            ai["start"] = 0
            ai["duration"] = min(260000, du_u // 3)
            anim_list.append(ai)
        if out_nm and out_nm in TEXT_ANIMS["out"]:
            ao = copy.deepcopy(TEXT_ANIMS["out"][out_nm])
            od = min(240000, du_u // 3)
            ao["duration"] = od
            ao["start"] = max(0, du_u - od)
            anim_list.append(ao)
        if loop_nm and loop_nm in TEXT_ANIMS["loop"]:
            al = copy.deepcopy(TEXT_ANIMS["loop"][loop_nm])
            al["start"] = 0
            al["duration"] = du_u
            anim_list.append(al)
        if anim_list:
            ma_id = uid()
            D["materials"].setdefault("material_animations", []).append({
                "animations": anim_list, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
            })
            refs.append(ma_id)

        sg = copy.deepcopy(sub_seg_tpl if is_sub else txt_seg_tpl)
        sg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        sg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        sg["clip"]["rotation"] = 0.0
        sg["clip"]["alpha"] = 1.0
        sg.update({
            "id": uid(), "material_id": tid,
            "target_timerange": {"start": st_u, "duration": du_u},
            "source_timerange": None,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        return sg

    # Subtitles (Track 3): Red fill + White stroke, smooth gaps, zero blinking!
    sub_segs = []
    SUB_SORTED = sorted(SUB_RAW, key=lambda x: x[0])
    for i, (t0, t1, tx, sz) in enumerate(SUB_SORTED):
        if i + 1 < len(SUB_SORTED):
            nxt_t0 = SUB_SORTED[i + 1][0]
            if 0.0 < (nxt_t0 - t1) <= 0.28:
                t1 = nxt_t0 - 0.034
            elif t1 > nxt_t0 - 0.034:
                t1 = max(t0 + 0.35, nxt_t0 - 0.034)
        sg = make_native_text(
            True, t0, t1, wrap_sub(tx), 0.0, -0.58, sz,
            COL_RED, COL_WHITE, 0.060,
            in_nm=("Chữ mờ dần hiện vào" if i == 0 else None)
        )
        sub_segs.append(sg)
    tr_sub = copy.deepcopy(sub_tr_tpl); tr_sub["id"] = uid(); tr_sub["segments"] = sub_segs

    # Floating F20 Green + White Accent Texts (pack cleanly onto non-overlapping text tracks!)
    ft_lanes: list[list[dict]] = []
    for t0, t1, tx, px, py, sz, is_wr, ain, aout, aloop in sorted(FLOATING_TEXTS, key=lambda x: x[0]):
        fcol = COL_WHITE if is_wr else COL_F20_GREEN
        scol = COL_RED   if is_wr else COL_WHITE
        sg = make_native_text(False, t0, t1, tx, px, py, sz, fcol, scol, 0.068, ain, aout, aloop)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for ln in ft_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                ln.append(sg); placed = True; break
        if not placed:
            ft_lanes.append([sg])
    ft_tracks = []
    for ln in ft_lanes:
        tt = copy.deepcopy(txt_tr_tpl); tt["id"] = uid(); tt["segments"] = ln
        ft_tracks.append(tt)

    # Filter Track (`Sống động 2`, val=0.146 — cloned straight from user's finalized 1117 F20!)
    filt_mat = copy.deepcopy(FILTER_MAT_TPL)
    filt_mat["id"] = uid()
    D["materials"].setdefault("effects", []).append(filt_mat)
    tr_filt = copy.deepcopy(FILTER_TRACK_TPL)
    tr_filt["id"] = uid()
    fseg = copy.deepcopy(tr_filt["segments"][0])
    fseg.update({
        "id": uid(), "material_id": filt_mat["id"],
        "target_timerange": {"start": 0, "duration": speech_end_u},
        "extra_material_refs": [],
    })
    tr_filt["segments"] = [fseg]

    # Audio Track 1: F20 Signature BGM (`Nhạc Sáo Trúc Đàn Tranh Gốc F20`, vol=0.28, cleanly spliced with cross-fade to cover full 220s + 1.2s fade-out!)
    bgm_dur_s = probe_audio_dur(BGM_F20)
    bgm_dur_u = us(bgm_dur_s)
    bgm_aid = uid()
    bgm_mat = copy.deepcopy(amat_tpl)
    bgm_mat.update({
        "id": bgm_aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
        "name": BGM_F20.name, "path": norm_fwd(BGM_F20), "duration": bgm_dur_u, "type": "music",
    })
    D["materials"]["audios"].append(bgm_mat)

    def make_bgm_seg(tgt_st_u: int, tgt_du_u: int, src_st_u: int, fi_u: int, fo_u: int, vol: float = 0.28):
        sg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, tpl_e in a_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        fid = uid()
        D["materials"].setdefault("audio_fades", []).append({
            "fade_in_duration": fi_u, "fade_out_duration": fo_u, "fade_type": 0, "id": fid, "type": "audio_fade"
        })
        refs.append(fid)
        sg.update({
            "id": uid(), "material_id": bgm_aid,
            "source_timerange": {"start": src_st_u, "duration": tgt_du_u},
            "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
            "speed": 1.0, "volume": vol, "last_nonzero_volume": vol,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        return sg

    seg1_u = min(total_u, us(125.0))
    bgm_segs = [make_bgm_seg(0, seg1_u, 0, 350000, 350000, 0.28)]
    if total_u > seg1_u:
        rem_u = total_u - seg1_u
        bgm_segs.append(make_bgm_seg(seg1_u, rem_u, us(8.0), 350000, 1200000, 0.28))
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = bgm_segs

    # Audio Tracks 2+: User's Exact `1117 F20` SFX Palette (`pop!` for circles + clean `Whoosh` / `Ding` / `Chimes` / `Paper turn`!)
    SFX_EVENTS = [
        (0.18, SFX_DIR / "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",  "Air Mở Cảnh",      0.12, 0.7),
        (0.30, SFX_DIR / "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3", "Chuông Gió Mở", 0.10, 1.8),
        (S["02_room_pan"]["tl_start"], SFX_DIR / "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3", "Lướt Vào Phòng", 0.10, 0.5),
        (S["04_q1_oanh"]["tl_start"] + 0.15, SFX_DIR / "Whoosh - Fast Swoosh Pop 01 (1s).mp3", "Mở Phần 01", 0.10, 0.6),
        (S["06_a1_quality"]["tl_start"] + 4.15, CC_WSH_SFX, "Woosh Chất Lượng", 0.30, 0.45),
        (S["08_a1_handmade"]["tl_start"], SFX_DIR / "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3", "Shine Thủ Công", 0.09, 0.9),
        (S["11_q2_oanh"]["tl_start"] + 0.15, SFX_DIR / "Whoosh - Fast Swoosh Pop 01 (1s).mp3", "Mở Phần 02", 0.10, 0.6),
        (src_to_tl(S["14_a2_mica"], 156.0), SFX_DIR / "Ding - Tiếng chuông ngân trong trẻo.mp3", "Ding Mica Trong", 0.11, 1.1),
        (S["16_a3_minimal"]["tl_start"], SFX_DIR / "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3", "Swoosh Tối Giản", 0.10, 0.5),
        (S["18_gift_intro"]["tl_start"] + 0.15, SFX_DIR / "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3", "Mở Quà Tri Ân", 0.10, 0.6),
        (S["20_book1"]["tl_start"], SFX_DIR / "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3", "Lật Sách 1", 0.11, 0.7),
        (S["22_book2b"]["tl_start"], SFX_DIR / "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3", "Lật Sách 2", 0.11, 0.7),
        (S["23_hau_thanks"]["tl_start"], SFX_DIR / "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3", "Shine Cảm Ơn", 0.09, 0.9),
        (src_to_tl(S["24_oanh_cta"], 13.5), SFX_DIR / "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3", "Bell CTA", 0.10, 1.1),
        (speech_end_s - 0.04, SFX_DIR / "Whoosh - Title Swoosh (1s).mp3", "Swoosh Banner", 0.12, 0.8),
        (speech_end_s + 0.10, SFX_DIR / "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3", "Chuông Gió Banner", 0.11, 2.3),
    ]
    # Add user's exact CapCut `pop!` SFX on every single round circular product badge (identical to 1117 F20 Track 17!)
    for idx_c, (t0, _, _, _, _, _, mlbl) in enumerate(CIRCLE_SPEC):
        SFX_EVENTS.append((t0, CC_POP_SFX, f"Pop {mlbl}", 0.45, 0.37))

    sfx_cache = {}
    sfx_lanes: list[list[dict]] = []
    for t0, sp, lbl, vol, mdur in sorted(SFX_EVENTS, key=lambda x: x[0]):
        if not sp.is_file():
            continue
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
            "fade_in_duration": min(15000, du // 6), "fade_out_duration": min(100000, du // 3),
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

    # Assemble clean tracks with unified Timeline ID (`D.id == project.id == main_timeline_id == timelines[0].id`!)
    new_tl_id = uid()
    D["id"] = new_tl_id
    D["name"] = DRAFT_NAME
    D["tracks"] = [tr_v0, tr_v1, tr_v2, tr_sub, *ft_tracks, tr_filt, tr_bgm, *sfx_tracks]
    D["duration"] = total_u
    D["update_time"] = now_s
    D["create_time"] = now_s
    D["time_marks"] = None
    D["canvas_config"] = {"width": W, "height": H, "ratio": "9:16", "background": None}
    if isinstance(D.get("extra_info"), dict):
        D["extra_info"]["subtitle_fragment_info_list"] = []
    if isinstance(D.get("config"), dict):
        D["config"]["subtitle_taskinfo"] = []

    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video":
                s["render_index"] = ti
            elif tr["type"] == "text":
                s["render_index"] = 14000 + ti
            elif tr["type"] == "filter":
                s["render_index"] = 10000

    # Preserve existing `draft_id` from root_meta_info.json so running CapCut's Home card matches 1-to-1!
    rmi_path = CC_ROOT / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    existing_ent = next((x for x in rmi.get("all_draft_store", []) if x.get("draft_name") == DRAFT_NAME), None)
    draft_uuid = existing_ent["draft_id"] if existing_ent and existing_ent.get("draft_id") else uid()

    # Compute actual total file size of unique media materials (matches CapCut schema!)
    uniq_paths = {v["path"] for v in D["materials"]["videos"]} | {a["path"] for a in D["materials"]["audios"]}
    total_media_bytes = sum(Path(p).stat().st_size for p in uniq_paths if Path(p).is_file())

    # Write cleanly into the ONE CapCut Desktop project `261121 F20 Phỏng Vấn Đăng Khoa Edu`!
    if DRAFT_DIR.exists():
        shutil.rmtree(DRAFT_DIR)
    tl_sub = DRAFT_DIR / "Timelines" / new_tl_id
    tl_sub.mkdir(parents=True, exist_ok=True)
    for sub in (
        "adjust_mask", "matting", "qr_upload", "Resources", "subdraft", "common_attachment", "smart_crop",
        f"Timelines/{new_tl_id}/attachment", f"Timelines/{new_tl_id}/common_attachment",
    ):
        (DRAFT_DIR / sub).mkdir(parents=True, exist_ok=True)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for tp in [
        DRAFT_DIR / "draft_content.json",
        DRAFT_DIR / "draft_content.json.bak",
        DRAFT_DIR / "template-2.tmp",
        tl_sub / "draft_content.json",
        tl_sub / "draft_content.json.bak",
        tl_sub / "template-2.tmp",
    ]:
        tp.write_bytes(dc_bytes)

    dmi = json.loads((D1117_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))
    dmi["draft_id"] = draft_uuid
    dmi["draft_name"] = DRAFT_NAME
    dmi["draft_fold_path"] = norm_fwd(DRAFT_DIR)
    dmi["draft_root_path"] = norm_fwd(CC_ROOT)
    dmi["draft_cover"] = "draft_cover.jpg"
    dmi["draft_timeline_materials_size_"] = total_media_bytes
    dmi["tm_duration"] = total_u
    dmi["tm_draft_create"] = existing_ent["tm_draft_create"] if existing_ent and existing_ent.get("tm_draft_create") else now_us
    dmi["tm_draft_modified"] = now_us
    for bucket in dmi.get("draft_materials", []):
        bucket["value"] = new_dm_entries if bucket.get("type") == 0 else []
    (DRAFT_DIR / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    # Exact CapCut 164+/193 Timelines/project.json (`id == main_timeline_id == timelines[0].id == D.id` + `is_marked_delete`!)
    pj = {
        "config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
        "create_time": now_us,
        "id": new_tl_id,
        "main_timeline_id": new_tl_id,
        "timelines": [{"create_time": now_us, "id": new_tl_id, "is_marked_delete": False, "name": "Timeline 01", "update_time": now_us}],
        "update_time": now_us,
        "version": 0,
    }
    pj_bytes = json.dumps(pj, ensure_ascii=False).encode("utf-8")
    (DRAFT_DIR / "Timelines" / "project.json").write_bytes(pj_bytes)
    (DRAFT_DIR / "Timelines" / "project.json.bak").write_bytes(pj_bytes)

    # Write required CapCut companion files (`timeline_layout.json`, `performance_opt_info.json`, clean virtual store & attachments!)
    tl_layout = {"dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": [new_tl_id], "timelineNames": ["Timeline 01"]}], "layoutOrientation": 1}
    (DRAFT_DIR / "timeline_layout.json").write_text(json.dumps(tl_layout, ensure_ascii=False), encoding="utf-8")
    (DRAFT_DIR / "performance_opt_info.json").write_text(json.dumps({"manual_cancle_precombine_segs": None, "need_auto_precombine_segs": None}), encoding="utf-8")
    (DRAFT_DIR / "key_value.json").write_text("{}", encoding="utf-8")
    dvs = {
        "draft_materials": [],
        "draft_virtual_store": [
            {"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "material_color_tag": "", "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]},
            {"type": 1, "value": [{"child_id": e["id"], "parent_id": ""} for e in new_dm_entries]},
            {"type": 2, "value": []},
        ],
    }
    (DRAFT_DIR / "draft_virtual_store.json").write_text(json.dumps(dvs, ensure_ascii=False), encoding="utf-8")
    (DRAFT_DIR / "draft_settings").write_text(
        f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=120\nreal_edit_keys=1\n",
        encoding="utf-8",
    )

    # Copy clean lightweight companion attachments (`draft.extra`, `attachment_editing.json`, `attachment_pc_common.json`, agency/biz configs)
    clean_donor = CC_ROOT / "FEEL CHICKEN - Food Cinematic V7"
    donor_dir = clean_donor if clean_donor.exists() else D1117_DIR
    for aux in ("draft_agency_config.json", "draft_biz_config.json"):
        if (donor_dir / aux).exists():
            shutil.copy2(donor_dir / aux, DRAFT_DIR / aux)
    for att in ("draft.extra", "attachment_editing.json", "attachment_pc_common.json"):
        if (donor_dir / att).exists():
            shutil.copy2(donor_dir / att, DRAFT_DIR / att)
            shutil.copy2(donor_dir / att, tl_sub / att)

    cover_jpg = DRAFT_DIR / "draft_cover.jpg"
    subprocess.run(["ffmpeg","-y","-v","error","-ss","21.2","-i",str(AH_DIR/"C3925.MP4"),"-frames:v","1","-update","1","-vf","scale=540:960",str(cover_jpg)], check=True)
    shutil.copy2(cover_jpg, tl_sub / "draft_cover.jpg")
    shutil.copy2(cover_jpg, DRAFT_DIR / "Timelines" / "draft_cover.jpg")

    store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_NAME]
    tpl_entry = copy.deepcopy(existing_ent if existing_ent else next(x for x in store if x.get("draft_name") == "1117 F20"))
    fold_fwd = norm_fwd(DRAFT_DIR)
    tpl_entry.update({
        "draft_id": draft_uuid,
        "draft_name": DRAFT_NAME,
        "draft_fold_path": fold_fwd,
        "draft_json_file": fold_fwd + "\\draft_content.json",
        "draft_cover": fold_fwd + "\\draft_cover.jpg",
        "draft_root_path": norm_fwd(CC_ROOT),
        "draft_timeline_materials_size": total_media_bytes,
        "tm_duration": total_u,
        "tm_draft_modified": now_us,
    })
    store.insert(0, tpl_entry)
    rmi["all_draft_store"] = store
    rmi["draft_ids"] = len(store)
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    # ==========================================================================
    # STRUCTURAL AUDIT + 12-FRAME VISUAL QC SHEET!
    # ==========================================================================
    assert D["id"] == pj["id"] == pj["main_timeline_id"] == pj["timelines"][0]["id"] == new_tl_id
    assert pj["timelines"][0]["is_marked_delete"] is False
    assert dmi["draft_id"] == tpl_entry["draft_id"] == draft_uuid
    assert tr_v0["flag"] == 0 and tr_v1["flag"] == 2 and tr_v2["flag"] == 2
    assert tr_filt["segments"][0]["render_index"] == 10000
    assert (DRAFT_DIR / "draft.extra").exists() and (DRAFT_DIR / "timeline_layout.json").exists()
    vmap = {v["id"]: v for v in D["materials"]["videos"]}
    for s in tr_v0["segments"]:
        assert s["clip"]["scale"] == {"x": 1.0, "y": 1.0}
        assert vmap[s["material_id"]]["crop"] == FULL_CROP_1_1
    for s in tr_v1["segments"][:-1]:
        assert s["clip"]["scale"] == {"x": 1.0, "y": 1.0}, "Non-1.0 scale on raw B-roll!"
        assert s["clip"]["transform"] == {"x": 0.0, "y": 0.0}, "Non-zero pan on raw B-roll!"
        assert s["common_keyframes"] == []
        assert vmap[s["material_id"]]["crop"] == FULL_CROP_1_1
    for s in tr_v2["segments"]:
        vm = vmap[s["material_id"]]
        assert (vm["width"], vm["height"]) == (W, H)
        assert vm["crop"] == FULL_CROP_1_1
    for t in D["materials"]["texts"]:
        assert t["check_flag"] == 15

    # Render 12-frame Visual QC Sheet showing our new F20-Green texts, context-matched B-rolls & round circles!
    qc_times = [
        1.2,   # Chị Oanh at doorway + White/Red Hero + F20 Green Sub-line
        4.0,   # Clean B-roll C3903 @18s (unloading gift sets from car, zero distracting sign!)
        15.8,  # Handshake + Anh Hậu • ĐĂNG KHOA EDU (Green+White on clean blue wall!)
        21.0,  # Q1 + 01 • LÝ DO CHỌN F20 (Green+White on clean blue wall!)
        52.0,  # B-roll DJI_0082 close-up of real Yến + Rong biển + Bánh hạt!
        59.2,  # A1 Yến thủ công + C3866 tying bows + YẾN THỦ CÔNG • KHÔNG HÓA CHẤT
        74.5,  # B-roll DJI_0084 close-up of Rong biển kẹp hạt!
        112.2, # B-roll DJI_0083 close-up of Giỏ Mica trong suốt!
        142.5, # A3 4 items + Circle 02 raised to +0.43 + 01 • RONG BIỂN cleanly on sky-blue wall!
        175.0, # Gift box handover C3932
        200.5, # Anh Hậu cảm ơn sách + MÓN QUÀ TAN CHẢY (Green+White on clean blue wall!)
        total_s - 1.0, # F20 Brand Closing Banner (0% AI!)
    ]
    fnt_sub = ImageFont.truetype(COINY_FONT_PATH, 45)
    fnt_hdr = ImageFont.truetype(COINY_FONT_PATH, 48)
    fnt_mini = ImageFont.truetype(COINY_FONT_PATH, 36)
    fnt_lbl = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 22)

    cols, rows = 4, 3
    tw, th = 360, 640
    sheet = Image.new("RGB", (cols * tw, rows * (th + 28)), (18, 20, 24))
    sdr = ImageDraw.Draw(sheet)
    tmap_all = {t["id"]: t for t in D["materials"]["texts"]}

    for idx, ts in enumerate(qc_times):
        tu = us(ts)
        active_seg = None
        for tr_v in (tr_v1, tr_v0):
            for s in tr_v["segments"]:
                st, du = s["target_timerange"]["start"], s["target_timerange"]["duration"]
                if st <= tu < st + du:
                    active_seg = s; break
            if active_seg: break
        vm = vmap[active_seg["material_id"]]
        src_t = (active_seg["source_timerange"]["start"] + (tu - active_seg["target_timerange"]["start"]) * active_seg["speed"]) / 1e6
        tmp_f = WORK / "_qc2_tmp.jpg"
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{src_t:.3f}","-i",vm["path"],"-frames:v","1","-update","1","-vf",f"scale={W}:{H}",str(tmp_f)], check=True)
        canvas = Image.open(tmp_f).convert("RGBA")
        tmp_f.unlink()

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

        dr = ImageDraw.Draw(canvas)
        for tr_t in [*ft_tracks, tr_sub]:
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
                    fnt = fnt_mini if tm["font_size"] <= 10.6 else (fnt_sub if tm["type"] == "subtitle" else fnt_hdr)
                    bb = dr.multiline_textbbox((0, 0), txt, font=fnt, stroke_width=7, align="center")
                    tw_t, th_t = bb[2] - bb[0], bb[3] - bb[1]
                    dr.multiline_text((cx - tw_t // 2, cy - th_t // 2), txt, font=fnt, fill=fcol,
                                      stroke_width=7, stroke_fill=scol, align="center")

        img = canvas.convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        r, c = divmod(idx, cols)
        x0, y0 = c * tw, r * (th + 28)
        sheet.paste(img, (x0, y0 + 28))
        sdr.text((x0 + 6, y0 + 4), f"t={ts:05.1f}s | {Path(vm['path']).name[:20]}", font=fnt_lbl, fill=(240, 235, 160))

    qc_out = WORK / "qc_dkedu_v2_12frames.jpg"
    sheet.save(qc_out, quality=90)

    # Sync updated script & QC sheet to Google Drive archive!
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), ARCHIVE_DIR / Path(__file__).name)
    shutil.copy2(qc_out, ARCHIVE_DIR / qc_out.name)

    print("\n=== SUCCESS V2 CAPCUT PROJECT (CLONED 100% USER'S FINISHED 1117 F20 STYLE!) ===")
    print(f"  -> Draft : {DRAFT_DIR}")
    print(f"  -> Dur   : {total_s:.2f}s ({int(total_s//60)}m {total_s%60:04.1f}s) | 0% AI!")
    print(f"  -> Track0: {len(tr0_segs)} raw cuts + 4 'Kết hợp' transitions")
    print(f"  -> Track1: {len(BROLL_SPEC)} context-perfect raw 9:16 B-rolls (scale=1.0, pos=(0,0)) + F20 Brand Banner")
    print(f"  -> Track2: {len(CIRCLE_SPEC)} clean round 1080x1920 circular badges (0% handle, 0% oval stretch)")
    print(f"  -> Texts : {len(sub_segs)} Red/White Coiny subtitles + {len(FLOATING_TEXTS)} F20-Green/White animated titles (check_flag=15)")
    print(f"  -> Filter: 'Sống động 2' (0.146) cloned straight from 1117 F20")
    print(f"  -> Audio : F20 Sáo Trúc Đàn Tranh BGM (0.28) + {len(SFX_EVENTS)} SFX (incl. user's exact CapCut pop! on every circle!)")
    print(f"  -> QC Img: {qc_out}")


if __name__ == "__main__":
    main()
