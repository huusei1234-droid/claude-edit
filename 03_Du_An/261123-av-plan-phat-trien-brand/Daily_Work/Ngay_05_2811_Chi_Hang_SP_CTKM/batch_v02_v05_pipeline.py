# -*- coding: utf-8 -*-
"""
Sản xuất song song 2 luồng dự án Google Flow trên 4 tài khoản đầy điểm (u/3, u/4, u/1, u/6 = 200 credits)
với model `Veo 3.1 - Lite` (720p, 9:16, Ingredients, 10 credits/clip -> đủ 20 clips!)
và dựng hoàn chỉnh có Nhạc Nền chuẩn EQ Voice-Pocket + Sidechain Ducking (-14.5 LUFS, SyncDelta = 0.0s) cho 4 Video (V02..V05):
- V02: 261128 AVPM Chị Hằng ưu đãi sinh nhật Droppii đến 30 tháng 11 final.mp4 (bgm_bright_riley.mp3)
- V03: 261128 AVPM Chị Hằng Collamela chăm da mua 2 tặng 1 final.mp4 (bgm_warm_fretless.mp3)
- V04: 261128 AVPM Chị Hằng Bojomi canxi gia đình mua 3 tặng 1 final.mp4 (bgm_sunny_carefree.mp3)
- V05: 261128 AVPM Chị Hằng AV Protein bữa sáng đạm sạch mua 5 tặng 1 final.mp4 (bgm_coconut_groove_tvc.mp3)
"""
import concurrent.futures
import json, os, re, shutil, subprocess, sys, threading, time, unicodedata
import urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import faster_whisper

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NODE = r"C:\Program Files\nodejs\node.exe"
PY = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
GATE = r"C:\AI\full studio\edit\canvas-tools\video_qc_gate.py"

BASE_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_05_2811_Chi_Hang_SP_CTKM")
ASSETS_DIR = BASE_DIR / "00_Assets"
DRIVE_DIR = Path(r"G:\My Drive\dự án ngoài\An Vượng\03. Video Hoàn Thiện\261128 - Ngày 28.11.2026")
DRIVE_DIR.mkdir(parents=True, exist_ok=True)

BGM_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx")
FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
F_BOLD = str(FONTS_DIR / "BeVietnamPro-Bold.ttf")
F_XBOLD = str(FONTS_DIR / "BeVietnamPro-ExtraBold.ttf")
NVENC = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0"]
DAEMON_PORT = 19489


def strip_accents(s: str) -> str:
    s = s.lower().replace("đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", s)


VOICE_LOCK = (
    "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 35 tuổi, âm sắc trong trẻo ấm áp, nhịp nói vừa phải rõ ràng từng chữ, "
    "CÓ TIẾNG NÓI VIỆT NAM RÕ RÀNG TỪ ĐẦU ĐẾN CUỐI CÂU, đọc đúng 1 lần rồi mỉm cười khép môi nghỉ im lặng (không nuốt chữ, không lặp từ). "
    "Lip-sync khớp môi chính xác 100%. KHÔNG nhạc nền, KHÔNG phụ đề hay chữ trên hình."
)

VIDEOS = [
    {
        "slug": "V02_CTKM_Tong_Hop",
        "group": "A",
        "out_name": "261128 AVPM Chị Hằng ưu đãi sinh nhật Droppii đến 30 tháng 11 final.mp4",
        "bgm": "bgm_bright_riley.mp3",
        "cards": {
            "hook": ("", "ĐỢT CUỐI ĐẾN HẾT 30/11:", "ĐẠI TIỆC QUÀ TẶNG TỚI 920K!"),
            "usp": ("ƯU ĐÃI LỚN NHẤT THÁNG · AN VƯỢNG", "Combo 4 SP (2.440K) • Tặng Collamela 920K", "Mua 3 Bojomi tặng 1 • Mua 4 Nghệ tặng 1"),
            "promo": ("ÁP DỤNG ĐẾN HẾT NGÀY 30/11", "MUA 2 COLLAMELA TẶNG 480K • MUA 5 ĐẠM TẶNG 520K", "Nhắn Chị Hằng giữ quà cho cả gia đình ngay hôm nay"),
        },
        "clips": [
            {
                "id": "s1_speaking",
                "is_speech": True,
                "refs": [("hang_v02_ivory.jpg", "hang_v02_ivory.jpg"), ("sku_combo_4sp_v2.jpg", "sku_combo_4sp.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v02_ivory.jpg (Chị Hằng mặc vest trắng kem thanh lịch)\n- image 2: @sku_combo_4sp_v2.jpg (bộ 4 sản phẩm thật An Vượng Pharma)\n"
                    "Giữ nguyên 100% khuôn mặt thật và bộ vest trắng kem của Chị Hằng trong @hang_v02_ivory.jpg, trên bàn đá trắng bày ngay ngắn bộ 4 hộp @sku_combo_4sp_v2.jpg.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nhìn thẳng ống kính nói rõ ràng: “Cả nhà ơi, đợt cuối mừng sinh nhật của An Vượng chỉ còn đến hết ngày ba mươi tháng này, với quà tặng lớn nhất tháng cho cả nhà!”\n"
                    + VOICE_LOCK
                ),
                "req": ["ca", "nha", "dot", "cuoi", "sinh", "nhat", "an", "vuong", "qua", "tang"],
                "must_30": True,
                "anchor": ["gia", "dinh"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_speaking",
                "is_speech": True,
                "refs": [("hang_v02_ivory.jpg", "hang_v02_ivory.jpg"), ("sku_collamela_v2.jpg", "sku_collamela_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v02_ivory.jpg (Chị Hằng)\n- image 2: @sku_collamela_v2.jpg (hộp quà lớn Collamela)\n"
                    "Giữ nguyên 100% khuôn mặt thật và bộ vest trắng kem của Chị Hằng trong @hang_v02_ivory.jpg, tay nâng nhẹ hộp quà thật @sku_collamela_v2.jpg giới thiệu tươi tắn trên bàn đá trắng sáng trong trẻo.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nói rõ ràng: “Đáng chọn nhất là Combo bốn sản phẩm tặng ngay hộp lớn Collamela chín trăm hai mươi nghìn, lấy ba Bojomi hay bốn Nghệ đều tặng thêm một hộp!”\n"
                    + VOICE_LOCK
                ),
                "req": ["chon", "bon", "san", "pham", "tang", "hop"],
                "anchor": ["mot", "hop"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_broll_4steps",
                "is_speech": False,
                "refs": [("sku_combo_4sp_v2.jpg", "sku_combo_4sp.jpg"), ("sku_collamela_v2.jpg", "sku_collamela_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy morning daylight).\n"
                    "Quay cận cảnh sang trọng lướt mượt trên mặt bàn đá trắng tinh khôi ngập nắng sớm trưng bày sắc nét trọn bộ 4 hộp thật @sku_combo_4sp_v2.jpg (AV Protein, Bojomi, Collamela, Curcumilk Phyto), "
                    "đôi tay thanh lịch mặc vest trắng kem đặt hộp quà tặng @sku_collamela_v2.jpg ngay ngắn cạnh bộ sản phẩm (giữ chuẩn 100% bao bì gốc).\n"
                    "Không lời thoại, không nhạc nền, không hiệu ứng lấp lánh bling, không chữ trên hình."
                ),
            },
            {
                "id": "s3_speaking_promo",
                "is_speech": True,
                "refs": [("hang_v02_ivory.jpg", "hang_v02_ivory.jpg"), ("sku_pair_v2.jpg", "sku_avprotein_bojomi_pair.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v02_ivory.jpg (Chị Hằng)\n- image 2: @sku_pair_v2.jpg (bộ đôi hộp thật AV Protein và Bojomi)\n"
                    "Giữ nguyên 100% khuôn mặt thật và bộ vest trắng kem của Chị Hằng trong @hang_v02_ivory.jpg, trên bàn đá trắng bày ngay ngắn các hộp thật @sku_pair_v2.jpg.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng mỉm cười rạng rỡ nói rõ ràng: “Lấy hai Collamela tặng hộp nhỏ bốn trăm tám mươi nghìn, lấy năm đạm tặng hộp Bojomi năm trăm hai mươi nghìn. Nhắn Hằng trước ngày ba mươi nhé!”\n"
                    + VOICE_LOCK
                ),
                "req": ["hai", "tang", "hop", "nam", "dam"],
                "must_30": True,
                "anchor": ["ba", "muoi"],
                "min_sec": 4.8,
            },
        ],
    },
    {
        "slug": "V03_Collamela",
        "group": "A",
        "out_name": "261128 AVPM Chị Hằng Collamela chăm da mua 2 tặng 1 final.mp4",
        "bgm": "bgm_warm_fretless.mp3",
        "cards": {
            "hook": ("", "SẮP TIỆC CUỐI NĂM:", "ĐỢI SÁT NGÀY MỚI CHĂM DA LÀ MUỘN!"),
            "usp": ("COLLAMELA · AN VƯỢNG PHARMA", "2.530 mg Collagen (Tripeptide) / 2 gói", "Kèm 87 mg Vitamin C & Kẽm • Vị đào thanh mát"),
            "promo": ("ĐỢT CUỐI SINH NHẬT (ĐẾN 30/11)", "MUA 2 HỘP LỚN (1.840K) • TẶNG 1 HỘP 10 GÓI 480K", "Nhắn chữ “DA ĐẸP” để Chị Hằng giữ quà ngay"),
        },
        "clips": [
            {
                "id": "s1_speaking",
                "is_speech": True,
                "refs": [("hang_v03_pink.jpg", "hang_v03_pink.jpg"), ("sku_col_box.jpg", "sku_collamela_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v03_pink.jpg (Chị Hằng mặc áo lụa hồng phấn)\n- image 2: @sku_col_box.jpg (hộp thật ANVUONG COLLAMELA)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo lụa hồng phấn của Chị Hằng trong @hang_v03_pink.jpg, cầm nhẹ hộp thật @sku_col_box.jpg trên bàn đá trắng sáng trong trẻo.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nhìn thẳng ống kính nói rõ ràng: “Cuối năm tiệc tùng liên miên, chị em đợi sát ngày mới chăm da là không kịp đâu. Chọn collagen mỗi ngày, Hằng luôn xem kỹ hàm lượng.”\n"
                    + VOICE_LOCK
                ),
                "req": ["cuoi", "nam", "cham", "da", "khong", "kip", "ham", "luong"],
                "anchor": ["ham", "luong"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_speaking",
                "is_speech": True,
                "refs": [("hang_v03_pink.jpg", "hang_v03_pink.jpg"), ("sku_col_box.jpg", "sku_collamela_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v03_pink.jpg (Chị Hằng)\n- image 2: @sku_col_box.jpg (hộp thật ANVUONG COLLAMELA)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo lụa hồng phấn của Chị Hằng trong @hang_v03_pink.jpg, trên bàn đá trắng đặt hộp @sku_col_box.jpg cạnh ly collagen hồng đào trong trẻo.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nói rõ ràng: “Hai gói Collamela có hơn hai nghìn năm trăm mi-li-gam collagen phân tử nhỏ, thêm vitamin C và kẽm, pha nước mát vị đào thanh nhẹ không tanh.”\n"
                    + VOICE_LOCK
                ),
                "req": ["hai", "goi", "phan", "tu", "nho", "nuoc", "mat", "tanh"],
                "anchor": ["khong", "tanh"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_broll_4steps",
                "is_speech": False,
                "refs": [("sku_col_b.jpg", "sku_collamela_b.jpg"), ("sku_col_box.jpg", "sku_collamela_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy daylight), quay cận cảnh bàn đá trắng tinh khôi đặt sẵn hộp @sku_col_box.jpg sắc nét ở hậu cảnh gần.\n"
                    "Đôi bàn tay thon gọn mặc tay áo lụa hồng phấn thực hiện liền mạch ĐỦ 4 BƯỚC PHA CHẾ nhanh gọn:\n"
                    "(1) Xé đầu gói stick hồng trắng từ @sku_col_b.jpg -> (2) Đổ bột mịn hồng phấn vào ly thủy tinh -> (3) Rót 100ml nước mát trong veo -> (4) Khuấy đều tan nhanh thành ly collagen hồng đào trong trẻo.\n"
                    "Không lời thoại, không nhạc nền, không hiệu ứng lấp lánh bling, không chữ trên hình."
                ),
            },
            {
                "id": "s3_speaking_promo",
                "is_speech": True,
                "refs": [("hang_v03_pink.jpg", "hang_v03_pink.jpg"), ("sku_col_box.jpg", "sku_collamela_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v03_pink.jpg (Chị Hằng)\n- image 2: @sku_col_box.jpg (hộp thật ANVUONG COLLAMELA)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo lụa hồng phấn của Chị Hằng trong @hang_v03_pink.jpg. Trên bàn đá trắng bày 2 hộp @sku_col_box.jpg bên trái và 1 hộp quà @sku_col_box.jpg bên phải.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng tươi tắn nói rõ ràng: “Đến hết ngày ba mươi tháng này, lấy hai hộp lớn Collamela được tặng thêm một hộp mười gói bốn trăm tám mươi nghìn. Nhắn Hằng chữ Da Đẹp nhé!”\n"
                    + VOICE_LOCK
                ),
                "req": ["hai", "hop", "tang", "goi", "da", "dep"],
                "must_30": True,
                "anchor": ["da", "dep"],
                "min_sec": 4.8,
            },
        ],
    },
    {
        "slug": "V04_Bojomi",
        "group": "B",
        "out_name": "261128 AVPM Chị Hằng Bojomi canxi gia đình mua 3 tặng 1 final.mp4",
        "bgm": "bgm_sunny_carefree.mp3",
        "cards": {
            "hook": ("", "HỎI BỐ MẸ ĂN NO CHƯA,", "CÒN ĐỦ CANXI MỖI NGÀY CHƯA?"),
            "usp": ("BOJOMI · CANXI TẢO BIỂN ĐỎ AQUAMIN", "417,6 mg Canxi / gói 20g • D3 + K2 MK-7", "Dạng bột pha ấm vị vani ngũ cốc dễ uống"),
            "promo": ("ĐỢT CUỐI SINH NHẬT (ĐẾN 30/11)", "MUA 3 HỘP BOJOMI (1.560K) • TẶNG 1 HỘP 520K", "Nhắn chữ “CANXI” để giữ quà sức khỏe cho cả nhà"),
        },
        "clips": [
            {
                "id": "s1_speaking",
                "is_speech": True,
                "refs": [("hang_v04_polo.jpg", "hang_v04_polo.jpg"), ("sku_boj_box.jpg", "sku_bojomi_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean morning daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v04_polo.jpg (Chị Hằng mặc áo polo dệt kim trắng kem)\n- image 2: @sku_boj_box.jpg (hộp thật ANVUONG BOJOMI)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo polo trắng kem của Chị Hằng trong @hang_v04_polo.jpg, cầm nhẹ hộp thật @sku_boj_box.jpg trò chuyện ấm áp.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nói rõ ràng: “Mình hay hỏi bố mẹ ăn no chưa, chứ ít để ý bữa hằng ngày đã đủ can-xi chưa. Người lớn ngại nuốt viên thì bột pha ấm dễ uống hơn.”\n"
                    + VOICE_LOCK
                ),
                "req": ["bo", "me", "an", "nguoi", "lon", "pha", "am", "de", "uong"],
                "anchor": ["uong", "hon"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_speaking",
                "is_speech": True,
                "refs": [("hang_v04_polo.jpg", "hang_v04_polo.jpg"), ("sku_boj_box.jpg", "sku_bojomi_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v04_polo.jpg (Chị Hằng)\n- image 2: @sku_boj_box.jpg (hộp thật ANVUONG BOJOMI)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo polo trắng kem của Chị Hằng trong @hang_v04_polo.jpg cùng hộp @sku_boj_box.jpg đặt cạnh ly sữa Bojomi ấm nóng trên bàn sáng.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nói rõ ràng: “Mỗi gói Bojomi hai mươi gam có hơn bốn trăm mi-li-gam can-xi tảo biển đỏ, cùng vi-ta-min D ba, K hai và collagen, vị va-ni ngũ cốc thơm dịu.”\n"
                    + VOICE_LOCK
                ),
                "req": ["moi", "goi", "tao", "bien", "do", "ngu", "coc", "thom", "diu"],
                "anchor": ["thom", "diu"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_broll_4steps",
                "is_speech": False,
                "refs": [("sku_boj_stick.jpg", "sku_bojomi_stick.jpg"), ("sku_boj_box.jpg", "sku_bojomi_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy morning daylight), quay cận cảnh bàn sáng tinh khôi đặt sẵn hộp @sku_boj_box.jpg sắc nét ở hậu cảnh gần.\n"
                    "Đôi bàn tay thon gọn thực hiện liền mạch ĐỦ 4 BƯỚC PHA CHẾ nhanh gọn:\n"
                    "(1) Xé đầu gói stick @sku_boj_stick.jpg -> (2) Đổ bột sữa mịn vào ly thủy tinh -> (3) Rót 150ml nước ấm 45 độ C vào ly -> (4) Khuấy đều tan mịn thành ly sữa canxi sánh mượt.\n"
                    "Không lời thoại, không nhạc nền, không hiệu ứng lấp lánh bling, không chữ trên hình."
                ),
            },
            {
                "id": "s3_speaking_promo",
                "is_speech": True,
                "refs": [("hang_v04_polo.jpg", "hang_v04_polo.jpg"), ("sku_boj_box.jpg", "sku_bojomi_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v04_polo.jpg (Chị Hằng)\n- image 2: @sku_boj_box.jpg (hộp thật ANVUONG BOJOMI)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo polo trắng kem của Chị Hằng trong @hang_v04_polo.jpg. Trên bàn trắng bày cụm 3 hộp @sku_boj_box.jpg bên trái và 1 hộp quà @sku_boj_box.jpg bên phải.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng tươi tắn nói rõ ràng: “Đến hết ngày ba mươi tháng này, cả nhà lấy ba hộp Bojomi được tặng ngay một hộp mới năm trăm hai mươi nghìn. Nhắn Hằng chữ Can-xi nhé!”\n"
                    + VOICE_LOCK
                ),
                "req": ["ca", "nha", "ba", "hop", "tang", "ngay"],
                "must_30": True,
                "anchor": ["can", "xi"],
                "min_sec": 4.8,
            },
        ],
    },
    {
        "slug": "V05_AV_Protein",
        "group": "B",
        "out_name": "261128 AVPM Chị Hằng AV Protein bữa sáng đạm sạch mua 5 tặng 1 final.mp4",
        "bgm": "bgm_coconut_groove_tvc.mp3",
        "cards": {
            "hook": ("", "SÁNG VỘI NGẠI ĂN ĐỒ KHÔ?", "NẠP ĐỦ ĐẠM SẠCH CHỈ 1 PHÚT!"),
            "usp": ("AV PROTEIN · ĐẠM THỰC VẬT SẠCH", "22g Đạm Thực Vật / khẩu phần • Giàu Chất Xơ", "Thêm Inulin & Lợi khuẩn • Nhẹ bụng êm dáng"),
            "promo": ("ĐỢT CUỐI SINH NHẬT (ĐẾN 30/11)", "MUA 5 HỘP AV PROTEIN (1.750K) • TẶNG 1 BOJOMI 520K", "Nhắn chữ “ĐẠM SẠCH” để Chị Hằng giữ quà ngay"),
        },
        "clips": [
            {
                "id": "s1_speaking",
                "is_speech": True,
                "refs": [("hang_v05_mint.jpg", "hang_v05_linen_mint.jpg"), ("sku_pro_box.jpg", "sku_avprotein_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean morning daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v05_mint.jpg (Chị Hằng mặc áo sơ mi linen xanh mint)\n- image 2: @sku_pro_box.jpg (hộp thật ANVUONG AV PROTEIN)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo sơ mi xanh mint của Chị Hằng trong @hang_v05_mint.jpg, cầm nhẹ hộp @sku_pro_box.jpg bên đảo bếp đá trắng ngập nắng sớm.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nói rõ ràng: “Sáng vội đi làm, chị em ngại ăn đồ khô mà bỏ bữa thì mười giờ đã đói cồn cào. Hằng luôn ưu tiên nạp đủ đạm sạch từ sáng.”\n"
                    + VOICE_LOCK
                ),
                "req": ["sang", "di", "lam", "bo", "bua", "doi", "dam", "sach"],
                "anchor": ["tu", "sang"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_speaking",
                "is_speech": True,
                "refs": [("hang_v05_mint.jpg", "hang_v05_linen_mint.jpg"), ("sku_pro_box.jpg", "sku_avprotein_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v05_mint.jpg (Chị Hằng)\n- image 2: @sku_pro_box.jpg (hộp thật ANVUONG AV PROTEIN)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo sơ mi xanh mint của Chị Hằng trong @hang_v05_mint.jpg cùng hộp @sku_pro_box.jpg đặt cạnh ly đạm hạt sánh mịn trên đảo bếp trắng.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng nói rõ ràng: “Một khẩu phần AV Protein có hai mươi hai gam đạm thực vật dễ tiêu hóa, thêm chất xơ và lợi khuẩn giúp nhẹ bụng suốt buổi sáng.”\n"
                    + VOICE_LOCK
                ),
                "req": ["khau", "phan", "hai", "muoi", "dam", "thuc", "vat", "chat", "xo", "nhe", "bung"],
                "anchor": ["buoi", "sang"],
                "min_sec": 4.8,
            },
            {
                "id": "s2_broll_4steps",
                "is_speech": False,
                "refs": [("sku_pro_b.jpg", "sku_avprotein_b.jpg"), ("sku_pro_box.jpg", "sku_avprotein_box.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy morning daylight), quay cận cảnh bàn đá trắng đặt sẵn hộp @sku_pro_box.jpg sắc nét ở hậu cảnh gần.\n"
                    "Đôi bàn tay thon gọn mặc tay áo sơ mi xanh mint thực hiện liền mạch ĐỦ 4 BƯỚC PHA CHẾ nhanh gọn:\n"
                    "(1) Xé đầu gói stick đạm từ @sku_pro_b.jpg -> (2) Đổ bột đạm thực vật mịn vào ly thủy tinh -> (3) Rót 180ml nước ấm vào ly -> (4) Khuấy đều tan mịn thành ly sữa đạm hạt sánh mượt.\n"
                    "Không lời thoại, không nhạc nền, không hiệu ứng lấp lánh bling, không chữ trên hình."
                ),
            },
            {
                "id": "s3_speaking_promo",
                "is_speech": True,
                "refs": [("hang_v05_mint.jpg", "hang_v05_linen_mint.jpg"), ("sku_pro_boj_pair.jpg", "sku_avprotein_bojomi_pair.jpg")],
                "prompt": (
                    "Tạo video dọc 9:16 photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight).\n"
                    "IMAGE XUẤT HIỆN:\n- image 1: @hang_v05_mint.jpg (Chị Hằng)\n- image 2: @sku_pro_boj_pair.jpg (hộp thật AV PROTEIN và hộp quà BOJOMI)\n"
                    "Giữ nguyên 100% khuôn mặt thật và áo sơ mi xanh mint của Chị Hằng trong @hang_v05_mint.jpg. Trên bàn trắng bày cụm 5 hộp AV PROTEIN bên trái và 1 hộp quà BOJOMI bên phải đúng bao bì trong @sku_pro_boj_pair.jpg.\n"
                    "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
                    "Chị Hằng tươi tắn nói rõ ràng: “Đến hết ngày ba mươi tháng này, chị em lấy năm hộp đạm AV Protein được tặng ngay một hộp Bojomi năm trăm hai mươi nghìn. Nhắn chữ Đạm Sạch nhé!”\n"
                    + VOICE_LOCK
                ),
                "req": ["chi", "em", "nam", "hop", "tang", "ngay", "dam", "sach"],
                "must_30": True,
                "anchor": ["dam", "sach"],
                "min_sec": 4.8,
            },
        ],
    },
]

DAEMON_JS = r"""
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const handlers = {};
Module._load = (function(orig){
  return function(req){
    if(req==="electron") return { ipcMain: { handle: (c,f)=>{handlers[c]=f;}, on: ()=>{} }, dialog: { showErrorBox: (t,m)=>console.error(t,m) }, shell: { openExternal: async ()=>{} } };
    return orig.apply(this, arguments);
  };
})(Module._load);

process.on("uncaughtException", (err) => console.error("[DAEMON_UNCAUGHT]", err && err.message ? err.message : err));
process.on("unhandledRejection", (err) => console.error("[DAEMON_UNHANDLED]", err && err.message ? err.message : err));

const DESKTOP = "C:\\AI\\full studio\\canvas\\desktop";
const PRIV = process.argv[2];
const PORT = Number(process.argv[3] || 19489);
const flow = require(path.join(DESKTOP, "flow-driver.js"));

(async () => {
  fs.mkdirSync(PRIV, { recursive: true });
  const now = Date.now();
  const ex = now + 43200000;

  // Create a 2nd clean project on u/9/ (1,050 PRO credits!) via flow.ensureBrowser() so Slot A & Slot B run 2 parallel PRO projects on u/9/!
  const bootCfg = {
    minCredits: { video: 30, image: 5 },
    accounts: [{ id: "a1", name: "Boot u/9", profile: "MAIN_BRAVE", userPrefix: "u/9/", projectId: "44e5d459-c4fe-43e9-a700-a03d1ee35203", agentOwnedProjectIds: ["44e5d459-c4fe-43e9-a700-a03d1ee35203"], workerTargets: [{ prefix: "u/9/", projectId: "44e5d459-c4fe-43e9-a700-a03d1ee35203" }] }],
    active: "a1",
  };
  fs.writeFileSync(path.join(PRIV, "flow-driver.json"), JSON.stringify(bootCfg, null, 2), "utf8");
  flow.setup({ getPath: () => PRIV });

  let pid9_b = null;
  try {
    const b0 = await flow.ensureBrowser({ visible: true });
    await new Promise(r => setTimeout(r, 2000));
    const p = await flow.createBackgroundPage(b0, "https://flow.google.com/u/9/");
    if (p) {
      await new Promise(r => setTimeout(r, 2800));
      await p.evaluate(() => {
        const nb = document.querySelector("button.new-project-button") ||
          [...document.querySelectorAll("button")].find(x => /Dự án mới|New project/i.test(x.innerText || ""));
        if (nb) nb.click();
      }).catch(() => {});
      for (let k = 0; k < 20; k++) {
        await new Promise(r => setTimeout(r, 500));
        const pm = (p.url() || "").match(/\/project\/([0-9a-f-]{20,})/i);
        if (pm) { pid9_b = pm[1]; break; }
      }
      if (pid9_b) {
        await new Promise(r => setTimeout(r, 2000));
        await p.evaluate(() => {
          for (const btn of document.querySelectorAll("button")) {
            const t = (btn.innerText || "").trim();
            if (/^(Bắt đầu|Get started|Got it|Đã hiểu|Đóng|Close|close|right_panel_close)$/i.test(t)) btn.click();
          }
        }).catch(() => {});
      }
      await p.close().catch(() => {});
    }
  } catch (e) {
    console.error("[BOOT_P9B]", e.message);
  }

  const pid9_a = "44e5d459-c4fe-43e9-a700-a03d1ee35203";
  const targets = [
    { prefix: "u/9/", projectId: pid9_a, email: "lmtcvn005@gmail.com" },
    ...(pid9_b ? [{ prefix: "u/9/", projectId: pid9_b, email: "lmtcvn005@gmail.com" }] : []),
    { prefix: "u/6/", projectId: "733dbbe0-6db2-4a31-88e0-f10a19b06fb1", email: "capcutvid269@gmail.com" },
    { prefix: "u/8/", projectId: "bd07af14-1d54-4996-8883-72f2e724d0f5", email: "hieulan14d@gmail.com" },
  ];
  const ownedIds = targets.map(t => t.projectId);
  const prefixCredits = {
    "u/0/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/1/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/2/": { credits: 2, updatedAt: now, exhaustedUntil: ex },
    "u/3/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/4/": { credits: 20, updatedAt: now, exhaustedUntil: ex },
    "u/5/": { credits: 9, updatedAt: now, exhaustedUntil: ex },
    "u/7/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/9/": { credits: 1050, email: "lmtcvn005@gmail.com", updatedAt: now },
    "u/6/": { credits: 50, email: "capcutvid269@gmail.com", updatedAt: now },
    "u/8/": { credits: 22, email: "hieulan14d@gmail.com", updatedAt: now },
  };

  const finalCfg = {
    minCredits: { video: 30, image: 5 },
    accounts: [{
      id: "a1",
      name: "Unified PRO u/9 Pool (1050cr)",
      profile: "MAIN_BRAVE",
      userPrefix: "u/9/",
      projectId: pid9_a,
      preferredEmail: "lmtcvn005@gmail.com",
      agentOwnedProjectIds: ownedIds,
      workerProjectIds: ownedIds,
      prefixCredits,
      workerTargets: targets,
    }],
    active: "a1",
  };
  fs.writeFileSync(path.join(PRIV, "flow-driver.json"), JSON.stringify(finalCfg, null, 2), "utf8");
  flow.setup({ getPath: () => PRIV });

  const srv = http.createServer((req, res) => {
    if (req.url === "/ping") { res.writeHead(200); res.end("OK"); return; }
    if (req.url === "/quit") { res.writeHead(200); res.end("BYE"); setTimeout(() => process.exit(0), 200); return; }
    let body = "";
    req.on("data", ch => { body += ch; });
    req.on("end", async () => {
      try {
        const pl = JSON.parse(body);
        const images = pl.refs.map(r => ({
          name: r.name,
          mime: "image/jpeg",
          base64: fs.readFileSync(r.path).toString("base64"),
        }));
        const out = await handlers["flow:generate-video"](null, {
          prompt: pl.prompt,
          model: "Omni 1.2 Flash",
          aspect: "portrait",
          resolution: "720p",
          seconds: 10,
          mode: "ingredients",
          count: 1,
          images,
        });
        const b64 = out?.data || out?.videoBase64 || out?.items?.[0]?.data || out?.items?.[0]?.base64;
        if (!b64) {
          res.writeHead(500);
          res.end(JSON.stringify({ ok: false, error: out?.error || "empty" }));
          return;
        }
        const buf = Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
        if (buf.length > 200000) {
          fs.writeFileSync(pl.outPath, buf);
          res.writeHead(200);
          res.end(JSON.stringify({ ok: true, kb: Math.round(buf.length / 1024) }));
          return;
        }
        res.writeHead(500);
        res.end(JSON.stringify({ ok: false, error: "SMALL_BUF_" + buf.length }));
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ ok: false, error: String(e.message || e) }));
      }
    });
  });
  srv.listen(PORT, "127.0.0.1", () => console.log(`[DAEMON_READY] http://127.0.0.1:${PORT} targets=${targets.length} (u/9 1050cr)`));
})();
"""


def transcribe_words(mp4_p: Path, asr):
    wav = mp4_p.parent / f"_w_{mp4_p.stem}_{threading.get_ident()}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4_p), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    segs, _ = asr.transcribe(str(wav), language="vi", word_timestamps=True)
    words = [(strip_accents(w.word), round(w.start, 3), round(w.end, 3), w.word.strip()) for s in segs for w in (s.words or []) if strip_accents(w.word)]
    wav.unlink(missing_ok=True)
    return words


SYN = {
    "bon": {"bon", "4"},
    "ba": {"ba", "3"},
    "hai": {"hai", "2", "22", "22g"},
    "nam": {"nam", "5"},
    "mot": {"mot", "1"},
    "muoi": {"muoi", "10", "20", "30", "22", "22g", "10g", "20g"},
    "goi": {"goi", "10g", "20g"},
    "da": {"da", "gia", "ra"},
    "xo": {"xo", "so"},
    "sach": {"sach", "xach"},
}


def verify_speech_clip(mp4_p: Path, clip_cfg: dict, asr) -> tuple[bool, str]:
    words = transcribe_words(mp4_p, asr)
    if not words:
        return False, "NO_SPEECH"
    heard = " ".join(w[3] for w in words)
    toks = [w[0] for w in words]
    tset = set(toks)
    joined_toks = " ".join(toks)
    if "ghien" in tset or "subscribe" in tset or len(words) < 13:
        return False, f"SILENT_OR_TOO_SHORT ({len(words)}w): '{heard}'"
    miss = [k for k in clip_cfg["req"] if not (tset & SYN.get(k, {k}))]
    if miss:
        return False, f"MISS={miss} | '{heard}'"
    if clip_cfg.get("must_30") and not (("30" in joined_toks) or ("ba muoi" in joined_toks)):
        return False, f"MISSING_30 | '{heard}'"
    if "31" in tset:
        return False, f"WRONG_DATE_31 | '{heard}'"
    ALLOWED_1 = {"tu", "deu", "luon", "rat", "lam", "nhieu", "ngay", "doi", "nguoi", "ai", "vua", "de", "hop"}
    for n in (4, 3, 2):
        for i in range(len(toks) - 2 * n + 1):
            if toks[i:i + n] == toks[i + n:i + 2 * n] and (words[i + n][1] - words[i + n - 1][2]) <= 1.85:
                return False, f"REPEAT_{n}GRAM={toks[i:i+n]} | '{heard}'"
    for i in range(len(toks) - 1):
        if len(toks[i]) >= 2 and toks[i] == toks[i + 1] and toks[i] not in ALLOWED_1 and (words[i + 1][1] - words[i][2]) <= 1.50:
            return False, f"REPEAT_1GRAM={toks[i]} | '{heard}'"
    return True, heard


def make_clean_airy_card(out_png: Path, badge: str, line1: str, line2: str = None, is_hook: bool = False, y_top: int = 886):
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    h = 152 if (line2 or is_hook) else 118
    box = (64, y_top, 868, y_top + h)
    sd.rounded_rectangle((box[0] + 4, box[1] + 7, box[2] + 4, box[3] + 7), radius=24, fill=(12, 42, 32, 54))
    ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(7)))
    dr = ImageDraw.Draw(ov)
    dr.rounded_rectangle(box, radius=24, fill=(251, 254, 252, 236), outline=(18, 118, 88, 215), width=3)
    dr.rounded_rectangle((64, box[1], 79, box[3]), radius=8, fill=(14, 112, 82, 255))

    f_badge = ImageFont.truetype(F_XBOLD, 21)
    if is_hook:
        f1 = ImageFont.truetype(F_XBOLD, 34)
        f2 = ImageFont.truetype(F_XBOLD, 37)
        dr.text((96, y_top + 18), line1, font=f1, fill=(18, 52, 40, 255))
        dr.text((96, y_top + 74), line2 or "", font=f2, fill=(186, 108, 12, 255))
    else:
        f1 = ImageFont.truetype(F_XBOLD, 27)
        f2 = ImageFont.truetype(F_BOLD, 24)
        bw = int(dr.textlength(badge, font=f_badge)) + 26
        dr.rounded_rectangle((94, y_top + 12, 94 + bw, y_top + 44), radius=13, fill=(14, 112, 82, 255))
        dr.text((107, y_top + 15), badge, font=f_badge, fill=(255, 255, 255, 255))
        dr.text((96, y_top + 54), line1, font=f1, fill=(18, 48, 38, 255))
        if line2:
            dr.text((96, y_top + 100), line2, font=f2, fill=(175, 98, 10, 255))
    ov.save(out_png)


def get_speech_bounds(mp4_p: Path, anchor: list, min_sec: float, asr, is_last: bool = False):
    raw_dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4_p)], text=True).strip())
    words = transcribe_words(mp4_p, asr)
    if not words:
        return 0.0, raw_dur, raw_dur
    first_st = max(0.0, round(words[0][1] - 0.08, 3))
    end_t = words[-1][2]
    speech_end = round(end_t + 0.10, 3)
    cut_dur = min(raw_dur, round(end_t + (0.65 if is_last else 0.24), 3))
    return first_st, speech_end, cut_dur


def assemble_video_with_bgm(vcfg: dict, asr):
    vdir = BASE_DIR / vcfg["slug"]
    raw_d = vdir / "01_Raw_Clips"
    work_d = vdir / "02_Work"
    fin_d = vdir / "03_Final"
    qc_d = vdir / "04_QC_Gate"
    for d in (work_d, fin_d, qc_d):
        d.mkdir(parents=True, exist_ok=True)

    s1_p = raw_d / "s1_speaking.mp4"
    s2_p = raw_d / "s2_speaking.mp4"
    b2_p = raw_d / "s2_broll_4steps.mp4"
    s3_p = raw_d / "s3_speaking_promo.mp4"

    st1, sp1, dur1 = get_speech_bounds(s1_p, vcfg["clips"][0]["anchor"], vcfg["clips"][0]["min_sec"], asr, is_last=False)
    st2, sp2, dur2 = get_speech_bounds(s2_p, vcfg["clips"][1]["anchor"], vcfg["clips"][1]["min_sec"], asr, is_last=False)
    st3, sp3, dur3 = get_speech_bounds(s3_p, vcfg["clips"][3]["anchor"], vcfg["clips"][3]["min_sec"], asr, is_last=True)

    clean_vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "delogo=x=860:y=1685:w=105:h=105,"
        "delogo=x=1008:y=1868:w=68:h=48,"
        "eq=brightness=0.015:saturation=1.04:contrast=1.02,"
        "fps=24,format=yuv420p"
    )

    p1_out = work_d / "part1.mp4"
    af1 = f"highpass=f=80,loudnorm=I=-14.5:TP=-1.5:LRA=9,volume=0:enable='lt(t,{st1:.3f})',afade=t=in:st={st1:.3f}:d=0.04,afade=t=out:st={max(0.1, sp1-0.02):.3f}:d=0.06,volume=0:enable='gt(t,{sp1+0.04:.3f})'"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(s1_p), "-t", f"{dur1:.3f}", "-vf", clean_vf, "-af", af1, *NVENC, "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(p1_out)], check=True)

    p2_out = work_d / "part2.mp4"
    b_dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(b2_p)], text=True).strip())
    lead_s = min(1.75, round(dur2 * 0.24, 3))
    tail_s = min(1.50, round(dur2 * 0.20, 3))
    mid_len = max(3.6, round(dur2 - lead_s - tail_s, 3))
    speed_factor = round(b_dur / mid_len, 4) if b_dur > mid_len else 1.0
    af2 = f"highpass=f=80,loudnorm=I=-14.5:TP=-1.5:LRA=9,volume=0:enable='lt(t,{st2:.3f})',afade=t=in:st={st2:.3f}:d=0.04,afade=t=out:st={max(0.1, sp2-0.02):.3f}:d=0.06,volume=0:enable='gt(t,{sp2+0.04:.3f})'"
    fc2 = (
        f"[0:v]{clean_vf},split=2[v2a][v2b];"
        f"[v2a]trim=0:{lead_s:.3f},setpts=PTS-STARTPTS[va];"
        f"[1:v]{clean_vf},setpts=PTS/{speed_factor:.4f},trim=0:{mid_len:.3f},setpts=PTS-STARTPTS[vb];"
        f"[v2b]trim={max(0.0, dur2 - tail_s):.3f}:{dur2:.3f},setpts=PTS-STARTPTS[vc];"
        f"[va][vb][vc]concat=n=3:v=1:a=0[v2out];"
        f"[0:a]atrim=0:{dur2:.3f},asetpts=PTS-STARTPTS,{af2}[a2out]"
    )
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(s2_p), "-i", str(b2_p), "-filter_complex", fc2, "-map", "[v2out]", "-map", "[a2out]", *NVENC, "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(p2_out)], check=True)
    p2_vdur = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(p2_out)], text=True).strip())

    p3_out = work_d / "part3.mp4"
    raw_d3 = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(s3_p)], text=True).strip())
    extra_pad = 0.65 if (raw_d3 - sp3) < 0.55 else 0.0
    vf3 = clean_vf + (f",tpad=stop_mode=clone:stop_duration={extra_pad:.2f}" if extra_pad > 0 else "")
    af3 = f"highpass=f=80,loudnorm=I=-14.5:TP=-1.5:LRA=9,volume=0:enable='lt(t,{st3:.3f})',afade=t=in:st={st3:.3f}:d=0.04,afade=t=out:st={max(0.1, sp3-0.02):.3f}:d=0.06,volume=0:enable='gt(t,{sp3+0.04:.3f})'" + (f",apad=pad_dur={extra_pad:.2f}" if extra_pad > 0 else "")
    final_d3 = round(dur3 + extra_pad, 3)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(s3_p), "-t", f"{final_d3:.3f}", "-vf", vf3, "-af", af3, *NVENC, "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(p3_out)], check=True)

    concat_txt = work_d / "concat.txt"
    concat_txt.write_text("file 'part1.mp4'\nfile 'part2.mp4'\nfile 'part3.mp4'\n", encoding="utf-8")
    joined = work_d / "joined.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(joined)], check=True)

    b_st = round(dur1 + lead_s, 3)
    b_step = round(mid_len / 3.0, 3)
    cuts = [
        {"start": 0.0, "end": round(dur1, 3), "label": "s1_mo_dau"},
        {"start": round(dur1, 3), "end": b_st, "label": "s2_gioi_thieu"},
        {"start": b_st, "end": round(b_st + b_step, 3), "label": "s2_broll_step1"},
        {"start": round(b_st + b_step, 3), "end": round(b_st + 2 * b_step, 3), "label": "s2_broll_step2"},
        {"start": round(b_st + 2 * b_step, 3), "end": round(dur1 + lead_s + mid_len, 3), "label": "s2_broll_step3"},
        {"start": round(dur1 + lead_s + mid_len, 3), "end": round(dur1 + p2_vdur, 3), "label": "s2_ket_cau"},
        {"start": round(dur1 + p2_vdur, 3), "end": round(dur1 + p2_vdur + final_d3, 3), "label": "s3_ctkm_den_30_11"},
    ]
    cuts_p = work_d / "cuts.json"
    cuts_p.write_text(json.dumps(cuts, indent=2), encoding="utf-8")

    c_hook, c_usp, c_promo = work_d / "card_hook.png", work_d / "card_usp.png", work_d / "card_promo.png"
    make_clean_airy_card(c_hook, *vcfg["cards"]["hook"], is_hook=True, y_top=886)
    make_clean_airy_card(c_usp, *vcfg["cards"]["usp"], y_top=264)
    make_clean_airy_card(c_promo, *vcfg["cards"]["promo"], y_top=886)

    overlays = [
        (c_hook, 0.12, min(3.10, round(dur1 - 0.3, 2))),
        (c_usp, round(dur1 + lead_s + 0.12, 2), round(dur1 + lead_s + mid_len - 0.12, 2)),
        (c_promo, round(dur1 + p2_vdur + 0.30, 2), round(dur1 + p2_vdur + final_d3 - 0.65, 2)),
    ]

    inputs = ["-i", str(joined)]
    fc_parts, prev = [], "0:v"
    for k, (png_p, st, en) in enumerate(overlays, 1):
        inputs += ["-loop", "1", "-t", f"{en + 0.3:.2f}", "-i", str(png_p)]
        ov_l, nx_l = f"ov{k}", f"v{k}"
        fc_parts.append(
            f"[{k}:v]format=rgba,fade=t=in:st={st:.2f}:d=0.25:alpha=1,fade=t=out:st={max(st+0.3, en-0.25):.2f}:d=0.25:alpha=1[{ov_l}];"
            f"[{prev}][{ov_l}]overlay=0:0:enable='between(t,{st:.2f},{en:.2f})':eof_action=pass[{nx_l}]"
        )
        prev = nx_l

    nobgm_mp4 = work_d / "nobgm_master.mp4"
    fc_str = ";".join(fc_parts) + f";[{prev}]format=yuv420p[vout]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc_str, "-map", "[vout]", "-map", "0:a", *NVENC, "-c:a", "aac", "-b:a", "192k", "-shortest", str(nobgm_mp4)], check=True)

    vdur = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(nobgm_mp4)], text=True).strip())
    bgm_p = BGM_DIR / vcfg["bgm"]
    fc_audio = (
        f"[0:a]atrim=0:{vdur:.3f},asetpts=PTS-STARTPTS,asplit=2[vo_main][vo_sc];"
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{vdur:.3f},asetpts=PTS-STARTPTS,"
        f"highpass=f=90,lowpass=f=11000,"
        f"equalizer=f=1800:t=q:w=1.1:g=-5.0,equalizer=f=3000:t=q:w=1.2:g=-4.0,"
        f"volume=0.14,afade=t=in:st=0:d=0.45,afade=t=out:st={max(0.5, vdur-1.0):.3f}:d=1.00[bgm_pre];"
        f"[bgm_pre][vo_sc]sidechaincompress=threshold=0.03:ratio=4:attack=35:release=320[bgm_duck];"
        f"[vo_main][bgm_duck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"loudnorm=I=-14.5:TP=-1.5:LRA=9,atrim=0:{vdur:.3f},asetpts=PTS-STARTPTS[aout]"
    )
    out_mp4 = fin_d / vcfg["out_name"]
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(nobgm_mp4), "-i", str(bgm_p),
        "-filter_complex", fc_audio, "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        "-movflags", "+faststart", str(out_mp4)
    ], check=True)
    shutil.copy2(out_mp4, DRIVE_DIR / vcfg["out_name"])

    pg = subprocess.run([PY, "-X", "utf8", GATE, "inspect", str(out_mp4), "--cuts-json", str(cuts_p), "--out-dir", str(qc_d)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"[{vcfg['slug']} FINAL + QC GATE rc={pg.returncode} dur={vdur:.2f}s]\n{pg.stdout}", flush=True)


def call_flow_daemon(payload: dict) -> tuple[bool, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"http://127.0.0.1:{DAEMON_PORT}/gen", data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=280) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return bool(res.get("ok")), str(res)
    except urllib.error.HTTPError as he:
        return False, he.read().decode("utf-8", errors="replace")
    except Exception as e:
        return False, str(e)


def run_worker_group(worker_key: str, video_list: list):
    asr = faster_whisper.WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=6)

    for vcfg in video_list:
        vdir = BASE_DIR / vcfg["slug"]
        raw_d = vdir / "01_Raw_Clips"
        raw_d.mkdir(parents=True, exist_ok=True)
        for c in vcfg["clips"]:
            out_mp4 = raw_d / f"{c['id']}.mp4"
            if out_mp4.exists() and out_mp4.stat().st_size > 180000:
                if not c["is_speech"]:
                    print(f"[{vcfg['slug']}:{worker_key}] CACHED {c['id']} OK", flush=True)
                    continue
                ok_c, msg_c = verify_speech_clip(out_mp4, c, asr)
                if ok_c:
                    print(f"[{vcfg['slug']}:{worker_key}] CACHED {c['id']} -> {msg_c}", flush=True)
                    continue

            cand_mp4 = raw_d / f"_cand_{c['id']}.mp4"
            refs_payload = [{"name": rn, "path": str(ASSETS_DIR / fn)} for rn, fn in c["refs"]]
            pl = {
                "refs": refs_payload,
                "outPath": str(cand_mp4),
                "prompt": c["prompt"],
            }

            for att in range(1, 5):
                cand_mp4.unlink(missing_ok=True)
                print(f"[{vcfg['slug']}:{worker_key}] GEN {c['id']} (Veo 3.1 Lite 720p) try {att}/4...", flush=True)
                ok_http, info = call_flow_daemon(pl)
                if not ok_http or not cand_mp4.exists():
                    print(f"  [{vcfg['slug']}:{worker_key}] warn: {info[-180:]}", flush=True)
                    continue
                if not c["is_speech"]:
                    shutil.move(str(cand_mp4), str(out_mp4))
                    print(f"  -> [{vcfg['slug']} B-ROLL OK] {c['id']}", flush=True)
                    break
                ok, msg = verify_speech_clip(cand_mp4, c, asr)
                if ok:
                    shutil.move(str(cand_mp4), str(out_mp4))
                    print(f"  -> [{vcfg['slug']} PASS] {msg}", flush=True)
                    break
                print(f"  -> [{vcfg['slug']} RETRY] {msg}", flush=True)
            if not out_mp4.exists():
                raise RuntimeError(f"Failed clip {vcfg['slug']}/{c['id']}")

        assemble_video_with_bgm(vcfg, asr)


def main():
    daemon_dir = BASE_DIR / "_unified_flow_daemon_lite"
    if daemon_dir.exists():
        shutil.rmtree(daemon_dir, ignore_errors=True)
    daemon_dir.mkdir(parents=True, exist_ok=True)
    d_js = daemon_dir / "_daemon.js"
    d_js.write_text(DAEMON_JS, encoding="utf-8")

    proc = subprocess.Popen([NODE, str(d_js), str(daemon_dir), str(DAEMON_PORT)], cwd=r"C:\AI\full studio\canvas\desktop", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    def _pump():
        for ln in proc.stdout:
            ln = ln.rstrip()
            if ln:
                print("  [NODE]", ln, flush=True)
    threading.Thread(target=_pump, daemon=True).start()

    ready = False
    for _ in range(60):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{DAEMON_PORT}/ping", timeout=1.5) as r:
                if r.status == 200:
                    ready = True
                    break
        except Exception:
            pass
    if not ready:
        proc.kill()
        raise RuntimeError("Unified Flow Daemon failed to start!")

    try:
        grp_a = [v for v in VIDEOS if v["group"] == "A"]
        grp_b = [v for v in VIDEOS if v["group"] == "B"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            fa = ex.submit(run_worker_group, "slotA", grp_a)
            time.sleep(2.5)
            fb = ex.submit(run_worker_group, "slotB", grp_b)
            fa.result()
            fb.result()
    finally:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{DAEMON_PORT}/quit", timeout=2)
        except Exception:
            pass
        proc.kill()

    print("=== ALL 4 REMAINING VIDEOS (V02..V05) COMPLETED & INSPECTED! ===", flush=True)


if __name__ == "__main__":
    main()
