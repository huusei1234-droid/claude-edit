# Báo Cáo Sản Xuất & Kiểm Định QC (V3 Muse Master) — HTPM LT PLUS Hằng Thu

- **Dự án (`slug`)**: `htpm-lt-plus-talking-head`
- **Nguồn A-roll gốc**: `C:\Users\Hang thu\Downloads\HTPM LT PLUS .mp4` (`1080×1920`, `30.00 fps`, `59.17s`, `1775` frames)
- **Dự án tạo ảnh ChatGPT**: Tự động đi vào dự án **`HTPM`** trên ChatGPT (`chatgpt-page-driver.js`).
- **Động cơ tạo video thực tế**: **`Muse` (`muse::muse-video`)** nhận trực tiếp ảnh tham chiếu sản phẩm thật **LT PLUS Hằng Thu** và ảnh cô mẫu da láng mịn từ ChatGPT `HTPM`.

---

## 1. Chi Tiết Nâng Cấp Toàn Diện Bản V3 Muse Master

1. **100% Lớp Phủ Là Video Chuyển Động Thực Tế (0% Ảnh Tĩnh, 0% Icon Hoạt Hình)**:
   - Xuyên suốt `0.00s – 59.17s`, toàn bộ 11 phân cảnh lớp phủ đều là **video chuyển động thực tế (`100% Real AI Video`)** nối tiếp mượt bằng chuyển cảnh chồng mờ `0.45s` (không dùng thẻ ảnh tĩnh và không hở tường thô):
     - **5 Video nhân vật từ ảnh ChatGPT (`HTPM`) + `Muse` (`muse::muse-video`)**: Giữ nguyên cô mẫu đang ngồi nói trong video với **làn da láng mịn rạng rỡ (`porcelain radiant skin`)** qua 5 bối cảnh: phòng chờ cầm sổ khám (`0.00–4.02s`), văn phòng thiếu thoải mái (`3.95–7.20s`), buổi tối lo lắng xem điện thoại (`7.20–10.78s`), bác sĩ nữ tư vấn giải tỏa lo lắng (`10.72–13.02s` & `17.05–23.22s`), và thăm khám chuyên khoa (`23.16–30.86s`).
     - **2 Video Y Khoa & Phòng Xét Nghiệm (`v2_med_cells.mp4` + `v2_lab_micro.mp4`)**: Minh họa tế bào tuyến hiện diện mặt ngoài & soi tiêu bản kính hiển vi quang học.
     - **4 Video Sản Phẩm Thật Qua `Muse` (`muse::muse-video`)**: Đưa trực tiếp ảnh chụp sản phẩm thật **LT PLUS Hằng Thu** làm tham chiếu vào `Muse` tạo 4 đại cảnh video lung linh:
       1. `30.80 – 41.58s`: Hộp hồng & lọ 15 viên LT PLUS trên nền **thạch men sứ trắng gợn sóng** kèm **6 bong bóng ngọc trai thảo dược nổi lên lung linh** (*Hoàng Bá*, *Ích Mẫu*, *Kim Ngân Hoa*, *Trà Xanh*, *Trầu Không*, *Acid Lactic*).
       2. `41.52 – 45.92s`: Cận cảnh **hộp nam châm LT PLUS mở nắp** dưới nắng ấm studio.
       3. `45.86 – 50.18s`: Bộ sản phẩm LT PLUS trên **bục pha lê & dải lụa hồng phấn bay mềm** kèm tia quét sáng vàng kim.
       4. `50.12 – 59.17s`: Bộ 3 sản phẩm LT PLUS tỏa sáng sang trọng đến hết kết thúc.
2. **Làm Mịn Da Tự Nhiên (`Beauty Porcelain Skin`) Cho Cả Mẫu Thật Đang Nói & Mẫu Trên Video Lớp Phủ**:
   - Tích hợp bộ lọc làm mịn da giữ nét chi tiết mắt – môi – lông mày (`smooth_speaker_skin_rgb`) trực tiếp trên chủ thể A-roll đang nói, đồng bộ hoàn hảo với làn da láng mịn của nhân vật trên 5 cảnh ChatGPT + Muse.
3. **Phụ Đề Dễ Đọc (`1.34s – 3.24s/cụm`) & 100% Chữ Đều Có Animation Đầu (`IN`) + Kết Thúc (`OUT`)**:
   - Gộp phụ đề thành **25 cụm 2 dòng cân đối theo đúng dấu câu** (trung bình `2.22s/cụm`), hiện trọn vẹn cụm câu ngay từ đầu để người xem đọc thoải mái, đồng thời tô sáng từ đang đọc theo giọng nói.
   - Áp dụng hàm **`text_in_out_anim` (`Quintic C2 Smoothstep`: trượt dọc nhẹ + thu phóng tinh tế + hòa tan quang học Gaussian)** cho **100% phần tử chữ** trong video: chữ Hook mở đầu, nhãn kính mờ đầu khung, 6 bong bóng thảo dược, 25 cụm phụ đề, bảng tên thương hiệu `LT PLUS` và thanh CTA.
4. **Chuẩn 1:1 Font & Màu Đỏ Thương Hiệu `LT PLUS` Trên Bao Bì Thật**:
   - Font **`Times New Roman Bold` (`timesbd.ttf`)** + màu **Đỏ Crimson `RGB(242, 6, 16)`** đổ khối 3D đỏ ruby trên nền hồng phấn `#F9CADF` khớp vỏ hộp thật.
5. **Nhạc Nền & Bộ SFX Thương Mại Tuyển Chọn Từ `TLH\Edit` (`-14.0 LUFS`)**:
   - **BGM 2 nửa** từ `TLH\Edit\01_Nhạc Nền (BGM)`: `Soft Piano Inspiration01` (`0–30.8s`) crossfade mượt sang `Corporate Medicine` (`30.8–59.17s`), kèm EQ cắt dải `2.15kHz` và Lookahead Sidechain Ducking.
   - **100% SFX tuyển chọn từ `TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)`**: Dùng bộ chuyển cảnh thương mại ấm áp (`Mở cảnh - Âm thanh tỏa sáng sang trọng (Magic Reveal)`, `Whoosh - Hiện chữ mượt tiêu chuẩn TVC`, `Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP)`, `Whoosh - Deep Swish Transiiton 2`, `Whoosh - Gió lướt chữ nhẹ (Swoosh 02)`), tiếng bọt nước tự nhiên (`Pop & Bong Bóng - Pukutsu (water bubbles air)`) cho 6 bong bóng thảo dược trên nền thạch men trắng, và chuông lấp lánh nhẹ (`Lấp Lánh & Phép Thuật - Shine_01`, `Magic Fairy Dust Sound Effect`, `Thông báo - Chuông hiện chữ tinh tế`) cho điểm nhấn thương hiệu.

---

## 2. Danh Sách Khẳng Định Y Khoa / Sản Phẩm Trong Thoại (`knowledge/10` Compliance)

| Mốc thời gian | Nội dung thoại gốc đã rà soát chính tả | Phân loại & Lưu ý kiểm duyệt |
| :--- | :--- | :--- |
| `00.00 – 10.32s` | *"Nghe kết luận lộ tuyến, chị có đang lo lắng không biết bắt đầu từ đâu? Khí hư khiến sinh hoạt thiếu thoải mái, có chị còn thấy máu sau khi quan hệ và lo tình trạng đang nghiêm trọng hơn."* | Mô tả triệu chứng thường gặp; tiêu đề lớn trên màn hình được trung hòa thành *"Nghe kết luận lộ tuyến... LO LẮNG bắt đầu từ đâu?"*. |
| `10.82 – 23.22s` | *"Điều cần làm trước tiên là hiểu đúng, lộ tuyến là tình trạng tế bào tuyến trong ống tử cung hiện diện ở mặt ngoài. Lộ tuyến không đồng nghĩa với nhiễm trùng và bản thân nó không phải là ung thư. Không phải trường hợp nào cũng cần điều trị."* | Thông tin giáo dục sức khỏe chuẩn mực. |
| `23.22 – 30.84s` | *"Khi có triệu chứng gây phiền toái, bác sĩ sẽ đánh giá nguyên nhân, loại trừ nhiễm trùng và những bất thường khác để lựa chọn hướng xử lý phù hợp."* | Khuyến nghị thăm khám chuyên khoa. |
| `30.84 – 41.62s` | *"Với LT PLUS Hằng Thu, công thức có Hoàng Bá, Ích Mẫu, Kim Ngân Hoa, Trà Xanh, Trầu Không và Acid Lactic. Đây là thông tin thành phần để khách hàng đang tìm hiểu."* | Liệt kê 6 thành phần công bố của sản phẩm. |
| `41.62 – 50.18s` | *"Nếu muốn dùng thêm sản phẩm đặt để mang tính hiệu quả và hỗ trợ điều trị, thì nhất định phải sử dụng viên đặt LT PLUS của nhà Hằng Thu, chị em nha!"* | Lưu ý kiểm duyệt Ads trả phí đối với cụm từ thoại *"hỗ trợ điều trị"*; thanh khuyến cáo cố định cuối khung hình hiển thị xuyên suốt 100% thời lượng. |
| `50.18 – 58.78s` | *"Chăm sóc sức khỏe phụ khoa, cần đúng tình trạng và đúng hướng dẫn. Nhắn LT PLUS để nhận thông tin sản phẩm, đọc kỹ trước khi lựa chọn."* | Khuyến nghị sử dụng đúng hướng dẫn & CTA an toàn. |
