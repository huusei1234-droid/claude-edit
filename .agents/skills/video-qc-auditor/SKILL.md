---
name: video-qc-auditor
description: Quy trình chuẩn chạy Trạm Kiểm Duyệt Video Độc Lập (video_qc_gate.py + subagent video-qc-auditor) cho mọi dự án video trước khi bàn giao. Kích hoạt bắt buộc ở bước nghiệm thu cuối của mọi dự án Phim AI, TVC, Talking-Head, CapCut, HyperFrames và Remotion.
---

# Quy Trình Kiểm Duyệt Thành Phẩm Video Toàn Hệ Thống (`video-qc-auditor`)

Mọi tệp video `.mp4` xuất Final đều bị khóa cứng bởi Lifecycle Hook `PreToolUse` (`video-qc-gate`) cho đến khi vượt qua đầy đủ 3 bước nghiệm thu độc lập dưới đây:

## Bước 1: Chạy Máy Quét Kỹ Thuật & Tách 100% Cú Cắt (`video_qc_gate.py inspect`)
Chạy công cụ trung tâm trên chính tệp `.mp4` vừa render xong:
```powershell
& "C:\AI\full studio\voice-studio\.venv\Scripts\python.exe" -X utf8 "C:\AI\full studio\edit\canvas-tools\video_qc_gate.py" inspect "<duong_dan_final.mp4>" --hook-end-sec <giay_ket_thuc_hook_neu_co> --out-dir "<thu_muc_qc>"
```
- Nếu lệnh trả mã lỗi `exit 2` (`MACHINE_FAIL` do lặp từ Whisper, đứt chữ cuối file, lệch Audio/Video hoặc viền đen thừa): **bắt buộc sửa/cắt/quay lại và render lại ngay**, không được chuyển sang Bước 2.

## Bước 2: Gọi Subagent Độc Lập `video-qc-auditor` Soi 100% Ô Hình & Logic
Gọi `invoke_subagent` với `TypeName: "video-qc-auditor"`, truyền rõ:
1. Đường dẫn tệp `<final.mp4>` và `<final.mp4>.qc_audit.json`.
2. Đường dẫn 2 bảng ảnh `QC_FINAL_ALL_CUTS_FULL.jpg` và `QC_FINAL_ALL_CUTS_ZOOM.jpg` (chứa **100% các cú cắt**, không được dùng bảng rút gọn!).
3. Đường dẫn ảnh sản phẩm thật (`SKU_REF`, nếu video có sản phẩm) và tóm tắt đường dây kịch bản để kiểm tra:
   - `0%` hộp trắng giả / hộp sai màu / nắp nhựa sai thiết kế;
   - `0%` hộp sản phẩm lòi ra ở cảnh không cần sản phẩm;
   - `100%` logic nhân quả (có cảnh giấu -> cảnh phát hiện -> cảnh mọi người bước nhanh/chạy tới bắt quả tang);
   - Đủ cảnh Toàn (`WS`/`MLS`) đan xen cảnh Trung/Cận (`MCU`/`CU`);
   - `0%` lặp từ, `0%` đứt chữ.

## Bước 3: Ký Chứng Nhận `.qc_pass.json` & Đồng Bộ Sang Drive/Local
- Khi `video-qc-auditor` xác nhận `PASS` và ký `<local_final.mp4>.qc_pass.json`, dùng `copy-cert` hoặc `final_delivery.py` để đồng bộ `.qc_pass.json` đi kèm tệp `.mp4` sang thư mục Kênh trên Google Drive, `04_Videos_Final` và `XUẤT CAPCUT`, sau đó mới gọi `show_file_location_card`.
