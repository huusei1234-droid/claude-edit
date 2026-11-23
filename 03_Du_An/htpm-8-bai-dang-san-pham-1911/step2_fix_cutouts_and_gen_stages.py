import os, sys, shutil
from collections import deque
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from ai_ref_video import generate_ref_image_4tier, export_canvas_nodes_to_files
from cutout_product_png import ISNetCutout

PROJ_DIR  = r"d:\AI\full studio\projects\htpm_8_posts_1911"
CUT_DIR   = os.path.join(PROJ_DIR, "assets", "cutouts")
STAGE_DIR = os.path.join(PROJ_DIR, "assets", "stages")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
ANH_DIR   = r"Z:\Máy tính khác\My Computer\hằng thu pharma\Ảnh"

os.makedirs(CUT_DIR, exist_ok=True)
os.makedirs(STAGE_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

def fix_ht_logo_tight():
    """Tightly crops only the circular Yin-Yang Lotus HT emblem from 1.png."""
    p = os.path.join(ANH_DIR, "1.png")
    im = Image.open(p).convert("RGB")
    w, h = im.size
    # Restrict search strictly to upper-center emblem area (x: 20%..80%, y: 8%..55%)
    roi = im.crop((int(w * 0.20), int(h * 0.08), int(w * 0.80), int(h * 0.55)))
    arr = np.array(roi, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # Red yin-yang half OR blue lotus crescent ring
    is_emblem = ((r > 205) & (g < 75) & (b < 80)) | ((b > 170) & (r < 120) & (g < 185))
    ys, xs = np.where(is_emblem)
    cx = int(w * 0.20) + int(round((xs.min() + xs.max()) * 0.5))
    cy = int(h * 0.08) + int(round((ys.min() + ys.max()) * 0.5))
    rad = int(round(max(xs.max() - xs.min(), ys.max() - ys.min()) * 0.525))

    crop = im.crop((cx - rad, cy - rad, cx + rad, cy + rad)).resize((512, 512), Image.Resampling.LANCZOS)
    crop = ImageEnhance.Contrast(ImageEnhance.Sharpness(crop).enhance(1.25)).enhance(1.06)

    mask = Image.new("L", (1024, 1024), 0)
    ImageDraw.Draw(mask).ellipse([12, 12, 1012, 1012], fill=255)
    mask = mask.resize((512, 512), Image.Resampling.LANCZOS)
    logo_rgba = crop.convert("RGBA")
    logo_rgba.putalpha(mask)

    canvas = Image.new("RGBA", (544, 544), (0, 0, 0, 0))
    ring = Image.new("RGBA", (1088, 1088), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([8, 8, 1080, 1080], fill=(255, 255, 255, 255))
    ring = ring.resize((544, 544), Image.Resampling.LANCZOS)
    canvas = Image.alpha_composite(canvas, ring)
    canvas.alpha_composite(logo_rgba, dest=(16, 16))

    out_logo = os.path.join(CUT_DIR, "ht_logo_official.png")
    canvas.save(out_logo)
    bk_logo = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma\logos_png\ht_logo_official.png"
    shutil.copy2(out_logo, bk_logo)
    print("Fixed tight circular HT logo ->", out_logo)

def fix_whiteskin_cutout():
    """Cuts out DSC08838.jpg (White Skin Box + Bottle + Golden Capsules) with 100% solid interior."""
    src_p = os.path.join(ANH_DIR, "DSC08838.jpg")
    im = Image.open(src_p).convert("RGB")
    im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    im_enh = ImageEnhance.Contrast(ImageEnhance.Sharpness(im).enhance(1.16)).enhance(1.05)

    cut = ISNetCutout().remove_bg(im_enh, trim_transparent=False)
    arr = np.array(cut)
    a = arr[:, :, 3]

    # Fill any internal holes inside the box & bottle (where white box face blended with white bg)
    # Using morphological close + contour fill on solid alpha mask
    bin_m = (a > 90).astype(np.uint8) * 255
    bin_closed = cv2.morphologyEx(bin_m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29)))
    contours, _ = cv2.findContours(bin_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(bin_m)
    for cnt in contours:
        if cv2.contourArea(cnt) > 1500:
            cv2.drawContours(filled, [cnt], -1, 255, thickness=cv2.FILLED)

    # Erode 2px inside filled interior so smooth anti-aliased ISNet outer edge stays intact, while interior is 100% 255!
    interior = cv2.erode(filled, np.ones((5, 5), np.uint8), iterations=1)
    a_fixed = np.maximum(a, interior)
    # Clean faint outer halo (<22 -> 0)
    a_fixed = np.where(a_fixed < 22, 0, a_fixed).astype(np.uint8)
    arr[:, :, 3] = a_fixed

    ys, xs = np.where(a_fixed > 20)
    pad = 8
    out_im = Image.fromarray(arr, "RGBA").crop((
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(im_enh.width, int(xs.max()) + 1 + pad),
        min(im_enh.height, int(ys.max()) + 1 + pad),
    ))
    dst = os.path.join(CUT_DIR, "08_white_skin.png")
    out_im.save(dst)
    print("Fixed 100% solid interior 08_white_skin.png ->", out_im.size)

def slice_2x2_grid(grid_img_path: str, out_names: list):
    im = Image.open(grid_img_path).convert("RGB")
    gw, gh = im.size
    hw, hh = gw // 2, gh // 2
    # Trim 14px around center seam and outer edge to avoid any divider line
    m = 14
    quads = [
        (out_names[0], (m, m, hw - m, hh - m)),
        (out_names[1], (hw + m, m, gw - m, hh - m)),
        (out_names[2], (m, hh + m, gw - m, gh - m)),  # wait: bottom-left is m..hw-m! Fix right below!
    ]
    quads = [
        (out_names[0], (m, m, hw - m, hh - m)),
        (out_names[1], (hw + m, m, gw - m, hh - m)),
        (out_names[2], (m, hh + m, hw - m, gh - m)),
        (out_names[3], (hw + m, hh + m, gw - m, gh - m)),
    ]
    for fn, box in quads:
        q = im.crop(box).resize((1200, 1500), Image.Resampling.LANCZOS)
        q.save(os.path.join(STAGE_DIR, fn), quality=95)
        print("Saved sliced 4:5 stage:", fn)

def generate_8_bespoke_stages():
    wanted_files = [f"stage_0{i}.jpg" for i in range(1, 9)]
    if all(os.path.exists(os.path.join(STAGE_DIR, f)) for f in wanted_files):
        print("All 8 bespoke stages already exist!")
        return

    prompt_g1 = (
        "Seamless borderless 2x2 grid of 4 distinct vertical 4:5 luxury commercial cosmetic & herbal product photography backgrounds, "
        "edge-to-edge full bleed with NO white borders and NO divider lines. In EVERY panel, place an EMPTY circular display podium on the RIGHT-CENTER side (around 68% horizontal, 68% vertical) ready for product placement, while keeping the LEFT side and TOP area clean soft out-of-focus bokeh for text: "
        "Top-Left panel: Soft blush-rose & warm peach silk studio, empty pink-veined white marble podium with gold rim on right, blooming pastel pink peonies and dried herbal roots softly blurred in warm morning sunbeams. "
        "Top-Right panel: Serene pearl-pink medical-luxury spa studio, empty white marble & crystal-rimmed podium on right, flowing blush-pink silk ribbon and white camellia blossoms in soft high-key light. "
        "Bottom-Left panel: Fresh emerald-herbal wellness studio, empty light travertine & natural wood podium on right, fresh dewy green medicinal leaves, golden turmeric slices and warm honey droplets in sunlit bokeh. "
        "Bottom-Right panel: Romantic pearl-ivory & ruby-rose luxury cosmetic studio, empty frosted crystal & white marble podium on right over gentle sunlit water ripples, velvet red rose petals and white chamomile flowers."
    )

    prompt_g2 = (
        "Seamless borderless 2x2 grid of 4 distinct vertical 4:5 luxury commercial cosmetic & pharmaceutical product photography backgrounds, "
        "edge-to-edge full bleed with NO white borders and NO divider lines. In EVERY panel, place an EMPTY circular display podium on the RIGHT-CENTER side (around 68% horizontal, 68% vertical) ready for product placement, while keeping the LEFT side and TOP area clean soft out-of-focus bokeh for text: "
        "Top-Left panel: Fresh botanical emerald-jade & warm cream spa studio, empty cream travertine stone podium on right, white jasmine blossoms, dewy green betel leaves and soft morning sun rays. "
        "Top-Right panel: Glamorous magenta-plum & blush-rose satin cosmetic studio, empty glossy pearl-pink & rose-gold podium on right, flowing magenta silk drape and glowing translucent hyaluronic serum pearls. "
        "Bottom-Left panel: Imperial dark obsidian-brown & warm amber-gold luxury men's vitality studio, empty black-and-gold veined marble podium on right, warm golden rim light, glowing cordyceps, ginseng root and subtle golden embers bokeh. "
        "Bottom-Right panel: Luminous royal-sapphire blue & diamond-white skincare science studio, empty clear sapphire crystal & white pearl podium on right, floating golden vitamin E spheres and glowing ice-blue molecular light bokeh."
    )

    nid1, prov1 = generate_ref_image_4tier(prompt_g1, "HTPM_STAGES_G1", ratio="9:16", timeout_per_tier=210)
    nid2, prov2 = generate_ref_image_4tier(prompt_g2, "HTPM_STAGES_G2", ratio="9:16", timeout_per_tier=210)

    g1_raw = os.path.join(STAGE_DIR, "_grid1_raw.png")
    g2_raw = os.path.join(STAGE_DIR, "_grid2_raw.png")
    export_canvas_nodes_to_files({nid1: g1_raw, nid2: g2_raw}, timeout_s=180)

    if os.path.exists(g1_raw):
        slice_2x2_grid(g1_raw, ["stage_01.jpg", "stage_02.jpg", "stage_03.jpg", "stage_04.jpg"])
    if os.path.exists(g2_raw):
        slice_2x2_grid(g2_raw, ["stage_05.jpg", "stage_06.jpg", "stage_07.jpg", "stage_08.jpg"])

    # Build QC sheet of all 8 stages
    tiles = []
    for i in range(1, 9):
        sp = os.path.join(STAGE_DIR, f"stage_0{i}.jpg")
        if os.path.exists(sp):
            im = Image.open(sp).convert("RGB")
            im.thumbnail((300, 375))
            tiles.append(im)
    if tiles:
        sheet = Image.new("RGB", (300 * 4, 375 * 2), (20, 20, 26))
        for idx, tl in enumerate(tiles):
            sheet.paste(tl, ((idx % 4) * 300, (idx // 4) * 375))
        sheet.save(os.path.join(CHECK_DIR, "stages_8_qc.jpg"), quality=90)
        print("Saved stages_8_qc.jpg!")

if __name__ == "__main__":
    fix_ht_logo_tight()
    fix_whiteskin_cutout()
    generate_8_bespoke_stages()
