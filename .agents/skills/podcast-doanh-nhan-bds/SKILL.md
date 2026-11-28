---
name: podcast-doanh-nhan-bds
description: >-
  Sản xuất video podcast, phỏng vấn doanh nhân và nội dung tài chính, bất động sản
  chuẩn Full Studio V6 Siêu Cấp. Dùng khi dựng tập đầy đủ hoặc trích đoạn dọc, phối
  tiêu đề kép băng ngọc và chữ ký tiếng Việt, hoặc kiểm tra BGM có sẵn trước khi mix.
---

# Podcast Doanh Nhân, Tài Chính & Bất Động Sản V6 Siêu Cấp

Dựng sườn theo lượt hỏi–đáp và ý trọn vẹn. Khi cắt sang đoạn trích, giữ phần ngữ cảnh cần thiết để người xem hiểu ai đang nói và các con số đang nói về điều gì. Đối chiếu tên khách mời, chức danh, tên dự án, số liệu và đơn vị với nguồn đã duyệt trước khi lên chữ.

## Tiêu đề kép quầng sáng băng ngọc tâm giữa và chữ ký viết tay đè

1. Dùng `render_podcast_signature_title()` trong `edit/canvas-tools/podcast_bds_title.py` để xuất PNG RGBA trong suốt. Truyền nội dung headline, chữ ký, `pair_key`, `theme` và `out_png`. Dùng font TTF theo `FONTS_DIR` của renderer. Xem dấu tiếng Việt ở kích thước xuất thực tế, nhất là các tổ hợp `Ắ`, `Ễ`, `Ộ`, `Ự`.
2. Tô quầng sáng ngay trên mặt headline. Theme `cyan_ice` chuyển từ hai mép cobalt `#1F42A6` qua cyan `#24B2E0` đến lõi băng ngọc `#84FFF6`, với hào quang mềm `#2EE8E4`. Dùng `gold_luxury` với hào quang `#FFCE58` cho BĐS sang trọng hoặc `rose_satin` với hào quang `#FF6EBA` cho trích đoạn chiêm nghiệm.
3. Đè chữ ký trắng `#FFFFFF` lên mặt chữ chính, có bóng tối mềm và viền sáng nhẹ. Với `bottom_center`, đặt chữ ký ở giữa ngang, bắt đầu khoảng 62% chiều cao headline. Với `top_left`, gác chữ ký lệch lên vai trái. Giữ nét ký và dấu đọc được ở chỗ giao nhau. Giảm cỡ hoặc rút gọn câu nếu nét chữ hay hào quang chạm mép PNG.

Sáu cặp font vàng tiếng Việt dùng đúng khóa và bố cục của renderer.

| `pair_key` | Headline | Chữ ký | Bố cục | Dùng cho |
| --- | --- | --- | --- | --- |
| `magnesium_amsterdam` | Unbounded Black | WindSong Medium | `bottom_center` | BĐS, mặc định `bds` |
| `chetta_adventures` | Playfair Display Bold | WindSong Regular | `bottom_center` | Villa, penthouse, bất động sản hạng sang |
| `barlow_artful` | Barlow Condensed ExtraBold Italic | Birthstone Bounce Medium | `top_left` | Tài chính, mặc định `tai-chinh` |
| `blona_starcity` | Saira ExtraCondensed ExtraBold | Cherish Regular | `top_left` | Hook tài chính hoặc chủ đề cần headline hẹp |
| `alexander_ameyallinda` | Montserrat Black | Birthstone Bounce Medium | `bottom_center` | Phỏng vấn, mặc định `doanh-nhan` |
| `braven_bengoda` | Prata Regular | Ephesis Regular | `bottom_center` | Trích dẫn, mặc định `triet-ly` |

## Đo RMS khoảng nghỉ thoại trước khi thêm BGM

Dùng [`.agents/skills/podcast-doanh-nhan-bds/scripts/podcast_bds_pack_builder.py`](./scripts/podcast_bds_pack_builder.py) trên bản mix nguồn sẽ đưa lên timeline, trước khi thêm BGM hay SFX. Script dùng Silero VAD trên từng kênh của track âm thanh đầu tiên. Khoảng đo phải vắng lời trên tất cả các kênh và dài ít nhất 120 ms sau khi chừa đệm ở biên lời. RMS gộp theo số mẫu trên từng kênh ở sample rate gốc. `non_speech_rms_dbfs` bằng `null` khi mọi mẫu trong khoảng đo đều bằng 0.

| Kết quả | Quy tắc mix |
| --- | --- |
| `RMS > -38.0 dBFS` · `has_existing_bgm: true` · `allow_new_bgm: false` | Tuyệt đối không chèn chồng BGM mới. Chỉ đi nhẹ Tactile Micro-SFX ở mức gain clip `-20 dB`, tại điểm xuất hiện chữ hoặc chuyển ý cần nhấn. |
| `RMS ≤ -38.0 dBFS` · `has_existing_bgm: false` · `allow_new_bgm: true` | Có thể thêm một lớp BGM nếu bản dựng cần. Nghe kiểm tra ở cả khoảng nghỉ và đoạn đang có lời. |

Tiếng máy lạnh, khán giả hoặc nhạc có lời có thể ảnh hưởng kết quả VAD và RMS. Nghe kiểm tra nền quanh ngưỡng. Nếu CLI báo thiếu track hoặc thiếu khoảng nghỉ, xem lại master và tìm một đoạn nghỉ đại diện trước khi quyết định thêm BGM.

Chạy các lệnh từ thư mục gốc Full Studio bằng Python 3.11. Probe và self-test cần `ffmpeg`, `ffprobe` trên `PATH`, `numpy` và Silero VAD từ `faster-whisper` 1.2.1 với `onnxruntime`. Script có thể chạy qua môi trường ảo `voice-studio` của Full Studio khi Python chính thiếu VAD. Gợi ý font dùng `numpy`, `Pillow` và đọc preset trực tiếp từ renderer.

```powershell
$podcastPython = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$podcastBuilder = '.agents/skills/podcast-doanh-nhan-bds/scripts/podcast_bds_pack_builder.py'
& $podcastPython -X utf8 $podcastBuilder --probe-bgm 'media\podcast master.mp4'
& $podcastPython -X utf8 $podcastBuilder --recommend-font-pair bds
& $podcastPython -X utf8 $podcastBuilder --self-test
```

`--recommend-font-pair` nhận `bds`, `tai-chinh`, `doanh-nhan`, `triet-ly` và trả `pair_key`, `theme`, font, bố cục và mã HEX để đặt tiêu đề. `--self-test` tạo hai WAV tạm `-55 dBFS` và `-31 dBFS` trong thư mục làm việc, kiểm cả RMS lẫn quyết định BGM và in `SELF_TEST_OK` khi cả hai đạt.

## Nhịp dựng và năm vùng đen cấm 9:16

- **J-cut `0.25–0.40 s`**. Cho tiếng của câu hoặc góc máy kế tiếp vào trước điểm cắt hình. Dùng ở chỗ chuyển lượt hỏi–đáp hoặc chuyển góc khi phù hợp với lời.
- **L-cut `0.25–0.40 s`**. Giữ tiếng người đang nói qua điểm cắt hình để đỡ cảnh phản ứng hoặc B-roll. Nghe lại biên cắt để giữ nguyên âm tiết và nhịp thở.
- **Zoom tâm lý `1.00 → 1.05`**. Đẩy khung hình chậm theo một ý quan trọng, lấy mắt hoặc gương mặt làm điểm neo. Kiểm tra crop ở cả hai đầu chuyển động. Giữ tiêu đề và phụ đề trên lớp riêng để vị trí của chúng không đổi theo zoom.

Áp vùng an toàn cho chữ, chữ ký, hào quang thấy được, phụ đề, lower third và thẻ UI trên canvas 1080 × 1920.

| Vùng cấm | Giới hạn |
| --- | --- |
| Đỉnh | `Y < 248 px` |
| Đáy | `Y > 1548 px` |
| Mép trái | `X < 54 px` |
| Mép phải phía trên | `X > 1024 px` khi `Y < 860 px` |
| Cột tương tác phải dưới | `X > 884 px` khi `Y = 860–1548 px` |

Chừa đệm theo `edit/canvas-tools/safe_zone_9x16.py`, với `Y = 250–1545 px` và mép phải theo cao độ. Với hộp chữ chạm dải dưới từ `Y = 860 px`, giữ toàn bộ hộp trong `X = 54–884 px`. Kiểm tra trên canvas 1080 × 1920 đã ghép PNG, tại điểm chữ vào, ở vị trí ổn định và khi chữ ra.
