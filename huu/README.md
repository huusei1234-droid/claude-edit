# Thư Mục Riêng Của Hữu Seiz (`huu/`)

Toàn bộ tài nguyên cá nhân của **Hữu Seiz** được gom gọn vào thư mục riêng `huu/` để tách bạch hoàn toàn với mã nguồn gốc của studio, giúp dễ quản lý và đồng bộ 1 chạm về máy tính ở nhà.

## Cấu Trúc Thư Mục

| Thư mục | Nội dung |
| :--- | :--- |
| **`huu/skills/`** | Trọn bộ **30 Skills AI** cá nhân (`talking-head-v3`, `kobe-motion-talking-head`, `tvc-qc-san-pham`, `capcut-pro-editor`, `photoshop-pro-studio`, `ps`, `viet-han-video-ban-hang`, `phim-ai-flow-prompt`, bộ 10 skills `hyperframes` & 13 skills `remotion`...). |
| **`huu/wallpapers/`** | Bộ **Hình nền động 4K Hữu Seiz** (`index.html` 40 cảnh + Màn hình khóa iPhone iOS 18 + Lịch Âm + Thời tiết + Trình quản lý tác vụ + Quick Launch), dịch vụ nền `sys_telemetry_server.py`, script tạo video `process_pinterest_*.py` và trình tự động cài `install_live_wallpapers_home.ps1`. *(Media 4K `.mp4`/`.jpg` nặng 3.66 GB được đồng bộ không nén tại Google Drive `AI_Full_Studio\05_Live_Wallpapers\Fresh_Muses_4K_Live\`)* |
| **`huu/rules_and_plugins/`** | Bộ quy chuẩn `GEMINI_GLOBAL.md`, `GEMINI_STUDIO.md` và các plugin Antigravity (`open-folder`, `gdrive`, `gsheets` — đã lọc sạch token/mật khẩu). |
| **`huu/fonts_tvc_vi/`** | Trọn bộ **72 tệp Font Tiếng Việt TVC & Preset Chữ Gradient**. |
| **`huu/sync_home_pc/`** | Bộ script đồng bộ tự động giữa máy công ty ↔ GitHub ↔ máy ở nhà. |

## Đồng Bộ Về Máy Ở Nhà (1 Chạm)
Chạy `huu/sync_home_pc/github_sync_22h_pull.ps1` (hoặc bấm shortcut **`Cập nhật từ GitHub ngay`** ngoài Desktop) — hệ thống sẽ tự động kéo toàn bộ `huu/skills/`, `huu/rules_and_plugins/`, `huu/fonts_tvc_vi/` và cài luôn bộ **Hình nền động 4K Hữu Seiz** vào Lively Wallpaper.
