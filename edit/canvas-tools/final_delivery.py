"""
Bộ Định Tuyến & Đặt Tên Chuẩn Mọi Video Final Toàn Hệ Thống (`final_delivery.py`):
- Định dạng tên file bắt buộc: `<YYMMDD> <Mã Thương Hiệu> <Tên Nội Dung Tiếng Việt Có Dấu> final.mp4`
  Ví dụ: `261119 HTPM 5 sản phẩm tuổi 25 final.mp4`
- Tự động xuất đồng thời vào 3 đích:
  1. Thư mục Hoàn thiện riêng của đúng Thương hiệu / Dự án đó trên Google Drive (`BRAND_FINAL_DIRS`)
  2. Kho tổng hợp hệ thống: `Z:\\Drive của tôi\\AI_Full_Studio\\04_Videos_Final`
  3. Kho cục bộ mở nhanh: `D:\\XUẤT CAPCUT`
"""
import datetime
import json
import os
import re
import shutil
import subprocess

MASTER_FINAL_DIR = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final"
LOCAL_EXPORT_DIR = r"D:\XUẤT CAPCUT"

BRAND_ROUTES = {
    "htpm": {
        "prefix": "HTPM",
        "dir": r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma",
        "fallback_dir": r"Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma",
        "local_subdir": "hằng thu pharma",
        "group_by_date_only": True,
    },
    "avpm": {
        "prefix": "AVPM",
        "dir": r"Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K5 - AVPM",
    },
    "bojomi": {
        "prefix": "BOJOMI",
        "dir": r"Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K5 - AVPM",
    },
    "k4": {
        "prefix": "K4",
        "dir": r"G:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu",
        "fallback_dir": r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu",
        "local_subdir": "K4 - Mẹ Chồng Nàng Dâu",
    },
    "k5": {
        "prefix": "K5",
        "dir": r"G:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K5 - Phim An Vượng",
        "fallback_dir": r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K5 - Phim An Vượng",
        "local_subdir": "K5 - Phim An Vượng",
    },
    "f20": {
        "prefix": "F20",
        "dir": r"Z:\Máy tính khác\My Computer\F20\Final",
    },
    "feelchicken": {
        "prefix": "Feel Chicken",
        "dir": r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN",
    },
    "ms_noithat": {
        "prefix": "MS Nội Thất",
        "dir": r"Z:\Drive của tôi\dự án ngoài\MS Nội Thất",
    },
    "viethan": {
        "prefix": "Việt Hàn",
        "dir": r"Z:\Máy tính khác\My Computer\Việt Hàn - Thiện Trang\VIỆT HÀN\File Hoàn Thiện Việt Hàn",
    },
    "thientrang": {
        "prefix": "Thiện Trang",
        "dir": r"Z:\Máy tính khác\My Computer\Việt Hàn - Thiện Trang\THIỆN TRANG\File Hoàn Thiện Thiện Trang",
    },
}


def build_standard_final_name(brand_key: str, vietnamese_title: str, date_yymmdd: str = None, ext: str = ".mp4") -> str:
    route = BRAND_ROUTES.get(brand_key.lower().strip(), {"prefix": brand_key.strip()})
    yymmdd = (date_yymmdd or datetime.datetime.now().strftime("%y%m%d")).strip()
    clean_title = re.sub(r'[\\/:*?"<>|]+', "-", vietnamese_title).strip()
    # Loại bỏ chữ 'final' bị lặp ở cuối nếu người gọi truyền thừa
    clean_title = re.sub(r"\s+final$", "", clean_title, flags=re.I).strip()
    prefix = route["prefix"]
    if clean_title.upper().startswith(prefix.upper() + " "):
        clean_title = clean_title[len(prefix):].strip()
    if not ext.startswith("."):
        ext = "." + ext
    return f"{yymmdd} {prefix} {clean_title} final{ext}"


def _is_landscape_video(src_mp4: str) -> bool:
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", src_mp4],
            timeout=10,
        )
        st = json.loads(out.decode("utf-8", errors="ignore")).get("streams", [{}])[0]
        w, h = int(st.get("width") or 0), int(st.get("height") or 0)
        return w > h > 0
    except Exception:
        return False


def deliver_final_video(src_mp4: str, brand_key: str, vietnamese_title: str, date_yymmdd: str = None, is_horizontal: bool = None) -> dict:
    if not os.path.exists(src_mp4):
        raise FileNotFoundError(f"Không tìm thấy tệp video nguồn: {src_mp4}")
    key = brand_key.lower().strip()
    if key not in BRAND_ROUTES:
        raise ValueError(f"brand_key '{brand_key}' chưa khai báo. Hỗ trợ: {list(BRAND_ROUTES.keys())}")

    if is_horizontal is None:
        is_horizontal = _is_landscape_video(src_mp4)

    fname = build_standard_final_name(key, vietnamese_title, date_yymmdd=date_yymmdd, ext=".mp4")
    yymmdd = (date_yymmdd or datetime.datetime.now().strftime("%y%m%d")).strip()
    clean_title = re.sub(r'[\\/:*?"<>|]+', "-", vietnamese_title).strip()
    clean_title = re.sub(r"\s+final$", "", clean_title, flags=re.I).strip()
    prefix = BRAND_ROUTES[key]["prefix"]
    if clean_title.upper().startswith(prefix.upper() + " "):
        clean_title = clean_title[len(prefix):].strip()
    title_cap = clean_title[:1].upper() + clean_title[1:] if clean_title else clean_title

    route_cfg = BRAND_ROUTES[key]
    brand_dir = route_cfg["dir"]
    if not os.path.isdir(brand_dir) and route_cfg.get("fallback_dir") and os.path.isdir(route_cfg["fallback_dir"]):
        brand_dir = route_cfg["fallback_dir"]
    local_dir = os.path.join(LOCAL_EXPORT_DIR, route_cfg["local_subdir"]) if route_cfg.get("local_subdir") else LOCAL_EXPORT_DIR
    master_dir = MASTER_FINAL_DIR

    # Phân thư mục phẳng theo Ngày (TUYỆT ĐỐI KHÔNG tạo thư mục con cho từng bài/video lẻ!)
    if (route_cfg.get("group_by_date_only") or route_cfg.get("group_by_date_and_title")) and len(yymmdd) == 6 and yymmdd.isdigit():
        day_folder = f"{yymmdd} - Ngày {yymmdd[4:6]}.{yymmdd[2:4]}.20{yymmdd[:2]}"
        brand_dir = os.path.join(brand_dir, day_folder)
        local_dir = os.path.join(local_dir, day_folder)

    # Mọi video Ngang (16:9 / width > height) tự động lưu riêng vào thư mục con 'Ngang'
    if is_horizontal:
        brand_dir = os.path.join(brand_dir, "Ngang")
        master_dir = os.path.join(master_dir, "Ngang")
        local_dir = os.path.join(local_dir, "Ngang")

    paths = {}
    for label, target_dir in [
        ("brand_path", brand_dir),
        ("master_cloud_path", master_dir),
        ("local_path", local_dir),
    ]:
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        dst = os.path.join(target_dir, fname)
        if os.path.abspath(src_mp4).lower() != os.path.abspath(dst).lower():
            shutil.copy2(src_mp4, dst)
        paths[label] = dst

    orient_tag = " [NGANG 16:9 -> thư mục Ngang]" if is_horizontal else " [DỌC 9:16]"
    print(f"[FinalDelivery]{orient_tag} Đã lưu chuẩn '{fname}':\n  • Thư mục dự án: {paths['brand_path']}\n  • Cloud Master : {paths['master_cloud_path']}\n  • Local Export : {paths['local_path']}")
    return {"filename": fname, "is_horizontal": is_horizontal, **paths}
