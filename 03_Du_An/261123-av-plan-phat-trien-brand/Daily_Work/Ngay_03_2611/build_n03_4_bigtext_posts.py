# -*- coding: utf-8 -*-
"""
Dựng TRỌN BỘ 4 BÀI ĐĂNG THIẾT KẾ NGÀY 03 — 26/11/2026 (100% Bối cảnh Sinh hoạt Đời thường Khớp Kịch bản,
0% ép bối cảnh Nha Trang, Text Cực To, .JPG 1600x1600 sRGB, KHÔNG PSD):
1. TK01: AV Protein — Bữa Sáng Vội 30s Êm Bụng Nhờ Inulin + Lợi Khuẩn B-3 (350.000đ • Mua 5 Tặng 1 Bojomi 520K)
2. TK02: Bojomi — Bộ 3 Dẫn Đường Ca – D3 – K2 MK-7 Dân Văn Phòng & Người Lớn (520.000đ • Mua 3 Tặng 1 Bojomi 520K, 0% trẻ em!)
3. TK03: Curcumilk Phyto — 3 Nguồn Nghệ + Phytosome Ý Không Hăng Cả Nhà Đều Mê (650.000đ • Mua 4 Tặng 1 Curcumilk 650K)
4. TK04: Collamela — Vị Đào 100ml Không Tanh 2.530mg Collagen Tripeptide Đón Tết (920.000đ • Mua 2 Tặng 1 Hộp 10g 480K)
Lồng ghép tinh tế sự kiện Black Friday 26/11 & Đợt Cuối Sinh Nhật Droppii (25/11–30/11).
"""
import os, base64, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageCms

WORK = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_03_2611"
ASSETS_DIR = os.path.join(WORK, "01_ChatGPT_Post_Portraits")
OUT_DIR = os.path.join(WORK, "03_Final_4_Designs_JPG")
TMP_DIR = os.path.join(WORK, "tmp_post_html")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

CUTOUT_DIR = r"G:\My Drive\dự án ngoài\An Vượng\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\01. Ảnh Sản Phẩm Tách Nền & Logo"
LOGO_ORIG = os.path.join(CUTOUT_DIR, "logo_an_vuong_orig.png")
FONTS_DIR = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"

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
P_CUR = os.path.join(CUTOUT_DIR, "av04_curcumilk_b.png")
P_COL = os.path.join(CUTOUT_DIR, "av03_collamela_b.png")

POSTS = [
    {
        "id": "N03_01",
        "filename": "261126 AVPM Thiet Ke 01 - AV Protein Bua Sang Voi Inulin Loi Khuan B3 Em Bung (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N03_POST1_AVP_KITCHEN.png"),
        "boxes": [(P_PRO, 236, 1442, 550)],
        "price_left": 468,
        "wash_rgb": "245,252,249",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ BỮA SÁNG VỘI 30 GIÂY • NHẸ BỤNG ĐỦ ĐẠM ★",
        "h_line1": "INULIN + B-3",
        "h_line2": "ÊM BỤNG MỖI SÁNG!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #0B469E 0%, #1567D8 100%)",
        "h1_size": 84, "h2_size": 74,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "22,05g ĐẠM SẠCH",
        "hero_sub": "ĐẬU HÀ LAN & GẠO • CHẤT XƠ INULIN • LỢI KHUẨN B-3",
        "chips": [
            ("20–40°C", "Pha mát 30 giây"),
            ("Không Khô", "Dễ uống buổi sáng"),
            ("17.500đ", "Chi phí 1 gói"),
        ],
        "prod_name": "AV PROTEIN (20 GÓI)",
        "price": "350.000đ",
        "promo_l1": "★ BLACK FRIDAY & ĐỢT CUỐI 30/11",
        "promo_l2": "MUA 5 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “ĐẠM SẠCH” nhận công thức bữa sáng 30s • Hotline: 0867 399 268",
    },
    {
        "id": "N03_02",
        "filename": "261126 AVPM Thiet Ke 02 - Bojomi Bo 3 Dan Duong Ca D3 K2 MK7 Van Phong (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N03_POST2_BOJOMI_OFFICE.png"),
        "boxes": [(P_BOJ, 236, 1442, 550)],
        "price_left": 468,
        "wash_rgb": "244,251,248",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "★ DÂN VĂN PHÒNG & NGƯỜI LỚN • ĐỌC NHÃN CHUẨN ★",
        "h_line1": "CA – D3 – K2 MK-7",
        "h_line2": "KIỀNG 3 CHÂN XƯƠNG!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #E31F2C 0%, #9E0815 100%)",
        "h1_size": 78, "h2_size": 72,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "417,6mg CANXI",
        "hero_sub": "TẢO BIỂN ĐỎ AQUAMIN F • 779,4 IU D3 • 169,8µg K2 MK-7",
        "chips": [
            ("60°C", "200ml ấm tan mịn"),
            ("Vị Vani", "Ngũ cốc dễ uống"),
            ("201,4mg", "Bổ sung Collagen"),
        ],
        "prod_name": "BOJOMI VỊ VANI (14 GÓI)",
        "price": "520.000đ",
        "promo_l1": "★ BLACK FRIDAY & ĐỢT CUỐI 30/11",
        "promo_l2": "MUA 3 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "▸ Nhắn “BOJOMI” kiểm tra bảng thành phần chuẩn • Hotline: 0867 399 268",
    },
    {
        "id": "N03_03",
        "filename": "261126 AVPM Thiet Ke 03 - Curcumilk Phyto 3 Nguon Nghe Phytosome Y Khong Hang (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N03_POST3_CURCU_HOME.png"),
        "boxes": [(P_CUR, 236, 1442, 540)],
        "price_left": 468,
        "wash_rgb": "255,250,238",
        "pill_bg": "linear-gradient(135deg, #B85D00, #E0820A)",
        "pill_txt": "✦ KHÁCH SHOWROOM MÊ TÍT • CẢ NHÀ DÙNG ÊM BỤNG ✦",
        "h_line1": "PHYTOSOME Ý",
        "h_line2": "KHÔNG HỀ HĂNG NGHỆ!",
        "h1_color": "#5E2D00",
        "h2_grad": "linear-gradient(180deg, #D6201D 0%, #9E0A10 100%)",
        "h1_size": 84, "h2_size": 68,
        "hero_badge_bg": "linear-gradient(135deg, #8F4200 0%, #C96A08 100%)",
        "hero_num": "343,2mg CURCUMINOID",
        "hero_sub": "HỆ 3 NGUỒN NGHỆ + CURCUMIN PHYTOSOME NHẬP KHẨU Ý",
        "chips": [
            ("Sữa Dừa", "Vị Vani thơm dịu"),
            ("40–50°C", "150ml ấm xế chiều"),
            ("14 Gói", "Tiện mang đi làm"),
        ],
        "prod_name": "CURCUMILK PHYTO (14 GÓI)",
        "price": "650.000đ",
        "promo_l1": "★ BLACK FRIDAY & ĐỢT CUỐI 30/11",
        "promo_l2": "MUA 4 TẶNG 1 CURCUMILK (650K)",
        "ftr_bg": "linear-gradient(90deg, #472000 0%, #8A4204 50%, #472000 100%)",
        "ftr_cta": "▸ Nhắn “PHYTO” nhận tư vấn liệu trình gia đình • Hotline: 0867 399 268",
    },
    {
        "id": "N03_04",
        "filename": "261126 AVPM Thiet Ke 04 - Collamela Vi Dao 100ml Khong Tanh Cham Da Don Tet (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N03_POST4_COL_VANITY.png"),
        "boxes": [(P_COL, 240, 1442, 545)],
        "price_left": 476,
        "wash_rgb": "255,246,248",
        "pill_bg": "linear-gradient(135deg, #9C124B, #DB2A6F)",
        "pill_txt": "★ THÓI QUEN TỐI 10 GIÂY • NUÔI DA ĐÓN TẾT ★",
        "h_line1": "VỊ ĐÀO 100ML",
        "h_line2": "NGON KHÔNG HỀ TANH!",
        "h1_color": "#6E0B35",
        "h2_grad": "linear-gradient(180deg, #D91A38 0%, #990822 100%)",
        "h1_size": 82, "h2_size": 68,
        "hero_badge_bg": "linear-gradient(135deg, #9C124B 0%, #DB2A6F 100%)",
        "hero_num": "2.530mg TRIPEPTIDE",
        "hero_sub": "COLLAGEN PHÂN TỬ NHỎ • 25,68MG HA • 87MG C • 3,9MG KẼM",
        "chips": [
            ("100ml", "Nước mát 10 giây"),
            ("Không Tanh", "Thanh ngọt dễ uống"),
            ("Gói Nhỏ", "Đặt bàn trang điểm"),
        ],
        "prod_name": "COLLAMELA (20 GÓI)",
        "price": "920.000đ",
        "promo_l1": "★ BLACK FRIDAY & ĐỢT CUỐI 30/11",
        "promo_l2": "MUA 2 TẶNG 1 HỘP 10 GÓI (480K)",
        "ftr_bg": "linear-gradient(90deg, #4F0725 0%, #941147 50%, #4F0725 100%)",
        "ftr_cta": "▸ Nhắn “DA ĐẸP” chốt quà 480K đón Tết ngay • Hotline: 0867 399 268",
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
  position: absolute; top: 382px; left: 48px; width: 730px;
  background: {spec["hero_badge_bg"]}; border: 4px solid #FFE07D;
  border-radius: 28px; padding: 18px 26px; box-shadow: 0 16px 32px rgba(0,0,0,0.24);
}}
.hs-num {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 50px; line-height: 1.05;
  color: #FFF7C2; letter-spacing: -1px; text-shadow: 0 4px 12px rgba(0,0,0,0.32); white-space: nowrap;
}}
.hs-sub {{
  font-family: 'BeVNExtra', sans-serif; font-size: 20px; color: #FFFFFF;
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
.pp-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 17px; color: #FFF3B0; line-height: 1.15; }}
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

    sheet = Image.new("RGB", (1480, 1520), (16, 22, 28))
    draw = ImageDraw.Draw(sheet)
    for idx, (pid, jp) in enumerate(qc_imgs):
        im = Image.open(jp).convert("RGB").resize((680, 680), Image.Resampling.LANCZOS)
        x = (idx % 2) * 720 + 28
        y = (idx // 2) * 750 + 20
        sheet.paste(im, (x, y))
        draw.text((x + 6, y + 692), f"{pid} | {os.path.basename(jp)[:52]}", fill=(255, 232, 118))
    qc_path = os.path.join(WORK, "QA_4_Bai_Thiet_Ke_Ngay_2611.jpg")
    sheet.save(qc_path, quality=92)
    print(f"[QC SHEET] {qc_path}")


if __name__ == "__main__":
    main()
