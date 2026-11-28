# -*- coding: utf-8 -*-
"""
Dữ liệu Master Ngày 02 — HÔM NAY 25/11/2026 (261125 - Ngày 25.11.2026)
Định mức đầy đủ: 10 Video USP Dọc 9:16 (@24fps) + 10 Ấn Phẩm Thiết Kế 4:5 (.JPG + 5-Layer .PSD + Caption.txt)
Bàn giao TRỰC TIẾP cả Video lẫn Thiết kế vào:
Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026\
"""
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

BATCH_ROOT = Path(r"d:\AI\full studio\output\htpm-ngay-261125")
REF_DIR = BATCH_ROOT / "01_Nha_Trang_Refs"
COMBO_DIR = BATCH_ROOT / "00_Combo_Refs"
POSTS_OUT = BATCH_ROOT / "09_10_Thiet_Ke_Nha_Trang"
for _d in (BATCH_ROOT, REF_DIR, COMBO_DIR, POSTS_OUT):
    _d.mkdir(parents=True, exist_ok=True)

BRAND_KIT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")
FB_DIR = BRAND_KIT / "ambassadors_models" / "FB_Hang_Thu_146_Nha_Trang"
PROD_DIR = BRAND_KIT / "products_cutout_png"

K6_DAY25_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026")
CLOUD_DAY25_VID = Path(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\261125 - Ngày 25.11.2026")
LOCAL_DAY25_DIR = Path(r"D:\XUẤT CAPCUT\hằng thu pharma\261125 - Ngày 25.11.2026")


def ensure_ecosystem_3sku_cutout() -> str:
    """Tạo cụm 3 sản phẩm chủ lực thật 100% (WhiteSkin + Điều Kinh HT + LT Plus) cho Slot 10 Thương hiệu CEO Chị Hằng."""
    out_p = PROD_DIR / "SP_HTPM_ECOSYSTEM_3SKU_CUTOUT.png"
    if out_p.exists() and out_p.stat().st_size > 100_000:
        return out_p.name
    canvas = Image.new("RGBA", (1100, 760), (0, 0, 0, 0))
    items = [
        ("SP_LT_PLUS_COMBO_CUTOUT.png", 440, 80, 290),
        ("SP_WHITESKIN_COMBO_CUTOUT.png", 540, 345, 190),
        ("SP_DIEU_KINH_HT_CUTOUT.png", 490, 735, 240),
    ]
    for fn, th, lx, ty in items:
        im = Image.open(PROD_DIR / fn).convert("RGBA")
        if im.getbbox():
            im = im.crop(im.getbbox())
        tw = int(round(im.width * (th / float(im.height))))
        im_r = im.resize((tw, th), Image.Resampling.LANCZOS)
        canvas.alpha_composite(im_r, (lx, ty))
    if canvas.getbbox():
        canvas = canvas.crop(canvas.getbbox())
    canvas.save(out_p, format="PNG")
    return out_p.name


ensure_ecosystem_3sku_cutout()

NHA_TRANG_LIGHT_LOCK = (
    "Pure photorealistic commercial photography, crystal-clear high-key natural coastal Nha Trang morning daylight "
    "(5400K airy sunlit clarity, pure turquoise-blue ocean sky & lush green tropical breeze, zero muddy yellow cast, "
    "zero dark shadows, luminous natural rosy-fair skin texture, no watermarks). "
)

CHAR_LOCK = (
    "[CHARACTER & SILHOUETTE LOCK — CEO NGUYEN THI HANG]: Keep 100% the EXACT SAME graceful Vietnamese woman's face, warm expressive dark-brown eyes, "
    "natural double eyelids, softly arched brows, refined nose, radiant coral-red smile, and glossy dark-brown hair from the portrait reference. "
    "Portray her with a tall statuesque 170cm fashion-model posture and a graceful, full-proportioned feminine S-line hourglass silhouette in flattering waist-cinched tailored attire, framed from mid-thigh/hips up. "
)

SLOTS_261125 = [
    # 01 — Viên Đặt Phụ Khoa LT Plus
    {
        "idx": 1, "vkey": "v01_lt_plus", "code": "V01",
        "folder_title": "261125 - 01 - Viên Đặt LT Plus - Hiểu đúng chăm sóc chuyên sâu không lo khô rát",
        "final_mp4": "261125 HTPM viên đặt LT Plus hiểu đúng chăm sóc chuyên sâu không khô rát final.mp4",
        "jpg_name": "261125 HTPM thiết kế 01 viên đặt LT Plus nắng sớm vịnh Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 01 viên đặt LT Plus nắng sớm vịnh Nha Trang.psd",
        "sku": "SP02 — Viên Đặt Phụ Khoa LT Plus",
        "cutout": "SP_LT_PLUS_COMBO_CUTOUT.png",
        "fb_ref": "01_ceo_white_draped_blazer_office.jpg",
        "fb_s02_ref": "16_nha_trang_white_architecture_resort.jpg",
        "outfit": "Wearing a flattering waist-cinched ivory-white tailored blazer draped gracefully over a pearl-silk camisole and fitted high-waisted skirt, highlighting her tall 170cm posture and full S-line hourglass silhouette. ",
        "scene_post": "on a sunlit glass penthouse balcony overlooking turquoise Nha Trang bay with gentle ocean breeze",
        "scene_vid": "inside an airy sunlit white coastal suite overlooking Nha Trang bay with sheer white curtains",
        "pri": "#C92A6A", "pri_dark": "#4A0B24", "pri_soft": "#FFEAF2", "grad_mid": "#FF8AB8",
        "accent_soft": "rgba(201, 42, 106, 0.16)", "wash_rgb": (255, 250, 252, 165),
        "prod_h": 430, "prod_cx": 360, "prod_by": 1800, "pack_w": 240, "s4_pack_h": 510,
        # Post copy
        "kicker": "Giải mã chăm sóc chuyên sâu • Phố biển Nha Trang",
        "hook_l1": "Bận rộn cả ngày dài,",
        "hook_l2": "đừng để <em>ẩm bí & khô rát</em>",
        "hook_l3": "làm vơi nét tự tin.",
        "script_top": "Chăm sóc chuyên sâu", "prod_title": "LT PLUS",
        "subclaim": "Kháng khuẩn • Khử mùi • Duy trì độ ẩm & pH",
        "pills": [
            "Hỗ trợ kháng khuẩn, khử mùi khó chịu vùng nhạy cảm",
            "Ngăn ngừa viêm nhiễm, giữ cảm giác thoáng sạch êm ái",
            "Duy trì độ ẩm & pH tự nhiên • Hộp 15 viên chính hãng",
        ],
        "footer_l": "Viên đặt phụ khoa LT Plus Hằng Thu • Dịu êm chuẩn pH", "footer_r": "Tư vấn kín đáo 1:1",
        "caption": "Bận rộn công việc từ sáng đến tối ở Nha Trang, nhiều chị em hay lầm tưởng chỉ vệ sinh bên ngoài là đủ.\n\nViên đặt phụ khoa LT Plus Hằng Thu giúp kháng khuẩn, khử mùi, ngăn ngừa viêm nhiễm mà vẫn duy trì độ ẩm và độ pH tự nhiên êm ái.\n\nChị nhắn ngay cho Hằng Thu để được hướng dẫn liệu trình phù hợp nhé!\n#HangThuPharma #LTPlus #CEOChiHang #NhaTrang",
        # Video copy & VO
        "hook_kicker": "BẬN RỘN SUỐT CẢ NGÀY DÀI", "hook_hero": "Chỉ rửa ngoài đủ chưa?",
        "slide1_hdr": "Hiểu lầm nhiều chị em hay gặp",
        "slide1_rows": ["Chỉ rửa ngoài khi bên trong ẩm bí", "E ngại viên đặt gây cảm giác khô rát", "Để mùi khó chịu làm mất tự tin"],
        "slide2_pill": "Chăm sóc êm dịu chuẩn pH<br/>Viên Đặt LT Plus Hằng Thu",
        "pack_kicker": "KHÁNG KHUẨN & GIỮ ẨM TỰ NHIÊN", "pack_hero": "LT Plus",
        "slide3_pills": ["Kháng khuẩn, khử mùi vùng nhạy cảm", "Hỗ trợ ngăn ngừa viêm nhiễm tái lại", "Duy trì độ ẩm & pH tự nhiên êm ái"],
        "end_cat": "VIÊN ĐẶT PHỤ KHOA CHUYÊN SÂU", "end_name": "LT Plus", "end_sub": "KHÁNG KHUẨN • KHỬ MÙI • GIỮ ẨM PH",
        "cta_txt": "Nhắn ngay “LT PLUS” · Tư vấn riêng 1:1",
        "legal_txt": "Hộp 15 viên chính hãng Hằng Thu Pharma · Êm dịu cho phái đẹp",
        "segments": [
            ("vo_01", "Đón nắng sớm trong trẻo bên vịnh Nha Trang, nhiều chị bận rộn cả ngày vẫn nghĩ chỉ cần rửa bên ngoài là đã đủ thoáng sạch.", "Đón nắng sớm trong trẻo bên vịnh Nha Trang, nhiều chị bận rộn cả ngày vẫn nghĩ chỉ cần rửa bên ngoài là đã đủ thoáng sạch.", ["nha trang", "thoáng sạch"]),
            ("vo_02", "Thực ra khi khí hư hay mùi khó chịu xuất hiện, không ít chị lại e ngại dùng viên đặt vì sợ cảm giác khô rát kém tự nhiên.", "Thực ra khi khí hư hay mùi khó chịu xuất hiện, không ít chị lại e ngại dùng viên đặt vì sợ cảm giác khô rát kém tự nhiên.", ["khó chịu", "tự nhiên"]),
            ("vo_03", "Đó là lý do chị Hằng tin chọn Viên Đặt Phụ Khoa Eo Ti Pờ Lớt Hằng Thu cho nhịp sống năng động mỗi tuần.", "Đó là lý do chị Hằng tin chọn Viên Đặt Phụ Khoa LT Plus Hằng Thu cho nhịp sống năng động mỗi tuần.", ["phụ khoa", "hằng thu"]),
            ("vo_04", "Eo Ti Pờ Lớt giúp kháng khuẩn, khử mùi, hỗ trợ ngăn ngừa viêm nhiễm mà vẫn duy trì độ ẩm và độ pê hát tự nhiên thật êm ái.", "LT Plus giúp kháng khuẩn, khử mùi, hỗ trợ ngăn ngừa viêm nhiễm mà vẫn duy trì độ ẩm và độ pH tự nhiên thật êm ái.", ["kháng khuẩn", "độ ẩm"]),
            ("vo_05", "Chị nhắn ngay Eo Ti Pờ Lớt để Hằng Thu tư vấn kín đáo đúng cơ địa cho chị nhé.", "Chị nhắn ngay LT Plus để Hằng Thu tư vấn kín đáo đúng cơ địa cho chị nhé.", ["hằng thu", "tư vấn"]),
        ],
        "caps": [
            ("vo_01", 'Đón nắng sớm trong trẻo <span class="cap-kw">bên vịnh Nha Trang,</span>', 'Bận rộn cả ngày <span class="cap-kw">chỉ rửa ngoài đủ chưa?</span>'),
            ("vo_02", 'Khi ẩm bí, mùi khó chịu <span class="cap-kw">làm mất tự tin,</span>', 'Nhiều chị lại e ngại <span class="cap-kw">cảm giác khô rát.</span>'),
            ("vo_03", 'Đó là lý do chị Hằng <span class="cap-kw">tin chọn đồng hành</span>', 'Cùng Viên Đặt Phụ Khoa <span class="cap-kw">LT Plus Hằng Thu.</span>'),
            ("vo_04", '<span class="cap-kw">LT Plus</span> kháng khuẩn, khử mùi, ngừa viêm nhiễm,', 'Vẫn duy trì <span class="cap-kw">độ ẩm &amp; pH tự nhiên êm ái.</span>'),
        ],
    },

    # 02 — Gel Phụ Khang Hằng Thu
    {
        "idx": 2, "vkey": "v02_gel_phu_khang", "code": "V02",
        "folder_title": "261125 - 02 - Gel Phụ Khang - Đừng đợi khó chịu mới vội chăm sóc",
        "final_mp4": "261125 HTPM Gel Phụ Khang gói nhỏ dịu nhẹ thoáng sạch suốt ngày dài final.mp4",
        "jpg_name": "261125 HTPM thiết kế 02 Gel Phụ Khang thanh khiết ban mai Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 02 Gel Phụ Khang thanh khiết ban mai Nha Trang.psd",
        "sku": "SP09 — Gel Phụ Khang Hằng Thu",
        "cutout": "SP_GEL_PHU_KHANG_COMBO_CUTOUT.png",
        "fb_ref": "08_pastel_ice_blue_ruffle_dress.jpg",
        "fb_s02_ref": "15_nha_trang_golden_hour_breeze.jpg",
        "outfit": "Wearing a flattering waist-cinched pastel ice-blue off-shoulder silk midi dress that highlights her tall 170cm posture and full S-line hourglass silhouette, with delicate pearl studs. ",
        "scene_post": "in a sunlit white marble coastal vanity lounge in Nha Trang with morning ocean breeze and white orchids",
        "scene_vid": "in a bright sunlit coastal Nha Trang glass lounge overlooking turquoise sea and palm trees",
        "pri": "#B53471", "pri_dark": "#3D0E25", "pri_soft": "#FCEBF3", "grad_mid": "#F78FB3",
        "accent_soft": "rgba(181, 52, 113, 0.16)", "wash_rgb": (254, 250, 253, 166),
        "prod_h": 310, "prod_cx": 385, "prod_by": 1790, "pack_w": 265, "s4_pack_h": 380,
        "kicker": "Thói quen tinh tế của phụ nữ phố biển",
        "hook_l1": "Đừng đợi khó chịu,",
        "hook_l2": "hãy giữ mình <em>sạch thơm</em>",
        "hook_l3": "từ gói nhỏ mỗi ngày.",
        "script_top": "Sạch dịu nhẹ & thơm mát", "prod_title": "GEL PHỤ KHANG",
        "subclaim": "Gói 5ml tiện lợi • Khử mùi • Thoáng mát tự nhiên",
        "pills": [
            "Dạng gói 5ml nhỏ gọn mang theo đi làm, du lịch biển",
            "Làm sạch dịu nhẹ, khử mùi khó chịu suốt 8 tiếng",
            "Giữ vùng nhạy cảm mềm mịn, thoáng mát tự nhiên",
        ],
        "footer_l": "Gel Phụ Khang Hằng Thu • Hộp 5 túi x 5ml tiện dụng", "footer_r": "Nhắn nhận tư vấn",
        "caption": "Phụ nữ hiện đại bận mấy cũng nhớ dành 1 phút yêu chiều bản thân.\n\nĐi làm hay đi công tác xa Nha Trang, trong túi Hằng lúc nào cũng có sẵn gói nhỏ Gel Phụ Khang Hằng Thu — sạch dịu nhẹ, khử mùi và thơm mát cực kỳ tiện lợi.\n\nNhắn Hằng Thu để rinh ngay hộp nhỏ xinh này nhé!\n#HangThuPharma #GelPhuKhang #PhuNuTinhTe #NhaTrang",
        "hook_kicker": "NGỒI VĂN PHÒNG SUỐT 8 TIẾNG", "hook_hero": "Đợi khó chịu mới chăm?",
        "slide1_hdr": "Thói quen dễ khiến chị kém tự tin",
        "slide1_rows": ["Ngồi lâu cả ngày gây hầm bí khó nói", "Đi làm, đi biển bất tiện mang chai lớn", "Đợi có mùi mới lo tìm cách xử lý"],
        "slide2_pill": "Gói nhỏ 5ml mang theo mọi nơi<br/>Gel Phụ Khang Hằng Thu",
        "pack_kicker": "SẠCH DỊU NHẸ • THƠM MÁT", "pack_hero": "Gel Phụ Khang",
        "slide3_pills": ["Làm sạch dịu nhẹ, không gây khô rát", "Khử mùi hiệu quả, giữ nét thơm mát", "Túi 5ml nhỏ gọn tiện mang đi làm, du lịch"],
        "end_cat": "GEL CHĂM SÓC THẢO DƯỢC DỊU ÊM", "end_name": "Gel Phụ Khang", "end_sub": "SẠCH DỊU NHẸ • KHỬ MÙI • THƠM MÁT",
        "cta_txt": "Nhắn ngay “GEL PHỤ KHANG” · Tư vấn 1:1",
        "legal_txt": "Hộp gồm 5 túi x 5ml chính hãng Hằng Thu Pharma",
        "segments": [
            ("vo_01", "Đi làm hay di chuyển suốt tám tiếng dưới nắng phố biển Nha Trang, đừng đợi đến khi hầm bí khó chịu chị mới vội vàng tìm cách chăm sóc.", "Đi làm hay di chuyển suốt 8 tiếng dưới nắng phố biển Nha Trang, đừng đợi đến khi hầm bí khó chịu chị mới vội vàng tìm cách chăm sóc.", ["nha trang", "chăm sóc"]),
            ("vo_02", "Ngồi văn phòng lâu hay đi công tác xa mà mang theo chai lọ cồng kềnh đôi khi khiến chị em mình ngại dùng đều đặn.", "Ngồi văn phòng lâu hay đi công tác xa mà mang theo chai lọ cồng kềnh đôi khi khiến chị em mình ngại dùng đều đặn.", ["văn phòng", "đều đặn"]),
            ("vo_03", "Bí quyết nhỏ gọn luôn nằm sẵn trong túi xách của Hằng chính là gói Gel Phụ Khang Hằng Thu.", "Bí quyết nhỏ gọn luôn nằm sẵn trong túi xách của Hằng chính là gói Gel Phụ Khang Hằng Thu.", ["nhỏ gọn", "phụ khang", "hằng thu"]),
            ("vo_04", "Thiết kế từng gói năm mi li lít tinh tế giúp làm sạch dịu nhẹ, khử mùi khó chịu và mang lại cảm giác thơm mát, êm ái suốt ngày dài.", "Thiết kế từng gói 5ml tinh tế giúp làm sạch dịu nhẹ, khử mùi khó chịu và mang lại cảm giác thơm mát, êm ái suốt ngày dài.", ["dịu nhẹ", "thơm mát"]),
            ("vo_05", "Chủ động sạch thơm ở bất cứ đâu, chị nhắn ngay Gel Phụ Khang để Hằng Thu gửi tư vấn chi tiết nhé.", "Chủ động sạch thơm ở bất cứ đâu, chị nhắn ngay Gel Phụ Khang để Hằng Thu gửi tư vấn chi tiết nhé.", ["sạch thơm", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Di chuyển suốt 8 tiếng <span class="cap-kw">nắng phố biển Nha Trang,</span>', 'Đừng đợi khó chịu <span class="cap-kw">mới vội vàng chăm sóc!</span>'),
            ("vo_02", 'Ngồi văn phòng lâu hay <span class="cap-kw">đi công tác, du lịch,</span>', 'Chai lọ cồng kềnh dễ làm <span class="cap-kw">chị ngại mang theo.</span>'),
            ("vo_03", 'Bí quyết nhỏ gọn luôn có <span class="cap-kw">trong túi của Hằng</span>', 'Chính là gói nhỏ <span class="cap-kw">Gel Phụ Khang Hằng Thu.</span>'),
            ("vo_04", 'Từng gói 5ml giúp <span class="cap-kw">làm sạch dịu nhẹ, khử mùi,</span>', 'Giữ cảm giác <span class="cap-kw">thơm mát suốt cả ngày dài.</span>'),
        ],
    },

    # 03 — Dạ Dày HT
    {
        "idx": 3, "vkey": "v03_da_day_ht", "code": "V03",
        "folder_title": "261125 - 03 - Dạ Dày HT - Bỏ bữa uống cà phê sáng và cách êm thượng vị",
        "final_mp4": "261125 HTPM Dạ Dày HT bỏ bữa cà phê sáng xoa dịu êm thượng vị final.mp4",
        "jpg_name": "261125 HTPM thiết kế 03 Dạ Dày HT buổi sáng sân vườn Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 03 Dạ Dày HT buổi sáng sân vườn Nha Trang.psd",
        "sku": "SP03 — Thực Phẩm Bảo Vệ Sức Khỏe Dạ Dày HT",
        "cutout": "SP_DA_DAY_HT_COMBO_CUTOUT.png",
        "fb_ref": "11_black_blazer_white_bow_blouse.jpg",
        "fb_s02_ref": "09_lime_green_modern_suit.jpg",
        "outfit": "Wearing a crisp waist-fitted white silk bow-tie blouse tucked into a sleek high-waisted emerald-olive pencil skirt, highlighting her tall 170cm posture and full S-line hourglass figure. ",
        "scene_post": "at a sunlit tropical garden terrace cafe in Nha Trang with lush green palms and morning ocean sky",
        "scene_vid": "in a bright sunlit tropical glasshouse cafe in Nha Trang overlooking green palms and blue sea",
        "pri": "#2E7D32", "pri_dark": "#103414", "pri_soft": "#E8F6E9", "grad_mid": "#7ED982",
        "accent_soft": "rgba(46, 125, 50, 0.18)", "wash_rgb": (248, 254, 248, 168),
        "prod_h": 455, "prod_cx": 365, "prod_by": 1800, "pack_w": 240, "s4_pack_h": 540,
        "kicker": "Chăm sóc hệ tiêu hóa giữa nhịp sống bận rộn",
        "hook_l1": "Sáng vội ly cà phê,",
        "hook_l2": "đừng để <em>nóng rát thượng vị</em>",
        "hook_l3": "làm ngày dài mệt mỏi.",
        "script_top": "Thảo mộc Dạ Cẩm & Nghệ Đen", "prod_title": "DẠ DÀY HT",
        "subclaim": "Giảm acid dịch vị • Bảo vệ niêm mạc dạ dày",
        "pills": [
            "Kết hợp Dạ Cẩm, Nghệ Đen, Hoàng Liên & Mộc Hương",
            "Hỗ trợ giảm acid dịch vị, giúp bảo vệ niêm mạc dạ dày",
            "Hỗ trợ giảm triệu chứng viêm loét dạ dày, trào ngược",
        ],
        "footer_l": "TPBVSK Dạ Dày HT • Không phải là thuốc, không thay thế thuốc chữa bệnh", "footer_r": "Tư vấn liệu trình",
        "caption": "Thói quen sáng vội ly cà phê, trưa ăn trễ giờ khi bận việc rất dễ làm vùng thượng vị nóng rát, ợ chua khó chịu.\n\nHằng luôn chuẩn bị sẵn Dạ Dày HT với thảo mộc Dạ Cẩm, Nghệ Đen, Hoàng Liên giúp giảm acid dịch vị và bảo vệ niêm mạc dạ dày êm ái.\n\nAnh chị cần tư vấn kỹ hơn cứ nhắn cho Hằng Thu nhé!\n#HangThuPharma #DaDayHT #ChamSocDaDay #NhaTrang",
        "hook_kicker": "SÁNG CÀ PHÊ VỘI • TRƯA ĂN TRỄ", "hook_hero": "Nóng rát thượng vị?",
        "slide1_hdr": "Thói quen hại dạ dày khi bận rộn",
        "slide1_rows": ["Uống cà phê lúc bụng rỗng buổi sáng", "Ăn uống thất thường gây ợ hơi, ợ chua", "Đau âm ỉ thượng vị, trào ngược mất ngủ"],
        "slide2_pill": "Xoa dịu từ thảo mộc Việt<br/>Dạ Dày HT Hằng Thu",
        "pack_kicker": "DẠ CẨM • NGHỆ ĐEN • HOÀNG LIÊN", "pack_hero": "Dạ Dày HT",
        "slide3_pills": ["Hỗ trợ giảm acid dịch vị dư thừa", "Giúp bảo vệ niêm mạc dạ dày êm khỏe", "Hỗ trợ giảm trào ngược & đau thượng vị"],
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE", "end_name": "Dạ Dày HT", "end_sub": "GIẢM ACID • BẢO VỆ NIÊM MẠC DẠ DÀY",
        "cta_txt": "Nhắn ngay “DẠ DÀY HT” · Tư vấn liệu trình",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "segments": [
            ("vo_01", "Buổi sáng ở Nha Trang bận xử lý công việc, nhiều anh chị có thói quen nhấp vội ly cà phê lúc bụng đói rồi trưa lại ăn trễ giờ.", "Buổi sáng ở Nha Trang bận xử lý công việc, nhiều anh chị có thói quen nhấp vội ly cà phê lúc bụng đói rồi trưa lại ăn trễ giờ.", ["nha trang", "cà phê"]),
            ("vo_02", "Lâu ngày vùng thượng vị cứ nóng rát, ợ hơi, ợ chua và trào ngược làm cả ngày mất tập trung, đêm nằm cũng chẳng tròn giấc.", "Lâu ngày vùng thượng vị cứ nóng rát, ợ hơi, ợ chua và trào ngược làm cả ngày mất tập trung, đêm nằm cũng chẳng tròn giấc.", ["thượng vị", "trào ngược"]),
            ("vo_03", "Để chăm sóc dạ dày bền vững cho cả nhà, Hằng luôn tin dùng Thực Phẩm Bảo Vệ Sức Khỏe Dạ Dày Hát Tê Hằng Thu.", "Để chăm sóc dạ dày bền vững cho cả nhà, Hằng luôn tin dùng Thực Phẩm Bảo Vệ Sức Khỏe Dạ Dày HT Hằng Thu.", ["dạ dày", "hằng thu"]),
            ("vo_04", "Sự hòa quyện của Dạ Cẩm, Nghệ Đen, Hoàng Liên và Mộc Hương hỗ trợ giảm a xít dịch vị, giúp bảo vệ niêm mạc và giảm triệu chứng viêm loét dạ dày, tá tràng.", "Sự hòa quyện của Dạ Cẩm, Nghệ Đen, Hoàng Liên và Mộc Hương hỗ trợ giảm acid dịch vị, giúp bảo vệ niêm mạc và giảm triệu chứng viêm loét dạ dày, tá tràng.", ["dạ cẩm", "nghệ đen", "niêm mạc"]),
            ("vo_05", "Bụng êm khỏe để làm việc trọn năng lượng, anh chị nhắn ngay Dạ Dày Hát Tê để Hằng Thu đồng hành nhé.", "Bụng êm khỏe để làm việc trọn năng lượng, anh chị nhắn ngay Dạ Dày HT để Hằng Thu đồng hành nhé.", ["êm khỏe", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Buổi sáng bận rộn <span class="cap-kw">nhấp vội ly cà phê,</span>', 'Trưa lại ăn trễ giờ <span class="cap-kw">khi cuốn vào công việc?</span>'),
            ("vo_02", 'Vùng thượng vị dễ <span class="cap-kw">nóng rát, ợ chua, trào ngược,</span>', 'Làm ngày mất tập trung, <span class="cap-kw">đêm nằm khó tròn giấc.</span>'),
            ("vo_03", 'Để chăm sóc dạ dày <span class="cap-kw">êm khỏe cho cả nhà,</span>', 'Hằng luôn tin chọn <span class="cap-kw">Dạ Dày HT Hằng Thu.</span>'),
            ("vo_04", 'Kết hợp <span class="cap-kw">Dạ Cẩm, Nghệ Đen, Hoàng Liên</span> giảm acid,', 'Giúp bảo vệ <span class="cap-kw">niêm mạc dạ dày êm ái.</span>'),
        ],
    },

    # 04 — Điều Kinh HT
    {
        "idx": 4, "vkey": "v04_dieu_kinh_ht", "code": "V04",
        "folder_title": "261125 - 04 - Điều Kinh HT - Đừng coi thường kỳ dâu thất thường tuổi 30",
        "final_mp4": "261125 HTPM Điều Kinh HT đừng coi thường kỳ dâu thất thường tuổi 30 final.mp4",
        "jpg_name": "261125 HTPM thiết kế 04 Điều Kinh HT villa trắng đón gió biển Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 04 Điều Kinh HT villa trắng đón gió biển Nha Trang.psd",
        "sku": "SP01 — Điều Kinh HT",
        "cutout": "SP_DIEU_KINH_HT_CUTOUT.png",
        "fb_ref": "02_cream_pearl_cape_blazer_lounge.jpg",
        "fb_s02_ref": "14_nha_trang_palm_garden_sunlit.jpg",
        "outfit": "Wearing an elegant waist-sculpted cream-ivory pearl-accented sheath dress with a light sheer ivory cape draped softly behind her shoulders, highlighting her tall 170cm posture and full hourglass silhouette. ",
        "scene_post": "in a sunlit white ocean-view villa living room in Nha Trang with fresh pink peonies and turquoise sea outside",
        "scene_vid": "on a bright sunlit white marble villa balcony overlooking Nha Trang bay and palm trees",
        "pri": "#8B1E72", "pri_dark": "#3B0830", "pri_soft": "#FBE8F7", "grad_mid": "#F28CD9",
        "accent_soft": "rgba(139, 30, 114, 0.16)", "wash_rgb": (253, 250, 255, 166),
        "prod_h": 505, "prod_cx": 340, "prod_by": 1800, "pack_w": 195, "s4_pack_h": 575,
        "kicker": "Dưỡng khí huyết phụ nữ sau tuổi 30 • Nha Trang",
        "hook_l1": "Kỳ dâu thất thường,",
        "hook_l2": "là lời nhắc cần <em>bồi bổ</em>",
        "hook_l3": "khí huyết từ gốc.",
        "script_top": "Bổ huyết & điều hòa", "prod_title": "ĐIỀU KINH HT",
        "subclaim": "Đương quy • Hương phụ • Êm dịu mỗi chu kỳ",
        "pills": [
            "Bổ huyết, hỗ trợ lưu thông khí huyết cho phụ nữ",
            "Hỗ trợ điều hòa kinh nguyệt đều đặn tự nhiên",
            "Giúp giảm đau bụng âm ỉ mỗi kỳ hành kinh",
        ],
        "footer_l": "TPBVSK Điều Kinh HT • Không phải là thuốc, không thay thế thuốc chữa bệnh", "footer_r": "Tư vấn theo cơ địa",
        "caption": "Nhiều chị em sau tuổi 30 thấy kỳ kinh thưa dần, đau bụng âm ỉ cứ nghĩ do mệt chút rồi thôi.\n\nThực ra khí huyết bên trong thông suốt thì sắc diện người phụ nữ mới hồng hào, tươi tắn. Chị Hằng luôn tin chọn Điều Kinh HT với Đương quy, Hương phụ để bồi bổ đều đặn.\n\nChị nhắn Hằng Thu để được tư vấn kỹ hơn nhé!\n#HangThuPharma #DieuKinhHT #BoHuyet #NhaTrang",
        "hook_kicker": "SAU TUỔI 30 BẬN RỘN LO TOAN", "hook_hero": "Coi nhẹ kỳ dâu lệch?",
        "slide1_hdr": "Dấu hiệu khí huyết đang lên tiếng",
        "slide1_rows": ["Chu kỳ tháng sớm tháng muộn thất thường", "Bụng dưới đau âm ỉ, người uể oải mất sức", "Da dẻ kém hồng hào, tay chân dễ lạnh"],
        "slide2_pill": "Nuôi dưỡng khí huyết từ gốc<br/>Điều Kinh HT Hằng Thu",
        "pack_kicker": "ĐƯƠNG QUY & HƯƠNG PHỤ QUÝ", "pack_hero": "Điều Kinh HT",
        "slide3_pills": ["Giúp bổ huyết, lưu thông khí huyết", "Hỗ trợ điều hòa kinh nguyệt đều đặn", "Hỗ trợ giảm đau bụng khi hành kinh"],
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE", "end_name": "Điều Kinh HT", "end_sub": "BỔ HUYẾT • LƯU THÔNG KHÍ HUYẾT",
        "cta_txt": "Nhắn ngay “ĐIỀU KINH HT” · Tư vấn riêng",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "segments": [
            ("vo_01", "Giữa nắng mai dịu dàng bên bờ biển Nha Trang, Hằng gặp rất nhiều chị sau tuổi ba mươi thấy kỳ dâu lệch ngày nhưng cứ tặc lưỡi bỏ qua.", "Giữa nắng mai dịu dàng bên bờ biển Nha Trang, Hằng gặp rất nhiều chị sau tuổi 30 thấy kỳ dâu lệch ngày nhưng cứ tặc lưỡi bỏ qua.", ["nha trang", "lệch ngày"]),
            ("vo_02", "Đừng coi thường chị nhé, vì khi khí huyết ứ trệ không chỉ gây đau bụng kinh mệt mỏi mà còn làm gương mặt kém tươi tắn rạng ngời.", "Đừng coi thường chị nhé, vì khi khí huyết ứ trệ không chỉ gây đau bụng kinh mệt mỏi mà còn làm gương mặt kém tươi tắn rạng ngời.", ["khí huyết", "tươi tắn"]),
            ("vo_03", "Hãy yêu chiều cơ thể từ bên trong cùng Viên Uống Điều Kinh Hát Tê Hằng Thu.", "Hãy yêu chiều cơ thể từ bên trong cùng Viên Uống Điều Kinh HT Hằng Thu.", ["bên trong", "điều kinh", "hằng thu"]),
            ("vo_04", "Chiết xuất từ Đương quy, Hương phụ giúp bổ huyết, lưu thông khí huyết, hỗ trợ điều hòa chu kỳ đều đặn và êm dịu những ngày đèn đỏ.", "Chiết xuất từ Đương quy, Hương phụ giúp bổ huyết, lưu thông khí huyết, hỗ trợ điều hòa chu kỳ đều đặn và êm dịu những ngày đèn đỏ.", ["đương quy", "hương phụ", "chu kỳ"]),
            ("vo_05", "Phụ nữ khỏe từ gốc mới đẹp bền lâu, chị nhắn ngay Điều Kinh Hát Tê để Hằng Thu tư vấn riêng nhé.", "Phụ nữ khỏe từ gốc mới đẹp bền lâu, chị nhắn ngay Điều Kinh HT để Hằng Thu tư vấn riêng nhé.", ["bền lâu", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Sau tuổi 30 bận rộn <span class="cap-kw">giữa nhịp sống mỗi ngày,</span>', 'Nhiều chị thấy kỳ dâu lệch <span class="cap-kw">nhưng vội bỏ qua.</span>'),
            ("vo_02", 'Khi khí huyết kém lưu thông <span class="cap-kw">gây đau bụng mệt mỏi,</span>', 'Sắc diện chị em cũng <span class="cap-kw">kém phần tươi tắn.</span>'),
            ("vo_03", 'Hãy yêu chiều cơ thể <span class="cap-kw">từ gốc bên trong</span>', 'Cùng Viên Uống <span class="cap-kw">Điều Kinh HT Hằng Thu.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Đương quy, Hương phụ</span> giúp bổ huyết, lưu thông,', 'Hỗ trợ điều hòa chu kỳ <span class="cap-kw">êm dịu ngày đèn đỏ.</span>'),
        ],
    },

    # 05 — DDVS Romance VIP
    {
        "idx": 5, "vkey": "v05_romance_vip", "code": "V05",
        "folder_title": "261125 - 05 - DDVS Romance VIP - Rửa nhiều lần chưa chắc sạch đúng chuẩn pH",
        "final_mp4": "261125 HTPM dung dịch Romance VIP rửa đúng cách giữ ẩm mềm mịn chuẩn pH final.mp4",
        "jpg_name": "261125 HTPM thiết kế 05 DDVS Romance VIP hàng dừa resort biển Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 05 DDVS Romance VIP hàng dừa resort biển Nha Trang.psd",
        "sku": "SP04 — DDVS Romance VIP",
        "cutout": "SP_ROMANCE_VIP_CUTOUT.png",
        "fb_ref": "13_nha_trang_resort_pink_maxi_lawn.jpg",
        "fb_s02_ref": "14_nha_trang_palm_garden_sunlit.jpg",
        "outfit": "Wearing a flattering waist-cinched ruby-rose silk resort midi dress that accentuates her tall 170cm statuesque posture and full feminine S-line hourglass curves, with pearl drop earrings. ",
        "scene_post": "in a sunlit Nha Trang beachfront resort palm garden with turquoise sea breeze and white marble walkway",
        "scene_vid": "on a sunlit coastal resort terrace overlooking coconut palms and clear blue Nha Trang ocean",
        "pri": "#C2184B", "pri_dark": "#4A091E", "pri_soft": "#FFE6EE", "grad_mid": "#FF7EA5",
        "accent_soft": "rgba(194, 24, 75, 0.16)", "wash_rgb": (255, 250, 252, 165),
        "prod_h": 540, "prod_cx": 335, "prod_by": 1800, "pack_w": 175, "s4_pack_h": 585,
        "kicker": "Hiểu đúng vệ sinh dịu nhẹ • Nắng biển Nha Trang",
        "hook_l1": "Rửa thật nhiều lần,",
        "hook_l2": "chưa chắc bằng <em>dịu nhẹ</em>",
        "hook_l3": "đúng chuẩn tự nhiên.",
        "script_top": "Tinh chất thảo dược", "prod_title": "Romance VIP",
        "subclaim": "Làm sạch êm dịu • Dưỡng ẩm • Không khô căng",
        "pills": [
            "Thành phần thiên nhiên làm sạch dịu êm không gây khô",
            "Dưỡng ẩm giúp vùng da nhạy cảm luôn mềm mại",
            "Ngăn mùi khó chịu • Giữ cảm giác sạch mát cả ngày",
        ],
        "footer_l": "Tinh chất thảo dược vệ sinh phụ nữ cao cấp Romance VIP 150ml", "footer_r": "Giữ lửa hạnh phúc",
        "caption": "Trời nắng nóng ở biển Nha Trang, nhiều chị có thói quen rửa thật nhiều lần bằng xà phòng mạnh mà không biết càng làm vùng nhạy cảm khô rát.\n\nQuan trọng nhất là chọn đúng tinh chất thảo dược dịu nhẹ như Romance VIP Hằng Thu — sạch thoáng, ngăn mùi mà da vẫn ẩm mịn tự nhiên.\n\nNhắn Hằng Thu để sở hữu ngay chai Romance VIP chính hãng nhé!\n#HangThuPharma #RomanceVIP #ChamSocDiuNhe #NhaTrang",
        "hook_kicker": "TRỜI NẮNG NÓNG OI BỨC", "hook_hero": "Càng rửa càng khô căng?",
        "slide1_hdr": "Sai lầm khi chọn dung dịch vệ sinh",
        "slide1_rows": ["Dùng sản phẩm tẩy mạnh làm mất độ ẩm", "Rửa quá nhiều lần gây khô rát khó chịu", "Mùi hương gắt nhưng nhanh bí bách trở lại"],
        "slide2_pill": "Làm sạch dịu nhẹ từ thiên nhiên<br/>Romance VIP Hằng Thu",
        "pack_kicker": "DƯỠNG ẨM • SẠCH THOÁNG ÊM ÁI", "pack_hero": "Romance VIP",
        "slide3_pills": ["Làm sạch nhẹ nhàng không gây khô căng", "Dưỡng ẩm cho vùng da nhạy cảm mềm mại", "Ngăn mùi hôi, thơm dịu mát tự nhiên"],
        "end_cat": "TINH CHẤT THẢO DƯỢC VỆ SINH", "end_name": "Romance VIP", "end_sub": "DƯỠNG ẨM • NGĂN MÙI • SẠCH DỊU ÊM",
        "cta_txt": "Nhắn ngay “ROMANCE VIP” · Tư vấn 1:1",
        "legal_txt": "Chai 150ml chính hãng Hằng Thu Pharma · Dịu êm cho phái đẹp",
        "segments": [
            ("vo_01", "Những ngày nắng rực rỡ ở biển Nha Trang, nhiều chị tưởng rửa vùng nhạy cảm thật nhiều lần bằng chất tẩy mạnh thì sẽ càng sạch sẽ.", "Những ngày nắng rực rỡ ở biển Nha Trang, nhiều chị tưởng rửa vùng nhạy cảm thật nhiều lần bằng chất tẩy mạnh thì sẽ càng sạch sẽ.", ["nha trang", "sạch sẽ"]),
            ("vo_02", "Thế nhưng chất tẩy mạnh lại cuốn trôi lớp ẩm tự nhiên, làm da khô căng rát mà cảm giác bí bách vẫn quay trở lại.", "Thế nhưng chất tẩy mạnh lại cuốn trôi lớp ẩm tự nhiên, làm da khô căng rát mà cảm giác bí bách vẫn quay trở lại.", ["tự nhiên", "khô căng"]),
            ("vo_03", "Thay vì rửa nhiều, chị Hằng chọn làm sạch đúng cách cùng tinh chất thảo dược Rô Man Vi Ai Pi Hằng Thu.", "Thay vì rửa nhiều, chị Hằng chọn làm sạch đúng cách cùng tinh chất thảo dược Romance VIP Hằng Thu.", ["đúng cách", "hằng thu"]),
            ("vo_04", "Thành phần từ thiên nhiên giúp làm sạch êm dịu, dưỡng ẩm mềm mại, ngăn mùi hôi và giữ cảm giác sạch sẽ mát mẻ suốt ngày dài.", "Thành phần từ thiên nhiên giúp làm sạch êm dịu, dưỡng ẩm mềm mại, ngăn mùi hôi và giữ cảm giác sạch sẽ mát mẻ suốt ngày dài.", ["thiên nhiên", "dưỡng ẩm", "mát mẻ"]),
            ("vo_05", "Nâng niu cơ thể đúng chuẩn dịu êm, chị nhắn ngay Rô Man Vi Ai Pi cho Hằng Thu nhé.", "Nâng niu cơ thể đúng chuẩn dịu êm, chị nhắn ngay Romance VIP cho Hằng Thu nhé.", ["dịu êm", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Những ngày nắng rực rỡ <span class="cap-kw">ở biển Nha Trang,</span>', 'Tưởng rửa thật nhiều lần <span class="cap-kw">là sẽ sạch thoáng?</span>'),
            ("vo_02", 'Chất tẩy mạnh dễ làm <span class="cap-kw">mất độ ẩm tự nhiên,</span>', 'Khiến vùng da nhạy cảm <span class="cap-kw">khô căng, kém êm ái.</span>'),
            ("vo_03", 'Thay vì rửa nhiều, <span class="cap-kw">chị Hằng chọn đúng cách</span>', 'Cùng tinh chất thảo dược <span class="cap-kw">Romance VIP Hằng Thu.</span>'),
            ("vo_04", 'Từ thiên nhiên giúp <span class="cap-kw">dưỡng ẩm mềm mại, ngăn mùi,</span>', 'Giữ trọn cảm giác <span class="cap-kw">sạch mát suốt ngày dài.</span>'),
        ],
    },

    # 06 — Legend WhiteSkin
    {
        "idx": 6, "vkey": "v06_whiteskin", "code": "V06",
        "folder_title": "261125 - 06 - Viên Uống WhiteSkin - Chỉ bôi kem chống nắng chưa đủ sáng mịn",
        "final_mp4": "261125 HTPM viên uống WhiteSkin dưỡng sáng từ gốc dưới nắng biển Nha Trang final.mp4",
        "jpg_name": "261125 HTPM thiết kế 06 Legend WhiteSkin dạo biển Trần Phú Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 06 Legend WhiteSkin dạo biển Trần Phú Nha Trang.psd",
        "sku": "SP08 — Viên Uống Trắng Da Legend WhiteSkin",
        "cutout": "SP_WHITESKIN_COMBO_CUTOUT.png",
        "fb_ref": "10_white_belted_blazer_dress_sunlit.jpg",
        "fb_s02_ref": "09_lime_green_modern_suit.jpg",
        "outfit": "Wearing a sharply tailored belted pure-white fitted blazer-dress cinched at the waist, emphasizing her tall 170cm model-like posture and full feminine S-line hourglass proportions. ",
        "scene_post": "along the sunlit coastal promenade overlooking crystal-blue Nha Trang bay and palm trees",
        "scene_vid": "on a sunlit glass ocean-view terrace overlooking turquoise Nha Trang bay",
        "pri": "#0072B8", "pri_dark": "#072A4A", "pri_soft": "#E3F4FF", "grad_mid": "#6CD0FF",
        "accent_soft": "rgba(0, 114, 184, 0.18)", "wash_rgb": (247, 252, 255, 168),
        "prod_h": 465, "prod_cx": 365, "prod_by": 1800, "pack_w": 245, "s4_pack_h": 565,
        "kicker": "Bí quyết làn da trong trẻo dưới nắng Nha Trang",
        "hook_l1": "Che chắn bên ngoài,",
        "hook_l2": "kết hợp <em>nuôi dưỡng da</em>",
        "hook_l3": "tươi sáng từ bên trong.",
        "script_top": "Viên uống dưỡng sáng", "prod_title": "WhiteSkin",
        "subclaim": "L-Glutathione • NMN • Peptide-GP • Vitamin E",
        "pills": [
            "Bổ sung L-Glutathione & NMN nuôi dưỡng làn da sáng mịn",
            "Amino Acid Peptide-GP chăm sóc bề mặt da căng mượt",
            "Vitamin E hỗ trợ chống oxy hóa trước nắng gió mỗi ngày",
        ],
        "footer_l": "Thực phẩm bổ sung Legend WhiteSkin • Hộp 30 viên chính hãng", "footer_r": "Nhận liệu trình da",
        "caption": "Sống ở thành phố biển Nha Trang đầy nắng, Hằng hiểu rằng chỉ bôi kem bên ngoài thôi thì làn da sau tuổi 30 vẫn rất dễ sạm màu, khô ráp.\n\nMỗi sáng Hằng kết hợp bổ sung Legend WhiteSkin với L-Glutathione, NMN, Peptide và Vitamin E để nuôi da sáng khỏe, trong trẻo từ gốc.\n\nChị nhắn Hằng Thu để được tư vấn liệu trình sáng da nhé!\n#HangThuPharma #LegendWhiteSkin #ChamDaTuGoc #NhaTrang",
        "hook_kicker": "CHỈ CHE NẮNG TỪ BÊN NGOÀI", "hook_hero": "Sao da vẫn sạm màu?",
        "slide1_hdr": "Vì sao thoa kem mãi chưa đủ?",
        "slide1_rows": ["Tia nắng & gốc tự do tác động sâu dưới da", "Thiếu dưỡng chất nội sinh sau tuổi 30", "Da dễ xỉn màu, khô ráp kém rạng rỡ"],
        "slide2_pill": "Nuôi da sáng khỏe từ bên trong<br/>Legend WhiteSkin",
        "pack_kicker": "L-GLUTATHIONE • NMN • VITAMIN E", "pack_hero": "WhiteSkin",
        "slide3_pills": ["L-Glutathione & NMN dưỡng da tươi sáng", "Amino Acid Peptide-GP nuôi da mịn màng", "Vitamin E hỗ trợ chống oxy hóa bền bỉ"],
        "end_cat": "VIÊN UỐNG DƯỠNG SÁNG DA", "end_name": "WhiteSkin", "end_sub": "L-GLUTATHIONE • NMN • VITAMIN E",
        "cta_txt": "Nhắn ngay “WHITESKIN” · Nhận liệu trình",
        "legal_txt": "Thực phẩm bổ sung Legend WhiteSkin · Hộp 30 viên chính hãng",
        "segments": [
            ("vo_01", "Dạo bước dưới nắng biển Trần Phú Nha Trang, nhiều chị thắc mắc sao mình che chắn kỹ lắm mà làn da vẫn xỉn màu và kém tươi?", "Dạo bước dưới nắng biển Trần Phú Nha Trang, nhiều chị thắc mắc sao mình che chắn kỹ lắm mà làn da vẫn xỉn màu và kém tươi?", ["nha trang", "làn da"]),
            ("vo_02", "Bởi sau tuổi ba mươi, nếu chỉ bảo vệ bên ngoài mà thiếu đi nguồn dưỡng chất chống ô xy hóa từ bên trong thì da rất nhanh khô sạm.", "Bởi sau tuổi 30, nếu chỉ bảo vệ bên ngoài mà thiếu đi nguồn dưỡng chất chống oxy hóa từ bên trong thì da rất nhanh khô sạm.", ["bên ngoài", "bên trong"]),
            ("vo_03", "Đó là lý do mỗi sáng Hằng luôn kết hợp nuôi dưỡng làn da cùng Viên Uống Lê Gần Goai Sờ Kin.", "Đó là lý do mỗi sáng Hằng luôn kết hợp nuôi dưỡng làn da cùng Viên Uống Legend WhiteSkin.", ["mỗi sáng", "làn da"]),
            ("vo_04", "Bảng thành phần hội tụ Lờ Gờ Lu Ta Thi On, En Em En, A xít A min Pép Tai và Vi Ta Min E giúp hỗ trợ chống ô xy hóa, cho làn da sáng mịn trong trẻo.", "Bảng thành phần hội tụ L-Glutathione, NMN, Amino Acid Peptide và Vitamin E giúp hỗ trợ chống oxy hóa, cho làn da sáng mịn trong trẻo.", ["sáng mịn", "trong trẻo"]),
            ("vo_05", "Muốn da sáng khỏe tự tin cam thường, chị nhắn ngay Goai Sờ Kin cho Hằng Thu nhé.", "Muốn da sáng khỏe tự tin cam thường, chị nhắn ngay WhiteSkin cho Hằng Thu nhé.", ["sáng khỏe", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Dưới nắng biển <span class="cap-kw">Trần Phú Nha Trang rực rỡ,</span>', 'Che chắn kỹ bên ngoài <span class="cap-kw">sao da vẫn xỉn màu?</span>'),
            ("vo_02", 'Sau tuổi 30 nếu thiếu <span class="cap-kw">dưỡng chất từ bên trong,</span>', 'Làn da rất dễ khô ráp <span class="cap-kw">&amp; kém vẻ tươi sáng.</span>'),
            ("vo_03", 'Mỗi sáng Hằng luôn <span class="cap-kw">nuôi dưỡng làn da</span>', 'Từ bên trong cùng <span class="cap-kw">Legend WhiteSkin.</span>'),
            ("vo_04", 'Hội tụ <span class="cap-kw">L-Glutathione, NMN, Peptide &amp; Vitamin E,</span>', 'Hỗ trợ chống oxy hóa, cho <span class="cap-kw">da sáng mịn trong trẻo.</span>'),
        ],
    },

    # 07 — Viên Đặt Phụ Khoa Hộp Xanh
    {
        "idx": 7, "vkey": "v07_vien_dat_xanh", "code": "V07",
        "folder_title": "261125 - 07 - Viên Đặt Phụ Khoa Hộp Xanh - Sau sinh đừng âm thầm chịu đựng",
        "final_mp4": "261125 HTPM viên đặt phụ khoa Hằng Thu sạch thoáng săn chắc sau sinh final.mp4",
        "jpg_name": "261125 HTPM thiết kế 07 Viên Đặt Phụ Khoa Hằng Thu phòng CEO Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 07 Viên Đặt Phụ Khoa Hằng Thu phòng CEO Nha Trang.psd",
        "sku": "SP05 — Viên Đặt Phụ Khoa Hằng Thu (Hộp Xanh)",
        "cutout": "SP_VIEN_DAT_HOP_XANH_CUTOUT.png",
        "fb_ref": "05_beige_blazer_bni_nha_trang.jpg",
        "fb_s02_ref": "01_ceo_white_draped_blazer_office.jpg",
        "outfit": "Wearing a refined waist-cinched cream-ivory tailored blazer-suit with emerald-green gemstone earrings, highlighting her tall 170cm statuesque posture and full S-line hourglass figure. ",
        "scene_post": "in a sunlit white marble executive CEO office in Nha Trang with ocean view and tropical greenery",
        "scene_vid": "in a bright sunlit white marble suite in Nha Trang overlooking palm trees and blue sea",
        "pri": "#1E6B43", "pri_dark": "#0C331E", "pri_soft": "#E6F5EC", "grad_mid": "#68C994",
        "accent_soft": "rgba(30, 107, 67, 0.18)", "wash_rgb": (248, 253, 250, 168),
        "prod_h": 310, "prod_cx": 385, "prod_by": 1790, "pack_w": 260, "s4_pack_h": 380,
        "kicker": "Đồng hành cùng phụ nữ sau sinh • Hằng Thu Pharma",
        "hook_l1": "Thiên chức làm mẹ,",
        "hook_l2": "xứng đáng được <em>chăm sóc</em>",
        "hook_l3": "sạch thoáng & tự tin.",
        "script_top": "Thảo mộc truyền thống", "prod_title": "VIÊN ĐẶT HẰNG THU",
        "subclaim": "Làm sạch • Săn khít • Duy trì độ ẩm & pH",
        "pills": [
            "Hỗ trợ làm sạch thoáng và khít hồng vùng nhạy cảm",
            "Duy trì độ ẩm cùng độ pH tự nhiên êm dịu",
            "Ngăn ngừa nguy cơ viêm nhiễm, nấm ngứa, khí hư có mùi",
        ],
        "footer_l": "Viên Đặt Phụ Khoa Hằng Thu chính hãng • Thấu hiểu phụ nữ sau sinh", "footer_r": "Tư vấn riêng 1:1",
        "caption": "Sau sinh nở, cơ thể người phụ nữ trải qua biết bao thay đổi thầm kín mà đôi khi ngại chia sẻ cùng ai.\n\nViên Đặt Phụ Khoa Hằng Thu (Hộp Xanh) đồng hành giúp làm sạch thoáng, hỗ trợ săn khít, duy trì độ ẩm pH tự nhiên và ngăn ngừa khí hư có mùi.\n\nChị cứ nhắn riêng để Hằng Thu lắng nghe và tư vấn tận tình nhé!\n#HangThuPharma #VienDatHangThu #PhuNuSauSinh #NhaTrang",
        "hook_kicker": "NHỮNG NỖI NIỀM PHỤ NỮ SAU SINH", "hook_hero": "Âm thầm chịu đựng?",
        "slide1_hdr": "Nỗi trăn trở khó giấu sau sinh",
        "slide1_rows": ["Cảm giác giãn rộng, giảm độ săn chắc", "Khí hư ra nhiều kèm mùi hôi khó nói", "Ngại ngần mỗi khi gần gũi bạn đời"],
        "slide2_pill": "Thấu hiểu phụ nữ sau sinh<br/>Viên Đặt Phụ Khoa Hằng Thu",
        "pack_kicker": "SẠCH THOÁNG • SĂN KHÍT TỰ NHIÊN", "pack_hero": "Viên Đặt Hằng Thu",
        "slide3_pills": ["Hỗ trợ làm sạch khít vùng nhạy cảm", "Duy trì độ ẩm và pH tự nhiên êm ái", "Ngăn ngừa viêm nhiễm, nấm ngứa, mùi hôi"],
        "end_cat": "CHĂM SÓC CHUYÊN BIỆT SAU SINH", "end_name": "Viên Đặt Hằng Thu", "end_sub": "SẠCH THOÁNG • KHÍT HỒNG • CHUẨN PH",
        "cta_txt": "Nhắn ngay “VIÊN ĐẶT” · Nhận liệu trình kín đáo",
        "legal_txt": "Sản phẩm chính hãng Hằng Thu Pharma · Đồng hành cùng phái đẹp",
        "segments": [
            ("vo_01", "Trò chuyện cùng hàng ngàn chị em từ khắp nơi về với phố biển Nha Trang, Hằng thương nhất những chị sau sinh cứ âm thầm chịu đựng nỗi buồn thầm kín.", "Trò chuyện cùng hàng ngàn chị em từ khắp nơi về với phố biển Nha Trang, Hằng thương nhất những chị sau sinh cứ âm thầm chịu đựng nỗi buồn thầm kín.", ["nha trang", "sau sinh"]),
            ("vo_02", "Cảm giác kém săn chắc, khí hư có mùi hay ngứa ngáy tái đi tái lại làm người phụ nữ mất hẳn sự tự tin bên chồng.", "Cảm giác kém săn chắc, khí hư có mùi hay ngứa ngáy tái đi tái lại làm người phụ nữ mất hẳn sự tự tin bên chồng.", ["săn chắc", "tự tin"]),
            ("vo_03", "Đừng giữ nỗi lo ấy một mình, hãy để Viên Đặt Phụ Khoa Hằng Thu hộp xanh nâng niu chị.", "Đừng giữ nỗi lo ấy một mình, hãy để Viên Đặt Phụ Khoa Hằng Thu hộp xanh nâng niu chị.", ["phụ khoa", "hằng thu"]),
            ("vo_04", "Sản phẩm hỗ trợ làm sạch khít vùng nhạy cảm, duy trì độ ẩm và độ pê hát tự nhiên, đồng thời ngăn ngừa viêm nhiễm, nấm ngứa và khí hư có mùi.", "Sản phẩm hỗ trợ làm sạch khít vùng nhạy cảm, duy trì độ ẩm và độ pH tự nhiên, đồng thời ngăn ngừa viêm nhiễm, nấm ngứa và khí hư có mùi.", ["độ ẩm", "tự nhiên", "nấm ngứa"]),
            ("vo_05", "Lấy lại nét xuân tự tin sau sinh, chị nhắn ngay Viên Đặt để Hằng Thu tư vấn kín đáo nhé.", "Lấy lại nét xuân tự tin sau sinh, chị nhắn ngay Viên Đặt để Hằng Thu tư vấn kín đáo nhé.", ["tự tin", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Lắng nghe tâm sự <span class="cap-kw">của hàng ngàn chị em sau sinh,</span>', 'Đừng âm thầm chịu đựng <span class="cap-kw">những đổi thay thầm kín!</span>'),
            ("vo_02", 'Cảm giác kém săn chắc, <span class="cap-kw">khí hư hay mùi khó nói</span>', 'Làm vơi đi sự tự tin <span class="cap-kw">bên người bạn đời.</span>'),
            ("vo_03", 'Đừng giữ nỗi lo một mình, <span class="cap-kw">hãy để Hằng Thu</span>', 'Đồng hành cùng <span class="cap-kw">Viên Đặt Phụ Khoa Hộp Xanh.</span>'),
            ("vo_04", 'Hỗ trợ <span class="cap-kw">làm sạch khít, duy trì ẩm &amp; pH tự nhiên,</span>', 'Ngăn ngừa nấm ngứa &amp; <span class="cap-kw">khí hư có mùi.</span>'),
        ],
    },

    # 08 — Viên Dưỡng Romance Love
    {
        "idx": 8, "vkey": "v08_romance_love", "code": "V08",
        "folder_title": "261125 - 08 - Viên Dưỡng Romance Love - Giữ lửa hôn nhân bắt đầu từ nâng niu chính mình",
        "final_mp4": "261125 HTPM viên dưỡng Romance Love nâng niu nét xuân giữ lửa yêu thương final.mp4",
        "jpg_name": "261125 HTPM thiết kế 08 Romance Love trà chiều hướng biển Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 08 Romance Love trà chiều hướng biển Nha Trang.psd",
        "sku": "SP06 — Viên Dưỡng Romance Love",
        "cutout": "SP_ROMANCE_LOVE_CUTOUT.png",
        "fb_ref": "12_white_suit_pink_rose_lifestyle.jpg",
        "fb_s02_ref": "08_pastel_ice_blue_ruffle_dress.jpg",
        "outfit": "Wearing a chic waist-cinched ivory tweed fitted jacket and matching tailored skirt set with delicate pearl buttons, highlighting her tall 170cm posture and full S-line hourglass curves. ",
        "scene_post": "in an airy sunlit coastal glass tea lounge in Nha Trang with fresh blush-pink roses and calm turquoise sea",
        "scene_vid": "on a sunlit white coastal terrace in Nha Trang with pink roses and turquoise sea bokeh",
        "pri": "#C91458", "pri_dark": "#470821", "pri_soft": "#FFE6F0", "grad_mid": "#FF80B3",
        "accent_soft": "rgba(201, 20, 88, 0.16)", "wash_rgb": (255, 249, 252, 166),
        "prod_h": 345, "prod_cx": 375, "prod_by": 1795, "pack_w": 255, "s4_pack_h": 450,
        "kicker": "Trà chiều phố biển & Câu chuyện giữ lửa yêu thương",
        "hook_l1": "Giữ lửa hôn nhân,",
        "hook_l2": "bắt đầu từ <em>yêu chiều</em>",
        "hook_l3": "cảm xúc của chính mình.",
        "script_top": "Viên dưỡng trẻ hóa dịu êm", "prod_title": "ROMANCE LOVE",
        "subclaim": "Cấp ẩm mềm mịn • Tươi sáng • Trọn cảm xúc",
        "pills": [
            "Dưỡng ẩm chuyên sâu, xoa dịu cảm giác khô hạn",
            "Chăm sóc vùng nhạy cảm mềm mịn, hồng hào tươi sáng",
            "Hộp 5 viên tinh tế • Nâng niu hạnh phúc lứa đôi",
        ],
        "footer_l": "Viên dưỡng Romance Love chính hãng Hằng Thu Pharma", "footer_r": "Trò chuyện riêng 1:1",
        "caption": "Bên tách trà chiều nhìn ra biển Nha Trang êm ả, Hằng nhận ra người phụ nữ hạnh phúc nhất là khi biết yêu chiều cảm xúc của chính mình.\n\nĐừng để sự khô hạn làm phai nhạt khoảnh khắc vợ chồng — Romance Love giúp dưỡng ẩm mềm mịn, giữ trọn nét quyến rũ tự nhiên.\n\nNhắn riêng cho Hằng Thu để được tư vấn kín đáo chị nhé!\n#HangThuPharma #RomanceLove #GiuLuaHonNhan #NhaTrang",
        "hook_kicker": "KHI CHUYỆN VỢ CHỒNG KÉM TỰ NHIÊN", "hook_hero": "Do tuổi tác hay thiếu ẩm?",
        "slide1_hdr": "Rào cản thầm lặng trong hôn nhân",
        "slide1_rows": ["Cảm giác khô rát làm chị e ngại gần gũi", "Tưởng do tuổi tác nên đành cam chịu", "Khoảng cách vợ chồng xa dần lúc nào không hay"],
        "slide2_pill": "Cấp ẩm mềm mịn đầy tinh tế<br/>Romance Love Hằng Thu",
        "pack_kicker": "DƯỠNG ẨM • MỀM MỊN • QUYẾN RŨ", "pack_hero": "Romance Love",
        "slide3_pills": ["Cấp ẩm dịu êm, xoa dịu nỗi lo khô hạn", "Nuôi dưỡng bề mặt mềm mịn, tươi sáng", "Giữ trọn sự tự tin & lửa yêu nồng nàn"],
        "end_cat": "VIÊN DƯỠNG TRẺ HÓA DỊU ÊM", "end_name": "Romance Love", "end_sub": "DƯỠNG ẨM • MỀM MỊN • TƯƠI SÁNG",
        "cta_txt": "Nhắn ngay “ROMANCE LOVE” · Tư vấn kín đáo",
        "legal_txt": "Hộp 5 viên chính hãng Hằng Thu Pharma · Nâng niu phái đẹp",
        "segments": [
            ("vo_01", "Bên tách trà chiều hướng ra biển Nha Trang bình yên, nhiều chị tâm sự với Hằng rằng sau tuổi ba mươi chuyện gần gũi vợ chồng bỗng trở thành áp lực.", "Bên tách trà chiều hướng ra biển Nha Trang bình yên, nhiều chị tâm sự với Hằng rằng sau tuổi 30 chuyện gần gũi vợ chồng bỗng trở thành áp lực.", ["nha trang", "vợ chồng"]),
            ("vo_02", "Không phải vì hết thương, mà chính cảm giác khô hạn kém mềm mại khiến chị em sợ đau rát rồi lặng lẽ né tránh.", "Không phải vì hết thương, mà chính cảm giác khô hạn kém mềm mại khiến chị em sợ đau rát rồi lặng lẽ né tránh.", ["mềm mại", "né tránh"]),
            ("vo_03", "Thương bản thân đúng cách, chị hãy để Viên Dưỡng Rô Man Lốp Hằng Thu nâng niu cảm xúc lứa đôi.", "Thương bản thân đúng cách, chị hãy để Viên Dưỡng Romance Love Hằng Thu nâng niu cảm xúc lứa đôi.", ["bản thân", "hằng thu"]),
            ("vo_04", "Rô Man Lốp hỗ trợ dưỡng ẩm dịu êm, chăm sóc vùng nhạy cảm mềm mịn, tươi sáng để mỗi khoảnh khắc bên nhau luôn trọn vẹn.", "Romance Love hỗ trợ dưỡng ẩm dịu êm, chăm sóc vùng nhạy cảm mềm mịn, tươi sáng để mỗi khoảnh khắc bên nhau luôn trọn vẹn.", ["dưỡng ẩm", "mềm mịn", "trọn vẹn"]),
            ("vo_05", "Giữ lửa yêu thương tinh tế từ hôm nay, chị nhắn ngay Rô Man Lốp cho Hằng Thu nhé.", "Giữ lửa yêu thương tinh tế từ hôm nay, chị nhắn ngay Romance Love cho Hằng Thu nhé.", ["yêu thương", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Bên tách trà chiều <span class="cap-kw">nhìn ra biển Nha Trang,</span>', 'Nhiều chị tâm sự chuyện gần gũi <span class="cap-kw">bỗng thành áp lực.</span>'),
            ("vo_02", 'Chính cảm giác khô hạn, <span class="cap-kw">kém mềm mại tự nhiên</span>', 'Khiến chị em e ngại <span class="cap-kw">rồi lặng lẽ né tránh.</span>'),
            ("vo_03", 'Thương bản thân đúng cách <span class="cap-kw">cùng người bạn tinh tế</span>', 'Viên Dưỡng Trẻ Hóa <span class="cap-kw">Romance Love Hằng Thu.</span>'),
            ("vo_04", 'Giúp <span class="cap-kw">dưỡng ẩm dịu êm, mềm mịn, tươi sáng,</span>', 'Cho khoảnh khắc bên nhau <span class="cap-kw">luôn trọn vẹn lửa yêu.</span>'),
        ],
    },

    # 09 — Ngọc Long Hoàn
    {
        "idx": 9, "vkey": "v09_ngoc_long_hoan", "code": "V09",
        "folder_title": "261125 - 09 - Ngọc Long Hoàn - Bí quyết giữ thể lực bền bỉ cho người thương",
        "final_mp4": "261125 HTPM Ngọc Long Hoàn bồi bổ nguyên khí vững phong độ phái mạnh final.mp4",
        "jpg_name": "261125 HTPM thiết kế 09 Ngọc Long Hoàn món quà sức khỏe từ Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 09 Ngọc Long Hoàn món quà sức khỏe từ Nha Trang.psd",
        "sku": "SP07 — TPBVSK Ngọc Long Hoàn Hằng Thu",
        "cutout": "SP_NGOC_LONG_HOAN_CUTOUT.png",
        "fb_ref": "03_crimson_red_suit_ceo_desk.jpg",
        "fb_s02_ref": "05_beige_blazer_bni_nha_trang.jpg",
        "outfit": "Wearing a sophisticated waist-cinched crimson-burgundy tailored executive blazer-dress that highlights her tall 170cm statuesque posture and full S-line hourglass figure, with gold pearl jewelry. ",
        "scene_post": "in a sunlit luxury coastal executive lounge in Nha Trang with warm natural morning sunlight and ocean horizon",
        "scene_vid": "in a bright sunlit marble lounge overlooking Nha Trang bay with warm coastal daylight",
        "pri": "#9E2A1C", "pri_dark": "#3A0D07", "pri_soft": "#FDECE8", "grad_mid": "#F08C7D",
        "accent_soft": "rgba(158, 42, 28, 0.18)", "wash_rgb": (255, 251, 248, 168),
        "prod_h": 510, "prod_cx": 345, "prod_by": 1800, "pack_w": 190, "s4_pack_h": 575,
        "kicker": "Món quà tinh tế dành tặng người bạn đời",
        "hook_l1": "Đằng sau người đàn ông",
        "hook_l2": "vững vàng <em>phong độ</em>,",
        "hook_l3": "là sự thấu hiểu của vợ.",
        "script_top": "Bổ thận & bồi bổ thể lực", "prod_title": "NGỌC LONG HOÀN",
        "subclaim": "Hỗ trợ bổ thận tráng dương • Giảm mệt mỏi đau lưng",
        "pills": [
            "Hỗ trợ bổ thận, bồi bổ nguyên khí bền vững từ gốc",
            "Giúp giảm mệt mỏi, đau lưng mỏi gối khi làm việc căng thẳng",
            "Duy trì thể lực dẻo dai & bản lĩnh phái mạnh • Lọ 40 viên",
        ],
        "footer_l": "TPBVSK Ngọc Long Hoàn • Không phải là thuốc, không thay thế thuốc chữa bệnh", "footer_r": "Tư vấn bảo mật",
        "caption": "Đàn ông gánh vác công việc áp lực ngoài xã hội thường ít khi than mệt, chỉ có người vợ tinh tế mới nhận ra anh hay đau lưng, xuống sức sau tuổi 35.\n\nMón quà thiết thực nhất chị em dành tặng chồng chính là bồi bổ thể lực bền vững cùng Ngọc Long Hoàn Hằng Thu.\n\nNhắn Hằng Thu để được tư vấn hoàn toàn bảo mật nhé!\n#HangThuPharma #NgocLongHoan #SucKhoePhaiManh #NhaTrang",
        "hook_kicker": "NGƯỜI ĐÀNÔNG ÍT KHI THAN MỆT", "hook_hero": "Chồng xuống sức tuổi 35?",
        "slide1_hdr": "Áp lực âm thầm của phái mạnh",
        "slide1_rows": ["Làm việc căng thẳng làm suy giảm thể lực", "Hay đau lưng mỏi gối, uể oải cuối ngày", "Ngại chia sẻ nhưng phong độ giảm dần"],
        "slide2_pill": "Món quà tinh tế vợ dành tặng chồng<br/>Ngọc Long Hoàn Hằng Thu",
        "pack_kicker": "BỔ THẬN • VỮNG VÀNG PHONG ĐỘ", "pack_hero": "Ngọc Long Hoàn",
        "slide3_pills": ["Hỗ trợ bổ thận, bồi bổ nguyên khí từ gốc", "Giúp giảm mệt mỏi, đau lưng mỏi gối", "Duy trì thể lực dẻo dai & phong độ bền bỉ"],
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE", "end_name": "Ngọc Long Hoàn", "end_sub": "BỒI BỔ THỂ LỰC • VỮNG PHONG ĐỘ",
        "cta_txt": "Nhắn ngay “NGỌC LONG HOÀN” · Tư vấn bảo mật",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "segments": [
            ("vo_01", "Phụ nữ tinh tế luôn nhận ra sau những giờ làm việc căng thẳng, người đàn ông bên cạnh mình bắt đầu hay đau lưng, mỏi gối và xuống sức.", "Phụ nữ tinh tế luôn nhận ra sau những giờ làm việc căng thẳng, người đàn ông bên cạnh mình bắt đầu hay đau lưng, mỏi gối và xuống sức.", ["tinh tế", "đau lưng"]),
            ("vo_02", "Đàn ông thường ít khi than thở, nhưng thể lực suy giảm sau tuổi ba mươi lăm lại ảnh hưởng trực tiếp đến sức khỏe và hạnh phúc gia đình.", "Đàn ông thường ít khi than thở, nhưng thể lực suy giảm sau tuổi 35 lại ảnh hưởng trực tiếp đến sức khỏe và hạnh phúc gia đình.", ["thể lực", "gia đình"]),
            ("vo_03", "Món quà sức khỏe thiết thực Hằng khuyên các chị dành tặng anh nhà chính là Ngọc Long Hoàn Hằng Thu.", "Món quà sức khỏe thiết thực Hằng khuyên các chị dành tặng anh nhà chính là Ngọc Long Hoàn Hằng Thu.", ["sức khỏe", "ngọc long", "hằng thu"]),
            ("vo_04", "Sản phẩm hỗ trợ bổ thận, bồi bổ nguyên khí từ gốc thảo dược, giúp giảm mệt mỏi đau lưng và duy trì phong độ dẻo dai bền bỉ.", "Sản phẩm hỗ trợ bổ thận, bồi bổ nguyên khí từ gốc thảo dược, giúp giảm mệt mỏi đau lưng và duy trì phong độ dẻo dai bền bỉ.", ["bổ thận", "phong độ", "bền bỉ"]),
            ("vo_05", "Chăm chồng khỏe để giữ tổ ấm trọn niềm vui, chị nhắn ngay Ngọc Long Hoàn để Hằng Thu tư vấn bảo mật nhé.", "Chăm chồng khỏe để giữ tổ ấm trọn niềm vui, chị nhắn ngay Ngọc Long Hoàn để Hằng Thu tư vấn bảo mật nhé.", ["tổ ấm", "hằng thu"]),
        ],
        "caps": [
            ("vo_01", 'Phụ nữ tinh tế luôn nhận ra <span class="cap-kw">sau giờ làm căng thẳng,</span>', 'Người bạn đời bắt đầu <span class="cap-kw">đau lưng, xuống sức.</span>'),
            ("vo_02", 'Đàn ông ít khi than thở <span class="cap-kw">chuyện suy giảm thể lực,</span>', 'Nhưng lại ảnh hưởng trực tiếp <span class="cap-kw">hạnh phúc gia đình.</span>'),
            ("vo_03", 'Món quà sức khỏe thiết thực <span class="cap-kw">dành tặng anh nhà</span>', 'Chính là <span class="cap-kw">Ngọc Long Hoàn Hằng Thu.</span>'),
            ("vo_04", 'Hỗ trợ <span class="cap-kw">bổ thận, bồi bổ nguyên khí từ gốc,</span>', 'Giảm mệt mỏi &amp; duy trì <span class="cap-kw">phong độ bền bỉ.</span>'),
        ],
    },

    # 10 — CEO Nguyễn Thị Hằng × Hệ Thống Hằng Thu Pharma Nha Trang
    {
        "idx": 10, "vkey": "v10_ceo_thuong_hieu", "code": "V10",
        "folder_title": "261125 - 10 - CEO Nguyễn Thị Hằng - Kinh doanh bền vững bằng sản phẩm thật giá trị thật",
        "final_mp4": "261125 HTPM CEO Nguyễn Thị Hằng kinh doanh bền vững bằng giá trị thật tại Nha Trang final.mp4",
        "jpg_name": "261125 HTPM thiết kế 10 CEO Nguyễn Thị Hằng truyền lửa từ phố biển Nha Trang.jpg",
        "psd_name": "261125 HTPM thiết kế 10 CEO Nguyễn Thị Hằng truyền lửa từ phố biển Nha Trang.psd",
        "sku": "TH10 — CEO Nguyễn Thị Hằng × Hệ Sinh Thái Hằng Thu Pharma",
        "cutout": "SP_HTPM_ECOSYSTEM_3SKU_CUTOUT.png",
        "fb_ref": "07_navy_blazer_pearl_necklace.jpg",
        "fb_s02_ref": "09_lime_green_modern_suit.jpg",
        "outfit": "Wearing a sharply tailored waist-cinched royal ocean-navy executive suit vest & skirt paired with a luminous white pearl necklace, emphasizing her tall 170cm statuesque posture and full S-line hourglass figure. ",
        "scene_post": "on a sunlit oceanfront conference terrace in Nha Trang overlooking crystal-blue bay and palm trees",
        "scene_vid": "in a sunlit glass ocean-view executive boardroom in Nha Trang overlooking the turquoise bay",
        "pri": "#0066A6", "pri_dark": "#07253D", "pri_soft": "#E4F3FF", "grad_mid": "#5CC4FF",
        "accent_soft": "rgba(0, 102, 166, 0.18)", "wash_rgb": (247, 252, 255, 168),
        "prod_h": 340, "prod_cx": 390, "prod_by": 1795, "pack_w": 280, "s4_pack_h": 410,
        "kicker": "Tầm nhìn thương hiệu từ phố biển Nha Trang",
        "hook_l1": "Đi đường dài bền vững,",
        "hook_l2": "chỉ có thể bằng <em>giá trị thật</em>",
        "hook_l3": "& sự tử tế mỗi ngày.",
        "script_top": "Hơn một thập kỷ tâm huyết", "prod_title": "HẰNG THU PHARMA",
        "subclaim": "Sản phẩm chuẩn mực • Đồng hành 15.000 thành viên",
        "pills": [
            "Hệ sinh thái chăm sóc sức khỏe & sắc đẹp chuẩn chỉnh",
            "Đào tạo bài bản, cầm tay chỉ việc cho phụ nữ khởi nghiệp",
            "Lan tỏa giá trị thật từ Nha Trang đến hàng triệu gia đình Việt",
        ],
        "footer_l": "CEO Nguyễn Thị Hằng • Hệ thống Hằng Thu Pharma toàn quốc", "footer_r": "Đồng hành khởi nghiệp",
        "caption": "Khởi nguồn từ tình yêu với sức khỏe phụ nữ và nắng gió hiền hòa phố biển Nha Trang, Hằng luôn giữ vững một nguyên tắc: Muốn đi đường dài, sản phẩm phải thật và cái tâm phải sáng.\n\nHằng Thu Pharma tự hào đồng hành cùng hàng ngàn chị em tự chủ tài chính và rạng rỡ mỗi ngày.\n\nChị em muốn bứt phá năm mới cùng Hằng thì nhắn ngay nhé!\n#HangThuPharma #CEONguyenThiHang #KinhDoanhTuTe #NhaTrang",
        "hook_kicker": "MUỐN KINH DOANH ĐI ĐƯỜNG DÀI", "hook_hero": "Đừng chạy theo trào lưu!",
        "slide1_hdr": "3 Nền tảng giữ vững Hằng Thu Pharma",
        "slide1_rows": ["Lấy chất lượng sản phẩm thật làm gốc rễ", "Chăm sóc khách hàng bằng sự thấu hiểu", "Đào tạo đội nhóm thực chiến, kỷ luật"],
        "slide2_pill": "Đồng hành cùng phụ nữ tự chủ<br/>CEO Nguyễn Thị Hằng",
        "pack_kicker": "HỆ SINH THÁI CHĂM SÓC TOÀN DIỆN", "pack_hero": "Hằng Thu Pharma",
        "slide3_pills": ["Danh mục sản phẩm thiết yếu, tái mua cao", "Quy trình chuẩn hóa dễ làm cho người mới", "Cộng đồng phụ nữ tích cực, nâng đỡ nhau"],
        "end_cat": "HỆ THỐNG CHĂM SÓC SỨC KHỎE & SẮC ĐẸP", "end_name": "Hằng Thu Pharma", "end_sub": "SẢN PHẨM THẬT • GIÁ TRỊ THẬT • BỀN VỮNG",
        "cta_txt": "Nhắn ngay “ĐỒNG HÀNH” · Kết nối cùng chị Hằng",
        "legal_txt": "CEO Nguyễn Thị Hằng · Hệ thống Hằng Thu Pharma toàn quốc",
        "segments": [
            ("vo_01", "Sống và làm việc tại thành phố biển Nha Trang trong trẻo, nhiều bạn trẻ hỏi Hằng bí quyết nào giúp Hằng Thu Pharma đi vững suốt chặng đường dài.", "Sống và làm việc tại thành phố biển Nha Trang trong trẻo, nhiều bạn trẻ hỏi Hằng bí quyết nào giúp Hằng Thu Pharma đi vững suốt chặng đường dài.", ["nha trang", "hằng thu"]),
            ("vo_02", "Giữa thị trường nhiều trào lưu sớm nở tối tàn, nếu chỉ chạy theo lời quảng cáo hào nhoáng thì khách hàng sẽ chỉ đến một lần rồi đi.", "Giữa thị trường nhiều trào lưu sớm nở tối tàn, nếu chỉ chạy theo lời quảng cáo hào nhoáng thì khách hàng sẽ chỉ đến một lần rồi đi.", ["thị trường", "khách hàng"]),
            ("vo_03", "Câu trả lời của Hằng luôn giản dị: Đặt trọn tâm huyết vào chất lượng sản phẩm thật và sự tử tế với từng chị em.", "Câu trả lời của Hằng luôn giản dị: Đặt trọn tâm huyết vào chất lượng sản phẩm thật và sự tử tế với từng chị em.", ["tâm huyết", "sản phẩm"]),
            ("vo_04", "Từ dòng chăm sóc phụ khoa, nội tiết đến tiêu hóa và sắc đẹp, mỗi sản phẩm Hằng Thu đều hướng tới giá trị thiết yếu để phụ nữ tự tin làm chủ cuộc sống.", "Từ dòng chăm sóc phụ khoa, nội tiết đến tiêu hóa và sắc đẹp, mỗi sản phẩm Hằng Thu đều hướng tới giá trị thiết yếu để phụ nữ tự tin làm chủ cuộc sống.", ["phụ khoa", "hằng thu", "tự tin"]),
            ("vo_05", "Chị em muốn khởi nghiệp bền vững cùng Hằng trong năm mới, hãy nhắn ngay chữ Đồng Hành nhé.", "Chị em muốn khởi nghiệp bền vững cùng Hằng trong năm mới, hãy nhắn ngay chữ Đồng Hành nhé.", ["bền vững", "đồng hành"]),
        ],
        "caps": [
            ("vo_01", 'Từ phố biển <span class="cap-kw">Nha Trang nắng gió trong trẻo,</span>', 'Đâu là gốc rễ giúp <span class="cap-kw">Hằng Thu đi đường dài?</span>'),
            ("vo_02", 'Giữa bao trào lưu <span class="cap-kw">sớm nở tối tàn ngoài kia,</span>', 'Quảng cáo hào nhoáng <span class="cap-kw">không giữ được chân khách.</span>'),
            ("vo_03", 'Nguyên tắc của chị Hằng: <span class="cap-kw">Trọn tâm huyết vào</span>', 'Chất lượng <span class="cap-kw">sản phẩm thật &amp; sự tử tế.</span>'),
            ("vo_04", 'Hệ sinh thái <span class="cap-kw">Hằng Thu Pharma thiết yếu, chuẩn mực,</span>', 'Giúp phụ nữ tự tin <span class="cap-kw">làm chủ cuộc sống.</span>'),
        ],
    },
]
