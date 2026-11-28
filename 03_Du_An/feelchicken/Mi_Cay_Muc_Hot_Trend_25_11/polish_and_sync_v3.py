import shutil
from pathlib import Path
import cv2
import numpy as np

BASE = Path(r"d:\AI\full studio\projects\feelchicken_micay_muc_chay")
OUT_V3 = BASE / "XUAT_CHATGPT_DESIGN_SACH_DEP"
ART_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856")
CUT_V7 = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\cutouts_v7")

# 1. Fix top logo ("OHDOREN" -> real crisp FEEL CHICKEN logo.png) on 01_Poster_Doc_Mi_Cay_Muc_Chinh.png & upscale 2x!
p01_raw_backup = BASE / "assets" / "raw_01_doc_chatgpt.png"
p01_path = OUT_V3 / "01_Poster_Doc_Mi_Cay_Muc_9x16.png"
src_01 = OUT_V3 / "01_Poster_Doc_Mi_Cay_Muc_Chinh.png"
if src_01.exists() and not p01_raw_backup.exists():
    shutil.copy2(src_01, p01_raw_backup)

im01 = cv2.imread(str(p01_raw_backup if p01_raw_backup.exists() else src_01))
h0, w0 = im01.shape[:2]  # 1376 x 768
# Upscale 2x to 2752 x 1536 first
im2 = cv2.resize(im01, (w0 * 2, h0 * 2), interpolation=cv2.INTER_LANCZOS4)
H, W = im2.shape[:2]  # 2752 x 1536

# Sample clean warm-cream background right around the top logo (x=0.39..0.61*W, y=0.015..0.132*H)
cream_sample = np.median(im2[int(H * 0.015) : int(H * 0.05), int(W * 0.36) : int(W * 0.40)].reshape(-1, 3), axis=0).astype(np.uint8)
# Paint smooth feathered cream patch over old garbled logo (x=0.38..0.61*W, y=0.018..0.132*H)
y_a, y_b = int(H * 0.016), int(H * 0.133)
x_a, x_b = int(W * 0.385), int(W * 0.615)
mask_patch = np.zeros((H, W), dtype=np.float32)
mask_patch[y_a:y_b, x_a:x_b] = 1.0
mask_patch = cv2.GaussianBlur(mask_patch, (21, 21), 5.0)[:, :, None]
im2 = (im2.astype(np.float32) * (1.0 - mask_patch) + cream_sample[None, None, :].astype(np.float32) * mask_patch).astype(np.uint8)

# Composite real official Feel Chicken logo.png at exact same center & scale!
logo_rgba = cv2.imread(str(CUT_V7 / "logo.png"), cv2.IMREAD_UNCHANGED)
lh, lw = logo_rgba.shape[:2]
target_w = int(W * 0.205)  # ~315px
target_h = int(round(lh * target_w / lw))
logo_rs = cv2.resize(logo_rgba, (target_w, target_h), interpolation=cv2.INTER_AREA)
lx = (W - target_w) // 2
ly = int(H * 0.020)
al = logo_rs[:, :, 3:4].astype(np.float32) / 255.0
im2[ly : ly + target_h, lx : lx + target_w] = (
    logo_rs[:, :, :3].astype(np.float32) * al + im2[ly : ly + target_h, lx : lx + target_w].astype(np.float32) * (1.0 - al)
).astype(np.uint8)

# Gentle unsharp crispness after 2x upscale
blur = cv2.GaussianBlur(im2, (0, 0), 1.3)
im2 = cv2.addWeighted(im2, 1.22, blur, -0.22, 0)
cv2.imwrite(str(p01_path), im2)
if src_01.exists():
    src_01.unlink()

# Also build an optimal 4:5 Facebook Feed version (1536 x 1920) from im2 by removing excess vertical cream band?
# Wait: im2 has red/yellow corner waves, so instead let's check im2 (9:16) + 02 (1:1) + 03 (16:9) AND a 3-image FB grid preview!
im_sq = cv2.imread(str(OUT_V3 / "02_Poster_Vuong_Mi_Cay_Muc_1x1.png"))
im_wide = cv2.imread(str(OUT_V3 / "03_Banner_Ngang_Mi_Cay_Muc_16x9.png"))

cv2.imwrite(str(ART_DIR / "v3_01_doc_preview.jpg"), cv2.resize(im2, (768, 1376), interpolation=cv2.INTER_AREA), [int(cv2.IMWRITE_JPEG_QUALITY), 93])
cv2.imwrite(str(ART_DIR / "v3_02_vuong_preview.jpg"), cv2.resize(im_sq, (1200, 1200), interpolation=cv2.INTER_AREA), [int(cv2.IMWRITE_JPEG_QUALITY), 93])
cv2.imwrite(str(ART_DIR / "v3_03_ngang_preview.jpg"), cv2.resize(im_wide, (1376, 768), interpolation=cv2.INTER_AREA), [int(cv2.IMWRITE_JPEG_QUALITY), 93])
print("Polished 01 logo & exported previews:", im2.shape, im_sq.shape, im_wide.shape)
