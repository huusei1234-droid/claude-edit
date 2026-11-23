# Báo Cáo Kiểm Định Chất Lượng (QC Report) — HTPM3 (AE-3D & 5-Stop Gradient)

- **Nguồn A-Roll**: `C:\Users\Hang thu\Downloads\HTPM3.mp4` (`1080×1920`, `30/1 fps`, `1,543` khung hình = `51.43s`)
- **Bản xuất cục bộ duy nhất**: `D:\XUẤT CAPCUT\HTPM3_TALKING_HEAD_FINAL.mp4`
- **Kho lưu trữ Cloud**: `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM3_TALKING_HEAD_FINAL.mp4`
- **Thông số kỹ thuật đã kiểm chứng**:
  - Video: `1080×1920`, `30/1 fps` CFR, `1,543` frames (`0` lỗi giải mã `ffmpeg -v error`)
  - Audio: Integrated Loudness **`-13.9 LUFS`** (`LRA: 1.3 LU`), 2-half BGM từ `TLH\Edit` + 24 điểm nhấn SFX tinh tế (`Chan` mở màn + `Whoosh TVC`, `Pop`, `Ting`, `Notification` kèm EQ Voice Pocket `-4.5 dB @ 2.65 kHz`).

## Kiến trúc Dựng Xen Kẽ & Đồ Hoạ 3D After Effects
1. **Xen kẽ 3 chế độ khung hình (`9` phân cảnh trong `51.43s`)**:
   - *Source trực tiếp*: Phân cảnh 1 (`0.0–3.3s`), Phân cảnh 3 (`9.2–13.5s`), Phân cảnh 6 (`24.3–31.1s`) giữ trọn tương tác tay & hộp sản phẩm của dược sĩ kết hợp vòng xoay ánh sáng & thẻ 3D lơ lửng sau lưng.
   - *Lớp phủ 3D xếp lớp nghiêng phối cảnh (`PIL.Image.Transform.PERSPECTIVE`)*: Phân cảnh 2 (`3.3–9.2s`), Phân cảnh 5 (`17.7–24.3s` ghép chồng 2 thẻ video lệch trục `±7.5°`), Phân cảnh 7 (`31.1–39.3s` tinh chất Niacinamide/Glycerin + Cúc La Mã & Cam Thảo + 4 viên nang 3D), Phân cảnh 9 (`44.1–51.4s` kết bài).
   - *Cắt cảnh toàn màn hình 9:16 (`lồng source trực tiếp` kèm PIP 3D trực tiếp của người nói)*: Phân cảnh 4 (`13.5–17.8s` mô phỏng 3D hàng rào niêm mạc) & Phân cảnh 8 (`39.2–44.2s` Hero Showcase 9:16 đúng bộ **Viên Đặt Phụ Khoa Hằng Thu Hộp 10 viên + lọ trắng** tạo từ Muse).
2. **Chuyển cảnh quang học êm dịu**: Hoà trộn mờ tiêu cự + ánh vàng nhẹ (`0.52s` đường cong bậc 5 `quintic_smooth`), không chớp trắng, không cắt gắt.
3. **Typography 5-Stop Gradient + Tách Viền 2 Lớp + Quét Sáng Ánh Kim `115°`**: Áp dụng đồng bộ `gold`, `rose_satin`, `emerald`, `sapphire`, `coral` từ `gradient-text-presets.css`; toàn bộ thẻ 3D, tiêu đề và phụ đề cụm câu đều có chuyển động **In** (`ease_out_back` + nghiêng 3D + mở nét) và **Out** (`quintic_smooth` + mờ quang học).
