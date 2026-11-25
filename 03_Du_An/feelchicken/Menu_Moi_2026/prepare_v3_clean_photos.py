from pathlib import Path
import cv2
import numpy as np
import onnxruntime as ort

TN_DIR = Path(r"Z:\Máy tính khác\My Computer\feel chicken\menu và tài nguyên")
RET_NV = Path(r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Ảnh Feel ngũ vị")
RET_MY = Path(r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Ảnh Feel ngũ vị & Mỳ")
MENU_OLD_BACK = Path(r"Z:\Máy tính khác\My Computer\feel chicken\MENU FEEL CHICKEN\Menu - Việt - sau.png")
DEMO_NEW = Path(r"Z:\Máy tính khác\My Computer\feel chicken\demo menu mới.jpg")

OUT_PHOTOS = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\photos_v3")
OUT_PHOTOS.mkdir(parents=True, exist_ok=True)
SCRATCH = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch")


def find_tn(substr: str) -> Path:
    matches = [p for p in TN_DIR.iterdir() if p.is_file() and substr.lower() in p.name.lower()]
    if not matches:
        raise FileNotFoundError(f"No file matching '{substr}' in {TN_DIR}")
    return sorted(matches)[0]


def read_img(p: Path) -> np.ndarray:
    im = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        raise RuntimeError(f"Failed to read {p}")
    return im


def studio_food_grade(bgr: np.ndarray, sat: float = 1.15, val: float = 1.05, warm: float = 4.5) -> np.ndarray:
    f = np.power(np.clip(bgr.astype(np.float32) / 255.0, 0.0, 1.0), 0.91)
    hsv = cv2.cvtColor((f * 255.0).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * val + 2.0, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    out[:, :, 2] = np.clip(out[:, :, 2] + warm, 0, 255)
    out[:, :, 1] = np.clip(out[:, :, 1] + warm * 0.35, 0, 255)
    out[:, :, 0] = np.clip(out[:, :, 0] - warm * 0.25, 0, 255)
    res = out.astype(np.uint8)
    return cv2.addWeighted(res, 1.15, cv2.GaussianBlur(res, (0, 0), 1.1), -0.15, 0)


saved_dishes = []


def save_crop(
    src_path: Path,
    y1: float,
    y2: float,
    x1: float,
    x2: float,
    out_name: str,
    w_out: int = 640,
    h_out: int = 440,
    sat: float = 1.15,
):
    im = read_img(src_path)
    H, W = im.shape[:2]
    cy0, cy1 = int(round(H * y1)), int(round(H * y2))
    cx0, cx1 = int(round(W * x1)), int(round(W * x2))
    sub = im[cy0:cy1, cx0:cx1]
    sh, sw = sub.shape[:2]
    target_ar = w_out / float(h_out)
    cur_ar = sw / float(sh)
    if cur_ar > target_ar:
        new_w = int(round(sh * target_ar))
        ox = (sw - new_w) // 2
        sub = sub[:, ox : ox + new_w]
    else:
        new_h = int(round(sw / target_ar))
        oy = (sh - new_h) // 2
        sub = sub[oy : oy + new_h, :]
    interp = cv2.INTER_AREA if sub.shape[1] >= w_out else cv2.INTER_CUBIC
    rs = cv2.resize(sub, (w_out, h_out), interpolation=interp)
    rs = studio_food_grade(rs, sat=sat)
    cv2.imwrite(str(OUT_PHOTOS / out_name), rs, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    saved_dishes.append((out_name, rs))
    return rs


# ==============================================================================
# 1. FRONT PAGE: 11 COMBOS (100% REAL HIGH-RES STUDIO PHOTOS — ZERO COLLAGE!)
# ==============================================================================
# 00. Cơm Gà Feel Chicken (45K) — Cơm gà + Salad + Canh + Coca (cropped clean of corner logo)
save_crop(find_tn("17f44e28"), 0.20, 0.96, 0.18, 0.92, "c00_com_ga.jpg")
# 01. Feel Solo (59K - 1 đùi gà + KTC + Coca) — crop below top-left mini logo (y>0.20, x>0.18)
save_crop(find_tn("3f6551b9"), 0.20, 0.96, 0.20, 0.96, "c01_feel_solo.jpg")
# 02. Feel Chicken Meal (79K - 1 đùi gà + Mì tương đen + Coca) — Sony A1 tabletop (zero hands!)
save_crop(RET_NV / "260628 Ngũ vị (24).jpg", 0.04, 0.96, 0.06, 0.96, "c02_chicken_meal.jpg")
# 03. Feel Spicy (89K - 1 đùi gà + Mì cay + Coca) — Sony A1 tabletop claypot + chicken (zero hands!)
save_crop(RET_NV / "260628 Ngũ vị (23).jpg", 0.04, 0.96, 0.02, 0.96, "c03_feel_spicy.jpg")
# 04. Feel Cheese (89K - 1 đùi gà + Bánh gạo lắc phô mai + Coca) — rich golden cheese chicken
save_crop(find_tn("b35ee678"), 0.08, 0.95, 0.06, 0.96, "c04_feel_cheese.jpg")

# 05. Feel Love (129K - 2 đùi gà + Tokbokki + Salad) — Sony A1 tabletop
save_crop(RET_MY / "A1_08999.JPG", 0.02, 0.98, 0.06, 0.98, "c05_feel_love.jpg")
# 06. Feel Couple (139K - 2 đùi gà + Mì tương đen) — Sony A1 tabletop
save_crop(RET_MY / "A1_09006.JPG", 0.02, 0.98, 0.02, 0.98, "c06_feel_couple.jpg")
# 07. Feel Party (179K - 4 miếng gà + Khoai tây + Tokbokki + 2 Coca) — Sony A1 tabletop
save_crop(RET_MY / "A1_09008.JPG", 0.02, 0.98, 0.02, 0.98, "c07_feel_party.jpg")

# 08. Feel Friends (249K - 6 miếng gà + Tokbokki + KTC + Salad + 3 Coca) — Sony A1 tabletop feast
save_crop(RET_MY / "A1_08956.JPG", 0.02, 0.98, 0.02, 0.98, "c08_feel_friends.jpg")
# 09. Combo Ngũ Vị (259K - 5 đùi gà đủ 5 sốt + KTC + 1 món kèm) — Sony A1 signature 5-sauce platter
save_crop(RET_MY / "A1_08995.JPG", 0.04, 0.96, 0.05, 0.96, "c09_combo_nguvi.jpg")
# 10. Feel Family (329K - 8 miếng gà + Tokbokki + KTC + Salad + 4 Coca) — Grand family table spread
save_crop(find_tn("3b3300cc"), 0.08, 0.95, 0.05, 0.95, "c10_feel_family.jpg")

# ==============================================================================
# 2. BACK PAGE: GÀ LẺ & MỲ Ý (3) + 10 FAST FOOD DISHES + 4 SIDES
# ==============================================================================
save_crop(find_tn("29d91955"), 0.18, 0.90, 0.08, 0.92, "b01_ga_phile.jpg", 520, 360)
save_crop(RET_NV / "260628 Ngũ vị (2).jpg", 0.06, 0.94, 0.06, 0.94, "b02_dui_canh.jpg", 520, 360)
save_crop(RET_MY / "A1_09056.JPG", 0.04, 0.96, 0.04, 0.96, "b03_combo_my_y.jpg", 520, 360)

# 10 Fast Food Dishes:
save_crop(find_tn("7bca2419"), 0.06, 0.94, 0.04, 0.96, "d01_micay_haisan.jpg", 540, 380)
save_crop(find_tn("d0b48d68"), 0.06, 0.94, 0.04, 0.96, "d02_micay_bachtuoc.jpg", 540, 380)
save_crop(find_tn("c43a30e6"), 0.06, 0.94, 0.04, 0.96, "d03_micay_duiga.jpg", 540, 380)
save_crop(find_tn("0bbd7869"), 0.14, 0.94, 0.06, 0.94, "d04_mituongden.jpg", 540, 380)
save_crop(RET_NV / "260628 Ngũ vị (25).jpg", 0.06, 0.96, 0.06, 0.96, "d05_mituongden_gacay.jpg", 540, 380)
save_crop(RET_MY / "A1_09061.JPG", 0.08, 0.92, 0.08, 0.92, "d06_mi_y.jpg", 540, 380)
save_crop(RET_MY / "A1_09000.JPG", 0.04, 0.96, 0.06, 0.96, "d07_tokbokki.jpg", 540, 380)
save_crop(find_tn("9a8b1b54"), 0.06, 0.94, 0.04, 0.96, "d08_tokbokki_phomai.jpg", 540, 380)
save_crop(RET_MY / "A1_09001.JPG", 0.06, 0.94, 0.04, 0.96, "d09_salad.jpg", 540, 380)
save_crop(find_tn("42bc8030"), 0.14, 0.88, 0.04, 0.96, "d10_banh_gao_lac.jpg", 540, 380)

# 4 Sides / Món Thêm:
save_crop(find_tn("163847b4"), 0.08, 0.92, 0.06, 0.94, "s01_khoai_chien.jpg", 460, 320)
save_crop(find_tn("89b4a132"), 0.05, 0.95, 0.05, 0.95, "s02_khoai_lac.jpg", 460, 320)
save_crop(find_tn("e31f4892"), 0.14, 0.90, 0.08, 0.92, "s03_phomai_que.jpg", 460, 320)
# Real Feel Chicken scored fried sausages from 2560x2560 studio photo c224faaa...
save_crop(find_tn("c224faaa"), 0.34, 0.67, 0.18, 0.56, "s04_xuc_xich.jpg", 460, 320, sat=1.12)

# ==============================================================================
# 3. 5 DRINKS EXTRACTED VIA IS-NET 1024px WITH ZERO PAPER HALO
# ==============================================================================
model_path = Path.home() / ".u2net" / "isnet-general-use.onnx"
sess = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
in_name = sess.get_inputs()[0].name


def isnet_cutout_drink(bgr_crop: np.ndarray, out_png: str) -> np.ndarray:
    # Pad generously with border median color so bottle cap/bottom never touches 1024 edge
    pad = 40
    med = np.median(
        np.concatenate([bgr_crop[0, :], bgr_crop[-1, :], bgr_crop[:, 0], bgr_crop[:, -1]], axis=0),
        axis=0,
    ).astype(np.uint8)
    padded = cv2.copyMakeBorder(bgr_crop, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=med.tolist())
    ph, pw = padded.shape[:2]

    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    inp = cv2.resize(rgb, (1024, 1024), interpolation=cv2.INTER_LINEAR)
    inp = (inp - 0.5) / 1.0
    inp = np.transpose(inp, (2, 0, 1))[None, ...].astype(np.float32)
    pred = sess.run(None, {in_name: inp})[0][0, 0]
    pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
    alpha = cv2.resize(pred, (pw, ph), interpolation=cv2.INTER_CUBIC)
    alpha = alpha[pad : ph - pad, pad : pw - pad]

    # Clean soft edge pull-in by 1px to eliminate any paper halo
    a_u8 = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    _, hard = cv2.threshold(a_u8, 30, 255, cv2.THRESH_BINARY)
    num_l, labels, stats, _ = cv2.connectedComponentsWithStats(hard)
    keep = np.zeros_like(a_u8)
    for lbl in range(1, num_l):
        if stats[lbl, cv2.CC_STAT_AREA] > 180:
            keep[labels == lbl] = 255
    a_u8 = cv2.bitwise_and(a_u8, keep)
    eroded = cv2.erode(a_u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
    smooth_a = cv2.GaussianBlur(eroded, (3, 3), 0.7)

    fg = studio_food_grade(bgr_crop, sat=1.16, val=1.04, warm=2.0)
    ys, xs = np.where(smooth_a > 18)
    y0, y1 = max(0, ys.min() - 4), min(fg.shape[0], ys.max() + 5)
    x0, x1 = max(0, xs.min() - 4), min(fg.shape[1], xs.max() + 5)
    fg = fg[y0:y1, x0:x1]
    smooth_a = smooth_a[y0:y1, x0:x1]

    # Upscale 2x cleanly for 3000px print sharpness
    th = 420
    tw = max(1, int(round(fg.shape[1] * (th / float(fg.shape[0])))))
    fg_up = cv2.resize(fg, (tw, th), interpolation=cv2.INTER_LANCZOS4)
    a_up = cv2.resize(smooth_a, (tw, th), interpolation=cv2.INTER_LANCZOS4)
    bgra = np.dstack([fg_up, a_up])
    cv2.imwrite(str(OUT_PHOTOS / out_png), bgra)
    return bgra


mb = read_img(MENU_OLD_BACK)
drink_specs = [
    ("dr01_soju.png", mb[1092:1264, 376:438]),
    ("dr02_coca_7up.png", mb[1106:1260, 692:812]),
    ("dr03_tra_tao.png", mb[1102:1264, 1076:1162]),
    ("dr04_tra_dao.png", mb[1104:1264, 1384:1462]),
    ("dr05_nuoc_suoi.png", mb[1104:1264, 1682:1748]),
]
drink_previews = []
for dname, dcrop in drink_specs:
    bgra = isnet_cutout_drink(dcrop, dname)
    bh, bw = bgra.shape[:2]
    cw_d = max(320, bw + 40)
    cream = np.full((460, cw_d, 3), (247, 253, 255), dtype=np.uint8)
    ox = (cw_d - bw) // 2
    oy = (460 - bh) // 2
    a = bgra[:, :, 3:4].astype(np.float32) / 255.0
    cream[oy : oy + bh, ox : ox + bw] = (
        bgra[:, :, :3].astype(np.float32) * a + cream[oy : oy + bh, ox : ox + bw].astype(np.float32) * (1.0 - a)
    ).astype(np.uint8)
    cv2.putText(cream, dname, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (20, 20, 180), 2, cv2.LINE_AA)
    drink_previews.append(cream)

cv2.imwrite(str(SCRATCH / "v3_drinks_qa.jpg"), np.hstack(drink_previews), [int(cv2.IMWRITE_JPEG_QUALITY), 92])

# Build QA sheet of all 28 dish photos
cols, cw, ch = 5, 340, 240
rows = (len(saved_dishes) + cols - 1) // cols
sheet = np.full((rows * ch, cols * cw, 3), 245, dtype=np.uint8)
for idx, (nm, img) in enumerate(saved_dishes):
    rs = cv2.resize(img, (cw - 12, ch - 34), interpolation=cv2.INTER_AREA)
    r, c = divmod(idx, cols)
    y0, x0 = r * ch + 28, c * cw + 6
    sheet[y0 : y0 + rs.shape[0], x0 : x0 + rs.shape[1]] = rs
    cv2.putText(sheet, nm, (x0 + 4, r * ch + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 15, 140), 2, cv2.LINE_AA)

cv2.imwrite(str(SCRATCH / "v3_all_photos_qa.jpg"), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
print(f"Prepared {len(saved_dishes)} studio photos + {len(drink_previews)} IS-Net drinks!")
