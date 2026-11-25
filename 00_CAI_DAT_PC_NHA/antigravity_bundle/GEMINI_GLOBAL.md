# Hồ Sơ & Chuẩn Mực Edit CapCut Cá Nhân (CapCut Pro Editor DNA)

Tài liệu này lưu trữ **toàn bộ phong cách dựng phim (Editing DNA)** đã được đúc kết từ các dự án thực tế của Editor cùng **Bộ Quy Tắc Nâng Cấp (Pro Upgrade)**. Mọi tác vụ phân tích, tạo mới hoặc chỉnh sửa dự án CapCut (`draft_content.json`) đều phải tuân thủ nghiêm ngặt bộ quy tắc này.

---

## 1. Kho Lưu Trữ Chính Trên Google Drive & Đường Dẫn Tài Nguyên
- **KHO LƯU TRỮ CHÍNH TOÀN HỆ THỐNG (Master Cloud Storage)**: `Z:\Drive của tôi\AI_Full_Studio`
  - **Kho 25 Skills trung tâm**: `Z:\Drive của tôi\AI_Full_Studio\01_Skills` (bao gồm **`talking-head-v3`**, **`kobe-motion-talking-head`**, `capcut-pro-editor`, `tvc-qc-san-pham`, bộ 10 skills `hyperframes` & 13 skills `remotion`).
  - **Kho Kiến thức & Tài nguyên chuẩn**: `Z:\Drive của tôi\AI_Full_Studio\02_Kien_Thuc_Va_Quy_Chuan` (`phong-cach/`, `BO_KIEN_THUC_TVC_AI_PORTABLE/`).
  - **Kho Lưu trữ Hồ sơ Dự án (kịch bản, transcript, script dựng, báo cáo QC)**: `Z:\Drive của tôi\AI_Full_Studio\03_Du_An\<slug>`
  - **Thư mục Xuất Video Final Chính Thức**: `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final` (đồng thời có thể lưu bản sao cục bộ tại `D:\XUẤT CAPCUT`).
- **Thư mục Chạy Môi Trường & Render Trung Gian Tốc Độ Cao (Local Scratch)**: `d:\AI\full studio` (giữ `.venv`, `node_modules` và các file video trung gian nặng ở ổ D để tránh nghẽn mạng Google Drive khi render; sau khi xuất xong bắt buộc đồng bộ mã dựng, báo cáo QC sang `03_Du_An` và file MP4 Final sang `04_Videos_Final`).
- **Thư mục Dự án CapCut (Drafts)**: `C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft`
- **Kho Nhạc Nền (BGM), Sound Effects (SFX), Video Meme & Font Chữ Gradient Đã Chuẩn Hóa (`2.500+` files)**:
  - **Nhạc nền 12 thể loại (`1.340` bài)**: `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)` (`01_Truyền Cảm Hứng - Quảng Cáo TVC`, `02_Chill - Lofi`, `03_Spa - Chữa Lành`, `04_Piano - Buồn`, `05_Acoustic`, `06_Jazz - Sang Trọng`, `07_Sôi Động - EDM`, `08_Hip-Hop`, `09_Gay Cấn - Cinematic`, `10_Rock`, `11_Hài Hước - Meme`, `12_Nhạc Tình Huống Ngắn`).
  - **Hiệu ứng âm thanh SFX phẳng (`1.043` files)**: `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)` (đầy đủ `Whoosh`, `Pop`, `Ting`, `Click`, `Nổ Impact`, `Riser`, `Lấp Lánh`, `Tiếng Cười`, `Thoại Hài`, `FAPTV`...).
  - **Video Meme & Chèn Cảnh (`76` clips)**: `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\03_Video Meme & Chèn Cảnh`.
  - **Kho 18 Họ Font Tiếng Việt TVC (`39` `.ttf`) & 6 Preset Chữ Gradient**: `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\04_Font Chữ TVC & Chữ Gradient` và `d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi` (**Luôn ưu tiên thiết kế Chữ Gradient đa điểm dừng + 2 lớp tách viền + quét sáng ánh kim**).
  - **Kho `448` Hiệu Ứng 3D, After Effects Motion Graphics & Final Cut Pro Offline Cho HyperFrames (`100%` Registry) + `ae-3d-effects.jsx`**: `d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fcp_hyperframes_pack` và `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\05_Hiệu Ứng Chữ & Chuyển Cảnh Final Cut (HyperFrames)` (đầy đủ 9 nhóm: 3D Three.js / Apple Vision Orbit / Isometric Explode, WebGL/WebGPU Orbs & Particles, Giao diện 3D SaaS kiểu After Effects, Transitions Shader/Whip-Pan/Zoom, Apple Liquid Glass, Chữ Blur-Focus/Kinetic, Lower-Thirds, Callouts & Charts kèm `copy_fcp_effect.py` + thư viện AE 3D `phong-cach/saas-animation/lib/ae-3d-effects.jsx`).
  - **Kho `12` 3D LUTs Chỉnh Màu (`.cube`), `10` Video Overlays Điện Ảnh (`.mp4` Screen), `Brand Kits` & Công cụ Tách nền Sản phẩm `IS-Net`**: `d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau` (`apply_lut.py`), `video_overlays_4k`, `brand_kits` và `05_SCRIPTS_TU_DONG_HOA\cutout_product_png.py` (đồng bộ tại thư mục `06_LUTs...`, `07_Video Overlay...`, `08_Brand Kits...` trong `TLH\Edit`).
  - **Cache SFX CapCut nội bộ**: `C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music`.

---

## 2. Phong Cách Cốt Lõi (Signature Style) & Quy Tắc Nâng Cấp (Pro Upgrades)

### A. Tư Duy Tổ Chức Timeline
- **Giữ Lịch Sử Phiên Bản Trên Timeline (Multi-Version Timeline)**: Khi dựng các dự án lớn (như TVC), giữ bản nháp/bản cũ ở cụm đầu timeline và đặt bản dựng mới cách một khoảng trống ngắn để dễ đối chiếu hoặc lấy lại cụm B-roll/compound clip đã cắt.
- **Phân Tầng Track Rõ Ràng**:
  - `Track 0 (Main Video)`: Đường dây hình ảnh chính (A-roll / cảnh nền chủ đạo), luôn liền mạch, không để hở khoảng đen.
  - `Track 1 – 6 (B-Roll, PIP, Split-Screen & Overlay)`: Các lớp cảnh phụ đè lên, khung chia đôi/chia ba (collage), hiệu ứng hạt sáng (`Partículas douradas`), hoặc logo góc (`scale: 0.11`).
  - `Track Text (2 tầng)`: Tách riêng Track Tiêu đề chính (Tầng 1) và Track Mô tả phụ / Phụ đề (Tầng 2).
  - `Track Audio (4+ tầng)`:
    - Track Nhạc nền (BGM) riêng biệt.
    - 2–4 Track Voiceover xếp kiểu **bậc thang (Checkerboard / J-cut & L-cut)** để cắt sạch nhịp nghỉ thừa và gối đầu câu mượt mà.
    - Các Track SFX & ASMR thực tế.

### B. Nhịp Cắt (Pacing) & Tốc Độ (Speed)
- **3 Giây Đầu (Hook)**: Nhịp cắt nhanh (`0.6s – 1.1s/shot`), kết hợp Text Hook nổi bật + SFX mở màn (`Magic reveal`, `Riser Metallic`, `Deep woosh`).
- **Nhịp Cắt Theo Thể Loại**:
  - **Reels / Short Trend (9:16)**: Median `1.0s – 1.3s/shot` (trung bình `1.4s – 1.5s`).
  - **TVC / Vlog / Quảng cáo thương hiệu (16:9 hoặc 9:16)**: Track chính median `1.8s – 2.5s/shot`; các lớp B-roll đè lên cắt nhanh hơn với median `1.1s – 1.67s/shot`.
  - **Storytelling / Kịch tính / AI Drama**: Median `2.6s – 3.5s/shot` để giữ cảm xúc diễn xuất và thoại.
- **[NÂNG CẤP] Quy Tắc Nhịp Sóng (Wave Pacing)**: Không để quá 3 clip liên tiếp có cùng thời lượng. Phối hợp nhịp **Nhanh – Nhanh – Chậm** (ví dụ: 2 cú cắt cận chi tiết `0.9s – 1.2s` mở ra 1 cú máy rộng/beauty `2.2s – 2.8s`).
- **Xử Lý Speed**:
  - Không lạm dụng Curve Speed giật cục.
  - Ưu tiên **Constant Slow-Motion mượt (`0.8x`, `0.7x`, `0.6x`)** cho cảnh không gian sang trọng, beauty, flycam, thao tác tỉ mỉ.
  - Dùng **Fast Speed (`1.5x – 3.33x`)** cho cảnh di chuyển hoặc quá trình thao tác dài.

### C. Kỹ Thuật Đa Tầng (Multi-Layering), Masking & Keyframe
- **3 Kiểu Mask Đặc Trưng**:
  1. **Chia Khung Chéo (`Tách / Line Mask`)**: Xoay góc nghiêng `101.5° – 105.5°`, làm mờ viền `feather: 0.45 – 0.58` để ghép 2–3 cảnh song song trên màn hình mà không bị cứng đường cắt.
  2. **Lồng Cảnh Nghệ Thuật (`Cuộn phim / Mirror Mask`)**: Xoay `-34°`, `-42°` hoặc `-79°`, `feather: 0.27 – 0.42`, `height: 0.08 – 0.76`.
  3. **Khung Collage / Tách Chủ Thể (`Hình chữ nhật / Rectangle Mask` & `Bút / Contour Mask`)**: Dùng `feather: 0.14 – 0.18` kết hợp thu nhỏ `scale: 0.71 – 0.77` đặt lệch góc (`pos X: 0.24 – 0.40, pos Y: ±0.69 – 0.77`) và animation `Trượt sang trái` / `Trượt sang phải`.
- **[NÂNG CẤP] Chuyển Động Micro-Zoom (Ken Burns) & Staggered PIP**:
  - Mọi shot tĩnh hoặc dài `> 2.2s` trên Track chính cần có **Micro-Zoom nhẹ (`scale: 1.00 -> 1.06` hoặc `1.08 -> 1.00`)** bằng keyframe (`KFTypeScaleX/Y`) để khung hình luôn có sức sống.
  - Khi ghép 2–3 khung PIP/Collage cùng lúc, cho từng khung xuất hiện **lệch nhau `0.15s – 0.25s` (Staggered Entry)** kèm tiếng `Woosh vshort - chữ.mp3` hoặc `Pop`.
- **[NÂNG CẤP] Vật Lý Chuyển Động Lớp Phủ (`Overlay Motion Physics` — xem `phong-cach/kobe-ai-motion-talking-head/CHUYEN-DONG-LOP-PHU-VA-SFX.md`)**:
  - **Mở nét quang học 2 chiều (`Bidirectional Blur-Focus`)**: Nhãn chữ, thẻ UI vào bằng `blur(18px -> 0)` + `scale(0.92 -> 1.0)` (`0.26s`) và ra bằng `blur(0 -> 14px)` (`0.20s`), cấm tắt đột ngột.
  - **Trọng lượng vật lý (`Drop-Bounce + Landing Ripple`)**: Thẻ rơi nhún nhẹ `~6%` kèm vòng sóng elip tỏa dưới chân đúng frame chạm đáy; khung người nói `Circle PiP` đóng/mở bằng màn trập tròn `Iris Wipe` (`0.20s`); dùng sợi dây sáng chạy trước `0.15s` kéo Camera trượt sang ý tiếp theo.
- **Transitions (Chuyển Cảnh)**:
  - Ưu tiên **Hard Cut (cắt thẳng)** kết hợp J-cut âm thanh hoặc Mask.
  - Chỉ đặt Transition ở điểm chuyển phân đoạn lớn (`0.33s – 0.67s`): `Kéo vào ii`, `Kết hợp`, `Chói lòa 1/2`, `Mờ thu phóng hiện ra`, `Rung lắc độ sâu trường ảnh`, `Mờ`, `Ký ức gợn sóng`.

### D. Âm Thanh (Audio Mixing, J-Cut/L-Cut & SFX)
- **Tỷ Lệ Âm Lượng Chuẩn (Gain Staging)**:
  - **Voiceover (Thoại chính)**: `volume = 1.12 – 1.46` (`+1dB` đến `+3.3dB`), rõ ràng, dày và nổi lên trên hết.
  - **Nhạc nền (BGM)**: `volume = 0.26 – 0.38` (`-8.4dB` đến `-11.7dB`) khi có thoại.
  - **[NÂNG CẤP] Dynamic Ducking**: Ở các đoạn intro, outro hoặc khoảng nghỉ thoại `> 1.5s`, nâng nhẹ BGM lên `0.50 – 0.60` và hạ mượt xuống `0.28` trước khi câu thoại mới bắt đầu `0.2s`.
  - **Clip Video Gốc**: Mặc định `volume = 0.0` cho toàn bộ B-roll; **chỉ bật và boost âm thanh gốc (ASMR)** ở các cảnh trải nghiệm thực tế (tiếng nước gội đầu, bọt, cạo mặt, ráy tai, thoa gel).
- **[NÂNG CẤP] Micro-Fade Chống Click/Pop Cho Voiceover**:
  - Khi băm nhỏ file Voiceover thành hàng chục/trăm đoạn xếp so le trên nhiều track, **bắt buộc gắn `audio_fade` (`fade_in_duration: 33333`, `fade_out_duration: 66666` µs, tức 1–2 frames)** cho từng đoạn cắt để triệt tiêu hoàn toàn tiếng "bụp/tách" ở điểm cắt sóng âm.
- **Đồng Bộ `Tactile Micro-SFX` Theo Điểm Chạm Vật Lý (Chuẩn Kobe Studio)**:
  - **Ưu tiên Micro-SFX xúc giác ngắn gọn (`30–120ms`, `-9` đến `-14 dB` dưới Voice)**: `sfx_pop_clean.mp3`, `Pop - Hiện chữ nảy nhẹ gọn 02.mp3`, `sfx_click_soft.mp3`, `Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3`, `打字-102214` (gõ chữ), `The sound that deals with the Shap Schat card` (lật thẻ nhanh `1→10`), `sfx_ping_glass.mp3`; **tuyệt đối tránh tiếng nổ `Boom` rền to rẻ tiền** ở video chia sẻ chuyên môn/TVC sang trọng.
  - **Đặt mốc chính xác**: Va chạm (`Pop/Click/Tick`) đặt **`0ms` đúng frame chạm đích** & trùng từ nhấn của giọng nói (`0` SFX rơi lạc vào khoảng nghỉ im lặng); tiếng gió lướt (`Airy Whoosh`) đặt sớm **`-110ms` (`-3 frames`)**; chuỗi 3–5 thẻ liên tiếp tăng nhẹ `+1 semitone`/bậc.

### E. Typography, Thiết Kế Chữ & Vùng An Toàn Video Dọc `9:16` (TikTok × Reels Safe Zone)
- **[BẮT BUỘC 100%] Vùng Cấm Đen Cho Mọi Video Dọc `9:16` (`1080×1920` — `safe_zone_9x16.py`)**:
  - **Cấm tuyệt đối** đặt bất kỳ Text, Phụ đề, Thẻ UI, Logo, Sticker hay Lớp phủ (Overlay/PiP/Bento) nào chạm vào 5 vùng đen bị giao diện TikTok & Reels che khuất:
    1. **Trên đỉnh**: `Y = 0 → 248px` (CapCut `Y > +0.74`).
    2. **Dưới đáy**: `Y = 1548 → 1920px` (cao `372px` từ đáy; CapCut `Y < -0.61`).
    3. **Lề trái**: `X = 0 → 52px` (`X >= 54px`).
    4. **Lề phải nửa trên (`Y < 860px`)**: `X = 1026 → 1080px` (`X <= 1024px`).
    5. **Cột nút tương tác Phải-Dưới (`Y = 860 → 1548px`)**: `X = 886 → 1080px` (ở nửa dưới `Y >= 860px` / CapCut `Y <= +0.10`, mép phải của mọi chữ & lớp phủ bắt buộc `X <= 884px`: nếu căn giữa `X=540` thì rộng tối đa `<= 680px`, hoặc dịch tâm trái về `X=469px` / CapCut `X = -0.13` để dùng trọn `830px` vùng trắng `[54..884]`).
- **Bố Cục Text 2 Tầng Thương Hiệu (TVC / Giới Thiệu Không Gian)**:
  - **Tầng 1 – Tiêu Đề Chính**: IN HOA toàn bộ, màu **Vàng Gold (`RGB: [1.0, 0.831, 0.0]` / `#FFD400`)**, cỡ `12` (16:9) hoặc `14–15` (9:16), viền đen mảnh (`stroke width: 0.08`), vị trí `Y = -0.38` (9:16, dịch tâm `X = -0.13` hoặc ngắt dòng gọn `<= 680px` tránh cột nút phải) / `Y = -0.42` (16:9).
  - **Tầng 2 – Mô Tả Phụ**: Chữ thường, màu **Trắng (`[1.0, 1.0, 1.0]`)**, cỡ `9`, viền đen `0.08`, vị trí `Y = -0.52` (9:16 — tuyệt đối không hạ xuống `-0.64` vì lọt vùng đen đáy `>1548px`!) / `Y = -0.64` (16:9).
  - **[NÂNG CẤP] Staggered Text In/Out**: Tầng 2 xuất hiện trễ hơn Tầng 1 từ `0.25s – 0.5s`; luôn gắn hiệu ứng vào (`Chữ mờ dần hiện vào`, `Bụi vàng`, `Mờ`) và hiệu ứng ra (`Mờ dần` `0.4s – 0.5s`) để chữ không biến mất đột ngột.
- **Text Hook Mở Đầu (Vlog / Reels)**:
  - Dùng font `Montserrat-Bold.otf` hoặc `Oswald-Bold.ttf`, cỡ `15 – 23`, đặt ở 1/3 trên trong vùng trắng an toàn (`Y = 0.35 – 0.65`, mép trên `>= 250px`), kết hợp hiệu ứng `Máy chữ`, `Xoay lấp lánh`, `Tan chảy điện tử`.
- **Phụ Đề Thoại Liên Tục (Subtitles)**:
  - Cắt gọn từng cụm `1.5s – 2.2s` (tối đa 5–7 từ/dòng để bề ngang `<= 680px` không chạm cột nút phải `X=886px`), đặt cố định ở `Y = -0.85` (16:9) hoặc `Y = -0.48` đến `-0.54` (9:16, mép dưới `<= 1545px`).

---

## 3. Tích Hợp HyperFrames (`heygen-com/hyperframes`) – Làm Video Bằng HTML/GSAP/Shader
- **Khái niệm**: HyperFrames là framework mã nguồn mở của HeyGen cho phép viết **HTML + CSS + GSAP / Lottie / Three.js / WebGL Shaders** và render thành video MP4 chuẩn từng khung hình (deterministic frame-by-frame capture qua Headless Chrome + FFmpeg).
- **Bộ 10 Skills HyperFrames Đã Cài Đặt Sẵn**:
  1. `hyperframes`: Quy tắc cốt lõi (Contract 12 điều, cấu trúc `index.html` + `compositions/`, `class="clip"`, `data-start`, `data-duration`, `window.__timelines`).
  2. `tvc-qc-san-pham` (**"TVC QC sản phẩm"**): Bộ quy chuẩn đạo diễn & dựng TVC Quảng Cáo Sản Phẩm cao cấp trên HyperFrames (cấu trúc 6 hồi Beat-Grid `0.92s`, Diegetic UI/Typography, chữ 3D Gold Glitter `Bling!` quét sáng, chữ ký SVG Write-On, Portal Spin Transition & bố cục End-Card chuẩn nhãn hàng `UL`).
  3. `hyperframes-cli`: Sử dụng CLI (`npx hyperframes init`, `preview`, `check --json`, `snapshot --review`, `render`).
  4. `hyperframes-registry`: Kho ~450 blocks & components dựng sẵn (shader transitions, social overlays, kinetic typography, data charts, maps, 3D, camera moves).
  5. `media-use`: Xử lý media, voiceover, music, SFX, cutout, color grading (`npx hyperframes media-treatment`).
  6. `reverse-any-video`: Phân tích và dựng lại bất kỳ video mẫu nào thành project HyperFrames chỉnh sửa được.
  7. `style-sampling`: 5 phong cách video chuẩn (Collage Explainer, Finance Explainer, Animated Science Explainer, 3D Brand Explainer, 3D True Crime).
  8. `figma`, `slideshow`, `remotion-to-hyperframes`.
- **Phối Hợp HyperFrames + CapCut Pro Editor**:
  - Dùng **HyperFrames** khi cần tạo các đoạn **Motion Graphics cao cấp, Kinetic Typography, Biểu đồ động (Data Charts), Bản đồ, Intro/Outro thương hiệu, hoặc Video Explainer tự động hóa bằng code**.
  - Dùng **CapCut Pro Editor** khi dựng **TVC thực tế, Vlog, Reels, AI Drama, cắt ghép đa tầng B-roll, Masking và trộn âm thanh phức tạp**.
  - *Lưu ý môi trường*: Trước khi chạy CLI `npx hyperframes`, cần đảm bảo máy đã cài **Node.js >= 22** và **FFmpeg** trong `PATH`.

---

## 4. Tích Hợp Remotion (`remotion-dev/remotion`) – Làm Video Bằng React Components
- **Khái niệm**: Remotion là framework tạo video bằng **React + TypeScript** (`useCurrentFrame()`, `useVideoConfig()`, `interpolate()`, `spring()`, `<Sequence>`, `<AbsoluteFill>`, `<OffthreadVideo>`, `<Audio>`).
- **Bộ 13 Skills Chính Thức Từ `remotion-dev/skills` Đã Cài Đặt Sẵn**:
  1. `remotion-best-practices`: Router trung tâm điều phối toàn bộ kỹ năng Remotion (version `4.0.542`).
  2. `remotion-create`: Khởi tạo dự án mới (`npx create-video@latest`) hoặc thêm composition mới.
  3. `remotion-markup`: Quy chuẩn viết React markup, animation (`interpolate`, `spring`), tách nền (matting), transitions, shapes, 3D (`@remotion/three`).
  4. `remotion-captions`: Xử lý phụ đề TikTok/Reels theo từng từ (`@remotion/captions`, SRT, transcribe).
  5. `remotion-maps`: Bản đồ động, đường bay 3D, Mapbox/MapLibre/MapTiler, GeoJSON.
  6. `remotion-multimedia`: Cắt/ghép, lấy metadata (`duration`, `dimensions`) bằng Mediabunny / Remotion.
  7. `remotion-interactivity`: Thiết kế schema (`zod`) để chỉnh sửa trực tiếp tham số trên giao diện Remotion Studio (`npx remotion studio`).
  8. `remotion-render`: Xuất MP4, WebM, ProRes, video trong suốt (alpha channel) để đem sang đè làm Overlay trên CapCut!
  9. `remotion-studio`, `remotion-saas`, `remotion-docs`, `remotion-upgrade`, `remotion-license`.
- **Phối Hợp "Tam Giác Vũ Khí Video" (CapCut + HyperFrames + Remotion)**:
  - **CapCut Pro Editor (`capcut-pro-editor`)**: Dựng phim thực tế (TVC, Vlog, Reels, AI Drama), cắt ghép đa tầng B-roll, Masking, J-cut/L-cut Voiceover và mix SFX.
  - **HyperFrames (`hyperframes`)**: Dựng nhanh video/motion graphics bằng **HTML + CSS + GSAP / WebGL Shaders** không cần bundler.
  - **Remotion (`remotion-best-practices`)**: Dựng các hệ thống **Component React phức tạp, Video trong suốt (Transparent Overlay/Lower-Thirds xuất ProRes 4444 / WebM Alpha để thả vào CapCut), Phụ đề TikTok highlight từng chữ, Bản đồ 3D, hoặc Tự động hóa sản xuất hàng loạt video theo dữ liệu**.

---

## 5. Quy Tắc Tự Động Chọn & Phân Luồng Model Theo Độ Khó Tác Vụ (Auto-Select Model: Tốc Độ Tối Đa → Carbon / Neon → Extra `XHigh`)
Người dùng đã ủy quyền cho hệ thống **tự động chọn và chuyển đổi model linh hoạt theo từng câu hỏi** (qua công cụ `swarm(action="model", ...)` cho luồng chính kết hợp `invoke_subagent` / `swarm` cho các tác vụ con) để luôn đạt **tốc độ phản hồi nhanh nhất** ở việc thường ngày nhưng **tối đa trí tuệ** ở việc quan trọng:
- **Tầng 1 — Hỏi đáp thường / Sửa cài đặt máy / Chạy lệnh đơn giản (Ưu tiên tốc độ ra kết quả nhanh nhất)**:
  - Xử lý trực tiếp tức thì ở chế độ điều phối nhanh (**`Orchestrator (Carbon)`** `gemini-pro-orchestrator` hoặc **`Gemini 4 Carbon (Low / Medium)`** `gemini-4-carbon-low` / `gemini-4-carbon-medium`), trả lời ngắn gọn dứt điểm, không gọi subagent dư thừa.
  - Với việc quét tệp số lượng lớn, thao tác trình duyệt hoặc việc lặp lại đơn giản: gọi `invoke_subagent` với `Model: "flash_lite"` hoặc `Model: "flash"` để trả kết quả cực nhanh.
- **Tầng 2 — Tác vụ Quan trọng / Kỹ thuật & Sáng tạo chuyên sâu (Ưu tiên `Gemini 4 Carbon` & `Gemini 4 Neon`)**:
  - Khi gặp bài toán quan trọng (viết kịch bản TVC/VSL, dựng Motion Graphics/HyperFrames/Remotion, thiết kế hệ thống, gỡ lỗi phức tạp): chủ động nâng lên **`Gemini 4 Carbon (High)`** (`gemini-4-carbon-high`), **`Gemini 4 Neon (Medium / High)`** (`gemini-4-neon-medium` / `gemini-4-neon-high`) hoặc **`Orchestrator (Neon)`** (`gemini-pro-orchestrator-neon`) (hoặc `invoke_subagent` với `Model: "pro"`).
- **Tầng 3 — Nhiệm vụ Đặc biệt Quan trọng / Dự án Lớn / Cần Độ Chính Xác Tuyệt Đối (Dùng tới mức `Extra` / `XHigh` khi cần thiết)**:
  - Khi giải quyết kiến trúc lớn, chiến dịch chốt khách quan trọng hoặc lỗi hóc búa đòi hỏi suy luận sâu tối đa: chủ động kích hoạt lên mức **`Extra` (`XHigh`)** với **`Gemini 4 Neon (XHigh)`** (`gemini-4-neon-xhigh`) (kết hợp `gemini-4-hydrogen-xhigh` / `claude-opus-5-5-high` trong `swarm` nếu cần), ưu tiên độ hoàn hảo tuyệt đối.

---

*Để xem chi tiết mã JSON (`effect_id`, `resource_id`, đường dẫn cache và công cụ tự động hóa), hãy kích hoạt skill `capcut-pro-editor`, `hyperframes` hoặc `remotion-best-practices`.*
