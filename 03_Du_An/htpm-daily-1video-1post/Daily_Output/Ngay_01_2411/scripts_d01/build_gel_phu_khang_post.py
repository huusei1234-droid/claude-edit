"""
Ngày 01 (24/11/2026) — Thiết kế Bài Đăng Thiết Kế Chuẩn Studio (Bộ 02 Ảnh HD 1600x1600 + 2 File .PSD Đa Layer Rời + Caption Thổi Hồn)
Sản phẩm: SP09 — Gel Phụ Khang Hằng Thu ("Skincare da mặt đủ 10 bước, sao lại để 'cô bé' chờ đến lúc khó chịu mới nhớ?")
- Ảnh 01 (Key Visual): Chị Hằng trong Bộ 01 (Blazer trắng kem & áo lụa hồng phấn) bên bàn trang điểm + Ghép trực tiếp 100% hộp thật
  SP_GEL_PHU_KHANG_STUDIO_CUTOUT.png (0% sai chữ bao bì) + Bóng đổ tiếp xúc tự nhiên + Chữ 2 lớp tách viền Gradient Rose-Gold.
- Ảnh 02 (Infographic): 4 Thảo dược thiên nhiên (Kim ngân hoa · Trầu không · Khổ sâm · Trinh nữ hoàng cung) + 3 Chuẩn Dịu Êm + Hộp thật.
- Xuất kèm 2 file .PSD tách 4 Layer RGBA trong suốt chuẩn Adobe Photoshop 2026 (pytoshop + packbits) & Caption_Bai_Dang_HTPM.txt!
"""
import os
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageFont
import packbits
import pytoshop
from pytoshop.user import nested_layers
import pytoshop.codecs

pytoshop.codecs.packbits = packbits

PROJ_DIR = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124")
ING_DIR = PROJ_DIR / "01_ChatGPT_Ingredients"
OUT_DIR = PROJ_DIR / "09_Bai_Thiet_Ke_Gel_Phu_Khang"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BRAND_KIT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")
FONTS_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")

BOX_CUTOUT_PATH = BRAND_KIT / "products_cutout_png" / "SP_GEL_PHU_KHANG_STUDIO_CUTOUT.png"
LOGO_PATH = BRAND_KIT / "logos_png" / "ht_logo_official.png"
SRGB_ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS_DIR / name), size)


def save_jpg_srgb(im_rgb: Image.Image, path: Path):
    im_rgb.convert("RGB").save(path, format="JPEG", quality=98, subsampling=0, optimize=True, icc_profile=SRGB_ICC)


def save_rgba_layers_psd(layer_tuples: list, size_wh: tuple, psd_path: Path):
    """
    layer_tuples: list of (layer_name_top_to_bottom, PIL.Image RGBA of size_wh)
    """
    W, H = size_wh
    psd_layers = []
    for name, im_rgba in layer_tuples:
        arr = np.array(im_rgba.convert("RGBA"), dtype=np.uint8)
        chans = {
            -1: arr[..., 3],
            0: arr[..., 0],
            1: arr[..., 1],
            2: arr[..., 2],
        }
        psd_layers.append(
            nested_layers.Image(
                name=name,
                visible=True,
                opacity=255,
                group_id=0,
                blend_mode=pytoshop.enums.BlendMode.normal,
                top=0,
                left=0,
                bottom=H,
                right=W,
                channels=chans,
            )
        )
    psd = nested_layers.nested_layers_to_psd(
        psd_layers,
        color_mode=pytoshop.enums.ColorMode.rgb,
        size=(W, H),
        compression=pytoshop.enums.Compression.rle,
    )
    with open(psd_path, "wb") as f:
        psd.write(f)


def draw_gradient_text_2layer(
    canvas_rgba: Image.Image,
    xy: tuple,
    text: str,
    font: ImageFont.FreeTypeFont,
    stops: list,
    stroke_w: int = 10,
    stroke_col=(255, 255, 255, 255),
    shadow_col=(68, 8, 32, 95),
    shadow_off=(0, 7),
    anchor: str = "la",
):
    """
    2-Layer Detached Stroke + Multi-Stop Vertical Gradient Fill (stroke NEVER eats into gradient!)
    """
    W, H = canvas_rgba.size
    tmp_mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(tmp_mask)
    bbox = md.textbbox(xy, text, font=font, anchor=anchor)
    md.text(xy, text, font=font, fill=255, anchor=anchor)

    # 1. Soft drop shadow + outer crisp stroke layer
    back = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(back)
    bd.text((xy[0] + shadow_off[0], xy[1] + shadow_off[1]), text, font=font, fill=shadow_col, stroke_width=stroke_w, stroke_fill=shadow_col, anchor=anchor)
    back = back.filter(ImageFilter.GaussianBlur(radius=6))
    bd2 = ImageDraw.Draw(back)
    bd2.text(xy, text, font=font, fill=stroke_col, stroke_width=stroke_w, stroke_fill=stroke_col, anchor=anchor)

    # 2. Multi-stop gradient front fill
    y0, y1 = max(0, bbox[1]), min(H, max(bbox[1] + 2, bbox[3]))
    gh = max(2, y1 - y0)
    grad_1d = np.zeros((gh, 1, 4), dtype=np.uint8)
    for r_i in range(gh):
        t = r_i / float(gh - 1)
        for s_idx in range(len(stops) - 1):
            p0, c0 = stops[s_idx]
            p1, c1 = stops[s_idx + 1]
            if p0 <= t <= p1:
                u = (t - p0) / max(1e-6, p1 - p0)
                col = [int(round(c0[k] * (1 - u) + c1[k] * u)) for k in range(3)] + [255]
                grad_1d[r_i, 0] = col
                break

    grad_full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad_strip = Image.fromarray(np.repeat(grad_1d, max(1, bbox[2] - bbox[0] + 16), axis=1), mode="RGBA")
    grad_full.paste(grad_strip, (max(0, bbox[0] - 8), y0))

    front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    front.paste(grad_full, (0, 0), mask=tmp_mask)

    canvas_rgba.alpha_composite(back)
    canvas_rgba.alpha_composite(front)


def rounded_frosted_box(canvas: Image.Image, box: tuple, radius: int, fill_rgba: tuple, border_rgba: tuple, border_w: int = 3):
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((box[0], box[1] + 10, box[2], box[3] + 10), radius=radius, fill=(78, 12, 38, 42))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    canvas.alpha_composite(sh)

    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(box, radius=radius, fill=fill_rgba, outline=border_rgba, width=border_w)
    canvas.alpha_composite(overlay)


def build_image_01_key_visual():
    W, H = 1600, 1600
    kv_ref = ING_DIR / "GPK_KV_ref.png"
    bg_raw = Image.open(kv_ref).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)

    # Layer 1: Base Photo (Chị Hằng in Day 01 Blazer & Blush Silk beside Vanity)
    l1_bg = bg_raw.convert("RGBA")

    # Layer 2: Soft Top-Right & Bottom-Right Editorial Readability Glow + Contact Shadow
    l2_fx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fx_d = ImageDraw.Draw(l2_fx)
    # Subtle warm ivory-pink glow on upper canvas & right side (never touching Chị Hằng's face!)
    fx_d.ellipse((660, 40, 1660, 620), fill=(255, 246, 250, 215))
    fx_d.ellipse((740, 860, 1620, 1520), fill=(255, 236, 244, 175))
    l2_fx = l2_fx.filter(ImageFilter.GaussianBlur(65))

    # Realistic 2-tier contact + ambient shadow under real Gel Phụ Khang box on marble counter
    sh_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh_d = ImageDraw.Draw(sh_layer)
    sh_d.ellipse((790, 1255, 1515, 1345), fill=(72, 16, 36, 115))
    sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(22))
    sh_tight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh_tight).ellipse((820, 1272, 1485, 1312), fill=(52, 8, 24, 150))
    sh_tight = sh_tight.filter(ImageFilter.GaussianBlur(8))
    l2_fx.alpha_composite(sh_layer)
    l2_fx.alpha_composite(sh_tight)

    # Layer 3: 100% Real Gel Phụ Khang Studio Cutout Box
    l3_prod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    box_im = Image.open(BOX_CUTOUT_PATH).convert("RGBA")
    target_w = 700
    target_h = int(round(box_im.height * (target_w / float(box_im.width))))
    box_resized = box_im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    bx, by = 805, 1300 - target_h
    l3_prod.alpha_composite(box_resized, (bx, by))

    # Layer 4: Brand Logo, 3D Rose-Silk Gradient Headline, Question Hook & Bottom Benefit Bar
    l4_typo = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Official Logo top-right pill
    rounded_frosted_box(l4_typo, (1245, 48, 1545, 142), radius=47, fill_rgba=(255, 255, 255, 238), border_rgba=(236, 168, 196, 210), border_w=2)
    if LOGO_PATH.exists():
        lg = Image.open(LOGO_PATH).convert("RGBA")
        lg.thumbnail((72, 72), Image.Resampling.LANCZOS)
        l4_typo.alpha_composite(lg, (1264, 95 - lg.height // 2))
    td = ImageDraw.Draw(l4_typo)
    td.text((1350, 78), "HẰNG THU", font=fnt("BeVietnamPro-ExtraBold.ttf", 24), fill=(184, 20, 86, 255))
    td.text((1350, 106), "PHARMA", font=fnt("BeVietnamPro-SemiBold.ttf", 18), fill=(112, 34, 64, 255))

    # Right-side Editorial Hook Card (X=760..1548, Y=178..630 -> 100% clear of Chị Hằng on left!)
    rounded_frosted_box(l4_typo, (760, 178, 1548, 636), radius=36, fill_rgba=(255, 252, 254, 228), border_rgba=(228, 128, 168, 190), border_w=3)
    td = ImageDraw.Draw(l4_typo)
    # Pill tag
    td.rounded_rectangle((796, 208, 1246, 258), radius=25, fill=(196, 24, 92, 255))
    td.text((1021, 233), "GÓC NHÌN PHỤ NỮ HIỆN ĐẠI", font=fnt("BeVietnamPro-ExtraBold.ttf", 20), fill=(255, 255, 255, 255), anchor="mm")

    td.text((798, 286), "Skincare da mặt đủ 10 bước,", font=fnt("BeVietnamPro-ExtraBold.ttf", 40), fill=(74, 13, 39, 255))
    td.text((798, 342), "Sao lại để vùng nhạy cảm", font=fnt("BeVietnamPro-SemiBold.ttf", 36), fill=(104, 26, 58, 255))

    rose_stops = [(0.0, (238, 68, 138)), (0.48, (188, 16, 84)), (1.0, (112, 6, 48))]
    draw_gradient_text_2layer(
        l4_typo,
        (798, 398),
        "Chờ khó chịu mới nhớ?",
        fnt("Fraunces-Black.ttf", 54),
        rose_stops,
        stroke_w=10,
    )

    td = ImageDraw.Draw(l4_typo)
    td.line([(798, 492), (1510, 492)], fill=(238, 184, 206, 220), width=2)
    td.text((798, 514), "✦ Gel Phụ Khang Hằng Thu — Hộp 8 túi × 5ml", font=fnt("BeVietnamPro-ExtraBold.ttf", 27), fill=(176, 88, 8, 255))
    td.text((798, 558), "   Nâng niu dịu nhẹ hằng ngày · Không Paraben", font=fnt("BeVietnamPro-SemiBold.ttf", 25), fill=(88, 28, 52, 255))

    # Bottom Full-Width Luxury Ribbon (Y=1378..1542)
    rounded_frosted_box(l4_typo, (56, 1378, 1544, 1544), radius=34, fill_rgba=(255, 250, 253, 242), border_rgba=(201, 24, 96, 180), border_w=3)
    td = ImageDraw.Draw(l4_typo)
    td.text((100, 1432), "GEL PHỤ KHANG HẰNG THU", font=fnt("PlayfairDisplay-ExtraBold.ttf", 42), fill=(184, 20, 86, 255), anchor="lm")
    td.text((100, 1492), "Sạch dịu nhẹ  •  Khử mùi hôi  •  Thoáng sạch thơm mát tự nhiên", font=fnt("BeVietnamPro-SemiBold.ttf", 27), fill=(74, 16, 40, 255), anchor="lm")

    td.rounded_rectangle((1156, 1414, 1510, 1508), radius=47, fill=(196, 24, 92, 255))
    td.text((1333, 1461), "TƯ VẤN RIÊNG 1:1", font=fnt("BeVietnamPro-ExtraBold.ttf", 26), fill=(255, 255, 255, 255), anchor="mm")

    # Flatten for JPG & save 4-layer PSD
    comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    for lyr in (l1_bg, l2_fx, l3_prod, l4_typo):
        comp.alpha_composite(lyr)

    jpg_p = OUT_DIR / "261124_HTPM_Gel_Phu_Khang_01_KeyVisual.jpg"
    psd_p = OUT_DIR / "261124_HTPM_Gel_Phu_Khang_01_KeyVisual.psd"
    save_jpg_srgb(comp, jpg_p)
    save_rgba_layers_psd(
        [
            ("04_Chu_Gradient_&_Logo_HTPM", l4_typo),
            ("03_Hop_Gel_Phu_Khang_That_ISNet", l3_prod),
            ("02_Hao_Quang_&_Bong_Do_Tiep_Xuc", l2_fx),
            ("01_Nen_Chi_Hang_Bo_01_Vanity", l1_bg),
        ],
        (W, H),
        psd_p,
    )
    print(f"[POST IMG 01 OK] {jpg_p.name} + {psd_p.name}")
    return jpg_p, psd_p


def build_image_02_infographic():
    W, H = 1600, 1600
    # Layer 1: Luxury Pearl-Blush Silk Radial Studio Background
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.sqrt(((xx - 800) / 950.0) ** 2 + ((yy - 680) / 950.0) ** 2)
    dist = np.clip(dist, 0.0, 1.2) / 1.2
    c_center = np.array([255, 250, 252], dtype=np.float32)
    c_edge = np.array([252, 218, 232], dtype=np.float32)
    bg_arr = (c_center[None, None, :] * (1.0 - dist[..., None]) + c_edge[None, None, :] * dist[..., None]).astype(np.uint8)
    l1_bg = Image.fromarray(bg_arr, mode="RGB").convert("RGBA")

    # Layer 2: Soft Botanical Orbs, Podium Ring & Cards Base
    l2_cards = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((420, 390, 1180, 930), fill=(255, 184, 212, 115))
    gd.ellipse((80, 80, 520, 480), fill=(255, 240, 214, 130))
    glow = glow.filter(ImageFilter.GaussianBlur(55))
    l2_cards.alpha_composite(glow)

    # Podium shadow under centerpiece box
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((450, 770, 1150, 850), fill=(92, 16, 46, 95))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    l2_cards.alpha_composite(sh)

    # 4 Botanical Ingredient Cards in 2x2 Grid below the centerpiece box
    card_specs = [
        ((76, 895, 776, 1135), "01 · KIM NGÂN HOA", "Làm dịu nhẹ nhàng, hỗ trợ kháng khuẩn\nvà giảm cảm giác ngứa rát khó chịu."),
        ((824, 895, 1524, 1135), "02 · LÁ TRẦU KHÔNG", "Làm sạch thoáng vùng nhạy cảm, khử mùi hôi\nvà giữ cảm giác tươi mát suốt ngày dài."),
        ((76, 1168, 776, 1408), "03 · KHỔ SÂM THIÊN NHIÊN", "Hỗ trợ thanh lọc dịu êm, duy trì sự khô thoáng\nmà không gây khô căng da nhạy cảm."),
        ((824, 1168, 1524, 1408), "04 · TRINH NỮ HOÀNG CUNG", "Thảo mộc quý nâng niu, bảo vệ và nuôi dưỡng\nvùng da nhạy cảm của phái đẹp mỗi ngày."),
    ]
    for box, title, desc in card_specs:
        rounded_frosted_box(l2_cards, box, radius=30, fill_rgba=(255, 255, 255, 240), border_rgba=(232, 146, 182, 200), border_w=3)

    # Layer 3: Centerpiece 100% Real Gel Phụ Khang Studio Cutout Box
    l3_prod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    box_im = Image.open(BOX_CUTOUT_PATH).convert("RGBA")
    tw = 740
    th = int(round(box_im.height * (tw / float(box_im.width))))
    box_r = box_im.resize((tw, th), Image.Resampling.LANCZOS)
    l3_prod.alpha_composite(box_r, ((W - tw) // 2, 815 - th))

    # Layer 4: Headline, Card Text, 3 Quality Badges & Official Notification Footer
    l4_typo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(l4_typo)

    # Top Header
    td.rounded_rectangle((530, 56, 1070, 112), radius=28, fill=(196, 24, 92, 255))
    td.text((800, 84), "BẢNG THÀNH PHẦN THẢO MỘC DỊU ÊM", font=fnt("BeVietnamPro-ExtraBold.ttf", 23), fill=(255, 255, 255, 255), anchor="mm")

    rose_stops = [(0.0, (238, 68, 138)), (0.50, (186, 16, 84)), (1.0, (108, 6, 46))]
    draw_gradient_text_2layer(
        l4_typo,
        (800, 188),
        "4 Thảo Dược Nâng Niu Phái Đẹp",
        fnt("Fraunces-Black.ttf", 64),
        rose_stops,
        stroke_w=12,
        anchor="mm",
    )
    td = ImageDraw.Draw(l4_typo)
    td.text(
        (800, 266),
        "Không Paraben  •  Không chất phụ thuộc  •  Hộp 8 túi × 5ml tiện lợi mang theo",
        font=fnt("BeVietnamPro-SemiBold.ttf", 28),
        fill=(116, 28, 62, 255),
        anchor="mm",
    )

    for (x0, y0, x1, y1), title, desc in card_specs:
        td.rounded_rectangle((x0 + 28, y0 + 24, x0 + 390, y0 + 70), radius=23, fill=(255, 232, 242, 255), outline=(228, 138, 176, 255), width=2)
        td.text((x0 + 46, y0 + 47), title, font=fnt("BeVietnamPro-ExtraBold.ttf", 23), fill=(184, 20, 86, 255), anchor="lm")
        for li, line in enumerate(desc.split("\n")):
            td.text((x0 + 32, y0 + 96 + li * 42), line, font=fnt("BeVietnamPro-SemiBold.ttf", 26), fill=(68, 16, 38, 255))

    # Footer Bar with Official Cosmetic Notification Number (05/25/CBMP-HB)
    rounded_frosted_box(l4_typo, (76, 1442, 1524, 1546), radius=28, fill_rgba=(184, 20, 86, 255), border_rgba=(255, 226, 168, 255), border_w=3)
    td = ImageDraw.Draw(l4_typo)
    td.text(
        (800, 1494),
        "HẰNG THU PHARMA  •  Số công bố Sở Y Tế: 05/25/CBMP-HB  •  Sạch dịu nhẹ – Khử mùi – Thơm mát",
        font=fnt("BeVietnamPro-ExtraBold.ttf", 25),
        fill=(255, 255, 255, 255),
        anchor="mm",
    )

    comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    for lyr in (l1_bg, l2_cards, l3_prod, l4_typo):
        comp.alpha_composite(lyr)

    jpg_p = OUT_DIR / "261124_HTPM_Gel_Phu_Khang_02_Infographic.jpg"
    psd_p = OUT_DIR / "261124_HTPM_Gel_Phu_Khang_02_Infographic.psd"
    save_jpg_srgb(comp, jpg_p)
    save_rgba_layers_psd(
        [
            ("04_Typography_4_Thao_Duoc_&_CBMP", l4_typo),
            ("03_Hop_Gel_Phu_Khang_That_ISNet", l3_prod),
            ("02_Khung_The_Frosted_&_Bong_Do", l2_cards),
            ("01_Nen_Lua_Hong_Ngoc_Studio", l1_bg),
        ],
        (W, H),
        psd_p,
    )
    print(f"[POST IMG 02 OK] {jpg_p.name} + {psd_p.name}")
    return jpg_p, psd_p


def write_caption():
    caption = """Skincare da mặt đủ 10 bước mỗi tối… sao nhiều khi chị em mình lại để vùng nhạy cảm chờ đến lúc khó chịu mới sực nhớ? 🌸

Phụ nữ hiện đại bận trăm công nghìn việc — sáng vội vã tới văn phòng, ngồi liền 8 tiếng đồng hồ, chiều về lại tất bật gia đình. Đôi khi chỉ một chút bí bách, ẩm ướt hay mùi hương kém tự tin thôi cũng đủ làm cả ngày dài mất đi sự thoải mái vốn có.

Thương bản thân thực ra không cần điều gì quá cầu kỳ, mà bắt đầu từ thói quen nâng niu dịu nhẹ mỗi ngày cùng Gel Phụ Khang Hằng Thu:
✨ Chiết xuất thảo mộc thiên nhiên lành tính: Kim ngân hoa, Lá trầu không, Khổ sâm và Trinh nữ hoàng cung.
✨ Làm sạch vùng nhạy cảm nhẹ nhàng, hỗ trợ khử mùi hôi, giữ cảm giác thoáng sạch và thơm mát tự nhiên.
✨ Công thức êm dịu: Không Paraben – Không chất phụ thuộc, thiết kế hộp 8 túi × 5ml nhỏ gọn, tinh tế để chị dễ dàng mang theo đi làm hay đi công tác.

Khi cơ thể bên trong sạch êm và thoải mái, ánh mắt hay nụ cười của người phụ nữ cũng tự khắc nhẹ nhõm, rạng rỡ hơn rất nhiều. 💕

📩 Nhắn ngay “GEL PHỤ KHANG” cho Hằng Thu Pharma để được lắng nghe và tư vấn riêng tư 1:1 cho chị nhé!

#HangThuPharma #GelPhuKhang #GelPhuKhangHangThu #ChamSocPhuNu #PhuNuHienDai #SachDiuNhe #YeuBanThan
"""
    cap_p = OUT_DIR / "261124_HTPM_Gel_Phu_Khang_Caption.txt"
    cap_p.write_text(caption, encoding="utf-8")
    print(f"[CAPTION OK] {cap_p.name}")
    return cap_p


def main():
    p1_jpg, p1_psd = build_image_01_key_visual()
    p2_jpg, p2_psd = build_image_02_infographic()
    cap_p = write_caption()

    # Build side-by-side preview sheet for visual QA
    im1 = Image.open(p1_jpg).resize((760, 760), Image.Resampling.LANCZOS)
    im2 = Image.open(p2_jpg).resize((760, 760), Image.Resampling.LANCZOS)
    sheet = Image.new("RGB", (1560, 800), (28, 16, 22))
    sheet.paste(im1, (14, 20))
    sheet.paste(im2, (786, 20))
    sheet.save(OUT_DIR / "qa_post_2images_sheet.jpg", quality=92)
    print(f"[POST QA SHEET] {OUT_DIR / 'qa_post_2images_sheet.jpg'}")


if __name__ == "__main__":
    main()
