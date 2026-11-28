"""
Single Source of Truth cho Chiến Dịch 9 Video USP Hằng Thu Pharma (HTPM) — Ngày 24/11/2026 (V01..V09 = Ngày 02..Ngày 10):
- Khổ dọc 9:16 ONLY (1080x1920 @ 24fps), giọng đọc THANH THANH TVC (78ef243f)
- Khóa cứng 100% gương mặt Chị Hằng (MAU_CHI_HANG_PORTRAIT.png) + 9 bộ trang phục mới hoàn toàn không trùng lặp (Bộ 02 -> Bộ 10)
- Nâng cấp theo yêu cầu trực tiếp của Người dùng:
  1. TIÊU ĐỀ HOOK ĐẦU TIÊN Ở TRÊN ĐẦU ĐÚNG TẦM 3 GIÂY (0.08s -> 3.08s = 3.00s, Y=262..470px, cỡ lớn 84-92px viền trắng dày 16px + Kicker Pill 32px).
  2. TOÀN BỘ CHỮ TEXT TO HƠN NỮA, TO RÕ RÀNG:
     - Phụ đề: cỡ lớn 46px (từ khóa vàng 50px) trên đệm nhung tối tương phản cao rgba(24,6,18,0.86) viền vàng mảnh, 4-6 chữ/dòng cực dễ đọc.
     - Thẻ Slide kính mờ: rộng 814px, tiêu đề thẻ 27px, nội dung dòng 34px đậm sắc nét.
     - End-Card: hộp sản phẩm thật IS-Net 100% + nút CTA cỡ lớn 34px + dòng pháp lý rõ nét 22px.
"""
from pathlib import Path

ROOT_OUT = Path(r"d:\AI\full studio\output\htpm-9usp-261124")
BRAND_KIT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")
CH_HANG_PORTRAIT = str(BRAND_KIT / "ambassadors_models" / "MAU_CHI_HANG_PORTRAIT.png")
HT_LOGO_PNG = str(BRAND_KIT / "logos_png" / "ht_logo_official.png")

CHAR_BASE = (
    "[CHARACTER LOCK — CHI HANG HTPM AMBASSADOR]: Keep the EXACT SAME graceful 36-year-old Vietnamese woman from the first reference portrait "
    "with 100% identical facial identity: soft full-oval face, luminous fair rosy realistic skin texture, warm expressive dark-brown eyes "
    "with natural double eyelids, softly arched dark-brown eyebrows, refined nose, warm trustworthy smile with coral-rose lips, "
    "natural dark-brown hair. "
)

CINE_916 = "Vertical 9:16 4K photorealistic commercial cinematography, ARRI Alexa Mini LF, 50mm f/1.8 prime lens, zero text, zero watermarks. "
ZERO_LIP = " Natural calm breathing, lips gently closed or softly smiling, zero speaking, zero lip-syncing, no mouthing words, no on-screen text."

VIDEOS_9USP = [
    # =========================================================================
    # V01 (Ngày 02) — SP08: Viên Uống Trắng Da Legend WhiteSkin
    # =========================================================================
    {
        "vid_code": "V01",
        "day_code": "Ngay_02_2511",
        "date_key": "2026-11-25",
        "sku": "SP08 — Viên Uống Trắng Da Legend WhiteSkin",
        "final_name": "261124 HTPM viên uống WhiteSkin sáng mịn tự tin cam thường final.mp4",
        "cutout_png": "SP_WHITESKIN_COMBO_CUTOUT.png",
        "accent_hex": "#C91860",
        "accent_dark": "#8F0D43",
        "outfit_desc": "Bộ 02 — Đầm lụa satin hồng đào tay bồng nhẹ cổ vuông tinh tế dưới nắng ban công buổi sáng",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 02]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a romantic peach-blush silk satin dress with soft puff sleeves and an elegant modest square neckline, hair tucked gently behind one ear with pearl drop earrings. "
        ),
        "hook_kicker": "DA XỈN MÀU • SẠM NẮNG LÂU NGÀY?",
        "hook_hero": "Ngại cam thường?",
        "s4_kicker": "VIÊN UỐNG DƯỠNG SÁNG TỪ GỐC",
        "s4_hero": "Legend WhiteSkin",
        "end_kicker": "VIÊN UỐNG TRẮNG DA",
        "end_title": "WhiteSkin",
        "end_tagline": "MỜ SẠM NÁM · SÁNG MỊN TỪ GỐC",
        "cta_text": "Nhắn ngay “WHITESKIN” · Tư vấn liệu trình 1:1",
        "legal_text": "Thực phẩm bảo vệ sức khỏe · Không phải là thuốc, không thay thế thuốc chữa bệnh",
        "slides": {
            "s2_header": "☀️ Vì sao thoa kem mãi vẫn xỉn màu?",
            "s2_rows": [
                "Da sạm màu, thiếu sức sống dưới nắng",
                "Đốm nâu, tàn nhang khiến nền da kém đều",
                "Thiếu hụt dưỡng chất chống oxy hóa từ trong",
            ],
            "s3_pill": "Nuôi da sáng khỏe từ gốc cùng<br/>Legend WhiteSkin Hằng Thu",
            "s4_header": "✨ Tác động dưỡng sáng đa tầng",
            "s4_rows": [
                "Hỗ trợ làm mờ sạm nám &amp; đốm nâu",
                "Chống oxy hóa, hạn chế lão hóa da sớm",
                "Nuôi làn da ẩm mịn, tươi tắn rạng ngời",
            ],
            "s5_header": "🌸 Bộ dưỡng chất trẻ hóa nền da",
            "s5_rows": [
                "L-Glutathione: Hỗ trợ dưỡng sáng đều màu",
                "NMN &amp; Collagen: Tăng độ đàn hồi, căng mịn",
                "Vitamin E: Dưỡng ẩm &amp; bảo vệ da trước nắng",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Ảnh chụp cam thường hơi xỉn màu, bước ra nắng chị lại càng ngại soi gương?",
                ["cam thường", "soi gương"],
                [
                    ('Ảnh chụp <span class="cap-kw">cam thường xỉn màu,</span>', 0.50),
                    ('Bước ra nắng càng <span class="cap-kw">ngại soi gương?</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Chỉ thoa kem bên ngoài thường khó cải thiện tận gốc khi làn da sạm nám, khô ráp và thiếu sức sống từ bên trong.",
                ["thoa kem", "sạm nám", "bên trong"],
                [
                    ('Chỉ thoa kem ngoài <span class="cap-kw">khó cải thiện tận gốc</span>', 0.48),
                    ('Khi da <span class="cap-kw">sạm nám, khô ráp</span> từ bên trong.', 1.00),
                ],
            ),
            (
                "vo_03",
                "Muốn nền da sáng khỏe bền vững, chị chọn nuôi dưỡng mỗi ngày cùng Viên Uống Trắng Da White Skin Hằng Thu.",
                ["sáng khỏe", "hằng thu"],
                [
                    ('Muốn nền da <span class="cap-kw">sáng khỏe bền vững,</span>', 0.46),
                    ('Chị chọn <span class="cap-kw">Viên Uống WhiteSkin Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "White Skin hỗ trợ làm mờ sạm nám, chống oxy hóa và nuôi dưỡng làn da sáng mịn, đều màu rạng rỡ từ gốc.",
                ["sạm nám", "sáng mịn", "từ gốc"],
                [
                    ('<span class="cap-kw">WhiteSkin</span> hỗ trợ làm mờ sạm nám,', 0.46),
                    ('Chống oxy hóa, dưỡng da <span class="cap-kw">sáng mịn từ gốc.</span>', 1.00),
                ],
            ),
            (
                "vo_05",
                "Sự kết hợp giữa Lờ Glu ta thi on, Nờ Mờ Nờ, Collagen và Vitamin E giúp làn da luôn căng mướt, tươi trẻ đầy sức sống.",
                ["collagen", "vitamin", "sức sống"],
                [
                    ('Kết hợp <span class="cap-kw">L-Glutathione, NMN, Collagen</span>', 0.52),
                    ('Cùng Vitamin E cho da <span class="cap-kw">căng mướt tươi trẻ.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay White Skin để Hằng Thu tư vấn liệu trình đón làn da rạng rỡ cho chị nhé.",
                ["hằng thu", "tư vấn", "rạng rỡ"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot on a sunlit morning balcony overlooking greenery. She holds her phone looking slightly thoughtful at her bare-camera selfie in morning sunlight. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving an airy luminous cream-and-peach sky bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle cinematic push-in on the sunlit morning balcony as she glances thoughtfully at her phone screen and touches her cheek gently in soft morning sunbeams.",
            },
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot beside a bright sunlit vanity mirror with skincare jars; she looks thoughtfully into the mirror noticing dull uneven skin tone after sun exposure, soft warm editorial bokeh.",
                "vid_prompt": "Smooth empathetic camera drift beside the sunlit vanity mirror as she observes her reflection calmly with closed lips.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in an airy sunlit living room accented with white roses; she smiles radiantly at the camera while holding the exact Legend WhiteSkin Hằng Thu box and bottle from the second reference image at chest-to-waist height.",
                "vid_prompt": "Warm graceful dolly-in as she smiles confidently with closed lips while holding the Legend WhiteSkin Hằng Thu box and bottle steadily at waist-chest height.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact Legend WhiteSkin Hằng Thu box and bottle from the reference image in the lower-middle third (Y=54%..84%) on a luminous pearl-white and blush-quartz podium surrounded by crystal water ripples and rose petals. Keep the entire upper half (Y=0..48%) bright airy ivory-pink bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the Legend WhiteSkin box and bottle on the pearl marble podium as golden light sparkles and crystal ripples shimmer.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K luxury skincare CGI & botanical macro photography: luminous golden Vitamin E oil pearls, crystalline L-Glutathione & NMN light spheres, fresh red ripe tomatoes and dewy pink rose petals resting on wet white marble in warm golden sunbeams, airy upper bokeh.",
                "vid_prompt": "Smooth macro slow-motion slider glide across glowing golden skincare serum pearls, crystal spheres, and dewy rose petals in warm morning sunlight.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng gracefully in the LEFT half of the frame (X=5%..50%, head below Y=28%), glowing rosy skin, smiling radiantly while presenting the Legend WhiteSkin Hằng Thu box on a white marble counter in the lower-left foreground. Keep the RIGHT half bright airy blush-cream bokeh.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling radiantly with glowing skin beside the WhiteSkin box while sunlit bokeh shimmers.",
            },
        ],
    },

    # =========================================================================
    # V02 (Ngày 03) — SP04: Dung Dịch Vệ Sinh Romance VIP
    # =========================================================================
    {
        "vid_code": "V02",
        "day_code": "Ngay_03_2611",
        "date_key": "2026-11-26",
        "sku": "SP04 — Dung Dịch Kháng Khuẩn Romance VIP",
        "final_name": "261124 HTPM dung dịch Romance VIP sạch dịu nhẹ chuẩn pH final.mp4",
        "cutout_png": "SP_ROMANCE_VIP_CUTOUT.png",
        "accent_hex": "#B81456",
        "accent_dark": "#7A0A37",
        "outfit_desc": "Bộ 03 — Sơ mi lụa tơ tằm màu đỏ hoa hồng (rose-burgundy) phối chân váy chữ A màu kem, tóc búi thấp thanh lịch",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 03]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a luxurious rose-burgundy mulberry silk blouse tucked into an ivory-cream A-line skirt, hair styled in an elegant Korean low bun with delicate gold stud earrings. "
        ),
        "hook_kicker": "CHĂM SÓC VÙNG NHẠY CẢM MỖI NGÀY",
        "hook_hero": "Cần chuẩn độ pH!",
        "s4_kicker": "DUNG DỊCH KHÁNG KHUẨN DỊU NHẸ",
        "s4_hero": "Romance VIP",
        "end_kicker": "DUNG DỊCH VỆ SINH",
        "end_title": "Romance VIP",
        "end_tagline": "SẠCH THOÁNG 24H · DỊU NHẸ CHUẨN PH",
        "cta_text": "Nhắn ngay “ROMANCE VIP” · Bảo bối êm dịu mỗi ngày",
        "legal_text": "Sản phẩm chăm sóc vệ sinh hằng ngày chiết xuất thiên nhiên · Dịu nhẹ cho làn da nhạy cảm",
        "slides": {
            "s2_header": "⚠️ Sai lầm khi chọn sản phẩm rửa mạnh",
            "s2_rows": [
                "Tẩy rửa quá mạnh dễ gây khô căng, rát đỏ",
                "Mùi hương hóa học nồng không giữ thoáng lâu",
                "Làm mất độ pH tự nhiên của vùng nhạy cảm",
            ],
            "s3_pill": "Nâng niu dịu nhẹ mỗi ngày cùng<br/>Dung Dịch Romance VIP Hằng Thu",
            "s4_header": "🌹 3 ưu điểm chinh phục phái đẹp",
            "s4_rows": [
                "Làm sạch êm dịu, khô thoáng suốt 24 giờ",
                "Hỗ trợ kháng khuẩn, hạn chế mùi khó chịu",
                "Dưỡng ẩm mềm mịn, không hề gây khô rát",
            ],
            "s5_header": "🌿 Tinh chất thiên nhiên thanh khiết",
            "s5_rows": [
                "Hoa hồng Bulgaria: Hương thơm thanh tao",
                "Lô hội &amp; Trà xanh: Làm dịu mát, sạch thoáng",
                "Vitamin E: Cấp ẩm mềm mại chuẩn pH sinh lý",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Chăm sóc vùng nhạy cảm không phải chạy theo mùi hương nồng, mà quan trọng nhất là sự dịu nhẹ chuẩn pê hát.",
                ["mùi hương", "dịu nhẹ"],
                [
                    ('Không cần chạy theo <span class="cap-kw">mùi hương quá nồng,</span>', 0.48),
                    ('Quan trọng nhất là <span class="cap-kw">sự dịu nhẹ chuẩn pH!</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Thời tiết nóng ẩm hay dùng sản phẩm tẩy rửa mạnh rất dễ khiến vùng nhạy cảm khô rát, bí bách và có mùi khó chịu.",
                ["nóng ẩm", "khô rát", "khó chịu"],
                [
                    ('Nóng ẩm hay dùng loại <span class="cap-kw">tẩy rửa quá mạnh</span>', 0.48),
                    ('Dễ gây <span class="cap-kw">khô rát, bí bách</span> và kém tự tin.', 1.00),
                ],
            ),
            (
                "vo_03",
                "Để cơ thể luôn sạch thoáng mỗi ngày, chị chọn nâng niu cùng Dung Dịch Kháng Khuẩn Romance Víp Hằng Thu.",
                ["sạch thoáng", "hằng thu"],
                [
                    ('Để cơ thể luôn <span class="cap-kw">sạch thoáng mỗi ngày,</span>', 0.46),
                    ('Chị chọn <span class="cap-kw">Dung Dịch Romance VIP Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Romance Víp giúp làm sạch nhẹ nhàng, hỗ trợ kháng khuẩn, hạn chế mùi khó chịu suốt hai mươi tư giờ mà không gây khô căng.",
                ["nhẹ nhàng", "kháng khuẩn", "hai mươi tư"],
                [
                    ('<span class="cap-kw">Romance VIP</span> làm sạch êm, kháng khuẩn,', 0.48),
                    ('Giữ thoáng sạch <span class="cap-kw">suốt 24 giờ</span> không khô căng.', 1.00),
                ],
            ),
            (
                "vo_05",
                "Chiết xuất Hoa hồng, Lô hội, Trà xanh cùng Vitamin E dưỡng ẩm mềm mịn, lưu hương thanh khiết đầy cuốn hút.",
                ["hoa hồng", "lô hội", "trà xanh"],
                [
                    ('Chiết xuất <span class="cap-kw">Hoa hồng, Lô hội, Trà xanh</span>', 0.50),
                    ('Và Vitamin E dưỡng ẩm <span class="cap-kw">thơm mát cuốn hút.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Romance Víp để Hằng Thu gửi trao bảo bối tự tin suốt ngày dài cho chị nhé.",
                ["hằng thu", "bảo bối", "tự tin"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot in an airy luxury white marble bathroom vanity bathed in morning sun. She stands gracefully beside fresh pink roses looking calm and poised. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving bright clean white-and-blush marble bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Smooth slow push-in inside the sunlit white marble vanity room as she touches a fresh pink rose petal gently with a poised warm smile.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K luxury feminine-care 3D sensory metaphor: pure crystal-clear water droplets gliding gently over soft blush-pink silk fabric and dewy Bulgarian rose petals in serene morning light, bright airy ivory upper space.",
                "vid_prompt": "Graceful slow-motion 3D silk and crystal water ripple motion cradling fresh dewy Bulgarian rose petals in soft morning light.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a sunlit marble dressing room; she smiles warmly and confidently while holding the exact tall sleek Romance VIP Hằng Thu bottle from the second reference image at chest-to-waist height.",
                "vid_prompt": "Gentle dolly-in as she smiles warmly with closed lips while holding the Romance VIP Hằng Thu bottle steadily in sunlit bokeh.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact Romance VIP Hằng Thu bottle from the reference image in the lower-middle third (Y=52%..86%) on a white marble pedestal surrounded by crystal water ripples and fresh pink Bulgarian roses. Keep upper half (Y=0..46%) airy blush-ivory bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the Romance VIP bottle surrounded by dewy Bulgarian roses and shimmering pure water ripples.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro botanical sensory photography: dewy pink Bulgarian rose blossoms, translucent fresh Aloe Vera gel cubes, tender green tea leaves, and golden Vitamin E droplets on wet white marble in morning sunlight.",
                "vid_prompt": "Sensory slow-motion macro slider across dewy Bulgarian rose petals, crystal aloe vera gel, and green tea leaves sparkling in sunlight.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng gracefully in the LEFT half (X=5%..50%, head below Y=28%), smiling radiantly while presenting the Romance VIP Hằng Thu bottle on a white marble counter in the lower-left foreground; bright airy blush-ivory right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling radiantly beside the Romance VIP bottle in warm sunlit bokeh.",
            },
        ],
    },

    # =========================================================================
    # V03 (Ngày 04) — SP01: Viên Uống Điều Kinh Bổ Trứng HT
    # =========================================================================
    {
        "vid_code": "V03",
        "day_code": "Ngay_04_2711",
        "date_key": "2026-11-27",
        "sku": "SP01 — Viên Uống Điều Kinh Bổ Trứng HT",
        "final_name": "261124 HTPM viên uống Điều Kinh HT chu kỳ đều đặn nhẹ tênh final.mp4",
        "cutout_png": "SP_DIEU_KINH_HT_CUTOUT.png",
        "accent_hex": "#B81456",
        "accent_dark": "#7B0B38",
        "outfit_desc": "Bộ 04 — Áo len mỏng dệt kim màu tím hoa cà (lilac) cổ tim phối quần âu trắng ngà bên bàn trà hoa ấm áp",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 04]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a soft pastel lilac fine-knit V-neck sweater paired with tailored ivory-white trousers, natural soft flowing dark-brown hair beside a warm floral tea table. "
        ),
        "hook_kicker": "LỊCH CÔNG VIỆC LUÔN ĐÚNG HẸN",
        "hook_hero": "Chu kỳ thất thường?",
        "s4_kicker": "VIÊN UỐNG BỒI BỔ KHÍ HUYẾT",
        "s4_hero": "Điều Kinh HT",
        "end_kicker": "ĐIỀU HÒA KINH NGUYỆT",
        "end_title": "Điều Kinh HT",
        "end_tagline": "BỔ HUYẾT · ÊM ĐAU BỤNG · ĐỀU CHU KỲ",
        "cta_text": "Nhắn ngay “ĐIỀU KINH” · Tư vấn riêng theo thể trạng",
        "legal_text": "Thực phẩm bảo vệ sức khỏe · Không phải là thuốc, không thay thế thuốc chữa bệnh",
        "slides": {
            "s2_header": "🩸 Tín hiệu khí huyết kém lưu thông",
            "s2_rows": [
                "Chu kỳ rối loạn, tháng sớm tháng muộn",
                "Đau âm ỉ bụng dưới, người mệt rũ rượi",
                "Nang trứng kém khỏe, chậm đón tin vui",
            ],
            "s3_pill": "Bồi bổ khí huyết từ gốc cùng<br/>Viên Uống Điều Kinh Hằng Thu",
            "s4_header": "✨ Chăm dưỡng chu kỳ êm ái mỗi tháng",
            "s4_rows": [
                "Hỗ trợ bổ huyết, điều hòa kinh nguyệt đều",
                "Giảm đau bụng kinh &amp; mệt mỏi ngày đèn đỏ",
                "Nuôi dưỡng nội tiết &amp; buồng trứng khỏe mạnh",
            ],
            "s5_header": "🌿 Tinh hoa thảo mộc quý cho phái đẹp",
            "s5_rows": [
                "Đương quy &amp; Thục địa: Bồi bổ khí huyết",
                "Hương phụ &amp; Ích mẫu: Điều hòa chu kỳ êm",
                "Hồng hoa &amp; Xuyên khung: Lưu thông ấm tử cung",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Lịch công việc lúc nào cũng đúng hẹn, vậy mà sao lịch chu kỳ của chị cứ tháng sớm tháng muộn?",
                ["công việc", "chu kỳ", "tháng muộn"],
                [
                    ('Lịch công việc luôn <span class="cap-kw">đúng hẹn từng ngày,</span>', 0.48),
                    ('Sao chu kỳ cứ <span class="cap-kw">tháng sớm tháng muộn?</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Mỗi kỳ đèn đỏ bụng đau âm ỉ, người mệt rũ hay thả tự nhiên lâu chưa có tin vui đều báo hiệu khí huyết đang cần được bồi bổ.",
                ["đau âm ỉ", "khí huyết", "bồi bổ"],
                [
                    ('Đau bụng âm ỉ, <span class="cap-kw">người mệt rũ mỗi tháng</span>', 0.48),
                    ('Là tín hiệu <span class="cap-kw">khí huyết cần được bồi bổ.</span>', 1.00),
                ],
            ),
            (
                "vo_03",
                "Thấu hiểu cơ thể phụ nữ, chị chọn chăm dưỡng từ gốc cùng Viên Uống Điều Kinh Hằng Thu.",
                ["thấu hiểu", "điều kinh", "hằng thu"],
                [
                    ('Thấu hiểu cơ thể để <span class="cap-kw">chăm dưỡng từ gốc,</span>', 0.46),
                    ('Chị chọn <span class="cap-kw">Viên Uống Điều Kinh Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Điều Kinh Hằng Thu hỗ trợ bổ huyết, điều hòa chu kỳ đều đặn, làm dịu cơn đau bụng kinh và nuôi dưỡng buồng trứng khỏe mạnh.",
                ["bổ huyết", "đều đặn", "khỏe mạnh"],
                [
                    ('<span class="cap-kw">Điều Kinh HT</span> hỗ trợ bổ huyết, đều chu kỳ,', 0.50),
                    ('Dịu đau bụng kinh &amp; <span class="cap-kw">dưỡng trứng khỏe mạnh.</span>', 1.00),
                ],
            ),
            (
                "vo_05",
                "Hội tụ các thảo mộc quý như Đương quy, Hương phụ, Ích mẫu và Hồng hoa giúp khí huyết lưu thông, sắc diện tươi hồng rạng rỡ.",
                ["đương quy", "hương phụ", "rạng rỡ"],
                [
                    ('Hội tụ <span class="cap-kw">Đương quy, Hương phụ, Ích mẫu</span>', 0.50),
                    ('Giúp khí huyết lưu thông, <span class="cap-kw">sắc diện tươi hồng.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Điều Kinh để Hằng Thu đồng hành cùng chị đón mỗi tháng nhẹ tênh nhé.",
                ["điều kinh", "hằng thu", "nhẹ tênh"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot seated beside a warm sunlit window tea table holding a small desk calendar and a warm ceramic cup with a gentle empathetic expression. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving bright airy warm cream-and-lilac window bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle push-in by the sunlit tea table as she glances thoughtfully at the small desk calendar and warms her hands around the teacup.",
            },
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot resting on a cozy cream sofa wrapped in soft sunlight, placing one hand gently on her lower abdomen with mild monthly fatigue and low energy, warm neutral home bokeh.",
                "vid_prompt": "Empathetic slow camera drift as she rests quietly on the cream sofa holding a warm herbal tea cup with closed lips.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a sunlit floral living room; she smiles warmly and reassuringly while holding the exact Điều Kinh Hằng Thu box from the second reference image at chest-to-waist height.",
                "vid_prompt": "Graceful slow dolly-in as she smiles warmly with closed lips while holding the Điều Kinh Hằng Thu box steadily in warm morning light.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact Điều Kinh Hằng Thu box from the reference image in the lower-middle third (Y=52%..85%) on a warm cream-and-rose marble podium surrounded by pink peony petals and golden light mist. Keep upper half (Y=0..46%) airy pastel bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the Điều Kinh Hằng Thu box on the marble podium as warm golden light particles and peony petals shimmer.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro Oriental herbal photography: slices of Đương quy root, Hương phụ herbs, crimson Hồng hoa (safflower) blossoms, and Ích mẫu leaves arranged beside a steaming glass teapot on warm stone in golden sunbeams, airy upper bokeh.",
                "vid_prompt": "Sensory slow-motion macro slider across Đương quy root slices, crimson safflower petals, and gentle warm herbal tea steam in golden sunlight.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng gracefully in the LEFT half (X=5%..50%, head below Y=28%), radiant rosy complexion, smiling warmly while presenting the Điều Kinh Hằng Thu box on a marble counter in the lower-left foreground; bright airy blush-cream right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling radiantly beside the Điều Kinh Hằng Thu box in warm sunlight.",
            },
        ],
    },

    # =========================================================================
    # V04 (Ngày 05) — SP06: Viên Dưỡng Tử Cung Romance Love
    # =========================================================================
    {
        "vid_code": "V04",
        "day_code": "Ngay_05_2811",
        "date_key": "2026-11-28",
        "sku": "SP06 — Viên Dưỡng Tử Cung Romance Love",
        "final_name": "261124 HTPM viên dưỡng Romance Love cấp ẩm giữ trọn lửa yêu final.mp4",
        "cutout_png": "SP_ROMANCE_LOVE_CUTOUT.png",
        "accent_hex": "#C91860",
        "accent_dark": "#7D0839",
        "outfit_desc": "Bộ 05 — Đầm midi lụa màu vàng champagne ánh kim thanh nhã khoác hờ khăn voan tơ mỏng, phòng ánh đèn vàng ấm",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 05]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "an elegant champagne-gold silk midi dress with a modest round neckline and a sheer organza shawl draped softly over her shoulders, soft romantic wavy hair. "
        ),
        "hook_kicker": "THAY ĐỔI NỘI TIẾT SAU TUỔI 30",
        "hook_hero": "Khô hạn ngại gần?",
        "s4_kicker": "VIÊN DƯỠNG CẤP ẨM CHUYÊN SÂU",
        "s4_hero": "Romance Love",
        "end_kicker": "VIÊN DƯỠNG CẤP ẨM",
        "end_title": "Romance Love",
        "end_tagline": "CẤP ẨM SÂU · MỀM MỊN · GIỮ LỬA YÊU",
        "cta_text": "Nhắn ngay “ROMANCE LOVE” · Tư vấn kín đáo 1:1",
        "legal_text": " Hộp 5 viên dưỡng gói riêng tinh tế · Cấp ẩm dịu êm & bảo mật cho phái đẹp",
        "slides": {
            "s2_header": "💔 Nỗi niềm khó giãi bày sau tuổi 30",
            "s2_rows": [
                "Thiếu hụt độ ẩm tự nhiên, dễ khô căng",
                "Đau rát, e ngại mỗi lần gần gũi bạn đời",
                "Giảm sự tự tin &amp; khoảng cách cảm xúc vợ chồng",
            ],
            "s3_pill": "Cấp ẩm mềm mịn tinh tế cùng<br/>Viên Dưỡng Romance Love Hằng Thu",
            "s4_header": "✨ 3 giá trị nâng niu nét xuân",
            "s4_rows": [
                "Cấp ẩm chuyên sâu, xoa dịu cảm giác khô rát",
                "Hỗ trợ kháng khuẩn, giữ vùng kín sạch thơm",
                "Nuôi dưỡng niêm mạc mềm mịn, trọn cảm xúc",
            ],
            "s5_header": "💧 Tinh chất dưỡng ẩm chuẩn Spa",
            "s5_rows": [
                "Hyaluronic Acid: Giữ nước &amp; cấp ẩm sâu",
                "Vitamin B5 (Panthenol): Làm dịu &amp; phục hồi êm",
                "Niacinamide &amp; Vitamin E: Mềm mại, tươi hồng",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Ánh nến đã thắp, cảm xúc đã lên, nhưng tình trạng khô hạn sau tuổi ba mươi lại khiến chị âm thầm e ngại?",
                ["ánh nến", "khô hạn", "e ngại"],
                [
                    ('Cảm xúc đã lên nhưng <span class="cap-kw">khô hạn tuổi 30+</span>', 0.50),
                    ('Lại khiến chị <span class="cap-kw">âm thầm e ngại gần gũi?</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Thay đổi nội tiết sau sinh hay áp lực tuổi tác làm thiếu hụt độ ẩm tự nhiên, gây đau rát và làm vơi đi sự tự tin vốn có.",
                ["nội tiết", "độ ẩm", "tự tin"],
                [
                    ('Thay đổi nội tiết làm <span class="cap-kw">thiếu độ ẩm tự nhiên,</span>', 0.50),
                    ('Gây khô rát &amp; vơi đi <span class="cap-kw">sự tự tin vốn có.</span>', 1.00),
                ],
            ),
            (
                "vo_03",
                "Để luôn mềm mại và rạng rỡ nét xuân, chị chọn chăm chút bản thân cùng Viên Dưỡng Romance Love Hằng Thu.",
                ["mềm mại", "hằng thu"],
                [
                    ('Để luôn mềm mại và <span class="cap-kw">giữ gìn nét xuân,</span>', 0.46),
                    ('Chị chọn <span class="cap-kw">Viên Dưỡng Romance Love Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Romance Love giúp cấp ẩm chuyên sâu, hỗ trợ kháng khuẩn, xoa dịu khô rát và giữ vùng nhạy cảm luôn mềm mịn, sạch thơm.",
                ["cấp ẩm", "khô rát", "mềm mịn"],
                [
                    ('<span class="cap-kw">Romance Love</span> cấp ẩm sâu, giảm khô rát,', 0.50),
                    ('Giữ vùng nhạy cảm luôn <span class="cap-kw">mềm mịn, sạch thơm.</span>', 1.00),
                ],
            ),
            (
                "vo_05",
                "Giàu Hy a lu ro nic A xít, Vitamin Bê năm, Ni a ci na mide và Vitamin E trong từng gói riêng tinh tế, nâng niu dịu êm.",
                ["vitamin", "tinh tế", "dịu êm"],
                [
                    ('Giàu <span class="cap-kw">Hyaluronic Acid, Vitamin B5,</span>', 0.48),
                    ('Niacinamide &amp; Vitamin E <span class="cap-kw">nâng niu dịu êm.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Romance Love để Hằng Thu tư vấn chi tiết và bảo mật riêng cho chị nhé.",
                ["hằng thu", "tư vấn", "bảo mật"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot in an elegant warm-lit luxury bedroom suite with soft blurred amber candlelight and cream silk drapes. She sits gracefully at a dressing table with a quiet wistful, thoughtful expression. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving warm champagne-and-rose bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle push-in in warm candlelight bokeh as she looks thoughtfully down with poised grace and closed lips.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K luxury skincare 3D CGI metaphor: a luminous silk ribbon transforming from dry matte fabric into dewy, supple rose-champagne satin bathed in glistening Hyaluronic Acid moisture pearls, airy ivory-gold upper bokeh.",
                "vid_prompt": "Smooth 3D luxury fluid motion as glistening moisture pearls glide across supple rose-champagne silk waves in warm golden light.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a bright elegant suite accented with red-pink roses; she smiles warmly and confidently while holding the exact magenta-crimson ROMANCE LOVE Hằng Thu rectangular box from the second reference image at chest-to-waist height.",
                "vid_prompt": "Warm graceful dolly-in as she smiles serenely with closed lips while holding the crimson ROMANCE LOVE box steadily.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact magenta-crimson ROMANCE LOVE Hằng Thu box from the reference image in the lower-middle third (Y=54%..84%) on a champagne-and-rose marble podium surrounded by shimmering moisture droplets and velvet rose petals. Keep upper half (Y=0..46%) airy blush-gold bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the crimson ROMANCE LOVE box on the marble podium as golden bokeh and pure water droplets shimmer.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro skincare active droplets photography: crystal-clear Hyaluronic Acid spheres, golden Vitamin E & B5 serum droplets, and dewy pink rose petals resting on luminous satin glass in warm sunlight.",
                "vid_prompt": "Sensory slow-motion macro slider across crystal Hyaluronic Acid spheres and golden Vitamin B5 & E serum pearls shimmering in warm light.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng gracefully in the LEFT half (X=5%..50%, head below Y=28%), smiling radiantly while presenting the crimson ROMANCE LOVE box on a cream marble counter in the lower-left foreground; bright airy champagne-blush right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling warmly beside the ROMANCE LOVE box in soft golden bokeh.",
            },
        ],
    },

    # =========================================================================
    # V05 (Ngày 06) — SP07: Ngọc Long Hoàn Hằng Thu
    # =========================================================================
    {
        "vid_code": "V05",
        "day_code": "Ngay_06_2911",
        "date_key": "2026-11-29",
        "sku": "SP07 — Ngọc Long Hoàn Hằng Thu",
        "final_name": "261124 HTPM Ngọc Long Hoàn bồi bổ thể lực vững phong độ final.mp4",
        "cutout_png": "SP_NGOC_LONG_HOAN_CUTOUT.png",
        "accent_hex": "#0B7A53",
        "accent_dark": "#064E35",
        "outfit_desc": "Bộ 06 — Set gile vest thiết kế màu xanh lục bảo trầm (emerald) sang trọng, đồng hồ dây da mảnh, phòng khách gỗ ấm cúng",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 06]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a sophisticated tailored deep emerald-green vest blazer set with a modest V-collar over an ivory silk camisole and a slim leather wristwatch, poised executive elegance. "
        ),
        "hook_kicker": "ÁP LỰC CÔNG VIỆC & TUỔI TÁC",
        "hook_hero": "Xuống sức, hụt hơi?",
        "s4_kicker": "BỔ THẬN TRÁNG DƯƠNG TỪ GỐC",
        "s4_hero": "Ngọc Long Hoàn",
        "end_kicker": "BỒI BỔ PHÁI MẠNH",
        "end_title": "Ngọc Long Hoàn",
        "end_tagline": "BỔ THẬN · TĂNG THỂ LỰC · VỮNG PHONG ĐỘ",
        "cta_text": "Nhắn ngay “NGỌC LONG HOÀN” · Tư vấn bảo mật 100%",
        "legal_text": "Thực phẩm bảo vệ sức khỏe · Không phải là thuốc, không thay thế thuốc chữa bệnh",
        "slides": {
            "s2_header": "⚡ Dấu hiệu phái mạnh suy giảm thể lực",
            "s2_rows": [
                "Cơ thể mệt mỏi, đau lưng mỏi gối sau giờ làm",
                "Sinh lực đi xuống, nhanh hụt hơi kém bền bỉ",
                "Khó duy trì phong độ &amp; sự tự tin của đàn ông",
            ],
            "s3_pill": "Món quà tinh tế bồi bổ từ gốc<br/>Ngọc Long Hoàn Hằng Thu",
            "s4_header": "🏆 3 trụ cột phục hồi bản lĩnh",
            "s4_rows": [
                "Hỗ trợ bổ thận tráng dương lành tính từ gốc",
                "Bồi bổ nguyên khí, giảm mệt mỏi đau lưng",
                "Duy trì thể lực dẻo dai &amp; phong độ vững vàng",
            ],
            "s5_header": "🌿 Hội tụ 8 vị thảo dược quý hiếm",
            "s5_rows": [
                "Đông trùng hạ thảo &amp; Nhung hươu bồi bổ",
                "Ba kích tím &amp; Sâm cau tăng cường sinh lực",
                "Dâm dương hoắc &amp; Bá bệnh bền bỉ tự nhiên",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Lịch công việc anh nhớ từng giờ, còn lịch bồi bổ sức khỏe của chính mình anh đã để quên bao lâu rồi?",
                ["công việc", "bồi bổ", "bao lâu"],
                [
                    ('Lịch công việc <span class="cap-kw">nhớ từng giờ mỗi ngày,</span>', 0.48),
                    ('Còn sức khỏe bản thân <span class="cap-kw">quên bao lâu rồi?</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Áp lực thương trường và tuổi tác khiến nhiều anh âm thầm mệt mỏi, đau lưng mỏi gối, hụt hơi và giảm đi phong độ vốn có.",
                ["áp lực", "mệt mỏi", "phong độ"],
                [
                    ('Áp lực &amp; tuổi tác gây <span class="cap-kw">đau lưng, mỏi gối,</span>', 0.48),
                    ('Nhanh hụt hơi &amp; giảm đi <span class="cap-kw">phong độ vốn có.</span>', 1.00),
                ],
            ),
            (
                "vo_03",
                "Món quà tinh tế người vợ tâm lý dành tặng chồng chính là Ngọc Long Hoàn Hằng Thu bồi bổ nền tảng từ gốc.",
                ["món quà", "ngọc long hoàn", "hằng thu"],
                [
                    ('Món quà tinh tế <span class="cap-kw">người vợ dành tặng chồng:</span>', 0.48),
                    ('Chăm sức khỏe từ gốc cùng <span class="cap-kw">Ngọc Long Hoàn.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Ngọc Long Hoàn hỗ trợ bổ thận tráng dương, bồi bổ thể lực và giúp phái mạnh duy trì phong độ vững vàng, bền bỉ.",
                ["bổ thận", "thể lực", "bền bỉ"],
                [
                    ('<span class="cap-kw">Ngọc Long Hoàn</span> hỗ trợ bổ thận tráng dương,', 0.50),
                    ('Bồi bổ thể lực &amp; giữ <span class="cap-kw">phong độ bền bỉ.</span>', 1.00),
                ],
            ),
            (
                "vo_05",
                "Hội tụ tám vị thảo dược quý như Đông trùng hạ thảo, Nhung hươu, Ba kích tím, Sâm cau và Dâm dương hoắc an toàn, lành tính.",
                ["đông trùng", "ba kích", "lành tính"],
                [
                    ('Hội tụ <span class="cap-kw">Đông trùng hạ thảo, Nhung hươu,</span>', 0.50),
                    ('Ba kích tím, Sâm cau <span class="cap-kw">bồi bổ lành tính.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Ngọc Long Hoàn để Hằng Thu tư vấn lộ trình bảo mật một trăm phần trăm nhé.",
                ["ngọc long hoàn", "hằng thu", "bảo mật"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot in a warm sunlit luxury wood-and-cream executive living room. Chị Hằng sits poised with an empathetic thoughtful expression beside a warm tea tray. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving warm sunlit cream-and-gold architectural bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle push-in in the warm sunlit executive living room as she nods empathetically with a warm calm expression and closed lips.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K cinematic lifestyle shot: a successful 40-year-old Vietnamese businessman in a crisp white shirt loosened at the collar sitting at his study desk late afternoon rubbing his shoulder with quiet work fatigue, warm golden window light.",
                "vid_prompt": "Empathetic slow camera drift as the tired Vietnamese businessman exhales quietly at his study desk and rests his hand on his shoulder.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a warm sunlit living room; Chị Hằng in her deep emerald vest suit smiles warmly while holding the exact Ngọc Long Hoàn Hằng Thu box from the second reference image at chest-to-waist height as a thoughtful wellness gift.",
                "vid_prompt": "Warm graceful dolly-in as she smiles reassuringly with closed lips while holding the Ngọc Long Hoàn Hằng Thu box steadily.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact Ngọc Long Hoàn Hằng Thu box from the reference image in the lower-middle third (Y=52%..85%) on a rich dark-gold and cream marble pedestal bathed in warm golden sunbeams. Keep upper half (Y=0..46%) bright warm champagne bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the Ngọc Long Hoàn Hằng Thu box on the marble pedestal as golden light particles shimmer.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro precious Oriental herbs photography: golden Cordyceps (Đông trùng hạ thảo), purple Ba kích roots, Sâm cau, and Dâm dương hoắc leaves arranged artfully on warm stone in golden sunbeams, airy upper bokeh.",
                "vid_prompt": "Sensory slow-motion macro slider across golden Đông trùng hạ thảo, Ba kích roots, and precious Oriental herbs in warm sunlight.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng in her emerald vest suit gracefully in the LEFT half (X=5%..50%, head below Y=28%), smiling warmly while presenting the Ngọc Long Hoàn Hằng Thu box on a marble counter in the lower-left foreground; bright warm cream-gold right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling confidently beside the Ngọc Long Hoàn box in warm golden bokeh.",
            },
        ],
    },

    # =========================================================================
    # V06 (Ngày 07) — SP09: Gel Phụ Khang Hằng Thu
    # =========================================================================
    {
        "vid_code": "V06",
        "day_code": "Ngay_07_3011",
        "date_key": "2026-11-30",
        "sku": "SP09 — Gel Phụ Khang Hằng Thu",
        "final_name": "261124 HTPM Gel Phụ Khang thoáng sạch suốt 8 tiếng văn phòng final.mp4",
        "cutout_png": "SP_GEL_PHU_KHANG_COMBO_CUTOUT.png",
        "accent_hex": "#C91860",
        "accent_dark": "#7F093A",
        "outfit_desc": "Bộ 07 — Áo blouse voan cổ nơ màu xanh bạc hà tươi mát sơ vin chân váy bút chì xám sáng tại văn phòng",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 07]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a fresh mint-green chiffon pussy-bow blouse tucked neatly into a light pearl-grey pencil skirt, half-up half-down hairstyle with delicate silver studs. "
        ),
        "hook_kicker": "DÂN VĂN PHÒNG NGỒI SUỐT 8 TIẾNG",
        "hook_hero": "Bí bách kém tự tin?",
        "s4_kicker": "GEL CHĂM SÓC THẢO DƯỢC DỊU ÊM",
        "s4_hero": "Gel Phụ Khang",
        "end_kicker": "CHĂM SÓC DỊU ÊM",
        "end_title": "Gel Phụ Khang",
        "end_tagline": "SẠCH DỊU NHẸ · KHỬ MÙI · ÊM MÁT CẢ NGÀY",
        "cta_text": "Nhắn ngay “GEL PHỤ KHANG” · Tư vấn riêng tư 1:1",
        "legal_text": "Chiết xuất thảo dược thiên nhiên lành tính · Nhỏ gọn tiện lợi & bảo mật cho phái đẹp",
        "slides": {
            "s2_header": "💻 Nỗi ám ảnh ngồi lâu nơi công sở",
            "s2_rows": [
                "Ngồi 8 tiếng liên tục gây hầm bí, ẩm ướt",
                "Cảm giác ngứa ngáy, mùi khó nói mất tự tin",
                "Ngại đứng gần đồng nghiệp trong phòng họp",
            ],
            "s3_pill": "Bí quyết thoáng sạch êm dịu cùng<br/>Gel Phụ Khang Hằng Thu",
            "s4_header": "✨ 3 tác động êm ái suốt ngày dài",
            "s4_rows": [
                "Làm sạch dịu nhẹ &amp; hỗ trợ kháng khuẩn",
                "Khử mùi khó chịu, xoa dịu cảm giác ngứa rát",
                "Cấp ẩm mềm da, giữ độ thoáng mát tự nhiên",
            ],
            "s5_header": "🌿 Tổ hợp 4 thảo dược lành tính",
            "s5_rows": [
                "Kim ngân hoa &amp; Trầu không: Sạch thoáng êm",
                "Khổ sâm: Làm dịu ngứa rát vùng nhạy cảm",
                "Trinh nữ hoàng cung: Nâng niu khỏe từ gốc",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Ngồi văn phòng suốt tám tiếng bí bách, làm sao để từ sáng đến chiều chị vẫn luôn thoáng sạch và thơm mát?",
                ["tám tiếng", "thoáng sạch", "thơm mát"],
                [
                    ('Ngồi văn phòng <span class="cap-kw">suốt 8 tiếng bí bách,</span>', 0.48),
                    ('Làm sao cả ngày vẫn <span class="cap-kw">thoáng sạch thơm mát?</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Trang phục công sở ôm sát cộng thêm ngồi lâu rất dễ gây ẩm ướt, ngứa rát và mùi khó nói làm chị mất đi sự tự tin.",
                ["công sở", "ẩm ướt", "tự tin"],
                [
                    ('Mặc đồ ôm sát &amp; <span class="cap-kw">ngồi lâu nơi công sở</span>', 0.48),
                    ('Dễ gây ẩm ướt, <span class="cap-kw">ngứa rát kém tự tin.</span>', 1.00),
                ],
            ),
            (
                "vo_03",
                "Đừng đợi đến lúc khó chịu mới nhớ thương mình, chị chọn chăm sóc dịu êm cùng Gel Phụ Khang Hằng Thu.",
                ["thương mình", "phụ khang", "hằng thu"],
                [
                    ('Đừng đợi khó chịu mới <span class="cap-kw">nhớ thương bản thân,</span>', 0.48),
                    ('Chị chọn <span class="cap-kw">Gel Phụ Khang Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Gel Phụ Khang giúp làm sạch nhẹ nhàng, hỗ trợ kháng khuẩn, khử mùi khó chịu và làm dịu êm vùng nhạy cảm suốt ngày dài.",
                ["nhẹ nhàng", "khử mùi", "ngày dài"],
                [
                    ('<span class="cap-kw">Gel Phụ Khang</span> làm sạch êm, kháng khuẩn,', 0.50),
                    ('Khử mùi &amp; dịu mát <span class="cap-kw">suốt cả ngày dài.</span>', 1.00),
                ],
            ),
            (
                "vo_05",
                "Sự kết hợp từ Kim ngân hoa, Trầu không, Khổ sâm và Trinh nữ hoàng cung giúp giữ ẩm mềm mịn, an toàn và lành tính.",
                ["kim ngân hoa", "trầu không", "lành tính"],
                [
                    ('Kết hợp <span class="cap-kw">Kim ngân hoa, Trầu không,</span>', 0.48),
                    ('Khổ sâm &amp; Trinh nữ hoàng cung <span class="cap-kw">lành tính.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Gel Phụ Khang để Hằng Thu tư vấn riêng tư giúp chị tự tin suốt tuần mới nhé.",
                ["phụ khang", "hằng thu", "tự tin"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot seated at a bright sunlit modern glass office desk with a laptop and notebook, pausing thoughtfully mid-afternoon. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving airy sunlit white-and-mint office window bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle push-in at the sunlit glass office desk as she pauses typing and exhales softly with poised calm.",
            },
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot standing beside a modern office glass meeting room holding a folder with subtle afternoon discomfort and hesitation before entering a meeting, soft daylight bokeh.",
                "vid_prompt": "Smooth empathetic camera drift beside the sunlit office glass wall as she adjusts her folder quietly with closed lips.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a sunlit modern lounge; Chị Hằng in her mint-green bow blouse smiles radiantly while holding the exact Gel Phụ Khang Hằng Thu box from the second reference image at chest-to-waist height.",
                "vid_prompt": "Graceful slow dolly-in as she smiles warmly with closed lips while holding the Gel Phụ Khang Hằng Thu box steadily.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact Gel Phụ Khang Hằng Thu box and sleek hygienically sealed tube from the reference image in the lower-middle third (Y=54%..85%) on a pure white-and-blush marble podium surrounded by crystal water ripples. Keep upper half (Y=0..46%) airy pastel bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the Gel Phụ Khang Hằng Thu box and tube on the marble podium as pure water ripples glisten.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro botanical photography: blooming white-and-gold Kim ngân hoa flowers, fresh green Trầu không leaves, Khổ sâm herbs, and white Trinh nữ hoàng cung lily petals with crystal dew droplets in morning sunbeams.",
                "vid_prompt": "Sensory slow-motion macro slider across Kim ngân hoa blossoms, dewy Trầu không leaves, and crystal morning dew in warm sunlight.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng in her mint-green blouse gracefully in the LEFT half (X=5%..50%, head below Y=28%), smiling confidently while presenting the Gel Phụ Khang Hằng Thu box on a white marble counter in the lower-left foreground; bright airy blush-white right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling radiantly beside the Gel Phụ Khang box in sunlit bokeh.",
            },
        ],
    },

    # =========================================================================
    # V07 (Ngày 08) — SP05: Viên Đặt Phụ Khoa Hộp Xanh (Khít Hồng)
    # =========================================================================
    {
        "vid_code": "V07",
        "day_code": "Ngay_08_0112",
        "date_key": "2026-12-01",
        "sku": "SP05 — Viên Đặt Phụ Khoa Hằng Thu (Hộp Xanh)",
        "final_name": "261124 HTPM viên đặt phụ khoa sạch thoáng săn chắc sau sinh final.mp4",
        "cutout_png": "SP_VIEN_DAT_HOP_XANH_CUTOUT.png",
        "accent_hex": "#0B7A53",
        "accent_dark": "#064E35",
        "outfit_desc": "Bộ 08 — Suit nữ hiện đại màu xanh lá thông nhạt (sage green) khoác ngoài áo lụa trắng kem đính cài áo hoa trà",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 08]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a modern tailored sage-green blazer worn over a cream-white silk top with a delicate camellia pearl brooch on the lapel, poised wellness advisor aura. "
        ),
        "hook_kicker": "TÂM SỰ THẦM KÍN CỦA MẸ SAU SINH",
        "hook_hero": "Tái đi tái lại?",
        "s4_kicker": "VIÊN ĐẶT THẢO MỘC SẠCH THOÁNG",
        "s4_hero": "Viên Đặt Hằng Thu",
        "end_kicker": "VIÊN ĐẶT PHỤ KHOA",
        "end_title": "Hằng Thu",
        "end_tagline": "SẠCH DỊCH VIÊM · SĂN CHẮC · CÂN BẰNG PH",
        "cta_text": "Nhắn ngay “VIÊN ĐẶT” · Nhận lộ trình chăm kín đáo",
        "legal_text": "Chiết xuất thảo mộc thiên nhiên lành tính · Chăm sóc dịu êm & bảo mật cho phái đẹp",
        "slides": {
            "s2_header": "🌸 Thay đổi khó nói của phụ nữ sau sinh",
            "s2_rows": [
                "Độ đàn hồi suy giảm, kém săn chắc hơn trước",
                "Dịch tiết có mùi, khó chịu dễ tái đi tái lại",
                "Mặc cảm, giảm cảm xúc khi gần gũi bạn đời",
            ],
            "s3_pill": "Lấy lại sự tự tin từ gốc cùng<br/>Viên Đặt Phụ Khoa Hằng Thu",
            "s4_header": "✨ 3 tác động chăm sóc chuyên sâu",
            "s4_rows": [
                "Làm sạch êm dịu &amp; giảm mùi hôi khó chịu",
                "Hỗ trợ cải thiện độ săn chắc, khít hồng",
                "Duy trì độ ẩm &amp; cân bằng pH sinh lý tự nhiên",
            ],
            "s5_header": "🌿 Công thức thảo mộc thiên nhiên êm dịu",
            "s5_rows": [
                "Cúc La Mã &amp; Cam thảo: Làm dịu niêm mạc",
                "Trầu không &amp; Thảo mộc: Kháng khuẩn sạch êm",
                "Acid Lactic &amp; Niacinamide: Giữ ẩm, sáng hồng",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Vừa hết khó chịu ít hôm lại tái đi tái lại, sau sinh nở chị đừng chỉ vội vàng che giấu mùi hương bên ngoài.",
                ["khó chịu", "sau sinh", "bên ngoài"],
                [
                    ('Vừa hết ít hôm lại <span class="cap-kw">tái đi tái lại,</span>', 0.46),
                    ('Đừng chỉ vội vàng <span class="cap-kw">che giấu mùi bên ngoài!</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Sau sinh, độ đàn hồi suy giảm kèm dịch tiết có mùi khiến nhiều chị em âm thầm mặc cảm và e ngại gần gũi chồng.",
                ["đàn hồi", "mặc cảm", "gần gũi"],
                [
                    ('Sau sinh <span class="cap-kw">kém săn chắc, dịch có mùi</span>', 0.48),
                    ('Khiến chị em mặc cảm, <span class="cap-kw">ngại gần gũi chồng.</span>', 1.00),
                ],
            ),
            (
                "vo_03",
                "Khi phụ nữ biết thương mình từ gốc, chị chọn đồng hành cùng Viên Đặt Phụ Khoa Hằng Thu.",
                ["thương mình", "phụ khoa", "hằng thu"],
                [
                    ('Biết thương bản thân <span class="cap-kw">chăm sóc từ gốc,</span>', 0.46),
                    ('Chị chọn <span class="cap-kw">Viên Đặt Phụ Khoa Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Viên Đặt Hằng Thu hỗ trợ làm sạch êm dịu, giảm mùi khó chịu, cải thiện độ săn chắc khít hồng và cân bằng pê hát tự nhiên.",
                ["làm sạch", "săn chắc", "tự nhiên"],
                [
                    ('<span class="cap-kw">Viên Đặt Hằng Thu</span> làm sạch êm, giảm mùi,', 0.50),
                    ('Hỗ trợ <span class="cap-kw">săn chắc khít hồng</span> &amp; chuẩn pH.', 1.00),
                ],
            ),
            (
                "vo_05",
                "Chiết xuất Cúc La Mã, Cam thảo cùng thảo mộc thiên nhiên nuôi dưỡng vùng nhạy cảm khỏe mạnh và mềm mịn.",
                ["cúc la mã", "cam thảo", "khỏe mạnh"],
                [
                    ('Chiết xuất <span class="cap-kw">Cúc La Mã, Cam thảo</span> tự nhiên', 0.50),
                    ('Nuôi dưỡng vùng nhạy cảm <span class="cap-kw">khỏe mạnh, êm ái.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Viên Đặt để Hằng Thu hướng dẫn liệu trình chăm sóc kín đáo tại nhà cho chị nhé.",
                ["viên đặt", "hằng thu", "kín đáo"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot in a sunlit wellness consultation room accented with white camellias and greenery. Chị Hằng in her sage-green blazer sits warmly with an empathetic advisor expression. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving bright airy cream-and-sage bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle push-in in the sunlit consultation room as she listens empathetically and nods with a warm reassuring smile.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K luxury feminine-care 3D sensory metaphor: pure crystal dew droplets and white chamomile blossoms floating gently over soft sage-and-ivory silk waves in serene morning sunlight, airy upper space.",
                "vid_prompt": "Smooth 3D silk and crystal dew motion cradling fresh white chamomile blossoms in warm morning light.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a bright sunlit living room; Chị Hằng in her sage-green suit smiles warmly while holding the exact green-and-gold Viên Đặt Phụ Khoa Hằng Thu rectangular box from the second reference image at chest-to-waist height.",
                "vid_prompt": "Warm graceful dolly-in as she smiles confidently with closed lips while holding the green Viên Đặt Phụ Khoa Hằng Thu box steadily.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact green-and-gold Viên Đặt Phụ Khoa Hằng Thu box from the reference image in the lower-middle third (Y=54%..84%) on a white-and-jade marble podium surrounded by crystal water ripples and white chamomile flowers. Keep upper half (Y=0..46%) airy ivory-green bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the green Viên Đặt Phụ Khoa Hằng Thu box on the marble podium as pure water ripples shimmer.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro botanical photography: fresh white Chamomile (Cúc La Mã) flowers, sliced Cam thảo licorice root, dewy green Trầu không leaves, and crystal water droplets on white marble in morning sunbeams.",
                "vid_prompt": "Sensory slow-motion macro slider across white Cúc La Mã blossoms, Cam thảo slices, and crystal morning dewdrops.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng in her sage-green blazer gracefully in the LEFT half (X=5%..50%, head below Y=28%), smiling radiantly while presenting the green Viên Đặt Phụ Khoa Hằng Thu box on a marble counter in the lower-left foreground; bright airy cream-sage right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling radiantly beside the green Viên Đặt Phụ Khoa box.",
            },
        ],
    },

    # =========================================================================
    # V08 (Ngày 09) — SP03: Dạ Dày HT Hằng Thu
    # =========================================================================
    {
        "vid_code": "V08",
        "day_code": "Ngay_09_0212",
        "date_key": "2026-12-02",
        "sku": "SP03 — Dạ Dày HT Hằng Thu",
        "final_name": "261124 HTPM Dạ Dày HT êm thượng vị ngủ ngon trọn giấc final.mp4",
        "cutout_png": "SP_DA_DAY_HT_COMBO_CUTOUT.png",
        "accent_hex": "#B56400",
        "accent_dark": "#7A4100",
        "outfit_desc": "Bộ 09 — Áo sơ mi đũi linen cao cấp màu vàng bơ tươi sáng (butter yellow) phối quần culottes trắng kem tại bếp sáng",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 09]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a fresh butter-yellow premium linen three-quarter-sleeve shirt tucked into cream-white wide-leg culottes, neat low ponytail in a bright sunlit modern kitchen. "
        ),
        "hook_kicker": "ĐÃ KIÊNG CAY NÓNG MỖI NGÀY",
        "hook_hero": "Vẫn rát thượng vị?",
        "s4_kicker": "HỖ TRỢ BẢO VỆ NIÊM MẠC DẠ DÀY",
        "s4_hero": "Dạ Dày HT",
        "end_kicker": "CHĂM SÓC DẠ DÀY",
        "end_title": "Dạ Dày HT",
        "end_tagline": "GIẢM Ợ CHUA · DỊU NÓNG RÁT · ÊM BỤNG",
        "cta_text": "Nhắn ngay “DẠ DÀY” · Tư vấn lộ trình êm bụng",
        "legal_text": "Thực phẩm bảo vệ sức khỏe · Không phải là thuốc, không thay thế thuốc chữa bệnh",
        "slides": {
            "s2_header": "🔥 Dấu hiệu trào ngược &amp; dư acid dạ dày",
            "s2_rows": [
                "Ợ hơi, ợ chua, nóng rát vùng thượng vị",
                "Đầy bụng, chướng hơi, khó tiêu sau bữa ăn",
                "Khó chịu tăng lên khi nằm khiến đêm mất ngủ",
            ],
            "s3_pill": "Chăm êm niêm mạc mỗi ngày cùng<br/>Thực Phẩm Dạ Dày HT Hằng Thu",
            "s4_header": "✨ Cơ chế kép xoa dịu từ thảo mộc",
            "s4_rows": [
                "Hỗ trợ trung hòa &amp; giảm acid dịch vị dư thừa",
                "Làm dịu nhanh cảm giác nóng rát, ợ chua",
                "Bao phủ bảo vệ niêm mạc dạ dày êm khỏe",
            ],
            "s5_header": "🌿 Bộ tứ thảo dược vàng cho dạ dày",
            "s5_rows": [
                "Chiết xuất Dạ cẩm: Trung hòa acid, dịu rát",
                "Nghệ đen &amp; Nghệ vàng: Hỗ trợ lành niêm mạc",
                "Hoàng liên &amp; Mộc hương: Giảm đầy hơi, chướng bụng",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Đã kiêng đồ cay nóng kỹ lắm rồi, vậy mà cứ mỗi buổi chiều hay lúc nằm xuống vùng thượng vị của chị vẫn nóng rát?",
                ["cay nóng", "thượng vị", "nóng rát"],
                [
                    ('Đã kiêng đồ cay nóng <span class="cap-kw">kỹ lắm rồi,</span>', 0.46),
                    ('Sao vùng thượng vị vẫn <span class="cap-kw">âm ỉ nóng rát?</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Ợ hơi, ợ chua, đầy bụng khó tiêu kéo dài là dấu hiệu acid dư thừa đang làm tổn thương lớp niêm mạc dạ dày mỗi ngày.",
                ["ợ chua", "đầy bụng", "niêm mạc"],
                [
                    ('Ợ hơi, ợ chua, <span class="cap-kw">đầy chướng khó tiêu</span>', 0.46),
                    ('Báo hiệu <span class="cap-kw">niêm mạc dạ dày</span> đang tổn thương.', 1.00),
                ],
            ),
            (
                "vo_03",
                "Bên cạnh ăn uống đúng giờ, chị chọn bảo vệ chiếc bụng êm cùng Dạ Dày Hắt Tê Hằng Thu.",
                ["đúng giờ", "dạ dày", "hằng thu"],
                [
                    ('Kết hợp ăn đúng giờ &amp; <span class="cap-kw">chăm bụng từ gốc,</span>', 0.48),
                    ('Chị chọn đồng hành cùng <span class="cap-kw">Dạ Dày HT Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Dạ Dày Hắt Tê hỗ trợ trung hòa a xít dịch vị, làm dịu cơn nóng rát thượng vị và bảo vệ niêm mạc dạ dày êm khỏe.",
                ["trung hòa", "thượng vị", "êm khỏe"],
                [
                    ('<span class="cap-kw">Dạ Dày HT</span> hỗ trợ giảm acid dịch vị,', 0.48),
                    ('Làm dịu nóng rát &amp; <span class="cap-kw">bảo vệ niêm mạc êm.</span>', 1.00),
                ],
            ),
            (
                "vo_05",
                "Sự hòa quyện giữa Dạ cẩm, Nghệ đen, Hoàng liên và Mộc hương giúp giảm đầy chướng để bữa cơm tròn vị, tối ngủ ngon giấc.",
                ["dạ cẩm", "nghệ", "ngon giấc"],
                [
                    ('Hòa quyện <span class="cap-kw">Dạ cẩm, Nghệ đen, Hoàng liên</span>', 0.50),
                    ('Giúp bữa cơm tròn vị, <span class="cap-kw">đêm ngủ trọn giấc.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Dạ Dày để Hằng Thu tư vấn chi tiết theo đúng tình trạng của chị nhé.",
                ["dạ dày", "hằng thu", "tư vấn"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot in a bright sunlit modern kitchen dining nook holding a glass of warm water while placing one hand gently over her upper stomach with mild epigastric discomfort. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving bright airy warm cream-and-butter-yellow bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle push-in in the sunlit kitchen nook as she holds the glass of warm water and touches her upper stomach thoughtfully.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K clean medical-aesthetic 3D CGI metaphor: soothing golden herbal honey-likeprotective gel gently coating and calming a luminous translucent wave surface in warm golden light, 100% tasteful non-anatomical luxury aesthetic.",
                "vid_prompt": "Smooth 3D golden soothing herbal essence flowing gently and calming luminous warm waves in serene light.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a sunlit dining room with fresh wholesome food; Chị Hằng in her butter-yellow linen shirt smiles warmly while holding the exact Dạ Dày HT Hằng Thu box and bottle from the second reference image at chest-to-waist height.",
                "vid_prompt": "Warm graceful dolly-in as she smiles reassuringly with closed lips while holding the Dạ Dày HT Hằng Thu box and bottle steadily.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact Dạ Dày HT Hằng Thu box and bottle from the reference image in the lower-middle third (Y=52%..85%) on a warm cream-and-amber marble podium bathed in golden morning light. Keep upper half (Y=0..46%) airy cream-gold bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the Dạ Dày HT box and bottle on the warm marble podium as golden light particles shimmer.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro herbal photography: fresh golden turmeric slices, Dạ cẩm leaves, Hoàng liên, and Mộc hương roots arranged beside a warm cup of herbal essence on cream stone in golden sunbeams.",
                "vid_prompt": "Sensory slow-motion macro slider across golden turmeric slices, Dạ cẩm herbs, and warm sunlit herbal essence.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng in her butter-yellow linen shirt gracefully in the LEFT half (X=5%..50%, head below Y=28%), smiling radiantly while presenting the Dạ Dày HT Hằng Thu box and bottle on a cream marble counter in the lower-left foreground; bright warm cream-gold right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling radiantly beside the Dạ Dày HT box in warm golden bokeh.",
            },
        ],
    },

    # =========================================================================
    # V09 (Ngày 10) — SP02: Viên Đặt LT Plus (Góc nhìn Tuổi 35–40+)
    # =========================================================================
    {
        "vid_code": "V09",
        "day_code": "Ngay_10_0312",
        "date_key": "2026-12-03",
        "sku": "SP02 — Viên Đặt Phụ Khoa LT Plus (Tuổi 35–40+)",
        "final_name": "261124 HTPM viên đặt LT Plus sạch dịch nhầy giữ ẩm tuổi 35 final.mp4",
        "cutout_png": "SP_LT_PLUS_COMBO_CUTOUT.png",
        "accent_hex": "#C91860",
        "accent_dark": "#82093B",
        "outfit_desc": "Bộ 10 — Áo khoác tweed dáng ngắn màu hồng phấn viền ánh kim phối chân váy xếp ly trắng trên sofa kem sang trọng",
        "outfit_lock": (
            "[DAILY OUTFIT SWAP LOCK — LOOK 10]: COMPLETELY REPLACE the beige knit cardigan from the reference photo with "
            "a chic pastel-pink cropped tweed jacket with subtle gold trim over a white silk camisole and pleated white skirt, glamorous soft water-wave curls. "
        ),
        "hook_kicker": "PHỤ NỮ BƯỚC QUA TUỔI 35 - 40",
        "hook_hero": "Rửa ngoài vẫn khô?",
        "s4_kicker": "TÁC ĐỘNG KÉP SẠCH ÊM & GIỮ ẨM",
        "s4_hero": "LT Plus Hằng Thu",
        "end_kicker": "VIÊN ĐẶT PHỤ KHOA",
        "end_title": "LT Plus",
        "end_tagline": "SẠCH DỊCH NHẦY · GIỮ ẨM · CÂN BẰNG PH",
        "cta_text": "Nhắn ngay “LT PLUS” · Tư vấn riêng tư tuổi 35+",
        "legal_text": "Hộp 15 viên thảo dược thiên nhiên · Chăm sóc dịu êm & bảo mật cho phái đẹp",
        "slides": {
            "s2_header": "🌷 Vì sao phụ nữ 35+ cần chăm từ bên trong?",
            "s2_rows": [
                "Dịch nhầy tồn đọng sâu bên trong gây mùi",
                "Niêm mạc sau tuổi 35 mỏng &amp; dễ khô rát hơn",
                "Chỉ rửa bên ngoài không cân bằng được độ pH",
            ],
            "s3_pill": "Chăm sóc kép tuổi 35+ cùng<br/>Viên Đặt LT Plus Hằng Thu",
            "s4_header": "✨ Tác động kép khác biệt của LT Plus",
            "s4_rows": [
                "Hỗ trợ đào thải dịch nhầy &amp; kháng khuẩn êm",
                "Khử mùi khó chịu, giảm ngứa rát vùng kín",
                "Song hành duy trì độ ẩm &amp; độ pH tự nhiên",
            ],
            "s5_header": "🌿 Thảo dược tuyển chọn nâng niu niêm mạc",
            "s5_rows": [
                "Hoàng bá &amp; Kim ngân hoa: Sạch êm dịu nhẹ",
                "Trầu không &amp; Trà xanh: Thoáng mát tự nhiên",
                "Acid Lactic: Giữ ẩm mềm mại không khô căng",
            ],
        },
        "segments": [
            (
                "vo_01",
                "Bước qua tuổi ba mươi lăm, bốn mươi, vì sao chỉ chú ý làm sạch bên ngoài thôi chị vẫn thấy khô rát và kém thoải mái?",
                ["ba mươi lăm", "làm sạch", "khô rát"],
                [
                    ('Bước qua độ tuổi <span class="cap-kw">35 đến 40+,</span>', 0.44),
                    ('Sao chỉ rửa ngoài vẫn <span class="cap-kw">khô và kém thoải mái?</span>', 1.00),
                ],
            ),
            (
                "vo_02",
                "Ở độ tuổi này, dịch nhầy tồn đọng bên trong cộng thêm niêm mạc nhạy cảm khiến việc chỉ rửa ngoài khó giữ được sự cân bằng.",
                ["dịch nhầy", "nhạy cảm", "cân bằng"],
                [
                    ('Dịch nhầy bên trong kèm <span class="cap-kw">niêm mạc nhạy cảm</span>', 0.50),
                    ('Khiến chỉ rửa ngoài <span class="cap-kw">khó giữ được cân bằng.</span>', 1.00),
                ],
            ),
            (
                "vo_03",
                "Phụ nữ hiện đại thương bản thân đúng cách, chị chọn tác động kép từ Viên Đặt Phụ Khoa Lờ Tê Plus Hằng Thu.",
                ["hiện đại", "hằng thu"],
                [
                    ('Phụ nữ hiện đại <span class="cap-kw">thương mình đúng cách,</span>', 0.48),
                    ('Chị chọn <span class="cap-kw">Viên Đặt LT Plus Hằng Thu.</span>', 1.00),
                ],
            ),
            (
                "vo_04",
                "Lờ Tê Plus vừa hỗ trợ kháng khuẩn, làm sạch dịch nhầy và khử mùi hôi, vừa duy trì độ ẩm cùng pê hát tự nhiên thật êm ái.",
                ["kháng khuẩn", "dịch nhầy", "độ ẩm"],
                [
                    ('<span class="cap-kw">LT Plus</span> vừa làm sạch dịch nhầy, khử mùi,', 0.50),
                    ('Vừa duy trì <span class="cap-kw">độ ẩm &amp; pH tự nhiên</span> êm ái.', 1.00),
                ],
            ),
            (
                "vo_05",
                "Tinh chất Hoàng bá, Kim ngân hoa, Trầu không hòa quyện cùng A xít Lắc tích giúp nâng niu vùng nhạy cảm mềm mịn, không khô căng.",
                ["hoàng bá", "kim ngân hoa", "mềm mịn"],
                [
                    ('Tinh chất <span class="cap-kw">Hoàng bá, Kim ngân hoa, Trầu không</span>', 0.52),
                    ('Cùng Acid Lactic giữ ẩm <span class="cap-kw">không lo khô căng.</span>', 1.00),
                ],
            ),
            (
                "vo_06",
                "Nhắn ngay Lờ Tê Plus để Hằng Thu đồng hành giữ trọn sự tự tin tuổi ba mươi lăm cho chị nhé.",
                ["hằng thu", "tự tin", "ba mươi lăm"],
                [],
            ),
        ],
        "shots": [
            {
                "use_ch": True, "use_pr": False,
                "img_prompt": "Medium shot seated gracefully on a luxury cream-velvet sofa in a bright sunlit Parisian-style salon, looking poised and thoughtful. Frame her head and body strictly in the LOWER HALF (top of hair below Y=50%), leaving bright airy pastel blush-and-ivory sunlit bokeh in the upper 48% for the 3s top hook title.",
                "vid_prompt": "Slow gentle push-in on the cream-velvet sofa in warm morning light as she reflects calmly with poised elegance and closed lips.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K luxury feminine-care 3D CGI metaphor: twin ribbons of pure crystal cleansing water and luminous rose-silk moisture swirling harmoniously around a pale-pink lotus blossom, airy ivory-pink upper bokeh.",
                "vid_prompt": "Smooth 3D twin streams of crystal water and blush-pink silk swirling gracefully around a blooming pink lotus flower.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Medium shot in a sunlit luxury living room; Chị Hằng in her pastel-pink tweed jacket smiles radiantly while holding the exact pastel-pink LT PLUS HẰNG THU box and white bottle from the second reference image at chest-to-waist height.",
                "vid_prompt": "Warm graceful dolly-in as she smiles reassuringly with closed lips while holding the pastel-pink LT PLUS box and white bottle steadily.",
            },
            {
                "use_ch": False, "use_pr": True,
                "img_prompt": "Luxury commercial product hero packshot: place the exact pastel-pink LT PLUS HẰNG THU box and white bottle from the reference image in the lower-middle third (Y=54%..85%) on a luminous rose-quartz marble podium with crystal water ripples and pink petals. Keep upper half (Y=0..46%) airy blush-ivory bokeh.",
                "vid_prompt": "Slow luxury tabletop orbit and push-in on the pastel-pink LT PLUS box and white bottle on the rose-quartz podium as water ripples glisten.",
            },
            {
                "use_ch": False, "use_pr": False,
                "img_prompt": "Vertical 9:16 4K macro botanical photography: golden Hoàng bá bark, blooming Kim ngân hoa flowers, fresh green Trầu không leaves, and luminous moisture droplets on white-and-rose marble in golden morning sun.",
                "vid_prompt": "Sensory slow-motion macro slider across Hoàng bá bark, Kim ngân hoa flowers, dewy Trầu không leaves, and crystal moisture pearls.",
            },
            {
                "use_ch": True, "use_pr": True,
                "img_prompt": "Commercial Brand End-Card composition: position Chị Hằng in her pastel-pink tweed jacket gracefully in the LEFT half (X=5%..50%, head below Y=28%), smiling radiantly while presenting the pastel-pink LT PLUS box and white bottle on a white marble counter in the lower-left foreground; bright airy blush-cream right half.",
                "vid_prompt": "Poised luxury End-Card slow push-in as she stands on the left smiling radiantly beside the LT PLUS box and bottle in sunlit bokeh.",
            },
        ],
    },
]
