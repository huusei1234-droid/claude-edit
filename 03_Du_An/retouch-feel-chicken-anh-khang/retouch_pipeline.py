import os
import sys
import glob
import time
import math
import json
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageCms
from transformers import AutoModelForImageSegmentation, SegformerImageProcessor, SegformerForSemanticSegmentation
from torchvision import transforms

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

RAW_DIR = r"d:\AI\full studio\output\retouch_anh_khang\01_raw_srgb"
TEST_DIR = r"d:\AI\full studio\output\retouch_anh_khang\02_test_check"
OUT_FINAL_DIR = r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Anh Khang"
LAMA_PATH = r"C:\Users\Hang thu\.cache\torch\hub\checkpoints\big-lama.pt"

os.makedirs(TEST_DIR, exist_ok=True)


def get_srgb_icc_bytes():
    srgb_prof = ImageCms.createProfile("sRGB")
    return ImageCms.ImageCmsProfile(srgb_prof).tobytes()


SRGB_ICC = get_srgb_icc_bytes()


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
    """Fast GPU/SIMD-friendly normalized convolution to pad values smoothly outside valid_mask (replaces slow Telea)."""
    w = (valid_mask > 0).astype(np.float32)
    num = gauss_blur(val * w, sigma)
    den = gauss_blur(w, sigma)
    med = float(np.median(val[valid_mask > 0])) if (valid_mask > 0).any() else 0.0
    padded = np.where(den > 1e-4, num / np.maximum(den, 1e-4), med)
    return np.where(valid_mask > 0, val, padded)


class StudioRetoucher:
    def __init__(self, device="cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        print(f"[Init] Loading Studio Retouch Models on {self.device}...")

        self.lama = torch.jit.load(LAMA_PATH, map_location=self.device).eval()
        self.face_proc = SegformerImageProcessor.from_pretrained("jonathandinu/face-parsing")
        self.face_model = SegformerForSemanticSegmentation.from_pretrained(
            "jonathandinu/face-parsing"
        ).to(self.device).eval()

        self.birefnet = AutoModelForImageSegmentation.from_pretrained(
            "ZhengPeng7/BiRefNet", trust_remote_code=True
        ).to(self.device).eval().half()
        self.biref_tf = transforms.Compose([
            transforms.Resize((1024, 1024)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        print("[Init] All models loaded successfully.")

    @torch.inference_mode()
    def get_person_mask(self, rgb_u8: np.ndarray) -> np.ndarray:
        H, W = rgb_u8.shape[:2]
        pil_im = Image.fromarray(rgb_u8)
        inp = self.biref_tf(pil_im).unsqueeze(0).to(self.device).half()
        preds = self.birefnet(inp)[-1].sigmoid().float()
        mask = F.interpolate(preds, size=(H, W), mode="bilinear", align_corners=False)[0, 0]
        return mask.cpu().numpy()

    @torch.inference_mode()
    def get_face_parsing(self, rgb_u8: np.ndarray):
        H, W = rgb_u8.shape[:2]
        pil_full = Image.fromarray(rgb_u8)
        inputs = self.face_proc(images=pil_full, return_tensors="pt").to(self.device)
        logits = self.face_model(**inputs).logits
        coarse = F.interpolate(logits, size=(512, 512), mode="bilinear", align_corners=False).argmax(dim=1)[0].cpu().numpy()

        # Restrict head search to upper 70% & largest connected head component (prevents red pasta false positives!)
        head_raw = np.isin(coarse, [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17]).astype(np.uint8)
        head_raw[int(512 * 0.68) :, :] = 0
        head_cc = largest_cc(head_raw)
        ys, xs = np.where(head_cc > 0)
        if len(xs) < 40:
            raise RuntimeError("Face not detected in image!")

        x0_c, x1_c = xs.min() / 512.0 * W, xs.max() / 512.0 * W
        y0_c, y1_c = ys.min() / 512.0 * H, ys.max() / 512.0 * H
        bw, bh = x1_c - x0_c, y1_c - y0_c
        pad = 0.25 * max(bw, bh)
        cx0 = max(0, int(x0_c - pad))
        cy0 = max(0, int(y0_c - pad))
        cx1 = min(W, int(x1_c + pad))
        cy1 = min(H, int(y1_c + pad))

        # High-res crop face parsing
        pil_crop = Image.fromarray(rgb_u8[cy0:cy1, cx0:cx1])
        inp_crop = self.face_proc(images=pil_crop, return_tensors="pt").to(self.device)
        logits_crop = self.face_model(**inp_crop).logits
        ch, cw = cy1 - cy0, cx1 - cx0
        up_logits = F.interpolate(logits_crop, size=(ch, cw), mode="bilinear", align_corners=False)
        crop_cls = up_logits.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)

        # Clean stray disconnected blobs inside crop_cls
        valid_head = largest_cc(np.isin(crop_cls, [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17]).astype(np.uint8))
        valid_head_dil = cv2.dilate(valid_head, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
        crop_cls[(valid_head_dil == 0) & (crop_cls != 18)] = 0

        cls_map = np.zeros((H, W), dtype=np.uint8)
        cls_map[cy0:cy1, cx0:cx1] = crop_cls

        face_core = largest_cc(np.isin(cls_map, [1, 2, 4, 5, 6, 7, 10, 11, 12]).astype(np.uint8))
        fys, fxs = np.where(face_core > 0)
        face_bbox = (int(fxs.min()), int(fys.min()), int(fxs.max()), int(fys.max()))
        return cls_map, face_bbox

    @torch.inference_mode()
    def lama_inpaint_crop(self, rgb_u8: np.ndarray, mask_u8: np.ndarray, pad_px: int = 96, grain_strength: float = 0.38) -> np.ndarray:
        ys, xs = np.where(mask_u8 > 0)
        if len(xs) == 0:
            return rgb_u8

        H, W = rgb_u8.shape[:2]
        out = rgb_u8.copy()

        # Fast separable rectangular dilation for clustering (0.005s instead of 60s MORPH_ELLIPSE!)
        cluster_k = cv2.getStructuringElement(cv2.MORPH_RECT, (141, 141))
        clustered = cv2.dilate((mask_u8 > 0).astype(np.uint8), cluster_k)
        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(clustered, connectivity=8)

        for lbl in range(1, num_labels):
            bx, by, bw, bh, _ = stats[lbl]
            x0 = max(0, bx - pad_px)
            y0 = max(0, by - pad_px)
            x1 = min(W, bx + bw + pad_px)
            y1 = min(H, by + bh + pad_px)

            min_side = 256
            if (x1 - x0) < min_side:
                extra = min_side - (x1 - x0)
                x0 = max(0, x0 - extra // 2)
                x1 = min(W, x0 + min_side)
                x0 = max(0, x1 - min_side)
            if (y1 - y0) < min_side:
                extra = min_side - (y1 - y0)
                y0 = max(0, y0 - extra // 2)
                y1 = min(H, y0 + min_side)
                y0 = max(0, y1 - min_side)

            sub_img = out[y0:y1, x0:x1]
            sub_msk = (mask_u8[y0:y1, x0:x1] > 0).astype(np.uint8)
            if sub_msk.sum() == 0:
                continue

            sh, sw = sub_img.shape[:2]
            ph = (8 - sh % 8) % 8
            pw = (8 - sw % 8) % 8
            if ph > 0 or pw > 0:
                sub_img_pad = cv2.copyMakeBorder(sub_img, 0, ph, 0, pw, cv2.BORDER_REFLECT_101)
                sub_msk_pad = cv2.copyMakeBorder(sub_msk, 0, ph, 0, pw, cv2.BORDER_CONSTANT, value=0)
            else:
                sub_img_pad, sub_msk_pad = sub_img, sub_msk

            img_t = torch.from_numpy(sub_img_pad).permute(2, 0, 1).unsqueeze(0).float().to(self.device) / 255.0
            msk_t = torch.from_numpy(sub_msk_pad).unsqueeze(0).unsqueeze(0).float().to(self.device)
            inpainted_t = self.lama(img_t, msk_t)[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()
            inpainted = (inpainted_t[:sh, :sw] * 255.0).astype(np.float32)

            if grain_strength > 0:
                ring_outer = cv2.dilate(sub_msk, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29)))
                ring_inner = cv2.dilate(sub_msk, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
                ring = (ring_outer > 0) & (ring_inner == 0)
                orig_f = sub_img.astype(np.float32)
                hf = orig_f - gauss_blur(orig_f, 1.3)
                if ring.sum() > 80:
                    std_ring = np.std(hf[ring], axis=0, keepdims=True).clip(0.5, 4.5)
                    std_inp = np.std((inpainted - gauss_blur(inpainted, 1.3))[sub_msk > 0], axis=0, keepdims=True).clip(0.1, 10.0)
                    need_std = np.maximum(0.0, std_ring - std_inp)
                    rng = np.random.default_rng(42 + lbl)
                    noise = rng.normal(0.0, 1.0, size=(sh, sw, 1)).astype(np.float32)
                    noise = gauss_blur(noise, 0.55) * 1.45
                    inpainted = np.clip(inpainted + noise * need_std * grain_strength, 0, 255)

            alpha = gauss_blur(sub_msk.astype(np.float32), 2.5)[..., None]
            blended = sub_img.astype(np.float32) * (1.0 - alpha) + inpainted * alpha
            out[y0:y1, x0:x1] = np.clip(np.round(blended), 0, 255).astype(np.uint8)

        return out

    def cleanup_scene_objects(self, rgb_u8: np.ndarray, face_bbox, cls_map: np.ndarray, person_mask: np.ndarray):
        H, W = rgb_u8.shape[:2]
        fx0, fy0, fx1, fy1 = face_bbox
        fw, fh = fx1 - fx0, fy1 - fy0
        out = rgb_u8.copy()
        stats_info = {"sticker": False, "mic": False, "plate_spots": 0}

        # 1. Cut-off red+white sticker at very bottom-right edge of wooden table (IMG_1335..1341 only)
        # Must touch the very bottom border (y >= 0.98*H) on warm wood table, never ketchup bowls!
        ry0, rx0 = int(0.935 * H), int(0.75 * W)
        sub_br = out[ry0:H, rx0:W]
        r_ch, g_ch, b_ch = sub_br[..., 0].astype(np.int16), sub_br[..., 1].astype(np.int16), sub_br[..., 2].astype(np.int16)
        red_core = ((r_ch > 135) & ((r_ch - g_ch) > 55) & ((r_ch - b_ch) > 45)).astype(np.uint8)
        white_rim = ((r_ch > 175) & (g_ch > 168) & (b_ch > 162) & (np.abs(r_ch - g_ch) < 28)).astype(np.uint8)
        # True wood grain has moderate B (65..135), unlike yellow french fries (high R/G, very low B < 65) or black bowls (R < 65)
        wood_like = (r_ch > 125) & (g_ch > 95) & (b_ch > 62) & ((r_ch - g_ch) < 48) & ((g_ch - b_ch) < 52)
        dark_bowl = (r_ch < 58) & (g_ch < 58) & (b_ch < 58)
        touches_bottom = red_core[-max(4, int(0.012 * H)) :, :].sum() > 80 or white_rim[-max(4, int(0.008 * H)) :, :].sum() > 120
        if touches_bottom and (red_core.sum() > 180 or white_rim.sum() > 350) and wood_like.mean() > 0.38 and dark_bowl.mean() < 0.08:
            seed = red_core if red_core.sum() > 0 else white_rim
            near_seed = cv2.dilate(seed, cv2.getStructuringElement(cv2.MORPH_RECT, (odd(0.025 * W), odd(0.025 * W))))
            sticker_all = (red_core | (white_rim & near_seed)).astype(np.uint8)
            dil_r = odd(0.014 * W)
            sticker_m = cv2.dilate(sticker_all, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil_r, dil_r)))
            full_m = np.zeros((H, W), dtype=np.uint8)
            full_m[ry0:H, rx0:W] = sticker_m
            out = self.lama_inpaint_crop(out, full_m, pad_px=int(0.045 * W), grain_strength=0.48)
            stats_info["sticker"] = True

        # 2. Small square grey wireless mic magnet on white T-shirt chest (all 19 photos)
        mx0 = max(0, int(fx0 + 0.30 * fw))
        mx1 = min(W, int(fx1 + 0.60 * fw))
        my0 = max(0, int(fy1 - 0.05 * fh))
        my1 = min(H, int(fy1 + 0.92 * fh))
        if mx1 > mx0 + 40 and my1 > my0 + 40:
            chest_rgb = out[my0:my1, mx0:mx1]
            chest_gray = cv2.cvtColor(chest_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
            chest_hsv = cv2.cvtColor(chest_rgb, cv2.COLOR_RGB2HSV)
            bg_med = gauss_blur(chest_gray, max(15.0, 0.09 * fw))
            dark_cand = ((bg_med - chest_gray > 20.0) & (chest_gray < 175.0)).astype(np.uint8)
            dark_cand = cv2.morphologyEx(dark_cand, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

            n_lbl, lbls, cstats, _ = cv2.connectedComponentsWithStats(dark_cand, connectivity=8)
            mic_local = np.zeros_like(dark_cand)
            min_s, max_s = 0.030 * fw, 0.175 * fw
            for i in range(1, n_lbl):
                bx, by, bw_i, bh_i, area_i = cstats[i]
                if not (min_s <= bw_i <= max_s and min_s <= bh_i <= max_s):
                    continue
                ar = bw_i / max(1.0, float(bh_i))
                fill = area_i / float(bw_i * bh_i)
                if not (0.55 <= ar <= 1.75 and fill >= 0.40):
                    continue
                comp = (lbls == i).astype(np.uint8)
                r_out = cv2.dilate(comp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.06 * fw), odd(0.06 * fw))))
                r_in = cv2.dilate(comp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.02 * fw), odd(0.02 * fw))))
                ring = (r_out > 0) & (r_in == 0)
                if ring.sum() < 50:
                    continue
                white_shirt_px = (chest_gray[ring] > 138.0) & (chest_hsv[..., 1][ring] < 50)
                if white_shirt_px.mean() >= 0.82:
                    mic_local |= comp

            if mic_local.sum() > 0:
                dil_m = odd(0.028 * fw)
                mic_local = cv2.dilate(mic_local, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil_m, dil_m)))
                full_mic = np.zeros((H, W), dtype=np.uint8)
                full_mic[my0:my1, mx0:mx1] = mic_local
                out = self.lama_inpaint_crop(out, full_mic, pad_px=int(0.12 * fw), grain_strength=0.42)
                stats_info["mic"] = True

        # 3. Spaghetti black plate rim cleanup (tiny crumbs + bottom red sauce drip onto matte black rim)
        py0 = int(0.56 * H)
        sub_p = out[py0:H, :]
        lab_p = cv2.cvtColor(sub_p, cv2.COLOR_RGB2LAB)
        L_p = lab_p[..., 0].astype(np.float32)
        a_p = lab_p[..., 1].astype(np.float32) - 128.0
        b_p = lab_p[..., 2].astype(np.float32) - 128.0
        chroma_p = np.hypot(a_p, b_p)

        # Matte black plate rim has low L and low chroma
        dark_plate_raw = ((L_p < 75.0) & (chroma_p < 18.0)).astype(np.uint8)
        plate_rim_cc = largest_cc(dark_plate_raw)
        if plate_rim_cc.sum() > 0.18 * (H - py0) * W:
            cnts, _ = cv2.findContours(plate_rim_cc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            plate_filled = np.zeros_like(plate_rim_cc)
            cv2.drawContours(plate_filled, cnts, -1, 1, thickness=-1)
            plate_safe = cv2.erode(plate_filled, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))

            # Identify yellow pasta noodles + red sauce (high chroma OR bright warm yellow)
            pasta_raw = ((plate_safe > 0) & ((chroma_p > 18.0) | ((L_p > 115.0) & (b_p > 10.0)))).astype(np.uint8)
            pasta_main = largest_cc(pasta_raw)
            p_cnts, _ = cv2.findContours(pasta_main, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            pasta_solid = np.zeros_like(pasta_main)
            cv2.drawContours(pasta_solid, p_cnts, -1, 1, thickness=-1)

            clean_mask_p = np.zeros_like(plate_rim_cc)

            # 3a. Tiny isolated bright/sauce specks strictly on dark rim (not broad specular reflection)
            rim_only = (plate_safe > 0) & (cv2.dilate(pasta_solid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))) == 0)
            local_L_med = gauss_blur(L_p, 9.0)
            specks = (rim_only & (((L_p - local_L_med) > 18.0) | (chroma_p > 22.0))).astype(np.uint8)
            n_sp, sp_l, sp_st, _ = cv2.connectedComponentsWithStats(specks, connectivity=8)
            max_sp_area = int((0.006 * W) ** 2)
            for s in range(1, n_sp):
                if 3 <= sp_st[s, cv2.CC_STAT_AREA] <= max_sp_area:
                    clean_mask_p |= (sp_l == s).astype(np.uint8)
                    stats_info["plate_spots"] += 1

            # 3b. Red sauce drip protruding below bottom yellow spaghetti noodles onto black rim
            noodles_bright = (pasta_solid > 0) & (L_p > 125.0) & (a_p < 18.0)
            nys, nxs = np.where(noodles_bright)
            if len(nys) > 100:
                # Smooth lower noodle boundary per column or overall morphological opening
                # Fast downscaled morphological opening for smooth pasta contour (0.002s vs 25s!)
                sh_p, sw_p = pasta_solid.shape[:2]
                ps_small = cv2.resize(pasta_solid, (sw_p // 4, sh_p // 4), interpolation=cv2.INTER_NEAREST)
                open_r = odd(0.022 * (W // 4), 5)
                ps_smooth_s = cv2.morphologyEx(ps_small, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_r, open_r)))
                pasta_smooth = cv2.resize(ps_smooth_s, (sw_p, sh_p), interpolation=cv2.INTER_NEAREST)
                red_sauce_px = (a_p > 16.0) & (L_p < 135.0)
                bot_zone_y = int(nys.min() + 0.80 * (nys.max() - nys.min()))
                drip_cand = ((pasta_solid > 0) & (pasta_smooth == 0) & red_sauce_px).astype(np.uint8)
                drip_cand[:bot_zone_y, :] = 0
                # Also catch red sauce smudges just outside noodles at the bottom
                sauce_smudge_below = ((plate_safe > 0) & (a_p > 14.0) & (L_p < 110.0)).astype(np.uint8)
                sauce_smudge_below[: int(nys.max() - 0.015 * H), :] = 0
                drip_all = (drip_cand | sauce_smudge_below).astype(np.uint8)
                n_d, d_l, d_st, _ = cv2.connectedComponentsWithStats(drip_all, connectivity=8)
                for d in range(1, n_d):
                    if 15 <= d_st[d, cv2.CC_STAT_AREA] <= int((0.025 * W) ** 2):
                        clean_mask_p |= (d_l == d).astype(np.uint8)
                        stats_info["plate_spots"] += 1

            if clean_mask_p.sum() > 0:
                clean_mask_p = cv2.dilate(clean_mask_p, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
                full_pl_m = np.zeros((H, W), dtype=np.uint8)
                full_pl_m[py0:H, :] = clean_mask_p
                out = self.lama_inpaint_crop(out, full_pl_m, pad_px=72, grain_strength=0.25)

        return out, stats_info

    def build_skin_and_feature_masks(self, rgb_u8: np.ndarray, cls_map: np.ndarray, person_mask: np.ndarray, face_bbox):
        H, W = rgb_u8.shape[:2]
        fx0, fy0, fx1, fy1 = face_bbox
        fw, fh = fx1 - fx0, fy1 - fy0

        face_skin = np.isin(cls_map, [1, 2]).astype(np.uint8)
        neck_skin = (cls_map == 17).astype(np.uint8)
        ears_skin = np.isin(cls_map, [8, 9]).astype(np.uint8)
        eyes = np.isin(cls_map, [4, 5]).astype(np.uint8)
        brows = np.isin(cls_map, [6, 7]).astype(np.uint8)
        mouth_in = (cls_map == 10).astype(np.uint8)
        lips = np.isin(cls_map, [11, 12]).astype(np.uint8)
        hair = (cls_map == 13).astype(np.uint8)

        # Protect dark nostril openings
        nose_m = (cls_map == 2)
        nostrils = np.zeros((H, W), dtype=np.uint8)
        nys, nxs = np.where(nose_m)
        if len(nys) > 20:
            ny_cut = int(nys.min() + 0.62 * (nys.max() - nys.min()))
            gray = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2GRAY)
            p16 = np.percentile(gray[face_skin > 0], 16)
            sub_nos = np.zeros_like(nostrils)
            sub_nos[ny_cut : nys.max() + 1, nxs.min() : nxs.max() + 1] = 1
            nostrils = ((sub_nos > 0) & nose_m & (gray < min(105, p16 * 0.85))).astype(np.uint8)

        # Detect arm & hand skin inside BiRefNet person mask (wider tolerance so shadowed hands match face!)
        lab = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2LAB).astype(np.float32)
        skin_ref_px = lab[(face_skin > 0) | (neck_skin > 0)]
        med_L, med_a, med_b = np.median(skin_ref_px, axis=0)

        non_arm = (cls_map > 0)
        person_bin = (person_mask > 0.5)
        dist_ab = np.hypot(lab[..., 1] - med_a, lab[..., 2] - med_b)
        chroma_all = np.hypot(lab[..., 1] - 128.0, lab[..., 2] - 128.0)
        arm_cand = (
            person_bin
            & (~non_arm)
            & (dist_ab < 15.5)
            & (chroma_all > 9.5)
            & (lab[..., 0] > max(55.0, med_L - 78.0))
            & (lab[..., 0] < min(245.0, med_L + 55.0))
            & ((lab[..., 2] - 128.0) > 5.0)
        ).astype(np.uint8)
        arm_cand[int(0.82 * H) :, :] = 0
        arm_cand = cv2.morphologyEx(arm_cand, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        n_arm, arm_l, arm_st, _ = cv2.connectedComponentsWithStats(arm_cand, connectivity=8)
        arm_skin = np.zeros((H, W), dtype=np.uint8)
        for i in range(1, n_arm):
            if arm_st[i, cv2.CC_STAT_AREA] > int((0.03 * fw) ** 2):
                arm_skin |= (arm_l == i).astype(np.uint8)

        # Merge face + neck without eroding jaw contour so borderline jawline moles are 100% covered!
        merged_head_skin = ((face_skin > 0) | (neck_skin > 0)).astype(np.uint8)
        heal_head = merged_head_skin.copy()
        heal_arm = cv2.erode(arm_skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.008 * fw, 5), odd(0.008 * fw, 5))))
        heal_skin = (heal_head | heal_arm).astype(np.uint8)

        # Generous horizontal brow guard to protect sparse outer eyebrow tail hairs!
        brow_guard = cv2.dilate(brows, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.048 * fw, 15), odd(0.022 * fw, 9))))
        excl_strong = ((eyes > 0) | (mouth_in > 0) | (lips > 0) | (nostrils > 0)).astype(np.uint8)
        excl_mid = ((hair > 0) | (ears_skin > 0)).astype(np.uint8)

        r_st = odd(0.018 * fw, 7)
        r_md = odd(0.008 * fw, 5)
        heal_skin[brow_guard > 0] = 0
        heal_skin[cv2.dilate(excl_strong, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r_st, r_st))) > 0] = 0
        heal_skin[cv2.dilate(excl_mid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r_md, r_md))) > 0] = 0

        return {
            "face_skin": face_skin,
            "neck_skin": neck_skin,
            "ears_skin": ears_skin,
            "arm_skin": arm_skin,
            "all_skin": ((face_skin > 0) | (neck_skin > 0) | (ears_skin > 0) | (arm_skin > 0)).astype(np.uint8),
            "heal_skin": heal_skin,
            "brow_guard": brow_guard,
            "eyes": eyes,
            "l_eye": (cls_map == 4).astype(np.uint8),
            "r_eye": (cls_map == 5).astype(np.uint8),
            "brows": brows,
            "mouth_in": mouth_in,
            "lips": lips,
            "hair": hair,
            "nostrils": nostrils,
        }

    def heal_skin_blemishes(self, rgb_u8: np.ndarray, masks: dict, face_bbox):
        """Fast spot-heal for moles, pimples, red acne marks, blackheads & stray neck hairs."""
        H, W = rgb_u8.shape[:2]
        fx0, fy0, fx1, fy1 = face_bbox
        fw = fx1 - fx0
        heal_skin = masks["heal_skin"]

        ys, xs = np.where(heal_skin > 0)
        if len(xs) < 100:
            return rgb_u8, 0

        pad = int(0.05 * fw)
        x0, y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
        x1, y1 = min(W, xs.max() + pad), min(H, ys.max() + pad)

        sub_rgb = rgb_u8[y0:y1, x0:x1]
        sub_heal = heal_skin[y0:y1, x0:x1]
        sub_neck = masks["neck_skin"][y0:y1, x0:x1]
        valid_skin = (
            (masks["all_skin"][y0:y1, x0:x1] > 0)
            & (masks["eyes"][y0:y1, x0:x1] == 0)
            & (masks["lips"][y0:y1, x0:x1] == 0)
            & (masks["mouth_in"][y0:y1, x0:x1] == 0)
            & (masks["brow_guard"][y0:y1, x0:x1] == 0)
            & (masks["hair"][y0:y1, x0:x1] == 0)
        ).astype(np.uint8)

        lab = cv2.cvtColor(sub_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
        L = lab[..., 0] * (100.0 / 255.0)
        a = lab[..., 1] - 128.0

        # Fast normalized Gaussian extrapolation outside valid_skin (0.02s instead of 300s Telea!)
        ext_sig = max(6.0, 0.015 * fw)
        L_filled = extrapolate_masked_channel(L, valid_skin, ext_sig)
        a_filled = extrapolate_masked_channel(a, valid_skin, ext_sig)

        d1 = odd(0.016 * fw, 7)
        d2 = odd(0.032 * fw, 13)
        se1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d1, d1))
        se2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d2, d2))

        L_s = gauss_blur(L_filled, max(0.8, 0.0016 * fw))
        a_s = gauss_blur(a_filled, max(1.0, 0.0020 * fw))

        dark_bh1 = cv2.morphologyEx(L_s, cv2.MORPH_BLACKHAT, se1)
        dark_bh2 = cv2.morphologyEx(L_s, cv2.MORPH_BLACKHAT, se2)
        dark_score = np.maximum(dark_bh1, 0.90 * dark_bh2)

        red_th1 = cv2.morphologyEx(a_s, cv2.MORPH_TOPHAT, se1)
        red_th2 = cv2.morphologyEx(a_s, cv2.MORPH_TOPHAT, se2)
        red_score = np.maximum(red_th1, 0.85 * red_th2)

        se_tiny = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.011 * fw, 5), odd(0.011 * fw, 5)))
        bright_th = cv2.morphologyEx(L_s, cv2.MORPH_TOPHAT, se_tiny)

        # Also catch thin dark stray hairs lying on neck/collarbone skin
        se_hair = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (odd(0.008 * fw, 5), odd(0.008 * fw, 5)))
        neck_hair_bh = cv2.morphologyEx(L, cv2.MORPH_BLACKHAT, se_hair)
        stray_neck_hair = (sub_neck > 0) & (sub_heal > 0) & (neck_hair_bh > 2.4)

        cand = (
            ((sub_heal > 0) & (
                (dark_score > 2.75)
                | (red_score > 2.10)
                | ((dark_score > 1.90) & (red_score > 1.40))
                | ((bright_th > 4.2) & (L_s < 83.0))
            ))
            | stray_neck_hair
        ).astype(np.uint8)

        cand = cv2.morphologyEx(cand, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        cand = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

        n_c, c_lbl, c_stats, _ = cv2.connectedComponentsWithStats(cand, connectivity=8)
        accepted = np.zeros_like(cand)
        min_area = max(5, int((0.0026 * fw) ** 2))
        max_area = int((0.038 * fw) ** 2)
        spot_count = 0

        for idx in range(1, n_c):
            area = c_stats[idx, cv2.CC_STAT_AREA]
            if area < min_area or area > max_area:
                continue
            comp = (c_lbl == idx)
            peak_dark = float(dark_score[comp].max())
            peak_red = float(red_score[comp].max())
            on_neck = float(sub_neck[comp].mean()) > 0.5

            cys, cxs = np.where(comp)
            if len(cxs) >= 12:
                pts = np.stack([cxs.astype(np.float32), cys.astype(np.float32)], axis=1)
                cov = np.cov(pts, rowvar=False)
                eigvals = np.linalg.eigvalsh(cov)
                elong = math.sqrt(max(eigvals[1], 1e-3) / max(eigvals[0], 1e-3))
                minor_w = 2.0 * math.sqrt(max(eigvals[0], 1e-3))
            else:
                elong, minor_w = 1.0, 2.0

            # Allow thin stray hairs on neck (minor_w < 0.012*fw), spare broad neck creases & smile folds
            if on_neck and minor_w < 0.012 * fw and peak_dark > 2.2:
                max_elong = 9.0
            elif peak_dark > 7.5 or peak_red > 4.0:
                max_elong = 3.8
            else:
                max_elong = 2.65

            if elong <= max_elong:
                accepted |= comp.astype(np.uint8)
                spot_count += 1

        if spot_count == 0:
            return rgb_u8, 0

        # Extra dilation for strong dark moles so zero dark halo remains
        strong_moles = (accepted > 0) & (dark_score > 6.0)
        dil_s = odd(0.0085 * fw, 7)
        accepted_dil = cv2.dilate(accepted, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil_s, dil_s)))
        if strong_moles.any():
            dil_mole = odd(0.016 * fw, 11)
            accepted_dil |= cv2.dilate(strong_moles.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil_mole, dil_mole)))
        accepted_dil &= (
            (masks["eyes"][y0:y1, x0:x1] == 0)
            & (masks["lips"][y0:y1, x0:x1] == 0)
            & (masks["mouth_in"][y0:y1, x0:x1] == 0)
            & (masks["nostrils"][y0:y1, x0:x1] == 0)
            & (masks["brow_guard"][y0:y1, x0:x1] == 0)
        ).astype(np.uint8)

        full_spot_mask = np.zeros((H, W), dtype=np.uint8)
        full_spot_mask[y0:y1, x0:x1] = accepted_dil
        healed = self.lama_inpaint_crop(rgb_u8, full_spot_mask, pad_px=int(0.10 * fw), grain_strength=0.58)
        return healed, spot_count

    def retouch_skin_fs(self, rgb_u8: np.ndarray, masks: dict, face_bbox):
        """
        Natural Studio 3-Band Frequency Separation + Under-Eye Softening
        + Oily Shine Matte-Satin Control + Shallow-DOF Clarity Recovery.
        """
        H, W = rgb_u8.shape[:2]
        fx0, fy0, fx1, fy1 = face_bbox
        fw, fh = fx1 - fx0, fy1 - fy0

        img_f = rgb_u8.astype(np.float32) / 255.0

        detail_guard = (
            (masks["eyes"] > 0)
            | (masks["brow_guard"] > 0)
            | (masks["lips"] > 0)
            | (masks["mouth_in"] > 0)
            | (masks["hair"] > 0)
            | (masks["nostrils"] > 0)
        ).astype(np.float32)
        detail_guard = gauss_blur(detail_guard, 0.005 * fw)

        w_face = gauss_blur(masks["face_skin"].astype(np.float32), 0.008 * fw) * (1.0 - detail_guard)
        w_neck = gauss_blur(masks["neck_skin"].astype(np.float32), 0.010 * fw) * (1.0 - detail_guard)
        w_arm = gauss_blur(masks["arm_skin"].astype(np.float32), 0.010 * fw)

        sig_fine = max(1.2, 0.0028 * fw)
        sig_mid = max(3.5, 0.0092 * fw)

        blur_fine = gauss_blur(img_f, sig_fine)
        lf_base = gauss_blur(img_f, sig_mid)

        hf_fine = img_f - blur_fine
        hf_mid = blur_fine - lf_base

        # Balanced studio tone evening (0.56 instead of 0.68 -> smooth & clean, zero powdery/plastic look!)
        half_lf = cv2.resize(lf_base, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
        d_bi = odd(0.060 * (fw * 0.5), 9)
        smooth_half = cv2.bilateralFilter(half_lf, d=d_bi, sigmaColor=0.065, sigmaSpace=max(12.0, 0.050 * (fw * 0.5)))
        lf_even = cv2.resize(smooth_half, (W, H), interpolation=cv2.INTER_CUBIC)

        tone_blend = np.clip(0.56 * w_face + 0.48 * w_neck + 0.40 * w_arm, 0.0, 0.60)[..., None]
        lf_new = lf_base * (1.0 - tone_blend) + lf_even * tone_blend

        lf_u8 = np.clip(np.round(lf_new * 255.0), 0, 255).astype(np.uint8)
        lf_lab = cv2.cvtColor(lf_u8, cv2.COLOR_RGB2LAB).astype(np.float32)
        L_lf = lf_lab[..., 0] * (100.0 / 255.0)
        a_lf = lf_lab[..., 1] - 128.0
        b_lf = lf_lab[..., 2] - 128.0

        # 1) Under-eye tear-trough / dark circle brightening
        for eye_key in ["l_eye", "r_eye"]:
            eys, exs = np.where(masks[eye_key] > 0)
            if len(exs) < 25:
                continue
            ex0, ex1 = exs.min(), exs.max()
            ey0, ey1 = eys.min(), eys.max()
            ew = ex1 - ex0
            eh = max(ey1 - ey0, int(0.035 * fh))

            ux0 = max(0, int(ex0 - 0.16 * ew))
            ux1 = min(W, int(ex1 + 0.16 * ew))
            uy0 = min(H, int(ey1 + 0.14 * eh))
            uy1 = min(H, int(ey1 + 1.50 * eh))

            cy0_r = min(H, int(ey1 + 1.60 * eh))
            cy1_r = min(H, int(ey1 + 2.90 * eh))
            if uy1 > uy0 + 6 and cy1_r > cy0_r + 6:
                cheek_patch = (masks["face_skin"][cy0_r:cy1_r, ux0:ux1] > 0)
                if cheek_patch.sum() > 40:
                    ref_L = float(np.percentile(L_lf[cy0_r:cy1_r, ux0:ux1][cheek_patch], 60))
                    ref_a = float(np.median(a_lf[cy0_r:cy1_r, ux0:ux1][cheek_patch]))
                    cres = np.zeros((H, W), dtype=np.float32)
                    cres[uy0:uy1, ux0:ux1] = 1.0
                    cres = gauss_blur(cres, 0.022 * fw) * w_face
                    deficit = np.clip(ref_L - L_lf, 0.0, 11.0)
                    L_lf += cres * np.minimum(deficit * 0.42, 4.2)
                    a_deficit = np.clip(ref_a - a_lf, 0.0, 4.5)
                    a_lf += cres * (a_deficit * 0.32)

        # 2) Oily Forehead / Nose Specular Glare Compression
        fs_bool = (masks["face_skin"] > 0)
        if fs_bool.sum() > 200:
            p85 = float(np.percentile(L_lf[fs_bool], 85))
            med_a_skin = float(np.median(a_lf[fs_bool]))
            med_b_skin = float(np.median(b_lf[fs_bool]))
            chroma_lf = np.hypot(a_lf, b_lf)
            med_c_skin = float(np.median(chroma_lf[fs_bool]))

            excess_L = np.maximum(0.0, L_lf - p85)
            low_c_weight = np.clip((med_c_skin * 1.05 - chroma_lf) / max(4.0, med_c_skin * 0.45), 0.25, 1.0)
            shine_w = w_face * low_c_weight * np.clip(excess_L / 10.0, 0.0, 1.0)

            L_lf -= shine_w * (excess_L * 0.44)
            a_lf = a_lf * (1.0 - 0.34 * shine_w) + med_a_skin * (0.34 * shine_w)
            b_lf = b_lf * (1.0 - 0.34 * shine_w) + med_b_skin * (0.34 * shine_w)

        lf_lab_out = np.stack([
            np.clip(L_lf * (255.0 / 100.0), 0, 255),
            np.clip(a_lf + 128.0, 0, 255),
            np.clip(b_lf + 128.0, 0, 255),
        ], axis=-1).astype(np.uint8)
        lf_toned = cv2.cvtColor(lf_lab_out, cv2.COLOR_LAB2RGB).astype(np.float32) / 255.0

        # Recombine natural masculine pore texture (92% crisp fine pores + 44% clamped mid texture)
        skin_total_w = np.clip(w_face + 0.75 * w_neck + 0.55 * w_arm, 0.0, 1.0)[..., None]
        hf_mid_clamped = np.tanh(hf_mid / 0.032) * 0.032
        hf_skin = 0.92 * hf_fine + 0.44 * hf_mid_clamped
        hf_orig = hf_fine + hf_mid
        hf_final = hf_orig * (1.0 - skin_total_w) + hf_skin * skin_total_w

        out_f = np.clip(lf_toned + hf_final, 0.0, 1.0)

        # Shallow-DOF Facial Clarity Recovery (for IMG_1342..1350 where focus locked on foreground pasta)
        feat_roi = ((masks["eyes"] > 0) | (masks["brows"] > 0) | (masks["lips"] > 0))
        if feat_roi.sum() > 100:
            norm_scale = 600.0 / max(200.0, float(fw))
            face_crop = cv2.resize(rgb_u8[fy0:fy1, fx0:fx1], (0, 0), fx=norm_scale, fy=norm_scale, interpolation=cv2.INTER_AREA)
            gray_fc = cv2.cvtColor(face_crop, cv2.COLOR_RGB2GRAY).astype(np.float32)
            lap_var = float(cv2.Laplacian(gray_fc, cv2.CV_32F).var())
            if lap_var < 105.0:
                boost = np.clip((105.0 - lap_var) / 68.0, 0.18, 0.62)
                usm_detail = out_f - gauss_blur(out_f, max(1.5, 0.0038 * fw))
                feat_w = gauss_blur(((masks["eyes"] > 0) | (masks["brow_guard"] > 0) | (masks["lips"] > 0) | (masks["mouth_in"] > 0) | (masks["hair"] > 0)).astype(np.float32), 0.008 * fw)
                head_w = np.clip(feat_w * 0.88 + w_face * 0.24, 0.0, 0.92)[..., None]
                out_f = np.clip(out_f + usm_detail * (boost * head_w), 0.0, 1.0)

        return np.clip(np.round(out_f * 255.0), 0, 255).astype(np.uint8)

    def polish_smile_and_eyes(self, rgb_u8: np.ndarray, masks: dict, face_bbox) -> np.ndarray:
        fw = face_bbox[2] - face_bbox[0]
        lab = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2LAB).astype(np.float32)
        L = lab[..., 0] * (100.0 / 255.0)
        a = lab[..., 1] - 128.0
        b = lab[..., 2] - 128.0

        mouth_m = (masks["mouth_in"] > 0)
        if mouth_m.sum() > 30:
            teeth_raw = (mouth_m & (L > 36.0) & (a < 13.5)).astype(np.float32)
            teeth_w = gauss_blur(teeth_raw, max(1.2, 0.0025 * fw))
            new_b = np.maximum(3.0, b * 0.48)
            b = b * (1.0 - teeth_w) + np.minimum(b, new_b) * teeth_w
            new_a = a * 0.68
            a = a * (1.0 - teeth_w) + new_a * teeth_w
            lift_L = np.clip((87.5 - L) * 0.15, 0.0, 6.2)
            L += teeth_w * lift_L

        lips_w = gauss_blur(masks["lips"].astype(np.float32), max(1.5, 0.0035 * fw))
        if lips_w.max() > 0.1:
            med_lip_a = float(np.median(a[masks["lips"] > 0]))
            if med_lip_a < 19.5:
                a += lips_w * min(2.4, (19.5 - med_lip_a) * 0.40)
            L += lips_w * 0.9

        eyes_w = gauss_blur(masks["eyes"].astype(np.float32), max(1.0, 0.002 * fw))
        if eyes_w.max() > 0.1:
            local_L = gauss_blur(L, max(2.0, 0.006 * fw))
            L += eyes_w * ((L - local_L) * 0.22 + 1.3)

        lab_out = np.stack([
            np.clip(L * (255.0 / 100.0), 0, 255),
            np.clip(a + 128.0, 0, 255),
            np.clip(b + 128.0, 0, 255),
        ], axis=-1).astype(np.uint8)
        return cv2.cvtColor(lab_out, cv2.COLOR_LAB2RGB)

    def grade_commercial_fresh(self, rgb_u8: np.ndarray, masks: dict, person_mask: np.ndarray, cls_map: np.ndarray) -> np.ndarray:
        H, W = rgb_u8.shape[:2]
        img_f = rgb_u8.astype(np.float32) / 255.0

        lab_in = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2LAB).astype(np.float32)
        L_in = lab_in[..., 0] * (100.0 / 255.0)
        skin_med_L = float(np.median(L_in[masks["face_skin"] > 0]))
        need_lift = np.clip((68.5 - skin_med_L) / 28.0, 0.09, 0.25)

        x = img_f
        lifted = x + need_lift * x * (1.0 - x) * (1.35 - 0.55 * x)
        contrasted = lifted + 0.036 * np.sin(np.pi * (lifted - 0.5)) * (1.0 - np.abs(2.0 * lifted - 1.0))
        img_f = np.clip(contrasted, 0.0, 1.0)

        graded_u8 = np.clip(np.round(img_f * 255.0), 0, 255).astype(np.uint8)
        lab = cv2.cvtColor(graded_u8, cv2.COLOR_RGB2LAB).astype(np.float32)
        L = lab[..., 0] * (100.0 / 255.0)
        a = lab[..., 1] - 128.0
        b = lab[..., 2] - 128.0

        # Healthy warm-rosy Vietnamese skin tone (face + neck + arms harmonized!)
        skin_w = gauss_blur(masks["all_skin"].astype(np.float32), 6.0)
        arm_w = gauss_blur(masks["arm_skin"].astype(np.float32), 8.0)

        cur_a = float(np.median(a[masks["face_skin"] > 0]))
        cur_b = float(np.median(b[masks["face_skin"] > 0]))
        cur_L = float(np.median(L[masks["face_skin"] > 0]))

        shift_b = np.clip(16.6 - cur_b, -3.2, 1.2)
        shift_a = np.clip(12.6 - cur_a, -1.5, 2.2)
        shift_L = np.clip(69.0 - cur_L, 0.0, 2.6)

        L += skin_w * shift_L * np.clip((92.0 - L) / 30.0, 0.0, 1.0)
        a += skin_w * shift_a
        b += skin_w * shift_b

        # Harmonize arm/hand brightness if shadowed compared to face
        if (masks["arm_skin"] > 0).sum() > 200:
            arm_med_L = float(np.median(L[masks["arm_skin"] > 0]))
            face_new_L = float(np.median(L[masks["face_skin"] > 0]))
            arm_lift = np.clip((face_new_L - 1.5 - arm_med_L) * 0.55, 0.0, 4.2)
            L += arm_w * arm_lift

        # Crisp Studio-White T-Shirt
        chroma = np.hypot(a, b)
        shirt_raw = (
            (person_mask > 0.5)
            & (masks["all_skin"] == 0)
            & (masks["hair"] == 0)
            & (masks["lips"] == 0)
            & (masks["mouth_in"] == 0)
            & (L > 52.0)
            & (chroma < 14.0)
        ).astype(np.float32)
        shirt_w = gauss_blur(shirt_raw, 4.0)
        b = b * (1.0 - 0.58 * shirt_w)
        a = a * (1.0 - 0.45 * shirt_w)
        L += shirt_w * np.clip((95.0 - L) * 0.08, 0.0, 2.8)

        # Appetizing Food Vibrance & Micro-Contrast
        yy = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
        lower_zone = np.clip((yy - 0.48) / 0.14, 0.0, 1.0)
        food_w = lower_zone * (1.0 - skin_w) * (1.0 - shirt_w) * np.clip((chroma - 8.0) / 14.0, 0.0, 1.0)

        vib_gain = 1.0 + 0.20 * food_w * np.clip(1.0 - chroma / 78.0, 0.15, 1.0)
        a *= vib_gain
        b *= vib_gain

        bg_vib = 1.0 + 0.07 * (1.0 - skin_w) * (1.0 - shirt_w) * np.clip(1.0 - chroma / 70.0, 0.0, 1.0)
        a *= bg_vib
        b *= bg_vib

        L_blur_food = gauss_blur(L, max(2.5, 0.0025 * W))
        L += food_w * (L - L_blur_food) * 0.16

        lab_final = np.stack([
            np.clip(L * (255.0 / 100.0), 0, 255),
            np.clip(a + 128.0, 0, 255),
            np.clip(b + 128.0, 0, 255),
        ], axis=-1).astype(np.uint8)
        return cv2.cvtColor(lab_final, cv2.COLOR_LAB2RGB)

    def process_one(self, img_path: str):
        t0 = time.time()
        rgb_orig = np.array(Image.open(img_path).convert("RGB"))

        person_mask = self.get_person_mask(rgb_orig)
        cls_map, face_bbox = self.get_face_parsing(rgb_orig)

        step1, scene_stats = self.cleanup_scene_objects(rgb_orig, face_bbox, cls_map, person_mask)
        masks = self.build_skin_and_feature_masks(step1, cls_map, person_mask, face_bbox)
        step2, n_spots = self.heal_skin_blemishes(step1, masks, face_bbox)
        step3 = self.retouch_skin_fs(step2, masks, face_bbox)
        step4 = self.polish_smile_and_eyes(step3, masks, face_bbox)
        final_rgb = self.grade_commercial_fresh(step4, masks, person_mask, cls_map)

        dt = time.time() - t0
        info = {"time_s": round(dt, 2), "spots_healed": n_spots, **scene_stats, "face_bbox": face_bbox}
        return rgb_orig, final_rgb, info


def save_jpg_srgb(rgb_u8: np.ndarray, out_path: str, quality: int = 98):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    Image.fromarray(rgb_u8).save(out_path, format="JPEG", quality=quality, subsampling=0, optimize=True, icc_profile=SRGB_ICC)


def save_before_after_debug(name: str, before: np.ndarray, after: np.ndarray, face_bbox):
    H, W = before.shape[:2]
    fx0, fy0, fx1, fy1 = face_bbox
    fw, fh = fx1 - fx0, fy1 - fy0

    cx0 = max(0, int(fx0 - 0.25 * fw))
    cx1 = min(W, int(fx1 + 0.35 * fw))
    cy0 = max(0, int(fy0 - 0.22 * fh))
    cy1 = min(H, int(fy1 + 0.65 * fh))

    b_face = before[cy0:cy1, cx0:cx1]
    a_face = after[cy0:cy1, cx0:cx1]
    scale = min(1.0, 1400.0 / b_face.shape[0])
    if scale < 1.0:
        nh, nw = int(b_face.shape[0] * scale), int(b_face.shape[1] * scale)
        b_face = cv2.resize(b_face, (nw, nh), interpolation=cv2.INTER_AREA)
        a_face = cv2.resize(a_face, (nw, nh), interpolation=cv2.INTER_AREA)

    comp_face = np.concatenate([b_face, a_face], axis=1)
    save_jpg_srgb(comp_face, os.path.join(TEST_DIR, f"{name}_face_BA.jpg"), quality=95)

    th = 1500
    tw = int(W * (th / float(H)))
    b_full = cv2.resize(before, (tw, th), interpolation=cv2.INTER_AREA)
    a_full = cv2.resize(after, (tw, th), interpolation=cv2.INTER_AREA)
    comp_full = np.concatenate([b_full, a_full], axis=1)
    save_jpg_srgb(comp_full, os.path.join(TEST_DIR, f"{name}_full_BA.jpg"), quality=94)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    retoucher = StudioRetoucher()

    if mode == "test":
        for nm in ["IMG_1336", "IMG_1346", "IMG_1352"]:
            p = os.path.join(RAW_DIR, f"{nm}.png")
            orig, res, meta = retoucher.process_one(p)
            print(f"[TEST] {nm}: {meta}")
            save_before_after_debug(nm, orig, res, meta["face_bbox"])
            save_jpg_srgb(res, os.path.join(TEST_DIR, f"{nm}_retouched.jpg"))
    elif mode in ("all", "fix_subset"):
        os.makedirs(OUT_FINAL_DIR, exist_ok=True)
        files = sorted(glob.glob(os.path.join(RAW_DIR, "IMG_*.png")))
        subset = {f"IMG_{n}" for n in range(1335, 1345)}
        report_path = os.path.join(TEST_DIR, "batch_report.json")
        all_meta = json.load(open(report_path, encoding="utf-8")) if (mode == "fix_subset" and os.path.exists(report_path)) else {}
        thumbs_ba = []
        for idx, p in enumerate(files, 1):
            nm = os.path.splitext(os.path.basename(p))[0]
            out_jpg = os.path.join(OUT_FINAL_DIR, f"{nm}.jpg")
            if mode == "fix_subset" and nm not in subset and os.path.exists(out_jpg):
                orig = np.array(Image.open(p).convert("RGB"))
                res = np.array(Image.open(out_jpg).convert("RGB"))
                print(f"[{idx:02d}/{len(files):02d}] {nm}.jpg kept (already verified)", flush=True)
            else:
                orig, res, meta = retoucher.process_one(p)
                save_jpg_srgb(res, out_jpg, quality=98)
                all_meta[nm] = meta
                print(f"[{idx:02d}/{len(files):02d}] {nm}.jpg saved -> {meta}", flush=True)

            # Build Before/After pair thumbnail for 19-photo QA contact sheet
            th = 560
            tw = int(orig.shape[1] * (th / float(orig.shape[0])))
            bo = cv2.resize(orig, (tw, th), interpolation=cv2.INTER_AREA)
            af = cv2.resize(res, (tw, th), interpolation=cv2.INTER_AREA)
            pair = np.concatenate([bo, af], axis=1)
            cv2.putText(pair, f"{nm} (Before | Retouch)", (14, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(pair, f"{nm} (Before | Retouch)", (14, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 230, 80), 2, cv2.LINE_AA)
            thumbs_ba.append(pair)

        # Save 4-col x 5-row QA Contact Sheet
        cols = 4
        rows = math.ceil(len(thumbs_ba) / cols)
        pw_t, ph_t = thumbs_ba[0].shape[1], thumbs_ba[0].shape[0]
        grid = np.zeros((rows * ph_t, cols * pw_t, 3), dtype=np.uint8) + 24
        for i, tile in enumerate(thumbs_ba):
            r, c = divmod(i, cols)
            grid[r * ph_t : (r + 1) * ph_t, c * pw_t : (c + 1) * pw_t] = tile
        save_jpg_srgb(grid, os.path.join(TEST_DIR, "00_QA_19_BEFORE_AFTER_SHEET.jpg"), quality=92)

        with open(os.path.join(TEST_DIR, "batch_report.json"), "w", encoding="utf-8") as f:
            json.dump(all_meta, f, indent=2, ensure_ascii=False)
