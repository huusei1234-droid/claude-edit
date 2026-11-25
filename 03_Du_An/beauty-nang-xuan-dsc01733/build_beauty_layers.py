import os
import math
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import AutoModelForImageSegmentation, SegformerImageProcessor, SegformerForSemanticSegmentation
from torchvision import transforms

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

WORK_DIR = r"d:\AI\full studio\output\beauty_dsc01733"
BASE_DEFAULT_PNG = os.path.join(WORK_DIR, "00_acr_base_6000x4000.png")
BASE_RECOV_PNG = os.path.join(WORK_DIR, "00_acr_recovered.png")
LAMA_PATH = r"C:\Users\Hang thu\.cache\torch\hub\checkpoints\big-lama.pt"


def odd(val: float, min_val: int = 3) -> int:
    k = max(min_val, int(round(val)))
    return k if k % 2 == 1 else k + 1


def gauss_blur(arr: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0.2:
        return arr.copy()
    res = cv2.GaussianBlur(arr, (0, 0), sigmaX=sigma, sigmaY=sigma)
    if arr.ndim == 3 and res.ndim == 2:
        res = res[..., None]
    return res


def largest_cc(mask_u8: np.ndarray) -> np.ndarray:
    n_lbl, lbls, stats, _ = cv2.connectedComponentsWithStats((mask_u8 > 0).astype(np.uint8), connectivity=8)
    if n_lbl <= 1:
        return (mask_u8 > 0).astype(np.uint8)
    best = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return (lbls == best).astype(np.uint8)


def extrapolate_masked_channel(val: np.ndarray, valid_mask: np.ndarray, sigma: float) -> np.ndarray:
    w = (valid_mask > 0).astype(np.float32)
    num = gauss_blur(val * w, sigma)
    den = gauss_blur(w, sigma)
    med = float(np.median(val[valid_mask > 0])) if (valid_mask > 0).any() else 0.0
    padded = np.where(den > 1e-4, num / np.maximum(den, 1e-4), med)
    return np.where(valid_mask > 0, val, padded)


def main():
    device = torch.device("cuda")
    # Use crisp default ACR base (deep rich blacks/eyes!) and blend RAW highlight recovery ONLY into bright sunlit cheek > 235!
    rgb_crisp = np.array(Image.open(BASE_DEFAULT_PNG).convert("RGB"))
    rgb_recov = np.array(Image.open(BASE_RECOV_PNG).convert("RGB"))
    H, W = rgb_crisp.shape[:2]

    lama = torch.jit.load(LAMA_PATH, map_location=device).eval()
    face_proc = SegformerImageProcessor.from_pretrained("jonathandinu/face-parsing")
    face_model = SegformerForSemanticSegmentation.from_pretrained("jonathandinu/face-parsing").to(device).eval()
    birefnet = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet", trust_remote_code=True).to(device).eval().half()
    biref_tf = transforms.Compose([
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    with torch.inference_mode():
        inp_b = biref_tf(Image.fromarray(rgb_crisp)).unsqueeze(0).to(device).half()
        person_mask = F.interpolate(birefnet(inp_b)[-1].sigmoid().float(), size=(H, W), mode="bilinear", align_corners=False)[0, 0].cpu().numpy()

        inp_f = face_proc(images=Image.fromarray(rgb_crisp), return_tensors="pt").to(device)
        coarse = F.interpolate(face_model(**inp_f).logits, size=(512, 512), mode="bilinear", align_corners=False).argmax(dim=1)[0].cpu().numpy()
        # Tight Pass 2 strictly around FACE SKIN (classes 1, 2) — NOT waist-length hair — so both eyes & lips parse at 5x resolution!
        face_only_coarse = largest_cc(np.isin(coarse, [1, 2, 4, 5, 6, 7, 10, 11, 12]).astype(np.uint8))
        ys, xs = np.where(face_only_coarse > 0)
        x0_c, x1_c = xs.min() / 512.0 * W, xs.max() / 512.0 * W
        y0_c, y1_c = ys.min() / 512.0 * H, ys.max() / 512.0 * H
        box_s = max(x1_c - x0_c, y1_c - y0_c)
        cx_mid, cy_mid = 0.5 * (x0_c + x1_c), 0.5 * (y0_c + y1_c)
        cx0, cy0 = max(0, int(cx_mid - 0.72 * box_s)), max(0, int(cy_mid - 0.68 * box_s))
        cx1, cy1 = min(W, int(cx_mid + 0.72 * box_s)), min(H, int(cy_mid + 0.95 * box_s))

        inp_c = face_proc(images=Image.fromarray(rgb_crisp[cy0:cy1, cx0:cx1]), return_tensors="pt").to(device)
        up_logits = F.interpolate(face_model(**inp_c).logits, size=(cy1 - cy0, cx1 - cx0), mode="bilinear", align_corners=False)
        crop_cls = up_logits.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)
        print("Tight crop classes pixel counts -> l_eye:", int((crop_cls == 4).sum()), "r_eye:", int((crop_cls == 5).sum()), "lips:", int(np.isin(crop_cls, [10, 11, 12]).sum()))

        cls_map = np.zeros((H, W), dtype=np.uint8)
        cls_map[cy0:cy1, cx0:cx1] = crop_cls

    face_core = largest_cc(np.isin(cls_map, [1, 2, 4, 5, 6, 7, 10, 11, 12]).astype(np.uint8))
    fys, fxs = np.where(face_core > 0)
    fx0, fy0, fx1, fy1 = int(fxs.min()), int(fys.min()), int(fxs.max()), int(fys.max())
    fw, fh = fx1 - fx0, fy1 - fy0

    face_skin = np.isin(cls_map, [1, 2]).astype(np.uint8)
    neck_skin = (cls_map == 17).astype(np.uint8)
    ears_skin = np.isin(cls_map, [8, 9]).astype(np.uint8)
    eyes = np.isin(cls_map, [4, 5]).astype(np.uint8)
    brows = np.isin(cls_map, [6, 7]).astype(np.uint8)
    lips = np.isin(cls_map, [10, 11, 12]).astype(np.uint8)
    hair = (cls_map == 13).astype(np.uint8)

    # Blend 14-bit RAW highlight recovery ONLY into ultra-bright skin highlights (max RGB > 228) so eyes & hair stay 100% crisp!
    max_ch = rgb_crisp.max(axis=-1).astype(np.float32)
    hl_skin_w = gauss_blur((((face_skin > 0) | (neck_skin > 0)) & (eyes == 0) & (lips == 0)).astype(np.float32) * np.clip((max_ch - 222.0) / 28.0, 0.0, 1.0), 8.0)[..., None]
    rgb_orig = np.clip(np.round(rgb_crisp.astype(np.float32) * (1.0 - 0.72 * hl_skin_w) + rgb_recov.astype(np.float32) * (0.72 * hl_skin_w)), 0, 255).astype(np.uint8)

    # Hand/arm skin
    lab_full = cv2.cvtColor(rgb_orig, cv2.COLOR_RGB2LAB).astype(np.float32)
    med_L, med_a, med_b = np.median(lab_full[(face_skin > 0) | (neck_skin > 0)], axis=0)
    dist_ab = np.hypot(lab_full[..., 1] - med_a, lab_full[..., 2] - med_b)
    hand_cand = (
        (person_mask > 0.5)
        & (cls_map == 0)
        & (dist_ab < 12.5)
        & ((lab_full[..., 1] - 128.0) < 20.0)
        & ((lab_full[..., 2] - 128.0) < 26.0)
        & (lab_full[..., 0] > 95.0)
    ).astype(np.uint8)
    hand_cand = cv2.morphologyEx(hand_cand, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n_hd, hd_l, hd_st, _ = cv2.connectedComponentsWithStats(hand_cand, connectivity=8)
    hand_skin = np.zeros((H, W), dtype=np.uint8)
    for i in range(1, n_hd):
        if hd_st[i, cv2.CC_STAT_AREA] > int((0.04 * fw) ** 2):
            hand_skin |= (hd_l == i).astype(np.uint8)

    # WIDE, IRONCLAD EYE-SOCKET, DOUBLE-EYELID, EYELASH, BROW, NOSTRIL & LIP PROTECTION!
    eye_guard = cv2.dilate(eyes, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.088 * fw, 29), odd(0.115 * fw, 39))))
    brow_guard = cv2.dilate(brows, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.065 * fw, 23), odd(0.040 * fw, 15))))
    lip_guard = cv2.dilate(lips, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.048 * fw, 19), odd(0.048 * fw, 19))))
    hair_guard = cv2.dilate((hair | ears_skin).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.014 * fw, 7), odd(0.014 * fw, 7))))

    nose_m = (cls_map == 2)
    nys, nxs = np.where(nose_m)
    nostril_guard = np.zeros((H, W), dtype=np.uint8)
    if len(nys) > 20:
        ny_cut = int(nys.min() + 0.48 * (nys.max() - nys.min()))
        nostril_guard[ny_cut : nys.max() + 1, nxs.min() : nxs.max() + 1] = nose_m[ny_cut : nys.max() + 1, nxs.min() : nxs.max() + 1].astype(np.uint8)
        nostril_guard = cv2.dilate(nostril_guard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.028 * fw, 13), odd(0.028 * fw, 13))))

    feature_guard = ((eye_guard > 0) | (brow_guard > 0) | (lip_guard > 0) | (hair_guard > 0) | (nostril_guard > 0)).astype(np.uint8)
    heal_skin = (((face_skin > 0) | (neck_skin > 0)) & (feature_guard == 0)).astype(np.uint8)

    # --- STAGE 1: Precision Spot-Healing (including bright sunlit forehead pimples!) ---
    hys, hxs = np.where(heal_skin > 0)
    pad_s = int(0.06 * fw)
    sx0, sy0 = max(0, hxs.min() - pad_s), max(0, hys.min() - pad_s)
    sx1, sy1 = min(W, hxs.max() + pad_s), min(H, hys.max() + pad_s)

    sub_rgb = rgb_orig[sy0:sy1, sx0:sx1]
    sub_heal = heal_skin[sy0:sy1, sx0:sx1]
    valid_sk = (((face_skin[sy0:sy1, sx0:sx1] > 0) | (neck_skin[sy0:sy1, sx0:sx1] > 0)) & (feature_guard[sy0:sy1, sx0:sx1] == 0)).astype(np.uint8)

    sub_lab = cv2.cvtColor(sub_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L_sub = sub_lab[..., 0] * (100.0 / 255.0)
    a_sub = sub_lab[..., 1] - 128.0

    L_ext = extrapolate_masked_channel(L_sub, valid_sk, max(6.0, 0.016 * fw))
    a_ext = extrapolate_masked_channel(a_sub, valid_sk, max(6.0, 0.016 * fw))

    d_spot = odd(0.024 * fw, 15)
    se_spot = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d_spot, d_spot))
    L_sm = gauss_blur(L_ext, max(1.0, 0.0020 * fw))
    a_sm = gauss_blur(a_ext, max(1.2, 0.0024 * fw))

    dark_bh = cv2.morphologyEx(L_sm, cv2.MORPH_BLACKHAT, se_spot)
    red_th = cv2.morphologyEx(a_sm, cv2.MORPH_TOPHAT, se_spot)
    se_bump = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.018 * fw, 11), odd(0.018 * fw, 11)))
    bump_th = cv2.morphologyEx(L_sm, cv2.MORPH_TOPHAT, se_bump)

    cand = (
        (sub_heal > 0)
        & (
            (dark_bh > 2.4)
            | (red_th > 1.65)
            | ((dark_bh > 1.6) & (red_th > 1.15))
            | ((bump_th > 2.4) & (L_sm < 95.0))
        )
    ).astype(np.uint8)
    cand = cv2.morphologyEx(cand, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    cand = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

    n_c, c_lbl, c_st, _ = cv2.connectedComponentsWithStats(cand, connectivity=8)
    spot_mask_sub = np.zeros_like(cand)
    min_a, max_a = max(6, int((0.0028 * fw) ** 2)), int((0.038 * fw) ** 2)
    n_spots = 0
    for idx in range(1, n_c):
        ar_px = c_st[idx, cv2.CC_STAT_AREA]
        if not (min_a <= ar_px <= max_a):
            continue
        comp = (c_lbl == idx)
        cys, cxs = np.where(comp)
        if len(cxs) >= 12:
            eig = np.linalg.eigvalsh(np.cov(np.stack([cxs.astype(np.float32), cys.astype(np.float32)], axis=1), rowvar=False))
            elong = math.sqrt(max(eig[1], 1e-3) / max(eig[0], 1e-3))
        else:
            elong = 1.0
        if elong <= 2.75:
            spot_mask_sub |= comp.astype(np.uint8)
            n_spots += 1

    spot_dil = cv2.dilate(spot_mask_sub, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.011 * fw, 9), odd(0.011 * fw, 9))))
    spot_dil[feature_guard[sy0:sy1, sx0:sx1] > 0] = 0

    step1_healed = rgb_orig.copy()
    if n_spots > 0:
        full_spot = np.zeros((H, W), dtype=np.uint8)
        full_spot[sy0:sy1, sx0:sx1] = spot_dil
        clustered = cv2.dilate(full_spot, cv2.getStructuringElement(cv2.MORPH_RECT, (141, 141)))
        n_cl, _, cl_st, _ = cv2.connectedComponentsWithStats(clustered, connectivity=8)
        with torch.inference_mode():
            for lbl in range(1, n_cl):
                bx, by, bw_c, bh_c, _ = cl_st[lbl]
                px0, py0 = max(0, bx - 96), max(0, by - 96)
                px1, py1 = min(W, bx + bw_c + 96), min(H, by + bh_c + 96)
                if px1 - px0 < 256:
                    px1 = min(W, px0 + 256); px0 = max(0, px1 - 256)
                if py1 - py0 < 256:
                    py1 = min(H, py0 + 256); py0 = max(0, py1 - 256)
                s_im = step1_healed[py0:py1, px0:px1]
                s_mk = (full_spot[py0:py1, px0:px1] > 0).astype(np.uint8)
                if s_mk.sum() == 0:
                    continue
                sh, sw = s_im.shape[:2]
                ph, pw = (8 - sh % 8) % 8, (8 - sw % 8) % 8
                s_im_p = cv2.copyMakeBorder(s_im, 0, ph, 0, pw, cv2.BORDER_REPLICATE) if (ph or pw) else s_im
                s_mk_p = cv2.copyMakeBorder(s_mk, 0, ph, 0, pw, cv2.BORDER_CONSTANT, value=0) if (ph or pw) else s_mk
                it = torch.from_numpy(s_im_p).permute(2, 0, 1).unsqueeze(0).float().to(device) / 255.0
                mt = torch.from_numpy(s_mk_p).unsqueeze(0).unsqueeze(0).float().to(device)
                inp_res = (lama(it, mt)[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()[:sh, :sw] * 255.0).astype(np.float32)

                r_out = cv2.dilate(s_mk, cv2.getStructuringElement(cv2.MORPH_RECT, (27, 27)))
                r_in = cv2.dilate(s_mk, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
                ring = (r_out > 0) & (r_in == 0)
                orig_f = s_im.astype(np.float32)
                hf = orig_f - gauss_blur(orig_f, 1.3)
                if ring.sum() > 80:
                    std_r = np.std(hf[ring], axis=0, keepdims=True).clip(0.6, 4.5)
                    std_i = np.std((inp_res - gauss_blur(inp_res, 1.3))[s_mk > 0], axis=0, keepdims=True).clip(0.1, 10.0)
                    rng = np.random.default_rng(100 + lbl)
                    nz = gauss_blur(rng.normal(0.0, 1.0, size=(sh, sw, 1)).astype(np.float32), 0.55) * 1.45
                    inp_res = np.clip(inp_res + nz * np.maximum(0.0, std_r - std_i) * 0.65, 0, 255)

                al = gauss_blur(s_mk.astype(np.float32), 2.5)[..., None]
                step1_healed[py0:py1, px0:px1] = np.clip(np.round(orig_f * (1.0 - al) + inp_res * al), 0, 255).astype(np.uint8)

    # Enforce 100% crisp untouched features on step1_healed
    core_untouched = ((eyes > 0) | (brows > 0) | (lips > 0) | (nostril_guard > 0) | (hair > 0))
    step1_healed[core_untouched] = rgb_crisp[core_untouched]
    print(f"Stage 1 Spot-Heal v2 done: {n_spots} blemishes removed.")
    Image.fromarray(step1_healed).save(os.path.join(WORK_DIR, "01_spot_heal.png"))

    # --- STAGE 2: Silky Natural Beauty Skin (100% Zero Bleed on Eyes, Eyelids, Brows, Lips!) ---
    img_f = step1_healed.astype(np.float32) / 255.0
    # Subtract feature_guard BEFORE blurring so w_head NEVER reaches eyes, eyelids, brows, or lips!
    safe_head_raw = (((face_skin > 0) | (neck_skin > 0)) & (feature_guard == 0)).astype(np.float32)
    w_head = gauss_blur(safe_head_raw, 0.012 * fw)
    w_head[eye_guard > 0] = 0.0
    w_head[brow_guard > 0] = 0.0
    w_head[lip_guard > 0] = 0.0
    w_head[nostril_guard > 0] = 0.0
    w_head = gauss_blur(w_head, 0.006 * fw)
    w_head[core_untouched] = 0.0

    w_hand = gauss_blur(hand_skin.astype(np.float32), 0.012 * fw)
    w_beauty = np.clip(w_head + 0.65 * w_hand, 0.0, 1.0)

    sig_fine = max(1.3, 0.0028 * fw)
    sig_mid = max(3.8, 0.0098 * fw)
    blur_fine = gauss_blur(img_f, sig_fine)
    lf_base = gauss_blur(img_f, sig_mid)
    hf_fine = img_f - blur_fine
    hf_mid = blur_fine - lf_base

    half_lf = cv2.resize(lf_base, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    smooth_half = cv2.bilateralFilter(half_lf, d=odd(0.060 * (fw * 0.5), 9), sigmaColor=0.056, sigmaSpace=max(12.0, 0.048 * (fw * 0.5)))
    lf_even = cv2.resize(smooth_half, (W, H), interpolation=cv2.INTER_CUBIC)

    tone_w = (0.38 * w_beauty)[..., None]
    lf_new = lf_base * (1.0 - tone_w) + lf_even * tone_w

    # Gentle Dodge & Burn lighting balance on safe skin only
    lf_u8 = np.clip(np.round(lf_new * 255.0), 0, 255).astype(np.uint8)
    lf_lab = cv2.cvtColor(lf_u8, cv2.COLOR_RGB2LAB).astype(np.float32)
    L_lf = lf_lab[..., 0] * (100.0 / 255.0)
    a_lf = lf_lab[..., 1] - 128.0
    b_lf = lf_lab[..., 2] - 128.0

    fs_mid = (safe_head_raw > 0) & (L_lf > 52.0) & (L_lf < 82.0)
    target_a = float(np.median(a_lf[fs_mid])) + 0.7
    target_b = float(np.median(b_lf[fs_mid])) - 0.5

    hot_excess = np.maximum(0.0, L_lf - 84.5)
    hot_w = w_head * np.clip(hot_excess / 12.0, 0.0, 1.0)
    L_lf -= hot_w * (hot_excess * 0.36)
    a_lf = a_lf * (1.0 - 0.42 * hot_w) + target_a * (0.42 * hot_w)
    b_lf = b_lf * (1.0 - 0.38 * hot_w) + target_b * (0.38 * hot_w)

    shad_w = w_head * np.clip((75.0 - L_lf) / 24.0, 0.0, 1.0) * np.clip((L_lf - 28.0) / 18.0, 0.0, 1.0)
    L_lf += shad_w * 2.8
    L_lf += w_beauty * 1.1 * np.clip((88.0 - L_lf) / 22.0, 0.0, 1.0)
    a_lf += w_beauty * 0.75
    b_lf -= w_beauty * 0.85

    lf_lab_out = np.stack([
        np.clip(L_lf * (255.0 / 100.0), 0, 255),
        np.clip(a_lf + 128.0, 0, 255),
        np.clip(b_lf + 128.0, 0, 255),
    ], axis=-1).astype(np.uint8)
    lf_beauty = cv2.cvtColor(lf_lab_out, cv2.COLOR_LAB2RGB).astype(np.float32) / 255.0

    # Keep 95% crisp fine pores + 55% soft-clamped mid pores -> ultra-real silky camera skin!
    hf_beauty = 0.95 * hf_fine + 0.55 * np.tanh(hf_mid / 0.032) * 0.032
    hf_orig = hf_fine + hf_mid
    wb3 = w_beauty[..., None]
    beauty_rgb_f = np.clip(lf_beauty + hf_orig * (1.0 - wb3) + hf_beauty * wb3, 0.0, 1.0)
    step2_beauty = np.clip(np.round(beauty_rgb_f * 255.0), 0, 255).astype(np.uint8)
    step2_beauty[core_untouched] = rgb_crisp[core_untouched]

    mask_u8 = np.clip(np.round(w_beauty * 255.0), 0, 255).astype(np.uint8)
    Image.fromarray(step2_beauty).save(os.path.join(WORK_DIR, "02_beauty_skin.png"))
    Image.fromarray(mask_u8).save(os.path.join(WORK_DIR, "02_beauty_mask.png"))

    zx0, zx1 = max(0, int(fx0 - 0.12 * fw)), min(W, int(fx1 + 0.12 * fw))
    zy0, zy1 = max(0, int(fy0 - 0.10 * fh)), min(H, int(fy1 + 0.25 * fh))
    zoom_comp = np.hstack([rgb_crisp[zy0:zy1, zx0:zx1], step2_beauty[zy0:zy1, zx0:zx1]])
    Image.fromarray(zoom_comp).save(os.path.join(WORK_DIR, "qc_zoom_200pct_skin.jpg"), quality=96)
    print("Stage 2 v2 Beauty Skin & Mask saved successfully!")


if __name__ == "__main__":
    main()
