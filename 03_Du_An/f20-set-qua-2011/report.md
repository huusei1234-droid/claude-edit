# Báo Cáo Nghiệm Thu & QC Dự Án: Thực Phẩm F20 × Yến Sào SKA NEST — Set Quà Tri Ân 20/11 (V7 Master)

## 1. Thông Số Kỹ Thuật Bản Xuất Chính Thức (V7 Final)
- **Định dạng**: `1080 × 1920` (`9:16` Vertical Reels/TikTok), `30.00 fps`, `H.264 + AAC 192kbps`
- **Thời lượng**: `143.40s` (`4.300 frames`)
- **Âm thanh chuẩn Broadcast**: `-13.9 LUFS` (nhạc nền `'Upbeat Ukulele'` + 28 điểm SFX tách trùng + giọng Chị Oanh đã lọc sạch vấp chữ)
- **Dung lượng**: `201.63 MB`

## 2. 04 Nâng Cấp Cốt Lõi Ở Bản V7
1. **Tạo Mới Bộ Ảnh Sản Phẩm Chuẩn Chữ 100% Qua `Muse` (`muse-image` `:18610`) & Giữ Tĩnh `1.00x` Không Zoom**:
   - Thay thế toàn bộ các clip AI bị biến dạng chữ bao bì bằng bộ 6 cảnh studio sản phẩm tạo trực tiếp từ **Muse** tham chiếu ảnh thật F20 (`muse_skanest_box.mp4`, `muse_two_jars.mp4`, `muse_hu_say_gion.mp4`, `muse_hu_say_me.mp4`, `muse_banh_thuyen.mp4`, `muse_kep_hat.mp4`), giữ tỷ lệ **`1.00x` không zoom** kết hợp lớp bụi ngọc trai mờ `10%`, đảm bảo chữ tiếng Việt sắc nét 100%.
2. **Hạ HSL Màu Cam (`-42%` Saturation), Giảm Độ Đậm Về Tự Nhiên & Chống Chói Sáng**:
   - Xây dựng bộ `33×33×33` `.cube` 3D LUT chuyên biệt (`lut_v7_showroom.cube`, `lut_v7_classroom.cube`, `lut_v7_outdoor.cube`, `lut_v7_product.cube`) kéo mạnh kênh **HSL Màu Cam (`Hue 14°–44°`, Saturation `-42%`)** và **Vàng (`-26%`)**, đưa quầy gỗ Showroom và mặt bàn lớp học về tông gỗ tự nhiên dịu mắt, hạ đỉnh sáng chống chói (`p98 <= 226`) và giữ độ bão hòa tự nhiên (`0.98x`).
3. **Thiết Kế Lại Toàn Bộ Typography 3D Không Hộp Nền Qua Headless Chrome (CSS3/SVG)**:
   - Bỏ hoàn toàn hộp nền chữ nhật và viền đen dày; render trực tiếp bằng trình duyệt Chrome (`Be Vietnam Pro ExtraBold` trắng ngà viền mảnh `2.8px` + từ khoá nhấn `Montserrat Black` **Gradient Vàng Champagne 5 điểm dừng đùn khối 3D** tách 2 lớp `.gold-back`/`.gold-front`), đặt đúng vùng an toàn TikTok phía dưới (`y = 1468–1530px`) kèm hiệu ứng xuất hiện lệch nhịp mượt mà.
4. **Dự Án CapCut `F20_SetQua_2011_SourceGoc` Trỏ Thẳng Tới 100% Source Gốc Camera Sony**:
   - Toàn bộ `22` vật liệu video trên Track 0 (`20` đoạn A-roll đã cắt sạch vấp) và Track 1 (`16` lớp phủ B-roll) trỏ trực tiếp tới các tệp `.MP4` gốc chưa qua encode trong `Z:/Máy tính khác/My Computer/F20/video gốc/261116/Chi Oanh/dọc/C3xxx.MP4` (`0` chữ, `0` nhạc, `0` hiệu ứng, `0` clip AI).

## 3. Đường Dẫn Bàn Giao & Lưu Trữ
- **Google Drive Master Final**: `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\F20_SET_QUA_2011_FINAL.mp4`
- **Thư mục Khách hàng TLH**: `Z:\Máy tính khác\My Computer\Document HT Media\TLH\f20-set-qua-2011_FINAL.mp4`
- **Bản sao Local**: `D:\XUẤT CAPCUT\F20_SET_QUA_2011_FINAL.mp4`
- **CapCut Desktop (`#1` trong `com.lveditor.draft`)**: `F20_SetQua_2011_SourceGoc`
