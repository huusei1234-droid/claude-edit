# -*- coding: utf-8 -*-
"""
Đồng bộ trọn bộ 8 Poster Quảng Cáo (PNG + JPG sRGB + PSD 3 Layer) & 8 Bài Đăng Mới
vào Thư mục Sản phẩm Hằng Thu Pharma và Master Cloud Storage (03_Du_An).
"""
import os, shutil

PROJ_DIR = r"d:\AI\full studio\projects\htpm_8_posts_1911"
ANH_DIR  = r"Z:\Máy tính khác\My Computer\hằng thu pharma\Ảnh"
SI_DIR   = os.path.join(ANH_DIR, "Ảnh gửi sỉ")

DEST_HT_MAIN = os.path.join(ANH_DIR, "Bộ 8 Hình & Bài Đăng Quảng Cáo Mới (19-11)")
DEST_CLOUD   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-8-bai-dang-san-pham-1911"

SI_SUBFOLDER_MAP = {
    "01_Vien_Uong_Dieu_Kinh_Bo_Trung_Hang_Thu": "Điều Kinh Hằng Thu",
    "03_Vien_Uong_Da_Day_HT_Hang_Thu": "Dạ dày Hằng Thu",
    "04_Dung_Dich_Ve_Sinh_Romance_VIP_Hang_Thu": "Dung Dịch Vệ Sinh Romance Vip Hằng Thu",
    "05_Vien_Dat_Phu_Khoa_Khit_Hong_Hang_Thu": "Viên đặt phụ khoa Hằng Thu",
    "06_Vien_Duong_Tu_Cung_Romance_Love_Hang_Thu": "Viên đặt bôi trơn ROMANCE LOVE",
    "07_Ngoc_Long_Hoan_Hang_Thu": "Ngọc Long Hoàn Hằng Thu",
    "08_Vien_Uong_White_Skin_Hang_Thu": "Viên uống trắng da, điều hòa nội tiết_ White skin",
}

def sync_tree(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)

def main():
    # 1. Sync main package into Hằng Thu Pharma/Ảnh/Bộ 8 Hình & Bài Đăng Quảng Cáo Mới (19-11)
    os.makedirs(DEST_HT_MAIN, exist_ok=True)
    for fn in ("00_TONG_HOP_8_BAI_DANG_MOI_HANG_THU.md", "00_TONG_HOP_8_BAI_DANG_MOI_HANG_THU.txt"):
        shutil.copy2(os.path.join(PROJ_DIR, fn), os.path.join(DEST_HT_MAIN, fn))

    sync_tree(os.path.join(PROJ_DIR, "Poster_JPG_sRGB"), DEST_HT_MAIN)
    sync_tree(os.path.join(PROJ_DIR, "Poster_PNG_1200x1500"), os.path.join(DEST_HT_MAIN, "Poster_PNG_Goc_1200x1500"))
    sync_tree(os.path.join(PROJ_DIR, "File_PSD_3_Layer_Photoshop"), os.path.join(DEST_HT_MAIN, "File_PSD_3_Layer_Photoshop"))
    sync_tree(os.path.join(PROJ_DIR, "Bai_Dang_Rieng_Tung_San_Pham"), os.path.join(DEST_HT_MAIN, "Bai_Dang_Rieng_Tung_San_Pham"))
    shutil.copy2(
        os.path.join(PROJ_DIR, "check", "all_8_posters_master_qc.jpg"),
        os.path.join(DEST_HT_MAIN, "00_TONG_QUAN_8_POSTER_HANG_THU.jpg"),
    )
    print("Synced complete package to:", DEST_HT_MAIN)

    # 2. Also place matching Poster JPG + Caption TXT right inside each subfolder of Ảnh gửi sỉ!
    for slug, sub_name in SI_SUBFOLDER_MAP.items():
        target_sub = os.path.join(SI_DIR, sub_name)
        if os.path.exists(target_sub):
            shutil.copy2(
                os.path.join(PROJ_DIR, "Poster_JPG_sRGB", f"{slug}.jpg"),
                os.path.join(target_sub, f"Poster_Quang_Cao_Moi_{slug[:2]}.jpg"),
            )
            shutil.copy2(
                os.path.join(PROJ_DIR, "Bai_Dang_Rieng_Tung_San_Pham", f"{slug}.txt"),
                os.path.join(target_sub, f"Bai_Dang_Moi_{slug[:2]}.txt"),
            )
            print(f"Synced into Ảnh gửi sỉ/{sub_name}")

    # 3. Sync scripts, captions, QC sheets & posters into Master Cloud Storage 03_Du_An
    os.makedirs(DEST_CLOUD, exist_ok=True)
    for fn in os.listdir(PROJ_DIR):
        sp = os.path.join(PROJ_DIR, fn)
        if os.path.isfile(sp) and fn.endswith((".py", ".md", ".txt")):
            shutil.copy2(sp, os.path.join(DEST_CLOUD, fn))
    sync_tree(os.path.join(PROJ_DIR, "Poster_JPG_sRGB"), os.path.join(DEST_CLOUD, "Poster_JPG_sRGB"))
    sync_tree(os.path.join(PROJ_DIR, "Bai_Dang_Rieng_Tung_San_Pham"), os.path.join(DEST_CLOUD, "Bai_Dang_Rieng_Tung_San_Pham"))
    shutil.copy2(
        os.path.join(PROJ_DIR, "check", "all_8_posters_master_qc.jpg"),
        os.path.join(DEST_CLOUD, "all_8_posters_master_qc.jpg"),
    )
    print("Synced project archive to:", DEST_CLOUD)

if __name__ == "__main__":
    main()
