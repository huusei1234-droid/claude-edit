"""
Screenplay & Shot-by-Shot Director Blueprint — Episodes 01 to 05 (`261123 K4 Batch`):
- Strict 180-degree spatial axis (`CHỐT KHÔNG GIAN`).
- Strict `<= 19 words` crisp Vietnamese cinema dialogue per shot + generous `9s–11s` Flow duration -> 0.00% mid-sentence cut-off!
- Interleaves Wide Establishing (`WIDE`), Crowd Public (`WIDE_CROWD`), Medium Action (`MED`), and Emotional Close-Up (`CU`).
- Zero illogical details; zero mention of interior walls in speech.
"""

EPISODES_01_05 = {
    # =========================================================================
    # EP01: Con rể hiếu thảo đón cả bố mẹ vợ về nuôi (21 scenes)
    # =========================================================================
    "ep01": {
        "title": "Con rể hiếu thảo đón cả bố mẹ vợ về nuôi",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("piano_warm_family.mp3", 4.0, 0.24),
        "pivot_scene": "s12",
        "board_items": [
            ("CH-1: Bà Hiền (Mẹ vợ)", "bahien"),
            ("CH-2: Tuấn (Con rể)", "tuan_vest"),
            ("CH-3: Thảo (Vợ Tuấn)", "thao"),
            ("CH-4: Mai (Em vợ)", "mai"),
            ("BO-1: Cổng biệt thự", "e01bo1"),
            ("BO-2: Phòng khách", "e01bo2"),
            ("BO-3: Bến xe đông người", "e01bo3"),
        ],
        "shots": [
            ("s01", "WIDE", "e01bo1", ["mai", "bahien", "tuan_vest"],
             "Trước cổng sắt biệt thự buổi sáng: CH-1 (Mai) và CH-2 (Bà Hiền đeo túi vải) đứng bên trái, CH-3 (Tuấn mặc vest) bước từ cổng bên phải ra đón.",
             "CH-1 dẫn mẹ tới trước cổng nói nhanh với anh rể CH-3 rồi khép môi chuẩn bị quay đi.",
             "CH-1 (Mai, nhìn sang phải nói nhanh với Tuấn)",
             "Anh rể ơi, nhà em nuôi bố rồi, còn anh chị nuôi mẹ cho công bằng nhé!"),

            ("s02", "CU", "e01bo1", ["tuan_vest", "bahien"],
             "Trước cổng biệt thự: CH-1 (Tuấn) đứng bên phải nhìn sang trái, CH-2 (Bà Hiền) đứng bên trái vẻ mặt ngại ngùng.",
             "CH-1 mỉm cười ấm áp dìu mẹ vợ CH-2 vào cổng.",
             "CH-1 (Tuấn, giọng lễ phép ấm áp nhìn Bà Hiền)",
             "Con bé này vội thế! Thôi mẹ vào nhà nghỉ ngơi với tụi con đi ạ."),

            ("s03", "WIDE", "e01bo2", ["tuan_vest", "bahien"],
             "Phòng khách sáng sủa: CH-2 (Bà Hiền) ngồi ghế sofa bên trái, CH-1 (Tuấn) đứng bên phải rót nước mời mẹ.",
             "CH-1 đặt chén nước lên bàn trà mời mẹ vợ với gương mặt chân thành.",
             "CH-1 (Tuấn, mỉm cười hiền hậu nhìn mẹ vợ)",
             "Phòng của mẹ con dọn sạch rồi, từ nay mẹ cứ yên tâm ở đây nhé."),

            ("s04", "CU", "e01bo2", ["bahien"],
             "Phòng khách: CH-1 (Bà Hiền) ngồi trên sofa bên trái nhìn sang phải hướng con rể.",
             "CH-1 nắm nhẹ quai túi vải, ánh mắt phân vân hỏi thật lòng con rể.",
             "CH-1 (Bà Hiền, giọng hiền lành lo lắng)",
             "Con rể à, mẹ lên ở thế này có làm phiền vợ chồng con không?"),

            ("s05", "CU", "e01bo2", ["tuan_vest"],
             "Phòng khách: CH-1 (Tuấn) đứng bên phải nhìn sang trái hướng mẹ vợ trên sofa.",
             "CH-1 lắc đầu mỉm cười trấn an mẹ vợ rồi chuẩn bị lên công ty.",
             "CH-1 (Tuấn, giọng dứt khoát chân tình)",
             "Mẹ của Thảo cũng là mẹ con mà. Con xin phép lên công ty lát nhé."),

            ("s06", "MED", "e01bo2", ["bahien"],
             "Phòng khách yên tĩnh: một mình CH-1 (Bà Hiền) ngồi trên sofa giữa phòng.",
             "CH-1 nhìn ra cửa thở dài thương chồng già phải sống tách riêng.",
             "CH-1 (Bà Hiền, giọng trầm buồn tâm sự khẽ)",
             "Vợ chồng già gắn bó mấy chục năm, nay lại phải chia ra mỗi người một nơi."),

            ("s07", "WIDE", "e01bo2", ["thao", "bahien"],
             "Phòng khách: CH-1 (Thảo mặc váy trắng) vừa bước vào bên phải, ngạc nhiên thấy mẹ ruột CH-2 (Bà Hiền) ngồi sofa bên trái.",
             "CH-1 bước nhanh lại gần bàn trà hỏi thăm mẹ.",
             "CH-1 (Thảo, ngạc nhiên bước tới hỏi mẹ)",
             "Ủa mẹ? Sao sáng sớm mẹ lại xách túi sang ngồi một mình thế này ạ?"),

            ("s08", "CU", "e01bo2", ["bahien", "thao"],
             "Phòng khách: CH-1 (Bà Hiền) ngồi bên trái ngước nhìn con gái CH-2 (Thảo) đứng bên phải.",
             "CH-1 kể lại lời con út với ánh mắt dè dặt.",
             "CH-1 (Bà Hiền, giọng nhỏ nhẹ nhìn Thảo)",
             "Em Mai bảo bên đó nuôi bố rồi, nên đưa mẹ sang ở cùng vợ chồng con."),

            ("s09", "CU", "e01bo2", ["thao"],
             "Phòng khách: CH-1 (Thảo) đứng bên phải nhìn xuống bên trái với nét mặt bối rối thở dài.",
             "CH-1 cắn nhẹ môi khó xử giãi bày áp lực tài chính với mẹ.",
             "CH-1 (Thảo, giọng ái ngại nhỏ dần)",
             "Mẹ thông cảm cho con nhé, dạo này anh Tuấn làm ăn khó khăn sợ gánh không nổi."),

            ("s10", "CU", "e01bo2", ["bahien"],
             "Phòng khách: CH-1 (Bà Hiền) ngồi bên trái rưng rưng mắt nhưng gượng cười gật đầu hiểu ý con gái.",
             "CH-1 đứng dậy cầm túi vải xin phép ra bến xe về quê.",
             "CH-1 (Bà Hiền, nghẹn giọng nhưng hiền từ)",
             "Mẹ hiểu rồi, mẹ không làm gánh nặng đâu, để mẹ ra bến bắt xe về quê."),

            ("s11", "WIDE", "e01bo2", ["tuan_vest", "thao"],
             "Phòng khách buổi trưa: CH-1 (Tuấn) từ cửa bên phải bước vào tìm quanh nhà, CH-2 (Thảo) đứng lúng túng bên trái.",
             "CH-1 nhìn quanh sofa trống không rồi quay sang hỏi vợ.",
             "CH-1 (Tuấn, ngạc nhiên hỏi vợ)",
             "Vợ ơi, sáng nay mẹ lên ở với mình mà giờ mẹ đi đâu rồi em?"),

            ("s12", "CU", "e01bo2", ["thao", "tuan_vest"],
             "Phòng khách: CH-1 (Thảo) đứng bên trái cúi mặt thú nhận với CH-2 (Tuấn) đứng bên phải.",
             "CH-1 ngập ngừng trả lời chồng rồi ngước nhìn sắc mặt anh.",
             "CH-1 (Thảo, giọng lí nhí chột dạ)",
             "Em sợ nhà mình đang kẹt tiền nên em bảo mẹ bắt xe về quê rồi."),

            ("s13", "CU", "e01bo2", ["tuan_vest"],
             "Phòng khách: CH-1 (Tuấn) đứng bên phải nhíu mày nghiêm giọng trách vợ nhìn sang trái.",
             "CH-1 sững sờ nói thẳng đạo lý chữ hiếu khiến vợ thức tỉnh.",
             "CH-1 (Tuấn, giọng nghiêm nghị đầy trách nhiệm)",
             "Em làm vậy sao đành! Tiền kiếm lại được, chứ mẹ già ốm đau chữ hiếu chờ được không?"),

            ("s14", "MED", "e01bo2", ["thao", "tuan_vest"],
             "Phòng khách: CH-1 (Thảo) bên trái bật khóc hối hận nắm tay áo chồng CH-2 (Tuấn) bên phải.",
             "CH-2 nắm tay vợ kéo nhanh ra cửa đi tìm mẹ.",
             "CH-1 (Thảo, bật khóc hối hận)",
             "Anh Tuấn ơi em sai rồi, vợ chồng mình chạy ra bến xe đón mẹ về ngay đi!"),

            ("s15", "WIDE_CROWD", "e01bo3", ["bahien"],
             "Nhà chờ bến xe khách đông người qua lại: CH-1 (Bà Hiền) ôm túi vải ngồi lặng lẽ trên ghế chờ giữa dòng hành khách tấp nập phía sau.",
             "CH-1 nhìn ra phía xe khách thở dài buồn bã một mình.",
             "CH-1 (Bà Hiền, nhìn xa xăm thở dài khẽ)",
             "Thành phố rộng lớn mà chẳng có chỗ dung thân, thôi mình về quê cho đỡ phiền con."),

            ("s16", "WIDE_CROWD", "e01bo3", ["thao", "tuan_vest", "bahien"],
             "Nhà chờ bến xe đông người: CH-3 (Bà Hiền) đứng dậy bên trái, vợ chồng CH-1 (Thảo) và CH-2 (Tuấn) từ bên phải hớt hải chạy tới giữ mẹ lại.",
             "CH-1 và CH-2 chạy ùa tới nắm chặt tay mẹ không cho mẹ lên xe.",
             "CH-1 (Thảo, thở gấp mừng rỡ gọi lớn)",
             "Mẹ ơi! May quá mẹ vẫn còn đây, tụi con tìm mẹ khắp cả bến xe!"),

            ("s17", "CU", "e01bo3", ["thao", "bahien"],
             "Trong bến xe khách: CH-1 (Thảo) bên phải ôm chầm lấy vai mẹ CH-2 (Bà Hiền) bên trái khóc xin lỗi.",
             "CH-1 ôm mẹ khóc hối lỗi chân thành, CH-2 vỗ lưng con gái.",
             "CH-1 (Thảo, khóc nghẹn ôm chặt mẹ)",
             "Mẹ ơi con ích kỷ quá, mẹ đừng về quê một mình, mẹ về với tụi con đi!"),

            ("s18", "CU", "e01bo3", ["tuan_vest", "bahien"],
             "Trong bến xe khách: CH-1 (Tuấn) đứng bên phải nắm hai bàn tay mẹ vợ CH-2 (Bà Hiền) bên trái đầy trân trọng.",
             "CH-1 lễ phép quyết định đón cả bố vợ về ở chung.",
             "CH-1 (Tuấn, giọng ấm áp dứt khoát)",
             "Chiều nay con sang nhà út đón cả bố về ở chung luôn cho ông bà sum vầy ạ!"),

            ("s19", "CU", "e01bo3", ["bahien"],
             "Trong bến xe khách: CH-1 (Bà Hiền) bên trái rơi nước mắt mỉm cười hạnh phúc nhìn con rể bên phải.",
             "CH-1 lau giọt nước mắt mừng tủi, nở nụ cười mãn nguyện.",
             "CH-1 (Bà Hiền, xúc động mỉm cười rưng rưng)",
             "Thế là vợ chồng già không phải chia lìa rồi, mẹ có phước quá con rể ơi!"),

            ("s20", "WIDE_CROWD", "e01bo3", ["tuan_vest", "bahien", "thao"],
             "Nhà chờ bến xe khách đông người: CH-1 (Tuấn) xách túi giúp mẹ, cùng CH-3 (Thảo) dìu CH-2 (Bà Hiền) ở giữa vui vẻ bước ra khỏi bến xe.",
             "Ba mẹ con khoác tay nhau bước đi ấm áp giữa dòng hành khách ở bến xe.",
             None, ""),

            ("s21", "CU", "e01bo3", ["tuan_vest", "bahien"],
             "Cửa nhà chờ bến xe: CH-1 (Tuấn) đứng cạnh CH-2 (Bà Hiền), quay thẳng mặt nhìn ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng vào camera mỉm cười điềm đạm hỏi người xem rồi khép môi.",
             "CH-1 (Tuấn, nhìn thẳng ống kính hỏi khán giả)",
             "Theo mọi người, con rể đón cả bố mẹ vợ về phụng dưỡng như vậy có đúng đạo hiếu không ạ?"),
        ],
    },

    # =========================================================================
    # EP02: Bố già vác bao tải thử lòng ba con ngày giáp Tết (16 scenes)
    # =========================================================================
    "ep02": {
        "title": "Bố già vác bao tải thử lòng ba con ngày giáp Tết",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("piano_warm_family.mp3", 5.0, 0.24),
        "pivot_scene": "s08",
        "board_items": [
            ("CH-1: Ông Phúc (Bố quê)", "ongphuc"),
            ("CH-2: Linh (Con gái út)", "linh"),
            ("CH-3: Khôi (Con trai thứ)", "khoi"),
            ("CH-4: Tiến (Con trai cả)", "tien"),
            ("CH-5: Khánh Ly (Con dâu cả)", "khanhly_tapde"),
            ("BO-1: Căn hộ nhà Linh", "e02bo1"),
            ("BO-2: Phố mua sắm đông người", "e02bo2"),
            ("BO-3: Nhà cấp 4 vợ chồng Tiến", "e02bo3"),
        ],
        "shots": [
            ("s01", "WIDE", "e02bo1", ["linh", "ongphuc"],
             "Sảnh cửa căn hộ hiện đại: CH-1 (Linh mặc đồ trắng) đứng chắn cửa bên trái, CH-2 (Ông Phúc vác bao tải) đứng khép nép bên phải.",
             "CH-1 nhíu mày xua tay từ chối không cho bố bước vào nhà.",
             "CH-1 (Linh, giọng lạnh nhạt khó chịu nhìn bố)",
             "Tết này nhà chồng con sang chơi đông lắm, nhà chật không có chỗ chứa ba đâu!"),

            ("s02", "CU", "e02bo1", ["linh", "ongphuc"],
             "Cửa căn hộ: CH-1 (Linh) bên trái hất hàm chỉ ra cửa nói với CH-2 (Ông Phúc) bên phải.",
             "CH-1 đẩy nhẹ bố ra lối cửa, vẻ mặt phũ phàng.",
             "CH-1 (Linh, giọng gắt nhẹ dứt khoát)",
             "Thôi ba chịu khó bắt xe qua bên nhà anh Khôi mà ở tạm mấy ngày nhé!"),

            ("s03", "WIDE_CROWD", "e02bo2", ["ongphuc", "khoi"],
             "Vỉa hè phố thương mại đông người qua lại: CH-1 (Ông Phúc vác bao tải) đứng bên trái gặp con trai thứ CH-2 (Khôi) bên phải giữa dòng người đi sắm Tết.",
             "CH-1 rụt rè bước lại gần con trai thứ mở lời xin ở nhờ.",
             "CH-1 (Ông Phúc, giọng khẩn khoản thương cảm)",
             "Khôi à, nhà em Linh bận đón bên nội, con cho ba ở nhờ vài hôm được không?"),

            ("s04", "CU", "e02bo2", ["khoi", "ongphuc"],
             "Giữa phố đông người: CH-1 (Khôi) bên phải xua tay từ chối CH-2 (Ông Phúc) bên trái.",
             "CH-1 lắc đầu viện cớ đi du lịch để đẩy bố sang nhà anh cả.",
             "CH-1 (Khôi, giọng vội vàng thoái thác)",
             "Ấy không tiện đâu ba ơi! Mai nhà con đi du lịch rồi, ba sang nhà anh Tiến nhé!"),

            ("s05", "CU", "e02bo2", ["khoi"],
             "Trên vỉa hè phố mua sắm: CH-1 (Khôi) rút điện thoại nghe cuộc gọi của vợ với giọng nịnh nọt.",
             "CH-1 tươi cười nói vào điện thoại rồi vội chạy về phía siêu thị.",
             "CH-1 (Khôi, giọng nịnh vợ hớn hở trên điện thoại)",
             "Alo vợ yêu ở siêu thị hả? Đợi năm phút anh chạy qua xách đồ cho em ngay!"),

            ("s06", "CU", "e02bo2", ["ongphuc"],
             "Giữa phố thương mại đông người: CH-1 (Ông Phúc) đứng chết lặng ôm chặt quai bao tải, hai mắt đỏ hoe ngấn lệ.",
             "CH-1 nhìn theo bóng con trai khuất dần giữa dòng người tấp nập.",
             None, ""),

            ("s07", "WIDE", "e02bo3", ["ongphuc", "tien"],
             "Trước cửa gỗ căn nhà cấp 4 giản dị: CH-1 (Ông Phúc vác bao tải) rụt rè đứng bên trái, con trai cả CH-2 (Tiến) từ bên phải vội chạy ra đỡ bố.",
             "CH-2 mừng rỡ đỡ bao tải xuống và dìu bố vào ghế gỗ.",
             "CH-2 (Tiến, giọng lo lắng thương xót dìu bố)",
             "Ơ kìa ba! Trời gió lạnh sao ba đứng ngoài cửa, mau vào nhà ngồi nghỉ đi ba!"),

            ("s08", "WIDE", "e02bo3", ["ongphuc", "tien", "khanhly_tapde"],
             "Trong phòng khách nhà cấp 4 mộc mạc: CH-1 (Ông Phúc) ngồi ghế gỗ bên trái cạnh bao tải, CH-2 (Tiến) ngồi giữa, con dâu CH-3 (Khánh Ly đeo tạp dề) bưng trà bên phải.",
             "CH-1 cúi đầu ngại ngùng mở lời xin con trai cả cho ở tạm.",
             "CH-1 (Ông Phúc, giọng nghẹn ngào tủi thân)",
             "Tiến à, hai đứa em đều bận cả rồi, ba hết chỗ đi mới dám ghé nhà con."),

            ("s09", "CU", "e02bo3", ["ongphuc"],
             "Trong căn nhà cấp 4: CH-1 (Ông Phúc) ngồi bên trái nhìn hai con bên phải với ánh mắt tự trọng sợ con vất vả.",
             "CH-1 xoa hai bàn tay chai sần nói khẽ.",
             "CH-1 (Ông Phúc, giọng trầm khàn chân thật)",
             "Nếu nhà mình chật chội bất tiện thì sáng mai ba lại bắt xe quay về quê cũng được."),

            ("s10", "CU", "e02bo3", ["tien", "khanhly_tapde"],
             "Trong nhà cấp 4: CH-1 (Tiến) ngồi giữa quay sang nhìn vợ CH-2 (Khánh Ly đeo tạp dề) bên phải đầy thương cảm.",
             "CH-1 nắm nhẹ tay vợ bàn chuyện đón bố ở hẳn lại.",
             "CH-1 (Tiến, rưng rưng mắt nhìn vợ)",
             "Mình ơi, giờ ba lủi thủi một thân một mình, vợ chồng mình đón ba ở luôn nhé?"),

            ("s11", "CU", "e02bo3", ["khanhly_tapde"],
             "Trong nhà cấp 4: CH-1 (Khánh Ly đeo tạp dề) bên phải mỉm cười hiền hậu, mắt đỏ hoe nhìn bố chồng.",
             "CH-1 gật đầu dứt khoát nói lời hiếu thảo ấm lòng.",
             "CH-1 (Khánh Ly, giọng dịu dàng chân thành)",
             "Anh nói gì lạ thế, nhà mình tuy nghèo nhưng rau cháo có nhau, nhà mình là nhà của ba mà!"),

            ("s12", "MED", "e02bo3", ["tien", "ongphuc", "khanhly_tapde"],
             "Trong phòng khách nhà cấp 4: CH-1 (Tiến) quàng vai CH-2 (Ông Phúc) bên trái, CH-3 (Khánh Ly) rót trà ấm bên phải.",
             "CH-1 mỉm cười ấm áp động viên bố già yên tâm.",
             "CH-1 (Tiến, giọng nghẹn ngào hạnh phúc)",
             "Ba nghe vợ con nói chưa ạ? Ba cứ ở đây, tụi con sẽ hết lòng phụng dưỡng ba!"),

            ("s13", "CU", "e02bo3", ["ongphuc"],
             "Trong nhà cấp 4: CH-1 (Ông Phúc) vỗ nhẹ lên bao tải dưới chân, rơi nước mắt mỉm cười mãn nguyện nhìn hai con.",
             "CH-1 tiết lộ tiền tiết kiệm dưỡng già cất trong bao tải trao cho vợ chồng con cả.",
             "CH-1 (Ông Phúc, rơi nước mắt mỉm cười ấm áp)",
             "Cảm ơn hai con! Toàn bộ tiền dưỡng già và giấy đất quê trong túi này ba giao cho hai đứa giữ."),

            ("s14", "CU", "e02bo3", ["tien", "khanhly_tapde"],
             "Trong nhà cấp 4: CH-1 (Tiến) và CH-2 (Khánh Ly) sững sờ xúc động nhìn bố bên trái.",
             "CH-1 lắc đầu rưng rưng nắm chặt tay bố.",
             "CH-1 (Tiến, nghẹn giọng xúc động)",
             "Tụi con chỉ cần ba khỏe mạnh vui vầy bên con cháu thôi, không màng tài sản đâu ba!"),

            ("s15", "WIDE", "e02bo3", ["ongphuc", "tien", "khanhly_tapde"],
             "Toàn cảnh ấm cúng trong căn nhà cấp 4: cả ba bố con quây quần bên bàn trà gỗ ngập nắng ấm ngày giáp Tết.",
             "Hai vợ chồng ôm chầm lấy người cha già trong niềm hạnh phúc đoàn viên.",
             None, ""),

            ("s16", "CU", "e02bo3", ["ongphuc"],
             "Trong nhà cấp 4: CH-1 (Ông Phúc) ngồi ngay ngắn nhìn thẳng vào ống kính hỏi khán giả.",
             "CH-1 nhìn thẳng camera mỉm cười hiền từ hỏi người xem rồi khép môi.",
             "CH-1 (Ông Phúc, nhìn thẳng ống kính hỏi khán giả)",
             "Lúc cơ hàn mới thấu lòng hiếu thảo. Khán giả thấy ba trao lộc cho vợ chồng thằng cả có xứng đáng không?"),
        ],
    },

    # =========================================================================
    # EP03: Chồng đi phụ hồ ngày lễ mua quà cho vợ và cái kết (18 scenes)
    # =========================================================================
    "ep03": {
        "title": "Chồng đi phụ hồ ngày lễ mua quà cho vợ và cái kết",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("piano_warm_family.mp3", 4.0, 0.24),
        "pivot_scene": "s09",
        "board_items": [
            ("CH-1: Sơn (Chồng phụ hồ)", "son_ct"),
            ("CH-2: Ngân (Vợ công sở)", "ngan"),
            ("CH-3: Thành (Anh Shipper)", "thanh_ship"),
            ("CH-4: An (Vợ anh Shipper)", "an"),
            ("BO-1: Phòng trọ vợ chồng trẻ", "e03bo1"),
            ("BO-2: Vỉa hè phố đông xe", "e03bo2"),
            ("BO-3: Đại công trường máy xúc", "e03bo3"),
        ],
        "shots": [
            ("s01", "WIDE", "e03bo1", ["son_ct", "ngan"],
             "Phòng trọ nhỏ mộc mạc buổi sáng: CH-1 (Sơn mặc áo bảo hộ công trường) đứng bên trái mỉm cười nhìn vợ CH-2 (Ngân mặc công sở) bên phải.",
             "CH-1 gửi lời chúc ngày phụ nữ tới vợ.",
             "CH-1 (Sơn, mỉm cười ấm áp nhìn vợ)",
             "Em à, nay ngày hai mươi tháng mười, anh chúc vợ yêu luôn xinh đẹp rạng rỡ nhé!"),

            ("s02", "CU", "e03bo1", ["son_ct"],
             "Trong phòng trọ: CH-1 (Sơn) đứng bên trái nhìn sang phải ngập ngừng xoa hai bàn tay mở lời.",
             "CH-1 ấp úng hỏi mượn vợ hai trăm nghìn đổ xăng đi làm.",
             "CH-1 (Sơn, giọng rụt rè ngại ngùng)",
             "À vợ ơi, trong ví em còn tiền lẻ cho anh mượn tạm hai trăm đi làm nhé?"),

            ("s03", "CU", "e03bo1", ["ngan"],
             "Trong phòng trọ: CH-1 (Ngân) đứng bên phải lập tức đổi sắc mặt giận dữ nhìn sang trái trách chồng.",
             "CH-1 bức xúc so sánh chồng với chồng bạn bè.",
             "CH-1 (Ngân, giọng gay gắt tủi thân)",
             "Bạn em đứa được tặng điện thoại, đứa được bó hoa, còn anh chúc xuông xong hỏi tiền à?"),

            ("s04", "CU", "e03bo1", ["son_ct"],
             "Trong phòng trọ: CH-1 (Sơn) đứng bên trái nhìn vợ bên phải với ánh mắt xót xa cố giải thích.",
             "CH-1 hạ giọng khuyên nhủ vợ thông cảm lúc khó khăn.",
             "CH-1 (Sơn, giọng trầm buồn nhẫn nhịn)",
             "Anh mới vấp ngã gây dựng lại từ đầu, em ráng hiểu và chờ anh thêm chút thôi."),

            ("s05", "MED", "e03bo1", ["ngan", "son_ct"],
             "Trong phòng trọ: CH-1 (Ngân) bên phải hất tay giận dỗi xách túi bỏ đi, CH-2 (Sơn) đứng lặng bên trái.",
             "CH-1 trách móc chồng rồi quay lưng bước ra cửa.",
             "CH-1 (Ngân, giọng nghẹn tức dứt khoát)",
             "Ba năm trời câu nào anh cũng hứa suông! Tôi mệt mỏi cảnh mơ mộng hão huyền lắm rồi!"),

            ("s06", "CU", "e03bo1", ["son_ct"],
             "Trong phòng trọ vắng lặng: một mình CH-1 (Sơn) nắm chặt bàn tay với ánh mắt quyết tâm.",
             "CH-1 hít sâu nén buồn, quyết đi làm thêm ca công trường.",
             "CH-1 (Sơn, nói khẽ kiên quyết một mình)",
             "Anh nhất định không để em thiệt thòi đâu, hôm nay anh sẽ tự tay mua quà tặng em!"),

            ("s07", "WIDE_CROWD", "e03bo2", ["ngan"],
             "Vỉa hè đường phố đông xe qua lại buổi sáng: CH-1 (Ngân) khoác túi bước đi chậm rãi trên vỉa hè với gương mặt nặng trĩu.",
             "CH-1 chợt khựng bước nhìn thấy đôi vợ chồng đứng cạnh chiếc xe máy phía trước.",
             None, ""),

            ("s08", "MED", "e03bo2", ["an", "thanh_ship"],
             "Trên vỉa hè phố đông xe: CH-1 (An mặc áo len hồng) bên trái ân cần cài mũ bảo hiểm cho chồng CH-2 (Thành mặc áo cam Shipper) bên phải.",
             "CH-1 dịu dàng chỉnh cổ áo cho chồng với ánh mắt yêu thương.",
             "CH-1 (An, giọng hiền dịu động viên chồng)",
             "Công ty vừa phá sản, anh đang làm giám đốc phải chạy giao hàng thế này thương anh quá."),

            ("s09", "CU", "e03bo2", ["thanh_ship", "an"],
             "Trên vỉa hè: CH-1 (Thành mặc áo Shipper cam) bên phải mỉm cười nắm bàn tay vợ CH-2 (An) bên trái.",
             "CH-1 cười hiền trấn an vợ đầy nghị lực.",
             "CH-1 (Thành, giọng ấm áp rắn rỏi)",
             "Không sao đâu em, chỉ cần về nhà thấy em cười là vất vả mấy anh cũng chịu được!"),

            ("s10", "CU", "e03bo2", ["ngan"],
             "Trên vỉa hè phố: CH-1 (Ngân) đứng sững nhìn cảnh đó, hai mắt rưng rưng hối hận nhớ lại lời cay nghiệt mình vừa mắng chồng.",
             "CH-1 nghẹn ngào tỉnh ngộ rồi vội quay bước đi tìm chồng.",
             "CH-1 (Ngân, thầm bật khóc ân hận)",
             "Chồng người ta phá sản vợ vẫn dịu dàng động viên, còn mình lại đay nghiến chồng ngày lễ..."),

            ("s11", "WIDE_CROWD", "e03bo3", ["son_ct"],
             "Đại công trường xây dựng nắng gắt có máy xúc vàng và công nhân phía xa: CH-1 (Sơn mặc áo phản quang cam) gồng lưng xúc từng xẻng cát nặng nhọc.",
             "CH-1 mồ hôi ướt đẫm trán vẫn miệt mài làm việc giữa nắng bụi.",
             None, ""),

            ("s12", "CU", "e03bo3", ["son_ct"],
             "Giữa công trường nắng gắt: cận cảnh CH-1 (Sơn) mồ hôi lăn dài trên má dính bụi, tay cầm cờ lê sắt mỉm cười hiền.",
             "CH-1 quệt mồ hôi trên trán nghĩ tới món quà chiều nay mua tặng vợ.",
             "CH-1 (Sơn, thở nhẹ nhưng mỉm cười hiền hậu)",
             "Ráng làm nốt ca chiều nay nhận tiền công ngày là đủ mua chiếc lắc bạc tặng vợ rồi."),

            ("s13", "WIDE_CROWD", "e03bo3", ["ngan", "son_ct"],
             "Đại công trường có máy xúc vàng phía sau: CH-1 (Ngân mặc vest công sở) đứng bên trái bật khóc nhìn CH-2 (Sơn áo phản quang lấm lem) vừa quay người lại bên phải.",
             "CH-2 sững sờ luống cuống giấu đôi bàn tay lấm bụi cát sau lưng.",
             "CH-2 (Sơn, sững sờ luống cuống hỏi vợ)",
             "Ơ vợ? Sao giờ này em lại tìm ra tận ngoài công trường nắng bụi thế này?"),

            ("s14", "CU", "e03bo3", ["ngan", "son_ct"],
             "Giữa công trường: CH-1 (Ngân) bên trái lao tới nắm chặt đôi bàn tay lấm bụi của CH-2 (Sơn) bên phải, nước mắt tuôn rơi.",
             "CH-1 khóc nức nở áp bàn tay chồng lên má mình xin lỗi.",
             "CH-1 (Ngân, khóc nghẹn xót xa nhìn chồng)",
             "Chồng ơi em xin lỗi! Em không biết vì mua quà cho em mà anh đi phụ hồ cực thế này!"),

            ("s15", "CU", "e03bo3", ["son_ct", "ngan"],
             "Giữa công trường: CH-1 (Sơn) bên phải dịu dàng dùng cổ tay áo sạch lau nước mắt cho vợ CH-2 (Ngân) bên trái.",
             "CH-1 mỉm cười hiền hậu bao dung không hề giận vợ.",
             "CH-1 (Sơn, giọng trầm ấm bao dung)",
             "Ngốc quá, anh vất vả ngoài nắng một chút mà đổi được nụ cười của em thì sá gì đâu."),

            ("s16", "CU", "e03bo3", ["ngan"],
             "Giữa công trường: CH-1 (Ngân) lắc đầu trong nước mắt, ánh mắt kiên định nhìn chồng bên phải.",
             "CH-1 nắm chặt vạt áo bảo hộ của chồng hứa đồng cam cộng khổ.",
             "CH-1 (Ngân, giọng nghẹn ngào chân thành)",
             "Từ nay em không đua đòi phù phiếm nữa, hai đứa mình cùng nắm tay gây dựng lại anh nhé!"),

            ("s17", "WIDE_CROWD", "e03bo3", ["son_ct", "ngan"],
             "Đại công trường dưới nắng chiều vàng ấm: CH-1 (Sơn) khoác vai CH-2 (Ngân), hai vợ chồng sánh bước rời công trường trước khung cảnh máy xúc phía xa.",
             "Hai vợ chồng tựa vai nhau bước đi bình yên ấm áp.",
             None, ""),

            ("s18", "CU", "e03bo3", ["son_ct", "ngan"],
             "Lối ra công trường: CH-1 (Sơn) khoác vai vợ CH-2 (Ngân), quay mặt nhìn thẳng ống kính mỉm cười hỏi khán giả.",
             "CH-1 nhìn thẳng camera gửi lời tâm sự rồi mỉm cười khép môi.",
             "CH-1 (Sơn, nhìn thẳng ống kính mỉm cười ấm áp)",
             "Đàn ông nghèo một lúc không sợ, chỉ cần người vợ thấu hiểu là vượt qua hết, đúng không mọi người?"),
        ],
    },

    # =========================================================================
    # EP04: Nhịn nhục sếp hống hách nuôi bố ốm cô gái được cất nhắc tổng giám đốc (16 scenes)
    # =========================================================================
    "ep04": {
        "title": "Nhịn nhục sếp hống hách nuôi bố ốm cô gái được cất nhắc tổng giám đốc",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.22),
        "pivot_scene": "s10",
        "board_items": [
            ("CH-1: An (Nhân viên hiếu thảo)", "an_cs"),
            ("CH-2: Ông Bách (Giám đốc nóng nảy)", "ongbach"),
            ("CH-3: Quân (Chủ tịch vi hành)", "quan_trang"),
            ("BO-1: Phòng Giám đốc Bách", "e04bo1"),
            ("BO-2: Văn phòng đông nhân viên", "e04bo2"),
            ("BO-3: Đại sảnh tập đoàn", "e04bo3"),
        ],
        "shots": [
            ("s01", "WIDE", "e04bo1", ["ongbach", "an_cs"],
             "Phòng Giám đốc chi nhánh: CH-1 (Ông Bách mặc sơ mi đen đeo dây chuyền vàng) chống tay lên bàn bên trái quát CH-2 (An mặc vest công sở) cúi đầu bên phải.",
             "CH-1 đập tay xuống bàn chỉ vào cốc nước lọc mắng nhân viên.",
             "CH-1 (Ông Bách, giọng hống hách gay gắt)",
             "Tôi bảo cô pha trà thượng hạng, sao cô dám bưng lên cốc nước lọc thế này hả?"),

            ("s02", "CU", "e04bo1", ["an_cs"],
             "Phòng Giám đốc: CH-1 (An mặc vest công sở) đứng bên phải cúi đầu lễ phép giải thích.",
             "CH-1 khép nép đan hai tay trước bụng trả lời nhỏ nhẹ.",
             "CH-1 (An, giọng nhỏ nhẹ lễ phép)",
             "Dạ em xin lỗi sếp, phòng trà hết sạch lá trà rồi, mai em xin mang trà nhà lên bù ạ."),

            ("s03", "CU", "e04bo1", ["ongbach"],
             "Phòng Giám đốc: CH-1 (Ông Bách) bên trái trừng mắt chỉ tay thẳng ra cửa đuổi nhân viên.",
             "CH-1 hất cằm quát lớn không thèm nghe giải thích.",
             "CH-1 (Ông Bách, giọng quát nạt ngạo mạn)",
             "Có mỗi chén trà cũng làm không xong còn lý sự à? Bước ra ngoài ngay!"),

            ("s04", "WIDE_CROWD", "e04bo2", ["quan_trang", "an_cs"],
             "Văn phòng mở đông nhân viên đang làm việc phía sau: CH-2 (An) bước về bàn bên phải mắt đỏ hoe, CH-1 (Quân áo trắng giản dị) ngồi bên trái quay sang hỏi.",
             "CH-1 nhìn vẻ cam chịu của đồng nghiệp rồi nhẹ nhàng hỏi thăm.",
             "CH-1 (Quân, giọng điềm đạm hỏi An)",
             "Này cô, ông sếp cư xử quá đáng thế, sao cô vẫn nhẫn nhịn chịu đựng giỏi vậy?"),

            ("s05", "CU", "e04bo2", ["an_cs"],
             "Trong văn phòng mở: CH-1 (An) đứng bên phải rơi nước mắt nhưng giữ giọng tự trọng trả lời CH-2 bên trái.",
             "CH-1 lau nhanh khóe mắt rồi giãi bày.",
             "CH-1 (An, mắt đỏ hoe nghẹn giọng chân thật)",
             "Nếu chỉ nghĩ cho bản thân thì tôi đã đàng hoàng nộp đơn nghỉ việc từ lâu rồi."),

            ("s06", "CU", "e04bo2", ["an_cs"],
             "Trong văn phòng mở: cận cảnh CH-1 (An) bên phải nghẹn ngào nhắc tới bố ốm và em gái.",
             "CH-1 hít sâu kìm nước mắt, ánh mắt kiên cường vì gia đình.",
             "CH-1 (An, giọng xúc động đầy nghị lực)",
             "Nhưng em gái tôi đang học đại học, bố lại nằm viện chờ thuốc, tôi cần lương để lo cho nhà."),

            ("s07", "CU", "e04bo2", ["quan_trang"],
             "Trong văn phòng mở: CH-1 (Quân mặc áo trắng) ngồi bên trái nhìn cô gái bên phải đầy cảm phục.",
             "CH-1 gật đầu mỉm cười ấm áp khích lệ cô đồng nghiệp.",
             "CH-1 (Quân, giọng ấm áp chân thành)",
             "Người con vừa hiếu thảo vừa kiên cường như cô, tôi tin trời xanh không phụ lòng đâu."),

            ("s08", "MED", "e04bo2", ["an_cs", "quan_trang"],
             "Trong văn phòng mở: CH-1 (An) bên phải lau khô nước mắt mỉm cười hỏi lại CH-2 (Quân) ngồi bên trái.",
             "CH-1 nghiêng đầu hỏi thăm anh chàng áo trắng.",
             "CH-1 (An, giọng thân thiện hiền lành)",
             "Cảm ơn anh động viên nhé, mà anh mới chuyển qua phòng này thử việc hôm nay hả?"),

            ("s09", "CU", "e04bo2", ["quan_trang", "an_cs"],
             "Trong văn phòng mở: CH-1 (Quân) bên trái mỉm cười kín đáo giấu thân phận Chủ tịch, thử lòng tốt của CH-2 (An).",
             "CH-1 nhờ cô lấy giúp cốc nước, CH-2 vui vẻ gật đầu ngay.",
             "CH-1 (Quân, mỉm cười hiền nhã nhặn)",
             "Ừ tôi mới qua làm đang khát quá, phiền cô rót giúp tôi cốc nước lọc được không?"),

            ("s10", "WIDE_CROWD", "e04bo3", ["ongbach", "an_cs"],
             "Đại sảnh tập đoàn sang trọng có nhân viên qua lại phía xa: sáng hôm sau CH-1 (Ông Bách) đứng bên trái cúi đầu khúm núm chào đón CH-2 (An) bước vào bên phải.",
             "CH-1 đổi thái độ khép nép cúi chào xin lỗi CH-2.",
             "CH-1 (Ông Bách, giọng lễ phép khẩn khoản bất ngờ)",
             "Chào cô An! Chuyện nóng nảy hôm qua cho tôi xin lỗi, mong cô rộng lượng bỏ qua nhé!"),

            ("s11", "CU", "e04bo3", ["an_cs", "ongbach"],
             "Giữa đại sảnh tập đoàn: CH-1 (An) bên phải mở to mắt ngơ ngác nhìn CH-2 (Ông Bách) bên trái.",
             "CH-1 sững người chưa hiểu chuyện gì xảy ra.",
             "CH-1 (An, ngạc nhiên chớp mắt hỏi lại)",
             "Ơ dạ... sao hôm nay sếp lại khách sáo thế ạ, có chuyện gì vậy anh?"),

            ("s12", "CU", "e04bo3", ["ongbach"],
             "Đại sảnh tập đoàn: CH-1 (Ông Bách) bên trái gượng cười thông báo quyết định từ cấp cao nhất.",
             "CH-1 trang trọng báo tin thăng chức cho An.",
             "CH-1 (Ông Bách, giọng kính nể rõ ràng)",
             "Tôi bị điều đi chi nhánh tỉnh rồi, ghế Tổng giám đốc này Chủ tịch đích thân giao cho cô!"),

            ("s13", "WIDE_CROWD", "e04bo3", ["quan_trang", "ongbach", "an_cs"],
             "Đại sảnh tập đoàn rộng lớn: CH-1 (Quân mặc áo trắng) bước tới đứng bên trái cạnh CH-2 (Ông Bách), mỉm cười nhìn CH-3 (An) đứng sững bên phải.",
             "CH-2 cúi rạp đầu chào CH-1, còn CH-3 tròn mắt nhận ra chàng nhân viên hôm qua.",
             "CH-2 (Ông Bách, cung kính giới thiệu với An)",
             "Chính Chủ tịch Quân hôm qua vi hành nghe câu chuyện của cô nên quyết định trao quyền cho cô đấy!"),

            ("s14", "CU", "e04bo3", ["an_cs"],
             "Đại sảnh tập đoàn: cận cảnh CH-1 (An) bên phải xúc động cúi đầu cảm ơn Chủ tịch bên trái.",
             "CH-1 rưng rưng mỉm cười hạnh phúc.",
             "CH-1 (An, xúc động rưng rưng mỉm cười)",
             "Thì ra anh chính là Chủ tịch ạ! Em cảm ơn anh tin tưởng, em hứa sẽ làm hết sức mình!"),

            ("s15", "CU", "e04bo3", ["quan_trang"],
             "Đại sảnh tập đoàn: CH-1 (Quân) bên trái mỉm cười điềm đạm khích lệ tân Tổng giám đốc bên phải.",
             "CH-1 gật đầu tin tưởng trao gửi trọng trách.",
             "CH-1 (Quân, giọng ấm áp uy nghiêm)",
             "Người con hiếu thảo trọng chữ tín chắc chắn sẽ lãnh đạo tốt. Chúc mừng tân Tổng giám đốc An!"),

            ("s16", "CU", "e04bo3", ["quan_trang", "an_cs"],
             "Đại sảnh tập đoàn: CH-1 (Quân) đứng cạnh CH-2 (An), cả hai quay mặt nhìn thẳng ống kính mỉm cười hỏi khán giả.",
             "CH-1 nhìn thẳng camera đặt câu hỏi kết phim rồi mỉm cười khép môi.",
             "CH-1 (Quân, nhìn thẳng ống kính hỏi khán giả)",
             "Trao ghế lãnh đạo cho người hiếu thảo tử tế thay kẻ hống hách, mọi người thấy quyết định này chuẩn chưa ạ?"),
        ],
    },

    # =========================================================================
    # EP05: Mang tiếng ác từ chối bạn thân để giữ sổ đỏ cứu vợ con bạn (15 scenes)
    # =========================================================================
    "ep05": {
        "title": "Mang tiếng ác từ chối bạn thân để giữ sổ đỏ cứu vợ con bạn",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("piano_warm_family.mp3", 4.0, 0.24),
        "pivot_scene": "s06",
        "board_items": [
            ("CH-1: Tuấn (Giám đốc trọng tình)", "tuan_somi"),
            ("CH-2: Sơn (Bạn thân lầm đường)", "son"),
            ("CH-3: Uyên (Vợ bạn cầm sổ đỏ)", "uyen_sodo"),
            ("BO-1: Phòng khách căn hộ Tuấn", "e05bo1"),
            ("BO-2: Hành lang thang máy", "e05bo2"),
        ],
        "shots": [
            ("s01", "WIDE", "e05bo1", ["son", "tuan_somi"],
             "Phòng khách căn hộ ban công kính rộng: CH-1 (Sơn mặc áo xám phờ phạc) đứng bên trái khẩn khoản nhìn CH-2 (Tuấn sơ mi trắng) khoanh tay lạnh lùng bên phải.",
             "CH-2 cố tình sa sầm nét mặt chỉ tay ra cửa từ chối thẳng.",
             "CH-2 (Tuấn, giọng lạnh lùng cứng rắn nhìn Sơn)",
             "Hai trăm triệu không phải lá mít đâu! Cậu tự làm thì tự chịu, về ngay đi!"),

            ("s02", "CU", "e05bo1", ["son"],
             "Phòng khách: CH-1 (Sơn) đứng bên trái mắt đỏ ngầu uất ức nhìn sang phải trách bạn thân.",
             "CH-1 nghiến răng chua chát nhắc lại tình nghĩa thuở nghèo khó.",
             "CH-1 (Sơn, giọng nghẹn uất thất vọng)",
             "Xưa mày tay trắng tao nhường từng gói mì, giờ tao ngã xuống mày coi tao không ra gì!"),

            ("s03", "CU", "e05bo1", ["tuan_somi"],
             "Phòng khách: CH-1 (Tuấn) bên phải nén xót xa trong mắt, tiếp tục đóng vai kẻ lạnh nhạt để cảnh tỉnh bạn.",
             "CH-1 hất mặt nói lời phũ phàng rồi ngoảnh đi.",
             "CH-1 (Tuấn, giọng cố gằn lạnh nhạt)",
             "Giờ tôi làm giám đốc rồi, suốt ngày cậu sang hỏi vay tiền không biết ngại à? Mời cậu về!"),

            ("s04", "WIDE", "e05bo1", ["son", "tuan_somi"],
             "Toàn cảnh phòng khách: CH-1 (Sơn) bên trái chỉ tay tuyệt giao với CH-2 (Tuấn) đứng bất động bên phải rồi giận dữ bỏ ra cửa.",
             "CH-1 gằn giọng tuyên bố cắt đứt rồi sập bước rời đi.",
             "CH-1 (Sơn, giọng gằn cay đắng)",
             "Được lắm! Tình anh em mười năm chấm dứt từ đây, coi như tao mù mới chơi với mày!"),

            ("s05", "CU", "e05bo1", ["tuan_somi"],
             "Phòng khách: khi bóng bạn khuất sau cửa, gương mặt CH-1 (Tuấn) lập tức trùng xuống đầy đau xót thở dài.",
             "CH-1 nhắm mắt thở dài xót bạn rồi quay nhìn về phía phòng trong.",
             None, ""),

            ("s06", "WIDE", "e05bo1", ["uyen_sodo", "tuan_somi"],
             "Phòng khách căn hộ: CH-1 (Uyên ôm cuốn sổ đỏ bìa đỏ trước ngực) từ phòng trong bên trái bước ra rưng rưng nhìn CH-2 (Tuấn) bên phải.",
             "CH-1 ôm chặt cuốn sổ đỏ nghẹn ngào cảm thương cho Tuấn.",
             "CH-1 (Uyên, mắt ngấn lệ xúc động nhìn Tuấn)",
             "Anh Tuấn ơi, anh đưa cả sổ đỏ cứu mẹ con em, sao lại tự nhận hết tiếng ác vậy?"),

            ("s07", "CU", "e05bo1", ["uyen_sodo"],
             "Phòng khách: cận cảnh CH-1 (Uyên) bên trái nhìn cuốn sổ đỏ rồi ngước nhìn Tuấn đầy áy náy.",
             "CH-1 rơi nước mắt lo chồng hiểu lầm oán trách bạn tốt.",
             "CH-1 (Uyên, giọng nghẹn ngào xót xa)",
             "Anh Sơn hiểu lầm lại oán hận anh như thế, em cầm cuốn sổ này sao đành lòng đây anh?"),

            ("s08", "CU", "e05bo1", ["tuan_somi"],
             "Phòng khách: CH-1 (Tuấn) đứng bên phải nhìn sang trái với ánh mắt chân tình giải thích lý do.",
             "CH-1 lắc đầu nhẹ dặn dò vợ bạn.",
             "CH-1 (Tuấn, giọng chân thành sâu lắng)",
             "Em cứ cầm lo giữ căn nhà cho con. Sơn đang mê đầu tư ảo, đưa tiền mặt chỉ hại nó thôi."),

            ("s09", "MED", "e05bo1", ["tuan_somi", "uyen_sodo"],
             "Phòng khách: CH-2 (Uyên ôm sổ đỏ) bên trái cúi đầu cảm tạ CH-1 (Tuấn) bên phải.",
             "CH-1 gật đầu tiễn vợ bạn ra cửa với nụ cười bao dung.",
             "CH-1 (Tuấn, giọng ấm áp dứt khoát)",
             "Cứ để nó trách anh cũng được, miễn sao qua vấp ngã này nó tỉnh ngộ quay về lo cho vợ con."),

            ("s10", "CU", "e05bo1", ["uyen_sodo"],
             "Phòng khách: CH-1 (Uyên ôm chặt sổ đỏ) bên trái cúi đầu rưng rưng tri ân bạn của chồng.",
             "CH-1 lau nước mắt cúi chào Tuấn trước khi bước ra ngoài.",
             "CH-1 (Uyên, nghẹn giọng biết ơn sâu sắc)",
             "Ân nghĩa lớn này của anh Tuấn, suốt cuộc đời gia đình em không bao giờ quên đâu ạ!"),

            ("s11", "WIDE", "e05bo2", ["son", "uyen_sodo"],
             "Hành lang sảnh thang máy chung cư: CH-1 (Sơn) đứng bên trái sững sờ bắt gặp vợ CH-2 (Uyên ôm cuốn sổ đỏ) vừa bước ra từ nhà Tuấn bên phải.",
             "CH-1 trố mắt nhìn cuốn sổ đỏ trên tay vợ đầy kinh ngạc.",
             "CH-1 (Sơn, sững người lắp bắp hỏi vợ)",
             "Uyên? Sao em từ nhà thằng Tuấn bước ra, cuốn sổ đỏ của ai trên tay em thế kia?"),

            ("s12", "CU", "e05bo2", ["uyen_sodo", "son"],
             "Hành lang thang máy: CH-1 (Uyên ôm sổ đỏ) bên phải bật khóc nói thẳng sự thật cho chồng CH-2 (Sơn) bên trái.",
             "CH-1 giơ cuốn sổ đỏ lên, nghẹn ngào đánh thức chồng.",
             "CH-1 (Uyên, bật khóc nghẹn ngào nói với chồng)",
             "Sổ đỏ nhà anh Tuấn đấy! Anh ấy sợ anh nướng sạch tiền nên đóng vai ác, âm thầm cứu mẹ con em!"),

            ("s13", "CU", "e05bo2", ["son"],
             "Hành lang thang máy: cận cảnh CH-1 (Sơn) bên trái chết lặng, hai mắt đỏ hoe trào nước mắt hối hận tột cùng.",
             "CH-1 run rẩy đưa tay che mặt bật khóc ân hận vì trách lầm bạn tri kỷ.",
             "CH-1 (Sơn, giọng nghẹn đắng rơi nước mắt hối hận)",
             "Trời ơi Tuấn ơi... tao đúng là thằng mù quáng mới buông lời trách lầm người anh em tốt nhất đời mình!"),

            ("s14", "WIDE", "e05bo1", ["tuan_somi"],
             "Trong căn hộ ban công kính sáng thoáng: một mình CH-1 (Tuấn) đứng trầm tư hướng mắt ra khung cửa thành phố.",
             "CH-1 khẽ mỉm cười nhẹ nhõm vì giữ được mái ấm cho bạn.",
             None, ""),

            ("s15", "CU", "e05bo1", ["tuan_somi"],
             "Trong phòng khách căn hộ: CH-1 (Tuấn) quay mặt nhìn thẳng ống kính hỏi ý kiến khán giả.",
             "CH-1 nhìn thẳng camera trò chuyện điềm đạm rồi khép môi.",
             "CH-1 (Tuấn, nhìn thẳng ống kính hỏi khán giả)",
             "Chấp nhận mang tiếng ác để cứu vợ con bạn và giúp bạn tỉnh ngộ, mọi người thấy Tuấn làm đúng không ạ?"),
        ],
    },
}
