---
name: premiere-pro-master-editor
description: Điều phối dựng timeline đa tầng V6 Siêu Cấp bằng Adobe Premiere Pro MCP và Full Studio. Dùng khi cần dựng hoặc kiểm timeline Premiere, rà khoảng lặng, nhập bản dựng từ Final Cut Pro 7 XML, hoặc xuất video và nghiệm thu âm lượng -14.0 LUFS.
---

# Premiere Pro Master Editor V6 Siêu Cấp

Làm việc từ `C:\AI\full studio`. Xác định project, sequence, tư liệu, tỷ lệ, fps, mốc Hook/CTA và đầu ra theo brief. **Cấm chạy `taskkill` hoặc `Stop-Process` lên `Adobe Premiere Pro.exe`.** Nếu bridge bị chặn bởi hộp thoại Premiere, xác định hộp thoại và xử lý qua giao diện khi có quyền. Giữ các thao tác tham chiếu playhead, active sequence và ghi timeline theo thứ tự.

## Điều phối Premiere Pro MCP

1. **Kết nối và khóa đích.** Gọi `get_capabilities` với `tool_query` theo nghiệp vụ và `tool_limit: 10`, hoặc dùng `tool_names` cho thao tác cụ thể. Dùng `verify_premiere_connection` trước khi làm việc với host. Gọi `get_premiere_state` để xác nhận project, active sequence và selection. Đọc `get_sequence_settings` và `get_full_sequence_info` theo `sequence_id`. Đi hết `pagination.nextOffset` nếu cần tập clip đầy đủ. Với thao tác ghi, dùng `expected_project_path` trên CEP khi schema và bridge hỗ trợ hoặc thông tin nhận diện snapshot mà UXP yêu cầu. Nếu timeout, kiểm tra trạng thái sequence và thao tác trước khi gửi lại. Dùng idempotency key của cùng thao tác nếu tool hỗ trợ retry.
2. **Rà điều kiện dựng.** Chạy `inspect_edit_readiness` trên đúng sequence đang active, với `primary_video_track: 0` cho V1. Xem gap, clip tắt, track mute và Motion Scale. Kiểm `get_offline_media` khi có nghi vấn link. Xác nhận các khoảng trống có chủ đích theo brief. Với project đã dựng, giữ bản dựng gốc hoặc dùng checkpoint phù hợp trước khi đổi cấu trúc.
3. **Làm sạch thoại.** Gọi `detect_silence` với `media_path` tuyệt đối hoặc `project_item_id`. Tool dùng FFmpeg, với mặc định `noise_threshold_db: -30` dBFS và `min_duration_seconds: 1.5`. Kết quả thuộc media gốc. Đưa các cặp `start_seconds` và `end_seconds` vào `map_source_ranges_to_timeline` trên track cần sửa. Đọc các trang kết quả và kiểm lại vị trí cắt trên sequence. Với clip đảo chiều hoặc đổi tốc độ mà tool từ chối map, kiểm bằng waveform/playback ở sequence. Nghe quanh mỗi điểm cắt để giữ đầu và cuối câu, nhịp thở có chủ đích và đồng bộ hình–tiếng. Dùng fade ngắn nếu nghe tiếng bật tại mép cắt.
4. **Dựng và đối chiếu.** Dùng thao tác sửa đã đăng ký cho project đang mở hoặc xuất XML theo phần dưới để nhập một sequence. Kiểm lại đúng media, track, frame in/out, alpha đồ họa và mốc Hook/CTA trên sequence đã dựng. Dùng trạng thái mới để xác nhận kết quả rồi lưu project khi phạm vi công việc bao gồm lưu bản dựng.
5. **Kiểm timeline.** Đưa snapshot đầy đủ vào `audit_timeline_health` qua `snapshot`, với `expected_frame_rate` và `expected_duration_seconds` theo brief. Chuẩn hóa track và clip theo schema `tracks` hoặc `videoTracks`/`audioTracks`, dùng `start_seconds` và `end_seconds` trong snapshot. Xem cảnh báo flash frame, gap, chồng clip, clip tắt, lặp shot, tốc độ bất thường và đuôi trống tại timecode tương ứng. Kiểm Hook, CTA, các điểm cắt thoại và cuối video bằng hình và playback.
6. **Xuất và nghiệm thu.** Gọi `validate_export_preset` với `.epr` đã chọn. Dùng `export_and_verify` khi CEP hỗ trợ xuất trực tiếp, với `preset_path`, `output_path` tuyệt đối chưa tồn tại, `range: "entire"` cho toàn sequence hoặc phạm vi đã duyệt, và `decoded_qc: true`. Trong `contract`, truyền `width`, `height`, `frame_rate`, `duration_seconds`, `target_lufs: -14.0` và các yêu cầu codec, kênh tiếng, dung sai hoặc true peak theo brief. Với job AME dài, dùng `export_sequence_job_start` và `get_export_job_status`. Kiểm hàng đợi trước khi chạy batch để tránh khởi động job ngoài phạm vi. Chờ trạng thái `completed` với `verified: true`, rồi dùng `verify_delivery_conformance` trên chính tệp đó. Ghi đường dẫn, thông số đo và timecode các phát hiện còn mở.

## Chuẩn sáu track và QC Full Studio

| Track | Nội dung và điểm kiểm |
| --- | --- |
| `V1_Base_Footage` | Hình chính, mạch dựng và đồng bộ với thoại. |
| `V2_Broll_Overlay` | B-roll minh họa, đặt theo ý thoại hoặc nhịp chuyển cảnh. |
| `V3_SafeZone_Graphics` | Hook, chữ, logo và CTA. Kiểm bounds sau scale, crop và animation. |
| `A1_Clean_Voice` | Thoại rõ, khớp khẩu hình và đủ âm tiết tại điểm cắt. |
| `A2_Micro_SFX` | Hiệu ứng âm ngắn tại đúng cue, giữ độ rõ của thoại. |
| `A3_BGM_Ducked` | Hạ nhạc dưới câu nói và phục hồi mượt ở khoảng nhạc. Có thể để trống khi brief yêu cầu tắt nhạc. |

Với `1080×1920`, giữ toàn bộ chữ, phụ đề và thẻ UI trong `54 ≤ X ≤ 1024`, `248 ≤ Y ≤ 1548`. Tại mọi phần tử đi qua dải `860 ≤ Y ≤ 1548`, giữ cạnh phải trong `X ≤ 884`. Kiểm theo `safe_zone_9x16.py` khi có và soi các frame có vị trí chuyển động lớn nhất.

Mục tiêu trên **mix cuối của tệp xuất** là **-14.0 LUFS Integrated**. Cân thoại, SFX và ducking trước, sau đó chỉnh mix theo mức đo. Kiểm lại Integrated LUFS và true peak trên đúng tệp bàn giao sau mỗi lần render lại. Khi cần đo cục bộ, lấy phần tổng kết của `ffmpeg -hide_banner -i <final.mp4> -vn -af ebur128=peak=true -f null -`. Với video final Full Studio, dùng `.agents/skills/video-qc-auditor/SKILL.md` theo yêu cầu nghiệm thu dự án.

## Bridge manifest → Final Cut Pro 7 XML

Chạy từ thư mục làm việc chính, với thư mục đích đã tồn tại.

```powershell
$py = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$bridge = '.\.agents\skills\premiere-pro-master-editor\scripts\premiere_xml_and_qc_bridge.py'
& $py -X utf8 $bridge --self-test
& $py -X utf8 $bridge --manifest '.\timeline.json' --out '.\sequence.xml'
```

`--self-test` sinh fixture trong bộ nhớ, đọc lại bằng `xml.etree.ElementTree.fromstring` và in `SELF_TEST_OK`. CLI xuất `xmeml` phiên bản 4 ở `1080×1920` hoặc `1920×1080`, 24 hoặc 30 fps nguyên. XML giữ ba track hình và ba track tiếng, kể cả track rỗng, cùng marker **Hook vàng** và **CTA xanh dương**. [Apple XMEML v4](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/DTD/DTD.html) · [Màu marker trong XML Premiere](https://github.com/evamedia/fcpxml-tools/blob/main/extract_markers.py)

Ví dụ `timeline.json` với đủ sáu lớp dựng.

```json
{
  "name": "Full Studio – Tập 42",
  "width": 1080,
  "height": 1920,
  "fps": 30,
  "sources": {
    "base": {"path": "Media/Cảnh chính.mov", "duration_frames": 240, "video": {"width": 1080, "height": 1920}},
    "broll": {"path": "Media/B-roll.mov", "duration_frames": 120, "video": {"width": 1080, "height": 1920}},
    "cta": {"path": "Media/CTA alpha.mov", "duration_frames": 60, "video": {"width": 1080, "height": 1920, "alpha": "straight"}},
    "voice": {"path": "Media/Thoại sạch.wav", "duration_frames": 240, "audio_channels": 1},
    "sfx": {"path": "Media/Cue.wav", "duration_frames": 24, "audio_channels": 1},
    "bgm": {"path": "Media/Nhạc.wav", "duration_frames": 240, "audio_channels": 2}
  },
  "tracks": {
    "V1_Base_Footage": [{"source": "base", "start_frame": 0, "in_frame": 12, "duration_frames": 120}],
    "V2_Broll_Overlay": [{"source": "broll", "start_frame": 30, "duration_frames": 48}],
    "V3_SafeZone_Graphics": [{"source": "cta", "start_frame": 90, "duration_frames": 30}],
    "A1_Clean_Voice": [{"source": "voice", "start_frame": 0, "duration_frames": 120}],
    "A2_Micro_SFX": [{"source": "sfx", "start_frame": 90, "duration_frames": 12}],
    "A3_BGM_Ducked": [{"source": "bgm", "start_frame": 0, "duration_frames": 120}]
  },
  "markers": {"Hook": 0, "CTA": 90}
}
```

- Đường dẫn `path` là đường dẫn tệp tuyệt đối hoặc tính từ thư mục manifest. Chuẩn bị đủ media trên máy Premiere. `sources.*.duration_frames` là tổng số frame tại fps của nguồn. `fps` mặc định theo sequence và nhận `24`, `25`, `30`, `48`, `50`, `60`, `120`. Với nguồn NTSC CFR, dùng timebase nguyên và `ntsc: true` cho tỷ lệ `1000/1001`. Dùng `audio_channels` 1 hoặc 2 cho nguồn tiếng và khai đúng `sample_rate_hz` nếu khác `48000`.
- `start_frame`, `tracks.*[].duration_frames` và giá trị marker tính theo frame sequence. `in_frame` tính theo frame gốc và mặc định `0`. Mọi mốc bắt đầu đếm từ `0`, điểm cuối là mốc loại trừ. Bridge làm tròn phần trim về frame nguồn gần nhất khi fps khác nhau. Cung cấp `video.width`, `video.height` và `video.alpha` theo tư liệu đã render, với hỗ trợ `none`, `straight`, `black` và `white`.
- Ghi Hook/CTA theo brief trong phạm vi sequence. Điền các track đang sử dụng, có thể bỏ key track rỗng. Bridge kiểm tra trim vượt media và va chạm trên cùng track. Các clip ở những track khác nhau có thể chồng theo bố cục.
- Dùng `import_fcp_xml` nếu `get_capabilities` cho thấy tool được đăng ký và có quyền cho phiên hiện tại. Có thể nhập trực tiếp bằng **File → Import** trong Premiere. Sau khi mở sequence mới, đối chiếu fps, kích thước, sáu track, trim, media online, kênh tiếng và màu hai marker. Khi host đổi màu hoặc tên track lúc import, đặt lại trong Premiere và đọc lại kết quả. XML trao đổi dựng cắt và tham chiếu media. Áp dụng keyframe ducking trong Premiere hoặc dùng stem đã duck, sau đó đo loudness trên tệp xuất. [Hướng dẫn nhập XML của Adobe](https://helpx.adobe.com/pdf/premiere_pro_reference.pdf) · [Thiết lập track mono/stereo của Blender Studio](https://studio.blender.org/blog/opentimelineio-in-blender/)
