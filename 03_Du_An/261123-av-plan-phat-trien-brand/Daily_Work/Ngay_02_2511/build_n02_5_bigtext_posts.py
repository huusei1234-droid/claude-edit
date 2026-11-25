# -*- coding: utf-8 -*-
"""
Dựng TRỌN BỘ 5 BÀI ĐĂNG THIẾT KẾ NGÀY 02 — 25/11/2026 (Bối cảnh TP. Nha Trang, Text Cực To, .JPG 1600x1600 sRGB, KHÔNG PSD):
1. TK01: AV Protein — 1.632mg L-Leucine Giữ Cơ Săn Chắc (350.000đ • CTKM 25/11–30/11: Mua 5 Tặng 1 Bojomi 520K)
2. TK02: Bojomi Chạy Bộ Nha Trang — Pha 60°C Tan Mịn Vị Vani (520.000đ • CTKM 25/11–30/11: Mua 3 Tặng 1 Bojomi 520K)
3. TK03: Combo Bé Từ 1 Tuổi+ Biếng Ăn Lười Sữa — Đạm + Canxi Êm Bụng (870.000đ • CHÍNH HÃNG DROPPII, 0% nhãn quà sai!)
4. TK04: Curcumilk Phyto — Bữa Phụ 15H Văn Phòng Ấm Bụng Phytosome Ý (650.000đ • CTKM 25/11–30/11: Mua 4 Tặng 1 Curcumilk 650K)
5. TK05: Collamela Đón Tết + Nhắc Zoom AI 19h30 (25/11) — 2.530mg Collagen Tripeptide (920.000đ • CTKM 25/11–30/11: Mua 2 Tặng 1 Hộp 10g 480K)
100% hộp thật tách nền IS-Net, 0% ký tự emoji lỗi ô vuông, 0% sai CTKM!
"""
import os, base64, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageCms

WORK = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_02_2511"
ASSETS_DIR = os.path.join(WORK, "01_ChatGPT_Post_Portraits")
OUT_DIR = os.path.join(WORK, "03_Final_5_Designs_JPG")
TMP_DIR = os.path.join(WORK, "tmp_post_html")
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

    refl_h = int(nh * 0.18)
    refl = box_r.transpose(Image.Transpose.FLIP_TOP_BOTTOM).crop((0, 0, nw, refl_h))
    grad = np.linspace(44, 0, refl_h, dtype=np.float32)[:, None]
    ra = np.array(refl, dtype=np.float32)
    ra[:, :, 3] = np.clip(ra[:, :, 3] * (grad / 255.0), 0, 255)
    canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(2.0)), (x0, bottom_y - 6))

    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse([x0 - 28, bottom_y - 20, x0 + nw + 16, bottom_y + 22], fill=(18, 28, 24, 85))
    sh = sh.filter(ImageFilter.GaussianBlur(15))
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
        "id": "N02_01",
        "filename": "261125 AVPM Thiet Ke 01 - AV Protein 1632mg Leucine Giu Co San Chac (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N02_POST1_AVP_GYM_NT.png"),
        "boxes": [(P_PRO, 236, 1442, 550)],
        "price_left": 468,
        "wash_rgb": "244,251,255",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ TẬP SÁNG NHA TRANG • ĐẠM THỰC VẬT ★",
        "h_line1": "1.632MG LEUCINE",
        "h_line2": "GIỮ CƠ SĂN CHẮC!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #0B469E 0%, #1567D8 100%)",
        "h1_size": 78, "h2_size": 78,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "22,05g ĐẠM SẠCH",
        "hero_sub": "ĐẬU HÀ LAN & GẠO • INULIN • LỢI KHUẨN B-3",
        "chips": [
            ("1.632mg", "L-Leucine giữ cơ"),
            ("20–40°C", "Pha mát 30 giây"),
            ("Êm Bụng", "Không đầy hơi"),
        ],
        "prod_name": "AV PROTEIN (20 GÓI)",
        "price": "350.000đ",
        "promo_l1": "★ CTKM DROPPII 25/11 – 30/11",
        "promo_l2": "MUA 5 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “ĐẠM SẠCH” nhận thực đơn sau tập sáng • Hotline: 0867 399 268",
    },
    {
        "id": "N02_02",
        "filename": "261125 AVPM Thiet Ke 02 - Bojomi Pha 60 Do Tan Min Vi Vani (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N02_POST2_BOJOMI_RUN5_NT.png"),
        "boxes": [(P_BOJ, 236, 1442, 550)],
        "price_left": 468,
        "wash_rgb": "244,252,248",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ CHẠY BỘ ĐƯỜNG BIỂN • BÍ KÍP PHA CHUẨN ★",
        "h_line1": "PHA ẤM 60°C",
        "h_line2": "TAN MỊN VỊ VANI!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #9E0815 100%)",
        "h1_size": 84, "h2_size": 78,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "417,6mg CANXI",
        "hero_sub": "TẢO BIỂN AQUAMIN F • D3 • K2 MK-7 • COLLAGEN",
        "chips": [
            ("200ml", "Nước ấm 60°C"),
            ("779,4 IU", "Vitamin D3 chuẩn"),
            ("169,8 µg", "K2 MK-7 dẫn canxi"),
        ],
        "prod_name": "BOJOMI VỊ VANI (14 GÓI)",
        "price": "520.000đ",
        "promo_l1": "★ CTKM DROPPII 25/11 – 30/11",
        "promo_l2": "MUA 3 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “BOJOMI” nhận hướng dẫn pha 60°C không vón • Hotline: 0867 399 268",
    },
    {
        "id": "N02_03",
        "filename": "261125 AVPM Thiet Ke 03 - Combo Be 1 Tuoi Bieng An Luoi Sua Em Bung (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N02_POST3_KID1Y_CREAM_NT.png"),
        "boxes": [(P_PRO, 166, 1434, 385), (P_BOJ, 432, 1446, 398)],
        "price_left": 588,
        "price_w": 438,
        "wash_rgb": "247,252,255",
        "pill_bg": "linear-gradient(135deg, #06426B, #0D7564)",
        "pill_txt": "★ BÉ TỪ 1 TUỔI+ BIẾNG ĂN • LƯỜI SỮA ★",
        "h_line1": "CHIA 2 KHUNG GIỜ",
        "h_line2": "CON UỐNG ÊM BỤNG!",
        "h1_color": "#06365A",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #9E0815 100%)",
        "h1_size": 76, "h2_size": 74,
        "hero_badge_bg": "linear-gradient(135deg, #07446E 0%, #0E7866 100%)",
        "hero_num": "BOJOMI + AV PROTEIN",
        "hero_sub": "SÁNG ĐẠM THỰC VẬT 20–40°C • CHIỀU CANXI 60°C",
        "chips": [
            ("1 Tuổi+", "Chia lượng đúng tuổi"),
            ("Lợi Khuẩn", "B-3 + Inulin êm bụng"),
            ("Vị Vani", "Thơm béo dễ uống"),
        ],
        "prod_name": "TRỌN BỘ ĐÔI 2 HỘP",
        "price": "870.000đ",
        "promo_bg": "linear-gradient(135deg, #064D33 0%, #0E7A54 100%)",
        "promo_l1": "★ CHÍNH HÃNG DROPPII",
        "promo_l2": "AV PROTEIN 350K + BOJOMI 520K",
        "ftr_bg": "linear-gradient(90deg, #04283D 0%, #095C52 50%, #04283D 100%)",
        "ftr_cta": "▸ Nhắn “BÉ 1 TUỔI” nhận bảng chia khẩu phần chuẩn • Hotline: 0867 399 268",
    },
    {
        "id": "N02_04",
        "filename": "261125 AVPM Thiet Ke 04 - Curcumilk Phyto 15H Van Phong Am Bung (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N02_POST4_CURCU_15H_NT.png"),
        "boxes": [(P_CUR, 236, 1442, 540)],
        "price_left": 468,
        "wash_rgb": "255,250,238",
        "pill_bg": "linear-gradient(135deg, #B85D00, #E0820A)",
        "pill_txt": "✦ BỮA PHỤ 15H VĂN PHÒNG • KHÔNG HĂNG NGHỆ ✦",
        "h_line1": "15H XẾ CHIỀU",
        "h_line2": "ẤM BỤNG NHẸ NHÀNG!",
        "h1_color": "#5E2D00",
        "h2_grad": "linear-gradient(180deg, #D6201D 0%, #9E0A10 100%)",
        "h1_size": 84, "h2_size": 72,
        "hero_badge_bg": "linear-gradient(135deg, #8F4200 0%, #C96A08 100%)",
        "hero_num": "343,2mg CURCUMINOID",
        "hero_sub": "HỆ 3 LỚP + CURCUMIN PHYTOSOME NHẬP KHẨU Ý",
        "chips": [
            ("Vị Vani", "Sữa dừa dịu béo"),
            ("40–50°C", "150ml nước ấm"),
            ("Không Hăng", "Dễ uống mỗi ngày"),
        ],
        "prod_name": "CURCUMILK PHYTO (14 GÓI)",
        "price": "650.000đ",
        "promo_l1": "★ CTKM DROPPII 25/11 – 30/11",
        "promo_l2": "MUA 4 TẶNG 1 CURCUMILK (650K)",
        "ftr_bg": "linear-gradient(90deg, #472000 0%, #8A4204 50%, #472000 100%)",
        "ftr_cta": "▸ Nhắn “SỮA NGHỆ” nhận bảng thành phần Phytosome Ý • Hotline: 0867 399 268",
    },
    {
        "id": "N02_05",
        "filename": "261125 AVPM Thiet Ke 05 - Collamela Don Tet Va Zoom AI 19h30 (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N02_POST5_COLLA_TET_NT.png"),
        "boxes": [(P_COL, 240, 1442, 545)],
        "price_left": 476,
        "wash_rgb": "255,246,248",
        "pill_bg": "linear-gradient(135deg, #9C124B, #DB2A6F)",
        "pill_txt": "★ ĐÓN TẾT RẠNG RỠ • ZOOM AI 19H30 TỐI NAY (25/11) ★",
        "h_line1": "2.530MG COLLAGEN",
        "h_line2": "DA MỊN ĐÓN TẾT!",
        "h1_color": "#6E0B35",
        "h2_grad": "linear-gradient(180deg, #D91A38 0%, #990822 100%)",
        "h1_size": 76, "h2_size": 84,
        "hero_badge_bg": "linear-gradient(135deg, #9C124B 0%, #DB2A6F 100%)",
        "hero_num": "COLLAGEN TRIPEPTIDE",
        "hero_sub": "2.530MG COLLAGEN • 25,68MG HA • 87MG C • 3,9MG KẼM",
        "chips": [
            ("Vị Đào", "100ml nước mát"),
            ("10 Giây", "Không tanh dễ uống"),
            ("25/11 19h30", "Zoom Tạo Ảnh AI"),
        ],
        "prod_name": "COLLAMELA (20 GÓI)",
        "price": "920.000đ",
        "promo_l1": "★ CTKM DROPPII 25/11 – 30/11",
        "promo_l2": "MUA 2 TẶNG 1 HỘP 10 GÓI (480K)",
        "ftr_bg": "linear-gradient(90deg, #4F0725 0%, #941147 50%, #4F0725 100%)",
        "ftr_cta": "▸ Nhắn “COLLAMELA” chốt quà 480K & nhận link Zoom 19h30 • Hotline: 0867 399 268",
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
  border-radius: 999px; padding: 13px 24px; font-family: 'BeVNExtra', sans-serif;
  font-size: 21px; letter-spacing: 0.3px; white-space: nowrap;
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
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 50px; line-height: 1.05;
  color: #FFF7C2; letter-spacing: -1px; text-shadow: 0 4px 12px rgba(0,0,0,0.32); white-space: nowrap;
}}
.hs-sub {{
  font-family: 'BeVNExtra', sans-serif; font-size: 21px; color: #FFFFFF;
  letter-spacing: 0.2px; margin-top: 6px; white-space: nowrap;
}}
.chips-row {{
  position: absolute; top: 546px; left: 48px; width: 730px;
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;
}}
.chip {{
  background: rgba(255,255,255,0.96); border: 3px solid #E2B64D; border-radius: 22px;
  padding: 14px 10px; text-align: center; box-shadow: 0 10px 22px rgba(0,0,0,0.12);
}}
.ch-v {{ font-family: 'BeVNExtra', sans-serif; font-size: 32px; color: #064D33; line-height: 1.08; white-space: nowrap; }}
.ch-k {{ font-family: 'BeVNBold', sans-serif; font-size: 19px; color: #243830; margin-top: 4px; line-height: 1.18; }}

.price-card {{
  position: absolute; top: 1094px; left: {spec["price_left"]}px; width: {spec.get("price_w", 456)}px;
  background: linear-gradient(155deg, rgba(255,255,255,0.98) 0%, rgba(255,248,228,0.98) 100%);
  border: 4px solid #E5B23E; border-radius: 30px; padding: 18px 18px;
  box-shadow: 0 20px 42px rgba(0,0,0,0.26); text-align: center;
}}
.pc-name {{ font-family: 'BeVNExtra', sans-serif; font-size: 22px; color: #064B32; letter-spacing: 0.3px; }}
.pc-price {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 68px; line-height: 1.04;
  color: #0B40A8; letter-spacing: -2px; margin: 4px 0 10px; white-space: nowrap;
}}
.pc-promo {{
  background: {spec.get("promo_bg", "linear-gradient(135deg, #EB202B 0%, #A60814 100%)")};
  border: 3px solid #FFE285; border-radius: 18px; padding: 10px 10px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.22);
}}
.pp-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 18px; color: #FFF3B0; line-height: 1.15; }}
.pp-2 {{ font-family: 'BeVNExtra', sans-serif; font-size: 19px; color: #FFFFFF; line-height: 1.15; margin-top: 2px; white-space: nowrap; }}

.ftr {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 118px;
  background: {spec["ftr_bg"]}; border-top: 4px solid #E8B948;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 0 36px;
}}
.f-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 23px; color: #FFE894; }}
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

    sheet = Image.new("RGB", (2160, 1520), (16, 22, 28))
    draw = ImageDraw.Draw(sheet)
    for idx, (pid, jp) in enumerate(qc_imgs):
        im = Image.open(jp).convert("RGB").resize((680, 680), Image.Resampling.LANCZOS)
        x = (idx % 3) * 720 + 20
        y = (idx // 3) * 760 + 20
        sheet.paste(im, (x, y))
        draw.text((x + 6, y + 692), f"{pid} | {os.path.basename(jp)}", fill=(255, 232, 118))
    qc_path = os.path.join(WORK, "QA_5_Bai_Thiet_Ke_Ngay_2511.jpg")
    sheet.save(qc_path, quality=92)
    print(f"[QC SHEET] {qc_path}")


if __name__ == "__main__":
    main()
