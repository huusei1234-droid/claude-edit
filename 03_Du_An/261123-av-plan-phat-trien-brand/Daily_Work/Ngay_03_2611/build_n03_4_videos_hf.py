# -*- coding: utf-8 -*-
"""
Dựng trọn bộ 4 HyperFrames Projects 24fps (1080x1920) cho NGÀY 03 — 26/11/2026 (AN VƯỢNG PHARMA):
- NHỊP CẮT NHANH SÔI ĐỘNG (11–12 cảnh sinh hoạt / ~28s, mỗi cảnh CHỈ 2.0s – 2.65s, 0% kéo giãn slow-mo lê thê!)
- KẾT HỢP 7 CLIP SINH HOẠT ĐỜI THƯỜNG RIÊNG BIỆT + 2 CẢNH SPLIT-SCREEN BENTO ĐÔI CHUYỂN ĐỘNG (0% méo hình!)
- BỎ 100% BỐI CẢNH NHA TRANG -> 100% hoạt động sinh hoạt thực tế bám sát từng câu kịch bản
- TUÂN THỦ KHUYẾN NGHỊ DS LÊ QUÝ (Nhóm Suport Zalo): Bojomi tập trung 100% dân văn phòng & người lớn (0% trẻ em!)
- LỒNG GHÉP SỰ KIỆN BLACK FRIDAY 26/11 & ĐỢT CUỐI SINH NHẬT DROPPII (25/11–30/11)
- END-CARD SỐNG ĐỘNG: Khung mẫu phát video chuyển động thật (đổi cảnh giữa End-Card) + Hộp thật IS-Net sắc nét 100%
- 4 BÀI NHẠC NỀN BGM RIÊNG BIỆT (-18 LUFS + EQ Voice Pocket + Dynamic Ducking) + 100% Vùng An Toàn TikTok x Reels!
"""
import os, sys, json, shutil, subprocess
from pathlib import Path

WORK = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_03_2611")
LOOKS_DIR = WORK / "04_Video_Looks_9x16"
CLIPS_DIR = WORK / "05_Flow_Raw_Clips"
BGM_DIR = WORK / "02_BGM_Normalized"

CUTOUT_DIR = Path(r"G:\My Drive\dự án ngoài\An Vượng\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\01. Ảnh Sản Phẩm Tách Nền & Logo")
FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
SFX_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx")
OV_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k")
LEGAL_TPBS = "Thực phẩm bổ sung. Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh."

COLOR_GRADE_ATTR = (
    'data-color-grading="{&quot;preset&quot;:null,&quot;intensity&quot;:1,'
    '&quot;adjust&quot;:{&quot;exposure&quot;:0.04,&quot;contrast&quot;:0.08,'
    '&quot;highlights&quot;:0.04,&quot;shadows&quot;:0.05,&quot;whites&quot;:0.06,'
    '&quot;blacks&quot;:0,&quot;temperature&quot;:0.03,&quot;tint&quot;:0.02,'
    '&quot;vibrance&quot;:0.12,&quot;saturation&quot;:0.05},'
    '&quot;details&quot;:{&quot;vignette&quot;:0.03,&quot;vignetteMidpoint&quot;:0.5,'
    '&quot;vignetteRoundness&quot;:0,&quot;vignetteFeather&quot;:0.65,&quot;grain&quot;:0,'
    '&quot;grainSize&quot;:0.25,&quot;grainRoughness&quot;:0.5},'
    '&quot;effects&quot;:{&quot;blur&quot;:0,&quot;pixelate&quot;:0,&quot;chromaBleed&quot;:0,'
    '&quot;tapeDamage&quot;:0,&quot;tapeTracking&quot;:0,&quot;tapeNoise&quot;:0,'
    '&quot;tapeSpeed&quot;:0.5,&quot;filmArtifacts&quot;:0,&quot;halftone&quot;:0,'
    '&quot;halftoneSize&quot;:0,&quot;twoInkPrint&quot;:0,&quot;twoInkPrintSize&quot;:0,'
    '&quot;ascii&quot;:0,&quot;asciiSize&quot;:0.065,&quot;asciiInvert&quot;:0,'
    '&quot;asciiStyle&quot;:0,&quot;asciiColor&quot;:1,&quot;asciiRotation&quot;:0,'
    '&quot;dither&quot;:0,&quot;ditherSize&quot;:0,&quot;bloom&quot;:0,&quot;bloomRadius&quot;:8,'
    '&quot;monoScreen&quot;:0,&quot;monoScreenSize&quot;:0,&quot;monoScreenAngle&quot;:0,'
    '&quot;monoScreenSpread&quot;:0,&quot;monoScreenShape&quot;:0,&quot;monoScreenInvert&quot;:0,'
    '&quot;scanlines&quot;:0,&quot;scanlineCount&quot;:0,&quot;scanlineSoftness&quot;:0,'
    '&quot;chromaticAberration&quot;:0,&quot;chromaticAngle&quot;:0,&quot;crtCurvature&quot;:0,'
    '&quot;digitalGlitch&quot;:0,&quot;digitalGlitchColorSplit&quot;:0,'
    '&quot;digitalGlitchLineTear&quot;:0,&quot;digitalGlitchPixelate&quot;:0,'
    '&quot;digitalGlitchBlockAmount&quot;:0,&quot;digitalGlitchBlockDisplacement&quot;:0,'
    '&quot;digitalGlitchBlockOpacity&quot;:0,&quot;digitalGlitchSpeed&quot;:0,'
    '&quot;engraving&quot;:0,&quot;engravingSpacing&quot;:0.41,&quot;engravingMinThickness&quot;:0.2,'
    '&quot;engravingMaxThickness&quot;:0.45,&quot;engravingAngle&quot;:0.25,'
    '&quot;engravingContrast&quot;:0.46,&quot;engravingSharpness&quot;:0.59,'
    '&quot;engravingWave&quot;:0.2,&quot;engravingWaveFrequency&quot;:0.22,'
    '&quot;crosshatch&quot;:0,&quot;crosshatchSpacing&quot;:0.28,&quot;crosshatchThickness&quot;:0.25,'
    '&quot;crosshatchAngle&quot;:0.25,&quot;crosshatchContrast&quot;:0.33,'
    '&quot;crosshatchEdges&quot;:0.5,&quot;crosshatchLineWeight&quot;:0,'
    '&quot;crosshatchWave&quot;:0.33,&quot;crosshatchWaveFrequency&quot;:0.22,'
    '&quot;kuwahara&quot;:0,&quot;kuwaharaRadius&quot;:0.14,&quot;kuwaharaSharpness&quot;:0.31,'
    '&quot;kuwaharaSaturation&quot;:0.5},&quot;lut&quot;:null,&quot;colorSpace&quot;:&quot;rec709&quot;}"'
)


def html_json(obj):
    return json.dumps(obj, separators=(",", ":")).replace('"', "&quot;")


VO_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "highpass", "id": "vhp", "params": {"frequency": 85}},
        {"type": "peaking", "id": "vlow", "params": {"frequency": 210, "gain": -1.8, "q": 1.1}},
        {"type": "peaking", "id": "vpres", "params": {"frequency": 3100, "gain": 1.8, "q": 1.0}},
        {"type": "limiter", "id": "vlim", "params": {"limit": -1.0}},
    ],
})
BGM_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "gain", "id": "bgu", "params": {"gain": 1.18}},
        {"type": "highpass", "id": "bhu", "params": {"frequency": 80}},
        {"type": "peaking", "id": "bcu", "params": {"frequency": 2350, "gain": -4.0, "q": 0.85}},
        {"type": "highshelf", "id": "bau", "params": {"frequency": 7800, "gain": 0.8}},
        {"type": "limiter", "id": "blu", "params": {"limit": -2.5}},
    ],
})

LOCAL_FONT_CSS = """
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-SemiBold.ttf') format('truetype'); font-weight: 600; }
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-Bold.ttf') format('truetype'); font-weight: 700; }
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-ExtraBold.ttf') format('truetype'); font-weight: 800; }
@font-face { font-family: 'MontBlk'; src: url('assets/fonts/Montserrat-Black.ttf') format('truetype'); font-weight: 900; }
"""


def build_ducking(segs, total_dur):
    pts = [{"t": 0.0, "v": 0.56}]
    for seg in segs:
        st, en = seg["start_s"], seg["end_s"]
        t_in = max(0.05, round(st - 0.14, 2))
        t_dk = max(t_in + 0.02, round(st, 2))
        t_rl = min(total_dur - 0.12, round(en, 2))
        t_up = min(total_dur - 0.05, round(en + 0.22, 2))
        if t_in > pts[-1]["t"] + 0.04: pts.append({"t": t_in, "v": 0.50})
        if t_dk > pts[-1]["t"] + 0.02: pts.append({"t": t_dk, "v": 0.30})
        if t_rl > pts[-1]["t"] + 0.02: pts.append({"t": t_rl, "v": 0.30})
        if t_up > pts[-1]["t"] + 0.02: pts.append({"t": t_up, "v": 0.50})
    if pts[-1]["t"] < total_dur - 0.75:
        pts.append({"t": round(total_dur - 0.75, 2), "v": 0.70})
    pts.append({"t": total_dur, "v": 0.72})
    return html_json({"version": 1, "lanes": [{"target": "volume", "points": pts}]})


def prep_clip_natural(src: Path, dst: Path, min_needed_dur: float = 5.2):
    """
    Chuẩn hóa clip 1080x1920@24fps ở TỐC ĐỘ TỰ NHIÊN (1.0x - 0.88x, tuyệt đối KHÔNG kéo slow-mo 2.4x lê thê!),
    bỏ 0.18s khung tĩnh đầu tiên của Flow để ngay frame 0 đã có chuyển động sống động!
    """
    raw_dur = float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(src)],
            text=True,
        ).strip()
    )
    usable = max(1.5, raw_dur - 0.18)
    pts_factor = 1.0 if usable >= min_needed_dur else min(1.22, min_needed_dur / usable)
    vf = f"trim=start=0.18,setpts={pts_factor:.4f}*(PTS-STARTPTS),scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24"
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-vf", vf, "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p",
        str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(src),
            "-vf", vf, "-an",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
            str(dst),
        ], check=True)


def prep_loop_overlay(src: Path, dst: Path, total_dur: float):
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", str(src),
        "-t", f"{total_dur + 1.0:.2f}", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24",
        "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "20", "-b:v", "0", "-pix_fmt", "yuv420p",
        str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", str(src),
            "-t", f"{total_dur + 1.0:.2f}", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24",
            "-an", "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p",
            str(dst),
        ], check=True)


def split_seg_exact(t_start: float, t_end: float, n: int) -> list:
    dur = round(t_end - t_start, 3)
    weights = [0.98, 1.00, 1.02, 1.00][:n]
    wsum = sum(weights)
    cuts, cur = [], t_start
    for i in range(n):
        nxt = t_end if i == n - 1 else round(cur + dur * (weights[i] / wsum), 2)
        cuts.append((round(cur, 2), round(nxt - cur, 2)))
        cur = nxt
    return cuts
def split_seg_fast(t_start: float, t_end: float, max_cut_dur: float = 2.65) -> list:
    """
    Chia mọi đoạn thoại thành các cú cắt nhanh 2.0s – 2.65s (KHÔNG BAO GIỜ để 1 cảnh quá 2.75s!),
    kèm biến thiên Wave Pacing nhẹ (0.94 / 1.00 / 1.06) để nhịp dựng tự nhiên như Editor chuyên nghiệp.
    """
    dur = round(t_end - t_start, 3)
    n = max(2, int((dur + max_cut_dur - 0.05) // max_cut_dur))
    if dur / n > max_cut_dur:
        n += 1
    weights = [0.94, 1.00, 1.06, 0.96, 1.04][:n]
    wsum = sum(weights)
    cuts = []
    cur = t_start
    for i in range(n):
        nxt = t_end if i == n - 1 else round(cur + dur * (weights[i] / wsum), 2)
        cuts.append((round(cur, 2), round(nxt - cur, 2)))
        cur = nxt
    return cuts


CFGS = [
    {
        "vkey": "n03_v1_av_protein_bua_sang_em_bung",
        "slug": "av-n03-v1",
        "prefix": "v1",
        "look_img": "N03_LOOK1_AVP_MORNING_9x16.png",
        "overlay_main": "03_Warm_Window_Sun_Rays_9x16.mp4",
        "ov_opacity": "0.38",
        "bg_dark": "#052B20",
        "ec_bg": "linear-gradient(175deg, #043222 0%, #0A6142 48%, #042B1D 100%)",
        "card_bg": "linear-gradient(145deg, rgba(4,48,32,0.92) 0%, rgba(10,84,56,0.88) 100%)",
        "brand_chip": "AV PROTEIN • BỮA SÁNG",
        "top_pill": "★ INULIN + B-3 ★",
        "box_files": [("av01_protein_a.png", "AV PROTEIN • 350K")],
        "big_hook": {
            "badge": "★ BỮA SÁNG VỘI KHÓ ĂN ĐỒ KHÔ? ★",
            "l1": "30 GIÂY ĐỦ ĐẠM",
            "l2": "ÊM BỤNG CẢ SÁNG!",
            "c1": "#05472F", "c2": "#0B469E", "s1": 70, "s2": 68,
            "badge_bg": "linear-gradient(135deg, #064F34, #0F7B54)",
        },
        "callouts": [
            ("KHÔNG NGÁN ĐỒ KHÔ BUỔI SÁNG", "PHA MÁT 20–40°C TRONG 30S", "Giữ trọn lợi khuẩn B-3 • Vị thơm béo dịu nhẹ"),
            ("TIÊU HÓA NHẸ NHÀNG", "22,05G ĐẠM + INULIN & B-3", "Đạm đậu Hà Lan & gạo — Không lo đầy hơi"),
            ("GỌN NHẸ ĐI LÀM ĐÚNG GIỜ", "CHỈ 17.500Đ / GÓI TIỆN LỢI", "Tỉnh táo tập trung suốt buổi sáng làm việc"),
        ],
        "ec_kicker": "★ ĐẠM THỰC VẬT ÊM BỤNG ★",
        "ec_brand": "AV PROTEIN<br/>20 GÓI / HỘP",
        "ec_sub": "22,05g Đạm đậu & gạo • Chất xơ Inulin • Lợi khuẩn B-3",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "350.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "BLACK FRIDAY & ĐẾN 30/11",
        "ec_promo_l2": "MUA 5 TẶNG 1 BOJOMI (520K)",
        "ec_cta": "▸ NHẮN “ĐẠM SẠCH” NHẬN CÔNG THỨC 30S!",
    },
    {
        "vkey": "n03_v2_bojomi_kieng_3_chan_van_phong",
        "slug": "av-n03-v2",
        "prefix": "v2",
        "look_img": "N03_LOOK2_BOJOMI_OFFICE_9x16.png",
        "overlay_main": "01_Golden_Dust_Bokeh_9x16.mp4",
        "ov_opacity": "0.40",
        "bg_dark": "#042E22",
        "ec_bg": "linear-gradient(175deg, #043222 0%, #0A6142 48%, #042B1D 100%)",
        "card_bg": "linear-gradient(145deg, rgba(4,48,32,0.92) 0%, rgba(10,84,56,0.88) 100%)",
        "brand_chip": "BOJOMI • VĂN PHÒNG",
        "top_pill": "★ CA – D3 – K2 ★",
        "box_files": [("av02_bojomi_b.png", "BOJOMI • 520K")],
        "big_hook": {
            "badge": "★ NGỒI VĂN PHÒNG 8 TIẾNG ÍT NẮNG ★",
            "l1": "BỘ 3 DẪN ĐƯỜNG",
            "l2": "CA – D3 – K2 MK-7!",
            "c1": "#05472F", "c2": "#D91A26", "s1": 70, "s2": 68,
            "badge_bg": "linear-gradient(135deg, #064F34, #0F7B54)",
        },
        "callouts": [
            ("ĐỌC NHÃN CHUẨN KHOA HỌC", "417,6MG CANXI AQUAMIN F", "Canxi hữu cơ từ tảo biển đỏ thân thiện tiêu hóa"),
            ("KIỀNG 3 CHÂN VỮNG CHẮC", "779,4 IU D3 + 169,8µG K2", "Hỗ trợ dẫn Canxi gắn đúng vào hệ xương"),
            ("DÂN CÔNG SỞ & NGƯỜI LỚN", "PHA ẤM 60°C VỊ VANI MỊN", "Thơm béo dễ uống hơn hẳn viên nén to"),
        ],
        "ec_kicker": "★ CANXI TẢO BIỂN NGƯỜI LỚN ★",
        "ec_brand": "BOJOMI VỊ VANI<br/>14 GÓI / HỘP",
        "ec_sub": "417,6mg Canxi Aquamin F • 779,4 IU D3 • 169,8µg K2 • Collagen",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "520.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "BLACK FRIDAY & ĐẾN 30/11",
        "ec_promo_l2": "MUA 3 TẶNG 1 BOJOMI (520K)",
        "ec_cta": "▸ NHẮN “BOJOMI” XEM BẢNG THÀNH PHẦN!",
    },
    {
        "vkey": "n03_v3_curcumilk_3_nguon_nghe_em_bung",
        "slug": "av-n03-v3",
        "prefix": "v3",
        "look_img": "N03_LOOK3_CURCU_AFTERNOON_9x16.png",
        "overlay_main": "06_Organic_Warm_Light_Leak_9x16.mp4",
        "ov_opacity": "0.38",
        "bg_dark": "#331A04",
        "ec_bg": "linear-gradient(175deg, #4A2204 0%, #8C4708 48%, #381802 100%)",
        "card_bg": "linear-gradient(145deg, rgba(72,34,4,0.92) 0%, rgba(132,68,8,0.88) 100%)",
        "brand_chip": "CURCUMILK PHYTO",
        "top_pill": "✦ PHYTOSOME Ý ✦",
        "box_files": [("av04_curcumilk_b.png", "CURCUMILK • 650K")],
        "big_hook": {
            "badge": "✦ SỢ MÙI NGHỆ TƯƠI HĂNG ĐẮNG? ✦",
            "l1": "SỮA DỪA VANI",
            "l2": "CẢ NHÀ ĐỀU MÊ!",
            "c1": "#5E2D00", "c2": "#D91A26", "s1": 70, "s2": 70,
            "badge_bg": "linear-gradient(135deg, #A85200, #DC7B06)",
        },
        "callouts": [
            ("KHÔNG HỀ HĂNG NGHỆ TƯƠI", "NGŨ CỐC SỮA DỪA VỊ VANI", "Thơm béo dịu nhẹ — Cả gia đình dễ uống mỗi ngày"),
            ("3 NGUỒN NGHỆ + PHYTOSOME Ý", "343,2MG CURCUMINOID / GÓI", "Minh bạch nguyên liệu nhập khẩu chuẩn Italia"),
            ("BỮA PHỤ XẾ CHIỀU 15H", "PHA ẤM 40–50°C ÊM BỤNG", "1 gói + 150ml nước ấm nạp năng lượng nhẹ nhàng"),
        ],
        "ec_kicker": "✦ CURCUMIN PHYTOSOME Ý ✦",
        "ec_brand": "CURCUMILK<br/>PHYTO (14 GÓI)",
        "ec_sub": "343,2mg Curcuminoid hệ 3 nguồn nghệ • Ngũ cốc sữa dừa Vani",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "650.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "BLACK FRIDAY & ĐẾN 30/11",
        "ec_promo_l2": "MUA 4 TẶNG 1 CURCUMILK (650K)",
        "ec_cta": "▸ NHẮN “PHYTO” TƯ VẤN LIỆU TRÌNH NHÀ!",
    },
    {
        "vkey": "n03_v4_collamela_vi_dao_100ml_khong_tanh",
        "slug": "av-n03-v4",
        "prefix": "v4",
        "look_img": "N03_LOOK4_COL_EVENING_9x16.png",
        "overlay_main": "04_Anamorphic_Gold_Rose_Flare_9x16.mp4",
        "ov_opacity": "0.40",
        "bg_dark": "#3A081E",
        "ec_bg": "linear-gradient(175deg, #540A2B 0%, #9E1952 48%, #3D061F 100%)",
        "card_bg": "linear-gradient(145deg, rgba(84,10,43,0.92) 0%, rgba(148,22,76,0.88) 100%)",
        "brand_chip": "COLLAMELA • VỊ ĐÀO",
        "top_pill": "★ KHÔNG HỀ TANH ★",
        "box_files": [("av03_collamela_b.png", "COLLAMELA • 920K")],
        "big_hook": {
            "badge": "★ NGẠI UỐNG COLLAGEN VỊ TANH? ★",
            "l1": "VỊ ĐÀO 100ML",
            "l2": "TAN NGAY 10 GIÂY!",
            "c1": "#6E0B35", "c2": "#D91A38", "s1": 70, "s2": 66,
            "badge_bg": "linear-gradient(135deg, #9C124B, #DB2A6F)",
        },
        "callouts": [
            ("THÓI QUEN TỐI NHẸ TÊNH", "100ML NƯỚC MÁT • VỊ ĐÀO", "Thanh ngọt trong veo — Hoàn toàn không tanh"),
            ("PHÂN TỬ NHỎ DỄ HẤP THU", "2.530MG COLLAGEN TRIPEPTIDE", "Kết hợp HA + Vitamin C + Kẽm nuôi dưỡng da"),
            ("GÓI NHỎ TIỆN MANG THEO", "ĐỂ BÀN TRANG ĐIỂM & TÚI XÁCH", "Duy trì đều đặn đón Tết rạng rỡ tươi tắn"),
        ],
        "ec_kicker": "★ COLLAGEN TRIPEPTIDE VỊ ĐÀO ★",
        "ec_brand": "COLLAMELA<br/>HỘP 20 GÓI",
        "ec_sub": "2.530mg Collagen Tripeptide • 25,68mg HA • 87mg C • 3,9mg Kẽm",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "920.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "BLACK FRIDAY & ĐẾN 30/11",
        "ec_promo_l2": "MUA 2 TẶNG 1 HỘP 10G (480K)",
        "ec_cta": "▸ NHẮN “DA ĐẸP” CHỐT QUÀ 480K NGAY!",
    },
]


def build_one(cfg: dict):
    vdir = WORK / cfg["vkey"]
    hf_dir = vdir / "07_HyperFrames_Project"
    comp_dir = hf_dir / "compositions"
    img_dir = hf_dir / "assets" / "images"
    vid_dir = hf_dir / "assets" / "videos"
    aud_dir = hf_dir / "assets" / "audio"
    fnt_dir = hf_dir / "assets" / "fonts"
    for d in (comp_dir, img_dir, vid_dir, aud_dir, fnt_dir):
        d.mkdir(parents=True, exist_ok=True)

    for fn in ["BeVietnamPro-SemiBold.ttf", "BeVietnamPro-Bold.ttf", "BeVietnamPro-ExtraBold.ttf", "Montserrat-Black.ttf"]:
        shutil.copy2(FONTS_DIR / fn, fnt_dir / fn)
    for fn in ["sfx_pop_clean.mp3", "sfx_whoosh_soft.mp3", "sfx_whoosh_cinematic.mp3", "sfx_sparkle_shine.mp3", "sfx_ping_glass.mp3", "sfx_notification_cta.mp3"]:
        sp = SFX_DIR / fn
        if sp.exists():
            shutil.copy2(sp, aud_dir / fn)

    shutil.copy2(LOOKS_DIR / cfg["look_img"], img_dir / "hero_look.png")
    shutil.copy2(CUTOUT_DIR / "logo_an_vuong_orig.png", img_dir / "logo_an_vuong_orig.png")
    for bfn, _ in cfg["box_files"]:
        shutil.copy2(CUTOUT_DIR / bfn, img_dir / bfn)

    vo_data = json.loads((vdir / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
    segs = vo_data["segments"]
    total_dur = float(vo_data["total_duration_s"])
    assert total_dur <= 59.5, f"Video exceeds 60s: {cfg['vkey']} = {total_dur}s"

    shutil.copy2(vo_data["bgm_path"], aud_dir / "bgm_unique.mp3")
    for s in segs:
        shutil.copy2(s["path"], aud_dir / f"{s['id']}.wav")

    # Prep all raw lifestyle + tactile sachet-cutting & water-pouring clips (s01..s09) at NATURAL speed — ZERO bling overlays!
    is_bojomi = (cfg["prefix"] == "v2")
    is_collamela = (cfg["prefix"] == "v4")
    for ci in range(1, 10):
        src_ci = CLIPS_DIR / f"{cfg['prefix']}_s0{ci}.mp4"
        dst_ci = vid_dir / f"s0{ci}.mp4"
        if src_ci.exists() and (not dst_ci.exists() or dst_ci.stat().st_size < 50_000):
            prep_clip_natural(src_ci, dst_ci, min_needed_dur=4.8)

    s0, s1, s2, s3, s4 = segs
    t1, t2, t3 = float(s0["shot_end_s"]), float(s1["shot_end_s"]), float(s2["shot_end_s"])
    end_start = float(s3["shot_end_s"])
    end_dur = round(total_dur - end_start, 2)

    # FAST LIFESTYLE PACING + FULL 4-BEAT PREPARATION SEQUENCE (1. Cắt/xé gói -> 2. Đổ bột vào ly -> 3. Chế nước -> 4. Khuấy tan mịn!)
    cuts_seg0 = split_seg_fast(0.0, t1, max_cut_dur=2.60)
    cuts_seg1 = split_seg_exact(t1, t2, 4)  # Đầy đủ 4 bước pha liên hoàn (Cắt gói -> Đổ bột -> Chế nước -> Khuấy mịn)!
    cuts_seg2 = split_seg_exact(t2, t3, 3)
    cuts_seg3 = split_seg_fast(t3, end_start, max_cut_dur=2.60)

    tear_pour_clip = "s08.mp4"
    pour_water_clip = "s04.mp4" if is_bojomi else ("s03.mp4" if is_collamela else "s09.mp4")
    stir_smooth_clip = "s05.mp4" if is_bojomi else "s04.mp4"
    hero_box_clip = "s03.mp4" if is_bojomi else "s05.mp4"
    prep_table_clip = "s01.mp4" if is_bojomi else ("s02.mp4" if is_collamela else "s03.mp4")
    prep_table_ms = 1.65 if (is_bojomi or is_collamela) else 0.05

    seg_recipes = [
        # Seg 0 (Mở màn sinh hoạt & chuẩn bị bàn/ly):
        [
            ("full", "s01.mp4", 0.05, 1.00, 1.04),
            ("full", "s02.mp4", 0.05, 1.04, 1.00),
            ("full", prep_table_clip, prep_table_ms, 1.00, 1.05),
        ],
        # Seg 1 (TRỌN BỘ CÁCH PHA ĐẦY ĐỦ 4 NHỊP: 1. Cắt/xé gói -> 2. Đổ bột vào ly -> 3. Chế nước vào ly -> 4. Khuấy tan mịn!):
        [
            ("full", tear_pour_clip, 0.05, 1.00, 1.04),
            ("full", tear_pour_clip, 2.15, 1.10, 1.04),
            ("full", pour_water_clip, 0.05, 1.04, 1.00),
            ("full", stir_smooth_clip, 0.05, 1.00, 1.05),
        ],
        # Seg 2 (Thành phần khoa học + Hộp thật + Split-Bento Đổ bột & Khuấy mịn + Uống thưởng thức):
        [
            ("full", hero_box_clip, 0.05, 1.00, 1.04),
            ("split", (tear_pour_clip, 2.15, stir_smooth_clip, 1.15), 0.0, 1.0, 1.0),
            ("full", "s06.mp4", 0.05, 1.00, 1.05),
        ],
        # Seg 3 (Thói quen sinh hoạt năng động mỗi ngày):
        [
            ("full", "s07.mp4", 0.05, 1.00, 1.04),
            ("full", "s06.mp4", 1.55, 1.08, 1.02),
            ("full", "s07.mp4", 1.60, 1.07, 1.01),
        ],
    ]

    all_beats = []
    for seg_cuts, recipes in zip([cuts_seg0, cuts_seg1, cuts_seg2, cuts_seg3], seg_recipes):
        for idx_c, (st, du) in enumerate(seg_cuts):
            rcp = recipes[idx_c % len(recipes)]
            all_beats.append((st, du, *rcp))

    max_beat_dur = max(b[1] for b in all_beats)
    print(f"  [{cfg['vkey']}] {len(all_beats)} fast lifestyle cuts in {end_start:.2f}s (avg={end_start/len(all_beats):.2f}s/cut, max={max_beat_dur:.2f}s/cut)", flush=True)

    # HyperFrames metadata
    (hf_dir / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": False}, "authoringSkill": "hyperframes",
    }, indent=2), encoding="utf-8")
    (hf_dir / "package.json").write_text(json.dumps({
        "name": cfg["slug"], "private": True, "type": "module",
        "scripts": {"check": "npx --yes hyperframes@0.9.38 check", "render": "npx --yes hyperframes@0.9.38 render"},
    }, indent=2), encoding="utf-8")
    (hf_dir / "meta.json").write_text(json.dumps({
        "title": vo_data["title"], "width": 1080, "height": 1920, "fps": 24, "duration": total_dur,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    bgm_auto = build_ducking(segs, total_dur)
    vo_tags = [
        f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
        f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{5 if i%2==0 else 6}" '
        f'data-volume="1.32" data-fade-in="0.04" data-fade-out="0.06" data-fx-chain="{VO_FX}"></audio>'
        for i, s in enumerate(segs)
    ]

    sfx = [
        ("sfx-01", "sfx_pop_clean.mp3", 0.10, 0.55, 9, 0.20),
        ("sfx-02", "sfx_whoosh_soft.mp3", round(t1 - 0.11, 2), 0.55, 9, 0.18),
        ("sfx-03", "sfx_whoosh_soft.mp3", round(t2 - 0.11, 2), 0.55, 9, 0.18),
        ("sfx-04", "sfx_ping_glass.mp3", round(t3 + 0.08, 2), 0.80, 10, 0.20),
        ("sfx-05", "sfx_whoosh_cinematic.mp3", round(end_start - 0.12, 2), 0.80, 9, 0.22),
        ("sfx-06", "sfx_notification_cta.mp3", round(end_start + 1.25, 2), 2.00, 11, 0.18),
    ]
    sfx_tags = [
        f'      <audio id="{sid}" class="clip" src="assets/audio/{fn}" data-start="{st}" '
        f'data-duration="{du}" data-track-index="{tr}" data-volume="{vol}" data-fade-out="0.16"></audio>'
        for sid, fn, st, du, tr, vol in sfx if (aud_dir / fn).exists()
    ]

    # Remove old cinema-fx.html if present
    (comp_dir / "cinema-fx.html").unlink(missing_ok=True)

    # index.html — CLEAN ZERO-BLING ARCHITECTURE
    (hf_dir / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{vo_data["title"]}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      {LOCAL_FONT_CSS}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: {cfg["bg_dark"]}; font-family: 'BeVN', sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .overlay-host {{ position: absolute; inset: 0; z-index: 14; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="{end_start}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene-host" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{end_start}" data-duration="{end_dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <audio id="bgm-main" class="clip" src="assets/audio/bgm_unique.mp3" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="7" data-fade-in="0.22" data-fade-out="0.85" data-fx-chain="{BGM_FX}" data-automation="{bgm_auto}"></audio>
{chr(10).join(vo_tags)}
{chr(10).join(sfx_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""", encoding="utf-8")

    # 1. main-video.html — 11–12 Fast Cuts + Dual-Layer Split-Screen Bento Cards!
    shot_els, shot_anims = [], []
    for idx, (st, du, kind, src_info, mstart, sc0, sc1) in enumerate(all_beats):
        rid = f"rig{idx+1}"
        if kind == "full":
            tr = 1 + (idx % 3)
            shot_els.append(
                f'    <div id="{rid}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>\n'
                f'      <video {COLOR_GRADE_ATTR} id="v{idx+1}" class="clip bg-video" src="assets/videos/{src_info}" '
                f'data-start="{st}" data-duration="{du}" data-media-start="{mstart}" data-hf-media-start-basis="local" '
                f'data-track-index="{tr}" muted playsinline></video>\n'
                f'    </div>'
            )
            shot_anims.append(
                f'    tl.fromTo("#{rid}", {{ scale: {sc0} }}, {{ scale: {sc1}, duration: {du}, ease: "none", immediateRender: false }}, {st});'
            )
        else:
            top_fn, top_ms, bot_fn, bot_ms = src_info
            shot_els.append(
                f'    <div id="{rid}" class="bento-wrap" data-layout-ignore>\n'
                f'      <div id="{rid}a" class="bento-card bento-top">\n'
                f'        <video {COLOR_GRADE_ATTR} id="vt{idx+1}" class="clip bento-vid" src="assets/videos/{top_fn}" '
                f'data-start="{st}" data-duration="{du}" data-media-start="{top_ms}" data-hf-media-start-basis="local" '
                f'data-track-index="4" muted playsinline></video>\n'
                f'      </div>\n'
                f'      <div id="{rid}b" class="bento-card bento-bot">\n'
                f'        <video {COLOR_GRADE_ATTR} id="vb{idx+1}" class="clip bento-vid" src="assets/videos/{bot_fn}" '
                f'data-start="{st}" data-duration="{du}" data-media-start="{bot_ms}" data-hf-media-start-basis="local" '
                f'data-track-index="5" muted playsinline></video>\n'
                f'      </div>\n'
                f'    </div>'
            )
            shot_anims.append(
                f'    tl.set("#{rid}", {{ opacity: 1 }}, {st})\n'
                f'      .fromTo("#{rid}a", {{ opacity: 0, y: -22, scale: 0.95 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.24, ease: "power2.out", immediateRender: false }}, {st})\n'
                f'      .fromTo("#{rid}b", {{ opacity: 0, y: 22, scale: 0.95 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.24, ease: "power2.out", immediateRender: false }}, {round(st + 0.12, 2)})\n'
                f'      .set("#{rid}", {{ opacity: 0 }}, {round(st + du, 2)});'
            )

    (comp_dir / "main-video.html").write_text(f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: {cfg["bg_dark"]}; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 42%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .bento-wrap {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; z-index: 6; opacity: 0;
      background: {cfg["ec_bg"]};
    }}
    .bento-card {{
      position: absolute; left: 58px; width: 814px; border-radius: 38px; overflow: hidden;
      border: 4px solid rgba(255,228,136,0.92); box-shadow: 0 18px 40px rgba(0,0,0,0.44);
    }}
    .bento-top {{ top: 336px; height: 468px; transform: rotate(-0.6deg); }}
    .bento-bot {{ top: 826px; height: 468px; transform: rotate(0.6deg); }}
    .bento-vid {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 28%; display: block; }}
  </style>
  <div id="root" data-composition-id="main-video" data-width="1080" data-height="1920" data-start="0" data-duration="{end_start}">
{chr(10).join(shot_els)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(shot_anims)}
    window.__timelines["main-video"] = tl;
  </script>
</template>
""", encoding="utf-8")

    # 3. safe-overlays.html — Clean editorial typography (ZERO metallic sheen, ZERO sparkle bling!)
    hk = cfg["big_hook"]
    hk_end = round(t1 - 0.14, 2)
    callouts = [
        ("c2", round(t1 + 0.14, 2), round(t2 - t1 - 0.30, 2), *cfg["callouts"][0]),
        ("c3", round(t2 + 0.14, 2), round(t3 - t2 - 0.30, 2), *cfg["callouts"][1]),
        ("c4", round(t3 + 0.14, 2), round(end_start - t3 - 0.30, 2), *cfg["callouts"][2]),
    ]
    c_divs, c_anims = [], []
    for cid, st, du, tag, big, sub in callouts:
        c_divs.append(f"""
      <div id="{cid}" class="safe-card" data-layout-ignore>
        <div class="sc-tag">{tag}</div>
        <div class="sc-big">{big}</div>
        <div class="sc-sub">{sub}</div>
      </div>""")
        c_anims.append(
            f'    tl.fromTo("#{cid}", {{ opacity: 0, y: 28, scale: 0.94, filter: "blur(12px)" }}, '
            f'{{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.2)", immediateRender: false }}, {st})\n'
            f'      .to("#{cid}", {{ opacity: 0, y: -10, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, {round(st + du - 0.20, 2)});'
        )

    float_html = f"""    <div id="prod-real" class="prod-float" data-layout-ignore>
      <img class="pf-box-single" src="assets/images/{cfg['box_files'][0][0]}" alt="Box" />
    </div>"""

    (comp_dir / "safe-overlays.html").write_text(f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; pointer-events: none; font-family: 'BeVN', sans-serif; }}
    .big-hook-wrap {{
      position: absolute; bottom: 400px; left: 56px; width: 814px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
      padding: 22px 16px 26px; overflow: hidden;
      background: linear-gradient(180deg, rgba(255,255,255,0.46) 0%, rgba(255,255,255,0.86) 100%);
      backdrop-filter: blur(8px);
      border: 4px solid rgba(255,255,255,0.94); border-radius: 32px;
      box-shadow: 0 20px 44px rgba(0,0,0,0.34); z-index: 20;
    }}
    .bh-badge {{
      background: {hk["badge_bg"]}; color: #FFF8D6; border: 3px solid #FFE288;
      border-radius: 999px; padding: 10px 24px; font-weight: 800; font-size: 25px;
      letter-spacing: 0.4px; box-shadow: 0 8px 20px rgba(0,0,0,0.30); margin-bottom: 14px;
    }}
    .bh-l1 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: {hk["s1"]}px; line-height: 1.06;
      color: {hk["c1"]}; white-space: nowrap;
      -webkit-text-stroke: 14px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 8px 16px rgba(0,0,0,0.34));
    }}
    .bh-l2 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: {hk["s2"]}px; line-height: 1.08;
      margin-top: 8px; color: {hk["c2"]}; white-space: nowrap;
      -webkit-text-stroke: 14px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 10px 20px rgba(0,0,0,0.38));
    }}
    .brand-chip {{
      position: absolute; top: 256px; left: 58px; opacity: 0;
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.96); border: 3px solid #E2B448;
      border-radius: 18px; padding: 8px 18px;
      box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }}
    .brand-chip img {{ height: 48px; width: auto; display: block; }}
    .brand-chip span {{ font-weight: 800; font-size: 21px; color: #064D33; letter-spacing: 0.3px; }}
    .top-pill {{
      position: absolute; top: 262px; right: 58px; opacity: 0;
      background: {hk["badge_bg"]}; color: #FFF8DC;
      border: 3px solid #FFE288; border-radius: 999px; padding: 10px 20px;
      font-weight: 800; font-size: 22px; letter-spacing: 0.3px;
      box-shadow: 0 10px 24px rgba(0,0,0,0.32);
    }}
    .prod-float {{
      position: absolute; left: 56px; bottom: 686px; width: 420px; height: 340px;
      display: flex; align-items: flex-end; justify-content: flex-start;
      opacity: 0; z-index: 16;
    }}
    .pf-box-single {{ height: 256px; width: auto; filter: drop-shadow(0 16px 26px rgba(0,0,0,0.44)); }}
    .safe-card {{
      position: absolute; left: 56px; bottom: 394px; width: 814px; overflow: hidden;
      background: {cfg["card_bg"]};
      border: 3.5px solid #F4CF68; border-left: 11px solid #FFE480;
      border-radius: 28px; padding: 22px 26px;
      box-shadow: 0 18px 38px rgba(0,0,0,0.44); opacity: 0;
    }}
    .card-sheen {{
      position: absolute; top: 0; bottom: 0; width: 170px; pointer-events: none;
      background: linear-gradient(105deg, rgba(255,255,255,0) 0%, rgba(255,250,210,0.34) 50%, rgba(255,255,255,0) 100%);
      transform: skewX(-20deg); opacity: 0;
    }}
    .sc-tag {{ font-weight: 800; font-size: 24px; color: #FFE888; letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.40); }}
    .sc-big {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 48px; line-height: 1.12; color: #FFFFFF; text-shadow: 0 4px 12px rgba(0,0,0,0.46); }}
    .sc-sub {{ font-weight: 700; font-size: 28px; color: #F2FFF8; margin-top: 10px; line-height: 1.26; text-shadow: 0 2px 8px rgba(0,0,0,0.35); }}
  </style>
  <div id="root" data-composition-id="safe-overlays" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <div id="big-hook" class="big-hook-wrap" data-layout-ignore>
      <div class="bh-badge">{hk["badge"]}</div>
      <div class="bh-l1">{hk["l1"]}</div>
      <div class="bh-l2">{hk["l2"]}</div>
    </div>
    <div id="top-brand" class="brand-chip" data-layout-ignore>
      <img src="assets/images/logo_an_vuong_orig.png" alt="An Vuong" />
      <span>{cfg["brand_chip"]}</span>
    </div>
    <div id="top-pill" class="top-pill" data-layout-ignore>{cfg["top_pill"]}</div>
{float_html}
    {"".join(c_divs)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#big-hook", {{ scale: 0.92, y: 10 }}, {{ scale: 1.0, y: 0, duration: 0.26, ease: "back.out(1.45)" }}, 0.0)
      .to("#big-hook", {{ opacity: 0, y: -18, filter: "blur(12px)", duration: 0.24, ease: "power2.in" }}, {round(hk_end - 0.24, 2)});
    tl.fromTo("#top-brand", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power2.out", immediateRender: false }}, 0.12)
      .to("#top-brand", {{ opacity: 0, duration: 0.24 }}, {round(end_start - 0.25, 2)});
    tl.fromTo("#top-pill", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1.0, duration: 0.30, ease: "back.out(1.5)", immediateRender: false }}, 0.18)
      .to("#top-pill", {{ opacity: 0, duration: 0.24 }}, {round(end_start - 0.25, 2)});
    tl.fromTo("#prod-real", {{ opacity: 0, y: 34, scale: 0.88 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.34, ease: "back.out(1.35)", immediateRender: false }}, {round(t3 + 0.18, 2)})
      .to("#prod-real", {{ opacity: 0, y: -14, filter: "blur(8px)", duration: 0.24, ease: "power2.in" }}, {round(end_start - 0.26, 2)});
{chr(10).join(c_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
""", encoding="utf-8")

    # 4. endcard.html — Live 2-Cut Video Portrait inside .ec-model + Real IS-Net Box + Black Friday 26/11 & 30/11 Deal!
    ec_half = round(end_dur / 2.0, 2)
    ec_rem = round(end_dur - ec_half, 2)
    (comp_dir / "endcard.html").write_text(f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: {cfg["ec_bg"]}; font-family: 'BeVN', sans-serif; }}
    .ec-model {{
      position: absolute; top: 256px; right: 58px; width: 404px; height: 590px;
      border-radius: 30px; overflow: hidden; border: 3.5px solid rgba(244,204,100,0.92);
      box-shadow: 0 20px 44px rgba(0,0,0,0.40); background: #08241A;
    }}
    .ec-model video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 18%; display: block; }}
    .ec-logo {{
      position: absolute; top: 260px; left: 58px;
      background: rgba(255,255,255,0.96); border: 3px solid #E5B442; border-radius: 22px;
      padding: 10px 22px; box-shadow: 0 10px 26px rgba(0,0,0,0.25);
    }}
    .ec-logo img {{ height: 68px; width: auto; display: block; }}
    .ec-title {{ position: absolute; top: 374px; left: 58px; width: 530px; }}
    .ec-kicker {{
      display: inline-block; background: linear-gradient(135deg, #D91A26, #A10B16); color: #FFF8DC;
      border: 2px solid #FFE288; border-radius: 999px; padding: 5px 18px;
      font-weight: 800; font-size: 21px; letter-spacing: 0.4px; margin-bottom: 8px;
    }}
    .ec-brand {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 52px; line-height: 1.08; color: #FFFFFF; text-shadow: 0 5px 16px rgba(0,0,0,0.38); }}
    .ec-sub {{ font-weight: 700; font-size: 25px; color: #EFFCF5; margin-top: 10px; line-height: 1.28; }}
    .ec-boxes-single {{ position: absolute; left: 106px; top: 684px; width: 420px; height: 412px; display: flex; align-items: flex-end; justify-content: center; }}
    .b-col {{ display: flex; flex-direction: column; align-items: center; }}
    .b-tag {{ background: rgba(4,48,32,0.94); color: #FFF8DC; border: 2.5px solid #F4CC62; border-radius: 999px; padding: 5px 16px; font-weight: 800; font-size: 19px; margin-bottom: 6px; white-space: nowrap; }}
    .b-single {{ height: 360px; width: auto; filter: drop-shadow(0 20px 30px rgba(0,0,0,0.48)); }}
    .ec-deal {{
      position: absolute; left: 58px; top: 1110px; width: 812px;
      background: linear-gradient(155deg, rgba(255,255,255,0.98), rgba(255,248,228,0.98));
      border: 4px solid #E5B442; border-radius: 28px; padding: 20px 22px;
      box-shadow: 0 18px 36px rgba(0,0,0,0.36);
    }}
    .ec-prow {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
    .ep-l {{ font-weight: 800; font-size: 20px; color: #074C32; }}
    .ep-n {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 56px; line-height: 1.02; color: #0B40A8; }}
    .ep-pr {{
      background: {cfg["ec_promo_bg"]}; border: 3px solid #FFE288;
      border-radius: 18px; padding: 12px 15px; text-align: center;
      box-shadow: 0 8px 18px rgba(0,0,0,0.28);
    }}
    .ep-1 {{ font-weight: 800; font-size: 17px; color: #FFF3B0; }}
    .ep-2 {{ font-weight: 800; font-size: 19px; color: #FFFFFF; margin-top: 3px; white-space: nowrap; }}
    .ec-cta {{
      margin-top: 15px; background: linear-gradient(90deg, #074F34, #0E744E);
      border: 3px solid #F2CC66; border-radius: 18px; padding: 15px 16px;
      text-align: center; font-weight: 800; font-size: 25px; color: #FFF8D6;
    }}
    .ec-legal {{
      position: absolute; left: 58px; top: 1464px; width: 812px;
      font-weight: 600; font-size: 20px; line-height: 1.32; color: #F0FCF6;
      text-shadow: 0 2px 6px rgba(0,0,0,0.48);
    }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920" data-start="0" data-duration="{end_dur}">
    <div id="ec-m" class="ec-model" data-layout-ignore>
      <video id="ecm1" class="clip" src="assets/videos/s06.mp4" data-start="0" data-duration="{ec_half}" data-media-start="0.2" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
      <video id="ecm2" class="clip" src="assets/videos/s07.mp4" data-start="{ec_half}" data-duration="{ec_rem}" data-media-start="0.2" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
    <div id="ec-l" class="ec-logo" data-layout-ignore><img src="assets/images/logo_an_vuong_orig.png" alt="Logo" /></div>
    <div id="ec-t" class="ec-title" data-layout-ignore>
      <div class="ec-kicker">{cfg["ec_kicker"]}</div>
      <div class="ec-brand">{cfg["ec_brand"]}</div>
      <div class="ec-sub">{cfg["ec_sub"]}</div>
    </div>
    <div id="ec-b" class="ec-boxes-single" data-layout-ignore>
      <div id="eb1" class="b-col">
        <div class="b-tag">{cfg['box_files'][0][1]}</div>
        <img class="b-single" src="assets/images/{cfg['box_files'][0][0]}" alt="Box" />
      </div>
    </div>
    <div id="ec-d" class="ec-deal" data-layout-ignore>
      <div class="ec-prow">
        <div>
          <div class="ep-l">{cfg["ec_price_label"]}</div>
          <div class="ep-n">{cfg["ec_price"]}</div>
        </div>
        <div class="ep-pr">
          <div class="ep-1">{cfg["ec_promo_l1"]}</div>
          <div class="ep-2">{cfg["ec_promo_l2"]}</div>
        </div>
      </div>
      <div class="ec-cta">{cfg["ec_cta"]}</div>
    </div>
    <div id="ec-g" class="ec-legal" data-layout-ignore>{LEGAL_TPBS} Hotline: 0867 399 268</div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#ec-m", {{ opacity: 0, scale: 1.06, x: 24 }}, {{ opacity: 1, scale: 1.0, x: 0, duration: 0.42, ease: "power3.out", immediateRender: false }}, 0.05)
      .fromTo("#ec-l", {{ opacity: 0, y: -18 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out", immediateRender: false }}, 0.12)
      .fromTo("#ec-t", {{ opacity: 0, x: -24, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.36, ease: "power3.out", immediateRender: false }}, 0.22)
      .fromTo("#eb1",  {{ opacity: 0, y: 36, scale: 0.90 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "back.out(1.35)", immediateRender: false }}, 0.32)
      .fromTo("#ec-d", {{ opacity: 0, y: 30, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.38, ease: "power3.out", immediateRender: false }}, 0.62)
      .fromTo("#ec-g", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.28, immediateRender: false }}, 0.84);
    window.__timelines["endcard"] = tl;
  </script>
</template>
""", encoding="utf-8")

    print(f"[BUILT N03 FAST HF] {cfg['vkey']} ({total_dur:.2f}s, {len(all_beats)} fast cuts + 2-cut live EndCard)", flush=True)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for i, c in enumerate(CFGS, 1):
        if arg in ("all", f"v{i}", c["vkey"]):
            build_one(c)


if __name__ == "__main__":
    main()
