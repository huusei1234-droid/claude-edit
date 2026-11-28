---
name: talking-head-ngoi-ban
description: >-
  Quy chuẩn sản xuất & hậu kỳ Video Chuyên Gia Ngồi Bàn Tư Vấn (9:16 @ 30fps,
  chuẩn Series 14 Reels Chị Hằng HTPM V5 Master): Bắt buộc tạo video mẫu & minh
  họa bằng Gemini Web Pro (10s/15s, tự động xoay cạn 100% các tài khoản Pro
  u/0..u/9 trong Brave trước rồi mới chuyển sang Google Flow), kiểm tra & cắt
  sạch 100% đoạn thoại lặp bằng Whisper, khóa nguyên vị trí khung hình gốc của
  mẫu (0px kéo lên xuống, 0% làm mờ nền), tách RVM đặt 100% lá bài B-Roll + đồ
  họa 3D + icon bay lượn phía sau lưng mẫu (0% che mẫu), hộp Hook vàng chữ đen
  3s đầu, chữ nhấn thoáng trên đỉnh đầu tự động tắt sub dưới tránh trùng, mỗi
  video một biến thể dựng riêng và tắt hoàn toàn nhạc nền (0% BGM, chuẩn -14.0
  LUFS).
---

# Quy Chuẩn Sản Xuất & Edit "Video Dạng Ngồi Bàn Tư Vấn" (`talking-head-ngoi-ban` — Chuẩn V5 Master)

Skill này đóng gói trọn vẹn quy chuẩn tạo source và dựng hậu kỳ HyperFrames cho dòng **Video Chuyên Gia / Dược Sĩ Ngồi Bàn Tư Vấn (`1080×1920 @ 30fps`)** đã được kiểm chứng và chốt duyệt thực tế trên bộ **14 Video Reels Chị Hằng — Hằng Thu Pharma (`V5 Master`)**.

---

## 1. Quy Tắc Bắt Buộc Số 1 Khi Tạo Video Source: `Gemini Pro (Cạn Sạch Mọi Acc) → Google Flow → Muse`

1. **Tạo Video Mẫu Ngồi (`10s` / `15s` dọc `9:16`) & Minh Họa Động**:
   - **BẮT BUỘC ƯU TIÊN SỐ 1 DÙNG GEMINI WEB PRO TRONG BRAVE (`:9333`)**:
     - Gọi qua `C:\AI\full studio\canvas\desktop\gemini-driver.js` (`gemini:generate-video` / `gemini.generateVideo(job)`) hoặc `gemini::gemini-video` trong `ai_ref_video.py`.
     - Chọn đúng thời lượng **`10 giây` (`10s`)** hoặc **`15 giây` (`15s`)** và khung dọc **`9:16`** kèm ảnh tham chiếu gốc của mẫu.
     - Tự động quét và xoay vòng tuần tự qua **TẤT CẢ các tài khoản Google Pro đang đăng nhập trong Brave (`u/0 → u/1 → u/2 → ... → u/9`)**. Hết lượt ở tài khoản này tự động nhảy sang tài khoản Pro kế tiếp.
   - **CHỈ CHUYỂN SANG GOOGLE FLOW KHI ĐÃ CẠN SẠCH TẤT CẢ ACC GEMINI PRO**:
     - Tuyệt đối **không gọi thẳng `flow-driver.js` trước** khi chưa thử hết toàn bộ dàn tài khoản Gemini Pro trong Brave.
     - Chỉ khi tất cả các tài khoản Gemini Pro đều báo hết hạn mức tạo video trong ngày mới tự động chuyển sang dự phòng **Google Flow (`flow-driver.js`) → Muse**.
2. **Tạo Ảnh Lớp Phủ / Thẻ Bài B-Roll Y Khoa**:
   - Dùng **Gemini** hoặc **ChatGPT (`chatgpt-driver.js` trong dự án `HTPM`)** tạo ảnh minh họa chuẩn xác 100% theo từng câu nói (tuyệt đối không dùng ảnh fallback lệch chủ đề và không nhồi nhét quá nhiều ảnh rác).

---

## 2. Kiểm Tra & Cắt Sạch 100% Lỗi Lặp Lời Nói (`0%` Thoại Lặp)

Khi tạo clip `15s`, AI tạo video đôi khi đọc lặp lại cụm từ ở giữa hoặc lặp lại câu cuối để lấp đầy thời lượng. **Bắt buộc thực hiện trước khi dựng**:
1. Chạy `faster-whisper` (`small`, `word_timestamps=True`) trong tiến trình con độc lập để lấy mốc từng từ và quét tự động `1-gram / 2-gram / 3-gram` lặp từ hoặc câu cụt cuối bài (`clean_speech_and_rvm_all14.py`).
2. Đo đường bao năng lượng âm thanh (`20ms RMS`) quanh đoạn lặp để cắt ngay đúng **điểm lặng hơi thở (`RMS < 0.012`)**, nối mượt bằng `xfade=transition=fade:duration=0.08` (hình) + `acrossfade=d=0.08:c1=tri:c2=tri` (tiếng) để không bị khực hình hay bụp tiếng.
3. Chạy lại `faster-whisper` trên file `presenter.mp4` sau khi cắt, xác nhận **`reps = []` (`0%` từ lặp)** và khớp kịch bản phụ đề đúng 100% những chữ mẫu thực sự nói.

---

## 3. Bố Cục Khung Hình Mẫu & Không Gian Đa Lớp Sau Lưng (`RVM Depth`)

1. **KHÓA CỨNG VỊ TRÍ GỐC CỦA MẪU (`0px` Kéo Lên Xuống)**:
   - **Cấm tuyệt đối** dịch mẫu lên/xuống (`0px` `topfill`/`vstack`), cấm zoom giật mẫu, cấm thu nhỏ mẫu vào khung tròn `Circle PiP`, cấm đẩy trượt mẫu sang một bên.
   - Giữ nguyên `scale=1080:1920:flags=lanczos,fps=30,format=yuv420p` tự nhiên, giữ sáng rõ phòng thật (**không làm mờ nền phòng**, **không rắc hạt chấm sáng bokeh**), và **không gò ép theo vùng an toàn TikTok** nếu làm bí khung hình.
2. **100% B-ROLL, LÁ BÀI & ĐỒ HỌA NẰM PHÍA SAU MẪU (`0%` Che Mẫu)**:
   - Tách lớp người nói tiền cảnh bằng RVM (`matte.py` trên proxy `540×960 --ratio 0.5` → `presenter_cutout.webm`) đặt ở **`z-index: 20`**.
   - Toàn bộ thẻ bài B-Roll, màn hình mô phỏng 3D và lớp icon đặt trong `#behind-stage` ở **`z-index: 4..10` (thấp hơn `presenter_cutout.webm`)**, bố trí ở hai hành lang vai trái (`X = 26..410px`) & vai phải (`X = 670..1054px`) để **không có bất kỳ pixel B-Roll nào đè che mặt, tóc hay cơ thể mẫu**.
3. **Lớp Phủ Lá Bài & Icon Chủ Đề Bay Lượn (`bay lượn`)**:
   - Kết hợp **chế độ lá bài B-Roll xếp xòe quạt, lật 3D (`rotateY`), xoay vòng carousel hoặc bay đảo hai bên vai** sát đúng nội dung từng câu thoại.
   - Bổ sung lớp Canvas **icon & vật thể chủ đề bay lượn liên tục (`#th-float-cvs`)** phía sau hai vai suốt thời lượng video (ví dụ: tinh binh 3D bơi lượn, giọt tinh dịch, noãn cầu hồng, chuỗi xoắn kép DNA, trái tim & pha lê, bông tuyết băng giá, bọt bia sủi, khiên & dấu cộng y tế...).

---

## 4. Quy Tắc Thiết Kế Chữ (Hook 3s • Chữ Nhấn Đỉnh Đầu • Tự Tắt Sub Trùng)

1. **Tiêu Đề Hook 3 Giây Đầu**:
   - Hộp chữ nhật vàng rực bo góc lớn (`#FFE800 → #FFD200`, `border-radius: 48px`, `left: 96px, top: 1158px, width: 888px`), chữ **Đen IN HOA đậm (`Montserrat-Black`, `51px`)** kèm vệt ánh sáng lướt nhẹ.
2. **Chữ Lớn Làm Điểm Nhấn Phía Trên Đầu (`#top-kw-master`)**:
   - Chỉ bật ở đúng **1–2 ý chốt quan trọng nhất** trong bài.
   - Đo tự động tọa độ đỉnh tóc `head_top_y` từ mặt nạ RVM và đặt chữ tại **`top = max(14, head_top_y - 186)px`** để **cả 2 dòng chữ nổi thoáng, đọc rõ 100% phía trên đỉnh đầu mẫu** (kèm hiệu ứng dịu nền nhẹ `ANIM_DIM` sau lưng RVM, dải quét sáng `Light-Sweep` và số Neon).
   - **[QUY TẮC BẮT BUỘC CHỐNG TRÙNG & CHỐNG ĐÈ]**: Trong suốt khoảng thời gian chữ nhấn trên đỉnh đầu hiển thị (`[kw_start .. kw_end]`):
     - **TẮT HOÀN TOÀN phụ đề phía dưới (`0%` xuất hiện 2 dòng chữ trùng nội dung trên cùng khung hình)**.
     - **Hạ mờ tạm các thẻ vai phía sau (`#cards-substage opacity -> 0.08`)** để chữ nhấn trên đầu không bao giờ chạm hay đè lên thẻ B-Roll.
3. **Phụ Đề Thoại (`Sub text`)**:
   - Đặt gọn ngang tầm ngực/mép bàn (`top: 1288px`), viền dày sắc nét dễ đọc kết hợp hiệu ứng chữ trồi nhẹ + bóng viền nở **`Stroke-Up`** (`03-thu-vien-hieu-ung.md` mục `A5 + A6`).

---

## 5. Đa Dạng Hóa Giữa Các Video & Tiêu Chuẩn Âm Thanh (`0%` BGM)

1. **Mỗi Video Trong Kênh Edit Khác Nhau Một Chút**:
   - Khi sản xuất hàng loạt nhiều video trên cùng một nhân vật ngồi tư vấn, **cấm dùng rập khuôn 1 bộ icon hay 1 kiểu khung duy nhất**.
   - Bắt buộc xoay vòng đa dạng giữa các bài: **6 kiểu huy hiệu Hook** (vuông viền neon, tròn kính xanh, viên thuốc trắng–xanh Kobe, khiên ngọc lục bảo, hồng pastel, lục giác cam–cyan) × **5 bảng font & màu chữ nhấn/phụ đề** × **mô hình đồ họa 3D riêng sát từng chủ đề** × luân phiên nền vòng xoay đồng tâm `RingsBg` ở đoạn kết.
2. **Âm Thanh Không Nhạc Nền (`0%` BGM)**:
   - **Không chèn nhạc nền (`0%` BGM)** đúng chất chuyên gia tư vấn trực diện của kênh mẫu.
   - Chỉ giữ giọng nói gốc sạch, dày, chuẩn hóa **`-14.0 LUFS`** (`highpass=f=70,loudnorm=I=-14:TP=-1.2:LRA=11`) đi kèm 3–5 tiếng động `Micro-SFX` xúc giác thật êm (`sfx_pop_clean`, `sfx_whoosh_soft`, `sfx_ping_glass` ở mức nhỏ `volume = 0.16–0.18`).

---

## 6. Bộ Code Mẫu Tham Chiếu Đã Kiểm Chứng Thực Tế
- Thư mục bộ code gốc 14 bài V5 Master: `C:\AI\full studio\projects\hanh_sung_suong_reels\`
  - Cắt thoại lặp + RVM không dịch khung: `clean_speech_and_rvm_all14.py`
  - Hệ thống 14 mô hình đồ họa & lá bài sau vai: `behind_styles_01_07.py`, `behind_styles_08_14.py`
  - Bộ tiêm hiệu ứng Talking-Head & Icon bay lượn 14 chủ đề: `th_fx_injector.py`
  - Trình điều phối kiểm lỗi `hyperframes check` & xuất `-14.0 LUFS`: `render_all14_final_v3.py`
