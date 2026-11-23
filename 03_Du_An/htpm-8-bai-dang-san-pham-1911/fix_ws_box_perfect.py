import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance

ANH_DIR = r"Z:\Máy tính khác\My Computer\hằng thu pharma\Ảnh"
CUT_DIR = r"d:\AI\full studio\projects\htpm_8_posts_1911\assets\cutouts"
import sys
sys.path.insert(0, r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\05_SCRIPTS_TU_DONG_HOA")
from cutout_product_png import ISNetCutout

src_p = os.path.join(ANH_DIR, "DSC08838.jpg")
im = Image.open(src_p).convert("RGB")
im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
im_enh = ImageEnhance.Contrast(ImageEnhance.Sharpness(im).enhance(1.16)).enhance(1.05)

cut = ISNetCutout().remove_bg(im_enh, trim_transparent=False)
arr = np.array(cut)
rgb = arr[:, :, :3].astype(np.float32)
a = arr[:, :, 3].copy()

# Find the blue top half of the White Skin box to get exact box_left and box_right!
# Royal blue on box has B > 155 and B - R > 65
is_blue_box = (rgb[:, :, 2] > 155) & ((rgb[:, :, 2] - rgb[:, :, 0]) > 65) & (a > 180)
bys, bxs = np.where(is_blue_box)
# The bottle label also has blue on the left; split at median/cluster to get the tall box on the right!
# Let's check x histogram of blue pixels in the upper region (above bottle cap)
box_top_y = int(bys.min())
upper_blue = is_blue_box[box_top_y : box_top_y + 180, :]
_, ub_xs = np.where(upper_blue)
box_x0 = int(np.percentile(ub_xs, 0.5))
box_x1 = int(np.percentile(ub_xs, 99.5))

# Find bottle bottom and capsule bottom to locate exact floor plane of the box!
# Amber bottle & capsules have R > 130, R - B > 55, or dark amber glass
is_amber = ((rgb[:, :, 0] - rgb[:, :, 2]) > 45) & (a > 120)
ays, axs = np.where(is_amber)
# Bottle is on the left (x < box_x0 + 60)
bottle_ys = ays[axs < (box_x0 + 40)]
bottle_bottom_y = int(np.percentile(bottle_ys, 99.2))
# Box sits slightly behind bottle & capsules: its bottom edge in DSC08838.jpg is ~28px above bottle_bottom_y!
# Let's detect the exact subtle shadow/edge under the white box in original image between x=box_x0+80..box_x1-20
gray = cv2.cvtColor(np.array(im_enh), cv2.COLOR_RGB2GRAY).astype(np.float32)
# Vertical gradient dy in y = bottle_bottom_y - 90 .. bottle_bottom_y
y_search0 = bottle_bottom_y - 95
y_search1 = bottle_bottom_y - 5
strip = gray[y_search0:y_search1, box_x0 + 90 : box_x1 - 20]
row_grad = np.mean(np.abs(np.diff(strip, axis=0)), axis=1)
box_bottom_y = y_search0 + int(np.argmax(row_grad))
print(f"Detected WhiteSkin box bounds: x={box_x0}..{box_x1}, y={box_top_y}..{box_bottom_y} (bottle_bottom={bottle_bottom_y})")

# 1. Fill solid 255 alpha across the entire rectangular face of the White Skin box!
a_fixed = a.copy()
a_fixed[box_top_y + 4 : box_bottom_y, box_x0 + 3 : box_x1 - 3] = 255

# 2. Remove any thin horizontal table crease artifacts outside the box/bottle/capsules!
# Specifically below box_bottom_y on the right, keep ONLY golden capsules (warm amber/yellow chroma)!
chroma = np.max(rgb, axis=2) - np.min(rgb, axis=2)
below_box_right = np.zeros_like(a_fixed, dtype=bool)
below_box_right[box_bottom_y + 2 :, box_x0 + 35 :] = True
# Capsules have strong golden-orange chroma (> 42) or soft contact around capsules; gray crease line has chroma < 22!
is_gray_crease = below_box_right & (chroma < 28)
a_fixed[is_gray_crease] = 0

# Also clean any stray low-alpha fringe (< 40 -> 0) and smooth 1px edge
a_fixed = np.where(a_fixed < 40, 0, a_fixed).astype(np.uint8)
# Remove tiny connected components (< 250 px area)
num_l, labels, stats, _ = cv2.connectedComponentsWithStats((a_fixed > 0).astype(np.uint8))
for lbl in range(1, num_l):
    if stats[lbl, cv2.CC_STAT_AREA] < 250:
        a_fixed[labels == lbl] = 0

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
print("Saved crisp rectangular-restored 08_white_skin.png ->", out_im.size)
