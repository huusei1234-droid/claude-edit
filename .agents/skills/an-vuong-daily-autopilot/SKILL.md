---
name: an-vuong-daily-autopilot
description: Sản xuất video và poster hằng ngày cho An Vượng Pharma (AVPM) với nhân vật Chị Hậu, từ cập nhật nguồn An Vượng đến khóa nhận diện, xoay trang phục, kiểm kịch bản và nghiệm thu.
---

# An Vượng Daily Autopilot V6

## Bước 0. Quét nguồn chỉ đọc và cập nhật Sources

- Mỗi lượt sản xuất bắt đầu bằng việc đọc đủ 5 nhóm Zalo An Vượng theo danh sách đã cấu hình của dự án và Group Facebook `Droppii An Vượng`. Đọc từ mốc đã ghi cho từng nhóm. Giữ chế độ chỉ đọc trên cả sáu nguồn, kể cả khi tài khoản có quyền nhắn tin, đăng bài hoặc tương tác.
- Cập nhật `NHAT_KY_CAP_NHAT_KIEN_THUC_ZALO.md` của dự án. Ghi tên nguồn, thời điểm bài đăng và lúc quét, liên kết hoặc mã bài nếu có, thay đổi đã xác nhận và mục còn cần xác minh. Gộp mục trùng theo nguồn và mã bài. Với nhóm không có cập nhật, ghi mốc quét và tình trạng tương ứng.
- Đồng bộ bản nhật ký mới lên `Sources` của dự án AVPM trên ChatGPT Plus. Mở lại nguồn và đối chiếu mốc cập nhật mới nhất. Khi thiếu quyền đọc, thiếu nhóm đã cấu hình hoặc chưa xác minh được bản đồng bộ, ghi rõ mục bị chặn và giữ Bước 0 ở trạng thái chưa hoàn tất.

## Bước 1. Chốt đề bài và nguồn cho từng sản phẩm

- Chốt chủ đề, SKU, định dạng video hoặc poster, thông điệp chính và ảnh sản phẩm thật `SKU_REF`. Đối chiếu thông tin sản phẩm, quy cách pha và nội dung quảng cáo với nhãn hoặc tài liệu AVPM đã duyệt. Dùng trao đổi trong nhóm để phát hiện thay đổi cần xác minh.
- Khi prompt video có mô tả hoặc cảnh thấy hộp, chai hay gói sản phẩm, đính kèm chính ảnh thật `SKU_REF` trong `refs`. Nếu thiếu ảnh thật, dùng cảnh sinh hoạt hoặc thao tác với ly và ấm nước, bỏ chi tiết về bao bì khỏi prompt.

## Bước 2. Khóa DNA Chị Hậu và chọn trang phục

- Mỗi lượt tạo ảnh mẫu Chị Hậu dùng `chatgpt::chatgpt-image` trên ChatGPT Plus với `noFallback: true` và truyền đồng thời `AV_MODEL_FACE_ANCHOR.png` cùng `AV_MODEL_BODY_ANCHOR.png` trong `refs`. Đối chiếu gương mặt và tỷ lệ cơ thể với hai ảnh mốc trước khi dùng mẫu cho video hoặc poster. Dừng khâu tạo mẫu nếu thiếu ảnh mốc hoặc Plus không thực hiện được yêu cầu.
- Chạy `--next-outfit` đúng một lần cho mỗi video mới. Ghi mã và mô tả vào brief, giữ nguyên trang phục qua các cảnh và khi dựng lại video đó. Poster đi kèm dùng cùng bộ đã chọn. Kho có 16 bộ khác nhau và chỉ bắt đầu vòng mới sau khi đã dùng hết. Dùng cùng một `--state-file` tại vị trí ghi được và dùng chung cho loạt AVPM để giữ vòng xoay qua các phiên và lần đồng bộ skill.

## Bước 3. Viết kịch bản và prompt theo bốn luật thép

1. **Nhịp cắt nhanh**. Giữ mỗi cảnh video trong khoảng `1.8s–2.7s`, tính theo mốc cắt trên timeline thành phẩm.
2. **Sinh hoạt khớp lời thoại**. Chọn hành động và bối cảnh đời thường phù hợp nội dung, chẳng hạn pha đồ uống ở bếp, chuẩn bị đi làm hoặc nghỉ sau vận động. Chỉ chọn Nha Trang khi đề bài hoặc nội dung thật sự cần địa điểm này.
3. **0% Bling-Bling và kim tuyến**. Giữ hình ảnh sạch, ánh sáng tự nhiên. Áp dụng cho prompt, chuyển cảnh, đồ họa, chữ và poster.
4. **Bốn bước pha gói bột liền mạch**. Mỗi video về `AV Protein`, `Bojomi`, `Curcumilk Phyto` hoặc `Collamela` phải cho thấy đủ thao tác mở gói, đổ bột, thêm nước và khuấy hoặc lắc theo hướng dẫn đã duyệt của SKU. Có thể chuẩn bị nước trước nếu hướng dẫn yêu cầu. Giữ continuity của gói, ly, lượng nước và trạng thái bột. Đặt thao tác trong một cảnh hoặc các cảnh liền nhau trên timeline, giữ thứ tự pha đã duyệt.

Với poster, chốt một thông điệp, tên SKU và hình ảnh chủ đạo. Khi có Chị Hậu, dùng ảnh mẫu đã khóa ở Bước 2. Khi lên hình có sản phẩm, đối chiếu ảnh thật, nhãn và chữ trước khi xuất. Dò các cụm y tế bị cấm như `chữa khỏi dứt điểm` và `thuốc đặc trị` trong lời thoại, chữ trên hình và nội dung poster.

## Bước 4. Chạy guard rồi sản xuất

Chạy từ workspace bằng Python 3.11 UTF-8. Thay đường dẫn kịch bản và poster bằng tệp UTF-8 của lượt sản xuất.

```powershell
$avpmPython = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$avpmGuard = '.agents/skills/an-vuong-daily-autopilot/scripts/avpm_autopilot_guard.py'
& $avpmPython -X utf8 $avpmGuard --next-outfit --state-file 'C:\AI\full studio\AVPM_OUTFIT_STATE.sqlite3'
& $avpmPython -X utf8 $avpmGuard --lint-script 'kich-ban.txt' --product 'AV Protein'
& $avpmPython -X utf8 $avpmGuard --lint-script 'poster.txt' --poster
& $avpmPython -X utf8 $avpmGuard --self-test
```

- Ghi thời lượng ngay sau tiêu đề như `Cảnh 01 (2.4s)` hoặc dùng khoảng thời gian như `Cảnh 02 [00:02.4–00:05.1]`. Viết động tác trực tiếp trên dòng cảnh hoặc dòng `Hình:`, chẳng hạn `Xé gói`, `Đổ bột vào ly`, `Thêm nước`, `Khuấy đều`. Dùng `--product` khi SKU nằm ngoài nội dung tệp hoặc chỉ xuất hiện dưới dạng mã nội bộ.
- Guard báo lỗi từ khóa hiệu ứng, thời lượng ngoài dải và chuỗi pha thiếu bước hoặc gián đoạn. Cảnh thiếu mốc và cụm y tế xuất hiện dưới dạng cảnh báo. Sửa lỗi và xử lý cảnh báo trước khi tạo hình. Kiểm tra trực tiếp ý nghĩa lời thoại và trình tự theo nhãn, vì guard đọc văn bản theo mẫu.
- Tạo hình theo brief đã qua guard. Với video AI, dùng thứ tự Gemini Web Pro, Google Flow, Sora Plus rồi Muse theo cấu hình Full Studio. Giữ ảnh mẫu Chị Hậu đã duyệt và `SKU_REF` ở các cảnh cần tham chiếu. Dựng và cắt theo thời lượng từng cảnh. Tạo poster từ hình đã duyệt và nội dung chốt ở Bước 3.

## Bước 5. Nghiệm thu và bàn giao

- Xem thành phẩm ở tốc độ phát thật. So gương mặt, tỷ lệ cơ thể và trang phục với mẫu đã duyệt. Kiểm mốc cắt, lời thoại khớp hành động, chuỗi pha trong các cảnh cần có và nhãn sản phẩm khi lên hình. Kiểm chính tả, bố cục chữ và các cụm y tế trên cả video lẫn poster.
- Với bản dọc `1080x1920`, áp dụng `safe_zone_9x16.py` cho chữ, phụ đề và thẻ UI. Giữ `54 ≤ X ≤ 1024` và `248 ≤ Y ≤ 1548`, đồng thời giữ `X ≤ 884` trong dải `860 ≤ Y ≤ 1548`. Chạy bước nghiệm thu video theo skill `.agents/skills/video-qc-auditor/SKILL.md`.
- Bàn giao các bản xuất được yêu cầu cùng thông tin truy vết gồm chủ đề, SKU, mã bộ trang phục, mốc nhật ký đã đồng bộ và kết quả guard. Chỉ đăng hoặc gửi theo yêu cầu riêng của người dùng.
