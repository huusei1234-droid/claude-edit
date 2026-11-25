# Báo Cáo Kiểm Định Chất Lượng (QC Report V4) — Feel Chicken 20/11 (100% Cơ Sở 1)
**Dự án**: `FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4` (`1080×1920 @ 30fps`, `46.97s`, `1409 frames`)
**Cơ sở áp dụng**: **100% Cơ sở 1 — 38 Nguyễn Đình Chiểu, TP. Nha Trang** (đã loại bỏ hoàn toàn mọi tư liệu và thông tin Cơ sở 2).
**Nhạc nền (BGM)**: `Food Funk02 (1p49s).mp3` (`08_Hip-Hop - Rap - Beat Ngầu Hiện Đại`)
**Chuẩn âm lượng Broadcast**: `-14.0 LUFS` | True Peak `<= -1.0 dBTP` | `48kHz Stereo AAC 256kbps`

---

## 9 Hạng Mục Nâng Cấp V4 Đã Hoàn Thiện & Kiểm Định

1. **Đưa trọn vẹn 2 Source Hũ Bốc Thăm Câu Hỏi (`HuCauHoi_LacHu_02.mp4` & `HuCauHoi_BocTham_01.mp4`) vào Cảnh 4 (`21.97..27.93s`)**:
   - `21.97..24.12s`: Nhân viên Feel Chicken lắc và giới thiệu hũ câu hỏi trước biển hiệu đèn neon tại Cơ sở 1.
   - `24.12..25.30s`: Cận tay đảo và bốc lá phiếu câu hỏi từ hũ `FEEL CHICKEN` căn chính giữa khung hình.
   - `25.30..27.93s`: Ngay khi rút lá phiếu lên, 6 thẻ câu hỏi học đường & đố mẹo bung ra liên tiếp (`0.38s/thẻ`) phủ kín màn hình.
2. **Image 3 (`11.52..13.47s`) — Học sinh Việt Nam xúc động bồi hồi**:
   - Thay hoàn toàn phòng học trống bằng cảnh 3 bạn học sinh cấp 3 Việt Nam mặc áo dài trắng & sơ mi trắng đồng phục ôm bó hoa 20/11 và sổ lưu bút trong lớp học ngập nắng vàng ấm áp, ánh mắt rưng rưng bồi hồi xúc động.
3. **Image 4 & Toàn bộ B-Roll — 100% Source Cơ Sở 1 (`38 Nguyễn Đình Chiểu`), cận cảnh món ngon & bỏ hẳn Chi nhánh 2**:
   - Xoá toàn bộ footage và địa chỉ Chi nhánh 2.
   - Chèn dày 6 cú máy quay cận cảnh món ngon đặc trưng của Cơ sở 1 từ `FILE GỐC/may anh` & `FILE GỐC/dji`: mâm 8 miếng gà đẫm sốt phô mai/cay ngọt trên đĩa tròn kem, tokbokki sốt đỏ trứng luộc, gắp gà sốt Hàn Quốc nóng hổi, salad & khoai tây chiên.
4. **Image 5 (`27.93..29.49s` & `32.85..36.83s`) — Animation Text & Lớp phủ sau đầu Anh Khang (RVM Matting)**:
   - Tách nền RVM (`rvm_mobilenetv3_fp32.onnx`) chính xác từng sợi tóc của Anh Khang để chèn lớp phủ ánh sáng ấm, 2 vòng xoay sao Kawaii đối chiều, cặp huy hiệu nổi hai bên vai và chữ 3D chuyển động cỡ lớn (**`AI ĐẾN QUÁN / CŨNG CÓ QUÀ!`** → **`ÁP DỤNG ĐẾN HẾT / NGÀY 20/11!`**) nằm gọn phía sau đầu Anh Khang.
5. **Image 6 (`36.83..39.55s`) — Không zoom camera (`zoom = 1.00`) + Cảnh đông đúc nhiều khách ăn tại Cơ sở 1**:
   - Khóa cứng khung máy tĩnh `0%` zoom, tái hiện không gian Cơ sở 1 (`38 Nguyễn Đình Chiểu`) nhộn nhịp kín 3–4 bàn học sinh & nhóm bạn trẻ ăn uống vui vẻ.
6. **Image 7 (`39.55..42.77s`) — Text nhảy lên sôi động trên cảnh xé & cắn gà giòn tan**:
   - Căn mẫu vào chính giữa khung hình kết hợp loạt chữ 3D nảy đàn hồi liên tục (**`XÉ ĐÙI GÀ NÓNG HỔI!!`**, **`THƠM NỨC MŨI!!`**, **`GIÒN RỤM RỤM!!`**, **`ĐẪM SỐT HÀN!!`**, **`ĂN LÀ MÊ!!`**) kèm pháo giấy và SFX sôi động.
7. **Image 8 (`44.57..46.97s`) — Mặt tiền Cơ sở 1 (`38 Nguyễn Đình Chiểu`) chống rung mượt nhất & Địa chỉ CS1 duy nhất**:
   - Tuyển chọn đoạn mặt tiền Cơ sở 1 quay bằng DJI 3K `60fps` (`DJI_20251201144741_0284_D.MP4`), xử lý chống rung 2-pass `vidstabtransform` êm mượt và hiển thị duy nhất địa chỉ **`38 NGUYỄN ĐÌNH CHIỂU – TP. NHA TRANG`**.
8. **Căn mẫu chính giữa khung hình xuyên suốt toàn video**:
   - Đo chính xác toạ độ tâm khuôn mặt & cơ thể bằng RVM trên mọi cảnh quay người thật (`C3938`, `C3942`, `C3956`, `C3957`, `IMG_6494`, `IMG_6495`) để đưa chủ thể về đúng trục giữa `x = 540`.
9. **Cập nhật Dự án CapCut 1-Track Source Gốc V4 (100% Cơ sở 1)**:
   - Cập nhật `FEEL_CHICKEN_KiemTraMieng_2011_Kute` chứa 16 phân đoạn source gốc thuần Cơ sở 1 (kèm 2 source hũ bốc thăm câu hỏi) để chỉnh màu đồng bộ nhanh chóng.
