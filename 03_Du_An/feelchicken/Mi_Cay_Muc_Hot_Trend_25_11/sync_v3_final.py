import shutil
from pathlib import Path

base = Path(r"d:\AI\full studio\projects\feelchicken_micay_muc_chay")
out_v3 = base / "XUAT_CHATGPT_DESIGN_SACH_DEP"

cap_38ndc = """MÌ CAY MỰC NGUYÊN CON – MÓN HOT TREND ĐÃ CÓ MẶT TẠI NHA TRANG!

Team mê hải sản và đồ cay Hàn Quốc đâu rồi? Siêu phẩm Mì Cay Mực nguyên con đang gây sốt đã chính thức lên kệ tại Feel Chicken – 38 Nguyễn Đình Chiểu!

Tô mì nóng hổi bốc khói nhìn là muốn xì xụp ngay:
- Mực ống tươi nguyên con khía khoanh dày căng mọng, giòn ngọt sần sật.
- Sợi mì Hàn dai ngon quyện cùng nước dùng kim chi chua cay đậm đà đủ 7 cấp độ thách thức vị giác, đầy ụ cá viên, xúc xích và rau tươi.

Rủ ngay hội bạn ghé 38 Nguyễn Đình Chiểu thưởng thức nóng tại bàn hoặc nhắn tin/gọi hotline để Feel ship tận nơi trong 15 phút nhé!
---
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
Địa chỉ phục vụ món: 38 Nguyễn Đình Chiểu, Nha Trang
Giờ mở cửa: 10:00 – 22:00
Hotline/Ship nhanh: 0796 601 106
#FeelChicken #MiCayMuc #HotTrendNhaTrang #38NguyenDinhChieu #FoodNhaTrang
"""

(out_v3 / "CAPTION_CHOT_38_NGUYEN_DINH_CHIEU.txt").write_text(cap_38ndc.strip() + "\n", encoding="utf-8")

dst1 = Path(r"Z:\Máy tính khác\My Computer\feel chicken\251125 MÌ CAY MỰC - BẢN SẠCH ĐẸP CHATGPT (38 NĐC)")
dst2 = Path(r"Z:\Máy tính khác\My Computer\feel chicken\Bai_Dang_Thang_11\25_11_Mi_Cay_Muc_ChatGPT_38NDC")
cloud = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken\Mi_Cay_Muc_Hot_Trend_25_11")

for d in [dst1, dst2]:
    d.parent.mkdir(parents=True, exist_ok=True)
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(out_v3, d)
    print("Synced:", d)

cloud.mkdir(parents=True, exist_ok=True)
for pf in ["chatgpt_design_v3.py", "polish_and_sync_v3.py", "sync_v3_final.py"]:
    if (base / pf).exists():
        shutil.copy2(base / pf, cloud / pf)
if (cloud / "XUAT_CHATGPT_DESIGN_SACH_DEP").exists():
    shutil.rmtree(cloud / "XUAT_CHATGPT_DESIGN_SACH_DEP")
shutil.copytree(out_v3, cloud / "XUAT_CHATGPT_DESIGN_SACH_DEP")
print("Synced cloud:", cloud)
