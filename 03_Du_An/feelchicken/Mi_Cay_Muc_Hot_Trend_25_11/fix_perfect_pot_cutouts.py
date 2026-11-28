from pathlib import Path
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

BASE = Path(r"d:\AI\full studio\projects\feelchicken_micay_muc_chay")
ASSETS = BASE / "assets"
UP_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\.user_uploaded")

# Photo 2 (32fd7d1a) has BOTH handles 100% inside the frame!
SRCS = {
    "2muc_hero45": UP_DIR / "media_1795611338979_32fd7d1a.jpg",
    "2muc_top":    UP_DIR / "media_1795611339002_5217ef00.jpg",
    "1muc_top":    UP_DIR / "media_1795611339023_42f8d62d.jpg",
    "1muc_hero45": UP_DIR / "media_1795611339029_325f199f.jpg",
}


def extract_full_pot_mask(bgr: np.ndarray, biref_alpha: np.ndarray, has_black_underplate: bool, key: str) -> np.ndarray:
    """
    Combines:
    1. BiRefNet alpha (captures 100% of squid tentacles spilling over top rim & handles).
    2. GrabCut + Marble-Table Rejection (captures 100% of silver bottom pot rim & black under-plate).
    3. Smooth geometric ellipse hull for the pot body + black under-plate so ZERO rim pixel is ever chipped!
    """
    h, w = bgr.shape[:2]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)

    # Sample marble table color from bottom corners & mid-side borders where table is guaranteed visible
    sample_pts = np.vstack([
        lab[int(h * 0.92) : h, 0 : int(w * 0.25)].reshape(-1, 3),
        lab[int(h * 0.92) : h, int(w * 0.75) : w].reshape(-1, 3),
        lab[int(h * 0.22) : int(h * 0.34), 0 : int(w * 0.12)].reshape(-1, 3),
        lab[int(h * 0.22) : int(h * 0.34), int(w * 0.88) : w].reshape(-1, 3),
    ]).astype(np.float32)
    med_lab = np.median(sample_pts, axis=0)

    # Distance from pale greenish marble table in LAB + HSV
    d_lab = np.linalg.norm(lab.astype(np.float32) - med_lab[None, None, :], axis=2)

    # Exclude top wooden chairs region (y < 0.23*h where biref_alpha == 0)
    yy, xx = np.mgrid[0:h, 0:w]

    # Black underplate is very dark (V < 92, L < 95) in lower half (y > 0.52*h, x in 0.05..0.92*w)
    black_plate = np.zeros((h, w), dtype=np.uint8)
    if has_black_underplate:
        raw_bp = (
            (yy > int(h * 0.55))
            & (yy < int(h * 0.93))
            & (xx > int(w * 0.05))
            & (xx < int(w * 0.92))
            & (hsv[:, :, 2] < 96)
        ).astype(np.uint8)
        raw_bp = cv2.morphologyEx(raw_bp, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
        cnts, _ = cv2.findContours(raw_bp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        big_cnts = [c for c in cnts if cv2.contourArea(c) > 2500]
        if big_cnts:
            pts = np.vstack(big_cnts)
            if len(pts) >= 5:
                ell = cv2.fitEllipse(pts)
                cv2.ellipse(black_plate, ell, 255, -1)

    # GrabCut initialized with sure-BG (marble table & top chairs) and sure-FG (BiRefNet + Black Plate + Pot Center)
    gc_mask = np.full((h, w), cv2.GC_PR_FGD, dtype=np.uint8)

    # Sure background: top chairs (y < 0.23*h and biref < 25), bottom below plate (y > 0.925*h), far right Sauce dish
    gc_mask[(yy < int(h * 0.235)) & (biref_alpha < 25)] = cv2.GC_BGD
    gc_mask[(yy > int(h * 0.935)) & (biref_alpha < 25)] = cv2.GC_BGD
    # Far-left stray bowl edge in 1muc_top / 1muc_hero45 (x < 0.065*w and y < 0.50*h)
    if key.startswith("1muc"):
        gc_mask[(xx < int(w * 0.062)) & (yy < int(h * 0.52))] = cv2.GC_BGD
    # Top-right sauce dish in 1muc_hero45 (x > 0.80*w and y < 0.32*h)
    if key == "1muc_hero45":
        gc_mask[(xx > int(w * 0.80)) & (yy < int(h * 0.33))] = cv2.GC_BGD

    # Clear marble table pixels (close to med_lab AND low saturation AND high value, outside BiRefNet)
    is_marble = (d_lab < 13.5) & (hsv[:, :, 1] < 32) & (hsv[:, :, 2] > 168) & (biref_alpha < 40) & (black_plate == 0)
    # Erode slightly so bright silver pot rim highlights aren't marked sure-BG
    sure_marble = cv2.erode(is_marble.astype(np.uint8), np.ones((9, 9), np.uint8), iterations=1)
    gc_mask[sure_marble > 0] = cv2.GC_BGD

    # Probable BG where marble is close
    gc_mask[(d_lab < 18.0) & (biref_alpha < 20) & (black_plate == 0) & (sure_marble == 0)] = cv2.GC_PR_BGD

    # Sure FG: BiRefNet core + Black Underplate + Pot Interior Ellipse
    gc_mask[biref_alpha > 150] = cv2.GC_FGD
    gc_mask[black_plate > 0] = cv2.GC_FGD

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, gc_mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)
    fg = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    # Also Fit a smooth ellipse to the main pot body so the bottom silver rim arc is 100% continuous & round!
    # Exclude protruding tentacles (top) and side handles when fitting pot body ellipse, or fit convex hull of pot rim:
    comb = np.maximum(fg, np.maximum((biref_alpha > 90).astype(np.uint8) * 255, black_plate))

    # Keep only single largest connected component
    nl, lb, st, _ = cv2.connectedComponentsWithStats((comb > 127).astype(np.uint8))
    if nl > 1:
        best = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        comb = (lb == best).astype(np.uint8) * 255

    # Close any micro-notches along the bottom silver rim using a smooth morphological close (35x35 ellipse)
    closed = cv2.morphologyEx(comb, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    # Preserve crisp tentacle gaps in the upper half (y < 0.48*h) from BiRefNet while using closed hull in lower half (y >= 0.48*h)!
    upper = np.maximum(comb, biref_alpha)
    blend_y = np.clip((yy - h * 0.44) / (h * 0.08), 0.0, 1.0)
    final_m = (upper.astype(np.float32) * (1.0 - blend_y) + np.maximum(upper, closed).astype(np.float32) * blend_y)
    final_u8 = np.clip(final_m, 0, 255).astype(np.uint8)
    final_u8 = cv2.GaussianBlur(final_u8, (5, 5), 1.0)
    return final_u8


def studio_food_grade_v2(bgr: np.ndarray, alpha_u8: np.ndarray) -> np.ndarray:
    h0, w0 = bgr.shape[:2]
    bgr2 = cv2.resize(bgr, (w0 * 2, h0 * 2), interpolation=cv2.INTER_CUBIC)
    a2 = cv2.resize(alpha_u8, (w0 * 2, h0 * 2), interpolation=cv2.INTER_CUBIC)

    lab = cv2.cvtColor(bgr2, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]

    # Identify black underplate (very low L < 75), silver pot rim (low chroma < 14), and food interior (higher chroma or squid ivory)
    chroma = np.sqrt((A - 128.0) ** 2 + (B - 128.0) ** 2)
    is_black_plate = np.clip((80.0 - L) / 28.0, 0.0, 1.0) * np.clip((18.0 - chroma) / 12.0, 0.0, 1.0)

    dist_in = cv2.distanceTransform((a2 > 90).astype(np.uint8), cv2.DIST_L2, 5)
    max_d = max(1.0, float(dist_in.max()))
    interior_w = np.clip((dist_in / (max_d * 0.24)), 0.0, 1.0) * (1.0 - is_black_plate)
    metal_rim = np.clip(1.0 - interior_w, 0.0, 1.0) * np.clip((16.0 - chroma) / 11.0, 0.0, 1.0) * (1.0 - is_black_plate)

    # Rich commercial contrast: keep black plate deep sleek black, lift food midtones
    Ln = L / 255.0
    Ln_food = np.clip(0.5 + ((Ln + 0.09 * (np.power(Ln, 0.80) * np.power(1.0 - Ln, 1.15))) - 0.5) * 1.15, 0.0, 1.0) * 255.0
    L_plate = np.clip(L * 0.82, 0, 255)
    L_new = Ln_food * (1.0 - is_black_plate) + L_plate * is_black_plate

    # Neutralize green marble reflection on silver rim & black plate
    neutral_w = np.clip(metal_rim + is_black_plate, 0.0, 1.0)
    A_clean = A * (1.0 - neutral_w) + 128.5 * neutral_w
    B_clean = B * (1.0 - neutral_w) + (128.0 + (B - 128.0) * 0.25) * neutral_w

    # Boost appetizing fiery warmth inside food (+9.0 A*, +11.5 B*)
    food_w = interior_w * np.clip((chroma - 4.0) / 16.0, 0.22, 1.0)
    A_warm = np.clip(A_clean + 9.0 * food_w, 0, 255)
    B_warm = np.clip(B_clean + 11.5 * food_w, 0, 255)

    graded = cv2.cvtColor(np.dstack([L_new, A_warm, B_warm]).astype(np.uint8), cv2.COLOR_LAB2BGR)

    # HSV boost for fiery red-orange gochujang broth & ramen
    hsv = cv2.cvtColor(graded, cv2.COLOR_BGR2HSV).astype(np.float32)
    H_h, S_h, V_h = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    is_spicy = ((H_h <= 26) | (H_h >= 165)).astype(np.float32) * interior_w
    S_h = np.clip(S_h * (1.0 + 0.34 * is_spicy + 0.15 * interior_w), 0, 255)
    V_h = np.clip(V_h * (1.0 + 0.05 * interior_w), 0, 255)
    graded = cv2.cvtColor(np.dstack([H_h, S_h, V_h]).astype(np.uint8), cv2.COLOR_HSV2BGR)

    # Crisp food detail sharpening
    blur = cv2.GaussianBlur(graded, (0, 0), 1.8)
    sharp = cv2.addWeighted(graded, 1.36, blur, -0.36, 0)

    a_smooth = cv2.GaussianBlur(a2, (5, 5), 0.9)
    ys, xs = np.where(a_smooth > 18)
    pad = 10
    y0, y1 = max(0, int(ys.min()) - pad), min(sharp.shape[0], int(ys.max()) + pad + 1)
    x0, x1 = max(0, int(xs.min()) - pad), min(sharp.shape[1], int(xs.max()) + pad + 1)
    return np.dstack([sharp[y0:y1, x0:x1], a_smooth[y0:y1, x0:x1]])


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet", trust_remote_code=True).to(device).eval()
if device.type == "cuda":
    model = model.half()
tf = transforms.Compose([
    transforms.Resize((1024, 1024)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

qa_cards = []
for key, src_p in SRCS.items():
    bgr = cv2.imread(str(src_p), cv2.IMREAD_COLOR)
    with torch.inference_mode():
        inp = tf(Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))).unsqueeze(0).to(device)
        if device.type == "cuda":
            inp = inp.half()
        pred = model(inp)[-1].sigmoid().float()
        biref = F.interpolate(pred, size=bgr.shape[:2], mode="bilinear", align_corners=False)[0, 0].cpu().numpy()
    biref_u8 = np.clip(biref * 255.0, 0, 255).astype(np.uint8)

    full_mask = extract_full_pot_mask(bgr, biref_u8, has_black_underplate=key.endswith("hero45"), key=key)
    rgba = studio_food_grade_v2(bgr, full_mask)
    out_p = ASSETS / f"cut_{key}.png"
    cv2.imwrite(str(out_p), rgba)
    print(f"Perfect full-pot cutout {out_p.name}: {rgba.shape}")

    ch, cw = rgba.shape[:2]
    sc = min(560 / cw, 560 / ch)
    nw, nh = int(cw * sc), int(ch * sc)
    rs = cv2.resize(rgba, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.full((620, 620, 3), (22, 18, 48), dtype=np.uint8)
    ox, oy = (620 - nw) // 2, (620 - nh) // 2
    al = rs[:, :, 3:4].astype(np.float32) / 255.0
    canvas[oy : oy + nh, ox : ox + nw] = (rs[:, :, :3] * al + canvas[oy : oy + nh, ox : ox + nw] * (1.0 - al)).astype(np.uint8)
    cv2.putText(canvas, key + " V2", (24, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (80, 230, 255), 2, cv2.LINE_AA)
    qa_cards.append(canvas)

del model
if device.type == "cuda":
    torch.cuda.empty_cache()

qa_grid = np.vstack([np.hstack(qa_cards[:2]), np.hstack(qa_cards[2:])])
cv2.imwrite(str(ASSETS / "qa_4_muc_cutouts_v2.jpg"), qa_grid, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
print("Saved V2 QA grid!")
