"""
Dựng TRỌN BỘ 4 BÀI ĐĂNG THIẾT KẾ NGÀY 01 (24/11/2026) — PHONG CÁCH BẮT MẮT, TEXT CỰC TO (.JPG 1600x1600 sRGB, KHÔNG PSD):
1. Post 01 (Chỉnh bản cũ lên Text Cực To): AV Protein — Bé mặc Đồ tập Pilates xanh mint + tóc buộc nửa
2. Post 02 (Mới): Bojomi — Bé mặc Sơ mi lụa kem công sở + búi thấp + bông tai ngọc trai + dây chuyền vàng + đồng hồ da
3. Post 03 (Mới): Collamela — Bé mặc Đầm lụa hồng đào cổ đổ + xoăn kẹp ngọc trai + bông tai hoa pha lê + dây chuyền giọt sương
4. Post 04 (Mới): Curcumilk Phyto — Bé mặc Cardigan len vàng bơ + đuôi ngựa thấp + khuyên tròn vàng + dây chuyền mặt lá
"""
import os
import base64
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageCms

WORK_DIR = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_01_2411"
ASSETS_DIR = os.path.join(WORK_DIR, "01_ChatGPT_Assets")
OUT_DIR = os.path.join(WORK_DIR, "03_Bai_Dang_Thiet_Ke_4_Bai_Text_To")
TMP_DIR = os.path.join(WORK_DIR, "tmp_4posts_html")
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

    # Realistic soft marble reflection
    refl_h = int(nh * 0.22)
    refl = box_r.transpose(Image.Transpose.FLIP_TOP_BOTTOM).crop((0, 0, nw, refl_h))
    grad = np.linspace(48, 0, refl_h, dtype=np.float32)[:, None]
    ra = np.array(refl, dtype=np.float32)
    ra[:, :, 3] = np.clip(ra[:, :, 3] * (grad / 255.0), 0, 255)
    canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(2.0)), (x0, bottom_y - 6))

    # Multi-layer grounded contact shadow
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse([x0 - 40, bottom_y - 24, x0 + nw + 16, bottom_y + 28], fill=(18, 28, 24, 88))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    d2 = ImageDraw.Draw(sh)
    d2.ellipse([x0 + 6, bottom_y - 12, x0 + nw - 6, bottom_y + 10], fill=(10, 18, 14, 135))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(box_r, (x0, y0))


POSTS = [
    {
        "id": "POST_01",
        "filename": "261124 AVPM Thiet Ke 01 - AV Protein 22g Dam Sach (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N01_HERO_MINT_POSTER_1x1.png"),
        "box": os.path.join(CUTOUT_DIR, "av01_protein_a.png"),
        "box_cx": 236, "box_h": 560,
        "wash_rgb": "246,252,248",
        "pill_bg": "linear-gradient(135deg, #064D33, #0F7A53)",
        "pill_txt": "✨ BỮA SÁNG 30 GIÂY • ĐẠM SẠCH",
        "h_line1": "ĂN ĐỦ NO",
        "h_line2": "HAY ĐỦ ĐẠM?",
        "h1_color": "#053E29",
        "h2_grad": "linear-gradient(180deg, #E58C08 0%, #B85600 100%)",
        "h1_size": 106, "h2_size": 112,
        "hero_badge_bg": "linear-gradient(135deg, #054A30 0%, #0D7A52 100%)",
        "hero_num": "22,05g ĐẠM",
        "hero_sub": "THỰC VẬT ĐẬU HÀ LAN & GẠO / 2 GÓI",
        "chips": [
            ("1.632mg", "L-Leucine giữ cơ"),
            ("1.090mg", "Chất xơ Inulin"),
            ("50mg", "Lợi khuẩn B-3"),
        ],
        "prod_name": "AV PROTEIN (20 GÓI)",
        "price": "350.000đ",
        "promo_l1": "🎁 CTKM DROPPII 23/11 – 30/11",
        "promo_l2": "MUA 5 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "💬 Nhắn “ĐẠM SẠCH” nhận bảng pha 20–40°C • Hotline: 0867 399 268",
    },
    {
        "id": "POST_02",
        "filename": "261124 AVPM Thiet Ke 02 - Bojomi Canxi Tao Bien D3 K2 (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N01_LOOK2_BOJOMI_1x1.png"),
        "box": os.path.join(CUTOUT_DIR, "av02_bojomi_b.png"),
        "box_cx": 236, "box_h": 560,
        "wash_rgb": "255,250,242",
        "pill_bg": "linear-gradient(135deg, #064D33, #0B6B48)",
        "pill_txt": "🦴 CHĂM XƯƠNG KHỚP CHO CẢ NHÀ",
        "h_line1": "CHỌN CANXI",
        "h_line2": "ĐỪNG NHÌN MG!",
        "h1_color": "#053B27",
        "h2_grad": "linear-gradient(180deg, #D91E2A 0%, #9E0916 100%)",
        "h1_size": 106, "h2_size": 98,
        "hero_badge_bg": "linear-gradient(135deg, #0B469E 0%, #1567D8 100%)",
        "hero_num": "417,6mg CANXI",
        "hero_sub": "TẢO BIỂN ĐỎ AQUAMIN F + D3 + K2 MK-7",
        "chips": [
            ("779,4 IU", "Vitamin D3"),
            ("169,8 µg", "K2 MK-7 dẫn lối"),
            ("201,4mg", "Collagen dẻo dai"),
        ],
        "prod_name": "BOJOMI VỊ VANI (14 GÓI)",
        "price": "520.000đ",
        "promo_l1": "🎁 CTKM DROPPII 23/11 – 30/11",
        "promo_l2": "MUA 3 TẶNG 1 BOJOMI (520K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "💬 Nhắn “BOJOMI” xem nhãn chuẩn & cách pha 60°C • Hotline: 0867 399 268",
    },
    {
        "id": "POST_03",
        "filename": "261124 AVPM Thiet Ke 03 - Collamela 60 Ngay Don Tet Da Dep (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N01_LOOK3_COLLAMELA_1x1.png"),
        "box": os.path.join(CUTOUT_DIR, "av03_collamela_b.png"),
        "box_cx": 236, "box_h": 540,
        "wash_rgb": "255,244,246",
        "pill_bg": "linear-gradient(135deg, #A3144F, #D82E6F)",
        "pill_txt": "🌸 60 NGÀY ĐÓN TẾT XINH — VỊ ĐÀO",
        "h_line1": "ĐÓN TẾT XINH",
        "h_line2": "DA CĂNG MƯỚT!",
        "h1_color": "#7D0B3C",
        "h2_grad": "linear-gradient(180deg, #E22A6F 0%, #9E0A44 100%)",
        "h1_size": 96, "h2_size": 100,
        "hero_badge_bg": "linear-gradient(135deg, #981048 0%, #D92B70 100%)",
        "hero_num": "2.530mg COLLAGEN",
        "hero_sub": "TRIPEPTIDE PHÂN TỬ NHỎ / 2 GÓI",
        "chips": [
            ("25,68mg", "HA cấp ẩm sâu"),
            ("87mg", "Vitamin C sáng"),
            ("3,9mg", "Kẽm & Vị Đào"),
        ],
        "prod_name": "COLLAMELA (20 GÓI × 4G)",
        "price": "920.000đ",
        "promo_l1": "🎁 CTKM DROPPII 23/11 – 30/11",
        "promo_l2": "MUA 2 TẶNG 1 HỘP 10G (480K)",
        "ftr_bg": "linear-gradient(90deg, #4E0726 0%, #8A1044 50%, #4E0726 100%)",
        "ftr_cta": "💬 Nhắn “DA ĐẸP” nhận lịch chăm da 60 ngày đón Tết • Hotline: 0867 399 268",
    },
    {
        "id": "POST_04",
        "filename": "261124 AVPM Thiet Ke 04 - Curcumilk Phyto Sua Nghe Y Em Bung (Text To).jpg",
        "hero": os.path.join(ASSETS_DIR, "N01_LOOK4_CURCUMILK_1x1.png"),
        "box": os.path.join(CUTOUT_DIR, "av04_curcumilk_b.png"),
        "box_cx": 236, "box_h": 560,
        "wash_rgb": "255,250,238",
        "pill_bg": "linear-gradient(135deg, #B86200, #E08A08)",
        "pill_txt": "☕ BỮA PHỤ 15H • KHÔNG HĂNG NGHỆ",
        "h_line1": "SỮA NGHỆ Ý",
        "h_line2": "ÊM BỤNG 15H!",
        "h1_color": "#06472F",
        "h2_grad": "linear-gradient(180deg, #E57F00 0%, #B34D00 100%)",
        "h1_size": 106, "h2_size": 106,
        "hero_badge_bg": "linear-gradient(135deg, #064C32 0%, #0F754F 100%)",
        "hero_num": "343,2mg NGHỆ Ý",
        "hero_sub": "CURCUMINOID PHYTOSOME • 1 GÓI 15G",
        "chips": [
            ("3 Nguồn", "Nghệ Phytosome"),
            ("Sữa Dừa", "Vị Vani béo êm"),
            ("40–50°C", "Pha tan 30 giây"),
        ],
        "prod_name": "CURCUMILK PHYTO (14 GÓI)",
        "price": "650.000đ",
        "promo_l1": "🎁 CTKM DROPPII 23/11 – 30/11",
        "promo_l2": "MUA 4 TẶNG 1 HỘP (650K)",
        "ftr_bg": "linear-gradient(90deg, #04291B 0%, #09573A 50%, #04291B 100%)",
        "ftr_cta": "💬 Nhắn “PHYTO” xem nhãn chuẩn & hướng dẫn pha ấm • Hotline: 0867 399 268",
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

/* Clean soft bright wash strictly on LEFT HALF (0..55%) so GIANT TEXT pops 10/10 while Bé Mẫu on right stays 100% vivid */
.left-wash {{
  position: absolute; inset: 0;
  background: linear-gradient(94deg, rgba({spec["wash_rgb"]},0.94) 0%, rgba({spec["wash_rgb"]},0.84) 40%, rgba({spec["wash_rgb"]},0.0) 58%);
}}

/* TOP ROW: Logo + Bold Pill */
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
  border-radius: 999px; padding: 13px 28px; font-family: 'BeVNExtra', sans-serif;
  font-size: 23px; letter-spacing: 0.4px; white-space: nowrap;
  box-shadow: 0 10px 22px rgba(0,0,0,0.18);
}}

/* GIANT SCROLL-STOPPING HEADLINE (TEXT CỰC TO!) */
.big-head {{
  position: absolute; top: 138px; left: 48px; width: 830px;
}}
.bh-1 {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: {spec["h1_size"]}px;
  line-height: 1.06; padding-top: 8px; letter-spacing: -2px;
  color: {spec["h1_color"]};
  -webkit-text-stroke: 3px rgba(255,255,255,0.85);
  paint-order: stroke fill;
  filter: drop-shadow(0 6px 12px rgba(0,0,0,0.12));
}}
.bh-2 {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: {spec["h2_size"]}px;
  line-height: 1.08; padding-top: 6px; letter-spacing: -2px;
  background: {spec["h2_grad"]};
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 0 #FFFFFF) drop-shadow(0 8px 14px rgba(0,0,0,0.14));
}}

/* GIANT HERO STAT RIBBON (BẮT MẮT TRONG 0.5 GIÂY!) */
.hero-stat {{
  position: absolute; top: 416px; left: 48px; width: 708px;
  background: {spec["hero_badge_bg"]}; border: 4px solid #FFE07D;
  border-radius: 28px; padding: 18px 28px;
  box-shadow: 0 16px 32px rgba(0,0,0,0.24);
}}
.hs-num {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 58px; line-height: 1.04;
  color: #FFF7C2; letter-spacing: -1px; text-shadow: 0 4px 12px rgba(0,0,0,0.32);
  white-space: nowrap;
}}
.hs-sub {{
  font-family: 'BeVNExtra', sans-serif; font-size: 24px; color: #FFFFFF;
  letter-spacing: 0.4px; margin-top: 6px; white-space: nowrap;
}}

/* 3 HIGH-CONTRAST MINI CHIPS */
.chips-row {{
  position: absolute; top: 584px; left: 48px; width: 708px;
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;
}}
.chip {{
  background: rgba(255,255,255,0.96); border: 3px solid #E2B64D; border-radius: 22px;
  padding: 14px 14px; text-align: center;
  box-shadow: 0 10px 22px rgba(0,0,0,0.12);
}}
.ch-v {{ font-family: 'BeVNExtra', sans-serif; font-size: 36px; color: #064D33; line-height: 1.08; white-space: nowrap; }}
.ch-k {{ font-family: 'BeVNBold', sans-serif; font-size: 20px; color: #243830; margin-top: 4px; line-height: 1.18; }}

/* BIG PRICE & PROMO CARD (Bottom Center-Left, ZERO overlap with real box cx=255 or Bé Mẫu right!) */
.price-card {{
  position: absolute; top: 1094px; left: 468px; width: 454px;
  background: linear-gradient(155deg, rgba(255,255,255,0.98) 0%, rgba(255,248,228,0.98) 100%);
  border: 4px solid #E5B23E; border-radius: 30px; padding: 18px 20px;
  box-shadow: 0 20px 42px rgba(0,0,0,0.26); text-align: center;
}}
.pc-name {{ font-family: 'BeVNExtra', sans-serif; font-size: 23px; color: #064B32; letter-spacing: 0.3px; }}
.pc-price {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 74px; line-height: 1.02;
  color: #0B40A8; letter-spacing: -2px; margin: 4px 0 10px;
}}
.pc-promo {{
  background: linear-gradient(135deg, #EB202B 0%, #A60814 100%);
  border: 3px solid #FFE285; border-radius: 18px; padding: 10px 14px;
  box-shadow: 0 10px 20px rgba(166,8,20,0.34);
}}
.pp-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 18px; color: #FFF3B0; line-height: 1.15; }}
.pp-2 {{ font-family: 'BeVNExtra', sans-serif; font-size: 25px; color: #FFFFFF; line-height: 1.15; margin-top: 2px; white-space: nowrap; }}

/* BOTTOM BRAND + LEGAL FOOTER */
.ftr {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 118px;
  background: {spec["ftr_bg"]}; border-top: 4px solid #E8B948;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 0 36px;
}}
.f-1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 25px; color: #FFE894; }}
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

        # Composite Hero -> Overlay (Wash + Big Text + Price Card) -> Real IS-Net Product Box on left marble!
        comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        comp.alpha_composite(bg)
        comp.alpha_composite(ov)
        place_box(comp, sp["box"], cx=sp["box_cx"], bottom_y=1442, target_h=sp["box_h"])

        out_jpg = os.path.join(OUT_DIR, sp["filename"])
        ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.06).save(
            out_jpg, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES
        )
        print(f"[DONE] {sp['id']} -> {sp['filename']}", flush=True)
        qc_imgs.append((sp["id"], out_jpg))

    # Build 2x2 QC contact sheet for all 4 Designed Posts
    sheet = Image.new("RGB", (1440, 1520), (16, 22, 28))
    draw = ImageDraw.Draw(sheet)
    for idx, (pid, jp) in enumerate(qc_imgs):
        im = Image.open(jp).convert("RGB").resize((680, 680), Image.Resampling.LANCZOS)
        x = (idx % 2) * 720 + 20
        y = (idx // 2) * 760 + 20
        sheet.paste(im, (x, y))
        draw.text((x + 6, y + 692), f"{pid} | {os.path.basename(jp)}", fill=(255, 232, 118))
    qc_path = os.path.join(WORK_DIR, "QA_4_Bai_Thiet_Ke_Text_To_N01.jpg")
    sheet.save(qc_path, quality=92)
    print(f"[QC SHEET] {qc_path}")


if __name__ == "__main__":
    main()
