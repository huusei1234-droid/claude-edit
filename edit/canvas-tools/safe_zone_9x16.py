# -*- coding: utf-8 -*-
"""
Quy chuan Vung An Toan Video Doc 9:16 (1080x1920) dung chung ca TikTok & Facebook/IG Reels.
Cam tuyet doi dat bat ky Text, Phu de, The UI, Sticker, Logo, Khung PIP/Bento nho hay Lop phu
cham vao 5 Vung Den Cam (UI che khuat cua TikTok + Reels):
  - Tren dinh (Top Black):       Y = 0 .. 248 px      (CapCut Y > +0.742)
  - Duoi day (Bottom Black):     Y = 1548 .. 1920 px  (CapCut Y < -0.612, cao 372px tu day len)
  - Le trai (Left Black):        X = 0 .. 52 px       (CapCut X < -0.904)
  - Le phai nua tren (Y<860):    X = 1026 .. 1080 px  (CapCut X > +0.900)
  - Cot nut tuong tac Phai-Duoi (Y = 860 .. 1548 px):
                                 X = 886 .. 1080 px   (CapCut X > +0.641, rong 194px ben phai)

Khung Trang An Toan cho phep di Text & Lop phu (co them 2-4px dem an toan):
  - Nua tren (Y = 250 .. 860 px):    X = 54 .. 1024 px (rong 970px, tam X = 539px)
  - Nua duoi (Y = 860 .. 1545 px):   X = 54 .. 884 px  (rong 830px, tam X = 469px / CapCut X = -0.131)
"""
import numpy as np
from PIL import Image

W_9X16 = 1080
H_9X16 = 1920

SAFE_TOP_Y = 250
SAFE_SPLIT_Y = 860
SAFE_BOTTOM_Y = 1545
SAFE_LEFT_X = 54
SAFE_RIGHT_UPPER_X = 1024
SAFE_RIGHT_LOWER_X = 884  # Tranh cot Avatar/Tim/Comment/Share/Dia nhac TikTok & Reels


def max_safe_right_x(y2: float) -> int:
    """Tra ve toa do X phai toi da cho phep dua theo mep duoi y2 cua hop chu/lop phu."""
    return SAFE_RIGHT_LOWER_X if y2 > SAFE_SPLIT_Y else SAFE_RIGHT_UPPER_X


def is_box_safe_9x16(x1: float, y1: float, x2: float, y2: float) -> tuple[bool, list[str]]:
    """Kiem tra khung chu nhat [x1, y1, x2, y2] tren canvas 1080x1920 co vi pham vung den khong."""
    reasons = []
    if x1 < SAFE_LEFT_X:
        reasons.append(f"Vi pham le trai den: x1={x1:.0f} < {SAFE_LEFT_X}px")
    if y1 < SAFE_TOP_Y:
        reasons.append(f"Vi pham vung den tren dinh: y1={y1:.0f} < {SAFE_TOP_Y}px")
    if y2 > SAFE_BOTTOM_Y:
        reasons.append(f"Vi pham vung den day (Caption/Nhac): y2={y2:.0f} > {SAFE_BOTTOM_Y}px")
    lim_rx = max_safe_right_x(y2)
    if x2 > lim_rx:
        zone_name = "cot nut TikTok/Reels ben phai" if y2 > SAFE_SPLIT_Y else "le phai tren"
        reasons.append(f"Vi pham {zone_name}: x2={x2:.0f} > {lim_rx}px (tai y2={y2:.0f})")
    return (len(reasons) == 0, reasons)


def clamp_box_to_safe_zone_9x16(cx: float, cy: float, w: float, h: float) -> tuple[int, int]:
    """Dich chuyen tam (cx, cy) cua hop kich thuoc (w, h) de nam tron 100% trong Vung Trang An Toan."""
    half_w, half_h = w / 2.0, h / 2.0
    cy = max(SAFE_TOP_Y + half_h, min(SAFE_BOTTOM_Y - half_h, cy))
    lim_rx = max_safe_right_x(cy + half_h)
    max_w = lim_rx - SAFE_LEFT_X
    if w > max_w:
        cx = (SAFE_LEFT_X + lim_rx) / 2.0
    else:
        cx = max(SAFE_LEFT_X + half_w, min(lim_rx - half_w, cx))
    return int(round(cx)), int(round(cy))


def px_to_capcut_norm(cx: float, cy: float) -> tuple[float, float]:
    """Chuyen tam pixel (1080x1920) sang toa do CapCut transform (x, y) trong doan [-1.0, +1.0]."""
    nx = (cx / (W_9X16 / 2.0)) - 1.0
    ny = 1.0 - (cy / (H_9X16 / 2.0))
    return round(nx, 4), round(ny, 4)


def audit_rgba_overlay_safe_zone(rgba_img: Image.Image, alpha_thresh: int = 16) -> tuple[bool, dict]:
    """Kiem tra anh PNG lop phu RGBA 1080x1920 xem co pixel hien thi nao tran vao Vung Den Cam khong."""
    im = rgba_img.convert("RGBA")
    if im.size != (W_9X16, H_9X16):
        im = im.resize((W_9X16, H_9X16), Image.Resampling.NEAREST)
    alpha = np.array(im)[:, :, 3] > alpha_thresh

    forbidden = np.zeros((H_9X16, W_9X16), dtype=bool)
    forbidden[:SAFE_TOP_Y, :] = True
    forbidden[SAFE_BOTTOM_Y:, :] = True
    forbidden[:, :SAFE_LEFT_X] = True
    forbidden[:SAFE_SPLIT_Y, SAFE_RIGHT_UPPER_X:] = True
    forbidden[SAFE_SPLIT_Y:SAFE_BOTTOM_Y, SAFE_RIGHT_LOWER_X:] = True

    viol = int(np.sum(alpha & forbidden))
    total = int(np.sum(alpha))
    return (viol == 0, {"violating_pixels": viol, "total_opaque_pixels": total})
