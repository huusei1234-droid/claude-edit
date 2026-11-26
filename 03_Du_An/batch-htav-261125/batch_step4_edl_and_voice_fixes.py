import json, math, os, re, shutil, subprocess, sys, time, wave
import numpy as np

BATCH_DIR = r"C:\AI\full studio\output\batch-htav-261125"
SRC_DIR   = r"C:\Users\001\Downloads\HT-AV(1)"
REF_WAV   = r"C:\AI\full studio\output\ht-av-261125\audio_stems\chi_hang_ref_24k.wav"
REF_TEXT  = "Bữa sáng toàn tinh bột, làm đường huyết tăng vọt cực nhanh, rồi tụt dốc không phanh, chỉ sau hai tiếng, cơ thể bạn không cần thêm tinh bột,"
LUT_ROSY  = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\01_HTPM_Beauty_Rosy_Skin.cube"
VS_ROOT   = r"C:\AI\full studio\voice-studio"

os.environ.setdefault("TORCH_HOME", r"C:\AI\full studio_data\ai-cache\torch")
sys.path.insert(0, os.path.join(VS_ROOT, "backend"))
sys.path.insert(0, VS_ROOT)

import torch
import torch.nn.functional as F
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from services.tts_backend import get_active_tts_backend

SR = 48000
FPS = 30.0

# ==============================================================================
# 1. COMPLETE 17-EPISODE EDL & VOICE STUDIO CLONE SPECIFICATION
# Every piece is either:
#   ("real", start_s, end_s, label)
#   ("clone", bg_src_s, clone_key, [(seed, tts_text, lang), ...], clean_display_text, label)
# Note: Every "clone" piece is recorded in `clone_spans` so our renderer ALWAYS
# covers 100% of that span with a Full-Screen Playing-Card / B-Roll Stage!
# ==============================================================================
EPISODES = {
    "v01": {
        "idx": 1, "code": "HT02", "brand": "HTPM",
        "final_name": "261125 HTPM Viên đặt phụ khoa LT Plus 3 tín hiệu báo động final.mp4",
        "pieces": [
            ("real",  2.42, 23.38, "Hook_And_3_Signs"),
            ("real", 25.34, 35.48, "Dont_Wait_Herbal_Care"),
            ("clone", 36.20, "v01_c1", [
                (2026, "Viên đặt eo ti pờ lút Hằng Thu,", "vi"),
                (2027, "Viên đặt LT Plus Hằng Thu,", "vi"),
            ], "Viên đặt LT Plus Hằng Thu", "Cloned_LT_Plus_Name"),
            ("real", 38.00, 47.82, "Ingredients_Deep_Clean_pH"),
            ("real", 50.94, 57.80, "Gentle_Mucosa_Dont_Suffer"),
            ("clone", 58.20, "v01_c2", [
                (2026, "Nhắn riêng chữ eo ti pờ lút để Hằng lắng nghe và hướng dẫn kín đáo!", "vi"),
                (2027, "Nhắn riêng chữ LT Plus để Hằng lắng nghe và hướng dẫn kín đáo!", "vi"),
            ], "Nhắn riêng chữ LT PLUS để Hằng lắng nghe và hướng dẫn kín đáo!", "Cloned_CTA_LTPlus"),
        ],
    },
    "v02": {
        "idx": 2, "code": "HT10", "brand": "HTPM",
        "final_name": "261125 HTPM Ngọc Long Hoàn 3 dấu hiệu chồng cạn pin final.mp4",
        "pieces": [
            ("real", 16.22, 42.94, "Hook_And_3_Low_Battery_Signs"),
            ("real", 45.74, 64.60, "Root_Vitality_8_Herbs"),
            ("real", 66.26, 71.54, "Enduring_Form_Save_Gift"),
            ("clone", 72.00, "v02_c1", [
                (2026, "Nhắn Ngọc Long Hoàn để Hằng tư vấn bảo mật một trăm phần trăm!", "vi"),
                (2027, "Nhắn ngay Ngọc Long Hoàn để Hằng tư vấn bảo mật một trăm phần trăm!", "vi"),
            ], "Nhắn NGỌC LONG HOÀN để Hằng tư vấn bảo mật 100%!", "Cloned_CTA_NgocLongHoan"),
        ],
    },
    "v03": {
        "idx": 3, "code": "AV03", "brand": "HTPM",
        "final_name": "261125 HTPM AV Protein phục hồi cơ sau tập 17500 đồng final.mp4",
        "pieces": [
            ("real",  2.48, 13.12, "Hook_Workout_Loose_Muscle"),
            ("clone", 13.50, "v03_c1", [
                (2026, "đặc biệt là thiếu eo liu xin,", "vi"),
                (2027, "đặc biệt là thiếu L-Leucine,", "en"),
            ], "đặc biệt là thiếu L-Leucine,", "Cloned_Lack_LLeucine"),
            ("real", 15.58, 36.64, "Switch_Mechanism_And_22g_PeaRice"),
            ("clone", 37.00, "v03_c2", [
                (2026, "lại sẵn một nghìn sáu trăm ba mươi hai mi li gam eo liu xin,", "vi"),
                (2027, "lại sẵn một nghìn sáu trăm ba mươi hai mi li gam L-Leucine,", "en"),
            ], "lại sẵn 1.632mg L-Leucine,", "Cloned_1632mg_LLeucine"),
            ("real", 43.08, 46.30, "Only_17500_VND"),
            ("real", 62.64, 67.92, "CTA_Tag_Gym_Buddy"),
            ("clone", 68.10, "v03_c3", [
                (2026, "nhắn chữ Đạm mình gửi miễn phí nhé!", "vi"),
                (2027, "nhắn ngay chữ Đạm mình gửi miễn phí nhé!", "vi"),
            ], "nhắn chữ ĐẠM mình gửi miễn phí nhé!", "Cloned_CTA_Dam"),
        ],
    },
    "v04": {
        "idx": 4, "code": "AV05", "brand": "HTPM",
        "final_name": "261125 HTPM Ngũ cốc Canxi Bojomi hương Vani biếu bố mẹ final.mp4",
        "pieces": [
            ("real",  1.88, 31.42, "Hook_Dusty_Calcium_Jar_To_Bojomi_60C"),
            ("clone", 32.00, "v04_c1", [
                (2026, "là bạn đã có ngay một ly Canxi đủ đầy dưỡng chất: Canxi tảo biển đỏ A qua min ép, Vitamin Dê ba, Ca hai em ca bảy và Cô la gen!", "vi"),
                (2027, "là bạn có ngay một ly Canxi đủ đầy Canxi tảo biển đỏ Aquamin F, Vitamin D3, K2 MK7 và Collagen!", "vi"),
            ], "là bạn đã có ngay 1 ly Canxi đủ đầy dưỡng chất: Canxi tảo biển đỏ Aquamin F, Vitamin D3, K2 MK-7 và Collagen!", "Cloned_Bojomi_D3_K2_Fix"),
            ("real", 45.68, 53.36, "Best_Gift_Parents_Finish_Daily"),
        ],
    },
    "v05": {
        "idx": 5, "code": "AV08", "brand": "HTPM",
        "final_name": "261125 HTPM Collamela Collagen Tripeptide vị đào căng mướt final.mp4",
        "pieces": [
            ("real",  3.60, 10.92, "Hook_Expensive_Cream_Sponge"),
            ("real", 12.74, 16.78, "After_25_Lose_Frame_Moisture"),
            ("real", 22.38, 44.80, "Large_Collagen_Vs_Collamela_2530mg"),
            ("clone", 45.20, "v05_c1", [
                (2026, "hai mươi lăm phẩy sáu mươi tám mi li gam hát a giữ ẩm, tám mươi bảy mi li gam Vitamin Cê và ba phẩy chín mi li gam Kẽm,", "vi"),
                (2027, "hai mươi lăm phẩy sáu tám mi li gam H A giữ ẩm, tám mươi bảy mi li gam Vitamin C và ba phẩy chín mi li gam Kẽm,", "vi"),
            ], "25,68mg HA giữ ẩm, 87mg Vitamin C và 3,9mg Kẽm,", "Cloned_2568mg_HA_VitC_Zinc"),
            ("real", 60.74, 67.60, "Mix_100ml_Cool_Peach_No_Fishy"),
            ("clone", 64.50, "v05_c2", [
                (2026, "Chăm da cần đều mỗi ngày chứ đừng đợi sát Tết! Lưu lại và nhắn Cô la mê la để nhận lộ trình sáu mươi ngày nhé!", "vi"),
                (2027, "Chăm da cần đều mỗi ngày chứ đừng đợi sát Tết! Lưu lại và nhắn Collamela để nhận lộ trình sáu mươi ngày nhé!", "vi"),
            ], "Chăm da cần đều mỗi ngày chứ đừng đợi sát Tết! Lưu lại và nhắn COLLAMELA để nhận lộ trình 60 ngày nhé!", "Cloned_CTA_Collamela"),
        ],
    },
    "v06": {
        "idx": 6, "code": "AV10", "brand": "HTPM",
        "final_name": "261125 HTPM Combo 60 ngày đón Tết xinh An Vượng final.mp4",
        "pieces": [
            ("real",  2.76, 11.50, "Hook_60_Days_To_Tet_Crash_Diet"),
            ("real", 12.70, 16.68, "Dull_Skin_Stomach_Upset"),
            ("real", 20.46, 28.10, "Steady_60Day_2_Slot_Schedule"),
            ("real", 31.68, 36.80, "Morning_AV_Protein_Light_Belly"),
            ("clone", 47.20, "v06_c1", [
                (2026, "Buổi tối một ly sữa nghệ ấm Cu cu miu Phai tô êm dạ dày, kèm một gói Cô la mê la vị Đào bổ sung", "vi"),
                (2027, "Buổi tối một ly sữa nghệ ấm Curcumilk Phyto êm dạ dày, kèm một gói Collamela vị Đào bổ sung", "vi"),
            ], "Buổi tối 1 ly sữa nghệ ấm Curcumilk Phyto êm dạ dày, kèm 1 gói Collamela vị Đào bổ sung", "Cloned_Evening_Curcumilk_Collamela"),
            ("real", 55.58, 65.30, "Collagen_HA_Tag_Besties_60Days"),
            ("clone", 65.70, "v06_c2", [
                (2026, "Nhắn Tết Xinh để nhận trọn bộ ưu đãi nhé!", "vi"),
                (2027, "Nhắn ngay chữ Tết Xinh để nhận trọn bộ ưu đãi!", "vi"),
            ], "Nhắn TẾT XINH để nhận trọn bộ ưu đãi nhé!", "Cloned_CTA_TetXinh"),
        ],
    },
    "v07": {
        "idx": 7, "code": "HT03", "brand": "HTPM",
        "final_name": "261125 HTPM Dạ Dày HT Hằng Thu cà phê sáng ăn khuya final.mp4",
        "pieces": [
            ("real",  3.56, 19.30, "Hook_Empty_Coffee_9PM_Dinner"),
            ("real", 22.96, 24.76, "Gravity_Cannot_Hold"),
            ("clone", 30.00, "v07_c1", [
                (2026, "dòng a xít trào ngược lên thực quản,", "vi"),
                (2027, "khiến dòng a xít trào ngược lên thực quản,", "vi"),
            ], "dòng acid trào ngược lên thực quản,", "Cloned_Acid_Reflux_Flow"),
            ("real", 34.66, 40.06, "Heartburn_Sour_Bitter_Morning"),
            ("real", 47.84, 58.84, "Eat_Light_Before_Coffee_DaDayHT"),
            ("clone", 68.40, "v07_c2", [
                (2026, "từ chiết xuất Dạ cẩm và Nghệ giúp hỗ trợ trung hòa a xít,", "vi"),
                (2027, "chiết xuất từ Dạ cẩm và Nghệ giúp hỗ trợ trung hòa a xít,", "vi"),
            ], "từ chiết xuất Dạ cẩm và Nghệ giúp hỗ trợ trung hòa acid,", "Cloned_DaCam_Nghe_Neutralize"),
            ("real", 72.66, 76.62, "Soothe_Burning_Coat_Mucosa"),
            ("real", 82.45, 86.92, "Share_Morning_Coffee_Skipper"),
            ("clone", 87.40, "v07_c3", [
                (2026, "Nhắn Dạ Dày để Hằng gửi mẹo ăn uống êm bụng!", "vi"),
                (2027, "Nhắn chữ Dạ Dày để Hằng gửi mẹo ăn uống êm bụng nhé!", "vi"),
            ], "Nhắn DẠ DÀY để Hằng gửi mẹo ăn uống êm bụng!", "Cloned_CTA_DaDay"),
        ],
    },
    "v08": {
        "idx": 8, "code": "HT05", "brand": "HTPM",
        "final_name": "261125 HTPM Legend White Skin chống oxy hóa sáng da đón Tết final.mp4",
        "pieces": [
            ("real",  4.22,  8.18, "Hook_Half_Apple_10Min_Brown"),
            ("real", 12.94, 32.88, "Skin_After_25_Oxidation_UV_BlueLight"),
            ("real", 39.50, 63.50, "Stubborn_DarkSpots_InsideOut_WhiteSkin"),
            ("real", 70.72, 75.02, "Dont_Leave_KPI_To_Photo_App"),
            ("clone", 75.40, "v08_c1", [
                (2026, "Nhắn Oai Sờ Kin để Hằng gửi lịch chăm da sáng đều đón Tết!", "vi"),
                (2027, "Nhắn White Skin để Hằng gửi lịch chăm da sáng đều đón Tết!", "vi"),
            ], "Nhắn WHITESKIN để Hằng gửi lịch chăm da sáng đều đón Tết!", "Cloned_CTA_WhiteSkin"),
        ],
    },
    "v09": {
        "idx": 9, "code": "HT06", "brand": "HTPM",
        "final_name": "261125 HTPM Viên dưỡng Romance Love cấp ẩm giữ lửa hạnh phúc final.mp4",
        "pieces": [
            ("real",  5.72, 33.96, "Hook_Two_Rose_Petals_Dryness_Distance"),
            ("clone", 34.30, "v09_c1", [
                (2026, "Viên dưỡng Rô man Lớp Hằng Thu,", "vi"),
                (2027, "Viên dưỡng Romance Love Hằng Thu,", "vi"),
            ], "Viên dưỡng Romance Love Hằng Thu,", "Cloned_Romance_Love_Name"),
            ("real", 36.32, 55.60, "HA_B5_Niacinamide_Collagen_SelfLove"),
            ("clone", 56.00, "v09_c2", [
                (2026, "Nhắn riêng Rô man Lớp để Hằng tư vấn thật bảo mật nhé!", "vi"),
                (2027, "Nhắn riêng Romance Love để Hằng tư vấn thật bảo mật nhé!", "vi"),
            ], "Nhắn riêng ROMANCE LOVE để Hằng tư vấn thật bảo mật nhé!", "Cloned_CTA_RomanceLove"),
        ],
    },
    "v10": {
        "idx": 10, "code": "AV02", "brand": "HTPM",
        "final_name": "261125 HTPM Mẹo pha chuẩn AV Protein nước 20 đến 40 độ final.mp4",
        "pieces": [
            ("real",  5.30, 20.95, "Hook_Stop_100C_Boiling_Water_Inulin_50mg"),
            ("clone", 21.40, "v10_c1", [
                (2026, "lợi khuẩn Bê bờ rê vê Bê ba!", "vi"),
                (2027, "lợi khuẩn B breve B ba!", "vi"),
            ], "lợi khuẩn B. breve B-3!", "Cloned_B_Breve_B3"),
            ("real", 24.50, 25.82, "Boiling_100C_Water"),
            ("real", 27.68, 31.66, "Clumps_Protein_Destroys_Probiotics"),
            ("clone", 12.00, "v10_c2", [
                (2026, "Cách pha chuẩn khoa học cực dễ: cứ dùng ba trăm mi li lít nước lọc mát hoặc ấm nhẹ từ hai mươi đến bốn mươi độ Cê, khuấy hoặc lắc mười lăm giây, bột tan mịn, thơm dịu, êm bụng cả với người hay đầy hơi vì sữa bò!", "vi"),
            ], "Cách pha chuẩn khoa học cực dễ: cứ dùng 300ml nước lọc mát hoặc ấm nhẹ từ 20 đến 40 độ C, khuấy hoặc lắc 15 giây — bột tan mịn, thơm dịu, êm bụng cả với người hay đầy hơi vì sữa bò!", "Cloned_HowToMix_20_40C"),
            ("clone", 29.00, "v10_c3", [
                (2026, "Lưu lại ngay để khỏi pha phí nhé! Ai đang uống A Vê Pờ rô tê in mà chưa biết mẹo này, gửi liền cho họ!", "vi"),
            ], "Lưu lại ngay để khỏi pha phí nhé! Ai đang uống AV Protein mà chưa biết mẹo này, gửi liền cho họ!", "Cloned_CTA_AV02"),
        ],
    },
    "v12": {
        "idx": 12, "code": "HT01", "brand": "HTPM",
        "final_name": "261125 HTPM Dung dịch vệ sinh Romance VIP làm sạch chuẩn pH final.mp4",
        "pieces": [
            ("real",  2.66,  9.22, "Hook_Stop_Deep_Shower_Spray"),
            ("real", 10.84, 49.80, "Protect_Probiotic_Barrier_RomanceVIP_24h"),
            ("clone", 50.00, "v12_c1", [
                (2026, "Nhắn Rô man Víp để Hằng tư vấn chăm sóc đúng cách!", "vi"),
                (2027, "Nhắn Romance VIP để Hằng tư vấn chăm sóc đúng cách nhé!", "vi"),
            ], "Nhắn ROMANCE VIP để Hằng tư vấn chăm sóc đúng cách!", "Cloned_CTA_RomanceVIP"),
        ],
    },
    "v13": {
        "idx": 13, "code": "HT04", "brand": "HTPM",
        "final_name": "261125 HTPM Viên uống Điều Kinh Bổ Trứng Hằng Thu chu kỳ êm final.mp4",
        "pieces": [
            ("real",  2.92, 26.82, "Hook_Irregular_Cycle_Fire_Alarm"),
            ("real", 27.60, 34.62, "Fertility_Journey_Nourish_Blood_Qi"),
            ("real", 37.66, 49.20, "DieuKinh_4_Herbs_Nourish_Ovaries"),
            ("real", 50.50, 57.18, "Lighter_Every_Month_Save_Share"),
            ("clone", 60.90, "v13_c1", [
                (2026, "Nhắn Điều Kinh để Hằng tư vấn theo đúng thể trạng!", "vi"),
                (2027, "Nhắn chữ Điều Kinh để Hằng tư vấn theo đúng thể trạng nhé!", "vi"),
            ], "Nhắn ĐIỀU KINH để Hằng tư vấn theo đúng thể trạng!", "Cloned_CTA_DieuKinh"),
        ],
    },
    "v15": {
        "idx": 15, "code": "HT07", "brand": "HTPM",
        "final_name": "261125 HTPM Viên đặt phụ khoa Hộp Xanh chăm từ gốc sau sinh final.mp4",
        "pieces": [
            ("real",  1.32, 19.72, "Hook_Stop_Perfume_Scented_Wipes_15Min"),
            ("real", 31.94, 41.22, "Postpartum_Elasticity_Root_Care_With"),
            ("clone", 41.30, "v15_c1", [
                (2026, "Viên đặt Phụ Khoa Hộp Xanh Hằng Thu,", "vi"),
                (2027, "Viên đặt Phụ Khoa Hộp Xanh nhà Hằng Thu,", "vi"),
            ], "Viên đặt Phụ Khoa Hộp Xanh Hằng Thu,", "Cloned_HopXanh_Exact_Name"),
            ("real", 43.44, 53.46, "Chamomile_Licorice_Lactic_Firmness"),
            ("real", 55.32, 61.34, "Pelvic_Floor_Kegel_Save_For_Moms"),
            ("clone", 58.00, "v15_c2", [
                (2026, "Nhắn Hộp Xanh để Hằng gửi kèm hướng dẫn bài tập săn chắc tại nhà!", "vi"),
            ], "Nhắn HỘP XANH để Hằng gửi kèm hướng dẫn bài tập săn chắc tại nhà!", "Cloned_CTA_HopXanh"),
        ],
    },
    "v16": {
        "idx": 16, "code": "AV04", "brand": "HTPM",
        "final_name": "261125 HTPM Canxi Bojomi kiềng ba chân Aquamin F D3 K2 MK7 final.mp4",
        "pieces": [
            ("real",  2.22, 35.18, "Hook_Calcium_3_Legged_Stool_Read_Label"),
            ("clone", 35.40, "v16_c1", [
                (2026, "bốn trăm mười bảy phẩy sáu mi li gam Canxi tảo biển đỏ A qua min ép,", "vi"),
                (2027, "bốn trăm mười bảy phẩy sáu mi li gam Canxi tảo biển đỏ Aquamin F,", "vi"),
            ], "417,6mg Canxi tảo biển đỏ Aquamin F,", "Cloned_417_6mg_AquaminF"),
            ("real", 40.28, 61.04, "779IU_D3_169mcg_K2_201mg_Collagen"),
            ("clone", 57.50, "v16_c2", [
                (2026, "Nhắn Bô giô mi để xem bảng đọc nhãn chi tiết nhé!", "vi"),
                (2027, "Nhắn Bojomi để xem bảng đọc nhãn chi tiết!", "vi"),
            ], "Nhắn BOJOMI để xem bảng đọc nhãn chi tiết nhé!", "Cloned_CTA_Bojomi"),
        ],
    },
    "v17": {
        "idx": 17, "code": "AV09", "brand": "HTPM",
        "final_name": "261125 HTPM Combo Xương Cơ AV Protein và Bojomi cho bố mẹ final.mp4",
        "pieces": [
            ("real",  4.58, 15.48, "Hook_Steel_Frame_Brick_Wall_Bone"),
            ("real", 18.62, 30.92, "Muscle_Supports_Bone_Seniors_Lack_Protein"),
            ("real", 33.44, 36.42, "Weak_Muscle_Tires_Fast"),
            ("real", 41.80, 48.82, "Morning_1_Cup_AV_Protein"),
            ("clone", 49.20, "v17_c1", [
                (2026, "và eo liu xin giữ cơ. Chiều một ly Bô giô mi hương Va ni bổ sung Canxi tảo biển đỏ A qua min ép, Dê ba, Ca hai em ca bảy và Cô la gen dưỡng xương!", "vi"),
            ], "và L-Leucine giữ cơ — Chiều 1 ly Bojomi hương Vani bổ sung Canxi tảo biển đỏ Aquamin F, D3, K2 MK-7 và Collagen dưỡng xương!", "Cloned_Leucine_And_Afternoon_Bojomi"),
            ("real", 61.22, 66.00, "Share_For_Parents_Health_Gift"),
            ("clone", 66.20, "v17_c2", [
                (2026, "Nhắn Xương Cơ mình gửi chi tiết nhé!", "vi"),
            ], "Nhắn XƯƠNG CƠ mình gửi chi tiết nhé!", "Cloned_CTA_XuongCo"),
        ],
    },
    "v18": {
        "idx": 18, "code": "AV07", "brand": "HTPM",
        "final_name": "261125 HTPM Sữa nghệ Curcumilk Phyto bữa phụ 3 giờ chiều êm bụng final.mp4",
        # Outdoor garden clip where wireless mic disconnected -> clean Voice Studio cloned voice + Full-Screen Multi-Card Stages + brief calm smiling outdoor establishers!
        "pieces": [
            ("clone", 13.50, "v18_c1", [
                (2026, "Ba giờ chiều đói cồn cào mà bạn lại đặt ly trà sữa hay cà phê đá? Dừng lại ngay!", "vi"),
            ], "3 giờ chiều đói cồn cào mà bạn lại order ly trà sữa hay cà phê đá? Dừng lại ngay!", "Cloned_Hook_3PM_MilkTea"),
            ("clone", 20.00, "v18_c2", [
                (2026, "Bụng đang rỗng, áp lực công việc lại làm dịch vị tiết mạnh, uống thêm đá lạnh, cà phê và đường ngọt vào chỉ khiến dạ dày càng cồn cào, đầy hơi, đến tối lại chẳng buồn ăn cơm!", "vi"),
            ], "Bụng đang rỗng, áp lực công việc lại làm dịch vị tiết mạnh — uống thêm đá lạnh, cà phê và đường ngọt vào chỉ khiến dạ dày càng cồn cào, đầy hơi, đến tối lại chẳng buồn ăn cơm!", "Cloned_Empty_Stomach_Cold_Sugar"),
            ("clone", 27.50, "v18_c3", [
                (2026, "Trong túi xách mình lúc nào cũng thủ sẵn một gói sữa nghệ Cu cu miu Phai tô nhỏ xíu này! Ra quầy nước lấy một trăm năm mươi mi li lít nước ấm bốn mươi đến năm mươi độ, khuấy hai mươi giây là có bữa phụ sữa dừa nghệ Va ni ấm dịu, no nhẹ mà êm bụng cả chiều!", "vi"),
            ], "Trong túi xách mình lúc nào cũng thủ sẵn 1 gói sữa nghệ Curcumilk Phyto nhỏ xíu này! Ra quầy nước lấy 150ml nước ấm 40 đến 50 độ, khuấy 20 giây là có bữa phụ sữa dừa nghệ Vani ấm dịu, no nhẹ mà êm bụng cả chiều!", "Cloned_Curcumilk_150ml_Warm"),
            ("clone", 39.00, "v18_c4", [
                (2026, "Gửi ngay cho đồng nghiệp ngồi cạnh chuyên rủ đặt trà sữa lúc ba giờ chiều nha!", "vi"),
            ], "Gửi ngay cho đồng nghiệp ngồi cạnh chuyên rủ đặt trà sữa lúc 3 giờ chiều nha!", "Cloned_CTA_3PM_Colleague"),
        ],
    },
    "v19": {
        "idx": 19, "code": "HT08", "brand": "HTPM",
        "final_name": "261125 HTPM Gel Phụ Khang Hằng Thu thoáng sạch dân văn phòng 8 tiếng final.mp4",
        "pieces": [
            ("clone", 1.80, "v19_c1", [
                (2026, "Ngồi ghế văn phòng tám tiếng cộng mặc quần ôm sát, bạn đang vô tình tạo ra hiệu ứng nhà kính đấy!", "vi"),
            ], "Ngồi ghế văn phòng 8 tiếng cộng mặc quần ôm sát — bạn đang vô tình tạo ra hiệu ứng nhà kính đấy!", "Cloned_Hook_8H_Office_Greenhouse"),
            ("clone", 18.00, "v19_c2", [
                (2026, "Ít vận động, quần jean dày hoặc đồ lót sợi tổng hợp làm độ ẩm và nhiệt độ tăng cao liên tục, đây là môi trường lý tưởng để mùi khó chịu và tình trạng bí rít xuất hiện mỗi cuối ngày!", "vi"),
            ], "Ít vận động, quần jean dày hoặc đồ lót sợi tổng hợp làm độ ẩm và nhiệt độ tăng cao liên tục — đây là môi trường lý tưởng để mùi khó chịu và tình trạng bí rít xuất hiện mỗi cuối ngày!", "Cloned_Humidity_Heat_Trap"),
            ("clone", 30.00, "v19_c3", [
                (2026, "Ngoài việc đổi đồ lót cốt tông thoáng và đứng dậy đi lại mỗi giờ, chị em đừng quên làm sạch êm dịu cuối ngày bằng Gel Phụ Khang Hằng Thu, chiết xuất Kim ngân hoa, Trầu không, Khổ sâm và Trinh nữ hoàng cung giúp làm sạch nhẹ, khử mùi, giữ ẩm và thơm mát dễ chịu!", "vi"),
            ], "Ngoài việc đổi đồ lót cotton thoáng và đứng dậy đi lại mỗi giờ, chị em đừng quên làm sạch êm dịu cuối ngày bằng Gel Phụ Khang Hằng Thu — chiết xuất Kim ngân hoa, Trầu không, Khổ sâm và Trinh nữ hoàng cung giúp làm sạch nhẹ, khử mùi, giữ ẩm và thơm mát dễ chịu!", "Cloned_GelPhuKhang_4_Herbs"),
            ("clone", 41.00, "v19_c4", [
                (2026, "Gửi ngay cho cô bạn đồng nghiệp ngồi dán mắt máy tính cả ngày nhé! Nhắn Gel Phụ Khang để Hằng tư vấn!", "vi"),
            ], "Gửi ngay cho cô bạn đồng nghiệp ngồi dán mắt máy tính cả ngày nhé! Nhắn GEL PHỤ KHANG để Hằng tư vấn!", "Cloned_CTA_GelPhuKhang"),
        ],
    },
}

# ==============================================================================
# VIETNAMESE TRANSCRIPT SPELL-CHECKER FOR CLEAN SUBTITLES
# ==============================================================================
PHRASE_FIXES = [
    (r"\btin nhắn bão đồng\b", "tin nhắn báo động"),
    (r"\bbao giờ hiểu\b", "3 dấu hiệu"),
    (r"\bba dạo hiệu\b", "3 dấu hiệu"),
    (r"\bvang xanh\b", "vàng xanh"),
    (r"\blờn cờn\b", "lợn cợn"),
    (r"\bnguôi họp\b", "ngồi họp"),
    (r"\bđựng gần\b", "đứng gần"),
    (r"\bcùng thấp thỏm\b", "cũng thấp thỏm"),
    (r"\bngựa rạn\b", "ngứa rát"),
    (r"\be ngài\b", "e ngại"),
    (r"\btừ chiều\b", "tự chịu"),
    (r"\btải nghi tải lại\b", "tái đi tái lại"),
    (r"\bthấm khám\b", "thăm khám"),
    (r"\bhoang bã\b", "Hoàng bá"),
    (r"\bkim ngân hoa\b", "Kim ngân hoa"),
    (r"\btrầu không\b", "Trầu không"),
    (r"\bCăn bằng nổi hạt\b", "cân bằng độ pH"),
    (r"\bcân bằng mế hạt\b", "cân bằng độ pH"),
    (r"\bđồ bế hạt\b", "độ pH"),
    (r"\bêm dìu\b", "êm dịu"),
    (r"\bdìu nhè\b", "dịu nhẹ"),
    (r"\bchịu đừng\b", "chịu đựng"),
    (r"\bhơi hợt\b", "hời hợt"),
    (r"\bcàn viên\b", "cạn pin"),
    (r"\bcàn pin\b", "cạn pin"),
    (r"\bta làm về\b", "tan làm về"),
    (r"\bcầu gắt\b", "cáu gắt"),
    (r"\bnẻ tránh truyền\b", "né tránh chuyện"),
    (r"\bsờ từ ti vậy vợ\b", "sợ tự ti với vợ"),
    (r"\bhay giàu lắm\b", "hay giấu lắm"),
    (r"\bdần dội\b", "giận dỗi"),
    (r"\bmô đồ cấp tóc\b", "mua đồ cấp tốc"),
    (r"\bhài sức khỏe\b", "hại sức khỏe"),
    (r"\bNgười vừa tâm lý\b", "Người vợ tâm lý"),
    (r"\btừ góc\b", "từ gốc"),
    (r"\btư gốc\b", "từ gốc"),
    (r"\bhồi tù tạm thảo dược quỷ\b", "hội tụ 8 thảo dược quý"),
    (r"\bĐông Trung Hà Thảo\b", "Đông trùng hạ thảo"),
    (r"\bNhung Hương\b", "Nhung hươu"),
    (r"\bBạ Bình\b", "Bá bệnh"),
    (r"\bXâm Câu\b", "Sâm cau"),
    (r"\bBộ Thần\b", "bổ thận"),
    (r"\bphong đồ\b", "phong độ"),
    (r"\bánh xã\b", "anh xã"),
    (r"\bthiểu đàm\b", "thiếu đạm"),
    (r"\bđược viễn như\b", "được ví như"),
    (r"\blà nhuốn\b", "lại nhũn"),
    (r"\bđàm đầu Hạ Lan\b", "đạm đậu Hà Lan"),
    (r"\bđầy bùng\b", "đầy bụng"),
    (r"\bTạc ngay đứa bàn\b", "Tag ngay đứa bạn"),
    (r"\bCùng phong tập\b", "cùng phòng tập"),
    (r"\bCân bản tính lương đàm theo cân năng\b", "Cần bảng tính lượng đạm theo cân nặng"),
    (r"\blò canxi bàn mua tặng bộ mè\b", "lọ Canxi bạn mua tặng bố mẹ"),
    (r"\bphủ vùi trên kề\b", "phủ bụi trên kệ"),
    (r"\bkhó muốt\b", "khó nuốt"),
    (r"\bnóng bùng, nàng tiêu\b", "nóng bụng, nặng tiêu"),
    (r"\bnõng bùng, nàng tiêu\b", "nóng bụng, nặng tiêu"),
    (r"\bsơ dân rồi cắt luôn vào gốc tủ\b", "sợ dần rồi cất luôn vào góc tủ"),
    (r"\bBozomi\b", "Bojomi"),
    (r"\bBô giô mi\b", "Bojomi"),
    (r"\bđược ấm khoảng 60 độ\b", "nước ấm khoảng 60 độ"),
    (r"\bbẹo ngày\b", "béo ngậy"),
    (r"\bquỷ dã nhất biểu bộ mẹ\b", "quý giá nhất biếu bố mẹ"),
    (r"\bquý giá nhất biểu bồ mẹ\b", "quý giá nhất biếu bố mẹ"),
    (r"\bcuồng hiệt mùi\b", "uống hết mỗi ngày"),
    (r"\bcuồng hệt mỗi ngày\b", "uống hết mỗi ngày"),
    (r"\bkèm căng mướt\b", "kém căng mướt"),
    (r"\bmiệng bọt biệt\b", "miếng bọt biển"),
    (r"\blận đồ ẩm\b", "lẫn độ ẩm"),
    (r"\bphân tử thương quá lớn\b", "phân tử thường quá lớn"),
    (r"\bColamella gõi tròn bồ tứ\b", "Collamela gói trọn bộ tứ"),
    (r"\b2 gõi nhỏ Vì đào\b", "2 gói nhỏ vị Đào"),
    (r"\btrimeptide\b", "Tripeptide"),
    (r"\bkhông hề thanh\b", "không hề tanh"),
    (r"\b2 tầm Tết\b", "28 Tết"),
    (r"\bcuồng cuồng nhìn ăn cắp tóc\b", "cuống cuồng nhịn ăn cấp tốc"),
    (r"\bÉp cân sản Tết\b", "Ép cân sát Tết"),
    (r"\bhốc hạc\b", "hốc hác"),
    (r"\bGiá sàm xỉn, giá dây là biểu tình\b", "da sạm xỉn, dạ dày lại biểu tình"),
    (r"\btiệc tung\b", "tiệc tùng"),
    (r"\brằng rửa thật sự\b", "rạng rỡ thật sự"),
    (r"\bnhịp chấm đều\b", "nhịp chăm đều"),
    (r"\bĐàm, gòn rã, nhè bùng\b", "đủ đạm, gọn dáng, nhẹ bụng"),
    (r"\bhạt A dưỡng ra các mướt\b", "HA dưỡng da căng mướt"),
    (r"\bhạt a giữ ẩm\b", "HA giữ ẩm"),
    (r"\btặng ngay những người bản thân\b", "Tag ngay hội bạn thân"),
    (r"\bđón đến sinh nhé\b", "đón Tết xinh nhé"),
    (r"\blê cà phê bùng rống\b", "ly cà phê bụng rỗng"),
    (r"\bmới ăn bu\b", "mới ăn bù"),
    (r"\bnhìn ra dây của bàn\b", "nhìn dạ dày của bạn"),
    (r"\bbùng trống\b", "bụng trống"),
    (r"\bdịch vì bao mon thẳng lập điếp mạc\b", "dịch vị bào mòn thẳng lớp niêm mạc"),
    (r"\băn muồn\b", "ăn muộn"),
    (r"\bgáy nọng rãi ngực\b", "gây nóng rát ngực"),
    (r"\bỞ chua, sáng dày, đặng miền và vượn cổ hồng\b", "ợ chua, sáng dậy đắng miệng và vướng cổ họng"),
    (r"\bthanh màn tĩnh\b", "thành mạn tính"),
    (r"\bTập ngày ăn sáng nhè\b", "Tập ngay ăn sáng nhẹ"),
    (r"\bĂn tội trước 3 tiếng\b", "ăn tối trước 3 tiếng"),
    (r"\bgiả dày hạt tê hàng thu\b", "Dạ Dày HT Hằng Thu"),
    (r"\blàm dìu cân nọng rát và bao phủ lập niêm mạc\b", "làm dịu cơn nóng rát và bao phủ lớp niêm mạc"),
    (r"\bcà phê sản thay cơm trong nhà bằng nhá\b", "cà phê sáng thay cơm trong nhà bạn nha"),
    (r"\bquả tạo\b", "quả táo"),
    (r"\bthấm sảm lại\b", "thâm sạm lại"),
    (r"\bGia bàn\b", "Da bạn"),
    (r"\breset Ý hệt\b", "rỉ sét y hệt"),
    (r"\bTiêu vê\b", "Tia UV"),
    (r"\bthức khuê\b", "thức khuya"),
    (r"\bvô sổ\b", "vô số"),
    (r"\btận công\b", "tấn công"),
    (r"\bbỏ mặt\b", "bỏ mặc"),
    (r"\bvề sàm cử ly lờm mãi\b", "vết sạm cứ lỳ lợm mãi"),
    (r"\bchóng nặng ký\b", "chống nắng kỹ"),
    (r"\bwhite skin Hằng thu\b", "White Skin Hằng Thu"),
    (r"\blàm mèo về thâm\b", "làm mờ vết thâm"),
    (r"\bmìn màng\b", "mịn màng"),
    (r"\bhệ KPI sản mình\b", "hết KPI sáng mịn"),
    (r"\bcảnh hoa\b", "cánh hoa"),
    (r"\bgiọng cảnh hoa\b", "giống cánh hoa"),
    (r"\bnồi tiệt\b", "nội tiết"),
    (r"\bđồ ẩm\b", "độ ẩm"),
    (r"\bkhô căng rạch, nhè\b", "khô căng, rát nhẹ"),
    (r"\bngài gân gũi về bản đời\b", "ngại gần gũi với bạn đời"),
    (r"\bLâu dân\b", "Lâu dần"),
    (r"\bnăng niu\b", "nâng niu"),
    (r"\bmềm mìn\b", "mềm mịn"),
    (r"\bgiữ tròn\b", "giữ trọn"),
    (r"\btừ khác ở lại\b", "tự khắc ở lại"),
    (r"\bDừng tay lái ngay nếu bà\b", "Dừng tay lại ngay nếu bạn"),
    (r"\bbột đàm\b", "bột đạm"),
    (r"\b100 đồ\b", "100 độ"),
    (r"\bmỗi khẩu phân AV protein\b", "mỗi khẩu phần AV Protein"),
    (r"\bđàm thực vật\b", "đạm thực vật"),
    (r"\bchất sơ inulin\b", "chất xơ Inulin"),
    (r"\blời khuẩn\b", "lợi khuẩn"),
    (r"\blợi quẩn\b", "lợi khuẩn"),
    (r"\bđàm võ cục\b", "đạm vón cục"),
    (r"\bđàm võn cục\b", "đạm vón cục"),
    (r"\bquý giã\b", "quý giá"),
    (r"\bThụt rửa sau\b", "thụt rửa sâu"),
    (r"\bmỡi sạch\b", "mới sạch"),
    (r"\bsà phong\b", "xà phòng"),
    (r"\bbản năng cuốn trôi\b", "bạn đang cuốn trôi"),
    (r"\ban rào\b", "hàng rào"),
    (r"\bMắt lạ chảnh\b", "Mất lá chắn"),
    (r"\bkhổ rạch\b", "khô rát"),
    (r"\bmỗi lần nhỏ dung dịch khẳng khuẩn Roman Vip\b", "một ấn nhỏ Dung dịch kháng khuẩn Romance VIP"),
    (r"\bchiến xuất hoa hồng Bulgari\b", "chiết xuất hoa hồng Bulgaria"),
    (r"\blô hổi\b", "lô hội"),
    (r"\bbàn thân của bạn Việt nhé\b", "bạn thân của bạn biết nhé"),
    (r"\bđau quần bùng mà bản vận cử viên cũng giảm đau cho quá\b", "đau quặn bụng mà bạn vẫn cứ uống viên giảm đau cho qua"),
    (r"\bCũng giảm đau\b", "Uống giảm đau"),
    (r"\bbản đưa lây lắt chuông bão chảy\b", "bạn đưa tay tắt chuông báo cháy"),
    (r"\bgốc rể\b", "gốc rễ"),
    (r"\bkhỉ huyệt\b", "khí huyết"),
    (r"\btrao đảo\b", "chao đảo"),
    (r"\bTrong kỳ\b", "Chu kỳ"),
    (r"\bnhanh xàm\b", "nhanh sạm"),
    (r"\bbùng trứng\b", "buồng trứng"),
    (r"\bbuôn trứng\b", "buồng trứng"),
    (r"\bbôi bổ Tư khí huyết\b", "bồi bổ từ khí huyết"),
    (r"\bViết uống điều kinh bổ trứng hàng thu\b", "Viên uống Điều Kinh Bổ Trứng Hằng Thu"),
    (r"\bđương quy, hương phù, hồng hoa, xài hồ\b", "Đương quy, Hương phụ, Hồng hoa, Sài hồ"),
    (r"\bchung kỳ\b", "chu kỳ"),
    (r"\bnhè tanh\b", "nhẹ tênh"),
    (r"\bngại cảm\b", "nhạy cảm"),
    (r"\bhương liều\b", "hương liệu"),
    (r"\bạt mùi trong đụng 15 phút\b", "át mùi trong đúng 15 phút"),
    (r"\bphạ vỡ\b", "phá vỡ"),
    (r"\bvùng da bị bách\b", "vùng da bí bách"),
    (r"\bđồ đàn hồi\b", "độ đàn hồi"),
    (r"\bche tàn\b", "che tạm"),
    (r"\bche dấu\b", "che giấu"),
    (r"\bChiến xuất từ cúc lá mã\b", "chiết xuất từ Cúc La Mã"),
    (r"\bacid latic\b", "Acid Lactic"),
    (r"\bdịch tô nồng\b", "dịch tồn đọng"),
    (r"\bđồ săn chắc\b", "độ săn chắc"),
    (r"\bCơ sát vùng trầu\b", "cơ sàn chậu"),
    (r"\bmẹ điểm sau xin\b", "mẹ bỉm sau sinh"),
    (r"\bvào bùng\b", "vào bụng"),
    (r"\bchày thẳng\b", "chạy thẳng"),
    (r"\bcân tròn bồ kiềng ba chân\b", "cần trọn bộ kiềng ba chân"),
    (r"\btai sẽ dẫn đường\b", "tài xế dẫn đường"),
    (r"\bThiếu bồ dẫn đường này cũng nhiều\b", "Thiếu bộ dẫn đường này uống nhiều"),
    (r"\bđồ dẻo dài\b", "độ dẻo dai"),
    (r"\bAquamin FD3K2\b", "Aquamin F - D3 - K2"),
    (r"\bdừng khung sắt không xây đường gạch\b", "dựng khung sắt, không xây tường gạch"),
    (r"\bcó thể chúng ta\b", "Cơ thể chúng ta"),
    (r"\bkẹo khung xương\b", "kéo khung xương"),
    (r"\bcho bộ mẹ\b", "cho bố mẹ"),
    (r"\bhụt đàm\b", "hụt đạm"),
    (r"\bthiểu cơ là đi đựng\b", "thiếu cơ là đi đứng"),
    (r"\btrong cả nhà cực gòn\b", "chăm cả nhà cực gọn"),
    (r"\bA qua min ép\b", "Aquamin F"),
    (r"\bVitamin Dê ba\b", "Vitamin D3"),
    (r"\bDê ba\b", "D3"),
    (r"\bCa hai em ca bảy\b", "K2 MK-7"),
    (r"\bCô la gen\b", "Collagen"),
    (r"\bCô la mê la\b", "Collamela"),
    (r"\bCu cu miu Phai tô\b", "Curcumilk Phyto"),
    (r"\beo liu xin\b", "L-Leucine"),
    (r"\beo ti pờ lút\b", "LT PLUS"),
    (r"\bOai Sờ Kin\b", "WHITESKIN"),
    (r"\bRô man Lớp\b", "Romance Love"),
    (r"\bRô man Víp\b", "Romance VIP"),
    (r"\bA Vê Pờ rô tê in\b", "AV Protein"),
    (r"\bBê bờ rê vê Bê ba\b", "B. breve B-3"),
    (r"\bcốt tông\b", "cotton"),
]

def polish_vi_text(txt):
    out = txt
    for pat, rep in PHRASE_FIXES:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    return out

def read_f32_48k(path, ss=None, dur=None, af=None):
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.6f}"]
    cmd += ["-i", path]
    if dur is not None:
        cmd += ["-t", f"{dur:.6f}"]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def apply_micro_fade(arr, fi_s=0.020, fo_s=0.026):
    out = arr.copy()
    fi = min(len(out) // 4, int(round(fi_s * SR)))
    fo = min(len(out) // 4, int(round(fo_s * SR)))
    if fi > 2:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 2:
        out[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return out

def rms_active(arr):
    mono = np.mean(arr, axis=1)
    hop = 960
    nh = len(mono) // hop
    if nh < 1:
        return float(np.sqrt(np.mean(mono**2)) + 1e-5)
    r = np.sqrt(np.mean(mono[:nh*hop].reshape((nh, hop))**2, axis=1))
    act = r[r > 0.016]
    return float(np.median(act)) if len(act) else float(np.mean(r) + 1e-5)

def main():
    t_start = time.time()
    print("[1/4] Loading OmniVoice CUDA + GPU Whisper FP16 + GPU RVM FP16...", flush=True)
    backend = get_active_tts_backend()

    asr_id = "openai/whisper-large-v3-turbo"
    asr_model = AutoModelForSpeechSeq2Seq.from_pretrained(asr_id, torch_dtype=torch.float16, low_cpu_mem_usage=True).to("cuda")
    asr_proc  = AutoProcessor.from_pretrained(asr_id)
    asr_pipe  = pipeline(
        "automatic-speech-recognition",
        model=asr_model,
        tokenizer=asr_proc.tokenizer,
        feature_extractor=asr_proc.feature_extractor,
        torch_dtype=torch.float16,
        device="cuda:0",
    )

    rvm_model = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3", trust_repo=True).cuda().eval().half()
    print(f"[MODELS READY] Loaded all 3 CUDA engines in {time.time() - t_start:.1f}s!", flush=True)

    clone_cache_dir = os.path.join(BATCH_DIR, "voice_clones_48k")
    os.makedirs(clone_cache_dir, exist_ok=True)

    def get_or_synth_clone(clone_key, candidates):
        out_wav = os.path.join(clone_cache_dir, f"{clone_key}.wav")
        if os.path.exists(out_wav) and os.path.getsize(out_wav) > 8000:
            return out_wav
        best_tmp = None
        for seed_i, ctext, lang in candidates:
            torch.manual_seed(seed_i)
            wt = backend.generate(
                text=ctext,
                ref_audio=REF_WAV,
                ref_text=REF_TEXT,
                language=lang,
                num_step=32,
                guidance_scale=2.2,
                speed=1.03,
            )
            sr_tts = int(getattr(backend, "sample_rate", 24000))
            arr = wt.detach().to("cpu").float().numpy().squeeze().astype(np.float32) if hasattr(wt, "detach") else np.asarray(wt, dtype=np.float32).squeeze()
            if arr.ndim > 1:
                arr = arr.mean(axis=int(np.argmin(arr.shape)))
            pk = float(np.max(np.abs(arr))) if len(arr) else 0.0
            if pk > 1e-4:
                arr = arr * (0.90 / pk)
            idx_act = np.where(np.abs(arr) > 0.014)[0]
            if len(idx_act) > 10:
                arr = arr[max(0, int(idx_act[0]) - int(0.025 * sr_tts)) : min(len(arr), int(idx_act[-1]) + int(0.045 * sr_tts))]
            tmp24 = out_wav + f".s{seed_i}.wav"
            pcm16 = (np.clip(arr, -1.0, 1.0) * 32767.0).astype(np.int16)
            with wave.open(tmp24, "wb") as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr_tts); wf.writeframes(pcm16.tobytes())
            best_tmp = tmp24
            break  # Seed 2026 phonetic Vietnamese on OmniVoice is ultra-stable & crisp!

        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", best_tmp,
            "-af", "highpass=f=85,equalizer=f=320:t=q:w=1.1:g=1.4,equalizer=f=3400:t=q:w=1.2:g=-1.2,lowpass=f=12500",
            "-ac", "2", "-ar", str(SR), out_wav
        ], check=True)
        os.remove(best_tmp)
        print(f"  [CLONED] {clone_key} -> {out_wav}", flush=True)
        return out_wav

    summary_report = []

    for vid_key, ep in EPISODES.items():
        t_ep = time.time()
        idx = ep["idx"]
        v_dir = os.path.join(BATCH_DIR, vid_key)
        os.makedirs(v_dir, exist_ok=True)
        src_mp4 = os.path.join(SRC_DIR, f"HT-AV(1)-{idx}.mp4")
        clean_mic = os.path.join(v_dir, "clean_mic_48k.wav")

        ed_graded = os.path.join(v_dir, "edited_graded.mp4")
        ed_matte  = os.path.join(v_dir, "edited_matte.mp4")
        ed_voice  = os.path.join(v_dir, "edited_voice_48k.wav")
        ed_meta_p = os.path.join(v_dir, "edl_meta.json")
        ed_tr_p   = os.path.join(v_dir, "main_cut_clean.json")

        if all(os.path.exists(p) and os.path.getsize(p) > 5000 for p in (ed_graded, ed_matte, ed_voice, ed_meta_p, ed_tr_p)):
            m_ex = json.load(open(ed_meta_p, "r", encoding="utf-8"))
            print(f"[SKIP CACHED] {vid_key} ({ep['code']}) -> {m_ex['total_frames']}f ({m_ex['duration_s']}s)", flush=True)
            summary_report.append(m_ex)
            continue

        print(f"\n=== Processing {vid_key} ({ep['code']} • {ep['final_name']}) ===", flush=True)

        # Denoised real mic audio (for indoor episodes v01..v17)
        has_real = any(p[0] == "real" for p in ep["pieces"])
        if has_real:
            full_mic = read_f32_48k(clean_mic, af="highpass=f=80,afftdn=nf=-24")
            ref_rms = rms_active(full_mic)
        else:
            full_mic = None
            ref_rms = 0.145

        # Normalize raw video to 1080x1920 30fps CFR temporary file so frame-exact slicing is 100% deterministic
        norm_src = os.path.join(v_dir, "_norm_30fps.mp4")
        if not os.path.exists(norm_src):
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-i", src_mp4,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                "-r", "30", "-fps_mode", "cfr", "-an",
                "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
                norm_src
            ], check=True)
        max_src_f = int(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=nb_frames", "-of", "csv=p=0", norm_src
        ], text=True).strip() or "1800")

        # Resolve piece frame counts & audio arrays
        resolved_pieces = []
        audio_chunks = []
        edl_items = []
        clone_spans = []
        cur_f = 0
        n_pieces = len(ep["pieces"])

        for pi, p_spec in enumerate(ep["pieces"]):
            is_last = (pi == n_pieces - 1)
            if p_spec[0] == "real":
                _, s_sec, e_sec, lbl = p_spec
                sf = max(0, int(round(s_sec * FPS)))
                ef_raw = min(max_src_f - 1, int(round(e_sec * FPS)))
                nf_speech = max(6, ef_raw - sf)
                tail_pad_f = 22 if is_last else 0  # +0.73s musical outro hold if last piece is real!
                nf_tot = nf_speech + tail_pad_f

                s_idx = int(round((sf / FPS) * SR))
                n_sp_samp = int(round((nf_speech / FPS) * SR))
                n_tot_samp = int(round((nf_tot / FPS) * SR))
                seg_sp = full_mic[s_idx : s_idx + n_sp_samp]
                if len(seg_sp) < n_sp_samp:
                    seg_sp = np.vstack([seg_sp, np.zeros((n_sp_samp - len(seg_sp), 2), dtype=np.float32)])
                seg_sp = apply_micro_fade(seg_sp, 0.018, 0.025)
                if tail_pad_f > 0:
                    seg_a = np.vstack([seg_sp, np.zeros((n_tot_samp - len(seg_sp), 2), dtype=np.float32)])
                else:
                    seg_a = seg_sp

                resolved_pieces.append(("real", sf, nf_tot, lbl, None))
            else:
                _, bg_s, c_key, c_cands, disp_txt, lbl = p_spec
                c_wav = get_or_synth_clone(c_key, c_cands)
                c_arr = read_f32_48k(c_wav)
                c_rms = rms_active(c_arr)
                scaled = apply_micro_fade(c_arr * (ref_rms / max(1e-5, c_rms)), 0.020, 0.030)

                pre_s  = 0.10
                post_s = 0.80 if is_last else 0.16
                nf_tot = int(math.ceil((pre_s + len(scaled) / SR + post_s) * FPS))
                n_tot_samp = int(round((nf_tot / FPS) * SR))
                seg_a = np.zeros((n_tot_samp, 2), dtype=np.float32)
                p0 = int(round(pre_s * SR))
                put = min(n_tot_samp - p0, len(scaled))
                seg_a[p0 : p0 + put] = scaled[:put]

                sf = max(0, min(max_src_f - 30, int(round(bg_s * FPS))))
                resolved_pieces.append(("clone", sf, nf_tot, lbl, disp_txt))
                clone_spans.append({
                    "key": c_key,
                    "label": lbl,
                    "start_s": round(cur_f / FPS, 3),
                    "end_s": round((cur_f + nf_tot) / FPS, 3),
                    "display_text": disp_txt,
                })

            audio_chunks.append(seg_a)
            edl_items.append({
                "label": lbl,
                "kind": p_spec[0],
                "src_start_s": round(sf / FPS, 3),
                "out_start_s": round(cur_f / FPS, 3),
                "out_end_s": round((cur_f + nf_tot) / FPS, 3),
                "frames": nf_tot,
            })
            cur_f += nf_tot

        total_frames = cur_f
        total_dur = total_frames / FPS

        # Save hybrid 48kHz voice WAV
        hybrid_vo = np.vstack(audio_chunks)
        exact_samples = int(round(total_dur * SR))
        if len(hybrid_vo) < exact_samples:
            hybrid_vo = np.vstack([hybrid_vo, np.zeros((exact_samples - len(hybrid_vo), 2), dtype=np.float32)])
        else:
            hybrid_vo = hybrid_vo[:exact_samples]
        pcm_vo = (np.clip(hybrid_vo, -0.99, 0.99) * 32767.0).astype(np.int16)
        with wave.open(ed_voice, "wb") as wf:
            wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm_vo.tobytes())

        # Slice & concat video + apply 01_HTPM_Beauty_Rosy_Skin.cube (48%/52% blend) in ONE fast NVENC pass!
        lut_local = os.path.join(v_dir, "_rosy.cube")
        shutil.copy2(LUT_ROSY, lut_local)
        vg_parts, vg_ins = [], []
        for i, (_, sf, nf, _, _) in enumerate(resolved_pieces):
            ef = min(max_src_f - 1, sf + nf - 1)
            avail = max(1, ef - sf + 1)
            pad_f = max(0, nf - avail)
            pad_str = f",tpad=stop_mode=clone:stop_duration={pad_f/FPS:.6f}" if pad_f > 0 else ""
            vg_parts.append(f"[0:v]select='between(n,{sf},{ef})',setpts=N/30/TB{pad_str}[v{i}];")
            vg_ins.append(f"[v{i}]")
        fc_grade = (
            "".join(vg_parts) + "".join(vg_ins)
            + f"concat=n={len(resolved_pieces)}:v=1:a=0,split=2[va][vb];"
            + "[vb]lut3d=_rosy.cube[vbg];[va][vbg]blend=all_expr=A*0.48+B*0.52[vout]"
        )
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", norm_src,
            "-filter_complex", fc_grade, "-map", "[vout]",
            "-r", "30", "-fps_mode", "cfr", "-frames:v", str(total_frames),
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
            ed_graded
        ], cwd=v_dir, check=True)
        os.remove(lut_local)
        os.remove(norm_src)

        # GPU PyTorch RVM FP16 Matting directly on edited_graded.mp4 (~180 fps!)
        pv = subprocess.Popen(["ffmpeg", "-v", "error", "-i", ed_graded, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        pm = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "gray", "-s", "1080x1920", "-r", "30", "-i", "-",
            "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
            ed_matte
        ], stdin=subprocess.PIPE)
        rec = [None, None, None, None]
        with torch.no_grad():
            for _ in range(total_frames):
                raw_b = pv.stdout.read(1080 * 1920 * 3)
                if len(raw_b) < 1080 * 1920 * 3:
                    break
                t_im = torch.from_numpy(np.frombuffer(raw_b, dtype=np.uint8).copy().reshape((1, 1920, 1080, 3))).cuda().permute(0, 3, 1, 2).half() / 255.0
                _, pha, *rec = rvm_model(t_im, *rec, downsample_ratio=0.25)
                pha_u8 = (pha[0, 0] * 255.0).clamp(0, 255).byte().cpu().numpy()
                pm.stdin.write(pha_u8.tobytes())
        pm.stdin.close(); pm.wait()
        pv.stdout.close(); pv.wait()

        # Transcribe assembled hybrid voice track on VAD islands with GPU Whisper + Polish Vietnamese text!
        n3_vo = (len(hybrid_vo) // 3) * 3
        mono16 = hybrid_vo[:n3_vo, 0].reshape((-1, 3)).mean(axis=1).astype(np.float32)
        hop16 = 320
        nh16 = len(mono16) // hop16
        rms16 = np.sqrt(np.mean(mono16[:nh16*hop16].reshape((nh16, hop16)) ** 2, axis=1))
        act16 = rms16 > 0.014
        dil16 = np.zeros_like(act16)
        for i16 in range(nh16):
            if act16[i16]:
                dil16[max(0, i16 - 8) : min(nh16, i16 + 10)] = True
        islands, in_s, sh0 = [], False, 0
        for i16 in range(nh16):
            if dil16[i16] and not in_s:
                in_s, sh0 = True, i16
            elif not dil16[i16] and in_s:
                in_s = False
                if i16 - sh0 >= 7:
                    islands.append((sh0 * hop16 / 16000.0, i16 * hop16 / 16000.0))
        if in_s and nh16 - sh0 >= 7:
            islands.append((sh0 * hop16 / 16000.0, nh16 * hop16 / 16000.0))

        merged_is = []
        for st_i, en_i in islands:
            if merged_is and (st_i - merged_is[-1][1]) < 0.42 and (en_i - merged_is[-1][0]) <= 12.5:
                merged_is[-1] = (merged_is[-1][0], en_i)
            else:
                cur_s = st_i
                while (en_i - cur_s) > 13.5:
                    w_lo = int((cur_s + 7.5) * 16000 / hop16)
                    w_hi = min(nh16 - 1, int((cur_s + 12.5) * 16000 / hop16))
                    bh = w_lo + int(np.argmin(rms16[w_lo : w_hi + 1]))
                    ct = bh * hop16 / 16000.0
                    merged_is.append((cur_s, ct))
                    cur_s = ct
                merged_is.append((cur_s, en_i))

        segs_clean = []
        for is_st, is_en in merged_is:
            sub16 = mono16[int(is_st * 16000) : int(is_en * 16000)]
            if len(sub16) < 2000:
                continue
            res_w = asr_pipe(
                {"array": sub16, "sampling_rate": 16000},
                return_timestamps="word",
                generate_kwargs={"language": "vi", "task": "transcribe"},
            )
            raw_ws = []
            for ch in res_w.get("chunks", []):
                wt = (ch.get("text") or "").strip()
                ts = ch.get("timestamp") or (None, None)
                if not wt:
                    continue
                rs = is_st + float(ts[0] if ts[0] is not None else 0.0)
                re_t = is_st + float(ts[1] if ts[1] is not None else (float(ts[0] or 0.0) + 0.22))
                if re_t <= rs:
                    re_t = rs + 0.15
                raw_ws.append({"word": wt, "start": round(rs, 3), "end": round(min(is_en + 0.12, re_t), 3)})
            if not raw_ws:
                continue

            # Polish full segment text and redistribute word timings cleanly if token count changes slightly
            raw_sent = " ".join(x["word"] for x in raw_ws)
            pol_sent = polish_vi_text(raw_sent)
            pol_toks = [t for t in pol_sent.split() if t]
            if len(pol_toks) == len(raw_ws):
                for k_w in range(len(raw_ws)):
                    raw_ws[k_w]["word"] = pol_toks[k_w]
                final_ws = raw_ws
            else:
                t_a, t_b = raw_ws[0]["start"], raw_ws[-1]["end"]
                tot_ch = max(1, sum(len(t) for t in pol_toks))
                cur_t = t_a
                final_ws = []
                for tk in pol_toks:
                    dt_w = (t_b - t_a) * (len(tk) / tot_ch)
                    final_ws.append({"word": tk, "start": round(cur_t, 3), "end": round(cur_t + dt_w, 3)})
                    cur_t += dt_w

            segs_clean.append({
                "start": final_ws[0]["start"],
                "end": final_ws[-1]["end"],
                "text": " ".join(x["word"] for x in final_ws),
                "words": final_ws,
            })

        face_box = [335, 558, 725, 1045]
        vad_orig_p = os.path.join(v_dir, "vad_tr.json")
        if os.path.exists(vad_orig_p):
            face_box = json.load(open(vad_orig_p, "r", encoding="utf-8")).get("face_box", face_box)

        meta_obj = {
            "vid_key": vid_key,
            "idx": idx,
            "code": ep["code"],
            "brand": ep["brand"],
            "final_name": ep["final_name"],
            "total_frames": total_frames,
            "duration_s": round(total_dur, 3),
            "face_box": face_box,
            "clone_spans": clone_spans,
            "edl": edl_items,
        }
        json.dump(meta_obj, open(ed_meta_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        json.dump({"lang": "vi", "duration": round(total_dur, 3), "total_frames": total_frames, "segments": segs_clean}, open(ed_tr_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

        summary_report.append(meta_obj)
        print(f"  -> DONE {vid_key} ({ep['code']}) in {time.time() - t_ep:.1f}s | {total_frames}f = {total_dur:.2f}s | clones={len(clone_spans)} | segs={len(segs_clean)}", flush=True)
        for s_c in segs_clean:
            print(f"     [{s_c['start']:5.2f}-{s_c['end']:5.2f}] {s_c['text']}", flush=True)

    json.dump(summary_report, open(os.path.join(BATCH_DIR, "all_17_edl_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n=== ALL 17 EPISODES EDL + VOICE STUDIO + GPU RVM COMPLETED IN {time.time() - t_start:.1f}s ===", flush=True)

if __name__ == "__main__":
    main()
