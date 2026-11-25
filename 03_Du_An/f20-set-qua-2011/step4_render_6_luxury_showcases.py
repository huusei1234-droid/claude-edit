import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT   = r"d:\AI\full studio\output\f20-set-qua-2011"
MEDIA = os.path.join(OUT, "capcut_media")
CHECK = os.path.join(OUT, "check_showcases")
os.makedirs(MEDIA, exist_ok=True)
os.makedirs(CHECK, exist_ok=True)

W, H = 1080, 1920
FPS  = 30.0

FONTS_DIR   = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
F_XBOLD     = os.path.join(FONTS_DIR, "BeVietnamPro-ExtraBold.ttf")
F_BOLD      = os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf")
F_MED       = os.path.join(FONTS_DIR, "BeVietnamPro-Medium.ttf")
F_MONTS_BLK = os.path.join(FONTS_DIR, "Montserrat-Black.ttf")
F_FRAUNCES  = os.path.join(FONTS_DIR, "Fraunces-Black.ttf")

_fcache = {}
def get_font(p, sz):
    k = (p, max(10, int(round(sz))))
    if k not in _fcache:
        _fcache[k] = ImageFont.truetype(p, k[1])
    return _fcache[k]

def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)

def ease_out_quart(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 4.0

def quintic(u):
    u = clamp01(u)
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)

def paste_subpixel(canvas_im, sprite_im, cx, cy, scale=1.0, opacity=1.0):
    if opacity <= 0.008 or scale <= 0.02:
        return
    sw, sh = sprite_im.size
    ow = int(math.ceil(sw * scale)) + 6
    oh = int(math.ceil(sh * scale)) + 6
    x0 = int(math.floor(cx - ow * 0.5))
    y0 = int(math.floor(cy - oh * 0.5))
    inv_s = 1.0 / scale
    c_off = sw * 0.5 - (cx - x0) * inv_s
    f_off = sh * 0.5 - (cy - y0) * inv_s
    tr = sprite_im.transform((ow, oh), Image.Transform.AFFINE, (inv_s, 0.0, c_off, 0.0, inv_s, f_off), resample=Image.Resampling.BICUBIC)
    if opacity < 0.996:
        arr = np.array(tr)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * clamp01(opacity)).astype(np.uint8)
        tr = Image.fromarray(arr, "RGBA")
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(canvas_im.width, x0 + ow), min(canvas_im.height, y0 + oh)
    if dx1 > dx0 and dy1 > dy0:
        canvas_im.alpha_composite(tr.crop((dx0 - x0, dy0 - y0, dx1 - x0, dy1 - y0)), dest=(dx0, dy0))

# 5-Stop Gradient + 2-Layer Outline (.grad-back + .grad-front) Text Sprite!
GRAD_STOPS_GOLD = [
    (0.00, (255, 253, 242)),
    (0.25, (252, 225, 129)),
    (0.52, (214, 146,  40)),
    (0.76, (255, 235, 168)),
    (1.00, (154,  94,  12)),
]
GRAD_STOPS_RUBY = [
    (0.00, (255, 238, 244)),
    (0.26, (248,  98, 128)),
    (0.54, (192,  18,  52)),
    (0.78, (255, 160, 182)),
    (1.00, (118,   8,  32)),
]

_tcache = {}
def render_5stop_grad_text(text, font_p, sz, stops, stroke_col=(38, 14, 18), stroke_w=7, extrude_col=(28, 8, 12), sheen_pos=None):
    k = (text, font_p, int(round(sz)), tuple(stops), stroke_col, stroke_w, extrude_col)
    if k not in _tcache:
        fnt = get_font(font_p, sz)
        bb = ImageDraw.Draw(Image.new("RGBA", (8, 8))).textbbox((0, 0), text, font=fnt, stroke_width=stroke_w)
        tw, th = max(4, bb[2] - bb[0]), max(4, bb[3] - bb[1])
        pad = stroke_w + 18
        cw, ch = tw + pad * 2, th + pad * 2
        ox, oy = pad - bb[0], pad - bb[1]

        base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        # Soft drop shadow
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 2, oy + 5), text, font=fnt, fill=255, stroke_width=stroke_w, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=6.0)), dtype=np.float32) * 0.55
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 3] = np.clip(sb, 0, 255).astype(np.uint8)
        base = Image.alpha_composite(base, Image.fromarray(sa, "RGBA"))

        # Layer 1 (.grad-back): Outer stroke + 3D extrude so stroke NEVER eats into gradient!
        if extrude_col:
            ex = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            ImageDraw.Draw(ex).text((ox + 2, oy + 3), text, font=fnt, fill=(*extrude_col, 245), stroke_width=stroke_w, stroke_fill=(*extrude_col, 245))
            base = Image.alpha_composite(base, ex)
        if stroke_w > 0:
            st = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            ImageDraw.Draw(st).text((ox, oy), text, font=fnt, fill=(*stroke_col, 255), stroke_width=stroke_w, stroke_fill=(*stroke_col, 255))
            base = Image.alpha_composite(base, st)

        # Layer 2 (.grad-front): 5-stop vertical gradient fill
        fm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(fm).text((ox, oy), text, font=fnt, fill=255)
        am = np.array(fm, dtype=np.float32) / 255.0
        yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)
        grad_line = np.zeros((ch, 3), dtype=np.float32)
        xs = [s[0] for s in stops]
        for c in range(3):
            ys = [s[1][c] for s in stops]
            grad_line[:, c] = np.interp(yy, xs, ys)
        grad_rgb = np.broadcast_to(grad_line[:, None, :], (ch, cw, 3)).copy()
        _tcache[k] = (base, grad_rgb, am)

    base, grad_rgb, am = _tcache[k]
    ch, cw = am.shape
    rgb = grad_rgb.copy()
    if sheen_pos is not None:
        xx = np.arange(cw, dtype=np.float32)[None, :] / max(1.0, float(cw))
        yy = np.arange(ch, dtype=np.float32)[:, None] / max(1.0, float(ch))
        diag = xx * 0.82 + yy * 0.35
        sh = np.exp(-((diag - sheen_pos) ** 2) / 0.009) * 95.0
        rgb = np.clip(rgb + sh[:, :, None], 0, 255)
    front = Image.fromarray(np.dstack([rgb.astype(np.uint8), (am * 255.0).astype(np.uint8)]), "RGBA")
    return Image.alpha_composite(base, front)

def make_pill_badge(text, bg_rgba=(138, 16, 36, 232), border_rgb=(252, 218, 128), text_rgb=(255, 248, 235), fsz=30):
    fnt = get_font(F_XBOLD, fsz)
    bb = ImageDraw.Draw(Image.new("RGBA", (8, 8))).textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pw, ph = tw + 58, max(62, th + 30)
    cw, ch = pw + 24, ph + 24
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([12, 16, 12 + pw, 16 + ph], radius=ph // 2, fill=(18, 8, 12, 110))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(radius=7)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([12, 10, 12 + pw, 10 + ph], radius=ph // 2, fill=bg_rgba, outline=(*border_rgb, 245), width=3)
    d.text((12 + (pw - tw) * 0.5 - bb[0], 10 + (ph - th) * 0.5 - bb[1]), text, font=fnt, fill=(*text_rgb, 255))
    return im

def load_frames_segment(path, ss, dur, vw=1080, vh=1920):
    n_frames = int(round(dur * FPS))
    p = subprocess.Popen([
        "ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", path,
        "-frames:v", str(n_frames), "-vf", f"scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh},fps=30",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ], stdout=subprocess.PIPE)
    frames = []
    nb = vw * vh * 3
    while True:
        b = p.stdout.read(nb)
        if len(b) < nb:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)))
    p.stdout.close(); p.wait()
    while len(frames) < n_frames and frames:
        frames.append(frames[-1])
    return frames

def extract_studio_pack_rgba(v4_path, ts, y_top=360, y_bot=1445, x_left=110, x_right=970):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{ts:.2f}", "-i", v4_path,
        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ])
    rgb = np.frombuffer(raw, dtype=np.uint8).reshape((H, W, 3))[y_top:y_bot, x_left:x_right].copy()
    # Clean studio white background removal with soft anti-aliased edge + preserve bright highlights inside package!
    # Notice studio backdrop around edges is near pure white (R>232, G>234, B>236, low saturation).
    # Flood-fill / distance from border white so white labels INSIDE the pouch stay 100% opaque!
    from collections import deque
    rh, rw = rgb.shape[:2]
    f = rgb.astype(np.float32)
    lum = 0.299 * f[:,:,0] + 0.587 * f[:,:,1] + 0.114 * f[:,:,2]
    sat = np.max(f, axis=2) - np.min(f, axis=2)
    bg_cand = (lum > 224.0) & (sat < 22.0)

    visited = np.zeros((rh, rw), dtype=bool)
    q = deque()
    for x in range(rw):
        if bg_cand[0, x]: visited[0, x] = True; q.append((0, x))
        if bg_cand[rh-1, x]: visited[rh-1, x] = True; q.append((rh-1, x))
    for y in range(rh):
        if bg_cand[y, 0]: visited[y, 0] = True; q.append((y, 0))
        if bg_cand[y, rw-1]: visited[y, rw-1] = True; q.append((y, rw-1))

    while q:
        cy, cx = q.popleft()
        for ny, nx in ((cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)):
            if 0 <= ny < rh and 0 <= nx < rw and not visited[ny, nx] and bg_cand[ny, nx]:
                visited[ny, nx] = True
                q.append((ny, nx))

    alpha = (~visited).astype(np.float32) * 255.0
    alpha_im = Image.fromarray(alpha.astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius=1.6))
    # Crop tight bounding box
    bb = alpha_im.getbbox()
    if bb:
        rgb = rgb[bb[1]:bb[3], bb[0]:bb[2]]
        alpha_im = alpha_im.crop(bb)
    return Image.fromarray(np.dstack([rgb, np.array(alpha_im)]), "RGBA")

def make_gold_framed_card(rgb_crop, cw, ch, radius=44, sheen_pos=None):
    im = Image.fromarray(rgb_crop, "RGB").resize((cw, ch), Image.Resampling.BICUBIC)
    arr = np.array(im, dtype=np.float32)
    if sheen_pos is not None:
        yy, xx = np.ogrid[0:ch, 0:cw]
        diag = (xx.astype(np.float32) * 0.8 + yy.astype(np.float32) * 0.45) / (cw * 0.8 + ch * 0.45)
        sh = np.exp(-((diag - sheen_pos) ** 2) / 0.009) * 34.0
        arr[:, :, 0] = np.clip(arr[:, :, 0] + sh * 1.1, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + sh * 0.96, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + sh * 0.82, 0, 255)
    pad = 24
    out = Image.new("RGBA", (cw + pad * 2, ch + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (cw + pad * 2, ch + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([pad, pad + 8, pad + cw, pad + 8 + ch], radius=radius, fill=(20, 8, 12, 130))
    out = Image.alpha_composite(out, shadow.filter(ImageFilter.GaussianBlur(radius=14)))

    rm = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=radius, fill=255)
    layer = Image.new("RGBA", (cw + pad * 2, ch + pad * 2), (0, 0, 0, 0))
    layer.paste(Image.fromarray(arr.astype(np.uint8), "RGB"), (pad, pad), mask=rm)
    out = Image.alpha_composite(out, layer)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([pad, pad, pad + cw - 1, pad + ch - 1], radius=radius, outline=(252, 222, 132, 245), width=4)
    d.rounded_rectangle([pad + 7, pad + 7, pad + cw - 8, pad + ch - 8], radius=max(12, radius - 6), outline=(255, 248, 225, 130), width=2)
    return out

def make_warm_bokeh_bg(frame_rgb, dim=0.58):
    bg = Image.fromarray(frame_rgb, "RGB").filter(ImageFilter.GaussianBlur(radius=26))
    arr = np.array(bg, dtype=np.float32) * dim
    # Warm festive burgundy-gold vignette
    yy, xx = np.ogrid[0:H, 0:W]
    r2 = ((xx - 540.0) / 620.0) ** 2 + ((yy - 880.0) / 1050.0) ** 2
    vig = np.clip(1.08 - 0.34 * r2, 0.52, 1.05)[:, :, None]
    arr = np.clip(arr * vig + np.array([18.0, 6.0, 4.0])[None, None, :], 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")

def write_clip(out_name, n_frames, render_fn, test_mode=False, test_f=45):
    if test_mode:
        im = render_fn(min(n_frames - 1, test_f))
        p = os.path.join(CHECK, out_name.replace(".mp4", ".jpg"))
        im.convert("RGB").save(p, quality=92)
        return p
    dst = os.path.join(MEDIA, out_name)
    proc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p", dst
    ], stdin=subprocess.PIPE)
    for fi in range(n_frames):
        im = render_fn(fi)
        proc.stdin.write(np.array(im.convert("RGB"), dtype=np.uint8).tobytes())
    proc.stdin.close(); proc.wait()
    print("Rendered showcase:", out_name, f"({n_frames}f)")
    return dst

def main():
    test_mode = "--test" in sys.argv
    v4_p = os.path.join(OUT, "source_v4.mp4")

    # Extract 3 crisp alpha-cutout F20 product packs!
    pack_seaweed_jar = extract_studio_pack_rgba(v4_p, 32.10, y_top=380, y_bot=1425, x_left=160, x_right=930)
    pack_boat_mix    = extract_studio_pack_rgba(v4_p, 37.20, y_top=430, y_bot=1435, x_left=120, x_right=960)
    pack_seaweed_bar = extract_studio_pack_rgba(v4_p, 43.50, y_top=430, y_bot=1435, x_left=140, x_right=940)

    bg_dolly  = load_frames_segment(os.path.join(MEDIA, "broll_01_dolly_sets.mp4"), 0.0, 9.5)
    bg_mica   = load_frames_segment(os.path.join(MEDIA, "broll_04_mica_sunlit.mp4"), 0.0, 6.5)
    bg_tower  = load_frames_segment(os.path.join(MEDIA, "broll_02_rotating_tower.mp4"), 0.0, 7.0)
    bag_macro = load_frames_segment(os.path.join(MEDIA, "broll_07_inside_bag_pip.mp4"), 0.0, 5.5)

    # Clean upper crops (y=240..1440 -> ZERO old text!) from v4's bird's nest close-ups
    yen_close1 = load_frames_segment(v4_p, 16.80, 3.95)
    yen_close2 = load_frames_segment(v4_p, 20.80, 3.65)
    yen_cgi    = load_frames_segment(v4_p, 72.02, 4.95)

    saved_tests = []

    # ------------------------------------------------------------------
    # SHOWCASE 1: Yến Sào SKA NEST + 4 Nguyên Liệu Chưng (9.40s = 282f)
    # Timeline: 15.95s -> 25.35s
    # ------------------------------------------------------------------
    pills_s1 = [
        (5.52, "TÁO ĐỎ",               (168, 22, 42, 240), (255, 222, 138), 295.0, 1175.0),
        (6.42, "ĐÔNG TRÙNG HẠ THẢO",   (142, 78, 12, 240), (255, 232, 150), 755.0, 1175.0),
        (7.72, "KỶ TỬ",                (176, 38, 24, 240), (255, 222, 138), 295.0, 1272.0),
        (8.48, "1 HỘP ĐƯỜNG PHÈN",     ( 28, 72, 64, 240), (185, 248, 225), 755.0, 1272.0),
    ]
    pill_sprites_s1 = [(t_in, make_pill_badge(lbl, bgc, bdc, fsz=25), px, py) for t_in, lbl, bgc, bdc, px, py in pills_s1]

    def ren_s1(fi):
        t = fi / FPS
        bg = make_warm_bokeh_bg(bg_dolly[fi % len(bg_dolly)], dim=0.55)
        if t < 4.40:
            src_f = yen_close1[min(len(yen_close1)-1, fi)][340:1430, 60:1020]
        elif t > 5.00:
            idx2 = min(len(yen_close2)-1, max(0, int((t - 4.60) * FPS)))
            src_f = yen_close2[idx2][250:1420, 40:1040]
        else:
            u = quintic((t - 4.40) / 0.60)
            a = yen_close1[min(len(yen_close1)-1, fi)][340:1430, 60:1020]
            b_im = Image.fromarray(yen_close2[0][250:1420, 40:1040]).resize((a.shape[1], a.shape[0]))
            src_f = np.clip(a.astype(np.float32)*(1-u) + np.array(b_im, dtype=np.float32)*u, 0, 255).astype(np.uint8)

        sheen = -0.25 + 1.5 * ((t % 3.2) / 3.2)
        card = make_gold_framed_card(src_f, 920, 760, radius=46, sheen_pos=sheen)
        sc_in = 0.94 + 0.06 * ease_out_quart(t / 0.45)
        paste_subpixel(bg, card, 540.0, 745.0, scale=sc_in, opacity=1.0)

        for t_in, sp, px, py in pill_sprites_s1:
            if t >= t_in:
                u = ease_out_quart((t - t_in) / 0.36)
                paste_subpixel(bg, sp, px, py + (1.0 - u) * 24.0, scale=0.86 + 0.14 * u, opacity=u)
        return bg

    saved_tests.append(write_clip("showcase_01_yensao_ingredients.mp4", 282, ren_s1, test_mode, test_f=265))

    # ------------------------------------------------------------------
    # SHOWCASE 2: Bộ Đôi 2 Hộp Rong Biển Sấy Giòn (5.10s = 153f)
    # Timeline: 28.55s -> 33.65s
    # ------------------------------------------------------------------
    p_spicy = make_pill_badge("01 HỘP SẤY GIÒN CAY NHẸ",  (168, 26, 22, 240), (255, 222, 132), fsz=28)
    p_sesam = make_pill_badge("01 HỘP SẤY MÈ KHÔNG CAY",  ( 22, 98, 54, 240), (195, 252, 212), fsz=28)

    def ren_s2(fi):
        t = fi / FPS
        bg = make_warm_bokeh_bg(bg_dolly[fi % len(bg_dolly)], dim=0.52)
        # Left card: real sunlit gift bag macro showing both jars stacked inside
        crop_l = bag_macro[fi % len(bag_macro)][380:1380, 120:960]
        card_l = make_gold_framed_card(crop_l, 500, 620, radius=38, sheen_pos=-0.2 + 1.4 * (t / 3.5))
        u1 = ease_out_quart(t / 0.45)
        paste_subpixel(bg, card_l, 315.0 - (1 - u1) * 40.0, 760.0, scale=0.94 + 0.06 * u1, opacity=u1)

        # Right card: rounded cream-gold pedestal card framing the F20 Rong Biển jar cleanly!
        u2 = ease_out_quart(max(0.0, t - 0.18) / 0.48)
        if u2 > 0.01:
            ped_r = Image.new("RGBA", (470, 650), (0, 0, 0, 0))
            ImageDraw.Draw(ped_r).rounded_rectangle([14, 14, 456, 636], radius=38, fill=(252, 248, 240, 236), outline=(245, 205, 112, 250), width=4)
            sc_jar = min(380.0 / max(1, pack_seaweed_jar.width), 550.0 / max(1, pack_seaweed_jar.height))
            paste_subpixel(ped_r, pack_seaweed_jar, 235.0, 325.0, scale=sc_jar, opacity=1.0)
            paste_subpixel(bg, ped_r, 775.0 + (1 - u2) * 38.0, 760.0, scale=0.94 + 0.06 * u2, opacity=u2)

        if t >= 0.25:
            up1 = ease_out_quart((t - 0.25) / 0.38)
            paste_subpixel(bg, p_spicy, 540.0, 1165.0 + (1 - up1) * 20.0, scale=0.9 + 0.1 * up1, opacity=up1)
        if t >= 2.75:
            up2 = ease_out_quart((t - 2.75) / 0.38)
            paste_subpixel(bg, p_sesam, 540.0, 1262.0 + (1 - up2) * 20.0, scale=0.9 + 0.1 * up2, opacity=up2)
        return bg

    saved_tests.append(write_clip("showcase_02_rongbien_doi.mp4", 153, ren_s2, test_mode, test_f=110))

    # ------------------------------------------------------------------
    # SHOWCASE 3: Bánh Thuyền Mix Hạt Dinh Dưỡng 250g (3.90s = 117f)
    # Timeline: 35.80s -> 39.70s
    # ------------------------------------------------------------------
    p_boat = make_pill_badge("GÓI 250G • BÁNH THUYỀN MIX HẠT DINH DƯỠNG", (138, 62, 14, 242), (255, 226, 138), fsz=26)

    def ren_s3(fi):
        t = fi / FPS
        bg = make_warm_bokeh_bg(bg_mica[fi % len(bg_mica)], dim=0.52)
        # Cream-gold luxury pedestal card behind crisp product pack
        ped = Image.new("RGBA", (860, 820), (0, 0, 0, 0))
        ImageDraw.Draw(ped).rounded_rectangle([20, 20, 840, 800], radius=52, fill=(252, 246, 236, 228), outline=(245, 205, 112, 250), width=5)
        u = ease_out_quart(t / 0.45)
        paste_subpixel(bg, ped, 540.0, 755.0, scale=0.94 + 0.06 * u, opacity=u)
        sc_p = (660.0 / max(1, pack_boat_mix.height)) * (0.95 + 0.05 * u + 0.025 * (t / 3.9))
        paste_subpixel(bg, pack_boat_mix, 540.0, 748.0 + math.sin(t * 2.4) * 5.0, scale=sc_p, opacity=u)
        if t >= 0.30:
            ub = ease_out_quart((t - 0.30) / 0.38)
            paste_subpixel(bg, p_boat, 540.0, 1235.0 + (1 - ub) * 22.0, scale=0.9 + 0.1 * ub, opacity=ub)
        return bg

    saved_tests.append(write_clip("showcase_03_banhthuyen_250g.mp4", 117, ren_s3, test_mode, test_f=60))

    # ------------------------------------------------------------------
    # SHOWCASE 4: Rong Biển Kẹp Hạt 500g - 22-24 Thanh (4.40s = 132f)
    # Timeline: 42.20s -> 46.60s
    # ------------------------------------------------------------------
    p_bar1 = make_pill_badge("TÚI LỚN 500G • RONG BIỂN KẸP HẠT TUỆ TÂM", (20, 92, 52, 242), (195, 252, 212), fsz=26)
    p_bar2 = make_pill_badge("GỒM 22 – 24 THANH BÁNH HẠT GIÒN BÙI",       (156, 24, 38, 242), (255, 226, 138), fsz=27)

    def ren_s4(fi):
        t = fi / FPS
        bg = make_warm_bokeh_bg(bg_dolly[fi % len(bg_dolly)], dim=0.52)
        ped = Image.new("RGBA", (860, 790), (0, 0, 0, 0))
        ImageDraw.Draw(ped).rounded_rectangle([20, 20, 840, 770], radius=52, fill=(246, 252, 248, 228), outline=(245, 205, 112, 250), width=5)
        u = ease_out_quart(t / 0.45)
        paste_subpixel(bg, ped, 540.0, 735.0, scale=0.94 + 0.06 * u, opacity=u)
        sc_p = (640.0 / max(1, pack_seaweed_bar.height)) * (0.95 + 0.05 * u + 0.025 * (t / 4.4))
        paste_subpixel(bg, pack_seaweed_bar, 540.0, 730.0 + math.sin(t * 2.4) * 5.0, scale=sc_p, opacity=u)
        if t >= 0.25:
            ub1 = ease_out_quart((t - 0.25) / 0.36)
            paste_subpixel(bg, p_bar1, 540.0, 1185.0 + (1 - ub1) * 20.0, scale=0.9 + 0.1 * ub1, opacity=ub1)
        if t >= 2.35:
            ub2 = ease_out_quart((t - 2.35) / 0.36)
            paste_subpixel(bg, p_bar2, 540.0, 1278.0 + (1 - ub2) * 20.0, scale=0.9 + 0.1 * ub2, opacity=ub2)
        return bg

    saved_tests.append(write_clip("showcase_04_rongbien_kephat_500g.mp4", 132, ren_s4, test_mode, test_f=95))

    # ------------------------------------------------------------------
    # SHOWCASE 5: Tổ Yến Tinh Chế Cao Cấp SKA NEST (4.95s = 149f)
    # Timeline: 71.75s -> 76.70s
    # ------------------------------------------------------------------
    p_ska = make_pill_badge("TỔ YẾN TINH CHẾ SỢI DÀI • YẾN SÀO SKA NEST", (132, 16, 32, 242), (255, 225, 132), fsz=26)

    def ren_s5(fi):
        t = fi / FPS
        f_cgi = yen_cgi[min(len(yen_cgi) - 1, fi)]
        bg = make_warm_bokeh_bg(f_cgi, dim=0.65)
        # Clean upper region y=180..1440 (100% above v4's old text!)
        crop = f_cgi[220:1440, 40:1040]
        sheen = -0.25 + 1.55 * (t / 4.95)
        card = make_gold_framed_card(crop, 930, 830, radius=48, sheen_pos=sheen)
        u = ease_out_quart(t / 0.48)
        paste_subpixel(bg, card, 540.0, 770.0, scale=0.95 + 0.05 * u, opacity=u)
        if t >= 0.35:
            ub = ease_out_quart((t - 0.35) / 0.40)
            paste_subpixel(bg, p_ska, 540.0, 1255.0 + (1 - ub) * 20.0, scale=0.9 + 0.1 * ub, opacity=ub)
        return bg

    saved_tests.append(write_clip("showcase_05_to_yen_cao_cap.mp4", 149, ren_s5, test_mode, test_f=80))

    # ------------------------------------------------------------------
    # SHOWCASE 6: Luxury Brand End-Card Đặt Quà 20/11 (6.58s = 197f)
    # Timeline: 105.85s -> 112.433s (100% solid Contact Info, ZERO glitch!)
    # ------------------------------------------------------------------
    def build_endcard_panel(sheen_pos):
        pw, ph = 940, 780
        pad = 24
        card = Image.new("RGBA", (pw + pad*2, ph + pad*2), (0, 0, 0, 0))
        sh = Image.new("RGBA", (pw + pad*2, ph + pad*2), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad+10, pad+pw, pad+10+ph], radius=48, fill=(14, 4, 8, 165))
        card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(radius=16)))

        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad, pad+pw, pad+ph], radius=48, fill=(52, 10, 20, 232), outline=(252, 222, 132, 250), width=4)
        d.rounded_rectangle([pad+10, pad+10, pad+pw-10, pad+ph-10], radius=40, outline=(255, 245, 210, 115), width=2)

        # Header 5-stop Champagne Gold 3D Text
        sp_h1 = render_5stop_grad_text("SET QUÀ TRI ÂN 20/11", F_XBOLD, 56, GRAD_STOPS_GOLD, stroke_col=(32, 8, 14), stroke_w=7, sheen_pos=sheen_pos)
        paste_subpixel(card, sp_h1, pad + pw*0.5, pad + 108, scale=1.0)

        # Sub-ribbon
        rib = make_pill_badge("THỰC PHẨM F20  •  YẾN SÀO SKA NEST", (156, 22, 42, 250), (252, 220, 130), fsz=26)
        paste_subpixel(card, rib, pad + pw*0.5, pad + 208, scale=1.0)

        # Hotline Box (Razor-sharp contrast!)
        d.rounded_rectangle([pad+46, pad+276, pad+pw-46, pad+492], radius=32, fill=(255, 251, 244, 250), outline=(235, 185, 88, 255), width=4)
        f_lbl = get_font(F_BOLD, 27)
        t_lbl = "HOTLINE / ZALO ĐẶT SỈ & LẺ"
        bbl = d.textbbox((0,0), t_lbl, font=f_lbl)
        d.text((pad + (pw - (bbl[2]-bbl[0]))*0.5, pad + 306), t_lbl, font=f_lbl, fill=(138, 16, 36, 255))

        f_ph = get_font(F_MONTS_BLK, 44)
        t_ph = "0706.001.626 - 0979.512.289"
        bbp = d.textbbox((0,0), t_ph, font=f_ph)
        d.text((pad + (pw - (bbp[2]-bbp[0]))*0.5 + 2, pad + 382 + 2), t_ph, font=f_ph, fill=(235, 195, 145, 255))
        d.text((pad + (pw - (bbp[2]-bbp[0]))*0.5, pad + 382), t_ph, font=f_ph, fill=(168, 12, 34, 255))

        # 2 Store Addresses in Nha Trang
        f_addr_b = get_font(F_XBOLD, 28)
        f_addr_m = get_font(F_MED, 27)
        a1 = "CS1: 149 Trần Nhật Duật, TP. Nha Trang"
        a2 = "CS2: 17/3 Điện Biên Phủ, Vĩnh Hòa, Nha Trang"
        a3 = "Nhận đóng set quà theo yêu cầu • Giao tận nơi"
        for yy_a, txt_a, f_a, col_a in [
            (pad + 545, a1, f_addr_b, (255, 246, 222, 255)),
            (pad + 605, a2, f_addr_b, (255, 246, 222, 255)),
            (pad + 682, a3, f_addr_m, (252, 218, 130, 255)),
        ]:
            bb_a = d.textbbox((0,0), txt_a, font=f_a)
            d.text((pad + (pw - (bb_a[2]-bb_a[0]))*0.5, yy_a), txt_a, font=f_a, fill=col_a)
        return card

    def ren_s6(fi):
        t = fi / FPS
        bg = make_warm_bokeh_bg(bg_tower[fi % len(bg_tower)], dim=0.56)
        sheen = -0.3 + 1.6 * ((t % 2.8) / 2.8)
        panel = build_endcard_panel(sheen)
        u = ease_out_quart(t / 0.50)
        paste_subpixel(bg, panel, 540.0, 825.0 + (1 - u) * 28.0, scale=0.94 + 0.06 * u, opacity=u)
        return bg

    saved_tests.append(write_clip("showcase_06_outro_endcard.mp4", 197, ren_s6, test_mode, test_f=80))

    if test_mode:
        imgs = [Image.open(p).resize((360, 640), Image.Resampling.LANCZOS) for p in saved_tests]
        grid = Image.new("RGB", (360 * 3, 640 * 2))
        for i, im in enumerate(imgs):
            grid.paste(im, ((i % 3) * 360, (i // 3) * 640))
        gp = os.path.join(CHECK, "showcases_test_grid.jpg")
        grid.save(gp, quality=92)
        print("Saved showcases_test_grid.jpg:", gp)

if __name__ == "__main__":
    main()
