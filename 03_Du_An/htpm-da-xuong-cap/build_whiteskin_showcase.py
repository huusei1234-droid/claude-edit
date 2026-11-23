import glob, math, os, shutil, subprocess, sys
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from cutout_product_png import ISNetCutout

_isnet = None
def get_isnet():
    global _isnet
    if _isnet is None:
        _isnet = ISNetCutout()
    return _isnet

PROJ_DIR  = r"d:\AI\full studio\output\htpm-20261119"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
ANH_DIR   = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\Ảnh"
LUTS_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau"
OV4K_DIR  = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k"
STAGE_BG  = r"d:\AI\full studio\output\htpm-lt-plus-talking-head\media_v2\bg_hydrogel_stage.png"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

def cutout_studio_photo(img_path, white_thresh=214.0, chroma_thresh=22.0):
    im = Image.open(img_path).convert("RGB")
    im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    im_enh = ImageEnhance.Contrast(ImageEnhance.Sharpness(im).enhance(1.16)).enhance(1.05)
    return get_isnet().remove_bg(im_enh, trim_transparent=True)

def make_sapphire_silk_stage(vw=1280, vh=720):
    if os.path.exists(STAGE_BG):
        bg = Image.open(STAGE_BG).convert("RGB").resize((vw, vh), Image.Resampling.LANCZOS)
        arr = np.array(bg, dtype=np.float32)
        # Tint warm stage toward luminous sapphire-pearl luxury aesthetic matching White Skin royal-blue & white box!
        tint = np.zeros_like(arr)
        yy = np.linspace(0.0, 1.0, vh, dtype=np.float32)[:, None]
        tint[:, :, 0] = 215.0 * (1.0 - yy * 0.25)
        tint[:, :, 1] = 236.0 * (1.0 - yy * 0.12)
        tint[:, :, 2] = 255.0
        arr = np.clip(arr * 0.58 + tint * 0.42, 0, 255)
    else:
        yy = np.linspace(0.0, 1.0, vh, dtype=np.float32)[:, None]
        xx = np.linspace(-1.0, 1.0, vw, dtype=np.float32)[None, :]
        rad = np.sqrt(xx * xx * 0.7 + (yy - 0.42) ** 2)
        arr = np.zeros((vh, vw, 3), dtype=np.float32)
        arr[:, :, 0] = np.clip(242 - rad * 95, 110, 250)
        arr[:, :, 1] = np.clip(248 - rad * 75, 150, 254)
        arr[:, :, 2] = np.clip(255 - rad * 35, 195, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGB")

def place_product_on_stage(stage_rgb, prod_rgba, zoom=1.0, dx=0.0, dy=0.0, sheen_u=-1.0, target_h_frac=0.76):
    vw, vh = stage_rgb.size
    canvas = stage_rgb.copy().convert("RGBA")
    # Subtle studio radial spotlight behind product
    sp = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
    ImageDraw.Draw(sp).ellipse([vw // 2 - 420, vh // 2 - 280, vw // 2 + 420, vh // 2 + 290], fill=(255, 255, 255, 88))
    canvas = Image.alpha_composite(canvas, sp.filter(ImageFilter.GaussianBlur(radius=58)))

    pw0, ph0 = prod_rgba.size
    sc = min((vw * 0.78) / pw0, (vh * target_h_frac) / ph0) * zoom
    nw, nh = max(16, int(round(pw0 * sc))), max(16, int(round(ph0 * sc)))
    pr = prod_rgba.resize((nw, nh), Image.Resampling.LANCZOS)

    cx = int(round(vw * 0.5 + dx))
    cy = int(round(vh * 0.50 + dy))
    px, py = cx - nw // 2, cy - nh // 2

    # Soft contact shadow + subtle glossy reflection on pedestal surface
    sh = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - int(nw * 0.44), py + nh - 22, cx + int(nw * 0.44), py + nh + 26], fill=(12, 26, 48, 128))
    canvas = Image.alpha_composite(canvas, sh.filter(ImageFilter.GaussianBlur(radius=16)))

    refl = pr.transpose(Image.Transpose.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(radius=4.5))
    ra = np.array(refl, dtype=np.float32)
    ry = np.linspace(0.24, 0.0, nh, dtype=np.float32)[:, None]
    ra[:, :, 3] = np.clip(ra[:, :, 3] * ry, 0, 255)
    refl_im = Image.fromarray(ra.astype(np.uint8), "RGBA")
    canvas.alpha_composite(refl_im.crop((0, 0, nw, min(nh, max(1, vh - (py + nh - 4))))), dest=(max(0, px), min(vh - 1, py + nh - 4)))

    # Specular light sweep across real packaging
    if -0.2 <= sheen_u <= 1.2:
        pa = np.array(pr, dtype=np.float32)
        yy, xx = np.ogrid[0:nh, 0:nw]
        diag = (xx * 0.88 + yy * 0.46) / max(1.0, nw * 0.88 + nh * 0.46)
        band = np.exp(-((diag - sheen_u) ** 2) / 0.006) * 58.0 * (pa[:, :, 3] / 255.0)
        for c in range(3):
            pa[:, :, c] = np.clip(pa[:, :, c] + band, 0, 255)
        pr = Image.fromarray(pa.astype(np.uint8), "RGBA")

    canvas.alpha_composite(pr, dest=(px, py))
    return canvas.convert("RGB")

def septic(u):
    u = max(0.0, min(1.0, u))
    return (u ** 4) * (35.0 + u * (-84.0 + u * (70.0 - 20.0 * u)))

def render_showcase_video(out_mp4, shots, total_frames, vw=1280, vh=720):
    stage_base = make_sapphire_silk_stage(vw, vh)
    # Load Pearl Sparkles overlay if present
    ov_sp = []
    ov_p = os.path.join(OV4K_DIR, "05_Soft_Pearl_Sparkles_Bling_9x16.mp4")
    if os.path.exists(ov_p):
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", ov_p, "-vf", f"scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        while len(ov_sp) < 180:
            b = p.stdout.read(vw * vh * 3)
            if len(b) < vw * vh * 3: break
            ov_sp.append(np.frombuffer(b, np.uint8).reshape((vh, vw, 3)))
        p.stdout.close(); p.wait()

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{vw}x{vh}", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out_mp4
    ], stdin=subprocess.PIPE)

    n_shots = len(shots)
    seg_len = total_frames / float(n_shots)
    xfade_f = 12.0

    def eval_shot(si, local_u):
        cut_im, z0, z1, dx0, dx1, t_hf = shots[si]
        sm = septic(local_u)
        st_z = stage_base.resize((int(vw * (1.0 + 0.05 * sm)), int(vh * (1.0 + 0.05 * sm))), Image.Resampling.BICUBIC)
        st_crop = st_z.crop(((st_z.width - vw) // 2, (st_z.height - vh) // 2, (st_z.width - vw) // 2 + vw, (st_z.height - vh) // 2 + vh))
        return place_product_on_stage(
            st_crop, cut_im,
            zoom=z0 + (z1 - z0) * sm,
            dx=dx0 + (dx1 - dx0) * sm,
            dy=0.0,
            sheen_u=-0.25 + 1.50 * local_u,
            target_h_frac=t_hf
        )

    for fi in range(total_frames):
        si = min(n_shots - 1, int(fi // seg_len))
        f_in_seg = fi - si * seg_len
        u_loc = max(0.0, min(1.0, f_in_seg / max(1.0, seg_len)))
        im_a = eval_shot(si, u_loc)

        if si + 1 < n_shots and (seg_len - f_in_seg) < xfade_f:
            w_b = septic(1.0 - (seg_len - f_in_seg) / xfade_f)
            im_b = eval_shot(si + 1, 0.04 * w_b)
            # Soft optical flash + blur transition between real studio product angles!
            bell = math.sin(w_b * math.pi)
            arr = np.array(im_a, np.float32) * (1.0 - w_b) + np.array(im_b, np.float32) * w_b + bell * 18.0
            rgb = np.clip(arr, 0, 255).astype(np.uint8)
        else:
            rgb = np.array(im_a, np.uint8)

        if ov_sp:
            ov = ov_sp[fi % len(ov_sp)].astype(np.float32) * 0.24
            rgb = np.clip(255.0 - ((255.0 - rgb.astype(np.float32)) * (255.0 - ov)) / 255.0, 0, 255).astype(np.uint8)

        enc.stdin.write(rgb.tobytes())
    enc.stdin.close(); enc.wait()
    print(f"Rendered multi-angle real-photo showcase -> {os.path.basename(out_mp4)} ({total_frames} frames)", flush=True)

def harmonize_broll(src, dst, crop_margin=0.0):
    lut_p = os.path.join(LUTS_DIR, "10_AI_Clip_Harmonizer_Natural.cube").replace("\\", "/").replace(":", "\\:")
    scale_expr = f"scale={int(1280*(1+crop_margin))}:{int(720*(1+crop_margin))}:force_original_aspect_ratio=increase,crop=1280:720:0:0,fps=30"
    vf = f"{scale_expr},split[o][g];[g]lut3d=file='{lut_p}':interp=tetrahedral[gg];[o][gg]blend=all_expr='A*0.28+B*0.72'"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", src, "-vf", vf,
        "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", dst
    ], check=True)

def main():
    ws_kv_dir = os.path.join(ANH_DIR, "Ảnh gửi sỉ", "Viên uống trắng da, điều hòa nội tiết_ White skin")
    kv_jpg = sorted(glob.glob(os.path.join(ws_kv_dir, "*.jpg")))[0]
    cut_kv      = cutout_studio_photo(kv_jpg, white_thresh=232.0, chroma_thresh=18.0)
    cut_front   = cutout_studio_photo(os.path.join(ANH_DIR, "A1_08797.jpg"), white_thresh=208.0, chroma_thresh=22.0)
    cut_open    = cutout_studio_photo(os.path.join(ANH_DIR, "DSC08820.jpg"), white_thresh=198.0, chroma_thresh=26.0)
    cut_duo     = cutout_studio_photo(os.path.join(ANH_DIR, "DSC08824.jpg"), white_thresh=206.0, chroma_thresh=22.0)
    cut_pedestal= cutout_studio_photo(os.path.join(ANH_DIR, "DSC08834.jpg"), white_thresh=206.0, chroma_thresh=22.0)
    cut_caps    = cutout_studio_photo(os.path.join(ANH_DIR, "DSC08838.jpg"), white_thresh=206.0, chroma_thresh=22.0)

    for nm, im in [
        ("ws_cut_kv.png", cut_kv),
        ("ws_cut_front.png", cut_front),
        ("ws_cut_open.png", cut_open),
        ("ws_cut_duo.png", cut_duo),
        ("ws_cut_pedestal.png", cut_pedestal),
        ("ws_cut_caps.png", cut_caps),
    ]:
        im.save(os.path.join(MEDIA_DIR, nm))
    print("Saved 6 clean real-photo RGBA cutouts of LEGEND White Skin!")

    # Render Showcase 1: Open Royal-Blue Box -> Bottle on Pedestal (135 frames = 4.5s)
    render_showcase_video(
        os.path.join(MEDIA_DIR, "prod_ws_01_openbox.mp4"),
        shots=[
            (cut_open,     0.95, 1.04, -18.0, +10.0, 0.78),
            (cut_pedestal, 0.96, 1.05, +16.0,  -8.0, 0.80),
        ],
        total_frames=135
    )

    # Render Showcase 2: 3-Angle Hero Commercial (KV Box -> Box+Bottle Duo -> Box+Bottle+Golden Capsules, 180 frames = 6.0s)
    render_showcase_video(
        os.path.join(MEDIA_DIR, "prod_ws_02_multi_showcase.mp4"),
        shots=[
            (cut_kv,   0.95, 1.05, -14.0, +10.0, 0.80),
            (cut_duo,  0.94, 1.04, +16.0, -10.0, 0.78),
            (cut_caps, 0.95, 1.05, -12.0, +12.0, 0.78),
        ],
        total_frames=180
    )

    # Copy & LUT-harmonize all clinical dermatology & lifestyle B-roll clips
    brolls = [
        (r"d:\AI\full studio\output\htpm-ddvs-2\media\m1_skincare_daily.mp4",                "b01_skincare_steps.mp4", 0.0),
        (r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\c4_viral_trend_buy.mp4",  "b02_many_products.mp4",  0.0),
        (r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\c5_cosmetic_vanity.mp4",  "b03_vanity_sigh.mp4",    0.0),
        (r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\c2_barrier_damaged.mp4",  "b04_acne_redness.mp4",   0.0),
        (r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\c3_oily_dehydrated.mp4",  "b05_dull_skin.mp4",      0.0),
        (r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\c6_late_night_2am.mp4",   "b06_late_night_2am.mp4", 0.0),
        (r"d:\AI\full studio\output\av-protein-talking-head\media\broll_c02_meal.mp4",       "b07_healthy_meal.mp4",   0.10),
        (r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\c8_healthy_routine.mp4",  "b08_morning_water.mp4",  0.0),
        (r"d:\AI\full studio\output\htpm-ddvs-2\media\m2_delayed_worry.mp4",                 "b09_work_stress.mp4",    0.0),
        (r"d:\AI\full studio\output\av-protein-talking-head\media\broll_c05_vitd.mp4",       "b10_sunlight_uv.mp4",    0.10),
        (r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\c7_junkfood_lowwater.mp4","b11_unbalanced_diet.mp4",0.0),
    ]
    for sp, fn, cm in brolls:
        dp = os.path.join(MEDIA_DIR, fn)
        if not os.path.exists(dp):
            harmonize_broll(sp, dp, crop_margin=cm)
            print("Harmonized:", fn)

    shutil.copy2(r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da\media\st_02_dry.jpg", os.path.join(MEDIA_DIR, "st_02_dry.jpg"))

    # Build visual QC sheet of the 6 White Skin cutouts + showcase frames
    tiles = []
    for t_s, vfn in [(0.8, "prod_ws_01_openbox.mp4"), (3.2, "prod_ws_01_openbox.mp4"), (0.8, "prod_ws_02_multi_showcase.mp4"), (2.8, "prod_ws_02_multi_showcase.mp4"), (4.8, "prod_ws_02_multi_showcase.mp4")]:
        tmp = os.path.join(CHECK_DIR, f"_ws_{vfn}_{t_s}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t_s), "-i", os.path.join(MEDIA_DIR, vfn), "-frames:v", "1", tmp], check=True)
        im = Image.open(tmp).convert("RGB"); im.thumbnail((380, 230))
        bg = Image.new("RGB", (400, 260), (16, 20, 30))
        bg.paste(im, ((400 - im.width) // 2, (235 - im.height) // 2))
        ImageDraw.Draw(bg).text((12, 238), f"{vfn} @ {t_s}s", fill=(255, 230, 140))
        tiles.append(bg)

    sheet = Image.new("RGB", (400 * 3, 260 * 2), (16, 20, 30))
    for i, tl in enumerate(tiles):
        sheet.paste(tl, ((i % 3) * 400, (i // 3) * 260))
    sheet.save(os.path.join(CHECK_DIR, "whiteskin_showcase_qc.jpg"), quality=92)
    print("Saved whiteskin_showcase_qc.jpg!")

if __name__ == "__main__":
    main()
