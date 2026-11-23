# Báo Cáo Kiểm Định Chất Lượng (QC Report) — HTPM Khô Rát Vùng Kín × Tokyo Drift (`HTPM_FINAL.mp4` v2)

## 1. Thông Số Kỹ Thuật Xuất Bản
- **File xuất cục bộ duy nhất**: `D:\XUẤT CAPCUT\HTPM_FINAL.mp4` (`1080×1920`, `30/1 fps` CFR, `1.134` frames = `37.80s`, `0` lỗi giải mã).
- **Đồng bộ Cloud Master**: `Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\HTPM_FINAL.mp4`
- **Chuẩn âm lượng phát sóng (`ebur128`)**: Integrated **`-14.0 LUFS`**, True Peak **`-3.0 dBFS`**, nhạc `Dj Kantik - Teriyaki Boyz - Tokyo Drift & Sean Paul - Temperature (Remix).mp3` bắt đầu chính xác từ **`29.00s`**.

## 2. Xử Lý Triệt Để 2 Điểm Phản Hồi
1. **Khóa tĩnh `100%` khung hình Studio (`0%` giật/nhịp camera)**:
   - Loại bỏ hoàn toàn dao động `math.sin(...)` theo nhịp beat trên toàn khung hình lẫn trên các thẻ lớp phủ sau khi hạ cánh, đồng thời gỡ toàn bộ 13 điểm zoom ra/vào liên tục (`CAM_KEYFRAMES`), giữ khung hình A-roll Dược sĩ và bàn sản phẩm đứng êm tuyệt đối `1:1` từng pixel suốt `37.80s`.
2. **Chữ nhấn kết xuất thực tế bằng HyperFrames (`ProRes 4444` Alpha) từ kho hiệu ứng Final Cut Pro & After Effects (`fcp_hyperframes_pack`)**:
   - `0.05 – 2.82s`: Final Cut `lt-mask-reveal` quét tia sáng vàng + `yt-prism-title` tách sắc sai RGB 3D + `shimmer-sweep` ánh kim (`"KHÔ RÁT VÙNG KÍN!"`).
   - `2.88 – 5.66s` & `8.55 – 11.25s`: Final Cut `lt-mask-reveal` thanh tiêu đề quét laser mở/đóng mượt.
   - `14.18 – 16.02s`: MotionVFX `lt-neon-border` viền sáng chạy vòng quanh + After Effects `marker-highlight` nét cọ vàng gạch chân động (`"VIÊM NHIỄM!"`).
   - `16.06 – 20.46s`: MotionVFX `lt-neon-border` 2 luồng sáng đối xứng + After Effects `bottom-up-letters` trồi từng từ qua mặt nạ + `shimmer-sweep` (`"CHỌN ĐÚNG THÀNH PHẦN / DƯỠNG ẨM + PHỤC HỒI"`).
   - `20.56 – 25.10s` & `25.26 – 30.14s`: Final Cut `lt-clean-bar` mở tâm đối xứng & `lt-mask-reveal` quét sáng Emerald.
   - `30.26 – 33.16s`: Apple Final Cut `lt-clean-bar` + 4 chip hoạt chất nảy lò xo lệch pha (`stagger: 0.07s`).
   - `33.22 – 37.76s`: After Effects `success-check` vẽ nét SVG dấu tích trực tiếp + `line-by-line-slide` 3 trụ cột + thanh CTA Final Cut mở tâm.
