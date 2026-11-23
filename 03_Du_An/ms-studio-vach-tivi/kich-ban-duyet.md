# Kịch bản & Hồ sơ Kỹ thuật để duyệt: Timelapse Thi Công Vách Tivi Phòng Khách – MS Studio

> Lưu tại `output/ms-studio-vach-tivi/kich-ban-duyet.md` (theo chuẩn Cổng 1 `HUONG-DAN-AI.md`).
> **Chưa tốn bất kỳ credit Flow/Muse nào ở bước này.** Ngay khi bạn duyệt, hệ thống sẽ sinh trọn bộ **6 Ảnh Mốc Trung Gian (`F1`–`F6`)** khóa cứng kiến trúc phòng + nhân sự `MS Studio`, sau đó tạo **7 Clip Nối (`Start Frame → End Frame`)** và dựng hậu kỳ Timelapse liền mạch từ đầu tới cuối.

---

## 1. Phân tích Đối chiếu Kiến trúc Thực tế (`Ảnh Cũ F0` → `Ảnh Mới F7`)

Để **tuyệt đối không có bất kỳ cảnh "thi công láo" hay biến hình ảo giác nào**, mọi chi tiết thay đổi giữa 2 bức ảnh gốc đã được bóc tách đúng trình tự thợ nội thất ngoài công trình:

1. **Xử lý nền tường cũ ố mốc (`F0` → `F2`)**: Chân tường sơn kem hai bên ở ảnh cũ đang bị bong tróc ẩm mốc → ngoài thực tế **không được dán thẳng tấm than tre lên tường ẩm tróc**, bắt buộc phải **bắn cốt laser xanh lấy tim đối xứng + đóng hệ khung xương phẳng & tấm cốt nền chống ẩm + đi sẵn dây điện âm** trước khi ốp.
2. **Hạng mục trần & điện âm (`F1` → `F5`)**: Trần ảnh mới xuất hiện thêm **2 miệng gió điều hòa âm trần dạng khe dài**, **đèn chùm pha lê mạ vàng tròn ở tâm trần**, **2 dải LED vàng hắt khe dọc hai biên vách đá** và **LED hắt gầm kệ Tivi** → phải có bước khoét khe gió trần, thả dây chờ và gắn thanh nhôm định hình LED trước khi ốp tấm.
3. **Kết cấu 3 lớp vật liệu bức vách (`F2` → `F4`)**:
   * **Tâm giữa**: Tấm ốp **than tre vân đá cẩm thạch xanh–vàng đối xứng vân (*Bookmatched*)** khổ lớn → phải trải sàn đo cắt máy, khoét lỗ luồn dây Tivi, **bơm keo chuyên dụng hình ziczac mặt sau bằng súng bắn keo**, đứng trên **giàn giáo khung nhôm trong nhà** ốp theo tia laser xanh và bắn ke âm.
   * **Hai bên ngoài cùng**: **Lam sóng gỗ óc chó kịch trần** → phải đo tọa độ, dùng máy cắt rung **khoét lỗ vuông chuẩn xác** cho công tắc đôi bên trái và bảng điều khiển điều hòa + công tắc bên phải, ốp xong lắp mặt ổ điện nổi khít lên trên.
   * **Hai khoang chuyển tiếp**: **Tấm than tre tráng gương đen bóng** kết hợp **3 thanh đố gỗ óc chó đứng mỗi bên** căn thẳng theo tia laser.
4. **Nội thất rời, Rèm & Chi tiết góc sàn Ảnh hoàn thiện (`F5` → `F7`)**:
   * Đưa **kệ Tivi gỗ óc chó bo cong mặt đá đen chân viền vàng** vào thế chỗ kệ gỗ cánh gián cũ; treo lại **Tivi + Soundbar**; thay đồng hồ gỗ bằng **đồng hồ kim loại mạ vàng hình vòng tròn nhành lá**; thay rèm hoa văn cũ bằng **rèm vải xanh xám hiện đại một màu**.
   * **Chi tiết khớp nối thực tế 100% ở góc trái dưới Ảnh `F7`**: Trong ảnh hoàn thiện bạn gửi, góc dưới bên trái sàn vẫn còn **tấm bìa carton lót sàn, vài mẩu lam gỗ cắt thừa, cuộn băng dính giấy và tuýp keo trắng xanh** → các ảnh `F1`–`F6` sẽ duy trì đúng khu vực lót bìa carton này ở góc trái để khi về đích ở `F7` **khớp từng milimet mà không có vật thể nào tự nhiên mọc ra hay biến mất vô lý**!

---

## 2. Cơ chế Chống Lặp Hình & Chống Giật Điểm Nối (`Zero-Loop Start-to-End Chain`)

* **Khóa cứng 2 đầu mỗi clip (`Start Frame` + `End Frame`)**: Không tạo video tự do từ 1 ảnh. Ta tạo trước **6 bức ảnh chụp trung gian (`F1` → `F6`)** giữ nguyên 100% tiêu cự ống kính, cửa kính đen bên trái, sàn gỗ và trần nhà như `F0` và `F7`. Mỗi clip `c0k` bị ép đi từ `F_{k-1}` đến đúng `F_k` nên tiến trình vật lý chỉ đi tới trước một chiều, **không bao giờ bị lặp động tác**.
* **Kỹ thuật Timelapse Chuẩn (Sinh tốc độ thực → Tua nhanh hậu kỳ + Motion Blur)**:
  * Ở bước AI sinh clip (`8 giây/clip`), mô tả hành động thi công diễn ra tự nhiên, dứt khoát (không ép AI tự làm hiệu ứng nhoè tua nhanh giả tạo dễ gây biến dạng tay chân).
  * Sang bước dựng hậu kỳ (`FFmpeg / vf / CapCut`), cắt chính xác frame trùng ở điểm giao tiếp giữa `End Frame clip trước` và `Start Frame clip sau`, sau đó đẩy tốc độ **Timelapse `2.2x – 2.5x` kèm Frame-Blending Motion Blur nhẹ** → ra đúng chất camera GoPro gắn tripod quay Timelapse công trình thật suốt 1 ngày rút gọn còn **~28 giây** cực kỳ mượt!
* **Né bẫy kiểm duyệt Google Flow**: Áp dụng quy tắc mục 6b (`HUONG-DAN-AI.md`): nhân sự **2 nam + 1 nữ mặc áo đồng phục `MS STUDIO`** được vẽ khóa sẵn trực tiếp trong 6 ảnh mốc `F1`–`F6`; còn câu lệnh chữ gửi vào Flow chỉ gọi `"the three MS Studio interior technicians"` (tuyệt đối không chứa các từ nhạy cảm về tuổi/giới tính khiến Flow chặn nhầm).

---

## 3. Sơ đồ 8 Khung Hình Mốc (`F0` → `F7`) & 7 Chặng Thi Công

| Cảnh | Mốc cuối video | Cặp Frame Khóa (`Start → End`) | Công đoạn Thi công Thực tế (2 Nam + 1 Nữ áo `MS Studio`) | Chữ chú thích nhỏ góc dưới (tuỳ chọn) | Nguồn Asset |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **c01** | `0.0s – 4.2s` | **`F0` (Ảnh cũ gốc) → `F1`** | Giữ tĩnh `1.0s` hiện trạng cũ → Đội 3 bạn `MS Studio` vào khảo sát, nhấc Tivi & đồng hồ cũ xuống, tháo rèm cũ, khiêng kệ gỗ cũ đi, trải bìa carton lót sàn, dựng **giàn giáo nhôm trong nhà**, đặt máy cắt bàn, máy laser & tập kết tấm ốp. | `01. KHẢO SÁT • THÁO DỠ & BẢO VỆ SÀN` | `flow` (`Omni 1.2`, 8s → tua `2.5x`) |
| **c02** | `4.2s – 7.8s` | **`F1` → `F2`** | Bật **máy bắn cốt laser tia xanh** lấy trục tim đối xứng; 1 nam trên giàn giáo khoét trần lắp **2 miệng gió điều hòa khe dài** & dây đèn chùm; 1 nam khoan đóng **hệ khung xương phẳng + tấm cốt chống ẩm** xử lý tường ố & đi gen dây điện âm chờ LED; nữ đo kiểm cốt ổ điện. | `02. BẮN CỐT LASER • ĐI ĐIỆN & KHUNG XƯƠNG` | `flow` (`Omni 1.2`, 8s → tua `2.2x`) |
| **c03** | `7.8s – 11.4s` | **`F2` → `F3`** | Đo thước & dùng máy cắt cắt tấm **than tre vân đá xanh–vàng đối xứng** (khoét lỗ dây Tivi giữa), dùng súng bơm **keo chuyên dụng ziczac** mặt sau, gắn 2 thanh nhôm profile LED dọc rồi 2 nam trên giàn giáo nâng ốp khít mảng đá trung tâm theo tia laser & bắn ke âm. | `03. ĐO CẮT • BƠM KEO & ỐP THAN TRE VÂN ĐÁ` | `flow` (`Omni 1.2`, 8s → tua `2.2x`) |
| **c04** | `11.4s – 15.0s` | **`F3` → `F4`** | Đo khoét lỗ công tắc điện 2 bên bằng máy cắt rung, cắt chiều cao **lam sóng gỗ óc chó** trên cưa bàn, bôi keo ốp kín 2 biên (lắp lại mặt công tắc trắng nổi khít) + ốp **tấm than tre tráng gương đen** & **3 thanh đố gỗ đứng** mỗi bên chuẩn laser. | `04. ỐP LAM SÓNG ÓC CHÓ & TRÁNG GƯƠNG ĐEN` | `flow` (`Omni 1.2`, 8s → tua `2.2x`) |
| **c05** | `15.0s – 18.4s` | **`F4` → `F5`** | Dán dây LED + bấm nắp mica tán sáng vào 2 khe dọc vách đá, đứng thang lắp **đèn chùm pha lê mạ vàng** giữa trần, dời giàn giáo ra ngoài và cả 3 cùng khiêng **kệ Tivi gỗ óc chó bo cong mặt đá đen chân viền vàng** vào đấu nguồn LED gầm. | `05. LẮP ĐÈN CHÙM • ĐI LED & ĐẶT KỆ TIVI` | `flow` (`Omni 1.2`, 8s → tua `2.4x`) |
| **c06** | `18.4s – 21.8s` | **`F5` → `F6`** | Khoan bắt khung sắt & nhấc **Tivi** treo lại chính tâm vách đá + đặt loa Soundbar; treo **đồng hồ mạ vàng nhành lá** phía trên Tivi; bạn nữ đứng thang chữ A bên phải treo **rèm vải xanh xám một màu** mới. | `06. TREO TIVI • ĐỒNG HỒ VÀNG & RÈM MỚI` | `flow` (`Omni 1.2`, 8s → tua `2.4x`) |
| **c07** | `21.8s – 28.0s` | **`F6` → `F7` (Ảnh mới gốc)** | Khăn microfiber lau bóng gương đen & mặt đá, đặt bình hoa trắng kem + hươu vàng + sách + vòng decor vàng lên kệ, mang thùng đồ nghề ra cửa trái, bấm công tắc **bật sáng rực toàn bộ Đèn Chùm + LED khe vách + LED gầm kệ** và bước ra ngoài để lộ thành quả `3.0s` cuối. | `07. LÊN ĐÈN NGHIỆM THU HOÀN THIỆN • MS STUDIO` | `flow` (`Omni 1.2`, 8s → tua `2.5x`) |

---

## 4. Dự toán Tài nguyên Sẽ Tạo

* **Số ảnh mốc trung gian tạo mới**: **6 ảnh (`F1` → `F6`)** độ phân giải cao ngang `16:9 / 3:2` đồng bộ tuyệt đối góc phòng của `F0` và `F7` (bạn sẽ được xem kiểm tra 6 tấm ảnh mốc này ngay khi tạo xong để chắc chắn 100% không sai chi tiết nào trước khi bấm chạy video!).
* **Số clip AI nối `Start → End Frame`**: **7 clip** (`flow::flow-omni-1.2-flash`, chế độ `Khung hình Đầu/Cuối`, `720p`, `8s/clip`, tạo tuần tự từng clip qua Canvas).
* **Hậu kỳ**: Ghép cắt khít frame nối + tăng tốc Timelapse `2.2x–2.5x` mượt + chỉnh màu nhẹ đồng nhất + xuất file MP4 Final (`Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\`) kèm bản nháp CapCut nếu cần.

---

## 5. Câu hỏi chốt nhanh trước khi bắt đầu tạo Asset

1. **Áo đồng phục `MS Studio`**: Bạn muốn 3 kỹ thuật viên (2 nam, 1 nữ) mặc **áo Polo màu Đen / Nâu trầm in chữ & logo `MS STUDIO` màu Vàng Gold trước ngực + sau lưng** (theo đúng bảng màu `#2C1E16` & `#D99B38` trong Brand Kit `02_MS_Noi_That`), hay bạn có ảnh mẫu áo/logo riêng muốn tải lên?
2. **Âm thanh & Chữ trên màn hình**:
   * Chỉ ghép **Nhạc nền Timelapse hiện đại** (không lời đọc) + dòng chữ nhỏ ghi tên 7 công đoạn góc dưới, **hay** bạn muốn để khung hình sạch 100% không chữ / có thêm giọng đọc thuyết minh?
3. **Chạy tạo Video tự động trên máy**: Bạn muốn mình tạo trước **6 tấm ảnh mốc `F1`–`F6`** ngay bây giờ để bạn xem duyệt mắt trước, rồi mở `full studido.exe` (Infinity Studio Canvas + Google Flow) chạy tiếp 7 clip video luôn chứ?
