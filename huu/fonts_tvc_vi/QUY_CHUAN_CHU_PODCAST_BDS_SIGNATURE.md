# Quy Chuẩn Thiết Kế Chữ Kép Podcast × BĐS / Doanh Nhân (`Cyan-Ice Spotlight × Signature Script`)

Đúc kết từ mẫu Typography Podcast & Bất Động Sản cao cấp (`@lopphovlog` / `editornghiepdu`), toàn bộ **21 tệp `.ttf` tĩnh hỗ trợ 100% dấu Tiếng Việt** đã được cài thẳng vào Windows Fonts (dùng ngay trong **CapCut / Premiere / Photoshop**) và đồng bộ vào cả 3 kho tài nguyên của Full Studio.

---

## 1. Giải Phẫu Hiệu Ứng Thị Giác Đặc Trưng

1. **Lớp Chữ Chính (`Main Display / Luxury Serif`)**:
   - **Tô màu Tâm Sáng Băng Ngọc (`Radial Cyan-Ice Spotlight`)**:
     - Hai rìa trái & phải: Xanh Lam Hoàng Gia đậm (`#1F42A6` -> `#24AEE0`).
     - Tâm giữa con chữ: Bừng sáng Xanh Ngọc Băng (`#35F2DF` -> `#9EFFFF`) kèm hào quang mờ nhẹ `drop-shadow(0 0 24px rgba(46, 232, 228, 0.28))`.
   - **Biến thể màu sang trọng khác**: `gold_luxury` (Đồng cổ -> Vàng Hoàng Kim tâm trắng kem cho BĐS hạng sang) & `rose_satin` (Hồng sen lụa cho Dược mỹ phẩm HTPM).
2. **Lớp Chữ Ký Đè Chồng (`Handwritten Signature Script`)**:
   - Màu trắng tinh khiết (`#FFFFFF`) đặt đè trực tiếp lên chữ chính, kèm bóng tách nền tối sát nét (`0 3px 10px rgba(4,8,22,0.88)`) + hào quang kem ấm dịu (`rgba(255,242,210,0.45)`).
   - **2 vị trí đặt chuẩn**:
     - `bottom_center` (*Đè chân chữ chính ở mốc `60%–65%` chiều cao*): dùng cho `UTM BEBAS × Autography`, `DOANH NHÂN × Signature`, `Chetta × Script`, `Braven × Bengoda`.
     - `top_left` (*Gác lệch vai trái đỉnh chữ chính*): dùng cho `Artful × BARLOW Italic`, `Starcity × BLONA`.

---

## 2. Bảng 10 Cặp Phối Font Tiếng Việt 100% Dấu (`PODCAST_BDS_PAIRS`)

| Mã Preset (`pair_key`) | Font Chính (`.ttf` Tiếng Việt) | Font Chữ Ký Đè (`.ttf` Tiếng Việt) | Bố cục | Ứng dụng đẹp nhất |
| :--- | :--- | :--- | :--- | :--- |
| **`barlow_artful`** | `BarlowCondensed-ExtraBoldItalic.ttf` | `BirthstoneBounce-Medium.ttf` | `top_left` | Intro tiêu đề Podcast hiện đại, Review công nghệ/tài chính |
| **`bebas_autography`** | `BigShouldersDisplay-Black.ttf` | `Allison-Regular.ttf` | `bottom_center` | Hook 3s Podcast tri thức, Kênh chia sẻ kinh doanh |
| **`magnesium_amsterdam`** | `Unbounded-Black.ttf` | `WindSong-Medium.ttf` | `bottom_center` | Tiêu đề điện ảnh BĐS, Dự án đại đô thị |
| **`blona_starcity`** | `SairaExtraCondensed-ExtraBold.ttf` | `Cherish-Regular.ttf` | `top_left` | Reels dọc 9:16 chữ cao gầy sang trọng |
| **`alexander_ameyallinda`** | `Montserrat-Black.ttf` | `BirthstoneBounce-Medium.ttf` | `bottom_center` | Thương hiệu cá nhân CEO / Doanh nhân / Diễn giả |
| **`caviar_catalina`** | `JosefinSans-Light.ttf` | `OoohBaby-Regular.ttf` | `bottom_center` | Penthouse, Villa nghỉ dưỡng tối giản tinh tế |
| **`chetta_adventures`** | `PlayfairDisplay-Bold.ttf` | `WindSong-Regular.ttf` | `bottom_center` | BĐS hạng sang, Kiến trúc nội thất, Mỹ phẩm cao cấp |
| **`braven_bengoda`** | `Prata-Regular.ttf` | `Ephesis-Regular.ttf` | `bottom_center` | Resort, Thời trang, Phong cách sống thượng lưu |
| **`impact_alfresco`** | `Anton-Regular.ttf` | `Corinthia-Bold.ttf` | `bottom_center` | Câu chốt cao trào, Hook tương phản mạnh |
| **`podcast_signature`** | `BarlowCondensed-Black.ttf` | `PassionsConflict-Regular.ttf` | `bottom_center` | Chuyên gia tư vấn sức khỏe / Dược sĩ / Podcast chữa lành |

---

## 3. Gọi Tự Động Bằng 1 Dòng Code Trong Mọi Video Full Studio

```python
import sys
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from podcast_bds_title import render_podcast_signature_title

# Xuất ngay file PNG trong suốt 1080p để ghép vào FFmpeg / CapCut / HyperFrames:
render_podcast_signature_title(
    main_text="DOANH NHÂN",
    sub_text="Đẳng cấp thương hiệu",
    pair_key="barlow_artful",   # hoặc bebas_autography, magnesium_amsterdam, chetta_adventures...
    theme="cyan_ice",           # hoặc "gold_luxury", "rose_satin"
    out_png="title_overlay.png",
)
```
