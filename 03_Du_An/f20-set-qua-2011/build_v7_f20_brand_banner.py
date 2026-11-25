import math, subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30.0

WORK     = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
V6_DIR   = WORK / "v6_assets"
V7_DIR   = WORK / "v7_assets"
V7_DIR.mkdir(parents=True, exist_ok=True)

F20      = Path(r"Z:\Máy tính khác\My Computer\F20")
LOGO_DIR = F20 / r"00_Ho_So_Thuong_Hieu_Va_Tham_Khao\Hinh_Anh_Logo_Va_San_Pham_Chuan"

COINY_TTF = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"
HERO_TTF  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\Montserrat-Black.ttf"
SANS_B    = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-ExtraBold.ttf"
SANS_M    = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-SemiBold.ttf"

def make_sep_text(text: str, font_path: str, size: int, fill_top: tuple, fill_bot: tuple,
                  stroke1_col: tuple, stroke1_w: int, stroke2_col: tuple | None = None, stroke2_w: int = 0,
                  shadow_a: int = 100) -> Image.Image:
    fnt = ImageFont.truetype(font_path, size)
    msw = max(stroke1_w, stroke2_w)
    bb = ImageDraw.Draw(Image.new("RGBA", (8, 8))).textbbox((0, 0), text, font=fnt, stroke_width=msw)
    tw, th = max(4, bb[2] - bb[0]), max(4, bb[3] - bb[1])
    pad = msw + 18
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bb[0], pad - bb[1]

    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    if shadow_a > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 5), text, font=fnt, fill=255, stroke_width=msw, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, :3] = (8, 28, 18)
        sa[:, :, 3] = np.clip(sb * shadow_a, 0, 255).astype(np.uint8)
        im = Image.alpha_composite(im, Image.fromarray(sa, "RGBA"))

    if stroke2_col and stroke2_w > 0:
        s2 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(s2).text((ox, oy), text, font=fnt, fill=(*stroke2_col, 255), stroke_width=stroke2_w, stroke_fill=(*stroke2_col, 255))
        im = Image.alpha_composite(im, s2)

    if stroke1_w > 0:
        s1 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(s1).text((ox, oy), text, font=fnt, fill=(*stroke1_col, 255), stroke_width=stroke1_w, stroke_fill=(*stroke1_col, 255))
        im = Image.alpha_composite(im, s1)

    fm = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(fm).text((ox, oy), text, font=fnt, fill=255)
    fa = np.array(fm, dtype=np.float32) / 255.0
    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)
    grad = np.zeros((ch, cw, 4), dtype=np.uint8)
    for c in range(3):
        col_1d = np.clip(fill_top[c] * (1.0 - yy) + fill_bot[c] * yy, 0, 255).astype(np.uint8)
        grad[:, :, c] = col_1d[:, None]
    grad[:, :, 3] = (fa * 255.0).astype(np.uint8)
    return Image.alpha_composite(im, Image.fromarray(grad, "RGBA"))

def paste_c(dst: Image.Image, src: Image.Image, cx: int, cy: int, max_w: int | None = None):
    im = src
    if max_w and im.width > max_w:
        sc = max_w / float(im.width)
        im = im.resize((int(round(im.width * sc)), int(round(im.height * sc))), Image.Resampling.LANCZOS)
    dst.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))

def build_clean_f20_studio_stage(ai_bg_pil: Image.Image, showroom_jpg: Path) -> Image.Image:
    """
    Builds an ultra-clean, zero-artifact F20 Brand-Tone Studio Stage (Pure White + F20 Emerald #009E49 + F20 Royal Blue #2563EB):
      1. Soft blurred real F20 showroom gift-set photography subtly blended (14%) into a bright studio Mint-White-Sky gradient
      2. Silky diagonal F20 Emerald & Royal Blue ambient light waves (smooth float32 math, zero HSV posterization!)
      3. Neutral White Carrara Marble & Silver-Emerald Podium extracted cleanly from our AI podium stage!
    """
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    yn, xn = yy / H, xx / W

    # Base bright clean F20 studio gradient (#EAF8F0 top-left -> #FFFFFF center -> #EAF2FE bottom-right)
    base = np.zeros((H, W, 3), dtype=np.float32)
    base[:, :, 0] = 247.0 - 14.0 * (1.0 - xn) * (1.0 - yn) - 10.0 * xn * yn
    base[:, :, 1] = 252.0 - 2.0 * (1.0 - xn) * (1.0 - yn) - 6.0 * xn * yn
    base[:, :, 2] = 249.0 - 8.0 * (1.0 - xn) * (1.0 - yn) + 6.0 * xn * yn

    # Subtle real F20 showroom bokeh depth (12% blend)
    if showroom_jpg.is_file():
        sr = Image.open(showroom_jpg).convert("RGB")
        sw, sh_i = sr.size
        sc = max(W / sw, H / sh_i)
        sr = sr.resize((int(sw * sc), int(sh_i * sc)), Image.Resampling.BILINEAR)
        sr = sr.crop(((sr.width - W) // 2, (sr.height - H) // 2, (sr.width + W) // 2, (sr.height + H) // 2))
        sr_blur = np.array(sr.filter(ImageFilter.GaussianBlur(radius=38)), dtype=np.float32)
        base = base * 0.88 + sr_blur * 0.12

    # Silky F20 Emerald Green (#009E49) top-left wave & F20 Royal Blue (#2563EB) bottom-right wave
    w_green = np.exp(-(((xn - 0.12) / 0.48) ** 2 + ((yn - 0.16) / 0.34) ** 2)) * 0.24
    w_blue  = np.exp(-(((xn - 0.88) / 0.48) ** 2 + ((yn - 0.52) / 0.36) ** 2)) * 0.20
    w_mint  = np.exp(-(((xn - 0.20) / 0.55) ** 2 + ((yn - 0.86) / 0.32) ** 2)) * 0.18

    emerald = np.array([0.0, 158.0, 73.0], dtype=np.float32)
    rblue   = np.array([37.0, 99.0, 235.0], dtype=np.float32)
    for c in range(3):
        base[:, :, c] = base[:, :, c] * (1.0 - w_green) + emerald[c] * w_green
        base[:, :, c] = base[:, :, c] * (1.0 - w_blue)  + rblue[c]   * w_blue
        base[:, :, c] = base[:, :, c] * (1.0 - w_mint)  + emerald[c] * w_mint

    stage = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    # Decorative subtle F20 concentric brand rings behind the gift basket center (540, 620)
    rings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rings)
    rd.ellipse([540 - 330, 625 - 330, 540 + 330, 625 + 330], fill=(255, 255, 255, 115), outline=(0, 158, 73, 55), width=3)
    rd.ellipse([540 - 265, 625 - 265, 540 + 265, 625 + 265], outline=(37, 99, 235, 48), width=2)
    stage = Image.alpha_composite(stage, rings)

    # Clean Studio 3D White Carrara Marble & Brushed F20 Emerald-Silver Podium at y = 835..945px!
    pod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pod)
    # Soft floor shadow under podium
    psh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(psh).ellipse([540 - 355, 922, 540 + 355, 992], fill=(12, 42, 28, 85))
    stage = Image.alpha_composite(stage, psh.filter(ImageFilter.GaussianBlur(radius=20)))

    # Lower metallic emerald-silver base cylinder (x: 205..875)
    for x_i in range(205, 876):
        u = (x_i - 205) / 670.0
        sh_f = 0.55 + 0.45 * math.sin(u * math.pi) ** 1.4
        gc = (int(12 + 45 * sh_f), int(118 + 68 * sh_f), int(62 + 52 * sh_f), 255)
        pd.line([(x_i, 895), (x_i, 942)], fill=gc)
    pd.ellipse([205, 916, 875, 968], fill=(18, 138, 74, 255))
    # Upper white marble cylinder body
    for x_i in range(210, 871):
        u = (x_i - 210) / 660.0
        sh_f = 0.88 + 0.12 * math.sin(u * math.pi)
        mc = (int(236 * sh_f + 16), int(243 * sh_f + 12), int(240 * sh_f + 14), 255)
        pd.line([(x_i, 854), (x_i, 906)], fill=mc)
    pd.ellipse([210, 882, 870, 932], fill=(232, 241, 237, 255), outline=(0, 158, 73, 180), width=3)
    # Crisp bright white top surface of podium
    pd.ellipse([210, 826, 870, 884], fill=(252, 255, 253, 255), outline=(215, 235, 224, 255), width=3)
    stage = Image.alpha_composite(stage, pod)
    return stage.convert("RGB")

def main():
    ai_src = Image.open(V6_DIR / "ai_outro_bg_2011.png").convert("RGB")
    f20_bg = build_clean_f20_studio_stage(ai_src, LOGO_DIR / "showroom_skanest_color_ref_2048w.jpg").convert("RGBA")

    # Paste hands-free REAL F20 20/11 Gift Basket onto the white-marble podium!
    bsk_raw = Image.open(V6_DIR / "real_f20_basket_cutout.png").convert("RGBA")
    bw_t = 415
    bh_t = int(round(bsk_raw.height * (bw_t / bsk_raw.width)))
    bsk = bsk_raw.resize((bw_t, bh_t), Image.Resampling.LANCZOS)

    sh_pod = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh_pod).ellipse([540 - 205, 868 - 28, 540 + 205, 868 + 30], fill=(12, 38, 24, 130))
    f20_bg = Image.alpha_composite(f20_bg, sh_pod.filter(ImageFilter.GaussianBlur(radius=15)))
    f20_bg.alpha_composite(bsk, (540 - bw_t // 2, 876 - bh_t))

    # Build unified F20 Logo-Tone Brand Overlay (100% inside safe zone y: 95 .. 1715px -> 205px bottom safety margin!)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Official F20 Logo (prominent!) + SKA NEST partner badge
    logo_f20 = Image.open(LOGO_DIR / "f20_logo_official.png").convert("RGBA").resize((138, 138), Image.Resampling.LANCZOS)
    logo_ska = Image.open(LOGO_DIR / "skanest_logo_official.png").convert("RGBA").resize((106, 106), Image.Resampling.LANCZOS)

    c1 = Image.new("RGBA", (152, 152), (0, 0, 0, 0))
    ImageDraw.Draw(c1).ellipse([2, 2, 149, 149], fill=(255, 255, 255, 252), outline=(0, 158, 73, 255), width=4)
    paste_c(ui, c1, 468, 128)
    paste_c(ui, logo_f20, 468, 128)

    c2 = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    ImageDraw.Draw(c2).ellipse([2, 2, 117, 117], fill=(255, 255, 255, 252), outline=(37, 99, 235, 255), width=3)
    paste_c(ui, c2, 616, 128)
    paste_c(ui, logo_ska, 616, 128)

    # Headline in F20 Emerald-to-Forest & Royal Blue crisp palette!
    t_hero = make_sep_text(
        "SET QUÀ TRI ÂN 20/11", HERO_TTF, 54,
        fill_top=(0, 168, 78), fill_bot=(10, 112, 56),
        stroke1_col=(255, 255, 255), stroke1_w=14, shadow_a=95
    )
    paste_c(ui, t_hero, W // 2, 246, max_w=940)

    pill_top = Image.new("RGBA", (730, 62), (0, 0, 0, 0))
    pd_t = ImageDraw.Draw(pill_top)
    pd_t.rounded_rectangle([2, 2, 727, 59], radius=29, fill=(29, 92, 208, 248), outline=(255, 255, 255, 255), width=3)
    t_sub = make_sep_text("CÔNG TY TNHH THỰC PHẨM F20  •  THUCPHAMF20.COM", SANS_B, 23, (255, 255, 255), (235, 246, 255), (14, 48, 118), 3, shadow_a=0)
    paste_c(pill_top, t_sub, 365, 31, max_w=695)
    paste_c(ui, pill_top, W // 2, 316)

    # Bottom F20 Brand Contact Card (Clean White + F20 Emerald Green #009E49 & Royal Blue #2563EB! Sits cleanly at y: 1050 .. 1680px -> 240px above bottom!)
    cw_c, ch_c = 940, 600
    card = Image.new("RGBA", (cw_c + 40, ch_c + 40), (0, 0, 0, 0))
    csh = Image.new("RGBA", (cw_c + 40, ch_c + 40), (0, 0, 0, 0))
    ImageDraw.Draw(csh).rounded_rectangle([20, 28, 20 + cw_c, 28 + ch_c], radius=42, fill=(10, 44, 26, 135))
    card = Image.alpha_composite(card, csh.filter(ImageFilter.GaussianBlur(radius=14)))

    cd = ImageDraw.Draw(card)
    # Crisp White body + F20 Emerald Green outer frame + Royal Blue accent pill!
    cd.rounded_rectangle([16, 16, 24 + cw_c, 24 + ch_c], radius=44, fill=(0, 158, 73, 255))
    cd.rounded_rectangle([23, 23, 17 + cw_c, 17 + ch_c], radius=38, fill=(255, 255, 255, 252))
    # Emerald header bar at top of card
    cd.rounded_rectangle([23, 23, 17 + cw_c, 118], radius=38, fill=(0, 152, 70, 255))
    cd.rectangle([23, 82, 17 + cw_c, 118], fill=(0, 152, 70, 255))

    ccx = (cw_c + 40) // 2
    t_cta = make_sep_text("ĐẶT SET QUÀ BIẾU TẶNG SỈ & LẺ", SANS_B, 30, (255, 255, 255), (238, 255, 244), (0, 88, 40), 4, shadow_a=55)
    paste_c(card, t_cta, ccx, 70, max_w=860)

    # Soft Mint-Blue Hotline Pill inside White Card
    cd.rounded_rectangle([58, 142, cw_c - 18, 332], radius=28, fill=(240, 249, 255, 255), outline=(37, 99, 235, 220), width=3)
    t_hl = make_sep_text("HOTLINE / ZALO TƯ VẤN NHANH", SANS_B, 24, (29, 92, 208), (20, 72, 178), (255, 255, 255), 0, shadow_a=0)
    paste_c(card, t_hl, ccx, 182)

    t_ph = make_sep_text(
        "0706.001.626 • 0979.512.289", COINY_TTF, 46,
        fill_top=(0, 158, 73), fill_bot=(0, 118, 54),
        stroke1_col=(255, 255, 255), stroke1_w=8, shadow_a=65
    )
    paste_c(card, t_ph, ccx, 262, max_w=830)

    # Addresses in crisp Forest/Slate & Royal Blue USP!
    t_cs1 = make_sep_text("CS1: 149 Trần Nhật Duật, P. Nha Trang, Khánh Hòa", SANS_B, 25, (16, 48, 32), (16, 48, 32), (255, 255, 255), 0, shadow_a=0)
    t_cs2 = make_sep_text("CS2: 17/3 Điện Biên Phủ, P. Vĩnh Hòa, Nha Trang", SANS_B, 25, (16, 48, 32), (16, 48, 32), (255, 255, 255), 0, shadow_a=0)
    t_usp = make_sep_text("Trực Tiếp Sản Xuất • Giá Tận Xưởng • Nhận Đóng Quà Theo Yêu Cầu", SANS_B, 22, (29, 92, 208), (20, 72, 178), (255, 255, 255), 0, shadow_a=0)
    paste_c(card, t_cs1, ccx, 396, max_w=860)
    paste_c(card, t_cs2, ccx, 452, max_w=860)
    cd.line([(95, 502), (cw_c - 55, 502)], fill=(0, 158, 73, 95), width=2)
    paste_c(card, t_usp, ccx, 548, max_w=860)

    # Center at y = 1365 -> card spans y: 1065 .. 1665px (255px safe margin above 1920px bottom!)
    paste_c(ui, card, W // 2, 1365)

    full_static = Image.alpha_composite(f20_bg, ui).convert("RGB")
    prev_p = WORK / "outro_banner_f20_brand_preview.jpg"
    full_static.save(prev_p, quality=94)

    # Render single unified 1080x1920 30fps MP4 (`outro_banner_f20_brand.mp4`, 3.0s) so ZERO multi-layer PNG crop bugs can ever occur!
    n_f = 90
    out_mp4 = V7_DIR / "outro_banner_f20_brand.mp4"
    rng = np.random.default_rng(2026)
    pts = [(rng.uniform(70, W - 70), rng.uniform(100, H - 200), rng.uniform(3.5, 8.5), rng.uniform(16, 36), rng.uniform(0, 6.28)) for _ in range(24)]

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ], stdin=subprocess.PIPE)

    bg_rgb = f20_bg.convert("RGB")
    for fi in range(n_f):
        t = fi / FPS
        z = 1.0 + 0.028 * (fi / max(1, n_f - 1))
        zw, zh = int(round(W * z)), int(round(H * z))
        fr = bg_rgb.resize((zw, zh), Image.Resampling.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H)).convert("RGBA")
        bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bok)
        for x0, y0, r, vy, ph in pts:
            yy_p = (y0 - vy * t) % H
            xx_p = x0 + math.sin(t * 1.8 + ph) * 12.0
            al = int(50 + 40 * (0.5 + 0.5 * math.sin(t * 2.8 + ph)))
            bd.ellipse([xx_p - r, yy_p - r, xx_p + r, yy_p + r], fill=(195, 255, 220, al))
        fr = Image.alpha_composite(fr, bok.filter(ImageFilter.GaussianBlur(radius=2.0)))
        fr = Image.alpha_composite(fr, ui)
        enc.stdin.write(np.array(fr.convert("RGB"), dtype=np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    print("SUCCESS Built Unified F20 Brand-Tone Closing Banner ->", prev_p)

if __name__ == "__main__":
    main()
