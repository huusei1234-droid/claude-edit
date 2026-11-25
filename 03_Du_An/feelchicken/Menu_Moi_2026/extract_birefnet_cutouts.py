from pathlib import Path
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

ROOT = Path(r"Z:\Máy tính khác\My Computer\feel chicken")
NVA_DIR = ROOT / "Ảnh retouch" / "Ảnh Feel ngũ vị" / "Ngũ vị A"
NV_DIR = ROOT / "Ảnh retouch" / "Ảnh Feel ngũ vị"
MY_DIR = ROOT / "Ảnh retouch" / "Ảnh Feel ngũ vị & Mỳ"
TN_DIR = ROOT / "menu và tài nguyên"
MENU_BACK = ROOT / "MENU FEEL CHICKEN" / "Menu - Việt - sau.png"
DEMO_NEW = ROOT / "demo menu mới.jpg"

OUT_CUT = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\birefnet_cutouts")
OUT_CUT.mkdir(parents=True, exist_ok=True)
SCR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Loading BiRefNet FP16 on:", device)
model = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet", trust_remote_code=True).to(device).eval()
if device.type == "cuda":
    model = model.half()

tf = transforms.Compose([
    transforms.Resize((1024, 1024)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def read_bgr(p: Path) -> np.ndarray:
    im = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        raise RuntimeError(f"Cannot read {p}")
    return im


def polish_food(bgr: np.ndarray, sat: float = 1.10, val: float = 1.03) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * val, 0, 255)
    res = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return cv2.addWeighted(res, 1.12, cv2.GaussianBlur(res, (0, 0), 1.0), -0.12, 0)


def decontaminate_bgr(bgr: np.ndarray, alpha_f: np.ndarray) -> np.ndarray:
    core = (alpha_f > 0.90).astype(np.float32)
    edge = (alpha_f > 0.02) & (alpha_f <= 0.90)
    f = bgr.astype(np.float32)
    num = cv2.GaussianBlur(f * core[..., None], (0, 0), 6.0)
    den = cv2.GaussianBlur(core, (0, 0), 6.0)[..., None]
    clean = np.where(den > 1e-4, num / np.maximum(den, 1e-4), f)
    out = f.copy()
    w = ((0.90 - alpha_f) / 0.88).clip(0.0, 1.0)[..., None] * 0.80
    out[edge] = (f * (1.0 - w) + clean * w)[edge]
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


qa_tiles = []


def birefnet_cut(
    src_bgr: np.ndarray,
    y1: float,
    y2: float,
    x1: float,
    x2: float,
    out_name: str,
    max_dim: int = 900,
    keep_largest_only: bool = True,
    sat: float = 1.08,
):
    H, W = src_bgr.shape[:2]
    crop = src_bgr[int(H * y1) : int(H * y2), int(W * x1) : int(W * x2)].copy()
    # Pad border slightly with median edge color so object close to crop border cleanly segments
    pad = int(max(crop.shape[:2]) * 0.06)
    med = np.median(
        np.concatenate([crop[0, :], crop[-1, :], crop[:, 0], crop[:, -1]], axis=0), axis=0
    ).astype(np.uint8)
    padded = cv2.copyMakeBorder(crop, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=med.tolist())
    ph, pw = padded.shape[:2]

    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
    with torch.inference_mode():
        inp = tf(Image.fromarray(rgb)).unsqueeze(0).to(device)
        if device.type == "cuda":
            inp = inp.half()
        pred = model(inp)[-1].sigmoid().float()
        alpha = F.interpolate(pred, size=(ph, pw), mode="bilinear", align_corners=False)[0, 0].cpu().numpy()

    alpha = alpha[pad : ph - pad, pad : pw - pad]
    a_u8 = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)

    # Keep main central component(s) & remove stray corner crumbs from adjacent plates
    _, bw = cv2.threshold(a_u8, 45, 255, cv2.THRESH_BINARY)
    num_l, labels, stats, centroids = cv2.connectedComponentsWithStats(bw)
    ch, cw = a_u8.shape[:2]
    keep_mask = np.zeros_like(a_u8)
    if num_l > 1:
        if keep_largest_only:
            # Pick component with largest (area * centrality_weight)
            best_l, best_score = 1, -1.0
            for lbl in range(1, num_l):
                area = stats[lbl, cv2.CC_STAT_AREA]
                cx, cy = centroids[lbl]
                dist = np.hypot((cx - cw / 2) / cw, (cy - ch / 2) / ch)
                score = area * max(0.15, 1.0 - dist * 1.1)
                if score > best_score:
                    best_score, best_l = score, lbl
            keep_mask[labels == best_l] = 255
            # Fill internal holes inside the plate!
            cnts, _ = cv2.findContours(keep_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(keep_mask, cnts, -1, 255, thickness=cv2.FILLED)
        else:
            for lbl in range(1, num_l):
                if stats[lbl, cv2.CC_STAT_AREA] > (ch * cw * 0.015):
                    keep_mask[labels == lbl] = 255
        keep_soft = cv2.GaussianBlur(cv2.dilate(keep_mask, np.ones((5, 5), np.uint8), 1), (5, 5), 1.2)
        a_u8 = np.minimum(a_u8, keep_soft)
        # Ensure interior of filled plate has solid 255 alpha (no holes inside cheese/rice!)
        if keep_largest_only:
            er_interior = cv2.erode(keep_mask, np.ones((11, 11), np.uint8), 1)
            a_u8 = np.maximum(a_u8, er_interior)

    # Slight 1px pull-in + smooth anti-aliased edge
    a_u8 = cv2.GaussianBlur(cv2.erode(a_u8, np.ones((3, 3), np.uint8), 1), (3, 3), 0.7)
    ys, xs = np.where(a_u8 > 16)
    y0, y1_b = max(0, ys.min() - 4), min(ch, ys.max() + 5)
    x0, x1_b = max(0, xs.min() - 4), min(cw, xs.max() + 5)

    fg_bgr = polish_food(decontaminate_bgr(crop[y0:y1_b, x0:x1_b], a_u8[y0:y1_b, x0:x1_b] / 255.0), sat=sat)
    fg_a = a_u8[y0:y1_b, x0:x1_b]

    fh, fw = fg_bgr.shape[:2]
    scale = min(1.0, max_dim / float(max(fh, fw)))
    if scale < 1.0 or max(fh, fw) < 360:
        target_s = max_dim / float(max(fh, fw)) if max(fh, fw) > max_dim else min(2.2, 520.0 / float(max(fh, fw)))
        nw, nh = max(1, int(round(fw * target_s))), max(1, int(round(fh * target_s)))
        interp = cv2.INTER_AREA if target_s < 1.0 else cv2.INTER_LANCZOS4
        fg_bgr = cv2.resize(fg_bgr, (nw, nh), interpolation=interp)
        fg_a = cv2.resize(fg_a, (nw, nh), interpolation=interp)

    bgra = np.dstack([fg_bgr, fg_a])
    cv2.imwrite(str(OUT_CUT / out_name), bgra)

    # Render QA tile over warm menu cream (#FAEBCD -> BGR 205, 235, 250)
    tw, th = 280, 220
    tile = np.full((th, tw, 3), (215, 240, 252), dtype=np.uint8)
    s = min((tw - 20) / float(bgra.shape[1]), (th - 38) / float(bgra.shape[0]))
    rw, rh = max(1, int(round(bgra.shape[1] * s))), max(1, int(round(bgra.shape[0] * s)))
    rs = cv2.resize(bgra, (rw, rh), interpolation=cv2.INTER_AREA)
    ox, oy = (tw - rw) // 2, 28 + (th - 32 - rh) // 2
    af = rs[:, :, 3:4].astype(np.float32) / 255.0
    tile[oy : oy + rh, ox : ox + rw] = (rs[:, :, :3] * af + tile[oy : oy + rh, ox : ox + rw] * (1.0 - af)).astype(np.uint8)
    cv2.putText(tile, out_name[:-4], (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (20, 20, 160), 1, cv2.LINE_AA)
    qa_tiles.append(tile)
    print(f"Cutout {out_name}: {bgra.shape}")


# --- 1. SONY A1 & HIGH-RES CHICKEN CUTOUTS ---
# Big crispy chicken platter (6-8 pcs) — Ngũ vị A (1).png (45° golden pile on round plate!)
birefnet_cut(read_bgr(NVA_DIR / "260628 ngũ vị A (1).png"), 0.02, 0.99, 0.02, 0.98, "ga_mam_lon.png", 950, sat=1.04)
# 4-5 Glazed sauces platter — Ngũ vị A  (21).png
birefnet_cut(read_bgr(NVA_DIR / "260628 ngũ vị A  (21).png"), 0.02, 0.99, 0.06, 0.96, "ga_mam_sot.png", 950, sat=1.04)
# 5-Flavor signature drumstick platter on lettuce — Sony A1 A1_08995.JPG
birefnet_cut(read_bgr(MY_DIR / "A1_08995.JPG"), 0.02, 0.98, 0.02, 0.98, "ga_5_nguvi.png", 950)
# Crispy chicken platter w/ veggies (4 pcs) — Ngũ vị A  (20).png
birefnet_cut(read_bgr(NVA_DIR / "260628 ngũ vị A  (20).png"), 0.08, 0.98, 0.04, 0.98, "ga_4_mieng.png", 900, sat=1.04)
# Boneless Chicken Fillet plate — 29d91955...
birefnet_cut(read_bgr(TN_DIR / "29d9195565deeb80b2cf45.jpg"), 0.14, 0.92, 0.06, 0.94, "ga_phile.png", 800)

# Individual Glazed Drumsticks (from 2560px studio shots!)
birefnet_cut(read_bgr(TN_DIR / "55eb71650dee83b0daff28.jpg"), 0.56, 0.95, 0.14, 0.88, "dui_sot_cay.png", 680)
birefnet_cut(read_bgr(TN_DIR / "09c94b4437cfb991e0de26.jpg"), 0.56, 0.96, 0.10, 0.86, "dui_sot_tuong.png", 680)
birefnet_cut(read_bgr(TN_DIR / "24410ac7764cf812a15d27.jpg"), 0.55, 0.95, 0.10, 0.88, "dui_sot_phomai.png", 680)

# --- 2. SONY A1 & STUDIO NOODLES, TOKBOKKI, RICE, SALAD & SNACKS ---
# Cơm Gà plate + Coca + Soup — a8906f12... (beige plate of Rice + Chicken + Veggies)
birefnet_cut(read_bgr(TN_DIR / "a8906f1213999dc7c48846.jpg"), 0.18, 0.96, 0.04, 0.96, "com_ga_dia.png", 820)
# Mì Ý Sốt Thịt Bằm — Sony A1 A1_09061.JPG
birefnet_cut(read_bgr(MY_DIR / "A1_09061.JPG"), 0.06, 0.94, 0.06, 0.94, "mi_y.png", 820)
# Mì Tương Đen — Sony A1 A1_09006.JPG (crop around black noodle plate)
birefnet_cut(read_bgr(MY_DIR / "A1_09006.JPG"), 0.0, 0.90, 0.0, 0.98, "mi_tuong_den.png", 820)
# Mì Cay Hải Sản (Sony A1 Ngũ vị A 17.png — 100% unclipped claypot!)
birefnet_cut(read_bgr(NVA_DIR / "260628 ngũ vị A  (17).png"), 0.04, 0.96, 0.08, 0.86, "mi_cay_haisan.png", 820, sat=1.05)

mb = read_bgr(MENU_BACK)
# Mì Cay Bạch Tuộc & Mì Cay Đùi Gà & Mì Tương Đen Gà Cay (clean unclipped round bowls!)
birefnet_cut(mb, 255 / 1294, 452 / 1294, 1088 / 2000, 1304 / 2000, "mi_cay_bachtuoc.png", 620)
birefnet_cut(mb, 255 / 1294, 452 / 1294, 1540 / 2000, 1756 / 2000, "mi_cay_duiga.png", 620)
birefnet_cut(mb, 486 / 1294, 676 / 1294, 668 / 2000, 864 / 2000, "mi_tuong_den_gacay.png", 620)

# Tokbokki Truyền Thống — Sony A1 A1_09000.JPG (100% unclipped leaf black bowl!)
birefnet_cut(read_bgr(MY_DIR / "A1_09000.JPG"), 0.0, 0.98, 0.06, 0.96, "tokbokki.png", 820)
# Tokbokki Phô Mai — 9a8b1b54...
birefnet_cut(read_bgr(TN_DIR / "9a8b1b5469dfe781bece108.jpg"), 0.02, 0.98, 0.02, 0.98, "tokbokki_phomai.png", 780)
# Salad Trộn Sốt Mè — Sony A1 A1_09001.JPG
birefnet_cut(read_bgr(MY_DIR / "A1_09001.JPG"), 0.02, 0.98, 0.02, 0.98, "salad.png", 800)

# Khoai Tây Chiên đĩa đen — 163847b4...
birefnet_cut(read_bgr(TN_DIR / "163847b43b3fb561ec2e48.jpg"), 0.04, 0.96, 0.02, 0.98, "khoai_tay_dia.png", 760)
# Khoai Tây Chiên rời vàng giòn (for pairing neatly inside combos!) — 09c94b44...
birefnet_cut(read_bgr(TN_DIR / "09c94b4437cfb991e0de26.jpg"), 0.24, 0.65, 0.34, 0.98, "khoai_tay_roi.png", 680)
# Khoai Tây Lắc Phô Mai (hộp) — mb[896:1066, 1585:1720]
birefnet_cut(mb, 892 / 1294, 1068 / 1294, 1582 / 2000, 1722 / 2000, "khoai_tay_hop.png", 580)
# Bánh Gạo Lắc Phô Mai — 42bc8030...
birefnet_cut(read_bgr(TN_DIR / "42bc8030fcbb72e52baa49.jpg"), 0.12, 0.88, 0.02, 0.98, "banh_gao_lac.png", 760)
# Phô Mai Que — e31f4892...
birefnet_cut(read_bgr(TN_DIR / "e31f48923419ba47e30847.jpg"), 0.10, 0.92, 0.06, 0.94, "phomai_que.png", 740)
# Xúc Xích Chiên — demo[735:832, 632:768]
birefnet_cut(read_bgr(DEMO_NEW), 735 / 1024, 832 / 1024, 632 / 1536, 768 / 1536, "xuc_xich.png", 560, keep_largest_only=False)

# Single Red Coca-Cola Can (for building 1, 2, 3, 4 Coca combos cleanly!) & Coca Bottle
birefnet_cut(mb, 1102 / 1294, 1262 / 1294, 690 / 2000, 752 / 2000, "lon_coca.png", 520)
birefnet_cut(read_bgr(TN_DIR / "55eb71650dee83b0daff28.jpg"), 0.04, 0.78, 0.04, 0.36, "chai_coca.png", 620)

# Save QA contact sheet
cols = 6
rows = (len(qa_tiles) + cols - 1) // cols
while len(qa_tiles) < rows * cols:
    qa_tiles.append(np.full_like(qa_tiles[0], 245))
grid = np.vstack([np.hstack(qa_tiles[r * cols : (r + 1) * cols]) for r in range(rows)])
cv2.imwrite(str(SCR / "birefnet_cutouts_qa.jpg"), grid, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
print(f"DONE! Extracted {len( list(OUT_CUT.glob('*.png')) )} BiRefNet FP16 studio cutouts!")
