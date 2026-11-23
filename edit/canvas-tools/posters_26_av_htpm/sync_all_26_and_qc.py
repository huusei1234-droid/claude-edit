# -*- coding: utf-8 -*-
"""
Build Side-by-Side Visual Comparison Sheets (Mẫu Chị Hằng vs Hôm Qua vs Bản Mới Chữ Lớn & Sản Phẩm Lớn)
+ Full 26-Poster Overview Grids + Sync all 26 .JPG & 26 .PSD files to all 4 Google Drive destinations + GitHub repo folder!
"""
import glob, os, shutil
from PIL import Image, ImageDraw, ImageFont, ImageCms

V3_DIR = r"d:\AI\full studio\projects\av_htpm_26_posters_v3"
OUT_ROOT = os.path.join(V3_DIR, "Final_Deliverables")
AUDIT_DIR = os.path.join(V3_DIR, "audit")
BRAIN_DIR = r"C:\Users\Hang thu\.gemini\antigravity\brain\3c47ebbb-8468-44f7-b584-19bc2acdc8cf"
SAMPLE_REF = os.path.join(BRAIN_DIR, ".user_uploaded", "media_1795404719183_a2e19ad8.jpg")
OLD_DRIVE_FINAL = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\261122-26-thiet-ke-infographic-av-htpm\Final_Deliverables"
FONT_BOLD = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\BeVietnamPro-ExtraBold.ttf"

SRGB_BYTES = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def make_grid(img_paths: list, cols: int, thumb_w: int, thumb_h: int, out_path: str):
    rows = (len(img_paths) + cols - 1) // cols
    pad = 22
    lbl_h = 52
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (thumb_h + lbl_h + pad) + pad), (16, 20, 18))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_BOLD, 19)
    for idx, p in enumerate(img_paths):
        im = Image.open(p).convert("RGB")
        im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        r, c = idx // cols, idx % cols
        x = pad + c * (thumb_w + pad) + (thumb_w - im.width) // 2
        y = pad + r * (thumb_h + lbl_h + pad)
        sheet.paste(im, (x, y))
        title = os.path.splitext(os.path.basename(p))[0].replace("261122 ", "")
        draw.text((pad + c * (thumb_w + pad), y + thumb_h + 10), title[:46], fill=(255, 228, 132), font=font)
    sheet.save(out_path, quality=94, subsampling=0, icc_profile=SRGB_BYTES)
    shutil.copy2(out_path, os.path.join(BRAIN_DIR, os.path.basename(out_path)))
    print("Saved QC grid ->", out_path, flush=True)


def make_comparison_vs_chihang():
    new_av1 = os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke", "01. AV Protein", "261122 AVPM AV Protein - Thiết kế 01 Thành phần chuẩn.jpg")
    new_av2 = os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke", "01. AV Protein", "261122 AVPM AV Protein - Thiết kế 02 Giá trị dinh dưỡng.jpg")
    new_ht1 = os.path.join(OUT_ROOT, "02_Hang_Thu_Pharma_18_Thiet_Ke", "01. Viên Uống Điều Kinh Bổ Trứng", "261122 HTPM Điều Kinh Bổ Trứng - Thiết kế 01 Thảo dược quý.jpg")

    items = [
        (SAMPLE_REF, "MẪU CHỊ HẰNG DUYỆT (Rõ ràng, kín bố cục)"),
        (new_av1, "BẢN MỚI #01: AV PROTEIN (Chữ & SP lớn + Bục đá 3D)"),
        (new_av2, "BẢN MỚI #02: AV PROTEIN (Layout B chữ kép cực rõ)"),
        (new_ht1, "BẢN MỚI HẰNG THU: ĐIỀU KINH (Đồng bộ chuẩn form)"),
    ]
    tw, th = 560, 700
    pad = 24
    sheet = Image.new("RGB", (4 * (tw + pad) + pad, th + 104), (16, 20, 18))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_BOLD, 21)
    for i, (p, lbl) in enumerate(items):
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x = pad + i * (tw + pad)
        draw.text((x, 24), lbl, fill=(255, 226, 120), font=font)
        sheet.paste(im, (x, 72))
    out_p = os.path.join(AUDIT_DIR, "V3_QC_Compare_ChiHang_vs_New.jpg")
    sheet.save(out_p, quality=95, subsampling=0, icc_profile=SRGB_BYTES)
    shutil.copy2(out_p, os.path.join(BRAIN_DIR, os.path.basename(out_p)))
    for sp_p in (new_av1, new_av2, new_ht1):
        if os.path.exists(sp_p):
            shutil.copy2(sp_p, os.path.join(BRAIN_DIR, os.path.basename(sp_p)))
    print("Saved comparison sheet ->", out_p, flush=True)


def sync_everywhere():
    av_src = os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke")
    ht_src = os.path.join(OUT_ROOT, "02_Hang_Thu_Pharma_18_Thiet_Ke")

    targets = [
        (av_src, r"Z:\Máy tính khác\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261122 - Bộ 8 Thiết Kế Infographic An Vượng Pharma"),
        (av_src, r"Z:\Drive của tôi\dự án ngoài\An Vượng\261122 - Bộ 8 Thiết Kế Infographic An Vượng Pharma"),
        (ht_src, r"Z:\Máy tính khác\My Computer\hằng thu pharma\01. Hình Đăng Bài & Bài Viết Mới\261122 - Bộ 18 Thiết Kế Infographic Hằng Thu Pharma"),
        (OUT_ROOT, r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\261122-26-thiet-ke-infographic-av-htpm\Final_Deliverables"),
    ]
    for src, dst in targets:
        if os.path.exists(src):
            os.makedirs(dst, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print("Synced ->", dst, flush=True)

    # Sync updated V3 Python code to both Google Drive 03_Du_An and GitHub repo edit/canvas-tools/posters_26_av_htpm
    for code_dst in [
        r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\261122-26-thiet-ke-infographic-av-htpm\code",
        r"d:\AI\full studio\edit\canvas-tools\posters_26_av_htpm",
    ]:
        os.makedirs(code_dst, exist_ok=True)
        for py in glob.glob(os.path.join(V3_DIR, "*.py")):
            shutil.copy2(py, os.path.join(code_dst, os.path.basename(py)))
        print("Synced code ->", code_dst, flush=True)


if __name__ == "__main__":
    av_jpgs = sorted(glob.glob(os.path.join(OUT_ROOT, "01_An_Vuong_Pharma_8_Thiet_Ke", "**", "*.jpg"), recursive=True))
    ht_jpgs = sorted(glob.glob(os.path.join(OUT_ROOT, "02_Hang_Thu_Pharma_18_Thiet_Ke", "**", "*.jpg"), recursive=True))
    make_comparison_vs_chihang()
    if av_jpgs:
        make_grid(av_jpgs, cols=4, thumb_w=460, thumb_h=575, out_path=os.path.join(AUDIT_DIR, "V3_QC_01_An_Vuong_8_Posters.jpg"))
    if ht_jpgs:
        make_grid(ht_jpgs[:9], cols=3, thumb_w=460, thumb_h=575, out_path=os.path.join(AUDIT_DIR, "V3_QC_02_Hang_Thu_Part1_9Posters.jpg"))
        make_grid(ht_jpgs[9:], cols=3, thumb_w=460, thumb_h=575, out_path=os.path.join(AUDIT_DIR, "V3_QC_03_Hang_Thu_Part2_9Posters.jpg"))
    sync_everywhere()
    print("ALL 26 V3 POSTERS + PSDs SYNCED TO GOOGLE DRIVE & REPO!", flush=True)
