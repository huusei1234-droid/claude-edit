# -*- coding: utf-8 -*-
"""
Dựng trọn bộ 5 HyperFrames Projects 24fps (1080x1920) cho NGÀY 02 — 25/11/2026 (AN VƯỢNG PHARMA):
- 5 diện mạo & bối cảnh TP. Nha Trang hoàn toàn khác nhau
- 5 bài nhạc nền BGM riêng biệt (-18 LUFS + EQ Voice Pocket + Dynamic Ducking)
- Thời lượng < 1 phút (<= 55s)
- Lớp phủ điện ảnh thật Screen (video_overlays_4k/ + Soft Pearl Bling + Specular Sheen)
- Text cực to siêu dễ đọc 100% trong Vùng An Toàn TikTok x Reels (X=56..870px, Y<=1534px)
- 100% Hộp thật IS-Net & 100% CHUẨN CTKM 25/11–30/11 (0% nhãn quà sai trên bộ đôi 870K!)
"""
import os, sys, json, shutil, subprocess
from pathlib import Path

WORK = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_02_2511")
LOOKS_DIR = WORK / "04_Video_Looks_9x16"
CLIPS_DIR = WORK / "05_Flow_Raw_Clips"
BGM_DIR = WORK / "02_BGM_Normalized"

CUTOUT_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG")
FONTS_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
SFX_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\sfx_studio")
OV_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k")
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


def prep_clip_to_dur(src: Path, dst: Path, target_dur: float):
    """Smoothly time-stretch (constant gentle slow-mo) + GPU encode 1080x1920@24fps so HyperFrames never stalls on short clip."""
    raw_dur = float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(src)],
            text=True,
        ).strip()
    )
    need_dur = target_dur + 0.55
    pts_factor = max(1.0, min(2.4, need_dur / max(1.0, raw_dur)))
    vf = f"setpts={pts_factor:.4f}*PTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24"
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-vf", vf, "-t", f"{need_dur:.2f}", "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p",
        str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        cmd = [
            "ffmpeg", "-y", "-v", "error", "-i", str(src),
            "-vf", vf, "-t", f"{need_dur:.2f}", "-an",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
            str(dst),
        ]
        subprocess.run(cmd, check=True)


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


CFGS = [
    {
        "vkey": "n02_v1_av_protein_leucine",
        "slug": "av-n02-v1",
        "prefix": "v1",
        "look_img": "N02_LOOK1_AVP_GYM_9x16.png",
        "overlay_main": "03_Warm_Window_Sun_Rays_9x16.mp4",
        "ov_opacity": "0.42",
        "bg_dark": "#052B20",
        "ec_bg": "linear-gradient(175deg, #043222 0%, #0A6142 48%, #042B1D 100%)",
        "card_bg": "linear-gradient(145deg, rgba(4,48,32,0.92) 0%, rgba(10,84,56,0.88) 100%)",
        "brand_chip": "AV PROTEIN • NHA TRANG",
        "top_pill": "★ 1.632MG LEUCINE ★",
        "is_duo": False,
        "box_files": [("av01_protein_a.png", "AV PROTEIN • 350K")],
        "big_hook": {
            "badge": "★ TẬP SÁNG GIỮ DÁNG NHA TRANG ★",
            "l1": "1.632MG LEUCINE",
            "l2": "GIỮ CƠ SĂN CHẮC!",
            "c1": "#05472F", "c2": "#0B469E", "s1": 72, "s2": 72,
            "badge_bg": "linear-gradient(135deg, #064F34, #0F7B54)",
        },
        "callouts": [
            ("CHỈ 30 GIÂY MỖI SÁNG", "PHA NƯỚC MÁT 20–40°C", "Bảo toàn lợi khuẩn B-3 & vị thơm béo nhẹ"),
            ("CHỈ SỐ MINH BẠCH", "22,05G ĐẠM • 1.632MG LEUCINE", "Đạm đậu Hà Lan & gạo hỗ trợ duy trì khối cơ"),
            ("ÊM BỤNG KHÔNG ĐẦY HƠI", "CHẤT XƠ INULIN + LỢI KHUẨN B-3", "Chỉ 17.500đ/gói — Gọn nhẹ cho người bận rộn"),
        ],
        "ec_kicker": "★ ĐẠM THỰC VẬT ÊM BỤNG ★",
        "ec_brand": "AV PROTEIN<br/>20 GÓI / HỘP",
        "ec_sub": "22,05g Đạm đậu & gạo • 1.632mg L-Leucine • Inulin • B-3",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "350.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "CTKM 25/11 – 30/11",
        "ec_promo_l2": "MUA 5 TẶNG 1 BOJOMI (520K)",
        "ec_cta": "▸ NHẮN “ĐẠM SẠCH” NHẬN THỰC ĐƠN SAU TẬP!",
    },
    {
        "vkey": "n02_v2_bojomi_chay_bo_60c",
        "slug": "av-n02-v2",
        "prefix": "v2",
        "look_img": "N02_LOOK2_BOJOMI_RUN5_9x16.png",
        "overlay_main": "01_Golden_Dust_Bokeh_9x16.mp4",
        "ov_opacity": "0.46",
        "bg_dark": "#042E22",
        "ec_bg": "linear-gradient(175deg, #043222 0%, #0A6142 48%, #042B1D 100%)",
        "card_bg": "linear-gradient(145deg, rgba(4,48,32,0.92) 0%, rgba(10,84,56,0.88) 100%)",
        "brand_chip": "BOJOMI • CHẠY BỘ SÁNG",
        "top_pill": "★ PHA ẤM 60°C ★",
        "is_duo": False,
        "box_files": [("av02_bojomi_b.png", "BOJOMI • 520K")],
        "big_hook": {
            "badge": "★ CHẠY BỘ BIỂN NHA TRANG ★",
            "l1": "PHA BOJOMI 60°C",
            "l2": "TAN MỊN VỊ VANI!",
            "c1": "#05472F", "c2": "#D91A26", "s1": 74, "s2": 72,
            "badge_bg": "linear-gradient(135deg, #064F34, #0F7B54)",
        },
        "callouts": [
            ("BÍ KÍP PHA KHÔNG VÓN", "1 GÓI + 200ML NƯỚC ẤM 60°C", "Bột ngũ cốc vị Vani tan mịn, thơm béo nhẹ bụng"),
            ("KIỀNG 3 CHÂN XƯƠNG KHỚP", "417,6MG CANXI • D3 • K2 MK-7", "Canxi hữu cơ tảo biển đỏ Aquamin F dễ hấp thu"),
            ("DẺO DAI MỖI KM CHẠY", "THÊM 201,4MG COLLAGEN", "Đồng hành chăm sóc khung xương khớp bền bỉ"),
        ],
        "ec_kicker": "★ CANXI TẢO BIỂN AQUAMIN F ★",
        "ec_brand": "BOJOMI VỊ VANI<br/>14 GÓI / HỘP",
        "ec_sub": "417,6mg Canxi Aquamin F • 779,4 IU D3 • 169,8µg K2 • Collagen",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "520.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "CTKM 25/11 – 30/11",
        "ec_promo_l2": "MUA 3 TẶNG 1 BOJOMI (520K)",
        "ec_cta": "▸ NHẮN “BOJOMI” NHẬN CÁCH PHA 60°C CHUẨN!",
    },
    {
        "vkey": "n02_v3_combo_be_1_tuoi_bieng_an",
        "slug": "av-n02-v3",
        "prefix": "v3",
        "look_img": "N02_LOOK3_KID1Y_CREAM_9x16.png",
        "overlay_main": "03_Warm_Window_Sun_Rays_9x16.mp4",
        "ov_opacity": "0.44",
        "bg_dark": "#052C36",
        "ec_bg": "linear-gradient(175deg, #04323D 0%, #0A6356 48%, #042B26 100%)",
        "card_bg": "linear-gradient(145deg, rgba(5,48,58,0.92) 0%, rgba(10,88,76,0.88) 100%)",
        "brand_chip": "BOJOMI × AV PROTEIN",
        "top_pill": "★ BÉ TỪ 1 TUỔI+ ★",
        "is_duo": True,
        "box_files": [("av01_protein_a.png", "AV PROTEIN • 350K"), ("av02_bojomi_b.png", "BOJOMI • 520K")],
        "big_hook": {
            "badge": "★ CHO BÉ TỪ 1 TUỔI TRỞ LÊN ★",
            "l1": "BÉ BIẾNG ĂN LƯỜI SỮA",
            "l2": "BỔ SUNG SAO ÊM BỤNG?",
            "c1": "#06365A", "c2": "#D91A26", "s1": 62, "s2": 62,
            "badge_bg": "linear-gradient(135deg, #06426B, #0D7564)",
        },
        "callouts": [
            ("BÍ QUYẾT MẸ HIỆN ĐẠI", "CHIA NHỎ 2 KHUNG GIỜ RIÊNG", "Không ép dồn 1 lần — Vị dịu nhẹ bé dễ hợp tác"),
            ("SÁNG • AV PROTEIN 20–40°C", "ĐẠM THỰC VẬT + LỢI KHUẨN B-3", "Êm bụng, dễ tiêu hóa, không gây nặng bụng con"),
            ("CHIỀU • BOJOMI ẤM 60°C", "CANXI AQUAMIN F + D3 + K2", "Hương Vani thơm béo — Chia lượng đúng độ tuổi"),
        ],
        "ec_kicker": "★ CHO BÉ TỪ 1 TUỔI TRỞ LÊN ★",
        "ec_brand": "BOJOMI +<br/>AV PROTEIN",
        "ec_sub": "Đạm thực vật + B-3 • Canxi Aquamin F + D3 + K2 MK-7",
        "ec_price_label": "BỘ ĐÔI 2 HỘP CHÍNH HÃNG",
        "ec_price": "870.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #064D33, #0F7B54)",
        "ec_promo_l1": "★ CHÍNH HÃNG DROPPII",
        "ec_promo_l2": "PROTEIN 350K + BOJOMI 520K",
        "ec_cta": "▸ NHẮN “BÉ 1 TUỔI” NHẬN BẢNG KHẨU PHẦN!",
    },
    {
        "vkey": "n02_v4_curcumilk_15h_em_bung",
        "slug": "av-n02-v4",
        "prefix": "v4",
        "look_img": "N02_LOOK4_CURCU_15H_9x16.png",
        "overlay_main": "06_Organic_Warm_Light_Leak_9x16.mp4",
        "ov_opacity": "0.42",
        "bg_dark": "#331A04",
        "ec_bg": "linear-gradient(175deg, #4A2204 0%, #8C4708 48%, #381802 100%)",
        "card_bg": "linear-gradient(145deg, rgba(72,34,4,0.92) 0%, rgba(132,68,8,0.88) 100%)",
        "brand_chip": "CURCUMILK PHYTO",
        "top_pill": "✦ BỮA PHỤ 15H ✦",
        "is_duo": False,
        "box_files": [("av04_curcumilk_b.png", "CURCUMILK • 650K")],
        "big_hook": {
            "badge": "✦ BỮA PHỤ 15H VĂN PHÒNG ✦",
            "l1": "SỮA NGHỆ ẤM BỤNG",
            "l2": "KHÔNG HỀ HĂNG NGHỆ!",
            "c1": "#5E2D00", "c2": "#D91A26", "s1": 68, "s2": 62,
            "badge_bg": "linear-gradient(135deg, #A85200, #DC7B06)",
        },
        "callouts": [
            ("VỊ NGŨ CỐC SỮA DỪA VANI", "THƠM BÉO DỊU NHẸ DỄ UỐNG", "Thay thế lành mạnh cho trà sữa nhiều đường 15h"),
            ("CÔNG NGHỆ PHYTOSOME Ý", "343,2MG CURCUMINOID / GÓI", "Hệ 3 lớp kết hợp Curcumin Phytosome nhập khẩu"),
            ("PHA NHANH 40–50°C", "1 GÓI + 150ML NƯỚC ẤM", "Nạp năng lượng êm bụng suốt buổi chiều làm việc"),
        ],
        "ec_kicker": "✦ CURCUMIN PHYTOSOME Ý ✦",
        "ec_brand": "CURCUMILK<br/>PHYTO (14 GÓI)",
        "ec_sub": "343,2mg Curcuminoid hệ 3 lớp • Ngũ cốc sữa dừa vị Vani",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "650.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "CTKM 25/11 – 30/11",
        "ec_promo_l2": "MUA 4 TẶNG 1 CURCUMILK (650K)",
        "ec_cta": "▸ NHẮN “SỮA NGHỆ” XEM BẢNG THÀNH PHẦN!",
    },
    {
        "vkey": "n02_v5_collamela_don_tet_480k",
        "slug": "av-n02-v5",
        "prefix": "v5",
        "look_img": "N02_LOOK5_COLLA_TET_9x16.png",
        "overlay_main": "04_Anamorphic_Gold_Rose_Flare_9x16.mp4",
        "ov_opacity": "0.44",
        "bg_dark": "#3A081E",
        "ec_bg": "linear-gradient(175deg, #540A2B 0%, #9E1952 48%, #3D061F 100%)",
        "card_bg": "linear-gradient(145deg, rgba(84,10,43,0.92) 0%, rgba(148,22,76,0.88) 100%)",
        "brand_chip": "COLLAMELA • ĐÓN TẾT",
        "top_pill": "★ 2.530MG COLLAGEN ★",
        "is_duo": False,
        "box_files": [("av03_collamela_b.png", "COLLAMELA • 920K")],
        "big_hook": {
            "badge": "★ 60 NGÀY ĐÓN TẾT RẠNG RỠ ★",
            "l1": "2.530MG COLLAGEN",
            "l2": "DA CĂNG MỊN KỊP TẾT!",
            "c1": "#6E0B35", "c2": "#D91A38", "s1": 66, "s2": 64,
            "badge_bg": "linear-gradient(135deg, #9C124B, #DB2A6F)",
        },
        "callouts": [
            ("VỊ ĐÀO THANH NGỌT", "PHA 100ML NƯỚC MÁT 10 GIÂY", "Hoàn toàn không tanh — Uống ngon mỗi ngày"),
            ("PHÂN TỬ SIÊU NHỎ", "2.530MG COLLAGEN TRIPEPTIDE", "Hỗ trợ cơ thể hấp thu nhanh từ bên trong"),
            ("BỘ 4 DƯỠNG CHẤT VÀNG", "HA + VITAMIN C + KẼM", "Nuôi dưỡng độ đàn hồi & sắc diện da tươi tắn"),
        ],
        "ec_kicker": "★ COLLAGEN TRIPEPTIDE VỊ ĐÀO ★",
        "ec_brand": "COLLAMELA<br/>HỘP 20 GÓI",
        "ec_sub": "2.530mg Collagen Tripeptide • 25,68mg HA • 87mg C • 3,9mg Kẽm",
        "ec_price_label": "GIÁ NIÊM YẾT DROPPII",
        "ec_price": "920.000đ",
        "ec_promo_bg": "linear-gradient(135deg, #E6222B, #A80A16)",
        "ec_promo_l1": "CTKM 25/11 – 30/11",
        "ec_promo_l2": "MUA 2 TẶNG 1 HỘP 10G (480K)",
        "ec_cta": "▸ NHẮN “COLLAMELA” CHỐT QUÀ 480K NGAY!",
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

    # Copy fonts, SFX, logo, look portrait, real IS-Net box(es)
    for fn in ["BeVietnamPro-SemiBold.ttf", "BeVietnamPro-Bold.ttf", "BeVietnamPro-ExtraBold.ttf", "Montserrat-Black.ttf"]:
        shutil.copy2(FONTS_DIR / fn, fnt_dir / fn)
    for fn in ["sfx_pop_clean.mp3", "sfx_whoosh_soft.mp3", "sfx_whoosh_cinematic.mp3", "sfx_sparkle_shine.mp3", "sfx_crystal_shimmer.mp3", "sfx_ping_glass.mp3", "sfx_notification_cta.mp3"]:
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

    # Copy VO wavs + unique BGM
    shutil.copy2(vo_data["bgm_path"], aud_dir / "bgm_unique.mp3")
    for s in segs:
        shutil.copy2(s["path"], aud_dir / f"{s['id']}.wav")

    # 5 segments: s0..s3 = main 4 shots; s4 = End-Card
    s0, s1, s2, s3, s4 = segs
    t1, t2, t3 = float(s0["shot_end_s"]), float(s1["shot_end_s"]), float(s2["shot_end_s"])
    end_start = float(s3["shot_end_s"])
    end_dur = round(total_dur - end_start, 2)

    shot_defs = [
        (f"{cfg['prefix']}_s01.mp4", "s01.mp4", 0.0, t1),
        (f"{cfg['prefix']}_s02.mp4", "s02.mp4", t1, round(t2 - t1, 2)),
        (f"{cfg['prefix']}_s03.mp4", "s03.mp4", t2, round(t3 - t2, 2)),
        (f"{cfg['prefix']}_s04.mp4", "s04.mp4", t3, round(end_start - t3, 2)),
    ]
    for raw_fn, out_fn, st, du in shot_defs:
        prep_clip_to_dur(CLIPS_DIR / raw_fn, vid_dir / out_fn, du)

    # Prep real 9:16 Cinema Screen Overlays
    prep_loop_overlay(OV_DIR / cfg["overlay_main"], vid_dir / "overlay_cinema.mp4", total_dur)
    prep_loop_overlay(OV_DIR / "05_Soft_Pearl_Sparkles_Bling_9x16.mp4", vid_dir / "overlay_bling.mp4", total_dur)

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

    # Audio tags
    bgm_auto = build_ducking(segs, total_dur)
    vo_tags = [
        f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
        f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{5 if i%2==0 else 6}" '
        f'data-volume="1.32" data-fade-in="0.04" data-fade-out="0.06" data-fx-chain="{VO_FX}"></audio>'
        for i, s in enumerate(segs)
    ]
    sfx = [
        ("sfx-01", "sfx_pop_clean.mp3", 0.10, 0.55, 9, 0.24),
        ("sfx-02", "sfx_whoosh_soft.mp3", round(t1 - 0.11, 2), 0.55, 9, 0.22),
        ("sfx-03", "sfx_whoosh_cinematic.mp3", round(t2 - 0.12, 2), 0.90, 9, 0.28),
        ("sfx-04", "sfx_sparkle_shine.mp3", round(t2 + 0.08, 2), 1.65, 10, 0.26),
        ("sfx-05", "sfx_ping_glass.mp3", round(t3 + 0.08, 2), 0.85, 11, 0.24),
        ("sfx-06", "sfx_whoosh_cinematic.mp3", round(end_start - 0.12, 2), 0.90, 9, 0.28),
        ("sfx-07", "sfx_sparkle_shine.mp3", round(end_start + 0.16, 2), 1.65, 10, 0.28),
        ("sfx-08", "sfx_notification_cta.mp3", round(end_start + 1.35, 2), 2.10, 11, 0.22),
    ]
    sfx_tags = [
        f'      <audio id="{sid}" class="clip" src="assets/audio/{fn}" data-start="{st}" '
        f'data-duration="{du}" data-track-index="{tr}" data-volume="{vol}" data-fade-out="0.16"></audio>'
        for sid, fn, st, du, tr, vol in sfx if (aud_dir / fn).exists()
    ]

    # index.html
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
      .fx-host {{ position: absolute; inset: 0; z-index: 8; pointer-events: none; mix-blend-mode: screen; }}
      .overlay-host {{ position: absolute; inset: 0; z-index: 14; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="{end_start}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene-host" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{end_start}" data-duration="{end_dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="cinema-fx" class="fx-host" data-composition-id="cinema-fx" data-composition-src="compositions/cinema-fx.html" data-start="0" data-duration="{total_dur}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

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

    # 1. main-video.html
    shot_els, shot_anims = [], []
    for idx, (_, out_fn, st, du) in enumerate(shot_defs):
        rid = f"rig{idx+1}"
        tr = 1 if idx % 2 == 0 else 2
        shot_els.append(
            f'    <div id="{rid}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>\n'
            f'      <video {COLOR_GRADE_ATTR} id="v{idx+1}" class="clip bg-video" src="assets/videos/{out_fn}" '
            f'data-start="{st}" data-duration="{du}" data-media-start="0.08" data-hf-media-start-basis="local" '
            f'data-track-index="{tr}" muted playsinline></video>\n'
            f'    </div>'
        )
        s0_sc, s1_sc = (1.00, 1.05) if idx % 2 == 0 else (1.04, 1.00)
        shot_anims.append(f'    tl.fromTo("#{rid}", {{ scale: {s0_sc} }}, {{ scale: {s1_sc}, duration: {du}, ease: "none", immediateRender: false }}, {st});')

    (comp_dir / "main-video.html").write_text(f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: {cfg["bg_dark"]}; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 50%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .sun-flare {{
      position: absolute; inset: 0; pointer-events: none; z-index: 12; opacity: 0;
      background: radial-gradient(circle at 50% 38%, rgba(255,248,215,0.92) 0%, rgba(252,226,136,0.52) 40%, rgba(255,255,255,0) 76%);
      mix-blend-mode: screen;
    }}
  </style>
  <div id="root" data-composition-id="main-video" data-width="1080" data-height="1920" data-start="0" data-duration="{end_start}">
{chr(10).join(shot_els)}
    <div id="fl1" class="sun-flare" data-layout-ignore></div>
    <div id="fl2" class="sun-flare" data-layout-ignore></div>
    <div id="fl3" class="sun-flare" data-layout-ignore></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(shot_anims)}
    tl.fromTo("#fl1", {{ opacity: 0 }}, {{ opacity: 0.82, duration: 0.14, immediateRender: false }}, {round(t1 - 0.10, 2)})
      .to("#fl1", {{ opacity: 0, duration: 0.24 }}, {round(t1 + 0.04, 2)});
    tl.fromTo("#fl2", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.14, immediateRender: false }}, {round(t2 - 0.10, 2)})
      .to("#fl2", {{ opacity: 0, duration: 0.24 }}, {round(t2 + 0.04, 2)});
    tl.fromTo("#fl3", {{ opacity: 0 }}, {{ opacity: 0.80, duration: 0.14, immediateRender: false }}, {round(t3 - 0.10, 2)})
      .to("#fl3", {{ opacity: 0, duration: 0.24 }}, {round(t3 + 0.04, 2)});
    window.__timelines["main-video"] = tl;
  </script>
</template>
""", encoding="utf-8")

    # 2. cinema-fx.html
    (comp_dir / "cinema-fx.html").write_text(f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; pointer-events: none; }}
    .ov-vid {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; mix-blend-mode: screen; }}
    #ov-main {{ opacity: {cfg["ov_opacity"]}; }}
    #ov-bling {{ opacity: 0.30; }}
    .warm-sun-corner {{
      position: absolute; top: -120px; right: -120px; width: 760px; height: 760px; border-radius: 50%;
      background: radial-gradient(circle, rgba(255,244,196,0.42) 0%, rgba(255,222,128,0.16) 42%, rgba(255,255,255,0) 74%);
      mix-blend-mode: screen;
    }}
  </style>
  <div id="root" data-composition-id="cinema-fx" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <video id="ov-main" class="clip ov-vid" src="assets/videos/overlay_cinema.mp4" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="1" muted playsinline data-layout-ignore></video>
    <video id="ov-bling" class="clip ov-vid" src="assets/videos/overlay_bling.mp4" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="2" muted playsinline data-layout-ignore></video>
    <div id="sun-glow" class="warm-sun-corner" data-layout-ignore></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#sun-glow", {{ opacity: 0.45, scale: 0.94 }}, {{ opacity: 0.82, scale: 1.08, duration: {round(total_dur/2.0, 2)}, ease: "sine.inOut" }}, 0.0)
      .to("#sun-glow", {{ opacity: 0.50, scale: 0.96, duration: {round(total_dur/2.0, 2)}, ease: "sine.inOut" }}, {round(total_dur/2.0, 2)});
    window.__timelines["cinema-fx"] = tl;
  </script>
</template>
""", encoding="utf-8")

    # 3. safe-overlays.html
    hk = cfg["big_hook"]
    hk_end = round(t1 - 0.14, 2)
    callouts = [
        ("c2", round(t1 + 0.16, 2), round(t2 - t1 - 0.36, 2), *cfg["callouts"][0]),
        ("c3", round(t2 + 0.16, 2), round(t3 - t2 - 0.36, 2), *cfg["callouts"][1]),
        ("c4", round(t3 + 0.16, 2), round(end_start - t3 - 0.36, 2), *cfg["callouts"][2]),
    ]
    c_divs, c_anims = [], []
    for cid, st, du, tag, big, sub in callouts:
        sh_id = f"sh-{cid}"
        c_divs.append(f"""
      <div id="{cid}" class="safe-card" data-layout-ignore>
        <div id="{sh_id}" class="card-sheen"></div>
        <div class="sc-tag">{tag}</div>
        <div class="sc-big">{big}</div>
        <div class="sc-sub">{sub}</div>
      </div>""")
        c_anims.append(
            f'    tl.fromTo("#{cid}", {{ opacity: 0, y: 32, scale: 0.92, filter: "blur(14px)" }}, '
            f'{{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.25)", immediateRender: false }}, {st})\n'
            f'      .fromTo("#{sh_id}", {{ x: -240, opacity: 0.0 }}, {{ x: 960, opacity: 0.65, duration: 0.95, ease: "power2.inOut", immediateRender: false }}, {round(st + 0.35, 2)})\n'
            f'      .to("#{cid}", {{ opacity: 0, y: -12, filter: "blur(10px)", duration: 0.22, ease: "power2.in" }}, {round(st + du - 0.22, 2)});'
        )

    # Real IS-Net floating product box(es) on scene 3 (c3) for 100% accurate label visibility!
    if cfg["is_duo"]:
        float_html = f"""    <div id="prod-real" class="prod-float" data-layout-ignore>
      <img class="pf-box" src="assets/images/{cfg['box_files'][0][0]}" alt="Box 1" />
      <div class="pf-plus">+</div>
      <img class="pf-box" src="assets/images/{cfg['box_files'][1][0]}" alt="Box 2" />
    </div>"""
    else:
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
      background: linear-gradient(180deg, rgba(255,255,255,0.44) 0%, rgba(255,255,255,0.84) 100%);
      backdrop-filter: blur(8px);
      border: 4px solid rgba(255,255,255,0.92); border-radius: 32px;
      box-shadow: 0 20px 44px rgba(0,0,0,0.34); z-index: 20;
    }}
    .bh-badge {{
      background: {hk["badge_bg"]}; color: #FFF8D6; border: 3px solid #FFE288;
      border-radius: 999px; padding: 10px 26px; font-weight: 800; font-size: 26px;
      letter-spacing: 0.5px; box-shadow: 0 8px 20px rgba(0,0,0,0.30); margin-bottom: 14px;
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
      position: absolute; left: 56px; bottom: 686px; width: 640px; height: 340px;
      display: flex; align-items: flex-end; justify-content: flex-start; gap: 18px;
      opacity: 0; z-index: 16;
    }}
    .pf-box {{ height: 310px; width: auto; filter: drop-shadow(0 18px 28px rgba(0,0,0,0.48)) drop-shadow(0 0 22px rgba(255,240,180,0.55)); }}
    .pf-box-single {{ height: 330px; width: auto; filter: drop-shadow(0 18px 28px rgba(0,0,0,0.48)) drop-shadow(0 0 24px rgba(255,240,180,0.58)); }}
    .pf-plus {{
      width: 48px; height: 48px; border-radius: 50%; margin-bottom: 118px; flex-shrink: 0;
      background: linear-gradient(145deg, #FCE078, #D98E10); border: 3px solid #FFFFFF;
      color: #053623; font-weight: 900; font-size: 34px; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 8px 18px rgba(0,0,0,0.40);
    }}
    .safe-card {{
      position: absolute; left: 56px; bottom: 394px; width: 814px; overflow: hidden;
      background: {cfg["card_bg"]};
      border: 3.5px solid #F4CF68; border-left: 11px solid #FFE480;
      border-radius: 28px; padding: 24px 28px;
      box-shadow: 0 18px 38px rgba(0,0,0,0.44); opacity: 0;
    }}
    .card-sheen {{
      position: absolute; top: 0; bottom: 0; width: 170px; pointer-events: none;
      background: linear-gradient(105deg, rgba(255,255,255,0) 0%, rgba(255,250,210,0.34) 50%, rgba(255,255,255,0) 100%);
      transform: skewX(-20deg); opacity: 0;
    }}
    .sc-tag {{ font-weight: 800; font-size: 25px; color: #FFE888; letter-spacing: 0.7px; text-transform: uppercase; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.40); }}
    .sc-big {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 52px; line-height: 1.12; color: #FFFFFF; text-shadow: 0 4px 12px rgba(0,0,0,0.46); }}
    .sc-sub {{ font-weight: 700; font-size: 29px; color: #F2FFF8; margin-top: 10px; line-height: 1.26; text-shadow: 0 2px 8px rgba(0,0,0,0.35); }}
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
    tl.fromTo("#big-hook", {{ scale: 0.92, y: 10 }}, {{ scale: 1.0, y: 0, duration: 0.28, ease: "back.out(1.45)" }}, 0.0)
      .to("#big-hook", {{ opacity: 0, y: -18, filter: "blur(12px)", duration: 0.26, ease: "power2.in" }}, {round(hk_end - 0.26, 2)});
    tl.fromTo("#top-brand", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power2.out", immediateRender: false }}, 0.12)
      .to("#top-brand", {{ opacity: 0, duration: 0.25 }}, {round(end_start - 0.26, 2)});
    tl.fromTo("#top-pill", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1.0, duration: 0.32, ease: "back.out(1.5)", immediateRender: false }}, 0.20)
      .to("#top-pill", {{ opacity: 0, duration: 0.25 }}, {round(end_start - 0.26, 2)});
    tl.fromTo("#prod-real", {{ opacity: 0, y: 38, scale: 0.88 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.38, ease: "back.out(1.35)", immediateRender: false }}, {round(t2 + 0.18, 2)})
      .to("#prod-real", {{ opacity: 0, y: -16, filter: "blur(8px)", duration: 0.26, ease: "power2.in" }}, {round(t3 - 0.28, 2)});
{chr(10).join(c_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
""", encoding="utf-8")

    # 4. endcard.html — 100% Real IS-Net Box(es) + Exact 25/11–30/11 Deal Card + Strict Safe Zone
    if cfg["is_duo"]:
        ec_boxes_html = f"""    <div id="ec-b" class="ec-boxes" data-layout-ignore>
      <div id="eb1" class="b-col">
        <div class="b-tag">{cfg['box_files'][0][1]}</div>
        <img class="b-pro" src="assets/images/{cfg['box_files'][0][0]}" alt="Box 1" />
      </div>
      <div id="eplus" class="b-plus">+</div>
      <div id="eb2" class="b-col">
        <div class="b-tag">{cfg['box_files'][1][1]}</div>
        <img class="b-boj" src="assets/images/{cfg['box_files'][1][0]}" alt="Box 2" />
      </div>
    </div>"""
        ec_box_anim = """      .fromTo("#eb1",  { opacity: 0, y: 36, scale: 0.90 }, { opacity: 1, y: 0, scale: 1.0, duration: 0.40, ease: "back.out(1.3)", immediateRender: false }, 0.32)
      .fromTo("#eplus",{ opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1.0, duration: 0.28, ease: "back.out(1.7)", immediateRender: false }, 0.44)
      .fromTo("#eb2",  { opacity: 0, y: 36, scale: 0.90 }, { opacity: 1, y: 0, scale: 1.0, duration: 0.40, ease: "back.out(1.3)", immediateRender: false }, 0.52)"""
    else:
        ec_boxes_html = f"""    <div id="ec-b" class="ec-boxes-single" data-layout-ignore>
      <div id="eb1" class="b-col">
        <div class="b-tag">{cfg['box_files'][0][1]}</div>
        <img class="b-single" src="assets/images/{cfg['box_files'][0][0]}" alt="Box" />
      </div>
    </div>"""
        ec_box_anim = """      .fromTo("#eb1",  { opacity: 0, y: 36, scale: 0.90 }, { opacity: 1, y: 0, scale: 1.0, duration: 0.44, ease: "back.out(1.35)", immediateRender: false }, 0.32)"""

    (comp_dir / "endcard.html").write_text(f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: {cfg["ec_bg"]}; font-family: 'BeVN', sans-serif; }}
    .ec-model {{
      position: absolute; top: 256px; right: 58px; width: 404px; height: 590px;
      border-radius: 30px; overflow: hidden; border: 3.5px solid rgba(244,204,100,0.92);
      box-shadow: 0 20px 44px rgba(0,0,0,0.40);
    }}
    .ec-model img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 15%; display: block; }}
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
    .ec-boxes {{ position: absolute; left: 58px; top: 696px; width: 720px; height: 396px; display: flex; align-items: flex-end; gap: 16px; }}
    .ec-boxes-single {{ position: absolute; left: 106px; top: 684px; width: 420px; height: 412px; display: flex; align-items: flex-end; justify-content: center; }}
    .b-col {{ display: flex; flex-direction: column; align-items: center; }}
    .b-tag {{ background: rgba(4,48,32,0.94); color: #FFF8DC; border: 2.5px solid #F4CC62; border-radius: 999px; padding: 5px 16px; font-weight: 800; font-size: 19px; margin-bottom: 6px; white-space: nowrap; }}
    .b-pro {{ height: 332px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .b-boj {{ height: 338px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .b-single {{ height: 360px; width: auto; filter: drop-shadow(0 20px 30px rgba(0,0,0,0.48)); }}
    .b-plus {{
      width: 54px; height: 54px; border-radius: 50%; flex-shrink: 0; margin-bottom: 136px;
      background: linear-gradient(145deg, #FCE078, #D98E10); border: 3.5px solid #FFFFFF;
      color: #053623; font-weight: 900; font-size: 40px; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 10px 20px rgba(0,0,0,0.38);
    }}
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
    .ep-1 {{ font-weight: 800; font-size: 18px; color: #FFF3B0; }}
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
    <div id="ec-m" class="ec-model" data-layout-ignore><img src="assets/images/hero_look.png" alt="Model" /></div>
    <div id="ec-l" class="ec-logo" data-layout-ignore><img src="assets/images/logo_an_vuong_orig.png" alt="Logo" /></div>
    <div id="ec-t" class="ec-title" data-layout-ignore>
      <div class="ec-kicker">{cfg["ec_kicker"]}</div>
      <div class="ec-brand">{cfg["ec_brand"]}</div>
      <div class="ec-sub">{cfg["ec_sub"]}</div>
    </div>
{ec_boxes_html}
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
    tl.fromTo("#ec-m", {{ opacity: 0, scale: 1.06, x: 24 }}, {{ opacity: 1, scale: 1.0, x: 0, duration: 0.45, ease: "power3.out", immediateRender: false }}, 0.05)
      .fromTo("#ec-l", {{ opacity: 0, y: -18 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out", immediateRender: false }}, 0.12)
      .fromTo("#ec-t", {{ opacity: 0, x: -24, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.38, ease: "power3.out", immediateRender: false }}, 0.22)
{ec_box_anim}
      .fromTo("#ec-d", {{ opacity: 0, y: 30, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.40, ease: "power3.out", immediateRender: false }}, 0.66)
      .fromTo("#ec-g", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.30, immediateRender: false }}, 0.88)
      .to("#ec-m", {{ scale: 1.03, duration: {round(end_dur - 0.6, 2)}, ease: "none" }}, 0.60);
    window.__timelines["endcard"] = tl;
  </script>
</template>
""", encoding="utf-8")

    print(f"[BUILT N02 HF] {cfg['vkey']} ({total_dur:.2f}s <= 60s!, endcard={end_start:.2f}..{total_dur:.2f}s)", flush=True)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for i, c in enumerate(CFGS, 1):
        if arg in ("all", f"v{i}", c["vkey"]):
            build_one(c)


if __name__ == "__main__":
    main()
