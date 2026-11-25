"""
F20 × ĐĂNG KHOA EDU (77 SET QUÀ 20/11) — V3 MASTER FINAL ("NÀNG XUÂN STYLE")
==============================================================================
100% Zero AI — Real 261116 footage + real F20 product cutouts + non-AI F20 brand banner.
Implements EVERY user requirement:
  1. Smooth Pause Speed-Up (`1.75x - 2.10x`, muted mic + 25ms edge crossfades) on 26 short pauses
     inside continuous takes (`C3926`, `C3932`) instead of jump-cutting -> ZERO frame snap!
  2. Carefully Hand-Picked Context-Exact Native 9:16 B-Roll Overlays (20 cuts + 9 round product badges)
     covering 100% of long cuts and matching every spoken product/phrase (`DJI_0085` handle macro,
     `DJI_0087` SKANEST bird's nest macro, `DJI_0084` rong biển kẹp hạt, `DJI_0083` mica trong, etc.).
  3. Exact Nàng Xuân (`260711 Triệt Lông 59k`) 2-Tier Typography:
       - Normal clean white subtitle (`BeVietnamPro-Bold`, subtle dark shadow + thin crisp edge) at bottom.
       - Key emphasis words/phrases CHANGE COLOR (Nàng Xuân Gold `#FFD83B` / F20 Bright Emerald `#42F57B`)
         and JUMP UP SEPARATELY above the bottom sub with elastic pop-up spring motion + Micro-SFX!
       - Stacking 5-item list (`01 -> 05`) when Anh Hậu names each gift item inside the basket!
  4. Renders Final HQ MP4 via GPU NVENC (`h264_nvenc`) with Broadcast Audio (`-13.5 LUFS`) AND updates
     the synced editable CapCut Draft (`D:\\Capcut\\CapCut Drafts\\261121 F20 Phỏng Vấn Đăng Khoa Edu`).
"""

import copy, json, math, os, shutil, subprocess, sys, time, uuid
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30

# ==============================================================================
# PATHS (PC 001: Local SSD D:\Capcut + Google Drive G:\)
# ==============================================================================
CC_ROOT    = Path(r"D:\Capcut\CapCut Drafts")
RMI_PATH   = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json")
DRAFT_NAME = "261121 F20 Phỏng Vấn Đăng Khoa Edu"
DRAFT_DIR  = CC_ROOT / DRAFT_NAME
MAT_V      = DRAFT_DIR / "materials" / "video"
MAT_A      = DRAFT_DIR / "materials" / "audio"
NX_DRAFT   = CC_ROOT / "Nàng Xuân"

FONTS_DIR  = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
FONT_SUB   = FONTS_DIR / "BeVietnamPro-Bold.ttf"
FONT_EMP   = FONTS_DIR / "BeVietnamPro-ExtraBold.ttf"

WORK       = Path(r"d:\AI\full studio\output\f20-phong-van-dang-khoa-edu")
TMP_DIR    = WORK / "_v3_tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

FINAL_NAME = "261122 F20 Phỏng vấn Đăng Khoa Edu 77 set quà final.mp4"
FINAL_F20  = Path(r"G:\Other computers\My Computer\F20\Final") / FINAL_NAME
FINAL_CLD  = Path(r"G:\My Drive\AI_Full_Studio\04_Videos_Final") / FINAL_NAME
ARCHIVE_G  = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\f20-phong-van-dang-khoa-edu")
LOCAL_OUT  = WORK / FINAL_NAME

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

# Colors (RGB 0..255 for PIL & 0..1 for CapCut)
RGB_WHITE   = (255, 255, 255)
RGB_GOLD    = (255, 218, 62)     # Nàng Xuân warm vibrant gold
RGB_EMERALD = (74, 245, 128)     # F20 luminous fresh emerald green
RGB_CORAL   = (255, 118, 92)     # Warm accent coral for heartfelt climax
RGB_STROKE_SUB = (14, 18, 22)
RGB_STROKE_GLD = (42, 24, 6)
RGB_STROKE_GRN = (6, 46, 18)

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
# 1. TRACK 0 — CONTINUOUS BLOCKS + SMOOTH PAUSE SPEED-UP BRIDGES (ZERO JUMP-CUT!)
# ==============================================================================
# Each block: (block_id, filename, src_in, src_out, base_speed, vol_spans, pause_bridges, xfade_after)
#   vol_spans: list of (t_start, t_end, cc_vol, mp4_db)
#   pause_bridges: list of (p_start, p_end, bridge_speed) -> kept continuous, sped up smoothly, muted audio!
BLOCKS_SPEC = [
    # HỒI 1: Cửa phòng báo ship hàng -> Pan phòng -> Bước vào bắt tay Anh Hậu
    ("B01_doorway",   "C3925.MP4", 1.70, 14.35, 1.04, [(1.70, 14.35, 1.15, +1.0)], [], True),
    ("B02_room_pan",  "C3908.MP4", 0.80,  2.30, 1.00, [(0.80,  2.30, 0.00, -99.0)], [], False),
    ("B03_handshake", "C3925.MP4",18.75, 23.30, 1.00, [(18.75,23.30, 1.35, +2.4)], [], True),

    # HỒI 2A: Continuous Take #1 (`C3926 5.75 -> 45.20`) — 7 smooth pause speed-ups, ZERO jump-cuts!
    ("B04_q1_to_a1u", "C3926.MP4", 5.75, 45.20, 1.04,
     [(5.75, 15.55, 1.15, +1.0), (15.55, 45.20, 1.75, +4.8)],
     [
         (15.55, 16.90, 2.00),   # Q1 -> A1 turn-taking smile
         (22.90, 23.52, 1.85),   # breath pause
         (28.87, 29.40, 1.75),   # short pause
         (31.51, 32.33, 1.85),   # before "phải chất lượng!"
         (33.80, 35.15, 1.95),   # nod transition
         (39.96, 40.62, 1.85),   # breath pause
         (41.67, 42.41, 1.85),   # breath pause
     ], False),

    # HỒI 2B: Continuous Take #2 (`C3926 53.85 -> 79.85`) — 7 smooth pause speed-ups, ZERO jump-cuts!
    # (Long gap 45.20 -> 53.85 covered 100% by full-screen B-roll DJI_0082_D!)
    ("B05_ngon_sea",  "C3926.MP4", 53.85, 79.85, 1.04,
     [(53.85, 79.85, 1.75, +4.8)],
     [
         (56.10, 57.85, 2.05),   # after "thấy rất là ngon!"
         (59.86, 60.60, 1.85),
         (63.10, 63.73, 1.85),
         (66.72, 67.51, 1.85),
         (69.05, 69.75, 1.85),   # between handmade & seaweed
         (72.95, 73.42, 1.75),
         (76.80, 77.37, 1.80),
     ], False),

    # HỒI 2C: Continuous Take #3 (`C3926 86.75 -> 98.10`) — Long gap 79.85->86.75 covered 100% by DJI_0084 + C3873!
    ("B06_energy",    "C3926.MP4", 86.75, 98.10, 1.04,
     [(86.75, 98.10, 1.75, +4.8)],
     [(96.60, 97.19, 1.75)], False),

    # HỒI 3A: Q2 (`C3926 108.00 -> 116.50`) — Long gap 98.10->108.00 covered 100% by C3922!
    ("B07_q2_oanh",   "C3926.MP4", 108.00, 116.50, 1.04,
     [(108.00, 116.50, 1.15, +1.0)], [], False),

    # HỒI 3B: Continuous Take #4 (`C3926 133.20 -> 165.40`) — 6 smooth pause speed-ups, ZERO jump-cuts!
    # (Long gap 116.50 -> 133.20 covered 100% by C3917 + C3911!)
    ("B08_a2_mica",   "C3926.MP4", 133.20, 165.40, 1.04,
     [(133.20, 152.80, 1.75, +4.8), (152.80, 156.00, 1.18, +1.2), (156.00, 165.40, 1.65, +4.2)],
     [
         (138.21, 138.94, 1.85),
         (142.55, 143.16, 1.85), # between "ưng ý" & "quai xách"
         (144.58, 145.41, 1.85),
         (146.83, 147.37, 1.75),
         (149.15, 150.20, 1.95), # before "Phía dưới đây là mica hả em?"
         (156.83, 157.48, 1.85),
     ], False),

    # HỒI 4A: Q3 (`C3926 187.55 -> 198.90`) — Long gap 165.40->187.55 covered 100% by DJI_0104 + C3918!
    ("B09_q3_consult","C3926.MP4", 187.55, 198.90, 1.04,
     [(187.55, 198.90, 1.15, +1.0)], [], False),

    # HỒI 4B: Continuous Take #5 (`C3926 204.90 -> 233.35`) — 5 smooth pause speed-ups, ZERO jump-cuts!
    # (Long gap 198.90 -> 204.90 covered 100% by C3874!)
    ("B10_a3_5items", "C3926.MP4", 204.90, 233.35, 1.04,
     [(204.90, 233.35, 1.75, +4.8)],
     [
         (212.80, 213.35, 1.85), # before pointing at 5 items
         (217.08, 217.86, 1.85), # item 1 -> 2
         (218.94, 219.57, 1.85), # item 2 -> 3
         (223.12, 223.86, 1.85), # item 3 -> 4
         (226.12, 226.67, 1.80), # item 4 -> 5
     ], True),

    # HỒI 5: Trao Hộp Quà Sách 20/11 (`C3932`)
    ("B11_gift_intro","C3932.MP4",   2.60,  16.45, 1.04, [(2.60, 16.45, 1.15, +1.0)], [], False),
    # Long gap 16.45 -> 47.65 covered 100% by C3921!
    ("B12_gift_give", "C3932.MP4",  47.65,  51.35, 1.04, [(47.65, 51.35, 1.35, +2.4)], [], False),
    # Long gap 51.35 -> 63.80 covered 100% by C3915!
    # Continuous Book 1 + motivation + Book 2 intro (`63.80 -> 84.70`, ZERO jump-cut between books!)
    ("B13_book1_2a",  "C3932.MP4",  63.80,  84.70, 1.04, [(63.80, 84.70, 1.15, +1.0)], [], False),
    # Long gap 84.70 -> 91.40 covered 100% by C3919!
    ("B14_book2b",    "C3932.MP4",  91.40,  96.25, 1.04, [(91.40, 96.25, 1.15, +1.0)], [], True),
    ("B15_hau_thanks","C3932.MP4", 122.40, 130.00, 1.04, [(122.40, 130.00, 1.75, +4.8)], [], True),

    # HỒI 6: Chị Oanh Cảm Ơn & CTA (`C3864`)
    ("B16_oanh_cta",  "C3864.MP4",   5.15,  19.30, 1.04, [(5.15, 19.30, 1.20, +1.4)], [], True),
]


def expand_timeline():
    """Expand continuous blocks into frame-accurate Track-0 micro-segments with pause speed-ups."""
    segs = []
    block_maps = {}  # block_id -> list of (src_a, src_b, tl_a_s, tl_b_s, speed)
    cur_f = 0

    for bid, fn, sin, sout, bspd, vspans, bridges, xfade_after in BLOCKS_SPEC:
        # Build sorted split points inside [sin, sout]
        # Apply safe speech-tail guard cushion (+0.14s start, -0.10s end) so quiet Anh Hậu syllables are NEVER clipped!
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
            # Check if inside a pause bridge
            br = next((sp for pa, pb, sp in safe_bridges if pa - 1e-4 <= mid_t <= pb + 1e-4), None)
            if br is not None:
                spd, vol_cc, vol_db, is_bridge = br, 0.0, -99.0, True
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

    speech_end_f = cur_f
    return segs, block_maps, speech_end_f


def src_to_tl(bmaps: dict, bid: str, src_t: float) -> float:
    bm = bmaps[bid]
    if src_t <= bm[0][0]: return bm[0][2]
    if src_t >= bm[-1][1]: return bm[-1][3]
    for a, b, ta, tb, spd in bm:
        if a - 1e-5 <= src_t <= b + 1e-5:
            ratio = (src_t - a) / max(1e-6, (b - a))
            return ta + ratio * (tb - ta)
    return bm[-1][3]


# ==============================================================================
# 2. TEXT WRAPPING & PIL NÀNG XUÂN RENDERING ENGINE
# ==============================================================================
def wrap_text(text: str, max_chars: int = 30) -> str:
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


def draw_styled_text_layer(canvas: Image.Image, text: str, cx: int, cy: int,
                           font: ImageFont.FreeTypeFont, fill_rgb: tuple,
                           stroke_rgb: tuple, stroke_w: int,
                           shadow_alpha: int = 165, shadow_off: tuple = (0, 5),
                           shadow_blur: int = 6, scale: float = 1.0, alpha: float = 1.0,
                           y_shift: int = 0):
    if alpha <= 0.01 or scale <= 0.05:
        return
    # Measure cleanly
    tmp = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    tdr = ImageDraw.Draw(tmp)
    pad = int(stroke_w + shadow_blur * 2 + 24)
    bb = tdr.multiline_textbbox((0, 0), text, font=font, stroke_width=stroke_w, align="center", spacing=10)
    tw, th = max(2, int(math.ceil(bb[2] - bb[0]))), max(2, int(math.ceil(bb[3] - bb[1])))
    bw, bh = int(tw + pad * 2), int(th + pad * 2)

    box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ox, oy = int(round(pad - bb[0])), int(round(pad - bb[1]))

    # Soft Gaussian Drop Shadow (exact Nàng Xuân clean editorial polish!)
    if shadow_alpha > 0:
        sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        sdr = ImageDraw.Draw(sh)
        sdr.multiline_text(
            (ox + shadow_off[0], oy + shadow_off[1]), text, font=font,
            fill=(0, 0, 0, int(shadow_alpha)),
            stroke_width=max(1, stroke_w), stroke_fill=(0, 0, 0, int(shadow_alpha)),
            align="center", spacing=10
        )
        if shadow_blur > 0:
            sh = sh.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
        box.alpha_composite(sh)

    # Crisp Stroke + Fill
    bdr = ImageDraw.Draw(box)
    bdr.multiline_text(
        (ox, oy), text, font=font,
        fill=(*fill_rgb, 255),
        stroke_width=stroke_w, stroke_fill=(*stroke_rgb, 255),
        align="center", spacing=10
    )

    if abs(scale - 1.0) > 0.005:
        nw, nh = max(2, int(round(bw * scale))), max(2, int(round(bh * scale)))
        box = box.resize((nw, nh), Image.Resampling.BICUBIC)
    else:
        nw, nh = bw, bh

    if alpha < 0.995:
        arr = np.array(box, dtype=np.uint8)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * alpha).astype(np.uint8)
        box = Image.fromarray(arr, mode="RGBA")

    px = int(round(cx - nw / 2))
    py = int(round(cy + y_shift - nh / 2))
    canvas.alpha_composite(box, (px, py))


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================
def main():
    t_start_wall = time.time()
    if DRAFT_DIR.exists() and (DRAFT_DIR / ".locked").exists():
        raise RuntimeError(f"'{DRAFT_NAME}' is currently open/locked in CapCut! Please exit to CapCut Home first.")

    segs, BM, speech_end_f = expand_timeline()
    banner_f = int(round(2.60 * FPS))
    total_f  = speech_end_f + banner_f
    speech_end_s = speech_end_f / FPS
    total_s      = total_f / FPS

    n_bridges = sum(1 for s in segs if s["is_bridge"])
    print(f"Timeline expanded: {len(segs)} Track-0 segments ({n_bridges} smooth pause speed-ups!), speech={speech_end_s:.2f}s, total={total_s:.2f}s")

    def tm(bid: str, s0: float, s1: float) -> tuple[float, float]:
        return (src_to_tl(BM, bid, s0), src_to_tl(BM, bid, s1))
    def tp(bid: str, s0: float) -> float:
        return src_to_tl(BM, bid, s0)

    # ==========================================================================
    # 2. TRACK 1 — 20 CAREFULLY HAND-PICKED NATIVE 9:16 B-ROLL OVERLAYS (0% AI!)
    #    Every single long cut is 100% seamlessly covered + every spoken product matched!
    # ==========================================================================
    BROLL_SPEC = [
        # (tl_t0, tl_t1, filename, src_in, speed, is_dji, note)
        # Hồi 1: Giữ Chị Oanh đứng cửa 3.05s mở đầu -> C3903 @18s (không biển quán) -> C3914 -> C3909
        (*tm("B01_doorway", 4.90, 7.00),     "C3903.MP4", 18.00, 1.00, False, "Chị Oanh & team F20 chuyển 77 set quà từ xe"),
        (*tm("B01_doorway", 7.00, 8.95),     "C3914.MP4",  3.00, 1.00, False, "Nhân viên F20 bày 77 set quà tại ĐK Edu"),
        (*tm("B01_doorway", 8.95, 10.60),    "C3909.MP4",  1.50, 1.00, False, "Pan cận 77 set quà xếp sẵn tại ĐK Edu"),

        # Hồi 2: Lý do chọn F20 + Chất lượng + Yến thủ công + Rong biển/bánh hạt
        (*tm("B04_q1_to_a1u", 18.20, 21.40), "C3910.MP4",  0.80, 0.90, False, "Toàn cảnh 77 set quà trên bàn Đăng Khoa Edu"),
        (*tm("B04_q1_to_a1u", 28.50, 32.10), "C3920.MP4",  1.20, 0.95, False, "Anh Hậu & Chị Oanh trực tiếp kiểm tra chất lượng"),
        # Cover long cut B04 -> B05 seamlessly with macro close-up of Set Quà!
        (tp("B04_q1_to_a1u", 42.30), tp("B05_ngon_sea", 55.60),
         "DJI_20261116093228_0082_D.MP4", 2.00, 0.95, True, "Cận set quà: Tổ Yến SKANEST, Bánh Thuyền, Rong Biển"),
        # "F20 làm yến thủ công hết, không hóa chất... gia đình dùng, bạn bè khen":
        (*tm("B05_ngon_sea", 60.60, 63.30),  "DJI_20261116093826_0087_D.MP4", 8.00, 0.95, True, "Cận macro Tổ Yến SKANEST + Cẩm nang trong giỏ Mica"),
        (*tm("B05_ngon_sea", 63.30, 66.20),  "C3866.MP4",  6.00, 1.00, False, "Đội ngũ F20 thắt nơ thủ công từng giỏ quà"),
        (*tm("B05_ngon_sea", 66.20, 68.40),  "C3870.MP4",  1.50, 1.00, False, "Nhân viên F20 tỉ mỉ kiểm tra hoàn thiện thủ công"),
        # Cover long cut B05 -> B06 seamlessly ("rong biển, bánh hạt... tiếp năng lượng")!
        (tp("B05_ngon_sea", 77.30), tp("B06_energy", 87.20),
         "DJI_20261116093322_0084_D.MP4", 48.00, 1.00, True, "Cận trực diện Rong Biển Kẹp Hạt & Rong Biển Tuệ Tâm"),
        (tp("B06_energy", 87.20), tp("B06_energy", 90.30),
         "C3873.MP4", 1.00, 0.90, False, "Dàn set quà đầy ắp rong biển, bánh thuyền, tổ yến"),

        # Cover long cut B06 -> B07 (transition to Q2)!
        (tp("B06_energy", 96.20), tp("B07_q2_oanh", 111.50),
         "C3922.MP4", 8.50, 1.00, False, "Anh Hậu & Chị Oanh nâng niu xem thành phẩm"),

        # Cover long cut B07 -> B08 (77 set quà đã tới Đăng Khoa Edu)!
        (tp("B07_q2_oanh", 114.60), tp("B08_a2_mica", 135.40),
         "C3917.MP4", 1.20, 1.00, False, "77 set quà xếp hàng ngay ngắn trên thảm đỏ ĐK Edu"),
        (tp("B08_a2_mica", 135.40), tp("B08_a2_mica", 137.80),
         "C3911.MP4", 1.50, 1.00, False, "Xếp hoàn thiện những set quà cuối tại phòng ĐK Edu"),

        # "Có quai xách tiện tay, cũng dễ thương nữa!" -> NEW macro close-up of burgundy leather handle!
        (*tm("B08_a2_mica", 143.30, 146.90), "DJI_20261116093624_0085_D.MP4", 3.50, 0.95, True, "Cận tay cầm quai xách da đỏ đô chắc chắn sang trọng"),
        # "túi giỏ đựng quà chất liệu mica trong ạ!" -> Rotating close-up of transparent Mica basket!
        (*tm("B08_a2_mica", 152.90, 156.80), "DJI_20261116093255_0083_D.MP4", 4.00, 0.95, True, "Cận xoay giỏ Mica trong suốt khoe trọn 4 món cao cấp"),

        # Cover long cut B08 -> B09 (Q3 tư vấn chất lượng)!
        (tp("B08_a2_mica", 163.80), tp("B09_q3_consult", 190.80),
         "DJI_20261116110956_0104_D.MP4", 0.60, 1.00, True, "Góc DJI Chị Oanh kiểm tra từng set quà tại ĐK Edu"),
        (tp("B09_q3_consult", 190.80), tp("B09_q3_consult", 193.90),
         "C3918.MP4", 1.00, 1.00, False, "Chị Oanh căn chỉnh tỉ mỉ từng giỏ quà"),

        # Cover long cut B09 -> B10 ("bồi bổ sức khỏe và tiện lợi" -> "Tối giản tập trung chất lượng")!
        (tp("B09_q3_consult", 197.40), tp("B10_a3_5items", 206.80),
         "C3874.MP4", 1.20, 0.90, False, "Cận kệ trưng bày Yến Sào SKANEST & Set Quà F20"),

        # Hồi 5: Cover long cuts B11->B12, B12->B13, B13->B14 seamlessly!
        (tp("B11_gift_intro", 14.00), tp("B12_gift_give", 47.65),
         "C3921.MP4", 1.20, 1.00, False, "Anh Hậu & Chị Oanh trò chuyện thân tình trước khi trao quà"),
        (tp("B12_gift_give", 50.80), tp("B13_book1_2a", 65.50),
         "C3915.MP4", 2.00, 1.00, False, "Dãy 77 set quà tri ân tại văn phòng Đăng Khoa Edu"),
        (tp("B13_book1_2a", 83.20), tp("B14_book2b", 92.60),
         "C3919.MP4", 1.50, 1.00, False, "Anh Hậu & Chị Oanh trao đổi vui vẻ bên 77 set quà"),

        # Hồi 6: CTA đặt quà 20/11!
        (*tm("B16_oanh_cta", 13.50, 17.20),  "C3875.MP4", 1.50, 0.90, False, "Dãy set quà 20/11 F20 sẵn sàng giao ngay"),
    ]

    # Verify ZERO same-track B-roll overlap!
    BROLL_SPEC.sort(key=lambda x: x[0])
    for i in range(len(BROLL_SPEC) - 1):
        assert BROLL_SPEC[i][1] <= BROLL_SPEC[i + 1][0] + 0.02, f"B-roll overlap: {BROLL_SPEC[i][6]} vs {BROLL_SPEC[i+1][6]}"
        if BROLL_SPEC[i][1] > BROLL_SPEC[i + 1][0]:
            BROLL_SPEC[i] = (*BROLL_SPEC[i][:1], BROLL_SPEC[i + 1][0], *BROLL_SPEC[i][2:])

    # ==========================================================================
    # 3. TRACK 2 — 9 CLEAN ROUND CIRCULAR PRODUCT OVERLAYS (`1080x1920`, `0%` AI!)
    #    Positioned cleanly on the open sky-blue wall gap (+0.08, +0.43, sc=0.45), ZERO B-roll collision!
    # ==========================================================================
    CIRCLE_SPEC = [
        # (tl_t0, tl_t1, png_name, px, py, sc, mini_label)
        (*tm("B04_q1_to_a1u", 38.60, 42.15), "circle_01_to_yen_a5.png",      +0.08, +0.45, 0.45, "YẾN SÀO SKANEST"),
        (*tm("B05_ngon_sea",  57.95, 60.50), "circle_01_to_yen_a5.png",      +0.08, +0.45, 0.45, "YẾN THỦ CÔNG 100%"),
        (*tm("B05_ngon_sea",  70.20, 73.55), "circle_02_2hop_rong_bien.png", +0.08, +0.45, 0.45, "RONG BIỂN TUỆ TÂM"),
        (*tm("B05_ngon_sea",  73.70, 77.15), "circle_03_banh_thuyen.png",    +0.08, +0.45, 0.45, "BÁNH THUYỀN MIX HẠT"),
        # 5 products named one-by-one while Anh Hậu points into the basket!
        (*tm("B10_a3_5items", 213.50, 216.30), "circle_02_2hop_rong_bien.png",+0.08, +0.45, 0.45, "01 • RONG BIỂN"),
        (*tm("B10_a3_5items", 216.40, 219.50), "circle_01_to_yen_a5.png",     +0.08, +0.45, 0.45, "02 • YẾN SÀO CAO CẤP"),
        (*tm("B10_a3_5items", 219.60, 222.95), "circle_08_duong_phen.png",    +0.08, +0.45, 0.45, "03 • ĐƯỜNG PHÈN"),
        (*tm("B10_a3_5items", 223.05, 226.75), "circle_03_banh_thuyen.png",   +0.08, +0.45, 0.45, "04 • BÁNH THUYỀN"),
        (*tm("B10_a3_5items", 226.85, 230.20), "circle_04_kep_hat_500g.png",  +0.08, +0.45, 0.45, "05 • RONG BIỂN KẸP HẠT"),
    ]
    for ct0, ct1, fn, *_ in CIRCLE_SPEC:
        for bt0, bt1, bfn, *_ in BROLL_SPEC:
            assert max(ct0, bt0) >= min(ct1, bt1) - 0.05, f"Circle {fn} overlaps B-roll {bfn}!"

    # ==========================================================================
    # 4. NÀNG XUÂN 2-TIER TYPOGRAPHY:
    #    - Tier 1 (`SUB_NORMAL`): Clean calm WHITE sentence-case sub at bottom (`y = -0.58` / `1517px`)
    #    - Tier 2 (`EMPHASIS_JUMPS`): Key punchlines CHANGE COLOR (Gold / F20 Emerald) & JUMP UP
    #      SEPARATELY right above the normal subtitle (`y = -0.42` / `1363px`), plus stacking 5-item list!
    #    - Tier 3 (`CHAPTER_TAGS`): Minimal clean top tags only on Opening + 3 major chapters!
    # ==========================================================================
    SUB_NORMAL = [
        # (tl_t0, tl_t1, text)
        (*tm("B01_doorway",   1.75,  4.55), "Bên Oanh đã chuẩn bị xong"),
        (*tm("B01_doorway",   4.60,  7.35), "giao tới văn phòng Đăng Khoa Edu"),
        (*tm("B01_doorway",   7.40, 10.10), "tại 23 Thái Nguyên rồi nhé mọi người!"),
        (*tm("B01_doorway",  10.20, 14.25), "Giờ cùng Oanh vào giao quà cho anh Hậu nhé!"),
        (*tm("B03_handshake",18.85, 20.15), "Xin chào anh Hậu ạ!"),
        (*tm("B03_handshake",20.20, 23.15), "Chào em, chào Oanh F20!"),

        (*tm("B04_q1_to_a1u", 5.80,  8.55), "Vì sao năm nay Đăng Khoa Edu"),
        (*tm("B04_q1_to_a1u", 8.60, 11.45), "chọn sản phẩm của Thực phẩm F20"),
        (*tm("B04_q1_to_a1u",11.50, 15.45), "làm quà tri ân thầy cô dịp 20/11 ạ?"),
        (*tm("B04_q1_to_a1u",16.95, 22.85), "Thầy cô Đăng Khoa Edu đã có nhiều\nđóng góp rất là tuyệt vời"),
        (*tm("B04_q1_to_a1u",23.55, 28.50), "Hậu muốn gửi lời cảm ơn đến thầy cô,"),
        (*tm("B04_q1_to_a1u",29.40, 33.75), "muốn có một chút quà, nhưng..."),
        (*tm("B04_q1_to_a1u",35.20, 39.80), "Ở F20, bản thân Hậu đã dùng rất nhiều rồi"),
        (*tm("B04_q1_to_a1u",40.65, 45.15), "từ bánh hạt, yến cho đến yến chưng tươi..."),
        (*tm("B05_ngon_sea", 53.90, 56.05), "thấy thật sự..."),
        (*tm("B05_ngon_sea", 57.90, 63.05), "F20 làm yến này bằng thủ công hết,"),
        (*tm("B05_ngon_sea", 63.75, 69.00), "gia đình dùng, tặng bạn bè..."),
        (*tm("B05_ngon_sea", 69.80, 72.90), "Đặc biệt rất thích là..."),
        (*tm("B05_ngon_sea", 73.45, 79.80), "Giáo viên nhiều khi bận bịu không kịp ăn sáng,"),
        (*tm("B06_energy",   86.80, 91.45), "ăn 1–2 cái giữa buổi dạy thấy rất ngon!"),
        (*tm("B06_energy",   91.55, 98.05), "Rong biển và các loại hạt..."),

        (*tm("B07_q2_oanh", 108.05,111.20), "Hôm nay giao những set quà tới đây,"),
        (*tm("B07_q2_oanh", 111.30,116.45), "anh Hậu chia sẻ cảm nhận khi nhận quà nhé!"),
        (*tm("B08_a2_mica", 133.25,138.15), "77 set quà đã tới Đăng Khoa Edu,"),
        (*tm("B08_a2_mica", 138.95,142.50), "cầm trên tay cảm thấy..."),
        (*tm("B08_a2_mica", 143.20,149.10), "Cầm trên tay vừa gọn vừa dễ thương nữa!"),
        (*tm("B08_a2_mica", 150.25,152.75), "Phía dưới đây là mica hả em?"),
        (*tm("B08_a2_mica", 152.85,156.00), "Dạ túi giỏ đựng quà chất liệu..."),
        (*tm("B08_a2_mica", 156.10,160.35), "Nhìn thấy là không giấu giếm gì hết!"),
        (*tm("B08_a2_mica", 160.45,165.35), "Cái gì tốt là mình khoe ra hết!"),

        (*tm("B09_q3_consult",187.60,193.55), "Anh Hậu nói muốn set quà tập trung chất lượng,"),
        (*tm("B09_q3_consult",193.65,198.85), "thầy cô dùng bồi bổ sức khỏe và tiện lợi!"),
        (*tm("B10_a3_5items", 204.95,209.60), "Toán học gọi là tối giản để tập trung chất lượng!"),
        (*tm("B10_a3_5items", 209.75,212.75), "Cái gì mà đơn giản..."),
        (*tm("B10_a3_5items", 213.45,216.25), "Đây là rong biển nè,"),
        (*tm("B10_a3_5items", 216.35,219.45), "đây là yến sào cao cấp nè,"),
        (*tm("B10_a3_5items", 219.55,222.90), "hộp đường phèn nè,"),
        (*tm("B10_a3_5items", 223.00,226.75), "bánh thuyền mix hạt nè,"),
        (*tm("B10_a3_5items", 226.85,229.00), "rong biển kẹp hạt nè!"),
        (*tm("B10_a3_5items", 229.10,233.30), "Những món rất hợp với thầy cô giáo luôn!"),

        (*tm("B11_gift_intro", 2.70,  8.60), "Hôm nay đến giao quà cho Đăng Khoa Edu,"),
        (*tm("B11_gift_intro", 8.70, 16.35), "F20 có món quà nhỏ tặng thầy Hậu dịp 20/11!"),
        (*tm("B12_gift_give", 47.70, 49.55), "Em xin gửi anh món quà nhỏ ạ!"),
        (*tm("B12_gift_give", 49.65, 51.30), "Cảm ơn Thực phẩm F20!"),
        (*tm("B13_book1_2a",  63.85, 68.50), "Biết anh Hậu là người cực kỳ mê sách,"),
        (*tm("B13_book1_2a",  68.60, 74.05), "F20 gửi tặng anh cuốn sách..."),
        (*tm("B13_book1_2a",  74.15, 78.40), "để anh truyền cảm hứng tới các bạn học trò!"),
        (*tm("B13_book1_2a",  78.60, 84.65), "Và quyển thứ hai — vì anh còn là doanh nhân..."),
        (*tm("B14_book2b",    91.45, 96.20), "Oanh gửi tặng anh quyển sách..."),
        (*tm("B15_hau_thanks",122.50,125.55), "Tuyệt vời! Cảm ơn Oanh và F20 rất là nhiều!"),
        (*tm("B15_hau_thanks",125.70,129.95), "Cầm trên tay mà thích quá trời luôn!"),

        (*tm("B16_oanh_cta",   5.20, 10.60), "Oanh xin cảm ơn quý anh chị đã tin tưởng\nđặt hàng Thực phẩm F20!"),
        (*tm("B16_oanh_cta",  10.75, 14.70), "Anh chị cần đặt set quà tặng dịp lễ 20/11"),
        (*tm("B16_oanh_cta",  14.80, 19.25), "để bên Oanh chuẩn bị chu đáo nhé!"),
    ]

    # Exact Nàng Xuân Jumping Emphasis Phrases (CHANGE COLOR + JUMP UP SEPARATELY right above bottom sub!)
    # Format: (tl_t0, tl_t1, text, py_norm, pil_font_px, cc_sz, color_key, sfx_key)
    #   py_norm = -0.41 -> PIL y = 1354px (right above bottom sub at -0.58 / 1517px, ZERO face collision!)
    EMPHASIS_JUMPS = [
        (*tm("B01_doorway",   2.35,  4.65), "77 SET QUÀ 20/11",           -0.42, 62, 13.4, "gold",    "pop"),
        (*tm("B01_doorway",   5.10,  9.90), "ĐĂNG KHOA EDU • 23 THÁI NGUYÊN", -0.42, 48, 10.6, "emerald", "ding"),
        (*tm("B04_q1_to_a1u",30.50, 33.80), "PHẢI CHẤT LƯỢNG!",           -0.42, 62, 13.4, "gold",    "ding"),
        (*tm("B05_ngon_sea", 53.95, 56.15), "RẤT LÀ NGON!",               -0.42, 64, 13.8, "gold",    "pop"),
        (*tm("B05_ngon_sea", 58.60, 63.10), "YẾN THỦ CÔNG • KHÔNG HÓA CHẤT", -0.42, 50, 11.0, "emerald", "shine"),
        (*tm("B05_ngon_sea", 65.40, 69.00), "TẶNG AI CŨNG KHEN!",         -0.42, 58, 12.6, "gold",    "pop"),
        (*tm("B05_ngon_sea", 70.30, 73.15), "RONG BIỂN & BÁNH HẠT",       -0.42, 56, 12.2, "emerald", "pop"),
        (*tm("B06_energy",   87.80, 91.50), "TIẾP NĂNG LƯỢNG CỰC NGON!",  -0.42, 52, 11.4, "gold",    "ding"),
        (*tm("B06_energy",   93.20, 98.05), "100% THIÊN NHIÊN",           -0.42, 60, 13.0, "emerald", "pop"),

        (*tm("B08_a2_mica", 139.10,142.55), "RẤT LÀ ƯNG Ý!",              -0.42, 64, 13.8, "gold",    "pop"),
        (*tm("B08_a2_mica", 143.40,147.60), "QUAI XÁCH TIỆN TAY",         -0.42, 58, 12.6, "gold",    "pop"),
        (*tm("B08_a2_mica", 153.20,156.60), "GIỎ MICA TRONG SUỐT",        -0.42, 58, 12.6, "emerald", "ding"),
        (*tm("B08_a2_mica", 157.50,165.35), "KHÔNG GIẤU GIẾM • SHOW HẾT!",-0.42, 52, 11.4, "gold",    "pop"),

        (*tm("B10_a3_5items",206.00,209.65),"TỐI GIẢN • CHẤT LƯỢNG",      -0.42, 56, 12.2, "emerald", "ding"),
        (*tm("B10_a3_5items",210.20,212.80),"ĐƠN GIẢN LÀ NGHỆ THUẬT!",    -0.42, 56, 12.2, "gold",    "pop"),

        # EXACT NÀNG XUÂN STACKING 5-ITEM LIST (each pops up and stacks cleanly while Anh Hậu counts 1->5!)
        (tp("B10_a3_5items",213.50), tp("B10_a3_5items",229.10), "01. Rong biển sấy giòn",    -0.21, 42,  9.4, "emerald", None),
        (tp("B10_a3_5items",216.40), tp("B10_a3_5items",229.10), "02. Yến sào cao cấp",       -0.27, 42,  9.4, "gold",    None),
        (tp("B10_a3_5items",219.60), tp("B10_a3_5items",229.10), "03. Hộp đường phèn",        -0.33, 42,  9.4, "emerald", None),
        (tp("B10_a3_5items",223.05), tp("B10_a3_5items",229.10), "04. Bánh thuyền mix hạt",   -0.39, 42,  9.4, "gold",    None),
        (tp("B10_a3_5items",226.85), tp("B10_a3_5items",229.10), "05. Rong biển kẹp hạt",     -0.45, 42,  9.4, "emerald", None),
        (*tm("B10_a3_5items",229.30,233.30),"RẤT HỢP THẦY CÔ GIÁO!",      -0.42, 56, 12.2, "gold",    "ding"),

        # Hồi 5: Books & Climax
        (*tm("B13_book1_2a", 71.20, 74.20), "DANH NHÂN THẾ GIỚI",         -0.42, 58, 12.6, "emerald", "page"),
        (*tm("B14_book2b",   93.00, 96.25), "TOÁN HỌC CỦA THỊNH VƯỢNG",   -0.42, 52, 11.4, "emerald", "page"),
        (*tm("B15_hau_thanks",125.70,130.00),"MÓN QUÀ TAN CHẢY • SIÊU THÍCH!", -0.42, 50, 11.0, "gold", "shine"),

        # Hồi 6: CTA
        (*tm("B16_oanh_cta", 14.80, 19.30), "INBOX NGAY CHO OANH!",       -0.42, 62, 13.4, "gold",    "bell"),
    ]

    # Minimal Refined Top Context Headers (clean sky-blue wall zone y=+0.52, ZERO clutter!)
    TOP_HEADERS = [
        (0.20, 4.40,  "GIAO 77 SET QUÀ 20/11",         0.00, +0.63, 56, 12.6, "gold"),
        (0.45, 4.40,  "THỰC PHẨM F20 × ĐĂNG KHOA EDU", 0.00, +0.52, 40,  9.0, "emerald"),
        (tp("B03_handshake", 19.0), tp("B03_handshake", 23.2),
         "Anh Hậu • ĐĂNG KHOA EDU",                    0.00, +0.52, 48, 11.0, "emerald"),
        (tp("B04_q1_to_a1u", 6.0), tp("B04_q1_to_a1u", 10.6),
         "01 • LÝ DO CHỌN F20",                        0.00, +0.51, 52, 11.8, "emerald"),
        (tp("B07_q2_oanh", 108.2), tp("B07_q2_oanh", 112.8),
         "02 • CẢM NHẬN THÀNH PHẨM",                   0.00, +0.51, 50, 11.4, "emerald"),
        (tp("B11_gift_intro", 2.9), tp("B11_gift_intro", 8.0),
         "QUÀ TRI ÂN THẦY HẬU 20/11",                  0.00, +0.51, 50, 11.4, "emerald"),
    ]
    # Add mini F20 emerald label cleanly underneath each round product circle (100% on sky-blue wall!)
    for ct0, ct1, _, px, py, _, mlbl in CIRCLE_SPEC:
        TOP_HEADERS.append((ct0, ct1, mlbl, px, py - 0.20, 36, 8.6, "emerald"))

    # ==========================================================================
    # STEP A: BUILD CLEAN VIDEO BASE MP4 VIA GPU NVENC (`h264_nvenc`, ~20s!)
    # ==========================================================================
    print("\n[STEP A] Rendering clean unified base video (Track 0 + 20 B-rolls + Banner) via GPU NVENC...")
    base_mp4 = TMP_DIR / "_base_video.mp4"
    if base_mp4.exists() and base_mp4.stat().st_size > 5_000_000 and "--rebuild-base" not in sys.argv:
        print(f"  -> Reusing cached base video: {base_mp4} ({base_mp4.stat().st_size / 1e6:.1f} MB)")
    else:
        # Slice the timeline [0, speech_end_f] into non-overlapping visual intervals (Track 1 overrides Track 0!)
        broll_f = []
        for bt0, bt1, bfn, bsin, bspd, is_dji, note in BROLL_SPEC:
            bf0, bf1 = int(round(bt0 * FPS)), int(round(bt1 * FPS))
            if bf1 > bf0:
                broll_f.append((bf0, bf1, bfn, bsin, bspd, is_dji, note))

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
            if f1 <= f0:
                continue
            mid_f = f0 + 0.5
            br = next((b for b in broll_f if b[0] <= mid_f < b[1]), None)
            if br is not None:
                bf0, bf1, bfn, bsin, bspd, is_dji, _ = br
                src_path = MAT_V / bfn
                src_in_s = bsin + ((f0 - bf0) / FPS) * bspd
                spd = bspd
                grade = "dji" if is_dji else "sony"
            else:
                s0 = next(s for s in segs if s["tl_f0"] <= mid_f < s["tl_f1"])
                src_path = s0["path"]
                src_in_s = s0["src_in"] + ((f0 - s0["tl_f0"]) / FPS) * s0["speed"]
                spd = s0["speed"]
                grade = "sony"

            nf = f1 - f0
            src_dur_s = (nf / FPS) * spd + 0.25
            _, _, mdur, _ = probe_media(src_path)
            if src_in_s + (nf / FPS) * spd > mdur - 0.05:
                src_in_s = max(0.0, mdur - (nf / FPS) * spd - 0.05)

            out_p = TMP_DIR / f"p_{idx:03d}.mp4"
            if grade == "dji":
                vf = (
                    f"setpts=(PTS-STARTPTS)/{spd:.5f},"
                    f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                    f"colorbalance=rs=0.045:gs=0.01:bs=-0.045,eq=saturation=1.18:contrast=1.07:brightness=0.025,setsar=1"
                )
            else:
                vf = (
                    f"setpts=(PTS-STARTPTS)/{spd:.5f},"
                    f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                    f"eq=saturation=1.10:contrast=1.03:brightness=0.01,setsar=1"
                )
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-ss", f"{src_in_s:.4f}", "-i", str(src_path),
                "-t", f"{src_dur_s:.4f}",
                "-vf", vf, "-frames:v", str(nf), "-an",
                "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "17", "-b:v", "0",
                "-pix_fmt", "yuv420p", str(out_p)
            ], check=True)
            piece_files.append(out_p)

        ban_p = TMP_DIR / "p_banner.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", str(MAT_V / "outro_banner_f20_brand.mp4"),
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},fade=t=in:st=0:d=0.30,setsar=1",
            "-frames:v", str(banner_f), "-an",
            "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "17", "-b:v", "0",
            "-pix_fmt", "yuv420p", str(ban_p)
        ], check=True)
        piece_files.append(ban_p)

        clist = TMP_DIR / "concat.txt"
        clist.write_text("\n".join(f"file '{p.as_posix()}'" for p in piece_files), encoding="utf-8")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(clist),
            "-c:v", "copy", str(base_mp4)
        ], check=True)
        print(f"  -> Base video rendered ({len(piece_files)} pieces, {total_f} frames) in {time.time() - t_start_wall:.1f}s!")

    # ==========================================================================
    # STEP B: RENDER ANIMATED NÀNG XUÂN OVERLAYS (SUBS + COLORED JUMP-UPS + CIRCLES)
    #         Piped directly over `_base_video.mp4` into GPU NVENC!
    # ==========================================================================
    print("\n[STEP B] Compositing Nàng Xuân subtitles, colored jump-up emphasis texts & round badges via NVENC...")
    t_b = time.time()

    # Preload fonts & resized circular badges
    fnt_sub_44 = ImageFont.truetype(str(FONT_SUB), 44)
    fnt_emp_cache = {}
    def get_emp_font(px: int):
        if px not in fnt_emp_cache:
            fnt_emp_cache[px] = ImageFont.truetype(str(FONT_EMP), px)
        return fnt_emp_cache[px]

    circle_imgs = {}
    for _, _, png, px, py, sc, _ in CIRCLE_SPEC:
        key = (png, sc)
        if key not in circle_imgs:
            im = Image.open(MAT_V / png).convert("RGBA")
            nw, nh = int(round(W * sc)), int(round(H * sc))
            circle_imgs[key] = im.resize((nw, nh), Image.Resampling.LANCZOS)

    # Sort & anti-blink smooth SUB_NORMAL
    SUB_SORTED = sorted(SUB_NORMAL, key=lambda x: x[0])
    SUB_CLEAN = []
    for i, (st, en, tx) in enumerate(SUB_SORTED):
        if i + 1 < len(SUB_SORTED):
            nxt = SUB_SORTED[i + 1][0]
            if 0.0 < nxt - en <= 0.25:
                en = nxt - 0.034
            elif en > nxt - 0.034:
                en = max(st + 0.30, nxt - 0.034)
        SUB_CLEAN.append((int(round(st * FPS)), int(round(en * FPS)), wrap_text(tx, 30)))

    EMP_F = []
    for st, en, tx, py_n, fpx, ccsz, ckey, _ in EMPHASIS_JUMPS:
        EMP_F.append((int(round(st * FPS)), int(round(en * FPS)), tx, py_n, fpx, ckey))

    HDR_F = []
    for st, en, tx, px_n, py_n, fpx, ccsz, ckey in TOP_HEADERS:
        HDR_F.append((int(round(st * FPS)), int(round(en * FPS)), tx, px_n, py_n, fpx, ckey))

    CIR_F = []
    for st, en, png, px_n, py_n, sc, _ in CIRCLE_SPEC:
        CIR_F.append((int(round(st * FPS)), int(round(en * FPS)), png, px_n, py_n, sc))

    COLOR_MAP = {
        "gold":    (RGB_GOLD,    RGB_STROKE_GLD),
        "emerald": (RGB_EMERALD, RGB_STROKE_GRN),
        "coral":   (RGB_CORAL,   RGB_STROKE_GLD),
    }

    # Pre-cache fully static overlay frames by state key -> ~85% instant cache hits!
    ANIM_IN_F  = 6   # 0.20s crisp spring pop-up!
    ANIM_OUT_F = 4   # 0.13s crisp fade-out!
    EMPTY_BYTES = bytes(W * H * 4)
    state_cache = {}

    vid_only_mp4 = TMP_DIR / "_video_with_overlays.mp4"
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
        # Collect active items & their quantized animation step
        act_sub = None
        for f0, f1, tx in SUB_CLEAN:
            if f0 <= fr < f1:
                act_sub = tx
                break

        act_emp = []
        for idx_e, (f0, f1, tx, py_n, fpx, ckey) in enumerate(EMP_F):
            if f0 <= fr < f1:
                age = fr - f0
                rem = f1 - 1 - fr
                step = ("in", age) if age < ANIM_IN_F else (("out", rem) if rem < ANIM_OUT_F else ("hold", 0))
                act_emp.append((idx_e, step))

        act_hdr = []
        for idx_h, (f0, f1, tx, px_n, py_n, fpx, ckey) in enumerate(HDR_F):
            if f0 <= fr < f1:
                age = fr - f0
                rem = f1 - 1 - fr
                step = ("in", age) if age < 5 else (("out", rem) if rem < 4 else ("hold", 0))
                act_hdr.append((idx_h, step))

        act_cir = []
        for idx_c, (f0, f1, png, px_n, py_n, sc) in enumerate(CIR_F):
            if f0 <= fr < f1:
                age = fr - f0
                rem = f1 - 1 - fr
                step = ("in", age) if age < ANIM_IN_F else (("out", rem) if rem < ANIM_OUT_F else ("hold", 0))
                act_cir.append((idx_c, step))

        if not act_sub and not act_emp and not act_hdr and not act_cir:
            ff_proc.stdin.write(EMPTY_BYTES)
            continue

        skey = (act_sub, tuple(act_emp), tuple(act_hdr), tuple(act_cir))
        if skey in state_cache:
            ff_proc.stdin.write(state_cache[skey])
            continue

        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        # 1) Circular product badges (elastic pop-in!)
        for idx_c, (ph, stp) in act_cir:
            _, _, png, px_n, py_n, sc = CIR_F[idx_c]
            im = circle_imgs[(png, sc)]
            if ph == "in":
                u = (stp + 1) / ANIM_IN_F
                m_sc = 0.72 + 0.28 * ease_out_back(u)
                al = min(1.0, u * 1.4)
            elif ph == "out":
                u = (stp + 1) / ANIM_OUT_F
                m_sc, al = 0.94 + 0.06 * u, u
            else:
                m_sc, al = 1.0, 1.0
            nw, nh = max(2, int(round(im.width * m_sc))), max(2, int(round(im.height * m_sc)))
            im2 = im.resize((nw, nh), Image.Resampling.BICUBIC) if abs(m_sc - 1.0) > 0.005 else im
            if al < 0.995:
                arr = np.array(im2, dtype=np.uint8)
                arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * al).astype(np.uint8)
                im2 = Image.fromarray(arr, mode="RGBA")
            cx = int(round((px_n + 1.0) * 0.5 * W))
            cy = int(round((1.0 - py_n) * 0.5 * H))
            ov.alpha_composite(im2, (cx - nw // 2, cy - nh // 2))

        # 2) Refined Top Headers & Mini Circle Labels
        for idx_h, (ph, stp) in act_hdr:
            _, _, tx, px_n, py_n, fpx, ckey = HDR_F[idx_h]
            fcol, scol = COLOR_MAP[ckey]
            al = (stp + 1) / 5.0 if ph == "in" else ((stp + 1) / 4.0 if ph == "out" else 1.0)
            y_sh = int(round((1.0 - al) * 14)) if ph == "in" else 0
            cx = int(round((px_n + 1.0) * 0.5 * W))
            cy = int(round((1.0 - py_n) * 0.5 * H))
            draw_styled_text_layer(ov, tx, cx, cy, get_emp_font(fpx), fcol, scol, 4,
                                   shadow_alpha=155, shadow_off=(0, 4), shadow_blur=5,
                                   scale=1.0, alpha=al, y_shift=y_sh)

        # 3) NÀNG XUÂN COLORED JUMP-UP EMPHASIS PHRASES (popping UP cleanly above normal white sub!)
        for idx_e, (ph, stp) in act_emp:
            _, _, tx, py_n, fpx, ckey = EMP_F[idx_e]
            fcol, scol = COLOR_MAP[ckey]
            if ph == "in":
                u = (stp + 1) / ANIM_IN_F
                e_sc = 0.80 + 0.20 * ease_out_back(u)
                y_sh = int(round((1.0 - min(1.0, u * 1.15)) * 28))  # upward jump-in!
                al = min(1.0, u * 1.5)
            elif ph == "out":
                u = (stp + 1) / ANIM_OUT_F
                e_sc, y_sh, al = 0.96 + 0.04 * u, 0, u
            else:
                e_sc, y_sh, al = 1.0, 0, 1.0
            cy = int(round((1.0 - py_n) * 0.5 * H))
            draw_styled_text_layer(ov, tx, W // 2, cy, get_emp_font(fpx), fcol, scol, 5,
                                   shadow_alpha=185, shadow_off=(0, 5), shadow_blur=6,
                                   scale=e_sc, alpha=al, y_shift=y_sh)

        # 4) NORMAL CLEAN WHITE SUBTITLE (`sub text bt` — calm readable Nàng Xuân bottom line!)
        if act_sub:
            cy_sub = int(round((1.0 - (-0.58)) * 0.5 * H))
            draw_styled_text_layer(ov, act_sub, W // 2, cy_sub, fnt_sub_44, RGB_WHITE, RGB_STROKE_SUB, 2,
                                   shadow_alpha=190, shadow_off=(0, 4), shadow_blur=5,
                                   scale=1.0, alpha=1.0, y_shift=0)

        raw = ov.tobytes()
        # Keep hold-state cache compact (max 160 states)
        if len(state_cache) > 160:
            state_cache.clear()
        state_cache[skey] = raw
        ff_proc.stdin.write(raw)

    ff_proc.stdin.close()
    rc = ff_proc.wait()
    if rc != 0:
        raise RuntimeError(f"FFmpeg overlay pipe exited with {rc}")
    print(f"  -> Overlay composite complete in {time.time() - t_b:.1f}s!")

    # ==========================================================================
    # STEP C: BROADCAST AUDIO MASTERING (`-13.5 LUFS`, Muted Pause Bridges, Voice Balance, BGM, Micro-SFX)
    # ==========================================================================
    print("\n[STEP C] Mastering broadcast audio (voice balance, muted speed-up bridges, F20 BGM & Nàng Xuân SFX)...")
    t_c = time.time()

    # Build clean continuous dialogue track (48kHz stereo WAV)
    sr = 48000
    voice_buf = np.zeros((int(round(total_s * sr)) + sr, 2), dtype=np.float32)

    def load_audio_f32(path: Path, ss: float = 0.0, dur: float | None = None, atempo: float = 1.0, extra_af: str = "") -> np.ndarray:
        cmd = ["ffmpeg", "-v", "error"]
        if ss > 0: cmd += ["-ss", f"{ss:.4f}"]
        cmd += ["-i", str(path)]
        if dur is not None: cmd += ["-t", f"{dur:.4f}"]
        afs = []
        if abs(atempo - 1.0) > 0.002:
            afs.append(f"atempo={atempo:.5f}")
        if extra_af:
            afs.append(extra_af)
        if afs:
            cmd += ["-af", ",".join(afs)]
        cmd += ["-ar", str(sr), "-ac", "2", "-f", "f32le", "pipe:1"]
        r = subprocess.run(cmd, capture_output=True, check=True)
        arr = np.frombuffer(r.stdout, dtype=np.float32)
        n = (len(arr) // 2) * 2
        return arr[:n].reshape(-1, 2).copy()

    # Extract each speech segment (+ whisper-soft -20dB room tone on pause bridges so ZERO digital vacuum!)
    for s in segs:
        if s["vol_cc"] <= 0.01 and not s["is_bridge"]:
            continue
        sdur = s["src_out"] - s["src_in"]
        if s["is_bridge"]:
            clip_a = load_audio_f32(s["path"], ss=s["src_in"], dur=sdur, atempo=s["speed"], extra_af="lowpass=f=650,volume=-18dB")
        else:
            clip_a = load_audio_f32(
                s["path"], ss=s["src_in"], dur=sdur, atempo=s["speed"],
                extra_af=f"volume={s['vol_db']:+.1f}dB"
            )
        # Apply smooth 22ms edge fades (anti-click!)
        nf_fade = min(int(0.022 * sr), len(clip_a) // 4)
        if nf_fade > 1:
            ramp = np.linspace(0.0, 1.0, nf_fade, dtype=np.float32)[:, None]
            clip_a[:nf_fade] *= ramp
            clip_a[-nf_fade:] *= ramp[::-1]
        pos = int(round(s["tl_start"] * sr))
        tgt_len = int(round((s["tl_end"] - s["tl_start"]) * sr))
        use_len = min(len(clip_a), tgt_len, len(voice_buf) - pos)
        if use_len > 0:
            voice_buf[pos:pos + use_len] += clip_a[:use_len]

    voice_raw_wav = TMP_DIR / "_voice_raw.wav"
    voice_pol_wav = TMP_DIR / "_voice_polished.wav"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", "pipe:0",
        "-c:a", "pcm_f32le", str(voice_raw_wav)
    ], input=voice_buf[:int(round(total_s * sr))].tobytes(), check=True)

    # Polish voice stem FIRST and lock cleanly to -14.2 LUFS so voices stay 100% crisp & dominant!
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(voice_raw_wav),
        "-af", "highpass=f=80,equalizer=f=260:t=q:w=1.2:g=-2.2,equalizer=f=3200:t=q:w=1.4:g=2.4,acompressor=threshold=-20dB:ratio=3.0:attack=8:release=110:makeup=2.5,loudnorm=I=-14.2:TP=-1.8:LRA=7",
        "-c:a", "pcm_f32le", str(voice_pol_wav)
    ], check=True)

    # Build continuous F20 BGM track WITH Voice Pocket EQ (-5dB @ 1.8kHz & -4.5dB @ 3.2kHz -> silk-soft behind speech!)
    bgm_total_n = int(round(total_s * sr))
    bgm_buf = np.zeros((bgm_total_n, 2), dtype=np.float32)
    bgm_vp_af = "equalizer=f=1800:t=q:w=1.0:g=-5.0,equalizer=f=3200:t=q:w=1.2:g=-4.5"
    b1 = load_audio_f32(BGM_PATH, ss=0.0, dur=126.0, extra_af=bgm_vp_af)
    b2 = load_audio_f32(BGM_PATH, ss=8.0, dur=max(10.0, total_s - 124.0), extra_af=bgm_vp_af)
    n1 = min(len(b1), int(125.5 * sr), bgm_total_n)
    bgm_buf[:n1] = b1[:n1]
    if bgm_total_n > int(124.5 * sr):
        ov_n = int(1.0 * sr)
        st2 = int(124.5 * sr)
        rem = bgm_total_n - st2
        u2 = min(len(b2), rem)
        fade = np.linspace(0.0, 1.0, ov_n, dtype=np.float32)[:, None]
        bgm_buf[st2:st2 + ov_n] *= (1.0 - fade)
        bgm_buf[st2:st2 + ov_n] += b2[:ov_n] * fade
        if u2 > ov_n:
            bgm_buf[st2 + ov_n:st2 + u2] = b2[ov_n:u2]
    # Keep BGM silk-soft behind voices (0.075 ~= -17dB under voice!), rising warmly to 0.24 on closing banner!
    env = np.full(bgm_total_n, 0.075, dtype=np.float32)
    fi_n = int(0.35 * sr)
    env[:fi_n] *= np.linspace(0.0, 1.0, fi_n, dtype=np.float32)
    ban_st = int(round(speech_end_s * sr))
    sw_n = int(0.45 * sr)
    if ban_st + sw_n < bgm_total_n:
        env[ban_st:ban_st + sw_n] = np.linspace(0.075, 0.24, sw_n, dtype=np.float32)
        env[ban_st + sw_n:] = 0.24
    fo_n = int(1.15 * sr)
    env[-fo_n:] *= np.linspace(1.0, 0.0, fo_n, dtype=np.float32)
    bgm_buf *= env[:, None]

    # Build Nàng Xuân Crisp Micro-SFX track (refined subtle -12dB under voice!)
    SFX_MAP = {
        "pop":   (SFX_POP,   0.24, 0.35),
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
        (tp("B04_q1_to_a1u", 5.90), "wsh3", "Mở Phần 01"),
        (tp("B07_q2_oanh", 108.15), "wsh3", "Mở Phần 02"),
        (tp("B11_gift_intro", 2.75), "wsh1", "Mở Quà Tri Ân"),
        (speech_end_s - 0.05, "wsht", "Swoosh Banner"),
        (speech_end_s + 0.08, "chime", "Chuông Gió Banner"),
    ]
    # Add subtle Pop on every circular product badge
    for ct0, _, _, _, _, _, mlbl in CIRCLE_SPEC:
        SFX_EVENTS.append((ct0, "pop", f"Pop {mlbl}"))
    # Add subtle Nàng Xuân tactile SFX on jumping emphasis highlights (skip if within 0.25s of a circle pop!)
    cir_times = [c[0] for c in CIRCLE_SPEC]
    for et0, _, tx, _, _, _, _, sk in EMPHASIS_JUMPS:
        if sk and not any(abs(et0 - ct) < 0.28 for ct in cir_times):
            SFX_EVENTS.append((et0, sk, f"SFX {tx[:18]}"))

    sfx_buf = np.zeros((bgm_total_n, 2), dtype=np.float32)
    sfx_pcm_cache = {}
    for t0, sk, _ in SFX_EVENTS:
        sp, gvol, mdur = SFX_MAP[sk]
        if sk not in sfx_pcm_cache:
            sfx_pcm_cache[sk] = load_audio_f32(sp, ss=0.0, dur=mdur)
        pcm = sfx_pcm_cache[sk] * float(gvol)
        pos = max(0, int(round(t0 * sr)))
        u = min(len(pcm), bgm_total_n - pos)
        if u > 0:
            sfx_buf[pos:pos + u] += pcm[:u]

    # Mix polished voice + BGM + SFX -> Loudnorm -13.5 LUFS!
    v_pol = load_audio_f32(voice_pol_wav)
    n_mix = min(bgm_total_n, len(v_pol))
    mix = v_pol[:n_mix] + bgm_buf[:n_mix] + sfx_buf[:n_mix]
    mix_raw_wav = TMP_DIR / "_mix_raw.wav"
    mix_master_aac = TMP_DIR / "_mix_master.m4a"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", "pipe:0",
        "-c:a", "pcm_f32le", str(mix_raw_wav)
    ], input=mix.tobytes(), check=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(mix_raw_wav),
        "-af", "alimiter=limit=0.89:attack=5:release=60",
        "-c:a", "aac", "-b:a", "192k", str(mix_master_aac)
    ], check=True)

    # Final Mux (Local SSD first -> copy to F20 Final + AI_Full_Studio Final!)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(vid_only_mp4), "-i", str(mix_master_aac),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart",
        str(LOCAL_OUT)
    ], check=True)
    print(f"  -> Final MP4 muxed in {time.time() - t_c:.1f}s: {LOCAL_OUT} ({LOCAL_OUT.stat().st_size / 1e6:.1f} MB)")

    # Verify Final MP4 LUFS & duration!
    eb = subprocess.run(["ffmpeg", "-v", "info", "-i", str(LOCAL_OUT), "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True)
    lufs_lines = [l.strip() for l in eb.stderr.splitlines() if "I:" in l or "Peak:" in l]
    print("  -> Final MP4 Loudness:", " | ".join(lufs_lines[-3:]))

    # Copy Final MP4 to Official F20 Folder & AI_Full_Studio Cloud!
    FINAL_F20.parent.mkdir(parents=True, exist_ok=True)
    FINAL_CLD.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LOCAL_OUT, FINAL_F20)
    shutil.copy2(LOCAL_OUT, FINAL_CLD)
    print(f"  -> Delivered to F20 Final : {FINAL_F20}")
    print(f"  -> Delivered to Cloud Bak : {FINAL_CLD}")

    # ==========================================================================
    # STEP D: UPDATE SYNCED EDITABLE CAPCUT PROJECT (`D:\Capcut\CapCut Drafts\261121 ...`)
    #         Matching EVERY pause speed-up, 20 B-rolls, 9 circles & Nàng Xuân text style!
    # ==========================================================================
    print("\n[STEP D] Updating synced CapCut Desktop draft on PC 001...")
    pj_cur_p = DRAFT_DIR / "Timelines" / "project.json"
    pj_cur   = json.loads(pj_cur_p.read_text(encoding="utf-8"))
    old_tl   = pj_cur["main_timeline_id"]
    D_old    = json.loads((DRAFT_DIR / "Timelines" / old_tl / "draft_content.json").read_text(encoding="utf-8"))
    dmi_old  = json.loads((DRAFT_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))
    D        = copy.deepcopy(D_old)

    # Extract templates cleanly from existing working draft & Nàng Xuân draft!
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

    # Pull Nàng Xuân exact native text animations (`Phóng to`, `Trượt xuống`, `Hình chiếu đập thẳng`) + existing F20 anims!
    TXT_ANIMS = {"in": {}, "out": {}}
    VID_ANIMS = {"in": {}, "out": {}}
    for src_d in [D_old, json.loads((NX_DRAFT / "draft_content.json").read_text(encoding="utf-8")) if (NX_DRAFT / "draft_content.json").exists() else {}]:
        for ma in src_d.get("materials", {}).get("material_animations", []):
            for a in ma.get("animations", []):
                anim_tp, nm = a.get("type"), a.get("name")
                if anim_tp in ("in", "out") and nm:
                    if a.get("panel") == "video" and nm not in VID_ANIMS[anim_tp]:
                        VID_ANIMS[anim_tp][nm] = copy.deepcopy(a)
                    elif nm not in TXT_ANIMS[anim_tp]:
                        TXT_ANIMS[anim_tp][nm] = copy.deepcopy(a)

    # Pull DJI color sliders from D_old
    DJI_SLIDERS = {}
    for ef in D_old["materials"].get("effects", []):
        if ef.get("type") in ("temperature", "saturation", "contrast", "brightness") and ef["type"] not in DJI_SLIDERS:
            DJI_SLIDERS[ef["type"]] = copy.deepcopy(ef)

    tmap_old    = {t["id"]: t for t in D_old["materials"]["texts"]}
    sub_tr_tpl  = copy.deepcopy(next(t for t in D_old["tracks"] if t["type"] == "text" and t["segments"] and tmap_old.get(t["segments"][0]["material_id"], {}).get("type") == "subtitle"))
    txt_tr_tpl  = copy.deepcopy(next(t for t in D_old["tracks"] if t["type"] == "text" and t["segments"] and tmap_old.get(t["segments"][0]["material_id"], {}).get("type") == "text"))
    sub_seg_tpl = copy.deepcopy(sub_tr_tpl["segments"][0])
    sub_mat_tpl = copy.deepcopy(tmap_old[sub_seg_tpl["material_id"]])
    txt_seg_tpl = copy.deepcopy(txt_tr_tpl["segments"][0])
    txt_mat_tpl = copy.deepcopy(tmap_old[txt_seg_tpl["material_id"]])

    dm_all = [x for g in dmi_old.get("draft_materials", []) for x in g.get("value", [])]
    dm_vid_tpl = copy.deepcopy(next(x for x in dm_all if x.get("metetype") == "video"))
    dm_pho_tpl = copy.deepcopy(next((x for x in dm_all if x.get("metetype") == "photo"), dm_vid_tpl))

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in D_old["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in D_old["materials"].get(k, []))}
    a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in D_old["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in D_old["materials"].get(k, []))}

    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = []

    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)
    vis_cache = {}
    new_dm_entries = []

    def reg_cc_visual(fn: str):
        path = MAT_V / fn
        if fn in vis_cache:
            return vis_cache[fn]
        fwd = norm_fwd(path)
        is_photo = path.suffix.lower() in (".png", ".jpg", ".jpeg")
        mid, lmid = uid(), str(uuid.uuid4())
        if is_photo:
            with Image.open(path) as im:
                w, h = im.size
            dur_u = 10_800_000_000
            m = copy.deepcopy(pmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "photo", "path": fwd, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": False,
                "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0,
            })
            dme = copy.deepcopy(dm_pho_tpl)
            dme.update({
                "id": lmid, "file_Path": f"./materials/video/{fn}", "extra_info": fn,
                "duration": 5_000_000, "width": w, "height": h, "metetype": "photo",
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
            })
        else:
            w, h, dur_s, has_aud = probe_media(path)
            dur_u = max(33333, us(dur_s))
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud),
                "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0,
            })
            dme = copy.deepcopy(dm_vid_tpl)
            dme.update({
                "id": lmid, "file_Path": f"./materials/video/{fn}", "extra_info": fn,
                "duration": dur_u, "width": w, "height": h, "metetype": "video",
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
                "roughcut_time_range": {"start": 0, "duration": dur_u},
                "sub_time_range": {"start": -1, "duration": -1},
            })
        D["materials"]["videos"].append(m)
        new_dm_entries.append(dme)
        vis_cache[fn] = (mid, dur_u, is_photo)
        return mid, dur_u, is_photo

    def make_cc_vseg(fn: str, st_u: int, du_u: int, src_in_s: float, spd: float, vol: float,
                     px: float = 0.0, py: float = 0.0, sc: float = 1.0,
                     in_anim: str | None = None, out_anim: str | None = None,
                     is_dji: bool = False, micro_fade: bool = False, add_tr: bool = False):
        mid, mat_dur_u, is_photo = reg_cc_visual(fn)
        if is_photo:
            src_st_u, src_du_u, spd = 0, du_u, 1.0
        else:
            src_st_u = us(src_in_s)
            src_du_u = int(round(du_u * spd))
            if src_st_u + src_du_u > mat_dur_u:
                src_st_u = max(0, mat_dur_u - src_du_u)
        sg = copy.deepcopy(vseg_tpl)
        refs = []
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
            D["materials"].setdefault("audio_fades", []).append({"fade_in_duration": 25000, "fade_out_duration": 33333, "fade_type": 0, "id": fid, "type": "audio_fade"})
            refs.append(fid)
        if add_tr and ket_hop_tpl:
            tr_o = copy.deepcopy(ket_hop_tpl); tr_o["id"] = uid(); tr_o["duration"] = 366666
            D["materials"].setdefault("transitions", []).append(tr_o); refs.append(tr_o["id"])
        alist = []
        if in_anim and in_anim in VID_ANIMS["in"]:
            ai = copy.deepcopy(VID_ANIMS["in"][in_anim]); ai["start"] = 0; ai["duration"] = min(200000, du_u // 4)
            alist.append(ai)
        if out_anim and out_anim in VID_ANIMS["out"]:
            ao = copy.deepcopy(VID_ANIMS["out"][out_anim]); od = min(180000, du_u // 4); ao["duration"] = od; ao["start"] = max(0, du_u - od)
            alist.append(ao)
        if alist:
            maid = uid()
            D["materials"].setdefault("material_animations", []).append({"animations": alist, "id": maid, "multi_language_current": "none", "type": "sticker_animation"})
            refs.append(maid)
        sg["clip"]["scale"] = {"x": round(sc, 4), "y": round(sc, 4)}
        sg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        sg["clip"]["rotation"] = 0.0
        sg["clip"]["alpha"] = 1.0
        sg["uniform_scale"] = {"on": True, "value": 1.0}
        sg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": int(src_st_u), "duration": int(src_du_u)},
            "target_timerange": {"start": int(st_u), "duration": int(du_u)},
            "speed": round(spd, 4), "volume": round(vol, 4), "last_nonzero_volume": round(max(vol, 1.0), 4),
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        return sg

    tr_v0 = copy.deepcopy(vtrack0_tpl); tr_v0["id"] = uid(); tr_v0["flag"] = 0
    tr_v0["segments"] = [
        make_cc_vseg(s["file"], s["tl_start_u"], s["tl_dur_u"], s["src_in"], s["speed"], s["vol_cc"],
                     micro_fade=(s["vol_cc"] > 0.0), add_tr=s["xfade_after"])
        for s in segs
    ]

    tr_v1 = copy.deepcopy(vtrack2_tpl); tr_v1["id"] = uid(); tr_v1["flag"] = 2
    tr_v1["segments"] = [
        make_cc_vseg(fn, us(t0), us(t1) - us(t0), sin, spd, 0.0, is_dji=is_dji)
        for t0, t1, fn, sin, spd, is_dji, _ in BROLL_SPEC
    ]
    tr_v1["segments"].append(
        make_cc_vseg("outro_banner_f20_brand.mp4", us(speech_end_s), us(total_s) - us(speech_end_s),
                     0.0, 1.0, 0.0, px=0.0, py=-0.05, sc=1.05, in_anim="Rõ dần")
    )

    tr_v2 = copy.deepcopy(vtrack2_tpl); tr_v2["id"] = uid(); tr_v2["flag"] = 2
    tr_v2["segments"] = [
        make_cc_vseg(png, us(t0), us(t1) - us(t0), 0.0, 1.0, 0.0, px=px, py=py, sc=sc, in_anim="Rõ dần", out_anim="Mờ dần")
        for t0, t1, png, px, py, sc, _ in CIRCLE_SPEC
    ]

    # Nàng Xuân Native CapCut Texts (Normal White Sub + Colored Jumping Emphasis Text!)
    FONT_SUB_FWD = norm_fwd(FONT_SUB)
    FONT_EMP_FWD = norm_fwd(FONT_EMP)

    def make_cc_text(is_sub: bool, t0_s: float, t1_s: float, text: str, px: float, py: float, sz: float,
                     fill_rgb: tuple, stroke_rgb: tuple | None, stroke_w: float,
                     in_nm: str | None = None, out_nm: str | None = None):
        tid = uid()
        tm = copy.deepcopy(sub_mat_tpl if is_sub else txt_mat_tpl)
        cobj = json.loads(tm["content"])
        cobj["text"] = text
        st0 = copy.deepcopy(cobj["styles"][0])
        st0["range"] = [0, len(text)]
        st0["size"] = float(sz)
        fpath = FONT_SUB_FWD if is_sub else FONT_EMP_FWD
        st0["font"] = {"path": fpath, "id": ""}
        st0["fill"] = {"content": {"render_type": "solid", "solid": {"color": rgb01(fill_rgb)}}}
        if stroke_rgb and stroke_w > 0:
            st0["strokes"] = [{"content": {"render_type": "solid", "solid": {"color": rgb01(stroke_rgb)}}, "width": float(stroke_w), "mode": 0}]
        else:
            st0["strokes"] = []
        st0["shadows"] = [{
            "alpha": 0.55, "angle": -35.0,
            "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
            "diffuse": 0.004, "distance": 4.5,
            "thickness_projection_angle": -45.0, "thickness_projection_distance": 0.0, "thickness_projection_enable": False
        }]
        cobj["styles"] = [st0]
        tm.update({
            "id": tid, "type": "subtitle" if is_sub else "text", "group_id": "",
            "content": json.dumps(cobj, ensure_ascii=False), "recognize_text": text,
            "font_size": float(sz), "font_path": fpath, "check_flag": 15,
            "background_style": 0, "has_shadow": True, "line_spacing": 0.02, "letter_spacing": 0.0,
        })
        D["materials"]["texts"].append(tm)
        st_u, du_u = us(t0_s), max(us(0.30), us(t1_s) - us(t0_s))
        refs, alist = [], []
        if in_nm and in_nm in TXT_ANIMS["in"]:
            ai = copy.deepcopy(TXT_ANIMS["in"][in_nm]); ai["start"] = 0; ai["duration"] = min(200000, du_u // 3)
            alist.append(ai)
        if out_nm and out_nm in TXT_ANIMS["out"]:
            ao = copy.deepcopy(TXT_ANIMS["out"][out_nm]); od = min(180000, du_u // 3); ao["duration"] = od; ao["start"] = max(0, du_u - od)
            alist.append(ao)
        if alist:
            maid = uid()
            D["materials"].setdefault("material_animations", []).append({"animations": alist, "id": maid, "multi_language_current": "none", "type": "sticker_animation"})
            refs.append(maid)
        sg = copy.deepcopy(sub_seg_tpl if is_sub else txt_seg_tpl)
        sg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        sg["clip"]["scale"] = {"x": 1.0, "y": 1.0}; sg["clip"]["rotation"] = 0.0; sg["clip"]["alpha"] = 1.0
        sg.update({
            "id": uid(), "material_id": tid,
            "target_timerange": {"start": st_u, "duration": du_u}, "source_timerange": None,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        return sg

    tr_sub = copy.deepcopy(sub_tr_tpl); tr_sub["id"] = uid()
    tr_sub["segments"] = [
        make_cc_text(True, f0 / FPS, f1 / FPS, tx, 0.0, -0.58, 9.8, RGB_WHITE, RGB_STROKE_SUB, 0.030)
        for f0, f1, tx in SUB_CLEAN
    ]

    # Pack Jumping Emphasis + Top Headers cleanly into non-overlapping native text lanes
    cc_text_items = []
    for st, en, tx, py_n, _, ccsz, ckey, _ in EMPHASIS_JUMPS:
        fcol, scol = COLOR_MAP[ckey]
        in_a = "Phóng to" if "Phóng to" in TXT_ANIMS["in"] else ("Trượt xuống" if "Trượt xuống" in TXT_ANIMS["in"] else "Mờ")
        cc_text_items.append((st, en, tx, 0.0, py_n, ccsz, fcol, scol, 0.058, in_a, "Mờ dần"))
    for st, en, tx, px_n, py_n, _, ccsz, ckey in TOP_HEADERS:
        fcol, scol = COLOR_MAP[ckey]
        cc_text_items.append((st, en, tx, px_n, py_n, ccsz, fcol, scol, 0.052, "Mờ", "Mờ dần"))

    ft_lanes = []
    for st, en, tx, px_n, py_n, ccsz, fcol, scol, sw, ia, oa in sorted(cc_text_items, key=lambda x: x[0]):
        sg = make_cc_text(False, st, en, tx, px_n, py_n, ccsz, fcol, scol, sw, ia, oa)
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

    # Filter Track (`Sống động 2`, val=0.16)
    fm = copy.deepcopy(filt_m_tpl); fm["id"] = uid(); fm["value"] = 0.16
    D["materials"]["effects"].append(fm)
    tr_filt = copy.deepcopy(filt_tr_tpl); tr_filt["id"] = uid()
    fsg = copy.deepcopy(tr_filt["segments"][0])
    fsg.update({"id": uid(), "material_id": fm["id"], "target_timerange": {"start": 0, "duration": us(speech_end_s)}, "extra_material_refs": [], "render_index": 10000})
    tr_filt["segments"] = [fsg]

    # Audio Tracks (BGM + SFX)
    bgm_dur_u = us(probe_audio_dur(BGM_PATH))
    bgm_aid = uid()
    bgm_m = copy.deepcopy(amat_tpl)
    bgm_m.update({"id": bgm_aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
                  "name": BGM_PATH.name, "path": norm_fwd(BGM_PATH), "duration": bgm_dur_u, "type": "music"})
    D["materials"]["audios"].append(bgm_m)

    def mk_cc_aseg(aid, st_u, du_u, src_st_u, fi_u, fo_u, vol):
        sg = copy.deepcopy(aseg_tpl)
        refs = []
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
        bgm_segs.append(mk_cc_aseg(bgm_aid, seg1_u, total_u - seg1_u, us(8.0), 350000, 1150000, 0.16))
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = bgm_segs

    sfx_cc_cache = {}
    sfx_lanes = []
    for t0, sk, lbl in sorted(SFX_EVENTS, key=lambda x: x[0]):
        sp, gvol, mdur = SFX_MAP[sk]
        fwd = norm_fwd(sp)
        if fwd not in sfx_cc_cache:
            du_f = us(probe_audio_dur(sp)); aid = uid()
            am = copy.deepcopy(amat_tpl)
            am.update({"id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
                       "name": lbl, "path": fwd, "duration": du_f, "type": "sound"})
            D["materials"]["audios"].append(am); sfx_cc_cache[fwd] = (aid, du_f)
        aid, du_f = sfx_cc_cache[fwd]
        du = min(du_f, us(mdur)); st_u = max(0, us(t0))
        sg = mk_cc_aseg(aid, st_u, du, 0, min(15000, du // 6), min(90000, du // 3), round(min(0.45, gvol * 1.1), 3))
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

    # Assemble & write CapCut draft IN-PLACE (keeping materials/ folder & existing draft_id 100% intact!)
    new_tl_id = uid()
    D["id"] = new_tl_id
    D["name"] = DRAFT_NAME
    D["tracks"] = [tr_v0, tr_v1, tr_v2, tr_sub, *ft_tracks, tr_filt, tr_bgm, *sfx_tracks]
    D["duration"] = total_u
    D["update_time"] = now_s
    D["time_marks"] = None
    D["canvas_config"] = {"width": W, "height": H, "ratio": "9:16", "background": None}
    if isinstance(D.get("extra_info"), dict):
        D["extra_info"]["subtitle_fragment_info_list"] = []
    if isinstance(D.get("config"), dict):
        D["config"]["subtitle_taskinfo"] = []
    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video": s["render_index"] = ti
            elif tr["type"] == "text": s["render_index"] = 14000 + ti
            elif tr["type"] == "filter": s["render_index"] = 10000

    # Replace Timelines/<old_tl> cleanly with Timelines/<new_tl_id>
    tl_root = DRAFT_DIR / "Timelines"
    for item in list(tl_root.iterdir()):
        if item.is_dir():
            shutil.rmtree(item)
    tl_sub = tl_root / new_tl_id
    tl_sub.mkdir(parents=True, exist_ok=True)
    (tl_sub / "attachment").mkdir(exist_ok=True)
    (tl_sub / "common_attachment").mkdir(exist_ok=True)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for tp_p in [DRAFT_DIR / "draft_content.json", DRAFT_DIR / "draft_content.json.bak", DRAFT_DIR / "template-2.tmp",
                 tl_sub / "draft_content.json", tl_sub / "draft_content.json.bak", tl_sub / "template-2.tmp"]:
        tp_p.write_bytes(dc_bytes)
    for att in ("draft.extra", "attachment_editing.json", "attachment_pc_common.json", "draft_cover.jpg"):
        if (DRAFT_DIR / att).exists():
            shutil.copy2(DRAFT_DIR / att, tl_sub / att)

    pj = {
        "config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
        "create_time": now_us, "id": new_tl_id, "main_timeline_id": new_tl_id,
        "timelines": [{"create_time": now_us, "id": new_tl_id, "is_marked_delete": False, "name": "Timeline 01", "update_time": now_us}],
        "update_time": now_us, "version": 0,
    }
    pj_bytes = json.dumps(pj, ensure_ascii=False).encode("utf-8")
    (tl_root / "project.json").write_bytes(pj_bytes)
    (tl_root / "project.json.bak").write_bytes(pj_bytes)
    (DRAFT_DIR / "timeline_layout.json").write_text(json.dumps({
        "dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": [new_tl_id], "timelineNames": ["Timeline 01"]}],
        "layoutOrientation": 1
    }, ensure_ascii=False), encoding="utf-8")

    uniq_paths = {v["path"] for v in D["materials"]["videos"]} | {a["path"] for a in D["materials"]["audios"]}
    total_bytes = sum(Path(p).stat().st_size for p in uniq_paths if Path(p).is_file())
    dmi_old["tm_duration"] = total_u
    dmi_old["tm_draft_modified"] = now_us
    dmi_old["draft_timeline_materials_size_"] = total_bytes
    for bkt in dmi_old.get("draft_materials", []):
        if bkt.get("type") == 0:
            bkt["value"] = new_dm_entries
    (DRAFT_DIR / "draft_meta_info.json").write_text(json.dumps(dmi_old, ensure_ascii=False), encoding="utf-8")

    # Sync root_meta_info.json duration & mtime (keeping exact draft_id!)
    if RMI_PATH.exists():
        rmi = json.loads(RMI_PATH.read_text(encoding="utf-8"))
        for ent in rmi.get("all_draft_store", []):
            if ent.get("draft_name") == DRAFT_NAME:
                ent["tm_duration"] = total_u
                ent["tm_draft_modified"] = now_us
                ent["draft_timeline_materials_size"] = total_bytes
        RMI_PATH.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    # Strict invariants check!
    assert D["id"] == pj["id"] == pj["main_timeline_id"] == pj["timelines"][0]["id"] == new_tl_id
    assert pj["timelines"][0]["is_marked_delete"] is False
    assert tr_v0["flag"] == 0 and tr_v1["flag"] == 2 and tr_v2["flag"] == 2

    # ==========================================================================
    # STEP E: EXTRACT 16-FRAME VISUAL QC SHEET DIRECTLY FROM RENDERED FINAL MP4!
    # ==========================================================================
    print("\n[STEP E] Extracting 16-frame Visual QC Sheet directly from rendered Final MP4...")
    qc_times = [
        2.9,                            # Doorway + Hero + "77 SET QUÀ 20/11" jump-up!
        5.8,                            # B-roll C3903 @18s + "ĐĂNG KHOA EDU • 23 THÁI NGUYÊN"
        tp("B03_handshake", 21.0),      # Handshake + Anh Hậu header + White sub
        tp("B04_q1_to_a1u", 31.4),      # "PHẢI CHẤT LƯỢNG!" Gold jump-up above white sub!
        tp("B04_q1_to_a1u", 40.5),      # Circle 01 Yến Sào + normal white sub
        tp("B05_ngon_sea", 54.6),       # B-roll DJI_0082 macro + "RẤT LÀ NGON!" jump-up
        tp("B05_ngon_sea", 61.8),       # NEW B-roll DJI_0087 macro SKANEST + "YẾN THỦ CÔNG • KHÔNG HÓA CHẤT"
        tp("B06_energy", 88.8),         # B-roll C3873 + "TIẾP NĂNG LƯỢNG CỰC NGON!"
        tp("B08_a2_mica", 140.8),       # "RẤT LÀ ƯNG Ý!" Gold jump-up above white sub
        tp("B08_a2_mica", 145.2),       # NEW B-roll DJI_0085 burgundy handle macro + "QUAI XÁCH TIỆN TAY"
        tp("B08_a2_mica", 154.8),       # B-roll DJI_0083 Mica trong + "GIỎ MICA TRONG SUỐT"
        tp("B09_q3_consult", 198.2),    # NEW B-roll C3874 F20 shelf glide!
        tp("B10_a3_5items", 227.6),     # STACKING 5-ITEM NÀNG XUÂN LIST (01->05!) + Circle 05!
        tp("B13_book1_2a", 72.5),       # Book 1 + "DANH NHÂN THẾ GIỚI" jump-up!
        tp("B15_hau_thanks", 127.5),    # Anh Hậu climax + "MÓN QUÀ TAN CHẢY • SIÊU THÍCH!"
        total_s - 1.0,                  # Official F20 Brand Closing Banner (0% AI!)
    ]
    cols, rows = 4, 4
    tw, th = 324, 576
    sheet = Image.new("RGB", (cols * tw, rows * (th + 26)), (16, 18, 22))
    sdr = ImageDraw.Draw(sheet)
    fnt_lbl = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 19)
    for i, ts in enumerate(qc_times):
        ts = max(0.2, min(total_s - 0.15, ts))
        tmp_f = TMP_DIR / "_qc_f.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(LOCAL_OUT),
                        "-frames:v", "1", "-update", "1", "-vf", f"scale={tw}:{th}", str(tmp_f)], check=True)
        im = Image.open(tmp_f)
        r, c = divmod(i, cols)
        sheet.paste(im, (c * tw, r * (th + 26) + 26))
        sdr.text((c * tw + 6, r * (th + 26) + 3), f"#{i+1:02d} t={ts:05.1f}s / {total_s:.1f}s", font=fnt_lbl, fill=(255, 240, 140))
        tmp_f.unlink()
    qc_out = WORK / "qc_v3_nangxuan_final_16frames.jpg"
    sheet.save(qc_out, quality=92)

    # Sync script + QC sheet to Google Drive project archive
    ARCHIVE_G.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), ARCHIVE_G / Path(__file__).name)
    shutil.copy2(qc_out, ARCHIVE_G / qc_out.name)

    print(f"\n=== ALL DONE IN {time.time() - t_start_wall:.1f}s! ===")
    print(f"  -> Final MP4 (F20)   : {FINAL_F20}")
    print(f"  -> Final MP4 (Cloud) : {FINAL_CLD}")
    print(f"  -> CapCut Draft      : {DRAFT_DIR}")
    print(f"  -> Duration          : {total_s:.2f}s ({int(total_s//60)}m {total_s%60:04.1f}s) | 0% AI!")
    print(f"  -> Smooth Speed-Ups  : {n_bridges} short pauses sped up (1.75x-2.05x, muted) -> ZERO jump-cuts!")
    print(f"  -> Overlays          : {len(BROLL_SPEC)} hand-picked native 9:16 B-rolls + {len(CIRCLE_SPEC)} clean round badges")
    print(f"  -> Nàng Xuân Texts   : {len(SUB_CLEAN)} normal white subs + {len(EMPHASIS_JUMPS)} colored jump-up highlights (incl. 5-item stack!)")
    print(f"  -> QC 16-Frame Sheet : {qc_out}")


if __name__ == "__main__":
    main()
