"""Hậu kỳ lắp ráp Timelapse Vách Tivi MS Studio (1920x1080 @ 30fps, sạch 100% không chữ, chỉ nhạc nền Timelapse).
- Tự động quét & cắt bỏ frame trắng đầu clip (nếu có) và cắt khít điểm nối F_k giữa các clip để không bị khựng/lặp.
- Tạo hiệu ứng Shutter Motion Blur thực tế của máy quay Timelapse công trình (chỉ mờ nhẹ chuyển động tay/người, nét căng kiến trúc tĩnh).
- Phối nhạc nền Timelapse chuẩn -14.0 LUFS, xuất bản Final lên Z:/Drive của tôi/AI_Full_Studio/04_Videos_Final/ và tạo Contact Sheet QA.
"""
import os, sys, json, shutil, subprocess
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(HERE, "frames")
CLIPS_DIR = os.path.join(HERE, "clips")
OUT_LOCAL = os.path.join(HERE, "ms-studio-vach-tivi-timelapse.mp4")
QA_SHEET = os.path.join(HERE, "qa_contact_sheet.jpg")

DRIVE_PROJECT_DIR = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\ms-studio-vach-tivi"
DRIVE_FINAL_MP4 = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\ms-studio-vach-tivi-timelapse.mp4"
BGM_PRIMARY = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Inspiring Design (4p31s).mp3"
BGM_FALLBACK = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx\bgm_bright_riley.mp3"


def find_clean_trim(video_path):
    """Kiểm tra 15 frame đầu để loại bỏ frame loé trắng (nếu ảnh tham chiếu sinh ra ở 0s) và kiểm tra độ mượt."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    dur = total / fps if fps > 0 else 8.0

    means = []
    diffs = []
    prev = None
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (160, 90))
        means.append(float(np.mean(small)))
        if prev is not None:
            diffs.append(float(np.mean(np.abs(small.astype(np.float32) - prev.astype(np.float32)))))
        prev = small
        idx += 1
    cap.release()

    # Tìm frame đầu tiên không bị loé trắng bất thường (Muse thường có khung 0..0.3s trắng/tĩnh)
    start_f = 0
    ref_mean = np.median(means[10:min(40, len(means))]) if len(means) > 12 else 128.0
    for i in range(min(15, len(means))):
        if means[i] > 240 or abs(means[i] - ref_mean) > 45:
            start_f = i + 1
    # Luôn cắt tối thiểu 0.32s đầu để triệt tiêu hoàn toàn khung trắng/tĩnh đầu clip Muse,
    # và giới hạn cửa sổ hành động tối đa 6.4s để không bao giờ bị kéo lê hay lặp động tác ở cuối clip 10s
    start_s = round(max(0.32, (start_f + 1) / fps), 3)
    end_s = round(min(start_s + 6.1, max(start_s + 1.0, dur - (2.0 / fps))), 3)
    avg_motion = float(np.mean(diffs)) if diffs else 0.0
    return {
        "fps": round(fps, 2),
        "total_frames": total,
        "raw_dur": round(dur, 3),
        "trim_start": start_s,
        "trim_end": end_s,
        "avg_motion": round(avg_motion, 2),
    }


def build_timelapse(speeds=None):
    if speeds is None:
        speeds = [2.4, 2.2, 2.2, 2.2, 2.3, 2.3, 2.3]

    bgm = BGM_PRIMARY if os.path.exists(BGM_PRIMARY) else BGM_FALLBACK
    if not os.path.exists(bgm):
        raise FileNotFoundError("Không tìm thấy file nhạc nền Timelapse!")

    tmp_dir = os.path.join(HERE, "_tmp_build")
    os.makedirs(tmp_dir, exist_ok=True)

    seg_files = []
    report_clips = []

    # 1. Đoạn mở đầu tĩnh 1.1s hiện trạng cũ F0_16x9.png
    f0_img = os.path.join(FRAMES_DIR, "F0_16x9.png")
    seg0 = os.path.join(tmp_dir, "seg_00_intro.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-t", "1.1", "-i", f0_img,
        "-vf", "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-an", seg0
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    seg_files.append(seg0)

    # 2. 6 chặng thi công Timelapse c01..c06 (đội ngũ 3 kỹ thuật viên áo xanh-cam-trắng MS STUDIO)
    for idx in range(1, 7):
        cpath = os.path.join(CLIPS_DIR, f"c0{idx}.mp4")
        if not os.path.exists(cpath):
            raise FileNotFoundError(f"Thiếu clip {cpath}")
        info = find_clean_trim(cpath)
        spd = speeds[idx - 1]
        seg_out = os.path.join(tmp_dir, f"seg_{idx:02d}.mp4")
        vf = (
            f"trim=start={info['trim_start']}:end={info['trim_end']},setpts=PTS-STARTPTS,"
            f"scale=1920:1080:flags=lanczos,"
            f"tblend=all_mode=average:all_opacity=0.45,"
            f"setpts=PTS/{spd},fps=30,format=yuv420p"
        )
        subprocess.run([
            "ffmpeg", "-y", "-i", cpath,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-an", seg_out
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        seg_files.append(seg_out)
        info["clip"] = f"c0{idx}.mp4"
        info["speed"] = spd
        report_clips.append(info)
        print(f"[seg {idx}] {info}", flush=True)

    # 3. Đoạn kết 4.0s: Hiệu ứng bật công tắc lên đèn sáng rực rỡ trên F7_16x9.png (viết trực tiếp từng frame bằng OpenCV để 100% đúng độ sáng gốc, không dính lỗi eval=init của bộ lọc eq FFmpeg)
    f7_img = os.path.join(FRAMES_DIR, "F7_16x9.png")
    seg8 = os.path.join(tmp_dir, "seg_08_outro.mp4")
    base_bgr = cv2.imread(f7_img)
    base_1080 = cv2.resize(base_bgr, (1920, 1080), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    outro_frames = 120  # 4.0s @ 30fps
    raw_avi = os.path.join(tmp_dir, "seg_08_raw.avi")
    vw = cv2.VideoWriter(raw_avi, cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (1920, 1080))
    for fi in range(outro_frames):
        t_sec = fi / 30.0
        # 0.0s -> 0.45s: bật đèn mượt từ 0.88 lên 1.04 (nhấn sáng nhẹ lúc đèn chùm bật) rồi ổn định đúng 1.00 độ sáng rực rỡ gốc của F7
        if t_sec < 0.35:
            p = t_sec / 0.35
            gain = 0.88 + 0.16 * (p * p * (3 - 2 * p))
        elif t_sec < 0.70:
            p = (t_sec - 0.35) / 0.35
            gain = 1.04 - 0.04 * p
        else:
            gain = 1.00
        # Micro-zoom cực nhẹ 1.000 -> 1.024 để cảnh kết có sức sống điện ảnh mà vẫn giữ trọn đèn chùm & sàn
        z = 1.0 + 0.024 * (fi / max(1, outro_frames - 1))
        cw, ch = int(round(1920 / z)), int(round(1080 / z))
        x0, y0 = (1920 - cw) // 2, (1080 - ch) // 2
        cropped = base_1080[y0:y0 + ch, x0:x0 + cw]
        zoomed = cv2.resize(cropped, (1920, 1080), interpolation=cv2.INTER_LINEAR)
        frame_u8 = np.clip(zoomed * gain, 0, 255).astype(np.uint8)
        vw.write(frame_u8)
    vw.release()
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_avi,
        "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-an", seg8
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    seg_files.append(seg8)

    # 4. Nối toàn bộ các đoạn không nén lại lần thừa, rồi phủ nhạc nền chuẩn -14.0 LUFS
    concat_txt = os.path.join(tmp_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for sf in seg_files:
            p_clean = sf.replace("\\", "/")
            f.write(f"file '{p_clean}'\n")

    vid_silent = os.path.join(tmp_dir, "video_silent.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c", "copy", vid_silent
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    # Đo thời lượng thực tế của video_silent
    cap = cv2.VideoCapture(vid_silent)
    v_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    v_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    total_dur = round(v_frames / v_fps, 3)
    cap.release()
    fade_out_st = round(max(0.5, total_dur - 1.8), 3)

    # Mix nhạc nền Timelapse chuẩn -14 LUFS (bỏ 1.5s im lặng đầu bài nhạc nếu có)
    af = (
        f"atrim=start=1.5:end={1.5 + total_dur},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={fade_out_st}:d=1.8,"
        f"loudnorm=I=-14.0:TP=-1.0:LRA=9.0"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", vid_silent, "-i", bgm,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
        "-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart", OUT_LOCAL
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    print(f"[FINAL] Đã xuất {OUT_LOCAL} (thời lượng {total_dur}s)", flush=True)

    # 5. Xuất Contact Sheet 12 khung hình trải đều để QA bằng mắt
    make_qa_sheet(OUT_LOCAL, QA_SHEET)

    # 6. Đồng bộ lên Google Drive (03_Du_An & 04_Videos_Final) theo quy tắc bắt buộc trong GEMINI.md
    if os.path.exists(r"Z:\Drive của tôi\AI_Full_Studio"):
        os.makedirs(DRIVE_PROJECT_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(DRIVE_FINAL_MP4), exist_ok=True)
        shutil.copy2(OUT_LOCAL, DRIVE_FINAL_MP4)
        shutil.copy2(QA_SHEET, os.path.join(DRIVE_PROJECT_DIR, "qa_contact_sheet.jpg"))
        for fn in ("job.json", "kich-ban-duyet.md", "canvas_mgr.py", "render_timelapse.py"):
            src_f = os.path.join(HERE, fn)
            if os.path.exists(src_f):
                shutil.copy2(src_f, os.path.join(DRIVE_PROJECT_DIR, fn))
        print(f"[SYNC] Đã đồng bộ lên Google Drive: {DRIVE_FINAL_MP4}", flush=True)

    json.dump({"total_dur": total_dur, "bgm": bgm, "clips": report_clips}, open(os.path.join(HERE, "render_stats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def make_qa_sheet(video_path, out_jpg):
    from PIL import Image, ImageDraw
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1)
    dur = nframes / fps
    cols, rows = 4, 3
    tw, th = 480, 270
    sheet = Image.new("RGB", (cols * tw, rows * th), (18, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for i in range(cols * rows):
        t = (dur * (i + 0.4)) / (cols * rows)
        fidx = min(nframes - 1, max(0, int(t * fps)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, fidx)
        ok, fr = cap.read()
        if not ok:
            continue
        rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(rgb).resize((tw, th), Image.LANCZOS)
        cx, cy = (i % cols) * tw, (i // cols) * th
        sheet.paste(pil_im, (cx, cy))
        draw.rectangle([(cx + 8, cy + 8), (cx + 110, cy + 32)], fill=(0, 0, 0))
        draw.text((cx + 14, cy + 13), f"t = {t:04.1f}s", fill=(255, 220, 80))
    cap.release()
    sheet.save(out_jpg, "JPEG", quality=92)
    print(f"[QA] Đã lưu Contact Sheet: {out_jpg}", flush=True)


if __name__ == "__main__":
    build_timelapse()
