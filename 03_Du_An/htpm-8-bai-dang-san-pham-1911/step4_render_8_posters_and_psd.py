# -*- coding: utf-8 -*-
"""
Render 8 Commercial Key-Visual Posters (1200x1500 4:5 Portrait) + 8 Multi-Layer .PSD Files
for Hằng Thu Pharma using 100% Real Studio Product Cutouts + Bespoke 8K Podium Stages + 2-Layer Gradient Typography.
"""
import base64, json, os, shutil
import cv2
import numpy as np
from PIL import Image, ImageCms, ImageEnhance, ImageFilter
import pytoshop
from pytoshop.user import nested_layers
from pytoshop import enums

PROJ_DIR  = r"d:\AI\full studio\projects\htpm_8_posts_1911"
CUT_DIR   = os.path.join(PROJ_DIR, "assets", "cutouts")
STAGE_DIR = os.path.join(PROJ_DIR, "assets", "stages")
HTML_DIR  = os.path.join(PROJ_DIR, "html_layers")
OUT_PNG   = os.path.join(PROJ_DIR, "Poster_PNG_1200x1500")
OUT_JPG   = os.path.join(PROJ_DIR, "Poster_JPG_sRGB")
OUT_PSD   = os.path.join(PROJ_DIR, "File_PSD_3_Layer_Photoshop")
CHECK_DIR = os.path.join(PROJ_DIR, "check")

FONTS_DIR = r"d:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi"

for d in (HTML_DIR, OUT_PNG, OUT_JPG, OUT_PSD, CHECK_DIR):
    os.makedirs(d, exist_ok=True)

SRGB_PROFILE = ImageCms.createProfile("sRGB")
SRGB_BYTES = ImageCms.ImageCmsProfile(SRGB_PROFILE).tobytes()

def b64_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

POSTER_SPECS = [
    {
        "idx": 1,
        "slug": "01_Vien_Uong_Dieu_Kinh_Bo_Trung_Hang_Thu",
        "stage": "stage_01.jpg",
        "cutout": "01_dieu_kinh.png",
        "prod_cx": 815, "prod_by": 980, "prod_max_w": 500, "prod_max_h": 485,
        "dark_mode": False,
        "cat_badge": "CHĂM SÓC SỨC KHỎE SINH SẢN",
        "kicker": "MONG CON ĐÃ LÂU • KINH NGUYỆT THẤT THƯỜNG?",
        "headline_l1": "TRỨNG LÉP – CHẬM CON",
        "headline_l2": "ĐỪNG CHỦ QUAN CHỜ ĐỢI!",
        "grad_stops": ("#9E0B41", "#D81B60", "#AD1457", "#880E4F", "#56062B"),
        "stroke_col": "#FFFFFF",
        "shadow_rgba": "rgba(136, 14, 79, 0.26)",
        "accent": "#C2185B",
        "accent_soft": "#FCE4EC",
        "veil_rgb": "255, 245, 248",
        "pain_header": "Dấu hiệu cảnh báo buồng trứng & nội tiết:",
        "pain_icon": "warn_rose",
        "pains": [
            ("Nang trứng phát triển kém", "Trứng nhỏ (trứng lép), khó trưởng thành đúng chu kỳ"),
            ("Kinh nguyệt rối loạn thất thường", "Tháng sớm tháng trễ, lượng kinh ít, thâm đen vón cục"),
            ("Khó canh ngày rụng trứng", "Rụng trứng không đều làm giảm cơ hội thụ thai tự nhiên"),
            ("Thả tự nhiên lâu chưa có tin vui", "Cơ thể thiếu hụt khí huyết & dưỡng chất nuôi dưỡng trứng"),
        ],
        "usp_badge": "GIẢI PHÁP ĐỒNG HÀNH ĐÓN CON YÊU",
        "usp_title": "VIÊN UỐNG ĐIỀU KINH BỔ TRỨNG HẰNG THU",
        "usp_Gradient": ("#FFF6D6", "#FDE08D", "#F5B942"),
        "usp_bg": "linear-gradient(135deg, #8E0E43 0%, #C2185B 55%, #880E4F 100%)",
        "pillars": [
            "Hỗ trợ bổ huyết, điều hòa kinh nguyệt đều đặn",
            "Nuôi dưỡng trứng khỏe – Rụng trứng đều nhịp",
            "Tăng cơ hội thụ thai & sớm đón bé yêu",
        ],
        "actives": "Đương Quy • Hương Phụ • Hồng Hoa • Đan Sâm • Huyết Đằng",
        "cta_text": "INBOX ĐỂ ĐƯỢC TƯ VẤN SỨC KHỎE SINH SẢN 1:1",
    },
    {
        "idx": 2,
        "slug": "02_Vien_Dat_Phu_Khoa_LT_Plus_Hang_Thu",
        "stage": "stage_02.jpg",
        "cutout": "02_lt_plus.png",
        "prod_cx": 835, "prod_by": 995, "prod_max_w": 545, "prod_max_h": 485,
        "dark_mode": False,
        "cat_badge": "GIẢI PHÁP PHỤ KHOA CHUYÊN SÂU",
        "kicker": "NỖI ÁM ẢNH MANG TÊN VIÊM PHỤ KHOA TÁI PHÁT",
        "headline_l1": "VIÊM LỘ TUYẾN CỔ TỬ CUNG",
        "headline_l2": "KHÔNG PHẢI AI CŨNG CẦN ĐỐT!",
        "grad_stops": ("#A40E3B", "#E11D48", "#BE123C", "#9F1239", "#640922"),
        "stroke_col": "#FFFFFF",
        "shadow_rgba": "rgba(159, 18, 57, 0.25)",
        "accent": "#BE123C",
        "accent_soft": "#FFE4E6",
        "veil_rgb": "255, 246, 248",
        "pain_header": "Viêm lộ tuyến gây ra nhiều phiền toái:",
        "pain_icon": "cross_red",
        "pains": [
            ("Khí hư ra nhiều bất thường", "Dịch tiết đặc dính, màu lạ kèm mùi hôi khó chịu"),
            ("Ngứa rát, ẩm ướt vùng nhạy cảm", "Gây bức bối, mất tự tin trong công việc & giao tiếp"),
            ("Đau rát mỗi khi gần gũi", "Làm suy giảm chất lượng đời sống hạnh phúc vợ chồng"),
            ("Viêm nhiễm tái đi tái lại", "Chăm sóc chưa tới gốc khiến niêm mạc khó phục hồi"),
        ],
        "usp_badge": "PHÙ HỢP CHO CẢ LỘ TUYẾN ĐỘ 1 – ĐỘ 2 – ĐỘ 3",
        "usp_title": "VIÊN ĐẶT PHỤ KHOA LT PLUS HẰNG THU",
        "usp_Gradient": ("#FFF8DC", "#FFE082", "#F59E0B"),
        "usp_bg": "linear-gradient(135deg, #881337 0%, #BE123C 52%, #7F1D1D 100%)",
        "pillars": [
            "Hỗ trợ đào thải dịch viêm tồn đọng từ sâu bên trong",
            "Kháng khuẩn, khử mùi & cân bằng độ pH tự nhiên",
            "Tái tạo & làm lành êm dịu niêm mạc cổ tử cung",
        ],
        "actives": "Hoàng Bá • Kim Ngân Hoa • Trầu Không • Ích Mẫu • Acid Lactic",
        "cta_text": "INBOX NGAY ĐỂ NHẬN PHÁC ĐỒ CHĂM SÓC KÍN ĐÁO",
    },
    {
        "idx": 3,
        "slug": "03_Vien_Uong_Da_Day_HT_Hang_Thu",
        "stage": "stage_03.jpg",
        "cutout": "03_da_day_ht.png",
        "prod_cx": 835, "prod_by": 935, "prod_max_w": 540, "prod_max_h": 475,
        "dark_mode": False,
        "cat_badge": "CHĂM SÓC HỆ TIÊU HÓA KHỎE MẠNH",
        "kicker": "ĐỪNG BỎ QUA TÍN HIỆU CẦU CỨU TỪ DẠ DÀY!",
        "headline_l1": "TRÀO NGƯỢC DẠ DÀY",
        "headline_l2": "ĐỪNG CHỦ QUAN ĐỂ BIẾN CHỨNG!",
        "grad_stops": ("#064E3B", "#059669", "#047857", "#065F46", "#022C22"),
        "stroke_col": "#FFFFFF",
        "shadow_rgba": "rgba(6, 78, 59, 0.25)",
        "accent": "#047857",
        "accent_soft": "#D1FAE5",
        "veil_rgb": "244, 253, 248",
        "pain_header": "Bạn có đang gặp 4 dấu hiệu điển hình này?",
        "pain_icon": "fire_orange",
        "pains": [
            ("Ợ hơi, ợ chua, nóng rát vùng ngực", "Acid dịch vị trào ngược gây bỏng rát dọc thượng vị"),
            ("Đầy bụng, chướng hơi, khó tiêu", "Ăn nhanh no, ngang bụng, dễ buồn nôn sau bữa ăn"),
            ("Đắng miệng, vướng nghẹn cổ họng", "Trào ngược ban đêm làm đắng miệng, ho khan kéo dài"),
            ("Đau tức tăng lên khi ăn no hoặc nằm", "Nguy cơ dẫn đến viêm thực quản & viêm loét dạ dày"),
        ],
        "usp_badge": "THẢO MỘC DẠ CẨM & NGHỆ LÀNH TÍNH CHO DẠ DÀY",
        "usp_title": "THỰC PHẨM BẢO VỆ SỨC KHỎE DẠ DÀY HT",
        "usp_Gradient": ("#FEF9C3", "#FDE047", "#F59E0B"),
        "usp_bg": "linear-gradient(135deg, #064E3B 0%, #047857 55%, #065F46 100%)",
        "pillars": [
            "Hỗ trợ trung hòa acid, dịu nhanh ợ hơi & ợ chua",
            "Bảo vệ & phục hồi niêm mạc dạ dày – thực quản",
            "Hỗ trợ người viêm loét dạ dày, tá tràng & đại tràng",
        ],
        "actives": "Tinh Chất Dạ Cẩm • Nghệ Vàng • Thảo Mộc Bảo Vệ Niêm Mạc",
        "cta_text": "INBOX ĐỂ ĐƯỢC TƯ VẤN CHĂM SÓC DẠ DÀY ÊM KHỎE",
    },
    {
        "idx": 4,
        "slug": "04_Dung_Dich_Ve_Sinh_Romance_VIP_Hang_Thu",
        "stage": "stage_04.jpg",
        "cutout": "04_romance_vip.png",
        "prod_cx": 845, "prod_by": 965, "prod_max_w": 470, "prod_max_h": 535,
        "dark_mode": False,
        "cat_badge": "BÍ QUYẾT NÂNG NIU PHÁI ĐẸP MỖI NGÀY",
        "kicker": "TẠM BIỆT ẨM ƯỚT & MÙI KHÓ CHỊU SUỐT 24H",
        "headline_l1": "DUNG DỊCH KHÁNG KHUẨN",
        "headline_l2": "SẠCH THOÁNG – THÊM QUYẾN RŨ!",
        "grad_stops": ("#881337", "#E11D48", "#BE123C", "#9F1239", "#4C0519"),
        "stroke_col": "#FFFFFF",
        "shadow_rgba": "rgba(136, 19, 55, 0.25)",
        "accent": "#BE123C",
        "accent_soft": "#FFE4E6",
        "veil_rgb": "255, 248, 246",
        "pain_header": "Giải tỏa nỗi lo thầm kín để nàng luôn tự tin:",
        "pain_icon": "check_rose",
        "pains": [
            ("Xóa tan mùi khó chịu & bí bách", "Đặc biệt trong ngày nắng nóng, vận động hay chu kỳ"),
            ("Làm sạch dịu nhẹ chuẩn độ pH", "Không gây khô căng, giữ trọn hệ vi sinh tự nhiên"),
            ("Giảm ngứa ngáy, ẩm ướt bất thường", "Hỗ trợ kháng khuẩn & ngăn ngừa tác nhân gây viêm"),
            ("Dưỡng da mềm mịn & lưu hương tinh tế", "Cảm giác thoáng mát, dễ chịu và cuốn hút suốt ngày dài"),
        ],
        "usp_badge": "TINH CHẤT HOA HỒNG & THẢO MỘC THIÊN NHIÊN",
        "usp_title": "ROMANCE VIP HẰNG THU – ĐỒNG HÀNH MỖI NGÀY",
        "usp_Gradient": ("#FFFBEB", "#FDE68A", "#F59E0B"),
        "usp_bg": "linear-gradient(135deg, #7F1D1D 0%, #BE123C 52%, #881337 100%)",
        "pillars": [
            "Làm sạch êm ái – Vùng nhạy cảm thơm tho, thoáng sạch",
            "Hỗ trợ kháng khuẩn, hạn chế tối đa mùi khó chịu",
            "Duy trì độ ẩm mềm mại, giữ lửa tự tin & hạnh phúc",
        ],
        "actives": "Tinh Chất Hoa Hồng • Cúc La Mã • Lô Hội • Vitamin E Tự Nhiên",
        "cta_text": "INBOX ĐỂ TƯ VẤN CHĂM SÓC ĐÚNG CÁCH MỖI NGÀY",
    },
    {
        "idx": 5,
        "slug": "05_Vien_Dat_Phu_Khoa_Khit_Hong_Hang_Thu",
        "stage": "stage_05.jpg",
        "cutout": "05_vien_dat_pk.png",
        "prod_cx": 880, "prod_by": 1095, "prod_max_w": 515, "prod_max_h": 495,
        "dark_mode": False,
        "cat_badge": "CHĂM SÓC CHUYÊN BIỆT PHỤ NỮ SAU SINH",
        "kicker": "SAU SINH THAY ĐỔI KHIẾN CHỊ EM THIẾU TỰ TIN?",
        "headline_l1": "VIÊN ĐẶT KHÍT HỒNG",
        "headline_l2": "ĐÁNH THỨC NÉT XUÂN THÌ!",
        "grad_stops": ("#064E3B", "#0D9488", "#0F766E", "#065F46", "#022C22"),
        "stroke_col": "#FFFFFF",
        "shadow_rgba": "rgba(6, 78, 59, 0.24)",
        "accent": "#0F766E",
        "accent_soft": "#CCFBF1",
        "veil_rgb": "246, 253, 250",
        "pain_header": "Nỗi niềm khó nói của phụ nữ sau sinh nở:",
        "pain_icon": "heart_rose",
        "pains": [
            ("Độ đàn hồi giảm, kém săn chắc", "Thay đổi cấu trúc sau sinh khiến chị em mặc cảm, tự ti"),
            ("Khô rát, khó chịu khi gần gũi", "Giảm cảm xúc thăng hoa và sự gắn kết vợ chồng"),
            ("Khí hư có mùi, dễ viêm nhiễm", "Tạp chất tích tụ ảnh hưởng trực tiếp sinh hoạt hằng ngày"),
            ("Kém hồng hào, giảm nét tươi xuân", "Nội tiết thay đổi sau sinh làm vùng nhạy cảm kém tươi tắn"),
        ],
        "usp_badge": "GIẢI PHÁP CHO PHỤ NỮ VIỆT – HỘP 10 VIÊN",
        "usp_title": "VIÊN ĐẶT PHỤ KHOA HẰNG THU",
        "usp_Gradient": ("#FFFBEB", "#FDE68A", "#F59E0B"),
        "usp_bg": "linear-gradient(135deg, #064E3B 0%, #0F766E 54%, #115E59 100%)",
        "pillars": [
            "Hỗ trợ làm săn chắc, se khít & tươi hồng tự nhiên",
            "Hỗ trợ làm sạch dịch viêm phụ khoa & khử mùi hôi",
            "Bồi dưỡng tử cung khỏe mạnh, êm ái mỗi ngày",
        ],
        "actives": "Thảo Mộc Cung Đình • Trầu Không • Trinh Nữ Hoàng Cung • Nghệ",
        "cta_text": "INBOX RIÊNG TƯ ĐỂ ĐƯỢC TƯ VẤN LIỆU TRÌNH SAU SINH",
    },
    {
        "idx": 6,
        "slug": "06_Vien_Duong_Tu_Cung_Romance_Love_Hang_Thu",
        "stage": "stage_06.jpg",
        "cutout": "06_romance_love.png",
        "prod_cx": 865, "prod_by": 1045, "prod_max_w": 545, "prod_max_h": 490,
        "dark_mode": False,
        "cat_badge": "VIÊN DƯỠNG CẤP ẨM & TRẺ HÓA CHUYÊN SÂU",
        "kicker": "TẠM BIỆT \"KHÔ HẠN\" • GIỮ GÌN NÉT XUÂN PHÁI ĐẸP",
        "headline_l1": "VIÊN DƯỠNG TỬ CUNG",
        "headline_l2": "MỀM MỊN – SẠCH THƠM TỰ TIN!",
        "grad_stops": ("#701A75", "#C026D3", "#DB2777", "#9D174D", "#4A044E"),
        "stroke_col": "#FFFFFF",
        "shadow_rgba": "rgba(131, 24, 67, 0.25)",
        "accent": "#BE185D",
        "accent_soft": "#FCE7F3",
        "veil_rgb": "253, 244, 250",
        "pain_header": "Chị em có đang âm thầm chịu đựng?",
        "pain_icon": "drop_pink",
        "pains": [
            ("Khô rát, thiếu hụt độ ẩm tự nhiên", "Bề mặt niêm mạc khô căng, kém mềm mại mịn màng"),
            ("Đau rát, e ngại gần gũi vợ chồng", "\"Khô hạn\" trở thành rào cản vô hình làm giảm hạnh phúc"),
            ("Có mùi khó chịu, đánh mất tự tin", "Mất cân bằng môi trường vi sinh gây mùi kém duyên"),
            ("Khó chịu sau sinh & đổi thay nội tiết", "Suy giảm Estrogen sau tuổi 30 hoặc giai đoạn sau sinh"),
        ],
        "usp_badge": "CÔNG THỨC DƯỠNG ẨM KÉP & LÀM ĐẸP TỪ SÂU BÊN TRONG",
        "usp_title": "ROMANCE LOVE HẰNG THU PHARMA",
        "usp_Gradient": ("#FFFBEB", "#FDE68A", "#F472B6"),
        "usp_bg": "linear-gradient(135deg, #701A75 0%, #BE185D 55%, #831843 100%)",
        "pillars": [
            "Cấp ẩm tức thì, giảm khô hạn & làm mềm dịu êm ái",
            "Kháng khuẩn nhẹ nhàng, giảm viêm & khử mùi sạch thơm",
            "Dưỡng hồng hào, trẻ hóa & giữ trọn nét xuân quyến rũ",
        ],
        "actives": "Hyaluronic Acid • Panthenol B5 • Niacinamide • Collagen • Vitamin E",
        "cta_text": "INBOX \"ROMANCE LOVE\" ĐỂ ĐƯỢC TƯ VẤN KÍN ĐÁO",
    },
    {
        "idx": 7,
        "slug": "07_Ngoc_Long_Hoan_Hang_Thu",
        "stage": "stage_07.jpg",
        "cutout": "07_ngoc_long_hoan.png",
        "prod_cx": 890, "prod_by": 1055, "prod_max_w": 490, "prod_max_h": 540,
        "dark_mode": True,
        "cat_badge": "BÍ QUYẾT BỒI BỔ SINH LỰC NAM GIỚI",
        "kicker": "ĐÁNH THỨC NỘI LỰC • LÀM CHỦ MỌI CUỘC CHƠI",
        "headline_l1": "PHỤC HỒI PHONG ĐỘ",
        "headline_l2": "LẤY LẠI BẢN LĨNH ĐÀN ÔNG!",
        "grad_stops": ("#FFFDF0", "#FDE047", "#F59E0B", "#D97706", "#FEF08A"),
        "stroke_col": "#290F02",
        "shadow_rgba": "rgba(0, 0, 0, 0.75)",
        "accent": "#F59E0B",
        "accent_soft": "rgba(245, 158, 11, 0.18)",
        "veil_rgb": "18, 10, 6",
        "pain_header": "Anh em có đang đối mặt với những dấu hiệu này?",
        "pain_icon": "bolt_gold",
        "pains": [
            ("Sinh lý suy giảm, lửa hứng thú thấp", "Áp lực & tuổi tác làm hụt giảm Testosterone tự nhiên"),
            ("Khó duy trì độ cương cứng vững vàng", "Phong độ thất thường khiến cuộc vui không trọn vẹn"),
            ("Chưa tới đích đã \"hụt hơi\" sớm", "Đánh mất sự tự tin & bản lĩnh trước người bạn đời"),
            ("Cơ thể mệt mỏi, đau lưng mỏi gối", "Thể lực suy kiệt, tiểu đêm, kém sung mãn sau ngày dài"),
        ],
        "usp_badge": "HỘI TỤ 8 ĐẠI DANH DƯỢC BỔ THẬN TRÁNG DƯƠNG",
        "usp_title": "NGỌC LONG HOÀN HẰNG THU – HỘP 40 VIÊN",
        "usp_Gradient": ("#FFFBEB", "#FDE047", "#F59E0B"),
        "usp_bg": "linear-gradient(135deg, #2A1205 0%, #5C2408 50%, #271003 100%)",
        "pillars": [
            "Hỗ trợ bổ thận tráng dương, tăng cường sinh lý nam",
            "Bồi bổ nguyên khí, nâng cao sức bền & thể lực dẻo dai",
            "Giữ vững phong độ đỉnh cao & lửa ấm hạnh phúc gia đình",
        ],
        "actives": "Đông Trùng Hạ Thảo • Nhung Hươu • Ba Kích Tím • Sâm Cau • Dâm Dương Hoắc",
        "cta_text": "INBOX BẢO MẬT 100% ĐỂ ĐƯỢC CHUYÊN VIÊN TƯ VẤN",
    },
    {
        "idx": 8,
        "slug": "08_Vien_Uong_White_Skin_Hang_Thu",
        "stage": "stage_08.jpg",
        "cutout": "08_white_skin.png",
        "prod_cx": 875, "prod_by": 1045, "prod_max_w": 505, "prod_max_h": 545,
        "dark_mode": False,
        "cat_badge": "VIÊN UỐNG SÁNG DA & TRẺ HÓA TỪ CẤP ĐỘ TẾ BÀO",
        "kicker": "YÊU CHIỀU LÀN DA • GIỮ GÌN NÉT XUÂN RẠNG RỠ",
        "headline_l1": "LEGEND WHITE SKIN",
        "headline_l2": "CHĂM DA ĐẸP TỪ BÊN TRONG!",
        "grad_stops": ("#0C4A6E", "#0284C7", "#0369A1", "#1E3A8A", "#082F49"),
        "stroke_col": "#FFFFFF",
        "shadow_rgba": "rgba(12, 74, 110, 0.25)",
        "accent": "#0284C7",
        "accent_soft": "#E0F2FE",
        "veil_rgb": "242, 249, 255",
        "pain_header": "Chị em có đang phiền lòng vì làn da xuống sắc?",
        "pain_icon": "diamond_blue",
        "pains": [
            ("Làn da xỉn màu, thiếu sức sống", "Thoa kem bên ngoài mãi nhưng da vẫn tối sầm, kém tươi"),
            ("Nám mảng, sạm da, đốm tàn nhang", "Tăng sắc tố Melanin khiến hai gò má kém đều màu"),
            ("Da khô ráp, mất độ căng bóng", "Hàng rào giữ ẩm suy yếu làm bề mặt da sần sùi"),
            ("Xuất hiện nếp nhăn & lão hóa sớm", "Gốc tự do & thiếu hụt nội tiết tố sau tuổi 25 – 30"),
        ],
        "usp_badge": "BỘ 3 HOẠT CHẤT VÀNG TRẺ HÓA & BẬT TÔNG DA",
        "usp_title": "VIÊN UỐNG WHITE SKIN HẰNG THU",
        "usp_Gradient": ("#FFFBEB", "#FDE68A", "#38BDF8"),
        "usp_bg": "linear-gradient(135deg, #0C4A6E 0%, #0369A1 52%, #1E3A8A 100%)",
        "pillars": [
            "L-Glutathione: Hỗ trợ mờ nám sạm, dưỡng da sáng đều màu",
            "NMN tinh khiết: Hỗ trợ trẻ hóa & phục hồi năng lượng tế bào",
            "Vitamin E & Peptide: Cấp ẩm sâu, chống oxy hóa & ngừa lão hóa",
        ],
        "actives": "L-Glutathione • NMN • Amino Acid Peptide • Vitamin E",
        "cta_text": "INBOX ĐỂ ĐƯỢC TƯ VẤN LIỆU TRÌNH SÁNG DA KHOA HỌC",
    },
]

def svg_pain_icon(kind: str, accent: str) -> str:
    if kind == "check_rose":
        return f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none"><circle cx="12" cy="12" r="9.5" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="2"/><path d="M8 12.3l2.7 2.7 5.5-5.8" stroke="{accent}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    if kind == "bolt_gold":
        return f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none"><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z" fill="{accent}"/></svg>'
    if kind == "diamond_blue":
        return f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none"><path d="M6 3h12l4 6-10 12L2 9l4-6z" fill="{accent}" fill-opacity="0.18" stroke="{accent}" stroke-width="2"/><path d="M2 9h20M12 21L8 9l4-6 4 6-4 12z" stroke="{accent}" stroke-width="1.6"/></svg>'
    if kind in ("sparkle_rose", "heart_rose", "drop_pink"):
        return f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none"><circle cx="12" cy="12" r="9.5" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="2"/><path d="M12 7.5v5.2M12 16.2h.01" stroke="{accent}" stroke-width="2.4" stroke-linecap="round"/></svg>'
    return f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none"><circle cx="12" cy="12" r="9.5" fill="{accent}" fill-opacity="0.14" stroke="{accent}" stroke-width="2"/><path d="M9 9l6 6M15 9l-6 6" stroke="{accent}" stroke-width="2.3" stroke-linecap="round"/></svg>'

def build_html(spec: dict, logo_b64: str, stage_b64: str, prod_b64: str, mode: str = "full") -> str:
    """
    mode:
      - 'full': Complete composite poster (1200x1500)
      - 'bg': Layer 1 (Stage + atmospheric readability veil, 1200x1500 opaque)
      - 'prod': Layer 2 (Real Product + studio contact shadow + reflection + rim glow, 1200x1500 transparent)
      - 'ui': Layer 3 (All Typography, Cards, USP Banner, Header & CTA, 1200x1500 transparent)
    """
    dark = spec["dark_mode"]
    g1, g2, g3, g4, g5 = spec["grad_stops"]
    u1, u2, u3 = spec["usp_Gradient"]
    vr = spec["veil_rgb"]

    show_bg   = mode in ("full", "bg")
    show_prod = mode in ("full", "prod")
    show_ui   = mode in ("full", "ui")

    if dark:
        veil_css = f"""
        background:
          radial-gradient(circle at 73% 64%, rgba({vr}, 0.02) 0%, rgba({vr}, 0.35) 56%, rgba({vr}, 0.72) 100%),
          linear-gradient(180deg, rgba({vr}, 0.82) 0%, rgba({vr}, 0.36) 24%, rgba({vr}, 0.14) 68%, rgba({vr}, 0.85) 100%),
          linear-gradient(90deg, rgba({vr}, 0.62) 0%, rgba({vr}, 0.44) 44%, rgba({vr}, 0.04) 72%, rgba({vr}, 0.18) 100%);
        """
        card_bg = "rgba(32, 19, 12, 0.82)"
        card_border = "rgba(245, 158, 11, 0.38)"
        card_title_col = "#FEF3C7"
        card_sub_col = "#E7D5C0"
        pain_hdr_col = "#FDE68A"
        brand_pill_bg = "rgba(38, 22, 12, 0.88)"
        brand_pill_txt = "#FDE68A"
        brand_pill_bdr = "rgba(245, 158, 11, 0.55)"
        kicker_bg = "rgba(245, 158, 11, 0.18)"
        kicker_txt = "#FDE047"
        kicker_bdr = "rgba(253, 224, 71, 0.45)"
        prod_glow = "rgba(251, 191, 36, 0.34)"
    else:
        veil_css = f"""
        background:
          linear-gradient(180deg, rgba({vr}, 0.94) 0%, rgba({vr}, 0.80) 22%, rgba({vr}, 0.18) 52%, rgba({vr}, 0.12) 74%, rgba({vr}, 0.90) 100%),
          linear-gradient(90deg, rgba({vr}, 0.92) 0%, rgba({vr}, 0.82) 45%, rgba({vr}, 0.04) 68%, rgba({vr}, 0.06) 100%);
        """
        card_bg = "rgba(255, 255, 255, 0.88)"
        card_border = "rgba(255, 255, 255, 0.96)"
        card_title_col = "#1E293B"
        card_sub_col = "#475569"
        pain_hdr_col = spec["accent"]
        brand_pill_bg = "rgba(255, 255, 255, 0.92)"
        brand_pill_txt = spec["accent"]
        brand_pill_bdr = "rgba(255, 255, 255, 1.0)"
        kicker_bg = spec["accent_soft"]
        kicker_txt = spec["accent"]
        kicker_bdr = f"{spec['accent']}33"
        prod_glow = "rgba(255, 255, 255, 0.65)"

    pain_cards_html = ""
    icon_svg = svg_pain_icon(spec["pain_icon"], spec["accent"])
    for pt, ps in spec["pains"]:
        pain_cards_html += f"""
        <div class="pain-card">
          <div class="pain-bar" style="background:{spec['accent']};"></div>
          <div class="pain-ico">{icon_svg}</div>
          <div class="pain-body">
            <div class="pain-t">{pt}</div>
            <div class="pain-s">{ps}</div>
          </div>
        </div>
        """

    pillars_html = ""
    for pl in spec["pillars"]:
        pillars_html += f"""
        <div class="usp-item">
          <span class="usp-check">✓</span>
          <span>{pl}</span>
        </div>
        """

    px_left = spec["prod_cx"] - spec["prod_max_w"] // 2
    py_top  = spec["prod_by"] - spec["prod_max_h"]

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'MontBlack';
    src: url('file:///{FONTS_DIR}/Montserrat-Black.ttf') format('truetype');
    font-weight: 900;
  }}
  @font-face {{
    font-family: 'BeVN';
    src: url('file:///{FONTS_DIR}/BeVietnamPro-Medium.ttf') format('truetype');
    font-weight: 500;
  }}
  @font-face {{
    font-family: 'BeVN';
    src: url('file:///{FONTS_DIR}/BeVietnamPro-SemiBold.ttf') format('truetype');
    font-weight: 600;
  }}
  @font-face {{
    font-family: 'BeVN';
    src: url('file:///{FONTS_DIR}/BeVietnamPro-Bold.ttf') format('truetype');
    font-weight: 700;
  }}
  @font-face {{
    font-family: 'BeVN';
    src: url('file:///{FONTS_DIR}/BeVietnamPro-ExtraBold.ttf') format('truetype');
    font-weight: 800;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: 1200px;
    height: 1500px;
    overflow: hidden;
    background: {'transparent' if mode in ('prod', 'ui') else ('#120A06' if dark else '#FFF8FA')};
    font-family: 'BeVN', sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .canvas {{
    position: relative;
    width: 1200px;
    height: 1500px;
  }}
  /* LAYER 1: STAGE + VEIL */
  .bg-layer {{
    position: absolute;
    inset: 0;
    display: {'block' if show_bg else 'none'};
  }}
  .bg-layer img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .bg-veil {{
    position: absolute;
    inset: 0;
    {veil_css}
  }}
  /* Subtle luxury outer frame line */
  .frame-border {{
    position: absolute;
    inset: 18px;
    border: 1.5px solid {'rgba(245, 196, 81, 0.34)' if dark else 'rgba(255, 255, 255, 0.72)'};
    border-radius: 28px;
    pointer-events: none;
    z-index: 30;
    display: {'block' if show_ui else 'none'};
  }}

  /* LAYER 2: REAL STUDIO PRODUCT HERO ON PODIUM */
  .prod-layer {{
    position: absolute;
    inset: 0;
    z-index: 10;
    display: {'block' if show_prod else 'none'};
  }}
  .prod-halo {{
    position: absolute;
    left: {spec['prod_cx'] - 290}px;
    top: {spec['prod_by'] - 490}px;
    width: 580px;
    height: 520px;
    border-radius: 50%;
    background: radial-gradient(circle, {prod_glow} 0%, rgba(255,255,255,0) 70%);
    filter: blur(18px);
  }}
  .prod-shadow-wide {{
    position: absolute;
    left: {spec['prod_cx'] - int(spec['prod_max_w'] * 0.44)}px;
    top: {spec['prod_by'] - 26}px;
    width: {int(spec['prod_max_w'] * 0.88)}px;
    height: 48px;
    border-radius: 50%;
    background: radial-gradient(ellipse at center, rgba(18, 12, 16, 0.46) 0%, rgba(18, 12, 16, 0.16) 55%, rgba(0,0,0,0) 78%);
    filter: blur(8px);
  }}
  .prod-shadow-core {{
    position: absolute;
    left: {spec['prod_cx'] - int(spec['prod_max_w'] * 0.34)}px;
    top: {spec['prod_by'] - 15}px;
    width: {int(spec['prod_max_w'] * 0.68)}px;
    height: 24px;
    border-radius: 50%;
    background: radial-gradient(ellipse at center, rgba(10, 6, 8, 0.58) 0%, rgba(0,0,0,0) 75%);
    filter: blur(4px);
  }}
  .prod-box {{
    position: absolute;
    left: {px_left}px;
    top: {py_top}px;
    width: {spec['prod_max_w']}px;
    height: {spec['prod_max_h']}px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
  }}
  .prod-box img {{
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
    filter: drop-shadow(0 14px 24px rgba(15, 10, 14, 0.24));
  }}

  /* LAYER 3: TYPOGRAPHY & INFOGRAPHIC UI */
  .ui-layer {{
    position: absolute;
    inset: 0;
    z-index: 20;
    display: {'block' if show_ui else 'none'};
  }}

  /* Header Bar */
  .top-bar {{
    position: absolute;
    top: 42px;
    left: 52px;
    right: 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .brand-chip {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 7px 20px 7px 8px;
    border-radius: 999px;
    background: {brand_pill_bg};
    border: 1.5px solid {brand_pill_bdr};
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.08);
  }}
  .brand-chip img {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    object-fit: cover;
  }}
  .brand-chip .b-name {{
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: {brand_pill_txt};
    text-transform: uppercase;
  }}
  .brand-chip .b-sub {{
    font-size: 11.5px;
    font-weight: 600;
    color: {'#D6C7B2' if dark else '#64748B'};
    display: block;
    margin-top: 1px;
  }}
  .cat-pill {{
    padding: 10px 22px;
    border-radius: 999px;
    background: {spec['accent']};
    color: {'#1C1008' if dark else '#FFFFFF'};
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.8px;
    box-shadow: 0 8px 20px {spec['accent']}44;
  }}

  /* Hero Headline Zone */
  .hero-head {{
    position: absolute;
    top: 118px;
    left: 52px;
    right: 52px;
  }}
  .kicker-pill {{
    display: inline-block;
    padding: 6px 16px;
    border-radius: 8px;
    background: {kicker_bg};
    border: 1px solid {kicker_bdr};
    color: {kicker_txt};
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.7px;
    margin-bottom: 12px;
  }}

  /* 2-Layer Separated Stroke + 5-Stop Gradient Title */
  .grad-wrap {{
    position: relative;
    display: block;
    font-family: 'MontBlack', sans-serif;
    font-size: 51px;
    line-height: 1.13;
    letter-spacing: -0.6px;
    text-transform: uppercase;
  }}
  .grad-back {{
    color: transparent;
    -webkit-text-stroke: 11px {spec['stroke_col']};
    paint-order: stroke fill;
    text-shadow: 0 10px 24px {spec['shadow_rgba']};
  }}
  .grad-front {{
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, {g1} 0%, {g2} 32%, {g3} 58%, {g4} 84%, {g5} 100%);
    -webkit-background-clip: text;
    color: transparent;
  }}

  .sub-headline {{
    margin-top: 8px;
    display: inline-block;
    font-family: 'BeVN', sans-serif;
    font-size: 27px;
    font-weight: 800;
    color: {'#FDE68A' if dark else '#1E293B'};
    text-shadow: {'0 3px 12px rgba(0,0,0,0.75)' if dark else '0 2px 10px rgba(255,255,255,0.95)'};
  }}

  /* Left Diagnostic / Symptom Cards */
  .left-col {{
    position: absolute;
    top: 332px;
    left: 52px;
    width: 505px;
  }}
  .pain-heading {{
    font-size: 18px;
    font-weight: 800;
    color: {pain_hdr_col};
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    text-shadow: {'0 2px 8px rgba(0,0,0,0.8)' if dark else '0 1px 6px rgba(255,255,255,0.9)'};
  }}
  .pain-stack {{
    display: flex;
    flex-direction: column;
    gap: 13px;
  }}
  .pain-card {{
    position: relative;
    display: flex;
    align-items: flex-start;
    gap: 13px;
    padding: 15px 18px 15px 20px;
    background: {card_bg};
    border: 1.5px solid {card_border};
    border-radius: 18px;
    box-shadow: 0 10px 26px rgba(15, 23, 42, {'0.38' if dark else '0.08'});
    overflow: hidden;
  }}
  .pain-bar {{
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
  }}
  .pain-ico {{
    flex-shrink: 0;
    margin-top: 2px;
  }}
  .pain-t {{
    font-size: 18.5px;
    font-weight: 800;
    color: {card_title_col};
    line-height: 1.25;
  }}
  .pain-s {{
    font-size: 14px;
    font-weight: 500;
    color: {card_sub_col};
    line-height: 1.38;
    margin-top: 3px;
  }}

  /* Authentic Seal Badge near Product */
  .auth-seal {{
    position: absolute;
    right: 46px;
    top: 312px;
    width: 104px;
    height: 104px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FFFDF2 0%, #FDE68A 48%, #D97706 100%);
    padding: 4px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .auth-seal-in {{
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 1.5px dashed #92400E;
    background: radial-gradient(circle, #FFFBEB 0%, #FEF3C7 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 6px;
  }}
  .auth-seal-in .s1 {{
    font-size: 11px;
    font-weight: 800;
    color: #92400E;
    letter-spacing: 0.5px;
  }}
  .auth-seal-in .s2 {{
    font-family: 'MontBlack', sans-serif;
    font-size: 16.5px;
    color: #B45309;
    line-height: 1.1;
    margin: 2px 0;
  }}
  .auth-seal-in .s3 {{
    font-size: 10.5px;
    font-weight: 700;
    color: #78350F;
  }}

  /* Bottom USP Solution Banner */
  .usp-banner {{
    position: absolute;
    left: 48px;
    right: 48px;
    bottom: 112px;
    border-radius: 24px;
    background: {spec['usp_bg']};
    border: 2px solid rgba(253, 230, 138, 0.65);
    box-shadow: 0 18px 38px rgba(15, 23, 42, 0.26);
    padding: 20px 28px 18px 28px;
    color: #FFFFFF;
  }}
  .usp-top-tag {{
    position: absolute;
    top: -15px;
    left: 28px;
    background: linear-gradient(90deg, #FEF3C7 0%, #FDE047 50%, #F59E0B 100%);
    color: #451A03;
    font-size: 12.5px;
    font-weight: 800;
    letter-spacing: 0.7px;
    padding: 5px 16px;
    border-radius: 999px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18);
  }}
  .usp-title {{
    font-family: 'MontBlack', sans-serif;
    font-size: 25px;
    letter-spacing: 0.3px;
    background: linear-gradient(180deg, {u1} 0%, {u2} 55%, {u3} 100%);
    -webkit-background-clip: text;
    color: transparent;
    margin-top: 3px;
    margin-bottom: 10px;
  }}
  .usp-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 14px;
    margin-bottom: 12px;
  }}
  .usp-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: rgba(255, 255, 255, 0.11);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 12px;
    padding: 9px 12px;
    font-size: 14px;
    font-weight: 700;
    line-height: 1.32;
    color: #FFFFFF;
  }}
  .usp-check {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #FDE047;
    color: #451A03;
    font-size: 13px;
    font-weight: 900;
    flex-shrink: 0;
    margin-top: 1px;
  }}
  .actives-bar {{
    font-size: 13.5px;
    font-weight: 600;
    color: #FEF3C7;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .actives-bar strong {{
    color: #FDE047;
    font-weight: 800;
    text-transform: uppercase;
    font-size: 12.5px;
    letter-spacing: 0.4px;
  }}

  /* Bottom CTA Row */
  .cta-row {{
    position: absolute;
    left: 48px;
    right: 48px;
    bottom: 34px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .cta-btn {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 13px 28px;
    border-radius: 999px;
    background: linear-gradient(90deg, #F59E0B 0%, #FBBF24 50%, #F59E0B 100%);
    color: #290F02;
    font-size: 16.5px;
    font-weight: 800;
    letter-spacing: 0.4px;
    box-shadow: 0 10px 22px rgba(245, 158, 11, 0.36);
    border: 2px solid #FFFBEB;
  }}
  .legal-note {{
    font-size: 12px;
    font-weight: 600;
    color: {'#D6C7B2' if dark else '#475569'};
    text-align: right;
    max-width: 410px;
    line-height: 1.35;
  }}
</style>
</head>
<body>
  <div class="canvas">
    <div class="bg-layer">
      <img src="data:image/jpeg;base64,{stage_b64}" alt="">
      <div class="bg-veil"></div>
    </div>

    <div class="prod-layer">
      <div class="prod-halo"></div>
      <div class="prod-shadow-wide"></div>
      <div class="prod-shadow-core"></div>
      <div class="prod-box">
        <img src="data:image/png;base64,{prod_b64}" alt="">
      </div>
    </div>

    <div class="ui-layer">
      <div class="top-bar">
        <div class="brand-chip">
          <img src="data:image/png;base64,{logo_b64}" alt="">
          <div>
            <span class="b-name">Hằng Thu Pharma</span>
            <span class="b-sub">Tinh Hoa Thảo Dược Việt • Chính Hãng</span>
          </div>
        </div>
        <div class="cat-pill">{spec['cat_badge']}</div>
      </div>

      <div class="hero-head">
        <div class="kicker-pill">{spec['kicker']}</div>
        <div class="grad-wrap">
          <div class="grad-back">{spec['headline_l1']}</div>
          <div class="grad-front">{spec['headline_l1']}</div>
        </div>
        <div class="sub-headline">{spec['headline_l2']}</div>
      </div>

      <div class="left-col">
        <div class="pain-heading">
          <span>{'🌸' if spec['pain_icon'] == 'check_rose' else '⚠️'} {spec['pain_header']}</span>
        </div>
        <div class="pain-stack">
          {pain_cards_html}
        </div>
      </div>

      <div class="auth-seal">
        <div class="auth-seal-in">
          <span class="s1">CAM KẾT</span>
          <span class="s2">100%<br>CHÍNH HÃNG</span>
          <span class="s3">HẰNG THU</span>
        </div>
      </div>

      <div class="usp-banner">
        <div class="usp-top-tag">✨ {spec['usp_badge']}</div>
        <div class="usp-title">{spec['usp_title']}</div>
        <div class="usp-grid">
          {pillars_html}
        </div>
        <div class="actives-bar">
          <strong>🌿 Thành phần nổi bật:</strong>
          <span>{spec['actives']}</span>
        </div>
      </div>

      <div class="cta-row">
        <div class="cta-btn">
          <span>💌 {spec['cta_text']}</span>
        </div>
        <div class="legal-note">
          Chăm sóc chủ động – Tư vấn tận tâm – Bảo mật thông tin<br>
          *Đọc kỹ hướng dẫn sử dụng trước khi dùng.
        </div>
      </div>
    </div>

    <div class="frame-border"></div>
  </div>
</body>
</html>"""

def export_psd_3layers(bg_png: str, prod_png: str, ui_png: str, out_psd: str):
    """Packs 3 RGBA 1200x1500 PNG layers into an editable Adobe Photoshop 2026 .PSD (RLE compressed)."""
    layers = []
    # nested_layers_to_psd expects top-to-bottom order!
    for lname, ppath in [
        ("03_Chu_Va_Khung_Thong_Tin", ui_png),
        ("02_San_Pham_That_Hang_Thu", prod_png),
        ("01_Nen_Studio_Podium", bg_png),
    ]:
        arr = np.array(Image.open(ppath).convert("RGBA"), dtype=np.uint8)
        channels = {
            0: arr[:, :, 0],
            1: arr[:, :, 1],
            2: arr[:, :, 2],
            -1: arr[:, :, 3],
        }
        layers.append(
            nested_layers.Image(
                name=lname,
                visible=True,
                opacity=255,
                group_id=0,
                blend_mode=enums.BlendMode.normal,
                top=0,
                left=0,
                bottom=arr.shape[0],
                right=arr.shape[1],
                channels=channels,
            )
        )
    psd = nested_layers.nested_layers_to_psd(
        layers,
        color_mode=enums.ColorMode.rgb,
        size=(1500, 1200),
        compression=enums.Compression.raw,
    )
    with open(out_psd, "wb") as f:
        psd.write(f)

def write_html_bundle():
    logo_b64 = b64_file(os.path.join(CUT_DIR, "ht_logo_official.png"))
    manifest = []
    for spec in POSTER_SPECS:
        stage_p = os.path.join(STAGE_DIR, spec["stage"])
        prod_p  = os.path.join(CUT_DIR, spec["cutout"])
        stage_b64 = b64_file(stage_p)
        prod_b64  = b64_file(prod_p)

        slug = spec["slug"]
        paths = {}
        for mode in ("full", "bg", "prod", "ui"):
            hp = os.path.join(HTML_DIR, f"{slug}_{mode}.html")
            with open(hp, "w", encoding="utf-8") as f:
                f.write(build_html(spec, logo_b64, stage_b64, prod_b64, mode=mode))
            paths[mode] = hp
        manifest.append({"slug": slug, "html": paths})
    with open(os.path.join(HTML_DIR, "render_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("Generated 32 HTML layer files for 8 posters!")

if __name__ == "__main__":
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    write_html_bundle()
    CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    layer_tmp = os.path.join(HTML_DIR, "rendered_layers")
    os.makedirs(layer_tmp, exist_ok=True)

    with open(os.path.join(HTML_DIR, "render_manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)

    jobs = []
    for item in manifest:
        slug = item["slug"]
        for mode in ("full", "bg", "prod", "ui"):
            html_p = item["html"][mode]
            out_p = os.path.join(OUT_PNG, f"{slug}.png") if mode == "full" else os.path.join(layer_tmp, f"{slug}_{mode}.png")
            transparent = mode in ("prod", "ui")
            jobs.append((slug, mode, html_p, out_p, transparent))

    def run_chrome_shot(job):
        slug, mode, html_p, out_p, transparent = job
        if os.path.exists(out_p) and os.path.getsize(out_p) > 20000:
            return f"{slug}:{mode} (cached)"
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            "--force-device-scale-factor=1",
            "--window-size=1200,1500",
        ]
        if transparent:
            cmd.append("--default-background-color=00000000")
        cmd.extend([
            f"--screenshot={out_p}",
            "file:///" + html_p.replace("\\", "/"),
        ])
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"{slug}:{mode}"

    with ThreadPoolExecutor(max_workers=4) as ex:
        for done_tag in ex.map(run_chrome_shot, jobs):
            print("Rendered:", done_tag, flush=True)
    qc_tiles = []
    for spec in POSTER_SPECS:
        slug = spec["slug"]
        full_png = os.path.join(OUT_PNG, f"{slug}.png")
        im_rgb = Image.open(full_png).convert("RGB")
        im_rgb.save(
            os.path.join(OUT_JPG, f"{slug}.jpg"),
            quality=98,
            subsampling=0,
            icc_profile=SRGB_BYTES,
        )
        export_psd_3layers(
            os.path.join(layer_tmp, f"{slug}_bg.png"),
            os.path.join(layer_tmp, f"{slug}_prod.png"),
            os.path.join(layer_tmp, f"{slug}_ui.png"),
            os.path.join(OUT_PSD, f"{slug}.psd"),
        )
        print("Saved sRGB JPG + 3-Layer PSD:", slug)

        th = im_rgb.copy()
        th.thumbnail((420, 525), Image.Resampling.LANCZOS)
        qc_tiles.append(th)

    grid = Image.new("RGB", (420 * 4, 525 * 2), (18, 20, 26))
    for i, tl in enumerate(qc_tiles):
        grid.paste(tl, ((i % 4) * 420, (i // 4) * 525))
    qc_grid_path = os.path.join(CHECK_DIR, "all_8_posters_master_qc.jpg")
    grid.save(qc_grid_path, quality=94, icc_profile=SRGB_BYTES)
    print("Saved Master QC Grid:", qc_grid_path)
