import os
import glob
import json
import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms as T
from transformers import AutoModelForImageSegmentation

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading BiRefNet on {device}...")

model = AutoModelForImageSegmentation.from_pretrained(
    "ZhengPeng7/BiRefNet", trust_remote_code=True
).to(device).half().eval()

INFER_SIZE = (1024, 1024)
transform_image = T.Compose([
    T.Resize(INFER_SIZE, interpolation=T.InterpolationMode.BILINEAR),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

with open(r"d:\AI\full studio\output\cutout_moto\bike_transforms.json", "r", encoding="utf-8") as f:
    bike_transforms = json.load(f)["transforms"]

# Subject ROI in aligned 3024x4032 space:
# Excludes parked scooter on left (x < 330) and sky/buildings above (y < 900)
X0, Y0, X1, Y1 = 350, 900, 2750, 3860
ROI_W, ROI_H = X1 - X0, Y1 - Y0  # 2400 x 2960

# Surgical kickstand polygon in aligned 3024x4032 coordinates
kickstand_poly_full = np.array([
    [1030, 3330],
    [1160, 3342],
    [1180, 3405],
    [1150, 3565],
    [1030, 3565],
], dtype=np.int32)
kickstand_poly_roi = kickstand_poly_full - np.array([[X0, Y0]])

kick_mask = np.zeros((ROI_H, ROI_W), dtype=np.uint8)
cv2.fillPoly(kick_mask, [kickstand_poly_roi], 255)
kick_mask_blur = cv2.GaussianBlur(kick_mask.astype(np.float32) / 255.0, (7, 7), 1.5)

out_alpha_dir = r"d:\AI\full studio\output\cutout_moto\02_aligned_alpha"
os.makedirs(out_alpha_dir, exist_ok=True)

files = sorted(glob.glob(r"d:\AI\full studio\output\cutout_moto\01_raw_png\IMG_*.png"))

def decontaminate_edges(bgr: np.ndarray, alpha_f: np.ndarray) -> np.ndarray:
    """Photoshop-style Color Decontamination on semi-transparent border pixels."""
    fg_core = (alpha_f > 0.90).astype(np.uint8)
    # Propagate interior foreground colors outward into semi-transparent edge band (0.01 < alpha < 0.90)
    # using multi-pass guided dilation / inpainting
    edge_band = ((alpha_f > 0.01) & (alpha_f <= 0.90)).astype(np.uint8)
    if edge_band.sum() == 0:
        return bgr
    # Erode slightly to avoid boundary color bleed
    kernel3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    pure_fg = cv2.erode(fg_core, kernel3, iterations=1)
    # Distance-weighted color propagation via iterative box blur of premultiplied pure foreground
    w_mask = pure_fg.astype(np.float32)  # (H, W)
    premult = bgr.astype(np.float32) * w_mask[..., None]
    for ksize in (7, 15, 31):
        blur_rgb = cv2.GaussianBlur(premult, (ksize, ksize), 0)
        blur_w = cv2.GaussianBlur(w_mask, (ksize, ksize), 0)  # (H, W)
        valid = blur_w > 1e-4
        fill = np.where(valid[..., None], blur_rgb / np.maximum(blur_w[..., None], 1e-4), bgr.astype(np.float32))
        premult = np.where((w_mask > 0.5)[..., None], premult, fill * 0.5)
        w_mask = np.where(w_mask > 0.5, w_mask, np.where(valid, 0.5, 0.0))
    clean_edge_rgb = np.where((w_mask > 1e-4)[..., None], premult / np.maximum(w_mask[..., None], 1e-4), bgr.astype(np.float32))
    # Mix based on how transparent the pixel is (more transparent -> stronger decontamination)
    mix = np.clip((0.92 - alpha_f) / 0.85, 0.0, 1.0)[..., None] * edge_band[..., None]
    out = bgr.astype(np.float32) * (1.0 - mix * 0.85) + clean_edge_rgb * (mix * 0.85)
    return np.clip(out, 0, 255).astype(np.uint8)

qa_thumbs = []

for fn in files:
    name = os.path.basename(fn).replace(".png", "")
    im_bgr = cv2.imread(fn)
    M = np.array(bike_transforms[name]["matrix"], dtype=np.float64)
    # Warp full image with high-quality Lanczos4 interpolation using replicate border for background continuity during AI inference
    warped_bgr = cv2.warpAffine(
        im_bgr, M, (3024, 4032),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_REPLICATE
    )
    # Also compute valid pixel mask (in case rotated corner enters ROI, though ROI is well inside!)
    ones = np.ones((4032, 3024), dtype=np.uint8) * 255
    valid_warp = cv2.warpAffine(ones, M, (3024, 4032), flags=cv2.INTER_NEAREST, borderValue=0)

    roi_bgr = warped_bgr[Y0:Y1, X0:X1]
    roi_valid = (valid_warp[Y0:Y1, X0:X1] > 127).astype(np.float32)

    roi_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(roi_rgb)
    inp = transform_image(pil_im).unsqueeze(0).to(device).half()

    with torch.no_grad():
        preds = model(inp)[-1].sigmoid().float().cpu()[0, 0].numpy()

    alpha = cv2.resize(preds, (ROI_W, ROI_H), interpolation=cv2.INTER_CUBIC)
    alpha = np.clip(alpha, 0.0, 1.0) * roi_valid

    # Remove kickstand cleanly
    alpha = alpha * (1.0 - kick_mask_blur)

    # Connected component filtering: keep ONLY the main connected component(s) containing our motorbike / rider!
    bin_mask = (alpha > 0.15).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bin_mask, connectivity=8)
    # Anchor points inside ROI: bike license plate center (1465-X0, 3060-Y0) and bike seat (1465-X0, 2450-Y0)
    keep_labels = set()
    for ax, ay in [(1465 - X0, 3060 - Y0), (1465 - X0, 2450 - Y0), (1465 - X0, 1950 - Y0)]:
        lbl = labels[ay, ax]
        if lbl > 0:
            keep_labels.add(lbl)
    # Also keep small legitimate detached parts ONLY if very close to main mask (e.g. side mirror glass separated by thin stalk)
    main_mask = np.isin(labels, list(keep_labels)).astype(np.uint8)
    dilated_main = cv2.dilate(main_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))
    for lbl in range(1, num_labels):
        if lbl in keep_labels:
            continue
        comp = (labels == lbl)
        area = stats[lbl, cv2.CC_STAT_AREA]
        # If small part (< 15000 px, like mirror face) overlaps dilated_main, keep it; reject distant passersby!
        if area < 15000 and np.any(comp & (dilated_main > 0)):
            main_mask[comp] = 1

    # Smooth mask boundary for component gate so anti-aliased edges stay soft
    keep_gate = cv2.dilate(main_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(np.float32)
    keep_gate = cv2.GaussianBlur(keep_gate, (7, 7), 1.5)
    alpha = alpha * np.clip(keep_gate * 1.5, 0.0, 1.0)

    # Slight contrast stretch on alpha edge for crisp Photoshop feel without stair-stepping
    alpha = np.clip((alpha - 0.04) / 0.92, 0.0, 1.0)

    clean_bgr = decontaminate_edges(roi_bgr, alpha)
    alpha_u8 = (alpha * 255.0 + 0.5).astype(np.uint8)
    bgra = np.dstack([clean_bgr, alpha_u8])
    cv2.imwrite(os.path.join(out_alpha_dir, f"{name}.png"), bgra)

    # Create QA thumb on bright studio green + magenta/dark split to spot ANY edge defect!
    tw, th = 450, 555
    small_bgr = cv2.resize(clean_bgr, (tw, th), interpolation=cv2.INTER_AREA)
    small_a = cv2.resize(alpha, (tw, th), interpolation=cv2.INTER_AREA)[..., None]
    # Checkerboard dark/green background so both dark tires and bright shirt/helmet show clearly
    yy, xx = np.indices((th, tw))
    checker = (((xx // 20) + (yy // 20)) % 2 == 0)
    bg = np.where(checker[..., None], np.array([45, 195, 45], dtype=np.float32), np.array([30, 145, 30], dtype=np.float32))
    comp_vis = (small_bgr.astype(np.float32) * small_a + bg * (1.0 - small_a)).astype(np.uint8)
    cv2.rectangle(comp_vis, (0, 0), (210, 40), (0, 0, 0), -1)
    cv2.putText(comp_vis, name, (10, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 255), 2)
    qa_thumbs.append(comp_vis)
    print(f"Cut out {name}")

cols, rows = 6, 3
sheet = np.full((rows * 555, cols * 450, 3), 25, dtype=np.uint8)
for idx, t in enumerate(qa_thumbs):
    r, c = divmod(idx, cols)
    sheet[r * 555 : (r + 1) * 555, c * 450 : (c + 1) * 450] = t
cv2.imwrite(r"d:\AI\full studio\output\cutout_moto\02_qa_cutouts_sheet.jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 94])
print("Saved 02_qa_cutouts_sheet.jpg")
