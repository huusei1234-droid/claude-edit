# Báo Cáo Sản Xuất & Kiểm Định QC: `261121 HTPM 40 tuổi đầu tư gì lời nhất final.mp4`

## 1. Thông Tin Tổng Quan
- **Thương hiệu**: Hằng Thu Pharma (`HTPM`)
- **Chủ đề**: *40 tuổi đầu tư gì lời nhất? (100 triệu không mua túi hiệu — 6 khoản đầu tư sinh lời bền vững cho phụ nữ trưởng thành)*
- **Nguồn A-Roll Multi-Cam (2 góc máy)**:
  - **Cam A (Chính diện)**: `C:\Users\Hang thu\Downloads\HTPM.mp4` (`1080×1920 @ 30fps`, `2,064` frames = `68.800s`, đã cắt sạch phần đuôi đen)
  - **Cam B (Góc nghiêng 3/4)**: `C:\Users\Hang thu\Downloads\HTPM(1).mp4` (`1080×1920 @ 30fps`, đồng bộ âm thanh từng cụm jump-cut chính xác `±3ms` với Cam A qua sóng thoại thuần `Demucs htdemucs`)
- **Chỉnh màu & Tách nền RVM**: Áp LUT `01_HTPM_Beauty_Rosy_Skin.cube` (`55%`) + tách nền tóc RVM ONNX 2x cho cả Cam A và Cam B để chữ tiêu đề luồn tự nhiên sau đỉnh tóc (`y = 205..385`).

## 2. Nhịp Dựng Multi-Cam (`Cam A` × `Cam B`) & Xử Lý Che Vật Thừa Góc Trái
- `0.00s – 8.55s` (`Cam A`): Câu hỏi Hook + Zoom-In nhấn mạnh sau *"lời nhất?"* (`2.68s`) → Chuyển cảnh quang học `Sunlit Bloom` + `SFX Riser` đúng frame `8.55s`.
- `8.55s – 12.25s` (`Cam B`): Cắt sang góc nghiêng 3/4 khung `1.00x` mở thoáng khi chốt *"Hằng sẽ đầu tư vào sức khỏe!"*.
- `12.25s – 21.20s` (`Cam A`) → `21.20s – 26.38s` (`Cam B`): Đảo góc mượt ngay trong khung tròn `Iris Circle PiP` trên sân khấu `Full Kobe 9:16 Stage #1`.
- `26.38s – 30.80s` (`Cam A`) → `30.80s – 41.55s` (`Cam B`): Liệt kê 6 trụ cột đầu tư & 3 lợi ích lãi kép, đồng thời **che sạch 100% cánh tay người lọt mép trái của `Cam A` quanh mốc `37s`**.
- `41.55s – 45.58s` (`Cam A`) → `45.58s – 62.55s` (`Cam B`): Chuyển vào `Full Kobe 9:16 Stage #2` và mở ra lời nhắn tuổi `30–40+`, **che sạch 100% bóng người lọt mép trái của `Cam A` ở đoạn `56–60s`**.
- `62.55s – 68.80s` (`Cam A`): Quay về cận cảnh chính diện ấm áp chốt câu CTA *"càng có lời cho chị em mình đấy!"*.

## 3. Hệ Thống Đồ Họa `Kobe Living Motion` + `11` AI Video Clips (`0%` Lặp)
- **Zero-Clip `<svg class="svg-headline">`**: Đặt tại `top: 205px` (`y = 205..385`) ôm sát sau đỉnh tóc diễn giả trên cả 2 góc máy, không cắt mất dấu Tiếng Việt và không chạm trán.
- **Phụ đề `Be Vietnam Pro ExtraBold` nâng cao (`y = 1602..1668`)**: Viền tách lớp `stroke_w = 5`, đệm kính tối mờ `rgba(14,19,38,106)`, gộp chuẩn cụm `"30-40+,"`, hiệu ứng `Bidirectional Blur-Focus` mượt 2 chiều.
- **11 Cảnh AI Độc Lập Khóa Khuôn Mặt Diễn Giả (`0%` Loop)**:
  1. `inv_01a_bag_sleepless.mp4` (`16.22–19.20s`)
  2. `inv_01b_dress_fatigue.mp4` (`19.20–22.72s`)
  3. `inv_01c_makeup_tired.mp4` (`22.72–26.26s`)
  4. `inv_02a_sleep_nutrition.mp4` (`26.52–31.60s`)
  5. `inv_02b_fitness_knowledge.mp4` (`31.60–35.54s`)
  6. `inv_03a_love_body_early.mp4` (`45.70–49.40s`)
  7. `inv_03b_vitality_yoga.mp4` (`49.40–53.05s`)
  8. `inv_03c_confident_age.mp4` (`53.05–56.58s`)
  9. `inv_04a_family_energy.mp4` (`56.82–60.80s`)
  10. `inv_04b_smart_woman.mp4` (`60.80–64.75s`)
  11. `inv_04c_radiant_40_close.mp4` (`64.75–68.70s`)

## 4. Âm Thanh Chuẩn `-14.0 LUFS` (`Demucs Stem Rebalance`)
- Tách sạch `vocals.wav` + `no_vocals.wav` từ video gốc bằng `Demucs htdemucs`: giữ nguyên `100%` độ dày giọng nói Stereo ở tâm, hạ nhạc nền gốc mượt mà xuống `-7.1 dB` khi nói / `-4.7 dB` ở nhịp nghỉ (**không chèn đè bài nhạc thứ 2 gây rối âm**).
- Điểm `SFX Riser` cao trào đúng mốc `8.55s` + `Tactile Micro-SFX` xúc giác nâng dần cao độ (`+1.0` đến `+1.3 semitone`) và chuẩn hóa 2-pass `loudnorm` đạt **`-14.0 LUFS`**, True Peak **`<= -1.0 dBTP`**.
