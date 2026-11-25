import os
import glob
import cv2
import numpy as np
import torch
from PIL import Image
from transformers import Sam2Model, Sam2Processor

X0, Y0 = 350, 900
ALPHA_DIR = r"d:\AI\full studio\output\cutout_moto\02_aligned_alpha"

# 1. Clean 100% of kickstand stub across all 17 cutouts
# Exact curve following CVT cover bottom-left contour in full 3024x4032 coords:
kick_poly_full = np.array([
    [950, 3330],
    [1164, 3338],
    [1182, 3378],
    [1202, 3422],
    [1270, 3445],
    [1270, 3750],
    [950, 3750],
], dtype=np.int32)
kick_poly_roi = kick_poly_full - np.array([[X0, Y0]])

files = sorted(glob.glob(os.path.join(ALPHA_DIR, "IMG_*.png")))
sample = cv2.imread(files[0], cv2.IMREAD_UNCHANGED)
H, W = sample.shape[:2]

kick_mask = np.zeros((H, W), dtype=np.uint8)
cv2.fillPoly(kick_mask, [kick_poly_roi], 255)
kick_soft = cv2.GaussianBlur(kick_mask.astype(np.float32) / 255.0, (5, 5), 1.2)

for fn in files:
    im = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    a = im[:, :, 3].astype(np.float32) / 255.0
    a = a * (1.0 - kick_soft)
    im[:, :, 3] = np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)
    cv2.imwrite(fn, im)
print("Cleaned kickstand stub across all 17 images.")

# 2. Use SAM2 on RTX 3060 to segment and subtract ONLY the background parked '79-H1' scooter
# in IMG_7675, IMG_7676, and IMG_7682!
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading SAM2 on {device}...")
processor = Sam2Processor.from_pretrained("facebook/sam2.1-hiera-small")
sam2 = Sam2Model.from_pretrained("facebook/sam2.1-hiera-small").to(device).eval()

# Crop region in ROI: x=700..1200, y=750..1200
CX0, CY0, CX1, CY1 = 700, 750, 1200, 1200

# Points in ROI coordinates: (x, y), label=1 for background scooter to REMOVE, label=0 for our rider/bike to KEEP
sam_configs = {
    "IMG_7675": {
        "pos": [(905, 920), (900, 965), (905, 1015), (875, 985)],
        "neg": [(970, 980), (945, 1030), (800, 1090), (870, 1085), (1030, 920), (925, 1065)],
        "clip_box": (835, 850, 990, 1070),
    },
    "IMG_7676": {
        "pos": [(915, 920), (915, 965), (910, 1005), (885, 975)],
        "neg": [(985, 980), (955, 1035), (790, 1080), (865, 1075), (1030, 920), (945, 1015)],
        "clip_box": (840, 850, 995, 1065),
    },
    "IMG_7682": {
        "pos": [(940, 860), (955, 925), (955, 975), (915, 900), (930, 995)],
        "neg": [(1020, 1015), (980, 1045), (945, 1075), (820, 1075), (895, 1065), (1090, 980)],
        "clip_box": (860, 800, 1045, 1065),
    },
}

crops_vis = []
for name, cfg in sam_configs.items():
    fn = os.path.join(ALPHA_DIR, f"{name}.png")
    im = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    sub_bgr = im[CY0:CY1, CX0:CX1, :3]
    pil_sub = Image.fromarray(cv2.cvtColor(sub_bgr, cv2.COLOR_BGR2RGB))

    pts = [[x - CX0, y - CY0] for (x, y) in (cfg["pos"] + cfg["neg"])]
    lbls = [1] * len(cfg["pos"]) + [0] * len(cfg["neg"])

    inputs = processor(
        images=pil_sub,
        input_points=[[pts]],
        input_labels=[[lbls]],
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = sam2(**inputs)

    masks = processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]
    # Pick highest IoU score mask or union if needed; masks shape: (1, 3, Hc, Wc)
    scores = outputs.iou_scores.cpu()[0, 0].numpy()
    best_idx = int(np.argmax(scores))
    rm_mask = masks[0, best_idx].numpy().astype(np.uint8) * 255
    print(f"{name}: SAM2 best_idx={best_idx}, score={scores[best_idx]:.3f}, area={int((rm_mask>0).sum())}")

    # Restrict strictly inside clip_box so mirror / body outside box can never be touched
    bx0, by0, bx1, by1 = cfg["clip_box"]
    gate = np.zeros_like(rm_mask)
    gate[by0 - CY0 : by1 - CY0, bx0 - CX0 : bx1 - CX0] = 255
    rm_mask = cv2.bitwise_and(rm_mask, gate)
    # Dilate 2px & feather 1.5px to kill any 1px rim of the background scooter
    rm_mask = cv2.dilate(rm_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
    rm_soft = cv2.GaussianBlur(rm_mask.astype(np.float32) / 255.0, (5, 5), 1.2)

    sub_a = im[CY0:CY1, CX0:CX1, 3].astype(np.float32) / 255.0
    sub_a = sub_a * (1.0 - rm_soft)
    im[CY0:CY1, CX0:CX1, 3] = np.clip(sub_a * 255.0 + 0.5, 0, 255).astype(np.uint8)
    cv2.imwrite(fn, im)

    # Save visual check on magenta
    a_vis = im[750:1250, 700:1200, 3:4].astype(np.float32) / 255.0
    bg = np.full((500, 500, 3), (220, 0, 220), dtype=np.float32)
    comp = (im[750:1250, 700:1200, :3].astype(np.float32) * a_vis + bg * (1.0 - a_vis)).astype(np.uint8)
    cv2.putText(comp, f"{name} CLEANED", (10, 485), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    crops_vis.append(comp)

cv2.imwrite(r"d:\AI\full studio\output\cutout_moto\test\handlebar_cleaned_check.jpg", np.hstack(crops_vis), [cv2.IMWRITE_JPEG_QUALITY, 95])
print("Saved handlebar_cleaned_check.jpg")
