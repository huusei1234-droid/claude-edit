import os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from concurrent.futures import ThreadPoolExecutor

OUT_DIR   = r'd:\AI\full studio\output\feelchicken-food-cinematic'
TITLE_DIR = os.path.join(OUT_DIR, 'titles_alpha')
CHECK_DIR = os.path.join(OUT_DIR, 'check')
FONTS_DIR = r'd:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi'
LOGO_PATH = r'd:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\03_FeelChicken\logos_png\logo.png'

os.makedirs(TITLE_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30

# 5-Stop Metallic Gradient Palettes (from gradient-text-presets.css)
GOLD_STOPS = [
    (0.00, (255, 253, 242)),  # #FFFDF2
    (0.25, (252, 225, 129)),  # #FCE181
    (0.52, (214, 146,  40)),  # #D69228
    (0.76, (255, 235, 168)),  # #FFEBA8
    (1.00, (154,  94,  12)),  # #9A5E0C
]

CORAL_GOLD_STOPS = [
    (0.00, (255, 247, 234)),
    (0.25, (255, 185,  98)),
    (0.52, (230,  68,  34)),
    (0.76, (255, 214, 158)),
    (1.00, (148,  32,  10)),
]

def build_vertical_gradient(w, h, stops):
    arr = np.zeros((h, w, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, max(2, h))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i+1]
        mask = (ys >= p0) & (ys <= p1)
        if np.any(mask):
            t = (ys[mask] - p0) / max(1e-6, (p1 - p0))
            for ch in range(3):
                arr[mask, :, ch] = (c0[ch] * (1.0 - t) + c1[ch] * t)[:, None]
    return arr

def ease_out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_in_out(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def render_gradient_text_block(lines, font_path, font_size, stops, sheen_prog, stroke_px=6, line_gap=14):
    """
    Renders multi-line 5-stop metallic gradient text with:
    - Layer 1 (.grad-back): Separated outer dark espresso bevel + soft cinema drop shadow (ZERO stroke eating into gradient!)
    - Layer 2 (.grad-front): Crisp 5-stop vertical gradient + diagonal 115-deg Specular Sheen Sweep!
    Returns RGBA PIL.Image cropped tightly with padding.
    """
    font = ImageFont.truetype(font_path, font_size)
    dummy = Image.new('L', (10, 10), 0)
    dd = ImageDraw.Draw(dummy)
    bboxes = [dd.textbbox((0, 0), ln, font=font) for ln in lines]
    widths = [b[2] - b[0] for b in bboxes]
    heights = [b[3] - b[1] for b in bboxes]
    pad = 44
    bw = max(widths) + pad * 2
    bh = sum(heights) + line_gap * (len(lines) - 1) + pad * 2

    # 1. Interior fill alpha mask (pure glyph interior, zero stroke)
    fill_mask = Image.new('L', (bw, bh), 0)
    fd = ImageDraw.Draw(fill_mask)
    # 2. Outer stroke mask (drawn with stroke_width, placed strictly UNDER fill_mask!)
    back_layer = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(back_layer)
    shadow_mask = Image.new('L', (bw, bh), 0)
    sd = ImageDraw.Draw(shadow_mask)

    cur_y = pad
    line_y_ranges = []
    for idx, ln in enumerate(lines):
        b = bboxes[idx]
        lw = b[2] - b[0]
        lh = b[3] - b[1]
        lx = (bw - lw) // 2 - b[0]
        ly = cur_y - b[1]
        # Deep shadow mask
        sd.text((lx, ly + 8), ln, font=font, fill=235, stroke_width=stroke_px + 4, stroke_fill=235)
        # Crisp dark espresso-bronze outer stroke (.grad-back)
        bd.text((lx, ly + 3), ln, font=font, fill=(28, 12, 6, 255), stroke_width=stroke_px + 1, stroke_fill=(24, 10, 4, 255))
        bd.text((lx, ly), ln, font=font, fill=(42, 20, 8, 255), stroke_width=stroke_px, stroke_fill=(38, 18, 6, 255))
        # Pure glyph interior (.grad-front)
        fd.text((lx, ly), ln, font=font, fill=255)
        line_y_ranges.append((cur_y, cur_y + lh))
        cur_y += lh + line_gap

    # Blur shadow
    shadow_blur = shadow_mask.filter(ImageFilter.GaussianBlur(radius=14))
    shadow_rgba = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    sh_np = np.zeros((bh, bw, 4), dtype=np.uint8)
    sh_np[:, :, 3] = (np.array(shadow_blur, dtype=np.float32) * 0.72).clip(0, 255).astype(np.uint8)
    shadow_rgba = Image.fromarray(sh_np, 'RGBA')

    # Build per-line 5-stop gradient + diagonal sheen sweep (-0.4 to +1.4)
    grad_rgb = np.zeros((bh, bw, 3), dtype=np.float32)
    for y0, y1 in line_y_ranges:
        gh = max(2, y1 - y0 + 6)
        vy0 = max(0, y0 - 3)
        vy1 = min(bh, vy0 + gh)
        grad_rgb[vy0:vy1, :, :] = build_vertical_gradient(bw, vy1 - vy0, stops)

    # Diagonal 115-degree Specular Sheen Sweep
    if sheen_prog is not None:
        xs = np.linspace(0.0, 1.0, bw)[None, :]
        ys = np.linspace(0.0, 1.0, bh)[:, None]
        diag = xs * 0.85 + ys * 0.28
        center = -0.25 + sheen_prog * 1.65
        band = np.exp(-((diag - center) ** 2) / (2.0 * (0.075 ** 2)))
        grad_rgb = grad_rgb + band[:, :, None] * 145.0

    grad_u8 = np.clip(grad_rgb, 0, 255).astype(np.uint8)
    front_np = np.zeros((bh, bw, 4), dtype=np.uint8)
    front_np[:, :, :3] = grad_u8
    front_np[:, :, 3] = np.array(fill_mask, dtype=np.uint8)
    front_rgba = Image.fromarray(front_np, 'RGBA')

    out = Image.alpha_composite(shadow_rgba, back_layer)
    out = Image.alpha_composite(out, front_rgba)
    return out

def render_eyebrow_pill(text, font_path, font_size=25):
    font = ImageFont.truetype(font_path, font_size)
    # Tracked uppercase string
    tracked = " ".join(list(text)) if len(text) <= 18 else text
    dummy = ImageDraw.Draw(Image.new('L', (10, 10)))
    b = dummy.textbbox((0, 0), tracked, font=font)
    tw, th = b[2] - b[0], b[3] - b[1]
    line_w = 56
    gap = 18
    bw = tw + (line_w + gap) * 2 + 40
    bh = th + 32
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cy = bh // 2
    # Shadow + text
    tx = (bw - tw) // 2 - b[0]
    ty = (bh - th) // 2 - b[1]
    d.text((tx, ty + 2), tracked, font=font, fill=(0, 0, 0, 210), stroke_width=3, stroke_fill=(0, 0, 0, 190))
    d.text((tx, ty), tracked, font=font, fill=(255, 224, 130, 255))
    # Gold hairline rules left & right with diamond accents
    lx0 = 20
    lx1 = lx0 + line_w
    rx0 = bw - 20 - line_w
    rx1 = bw - 20
    d.line([(lx0, cy), (lx1, cy)], fill=(255, 212, 96, 220), width=2)
    d.line([(rx0, cy), (rx1, cy)], fill=(255, 212, 96, 220), width=2)
    return im

def render_subhead(text, font_path, font_size=34):
    font = ImageFont.truetype(font_path, font_size)
    dummy = ImageDraw.Draw(Image.new('L', (10, 10)))
    b = dummy.textbbox((0, 0), text, font=font)
    tw, th = b[2] - b[0], b[3] - b[1]
    bw, bh = tw + 60, th + 40
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tx, ty = 30 - b[0], 20 - b[1]
    # Soft dark halo + crisp pure white text
    sh = Image.new('L', (bw, bh), 0)
    ImageDraw.Draw(sh).text((tx, ty + 4), text, font=font, fill=230, stroke_width=6, stroke_fill=230)
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh_np = np.zeros((bh, bw, 4), dtype=np.uint8)
    sh_np[:, :, 3] = (np.array(sh, dtype=np.float32) * 0.78).clip(0, 255).astype(np.uint8)
    im = Image.alpha_composite(im, Image.fromarray(sh_np, 'RGBA'))
    d = ImageDraw.Draw(im)
    d.text((tx, ty), text, font=font, fill=(255, 252, 245, 255), stroke_width=3, stroke_fill=(20, 10, 5, 235))
    return im

def make_bottom_scrim():
    scrim = np.zeros((H, W, 4), dtype=np.uint8)
    y0 = 1220
    ys = np.linspace(0.0, 1.0, H - y0)
    alpha = (ys ** 1.55) * 168.0
    scrim[y0:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)[:, None]
    return Image.fromarray(scrim, 'RGBA')

BOTTOM_SCRIM = make_bottom_scrim()

# 9 Luxury Cinema Title Cards synced to the 5-Act Musical Storyboard!
# Placement: Lower-Third Cinema Safe Zone (y ~ 1380..1740) so center food (y=360..1360) is 100% clear!
TITLE_CARDS = [
    {
        'id': 'T01_hook',
        'start': 0.15, 'end': 3.85,
        'eyebrow': 'FEEL CHICKEN  •  CINEMA',
        'lines': ['ĐÁNH THỨC', 'MỌI GIÁC QUAN'],
        'sub': 'Nghệ thuật gà rán Hàn Quốc nóng hổi vừa ra lò',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 78, 'palette': 'gold', 'y_center': 1525,
    },
    {
        'id': 'T02_craft',
        'start': 4.25, 'end': 8.75,
        'eyebrow': 'CHẾ BIẾN THỦ CÔNG',
        'lines': ['TƯƠI NGON TỪNG MẺ'],
        'sub': 'Tẩm bột chuẩn công thức  •  Giữ trọn độ mọng ngọt',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 72, 'palette': 'gold', 'y_center': 1605,
    },
    {
        'id': 'T03_crispy',
        'start': 8.98, 'end': 14.95,
        'eyebrow': 'CHUẨN NHIỆT VÀNG ÓNG',
        'lines': ['LỚP VỎ GIÒN RỤM'],
        'sub': 'Chiên ngập dầu vàng ruộm  •  Khoai tây nóng giòn',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 78, 'palette': 'coral', 'y_center': 1545,
    },
    {
        'id': 'T04_cheese',
        'start': 15.30, 'end': 18.60,
        'eyebrow': 'BÉO THƠM NGẬY QUYỆN',
        'lines': ['TAN CHẢY PHÔ MAI'],
        'sub': 'Sốt phô mai hoàng kim phủ đẫm từng miếng gà',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 76, 'palette': 'gold', 'y_center': 1545,
    },
    {
        'id': 'T05_sauces',
        'start': 18.85, 'end': 23.40,
        'eyebrow': '5 TẦNG HƯƠNG VỊ',
        'lines': ['ĐẪM SỐT CHUẨN HÀN'],
        'sub': 'Cay nồng Yangnyeom  •  Mật ong mù tạt  •  Bơ tỏi',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 74, 'palette': 'coral', 'y_center': 1545,
    },
    {
        'id': 'T06_sides',
        'start': 23.62, 'end': 26.52,
        'eyebrow': 'MÓN KÈM TRỨ DANH',
        'lines': ['TOKBOKKI & MÌ ĐEN'],
        'sub': 'Sốt cay dẻo mềm  •  Sợi mì tương đen bóng mượt',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 72, 'palette': 'gold', 'y_center': 1545,
    },
    {
        'id': 'T07_crunch',
        'start': 26.68, 'end': 28.98,
        'eyebrow': 'KHOẢNH KHẮC THƯỞNG THỨC',
        'lines': ['GIÒN TAN ĐÃ MIỆNG!'],
        'sub': 'Vỏ giòn rôm rốp  •  Thịt mềm mọng nước',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 76, 'palette': 'coral', 'y_center': 1545,
    },
    {
        'id': 'T08_feast',
        'start': 29.12, 'end': 34.32,
        'eyebrow': 'ĂN LÀ MÊ  •  SARANGHAE',
        'lines': ['TRỌN VẸN ĐẠI TIỆC'],
        'sub': 'Bàn tiệc Hàn Quốc ngập tràn sắc hương tại Nha Trang',
        'font': 'PlayfairDisplay-ExtraBold.ttf', 'size': 76, 'palette': 'gold', 'y_center': 1545,
    },
]

def apply_opacity_and_offset(canvas, layer, cx, cy, alpha_mult, dy=0, blur_px=0.0):
    if alpha_mult <= 0.01:
        return canvas
    im = layer
    if blur_px >= 0.6:
        im = im.filter(ImageFilter.GaussianBlur(radius=blur_px))
    if alpha_mult < 0.995:
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 3] *= alpha_mult
        im = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    px = int(round(cx - im.width / 2))
    py = int(round(cy - im.height / 2 + dy))
    canvas.alpha_composite(im, (px, py))
    return canvas

def render_one_card_mov(card):
    cid = card['id']
    dur = card['end'] - card['start']
    n_frames = max(1, int(round(dur * FPS)))
    stops = GOLD_STOPS if card['palette'] == 'gold' else CORAL_GOLD_STOPS
    fp_head = os.path.join(FONTS_DIR, card['font'])
    fp_eyeb = os.path.join(FONTS_DIR, 'Montserrat-Bold.ttf')
    fp_sub  = os.path.join(FONTS_DIR, 'BeVietnamPro-SemiBold.ttf')

    eyebrow_im = render_eyebrow_pill(card['eyebrow'], fp_eyeb, 23)
    sub_im     = render_subhead(card['sub'], fp_sub, 31)

    mov_path = os.path.join(TITLE_DIR, f"{cid}.mov")
    cmd = [
        'ffmpeg', '-y', '-v', 'error',
        '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS),
        '-i', '-',
        '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le',
        mov_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    mid_idx = n_frames // 2

    for f_i in range(n_frames):
        t = f_i / FPS
        rem = dur - t
        # Global fade out in last 0.42s
        out_a = ease_in_out(rem / 0.42) if rem < 0.42 else 1.0

        # Scrim alpha
        scrim_a = ease_in_out(min(t / 0.40, 1.0)) * out_a
        frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if scrim_a > 0.02:
            sc_arr = np.array(BOTTOM_SCRIM, dtype=np.float32)
            sc_arr[:, :, 3] *= scrim_a
            frame.alpha_composite(Image.fromarray(sc_arr.astype(np.uint8), 'RGBA'))

        # Sheen sweep across 0.25s..1.85s
        sheen_p = (t - 0.20) / 1.55 if 0.15 <= t <= 1.85 else None
        head_im = render_gradient_text_block(card['lines'], fp_head, card['size'], stops, sheen_p, stroke_px=6)

        yc = card['y_center']
        h_half = head_im.height // 2

        # Tier 0: Eyebrow (0.00s..0.38s) - generous clearance above Vietnamese uppercase accents
        p0 = ease_out_cubic(t / 0.36)
        apply_opacity_and_offset(frame, eyebrow_im, W // 2, yc - h_half - 40, p0 * out_a, dy=(1.0 - p0) * 14)

        # Tier 1: Main 5-stop Gold Headline (0.06s..0.48s with optical blur-to-focus)
        p1 = ease_out_cubic((t - 0.06) / 0.42)
        blur1 = max(0.0, (1.0 - p1) * 6.5)
        apply_opacity_and_offset(frame, head_im, W // 2, yc, p1 * out_a, dy=(1.0 - p1) * 22, blur_px=blur1)

        # Tier 2: Subhead (Staggered +0.28s per User Rules!)
        p2 = ease_out_cubic((t - 0.28) / 0.42)
        apply_opacity_and_offset(frame, sub_im, W // 2, yc + h_half + 32, p2 * out_a, dy=(1.0 - p2) * 16)

        if f_i == mid_idx:
            frame.save(os.path.join(CHECK_DIR, f"preview_{cid}.png"))

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    return mov_path

def render_endcard_mov():
    cid = 'T09_endcard'
    t_start, t_end = 34.49, 38.50
    dur = t_end - t_start
    n_frames = int(round(dur * FPS))

    fp_head = os.path.join(FONTS_DIR, 'PlayfairDisplay-ExtraBold.ttf')
    fp_bold = os.path.join(FONTS_DIR, 'Montserrat-ExtraBold.ttf')
    fp_semi = os.path.join(FONTS_DIR, 'BeVietnamPro-SemiBold.ttf')

    logo_raw = Image.open(LOGO_PATH).convert('RGBA')
    # Resize logo cleanly to width 340px
    lw = 340
    lh = int(round(logo_raw.height * (lw / logo_raw.width)))
    logo_im = logo_raw.resize((lw, lh), Image.LANCZOS)
    # Add soft warm gold glow behind logo
    glow_mask = logo_im.split()[3].filter(ImageFilter.GaussianBlur(22))
    glow_np = np.zeros((lh + 60, lw + 60, 4), dtype=np.uint8)
    gm = np.array(glow_mask, dtype=np.float32)
    glow_np[30:30+lh, 30:30+lw, 0] = 255
    glow_np[30:30+lh, 30:30+lw, 1] = 195
    glow_np[30:30+lh, 30:30+lw, 2] = 65
    glow_np[30:30+lh, 30:30+lw, 3] = np.clip(gm * 0.55, 0, 255).astype(np.uint8)
    logo_card = Image.fromarray(glow_np, 'RGBA')
    logo_card.alpha_composite(logo_im, (30, 30))

    eyebrow_im = render_eyebrow_pill('HẸN GẶP BẠN TẠI QUÁN', os.path.join(FONTS_DIR, 'Montserrat-Bold.ttf'), 23)
    sub_brand  = render_subhead('GÀ RÁN HÀN QUỐC CHUẨN VỊ  •  ĂN LÀ MÊ', fp_semi, 30)

    # Luxury Glassmorphic Gold-Bordered Info Box for CS1 ONLY (38 Nguyễn Đình Chiểu, 10:00-22:00, 0979 233 139)
    box_w, box_h = 900, 196
    info_box = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
    ibd = ImageDraw.Draw(info_box)
    ibd.rounded_rectangle([4, 4, box_w - 5, box_h - 5], radius=32, fill=(18, 10, 6, 208), outline=(252, 212, 102, 235), width=3)
    ibd.rounded_rectangle([12, 12, box_w - 13, box_h - 13], radius=26, outline=(255, 235, 168, 70), width=1)
    f_addr = ImageFont.truetype(fp_bold, 34)
    f_time = ImageFont.truetype(fp_semi, 28)
    addr_txt = "38 NGUYỄN ĐÌNH CHIỂU – TP. NHA TRANG"
    time_txt = "Mở cửa: 10:00 – 22:00   |   Hotline: 0979 233 139"
    ba = ibd.textbbox((0, 0), addr_txt, font=f_addr)
    bt = ibd.textbbox((0, 0), time_txt, font=f_time)
    ibd.text(((box_w - (ba[2]-ba[0]))//2 - ba[0], 44 - ba[1]), addr_txt, font=f_addr, fill=(255, 224, 122, 255))
    ibd.line([(140, 106), (box_w - 140, 106)], fill=(255, 212, 102, 95), width=1)
    ibd.text(((box_w - (bt[2]-bt[0]))//2 - bt[0], 124 - bt[1]), time_txt, font=f_time, fill=(255, 250, 240, 255))

    # Full-frame luxury cinema top & bottom vignette leaving center storefront (y=720..1200) crystal clear!
    end_scrim_np = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    top_dark = np.clip((0.40 - ys) / 0.40, 0.0, 1.0) ** 1.35 * 175.0
    bot_dark = np.clip((ys - 0.48) / 0.52, 0.0, 1.0) ** 1.25 * 225.0
    a_map = np.clip(32.0 + top_dark + bot_dark, 0, 232)
    end_scrim_np[:, :, 0] = 10
    end_scrim_np[:, :, 1] = 6
    end_scrim_np[:, :, 2] = 4
    end_scrim_np[:, :, 3] = a_map[:, 0].astype(np.uint8)[:, None]
    end_scrim = Image.fromarray(end_scrim_np, 'RGBA')

    mov_path = os.path.join(TITLE_DIR, f"{cid}.mov")
    cmd = [
        'ffmpeg', '-y', '-v', 'error',
        '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS),
        '-i', '-',
        '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le',
        mov_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for f_i in range(n_frames):
        t = f_i / FPS
        rem = dur - t
        fade_end = ease_in_out(rem / 0.35) if rem < 0.35 else 1.0

        frame = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sc_a = ease_in_out(min(t / 0.55, 1.0)) * fade_end
        if sc_a > 0.02:
            arr = np.array(end_scrim, dtype=np.float32)
            arr[:, :, 3] *= sc_a
            frame.alpha_composite(Image.fromarray(arr.astype(np.uint8), 'RGBA'))

        # Logo gentle scale-in in upper sky/balcony zone (y=410) so storefront sign at y=850..1180 is 100% visible!
        p_logo = ease_out_cubic(t / 0.52)
        if p_logo > 0.02:
            scale = 0.88 + 0.12 * p_logo
            sw, sh = int(logo_card.width * scale), int(logo_card.height * scale)
            lg = logo_card.resize((sw, sh), Image.LANCZOS)
            apply_opacity_and_offset(frame, lg, W // 2, 410, p_logo * fade_end, dy=(1.0 - p_logo) * 18)

        sheen_p = (t - 0.30) / 1.90 if 0.25 <= t <= 2.25 else None
        brand_im = render_gradient_text_block(['FEEL CHICKEN'], fp_head, 90, GOLD_STOPS, sheen_p, stroke_px=7)

        p_eb = ease_out_cubic((t - 0.18) / 0.42)
        apply_opacity_and_offset(frame, eyebrow_im, W // 2, 1265, p_eb * fade_end, dy=(1.0 - p_eb) * 14)

        p_br = ease_out_cubic((t - 0.26) / 0.46)
        apply_opacity_and_offset(frame, brand_im, W // 2, 1365, p_br * fade_end, dy=(1.0 - p_br) * 20, blur_px=max(0.0, (1.0 - p_br) * 5.0))

        p_sb = ease_out_cubic((t - 0.44) / 0.42)
        apply_opacity_and_offset(frame, sub_brand, W // 2, 1468, p_sb * fade_end, dy=(1.0 - p_sb) * 14)

        p_bx = ease_out_cubic((t - 0.60) / 0.48)
        apply_opacity_and_offset(frame, info_box, W // 2, 1638, p_bx * fade_end, dy=(1.0 - p_bx) * 24)

        if f_i == int(n_frames * 0.55):
            frame.save(os.path.join(CHECK_DIR, f"preview_{cid}.png"))

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    return mov_path

if __name__ == '__main__':
    print("Rendering 8 Cinema Lower-Third Title MOVs + Hero End-Card MOV in parallel...")
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(render_one_card_mov, c) for c in TITLE_CARDS]
        futs.append(ex.submit(render_endcard_mov))
        for fu in futs:
            print("  Done:", fu.result())
