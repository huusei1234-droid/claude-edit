# -*- coding: utf-8 -*-
"""
Dựng TRỌN BỘ 5 HÌNH THIẾT KẾ AN VƯỢNG PHARMA — NGÀY 28/11/2026
(Nhân vật Chị Hằng khóa 100% nét mặt gốc + dáng chuẩn An Vượng, 5 bộ đồ đời thường riêng biệt,
Hộp thật IS-Net 2200px 0% lỗi chữ, Text Cực To Chuẩn Agency, xuất .JPG 1600x1600 sRGB ICC + .PSD đa layer Photoshop!)
Cập nhật 100% theo dữ liệu Zalo (5 nhóm) & Group FB CỘNG ĐỒNG DROPPII - AN VƯỢNG PHARMA ngày 28/11/2026:
  1. D01: CÒN 2 NGÀY CUỐI (ĐẾN 30/11) — COMBO 4 SẢN PHẨM (2.440.000đ) TẶNG COLLAMELA 20 GÓI (920K) & ĐUA TOP TRI ÂN T11
  2. D02: AV PROTEIN — 22,05g ĐẠM SẠCH BỮA SÁNG GIỮ CƠ KHÔNG NHỊN ĂN (350.000đ • MUA 5 TẶNG 1 BOJOMI 520K)
  3. D03: BOJOMI — 417,6mg CANXI TẢO BIỂN ĐỎ BỮA ĂN GIA ĐÌNH NGƯỜI LỚN (520.000đ • MUA 3 TẶNG 1 BOJOMI 520K • 0% trẻ em!)
  4. D04: CURCUMILK PHYTO — 343,2mg CURCUMINOID PHYTOSOME Ý DỊU HỌNG ÊM BỤNG (650.000đ • MUA 4 TẶNG 1 CURCUMILK 650K)
  5. D05: COLLAMELA — ĐỌC NHÃN 2.530mg COLLAGEN + 87mg VITAMIN C CHĂM DA ĐÓN TIỆC (920.000đ • MUA 2 TẶNG 1 HỘP 10 GÓI 480K)
"""
import os
import base64
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageCms
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, Compression

WORK = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_05_2811_5_Thiet_Ke"
ASSETS_DIR = os.path.join(WORK, "01_ChatGPT_Portraits_1x1")
OUT_JPG_DIR = os.path.join(WORK, "02_Final_5_Designs_JPG")
OUT_PSD_DIR = os.path.join(WORK, "03_File_PSD_Da_Layer")
TMP_DIR = os.path.join(WORK, "tmp_html")
for d in (OUT_JPG_DIR, OUT_PSD_DIR, TMP_DIR):
    os.makedirs(d, exist_ok=True)

CUTOUT_DIR = r"G:\My Drive\dự án ngoài\An Vượng\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\01. Ảnh Sản Phẩm Tách Nền & Logo"
LOGO_ORIG = os.path.join(CUTOUT_DIR, "logo_an_vuong_orig.png")
FONTS_DIR = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_EXE):
    EDGE_EXE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

SRGB_BYTES = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
LEGAL_TPBS = "Thực phẩm bổ sung. Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh."

P_PRO = os.path.join(CUTOUT_DIR, "av01_protein_a.png")
P_BOJ = os.path.join(CUTOUT_DIR, "av02_bojomi_b.png")
P_CUR = os.path.join(CUTOUT_DIR, "av04_curcumilk_b.png")
P_COL = os.path.join(CUTOUT_DIR, "av03_collamela_b.png")


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


def place_box_on_layer(layer: Image.Image, box_path: str, cx: int, bottom_y: int, target_h: int):
    box = Image.open(box_path).convert("RGBA")
    bb = box.getbbox()
    if bb:
        box = box.crop(bb)
    sc = target_h / box.height
    nw, nh = int(round(box.width * sc)), int(round(box.height * sc))
    box_r = ImageEnhance.Sharpness(box.resize((nw, nh), Image.Resampling.LANCZOS)).enhance(1.14)
    x0, y0 = cx - nw // 2, bottom_y - nh

    # Subtle ground reflection
    refl_h = int(nh * 0.16)
    refl = box_r.transpose(Image.Transpose.FLIP_TOP_BOTTOM).crop((0, 0, nw, refl_h))
    grad = np.linspace(40, 0, refl_h, dtype=np.float32)[:, None]
    ra = np.array(refl, dtype=np.float32)
    ra[:, :, 3] = np.clip(ra[:, :, 3] * (grad / 255.0), 0, 255)
    layer.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(2.0)), (x0, bottom_y - 6))

    # Realistic dual soft contact shadow
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse([x0 - 26, bottom_y - 18, x0 + nw + 16, bottom_y + 20], fill=(18, 28, 24, 82))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    d2 = ImageDraw.Draw(sh)
    d2.ellipse([x0 + 6, bottom_y - 9, x0 + nw - 6, bottom_y + 9], fill=(10, 18, 14, 128))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    layer.alpha_composite(sh)
    layer.alpha_composite(box_r, (x0, y0))


def save_multilayer_psd(out_psd: str, bg_rgba: Image.Image, ui_rgba: Image.Image, boxes_rgba: Image.Image):
    W, H = bg_rgba.size
    def to_psd_layer(im_rgba: Image.Image, name: str):
        arr = np.array(im_rgba, dtype=np.uint8)
        channels = {
            -1: arr[:, :, 3],
            0: arr[:, :, 0],
            1: arr[:, :, 1],
            2: arr[:, :, 2],
        }
        return nested_layers.Image(
            name=name,
            visible=True,
            opacity=255,
            top=0, left=0, bottom=H, right=W,
            channels=channels,
            color_mode=ColorMode.rgb,
        )

    # pytoshop nested_layers expects top-to-bottom stacking order
    layers = [
        to_psd_layer(boxes_rgba, "03_Hop_San_Pham_That_ISNet"),
        to_psd_layer(ui_rgba, "02_Chu_To_Va_The_Gia_UI"),
        to_psd_layer(bg_rgba, "01_Nen_Va_Chi_Hang"),
    ]
    psd = nested_layers.nested_layers_to_psd(
        layers,
        color_mode=ColorMode.rgb,
        depth=8,
        compression=Compression.zip,
    )
    with open(out_psd, "wb") as f:
        psd.write(f)


POSTS = [
    {
        "id": "N05_01",
        "filename": "261128 AVPM Thiet Ke 01 - 2 Ngay Cuoi Combo 4 San Pham Tang Collamela 920K.jpg",
        "hero": os.path.join(ASSETS_DIR, "D01_COMBO4_IVORY_BLAZER.png"),
        "boxes": [
            (P_PRO, 130, 1228, 280),
            (P_BOJ, 332, 1228, 286),
            (P_CUR, 152, 1450, 280),
            (P_COL, 362, 1450, 304),
        ],
        "price_left": 536,
        "price_w": 448,
        "wash_rgb": "255,250,242",
        "pill_bg": "linear-gradient(135deg, #B8121E, #E62534)",
        "pill_txt": "★ CÒN 2 NGÀY CUỐI ĐẾN 30/11 • ĐUA TOP TRI ÂN T11 ★",
        "h_line1": "COMBO 4 SẢN PHẨM",
        "h_line2": "TẶNG QUÀ 920K!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #990814 100%)",
        "h1_size": 76, "h2_size": 94,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "TẶNG 1 COLLAMELA",
        "hero_sub": "NGUYÊN HỘP 20 GÓI (920.000Đ) • ĐỢT CUỐI DROPPII 8 TUỔI",
        "chips": [
            ("Đạm Sạch", "AV Protein 350K"),
            ("Xương Khớp", "Bojomi 520K"),
            ("Bụng & Da", "Nghệ + Collamela"),
        ],
        "prod_name": "TRỌN COMBO 4 SẢN PHẨM",
        "price": "2.440.000đ",
        "promo_l1": "★ CÒN 2 NGÀY CUỐI (28/11 – 30/11)",
        "promo_l2": "TẶNG 1 COLLAMELA 20 GÓI (920K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #0A5B3D 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “COMBO 4 SP” chốt quà 920K trước 23h59 30/11 • Hotline: 0867 399 268",
    },
    {
        "id": "N05_02",
        "filename": "261128 AVPM Thiet Ke 02 - AV Protein 22g Dam Sach Bua Sang Giu Co Mua 5 Tang 1.jpg",
        "hero": os.path.join(ASSETS_DIR, "D02_AVPROTEIN_SAGE_MORNING.png"),
        "boxes": [(P_PRO, 236, 1442, 550)],
        "price_left": 468,
        "wash_rgb": "244,252,248",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ BỮA SÁNG 30 GIÂY • GIỮ DÁNG KHÔNG NHỊN ĂN ★",
        "h_line1": "22g ĐẠM SẠCH",
        "h_line2": "GIỮ CƠ ÊM BỤNG!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #0B469E 0%, #1567D8 100%)",
        "h1_size": 86, "h2_size": 78,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "22,05g ĐẠM THỰC VẬT",
        "hero_sub": "1.632MG L-LEUCINE • 1.090MG INULIN • LỢI KHUẨN B-3",
        "chips": [
            ("20–40°C", "Pha mát 30 giây"),
            ("17.500đ", "Chỉ 1 gói sáng"),
            ("Đậu & Gạo", "Nhẹ bụng no êm"),
        ],
        "prod_name": "AV PROTEIN (20 GÓI)",
        "price": "350.000đ",
        "promo_l1": "★ CÒN 2 NGÀY CUỐI (ĐẾN 30/11)",
        "promo_l2": "MUA 5 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “ĐẠM SẠCH” nhận thực đơn bữa sáng 30s • Hotline: 0867 399 268",
    },
    {
        "id": "N05_03",
        "filename": "261128 AVPM Thiet Ke 03 - Bojomi 417mg Canxi Tao Bien Do Bua An Gia Dinh Mua 3 Tang 1.jpg",
        "hero": os.path.join(ASSETS_DIR, "D03_BOJOMI_POLO_FAMILY.png"),
        "boxes": [(P_BOJ, 236, 1442, 550)],
        "price_left": 468,
        "wash_rgb": "245,252,248",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ NGƯỜI LỚN & BỐ MẸ • BỮA ĂN ĐỦ CANXI MỖI NGÀY ★",
        "h_line1": "417,6mg CANXI",
        "h_line2": "TẢO BIỂN ĐỎ CHUẨN!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #9E0815 100%)",
        "h1_size": 84, "h2_size": 70,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "AQUAMIN F + D3 + K2",
        "hero_sub": "779,4 IU VITAMIN D3 • 169,8µg K2 MK-7 • 201,4MG COLLAGEN",
        "chips": [
            ("60°C Ấm", "200ml tan mịn"),
            ("Vị Vani", "Ngũ cốc dễ uống"),
            ("14 Gói", "Tiện biếu bố mẹ"),
        ],
        "prod_name": "BOJOMI VỊ VANI (14 GÓI)",
        "price": "520.000đ",
        "promo_l1": "★ CÒN 2 NGÀY CUỐI (ĐẾN 30/11)",
        "promo_l2": "MUA 3 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “BOJOMI” nhận bảng đọc nhãn & ưu đãi gia đình • Hotline: 0867 399 268",
    },
    {
        "id": "N05_04",
        "filename": "261128 AVPM Thiet Ke 04 - Curcumilk Phyto 343mg Curcuminoid Diu Hong Em Bung Mua 4 Tang 1.jpg",
        "hero": os.path.join(ASSETS_DIR, "D04_CURCUMILK_EMERALD_OFFICE.png"),
        "boxes": [(P_CUR, 236, 1442, 540)],
        "price_left": 468,
        "wash_rgb": "255,250,238",
        "pill_bg": "linear-gradient(135deg, #B85D00, #E0820A)",
        "pill_txt": "✦ NGƯỜI NÓI NHIỀU & HỌP ZOOM • LY NGHỆ ẤM ÊM DỊU ✦",
        "h_line1": "DỊU HỌNG ÊM BỤNG",
        "h_line2": "PHYTOSOME Ý CHUẨN!",
        "h1_color": "#5E2D00",
        "h2_grad": "linear-gradient(180deg, #D6201D 0%, #9E0A10 100%)",
        "h1_size": 76, "h2_size": 68,
        "hero_badge_bg": "linear-gradient(135deg, #8F4200 0%, #C96A08 100%)",
        "hero_num": "343,2mg CURCUMINOID",
        "hero_sub": "HỆ 3 LỚP NGHỆ • CURCUMIN PHYTOSOME Ý / GÓI 15G",
        "chips": [
            ("40–50°C", "Đong 150ml ấm"),
            ("Sữa Dừa", "Vị Vani không hăng"),
            ("14 Gói", "Gọn nhẹ văn phòng"),
        ],
        "prod_name": "CURCUMILK PHYTO (14 GÓI)",
        "price": "650.000đ",
        "promo_l1": "★ CÒN 2 NGÀY CUỐI (ĐẾN 30/11)",
        "promo_l2": "MUA 4 TẶNG 1 CURCUMILK (650K)",
        "ftr_bg": "linear-gradient(90deg, #472000 0%, #8A4204 50%, #472000 100%)",
        "ftr_cta": "▸ Nhắn “PHYTO” nhận hướng dẫn pha ấm 40–50°C • Hotline: 0867 399 268",
    },
    {
        "id": "N05_05",
        "filename": "261128 AVPM Thiet Ke 05 - Collamela 2530mg Collagen 87mg Vit C Cham Da Don Tiec Mua 2 Tang 1.jpg",
        "hero": os.path.join(ASSETS_DIR, "D05_COLLAMELA_BLUSH_SILK.png"),
        "boxes": [(P_COL, 240, 1442, 545)],
        "price_left": 476,
        "wash_rgb": "255,246,248",
        "pill_bg": "linear-gradient(135deg, #9C124B, #DB2A6F)",
        "pill_txt": "★ ĐỌC NHÃN CHUẨN KHẨU PHẦN 2 GÓI • ĐÓN TIỆC TẾT ★",
        "h_line1": "2.530mg COLLAGEN",
        "h_line2": "CHĂM DA ĐÓN TIỆC!",
        "h1_color": "#6E0B35",
        "h2_grad": "linear-gradient(180deg, #D91A38 0%, #990822 100%)",
        "h1_size": 76, "h2_size": 74,
        "hero_badge_bg": "linear-gradient(135deg, #9C124B 0%, #DB2A6F 100%)",
        "hero_num": "TRIPEPTIDE + 87mg C",
        "hero_sub": "25,68MG HA GIỮ ẨM • 3,9MG KẼM • KHẨU PHẦN 2 GÓI (8G)",
        "chips": [
            ("Vị Đào", "Thanh nhẹ 0% tanh"),
            ("100ml", "Nước mát 10 giây"),
            ("20 Gói", "Đều nhịp đón Tết"),
        ],
        "prod_name": "COLLAMELA (20 GÓI)",
        "price": "920.000đ",
        "promo_l1": "★ CÒN 2 NGÀY CUỐI (ĐẾN 30/11)",
        "promo_l2": "MUA 2 TẶNG 1 HỘP 10 GÓI (480K)",
        "ftr_bg": "linear-gradient(90deg, #4F0725 0%, #941147 50%, #4F0725 100%)",
        "ftr_cta": "▸ Nhắn “DA ĐẸP” chốt quà 480K đón tiệc cuối năm • Hotline: 0867 399 268",
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
.big-head {{ position: absolute; top: 132px; left: 48px; width: 960px; display: flex; flex-direction: column; align-items: flex-start; }}
.bh-1 {{
  display: inline-block;
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: {spec["h1_size"]}px;
  line-height: 1.16; padding-top: 14px; letter-spacing: -1.5px; color: {spec["h1_color"]};
  -webkit-text-stroke: 3px rgba(255,255,255,0.88); paint-order: stroke fill;
  filter: drop-shadow(0 6px 12px rgba(0,0,0,0.12)); white-space: nowrap;
}}
.bh-2 {{
  display: inline-block;
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: {spec["h2_size"]}px;
  line-height: 1.22; padding-top: 18px; margin-top: -10px; padding-right: 14px; letter-spacing: -1.5px;
  background: {spec["h2_grad"]}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 0 #FFFFFF) drop-shadow(0 8px 14px rgba(0,0,0,0.14)); white-space: nowrap;
}}
.hero-stat {{
  position: absolute; top: 382px; left: 48px; width: 716px;
  background: {spec["hero_badge_bg"]}; border: 4px solid #FFE07D;
  border-radius: 28px; padding: 18px 24px; box-shadow: 0 16px 32px rgba(0,0,0,0.24);
}}
.hs-num {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 48px; line-height: 1.06;
  color: #FFF7C2; letter-spacing: -1px; text-shadow: 0 4px 12px rgba(0,0,0,0.32); white-space: nowrap;
}}
.hs-sub {{
  font-family: 'BeVNExtra', sans-serif; font-size: 18.5px; color: #FFFFFF;
  letter-spacing: 0.1px; margin-top: 6px; white-space: nowrap;
}}
.chips-row {{
  position: absolute; top: 546px; left: 48px; width: 716px;
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;
}}
.chip {{
  background: rgba(255,255,255,0.96); border: 3px solid #E2B64D; border-radius: 22px;
  padding: 14px 10px; text-align: center; box-shadow: 0 10px 22px rgba(0,0,0,0.12);
}}
.ch-v {{ font-family: 'BeVNExtra', sans-serif; font-size: 31px; color: #064D33; line-height: 1.08; white-space: nowrap; }}
.ch-k {{ font-family: 'BeVNBold', sans-serif; font-size: 18.5px; color: #243830; margin-top: 4px; line-height: 1.18; }}

.price-card {{
  position: absolute; top: 1088px; left: {spec["price_left"]}px; width: {spec.get("price_w", 460)}px;
  background: linear-gradient(155deg, rgba(255,255,255,0.98) 0%, rgba(255,248,228,0.98) 100%);
  border: 4px solid #E5B23E; border-radius: 30px; padding: 18px 18px;
  box-shadow: 0 20px 42px rgba(0,0,0,0.26); text-align: center;
}}
.pc-name {{ font-family: 'BeVNExtra', sans-serif; font-size: 22px; color: #064B32; letter-spacing: 0.3px; }}
.pc-price {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 66px; line-height: 1.04;
  color: #0B40A8; letter-spacing: -2px; margin: 4px 0 10px; white-space: nowrap;
}}
.pc-promo {{
  background: {spec.get("promo_bg", "linear-gradient(135deg, #EB202B 0%, #A60814 100%)")};
  border: 3px solid #FFE285; border-radius: 18px; padding: 10px 10px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.22);
}}
.pp-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 17px; color: #FFF3B0; line-height: 1.15; }}
.pp-2 {{ font-family: 'BeVNExtra', sans-serif; font-size: 18.5px; color: #FFFFFF; line-height: 1.15; margin-top: 2px; white-space: nowrap; }}

.ftr {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 118px;
  background: {spec["ftr_bg"]}; border-top: 4px solid #E8B948;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 0 36px;
}}
.f-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 22.5px; color: #FFE894; }}
.f-2 {{ font-family: 'BeVNSemi', sans-serif; font-size: 20.5px; color: #EDF7F1; }}
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

        boxes_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for bp, cx, by, th in sp["boxes"]:
            place_box_on_layer(boxes_layer, bp, cx=cx, bottom_y=by, target_h=th)

        comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        comp.alpha_composite(bg)
        comp.alpha_composite(ov)
        comp.alpha_composite(boxes_layer)

        out_jpg = os.path.join(OUT_JPG_DIR, sp["filename"])
        ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.06).save(
            out_jpg, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES
        )

        out_psd = os.path.join(OUT_PSD_DIR, sp["filename"].replace(".jpg", ".psd"))
        save_multilayer_psd(out_psd, bg, ov, boxes_layer)

        print(f"[DONE] {sp['id']} -> JPG + PSD ({os.path.getsize(out_psd)//1024} KB)", flush=True)
        qc_imgs.append((sp["id"], out_jpg))

    # Build 3x2 Contact Sheet for visual QC
    cols, rows = 3, 2
    tw = 660
    sheet = Image.new("RGB", (cols * (tw + 32) + 32, rows * (tw + 60) + 28), (16, 22, 28))
    draw = ImageDraw.Draw(sheet)
    for idx, (pid, jp) in enumerate(qc_imgs):
        im = Image.open(jp).convert("RGB").resize((tw, tw), Image.Resampling.LANCZOS)
        r, c = divmod(idx, cols)
        x = 32 + c * (tw + 32)
        y = 20 + r * (tw + 60)
        sheet.paste(im, (x, y))
        draw.text((x + 6, y + tw + 10), f"{pid} | {os.path.basename(jp)[:58]}", fill=(255, 232, 118))
    qc_path = os.path.join(WORK, "QA_5_Bai_Thiet_Ke_Ngay_2811.jpg")
    sheet.save(qc_path, quality=92)
    print(f"[QC SHEET] {qc_path}")


if __name__ == "__main__":
    main()
