---
name: talking-head-v3
description: >-
  Dựng Talking Head dọc 1080×1920 @ 30fps chuẩn V6 Siêu Cấp cho dược sĩ và
  chuyên gia tư vấn theo BOJOMI V3 và LT PLUS V3. Lập 4 cảnh Split B-Roll
  từ transcript, dựng nền phòng thật với RVM, chữ lớn và vòng xoay sau đầu,
  kiểm vùng an toàn cho phụ đề từng từ và phối BGM C-Major ở -14.0 LUFS.
---

# Talking Head V3 · V6 Siêu Cấp

Quy trình dựng **Talking Head dọc 1080×1920 @ 30fps** dựa trên **BOJOMI An Vượng V3** và **Viên Đặt LT PLUS Hằng Thu V3**, dùng RVM Person Matting, Google Flow và FFmpeg. Bản V6 bổ sung planner, kiểm phụ đề theo tọa độ và sân khấu HTML theo frame.

## Bộ công cụ V6

- CLI Python 3.11 tại `.agents/skills/talking-head-v3/scripts/talking_head_v3_master_pipeline.py`.
- Sân khấu HTML tại `.agents/skills/talking-head-v3/templates/talking_head_v3_stage_9x16.html`.

```powershell
$python = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$pipeline = '.agents/skills/talking-head-v3/scripts/talking_head_v3_master_pipeline.py'
& $python -X utf8 $pipeline --self-test
& $python -X utf8 $pipeline --plan-split-broll main_cut_clean.json --out plan.json
& $python -X utf8 $pipeline --check-subtitles words.json
& $python -X utf8 $pipeline --build-audio-filtergraph --duration 60 --split-at 30 --out mix_v6.ffgraph
```

### Hợp đồng timeline và media

- `main_cut_clean.json` dùng `segments[].start/end/text` hoặc `segments[].words[]` kiểu Whisper. Dạng phẳng `{"words":[{"word":"Theo dõi","start":0.2,"end":0.6}]}` cũng dùng được. Thêm `duration` theo giây để bao cả đuôi hình sau câu cuối. Thêm `protected_ranges` với các cặp `start/end` để giữ nguyên Hook và cảnh người nói trực tiếp cầm hoặc chỉ hộp. Planner cần tối thiểu bốn khoảng 12 frame khả dụng.
- Planner chia bốn cửa sổ theo thứ tự thời gian, ưu tiên đặt đầu cảnh gần mốc lời và nhắm khoảng 2,4 giây mỗi cảnh. `start_frame` là frame đầu và `end_frame` là frame ngay sau cảnh. `dim_room_alpha` lưu các mốc `0.0 → 0.42 → 0.0`. Fade nền dùng `smoothstep` 15 frame mỗi đầu ở cảnh đủ dài. Lớp B-Roll có fade riêng tối đa 13 frame.
- Có thể thêm 4 object `assets` theo thứ tự cảnh. Mỗi object nhận `flow_src`, `product_src`, `flow_in` theo giây và `flow_focus`/`product_focus` theo `[x, y]` chuẩn hóa `0..1`. Mặc định là `assets/flow_01.mp4` đến `assets/flow_04.mp4` và `assets/SP_PRODUCT_CUTOUT.png`. Thay tên mẫu bằng tài nguyên thật trước khi dựng. Với ảnh sản phẩm, chừa đệm trong suốt quanh bao bì và kiểm tra chữ trên nhãn sau khi crop.
- Sao chép HTML vào thư mục dự án. Dùng `assets/presenter_room.mp4` và `assets/presenter_cutout.webm` có alpha, cùng khung hình, đồng bộ cùng frame đầu. Trong `stage-data`, dán nội dung `plan.json` vào `plan`, danh sách từ vào `captions`, và thêm các cue dạng `{"text":"THEO DÕI","start_frame":0,"end_frame":90}` vào `keywords`. Khi dán JSON chứa ký tự `<`, ghi ký tự đó dưới dạng `\u003c`.
- Sân khấu dựng theo thứ tự nền phòng, lớp tối, vòng xoay và chữ lớn, người nói đã tách nền, video Flow và Showcase, rồi đến phụ đề. `await window.talkingHeadV3.setFrame(60)` hiển thị giây thứ hai và đợi media sẵn sàng. `window.talkingHeadV3.configure({...})` có thể nạp cấu hình trực tiếp. `window.talkingHeadV3.captionLayout()` trả lại `words` kèm bbox cuối để đưa vào CLI. Template mặc định đặt phụ đề dưới hai thẻ Split và cho phép chỉnh bbox theo cằm, áo và hộp thật của từng footage.
- `words.json` dùng danh sách từ hoặc `{"words":[...]}`. Mỗi từ có `bbox: [left, top, right, bottom]` theo px hoặc object `x/y/width/height`. Bbox cuối bao cả viền và glow. Nếu bbox mới đo chữ gốc, truyền thêm `glow_padding` để mở đều bốn cạnh. `--check-subtitles` trả JSON và mã `0` khi đạt, `1` khi từ vượt vùng hoặc thiếu bbox, `2` khi cấu trúc tệp đầu vào sai. Kiểm bằng mắt để xác nhận Face-Safe và Box-Safe trên footage thật.

### Tạo filtergraph FFmpeg

Gán input `0:a` cho giọng đọc đã dựng, `1:a` cho `bgm_warm_fretless.mp3` và `2:a` cho `bgm_bright_riley.mp3`. Có thể dùng `-stream_loop -1` trước từng input BGM khi nguồn ngắn. `--duration` là thời lượng hình, mặc định 60 giây. `--split-at` là tâm crossfade, mặc định giữa timeline. Chèn SFX vào stem giọng trước khi phối nếu dự án có cue SFX.

```powershell
ffmpeg -hide_banner -i voice.wav -stream_loop -1 -i bgm_warm_fretless.mp3 -stream_loop -1 -i bgm_bright_riley.mp3 -/filter_complex mix_v6.ffgraph -map '[aout]' -f null -
```

Lưu object JSON `loudnorm` cuối log thành `mix_stats.json`. Sinh lại graph với cùng `--duration` và `--split-at`, thêm `--loudnorm-stats mix_stats.json` và xuất `mix_v6_pass2.ffgraph`. Dùng graph lượt hai với đúng ba input trên, map `[aout]` ra WAV 48 kHz stereo rồi ghép hình. Đo lại file giao để xác nhận mục tiêu **-14.0 LUFS** và **True Peak ≤ -0.95 dBTP**.

---

## 1. Đường Dẫn Lưu Trữ & Môi Trường Chuẩn Trên Máy

- **Kho Lưu Trữ Chính (Master Cloud Storage)**: `G:\My Drive\AI_Full_Studio`. Các đường dẫn `Z:` dưới đây thuộc cấu hình máy dựng cũ.
  - Kho Skills: `Z:\Drive của tôi\AI_Full_Studio\01_Skills`
  - Kho Kiến thức & Tài nguyên âm thanh chuẩn (`3 BGM C-Major` + `10 Studio SFX`):
    `Z:\Drive của tôi\AI_Full_Studio\02_Kien_Thuc_Va_Quy_Chuan\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx`
  - Kho `18` Họ Font Tiếng Việt TVC (`39` `.ttf`) & Chữ Gradient ưu tiên số 1:
    `d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi` (đồng bộ tại `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\04_Font Chữ TVC & Chữ Gradient`)
  - Kho mở rộng `1.340` BGM 12 thể loại & `1.043` SFX phẳng:
    `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)` và `02_Hiệu Ứng Âm Thanh (SFX)`
  - Kho `229` Hiệu ứng Chữ & Chuyển cảnh Final Cut Pro / Apple Liquid Glass (khi xuất đoạn Intro/Overlay bằng HyperFrames):
    `d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fcp_hyperframes_pack`
  - Hồ sơ Dự án (kịch bản, transcript, script dựng, báo cáo QC): `Z:\Drive của tôi\AI_Full_Studio\03_Du_An\<slug>`
  - **Thư mục Xuất Video Final Hằng Thu Pharma (`HTPM`)**: **`Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\`** (đồng bộ bản sao tại `D:\XUẤT CAPCUT\hằng thu pharma\` và `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\`), **bắt buộc đặt tên theo chuẩn `<YYMMDD> HTPM <tên tiếng Việt có dấu> final.mp4`** (ví dụ: `261119 HTPM 5 sản phẩm tuổi 25 final.mp4`).
- **Thư mục Render Trung Gian Tốc Độ Cao (Local Scratch)**: `C:\AI\full studio\output\<slug>` (giữ file trung gian `_mc_p1.mp4`, `_v3_video_only.mp4` cục bộ khi render theo frame).
- **Python Venv Có Đủ Thư Viện (`PIL`, `numpy`, `onnxruntime`, `faster_whisper`)**:
  `d:\AI\full studio\voice-studio\.venv\Scripts\python.exe`
- **Dự án CapCut Desktop**: `C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft`

---

## 2. Quy Trình 7 Bước Sản Xuất Talking Head V3 · V6

### Bước 1: Kiểm Tra Footage A-Roll, Phiên Âm `--cpu` & Hiệu Đính 100% Chính Tả
1. Trích xuất lưới khung hình `raw_sheet.jpg` và phóng cận vùng ngực/bàn (`box_closeup.jpg`) để đo chính xác toạ độ `y` của **cằm người nói**, **mép bàn** và **vùng hộp sản phẩm thật** (trên bàn hoặc cầm trên tay).
2. Chạy nhận dạng mốc từng chữ bằng `faster-whisper` (**bắt buộc truyền `--cpu`** trên máy thiếu `cudnn_ops_infer64_8.dll`):
   ```powershell
   & "d:\AI\full studio\voice-studio\.venv\Scripts\python.exe" "d:\AI\full studio\phong-cach\talking-head\tools\transcribe.py" "<main_cut.mp4>" "<main_cut.json>" --lang vi --cpu --prompt "<tên thương hiệu, hoạt chất>"
   ```
3. **[BẮT BUỘC]** Đọc soát toàn bộ `segments` & `words` trong `main_cut.json`, sửa sạch 100% lỗi dấu tiếng Việt, tên sản phẩm (ví dụ gộp `"LT"` + `"và lớn"` → `"LT Plus"`) và thuật ngữ y khoa trước khi dựng (`main_cut_clean.json`).

### Bước 2: Tách Nền Người Nói RVM Song Song 2 Nửa (`main_cut_matte.mp4`)
- Chia đôi `main_cut.mp4` thành 2 nửa (`_mc_p1.mp4`, `_mc_p2.mp4`) và chạy song song 2 tiến trình `matte.py` (`rvm_mobilenetv3_fp32.onnx`), sau đó nối `ffmpeg -f concat` thành `main_cut_matte.mp4`. Kiểm tra `ffprobe -count_frames` đảm bảo đủ tổng số khung hình.

### Bước 3: Sinh Ảnh Tham Chiếu (Dự Phòng 4 Tầng) & Tạo Video AI Google Flow Có Tham Chiếu Bắt Buộc
1. **Quy tắc Mặc Định Bắt Buộc: Mọi Video AI Phải Gửi Kèm Ảnh Tham Chiếu (`Reference-First Video`)**:
   - **Tuyệt đối không tạo Video AI chay (Text-to-Video không tham chiếu)**. Mọi clip B-Roll AI đều phải đi qua 2 bước:
     - **Bước 3A — Sinh Ảnh Tham Chiếu Khung Đầu (`Reference Image`) với Chuỗi Dự Phòng 4 Tầng Tự Động (`ChatGPT → Gemini → Flow → Muse`)**:
       1. `chatgpt::chatgpt-image` (ChatGPT — ưu tiên 1, có thể chạy song song khi Flow đang render video).
       2. `gemini::gemini-image` / `flow::flow-nano-banana-2-1` (Gemini — dự phòng 2).
       3. `flow::flow-nano-banana-pro` (Google Flow — dự phòng 3).
       4. `muse::muse-image` (Muse — dự phòng 4).
     - **Bước 3B — Sinh Video AI trên Google Flow (`flow::flow-omni-1.2-flash`) Ở Chế Độ "Thành Phần" (`videoMode: "reference"`) & Cân Chỉnh Đúng Giây Tiết Kiệm Điểm**:
       Đặt tiêu đề node ảnh ngắn gọn (`<= 20` ký tự ASCII, ví dụ `ref_aa01`), nối trực tiếp node ảnh vào node video (`@[node:<ref_img_id>]`, **bắt buộc `videoMode: "reference"` = chế độ `Thành phần` / `Ingredients`, không dùng `frames` Bắt đầu/Kết thúc!**) và **tính toán `seconds` (`3s`, `4s`, `5s`...) sát đúng thời lượng hiển thị của từng footage (`calc_optimal_flow_seconds`) để không tốn thừa điểm Flow**. Chỉ dự phòng sang `muse::muse-video` kèm `referenceNodeIds` khi Flow ngừng phản hồi. Sử dụng helper chuẩn `d:\AI\full studio\edit\canvas-tools\ai_ref_video.py`.
2. **Quy tắc an toàn Y khoa & Kiểm duyệt nền tảng (`knowledge/10`)**:
   - Tuyệt đối không đưa máu, cơ thể thật, trẻ em hoặc từ nhạy cảm vào prompt ảnh/video.
   - Với **cảnh B-Roll có hộp sản phẩm tiếng Việt**, dựng clip Showcase chuyển động trực tiếp từ **bộ ảnh chụp sản phẩm thật chất lượng cao tách nền bằng `IS-Net 1024px` (`cutout_product_png.py`)** để chữ tiếng Việt trên bao bì sắc nét 100%, không bị AI làm biến dạng chữ và không bị lem góc hộp trắng.
3. **Chống trùng tên file khi xuất từ Infinity Studio Canvas (`127.0.0.1:17371`)**:
   - Trước khi kích hoạt node `export:folder` (`exportRequest` mới), **bắt buộc đổi `title` của từng node ảnh/video đầu ra thành mã duy nhất** (`OUT_<slug>_v01`...) và đưa viewport về gần node `export:folder`, sau đó tra cứu theo `nodeId` trong `d:\AI\full studio\canvas\exports\manifest.json`.
   - Cắt bỏ `0.20s – 0.25s` đầu của mọi clip Flow (tránh khung tĩnh đầu tiên), áp LUT `10_AI_Clip_Harmonizer_Natural.cube` và chuẩn hoá CFR `30fps`.
   - Xuất bảng kiểm `brolls_qc.jpg` để xem bằng mắt 100% tài nguyên trước khi ghép.
4. **Quy tắc Typography (`Asap Condensed`) & SFX Sạch**:
   - Ưu tiên họ font **`Asap Condensed`** (`AsapCondensed-Bold.ttf` cho phụ đề Sentence-Case *"Viết hoa đầu câu"* viền mảnh `2px`; `AsapCondensed-ExtraBold.ttf` / `Black.ttf` cho tiêu đề thẻ Liquid-Glass Bento & hiệu ứng FCP/AE).
   - Tuyệt đối không sử dụng các SFX ồn/gắt (đã xoá vĩnh viễn `Whoosh - Lướt chuyển cảnh cơ bản.mp3`); chỉ chọn SFX êm nhẹ (`-19dB` đến `-21dB`).

### Bước 4: Đồ Họa Và Chuyển Động V6
1. **Nền Phòng Thật + Làm Tối Mượt Khi Lên Animation (`ANIM_DIM_WINDOWS`)**:
   - Không thay phông giả cứng suốt video. Khi người nói dẫn chuyện bình thường (`dim == 0`), giữ **100% nền phòng thật tự nhiên**.
   - Khi xuất hiện chữ lớn sau đầu, Hook, vòng xoay hoặc Split B-Roll, tăng `dim_room_alpha` trên lớp nền phòng từ `0.0` đến `0.42` rồi giảm về `0.0` bằng `smoothstep`. Lớp người nói và mask hộp thật đặt phía trên lớp dim để giữ sáng và nét.
2. **4 Cảnh Split B-Roll 2 Lớp Riêng Biệt — `0%` Méo Tỷ Lệ (`fit_cover`)**:
   - Hai thẻ V6 tách lớp riêng, trên là video Google Flow và dưới là Showcase từ ảnh thật `SP_*_CUTOUT.png`. Dùng `fit-cover` với một hệ số phóng đồng nhất, canh vào tâm chủ thể trong phạm vi crop. Sân khấu dùng hai khung `766×465`, xoay `±1°`, trượt ngang tối đa `18px` và fade tối đa `13` frame. Phụ đề nằm ở dải riêng bên dưới khi dùng tọa độ mặc định.
   - *Lưu ý đạo diễn*: Khi người nói đang **cầm hộp sản phẩm trên tay và chỉ trực tiếp vào hộp** (*"1 hộp như thế này..."*), giữ cảnh người nói cầm hộp trên màn hình (kèm `Orbital Rings` + `Từ khoá lớn` sau lưng), không đè B-Roll che mất hành động thật.
3. **Bố Cục Chữ Face-Safe, Box-Safe & An Toàn Kiểm Duyệt**:
   - **Từ khóa lớn sau đầu** giữ một dòng và thu cỡ theo bề ngang, căn giữa quanh `Y = 445px`. Đồng bộ vệt sáng chéo và vòng xoay với `start_frame`/`end_frame` của cue `keywords`.
   - **Chữ Hook 3 kiểu font (`0.05 – 4.5s`)**: Dùng từ ngữ y khoa trung tính, không che mặt, đi kèm **3 thẻ Icon Tile viền sáng chạy vòng (`EdgeSweep`)** xếp vòng cung trên đỉnh đầu (`cx = 215, 540, 865`, bật lệch nhau `0.18s` + nổ vòng tròn `Burst`).
   - **Phụ đề từng từ** dùng Asap Condensed và bóng đổ hai lớp cùng màu chữ. Đo dải áo tối giữa cằm và hộp sản phẩm khi chọn tọa độ. Toàn bộ chữ và glow nằm trong `X = 54..884px`, `Y = 248..1545px`. Chạy `--check-subtitles` với bbox sau hiệu ứng ở hệ tọa độ canvas `1080×1920`.
   - **Thẻ `Icon Tile` & Lớp phủ thân bài**: Luôn tuân thủ **Vùng Trắng An Toàn TikTok × Reels (`Y = 250..1545px`, nửa trên `X = 54..1024px`, nửa dưới `Y >= 860px` giới hạn `X = 54..884px`)**. Nếu hộp sản phẩm đặt bên phải bàn, đặt `Icon Tile` ở góc trái dưới (`cx = 215, cy = 1410`, mép dưới `<= 1545px`) để vừa không đè sản phẩm thật vừa không chạm vùng đen đáy.

### Bước 5: Kiểm Định Khung Thử Trước Render
- Chạy `--self-test` và kiểm `words.json` bằng CLI. Kiểm hình đại diện ở đầu, giữa, cuối từng cảnh Split và tại mốc dim nền. Soát dấu tiếng Việt, alpha của người nói, mép nhãn sản phẩm, vị trí phụ đề so với cằm và hộp. Với dự án dùng renderer LT PLUS cũ, chế độ `--test` nằm tại `.agents/skills/talking-head-v3/scripts/render_talking_head_v3_template.py`.

### Bước 6: Phối Âm BGM 2 Nửa C-Major + EQ Voice Pocket + Sidechain Ducking (`-14.0 LUFS`)
- **Nhạc nền 2 nửa cảm xúc**: Nửa đầu (nêu vấn đề/triệu chứng) dùng `bgm_warm_fretless.mp3`, crossfade `1.6s` sang `bgm_bright_riley.mp3` ở nửa sau (giới thiệu giải pháp sản phẩm & CTA).
- **EQ Voice Pocket và Sidechain Ducking** áp `highpass=f=75,equalizer=f=1850:t=q:w=1.4:g=-3.5` lên BGM đã crossfade. `sidechaincompress` nhận tín hiệu giọng đọc với attack `35 ms` và release `380 ms`. Nếu dùng Micro-SFX cho icon hoặc từ khóa, canh cue `30–120 ms` ở frame chạm đích và giữ thấp hơn giọng đọc `9–14 dB`.
- **Chuẩn hoá 2 lượt (`2-pass loudnorm`)**: Đưa bản trộn cuối cùng về đúng **`-14.0 LUFS`** (`True Peak <= -0.95 dBTP`).

### Bước 7: Xuất Bản Final Cục Bộ & Lưu Hồ Sơ Dự Án Lên Google Drive (Không Xuất Nháp CapCut)
1. Xuất **một bản Final cục bộ** tại `D:\XUẤT CAPCUT\<TEN_VIDEO>_FINAL.mp4` và đồng bộ vào `G:\My Drive\AI_Full_Studio\04_Videos_Final`. Tạo nháp CapCut khi người dùng yêu cầu.
2. Kiểm tra lại bằng `ffprobe -count_frames`, giải mã thử `ffmpeg -v error ... -f null -` và chụp Contact Sheet 20 khung `v3_sheet.jpg`.
3. Lưu kịch bản (`job.json`), `plan.json`, báo cáo QC (`report.md`), lưới `v3_sheet.jpg` và mã dựng vào `G:\My Drive\AI_Full_Studio\03_Du_An\<slug>`.
