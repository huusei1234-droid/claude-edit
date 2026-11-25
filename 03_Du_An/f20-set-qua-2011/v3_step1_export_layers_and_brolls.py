import json, math, os, subprocess, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30.0

WORK       = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
LAYERS_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_layers_1117_v3")
BROLL_DIR  = LAYERS_DIR / "brolls"
PNG_DIR    = LAYERS_DIR / "png_layers"
BROLL_DIR.mkdir(parents=True, exist_ok=True)
PNG_DIR.mkdir(parents=True, exist_ok=True)

F20_261116 = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116")
DOC_DIR    = F20_261116 / r"Chi Oanh\dọc"
NGANG_DIR  = F20_261116 / r"Chi Oanh\ngang"
DJI_DIR    = F20_261116 / r"Chi Oanh\dji"
ANH_HAU    = F20_261116 / r"Anh Hậu"

BRAND_KIT  = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\f20_skanest")
COINY_TTF  = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"
SANS_B_TTF = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-ExtraBold.ttf"

# Palettes (F20 × SKA NEST Crimson / Pearl White / Champagne Gold)
STOPS_RED_5   = [(255, 68, 78), (242, 34, 46), (222, 18, 30), (236, 28, 40), (255, 76, 86)]
STOPS_WHITE_5 = [(255, 255, 255), (255, 252, 246), (255, 245, 232), (255, 252, 248), (255, 255, 255)]
STOPS_GOLD_5  = [(255, 252, 200), (255, 228, 102), (246, 188, 42), (255, 222, 92), (255, 248, 185)]
CRIMSON_DARK  = (204, 16, 28)
CREAM_OUTER   = (255, 252, 244)
CHOCO_SHADOW  = (38, 12, 16)

_font_cache = {}
def get_font(path: str, size: int):
    k = (path, max(10, int(round(size))))
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, k[1])
    return _font_cache[k]

def draw_four_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, col_rgba: tuple):
    pts = []
    for i in range(8):
        ang = i * (math.pi / 4.0)
        rad = r if i % 2 == 0 else r * 0.34
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    draw.polygon(pts, fill=col_rgba)

# ==============================================================================
# 1. STUDIO 2-LAYER SEPARATED-STROKE COINY ENGINE (From FEEL_CHICKEN V6!)
#    Stroke NEVER eats into Coiny's glyph body!
# ==============================================================================
_sprite_cache = {}
def make_separated_text_sprite(
    text: str, font_path: str, size: int, stops5: list,
    outer_stroke=(255, 255, 255), outer_w: int = 12,
    inner_stroke=(204, 16, 28), inner_w: int = 7,
    shadow_alpha: int = 115, glow_col=None, glow_rad: int = 0
) -> Image.Image:
    key = (text, font_path, size, tuple(stops5), outer_stroke, outer_w, inner_stroke, inner_w, shadow_alpha, glow_col, glow_rad)
    if key in _sprite_cache:
        return _sprite_cache[key]

    font = get_font(font_path, size)
    max_sw = max(outer_w, inner_w)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bbox = dummy.textbbox((0, 0), text, font=font, stroke_width=max_sw)
    tw, th = max(4, bbox[2] - bbox[0]), max(4, bbox[3] - bbox[1])
    pad = int(max(glow_rad * 2.2, 10) + max_sw + 14)
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    back = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    if glow_col and glow_rad > 0:
        gm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(gm).text((ox, oy), text, font=font, fill=255, stroke_width=max(2, inner_w), stroke_fill=255)
        gb = np.array(gm.filter(ImageFilter.GaussianBlur(radius=glow_rad)), dtype=np.float32)
        ga = np.zeros((ch, cw, 4), dtype=np.uint8)
        ga[:, :, 0], ga[:, :, 1], ga[:, :, 2] = glow_col
        ga[:, :, 3] = np.clip(gb * 0.55, 0, 255).astype(np.uint8)
        back = Image.alpha_composite(back, Image.fromarray(ga, "RGBA"))

    if shadow_alpha > 0:
        sm = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(sm).text((ox + 3, oy + 6), text, font=font, fill=255, stroke_width=max_sw, stroke_fill=255)
        sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=5.0)), dtype=np.float32) / 255.0
        sa = np.zeros((ch, cw, 4), dtype=np.uint8)
        sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = CHOCO_SHADOW
        sa[:, :, 3] = np.clip(sb * shadow_alpha, 0, 255).astype(np.uint8)
        back = Image.alpha_composite(back, Image.fromarray(sa, "RGBA"))

    if outer_w > 0 and outer_stroke is not None:
        os_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(os_im).text((ox, oy), text, font=font, fill=(*outer_stroke, 255), stroke_width=outer_w, stroke_fill=(*outer_stroke, 255))
        back = Image.alpha_composite(back, os_im)

    if inner_w > 0 and inner_stroke is not None:
        is_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(is_im).text((ox, oy), text, font=font, fill=(*inner_stroke, 255), stroke_width=inner_w, stroke_fill=(*inner_stroke, 255))
        back = Image.alpha_composite(back, is_im)

    # Pure un-choked glyph face!
    face_mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(face_mask).text((ox, oy), text, font=font, fill=255)
    m_arr = np.array(face_mask, dtype=np.float32) / 255.0

    yy = np.clip((np.arange(ch, dtype=np.float32) - pad) / max(1.0, float(th)), 0.0, 1.0)
    stops_pos = np.array([0.0, 0.28, 0.52, 0.76, 1.0], dtype=np.float32)
    stops_arr = np.array(stops5, dtype=np.float32)
    grad_1d = np.zeros((ch, 3), dtype=np.uint8)
    for c in range(3):
        grad_1d[:, c] = np.clip(np.interp(yy, stops_pos, stops_arr[:, c]), 0, 255).astype(np.uint8)
    grad_rgb = np.broadcast_to(grad_1d[:, None, :], (ch, cw, 3)).copy()
    front = Image.fromarray(np.dstack([grad_rgb, (m_arr * 255.0).astype(np.uint8)]), "RGBA")
    comp = Image.alpha_composite(back, front)
    _sprite_cache[key] = comp
    return comp

def paste_centered(canvas_im: Image.Image, sprite: Image.Image, cx: int, cy: int, scale: float = 1.0, angle: float = 0.0):
    im = sprite
    if abs(scale - 1.0) > 0.01:
        im = im.resize((max(2, int(round(im.width * scale))), max(2, int(round(im.height * scale)))), Image.Resampling.LANCZOS)
    if abs(angle) > 0.1:
        im = im.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=True)
    canvas_im.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))

def render_subtitle_line_mixed(chunks: list[tuple[str, bool]], font_size: int = 44) -> Image.Image:
    """
    Renders a single line of mixed regular (Red fill + White stroke) and emphasized (White fill + Red stroke) Coiny words
    with 0% stroke encroachment and seamless baseline alignment!
    """
    font = get_font(COINY_TTF, font_size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    # Measure exact advances of each chunk
    advances = []
    full_str = ""
    for txt, is_emph in chunks:
        w0 = dummy.textlength(full_str, font=font)
        full_str += txt
        w1 = dummy.textlength(full_str, font=font)
        advances.append((txt, is_emph, w0, w1 - w0))

    bbox = dummy.textbbox((0, 0), full_str, font=font, stroke_width=12)
    tw, th = max(8, bbox[2] - bbox[0]), max(8, bbox[3] - bbox[1])
    pad = 26
    cw, ch = tw + pad * 2, th + pad * 2
    ox, oy = pad - bbox[0], pad - bbox[1]

    # 1. Unified soft drop shadow
    line_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sm = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(sm).text((ox + 3, oy + 5), full_str, font=font, fill=255, stroke_width=10, stroke_fill=255)
    sb = np.array(sm.filter(ImageFilter.GaussianBlur(radius=4.5)), dtype=np.float32) / 255.0
    sa = np.zeros((ch, cw, 4), dtype=np.uint8)
    sa[:, :, 0], sa[:, :, 1], sa[:, :, 2] = (28, 10, 14)
    sa[:, :, 3] = np.clip(sb * 120.0, 0, 255).astype(np.uint8)
    line_im = Image.alpha_composite(line_im, Image.fromarray(sa, "RGBA"))

    # 2. Outer halo rim for emphasized White-on-Red chunks so Red border pops even over red baskets!
    halo_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo_im)
    for txt, is_emph, x_off, _ in advances:
        if is_emph and txt.strip():
            hd.text((ox + x_off, oy), txt, font=font, fill=(255, 252, 245, 255), stroke_width=12, stroke_fill=(255, 252, 245, 255))
    line_im = Image.alpha_composite(line_im, halo_im)

    # 3. Primary Stroke Layer (White stroke 8px for regular Red text; Crimson stroke 8px for emphasized White text!)
    st_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st_im)
    for txt, is_emph, x_off, _ in advances:
        scol = (*CRIMSON_DARK, 255) if is_emph else (255, 255, 255, 255)
        sw   = 8 if is_emph else 8
        sd.text((ox + x_off, oy), txt, font=font, fill=scol, stroke_width=sw, stroke_fill=scol)
    line_im = Image.alpha_composite(line_im, st_im)

    # 4. Pure Un-choked Face Layer (Ruby Red for regular; Pure White for emphasized!)
    fc_im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fc_im)
    for txt, is_emph, x_off, _ in advances:
        fcol = (255, 255, 255, 255) if is_emph else (232, 24, 36, 255)
        fd.text((ox + x_off, oy), txt, font=font, fill=fcol)
    line_im = Image.alpha_composite(line_im, fc_im)
    return line_im

def render_full_subtitle_png(parts: list[tuple[str, bool]], out_path: Path, cy_px: int = 1585):
    """Splits parts by '\n' into 1 or 2 crisp balanced lines inside TikTok Safe Zone (max width 920px)."""
    lines_chunks: list[list[tuple[str, bool]]] = [[]]
    for txt, is_emph in parts:
        segs = txt.split("\n")
        for idx, sg in enumerate(segs):
            if idx > 0:
                lines_chunks.append([])
            if sg:
                lines_chunks[-1].append((sg, is_emph))
    lines_chunks = [lc for lc in lines_chunks if lc]

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n_l = len(lines_chunks)
    line_gap = 64
    start_y = cy_px - ((n_l - 1) * line_gap) // 2
    for li, lc in enumerate(lines_chunks):
        spr = render_subtitle_line_mixed(lc, font_size=45)
        max_w = 930.0
        sc = min(1.0, max_w / max(1.0, spr.width - 36))
        paste_centered(canvas, spr, W // 2, start_y + li * line_gap, scale=sc)
    canvas.save(out_path)

def render_floating_callout_png(text: str, cx_px: int, cy_px: int, font_size: int, angle: float, style: str, out_path: Path):
    """
    Renders FEEL × HTPM style Floating White-Fill Red-Stroke Sticker ('chữ trắng viền đỏ bay bay'):
      - style='sticker': Plump Coiny Pure White Face + Deep Crimson Inner Stroke (9px) + Warm Cream Sticker Outer Rim (15px) + 2 cute 4-point Gold Sparkles!
      - style='pill_red': Sleek Rounded Pill Capsule (Crimson background + double White/Gold rim) + Coiny White-on-Red text!
    """
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if style == "pill_hdr":
        spr_t = make_separated_text_sprite(
            text, COINY_TTF, font_size, STOPS_WHITE_5,
            outer_stroke=None, outer_w=0, inner_stroke=(165, 10, 22), inner_w=5, shadow_alpha=75
        )
        pw = min(980, spr_t.width + 64)
        ph = spr_t.height + 16
        pill = Image.new("RGBA", (pw + 36, ph + 36), (0, 0, 0, 0))
        sh = Image.new("RGBA", (pw + 36, ph + 36), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([18, 24, 18 + pw, 24 + ph], radius=ph // 2, fill=(28, 8, 12, 130))
        pill = Image.alpha_composite(pill, sh.filter(ImageFilter.GaussianBlur(radius=8)))
        pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle([14, 14, 22 + pw, 22 + ph], radius=(ph + 8) // 2, fill=(255, 252, 244, 255))
        pd.rounded_rectangle([19, 19, 17 + pw, 17 + ph], radius=ph // 2, fill=(214, 22, 34, 248), outline=(255, 218, 108, 255), width=3)
        sc_t = min(1.0, (pw - 36) / max(1.0, spr_t.width))
        paste_centered(pill, spr_t, (pw + 36) // 2, (ph + 36) // 2 - 2, scale=sc_t)
        paste_centered(canvas, pill, cx_px, cy_px, angle=angle)
    else:
        # Pure Floating White-Fill Red-Stroke 3D Sticker + Gold Sparkle Stars!
        spr = make_separated_text_sprite(
            text, COINY_TTF, font_size, STOPS_WHITE_5,
            outer_stroke=CREAM_OUTER, outer_w=15,
            inner_stroke=CRIMSON_DARK, inner_w=9,
            shadow_alpha=125, glow_col=(255, 210, 120), glow_rad=6
        )
        max_w = 880.0
        sc = min(1.0, max_w / max(1.0, spr.width - 30))
        badge = Image.new("RGBA", (spr.width + 64, spr.height + 44), (0, 0, 0, 0))
        paste_centered(badge, spr, badge.width // 2, badge.height // 2)
        bd = ImageDraw.Draw(badge)
        draw_four_star(bd, 24, badge.height * 0.30, 13, (255, 232, 102, 245))
        draw_four_star(bd, badge.width - 22, badge.height * 0.68, 11, (255, 232, 102, 235))
        # Clamp cx_px safely inside 1080 canvas so zero letters ever clip!
        eff_w = badge.width * sc
        safe_cx = int(max(eff_w * 0.5 + 24, min(W - eff_w * 0.5 - 24, cx_px)))
        paste_centered(canvas, badge, safe_cx, cy_px, scale=sc, angle=angle)
    canvas.save(out_path)


# ==============================================================================
# 2. CROSS-CAMERA COLOR-MATCHED B-ROLL EXPORTER + 2 BENTO SHOWCASE STAGES!
# ==============================================================================
# Warm Sony-Showroom Color Grade Filter for flat DJI D-Log M clips:
# Lifts contrast (1.16), boosts saturation (1.34), adds subtle golden-ruby warmth (r*1.045, g*1.01, b*0.935), gentle gamma 1.03 & unsharp!
VF_DJI_TO_SONY = (
    "eq=contrast=1.15:brightness=0.015:saturation=1.34:gamma=1.03,"
    "colorbalance=rs=0.035:gs=0.005:bs=-0.035:rm=0.045:gm=0.008:bm=-0.045:rh=0.025:gh=0.005:bh=-0.025,"
    "unsharp=5:5:0.55:5:5:0.0"
)
# Gentle polish for Sony clips so highlights aren't harsh and colors match seamlessly:
VF_SONY_POLISH = (
    "eq=contrast=1.04:brightness=0.005:saturation=1.06:gamma=0.99,"
    "unsharp=5:5:0.35:5:5:0.0"
)

def bake_graded_broll(
    out_name: str, src_path: Path, src_in: float, tgt_dur: float, spd: float = 1.0,
    is_dji_flat: bool = False, zoom_crop: float = 1.0, cx_shift: float = 0.0, cy_shift: float = 0.0
) -> Path:
    """
    Renders a clean, CFR 30fps, 1080x1920 H.264 high-bitrate color-matched B-roll clip!
    cx_shift, cy_shift in [-0.5..+0.5] shift the crop window smoothly.
    """
    out_p = BROLL_DIR / out_name
    src_dur = tgt_dur * spd + 0.15
    sw_target = int(round(W * zoom_crop / 2)) * 2
    sh_target = int(round(H * zoom_crop / 2)) * 2

    # Cover-scale to (sw_target, sh_target), then crop W x H with offset
    dx_px = int(round(cx_shift * sw_target))
    dy_px = int(round(cy_shift * sh_target))
    crop_x = rf"clip((iw-{W})/2+{dx_px}\,0\,iw-{W})"
    crop_y = rf"clip((ih-{H})/2+{dy_px}\,0\,ih-{H})"

    grade_vf = VF_DJI_TO_SONY if is_dji_flat else VF_SONY_POLISH
    pts_expr = f"setpts=PTS/{spd:.4f}" if abs(spd - 1.0) > 0.01 else "null"
    vf = (
        f"{pts_expr},"
        f"scale={sw_target}:{sh_target}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={W}:{H}:{crop_x}:{crop_y},"
        f"{grade_vf},fps=30,format=yuv420p"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{src_in:.3f}", "-t", f"{src_dur:.3f}", "-i", str(src_path),
        "-an", "-vf", vf, "-t", f"{tgt_dur:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
        str(out_p)
    ], check=True)
    return out_p

def load_clip_frames(mp4_path: Path, tw: int, th: int, n_frames: int) -> np.ndarray:
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(mp4_path),
        "-vf", f"scale={tw}:{th}:force_original_aspect_ratio=increase:flags=lanczos,crop={tw}:{th}",
        "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((-1, th, tw, 3))
    if len(arr) < n_frames:
        pad = np.repeat(arr[-1:], n_frames - len(arr), axis=0)
        arr = np.concatenate([arr, pad], axis=0)
    return arr[:n_frames]

def ease_out_back(u: float, s: float = 1.35) -> float:
    u = max(0.0, min(1.0, u)) - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0

def build_bento_4mon_mp4(out_name: str, dur_s: float, card_mp4s: list[tuple[Path, str]]) -> Path:
    """
    HTPM × FEEL 2x2 Animated Bento Showcase Stage (52.18 - 56.18s: 'Một set quà tặng bên trong gồm có:'):
      - Warm luxury F20 blurred showroom backdrop + golden glow
      - Official F20 × SKA NEST Header Pill at top
      - 4 Rounded Video Cards (464 x 620 px each) popping in 01 -> 02 -> 03 -> 04 with crisp White-on-Red number tags!
    """
    out_p = BROLL_DIR / out_name
    n_f = int(round(dur_s * FPS))
    cw, ch = 462, 610
    frames_4 = [load_clip_frames(mp, cw, ch, n_f) for mp, _ in card_mp4s]

    # Build warm blurred showroom background from C3875 frame
    bg_raw = load_clip_frames(BROLL_DIR / "ov_01_intro_104sets.mp4", W, H, 1)[0]
    bg_im = Image.fromarray(bg_raw, "RGB").filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
    bg_im = Image.alpha_composite(bg_im, Image.new("RGBA", (W, H), (48, 12, 18, 138)))

    # Header pill sprite
    hdr_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    render_floating_callout_png("04 MÓN TRONG 01 SET QUÀ F20", W // 2, 165, 40, 0.0, "pill_hdr", PNG_DIR / "_tmp_hdr.png")
    hdr_im = Image.open(PNG_DIR / "_tmp_hdr.png").convert("RGBA")
    bg_im = Image.alpha_composite(bg_im, hdr_im)

    # Prebuild rounded mask & border + label sprites for the 4 cards
    mask_c = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_c).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=36, fill=255)

    card_frames_border = []
    for _, lbl in card_mp4s:
        ov_b = Image.new("RGBA", (cw + 28, ch + 36), (0, 0, 0, 0))
        sh = Image.new("RGBA", (cw + 28, ch + 36), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([14, 18, 14 + cw, 18 + ch], radius=38, fill=(18, 4, 8, 150))
        ov_b = Image.alpha_composite(ov_b, sh.filter(ImageFilter.GaussianBlur(radius=9)))
        ImageDraw.Draw(ov_b).rounded_rectangle([10, 10, 18 + cw, 18 + ch], radius=40, fill=(255, 252, 245, 255))
        lspr = make_separated_text_sprite(lbl, COINY_TTF, 30, STOPS_WHITE_5, outer_stroke=CREAM_OUTER, outer_w=11, inner_stroke=CRIMSON_DARK, inner_w=7, shadow_alpha=95)
        sc_l = min(1.0, (cw - 20) / max(1.0, lspr.width))
        paste_centered(ov_b, lspr, (cw + 28) // 2, ch - 26, scale=sc_l)
        card_frames_border.append((ov_b, lspr, sc_l))

    centers = [(288, 595), (792, 595), (288, 1245), (792, 1245)]
    staggers = [0.05, 0.32, 0.58, 0.84]

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        str(out_p)
    ], stdin=subprocess.PIPE)

    for fi in range(n_f):
        t = fi / FPS
        frame_rgba = bg_im.copy()
        for ci in range(4):
            dt = t - staggers[ci]
            if dt <= 0:
                continue
            sc = ease_out_back(min(1.0, dt / 0.28), s=1.35)
            ov_b, lspr, sc_l = card_frames_border[ci]
            card_im = ov_b.copy()
            vid_rgb = Image.fromarray(frames_4[ci][fi], "RGB")
            card_im.paste(vid_rgb, (14, 14), mask_c)
            paste_centered(card_im, lspr, (cw + 28) // 2, ch - 18, scale=sc_l)
            cx, cy = centers[ci]
            paste_centered(frame_rgba, card_im, cx, cy, scale=sc)
        enc.stdin.write(np.array(frame_rgba.convert("RGB"), dtype=np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    return out_p

def build_chung_yen_showcase_mp4(out_name: str, dur_s: float, macro_mp4: Path) -> Path:
    """
    HTPM Cinema Showcase Stage (63.15 - 66.65s: 'Táo đỏ • Đông trùng hạ thảo • Kỷ tử • 01 hộp đường phèn'):
      - Warm blurred showroom background
      - Large Rounded Cinema Video Window (964 x 660 px) at top showing real macro of round SKA NEST Bird's Nest & Stewing Box (zero red-shelf tilt!)
      - 4 Sleek Pill Cards ('01 • TÁO ĐỎ', '02 • ĐÔNG TRÙNG HẠ THẢO', '03 • KỶ TỬ', '04 • 01 HỘP ĐƯỜNG PHÈN') popping in right on the spoken beat!
    """
    out_p = BROLL_DIR / out_name
    n_f = int(round(dur_s * FPS))
    vw, vh = 956, 650
    vframes = load_clip_frames(macro_mp4, vw, vh, n_f)

    bg_raw = load_clip_frames(BROLL_DIR / "ov_01_intro_104sets.mp4", W, H, 1)[0]
    bg_im = Image.fromarray(bg_raw, "RGB").filter(ImageFilter.GaussianBlur(radius=24)).convert("RGBA")
    bg_im = Image.alpha_composite(bg_im, Image.new("RGBA", (W, H), (44, 10, 16, 142)))

    render_floating_callout_png("ĐỦ 04 NGUYÊN LIỆU CHƯNG KÈM THEO", W // 2, 145, 36, 0.0, "pill_hdr", PNG_DIR / "_tmp_hdr2.png")
    bg_im = Image.alpha_composite(bg_im, Image.open(PNG_DIR / "_tmp_hdr2.png").convert("RGBA"))

    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw - 1, vh - 1], radius=42, fill=255)
    vframe_bg = Image.new("RGBA", (vw + 28, vh + 32), (0, 0, 0, 0))
    sh = Image.new("RGBA", (vw + 28, vh + 32), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([14, 18, 14 + vw, 18 + vh], radius=44, fill=(16, 4, 8, 155))
    vframe_bg = Image.alpha_composite(vframe_bg, sh.filter(ImageFilter.GaussianBlur(radius=10)))
    ImageDraw.Draw(vframe_bg).rounded_rectangle([9, 9, 19 + vw, 19 + vh], radius=46, fill=(255, 252, 245, 255))

    # 4 Ingredient Pill Sprites (2x2 grid below the cinema window: y = 1045, 1235)
    ing_specs = [
        (0.03, "01 • TÁO ĐỎ",              295, 1065),
        (0.67, "02 • ĐÔNG TRÙNG",          785, 1065),
        (1.88, "03 • KỶ TỬ",               295, 1245),
        (2.62, "04 • ĐƯỜNG PHÈN",          785, 1245),
    ]
    ing_pills = []
    for t_in, itxt, icx, icy in ing_specs:
        pw, ph = 456, 132
        p_im = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
        psh = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
        ImageDraw.Draw(psh).rounded_rectangle([12, 16, 12 + pw, 16 + ph], radius=42, fill=(20, 6, 10, 135))
        p_im = Image.alpha_composite(p_im, psh.filter(ImageFilter.GaussianBlur(radius=7)))
        pd = ImageDraw.Draw(p_im)
        pd.rounded_rectangle([8, 8, 16 + pw, 16 + ph], radius=44, fill=(255, 252, 244, 255))
        pd.rounded_rectangle([13, 13, 11 + pw, 11 + ph], radius=39, fill=(208, 20, 32, 248), outline=(255, 222, 112, 255), width=3)
        tspr = make_separated_text_sprite(itxt, COINY_TTF, 36, STOPS_WHITE_5, outer_stroke=None, outer_w=0, inner_stroke=(130, 8, 16), inner_w=5, shadow_alpha=70)
        paste_centered(p_im, tspr, (pw + 24) // 2, (ph + 24) // 2 - 2, scale=min(1.0, (pw - 32) / max(1.0, tspr.width)))
        ing_pills.append((t_in, p_im, icx, icy))

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        str(out_p)
    ], stdin=subprocess.PIPE)

    for fi in range(n_f):
        t = fi / FPS
        fr = bg_im.copy()
        win = vframe_bg.copy()
        win.paste(Image.fromarray(vframes[fi], "RGB"), (14, 14), vmask)
        paste_centered(fr, win, W // 2, 565)
        for t_in, p_im, icx, icy in ing_pills:
            if t >= t_in:
                sc = ease_out_back(min(1.0, (t - t_in) / 0.24), s=1.42)
                paste_centered(fr, p_im, icx, icy, scale=sc)
        enc.stdin.write(np.array(fr.convert("RGB"), dtype=np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    return out_p


def main():
    t0 = time.time()
    print("Step 1A: Baking color-matched crisp 1080x1920 B-roll clips...", flush=True)

    # Bake every overlay B-roll with Sony-warmth color matching & clean centered framing!
    RAW_BROLL_JOBS = [
        # (out_name, src_path, src_in, tgt_dur, spd, is_dji_flat, zoom_crop, cx_shift, cy_shift)
        ("ov_01_intro_104sets.mp4",    DOC_DIR / "C3875.MP4",                      0.60, 2.05, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_02_anh_hau_handover.mp4", ANH_HAU / "C3920.MP4",                      4.60, 2.15, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_03_anh_hau_77sets.mp4",   ANH_HAU / "C3928.MP4",                      1.20, 2.25, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_04_phu_huynh_13sets.mp4", DOC_DIR / "C3882.MP4",                      0.60, 3.75, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_05_hanoi_10sets_pack.mp4",DOC_DIR / "C3887.MP4",                      0.50, 3.45, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_06_hcm_4sets_car.mp4",    DOC_DIR / "C3901.MP4",                      0.50, 3.70, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_07_du_104_sets_glide.mp4",DOC_DIR / "C3869.MP4",                      1.40, 2.90, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_08_showroom_bows_4k.mp4", NGANG_DIR / "DJI_20261116095310_0100_D.MP4",0.40, 3.30, 0.90, True,  1.02,  0.00,  0.00),
        ("ov_09_to_yen_soi_dai.mp4",   DJI_DIR / "DJI_20261116093322_0084_D.MP4", 14.20, 3.55, 1.00, True,  1.52, -0.04, +0.03),
        ("ov_09b_basket_macro.mp4",    DOC_DIR / "C3873.MP4",                      0.20, 3.60, 0.74, False, 1.06,  0.00, -0.04),
        ("ov_10_2hop_rong_bien.mp4",   DJI_DIR / "DJI_20261116093322_0084_D.MP4", 33.80, 4.45, 1.05, True,  1.52, -0.02, +0.03),
        ("ov_11_banh_thuyen_250g.mp4", DJI_DIR / "DJI_20261116093322_0084_D.MP4", 43.67, 2.90, 1.05, True,  1.56, +0.16, +0.03),
        ("ov_12_kep_hat_500g.mp4",     DJI_DIR / "DJI_20261116093322_0084_D.MP4", 49.29, 3.30, 1.05, True,  1.56, +0.16, +0.03),
        ("ov_13_gia_tri_nhat_yen.mp4", DOC_DIR / "C3873.MP4",                      0.90, 3.25, 0.80, False, 1.12,  0.02, -0.02),
        ("ov_14_cam_nang_open.mp4",    DJI_DIR / "DJI_20261116093955_0088_D.MP4", 13.04, 4.25, 1.05, True,  1.04,  0.00,  0.00),
        ("ov_15_cam_nang_pages.mp4",   DJI_DIR / "DJI_20261116093826_0087_D.MP4", 16.50, 4.55, 0.95, True,  1.38, +0.06, +0.22),
        ("ov_16_gio_mica.mp4",         DOC_DIR / "C3908.MP4",                      1.40, 3.35, 0.90, False, 1.04,  0.00,  0.00),
        ("ov_17_quai_da_do.mp4",       NGANG_DIR / "DJI_20261116095317_0101_D.MP4",4.60, 3.05, 0.80, True,  1.04,  0.00,  0.00),
        ("ov_18_bong_hoa_do.mp4",      DOC_DIR / "C3873.MP4",                      1.85, 3.40, 0.80, False, 1.08,  0.00, +0.04),
        ("ov_19_no_mau_be.mp4",        NGANG_DIR / "DJI_20261116095310_0100_D.MP4",0.50, 3.35, 0.80, True,  1.04,  0.00,  0.00),
        ("ov_20_f20_san_xuat_a.mp4",   DOC_DIR / "C3870.MP4",                      1.00, 2.85, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_21_f20_san_xuat_b.mp4",   DOC_DIR / "C3866.MP4",                      2.50, 2.85, 1.00, False, 1.02,  0.00,  0.00),
        ("ov_22_outro_beauty.mp4",     DOC_DIR / "C3873.MP4",                      1.10, 3.20, 0.85, False, 1.04,  0.00,  0.00),
    ]
    for args in RAW_BROLL_JOBS:
        bake_graded_broll(*args)

    print("Step 1B: Rendering HTPM × FEEL 2x2 Bento Showcase & 4-Ingredient Cinema Stage...", flush=True)
    build_bento_4mon_mp4("bento_4mon_setqua.mp4", 4.05, [
        (BROLL_DIR / "ov_09_to_yen_soi_dai.mp4", "01 • TỔ YẾN SÀO"),
        (BROLL_DIR / "ov_10_2hop_rong_bien.mp4", "02 • RONG BIỂN"),
        (BROLL_DIR / "ov_11_banh_thuyen_250g.mp4","03 • BÁNH THUYỀN"),
        (BROLL_DIR / "ov_12_kep_hat_500g.mp4",   "04 • KẸP HẠT 500G"),
    ])
    build_chung_yen_showcase_mp4("bento_4nguyenlieu_chung.mp4", 3.55, BROLL_DIR / "ov_09b_basket_macro.mp4")

    print("Step 1C: Exporting 52 Separated-Stroke Coiny Subtitle PNGs & 32 Floating White-on-Red Callout PNGs...", flush=True)
    SUB_ITEMS = [
        (4.56,  6.38,  [("Hôm nay bên Oanh đang chuẩn bị", False)]),
        (6.40,  7.96,  [("tổng cộng ", False), ("104 set quà", True)]),
        (7.98,  9.44,  [("cho các khách hàng đặt", False)]),
        (9.46,  11.48, [("làm ", False), ("quà biếu tặng", True), (" thầy cô giáo", False)]),
        (11.50, 13.65, [("nhân dịp tri ân ngày ", False), ("20/11", True)]),

        (13.96, 15.58, [("Ở ", False), ("Nha Trang", True), (" có 2 khách hàng", False)]),
        (15.64, 17.56, [("1 là ", False), ("Anh Hậu", True), (" • Trung tâm luyện thi", False)]),
        (17.58, 19.85, [("Đăng Khoa Edu", True), (" đặt ", False), ("77 set quà", True)]),
        (20.18, 22.45, [("Khách thứ 2 là ", False), ("Hội phụ huynh", True)]),
        (22.47, 23.90, [("đặt ", False), ("13 set quà", True)]),
        (24.00, 26.85, [("1 bạn giáo viên ở ", False), ("Hà Nội", True)]),
        (26.87, 27.85, [("đặt ", False), ("10 set quà", True)]),
        (27.92, 30.54, [("và 1 bạn ở ", False), ("TP. Hồ Chí Minh", True)]),
        (30.56, 31.68, [("đặt ", False), ("4 set quà", True)]),

        (31.70, 34.36, [("Tổng sáng nay bên mình chuẩn bị", False)]),
        (34.38, 36.55, [("đủ 104 set quà", True), (" nha mọi người!", False)]),

        (38.60, 40.62, [("Đây là những ", False), ("set quà", True), (" bên Oanh", False)]),
        (40.64, 42.85, [("đã chuẩn bị xong trong sáng nay ạ!", False)]),

        (45.08, 47.72, [("Bây giờ Oanh giới thiệu ", False), ("1 set quà", True)]),
        (47.74, 49.55, [("của bên Oanh cho mọi người xem nhé!", False)]),

        (52.00, 55.70, [("Một ", False), ("set quà tặng", True), (" bên trong gồm có:", False)]),
        (56.25, 58.24, [("Đầu tiên là ", False), ("1 set yến sào", True)]),
        (58.26, 61.05, [("gồm ", False), ("1 tổ yến tinh chế sợi dài", True)]),
        (61.10, 63.15, [("kèm theo đầy đủ ", False), ("nguyên liệu chưng:", True)]),
        (63.18, 66.64, [("Táo đỏ • Đông trùng\nKỷ tử • Đường phèn", True)]),

        (66.66, 69.90, [("Thứ 2 là ", False), ("2 hộp rong biển sấy giòn", True)]),
        (70.12, 72.30, [("1 hộp ", False), ("sấy giòn cay nhẹ", True)]),
        (72.42, 74.50, [("và 1 hộp ", False), ("sấy mè không cay", True)]),

        (74.80, 77.65, [("Thứ 3 là 1 gói ", False), ("bánh thuyền", True)]),
        (77.67, 79.95, [("mix hạt dinh dưỡng ", False), ("250g", True)]),

        (80.28, 84.60, [("Thứ 4 là 1 gói\n", False), ("rong biển kẹp hạt 500g", True)]),
        (84.76, 86.30, [("Ở trong này thì sẽ có từ", False)]),
        (86.32, 89.32, [("22 đến 24 thanh\n", True), ("bánh hạt dinh dưỡng!", False)]),

        (89.36, 92.68, [("Sản phẩm ", False), ("giá trị nhất", True), (" trong set quà", False)]),
        (92.70, 95.85, [("là ", False), ("1 tổ yến tinh chế sợi dài", True)]),

        (96.04, 100.20, [("Có chuẩn bị thêm ", False), ("tờ cẩm nang yến sào", True)]),
        (100.48, 103.85, [("gồm ", False), ("công dụng của yến sào", True)]),
        (103.95, 107.55, [("và hướng dẫn\n", False), ("chưng yến đúng cách", True)]),

        (107.84, 111.24, [("Tất cả được set trong ", False), ("giỏ đựng quà", True)]),
        (111.26, 114.08, [("chất liệu ", False), ("mica trong suốt\n", True), ("như thế này!", False)]),
        (114.24, 117.36, [("Bên trên có ", False), ("quai xách bằng da", True)]),
        (117.38, 119.10, [("màu đỏ đô", True), (" rất là sang trọng ạ!", False)]),
        (119.52, 122.90, [("Thiết kế thêm ", False), ("bông hoa", True), (" tạo điểm nhấn", False)]),
        (122.95, 126.15, [("và 1 chiếc ", False), ("nơ màu be", True), (" rất xinh xắn!", False)]),

        (127.52, 130.05, [("Đặc biệt các sản phẩm trong set quà", False)]),
        (130.08, 132.02, [("đều do bên Oanh ", False), ("trực tiếp sản xuất", True)]),
        (132.28, 135.40, [("nên cứ yên tâm về ", False), ("chất lượng & giá cả!", True)]),

        (135.62, 138.00, [("Oanh xin gửi ", False), ("lời cảm ơn", True), (" tới quý anh chị", False)]),
        (138.02, 140.50, [("đã tin tưởng đặt hàng ", False), ("Thực phẩm F20", True)]),
        (140.54, 144.42, [("Anh chị có nhu cầu đặt ", False), ("set quà tặng", True)]),
        (144.60, 147.00, [("làm quà biếu tặng nhân dịp lễ ", False), ("20/11", True)]),
        (147.02, 148.60, [("hãy ", False), ("inbox ngay", True), (" cho Oanh nhé!", False)]),
    ]

    sub_manifest = []
    for i, (ts0, ts1, parts) in enumerate(SUB_ITEMS, 1):
        fn = f"sub_{i:03d}.png"
        render_full_subtitle_png(parts, PNG_DIR / fn, cy_px=1590)
        sub_manifest.append({"file": fn, "t0": ts0, "t1": ts1, "text": "".join(p[0] for p in parts)})

    # Floating White-Fill Red-Stroke Stickers & Pill Headers (cx_px, cy_px in 1080x1920 — 100% Face-Safe!)
    FLOAT_SPECS = [
        # (t0, t1, text, cx_px, cy_px, font_size, angle, style)
        (0.18,   3.68, "SET QUÀ TRI ÂN 20/11",       540,  220, 44,  0.0, "pill_hdr"),
        (0.42,   3.68, "THỰC PHẨM F20 × SKA NEST",   540,  345, 42,  0.0, "sticker"),

        # Floating beside/above Chị Oanh on Track 0 (her head top is y=520px, so cy=380..430px is 100% clear!)
        (6.38,   9.30, "104 SET QUÀ!",               310,  405, 52, -3.5, "sticker"),
        (9.55,  13.55, "QUÀ BIẾU 20/11",             760,  405, 48, +3.5, "sticker"),

        # Customer Order Highlights
        (15.70, 19.88, "TRUNG TÂM ĐĂNG KHOA EDU",    540,  160, 36,  0.0, "pill_hdr"),
        (17.55, 19.88, "77 SET QUÀ!",                770,  330, 54, +3.5, "sticker"),
        (20.30, 23.85, "HỘI PHỤ HUYNH • 13 SET",     540,  240, 46, -2.0, "sticker"),
        (24.72, 27.85, "HÀ NỘI • 10 SET",            340,  280, 48, -3.0, "sticker"),
        (28.08, 31.62, "TP.HCM • 04 SET",            735,  280, 48, +3.0, "sticker"),
        (33.82, 36.60, "ĐỦ 104 SET QUÀ!",            540,  250, 56,  0.0, "sticker"),

        # Gift Basket Walkthrough (Note: 52.18-56.18s & 63.15-66.65s already have rich Bento stage titles!)
        (45.20, 49.45, "CHI TIẾT 01 SET QUÀ",        730,  380, 46, +3.0, "sticker"),
        (56.28, 61.05, "MÓN 01 • YẾN SÀO SKA NEST",  540,  165, 36,  0.0, "pill_hdr"),
        (58.30, 61.05, "01 TỔ YẾN SỢI DÀI",          540,  310, 50, -2.0, "sticker"),

        # Item 2: 2 Hộp Rong Biển Sấy Giòn
        (66.70, 74.45, "MÓN 02 • 02 HỘP RONG BIỂN",  540,  165, 36,  0.0, "pill_hdr"),
        (70.15, 74.45, "CAY NHẸ",                    300,  325, 48, -3.5, "sticker"),
        (72.42, 74.45, "SẤY MÈ KHÔNG CAY",           725,  435, 44, +3.0, "sticker"),

        # Item 3: Bánh thuyền mix hạt 250g
        (74.85, 79.92, "MÓN 03 • BÁNH THUYỀN HẠT",   540,  165, 36,  0.0, "pill_hdr"),
        (77.65, 79.92, "GÓI 250G!",                  765,  330, 52, +3.5, "sticker"),

        # Item 4: Rong biển kẹp hạt 500g
        (80.32, 85.35, "MÓN 04 • RONG BIỂN KẸP HẠT", 540,  165, 36,  0.0, "pill_hdr"),
        (82.30, 85.35, "GÓI LỚN 500G!",              740,  325, 50, +3.0, "sticker"),
        (86.28, 89.28, "22 – 24 THANH!",             765,  395, 50, +3.5, "sticker"),

        # Giá trị nhất: Tổ Yến Tinh Chế Sợi Dài
        (89.45, 92.62, "GIÁ TRỊ NHẤT!",              330,  395, 50, -3.5, "sticker"),
        (92.68, 95.82, "01 TỔ YẾN TINH CHẾ SỢI DÀI", 540,  220, 38,  0.0, "pill_hdr"),

        # Cẩm nang yến sào
        (98.60, 107.25, "TẶNG KÈM CẨM NANG YẾN SÀO", 540,  165, 36,  0.0, "pill_hdr"),
        (102.85,107.25, "CÔNG DỤNG & CÁCH CHƯNG",    540,  300, 44, -1.5, "sticker"),

        # Bao bì sang trọng: Giỏ mica, Quai da đỏ đô, Bông hoa, Nơ màu be
        (110.82,114.08, "GIỎ MICA TRONG SUỐT",       540,  230, 48,  0.0, "sticker"),
        (116.18,119.12, "QUAI XÁCH DA ĐỎ ĐÔ",        540,  230, 50, -2.0, "sticker"),
        (119.56,122.88, "HOA ĐỎ ĐIỂM NHẤN",          350,  270, 48, -3.0, "sticker"),
        (122.92,126.18, "NƠ MÀU BE XINH XẮN",        540,  230, 48, +2.0, "sticker"),

        # Trực tiếp sản xuất & CTA cuối
        (129.85,135.35, "F20 TRỰC TIẾP SẢN XUẤT",    540,  175, 38,  0.0, "pill_hdr"),
        (132.32,135.35, "GIÁ TẬN XƯỞNG!",            750,  325, 50, +3.5, "sticker"),
        (138.02,140.48, "THỰC PHẨM F20",             320,  405, 46, -3.0, "sticker"),
        (146.82,148.58, "INBOX OANH NGAY!",          745,  395, 50, +3.5, "sticker"),
    ]

    flt_manifest = []
    for i, (tf0, tf1, txt, cx, cy, fsz, ang, sty) in enumerate(FLOAT_SPECS, 1):
        fn = f"flt_{i:03d}.png"
        render_floating_callout_png(txt, cx, cy, fsz, ang, sty, PNG_DIR / fn)
        flt_manifest.append({"file": fn, "t0": tf0, "t1": tf1, "text": txt, "style": sty})

    (LAYERS_DIR / "layers_manifest.json").write_text(
        json.dumps({"subtitles": sub_manifest, "floating": flt_manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"DONE Step 1 in {time.time()-t0:.1f}s: {len(RAW_BROLL_JOBS)+2} graded/Bento B-rolls + {len(sub_manifest)} subtitle PNGs + {len(flt_manifest)} floating callout PNGs!", flush=True)

if __name__ == "__main__":
    main()
