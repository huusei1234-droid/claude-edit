# Báo cáo bàn giao — BOJOMI An Vượng (`v4 Master` chuẩn `video mẫu.mov`)

## 1. File đầu ra đã kiểm chứng kỹ thuật
- **File Final xuất trên Google Drive (`Z:\Drive của tôi`)**:
  - `Z:\Drive của tôi\BOJOMI_TALKING_HEAD_FINAL.mp4` (`1080×1920`, `30 fps`, `1992` khung = `66.40s`, `-14.0 LUFS`)
- **Video Master MP4 trong thư mục dự án**:
  - `D:\AI\full studio\output\av-protein-talking-head\bojomi_talking_head_v4_final.mp4`
  - Bản sao đồng bộ: `D:\AI\full studio\output\av-protein-talking-head\bojomi_final.mp4`
- **Dự án CapCut Desktop tách 4 tầng âm thanh riêng (`BOJOMI_AnVuong_TalkingHead_v4_Master`)**:
  - `C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\BOJOMI_AnVuong_TalkingHead_v4_Master`
  - Gồm `Track 0` (Video cắt sẵn theo phân đoạn) + **4 Stems WAV 48kHz độc lập** trong `D:\AI\full studio\output\av-protein-talking-head\audio_stems_v4\` (`01_Voice_Master.wav`, `02_BGM_Ducked.wav`, `03_SFX_Transitions_Risers.wav`, `04_SFX_Pops_Shutters_Ticks.wav`) để bạn có thể tăng/giảm riêng từng nhóm SFX, nhạc nền hoặc giọng đọc ngay trong CapCut.

---

## 2. Sáu (6) nâng cấp lớn từ `v3` lên `v4 Master` (bám sát 100% `video mẫu.mov`)
1. **Hệ thống Sound Design 146 điểm SFX Stereo (18 nhạc cụ SFX thật từ kho CapCut & `D:\Edit\Sound Effect`)**:
   - Chuẩn hóa đỉnh `0 dBFS` từng file trước khi trộn và căn **chính xác mili-giây đỉnh sóng âm (`peak_at`)** trùng khớp khung hình.
   - Đầy đủ 6 lớp như `video mẫu.mov`: `SFX - Riser Metallic` & `riser.mp3` dâng đúng vào điểm rơi số `1 / 2 / 3` & B-roll; `Deep woosh` + `SWOOSH #5` ra/vào thẻ 3D; `Camera shutter (analog)` đanh gọn cho toàn bộ 12 nhịp chữ lớn sau đầu; `Pop telop` / `Pop - chữ` / `Poyoi` / `Noitifi` / `Slide up & ngang` có pan trái-phải theo vị trí thẻ; `Magic reveal` cho vòng tròn quỹ đạo; và `Caption micro-ticks` nhẹ (`-16 dB`) tạo nhịp cuốn tai mà không lấn giọng.
   - Nhạc nền C-major có EQ hốc giọng (`-3.5 dB @ 2.2kHz`) và tự động nâng nhẹ khi sang cảnh B-roll; tổng thể đo `ebur128` đạt chuẩn **`-14.0 LUFS` (`LRA: 3.1 LU`)**.
2. **Xử lý nền thông minh (Nền thật ấm-trong khi nói bình thường × Bokeh tối sâu điện ảnh `88%` khi có Animation)**:
   - Khi dược sĩ nói bình thường: giữ nguyên phòng thật với lớp chỉnh màu ấm, trong trẻo.
   - Khi xuất hiện bất kỳ chữ/số/icon/vòng tròn nào: tự động làm mờ ống kính (`Bokeh`) + hạ tối sâu `88%` phía sau người tách nền RVM, xóa sạch chữ cam/xanh rối mắt trên tường để hiệu ứng neon nổi bật tuyệt đối (không còn lỗi chữ đè lên tường trắng).
3. **Thẻ Kính Đen Viền Sáng (`Obsidian Neon Tile` + `EdgeSweep` + `T.burst`)**:
   - Thay hoàn toàn các ô vuông màu nhạt cũ bằng thẻ kính đen `#0e1119` có quầng sáng tím-lam, vệt sao chổi chạy vòng quanh viền, icon nét neon phát sáng sắc nét, bay lên kèm nhòe chuyển động dọc (`directional motion blur`) và vòng nổ trắng `T.burst`.
4. **Thẻ B-Roll Phối Cảnh Camera 3D Xếp Lớp (`True 3D Homography`, `0%` méo hình)**:
   - Bỏ thanh chữ xanh cắt ngang màn hình; dựng đúng phối cảnh Camera 3D của `video mẫu.mov`: lớp video dưới nghiêng chéo 3D trên nền nhám tối (`BG_Grain`), thẻ video bo góc nổi phía trước (`z = -250`) đè lên mép trên và đổ bóng sâu 3D xuống lớp dưới, giữ tỷ lệ hình ảnh chuẩn `100%`.
5. **Số Neon `900px` (`1 / 2 / 3` + Tia điện) & 12 Nhịp Chữ Lớn Cài Sau Mái Tóc (`T.behind`)**:
   - Đặt tại cao độ chuẩn để phần tóc trên đỉnh đầu dược sĩ che nhẹ ~15–20% chân chữ tạo chiều sâu 3D thật sự (không chạm trán/mắt), đổi từ khóa liên tục theo lời nói.
6. **Phụ Đề Phát Sáng Cỡ Lớn (`84–104px`) + Nổ Viền Rỗng `Stroke Up` + `19` Nhịp Camera Zoom + `7` Điểm `Light Leak`**.

---

## 3. Lưu ý kiểm tra cuối & Tuân thủ ngành Dược / TPBS
- Video giữ dòng khuyến cáo bắt buộc: *"Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh"*.
- Do AI không nghe trực tiếp bằng tai người, mời bạn mở nghe thử độ cân bằng giữa giọng dược sĩ và 146 điểm SFX; nếu muốn tăng/giảm riêng lớp SFX, trong project CapCut `BOJOMI_AnVuong_TalkingHead_v4_Master` đã tách sẵn 2 track SFX riêng biệt (`03_SFX_Transitions_Risers` và `04_SFX_Pops_Shutters_Ticks`) để kéo thanh âm lượng trong 1 giây.
