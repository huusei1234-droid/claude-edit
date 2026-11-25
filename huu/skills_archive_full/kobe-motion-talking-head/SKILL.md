---
name: kobe-motion-talking-head
description: >-
  Bộ kỹ năng dựng Video Talking Head × Motion Graphics hiện đại (không phụ đề
  karaoke, tập trung trực quan hóa ý tưởng bằng Sân khấu Đồ họa + Khung tròn
  Circle PiP + Chữ lớn sau đầu + Đường ray dẫn chuyện) kèm Công thức Viết 10
  Kịch Bản Liên Hoàn 3-Hook (Pain / Desire / Contrarian). Gồm 2 biến thể: Dark
  Cyber 16:9-in-9:16 và Light Pastel SaaS UI 9:16.
---

# Kobe Motion × Talking Head Skill (Visual Metaphor Stage + 3-Hook Content System)

Skill này kích hoạt khi người dùng muốn làm video **chia sẻ kiến thức, bán khóa học/dịch vụ, review công nghệ/AI, tư vấn chuyên gia hoặc quảng cáo chuyển đổi** theo phong cách **Motion Graphics dẫn chuyện kết hợp người nói thu tròn (`Circle PiP`)**, hoặc khi muốn triển khai **1 phiên Super-Prompt ra trọn bộ 10 kịch bản + VSL + Landing Page**.

Đọc chi tiết thông số đo đạc gốc tại:
- Quy chuẩn hình ảnh & hiệu ứng: `d:\AI\full studio\phong-cach\kobe-ai-motion-talking-head\PHONG-CACH.md`
- **Vật lý chuyển động Lớp phủ & Nghệ thuật đi Micro-SFX (BẮT BUỘC ĐỌC TRƯỚC KHI DỰNG)**: `d:\AI\full studio\phong-cach\kobe-ai-motion-talking-head\CHUYEN-DONG-LOP-PHU-VA-SFX.md` (gồm 6 kỹ thuật: `Iris Circle Wipe` trên PiP, `Drop-Bounce + Landing Ripple Ring`, `Bidirectional Optical Blur-Focus`, `State Escalation + Gravity Particles`, `Thread-Line Camera Follow`, `Rapid Riffle 1→10` & bảng đi `Tactile Micro-SFX` `-9..-14 dB` dưới giọng đọc)
- Tư duy đạo diễn & công thức nội dung/prompt: `d:\AI\full studio\phong-cach\kobe-ai-motion-talking-head\KIEN-THUC-TRUYEN-TAI-TU-2-VIDEO.md`

---

## 1. Bốn Quy Luật Vàng Khi Dựng Theo Phong Cách Này

1. **Tuyệt đối KHÔNG bật phụ đề chạy từng từ (Zero Karaoke Subtitles)**:
   - Không làm rối màn hình bằng chữ chép lại lời nói. Thay vào đó, **mỗi ý chính (`4–8 giây`) phải được biến thành 1 cụm Đồ họa trực quan (Visual Metaphor / UI Card)** trên sân khấu.
2. **Nhịp Luân Phiên `A-Roll Toàn Khung` (`20%`) ↔ `Motion Stage + Circle PiP` (`80%`)**:
   - Mở đầu (`0–3s`), chuyển chương lớn và chốt CTA cuối bài: Hiện **A-Roll người nói lớn** kèm **Chữ/Số khổng lồ sau lưng đầu** (tách nền RVM) hoặc **Pill Sticker nghiêng `-2°` trước ngực**.
   - Phần thân giải thích: Thu người nói vào **Circle PiP** sắc nét, nhường sân khấu cho sơ đồ chuyển động mượt trên HyperFrames (`1080×1920 @ 30fps`).
3. **Chọn 1 trong 2 Biến Thể Giao Diện Theo Ngành Hàng**:
   - **Biến thể A — `Dark Cyber Letterbox (16:9 đặt giữa 9:16)`**: Sân khấu `1080×608px` (`y = 656..1264`) giữa hai dải đen `#000000`, nền lưới `#17191e`, Circle PiP `246px` góc dưới phải (`cx=924, cy=1118`), viền phát sáng Cyan `#36CCC8` × Cam `#F26B21`. Hợp chủ đề **tư duy, bóc tách sai lầm, công nghệ, bất động sản/nội thất cao cấp**.
   - **Biến thể B — `Light Pastel Dot-Grid UI (Full 9:16)`**: Phủ kín `1080×1920` nền sáng `#F4F6FC` → `#CED8FA` có chấm bi `Dot-Matrix` bước `32px`, Circle PiP lớn `416px` căn giữa bên dưới (`cx=540, cy=1465`, viền trắng `8px` + xanh `3px`), đường ray nét đứt nối các thẻ `1 → 2 → 3 → 4`, thẻ UI bo góc `32px` có `Skeleton Blur` làm mờ chữ phụ để nổi bật dòng chính + Pill Sticker nghiêng `-2°`. Hợp **hướng dẫn quy trình, demo phần mềm/AI, giáo dục, dược sĩ giải thích cơ chế**.
4. **Cá Nhân Hóa `DNA Độc Bản` Bằng Tài Nguyên Sẵn Có Của `Full Studio`**:
   - Luôn áp đúng bảng màu trong `brand_kits/`, ưu tiên **Chữ Gradient 5 điểm dừng tách viền (`fonts_tvc_vi/gradient-text-presets.css`)** cho tiêu đề lớn và dùng kho **`448` hiệu ứng 3D/Final Cut Offline (`fcp_hyperframes_pack`)** (`spring-pop`, `focus-blur-resolve`, `tracing-beam`, `stagger-cascade`, `cursor-glyph-trail`), tránh lạm dụng hiệu ứng nổ rối mắt vô nghĩa.

---

## 2. Quy Chuẩn Viết Kịch Bản Theo Công Thức `3-Hook + Nhạy Số Hình Ảnh`

Mỗi kịch bản xuất ra bắt buộc có đủ:
1. **3 Phương Án Hook Mở Đầu (`0–4s`)**:
   - `Hook 1 (Nỗi đau / Thói quen sai)`: Chỉ thẳng cái bẫy số đông đang mắc.
   - `Hook 2 (Khao khát kết quả - Desire)`: Show kết quả làm xong 1 mạch cực gọn ngay câu đầu.
   - `Hook 3 (Góc nhìn ngược - Contrarian)`: Đập tan lầm tưởng phổ biến trên thị trường.
2. **Bảng Phân Cảnh Chuyển Hóa Chữ Thô → Ẩn Dụ Thị Giác (`Visual Metaphor`)**:
   - Cột `Lời thoại` phải luôn đi kèm cột `Đồ họa sân khấu cụ thể` (ví dụ: bẫy kẹp, bình bộ nhớ tràn đỏ, hộp mở nắp, chuỗi DNA, thẻ đánh số nối xích, cửa sổ tài liệu có tích xanh), không ghi chung chung *"hiện chữ minh họa"*.
3. **Bản Caption Đăng Bài Đi Kèm (`Copy & Đăng Ngay`)** + **Gom Nhóm Lịch Quay Theo Bối Cảnh** khi làm chuỗi nhiều tập.
