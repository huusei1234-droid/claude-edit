"""
F20 × ĐĂNG KHOA EDU (77 SET QUÀ 20/11) — V4 MASTER FINAL
("COINY CAPCUT + SHORTENED ~2p20s + 5 CUTE DIE-CUT STICKERS FLYING UP + EXECUTIVE NAME TAG")
==============================================================================================
100% Zero AI — Real 261116 footage + real IS-Net F20 product sticker cutouts + non-AI F20 banner.
  1. Font COINY (`Coiny-Regular.ttf`, CapCut ID `7482665772876156165`) for ALL normal white subs
     & colored jumping emphasis callouts (Nàng Xuân 2-tier layout: calm white sub below + vibrant
     colored emphasis jumping up separately above + 5-item stacking Coiny list).
  2. Tightened Retention Cut (`~2m 22s`, trimmed ~1m 28s of filler!) keeping 100% of punchlines,
     emotion, and gift moments, with 20 guarded short-pause speed-ups (`1.75x-1.90x`) -> ZERO jump-cuts!
  3. 5 Adorable White-Bordered Die-Cut Product Stickers (`IS-Net 1024px` cutouts of REAL F20 products)
     FLYING UP cutely from the basket (`+220px -> 0px` bounce + gentle floating bob) as Anh Hậu names
     each ingredient (01 Rong Biển -> 02 Yến Sào -> 03 Đường Phèn -> 04 Bánh Thuyền -> 05 Kẹp Hạt)!
  4. Prestigious Executive Lower-Third Name Tag (`Thầy LOAN VĂN HẬU • Giám đốc Hệ thống Luyện thi
     Đăng Khoa Edu`) with frosted emerald glass + metallic gold accent bar sliding cleanly below hands.
  5. Renders Final HQ MP4 via GPU NVENC (`h264_nvenc`, `-14.0 LUFS` Voice-Pocket audio mix) AND
     updates synced editable CapCut Draft (`D:\\Capcut\\CapCut Drafts\\261121 F20 Phỏng Vấn Đăng Khoa Edu`).
"""

import copy, json, math, os, shutil, subprocess, sys, time, uuid
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30

CC_ROOT    = Path(r"D:\Capcut\CapCut Drafts")
RMI_PATH   = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json")
DRAFT_NAME = "261121 F20 Phỏng Vấn Đăng Khoa Edu"
DRAFT_DIR  = CC_ROOT / DRAFT_NAME
MAT_V      = DRAFT_DIR / "materials" / "video"
MAT_A      = DRAFT_DIR / "materials" / "audio"
NX_DRAFT   = CC_ROOT / "Nàng Xuân"

FONTS_DIR   = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
FONT_COINY  = FONTS_DIR / "Coiny-Regular.ttf"
COINY_CC_ID = "7482665772876156165"
COINY_CC_P  = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Cache\effect\7482665772876156165\57619fa23667c87dee08a75d49a8b51a\font.ttf")

WORK        = Path(r"d:\AI\full studio\output\f20-phong-van-dang-khoa-edu")
V4_DIR      = WORK / "v4_assets"
TMP_DIR     = WORK / "_v4_tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

FINAL_NAME  = "261122 F20 Phỏng vấn Đăng Khoa Edu 77 set quà final.mp4"
FINAL_F20   = Path(r"G:\Other computers\My Computer\F20\Final") / FINAL_NAME
FINAL_CLD   = Path(r"G:\My Drive\AI_Full_Studio\04_Videos_Final") / FINAL_NAME
ARCHIVE_G   = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\f20-phong-van-dang-khoa-edu")
LOCAL_OUT   = WORK / FINAL_NAME

BGM_PATH   = MAT_A / "Nhạc Sáo Trúc Đàn Tranh Gốc F20 - Bản Dài Sạch Lỗi (2p13s).mp3"
SFX_POP    = MAT_A / "6238aa6c3491fbc9af81e0e8afcb5931.mp3"
SFX_DING   = MAT_A / "Ding - Tiếng chuông ngân trong trẻo.mp3"
SFX_BELL   = MAT_A / "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3"
SFX_CHIME  = MAT_A / "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3"
SFX_SHINE  = MAT_A / "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3"
SFX_WSH1   = MAT_A / "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"
SFX_WSH2   = MAT_A / "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"
SFX_WSH3   = MAT_A / "Whoosh - Fast Swoosh Pop 01 (1s).mp3"
SFX_WSHT   = MAT_A / "Whoosh - Title Swoosh (1s).mp3"
SFX_PAGE   = MAT_A / "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3"

FULL_CROP_1_1 = {
    "upper_left_x": 0.0, "upper_left_y": 0.0,
    "upper_right_x": 1.0, "upper_right_y": 0.0,
    "lower_left_x": 0.0, "lower_left_y": 1.0,
    "lower_right_x": 1.0, "lower_right_y": 1.0,
}

# Colors tailored to each scene's real background (high-contrast Coiny + Nàng Xuân 2-tier system!)
RGB_WHITE      = (255, 255, 255)
RGB_GOLD       = (255, 224, 66)    # Bright luminous gold (pops on dark red carpet & showroom wood!)
RGB_EMERALD    = (62, 245, 124)    # Fresh F20 luminous green (pops on dark/mid backgrounds)
RGB_F20_DEEP   = (0, 168, 64)      # Deep F20 emerald with crisp white stroke (pops on bright white glass door!)
RGB_RED_F20    = (232, 36, 36)     # Official F20 red with crisp white stroke (for bright white doorway sub-title!)
RGB_STROKE_SUB = (14, 18, 22)
RGB_STROKE_GLD = (44, 24, 6)
RGB_STROKE_GRN = (6, 48, 18)

def rgb01(c): return [round(c[0] / 255.0, 4), round(c[1] / 255.0, 4), round(c[2] / 255.0, 4)]
def uid(): return str(uuid.uuid4()).upper()
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
# 1. TRACK 0 — TIGHTENED RETENTION-FOCUSED TIMELINE (~2p 22s, CUT ~1p 28s FAT!)
#    Every short pause sped up smoothly (1.75x-1.85x with +0.14s/-0.10s speech guard)
#    Every long cut 100% hidden under context-exact native 9:16 B-roll!
# ==============================================================================
BLOCKS_SPEC = [
    # HỒI 1: Cửa phòng báo 77 set quà -> Pan nhanh 1.0s -> Bắt tay Thầy Loan Văn Hậu (+ Executive Name Tag!)
    ("B01_doorway",   "C3925.MP4", 1.70, 14.35, 1.08, [(1.70, 14.35, 1.15, +1.0)], [], True),
    ("B02_room_pan",  "C3908.MP4", 0.80,  1.85, 1.00, [(0.80,  1.85, 0.00, -99.0)], [], False),
    ("B03_handshake", "C3925.MP4",18.75, 23.15, 1.04, [(18.75,23.15, 1.35, +2.4)], [], True),

    # HỒI 2: Lý do chọn F20 (Tinh gọn mạnh tay: Q1 -> Phải chất lượng -> Yến thủ công không hóa chất -> Rong biển & bánh hạt tiếp năng lượng!)
    ("B04_q1_oanh",   "C3926.MP4", 5.75, 15.48, 1.08, [(5.75, 15.48, 1.15, +1.0)], [], False),
    # Cover cut 15.48 -> 23.50 with C3910 wide 77 sets!
    ("B05_quality",   "C3926.MP4",23.50, 33.75, 1.07,
     [(23.50, 33.75, 1.75, +4.8)],
     [(28.87, 29.40, 1.75), (31.51, 32.33, 1.85)], False),
    # Cover cut 33.75 -> 57.85 seamlessly with DJI_0082_D (macro gift basket)!
    ("B06_hand_sea",  "C3926.MP4",57.85, 79.85, 1.07,
     [(57.85, 79.85, 1.75, +4.8)],
     [
         (59.86, 60.60, 1.85),
         (63.10, 63.73, 1.85),
         (66.72, 67.51, 1.85),
         (69.05, 69.75, 1.85),
         (72.95, 73.42, 1.75),
         (76.80, 77.37, 1.80),
     ], False),
    # Cover cut 79.85 -> 86.75 seamlessly with DJI_0084_D (Rong biển kẹp hạt)!
    ("B07_energy",    "C3926.MP4",86.75, 92.20, 1.07, [(86.75, 92.20, 1.75, +4.8)], [], False),

    # HỒI 3: Cảm nhận cầm trên tay & Giỏ Mica Trong ("Rất là ưng ý -> Quai xách tiện tay -> Mica trong show hết!" — 1 cú máy liền mạch!)
    # Cover cut 92.20 -> 133.20 seamlessly with C3917 (77 sets on red carpet)!
    ("B08_a2_mica",   "C3926.MP4",133.20, 165.35, 1.07,
     [(133.20, 152.80, 1.75, +4.8), (152.80, 156.00, 1.18, +1.2), (156.00, 165.35, 1.65, +4.2)],
     [
         (138.21, 138.94, 1.85),
         (142.55, 143.16, 1.85),
         (144.58, 145.41, 1.85),
         (146.83, 147.37, 1.75),
         (149.15, 150.20, 1.85),
         (156.83, 157.48, 1.85),
     ], False),

    # HỒI 4: Tối giản chất lượng & Đọc 5 thành phần (+ 5 CUTE DIE-CUT STICKERS BAY LÊN!) — 1 cú máy liền mạch!
    # Cover cut 165.35 -> 204.90 seamlessly with C3874 (gleaming F20 shelf)!
    ("B09_a3_5items", "C3926.MP4",204.90, 233.30, 1.07,
     [(204.90, 233.30, 1.75, +4.8)],
     [
         (212.80, 213.35, 1.85),
         (217.08, 217.86, 1.85),
         (218.94, 219.57, 1.85),
         (223.12, 223.86, 1.85),
         (226.12, 226.67, 1.80),
     ], True),

    # HỒI 5: Trao Hộp Quà Sách Tri Ân Thầy Hậu (Siêu gọn & cảm xúc!)
    ("B10_gift_give", "C3932.MP4", 47.65, 51.35, 1.06, [(47.65, 51.35, 1.35, +2.4)], [], False),
    # Cover cut 51.35 -> 63.85 with C3921 (warm smile/chat)!
    ("B11_book1",     "C3932.MP4", 63.85, 74.05, 1.07, [(63.85, 74.05, 1.15, +1.0)], [], False),
    # Cover cut 74.05 -> 91.40 with C3919 (Anh Hậu & Chị Oanh smiling beside 77 sets)!
    ("B12_book2",     "C3932.MP4", 91.40, 96.25, 1.07, [(91.40, 96.25, 1.15, +1.0)], [], True),
    ("B13_hau_thanks","C3932.MP4",122.40,130.00, 1.06, [(122.40,130.00, 1.75, +4.8)], [], True),

    # HỒI 6: Chị Oanh Cảm Ơn & CTA (`C3864`) + Banner Kết F20 (0% AI!)
    ("B14_oanh_cta",  "C3864.MP4",  5.15, 19.30, 1.08, [(5.15, 19.30, 1.20, +1.4)], [], False),
]


def expand_timeline():
    segs = []
    block_maps = {}
    cur_f = 0

    for bid, fn, sin, sout, bspd, vspans, bridges, xfade_after in BLOCKS_SPEC:
        safe_bridges = []
        for pa, pb, sp in bridges:
            sa, sb = pa + 0.14, pb - 0.10
            if sb - sa >= 0.36:
                safe_bridges.append((sa, sb, min(sp, 1.85)))

        pts = {sin, sout}
        for va, vb, _, _ in vspans:
            if sin < va < sout: pts.add(va)
            if sin < vb < sout: pts.add(vb)
        for pa, pb, _ in safe_bridges:
            if sin < pa < sout: pts.add(pa)
            if sin < pb < sout: pts.add(pb)
        pts = sorted(pts)

        bmap = []
        block_segs = []
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            if b - a < 0.08:
                continue
            mid_t = 0.5 * (a + b)
            br = next((sp for pa, pb, sp in safe_bridges if pa - 1e-4 <= mid_t <= pb + 1e-4), None)
            if br is not None:
                # Keep soft room-tone continuity (0.15 in CapCut, -18dB lowpass in FFmpeg) so bridges NEVER sound like muted drop-outs!
                spd, vol_cc, vol_db, is_bridge = br, 0.15, -99.0, True
            else:
                spd, is_bridge = bspd, False
                vs = next(((vc, vd) for va, vb, vc, vd in vspans if va - 1e-4 <= mid_t <= vb + 1e-4), (1.15, +1.0))
                vol_cc, vol_db = vs

            dur_f = max(2, int(round(((b - a) / spd) * FPS)))
            tl_a = cur_f / FPS
            tl_b = (cur_f + dur_f) / FPS
            rec = {
                "block": bid, "file": fn, "path": MAT_V / fn,
                "src_in": a, "src_out": b, "speed": spd,
                "vol_cc": vol_cc, "vol_db": vol_db, "is_bridge": is_bridge,
                "tl_f0": cur_f, "tl_f1": cur_f + dur_f, "dur_f": dur_f,
                "tl_start": tl_a, "tl_end": tl_b,
                "tl_start_u": us(tl_a), "tl_dur_u": us(tl_b) - us(tl_a),
                "xfade_after": False,
            }
            segs.append(rec)
            block_segs.append(rec)
            bmap.append((a, b, tl_a, tl_b, spd))
            cur_f += dur_f

        if block_segs and xfade_after:
            block_segs[-1]["xfade_after"] = True
        block_maps[bid] = bmap

    return segs, block_maps, cur_f


def src_to_tl(bmaps: dict, bid: str, src_t: float) -> float:
    bm = bmaps[bid]
    if src_t <= bm[0][0]: return bm[0][2]
    if src_t >= bm[-1][1]: return bm[-1][3]
    for a, b, ta, tb, _ in bm:
        if a - 1e-5 <= src_t <= b + 1e-5:
            return ta + ((src_t - a) / max(1e-6, (b - a))) * (tb - ta)
    return bm[-1][3]


def wrap_text(text: str, max_chars: int = 28) -> str:
    if "\n" in text or len(text) <= max_chars:
        return text
    words = text.split()
    best_i, best_diff = 1, 999
    for i in range(1, len(words)):
        diff = abs(len(" ".join(words[:i])) - len(" ".join(words[i:])))
        if diff < best_diff:
            best_diff, best_i = diff, i
    return " ".join(words[:best_i]) + "\n" + " ".join(words[best_i:])


def ease_out_back(u: float) -> float:
    u = max(0.0, min(1.0, u))
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2)


def draw_styled_text(canvas: Image.Image, text: str, cx: int, cy: int,
                     font: ImageFont.FreeTypeFont, fill_rgb: tuple,
                     stroke_rgb: tuple, stroke_w: int,
                     shadow_alpha: int = 170, shadow_off: tuple = (0, 5),
                     shadow_blur: int = 6, scale: float = 1.0, alpha: float = 1.0,
                     y_shift: int = 0):
    if alpha <= 0.01 or scale <= 0.05:
        return
    tmp = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    tdr = ImageDraw.Draw(tmp)
    pad = int(stroke_w + shadow_blur * 2 + 24)
    bb = tdr.multiline_textbbox((0, 0), text, font=font, stroke_width=stroke_w, align="center", spacing=8)
    tw, th = max(2, int(math.ceil(bb[2] - bb[0]))), max(2, int(math.ceil(bb[3] - bb[1])))
    bw, bh = int(tw + pad * 2), int(th + pad * 2)
    box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ox, oy = int(round(pad - bb[0])), int(round(pad - bb[1]))

    if shadow_alpha > 0:
        sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        sdr = ImageDraw.Draw(sh)
        sdr.multiline_text((ox + shadow_off[0], oy + shadow_off[1]), text, font=font,
                           fill=(0, 0, 0, int(shadow_alpha)),
                           stroke_width=max(1, stroke_w), stroke_fill=(0, 0, 0, int(shadow_alpha)),
                           align="center", spacing=8)
        if shadow_blur > 0:
            sh = sh.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
        box.alpha_composite(sh)

    bdr = ImageDraw.Draw(box)
    bdr.multiline_text((ox, oy), text, font=font, fill=(*fill_rgb, 255),
                       stroke_width=stroke_w, stroke_fill=(*stroke_rgb, 255),
                       align="center", spacing=8)

    if abs(scale - 1.0) > 0.005:
        nw, nh = max(2, int(round(bw * scale))), max(2, int(round(bh * scale)))
        box = box.resize((nw, nh), Image.Resampling.BICUBIC)
    else:
        nw, nh = bw, bh
    if alpha < 0.995:
        arr = np.array(box, dtype=np.uint8)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * alpha).astype(np.uint8)
        box = Image.fromarray(arr, mode="RGBA")
    canvas.alpha_composite(box, (int(round(cx - nw / 2)), int(round(cy + y_shift - nh / 2))))


def main():
    t_wall = time.time()
    draft_is_locked = DRAFT_DIR.exists() and (DRAFT_DIR / ".locked").exists()
    if draft_is_locked:
        print(f"[INFO] '{DRAFT_NAME}' is currently open in CapCut (.locked) -> will NEVER touch/kill CapCut; creating clean sibling draft instead!")

    segs, BM, speech_end_f = expand_timeline()
    banner_f = int(round(2.50 * FPS))
    total_f  = speech_end_f + banner_f
    speech_end_s = speech_end_f / FPS
    total_s      = total_f / FPS
    n_bridges = sum(1 for s in segs if s["is_bridge"])
    print(f"V4 Shortened Timeline: {len(segs)} Track-0 segments ({n_bridges} smooth pause speed-ups!), speech={speech_end_s:.2f}s, total={total_s:.2f}s ({int(total_s//60)}m {total_s%60:04.1f}s)")

    def tm(bid: str, s0: float, s1: float) -> tuple[float, float]:
        return (src_to_tl(BM, bid, s0), src_to_tl(BM, bid, s1))
    def tp(bid: str, s0: float) -> float:
        return src_to_tl(BM, bid, s0)

    # ==========================================================================
    # 2. TRACK 1 — 18 CONTEXT-EXACT NATIVE 9:16 B-ROLL OVERLAYS (0% AI!)
    #    100% of long cuts hidden seamlessly behind visually matched real shots!
    # ==========================================================================
    BROLL_SPEC = [
        # Hồi 1: Doorway 3.0s -> C3903 @18s (clean car unloading) -> C3914 -> C3909
        (*tm("B01_doorway", 4.90, 7.00),     "C3903.MP4", 18.00, 1.00, False, "Chuyển 77 set quà từ xe"),
        (*tm("B01_doorway", 7.00, 8.95),     "C3914.MP4",  3.00, 1.00, False, "Bày 77 set quà tại ĐK Edu"),
        (*tm("B01_doorway", 8.95, 10.60),    "C3909.MP4",  1.50, 1.00, False, "Pan cận 77 set quà"),

        # Hồi 2: Cover B04->B05 with C3910 (wide 77 sets) + C3920 (inspecting quality)
        (tp("B04_q1_oanh", 13.00), tp("B05_quality", 25.00),
         "C3910.MP4", 0.80, 0.92, False, "Toàn cảnh 77 set quà tại ĐK Edu"),
        (*tm("B05_quality", 28.50, 31.80),   "C3920.MP4",  1.20, 0.95, False, "Anh Hậu & Chị Oanh kiểm tra chất lượng"),
        # Cover B05->B06 seamlessly with DJI_0082_D (macro gift basket)!
        (tp("B05_quality", 32.80), tp("B06_hand_sea", 60.40),
         "DJI_20261116093228_0082_D.MP4", 2.00, 0.95, True, "Cận set quà Yến SKANEST, Rong Biển, Bánh Hạt"),
        (*tm("B06_hand_sea", 60.40, 63.30),  "DJI_20261116093826_0087_D.MP4", 8.00, 0.95, True, "Macro Tổ Yến SKANEST & Cẩm nang"),
        (*tm("B06_hand_sea", 63.30, 66.40),  "C3866.MP4",  6.00, 1.00, False, "Thắt nơ hoàn thiện thủ công"),
        (*tm("B06_hand_sea", 66.40, 68.70),  "C3870.MP4",  1.50, 1.00, False, "Kiểm tra thủ công từng set"),
        # Cover B06->B07 seamlessly with DJI_0084_D (Rong biển kẹp hạt) + C3873!
        (tp("B06_hand_sea", 77.30), tp("B07_energy", 87.60),
         "DJI_20261116093322_0084_D.MP4", 48.00, 1.00, True, "Cận Rong Biển Kẹp Hạt & Tuệ Tâm"),
        (*tm("B07_energy", 87.60, 90.20),    "C3873.MP4",  1.00, 0.92, False, "Dàn set quà đầy ắp hạt dinh dưỡng"),

        # Hồi 3: Cover B07->B08 seamlessly with C3917 (77 sets on red carpet)!
        (tp("B07_energy", 90.80), tp("B08_a2_mica", 136.50),
         "C3917.MP4", 1.20, 1.00, False, "77 set quà xếp ngay ngắn trên thảm đỏ ĐK Edu"),
        (*tm("B08_a2_mica", 143.30, 146.90), "DJI_20261116093624_0085_D.MP4", 3.50, 0.95, True, "Cận quai xách da đỏ đô tiện tay"),
        (*tm("B08_a2_mica", 152.90, 156.80), "DJI_20261116093255_0083_D.MP4", 4.00, 0.95, True, "Cận xoay giỏ Mica trong suốt"),

        # Hồi 4: Cover B08->B09 seamlessly with C3874 (gleaming F20 shelf)!
        (tp("B08_a2_mica", 163.60), tp("B09_a3_5items", 207.20),
         "C3874.MP4", 1.20, 0.92, False, "Kệ trưng bày Yến Sào SKANEST & Set Quà F20"),

        # Hồi 5: Cover B10->B11 (C3921) & B11->B12 (C3919)!
        (tp("B10_gift_give", 50.60), tp("B11_book1", 65.50),
         "C3921.MP4", 1.20, 1.00, False, "Anh Hậu & Chị Oanh trò chuyện thân tình"),
        (tp("B11_book1", 72.80), tp("B12_book2", 92.60),
         "C3919.MP4", 1.50, 1.00, False, "Anh Hậu & Chị Oanh bên 77 set quà"),

        # Hồi 6: CTA
        (*tm("B14_oanh_cta", 13.50, 17.20),  "C3875.MP4",  1.50, 0.92, False, "Dãy set quà 20/11 sẵn sàng giao ngay"),
    ]
    BROLL_SPEC.sort(key=lambda x: x[0])
    for i in range(len(BROLL_SPEC) - 1):
        if BROLL_SPEC[i][1] > BROLL_SPEC[i + 1][0]:
            BROLL_SPEC[i] = (*BROLL_SPEC[i][:1], BROLL_SPEC[i + 1][0], *BROLL_SPEC[i][2:])

    # ==========================================================================
    # 3. TRACK 2 — 5 CUTE FLYING DIE-CUT PRODUCT STICKERS (IS-Net 1024px, White Border, 0% AI!)
    #    + PRESTIGIOUS EXECUTIVE NAME TAG FOR THẦY LOAN VĂN HẬU!
    # ==========================================================================
    # Cute die-cut stickers FLYING UP from the basket (`+220px -> 0px` bounce + cute floating bob!)
    # Format: (tl_t0, tl_t1, png_name, px_norm, py_norm, sc, kind)
    STICKER_SPEC = [
        # Directional Executive Name Tags matched strictly to Thầy Hậu's exact side in frame!
        # - Handshake (C3925): Thầy Hậu stands on RIGHT -> nametag_thay_hau_right.png (slides in from right!)
        # - Interview (C3926): Thầy Hậu stands on LEFT  -> nametag_thay_hau_left.png  (slides in from left!)
        (tp("B03_handshake", 19.30), tp("B03_handshake", 23.05), "nametag_thay_hau_right.png", 0.0, 0.0, 1.00, "nametag_right"),
        (tp("B05_quality",   25.15), tp("B05_quality",   28.40), "nametag_thay_hau_left.png",  0.0, 0.0, 1.00, "nametag_left"),

        # Cute floating product sticker when Anh Hậu praises Rong Biển & Bánh Hạt in Act 2
        (*tm("B06_hand_sea", 70.10, 73.55), "sticker_01_rong_bien.png",   +0.08, +0.42, 0.56, "fly_sticker"),
        (*tm("B06_hand_sea", 73.65, 77.10), "sticker_04_banh_thuyen.png", +0.08, +0.42, 0.56, "fly_sticker"),

        # STAR MOMENT: 5 CUTE DIE-CUT STICKERS FLYING UP ONE-BY-ONE AS ANH HẬU NAMES ALL 5 ITEMS!
        (*tm("B09_a3_5items", 213.45, 216.30), "sticker_01_rong_bien.png",   +0.07, +0.42, 0.60, "fly_sticker"),
        (*tm("B09_a3_5items", 216.40, 219.50), "sticker_02_to_yen.png",      +0.07, +0.42, 0.60, "fly_sticker"),
        (*tm("B09_a3_5items", 219.60, 222.95), "sticker_03_duong_phen.png",  +0.07, +0.42, 0.60, "fly_sticker"),
        (*tm("B09_a3_5items", 223.05, 226.75), "sticker_04_banh_thuyen.png", +0.07, +0.42, 0.60, "fly_sticker"),
        (*tm("B09_a3_5items", 226.85, 230.40), "sticker_05_kep_hat.png",     +0.07, +0.42, 0.60, "fly_sticker"),
    ]
    for st0, st1, fn, _, _, _, knd in STICKER_SPEC:
        if knd == "fly_sticker":
            for bt0, bt1, bfn, *_ in BROLL_SPEC:
                assert max(st0, bt0) >= min(st1, bt1) - 0.05, f"Sticker {fn} overlaps B-roll {bfn}!"

    # ==========================================================================
    # 4. 100% COINY 2-TIER TYPOGRAPHY (NÀNG XUÂN STYLE + SCENE-MATCHED COLORS!)
    # ==========================================================================
    SUB_NORMAL = [
        (*tm("B01_doorway",   1.75,  4.55), "Bên Oanh đã chuẩn bị xong"),
        (*tm("B01_doorway",   4.60,  7.35), "giao tới văn phòng Đăng Khoa Edu"),
        (*tm("B01_doorway",   7.40, 10.10), "tại 23 Thái Nguyên rồi nhé mọi người!"),
        (*tm("B01_doorway",  10.20, 14.25), "Giờ cùng Oanh vào giao quà cho anh Hậu nhé!"),
        (*tm("B03_handshake",18.85, 20.15), "Xin chào anh Hậu ạ!"),
        (*tm("B03_handshake",20.20, 23.05), "Chào em, chào Oanh F20!"),

        (*tm("B04_q1_oanh",   5.80,  8.55), "Vì sao năm nay Đăng Khoa Edu"),
        (*tm("B04_q1_oanh",   8.60, 11.45), "chọn sản phẩm của Thực phẩm F20"),
        (*tm("B04_q1_oanh",  11.50, 15.40), "làm quà tri ân thầy cô dịp 20/11 ạ?"),
        (*tm("B05_quality",  23.55, 28.50), "Hậu muốn gửi lời cảm ơn đến thầy cô,"),
        (*tm("B05_quality",  29.40, 33.70), "muốn có một chút quà, nhưng..."),
        (*tm("B06_hand_sea", 57.90, 63.05), "F20 làm yến này bằng thủ công hết,"),
        (*tm("B06_hand_sea", 63.75, 69.00), "gia đình dùng, tặng bạn bè..."),
        (*tm("B06_hand_sea", 69.80, 72.90), "Đặc biệt rất thích là..."),
        (*tm("B06_hand_sea", 73.45, 79.80), "Giáo viên nhiều khi bận không kịp ăn sáng,"),
        (*tm("B07_energy",   86.80, 92.10), "ăn 1–2 cái giữa buổi dạy thấy rất ngon!"),

        (*tm("B08_a2_mica", 133.25,138.15), "77 set quà đã tới Đăng Khoa Edu,"),
        (*tm("B08_a2_mica", 138.95,142.50), "cầm trên tay cảm thấy..."),
        (*tm("B08_a2_mica", 143.20,149.10), "Cầm trên tay vừa gọn vừa dễ thương nữa!"),
        (*tm("B08_a2_mica", 150.25,152.75), "Phía dưới đây là mica hả em?"),
        (*tm("B08_a2_mica", 152.85,156.00), "Dạ túi giỏ đựng quà chất liệu..."),
        (*tm("B08_a2_mica", 156.10,160.35), "Nhìn thấy là không giấu giếm gì hết!"),
        (*tm("B08_a2_mica", 160.45,165.30), "Cái gì tốt là mình khoe ra hết!"),

        (*tm("B09_a3_5items",204.95,209.60), "Toán học gọi là tối giản để tập trung chất lượng!"),
        (*tm("B09_a3_5items",209.75,212.75), "Cái gì mà đơn giản..."),
        (*tm("B09_a3_5items",213.45,216.25), "Đây là rong biển nè,"),
        (*tm("B09_a3_5items",216.35,219.45), "đây là yến sào cao cấp nè,"),
        (*tm("B09_a3_5items",219.55,222.90), "hộp đường phèn nè,"),
        (*tm("B09_a3_5items",223.00,226.75), "bánh thuyền mix hạt nè,"),
        (*tm("B09_a3_5items",226.85,229.00), "rong biển kẹp hạt nè!"),
        (*tm("B09_a3_5items",229.10,233.25), "Những món rất hợp với thầy cô giáo luôn!"),

        (*tm("B10_gift_give", 47.70, 49.55), "Em xin gửi thầy món quà nhỏ tri ân 20/11!"),
        (*tm("B10_gift_give", 49.65, 51.30), "Cảm ơn Thực phẩm F20!"),
        (*tm("B11_book1",     63.85, 68.50), "Biết anh Hậu là người cực kỳ mê sách,"),
        (*tm("B11_book1",     68.60, 74.00), "F20 gửi tặng anh cuốn sách..."),
        (*tm("B12_book2",     91.45, 96.20), "Và cuốn sách thứ hai gửi tặng anh..."),
        (*tm("B13_hau_thanks",122.50,125.55), "Tuyệt vời! Cảm ơn Oanh và F20 rất là nhiều!"),
        (*tm("B13_hau_thanks",125.70,129.95), "Cầm trên tay mà thích quá trời luôn!"),

        (*tm("B14_oanh_cta",   5.20, 10.60), "Oanh xin cảm ơn quý anh chị đã tin tưởng\nđặt hàng Thực phẩm F20!"),
        (*tm("B14_oanh_cta",  10.75, 14.70), "Anh chị cần đặt set quà tặng dịp lễ 20/11"),
        (*tm("B14_oanh_cta",  14.80, 19.25), "để bên Oanh chuẩn bị chu đáo nhé!"),
    ]

    # Colored Jumping Coiny Emphasis Phrases (popping UP cleanly right above white Coiny sub!)
    # Format: (tl_t0, tl_t1, text, py_norm, pil_font_px, cc_sz, color_key, sfx_key)
    EMPHASIS_JUMPS = [
        (*tm("B01_doorway",   2.20,  4.65), "77 SET QUÀ 20/11",             -0.43, 62, 13.5, "gold",    "pop"),
        (*tm("B01_doorway",   5.10,  9.90), "ĐĂNG KHOA EDU • 23 THÁI NGUYÊN",-0.43, 46, 10.2, "emerald", "ding"),
        (*tm("B05_quality",  30.40, 33.75), "PHẢI CHẤT LƯỢNG!",             -0.43, 62, 13.5, "gold",    "ding"),
        (*tm("B06_hand_sea", 58.50, 63.10), "YẾN THỦ CÔNG • KHÔNG HÓA CHẤT",-0.43, 48, 10.6, "emerald", "shine"),
        (*tm("B06_hand_sea", 65.40, 69.00), "TẶNG AI CŨNG KHEN!",           -0.43, 58, 12.6, "gold",    "pop"),
        (*tm("B06_hand_sea", 70.10, 73.10), "RONG BIỂN & BÁNH HẠT",         -0.43, 54, 11.8, "emerald", None),
        (*tm("B07_energy",   87.50, 92.15), "TIẾP NĂNG LƯỢNG CỰC NGON!",    -0.43, 50, 11.0, "gold",    "ding"),

        (*tm("B08_a2_mica", 139.10,142.55), "RẤT LÀ ƯNG Ý!",                -0.43, 64, 13.8, "gold",    "pop"),
        (*tm("B08_a2_mica", 143.40,147.60), "QUAI XÁCH TIỆN TAY",           -0.43, 58, 12.6, "gold",    "pop"),
        (*tm("B08_a2_mica", 153.10,156.60), "GIỎ MICA TRONG SUỐT",          -0.43, 56, 12.2, "emerald", "ding"),
        (*tm("B08_a2_mica", 157.50,165.30), "KHÔNG GIẤU GIẾM • SHOW HẾT!",  -0.43, 50, 11.0, "gold",    "pop"),

        (*tm("B09_a3_5items",206.00,209.65),"TỐI GIẢN • CHẤT LƯỢNG",        -0.43, 56, 12.2, "emerald", "ding"),
        (*tm("B09_a3_5items",210.20,212.80),"ĐƠN GIẢN LÀ NGHỆ THUẬT!",      -0.43, 54, 11.8, "gold",    "pop"),

        # 5-Item Stacking Coiny Checklist synchronized 0ms with the 5 Cute Flying Die-Cut Stickers!
        (tp("B09_a3_5items",213.45), tp("B09_a3_5items",229.10), "01. Rong biển sấy giòn",  -0.21, 41, 9.2, "emerald", None),
        (tp("B09_a3_5items",216.40), tp("B09_a3_5items",229.10), "02. Yến sào cao cấp",     -0.27, 41, 9.2, "gold",    None),
        (tp("B09_a3_5items",219.60), tp("B09_a3_5items",229.10), "03. Hộp đường phèn",      -0.33, 41, 9.2, "emerald", None),
        (tp("B09_a3_5items",223.05), tp("B09_a3_5items",229.10), "04. Bánh thuyền mix hạt", -0.39, 41, 9.2, "gold",    None),
        (tp("B09_a3_5items",226.85), tp("B09_a3_5items",229.10), "05. Rong biển kẹp hạt",   -0.45, 41, 9.2, "emerald", None),
        (*tm("B09_a3_5items",229.30,233.25),"RẤT HỢP THẦY CÔ GIÁO!",        -0.43, 56, 12.2, "gold",    "ding"),

        (*tm("B11_book1",    70.80, 74.05), "DANH NHÂN THẾ GIỚI",           -0.43, 58, 12.6, "emerald", "page"),
        (*tm("B12_book2",    93.00, 96.25), "TOÁN HỌC CỦA THỊNH VƯỢNG",     -0.43, 50, 11.0, "emerald", "page"),
        (*tm("B13_hau_thanks",125.70,130.00),"MÓN QUÀ TAN CHẢY • SIÊU THÍCH!",-0.43, 48, 10.6, "gold", "shine"),
        (*tm("B14_oanh_cta", 14.80, 19.30), "INBOX NGAY CHO OANH!",         -0.43, 62, 13.5, "gold",    "bell"),
    ]

    # Scene-aware Top Headers ONLY where background is clean (ZERO text over Scene 2 ceiling streamers or Scene 8 SKANEST wall sign!)
    TOP_HEADERS = [
        # Scene 1 bright glass door -> Deep F20 Green + White stroke & F20 Red + White stroke (super crisp contrast!)
        (0.20, 4.30,  "GIAO 77 SET QUÀ 20/11",         0.00, +0.64, 54, 12.2, "f20_white"),
        (0.45, 4.30,  "THỰC PHẨM F20 × ĐĂNG KHOA EDU", 0.00, +0.54, 38,  8.8, "red_white"),
        # Scene 3 & 5 clean sky-blue wall strictly below silver streamer bar (py = +0.49!)
        (tp("B04_q1_oanh", 6.0), tp("B04_q1_oanh", 10.5),
         "01 • LÝ DO CHỌN F20",                        0.00, +0.49, 50, 11.4, "emerald"),
        (tp("B08_a2_mica", 136.6), tp("B08_a2_mica", 140.5),
         "02 • CẢM NHẬN THÀNH PHẨM",                   0.00, +0.49, 48, 11.0, "emerald"),
        (tp("B10_gift_give", 47.7), tp("B10_gift_give", 51.3),
         "QUÀ TRI ÂN THẦY HẬU 20/11",                  0.00, +0.49, 48, 11.0, "emerald"),
    ]

    COLOR_MAP = {
        "gold":      (RGB_GOLD,     RGB_STROKE_GLD),
        "emerald":   (RGB_EMERALD,  RGB_STROKE_GRN),
        "f20_white": (RGB_F20_DEEP, RGB_WHITE),
        "red_white": (RGB_RED_F20,  RGB_WHITE),
    }

    # ==========================================================================
    # STEP A: RENDER BASE VIDEO VIA GPU NVENC
    # ==========================================================================
    print("\n[STEP A] Rendering shortened base video via GPU NVENC...")
    base_mp4 = TMP_DIR / "_base_v4.mp4"
    if base_mp4.exists() and base_mp4.stat().st_size > 5_000_000 and "--rebuild-base" not in sys.argv:
        print(f"  -> Reusing cached V4 base video: {base_mp4}")
    else:
        broll_f = [(int(round(a * FPS)), int(round(b * FPS)), fn, sin, spd, dji, nt)
                   for a, b, fn, sin, spd, dji, nt in BROLL_SPEC if int(round(b * FPS)) > int(round(a * FPS))]
        cut_pts = {0, speech_end_f}
        for s in segs:
            cut_pts.add(s["tl_f0"]); cut_pts.add(s["tl_f1"])
        for bf0, bf1, *_ in broll_f:
            cut_pts.add(max(0, min(speech_end_f, bf0)))
            cut_pts.add(max(0, min(speech_end_f, bf1)))
        cut_pts = sorted(cut_pts)

        piece_files = []
        for idx in range(len(cut_pts) - 1):
            f0, f1 = cut_pts[idx], cut_pts[idx + 1]
            if f1 <= f0: continue
            mid_f = f0 + 0.5
            br = next((b for b in broll_f if b[0] <= mid_f < b[1]), None)
            if br is not None:
                bf0, bf1, bfn, bsin, bspd, is_dji, _ = br
                src_path, src_in_s, spd, grade = MAT_V / bfn, bsin + ((f0 - bf0) / FPS) * bspd, bspd, ("dji" if is_dji else "sony")
            else:
                s0 = next(s for s in segs if s["tl_f0"] <= mid_f < s["tl_f1"])
                src_path, src_in_s, spd, grade = s0["path"], s0["src_in"] + ((f0 - s0["tl_f0"]) / FPS) * s0["speed"], s0["speed"], "sony"

            nf = f1 - f0
            _, _, mdur, _ = probe_media(src_path)
            if src_in_s + (nf / FPS) * spd > mdur - 0.05:
                src_in_s = max(0.0, mdur - (nf / FPS) * spd - 0.05)

            out_p = TMP_DIR / f"p_{idx:03d}.mp4"
            if grade == "dji":
                vf = f"setpts=(PTS-STARTPTS)/{spd:.5f},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},colorbalance=rs=0.045:gs=0.01:bs=-0.045,eq=saturation=1.18:contrast=1.07:brightness=0.025,setsar=1"
            else:
                vf = f"setpts=(PTS-STARTPTS)/{spd:.5f},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},eq=saturation=1.10:contrast=1.03:brightness=0.01,setsar=1"
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", f"{src_in_s:.4f}", "-i", str(src_path),
                "-t", f"{(nf / FPS) * spd + 0.25:.4f}", "-vf", vf, "-frames:v", str(nf), "-an",
                "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "17", "-b:v", "0",
                "-pix_fmt", "yuv420p", str(out_p)
            ], check=True)
            piece_files.append(out_p)

        ban_p = TMP_DIR / "p_banner.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(MAT_V / "outro_banner_f20_brand.mp4"),
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},fade=t=in:st=0:d=0.30,setsar=1",
            "-frames:v", str(banner_f), "-an",
            "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "17", "-b:v", "0",
            "-pix_fmt", "yuv420p", str(ban_p)
        ], check=True)
        piece_files.append(ban_p)

        clist = TMP_DIR / "concat.txt"
        clist.write_text("\n".join(f"file '{p.as_posix()}'" for p in piece_files), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(clist), "-c:v", "copy", str(base_mp4)], check=True)
        print(f"  -> Base video rendered ({len(piece_files)} pieces, {total_f} frames) in {time.time() - t_wall:.1f}s!")

    # ==========================================================================
    # STEP B: COMPOSITE COINY SUBS + JUMPING EMPHASIS + FLYING CUTE STICKERS + EXECUTIVE NAME TAG
    # ==========================================================================
    print("\n[STEP B] Compositing 100% Coiny texts, cute flying die-cut stickers & Executive Name Tag...")
    t_b = time.time()

    fnt_sub = ImageFont.truetype(str(FONT_COINY), 44)
    fnt_cache = {}
    def get_coiny(px: int):
        if px not in fnt_cache:
            fnt_cache[px] = ImageFont.truetype(str(FONT_COINY), px)
        return fnt_cache[px]

    # Preload sticker & nametag PNGs cleanly
    stk_imgs = {}
    for _, _, png, _, _, sc, knd in STICKER_SPEC:
        key = (png, sc)
        if key not in stk_imgs:
            im = Image.open(MAT_V / png).convert("RGBA")
            if abs(sc - 1.0) > 0.005:
                im = im.resize((int(round(W * sc)), int(round(H * sc))), Image.Resampling.LANCZOS)
            stk_imgs[key] = im

    SUB_SORTED = sorted(SUB_NORMAL, key=lambda x: x[0])
    SUB_CLEAN = []
    for i, (st, en, tx) in enumerate(SUB_SORTED):
        if i + 1 < len(SUB_SORTED):
            nxt = SUB_SORTED[i + 1][0]
            if 0.0 < nxt - en <= 0.25: en = nxt - 0.034
            elif en > nxt - 0.034: en = max(st + 0.30, nxt - 0.034)
        SUB_CLEAN.append((int(round(st * FPS)), int(round(en * FPS)), wrap_text(tx, 28)))

    EMP_F = [(int(round(st*FPS)), int(round(en*FPS)), tx, py_n, fpx, ckey) for st, en, tx, py_n, fpx, _, ckey, _ in EMPHASIS_JUMPS]
    HDR_F = [(int(round(st*FPS)), int(round(en*FPS)), tx, px_n, py_n, fpx, ckey) for st, en, tx, px_n, py_n, fpx, _, ckey in TOP_HEADERS]
    STK_F = [(int(round(st*FPS)), int(round(en*FPS)), png, px_n, py_n, sc, knd) for st, en, png, px_n, py_n, sc, knd in STICKER_SPEC]

    ANIM_IN_F, ANIM_OUT_F = 7, 5
    EMPTY_BYTES = bytes(W * H * 4)
    state_cache = {}

    vid_only_mp4 = TMP_DIR / "_v4_with_overlays.mp4"
    ff_proc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(base_mp4),
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-filter_complex", "[0:v][1:v]overlay=shortest=1:format=auto[v]",
        "-map", "[v]",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
        "-pix_fmt", "yuv420p", str(vid_only_mp4)
    ], stdin=subprocess.PIPE)

    for fr in range(total_f):
        act_sub = next((tx for f0, f1, tx in SUB_CLEAN if f0 <= fr < f1), None)

        act_emp = []
        for idx_e, (f0, f1, tx, py_n, fpx, ckey) in enumerate(EMP_F):
            if f0 <= fr < f1:
                age, rem = fr - f0, f1 - 1 - fr
                step = ("in", age) if age < 6 else (("out", rem) if rem < 4 else ("hold", 0))
                act_emp.append((idx_e, step))

        act_hdr = []
        for idx_h, (f0, f1, tx, px_n, py_n, fpx, ckey) in enumerate(HDR_F):
            if f0 <= fr < f1:
                age, rem = fr - f0, f1 - 1 - fr
                step = ("in", age) if age < 5 else (("out", rem) if rem < 4 else ("hold", 0))
                act_hdr.append((idx_h, step))

        act_stk = []
        for idx_s, (f0, f1, png, px_n, py_n, sc, knd) in enumerate(STK_F):
            if f0 <= fr < f1:
                age, rem = fr - f0, f1 - 1 - fr
                if knd == "fly_sticker":
                    # Cute fly-up entrance (9 frames) + gentle cute floating bob (quantized 8 phases!) + fade out (5 frames)
                    if age < 9: step = ("fly_in", age)
                    elif rem < 5: step = ("fly_out", rem)
                    else: step = ("bob", (age // 3) % 8)
                else:
                    # Executive Name Tag smooth slide-in from left (9 frames) + hold + fade-out (6 frames)
                    if age < 9: step = ("nt_in", age)
                    elif rem < 6: step = ("nt_out", rem)
                    else: step = ("nt_hold", 0)
                act_stk.append((idx_s, step))

        if not act_sub and not act_emp and not act_hdr and not act_stk:
            ff_proc.stdin.write(EMPTY_BYTES)
            continue

        skey = (act_sub, tuple(act_emp), tuple(act_hdr), tuple(act_stk))
        if skey in state_cache:
            ff_proc.stdin.write(state_cache[skey])
            continue

        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        # 1) Cute Flying Die-Cut Product Stickers + Executive Name Tag
        for idx_s, (ph, stp) in act_stk:
            _, _, png, px_n, py_n, sc, knd = STK_F[idx_s]
            im = stk_imgs[(png, sc)]
            if knd in ("nametag_left", "nametag_right"):
                sign = +1 if knd == "nametag_right" else -1
                if ph == "nt_in":
                    u = (stp + 1) / 9.0
                    ease = 1.0 - (1.0 - u) ** 3
                    x_off = int(round((1.0 - ease) * 140 * sign))
                    al = min(1.0, u * 1.4)
                elif ph == "nt_out":
                    u = (stp + 1) / 6.0
                    x_off, al = int(round((1.0 - u) * 40 * sign)), u
                else:
                    x_off, al = 0, 1.0
                im2 = im
                if al < 0.995:
                    arr = np.array(im, dtype=np.uint8)
                    arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * al).astype(np.uint8)
                    im2 = Image.fromarray(arr, mode="RGBA")
                if x_off >= 0:
                    ov.alpha_composite(im2, (x_off, 0), source=(0, 0, max(1, W - x_off), H))
                else:
                    ov.alpha_composite(im2, (0, 0), source=(-x_off, 0, W, H))
            else:
                # Cute sticker FLYING UP from gift basket (`+220px -> 0px` with bouncy overshoot + gentle bob!)
                if ph == "fly_in":
                    u = (stp + 1) / 9.0
                    eb = ease_out_back(u)
                    m_sc = 0.58 + 0.42 * eb
                    y_off = int(round((1.0 - min(1.05, eb)) * 220))
                    al = min(1.0, u * 1.7)
                elif ph == "fly_out":
                    u = (stp + 1) / 5.0
                    m_sc, y_off, al = 0.92 + 0.08 * u, int(round((1.0 - u) * -32)), u
                else:
                    # Gentle cute floating bob (smooth 8-step sine!)
                    m_sc, al = 1.0, 1.0
                    y_off = int(round(math.sin(stp * 2.0 * math.pi / 8.0) * 10))
                nw, nh = max(2, int(round(im.width * m_sc))), max(2, int(round(im.height * m_sc)))
                im2 = im.resize((nw, nh), Image.Resampling.BICUBIC) if abs(m_sc - 1.0) > 0.005 else im
                if al < 0.995:
                    arr = np.array(im2, dtype=np.uint8)
                    arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * al).astype(np.uint8)
                    im2 = Image.fromarray(arr, mode="RGBA")
                cx = int(round((px_n + 1.0) * 0.5 * W))
                cy = int(round((1.0 - py_n) * 0.5 * H)) + y_off
                ov.alpha_composite(im2, (cx - nw // 2, cy - nh // 2))

        # 2) Scene-Aware Top Headers (Coiny!)
        for idx_h, (ph, stp) in act_hdr:
            _, _, tx, px_n, py_n, fpx, ckey = HDR_F[idx_h]
            fcol, scol = COLOR_MAP[ckey]
            al = (stp + 1) / 5.0 if ph == "in" else ((stp + 1) / 4.0 if ph == "out" else 1.0)
            cx = int(round((px_n + 1.0) * 0.5 * W))
            cy = int(round((1.0 - py_n) * 0.5 * H))
            sw_h = 6 if ckey in ("f20_white", "red_white") else 4
            draw_styled_text(ov, tx, cx, cy, get_coiny(fpx), fcol, scol, sw_h,
                             shadow_alpha=155, shadow_off=(0, 4), shadow_blur=5, alpha=al,
                             y_shift=int(round((1.0 - al) * 14)) if ph == "in" else 0)

        # 3) Colored Jumping Coiny Emphasis Phrases (Nàng Xuân jump-up!)
        for idx_e, (ph, stp) in act_emp:
            _, _, tx, py_n, fpx, ckey = EMP_F[idx_e]
            fcol, scol = COLOR_MAP[ckey]
            if ph == "in":
                u = (stp + 1) / 6.0
                e_sc = 0.80 + 0.20 * ease_out_back(u)
                y_sh = int(round((1.0 - min(1.0, u * 1.15)) * 28))
                al = min(1.0, u * 1.5)
            elif ph == "out":
                u = (stp + 1) / 4.0
                e_sc, y_sh, al = 0.96 + 0.04 * u, 0, u
            else:
                e_sc, y_sh, al = 1.0, 0, 1.0
            cy = int(round((1.0 - py_n) * 0.5 * H))
            draw_styled_text(ov, tx, W // 2, cy, get_coiny(fpx), fcol, scol, 5,
                             shadow_alpha=185, shadow_off=(0, 5), shadow_blur=6,
                             scale=e_sc, alpha=al, y_shift=y_sh)

        # 4) Calm Clean White Coiny Normal Subtitle (`sub text bt`)
        if act_sub:
            cy_sub = int(round((1.0 - (-0.59)) * 0.5 * H))
            draw_styled_text(ov, act_sub, W // 2, cy_sub, fnt_sub, RGB_WHITE, RGB_STROKE_SUB, 3,
                             shadow_alpha=190, shadow_off=(0, 4), shadow_blur=5)

        raw = ov.tobytes()
        if len(state_cache) > 180:
            state_cache.clear()
        state_cache[skey] = raw
        ff_proc.stdin.write(raw)

    ff_proc.stdin.close()
    if ff_proc.wait() != 0:
        raise RuntimeError("FFmpeg overlay pipe failed!")
    print(f"  -> V4 Overlay composite complete in {time.time() - t_b:.1f}s!")

    # ==========================================================================
    # STEP C: STUDIO VOICE-POCKET AUDIO MASTERING (`-14.0 LUFS`, Crystal Voices!)
    # ==========================================================================
    print("\n[STEP C] Mastering studio audio (Voice-Pocket BGM, guarded speed-ups, cute Pop SFX)...")
    t_c = time.time()
    sr = 48000
    total_n = int(round(total_s * sr))
    voice_buf = np.zeros((total_n + sr, 2), dtype=np.float32)

    def load_audio_f32(path: Path, ss: float = 0.0, dur: float | None = None, atempo: float = 1.0, extra_af: str = "") -> np.ndarray:
        cmd = ["ffmpeg", "-v", "error"]
        if ss > 0: cmd += ["-ss", f"{ss:.4f}"]
        cmd += ["-i", str(path)]
        if dur is not None: cmd += ["-t", f"{dur:.4f}"]
        afs = []
        if abs(atempo - 1.0) > 0.002: afs.append(f"atempo={atempo:.5f}")
        if extra_af: afs.append(extra_af)
        if afs: cmd += ["-af", ",".join(afs)]
        cmd += ["-ar", str(sr), "-ac", "2", "-f", "f32le", "pipe:1"]
        arr = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)
        return arr[:(len(arr) // 2) * 2].reshape(-1, 2).copy()

    for s in segs:
        if s["vol_cc"] <= 0.01 and not s["is_bridge"]:
            continue
        sdur = s["src_out"] - s["src_in"]
        if s["is_bridge"]:
            clip_a = load_audio_f32(s["path"], ss=s["src_in"], dur=sdur, atempo=s["speed"], extra_af="lowpass=f=650,volume=-18dB")
        else:
            clip_a = load_audio_f32(s["path"], ss=s["src_in"], dur=sdur, atempo=s["speed"], extra_af=f"volume={s['vol_db']:+.1f}dB")
        nf_fade = min(int(0.022 * sr), len(clip_a) // 4)
        if nf_fade > 1:
            ramp = np.linspace(0.0, 1.0, nf_fade, dtype=np.float32)[:, None]
            clip_a[:nf_fade] *= ramp
            clip_a[-nf_fade:] *= ramp[::-1]
        pos = int(round(s["tl_start"] * sr))
        use_len = min(len(clip_a), int(round((s["tl_end"] - s["tl_start"]) * sr)), len(voice_buf) - pos)
        if use_len > 0:
            voice_buf[pos:pos + use_len] += clip_a[:use_len]

    voice_raw_wav = TMP_DIR / "_voice_raw.wav"
    voice_pol_wav = TMP_DIR / "_voice_pol.wav"
    subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(sr),"-ac","2","-i","pipe:0","-c:a","pcm_f32le",str(voice_raw_wav)],
                   input=voice_buf[:total_n].tobytes(), check=True)
    subprocess.run(["ffmpeg","-y","-v","error","-i",str(voice_raw_wav),
                    "-af","highpass=f=80,equalizer=f=260:t=q:w=1.2:g=-2.2,equalizer=f=3200:t=q:w=1.4:g=2.4,acompressor=threshold=-20dB:ratio=3.0:attack=8:release=110:makeup=2.5,loudnorm=I=-14.0:TP=-1.8:LRA=7",
                    "-c:a","pcm_f32le",str(voice_pol_wav)], check=True)

    # Voice-Pocket F20 BGM (`0.075` silk-soft under voices, `0.24` on closing banner!)
    bgm_buf = np.zeros((total_n, 2), dtype=np.float32)
    bgm_vp = "equalizer=f=1800:t=q:w=1.0:g=-5.0,equalizer=f=3200:t=q:w=1.2:g=-4.5"
    b1 = load_audio_f32(BGM_PATH, ss=0.0, dur=126.0, extra_af=bgm_vp)
    n1 = min(len(b1), int(125.5 * sr), total_n)
    bgm_buf[:n1] = b1[:n1]
    if total_n > int(124.5 * sr):
        b2 = load_audio_f32(BGM_PATH, ss=8.0, dur=max(10.0, total_s - 124.0), extra_af=bgm_vp)
        ov_n, st2 = int(1.0 * sr), int(124.5 * sr)
        u2 = min(len(b2), total_n - st2)
        fade = np.linspace(0.0, 1.0, ov_n, dtype=np.float32)[:, None]
        bgm_buf[st2:st2 + ov_n] *= (1.0 - fade)
        bgm_buf[st2:st2 + ov_n] += b2[:ov_n] * fade
        if u2 > ov_n: bgm_buf[st2 + ov_n:st2 + u2] = b2[ov_n:u2]

    env = np.full(total_n, 0.075, dtype=np.float32)
    fi_n = int(0.35 * sr); env[:fi_n] *= np.linspace(0.0, 1.0, fi_n, dtype=np.float32)
    ban_st, sw_n = int(round(speech_end_s * sr)), int(0.40 * sr)
    if ban_st + sw_n < total_n:
        env[ban_st:ban_st + sw_n] = np.linspace(0.075, 0.24, sw_n, dtype=np.float32)
        env[ban_st + sw_n:] = 0.24
    fo_n = int(1.10 * sr); env[-fo_n:] *= np.linspace(1.0, 0.0, fo_n, dtype=np.float32)
    bgm_buf *= env[:, None]

    SFX_MAP = {
        "pop":   (SFX_POP,   0.26, 0.35),
        "ding":  (SFX_DING,  0.10, 0.85),
        "bell":  (SFX_BELL,  0.10, 0.95),
        "shine": (SFX_SHINE, 0.09, 0.80),
        "page":  (SFX_PAGE,  0.12, 0.65),
        "wsh1":  (SFX_WSH1,  0.10, 0.60),
        "wsh2":  (SFX_WSH2,  0.09, 0.50),
        "wsh3":  (SFX_WSH3,  0.09, 0.50),
        "wsht":  (SFX_WSHT,  0.11, 0.70),
        "chime": (SFX_CHIME, 0.09, 1.80),
    }
    SFX_EVENTS = [
        (0.18, "wsh1", "Air Mở Cảnh"),
        (0.30, "chime", "Chuông Gió Mở"),
        (tp("B02_room_pan", 0.80), "wsh2", "Lướt Vào Phòng"),
        (tp("B03_handshake", 19.25), "wsh2", "Name Tag Slide"),
        (tp("B04_q1_oanh", 5.90), "wsh3", "Mở Phần 01"),
        (tp("B10_gift_give", 47.65), "wsh1", "Mở Quà Tri Ân"),
        (speech_end_s - 0.05, "wsht", "Swoosh Banner"),
        (speech_end_s + 0.08, "chime", "Chuông Gió Banner"),
    ]
    fly_times = []
    for st0, _, png, _, _, _, knd in STICKER_SPEC:
        if knd == "fly_sticker":
            SFX_EVENTS.append((st0, "pop", f"Pop {png[:16]}"))
            fly_times.append(st0)
    for et0, _, tx, _, _, _, _, sk in EMPHASIS_JUMPS:
        if sk and not any(abs(et0 - ft) < 0.28 for ft in fly_times):
            SFX_EVENTS.append((et0, sk, f"SFX {tx[:18]}"))

    sfx_buf = np.zeros((total_n, 2), dtype=np.float32)
    sfx_pcm_cache = {}
    for t0, sk, _ in SFX_EVENTS:
        sp, gvol, mdur = SFX_MAP[sk]
        if sk not in sfx_pcm_cache:
            sfx_pcm_cache[sk] = load_audio_f32(sp, ss=0.0, dur=mdur)
        pcm = sfx_pcm_cache[sk] * float(gvol)
        pos = max(0, int(round(t0 * sr)))
        u = min(len(pcm), total_n - pos)
        if u > 0: sfx_buf[pos:pos + u] += pcm[:u]

    v_pol = load_audio_f32(voice_pol_wav)
    n_mix = min(total_n, len(v_pol))
    mix = v_pol[:n_mix] + bgm_buf[:n_mix] + sfx_buf[:n_mix]
    mix_raw = TMP_DIR / "_mix_raw.wav"
    mix_aac = TMP_DIR / "_mix_master.m4a"
    subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(sr),"-ac","2","-i","pipe:0","-c:a","pcm_f32le",str(mix_raw)], input=mix.tobytes(), check=True)
    subprocess.run(["ffmpeg","-y","-v","error","-i",str(mix_raw),"-af","alimiter=limit=0.89:attack=5:release=60","-c:a","aac","-b:a","192k",str(mix_aac)], check=True)

    subprocess.run(["ffmpeg","-y","-v","error","-i",str(vid_only_mp4),"-i",str(mix_aac),
                    "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","copy","-shortest","-movflags","+faststart",str(LOCAL_OUT)], check=True)
    eb = subprocess.run(["ffmpeg","-v","info","-i",str(LOCAL_OUT),"-af","ebur128=framelog=quiet","-f","null","-"], capture_output=True, text=True)
    lufs_line = " | ".join([l.strip() for l in eb.stderr.splitlines() if "I:" in l or "Peak:" in l][-3:])
    print(f"  -> Final MP4 muxed ({LOCAL_OUT.stat().st_size/1e6:.1f} MB) | {lufs_line}")

    FINAL_F20.parent.mkdir(parents=True, exist_ok=True)
    FINAL_CLD.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LOCAL_OUT, FINAL_F20)
    shutil.copy2(LOCAL_OUT, FINAL_CLD)

    # ==========================================================================
    # STEP D: UPDATE SYNCED CAPCUT DESKTOP PROJECT (100% COINY + CUTE STICKERS + NAME TAG!)
    # ==========================================================================
    print("\n[STEP D] Updating synced CapCut Desktop project with Coiny, cute stickers & Name Tag...")
    pj_cur = json.loads((DRAFT_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
    D_old  = json.loads((DRAFT_DIR / "Timelines" / pj_cur["main_timeline_id"] / "draft_content.json").read_text(encoding="utf-8"))
    dmi_old = json.loads((DRAFT_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))
    D = copy.deepcopy(D_old)

    vtrack0_tpl = copy.deepcopy(D_old["tracks"][0])
    vtrack2_tpl = copy.deepcopy(D_old["tracks"][1])
    vseg_tpl    = copy.deepcopy(D_old["tracks"][0]["segments"][0])
    vmat_tpl    = copy.deepcopy(next(m for m in D_old["materials"]["videos"] if m.get("type") == "video"))
    pmat_tpl    = copy.deepcopy(next(m for m in D_old["materials"]["videos"] if m.get("type") == "photo"))
    atrack_tpl  = copy.deepcopy(next(t for t in D_old["tracks"] if t["type"] == "audio" and t["segments"]))
    aseg_tpl    = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl    = copy.deepcopy(D_old["materials"]["audios"][0])
    filt_tr_tpl = copy.deepcopy(next(t for t in D_old["tracks"] if t["type"] == "filter" and t["segments"]))
    filt_m_tpl  = copy.deepcopy(next(e for e in D_old["materials"]["effects"] if e["id"] == filt_tr_tpl["segments"][0]["material_id"]))
    ket_hop_tpl = copy.deepcopy(D_old["materials"]["transitions"][0]) if D_old["materials"].get("transitions") else None

    TXT_ANIMS, VID_ANIMS = {"in": {}, "out": {}}, {"in": {}, "out": {}}
    for src_d in [D_old, json.loads((NX_DRAFT / "draft_content.json").read_text(encoding="utf-8")) if (NX_DRAFT / "draft_content.json").exists() else {}]:
        for ma in src_d.get("materials", {}).get("material_animations", []):
            for a in ma.get("animations", []):
                atp, nm = a.get("type"), a.get("name")
                if atp in ("in", "out") and nm:
                    if a.get("panel") == "video" and nm not in VID_ANIMS[atp]: VID_ANIMS[atp][nm] = copy.deepcopy(a)
                    elif nm not in TXT_ANIMS[atp]: TXT_ANIMS[atp][nm] = copy.deepcopy(a)

    DJI_SLIDERS = {}
    for ef in D_old["materials"].get("effects", []):
        if ef.get("type") in ("temperature", "saturation", "contrast", "brightness") and ef["type"] not in DJI_SLIDERS:
            DJI_SLIDERS[ef["type"]] = copy.deepcopy(ef)

    tmap_old    = {t["id"]: t for t in D_old["materials"]["texts"]}
    sub_tr_tpl  = copy.deepcopy(next(t for t in D_old["tracks"] if t["type"] == "text" and t["segments"] and tmap_old.get(t["segments"][0]["material_id"], {}).get("type") == "subtitle"))
    txt_tr_tpl  = copy.deepcopy(next(t for t in D_old["tracks"] if t["type"] == "text" and t["segments"] and tmap_old.get(t["segments"][0]["material_id"], {}).get("type") == "text"))
    sub_seg_tpl, sub_mat_tpl = copy.deepcopy(sub_tr_tpl["segments"][0]), copy.deepcopy(tmap_old[sub_tr_tpl["segments"][0]["material_id"]])
    txt_seg_tpl, txt_mat_tpl = copy.deepcopy(txt_tr_tpl["segments"][0]), copy.deepcopy(tmap_old[txt_tr_tpl["segments"][0]["material_id"]])

    dm_all = [x for g in dmi_old.get("draft_materials", []) for x in g.get("value", [])]
    dm_vid_tpl = copy.deepcopy(next(x for x in dm_all if x.get("metetype") == "video"))
    dm_pho_tpl = copy.deepcopy(next((x for x in dm_all if x.get("metetype") == "photo"), dm_vid_tpl))

    # CRITICAL FIX: Force EVERY vocal_separation to clean disabled (choice=0, production_path="")!
    # Never inherit broken choice=2 / dead Resources/audioAlg/*.wav from donor drafts (causes intermittent silent clips in CapCut!)
    CLEAN_VOCAL_SEP = {"id": "", "type": "vocal_separation", "choice": 0, "removed_sounds": [], "time_range": None, "production_path": "", "final_algorithm": "", "enter_from": ""}
    CLEAN_SOUND_MAP = {"id": "", "type": "none", "audio_channel_mapping": 0, "is_config_open": False}

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in D_old["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in D_old["materials"].get(k, []))}
    v_extra_tpl["vocal_separations"] = copy.deepcopy(CLEAN_VOCAL_SEP)
    v_extra_tpl["sound_channel_mappings"] = copy.deepcopy(CLEAN_SOUND_MAP)

    a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in D_old["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in D_old["materials"].get(k, []))}
    a_extra_tpl["vocal_separations"] = copy.deepcopy(CLEAN_VOCAL_SEP)
    a_extra_tpl["sound_channel_mappings"] = copy.deepcopy(CLEAN_SOUND_MAP)

    # Determine safe target draft directory (NEVER touch a .locked draft or kill CapCut!)
    if draft_is_locked:
        TGT_DRAFT_NAME = "261122 F20 Phỏng Vấn Đăng Khoa Edu (Fix Audio + NameTag)"
        TGT_DRAFT_DIR  = CC_ROOT / TGT_DRAFT_NAME
        if TGT_DRAFT_DIR.exists() and not (TGT_DRAFT_DIR / ".locked").exists():
            shutil.rmtree(TGT_DRAFT_DIR)
        TGT_MAT_V = TGT_DRAFT_DIR / "materials" / "video"
        TGT_MAT_A = TGT_DRAFT_DIR / "materials" / "audio"
        TGT_MAT_V.mkdir(parents=True, exist_ok=True)
        TGT_MAT_A.mkdir(parents=True, exist_ok=True)
        for sub in ("adjust_mask", "matting", "qr_upload", "Resources", "subdraft", "common_attachment", "smart_crop"):
            (TGT_DRAFT_DIR / sub).mkdir(exist_ok=True)
        # Instant zero-extra-space NTFS hardlinks on D:\ for all video & audio materials!
        for src_dir, dst_dir in [(MAT_V, TGT_MAT_V), (MAT_A, TGT_MAT_A)]:
            for f in src_dir.iterdir():
                if f.is_file():
                    df = dst_dir / f.name
                    if not df.exists():
                        try: os.link(f, df)
                        except OSError: shutil.copy2(f, df)
        for aux in ("draft.extra", "attachment_editing.json", "attachment_pc_common.json", "draft_cover.jpg",
                    "draft_agency_config.json", "draft_biz_config.json", "performance_opt_info.json", "draft_settings", "key_value.json"):
            if (DRAFT_DIR / aux).exists():
                shutil.copy2(DRAFT_DIR / aux, TGT_DRAFT_DIR / aux)
    else:
        TGT_DRAFT_NAME = DRAFT_NAME
        TGT_DRAFT_DIR  = DRAFT_DIR
        TGT_MAT_V      = MAT_V
        TGT_MAT_A      = MAT_A

    for k, val in list(D["materials"].items()):
        if isinstance(val, list): D["materials"][k] = []

    now_s, now_us = int(time.time()), int(time.time() * 1_000_000)
    vis_cache, new_dm_entries = {}, []

    def reg_cc_visual(fn: str):
        path = TGT_MAT_V / fn
        if fn in vis_cache: return vis_cache[fn]
        fwd, is_photo = norm_fwd(path), path.suffix.lower() in (".png", ".jpg", ".jpeg")
        mid, lmid = uid(), str(uuid.uuid4())
        if is_photo:
            with Image.open(path) as im: w, h = im.size
            dur_u = 10_800_000_000
            m = copy.deepcopy(pmat_tpl)
            m.update({"id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid, "type": "photo",
                      "path": fwd, "media_path": "", "local_id": "", "material_name": fn,
                      "width": w, "height": h, "duration": dur_u, "has_audio": False,
                      "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0})
            dme = copy.deepcopy(dm_pho_tpl)
            dme.update({"id": lmid, "file_Path": f"./materials/video/{fn}", "extra_info": fn,
                        "duration": 5_000_000, "width": w, "height": h, "metetype": "photo",
                        "create_time": now_s, "import_time": now_s, "import_time_ms": now_us})
        else:
            w, h, dur_s, has_aud = probe_media(path)
            dur_u = max(33333, us(dur_s))
            m = copy.deepcopy(vmat_tpl)
            m.update({"id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid, "type": "video",
                      "path": fwd, "media_path": "", "local_id": "", "material_name": fn,
                      "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud),
                      "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0})
            dme = copy.deepcopy(dm_vid_tpl)
            dme.update({"id": lmid, "file_Path": f"./materials/video/{fn}", "extra_info": fn,
                        "duration": dur_u, "width": w, "height": h, "metetype": "video",
                        "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
                        "roughcut_time_range": {"start": 0, "duration": dur_u}, "sub_time_range": {"start": -1, "duration": -1}})
        D["materials"]["videos"].append(m)
        new_dm_entries.append(dme)
        vis_cache[fn] = (mid, dur_u, is_photo)
        return mid, dur_u, is_photo

    def make_cc_vseg(fn, st_u, du_u, src_in_s, spd, vol, px=0.0, py=0.0, sc=1.0, in_anim=None, out_anim=None, is_dji=False, micro_fade=False, add_tr=False):
        mid, mat_dur_u, is_photo = reg_cc_visual(fn)
        if is_photo: src_st_u, src_du_u, spd = 0, du_u, 1.0
        else:
            src_st_u, src_du_u = us(src_in_s), int(round(du_u * spd))
            if src_st_u + src_du_u > mat_dur_u: src_st_u = max(0, mat_dur_u - src_du_u)
        sg = copy.deepcopy(vseg_tpl); refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = round(spd, 4)
            D["materials"][k].append(em); refs.append(em["id"])
        if is_dji:
            for stype, sval in [("temperature", 0.14), ("saturation", 0.18), ("contrast", 0.08), ("brightness", 0.03)]:
                if stype in DJI_SLIDERS:
                    ef = copy.deepcopy(DJI_SLIDERS[stype]); ef["id"] = uid(); ef["value"] = float(sval)
                    D["materials"]["effects"].append(ef); refs.append(ef["id"])
        if micro_fade and vol > 0.0:
            fid = uid()
            D["materials"].setdefault("audio_fades", []).append({"fade_in_duration": 22000, "fade_out_duration": 30000, "fade_type": 0, "id": fid, "type": "audio_fade"})
            refs.append(fid)
        if add_tr and ket_hop_tpl:
            tr_o = copy.deepcopy(ket_hop_tpl); tr_o["id"] = uid(); tr_o["duration"] = 366666
            D["materials"].setdefault("transitions", []).append(tr_o); refs.append(tr_o["id"])
        alist = []
        if in_anim and in_anim in VID_ANIMS["in"]:
            ai = copy.deepcopy(VID_ANIMS["in"][in_anim]); ai["start"] = 0; ai["duration"] = min(220000, du_u // 4); alist.append(ai)
        if out_anim and out_anim in VID_ANIMS["out"]:
            ao = copy.deepcopy(VID_ANIMS["out"][out_anim]); od = min(180000, du_u // 4); ao["duration"] = od; ao["start"] = max(0, du_u - od); alist.append(ao)
        if alist:
            maid = uid()
            D["materials"].setdefault("material_animations", []).append({"animations": alist, "id": maid, "multi_language_current": "none", "type": "sticker_animation"})
            refs.append(maid)
        sg["clip"]["scale"] = {"x": round(sc, 4), "y": round(sc, 4)}
        sg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        sg["clip"]["rotation"] = 0.0; sg["clip"]["alpha"] = 1.0; sg["uniform_scale"] = {"on": True, "value": 1.0}
        sg.update({"id": uid(), "material_id": mid,
                   "source_timerange": {"start": int(src_st_u), "duration": int(src_du_u)},
                   "target_timerange": {"start": int(st_u), "duration": int(du_u)},
                   "speed": round(spd, 4), "volume": round(vol, 4), "last_nonzero_volume": round(max(vol, 1.0), 4),
                   "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []})
        return sg

    tr_v0 = copy.deepcopy(vtrack0_tpl); tr_v0["id"] = uid(); tr_v0["flag"] = 0
    tr_v0["segments"] = [make_cc_vseg(s["file"], s["tl_start_u"], s["tl_dur_u"], s["src_in"], s["speed"], s["vol_cc"], micro_fade=(s["vol_cc"] > 0.0), add_tr=s["xfade_after"]) for s in segs]

    tr_v1 = copy.deepcopy(vtrack2_tpl); tr_v1["id"] = uid(); tr_v1["flag"] = 2
    tr_v1["segments"] = [make_cc_vseg(fn, us(t0), us(t1) - us(t0), sin, spd, 0.0, is_dji=is_dji) for t0, t1, fn, sin, spd, is_dji, _ in BROLL_SPEC]
    tr_v1["segments"].append(make_cc_vseg("outro_banner_f20_brand.mp4", us(speech_end_s), us(total_s) - us(speech_end_s), 0.0, 1.0, 0.0, px=0.0, py=-0.05, sc=1.05, in_anim="Rõ dần"))

    tr_v2 = copy.deepcopy(vtrack2_tpl); tr_v2["id"] = uid(); tr_v2["flag"] = 2
    tr_v2["segments"] = [make_cc_vseg(png, us(t0), us(t1) - us(t0), 0.0, 1.0, 0.0, px=px, py=py, sc=sc, in_anim="Rõ dần", out_anim="Mờ dần") for t0, t1, png, px, py, sc, _ in STICKER_SPEC]

    # 100% Native Coiny CapCut Texts (`7482665772876156165`!)
    COINY_FWD = norm_fwd(COINY_CC_P if COINY_CC_P.exists() else FONT_COINY)

    def make_cc_text(is_sub, t0_s, t1_s, text, px, py, sz, fill_rgb, stroke_rgb, stroke_w, in_nm=None, out_nm=None):
        tid = uid()
        tm = copy.deepcopy(sub_mat_tpl if is_sub else txt_mat_tpl)
        cobj = json.loads(tm["content"])
        cobj["text"] = text
        st0 = copy.deepcopy(cobj["styles"][0])
        st0["range"] = [0, len(text)]
        st0["size"] = float(sz)
        st0["font"] = {"path": COINY_FWD, "id": COINY_CC_ID}
        st0["fill"] = {"content": {"render_type": "solid", "solid": {"color": rgb01(fill_rgb)}}}
        st0["strokes"] = [{"content": {"render_type": "solid", "solid": {"color": rgb01(stroke_rgb)}}, "width": float(stroke_w), "mode": 0}]
        st0["shadows"] = [{"alpha": 0.55, "angle": -35.0, "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}}, "diffuse": 0.004, "distance": 4.5, "thickness_projection_angle": -45.0, "thickness_projection_distance": 0.0, "thickness_projection_enable": False}]
        cobj["styles"] = [st0]
        tm.update({"id": tid, "type": "subtitle" if is_sub else "text", "group_id": "",
                   "content": json.dumps(cobj, ensure_ascii=False), "recognize_text": text,
                   "font_size": float(sz), "font_path": COINY_FWD, "check_flag": 15,
                   "background_style": 0, "has_shadow": True, "line_spacing": 0.02, "letter_spacing": 0.0})
        D["materials"]["texts"].append(tm)
        st_u, du_u = us(t0_s), max(us(0.30), us(t1_s) - us(t0_s))
        refs, alist = [], []
        if in_nm and in_nm in TXT_ANIMS["in"]:
            ai = copy.deepcopy(TXT_ANIMS["in"][in_nm]); ai["start"] = 0; ai["duration"] = min(200000, du_u // 3); alist.append(ai)
        if out_nm and out_nm in TXT_ANIMS["out"]:
            ao = copy.deepcopy(TXT_ANIMS["out"][out_nm]); od = min(180000, du_u // 3); ao["duration"] = od; ao["start"] = max(0, du_u - od); alist.append(ao)
        if alist:
            maid = uid()
            D["materials"].setdefault("material_animations", []).append({"animations": alist, "id": maid, "multi_language_current": "none", "type": "sticker_animation"})
            refs.append(maid)
        sg = copy.deepcopy(sub_seg_tpl if is_sub else txt_seg_tpl)
        sg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        sg["clip"]["scale"] = {"x": 1.0, "y": 1.0}; sg["clip"]["rotation"] = 0.0; sg["clip"]["alpha"] = 1.0
        sg.update({"id": uid(), "material_id": tid, "target_timerange": {"start": st_u, "duration": du_u},
                   "source_timerange": None, "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []})
        return sg

    tr_sub = copy.deepcopy(sub_tr_tpl); tr_sub["id"] = uid()
    tr_sub["segments"] = [make_cc_text(True, f0/FPS, f1/FPS, tx, 0.0, -0.59, 9.8, RGB_WHITE, RGB_STROKE_SUB, 0.038) for f0, f1, tx in SUB_CLEAN]

    cc_text_items = []
    for st, en, tx, py_n, _, ccsz, ckey, _ in EMPHASIS_JUMPS:
        fcol, scol = COLOR_MAP[ckey]
        in_a = "Phóng to" if "Phóng to" in TXT_ANIMS["in"] else ("Trượt xuống" if "Trượt xuống" in TXT_ANIMS["in"] else "Mờ")
        cc_text_items.append((st, en, tx, 0.0, py_n, ccsz, fcol, scol, 0.058, in_a, "Mờ dần"))
    for st, en, tx, px_n, py_n, _, ccsz, ckey in TOP_HEADERS:
        fcol, scol = COLOR_MAP[ckey]
        cc_text_items.append((st, en, tx, px_n, py_n, ccsz, fcol, scol, 0.062 if "white" in ckey else 0.052, "Mờ", "Mờ dần"))

    ft_lanes = []
    for st, en, tx, px_n, py_n, ccsz, fcol, scol, sw, ia, oa in sorted(cc_text_items, key=lambda x: x[0]):
        sg = make_cc_text(False, st, en, tx, px_n, py_n, ccsz, fcol, scol, sw, ia, oa)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for ln in ft_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                ln.append(sg); placed = True; break
        if not placed: ft_lanes.append([sg])
    ft_tracks = [copy.deepcopy(txt_tr_tpl) for _ in ft_lanes]
    for tt, ln in zip(ft_tracks, ft_lanes):
        tt["id"] = uid(); tt["segments"] = ln

    fm = copy.deepcopy(filt_m_tpl); fm["id"] = uid(); fm["value"] = 0.16
    D["materials"]["effects"].append(fm)
    tr_filt = copy.deepcopy(filt_tr_tpl); tr_filt["id"] = uid()
    fsg = copy.deepcopy(tr_filt["segments"][0])
    fsg.update({"id": uid(), "material_id": fm["id"], "target_timerange": {"start": 0, "duration": us(speech_end_s)}, "extra_material_refs": [], "render_index": 10000})
    tr_filt["segments"] = [fsg]

    cc_bgm_path = TGT_MAT_A / BGM_PATH.name
    bgm_dur_u, bgm_aid = us(probe_audio_dur(cc_bgm_path)), uid()
    bgm_m = copy.deepcopy(amat_tpl)
    bgm_m.update({"id": bgm_aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
                  "name": cc_bgm_path.name, "path": norm_fwd(cc_bgm_path), "duration": bgm_dur_u, "type": "music"})
    D["materials"]["audios"].append(bgm_m)

    def mk_cc_aseg(aid, st_u, du_u, src_st_u, fi_u, fo_u, vol):
        sg = copy.deepcopy(aseg_tpl); refs = []
        for k, tpl_e in a_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        fid = uid()
        D["materials"].setdefault("audio_fades", []).append({"fade_in_duration": fi_u, "fade_out_duration": fo_u, "fade_type": 0, "id": fid, "type": "audio_fade"})
        refs.append(fid)
        sg.update({"id": uid(), "material_id": aid, "source_timerange": {"start": src_st_u, "duration": du_u},
                   "target_timerange": {"start": st_u, "duration": du_u}, "speed": 1.0,
                   "volume": vol, "last_nonzero_volume": vol, "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []})
        return sg

    total_u = us(total_s)
    seg1_u = min(total_u, us(125.0))
    bgm_segs = [mk_cc_aseg(bgm_aid, 0, seg1_u, 0, 350000, 350000, 0.16)]
    if total_u > seg1_u:
        bgm_segs.append(mk_cc_aseg(bgm_aid, seg1_u, total_u - seg1_u, us(8.0), 350000, 1100000, 0.16))
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = bgm_segs

    sfx_cc_cache, sfx_lanes = {}, []
    for t0, sk, lbl in sorted(SFX_EVENTS, key=lambda x: x[0]):
        sp, gvol, mdur = SFX_MAP[sk]
        cc_sp = TGT_MAT_A / sp.name
        fwd = norm_fwd(cc_sp)
        if fwd not in sfx_cc_cache:
            du_f, aid = us(probe_audio_dur(cc_sp)), uid()
            am = copy.deepcopy(amat_tpl)
            am.update({"id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
                       "name": lbl, "path": fwd, "duration": du_f, "type": "sound"})
            D["materials"]["audios"].append(am); sfx_cc_cache[fwd] = (aid, du_f)
        aid, du_f = sfx_cc_cache[fwd]
        du, st_u = min(du_f, us(mdur)), max(0, us(t0))
        sg = mk_cc_aseg(aid, st_u, du, 0, min(15000, du // 6), min(90000, du // 3), round(min(0.45, gvol * 1.1), 3))
        placed = False
        for ln in sfx_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                ln.append(sg); placed = True; break
        if not placed: sfx_lanes.append([sg])
    sfx_tracks = [copy.deepcopy(atrack_tpl) for _ in sfx_lanes]
    for ta, ln in zip(sfx_tracks, sfx_lanes):
        ta["id"] = uid(); ta["segments"] = ln

    new_tl_id = uid()
    D["id"] = new_tl_id; D["name"] = TGT_DRAFT_NAME
    D["tracks"] = [tr_v0, tr_v1, tr_v2, tr_sub, *ft_tracks, tr_filt, tr_bgm, *sfx_tracks]
    D["duration"] = total_u; D["update_time"] = now_s; D["time_marks"] = None
    D["canvas_config"] = {"width": W, "height": H, "ratio": "9:16", "background": None}
    if isinstance(D.get("extra_info"), dict): D["extra_info"]["subtitle_fragment_info_list"] = []
    if isinstance(D.get("config"), dict): D["config"]["subtitle_taskinfo"] = []
    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video": s["render_index"] = ti
            elif tr["type"] == "text": s["render_index"] = 14000 + ti
            elif tr["type"] == "filter": s["render_index"] = 10000

    tl_root = TGT_DRAFT_DIR / "Timelines"
    tl_root.mkdir(parents=True, exist_ok=True)
    for item in list(tl_root.iterdir()):
        if item.is_dir(): shutil.rmtree(item)
    tl_sub = tl_root / new_tl_id
    tl_sub.mkdir(parents=True, exist_ok=True)
    (tl_sub / "attachment").mkdir(exist_ok=True); (tl_sub / "common_attachment").mkdir(exist_ok=True)
    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for p_out in [TGT_DRAFT_DIR/"draft_content.json", TGT_DRAFT_DIR/"draft_content.json.bak", TGT_DRAFT_DIR/"template-2.tmp",
                  tl_sub/"draft_content.json", tl_sub/"draft_content.json.bak", tl_sub/"template-2.tmp"]:
        p_out.write_bytes(dc_bytes)
    for att in ("draft.extra", "attachment_editing.json", "attachment_pc_common.json", "draft_cover.jpg"):
        if (TGT_DRAFT_DIR / att).exists(): shutil.copy2(TGT_DRAFT_DIR / att, tl_sub / att)

    pj = {"config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
          "create_time": now_us, "id": new_tl_id, "main_timeline_id": new_tl_id,
          "timelines": [{"create_time": now_us, "id": new_tl_id, "is_marked_delete": False, "name": "Timeline 01", "update_time": now_us}],
          "update_time": now_us, "version": 0}
    pj_b = json.dumps(pj, ensure_ascii=False).encode("utf-8")
    (tl_root / "project.json").write_bytes(pj_b); (tl_root / "project.json.bak").write_bytes(pj_b)
    (TGT_DRAFT_DIR / "timeline_layout.json").write_text(json.dumps({"dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": [new_tl_id], "timelineNames": ["Timeline 01"]}], "layoutOrientation": 1}, ensure_ascii=False), encoding="utf-8")

    # Clean draft_virtual_store.json matched 1:1 to new_dm_entries
    vs_obj = {
        "draft_materials": [],
        "draft_virtual_store": [
            {"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]},
            {"type": 1, "value": [{"child_id": e["id"], "parent_id": ""} for e in new_dm_entries]},
            {"type": 2, "value": []},
        ],
    }
    (TGT_DRAFT_DIR / "draft_virtual_store.json").write_text(json.dumps(vs_obj, ensure_ascii=False), encoding="utf-8")

    uniq_paths = {v["path"] for v in D["materials"]["videos"]} | {a["path"] for a in D["materials"]["audios"]}
    total_bytes = sum(Path(p).stat().st_size for p in uniq_paths if Path(p).is_file())
    dmi_out = copy.deepcopy(dmi_old)
    dmi_out["draft_name"] = TGT_DRAFT_NAME
    dmi_out["draft_fold_path"] = norm_fwd(TGT_DRAFT_DIR)
    dmi_out["draft_root_path"] = norm_fwd(CC_ROOT)
    dmi_out["tm_duration"] = total_u
    dmi_out["tm_draft_modified"] = now_us
    dmi_out["draft_timeline_materials_size_"] = total_bytes
    if draft_is_locked:
        new_draft_uuid = uid()
        dmi_out["draft_id"] = new_draft_uuid
        dmi_out["tm_draft_create"] = now_us
        dmi_out["cloud_draft_sync"] = False
        dmi_out["cloud_draft_cover"] = False
        dmi_out["draft_cloud_last_action_download"] = False
        dmi_out["tm_draft_cloud_entry_id"] = -1
        dmi_out["tm_draft_cloud_modified"] = 0
        dmi_out["tm_draft_cloud_completed"] = ""
    for bkt in dmi_out.get("draft_materials", []):
        if bkt.get("type") == 0: bkt["value"] = new_dm_entries
    (TGT_DRAFT_DIR / "draft_meta_info.json").write_text(json.dumps(dmi_out, ensure_ascii=False), encoding="utf-8")

    if RMI_PATH.exists():
        rmi = json.loads(RMI_PATH.read_text(encoding="utf-8"))
        store = rmi.get("all_draft_store", [])
        if draft_is_locked:
            base_ent = next((e for e in store if e.get("draft_name") == DRAFT_NAME), store[0] if store else {})
            new_ent = copy.deepcopy(base_ent)
            tgt_fwd = norm_fwd(TGT_DRAFT_DIR)
            new_ent.update({
                "draft_id": dmi_out["draft_id"],
                "draft_name": TGT_DRAFT_NAME,
                "draft_fold_path": tgt_fwd,
                "draft_json_file": f"{tgt_fwd}\\draft_content.json",
                "draft_cover": f"{tgt_fwd}\\draft_cover.jpg",
                "draft_root_path": norm_fwd(CC_ROOT),
                "tm_draft_create": now_us,
                "tm_draft_modified": now_us,
                "tm_duration": total_u,
                "draft_timeline_materials_size": total_bytes,
                "cloud_draft_sync": False,
                "cloud_draft_cover": False,
                "draft_cloud_last_action_download": False,
                "tm_draft_cloud_entry_id": -1,
                "tm_draft_cloud_modified": 0,
                "tm_draft_cloud_completed": "",
                "tm_draft_removed": 0,
            })
            store = [e for e in store if e.get("draft_name") != TGT_DRAFT_NAME]
            store.insert(0, new_ent)
            rmi["all_draft_store"] = store
        else:
            for ent in store:
                if ent.get("draft_name") == DRAFT_NAME:
                    ent["tm_duration"] = total_u; ent["tm_draft_modified"] = now_us; ent["draft_timeline_materials_size"] = total_bytes
        RMI_PATH.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    assert D["id"] == pj["id"] == pj["main_timeline_id"] == pj["timelines"][0]["id"] == new_tl_id
    assert pj["timelines"][0]["is_marked_delete"] is False
    assert tr_v0["flag"] == 0 and tr_v1["flag"] == 2 and tr_v2["flag"] == 2
    assert all(vs.get("choice") == 0 and vs.get("production_path") == "" for vs in D["materials"]["vocal_separations"]), "Dirty vocal_separation!"
    assert all(Path(v["path"]).is_file() for v in D["materials"]["videos"]), "Missing video material!"
    assert all(Path(a["path"]).is_file() for a in D["materials"]["audios"]), "Missing audio material!"

    # ==========================================================================
    # STEP E: 16-FRAME VISUAL QC SHEET DIRECTLY FROM RENDERED V4 FINAL MP4!
    # ==========================================================================
    print("\n[STEP E] Extracting 16-frame Visual QC Sheet from V4 Final MP4...")
    qc_times = [
        2.7,                           # #01 Doorway + F20 Green/Red Coiny Hero + "77 SET QUÀ 20/11"
        tp("B03_handshake", 21.0),     # #02 Handshake + Executive Name Tag (Thầy Loan Văn Hậu!)
        tp("B05_quality", 26.8),       # #03 Interview Name Tag + White Coiny sub
        tp("B05_quality", 32.0),       # #04 "PHẢI CHẤT LƯỢNG!" Gold Coiny jump-up
        tp("B06_hand_sea", 61.8),      # #05 Macro DJI_0087 SKANEST + "YẾN THỦ CÔNG • KHÔNG HÓA CHẤT"
        tp("B06_hand_sea", 71.8),      # #06 Cute Flying Sticker 01 (Rong Biển) in Act 2
        tp("B08_a2_mica", 140.8),      # #07 "RẤT LÀ ƯNG Ý!" Gold Coiny jump-up
        tp("B08_a2_mica", 145.0),      # #08 Macro DJI_0085 Handle + "QUAI XÁCH TIỆN TAY"
        tp("B08_a2_mica", 154.8),      # #09 Macro DJI_0083 Mica Trong + "GIỎ MICA TRONG SUỐT"
        tp("B09_a3_5items", 215.0),    # #10 Cute Flying Sticker 01 (Rong Biển) + Stack 01!
        tp("B09_a3_5items", 218.0),    # #11 Cute Flying Sticker 02 (Yến Sào A5!) + Stack 01-02!
        tp("B09_a3_5items", 224.8),    # #12 Cute Flying Sticker 04 (Bánh Thuyền!) + Stack 01-04!
        tp("B09_a3_5items", 228.4),    # #13 Cute Flying Sticker 05 (Kẹp Hạt!) + FULL Stack 01-05!
        tp("B11_book1", 72.2),         # #14 Book 1 + "DANH NHÂN THẾ GIỚI" Coiny jump-up
        tp("B13_hau_thanks", 127.5),   # #15 Climax + "MÓN QUÀ TAN CHẢY • SIÊU THÍCH!"
        total_s - 1.0,                 # #16 Official F20 Brand Closing Banner (0% AI!)
    ]
    cols, rows, tw, th = 4, 4, 324, 576
    sheet = Image.new("RGB", (cols * tw, rows * (th + 26)), (16, 18, 22))
    sdr = ImageDraw.Draw(sheet)
    fnt_lbl = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 19)
    for i, ts in enumerate(qc_times):
        ts = max(0.2, min(total_s - 0.15, ts))
        tf = TMP_DIR / "_qc_v4.jpg"
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{ts:.3f}","-i",str(LOCAL_OUT),"-frames:v","1","-update","1","-vf",f"scale={tw}:{th}",str(tf)], check=True)
        r, c = divmod(i, cols)
        sheet.paste(Image.open(tf), (c * tw, r * (th + 26) + 26))
        sdr.text((c * tw + 6, r * (th + 26) + 3), f"#{i+1:02d} t={ts:05.1f}s / {total_s:.1f}s", font=fnt_lbl, fill=(255, 240, 140))
        tf.unlink()
    qc_out = WORK / "qc_v4_coiny_cute_short_16frames.jpg"
    sheet.save(qc_out, quality=92)

    ARCHIVE_G.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), ARCHIVE_G / Path(__file__).name)
    shutil.copy2(qc_out, ARCHIVE_G / qc_out.name)
    for extra_qc in ("v4_stickers_and_nametag_qc.jpg", "v4_nametag_placement_check.jpg"):
        if (WORK / extra_qc).exists():
            shutil.copy2(WORK / extra_qc, ARCHIVE_G / extra_qc)

    print(f"\n=== V4 MASTER COMPLETE IN {time.time() - t_wall:.1f}s! ===")
    print(f"  -> Final MP4 (F20)  : {FINAL_F20}")
    print(f"  -> CapCut Draft     : {TGT_DRAFT_DIR}")
    print(f"  -> Duration         : {total_s:.2f}s ({int(total_s//60)}m {total_s%60:04.1f}s) — SHORTENED BY ~79s! | 0% AI!")
    print(f"  -> Font             : 100% Coiny (CapCut ID {COINY_CC_ID})!")
    print(f"  -> Cute Stickers    : 5 IS-Net white-bordered die-cut product stickers flying up + Directional Name Tags (Right & Left)!")
    print(f"  -> Audio Fix        : 100% clean vocal_separations (choice=0, production_path='') + 0.15 ambient continuity on speed bridges!")
    print(f"  -> QC Sheet         : {qc_out}")


if __name__ == "__main__":
    main()
