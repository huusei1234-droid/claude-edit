# -*- coding: utf-8 -*-
"""
V6 STEP 3 — KẾT XUẤT TRỌN BỘ 12 VIDEO AI USP TÔNG TRONG TRẺO CHUẨN GROUP ZALO (`1080x1920 @ 24fps`):
1. 0% BLING-BLING / 0% ÁM TÍM HỒNG: Gỡ bỏ hoàn toàn video hạt lấp lánh/flare & nền tối; chuyển sang 100% Tông Sáng Trắng Ngọc Trai – Nắng Sớm Trong Trẻo!
2. 0% RUNG CẦM CẬP: Gỡ bỏ 100% FFmpeg `zoompan` và `setpts > 1.0`; toàn bộ 120 cảnh chạy mượt ở tốc độ gốc 1.0x 24fps + GPU sub-pixel!
3. 0% MẤT SẢN PHẨM / MẤT NHÃN: Loại bỏ 100% clip AI tự vẽ chai lọ mờ chữ; gắn trực tiếp ảnh gốc tách nền sắc nét `SP_*_CUTOUT.png` lên bục đá nắng sớm chuyển động mượt (`sunpod_01..06`) + thẻ giới thiệu & End-Card!
4. 100% KỊCH BẢN & THÀNH PHẦN CHUẨN GROUP ZALO `CONTENT HẰNG THU PHARMA` NGÀY 25/11 (0% Ích mẫu trên Điều Kinh HT, đủ thành phần chuẩn cho cả 10 dòng + ưu đãi 5% duy nhất 2026!).
5. 100% KHÔNG CHE MẶT (`Face-Safe`) & 100% VÙNG AN TOÀN TIKTOK × REELS (`X: 54..884px`, `Y: 248..1548px`)!
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

THIS_DIR = Path(r"d:\AI\full studio\output\htpm-ngay-261125")
sys.path.insert(0, str(THIS_DIR))

from day25_master_spec import (
    BATCH_ROOT, PROD_DIR, BRAND_KIT, K6_DAY25_DIR, CLOUD_DAY25_VID, LOCAL_DAY25_DIR, SLOTS_261125,
)

V4_COUPLE_ROOT = Path(r"d:\AI\full studio\output\htpm-ai-usp-v4-261125")
V5_RAW_VID = BATCH_ROOT / "10_V5_Action_USP" / "02_Flow_Raw"
V6_ROOT = BATCH_ROOT / "12_V6_Crystal_Clear_USP"
V6_VO_ROOT = V6_ROOT / "01_Voices"
V6_CLEAN_VID = V6_ROOT / "03_Clean_Native24_Clips"
V6_CLEAN_VID.mkdir(parents=True, exist_ok=True)

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
ARTIFACT_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682")

# Pure airy crystal-clear daylight color grade (bright, fresh, natural skin, zero purple/murky tint)
COLOR_GRADE_AIRY = (
    '{&quot;preset&quot;:null,&quot;intensity&quot;:1,&quot;adjust&quot;:{&quot;exposure&quot;:0.04,&quot;contrast&quot;:0.04,'
    '&quot;highlights&quot;:0.02,&quot;shadows&quot;:0.06,&quot;whites&quot;:0.05,&quot;blacks&quot;:0,&quot;temperature&quot;:0.0,'
    '&quot;tint&quot;:0.0,&quot;vibrance&quot;:0.08,&quot;saturation&quot;:0.02},&quot;details&quot;:{&quot;vignette&quot;:0,'
    '&quot;vignetteMidpoint&quot;:0.5,&quot;vignetteRoundness&quot;:0,&quot;vignetteFeather&quot;:0.65,&quot;grain&quot;:0,'
    '&quot;grainSize&quot;:0.25,&quot;grainRoughness&quot;:0.5},&quot;effects&quot;:{&quot;blur&quot;:0,&quot;pixelate&quot;:0,'
    '&quot;chromaBleed&quot;:0,&quot;tapeDamage&quot;:0,&quot;tapeTracking&quot;:0,&quot;tapeNoise&quot;:1,&quot;tapeSpeed&quot;:0.5,'
    '&quot;filmArtifacts&quot;:0,&quot;halftone&quot;:0,&quot;halftoneSize&quot;:0,&quot;twoInkPrint&quot;:0,&quot;twoInkPrintSize&quot;:0,'
    '&quot;ascii&quot;:0,&quot;asciiSize&quot;:0.065,&quot;asciiInvert&quot;:0,&quot;asciiStyle&quot;:0,&quot;asciiColor&quot;:1,'
    '&quot;asciiRotation&quot;:0,&quot;dither&quot;:0,&quot;ditherSize&quot;:0,&quot;bloom&quot;:0,&quot;bloomRadius&quot;:8,'
    '&quot;monoScreen&quot;:0,&quot;monoScreenSize&quot;:0,&quot;monoScreenAngle&quot;:0,&quot;monoScreenSpread&quot;:0,'
    '&quot;monoScreenShape&quot;:0,&quot;monoScreenInvert&quot;:0,&quot;scanlines&quot;:0,&quot;scanlineCount&quot;:0,'
    '&quot;scanlineSoftness&quot;:0,&quot;chromaticAberration&quot;:0,&quot;chromaticAngle&quot;:0,&quot;crtCurvature&quot;:0,'
    '&quot;digitalGlitch&quot;:0,&quot;digitalGlitchColorSplit&quot;:0,&quot;digitalGlitchLineTear&quot;:0,'
    '&quot;digitalGlitchPixelate&quot;:0,&quot;digitalGlitchBlockAmount&quot;:0,&quot;digitalGlitchBlockDisplacement&quot;:0,'
    '&quot;digitalGlitchBlockOpacity&quot;:0,&quot;digitalGlitchSpeed&quot;:0,&quot;engraving&quot;:0,&quot;engravingSpacing&quot;:0.41,'
    '&quot;engravingMinThickness&quot;:0.2,&quot;engravingMaxThickness&quot;:0.45,&quot;engravingAngle&quot;:0.25,'
    '&quot;engravingContrast&quot;:0.46,&quot;engravingSharpness&quot;:0.59,&quot;engravingWave&quot;:0.2,'
    '&quot;engravingWaveFrequency&quot;:0.22,&quot;crosshatch&quot;:0,&quot;crosshatchSpacing&quot;:0.28,'
    '&quot;crosshatchThickness&quot;:0.25,&quot;crosshatchAngle&quot;:0.25,&quot;crosshatchContrast&quot;:0.33,'
    '&quot;crosshatchEdges&quot;:0.5,&quot;crosshatchLineWeight&quot;:0,&quot;crosshatchWave&quot;:0.33,'
    '&quot;crosshatchWaveFrequency&quot;:0.22,&quot;kuwahara&quot;:0,&quot;kuwaharaRadius&quot;:0.14,&quot;kuwaharaSharpness&quot;:0.31,'
    '&quot;kuwaharaSaturation&quot;:0.5},&quot;lut&quot;:null,&quot;colorSpace&quot;:&quot;rec709&quot;}'
)

VO_FX_CHAIN = (
    '{&quot;version&quot;:1,&quot;nodes&quot;:['
    '{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;vhp&quot;,&quot;label&quot;:&quot;Clean rumble&quot;,&quot;params&quot;:{&quot;frequency&quot;:85}},'
    '{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;vlow&quot;,&quot;label&quot;:&quot;Warmth balance&quot;,&quot;params&quot;:{&quot;frequency&quot;:210,&quot;gain&quot;:-1.5,&quot;q&quot;:1.1}},'
    '{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;vpres&quot;,&quot;label&quot;:&quot;Broadcast clarity&quot;,&quot;params&quot;:{&quot;frequency&quot;:3100,&quot;gain&quot;:1.9,&quot;q&quot;:1.0}},'
    '{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;vlim&quot;,&quot;params&quot;:{&quot;limit&quot;:-1.0}}]}'
)

# 100% VERIFIED CLEAN BRIGHT DAYLIGHT 10-CUT STORYBOARD MAPS:
# - ZERO banned missing-label/blank-bottle clips!
# - ZERO dark evening clips!
# - Cut 3 = 3D CGI Mechanism, Cut 7 = Sunlit Podium + Giant Real SP_*_CUTOUT DOM Layer, Cut 8 = 3D Botanical Macro, Cut 10 = Airy Split End-Card!
V6_10CUT_MAPS = {
    "v01_lt_plus": [
        "act_v01_c01_street_rush",        # C01: Bước nhanh trên phố nắng sớm đi làm
        "act_v01_c02_office_shift",       # C02: Ngồi bàn làm việc văn phòng mệt mỏi thiếu thoải mái
        "cgi_v01",                        # C03: 3D CGI màng chắn ẩm ngọc trai cân bằng pH
        "act_v01_c04_car_schedule",       # C04: Ngồi xe ô tô di chuyển xem lịch trình
        "day_act_01_vanity_morning",      # C05: Buổi sáng trong phòng trắng ngập nắng chăm sóc bản thân (+ Thẻ LT Plus thật!)
        "act_v07_c06_car_buckle_confident", # C06: Ngồi xe ô tô đi làm tự tin rạng ngời
        "sunpod_01_rose_water",           # C07: Bục đá cẩm thạch nước hồng nắng sớm + Hộp LT Plus thật siêu nét!
        "mac_v01",                        # C08: 3D Macro Thảo dược & hoa thanh khiết
        "act_v01_c09_boulevard_walk",     # C09: Dạo bước thảnh thơi trên đại lộ ngập nắng
        "day_act_06_sunlit_garden_breeze", # C10: Sân hiên hoa hồng gió biển trong trẻo + Airy Split End-Card
    ],
    "v02_gel_phu_khang": [
        "act_v02_c01_desk_stretch",       # C01: Ngồi bàn kính văn phòng 8 tiếng vươn vai mỏi mệt
        "act_v01_c01_street_rush",        # C02: Tất bật di chuyển ngoài đường phố cả ngày
        "cgi_v02",                        # C03: 3D CGI bọt tơ mịn & sương mát thanh khiết
        "act_v01_c04_car_schedule",       # C04: Đi xe ô tô công tác bận rộn
        "day_act_02_handbag_zip_walk",    # C05: Sảnh nhà đá trắng ngập nắng cầm túi xách nhỏ gọn (+ Thẻ Gel Phụ Khang thật!)
        "act_v06_c06_car_selfie_cam",     # C06: Ngồi trên xe ô tô tươi tắn suốt ngày dài
        "sunpod_02_aqua_orchid",          # C07: Bục đá Carrara nước trong & hoa lan trắng + Bộ Gel Phụ Khang 5ml thật!
        "mac_v02",                        # C08: 3D Macro Thảo mộc xanh & hoa trắng
        "act_v02_c09_boutique_stroll",    # C09: Dạo phố boutique rợp nắng tự tin
        "act_v01_c09_boulevard_walk",     # C10: Đại lộ nắng sớm trong trẻo + Airy Split End-Card
    ],
    "v03_da_day_ht": [
        "act_v03_c01_car_coffee",         # C01: Ngồi xe ô tô buổi sáng nhấp vội ly cà phê đá bụng rỗng
        "act_v03_c02_stomach_burn",       # C02: Ngồi bàn làm việc ôm vùng thượng vị nóng rát
        "cgi_v03",                        # C03: 3D CGI Dạ dày pha lê & dòng thảo mộc bao phủ êm dịu
        "act_v03_c04_evening_sofa_bloat", # C04: Ngồi sofa sáng xoa bụng đầy chướng khó tiêu
        "act_v03_c05_kitchen_daday",      # C05: Đứng đảo bếp ngập nắng rót nước ấm cạnh hộp Dạ Dày HT thật rõ nhãn!
        "day_act_04_white_kitchen_water", # C06: Rót ly nước tinh khiết buổi sáng chăm bụng êm khỏe
        "sunpod_03_herbal_travertine",    # C07: Bục đá travertine vườn thảo mộc nắng sớm + Bộ Dạ Dày HT thật siêu nét!
        "mac_v03",                        # C08: 3D Macro Nghệ, Dạ cẩm, Chè dây, Lá khôi
        "act_v03_c09_happy_breakfast",    # C09: Thưởng thức bữa sáng ngon miệng êm bụng tại bàn ăn ngập nắng
        "day_act_03_sunlit_tea_sip",      # C10: Phòng khách nắng mai thưởng trà êm dịu + Airy Split End-Card
    ],
    "v04_dieu_kinh_ht": [
        "act_v04_c01_sofa_cramps",        # C01: Ngồi ghế cửa sổ nắng nhẹ ôm cốc sứ ấm mệt mỏi ngày đèn đỏ
        "act_v04_c02_mirror_pale",        # C02: Soi gương buổi sáng thấy sắc diện kém hồng hào, tay lạnh
        "cgi_v04",                        # C03: 3D CGI Dải lụa khí huyết hồng ngọc lưu thông ấm áp
        "act_v04_c04_open_curtains",      # C04: Kéo rèm voan trắng đón nắng ban mai tràn ngập phòng
        "day_act_03_sunlit_tea_sip",      # C05: Ngồi phòng khách hoa mẫu đơn nâng tách trà ấm (+ Thẻ Điều Kinh HT thật!)
        "act_v08_c09_terrace_tea_pour",   # C06: Rót trà hoa hồng chăm dưỡng cơ thể đều đặn
        "sunpod_01_rose_water",           # C07: Bục đá hồng phấn gợn nước nắng mai + Lọ Điều Kinh HT thật siêu nét!
        "mac_v04",                        # C08: 3D Macro Đương quy, Hương phụ & hoa hồng đào
        "act_v04_c09_flower_street_walk", # C09: Dạo con đường hoa giấy nắng sớm hồng hào rạng rỡ
        "day_act_06_sunlit_garden_breeze", # C10: Sân vườn hoa hồng trong trẻo + Airy Split End-Card
    ],
    "v05_romance_vip": [
        "act_v05_c01_hot_sun_walk",       # C01: Đi bộ dưới trời nắng chói oi bức ngoài phố
        "act_v02_c01_desk_stretch",       # C02: Ngồi lâu ẩm ướt bí bách khó chịu
        "cgi_v05",                        # C03: 3D CGI Màng lụa ẩm Hoa hồng & Lô hội chuẩn pH
        "act_v04_c04_open_curtains",      # C04: Mở rèm voan trắng đón gió mát trong lành
        "act_v05_c05_bathroom_rvip",      # C05: Đặt hộp Romance VIP thật rõ nhãn lên khay pha lê cạnh hoa hồng đỏ!
        "day_act_01_vanity_morning",      # C06: Chăm chút bản thân dịu dàng trong phòng trắng ngập nắng
        "sunpod_01_rose_water",           # C07: Bục đá cẩm thạch nước trong & cánh hoa + Hộp Romance VIP thật siêu nét!
        "mac_v05",                        # C08: 3D Macro Hoa hồng, Lô hội & giọt sương tinh khiết
        "act_v05_c09_car_exit_breeze",    # C09: Bước xuống xe SUV trắng giữa hàng cọ gió biển thanh thoát
        "act_v04_c09_flower_street_walk", # C10: Dạo bước nhẹ tênh dưới nắng mai + Airy Split End-Card
    ],
    "v06_whiteskin": [
        "act_v06_c01_sunglasses_sun",     # C01: Bước xuống phố nắng gắt đeo kính che nắng
        "act_v04_c02_mirror_pale",        # C02: Soi gương sáng kiểm tra vết sạm nám & độ đàn hồi da
        "cgi_v06",                        # C03: 3D CGI Tầng biểu bì pha lê L-Glutathione & Vitamin E trước tia UV
        "day_act_04_white_kitchen_water", # C04: Đứng đảo bếp đá trắng rót ly nước tinh khiết buổi sáng
        "day_act_01_vanity_morning",      # C05: Chăm da sáng khỏe từ bên trong mỗi sáng (+ Thẻ Legend WhiteSkin thật!)
        "act_v06_c06_car_selfie_cam",     # C06: Ngồi xe ô tô nắng tự nhiên soi cam thường ưng ý làn da căng mịn
        "sunpod_02_aqua_orchid",          # C07: Bục đá trắng Carrara trước biển xanh Nha Trang + Bộ WhiteSkin thật siêu nét!
        "mac_v06",                        # C08: 3D Macro L-Glutathione, NMN, Collagen & Vitamin E
        "act_v06_c09_coastal_promenade",  # C09: Sải bước rạng ngời dọc bờ biển Trần Phú nắng trong veo
        "act_v01_c09_boulevard_walk",     # C10: Dạo đại lộ nắng sớm trắng hồng + Airy Split End-Card
    ],
    "v07_vien_dat_xanh": [
        "act_v07_c01_home_tidy_tired",    # C01: Gấp chăn trên sofa phòng khách sáng với nỗi niềm trầm tư sau sinh
        "act_v04_c01_sofa_cramps",        # C02: Ngồi bên khung cửa sổ nắng mai trăn trở chuyện thầm kín
        "cgi_v07",                        # C03: 3D CGI Dải lụa ngọc bích cân bằng vi sinh & săn chắc
        "act_v04_c04_open_curtains",      # C04: Kéo rèm voan đón ánh nắng tích cực vào phòng
        "day_act_05_sunlit_study_journal", # C05: Ghi chú lịch chăm sóc sức khỏe tại phòng sáng (+ Thẻ Viên Đặt Hộp Xanh thật!)
        "act_v07_c06_car_buckle_confident", # C06: Lên xe ô tô đi làm với thần thái nhẹ nhõm tự tin hẳn
        "sunpod_05_emerald_garden",       # C07: Bục đá ngọc bích hoa cúc trắng nắng mai + Hộp Xanh Viên Đặt thật siêu nét!
        "mac_v07",                        # C08: 3D Macro Thảo mộc thanh khiết & hoa trắng đọng sương
        "act_v07_c09_livingroom_flowers", # C09: Cắm bình hoa ly trắng trong phòng khách ngập nắng viên mãn
        "day_act_03_sunlit_tea_sip",      # C10: Thưởng trà sáng thư thái nhẹ người + Airy Split End-Card
    ],
    "v08_romance_love": [
        "act_v04_c02_mirror_pale",        # C01: Ngồi bàn gương buổi sáng trầm tư chuyện khô hạn tuổi 30+
        "act_v07_c01_home_tidy_tired",    # C02: Khoảnh khắc lặng lẽ trong phòng khách sáng khi thiếu độ ẩm tự nhiên
        "cgi_v08",                        # C03: 3D CGI Giọt tinh chất HA & lụa hồng cấp ẩm mềm mịn
        "act_v04_c04_open_curtains",      # C04: Mở rèm đón nắng mới đánh thức cảm xúc yêu thương
        "day_act_06_sunlit_garden_breeze", # C05: Dạo vườn hồng phấn trong nắng sớm (+ Thẻ Romance Love thật!)
        "act_v08_c09_terrace_tea_pour",   # C06: Rót tách trà hoa hồng thơm dịu nâng niu bản thân
        "sunpod_01_rose_water",           # C07: Bục đá ngọc thạch hồng gợn nước trong veo + Hộp Romance Love thật siêu nét!
        "mac_v08",                        # C08: 3D Macro Hoa hồng phấn & tinh chất cấp ẩm lấp lánh tự nhiên
        "act_v05_c09_car_exit_breeze",    # C09: Bước xuống xe giữa đại lộ nắng gió đầy quyến rũ
        "act_v07_c09_livingroom_flowers", # C10: Cắm hoa tươi giữ lửa tổ ấm + Airy Split End-Card
    ],
    "v09_ngoc_long_hoan": [
        "nlh_back_pain",                  # C01: Người đàn ông ngồi bàn làm việc sáng xoa vai lưng mỏi mệt sau tuổi 35
        "day_act_05_sunlit_study_journal", # C02: Người vợ tinh tế ghi chú chăm sóc sức khỏe gia đình
        "cgi_v09",                        # C03: 3D CGI Cột sống & Nguyên khí thận vàng kim dưới nắng sáng
        "act_v09_c04_brew_herbal_tea",    # C04: Chị Hằng rót ấm trà thảo mộc vàng óng trong phòng sáng
        "act_v09_c05_tray_ngoclonghoan",  # C05: Chị Hằng đặt lọ Ngọc Long Hoàn thật rõ nhãn bên tách trà ấm!
        "act_v09_c06_giftbag_car_step",   # C06: Chị Hằng cầm túi quà sang trọng từ xe bước vào hiên nhà nắng
        "sunpod_06_warm_sunlit_amber",    # C07: Bục đá kem-vàng nắng mai & nhân sâm đông trùng + Lọ Ngọc Long Hoàn thật siêu nét!
        "mac_v09",                        # C08: 3D Macro Đông trùng hạ thảo, Nhân sâm & thảo dược quý
        "act_v03_c09_happy_breakfast",    # C09: Bữa sáng gia đình ấm áp tràn đầy sinh lực
        "act_v06_c09_coastal_promenade",  # C10: Dạo biển nắng sớm rạng rỡ (0% chồng ở V09!) + Airy Split End-Card
    ],
    "v10_ceo_thuong_hieu": [
        "act_v10_c01_ceo_car_ipad",       # C01: Ngồi xe sedan lướt đại lộ biển Nha Trang nắng trong veo đọc iPad
        "act_v10_c02_hq_entrance_stride", # C02: Bước xuống xe sải bước vào sảnh tòa nhà kính hiện đại
        "cgi_v10",                        # C03: 3D CGI Bản đồ pha lê Việt Nam tỏa sáng từ Nha Trang
        "act_v10_c04_boardroom_inspect",  # C04: Họp phòng kính kiểm định bộ sản phẩm thật HTPM
        "day_act_05_sunlit_study_journal", # C05: Hoạch định chiến lược đào tạo & ưu đãi 5% cho hệ thống
        "act_v10_c06_coastal_ceo_walk",   # C06: Dạo bước điềm đạm dọc bờ biển Nha Trang xanh ngắt
        "mac_v10",                        # C07: Bục đá trắng cẩm thạch trước vịnh biển Nha Trang + Kệ 8 Sản Phẩm HTPM thật!
        "sunpod_02_aqua_orchid",          # C08: Không gian đá trắng hoa lan biển xanh chuẩn mực thương hiệu
        "act_v09_c04_brew_herbal_tea",    # C09: Khoảnh khắc đời thường ấm áp pha trà sáng
        "act_v06_c09_coastal_promenade",  # C10: Sải bước truyền lửa dưới nắng biển + Airy Split End-Card
    ],
    "flagship_ngoc_long_hoan": [
        "day_act_05_sunlit_study_journal", # C01: Chị Hằng thấu hiểu những vất vả thầm lặng của ông xã
        "nlh_back_pain",                  # C02: Người chồng làm việc căng thẳng xoa vai lưng mỏi mệt
        "cgi_v09",                        # C03: 3D CGI Cột sống & Nguyên khí thận vàng kim
        "act_v09_c04_brew_herbal_tea",    # C04: Chị Hằng pha ấm trà thảo mộc nóng buổi sáng tại nhà
        "act_v09_c05_tray_ngoclonghoan",  # C05: Chị Hằng đặt lọ Ngọc Long Hoàn thật rõ nhãn bên tách trà ấm!
        "act_v09_c06_giftbag_car_step",   # C06: Chuẩn bị món quà sức khỏe chu đáo từ xe bước vào nhà
        "sunpod_06_warm_sunlit_amber",    # C07: Bục đá kem-vàng nắng sớm trong trẻo + Lọ Ngọc Long Hoàn thật siêu nét (0% tím/rung!)
        "mac_v09",                        # C08: 3D Macro Đông trùng hạ thảo, Nhung hươu & thảo dược quý
        "act_v07_c09_livingroom_flowers", # C09: Chăm chút tổ ấm ngập nắng tươi vui
        "act_nlh_couple_tea_end",         # C10: CẢNH CUỐI DUY NHẤT CÓ ANH HẢI: Vợ chồng nâng tách trà sáng bên hiên nhà xanh mát + Airy Split End-Card!
    ],
    "flagship_dieu_kinh_ht": [
        "act_v04_c09_flower_street_walk", # C01: Chị Hằng dạo đường hoa nắng sớm sắc diện hồng hào rạng rỡ
        "act_v04_c01_sofa_cramps",        # C02: Nỗi niềm phụ nữ đến kỳ đau bụng âm ỉ, người uể oải
        "cgi_v04",                        # C03: 3D CGI Dải lụa khí huyết hồng ngọc lưu thông ấm áp
        "act_v04_c04_open_curtains",      # C04: Mở rèm voan trắng đón ánh nắng ban mai trong trẻo
        "day_act_03_sunlit_tea_sip",      # C05: Thưởng tách trà ấm bên hoa mẫu đơn chăm dưỡng từ gốc (+ Thẻ Điều Kinh HT thật!)
        "act_v08_c09_terrace_tea_pour",   # C06: Rót trà hoa đều đặn giữ nhịp sinh học êm hòa
        "sunpod_01_rose_water",           # C07: Bục đá hồng phấn gợn nước nắng mai + Lọ Điều Kinh HT thật siêu nét!
        "mac_v04",                        # C08: 3D Macro Đương quy, Hương phụ & Hồng hoa quý (0% Ích mẫu!)
        "act_v06_c06_car_selfie_cam",     # C09: Ngồi xe ô tô đi làm nhẹ tênh sắc mặt tươi nhuận
        "day_act_06_sunlit_garden_breeze", # C10: Dạo vườn hồng nắng mai trong trẻo (0% chồng!) + Airy Split End-Card
    ],
}


def list_fresh_bgms():
    z_aco = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc")
    z_tvc = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng")
    fb = [
        AUDIO_BUNDLE_DIR / "bgm_sunny_carefree.mp3",
        AUDIO_BUNDLE_DIR / "bgm_coconut_groove_tvc.mp3",
        AUDIO_BUNDLE_DIR / "bgm_fresh_wellness_tvc.mp3",
    ]
    aco = sorted([f for f in z_aco.rglob("*.mp3") if 1_000_000 < f.stat().st_size < 14_000_000]) if z_aco.exists() else []
    tvc = sorted([f for f in z_tvc.rglob("*.mp3") if 1_000_000 < f.stat().st_size < 14_000_000]) if z_tvc.exists() else []
    return (aco if aco else fb), (tvc if tvc else fb)


def ensure_native24_no_stretch(raw_src: Path, clean_dst: Path):
    """
    Encode at 1.000x NATIVE speed (ZERO setpts time-stretch, ZERO zoompan!)
    so there is 0.00% frame-duplication stutter and 0.00% integer-rounding vibration!
    """
    if clean_dst.exists() and clean_dst.stat().st_size > 200_000:
        return clean_dst
    clean_dst.parent.mkdir(parents=True, exist_ok=True)
    vf = "fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(raw_src),
            "-vf", vf, "-r", "24", "-fps_mode", "cfr", "-an",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-g", "24",
            str(clean_dst),
        ],
        check=True,
    )
    return clean_dst


def resolve_clean_native_clip(token: str) -> Path:
    # 1. V6 newly generated sunlit podiums & daytime actions (already native 1.0x 24fps!)
    if token.startswith("sunpod_") or token.startswith("day_act_"):
        p = V6_CLEAN_VID / f"{token}.mp4"
        if not p.exists():
            raise FileNotFoundError(f"Missing V6 clip: {p}")
        return p
    # 2. Kept V5 raw Flow clips -> convert from RAW (`02_Flow_Raw`) at 1.0x native speed (NO V5 stretch!)
    if token.startswith("act_"):
        raw_p = V5_RAW_VID / f"{token}_raw.mp4"
        return ensure_native24_no_stretch(raw_p, V6_CLEAN_VID / f"{token}_native24.mp4")
    if token == "nlh_back_pain":
        raw_p = V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "03_Flow_Raw" / "NLH4_C02_raw.mp4"
        if not raw_p.exists():
            raw_p = V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos" / "NLH4_C02.mp4"
        return ensure_native24_no_stretch(raw_p, V6_CLEAN_VID / "nlh_back_pain_native24.mp4")
    if token.startswith("cgi_v") or token.startswith("mac_v"):
        idx = int(token[-2:])
        is_cgi = token.startswith("cgi_")
        if idx == 4:
            fn = "DK4_C03" if is_cgi else "DK4_C05"
            raw_p = V4_COUPLE_ROOT / "c02_dieu_kinh_ht" / "03_Flow_Raw" / f"{fn}_raw.mp4"
            if not raw_p.exists():
                raw_p = V4_COUPLE_ROOT / "c02_dieu_kinh_ht" / "07_HyperFrames_Project" / "assets" / "videos" / f"{fn}.mp4"
        elif idx == 9:
            fn = "NLH4_C03" if is_cgi else "NLH4_C04"
            raw_p = V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "03_Flow_Raw" / f"{fn}_raw.mp4"
            if not raw_p.exists():
                raw_p = V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos" / f"{fn}.mp4"
        else:
            sl = SLOTS_261125[idx - 1]
            fn = f"V{idx:02d}_U02" if is_cgi else f"V{idx:02d}_U04"
            raw_p = BATCH_ROOT / sl["vkey"] / "03_Flow_Raw" / f"{fn}_raw.mp4"
            if not raw_p.exists():
                raw_p = BATCH_ROOT / sl["vkey"] / "07_HyperFrames_Project" / "assets" / "videos" / f"{fn}.mp4"
        return ensure_native24_no_stretch(raw_p, V6_CLEAN_VID / f"{token}_native24.mp4")
    raise KeyError(f"Unknown token: {token}")


def build_and_render_v6_video(cfg: dict, bgm1_src: Path, bgm2_src: Path):
    vkey = cfg["vkey"]
    work_dir = V6_ROOT / "renders" / vkey
    hf_dir = work_dir / "07_HyperFrames_Project"
    comp_dir = hf_dir / "compositions"
    vid_dir = hf_dir / "assets" / "videos"
    img_dir = hf_dir / "assets" / "images"
    aud_dir = hf_dir / "assets" / "audio"
    fnt_dir = hf_dir / "assets" / "fonts"
    for _d in (comp_dir, vid_dir, img_dir, aud_dir, fnt_dir):
        _d.mkdir(parents=True, exist_ok=True)

    for fn in ("Fraunces-Black.ttf", "PlayfairDisplay-BoldItalic.ttf", "BeVietnamPro-ExtraBold.ttf", "BeVietnamPro-Bold.ttf", "BeVietnamPro-SemiBold.ttf"):
        src_f = FONTS_BUNDLE_DIR / fn
        if src_f.exists() and not (fnt_dir / fn).exists():
            shutil.copy2(src_f, fnt_dir / fn)

    logo_src = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124\10_Bai_Thiet_Ke_Soft_Editorial\ht_logo_33mp_clean.png")
    if not logo_src.exists():
        logo_src = BRAND_KIT / "logos_png" / "ht_logo_official.png"
    shutil.copy2(logo_src, img_dir / "ht_logo.png")
    shutil.copy2(PROD_DIR / cfg["cutout"], img_dir / cfg["cutout"])

    vo_dir = V6_VO_ROOT / vkey
    vo_m = json.loads((vo_dir / "vo_manifest.json").read_text(encoding="utf-8"))
    segs = vo_m["segments"]
    total_dur = float(vo_m["total_duration_s"])

    for s in segs:
        shutil.copy2(vo_dir / f"{s['id']}.wav", aud_dir / f"{s['id']}.wav")
    shutil.copy2(bgm1_src, aud_dir / "bgm_1.mp3")
    shutil.copy2(bgm2_src, aud_dir / "bgm_2.mp3")
    for sfx_fn in ("sfx_whoosh_soft.mp3", "sfx_pop_clean.mp3", "sfx_chime_warm.mp3"):
        if (AUDIO_BUNDLE_DIR / sfx_fn).exists():
            shutil.copy2(AUDIO_BUNDLE_DIR / sfx_fn, aud_dir / sfx_fn)

    # Split each VO segment into 2 crisp native-speed cuts (~3.3s - 4.1s each -> 100% < 5.5s native Flow clip!)
    ratios = [0.48, 0.52, 0.50, 0.52, 0.44]
    tokens = V6_10CUT_MAPS[vkey]
    cuts_10 = []
    for si, s in enumerate(segs):
        st = float(s["shot_start_s"])
        dur = float(s["shot_duration_s"])
        d_a = round(dur * ratios[si], 2)
        d_b = round(dur - d_a, 2)
        cuts_10.append((si * 2 + 1, tokens[si * 2], st, d_a))
        cuts_10.append((si * 2 + 2, tokens[si * 2 + 1], round(st + d_a, 2), d_b))

    for c_idx, tok, c_st, c_dur in cuts_10:
        src_clip = resolve_clean_native_clip(tok)
        shutil.copy2(src_clip, vid_dir / f"C{c_idx:02d}.mp4")

    pri = cfg["pri"]
    pri_dark = cfg["pri_dark"]
    pri_soft = cfg["pri_soft"]

    # Direct native 1:1 <video> playback (NO .cam-rig scale jitter, NO bling ov-screen!)
    vid_tags = []
    for c_idx, tok, c_st, c_dur in cuts_10[:9]:
        vid_tags.append(
            f'    <video data-color-grading="{COLOR_GRADE_AIRY}" id="vid-{c_idx:02d}" class="clip bg-video" '
            f'src="assets/videos/C{c_idx:02d}.mp4" data-start="{c_st:.2f}" data-duration="{c_dur:.2f}" '
            f'data-media-start="0.10" data-hf-media-start-basis="local" data-track-index="{c_idx}" muted playsinline></video>'
        )

    c3_st, c3_dur = cuts_10[2][2], cuts_10[2][3]
    c5_st, c5_dur = cuts_10[4][2], cuts_10[4][3]
    c6_st, c6_dur = cuts_10[5][2], cuts_10[5][3]
    c7_st, c7_dur = cuts_10[6][2], cuts_10[6][3]
    c8_st, c8_dur = cuts_10[7][2], cuts_10[7][3]
    c10_st, c10_dur = cuts_10[9][2], cuts_10[9][3]

    hook_end = round(min(cuts_10[0][3] + 0.30, 3.50), 2)
    choice_st = round(c5_st + 0.12, 2)
    choice_dur = round(min(c5_dur + c6_dur - 0.30, 4.10), 2)
    mid_t = round(c5_st, 2)

    # Frosted Pearl-White Daylight Captions (airy, fresh, high-contrast, 0% funeral black!)
    cap_divs = []
    cap_js = []
    cap_n = 0
    for si, (_, l1_html, l2_html) in enumerate(cfg["caps_pair"]):
        c_a = cuts_10[si * 2]
        c_b = cuts_10[si * 2 + 1]
        for st_c, dur_c, txt_html in [(c_a[2], c_a[3], l1_html), (c_b[2], c_b[3], l2_html)]:
            cap_n += 1
            cid = f"cap-{cap_n:02d}"
            in_id = f"cap-in-{cap_n:02d}"
            d_safe = max(0.5, round(dur_c - 0.10, 2))
            cap_divs.append(f'    <div id="{cid}" class="clip cap-box" data-start="{st_c + 0.04:.2f}" data-duration="{d_safe:.2f}" data-track-index="40"><div id="{in_id}" class="cap-txt">{txt_html}</div></div>')
            cap_js.append(
                f'    tl.fromTo("#{in_id}", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "power2.out" }}, {st_c + 0.04:.2f});\n'
                f'    tl.to("#{in_id}", {{ opacity: 0, duration: 0.12 }}, {st_c + d_safe - 0.08:.2f});'
            )

    rows_s1 = "\n".join(
        f'        <div class="usp-row"><span class="usp-num">{i}</span><span>{r}</span></div>'
        for i, r in enumerate(cfg["slide1_rows"], start=1)
    )
    rows_s2 = "\n".join(
        f'        <div class="usp-row"><span class="usp-num">✓</span><span>{r}</span></div>'
        for i, r in enumerate(cfg["slide3_pills"], start=1)
    )

    is_shelf = (cfg["cutout"] == "SP_HTPM_FULL_8SKU_SHELF.png")
    c7_prod_style = "max-width: 740px; max-height: 390px;" if is_shelf else "max-width: 560px; max-height: 550px;"

    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "FrauncesVN"; src: url("assets/fonts/Fraunces-Black.ttf") format("truetype"); font-weight: 900; }}
    @font-face {{ font-family: "PlayfairIt"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; }}
    @font-face {{ font-family: "BeVNExtra"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; }}
    @font-face {{ font-family: "BeVNBold"; src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype"); font-weight: 700; }}
    @font-face {{ font-family: "BeVNSemi"; src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype"); font-weight: 600; }}

    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: #F8FAFC; font-family: "BeVNExtra", sans-serif; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}

    /* Clean Airy Top Progress & Brand Pill (strictly Y=252..326px, 0% touching face!) */
    .prog-track {{ position: absolute; left: 56px; top: 252px; width: 966px; height: 6px; border-radius: 99px; background: rgba(255,255,255,0.58); z-index: 30; overflow: hidden; }}
    .prog-fill {{ width: 100%; height: 100%; transform-origin: 0% 50%; background: {pri}; }}
    .brand-pill {{
      position: absolute; left: 56px; top: 268px; z-index: 28;
      display: inline-flex; align-items: center; gap: 10px;
      background: rgba(255,255,255,0.96); border: 2px solid {pri};
      border-radius: 999px; padding: 6px 18px 6px 8px;
      box-shadow: 0 8px 20px rgba(20,30,45,0.12);
    }}
    .brand-pill img {{ width: 38px; height: 38px; border-radius: 50%; object-fit: contain; }}
    .brand-pill .bp-t {{ font-size: 18px; color: {pri_dark}; letter-spacing: 0.04em; line-height: 1.1; }}
    .seal-badge {{
      position: absolute; left: 926px; top: 266px; width: 90px; height: 90px; border-radius: 50%; z-index: 28;
      background: #FFFFFF; border: 3px solid {pri};
      color: {pri_dark}; display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; font-size: 12px; line-height: 1.12; box-shadow: 0 8px 20px rgba(20,30,45,0.14);
    }}
    .seal-badge b {{ font-size: 20px; color: {pri}; display: block; }}

    /* 100% FACE-SAFE LOWER HOOK BANNER (Y=1142..1362px, X=58..878px) */
    .hook-lower {{ position: absolute; left: 58px; top: 1142px; width: 820px; z-index: 22; pointer-events: none; }}
    .hook-kicker {{
      display: inline-block; background: {pri}; color: #FFFFFF;
      font-size: 23px; padding: 7px 22px; border-radius: 999px;
      border: 2.5px solid #FFFFFF; letter-spacing: 0.04em; margin-bottom: 8px;
      box-shadow: 0 8px 20px rgba(20,30,45,0.18);
    }}
    .hook-title {{
      font-family: "FrauncesVN", serif; font-size: 68px; line-height: 1.06; color: {pri};
      -webkit-text-stroke: 14px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 8px 18px rgba(20,30,45,0.22));
    }}

    /* CUT 5-6 REAL PRODUCT INTRO PILL (100% Real SP_*_CUTOUT, Y=1192..1358px, X=58..818px -> 0% Face Overlap!) */
    .choice-pill {{
      position: absolute; left: 58px; top: 1196px; width: 770px; z-index: 22;
      background: rgba(255,255,255,0.97); border-left: 10px solid {pri}; border-top: 2px solid #FFF;
      border-radius: 26px; padding: 14px 24px; display: flex; align-items: center; gap: 18px;
      box-shadow: 0 14px 32px rgba(20,30,45,0.16);
    }}
    .choice-pill img {{ width: 92px; height: 108px; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.16)); }}
    .choice-pill .cp-txt {{ font-size: 28px; line-height: 1.26; color: {pri_dark}; }}

    /* FROSTED DAYLIGHT USP CARDS (Cuts 3 & 7 ONLY -> 0% human face!) */
    .usp-card {{
      position: absolute; left: 58px; top: 368px; width: 818px; z-index: 20;
      background: rgba(255,255,255,0.96); border: 2.5px solid {pri}; border-radius: 30px;
      padding: 20px 24px; box-shadow: 0 16px 36px rgba(20,30,45,0.14);
    }}
    .usp-hdr {{
      display: inline-block; background: {pri}; color: #FFFFFF;
      font-size: 23px; padding: 7px 20px; border-radius: 999px;
      text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 10px;
    }}
    .usp-row {{
      display: flex; align-items: center; gap: 14px; font-size: 28px; color: #1E2430;
      padding: 6px 0; line-height: 1.25;
    }}
    .usp-num {{
      width: 36px; height: 36px; border-radius: 50%; background: {pri_soft}; color: {pri}; border: 2px solid {pri};
      display: inline-flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;
    }}

    /* CUT 7 DIRECT 100% REAL PRODUCT CUTOUT ON SUNLIT PODIUM (0% zoompan, 0% purple, 100% razor-sharp label!) */
    .c7-prod-stage {{
      position: absolute; left: 58px; top: 736px; width: 818px; height: 610px; z-index: 19;
      display: flex; flex-direction: column; align-items: center; justify-content: flex-end; pointer-events: none;
    }}
    .c7-disc {{
      width: 480px; height: 54px; border-radius: 50%;
      background: radial-gradient(ellipse at center, #FFFFFF 0%, {pri_soft} 72%, rgba(255,255,255,0) 100%);
      border: 2px solid #FFFFFF; box-shadow: 0 14px 28px rgba(20,30,45,0.18); margin-top: -22px;
    }}
    .c7-prod-stage img {{
      position: relative; z-index: 2; {c7_prod_style} object-fit: contain;
      filter: drop-shadow(0 22px 30px rgba(20,30,45,0.26));
    }}

    /* CUT 8 BOTANICAL CRYSTAL HEADER BANNER */
    .macro-banner {{
      position: absolute; left: 58px; top: 374px; width: 818px; z-index: 20;
      background: rgba(255,255,255,0.95); border: 2.5px solid {pri};
      border-radius: 30px; padding: 20px 28px; box-shadow: 0 16px 36px rgba(20,30,45,0.14);
    }}
    .macro-banner .mb-k {{ font-size: 21px; color: {pri}; letter-spacing: 0.05em; margin-bottom: 4px; }}
    .macro-banner .mb-h {{ font-family: "FrauncesVN", serif; font-size: 54px; color: {pri_dark}; line-height: 1.08; }}

    /* CUT 10: AIRY CRYSTAL-CLEAR DAYLIGHT SPLIT END-CARD (NO dark background! 100% Safe Zone!) */
    .end-stage {{ position: absolute; inset: 0; background: {pri_soft}; z-index: 23; }}
    .end-vid-direct {{
      position: absolute; left: 58px; top: 364px; width: 822px; height: 530px; z-index: 25;
      border-radius: 34px; object-fit: cover; object-position: center 20%; display: block;
      border: 5px solid #FFFFFF; box-shadow: 0 16px 36px rgba(20,30,45,0.14);
    }}
    .end-dock {{
      position: absolute; left: 58px; top: 914px; width: 822px; height: 614px;
      background: #FFFFFF; border: 3px solid {pri}; border-radius: 34px; padding: 26px 28px;
      box-shadow: 0 18px 40px rgba(20,30,45,0.14);
      display: flex; flex-direction: column; justify-content: space-between;
    }}
    .end-dock-top {{ display: flex; align-items: center; gap: 24px; height: 390px; }}
    .end-prod-wrap {{ width: 280px; height: 375px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; background: {pri_soft}; border-radius: 26px; padding: 12px; }}
    .end-prod-wrap img {{ max-width: 256px; max-height: 350px; object-fit: contain; filter: drop-shadow(0 14px 22px rgba(20,30,45,0.22)); }}
    .end-info {{ flex: 1; }}
    .end-cat {{ display: inline-block; background: {pri_soft}; color: {pri}; font-size: 19px; padding: 6px 16px; border-radius: 999px; margin-bottom: 10px; }}
    .end-name {{ font-family: "FrauncesVN", serif; font-size: 54px; color: {pri_dark}; line-height: 1.05; margin-bottom: 10px; }}
    .end-sub {{ font-size: 24px; color: #334155; font-family: "BeVNBold"; line-height: 1.32; }}
    .end-cta {{
      background: {pri}; color: #FFFFFF; border-radius: 999px; padding: 18px 24px;
      text-align: center; font-size: 26px; letter-spacing: 0.02em;
      box-shadow: 0 10px 24px rgba(20,30,45,0.18);
    }}
    .end-legal {{ text-align: center; font-family: "BeVNSemi"; font-size: 19px; color: #64748B; margin-top: 6px; }}

    /* AIRY FROSTED PEARL-WHITE DAYLIGHT SUBTITLES (X=58..880 <= 884px, Y=1388..1526 <= 1545px!) */
    .cap-box {{
      position: absolute; left: 58px; bottom: 394px; width: 822px; z-index: 26;
      display: flex; justify-content: center; pointer-events: none;
    }}
    .cap-txt {{
      background: rgba(255, 255, 255, 0.96); border: 2.5px solid {pri};
      border-radius: 22px; padding: 13px 24px; color: #1E2430;
      font-family: "BeVNExtra", sans-serif; font-size: 34px; line-height: 1.25;
      text-align: center; box-shadow: 0 12px 28px rgba(15,23,42,0.18);
    }}
    .cap-kw {{ font-family: "PlayfairIt", serif; font-size: 38px; color: {pri}; }}
  </style>

  <div id="root" data-composition-id="scene-main" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur:.2f}">
{chr(10).join(vid_tags)}
    <div class="prog-track"><div id="prog-bar" class="prog-fill"></div></div>
    <div class="brand-pill"><img src="assets/images/ht_logo.png" alt="HT"/><div class="bp-t">HẰNG THU PHARMA</div></div>
    <div id="seal-spin" class="seal-badge"><span>CAM KẾT</span><b>100%</b><span>CHÍNH HÃNG</span></div>

    <div id="hook-box" class="clip hook-lower" data-start="0.08" data-duration="{hook_end:.2f}" data-track-index="20">
      <div id="hook-in">
        <div class="hook-kicker">{cfg['hook_kicker']}</div>
        <div class="hook-title">{cfg['hook_hero']}</div>
      </div>
    </div>

    <div id="card-s1" class="clip" data-start="{c3_st + 0.08:.2f}" data-duration="{max(0.6, c3_dur - 0.14):.2f}" data-track-index="21">
      <div id="card-s1-in" class="usp-card">
        <div class="usp-hdr">{cfg['slide1_hdr']}</div>
{rows_s1}
      </div>
    </div>

    <div id="pill-s2" class="clip" data-start="{choice_st:.2f}" data-duration="{choice_dur:.2f}" data-track-index="22">
      <div id="pill-s2-in" class="choice-pill">
        <img src="assets/images/{cfg['cutout']}" alt="SP"/>
        <div class="cp-txt">{cfg['slide2_pill']}</div>
      </div>
    </div>

    <!-- Cut 7: 100% Real Product Cutout Floating Smoothly Over Sunlit Marble Podium + Official Ingredient Card -->
    <div id="c7-prod" class="clip" data-start="{c7_st:.2f}" data-duration="{c7_dur:.2f}" data-track-index="23">
      <div id="c7-prod-in" class="c7-prod-stage">
        <img id="c7-hero-img" src="assets/images/{cfg['cutout']}" alt="HeroProduct"/>
        <div class="c7-disc"></div>
      </div>
      <div id="card-s2-in" class="usp-card">
        <div class="usp-hdr">{cfg['pack_kicker']}</div>
{rows_s2}
      </div>
    </div>

    <div id="ban-s3" class="clip" data-start="{c8_st + 0.08:.2f}" data-duration="{max(0.6, c8_dur - 0.14):.2f}" data-track-index="24">
      <div id="ban-s3-in" class="macro-banner">
        <div class="mb-k">{cfg['pack_kicker']}</div>
        <div class="mb-h">{cfg['pack_hero']}</div>
      </div>
    </div>

    <div id="end-card" class="clip end-stage" data-start="{c10_st:.2f}" data-duration="{c10_dur:.2f}" data-track-index="25">
      <div id="end-in" class="end-dock">
        <div>
          <div class="end-dock-top">
            <div class="end-prod-wrap"><img src="assets/images/{cfg['cutout']}" alt="Product"/></div>
            <div class="end-info">
              <div class="end-cat">{cfg['end_cat']}</div>
              <div class="end-name">{cfg['end_name']}</div>
              <div class="end-sub">{cfg['end_sub']}</div>
            </div>
          </div>
        </div>
        <div>
          <div id="cta-pulse" class="end-cta">{cfg['cta_txt']}</div>
          <div class="end-legal">{cfg['legal_txt']}</div>
        </div>
      </div>
    </div>
    <video data-color-grading="{COLOR_GRADE_AIRY}" id="vid-10" class="clip end-vid-direct" src="assets/videos/C10.mp4" data-start="{c10_st:.2f}" data-duration="{c10_dur:.2f}" data-media-start="0.10" data-hf-media-start-basis="local" data-track-index="26" muted playsinline></video>

{chr(10).join(cap_divs)}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#prog-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {total_dur:.2f}, ease: "none" }}, 0);
    tl.to("#seal-spin", {{ rotation: 360, duration: {total_dur:.2f}, ease: "none" }}, 0);

    tl.fromTo("#hook-in", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power2.out" }}, 0.10);
    tl.to("#hook-in", {{ opacity: 0, duration: 0.18 }}, {max(0.5, hook_end - 0.16):.2f});

    tl.fromTo("#card-s1-in", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power2.out" }}, {c3_st + 0.08:.2f});
    tl.to("#card-s1-in", {{ opacity: 0, duration: 0.16 }}, {c3_st + c3_dur - 0.18:.2f});

    tl.fromTo("#pill-s2-in", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.24, ease: "power2.out" }}, {choice_st:.2f});
    tl.to("#pill-s2-in", {{ opacity: 0, duration: 0.18 }}, {choice_st + choice_dur - 0.20:.2f});

    tl.fromTo("#c7-prod-in", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power2.out" }}, {c7_st:.2f});
    tl.fromTo("#c7-hero-img", {{ y: 8, scale: 0.96 }}, {{ y: -6, scale: 1.02, duration: {c7_dur:.2f}, ease: "sine.inOut" }}, {c7_st:.2f});
    tl.fromTo("#card-s2-in", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power2.out" }}, {c7_st + 0.08:.2f});

    tl.fromTo("#ban-s3-in", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power2.out" }}, {c8_st + 0.08:.2f});
    tl.to("#ban-s3-in", {{ opacity: 0, duration: 0.16 }}, {c8_st + c8_dur - 0.18:.2f});

    tl.fromTo("#end-in", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.26, ease: "power2.out" }}, {c10_st:.2f});
    tl.fromTo("#cta-pulse", {{ scale: 0.97 }}, {{ scale: 1.02, duration: 0.55, yoyo: true, repeat: 6, ease: "sine.inOut" }}, {c10_st + 0.25:.2f});
{chr(10).join(cap_js)}
    window.__timelines = window.__timelines || {{}};
    window.__timelines["scene-main"] = tl;
  </script>
</template>
"""
    (comp_dir / "scene-main.html").write_text(scene_html, encoding="utf-8")

    vo_clips = "\n".join(
        f'    <audio id="vo-{vi+1}" class="clip" src="assets/audio/{s["id"]}.wav" data-start="{float(s["start_s"]):.2f}" data-duration="{float(s["duration_s"]):.2f}" data-volume="1.34" data-fade-in="0.03" data-fade-out="0.05" data-track-index="{4 if vi % 2 == 0 else 5}" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        for vi, s in enumerate(segs)
    )
    sfx_tags = []
    if (aud_dir / "sfx_whoosh_soft.mp3").exists():
        for wi, (_, _, wst, _) in enumerate(cuts_10[1:], start=2):
            sfx_tags.append(f'    <audio id="sfx-w{wi}" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{max(0.0, wst - 0.08):.2f}" data-duration="0.42" data-volume="0.12" data-fade-out="0.12" data-track-index="8"></audio>')
    if (aud_dir / "sfx_pop_clean.mp3").exists():
        for pi, pst in enumerate([c3_st + 0.08, choice_st, c7_st + 0.08], start=1):
            sfx_tags.append(f'    <audio id="sfx-p{pi}" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{pst:.2f}" data-duration="0.42" data-volume="0.16" data-track-index="9"></audio>')
    if (aud_dir / "sfx_chime_warm.mp3").exists():
        sfx_tags.append(f'    <audio id="sfx-end" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="{c10_st + 0.14:.2f}" data-duration="1.60" data-volume="0.38" data-track-index="10"></audio>')

    # Pure solid background (#F8FAFC) on html/body/#root enables HyperFrames GPU fast-streaming capture!
    index_html = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
  <title>{cfg['final_mp4']}</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body, #root {{ width: 1080px; height: 1920px; overflow: hidden; background: #F8FAFC; position: relative; }}
    .scene-host {{ position: absolute; inset: 0; width: 1080px; height: 1920px; z-index: 2; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur:.2f}" data-fps="24">
    <div id="scene-main" class="scene-host" data-composition-id="scene-main" data-composition-src="compositions/scene-main.html" data-start="0" data-duration="{total_dur:.2f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
{vo_clips}
    <audio id="bgm-1" class="clip" src="assets/audio/bgm_1.mp3" data-start="0" data-duration="{mid_t:.2f}" data-media-start="2.0" data-volume="0.24" data-fade-in="0.35" data-fade-out="0.55" data-loop="true" data-track-index="6"></audio>
    <audio id="bgm-2" class="clip" src="assets/audio/bgm_2.mp3" data-start="{max(0.0, mid_t - 0.25):.2f}" data-duration="{round(total_dur - mid_t + 0.25, 2):.2f}" data-media-start="4.0" data-volume="0.26" data-fade-in="0.50" data-fade-out="0.80" data-loop="true" data-track-index="7"></audio>
{chr(10).join(sfx_tags)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    window.__timelines["main"] = gsap.timeline({{ paused: true }});
  </script>
</body>
</html>
"""
    (hf_dir / "index.html").write_text(index_html, encoding="utf-8")

    out_dir = work_dir / "08_Render_Master_V6"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / cfg["final_mp4"]

    if "--qa-only" not in sys.argv or not (out_mp4.exists() and out_mp4.stat().st_size > 12_000_000):
        subprocess.run(
            ["npx.cmd", "hyperframes", "render", "--output", str(out_mp4), "--quality", "delivery"],
            cwd=str(hf_dir),
            check=True,
        )
        for dst_folder in (K6_DAY25_DIR, CLOUD_DAY25_VID, LOCAL_DAY25_DIR):
            dst_folder.mkdir(parents=True, exist_ok=True)
            shutil.copy2(out_mp4, dst_folder / cfg["final_mp4"])
        print(f"[V6 CRYSTAL-CLEAR DELIVERED TO K6] {cfg['final_mp4']} ({round(out_mp4.stat().st_size / 1048576, 1)} MB)", flush=True)

    return out_mp4, cuts_10, total_dur


def build_all_12_v6_configs():
    v6_sc_map = {s["vkey"]: s for s in json.loads((V6_ROOT / "v6_scripts_spec.json").read_text(encoding="utf-8"))}
    cfgs = []

    for sl in SLOTS_261125:
        idx = sl["idx"]
        vkey = sl["vkey"]
        sc = v6_sc_map[vkey]
        cfgs.append({
            "label": sl["code"],
            "vkey": vkey,
            "final_mp4": sl["final_mp4"],
            "cutout": "SP_HTPM_FULL_8SKU_SHELF.png" if idx == 10 else sl["cutout"],
            "pri": sl["pri"],
            "pri_dark": sl["pri_dark"],
            "pri_soft": sl["pri_soft"],
            "hook_kicker": sc["hook_kicker"],
            "hook_hero": sc["hook_hero"],
            "slide1_hdr": sc["slide1_hdr"],
            "slide1_rows": sc["slide1_rows"],
            "slide2_pill": sc["slide2_pill"],
            "pack_kicker": sc["pack_kicker"],
            "pack_hero": sc["pack_hero"],
            "slide3_pills": sc["slide3_pills"],
            "end_cat": sl["end_cat"],
            "end_name": sl["end_name"],
            "end_sub": sl["end_sub"],
            "cta_txt": sl["cta_txt"].upper(),
            "legal_txt": sl["legal_txt"],
            "caps_pair": sc["caps"],
        })

    sc_nlh = v6_sc_map["flagship_ngoc_long_hoan"]
    cfgs.append({
        "label": "NLH_SP",
        "vkey": "flagship_ngoc_long_hoan",
        "final_mp4": "261125 HTPM Ngọc Long Hoàn chị Hằng chia sẻ bí quyết chăm sức khỏe chồng final.mp4",
        "cutout": "SP_NGOC_LONG_HOAN_CUTOUT.png",
        "pri": "#9E2A1C",
        "pri_dark": "#3A0D07",
        "pri_soft": "#FDF1EC",
        "hook_kicker": sc_nlh["hook_kicker"],
        "hook_hero": sc_nlh["hook_hero"],
        "slide1_hdr": sc_nlh["slide1_hdr"],
        "slide1_rows": sc_nlh["slide1_rows"],
        "slide2_pill": sc_nlh["slide2_pill"],
        "pack_kicker": sc_nlh["pack_kicker"],
        "pack_hero": sc_nlh["pack_hero"],
        "slide3_pills": sc_nlh["slide3_pills"],
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE",
        "end_name": "Ngọc Long Hoàn",
        "end_sub": "BA KÍCH TÍM • NHUNG HƯƠU • ĐÔNG TRÙNG",
        "cta_txt": "NHẮN NGAY “NGỌC LONG HOÀN” · TƯ VẤN BẢO MẬT",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "caps_pair": sc_nlh["caps"],
    })

    sc_dk = v6_sc_map["flagship_dieu_kinh_ht"]
    cfgs.append({
        "label": "DK_SP",
        "vkey": "flagship_dieu_kinh_ht",
        "final_mp4": "261125 HTPM Điều Kinh HT bí quyết dưỡng khí huyết rạng rỡ của chị Hằng final.mp4",
        "cutout": "SP_DIEU_KINH_HT_CUTOUT.png",
        "pri": "#8B1E72",
        "pri_dark": "#3B0830",
        "pri_soft": "#FBE8F7",
        "hook_kicker": sc_dk["hook_kicker"],
        "hook_hero": sc_dk["hook_hero"],
        "slide1_hdr": sc_dk["slide1_hdr"],
        "slide1_rows": sc_dk["slide1_rows"],
        "slide2_pill": sc_dk["slide2_pill"],
        "pack_kicker": sc_dk["pack_kicker"],
        "pack_hero": sc_dk["pack_hero"],
        "slide3_pills": sc_dk["slide3_pills"],
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE",
        "end_name": "Điều Kinh HT",
        "end_sub": "ĐƯƠNG QUY • HƯƠNG PHỤ • HỒNG HOA",
        "cta_txt": "NHẮN NGAY “ĐIỀU KINH HT” · TƯ VẤN RIÊNG",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "caps_pair": sc_dk["caps"],
    })
    return cfgs


def main():
    aco_list, tvc_list = list_fresh_bgms()
    cfgs = build_all_12_v6_configs()
    if "--test-nlh" in sys.argv:
        cfgs = [cfgs[10]]  # Test Flagship Ngọc Long Hoàn first so we verify the exact shot the user screenshotted!

    qa_rows = []
    for idx, cfg in enumerate(cfgs):
        b1 = aco_list[idx % len(aco_list)]
        b2 = tvc_list[idx % len(tvc_list)]
        mp4_p, cuts_10, tdur = build_and_render_v6_video(cfg, b1, b2)
        row_tiles = []
        for c_num, tok, c_st, c_dur in cuts_10:
            ts = min(tdur - 0.30, c_st + c_dur * 0.52)
            fp = mp4_p.parent / f"qa10_{c_num:02d}.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(mp4_p), "-frames:v", "1", "-q:v", "2", str(fp)], check=True)
            im = Image.open(fp).convert("RGB")
            d = ImageDraw.Draw(im)
            d.line([(0, 248), (1080, 248)], fill=(255, 60, 60), width=4)
            d.line([(0, 1548), (1080, 1548)], fill=(255, 60, 60), width=4)
            d.rectangle([(886, 860), (1080, 1548)], outline=(255, 60, 60), width=4)
            row_tiles.append((f"{cfg['label']}_C{c_num:02d}", im))
        qa_rows.append(row_tiles)

    tw, th = 220, 390
    sheet = Image.new("RGB", (tw * 10, th * len(qa_rows)), (240, 245, 250))
    sd = ImageDraw.Draw(sheet)
    for r_idx, r_tiles in enumerate(qa_rows):
        for c_idx, (lbl, im) in enumerate(r_tiles):
            sheet.paste(im.resize((tw - 6, th - 22), Image.Resampling.LANCZOS), (c_idx * tw + 3, r_idx * th + 19))
            sd.text((c_idx * tw + 5, r_idx * th + 2), lbl, fill=(20, 40, 70))

    qa_out = V6_ROOT / ("v6_test_nlh_qa.jpg" if "--test-nlh" in sys.argv else "v6_all_12_crystal_videos_120_cuts_qa.jpg")
    sheet.save(qa_out, quality=92)
    shutil.copy2(qa_out, ARTIFACT_DIR / ("htpm_v6_test_nlh_qa.jpg" if "--test-nlh" in sys.argv else "htpm_261125_12_videos_120cuts_v6_crystal_qa.jpg"))
    print(f"=== V6 CRYSTAL-CLEAR RENDER COMPLETE ({len(qa_rows)} VIDEOS) -> {qa_out} ===", flush=True)


if __name__ == "__main__":
    main()
