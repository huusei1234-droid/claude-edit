# -*- coding: utf-8 -*-
"""
Xây dựng & Đồng bộ Kế hoạch Tổng thể 30 Ngày (Mỗi ngày 10 Video USP 9:16 + 10 Ấn phẩm Thiết kế = 20 Ấn phẩm/ngày, 600 Ấn phẩm/tháng)
Phong cách: TRONG TRẺO — NẮNG BIỂN NHA TRANG (Crystal-Clear Coastal Nha Trang Lifestyle)
Nhân vật xuyên suốt: CEO Nguyễn Thị Hằng (tham chiếu từ https://www.facebook.com/hang.thu.146 — 16 ảnh gốc tại Nha Trang).
"""
import csv
import json
from pathlib import Path

PROJ_HUB = Path(r"d:\AI\full studio\03_Du_An\htpm-daily-1video-1post")
PROJ_HUB.mkdir(parents=True, exist_ok=True)

ARTIFACT_MD = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682\ke_hoach_content_30_ngay_htpm.md")
SIDECAR_JSON = Path(r"C:\Users\Hang thu\.gemini\config\sidecars\htpm-daily-1video-1post\sidecar.json")

DRIVE_HTPM_POSTS = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới")
CLOUD_HUB = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-daily-1video-1post")

# 10 Slot cố định mỗi ngày (cân đối 9 sản phẩm Hằng Thu Pharma + 1 slot Thương hiệu CEO/Hệ thống Nha Trang, có thể bật chế độ 6 HTPM + 4 AVPM linh hoạt)
TEN_DAILY_SLOTS = [
    ("Slot 01", "HTPM — Viên Đặt Phụ Khoa LT Plus", "Ban công căn hộ kính hướng Vịnh Nha Trang nắng sớm trong vắt", "Vest trắng kem khoác hờ vai + áo lụa trắng ngọc trai (Ref #01)"),
    ("Slot 02", "HTPM — Gel Phụ Khang Hằng Thu", "Phòng tắm & bàn vanity đá trắng ánh nắng ban mai dịu mát", "Đầm xanh băng pastel trễ vai thanh khiết (Ref #08)"),
    ("Slot 03", "HTPM — Dạ Dày HT", "Quán cà phê sân vườn nhiệt đới Nha Trang dưới tán cọ xanh", "Sơ mi trắng lụa thắt nơ thanh lịch + đồng hồ bạc (Ref #11)"),
    ("Slot 04", "HTPM — Điều Kinh HT (Bổ Trứng)", "Phòng khách Villa trắng đón gió biển Nha Trang & bình hoa tươi", "Đầm kem đính ngọc trai & áo khoác cape hoa hồng trắng (Ref #02)"),
    ("Slot 05", "HTPM — DDVS Romance VIP", "Khu nghỉ dưỡng Vinpearl / Marriott Nha Trang thảm cỏ xanh & hàng dừa", "Đầm maxi hồng cánh sen bay nhẹ trong nắng biển (Ref #13–#15)"),
    ("Slot 06", "HTPM — Viên Uống Trắng Da WhiteSkin", "Đường dạo biển Trần Phú / Bến du thuyền Nha Trang nắng trong trẻo", "Đầm vest trắng chiết eo tôn dáng dưới nắng biển (Ref #10)"),
    ("Slot 07", "HTPM — Viên Đặt Phụ Khoa (Hộp Xanh)", "Phòng điều hành CEO đá cẩm thạch sáng thoáng tại Nha Trang", "Blazer màu kem BNI thanh lịch + khuyên tai ngọc lục bảo (Ref #05)"),
    ("Slot 08", "HTPM — Viên Dưỡng Romance Love", "Không gian trà chiều Lounge kính hướng biển Nha Trang chiều dịu", "Set trắng tinh khôi cầm hoa hồng phấn nhẹ nhàng (Ref #12)"),
    ("Slot 09", "HTPM — Ngọc Long Hoàn", "Phòng làm việc sang trọng ánh sáng tự nhiên ấm áp", "Suit đỏ đô quyền lực của nữ doanh nhân (Ref #03)"),
    ("Slot 10", "CEO Nguyễn Thị Hằng × Hệ Thống / An Vượng", "Hội trường biển / Sân vườn đào tạo đội nhóm 15.000 thành viên tại Nha Trang", "Vest xanh navy phối chuỗi ngọc trai hoặc Suit xanh trẻ trung (Ref #07/#09)"),
]

WEEKLY_ANGLES = [
    ("Tuần 1 (Ngày 01–07)", "Nhịp Sống Phố Biển Trong Trẻo & Thói Quen Chăm Sóc Chủ Động", "Câu chuyện đời thường gần gũi tại Nha Trang, chạm tâm lý thầm kín tinh tế"),
    ("Tuần 2 (Ngày 08–14)", "Giải Mã Hiểu Lầm Thường Gặp & Chuẩn Thảo Dược Lành Tính", "Góc nhìn ngược đám đông nhẹ nhàng, trực quan hóa bằng lớp phủ Slide kính mờ"),
    ("Tuần 3 (Ngày 15–21)", "Hành Trình Tự Tin Rạng Rỡ Của Phụ Nữ Hiện Đại", "Chuyển hóa cảm xúc từ mệt mỏi sang nhẹ nhõm, yêu bản thân & giữ lửa hạnh phúc"),
    ("Tuần 4 (Ngày 22–30)", "Tỏa Sáng Cuối Năm & Bứt Phá Cùng Hệ Thống CEO Nguyễn Thị Hằng", "Truyền cảm hứng tự chủ tài chính, quà tặng sức khỏe gia đình & bùng nổ doanh số"),
]


def build_dna_md() -> str:
    return """# HỒ SƠ KHÓA NHÂN VẬT CHỊ HẰNG (SỐNG TẠI NHA TRANG) & QUY CHUẨN 10 VIDEO + 10 THIẾT KẾ / NGÀY

> **Nguồn tham chiếu nhân vật chính thức**: `https://www.facebook.com/hang.thu.146` (**CEO Nguyễn Thị Hằng** — `65K followers`, sống & làm việc tại **TP. Nha Trang**, dẫn dắt hệ thống `15.000+` thành viên Hằng Thu Pharma & An Vượng Pharma).
> **Kho 16 ảnh gốc độ phân giải cao đã tải về máy & Cloud**:
> - Local Brand Kit: `d:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\brand_kits\\01_HTPM_Hang_Thu_Pharma\\ambassadors_models\\FB_Hang_Thu_146_Nha_Trang\\`
> - Google Drive HTPM: `Z:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\00_Ho_So_Thuong_Hieu_Va_Tham_Khao\\FB_Hang_Thu_146_Nha_Trang\\`

---

## 1. Khóa Thẩm Mỹ Bắt Buộc: "HÌNH ẢNH TRONG TRẺO — PHỐ BIỂN NHA TRANG"
1. **Ánh sáng & Màu sắc trong trẻo (`Crystal-Clear Nha Trang Daylight`)**:
   - Mọi khung hình Video AI và Ảnh Thiết Kế bắt buộc mang hơi thở **trong trẻo, thoáng sáng, sạch mịn tự nhiên** của nắng sớm và gió biển Nha Trang (`5200K–5500K` high-key daylight).
   - Làn da chị Hằng trắng hồng tự nhiên, đôi mắt sáng có hồn, môi đỏ tươi / đỏ cam rạng rỡ đúng chuẩn ảnh đời thực trên Facebook `hang.thu.146`.
   - **Cấm tuyệt đối**: nền tối u ám, ám vàng đục ngầu, chữ vàng 3D AI sến lố, hoặc vẽ sai Logo `HT` gốc!
2. **10 Bối Cảnh Đời Thực Tại Nha Trang Xoay Vòng Trong Ngày (`0%` trùng bối cảnh giữa 10 video cùng ngày)**:
   - Ban công căn hộ hướng Vịnh Nha Trang rèm voan trắng bay nhẹ · Quán cà phê sân vườn lá cọ nắng xuyên tán cây · Thảm cỏ xanh & hàng dừa trắng khu nghỉ dưỡng Vinpearl/Marriott Nha Trang · Phòng CEO đá cẩm thạch sáng · Villa trắng đón gió biển · Đường biển Trần Phú sáng sớm · Phòng trà chiều view biển · Góc vanity trắng tinh khôi · Bếp đảo đá trắng dinh dưỡng gia đình · Không gian mentoring đội nhóm sang trọng tại Nha Trang.
3. **10 Tạo Hình Trang Phục Mỗi Ngày (Tham chiếu trực tiếp từ 16 ảnh Facebook `01..16`)**:
   - Mỗi sản phẩm trong 10 Video & 10 Thiết kế của cùng 1 ngày mang 1 bộ trang phục riêng biệt (Vest trắng khoác vai, Đầm xanh băng pastel, Sơ mi trắng thắt nơ, Đầm kem cape hoa hồng, Maxi hồng dạo resort biển Nha Trang, Đầm vest trắng chiết eo, Blazer kem BNI, Set trắng hoa hồng phấn, Suit đỏ đô, Vest navy ngọc trai), biến tấu chất liệu/màu pastel nhẹ qua từng ngày để 30 ngày không bao giờ nhàm chán.

---

## 2. Kiến Trúc Chia 3 Ca Tự Động Sản Xuất `10 Video + 10 Thiết Kế / Ngày` (`20 Ấn Phẩm / Ngày`)
Để sản xuất mượt mà **10 Video Dọc `9:16` (`1080×1920 @ 24fps`) + 10 Bài Thiết Kế (`1600×2000 4:5` sRGB `.JPG` + `.PSD`)** mỗi ngày trên GPU `RTX 4070` mà không nghẽn tài nguyên:
- **Ca 1 (`08:00` — hoặc ngay khi mở máy buổi sáng)**: Sản xuất **Video `01 → 04` + Thiết kế `01 → 04`** (`8 ấn phẩm`).
- **Ca 2 (`11:15` — giữa ngày)**: Sản xuất **Video `05 → 07` + Thiết kế `05 → 07`** (`6 ấn phẩm`).
- **Ca 3 (`14:00` — hoàn tất trước `16:30`)**: Sản xuất **Video `08 → 10` + Thiết kế `08 → 10`** (`6 ấn phẩm` -> Chốt đủ **`10/10 Video + 10/10 Thiết kế`**!).
- **Cơ chế chống đứt quãng (`Checkpoint Resume`)**: File `daily_progress.json` lưu chi tiết tiến độ từng slot `V01..V10` và `P01..P10`. Nếu máy tính mở muộn hoặc tắt ngang, ngay lần kích hoạt kế tiếp hệ thống tự nối tiếp đúng từ slot đang dở cho tới khi đủ `10 Video + 10 Thiết kế` trong ngày!
"""


def build_schedule_md_and_csv():
    lines = [
        "# Kế Hoạch & Lịch Sản Xuất Tự Động 30 Ngày — 10 Video + 10 Thiết Kế / Ngày (Phong Cách Trong Trẻo Nha Trang)",
        "",
        "**Định mức mới đã cân đối:** `10 Video USP Dọc 9:16 (24fps)` **+** `10 Ấn Phẩm Thiết Kế (1600×2000 4:5 + .PSD)` **= `20 Ấn phẩm / ngày` (`600 Ấn phẩm / 30 ngày`)**",
        "**Nhân vật xuyên suốt:** **CEO Nguyễn Thị Hằng** ([facebook.com/hang.thu.146](https://www.facebook.com/hang.thu.146)) — Hình ảnh **trong trẻo, tươi sáng tự nhiên tại phố biển Nha Trang**.",
        "",
        "> [!IMPORTANT]",
        "> **Quy chuẩn Vàng cho cả 20 Ấn phẩm mỗi ngày:**",
        "> 1. **Hình ảnh trong trẻo Nha Trang (`Crystal-Clear Coastal Daylight`)**: Nắng tự nhiên sáng mịn, gió biển, hàng dừa, villa trắng, quán cà phê sân vườn nhiệt đới, ban công hướng biển Nha Trang & phòng CEO đá trắng thoáng đãng.",
        "> 2. **10 Video Dọc `9:16` (`1080×1920 @ 24fps` ONLY)**: Giọng `THANH THANH TVC` · Viết hoa `100%` đầu câu · `0%` chữ che mặt chị Hằng (`Face-Safe`) · Đan xen **4–6 Lớp phủ Slide kính mờ động** · Nằm gọn `100%` trong Vùng An Toàn TikTok × Reels.",
        "> 3. **10 Ấn Phẩm Thiết Kế (`1600×2000 4:5` sRGB `.JPG` + `.PSD` đa layer)**: Gắn chuẩn **Logo tròn `HT` gốc 33MP** (`0%` sai logo), ghép **100% hộp sản phẩm thật `IS-Net`**, bảng màu trong trẻo thanh lịch hoặc nổi bật hiện đại theo chủ đề, cỡ chữ rõ nét đọc ngay trên điện thoại.",
        "",
        "---",
        "",
        "## 1. Ma Trận Phân Bổ 10 Video + 10 Thiết Kế Trong Mỗi Ngày (Chia 3 Ca Tự Động)",
        "",
        "| Ca Chạy | Slot | Sản Phẩm / Chủ Đề | Bối Cảnh Trong Trẻo Tại Nha Trang | Tạo Hình Tham Chiếu Từ FB `hang.thu.146` | Đầu Ra Trong Ngày |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for idx, (slot, prod, loc, look) in enumerate(TEN_DAILY_SLOTS, start=1):
        ca = "Ca 1 (08:00)" if idx <= 4 else ("Ca 2 (11:15)" if idx <= 7 else "Ca 3 (14:00)")
        lines.append(f"| **{ca}** | **{slot}** | **{prod}** | {loc} | {look} | `01 Video 9:16` + `01 Thiết kế 4:5` |")

    lines += [
        "",
        "---",
        "",
        "## 2. Lộ Trình Chủ Đề & Biến Tấu Góc Kể Chuyện Xuyên Suốt 30 Ngày (`600 Ấn Phẩm`)",
        "",
        "| Ngày | Tuần & Tinh Thần Chủ Đạo | Góc Hook 10 Video USP 9:16 Trong Ngày (`V01 → V10`) | Chủ Đề 10 Ấn Phẩm Thiết Kế Trong Ngày (`P01 → P10`) | Bối Cảnh Điểm Nhấn Nha Trang |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    csv_rows = []
    hook_variants = [
        ("Buổi sáng đón nắng biển Nha Trang & thói quen nhỏ giúp cơ thể nhẹ tênh", "Key Visual Trong Trẻo Nắng Sớm Nha Trang + 3 Điểm Chạm Lành Tính"),
        ("Giải mã hiểu lầm nhiều chị em hay mắc phải khi bận rộn cả ngày", "Infographic So Sánh Tinh Tế & Bộ Thảo Dược Tự Nhiên Chuẩn Sở Y Tế"),
        ("Bí quyết giữ năng lượng rạng rỡ từ văn phòng đến chiều dạo phố biển", "Editorial Lifestyle Chị Hằng Tại Nha Trang × Sản Phẩm Chủ Lực"),
        ("Tâm sự thật của phụ nữ sau tuổi 30: Yêu thương bản thân đúng cách", "Bento 4 Thảo Dược Tinh Khiết Trên Mặt Nước & Đá Trắng Trong Trẻo"),
        ("Lịch trình 1 ngày bận rộn của CEO 15.000 thành viên vẫn luôn tươi tắn", "Poster Truyền Lửa Kinh Doanh Bằng Giá Trị Thật & Hệ Sinh Thái Sản Phẩm"),
        ("Cuối tuần thư thái tại resort biển Nha Trang: Nhỏ gọn mang theo mọi nơi", "Resort Chic Key Visual Dưới Hàng Dừa Xanh & Cẩm Nang Sử Dụng Nhanh"),
        ("Chăm sóc sức khỏe chủ động cho cả gia đình từ gốc thảo dược Việt", "Bộ Ấn Phẩm Gia Đình Hạnh Phúc & Cam Kết Chất Lượng Chính Hãng"),
    ]

    from datetime import date, timedelta
    start_d = date(2026, 11, 24)
    for d_idx in range(30):
        cur_d = start_d + timedelta(days=d_idx)
        d_str = cur_d.strftime("%d/%m/%Y")
        w_idx = min(3, d_idx // 7)
        w_name, w_theme, _ = WEEKLY_ANGLES[w_idx]
        hv_vid, hv_post = hook_variants[d_idx % len(hook_variants)]
        nt_spot = TEN_DAILY_SLOTS[d_idx % len(TEN_DAILY_SLOTS)][2]
        day_label = f"Ngày {d_idx+1:02d} ({d_str})"
        lines.append(
            f"| **{day_label}** | **{w_theme}** | **10 Video (`V01..V10`)**: {hv_vid} *(xoay đủ 10 Slot SP, đổi 10 bộ trang phục không trùng)* | **10 Thiết kế (`P01..P10`)**: {hv_post} *(chuẩn Logo HT gốc 33MP + `.PSD`)* | {nt_spot} |"
        )
        for s_idx, (slot, prod, loc, look) in enumerate(TEN_DAILY_SLOTS, start=1):
            csv_rows.append([
                day_label,
                f"Ca {1 if s_idx<=4 else (2 if s_idx<=7 else 3)}",
                slot,
                prod,
                f"[Video V{s_idx:02d} 9:16] {hv_vid}",
                f"[Thiết kế P{s_idx:02d} 4:5] {hv_post}",
                f"{loc} (Nha Trang — Trong trẻo)",
                look,
            ])

    return "\n".join(lines) + "\n", csv_rows


def update_sidecar():
    sidecar_data = {
        "builtin": "schedule",
        "args": [
            "CRON_TZ=Asia/Ho_Chi_Minh 5 8,10,11,13,14,15 * * *",
            "agentapi",
            "new-conversation",
            "--",
            (
                "Tự động sản xuất theo Ca định mức hằng ngày cho CEO Nguyễn Thị Hằng (Hằng Thu Pharma) với mục tiêu ĐỦ 10 VIDEO USP DỌC 9:16 (@24fps) + 10 ẤN PHẨM THIẾT KẾ (1600x2000 4:5 + .PSD) MỖI NGÀY — Phong cách HÌNH ẢNH TRONG TRẺO SỐNG TẠI NHA TRANG:\n"
                "1. Đọc `d:/AI/full studio/03_Du_An/htpm-daily-1video-1post/daily_progress.json`. Kiểm tra tiến độ ngày hôm nay (`YYYY-MM-DD` theo `Asia/Ho_Chi_Minh`): nếu đã đủ `completed_videos >= 10` và `completed_posts >= 10` (`status == \"done\"`), báo ngắn gọn đã hoàn thành đủ 10 Video + 10 Thiết kế hôm nay và DỪNG NGAY.\n"
                "2. Nếu chưa đủ `10 + 10`: đọc `d:/AI/full studio/03_Du_An/htpm-daily-1video-1post/LICH_30_NGAY_HTPM_10VIDEO_10POST_NHA_TRANG.md` và kho 16 ảnh mẫu đời thực Nha Trang tại `d:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/brand_kits/01_HTPM_Hang_Thu_Pharma/ambassadors_models/FB_Hang_Thu_146_Nha_Trang/` (`HO_SO_NHAN_VAT_CHI_HANG_NHA_TRANG_FB.md`).\n"
                "3. Chủ động bật bền vững Full Studio (`ensure_studio_services.ps1` qua `Win32_Process.Create`; cấm tuyệt đối `taskkill`/`Stop-Process`).\n"
                "4. Chạy tiếp lô Ca hiện tại (mỗi ca xử lý tuần tự/song song 3–4 cặp Video 9:16 + Thiết kế 4:5 bằng `generate_ref_images_parallel_batch(max_workers=3)` + `generate_videos_parallel_batch(max_workers=4)` + GPU `h264_nvenc` cho đến khi hoàn tất đủ 10/10 Video + 10/10 Thiết kế của ngày):\n"
                "   - **Hình ảnh BẮT BUỘC trong trẻo, tươi sáng tự nhiên tại Nha Trang** (ban công hướng biển, hàng dừa resort trắng, quán cà phê sân vườn nắng sớm, villa đón gió biển, phòng CEO đá sáng), giữ chuẩn 100% gương mặt chị Hằng từ bộ 16 ảnh Facebook `hang.thu.146` và thay trang phục riêng cho từng slot.\n"
                "   - **10 Video Dọc `9:16` (`1080x1920 @ 24fps` ONLY)**: Giọng `THANH THANH TVC`, viết hoa 100% đầu câu, 0% chữ che mặt, chèn 4–6 Lớp phủ Slide kính mờ động, chuẩn Vùng An Toàn TikTok × Reels.\n"
                "   - **10 Thiết Kế (`1600x2000 4:5` sRGB `.JPG` + `.PSD`)**: Chuẩn 100% Logo tròn `HT` gốc 33MP (`ht_logo_official.png`), 100% hộp sản phẩm thật `IS-Net`, cỡ chữ to rõ, trong trẻo bắt mắt, 0% chữ vàng AI.\n"
                "5. Lưu từng Video vào `05. Video Hoàn Thiện/K6 - Hằng Thu Pharma/` (`<YYMMDD> HTPM <tên> final.mp4`), lưu từng Thiết kế vào `01. Hình Đăng Bài & Bài Viết Mới/HTPM_Daily_Content/Ngay_XX_DDMM/`, cập nhật `daily_progress.json` sau mỗi ca và hiển thị thẻ 1 chạm `open-folder_explorer/show_file_location_card`."
            ),
        ],
        "restart_policy": "always",
        "display_name": "Hằng Thu Pharma Nha Trang Daily — 10 Videos + 10 Thiết Kế",
        "description": "Tự động chia 3 ca chạy mỗi ngày ngay khi máy mở (08:05, 10:05, 11:05, 13:05, 14:05, 15:05) để sản xuất đủ 10 Video USP Dọc 9:16 + 10 Ấn phẩm Thiết kế (.JPG + .PSD) phong cách trong trẻo phố biển Nha Trang (nhân vật CEO Nguyễn Thị Hằng từ facebook.com/hang.thu.146).",
        "agent_permissions": {
            "workspace_uris": ["file:///d:/AI/full%20studio"],
            "access_grants": [
                "command(powershell -NoProfile -ExecutionPolicy Bypass -File \"d:/AI/full studio/03_Du_An/htpm-daily-1video-1post/ensure_studio_services.ps1\")",
                "command(d:/AI/full studio/voice-studio/.venv/Scripts/python.exe)",
                "command(D:/AI/full studio/voice-studio/.venv/Scripts/python.exe)",
                "command(C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe)",
                "command(C:/Program Files/Microsoft/Edge/Application/msedge.exe)",
                "command(node)",
                "command(ffmpeg)",
                "command(ffprobe)",
                "command(npx.cmd hyperframes check)",
                "command(npx.cmd hyperframes render)",
                "read_file(d:/AI/full studio)",
                "write_file(d:/AI/full studio)",
                "write_file(D:/full studio_data/infinite-canvas-flow)",
                "read_file(C:/Users/Hang thu/AppData/Roaming/infinite-canvas-flow)",
                "read_file(Z:/.shortcut-targets-by-id/1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-/hằng thu pharma)",
                "write_file(Z:/.shortcut-targets-by-id/1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-/hằng thu pharma)",
                "read_file(Z:/Drive của tôi/AI_Full_Studio)",
                "write_file(Z:/Drive của tôi/AI_Full_Studio)",
                "write_file(D:/XUẤT CAPCUT/hằng thu pharma)",
                "mcp(open-folder_explorer/show_file_location_card)",
            ],
        },
    }
    SIDECAR_JSON.parent.mkdir(parents=True, exist_ok=True)
    SIDECAR_JSON.write_text(json.dumps(sidecar_data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    dna_txt = build_dna_md()
    sched_md, csv_rows = build_schedule_md_and_csv()

    (PROJ_HUB / "MODEL_DNA_LOCK_CHI_HANG_HTPM.md").write_text(dna_txt, encoding="utf-8")
    (PROJ_HUB / "LICH_30_NGAY_HTPM_10VIDEO_10POST_NHA_TRANG.md").write_text(sched_md, encoding="utf-8")
    ARTIFACT_MD.write_text(sched_md, encoding="utf-8")

    csv_local = PROJ_HUB / "261124_LICH_30_NGAY_10VIDEO_10THIETKE_NHA_TRANG_EXCEL.csv"
    with open(csv_local, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Ngày", "Ca Tự Động", "Slot Trong Ngày (1..10)", "Sản Phẩm / Chủ Đề",
            "Video USP Dọc 9:16 (24fps)", "Ấn Phẩm Thiết Kế 4:5 (.JPG + .PSD)",
            "Bối Cảnh Trong Trẻo Tại Nha Trang", "Tạo Hình Chị Hằng (FB hang.thu.146)"
        ])
        w.writerows(csv_rows)

    # Update daily_progress.json schema for 10x10 tracking (preserving the 1 video + 2 posts already completed today!)
    prog_p = PROJ_HUB / "daily_progress.json"
    prog = {
        "campaign": "HTPM Nha Trang Crystal-Clear Daily 10 Videos + 10 Posts",
        "daily_quota": {"videos_9x16": 10, "designs_4x5": 10},
        "character_ref_hub": "d:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/brand_kits/01_HTPM_Hang_Thu_Pharma/ambassadors_models/FB_Hang_Thu_146_Nha_Trang",
        "days": {
            "2026-11-24": {
                "status": "in_progress",
                "completed_videos": 1,
                "completed_posts": 2,
                "notes": "Đã xong Video 01 (LT Plus) + Thiết kế 01 (Gel Phụ Khang Soft Editorial) + Poster Họp Zoom 19h V3.",
            }
        },
    }
    prog_p.write_text(json.dumps(prog, ensure_ascii=False, indent=2), encoding="utf-8")

    update_sidecar()

    for gdir in (DRIVE_HTPM_POSTS, CLOUD_HUB):
        try:
            if Path(gdir.anchor).exists():
                gdir.mkdir(parents=True, exist_ok=True)
                (gdir / "261124_LICH_30_NGAY_10VIDEO_10THIETKE_NHA_TRANG.md").write_text(sched_md, encoding="utf-8")
                with open(gdir / "261124_LICH_30_NGAY_10VIDEO_10THIETKE_NHA_TRANG_EXCEL.csv", "w", encoding="utf-8-sig", newline="") as f:
                    w = csv.writer(f)
                    w.writerow([
                        "Ngày", "Ca Tự Động", "Slot Trong Ngày (1..10)", "Sản Phẩm / Chủ Đề",
                        "Video USP Dọc 9:16 (24fps)", "Ấn Phẩm Thiết Kế 4:5 (.JPG + .PSD)",
                        "Bối Cảnh Trong Trẻo Tại Nha Trang", "Tạo Hình Chị Hằng (FB hang.thu.146)"
                    ])
                    w.writerows(csv_rows)
                print(f"[SYNCED 10x10 SCHEDULE] {gdir}")
        except Exception as e:
            print(f"[WARN SYNC] {gdir}: {e}")

    print(f"[DONE 10x10 MASTER PLAN] Total scheduled items = {len(csv_rows)} pairs ({len(csv_rows)*2} assets / 30 days)")


if __name__ == "__main__":
    main()
