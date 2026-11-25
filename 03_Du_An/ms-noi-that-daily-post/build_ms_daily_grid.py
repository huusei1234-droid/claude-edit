# -*- coding: utf-8 -*-
"""
Công cụ tự động sản xuất Bộ Ảnh Lưới 2x2 Facebook (2:1 cắt đôi ở hàng trên + 2 thẻ vuông 1:1 mã vật liệu ở hàng dưới)
& Caption chuẩn SEO cho Nội Thất MS – Chuyên ốp tường Nha Trang.
"""
import argparse
import datetime
import json
import os
import pathlib
import shutil
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

STUDIO_ROOT = pathlib.Path(r"d:\AI\full studio")
PROJ_DIR = STUDIO_ROOT / "03_Du_An" / "ms-noi-that-daily-post"
FONT_DIR = STUDIO_ROOT / "BO_KIEN_THUC_TVC_AI_PORTABLE" / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
MS_DRIVE_DIR = pathlib.Path(r"Z:\Drive của tôi\dự án ngoài\MS Nội Thất")
DAILY_DRIVE_ROOT = MS_DRIVE_DIR / "Bài Đăng Hàng Ngày"
CLOUD_BACKUP_ROOT = pathlib.Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\ms-noi-that-daily-post\Daily_Output")

CANVAS_TOOLS = STUDIO_ROOT / "edit" / "canvas-tools"
if str(CANVAS_TOOLS) not in sys.path:
    sys.path.insert(0, str(CANVAS_TOOLS))


def imread_unicode(path: pathlib.Path) -> np.ndarray:
    arr = np.fromfile(str(path), dtype=np.uint8)
    im = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if im is None:
        raise RuntimeError(f"Cannot decode image: {path}")
    return im


def imwrite_unicode(path: pathlib.Path, bgr: np.ndarray, quality: int = 96):
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, enc = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise RuntimeError(f"Cannot encode jpg: {path}")
    enc.tofile(str(path))


def extract_pure_swatch(card_path: pathlib.Path, out_path: pathlib.Path) -> pathlib.Path:
    """Cắt vùng bề mặt tấm ốp/lam sóng thuần túy (không dính chữ/logo) từ thẻ MS STUDIO 1080x1440 để làm ảnh tham chiếu AI."""
    bgr = imread_unicode(card_path)
    h, w = bgr.shape[:2]
    # Vùng tấm đứng phía sau bên phải: x=365..1005, y=68..660
    x1, x2 = int(w * 0.34), int(w * 0.93)
    y1, y2 = int(h * 0.05), int(h * 0.47)
    crop = bgr[y1:y2, x1:x2].copy()
    imwrite_unicode(out_path, crop, quality=95)
    return out_path


def make_square_material_card(card_path: pathlib.Path, badge_idx: int, mat_code: str) -> np.ndarray:
    """
    Đặt nguyên bản thẻ catalog MS STUDIO 1080x1440 (tỷ lệ gốc 100%, 0% vết ghép, 0% cắt mép chữ hay tấm sàn)
    vào khung vuông 1:1 (1200x1200) trên nền kem ấm đồng bộ kèm bóng đổ studio tinh tế & huy hiệu Vật liệu (1)/(2).
    """
    src = imread_unicode(card_path)
    sh, sw = src.shape[:2]  # 1440 x 1080

    bg_patch = src[int(sh * 0.25):int(sh * 0.30), int(sw * 0.02):int(sw * 0.08)]
    bg_color = tuple(int(c) for c in np.median(bg_patch.reshape(-1, 3), axis=0))
    canvas = np.full((1200, 1200, 3), bg_color, dtype=np.uint8)

    card_h = 1144
    card_w = int(round(sw * (card_h / float(sh))))  # 858px
    card_resized = cv2.resize(src, (card_w, card_h), interpolation=cv2.INTER_AREA)

    cx0 = (1200 - card_w) // 2  # 171px lề mỗi bên
    cy0 = (1200 - card_h) // 2  # 28px lề trên dưới

    shadow_mask = np.zeros((1200, 1200), dtype=np.float32)
    shadow_mask[cy0 + 8:cy0 + card_h + 8, cx0 + 6:cx0 + card_w + 6] = 0.15
    shadow_mask = cv2.GaussianBlur(shadow_mask, (35, 35), 12)
    for c in range(3):
        canvas[:, :, c] = (canvas[:, :, c].astype(np.float32) * (1.0 - shadow_mask)).astype(np.uint8)

    pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    card_pil = Image.fromarray(cv2.cvtColor(card_resized, cv2.COLOR_BGR2RGB))
    rmask = Image.new("L", (card_w, card_h), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=20, fill=255)
    pil.paste(card_pil, (cx0, cy0), rmask)

    draw = ImageDraw.Draw(pil, "RGBA")
    draw.rounded_rectangle([cx0, cy0, cx0 + card_w - 1, cy0 + card_h - 1], radius=20, outline=(215, 198, 182, 220), width=2)

    f_badge = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 19)
    f_num = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 19)

    GREEN = (19, 69, 50, 245)
    TERRA = (188, 92, 40, 255)

    label_txt = "VẬT LIỆU TRÊN VÁCH"
    bb = draw.textbbox((0, 0), label_txt, font=f_badge)
    tw = bb[2] - bb[0]
    pill_w = tw + 64
    px2 = cx0 + card_w - 18
    px1 = px2 - pill_w
    py1 = cy0 + 18
    py2 = py1 + 44

    draw.rounded_rectangle([px1, py1 + 3, px2, py2 + 3], radius=22, fill=(0, 0, 0, 50))
    draw.rounded_rectangle([px1, py1, px2, py2], radius=22, fill=GREEN, outline=(255, 255, 255, 230), width=2)

    cx, cy, cr = px1 + 24, (py1 + py2) // 2, 15
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=TERRA, outline=(255, 255, 255, 255), width=2)
    nb = draw.textbbox((0, 0), str(badge_idx), font=f_num)
    draw.text((cx - (nb[2] - nb[0]) // 2, cy - (nb[3] - nb[1]) // 2 - 3), str(badge_idx), font=f_num, fill=(255, 255, 255, 255))
    draw.text((px1 + 46, py1 + 10), label_txt, font=f_badge, fill=(255, 255, 255, 255))

    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def build_2x1_interior_and_splits(raw_scene_path: pathlib.Path, mat1_code: str, mat2_code: str) -> tuple:
    """
    Chuẩn hóa ảnh phối cảnh nội thất thành đúng tỷ lệ 2:1 (2400 x 1200), gắn tag thương hiệu & ghim (1), (2)
    né hoàn toàn đường cắt giữa x = 1200, sau đó cắt đôi thành 2 ảnh vuông 1:1 (1200x1200 Trái + 1200x1200 Phải).
    """
    bgr = imread_unicode(raw_scene_path)
    h, w = bgr.shape[:2]

    # Scale phủ kín 2400 x 1200 (ưu tiên giữ trọn phần vách tường trung tâm)
    target_w, target_h = 2400, 1200
    scale = max(target_w / float(w), target_h / float(h))
    nw, nh = int(round(w * scale)), int(round(h * scale))
    interp = cv2.INTER_CUBIC if scale > 1.0 else cv2.INTER_AREA
    resized = cv2.resize(bgr, (nw, nh), interpolation=interp)

    x0 = (nw - target_w) // 2
    # Lấy hơi thiên lên nửa trên một chút (0.44) để giữ trọn trần đèn LED hắt & vách Tivi/đầu giường
    y0 = int(round((nh - target_h) * 0.44))
    crop_2x1 = resized[y0:y0 + target_h, x0:x0 + target_w].copy()

    pil = Image.fromarray(cv2.cvtColor(crop_2x1, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil, "RGBA")

    f_tag = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-Bold.ttf"), 21)
    f_sub = ImageFont.truetype(str(FONT_DIR / "Inter-SemiBold.ttf"), 18)
    f_pin = ImageFont.truetype(str(FONT_DIR / "BeVietnamPro-ExtraBold.ttf"), 22)

    GREEN = (19, 69, 50, 228)
    TERRA = (188, 92, 40, 245)

    # 1) Nhãn góc Trên-Trái (nằm gọn trong tấm vuông 01: x = 42..560 < 1200)
    left_label = "NỘI THẤT MS – PHỐI MẪU KHÔNG GIAN THỰC TẾ"
    lb = draw.textbbox((0, 0), left_label, font=f_tag)
    lw = lb[2] - lb[0] + 44
    draw.rounded_rectangle([40, 36, 40 + lw, 86], radius=25, fill=GREEN, outline=(255, 255, 255, 210), width=2)
    draw.text((62, 48), left_label, font=f_tag, fill=(255, 255, 255, 255))

    # 2) Nhãn mã phối góc Trên-Phải (nằm gọn trong tấm vuông 02: x > 1250)
    right_label = f"Mã vật tư: {mat1_code}  ×  {mat2_code}"
    rb = draw.textbbox((0, 0), right_label, font=f_sub)
    rw = rb[2] - rb[0] + 44
    rx1 = 2400 - 40 - rw
    draw.rounded_rectangle([rx1, 36, 2400 - 40, 84], radius=24, fill=(28, 32, 30, 205), outline=(245, 212, 162, 220), width=2)
    draw.text((rx1 + 22, 49), right_label, font=f_sub, fill=(255, 242, 218, 255))

    # 3) Hai nút ghim vật liệu tinh tế (1) ở vùng lam sóng bên cánh & (2) ở vùng tấm ốp trung tâm (cách xa đường cắt giữa x=1200!)
    def draw_pin(cx, cy, num_str, code_str):
        cb = draw.textbbox((0, 0), code_str, font=f_sub)
        cw = cb[2] - cb[0]
        pw = cw + 64
        px1, py1 = cx - 22, cy - 22
        px2, py2 = px1 + pw, py1 + 44
        draw.rounded_rectangle([px1, py1 + 3, px2, py2 + 3], radius=22, fill=(0, 0, 0, 65))
        draw.rounded_rectangle([px1, py1, px2, py2], radius=22, fill=(255, 255, 255, 232), outline=TERRA, width=2)
        draw.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=TERRA)
        nb = draw.textbbox((0, 0), num_str, font=f_pin)
        draw.text((cx - (nb[2] - nb[0]) // 2, cy - (nb[3] - nb[1]) // 2 - 4), num_str, font=f_pin, fill=(255, 255, 255, 255))
        draw.text((cx + 24, cy - 10), code_str, font=f_sub, fill=(23, 62, 46, 255))

    # Đặt ghim (1) đúng giữa cánh lam sóng trái (x=360, y=270) và ghim (2) bên mảng PVC vân đá trung tâm (x=1360, y=270)
    draw_pin(360, 270, "1", mat1_code)
    draw_pin(1360, 270, "2", mat2_code)

    full_bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    left_sq = full_bgr[:, :1200].copy()
    right_sq = full_bgr[:, 1200:].copy()
    return full_bgr, left_sq, right_sq


def build_facebook_2x2_preview(sq1: np.ndarray, sq2: np.ndarray, sq3: np.ndarray, sq4: np.ndarray) -> np.ndarray:
    """Tạo ảnh mô phỏng chính xác giao diện lưới 4 ảnh vuông 2x2 trên Facebook (có khe trắng 8px ở giữa)."""
    s = 720
    a1 = cv2.resize(sq1, (s, s), interpolation=cv2.INTER_AREA)
    a2 = cv2.resize(sq2, (s, s), interpolation=cv2.INTER_AREA)
    a3 = cv2.resize(sq3, (s, s), interpolation=cv2.INTER_AREA)
    a4 = cv2.resize(sq4, (s, s), interpolation=cv2.INTER_AREA)
    g_v = np.full((s, 8, 3), 255, dtype=np.uint8)
    row1 = np.hstack([a1, g_v, a2])
    row2 = np.hstack([a3, g_v, a4])
    g_h = np.full((8, row1.shape[1], 3), 255, dtype=np.uint8)
    return np.vstack([row1, g_h, row2])


def compose_caption(day_item: dict) -> str:
    m1 = day_item["mat_1"]
    m2 = day_item["mat_2"]
    title = day_item["title"].strip().upper()
    angle = day_item["reference_angle"].split(":", 1)[-1].strip()
    return f"""✨ {title} ✨

{angle}

🔎 Bóc tách bộ đôi mã vật liệu tạo nên bức vách trong hình (xem chi tiết ở 2 ảnh vuông bên dưới):
1️⃣ Vật liệu (1): {m1['name']} – Mã {m1['code']} (Hiệu ứng sóng nổi 3D tạo chiều sâu sang trọng, che khuyết điểm tường).
2️⃣ Vật liệu (2): {m2['name']} – Mã {m2['code']} (Bề mặt bóng sáng, vân sắc nét, lau chùi nhẹ nhàng).

✅ Chống thấm nước, chống ẩm mốc & mối mọt 100% – cực hợp khí hậu biển Nha Trang.
✅ Thi công nhanh gọn ngay trong ngày, không bụi bặm, không mùi khó chịu.
✅ Sẵn kho hơn 100+ mẫu Lam sóng, PVC vân đá & Tấm than tre cắt theo kích thước thực tế.

📥 Anh/chị chỉ cần gửi ảnh bức tường + kích thước ngang cao, Nội Thất MS sẽ tư vấn phối mã màu chuẩn gu và báo giá trọn gói tận nơi ạ!
------------------------------------
Nội Thất MS – Chuyên ốp tường Nha Trang
📍 Địa chỉ: 46 Phù Sa, Vĩnh Ngọc, Nha Trang
🌐 Website: https://noithat.htmediakey.click/ | 📲 082 387 3287
#optuongnhatrang #noithatms #lamsongnhatrang #pvcvanda #vachtivinhatrang #caitaonhanhatrang
"""


def run_for_day(day_id: str = None, raw_scene_override: str = None) -> dict:
    plan_data = json.loads((PROJ_DIR / "30_ngay_ke_hoach_ms_noi_that.json").read_text(encoding="utf-8"))
    prog_path = PROJ_DIR / "daily_progress.json"
    prog = json.loads(prog_path.read_text(encoding="utf-8")) if prog_path.exists() else {"last_completed_index": -1, "completed_days": {}}

    days = plan_data["days"]
    if day_id:
        idx = next(i for i, d in enumerate(days) if d["day_id"] == day_id)
    else:
        idx = (int(prog.get("last_completed_index", -1)) + 1) % len(days)

    day_item = days[idx]
    did = day_item["day_id"]
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    local_out = PROJ_DIR / "output" / f"{today_str}_{did}_{day_item['slug']}"
    local_out.mkdir(parents=True, exist_ok=True)

    m1_path = pathlib.Path(day_item["mat_1"]["abs_path"])
    m2_path = pathlib.Path(day_item["mat_2"]["abs_path"])

    # Bước A: Tạo hoặc nạp ảnh phối cảnh nội thất 2:1 từ 2 mã vật liệu thật
    raw_scene_path = local_out / "_raw_interior_scene.jpg"
    if raw_scene_override and os.path.exists(raw_scene_override):
        shutil.copy2(raw_scene_override, raw_scene_path)
    elif not raw_scene_path.exists():
        import time as _time
        from ai_ref_video import (
            call,
            get_canvas_state,
            stage_local_ref_image_once,
            generate_ref_image_4tier,
            export_canvas_nodes_to_files,
            cleanup_exported_canvas_nodes,
        )
        # Đảm bảo đang đứng trên bảng Canvas có sẵn plugin 'export:folder' (NxSjY5F945m-fLx6nHjoU)
        r_state, _ = get_canvas_state()
        if not any(x.get("type") == "export:folder" for x in r_state.get("nodes", [])):
            projs = (call("canvas_list_projects", {}).get("result") or {}).get("items") or []
            for prj in projs:
                call("site_navigate", {"path": f"/canvas/{prj['id']}"})
                _time.sleep(1.5)
                rs2, _ = get_canvas_state()
                if any(x.get("type") == "export:folder" for x in rs2.get("nodes", [])):
                    break

        sw1 = extract_pure_swatch(m1_path, local_out / f"_swatch_{did}_1.jpg")
        sw2 = extract_pure_swatch(m2_path, local_out / f"_swatch_{did}_2.jpg")
        n1 = stage_local_ref_image_once(str(sw1), f"ms_{did}_m1")
        n2 = stage_local_ref_image_once(str(sw2), f"ms_{did}_m2")
        gen_nid, prov = generate_ref_image_4tier(
            prompt=day_item["scene_prompt"],
            ref_tag=f"ms_scene_{today_str.replace('-', '')}_{did}",
            ratio="16:9",
            reference_node_ids=[n1, n2],
        )
        export_canvas_nodes_to_files({gen_nid: str(raw_scene_path)})
        cleanup_exported_canvas_nodes([n1, n2, gen_nid])
        if not raw_scene_path.exists():
            raise RuntimeError("Failed to save generated interior scene from Canvas!")

    # Bước B: Dựng ảnh gốc 2:1 (2400x1200) + cắt đôi thành 01 & 02 (1200x1200) + 2 thẻ vuông vật liệu 03 & 04 (1200x1200)
    full_2x1, sq1, sq2 = build_2x1_interior_and_splits(
        raw_scene_path, day_item["mat_1"]["code"], day_item["mat_2"]["code"]
    )
    sq3 = make_square_material_card(m1_path, 1, day_item["mat_1"]["code"])
    sq4 = make_square_material_card(m2_path, 2, day_item["mat_2"]["code"])
    preview_2x2 = build_facebook_2x2_preview(sq1, sq2, sq3, sq4)
    caption_txt = compose_caption(day_item)

    files_map = {
        "00_Full_Vach_2x1_2400x1200.jpg": full_2x1,
        "01_Vach_Trai_1x1.jpg": sq1,
        "02_Vach_Phai_1x1.jpg": sq2,
        "03_Vat_Lieu_1_1x1.jpg": sq3,
        "04_Vat_Lieu_2_1x1.jpg": sq4,
        "99_Preview_Bo_Cuc_Facebook_2x2.jpg": preview_2x2,
    }
    for fname, im_bgr in files_map.items():
        imwrite_unicode(local_out / fname, im_bgr, quality=96)
    (local_out / "Caption.txt").write_text(caption_txt, encoding="utf-8")

    # Bước C: Đồng bộ sang Google Drive (MS Nội Thất\Bài Đăng Hàng Ngày + AI_Full_Studio)
    folder_name = f"{today_str} - {did} - {day_item['slug']}"
    drive_dir = DAILY_DRIVE_ROOT / folder_name
    backup_dir = CLOUD_BACKUP_ROOT / folder_name
    for target_root in [drive_dir, backup_dir]:
        target_root.mkdir(parents=True, exist_ok=True)
        for fname in list(files_map.keys()) + ["Caption.txt"]:
            shutil.copy2(local_out / fname, target_root / fname)

    result = {
        "date": today_str,
        "day_index": idx,
        "day_id": did,
        "title": day_item["title"],
        "mat_1_code": day_item["mat_1"]["code"],
        "mat_2_code": day_item["mat_2"]["code"],
        "local_dir": str(local_out),
        "drive_dir": str(drive_dir),
        "upload_files_in_order": [
            str(local_out / "01_Vach_Trai_1x1.jpg"),
            str(local_out / "02_Vach_Phai_1x1.jpg"),
            str(local_out / "03_Vat_Lieu_1_1x1.jpg"),
            str(local_out / "04_Vat_Lieu_2_1x1.jpg"),
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-id", default=None)
    ap.add_argument("--raw-scene", default=None)
    args = ap.parse_args()
    run_for_day(day_id=args.day_id, raw_scene_override=args.raw_scene)
