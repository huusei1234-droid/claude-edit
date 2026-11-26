# -*- coding: utf-8 -*-
"""
Đồng bộ toàn bộ bàn giao Ngày 03 (26/11/2026) — AN VƯỢNG PHARMA lên Google Drive & Bản sao cục bộ:
- 4 Video 9:16 Nhịp Nhanh Sinh Hoạt -> G:\My Drive\dự án ngoài\An Vượng\03. Video Hoàn Thiện\261126 - Ngày 26.11.2026\
- 4 Bài Thiết Kế JPG Text To -> G:\My Drive\dự án ngoài\An Vượng\01. Hình Đăng Bài & Bài Viết Mới\261126 - Ngày 26.11.2026\
- 4 Ảnh Mẫu Diện Mạo 9:16 -> G:\My Drive\dự án ngoài\An Vượng\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\02. Ảnh Mẫu Nhân Vật Xuyên Suốt\Trang Phục Mẫu 9x16 (26.11)\
- Bản sao lưu tại G:\My Drive\AI_Full_Studio\04_Videos_Final\ & C:\XUẤT CAPCUT\An Vượng\
- Cập nhật daily_progress.json trên cả Local và Drive!
"""
import json, os, shutil
from pathlib import Path

WORK = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_03_2611")
G_BRAND = Path(r"G:\My Drive\dự án ngoài\An Vượng")

DST_VID = G_BRAND / "03. Video Hoàn Thiện" / "261126 - Ngày 26.11.2026"
DST_DES = G_BRAND / "01. Hình Đăng Bài & Bài Viết Mới" / "261126 - Ngày 26.11.2026"
DST_LKS = G_BRAND / "02. Ảnh Sản Phẩm & Mẫu Nhân Vật" / "02. Ảnh Mẫu Nhân Vật Xuyên Suốt" / "Trang Phục Mẫu 9x16 (26.11)"
DST_MASTER_VID = Path(r"G:\My Drive\AI_Full_Studio\04_Videos_Final")
DST_LOCAL_VID = Path(r"C:\XUẤT CAPCUT\An Vượng\261126 - Ngày 26.11.2026")

for d in (DST_VID, DST_DES, DST_LKS, DST_MASTER_VID, DST_LOCAL_VID):
    d.mkdir(parents=True, exist_ok=True)


def main():
    # 1. Copy 4 Designs + QA + Caption
    for jp in sorted((WORK / "03_Final_4_Designs_JPG").glob("*.jpg")):
        shutil.copy2(jp, DST_DES / jp.name)
        print(f"[SYNC DESIGN] {DST_DES / jp.name}")
    for extra in [WORK / "QA_4_Bai_Thiet_Ke_Ngay_2611.jpg", WORK / "Caption_Ngay_03_2611_Chuan_Luat_TPBS.txt"]:
        if extra.exists():
            shutil.copy2(extra, DST_DES / extra.name)

    # 2. Copy 4 Videos + QA + Caption
    for vp in sorted((WORK / "06_Final_4_Videos_MP4").glob("*.mp4")):
        shutil.copy2(vp, DST_VID / vp.name)
        shutil.copy2(vp, DST_MASTER_VID / vp.name)
        shutil.copy2(vp, DST_LOCAL_VID / vp.name)
        print(f"[SYNC VIDEO] {DST_VID / vp.name}")
    for extra in [WORK / "QA_4_Videos_Ngay_2611_Nhanh_SinhHoat.jpg", WORK / "Caption_Ngay_03_2611_Chuan_Luat_TPBS.txt"]:
        if extra.exists():
            shutil.copy2(extra, DST_VID / extra.name)

    # 3. Copy 4 Look Anchors 9x16
    for lp in sorted((WORK / "04_Video_Looks_9x16").glob("*.png")):
        shutil.copy2(lp, DST_LKS / lp.name)

    # 4. Update daily_progress.json
    for prog_path in [
        Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\daily_progress.json"),
        G_BRAND / "00. Hồ Sơ Thương Hiệu & Kế Hoạch" / "daily_progress.json",
    ]:
        if prog_path.exists():
            pdata = json.loads(prog_path.read_text(encoding="utf-8"))
            pdata["character_location"] = "Đa dạng không gian sinh hoạt đời thường khớp kịch bản (không khóa cứng Nha Trang)"
            pdata["video_pacing_rule"] = "FAST_CUTS_2_0S_TO_2_65S_MAX_NO_SLOWMO_DRAG_12_SCENES_PER_VIDEO"
            pdata["last_zalo_sync_date"] = "2026-11-26"
            pdata.setdefault("completed_days", {})["2026-11-26"] = {
                "day_code": "N03",
                "zalo_synced": True,
                "total_videos_delivered": 4,
                "total_designs_delivered": 4,
                "status": "done",
                "folders": [
                    str(DST_VID),
                    str(DST_DES),
                ],
            }
            prog_path.write_text(json.dumps(pdata, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[UPDATED PROGRESS] {prog_path}")


if __name__ == "__main__":
    main()
