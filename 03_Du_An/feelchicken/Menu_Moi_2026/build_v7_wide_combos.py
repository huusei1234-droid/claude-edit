from pathlib import Path
import cv2
import numpy as np

BASE = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026")
CUT_DIR = BASE / "assets" / "cutouts_v7"
COMBO_OUT = BASE / "assets" / "combos_v7"
COMBO_OUT.mkdir(parents=True, exist_ok=True)
SCR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch")

CACHE = {}


def get_cut(name: str) -> np.ndarray:
    if name not in CACHE:
        im = cv2.imread(str(CUT_DIR / name), cv2.IMREAD_UNCHANGED)
        if im is None:
            raise FileNotFoundError(f"Missing cutout: {name}")
        CACHE[name] = im
    return CACHE[name]


def rotate_bgra(bgra: np.ndarray, angle_deg: float, flip_x: bool = False) -> np.ndarray:
    im = bgra[:, ::-1, :].copy() if flip_x else bgra
    if abs(angle_deg) < 0.5:
        return im
    h, w = im.shape[:2]
    pad = int(max(h, w) * 0.38)
    p_im = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    ph, pw = p_im.shape[:2]
    M = cv2.getRotationMatrix2D((pw / 2.0, ph / 2.0), angle_deg, 1.0)
    rot = cv2.warpAffine(p_im, M, (pw, ph), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    ys, xs = np.where(rot[:, :, 3] > 12)
    if len(xs) == 0:
        return im
    return rot[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]


def compose_combo(out_name: str, layers_spec: list, cw: int = 1200, ch: int = 820) -> np.ndarray:
    canvas = np.zeros((ch, cw, 4), dtype=np.float32)

    for cut_nm, cx_n, cy_n, sz_px, by_h, ang, flp in layers_spec:
        src = rotate_bgra(get_cut(cut_nm), ang, flp)
        sh0, sw0 = src.shape[:2]
        scale = (sz_px / float(sh0)) if by_h else (sz_px / float(sw0))
        nw, nh = max(1, int(round(sw0 * scale))), max(1, int(round(sh0 * scale)))
        interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LANCZOS4
        item = cv2.resize(src, (nw, nh), interpolation=interp).astype(np.float32)

        x0 = int(round(cx_n * cw - nw / 2.0))
        y0 = int(round(cy_n * ch - nh / 2.0))

        # Soft warm studio contact shadow between overlapping dishes
        sh_layer = np.zeros((ch, cw, 4), dtype=np.float32)
        sx0, sy0 = x0 + 4, y0 + 14
        ix0, iy0 = max(0, -sx0), max(0, -sy0)
        ox0, oy0 = max(0, sx0), max(0, sy0)
        copy_w = min(nw - ix0, cw - ox0)
        copy_h = min(nh - iy0, ch - oy0)
        if copy_w > 0 and copy_h > 0:
            sh_a = item[iy0 : iy0 + copy_h, ix0 : ix0 + copy_w, 3] * 0.34
            sh_layer[oy0 : oy0 + copy_h, ox0 : ox0 + copy_w, 0] = 8.0
            sh_layer[oy0 : oy0 + copy_h, ox0 : ox0 + copy_w, 1] = 22.0
            sh_layer[oy0 : oy0 + copy_h, ox0 : ox0 + copy_w, 2] = 54.0
            sh_layer[oy0 : oy0 + copy_h, ox0 : ox0 + copy_w, 3] = sh_a
            sh_layer[:, :, 3] = cv2.GaussianBlur(sh_layer[:, :, 3], (37, 37), 11.5)
            sa = sh_layer[:, :, 3:4] / 255.0
            da = canvas[:, :, 3:4] / 255.0
            out_a = sa + da * (1.0 - sa)
            canvas[:, :, :3] = np.where(
                out_a > 1e-5,
                (sh_layer[:, :, :3] * sa + canvas[:, :, :3] * da * (1.0 - sa)) / np.maximum(out_a, 1e-5),
                0.0,
            )
            canvas[:, :, 3:4] = out_a * 255.0

        ix0, iy0 = max(0, -x0), max(0, -y0)
        ox0, oy0 = max(0, x0), max(0, y0)
        copy_w = min(nw - ix0, cw - ox0)
        copy_h = min(nh - iy0, ch - oy0)
        if copy_w > 0 and copy_h > 0:
            fg_sub = item[iy0 : iy0 + copy_h, ix0 : ix0 + copy_w]
            sa = fg_sub[:, :, 3:4] / 255.0
            dst_sub = canvas[oy0 : oy0 + copy_h, ox0 : ox0 + copy_w]
            da = dst_sub[:, :, 3:4] / 255.0
            out_a = sa + da * (1.0 - sa)
            dst_sub[:, :, :3] = np.where(
                out_a > 1e-5,
                (fg_sub[:, :, :3] * sa + dst_sub[:, :, :3] * da * (1.0 - sa)) / np.maximum(out_a, 1e-5),
                0.0,
            )
            dst_sub[:, :, 3:4] = out_a * 255.0
            canvas[oy0 : oy0 + copy_h, ox0 : ox0 + copy_w] = dst_sub

    res = np.clip(np.round(canvas), 0, 255).astype(np.uint8)
    ys, xs = np.where(res[:, :, 3] > 10)
    pad = 8
    y0, y1 = max(0, ys.min() - pad), min(ch, ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(cw, xs.max() + pad)
    res = res[y0:y1, x0:x1]
    cv2.imwrite(str(COMBO_OUT / out_name), res)
    return res


# Wide, full-filling studio combo spreads (~1.48:1 - 1.62:1 aspect ratio so food fills 92%+ of column width!)
combos_spec = [
    # 00. Cơm Gà Feel Chicken (45K): 1 Coca + Cơm gà đùi sốt + Salad
    ("cb00_com_ga.png", [
        ("lon_coca.png", 0.74, 0.39, 430, True, 3, False),
        ("com_ga_plate.png", 0.43, 0.56, 610, False, 0, False),
    ]),
    # 01. Feel Solo (59K): 1 đùi gà giòn + Khoai tây chiên + 1 Coca
    ("cb01_solo.png", [
        ("lon_coca.png", 0.75, 0.38, 435, True, 2, False),
        ("khoai_tay_dia.png", 0.64, 0.63, 500, False, -3, False),
        ("dui_gion.png", 0.34, 0.60, 520, False, 20, True),
    ]),
    # 02. Feel Chicken Meal (79K): 1 đùi gà sốt tương Hàn + Mì tương đen + 1 Coca
    ("cb02_meal.png", [
        ("lon_coca.png", 0.76, 0.38, 435, True, 2, False),
        ("mi_tuong_den.png", 0.41, 0.54, 570, False, 0, False),
        ("dui_sot_tuong.png", 0.67, 0.69, 490, False, -16, True),
    ]),
    # 03. Feel Spicy (89K): 1 đùi gà sốt cay Hàn đỏ rực + Nồi Mì cay đủ 2 quai + 1 Coca!
    ("cb03_spicy.png", [
        ("lon_coca.png", 0.76, 0.38, 435, True, 2, False),
        ("mi_cay_haisan.png", 0.39, 0.53, 555, False, 0, False),
        ("dui_sot_cay.png", 0.67, 0.69, 500, False, -15, False),
    ]),
    # 04. Feel Cheese (89K): 1 đùi gà sốt phô mai + Bánh gạo lắc phô mai + 1 Coca
    ("cb04_cheese.png", [
        ("lon_coca.png", 0.75, 0.38, 435, True, 2, False),
        ("banh_gao_lac.png", 0.64, 0.63, 505, False, -3, False),
        ("dui_sot_phomai.png", 0.35, 0.60, 520, False, 20, True),
    ]),
    # 05. Feel Love (129K): 2 đùi gà + Tokbokki + Salad
    ("cb05_love.png", [
        ("salad.png", 0.65, 0.40, 470, False, 3, False),
        ("dui_gion.png", 0.29, 0.44, 480, False, 32, False),
        ("tokbokki.png", 0.63, 0.64, 480, False, -5, False),
        ("dui_sot_cay.png", 0.33, 0.66, 500, False, 14, True),
    ]),
    # 06. Feel Couple (139K): 2 đùi gà + Mì tương đen
    ("cb06_couple.png", [
        ("mi_tuong_den.png", 0.63, 0.54, 570, False, 2, False),
        ("dui_sot_phomai.png", 0.30, 0.44, 490, False, 28, True),
        ("dui_sot_tuong.png", 0.34, 0.67, 500, False, 10, True),
    ]),
    # 07. Feel Party (179K): 4 miếng gà + Khoai tây + Tokbokki + 2 Coca
    ("cb07_party.png", [
        ("lon_coca.png", 0.66, 0.30, 385, True, -2, False),
        ("lon_coca.png", 0.77, 0.32, 385, True, 3, False),
        ("tokbokki.png", 0.27, 0.45, 440, False, -7, False),
        ("khoai_tay_dia.png", 0.72, 0.58, 450, False, 4, False),
        ("ga_4_mieng.png", 0.48, 0.61, 535, False, 0, False),
    ]),
    # 08. Feel Friends (249K): 6 miếng gà + Tokbokki + Khoai tây + Salad + 3 Coca
    ("cb08_friends.png", [
        ("lon_coca.png", 0.62, 0.29, 365, True, -3, False),
        ("lon_coca.png", 0.72, 0.29, 365, True, 0, False),
        ("lon_coca.png", 0.82, 0.31, 365, True, 4, False),
        ("salad.png", 0.24, 0.42, 420, False, -5, False),
        ("tokbokki.png", 0.46, 0.38, 420, False, 4, False),
        ("khoai_tay_dia.png", 0.76, 0.59, 440, False, 5, False),
        ("ga_mam_sot.png", 0.46, 0.62, 560, False, 0, False),
    ]),
    # 09. Combo Ngũ Vị (259K): 5 đùi gà đủ 5 sốt + KTC + Salad / Tokbokki / Mì tương đen
    ("cb09_nguvi.png", [
        ("salad.png", 0.24, 0.36, 390, False, -6, False),
        ("tokbokki.png", 0.49, 0.32, 400, False, 0, False),
        ("mi_tuong_den.png", 0.75, 0.37, 420, False, 5, False),
        ("khoai_tay_dia.png", 0.76, 0.62, 430, False, 4, False),
        ("ga_5_nguvi.png", 0.44, 0.61, 560, False, 0, False),
    ]),
    # 10. Feel Family (329K): 8 miếng gà + Tokbokki + Khoai tây + Salad + 4 Coca
    ("cb10_family.png", [
        ("lon_coca.png", 0.56, 0.28, 350, True, -4, False),
        ("lon_coca.png", 0.65, 0.28, 350, True, -1, False),
        ("lon_coca.png", 0.74, 0.29, 350, True, 2, False),
        ("lon_coca.png", 0.83, 0.31, 350, True, 5, False),
        ("salad.png", 0.23, 0.41, 410, False, -6, False),
        ("tokbokki.png", 0.42, 0.37, 410, False, 3, False),
        ("khoai_tay_dia.png", 0.77, 0.60, 445, False, 4, False),
        ("ga_mam_lon.png", 0.45, 0.63, 595, False, 0, False),
    ]),
    # 11. Combo Mỳ Ý Gà Rán (79K / 149K — Back Page)
    ("cb11_my_y.png", [
        ("lon_coca.png", 0.20, 0.39, 405, True, -3, False),
        ("lon_coca.png", 0.31, 0.41, 405, True, 2, False),
        ("mi_y.png", 0.64, 0.52, 540, False, 2, False),
        ("dui_sot_cay.png", 0.37, 0.69, 460, False, 16, True),
    ]),
    # 12. Đùi / Cánh Gà Rán Duo (39K / 35K — Back Page)
    ("cb_dui_canh.png", [
        ("dui_gion.png", 0.43, 0.43, 570, False, 26, False),
        ("dui_sot_cay.png", 0.55, 0.64, 590, False, 8, True),
    ]),
]

qa_cards = []
for out_nm, spec in combos_spec:
    res = compose_combo(out_nm, spec)
    ar = res.shape[1] / float(res.shape[0])
    print(f"Composed {out_nm:18s}: {res.shape[1]}x{res.shape[0]} (AR={ar:.2f})")
    tw, th = 360, 250
    card = np.full((th, tw, 3), (220, 242, 254), dtype=np.uint8)
    s = min((tw - 14) / float(res.shape[1]), (th - 34) / float(res.shape[0]))
    rw, rh = int(res.shape[1] * s), int(res.shape[0] * s)
    rs = cv2.resize(res, (rw, rh), interpolation=cv2.INTER_AREA)
    ox, oy = (tw - rw) // 2, 26 + (th - 30 - rh) // 2
    af = rs[:, :, 3:4].astype(np.float32) / 255.0
    card[oy : oy + rh, ox : ox + rw] = (rs[:, :, :3] * af + card[oy : oy + rh, ox : ox + rw] * (1.0 - af)).astype(np.uint8)
    cv2.putText(card, f"{out_nm[:-4]} AR={ar:.2f}", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (15, 15, 160), 1, cv2.LINE_AA)
    qa_cards.append(card)

while len(qa_cards) < 15:
    qa_cards.append(np.full_like(qa_cards[0], 245))
grid = np.vstack([np.hstack(qa_cards[r * 5 : (r + 1) * 5]) for r in range(3)])
cv2.imwrite(str(SCR / "v7_combos_audit.jpg"), grid, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
print("V7 WIDE COMBOS READY!")
