import shutil
from pathlib import Path

base = Path(r"d:\AI\full studio\projects\feelchicken_3posts_t11")
out_root = base / "XUAT_3_BAI_THANG_11"

cap1 = """MƯA LẠNH THÌ ĂN GÌ? MỘT TÔ MÌ CAY NÓNG HỔI LÀ CHÂN ÁI!

Nha Trang mấy hôm nay mưa lành lạnh, ngồi xì xụp nồi mì cay Hàn Quốc bốc khói nghi ngút, nước dùng kim chi chua cay đậm đà thì ấm bụng hết sảy.

Tại Feel Chicken đang có đủ 7 cấp độ cay tự chọn chỉ 55.000đ/tô (Hải sản, Bạch tuộc, Đùi gà). Muốn ăn no căng hơn thì gọi ngay Combo Feel Spicy 89.000đ gồm 01 nồi mì cay + 01 đùi gà sốt Hàn + 01 lon Coca mát lạnh.

Ghé quán ngồi ấm cúng hoặc nhắn Feel giao nóng tận nơi trong 15 phút nhé!
---
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
CS1: 38 Nguyễn Đình Chiểu, Nha Trang
CS2: 35 Trần Hữu Duyệt, Vĩnh Điềm Trung, Nha Trang
Giờ mở cửa: 10:00 – 22:00
Hotline/Ship nhanh: 0796 601 106
#FeelChicken #MiCayNhaTrang #GaRanSotHanQuoc #AnVatNhaTrang #FoodNhaTrang
"""

cap2 = """5 ĐÙI GÀ + 1 MÌ TƯƠNG ĐEN TRONG 5 PHÚT – BẠN DÁM NHẬN 1.500.000Đ?

Kèo thách đấu dành riêng cho hội "chiến thần ăn uống" Nha Trang vẫn đang chờ người tiếp theo ghi danh Bảng Vàng tại Feel Chicken!

Thể lệ cực kỳ đơn giản:
- Khẩu phần: Ăn sạch 05 đùi gà rán cỡ lớn + 01 phần mì tương đen Hàn Quốc.
- Thời gian: Cá nhân 01 người hoàn thành trong vòng 05 phút.
- Giải thưởng: Nhận ngay 1.500.000đ tiền mặt tại bàn và miễn phí 100% phần ăn. Nếu chưa vượt qua, bạn chỉ thanh toán đúng 250.000đ tiền phần ăn (vẫn no căng bụng không lo lỗ).

Tag ngay đứa bạn ăn khỏe nhất hội vào nhận kèo hoặc gọi hotline đặt lịch thi ngay hôm nay!
---
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
CS1: 38 Nguyễn Đình Chiểu, Nha Trang
CS2: 35 Trần Hữu Duyệt, Vĩnh Điềm Trung, Nha Trang
Giờ mở cửa: 10:00 – 22:00
Hotline đăng ký & đặt món: 0796 601 106
#FeelChicken #ThuThachAnUong #GaRanNhaTrang #MiTuongDen #FoodNhaTrang
"""

cap3 = """MỘT NGÀY MƯA ƯƠNG ƯƠNG, GHÉ FEEL CHICKEN ĂN NGON CHO ẤM BỤNG!

Trời mưa ương ương ngại đi xa, cứ rẽ vào Feel Chicken ngồi phòng khô ráo, gọi bàn tiệc nóng giòn vừa ra lò là vui trọn buổi chiều tối.

Từ gà rán 5 vị sốt Hàn Quốc, mì cay 7 cấp độ, tokbokki dẻo cay đến mì tương đen và mì Ý sốt bò bằm đều sẵn sàng lên mâm nóng hổi (Combo cá nhân chỉ từ 59K, Combo đôi 129K, Combo hội bạn 249K - 259K). Ngại ra đường lúc mưa thì nhấc máy alo, Feel đóng hộp giữ nhiệt giao tận nhà chỉ 15 phút!
---
FEEL CHICKEN – Gà Rán Sốt Hàn Quốc
CS1: 38 Nguyễn Đình Chiểu, Nha Trang
CS2: 35 Trần Hữu Duyệt, Vĩnh Điềm Trung, Nha Trang
Giờ mở cửa: 10:00 – 22:00
Hotline/Ship nhanh: 0796 601 106
#FeelChicken #GaRanSotHanQuoc #AnGiNhaTrang #ComboGaRan #FoodNhaTrang
"""

(out_root / "Bai_01_Mi_Cay_Ngay_Mua_4_Tam" / "CAPTION_BAI_01_MI_CAY.txt").write_text(cap1.strip() + "\n", encoding="utf-8")
(out_root / "Bai_02_Thu_Thach_5_Phut_1500K_2_Tam" / "CAPTION_BAI_02_THU_THACH_1500K.txt").write_text(cap2.strip() + "\n", encoding="utf-8")
(out_root / "Bai_03_Mua_Uong_Uong_Ghe_Feel_Am_Bung_3_Tam" / "CAPTION_BAI_03_GHE_FEEL_AM_BUNG.txt").write_text(cap3.strip() + "\n", encoding="utf-8")

brand_dir = Path(r"Z:\Máy tính khác\My Computer\feel chicken\Bai_Dang_Thang_11\3_Bai_Tiep_Theo_22_24_28_11")
brand_dir2 = Path(r"Z:\Máy tính khác\My Computer\feel chicken\3 BÀI ĐĂNG TIẾP THEO THÁNG 11")
cloud_dir = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken\Bai_Dang_Tiep_Theo_Thang_11")

for dst in [brand_dir, brand_dir2]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(out_root, dst)
    print("Synced brand folder:", dst)

cloud_dir.mkdir(parents=True, exist_ok=True)
for pyf in ["prepare_3posts_assets.py", "build_all_3_posts_t11.py", "sync_3_posts_t11.py"]:
    shutil.copy2(base / pyf, cloud_dir / pyf)
if (cloud_dir / "XUAT_3_BAI_THANG_11").exists():
    shutil.rmtree(cloud_dir / "XUAT_3_BAI_THANG_11")
shutil.copytree(out_root, cloud_dir / "XUAT_3_BAI_THANG_11")
print("Synced cloud archive:", cloud_dir)
