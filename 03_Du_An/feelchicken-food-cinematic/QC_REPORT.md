# Báo Cáo Kiểm Định Chất Lượng (QC Report) — Feel Chicken Food Cinematic (`V5 Authentic`)

## 1. Thông Số Kỹ Thuật Master MP4
- **Tệp xuất chuẩn**: `FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4`
- **Độ phân giải & Tốc độ khung hình**: `1080×1920 @ 30fps` (`27.60s` • `828 frames`)
- **Mã hóa phần cứng**: `NVIDIA RTX 3060 h264_nvenc` (`-preset p5 -rc vbr -cq 16`, `yuv420p`)
- **Chỉnh màu**: **`0%` (Giữ nguyên 100% màu sắc tự nhiên gốc của máy quay Sony Alpha A1 & ảnh món thật — không áp LUT, không nháy đen trắng, không phủ film-burn)**
- **Âm thanh**: Nhạc nền `Slow Cook Honey` + ASMR nấu ăn thực tế + Micro-SFX sạch (`I = -13.77 LUFS`, `TP = -0.98 dBTP`, `48kHz AAC 320kbps`, `0` giọng đọc)

## 2. Kết Quả Đối Chiếu Google Flow (`Omni 1.2 Flash`) vs Muse (`muse-video`) vs Sony `60fps`
- **Nguyên nhân lỗi bản V3/V4 đã khắc phục triệt để**:
  1. Sửa `flow-driver.json` kết nối đúng Project mới trên **Google Flow PRO (`Omni 1.2 Flash`)** thay vì rơi ngầm sang Muse.
  2. Loại bỏ hậu tố prompt người/môi cười gây xuất hiện mặt người trong bếp và loại bỏ prompt nền đen / găng tay đen.
  3. Dùng trực tiếp ảnh chụp Sony Alpha A1 thật (`A1_07833.jpg`, `A1_07871.jpg`, `A1_07983.jpg`, `A1_08995.JPG`) cắt chuẩn `9:16` ở chế độ `Thành phần` (`videoMode: "reference"`).
- **7 Điểm Nghiệm Thu Theo Yêu Cầu**:
  - **Image 1 (Áo bột)**: Thay hoàn toàn đùi gà sống giả bằng cảnh tô inox + vợt inox áo bột trắng mịn thật của bếp Feel Chicken (`SC01_flour_bowl_FLOW.mp4`, `0%` da gà giả, `0%` người).
  - **Image 2 (Bếp chiên)**: Dùng đúng mẫu bếp chiên nhúng inox đôi Hanaky của Feel Chicken được làm sạch sáng bóng chuyên nghiệp (`SC02_clean_fryer_FLOW.mp4`, **`0%` xuất hiện người/khuôn mặt/tay**).
  - **Image 3 (Vớt gà giòn)**: Xuất đối chiếu song song cả **Google Flow (`SC03_crispy_lift_FLOW.mp4`)** và **Muse (`SC03_crispy_lift_MUSE.mp4`)**, chọn bản lớp vảy bột giòn rụm tự nhiên không rỏ giọt dầu đặc giả.
  - **Image 4 (Đổ sốt)**: Dùng trực tiếp ảnh chụp chén inox đổ sốt thật của quán (`A1_07833.jpg` sốt đỏ Hàn Quốc trên **Flow** & `A1_07871.jpg` sốt phô mai trên **Muse**) phối cùng cảnh rắc mè quay thật Sony `60fps` (`m19_sesame_plate.MP4`).
  - **Image 5 (Xé gà)**: Dùng ảnh chụp găng tay nilon trong suốt thật của quán (`A1_07983.jpg` -> `SC06_clear_tear_MUSE.mp4`), thớ thịt trắng mọng thật, không găng đen, không khói giả.
  - **Image 6 (Mâm gà ngũ vị)**: Dùng ảnh mâm Gà Ngũ Vị thật (`A1_08995.JPG` -> `SC07_nguvi_orbit_MUSE.mp4`) đẩy máy quang học mượt mà + `m27_hero_macro1.MOV` (`0%` bàn tay găng đen).
  - **Typography & Màu sắc**: Thiết kế chữ đồng nhất 1:1 với bảng hiệu thật của Cơ sở 1 (`GÀ RÁN HÀN QUỐC` / `FEEL CHICKEN` / `ĂN LÀ MÊ, 사랑해` / `38 Nguyễn Đình Chiểu, Nha Trang • ĐT: 0979.233.139`), không chỉnh màu video.

## 3. Kiểm Định Nháp CapCut Desktop (`FEEL_CHICKEN_Food_Cinematic_Pro`)
- **Tổng số Track**: `6` (`3` Video Tracks: `16` clip gốc không chỉnh màu + `2` lớp chữ bảng hiệu `ProRes 4444` trong suốt; `3` Audio Tracks: BGM + ASMR + SFX).
- **Missing files**: `0`
- **Segment overlaps**: `0`
