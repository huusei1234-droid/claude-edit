# -*- coding: utf-8 -*-
"""
AN VƯỢNG PHARMA — 7 COMMERCIAL STUDIO BANNERS & 4-LAYER PSD ENGINE
- 6 CTKM Banners (23/11 – 30/11/2026, Droppii Mừng Sinh Nhật 8 Tuổi, 1600x1600 sRGB)
  100% REAL IS-Net product box cutouts (0% AI spelling errors on packaging!)
- 1 Droppii 3-Step Combo Ordering Guide Card (1600x2000 sRGB, prevents wrong SKU orders)
- Exports Master .JPG (98%, sRGB ICC) + Editable 4-Layer .PSD + QC Contact Sheet
"""
import base64, math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import packbits
import pytoshop
import pytoshop.codecs
pytoshop.codecs.packbits = packbits
from pytoshop.user import nested_layers
from pytoshop import enums

PROJ_DIR   = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand"
STAGE_DIR  = os.path.join(PROJ_DIR, "assets_stage")
CUT_DIR    = r"d:\AI\full studio\projects\av_htpm_26_posters_2211\assets\cutouts"
LOGO_ORIG  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\An vượng\Logo AN Vượng Pharma Xanh Vàng.png"
FONTS_DIR  = r"d:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi"

HTML_DIR   = os.path.join(PROJ_DIR, "tmp_html_banners")
OUT_BANNERS = os.path.join(PROJ_DIR, "01_Bo_6_Banner_CTKM_23_30_11_Va_The_Len_Don")
OUT_PSD     = os.path.join(OUT_BANNERS, "File_PSD_Chinh_Sua_Da_Layer")
AUDIT_DIR   = os.path.join(PROJ_DIR, "audit")

for d in (HTML_DIR, OUT_BANNERS, OUT_PSD, AUDIT_DIR):
    os.makedirs(d, exist_ok=True)

SRGB_PROFILE = ImageCms.createProfile("sRGB")
SRGB_BYTES   = ImageCms.ImageCmsProfile(SRGB_PROFILE).tobytes()

LEGAL_TPBS = "Thực phẩm bổ sung. Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh."

def find_browser_exe() -> str:
    for c in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ]:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("No Chromium browser found!")

BROWSER_EXE = find_browser_exe()

def file_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")

def tight_crop_rgba(im: Image.Image, alpha_thresh: int = 35, pad: int = 4) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    ys, xs = np.where(arr[:, :, 3] > alpha_thresh)
    if len(xs) == 0:
        return im.convert("RGBA")
    return im.convert("RGBA").crop((
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(im.width, int(xs.max()) + 1 + pad),
        min(im.height, int(ys.max()) + 1 + pad),
    ))

def polish_box(im: Image.Image) -> Image.Image:
    im = tight_crop_rgba(im)
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Brightness(rgb).enhance(1.03)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.05)
    rgb = ImageEnhance.Color(rgb).enhance(1.05)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.14)
    r2, g2, b2 = rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))

def build_collamela_10goi_box(src_path: str) -> Image.Image:
    """Creates an honest, crisp Collamela 10-sachet (40g) gift box from the real 20-sachet box cutout."""
    im = polish_box(Image.open(src_path))
    w, h = im.size
    # Cleanly update the bottom-right yellow badge area ("20 gói x 4g / 80g" -> "10 gói x 4g / 40g")
    # Locate the small yellow spec rectangle on the right side of the lower dark-green band
    arr = np.array(im)
    # In av03_collamela_b.png (tight-cropped), the yellow spec box sits roughly at x: 75%..95%, y: 74%..87%
    x0, y0, x1, y1 = int(w * 0.77), int(h * 0.72), int(w * 0.96), int(h * 0.87)
    sub = arr[y0:y1, x0:x1]
    # Detect warm-yellow pixels of that small spec tag
    ymask = (sub[:, :, 3] > 200) & (sub[:, :, 0] > 180) & (sub[:, :, 1] > 155) & (sub[:, :, 2] < 130)
    ys, xs = np.where(ymask)
    if len(xs) > 120:
        bx0 = x0 + int(xs.min()) - 4
        by0 = y0 + int(ys.min()) - 4
        bx1 = x0 + int(xs.max()) + 4
        by1 = y0 + int(ys.max()) + 4
        draw = ImageDraw.Draw(im)
        # Repaint the small spec badge cleanly in deep emerald + gold border with "10 gói x 4g / 40 g"
        bw, bh = bx1 - bx0, by1 - by0
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=max(6, bw // 14), fill=(11, 66, 42, 255), outline=(235, 198, 92, 255), width=max(3, bw // 40))
        top_h = int(bh * 0.44)
        draw.rounded_rectangle([bx0 + 3, by0 + 3, bx1 - 3, by0 + top_h], radius=max(4, bw // 18), fill=(242, 206, 98, 255))
        try:
            f_top = ImageFont.truetype(os.path.join(FONTS_DIR.replace("/", os.sep), "Montserrat-ExtraBold.ttf"), max(14, int(bh * 0.24)))
            f_bot = ImageFont.truetype(os.path.join(FONTS_DIR.replace("/", os.sep), "Montserrat-Bold.ttf"), max(14, int(bh * 0.28)))
        except Exception:
            f_top = f_bot = ImageFont.load_default()
        draw.text((bx0 + bw // 2, by0 + top_h // 2 + 1), "10 gói x 4g", fill=(8, 48, 30, 255), font=f_top, anchor="mm")
        draw.text((bx0 + bw // 2, by0 + top_h + (bh - top_h) // 2), "40 g", fill=(248, 224, 132, 255), font=f_bot, anchor="mm")
    return im

def load_all_boxes() -> dict:
    return {
        "protein":    polish_box(Image.open(os.path.join(CUT_DIR, "av01_protein_a.png"))),
        "protein_fr": polish_box(Image.open(os.path.join(CUT_DIR, "av01_protein_b.png"))),
        "bojomi":     polish_box(Image.open(os.path.join(CUT_DIR, "av02_bojomi_b.png"))),
        "collamela":  polish_box(Image.open(os.path.join(CUT_DIR, "av03_collamela_b.png"))),
        "colla10":    build_collamela_10goi_box(os.path.join(CUT_DIR, "av03_collamela_b.png")),
        "curcumilk":  polish_box(Image.open(os.path.join(CUT_DIR, "av04_curcumilk_b.png"))),
    }

def paste_box_with_shadow(layer: Image.Image, box_im: Image.Image, cx: int, bottom_y: int, target_h: int,
                          shadow_alpha: int = 135, reflect: bool = True, tilt_deg: float = 0.0):
    """Places a real product box squarely on the podium with grounded AO shadow + subtle glossy reflection."""
    scale = target_h / box_im.height
    nw, nh = max(10, int(round(box_im.width * scale))), max(10, int(round(target_h)))
    im = box_im.resize((nw, nh), Image.Resampling.LANCZOS)
    if abs(tilt_deg) > 0.1:
        im = im.rotate(tilt_deg, resample=Image.Resampling.BICUBIC, expand=True)
        nw, nh = im.size

    x0 = int(round(cx - nw / 2))
    y0 = int(round(bottom_y - nh))

    # 1. Soft studio mirror reflection below podium contact line
    if reflect:
        ref = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        ref_h = min(nh // 4, 85)
        ref = ref.crop((0, 0, nw, ref_h))
        r_arr = np.array(ref, dtype=np.float32)
        grad = np.linspace(0.18, 0.0, ref_h, dtype=np.float32)[:, None]
        r_arr[:, :, 3] = np.clip(r_arr[:, :, 3] * grad, 0, 255)
        ref_im = Image.fromarray(r_arr.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(2.2))
        layer.alpha_composite(ref_im, (x0, bottom_y - 6))

    # 2. Grounded elliptical AO + soft drop shadow
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh, "RGBA")
    ell_w = int(nw * 0.92)
    ell_h = max(18, int(nw * 0.14))
    d.ellipse([cx - ell_w // 2, bottom_y - ell_h // 2 + 2, cx + ell_w // 2, bottom_y + ell_h // 2 + 6],
              fill=(18, 32, 58, shadow_alpha))
    d.ellipse([cx - int(ell_w * 0.42), bottom_y - ell_h // 3, cx + int(ell_w * 0.42), bottom_y + ell_h // 3 + 2],
              fill=(10, 18, 36, min(200, shadow_alpha + 40)))
    sh = sh.filter(ImageFilter.GaussianBlur(13))
    layer.alpha_composite(sh)

    # 3. Crisp box
    layer.alpha_composite(im, (x0, y0))
    return (x0, y0, x0 + nw, y0 + nh)

def render_html_to_rgba(html_path: str, out_png: str, w: int, h: int) -> Image.Image:
    raw_png = out_png.replace(".png", "_2x.png")
    cmd = [
        BROWSER_EXE,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        "--force-device-scale-factor=2",
        "--default-background-color=00000000",
        f"--screenshot={raw_png}",
        f"file:///{html_path.replace(os.sep, '/')}",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(raw_png).convert("RGBA")
    if im.size != (w, h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    im.save(out_png)
    try:
        os.remove(raw_png)
    except OSError:
        pass
    return im

def save_multilayer_psd(layers_named: list, out_psd_path: str, w: int, h: int):
    psd_layers = []
    for name, im_rgba in reversed(layers_named):
        arr = np.array(im_rgba.convert("RGBA"), dtype=np.uint8)
        channels = {
            0: arr[:, :, 0],
            1: arr[:, :, 1],
            2: arr[:, :, 2],
            -1: arr[:, :, 3],
        }
        psd_layers.append(
            nested_layers.Image(
                name=name,
                visible=True,
                opacity=255,
                group_id=0,
                blend_mode=enums.BlendMode.normal,
                top=0,
                left=0,
                bottom=h,
                right=w,
                channels=channels,
            )
        )
    psd = nested_layers.nested_layers_to_psd(
        psd_layers,
        color_mode=enums.ColorMode.rgb,
        size=(w, h),
        compression=enums.Compression.rle,
    )
    with open(out_psd_path, "wb") as f:
        psd.write(f)

def font_faces_css() -> str:
    return f"""
    @font-face {{ font-family: 'MontBlack'; src: url('file:///{FONTS_DIR}/Montserrat-Black.ttf'); font-weight: 900; }}
    @font-face {{ font-family: 'MontEB'; src: url('file:///{FONTS_DIR}/Montserrat-ExtraBold.ttf'); font-weight: 800; }}
    @font-face {{ font-family: 'MontBold'; src: url('file:///{FONTS_DIR}/Montserrat-Bold.ttf'); font-weight: 700; }}
    @font-face {{ font-family: 'BeVNExtra'; src: url('file:///{FONTS_DIR}/BeVietnamPro-ExtraBold.ttf'); font-weight: 800; }}
    @font-face {{ font-family: 'BeVNBold'; src: url('file:///{FONTS_DIR}/BeVietnamPro-Bold.ttf'); font-weight: 700; }}
    @font-face {{ font-family: 'BeVNSemi'; src: url('file:///{FONTS_DIR}/BeVietnamPro-SemiBold.ttf'); font-weight: 600; }}
    @font-face {{ font-family: 'PlayfairEB'; src: url('file:///{FONTS_DIR}/PlayfairDisplay-BoldItalic.ttf'); font-weight: 700; font-style: italic; }}
    @font-face {{ font-family: 'FrauncesBlk'; src: url('file:///{FONTS_DIR}/Fraunces-Black.ttf'); font-weight: 900; }}
    """

# =============================================================================
# 6 VERIFIED CTKM BANNERS (23/11/2026 – 30/11/2026)
# =============================================================================
CTKM_BANNERS = [
    {
        "id": "CTKM_01",
        "filename": "261123 AVPM CTKM 01 - Combo 4 San Pham Tang Collamela 20 Goi",
        "offer_left": "MUA COMBO",
        "offer_right_html": """
            <div class="combo-list">
              <div class="cl-title">Gồm 4 sản phẩm chính hãng:</div>
              <div class="cl-grid">
                <span>✓ 1 Hộp AV Protein</span>
                <span>✓ 1 Hộp BOJOMI</span>
                <span>✓ 1 Hộp Collamela (20 gói)</span>
                <span>✓ 1 Hộp Curcumilk Phyto</span>
              </div>
            </div>
        """,
        "boxes": [
            # Top tier (100% unobstructed face)
            ("protein",   345, 838, 355, 85, False),
            ("bojomi",    705, 838, 355, 85, False),
            # Bottom tier (grounded on marble podium y=1176)
            ("collamela", 345, 1176, 365, 140, True),
            ("curcumilk", 705, 1176, 365, 140, True),
        ],
        "plus_pos": (995, 955),
        "gift_box": ("collamela", 1265, 1175, 475, 145, True),
        "gift_subtag": "HỘP 20 GÓI × 4G",
        "gift_value": "920.000đ",
        "price_label": "Tổng Combo<br>4 sản phẩm",
        "price_val": "2.440.000đ",
        "save_val": "920.000đ",
        "date_str": "Từ 23/11/2026 đến hết ngày 30/11/2026",
        "pillars": [
            ("💪", "BỔ SUNG ĐẠM<br>THỰC VẬT"),
            ("🦴", "HỖ TRỢ<br>XƯƠNG KHỚP"),
            ("✨", "HỖ TRỢ DA ẨM<br>MỊN, ĐÀN HỒI"),
            ("🌿", "HỖ TRỢ TIÊU<br>HÓA ÊM DỊU"),
        ],
    },
    {
        "id": "CTKM_02",
        "filename": "261123 AVPM CTKM 02 - Mua 5 Hop AV Protein Tang 1 Bojomi",
        "offer_left": "MUA <b>5</b> HỘP",
        "offer_right_html": '<div class="prod-big emerald">AV PROTEIN <span class="spec-chip">20 gói × 15g</span></div>',
        "boxes": [
            # 2 top tier (cleanly resting on top of 3 bottom boxes — all 5 faces 100% readable!)
            ("protein", 378, 845, 345, 85, False),
            ("protein", 658, 845, 345, 85, False),
            # 3 bottom tier grounded on marble
            ("protein", 245, 1176, 355, 135, True),
            ("protein", 518, 1180, 360, 140, True),
            ("protein", 790, 1176, 355, 135, True),
        ],
        "plus_pos": (1005, 955),
        "gift_box": ("bojomi", 1265, 1176, 480, 145, True),
        "gift_subtag": "HỘP 14 GÓI × 20G",
        "gift_value": "520.000đ",
        "price_label": "Tổng 5 hộp<br>AV Protein",
        "price_val": "1.750.000đ",
        "save_val": "520.000đ",
        "date_str": "Từ 23/11/2026 đến hết ngày 30/11/2026",
        "pillars": None,
    },
    {
        "id": "CTKM_03",
        "filename": "261123 AVPM CTKM 03 - Mua 3 Hop Bojomi Tang 1 Bojomi",
        "offer_left": "MUA <b>3</b> HỘP",
        "offer_right_html": '<div class="prod-stack"><span class="ps-sub">Sữa Dinh Dưỡng Xương Khớp</span><span class="ps-main">BOJOMI</span></div>',
        "boxes": [
            # 1 top pyramid center box (100% unobstructed face!)
            ("bojomi", 520, 842, 360, 90, False),
            # 2 bottom tier grounded on marble
            ("bojomi", 340, 1178, 375, 140, True),
            ("bojomi", 700, 1178, 375, 140, True),
        ],
        "plus_pos": (995, 955),
        "gift_box": ("bojomi", 1265, 1176, 485, 145, True),
        "gift_subtag": "TỔNG NHẬN 4 HỘP",
        "gift_value": "520.000đ",
        "price_label": "Tổng 3 hộp<br>BOJOMI",
        "price_val": "1.560.000đ",
        "save_val": "520.000đ",
        "date_str": "Từ 23/11/2026 đến hết ngày 30/11/2026",
        "pillars": None,
    },
    {
        "id": "CTKM_04",
        "filename": "261123 AVPM CTKM 04 - Mua 4 Hop Curcumilk Phyto Tang 1 Curcumilk",
        "offer_left": "MUA <b>4</b> HỘP",
        "offer_right_html": '<div class="prod-stack"><span class="ps-sub">Sữa Nghệ Công Nghệ Phytosome</span><span class="ps-main">CURCUMILK PHYTO</span></div>',
        "boxes": [
            # 2 top tier (clean 2x2 retail stack — all 4 faces 100% readable!)
            ("curcumilk", 355, 840, 355, 85, False),
            ("curcumilk", 695, 840, 355, 85, False),
            # 2 bottom tier
            ("curcumilk", 345, 1178, 368, 140, True),
            ("curcumilk", 705, 1178, 368, 140, True),
        ],
        "plus_pos": (995, 955),
        "gift_box": ("curcumilk", 1265, 1176, 485, 145, True),
        "gift_subtag": "TỔNG NHẬN 5 HỘP",
        "gift_value": "650.000đ",
        "price_label": "Tổng 4 hộp<br>Curcumilk Phyto",
        "price_val": "2.600.000đ",
        "save_val": "650.000đ",
        "date_str": "Từ 23/11/2026 đến hết ngày 30/11/2026",
        "pillars": None,
    },
    {
        "id": "CTKM_05",
        "filename": "261123 AVPM CTKM 05 - Mua 2 Hop Collamela 20 Goi Tang 1 Hop 10 Goi",
        "offer_left": "MUA <b>2</b> HỘP",
        "offer_right_html": '<div class="prod-stack"><span class="ps-sub">Collagen Tripeptide (20 gói × 4g)</span><span class="ps-main">COLLAMELA</span></div>',
        "boxes": [
            # 2 hero Collamela 20-sachet boxes side by side
            ("collamela", 345, 1178, 485, 140, True),
            ("collamela", 720, 1178, 485, 140, True),
        ],
        "plus_pos": (1002, 955),
        "gift_box": ("colla10", 1272, 1176, 418, 145, True),
        "gift_subtag": "HỘP 10 GÓI × 4G (40G)",
        "gift_value": "480.000đ",
        "price_label": "Tổng 2 hộp<br>Collamela (20 gói)",
        "price_val": "1.840.000đ",
        "save_val": "480.000đ",
        "date_str": "Từ 23/11/2026 đến hết ngày 30/11/2026",
        "pillars": None,
    },
    {
        "id": "CTKM_06",
        "filename": "261123 AVPM CTKM 06 - Combo 2 Bojomi 2 Curcumilk Tang 1 Bojomi",
        "offer_left": "MUA COMBO",
        "offer_right_html": '<div class="prod-stack"><span class="ps-sub">Chăm Sóc Xương Khớp & Tiêu Hóa</span><span class="ps-main sm">2 BOJOMI + 2 CURCUMILK PHYTO</span></div>',
        "boxes": [
            # 2 Bojomi top tier (100% readable BOJOMI labels!)
            ("bojomi",    355, 840, 355, 85, False),
            ("bojomi",    695, 840, 355, 85, False),
            # 2 Curcumilk bottom tier
            ("curcumilk", 345, 1178, 368, 140, True),
            ("curcumilk", 705, 1178, 368, 140, True),
        ],
        "plus_pos": (995, 955),
        "gift_box": ("bojomi", 1265, 1176, 485, 145, True),
        "gift_subtag": "HỘP 14 GÓI × 20G",
        "gift_value": "520.000đ",
        "price_label": "Combo 2 Bojomi<br>+ 2 Curcumilk",
        "price_val": "2.340.000đ",
        "save_val": "520.000đ",
        "date_str": "Từ 23/11/2026 đến hết ngày 30/11/2026",
        "pillars": None,
    },
]

def build_ctkm_html(spec: dict, logo_uri: str, gift_bbox: tuple, pass_mode: str) -> str:
    """
    pass_mode = 'decor' (ribbons, plus sign, frames, price capsules)
             or 'text'  (logos, headlines, numbers, gift badges, legal disclaimer)
    Clean separation for editable 4-layer PSD!
    """
    gx0, gy0, gx1, gy1 = gift_bbox
    gcx = (gx0 + gx1) // 2
    px, py = spec["plus_pos"]
    has_pillars = bool(spec.get("pillars"))

    # Shift bottom bars cleanly below the golden marble podium rim (y=1215..1310)
    price_top = 1218 if has_pillars else 1272
    date_top  = 1458 if has_pillars else 1438

    pillars_html = ""
    if has_pillars:
        items = "".join([
            f'<div class="pil-item"><div class="pil-ico">{ico}</div><div class="pil-txt">{txt}</div></div>'
            for ico, txt in spec["pillars"]
        ])
        pillars_html = f'<div class="pillars-row">{items}</div>'

    is_decor = (pass_mode == "decor")
    decor_vis = "visible" if is_decor else "hidden"
    text_vis  = "hidden"  if is_decor else "visible"

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<style>
{font_faces_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1600px; height: 1600px; overflow: hidden;
  background: transparent; position: relative;
  font-family: 'BeVNBold', sans-serif;
  -webkit-font-smoothing: antialiased;
}}

/* ---- TOP CO-BRAND BAR (KEEPS BALLOONS & GIFT BOX 100% VISIBLE) ---- */
.cobrand-bar {{
  position: absolute; top: 20px; left: 0; right: 0;
  display: flex; align-items: center; justify-content: center; gap: 22px;
  visibility: {text_vis};
}}
.av-logo-chip {{
  background: rgba(255,255,255,0.92);
  border: 2.5px solid rgba(226,184,78,0.85);
  border-radius: 999px; padding: 8px 26px;
  box-shadow: 0 8px 22px rgba(12,48,118,0.14);
  display: flex; align-items: center;
}}
.av-logo-chip img {{ height: 68px; width: auto; display: block; }}
.cobrand-x {{
  font-family: 'MontBlack', sans-serif; font-size: 38px; color: #D99B1C;
  text-shadow: 0 2px 0 #FFFFFF;
}}
.droppii-brand {{
  font-family: 'MontBlack', sans-serif; font-size: 68px; letter-spacing: -2px;
  color: #134DC6; line-height: 1;
  text-shadow: 0 4px 0 #FFFFFF, 0 8px 20px rgba(19,77,198,0.18);
}}
.droppii-dot {{
  display: inline-block; width: 14px; height: 14px; border-radius: 50%;
  background: linear-gradient(135deg, #FF7A2F, #E62E2D);
  margin-left: 2px; vertical-align: super; transform: translateY(-18px);
}}

/* ---- MAIN CELEBRATION HEADER ---- */
.bday-row {{
  position: absolute; top: 108px; left: 0; right: 0;
  display: flex; align-items: center; justify-content: center; gap: 18px;
  visibility: {text_vis};
}}
.bday-script {{
  font-family: 'PlayfairEB', serif; font-size: 98px; line-height: 1.08;
  background: linear-gradient(180deg, #1757D6 0%, #0A2E8A 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 0 #FFFFFF) drop-shadow(0 8px 18px rgba(10,46,138,0.22));
  padding-right: 8px;
}}
.gold-eight-wrap {{
  position: relative; display: inline-flex; align-items: center; margin-top: -18px;
}}
.gold-eight-back {{
  position: absolute; left: 0; top: 5px; padding: 10px 6px;
  font-family: 'FrauncesBlk', serif; font-size: 164px; line-height: 1.05;
  color: #8A5308;
  -webkit-text-stroke: 10px #FFFFFF;
  filter: drop-shadow(0 10px 18px rgba(128,72,6,0.34));
}}
.gold-eight-front {{
  position: relative; z-index: 2; padding: 10px 6px;
  font-family: 'FrauncesBlk', serif; font-size: 164px; line-height: 1.05;
  background: linear-gradient(180deg, #FFFCE0 0%, #FCE078 28%, #D99214 62%, #FFF3B0 84%, #AE6C08 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  -webkit-text-stroke: 2px rgba(255,248,210,0.65);
}}
.tuoi-pill {{
  margin-left: -6px; margin-top: 24px;
  background: linear-gradient(135deg, #2578F0 0%, #0E45B8 100%);
  color: #FFFFFF; font-family: 'BeVNExtra', sans-serif; font-size: 36px;
  padding: 10px 26px; border-radius: 999px;
  border: 3px solid #FFFFFF;
  box-shadow: 0 8px 18px rgba(14,69,184,0.32);
  transform: rotate(-6deg);
}}

/* ---- OFFER TITLE CAPSULE ---- */
.offer-pill-bg {{
  position: absolute; top: 274px; left: 106px; right: 106px; height: 138px;
  background: linear-gradient(180deg, #FFFFFF 0%, #FFF8E6 100%);
  border: 4px solid #E5B342; border-radius: 70px;
  box-shadow: 0 14px 32px rgba(12,48,118,0.16), inset 0 2px 0 #FFFFFF;
  visibility: {decor_vis};
}}
.offer-pill-content {{
  position: absolute; top: 274px; left: 106px; right: 106px; height: 138px;
  display: flex; align-items: center; justify-content: center; gap: 30px; padding: 0 42px;
  visibility: {text_vis};
}}
.offer-left {{
  font-family: 'MontBlack', sans-serif; font-size: 54px; letter-spacing: -0.5px;
  color: #103FA8; white-space: nowrap;
  display: flex; align-items: baseline; gap: 10px;
}}
.offer-left b {{
  font-size: 86px; color: #D91E2A; line-height: 0.9;
  text-shadow: 0 4px 10px rgba(217,30,42,0.22);
}}
.offer-div {{
  width: 4px; height: 76px; border-radius: 4px;
  background: linear-gradient(180deg, #E6B442, #0C5A3B);
  flex-shrink: 0;
}}
.prod-big {{
  font-family: 'MontBlack', sans-serif; font-size: 62px; color: #053A25;
  display: flex; align-items: center; gap: 18px; letter-spacing: -0.5px;
}}
.spec-chip {{
  font-family: 'BeVNBold', sans-serif; font-size: 24px; color: #FFFFFF;
  background: #0B5B3E; padding: 8px 18px; border-radius: 999px;
}}
.prod-stack {{
  display: flex; flex-direction: column; align-items: flex-start; line-height: 1.08;
}}
.ps-sub {{
  font-family: 'BeVNSemi', sans-serif; font-size: 28px; color: #0D5E3F;
}}
.ps-main {{
  font-family: 'MontBlack', sans-serif; font-size: 56px; color: #053824; letter-spacing: -0.5px;
}}
.ps-main.sm {{ font-size: 42px; }}

.combo-list {{ display: flex; flex-direction: column; gap: 6px; }}
.cl-title {{ font-family: 'BeVNExtra', sans-serif; font-size: 23px; color: #0B5B3E; text-transform: uppercase; letter-spacing: 0.6px; }}
.cl-grid {{
  display: grid; grid-template-columns: auto auto; gap: 4px 26px;
  font-family: 'BeVNBold', sans-serif; font-size: 25px; color: #092B5A;
}}

/* ---- PLUS SIGN ---- */
.plus-sign {{
  position: absolute; left: {px - 44}px; top: {py - 44}px; width: 88px; height: 88px;
  display: flex; align-items: center; justify-content: center;
  visibility: {decor_vis};
}}
.plus-circle {{
  width: 82px; height: 82px; border-radius: 50%;
  background: linear-gradient(145deg, #FF3B3B 0%, #B80D1B 100%);
  border: 5px solid #FFFFFF;
  box-shadow: 0 10px 24px rgba(184,13,27,0.38);
  display: flex; align-items: center; justify-content: center;
  color: #FFFFFF; font-family: 'MontBlack', sans-serif; font-size: 62px; line-height: 1;
}}

/* ---- GIFT RIBBON BANNER & VALUE STARBURST ON GIFT BOX ---- */
.gift-top-ribbon {{
  position: absolute; left: {gcx - 165}px; top: {max(435, gy0 - 134)}px; width: 330px;
  display: flex; flex-direction: column; align-items: center;
  visibility: {decor_vis};
}}
.gift-bow-svg {{ width: 178px; height: 80px; margin-bottom: -14px; filter: drop-shadow(0 8px 12px rgba(140,10,20,0.36)); }}
.gift-tang-pill-bg {{
  width: 296px; height: 66px; border-radius: 33px;
  background: linear-gradient(135deg, #F02832 0%, #B50B18 100%);
  border: 4px solid #FFE28A;
  box-shadow: 0 10px 22px rgba(181,11,24,0.42);
  transform: rotate(-3deg);
}}
.gift-tang-text {{
  position: absolute; left: {gcx - 148}px; top: {max(435, gy0 - 134) + 66}px;
  width: 296px; height: 66px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'MontBlack', sans-serif; font-size: 40px; letter-spacing: 3px;
  color: #FFFFFF; text-shadow: 0 3px 6px rgba(90,0,8,0.45);
  transform: rotate(-3deg);
  visibility: {text_vis};
}}

.gift-subtag-bg {{
  position: absolute; left: {gcx - 142}px; top: {gy1 - 12}px; width: 284px; height: 40px;
  background: #06452D; border: 2.5px solid #F4CC62; border-radius: 999px;
  box-shadow: 0 6px 14px rgba(5,40,26,0.32);
  visibility: {decor_vis};
}}
.gift-subtag-txt {{
  position: absolute; left: {gcx - 142}px; top: {gy1 - 12}px; width: 284px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'BeVNExtra', sans-serif; font-size: 20px; letter-spacing: 0.6px; color: #FFF4C2;
  visibility: {text_vis};
}}

.gift-val-badge-bg {{
  position: absolute; left: {min(1300, gx1 - 105)}px; top: {gy1 - 188}px; width: 256px; height: 128px;
  background: linear-gradient(145deg, #FF2A32 0%, #AD0916 100%);
  border: 4.5px solid #FFE48A; border-radius: 30px;
  box-shadow: 0 14px 28px rgba(145,8,20,0.42);
  transform: rotate(-7deg);
  visibility: {decor_vis};
}}
.gift-val-badge-txt {{
  position: absolute; left: {min(1300, gx1 - 105)}px; top: {gy1 - 188}px; width: 256px; height: 128px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transform: rotate(-7deg);
  visibility: {text_vis};
}}
.gv-k {{ font-family: 'BeVNBold', sans-serif; font-size: 26px; color: #FFF3B8; line-height: 1.05; }}
.gv-v {{ font-family: 'MontBlack', sans-serif; font-size: 44px; color: #FFFFFF; line-height: 1.08; text-shadow: 0 3px 8px rgba(80,0,8,0.45); }}

/* ---- PRICE & SAVINGS ROW ---- */
.price-row-bg {{
  position: absolute; top: {price_top}px; left: 96px; right: 96px; height: 144px;
  display: flex; align-items: center; justify-content: space-between; gap: 22px;
  visibility: {decor_vis};
}}
.price-cap-bg {{
  flex: 1; height: 126px; border-radius: 63px;
  background: linear-gradient(180deg, #FFFFFF 0%, #FFF7E0 100%);
  border: 4px solid #E5B23E;
  box-shadow: 0 12px 28px rgba(12,48,118,0.16);
}}
.save-cap-bg {{
  width: 455px; height: 138px; border-radius: 34px;
  background: linear-gradient(145deg, #F5262E 0%, #AD0A16 100%);
  border: 5px solid #FFE284;
  box-shadow: 0 14px 28px rgba(173,10,22,0.36);
  transform: rotate(-2deg);
}}

.price-row-txt {{
  position: absolute; top: {price_top}px; left: 96px; right: 96px; height: 144px;
  display: flex; align-items: center; justify-content: space-between; gap: 22px;
  visibility: {text_vis};
}}
.price-cap-txt {{
  flex: 1; height: 126px; padding: 0 42px;
  display: flex; align-items: center; justify-content: center; gap: 26px;
}}
.p-lbl {{ font-family: 'BeVNExtra', sans-serif; font-size: 32px; color: #0B368A; line-height: 1.15; text-align: right; }}
.p-div {{ width: 3.5px; height: 68px; background: #D9A534; border-radius: 2px; }}
.p-num {{ font-family: 'MontBlack', sans-serif; font-size: 74px; color: #0D389C; letter-spacing: -1.5px; }}
.save-cap-txt {{
  width: 455px; height: 138px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transform: rotate(-2deg);
}}
.s-lbl {{ font-family: 'BeVNExtra', sans-serif; font-size: 32px; color: #FFF1AE; line-height: 1.05; }}
.s-num {{ font-family: 'MontBlack', sans-serif; font-size: 64px; color: #FFFFFF; letter-spacing: -1px; text-shadow: 0 4px 10px rgba(80,0,8,0.4); line-height: 1.05; }}

/* ---- 4 BENEFIT PILLARS (ONLY BANNER 01) ---- */
.pillars-row {{
  position: absolute; top: 1364px; left: 96px; right: 96px; height: 82px;
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  visibility: {text_vis};
}}
.pil-item {{
  background: rgba(255,255,255,0.94); border: 2.5px solid #BBD6F8; border-radius: 20px;
  display: flex; align-items: center; gap: 12px; padding: 8px 14px;
  box-shadow: 0 6px 14px rgba(15,58,138,0.12);
}}
.pil-ico {{
  width: 48px; height: 48px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #165AE0, #0C3A9E);
  display: flex; align-items: center; justify-content: center; font-size: 24px;
}}
.pil-txt {{ font-family: 'BeVNExtra', sans-serif; font-size: 19px; color: #083075; line-height: 1.2; }}

/* ---- DATE CAPSULE ---- */
.date-pill-bg {{
  position: absolute; top: {date_top}px; left: 265px; right: 265px; height: 72px;
  background: rgba(255,255,255,0.96);
  border: 3px solid #1C64E2; border-radius: 999px;
  box-shadow: 0 10px 24px rgba(14,62,158,0.16);
  visibility: {decor_vis};
}}
.date-pill-txt {{
  position: absolute; top: {date_top}px; left: 265px; right: 265px; height: 72px;
  display: flex; align-items: center; justify-content: center; gap: 18px;
  visibility: {text_vis};
}}
.date-badge {{
  background: linear-gradient(135deg, #195EE0, #0D3C9E); color: #FFFFFF;
  font-family: 'BeVNExtra', sans-serif; font-size: 22px; padding: 10px 20px; border-radius: 999px;
}}
.date-val {{ font-family: 'BeVNExtra', sans-serif; font-size: 30px; color: #092B6E; }}

/* ---- LEGAL FOOTER BAR ---- */
.legal-bg {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 54px;
  background: linear-gradient(90deg, #042D1E 0%, #094D34 50%, #042D1E 100%);
  border-top: 2px solid #E5B442;
  visibility: {decor_vis};
}}
.legal-txt {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 54px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'BeVNSemi', sans-serif; font-size: 22px; color: #FFF8DC; letter-spacing: 0.2px;
  visibility: {text_vis};
}}
</style>
</head>
<body>
  <div class="cobrand-bar">
    <div class="av-logo-chip"><img src="{logo_uri}" /></div>
    <span class="cobrand-x">×</span>
    <div class="droppii-brand">droppii<span class="droppii-dot"></span></div>
  </div>

  <div class="bday-row">
    <div class="bday-script">Mừng Sinh Nhật</div>
    <div class="gold-eight-wrap">
      <span class="gold-eight-back">8</span>
      <span class="gold-eight-front">8</span>
      <span class="tuoi-pill">Tuổi</span>
    </div>
  </div>

  <div class="offer-pill-bg"></div>
  <div class="offer-pill-content">
    <div class="offer-left">{spec["offer_left"]}</div>
    <div class="offer-div"></div>
    {spec["offer_right_html"]}
  </div>

  <div class="plus-sign"><div class="plus-circle">+</div></div>

  <div class="gift-top-ribbon">
    <svg class="gift-bow-svg" viewBox="0 0 180 80" fill="none">
      <defs>
        <linearGradient id="bowRed" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#FF474F"/>
          <stop offset="55%" stop-color="#D1121F"/>
          <stop offset="100%" stop-color="#8A0610"/>
        </linearGradient>
        <linearGradient id="bowGold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#FFF5C0"/>
          <stop offset="100%" stop-color="#D99B1C"/>
        </linearGradient>
      </defs>
      <path d="M90 52 C62 12, 16 6, 18 38 C20 62, 62 66, 90 52 Z" fill="url(#bowRed)" stroke="url(#bowGold)" stroke-width="3"/>
      <path d="M90 52 C118 12, 164 6, 162 38 C160 62, 118 66, 90 52 Z" fill="url(#bowRed)" stroke="url(#bowGold)" stroke-width="3"/>
      <path d="M84 54 L46 78 L62 78 L88 58 Z" fill="#A60B17"/>
      <path d="M96 54 L134 78 L118 78 L92 58 Z" fill="#A60B17"/>
      <ellipse cx="90" cy="52" rx="18" ry="15" fill="url(#bowRed)" stroke="url(#bowGold)" stroke-width="3.5"/>
    </svg>
    <div class="gift-tang-pill-bg"></div>
  </div>
  <div class="gift-tang-text">TẶNG NGAY</div>

  <div class="gift-subtag-bg"></div>
  <div class="gift-subtag-txt">{spec["gift_subtag"]}</div>

  <div class="gift-val-badge-bg"></div>
  <div class="gift-val-badge-txt">
    <div class="gv-k">Trị giá</div>
    <div class="gv-v">{spec["gift_value"]}</div>
  </div>

  <div class="price-row-bg">
    <div class="price-cap-bg"></div>
    <div class="save-cap-bg"></div>
  </div>
  <div class="price-row-txt">
    <div class="price-cap-txt">
      <div class="p-lbl">{spec["price_label"]}</div>
      <div class="p-div"></div>
      <div class="p-num">{spec["price_val"]}</div>
    </div>
    <div class="save-cap-txt">
      <div class="s-lbl">Tiết kiệm ngay</div>
      <div class="s-num">{spec["save_val"]}</div>
    </div>
  </div>

  {pillars_html}

  <div class="date-pill-bg"></div>
  <div class="date-pill-txt">
    <span class="date-badge">📅 Thời gian ưu đãi</span>
    <span class="date-val">{spec["date_str"]}</span>
  </div>

  <div class="legal-bg"></div>
  <div class="legal-txt">{LEGAL_TPBS} • Áp dụng khi chọn đúng Mã Combo trên App Droppii.</div>
</body>
</html>"""

def render_ctkm_banner(spec: dict, stage_bg: Image.Image, boxes: dict, logo_uri: str) -> dict:
    W, H = 1600, 1600
    cid = spec["id"]

    # Layer 1: Clean 3D Studio Stage Backdrop
    l1_bg = stage_bg.resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")

    # Layer 2: 100% REAL Product Box Cutouts + Shadows + Reflections
    l2_prod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for key, cx, by, th, sha, refl in spec["boxes"]:
        paste_box_with_shadow(l2_prod, boxes[key], cx, by, th, shadow_alpha=sha, reflect=refl)
    gkey, gcx, gby, gth, gsha, grefl = spec["gift_box"]
    gift_bbox = paste_box_with_shadow(l2_prod, boxes[gkey], gcx, gby, gth, shadow_alpha=gsha, reflect=grefl)

    # Layer 3: Ribbons, Plus Sign, Capsules, Badges
    h_dec = os.path.join(HTML_DIR, f"{cid}_decor.html")
    p_dec = os.path.join(HTML_DIR, f"{cid}_decor.png")
    with open(h_dec, "w", encoding="utf-8") as f:
        f.write(build_ctkm_html(spec, logo_uri, gift_bbox, "decor"))
    l3_dec = render_html_to_rgba(h_dec, p_dec, W, H)

    # Layer 4: Logos, Headlines, Prices, Disclaimer Text
    h_txt = os.path.join(HTML_DIR, f"{cid}_text.html")
    p_txt = os.path.join(HTML_DIR, f"{cid}_text.png")
    with open(h_txt, "w", encoding="utf-8") as f:
        f.write(build_ctkm_html(spec, logo_uri, gift_bbox, "text"))
    l4_txt = render_html_to_rgba(h_txt, p_txt, W, H)

    # Composite final sRGB JPG
    comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    comp.alpha_composite(l1_bg)
    comp.alpha_composite(l2_prod)
    comp.alpha_composite(l3_dec)
    comp.alpha_composite(l4_txt)

    final_rgb = ImageEnhance.Sharpness(comp.convert("RGB")).enhance(1.06)
    jpg_path = os.path.join(OUT_BANNERS, f"{spec['filename']}.jpg")
    psd_path = os.path.join(OUT_PSD, f"{spec['filename']}.psd")
    final_rgb.save(jpg_path, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES)
    save_multilayer_psd([
        ("01_Nen_San_Khau_Sinh_Nhat_3D", l1_bg),
        ("02_Hop_San_Pham_That_ISNet", l2_prod),
        ("03_No_Qua_Khung_The_Badges", l3_dec),
        ("04_Logo_Chu_Gia_Va_Phap_Ly", l4_txt),
    ], psd_path, W, H)
    print(f"[DONE] {cid} -> {os.path.basename(jpg_path)}", flush=True)
    return {"id": cid, "jpg": jpg_path, "psd": psd_path}

# =============================================================================
# BANNER 07: THẺ HƯỚNG DẪN 3 BƯỚC LÊN ĐƠN COMBO DROPPII (1600x2000)
# =============================================================================
def build_guide_card_html(logo_uri: str, pass_mode: str) -> str:
    is_decor = (pass_mode == "decor")
    decor_vis = "visible" if is_decor else "hidden"
    text_vis  = "hidden"  if is_decor else "visible"

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<style>
{font_faces_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1600px; height: 2000px; overflow: hidden;
  background: transparent; position: relative;
  font-family: 'BeVNBold', sans-serif;
  -webkit-font-smoothing: antialiased;
}}

/* HEADER BAND */
.hdr-bg {{
  position: absolute; top: 0; left: 0; right: 0; height: 425px;
  background: linear-gradient(155deg, rgba(4,41,27,0.95) 0%, rgba(8,71,48,0.92) 55%, rgba(3,34,22,0.96) 100%);
  border-bottom: 6px solid #E6B442;
  box-shadow: 0 14px 36px rgba(4,36,24,0.28);
  visibility: {decor_vis};
}}
.hdr-content {{
  position: absolute; top: 0; left: 0; right: 0; height: 425px;
  padding: 36px 64px 28px; display: flex; flex-direction: column; justify-content: space-between;
  visibility: {text_vis};
}}
.hdr-top {{ display: flex; align-items: center; justify-content: space-between; }}
.logo-chip {{
  background: rgba(255,255,255,0.95); border: 2.5px solid #E6B442; border-radius: 18px;
  padding: 8px 18px; display: flex; align-items: center;
}}
.logo-chip img {{ height: 74px; width: auto; }}
.alert-pill {{
  background: linear-gradient(135deg, #E8252E, #AA0B14); color: #FFF8DC;
  border: 3px solid #FFE28A; border-radius: 999px; padding: 14px 32px;
  font-family: 'MontBlack', sans-serif; font-size: 26px; letter-spacing: 1px;
  box-shadow: 0 8px 20px rgba(170,11,20,0.35);
}}
.main-h1 {{
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 64px; line-height: 1.24;
  padding-top: 14px; letter-spacing: 0.5px;
  background: linear-gradient(180deg, #FFFCE0 0%, #FCE186 48%, #E4AE38 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.35));
  text-align: center;
}}
.main-sub {{
  font-family: 'BeVNSemi', sans-serif; font-size: 30px; color: #EFFCF4;
  text-align: center; margin-top: 6px;
}}

/* 3 STEP CARDS */
.steps-wrap {{
  position: absolute; top: 462px; left: 64px; right: 64px;
  display: flex; flex-direction: column; gap: 26px;
}}
.step-card-bg {{
  height: 232px; border-radius: 30px;
  background: linear-gradient(180deg, #FFFFFF 0%, #FFFDF5 100%);
  border: 3.5px solid #E2B854;
  box-shadow: 0 12px 28px rgba(7,59,39,0.12);
  visibility: {decor_vis};
}}
.step-card-bg.warn {{
  border-color: #DF383E;
  background: linear-gradient(180deg, #FFFDFC 0%, #FFF3F2 100%);
}}

.steps-txt-wrap {{
  position: absolute; top: 462px; left: 64px; right: 64px;
  display: flex; flex-direction: column; gap: 26px;
  visibility: {text_vis};
}}
.step-row {{
  height: 232px; padding: 24px 36px; display: flex; align-items: center; gap: 32px;
}}
.step-num {{
  width: 118px; height: 118px; border-radius: 30px; flex-shrink: 0;
  background: linear-gradient(145deg, #0D6B49, #053A26);
  border: 4px solid #F2CB63;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  box-shadow: 0 10px 20px rgba(5,58,38,0.28);
}}
.step-num.red {{
  background: linear-gradient(145deg, #E62932, #9E0A14);
  border-color: #FFE082;
}}
.sn-k {{ font-family: 'BeVNBold', sans-serif; font-size: 20px; color: #FCE186; letter-spacing: 1px; }}
.sn-v {{ font-family: 'MontBlack', sans-serif; font-size: 54px; color: #FFFFFF; line-height: 0.95; }}
.step-body {{ flex: 1; }}
.st-title {{ font-family: 'MontBlack', sans-serif; font-size: 36px; color: #053A26; margin-bottom: 10px; }}
.st-title.red {{ color: #B50E19; }}
.st-desc {{ font-family: 'BeVNSemi', sans-serif; font-size: 28px; color: #20372E; line-height: 1.38; }}
.st-desc b {{ color: #B50E19; font-family: 'BeVNExtra', sans-serif; }}
.st-desc em {{ font-style: normal; color: #095C3E; font-family: 'BeVNExtra', sans-serif; }}

/* QUICK 6-COMBO REFERENCE TABLE */
.tbl-box-bg {{
  position: absolute; top: 1244px; left: 64px; right: 64px; height: 604px;
  background: rgba(255,255,255,0.96);
  border: 3.5px solid #0B5B3E; border-radius: 30px;
  box-shadow: 0 14px 32px rgba(5,48,32,0.14);
  overflow: hidden;
  visibility: {decor_vis};
}}
.tbl-hdr-bar {{
  height: 78px; background: linear-gradient(90deg, #053825, #0B6444, #053825);
  border-bottom: 3px solid #E6B442;
}}
.tbl-content {{
  position: absolute; top: 1244px; left: 64px; right: 64px; height: 604px;
  border-radius: 30px; overflow: hidden; border: 3.5px solid transparent;
  visibility: {text_vis};
}}
.tbl-title {{
  height: 75px; display: flex; align-items: center; justify-content: center;
  font-family: 'BeVNExtra', 'MontBlack', sans-serif; font-size: 31px; color: #FFF5C8; letter-spacing: 0.5px;
}}
table {{ width: 100%; border-collapse: collapse; }}
th {{
  background: rgba(237,247,242,0.88); color: #06402A; font-family: 'BeVNExtra', sans-serif; font-size: 24px;
  padding: 15px 22px; text-align: left; border-bottom: 2px solid #C8E2D5;
}}
td {{
  padding: 18px 22px; font-family: 'BeVNSemi', sans-serif; font-size: 25px; color: #162E25;
  border-bottom: 1.5px solid #E5EFEA;
}}
tbody tr:last-child td {{ border-bottom: none; }}
tr:nth-child(even) td {{ background: rgba(244,251,247,0.72); }}
.td-price {{ font-family: 'MontBlack', sans-serif; color: #0C40A8; white-space: nowrap; }}
.td-gift {{ font-family: 'BeVNExtra', sans-serif; color: #C2121E; }}

/* FOOTER */
.ftr-bg {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 104px;
  background: linear-gradient(90deg, #04291B 0%, #084931 50%, #04291B 100%);
  border-top: 4px solid #E6B442;
  visibility: {decor_vis};
}}
.ftr-txt {{
  position: absolute; bottom: 0; left: 0; right: 0; height: 104px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;
  visibility: {text_vis};
}}
.ftr-hot {{ font-family: 'BeVNExtra', sans-serif; font-size: 28px; color: #FCE186; }}
.ftr-leg {{ font-family: 'BeVNSemi', sans-serif; font-size: 22px; color: #E8F5EE; }}
</style>
</head>
<body>
  <div class="hdr-bg"></div>
  <div class="hdr-content">
    <div class="hdr-top">
      <div class="logo-chip"><img src="{logo_uri}" /></div>
      <div class="alert-pill">⚠️ LƯU Ý QUAN TRỌNG CHO ĐỐI TÁC DROPPII</div>
    </div>
    <div>
      <div class="main-h1">HƯỚNG DẪN 3 BƯỚC LÊN ĐƠN COMBO</div>
      <div class="main-sub">Chống đặt nhầm mã lẻ — Đảm bảo nhận đủ 100% quà tặng đợt 23/11 – 30/11/2026</div>
    </div>
  </div>

  <div class="steps-wrap">
    <div class="step-card-bg"></div>
    <div class="step-card-bg"></div>
    <div class="step-card-bg warn"></div>
  </div>
  <div class="steps-txt-wrap">
    <div class="step-row">
      <div class="step-num"><span class="sn-k">BƯỚC</span><span class="sn-v">01</span></div>
      <div class="step-body">
        <div class="st-title">CHỌN ĐÚNG MÃ COMBO KHUYẾN MÃI TRÊN APP</div>
        <div class="st-desc">Vào App Droppii → mục <em>Khuyến mãi / Combo An Vượng Pharma</em> và chọn đúng mã Combo đang chạy. <b>KHÔNG tự bấm cộng từng hộp lẻ</b> vào giỏ hàng vì hệ thống sẽ không tự gắn quà tặng!</div>
      </div>
    </div>
    <div class="step-row">
      <div class="step-num"><span class="sn-k">BƯỚC</span><span class="sn-v">02</span></div>
      <div class="step-body">
        <div class="st-title">KIỂM TRA DÒNG QUÀ TẶNG (0Đ) TRONG GIỎ HÀNG</div>
        <div class="st-desc">Trước khi bấm thanh toán, nhìn kỹ giỏ hàng phải hiển thị đầy đủ <em>tên sản phẩm quà tặng đi kèm (giá 0đ)</em> khớp đúng bảng 6 mức Combo bên dưới.</div>
      </div>
    </div>
    <div class="step-row">
      <div class="step-num red"><span class="sn-k">BƯỚC</span><span class="sn-v">03</span></div>
      <div class="step-body">
        <div class="st-title red">SOÁT KỸ 2 GIÂY TRƯỚC KHI BẤM XÁC NHẬN ĐƠN</div>
        <div class="st-desc">Đơn đã chốt trên hệ thống Droppii <b>không thể tự đổi lại mã combo</b>. Nếu chưa thấy dòng quà tặng, hãy <em>dừng lại và nhắn ngay nhóm Hỗ trợ / Đối tác An Vượng</em> để được xử lý ngay!</div>
      </div>
    </div>
  </div>

  <div class="tbl-box-bg"><div class="tbl-hdr-bar"></div></div>
  <div class="tbl-content">
    <div class="tbl-title">📋 BẢNG TRA CỨU NHANH 6 MỨC COMBO DROPPII (23/11 – 30/11/2026)</div>
    <table>
      <thead>
        <tr>
          <th style="width:42%">Gói Combo Khuyến Mãi</th>
          <th style="width:20%">Giá Combo</th>
          <th style="width:38%">Quà Tặng Kèm (0đ)</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><b>Combo 4 SP</b> (Protein + Bojomi + Curcumilk + Collamela 20g)</td><td class="td-price">2.440.000đ</td><td class="td-gift">🎁 Tặng 1 Collamela 20 gói (920K)</td></tr>
        <tr><td><b>Mua 5 hộp AV Protein</b> (20 gói × 15g)</td><td class="td-price">1.750.000đ</td><td class="td-gift">🎁 Tặng 1 hộp Bojomi (520K)</td></tr>
        <tr><td><b>Mua 3 hộp Bojomi</b> (14 gói × 20g)</td><td class="td-price">1.560.000đ</td><td class="td-gift">🎁 Tặng 1 hộp Bojomi (520K)</td></tr>
        <tr><td><b>Mua 4 hộp Curcumilk Phyto</b> (14 gói × 15g)</td><td class="td-price">2.600.000đ</td><td class="td-gift">🎁 Tặng 1 hộp Curcumilk (650K)</td></tr>
        <tr><td><b>Mua 2 hộp Collamela 20 gói</b> (20 gói × 4g)</td><td class="td-price">1.840.000đ</td><td class="td-gift">🎁 Tặng 1 Collamela 10 gói (480K)</td></tr>
        <tr><td><b>Combo 2 Bojomi + 2 Curcumilk Phyto</b></td><td class="td-price">2.340.000đ</td><td class="td-gift">🎁 Tặng 1 hộp Bojomi (520K)</td></tr>
      </tbody>
    </table>
  </div>

  <div class="ftr-bg"></div>
  <div class="ftr-txt">
    <div class="ftr-hot">📞 Hotline hỗ trợ An Vượng Pharma: 0867 399 268 • Website: anvuongpharma.vn</div>
    <div class="ftr-leg">{LEGAL_TPBS}</div>
  </div>
</body>
</html>"""

def render_guide_card(guide_bg: Image.Image, logo_uri: str) -> dict:
    W, H = 1600, 2000
    l1_bg = guide_bg.resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")
    # Soft cream veil over middle body so card shadows pop cleanly
    veil = Image.new("RGBA", (W, H), (255, 252, 244, 155))
    l1_bg.alpha_composite(veil)

    h_dec = os.path.join(HTML_DIR, "GUIDE_07_decor.html")
    p_dec = os.path.join(HTML_DIR, "GUIDE_07_decor.png")
    with open(h_dec, "w", encoding="utf-8") as f:
        f.write(build_guide_card_html(logo_uri, "decor"))
    l2_dec = render_html_to_rgba(h_dec, p_dec, W, H)

    h_txt = os.path.join(HTML_DIR, "GUIDE_07_text.html")
    p_txt = os.path.join(HTML_DIR, "GUIDE_07_text.png")
    with open(h_txt, "w", encoding="utf-8") as f:
        f.write(build_guide_card_html(logo_uri, "text"))
    l3_txt = render_html_to_rgba(h_txt, p_txt, W, H)

    comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    comp.alpha_composite(l1_bg)
    comp.alpha_composite(l2_dec)
    comp.alpha_composite(l3_txt)

    fname = "261123 AVPM 07 - The Huong Dan 3 Buoc Len Don Combo Droppii"
    jpg_path = os.path.join(OUT_BANNERS, f"{fname}.jpg")
    psd_path = os.path.join(OUT_PSD, f"{fname}.psd")
    comp.convert("RGB").save(jpg_path, "JPEG", quality=98, subsampling=0, icc_profile=SRGB_BYTES)
    save_multilayer_psd([
        ("01_Nen_Kem_Ngoc_An_Vuong", l1_bg),
        ("02_Khung_The_3_Buoc_Va_Bang", l2_dec),
        ("03_Logo_Noi_Dung_Huong_Dan", l3_txt),
    ], psd_path, W, H)
    print(f"[DONE] GUIDE_07 -> {os.path.basename(jpg_path)}", flush=True)
    return {"id": "GUIDE_07", "jpg": jpg_path, "psd": psd_path}

def build_qc_sheet(results: list):
    cols, rows = 4, 2
    cw, ch = 560, 620
    sheet = Image.new("RGB", (cols * cw, rows * ch), (20, 26, 34))
    draw = ImageDraw.Draw(sheet)
    for i, r in enumerate(results):
        im = Image.open(r["jpg"]).convert("RGB")
        im.thumbnail((cw - 24, ch - 60), Image.Resampling.LANCZOS)
        x = (i % cols) * cw + (cw - im.width) // 2
        y = (i // cols) * ch + 12
        sheet.paste(im, (x, y))
        draw.text(((i % cols) * cw + 14, (i // cols) * ch + ch - 38), r["id"] + " | " + os.path.basename(r["jpg"])[:46], fill=(255, 232, 118))
    qc_path = os.path.join(AUDIT_DIR, "QC_7_Banners_CTKM_Va_Huong_Dan.jpg")
    sheet.save(qc_path, quality=92)
    print(f"[QC SHEET] Saved -> {qc_path}")
    return qc_path

if __name__ == "__main__":
    stage_p = os.path.join(STAGE_DIR, "bg_droppii_8th_stage.png")
    guide_p = os.path.join(STAGE_DIR, "bg_av_guide_cream_emerald.png")
    if not os.path.exists(stage_p) or not os.path.exists(guide_p):
        raise FileNotFoundError(f"Missing stage backdrops in {STAGE_DIR}")

    stage_bg = Image.open(stage_p)
    guide_bg = Image.open(guide_p)
    boxes = load_all_boxes()
    logo_uri = file_to_data_uri(LOGO_ORIG)

    results = []
    for sp in CTKM_BANNERS:
        results.append(render_ctkm_banner(sp, stage_bg, boxes, logo_uri))
    results.append(render_guide_card(guide_bg, logo_uri))
    build_qc_sheet(results)
    print("=== ALL 7 BANNERS + 7 PSDs COMPLETE ===")
