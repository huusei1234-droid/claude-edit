import os
import sys
import io
import math
import base64
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageCms
import pytoshop
from pytoshop import enums as pe
from pytoshop.layers import LayerRecord, ChannelImageData

PROJ = Path(r"C:\AI\full studio\projects\htpm_5_trongtreo_261127")
STAGES_DIR = PROJ / "stages"
CUTOUTS_DIR = PROJ / "cutouts"
FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
OUT_JPG_DIR = PROJ / "final_jpg"
OUT_PSD_DIR = PROJ / "final_psd"
TMP_DIR = PROJ / "tmp_render"
QC_DIR = PROJ / "qc"
CHROME = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

for d in (OUT_JPG_DIR, OUT_PSD_DIR, TMP_DIR, QC_DIR):
    d.mkdir(parents=True, exist_ok=True)

W, H = 1600, 2000

# Verify fonts available
def font_url(name: str) -> str:
    p = FONTS_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing font: {p}")
    return p.as_uri()

def file_to_data_uri(path: Path, mime: str = "image/png") -> str:
    b = path.read_bytes()
    return f"data:{mime};base64,{base64.b64encode(b).decode('ascii')}"

def prepare_product_layer(
    cutout_path: Path,
    cx: int,
    bottom_y: int,
    target_w: int,
    mode: str,  # "water" or "plinth"
    shadow_rgb: tuple,
    reflection_strength: float = 0.24,
    soft_arch_rgba: tuple = None,
    plinth_clip_y: int = None,
) -> Path:
    """
    Build a transparent 1600x2000 RGBA PNG containing ONLY:
    - Optional ultra-subtle translucent sunlit editorial arch behind matte-white packaging
    - Realistic sunlit dual-layer contact shadow (ambient occlusion + directional morning cast)
    - Optional vertical water reflection (for water stages P01 & P02)
    - The 100% REAL Hằng Thu product cutout (cleanly scaled & micro-sharpened, ZERO AI distortion)
    """
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im = Image.open(cutout_path).convert("RGBA")

    # Clean micro-defringe: trim faint semi-transparent dust at alpha < 10
    arr = np.array(im)
    alpha = arr[:, :, 3]
    arr[alpha < 10, 3] = 0
    im = Image.fromarray(arr, "RGBA")

    # Compute target size preserving exact aspect ratio
    ow, oh = im.size
    scale = target_w / float(ow)
    nw = int(round(ow * scale))
    nh = int(round(oh * scale))

    # Resize RGB and Alpha separately with Lanczos for razor-sharp packaging text
    rgb = im.convert("RGB").resize((nw, nh), Image.Resampling.LANCZOS)
    # Gentle studio unsharp mask so packaging label text stays razor sharp
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.1, percent=62, threshold=2))
    # Subtle high-key sunlit lift (+3% brightness, +4% contrast) to harmonize with sunlit backdrop
    rgb = ImageEnhance.Brightness(rgb).enhance(1.03)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.04)
    a_ch = im.split()[3].resize((nw, nh), Image.Resampling.LANCZOS)
    prod = Image.merge("RGBA", (*rgb.split(), a_ch))

    x0 = int(round(cx - nw / 2))
    y0 = int(round(bottom_y - nh))

    # Optional subtle editorial soft arch behind matte-white product (e.g., Romance VIP)
    if soft_arch_rgba is not None:
        arch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(arch)
        aw = int(nw * 1.12)
        ah = int(nh * 0.86)
        ax0 = cx - aw // 2
        ay0 = y0 - int(nh * 0.06)
        ay1 = bottom_y - int(nh * 0.14)
        # Draw rounded arch (semicircle top + rectangle body)
        r = aw // 2
        dr.ellipse([ax0, ay0, ax0 + aw, ay0 + aw], fill=soft_arch_rgba)
        dr.rectangle([ax0, ay0 + r, ax0 + aw, ay1], fill=soft_arch_rgba)
        arch = arch.filter(ImageFilter.GaussianBlur(radius=46))
        # Fade out bottom of arch smoothly so it melts into water horizon
        a_arr = np.array(arch, dtype=np.float32)
        ys = np.arange(H, dtype=np.float32)[:, None]
        fade = np.clip((ay1 - ys) / 180.0, 0.0, 1.0)
        a_arr[:, :, 3] *= fade
        arch = Image.fromarray(a_arr.astype(np.uint8), "RGBA")
        canvas = Image.alpha_composite(canvas, arch)

    # Build elevation-aware contact shadow directly under every sub-object's exact base contour!
    pa = np.array(a_ch)
    col_has = pa > 120
    sr, sg, sb = shadow_rgb

    # Compute exact lowest opaque y for every column in the cutout
    ys_grid = np.arange(nh, dtype=np.int32)[:, None]
    masked_y = np.where(col_has, ys_grid, -1)
    col_bot = masked_y.max(axis=0)  # shape (nw,), -1 if empty

    # Keep columns whose lowest pixel sits in the ground-contact zone (bottom 38% of cutout)
    valid_cols = col_bot >= int(nh * 0.62)

    ao_mask = np.zeros((H, W), dtype=np.float32)
    dir_mask = np.zeros((H, W), dtype=np.float32)
    for ix in range(nw):
        if not valid_cols[ix]:
            continue
        gx = x0 + ix
        gy = y0 + int(col_bot[ix])
        if 0 <= gx < W and 0 <= gy < H:
            # Tight ambient occlusion band directly under base edge
            y_lo = max(0, gy - 5)
            y_hi = min(H, gy + 11)
            ao_mask[y_lo:y_hi, gx] = 1.0
            # Directional morning shadow cast slightly right & down (sun from upper-left)
            dx_lo = min(W - 1, gx + 4)
            dx_hi = min(W, gx + 42)
            dy_lo = max(0, gy - 4)
            dy_hi = min(H, gy + 26)
            dir_mask[dy_lo:dy_hi, dx_lo:dx_hi] = np.maximum(dir_mask[dy_lo:dy_hi, dx_lo:dx_hi], 1.0)

    # Convert masks to softly blurred tinted RGBA shadow layers
    dir_alpha = Image.fromarray((dir_mask * 72).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius=22))
    ao_alpha = Image.fromarray((ao_mask * 138).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius=8))

    dir_sh = Image.new("RGBA", (W, H), (sr, sg, sb, 0))
    dir_sh.putalpha(dir_alpha)
    ao_sh = Image.new("RGBA", (W, H), (sr, sg, sb, 0))
    ao_sh.putalpha(ao_alpha)

    # Clip plinth shadows softly so they never spill below plinth front edge
    if mode == "plinth" and plinth_clip_y is not None:
        for sh_img in (dir_sh, ao_sh):
            sa = np.array(sh_img, dtype=np.float32)
            ys = np.arange(H, dtype=np.float32)[:, None]
            clip_m = np.clip((plinth_clip_y - ys) / 14.0, 0.0, 1.0)
            sa[:, :, 3] *= clip_m
            sh_img.paste(Image.fromarray(sa.astype(np.uint8), "RGBA"))

    # Optional realistic mirror reflection for water stages (P01 & P02)
    if mode == "water" and reflection_strength > 0:
        ref_h = int(nh * 0.30)
        # Flip bottom portion of product vertically
        bot_crop = prod.crop((0, nh - ref_h, nw, nh))
        ref = ImageOps.flip(bot_crop)
        # Slight vertical compression (perspective on shallow water)
        ref_disp_h = int(ref_h * 0.72)
        ref = ref.resize((nw, ref_disp_h), Image.Resampling.LANCZOS)
        # Soft ripple blur
        ref = ref.filter(ImageFilter.GaussianBlur(radius=2.2))
        # Smooth exponential vertical fade
        rarr = np.array(ref, dtype=np.float32)
        ry = np.linspace(0.0, 1.0, ref_disp_h, dtype=np.float32)[:, None]
        fade = reflection_strength * np.power(1.0 - ry, 1.75)
        # Add subtle horizontal ripple shimmer modulation
        ripple = 0.88 + 0.12 * np.sin(ry * 28.0)
        rarr[:, :, 3] = np.clip(rarr[:, :, 3] * fade * ripple, 0, 255)
        ref_im = Image.fromarray(rarr.astype(np.uint8), "RGBA")
        ref_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ref_canvas.paste(ref_im, (x0, bottom_y - 6))
        canvas = Image.alpha_composite(canvas, ref_canvas)

    canvas = Image.alpha_composite(canvas, dir_sh)
    canvas = Image.alpha_composite(canvas, ao_sh)

    # Paste the crisp 100% REAL product on top
    prod_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    prod_layer.paste(prod, (x0, y0))
    canvas = Image.alpha_composite(canvas, prod_layer)

    out_path = TMP_DIR / f"{cutout_path.stem}_prod_layer.png"
    canvas.save(out_path)
    return out_path


POSTERS = [
    {
        "id": "01",
        "key": "01_white_skin",
        "filename": "261127 HTPM 01 Legend White Skin Trong Trẻo final",
        "stage": STAGES_DIR / "01_white_skin_stage.jpg",
        "cutout": CUTOUTS_DIR / "01_white_skin.png",
        "prod_cfg": dict(
            cx=820, bottom_y=1670, target_w=780, mode="water",
            shadow_rgb=(18, 66, 128), reflection_strength=0.25,
        ),
        "category_tag": "DƯỠNG TRẮNG CHUYÊN SÂU",
        "eyebrow": "VIÊN UỐNG TRẮNG DA • LEGEND WHITE SKIN",
        "hl1": "TRẮNG SÁNG",
        "hl2": "TỪ BÊN TRONG",
        "hl_size": 134,
        "ingredients": "L-Glutathione  •  NMN  •  Amino Acid Peptide  •  Vitamin E",
        "pills": ["Mờ sạm nám da", "Trẻ hóa NMN", "Căng mịn đều màu"],
        "seal_top": "CHÍNH HÃNG 100%",
        "seal_mid": "HẰNG THU",
        "seal_pos": ("right: 76px; top: 940px;"),
        "footer_left": "HỘP 30 VIÊN NANG MỀM",
        "footer_right": "Thực phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh.",
        "theme": {
            "ink_main": "#082D63",
            "ink_grad_1": "#0A3F8F",
            "ink_grad_2": "#0F7AD9",
            "ink_sub": "#12427D",
            "pill_bg": "rgba(255, 255, 255, 0.78)",
            "pill_border": "rgba(15, 112, 210, 0.28)",
            "pill_dot": "#0F7AD9",
            "eyebrow_bg": "rgba(15, 112, 210, 0.10)",
            "eyebrow_border": "rgba(15, 112, 210, 0.28)",
            "seal_ink": "#0A4A9E",
            "seal_bg": "rgba(255, 255, 255, 0.72)",
            "footer_bg": "rgba(255, 255, 255, 0.78)",
        },
    },
    {
        "id": "02",
        "key": "02_romance_vip",
        "filename": "261127 HTPM 02 Dung Dịch Vệ Sinh Romance VIP Trong Trẻo final",
        "stage": STAGES_DIR / "02_romance_vip_stage.jpg",
        "cutout": CUTOUTS_DIR / "02_romance_vip.png",
        "prod_cfg": dict(
            cx=800, bottom_y=1675, target_w=685, mode="water",
            shadow_rgb=(135, 34, 62), reflection_strength=0.22,
            soft_arch_rgba=(246, 198, 210, 118),
        ),
        "category_tag": "CHĂM SÓC DỊU NHẸ HẰNG NGÀY",
        "eyebrow": "DUNG DỊCH VỆ SINH • ROMANCE VIP 150ML",
        "hl1": "SẠCH THOÁNG",
        "hl2": "DỊU ÊM 24H",
        "hl_size": 136,
        "ingredients": "Chiết xuất Hoa Hồng  •  Trà Xanh  •  Lô Hội  •  Collagen",
        "pills": ["Chuẩn pH dịu nhẹ", "Kháng khuẩn khử mùi", "Hương hồng tinh tế"],
        "seal_top": "CHÍNH HÃNG 100%",
        "seal_mid": "HẰNG THU",
        "seal_pos": ("right: 78px; top: 910px;"),
        "footer_left": "CHAI 150ML / 5.0 FL.OZ",
        "footer_right": "Thành phần từ thiên nhiên • Không gây khô rát • Phù hợp dùng hằng ngày",
        "theme": {
            "ink_main": "#8F0E32",
            "ink_grad_1": "#A6123B",
            "ink_grad_2": "#DC1E4E",
            "ink_sub": "#7D1A37",
            "pill_bg": "rgba(255, 255, 255, 0.80)",
            "pill_border": "rgba(186, 26, 70, 0.25)",
            "pill_dot": "#D61B4C",
            "eyebrow_bg": "rgba(214, 27, 76, 0.08)",
            "eyebrow_border": "rgba(214, 27, 76, 0.25)",
            "seal_ink": "#A6123B",
            "seal_bg": "rgba(255, 255, 255, 0.76)",
            "footer_bg": "rgba(255, 255, 255, 0.80)",
        },
    },
    {
        "id": "03",
        "key": "03_lt_plus",
        "filename": "261127 HTPM 03 Viên Đặt Phụ Khoa LT Plus Trong Trẻo final",
        "stage": STAGES_DIR / "03_lt_plus_stage.jpg",
        "cutout": CUTOUTS_DIR / "03_lt_plus.png",
        "prod_cfg": dict(
            cx=815, bottom_y=1525, target_w=745, mode="plinth",
            shadow_rgb=(122, 54, 82), reflection_strength=0.0,
            plinth_clip_y=1545,
        ),
        "category_tag": "CHĂM SÓC PHỤ KHOA THẢO MỘC",
        "eyebrow": "VIÊN ĐẶT PHỤ KHOA • LT PLUS HẰNG THU",
        "hl1": "ÊM DỊU SẠCH SÂU",
        "hl2": "TÁI TẠO NIÊM MẠC",
        "hl_size": 114,
        "ingredients": "Hoàng Bá  •  Kim Ngân Hoa  •  Trầu Không  •  Acid Lactic",
        "pills": ["Thảo mộc lành tính", "Cân bằng pH chuẩn", "Kháng khuẩn khử mùi"],
        "seal_top": "CHÍNH HÃNG 100%",
        "seal_mid": "HẰNG THU",
        "seal_pos": ("right: 76px; top: 830px;"),
        "footer_left": "HỘP 15 VIÊN ĐẶT THẢO MỘC",
        "footer_right": "Kháng khuẩn, khử mùi, ngăn ngừa viêm nhiễm • Hỗ trợ chăm sóc vùng kín khỏe mạnh",
        "theme": {
            "ink_main": "#8A1242",
            "ink_grad_1": "#A3164E",
            "ink_grad_2": "#D62B6C",
            "ink_sub": "#7E1F46",
            "pill_bg": "rgba(255, 255, 255, 0.82)",
            "pill_border": "rgba(184, 30, 92, 0.25)",
            "pill_dot": "#CC2264",
            "eyebrow_bg": "rgba(196, 30, 96, 0.08)",
            "eyebrow_border": "rgba(196, 30, 96, 0.25)",
            "seal_ink": "#9E164C",
            "seal_bg": "rgba(255, 255, 255, 0.78)",
            "footer_bg": "rgba(255, 255, 255, 0.84)",
        },
    },
    {
        "id": "04",
        "key": "04_da_day_ht",
        "filename": "261127 HTPM 04 Dạ Dày HT Thảo Mộc Trong Trẻo final",
        "stage": STAGES_DIR / "04_da_day_ht_stage.jpg",
        "cutout": CUTOUTS_DIR / "04_da_day_ht.png",
        "prod_cfg": dict(
            cx=820, bottom_y=1548, target_w=770, mode="plinth",
            shadow_rgb=(28, 76, 48), reflection_strength=0.0,
            plinth_clip_y=1568,
        ),
        "category_tag": "THẢO MỘC BẢO VỆ TIÊU HÓA",
        "eyebrow": "THỰC PHẨM BẢO VỆ SỨC KHỎE • DẠ DÀY HT",
        "hl1": "ÊM DẠ DÀY",
        "hl2": "GIẢM TRÀO NGƯỢC",
        "hl_size": 122,
        "ingredients": "Dạ Cẩm  •  Nghệ Đen  •  Mộc Hương  •  Hoàng Liên",
        "pills": ["Giảm acid dịch vị", "Dịu nhanh ợ chua", "Bảo vệ niêm mạc"],
        "seal_top": "CHÍNH HÃNG 100%",
        "seal_mid": "HẰNG THU",
        "seal_pos": ("right: 76px; top: 850px;"),
        "footer_left": "LỌ 90G VIÊN HOÀN THẢO MỘC",
        "footer_right": "Thực phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh.",
        "theme": {
            "ink_main": "#0A522B",
            "ink_grad_1": "#0D6A38",
            "ink_grad_2": "#18944E",
            "ink_sub": "#125732",
            "pill_bg": "rgba(255, 255, 255, 0.82)",
            "pill_border": "rgba(18, 128, 68, 0.28)",
            "pill_dot": "#158E4A",
            "eyebrow_bg": "rgba(18, 128, 68, 0.09)",
            "eyebrow_border": "rgba(18, 128, 68, 0.26)",
            "seal_ink": "#0C6334",
            "seal_bg": "rgba(255, 255, 255, 0.80)",
            "footer_bg": "rgba(255, 255, 255, 0.86)",
        },
    },
    {
        "id": "05",
        "key": "05_dieu_kinh_ht",
        "filename": "261127 HTPM 05 Điều Kinh Bổ Trứng HT Trong Trẻo final",
        "stage": STAGES_DIR / "05_dieu_kinh_ht_stage.jpg",
        "cutout": CUTOUTS_DIR / "05_dieu_kinh_ht.png",
        "prod_cfg": dict(
            cx=805, bottom_y=1638, target_w=715, mode="plinth",
            shadow_rgb=(116, 44, 78), reflection_strength=0.0,
            plinth_clip_y=1655,
        ),
        "category_tag": "BỔ HUYẾT • ĐIỀU HÒA CHU KỲ",
        "eyebrow": "THẢO MỘC NỮ GIỚI • ĐIỀU KINH BỔ TRỨNG HT",
        "hl1": "TRỨNG KHỎE ĐỀU KINH",
        "hl2": "SỚM ĐÓN CON YÊU",
        "hl_size": 106,
        "ingredients": "Đương Quy  •  Hương Phụ  •  Hồng Hoa  •  Đan Sâm",
        "pills": ["Bổ huyết điều kinh", "Dưỡng trứng khỏe", "Giảm đau bụng kinh"],
        "seal_top": "CHÍNH HÃNG 100%",
        "seal_mid": "HẰNG THU",
        "seal_pos": ("right: 76px; top: 870px;"),
        "footer_left": "LỌ 90G VIÊN HOÀN THẢO MỘC",
        "footer_right": "Thực phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh.",
        "theme": {
            "ink_main": "#73114E",
            "ink_grad_1": "#8C155E",
            "ink_grad_2": "#C4227A",
            "ink_sub": "#751B52",
            "pill_bg": "rgba(255, 255, 255, 0.82)",
            "pill_border": "rgba(166, 26, 108, 0.26)",
            "pill_dot": "#B81F74",
            "eyebrow_bg": "rgba(166, 26, 108, 0.08)",
            "eyebrow_border": "rgba(166, 26, 108, 0.25)",
            "seal_ink": "#8A145D",
            "seal_bg": "rgba(255, 255, 255, 0.80)",
            "footer_bg": "rgba(255, 255, 255, 0.84)",
        },
    },
]

LOGO_URI = file_to_data_uri(CUTOUTS_DIR / "ht_logo_official.png", "image/png")

FONT_CSS = f"""
@font-face {{
  font-family: 'BeVietnam';
  src: url('{font_url("BeVietnamPro-ExtraBold.ttf")}') format('truetype');
  font-weight: 800;
  font-style: normal;
}}
@font-face {{
  font-family: 'BeVietnam';
  src: url('{font_url("BeVietnamPro-Bold.ttf")}') format('truetype');
  font-weight: 700;
  font-style: normal;
}}
@font-face {{
  font-family: 'BeVietnam';
  src: url('{font_url("BeVietnamPro-SemiBold.ttf")}') format('truetype');
  font-weight: 600;
  font-style: normal;
}}
@font-face {{
  font-family: 'BeVietnam';
  src: url('{font_url("BeVietnamPro-Medium.ttf")}') format('truetype');
  font-weight: 500;
  font-style: normal;
}}
@font-face {{
  font-family: 'MontserratBlack';
  src: url('{font_url("Montserrat-Black.ttf")}') format('truetype');
  font-weight: 900;
  font-style: normal;
}}
"""


def build_ui_html(p: dict, bg_uri: str = None, prod_uri: str = None, mode: str = "full") -> str:
    """
    mode:
      - 'full': bg + prod + ui (for direct 2K JPEG + reference)
      - 'ui': transparent background + ONLY typography, top bar, glass pills, seal, footer (for PSD layer 3)
    """
    th = p["theme"]
    show_bg = (mode == "full")
    show_prod = (mode == "full")
    body_bg = "transparent" if mode == "ui" else "#ffffff"

    pills_html = "".join(
        f"""
        <div class="pill">
          <span class="pill-dot"></span>
          <span>{txt}</span>
        </div>
        """
        for txt in p["pills"]
    )

    bg_tag = f'<img class="layer-bg" src="{bg_uri}" />' if show_bg else ""
    prod_tag = f'<img class="layer-prod" src="{prod_uri}" />' if show_prod else ""

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<style>
{FONT_CSS}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: {W}px;
  height: {H}px;
  overflow: hidden;
  background: {body_bg};
  font-family: 'BeVietnam', sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.canvas {{
  position: relative;
  width: {W}px;
  height: {H}px;
  overflow: hidden;
}}
.layer-bg {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}}
.layer-prod {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}}

/* TOP BRAND BAR */
.topbar {{
  position: absolute;
  top: 52px;
  left: 72px;
  right: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 10;
}}
.brand-left {{
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 10px 26px 10px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  border: 1.5px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.05);
}}
.brand-logo {{
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: contain;
  display: block;
}}
.brand-name {{
  font-family: 'BeVietnam', sans-serif;
  font-weight: 800;
  font-size: 25px;
  letter-spacing: 0.14em;
  color: {th["ink_main"]};
}}
.cat-tag {{
  font-weight: 700;
  font-size: 21px;
  letter-spacing: 0.12em;
  color: {th["ink_sub"]};
  padding: 14px 28px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  border: 1.5px solid {th["eyebrow_border"]};
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}}

/* HERO TYPOGRAPHY STACK */
.hero-stack {{
  position: absolute;
  top: 162px;
  left: 64px;
  right: 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 10;
}}
.eyebrow {{
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 11px 30px;
  border-radius: 999px;
  background: {th["eyebrow_bg"]};
  border: 1.5px solid {th["eyebrow_border"]};
  font-weight: 800;
  font-size: 23px;
  letter-spacing: 0.13em;
  color: {th["ink_main"]};
  margin-bottom: 24px;
}}
.headline {{
  font-family: 'MontserratBlack', 'BeVietnam', sans-serif;
  font-weight: 900;
  font-size: {p["hl_size"]}px;
  line-height: 1.13;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  margin-bottom: 24px;
  filter: drop-shadow(0 3px 22px rgba(255, 255, 255, 0.96));
}}
.hl-l1 {{
  display: block;
  color: {th["ink_main"]};
}}
.hl-l2 {{
  display: block;
  background: linear-gradient(92deg, {th["ink_grad_1"]} 0%, {th["ink_grad_2"]} 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.ingredients {{
  font-weight: 700;
  font-size: 31px;
  letter-spacing: 0.015em;
  color: {th["ink_sub"]};
  background: rgba(255, 255, 255, 0.62);
  padding: 10px 34px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  margin-bottom: 28px;
}}
.pills-row {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  flex-wrap: nowrap;
}}
.pill {{
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 15px 30px;
  border-radius: 999px;
  background: {th["pill_bg"]};
  border: 1.8px solid {th["pill_border"]};
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.055), inset 0 1px 0 rgba(255, 255, 255, 0.95);
  font-weight: 700;
  font-size: 27px;
  color: {th["ink_main"]};
  white-space: nowrap;
}}
.pill-dot {{
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: {th["pill_dot"]};
  flex-shrink: 0;
  box-shadow: 0 0 0 4px {th["eyebrow_bg"]};
}}

/* CIRCULAR LUXURY AUTHENTICITY SEAL */
.seal {{
  position: absolute;
  {p["seal_pos"]}
  width: 176px;
  height: 176px;
  border-radius: 50%;
  background: {th["seal_bg"]};
  border: 2px solid {th["pill_border"]};
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.07), inset 0 1px 2px rgba(255,255,255,0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}}
.seal svg {{
  width: 162px;
  height: 162px;
  display: block;
}}

/* BOTTOM AIRY COMPLIANCE BAR */
.footer-bar {{
  position: absolute;
  bottom: 42px;
  left: 72px;
  right: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 32px;
  border-radius: 999px;
  background: {th["footer_bg"]};
  border: 1.5px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  z-index: 10;
}}
.footer-left {{
  font-weight: 800;
  font-size: 21px;
  letter-spacing: 0.08em;
  color: {th["ink_main"]};
  white-space: nowrap;
}}
.footer-div {{
  width: 2px;
  height: 22px;
  background: {th["pill_border"]};
  flex-shrink: 0;
}}
.footer-right {{
  font-weight: 600;
  font-size: 20px;
  color: {th["ink_sub"]};
  opacity: 0.92;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
</style>
</head>
<body>
<div class="canvas">
  {bg_tag}
  {prod_tag}

  <div class="topbar">
    <div class="brand-left">
      <img class="brand-logo" src="{LOGO_URI}" />
      <span class="brand-name">HẰNG THU PHARMA</span>
    </div>
    <div class="cat-tag">{p["category_tag"]}</div>
  </div>

  <div class="hero-stack">
    <div class="eyebrow">{p["eyebrow"]}</div>
    <div class="headline">
      <span class="hl-l1">{p["hl1"]}</span>
      <span class="hl-l2">{p["hl2"]}</span>
    </div>
    <div class="ingredients">{p["ingredients"]}</div>
    <div class="pills-row">
      {pills_html}
    </div>
  </div>

  <div class="seal">
    <svg viewBox="0 0 180 180">
      <defs>
        <path id="sealCircle" d="M 90, 90 m -66, 0 a 66,66 0 1,1 132,0 a 66,66 0 1,1 -132,0" />
      </defs>
      <circle cx="90" cy="90" r="82" fill="none" stroke="{th["seal_ink"]}" stroke-opacity="0.22" stroke-width="1.5" stroke-dasharray="4 4"/>
      <text fill="{th["seal_ink"]}" font-family="BeVietnam, sans-serif" font-weight="800" font-size="11.8" letter-spacing="2.2">
        <textPath href="#sealCircle" startOffset="2%">★ {p["seal_top"]} • HẰNG THU PHARMA • </textPath>
      </text>
      <text x="90" y="84" text-anchor="middle" fill="{th["seal_ink"]}" font-family="MontserratBlack, BeVietnam, sans-serif" font-weight="900" font-size="28">100%</text>
      <text x="90" y="109" text-anchor="middle" fill="{th["seal_ink"]}" font-family="BeVietnam, sans-serif" font-weight="800" font-size="15" letter-spacing="1.6">{p["seal_mid"]}</text>
    </svg>
  </div>

  <div class="footer-bar">
    <span class="footer-left">{p["footer_left"]}</span>
    <span class="footer-div"></span>
    <span class="footer-right">{p["footer_right"]}</span>
  </div>
</div>
</body>
</html>
"""


def render_chrome(html_path: Path, png_out: Path, transparent: bool = False):
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        "--force-device-scale-factor=1",
        f"--window-size={W},{H}",
        f"--screenshot={png_out}",
    ]
    if transparent:
        cmd.append("--default-background-color=00000000")
    cmd.append(html_path.as_uri())
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not png_out.exists():
        raise RuntimeError(f"Chrome failed ({res.returncode}): {res.stderr}")


def rgba_to_layer(im_rgba: Image.Image, name: str) -> LayerRecord:
    arr = np.array(im_rgba.convert("RGBA"))
    h, w, _ = arr.shape
    channels = {
        -1: ChannelImageData(image=arr[:, :, 3], compression=pe.Compression.raw),
        0: ChannelImageData(image=arr[:, :, 0], compression=pe.Compression.raw),
        1: ChannelImageData(image=arr[:, :, 1], compression=pe.Compression.raw),
        2: ChannelImageData(image=arr[:, :, 2], compression=pe.Compression.raw),
    }
    return LayerRecord(
        top=0, left=0, bottom=h, right=w,
        channels=channels,
        name=name,
        opacity=255,
    )


def save_3layer_psd(bg_path: Path, prod_path: Path, ui_path: Path, psd_out: Path):
    bg_im = Image.open(bg_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    prod_im = Image.open(prod_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    ui_im = Image.open(ui_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)

    psd = pytoshop.core.PsdFile(num_channels=3, height=H, width=W, depth=8, color_mode=pe.ColorMode.rgb)
    # pytoshop layer order: bottom to top
    psd.layer_and_mask_info.layer_info.layer_records = [
        rgba_to_layer(bg_im, "01_Nen_Trong_Treo_Ngap_Nang"),
        rgba_to_layer(prod_im, "02_San_Pham_That_Hang_Thu"),
        rgba_to_layer(ui_im, "03_Chu_Va_Khung_Thong_Tin"),
    ]
    with open(psd_out, "wb") as f:
        psd.write(f)


def main():
    srgb_icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    rendered_jpgs = []

    for p in POSTERS:
        print(f"=== Building Poster {p['id']}: {p['filename']} ===", flush=True)
        # 1. Build transparent 1600x2000 Layer 2 (100% Real Product + Reflection + Shadow)
        prod_png = prepare_product_layer(p["cutout"], **p["prod_cfg"])

        bg_uri = file_to_data_uri(p["stage"], "image/jpeg")
        prod_uri = file_to_data_uri(prod_png, "image/png")

        # 2. Render Layer 3 transparent UI overlay via Headless Chrome
        ui_html = TMP_DIR / f"{p['key']}_ui.html"
        ui_png = TMP_DIR / f"{p['key']}_ui.png"
        ui_html.write_text(build_ui_html(p, mode="ui"), encoding="utf-8")
        render_chrome(ui_html, ui_png, transparent=True)

        # 3. Render composite full 2K preview directly by alpha-compositing exact 3 layers (guarantees 100% parity with PSD!)
        bg_im = Image.open(p["stage"]).convert("RGBA")
        prod_im = Image.open(prod_png).convert("RGBA")
        ui_im = Image.open(ui_png).convert("RGBA")
        comp = Image.alpha_composite(Image.alpha_composite(bg_im, prod_im), ui_im).convert("RGB")

        jpg_out = OUT_JPG_DIR / f"{p['filename']}.jpg"
        comp.save(jpg_out, format="JPEG", quality=96, subsampling=0, icc_profile=srgb_icc, dpi=(300, 300))
        rendered_jpgs.append((p["id"], jpg_out))

        # 4. Build genuine 3-layer editable .PSD for Photoshop 2027
        psd_out = OUT_PSD_DIR / f"{p['filename']}.psd"
        save_3layer_psd(p["stage"], prod_png, ui_png, psd_out)
        print(f"   OK JPG ({jpg_out.stat().st_size // 1024} KB) | PSD ({psd_out.stat().st_size // 1024} KB)", flush=True)

    # 5. Build bright 5-poster Overview Board (2800px wide crisp sRGB)
    card_w, card_h, gap, pad = 520, 650, 26, 44
    ov_w = pad * 2 + card_w * 5 + gap * 4
    ov_h = pad * 2 + card_h + 70
    ov = Image.new("RGB", (ov_w, ov_h), (247, 250, 253))
    dr = ImageDraw.Draw(ov)
    for idx, (pid, jp) in enumerate(rendered_jpgs):
        im = Image.open(jp).resize((card_w, card_h), Image.Resampling.LANCZOS)
        x = pad + idx * (card_w + gap)
        y = pad
        # Subtle card border
        dr.rectangle([x - 2, y - 2, x + card_w + 1, y + card_h + 1], outline=(218, 226, 236), width=2)
        ov.paste(im, (x, y))
        dr.text((x + 6, y + card_h + 18), f"POSTER {pid}", fill=(28, 45, 72))

    ov_out = QC_DIR / "final_5_trongtreo_overview.jpg"
    ov.save(ov_out, format="JPEG", quality=95, subsampling=0, icc_profile=srgb_icc)
    print(f"ALL DONE! Overview: {ov_out}")


if __name__ == "__main__":
    main()
