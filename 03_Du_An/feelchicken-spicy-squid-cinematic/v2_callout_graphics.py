import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
from safe_zone_9x16 import audit_rgba_overlay_safe_zone

W, H = 1080, 1920
FONT_DIR = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"

_FONT_CACHE = {}
def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    k = (name, size)
    if k not in _FONT_CACHE:
        p = os.path.join(FONT_DIR, name)
        _FONT_CACHE[k] = ImageFont.truetype(p if os.path.exists(p) else r"C:\Windows\Fonts\arialbd.ttf", size)
    return _FONT_CACHE[k]

def ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_out_back(x: float, s: float = 1.32) -> float:
    x = max(0.0, min(1.0, x)) - 1.0
    return x * x * ((s + 1.0) * x + s) + 1.0

def ease_in_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def draw_diamond(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)

def draw_gradient_headline(
    canvas: Image.Image,
    cx: int,
    cy: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    sheen_pos: float = -1.0,
    alpha_mul: float = 1.0,
):
    bb = font.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 24
    lw, lh = tw + pad * 2, th + pad * 2
    txt_mask = Image.new("L", (lw, lh), 0)
    md = ImageDraw.Draw(txt_mask)
    ox, oy = pad - bb[0], pad - bb[1]
    md.text((ox, oy), text, font=font, fill=255)

    stroke_mask = Image.new("L", (lw, lh), 0)
    sd = ImageDraw.Draw(stroke_mask)
    sd.text((ox, oy), text, font=font, fill=255, stroke_width=6, stroke_fill=255)
    sh_blur = stroke_mask.filter(ImageFilter.GaussianBlur(radius=7.0))

    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    sh_rgba = Image.new("RGBA", (lw, lh), (10, 2, 2, 0))
    sh_rgba.putalpha(Image.fromarray((np.array(sh_blur, dtype=np.float32) * 0.80 * alpha_mul).astype(np.uint8)))
    layer.alpha_composite(sh_rgba, (0, 5))

    st_rgba = Image.new("RGBA", (lw, lh), (48, 8, 6, 0))
    st_rgba.putalpha(Image.fromarray((np.array(stroke_mask, dtype=np.float32) * 0.96 * alpha_mul).astype(np.uint8)))
    layer.alpha_composite(st_rgba, (0, 2))

    yy = np.linspace(0.0, 1.0, lh, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, lw, dtype=np.float32)[None, :]
    stops_t = np.array([0.0, 0.30, 0.52, 0.78, 1.0], dtype=np.float32)
    stops_r = np.array([255, 255, 255, 255, 255], dtype=np.float32)
    stops_g = np.array([248, 214, 252, 172, 108], dtype=np.float32)
    stops_b = np.array([188,  58, 232,  26,  18], dtype=np.float32)
    grad = np.zeros((lh, lw, 4), dtype=np.float32)
    grad[:, :, 0] = np.interp(yy, stops_t, stops_r)
    grad[:, :, 1] = np.interp(yy, stops_t, stops_g)
    grad[:, :, 2] = np.interp(yy, stops_t, stops_b)

    if 0.0 <= sheen_pos <= 1.0:
        diag = xx * 0.82 + yy * 0.18
        band = np.exp(-0.5 * ((diag - sheen_pos) / 0.075) ** 2)
        grad[:, :, 0] = np.clip(grad[:, :, 0] + band * 75.0, 0, 255)
        grad[:, :, 1] = np.clip(grad[:, :, 1] + band * 75.0, 0, 255)
        grad[:, :, 2] = np.clip(grad[:, :, 2] + band * 145.0, 0, 255)

    grad[:, :, 3] = np.array(txt_mask, dtype=np.float32) * alpha_mul
    layer.alpha_composite(Image.fromarray(grad.astype(np.uint8), "RGBA"), (0, 0))
    canvas.alpha_composite(layer, (int(round(cx - lw / 2.0)), int(round(cy - lh / 2.0))))


def draw_hud_callout(
    ov: Image.Image,
    ax: float,
    ay: float,
    kx: float,
    ky: float,
    attach_x: int,
    side: str,
    title: str,
    sub: str,
    ct: float,
    p_out_all: float,
    is_hero: bool = False,
):
    if ct <= 0.0 or p_out_all <= 0.01:
        return

    f_t = fnt("BeVietnamPro-ExtraBold.ttf", 23 if is_hero else 21)
    f_s = fnt("BeVietnamPro-SemiBold.ttf", 17 if is_hero else 16)
    pad_x = 18
    cw = int(math.ceil(max(f_t.getlength(title), f_s.getlength(sub)))) + pad_x * 2 + 8
    ch = 84 if is_hero else 76

    if side == "L":
        card_x1 = attach_x
        card_x0 = max(58, card_x1 - cw)
        cw = card_x1 - card_x0
    else:
        card_x0 = attach_x
        max_r = 880 if (ky + ch // 2) >= 860 else 1018
        card_x1 = min(max_r, card_x0 + cw)
        cw = card_x1 - card_x0

    p_dot  = ease_out_cubic(min(1.0, ct / 0.16))
    p_line = ease_out_cubic(min(1.0, max(0.0, (ct - 0.04) / 0.25)))
    p_card = min(1.0, max(0.0, (ct - 0.13) / 0.27))

    al_master = p_out_all
    axi, ayi = int(round(ax)), int(round(ay))
    kxi, kyi = int(round(kx)), int(round(ky))

    line_lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(line_lay)

    pulse_phase = (ct * 1.7) % 1.0
    r_pulse = int(round(9 + 16 * ease_out_cubic(pulse_phase)))
    a_pulse = int(round(195 * (1.0 - pulse_phase) * p_dot * al_master))
    if a_pulse > 6 and ayi - r_pulse >= 250 and ayi + r_pulse <= 1544 and axi - r_pulse >= 55:
        ld.ellipse([axi - r_pulse, ayi - r_pulse, axi + r_pulse, ayi + r_pulse], outline=(255, 214, 68, a_pulse), width=2)

    r_out = int(round((11 if is_hero else 9) * p_dot))
    if r_out >= 3:
        a_d = int(round(252 * p_dot * al_master))
        ld.ellipse([axi - r_out - 2, ayi - r_out - 2, axi + r_out + 2, ayi + r_out + 2], fill=(12, 5, 5, int(a_d * 0.76)))
        ld.ellipse([axi - r_out, ayi - r_out, axi + r_out, ayi + r_out], outline=(255, 210, 56, a_d), width=3)
        ld.ellipse([axi - 4, ayi - 4, axi + 4, ayi + 4], fill=(255, 252, 240, a_d))

    seg1_len = math.hypot(kxi - axi, kyi - ayi)
    seg2_len = abs(attach_x - kxi)
    tot_len = max(1.0, seg1_len + seg2_len)
    cur_len = tot_len * p_line

    pts = [(axi, ayi)]
    if cur_len <= seg1_len:
        r1 = cur_len / max(1.0, seg1_len)
        pts.append((int(round(axi + (kxi - axi) * r1)), int(round(ayi + (kyi - ayi) * r1))))
    else:
        pts.append((kxi, kyi))
        r2 = (cur_len - seg1_len) / max(1.0, seg2_len)
        pts.append((int(round(kxi + (attach_x - kxi) * r2)), kyi))

    if len(pts) >= 2 and p_line > 0.02:
        a_ln = int(round(248 * al_master))
        ld.line(pts, fill=(10, 4, 4, int(a_ln * 0.82)), width=6, joint="curve")
        line_col = (255, 214, 68, a_ln) if is_hero else (255, 236, 175, a_ln)
        ld.line(pts, fill=line_col, width=3, joint="curve")
        if p_line < 0.98:
            tx, ty = pts[-1]
            ld.ellipse([tx - 6, ty - 6, tx + 6, ty + 6], fill=(255, 248, 210, a_ln))

    ov.alpha_composite(line_lay)

    if p_card > 0.02:
        ec = ease_out_cubic(p_card)
        eb = ease_out_back(p_card, 1.24)
        cy0 = kyi - ch // 2

        card_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card_im)

        bg_col = (30, 11, 9, 230) if is_hero else (16, 10, 10, 222)
        bd_col = (255, 206, 56, 250) if is_hero else (255, 198, 82, 208)
        cd.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=14, fill=bg_col, outline=bd_col, width=2)

        acc_col = (255, 208, 48, 255) if is_hero else (255, 96, 36, 255)
        if side == "L":
            cd.rounded_rectangle([cw - 7, 10, cw - 2, ch - 10], radius=3, fill=acc_col)
            tw1 = f_t.getlength(title)
            tw2 = f_s.getlength(sub)
            cd.text((cw - pad_x - tw1, 11 if is_hero else 10), title, font=f_t, fill=(255, 220, 72, 255) if is_hero else (255, 234, 142, 255))
            cd.text((cw - pad_x - tw2, 45 if is_hero else 41), sub, font=f_s, fill=(248, 242, 232, 242))
        else:
            cd.rounded_rectangle([2, 10, 7, ch - 10], radius=3, fill=acc_col)
            cd.text((pad_x, 11 if is_hero else 10), title, font=f_t, fill=(255, 220, 72, 255) if is_hero else (255, 234, 142, 255))
            cd.text((pad_x, 45 if is_hero else 41), sub, font=f_s, fill=(248, 242, 232, 242))

        blur_r = max((1.0 - ec) * 8.5, (1.0 - p_out_all) * 7.5)
        if blur_r > 0.4:
            card_im = card_im.filter(ImageFilter.GaussianBlur(radius=blur_r))

        sc = (0.90 + 0.10 * eb) if p_card < 1.0 else 1.0
        if abs(sc - 1.0) > 0.003:
            nw, nh = max(8, int(round(cw * sc))), max(8, int(round(ch * sc)))
            card_im = card_im.resize((nw, nh), Image.Resampling.BILINEAR)
            px = card_x0 + (cw - nw) // 2
            py = cy0 + (ch - nh) // 2
        else:
            px, py = card_x0, cy0

        a_mul = ec * al_master
        if a_mul < 0.999:
            arr = np.array(card_im, dtype=np.float32)
            arr[:, :, 3] *= max(0.0, min(1.0, a_mul))
            card_im = Image.fromarray(arr.astype(np.uint8), "RGBA")

        ov.alpha_composite(card_im, (px, py))


def render_master_overlay(t: float) -> tuple[Image.Image, float]:
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # --- 1. OPENING HOOK TITLE (0.12s -> 2.62s) ---
    if 0.12 <= t <= 2.62:
        lt, dur = t - 0.12, 2.50
        p_in = ease_out_cubic(min(1.0, lt / 0.28))
        p_out = ease_in_out(min(1.0, (dur - lt) / 0.24))
        am = p_in * p_out

        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)

        f_brand = fnt("BeVietnamPro-ExtraBold.ttf", 21)
        b_txt = "FEEL CHICKEN NHA TRANG"
        tw_b = f_brand.getlength(b_txt)
        bw = int(tw_b) + 72
        bx0 = 540 - bw // 2
        d.rounded_rectangle([bx0, 492, bx0 + bw, 540], radius=24, fill=(188, 18, 22, int(238 * am)), outline=(255, 212, 68, int(248 * am)), width=2)
        d.text((540 - tw_b / 2, 502), b_txt, font=f_brand, fill=(255, 246, 205, int(255 * am)))
        draw_diamond(d, bx0 + 20, 516, 5.5, (255, 216, 72, int(255 * am)))
        draw_diamond(d, bx0 + bw - 20, 516, 5.5, (255, 216, 72, int(255 * am)))

        sheen = (lt - 0.25) / 1.35 if 0.25 <= lt <= 1.60 else -1.0
        f_h1 = fnt("BarlowCondensed-ExtraBold.ttf", 104)
        f_h2 = fnt("BarlowCondensed-ExtraBold.ttf", 112)
        draw_gradient_headline(lay, 540, 608, "MÌ CAY MỰC", f_h1, sheen_pos=sheen, alpha_mul=am)
        draw_gradient_headline(lay, 540, 732, "KHỔNG LỒ", f_h2, sheen_pos=sheen, alpha_mul=am)

        f_sub = fnt("BeVietnamPro-Bold.ttf", 22)
        s_txt = "MỰC ỐNG NGUYÊN CON 250G–300G  •  7 CẤP ĐỘ CAY"
        sw = int(f_sub.getlength(s_txt)) + 46
        sx0 = 540 - sw // 2
        d.rounded_rectangle([sx0, 796, sx0 + sw, 848], radius=14, fill=(18, 8, 8, int(220 * am)), outline=(255, 196, 64, int(215 * am)), width=2)
        d.text((540 - f_sub.getlength(s_txt) / 2, 808), s_txt, font=f_sub, fill=(255, 232, 145, int(252 * am)))

        blur_r = max((1.0 - p_in) * 10.0, (1.0 - p_out) * 8.0)
        if blur_r > 0.4:
            lay = lay.filter(ImageFilter.GaussianBlur(radius=blur_r))
        return lay, 0.34 * am

    # --- 2. SCENE 7 EXPLODED TOWER: 6 MOTION-TRACKED INGREDIENT CALLOUTS (13.45s -> 17.95s) ---
    if 13.45 <= t <= 17.95:
        lt, dur = t - 13.45, 4.50
        prog = max(0.0, min(1.0, lt / dur))
        p_out_all = ease_in_out(min(1.0, (dur - lt) / 0.24))

        def lerp(a, b):
            return a + (b - a) * prog

        specs = [
            # (delay, ax, ay, kx, ky, attach_x, side, title, sub, is_hero)
            (0.08, lerp(535, 530), lerp(274, 268), 598, 304, 622, "R", "ỚT CAY 7 CẤP ĐỘ",      "Bắp cải tím & bột ớt Hàn",    False),
            (0.42, lerp(395, 388), lerp(352, 336), 362, 428, 344, "L", "CẢI THÌA TƯƠI XANH",    "Rau ngọt giòn thanh mát",     False),
            (0.76, lerp(668, 658), lerp(580, 602), 692, 558, 712, "R", "XÚC XÍCH & CÁ VIÊN",    "Đầy ắp nhân ngon đậm đà",     False),
            (1.10, lerp(522, 512), lerp(925, 962), 462, 810, 442, "L", "MỰC ỐNG 250G – 300G",   "Nguyên con giòn sần sật",     True),
            (1.44, lerp(568, 562), lerp(1245, 1308), 448, 1368, 428, "L", "MÌ SỢI HÀN QUỐC",     "Xoăn vàng dai thấm đẫm súp",  False),
            (1.78, lerp(448, 448), lerp(1522, 1522), 504, 1482, 526, "R", "NƯỚC DÙNG THỐ ĐÁ",    "Hầm xương cay nồng bốc khói", False),
        ]
        for stg, ax, ay, kx, ky, att_x, side, tl, sb, hero in specs:
            draw_hud_callout(ov, ax, ay, kx, ky, att_x, side, tl, sb, lt - stg, p_out_all, is_hero=hero)
        return ov, 0.0

    # --- 3. SCENE 8 COMPLETED HERO CLAYPOT: END-CARD + 3 LIVE BOWL CALLOUTS (19.32s -> 24.00s) ---
    if 19.32 <= t <= 24.00:
        lt = t - 19.32
        p_in = ease_out_cubic(min(1.0, lt / 0.30))
        p_out = 1.0 if t < 23.82 else ease_in_out(max(0.25, (24.00 - t) / 0.18))
        am = p_in * p_out

        d = ImageDraw.Draw(ov)

        f_kicker = fnt("BeVietnamPro-Bold.ttf", 22)
        k_txt = "FEEL CHICKEN  •  MÓN MỚI BÙNG NỔ"
        d.text((540 - f_kicker.getlength(k_txt) / 2, 268), k_txt, font=f_kicker, fill=(255, 224, 128, int(248 * am)))

        sheen = (lt - 0.28) / 1.45 if 0.28 <= lt <= 1.73 else -1.0
        f_title = fnt("BarlowCondensed-ExtraBold.ttf", 94)
        draw_gradient_headline(ov, 540, 356, "MÌ CAY MỰC KHỔNG LỒ", f_title, sheen_pos=sheen, alpha_mul=am)

        f_prc = fnt("BeVietnamPro-ExtraBold.ttf", 34)
        p_txt = "CHỈ 99K / TÔ  •  ĐỦ 7 CẤP ĐỘ CAY"
        pw = int(f_prc.getlength(p_txt)) + 64
        px0 = 540 - pw // 2
        d.rounded_rectangle([px0, 424, px0 + pw, 496], radius=36, fill=(208, 18, 24, int(246 * am)), outline=(255, 216, 68, int(255 * am)), width=3)
        d.text((540 - f_prc.getlength(p_txt) / 2, 438), p_txt, font=f_prc, fill=(255, 244, 130, int(255 * am)))

        bowl_specs = [
            (0.30, 445,  695, 398,  615, 380, "L", "RÂU MỰC XÒE TƯƠI",    "Giòn ngọt tự nhiên",       False),
            (0.62, 535, 1045, 448,  935, 430, "L", "MỰC ỐNG NGUYÊN CON",  "Khía khoanh thấm đẫm sốt", True),
            (0.94, 196, 1308, 405, 1345, 430, "R", "SÚP CAY HÀN & MÌ DAI","Nóng hổi giữ nhiệt lâu",   False),
        ]
        for stg, ax, ay, kx, ky, att_x, side, tl, sb, hero in bowl_specs:
            draw_hud_callout(ov, ax, ay, kx, ky, att_x, side, tl, sb, lt - stg, p_out, is_hero=hero)

        if lt > 0.18:
            pa = ease_out_cubic(min(1.0, (lt - 0.18) / 0.28)) * p_out
            d.rounded_rectangle([62, 1424, 876, 1534], radius=18, fill=(16, 9, 9, int(228 * pa)), outline=(255, 198, 68, int(218 * pa)), width=2)
            f_ad1 = fnt("BeVietnamPro-Bold.ttf", 20)
            f_ad2 = fnt("BeVietnamPro-ExtraBold.ttf", 21)
            t1 = "CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt"
            t2 = "Mở cửa: 10:00 – 22:00   •   Hotline: 0796 601 106"
            cx_bar = (62 + 876) / 2.0
            d.text((cx_bar - f_ad1.getlength(t1) / 2, 1440), t1, font=f_ad1, fill=(255, 246, 232, int(252 * pa)))
            d.text((cx_bar - f_ad2.getlength(t2) / 2, 1482), t2, font=f_ad2, fill=(255, 214, 72, int(255 * pa)))

        return ov, 0.16 * am

    return ov, 0.0
