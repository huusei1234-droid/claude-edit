import os
import glob
import cv2
import numpy as np
import pytoshop
from pytoshop.user import nested_layers
from pytoshop import enums

IN_DIR = r"d:\AI\full studio\output\cutout_moto\02_aligned_alpha"
OUT_LOCAL = r"d:\AI\full studio\output\cutout_moto\final_delivery"
OUT_DRIVE_MAIN = r"Z:\Drive của tôi\Hinh_Cat_Photoshop_Xe_May"
OUT_STUDIO_PROJ = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\cutout-xe-may-chi-duong"

os.makedirs(OUT_LOCAL, exist_ok=True)
files = sorted(glob.glob(os.path.join(IN_DIR, "IMG_*.png")))
assert len(files) == 17, f"Expected 17 files, got {len(files)}"

# 1. Find exact union bounding box across all 17 aligned 2400x2960 cutouts
ux0, uy0, ux1, uy1 = 99999, 99999, 0, 0
for fn in files:
    im = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    a = im[:, :, 3]
    ys, xs = np.where(a > 8)
    ux0 = min(ux0, int(xs.min()))
    uy0 = min(uy0, int(ys.min()))
    ux1 = max(ux1, int(xs.max()))
    uy1 = max(uy1, int(ys.max()))

print(f"Union bbox inside 2400x2960 ROI: x={ux0}..{ux1} (w={ux1-ux0+1}), y={uy0}..{uy1} (h={uy1-uy0+1})")

# Note: In ROI (X0=350, Y0=900), bike rear wheel center X is at 1465 - 350 = 1115!
BIKE_CENTER_X_ROI = 1465 - 350  # 1115
BIKE_BOTTOM_Y_ROI = uy1         # Rear tire bottom

# Build Symmetric Uniform Tight Canvas centered horizontally on BIKE_CENTER_X_ROI!
# Why symmetric around BIKE_CENTER_X_ROI? So if the user scales the PNG in CapCut around its image center,
# the motorbike stays dead-center horizontally!
half_w = max(BIKE_CENTER_X_ROI - ux0, ux1 - BIKE_CENTER_X_ROI) + 40
crop_x0 = max(0, BIKE_CENTER_X_ROI - half_w)
crop_x1 = min(2400, BIKE_CENTER_X_ROI + half_w)
# Re-symmetrize exact width (even number)
sym_half = min(BIKE_CENTER_X_ROI - crop_x0, crop_x1 - BIKE_CENTER_X_ROI)
crop_x0 = BIKE_CENTER_X_ROI - sym_half
crop_x1 = BIKE_CENTER_X_ROI + sym_half
crop_y0 = max(0, uy0 - 40)
crop_y1 = min(2960, uy1 + 40)
if (crop_y1 - crop_y0) % 2 == 1:
    crop_y0 = max(0, crop_y0 - 1)

UNIFORM_W = crop_x1 - crop_x0
UNIFORM_H = crop_y1 - crop_y0
print(f"Symmetric Uniform High-Res Canvas: {UNIFORM_W}x{UNIFORM_H} (bike centered at X={UNIFORM_W//2})")

# Also compute 1080x1920 (9:16 Video Ready) placement matching reference TikTok video:
# Reference video has rear tire bottom at y = 1785, bike centered at x = 540,
# standing helmet top around y = 740 -> total height ~ 1045px!
VID_W, VID_H = 1080, 1920
subject_total_h = uy1 - uy0
scale_916 = min(1045.0 / subject_total_h, 980.0 / (ux1 - ux0))
print(f"9:16 Video Ready scale factor: {scale_916:.4f}")

dir_916 = os.path.join(OUT_LOCAL, "01_PNG_Khung_Video_9x16_1080x1920")
dir_2k = os.path.join(OUT_LOCAL, "02_PNG_Cat_Gon_Cung_Kich_Co_2K")
os.makedirs(dir_916, exist_ok=True)
os.makedirs(dir_2k, exist_ok=True)

psd_layers_916 = []
psd_layers_2k_half = []  # Half-res (1K+) multi-layer PSD for fast Photoshop opening + full 1080x1920 PSD!

# Pose descriptions for friendly naming / preview
POSE_LABELS = {
    "IMG_7669": "01_IMG_7669_Ngoi_Thang_1",
    "IMG_7670": "02_IMG_7670_Ngoi_Thang_2",
    "IMG_7671": "03_IMG_7671_Nup_Gio_1",
    "IMG_7672": "04_IMG_7672_Nup_Gio_2",
    "IMG_7673": "05_IMG_7673_Nghieng_Trai_Duoi_Chan_Phai_1",
    "IMG_7674": "06_IMG_7674_Nghieng_Trai_Duoi_Chan_Phai_2",
    "IMG_7675": "07_IMG_7675_Nghieng_Phai_Duoi_Chan_Trai_1",
    "IMG_7676": "08_IMG_7676_Nghieng_Phai_Duoi_Chan_Trai_2",
    "IMG_7677": "09_IMG_7677_Nam_Bay_Dang_Chan",
    "IMG_7678": "10_IMG_7678_Nam_Bay_Khep_Chan_1",
    "IMG_7679": "11_IMG_7679_Nam_Bay_Khep_Chan_2",
    "IMG_7680": "12_IMG_7680_Dung_Thang_1",
    "IMG_7681": "13_IMG_7681_Dung_Thang_2",
    "IMG_7682": "14_IMG_7682_Ngoi_Ngang_Re_Trai_1",
    "IMG_7683": "15_IMG_7683_Ngoi_Ngang_Re_Trai_2",
    "IMG_7684": "16_IMG_7684_Ngoi_Ngang_Re_Phai_1",
    "IMG_7685": "17_IMG_7685_Ngoi_Ngang_Re_Phai_2",
}

scaled_w = int(round(UNIFORM_W * scale_916))
scaled_h = int(round(UNIFORM_H * scale_916))
# Place on 1080x1920 so bike center lands at X=540 and tire bottom lands at Y=1785
tire_in_uniform_y = BIKE_BOTTOM_Y_ROI - crop_y0
tire_in_scaled_y = int(round(tire_in_uniform_y * scale_916))
paste_x = 540 - (scaled_w // 2)
paste_y = 1785 - tire_in_scaled_y

for idx, fn in enumerate(files):
    base = os.path.basename(fn).replace(".png", "")
    out_stem = POSE_LABELS.get(base, base)
    im_bgra = cv2.imread(fn, cv2.IMREAD_UNCHANGED)

    # 1) Uniform High-Res 2K Cutout (exact same dimensions UNIFORM_W x UNIFORM_H for all 17!)
    cut_2k = im_bgra[crop_y0:crop_y1, crop_x0:crop_x1].copy()
    cv2.imwrite(os.path.join(dir_2k, f"{out_stem}.png"), cut_2k)

    # 2) 1080x1920 Video-Ready Cutout (exact same 1080x1920 dimensions, ready to drop into CapCut!)
    # Premultiplied resize to prevent dark/halo artifacts when downscaling RGBA!
    rgb_f = cut_2k[:, :, :3].astype(np.float32)
    a_f = cut_2k[:, :, 3:4].astype(np.float32) / 255.0
    premult = rgb_f * a_f
    premult_s = cv2.resize(premult, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
    a_s = cv2.resize(a_f, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)[..., None]
    rgb_s = np.where(a_s > 1e-4, premult_s / np.maximum(a_s, 1e-4), 0.0)
    scaled_bgra = np.dstack([
        np.clip(rgb_s + 0.5, 0, 255).astype(np.uint8),
        np.clip(a_s[:, :, 0] * 255.0 + 0.5, 0, 255).astype(np.uint8)
    ])

    canvas_916 = np.zeros((VID_H, VID_W, 4), dtype=np.uint8)
    src_x0 = max(0, -paste_x)
    src_y0 = max(0, -paste_y)
    dst_x0 = max(0, paste_x)
    dst_y0 = max(0, paste_y)
    copy_w = min(scaled_w - src_x0, VID_W - dst_x0)
    copy_h = min(scaled_h - src_y0, VID_H - dst_y0)
    canvas_916[dst_y0 : dst_y0 + copy_h, dst_x0 : dst_x0 + copy_w] = scaled_bgra[src_y0 : src_y0 + copy_h, src_x0 : src_x0 + copy_w]

    cv2.imwrite(os.path.join(dir_916, f"{out_stem}.png"), canvas_916)

    # Add to Photoshop PSD layer stack (1080x1920)
    # Tight non-zero bbox in 1080x1920 for compact fast PSD
    ys9, xs9 = np.where(canvas_916[:, :, 3] > 0)
    ly0, ly1 = int(ys9.min()), int(ys9.max()) + 1
    lx0, lx1 = int(xs9.min()), int(xs9.max()) + 1
    sub = canvas_916[ly0:ly1, lx0:lx1]
    # BGRA -> R, G, B, A channels for pytoshop
    ch_dict = {
        0: sub[:, :, 2],  # R
        1: sub[:, :, 1],  # G
        2: sub[:, :, 0],  # B
        -1: sub[:, :, 3], # Alpha
    }
    layer = nested_layers.Image(
        name=out_stem,
        visible=(idx == 0),  # First pose visible by default, others toggleable with 1 click!
        opacity=255,
        group_id=0,
        blend_mode=enums.BlendMode.normal,
        top=ly0,
        left=lx0,
        bottom=ly1,
        right=lx1,
        channels=ch_dict,
    )
    psd_layers_916.append(layer)
    print(f"Exported {out_stem}")

# Save genuine Adobe Photoshop .PSD (1080x1920 with all 17 aligned layers!)
psd_doc = nested_layers.nested_layers_to_psd(
    psd_layers_916[::-1],  # Top-to-bottom order in Photoshop Layers panel: 01 at top!
    color_mode=enums.ColorMode.rgb,
    size=(VID_H, VID_W),
    compression=enums.Compression.rle,
)
psd_path = os.path.join(OUT_LOCAL, "Xe_May_17_Tu_The_1080x1920.psd")
with open(psd_path, "wb") as fp:
    psd_doc.write(fp)
print(f"Saved multi-layer Photoshop PSD: {psd_path}")

# Also save High-Res 2K multi-layer Photoshop .PSD!
psd_layers_2k = []
for idx, fn in enumerate(files):
    base = os.path.basename(fn).replace(".png", "")
    out_stem = POSE_LABELS.get(base, base)
    cut_2k = cv2.imread(os.path.join(dir_2k, f"{out_stem}.png"), cv2.IMREAD_UNCHANGED)
    ys2, xs2 = np.where(cut_2k[:, :, 3] > 0)
    ly0, ly1 = int(ys2.min()), int(ys2.max()) + 1
    lx0, lx1 = int(xs2.min()), int(xs2.max()) + 1
    sub = cut_2k[ly0:ly1, lx0:lx1]
    ch_dict = {
        0: sub[:, :, 2],
        1: sub[:, :, 1],
        2: sub[:, :, 0],
        -1: sub[:, :, 3],
    }
    psd_layers_2k.append(nested_layers.Image(
        name=out_stem,
        visible=(idx == 0),
        opacity=255,
        group_id=0,
        blend_mode=enums.BlendMode.normal,
        top=ly0,
        left=lx0,
        bottom=ly1,
        right=lx1,
        channels=ch_dict,
    ))

psd_2k_doc = nested_layers.nested_layers_to_psd(
    psd_layers_2k[::-1],
    color_mode=enums.ColorMode.rgb,
    size=(UNIFORM_H, UNIFORM_W),
    compression=enums.Compression.rle,
)
psd_2k_path = os.path.join(OUT_LOCAL, f"Xe_May_17_Tu_The_2K_{UNIFORM_W}x{UNIFORM_H}.psd")
with open(psd_2k_path, "wb") as fp:
    psd_2k_doc.write(fp)
print(f"Saved High-Res 2K Photoshop PSD: {psd_2k_path}")
