import csv
import re
import shutil
from pathlib import Path

art = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682\ke_hoach_content_30_ngay_htpm.md")
local_dir = Path(r"d:\AI\full studio\03_Du_An\htpm-daily-1video-1post")
local_dir.mkdir(parents=True, exist_ok=True)

local_md = local_dir / "LICH_30_NGAY_HTPM_1VIDEO_1POST_VA_TU_DO_CHI_HANG.md"
shutil.copy2(art, local_md)

brand_kit_dir = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")
shutil.copy2(local_dir / "MODEL_DNA_LOCK_CHI_HANG_HTPM.md", brand_kit_dir / "MODEL_DNA_LOCK_CHI_HANG_HTPM.md")

drive_post_dir = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới")
cloud_proj_dir = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-daily-1video-1post")
cloud_proj_dir.mkdir(parents=True, exist_ok=True)

text = art.read_text(encoding="utf-8")
rows = []
for line in text.splitlines():
    if line.startswith("| **Ngày "):
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) == 4:
            clean = [re.sub(r"<br\s*/?>", " | ", p) for p in parts]
            clean = [re.sub(r"\*\*(.*?)\*\*", r"\1", c) for c in clean]
            clean = [re.sub(r"\*(.*?)\*", r"\1", c) for c in clean]
            clean = [c.replace("`", "") for c in clean]
            rows.append(clean)

csv_local = local_dir / "261124_LICH_CONTENT_30_NGAY_HTPM_TU_DO_CHI_HANG.csv"
with csv_local.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "Ngày & Thứ",
        "Tạo hình & Trang phục Chị Hằng (Đổi mới mỗi ngày)",
        "01 Video USP (9:16 @ 24fps — Giọng Thanh Thanh)",
        "01 Bài Đăng Thiết Kế (2 Ảnh HD + .PSD + Caption)",
    ])
    w.writerows(rows)

for dst_dir in [drive_post_dir, cloud_proj_dir]:
    if dst_dir.exists():
        shutil.copy2(local_md, dst_dir / "261124_LICH_CONTENT_30_NGAY_HTPM_VA_TU_DO_CHI_HANG.md")
        shutil.copy2(csv_local, dst_dir / "261124_LICH_CONTENT_30_NGAY_HTPM_EXCEL.csv")
        shutil.copy2(local_dir / "MODEL_DNA_LOCK_CHI_HANG_HTPM.md", dst_dir / "MODEL_DNA_LOCK_CHI_HANG_HTPM.md")

# Also keep htpm-ke-hoach-content-30-ngay folder updated if present
old_cloud_dir = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-ke-hoach-content-30-ngay")
if old_cloud_dir.exists():
    shutil.copy2(local_md, old_cloud_dir / "261124_LICH_CONTENT_30_NGAY_HTPM_VA_TU_DO_CHI_HANG.md")
    shutil.copy2(csv_local, old_cloud_dir / "261124_LICH_CONTENT_30_NGAY_HTPM_EXCEL.csv")

print(f"[SYNC OK] Parsed {len(rows)} daily rows -> synced MD + CSV + DNA Lock to Local & Google Drive!")
