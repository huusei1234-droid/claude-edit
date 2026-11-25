# -*- coding: utf-8 -*-
"""
Step 5: Build High-Res Visual QC Sheets (including Side-by-Side vs CT Hằng's Sample)
and Sync all 26 .JPG + 26 .PSD 4-Layer Photoshop files to Google Drive (An Vượng & Hằng Thu Pharma).
"""
import glob, os, shutil
from PIL import Image, ImageDraw, ImageFont

PROJ = r"d:\AI\full studio\projects\av_htpm_26_posters_2211"
OUT_ROOT = os.path.join(PROJ, "Final_Deliverables")
AUDIT_DIR = os.path.join(PROJ, "audit")
SAMPLE_REF = r"C:\Users\001\.gemini\antigravity\brain\8c410fa3-31d5-47df-8611-fc1b3fad1994\.user_uploaded\media_1795363232203_c85550ff.jpg"
FONT_BOLD = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-Bold.ttf"

def make_grid(img_paths: list, cols: int, thumb_w: int, thumb_h: int, out_path: str):
    rows = (len(img_paths) + cols - 1) // cols
    pad = 24
    lbl_h = 54
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (thumb_h + lbl_h + pad) + pad), (18, 22, 20))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_BOLD, 20)
    for idx, p in enumerate(img_paths):
        im = Image.open(p).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        r, c = idx // cols, idx % cols
        x = pad + c * (thumb_w + pad) + (thumb_w - im.width) // 2
        y = pad + r * (thumb_h + lbl_h + pad)
        sheet.paste(im, (x, y))
        title = os.path.splitext(os.path.basename(p))[0]
        draw.text((pad + c * (thumb_w + pad), y + thumb_h + 10), title[:54], fill=(255, 228, 132), font=font)
    sheet.save(out_path, quality=94)
    print("Saved QC sheet ->", out_path)

def make_vs_sample_sheet():
    av_dir = os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke", "01. AV Protein")
    jpgs = sorted(glob.glob(os.path.join(av_dir, "*.jpg")))
    if not jpgs or not os.path.exists(SAMPLE_REF):
        return
    items = [SAMPLE_REF] + jpgs[:2]
    labels = ["MẪU THAM KHẢO CHỊ HẰNG GỬI", "BẢN MỚI #01 (THÀNH PHẦN + BAO BÌ THẬT 6K)", "BẢN MỚI #02 (LỢI ÍCH & BỮA PHỤ CHUẨN)"]
    tw, th = 640, 800
    sheet = Image.new("RGB", (3 * (tw + 30) + 30, th + 100), (16, 20, 18))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_BOLD, 24)
    for i, (p, lbl) in enumerate(zip(items, labels)):
        im = Image.open(p).convert("RGB")
        im.thumbnail((tw, th), Image.Resampling.LANCZOS)
        x = 30 + i * (tw + 30) + (tw - im.width) // 2
        y = 70 + (th - im.height) // 2
        draw.text((30 + i * (tw + 30), 22), lbl, fill=(255, 224, 115), font=font)
        sheet.paste(im, (x, y))
    out_p = os.path.join(AUDIT_DIR, "QC_Compare_Sample_vs_New_AV_Protein.jpg")
    sheet.save(out_p, quality=95)
    print("Saved comparison sheet ->", out_p)

def sync_to_google_drive():
    av_src = os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke")
    ht_src = os.path.join(OUT_ROOT, "02_Hang_Thu_Pharma_18_Thiet_Ke")

    targets = [
        (av_src, r"G:\Other computers\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261122 - Bộ 8 Thiết Kế Infographic An Vượng Pharma"),
        (av_src, r"G:\My Drive\dự án ngoài\An Vượng\261122 - Bộ 8 Thiết Kế Infographic An Vượng Pharma"),
        (ht_src, r"G:\Other computers\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261122 - Bộ 18 Thiết Kế Infographic Hằng Thu Pharma"),
        (OUT_ROOT, r"G:\My Drive\AI_Full_Studio\03_Du_An\261122-26-thiet-ke-infographic-av-htpm\Final_Deliverables"),
    ]
    for src, dst in targets:
        if os.path.exists(src):
            os.makedirs(dst, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print("Synced ->", dst)

if __name__ == "__main__":
    av_jpgs = sorted(glob.glob(os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke", "**", "*.jpg"), recursive=True))
    ht_jpgs = sorted(glob.glob(os.path.join(OUT_ROOT, "02_Hang_Thu_Pharma_18_Thiet_Ke", "**", "*.jpg"), recursive=True))
    if av_jpgs:
        make_grid(av_jpgs, cols=4, thumb_w=480, thumb_h=600, out_path=os.path.join(AUDIT_DIR, "QC_01_An_Vuong_8_Posters.jpg"))
        make_vs_sample_sheet()
    if ht_jpgs:
        make_grid(ht_jpgs[:10], cols=5, thumb_w=420, thumb_h=525, out_path=os.path.join(AUDIT_DIR, "QC_02_Hang_Thu_Part1_10Posters.jpg"))
        make_grid(ht_jpgs[10:], cols=4, thumb_w=460, thumb_h=575, out_path=os.path.join(AUDIT_DIR, "QC_03_Hang_Thu_Part2_8Posters.jpg"))
    sync_to_google_drive()
    print("SYNC & QC COMPLETE!")
