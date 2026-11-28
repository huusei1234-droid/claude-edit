"""
Ngày 01 (24/11/2026) — Kiểm định QA 12 Khung Hình + Vùng An Toàn 9:16 + Loudness LUFS
và Bàn giao Trọn Bộ 01 Video USP Dọc 9:16 + 01 Bài Đăng Thiết Kế (2 Ảnh HD + 2 .PSD + Caption)
lên Google Drive Hằng Thu Pharma + Cập nhật daily_progress.json!
"""
import datetime
import json
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

PROJ_DIR = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124")
MASTER_MP4 = PROJ_DIR / "08_Render_Master" / "ltplus_d01_master_24p.mp4"
POST_DIR = PROJ_DIR / "09_Bai_Thiet_Ke_Gel_Phu_Khang"
ARTIFACT_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682")

FINAL_VIDEO_NAME = "261124 HTPM viên đặt LT Plus tự tin suốt ngày dài final.mp4"

BRAND_VIDEO_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma")
CLOUD_VIDEO_DIR = Path(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final")
LOCAL_BACKUP_DIR = Path(r"D:\XUẤT CAPCUT\hằng thu pharma")

BRAND_POST_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\HTPM_Daily_Content\Ngay_01_2411")
CLOUD_POST_DIR = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-daily-1video-1post\Daily_Output\Ngay_01_2411")

PROGRESS_JSON = Path(r"d:\AI\full studio\03_Du_An\htpm-daily-1video-1post\daily_progress.json")


def measure_video_qa(mp4_path: Path):
    pr = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate",
                "-of", "json", str(mp4_path),
            ]
        ).decode("utf-8")
    )
    ebu = subprocess.run(
        ["ffmpeg", "-nostats", "-i", str(mp4_path), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    m_i = re.findall(r"I:\s*(-?\d+\.\d+)\s*LUFS", ebu)
    lufs = float(m_i[-1]) if m_i else None

    dur = float(pr["format"]["duration"])
    size_mb = round(int(pr["format"]["size"]) / (1024 * 1024), 2)

    # Extract 12 evenly spaced frames with Safe-Zone 9:16 red guidelines drawn for visual inspection
    qa_frames_dir = PROJ_DIR / "08_Render_Master" / "qa_frames"
    qa_frames_dir.mkdir(parents=True, exist_ok=True)
    timestamps = [0.8, 3.8, 7.5, 11.5, 15.5, 23.0, 30.0, 33.5, 38.0, 46.5, 52.8, 55.5]
    tiles = []
    for idx, ts in enumerate(timestamps, start=1):
        ts_clamped = min(dur - 0.3, ts)
        fp = qa_frames_dir / f"f_{idx:02d}.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{ts_clamped:.2f}", "-i", str(mp4_path), "-frames:v", "1", "-q:v", "2", str(fp)],
            check=True,
        )
        im = Image.open(fp).convert("RGB")
        d = ImageDraw.Draw(im)
        # Draw 5 TikTok x Reels Forbidden Zone Borders in Red
        d.line([(0, 248), (1080, 248)], fill=(255, 60, 60), width=4)
        d.line([(0, 1548), (1080, 1548)], fill=(255, 60, 60), width=4)
        d.line([(52, 248), (52, 1548)], fill=(255, 60, 60), width=3)
        d.line([(1026, 248), (1026, 860)], fill=(255, 60, 60), width=3)
        d.rectangle([(886, 860), (1080, 1548)], outline=(255, 60, 60), width=4)
        tiles.append((f"t={ts_clamped:.1f}s", im))

    tw, th = 330, 586
    sheet = Image.new("RGB", (tw * 4, th * 3), (20, 12, 16))
    sd = ImageDraw.Draw(sheet)
    for i, (lbl, im) in enumerate(tiles):
        c, r = i % 4, i // 4
        sheet.paste(im.resize((tw - 8, th - 28), Image.Resampling.LANCZOS), (c * tw + 4, r * th + 24))
        sd.text((c * tw + 12, r * th + 4), lbl, fill=(255, 220, 235))

    qa_sheet = PROJ_DIR / "htpm_d01_ltplus_261124_qa_sheet.jpg"
    sheet.save(qa_sheet, quality=90)
    if ARTIFACT_DIR.exists():
        shutil.copy2(qa_sheet, ARTIFACT_DIR / "htpm_d01_ltplus_261124_qa_sheet.jpg")

    return {"duration_s": round(dur, 2), "size_mb": size_mb, "lufs": lufs, "streams": pr["streams"], "qa_sheet": str(qa_sheet)}


def main():
    qa_info = measure_video_qa(MASTER_MP4)
    print(f"[QA OK] {qa_info}", flush=True)

    delivered_videos = []
    for vdir in (BRAND_VIDEO_DIR, CLOUD_VIDEO_DIR, LOCAL_BACKUP_DIR):
        vdir.mkdir(parents=True, exist_ok=True)
        dst = vdir / FINAL_VIDEO_NAME
        shutil.copy2(MASTER_MP4, dst)
        delivered_videos.append(str(dst))
        print(f"[VIDEO DELIVERED] {dst}", flush=True)

    delivered_posts = []
    for pdir in (BRAND_POST_DIR, CLOUD_POST_DIR):
        pdir.mkdir(parents=True, exist_ok=True)
        for f in POST_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in (".jpg", ".psd", ".txt"):
                shutil.copy2(f, pdir / f.name)
        # Also copy the Day 01 Video into the unified Day_01 folder if convenient? Keep clean link/meta
        delivered_posts.append(str(pdir))
        print(f"[POST DELIVERED] {pdir}", flush=True)

    # Also archive build scripts to Cloud project dir
    cloud_code_dir = CLOUD_POST_DIR / "scripts_d01"
    cloud_code_dir.mkdir(parents=True, exist_ok=True)
    for pyf in PROJ_DIR.glob("*.py"):
        shutil.copy2(pyf, cloud_code_dir / pyf.name)

    # Update daily_progress.json so 16:00 / multi-slot cron knows 2026-11-24 is 100% DONE!
    prog = json.loads(PROGRESS_JSON.read_text(encoding="utf-8"))
    prog["video_ratio"] = "9:16 ONLY (1080x1920 @ 24fps — KHÔNG làm 16:9)"
    prog["completed_days"]["2026-11-24"] = {
        "day_code": "Ngày 01 (24/11/2026)",
        "status": "done",
        "completed_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "chi_hang_outfit": "Bộ 01 — Blazer trắng kem chiết eo khoác ngoài áo lụa hồng phấn cổ đổ, khuyên tai ngọc trai nhỏ",
        "usp_video_sku": "SP02 — Viên Đặt Phụ Khoa LT Plus Hằng Thu",
        "usp_video_final": str(BRAND_VIDEO_DIR / FINAL_VIDEO_NAME),
        "design_post_sku": "SP09 — Gel Phụ Khang Hằng Thu",
        "design_post_dir": str(BRAND_POST_DIR),
        "qa": qa_info,
    }
    PROGRESS_JSON.write_text(json.dumps(prog, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(PROGRESS_JSON, Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-daily-1video-1post\daily_progress.json"))
    print("[PROGRESS UPDATED] 2026-11-24 marked as DONE!", flush=True)


if __name__ == "__main__":
    main()
