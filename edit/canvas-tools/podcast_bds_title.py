"""
Bộ Render Chữ Tiêu Đề Kép Phong Cách Podcast × BĐS / Doanh Nhân Thượng Lưu (`podcast_bds_title.py`)
Chuẩn mẫu @lopphovlog / editornghiepdu:
- Lớp Chính (Headline): Chữ lớn IN HOA hoặc Serif sang trọng, tô chuyển sắc Tâm Sáng Băng Ngọc (Radial/Horizontal Cyan-Ice Spotlight:
  2 mép Xanh Lam Hoàng Gia `#1D3E96` -> tâm giữa Băng Ngọc Phát Sáng `#58FFF5` / `#9EFFFF`) kèm hào quang mờ nhẹ.
- Lớp Phụ (Signature Script): Chữ ký tay trắng tinh khiết (`#FFFFFF`) kèm bóng tách nền mềm + viền sáng ấm nhẹ,
  hỗ trợ 2 bố cục chuẩn:
  + `mode="bottom_center"`: Đè lên 1/3 chân dưới của chữ chính (kiểu `EDITOR` + `Nghiệp dư` / `UTM BEBAS` + `Autography`).
  + `mode="top_left"`: Gác lệch vai trái đỉnh chữ chính (kiểu `Artful Beauty` + `BARLOW` / `Starcity` + `BLONA`).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"

# 10 Cặp Phối Font Tiếng Việt 100% Dấu Chuẩn Podcast × BĐS
PODCAST_BDS_PAIRS = {
    "barlow_artful": {
        "main_font": "BarlowCondensed-ExtraBoldItalic.ttf",
        "sub_font": "BirthstoneBounce-Medium.ttf",
        "mode": "top_left",
        "uppercase": True,
        "desc": "Barlow Condensed Italic × Artful Signature (Gác vai trái hiện đại)",
    },
    "bebas_autography": {
        "main_font": "BigShouldersDisplay-Black.ttf",
        "sub_font": "Allison-Regular.ttf",
        "mode": "bottom_center",
        "uppercase": True,
        "desc": "Bebas Tall Black × Autography Signature (Podcast mạnh mẽ)",
    },
    "magnesium_amsterdam": {
        "main_font": "Unbounded-Black.ttf",
        "sub_font": "WindSong-Medium.ttf",
        "mode": "bottom_center",
        "uppercase": True,
        "main_scale": 0.68,
        "desc": "Magnesium Wide Black × Amsterdam Signature (Điện ảnh BĐS)",
    },
    "blona_starcity": {
        "main_font": "SairaExtraCondensed-ExtraBold.ttf",
        "sub_font": "Cherish-Regular.ttf",
        "mode": "top_left",
        "uppercase": True,
        "desc": "Blona Tall Display × Starcity Script (Gác vai trái cao ráo)",
    },
    "alexander_ameyallinda": {
        "main_font": "Montserrat-Black.ttf",
        "sub_font": "BirthstoneBounce-Medium.ttf",
        "mode": "bottom_center",
        "uppercase": True,
        "main_scale": 0.84,
        "desc": "Alexander Bold Sans × Ameyallinda Signature (Doanh nhân / Diễn giả)",
    },
    "caviar_catalina": {
        "main_font": "JosefinSans-Light.ttf",
        "sub_font": "OoohBaby-Regular.ttf",
        "mode": "bottom_center",
        "uppercase": False,
        "main_scale": 0.78,
        "desc": "Caviar Sleek Thin × Santa Catalina (Penthouse / Villa tinh tế)",
    },
    "chetta_adventures": {
        "main_font": "PlayfairDisplay-Bold.ttf",
        "sub_font": "WindSong-Regular.ttf",
        "mode": "bottom_center",
        "uppercase": False,
        "main_scale": 0.88,
        "desc": "Chetta Luxury Serif × Adventures Script (BĐS Hạng Sang / Mỹ phẩm)",
    },
    "braven_bengoda": {
        "main_font": "Prata-Regular.ttf",
        "sub_font": "Ephesis-Regular.ttf",
        "mode": "bottom_center",
        "uppercase": False,
        "main_scale": 0.86,
        "desc": "Braven Editorial Didone × Bengoda Script (Resort / Thượng lưu)",
    },
    "impact_alfresco": {
        "main_font": "Anton-Regular.ttf",
        "sub_font": "Corinthia-Bold.ttf",
        "mode": "bottom_center",
        "uppercase": True,
        "main_scale": 0.88,
        "desc": "Impact Heavy × AlFresco Brush Script (Hook 3s chốt điểm nhấn)",
    },
    "podcast_signature": {
        "main_font": "BarlowCondensed-Black.ttf",
        "sub_font": "PassionsConflict-Regular.ttf",
        "mode": "bottom_center",
        "uppercase": True,
        "desc": "Podcast Classic Tall × Photograph Signature (Chuẩn Podcast Tri Thức)",
    },
}

THEMES = {
    "cyan_ice": {
        "edge_rgb": (31, 66, 166),     # Royal Cobalt Blue #1F42A6
        "mid_rgb": (36, 178, 224),     # Electric Cerulean #24B2E0
        "core_rgb": (132, 255, 246),   # Luminous Ice Aqua #84FFF6
        "glow_rgba": (46, 232, 228, 72),
        "sub_glow_rgba": (255, 242, 210, 105),
    },
    "gold_luxury": {
        "edge_rgb": (138, 86, 18),     # Deep Bronze Gold
        "mid_rgb": (228, 176, 62),     # Rich Champagne Gold
        "core_rgb": (255, 248, 204),   # Bright Ivory Gold Spotlight
        "glow_rgba": (255, 206, 88, 72),
        "sub_glow_rgba": (255, 255, 255, 110),
    },
    "rose_satin": {
        "edge_rgb": (138, 18, 83),     # Deep Lotus Berry
        "mid_rgb": (236, 82, 160),     # Satin Rose
        "core_rgb": (255, 224, 243),   # Pearl Pink Spotlight
        "glow_rgba": (255, 110, 186, 72),
        "sub_glow_rgba": (255, 245, 225, 105),
    },
}


def _make_spotlight_gradient(w: int, h: int, theme_cfg: dict) -> np.ndarray:
    """Tạo bề mặt màu Quầng Sáng Tâm Giữa (2 mép đậm -> chính giữa bừng sáng Băng Ngọc / Hoàng Kim)."""
    xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    ys = np.linspace(-0.6, 0.6, h, dtype=np.float32)[:, None]
    # Quầng sáng tập trung mạnh ở vùng trung tâm chữ (hơi lệch xuống 10% như mẫu gốc TikTok)
    dist = np.sqrt((xs * 1.08) ** 2 + ((ys - 0.08) * 0.85) ** 2)
    t = np.clip(1.0 - dist, 0.0, 1.0) ** 1.45

    edge = np.array(theme_cfg["edge_rgb"], dtype=np.float32)
    mid = np.array(theme_cfg["mid_rgb"], dtype=np.float32)
    core = np.array(theme_cfg["core_rgb"], dtype=np.float32)

    rgb = np.zeros((h, w, 3), dtype=np.float32)
    low_mask = t < 0.52
    t_low = np.clip(t / 0.52, 0.0, 1.0)[..., None]
    t_high = np.clip((t - 0.52) / 0.48, 0.0, 1.0)[..., None]

    rgb = np.where(low_mask[..., None], edge + (mid - edge) * t_low, mid + (core - mid) * t_high)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def render_podcast_signature_title(
    main_text: str,
    sub_text: str,
    pair_key: str = "barlow_artful",
    theme: str = "cyan_ice",
    canvas_size: tuple = (1080, 520),
    main_font_px: int = 168,
    sub_font_px: int = 86,
    mode_override: str = None,
    out_png: str = None,
) -> Image.Image:
    cfg = PODCAST_BDS_PAIRS.get(pair_key, PODCAST_BDS_PAIRS["barlow_artful"])
    th_cfg = THEMES.get(theme, THEMES["cyan_ice"])
    layout_mode = mode_override or cfg["mode"]

    m_scale = cfg.get("main_scale", 1.0)
    f_main = ImageFont.truetype(os.path.join(FONTS_DIR, cfg["main_font"]), int(round(main_font_px * m_scale)))
    f_sub = ImageFont.truetype(os.path.join(FONTS_DIR, cfg["sub_font"]), sub_font_px)

    disp_main = main_text.upper() if cfg.get("uppercase", True) else main_text
    cw, ch = canvas_size
    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    # 1. Đo kích thước chữ chính & vẽ mặt nạ Alpha siêu mịn (2x Supersampling)
    dummy = ImageDraw.Draw(out)
    mb = dummy.textbbox((0, 0), disp_main, font=f_main)
    mw, mh = mb[2] - mb[0], mb[3] - mb[1]
    mx = (cw - mw) // 2 - mb[0]
    my = (ch - mh) // 2 - mb[1] - (18 if layout_mode == "bottom_center" else -16)

    mask_main = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_main).text((mx, my), disp_main, font=f_main, fill=255)

    # Tạo lớp màu Spotlight chỉ phủ đúng vùng bbox của chữ chính để tâm sáng luôn nằm giữa chữ!
    grad_patch = _make_spotlight_gradient(max(1, mw + 20), max(1, mh + 20), th_cfg)
    grad_full = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    patch_rgba = Image.fromarray(grad_patch, mode="RGB").convert("RGBA")
    bx0 = max(0, (cw - mw) // 2 - 10)
    by0 = max(0, (ch - mh) // 2 - 10 - (18 if layout_mode == "bottom_center" else -16))
    grad_full.paste(patch_rgba, (bx0, by0))
    grad_full.putalpha(mask_main)

    # Hào quang băng ngọc dịu sau lưng chữ chính
    glow_layer = Image.new("RGBA", (cw, ch), th_cfg["glow_rgba"][:3] + (0,))
    glow_alpha = mask_main.filter(ImageFilter.GaussianBlur(radius=22))
    glow_alpha = glow_alpha.point(lambda a: min(255, int(a * (th_cfg["glow_rgba"][3] / 255.0))))
    glow_layer.putalpha(glow_alpha)
    out = Image.alpha_composite(out, glow_layer)
    out = Image.alpha_composite(out, grad_full)

    # 2. Vẽ Lớp Chữ Ký Đè Lên (Signature Script Overlay)
    sb = dummy.textbbox((0, 0), sub_text, font=f_sub)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    main_left = (cw - mw) // 2
    main_top = (ch - mh) // 2 - (18 if layout_mode == "bottom_center" else -16)

    if layout_mode == "top_left":
        sx = main_left + int(mw * 0.02) - sb[0]
        sy = main_top - int(sh * 0.46) - sb[1]
    else:
        sx = (cw - sw) // 2 - sb[0]
        sy = main_top + int(mh * 0.62) - sb[1]

    mask_sub = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_sub).text((sx, sy), sub_text, font=f_sub, fill=255)

    # Bóng đen mềm sát chân chữ ký để nổi bật 100% trên nền sáng xanh băng của chữ chính
    shadow_layer = Image.new("RGBA", (cw, ch), (4, 8, 22, 0))
    sh_alpha = mask_sub.filter(ImageFilter.GaussianBlur(radius=6)).point(lambda a: min(255, int(a * 0.88)))
    shadow_shifted = Image.new("L", (cw, ch), 0)
    shadow_shifted.paste(sh_alpha, (0, 3))
    shadow_layer.putalpha(shadow_shifted)
    out = Image.alpha_composite(out, shadow_layer)

    # Hào quang kem ấm nhẹ quanh nét bút chữ ký (giống mẫu gốc TikTok)
    sub_glow = Image.new("RGBA", (cw, ch), th_cfg["sub_glow_rgba"][:3] + (0,))
    sg_alpha = mask_sub.filter(ImageFilter.GaussianBlur(radius=9)).point(
        lambda a: min(255, int(a * (th_cfg["sub_glow_rgba"][3] / 255.0)))
    )
    sub_glow.putalpha(sg_alpha)
    out = Image.alpha_composite(out, sub_glow)

    # Ruột chữ ký trắng sắc nét
    white_sub = Image.new("RGBA", (cw, ch), (255, 255, 255, 0))
    white_sub.putalpha(mask_sub)
    out = Image.alpha_composite(out, white_sub)

    if out_png:
        os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
        out.save(out_png)
    return out
