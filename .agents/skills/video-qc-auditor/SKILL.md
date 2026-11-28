---
name: video-qc-auditor
description: Kiểm duyệt độc lập video Final theo V6 Forensic Siêu Cấp. Dùng ở bước nghiệm thu Phim AI, TVC, Talking Head, CapCut, HyperFrames và Remotion trước khi ký PASS và bàn giao.
---

# Cẩm nang Kiểm duyệt 6 Bước V6 Forensic Siêu Cấp

Kiểm duyệt đúng tệp MP4 chuẩn bị bàn giao. Lifecycle Hook `PreToolUse` (`video-qc-gate`) dùng chứng nhận `<final.mp4>.qc_pass.json` để mở khóa giao file. Sau mỗi lần render lại hoặc sửa bản MP4, chạy lại từ Bước 1 trên bản mới.

## Bước 1 — Quét kỹ thuật và lập hồ sơ cho mọi cú cắt

Chạy từ thư mục `C:\AI\full studio` trong PowerShell. Analyzer cần Python 3.11, `opencv-python`, `numpy` và `ffprobe`/`ffmpeg` trên PATH. Gate dùng môi trường Voice Studio cho Whisper.

```powershell
$video = 'C:\du-an\Final.mp4'
$qc = 'C:\du-an\QC'
$py = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$gatePy = '.\voice-studio\.venv\Scripts\python.exe'
$gate = '.\edit\canvas-tools\video_qc_gate.py'
$analyzer = '.\.agents\skills\video-qc-auditor\scripts\forensic_qc_analyzer.py'

& $py -X utf8 $analyzer --self-test  # Kiểm tra công cụ, kết quả là SELF_TEST_OK
& $py -X utf8 $analyzer --video $video --json-out (Join-Path $qc 'forensic_qc.json')
if ($LASTEXITCODE -ne 0) { throw 'Quét forensic gặp lỗi.' }
& $gatePy -X utf8 $gate inspect $video --out-dir $qc
```

Thêm `--hook-end-sec <giây>` vào lệnh `inspect` khi có Hook và `--cuts-json <tệp>` khi có danh sách đầy đủ các cú cắt từ timeline. Đối chiếu số cú cắt và mốc thời gian với timeline. Hồ sơ gồm `forensic_qc.json`, `<final.mp4>.qc_audit.json`, `QC_FINAL_ALL_CUTS_FULL.jpg` và `QC_FINAL_ALL_CUTS_ZOOM.jpg`. Nếu gate trả `exit 2` (`MACHINE_FAIL`), hoặc có lỗi chạy công cụ, xử lý nguyên nhân và quét lại trước khi chuyển bước.

- Đối chiếu `width`, `height` và `fps` với preset. Kích thước phản ánh xoay hiển thị của video. `fps_ratio` giữ tỷ lệ chính xác từ `avg_frame_rate` khi có. Với video VFR, dùng mốc PTS theo giây trong báo cáo khi định vị frame.
- `av_delta_s` là chênh lệch tuyệt đối thời lượng giữa track tiếng đầu tiên và track hình đầu tiên có nội dung. Đối chiếu ngưỡng gate `0.12 s` và nghe kiểm tra đồng bộ tại các mốc có âm–hình rõ. Giá trị `null` cho biết thiếu thời lượng track để tính.
- `letterbox` và `pillarbox` chỉ vị trí, độ dày và khoảng thời gian của dải đen bám mép từ 2 px, duy trì ít nhất 3 frame và 0,25 giây. Mở đúng timecode để xác nhận viền thừa.
- `boundary_flash_frames` liệt kê chỉ số frame bắt đầu từ 0. `boundary_flash_events` ghi loại đen/trắng và mốc PTS của các cụm nháy ngắn tối đa 125 ms có bước nhảy độ sáng ở mép. `blank_frame_ranges` ghi cả các cụm đen hoặc trắng kéo dài. `end_frame` là frame cuối của cụm, còn `end_time_s` là mốc đã ra khỏi cụm. Xem từng frame trước, trong và sau vùng cảnh báo để phân biệt lỗi biên với fade hoặc flash có chủ đích.
- `audio.integrated_lufs` và `audio.true_peak_dbtp` lấy từ tổng kết `ffmpeg -af ebur128=peak=true`. So với mục tiêu của preset dự án. `audio.status` phân biệt `measured`, `silent` và `no_audio`. Khi track im lặng, true peak âm vô cực được ghi là `null`.

Mã thoát `0` của analyzer cho biết đã xuất đủ báo cáo. Kết luận PASS do kiểm duyệt viên đưa ra sau Bước 5.

## Bước 2 — Soi 100% cú cắt và đối chiếu sản phẩm

Gọi subagent độc lập `video-qc-auditor`. Với `invoke_subagent`, dùng `TypeName: "video-qc-auditor"`. Chuyển MP4, hai báo cáo JSON, hai bảng ảnh đủ 100% cú cắt, `SKU_REF` nếu có và tóm tắt kịch bản. Subagent dùng bảng full để kiểm tra bố cục, bảng zoom để soi chi tiết và video gốc để kiểm tra diễn biến giữa các ảnh trích.

- Đối chiếu mọi lần xuất hiện của sản phẩm với `SKU_REF`, kể cả lúc bị che một phần, trong phản chiếu và ở hậu cảnh. So hình dáng, tỷ lệ, màu, tên, logo, mặt nhãn, nắp và mép hộp. Chặn mọi hộp trắng giả, nhãn AI, sai SKU, sai thiết kế hoặc sản phẩm xuất hiện ở cảnh không cần.
- Với HTPM và AVPM, khi làm lại cảnh AI có bao bì, đưa ảnh thật `SKU_REF` vào `refs` trước khi mô tả hộp hoặc chai. Nếu cảnh cần xác minh sản phẩm mà hồ sơ thiếu ảnh đối chiếu, ghi rõ cảnh và giữ lại để kiểm tra.
- Ghi timecode và mô tả từng sai lệch để người dựng có thể sửa đúng frame hoặc cảnh.

## Bước 3 — Đếm cảnh Toàn và kiểm tra nhân quả vật lý

- Gắn cỡ cảnh cho mỗi shot giữa hai cú cắt. Đếm mỗi shot WS/MLS có chức năng cảnh Toàn một lần. Chia số shot Toàn cho tổng số shot của bản Final. Tỷ lệ phải nằm trong khoảng 25–35%, tính theo số shot và xét trước khi làm tròn. Ghi tử số, mẫu số và phần trăm.
- Kiểm từng điểm nối và diễn biến trong shot. Hành động đi trước hệ quả. Vị trí, hướng di chuyển, hướng nhìn, đạo cụ, tay cầm và trạng thái vật thể phải khớp khi đổi góc máy. Ví dụ, nhân vật giấu vật trước khi người khác phát hiện, rồi người phát hiện di chuyển từ vị trí đã thiết lập đến nơi bắt quả tang.
- Ghi cặp timecode và chi tiết vật lý hoặc nguyên nhân còn thiếu tại mỗi lỗi. Đối chiếu chuyển cảnh có chủ đích với kịch bản và footage.

## Bước 4 — Nghe toàn bộ thoại và xác nhận 0% lặp hoặc đứt từ

- Đọc `audio_audit.repetitions`, `audio_audit.eof_cutoff` và transcript Whisper trong `qc_audit.json`. Nghe trọn bản Final, kiểm lại Hook, đầu và cuối mỗi câu, mọi điểm cắt thoại và phần âm cuối tệp. Dò cả từ hoặc cụm từ lặp do ghép take và âm tiết mất ở giữa câu.
- Tiêu chí PASS là 0 từ lặp ngoài kịch bản và 0 từ bị đứt. Dùng waveform và đoạn thoại gốc để xác định chính xác chỗ cần phục hồi. Đối chiếu chuyển động môi tại các mốc nói và so LUFS/True Peak với preset.

## Bước 5 — Kiểm 5 vùng cấm trên bản dọc 1080×1920

Dùng vùng có đệm của `edit/canvas-tools/safe_zone_9x16.py`. Các cận dưới đây là khoảng nửa mở theo pixel, gồm cận đầu và loại cận cuối. Các vùng có thể giao nhau ở góc.

| Vùng | Phạm vi cấm |
| --- | --- |
| Đỉnh | `0 ≤ Y < 250` |
| Đáy | `1545 ≤ Y < 1920` |
| Trái | `0 ≤ X < 54` |
| Phải trên | `1024 ≤ X < 1080`, `0 ≤ Y < 860` |
| Cột tương tác phải dưới | `884 ≤ X < 1080`, `860 ≤ Y < 1545` |

- Dùng `safe_zone_9x16.zones` để định vị frame nghi vấn. `edge_density` là phần diện tích vùng có cạnh Canny. `edge_change_density` là phần diện tích thay đổi trạng thái cạnh giữa hai frame liên tiếp. Mỗi mục ghi trung bình, cực đại và mốc frame/PTS của cực đại. Nền nhiều chi tiết hoặc chuyển động cũng có thể làm các số đo tăng. Với kích thước khác, báo cáo ghi `safe_zone_9x16.applicable: false`.
- Soi tất cả phụ đề, tiêu đề, logo, sticker, thẻ UI, PiP/Bento và lớp phủ, gồm viền, bóng, đường di chuyển và các frame vào/ra. Dùng `is_box_safe_9x16` cho hộp bao cả hiệu ứng hoặc `audit_rgba_overlay_safe_zone` cho lớp phủ RGBA khi có. Tiêu chí PASS là 0 pixel lớp phủ lấn vùng cấm.

## Bước 6 — Ký PASS và giao đúng bản đã kiểm

Subagent kiểm duyệt độc lập chỉ ký PASS sau khi năm bước trên đạt và mọi lỗi đã được sửa rồi kiểm lại. Ghi nhận kết quả về SKU, tỷ lệ cảnh Toàn, nhân quả, thoại, các cảnh báo forensic và vùng an toàn. Gate yêu cầu ghi chú có ít nhất 30 ký tự. Dùng kết luận thực tế thay cho phần giữ chỗ dưới đây.

```powershell
& $gatePy -X utf8 $gate sign $video --verdict PASS --auditor '<tên kiểm duyệt viên>' --notes '<kết quả có số liệu và các mốc đã kiểm>'
```

Gate đối chiếu fingerprint với `qc_audit.json` trước khi ký và ghi `<final.mp4>.qc_pass.json` với `file_size` và `sha256_head_tail`. Khi đồng bộ, chuyển chứng nhận bằng `copy-cert` hoặc luồng `final_delivery.py`. Có thể dùng mẫu dưới đây để kiểm SHA-256 toàn tệp khi sao chép thủ công.

```powershell
$dest = 'C:\duong-dan-ban-sao\Final.mp4'
if ((Get-FileHash -LiteralPath $video -Algorithm SHA256).Hash -ne
    (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash) {
    throw 'MP4 đích khác bản đã kiểm duyệt.'
}
& $gatePy -X utf8 $gate copy-cert $video $dest
```

Kiểm tra cặp MP4 và chứng nhận PASS tại từng điểm giao của dự án trên Google Drive, `04_Videos_Final` và `XUẤT CAPCUT`. Sau khi xác nhận, mở thẻ vị trí file bằng `show_file_location_card` nếu môi trường hỗ trợ.
