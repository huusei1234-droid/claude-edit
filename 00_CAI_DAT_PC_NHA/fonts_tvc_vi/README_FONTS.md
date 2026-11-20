# 🔤 KHO 12 HỌ FONT TIẾNG VIỆT CHUẨN TVC OFFLINE (`31` FILE `.TTF`)

Toàn bộ các file `.ttf` trong thư mục này đều tích hợp đầy đủ **100% dấu Tiếng Việt + Latin** trong 1 file duy nhất, giúp HyperFrames vượt qua tuyệt đối kiểm tra `font_family_without_font_face` (Rule 9) và render mượt từ Frame 0 ngay cả khi không có mạng!

## Phân Vai 12 Họ Font Khi Dựng TVC

| Họ Font (`font-family`) | Các độ đậm có sẵn | Vai trò chuẩn trong TVC |
| :--- | :--- | :--- |
| **`Be Vietnam Pro`** | `500`, `600`, `700`, `800` | Phụ đề đáy không hộp nền, nút CTA, nhãn công dụng tiếng Việt gọn dấu |
| **`Cormorant Garamond`** | `600`, `700`, `700 Italic` | Chữ nổi **3D Glossy Silk-Satin** chuẩn Comfort / Dược mỹ phẩm |
| **`Playfair Display`** | `400`, `700`, `800`, `700 Italic` | Tên thương hiệu (`ĐIỀU KINH HT`, `ROMANCE LOVE`), chữ **3D Gold Bling!** |
| **`Prata`** | `400` | Tiêu đề thời trang / nước hoa / mỹ phẩm cao cấp (Editorial Didone) |
| **`Noto Serif Display`** | `700`, `800` | Tiêu đề Hoàng gia / Vàng kim / Đông y thượng hạng |
| **`Montserrat`** | `600`, `700`, `800`, `900` | Bảng tên đạo cụ (Diegetic UI), nhãn tập đoàn (`HT Pharma`), tiêu đề hiện đại |
| **`Oswald`** | `600`, `700` | Chữ IN HOA cao gầy cho **Text Hook 3 giây đầu** Reels / TikTok |
| **`Plus Jakarta Sans`** | `600`, `700`, `800` | Sans-serif trẻ trung cho dòng Skincare / Khoa học công nghệ |
| **`Lora`** | `600`, `700`, `400 Italic` | Chữ kể chuyện cảm xúc (Storytelling / Lời khuyên chuyên gia / Đạo lý) |
| **`Dancing Script`** | `700` | Dòng chữ viết tay mềm mại (`Hằng Thu`, `pure`) |
| **`Great Vibes`** | `400` | Chữ ký thư pháp bay bổng cho Đại sứ thương hiệu |
| **`Inter`** | `400`, `500`, `600` | Dòng khuyến cáo pháp lý nhỏ (`Legal Super`) sắc nét ở cỡ 14–18px |

## Cách Dùng Trong Project HyperFrames Mới
1. Chép các file `.ttf` cần dùng vào `07_HyperFrames_Project/assets/fonts/`.
2. Copy khối `@font-face` tương ứng từ file `fonts-tvc-vi.css` dán vào đầu thẻ `<style>` của `index.html` và các file `compositions/*.html`.
