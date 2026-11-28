# -*- coding: utf-8 -*-
import os, sys, shutil, subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import pytoshop
from pytoshop.user import nested_layers
from pytoshop import enums

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJ    = Path(r"C:\AI\full studio\projects\feelchicken_3posts_redesign_v2")
REF_DIR = PROJ / "refs"
RAW_DIR = PROJ / "raw"
OUT_DIR = PROJ / "XUAT_3_BAI_MOI_CHUAN_STUDIO"
SCR_DIR = Path(r"C:\Users\001\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch\redesign_3posts")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SCR_DIR.mkdir(parents=True, exist_ok=True)

LOGO_RGBA = cv2.imread(str(REF_DIR / "fc_logo_rgba.png"), cv2.IMREAD_UNCHANGED)  # BGRA

def unsharp_crisp(bgr: np.ndarray, target_size: tuple[int, int], amount: float = 0.18) -> np.ndarray:
    rs = cv2.resize(bgr, target_size, interpolation=cv2.INTER_LANCZOS4)
    bl = cv2.GaussianBlur(rs, (0, 0), 1.15)
    return cv2.addWeighted(rs, 1.0 + amount, bl, -amount, 0)

def save_png_rgb(bgr: np.ndarray, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    Image.fromarray(rgb).save(dst, "PNG", optimize=True)

def expand_3x2_to_clean_2x1(bgr_3x2: np.ndarray, out_w: int = 2160, out_h: int = 1080) -> np.ndarray:
    """
    Preserves 100% vertical height of a 3:2 banner (0% top/bottom crop on logo or footer!)
    while seamlessly extending atmospheric blurred/textured side margins to 2:1 (2160x1080)
    with a wide cosine feather blend + subtle dark edge vignette.
    """
    inner_w = int(round(out_h * (bgr_3x2.shape[1] / bgr_3x2.shape[0])))  # 1620px for 1080p height
    inner = unsharp_crisp(bgr_3x2, (inner_w, out_h), 0.18)
    pad_l = (out_w - inner_w) // 2  # 270px each side

    # Build atmospheric ambient background from stretched + softly blurred + darkened outer strips
    bg = cv2.resize(bgr_3x2, (out_w, out_h), interpolation=cv2.INTER_CUBIC)
    bg = cv2.GaussianBlur(bg, (0, 0), 26.0)
    bg = (bg.astype(np.float32) * 0.62).astype(np.uint8)

    # Mirror-extend 320px edge texture from inner with strong blur so color/lighting matches 100% seamlessly
    strip_w = pad_l + 90
    left_tex  = cv2.flip(inner[:, :strip_w], 1)
    right_tex = cv2.flip(inner[:, -strip_w:], 1)
    left_tex  = cv2.GaussianBlur(left_tex, (0, 0), 18.0)
    right_tex = cv2.GaussianBlur(right_tex, (0, 0), 18.0)
    # Darken outer margins gracefully like studio vignette so eye stays on the main composition
    grad_l = np.linspace(0.48, 0.96, strip_w, dtype=np.float32)[None, :, None]
    grad_r = np.linspace(0.96, 0.48, strip_w, dtype=np.float32)[None, :, None]
    bg[:, :strip_w]  = np.clip(left_tex.astype(np.float32) * grad_l, 0, 255).astype(np.uint8)
    bg[:, -strip_w:] = np.clip(right_tex.astype(np.float32) * grad_r, 0, 255).astype(np.uint8)

    # Smooth 76px cosine feather blend at x = pad_l and x = pad_l + inner_w
    feather = 76
    mask = np.zeros((out_h, inner_w), dtype=np.float32) + 1.0
    ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, feather, dtype=np.float32))
    mask[:, :feather]  = ramp[None, :]
    mask[:, -feather:] = ramp[::-1][None, :]

    roi = bg[:, pad_l : pad_l + inner_w].astype(np.float32)
    bg[:, pad_l : pad_l + inner_w] = np.clip(
        inner.astype(np.float32) * mask[:, :, None] + roi * (1.0 - mask[:, :, None]), 0, 255
    ).astype(np.uint8)
    return bg

def stamp_exact_logo_on_p1_02(bgr: np.ndarray) -> np.ndarray:
    """Replaces P1_02's plain 'FEEL' emblem inside the top-left cream brush splash with official fc_logo_rgba.png."""
    H, W = bgr.shape[:2]
    out = bgr.copy()
    # Sample warm parchment color inside the brush splash around the old logo
    patch_color = np.median(out[int(H*0.02):int(H*0.06), int(W*0.14):int(W*0.19)].reshape(-1, 3), axis=0).astype(np.float32)
    mask = np.zeros((H, W), dtype=np.uint8)
    pts = np.array([
        [int(W*0.015), int(H*0.008)],
        [int(W*0.182), int(H*0.008)],
        [int(W*0.186), int(H*0.145)],
        [int(W*0.025), int(H*0.165)],
    ], dtype=np.int32)
    cv2.fillPoly(mask, [pts], 255)
    # Inpaint + warm parchment blend
    inp = cv2.inpaint(out, mask, 9, cv2.INPAINT_TELEA)
    mf = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (19, 19), 5.0)[:, :, None]
    blended_patch = inp.astype(np.float32) * 0.35 + patch_color[None, None, :] * 0.65
    out = np.clip(out.astype(np.float32) * (1.0 - mf) + blended_patch * mf, 0, 255).astype(np.uint8)

    # Composite crisp official fc_logo_rgba.png
    lh, lw = LOGO_RGBA.shape[:2]
    tw = int(W * 0.162)
    th = int(round(lh * tw / lw))
    lrs = cv2.resize(LOGO_RGBA, (tw, th), interpolation=cv2.INTER_AREA)
    lx, ly = int(W * 0.018), int(H * 0.012)
    al = lrs[:, :, 3:4].astype(np.float32) / 255.0
    out[ly:ly+th, lx:lx+tw] = np.clip(
        lrs[:, :, :3].astype(np.float32) * al + out[ly:ly+th, lx:lx+tw].astype(np.float32) * (1.0 - al),
        0, 255
    ).astype(np.uint8)
    return out

def heal_collar_mic_on_p2_01(bgr: np.ndarray) -> np.ndarray:
    """Spot-heals the small clip-on wireless mic square on Anh Khang's white T-shirt (preserving 100% face/eyes!)."""
    H, W = bgr.shape[:2]
    out = bgr.copy()
    x1, x2 = int(W * 0.506), int(W * 0.534)
    y1, y2 = int(H * 0.538), int(H * 0.566)
    roi = out[y1:y2, x1:x2]
    # Detect dark square pixels of the clip-on mic against the bright white shirt
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    m_local = (gray < 185).astype(np.uint8) * 255
    m_local = cv2.dilate(m_local, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=1)
    mask = np.zeros((H, W), dtype=np.uint8)
    mask[y1:y2, x1:x2] = m_local
    healed = cv2.inpaint(out, mask, 6, cv2.INPAINT_TELEA)
    # Add tiny natural cotton sensor grain (strength 0.55) on healed pixels
    rng = np.random.default_rng(42)
    noise = rng.normal(0.0, 2.2, size=healed.shape).astype(np.float32)
    mf = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (5, 5), 1.0)[:, :, None]
    out = np.clip(out.astype(np.float32) * (1.0 - mf) + (healed.astype(np.float32) + noise) * mf, 0, 255).astype(np.uint8)
    return out

def export_multilayer_psd(layers_bgr: list[tuple[str, np.ndarray]], dst_psd: Path, canvas_size: tuple[int, int]):
    """Exports an editable multi-layer RGB .PSD (RLE compressed) compatible with Adobe Photoshop 2026/2027."""
    cw, ch = canvas_size
    nl_list = []
    for idx, (lname, bgr) in enumerate(layers_bgr):
        im_rs = cv2.resize(bgr, (cw, ch), interpolation=cv2.INTER_LANCZOS4) if (bgr.shape[1], bgr.shape[0]) != (cw, ch) else bgr
        rgb = cv2.cvtColor(im_rs, cv2.COLOR_BGR2RGB)
        ch_dict = {
            -1: np.full((ch, cw), 255, dtype=np.uint8),
            0: np.ascontiguousarray(rgb[:, :, 0], dtype=np.uint8),
            1: np.ascontiguousarray(rgb[:, :, 1], dtype=np.uint8),
            2: np.ascontiguousarray(rgb[:, :, 2], dtype=np.uint8),
        }
        nl_list.append(
            nested_layers.Image(
                name=lname.encode("ascii", "ignore").decode("ascii") or f"Layer_{idx+1}",
                visible=(idx == len(layers_bgr) - 1),
                opacity=255,
                group_id=0,
                blend_mode=enums.BlendMode.normal,
                top=0, left=0, bottom=ch, right=cw,
                channels=ch_dict,
            )
        )
    psd = nested_layers.nested_layers_to_psd(nl_list, color_mode=enums.ColorMode.rgb, size=(cw, ch), compression=enums.Compression.raw)
    dst_psd.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_psd, "wb") as f:
        psd.write(f)

def save_jpg_bgr(bgr: np.ndarray, dst_jpg: Path, quality: int = 94):
    dst_jpg.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).save(dst_jpg, "JPEG", quality=quality, subsampling=0)

def make_fb_preview_4(top_3x2: np.ndarray, sq1: np.ndarray, sq2: np.ndarray, sq3: np.ndarray, dst_jpg: Path):
    W_tot = 1620
    gap = 12
    top_h = 1080  # 3:2 exact!
    top_rs = cv2.resize(top_3x2, (W_tot, top_h), interpolation=cv2.INTER_AREA)
    sw = (W_tot - 2 * gap) // 3  # 532px
    s1 = cv2.resize(sq1, (sw, sw), interpolation=cv2.INTER_AREA)
    s2 = cv2.resize(sq2, (sw, sw), interpolation=cv2.INTER_AREA)
    s3 = cv2.resize(sq3, (W_tot - 2 * (sw + gap), sw), interpolation=cv2.INTER_AREA)
    canvas = np.full((top_h + gap + sw, W_tot, 3), 255, dtype=np.uint8)
    canvas[:top_h, :] = top_rs
    y0 = top_h + gap
    canvas[y0:, :sw] = s1
    canvas[y0:, sw+gap : 2*sw+gap] = s2
    canvas[y0:, 2*(sw+gap):] = s3
    save_jpg_bgr(canvas, dst_jpg)

def make_fb_preview_2(sq_l: np.ndarray, sq_r: np.ndarray, dst_jpg: Path):
    sw, gap = 900, 12
    canvas = np.full((sw, sw * 2 + gap, 3), 255, dtype=np.uint8)
    canvas[:, :sw] = cv2.resize(sq_l, (sw, sw), interpolation=cv2.INTER_AREA)
    canvas[:, sw+gap:] = cv2.resize(sq_r, (sw, sw), interpolation=cv2.INTER_AREA)
    save_jpg_bgr(canvas, dst_jpg)

def make_fb_preview_3(top_2x1: np.ndarray, sq_l: np.ndarray, sq_r: np.ndarray, dst_jpg: Path):
    W_tot, gap = 1620, 12
    top_h = 810  # 2:1 exact Facebook 3-photo top slot!
    sw = (W_tot - gap) // 2  # 804px
    canvas = np.full((top_h + gap + sw, W_tot, 3), 255, dtype=np.uint8)
    canvas[:top_h, :] = cv2.resize(top_2x1, (W_tot, top_h), interpolation=cv2.INTER_AREA)
    canvas[top_h+gap:, :sw] = cv2.resize(sq_l, (sw, sw), interpolation=cv2.INTER_AREA)
    canvas[top_h+gap:, sw+gap:] = cv2.resize(sq_r, (W_tot - sw - gap, sw), interpolation=cv2.INTER_AREA)
    save_jpg_bgr(canvas, dst_jpg)

# ==============================================================================
# PROCESS POST 1: 261122 - Mì Cay Ngày Mưa (4 tấm)
# ==============================================================================
print("[1/4] Polishing & packaging Bài 1: 261122 - Mì Cay Ngày Mưa (4 tấm)...", flush=True)
d_p1 = OUT_DIR / "261122 - Mì Cay Ngày Mưa (4 tấm)"
p1_01_raw = cv2.imread(str(RAW_DIR / "P1_01_Banner_Mi_Cay.png"))
p1_02_raw = stamp_exact_logo_on_p1_02(cv2.imread(str(RAW_DIR / "P1_02_Mi_Cay_Hai_San.png")))
p1_03_raw = cv2.imread(str(RAW_DIR / "P1_03_Mi_Cay_Dui_Ga_7Cap.png"))
p1_04_raw = cv2.imread(str(RAW_DIR / "P1_04_Combo_Feel_Spicy_89K.png"))

p1_01_hi = unsharp_crisp(p1_01_raw, (2160, 1440), 0.18)
p1_02_hi = unsharp_crisp(p1_02_raw, (1600, 1600), 0.18)
p1_03_hi = unsharp_crisp(p1_03_raw, (1600, 1600), 0.18)
p1_04_hi = unsharp_crisp(p1_04_raw, (1600, 1600), 0.18)

save_png_rgb(p1_01_hi, d_p1 / "01_Banner_Mi_Cay_Ngay_Mua_3x2.png")
save_png_rgb(p1_02_hi, d_p1 / "02_Mi_Cay_Hai_San_Bach_Tuoc_55K_1x1.png")
save_png_rgb(p1_03_hi, d_p1 / "03_Mi_Cay_Dui_Ga_7_Cap_Do_55K_1x1.png")
save_png_rgb(p1_04_hi, d_p1 / "04_Combo_Feel_Spicy_89K_1x1.png")
make_fb_preview_4(p1_01_hi, p1_02_hi, p1_03_hi, p1_04_hi, d_p1 / "Xem_Truoc_Hien_Thi_Facebook_4_Tam.jpg")
export_multilayer_psd([
    ("04_Combo_Feel_Spicy_89K", p1_04_hi),
    ("03_Mi_Cay_Dui_Ga_7_Cap", p1_03_hi),
    ("02_Mi_Cay_Hai_San_55K", p1_02_hi),
], d_p1 / "FeelChicken_261122_MiCayNgayMua_Master.psd", (1600, 1600))

cap1 = """🌧️🍜 MƯA LẠNH NHA TRANG THÌ ĂN GÌ? XÌ XỤP NGAY MÌ CAY NÓNG HỔI TẠI FEEL CHICKEN! 🔥

Nha Trang mấy hôm nay mưa lành lạnh, ngồi xì xụp thố đá mì cay Hàn Quốc sôi sùng sục bốc khói nghi ngút, nước dùng kim chi chua cay đậm đà thì ấm bụng hết sảy luôn cả nhà ơi!

✨ Đủ 3 vị Mì Cay đầy ắp topping đồng giá chỉ 55.000đ/tô (tự chọn từ Cấp 1 dịu nhẹ đến Cấp 7 bùng nổ):
🦐 Mì Cay Hải Sản & Bạch Tuộc – Tôm tươi ngọt thịt, bạch tuộc giòn sần sật, chả cá Hàn, nấm kim châm.
🍗 Mì Cay Đùi Gà – Đùi gà cỡ lớn thấm đẫm súp cay Hàn Quốc nóng hổi.
🔥 ĐẶC BIỆT: Gọi ngay COMBO FEEL SPICY chỉ 89.000đ (01 Nồi Mì Cay + 01 Đùi Gà Sốt Hàn giòn rụm + 01 Coca-Cola mát lạnh) ăn no căng bụng siêu hời!

🛵 Ngại mưa gió ra đường? Nhắn tin cho Page hoặc nhấc máy alo, Feel đóng hộp giữ nhiệt giao nóng tận cửa chỉ trong 15 phút nha! 👇
----------------------------
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
📍 CS1: 38 Nguyễn Đình Chiểu (Dốc ĐH Nha Trang)
📍 CS2: 35 Trần Hữu Duyệt (Vĩnh Điềm Trung)
⏰ Mở cửa: 10:00 – 22:00
📞 Hotline / Ship nhanh: 0796 601 106
#FeelChicken #MiCayNhaTrang #GaRanSotHanQuoc #AnVatNhaTrang #FoodNhaTrang
"""
(d_p1 / "CAPTION_BAI_01_MI_CAY.txt").write_text(cap1.strip() + "\n", encoding="utf-8")

# ==============================================================================
# PROCESS POST 2: 261124 - Thử Thách 5 Phút 1Tr5 (2 tấm)
# ==============================================================================
print("[2/4] Polishing & packaging Bài 2: 261124 - Thử Thách 5 Phút 1Tr5 (2 tấm)...", flush=True)
d_p2 = OUT_DIR / "261124 - Thử Thách 5 Phút 1Tr5 (2 tấm)"
p2_01_raw = heal_collar_mic_on_p2_01(cv2.imread(str(RAW_DIR / "P2_01_Thu_Thach_Trai.png")))
p2_02_raw = cv2.imread(str(RAW_DIR / "P2_02_The_Le_Phai.png"))

p2_01_hi = unsharp_crisp(p2_01_raw, (1600, 1600), 0.18)
p2_02_hi = unsharp_crisp(p2_02_raw, (1600, 1600), 0.18)

save_png_rgb(p2_01_hi, d_p2 / "01_Thu_Thach_5_Phut_Anh_Khang_1x1.png")
save_png_rgb(p2_02_hi, d_p2 / "02_Bang_Vang_Giai_Thuong_1500K_1x1.png")
make_fb_preview_2(p2_01_hi, p2_02_hi, d_p2 / "Xem_Truoc_Hien_Thi_Facebook_2_Tam.jpg")
export_multilayer_psd([
    ("02_Bang_Vang_The_Le_1500K", p2_02_hi),
    ("01_Thu_Thach_5_Phut_Anh_Khang", p2_01_hi),
], d_p2 / "FeelChicken_261124_ThuThach1500K_Master.psd", (1600, 1600))

cap2 = """🏆🔥 5 ĐÙI GÀ + 1 MÌ TƯƠNG ĐEN TRONG 5 PHÚT – BẠN DÁM NHẬN 1.500.000Đ TIỀN MẶT? 🔥🍗

Đấu trường ẩm thực tại Feel Chicken vẫn đang tìm kiếm "chiến thần ăn uống" tiếp theo phá đảo thử thách và rinh thưởng nóng ngay tại bàn!

📌 Thể lệ cực kỳ đơn giản:
1️⃣ Khẩu phần thách đấu: Ăn sạch 05 Đùi Gà Rán cỡ lớn giòn rụm + 01 phần Mì Tương Đen Hàn Quốc.
2️⃣ Thời gian bấm giờ: Cá nhân 01 người hoàn thành trong vòng 05 phút.
3️⃣ Giải thưởng trao tay: Nhận ngay 1.500.000Đ TIỀN MẶT tại bàn + MIỄN PHÍ 100% phần ăn khi chiến thắng!
💛 Chơi vui không lo lỗ: Nếu chưa vượt qua thời gian, bạn chỉ thanh toán đúng 250.000đ tiền phần ăn (vẫn no căng bụng cực hời!).

Tag ngay đứa bạn có "chiếc bụng không đáy" vào nhận kèo hoặc gọi Hotline đặt lịch thi ngay hôm nay! 👇👇
----------------------------
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
📍 CS1: 38 Nguyễn Đình Chiểu (Dốc ĐH Nha Trang)
📍 CS2: 35 Trần Hữu Duyệt (Vĩnh Điềm Trung)
⏰ Mở cửa: 10:00 – 22:00
📞 Hotline đăng ký thi & đặt món: 0796 601 106
#FeelChicken #ThuThachAnUong #GaRanNhaTrang #MiTuongDen #FoodNhaTrang
"""
(d_p2 / "CAPTION_BAI_02_THU_THACH_1500K.txt").write_text(cap2.strip() + "\n", encoding="utf-8")

# ==============================================================================
# PROCESS POST 3: 261128 - Mưa Ghé Feel Ấm Bụng (3 tấm)
# ==============================================================================
print("[3/4] Polishing & packaging Bài 3: 261128 - Mưa Ghé Feel Ấm Bụng (3 tấm)...", flush=True)
d_p3 = OUT_DIR / "261128 - Mưa Ghé Feel Ấm Bụng (3 tấm)"
p3_01_raw = cv2.imread(str(RAW_DIR / "P3_01_Mua_Ghe_Feel_Banner.png"))
p3_02_raw = cv2.imread(str(RAW_DIR / "P3_02_Ga_Ran_5_Vi.png"))
p3_03_raw = cv2.imread(str(RAW_DIR / "P3_03_Ban_Tiec_Hoi_Ban.png"))

# Expand 3:2 -> 2160x1080 (2:1) seamlessly so Facebook's 3-photo top slot shows 100% of logo & bottom address with 0% crop!
p3_01_2x1 = expand_3x2_to_clean_2x1(p3_01_raw, 2160, 1080)
p3_01_3x2 = unsharp_crisp(p3_01_raw, (2160, 1440), 0.18)
p3_02_hi  = unsharp_crisp(p3_02_raw, (1600, 1600), 0.18)
p3_03_hi  = unsharp_crisp(p3_03_raw, (1600, 1600), 0.18)

save_png_rgb(p3_01_2x1, d_p3 / "01_Tren_Ngang_Mua_Ghe_Feel_2x1.png")
save_png_rgb(p3_01_3x2, d_p3 / "01b_Banner_Ngang_Day_Du_3x2.png")
save_png_rgb(p3_02_hi,  d_p3 / "02_Duoi_Trai_Ga_Ran_5_Vi_129K_1x1.png")
save_png_rgb(p3_03_hi,  d_p3 / "03_Duoi_Phai_Ban_Tiec_Hoi_Ban_249K_1x1.png")
make_fb_preview_3(p3_01_2x1, p3_02_hi, p3_03_hi, d_p3 / "Xem_Truoc_Hien_Thi_Facebook_3_Tam.jpg")
export_multilayer_psd([
    ("03_Ban_Tiec_Hoi_Ban_249K", p3_03_hi),
    ("02_Ga_Ran_5_Vi_129K", p3_02_hi),
], d_p3 / "FeelChicken_261128_MuaGheFeel_Master.psd", (1600, 1600))

cap3 = """🌧️🍗 MỘT NGÀY MƯA ƯƠNG ƯƠNG, GHÉ FEEL CHICKEN ĂN NGON CHO ẤM BỤNG! 💛

Trời mưa ương ương ngại đi xa, cứ rẽ vào Feel Chicken ngồi phòng ấm khô ráo, gọi ngay một mâm tiệc nóng giòn vừa ra lò là vui trọn buổi chiều tối cùng người thương và hội cạ cứng!

✨ Menu nóng hổi chiều lòng mọi chiếc bụng đói:
🍗 Gà Rán 5 Vị Sốt Hàn Quốc – Vỏ giòn rụm áo đẫm sốt Phô Mai, Cay Hàn, Tỏi Cay, Chanh Dây, Sốt Tương.
🍜 Đủ món Hàn – Âu bắt vị: Mì Cay 7 Cấp Độ (55K), Tokbokki dẻo cay, Mì Tương Đen, Mì Ý sốt bò bằm, Khoai tây chiên & Salad tươi.
💛 Combo tiết kiệm cho mọi cuộc vui: Combo cá nhân từ 59K • Combo đôi từ 129K • Combo hội bạn no căng 249K – 259K!

🛵 Mưa ngại ra ngoài? Nhấc máy alo ngay, Feel đóng hộp giữ nhiệt giao nóng tận nhà chỉ trong 15 phút! 👇
----------------------------
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
📍 CS1: 38 Nguyễn Đình Chiểu (Dốc ĐH Nha Trang)
📍 CS2: 35 Trần Hữu Duyệt (Vĩnh Điềm Trung)
⏰ Mở cửa: 10:00 – 22:00
📞 Hotline / Giao nóng 15p: 0796 601 106
#FeelChicken #GaRanSotHanQuoc #AnGiNhaTrang #ComboGaRan #FoodNhaTrang
"""
(d_p3 / "CAPTION_BAI_03_GHE_FEEL_AM_BUNG.txt").write_text(cap3.strip() + "\n", encoding="utf-8")

# Save quick QC copies to SCR_DIR
shutil.copy2(d_p1 / "Xem_Truoc_Hien_Thi_Facebook_4_Tam.jpg", SCR_DIR / "preview_fb_post1_micay.jpg")
shutil.copy2(d_p2 / "Xem_Truoc_Hien_Thi_Facebook_2_Tam.jpg", SCR_DIR / "preview_fb_post2_thuthach.jpg")
shutil.copy2(d_p3 / "Xem_Truoc_Hien_Thi_Facebook_3_Tam.jpg", SCR_DIR / "preview_fb_post3_ghefeel.jpg")

# ==============================================================================
# 4. SYNC ALL 3 NEW POST FOLDERS TO FEEL CHICKEN (G:) & AI_FULL_STUDIO ARCHIVE
# ==============================================================================
print("[4/4] Syncing all 3 redesigned posts to G:\\Other computers\\My Computer\\feel chicken...", flush=True)
fc_t11 = Path(r"G:\Other computers\My Computer\feel chicken\04. Bài Đăng Fanpage (Thiết Kế & Caption)\02_Thang_11_2026")
cloud_arch = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\feelchicken\Bai_Dang_Tiep_Theo_Thang_11\XUAT_3_BAI_THANG_11")
cloud_arch.mkdir(parents=True, exist_ok=True)

for sub_d in (d_p1, d_p2, d_p3):
    for target_parent in (fc_t11, cloud_arch):
        dst_sub = target_parent / sub_d.name
        if dst_sub.exists():
            shutil.rmtree(dst_sub)
        shutil.copytree(sub_d, dst_sub)

shutil.copy2(__file__, Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\feelchicken\Bai_Dang_Tiep_Theo_Thang_11\polish_psd_and_sync_3posts.py"))
subprocess.Popen(["explorer.exe", str(fc_t11)])
print("ALL 3 REDESIGNED POSTS POLISHED, PSD EXPORTED & SYNCED!", flush=True)
