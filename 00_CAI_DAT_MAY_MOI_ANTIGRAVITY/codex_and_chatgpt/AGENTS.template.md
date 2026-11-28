# Quy Chuẩn Toàn Hệ Thống Full Studio (Áp Dụng Chung Cho OpenAI Codex & Infinite Canvas)

1. **Thư mục làm việc chính trên ổ SSD NVMe**: `C:\AI\full studio` (dữ liệu cấu hình tại `C:\AI\full studio_data\infinite-canvas-flow`, kho Google Drive đồng bộ tại `G:\My Drive\AI_Full_Studio`).
2. **Bảo vệ Phần mềm Đang Mở**: TUYỆT ĐỐI KHÔNG chạy `taskkill` / `Stop-Process` lên `CapCut.exe`, `VEDesktop.exe`, `Adobe Premiere Pro.exe`, `Photoshop.exe` hoặc `brave.exe` của người dùng khi chưa được phép.
3. **Vùng An Toàn Video Dọc `9:16` (`1080x1920` — `safe_zone_9x16.py`)**:
   - Không đặt chữ/phụ đề/thẻ UI chạm 5 vùng cấm TikTok & Reels: Đỉnh `Y < 248px`, Đáy `Y > 1548px`, Trái `X < 54px`, Phải trên `X > 1024px`, và Cột nút tương tác Dưới-Phải (`Y = 860..1548px`, giữ `X <= 884px`).
4. **Chuỗi Tạo Ảnh & Video Mặc Định**:
   - Tạo Ảnh AI: Ưu tiên số 1 **ChatGPT Plus** (`chatgpt::chatgpt-image`, 3 luồng song song trên Brave `:9333`), tự xóa đoạn chat nháp sau khi tải ảnh.
   - Tạo Video AI: Ưu tiên số 1 **Gemini Web Pro** (`gemini::gemini-video` `10s/15s` xoay hết các nick `u/0..u/9`) -> **Google Flow** (`flow::flow-omni-1.2-flash`) -> **OpenAI Sora Plus** (`chatgpt::sora-video`) -> **Muse**.
5. **Quy tắc Hằng Thu Pharma (`HTPM`), An Vượng Pharma (`AVPM`) & K4 Phim AI**:
   - Không mô tả hộp/chai sản phẩm trong prompt video AI nếu không truyền trực tiếp ảnh thật sản phẩm (`SKU_REF`) trong `refs`.
   - Với `AVPM` (nhân vật đại diện Chị Hậu): nhịp cắt nhanh `1.8s–2.7s`, 0% hiệu ứng bling-bling, đủ 4 bước pha chế gói bột liền mạch, mỗi video đổi trang phục/style mới.
   - Với `K4 Phim Chuyện Trong Nhà`: mỗi prompt video bắt buộc đủ 3 mục `IMAGE XUẤT HIỆN`, `CHỐT KHÔNG GIAN & VỊ TRÍ` (cuối cảnh trước = đầu cảnh sau), `BẮT ĐẦU PROMPT` (`1–15s` linh hoạt theo cảnh).
6. **Quy tắc Khóa Cứng Zalo**: Chỉ đọc dữ liệu khi quét nhóm; tuyệt đối không nhắn tin/tương tác bất kỳ nơi nào ngoài 3 hội thoại được phép (`Document`, `Quản lý MS`, `CT Hằng`).


























