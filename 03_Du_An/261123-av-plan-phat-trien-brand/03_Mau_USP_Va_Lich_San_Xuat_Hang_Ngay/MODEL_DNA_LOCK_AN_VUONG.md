# HỒ SƠ KHÓA DANH TÍNH MẪU USP XUYÊN SUỐT — AN VƯỢNG PHARMA

> **Đơn vị áp dụng**: Toàn bộ hệ thống sản xuất hằng ngày **5 Video USP Dọc `9:16` (<= 1 phút, Text cực to, lớp phủ ánh sáng, 5 nhạc nền riêng, 0% sai sản phẩm) + 5 Bài đăng Thiết kế `.JPG` Text To (không `.PSD`) + 1 lần quét chỉ đọc 2 nhóm Zalo** của **An Vượng Pharma** — lưu chính thức tại `Z:\Drive của tôi\dự án ngoài\An Vượng\`.
> **Nơi sinh sống của Nhân vật (Location DNA)**: **TP. NHA TRANG, KHÁNH HÒA** — khí hậu nắng ấm gió biển quanh năm! Mọi bối cảnh sống, chạy bộ, cà phê, căn hộ gia đình và trang phục đều phản ánh chân thực cuộc sống hiện đại tại Nha Trang.
> **Nguyên tắc vàng**: **KHÓA CỨNG 100% KHUÔN MẶT & VÓC DÁNG** xuyên suốt mọi ngày — **MỖI VIDEO & MỖI BÀI THIẾT KẾ ĐỔI TOÀN DIỆN NHƯ NGƯỜI THẬT**: đổi trang phục + kiểu tóc + bông tai + dây chuyền/đồng hồ/kẹp tóc + bối cảnh Nha Trang.

---

## 1. Đường Dẫn 3 Ảnh Neo Danh Tính Chính Thức (Master Anchors)
- **Bảng chuẩn gốc 2 khung (`Master Sheet` — dùng 1 file duy nhất khi upload lên ChatGPT `HTPM`)**: `01_Mau_USP_Xuyen_Suot\AV_MODEL_MASTER_SHEET.jpg`
- **Ảnh neo cận mặt (`Face Anchor`)**: `01_Mau_USP_Xuyen_Suot\AV_MODEL_FACE_ANCHOR.png`
- **Ảnh neo toàn thân (`Body Anchor`)**: `01_Mau_USP_Xuyen_Suot\AV_MODEL_BODY_ANCHOR.png`

---

## 2. Hồ Sơ Cuộc Sống Tại TP. Nha Trang (`[NHA TRANG LOCATION LOCK]`)
Đưa tự nhiên vào prompt bối cảnh ChatGPT `HTPM` & Google Flow tùy từng ca video trong ngày:
1. **Chạy bộ & Thể thao sáng (`AV Protein` / `Bojomi`)**: Đường biển **Trần Phú** & **Phạm Văn Đồng (Nha Trang)** bình minh nắng vàng rực, hàng dừa xanh nghiêng gió biển, bãi cát trắng và mặt biển xanh ngọc vịnh Nha Trang lấp lánh phía sau.
2. **Căn hộ gia đình & Bếp sáng (`Combo Chiều Cao Bé 1 Tuổi+` / `AV Protein` / `Curcumilk`)**: Căn hộ chung cư cao tầng hiện đại tại Nha Trang có ban công kính / cửa sổ lớn **view vịnh biển Nha Trang** tràn nắng sáng, rèm voan trắng bay nhẹ theo gió biển.
3. **Công sở / Cà phê / Dạo phố chiều (`Bojomi` / `Curcumilk`)**: Quán cà phê ngoài trời view biển Nha Trang sáng trong, đại lộ hàng dừa ven biển, không gian làm việc tràn ánh sáng tự nhiên.
4. **Dạ tiệc / Dưỡng da tối (`Collamela` / `Combo CTKM`)**: Không gian lounge / ban công tối nhìn ra đèn thành phố biển Nha Trang lung linh hoặc phòng trang điểm hiện đại ấm áp.
5. **Quy tắc trang phục theo khí hậu Nha Trang**: Luôn chọn đồ thoáng mát, tươi sáng, bay bổng (đồ chạy bộ/Pilates năng động, đầm linen/sơ mi lụa, cardigan mỏng khoác hờ, nón visor nắng biển) — **KHÔNG** dùng áo khoác đại hàn hay đồ len dày mùa đông rét đậm.

---

## 3. Khối Khóa Prompt Chuẩn Cho ChatGPT (`HTPM`) & Google Flow (`Omni 1.2`)

### A. `[CHARACTER LOCK]`
```text
Keep the EXACT SAME young Vietnamese woman (25–27 years old, living a sunny modern lifestyle in Nha Trang coastal city) from the attached reference photo av_model_master.jpg with 100% identical facial features, expressive dark-brown eyes, soft brows, gentle rosy smile, luminous fair skin, and slender graceful proportions.
```

### B. `[PRODUCT ACCURACY LOCK]` (Chống Sai Sản Phẩm 100%)
- **TUYỆT ĐỐI KHÔNG gửi cùng lúc 2 hộp sản phẩm khác nhau (`AV Protein` + `Bojomi`) vào cùng 1 prompt Google Flow** (tránh AI trộn chữ 2 nhãn hộp).
- **Cảnh pha/cầm từng sản phẩm lẻ trên Flow**: Chỉ đính kèm **tối đa 1 hộp thật duy nhất** (`av01_protein_a.png`, `av02_bojomi_b.png`, `av03_collamela_b.png`, hoặc `av04_curcumilk_b.png`) và **bắt buộc soi QC trực quan từng clip thô (`qc_raw_clips.py`)** trước khi render.
- **Cảnh giới thiệu Bộ đôi / Combo 2+ sản phẩm & End-Card**: Sinh cảnh nhân vật không có hộp AI → ghép trực tiếp **100% ảnh hộp thật tách nền `IS-Net`** nổi khối 3D sắc nét trong HyperFrames.

### C. `[VIDEO PRODUCTION & AUDIO STANDARD]` (5 Video / Ngày)
- **Định dạng & Thời lượng**: Dọc `9:16` (`1080×1920 @ 24fps`), gọn **dưới 1 phút (`38s – 55s`)**, giọng **`THANH THANH TVC`** trên RTX 4070 CUDA.
- **5 Bài Nhạc Nền BGM Riêng Biệt Mỗi Ngày**: Lấy 5 bài khác nhau từ `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\`, chuẩn hóa `-18 LUFS` + EQ Voice Pocket + Dynamic Ducking.
- **Hiệu Ứng Lớp Phủ Điện Ảnh (`Screen`)**: Ghép thật `video_overlays_4k/` (`01_Golden_Dust_Bokeh_9x16.mp4`, `03_Warm_Window_Sun_Rays_9x16.mp4`, `05_Soft_Pearl_Sparkles_Bling_9x16.mp4`) + ánh kim Specular Sheen quét ngang thẻ chữ.
- **Text Cực To Siêu Dễ Đọc**: Hook mở đầu `64–74px` viền trắng dày 15px, tiêu đề thẻ `52–56px`, mô tả `28–30px`, strict `box-sizing: border-box` trong Vùng An Toàn `9:16` (`X = 56..870px, Y <= 1534px`, 0% chạm cột nút phải).
- **Pháp Lý TPBS & Zero Lip-Sync**: `ZERO speaking, ZERO lip-syncing, NO text overlays, NO watermarks`; pha riêng 2 nhiệt độ (`AV Protein 20–40°C`, `Bojomi 60°C`); chia lượng theo độ tuổi từ 1 tuổi+; luôn gắn câu miễn trừ TPBS ở End-Card & Caption.
