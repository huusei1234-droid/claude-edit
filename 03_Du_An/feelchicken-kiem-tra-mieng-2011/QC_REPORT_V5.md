# Báo Cáo Kiểm Định Chất Lượng (QC Report V5) — Đồng Bộ Màu & Key CapCut + Banner Hoạt Hình Thầy Cô 20/11 + Thẻ Địa Chỉ Siêu Kute
**Dự án**: `FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4` (`1080×1920 @ 30fps`, `48.47s`, `1454 frames`)
**Nguồn đồng bộ màu & vị trí**: Trích xuất trực tiếp `100%` thông số chỉnh màu (`effects` + `8-band HSL`) và bố cục/cắt cảnh (`clip.scale`, `clip.transform`, `source_timerange`) từ dự án CapCut `FEEL_CHICKEN_KiemTraMieng_2011_V4_CS1_SourceGoc` bạn vừa tinh chỉnh lúc `15:06`.
**Nhạc nền (BGM)**: `Food Funk02 (1p49s).mp3` (`-14.0 LUFS` Broadcast Master)

---

## 3 Hạng Mục Nâng Cấp Chính Bản V5

### 1. Đồng bộ 100% Màu chỉnh & Khung Key của bạn từ Dự án CapCut sang Video V5
- Đọc trực tiếp `draft_content.json` của `FEEL_CHICKEN_KiemTraMieng_2011_V4_CS1_SourceGoc` và hiệu chuẩn Engine màu (`capcut_color_engine.py`) khớp trực tiếp với ảnh GPU thực tế `draft_cover.jpg` của CapCut:
  - **8-Band HSL đồng bộ da & màu thương hiệu**: `Red (sat +18, light +7)`, `Orange/Skin (sat -9, light +15)` làm trắng hồng da tự nhiên, `Green (hue +14, sat -4)`, `Blue (hue +6, sat +12)` tôn áo sơ mi denim xanh và đèn neon.
  - **Thông số ánh sáng & cân bằng trắng riêng từng clip**: Áp dụng chính xác `brightness`, `contrast`, `saturation`, `highlight`, `shadow`, `black (-0.0645)`, `clear (+0.1785)`, `temperature`, `tone`, `light_sensation` và `smart_color_adjust` riêng cho từng phân đoạn (`C3938`, `C3942`, `C1381`, `C1385`, `HuCauHoi_LacHu_02`, `HuCauHoi_BocTham_01`, `C3956`, `C1395`, `0327_D`, `0339_D`, `IMG_6494`, `IMG_6495`, `C3957`, `0284_D`).
  - **Giữ nguyên 100% khung Key/Transform & thời lượng bạn đã căn lại**:
    - `C1385.MP4`: `scale = 1.0446`, `transform = (0.0, -0.0444)`
    - `C3956.MP4` (phần đầu): `scale = 1.1099`, `transform = (-0.1099, 0.0)`
    - `C3956.MP4` (phần sau): `scale = 1.0747`, `transform = (-0.0769, 0.0)`
    - `C3957.MP4`: `scale = 1.0703`, `transform = (-0.0725, 0.0)`
    - `DJI_20251201144741_0284_D.MP4` (Mặt tiền Cơ sở 1): Lấy đúng đoạn `SRC 2.37s + 3.90s` (`3.90s`) kèm `scale = 1.1308`, `transform = (+0.0812, +0.0810)` và chống rung `vidstab`.

### 2. Thay Image 2 bằng Banner Animation Hoạt Hình Thầy Cô & Học Trò 20/11 (`13.47..15.81s`)
- Gỡ bỏ cảnh cặp đôi ngồi bàn ăn (`0342_D.MP4`) và thay bằng **Banner Hoạt Hình Kawaii 20/11** (`FC_v5_kute_teachers_2011_vid.mp4`): cô giáo mặc áo dài hồng phấn dịu dàng ôm bó hoa, thầy giáo đeo kính tròn cầm hộp quà, các bé học sinh quàng khăn đỏ vỗ tay tặng hoa và chú gà vàng Feel Chicken đeo tai nghe đỏ nhún nhảy dễ thương giữa lớp học pastel bay đầy tim hồng & máy bay giấy.

### 3. Thiết kế lại Thẻ Địa Chỉ Cuối Video Siêu Kute (`44.57..48.47s`)
- Thay khung chữ nhật đỏ cứng cũ bằng **Thẻ Đám Mây / Sticker Kẹo Ngọt Kawaii (`build_ultra_kute_storefront_card`)**: viền lượn sóng đám mây hồng dâu + nền kem sữa đường chỉ khâu nét đứt, ruy-băng nổi `HẸN GẶP BẠN TẠI QUÁN NHA!`, thẻ viên kẹo hồng phấn `ĐỊA CHỈ: 38 Nguyễn Đình Chiểu • Nha Trang`, hai viên kẹo bạc hà & mật ong hiển thị giờ mở cửa `10:00 – 22:00` và Hotline `0979 233 139`, kèm cặp chibi gà con & ly trà đào nhún nhảy hai bên góc thẻ.
