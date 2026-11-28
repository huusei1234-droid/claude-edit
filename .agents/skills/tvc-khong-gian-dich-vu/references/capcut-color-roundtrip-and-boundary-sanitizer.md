# Thuật Toán Đồng Bộ Màu/Làm Đẹp Da CapCut & Lọc Sạch Frame Biên (`CapCut Round-Trip Engine`)

Tài liệu kỹ thuật chi tiết cho quy trình **Editor chỉnh màu & làm đẹp da trên CapCut → Xuất file 2K/1080p → AI tự động bóc tách màu + da mịn đưa ngược vào các Slide chuyển động trên HyperFrames**.

---

## 1. Bẫy Xoay `90°` Trên Clip Sony / iPhone Trong `draft_content.json`

Trong `materials.videos` của CapCut, các file quay dọc bằng máy Sony (`C9xxx.MP4`) hoặc iPhone thường vẫn ghi `width: 1920, height: 1080` kèm cờ xoay metadata `90°`. Nếu dùng `(1920, 1080)` để tính khung hiển thị trên canvas `1920×1080` của CapCut sẽ sai lệch hoàn toàn vùng lấy mẫu màu!

**Quy tắc bắt buộc**: Luôn đọc kích thước thực **sau xoay (`post-rotation`)** bằng OpenCV:

```python
import cv2

def get_true_post_rotation_dims(video_path: str) -> tuple[int, int]:
    cap = cv2.VideoCapture(video_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return w, h
```

Khi dựng lại hình học hiển thị của một `segment` trên canvas `(CW, CH) = (1920, 1080)` của CapCut:
1. Gọi `(rw, rh) = get_true_post_rotation_dims(path)`.
2. Khung fit cơ bản trên canvas CapCut: `base_s = min(CW / rw, CH / rh)`, `dw0 = rw * base_s`, `dh0 = rh * base_s`.
3. Nhân với `seg["clip"]["scale"]["x"]`, `["y"]` và dịch tâm theo `seg["clip"]["transform"]["x"] * (CW / 2)`, `-seg["clip"]["transform"]["y"] * (CH / 2)` (lưu ý trục `Y` của CapCut hướng lên trên, ngược dấu với toạ độ pixel ảnh!).

---

## 2. Chiến Lược Kép: `DIRECT_CROP` Cho Thẻ Ngang + `Poly3 33³ 3D-LUT` Cho Thẻ Dọc

1. **Trường hợp 1 — Thẻ Ngang Hiển Thị Đủ Khung Trên Video Xuất CapCut (`vis_w >= box_w - 2` và không bị lớp trên đè)**:
   - **Crop trực tiếp (`DIRECT_CROP`)** từ file video xuất `2K/1080p` của CapCut để bảo toàn **100% tuyệt đối** cả màu chỉnh lẫn da mịn/trắng sáng của CapCut.
   - **Cảnh báo quan trọng**: Tuyệt đối kiểm tra `rw > rh` (clip ngang thật) trước khi đưa vào `DIRECT_CROP`! Nếu nhầm một clip dọc (`1080×1920`, `vis_w = 266px`) vào khung ngang `842px`, phần rìa hai bên sẽ cắt dính hình của `Track 0` bên dưới (ví dụ dính chữ biển hiệu nền vào thẻ mặt tiền!).

2. **Trường hợp 2 — Thẻ Dọc `9:16` Hoặc Vùng `Track 0` Bị Thẻ PiP Đè Lên**:
   - Chỉ lấy mẫu các pixel **không bị che khuất** giữa frame gốc `(X)` và frame đã xuất từ CapCut `(Y)`.
   - Khớp đa thức bậc 3 `20` hạng tử RGB (`b, g, r, b², g², r², bg, gr, rb, b³, g³, r³, b²g, bg², g²r, gr², r²b, rb², bgr, 1`) có neo góc mềm (`w_c = 0.035`, `reg = 8e-3`), kết hợp đường cong phần dư đơn điệu theo phân vị (`Quantile Residual Curve`) và nướng thành **`33×33×33 3D-LUT`** (`MAE ≈ 2.3 – 5.5 / 255`).
   - Áp dụng nội suy 3 chiều (`trilinear interpolation`) + lọc nét nhẹ tương đương hiệu ứng `clear` của CapCut, xuất qua ống dẫn `rawvideo -> h264_nvenc` chuẩn `bt709` để loại bỏ hoàn toàn HDR container atoms.

---

## 3. Bộ Lọc Sạch Frame Biên Tự Động (`Boundary Frame Sanitizer`)

Khi cắt nhiều clip con từ một file xuất CapCut bằng `ffmpeg -ss <t>`, sai số keyframe/timestamp rất dễ làm **frame `0` dính 1 frame của cảnh trước** hoặc **frame cuối dính 1 frame của cảnh kế tiếp** (`diff > 20.0`).

Sau khi sinh xong thư mục `assets/slides/*.mp4`, **bắt buộc chạy bước lọc biên** cho mọi clip:

```python
import cv2, numpy as np

def audit_clip_Active_Frames(mp4_path: str, used_duration_s: float):
    cap = cv2.VideoCapture(mp4_path)
    need_frames = int(round(used_duration_s * 30.0)) + 2
    prev = None
    jumps = []
    for fidx in range(need_frames):
        ok, fr = cap.read()
        if not ok:
            jumps.append((fidx, "EOF"))
            break
        if prev is not None:
            d = float(np.mean(np.abs(fr.astype(np.float32) - prev.astype(np.float32))))
            if d > 18.0:
                jumps.append((fidx, round(d, 2)))
        prev = fr
    cap.release()
    return jumps
```

- Nếu xuất hiện bước nhảy cảnh ở `fidx == 1` (`frame 0` bị lẫn cảnh trước): bỏ `frame 0`, lấy từ `frame 1` trở đi.
- Nếu xuất hiện bước nhảy cảnh ở cuối (`fidx >= need_frames - 4`): cắt dừng ngay trước frame nhảy và nhân bản mượt (`clone`) frame sạch cuối cùng thêm `6 frames` dự phòng để đảm bảo `0%` nháy hình và `0%` thiếu thời lượng.

---

## 4. Chuẩn Mã Hóa Âm Thanh Dấu Phẩy Động Không Rè & Không Chồng Nhạc

1. **Tránh lỗi chồng 2 lớp nhạc nền (`Double-BGM Clash`)**:
   - Khi dự án đã có file tổng hợp thoại + nhạc nền (`clean_vo_bgm.mp3`), kiểm tra kỹ phổ âm và các track nhạc trong CapCut (`T9`, `T13`, `T14`...) để đảm bảo tại bất kỳ giây nào từ `0.0s → cuối video` chỉ có **đúng 1 bản nhạc nền duy nhất đang phát** (tránh lỗi 2 segment cùng bài nhạc đặt lệch `src_start` đè lên nhau hoặc trộn đè thêm nhạc lần 2).
2. **Tránh clipping nội bộ khi qua bộ lọc `equalizer` của FFmpeg**:
   - Nguồn WAV `pcm_s16le` nếu đưa thẳng vào `highpass` / `equalizer` sẽ bị clipping số nguyên 16-bit ở các đỉnh hô đồng thanh lớn.
   - **Luôn đặt `aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.93` ở đầu chuỗi `-af`**:
     ```powershell
     ffmpeg -y -i verified_zero_sfx_master.wav `
       -af "aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.93,highpass=f=55,equalizer=f=2800:t=q:w=1.2:g=1.8,equalizer=f=185:t=q:w=1.4:g=1.0,alimiter=limit=0.95" `
       -c:a libmp3lame -b:a 320k assets/audio/clean_vo_bgm.mp3
     ```
