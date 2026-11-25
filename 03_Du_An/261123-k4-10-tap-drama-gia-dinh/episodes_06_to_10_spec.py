"""
Screenplay & Shot-by-Shot Director Blueprint — Episodes 06 to 10 (`261123 K4 Batch`):
- Strict 180-degree spatial axis (`CHỐT KHÔNG GIAN`).
- Strict `<= 19 words` crisp Vietnamese cinema dialogue per shot + generous `9s–11s` Flow duration -> 0.00% mid-sentence cut-off!
- Interleaves Wide Establishing (`WIDE`), Crowd Public (`WIDE_CROWD`), Medium Action (`MED`), and Emotional Close-Up (`CU`).
"""

EPISODES_06_10 = {
    # =========================================================================
    # EP06: Khinh mẹ chú rể ăn mặc giản dị ngay tiệc cưới bố vợ mất trắng vốn đầu tư (15 scenes)
    # =========================================================================
    "ep06": {
        "title": "Khinh mẹ chú rể ăn mặc giản dị ngay tiệc cưới bố vợ mất trắng vốn đầu tư",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.22),
        "pivot_scene": "s06",
        "board_items": [
            ("CH-1: Cô Lan (Mẹ chú rể giản dị)", "colan_giandi"),
            ("CH-2: Tú (Chú rể)", "tu_chure"),
            ("CH-3: Lam (Cô dâu)", "lam_codau"),
            ("CH-4: Ông Khải (Bố cô dâu)", "khai"),
            ("BO-1: Sảnh tiệc cưới đông khách", "e06bo1"),
            ("BO-2: Bậc thềm hoa lễ đường", "e06bo2"),
        ],
        "shots": [
            ("s01", "WIDE_CROWD", "e06bo1", ["khai", "colan_giandi", "tu_chure"],
             "Sảnh tiệc cưới khách sạn sang trọng đông khách mời ngồi bàn tròn dưới đèn chùm pha lê: CH-1 (Ông Khải mặc vest) đứng bên trái nhìn khinh miệt CH-2 (Cô Lan mặc sơ mi kem giản dị) và chú rể CH-3 (Tú) bên phải.",
             "CH-1 chỉ tay chê bai bộ đồ giản dị của bà thông gia trước mặt quan khách.",
             "CH-1 (Ông Khải, giọng ngạo mạn khinh thường)",
             "Nhà cậu nghèo thế mà đòi kết thông gia à? Mẹ cậu ăn mặc chẳng bằng giúp việc nhà tôi!"),

            ("s02", "CU", "e06bo1", ["tu_chure", "colan_giandi"],
             "Trong sảnh tiệc cưới: chú rể CH-1 (Tú) bên phải nắm chặt tay bảo vệ mẹ CH-2 (Cô Lan) bên cạnh.",
             "CH-1 nhíu mày bức xúc lên tiếng bảo vệ mẹ ruột.",
             "CH-1 (Tú, giọng nén giận cứng rắn)",
             "Bố à, hôm nay là ngày cưới của tụi con, sao bố lại xúc phạm mẹ ruột con như thế?"),

            ("s03", "CU", "e06bo1", ["khai"],
             "Trong sảnh tiệc cưới: CH-1 (Ông Khải) bên trái hất cằm nhìn sang phải mỉa mai nặng lời hơn.",
             "CH-1 khoanh tay cười nhạt coi thường nhà trai.",
             "CH-1 (Ông Khải, giọng hách dịch trịch thượng)",
             "Tôi nói sai chắc? Con gái tôi lấy cậu, chẳng lẽ phải còng lưng gánh thêm bà mẹ quê này?"),

            ("s04", "CU", "e06bo1", ["colan_giandi", "tu_chure"],
             "Trong sảnh tiệc cưới: CH-1 (Cô Lan) bên phải vỗ nhẹ lên cánh tay con trai CH-2 (Tú) đầy bình thản.",
             "CH-1 giữ phong thái uy nghi trầm tĩnh ngăn con trai nổi nóng.",
             "CH-1 (Cô Lan, giọng điềm tĩnh nhẹ nhàng)",
             "Tú, con cứ bình tĩnh đứng đây, để mẹ nói chuyện rõ với ông thông gia."),

            ("s05", "CU", "e06bo1", ["khai"],
             "Trong sảnh tiệc cưới: CH-1 (Ông Khải) bên trái nhếch mép cười khẩy nhìn sang phải.",
             "CH-1 phẩy tay mỉa mai sự điềm tĩnh của bà thông gia.",
             "CH-1 (Ông Khải, giọng mỉa mai cay nghiệt)",
             "Nghèo thì cứ nhận là nghèo đi, đứng trước mặt tôi đừng có làm bộ thanh cao tự trọng!"),

            ("s06", "CU", "e06bo1", ["colan_giandi"],
             "Trong sảnh tiệc cưới dưới đèn chùm: CH-1 (Cô Lan) điềm nhiên rút điện thoại ra lệnh dứt khoát như nữ chủ tịch thực thụ.",
             "CH-1 nói ngắn gọn vào điện thoại rồi hạ máy nhìn thẳng Ông Khải.",
             "CH-1 (Cô Lan, giọng đanh thép quyền lực trên điện thoại)",
             "Alo trợ lý Năm à, khoản vốn rót vào công ty ông Khải sáng mai, hủy toàn bộ cho chị!"),

            ("s07", "WIDE_CROWD", "e06bo1", ["khai", "lam_codau", "colan_giandi"],
             "Giữa sảnh tiệc cưới đông khách: cô dâu CH-2 (Lam mặc váy cưới trắng) hốt hoảng bước tới giữa bố CH-1 (Ông Khải) bên trái và mẹ chồng CH-3 (Cô Lan) bên phải.",
             "CH-2 mở to mắt hoảng sợ hỏi mẹ chồng về khoản vốn của gia đình.",
             "CH-2 (Lam, giọng hốt hoảng hỏi mẹ chồng)",
             "Mẹ ơi! Có phải khoản vốn cứu công ty bố con không ạ? Thiếu nó công ty sập mất!"),

            ("s08", "CU", "e06bo1", ["colan_giandi"],
             "Trong sảnh tiệc cưới: cận cảnh CH-1 (Cô Lan) bên phải nhìn thẳng sang trái với ánh mắt sắc lạnh bản lĩnh.",
             "CH-1 gật đầu xác nhận thân phận nhà đầu tư đứng sau.",
             "CH-1 (Cô Lan, giọng đĩnh đạc rõ từng chữ)",
             "Đúng vậy, khoản vốn giải cứu công ty nhà con tháng này chính là tiền của mẹ rót xuống."),

            ("s09", "CU", "e06bo1", ["khai"],
             "Trong sảnh tiệc cưới: CH-1 (Ông Khải) bên trái tái mét mặt mày, môi run rẩy nhìn người phụ nữ áo trắng giản dị.",
             "CH-1 lùi nhẹ nửa bước, ánh mắt bàng hoàng sững sờ.",
             "CH-1 (Ông Khải, giọng lắp bắp bàng hoàng)",
             "Bà... chính bà là nhà đầu tư lớn đứng sau quỹ đầu tư đó thật sao?"),

            ("s10", "CU", "e06bo1", ["colan_giandi"],
             "Trong sảnh tiệc cưới: CH-1 (Cô Lan) bên phải ngẩng cao đầu nói thẳng đạo lý khiến cả bàn tiệc nín lặng.",
             "CH-1 nhìn thẳng Ông Khải tuyên bố đanh thép.",
             "CH-1 (Cô Lan, giọng trầm vang đầy tự tôn)",
             "Tôi ăn mặc giản dị thật, nhưng con trai tôi không phải món hàng để đem tiền ra cân đo!"),

            ("s11", "CU", "e06bo1", ["lam_codau"],
             "Trong sảnh tiệc cưới: cô dâu CH-1 (Lam mặc váy cưới trắng) bật khóc nhìn sang chú rể và mẹ chồng cầu xin.",
             "CH-1 rơi nước mắt nghẹn ngào xin lỗi thay bố.",
             "CH-1 (Lam, bật khóc nghẹn ngào cầu khẩn)",
             "Mẹ ơi, anh Tú ơi, con xin lỗi mà, xin hai người đừng hủy hôn lễ hôm nay nhé!"),

            ("s12", "CU", "e06bo1", ["colan_giandi", "tu_chure"],
             "Trong sảnh tiệc cưới: CH-1 (Cô Lan) nắm bàn tay con trai CH-2 (Tú) bên phải, nói lời cuối điềm tĩnh.",
             "CH-1 nhìn ông thông gia lần cuối rồi dắt tay con trai chuẩn bị rời sảnh.",
             "CH-1 (Cô Lan, giọng điềm đạm dứt khoát)",
             "Có những lời xúc phạm nói ra rồi xin lỗi cả đời cũng không lành lại. Về nhà thôi con!"),

            ("s13", "WIDE_CROWD", "e06bo1", ["khai", "lam_codau", "colan_giandi"],
             "Toàn cảnh sảnh tiệc cưới đông người: CH-3 (Cô Lan) hiên ngang bước đi về cửa lớn, bỏ lại CH-1 (Ông Khải) chết trân và CH-2 (Lam) bật khóc.",
             "CH-3 bước đi dứt khoát dưới ánh đèn chùm trước sự chứng kiến của quan khách.",
             None, ""),

            ("s14", "WIDE", "e06bo2", ["tu_chure"],
             "Bậc thềm hoa lễ đường đá hoa cương trắng: chú rể CH-1 (Tú mặc vest cưới đen) ngồi trầm ngâm một mình trên bậc thềm.",
             "CH-1 thở dài nhẹ rồi ngẩng đầu nhìn thẳng về phía khán giả.",
             None, ""),

            ("s15", "CU", "e06bo2", ["tu_chure"],
             "Trên bậc thềm lễ đường: cận cảnh CH-1 (Tú) nhìn thẳng ống kính đặt câu hỏi cho khán giả.",
             "CH-1 nhìn thẳng camera trò chuyện điềm tĩnh rồi khép môi tự nhiên.",
             "CH-1 (Tú, nhìn thẳng ống kính hỏi khán giả)",
             "Gặp nhà thông gia cậy tiền coi khinh mẹ ruột mình, mọi người thấy mẹ con Tú bước đi là đúng không ạ?"),
        ],
    },

    # =========================================================================
    # EP07: Khi sự quan tâm của chồng bị coi là phiền phức cái kết lạnh lòng (14 scenes)
    # =========================================================================
    "ep07": {
        "title": "Khi sự quan tâm của chồng bị coi là phiền phức cái kết lạnh lòng",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("piano_warm_family.mp3", 8.0, 0.22),
        "pivot_scene": "s07",
        "board_items": [
            ("CH-1: Tuấn (Người chồng nguội lạnh)", "tuan_polo"),
            ("CH-2: Linh (Cô vợ đi chơi khuya)", "linh_blazer"),
            ("BO-1: Phòng khách đêm khuya", "e07bo1"),
            ("BO-2: Góc cửa sổ đêm thành phố", "e07bo2"),
        ],
        "shots": [
            ("s01", "WIDE", "e07bo1", ["linh_blazer", "tuan_polo"],
             "Phòng khách căn hộ ánh đèn vàng đêm khuya: CH-1 (Linh mặc vest họa tiết xách túi) đứng bên trái chất vấn CH-2 (Tuấn mặc polo nâu) ngồi sofa bên phải.",
             "CH-1 chỉ tay tra hỏi chồng với vẻ mặt ghen tuông vô cớ.",
             "CH-1 (Linh, giọng cao vút chất vấn)",
             "Anh có người khác rồi phải không? Em đi tới nửa đêm sao anh chẳng gọi lấy một cuộc!"),

            ("s02", "CU", "e07bo1", ["linh_blazer"],
             "Phòng khách đêm khuya: cận cảnh CH-1 (Linh) đứng bên trái nhíu mày trách sự im lặng của chồng.",
             "CH-1 khoanh tay nhìn xuống sofa bên phải đầy hờn trách.",
             "CH-1 (Linh, giọng gay gắt khó chịu)",
             "Trước kia em về trễ chút anh đã hỏi đi với ai, sao giờ anh thờ ơ mặc kệ thế?"),

            ("s03", "CU", "e07bo1", ["tuan_polo"],
             "Phòng khách đêm khuya: cận cảnh CH-1 (Tuấn) ngồi trên sofa bên phải ngước nhìn vợ với đôi mắt trầm buồn.",
             "CH-1 bình thản cất lời giải thích không chút lớn tiếng.",
             "CH-1 (Tuấn, giọng trầm tĩnh sâu lắng)",
             "Ngày trước anh gọi liên tục là vì đêm hôm khuya khoắt, anh lo em đi đường gặp nguy hiểm."),

            ("s04", "CU", "e07bo1", ["tuan_polo"],
             "Phòng khách đêm khuya: CH-1 (Tuấn) ngồi bên phải tiếp lời với nỗi buồn chất chứa lâu ngày.",
             "CH-1 nhìn sang trái nhắc lại những lần vợ gạt phắt sự quan tâm.",
             "CH-1 (Tuấn, giọng điềm đạm chua xót)",
             "Nhưng anh gọi thì em tắt máy ngang, anh dặn về sớm giữ sức khỏe thì em mắng anh kiểm soát."),

            ("s05", "WIDE", "e07bo1", ["linh_blazer", "tuan_polo"],
             "Toàn cảnh phòng khách đêm trầm: CH-1 (Linh) đứng bên trái bắt đầu chột dạ, CH-2 (Tuấn) đứng dậy khỏi sofa bên phải.",
             "CH-1 hạ giọng cố biện minh cho bản thân.",
             "CH-1 (Linh, giọng chùng xuống chống chế)",
             "Thì chí ít anh cũng phải nhắn hỏi một câu, vợ chồng chứ có phải người dưng đâu!"),

            ("s06", "MED", "e07bo2", ["tuan_polo", "linh_blazer"],
             "Góc cửa sổ nhìn ra đèn đêm thành phố: CH-1 (Tuấn) đứng bên phải quay lại nhìn CH-2 (Linh) bên trái.",
             "CH-1 cười nhạt bất lực hỏi ngược lại vợ.",
             "CH-1 (Tuấn, cười nhạt hỏi thẳng vợ)",
             "Chẳng phải sự tự do không ai làm phiền này chính là điều bấy lâu nay em luôn đòi hỏi sao?"),

            ("s07", "CU", "e07bo2", ["tuan_polo"],
             "Bên khung cửa sổ đêm: cận cảnh CH-1 (Tuấn) bên phải nói rõ sự nghịch lý khiến người nghe thấm thía.",
             "CH-1 lắc đầu nhẹ, giọng trầm buồn rành mạch.",
             "CH-1 (Tuấn, giọng điềm tĩnh thấm thía)",
             "Lúc người ta quan tâm thì chê ngột ngạt, tới khi trả lại tự do thì nghi ngờ có người khác."),

            ("s08", "CU", "e07bo2", ["linh_blazer"],
             "Trong ánh đèn đêm: cận cảnh CH-1 (Linh) đứng bên trái cúi gằm mặt cắn môi im lặng, ánh mắt dâng nỗi hối hận.",
             "CH-1 buông thõng hai tay không cãi thêm được nửa lời.",
             None, ""),

            ("s09", "CU", "e07bo2", ["tuan_polo"],
             "Trong căn hộ đêm: CH-1 (Tuấn) bên phải khẳng định sự trong sạch nhưng mệt mỏi của mình.",
             "CH-1 nói chậm rãi từ tận đáy lòng.",
             "CH-1 (Tuấn, giọng trầm khàn chân thật)",
             "Anh không có ai bên ngoài cả, anh chỉ nhận ra nói mãi không đổi được gì chỉ thêm mệt mỏi."),

            ("s10", "CU", "e07bo2", ["tuan_polo"],
             "Cận cảnh CH-1 (Tuấn) bên phải với đôi mắt đỏ nhẹ nói về sự lạnh nhạt từ phía vợ.",
             "CH-1 nhìn sang trái nhắc lại nỗi cô đơn của chính mình.",
             "CH-1 (Tuấn, giọng nghẹn nhẹ điềm đạm)",
             "Anh dành hết tâm tư lo cho em, còn em chưa một lần hỏi anh đi làm mệt nhọc thế nào."),

            ("s11", "WIDE", "e07bo1", ["linh_blazer", "tuan_polo"],
             "Toàn cảnh phòng khách đêm khuya: CH-2 (Tuấn) bên phải đặt chìa khóa lên bàn trà chuẩn bị vào phòng nghỉ, CH-1 (Linh) đứng chôn chân bên trái.",
             "CH-2 nói câu kết nhẹ tênh giữa không gian tĩnh mịch.",
             "CH-2 (Tuấn, giọng bình thản buông nhẹ)",
             "Từ nay việc ai người nấy làm, mỗi người tự giữ không gian riêng như ý em muốn đi."),

            ("s12", "CU", "e07bo1", ["linh_blazer"],
             "Phòng khách đêm khuya: cận cảnh CH-1 (Linh) rơi nước mắt muộn màng khi nhận ra lòng chồng đã nguội lạnh.",
             "CH-1 rưng rưng nhìn theo hướng phòng trong khẽ gọi.",
             "CH-1 (Linh, giọng run rẩy ân hận khẽ gọi)",
             "Anh Tuấn... chẳng lẽ đến giận em mà giờ anh cũng không còn muốn giận nữa sao?"),

            ("s13", "MED", "e07bo2", ["tuan_polo"],
             "Bên cửa sổ đêm thành phố: một mình CH-1 (Tuấn) đứng trầm tư dưới ánh đèn vàng cô đơn.",
             "CH-1 hít sâu rồi từ từ quay mặt nhìn thẳng về phía khán giả.",
             None, ""),

            ("s14", "CU", "e07bo2", ["tuan_polo"],
             "Bên cửa sổ đêm: cận cảnh CH-1 (Tuấn) nhìn thẳng vào ống kính hỏi ý kiến khán giả.",
             "CH-1 nhìn thẳng camera đặt câu hỏi kết phim rồi khép môi tự nhiên.",
             "CH-1 (Tuấn, nhìn thẳng ống kính hỏi khán giả)",
             "Đem hết chân tình đối đãi mà chỉ nhận về sự lạnh nhạt, theo mọi người có nên buông tay giải thoát không ạ?"),
        ],
    },

    # =========================================================================
    # EP08: Chàng trai thật thà bán ổi cho nợ cả sạp và cái kết ấm lòng lúc chiều muộn (20 scenes)
    # =========================================================================
    "ep08": {
        "title": "Chàng trai thật thà bán ổi cho nợ cả sạp và cái kết ấm lòng lúc chiều muộn",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.20),
        "bgm_act2": ("piano_warm_family.mp3", 4.0, 0.25),
        "pivot_scene": "s15",
        "board_items": [
            ("CH-1: Tiến (Chàng trai bán ổi)", "tien"),
            ("CH-2: Bác Thắm (Bà bán bí kế bên)", "bactham"),
            ("CH-3: Thảo (Khách mua ổi 1)", "thao"),
            ("CH-4: Tuấn (Khách mua hết sạp)", "tuan_somi"),
            ("CH-5: Quỳnh (Khách không tiền lẻ)", "quynh"),
            ("BO-1: Vỉa hè sạp ổi ban ngày", "e08bo1"),
            ("BO-2: Vỉa hè nắng chiều hoàng hôn", "e08bo2"),
        ],
        "shots": [
            ("s01", "WIDE_CROWD", "e08bo1", ["thao", "tien", "bactham"],
             "Vỉa hè rợp bóng cây cạnh hàng rào sắt ban ngày: CH-2 (Tiến) đứng giữa cạnh rổ ổi trao túi ổi cho CH-1 (Thảo váy trắng) bên trái, CH-3 (Bác Thắm ngồi cạnh rổ bí) bên phải.",
             "CH-2 cười hiền đưa túi ổi cho khách dù điện thoại cô sập nguồn.",
             "CH-2 (Tiến, cười hiền lành xởi lởi với Thảo)",
             "Máy chị hết pin thì cứ cầm ổi về ăn trước đi, chiều tan làm ghé gửi em sau nhé!"),

            ("s02", "CU", "e08bo1", ["thao", "tien"],
             "Trên vỉa hè: CH-1 (Thảo) bên trái mỉm cười cảm kích nhận túi ổi từ tay CH-2 (Tiến) bên phải.",
             "CH-1 gật đầu hẹn chiều tan ca quay lại trả tiền.",
             "CH-1 (Thảo, mỉm cười lịch sự cảm ơn)",
             "Cảm ơn cậu nhiều nhé, chiều tan ca tôi nhất định quay lại gửi tiền cậu ngay!"),

            ("s03", "CU", "e08bo1", ["bactham"],
             "Bên rổ bí xanh: CH-1 (Bác Thắm quấn khăn rằn) ngồi bên phải bĩu môi chép miệng cười chê Tiến bên trái.",
             "CH-1 lắc đầu mỉa mai tính tin người của chàng trai.",
             "CH-1 (Bác Thắm, giọng châm chọc mỉa mai)",
             "Đúng là dại gái! Người lạ cầm đồ đi rồi thì bắc thang lên giời mà đòi tiền nhé con!"),

            ("s04", "WIDE_CROWD", "e08bo1", ["quynh", "tien", "bactham"],
             "Vỉa hè sạp ổi ban ngày: khách thứ hai CH-1 (Quỳnh váy chấm bi) đứng bên trái mở ví tờ tiền lớn trước mặt CH-2 (Tiến) ở giữa và CH-3 (Bác Thắm) bên phải.",
             "CH-2 gãi đầu lục túi chưa có tiền lẻ trả lại.",
             "CH-2 (Tiến, cười ngại ngùng thật thà)",
             "Sáng giờ em chưa có tiền lẻ thối lại tờ năm trăm, bác Thắm đổi giúp cháu với ạ!"),

            ("s05", "CU", "e08bo1", ["bactham", "tien"],
             "Trên vỉa hè: CH-1 (Bác Thắm) ngồi bên phải khoát tay từ chối đổi tiền lẻ cho CH-2 (Tiến) bên trái.",
             "CH-1 giữ khư khư túi tiền lắc đầu.",
             "CH-1 (Bác Thắm, giọng đanh đá từ chối)",
             "Tôi chỉ có mấy chục lẻ thôi không đủ đổi đâu, tự bán hàng thì tự xoay xở đi!"),

            ("s06", "CU", "e08bo1", ["tien", "quynh"],
             "Trên vỉa hè: CH-1 (Tiến) bên phải vui vẻ trao luôn túi ổi ba cân cho CH-2 (Quỳnh) đứng bên trái.",
             "CH-1 hào sảng cho khách cầm ổi về trước.",
             "CH-1 (Tiến, giọng chân chất tươi cười)",
             "Thôi chị cứ mang ổi về ăn trước đi, mai mốt tiện đường ghé trả em sau cũng được!"),

            ("s07", "CU", "e08bo1", ["bactham"],
             "Bên rổ bí vỉa hè: CH-1 (Bác Thắm) bên phải trố mắt lắc đầu ngao ngán mắng Tiến.",
             "CH-1 vỗ đùi chê bai cách buôn bán của Tiến.",
             "CH-1 (Bác Thắm, giọng cười khẩy chê bai)",
             "Lại cho người dưng nợ tiếp! Buôn bán khờ khạo kiểu cậu thì chỉ có cạp đất mà ăn thôi!"),

            ("s08", "CU", "e08bo1", ["tien"],
             "Bên rổ ổi xanh: CH-1 (Tiến) ngồi ghế xếp mỉm cười hiền lành đáp lời bác hàng xóm.",
             "CH-1 lau từng quả ổi với ánh mắt trong sáng lạc quan.",
             "CH-1 (Tiến, giọng hiền lành chân thật)",
             "Ổi vườn nhà cháu tự trồng mà bác, mình cứ tin người ta trước cho lòng thanh thản ạ."),

            ("s09", "WIDE_CROWD", "e08bo1", ["tuan_somi", "tien"],
             "Vỉa hè sạp ổi buổi trưa: khách thứ ba CH-1 (Tuấn mặc sơ mi trắng) đứng bên trái chỉ vào rổ ổi còn lại của CH-2 (Tiến) bên phải.",
             "CH-1 mỉm cười muốn mua ủng hộ sạch cả rổ ổi.",
             "CH-1 (Tuấn, giọng lịch thiệp vui vẻ)",
             "Ổi nhà trồng nhìn tươi ngon quá, cậu cân hết sạch chỗ còn lại trong rổ cho tôi nhé!"),

            ("s10", "CU", "e08bo1", ["tien", "tuan_somi"],
             "Trên vỉa hè: CH-1 (Tiến) bên phải gói xong túi ổi nhưng điện thoại cũ hết pin, nhìn CH-2 (Tuấn) bên trái phân trần.",
             "CH-1 giơ chiếc điện thoại tắt màn hình hỏi khách.",
             "CH-1 (Tiến, giọng thật thà ngại ngùng)",
             "Điện thoại cũ của em hết pin không mở mã quét được, anh có sẵn tiền mặt không ạ?"),

            ("s11", "CU", "e08bo1", ["tuan_somi", "tien"],
             "Trên vỉa hè: CH-1 (Tuấn) bên trái sờ túi thấy không mang tiền mặt nên định gửi lại túi ổi.",
             "CH-1 lịch sự ngại ngần định hẹn hôm khác.",
             "CH-1 (Tuấn, giọng tiếc nuối lịch sự)",
             "Nay tôi đi làm lại chẳng mang tiền mặt, hay để hôm khác tôi quay lại mua ủng hộ nhé."),

            ("s12", "MED", "e08bo1", ["tien", "tuan_somi"],
             "Trên vỉa hè: CH-1 (Tiến) bên phải nhấc túi ổi lớn đặt vào tay CH-2 (Tuấn) bên trái với nụ cười tin tưởng.",
             "CH-1 vui vẻ đưa ổi ra tận tay khách.",
             "CH-1 (Tiến, cười rạng rỡ xởi lởi)",
             "Gói xong cả rồi anh cứ cầm về biếu gia đình đi, lúc nào tiện đường ghé gửi em sau!"),

            ("s13", "WIDE", "e08bo2", ["tien", "bactham"],
             "Vỉa hè dưới nắng chiều hoàng hôn vàng cam: rổ ổi của CH-1 (Tiến) bên trái trống trơn, CH-2 (Bác Thắm) bên phải xách rổ bí ế nguyên đứng dậy về.",
             "CH-2 nhìn rổ không của Tiến mỉa mai rồi xách bí bỏ về.",
             "CH-2 (Bác Thắm, thở dài lắc đầu xách rổ về)",
             "Tắt nắng rồi đấy cậu tướng, mất trắng rổ ổi chẳng ai quay lại đâu, tôi về trước đây!"),

            ("s14", "CU", "e08bo2", ["tien"],
             "Dưới nắng hoàng hôn ấm áp: một mình CH-1 (Tiến) thu dọn chiếc rổ nhựa trống không, ánh mắt thoáng buồn nhẹ.",
             "CH-1 phủi tay đứng dậy bên hàng rào sắt chuẩn bị ra về.",
             None, ""),

            ("s15", "WIDE_CROWD", "e08bo2", ["thao", "quynh", "tien"],
             "Vỉa hè hoàng hôn rực rỡ: lúc CH-3 (Tiến) định xách rổ về thì từ bên trái CH-1 (Thảo) và CH-2 (Quỳnh) bước nhanh tới tươi cười gọi lớn.",
             "Hai vị khách ban sáng đồng loạt cầm tiền mặt bước tới trả.",
             "CH-1 (Thảo, tươi cười vẫy tay gọi từ xa)",
             "Chàng trai bán ổi ơi khoan về đã! Chị tan làm ghé gửi tiền ổi sáng nay đây này!"),

            ("s16", "CU", "e08bo2", ["quynh", "tien"],
             "Dưới ánh chiều vàng: CH-1 (Quỳnh) bên trái tươi cười đặt tiền lẻ vào tay CH-2 (Tiến) đang xúc động bên phải.",
             "CH-1 khen ngợi vị ổi ngọt lành của Tiến.",
             "CH-1 (Quỳnh, mỉm cười rạng rỡ chân thành)",
             "Chị cũng đổi sẵn tiền lẻ mang qua gửi em đây, ổi vườn nhà em giòn ngọt lắm nhé!"),

            ("s17", "WIDE_CROWD", "e08bo2", ["tuan_somi", "thao", "tien"],
             "Vỉa hè hoàng hôn: CH-1 (Tuấn sơ mi trắng) bước tới bên trái cạnh CH-2 (Thảo), trao tiền mặt hậu hĩnh vào tay CH-3 (Tiến) bên phải.",
             "CH-1 bắt tay chàng trai trẻ đặt thêm trái cây cho văn phòng.",
             "CH-1 (Tuấn, mỉm cười ấm áp bắt tay Tiến)",
             "Tôi rút tiền mặt quay lại gửi cậu đây, từ tuần sau cậu giao trái cây sạch cho công ty tôi nhé!"),

            ("s18", "CU", "e08bo2", ["tien"],
             "Dưới nắng hoàng hôn vàng ấm: cận cảnh CH-1 (Tiến) cầm tiền trên tay, mắt sáng bừng hạnh phúc cúi đầu cảm ơn.",
             "CH-1 nở nụ cười hiền hậu tràn ngập niềm vui.",
             "CH-1 (Tiến, xúc động cúi đầu cười tươi)",
             "Em cảm ơn các anh chị nhiều lắm ạ! Sống chân thành thật thà đúng là chẳng bao giờ thiệt đâu!"),

            ("s19", "WIDE_CROWD", "e08bo2", ["tuan_somi", "thao", "tien"],
             "Toàn cảnh ấm áp dưới ráng chiều hoàng hôn bên hàng rào sắt: mọi người đứng trò chuyện vui vẻ quanh chàng trai bán ổi.",
             "Khung cảnh đời thường giản dị tràn ngập tình người lúc chiều muộn.",
             None, ""),

            ("s20", "CU", "e08bo2", ["tien"],
             "Dưới ánh hoàng hôn: cận cảnh CH-1 (Tiến) ôm chiếc rổ nhựa nhìn thẳng vào ống kính mỉm cười hỏi khán giả.",
             "CH-1 nhìn thẳng camera trò chuyện mộc mạc rồi khép môi tự nhiên.",
             "CH-1 (Tiến, nhìn thẳng ống kính mỉm cười hỏi khán giả)",
             "Trao đi lòng tin để nhận lại chữ tín ấm lòng, mọi người thấy cách sống của Tiến có đáng quý không ạ?"),
        ],
    },

    # =========================================================================
    # EP09: Cô gái hám danh đi xem mắt tưởng giám đốc tập đoàn là thợ lau xe (19 scenes)
    # =========================================================================
    "ep09": {
        "title": "Cô gái hám danh đi xem mắt tưởng giám đốc tập đoàn là thợ lau xe",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.22),
        "pivot_scene": "s13",
        "board_items": [
            ("CH-1: Tuấn (Giám đốc tập đoàn)", "tuan_vest"),
            ("CH-2: Mỹ (Cô gái xem mắt hám danh)", "my_tochong"),
            ("CH-3: Ngân (Trợ lý Giám đốc)", "ngan"),
            ("BO-1: Bãi đỗ xe sang quảng trường", "e09bo1"),
        ],
        "shots": [
            ("s01", "WIDE_CROWD", "e09bo1", ["my_tochong", "tuan_vest"],
             "Bãi đỗ xe quảng trường khu đô thị sang trọng có chiếc sedan đen bên phải và người qua lại phía xa: CH-1 (Mỹ tóc hồng đầm hoa) đứng bên trái hất hàm sai CH-2 (Tuấn mặc vest đen cầm khăn tay lau gương xe) bên phải.",
             "CH-1 chống nạnh chỉ tay ra lệnh như bà chủ.",
             "CH-1 (Mỹ, giọng chảnh chọe hách dịch)",
             "Này cậu lau xe kia, tiện tay lau bóng luôn chiếc xe sang phía sau cho chị đi!"),

            ("s02", "CU", "e09bo1", ["tuan_vest", "my_tochong"],
             "Tại bãi đỗ xe: CH-1 (Tuấn mặc vest đen) bên phải quay lại nhướng mày định giải thích với CH-2 (Mỹ) bên trái.",
             "CH-1 bình thản gấp nhẹ chiếc khăn tay.",
             "CH-1 (Tuấn, giọng điềm tĩnh lịch sự)",
             "Cô nhầm rồi, tôi đâu phải nhân viên nhận lau xe thuê ở bãi này."),

            ("s03", "CU", "e09bo1", ["my_tochong"],
             "Tại bãi đỗ xe: CH-1 (Mỹ tóc hồng) bên trái bĩu môi cắt ngang rồi rút điện thoại gọi cho người mai mối.",
             "CH-1 áp điện thoại lên tai hỏi giục đối tượng xem mắt.",
             "CH-1 (Mỹ, giọng sốt ruột kiêu kỳ trên điện thoại)",
             "Alo chú Trần à, vị Giám đốc chú hẹn xem mắt tới chưa? Cháu đợi mỏi chân rồi đấy!"),

            ("s04", "MED", "e09bo1", ["my_tochong", "tuan_vest"],
             "Bãi đỗ xe sang: CH-1 (Mỹ) hạ điện thoại nhìn bộ vest đen sơ mi trắng của CH-2 (Tuấn) bên phải với vẻ thất vọng.",
             "CH-1 chỉ tay vào bộ vest của Tuấn trố mắt hỏi lớn.",
             "CH-1 (Mỹ, trố mắt thất vọng thốt lên)",
             "Vest đen sơ mi trắng... Khoan đã, đừng nói anh chính là người hẹn xem mắt với tôi nhé!"),

            ("s05", "CU", "e09bo1", ["tuan_vest"],
             "Bãi đỗ xe: CH-1 (Tuấn) bên phải mỉm cười lịch thiệp gật đầu chào để xem cô bộc lộ tính cách thật.",
             "CH-1 đút một tay vào túi quần chào nhã nhặn.",
             "CH-1 (Tuấn, giọng điềm đạm mỉm cười nhẹ)",
             "Thì ra cô là Mỹ do chú Trần giới thiệu đúng không? Chào cô."),

            ("s06", "CU", "e09bo1", ["my_tochong"],
             "Bãi đỗ xe: CH-1 (Mỹ tóc hồng) bên trái khoanh tay khinh khỉnh cười nhạo từ chối lời chào.",
             "CH-1 hất tóc nhìn xéo sang phải đầy coi thường.",
             "CH-1 (Mỹ, giọng chua ngoa khinh miệt)",
             "Chú Trần hứa giới thiệu đại gia, ai dè gặp thợ lau xe bày đặt mặc vest làm màu!"),

            ("s07", "CU", "e09bo1", ["tuan_vest"],
             "Bãi đỗ xe: CH-1 (Tuấn) bên phải giữ nụ cười điềm tĩnh hỏi vặn lại quan điểm của cô.",
             "CH-1 nghiêng đầu nhìn thẳng vào mắt Mỹ.",
             "CH-1 (Tuấn, giọng bình thản sắc sảo)",
             "Cô thành kiến với người lao động thế nhỉ? Làm nghề chân chính có gì đáng xấu hổ đâu?"),

            ("s08", "CU", "e09bo1", ["my_tochong"],
             "Bãi đỗ xe: CH-1 (Mỹ) bên trái vênh mặt khoe khoang mức sống xa xỉ của mình.",
             "CH-1 vỗ nhẹ lên túi xách hàng hiệu đầy ngạo mạn.",
             "CH-1 (Mỹ, giọng kênh kiệu khoe mẽ)",
             "Cả tháng tiền lương của hạng người như anh còn chẳng đủ cho tôi ăn một bữa nhà hàng!"),

            ("s09", "MED", "e09bo1", ["tuan_vest", "my_tochong"],
             "Bãi đỗ xe rộng: CH-1 (Tuấn) bên phải điềm nhiên hỏi ngược lại công việc của CH-2 (Mỹ) bên trái.",
             "CH-1 mỉm cười nhẹ nhướng mày hỏi khéo.",
             "CH-1 (Tuấn, giọng tỉnh rụi hỏi lại)",
             "Nghe cô nói vậy chắc thu nhập cô cao lắm nhỉ, cô đang làm sếp lớn ở đâu thế?"),

            ("s10", "CU", "e09bo1", ["my_tochong"],
             "Bãi đỗ xe: CH-1 (Mỹ) bên trái bật cười tự đắc vuốt tóc hồng khoe không cần đi làm.",
             "CH-1 ngẩng mặt khoe có nhiều đại gia theo đuổi.",
             "CH-1 (Mỹ, giọng tự đắc hãnh diện)",
             "Xinh đẹp như tôi việc gì phải đi làm, khối đại gia xếp hàng mang tiền tới cho tôi!"),

            ("s11", "CU", "e09bo1", ["tuan_vest"],
             "Bãi đỗ xe: CH-1 (Tuấn) bên phải gật gù bóc mẽ thẳng thừng khiến cô gái cứng họng.",
             "CH-1 nhìn thẳng sang trái nói lời sâu cay.",
             "CH-1 (Tuấn, giọng điềm tĩnh bóc mẽ cực gắt)",
             "Thảo nào ngoài ba mươi cô vẫn đi xem mắt! Vì họ chỉ qua đường chứ ai cưới cô làm vợ."),

            ("s12", "CU", "e09bo1", ["my_tochong"],
             "Bãi đỗ xe: CH-1 (Mỹ) bên trái tức đỏ mặt chỉ tay mắng xối xả vì bị nói trúng tim đen.",
             "CH-1 giậm gót giày giận dữ phản pháo.",
             "CH-1 (Mỹ, tức tối đỏ mặt gắt lên)",
             "Anh dám hỗn hào thế à! Đàn ông vừa nghèo vừa độc miệng như anh muôn đời ế vợ!"),

            ("s13", "WIDE_CROWD", "e09bo1", ["my_tochong", "tuan_vest", "ngan"],
             "Bãi đỗ xe quảng trường: trợ lý CH-3 (Ngân mặc công sở cầm bìa hồ sơ) từ bên phải vội bước tới cúi chào kính cẩn CH-2 (Tuấn) trước mặt CH-1 (Mỹ) chết trân bên trái.",
             "CH-3 hai tay trình hợp đồng cho Giám đốc Tuấn bên cạnh chiếc xe sang.",
             "CH-3 (Ngân, giọng lễ phép cung kính báo cáo)",
             "Dạ thưa Tổng giám đốc Tuấn, cuối cùng cũng thấy anh ngoài xe riêng, mời sếp ký gấp hợp đồng ạ!"),

            ("s14", "CU", "e09bo1", ["tuan_vest", "my_tochong"],
             "Bãi đỗ xe: CH-1 (Tuấn) bên phải bấm chìa khóa mở đèn chiếc xe sang rồi giới thiệu chính thức với CH-2 (Mỹ).",
             "CH-1 mỉm cười lạnh nhạt nhìn vẻ mặt hóa đá của cô gái.",
             "CH-1 (Tuấn, giọng điềm đạm đĩnh đạc)",
             "Tôi là Tuấn chủ chiếc xe này, thấy gương bám bụi nên tiện tay lau vì tôi ưa sạch sẽ thôi."),

            ("s15", "CU", "e09bo1", ["my_tochong"],
             "Bãi đỗ xe: cận cảnh CH-1 (Mỹ tóc hồng) bên trái lật mặt nhanh như chớp, cười ngọt xớt nịnh bợ.",
             "CH-1 chớp mắt nũng nịu giả vờ vừa nãy chỉ thử lòng Giám đốc.",
             "CH-1 (Mỹ, đổi giọng ngọt ngào thảo mai)",
             "Ôi anh Tuấn Giám đốc! Nãy em chỉ đùa thử lòng anh thôi, tối anh về nhà em nấu cơm nhé!"),

            ("s16", "CU", "e09bo1", ["tuan_vest"],
             "Bãi đỗ xe: CH-1 (Tuấn) bên phải lắc đầu dứt khoát từ chối không chút lưu tình.",
             "CH-1 cài lại khuy áo vest với ánh mắt nghiêm nghị.",
             "CH-1 (Tuấn, giọng lạnh nhạt dứt khoát)",
             "Khỏi cần đâu cô Mỹ, người ưa sạch sẽ như tôi ăn cơm thực dụng của cô nuốt không trôi nổi."),

            ("s17", "MED", "e09bo1", ["my_tochong", "tuan_vest"],
             "Bãi đỗ xe: CH-1 (Mỹ) bên trái cố bước theo níu kéo nhưng CH-2 (Tuấn) bên phải giơ tay chặn khoảng cách.",
             "CH-2 tuyên bố kết thúc buổi xem mắt ngay tại chỗ.",
             "CH-2 (Tuấn, giọng dứt khoát rõ ràng)",
             "Buổi xem mắt kết thúc tại đây, mẫu phụ nữ trọng tiền khinh người như cô tôi không dám rước!"),

            ("s18", "WIDE_CROWD", "e09bo1", ["my_tochong", "tuan_vest"],
             "Toàn cảnh bãi đỗ xe quảng trường: CH-2 (Tuấn) sải bước thẳng về phía trước, bỏ lại CH-1 (Mỹ tóc hồng) đứng chôn chân tiếc nuối phía sau.",
             "CH-2 bước đi tự tin dứt khoát không ngoái đầu lại.",
             None, ""),

            ("s19", "CU", "e09bo1", ["tuan_vest"],
             "Tại bãi đỗ xe quảng trường: cận cảnh CH-1 (Tuấn) dừng bước nhìn thẳng vào ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera trò chuyện tự nhiên rồi mỉm cười khép môi.",
             "CH-1 (Tuấn, nhìn thẳng ống kính hỏi khán giả)",
             "Cả nhà ơi, gặp cô gái tham danh hám lợi thế này Tuấn từ chối thẳng là chuẩn rồi đúng không ạ?"),
        ],
    },

    # =========================================================================
    # EP10: Tình cũ mang hai tỷ khinh vợ giản dị của chồng và màn lột xác chấn động (24 scenes)
    # =========================================================================
    "ep10": {
        "title": "Tình cũ mang hai tỷ khinh vợ giản dị của chồng và màn lột xác chấn động",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.22),
        "pivot_scene": "s08",
        "board_items": [
            ("CH-1: Tuấn (Ông chủ nhà hàng)", "tuan_vest"),
            ("CH-2a: Khánh Ly [Tạp dề giản dị]", "khanhly_tapde"),
            ("CH-2b: Khánh Ly [Vest vàng quý phái]", "khanhly_vestvang"),
            ("CH-3: Nhung (Tình cũ áo lông xanh)", "nhung_aolong"),
            ("BO-1: Nhà hàng sang trọng đông khách", "e10bo1"),
            ("BO-2: Lối ra phòng VIP nhà hàng", "e10bo2"),
        ],
        "shots": [
            ("s01", "WIDE_CROWD", "e10bo1", ["nhung_aolong", "khanhly_tapde"],
             "Sảnh chính nhà hàng sang trọng có thực khách ngồi ăn phía xa: CH-1 (Nhung khoác áo lông xanh đầm đỏ) đứng khoanh tay bên trái đối diện CH-2 (Khánh Ly đeo tạp dề) bên phải.",
             "CH-1 hất cằm ngạo mạn đòi người vợ giản dị nhường chồng.",
             "CH-1 (Nhung, giọng trịch thượng ngạo mạn)",
             "Tôi bồi thường cho cô một khoản lớn, cô ký giấy nhường lại anh Tuấn cho tôi đi!"),

            ("s02", "CU", "e10bo1", ["nhung_aolong"],
             "Trong nhà hàng sang trọng: cận cảnh CH-1 (Nhung áo lông xanh) bên trái nhếch môi tự hào nhắc chuyện quá khứ.",
             "CH-1 liếc nhìn chiếc tạp dề của đối phương đầy khinh khi.",
             "CH-1 (Nhung, giọng sắc sảo coi thường)",
             "Xưa tôi bận đi nước ngoài mới chia tay, chứ quê mùa như cô làm gì có cửa lấy anh ấy!"),

            ("s03", "CU", "e10bo1", ["khanhly_tapde"],
             "Trong nhà hàng: cận cảnh CH-1 (Khánh Ly đeo tạp dề) bên phải bình tĩnh nhìn thẳng tình cũ để thử lòng cô ta.",
             "CH-1 điềm đạm nhẹ nhàng hỏi về đứa con nhỏ.",
             "CH-1 (Khánh Ly, giọng điềm tĩnh nhẹ nhàng)",
             "Tôi nghe rõ ý cô rồi, nhưng còn đứa con nhỏ của tụi tôi thì tính sao đây?"),

            ("s04", "CU", "e10bo1", ["nhung_aolong"],
             "Trong nhà hàng: CH-1 (Nhung) bên trái phẩy tay lạnh lùng bắt cô mang con đi luôn.",
             "CH-1 nhíu mày xua tay không chút tình cảm.",
             "CH-1 (Nhung, giọng ích kỷ phũ phàng)",
             "Đứa bé đó cô tự dắt đi luôn đi, tôi với anh Tuấn còn sinh con riêng của tụi tôi chứ!"),

            ("s05", "CU", "e10bo1", ["khanhly_tapde"],
             "Trong nhà hàng: CH-1 (Khánh Ly đeo tạp dề) bên phải điềm nhiên dặn thói quen chăm sóc chồng.",
             "CH-1 nói chậm rãi từng thói quen sức khỏe của chồng.",
             "CH-1 (Khánh Ly, giọng hiền hậu tinh tế)",
             "Vậy cô nhớ giặt riêng sơ mi cho anh ấy, dạ dày anh yếu sáng nào cũng phải nấu cháo ấm."),

            ("s06", "CU", "e10bo1", ["nhung_aolong"],
             "Trong nhà hàng: CH-1 (Nhung áo lông xanh) bên trái cười khẩy cắt ngang sỉ nhục người vợ như giúp việc.",
             "CH-1 khoanh tay mỉa mai đầy ngạo mạn.",
             "CH-1 (Nhung, cười khẩy mỉa mai cay độc)",
             "Thôi dẹp mấy việc của người giúp việc đi! Hóa ra bấy lâu cô chỉ làm chân hầu hạ trong nhà à?"),

            ("s07", "MED", "e10bo1", ["nhung_aolong", "khanhly_tapde"],
             "Giữa sảnh nhà hàng: CH-1 (Nhung) bên trái vênh mặt tự ca tụng bản thân rồi chỉ tay đuổi CH-2 (Khánh Ly) bên phải.",
             "CH-1 hất tay ra lệnh đuổi Khánh Ly đi.",
             "CH-1 (Nhung, giọng kiêu căng hống hách)",
             "Phụ nữ sang trọng như tôi sinh ra để hưởng thụ! Thôi cô mau khuất mắt tôi ngay đi!"),

            ("s08", "WIDE_CROWD", "e10bo1", ["nhung_aolong", "tuan_vest", "khanhly_tapde"],
             "Sảnh nhà hàng đông thực khách: ông chủ CH-2 (Tuấn mặc vest đen lịch lãm) sải bước tới đứng chắn giữa CH-1 (Nhung) bên trái và vợ CH-3 (Khánh Ly) bên phải.",
             "CH-2 cất giọng trầm đanh thép che chở phía trước vợ.",
             "CH-2 (Tuấn, giọng trầm đanh thép vang lên)",
             "Đúng là có người cần phải bước ra khỏi đây ngay lập tức đấy!"),

            ("s09", "CU", "e10bo1", ["nhung_aolong", "tuan_vest"],
             "Trong nhà hàng: CH-1 (Nhung áo lông xanh) bên trái mừng hụt reo lên tưởng tình cũ bênh vực mình.",
             "CH-1 chớp mắt mỉm cười đắc ý bước lại gần Tuấn.",
             "CH-1 (Nhung, hớn hở mừng rỡ hiểu lầm)",
             "Anh Tuấn! Em biết ngay trong lòng anh lúc nào cũng còn thương nhớ em mà!"),

            ("s10", "CU", "e10bo1", ["tuan_vest"],
             "Trong nhà hàng: cận cảnh CH-1 (Tuấn mặc vest đen) bên phải nhìn Nhung với ánh mắt băng giá dập tắt ảo tưởng.",
             "CH-1 gằn từng tiếng bảo vệ danh dự cho vợ.",
             "CH-1 (Tuấn, giọng lạnh băng dứt khoát)",
             "Cô bớt ảo tưởng đi, người tôi yêu cầu rời khỏi nhà hàng của vợ chồng tôi chính là cô đấy!"),

            ("s11", "CU", "e10bo1", ["nhung_aolong"],
             "Trong nhà hàng: CH-1 (Nhung) bên trái sững sờ tái mặt không tin anh chọn người vợ mặc tạp dề.",
             "CH-1 mở to mắt tức tối hỏi lớn.",
             "CH-1 (Nhung, giọng sững sờ cay cú)",
             "Không thể nào! Sao ông chủ lớn như anh lại chọn cô vợ quê mùa thay vì người đẹp như em?"),

            ("s12", "CU", "e10bo1", ["tuan_vest"],
             "Trong nhà hàng: CH-1 (Tuấn) bên phải cười lạnh vạch trần sự thực dụng khi xưa của tình cũ.",
             "CH-1 nhìn thẳng mặt cô ta hỏi câu chí mạng.",
             "CH-1 (Tuấn, giọng sắc lạnh đanh thép)",
             "Cô chọn khéo lúc tôi giàu mới về nhỉ! Nếu tôi vẫn nghèo rớt mùng tơi cô có thèm nhìn không?"),

            ("s13", "MED", "e10bo1", ["tuan_vest", "khanhly_tapde"],
             "Trong nhà hàng: CH-1 (Tuấn) quay sang bên phải đổi ánh mắt dịu dàng nắm tay vợ CH-2 (Khánh Ly đeo tạp dề).",
             "CH-1 ân cần bảo vợ vào phòng VIP thay bộ vest mới anh mua sáng nay.",
             "CH-1 (Tuấn, giọng cưng chiều ấm áp nói với vợ)",
             "Việc dọn dẹp để nhân viên làm, sáng anh mua bộ vest mới trong phòng VIP, vợ vào mặc thử đi!"),

            ("s14", "CU", "e10bo1", ["khanhly_tapde", "tuan_vest"],
             "Trong nhà hàng: CH-1 (Khánh Ly đeo tạp dề) bên phải mỉm cười hiền dịu gật đầu với chồng rồi bước vào phòng trong.",
             "CH-1 mỉm cười ngọt ngào đáp lời chồng.",
             "CH-1 (Khánh Ly, mỉm cười dịu dàng lễ phép)",
             "Dạ ở nhà hoài buồn chân tay nên em ra phụ một chút thôi, để em vào thay ngay ạ."),

            ("s15", "CU", "e10bo1", ["nhung_aolong", "tuan_vest"],
             "Trong nhà hàng: khi vợ Tuấn vừa khuất vào trong, CH-1 (Nhung) bên trái vẫn cố cười mỉa chê bai trước mặt CH-2 (Tuấn).",
             "CH-1 hất cằm khẳng định chỉ mình mới xứng đi cạnh Tuấn.",
             "CH-1 (Nhung, giọng tự phụ mỉa mai)",
             "Anh đừng dối lòng nữa, doanh nhân thành đạt phải sánh đôi với phụ nữ quý phái như em mới xứng!"),

            ("s16", "WIDE", "e10bo2", ["khanhly_vestvang"],
             "Lối cửa phòng VIP nhà hàng sang trọng dưới ánh đèn chùm vàng ấm: CH-1 (Khánh Ly nay diện bộ vest vàng mù tạt quý phái, trang điểm rạng ngời) thong thả sải bước ra đầy khí chất bà chủ.",
             "CH-1 bước đi uyển chuyển tự tin hướng ra sảnh chính.",
             None, ""),

            ("s17", "WIDE_CROWD", "e10bo1", ["nhung_aolong", "tuan_vest", "khanhly_vestvang"],
             "Sảnh nhà hàng sang trọng: CH-3 (Khánh Ly trong bộ vest vàng quý phái) bước tới đứng bên phải CH-2 (Tuấn), khiến CH-1 (Nhung áo lông xanh) bên trái há hốc miệng sững sờ.",
             "CH-2 tự hào nắm tay người vợ xinh đẹp quý phái của mình.",
             "CH-2 (Tuấn, giọng tự hào kiêu hãnh nhìn Nhung)",
             "Cô nhìn cho rõ đi! Vợ tôi bình thường giản dị lo cho nhà, chứ lên đồ nhẹ đã sang gấp trăm lần cô!"),

            ("s18", "CU", "e10bo1", ["tuan_vest", "khanhly_vestvang"],
             "Trong nhà hàng: CH-1 (Tuấn) đứng cạnh CH-2 (Khánh Ly vest vàng), ánh mắt xúc động nhắc lại thuở hàn vi.",
             "CH-1 siết chặt bàn tay vợ nói lời tri ân sâu sắc.",
             "CH-1 (Tuấn, giọng trầm ấm xúc động chân tình)",
             "Lúc tôi nghèo khổ ăn từng ổ bánh mì qua ngày, chỉ có mình vợ tôi kề vai sát cánh chưa từng rời bỏ."),

            ("s19", "CU", "e10bo1", ["tuan_vest"],
             "Trong nhà hàng: cận cảnh CH-1 (Tuấn) quay sang nhìn thẳng Nhung bên trái cảnh cáo đanh thép.",
             "CH-1 nghiêm mặt khẳng định vị trí bất khả xâm phạm của vợ.",
             "CH-1 (Tuấn, giọng đanh thép uy nghiêm)",
             "Nay có tiền rồi tôi muốn đưa cô ấy đi ngắm thế giới, cô lấy tư cách gì đòi phán xét vợ tôi!"),

            ("s20", "CU", "e10bo1", ["nhung_aolong"],
             "Trong nhà hàng: CH-1 (Nhung áo lông xanh) bên trái bẽ bàng cay cú đưa ra lời thách đố khán giả.",
             "CH-1 nghiến răng cố vớt vát sĩ diện cuối cùng.",
             "CH-1 (Nhung, giọng cay cú thách thức)",
             "Vậy anh dám hỏi khán giả xem ai đúng không? Nếu tôi thua tôi bay ra nước ngoài không bao giờ quay lại!"),

            ("s21", "CU", "e10bo1", ["tuan_vest", "khanhly_vestvang"],
             "Trong nhà hàng: CH-1 (Tuấn) khoác vai CH-2 (Khánh Ly vest vàng) bên phải, mỉm cười bản lĩnh khẳng định tình yêu.",
             "CH-1 khẳng định chung thủy tuyệt đối khiến Khánh Ly mỉm cười hạnh phúc.",
             "CH-1 (Tuấn, giọng kiên định ấm áp)",
             "Chẳng ai ủng hộ kẻ chen ngang đâu! Mà dù thế nào, vợ của Tuấn trọn đời chỉ có mình Khánh Ly thôi!"),

            ("s22", "WIDE_CROWD", "e10bo1", ["nhung_aolong", "tuan_vest", "khanhly_vestvang"],
             "Toàn cảnh sảnh nhà hàng sang trọng: CH-1 (Nhung áo lông xanh) bẽ mặt xách túi quay lưng bỏ đi bên trái, vợ chồng CH-2 (Tuấn) và CH-3 (Khánh Ly vest vàng) nắm tay nhau mỉm cười bên phải.",
             "CH-1 bước nhanh khỏi nhà hàng, hai vợ chồng ông chủ nhìn nhau ấm áp.",
             None, ""),

            ("s23", "CU", "e10bo1", ["khanhly_vestvang", "tuan_vest"],
             "Trong nhà hàng: cận cảnh CH-1 (Khánh Ly trong bộ vest vàng) mỉm cười hiền hậu tựa nhẹ bên vai chồng CH-2 (Tuấn).",
             "CH-1 nhìn chồng với ánh mắt biết ơn và viên mãn.",
             "CH-1 (Khánh Ly, giọng dịu dàng hạnh phúc)",
             "Cảm ơn chồng đã luôn trân trọng và che chở cho mẹ con em."),

            ("s24", "CU", "e10bo1", ["tuan_vest", "khanhly_vestvang"],
             "Trong sảnh nhà hàng sang trọng: CH-1 (Tuấn) đứng cạnh vợ CH-2 (Khánh Ly vest vàng), quay mặt nhìn thẳng ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera kêu gọi khán giả ủng hộ rồi mỉm cười khép môi.",
             "CH-1 (Tuấn, nhìn thẳng ống kính mỉm cười hỏi khán giả)",
             "Người vợ tảo tần từ thuở hàn vi xứng đáng được yêu thương trọn đời đúng không ạ? Cả nhà thả tim nhé!"),
        ],
    },
}
