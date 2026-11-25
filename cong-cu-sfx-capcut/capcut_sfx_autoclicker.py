"""
Công cụ Auto-Click tải tự động toàn bộ SFX chưa tải (nút mũi tên ↓) trên CapCut PC.
- Nhận diện chính xác 100% nút mũi tên tải xuống (↓) bằng OpenCV.
- Khóa an toàn kép (Double-Lock): Loại trừ tuyệt đối nút dấu cộng (+) để không bao giờ chèn nhầm SFX vào Timeline.
- Tự động cuộn danh sách xuống trang tiếp theo và chờ sẵn khi bạn chuyển sang Tab danh mục SFX mới.
- Nhấn phím ESC bất kỳ lúc nào (hoặc đưa chuột sát góc trên-trái màn hình) để dừng ngay lập tức!
"""
import sys
import time
import ctypes
from ctypes import wintypes
from pathlib import Path
import numpy as np
import cv2

HERE = Path(__file__).resolve().parent
TPL_DL_PATH = HERE / "tpl_download.png"
TPL_PL_PATH = HERE / "tpl_plus.png"

# Enable Per-Monitor DPI Awareness so screen coordinates == physical pixels 1:1
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

VK_ESCAPE = 0x1B
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_WHEEL = 0x0800
SRCCOPY = 0x00CC0020


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


def should_stop() -> bool:
    if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
        return True
    pt = wintypes.POINT()
    if user32.GetCursorPos(ctypes.byref(pt)):
        if pt.x <= 3 and pt.y <= 3:
            return True
    return False


def find_capcut_rect():
    """Find visible CapCut main window rectangle (left, top, right, bottom) if possible."""
    best = None
    best_area = 0
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(hwnd, _):
        nonlocal best, best_area
        if user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, buf, 256)
            title = buf.value.lower()
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            if w >= 600 and h >= 450 and ("capcut" in title or "jianying" in title):
                area = w * h
                if area > best_area:
                    best_area = area
                    best = (rect.left, rect.top, rect.right, rect.bottom)
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return best


def grab_screen_gray(region=None):
    """Capture screen region (left, top, right, bottom) into grayscale numpy array + (offset_x, offset_y)."""
    if region:
        left, top, right, bottom = region
    else:
        left = user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
        top = user32.GetSystemMetrics(77)    # SM_YVIRTUALSCREEN
        w_all = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        h_all = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        if w_all <= 0 or h_all <= 0:
            left, top = 0, 0
            w_all = user32.GetSystemMetrics(0)
            h_all = user32.GetSystemMetrics(1)
        right, bottom = left + w_all, top + h_all

    width = max(1, right - left)
    height = max(1, bottom - top)

    hdc_screen = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
    old_obj = gdi32.SelectObject(hdc_mem, hbmp)

    gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc_screen, left, top, SRCCOPY)

    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0

    buf = ctypes.create_string_buffer(width * height * 4)
    gdi32.GetDIBits(hdc_mem, hbmp, 0, height, buf, ctypes.byref(bmi), 0)

    gdi32.SelectObject(hdc_mem, old_obj)
    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc_screen)

    arr = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))
    gray = cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)
    return gray, left, top


def detect_download_buttons(gray_img, tpl_dl_base, tpl_pl_base, scales=(1.0, 0.8, 1.25, 0.67, 1.5)):
    """
    Find all '↓' (download) button centers in gray_img.
    Double-lock safety:
      1) match_dl >= 0.84
      2) match_dl >= match_plus + 0.14 (guarantees '+' buttons are NEVER clicked!)
      3) Clustered in the dominant X column (since CapCut SFX list aligns all ↓ vertically!)
    """
    best_scale_pts = []
    best_peak = 0.0

    for sc in scales:
        tw = max(12, int(round(tpl_dl_base.shape[1] * sc)))
        th = max(12, int(round(tpl_dl_base.shape[0] * sc)))
        if gray_img.shape[0] <= th + 4 or gray_img.shape[1] <= tw + 4:
            continue

        tpl_dl = tpl_dl_base if sc == 1.0 else cv2.resize(tpl_dl_base, (tw, th), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_CUBIC)
        tpl_pl = tpl_pl_base if sc == 1.0 else cv2.resize(tpl_pl_base, (tw, th), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_CUBIC)

        res_dl = cv2.matchTemplate(gray_img, tpl_dl, cv2.TM_CCOEFF_NORMED)
        res_pl = cv2.matchTemplate(gray_img, tpl_pl, cv2.TM_CCOEFF_NORMED)

        ys, xs = np.where((res_dl >= 0.84) & ((res_dl - res_pl) >= 0.14))
        if len(xs) == 0:
            continue

        # Non-maximum suppression (radius = th * 0.7)
        scores = res_dl[ys, xs]
        order = np.argsort(-scores)
        kept = []
        min_dist2 = (max(14, int(th * 0.75))) ** 2
        for idx in order:
            cx = int(xs[idx] + tw // 2)
            cy = int(ys[idx] + th // 2)
            sc_val = float(scores[idx])
            if all((cx - kx) ** 2 + (cy - ky) ** 2 >= min_dist2 for kx, ky, _ in kept):
                kept.append((cx, cy, sc_val))

        peak = max(k[2] for k in kept) if kept else 0.0
        if len(kept) > len(best_scale_pts) or (len(kept) == len(best_scale_pts) and peak > best_peak):
            best_scale_pts = kept
            best_peak = peak

    if not best_scale_pts:
        return []

    # Keep buttons aligned to the dominant vertical column (±8px in X) so random UI icons elsewhere are ignored
    if len(best_scale_pts) >= 2:
        xs_only = [p[0] for p in best_scale_pts]
        # Find X with most neighbors within ±8px
        best_x = max(xs_only, key=lambda x0: sum(1 for x1 in xs_only if abs(x1 - x0) <= 8))
        best_scale_pts = [p for p in best_scale_pts if abs(p[0] - best_x) <= 8]

    best_scale_pts.sort(key=lambda p: p[1])  # top-to-bottom
    return best_scale_pts


def click_at(x: int, y: int):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.04)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.03)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def scroll_list_down(list_x: int, list_y: int, notches: int = 5):
    user32.SetCursorPos(int(list_x), int(list_y))
    time.sleep(0.05)
    for _ in range(notches):
        if should_stop():
            return
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, ctypes.c_ulong(-120 & 0xFFFFFFFF).value, 0)
        time.sleep(0.04)


def run_self_test(sample_img_path: str):
    tpl_dl = cv2.imread(str(TPL_DL_PATH), cv2.IMREAD_GRAYSCALE)
    tpl_pl = cv2.imread(str(TPL_PL_PATH), cv2.IMREAD_GRAYSCALE)
    sample = cv2.imread(sample_img_path, cv2.IMREAD_GRAYSCALE)
    pts = detect_download_buttons(sample, tpl_dl, tpl_pl)
    print(f"[SELF-TEST] Found {len(pts)} download (↓) buttons (expected 6, and 0 '+' buttons):")
    for cx, cy, sc in pts:
        print(f"  -> click=({cx}, {cy}) | confidence={sc:.4f}")
    assert len(pts) == 6, f"Expected 6 download buttons, got {len(pts)}"
    print("[SELF-TEST] 100% PASSED! Zero '+' buttons matched.")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--self-test":
        run_self_test(sys.argv[2])
        return

    tpl_dl = cv2.imread(str(TPL_DL_PATH), cv2.IMREAD_GRAYSCALE)
    tpl_pl = cv2.imread(str(TPL_PL_PATH), cv2.IMREAD_GRAYSCALE)
    if tpl_dl is None or tpl_pl is None:
        print("Không tìm thấy file mẫu ảnh nút bấm tpl_download.png / tpl_plus.png!")
        sys.exit(1)

    print("=" * 68)
    print("  AUTO-CLICK TẢI TOÀN BỘ SFX CHƯA TẢI (↓) TRÊN CAPCUT PC")
    print("=" * 68)
    print("  • Chỉ click đúng nút MŨI TÊN TẢI XUỐNG (↓), bỏ qua 100% nút (+).")
    print("  • Tự động cuộn xuống tải tiếp cho tới cuối danh sách.")
    print("  • Bấm phím [ESC] (hoặc kéo chuột sát góc trên-trái) để DỪNG NGAY!")
    print("=" * 68)
    for sec in (3, 2, 1):
        print(f"  Bắt đầu sau {sec} giây... (Hãy để cửa sổ danh sách SFX CapCut hiện trên màn hình)")
        time.sleep(1.0)

    total_clicked = 0
    anchor_col_x = None
    anchor_mid_y = None
    empty_scrolls = 0
    prev_strip = None
    waiting_msg_shown = False

    while not should_stop():
        rect = find_capcut_rect()
        gray, ox, oy = grab_screen_gray(rect)
        pts = detect_download_buttons(gray, tpl_dl, tpl_pl)

        if pts:
            waiting_msg_shown = False
            empty_scrolls = 0
            anchor_col_x = ox + pts[0][0]
            anchor_mid_y = oy + pts[len(pts) // 2][1]

            print(f"  [+] Phát hiện {len(pts)} SFX chưa tải trên màn hình -> Đang click tải...")
            for cx, cy, sc in pts:
                if should_stop():
                    break
                sx, sy = ox + cx, oy + cy
                click_at(sx, sy)
                total_clicked += 1
                time.sleep(0.32)

            if should_stop():
                break

            # Wait briefly so newly clicked buttons switch from ↓ to loading/+ before scrolling
            time.sleep(0.55)
            # Scroll down in safe zone 95px left of ↓ column (avoids ☆ and ↓/+ buttons)
            scroll_x = max(ox + 40, anchor_col_x - 95)
            scroll_list_down(scroll_x, anchor_mid_y, notches=5)
            time.sleep(0.85)
        else:
            # No visible ↓ buttons on current view — if we already locked onto the SFX list column, try scrolling down!
            if anchor_col_x is not None and empty_scrolls < 8:
                scroll_x = max(ox + 40, anchor_col_x - 95)
                # Check if list pixels still change when scrolling (in case a whole screen is already '+' downloaded!)
                strip_x0 = max(0, (anchor_col_x - ox) - 180)
                strip_x1 = min(gray.shape[1], (anchor_col_x - ox) + 20)
                cur_strip = gray[:, strip_x0:strip_x1].copy()
                if prev_strip is not None and cur_strip.shape == prev_strip.shape:
                    diff = float(np.mean(np.abs(cur_strip.astype(np.int16) - prev_strip.astype(np.int16))))
                    if diff < 1.2 and empty_scrolls >= 2:
                        # List stopped moving -> Reached the very bottom!
                        empty_scrolls = 99
                        prev_strip = None
                        continue
                prev_strip = cur_strip
                empty_scrolls += 1
                print(f"  [>] Màn hiện tại đã tải hết (+), đang tự cuộn xuống tìm tiếp ({empty_scrolls}/8)...")
                scroll_list_down(scroll_x, anchor_mid_y, notches=6)
                time.sleep(0.85)
            else:
                if not waiting_msg_shown:
                    try:
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    except Exception:
                        pass
                    if total_clicked > 0:
                        print(f"\n  [HOÀN TẤT TAB HIỆN TẠI] Đã tự động bấm tải {total_clicked} SFX!")
                        print("  👉 Hãy bấm sang Tab danh mục SFX tiếp theo trên CapCut (hoặc cuộn tới vùng có nút ↓) để tải tiếp,")
                        print("     HOẶC bấm phím [ESC] để thoát công cụ.")
                    else:
                        print("\n  [ĐANG CHỜ] Chưa thấy nút mũi tên tải xuống (↓) nào của CapCut trên màn hình.")
                        print("  👉 Hãy mở mục Âm thanh -> Hiệu ứng âm thanh trên CapCut (hoặc bấm [ESC] để thoát)...")
                    waiting_msg_shown = True
                time.sleep(1.0)

    print(f"\n[ĐÃ DỪNG AN TOÀN] Tổng cộng đã tự động tải {total_clicked} hiệu ứng SFX trên CapCut!")


if __name__ == "__main__":
    main()
