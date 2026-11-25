"""
Dựng TRỌN BỘ 5 BÀI ĐĂNG THIẾT KẾ BỐI CẢNH TP. NHA TRANG (24/11/2026) — BẮT MẮT, TEXT CỰC TO (.JPG 1600x1600 sRGB, KHÔNG PSD):
1. Post 01: Bojomi Chạy Bộ Đường Biển Trần Phú Nha Trang — 417,6mg Canxi Tảo Biển + D3 + K2 + Mua 3 Tặng 1 (520K)
2. Post 02: Combo Chiều Cao Bé Từ 1 Tuổi+ (Bojomi + AV Protein) — Ban công view biển Nha Trang — 870.000đ + Quà tới 520K
3. Post 03: Bí Kíp Pha Chuẩn 2 Nhiệt Độ (AV Protein 20–40°C • Bojomi 60°C) — Bếp sáng view vịnh Nha Trang
4. Post 04: AV Protein 1.632mg L-Leucine Giữ Cơ Không Đầy Hơi — Pilates ban công biển Nha Trang — 350.000đ + Mua 5 Tặng 1
5. Post 05: Combo 4 Sản Phẩm Sinh Nhật Droppii Tặng Collamela 920K — Đầm lụa hoàng hôn biển Nha Trang — 2.440.000đ
100% Hộp thật tách nền IS-Net (0% sai chữ hộp AI), 0% ký tự emoji lỗi ô vuông!
"""
import os, base64, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageCms

WORK_DIR = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Bo_5_Bai_Thiet_Ke_Nha_Trang"
ASSETS_DIR = os.path.join(WORK_DIR, "01_ChatGPT_Assets")
OUT_DIR = os.path.join(WORK_DIR, "02_Final_JPG")
TMP_DIR = os.path.join(WORK_DIR, "tmp_html")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

CUTOUT_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG"
LOGO_ORIG = os.path.join(CUTOUT_DIR, "logo_an_vuong_orig.png")
FONTS_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_EXE):
    EDGE_EXE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

SRGB_BYTES = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
LEGAL_TPBS = "Thực phẩm bổ sung. Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh."


def file_to_data_uri(p: str) -> str:
    ext = os.path.splitext(p)[1].lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "ttf": "font/ttf"}.get(ext, "application/octet-stream")
    with open(p, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode('ascii')}"


def font_css() -> str:
    fonts = [
        ("BeVNExtra", "BeVietnamPro-ExtraBold.ttf"),
        ("BeVNBold", "BeVietnamPro-Bold.ttf"),
        ("BeVNSemi", "BeVietnamPro-SemiBold.ttf"),
        ("MontBlack", "Montserrat-Black.ttf"),
    ]
    return "\n".join(
        f"@font-face {{ font-family: '{fam}'; src: url('{file_to_data_uri(os.path.join(FONTS_DIR, fn))}') format('truetype'); font-weight: 100 900; }}"
        for fam, fn in fonts
    )


def place_box(canvas: Image.Image, box_path: str, cx: int, bottom_y: int, target_h: int):
    box = Image.open(box_path).convert("RGBA")
    bb = box.getbbox()
    if bb:
        box = box.crop(bb)
    sc = target_h / box.height
    nw, nh = int(round(box.width * sc)), int(round(box.height * sc))
    box_r = ImageEnhance.Sharpness(box.resize((nw, nh), Image.Resampling.LANCZOS)).enhance(1.14)
    x0, y0 = cx - nw // 2, bottom_y - nh

    refl_h = int(nh * 0.20)
    refl = box_r.transpose(Image.Transpose.FLIP_TOP_BOTTOM).crop((0, 0, nw, refl_h))
    grad = np.linspace(46, 0, refl_h, dtype=np.float32)[:, None]
    ra = np.array(refl, dtype=np.float32)
    ra[:, :, 3] = np.clip(ra[:, :, 3] * (grad / 255.0), 0, 255)
    canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(2.0)), (x0, bottom_y - 6))

    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse([x0 - 30, bottom_y - 20, x0 + nw + 16, bottom_y + 24], fill=(18, 28, 24, 85))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    d2 = ImageDraw.Draw(sh)
    d2.ellipse([x0 + 6, bottom_y - 10, x0 + nw - 6, bottom_y + 10], fill=(10, 18, 14, 130))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(box_r, (x0, y0))


P_PRO = os.path.join(CUTOUT_DIR, "av01_protein_a.png")
P_BOJ = os.path.join(CUTOUT_DIR, "av02_bojomi_b.png")
P_COL = os.path.join(CUTOUT_DIR, "av03_collamela_b.png")
P_CUR = os.path.join(CUTOUT_DIR, "av04_curcumilk_b.png")

POSTS = [
    {
        "id": "NT_01",
        "filename": "261124 AVPM Thiet Ke 05 - Bojomi Chay Bo Bien Nha Trang (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "NT_DES1_BOJOMI_BEACH_RUN.png"),
        "boxes": [(P_BOJ, 236, 1442, 555)],
        "price_left": 468,
        "wash_rgb": "244,252,248",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ DÂN CHẠY BỘ SÁNG • NHA TRANG ★",
        "h_line1": "CHẠY BỀN MỖI SÁNG",
        "h_line2": "KHUNG XƯƠNG KHỎE!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #9E0815 100%)",
        "h1_size": 76, "h2_size": 74,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "417,6mg CANXI",
        "hero_sub": "TẢO BIỂN AQUAMIN F • D3 • K2 MK-7 • COLLAGEN",
        "chips": [
            ("779,4 IU", "Vitamin D3"),
            ("169,8 µg", "K2 MK-7 chuẩn"),
            ("201,4mg", "Collagen dẻo dai"),
        ],
        "prod_name": "BOJOMI VỊ VANI (14 GÓI)",
        "price": "520.000đ",
        "promo_l1": "★ CTKM DROPPII 25/11 – 30/11",
        "promo_l2": "MUA 3 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “BOJOMI” xem nhãn & cách pha 60°C sau chạy • Hotline: 0867 399 268",
    },
    {
        "id": "NT_02",
        "filename": "261124 AVPM Thiet Ke 06 - Combo Chieu Cao Be Tu 1 Tuoi (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "NT_DES2_COMBO_KID1Y_BALCONY.png"),
        "boxes": [(P_PRO, 166, 1434, 385), (P_BOJ, 432, 1446, 398)],
        "price_left": 588,
        "price_w": 436,
        "wash_rgb": "246,251,255",
        "pill_bg": "linear-gradient(135deg, #06426B, #0D7564)",
        "pill_txt": "★ DÀNH CHO BÉ TỪ 1 TUỔI TRỞ LÊN ★",
        "h_line1": "CHIỀU CAO CỦA BÉ",
        "h_line2": "ĐẠM + CANXI CHUẨN!",
        "h1_color": "#06365A",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #9E0815 100%)",
        "h1_size": 84, "h2_size": 78,
        "hero_badge_bg": "linear-gradient(135deg, #07446E 0%, #0E7866 100%)",
        "hero_num": "BOJOMI + AV PROTEIN",
        "hero_sub": "ĐẠM THỰC VẬT ÊM BỤNG + CANXI AQUAMIN F",
        "chips": [
            ("22,05g", "Đạm + B-3 êm bụng"),
            ("417,6mg", "Canxi + D3 + K2"),
            ("1 Tuổi+", "Chia theo độ tuổi"),
        ],
        "prod_name": "TRỌN BỘ ĐÔI 2 HỘP",
        "price": "870.000đ",
        "promo_bg": "linear-gradient(135deg, #064D33 0%, #0E7A54 100%)",
        "promo_l1": "★ CHÍNH HÃNG DROPPII",
        "promo_l2": "AV PROTEIN 350K + BOJOMI 520K",
        "ftr_bg": "linear-gradient(90deg, #04283D 0%, #095C52 50%, #04283D 100%)",
        "ftr_cta": "▸ Nhắn “BÉ 1 TUỔI” nhận bảng chia khẩu phần theo độ tuổi • Hotline: 0867 399 268",
    },
    {
        "id": "NT_03",
        "filename": "261124 AVPM Thiet Ke 07 - Pha Chuan 2 Nhiet Do Bojomi AV Protein (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "NT_DES3_2TEMP_KITCHEN_SEA.png"),
        "boxes": [(P_PRO, 166, 1434, 385), (P_BOJ, 432, 1446, 398)],
        "price_left": 588,
        "price_w": 436,
        "wash_rgb": "255,252,240",
        "pill_bg": "linear-gradient(135deg, #C76800, #E58C08)",
        "pill_txt": "✦ LƯU Ý QUAN TRỌNG CHO MẸ THÔNG THÁI ✦",
        "h_line1": "ĐỪNG PHA CHUNG!",
        "h_line2": "CHUẨN 2 NHIỆT ĐỘ",
        "h1_color": "#053F2A",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #A30815 100%)",
        "h1_size": 84, "h2_size": 84,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "20–40°C  |  60°C",
        "hero_sub": "SÁNG AV PROTEIN MÁT • CHIỀU BOJOMI ẤM",
        "chips": [
            ("20–40°C", "Giữ lợi khuẩn B-3"),
            ("60°C Ấm", "Tan mịn vị Vani"),
            ("30 Giây", "Êm bụng dễ hấp thu"),
        ],
        "prod_name": "COMBO 2 HỘP CHÍNH HÃNG",
        "price": "870.000đ",
        "promo_bg": "linear-gradient(135deg, #064D33 0%, #0E7A54 100%)",
        "promo_l1": "★ ĐÚNG GIÁ NIÊM YẾT DROPPII",
        "promo_l2": "AV PROTEIN 350K + BOJOMI 520K",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “CHIỀU CAO” nhận lịch pha chuẩn 2 khung giờ • Hotline: 0867 399 268",
    },
    {
        "id": "NT_04",
        "filename": "261124 AVPM Thiet Ke 08 - AV Protein 1632mg Leucine Giu Dang (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "NT_DES4_PROTEIN_YOGA_BAY.png"),
        "boxes": [(P_PRO, 236, 1442, 555)],
        "price_left": 468,
        "wash_rgb": "244,251,255",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ TẬP ĐỀU GIỮ DÁNG • KHÔNG ĐẦY HƠI ★",
        "h_line1": "GIỮ CƠ SĂN CHẮC",
        "h_line2": "NHẸ BỤNG MỖI NGÀY",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #0B469E 0%, #1567D8 100%)",
        "h1_size": 84, "h2_size": 76,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "1.632mg LEUCINE",
        "hero_sub": "22,05G ĐẠM THỰC VẬT + INULIN + B-3 / 2 GÓI",
        "chips": [
            ("22,05g", "Đạm đậu & gạo"),
            ("17.500đ", "Chỉ 1 ly sáng"),
            ("20–40°C", "Pha mát 30 giây"),
        ],
        "prod_name": "AV PROTEIN (20 GÓI)",
        "price": "350.000đ",
        "promo_l1": "★ CTKM DROPPII 25/11 – 30/11",
        "promo_l2": "MUA 5 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “ĐẠM SẠCH” nhận thực đơn giữ dáng nhẹ bụng • Hotline: 0867 399 268",
    },
    {
        "id": "NT_05",
        "filename": "261124 AVPM Thiet Ke 09 - Combo 4 San Pham Tang Collamela 920K (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "NT_DES5_COMBO4SP_SUNSET_LOUNGE.png"),
        "boxes": [
            (P_PRO, 136, 1230, 280),
            (P_BOJ, 342, 1230, 285),
            (P_CUR, 162, 1452, 280),
            (P_COL, 382, 1452, 305),
        ],
        "price_left": 528,
        "price_w": 446,
        "wash_rgb": "255,247,242",
        "pill_bg": "linear-gradient(135deg, #073882, #1562DF)",
        "pill_txt": "★ SINH NHẬT DROPPII 8 TUỔI • 25/11 – 30/11 ★",
        "h_line1": "COMBO 4 SẢN PHẨM",
        "h_line2": "TẶNG QUÀ 920K!",
        "h1_color": "#073882",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #9E0815 100%)",
        "h1_size": 76, "h2_size": 98,
        "hero_badge_bg": "linear-gradient(135deg, #A3144F 0%, #DF2D72 100%)",
        "hero_num": "TẶNG 1 COLLAMELA",
        "hero_sub": "NGUYÊN HỘP 20 GÓI TRỊ GIÁ 920.000Đ!",
        "chips": [
            ("Đạm Sạch", "AV Protein 350K"),
            ("Xương Khớp", "Bojomi 520K"),
            ("Êm Bụng/Da", "Curcumilk & Collamela"),
        ],
        "prod_name": "TRỌN COMBO 4 SẢN PHẨM",
        "price": "2.440.000đ",
        "promo_l1": "★ TIẾT KIỆM NGAY 920.000Đ",
        "promo_l2": "CHỌN ĐÚNG MÃ COMBO DROPPII",
        "ftr_bg": "linear-gradient(90deg, #052B66 0%, #0D50B0 50%, #052B66 100%)",
        "ftr_cta": "▸ Nhắn “COMBO 4 SP” nhận hướng dẫn chọn mã hiện quà 0đ • Hotline: 0867 399 268",
    },
]


def build_html(spec: dict, logo_uri: str, fcss: str) -> str:
    chips_html = "".join(
        f'<div class="chip"><div class="ch-v">{v}</div><div class="ch-k">{k}</div></div>'
        for v, k in spec["chips"]
    )
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<style>
{fcss}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1600px; height: 1600px; overflow: hidden; background: transparent;
  position: relative; font-family: 'BeVNBold', sans-serif; -webkit-font-smoothing: antialiased;
}}
.left-wash {{
  position: absolute; inset: 0;
  background: linear-gradient(94deg, rgba({spec["wash_rgb"]},0.95) 0%, rgba({spec["wash_rgb"]},0.85) 42%, rgba({spec["wash_rgb"]},0.0) 60%);
}}
.top-row {{
  position: absolute; top: 38px; left: 48px; display: flex; align-items: center; gap: 16px;
}}
.logo-box {{
  background: rgba(255,255,255,0.97); border: 3px solid #E2B345; border-radius: 20px;
  padding: 8px 18px; height: 82px; display: flex; align-items: center;
  box-shadow: 0 10px 24px rgba(0,0,0,0.12);
}}
.logo-box img {{ height: 64px; width: auto; display: block; }}
.top-pill {{
  background: {spec["pill_bg"]}; color: #FFF8D6; border: 2.5px solid #FFE285;
  border-radius: 999px; padding: 13px 26px; font-family: 'BeVNExtra', sans-serif;
  font-size: 22px; letter-spacing: 0.4px; white-space: nowrap;
  box-shadow: 0 10px 22px rgba(0,0,0,0.18);
}}
.big-head {{ position: absolute; top: 140px; left: 48px; width: 960px; display: flex; flex-direction: column; align-items: flex-start; }}
.bh-1 {{
  display: inline-block;
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: {spec["h1_size"]}px;
  line-height: 1.08; padding-top: 8px; letter-spacing: -1.5px; color: {spec["h1_color"]};
  -webkit-text-stroke: 3px rgba(255,255,255,0.88); paint-order: stroke fill;
  filter: drop-shadow(0 6px 12px rgba(0,0,0,0.12)); white-space: nowrap;
}}
.bh-2 {{
  display: inline-block;
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: {spec["h2_size"]}px;
  line-height: 1.10; padding-top: 6px; padding-right: 12px; letter-spacing: -1.5px;
  background: {spec["h2_grad"]}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 0 #FFFFFF) drop-shadow(0 8px 14px rgba(0,0,0,0.14)); white-space: nowrap;
}}
.hero-stat {{
  position: absolute; top: 382px; left: 48px; width: 730px;
  background: {spec["hero_badge_bg"]}; border: 4px solid #FFE07D;
  border-radius: 28px; padding: 18px 26px; box-shadow: 0 16px 32px rgba(0,0,0,0.24);
}}
.hs-num {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 54px; line-height: 1.05;
  color: #FFF7C2; letter-spacing: -1px; text-shadow: 0 4px 12px rgba(0,0,0,0.32); white-space: nowrap;
}}
.hs-sub {{
  font-family: 'BeVNExtra', sans-serif; font-size: 22px; color: #FFFFFF;
  letter-spacing: 0.3px; margin-top: 6px; white-space: nowrap;
}}
.chips-row {{
  position: absolute; top: 546px; left: 48px; width: 730px;
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;
}}
.chip {{
  background: rgba(255,255,255,0.96); border: 3px solid #E2B64D; border-radius: 22px;
  padding: 14px 12px; text-align: center; box-shadow: 0 10px 22px rgba(0,0,0,0.12);
}}
.ch-v {{ font-family: 'BeVNExtra', sans-serif; font-size: 34px; color: #064D33; line-height: 1.08; white-space: nowrap; }}
.ch-k {{ font-family: 'BeVNBold', sans-serif; font-size: 19px; color: #243830; margin-top: 4px; line-height: 1.18; }}

.price-card {{
  position: absolute; top: 1094px; left: {spec["price_left"]}px; width: {spec.get("price_w", 454)}px;
  background: linear-gradient(155deg, rgba(255,255,255,0.98) 0%, rgba(255,248,228,0.98) 100%);
  border: 4px solid #E5B23E; border-radius: 30px; padding: 18px 20px;
  box-shadow: 0 20px 42px rgba(0,0,0,0.26); text-align: center;
}}
.pc-name {{ font-family: 'BeVNExtra', sans-serif; font-size: 22px; color: #064B32; letter-spacing: 0.3px; }}
.pc-price {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 68px; line-height: 1.04;
  color: #0B40A8; letter-spacing: -2px; margin: 4px 0 10px; white-space: nowrap;
}}
.pc-promo {{
  background: {spec.get("promo_bg", "linear-gradient(135deg, #EB202B 0%, #A60814 100%)")};
  border: 3px solid #FFE285; border-radius: 18px; padding: 10px 12px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.22);
}}
.pp-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 18px; color: #FFF3B0; line-height: 1.15; }}
.pp-2 {{ font-family: 'BeVNExtra', sans-serif; font-size: 20px; color: #FFFFFF; line-height: 1.15; margin-top: 2px; white-space: nowrap; }}

.ftr {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 118px;
  background: {spec["ftr_bg"]}; border-top: 4px solid #E8B948;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 0 36px;
}}
.f-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 24px; color: #FFE894; }}
.f-2 {{ font-family: 'BeVNSemi', sans-serif; font-size: 21px; color: #EDF7F1; }}
</style>
</head>
<body>
  <div class="left-wash"></div>
  <div class="top-row">
    <div class="logo-box"><img src="{logo_uri}" /></div>
    <div class="top-pill">{spec["pill_txt"]}</div>
  </div>
  <div class="big-head">
    <div class="bh-1">{spec["h_line1"]}</div>
    <div class="bh-2">{spec["h_line2"]}</div>
  </div>
  <div class="hero-stat">
    <div class="hs-num">{spec["hero_num"]}</div>
    <div class="hs-sub">{spec["hero_sub"]}</div>
  </div>
  <div class="chips-row">{chips_html}</div>
  <div class="price-card">
    <div class="pc-name">{spec["prod_name"]}</div>
    <div class="pc-price">{spec["price"]}</div>
    <div class="pc-promo">
      <div class="pp-1">{spec["promo_l1"]}</div>
      <div class="pp-2">{spec["promo_l2"]}</div>
    </div>
  </div>
  <div class="ftr">
    <div class="f-1">{spec["ftr_cta"]}</div>
    <div class="f-2">{LEGAL_TPBS}</div>
  </div>
</body>
</html>"""


def render_overlay(html_path: str, png_path: str, w: int, h: int) -> Image.Image:
    url = "file:///" + html_path.replace("\\", "/")
    cmd = [
        EDGE_EXE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", "--default-background-color=00000000",
        f"--window-size={w},{h}", f"--screenshot={png_path}", url,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(png_path).convert("RGBA")
    return im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im


def main():
    W, H = 1600, 1600
    logo_uri = file_to_data_uri(LOGO_ORIG)
    fcss = font_css()
    qc_imgs = []

    for sp in POSTS:
        bg = Image.open(sp["hero"]).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
        hp = os.path.join(TMP_DIR, f"{sp['id']}.html")
        pp = os.path.join(TMP_DIR, f"{sp['id']}.png")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(build_html(sp, logo_uri, fcss))
        ov = render_overlay(hp, pp, W, H)

        comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        comp.alpha_composite(bg)
        comp.alpha_composite(ov)
        for bp, cx, by, th in sp["boxes"]:
            place_box(comp, bp, cx=cx, bottom_y=by, target_h=th)

        out_jpg = os.path.join(OUT_DIR, sp["filename"])
        ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.06).save(
            out_jpg, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES
        )
        print(f"[DONE] {sp['id']} -> {sp['filename']}", flush=True)
        qc_imgs.append((sp["id"], out_jpg))

    # Build clean 3x2 QC contact sheet for all 5 Designed Posts
    sheet = Image.new("RGB", (2160, 1520), (16, 22, 28))
    draw = ImageDraw.Draw(sheet)
    for idx, (pid, jp) in enumerate(qc_imgs):
        im = Image.open(jp).convert("RGB").resize((680, 680), Image.Resampling.LANCZOS)
        x = (idx % 3) * 720 + 20
        y = (idx // 3) * 760 + 20
        sheet.paste(im, (x, y))
        draw.text((x + 6, y + 692), f"{pid} | {os.path.basename(jp)}", fill=(255, 232, 118))
    qc_path = os.path.join(WORK_DIR, "QA_5_Bai_Thiet_Ke_Nha_Trang.jpg")
    sheet.save(qc_path, quality=92)
    print(f"[QC SHEET] {qc_path}")


if __name__ == "__main__":
    main()
