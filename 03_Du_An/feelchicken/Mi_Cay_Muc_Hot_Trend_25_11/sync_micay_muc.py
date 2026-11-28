import shutil
from pathlib import Path

base = Path(r"d:\AI\full studio\projects\feelchicken_micay_muc_chay")
out_dir = base / "XUAT_MI_CAY_MUC_THAT_CHAY"

cap_no_price = """MÌ CAY MỰC NGUYÊN CON – MÓN HOT TREND ĐÃ CHÍNH THỨC ĐỔ BỘ NHA TRANG!

Team mê hải sản và đồ cay Hàn Quốc tại Nha Trang đâu rồi? Siêu phẩm Mì Cay Mực nguyên con khổng lồ đang làm mưa làm gió đã chính thức lên sóng tại cả 2 cơ sở Feel Chicken!

Nhìn nồi mì bốc khói nghi ngút là muốn xì xụp liền tay:
- Mực ống nguyên con khía khoanh dày căng mọng, tươi giòn ngọt lịm ngập tràn mặt nồi.
- Nước dùng kim chi Hàn Quốc chua cay đậm đà đủ 7 cấp độ thách thức vị giác, ăn kèm sợi mì Hàn dai ngon và topping xúc xích, cá viên, nấm, rau tươi đầy ụ.

Tag ngay hội cạ cứng lên kèo ghé Feel Chicken chiến thử hôm nay hoặc nhắn tin/gọi hotline để quán ship nóng tận nhà chỉ trong 15 phút nhé!
---
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
CS1: 38 Nguyễn Đình Chiểu, Nha Trang
CS2: 35 Trần Hữu Duyệt, Vĩnh Điềm Trung, Nha Trang
Giờ mở cửa: 10:00 – 22:00
Hotline/Ship nhanh: 0796 601 106
#FeelChicken #MiCayMuc #HotTrendNhaTrang #MiCayNhaTrang #FoodNhaTrang
"""

cap_with_129k = """MÌ CAY MỰC NGUYÊN CON – MÓN HOT TREND ĐÃ CHÍNH THỨC ĐỔ BỘ NHA TRANG!

Team mê hải sản và đồ cay Hàn Quốc tại Nha Trang đâu rồi? Siêu phẩm Mì Cay Mực nguyên con khổng lồ (129K/phần ngập tràn topping) đã chính thức lên sóng tại cả 2 cơ sở Feel Chicken!

Nhìn nồi mì bốc khói nghi ngút là muốn xì xụp liền tay:
- Mực ống nguyên con khía khoanh dày căng mọng, tươi giòn ngọt lịm ngập tràn mặt nồi.
- Nước dùng kim chi Hàn Quốc chua cay đậm đà đủ 7 cấp độ thách thức vị giác, ăn kèm sợi mì Hàn dai ngon và topping xúc xích, cá viên, nấm, rau tươi đầy ụ.

Tag ngay hội cạ cứng lên kèo ghé Feel Chicken chiến thử hôm nay hoặc gọi hotline để quán ship nóng tận nhà chỉ trong 15 phút nhé!
---
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
CS1: 38 Nguyễn Đình Chiểu, Nha Trang
CS2: 35 Trần Hữu Duyệt, Vĩnh Điềm Trung, Nha Trang
Giờ mở cửa: 10:00 – 22:00
Hotline/Ship nhanh: 0796 601 106
#FeelChicken #MiCayMuc #HotTrendNhaTrang #MiCayNhaTrang #FoodNhaTrang
"""

(out_dir / "CAPTION_01_KHONG_DE_GIA_KEO_INBOX.txt").write_text(cap_no_price.strip() + "\n", encoding="utf-8")
(out_dir / "CAPTION_02_CO_GHI_129K_TRONG_BAI.txt").write_text(cap_with_129k.strip() + "\n", encoding="utf-8")

brand_dst1 = Path(r"Z:\Máy tính khác\My Computer\feel chicken\251125 MÌ CAY MỰC HOT TREND (THẬT CHÁY)")
brand_dst2 = Path(r"Z:\Máy tính khác\My Computer\feel chicken\Bai_Dang_Thang_11\25_11_Mi_Cay_Muc_Hot_Trend")
cloud_dst = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken\Mi_Cay_Muc_Hot_Trend_25_11")

for dst in [brand_dst1, brand_dst2]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(out_dir, dst)
    print("Synced to brand folder:", dst)

cloud_dst.mkdir(parents=True, exist_ok=True)
for pf in ["prepare_micay_muc_assets.py", "fix_perfect_pot_cutouts.py", "build_micay_muc_chay.py", "sync_micay_muc.py"]:
    if (base / pf).exists():
        shutil.copy2(base / pf, cloud_dst / pf)
shutil.copy2(base / "assets" / "qa_4_muc_cutouts_v2.jpg", cloud_dst / "qa_4_muc_cutouts_v2.jpg")
if (cloud_dst / "XUAT_MI_CAY_MUC_THAT_CHAY").exists():
    shutil.rmtree(cloud_dst / "XUAT_MI_CAY_MUC_THAT_CHAY")
shutil.copytree(out_dir, cloud_dst / "XUAT_MI_CAY_MUC_THAT_CHAY")
print("Synced to cloud archive:", cloud_dst)
