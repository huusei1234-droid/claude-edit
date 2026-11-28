# -*- coding: utf-8 -*-
"""
Master Specification for all 13 remaining HTPM Reels (#02 -> #14) from hanh.sung.suong.
Video #01 (v01_cat_bao_quy_dau) is already completed & delivered (V5).
"""

VIDEOS_SPEC = [
    {
        "idx": 2,
        "slug": "v02_quan_he_nhieu_can_tinh_trung",
        "final_name": "261126 HTPM quan hệ nhiều có làm cạn tinh trùng không final.mp4",
        "hook_lines": ["QUAN HỆ NHIỀU", "CÓ LÀM CẠN", "TINH TRÙNG KHÔNG?"],
        "spoken_script": (
            "Quan hệ nhiều có làm cạn tinh trùng không các anh? "
            "Lượng tinh dịch và số lượng tinh trùng là hai chỉ số hoàn toàn khác nhau. "
            "Xuất tinh thường xuyên không đồng nghĩa chắc chắn bị vô sinh đâu. "
            "Đừng tự đoán qua mắt thường, đang mong con thì đi khám xét nghiệm nhé!"
        ),
        "behind_kw_anchor": ["không", "đồng", "nghĩa"],
        "behind_kw_lines": ["KHÔNG ĐỒNG NGHĨA", "BỊ VÔ SINH!"],
        "mascot_mode": "sperm_droplet",
        "hook_card": {
            "badge": "💧 MẮT THƯỜNG?",
            "caption": "ÍT DỊCH = CẠN TINH?",
            "prompt": "Clean editorial macro medical photography in a bright clinic lab: a crystal-clear glass specimen cup with a glowing aqua droplet icon beside a sleek question mark token on a clean white medical counter, warm natural hospital lighting, zero text, zero letters."
        },
        "broll_cards": [
            {
                "tag": "PHÂN BIỆT RÕ",
                "tag_color": "blue",
                "head": "DỊCH ≠ TINH TRÙNG",
                "desc": "Hai chỉ số hoàn toàn khác nhau",
                "prompt": "Clean bright medical laboratory photography: a modern optical microscope on a white lab desk next to two neat glass test tubes under warm clinic light, crisp shallow depth of field, zero text, zero letters."
            },
            {
                "tag": "✔ CHUẨN Y KHOA",
                "tag_color": "green",
                "head": "XÉT NGHIỆM TINH DỊCH",
                "desc": "Đang mong con nên kiểm tra sớm",
                "prompt": "Authentic Vietnamese male doctor in a crisp white lab coat warmly consulting a young Vietnamese couple sitting across a bright modern fertility clinic desk, clean medical folder, candid natural lighting, zero text."
            }
        ]
    },
    {
        "idx": 3,
        "slug": "v03_cuong_tot_vi_sao_kho_co_con",
        "final_name": "261126 HTPM cương vẫn tốt vì sao vẫn khó có con final.mp4",
        "hook_lines": ["CƯƠNG VẪN TỐT", "VÌ SAO VẪN", "KHÓ CÓ CON?"],
        "spoken_script": (
            "Vẫn gần gũi đều, cương vẫn tốt, sao hai vợ chồng mãi chưa có con? "
            "Các anh nhớ nhé, khả năng cương không cho biết số lượng, độ di động hay hình dạng tinh trùng bên trong. "
            "Muốn biết chính xác phải xét nghiệm tinh dịch đồ. "
            "Chậm có con thì hai vợ chồng cùng đi kiểm tra sớm nhé!"
        ),
        "behind_kw_anchor": ["khả", "năng", "cương"],
        "behind_kw_lines": ["CƯƠNG TỐT CHƯA CHẮC", "TINH BINH KHỎE!"],
        "mascot_mode": "sperm_ovum",
        "hook_card": {
            "badge": "❓ CHẬM CÓ CON",
            "caption": "CƯƠNG TỐT = ĐỦ KHỎE?",
            "prompt": "Warm candid lifestyle photography of a thoughtful young Vietnamese husband and wife sitting together on a bright modern cream sofa holding a tiny pair of baby shoes with gentle hope, natural window light, zero text."
        },
        "broll_cards": [
            {
                "tag": "BÊN TRONG",
                "tag_color": "blue",
                "head": "SỐ LƯỢNG & DI ĐỘNG",
                "desc": "Mắt thường không thể nhìn thấy",
                "prompt": "Photorealistic medical laboratory technician in white coat and blue gloves looking through a high-precision clinical microscope in a sunlit modern fertility lab, clean editorial photography, zero text."
            },
            {
                "tag": "✔ LỜI KHUYÊN",
                "tag_color": "green",
                "head": "KHÁM CẢ HAI VỢ CHỒNG",
                "desc": "Làm tinh dịch đồ để yên tâm",
                "prompt": "Authentic Vietnamese male fertility specialist doctor in white coat smiling and explaining a visual diagram without words to a smiling young Vietnamese husband and wife at a bright clinic desk, zero text."
            }
        ]
    },
    {
        "idx": 4,
        "slug": "v04_bi_quai_bi_co_vo_sinh_khong",
        "final_name": "261126 HTPM từng bị quai bị có bị vô sinh nam không final.mp4",
        "hook_lines": ["BỊ QUAI BỊ", "CÓ ẢNH HƯỞNG", "SINH SẢN KHÔNG?"],
        "spoken_script": (
            "Các anh từng bị quai bị thì có chắc chắn bị vô sinh không? "
            "Quai bị gây biến chứng viêm sưng tinh hoàn mới có nguy cơ ảnh hưởng sinh sản, chứ từng mắc quai bị không đồng nghĩa chắc chắn vô sinh đâu. "
            "Đi khám hãy nói rõ lúc đó có sưng đau một hay hai bên nhé!"
        ),
        "behind_kw_anchor": ["không", "đồng", "nghĩa"],
        "behind_kw_lines": ["KHÔNG PHẢI AI MẮC", "CŨNG VÔ SINH!"],
        "mascot_mode": "sperm_shield",
        "hook_card": {
            "badge": "⚠ BIẾN CHỨNG",
            "caption": "SƯNG ĐAU KHI QUAI BỊ?",
            "prompt": "Clean editorial medical portrait of a young Asian man in a light casual shirt gently touching his swollen jawline with a cold compress pack in a bright modern clinic room, natural lighting, zero text."
        },
        "broll_cards": [
            {
                "tag": "CẦN LƯU Ý",
                "tag_color": "red",
                "head": "THEO DÕI VIÊM SƯNG",
                "desc": "Một bên hay cả hai bên",
                "prompt": "Clean medical photography of a digital clinical thermometer, a soft blue medical ice pack, and a silver stethoscope arranged neatly on a bright white hospital desk, shallow depth of field, zero text."
            },
            {
                "tag": "✔ KHÁM SỚM",
                "tag_color": "green",
                "head": "KHAI RÕ TIỀN SỬ BỆNH",
                "desc": "Đừng chủ quan khi sưng đau",
                "prompt": "Authentic Vietnamese male urologist in a white lab coat taking notes on a clean clipboard while listening attentively to a male patient across a warm sunlit clinic desk, zero text."
            }
        ]
    },
    {
        "idx": 5,
        "slug": "v05_chua_duoc_3_phut_da_xuat_tinh",
        "final_name": "261126 HTPM chưa được 3 phút đã xuất tinh có sao không final.mp4",
        "hook_lines": ["CHƯA ĐƯỢC 3 PHÚT", "ĐÃ XUẤT TINH", "CÓ SAO KHÔNG?"],
        "spoken_script": (
            "Chưa được ba phút đã xuất tinh, vậy là yếu sinh lý nặng rồi sao? "
            "Một vài lần nhanh do hồi hộp hay căng thẳng chưa đủ kết luận mắc bệnh đâu các anh. "
            "Nếu lặp lại liên tục và khó kiểm soát, hãy đi khám chuyên khoa, tuyệt đối đừng tự mua thuốc trôi nổi nhé!"
        ),
        "behind_kw_anchor": ["đừng", "tự", "mua"],
        "behind_kw_lines": ["ĐỪNG TỰ MUA", "THUỐC TRÔI NỔI!"],
        "mascot_mode": "sperm_timer",
        "hook_card": {
            "badge": "⏱ DƯỚI 3 PHÚT",
            "caption": "DO HỒI HỘP HAY BỆNH?",
            "prompt": "Editorial close-up photography of a sleek metallic silver mechanical stopwatch resting on a crisp white bedside table under soft warm morning light, shallow depth of field, zero text, zero numbers."
        },
        "broll_cards": [
            {
                "tag": "ĐÁNH GIÁ ĐÚNG",
                "tag_color": "blue",
                "head": "MỚI BỊ HAY LẶP LẠI?",
                "desc": "Ghi nhận tần suất & độ kiểm soát",
                "prompt": "Authentic Vietnamese male doctor in white coat holding a pen over a neat blank calendar notebook while consulting a male patient in a bright modern clinic office, warm lighting, zero text."
            },
            {
                "tag": "✕ CẤM TUYỆT ĐỐI",
                "tag_color": "red",
                "head": "TRÁNH THUỐC TRÔI NỔI",
                "desc": "Không rõ nguồn gốc rất nguy hiểm",
                "prompt": "Clean medical warning photography: unlabelled generic capsule pills scattered beside a glossy red circular X prohibition token on a white clinic counter, sharp focus, bright lighting, zero text."
            }
        ]
    },
    {
        "idx": 6,
        "slug": "v06_muon_gan_vo_nhung_cuong_khong_noi",
        "final_name": "261126 HTPM muốn gần vợ nhưng cương không nổi phải làm sao final.mp4",
        "hook_lines": ["MUỐN GẦN VỢ", "NHƯNG CƯƠNG", "KHÔNG NỔI?"],
        "spoken_script": (
            "Rất muốn gần vợ mà cơ thể lại không nghe lời phải làm sao? "
            "Các anh tách riêng hai chuyện nhé: ham muốn là cảm xúc yêu thương, còn cương là phản ứng mạch máu của cơ thể. "
            "Đừng để một lần trục trặc thành hiểu lầm hết yêu, hãy chia sẻ thật với vợ và khám sức khỏe nhé!"
        ),
        "behind_kw_anchor": ["tách", "riêng", "hai"],
        "behind_kw_lines": ["HAM MUỐN KHÁC", "PHẢN ỨNG CƠ THỂ!"],
        "mascot_mode": "heart_pulse",
        "hook_card": {
            "badge": "❤ TÂM LÝ & CƠ THỂ",
            "caption": "CƠ THỂ CHƯA ĐÁP ỨNG",
            "prompt": "Candid warm indoor photography of a thoughtful Asian husband sitting on the edge of a cozy sunlit bed while his supportive wife gently rests her hand on his shoulder, empathetic atmosphere, zero text."
        },
        "broll_cards": [
            {
                "tag": "CHIA SẺ THẬT",
                "tag_color": "blue",
                "head": "TRÁNH HIỂU LẦM HẾT YÊU",
                "desc": "Nói rõ với bạn đời để thấu hiểu",
                "prompt": "Warm close-up photography of a husband and wife holding hands affectionately across a sunlit wooden coffee table in a bright modern living room, natural candid emotion, zero text."
            },
            {
                "tag": "✔ KIỂM TRA",
                "tag_color": "green",
                "head": "KHÁM MẠCH MÁU & NỘI TIẾT",
                "desc": "Tìm đúng nguyên nhân thể chất",
                "prompt": "Authentic Vietnamese doctor in white coat measuring blood pressure on a male patient's arm in a bright modern medical clinic, clean trustworthy hospital lighting, zero text."
            }
        ]
    },
    {
        "idx": 7,
        "slug": "v07_cang_tu_xu_cang_de_teo",
        "final_name": "261126 HTPM càng tự xử càng dễ bị teo có đúng không final.mp4",
        "hook_lines": ["CÀNG TỰ XỬ", "CÀNG DỄ BỊ TEO", "CÓ ĐÚNG KHÔNG?"],
        "spoken_script": (
            "Thấy nhỏ lại sau khi tự xử rồi sợ bị teo dần hả các anh? "
            "Thực ra sau xuất tinh, cơ thể trở về trạng thái mềm nghỉ ngơi nên trông nhỏ hơn lúc cương, chứ không hề mất đi kích thước thật. "
            "Đừng tự dọa mình nhé, chỉ cần đi khám nếu có đau hay tổn thương kéo dài thôi!"
        ),
        "behind_kw_anchor": ["không", "hề", "mất"],
        "behind_kw_lines": ["KHÔNG HỀ MẤT", "KÍCH THƯỚC THẬT!"],
        "mascot_mode": "sperm_shield",
        "hook_card": {
            "badge": "❓ LO BỊ TEO?",
            "caption": "HIỂU ĐÚNG SINH LÝ",
            "prompt": "Editorial portrait of a worried young Asian man looking thoughtfully into a bright bathroom mirror in morning sunlight, clean modern home interior, candid natural expression, zero text."
        },
        "broll_cards": [
            {
                "tag": "SINH LÝ TỰ NHIÊN",
                "tag_color": "blue",
                "head": "TRẠNG THÁI NGHỈ NGƠI",
                "desc": "Máu rút về sau khi xuất tinh",
                "prompt": "Clean bright medical photography of a doctor's hands holding a sleek blue and red vascular blood-flow anatomical model on a white clinic desk, crisp studio light, zero text."
            },
            {
                "tag": "✔ KHI NÀO KHÁM?",
                "tag_color": "green",
                "head": "KHI ĐAU HOẶC TỔN THƯƠNG",
                "desc": "Kiểm tra trực tiếp để yên tâm",
                "prompt": "Friendly Vietnamese male urologist in crisp white lab coat giving a reassuring thumbs-up gesture while talking to a relieved male patient across a bright clinic desk, zero text."
            }
        ]
    },
    {
        "idx": 8,
        "slug": "v08_an_toi_cuong_tot_hon_khong",
        "final_name": "261126 HTPM ăn tỏi để cương tốt hơn có chắc không final.mp4",
        "hook_lines": ["ĂN NHIỀU TỎI", "GIÚP CƯƠNG TỐT HƠN", "CÓ CHẮC KHÔNG?"],
        "spoken_script": (
            "Ăn thật nhiều tỏi là hết ngay chuyện khó cương, có thật không các anh? "
            "Chế độ ăn lành mạnh có hỗ trợ tuần hoàn máu, nhưng không có món ăn đơn lẻ nào tự chữa khỏi rối loạn cương đâu. "
            "Đừng chỉ trông chờ một món ăn, hãy tập luyện, ngủ đủ và khám sức khỏe toàn diện nhé!"
        ),
        "behind_kw_anchor": ["không", "có", "món"],
        "behind_kw_lines": ["MỘT MÓN ĂN", "KHÔNG THỂ TRỊ BỆNH!"],
        "mascot_mode": "heart_pulse",
        "hook_card": {
            "badge": "🧄 LỜI ĐỒN?",
            "caption": "ĂN TỎI LÀ KHỎE NGAY?",
            "prompt": "Crisp commercial food photography of fresh organic white garlic bulbs and peeled cloves in a ceramic bowl on a bright clean marble kitchen counter in morning sunlight, shallow depth of field, zero text."
        },
        "broll_cards": [
            {
                "tag": "CHỈ HỖ TRỢ",
                "tag_color": "red",
                "head": "KHÔNG THAY THẾ PHÁC ĐỒ",
                "desc": "Đừng tin mẹo truyền miệng đơn lẻ",
                "prompt": "Balanced healthy Mediterranean meal plate with grilled salmon, avocado, greens, and garlic on a sunlit dining table beside a stethoscope, bright editorial health photography, zero text."
            },
            {
                "tag": "✔ GIẢI PHÁP BỀN",
                "tag_color": "green",
                "head": "TẬP LUYỆN & KHÁM TỔNG QUÁT",
                "desc": "Cải thiện mạch máu từ gốc",
                "prompt": "Energetic fit Vietnamese man in athletic sportswear jogging outdoors in a sunny green park in early morning golden light, healthy lifestyle photography, zero text."
            }
        ]
    },
    {
        "idx": 9,
        "slug": "v09_con_yeu_vo_sao_it_muon_gan_gui",
        "final_name": "261126 HTPM còn yêu vợ sao lại ít muốn gần gũi final.mp4",
        "hook_lines": ["VẪN THƯƠNG VỢ", "SAO GẦN ĐÂY", "ÍT MUỐN GẦN GŨI?"],
        "spoken_script": (
            "Vẫn thương vợ nhưng gần đây lại ít muốn gần gũi là vì sao các anh? "
            "Ham muốn giảm còn do căng thẳng kéo dài, thiếu ngủ, dùng thuốc hoặc suy giảm sức khỏe nội tiết chứ không chỉ tình cảm. "
            "Đừng im lặng để hai người tự đoán, hãy chia sẻ cùng vợ và đi bác sĩ kiểm tra sớm nhé!"
        ),
        "behind_kw_anchor": ["căng", "thẳng"],
        "behind_kw_lines": ["DO CĂNG THẲNG", "& SỨC KHỎE NỘI TIẾT!"],
        "mascot_mode": "heart_pulse",
        "hook_card": {
            "badge": "💤 ÁP LỰC NGẦM",
            "caption": "MỆT MỎI LÀM GIẢM LỬA",
            "prompt": "Candid lifestyle photo of a tired Asian businessman in a dress shirt rubbing his temples in front of a laptop late at night in a warm home office, realistic shallow depth of field, zero text."
        },
        "broll_cards": [
            {
                "tag": "ĐỪNG IM LẶNG",
                "tag_color": "blue",
                "head": "TÂM SỰ CÙNG BẠN ĐỜI",
                "desc": "Vợ chồng cùng tìm hiểu nguyên nhân",
                "prompt": "Warm sunlit lifestyle photo of an affectionate Vietnamese couple sitting close together with tea cups by a bright window talking openly and smiling gently, zero text."
            },
            {
                "tag": "✔ KHÁM NỘI TIẾT",
                "tag_color": "green",
                "head": "KIỂM TRA SỚM TẠI PHÒNG KHÁM",
                "desc": "Đánh giá giấc ngủ, thuốc & hormone",
                "prompt": "Authentic Vietnamese male doctor in white lab coat reviewing clean lab test tubes and consulting a male patient in a modern bright hospital room, zero text."
            }
        ]
    },
    {
        "idx": 10,
        "slug": "v10_vua_xuat_ra_da_mem_co_yeu_khong",
        "final_name": "261126 HTPM vừa xuất ra đã mềm có phải yếu sinh lý final.mp4",
        "hook_lines": ["VỪA XUẤT TINH", "ĐÃ MỀM NGAY", "CÓ PHẢI YẾU KHÔNG?"],
        "spoken_script": (
            "Vừa xuất tinh xong đã mềm ngay, các anh tưởng mình bị yếu đi à? "
            "Thực ra mất cương sau khi xuất tinh là phản ứng hồi phục hoàn toàn bình thường của cơ thể. "
            "Chỉ đáng lo khi chưa xuất, mới gần gũi hai ba phút đã mềm giữa chừng. Phân biệt rõ để khỏi lo nhé!"
        ),
        "behind_kw_anchor": ["phản", "ứng", "hồi"],
        "behind_kw_lines": ["PHẢN ỨNG CƠ THỂ", "BÌNH THƯỜNG!"],
        "mascot_mode": "sperm_droplet",
        "hook_card": {
            "badge": "🔋 GIAI ĐOẠN NGHỈ",
            "caption": "SAU XUẤT TINH CẦN HỒI SỨC",
            "prompt": "Clean minimalist photography of a glowing green glass battery icon and a calm water ripple bowl on a bright spa-like white clinic table, warm natural morning light, zero text."
        },
        "broll_cards": [
            {
                "tag": "✔ BÌNH THƯỜNG",
                "tag_color": "green",
                "head": "MỀM SAU KHI ĐÃ XUẤT",
                "desc": "Cơ chế trơ sinh lý tự nhiên",
                "prompt": "Relaxed smiling Asian man in a clean white cotton shirt stretching comfortably in bright morning sunlight by a bedroom window, healthy rested expression, zero text."
            },
            {
                "tag": "⚠ ĐÁNG LƯU Ý",
                "tag_color": "red",
                "head": "XÌU SỚM KHI CHƯA XUẤT",
                "desc": "Mới 2–3 phút đã mềm cần đi khám",
                "prompt": "Authentic Vietnamese male urologist doctor in white coat pointing to a clean anatomical vascular chart while advising a male patient at a bright clinic desk, zero text."
            }
        ]
    },
    {
        "idx": 11,
        "slug": "v11_tac_hai_xem_phim_nhay_cam_qua_nhieu",
        "final_name": "261126 HTPM tác hại xem phim nhạy cảm quá nhiều ở nam giới final.mp4",
        "hook_lines": ["XEM PHIM NHẠY CẢM", "QUÁ NHIỀU GÂY HẠI", "NHƯ THẾ NÀO?"],
        "spoken_script": (
            "Xem phim nhạy cảm quá nhiều gây ra bốn tác hại gì cho nam giới? "
            "Một là tốn thời gian thức khuya. Hai là dễ rối loạn cương cứng. "
            "Ba là bị trơ, giảm cảm xúc khi gần gũi thật. Bốn là khó xuất hoặc xuất muộn bất thường. "
            "Anh nào đang xem quá nhiều hãy điều chỉnh ngay nhé!"
        ),
        "behind_kw_anchor": ["giảm", "cảm", "xúc"],
        "behind_kw_lines": ["TRƠ CẢM XÚC", "KHI GẦN GŨI THẬT!"],
        "mascot_mode": "sperm_timer",
        "hook_card": {
            "badge": "📵 CẢNH BÁO",
            "caption": "LẠM DỤNG KÍCH THÍCH ẢO",
            "prompt": "Moody yet clean editorial photography of a smartphone lying face-down on a wooden nightstand beside a red circular prohibition X token in soft dim bedroom lamp light, zero text."
        },
        "broll_cards": [
            {
                "tag": "✕ 4 HỆ LỤY",
                "tag_color": "red",
                "head": "RỐI LOẠN CƯƠNG & CẢM XÚC",
                "desc": "Mất kết nối thật với bạn đời",
                "prompt": "Candid photo of an exhausted young Asian man rubbing his eyes late at night with blue smartphone glow on his face in a dark bedroom, realistic cinema lighting, zero text."
            },
            {
                "tag": "✔ CAI KÍCH THÍCH ẢO",
                "tag_color": "green",
                "head": "NGỦ SỚM & VẬN ĐỘNG THẬT",
                "desc": "Khôi phục phản xạ tự nhiên",
                "prompt": "Happy healthy Vietnamese couple jogging together outdoors in bright morning park sunshine, energetic natural smiles, crisp commercial photography, zero text."
            }
        ]
    },
    {
        "idx": 12,
        "slug": "v12_uong_bia_truoc_khi_gan_gui",
        "final_name": "261126 HTPM uống bia trước khi gần gũi có giúp lâu hơn không final.mp4",
        "hook_lines": ["UỐNG BIA RƯỢU", "TRƯỚC KHI YÊU", "CÓ LÂU HƠN KHÔNG?"],
        "spoken_script": (
            "Uống bia trước khi gần gũi có giúp kéo dài cuộc yêu hơn không? "
            "Rượu bia ức chế thần kinh và tuần hoàn, uống nhiều dễ gây khó cương, cương không đủ và mất kết nối cảm xúc với bạn đời. "
            "Đừng mượn bia rượu nhé, hãy rèn nhịp thở, tập kiểm soát và giữ cơ thể khỏe mạnh!"
        ),
        "behind_kw_anchor": ["ức", "chế", "thần"],
        "behind_kw_lines": ["BIA RƯỢU GÂY", "KHÓ CƯƠNG & XÌU SỚM!"],
        "mascot_mode": "beer_warning",
        "hook_card": {
            "badge": "🍺 SAI LẦM",
            "caption": "MƯỢN BIA KÉO DÀI GIỜ?",
            "prompt": "Crisp commercial photography of a chilled glass mug of golden beer with foam on a wooden table right next to a glossy red circular X stop badge, bright natural lighting, zero text."
        },
        "broll_cards": [
            {
                "tag": "✕ TÁC ĐỘNG NGƯỢC",
                "tag_color": "red",
                "head": "ỨC CHẾ THẦN KINH & MẠCH MÁU",
                "desc": "Khó cương cứng, phản ứng chậm",
                "prompt": "Editorial photo of a dizzy tired Asian man pushing away a beer glass at a dinner table with a regretful expression, warm restaurant lighting, shallow depth of field, zero text."
            },
            {
                "tag": "✔ BỀN VỮNG",
                "tag_color": "green",
                "head": "RÈN NHỊP THỞ & SỨC BỀN",
                "desc": "Kiểm soát tự nhiên không cần cồn",
                "prompt": "Fit Vietnamese man in clean athletic wear practicing calm deep breathing and stretching on a sunlit modern balcony in the morning, fresh water bottle nearby, zero text."
            }
        ]
    },
    {
        "idx": 13,
        "slug": "v13_tu_xu_5_dau_hieu_mat_kiem_soat",
        "final_name": "261126 HTPM 5 dấu hiệu tự xử mất kiểm soát cần chú ý final.mp4",
        "hook_lines": ["TỰ XỬ KHÔNG XẤU", "NHƯNG 5 DẤU HIỆU", "NÀY CẦN CHÚ Ý!"],
        "spoken_script": (
            "Tự xử điều độ không xấu, nhưng năm dấu hiệu này các anh cần chú ý: "
            "một là làm liên tục dù cơ thể mệt; hai là thức khuya xem kích thích; ba là mất tập trung làm việc; "
            "bốn là đòi hỏi mức độ ngày càng mạnh; năm là ít cảm xúc khi gần bạn đời thật. Khó kiểm soát hãy gặp chuyên gia nhé!"
        ),
        "behind_kw_anchor": ["năm", "dấu", "hiệu"],
        "behind_kw_lines": ["5 DẤU HIỆU", "MẤT KIỂM SOÁT!"],
        "mascot_mode": "sperm_timer",
        "hook_card": {
            "badge": "⚠ 5 DẤU HIỆU",
            "caption": "VƯỢT NGƯỠNG ĐIỀU ĐỘ",
            "prompt": "Clean studio medical photography of a metallic balance scale tipping to one side with a red warning triangle token on a bright white clinic desk, crisp natural lighting, zero text."
        },
        "broll_cards": [
            {
                "tag": "✕ KIỆT SỨC",
                "tag_color": "red",
                "head": "MẤT TẬP TRUNG & THỨC KHUYA",
                "desc": "Giảm cảm xúc khi gần gũi thật",
                "prompt": "Candid daytime office photo of an unfocused exhausted young Asian man staring blankly past his laptop screen with a cup of cold coffee on a bright desk, zero text."
            },
            {
                "tag": "✔ HỖ TRỢ ĐÚNG",
                "tag_color": "green",
                "head": "GẶP BÁC SĨ CHUYÊN MÔN",
                "desc": "Lấy lại cân bằng sinh học khỏe mạnh",
                "prompt": "Warm trustworthy Vietnamese male doctor counselor in white coat speaking kindly with a young male patient in a bright private consultation room, zero text."
            }
        ]
    },
    {
        "idx": 14,
        "slug": "v14_5_thoi_quen_giam_phong_do_nam_gioi",
        "final_name": "261126 HTPM 5 thói quen âm thầm làm giảm phong độ nam giới final.mp4",
        "hook_lines": ["5 THÓI QUEN", "ÂM THẦM BÀO MÒN", "PHONG ĐỘ ĐÀN ÔNG!"],
        "spoken_script": (
            "Năm thói quen âm thầm làm giảm phong độ ở nam giới: "
            "thứ nhất là thức khuya liên tục; thứ hai là uống nhiều rượu bia làm cương kém ổn định; "
            "thứ ba là hút thuốc hại mạch máu; thứ tư là ngồi nhiều ít vận động; "
            "và thứ năm là căng thẳng kéo dài. Các anh thay đổi sớm nhé!"
        ),
        "behind_kw_anchor": ["thói", "quen"],
        "behind_kw_lines": ["5 THÓI QUEN", "BÀO MÒN PHONG ĐỘ!"],
        "mascot_mode": "beer_warning",
        "hook_card": {
            "badge": "🚨 5 THỦ PHẠM",
            "caption": "ÂM THẦM HẠI BẢN LĨNH",
            "prompt": "Clean flat-lay editorial health photography on a white surface: a crushed cigarette, a small glass of spirits, and a late-night alarm clock next to a glossy red X symbol, bright studio light, zero text."
        },
        "broll_cards": [
            {
                "tag": "✕ HẠI MẠCH MÁU",
                "tag_color": "red",
                "head": "THỨC KHUYA • BIA RƯỢU • THUỐC LÁ",
                "desc": "Ngồi lì & căng thẳng làm tụt nội tiết",
                "prompt": "Stressed Asian office worker sitting hunched at a desk surrounded by paperwork late in the evening, rubbing his neck with fatigue, realistic photography, zero text."
            },
            {
                "tag": "✔ PHỤC HỒI PHONG ĐỘ",
                "tag_color": "green",
                "head": "NGỦ ĐỦ • THỂ THAO • BỎ THUỐC",
                "desc": "Giữ mạch máu & sinh lực bền bỉ",
                "prompt": "Confident healthy Vietnamese man in his 30s smiling outdoors in morning sunlight wearing athletic polo shirt after a workout in a green park, crisp commercial portrait, zero text."
            }
        ]
    },
]
