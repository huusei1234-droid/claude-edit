import cv2
import numpy as np
import glob
import os
import json

files = sorted(glob.glob(r"d:\AI\full studio\output\cutout_moto\01_raw_png\IMG_*.png"))
ref_file = files[0]  # IMG_7669.png
ref_img = cv2.imread(ref_file, cv2.IMREAD_GRAYSCALE)
h, w = ref_img.shape

# Locate the license plate + rear fender region in IMG_7669
# In 3024x4032, the bike rear / license plate is roughly x: 1050..1950, y: 2750..3850
# Let's save a debug crop of ref_img to verify exact plate coordinates, and match SIFT features!
sift = cv2.SIFT_create(nfeatures=8000)

# Mask in reference image focusing ONLY on license plate + rear mudguard + exhaust (never touched by shoes/legs)
ref_mask = np.zeros((h, w), dtype=np.uint8)
# Let's check exact coordinates of the plate in IMG_7669 first by finding the bright white rectangle in lower center
roi = ref_img[2600:3600, 1000:2000]
_, thresh = cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
best_rect = None
best_area = 0
for cnt in contours:
    area = cv2.contourArea(cnt)
    x, y, rw, rh = cv2.boundingRect(cnt)
    if 150 < rw < 600 and 120 < rh < 500 and area > best_area:
        best_area = area
        best_rect = (x + 1000, y + 2600, rw, rh)

print("Detected plate in IMG_7669:", best_rect, "area:", best_area)
px, py, pw, ph = best_rect
# Build reference mask around plate + lower fender + muffler (below shoes in all poses!)
# Notice in IMG_7678/7679 shoes reach down to just above top of license plate, so y >= py - 20 down to py + ph + 450 is 100% rigid bike!
ref_mask[py - 10 : min(h, py + ph + 450), max(0, px - 180) : min(w, px + pw + 320)] = 255

kp_ref, des_ref = sift.detectAndCompute(ref_img, ref_mask)
print(f"Ref keypoints in rigid bike zone: {len(kp_ref)}")

bf = cv2.BFMatcher(cv2.NORM_L2)
transforms = {}

for f in files:
    name = os.path.basename(f).replace(".png", "")
    if f == ref_file:
        transforms[name] = {
            "matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            "scale": 1.0,
            "angle_deg": 0.0,
            "tx": 0.0,
            "ty": 0.0,
            "inliers": len(kp_ref),
        }
        continue

    img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
    # Search in lower half center of target image
    tgt_mask = np.zeros((h, w), dtype=np.uint8)
    tgt_mask[2200:4000, 700:2400] = 255
    kp_tgt, des_tgt = sift.detectAndCompute(img, tgt_mask)

    matches = bf.knnMatch(des_ref, des_tgt, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    # Estimate similarity transform FROM target TO reference: dst(ref) = M * src(tgt)
    src_pts = np.float32([kp_tgt[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_ref[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)

    M, inliers = cv2.estimateAffinePartial2D(src_pts, dst_pts, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    inlier_count = int(inliers.sum()) if inliers is not None else 0
    scale = float(np.sqrt(M[0, 0]**2 + M[1, 0]**2))
    angle = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    tx, ty = float(M[0, 2]), float(M[1, 2])
    print(f"{name}: scale={scale:.4f}, angle={angle:+.2f} deg, tx={tx:+.1f}, ty={ty:+.1f}, inliers={inlier_count}/{len(good)}")
    transforms[name] = {
        "matrix": M.tolist(),
        "scale": scale,
        "angle_deg": angle,
        "tx": tx,
        "ty": ty,
        "inliers": inlier_count,
    }

with open(r"d:\AI\full studio\output\cutout_moto\bike_transforms.json", "w", encoding="utf-8") as fp:
    json.dump({"plate_ref": best_rect, "transforms": transforms}, fp, indent=2)
print("Saved bike_transforms.json")
