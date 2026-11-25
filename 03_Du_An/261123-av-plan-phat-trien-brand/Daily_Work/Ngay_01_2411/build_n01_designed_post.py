"""
Dựng Bài Đăng Thiết Kế Ngày 01 (24/11/2026) — An Vượng Pharma (1600x1600 sRGB + 4-Layer Editable PSD).
Ghép 100% ảnh Bé Mẫu mặc đồ tập Pilates xanh mint (N01_HERO_MINT_POSTER_1x1.png)
+ 100% hộp sản phẩm thật IS-Net (av01_protein_a.png) + Logo chính thức + 4 chỉ số chuẩn hộp + pháp lý TPBS.
"""
import os
import base64
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageCms
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, Compression

WORK_DIR = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_01_2411"
OUT_DIR = os.path.join(WORK_DIR, "03_Bai_Dang_Thiet_Ke")
TMP_DIR = os.path.join(WORK_DIR, "tmp_post_html")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

HERO_IMG = os.path.join(WORK_DIR, "01_ChatGPT_Assets", "N01_HERO_MINT_POSTER_1x1.png")
BOX_AV_PRO = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG\av01_protein_a.png"
LOGO_ORIG = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG\logo_an_vuong_orig.png"
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
        ("PlayfairBI", "PlayfairDisplay-BoldItalic.ttf"),
    ]
    lines = []
    for fam, fn in fonts:
        uri = file_to_data_uri(os.path.join(FONTS_DIR, fn))
        lines.append(f"@font-face {{ font-family: '{fam}'; src: url('{uri}') format('truetype'); font-weight: 100 900; }}")
    return "\n".join(lines)


def render_html_rgba(html_path: str, png_path: str, w: int, h: int) -> Image.Image:
    url = "file:///" + html_path.replace("\\", "/")
    cmd = [
        EDGE_EXE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", "--default-background-color=00000000",
        f"--window-size={w},{h}", f"--screenshot={png_path}", url,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(png_path).convert("RGBA")
    if im.size != (w, h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    return im


def save_psd(layers_spec: list, out_path: str, w: int, h: int):
    psd_layers = []
    for name, img_rgba in reversed(layers_spec):
        arr = np.array(img_rgba.convert("RGBA"), dtype=np.uint8)
        ch = {0: arr[:, :, 0], 1: arr[:, :, 1], 2: arr[:, :, 2], -1: arr[:, :, 3]}
        psd_layers.append(nested_layers.Image(name=name, top=0, left=0, bottom=h, right=w, channels=ch, opacity=255, visible=True))
    psd = nested_layers.nested_layers_to_psd(psd_layers, color_mode=ColorMode.rgb, size=(w, h), compression=Compression.zip)
    with open(out_path, "wb") as f:
        psd.write(f)


def place_box_on_marble(canvas: Image.Image, box_path: str, cx: int, bottom_y: int, target_h: int):
    box = Image.open(box_path).convert("RGBA")
    bb = box.getbbox()
    if bb:
        box = box.crop(bb)
    sc = target_h / box.height
    nw, nh = int(round(box.width * sc)), int(round(box.height * sc))
    box_r = box.resize((nw, nh), Image.Resampling.LANCZOS)
    box_r = ImageEnhance.Sharpness(box_r).enhance(1.12)

    x0, y0 = cx - nw // 2, bottom_y - nh

    # Soft directional marble reflection
    refl_h = int(nh * 0.24)
    refl = box_r.transpose(Image.Transpose.FLIP_TOP_BOTTOM).crop((0, 0, nw, refl_h))
    grad = np.linspace(54, 0, refl_h, dtype=np.float32)[:, None]
    ra = np.array(refl, dtype=np.float32)
    ra[:, :, 3] = np.clip(ra[:, :, 3] * (grad / 255.0), 0, 255)
    refl_im = Image.fromarray(ra.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(2.2))
    canvas.alpha_composite(refl_im, (x0, bottom_y - 6))

    # Realistic multi-layer contact + ambient shadow on marble
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    # Ambient cast shadow toward left-bottom (sunlight comes from right window!)
    d.ellipse([x0 - 46, bottom_y - 26, x0 + nw + 12, bottom_y + 30], fill=(24, 38, 30, 82))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    d2 = ImageDraw.Draw(sh)
    d2.ellipse([x0 + 6, bottom_y - 14, x0 + nw - 8, bottom_y + 12], fill=(12, 26, 18, 128))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    canvas.alpha_composite(sh)

    canvas.alpha_composite(box_r, (x0, y0))
    return (x0, y0, x0 + nw, bottom_y)


def build_html(logo_uri: str, pass_mode: str) -> str:
    is_decor = (pass_mode == "decor")
    d_vis = "visible" if is_decor else "hidden"
    t_vis = "hidden" if is_decor else "visible"

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<style>
{font_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1600px; height: 1600px; overflow: hidden;
  background: transparent; position: relative;
  font-family: 'BeVNBold', sans-serif;
  -webkit-font-smoothing: antialiased;
}}

/* Soft left sunlit ivory wash so typography pops with 10/10 legibility while leaving Bé Mẫu on right 100% crisp */
.left-wash {{
  position: absolute; inset: 0;
  background: linear-gradient(96deg, rgba(252,250,244,0.88) 0%, rgba(252,250,244,0.72) 38%, rgba(252,250,244,0.0) 56%);
  visibility: {d_vis};
}}

/* Top-left logo + campaign chip */
.top-row-bg {{
  position: absolute; top: 44px; left: 52px; display: flex; align-items: center; gap: 16px;
  visibility: {d_vis};
}}
.logo-pill-bg {{
  width: 214px; height: 84px; border-radius: 22px;
  background: rgba(255,255,255,0.96); border: 2.5px solid #DFB145;
  box-shadow: 0 10px 24px rgba(10,58,38,0.12);
}}
.tag-pill-bg {{
  width: 452px; height: 54px; border-radius: 999px;
  background: linear-gradient(135deg, #074C32 0%, #0E6E4A 100%);
  border: 2px solid #F0CC69;
  box-shadow: 0 8px 18px rgba(7,76,50,0.22);
}}
.top-row-txt {{
  position: absolute; top: 44px; left: 52px; display: flex; align-items: center; gap: 16px;
  visibility: {t_vis};
}}
.logo-pill-txt {{
  width: 214px; height: 84px; display: flex; align-items: center; justify-content: center; padding: 8px 14px;
}}
.logo-pill-txt img {{ height: 68px; width: auto; }}
.tag-pill-txt {{
  width: 452px; height: 54px; display: flex; align-items: center; justify-content: center;
  font-family: 'BeVNExtra', sans-serif; font-size: 19px; letter-spacing: 0.5px; color: #FFF4C7;
  white-space: nowrap;
}}

/* Editorial Headline Block (Left upper area, zero overlap with Bé Mẫu!) */
.headline-wrap {{
  position: absolute; top: 154px; left: 54px; width: 730px;
  visibility: {t_vis};
}}
.h-kicker {{
  font-family: 'BeVNExtra', sans-serif; font-size: 32px; color: #0C6140;
  letter-spacing: 0.4px; margin-bottom: 6px;
}}
.h-main {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 74px; line-height: 1.08;
  padding-top: 6px; letter-spacing: -1px;
  background: linear-gradient(180deg, #053A26 0%, #0B6141 68%, #043220 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 3px 0 rgba(255,255,255,0.85));
}}
.h-accent {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 82px; line-height: 1.08;
  padding-top: 6px; letter-spacing: -1px;
  background: linear-gradient(180deg, #D98A0C 0%, #B86404 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 3px 0 rgba(255,255,255,0.9));
}}
.h-sub-bg {{
  position: absolute; top: 386px; left: 54px; width: 642px; height: 52px; border-radius: 14px;
  background: linear-gradient(90deg, #085437 0%, #107650 100%);
  border-left: 6px solid #F0C44C;
  box-shadow: 0 8px 18px rgba(8,84,55,0.20);
  visibility: {d_vis};
}}
.h-sub-txt {{
  position: absolute; top: 386px; left: 54px; width: 642px; height: 52px; padding-left: 20px;
  display: flex; align-items: center; white-space: nowrap;
  font-family: 'BeVNExtra', sans-serif; font-size: 22px; color: #FFFFFF; letter-spacing: 0.3px;
  visibility: {t_vis};
}}

/* 4 Gold Stat Cards (2x2 clean grid, left middle) */
.stats-bg {{
  position: absolute; top: 462px; left: 54px; width: 642px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 18px;
  visibility: {d_vis};
}}
.stat-card-bg {{
  height: 132px; border-radius: 22px;
  background: rgba(255,255,255,0.93);
  border: 2.5px solid #D9B45A;
  box-shadow: 0 10px 24px rgba(8,56,37,0.11);
}}
.stats-txt {{
  position: absolute; top: 462px; left: 54px; width: 642px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 18px;
  visibility: {t_vis};
}}
.stat-card-txt {{
  height: 132px; padding: 16px 20px; display: flex; flex-direction: column; justify-content: center;
}}
.st-num {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 40px; line-height: 1.05;
  color: #064D33; letter-spacing: -0.5px;
}}
.st-num span {{ font-size: 24px; color: #C27408; }}
.st-lbl {{
  font-family: 'BeVNSemi', sans-serif; font-size: 20px; line-height: 1.24; color: #243C32; margin-top: 4px;
}}

/* Price & CTKM floating card beside real AV Protein box (bottom center-left, zero overlap on Bé Mẫu glass) */
.price-card-bg {{
  position: absolute; top: 1084px; left: 492px; width: 396px; height: 244px;
  border-radius: 28px;
  background: linear-gradient(155deg, rgba(255,255,255,0.97) 0%, rgba(255,248,230,0.97) 100%);
  border: 3.5px solid #E4B23E;
  box-shadow: 0 16px 34px rgba(10,48,32,0.22);
  visibility: {d_vis};
}}
.price-promo-bar-bg {{
  position: absolute; top: 1246px; left: 510px; width: 360px; height: 64px; border-radius: 16px;
  background: linear-gradient(135deg, #E6222B 0%, #AA0A16 100%);
  border: 2px solid #FFE285;
  box-shadow: 0 8px 18px rgba(170,10,22,0.32);
  visibility: {d_vis};
}}
.price-card-txt {{
  position: absolute; top: 1084px; left: 492px; width: 396px; height: 244px;
  padding: 20px 18px 18px; display: flex; flex-direction: column; align-items: center; justify-content: space-between;
  visibility: {t_vis};
}}
.pc-top {{ text-align: center; }}
.pc-name {{ font-family: 'BeVNExtra', sans-serif; font-size: 21px; color: #074C32; letter-spacing: 0.4px; }}
.pc-price {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 56px; line-height: 1.05;
  color: #0B40A8; letter-spacing: -1px; margin-top: 4px;
}}
.pc-spec {{ font-family: 'BeVNSemi', sans-serif; font-size: 16.5px; color: #364F44; margin-top: 6px; white-space: nowrap; }}
.pc-promo {{
  height: 64px; width: 360px; display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center;
}}
.pc-p1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 17px; color: #FFF3B0; line-height: 1.15; }}
.pc-p2 {{ font-family: 'BeVNExtra', sans-serif; font-size: 20px; color: #FFFFFF; line-height: 1.18; }}

/* Bottom emerald brand & legal bar */
.ftr-bg {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 118px;
  background: linear-gradient(90deg, #04291B 0%, #084D33 50%, #04291B 100%);
  border-top: 4px solid #E5B442;
  visibility: {d_vis};
}}
.ftr-txt {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 118px;
  padding: 0 40px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 7px;
  visibility: {t_vis};
}}
.ftr-l1 {{ font-family: 'BeVNExtra', sans-serif; font-size: 24px; color: #FCE28A; }}
.ftr-l2 {{ font-family: 'BeVNSemi', sans-serif; font-size: 21px; color: #E9F6EF; }}
</style>
</head>
<body>
  <div class="left-wash"></div>

  <div class="top-row-bg">
    <div class="logo-pill-bg"></div>
    <div class="tag-pill-bg"></div>
  </div>
  <div class="top-row-txt">
    <div class="logo-pill-txt"><img src="{logo_uri}" /></div>
    <div class="tag-pill-txt">✨ DINH DƯỠNG CHỦ ĐỘNG MỖI SÁNG</div>
  </div>

  <div class="headline-wrap">
    <div class="h-kicker">ĂN SÁNG ĐỦ NO</div>
    <div class="h-main">HAY ĂN CHO</div>
    <div class="h-accent">ĐỦ ĐẠM SẠCH?</div>
  </div>

  <div class="h-sub-bg"></div>
  <div class="h-sub-txt">AV PROTEIN • ĐẠM THỰC VẬT ĐẬU HÀ LAN &amp; GẠO</div>

  <div class="stats-bg">
    <div class="stat-card-bg"></div>
    <div class="stat-card-bg"></div>
    <div class="stat-card-bg"></div>
    <div class="stat-card-bg"></div>
  </div>
  <div class="stats-txt">
    <div class="stat-card-txt">
      <div class="st-num">22,05<span>g</span></div>
      <div class="st-lbl">Đạm thực vật sạch / 2 gói (30g)</div>
    </div>
    <div class="stat-card-txt">
      <div class="st-num">1.632<span>mg</span></div>
      <div class="st-lbl">L-Leucine hỗ trợ giữ cơ săn chắc</div>
    </div>
    <div class="stat-card-txt">
      <div class="st-num">1.090<span>mg</span></div>
      <div class="st-lbl">Chất xơ Inulin êm bụng dễ tiêu</div>
    </div>
    <div class="stat-card-txt">
      <div class="st-num">50<span>mg</span></div>
      <div class="st-lbl">Nguyên liệu lợi khuẩn B. breve B-3</div>
    </div>
  </div>

  <div class="price-card-bg"></div>
  <div class="price-promo-bar-bg"></div>
  <div class="price-card-txt">
    <div class="pc-top">
      <div class="pc-name">AV PROTEIN CHÍNH HÃNG</div>
      <div class="pc-price">350.000đ</div>
      <div class="pc-spec">Hộp 20 gói × 15g (300g) • Pha 20–40°C</div>
    </div>
    <div class="pc-promo">
      <div class="pc-p1">🎁 ƯU ĐÃI DROPPII 23/11 – 30/11</div>
      <div class="pc-p2">MUA 5 TẶNG 1 BOJOMI (520K)</div>
    </div>
  </div>

  <div class="ftr-bg"></div>
  <div class="ftr-txt">
    <div class="ftr-l1">🥤 30 giây bữa sáng nhẹ bụng, bền năng lượng • Hotline: 0867 399 268 • anvuongpharma.vn</div>
    <div class="ftr-l2">{LEGAL_TPBS}</div>
  </div>
</body>
</html>"""


def main():
    W, H = 1600, 1600
    logo_uri = file_to_data_uri(LOGO_ORIG)

    # Layer 1: Hero Lifestyle Photo (Bé Mẫu wearing Pastel Mint Pilates set)
    l1_bg = Image.open(HERO_IMG).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)

    # Layer 3 (decor wash + cards): render decor HTML
    h_dec = os.path.join(TMP_DIR, "post_decor.html")
    p_dec = os.path.join(TMP_DIR, "post_decor.png")
    with open(h_dec, "w", encoding="utf-8") as f:
        f.write(build_html(logo_uri, "decor"))
    l3_dec = render_html_rgba(h_dec, p_dec, W, H)

    # Layer 2: 100% REAL IS-Net AV Protein box standing cleanly on the left marble counter
    l2_prod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    place_box_on_marble(l2_prod, BOX_AV_PRO, cx=262, bottom_y=1428, target_h=608)

    # Layer 4: Crisp Vietnamese typography, logo, price & legal disclaimer
    h_txt = os.path.join(TMP_DIR, "post_text.html")
    p_txt = os.path.join(TMP_DIR, "post_text.png")
    with open(h_txt, "w", encoding="utf-8") as f:
        f.write(build_html(logo_uri, "text"))
    l4_txt = render_html_rgba(h_txt, p_txt, W, H)

    # Composite in proper depth order: Hero -> Decor Cards -> Real Product Box (foreground!) -> Text
    comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    comp.alpha_composite(l1_bg)
    comp.alpha_composite(l3_dec)
    comp.alpha_composite(l2_prod)
    comp.alpha_composite(l4_txt)

    fname = "261124 AVPM Bai Thiet Ke N01 - AV Protein Do Tap Xanh Mint"
    jpg_out = os.path.join(OUT_DIR, f"{fname}.jpg")
    psd_out = os.path.join(OUT_DIR, f"{fname}.psd")

    ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.05).save(
        jpg_out, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES
    )
    save_psd([
        ("01_Anh_Mau_USP_Do_Tap_Xanh_Mint", l1_bg),
        ("02_Khung_The_Thong_So_Va_Badges", l3_dec),
        ("03_Hop_AV_Protein_That_ISNet", l2_prod),
        ("04_Logo_Tieu_De_Gia_Va_Phap_Ly", l4_txt),
    ], psd_out, W, H)
    print(f"[DONE POST N01] {jpg_out} + {psd_out}")


if __name__ == "__main__":
    main()
