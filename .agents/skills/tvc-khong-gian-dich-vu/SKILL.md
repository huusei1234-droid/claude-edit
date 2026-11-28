---
name: tvc-khong-gian-dich-vu
description: >-
  Quy chuẩn đạo diễn và dựng TVC Giới Thiệu Không Gian & Dịch Vụ Cao Cấp (Salon,
  Spa, Thẩm mỹ viện, Phòng khám, Showroom, Nhà hàng, Resort — phát màn hình TV
  cửa hàng, YouTube & Fanpage 1920x1080 @ 30fps) phối hợp CapCut Color/Beauty
  Round-Trip × HyperFrames Motion Graphics. Đúc kết thực chiến từ TVC Win Hair
  Salon CS2 (V11 Master): trích xuất 100% màu chỉnh & làm mịn da từ bản xuất
  CapCut (Direct Crop + Poly3 33x33x33 3D-LUT sau xoay 90°), khử sạch 100% nháy
  frame biên chuyển cảnh, bảng tiêu đề trượt ngược Đen–Vàng kiểu Final Cut Pro,
  thẻ tên đôi KOL nổi tiếng, chữ vàng kim không cắt dấu tiếng Việt, phụ đề 43px
  đọc rõ trên TV từ xa, và bộ 23 màu âm Whoosh/Deep Woosh/Swish/Wish xoay vòng.
---

# TVC Không Gian & Dịch Vụ Cao Cấp — Quy Chuẩn CapCut Color Round-Trip × HyperFrames

Skill này đóng gói trọn vẹn quy trình sản xuất **TVC Giới Thiệu Không Gian & Trải Nghiệm Dịch Vụ dài (`2 – 6 phút`, `1920×1080 @ 30fps`, chuẩn màu `SDR bt709`)** phục vụ trình chiếu màn hình TV lớn tại cơ sở kinh doanh, YouTube và Fanpage thương hiệu (Salon tóc nam/nữ, Spa dưỡng sinh, Phòng khám, Thẩm mỹ viện, Showroom, Khách sạn/Nhà hàng).

Đọc kết hợp cùng [`hyperframes`](../hyperframes/SKILL.md) và [`capcut-pro-editor`](../capcut-pro-editor/SKILL.md).

---

## 1. Khi Nào Kích Hoạt & Tư Duy Phối Hợp CapCut × HyperFrames

Kích hoạt skill này khi người dùng yêu cầu:
- Dựng hoặc nâng cấp **TVC giới thiệu cơ sở / chi nhánh mới / quy trình dịch vụ / bảng giá combo** (như chuẩn **Win Hair Salon CS2**).
- **Lấy dự án CapCut đã cắt sườn, chỉnh màu & làm đẹp da của Editor đưa lên HyperFrames** để thay toàn bộ hiệu ứng chữ, bảng tiêu đề, slide đa khung hình và âm thanh SFX sang phong cách **After Effects × Final Cut Pro** sang trọng.

### Nguyên tắc "Giữ Trọn Tinh Hoa CapCut — Nâng Tầm Đồ Họa HyperFrames"
1. **Từ CapCut giữ nguyên `100%`**:
   - Nhịp cắt câu chuyện, các vị trí Editor đã đích thân chọn/đổi source và trim timeline.
   - Màu chỉnh (`HSL 6 kênh`, `Curves`, `LUT`, `Smart Color`) và hiệu ứng làm đẹp da (`Làm mịn`, `Làm trắng`, `Làn da lấp lánh`, `Clear`).
   - Bản thu Master **Voiceover + Đồng thanh hô khẩu hiệu + Phỏng vấn khách thật + Nhạc nền sạch 1 lớp duy nhất** (tuyệt đối không đè chồng thêm bản nhạc thứ 2 cùng bài gây rối tai).
2. **Trên HyperFrames nâng cấp `100%`**:
   - Hệ thống **Slide Đa Khung Hình (`9:16` dọc + `16:9` ngang trên sân khấu tối ấm điện ảnh)** trình diễn từng dịch vụ và gói ưu đãi.
   - **Bảng Tiêu Đề Góc Trái Trên kiểu Final Cut Pro** (`Nền đen quét từ phải qua ←` × `Dải ánh vàng kim chạy ngược lại →` × `Chữ trượt mở từ mặt nạ`).
   - **Thẻ Tên Đôi KOL / Khách Mời Nổi Tiếng** vát nghiêng kim loại vàng.
   - **Phụ Đề TV Cỡ Lớn `43px` IN HOA** không khung viền, nhấn từ khóa vàng Champagne dễ đọc từ khoảng cách `3–5m` tại cửa hàng.
   - **Bộ `23` màu âm `Whoosh / Deep Woosh / Swish / Wish` xoay vòng** tinh tế (loại bỏ hoàn toàn tiếng `Pop` hoạt hình rẻ tiền).

---

## 2. Kiến Trúc Phân Tầng 7 Lớp Chuẩn Không Lỗi Render (`index.html`)

Mọi dự án TVC dài trên HyperFrames phải phân tách rõ 7 lớp độc lập để dễ kiểm soát và không chạm ngưỡng giới hạn bộ nhớ GPU của trình duyệt:

| Tầng | ID / Composition | Vai trò & Quy tắc bắt buộc |
| :--- | :--- | :--- |
| **Track 0** | `#base-video` (`clean_base_1080p.mp4`) | Video nền liền mạch đúng chính xác tổng số frame (`duration * 30`, chuẩn `SDR bt709`). Khi bảng Combo phủ nửa phải (như `Slide 09`), dùng GSAP dịch mượt `#base-video` sang trái (`x: 0 -> -430`) để **gương mặt kỹ thuật viên & khách hàng không bao giờ bị bảng đè che khuất**. |
| **Track 1** | `slide-01..10.html` | Các Slide trình diễn dịch vụ có nền tối đặc `100%` (`.wh-bg-obsidian` / `.wh-bg-walnut` / `.wh-bg-crimson`). **CẤM TUYỆT ĐỐI animate `opacity` của `.wh-stage` về `0` ở giữa slide** (xem Quy tắc Chống Lộ Frame mục 3). |
| **Track 2** | `reviews-broll.html` | Các khung PiP bo góc mềm (`border-radius: 20px`) và cảnh chèn thực tế khi khách feedback. **Cấm chèn B-roll khác người khi khách hàng đang trực tiếp lên hình nói**. |
| **Track 3** | `overlays-hud.html` | Cụm Intro mở màn (`data-start="0"` mượt ngay từ frame `0`), Thẻ tên đôi KOL, `10` Bảng tiêu đề khu vực kiểu Final Cut Pro, và Cụm chữ End-Card. **Bỏ logo góc phải trên cố định** để khung hình rộng thoáng như phim thương mại. |
| **Track 4** | `tvc-transitions.html` | Chớp sáng chuyển cảnh ấm `0.30s` (`tr-veil` + `tr-streak`) đặt tại các điểm cắt slide. **Tuyệt đối không đặt đè lên điểm cắt vào cảnh 3D Logo cuối phim**. |
| **Track 5** | `captions-tv.html` | Phụ đề truyền hình `43px` (`Be Vietnam Pro 700` IN HOA) + lớp phủ tối đáy màn hình (`tv-scrim`) giữ thêm `0.50s` và `fade-out` mượt `0.65s` sau khi dứt thoại để không bị chớp sáng gắt. |
| **Track 6+** | `clean_vo_bgm.mp3` + `4` làn SFX | `1` file Master VO+BGM sạch duy nhất (`data-volume="1.06"`) + các làn SFX tự động chia rãnh cách nhau `>= 20ms`, âm lượng tổng bài đạt chuẩn **`-14.0 dB` (`True Peak <= -1.0 dB`)**. |

---

## 3. Ba Quy Tắc Sống Còn Chống Lỗi Frame, Tràn Biển Hiệu & Nháy Logo

1. **Cấm Mờ Nền Slide Giữa Chừng — Tách Độc Lập Theo Chỉ Số Frame (`Bài học 01:03`)**:
   - Khi Editor muốn mở lộ một cảnh trên `Track 0` ở giữa hai cụm slide (ví dụ: hết cảnh Ghế Massage `59.67..62.77s` → mở lộ biển `PHÒNG VIP` `62.77..64.27s` → vào cảnh Mời Nước VIP `64.27..70.10s`), **tuyệt đối không gộp chung 1 composition rồi giảm `opacity` của `#stage` xuống `0`** — trong `6 frames` mờ bán trong suốt sẽ làm lộ lớp cắt ghép thô của CapCut nằm dưới `Track 0`!
   - **Giải pháp bắt buộc**: Tách thành **2 composition độc lập** (`slide-02c-a.html` từ `f_time(1790)` dài `f_time(93)` và `slide-02c-b.html` từ `f_time(1928)` dài `f_time(175)`), mỗi bên giữ nền đặc `opacity: 1` xuyên suốt từ frame đầu tiên tới frame cuối cùng.
2. **Xử Lý Chuẩn Trích Xuất Màu CapCut & Cắt Sạch Frame Biên (`CapCut Color Round-Trip`)**:
   - Đọc chi tiết thuật toán tại [`references/capcut-color-roundtrip-and-boundary-sanitizer.md`](./references/capcut-color-roundtrip-and-boundary-sanitizer.md):
     - Luôn lấy kích thước thực **sau xoay `90°`** (`cv2.VideoCapture` `rw, rh`) vì CapCut lưu metadata `1920×1080` cho cả clip dọc quay máy Sony/iPhone.
     - Chỉ dùng **`DIRECT_CROP`** từ video xuất CapCut khi chiều rộng hiển thị thực `vis_w == box_w` (nếu `vis_w < box_w` trên clip dọc như `C0057.MP4`, crop rộng ra sẽ làm lọt chữ biển hiệu `Track 0` vào trong thẻ!). Với mọi clip dọc `9:16`, dùng **`Poly3 33×33×33 3D-LUT`** khớp trên vùng không bị che khuất.
     - Chạy bộ lọc **`Boundary Frame Sanitizer`** quét toàn bộ clip trong `assets/slides/`: loại bỏ ngay `frame 0` hoặc frame cuối bị dính cảnh kế bên khi cắt bằng `ffmpeg -ss` (`max_frame_diff < 18.0` trên toàn bộ 100% clip).
3. **Giữ Nguyên Vẹn Độ Sắc Nét Cảnh Mở 3D Logo Cuối Phim (`End-Card Cleanliness`)**:
   - Khi `Track 0` cuối phim đã là video 3D Logo thương hiệu có sẵn hạt bụi vàng kim (`Logo_revealing_with_gold_dust`), **cấm phủ đè thêm video `golden_dust_16x9.mp4` (`#end-bokeh`)** và **cấm đặt `tvc-transitions` cắt ngang lúc mở Logo** (gây nháy sáng trễ 6 frame và làm đục bề mặt kim loại của Logo).
   - Mount `#end-lockup` ngay đúng frame cắt sang Logo, đặt `opacity: 0` mặc định cho `#end-top` / `#end-bot`, chờ biểu tượng 3D hiện rõ mới trượt nhẹ dòng Slogan & Địa chỉ/Hotline lên. Nếu dùng chung 1 ảnh logo `.png` ở 2 beat khác nhau trong cùng 1 composition, tạo bản sao tên tệp riêng (`logo_b3.png`) để triệt tiêu cảnh báo `duplicate_media_discovery_risk`.

---

## 4. Quy Chuẩn Thiết Kế Chữ Điện Ảnh (Không Cắt Dấu, Không "Màn Hình Code AI")

1. **Chữ Tiêu Đề Vàng Ánh Kim Không Bao Giờ Cắt Dấu Tiếng Việt (`.wh-bullion-face`)**:
   - Khi kết hợp `-webkit-background-clip: text; color: transparent` và `filter: drop-shadow(...)` trên font có chân sang trọng (`Playfair Display 800` `54–56px` hoặc `Cormorant Garamond Bold Italic` `66px`), dấu mũ kép tiếng Việt (`Ể`, `Ẩ`, `Ỗ`, `Ắ`, `Ộ`, `Ứ`) rất dễ bị xén đỉnh móc.
   - **Bắt buộc bù vùng đệm âm** trên lớp mặt chữ:
     ```css
     .wh-bullion-face {
       display: inline-block;
       padding: 48px 22px 28px 22px;
       margin: -44px -22px -24px -22px;
       line-height: 1.30;
     }
     ```
2. **Loại Bỏ Hoàn Toàn Cảm Giác "Giao Diện Code / AI UI"**:
   - **Cấm**: Nhãn tiếng Anh cứng nhắc (`01 · SERVICE`, `02 · RITUAL`, `BESPOKE`), các hộp chữ nhật viền mảnh xếp hàng ở đáy như dashboard phần mềm, chữ có viền `text-stroke`, hoặc hình đồ uống AI trông giả.
   - **Thay bằng**:
     - `100%` tiếng Việt giàu cảm xúc nghỉ dưỡng (*"Chăm Chút Những Điều Nhỏ Nhất"*, *"Chu Đáo Như Một Kỳ Nghỉ Dưỡng"*).
     - Dải điểm nhấn đáy không khung hộp, ngăn cách bằng hoa thị vàng `✦` (`Be Vietnam Pro 700`, `22px`).
     - Thực đơn đồ uống mời miễn phí dùng thẻ Typography thuần Việt chuyển sắc nâu trầm viền trái vàng Champagne (`Oswald 700` `46px` + mô tả `22px`).
3. **Bảng Tiêu Đề Góc Trái Trên Trượt Ngược Kiểu Final Cut Pro (`FCP Counter-Slide Banner`)**:
   - Kích thước lớn rõ nét (`max-width: 1080px`, tiêu đề chính `44px Oswald Bold`, phụ đề `23px`), biên phải tan mờ mềm mại vào cảnh quay.
   - **Chuyển động 3 nhịp đối hướng bằng thuần GPU `transform` + `overflow: hidden`** (không dùng `clip-path` hay `filter: blur` để tránh lỗi đen hình `composition_heavy_overlay_count_high` khi nhiều phần tử):
     1. **Nền đen mờ biên (`.wh-fcp-bg`)**: Quét nhanh từ phải sang trái (`xPercent: 103 -> 0`, `0.42s`, `expo.out`).
     2. **Dải ánh vàng kim (`.wh-fcp-gold-run`) + Thanh dọc & Đường kẻ vàng**: Chạy ngược chiều từ trái sang phải (`xPercent: -115 -> 245`, `0.56s`, `power3.inOut` + `scaleX: 0 -> 1`).
     3. **3 dòng chữ nằm trong mặt nạ `.wh-fcp-mask` riêng**: Trượt sắc nét ra khỏi mép mặt nạ (`xPercent: -106 -> 0` cho Kicker; `yPercent: 120 -> 0` lệch nhau `0.08s` cho Tiêu đề & Mô tả), và thu gọn ngược vào mặt nạ khi kết thúc.
   - Mẫu code chuẩn đặt tại [`templates/fcp-counter-slide-banner-and-kol-tags.html`](./templates/fcp-counter-slide-banner-and-kol-tags.html).

---

## 5. Đa Dạng Hóa Chuyển Động Slide & Phối Âm `23` Màu `Whoosh / Swish / Wish`

### A. 7 Bố Cục Slide Luân Phiên Chống Nhàm Chán Trong TVC Dài
1. **3 Cột Đứng Trượt Ngược Chiều (`Down – Up – Down`)**: Dành cho 3 giá trị cốt lõi mở màn (`Slide 01`).
2. **1 Khung Lớn Ngang (`Hero`) + 2 Cột Đứng Lệch Nhịp**: Dành cho khu Gội đầu & Phòng VIP (`Slide 02`, `Slide 02B`).
3. **Song Đôi Ngang Cân Xứng (`842×664` × 2)**: Dành cho Ghế Massage, Làm Móng & Mặt tiền chính diện 2 Cơ sở (`Slide 02C-A`, `Slide 08`, `Slide 10 Beat 4` — bắt buộc dùng góc quay trực diện thẳng mặt tiền bảng hiệu).
4. **Xòe Quạt 5 Lá Bài (`5-Card Poker Fan`)**: 5 thẻ dọc xoay nghiêng `-9° → +9°` chia bài lần lượt kèm tiếng lướt thẻ tăng dần cao độ (`Slide 03`).
5. **3 Lát Cắt Chéo Song Song (`Diagonal Blades`)**: Dành cho Cạo mặt / Tạo kiểu sắc bén (`Slide 05`).
6. **Lật Pha 2 Hồi & Đường Ray Trượt Ngang (`2-Act Flip & Horizontal Rail`)**: Từ Xông hơi chuyển mượt sang 3 thẻ Massage Tay – Chân – Cổ Vai Gáy lướt ngang (`Slide 06`, `Slide 07`).
7. **Dịch Máy Quay Trái + Lưới 6 Ô Combo + Khối Giá Vàng Khổng Lồ (`176px`)**: Dành cho Tổng kết liệu trình 6 bước (`Slide 09`) và Khung giờ vàng `-20%` / `129K` / `79K` (`Slide 10`).

### B. Quy Chuẩn Âm Thanh & SFX Tinh Tế (Chuẩn Broadcast `-14.0 dB`)
- **Nhạc nền & Thoại (`clean_vo_bgm.mp3`)**: Mã hóa từ file WAV sạch qua chuỗi lọc dấu phẩy động `aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.93,highpass=f=55,equalizer=f=2800:t=q:w=1.2:g=1.8,equalizer=f=185:t=q:w=1.0,alimiter=limit=0.95` để **0% clipping bộ lọc** và **0% đè chồng 2 lớp nhạc nền**.
- **23 Màu Âm Gió Lướt Xoay Vòng (`vol = 0.15 – 0.22`)**:
  - *Nhóm trầm dày (vào/ra Slide lớn)*: `w_deep_classic`, `w_deep_warm`, `w_deep_punch`, `w_wind_thick`, `cinematic_whoosh_16`, `whoosh_hit_low2`, `deep_title_wind`, `w_swoosh_long`.
  - *Nhóm lướt mượt trung tính (thẻ bay ngang/dọc)*: `w_tvc_smooth`, `w_swipe_air`, `w_move_soft`, `w_swoosh_4`, `w_short_2`, `deep_swish_tight`.
  - *Nhóm thanh mảnh / ánh sáng (bảng FCP, thẻ KOL, chia bài)*: `w_fuwa_wish`, `w_shun_magic`, `w_swish_crisp`, `w_swish_velvet`, `w_wind_airy`, `w_tvc_pip`, `electro_card_1..5`, `blade_shine`, `tech_particle_pass`.

---

## 6. Danh Sách Kiểm Định Bắt Buộc Trước Khi Bàn Giao (`Final QC Checklist`)

1. **Chạy `npx.cmd hyperframes lint --json`**: Đảm bảo `errorCount == 0`, `0` `duplicate_media_discovery_risk`, `0` `composition_heavy_overlay_count_high`.
2. **Chụp `npx.cmd hyperframes snapshot`** tại các điểm nhạy cảm và đọc kiểm tra bằng mắt:
   - Tiêu đề chữ hoa tiếng Việt có dấu chồng (`Ể`, `Ẩ`, `Ỗ`) không bị xén đỉnh.
   - Mọi điểm chuyển giữa Slide và `Track 0` cắt dứt khoát đúng 1 frame đơn lẻ (`0%` bóng mờ chồng lớp).
   - Bảng tiêu đề Final Cut Pro quét Đen – Vàng mượt và không xén chữ khi đứng yên.
   - Đoạn mở Logo cuối phim (`jumps > 6.5 == []`) không bị nháy hạt bokeh hay vệt ngang.
3. **Xuất GPU chất lượng cao & Đồng bộ 3 đích chuẩn Quy tắc Hệ thống**:
   - Lệnh xuất: `npx.cmd hyperframes render --gpu --quality looks --browser-timeout 120` (tuyệt đối không `taskkill` CapCut/Premiere/Photoshop/Brave đang mở của người dùng).
   - Đặt tên chuẩn `<YYMMDD> <Thương hiệu> <tên tiếng Việt có dấu> final.mp4`, đồng bộ sang thư mục Google Drive riêng của khách hàng, `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\`, `D:\XUẤT CAPCUT\`, lưu mã nguồn + báo cáo QC vào `03_Du_An\`, và gọi MCP `show_file_location_card` hiển thị nút **📂 Mở vị trí tệp**.
