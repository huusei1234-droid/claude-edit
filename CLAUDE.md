# Full studio

**Việc đầu tiên, với mọi yêu cầu: đọc `HUONG-DAN-AI.md`** (mục tiêu dự án, luồng subagent, chọn kit, dịch vụ và cổng, việc phải hỏi người dùng). Sau đó mới đọc kit theo loại video bên dưới.

## Làm một video (luồng điều phối bằng subagent)
Khi người dùng đưa chủ đề / brief và muốn ra video: theo **mục 2 của `HUONG-DAN-AI.md`**. Gọi lần lượt subagent
`content` (viết kịch bản, **dừng chờ người dùng duyệt**), `tao-asset` (giọng + clip AI, chỉ sau khi duyệt), `edit` (dựng bằng kit
của thể loại, tự kiểm QC). Định nghĩa subagent: `.claude/agents/`; mẫu `job.json` và bản kịch bản duyệt: `mau/`.

## Tạo thể loại video MỚI từ video mẫu (việc riêng)
Chỉ khi người dùng muốn **thêm thể loại mới / học phong cách từ một video mẫu** (hoặc hỏi "video này làm thế nào"), **đọc
`phong-cach/PHAN-TICH-VIDEO-MAU/PHAN-TICH-VIDEO-MAU.md`**: chọn mức giống (1–4), chạy `refkit.py analyze`, xem 4 lượt, đo chi tiết,
viết `ref-notes.md`, rồi biến thành một kit mới trong `phong-cach/<tên>/`. Việc này **không** chạy trong mỗi lần làm video thường:
khi đã có kit thì chỉ đọc kit.

## Video dạng SaaS (sass)
Khi người dùng yêu cầu tạo hoặc edit video dạng SaaS (quảng cáo phần mềm, giao diện kính, nền tối, After Effects),
**phải đọc folder `phong-cach/saas-animation/` trước khi làm**:
1. `phong-cach/saas-animation/PHONG-CACH.md` (tóm tắt phong cách, kit 1.3.0)
2. `phong-cach/saas-animation/CLAUDE.md` (quy trình 11 bước: brief → 16:9 + 9:16 có nhạc/SFX → QC → tự học)
3. `phong-cach/saas-animation/knowledge/01, 02, 03, 07, 10` (07 bắt buộc: các bẫy đã gặp)
4. Khi cần: `knowledge/11` (9:16), `knowledge/12` + `audio/music/INDEX.md` (âm thanh, chọn nhạc)

Dùng `lib/`, `tools/`, `audio/` và mẫu `projects/orbiq/build.jsx` trong folder đó. Nhạc Mixkit không có trong repo công khai: xem `HUONG-DAN-AI.md` mục 9.

## Video talking head dọc (người nói + đồ hoạ)
Khi người dùng yêu cầu tạo hoặc edit video talking head dọc 1080×1920 (TikTok/Reels/Shorts, clip người nói, phụ đề từng từ,
chữ sau lưng người, B-roll, After Effects), **phải đọc folder `phong-cach/talking-head/` trước khi làm**:
1. `phong-cach/talking-head/AGENTS.md` (hướng dẫn chính, quy trình tóm tắt, luật dựng)
2. `phong-cach/talking-head/CON-THIEU.md` (những gì chưa kiểm chứng: tiếng Việt, ngành y, v.v.)
3. `phong-cach/talking-head/knowledge/01, 02, 07` (07 bắt buộc: các bẫy đã gặp)
4. Khi cần: `knowledge/03` (thư viện hiệu ứng), `04` (chuẩn bị clip), `05` (âm thanh), `10` (font Việt, nội dung y tế)

Dùng `lib/` (`saas-lib.jsx` + `th-lib.jsx`), `tools/` và mẫu `examples/foodtage/build.jsx` trong folder đó. Đây là kit khác với SaaS:
đừng nhầm hai phong cách. Tài nguyên Foodtage (`assets`, `media`) không có trong repo công khai.
Làm hook: đọc thêm `knowledge/11` (ví dụ tiếng Việt) và `knowledge/12` (luật hook); `plan.md` phải có mục Hook.

## Video UGC AI một cú máy (thời trang/sản phẩm, thể loại thử)
Khi người dùng muốn video người mẫu AI nói + khoe sản phẩm, một cú máy, camera cố định, không chữ (clip Omni + giọng AI):
đọc `phong-cach/ugc-ai-thoi-trang/PHONG-CACH.md` rồi `ref-notes.md`. Kit rút từ **một** video mẫu, đã chạy thật 1 lần (bài học ở mục 6b của `PHONG-CACH.md`).

## Video Talking Head × Motion Graphics Kiểu Kobe (`Dark 16:9 Stage` & `Light SaaS UI` + `Circle PiP`) & Chiến Dịch 10 Kịch Bản Liên Hoàn
Khi người dùng yêu cầu làm video **chia sẻ chuyên môn / bán khóa học / giới thiệu công cụ / tư vấn dịch vụ** theo phong cách **Motion Graphics trực quan + Người nói khung tròn (`Circle PiP`), không rải phụ đề karaoke**, hoặc muốn viết **1 Super-Prompt ra trọn bộ 10 kịch bản (3 Hook) + Ads + Bài giảng + Landing Page**:
1. Đọc `phong-cach/kobe-ai-motion-talking-head/PHONG-CACH.md`, `phong-cach/kobe-ai-motion-talking-head/KIEN-THUC-TRUYEN-TAI-TU-2-VIDEO.md` và `.agents/skills/kobe-motion-talking-head/SKILL.md`.
2. Chọn đúng biến thể (`Dark Cyber 16:9-in-9:16` hoặc `Light Pastel Dot-Grid 9:16`), tuân thủ nghiêm **6 quy luật Vật lý Lớp phủ & 4 quy luật `Tactile Micro-SFX`** trong `phong-cach/kobe-ai-motion-talking-head/CHUYEN-DONG-LOP-PHU-VA-SFX.md`, cá nhân hóa **DNA Độc Bản** bằng `brand_kits/` + `fonts_tvc_vi` Chữ Gradient + `fcp_hyperframes_pack` và soát lỗi bằng mắt Editor trước khi xuất Final.

## Video TVC Quảng Cáo Sản Phẩm / Motion Graphics trên HyperFrames (`24fps` / `30fps`)
Khi người dùng yêu cầu dựng **TVC quảng cáo sản phẩm (Dược mỹ phẩm / FMCG / Nội thất / Thương hiệu)** hoặc Motion Graphics bằng **HyperFrames**:
1. Đọc `GEMINI.md`, `BO_KIEN_THUC_TVC_AI_PORTABLE/GEMINI.md` và các skills `.agents/skills/tvc-qc-san-pham/SKILL.md`, `.agents/skills/hyperframes/SKILL.md`, `.agents/skills/hyperframes-registry/SKILL.md`.
2. **Ưu tiên số 1 Chữ Gradient Tiếng Việt (`fonts_tvc_vi`)**: Luôn nhúng bộ `39` font `.ttf` đã kiểm chứng 100% dấu tiếng Việt + `fonts-tvc-vi.css` + `gradient-text-presets.css` tại `BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi/` (cấu trúc 2 lớp tách viền `.grad-back` + `.grad-front` 5 điểm dừng màu + quét sáng ánh kim).
3. **Kho `229` Hiệu Ứng Chữ & Chuyển Cảnh Final Cut Pro / Apple Liquid Glass Offline (`fcp_hyperframes_pack`)**: Luôn tra cứu và chép trực tiếp từ `BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fcp_hyperframes_pack/` bằng lệnh `python .../copy_fcp_effect.py <project_dir> <ten_hieu_ung>` (`cinematic-zoom`, `whip-pan`, `vfx-liquid-glass`, `focus-blur-resolve`, `lt-clean-bar`, `light-leak`...) **trước khi** gọi mạng `npx hyperframes add`.

## Kho Tài Nguyên Chuẩn Hóa Dùng Chung Cho Mọi Dự Án
- **Font Tiếng Việt TVC & Chữ Gradient (`39` `.ttf` + `6` Presets)**: `BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi/` (đồng bộ tại `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\04_Font Chữ TVC & Chữ Gradient`).
- **Hiệu ứng 3D, After Effects Motion Graphics & Final Cut Pro Offline (`448/448` items + `ae-3d-effects.jsx`)**: `BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fcp_hyperframes_pack/` (cho HyperFrames) và `phong-cach/saas-animation/lib/ae-3d-effects.jsx` (Camera 3D, Chữ nổi 3D Extrude, Thẻ nghiêng 3D, Vòng xoay Orbit 3D, Tách lớp Isometric 3D cho After Effects).
- **Nhạc nền BGM (`1.340` bài / 12 thể loại) & SFX phẳng (`1.043` files)**: `Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)` và `02_Hiệu Ứng Âm Thanh (SFX)`.
- **Chỉnh màu 3D LUTs (`12` `.cube`), Video Overlays (`10` `.mp4` Screen), `Brand Kits` & Tách nền sản phẩm PNG (`IS-Net`)**: `BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/luts_chinh_mau/` (`apply_lut.py`), `video_overlays_4k/`, `brand_kits/` và `05_SCRIPTS_TU_DONG_HOA/cutout_product_png.py`.
- **Talking Head Dược sĩ / Chuyên gia (`talking-head-v3`)**: Đọc thêm `.agents/skills/talking-head-v3/SKILL.md`.
- **Quy chuẩn Đặt Tên & Thư Mục Xuất Video Final Bắt Buộc Toàn Hệ Thống (`edit/canvas-tools/final_delivery.py`)**: Mọi video Final bắt buộc đặt tên **`<YYMMDD> <Thương hiệu> <tên tiếng Việt có dấu> final.mp4`** (ví dụ: `261119 HTPM 5 sản phẩm tuổi 25 final.mp4`) và lưu thẳng vào đúng thư mục hoàn thiện của từng nhãn hàng (`HTPM` → `Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\`, `F20` → `Z:\Máy tính khác\My Computer\F20\Final\`, `Feel Chicken` → `Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\`, `MS Nội Thất` → `Z:\Drive của tôi\dự án ngoài\MS Nội Thất\`, `Việt Hàn` → `...\VIỆT HÀN\File Hoàn Thiện Việt Hàn\`), đồng bộ kèm bản sao tại `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\` và `D:\XUẤT CAPCUT\`.

Trả lời bằng tiếng Việt.
