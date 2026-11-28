# -*- coding: utf-8 -*-
"""
V6 STEP 1 — CẬP NHẬT KỊCH BẢN MỚI CUỐN HÚT BÁM SÁT 100% GROUP ZALO `CONTENT HẰNG THU PHARMA` (25/11/2026)
& TỔNG HỢP GIỌNG ĐỌC MỚI `THANH THANH TVC` (`speed=1.10`, nhịp nhanh gọn trong trẻo, mỗi câu 6.5s - 8.0s -> mỗi cú cắt ~3.4s - 4.1s < 5.5s để 0% kéo giãn frame!):
- Tuân thủ tuyệt đối lưu ý pháp lý từ Group:
  + Điều Kinh HT: Đương quy, Hương phụ, Hồng hoa (TUYỆT ĐỐI KHÔNG NÊU ÍCH MẪU!).
  + Viên đặt Hằng Thu (Hộp Xanh): Cúc La Mã, Cam thảo, Niacinamide, Tinh dầu Hoa hồng, Acid Lactic + feedback thật "dịu nhẹ, nhẹ người hẳn".
  + LT Plus: Hoàng bá, Kim ngân hoa, Trà xanh, Acid Lactic (góc viêm lộ tuyến tái lại sau đốt điện/áp lạnh).
  + Gel Phụ Khang: Trinh nữ hoàng cung, Xà sàng tử, Kim ngân hoa, Khổ sâm, Lá trầu không (gói 5ml bỏ túi).
  + Romance VIP: Lô hội, Trà xanh, Vitamin E, Tinh chất Hoa hồng (dịu nhẹ chuẩn pH, dùng êm cho cả mẹ bầu ra nhiều khí hư).
  + Romance Love: Hyaluronic Acid, Collagen, Panthenol, Lô hội (khô hạn sau sinh, tiền mãn kinh).
  + Dạ Dày HT: Dạ cẩm, Chè dây, Lá khôi, Nghệ đen, Hoàng liên, Mộc hương (cà phê sáng bụng rỗng, bia rượu tiếp khách).
  + WhiteSkin: L-Glutathione, NMN, Collagen Peptide, Vitamin C, Vitamin E (sạm nám trung niên, mất đàn hồi, sáng da đón Tết).
  + Ngọc Long Hoàn: Ba kích tím, Bá bệnh, Nhung hươu, Đông trùng hạ thảo (suy giảm thể lực tuổi 35+, đau lưng mỏi gối).
  + CEO HTPM: Giá trị thật + Ưu đãi tặng 5% duy nhất năm 2026 trong tháng này!
"""
import json, math, os, shutil, sys, wave
from pathlib import Path

_omni_short_cache = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\Hang thu\AppData\Local"), "OmniVoice", "hf_cache")
os.environ["HF_HOME"] = _omni_short_cache
os.environ["HF_HUB_CACHE"] = _omni_short_cache
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import numpy as np
import torch
from faster_whisper import WhisperModel

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
V6_ROOT = Path(r"d:\AI\full studio\output\htpm-ngay-261125\12_V6_Crystal_Clear_USP")
V6_VO_ROOT = V6_ROOT / "01_Voices"
V6_VO_ROOT.mkdir(parents=True, exist_ok=True)
K6_DAY25_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026")
LOCAL_DAY25_DIR = Path(r"D:\XUẤT CAPCUT\hằng thu pharma\261125 - Ngày 25.11.2026")

vs_proj = Path(r"d:\AI\full studio\voice-studio")
sys.path.insert(0, str(vs_proj / "backend"))
sys.path.insert(0, str(vs_proj))
from services.tts_backend import get_active_tts_backend

V6_SCRIPTS = [
    # 01 — LT Plus (Góc Group 25/11: Viêm lộ tuyến tái lại sau đốt điện + Hoàng bá, Kim ngân hoa, Trà xanh, Acid Lactic)
    {
        "vkey": "v01_lt_plus",
        "caption_idx": 1,
        "caption_txt": "Từng đi đốt điện hay áp lạnh mà cảm giác ẩm ướt, khó chịu vẫn quay trở lại?\n\nViên đặt LT Plus Hằng Thu kết hợp Hoàng bá, Kim ngân hoa, Trà xanh và Acid Lactic giúp hỗ trợ kháng khuẩn, khử mùi, chăm sóc êm dịu ngay tại nhà mà vẫn giữ độ ẩm chuẩn pH tự nhiên.\n\nTháng này Hằng Thu Pharma đang có ưu đãi đặc biệt — chị nhắn ngay chữ LT PLUS để được tư vấn kín đáo 1:1 nhé!\n#HangThuPharma #LTPlus #ChamSocPhuKhoa",
        "hook_kicker": "TỪNG ĐỐT ĐIỆN VẪN TÁI LẠI?",
        "hook_hero": "Sao cứ ẩm ướt mãi?",
        "slide1_hdr": "Vì sao chăm mãi vẫn dễ tái lại?",
        "slide1_rows": [
            "Chỉ rửa bên ngoài chưa làm sạch dịch tồn đọng",
            "Mất cân bằng pH khiến vi khuẩn dễ quay lại",
            "E ngại viên đặt thông thường gây khô rát",
        ],
        "slide2_pill": "Chăm sóc chuyên sâu êm dịu tại nhà<br/>Viên Đặt LT Plus Hằng Thu",
        "pack_kicker": "HOÀNG BÁ • KIM NGÂN HOA • ACID LACTIC",
        "pack_hero": "LT Plus",
        "slide3_pills": [
            "Hoàng bá & Kim ngân hoa kháng khuẩn, khử mùi",
            "Trà xanh & Acid Lactic cân bằng độ pH tự nhiên",
            "Êm dịu thoáng sạch, không gây cảm giác khô rát",
        ],
        "segments": [
            ("vo_01", "Từng tốn kém đi đốt điện hay áp lạnh, vậy mà chỉ vài tháng sau cảm giác ẩm ướt khó chịu lại quay về?", ["đốt điện", "ẩm ướt"]),
            ("vo_02", "Bởi khi dịch bẩn tồn đọng bên trong và độ pê hát mất cân bằng, chỉ vệ sinh bên ngoài thôi sẽ rất khó dứt hẳn.", ["bên trong", "cân bằng"]),
            ("vo_03", "Để tự chăm sóc nhẹ nhàng ngay tại nhà, nhiều chị em đã chọn đồng hành cùng Viên Đặt Eo Ti Pờ Lớt Hằng Thu.", ["tại nhà", "hằng thu"]),
            ("vo_04", "Sự kết hợp của Hoàng bá, Kim ngân hoa, Trà xanh và A xít Lắc tích giúp kháng khuẩn, khử mùi mà vẫn giữ độ ẩm êm ái tự nhiên.", ["hoàng bá", "kim ngân", "độ ẩm"]),
            ("vo_05", "Êm dịu và kín đáo mỗi tuần, chị nhắn ngay Eo Ti Pờ Lớt để Hằng Thu tư vấn theo đúng cơ địa nhé.", ["êm dịu", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Từng đi <span class="cap-kw">đốt điện hay áp lạnh</span> tốn kém,', 'Sao vài tháng cảm giác <span class="cap-kw">ẩm ướt lại quay về?</span>'),
            ("vo_02", 'Khi dịch bẩn tồn đọng &amp; <span class="cap-kw">mất cân bằng pH,</span>', 'Chỉ rửa bên ngoài thôi <span class="cap-kw">rất khó êm dứt điểm.</span>'),
            ("vo_03", 'Để tự chăm sóc <span class="cap-kw">nhẹ nhàng ngay tại nhà,</span>', 'Chị em tin chọn <span class="cap-kw">Viên Đặt LT Plus Hằng Thu.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Hoàng bá, Kim ngân hoa, Trà xanh, Acid Lactic,</span>', 'Kháng khuẩn khử mùi, <span class="cap-kw">giữ độ ẩm êm ái tự nhiên!</span>'),
        ],
    },

    # 02 — Gel Phụ Khang (Góc Group 25/11: Viêm ngứa khi ngồi 8 tiếng + Trinh nữ hoàng cung, Xà sàng tử, Kim ngân hoa, Khổ sâm, Trầu không)
    {
        "vkey": "v02_gel_phu_khang",
        "caption_idx": 2,
        "caption_txt": "Ngồi văn phòng suốt 8 tiếng hay di chuyển cả ngày làm vùng nhạy cảm hầm bí, ngứa ngáy kém tự tin?\n\nGói nhỏ 5ml Gel Phụ Khang Hằng Thu chiết xuất Trinh nữ hoàng cung, Xà sàng tử, Kim ngân hoa, Khổ sâm và Lá trầu không — bỏ gọn vào túi xách, sạch êm thơm mát mọi lúc mọi nơi.\n\nNhắn ngay GEL PHỤ KHANG để Hằng Thu gửi tư vấn chi tiết nhé!\n#HangThuPharma #GelPhuKhang #GoiNho5ml",
        "hook_kicker": "NGỒI VĂN PHÒNG SUỐT 8 TIẾNG",
        "hook_hero": "Hầm bí, ngứa khó nói?",
        "slide1_hdr": "Nỗi khổ của chị em bận rộn",
        "slide1_rows": [
            "Ngồi làm việc lâu gây ẩm bí, ngứa rát khó chịu",
            "Đi làm, công tác bất tiện mang theo chai lớn",
            "Để mùi khó chịu làm mất tự tin giao tiếp",
        ],
        "slide2_pill": "Gói nhỏ 5ml nằm gọn trong túi xách<br/>Gel Phụ Khang Hằng Thu",
        "pack_kicker": "TRINH NỮ HOÀNG CUNG • TRẦU KHÔNG",
        "pack_hero": "Gel Phụ Khang",
        "slide3_pills": [
            "Trinh nữ hoàng cung, Khổ sâm & Xà sàng tử dịu êm",
            "Kim ngân hoa & Lá trầu không khử mùi, thoáng mát",
            "Gói 5ml nhỏ xinh tiện mang đi làm, đi du lịch",
        ],
        "segments": [
            ("vo_01", "Ngồi văn phòng suốt tám tiếng hay di chuyển liên tục ngoài đường, cảm giác hầm bí ngứa rát khiến chị mất tập trung?", ["văn phòng", "ngứa rát"]),
            ("vo_02", "Muốn chăm sóc giữa ngày cho thoáng sạch nhưng chẳng lẽ lại cầm theo chai dung dịch to cồng kềnh vào nhà vệ sinh công sở.", ["thoáng sạch", "cồng kềnh"]),
            ("vo_03", "Đó là lý do trong túi xách của Hằng lúc nào cũng có sẵn gói nhỏ năm mi li lít Gel Phụ Khang Hằng Thu.", ["túi xách", "phụ khang"]),
            ("vo_04", "Chiết xuất Trinh nữ hoàng cung, Xà sàng tử, Kim ngân hoa, Khổ sâm và Lá trầu không giúp làm sạch dịu nhẹ, khử mùi thơm mát tức thì.", ["hoàng cung", "trầu không", "thơm mát"]),
            ("vo_05", "Nhỏ gọn tinh tế mang theo mọi nơi, chị nhắn ngay Gel Phụ Khang để Hằng Thu gửi ưu đãi nhé.", ["nhỏ gọn", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Ngồi làm việc 8 tiếng <span class="cap-kw">hay di chuyển cả ngày,</span>', 'Cảm giác hầm bí, ngứa rát <span class="cap-kw">làm chị kém tự tin?</span>'),
            ("vo_02", 'Muốn chăm sóc giữa ngày <span class="cap-kw">cho thoáng sạch,</span>', 'Mà ngại mang theo <span class="cap-kw">chai lọ to cồng kềnh!</span>'),
            ("vo_03", 'Trong túi xách của Hằng <span class="cap-kw">luôn có sẵn gói nhỏ 5ml</span>', 'Gel Phụ Khang <span class="cap-kw">Hằng Thu cực kỳ tiện lợi.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Trinh nữ hoàng cung, Khổ sâm, Trầu không,</span>', 'Làm sạch dịu nhẹ, <span class="cap-kw">khử mùi thơm mát tức thì!</span>'),
        ],
    },

    # 03 — Dạ Dày HT (Góc Group 25/11: Cà phê sáng bụng rỗng + Bia rượu tiếp khách ăn trễ + Dạ cẩm, Chè dây, Lá khôi, Nghệ đen, Hoàng liên, Mộc hương)
    {
        "vkey": "v03_da_day_ht",
        "caption_idx": 3,
        "caption_txt": "Sáng vội ly cà phê lúc bụng rỗng, tối tiếp khách ăn trễ làm vùng thượng vị nóng rát, ợ chua trào ngược?\n\nDạ Dày HT Hằng Thu hội tụ Dạ cẩm, Chè dây, Lá khôi, Nghệ đen, Hoàng liên và Mộc hương — hỗ trợ giảm acid dịch vị, xoa dịu và bảo vệ niêm mạc dạ dày êm khỏe.\n\nNhắn ngay DẠ DÀY HT để nhận tư vấn liệu trình phù hợp nhé!\n#HangThuPharma #DaDayHT #EmThuongVi",
        "hook_kicker": "CÀ PHÊ BỤNG ĐÓI • TIẾP KHÁCH ĂN TRỄ",
        "hook_hero": "Nóng rát thượng vị?",
        "slide1_hdr": "Thói quen bào mòn niêm mạc dạ dày",
        "slide1_rows": [
            "Cà phê sáng lúc bụng rỗng làm tăng tiết acid",
            "Tiếp khách bia rượu, ăn trễ gây kích ứng niêm mạc",
            "Ợ hơi, ợ chua, nóng rát thượng vị mất ngủ đêm",
        ],
        "slide2_pill": "Xoa dịu & bảo vệ niêm mạc mỗi ngày<br/>Dạ Dày HT Hằng Thu",
        "pack_kicker": "DẠ CẨM • CHÈ DÂY • LÁ KHÔI • NGHỆ ĐEN",
        "pack_hero": "Dạ Dày HT",
        "slide3_pills": [
            "Dạ cẩm, Chè dây & Lá khôi trung hòa acid dịch vị",
            "Nghệ đen, Hoàng liên & Mộc hương dịu êm niêm mạc",
            "Hỗ trợ giảm trào ngược, đầy chướng, đau thượng vị",
        ],
        "segments": [
            ("vo_01", "Sáng nhấp vội ly cà phê đá khi bụng rỗng, tối lại ăn trễ tiếp khách khiến vùng thượng vị nóng rát âm ỉ?", ["cà phê", "thượng vị"]),
            ("vo_02", "Khi a xít dịch vị dư thừa kích ứng niêm mạc, cơn ợ chua đầy chướng không chỉ làm ngày mệt mỏi mà đêm cũng mất ngon giấc.", ["niêm mạc", "ợ chua"]),
            ("vo_03", "Để giữ chiếc bụng êm khỏe cho cả gia đình, trong bếp nhà Hằng luôn có Thực Phẩm Bảo Vệ Sức Khỏe Dạ Dày Hát Tê.", ["êm khỏe", "dạ dày"]),
            ("vo_04", "Hội tụ sáu vị thảo mộc quý Dạ cẩm, Chè dây, Lá khôi, Nghệ đen, Hoàng liên và Mộc hương giúp giảm a xít và bảo vệ niêm mạc dạ dày.", ["dạ cẩm", "chè dây", "niêm mạc"]),
            ("vo_05", "Ăn ngon ngủ trọn giấc mỗi ngày, anh chị nhắn ngay Dạ Dày Hát Tê cho Hằng Thu nhé.", ["ăn ngon", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Sáng vội <span class="cap-kw">cà phê bụng rỗng,</span> trưa tối ăn thất thường,', 'Khiến vùng thượng vị <span class="cap-kw">nóng rát âm ỉ?</span>'),
            ("vo_02", 'Acid dư thừa kích ứng <span class="cap-kw">gây ợ chua, trào ngược,</span>', 'Làm ngày kém tập trung, <span class="cap-kw">đêm trằn trọc khó ngủ.</span>'),
            ("vo_03", 'Bí quyết giữ bụng êm khỏe <span class="cap-kw">trong bếp nhà Hằng</span>', 'Chính là thảo mộc <span class="cap-kw">Dạ Dày HT Hằng Thu.</span>'),
            ("vo_04", 'Hội tụ <span class="cap-kw">Dạ cẩm, Chè dây, Lá khôi, Nghệ đen,</span>', 'Giúp giảm acid &amp; <span class="cap-kw">bảo vệ niêm mạc êm ái!</span>'),
        ],
    },

    # 04 — Điều Kinh HT (Góc Group 25/11: Kinh ra ít chỉ 1-2 ngày + Đương quy, Hương phụ, Hồng hoa — 0% ÍCH MẪU!)
    {
        "vkey": "v04_dieu_kinh_ht",
        "caption_idx": 4,
        "caption_txt": "Sau tuổi 30 thấy kỳ dâu thưa dần, mỗi tháng chỉ ra 1–2 ngày đã hết kèm đau bụng âm ỉ, tay chân lạnh?\n\nViên uống Điều Kinh HT Hằng Thu kết hợp Đương quy, Hương phụ, Hồng hoa giúp bổ huyết, hoạt huyết, hỗ trợ điều hòa chu kỳ đều đặn và nuôi dưỡng sắc diện hồng hào tươi tắn.\n\nChị nhắn ngay ĐIỀU KINH HT để Hằng Thu tư vấn riêng nhé!\n#HangThuPharma #DieuKinhHT #BoHuyetDieuKinh",
        "hook_kicker": "KỲ DÂU CHỈ 1–2 NGÀY ĐÃ HẾT?",
        "hook_hero": "Kinh ít, chu kỳ lệch?",
        "slide1_hdr": "Tín hiệu khí huyết suy giảm ở phụ nữ",
        "slide1_rows": [
            "Lượng kinh ít dần, chỉ 1–2 ngày đã vội sạch",
            "Chu kỳ tháng sớm tháng muộn, bụng dưới đau âm ỉ",
            "Tay chân hay lạnh, sắc diện nhợt nhạt kém tươi",
        ],
        "slide2_pill": "Bồi bổ khí huyết thông suốt từ gốc<br/>Điều Kinh HT Hằng Thu",
        "pack_kicker": "ĐƯƠNG QUY • HƯƠNG PHỤ • HỒNG HOA",
        "pack_hero": "Điều Kinh HT",
        "slide3_pills": [
            "Đương quy, Hương phụ & Hồng hoa bổ huyết, hoạt huyết",
            "Hỗ trợ điều hòa kinh nguyệt đều đặn tự nhiên",
            "Giảm đau bụng kinh, nuôi làn da hồng hào rạng rỡ",
        ],
        "segments": [
            ("vo_01", "Nhiều chị sau tuổi ba mươi thấy kỳ dâu chỉ một hai ngày đã hết sạch lại tưởng thế là khỏe và gọn nhẹ?", ["ba mươi", "hết sạch"]),
            ("vo_02", "Thực ra kinh nguyệt ít dần kèm đau bụng âm ỉ, tay chân lạnh là lời nhắc khí huyết bên trong đang kém lưu thông.", ["khí huyết", "lưu thông"]),
            ("vo_03", "Muốn phụ nữ tươi nhuận như hoa được tưới nước, Hằng luôn bồi bổ đều đặn cùng Viên Uống Điều Kinh Hát Tê.", ["tươi nhuận", "điều kinh"]),
            ("vo_04", "Bảng thành phần từ Đương quy, Hương phụ và Hồng hoa giúp bổ huyết, lưu thông khí huyết, hỗ trợ chu kỳ đều đặn và êm dịu.", ["đương quy", "hương phụ", "hồng hoa"]),
            ("vo_05", "Khí huyết đầy đủ thì sắc diện mới hồng hào, chị nhắn ngay Điều Kinh Hát Tê cho Hằng Thu nhé.", ["hồng hào", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Kỳ dâu chỉ <span class="cap-kw">1–2 ngày đã hết sạch,</span>', 'Nhiều chị sau tuổi 30 <span class="cap-kw">lại tưởng thế là khỏe?</span>'),
            ("vo_02", 'Kinh ít kèm đau bụng, <span class="cap-kw">tay chân hay lạnh</span>', 'Là tín hiệu <span class="cap-kw">khí huyết đang kém lưu thông!</span>'),
            ("vo_03", 'Muốn cơ thể tươi nhuận, <span class="cap-kw">Hằng bồi bổ từ gốc</span>', 'Cùng Viên Uống <span class="cap-kw">Điều Kinh HT Hằng Thu.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Đương quy, Hương phụ &amp; Hồng hoa</span> quý,', 'Bổ huyết lưu thông, <span class="cap-kw">cho chu kỳ đều đặn êm ái!</span>'),
        ],
    },

    # 05 — DDVS Romance VIP (Góc Group 25/11: Mẹ bầu cuối kỳ / ra nhiều khí hư + Lô hội, Trà xanh, Vitamin E, Tinh chất Hoa hồng)
    {
        "vkey": "v05_romance_vip",
        "caption_idx": 5,
        "caption_txt": "Ngày nắng nóng hay các mẹ bầu cuối thai kỳ ra nhiều khí hư ẩm ướt, rửa nhiều lần bằng xà phòng mạnh lại càng khô rát?\n\nDung dịch Romance VIP Hằng Thu từ Lô hội, Trà xanh, Vitamin E và Tinh chất Hoa hồng — làm sạch êm dịu chuẩn pH, dưỡng ẩm mềm mịn, an toàn lành tính cho cả mẹ bầu.\n\nNhắn ngay ROMANCE VIP để Hằng Thu gửi tư vấn nhé!\n#HangThuPharma #RomanceVIP #DiuNheChuanPH",
        "hook_kicker": "RA NHIỀU KHÍ HƯ • MẸ BẦU NHẠY CẢM",
        "hook_hero": "Rửa nhiều lại khô rát?",
        "slide1_hdr": "Sai lầm khi vùng nhạy cảm ẩm ướt",
        "slide1_rows": [
            "Dùng dung dịch tẩy mạnh làm mất màng ẩm bảo vệ",
            "Mẹ bầu & da nhạy cảm dễ kích ứng bởi hóa chất gắt",
            "Càng rửa nhiều lần càng khô căng, bí bách quay lại",
        ],
        "slide2_pill": "Sạch thoáng chuẩn pH, lành tính cho cả mẹ bầu<br/>Romance VIP Hằng Thu",
        "pack_kicker": "LÔ HỘI • TRÀ XANH • VITAMIN E • HOA HỒNG",
        "pack_hero": "Romance VIP",
        "slide3_pills": [
            "Lô hội & Trà xanh làm sạch êm dịu, ngăn mùi hôi",
            "Vitamin E & Tinh chất Hoa hồng cấp ẩm mềm mịn",
            "Chuẩn độ pH tự nhiên, an toàn cho cả phụ nữ mang thai",
        ],
        "segments": [
            ("vo_01", "Những ngày ra nhiều khí hư hay các mẹ bầu cuối thai kỳ nhạy cảm, sao càng rửa nhiều lần lại càng thấy khô căng khó chịu?", ["khí hư", "khô căng"]),
            ("vo_02", "Bởi các chất tẩy bọt mạnh vô tình cuốn trôi luôn lớp màng ẩm tự nhiên, khiến vùng da mỏng manh dễ kích ứng hơn.", ["tự nhiên", "kích ứng"]),
            ("vo_03", "Bí quyết nâng niu dịu nhẹ chuẩn pê hát mỗi ngày của Hằng chính là Tinh Chất Thảo Dược Rô Man Vi Ai Pi.", ["dịu nhẹ", "tinh chất"]),
            ("vo_04", "Chiết xuất Lô hội, Trà xanh, Vi ta min E và Tinh chất Hoa hồng giúp làm sạch thoáng, ngăn mùi mà vẫn mềm mịn, lành tính cho cả mẹ bầu.", ["lô hội", "trà xanh", "hoa hồng"]),
            ("vo_05", "Dịu êm suốt hai mươi tư giờ, chị nhắn ngay Rô Man Vi Ai Pi để Hằng Thu gửi trao nhé.", ["dịu êm", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Ngày ra nhiều khí hư hay <span class="cap-kw">mẹ bầu nhạy cảm,</span>', 'Sao càng rửa nhiều lần <span class="cap-kw">lại càng khô rát?</span>'),
            ("vo_02", 'Chất tẩy mạnh cuốn trôi <span class="cap-kw">màng ẩm tự nhiên,</span>', 'Làm vùng da mỏng manh <span class="cap-kw">dễ kích ứng, bí bách.</span>'),
            ("vo_03", 'Bí quyết làm sạch <span class="cap-kw">dịu nhẹ chuẩn pH</span>', 'Chính là tinh chất <span class="cap-kw">Romance VIP Hằng Thu.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Lô hội, Trà xanh, Vitamin E &amp; Hoa hồng,</span>', 'Sạch thơm mềm mịn, <span class="cap-kw">lành tính cho cả mẹ bầu!</span>'),
        ],
    },

    # 06 — Legend WhiteSkin (Góc Group 25/11: Sạm nám trung niên, nếp nhăn, mất đàn hồi + L-Glutathione, NMN, Collagen Peptide, Vitamin C, E)
    {
        "vkey": "v06_whiteskin",
        "caption_idx": 6,
        "caption_txt": "Bước qua tuổi 30, thoa kem chống nắng kỹ mấy vẫn thấy vết sạm nám đậm dần, nền da khô và kém đàn hồi?\n\nViên uống Legend WhiteSkin hội tụ L-Glutathione, NMN, Collagen Peptide cùng Vitamin C & E — chống oxy hóa đa tầng, nuôi làn da sáng mịn căng mướt rạng rỡ đón Tết.\n\nNhắn ngay WHITESKIN để nhận liệu trình sáng da từ gốc nhé!\n#HangThuPharma #LegendWhiteSkin #SangMinTuGoc",
        "hook_kicker": "SẠM NÁM & DA KÉM ĐÀN HỒI TUỔI 30+",
        "hook_hero": "Thoa kem sao chưa đủ?",
        "slide1_hdr": "Vì sao làn da sau tuổi 30 nhanh xuống sắc?",
        "slide1_rows": [
            "Hắc sắc tố melanin tích tụ sâu dưới tầng biểu bì",
            "Suy giảm Collagen làm da khô, kém độ căng mướt",
            "Chỉ che nắng bên ngoài chưa nuôi khỏe nền da từ gốc",
        ],
        "slide2_pill": "Dưỡng sáng & trẻ hóa nền da từ bên trong<br/>Legend WhiteSkin",
        "pack_kicker": "L-GLUTATHIONE • NMN • COLLAGEN PEPTIDE",
        "pack_hero": "WhiteSkin",
        "slide3_pills": [
            "L-Glutathione & Vitamin C hỗ trợ mờ sạm nám, sáng da",
            "NMN & Collagen Peptide tăng độ đàn hồi căng mịn",
            "Vitamin E chống oxy hóa, bảo vệ da trước tia UV",
        ],
        "segments": [
            ("vo_01", "Bước qua tuổi ba mươi, nhiều chị giật mình khi chụp cam thường thấy vết sạm nám rõ dần và làn da mất đi độ căng mịn?", ["ba mươi", "sạm nám"]),
            ("vo_02", "Khi co la gen suy giảm và sắc tố sậm màu hình thành từ tầng sâu, chỉ thoa kem bên ngoài thôi thật sự chưa đủ.", ["tầng sâu", "bên ngoài"]),
            ("vo_03", "Mỗi buổi sáng, Hằng luôn dành ba mươi giây nuôi dưỡng làn da từ gốc cùng Viên Uống Lê Gần Goai Sờ Kin.", ["buổi sáng", "làn da"]),
            ("vo_04", "Sự cộng hưởng của Lờ Glu ta thi on, En Em En, Co la gen Pép tai cùng Vi ta min C và E giúp chống ô xy hóa, dưỡng da sáng trong căng mướt.", ["sáng trong", "căng mướt"]),
            ("vo_05", "Tự tin làn da rạng rỡ đón Tết, chị nhắn ngay Goai Sờ Kin để Hằng Thu tư vấn liệu trình nhé.", ["rạng rỡ", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Qua tuổi 30 chụp <span class="cap-kw">cam thường dưới nắng,</span>', 'Thấy sạm nám rõ dần &amp; <span class="cap-kw">da kém đàn hồi?</span>'),
            ("vo_02", 'Khi sắc tố sậm màu <span class="cap-kw">tích tụ từ tầng sâu,</span>', 'Chỉ thoa kem bên ngoài <span class="cap-kw">thật sự chưa đủ!</span>'),
            ("vo_03", 'Mỗi sáng Hằng luôn <span class="cap-kw">nuôi khỏe nền da từ gốc</span>', 'Cùng Viên Uống <span class="cap-kw">Legend WhiteSkin Hằng Thu.</span>'),
            ("vo_04", 'Hội tụ <span class="cap-kw">L-Glutathione, NMN, Collagen Peptide,</span>', 'Chống oxy hóa, dưỡng da <span class="cap-kw">sáng trong căng mướt!</span>'),
        ],
    },

    # 07 — Viên đặt phụ khoa Hằng Thu Hộp Xanh (Góc Group 25/11: Mùi hôi mất cân bằng vi sinh + Cúc La Mã, Cam thảo, Niacinamide, Hoa hồng, Acid Lactic + Feedback "nhẹ người hẳn")
    {
        "vkey": "v07_vien_dat_xanh",
        "caption_idx": 7,
        "caption_txt": "Khí hư có mùi khó nói do mất cân bằng vi sinh vùng nhạy cảm sau sinh làm chị ngại ngần bên chồng?\n\nViên đặt phụ khoa Hằng Thu kết hợp Cúc La Mã, Cam thảo, Niacinamide, Tinh dầu Hoa hồng & Acid Lactic — dịu nhẹ, an toàn, làm sạch thoáng để chị thấy nhẹ người hẳn như hàng ngàn phản hồi thật mỗi ngày.\n\nNhắn ngay VIÊN ĐẶT để Hằng Thu tư vấn kín đáo 1:1 nhé!\n#HangThuPharma #VienDatHangThu #PhuNuSauSinh",
        "hook_kicker": "MẤT CÂN BẰNG VI SINH SAU SINH",
        "hook_hero": "Khí hư, mùi khó nói?",
        "slide1_hdr": "Nỗi niềm khiến chị em khép mình",
        "slide1_rows": [
            "Mất cân bằng hệ vi sinh gây khí hư & mùi khó chịu",
            "Cảm giác kém săn chắc, ẩm ướt sau sinh nở",
            "Ngại chia sẻ, mất tự tin khi gần gũi bạn đời",
        ],
        "slide2_pill": "Dịu nhẹ an toàn, sạch thoáng nhẹ người<br/>Viên Đặt Phụ Khoa Hằng Thu",
        "pack_kicker": "CÚC LA MÃ • CAM THẢO • ACID LACTIC",
        "pack_hero": "Viên Đặt Hằng Thu",
        "slide3_pills": [
            "Cúc La Mã & Cam thảo làm dịu êm vùng nhạy cảm",
            "Acid Lactic cân bằng hệ vi sinh & độ pH tự nhiên",
            "Niacinamide & Hoa hồng dưỡng sáng hồng, săn khít",
        ],
        "segments": [
            ("vo_01", "Sau sinh nở, cảm giác khí hư có mùi do mất cân bằng vi sinh khiến không ít chị âm thầm tự ti mỗi khi gần chồng.", ["sau sinh", "vi sinh"]),
            ("vo_02", "Đừng chịu đựng một mình chị nhé, vì khi vùng nhạy cảm được làm sạch đúng cách, cơ thể sẽ nhẹ nhõm hơn rất nhiều.", ["đúng cách", "nhẹ nhõm"]),
            ("vo_03", "Sáng nay Hằng lại nhận thêm phản hồi khách khen Viên Đặt Phụ Khoa Hằng Thu dùng dịu nhẹ, sạch thoáng thấy nhẹ người hẳn.", ["phản hồi", "dịu nhẹ", "hằng thu"]),
            ("vo_04", "Công thức từ Cúc La Mã, Cam thảo, Ni a ci na mai, Tinh dầu Hoa hồng và A xít Lắc tích giúp sạch khít êm ái và cân bằng pê hát tự nhiên.", ["cúc la mã", "cam thảo", "tự nhiên"]),
            ("vo_05", "Lấy lại sự tự tin trọn vẹn, chị nhắn ngay chữ Viên Đặt để Hằng Thu đồng hành kín đáo nhé.", ["tự tin", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Sau sinh mất cân bằng vi sinh <span class="cap-kw">gây khí hư, mùi khó nói,</span>', 'Khiến nhiều chị <span class="cap-kw">âm thầm tự ti bên chồng?</span>'),
            ("vo_02", 'Đừng giữ nỗi lo một mình, <span class="cap-kw">chăm sóc đúng cách</span>', 'Sẽ giúp cơ thể <span class="cap-kw">thoáng sạch, nhẹ nhõm hơn hẳn!</span>'),
            ("vo_03", 'Khách phản hồi dùng <span class="cap-kw">Viên Đặt Hằng Thu dịu nhẹ,</span>', 'Đào thải sạch thoáng, <span class="cap-kw">thấy nhẹ người hẳn ra!</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Cúc La Mã, Cam thảo, Hoa hồng, Acid Lactic,</span>', 'Hỗ trợ sạch khít &amp; <span class="cap-kw">cân bằng pH tự nhiên!</span>'),
        ],
    },

    # 08 — Romance Love (Góc Group 25/11: Khô hạn sau sinh / tiền mãn kinh + Hyaluronic Acid, Collagen, Panthenol, Lô hội)
    {
        "vkey": "v08_romance_love",
        "caption_idx": 8,
        "caption_txt": "Khô hạn sau sinh hay giai đoạn tiền mãn kinh khiến chuyện vợ chồng trở thành nỗi sợ đau rát?\n\nViên dưỡng Romance Love Hằng Thu giàu Hyaluronic Acid (HA), Collagen, Panthenol và Lô hội — cấp ẩm chuyên sâu mềm mịn tự nhiên để giữ trọn lửa yêu hạnh phúc.\n\nChị nhắn riêng chữ ROMANCE LOVE để được tư vấn hoàn toàn bảo mật nhé!\n#HangThuPharma #RomanceLove #CapAmGiuLuaYeu",
        "hook_kicker": "KHÔ HẠN SAU SINH & TIỀN MÃN KINH",
        "hook_hero": "Sợ rát, ngại gần chồng?",
        "slide1_hdr": "Rào cản thầm lặng làm nguội lửa yêu",
        "slide1_rows": [
            "Nội tiết thay đổi gây khô hạn, đau rát khi gần gũi",
            "Phụ nữ sau sinh & tiền mãn kinh âm thầm né tránh",
            "Để lâu dễ tạo khoảng cách lạnh nhạt trong hôn nhân",
        ],
        "slide2_pill": "Cấp ẩm chuyên sâu mềm mịn tự nhiên<br/>Romance Love Hằng Thu",
        "pack_kicker": "HYALURONIC ACID • COLLAGEN • PANTHENOL",
        "pack_hero": "Romance Love",
        "slide3_pills": [
            "Hyaluronic Acid (HA) & Lô hội cấp ẩm dồi dào êm dịu",
            "Collagen & Panthenol nuôi dưỡng niêm mạc mềm mại",
            "Xóa tan nỗi lo khô hạn, giữ trọn cảm xúc lứa đôi",
        ],
        "segments": [
            ("vo_01", "Sau sinh hay bước vào giai đoạn tiền mãn kinh, cảm giác khô hạn đau rát khiến nhiều chị sợ hãi mỗi khi gần gũi chồng?", ["sau sinh", "khô hạn"]),
            ("vo_02", "Không phải vì tình cảm nhạt phai, mà chính sự thiếu hụt độ ẩm tự nhiên đang âm thầm đẩy hai vợ chồng ra xa.", ["độ ẩm", "vợ chồng"]),
            ("vo_03", "Biết yêu chiều bản thân tinh tế, chị hãy để Viên Dưỡng Rô Man Lốp Hằng Thu đánh thức lại sự mềm mại.", ["tinh tế", "mềm mại"]),
            ("vo_04", "Giàu Hy a lu rô níc A xít, Co la gen, Pan the non và Lô hội giúp cấp ẩm chuyên sâu, nuôi dưỡng vùng nhạy cảm mềm mịn tươi trẻ.", ["lô hội", "cấp ẩm", "mềm mịn"]),
            ("vo_05", "Giữ lửa hôn nhân nồng nàn như thuở đầu, chị nhắn riêng Rô Man Lốp cho Hằng Thu nhé.", ["hôn nhân", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Sau sinh hay bước sang <span class="cap-kw">tuổi tiền mãn kinh,</span>', 'Cảm giác khô hạn làm chị <span class="cap-kw">e ngại gần chồng?</span>'),
            ("vo_02", 'Không phải hết thương, <span class="cap-kw">mà thiếu độ ẩm tự nhiên</span>', 'Đang âm thầm tạo <span class="cap-kw">khoảng cách vợ chồng!</span>'),
            ("vo_03", 'Yêu chiều bản thân tinh tế <span class="cap-kw">cùng bảo bối cấp ẩm</span>', 'Viên Dưỡng Trẻ Hóa <span class="cap-kw">Romance Love Hằng Thu.</span>'),
            ("vo_04", 'Giàu <span class="cap-kw">Hyaluronic Acid, Collagen, Panthenol &amp; Lô hội,</span>', 'Cấp ẩm sâu mềm mịn, <span class="cap-kw">giữ trọn lửa yêu thương!</span>'),
        ],
    },

    # 09 — Ngọc Long Hoàn (Góc Group 25/11: Phái mạnh suy giảm sinh lực/thể lực tuổi 35+ + Ba kích tím, Bá bệnh, Nhung hươu, Đông trùng hạ thảo)
    {
        "vkey": "v09_ngoc_long_hoan",
        "caption_idx": 9,
        "caption_txt": "Đàn ông ngoài 35 gánh vác công việc ít khi than mệt, nhưng hay đau lưng mỏi gối, hụt hơi cuối ngày?\n\nNgọc Long Hoàn Hằng Thu kết hợp Ba kích tím, Bá bệnh, Nhung hươu và Đông trùng hạ thảo — hỗ trợ bổ thận, bồi bổ nguyên khí bền vững từ gốc để giữ vững phong độ phái mạnh.\n\nNhắn ngay NGỌC LONG HOÀN để được tư vấn bảo mật 100% nhé!\n#HangThuPharma #NgocLongHoan #PhongDoPhaiManh",
        "hook_kicker": "PHÁI MẠNH NGOÀI 35 ÍT KHI THAN MỆT",
        "hook_hero": "Đau lưng, hụt thể lực?",
        "slide1_hdr": "Dấu hiệu nguyên khí suy giảm theo tuổi tác",
        "slide1_rows": [
            "Áp lực công việc làm cơ thể nhanh hụt hơi, uể oải",
            "Hay đau mỏi thắt lưng, đầu gối sau ngày dài",
            "Sinh lực & phong độ giảm dần nhưng ngại giãi bày",
        ],
        "slide2_pill": "Món quà bồi bổ nguyên khí từ người vợ tinh tế<br/>Ngọc Long Hoàn",
        "pack_kicker": "BA KÍCH TÍM • NHUNG HƯƠU • ĐÔNG TRÙNG",
        "pack_hero": "Ngọc Long Hoàn",
        "slide3_pills": [
            "Ba kích tím & Bá bệnh hỗ trợ bổ thận tráng dương",
            "Nhung hươu & Đông trùng hạ thảo bồi bổ thể lực",
            "Giảm đau lưng mỏi gối, duy trì phong độ bền bỉ",
        ],
        "segments": [
            ("vo_01", "Đàn ông ngoài ba mươi lăm gánh vác gia đình hiếm khi than mệt, nhưng tối về lại hay xoa lưng uể oải hụt hơi?", ["ba mươi lăm", "xoa lưng"]),
            ("vo_02", "Theo tuổi tác và áp lực thương trường, nguồn nguyên khí bên trong suy giảm sẽ kéo theo cả thể lực lẫn phong độ đi xuống.", ["tuổi tác", "phong độ"]),
            ("vo_03", "Người vợ tâm lý không đợi chồng nói ra mà luôn chuẩn bị sẵn Ngọc Long Hoàn Hằng Thu bên tách trà ấm.", ["tâm lý", "ngọc long"]),
            ("vo_04", "Hội tụ Ba kích tím, Bá bệnh, Nhung hươu và Đông trùng hạ thảo giúp bổ thận, giảm đau lưng mỏi gối và bồi bổ sinh lực bền bỉ từ gốc.", ["ba kích", "nhung hươu", "đông trùng"]),
            ("vo_05", "Chăm anh khỏe để giữ tổ ấm trọn niềm vui, chị nhắn ngay Ngọc Long Hoàn để Hằng Thu tư vấn bảo mật nhé.", ["tổ ấm", "bảo mật"]),
        ],
        "caps": [
            ("vo_01", 'Đàn ông ngoài 35 <span class="cap-kw">hiếm khi than mệt,</span>', 'Nhưng tối về hay <span class="cap-kw">đau lưng, hụt hơi uể oải?</span>'),
            ("vo_02", 'Áp lực &amp; tuổi tác làm <span class="cap-kw">suy giảm nguyên khí,</span>', 'Kéo theo thể lực &amp; <span class="cap-kw">phong độ giảm dần.</span>'),
            ("vo_03", 'Người vợ tâm lý luôn <span class="cap-kw">chuẩn bị bên tách trà ấm</span>', 'Món quà sức khỏe <span class="cap-kw">Ngọc Long Hoàn Hằng Thu.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Ba kích tím, Bá bệnh, Nhung hươu, Đông trùng,</span>', 'Bổ thận giảm đau mỏi, <span class="cap-kw">giữ vững phong độ bền bỉ!</span>'),
        ],
    },

    # 10 — CEO Nguyễn Thị Hằng & Hệ thống HTPM (Góc Group 25/11: Phản hồi thật + Tặng 5% duy nhất năm 2026!)
    {
        "vkey": "v10_ceo_thuong_hieu",
        "caption_idx": 10,
        "caption_txt": "Giữa thị trường bao trào lưu sớm nở tối tàn, điều gì giữ chân khách hàng suốt hơn một thập kỷ cùng Hằng Thu Pharma?\n\nĐó là chất lượng sản phẩm thật và hàng ngàn phản hồi thật mỗi ngày. Đặc biệt trong tháng này, Hằng Thu Pharma dành tặng ưu đãi 5% duy nhất trong năm 2026 cho đối tác toàn hệ thống!\n\nNhắn ngay ĐỒNG HÀNH để bứt phá cùng CEO Nguyễn Thị Hằng nhé!\n#HangThuPharma #CEONguyenThiHang #UuDai5PhanTram2026",
        "hook_kicker": "ƯU ĐÃI TẶNG 5% DUY NHẤT NĂM 2026",
        "hook_hero": "Đi đường dài nhờ đâu?",
        "slide1_hdr": "3 Giá trị thật tạo nên Hằng Thu Pharma",
        "slide1_rows": [
            "Danh mục sản phẩm thiết yếu, khách dùng phản hồi thật",
            "Quy trình đào tạo bài bản, ứng dụng công nghệ mới",
            "Đặc quyền tặng thêm 5% duy nhất năm 2026 trong tháng này",
        ],
        "slide2_pill": "Kinh doanh tử tế & bền vững cùng<br/>CEO Nguyễn Thị Hằng",
        "pack_kicker": "HỆ SINH THÁI SỨC KHỎE & SẮC ĐẸP",
        "pack_hero": "Hằng Thu Pharma",
        "slide3_pills": [
            "Trọn bộ sản phẩm phụ khoa, nội tiết, tiêu hóa, sắc đẹp",
            "Tỷ lệ khách hàng hài lòng & quay lại tái mua cao",
            "Tặng 5% duy nhất 2026 cho đối tác lên đơn tháng này",
        ],
        "segments": [
            ("vo_01", "Giữa thị trường bao trào lưu sớm nở tối tàn, điều gì giúp Hằng Thu Pharma giữ trọn niềm tin suốt hơn một thập kỷ?", ["thị trường", "hằng thu"]),
            ("vo_02", "Quảng cáo hay có thể kéo khách đến lần đầu, nhưng chỉ có chất lượng thật và phản hồi thật mới giữ khách ở lại dài lâu.", ["chất lượng", "phản hồi"]),
            ("vo_03", "Mỗi sản phẩm trao tay từ phụ khoa, nội tiết đến tiêu hóa đều được Hằng đặt trọn tâm huyết và sự tử tế.", ["tâm huyết", "tử tế"]),
            ("vo_04", "Đặc biệt trong tháng này, Hằng Thu Pharma dành tặng thêm ưu đãi năm phần trăm duy nhất của năm hai nghìn không trăm hai mươi sáu cho toàn hệ thống.", ["tháng này", "năm phần trăm"]),
            ("vo_05", "Nắm bắt cơ hội bứt phá ngay hôm nay, chị em nhắn chữ Đồng Hành để kết nối trực tiếp cùng Hằng nhé.", ["bứt phá", "đồng hành"]),
        ],
        "caps": [
            ("vo_01", 'Giữa bao trào lưu <span class="cap-kw">sớm nở tối tàn ngoài kia,</span>', 'Điều gì giữ vững <span class="cap-kw">Hằng Thu hơn một thập kỷ?</span>'),
            ("vo_02", 'Chỉ có <span class="cap-kw">chất lượng sản phẩm thật</span> &amp; phản hồi thật', 'Mới giữ trọn niềm tin <span class="cap-kw">khách hàng dài lâu!</span>'),
            ("vo_03", 'Trọn hệ sinh thái <span class="cap-kw">phụ khoa, nội tiết, tiêu hóa</span>', 'Đều gửi gắm <span class="cap-kw">tâm huyết &amp; sự tử tế của Hằng.</span>'),
            ("vo_04", 'Đặc biệt tháng này <span class="cap-kw">tặng thêm 5% duy nhất 2026</span>', 'Cho đối tác toàn hệ thống <span class="cap-kw">bứt phá doanh số!</span>'),
        ],
    },

    # 11 — Flagship Ngọc Long Hoàn (Chị Hằng chia sẻ bí quyết chăm chồng — Cảnh cuối vợ chồng uống trà trong trẻo)
    {
        "vkey": "flagship_ngoc_long_hoan",
        "caption_idx": None,
        "hook_kicker": "BÍ QUYẾT GIỮ LỬA TỔ ẤM CỦA CHỊ HẰNG",
        "hook_hero": "Chồng mệt chẳng nói ra?",
        "slide1_hdr": "Áp lực thầm lặng sau tuổi 35 của chồng",
        "slide1_rows": [
            "Thức khuya lo công việc làm hao hụt nguyên khí",
            "Đau mỏi thắt lưng, thể lực giảm nhưng ngại than",
            "Cần bồi bổ thận khí từ thảo dược chuẩn chỉnh",
        ],
        "slide2_pill": "Sự chăm sóc tinh tế mỗi sáng của Hằng<br/>Ngọc Long Hoàn",
        "pack_kicker": "BA KÍCH TÍM • BÁ BỆNH • ĐÔNG TRÙNG",
        "pack_hero": "Ngọc Long Hoàn",
        "slide3_pills": [
            "Ba kích tím & Bá bệnh hỗ trợ bổ thận, tăng sinh lực",
            "Nhung hươu & Đông trùng hạ thảo phục hồi thể lực",
            "Giảm đau lưng mỏi gối, giữ phong độ bền bỉ",
        ],
        "segments": [
            ("vo_01", "Đi qua hơn mười năm hôn nhân, Hằng hiểu đàn ông thương vợ con thường gánh hết áp lực vào lòng chứ chẳng mấy khi than mệt.", ["hôn nhân", "áp lực"]),
            ("vo_02", "Thấy ông xã sau ngày dài làm việc hay xoa nhẹ thắt lưng uể oải, thương chồng mình phải chăm từ gốc ngay khi anh chưa kịp nói.", ["ông xã", "thương chồng"]),
            ("vo_03", "Mỗi sáng bên tách trà ấm, Hằng luôn chuẩn bị đều đặn Ngọc Long Hoàn Hằng Thu để tiếp thêm sinh lực cho anh.", ["trà ấm", "ngọc long"]),
            ("vo_04", "Sự hòa quyện của Ba kích tím, Bá bệnh, Nhung hươu và Đông trùng hạ thảo giúp bổ thận, giảm đau mỏi lưng gối và giữ phong độ dẻo dai.", ["ba kích", "nhung hươu", "phong độ"]),
            ("vo_05", "Chồng khỏe mạnh vững vàng là điểm tựa bình yên nhất, các chị nhắn Ngọc Long Hoàn để Hằng tư vấn kín đáo nhé.", ["khỏe mạnh", "ngọc long"]),
        ],
        "caps": [
            ("vo_01", 'Hơn 10 năm hôn nhân, <span class="cap-kw">Hằng hiểu người đàn ông</span>', 'Gánh vác áp lực <span class="cap-kw">nhưng hiếm khi than mệt!</span>'),
            ("vo_02", 'Thấy ông xã cuối ngày <span class="cap-kw">hay đau mỏi thắt lưng,</span>', 'Thương chồng hãy <span class="cap-kw">bồi bổ ngay từ gốc!</span>'),
            ("vo_03", 'Mỗi sáng bên tách trà ấm, <span class="cap-kw">Hằng luôn chuẩn bị sẵn</span>', 'Ngọc Long Hoàn Hằng Thu <span class="cap-kw">chăm sức khỏe chồng.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Ba kích tím, Bá bệnh, Nhung hươu, Đông trùng,</span>', 'Bổ thận giảm đau lưng, <span class="cap-kw">vững vàng phong độ!</span>'),
        ],
    },

    # 12 — Flagship Điều Kinh HT (Bí quyết dưỡng khí huyết rạng rỡ của chị Hằng — 0% chồng, 0% Ích mẫu!)
    {
        "vkey": "flagship_dieu_kinh_ht",
        "caption_idx": None,
        "hook_kicker": "BÍ QUYẾT SẮC DIỆN HỒNG HÀO CỦA HẰNG",
        "hook_hero": "Tới kỳ đau bụng, kinh ít?",
        "slide1_hdr": "3 Dấu hiệu phụ nữ cần dưỡng huyết ngay",
        "slide1_rows": [
            "Đến kỳ đau bụng âm ỉ, người uể oải thiếu sức",
            "Kinh nguyệt ra ít dần, chu kỳ sớm muộn thất thường",
            "Sắc mặt kém hồng hào dù dưỡng da bên ngoài kỹ",
        ],
        "slide2_pill": "Thói quen dưỡng khí huyết mỗi ngày của Hằng<br/>Điều Kinh HT",
        "pack_kicker": "ĐƯƠNG QUY • HƯƠNG PHỤ • HỒNG HOA",
        "pack_hero": "Điều Kinh HT",
        "slide3_pills": [
            "Đương quy, Hương phụ & Hồng hoa bổ huyết từ gốc",
            "Hỗ trợ lưu thông khí huyết, điều hòa chu kỳ êm ái",
            "Giảm đau bụng ngày đèn đỏ, cho da dẻ tươi nhuận",
        ],
        "segments": [
            ("vo_01", "Nhiều chị em gặp Hằng cứ hỏi bí quyết nào để bận rộn suốt ngày mà sắc diện vẫn luôn hồng hào, đến kỳ cũng nhẹ tênh.", ["bí quyết", "hồng hào"]),
            ("vo_02", "Thật ra phụ nữ mình sau tuổi ba mươi nếu khí huyết kém lưu thông thì kỳ dâu rất dễ thưa ít, đau bụng âm ỉ và da cũng tái nhợt đi.", ["khí huyết", "đau bụng"]),
            ("vo_03", "Thay vì đợi đến kỳ mới lo, Hằng duy trì bồi bổ từ bên trong cùng Viên Uống Điều Kinh Hát Tê Hằng Thu.", ["bên trong", "điều kinh"]),
            ("vo_04", "Tinh hoa từ Đương quy, Hương phụ và Hồng hoa giúp bổ huyết, hoạt huyết, hỗ trợ điều hòa kinh nguyệt đều đặn và giảm đau bụng kinh êm ái.", ["đương quy", "hương phụ", "hồng hoa"]),
            ("vo_05", "Phụ nữ khỏe khí huyết là tự khắc rạng ngời, chị nhắn ngay Điều Kinh Hát Tê để Hằng chia sẻ liệu trình nhé.", ["rạng ngời", "điều kinh"]),
        ],
        "caps": [
            ("vo_01", 'Bận rộn suốt ngày mà <span class="cap-kw">sắc diện vẫn hồng hào,</span>', 'Mỗi tháng đến kỳ dâu <span class="cap-kw">cũng êm ái nhẹ tênh?</span>'),
            ("vo_02", 'Sau tuổi 30 nếu <span class="cap-kw">khí huyết kém lưu thông,</span>', 'Kỳ dâu dễ thưa ít, <span class="cap-kw">đau bụng &amp; kém tươi tắn!</span>'),
            ("vo_03", 'Bí quyết của Hằng là <span class="cap-kw">chủ động bồi bổ từ gốc</span>', 'Cùng Viên Uống <span class="cap-kw">Điều Kinh HT Hằng Thu.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Đương quy, Hương phụ &amp; Hồng hoa</span> bổ huyết,', 'Điều hòa chu kỳ êm dịu, <span class="cap-kw">nuôi nét xuân rạng rỡ!</span>'),
        ],
    },
]


def trim_and_normalize(tensor_or_arr, sample_rate):
    arr = tensor_or_arr.detach().to("cpu").float().numpy().squeeze().astype(np.float32) if hasattr(tensor_or_arr, "detach") else np.asarray(tensor_or_arr, dtype=np.float32).squeeze()
    if arr.ndim > 1:
        arr = arr.mean(axis=int(np.argmin(arr.shape)))
    abs_arr = np.abs(arr)
    peak = float(np.max(abs_arr)) if len(abs_arr) > 0 else 0.0
    if peak > 1e-4:
        arr = arr * (0.92 / peak)
        abs_arr = np.abs(arr)
    idx = np.where(abs_arr > 0.012)[0]
    if len(idx) > 10:
        arr = arr[max(0, int(idx[0]) - int(0.025 * sample_rate)):min(len(arr), int(idx[-1]) + int(0.05 * sample_rate))]
    return arr


def save_wav(path, pcm_f32, sample_rate):
    pcm = np.clip(np.copy(pcm_f32), -1.0, 1.0)
    fi, fo = min(int(0.025 * sample_rate), len(pcm) // 4), min(int(0.045 * sample_rate), len(pcm) // 4)
    if fi > 0:
        pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        pcm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    pcm16 = (pcm * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())


def main():
    # Update 10 Captions in K6 & Local immediately with Group-synced copy!
    for sc in V6_SCRIPTS:
        cidx = sc.get("caption_idx")
        if cidx:
            for d in (K6_DAY25_DIR, LOCAL_DAY25_DIR):
                d.mkdir(parents=True, exist_ok=True)
                (d / f"Caption_261125_{cidx:02d}.txt").write_text(sc["caption_txt"], encoding="utf-8")

    # Save full V6 script metadata JSON for the renderer
    (V6_ROOT / "v6_scripts_spec.json").write_text(json.dumps(V6_SCRIPTS, ensure_ascii=False, indent=2), encoding="utf-8")

    meta = json.loads((VOICE_BUNDLE_DIR / "profile_metadata.json").read_text(encoding="utf-8"))
    ref_audio = str(VOICE_BUNDLE_DIR / meta["ref_audio_filename"])
    ref_text = meta["ref_text"]
    backend = get_active_tts_backend()
    asr = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=6, download_root=r"C:\Users\Hang thu\.cache\huggingface\hub")

    for sc in V6_SCRIPTS:
        vkey = sc["vkey"]
        vdir = V6_VO_ROOT / vkey
        vdir.mkdir(parents=True, exist_ok=True)
        man_p = vdir / "vo_manifest.json"
        if man_p.exists() and (vdir / "vo_05.wav").exists():
            print(f"[VO CACHED] {vkey}", flush=True)
            continue

        segs_out = []
        prev_end = 0.0
        for idx, (seg_id, tts_text, kw_list) in enumerate(sc["segments"]):
            best_path, best_dur, best_tr, best_sc = None, 0.0, "", -1
            for sd in [2028, 369]:
                torch.manual_seed(sd)
                # Speed 1.11 for brisk, natural, engaging pacing (honoring CT Hằng's feedback!)
                wav_t = backend.generate(text=tts_text, ref_audio=ref_audio, ref_text=ref_text, language="vi", num_step=24, guidance_scale=2.0, speed=1.11)
                sr = int(getattr(backend, "sample_rate", 24000))
                arr = trim_and_normalize(wav_t, sr)
                cp = vdir / f"{seg_id}_cand_{sd}.wav"
                save_wav(cp, arr, sr)
                segs_asr, _ = asr.transcribe(str(cp), language="vi", beam_size=1)
                tr = " ".join(s.text.strip() for s in segs_asr).strip()
                hits = sum(1 for k in kw_list if k in tr.lower())
                if hits > best_sc:
                    best_sc, best_path, best_dur, best_tr = hits, cp, round(len(arr) / float(sr), 3), tr
                if hits == len(kw_list):
                    break
            seg_path = vdir / f"{seg_id}.wav"
            shutil.copy2(best_path, seg_path)
            for c in vdir.glob(f"{seg_id}_cand_*.wav"):
                c.unlink(missing_ok=True)

            # Snap to 0.25s (6 frames @ 24fps), tight brisk gap 0.34s!
            raw_shot_dur = best_dur + (0.65 if idx == 4 else 0.36)
            shot_dur_s = max(4.25 if idx == 4 else 3.50, round(math.ceil(raw_shot_dur * 4.0) / 4.0, 2))
            shot_start_s = 0.0 if idx == 0 else prev_end
            segs_out.append({
                "id": seg_id,
                "tts_text": tts_text,
                "whisper_verified": best_tr,
                "shot_start_s": shot_start_s,
                "shot_duration_s": shot_dur_s,
                "shot_end_s": round(shot_start_s + shot_dur_s, 2),
                "start_s": round(shot_start_s + 0.14, 3),
                "duration_s": best_dur,
                "end_s": round(shot_start_s + 0.14 + best_dur, 3),
            })
            prev_end = round(shot_start_s + shot_dur_s, 2)

        man_p.write_text(json.dumps({
            "vkey": vkey,
            "total_duration_s": prev_end,
            "fps": 24,
            "segments": segs_out,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[VO OK] {vkey} -> {prev_end:.2f}s (10 cuts avg {prev_end/10:.2f}s/cut)", flush=True)

    print("=== ALL 12 GROUP-UPDATED V6 VOICEOVERS READY ===", flush=True)


if __name__ == "__main__":
    main()
