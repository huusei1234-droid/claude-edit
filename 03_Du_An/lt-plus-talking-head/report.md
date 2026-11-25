# Report: lt-plus-talking-head (Viên Đặt Phụ Khoa LT PLUS Hằng Thu) — Bản Final chuẩn v3

- **Video Master MP4 (`1080×1920`, `30 fps`, `70.37s`, `-14.0 LUFS`)**:
  - Xuất trực tiếp lên Google Drive: `Z:/Drive của tôi/LT_PLUS_TALKING_HEAD_FINAL.mp4`
  - Bản xuất ổ D: `D:/XUẤT CAPCUT/LT_PLUS_TALKING_HEAD_FINAL.mp4`
  - Bản lưu dự án: `output/lt-plus-talking-head/lt_plus_talking_head_v3_final.mp4`
- **Dự án CapCut Desktop (`9:16`, 2 Track tách biệt: Track 0 Video+VO+SFX 12 phân cảnh & Track 1 Nhạc nền BGM riêng `vol=0.28`)**:
  - `C:/Users/Hang thu/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/LT_PLUS_HangThu_TalkingHead_Final`
- **Nguồn Footage & Ảnh Sản Phẩm Gốc**:
  - Footage người nói đã cắt sẵn: `D:/AI/1/LT PLUS.mp4` (`1080×1920`, `30 fps`)
  - Bộ ảnh thật sản phẩm: `Z:/.shortcut-targets-by-id/1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-/hằng thu pharma/Ảnh` (`4.png`, `2.png`, `6.png`, `DSC00268.JPG`, `DSC00274.JPG`, `DSC00275.JPG`)

---

## 1. Cấu trúc kỹ thuật & Nâng cấp chuẩn Talking-Head v3

1. **Hiệu đính 100% chính tả tiếng Việt & Thuật ngữ Y dược (`main_cut_clean.json`)**:
   - Đã rà soát từng từ trên toàn bộ `27` đoạn thoại (`238` từ), sửa triệt để các lỗi nhận dạng giọng nói (`"Khí hữu"` → `"Khí hư"`, `"ra mạo"` → `"ra máu"`, `"triều chứng"` → `"triệu chứng"`, `"khảm phù khoa"` → `"khám phụ khoa"`, `"nguồn nhìn"` → `"hướng dẫn"`, `"viết đặt LT và lớn của hàng thu"` → `"viên đặt LT Plus của Hằng Thu"`, `"hoang bã, ít bấu, kim ân hoa, axit latix"` → `"Hoàng bá, Ích mẫu, Kim ngân hoa, Acid Lactic"`).
2. **Nền phòng thật tự nhiên + Làm tối mượt khi lên Animation (`ANIM_DIM_WINDOWS`)**:
   - Tách riêng người nói bằng mô hình **RVM** (`main_cut_matte.mp4`, đủ `2111` khung) kết hợp mặt nạ bảo vệ bàn gỗ và hộp **LT PLUS** thật trên bàn (`0–38s`) lẫn trên tay Dược sĩ (`38–70.4s`).
   - Giữ nền phòng thật 100% tự nhiên ở các đoạn nói chuyển ý; khi xuất hiện khối đồ hoạ (`Hook`, `Lưu ý 1/2`, `Giải pháp 3`, `Từ khoá lớn sau đầu`, `Orbital Rings`), nền sau lưng tự động hạ sáng mượt xuống `25%` kèm bokeh blur nhẹ (`smoothstep` `0.50s`) để tôn bật chữ phát sáng.
3. **4 Cảnh Split B-Roll 2 Lớp Riêng Biệt — Khoá Tỷ Lệ `0%` Méo Hình (`fit_cover`)**:
   - `13.36–17.85s` (*Biểu hiện dễ nhầm lẫn*): Clip bàn trà hoa cúc & sổ tay hồng (`broll_1a_calendar.mp4`) + Clip 3D giọt sương ngọc trai trên lụa hồng (`broll_1b_droplet.mp4`).
   - `22.48–27.90s` (*Không phải dấu hiệu riêng biệt*): Clip bàn tư vấn ống nghe y khoa (`broll_2a_consult.mp4`) + Clip 3D màng chắn bảo vệ sinh học (`broll_2b_barrier.mp4`).
   - `33.88–37.62s` (*Chẩn đoán chính xác*): Clip kính hiển vi & ống nghiệm phòng khám (`broll_3a_lab.mp4`) + Clip 3D khiên pha lê hồng-vàng (`broll_3b_shield.mp4`).
   - `47.35–52.52s` (*Tổ hợp 6 thành phần*): Clip thảo dược thiên nhiên Kim ngân hoa – Trà xanh – Trầu không (`broll_4a_herbs.mp4`) + Clip **Showcase Sản Phẩm Thật 100%** từ bộ ảnh gốc Hộp đóng, Lọ 15 viên & Hộp nam châm mở (`broll_4b_ltplus.mp4` — giữ nét tuyệt đối từng chữ tiếng Việt trên bao bì).
4. **Bố cục Face-Safe & Box-Safe + An toàn kiểm duyệt nền tảng (`knowledge/10`)**:
   - Chữ Hook mở đầu sử dụng thuật ngữ y khoa trung tính (*"Dấu hiệu bất thường / PHẢI Lộ Tuyến? / Chưa thể đoán chỉ qua bên ngoài!"*) tránh bị AI của TikTok/Reels hạn chế phân phối chữ lớn.
   - Phụ đề từng từ (`Palatino Bold Italic`, tối đa 2 dòng tại `y = 1130..1196`) nằm gọn trên nền áo tối: dưới cằm `95px` và trên mép hộp **LT PLUS** `130px`, không che mặt hay che sản phẩm ở bất kỳ khung hình nào.
   - Các thẻ `Icon Tile` viền sáng chạy vòng (`EdgeSweep`) đặt ở góc trái dưới (`x = 215, y = 1455`) để nhường trọn không gian bên phải cho hộp **LT PLUS** thật.
5. **Âm thanh Broadcast `-14.0 LUFS`**:
   - Phối giọng thật Dược sĩ + nhạc nền ấm `bgm_warm_fretless.mp3` + 20 điểm Studio SFX đồng bộ từng chuyển động, chuẩn hoá **2 lượt `loudnorm` đạt `-14.0 LUFS`**.

---

## 2. Kết quả tự kiểm QC (`knowledge/08-qc.md`)
- **[Đạt — Đã kiểm & tinh chỉnh trước render]** Qua lưới kiểm 9 khung `v3_test_grid.jpg`, phát hiện chữ sau đầu `"KHÁM PHỤ KHOA"` chạm mép khung và khoảng cách chữ Hook `"PHẢI Lộ Tuyến?"` hơi sát; đã thu cỡ chữ sau đầu xuống `132–158px`, tách thoáng cụm Hook và thu gọn dòng khuyến cáo đáy (`17px`) trước khi chạy bản render cuối.
- **[Đạt]** Font tiếng Việt đủ 100% dấu; Glow dùng Dual Drop-Shadow giữ nguyên sắc độ hồng phấn, vàng champagne và xanh ngọc.
- **[Không kiểm được bằng tai]** Độ cân bằng cảm xúc chủ quan giữa giọng thật, SFX và nhạc nền cần người dùng mở nghe trực tiếp.

---

## 3. Các câu khẳng định sức khoẻ trong lời nói (liệt kê theo `knowledge/10` để duyệt cuối)
- *"Lộ tuyến có thể không có triệu chứng, một số người có thể tăng tiết dịch, ra máu giữa kỳ kinh hoặc sau quan hệ, nhưng dấu hiệu này có thể xuất hiện trong các tình trạng khác nên cần được kiểm tra."*
- *"Ngứa, mùi khó chịu hoặc khí hư đổi màu không phải là dấu hiệu riêng biệt của lộ tuyến."*
- *"Đừng tự chẩn đoán rồi dùng viên đặt theo lời truyền miệng. Điều cần là cần phải khám phụ khoa, mô tả rõ triệu chứng, và thực hiện xét nghiệm theo hướng dẫn của bác sĩ."*
- *"Nếu đang tìm hiểu một loại viên đặt hỗ trợ điều trị viêm lộ tuyến, thì có thể xem xét đến sản phẩm viên đặt LT Plus của Hằng Thu."*
- *"Sản phẩm có Hoàng bá, Ích mẫu, Kim ngân hoa, Trà xanh, Trầu không và Acid Lactic."*
- *"3 ngày các chị dùng 1 lần. 1 hộp như thế này 15 viên, dùng trong vòng 30 ngày đến 40 ngày, các chị sẽ cảm nhận sự khác biệt so với trước khi chưa dùng sản phẩm."* *(Đã gắn cố định dòng khuyến cáo ở chân khung hình suốt thời lượng video).*
