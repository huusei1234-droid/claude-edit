import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR   = r"d:\AI\full studio\output\feelchicken-food-cinematic"
TITLE_V5  = os.path.join(OUT_DIR, "titles_v5_signboard")
CHK_V5    = os.path.join(OUT_DIR, "check_v5")
FONTS_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
os.makedirs(TITLE_V5, exist_ok=True)
os.makedirs(CHK_V5, exist_ok=True)

W, H = 1080, 1920
FPS = 30

def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def resolve_font(font_file, size):
    p = font_file if os.path.isabs(font_file) else os.path.join(FONTS_DIR, font_file)
    return ImageFont.truetype(p, size)

def draw_signboard_line(segments, tracking=2, color=(255, 255, 255), extrude_px=4, sh_blur=18, sh_op=0.65):
    """
    Renders a single line made of [(text_str, font_file, font_size), ...] so mixed Vietnamese + Korean Hangul ('사랑해')
    renders with 0 tofu boxes, in crisp solid white Feel Chicken signboard style (3D dark signboard drop-extrusion + soft shadow).
    """
    dd = ImageDraw.Draw(Image.new("L", (10, 10)))
    glyphs = []
    max_ascent = 0
    max_descent = 0
    for txt_part, ffile, fsz in segments:
        fnt = resolve_font(ffile, fsz)
        asc, desc = fnt.getmetrics()
        max_ascent = max(max_ascent, asc)
        max_descent = max(max_descent, desc)
        for ch in txt_part:
            adv = dd.textlength(ch, font=fnt)
            glyphs.append((ch, fnt, asc, adv))

    if not glyphs:
        return Image.new("RGBA", (4, 4), (0, 0, 0, 0))

    tw = int(round(sum(g[3] for g in glyphs) + tracking * max(0, len(glyphs) - 1)))
    th = max_ascent + max_descent
    pad = 48
    bw, bh = tw + pad * 2, th + pad * 2

    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    cx = float(pad)
    baseline_y = pad + max_ascent
    for ch, fnt, asc, adv in glyphs:
        md.text((int(round(cx)), baseline_y - asc), ch, font=fnt, fill=255)
        cx += adv + tracking

    out = Image.new("RGBA", (bw + extrude_px + 4, bh + extrude_px + 8), (0, 0, 0, 0))

    # Soft ambient shadow for legibility on ungraded natural footage
    sh = mask.filter(ImageFilter.GaussianBlur(sh_blur))
    sh_a = np.clip(np.array(sh, dtype=np.float32) * sh_op, 0, 255).astype(np.uint8)
    sh_im = Image.fromarray(np.dstack([np.zeros_like(sh_a)] * 3 + [sh_a]), "RGBA")
    out.alpha_composite(sh_im, (extrude_px, extrude_px + 4))

    # Subtle 3D raised-letter signboard depth (just like Feel Chicken's real 3D acrylic signboard letters!)
    if extrude_px > 0:
        ex_arr = np.zeros((bh, bw, 4), dtype=np.uint8)
        ex_arr[:, :, 0] = 36
        ex_arr[:, :, 1] = 12
        ex_arr[:, :, 2] = 12
        ex_arr[:, :, 3] = (np.array(mask, dtype=np.float32) * 0.82).astype(np.uint8)
        ex_im = Image.fromarray(ex_arr, "RGBA")
        for d in range(extrude_px, 0, -1):
            out.alpha_composite(ex_im, (d, d))

    # Crisp solid monochrome white signboard face
    fg = np.zeros((bh, bw, 4), dtype=np.uint8)
    fg[:, :, :3] = color
    fg[:, :, 3] = np.array(mask, dtype=np.uint8)
    out.alpha_composite(Image.fromarray(fg, "RGBA"), (0, 0))
    return out

def paste_c(canvas, im, cx, cy, alpha=1.0, dy=0.0, scale=1.0, blur_px=0.0):
    if alpha <= 0.01:
        return
    layer = im
    if abs(scale - 1.0) > 0.004:
        nw, nh = max(2, int(round(layer.width * scale))), max(2, int(round(layer.height * scale)))
        layer = layer.resize((nw, nh), Image.Resampling.LANCZOS)
    if blur_px > 0.35:
        layer = layer.filter(ImageFilter.GaussianBlur(blur_px))
    if alpha < 0.995:
        arr = np.array(layer, dtype=np.float32)
        arr[:, :, 3] *= alpha
        layer = Image.fromarray(arr.astype(np.uint8), "RGBA")
    canvas.alpha_composite(layer, (int(round(cx - layer.width / 2)), int(round(cy - layer.height / 2 + dy))))

def render_signboard_titles():
    SIGN_WHITE = (252, 250, 247)
    SOFT_WHITE = (236, 234, 230)
    KR_FONT    = r"C:\Windows\Fonts\malgunbd.ttf"

    # 1) Opening Signboard Lockup (0.15s - 3.85s) — Exact Feel Chicken Signboard Layout:
    #    GÀ RÁN HÀN QUỐC
    #    FEEL CHICKEN
    #    ĂN LÀ MÊ, 사랑해
    op_top  = draw_signboard_line([("GÀ RÁN HÀN QUỐC", "AsapCondensed-Bold.ttf", 40)], tracking=5, color=SIGN_WHITE, extrude_px=3, sh_blur=16, sh_op=0.65)
    op_main = draw_signboard_line([("FEEL CHICKEN", "Oswald-Bold.ttf", 142)], tracking=6, color=SIGN_WHITE, extrude_px=6, sh_blur=22, sh_op=0.70)
    op_sub  = draw_signboard_line([
        ("ĂN LÀ MÊ, ", "AsapCondensed-Bold.ttf", 36),
        ("사랑해", KR_FONT, 34),
    ], tracking=3, color=SOFT_WHITE, extrude_px=2, sh_blur=14, sh_op=0.62)

    t0_op, t1_op = 0.15, 3.85
    nf_op = int(round((t1_op - t0_op) * FPS))
    mov_op = os.path.join(TITLE_V5, "V5_T01_signboard_opening.mov")
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_op
    ], stdin=subprocess.PIPE)
    dur_op = t1_op - t0_op
    for fi in range(nf_op):
        t = fi / FPS
        # Bidirectional Blur-Focus per Overlay Physics rule (0.26s in, 0.20s out)
        pin1 = ease_out(t / 0.28)
        pin2 = ease_out((t - 0.12) / 0.28)
        pout = ease_io((dur_op - t) / 0.24) if (dur_op - t) < 0.24 else 1.0
        b_out = (1.0 - pout) * 12.0

        frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        yc = 930
        paste_c(frm, op_top,  W // 2, yc - 102, pin1 * pout, dy=(1.0 - pin1) * 8, scale=0.94 + 0.06 * pin1, blur_px=(1.0 - pin1) * 14.0 + b_out)
        paste_c(frm, op_main, W // 2, yc,       pin1 * pout, scale=0.93 + 0.07 * pin1, blur_px=(1.0 - pin1) * 16.0 + b_out)
        paste_c(frm, op_sub,  W // 2, yc + 102, pin2 * pout, dy=(1.0 - pin2) * 8, scale=0.94 + 0.06 * pin2, blur_px=(1.0 - pin2) * 14.0 + b_out)
        p.stdin.write(frm.tobytes())
    p.stdin.close(); p.wait()

    # 2) Subtle Clean Signboard Footer ('FEEL CHICKEN  •  38 Nguyễn Đình Chiểu' from 0.25s to 24.40s)
    ft_im = draw_signboard_line([("FEEL CHICKEN  •  38 Nguyễn Đình Chiểu", "AsapCondensed-SemiBold.ttf", 26)], tracking=2, color=SOFT_WHITE, extrude_px=0, sh_blur=10, sh_op=0.58)
    t0_ft, t1_ft = 0.25, 24.40
    nf_ft = int(round((t1_ft - t0_ft) * FPS))
    mov_ft = os.path.join(TITLE_V5, "V5_T02_signboard_footer.mov")
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_ft
    ], stdin=subprocess.PIPE)
    dur_ft = t1_ft - t0_ft
    for fi in range(nf_ft):
        t = fi / FPS
        a = ease_io(min(t / 0.4, 1.0)) * (ease_io((dur_ft - t) / 0.35) if (dur_ft - t) < 0.35 else 1.0) * 0.78
        frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        paste_c(frm, ft_im, W // 2, 1805, a)
        p.stdin.write(frm.tobytes())
    p.stdin.close(); p.wait()

    # 3) End-Card Signboard Lockup (24.60s - 27.60s over CS1 Walk-In DJI_0312_D.MP4 — positioned cleanly in lower third so CS1's real red signboard above stays 100% visible!)
    ec_top  = draw_signboard_line([("GÀ RÁN HÀN QUỐC", "AsapCondensed-Bold.ttf", 34)], tracking=5, color=SIGN_WHITE, extrude_px=2, sh_blur=14, sh_op=0.68)
    ec_main = draw_signboard_line([("FEEL CHICKEN", "Oswald-Bold.ttf", 118)], tracking=5, color=SIGN_WHITE, extrude_px=5, sh_blur=20, sh_op=0.72)
    ec_slog = draw_signboard_line([
        ("ĂN LÀ MÊ, ", "AsapCondensed-Bold.ttf", 32),
        ("사랑해 (Saranghae)", KR_FONT, 30),
    ], tracking=2, color=SOFT_WHITE, extrude_px=2, sh_blur=12, sh_op=0.65)
    ec_addr = draw_signboard_line([("38 Nguyễn Đình Chiểu, Nha Trang", "AsapCondensed-Bold.ttf", 36)], tracking=2, color=SIGN_WHITE, extrude_px=2, sh_blur=14, sh_op=0.70)
    ec_info = draw_signboard_line([("10:00 – 22:00   •   ĐT: 0979.233.139", "AsapCondensed-SemiBold.ttf", 30)], tracking=2, color=SOFT_WHITE, extrude_px=2, sh_blur=12, sh_op=0.68)

    sc_np = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.linspace(0.0, 1.0, H - 1180)
    sc_np[1180:, :, 3] = np.clip((ys ** 1.35) * 190.0, 0, 255).astype(np.uint8)[:, None]
    sc_im = Image.fromarray(sc_np, "RGBA")

    t0_ec, t1_ec = 24.60, 27.60
    nf_ec = int(round((t1_ec - t0_ec) * FPS))
    mov_ec = os.path.join(TITLE_V5, "V5_T03_signboard_endcard.mov")
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov_ec
    ], stdin=subprocess.PIPE)
    dur_ec = t1_ec - t0_ec
    for fi in range(nf_ec):
        t = fi / FPS
        pin1 = ease_out((t - 0.05) / 0.28)
        pin2 = ease_out((t - 0.18) / 0.28)
        pout = ease_io((dur_ec - t) / 0.24) if (dur_ec - t) < 0.24 else 1.0
        b_out = (1.0 - pout) * 10.0

        frm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sa = ease_io(min(t / 0.40, 1.0)) * pout
        if sa > 0.02:
            arr = np.array(sc_im, dtype=np.float32); arr[:, :, 3] *= sa
            frm.alpha_composite(Image.fromarray(arr.astype(np.uint8), "RGBA"))

        paste_c(frm, ec_top,  W // 2, 1335, pin1 * pout, dy=(1.0 - pin1) * 8, blur_px=(1.0 - pin1) * 12.0 + b_out)
        paste_c(frm, ec_main, W // 2, 1425, pin1 * pout, scale=0.94 + 0.06 * pin1, blur_px=(1.0 - pin1) * 14.0 + b_out)
        paste_c(frm, ec_slog, W // 2, 1515, pin2 * pout, dy=(1.0 - pin2) * 8, blur_px=(1.0 - pin2) * 12.0 + b_out)
        paste_c(frm, ec_addr, W // 2, 1595, pin2 * pout, dy=(1.0 - pin2) * 8, blur_px=(1.0 - pin2) * 12.0 + b_out)
        paste_c(frm, ec_info, W // 2, 1652, pin2 * pout * 0.95, dy=(1.0 - pin2) * 8, blur_px=(1.0 - pin2) * 12.0 + b_out)
        p.stdin.write(frm.tobytes())
    p.stdin.close(); p.wait()

    print("Rendered all 3 V5 Signboard Title MOVs!", flush=True)
    return [
        ("V5_T01_signboard_opening.mov", t0_op, t1_op),
        ("V5_T02_signboard_footer.mov",  t0_ft, t1_ft),
        ("V5_T03_signboard_endcard.mov", t0_ec, t1_ec),
    ]

if __name__ == "__main__":
    render_signboard_titles()
