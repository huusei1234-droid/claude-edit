# -*- coding: utf-8 -*-
"""
Base ChatGPT Asset Definitions (`CHAR_SPECS_BASE` & `SET_SPECS_BASE`) for the 18 confirmed episodes (`r01..r05`, `r07..r13`, `r15..r20`).
Every new character has:
  (ep, key, drive_filename, branch, display_name_age, genealogy_relation, prompt_desc)
Every bespoke 9:16 set has:
  (ep, skey, sbase, prompt_desc)
"""

SPLIT_PROMPT_TPL = (
    "Character reference sheet split into two side-by-side panels separated by a clean thin white vertical line "
    "(left panel: close-up portrait from chest up looking slightly toward camera; "
    "right panel: full-body standing shot head-to-toe in a realistic neutral Vietnamese home or street setting). "
    "{desc} "
    "Photorealistic live-action Vietnamese TV family drama actor, natural skin pores, warm cinematic lighting, 8k, ZERO text, ZERO labels, ZERO watermarks."
)

SET_PROMPT_TPL = (
    "Vertical 9:16 photorealistic live-action Vietnamese television drama empty film set establishing background (NO main foreground actors blocking center, "
    "unless natural distant background diners/guests are specified). {desc} "
    "Natural cinematic lighting, realistic textures, 8k, ZERO text, ZERO signs with gibberish letters, ZERO watermarks."
)

# Existing canonical K4 sheets in `CHARACTER/` reused strictly in their exact K4 roles & ages:
EXISTING_K4_REUSE = [
    ("quan_somi", "G04_05c - Quân (Con trai Bác Trọng - Cháu đích tôn cụ Cúc) [Sơ mi trắng quần âu].png", None),
    ("thanh_ck",  "G01_09 - Thành (Chồng Linh - Em rể Tuấn - Con rể ông Tấn).png", None),
    ("linh_vo",   "G01_08 - Linh (Em gái ruột Tuấn - Em chồng Thảo - Vợ Thành).png", None),
    ("hieu_vest", "G05_02b - Hiếu (Con trai trưởng bà Mận - Giám đốc công ty) [Vest đen lễ khánh thành].png", None),
    ("tu_ck",     "G03_02 - Tú (Con trai cô Lan - Em họ nội Tuấn - Anh ruột Hà - Chồng Lam).png", None),
    ("lam_vo",    "G03_03 - Lam (Vợ Tú - Con dâu cô Lan - Em dâu họ Tuấn).png", None),
    ("khoa_bs",   "G08_03 - Khoa (Bác sĩ Trưởng khoa hiếu thảo - Con trai thứ ông Lộc - Chồng Châu) [Áo blouse trắng bác sĩ].png", None),
]

CHAR_SPECS_BASE = [
    # --- R01 (G10: Gia đình Kiên đi XKLĐ 8 năm xây nhà 6 tỷ & nhà ngoại nhận vơ) ---
    ("r01", "kien", "G10_01 - Kiên (Chồng đi xuất khẩu lao động tám năm xây nhà sáu tỷ - Con ông Hòa & bà Duyên) [Vest xanh đen tân gia].png",
     "G10", "Kiên (32t)", "Con trai ông Hòa & bà Duyên; chồng Thư; 8 năm XKLĐ tự mua nhà 6 tỷ [Vest xanh đen]",
     "Subject: Distinct 32-year-old upright hardworking Vietnamese man, tanned masculine jawline, neat short black hair, honest determined eyes, NO glasses, clean-shaven. Outfit: sharp dark navy-blue formal suit jacket over a crisp white open-collar dress shirt (no tie), tailored dark trousers, black leather dress shoes."),
    ("r01", "onghoa", "G10_02 - Ông Hòa (Bố quê hiền lành bán vườn giúp Kiên mua nhà - Chồng bà Duyên).png",
     "G10", "Ông Hòa (64t)", "Bố ruột ở quê của Kiên; chồng bà Duyên (Có râu cằm bạc ngắn riêng biệt, bán vườn giúp con)",
     "Subject: Distinct 64-year-old humble Vietnamese countryside father, sun-weathered square face with a neat short silver-grey goatee beard and grey-flecked mustache, salt-and-pepper hair parted on the side, NO glasses, kind emotional eyes, weathered calloused hands. Outfit: modest dark earth-brown long-sleeve buttoned cotton shirt, loose charcoal-grey cloth trousers, simple dark sandals."),
    ("r01", "baduyen", "G10_03 - Bà Duyên (Mẹ quê tần tảo của Kiên - Vợ ông Hòa) [Áo bà ba nâu].png",
     "G10", "Bà Duyên (61t)", "Mẹ ruột ở quê của Kiên; vợ ông Hòa [Áo bà ba nâu giản dị]",
     "Subject: Distinct 61-year-old gentle Vietnamese rural mother, warm round sun-tanned face with soft wrinkles, greying hair tied in a neat low bun at the nape, gentle humble expression. Outfit: traditional modest brown cotton long-sleeve button-up shirt ('áo bà ba nâu'), black loose trousers, simple flat slippers."),
    ("r01", "batuyet", "G10_04 - Bà Tuyết (Mẹ vợ hách dịch nhận vơ nhà tân gia của Kiên - Vợ ông Sỹ - Mẹ Thư) [Áo dài nhung đỏ đô].png",
     "G10", "Bà Tuyết (54t)", "Vợ ông Sỹ; mẹ ruột Thư; mẹ vợ hách dịch nhận vơ nhà 6 tỷ của Kiên [Áo dài nhung đỏ đô]",
     "Subject: Distinct 54-year-old status-obsessed city Vietnamese mother-in-law, sharp haughty facial features, voluminous shoulder-length curled chestnut-brown hair, wearing an ornate gold statement necklace and gold earrings. Outfit: luxurious deep crimson-burgundy velvet Vietnamese traditional mandarin-collar tunic ('áo dài nhung đỏ đô') with dark trousers and low heels."),
    ("r01", "ongsy", "G10_05 - Ông Sỹ (Bố vợ sĩ diện khoe khoang của Kiên - Chồng bà Tuyết - Bố Thư) [Vest đen kẻ].png",
     "G10", "Ông Sỹ (57t)", "Chồng bà Tuyết; bố ruột Thư; bố vợ sĩ diện của Kiên (Mặt góc cạnh lông mày rậm, không kính không râu)",
     "Subject: Distinct 57-year-old arrogant urban Vietnamese father-in-law, angular narrow face, thick dark eyebrows, sleek slicked-back black hair with silver temples, clean-shaven, NO glasses, boastful proud expression. Outfit: dark charcoal pinstripe suit jacket over a white collared shirt, dark trousers, black leather shoes."),
    ("r01", "thu_vo", "G10_06 - Thư (Vợ sĩ diện của Kiên - Con gái ông Sỹ & bà Tuyết) [Đầm dạ tiệc trắng trễ vai].png",
     "G10", "Thư (27t)", "Con gái ông Sỹ & bà Tuyết; vợ sĩ diện khoe nhà của ngoại của Kiên [Đầm trắng trễ vai]",
     "Subject: Distinct 27-year-old vain city Vietnamese young wife, long sleek dark wavy hair, polished glamorous makeup, pearl stud earrings. Outfit: elegant fitted off-shoulder white midi party dress, white high-heel sandals."),

    # --- R02 (G11: Gia đình Nam – Phương quản lý dự án online 40 triệu & Mẹ chồng Bà Liên – Chị chồng Bích) ---
    ("r02", "nam_ck", "G11_01 - Nam (Chồng công sở hiểu chuyện bảo vệ vợ - Chồng Phương - Em trai Bích) [Sơ mi trắng].png",
     "G11", "Nam (30t)", "Con trai bà Liên; em trai Bích; chồng hiểu lý lẽ của Phương [Sơ mi trắng quần âu]",
     "Subject: Distinct 30-year-old handsome upright Vietnamese office-worker husband, clean-cut side-parted black hair, warm intelligent eyes, NO glasses, clean-shaven. Outfit: crisp white long-sleeve dress shirt tucked into black tailored trousers with a leather belt, wristwatch, black dress shoes."),
    ("r02", "phuong_vo", "G11_02 - Phương (Vợ hiền làm quản lý dự án online bốn mươi triệu - Vợ Nam) [Sơ mi kem chân váy đen].png",
     "G11", "Phương (28t)", "Vợ đảm đang kiếm 40 triệu/tháng của Nam; con dâu bà Liên [Sơ mi kem chân váy]",
     "Subject: Distinct 28-year-old gentle intelligent Vietnamese young wife, soft oval face, dark hair tied neatly in a low ponytail with light wisps, natural makeup, filial sincere expression. Outfit: modest cream-ivory chiffon long-sleeve blouse tucked into a knee-length black skirt, indoor slippers."),
    ("r02", "balien", "G11_03 - Bà Liên (Mẹ chồng khắt khe đòi giữ tiền con dâu - Mẹ Bích & Nam) [Áo lụa tím than].png",
     "G11", "Bà Liên (56t)", "Mẹ ruột Bích & Nam; mẹ chồng khắt khe của Phương [Áo lụa tím than]",
     "Subject: Distinct 56-year-old strict Vietnamese city mother-in-law, high cheekbones, stern narrow eyes, dark hair pulled tightly into a neat bun, thin silver chain necklace. Outfit: dark plum-purple silk traditional middle-aged blouse with subtle brocade pattern and black trousers."),
    ("r02", "bich_cc", "G11_04 - Bích (Chị chồng đanh đá hay sang lục lọi vay tiền em dâu - Chị gái Nam) [Đầm đỏ hoa nhí].png",
     "G11", "Bích (34t)", "Con gái lớn bà Liên; chị gái Nam; chị chồng đanh đá của Phương [Đầm đỏ hoa nhí]",
     "Subject: Distinct 34-year-old sharp-tongued Vietnamese sister-in-law, wavy medium-brown shoulder-length hair, judgmental nosy expression. Outfit: fitted red floral-print short-sleeve V-neck midi dress, beige low heels."),

    # --- R03 (G12: Gia đình Ông Chính xử công minh 10 mâm cỗ giỗ cho con dâu Diệp) ---
    ("r03", "ongchinh", "G12_01 - Ông Chính (Bố chồng nghiêm minh thấu tình đạt lý - Chồng bà Lệ - Bố chồng Diệp) [Sơ mi xám than].png",
     "G12", "Ông Chính (59t)", "Chồng bà Lệ; bố chồng công minh bảo vệ con dâu Diệp ngày giỗ họ [Sơ mi xám than]",
     "Subject: Distinct 59-year-old dignified righteous Vietnamese patriarch father-in-law, thick salt-and-pepper hair neatly parted 7/3, straight nose, calm authoritative eyes, NO glasses, clean-shaven. Outfit: dark charcoal-grey long-sleeve collared dress shirt tucked into black formal trousers with leather belt, black leather shoes."),
    ("r03", "bale_mc", "G12_02 - Bà Lệ (Mẹ chồng sĩ diện nhận vơ mười mâm cỗ giỗ - Vợ ông Chính) [Đầm nhung xanh lục bảo].png",
     "G12", "Bà Lệ (55t)", "Vợ ông Chính; mẹ chồng sĩ diện nhận vơ công nấu cỗ của con dâu Diệp [Nhung xanh lục bảo]",
     "Subject: Distinct 55-year-old vain wealthy Vietnamese mother-in-law, classic bouffant curled jet-black short hair, double-strand white pearl necklace and pearl stud earrings, proud expression. Outfit: luxurious emerald-green long-sleeve velvet midi dress, dark low heels."),
    ("r03", "diep_dau", "G12_03 - Diệp (Con dâu hiền một mình nấu mười mâm cỗ bỏng tay - Con dâu ông Chính) [Áo xanh tạp dề nâu].png",
     "G12", "Diệp (27t)", "Con dâu hiền thảo chăm chỉ của ông Chính & bà Lệ [Áo xanh đeo tạp dề nâu]",
     "Subject: Distinct 27-year-old gentle hardworking Vietnamese daughter-in-law, hair tied up neatly in a bun for cooking, honest kind face, slightly reddened hands from kitchen work. Outfit: modest teal-green long-sleeve cotton top with a brown kitchen apron tied over dark trousers, simple house slippers."),
    ("r03", "thimhoa", "G12_04 - Thím Hoa (Thím họ xu nịnh hùa theo bà Lệ bắt nạt cháu dâu) [Áo gấm đỏ mận].png",
     "G12", "Thím Hoa (51t)", "Thím họ khéo nịnh hùa theo bà Lệ trong ngày giỗ tổ [Áo gấm đỏ mận]",
     "Subject: Distinct 51-year-old gossipy flattering Vietnamese aunt, hair pinned in a sleek updo, small silver brooch on chest, sly expressive face. Outfit: traditional plum-burgundy brocade mandarin-collar blouse ('áo bà ba gấm đỏ mận') with black silk pants."),
    ("r03", "bactruong", "G12_05 - Bác Trưởng (Bác trưởng họ cao niên công tâm dự lễ giỗ) [Vest nâu sẫm].png",
     "G12", "Bác Trưởng (67t)", "Bậc trưởng tộc cao niên đáng kính trong họ của ông Chính [Vest nâu sẫm]",
     "Subject: Distinct 67-year-old respected elderly Vietnamese clan elder, full head of neat silver-white hair, warm wise wrinkled face, NO glasses, benevolent dignified posture. Outfit: classic dark espresso-brown formal jacket over a cream collared shirt, dark trousers, leather shoes."),

    # --- R04 (G13: Bà Tơ mang làn trứng quê bị con dâu Yến & mẹ vợ Bà Quế gài bẫy nhẫn kim cương) ---
    ("r04", "bato_me", "G13_01 - Bà Tơ (Mẹ quê hiền lành mang làn trứng gà thăm con - Mẹ ruột Hoàng) [Áo nâu xách làn đỏ].png",
     "G13", "Bà Tơ (63t)", "Mẹ ruột ở quê của Hoàng; mang làn trứng gà lên thăm bị vu lấy nhẫn [Áo nâu]",
     "Subject: Distinct 63-year-old petite humble Vietnamese countryside mother, silver-streaked hair parted in the middle and tied back low, gentle sorrowful eyes, weathered skin. Outfit: simple dark brown buttoned cotton grandma shirt, black loose pants, flat sandals, holding a red plastic woven market basket."),
    ("r04", "hoang_ck", "G13_02 - Hoàng (Con trai bản lĩnh bảo vệ danh dự mẹ quê - Chồng Yến) [Vest xanh navy cặp da].png",
     "G13", "Hoàng (31t)", "Con trai bà Tơ; chồng của Yến; con rể bà Quế [Vest xanh navy công sở]",
     "Subject: Distinct 31-year-old sharp composed Vietnamese corporate husband, modern short neat black haircut, strong eyebrows, NO glasses, clean-shaven. Outfit: tailored dark navy business suit over a crisp white open-collar dress shirt, dark brown leather dress shoes, holding a brown leather briefcase."),
    ("r04", "yen_vo", "G13_03 - Yến (Vợ đanh đá dàn cảnh nhẫn kim cương đuổi mẹ chồng - Vợ Hoàng) [Đầm lụa đỏ sát nách].png",
     "G13", "Yến (27t)", "Vợ đanh đá của Hoàng; con gái bà Quế [Đầm lụa đỏ đô sát nách]",
     "Subject: Distinct 27-year-old sharp-featured spoiled city Vietnamese wife, high bun hairstyle with wispy bangs, drop crystal earrings, haughty expression. Outfit: chic sleeveless ruby-red satin midi dress, beige heels."),
    ("r04", "baque_mv", "G13_04 - Bà Quế (Mẹ vợ làm chứng giả bênh con gái bắt nạt bà Tơ - Mẹ ruột Yến) [Áo gấm tím].png",
     "G13", "Bà Quế (54t)", "Mẹ ruột Yến; mẹ vợ đanh đá của Hoàng [Áo gấm tím chuỗi ngọc]",
     "Subject: Distinct 54-year-old domineering urban Vietnamese mother-in-law, short permed wavy dark hair, pearl necklace, calculating stern gaze. Outfit: royal purple floral-jacquard collared blouse with black tailored trousers."),

    # --- R05 (G14: Bà Nhàn đau xương khớp ở quê & con trai Tùng ly hôn người vợ ích kỷ Vân) ---
    ("r05", "banhan_me", "G14_01 - Bà Nhàn (Mẹ quê đau xương khớp xót con - Mẹ ruột Tùng) [Áo vải nâu be].png",
     "G14", "Bà Nhàn (62t)", "Mẹ ruột gầy yếu ở quê của Tùng; từ chối nhận 5 triệu vì sợ con dâu mắng [Áo nâu be]",
     "Subject: Distinct 62-year-old frail kind-hearted Vietnamese rural mother, thin face, greying hair tied neatly at the back, compassionate worried eyes. Outfit: faded taupe-brown cotton long-sleeve button shirt, loose black cloth trousers, rubber sandals."),
    ("r05", "tung_ck", "G14_02 - Tùng (Chồng hiếu thảo quyết bảo vệ mẹ ruột - Con bà Nhàn - Chồng Vân) [Sơ mi xanh nhạt].png",
     "G14", "Tùng (31t)", "Con trai hiếu thảo của bà Nhàn; chồng Vân [Sơ mi xanh da trời nhạt]",
     "Subject: Distinct 31-year-old earnest hardworking Vietnamese man, natural short black hair, sincere emotional eyes, NO glasses, clean-shaven. Outfit: light sky-blue long-sleeve dress shirt with sleeves rolled to forearms, dark black trousers with leather belt, black shoes."),
    ("r05", "van_vo", "G14_03 - Vân (Vợ ích kỷ biếu mẹ ngoại mười triệu nhưng cấm biếu mẹ chồng - Vợ Tùng) [Áo đỏ đô chân váy đen].png",
     "G14", "Vân (28t)", "Vợ ích kỷ giữ hết tiền lương của Tùng [Áo cổ tim đỏ đô chân váy đen]",
     "Subject: Distinct 28-year-old Materialistic sharp-tongued Vietnamese wife, straight shoulder-length chestnut hair, bold red lipstick, pearl earrings, bossy expression. Outfit: fitted burgundy-red V-neck long-sleeve top tucked into a black pleated midi skirt with double belt, black ankle heels."),

    # --- R07 (G15: Chàng trai Lâm mua cơm gà và áo ấm tặng Bà Mến ở quán cơm vỉa hè) ---
    ("r07", "lam_tot", "G15_01 - Lâm (Chàng trai tử tế mua cơm gà và áo ấm biếu bà cụ nghèo) [Khoác kaki đen sơ mi trắng].png",
     "G15", "Lâm (28t)", "Chàng trai trẻ ấm áp tinh tế giúp đỡ bà Mến tại quán cơm bình dân [Khoác kaki đen]",
     "Subject: Distinct 28-year-old warm-hearted Vietnamese young man, gentle bright smile, neat black hair, wristwatch, NO glasses. Outfit: casual black denim/cotton trucker jacket worn open over a white collared polo shirt, dark chinos, clean sneakers."),
    ("r07", "bamen_cu", "G15_02 - Bà Mến (Bà cụ nghèo đội mũ vải nhặt vỏ chai bên quán cơm) [Áo đũi nâu mũ vải be].png",
     "G15", "Bà Mến (62t)", "Bà cụ nghèo nhặt vỏ nhựa được Lâm mời suất cơm đùi gà và tặng áo ấm [Áo đũi nâu mũ vải be]",
     "Subject: Distinct 62-year-old humble impoverished Vietnamese elderly woman, wearing a beige cotton sun hat, weathered kind face, grateful tearful eyes. Outfit: modest brown linen-cotton button shirt ('áo bà ba đũi nâu'), dark loose pants, worn walking shoes."),
    ("r07", "hao_khach", "G15_03 - Hào (Thực khách trẻ nóng nảy mắng bà cụ nhặt vỏ chai) [Áo polo đen khóa kéo].png",
     "G15", "Hào (26t)", "Khách ăn cơm vỉa hè cộc cằn xua đuổi bà Mến [Áo polo đen khóa kéo]",
     "Subject: Distinct 26-year-old impatient grumpy Vietnamese young man, short textured crop black hair, scowling expression, NO glasses. Outfit: fitted black zip-collar knitted polo shirt, dark jeans, sneakers."),
    ("r07", "chutoan_quan", "G15_04 - Chú Toàn (Chủ quán cơm bình dân hiền lành tốt bụng) [Áo ba lỗ xám tạp dề be].png",
     "G15", "Chú Toàn (48t)", "Chủ quán cơm bình dân vỉa hè chứng kiến lòng tốt của Lâm [Đeo tạp dề quán cơm]",
     "Subject: Distinct 48-year-old friendly Vietnamese street-eatery owner, short black hair, warm honest smile, sturdy build. Outfit: casual grey cotton top with a stained beige canvas cook's apron tied around waist and neck, dark pants, sandals."),

    # --- R08 (G16: Ông cụ đãng trí Ông Thiện ngồi nhầm bàn ăn & hai chàng trai tử tế Duy – Khánh) ---
    ("r08", "ongthien_cu", "G16_01 - Ông Thiện (Cụ ông bảy hai tuổi đãng trí hiền lành - Bố ruột Hạnh Nguyên) [Sơ mi kẻ sọc sáng].png",
     "G16", "Ông Thiện (72t)", "Bố già 72 tuổi mắc chứng đãng trí của Hạnh Nguyên; ngồi nhầm bàn ăn vì nhớ không khí đông vui",
     "Subject: Distinct 72-year-old gentle elderly Vietnamese grandfather with mild forgetfulness, high receding forehead with soft pure-white hair on sides, innocent warm smile, NO glasses, clean-shaven. Outfit: clean loose light blue-and-white vertical striped long-sleeve button shirt, beige-grey comfort trousers, slip-on shoes."),
    ("r08", "duy_tot", "G16_02 - Duy (Chàng trai công sở đeo kính tử tế mời cụ ông ăn cùng - Bạn Khánh) [Vest đen kính gọng mảnh].png",
     "G16", "Duy (29t)", "Chàng trai lịch thiệp đeo kính mời ông Thiện ngồi ăn chung bàn [Vest đen sơ mi đen]",
     "Subject: Distinct 29-year-old polite cultured Vietnamese office professional, wearing thin metal-frame eyeglasses, neat side-parted black hair, kind smile. Outfit: smart black blazer over a black collared dress shirt, dark trousers, leather shoes."),
    ("r08", "khanh_ban", "G16_03 - Khánh (Bạn đồng nghiệp ấm áp của Duy cùng tiếp đãi cụ ông) [Sơ mi xanh than].png",
     "G16", "Khánh (29t)", "Đồng nghiệp tốt bụng đi ăn trưa cùng Duy, ân cần gắp thức ăn mời ông Thiện [Sơ mi xanh than]",
     "Subject: Distinct 29-year-old cheerful kind Vietnamese young man, clean-shaven, NO glasses, neat dark hair, friendly expression. Outfit: dark navy-blue long-sleeve button-up shirt with sleeves rolled slightly, grey dress trousers, dark loafers."),
    ("r08", "gahung", "G16_04 - Gã Hùng (Thực khách bặm trợn xua đuổi cụ ông đãng trí) [Đầu trọc áo ba lỗ đen].png",
     "G16", "Gã Hùng (35t)", "Vị khách thô lỗ ở bàn bên cạnh quát đuổi ông Thiện [Đầu cạo trọc áo đen]",
     "Subject: Distinct 35-year-old burly hot-tempered Vietnamese man, shaved bald head, fierce intimidating frown, muscular arms. Outfit: plain black sleeveless tank top, dark cargo pants, dark shoes."),
    ("r08", "hanhnguyen", "G16_05 - Hạnh Nguyên (Con gái hiếu thảo thanh toán bàn ăn cảm ơn hai chàng trai - Con ông Thiện) [Đầm đỏ cổ yếm].png",
     "G16", "Hạnh Nguyên (33t)", "Con gái ruột hiếu thảo của ông Thiện; bí mật trả tiền bàn ăn báo đáp Duy & Khánh [Đầm đỏ]",
     "Subject: Distinct 33-year-old graceful grateful Vietnamese woman, chin-length soft wavy chestnut bob haircut, warm tearful appreciative smile. Outfit: elegant modest crimson-red halter-neck midi dress, beige heels."),

    # --- R09 (G17: Bà Cậy nhặt ve chai trả lại tiền rơi bị Trâm vu ăn cắp & Việt đứng ra phân xử) ---
    ("r09", "bacay_cu", "G17_01 - Bà Cậy (Bà cụ nhặt ve chai thật thà trả lại tiền rơi trong công viên) [Áo bà ba nâu cầm bao tải].png",
     "G17", "Bà Cậy (65t)", "Bà cụ nhặt ve chai trung thực nhặt trả tiền rơi nhưng bị vu oan trong công viên",
     "Subject: Distinct 65-year-old honest weathered Vietnamese elderly woman who collects recyclables, grey hair tied in a neat bun, deep wrinkles, earnest eyes. Outfit: worn dark-brown traditional buttoned cotton shirt, black trousers, simple sandals, holding a clean folded white woven sack."),
    ("r09", "viet_sep", "G17_02 - Việt (Doanh nhân trẻ chính trực bảo vệ bà cụ nhặt ve chai giữa công viên) [Áo polo nâu đất].png",
     "G17", "Việt (30t)", "Chàng doanh nhân trẻ đi dạo công viên đứng ra bảo vệ sự trong sạch của bà Cậy [Polo nâu]",
     "Subject: Distinct 30-year-old upright athletic Vietnamese man, neat short black hair, firm righteous gaze, NO glasses, clean-shaven. Outfit: smart fitted cognac-brown knitted polo shirt tucked into dark navy chinos with leather belt, dark casual loafers."),
    ("r09", "tram_kieu", "G17_03 - Trâm (Cô gái ăn diện kiêu kỳ đánh rơi tiền rồi vu oan bà cụ) [Set tweed hồng tiểu thư].png",
     "G17", "Trâm (24t)", "Cô gái trẻ kiêu ngạo được bà Cậy nhặt trả tiền nhưng lại vu bà ăn cắp [Set tweed hồng tiểu thư]",
     "Subject: Distinct 24-year-old arrogant trendy Vietnamese young woman, long wavy brown hair with bangs, haughty spoiled expression, small shoulder handbag. Outfit: chic pastel pink tweed cropped jacket with matching pink tweed mini-skirt set, strappy heels."),

    # --- R10 (G18: Bà Vượng bó bột ngồi xe lăn ở phòng trọ & con trai Đăng đòi lại nhà tên mẹ) ---
    ("r10", "bavuong_me", "G18_01 - Bà Vượng (Mẹ quê tay bó bột ngồi xe lăn đứng tên sổ đỏ nhà phố - Mẹ ruột Đăng).png",
     "G18", "Bà Vượng (63t)", "Mẹ ruột bán vườn mua nhà cho Đăng; bị gãy tay ở phòng trọ vì nhường nhịn con dâu [Tay bó bột]",
     "Subject: Distinct 63-year-old loving Vietnamese mother, greying hair in a bun, gentle tearful face; her RIGHT forearm is wrapped in a clean white medical plaster cast supported by a black arm sling strap around her neck. Outfit: humble patched brown cotton long-sleeve shirt and dark loose trousers, slippers."),
    ("r10", "dang_ck", "G18_02 - Đăng (Người chồng chí hiếu quyết đón mẹ ngồi xe lăn về nhà chính - Con bà Vượng) [Polo xanh navy viền trắng].png",
     "G18", "Đăng (31t)", "Con trai hiếu thảo của bà Vượng; chồng Oanh [Polo xanh navy viền trắng]",
     "Subject: Distinct 31-year-old devoted Vietnamese son, clean short black hair, expressive emotional eyes, NO glasses, clean-shaven. Outfit: smart navy-blue knitted polo shirt with crisp white collar piping trim, dark navy trousers with leather belt, wristwatch, black shoes."),
    ("r10", "oanh_vo", "G18_03 - Oanh (Nàng dâu ích kỷ đòi đẩy mẹ chồng vào viện dưỡng lão - Vợ Đăng) [Đầm trễ vai đỏ rượu].png",
     "G18", "Oanh (28t)", "Vợ ích kỷ của Đăng; đưa bố mẹ đẻ sang ở nhà mẹ chồng mua nhưng lại đuổi mẹ chồng [Đầm đỏ rượu]",
     "Subject: Distinct 28-year-old fierce selfish Vietnamese wife, high updo bun with neat bangs, cold arrogant expression, gold necklace. Outfit: fitted off-shoulder burgundy-maroon midi dress, dark heels."),

    # --- R11 (G07 additions: Giám đốc chi nhánh Vũ & Cô lao công Cô Thu — paired with existing Quân G04_05c) ---
    ("r11", "vu_gd", "G07_06 - Vũ (Giám đốc chi nhánh số bảy hách dịch cậy chị làm nhân sự tổng) [Vest xanh sọc cà vạt xanh].png",
     "G07", "Vũ (33t)", "Giám đốc chi nhánh số 7 hống hách bắt cô lao công lau giày, bị Chủ tịch Quân sa thải tại chỗ",
     "Subject: Distinct 33-year-old arrogant Vietnamese corporate branch director, slicked-back black hair, sneering condescending expression, NO glasses. Outfit: navy-blue pinstripe business suit with a small gold name badge on chest, white dress shirt, patterned blue silk necktie, shiny black leather oxford shoes."),
    ("r11", "cothu_lc", "G07_07 - Cô Thu (Cô lao công tòa nhà hiền lành bị ép lau giày trong sảnh thang máy) [Đồng phục lao công xanh xám].png",
     "G07", "Cô Thu (60t)", "Cô lao công tòa nhà chăm chỉ được Chủ tịch Quân bảo vệ danh dự [Đồng phục lao công]",
     "Subject: Distinct 60-year-old humble hardworking Vietnamese female building cleaner, short silver-grey hair under a neat grey cloth cap, kind worried wrinkled face. Outfit: modest light grey-blue long-sleeve cleaner's button-up work tunic, black work trousers, non-slip dark flat shoes."),

    # --- R13 (G07 additions: Quản lý Huyền & Bà Lụa — paired with existing Giám đốc Hiếu G05_02b) ---
    ("r13", "huyen_ql", "G07_08 - Huyền (Quản lý hành chính tham lam ăn chặn tiền công người nghèo dưới quyền Hiếu) [Đầm kim tuyến cổ yếm].png",
     "G07", "Huyền (29t)", "Quản lý hành chính kiêu kỳ ăn bớt 1 triệu tiền dọn vệ sinh của bà Lụa tại công ty Hiếu",
     "Subject: Distinct 29-year-old flashy greedy Vietnamese female office manager, long glamorous wavy dark hair, silver hoop earrings, calculating haughty look. Outfit: flashy colorful sequin-patterned sleeveless halter midi dress, high heels."),
    ("r13", "balua_lc", "G07_09 - Bà Lụa (Bà cụ dọn vệ sinh thời vụ gom tiền lo cho chồng nằm viện) [Áo nâu vá túi ngực].png",
     "G07", "Bà Lụa (62t)", "Bà cụ nghèo làm vệ sinh thời vụ bị Huyền ăn chặn 1 triệu tiền viện phí của chồng",
     "Subject: Distinct 62-year-old exhausted poor Vietnamese elderly woman, silver hair tied tightly back, tearful pleading eyes, thin frame. Outfit: faded brown long-sleeve work shirt with a lighter tan cloth patch sewn on the right chest pocket, dark trousers, worn sandals."),

    # --- R15 (G19: Chồng Toàn mê bạn nhậu & người vợ tinh tế Hạnh nấu cơm sườn cảm hóa) ---
    ("r15", "toan_ck", "G19_01 - Toàn (Người chồng mê bạn nhậu tỉnh ngộ nhờ bữa cơm sườn của vợ - Chồng Hạnh) [Sơ mi xám than].png",
     "G19", "Toàn (30t)", "Chồng của Hạnh; từng ham vui bạn nhậu nhưng thức tỉnh nhờ sự bao dung của vợ [Sơ mi xám]",
     "Subject: Distinct 30-year-old relatable Vietnamese working husband, short natural black hair, expressive face capable of remorse and warmth, NO glasses, clean-shaven. Outfit: casual dark slate-grey long-sleeve button shirt with sleeves rolled up, dark trousers, casual shoes."),
    ("r15", "hanh_vo", "G19_02 - Hạnh (Người vợ hiền khéo léo nấu cơm sườn cảm hóa chồng - Vợ Toàn) [Áo blouse hồng nhạt].png",
     "G19", "Hạnh (27t)", "Vợ hiền dịu tinh tế của Toàn; dùng bữa cơm nóng cảm hóa chồng bỏ nhậu [Áo hồng nhạt]",
     "Subject: Distinct 27-year-old gentle wise Vietnamese wife, shoulder-length soft black hair, warm forgiving eyes and tender smile. Outfit: modest pastel dusty-pink long-sleeve home blouse with white piping trim, comfortable dark trousers, indoor slippers."),
    ("r15", "manh_nhau", "G19_03 - Mạnh (Gã bạn nhậu hay rủ rê khích tướng Toàn ngoài quán bia) [Áo thun đen cổ tròn].png",
     "G19", "Mạnh (31t)", "Bạn nhậu hay khích bác rủ rê Toàn bỏ bê cơm nhà [Áo thun đen]",
     "Subject: Distinct 31-year-old loud-mouthed Vietnamese drinking buddy, slightly flushed cheeks, messy short black hair, smirk expression. Outfit: casual black crew-neck t-shirt, dark blue jeans, sneakers."),
    ("r15", "trung_ql", "G19_04 - Anh Trung (Đội trưởng mang tiền lương tới nhà gửi Toàn và khen vợ Toàn đảm đang) [Sơ mi xanh dương].png",
     "G19", "Anh Trung (35t)", "Quản lý đội làm việc mang lương tới nhà gửi cho vợ chồng Toàn – Hạnh [Sơ mi xanh]",
     "Subject: Distinct 35-year-old polite Vietnamese team supervisor, neat short hair, friendly respectful demeanor, NO glasses. Outfit: clean medium-blue collared work shirt tucked into dark trousers, leather shoes."),

    # --- R17 (G20: Vợ chồng Khiêm – Thùy quyết định đón hai cháu mồ côi sau đám tang bố vợ) ---
    ("r17", "khiem_ck", "G20_01 - Khiêm (Người chồng đeo kính nhân hậu đón hai cháu vợ mồ côi về nuôi - Chồng Thùy) [Vest đen sơ mi đen].png",
     "G20", "Khiêm (32t)", "Chồng nhân hậu trọng tình thân của Thùy; tình nguyện nuôi hai cháu mồ côi [Đeo kính vest đen]",
     "Subject: Distinct 32-year-old compassionate Vietnamese husband wearing rectangular black-frame eyeglasses, neat black hair, warm sincere eyes, clean-shaven. Outfit: solemn black blazer worn over a black collared button-up shirt, black trousers, black shoes."),
    ("r17", "thuy_vo", "G20_02 - Thùy (Người vợ hiền thương hai cháu ruột bơ vơ sau khi bố qua đời - Vợ Khiêm) [Áo đen trang nghiêm].png",
     "G20", "Thùy (29t)", "Vợ hiền giàu tình thương của Khiêm; lo cho hai cháu nhỏ sau lễ tang bố đẻ [Áo đen giản dị]",
     "Subject: Distinct 29-year-old gentle emotional Vietnamese wife, hair tied neatly back, red-rimmed tearful eyes after mourning her late father, modest natural face. Outfit: solemn modest plain black long-sleeve button-up blouse and black ankle-length skirt, black flat shoes."),

    # --- R18 (G21: Bà Thơm ở quê dậy sớm nấu cơm bị con dâu Đào chê bẩn ném trả 200 nghìn) ---
    ("r18", "bathom_me", "G21_01 - Bà Thơm (Mẹ quê tóc bạc dậy sớm nấu cơm lén cho con dâu hai trăm nghìn - Mẹ Vĩnh) [Áo chàm xanh vá vai].png",
     "G21", "Bà Thơm (64t)", "Mẹ ruột tảo tần ở quê của Vĩnh; bị con dâu Đào chê cơm quê và ném trả tiền [Áo chàm xanh]",
     "Subject: Distinct 64-year-old silver-haired Vietnamese rural mother, kind deeply lined face, tearful loving eyes. Outfit: faded indigo-blue cotton country grandma shirt with small neat cloth patches on shoulders, loose black pants, rubber slippers."),
    ("r18", "vinh_ck", "G21_02 - Vĩnh (Người con trai thương mẹ thẳng thừng đuổi người vợ vô lễ - Con bà Thơm) [Polo xanh rêu].png",
     "G21", "Vĩnh (30t)", "Con trai hiếu thảo của bà Thơm; dứt khoát không dung thứ khi vợ xúc phạm mẹ [Polo xanh rêu]",
     "Subject: Distinct 30-year-old filial Vietnamese man, clean short black hair, honest expressive face, NO glasses, clean-shaven. Outfit: forest-green knitted collared polo shirt with thin white trim on collar, dark trousers, casual dark shoes."),
    ("r18", "dao_vo", "G21_03 - Đào (Nàng dâu đỏng đảnh chê nhà ngói mẹ chồng bẩn ném trả tiền - Vợ Vĩnh) [Sơ mi kem nơ chân váy đen].png",
     "G21", "Đào (26t)", "Vợ đỏng đảnh vô lễ của Vĩnh; chê bai nhà quê bà Thơm [Sơ mi kem nơ chân váy đen]",
     "Subject: Distinct 26-year-old spoiled city Vietnamese young woman, straight chestnut-brown shoulder-length hair, annoyed disdainful expression, wristwatch. Outfit: trendy cream silk bow-tie blouse tucked into a high-waisted black A-line skirt, heeled sandals."),

    # --- R19 (G22: Em trai Nghĩa cho anh trai Thịnh – chị dâu Dung vay 25 cây vàng không giấy tờ) ---
    ("r19", "nghia_em", "G22_01 - Nghĩa (Em trai trọng tình cho anh ruột vay hai mươi lăm cây vàng không giấy - Em Thịnh) [Kính gọng mảnh sơ mi trắng].png",
     "G22", "Nghĩa (30t)", "Em trai ruột của Thịnh; cho anh chị vay 25 cây vàng cứu nợ nhưng bị ép nhận 1 tỷ tiền mặt",
     "Subject: Distinct 30-year-old educated upright Vietnamese younger brother, wearing thin silver-rimmed eyeglasses, neat side-parted black hair, composed righteous expression. Outfit: crisp white long-sleeve dress shirt tucked into charcoal trousers, black shoes."),
    ("r19", "thinh_anh", "G22_02 - Thịnh (Anh trai khấm khá nhưng tính toán trả tiền mặt thay vì trả vàng cho em - Chồng Dung) [Sơ mi lụa xanh lục bảo].png",
     "G22", "Thịnh (36t)", "Anh trai ruột của Nghĩa; chồng Dung; làm ăn phất lên từ 25 cây vàng của em nhưng lật lọng [Sơ mi lụa xanh lục bảo]",
     "Subject: Distinct 36-year-old stocky wealthy-looking Vietnamese older brother, slick combed black hair, defensive calculating expression, NO glasses. Outfit: luxurious emerald-green silk collared dress shirt with black trousers, dress shoes."),
    ("r19", "dung_cd", "G22_03 - Dung (Chị dâu sắc sảo cậy không giấy nợ ép chú em nhận tiền lúc vàng rẻ - Vợ Thịnh) [Áo dài đỏ ngọc trai].png",
     "G22", "Dung (34t)", "Vợ Thịnh; chị dâu tráo trở của Nghĩa [Áo dài đỏ cổ đính ngọc trai]",
     "Subject: Distinct 34-year-old sharp calculating Vietnamese sister-in-law, half-up long black hair, pearl-trimmed collar, smug argumentative face. Outfit: festive bright red traditional Vietnamese tunic ('áo dài cách tân đỏ') with pearl neckline trim and dark pants."),

    # --- R20 (G23: Bà Tần nhịn thuốc bán rau nuôi con trai Cường & ân nhân Phong — paired with Bác sĩ Khoa G08_03) ---
    ("r20", "batan_me", "G23_01 - Bà Tần (Người mẹ đau dạ dày nhịn tiền thuốc ngồi chợ bán rau tám nghìn - Mẹ ruột Cường) [Áo hoa nâu sẫm].png",
     "G23", "Bà Tần (61t)", "Mẹ nghèo nhịn viện phí bán từng mớ rau nuôi con trai Cường; bệnh nhân của bác sĩ Khoa",
     "Subject: Distinct 61-year-old pale hardworking Vietnamese mother with stomach illness, dark hair with grey strands tied in a bun, tired loving eyes. Outfit: modest dark brown-and-grey small floral print long-sleeve button shirt, black cloth pants, simple sandals."),
    ("r20", "cuong_con", "G23_02 - Cường (Đứa con trai ham chơi thức tỉnh quỳ bên rổ rau xin lỗi mẹ - Con bà Tần) [Áo ba lỗ đen].png",
     "G23", "Cường (27t)", "Con trai bà Tần; từng lấy tiền lẻ bán rau đi nhậu nhưng hối hận quay đầu [Áo ba lỗ đen]",
     "Subject: Distinct 27-year-old rebellious working-class Vietnamese young man who repents, short buzzed-side black haircut, tanned skin, raw emotional expression. Outfit: casual black sleeveless cotton tank top, slim black jeans, dark sneakers."),
    ("r20", "phong_sep", "G23_03 - Phong (Chủ nhà hàng tử tế đeo kính dẫn Cường ra chợ tỉnh ngộ và mua hết rau giúp bà Tần) [Kính đen sơ mi trắng].png",
     "G23", "Phong (30t)", "Ông chủ nhà hàng tốt bụng thức tỉnh Cường và bao tiêu rau sạch giúp bà Tần chữa bệnh",
     "Subject: Distinct 30-year-old calm wise Vietnamese restaurant owner, wearing sleek black-rimmed eyeglasses, neat straight black hair with light fringe, upright principled demeanor. Outfit: crisp white long-sleeve dress shirt tucked into black tailored trousers with belt, black leather shoes."),
]

SET_SPECS_BASE = [
    ("r01", "r01bo1", "R01_BO1_SanhTanGiaDongKhach",
     SET_PROMPT_TPL.format(desc="Spacious bright modern Vietnamese luxury townhouse banquet hall during a crowded housewarming celebration: warm cream walls with subtle tasteful fluted wood and marble accent panels, crystal chandeliers overhead, round banquet tables with white tablecloths in the background where blurred Vietnamese relatives sit chatting warmly, clear open polished porcelain tile floor in the foreground.")),
    ("r02", "r02bo1", "R02_BO1_PhongKhachNamPhuong",
     SET_PROMPT_TPL.format(desc="Clean modern middle-class Vietnamese city apartment living room: warm cream-beige sofa, tasteful subtle light oak wood-slat accent wall with a framed landscape painting, small neat work desk with an open laptop on the side, warm recessed ceiling lights, open floor space in foreground.")),
    ("r03", "r03bo1", "R03_BO1_DaiSanhGioHoDongNguoi",
     SET_PROMPT_TPL.format(desc="Grand traditional-meets-modern Vietnamese family clan hall during an ancestral feast day ('ngày giỗ họ'): warm timber ceiling beams, chandelier, round feast tables in the background with blurred Vietnamese clan relatives seated politely, wooden tea sofa on one side, spacious clean stone-tiled center floor.")),
    ("r03", "r03bo2", "R03_BO2_GianBepMuoiMamBat",
     SET_PROMPT_TPL.format(desc="Large realistic Vietnamese home kitchen after a big family feast: stainless sink and counter stacked neatly with many ceramic bowls, plates, and chopsticks waiting to be washed, warm practical indoor lighting, clean tiled floor.")),
    ("r04", "r04bo1", "R04_BO1_CanHoCaoCapHoangYen",
     SET_PROMPT_TPL.format(desc="Upscale high-rise Vietnamese city apartment open living-dining foyer: floor-to-ceiling glass window showing distant daytime city skyline, marble kitchen island on one side, subtle modern walnut and cream decorative wall paneling, polished bright floor in foreground.")),
    ("r05", "r05bo1", "R05_BO1_SanGachNhaNgoiQueCu",
     SET_PROMPT_TPL.format(desc="Authentic humble Northern Vietnamese countryside courtyard in front of an old weathered yellow-plaster three-bay clay-tile roof house ('nhà ngói ba gian cũ'), red clay brick yard, small low wooden tea table and stools, green banana trees by a weathered brick gate, natural overcast daylight, ZERO luxury decor.")),
    ("r07", "r07bo1", "R07_BO1_QuanComBinhDanViaHe",
     SET_PROMPT_TPL.format(desc="Authentic bustling Vietnamese street-side affordable rice eatery ('quán cơm bình dân vỉa hè Hà Nội'): simple wooden and plastic tables on a tree-lined sidewalk, steaming metal soup pot by the storefront counter, blurred motorbikes and pedestrians passing along the street in background, natural daytime light, ZERO luxury walls.")),
    ("r08", "r08bo1", "R08_BO1_NhaHangComGiaDinh",
     SET_PROMPT_TPL.format(desc="Warm inviting casual Vietnamese family restaurant at lunchtime: neat wooden dining tables and chairs, warm pendant lamps, wooden lattice divider, cashier counter near entrance, several blurred diners eating quietly in background, clear foreground aisle.")),
    ("r09", "r09bo1", "R09_BO1_LoiDiCongVienXanhMat",
     SET_PROMPT_TPL.format(desc="Sunlit paved brick walkway lined with lush green mature trees and manicured lawns inside a clean Vietnamese public city park, a few distant blurred walkers in background, natural dappled morning sunlight.")),
    ("r10", "r10bo1", "R10_BO1_PhongTroNhoTuongVangCu",
     SET_PROMPT_TPL.format(desc="Humble small ground-floor Vietnamese rental room: aged peeling pale-yellow painted plaster walls, old brown wooden wardrobe, a simple small wooden table with two bowls and rice plates, modest natural window light, ZERO luxury paneling.")),
    ("r11", "r11bo1", "R11_BO1_SanhThangMayToaNha",
     SET_PROMPT_TPL.format(desc="Modern Vietnamese corporate office building ground-floor elevator lobby: brushed Champagne-gold elevator doors open in background, cream marble walls, several blurred office employees standing respectfully in background, gleaming marble floor in foreground.")),
    ("r12", "r12bo1", "R12_BO1_GianBepAmCungThanhLinh",
     SET_PROMPT_TPL.format(desc="Warm cozy Vietnamese home kitchen-dining room: wooden shelves with clay pots and bowls, wooden dining table with a woven food cover ('lồng bàn') and fresh green vegetables, warm morning sunlight streaming in.")),
    ("r13", "r13bo1", "R13_BO1_QuangTruongSanhCongTy",
     SET_PROMPT_TPL.format(desc="Clean paved stone plaza directly outside the glass entrance lobby of a modern Vietnamese office building, green ornamental trees along the walkway, natural bright daylight.")),
    ("r15", "r15bo1", "R15_BO1_QuanNhauBinhDanToi",
     SET_PROMPT_TPL.format(desc="Lively casual Vietnamese evening street-side beer & hotpot eatery ('quán nhậu bình dân'): warm string lights, low wooden tables with beer glasses and snack plates, blurred evening diners in background.")),
    ("r15", "r15bo2", "R15_BO2_PhongAnAmCungToanHanh",
     SET_PROMPT_TPL.format(desc="Warm modest Vietnamese young couple's apartment dining room in the evening: neat wooden dining table set with a plate of glazed braised pork ribs, rice bowls, and warm yellow pendant light overhead, cozy lived-in home atmosphere.")),
    ("r16", "r16bo1", "R16_BO1_CanHoHienDaiTuLam",
     SET_PROMPT_TPL.format(desc="Bright clean modern Vietnamese young couple's apartment hallway and living room near the front door: soft off-white walls with a minimalist framed floral art print, fabric sofa, a rolling suitcase standing near the wooden entrance door.")),
    ("r17", "r17bo1", "R17_BO1_PhongKhachTramAmKhiemThuy",
     SET_PROMPT_TPL.format(desc="Quiet modest Vietnamese apartment living room in soft late-afternoon light: neutral beige fabric sofa, sheer grey window curtains, warm understated home atmosphere.")),
    ("r18", "r18bo1", "R18_BO1_NgoGachSanNhaQue",
     SET_PROMPT_TPL.format(desc="Authentic rustic Vietnamese village brick alley opening into a packed-earth courtyard in front of a modest old tile-roof country house, brick garden wall with green pomelo tree branches, natural daylight, ZERO modern luxury decor.")),
    ("r19", "r19bo1", "R19_BO1_GianNhaGoBanTraGiaToc",
     SET_PROMPT_TPL.format(desc="Traditional dignified Vietnamese wooden ancestral house interior ('nhà gỗ truyền thống'): polished dark wooden pillars, carved wooden cabinet in background, solid rosewood tea table with porcelain teapot and teacups in center, warm natural window light.")),
    ("r20", "r20bo1", "R20_BO1_DauNgoNhoHienNhaCu",
     SET_PROMPT_TPL.format(desc="Humble narrow Vietnamese working-class residential alley beside a weathered plaster house stoop with a red plastic chair, motorbikes parked in far distance, natural afternoon light, ZERO luxury walls.")),
    ("r20", "r20bo2", "R20_BO2_SapRauGocChoDanSinh",
     SET_PROMPT_TPL.format(desc="Authentic bustling Vietnamese local wet-market street corner ('chợ dân sinh buổi chiều'): blue tarpaulin awnings, baskets of fresh green leafy vegetables on low stools at the side, blurred afternoon shoppers with conical hats walking in background.")),
]
