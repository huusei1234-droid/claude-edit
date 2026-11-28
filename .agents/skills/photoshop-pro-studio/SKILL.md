---
name: photoshop-pro-studio
description: >-
  Quy trình V6 Siêu Cấp cho retouch ảnh thương mại trong Adobe Photoshop 2026,
  khóa vùng mắt, kiểm tra chi tiết da và ICC sRGB, tách nền BiRefNet,
  chuẩn hóa lô PNG sản phẩm và dựng PSD poster 4 nhóm qua ExtendScript.
---

# Photoshop Pro Studio V6 Siêu Cấp

## Retouch tự nhiên và bảo vệ ngũ quan

- Giữ nguyên con ngươi, tròng mắt, nếp mí trên, bọng mắt cười và chân mày. Tạo `eye_socket_guard` bằng cách mở rộng vùng mắt khoảng 5.5–7.5% chiều ngang mặt. Mở rộng riêng vùng chân mày khoảng 5.5% theo chiều ngang mặt để giữ đuôi mày. Khóa lỗ mũi, viền môi và rãnh cười khỏi các bước làm mịn, chấm xóa và cộng sáng. Giới hạn `shirt_mask` dưới cằm `y > face_bottom`.
- Chấm xóa cục bộ ở độ phân giải gốc bằng Big-LaMa và bù hạt cảm biến với `grain_strength = 0.55–0.65`. Dùng `red_score > 2.65` cho mụn đỏ và `dark_score > 3.8` cho điểm thâm đậm làm ngưỡng rà soát. Dùng kernel `cv2.MORPH_RECT` khi gom cụm có kích thước lớn hơn 45 px.
- Làm mịn nhẹ với mức hòa trộn Low-Frequency Bilateral 22–28%. Mục tiêu giữ 96% fine texture và 68% mid texture trong bước retouch. Chỉnh vùng midtone khoảng +0.15 đến +0.20 EV, bảo vệ vùng tối và giữ sắc trắng ngà khi khử vàng răng.
- Đọc HEIC bằng `pillow_heif`, áp dụng `ImageOps.exif_transpose` rồi chuyển từ ICC nguồn sang sRGB bằng `ImageCms.profileToProfile`. Xác nhận màu nguồn khi ảnh thiếu ICC. Nhúng sRGB khi xuất JPEG với `quality=98, subsampling=0`.
- Dùng [retouch_portrait_natural.py](./scripts/retouch_portrait_natural.py) cho retouch GPU và PSD 3 lớp `Anh Goc`, `Xoa Mun & Vat Thua`, `Chinh Tuoi & Min Nhe`. Soi 2–3 cặp ảnh mẫu ở 200% trước khi xử lý cả lô.

## Chuẩn hóa lô PNG sản phẩm

Khi ảnh còn nền, dùng [cutout_align_batch.py](./scripts/cutout_align_batch.py) để tách nền với BiRefNet FP16, xử lý halo và căn baseline. Chuẩn bị tên `SP_*_CUTOUT.png` cho bước dàn trang sản phẩm.

Dùng Python 3.11 có Pillow và NumPy để chạy [ps2026_commercial_batch_studio.py](./scripts/ps2026_commercial_batch_studio.py) từ thư mục gốc workspace.

```powershell
$python311 = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$commercialStudio = '.agents/skills/photoshop-pro-studio/scripts/ps2026_commercial_batch_studio.py'
& $python311 -X utf8 $commercialStudio --normalize-cutouts 'cutouts/input' --out 'cutouts/normalized' --canvas 1200x1200 --fill-ratio 0.78
```

CLI cắt sát biên alpha, resize đồng tỷ lệ và căn tâm theo trọng số alpha trên cả hai trục. Mặc định chiều cao chung là 936 px. SKU quá rộng sẽ hạ chiều cao chung xuống mức cả lô có thể nằm vừa canvas. PNG đích giữ nguyên tên, nền trong suốt và ICC nhúng của nguồn nếu có. Chọn thư mục đích riêng. Khi chạy lại, tệp trùng tên trong thư mục đích được thay thế.

## Kiểm định ảnh retouch

```powershell
& $python311 -X utf8 $commercialStudio --verify-retouch 'before.png' 'after.png' --eye-box 420,280,290,125 --skin-box 455,455,90,100 --skin-box 620,455,90,100
& $python311 -X utf8 $commercialStudio --self-test
```

- Dùng hai PNG 8-bit cùng kích thước, cùng vị trí pixel, đã áp dụng hướng ảnh và có ICC sRGB nhúng. Tọa độ lấy theo pixel từ góc trên trái. Bao trọn chân mày, nếp mí, bọng mắt cười và con ngươi bằng một `--eye-box x,y,w,h` hoặc một hộp cho mỗi mắt. Mỗi hộp phải có đúng 0 pixel RGBA thay đổi.
- Đặt `--skin-box` ở vùng da có chi tiết, như má hoặc trán, và có thể lặp cờ để kiểm nhiều vùng. Khi bỏ cờ này, phép đo lấy mẫu toàn khung ngoài vùng mắt. Chỉ số `pore_retention_pct` đo độ khớp của chi tiết tần số cao theo đúng vị trí pixel và cần đạt ít nhất 92%. Báo cáo trả `null` nếu mẫu thiếu chi tiết để tính. Kiểm tra ICC cho cả hai ảnh bằng phép chuyển màu tham chiếu sRGB.
- Báo cáo JSON có mã thoát `0` khi PASS, `1` khi FAIL, `2` khi đầu vào hoặc tham số lỗi. Self-test tạo ảnh RGBA trong thư mục tạm và in `SELF_TEST_OK` khi cả hai chế độ đạt.

## Dựng poster PSD 4 nhóm trong Photoshop 2026

Trong Photoshop, mở **File → Scripts → Browse** và chọn `.agents/skills/photoshop-pro-studio/scripts/ps_extendscript_poster_4layer.jsx`. Chọn đường dẫn PSD mới, rồi chọn ảnh nền, cutout mẫu và ảnh thật của SKU theo các hộp thoại. Có thể bỏ qua từng ảnh và tiêu đề để dựng template. Ảnh được đặt dưới dạng Embedded Smart Object. Để bổ sung SKU vào template, mở khóa nhóm và lớp chờ, thay bằng ảnh SKU thật rồi khóa lại. [Mở script poster PSD](./scripts/ps_extendscript_poster_4layer.jsx)

PSD khổ 1080 × 1920, RGB 8-bit, nhúng `sRGB IEC61966-2.1` và lưu đủ bốn nhóm có thể chỉnh sửa theo thứ tự sau từ dưới lên.

1. `01_BACKGROUND_STUDIO`
2. `02_MODEL_CUTOUT`
3. `03_PRODUCT_SKU_LOCKED` (khóa nhóm và layer SKU)
4. `04_TYPOGRAPHY_SAFEZONE`

Guide vùng chữ đặt tại X = 54, 884, 1024 và Y = 248, 860, 1548. Trong dải Y = 860–1548, giữ chữ và thẻ UI ở X ≤ 884. Soi lại bounds sau khi sửa tiêu đề hoặc thêm chữ. Script tạo tài liệu mới và giữ các tài liệu đang mở của người dùng.

Với các tác vụ retouch trên tài liệu được chỉ định, dùng Photoshop MCP hoặc [run_photoshop_jsx.jsx](./scripts/run_photoshop_jsx.jsx) để chuẩn bị các lớp chỉnh sửa. Khi cần kiểm tra trạng thái tiến trình, dùng lệnh chỉ đọc dưới đây.

```powershell
Get-Process -Name Photoshop -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle, Responding
```

## RAW 16-bit và bàn giao

- Với RAW Beauty hoặc màu Mizuki, xử lý Adobe Portrait trong Camera Raw, chấm mụn cục bộ và tách tần số trực tiếp ở 16-bit. Dùng năm lớp mask Mizuki cho nền, tán lá, vùng tối, nắng xiên và vùng sáng khuôn mặt. [Hướng dẫn màu và mask Mizuki](./references/mizuki-color-and-masking.md)
- Soi nếp mí, bọng mắt, con ngươi và đuôi mày ở 200%. Kiểm tra bốn góc, halo, tem thừa, mép padding và dấu loang inpaint. Với poster, mở PSD để kiểm tra ICC nhúng, bốn nhóm, khóa SKU và vùng an toàn của chữ.
- Lưu script dự án và contact sheet trước/sau tại `G:\My Drive\AI_Full_Studio\03_Du_An\<slug>\`.
