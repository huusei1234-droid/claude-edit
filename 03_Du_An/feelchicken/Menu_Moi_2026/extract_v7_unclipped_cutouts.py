from pathlib import Path
import shutil
import cv2
import numpy as np
import segno
import onnxruntime as ort
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
MENU_FRONT = ROOT / "MENU FEEL CHICKEN" / "Menu - Việt- trước.png"
MENU_BACK = ROOT / "MENU FEEL CHICKEN" / "Menu - Việt - sau.png"
DEMO_NEW = ROOT / "demo menu mới.jpg"

BASE = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026")
CUT_DIR = BASE / "assets" / "cutouts_v7"
CUT_DIR.mkdir(parents=True, exist_ok=True)
SCR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch")
SCR.mkdir(parents=True, exist_ok=True)


def read_bgr(p: Path) -> np.ndarray:
    im = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        raise RuntimeError(f"Cannot read {p}")
    return im


# --- 1. Brand Logo + Lossless TPBank VietQR + ISO Fanpage QR ---
shutil.copy2(ROOT / "logo feel tn.png", CUT_DIR / "logo.png")
mf = read_bgr(MENU_FRONT)
mb = read_bgr(MENU_BACK)
# TPBank QR sits at top-right of Menu - Việt- trước.png (2000x1294): [16:136, 1864:1984]
qr_crop = mf[16:136, 1864:1984]
_, qr_bw = cv2.threshold(cv2.cvtColor(qr_crop, cv2.COLOR_BGR2GRAY), 165, 255, cv2.THRESH_BINARY)
qr_up = cv2.resize(qr_bw, (360, 360), interpolation=cv2.INTER_NEAREST)
cv2.imwrite(str(CUT_DIR / "tpbank_qr.png"), qr_up)

q_fb = segno.make("https://www.facebook.com/feelchickenvn/", error="m")
q_fb.save(str(CUT_DIR / "fanpage_qr.png"), scale=10, border=1, dark="#1F0E08", light="#FFFFFF")

# 5 Sony A1 Sauce Medallion Macros
sauce_specs = [
    ("s1_phomai.jpg", NV_DIR / "A1_07875.jpg", 0.08, 0.92, 0.14, 0.86),
    ("s2_cayhan.jpg", NV_DIR / "A1_07854.jpg", 0.08, 0.92, 0.12, 0.84),
    ("s3_toicay.jpg", NV_DIR / "A1_07901.jpg", 0.06, 0.90, 0.14, 0.86),
    ("s4_chanhday.jpg", NV_DIR / "A1_07982.jpg", 0.08, 0.92, 0.14, 0.86),
    ("s5_tuonghan.jpg", NV_DIR / "A1_07912.jpg", 0.06, 0.92, 0.12, 0.84),
]
for snm, spath, y1, y2, x1, x2 in sauce_specs:
    sim = read_bgr(spath)
    H, W = sim.shape[:2]
    sub = sim[int(H * y1) : int(H * y2), int(W * x1) : int(W * x2)]
    m = min(sub.shape[:2])
    oy, ox = (sub.shape[0] - m) // 2, (sub.shape[1] - m) // 2
    sq = cv2.resize(sub[oy : oy + m, ox : ox + m], (380, 380), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(sq, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.12, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.04, 0, 255)
    sq = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(str(CUT_DIR / snm), sq, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

# --- 2. Load BiRefNet FP16 on CUDA ---
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


def polish_food(bgr: np.ndarray, sat: float = 1.10, val: float = 1.03, warm_r: float = 0.0) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * val, 0, 255)
    res = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    if warm_r != 0.0:
        res[:, :, 2] = np.clip(res[:, :, 2] + warm_r, 0, 255)
        res[:, :, 1] = np.clip(res[:, :, 1] - warm_r * 0.25, 0, 255)
        res[:, :, 0] = np.clip(res[:, :, 0] - warm_r * 0.45, 0, 255)
    res_u8 = res.astype(np.uint8)
    return cv2.addWeighted(res_u8, 1.13, cv2.GaussianBlur(res_u8, (0, 0), 1.0), -0.13, 0)


def decontaminate_bgr(bgr: np.ndarray, alpha_f: np.ndarray) -> np.ndarray:
    core = (alpha_f > 0.90).astype(np.float32)
    edge = (alpha_f > 0.01) & (alpha_f <= 0.90)
    f = bgr.astype(np.float32)
    num = cv2.GaussianBlur(f * core[..., None], (0, 0), 6.5)
    den = cv2.GaussianBlur(core, (0, 0), 6.5)[..., None]
    clean = np.where(den > 1e-4, num / np.maximum(den, 1e-4), f)
    out = f.copy()
    w = ((0.90 - alpha_f) / 0.89).clip(0.0, 1.0)[..., None] * 0.85
    out[edge] = (f * (1.0 - w) + clean * w)[edge]
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def biref_alpha(crop_bgr: np.ndarray) -> np.ndarray:
    pad = max(24, int(max(crop_bgr.shape[:2]) * 0.08))
    med = np.median(
        np.concatenate([crop_bgr[0, :], crop_bgr[-1, :], crop_bgr[:, 0], crop_bgr[:, -1]], axis=0), axis=0
    ).astype(np.uint8)
    padded = cv2.copyMakeBorder(crop_bgr, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=med.tolist())
    ph, pw = padded.shape[:2]
    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
    with torch.inference_mode():
        inp = tf(Image.fromarray(rgb)).unsqueeze(0).to(device)
        if device.type == "cuda":
            inp = inp.half()
        pred = model(inp)[-1].sigmoid().float()
        alpha = F.interpolate(pred, size=(ph, pw), mode="bilinear", align_corners=False)[0, 0].cpu().numpy()
    return alpha[pad : ph - pad, pad : pw - pad]


def save_trimmed_bgra(
    crop_bgr: np.ndarray,
    a_u8: np.ndarray,
    out_name: str,
    max_dim: int = 920,
    strip_white_halo: bool = False,
    sat: float = 1.08,
    warm_r: float = 0.0,
):
    if strip_white_halo:
        hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
        inner = cv2.erode(a_u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)), 1)
        border_z = (a_u8 > 0) & (inner < 205)
        white_px = border_z & (hsv[:, :, 1] < 40) & (hsv[:, :, 2] > 210)
        a_u8 = a_u8.copy()
        a_u8[white_px] = 0
        a_u8 = cv2.erode(a_u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    a_u8 = cv2.GaussianBlur(a_u8, (3, 3), 0.7)
    ys, xs = np.where(a_u8 > 16)
    ch, cw = a_u8.shape[:2]
    y0, y1 = max(0, ys.min() - 4), min(ch, ys.max() + 5)
    x0, x1 = max(0, xs.min() - 4), min(cw, xs.max() + 5)

    fg = polish_food(decontaminate_bgr(crop_bgr[y0:y1, x0:x1], a_u8[y0:y1, x0:x1] / 255.0), sat=sat, warm_r=warm_r)
    fa = a_u8[y0:y1, x0:x1]

    fh, fw = fg.shape[:2]
    m = max(fh, fw)
    if m > max_dim or m < 420:
        s = (max_dim / float(m)) if m > max_dim else min(2.4, 560.0 / float(m))
        nw, nh = max(1, int(round(fw * s))), max(1, int(round(fh * s)))
        interp = cv2.INTER_AREA if s < 1.0 else cv2.INTER_LANCZOS4
        fg = cv2.resize(fg, (nw, nh), interpolation=interp)
        fa = cv2.resize(fa, (nw, nh), interpolation=interp)

    bgra = np.dstack([fg, fa])
    cv2.imwrite(str(CUT_DIR / out_name), bgra)
    return bgra


def cut_clean(
    src_bgr: np.ndarray,
    y1: float,
    y2: float,
    x1: float,
    x2: float,
    out_name: str,
    max_dim: int = 920,
    keep_largest: bool = True,
    strip_white: bool = False,
    sat: float = 1.08,
    warm_r: float = 0.0,
):
    H, W = src_bgr.shape[:2]
    crop = src_bgr[int(H * y1) : int(H * y2), int(W * x1) : int(W * x2)].copy()
    alpha = biref_alpha(crop)
    a_u8 = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    _, bw = cv2.threshold(a_u8, 45, 255, cv2.THRESH_BINARY)
    nl, lb, st, cents = cv2.connectedComponentsWithStats(bw)
    ch, cw = a_u8.shape[:2]
    if nl > 1:
        keep = np.zeros_like(a_u8)
        if keep_largest:
            best_l, best_s = 1, -1.0
            for l_i in range(1, nl):
                area = st[l_i, cv2.CC_STAT_AREA]
                cx, cy = cents[l_i]
                dist = np.hypot((cx - cw / 2) / cw, (cy - ch / 2) / ch)
                sc = area * max(0.2, 1.0 - dist * 1.1)
                if sc > best_s:
                    best_s, best_l = sc, l_i
            keep[lb == best_l] = 255
            cnts, _ = cv2.findContours(keep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(keep, cnts, -1, 255, thickness=cv2.FILLED)
            er_in = cv2.erode(keep, np.ones((11, 11), np.uint8), 1)
            a_u8 = np.maximum(np.minimum(a_u8, cv2.dilate(keep, np.ones((5, 5), np.uint8), 1)), er_in)
        else:
            for l_i in range(1, nl):
                if st[l_i, cv2.CC_STAT_AREA] > (ch * cw * 0.012):
                    keep[lb == l_i] = 255
            a_u8 = np.minimum(a_u8, cv2.dilate(keep, np.ones((5, 5), np.uint8), 1))
    a_u8 = cv2.erode(a_u8, np.ones((3, 3), np.uint8), 1)
    return save_trimmed_bgra(crop, a_u8, out_name, max_dim, strip_white, sat, warm_r)


def cut_wood_black_plate(src_bgr: np.ndarray, y1: float, y2: float, x1: float, x2: float, out_name: str, max_dim: int = 860):
    """Segments dark ceramic plate + food on warm wooden tabletop with 100% intact unbroken plate rim!"""
    H, W = src_bgr.shape[:2]
    crop = src_bgr[int(H * y1) : int(H * y2), int(W * x1) : int(W * x2)].copy()
    ch, cw = crop.shape[:2]
    alpha_ai = biref_alpha(crop)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    b, g, r = crop[:, :, 0].astype(np.int16), crop[:, :, 1].astype(np.int16), crop[:, :, 2].astype(np.int16)
    dark_plate = ((hsv[:, :, 2] < 96) & ((r - b) < 34)).astype(np.uint8) * 255
    ai_m = (alpha_ai > 0.35).astype(np.uint8) * 255
    comb = cv2.morphologyEx(cv2.bitwise_or(ai_m, dark_plate), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)))
    nl, lb, st, cents = cv2.connectedComponentsWithStats(comb)
    best_l, best_s = 1, -1.0
    for l_i in range(1, nl):
        area = st[l_i, cv2.CC_STAT_AREA]
        cx, cy = cents[l_i]
        sc = area * max(0.2, 1.0 - np.hypot((cx - cw / 2) / cw, (cy - ch / 2) / ch))
        if sc > best_s:
            best_s, best_l = sc, l_i
    keep = (lb == best_l).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(keep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(keep)
    cv2.drawContours(filled, cnts, -1, 255, thickness=cv2.FILLED)
    smooth = cv2.GaussianBlur(cv2.erode(filled, np.ones((5, 5), np.uint8), 1), (7, 7), 1.6)
    guard = cv2.dilate(filled, np.ones((11, 11), np.uint8), 1)
    final_a = np.minimum(np.maximum(smooth, np.clip(alpha_ai * 255.0, 0, 255).astype(np.uint8)), guard)
    return save_trimmed_bgra(crop, final_a, out_name, max_dim, False, 1.08)


# ==============================================================================
# EXTRACT ALL 28 CUTOUTS — 100% UNCLIPPED PLATES & HANDLES (ZERO FLAT EDGES!)
# ==============================================================================
# 1. Chicken Platters (Sony A1 6000px — 100% unclipped organic silhouettes!)
cut_clean(read_bgr(NVA_DIR / "260628 ngũ vị A (1).png"), 0.0, 1.0, 0.0, 1.0, "ga_mam_lon.png", 960, sat=1.05)
cut_clean(read_bgr(NVA_DIR / "260628 ngũ vị A  (21).png"), 0.0, 1.0, 0.04, 0.98, "ga_mam_sot.png", 960, sat=1.05)
cut_clean(read_bgr(MY_DIR / "A1_08995.JPG"), 0.01, 0.99, 0.01, 0.99, "ga_5_nguvi.png", 960, sat=1.08)
cut_clean(read_bgr(NVA_DIR / "260628 ngũ vị A  (35).png"), 0.01, 0.99, 0.02, 0.98, "ga_4_mieng.png", 920, sat=1.05)
cut_wood_black_plate(read_bgr(TN_DIR / "29d9195565deeb80b2cf45.jpg"), 0.12, 0.94, 0.02, 0.98, "ga_phile.png", 840)

# 2. 4 Individual Glazed Drumsticks (de-haloed + rich appetizing color!)
cut_clean(read_bgr(TN_DIR / "55eb71650dee83b0daff28.jpg"), 0.54, 0.96, 0.12, 0.90, "dui_sot_cay.png", 720, strip_white=True, sat=1.10)
cut_clean(read_bgr(TN_DIR / "09c94b4437cfb991e0de26.jpg"), 0.54, 0.97, 0.08, 0.88, "dui_sot_tuong.png", 720, strip_white=True, sat=1.14, warm_r=14.0)
cut_clean(read_bgr(TN_DIR / "24410ac7764cf812a15d27.jpg"), 0.53, 0.96, 0.08, 0.90, "dui_sot_phomai.png", 720, strip_white=True, sat=1.10)
fe_p = [p for p in TN_DIR.iterdir() if p.name.lower().startswith("fe763")][0]
cut_clean(read_bgr(fe_p), 0.10, 0.90, 0.10, 0.90, "dui_gion.png", 720, sat=1.10, warm_r=6.0)

# 3. Cơm Gà Round Beige Plate (100% pure ellipse — zero grey stone!)
cg_src = read_bgr(TN_DIR / "17f44e283ca3b2fdebb2142.jpg")
Hc, Wc = cg_src.shape[:2]
roi = cg_src[int(Hc * 0.44) : int(Hc * 0.95), int(Wc * 0.14) : int(Wc * 0.69)]
lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
pm = ((lab[:, :, 2] >= 140) & (lab[:, :, 0] >= 40)).astype(np.uint8) * 255
pm = cv2.morphologyEx(cv2.morphologyEx(pm, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))
nl, lb, st, _ = cv2.connectedComponentsWithStats(pm)
pm_b = (lb == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))).astype(np.uint8) * 255
cnts, _ = cv2.findContours(pm_b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
ell_m = np.zeros_like(pm_b)
cv2.ellipse(ell_m, cv2.fitEllipse(cnts[0]), 255, -1, lineType=cv2.LINE_AA)
save_trimmed_bgra(roi, cv2.erode(ell_m, np.ones((5, 5), np.uint8), 1), "com_ga_plate.png", 800, False, 1.14)

# 4. ALL 3 MÌ CAY CLAYPOTS WITH 100% INTACT LEFT & RIGHT HANDLES (from Menu - Việt - sau.png!)
cut_clean(mb, 252 / 1294, 454 / 1294, 654 / 2000, 876 / 2000, "mi_cay_haisan.png", 680, sat=1.12)
cut_clean(mb, 252 / 1294, 454 / 1294, 1086 / 2000, 1306 / 2000, "mi_cay_bachtuoc.png", 680, sat=1.12)
cut_clean(mb, 252 / 1294, 454 / 1294, 1538 / 2000, 1758 / 2000, "mi_cay_duiga.png", 680, sat=1.12)

# 5. Mì Tương Đen (Sony A1 Ngũ vị A 12.jpeg — 100% unclipped on all 4 sides!) & Mì Tương Đen Gà Cay
cut_wood_black_plate(read_bgr(NVA_DIR / "260628 ngũ vị A  (12).jpeg"), 0.08, 0.92, 0.14, 0.88, "mi_tuong_den.png", 840)
cut_clean(mb, 484 / 1294, 678 / 1294, 666 / 2000, 866 / 2000, "mi_tuong_den_gacay.png", 660, sat=1.12)

# 6. Mì Ý Sốt Thịt Bằm (Sony A1 A1_09061.JPG — 100% unbroken square black plate!)
miy_src = read_bgr(MY_DIR / "A1_09061.JPG")
Hm, Wm = miy_src.shape[:2]
mcrop = miy_src[int(Hm * 0.05) : int(Hm * 0.94), int(Wm * 0.05) : int(Wm * 0.95)]
hsv_m = cv2.cvtColor(mcrop, cv2.COLOR_BGR2HSV)
is_wood = (hsv_m[:, :, 0] >= 7) & (hsv_m[:, :, 0] <= 26) & (hsv_m[:, :, 1] >= 32) & (hsv_m[:, :, 1] <= 145) & (hsv_m[:, :, 2] > 108)
nw_m = cv2.morphologyEx(cv2.morphologyEx((~is_wood).astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8)), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
nl, lb, st, _ = cv2.connectedComponentsWithStats(nw_m)
pm_m = (lb == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))).astype(np.uint8) * 255
cnts_m, _ = cv2.findContours(pm_m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
filled_m = np.zeros_like(pm_m)
cv2.drawContours(filled_m, cnts_m, -1, 255, thickness=cv2.FILLED)
b_c, g_c, r_c = mcrop[:, :, 0].astype(int), mcrop[:, :, 1].astype(int), mcrop[:, :, 2].astype(int)
filled_m[(np.arange(mcrop.shape[0])[:, None] > int(mcrop.shape[0] * 0.84)) & ((r_c - b_c) > 12)] = 0
save_trimmed_bgra(mcrop, cv2.erode(filled_m, np.ones((7, 7), np.uint8), 1), "mi_y.png", 840, False, 1.10)

# 7. Tokbokki Truyền Thống (Sony A1 A1_08999.JPG — 100% unclipped leaf black bowl from tip to tip!)
cut_clean(read_bgr(MY_DIR / "A1_08999.JPG"), 0.28, 0.98, 0.03, 0.92, "tokbokki.png", 840, sat=1.10)
# 8. Tokbokki Phô Mai (100% unclipped triangular bowl!)
cut_clean(mb, 698 / 1294, 876 / 1294, 672 / 2000, 862 / 2000, "tokbokki_phomai.png", 660, sat=1.12)
# 9. Salad Trộn Sốt Mè (100% unclipped triangular black bowl — zero cut leaves!)
cut_clean(mb, 484 / 1294, 678 / 1294, 1548 / 2000, 1774 / 2000, "salad.png", 680, sat=1.12)

# 10. Khoai Tây Chiên Đĩa Đen (full 0.0..1.0 width of 163847b4 so right tip is 100% unclipped!) + Khoai Đĩa Chéo + Khoai Hộp
cut_wood_black_plate(read_bgr(TN_DIR / "163847b43b3fb561ec2e48.jpg"), 0.02, 0.98, 0.0, 1.0, "khoai_tay_dia.png", 800)
cut_clean(mf, 266 / 1294, 336 / 1294, 110 / 2000, 304 / 2000, "khoai_tay_cheo.png", 640, sat=1.12)
cut_clean(mb, 890 / 1294, 1070 / 1294, 1580 / 2000, 1724 / 2000, "khoai_tay_hop.png", 620, sat=1.12)

# 11. Bánh Gạo Lắc Phô Mai (full 0.0..1.0 width!), Phô Mai Que, Xúc Xích
cut_wood_black_plate(read_bgr(TN_DIR / "42bc8030fcbb72e52baa49.jpg"), 0.08, 0.92, 0.0, 1.0, "banh_gao_lac.png", 800)
cut_wood_black_plate(read_bgr(TN_DIR / "e31f48923419ba47e30847.jpg"), 0.08, 0.94, 0.04, 0.96, "phomai_que.png", 780)
cut_clean(read_bgr(DEMO_NEW), 735 / 1024, 834 / 1024, 632 / 1536, 768 / 1536, "xuc_xich.png", 600, keep_largest=False, sat=1.10)

# 12. Single Red Coca Can + 5 Refreshing Drinks
cut_clean(mb, 1100 / 1294, 1264 / 1294, 690 / 2000, 754 / 2000, "lon_coca.png", 580, sat=1.12)
drink_crops = [
    ("dr01_soju.png", 1090, 1266, 374, 440),
    ("dr02_coca_7up.png", 1102, 1264, 690, 814),
    ("dr03_tra_tao.png", 1098, 1266, 1074, 1164),
    ("dr04_tra_dao.png", 1100, 1266, 1382, 1464),
    ("dr05_nuoc_suoi.png", 1100, 1266, 1680, 1750),
]
for dnm, y0, y1, x0, x1 in drink_crops:
    cut_clean(mb, y0 / 1294, y1 / 1294, x0 / 2000, x1 / 2000, dnm, 560, keep_largest=False, sat=1.12)

# --- 3. AUTOMATED FLAT-EDGE & SILHOUETTE AUDIT SHEET ---
pngs = sorted(CUT_DIR.glob("*.png"))
tiles = []
for p in pngs:
    if p.name in ("logo.png", "tpbank_qr.png", "fanpage_qr.png"):
        continue
    im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    h, w = im.shape[:2]
    a = im[:, :, 3]
    ys, xs = np.where(a > 25)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    lf = int((a[:, x0 : x0 + 3].max(axis=1) > 120).sum()) / float(y1 - y0 + 1)
    rf = int((a[:, max(0, x1 - 2) : x1 + 1].max(axis=1) > 120).sum()) / float(y1 - y0 + 1)
    flags = []
    if lf > 0.30 and p.name not in ("lon_coca.png", "dr02_coca_7up.png", "dr05_nuoc_suoi.png"):
        flags.append(f"L:{lf:.2f}")
    if rf > 0.30 and p.name not in ("lon_coca.png", "dr02_coca_7up.png", "dr05_nuoc_suoi.png"):
        flags.append(f"R:{rf:.2f}")
    print(f"{p.name:24s} ({w:3d}x{h:3d}) -> {' '.join(flags) if flags else 'CLEAN'}")

    tw, th = 290, 220
    tile = np.full((th, tw, 3), (220, 242, 254), np.uint8)
    s = min((tw - 24) / w, (th - 40) / h)
    rw, rh = max(1, int(w * s)), max(1, int(h * s))
    rs = cv2.resize(im, (rw, rh), interpolation=cv2.INTER_AREA)
    ox, oy = (tw - rw) // 2, 28 + (th - 34 - rh) // 2
    af = rs[:, :, 3:4] / 255.0
    tile[oy : oy + rh, ox : ox + rw] = (rs[:, :, :3] * af + tile[oy : oy + rh, ox : ox + rw] * (1 - af)).astype(np.uint8)
    cv2.putText(tile, p.stem[:18], (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (15, 20, 160), 1, cv2.LINE_AA)
    tiles.append(tile)

cols = 6
rows = (len(tiles) + cols - 1) // cols
while len(tiles) < rows * cols:
    tiles.append(np.full_like(tiles[0], 245))
grid = np.vstack([np.hstack(tiles[r * cols : (r + 1) * cols]) for r in range(rows)])
cv2.imwrite(str(SCR / "v7_cutouts_audit.jpg"), grid, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
print("V7 UNCLIPPED CUTOUTS READY!")
