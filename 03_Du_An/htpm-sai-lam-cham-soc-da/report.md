# Báo Cáo Kiểm Định (QC) — HTPM Sai Lầm Khi Chăm Sóc Da (3D Playing-Card Fan & Push-Carousel)

- **File Xuất Cục Bộ Duy Nhất**: `D:\XUẤT CAPCUT\HTPM_SAI_LAM_CHAM_SOC_DA_FINAL.mp4` (Không tạo bản nháp CapCut Desktop theo yêu cầu).
- **Kho Lưu Trữ Đám Mây**: `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_SAI_LAM_CHAM_SOC_DA_FINAL.mp4`
- **Thông Số Kỹ Thuật**: `1080×1920`, `30/1 fps` CFR, `2.422` frames (`80.73s`), `0` lỗi giải mã FFmpeg, chuẩn âm lượng **`-14.0 LUFS`** (`LRA: 1.5 LU`).

## 1. Hệ Thống Thẻ 3D Xòe Bài & Đẩy Qua Lại Theo Thứ Tự (`render_skincare_carddeck.py`)
- **Đường cong chuyển động `septic_smooth` (`C3`) + Homography 3D `PERSPECTIVE` liên tục + Shutter Motion Blur 180° + SciPy Gaussian DOF**: loại bỏ hoàn toàn hiện tượng khựng khung hình.
- **4 Bộ Thẻ 3D Xòe Như Lá Bài & Đẩy Qua Lại Khớp Từng Câu Thoại**:
  1. **Overview 3-Card Fan (`02.95s – 05.82s`)**: 3 thẻ bài `01 Làm Sạch Quá Mức` • `02 Chạy Theo Xu Hướng` • `03 Quên Chăm Bên Trong` xòe quạt đối xứng.
  2. **Deck #1 — Làm Sạch Quá Mức (`08.08s – 30.08s`)**: 3 thẻ video da liễu thực tế xòe bài cùng lúc rồi đẩy tuần tự `01 Rửa Mặt Quá Nhiều Lần` → `02 Tổn Thương Màng Bảo Vệ Da` → `03 Mất Nước • Bóng Nhờn Bù Trừ`.
  3. **Deck #2 — 4 Loại Da (`39.20s – 49.06s`)**: 4 thẻ cận cảnh da liễu (`01 Da Dầu` → `02 Da Khô` → `03 Da Hỗn Hợp` → `04 Da Nhạy Cảm`) xòe bài → đẩy qua theo nhịp đọc → xòe lại cả 4 lá bài khi đối chiếu nhu cầu (`43.95s`) → đẩy ngược về thẻ `04 Da Nhạy Cảm • Dễ Kích Ứng` (`47.45s`).
  4. **Deck #3 — Quên Chăm Bên Trong (`53.48s – 67.86s`)**: 3 thẻ đời thực xòe bài → `01 Trăm Triệu Mỹ Phẩm Đắt Tiền` → đẩy sang `02 Thức Khuya Đến 1–2 Giờ Sáng` (`02:37`) → đẩy sang `03 Ít Nước • Nhiều Đồ Ngọt & Đồ Nhanh` → đẩy ngược lại về `01 Trăm Triệu Mỹ Phẩm` (`63.35s`) khi chốt câu *"dù mỹ phẩm có tốt đến đâu cũng rất khó mang lại hiệu quả"*.
- **Cutaway 9:16 + Live 3D PIP (`71.25s – 76.68s`)**: Chuyển cảnh quang học mượt sang cảnh thói quen lành mạnh buổi sáng kèm khung PIP 3D trực tiếp của Dược sĩ ở góc phải dưới.

## 2. Footage Da Liễu & Đời Thực 100% Đúng Kịch Bản (0% Kute / Lạc Đề)
- 8 video Muse (`muse-video`) + 4 ảnh macro da liễu trong dự án ChatGPT `HTPM` quay phong cách tư liệu thực tế (`Sony FX6` / `85mm clinical macro`), tái hiện chân thực bọt rửa mặt dày, đỏ rát bong tróc hàng rào da, giấy thấm dầu vùng chữ T, đồng hồ `02:37` sáng, trà sữa & đồ ăn nhanh.

## 3. Typography Gradient 5 Điểm Dừng & 42 Điểm SFX Đồng Bộ (`mix_skincare_final.py`)
- Chữ Gradient 5-stop (`gold`, `coral`, `emerald`, `rose_satin`, `sapphire`) tách lớp viền tối dày `(12, 16, 28)` + đổ bóng nổi bật sắc nét trên nền áo vest trắng, kèm 6 thẻ Banner chuyển đoạn và 6 Pill nhấn nhá câu chốt.
- 42 điểm SFX chọn lọc từ `TLH\Edit` (`card_swipe`, `card_slide`, `chan_hook`, `whoosh_tvc`, `ting_clean`, `notif_subtle`, `pop_soft`) phối cùng BGM 2 nửa ducking tự động chuẩn `-14.0 LUFS`.
