import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from batch_step6_render_all_17 import (
    W, H, FONT_TITLE, FONT_BLACK, FONT_EBOLD, FONT_BOLD, FONT_SERIF,
    get_font, clamp01, smoothstep, ease_out_cubic, ease_out_back,
    fit_cover, render_glow_text_sprite, paste_centered, draw_suit_icon,
)

CENTER_X = 540
SAFE_LOW_MAX_W = 672  # X in [204..876] <= 884px AND 100% Dead-Center on X = 540!

_comp_cache = {}


def _wrap_text(draw, text, font, max_w):
    lines = []
    for raw_ln in str(text).split("\n"):
        words = raw_ln.split()
        if not words:
            continue
        cur = words[0]
        for w in words[1:]:
            cand = cur + " " + w
            if draw.textbbox((0, 0), cand, font=font)[2] <= max_w:
                cur = cand
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines[:3]


# ==============================================================================
# 1. NATIVE KOBE LIGHT SAAS UI CARD (Pure White #FFFFFF + Step Badge + Skeleton Bars)
# ==============================================================================
def make_kobe_saas_step_card(w, h, step_num, icon_kind, accent_rgb, title_txt, sub_txt, tag_txt=None):
    key = ("KOBE_SAAS_CARD", w, h, step_num, icon_kind, accent_rgb, title_txt, sub_txt, tag_txt)
    if key in _comp_cache:
        return _comp_cache[key]

    pad = 18
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius=28, fill=(16, 26, 56, 72))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=9)))

    d = ImageDraw.Draw(im)
    x0, y0 = pad, pad
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=28, fill=(255, 255, 255, 253), outline=(*accent_rgb, 185), width=3)
    # Top accent bar
    d.rounded_rectangle([x0 + 22, y0 + 14, x0 + w - 22, y0 + 22], radius=4, fill=(*accent_rgb, 65))

    # Solid circular number badge (Top-Left) + Vector Icon Pill (Top-Right)
    d.ellipse([x0 + 18, y0 + 30, x0 + 66, y0 + 78], fill=(16, 22, 38, 255))
    fn_n = get_font(FONT_BLACK, 26)
    s_str = str(step_num)
    bn = d.textbbox((0, 0), s_str, font=fn_n)
    d.text((x0 + 42 - (bn[2] - bn[0]) * 0.5, y0 + 54 - (bn[1] + bn[3]) * 0.5), s_str, font=fn_n, fill=(255, 255, 255, 255))

    d.ellipse([x0 + w - 66, y0 + 30, x0 + w - 18, y0 + 78], fill=(*accent_rgb, 36), outline=(*accent_rgb, 190), width=2)
    draw_suit_icon(d, icon_kind, x0 + w - 42, y0 + 54, 14, (*accent_rgb, 255))

    # Bold Title
    ft = get_font(FONT_BLACK, 30 if w >= 260 else 26)
    t_clean = title_txt.replace("\n", " ").upper()
    while ft.size > 18 and d.textbbox((0, 0), t_clean, font=ft)[2] > w - 32:
        ft = get_font(FONT_BLACK, ft.size - 2)
    bt = d.textbbox((0, 0), t_clean, font=ft)
    d.text((x0 + w * 0.5 - (bt[2] - bt[0]) * 0.5, y0 + 96), t_clean, font=ft, fill=(16, 22, 38, 255))

    # Clean Subtitle
    fs = get_font(FONT_BOLD, 22 if w >= 260 else 20)
    s_lines = _wrap_text(d, sub_txt, fs, w - 34)
    sy = y0 + 142
    for sl in s_lines[:2]:
        bs = d.textbbox((0, 0), sl, font=fs)
        d.text((x0 + w * 0.5 - (bs[2] - bs[0]) * 0.5, sy), sl, font=fs, fill=(64, 76, 98, 255))
        sy += 29

    # Kobe Signature Skeleton UI Bars or Tag Pill at Bottom!
    if tag_txt:
        d.rounded_rectangle([x0 + 20, y0 + h - 54, x0 + w - 20, y0 + h - 16], radius=18, fill=(*accent_rgb, 30), outline=(*accent_rgb, 180), width=2)
        fg = get_font(FONT_EBOLD, 19)
        t_up = str(tag_txt).upper()
        while fg.size > 14 and d.textbbox((0, 0), t_up, font=fg)[2] > w - 52:
            fg = get_font(FONT_EBOLD, fg.size - 1)
        bg_b = d.textbbox((0, 0), t_up, font=fg)
        d.text((x0 + w * 0.5 - (bg_b[2] - bg_b[0]) * 0.5, y0 + h - 35 - (bg_b[1] + bg_b[3]) * 0.5), t_up, font=fg, fill=(*accent_rgb, 255))
    else:
        d.rounded_rectangle([x0 + 26, y0 + h - 46, x0 + w - 56, y0 + h - 34], radius=6, fill=(220, 226, 240, 255))
        d.rounded_rectangle([x0 + 26, y0 + h - 26, x0 + w - 92, y0 + h - 14], radius=6, fill=(*accent_rgb, 95))

    _comp_cache[key] = im
    return im


def make_clean_broll_viewport(vid_rgb, w, h, pill_txt, foot_txt, accent_rgb=(54, 86, 251), light_ui=True, zoom=1.03):
    """Modern SaaS / Editorial / Cyber rounded live-video window (ZERO playing-card ranks/suits!)."""
    pad = 16
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius=30, fill=(8, 14, 28, 115))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=9)))

    vis = fit_cover(vid_rgb, w, h, zoom).convert("RGBA")
    arr = np.array(vis, dtype=np.float32)
    # Darken bottom 34% smoothly for crisp big footer caption
    grad = np.clip((np.arange(h, dtype=np.float32) - h * 0.58) / (h * 0.42), 0.0, 1.0)[:, None, None]
    arr[:, :, :3] *= (1.0 - 0.72 * grad)
    vis = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=255)
    v_layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    v_layer.paste(vis, (pad, pad), mask=mask)
    im = Image.alpha_composite(im, v_layer)

    d = ImageDraw.Draw(im)
    border_c = (255, 255, 255, 245) if light_ui else (*accent_rgb, 235)
    d.rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius=30, outline=border_c, width=5)

    if pill_txt:
        fp = get_font(FONT_EBOLD, 23)
        p_up = pill_txt.upper()
        while fp.size > 15 and d.textbbox((0, 0), p_up, font=fp)[2] > w - 68:
            fp = get_font(FONT_EBOLD, fp.size - 2)
        bp = d.textbbox((0, 0), p_up, font=fp)
        pw_p = (bp[2] - bp[0]) + 36
        px0 = pad + int((w - pw_p) * 0.5)
        d.rounded_rectangle([px0, pad + 16, px0 + pw_p, pad + 56], radius=20,
                            fill=(255, 255, 255, 246) if light_ui else (14, 22, 38, 236),
                            outline=(*accent_rgb, 220), width=2)
        d.text((px0 + 18 - bp[0], pad + 36 - (bp[1] + bp[3]) * 0.5), p_up, font=fp,
               fill=(16, 24, 42, 255) if light_ui else (255, 242, 165, 255))

    if foot_txt:
        ff = get_font(FONT_BLACK, 30)
        while ff.size > 19 and d.textbbox((0, 0), foot_txt, font=ff)[2] > w - 44:
            ff = get_font(FONT_BLACK, ff.size - 2)
        bf = d.textbbox((0, 0), foot_txt, font=ff)
        fx = pad + w * 0.5 - (bf[2] - bf[0]) * 0.5
        fy = pad + h - 38 - (bf[1] + bf[3]) * 0.5
        d.text((fx, fy + 2), foot_txt, font=ff, fill=(0, 0, 0, 220))
        d.text((fx, fy), foot_txt, font=ff, fill=(255, 248, 210, 255))

    return im


# ==============================================================================
# 2. NATIVE KOBE DARK CYBER HUD CARD (Chamfered Tech Corners + Neon Brackets)
# ==============================================================================
def make_cyber_hud_card(w, h, code_lbl, pri_rgb, sec_rgb, title_txt, sub_txt, big_metric=None):
    key = ("CYBER_HUD", w, h, code_lbl, pri_rgb, sec_rgb, title_txt, sub_txt, big_metric)
    if key in _comp_cache:
        return _comp_cache[key]

    pad = 16
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0 = pad, pad
    # Dark slate glass body + neon rim
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=20, fill=(18, 24, 34, 244), outline=(*pri_rgb, 155), width=2)
    # 4 Glowing Cyber Corner Brackets [ ]
    bl = 26
    for cx_b, cy_b, sx, sy in [(x0, y0, 1, 1), (x0 + w, y0, -1, 1), (x0, y0 + h, 1, -1), (x0 + w, y0 + h, -1, -1)]:
        d.line([(cx_b, cy_b), (cx_b + sx * bl, cy_b)], fill=(*pri_rgb, 255), width=5)
        d.line([(cx_b, cy_b), (cx_b, cy_b + sy * bl)], fill=(*pri_rgb, 255), width=5)

    # Top status chip
    fc = get_font(FONT_EBOLD, 19)
    d.rounded_rectangle([x0 + 18, y0 + 16, x0 + w - 18, y0 + 50], radius=10, fill=(*pri_rgb, 34))
    bc = d.textbbox((0, 0), str(code_lbl).upper(), font=fc)
    d.text((x0 + w * 0.5 - (bc[2] - bc[0]) * 0.5, y0 + 33 - (bc[1] + bc[3]) * 0.5), str(code_lbl).upper(), font=fc, fill=(*pri_rgb, 255))

    cur_y = y0 + 68
    if big_metric:
        fm = get_font(FONT_BLACK, 54)
        while fm.size > 30 and d.textbbox((0, 0), str(big_metric), font=fm)[2] > w - 32:
            fm = get_font(FONT_BLACK, fm.size - 3)
        bm = d.textbbox((0, 0), str(big_metric), font=fm)
        d.text((x0 + w * 0.5 - (bm[2] - bm[0]) * 0.5, cur_y), str(big_metric), font=fm, fill=(*sec_rgb, 255))
        cur_y += (bm[3] - bm[1]) + 16

    ft = get_font(FONT_BLACK, 29)
    t_s = title_txt.replace("\n", " ").upper()
    while ft.size > 18 and d.textbbox((0, 0), t_s, font=ft)[2] > w - 30:
        ft = get_font(FONT_BLACK, ft.size - 2)
    bt = d.textbbox((0, 0), t_s, font=ft)
    d.text((x0 + w * 0.5 - (bt[2] - bt[0]) * 0.5, cur_y), t_s, font=ft, fill=(255, 255, 255, 255))
    cur_y += (bt[3] - bt[1]) + 14

    fs = get_font(FONT_BOLD, 21)
    for sl in _wrap_text(d, sub_txt, fs, w - 32)[:2]:
        bs = d.textbbox((0, 0), sl, font=fs)
        d.text((x0 + w * 0.5 - (bs[2] - bs[0]) * 0.5, cur_y), sl, font=fs, fill=(198, 214, 232, 255))
        cur_y += 27

    _comp_cache[key] = im
    return im


# ==============================================================================
# 3. NATIVE SAAS FROSTED GLASSMORPHISM CARD (Icy Rim + Specular Top Sheen)
# ==============================================================================
def make_frosted_glass_card(w, h, badge_txt, title_txt, sub_txt, big_val=None, tint_rgb=(28, 68, 128), rim_rgb=(135, 222, 255)):
    key = ("SAAS_GLASS", w, h, badge_txt, title_txt, sub_txt, big_val, tint_rgb, rim_rgb)
    if key in _comp_cache:
        return _comp_cache[key]

    pad = 16
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + w, pad + h + 8], radius=30, fill=(4, 10, 26, 145))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    d = ImageDraw.Draw(im)
    x0, y0 = pad, pad
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=30, fill=(*tint_rgb, 212), outline=(*rim_rgb, 215), width=3)
    # Specular glass top highlight
    d.rounded_rectangle([x0 + 24, y0 + 8, x0 + w - 24, y0 + 14], radius=3, fill=(255, 255, 255, 130))

    cy_t = y0 + 22
    if badge_txt:
        fb = get_font(FONT_EBOLD, 20)
        b_up = badge_txt.upper()
        while fb.size > 14 and d.textbbox((0, 0), b_up, font=fb)[2] > w - 48:
            fb = get_font(FONT_EBOLD, fb.size - 1)
        bb = d.textbbox((0, 0), b_up, font=fb)
        pw_b = (bb[2] - bb[0]) + 32
        bx0 = x0 + int((w - pw_b) * 0.5)
        d.rounded_rectangle([bx0, cy_t, bx0 + pw_b, cy_t + 36], radius=18, fill=(255, 255, 255, 36), outline=(*rim_rgb, 185), width=2)
        d.text((bx0 + 16 - bb[0], cy_t + 18 - (bb[1] + bb[3]) * 0.5), b_up, font=fb, fill=(255, 244, 175, 255))
        cy_t += 50

    if big_val:
        fv = get_font(FONT_BLACK, 56)
        while fv.size > 30 and d.textbbox((0, 0), str(big_val), font=fv)[2] > w - 32:
            fv = get_font(FONT_BLACK, fv.size - 3)
        bv = d.textbbox((0, 0), str(big_val), font=fv)
        d.text((x0 + w * 0.5 - (bv[2] - bv[0]) * 0.5, cy_t), str(big_val), font=fv, fill=(255, 238, 122, 255))
        cy_t += (bv[3] - bv[1]) + 14

    ft = get_font(FONT_BLACK, 32)
    for tl in _wrap_text(d, title_txt.upper(), ft, w - 36)[:2]:
        while ft.size > 20 and d.textbbox((0, 0), tl, font=ft)[2] > w - 32:
            ft = get_font(FONT_BLACK, ft.size - 2)
        bt = d.textbbox((0, 0), tl, font=ft)
        d.text((x0 + w * 0.5 - (bt[2] - bt[0]) * 0.5, cy_t), tl, font=ft, fill=(255, 255, 255, 255))
        cy_t += (bt[3] - bt[1]) + 10

    fs = get_font(FONT_BOLD, 22)
    cy_t += 4
    for sl in _wrap_text(d, sub_txt, fs, w - 36)[:2]:
        bs = d.textbbox((0, 0), sl, font=fs)
        d.text((x0 + w * 0.5 - (bs[2] - bs[0]) * 0.5, cy_t), sl, font=fs, fill=(214, 238, 255, 255))
        cy_t += 28

    _comp_cache[key] = im
    return im


# ==============================================================================
# 4. NATIVE HD-CL MINIMAL EDITORIAL PAPER CARD & ARCH PORTRAIT PiP
# ==============================================================================
def make_editorial_paper_card(w, h, kicker_txt, serif_title, sub_txt, metric_txt=None, accent_rgb=(176, 98, 18)):
    key = ("EDITORIAL_PAPER", w, h, kicker_txt, serif_title, sub_txt, metric_txt, accent_rgb)
    if key in _comp_cache:
        return _comp_cache[key]

    pad = 14
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + 4, pad + 8, pad + w + 4, pad + h + 8], radius=16, fill=(36, 26, 14, 68))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=6)))

    d = ImageDraw.Draw(im)
    x0, y0 = pad, pad
    # Warm ivory archival paper + fine double ink rule
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=16, fill=(253, 249, 240, 255), outline=(34, 28, 22, 235), width=2)
    d.rounded_rectangle([x0 + 8, y0 + 8, x0 + w - 8, y0 + h - 8], radius=11, outline=(*accent_rgb, 130), width=1)

    cy = y0 + 20
    if kicker_txt:
        fk = get_font(FONT_EBOLD, 19)
        k_up = f"— {kicker_txt.upper()} —"
        while fk.size > 13 and d.textbbox((0, 0), k_up, font=fk)[2] > w - 36:
            fk = get_font(FONT_EBOLD, fk.size - 1)
        bk = d.textbbox((0, 0), k_up, font=fk)
        d.text((x0 + w * 0.5 - (bk[2] - bk[0]) * 0.5, cy), k_up, font=fk, fill=(*accent_rgb, 255))
        cy += 34

    if metric_txt:
        fm = get_font(FONT_SERIF, 50)
        while fm.size > 28 and d.textbbox((0, 0), str(metric_txt), font=fm)[2] > w - 36:
            fm = get_font(FONT_SERIF, fm.size - 3)
        bm = d.textbbox((0, 0), str(metric_txt), font=fm)
        d.text((x0 + w * 0.5 - (bm[2] - bm[0]) * 0.5, cy), str(metric_txt), font=fm, fill=(22, 20, 18, 255))
        cy += (bm[3] - bm[1]) + 12

    ft = get_font(FONT_SERIF, 34)
    for tl in _wrap_text(d, serif_title, ft, w - 38)[:2]:
        while ft.size > 20 and d.textbbox((0, 0), tl, font=ft)[2] > w - 36:
            ft = get_font(FONT_SERIF, ft.size - 2)
        bt = d.textbbox((0, 0), tl, font=ft)
        d.text((x0 + w * 0.5 - (bt[2] - bt[0]) * 0.5, cy), tl, font=ft, fill=(22, 20, 18, 255))
        cy += (bt[3] - bt[1]) + 10

    d.line([(x0 + 48, cy + 4), (x0 + w - 48, cy + 4)], fill=(*accent_rgb, 145), width=2)
    cy += 16
    fs = get_font(FONT_BOLD, 21)
    for sl in _wrap_text(d, sub_txt, fs, w - 38)[:2]:
        bs = d.textbbox((0, 0), sl, font=fs)
        d.text((x0 + w * 0.5 - (bs[2] - bs[0]) * 0.5, cy), sl, font=fs, fill=(76, 68, 58, 255))
        cy += 27

    _comp_cache[key] = im
    return im


def draw_editorial_arch_pip(canvas_im, fg_rgb, t, s0, s1, cx=540, cy=1318, w=292, h=336, accent_rgb=(184, 108, 18)):
    """Editorial Dome-Arch Live Speaker Portrait PiP (Distinct from Circle PiP!)."""
    u = min(ease_out_cubic(min(1.0, max(0.0, t - s0) / 0.26)), ease_out_cubic(min(1.0, max(0.0, s1 - t) / 0.22)))
    if u <= 0.03:
        return
    crop_w, crop_h = 440, 506
    x0, y0 = max(0, 540 - crop_w // 2), max(0, 755 - crop_h // 2)
    sub = Image.fromarray(np.ascontiguousarray(fg_rgb[y0:y0 + crop_h, x0:x0 + crop_w]), "RGB").resize((w, h), Image.Resampling.BICUBIC).convert("RGBA")

    pad = 20
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.pieslice([0, 0, w - 1, w - 1], 180, 360, fill=255)
    md.rectangle([0, w // 2, w - 1, h - 1], fill=255)

    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste((32, 24, 14, 95), (pad, pad + 10), mask=mask)
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=9)))

    v_l = Image.new("RGBA", im.size, (0, 0, 0, 0))
    v_l.paste(sub, (pad, pad), mask=mask)
    im = Image.alpha_composite(im, v_l)

    d = ImageDraw.Draw(im)
    d.arc([pad, pad, pad + w - 1, pad + w - 1], 180, 360, fill=(253, 249, 240, 255), width=6)
    d.line([(pad, pad + w // 2), (pad, pad + h - 1), (pad + w - 1, pad + h - 1), (pad + w - 1, pad + w // 2)], fill=(253, 249, 240, 255), width=6)
    d.arc([pad - 4, pad - 4, pad + w + 3, pad + w + 3], 180, 360, fill=(*accent_rgb, 235), width=3)
    paste_centered(canvas_im, im, cx, cy + (1.0 - u) * 24.0, scale_x=0.92 + 0.08 * u, opacity=u)


# ==============================================================================
# 5. NATIVE VIỆT-HÀN 5-CELL LIVE BENTO STAGE (3 Top + 2 Symmetric Bottom @ X=540!)
# ==============================================================================
def render_viethan_5cell_bento(stage_im, dt, brolls, cfg, assets):
    """
    Signature Việt-Hàn / Thiện Trang 5-Cell Rounded Bento Grid:
    - Yellow/Emerald Branded Header Pill at Y=306 (cx=540)
    - Top Row (Y=510, <860): 3 Rounded Cells at cx = [214, 540, 866] (w=292, h=268)
    - Bottom Row (Y=820..1095): 2 Symmetric Cells at cx = [378, 702] (w=308, h=256 -> X in [224..856] <= 884px AND midpoint=540!)
    """
    fn_c = cfg["fan"]
    rf_c = cfg["riffle"]

    # Header Banner
    hdr = Image.new("RGBA", (900, 96), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hdr)
    hd.rounded_rectangle([4, 4, 895, 91], radius=24, fill=(255, 232, 36, 252), outline=(255, 255, 255, 255), width=4)
    fh = get_font(FONT_BLACK, 38)
    h_txt = fn_c["headline"].upper()
    while fh.size > 22 and hd.textbbox((0, 0), h_txt, font=fh)[2] > 852:
        fh = get_font(FONT_BLACK, fh.size - 2)
    bh = hd.textbbox((0, 0), h_txt, font=fh)
    hd.text((450 - (bh[2] - bh[0]) * 0.5, 48 - (bh[1] + bh[3]) * 0.5), h_txt, font=fh, fill=(10, 114, 56, 255))
    paste_centered(stage_im, hdr, CENTER_X, 304)

    cells_5 = [
        (214, 515, 294, 272, 0, fn_c["left"][3],  (218, 18, 42)),
        (540, 515, 294, 272, 1, fn_c["right"][3], (12, 134, 72)),
        (866, 515, 294, 272, 2, fn_c["ace"][3],   (12, 134, 72)),
        (378, 832, 308, 264, 3, rf_c["c1"][3],    (184, 112, 12)),
        (702, 832, 308, 264, 2, rf_c["hero"][6],  (218, 18, 42)),
    ]
    for idx_c, (cx_c, cy_c, cw_c, ch_c, br_i, lbl_c, col_c) in enumerate(cells_5):
        ts_c = idx_c * 0.14
        if dt >= ts_c:
            uc = ease_out_back(min(1.0, (dt - ts_c) / 0.28), 1.10)
            br_clip = brolls[br_i % len(brolls)]
            frm_rgb = br_clip[int((dt * 30 + idx_c * 17) % len(br_clip))]
            vis = fit_cover(frm_rgb, cw_c, ch_c, 1.05).convert("RGBA")
            m_c = Image.new("L", (cw_c, ch_c), 0)
            ImageDraw.Draw(m_c).rounded_rectangle([0, 0, cw_c - 1, ch_c - 1], radius=24, fill=255)

            box = Image.new("RGBA", (cw_c + 12, ch_c + 12), (0, 0, 0, 0))
            box.paste(vis, (6, 6), mask=m_c)
            bd = ImageDraw.Draw(box)
            bd.rounded_rectangle([6, 6, cw_c + 5, ch_c + 5], radius=24, outline=(255, 255, 255, 255), width=5)
            # Bottom label pill inside cell
            bd.rounded_rectangle([14, ch_c - 50, cw_c - 2, ch_c - 4], radius=14, fill=(255, 255, 255, 246))
            fl = get_font(FONT_BLACK, 23)
            l_s = f"{idx_c+1}. {lbl_c.replace(chr(10), ' ')}"
            while fl.size > 14 and bd.textbbox((0, 0), l_s, font=fl)[2] > cw_c - 28:
                fl = get_font(FONT_BLACK, fl.size - 1)
            bl_b = bd.textbbox((0, 0), l_s, font=fl)
            bd.text((6 + cw_c * 0.5 - (bl_b[2] - bl_b[0]) * 0.5, ch_c - 27 - (bl_b[1] + bl_b[3]) * 0.5), l_s, font=fl, fill=(*col_c, 255))
            paste_centered(stage_im, box, cx_c, cy_c, scale_x=0.88 + 0.12 * uc)


# ==============================================================================
# 6. NATIVE TVC CIRCULAR SPINNING GOLD PORTAL + 3D GOLD PLAQUE
# ==============================================================================
def draw_tvc_gold_portal(stage_im, vid_rgb, t, cx=540, cy=525, diam=420):
    vis = fit_cover(vid_rgb, diam, diam, 1.05).convert("RGBA")
    mask = Image.new("L", (diam, diam), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, diam - 1, diam - 1], fill=255)

    pad = 36
    im = Image.new("RGBA", (diam + pad * 2, diam + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad - 6, pad - 6, pad + diam + 6, pad + diam + 6], fill=(255, 210, 112, 90))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    vl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    vl.paste(vis, (pad, pad), mask=mask)
    im = Image.alpha_composite(im, vl)

    d = ImageDraw.Draw(im)
    d.ellipse([pad - 3, pad - 3, pad + diam + 3, pad + diam + 3], outline=(255, 236, 152, 255), width=7)
    d.ellipse([pad - 13, pad - 13, pad + diam + 13, pad + diam + 13], outline=(255, 212, 118, 130), width=2)
    # Orbiting gold pearls along portal ring!
    c_mid = pad + diam * 0.5
    r_orb = diam * 0.5 + 13
    for oi in range(6):
        ang = t * 1.35 + oi * (math.pi / 3.0)
        ox = c_mid + r_orb * math.cos(ang)
        oy = c_mid + r_orb * math.sin(ang)
        d.ellipse([ox - 6, oy - 6, ox + 6, oy + 6], fill=(255, 248, 200, 245))
    paste_centered(stage_im, im, cx, cy)


def make_tvc_gold_cta_plaque(w, h, badge_txt, title_txt, sub_txt):
    key = ("TVC_GOLD_PLAQUE", w, h, badge_txt, title_txt, sub_txt)
    if key in _comp_cache:
        return _comp_cache[key]

    pad = 18
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius=34, fill=(24, 8, 16, 155))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=10)))

    # Rich metallic champagne-gold gradient body
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    c1 = np.array([[[255, 246, 208]]], dtype=np.float32)
    c2 = np.array([[[232, 182, 78]]], dtype=np.float32)
    rgb = np.clip(c1 * (1.0 - yy) + c2 * yy, 0, 255).astype(np.uint8)
    body = Image.fromarray(np.repeat(rgb, w, axis=1), "RGB").convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=255)
    bl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bl.paste(body, (pad, pad), mask=m)
    im = Image.alpha_composite(im, bl)

    d = ImageDraw.Draw(im)
    x0, y0 = pad, pad
    d.rounded_rectangle([x0, y0, x0 + w - 1, y0 + h - 1], radius=34, outline=(255, 255, 240, 255), width=4)
    d.rounded_rectangle([x0 + 10, y0 + 10, x0 + w - 11, y0 + h - 11], radius=26, outline=(142, 86, 14, 155), width=2)

    cy = y0 + 20
    if badge_txt:
        fb = get_font(FONT_EBOLD, 20)
        b_up = badge_txt.upper()
        bb = d.textbbox((0, 0), b_up, font=fb)
        pw_b = (bb[2] - bb[0]) + 36
        bx0 = x0 + int((w - pw_b) * 0.5)
        d.rounded_rectangle([bx0, cy, bx0 + pw_b, cy + 36], radius=18, fill=(58, 16, 30, 245))
        d.text((bx0 + 18 - bb[0], cy + 18 - (bb[1] + bb[3]) * 0.5), b_up, font=fb, fill=(255, 238, 156, 255))
        cy += 48

    ft = get_font(FONT_BLACK, 38)
    for tl in _wrap_text(d, title_txt.upper(), ft, w - 44)[:2]:
        while ft.size > 22 and d.textbbox((0, 0), tl, font=ft)[2] > w - 40:
            ft = get_font(FONT_BLACK, ft.size - 2)
        bt = d.textbbox((0, 0), tl, font=ft)
        d.text((x0 + w * 0.5 - (bt[2] - bt[0]) * 0.5, cy), tl, font=ft, fill=(46, 12, 24, 255))
        cy += (bt[3] - bt[1]) + 10

    fs = get_font(FONT_EBOLD, 22)
    cy += 4
    for sl in _wrap_text(d, sub_txt, fs, w - 44)[:2]:
        bs = d.textbbox((0, 0), sl, font=fs)
        d.text((x0 + w * 0.5 - (bs[2] - bs[0]) * 0.5, cy), sl, font=fs, fill=(78, 36, 14, 255))
        cy += 28

    _comp_cache[key] = im
    return im


# ==============================================================================
# 7. COLLAGE POLAROID CUTOUT CARD (Style-Sampling Collage Explainer!)
# ==============================================================================
def make_collage_polaroid(vid_rgb, w, h, caption_txt, tape_rgb=(255, 218, 92)):
    pad = 22
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad + 4, pad + 10, pad + w + 4, pad + h + 10], fill=(16, 16, 18, 105))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=8)))

    d = ImageDraw.Draw(im)
    x0, y0 = pad, pad
    # Crisp white Polaroid paper frame (thick bottom margin for caption)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10, fill=(252, 250, 244, 255), outline=(218, 212, 198, 255), width=2)
    vw, vh = w - 28, h - 76
    vis = fit_cover(vid_rgb, vw, vh, 1.04).convert("RGBA")
    im.paste(vis, (x0 + 14, y0 + 14))

    # Washi masking tape across top center!
    tw = 118
    d.rounded_rectangle([x0 + w // 2 - tw // 2, y0 - 10, x0 + w // 2 + tw // 2, y0 + 20], radius=4, fill=(*tape_rgb, 222))

    fc = get_font(FONT_BLACK, 25)
    c_s = caption_txt.replace("\n", " ")
    while fc.size > 16 and d.textbbox((0, 0), c_s, font=fc)[2] > w - 30:
        fc = get_font(FONT_BLACK, fc.size - 2)
    bc = d.textbbox((0, 0), c_s, font=fc)
    d.text((x0 + w * 0.5 - (bc[2] - bc[0]) * 0.5, y0 + h - 34 - (bc[1] + bc[3]) * 0.5), c_s, font=fc, fill=(24, 24, 28, 255))
    return im
