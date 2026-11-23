# Báo Cáo Sản Xuất & Kiểm Định Chất Lượng (QC V2): HTPM(4) — Căng Thẳng Kéo Dài & Khả Năng Sinh Sản

- **Tệp video gốc**: `C:\Users\Hang thu\Downloads\HTPM(4).mp4` (`1080×1920 @ 30fps`, cắt sạch 29 frame đen cuối -> giữ nguyên vẹn **`1.479 frames` = `49.300s`**)
- **Tệp xuất Final chuẩn quy ước**: **`261120 HTPM căng thẳng kéo dài ảnh hưởng sinh sản final.mp4`**
- **Thư mục bàn giao chính thức**: `Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\`
- **Bản sao dự phòng**: `D:\XUẤT CAPCUT\hằng thu pharma\` & `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\`

---

## 1. Nâng Cấp Toàn Diện Bản V2 Theo Góp Ý Editor

1. **Xử lý triệt để âm thanh (`htdemucs` Vocal Isolation + Mono-Center `L == R`)**:
   - Phát hiện file gốc `HTPM(4).mp4` có sẵn nhạc nền/tạp âm trộn ở cả 2 kênh (`peak -3.7 dBFS`) và giọng mic thu lệch kênh Trái (`L = 0.216`, `R = 0.031`).
   - Tách sạch vocal bằng `htdemucs` GPU, lấy kênh mic Trái sạch đưa đều ra 2 kênh (`pan=stereo|c0=c0|c1=c0`), lọc nhiễu nhẹ `afftdn=nf=-25`, phối cùng nhạc nền 2 nửa C-Major êm dịu (`-15.8 dB` dưới giọng nói) và `19` điểm nhấn `Tactile Micro-SFX` tinh tế (`-13.2` đến `-14.6 dB` dưới giọng), chuẩn hóa 2-pass `loudnorm` đạt **`-14.0 LUFS`**.
2. **Hạ cụm tiêu đề Chữ Gradient sát đỉnh tóc (`y = 232..420`)**:
   - Đưa cụm nhãn + tiêu đề **Chữ Gradient 5 điểm dừng tách viền 2 lớp** từ `top: 46px` xuống `top: 232px` để chân chữ lồng nhẹ phía sau phần đỉnh tóc (`RVM Matte y < 452`), xóa bỏ khoảng trống lơ lửng phía trên đầu mà vẫn cách xa trán & gọng kính.
3. **Đẩy cao phụ đề (`y = 1568..1634`) & Nâng cấp Font `Be Vietnam Pro ExtraBold`**:
   - Nâng cụm sân khấu Kobe dưới lên `y = 1036..1522` và đẩy phụ đề cao lên vùng đọc vàng `y = 1568..1634` (thoát hoàn toàn thanh UI dưới cùng của TikTok/Reels).
   - Đổi sang font **`Be Vietnam Pro ExtraBold`** (`stroke_w = 5` tách viền 2 lớp + đệm mờ bán trong suốt `rgba(14,19,38,0.36)` + hiệu ứng mở nét quang học 2 chiều `Bidirectional Blur-Focus`).
4. **Trọn bộ `11` Source Video AI Riêng Biệt (`0%` Lặp Lại Xuyên Suốt `49.30s`)**:
   - Tạo đủ `11` cảnh độc lập từ ảnh tham chiếu ChatGPT (`Dự án HTPM`) -> Google Flow / Muse (`4s`, đồng bộ màu `10_AI_Clip_Harmonizer_Natural.cube`):
     - **Chặng 1 (`8.92–18.22s`)**: `st_01_chronic_stress` → `st_01b_sleepless_night` → `st_01c_office_pressure`
     - **Chặng 2 (`18.42–27.80s`)**: `st_02_hormone_balance` → `st_02b_irregular_cycle` → `st_02c_ovulation_follicle`
     - **Chặng 3 (`33.74–40.60s`)**: `st_03_nourish_relax` → `st_03b_garden_breathing`
     - **Chặng 4 (`40.82–49.20s`)**: `st_04_radiant_vitality` → `st_04b_selfcare_glow` → `st_04c_happy_couple_garden`
