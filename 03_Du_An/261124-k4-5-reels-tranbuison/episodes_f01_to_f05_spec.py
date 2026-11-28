"""
Screenplay & Shot-by-Shot Cinema Blueprint — 5 New Tran Bui Son Remake Films (`261124 K4 Batch`):
- 100% Canonical K4 Character Genealogy & Strict Age Fit (`0%` father reuse, `1 character = 1 family relationship`!).
- All newly created characters are permanently saved & indexed in `CHARACTER/` (`00_GIA_PHA_NHAN_VAT_K4.md` & `character_registry.json`).
- Strict 180-degree spatial axis (`CHỐT KHÔNG GIAN`), crisp `<= 19 words` natural Vietnamese cinema dialogue per shot, `0%` mention of interior walls.
- 3-Act Natural Film Scoring (`Acoustic Guitar` everyday -> `Dramatic Tension` conflict -> `Warm Family Piano` resolution).
"""

EPISODES_261124 = {
    # =========================================================================
    # F01: Lễ mừng thọ 75 — Con trai giấu mẹ già sau buồng và chiếc bát nhôm 50 năm (22 scenes)
    # Cast (G04): Cụ Cúc (75t, Bà nội) — Bác Trọng (55t, Con trai) — Quân (27t, Cháu đích tôn)
    # =========================================================================
    "f01": {
        "title": "Mở đại tiệc mừng thọ bảy lăm tuổi nhưng giấu mẹ già trong buồng tối",
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.94),
            ("s14", "piano_ltk_emotional.mp3", 4.0, 1.02),
            ("s19", "piano_warm_family.mp3", 5.0, 1.08),
        ],
        "board_items": [
            ("CH-1: Cụ Cúc 75t (G04_01b)", "cucuc"),
            ("CH-2: Bác Trọng 55t (G04_07 Mới)", "bactrong"),
            ("CH-3: Quân 27t (G04_05c)", "quan_somi"),
            ("BO-1: Buồng trong cũ tối", "f01bo1"),
            ("BO-2: Sảnh tiệc mừng thọ đông khách", "f01bo2"),
        ],
        "shots": [
            ("s01", "WIDE", "f01bo1", ["bactrong", "cucuc"],
             "Trong căn buồng nhỏ cũ kỹ ánh đèn vàng mờ: CH-1 (Bác Trọng 55 tuổi mặc vest đen cài hoa đỏ) đứng chắn cửa bên trái xua tay ngăn CH-2 (Cụ Cúc 75 tuổi mặc áo nâu) ngồi mép ghế gỗ bên phải.",
             "CH-1 nhíu mày khó chịu ra lệnh bắt mẹ già ngồi yên trong buồng không được bước ra ngoài.",
             "CH-1 (Bác Trọng, giọng gắt nhẹ sĩ diện nhìn mẹ)",
             "Mẹ cứ ngồi yên trong buồng này thôi, tay chân run rẩy bước ra sảnh làm rơi đồ họ hàng cười cho!"),

            ("s02", "CU", "f01bo1", ["cucuc"],
             "Trong buồng nhỏ cũ: cận cảnh CH-1 (Cụ Cúc 75 tuổi tóc bạc mặc áo nâu) ngồi bên phải ngước nhìn con trai bên trái với ánh mắt tủi thân khẩn khoản.",
             "CH-1 đan hai bàn tay già nua run nhẹ, năn nỉ con trai bằng giọng hiền lành.",
             "CH-1 (Cụ Cúc, giọng run nhẹ khẩn khoản)",
             "Trọng ơi, nay là lễ mừng thọ bảy mươi lăm tuổi của mẹ, cho mẹ ra chào họ hàng năm phút thôi con."),

            ("s03", "CU", "f01bo1", ["bactrong"],
             "Trong buồng nhỏ: cận cảnh CH-1 (Bác Trọng mặc vest đen hoa đỏ) đứng bên trái nghiêm mặt lắc đầu nhìn sang phải.",
             "CH-1 chỉnh lại vạt áo vest sang trọng, dứt khoát từ chối rồi quay lưng ra cửa.",
             "CH-1 (Bác Trọng, giọng lạnh lùng áp đặt)",
             "Ngoài sảnh toàn chủ doanh nghiệp với đối tác lớn của con, mẹ ăn cháo trong này đi đừng ra làm mất mặt!"),

            ("s04", "WIDE_CROWD", "f01bo2", ["bactrong"],
             "Sảnh đại tiệc mừng thọ sang trọng đông quan khách ngồi bàn tròn phía sau: CH-1 (Bác Trọng mặc vest hoa đỏ) đứng giữa sảnh tươi cười nâng ly chào khách.",
             "CH-1 cười nói hào sảng khoe khoang giả tạo trước mặt đông đảo quan khách.",
             "CH-1 (Bác Trọng, giọng hồ hởi sĩ diện trước đám đông)",
             "Cảm ơn các bác tới dự đại lễ mừng thọ! Cụ nhà tôi hơi mệt nên đang dùng yến thượng hạng trong phòng lạnh ạ!"),

            ("s05", "MED", "f01bo1", ["cucuc"],
             "Trong căn buồng tối lặng lẽ: một mình CH-1 (Cụ Cúc) bưng bát cháo trắng trên bàn gỗ nhưng đôi tay run làm cháo sánh nhẹ lên vạt áo nâu.",
             "CH-1 vội đặt bát xuống, cúi đầu lau vạt áo với giọt nước mắt tủi phận.",
             "CH-1 (Cụ Cúc, thở dài nghẹn ngào tự trách)",
             "Đến bát cháo mình cầm cũng đổ thế này, trách sao thằng Trọng nó xấu hổ chẳng dám cho ra ngoài..."),

            ("s06", "WIDE", "f01bo1", ["quan_somi", "cucuc"],
             "Căn buồng nhỏ phía sau: cháu nội CH-1 (Quân 27 tuổi mặc sơ mi trắng) từ cửa gỗ bên trái bước vào, sững sờ thấy bà nội CH-2 (Cụ Cúc) ngồi lủi thủi bên bát cháo trắng phía phải.",
             "CH-1 vội bước nhanh tới cạnh bàn đỡ lấy tay bà nội đầy xót xa.",
             "CH-1 (Quân, giọng bàng hoàng đau xót hỏi bà)",
             "Bà nội! Ngoài sân bố mở tiệc mừng thọ mấy chục mâm linh đình, sao bà lại ngồi ăn cháo trắng trong buồng tối thế này?"),

            ("s07", "CU", "f01bo1", ["cucuc", "quan_somi"],
             "Trong buồng nhỏ: CH-1 (Cụ Cúc) bên phải vội nắm tay cháu nội CH-2 (Quân) bên trái, gượng cười che giấu lỗi cho con trai.",
             "CH-1 lắc đầu nhẹ khuyên cháu đừng ra ngoài trách bố.",
             "CH-1 (Cụ Cúc, giọng hiền hậu bao dung)",
             "Quân mới đi công tác về đấy à, con đừng trách bố nhé, tại tay bà run sợ bẩn cỗ nên bà tự xin ở đây thôi."),

            ("s08", "WIDE", "f01bo1", ["bactrong", "quan_somi", "cucuc"],
             "Trong căn buồng nhỏ: CH-1 (Bác Trọng) mở cửa bước vào bên trái, phân trần với con trai CH-2 (Quân) đứng giữa cạnh CH-3 (Cụ Cúc) bên phải.",
             "CH-1 chỉ vào tay mẹ già giải thích lý do giấu mẹ với con trai.",
             "CH-1 (Bác Trọng, giọng thản nhiên thực dụng)",
             "Quân về lúc nào thế? Tiệc hôm nay toàn khách quý, tay bà nội mày run thế kia ra bàn chỉ làm khách mất ngon!"),

            ("s09", "CU", "f01bo1", ["quan_somi"],
             "Trong buồng nhỏ: cận cảnh CH-1 (Quân mặc sơ mi trắng) nén chặt nỗi xót xa trong đáy mắt, cố tình giả vờ hùa theo ý bố.",
             "CH-1 nhìn bố gật đầu nói giọng tỉnh bơ để đưa bố ra bàn tiệc chính.",
             "CH-1 (Quân, cố nén nghẹn giả vờ đồng tình với bố)",
             "Bố nói phải đấy ạ, áo bà dính cháo mà tay cứ run thế này bước ra sảnh đúng là mất hết thể diện nhà mình."),

            ("s10", "CU", "f01bo1", ["cucuc"],
             "Trong buồng nhỏ: cận cảnh CH-1 (Cụ Cúc) sững người nhìn cháu nội, hai mắt đỏ hoe rơi lệ đau đớn.",
             "CH-1 cúi mặt nghẹn lời khi tưởng đứa cháu thương nhất cũng chê mình.",
             "CH-1 (Cụ Cúc, giọng nghẹn đắng rơi nước mắt)",
             "Quân ơi... đến cả cháu nội của bà mà giờ cũng chê bà bẩn thỉu xấu xí sao con?"),

            ("s11", "MED", "f01bo1", ["bactrong", "quan_somi"],
             "Trong buồng nhỏ: CH-1 (Bác Trọng) bên trái vỗ vai khen ngợi CH-2 (Quân) bên phải biết suy nghĩ thời thế.",
             "CH-2 mời bố ra ghế chủ tọa giữa sảnh lớn để tặng quà mừng.",
             "CH-1 (Bác Trọng, cười đắc ý vỗ vai con trai)",
             "Thanh niên đi làm xã hội phải thức thời như mày thế chứ! Ra sảnh ngồi với bố để nhận quà mừng nào!"),

            ("s12", "WIDE_CROWD", "f01bo2", ["bactrong", "quan_somi"],
             "Giữa sảnh tiệc mừng thọ đông người: CH-1 (Bác Trọng) ngồi chễm chệ bên trái bàn tiệc chính, CH-2 (Quân) đứng bên phải đặt chiếc hộp gỗ chạm khắc trang trọng lên mặt bàn.",
             "CH-1 nhìn chiếc hộp gỗ quý trên tay con trai với ánh mắt háo hức khoe của.",
             "CH-1 (Bác Trọng, cười lớn hãnh diện hỏi con trai)",
             "Con trai bố tâm lý quá! Trong hộp gỗ kia là nhân sâm ngàn năm hay vàng miếng đấy, mở ra cho bố chụp ảnh khoe nào!"),

            ("s13", "CU", "f01bo2", ["quan_somi"],
             "Tại sảnh tiệc: cận cảnh CH-1 (Quân) đứng bên phải nhìn thẳng bố với ánh mắt nghiêm nghị sâu thẳm.",
             "CH-1 đặt tay mở nắp hộp gỗ, giọng trầm vang rõ từng chữ.",
             "CH-1 (Quân, giọng điềm tĩnh sâu lắng)",
             "Không phải vàng miếng hay sâm ngoại đâu bố, thứ trong hộp này còn quý giá gấp vạn lần tiền bạc ngoài kia."),

            ("s14", "MED", "f01bo2", ["bactrong", "quan_somi"],
             "Tại bàn tiệc sang trọng: CH-2 (Quân) lấy từ hộp ra một chiếc bát nhôm cũ móp méo đặt lên bàn, khiến CH-1 (Bác Trọng) bên trái sầm mặt đập bàn tức giận.",
             "CH-1 chỉ tay vào chiếc bát nhôm cũ quát hỏi con trai.",
             "CH-1 (Bác Trọng, sầm mặt giận dữ quát con)",
             "Mày điên à Quân? Sao lại lôi cái bát nhôm đồng nát cũ rích này đặt lên bàn đại tiệc sang trọng của bố!"),

            ("s15", "CU", "f01bo2", ["quan_somi"],
             "Tại sảnh tiệc: cận cảnh CH-1 (Quân) hai mắt đỏ hoe nhìn thẳng vào mắt bố không chút né tránh.",
             "CH-1 nghẹn giọng nói rõ lý do vừa nãy phải đóng kịch trong buồng.",
             "CH-1 (Quân, mắt đỏ hoe nghẹn giọng thức tỉnh bố)",
             "Nãy con không nén đứt ruột giả vờ chê bà, thì người trọng sĩ diện như bố có chịu ngồi yên nghe sự thật này không?"),

            ("s16", "CU", "f01bo2", ["quan_somi"],
             "Tại sảnh tiệc (cận đặc tả): CH-1 (Quân) nâng chiếc bát nhôm móp méo lên, nước mắt lăn dài kể về tuổi thơ của bố.",
             "CH-1 nhìn thẳng sang trái nhắc lại kỷ vật bà cất đầu giường năm mươi năm.",
             "CH-1 (Quân, giọng nghẹn ngào lay động)",
             "Đây là bát tập ăn của bố năm mươi năm trước! Ngày bé bố ốm hất đổ cơm đầy áo bà, bà có nhốt bố vào buồng tối không?"),

            ("s17", "CU", "f01bo2", ["quan_somi", "bactrong"],
             "Tại sảnh tiệc: CH-1 (Quân) bên phải nghẹn giọng nhắc lại tai nạn giếng làng khiến CH-2 (Bác Trọng) bên trái bàng hoàng run rẩy.",
             "CH-1 nói rõ nguyên nhân đôi bàn tay bà nội bị run suốt đời.",
             "CH-1 (Quân, giọng run rẩy xúc động mạnh)",
             "Năm bố mười hai tuổi ngã giếng mùa đông, mười ngón tay bà bấu rách đá lạnh ngâm nước buốt cứu bố nên tay mới run suốt đời!"),

            ("s18", "WIDE_CROWD", "f01bo2", ["bactrong", "quan_somi"],
             "Toàn cảnh sảnh tiệc lặng phắc dưới phông đỏ mừng thọ: CH-2 (Quân) đứng bên phải đặt câu hỏi cuối cùng khiến CH-1 (Bác Trọng) ngồi chết lặng bên trái trước mặt quan khách.",
             "CH-2 nhìn bố hỏi câu thấm thía tận tâm can.",
             "CH-2 (Quân, giọng trầm vang xé lòng)",
             "Hai mươi năm nữa tay bố cũng run, nếu con nhốt bố vào nhà kho ăn cháo nguội để ngoài này đếm phong bì thì bố có đau lòng không?"),

            ("s19", "CU", "f01bo2", ["bactrong"],
             "Tại sảnh tiệc: cận cảnh gương mặt CH-1 (Bác Trọng 55 tuổi) giàn giụa nước mắt hối hận tột cùng.",
             "CH-1 bật khóc nghẹn ngào đứng bật dậy đi đón mẹ già.",
             "CH-1 (Bác Trọng, bật khóc nức nở ân hận)",
             "Đừng nói nữa Quân ơi... bố là thằng con bất hiếu vì chút sĩ diện hão! Đi với bố vào đón bà nội ra ngay con ơi!"),

            ("s20", "WIDE", "f01bo1", ["bactrong", "cucuc", "quan_somi"],
             "Trong căn buồng nhỏ: CH-1 (Bác Trọng) lao vào cúi gập người nắm chặt đôi bàn tay gầy của CH-2 (Cụ Cúc) bên phải, CH-3 (Quân) đứng cạnh rưng rưng.",
             "CH-1 khóc nghẹn áp bàn tay mẹ lên má mình xin tha thứ.",
             "CH-1 (Bác Trọng, nghẹn giọng xin lỗi mẹ ruột)",
             "Mẹ ơi con sai thật rồi! Con xin lỗi mẹ, để bố con con rước mẹ ra ghế chính mừng thọ mẹ nhé!"),

            ("s21", "WIDE_CROWD", "f01bo2", ["bactrong", "cucuc", "quan_somi"],
             "Toàn cảnh sảnh tiệc mừng thọ rực rỡ ấm áp: CH-1 (Bác Trọng) bên trái và CH-3 (Quân) bên phải trân trọng dìu CH-2 (Cụ Cúc mỉm cười hạnh phúc) bước ra giữa tiếng vỗ tay của quan khách.",
             "Ba thế hệ ông con cháu sum vầy bước đi tràn ngập tình thân.",
             None, ""),

            ("s22", "CU", "f01bo2", ["quan_somi", "cucuc"],
             "Giữa sảnh mừng thọ: CH-1 (Quân) đứng khoác vai bà nội CH-2 (Cụ Cúc), quay mặt nhìn thẳng ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera mỉm cười ấm áp trò chuyện cùng khán giả rồi khép môi.",
             "CH-1 (Quân, nhìn thẳng ống kính hỏi khán giả)",
             "Báo hiếu là trân trọng khi cha mẹ còn bên cạnh chứ đâu phải mâm cao cỗ đầy khoe thiên hạ, mọi người thấy Quân làm vậy đúng không ạ?"),
        ],
    },

    # =========================================================================
    # F02: Mẹ chồng tự ý hứa cho em gái chiếc xe hồi môn của con dâu (21 scenes)
    # Cast (G01 100% Canonical): Bà Hạnh (56t) — Tuấn (31t) — Thảo (28t) — Linh (24t)
    # =========================================================================
    "f02": {
        "title": "Mẹ chồng tự ý đem xe hồi môn của con dâu hứa cho em chồng và cái kết",
        "acts_bgm": [
            ("s01", "acoustic_gentle_day.mp3", 0.5, 0.90),
            ("s04", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s13", "dram_ltk.mp3", 0.0, 1.05),
        ],
        "board_items": [
            ("CH-1: Bà Hạnh 56t (G01_03c)", "bahanh"),
            ("CH-2: Tuấn 31t (G01_04c)", "tuan_vest"),
            ("CH-3: Thảo 28t (G01_05a)", "thao"),
            ("CH-4: Linh 24t (G01_08)", "linh"),
            ("BO-1: Phòng tủ đồ Tuấn Thảo", "f02bo1"),
            ("BO-2: Phòng khách nhà Bà Hạnh", "f02bo2"),
        ],
        "shots": [
            ("s01", "WIDE", "f02bo1", ["linh", "thao"],
             "Phòng ngủ và tủ đồ hiện đại của vợ chồng Tuấn Thảo: CH-1 (Linh tóc vàng sành điệu) bên trái đang tự tiện lục túi xách váy áo trước tủ kính thì chị dâu CH-2 (Thảo mặc váy trắng) bên phải mở cửa bắt gặp.",
             "CH-1 thản nhiên ướm túi xách của chị dâu trước gương không chút ngại ngùng.",
             "CH-1 (Linh, giọng tỉnh bơ tự tiện)",
             "Đồ hiệu của chị Thảo để không trong tủ phí quá, em sang lấy mấy món mặc đi chơi chút nhé!"),

            ("s02", "CU", "f02bo1", ["thao", "linh"],
             "Trong phòng ngủ: CH-1 (Thảo) đứng bên phải nhìn em chồng CH-2 (Linh) bên trái, nhẹ nhàng nhưng thẳng thắn góp ý.",
             "CH-1 nói lời lịch sự nhắc nhở phép tắc tối thiểu trong nhà.",
             "CH-1 (Thảo, giọng điềm đạm nhã nhặn)",
             "Linh à, phòng riêng của anh chị em muốn mượn đồ gì thì ít nhất cũng nên hỏi chị một tiếng chứ."),

            ("s03", "WIDE", "f02bo2", ["bahanh", "linh", "thao"],
             "Phòng khách sang trọng: mẹ chồng CH-1 (Bà Hạnh mặc nhung đỏ) ngồi sofa bên trái kéo CH-2 (Linh) ngồi cạnh bênh vực trước mặt con dâu CH-3 (Thảo) đứng bên phải.",
             "CH-1 xua tay trách con dâu hẹp hòi rồi buột miệng nhắc chuyện chiếc xe hơi.",
             "CH-1 (Bà Hạnh, giọng bề trên thiên vị con gái)",
             "Người một nhà tính toán làm gì! Sẵn tiện mẹ bảo luôn, chiếc xe của con sang tuần giao cho cái Linh đi nhé!"),

            ("s04", "CU", "f02bo2", ["thao"],
             "Trong phòng khách: cận cảnh CH-1 (Thảo) đứng bên phải mở to mắt ngơ ngác nhìn mẹ chồng và em chồng bên trái.",
             "CH-1 sững sờ hỏi lại vì hoàn toàn không hề biết chuyện tặng xe.",
             "CH-1 (Thảo, ngạc nhiên sững sờ hỏi lại)",
             "Xe nào cơ ạ? Dạ thưa mẹ, con hứa tặng chiếc xe hồi môn của con cho em Linh từ bao giờ thế ạ?"),

            ("s05", "CU", "f02bo2", ["bahanh"],
             "Trong phòng khách: cận cảnh CH-1 (Bà Hạnh) ngồi bên trái hất cằm thản nhiên nhận quyền quyết định thay con dâu.",
             "CH-1 phẩy tay coi tài sản của con dâu như đồ chung của bà.",
             "CH-1 (Bà Hạnh, giọng thản nhiên áp đặt)",
             "Là chính mẹ hứa cho đấy! Vợ chồng con có xe của thằng Tuấn rồi, chiếc xe kia để dư thì nhường cho em gái!"),

            ("s06", "CU", "f02bo2", ["linh", "thao"],
             "Trong phòng khách: CH-1 (Linh) bên trái vênh mặt hạch sách CH-2 (Thảo) đứng bên phải.",
             "CH-1 trừng mắt ép chị dâu phải giao chìa khóa xe.",
             "CH-1 (Linh, giọng đỏng đảnh ngang ngược)",
             "Mẹ đã mở lời hứa với em rồi, chị làm chị dâu trưởng thì đừng có sống ích kỷ lật lọng như thế chứ!"),

            ("s07", "MED", "f02bo2", ["thao", "bahanh"],
             "Trong phòng khách: CH-1 (Thảo) bên phải cố giữ bình tĩnh giải thích lý do với CH-2 (Bà Hạnh) bên trái.",
             "CH-1 nói rõ chiếc xe là của hồi môn bố mẹ ruột mua cho cô đi làm.",
             "CH-1 (Thảo, giọng lễ phép nhưng kiên quyết)",
             "Mẹ chưa hỏi con sao lại tự quyết ạ? Xe đó bố mẹ đẻ tặng con đi làm hằng ngày, con không cho được đâu ạ."),

            ("s08", "MED", "f02bo2", ["bahanh", "tuan_vest"],
             "Trong phòng khách sang trọng: người chồng CH-2 (Tuấn mặc vest đen) từ bên phải sải bước tới đứng đối diện nghiêm mặt hỏi thẳng mẹ CH-1 (Bà Hạnh mặc nhung đỏ) bên trái.",
             "CH-2 đứng đĩnh đạc nghiêm nghị bảo vệ vợ trước mặt mẹ.",
             "CH-2 (Tuấn, giọng trầm nghiêm nghị hỏi thẳng)",
             "Mẹ với cái Linh đang làm ầm chuyện gì đấy? Vợ chồng con giúp đỡ cái Linh bao năm nay còn chưa đủ sao ạ!"),

            ("s09", "CU", "f02bo2", ["bahanh"],
             "Trong phòng khách: CH-1 (Bà Hạnh) bên trái nhíu mày trách ngược con trai tính toán với em ruột.",
             "CH-1 nhìn sang phải mắng Tuấn bênh vợ.",
             "CH-1 (Bà Hạnh, giọng bực bội trách con trai)",
             "Có mỗi chiếc xe cũ đi lại thôi mà vợ chồng mày cũng tính toán chi ly với em gái ruột làm gì!"),

            ("s10", "CU", "f02bo2", ["tuan_vest"],
             "Trong phòng khách: cận cảnh CH-1 (Tuấn mặc vest đen) bên phải đanh mặt kể rõ từng khoản vợ đã lo cho em chồng.",
             "CH-1 nhìn thẳng sang Linh bên trái vạch trần sự vô ơn.",
             "CH-1 (Tuấn, giọng đanh thép rõ ràng)",
             "Đám cưới Linh vợ chồng con lo, Thảo còn lấy tiền riêng cho nó vay mở tiệm chưa trả mà giờ còn đòi cả xe!"),

            ("s11", "CU", "f02bo2", ["linh"],
             "Trong phòng khách: cận cảnh CH-1 (Linh) bên trái giậm chân hờn dỗi chống chế với anh trai.",
             "CH-1 bĩu môi coi chuyện lấy đồ của chị dâu là chuyện nhỏ.",
             "CH-1 (Linh, giọng dỗi hờn trơ trẽn)",
             "Sao anh nói em nặng lời thế! Chỗ chị em trong nhà em mượn vài món đồ thôi mà anh cũng lôi chuyện cũ ra!"),

            ("s12", "MED", "f02bo2", ["tuan_vest", "linh"],
             "Trong phòng khách: CH-1 (Tuấn) bên phải chỉ thẳng vào thói quen xấu của em gái CH-2 (Linh) bên trái.",
             "CH-1 nghiêm khắc vạch rõ ranh giới khiến Linh câm nín.",
             "CH-1 (Tuấn, giọng nghiêm khắc chấn chỉnh em gái)",
             "Lần nào sang em cũng lục tủ lấy váy áo, mỹ phẩm đến cả trang sức cưới! Chị dâu nhịn em là vì cô ấy tử tế đấy!"),

            ("s13", "CU", "f02bo2", ["bahanh"],
             "Trong phòng khách: CH-1 (Bà Hạnh) bên trái tức giận đập nhẹ tay lên ghế quát lớn át lời con trai.",
             "CH-1 trừng mắt lấy quyền làm mẹ ra ép Tuấn im miệng.",
             "CH-1 (Bà Hạnh, giọng cao vút giận dữ)",
             "Tuấn, mày câm miệng ngay! Nó là em gái ruột thịt của mày, vì con vợ mà mày dám hỗn hào với mẹ à!"),

            ("s14", "MED", "f02bo2", ["thao", "tuan_vest"],
             "Trong phòng khách: CH-1 (Thảo) bên phải kéo nhẹ tay áo chồng khuyên nhủ, nhưng CH-2 (Tuấn) nắm chặt bàn tay vợ đầy bản lĩnh.",
             "CH-2 quay sang trấn an vợ rồi nhìn thẳng về phía mẹ.",
             "CH-2 (Tuấn, nắm chặt tay vợ tuyên bố dứt khoát)",
             "Em đừng nhịn nữa, anh nhịn đủ rồi! Từ hôm nay trong nhà này không ai được phép bắt nạt vợ anh thêm lần nào nữa!"),

            ("s15", "CU", "f02bo2", ["tuan_vest"],
             "Trong phòng khách: cận cảnh CH-1 (Tuấn) bên phải nhìn thẳng mẹ với ánh mắt thất vọng nhưng điềm tĩnh.",
             "CH-1 nói lời thấu tình đạt lý đánh thẳng vào sự thiên vị của mẹ.",
             "CH-1 (Tuấn, giọng trầm sâu thẳng thắn với mẹ)",
             "Bao năm mẹ hưởng sự chăm sóc hiếu thảo của Thảo, sao mẹ lại dung túng cái Linh nhắm tới cả xe hồi môn của cô ấy?"),

            ("s16", "CU", "f02bo2", ["tuan_vest", "linh"],
             "Trong phòng khách: CH-1 (Tuấn) bên phải quay sang dạy thẳng em gái CH-2 (Linh) đang cúi gằm bên trái.",
             "CH-1 dứt khoát cắt đứt thói ỷ lại của em gái đã lập gia đình.",
             "CH-1 (Tuấn, giọng rắn rỏi dứt khoát)",
             "Em lấy chồng rồi, muốn lái xe sang thì tự lao động mà mua! Chị dâu không phải mẹ ruột, không có nghĩa vụ nuôi em!"),

            ("s17", "CU", "f02bo2", ["bahanh"],
             "Trong phòng khách: CH-1 (Bà Hạnh) bên trái nghẹn lời lu loa trách con trai bất hiếu.",
             "CH-1 thở dài than vãn sợ tuổi già không cậy nhờ được con.",
             "CH-1 (Bà Hạnh, giọng hờn dỗi trách móc)",
             "Đúng là đồ con trai bênh vợ quên mẹ! Sau này mẹ già yếu còn trông cậy gì được vào vợ chồng chúng mày nữa!"),

            ("s18", "WIDE", "f02bo2", ["bahanh", "tuan_vest", "thao"],
             "Toàn cảnh phòng khách: CH-2 (Tuấn) đứng bên phải khoác vai bảo vệ CH-3 (Thảo), nói rõ đạo lý phân minh trước mặt CH-1 (Bà Hạnh) bên trái.",
             "CH-2 khẳng định trọn đạo hiếu nhưng giữ vững quyền tài sản riêng của vợ.",
             "CH-2 (Tuấn, giọng đĩnh đạc phân minh)",
             "Đạo hiếu phụng dưỡng mẹ tụi con tuyệt đối không thiếu, nhưng xe hồi môn và đồ riêng của Thảo ngay cả con cũng không quyền tự quyết!"),

            ("s19", "CU", "f02bo1", ["thao", "tuan_vest"],
             "Trong phòng riêng ấm áp: CH-1 (Thảo) mắt long lanh xúc động ngước nhìn chồng CH-2 (Tuấn) bên cạnh.",
             "CH-1 mỉm cười hạnh phúc cảm ơn người chồng thấu hiểu.",
             "CH-1 (Thảo, giọng dịu dàng xúc động)",
             "Em cảm ơn chồng nhiều lắm, chỉ cần anh luôn thấu hiểu và đứng về phía lẽ phải là bao ấm ức em cũng quên hết."),

            ("s20", "MED", "f02bo1", ["tuan_vest", "thao"],
             "Trong phòng riêng sáng ấm: CH-1 (Tuấn) dịu dàng nắm hai bàn tay vợ CH-2 (Thảo), cả hai nhìn nhau mỉm cười bình yên.",
             "Khoảnh khắc vợ chồng đồng lòng ấm áp.",
             None, ""),

            ("s21", "CU", "f02bo1", ["tuan_vest", "thao"],
             "Trong phòng riêng: CH-1 (Tuấn) đứng cạnh vợ CH-2 (Thảo), quay mặt nhìn thẳng ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera trò chuyện chân thành rồi mỉm cười khép môi.",
             "CH-1 (Tuấn, nhìn thẳng ống kính hỏi khán giả)",
             "Giữ trọn chữ hiếu với mẹ nhưng kiên quyết bảo vệ tài sản hồi môn và danh dự của vợ, cả nhà thấy Tuấn xử lý vậy đúng không ạ?"),
        ],
    },

    # =========================================================================
    # F03: Mẹ nghèo áo vá dự lễ khánh thành trụ sở công ty, con trai cõng mẹ trên thảm đỏ (20 scenes)
    # Cast (G05 + G07): Bà Mận (63t) — Giám đốc Hiếu (31t) — Lễ tân Lê (26t) — Quản lý Khang (29t)
    # =========================================================================
    "f03": {
        "title": "Mẹ quê mặc áo vá dự lễ khánh thành công ty và cái kết con trai cõng mẹ trên thảm đỏ",
        "acts_bgm": [
            ("s01", "acoustic_warm_morning.mp3", 2.0, 0.90),
            ("s02", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s15", "piano_warm_family.mp3", 4.0, 1.08),
        ],
        "board_items": [
            ("CH-1: Bà Mận 63t (G05_01)", "baman"),
            ("CH-2: Giám đốc Hiếu 31t (G05_02b)", "hieu_vest"),
            ("CH-3: Lễ tân Lê 26t (G07_04 Mới)", "le_letan"),
            ("CH-4: Quản lý Khang 29t (G07_05 Mới)", "khang_ql"),
            ("BO-1: Thảm đỏ khánh thành đông người", "f03bo1"),
            ("BO-2: Bậc thềm lễ đài khánh thành", "f03bo2"),
        ],
        "shots": [
            ("s01", "WIDE_CROWD", "f03bo1", ["baman"],
             "Quảng trường thảm đỏ lễ khánh thành trụ sở công ty đông khách mời đứng hai bên: CH-1 (Bà Mận 63 tuổi mặc đồ nâu sờn vá ôm túi vải) rụt rè bước ở mép thảm đỏ ngóng tìm con trai.",
             "CH-1 nhìn quanh đám đông sang trọng với vẻ bỡ ngỡ sợ làm vướng lối đi.",
             "CH-1 (Bà Mận, nói khẽ bỡ ngỡ một mình)",
             "Trụ sở mới đông người sang trọng quá, không biết thằng Hiếu đang đứng chỗ nào mà mình chẳng dám bước vào..."),

            ("s02", "WIDE_CROWD", "f03bo1", ["baman", "le_letan", "khang_ql"],
             "Trên thảm đỏ đông người: CH-2 (Lê mặc đầm kem) và CH-3 (Khang mặc vest xanh) từ bên phải bước tới chắn trước mặt CH-1 (Bà Mận) bên trái với thái độ khinh khỉnh.",
             "CH-2 chỉ tay chê trách sao để người quê rách rưới bước lên thảm đỏ.",
             "CH-2 (Lê, giọng chảnh chọe chê bai)",
             "Anh Khang nhìn kìa, bảo vệ trực cổng kiểu gì lại để bà lão mặc đồ vá chằng chịt bước lên thảm đỏ công ty thế này!"),

            ("s03", "CU", "f03bo1", ["khang_ql", "baman"],
             "Trên thảm đỏ: CH-1 (Khang mặc vest xanh) bên phải hất mặt xua tay đuổi CH-2 (Bà Mận) bên trái.",
             "CH-1 nhíu mày ra lệnh đuổi bà cụ rời khỏi khu vực đón khách.",
             "CH-1 (Khang, giọng hách dịch trịch thượng)",
             "Này bà cụ kia, nay là đại lễ khánh thành trụ sở tập đoàn lớn, không phải chỗ phát quà từ thiện đâu, mời bà đi ngay!"),

            ("s04", "CU", "f03bo1", ["baman"],
             "Trên thảm đỏ: cận cảnh CH-1 (Bà Mận ôm chặt túi vải) bên trái khép nép giải thích lễ phép với hai nhân viên bên phải.",
             "CH-1 gượng cười hiền lành thưa rõ lý do lặn lội từ quê lên.",
             "CH-1 (Bà Mận, giọng nhỏ nhẹ chất phác)",
             "Dạ cô cậu thông cảm, tôi không phải ăn xin đâu ạ, tôi ở dưới quê bắt xe lên thăm con trai làm việc ở công ty mình."),

            ("s05", "CU", "f03bo1", ["le_letan"],
             "Trên thảm đỏ: cận cảnh CH-1 (Lê mặc đầm kem) bên phải nhếch môi cười khẩy đánh giá qua bộ quần áo vá.",
             "CH-1 khoanh tay buông lời miệt thị hai mẹ con bà cụ.",
             "CH-1 (Lê, giọng mỉa mai cay độc)",
             "Áo quần vá đụp thế kia thì con bà giỏi lắm cũng chỉ làm bảo vệ ca đêm hay tạp vụ thôi! Vòng ra cửa sau mà đợi!"),

            ("s06", "MED", "f03bo1", ["baman", "khang_ql", "le_letan"],
             "Trên thảm đỏ: CH-2 (Khang) bên phải xua mạnh tay khiến CH-1 (Bà Mận) loạng choạng suýt vấp, CH-3 (Lê) vội lùi lại la lối vì sợ bụi bẩn vấy lên giày cao gót.",
             "CH-3 nhăn nhó chỉ xuống mũi giày mắng nhiếc người mẹ già.",
             "CH-3 (Lê, giọng chanh chua đỏng đảnh)",
             "Trời ơi xém chút bụi bẩn dưới dép bà quệt hỏng đôi giày mấy triệu của tôi rồi! Đúng là đồ nhà quê phiền phức!"),

            ("s07", "CU", "f03bo1", ["baman"],
             "Trên thảm đỏ: cận cảnh CH-1 (Bà Mận) bên trái hoảng sợ cúi đầu liên tục xin lỗi để bảo vệ công việc cho con trai.",
             "CH-1 rưng rưng mắt van nài hai người nhân viên.",
             "CH-1 (Bà Mận, giọng run run cam chịu)",
             "Dạ cho tôi xin lỗi cô cậu, để tôi lùi ra ngoài cổng liền, xin cô cậu đừng làm khó công việc của con trai tôi nhé!"),

            ("s08", "WIDE_CROWD", "f03bo1", ["baman", "hieu_vest", "khang_ql"],
             "Giữa thảm đỏ đông khách ngoái nhìn: Tổng giám đốc CH-2 (Hiếu mặc vest đen) sải bước nhanh tới đứng chắn bảo vệ mẹ CH-1 (Bà Mận) bên trái, quắc mắt nhìn CH-3 (Khang) bên phải.",
             "CH-2 đỡ lấy tay mẹ già, cất giọng trầm uy quyền làm cả sảnh lặng đi.",
             "CH-2 (Hiếu, giọng đanh thép vang dội)",
             "Dừng tay lại ngay! Trước sảnh công ty tôi mà ai cho phép các người dám xô đẩy xúc phạm mẹ ruột của tôi hả!"),

            ("s09", "CU", "f03bo1", ["hieu_vest", "baman"],
             "Trên thảm đỏ: CH-1 (Hiếu) bên phải quay sang nắm chặt đôi bàn tay thô ráp của mẹ CH-2 (Bà Mận) bên trái đầy xót thương.",
             "CH-1 ân cần hỏi thăm mẹ với đôi mắt đỏ hoe.",
             "CH-1 (Hiếu, giọng nghẹn ngào hiếu thảo)",
             "Mẹ ơi! Sao mẹ lặn lội từ quê lên tận đây mà không gọi điện báo trước để con đánh xe ra bến đón mẹ?"),

            ("s10", "CU", "f03bo1", ["baman", "hieu_vest"],
             "Trên thảm đỏ: CH-1 (Bà Mận) bên trái ngước nhìn con trai CH-2 (Hiếu) mỉm cười hiền hậu quên hết tủi thân.",
             "CH-1 vỗ nhẹ lên tay con trai giải thích vì sợ con bận việc lớn.",
             "CH-1 (Bà Mận, giọng ấm áp thương con)",
             "Mẹ sợ ngày khánh thành con bận trăm công nghìn việc nên không dám gọi, mẹ chỉ tính đứng xa nhìn con một lát thôi."),

            ("s11", "MED", "f03bo1", ["khang_ql", "le_letan"],
             "Trên thảm đỏ: CH-1 (Khang) và CH-2 (Lê) bên phải tái mét mặt mày đứng khép nép cúi đầu run rẩy.",
             "Cả hai lắp bắp bàng hoàng khi biết thân phận thật của bà cụ.",
             "CH-1 (Khang, giọng lắp bắp hoảng hốt)",
             "Dạ thưa Tổng giám đốc Hiếu... bà cụ mặc áo vá này thực sự là mẹ đẻ của sếp sao ạ? Tụi em lỡ mắt không biết!"),

            ("s12", "CU", "f03bo1", ["hieu_vest"],
             "Trên thảm đỏ: cận cảnh CH-1 (Hiếu mặc vest đen) nhìn thẳng sang phải với ánh mắt rực lửa tự hào và phẫn nộ.",
             "CH-1 tuyên bố dõng dạc về công ơn sinh thành của mẹ trước toàn thể khách mời.",
             "CH-1 (Hiếu, giọng trầm vang đầy tự tôn)",
             "Tấm áo sờn vá các người chê cười là mồ hôi nước mắt mẹ tôi bán rau khâu thuê suốt đời để nuôi tôi dựng nên cơ nghiệp này!"),

            ("s13", "CU", "f03bo1", ["le_letan", "khang_ql"],
             "Trên thảm đỏ: cận cảnh CH-1 (Lê) bên phải rối rít cúi đầu viện cớ thanh minh xin tha tội.",
             "CH-1 chắp tay năn nỉ mong giữ lại ghế làm việc.",
             "CH-1 (Lê, giọng hốt hoảng biện minh)",
             "Sếp Hiếu tha lỗi cho tụi em với ạ! Chỉ tại bác gái không nói rõ là mẹ sếp nên tụi em mới hiểu lầm nhắc nhở thôi!"),

            ("s14", "CU", "f03bo1", ["hieu_vest"],
             "Trên thảm đỏ: cận cảnh CH-1 (Hiếu) nghiêm mặt bác bỏ lời ngụy biện và ra quyết định kỷ luật dứt khoát.",
             "CH-1 phất tay sa thải hai kẻ coi người bằng nửa con mắt.",
             "CH-1 (Hiếu, giọng lạnh băng dứt khoát)",
             "Thế gặp mẹ già của người khác thì các người có quyền chà đạp à? Công ty tôi không chứa người thiếu đạo đức, hai người nghỉ việc ngay!"),

            ("s15", "CU", "f03bo1", ["baman", "hieu_vest"],
             "Trên thảm đỏ: CH-1 (Bà Mận) bên trái kéo nhẹ tay áo CH-2 (Hiếu) bên phải, ngại ngần sợ bộ đồ cũ làm con mất mặt với khách quý.",
             "CH-1 lùi nhẹ nửa bước nhường con trai lên sân khấu một mình.",
             "CH-1 (Bà Mận, giọng e dè lo cho con)",
             "Thôi con trai ơi, bao nhiêu khách sang đang nhìn, mẹ áo quần cũ kỹ đứng cạnh sợ làm Giám đốc như con mất mặt..."),

            ("s16", "CU", "f03bo1", ["hieu_vest", "baman"],
             "Trên thảm đỏ: CH-1 (Hiếu) nắm chặt hai vai mẹ CH-2 (Bà Mận), mỉm cười rưng rưng nói lời tận đáy lòng.",
             "CH-1 nhìn mẹ đầy tự hào và kính yêu.",
             "CH-1 (Hiếu, giọng trầm ấm chân tình)",
             "Ngoài xã hội con là Giám đốc, nhưng trước mặt mẹ con mãi là thằng Hiếu bé nhỏ của mẹ! Có mẹ mới có con hôm nay!"),

            ("s17", "WIDE_CROWD", "f03bo2", ["hieu_vest", "baman"],
             "Trước bậc thềm lễ đài trải thảm đỏ đông quan khách đứng hai bên: thấy đôi chân mẹ mỏi nhừ sau quãng đường đi bộ dài, CH-1 (Hiếu mặc vest) quỳ thấp xuống trước mặt CH-2 (Bà Mận) mời mẹ lên lưng.",
             "CH-1 ân cần xoay người đón mẹ lên vai giữa ánh mắt xúc động của cả quảng trường.",
             "CH-1 (Hiếu, giọng xúc động tha thiết)",
             "Chân mẹ đi bộ tìm con mỏi rát hết rồi! Mẹ lên lưng đi, để hôm nay con trai cõng mẹ bước lên lễ đài danh dự nhé!"),

            ("s18", "MED", "f03bo2", ["hieu_vest", "baman"],
             "Trên bậc thềm thảm đỏ lễ đài: CH-1 (Hiếu) đỡ mẹ CH-2 (Bà Mận đang rơi nước mắt hạnh phúc) đứng cạnh mình ở vị trí trang trọng nhất.",
             "Hai mẹ con nắm chặt tay nhau trong niềm tự hào nghẹn ngào.",
             "CH-1 (Hiếu, giọng nghẹn ngào ấm áp)",
             "Ngày xưa tấm lưng gầy của mẹ cõng con đi qua bao giông bão, từ nay hãy để con làm đôi chân đưa mẹ sống đời bình yên!"),

            ("s19", "WIDE_CROWD", "f03bo2", ["hieu_vest", "baman"],
             "Toàn cảnh bậc thềm lễ đài khánh thành rực rỡ hoa tươi: CH-1 (Hiếu) khoác vai CH-2 (Bà Mận mỉm cười hiền từ) đứng giữa hai hàng quan khách vỗ tay chúc mừng nồng nhiệt.",
             "Khung cảnh vinh quy báo hiếu đầy xúc động trên thảm đỏ.",
             None, ""),

            ("s20", "CU", "f03bo2", ["hieu_vest", "baman"],
             "Trên lễ đài thảm đỏ: CH-1 (Hiếu) đứng cạnh mẹ CH-2 (Bà Mận), quay mặt nhìn thẳng ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera mỉm cười đĩnh đạc trò chuyện rồi khép môi.",
             "CH-1 (Hiếu, nhìn thẳng ống kính hỏi khán giả)",
             "Vinh hoa phú quý mấy cũng không sánh bằng tấm áo tảo tần của mẹ nghèo, mọi người thấy Hiếu làm vậy có đúng đạo làm con không ạ?"),
        ],
    },

    # =========================================================================
    # F04: Thăng chức Trưởng khoa, nhà vợ khinh bố quê vôi ăn nát tay (21 scenes)
    # Cast (G08 NEW BRANCH — 0% overlap!): Ông Lộc (63t) — Anh Hải (36t) — Bác sĩ Khoa (31t)
    #                                      Vợ Châu (28t) — Bố vợ Ông Đạt (58t) — Mẹ vợ Bà Quý (55t)
    # =========================================================================
    "f04": {
        "title": "Con trai lên Trưởng khoa nhà vợ khinh bố quê làm thợ xây vôi ăn sần tay",
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s09", "dram_ltk.mp3", 0.0, 1.05),
            ("s18", "piano_warm_family.mp3", 4.0, 1.06),
        ],
        "board_items": [
            ("CH-1: Ông Lộc 63t (G08_01 Mới)", "ongloc"),
            ("CH-2: Anh Hải 36t (G08_02 Mới)", "hai_anhca"),
            ("CH-3: Bác sĩ Khoa 31t (G08_03 Mới)", "khoa_bs"),
            ("CH-4: Vợ Châu 28t (G08_04 Mới)", "chau_vo"),
            ("CH-5: Bố vợ Ông Đạt 58t (G08_05 Mới)", "ongdat"),
            ("CH-6: Mẹ vợ Bà Quý 55t (G08_06 Mới)", "baquy"),
            ("BO-1: Sảnh tiệc Trưởng khoa đông khách", "f04bo1"),
        ],
        "shots": [
            ("s01", "WIDE_CROWD", "f04bo1", ["ongloc", "hai_anhca", "baquy"],
             "Sảnh tiệc khách sạn sang trọng đông khách mời ngồi bàn tròn dưới đèn chùm: hai bố con quê mùa CH-1 (Ông Lộc 63 tuổi) và CH-2 (Hải 36 tuổi) đứng khép nép bên trái bị bà thông gia CH-3 (Bà Quý mặc áo dài nhung) chắn ngang bên phải.",
             "CH-3 chống nạnh chỉ tay xua đuổi hai bố con nhà quê ngay giữa sảnh tiệc.",
             "CH-3 (Bà Quý, giọng chua ngoa khinh miệt)",
             "Này đây là khách sạn sang trọng chứ cái chợ quê à? Ai cho hai bố con thợ hồ mò vào bàn VIP ngồi thế hả!"),

            ("s02", "CU", "f04bo1", ["chau_vo"],
             "Trong sảnh tiệc: cận cảnh cô con dâu CH-1 (Châu mặc đầm dạ tiệc đỏ rượu) đứng bên phải nhăn mặt bĩu môi nhìn sang trái.",
             "CH-1 khoanh tay chê bai bộ dạng lấm bụi đường xa của bố chồng và anh chồng.",
             "CH-1 (Châu, giọng kiêu kỳ chán ghét)",
             "Trông quần áo với bàn tay đầy sẹo vôi vữa kìa! Thấy chồng tôi vừa lên Trưởng khoa là vội bắt xe lên ăn trực à?"),

            ("s03", "CU", "f04bo1", ["ongdat"],
             "Trong sảnh tiệc: cận cảnh bố vợ CH-1 (Ông Đạt 58 tuổi mặc vest kẻ xám ghi lê) bên phải hất hàm ra lệnh đuổi khách.",
             "CH-1 phẩy tay ngạo mạn coi thường thông gia dưới quê.",
             "CH-1 (Ông Đạt, giọng hách dịch bề trên)",
             "Hôm nay toàn bác sĩ danh giá với khách quý nhà tôi, hai người mau ra bến bắt xe về quê đừng làm bẩn bữa tiệc!"),

            ("s04", "CU", "f04bo1", ["hai_anhca", "ongloc"],
             "Trong sảnh tiệc: người anh cả CH-1 (Hải mặc áo caro cũ) đứng che nhẹ trước bố CH-2 (Ông Lộc) bên trái, cúi đầu lễ phép phân trần.",
             "CH-1 nhỏ nhẹ xin phép chỉ nhìn em trai nhận chức ít phút rồi về.",
             "CH-1 (Hải, giọng thật thà nhẫn nhịn)",
             "Dạ hai bác và thím bớt giận, bố con cháu đi xe đò suốt đêm chỉ mong nhìn chú Khoa khoác áo Trưởng khoa năm phút thôi ạ."),

            ("s05", "CU", "f04bo1", ["baquy"],
             "Trong sảnh tiệc: cận cảnh CH-1 (Bà Quý mặc áo dài nhung xanh đen) bên phải cười khẩy buông lời cay nghiệt.",
             "CH-1 liếc xéo mắng nhiếc không chút nể nang.",
             "CH-1 (Bà Quý, giọng cay độc sắc lẻm)",
             "Thôi đừng kể khổ nữa! Đúng là giống đỉa đói bám càng, đứng thêm phút nào làm mất mặt thông gia chúng tôi phút đấy!"),

            ("s06", "WIDE_CROWD", "f04bo1", ["ongloc", "khoa_bs", "chau_vo"],
             "Giữa sảnh tiệc đông quan khách: bác sĩ CH-2 (Khoa mặc blouse trắng sơ mi cà vạt) vừa bước vào giữa thì vợ CH-3 (Châu) bên phải lập tức chỉ tay sang CH-1 (Ông Lộc) bên trái giục chồng đuổi đi.",
             "CH-3 kéo tay chồng ép phải chọn thể diện nhà ngoại.",
             "CH-3 (Châu, giọng gắt gỏng ép chồng)",
             "Anh Khoa ra đây mà giải quyết đi! Đưa ngay ông bố với ông anh nhếch nhác của anh về quê kẻo đồng nghiệp cười vào mặt!"),

            ("s07", "CU", "f04bo1", ["ongloc", "khoa_bs"],
             "Trong sảnh tiệc: người cha già CH-1 (Ông Lộc) bên trái rưng rưng nắm tay áo CH-2 (Khoa), cố mỉm cười hiền từ xin tự rút lui để giữ sự nghiệp cho con.",
             "CH-1 vỗ nhẹ tay con trai rồi quay bước định rời đi trong tủi nhục.",
             "CH-1 (Ông Lộc, giọng nghẹn ngào thương con)",
             "Thôi Khoa ơi, thấy con thành tài là bố mãn nguyện cả đời rồi, đừng vì bố với anh Hải mà ảnh hưởng chức Trưởng khoa nhé."),

            ("s08", "CU", "f04bo1", ["ongdat"],
             "Trong sảnh tiệc: cận cảnh CH-1 (Ông Đạt) bên phải nhếch mép hối thúc hai bố con bước nhanh ra cửa.",
             "CH-1 khoanh tay nhìn theo đầy ngạo mạn.",
             "CH-1 (Ông Đạt, giọng khinh khỉnh đuổi khéo)",
             "Biết điều thế thì mau bước ra cửa sau đi, đứng lâu mùi vôi vữa xi măng làm khách khứa bàn tiệc mất cả ngon!"),

            ("s09", "WIDE_CROWD", "f04bo1", ["ongloc", "khoa_bs", "ongdat"],
             "Toàn cảnh cao trào giữa sảnh tiệc: CH-2 (Khoa) nắm chặt tay giữ CH-1 (Ông Lộc) đứng lại bên trái, rồi sải bước chắn phía trước đối diện thẳng mặt bố vợ CH-3 (Ông Đạt) bên phải.",
             "CH-2 quắc mắt cất giọng đanh thép khiến cả sảnh tiệc nín lặng.",
             "CH-2 (Khoa, giọng đanh thép uy nghiêm)",
             "Đủ lắm rồi! Tôi tuyên bố rõ tại đây, trên đời này không một ai có quyền bắt cha và anh trai tôi cúi đầu chịu nhục!"),

            ("s10", "CU", "f04bo1", ["baquy"],
             "Trong sảnh tiệc: CH-1 (Bà Quý) bên phải trố mắt tức tối lu loa với quan khách xung quanh.",
             "CH-1 chỉ tay mắng con rể vừa thăng chức đã qua cầu rút ván.",
             "CH-1 (Bà Quý, giọng cao vút lu loa)",
             "Mọi người xem kìa, thằng rể nhà này vừa lên ghế Trưởng khoa đã cậy quyền cậy thế đứng ra mắng cả nhà thông gia đấy!"),

            ("s11", "CU", "f04bo1", ["khoa_bs", "ongloc"],
             "Trong sảnh tiệc: CH-1 (Khoa) bên trái hai mắt đỏ ngầu xúc động nâng đôi bàn tay thô ráp sần sùi của cha CH-2 (Ông Lộc) lên trước ngực.",
             "CH-1 nghẹn giọng kể rõ nguồn gốc từng đồng học phí nuôi mình thành bác sĩ.",
             "CH-1 (Khoa, mắt đỏ hoe nghẹn giọng tự hào)",
             "Bảy năm tôi học trường Y, từng đồng học phí đều vắt từ đôi bàn tay bị vôi sống ăn nát đầy sẹo này của bố tôi đấy!"),

            ("s12", "MED", "f04bo1", ["hai_anhca", "khoa_bs"],
             "Trong sảnh tiệc: CH-2 (Khoa) đặt bàn tay lên vai anh cả CH-1 (Hải đang rưng rưng cúi mặt) bên trái, nói vang sự hy sinh của anh trai.",
             "CH-2 nhìn thẳng sang nhà vợ bên phải bằng ánh mắt kiên định.",
             "CH-2 (Khoa, giọng nghẹn vang thấm thía)",
             "Còn người anh các người chê thất học này đã tự cất giấy báo đại học năm mười tám tuổi, vác vạn bao xi măng nuôi tôi thành tài!"),

            ("s13", "CU", "f04bo1", ["khoa_bs"],
             "Trong sảnh tiệc (cận đặc tả): CH-1 (Khoa) nhìn thẳng sang phải tuyên bố sẵn sàng bỏ chức vụ để giữ trọn chữ hiếu.",
             "CH-1 đặt tay lên vạt áo blouse trắng khẳng định khí phách.",
             "CH-1 (Khoa, giọng rắn rỏi bất khuất)",
             "Nếu làm Trưởng khoa mà phải đứng nhìn cha anh mình bị sỉ nhục, tôi thà cởi áo từ chức chứ danh dự cha anh không gì đổi được!"),

            ("s14", "CU", "f04bo1", ["ongdat"],
             "Trong sảnh tiệc: cận cảnh CH-1 (Ông Đạt) bên phải tức giận cười gằn mỉa mai quyết định của con rể.",
             "CH-1 hất cằm thách thức sự lựa chọn của Khoa.",
             "CH-1 (Ông Đạt, giọng gằn cay nghiệt)",
             "Đúng là thằng ngu muội! Để tao chống mắt xem cái chữ hiếu nhà quê rách nát của mày có mài ra mà ăn thay tiền được không!"),

            ("s15", "CU", "f04bo1", ["chau_vo"],
             "Trong sảnh tiệc: cận cảnh cô vợ CH-1 (Châu mặc đầm đỏ rượu) bên phải giận đỏ mặt đưa tối hậu thư ly hôn.",
             "CH-1 trừng mắt xúc phạm xuất thân của chồng lần cuối.",
             "CH-1 (Châu, giọng gay gắt tuyệt tình)",
             "Vậy thì ly hôn ngay đi! Anh khoác áo bác sĩ vào người mà cốt cách vẫn bần nông thì về quê trộn vữa với bố anh luôn đi!"),

            ("s16", "CU", "f04bo1", ["khoa_bs"],
             "Trong sảnh tiệc: cận cảnh CH-1 (Khoa) ánh mắt lạnh băng dứt khoát chấp nhận ly hôn không một giây luyến tiếc.",
             "CH-1 đáp trả thẳng thắn khiến nhà vợ chết sững.",
             "CH-1 (Khoa, giọng đanh lạnh dứt khoát)",
             "Ly hôn thì ly hôn! Dòng máu trộn vữa kiếm đồng tiền lương thiện nuôi tôi nên người, còn hạng khoác lụa khinh người tôi không tiếc!"),

            ("s17", "MED", "f04bo1", ["chau_vo", "baquy"],
             "Trong sảnh tiệc: CH-1 (Châu) và mẹ CH-2 (Bà Quý) bên phải tái mặt bẽ bàng trước ánh nhìn của cả khán phòng, cố vớt vát lời thách đố.",
             "CH-1 nghiến răng thách khán giả phân xử.",
             "CH-1 (Châu, giọng cay cú thách thức)",
             "Để xem thiên hạ có ai bênh ba bố con nhà quê các người không! Nếu tôi sai tôi xin lỗi và mời ba bố con ngồi mâm chính ngay!"),

            ("s18", "WIDE_CROWD", "f04bo1", ["ongloc", "khoa_bs", "hai_anhca"],
             "Toàn cảnh sảnh tiệc sáng rực: bác sĩ CH-2 (Khoa) đứng giữa choàng tay ôm vai cha già CH-1 (Ông Lộc) bên trái và anh cả CH-3 (Hải) bên phải đầy tự hào.",
             "Ba cha con mỉm cười ấm áp chuẩn bị rời khỏi bữa tiệc phù phiếm.",
             "CH-2 (Khoa, giọng ấm áp hiếu thảo nói với cha và anh)",
             "Đi thôi bố, đi anh Hải! Con đưa bố với anh ra quán quen ăn bữa cơm sum vầy thật ngon của ba bố con mình!"),

            ("s19", "CU", "f04bo1", ["ongloc", "hai_anhca"],
             "Trong sảnh tiệc: cận cảnh người cha già CH-1 (Ông Lộc) rơi giọt nước mắt mãn nguyện nhìn hai con trai hiếu nghĩa.",
             "CH-1 gật đầu mỉm cười ấm lòng bên cạnh con cả CH-2 (Hải).",
             "CH-1 (Ông Lộc, nghẹn ngào mỉm cười hạnh phúc)",
             "Đời bố vất vả nắng mưa bao năm, nghe câu nói này của hai anh em con là bố thấy xứng đáng hết thảy rồi!"),

            ("s20", "WIDE_CROWD", "f04bo1", ["ongloc", "khoa_bs", "hai_anhca"],
             "Toàn cảnh sảnh tiệc đông quan khách: ba cha con CH-1, CH-2, CH-3 ngẩng cao đầu khoác vai nhau sải bước hiên ngang ra cửa chính.",
             "Bước chân vững chãi đầy tự trọng của ba cha con giữa ánh đèn chùm.",
             None, ""),

            ("s21", "CU", "f04bo1", ["khoa_bs", "ongloc"],
             "Trước sảnh tiệc: bác sĩ CH-1 (Khoa) đứng cạnh cha già CH-2 (Ông Lộc), quay mặt nhìn thẳng ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera trò chuyện chân thành rồi mỉm cười khép môi.",
             "CH-1 (Khoa, nhìn thẳng ống kính hỏi khán giả)",
             "Đứng ra bảo vệ đôi bàn tay chai sần của cha và sự hy sinh của anh trước nhà thông gia cậy tiền, mọi người thấy Khoa làm đúng không ạ?"),
        ],
    },

    # =========================================================================
    # F05: Bố vợ dầm mưa mang trứng gà lên thăm, con rể giấu vợ rút tiết kiệm sửa mái nhà (20 scenes)
    # Cast (G09 NEW BRANCH — 0% overlap!): Ông Bình (62t) — Anh Đức (34t) — Con gái Ngọc (28t) — Con rể Minh (31t)
    # =========================================================================
    "f05": {
        "title": "Bố vợ dầm mưa mang trứng gà lên thăm con rể giấu vợ rút tiết kiệm sửa mái nhà",
        "acts_bgm": [
            ("s01", "acoustic_warm_morning.mp3", 2.0, 0.90),
            ("s10", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s15", "piano_warm_family.mp3", 5.0, 1.08),
        ],
        "board_items": [
            ("CH-1: Ông Bình 62t (G09_01 Mới)", "ongbinh"),
            ("CH-2: Con trai Đức 34t (G09_02 Mới)", "duc_anh"),
            ("CH-3: Con gái Ngọc 28t (G09_03 Mới)", "ngoc_vo"),
            ("CH-4: Con rể Minh 31t (G09_04 Mới)", "minh_re"),
            ("BO-1: Phòng khách sang nhà Đức", "f05bo1"),
            ("BO-2: Cửa căn hộ Minh Ngọc", "f05bo2"),
            ("BO-3: Bàn ăn ấm cúng Minh Ngọc", "f05bo3"),
        ],
        "shots": [
            ("s01", "WIDE", "f05bo1", ["ongbinh", "duc_anh"],
             "Phòng khách căn hộ sang trọng của con trai lớn: CH-1 (Ông Bình 62 tuổi mặc áo nâu xách giỏ tre) đứng bên trái trò chuyện nhẹ nhàng với con trai trưởng CH-2 (Đức 34 tuổi mặc polo sẫm) bên phải.",
             "CH-1 hiền lành nhắc chuyện mái ngói cũ ở quê bị mưa dột cần sửa sang.",
             "CH-1 (Ông Bình, giọng hiền lành dè dặt)",
             "Đức ơi, đợt mưa lớn vừa rồi mái ngói nhà quê dột nhiều quá, con xem đỡ đần bố lợp lại mái hiên nhé?"),

            ("s02", "CU", "f05bo1", ["duc_anh", "ongbinh"],
             "Trong căn hộ sang trọng: CH-1 (Đức) bên phải phẩy tay lạnh nhạt từ chối bố già CH-2 (Ông Bình) bên trái.",
             "CH-1 nhìn đồng hồ viện cớ mới đổi xe hơi để đẩy bố sang nhà em gái.",
             "CH-1 (Đức, giọng thờ ơ thoái thác)",
             "Tháng này con vừa đổi chiếc xe hơi mới hết sạch tiền mặt rồi, bố chịu khó bắt xe sang bên nhà vợ chồng cái Ngọc ấy!"),

            ("s03", "WIDE", "f05bo2", ["ongbinh", "ngoc_vo"],
             "Cửa căn hộ chung cư giản dị ấm cúng: CH-1 (Ông Bình xách giỏ tre trứng gà) đứng ngoài cửa bên trái, con gái CH-2 (Ngọc mặc sơ mi caro) bên phải mở cửa mừng rỡ nhưng xót xa thấy tay bố trầy nhẹ.",
             "CH-2 vội đỡ giỏ trứng gà và nắm bàn tay bố hỏi han đầy thương cảm.",
             "CH-2 (Ngọc, giọng xót xa thương bố)",
             "Trời mưa gió thế này bố xách trứng gà lên làm gì cho vất vả! Mà mu bàn tay bố trượt ngã ở đâu xước thế kia ạ?"),

            ("s04", "CU", "f05bo2", ["ongbinh", "ngoc_vo"],
             "Trước cửa căn hộ: cận cảnh CH-1 (Ông Bình) bên trái cười hiền hậu giấu vết xước để con gái CH-2 (Ngọc) yên lòng.",
             "CH-1 nhìn con gái trìu mến khoe giỏ trứng gà quê mới nhặt.",
             "CH-1 (Ông Bình, mỉm cười hiền từ trấn an con)",
             "Bố trượt chân ngoài ngõ nhẹ hều ấy mà! Gà quê mới đẻ trứng thơm lắm, bố mang lên bồi bổ cho vợ chồng con đây."),

            ("s05", "WIDE", "f05bo3", ["ongbinh", "ngoc_vo", "minh_re"],
             "Bàn ăn tối ấm cúng trong căn hộ nhỏ: CH-1 (Ông Bình) ngồi bên trái, con gái CH-2 (Ngọc) ngồi giữa, con rể CH-3 (Minh mặc sơ mi trắng) bên phải lễ phép gắp thức ăn vào bát mời bố vợ.",
             "CH-3 ân cần tiếp thức ăn chăm sóc bố vợ chu đáo.",
             "CH-3 (Minh, giọng lễ phép ấm áp)",
             "Đường xa mưa lạnh vất vả quá, bố ăn nhiều cơm nóng vào cho lại sức nhé, dạo này con thấy bố gầy đi đấy ạ."),

            ("s06", "CU", "f05bo3", ["ongbinh"],
             "Bên bàn ăn ấm cúng: cận cảnh CH-1 (Ông Bình) đặt đũa xuống ôn tồn tâm sự chuyện mái ngói cũ ở quê với con rể bên phải.",
             "CH-1 mỉm cười hiền hậu mở lời nhờ các con phụ sửa lại mái hiên.",
             "CH-1 (Ông Bình, giọng ngại ngùng chân chất)",
             "Minh này, mái ngói nhà quê dạo này mưa dột quá, hai đứa xem thu xếp phụ bố sửa sang lại ít hôm nhé."),

            ("s07", "CU", "f05bo3", ["minh_re"],
             "Bên bàn ăn: cận cảnh chàng rể CH-1 (Minh mặc sơ mi trắng) bên phải thoáng trầm ngâm áy náy vì áp lực công việc hiện tại.",
             "CH-1 thành thật chia sẻ tình hình khó khăn ở công ty với bố vợ.",
             "CH-1 (Minh, giọng trầm tĩnh ái ngại)",
             "Dạ thú thật công ty con đợt này đang cắt giảm nhân sự khó khăn, tiền sinh hoạt trong nhà hiện cũng chẳng dư bao nhiêu bố ạ."),

            ("s08", "CU", "f05bo3", ["ongbinh"],
             "Bên bàn ăn: cận cảnh CH-1 (Ông Bình) lập tức tươi cười xua tay để hai con không phải bận lòng áy náy.",
             "CH-1 vội đứng dậy viện cớ về quê nhốt đàn gà ngay trong chiều.",
             "CH-1 (Ông Bình, cười xòa giàu lòng tự trọng)",
             "À bố hỏi thử thế thôi, mai bố trèo lên căng tấm bạt che tạm cũng qua mùa mưa! Thôi đàn gà quê chưa nhốt, bố về luôn đây!"),

            ("s09", "MED", "f05bo3", ["ngoc_vo", "ongbinh"],
             "Cạnh bàn ăn: CH-1 (Ngọc) bên phải nắm tay áo năn nỉ giữ bố CH-2 (Ông Bình) bên trái ngủ lại qua đêm nhưng ông cụ kiên quyết từ chối.",
             "CH-2 lắc đầu hiền hậu sợ ở lại làm phiền vợ chồng con rể.",
             "CH-1 (Ngọc, giọng nghẹn ngào giữ bố)",
             "Ngoài trời tối mưa rồi bố ở lại với tụi con đêm nay đi, sáng mai tạnh mưa hẵng bắt xe về quê bố ơi!"),

            ("s10", "WIDE", "f05bo2", ["ongbinh", "ngoc_vo", "minh_re"],
             "Trước cửa căn hộ lúc tiễn bố: CH-3 (Minh) bên phải trao lại chiếc giỏ tre cho CH-1 (Ông Bình) bên trái rồi rút hai tờ tiền lẻ mỏng đưa ra làm tiền xe trước mặt CH-2 (Ngọc).",
             "CH-3 đưa ít tiền lẻ ra ngoài mặt khiến CH-2 đứng cạnh sững người tức giận.",
             "CH-3 (Minh, giọng bình thản đưa tiền xe lẻ)",
             "Bố thông cảm trong ví con chỉ còn mấy đồng lẻ này thôi, bố cầm tạm bắt xe khách về quê sớm kẻo tối muộn ạ."),

            ("s11", "CU", "f05bo2", ["ngoc_vo", "minh_re"],
             "Trước cửa căn hộ: cận cảnh CH-1 (Ngọc) trào nước mắt thất vọng tột độ quay sang trách chồng CH-2 (Minh) bên phải.",
             "CH-1 bật khóc nức nở đòi ly hôn ngay trước cửa vì tưởng chồng bạc bẽo với bố mình.",
             "CH-1 (Ngọc, bật khóc tức tưởi trách chồng)",
             "Mái nhà bố dột nát mà anh đưa vài đồng lẻ giục bố về trong mưa à? Lòng dạ anh thế này thì mình ly hôn đi!"),

            ("s12", "CU", "f05bo2", ["ngoc_vo"],
             "Trước cửa căn hộ: cận cảnh CH-1 (Ngọc) nước mắt giàn giụa nhắc lại lời hứa ngày cưới của chồng.",
             "CH-1 nghẹn giọng uất ức nhìn Minh.",
             "CH-1 (Ngọc, giọng nức nở đau lòng)",
             "Ngày rước em về anh hứa thương bố vợ như bố ruột, vậy mà giờ bố hoạn nạn anh lại đối xử lạnh lùng thế sao!"),

            ("s13", "MED", "f05bo2", ["ongbinh", "ngoc_vo", "minh_re"],
             "Trước cửa căn hộ: người cha già CH-1 (Ông Bình) vội bước vào giữa nắm tay can ngăn CH-2 (Ngọc) và vỗ vai an ủi chàng rể CH-3 (Minh).",
             "CH-1 nhận hết lỗi về mình để giữ êm ấm cho hôn nhân của con gái.",
             "CH-1 (Ông Bình, giọng trầm ấm bao dung khuyên các con)",
             "Thôi bố xin hai đứa! Tại bố già vô dụng mới làm vợ chồng con bất hòa, các con cãi nhau thế này bố đau lòng lắm!"),

            ("s14", "CU", "f05bo2", ["ongbinh", "minh_re"],
             "Trước cửa căn hộ: CH-1 (Ông Bình) bên trái nắm chặt vai con rể CH-2 (Minh) bên phải dặn dò đầy thấu hiểu trước khi bước đi.",
             "CH-1 mỉm cười hiền hậu tin tưởng nhân cách của con rể rồi xách giỏ ra về.",
             "CH-1 (Ông Bình, giọng chân tình ấm áp)",
             "Minh à, bố biết con sống rất tốt với cái Ngọc, con bé thương bố mới nóng lời, vợ chồng chín bỏ làm mười con nhé!"),

            ("s15", "WIDE", "f05bo3", ["ngoc_vo", "minh_re"],
             "Trong phòng ăn căn hộ ấm cúng sau khi tiễn bố: CH-1 (Ngọc) đứng bên trái cầm cuốn sổ nhỏ trên bàn ngạc nhiên quay sang hỏi chồng CH-2 (Minh) đứng bên phải.",
             "CH-1 nhìn chồng hỏi nhẹ nhàng với ánh mắt băn khoăn.",
             "CH-1 (Ngọc, ngạc nhiên hỏi chồng)",
             "Ủa anh Minh? Cuốn sổ tích cóp bấy lâu của hai vợ chồng mình sao hôm nay anh lại đem ra dùng việc gì thế?"),

            ("s16", "CU", "f05bo3", ["minh_re"],
             "Trong phòng ăn ấm áp: cận cảnh CH-1 (Minh) bên phải mỉm cười hiền hậu ôn tồn chia sẻ tấm lòng hiếu thảo với vợ.",
             "CH-1 điềm đạm kể chuyện đã gửi món quà biếu bố sửa lại mái nhà quê.",
             "CH-1 (Minh, giọng điềm đạm ấm áp chân thành)",
             "Anh đã gói trọn khoản tích cóp đó đặt khéo bên dưới lớp trứng quê trong giỏ để biếu bố lợp lại mái nhà rồi em ạ."),

            ("s17", "CU", "f05bo3", ["minh_re", "ngoc_vo"],
             "Trong phòng ăn: CH-1 (Minh) bên phải nắm nhẹ tay vợ CH-2 (Ngọc đang chết lặng xúc động) bên trái giải thích lý do phải đóng kịch ngoài cửa.",
             "CH-1 nhìn vợ đầy thấu hiểu tính cách người cha quê tự trọng.",
             "CH-1 (Minh, giọng sâu sắc thấu tình đạt lý)",
             "Tính bố tự trọng cao lắm, đưa thẳng đời nào bố chịu cầm! Anh phải giả vờ than kẹt tiền ngoài cửa bố mới yên tâm mang giỏ về."),

            ("s18", "MED", "f05bo3", ["ngoc_vo", "minh_re"],
             "Trong phòng ăn ấm áp: CH-1 (Ngọc) vỡ òa bật khóc nức nở ôm chầm lấy chồng CH-2 (Minh) hối hận vì đã trách lầm tấm lòng cao cả của anh.",
             "CH-2 dịu dàng vỗ lưng vợ hẹn sáng mai cùng về quê sửa nhà cho bố.",
             "CH-1 (Ngọc, khóc nghẹn hạnh phúc ôm chồng)",
             "Chồng ơi cho em xin lỗi vì đã trách oan anh! Em thật có phước mới lấy được người chồng thương bố em thấu đáo thế này!"),

            ("s19", "WIDE", "f05bo3", ["minh_re", "ngoc_vo"],
             "Toàn cảnh phòng ăn căn hộ dưới ánh đèn vàng ấm cúng: CH-1 (Minh) ôm nhẹ vai CH-2 (Ngọc mỉm cười lau nước mắt), hai vợ chồng tựa vào nhau bình yên.",
             "Khoảnh khắc hóa giải tràn đầy tình nghĩa vợ chồng.",
             None, ""),

            ("s20", "CU", "f05bo3", ["minh_re", "ngoc_vo"],
             "Trong căn hộ ấm cúng: CH-1 (Minh) đứng cạnh vợ CH-2 (Ngọc), quay mặt nhìn thẳng ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera trò chuyện chân thành rồi mỉm cười khép môi.",
             "CH-1 (Minh, nhìn thẳng ống kính hỏi khán giả)",
             "Giấu vợ đặt tiền tiết kiệm dưới đáy giỏ để giữ trọn lòng tự trọng cho bố vợ sửa nhà, mọi người thấy Minh làm vậy ổn thỏa chưa ạ?"),
        ],
    },
}
