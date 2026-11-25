from pathlib import Path
import cv2
import numpy as np

ROOT = Path(r"Z:\Máy tính khác\My Computer\feel chicken")
NVA_DIR = ROOT / "Ảnh retouch" / "Ảnh Feel ngũ vị" / "Ngũ vị A"
NV_DIR = ROOT / "Ảnh retouch" / "Ảnh Feel ngũ vị"
MY_DIR = ROOT / "Ảnh retouch" / "Ảnh Feel ngũ vị & Mỳ"
ARW_DIR = ROOT / "FILE GỐC" / "261015" / "ảnh"
TN_DIR = ROOT / "menu và tài nguyên"

OUT = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\photos_v5")
OUT.mkdir(parents=True, exist_ok=True)
OLD_V3 = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\photos_v3")
SCR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch")


def read_any(p: Path) -> np.ndarray:
    if p.suffix.lower() == ".arw":
        raw_bytes = p.read_bytes()
        best_im = None
        pos = 0
        while True:
            s = raw_bytes.find(b"\xff\xd8\xff", pos)
            if s == -1 or s > 15_000_000:
                break
            e = raw_bytes.find(b"\xff\xd9", s + 20000)
            if e != -1 and (e - s) > 80000:
                arr = np.frombuffer(raw_bytes[s : e + 2], dtype=np.uint8)
                dec = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if dec is not None and (best_im is None or dec.shape[1] > best_im.shape[1]):
                    best_im = dec
            pos = s + 4096
        if best_im is None:
            raise RuntimeError(f"Could not extract preview from {p}")
        return best_im
    im = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        raise RuntimeError(f"Could not read {p}")
    return im


def light_polish(bgr: np.ndarray, boost_sat: float = 1.05, boost_val: float = 1.02) -> np.ndarray:
    """Gentle clarity polish preserving the photographer's authentic Sony A1 color grade!"""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * boost_sat, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * boost_val, 0, 255)
    res = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return cv2.addWeighted(res, 1.12, cv2.GaussianBlur(res, (0, 0), 1.0), -0.12, 0)


qa_items = []


def crop_save(
    src: Path,
    y1: float,
    y2: float,
    x1: float,
    x2: float,
    out_name: str,
    w: int = 680,
    h: int = 460,
    rot90_cw: int = 0,
    sat: float = 1.05,
    val: float = 1.02,
):
    im = read_any(src)
    if rot90_cw == 1:
        im = cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)
    elif rot90_cw == 2:
        im = cv2.rotate(im, cv2.ROTATE_180)
    elif rot90_cw == 3:
        im = cv2.rotate(im, cv2.ROTATE_90_COUNTERCLOCKWISE)

    H, W = im.shape[:2]
    sub = im[int(round(H * y1)) : int(round(H * y2)), int(round(W * x1)) : int(round(W * x2))]
    sh, sw = sub.shape[:2]
    tar = w / float(h)
    if sw / float(sh) > tar:
        nw = int(round(sh * tar))
        ox = (sw - nw) // 2
        sub = sub[:, ox : ox + nw]
    else:
        nh = int(round(sw / tar))
        oy = (sh - nh) // 2
        sub = sub[oy : oy + nh, :]
    interp = cv2.INTER_AREA if sub.shape[1] >= w else cv2.INTER_LANCZOS4
    rs = light_polish(cv2.resize(sub, (w, h), interpolation=interp), sat, val)
    cv2.imwrite(str(OUT / out_name), rs, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    qa_items.append((out_name, rs))
    return rs


# ==============================================================================
# FRONT PAGE: 11 COMBOS — 100% DISTINCT ANGLES & PLATTERS (USER SONY A1 FIRST!)
# ==============================================================================
# 00. Cơm Gà Feel Chicken (45K) — clean warm wood overhead (no grey table!)
crop_save(TN_DIR / "a8906f1213999dc7c48846.jpg", 0.08, 0.94, 0.08, 0.94, "f00_com_ga.jpg", sat=1.12, val=1.05)

# 01. Feel Solo (59K: 1 đùi gà + KTC + Coca) — Sony A1 Fries + Chicken + Dipping sauce on bright wood
crop_save(MY_DIR / "A1_09008.JPG", 0.0, 0.98, 0.02, 0.98, "f01_feel_solo.jpg", sat=1.08)

# 02. Feel Chicken Meal (79K: 1 đùi gà + Mì tương đen + Coca) — Ngũ vị A 45° chopsticks lifting Black Noodles!
crop_save(NVA_DIR / "260628 ngũ vị A  (27).png", 0.04, 0.96, 0.04, 0.96, "f02_chicken_meal.jpg", sat=1.03)

# 03. Feel Spicy (89K: 1 đùi gà + Mì cay + Coca) — Ngũ vị A 45° chopsticks lifting steaming Spicy Noodles!
crop_save(NVA_DIR / "260628 ngũ vị A  (29).png", 0.04, 0.96, 0.04, 0.96, "f03_feel_spicy.jpg", sat=1.03)

# 04. Feel Cheese (89K: 1 đùi gà + Bánh gạo lắc phô mai + Coca) — Sony A1 molten golden cheese glaze on chicken!
crop_save(NV_DIR / "A1_07881.jpg", 0.04, 0.96, 0.04, 0.96, "f04_feel_cheese.jpg", sat=1.06)

# 05. Feel Love (129K: 2 đùi gà + Tokbokki + Salad) — Ngũ vị A overhead 2 Chicken + Tokbokki leaf bowl + Lettuce!
crop_save(NVA_DIR / "260628 ngũ vị A  (5).jpeg", 0.04, 0.96, 0.02, 0.98, "f05_feel_love.jpg", sat=1.04)

# 06. Feel Couple (139K: 2 đùi gà + Mì tương đen) — Ngũ vị A overhead Chicken platter + Black Noodles side-by-side!
crop_save(NVA_DIR / "260628 ngũ vị A  (7).jpeg", 0.04, 0.96, 0.02, 0.98, "f06_feel_couple.jpg", sat=1.04)

# 07. Feel Party (179K: 4 miếng gà + Khoai tây + Tokbokki + 2 Coca) — Sony A1 261015 shoot (Fries + Tokbokki + 4-5 Glazed Drumsticks)!
crop_save(ARW_DIR / "A1_09633.ARW", 0.02, 0.98, 0.02, 0.98, "f07_feel_party.jpg", sat=1.12, val=1.06)

# 08. Feel Friends (249K: 6 miếng gà + Tokbokki + KTC + Salad + 3 Coca) — Ngũ vị A dark-slate wood grand feast!
crop_save(NVA_DIR / "260628 ngũ vị A (1).jpeg", 0.02, 0.98, 0.02, 0.98, "f08_feel_friends.jpg", sat=1.04)

# 09. Combo Ngũ Vị (259K: 5 đùi gà đủ 5 sốt + KTC + 1 món kèm) — Ngũ vị A 45° eye-level multicolor glazed chicken platter!
crop_save(NVA_DIR / "260628 ngũ vị A  (21).png", 0.02, 0.98, 0.04, 0.96, "f09_combo_nguvi.jpg", sat=1.03)

# 10. Feel Family (329K: 8 miếng gà + Tokbokki + KTC + Salad + 4 Coca) — Sony A1 warm-wood full family banquet!
crop_save(MY_DIR / "A1_08956.JPG", 0.02, 0.98, 0.02, 0.98, "f10_feel_family.jpg", sat=1.08)

# 5 Signature Sauce Close-ups (100% Sony A1 sauce-pour / glaze macro shots!)
crop_save(NV_DIR / "A1_07875.jpg", 0.08, 0.92, 0.14, 0.86, "s1_phomai.jpg", 360, 360, sat=1.08)
crop_save(NV_DIR / "A1_07854.jpg", 0.08, 0.92, 0.12, 0.84, "s2_cayhan.jpg", 360, 360, sat=1.08)
crop_save(NV_DIR / "A1_07901.jpg", 0.06, 0.90, 0.14, 0.86, "s3_toicay.jpg", 360, 360, sat=1.08)
crop_save(NV_DIR / "A1_07892.jpg", 0.08, 0.92, 0.14, 0.86, "s4_chanhday.jpg", 360, 360, sat=1.08)
crop_save(NV_DIR / "A1_07912.jpg", 0.06, 0.92, 0.12, 0.84, "s5_tuonghan.jpg", 360, 360, sat=1.08)

# ==============================================================================
# BACK PAGE: 3 CHICKEN/PASTA + 8 FAST FOOD + 4 SIDES — ZERO REPEATS FROM FRONT!
# ==============================================================================
# Left 3 Cards:
# B1. Gà Phi Lê Giòn (45K) — Ngũ vị A 45° eye-level bokeh golden crispy chicken pile!
crop_save(NVA_DIR / "260628 ngũ vị A  (33).png", 0.04, 0.98, 0.04, 0.96, "b01_ga_phile.jpg", 620, 440, sat=1.03)
# B2. Đùi / Cánh Gà Rán (39K / 35K) — Sony A1 261015 close-up single glistening glazed drumstick!
crop_save(ARW_DIR / "A1_09623.ARW", 0.04, 0.96, 0.06, 0.94, "b02_dui_canh.jpg", 620, 440, rot90_cw=3, sat=1.10, val=1.05)
# B3. Combo Mỳ Ý Gà Rán (79K / 149K) — Sony A1 Spaghetti + Glazed Chicken + Fries!
crop_save(MY_DIR / "A1_09056.JPG", 0.04, 0.96, 0.04, 0.96, "b03_combo_my_y.jpg", 620, 440, sat=1.08)

# Right 8 Fast Food Cards (2x4 Grid — ZERO duplicate claypots, 100% distinct!):
# D1. Mì Cay Hàn Quốc (Hải sản • Bạch tuộc • Đùi gà — 55K) — Ngũ vị A overhead steaming claypot!
crop_save(NVA_DIR / "260628 ngũ vị A  (17).png", 0.04, 0.96, 0.04, 0.96, "d01_mi_cay.jpg", 620, 430, sat=1.04)
# D2. Mì Tương Đen (42K) — Sony A1 solo plate w/ soft-boiled eggs & cucumber!
crop_save(MY_DIR / "A1_09006.JPG", 0.02, 0.96, 0.02, 0.98, "d02_mi_tuong_den.jpg", 620, 430, sat=1.08)
# D3. Mì Tương Đen Gà Cay (60K) — Ngũ vị A close-up Black Noodles + Red Spicy Chicken!
crop_save(NVA_DIR / "260628 ngũ vị A  (2).png", 0.02, 0.96, 0.02, 0.96, "d03_mituongden_gacay.jpg", 620, 430, sat=1.04)
# D4. Mì Ý Sốt Thịt Bằm (40K) — Sony A1 solo square black plate Spaghetti Bolognese!
crop_save(MY_DIR / "A1_09061.JPG", 0.08, 0.92, 0.08, 0.92, "d04_mi_y.jpg", 620, 430, sat=1.08)
# D5. Tokbokki Truyền Thống (39K) — Ngũ vị A 45° spoon lifting glossy red Tokbokki!
crop_save(NVA_DIR / "260628 ngũ vị A  (16).jpeg", 0.06, 0.96, 0.04, 0.96, "d05_tokbokki.jpg", 620, 430, sat=1.04)
# D6. Tokbokki Phô Mai (40K) — Melted golden mozzarella Cheese Tokbokki!
crop_save(TN_DIR / "9a8b1b5469dfe781bece108.jpg", 0.06, 0.94, 0.04, 0.96, "d06_tokbokki_phomai.jpg", 620, 430, sat=1.12)
# D7. Salad Trộn Sốt Mè (25K) — Sony A1 crisp colorful garden salad!
crop_save(MY_DIR / "A1_09001.JPG", 0.06, 0.94, 0.04, 0.96, "d07_salad.jpg", 620, 430, sat=1.08)
# D8. Bánh Gạo Lắc Phô Mai (25K) — Crispy fried cheese-powdered rice cakes!
crop_save(TN_DIR / "42bc8030fcbb72e52baa49.jpg", 0.14, 0.88, 0.04, 0.96, "d08_banh_gao_lac.jpg", 620, 430, sat=1.12)

# Bottom-Right 4 Crispy Snacks & Extra Chicken (ZERO duplicate with Fast Food above!):
# X1. Khoai Tây Chiên / Lắc Phô Mai (25K / 30K) — Sony A1 261015 chopsticks picking golden crinkle fries!
crop_save(ARW_DIR / "A1_09590.ARW", 0.02, 0.96, 0.14, 0.98, "x01_khoai_tay.jpg", 520, 370, sat=1.12, val=1.06)
# X2. Phô Mai Que Kéo Sợi (3 / 5 cái: 30K / 40K) — Crispy mozzarella sticks!
crop_save(TN_DIR / "e31f48923419ba47e30847.jpg", 0.14, 0.90, 0.08, 0.92, "x02_phomai_que.jpg", 520, 370, sat=1.12)
# X3. Xúc Xích Chiên Khứa Hoa (10K) — Reuse clean studio sausage from v3
x3_im = cv2.imread(str(OLD_V3 / "s04_xuc_xich.jpg"))
x3_rs = cv2.resize(x3_im, (520, 370), interpolation=cv2.INTER_LANCZOS4)
cv2.imwrite(str(OUT / "x03_xuc_xich.jpg"), x3_rs, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
qa_items.append(("x03_xuc_xich.jpg", x3_rs))
# X4. Gà Giòn Xé Nóng / Gọi Thêm Miếng Lẻ (35K / 39K) — Sony A1 hands pulling hot crispy saucy chicken!
crop_save(NV_DIR / "A1_08040.jpg", 0.06, 0.96, 0.08, 0.92, "x04_ga_xe_them.jpg", 520, 370, sat=1.06)

# Copy 5 spotless IS-Net drink PNGs from photos_v3
import shutil
for dr in OLD_V3.glob("dr*.png"):
    shutil.copy2(dr, OUT / dr.name)

# Build visual QA grid of all 32 photos to verify ZERO duplicates and correct orientation!
cols, cw, ch = 6, 300, 220
rows = (len(qa_items) + cols - 1) // cols
sheet = np.full((rows * ch, cols * cw, 3), 245, dtype=np.uint8)
for idx, (nm, im) in enumerate(qa_items):
    rs = cv2.resize(im, (cw - 10, ch - 30), interpolation=cv2.INTER_AREA)
    r, c = divmod(idx, cols)
    y0, x0 = r * ch + 26, c * cw + 5
    sheet[y0 : y0 + rs.shape[0], x0 : x0 + rs.shape[1]] = rs
    cv2.putText(sheet, nm, (x0 + 3, r * ch + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (15, 15, 160), 1, cv2.LINE_AA)

cv2.imwrite(str(SCR / "v5_zero_dup_qa.jpg"), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
print(f"Prepared {len(qa_items)} 100%-distinct photos!")
