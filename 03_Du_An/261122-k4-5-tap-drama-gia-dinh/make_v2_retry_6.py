import json, os

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
CAST_DIR = os.path.join(BASE_DIR, "cast_clean")
BODY_DIR = os.path.join(BASE_DIR, "cast_fullbody")
SETS_DIR = os.path.join(BASE_DIR, "sets")

jobs_6 = [
    {
        "id": "v03_w12_9x16",
        "episode": "v03", "scene": "w12", "ratio": "9:16", "seconds": 6, "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v03", "raw_9x16", "w12.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V3_BO1_PhongChuTichCoLan.jpg"), "name": "set_v3bo1.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_khai_full.jpg"), "name": "k4_khai_full.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_son_full.jpg"), "name": "k4_son_full.jpg"},
        ],
        "prompts": [
            'Tạo video 6 giây, điện ảnh người thật photorealistic live-action, khung dọc 9:16. BỐI CẢNH: tại @set_v3bo1.jpg sáng ấm sang trọng. GÓC MÁY: TRUNG CẢNH RỘNG từ thắt lưng trở lên thấy rõ không gian phòng Chủ tịch. CHỐT KHÔNG GIAN & DIỄN BIẾN: Bên phải người cha mặc vest xám @k4_khai_full.jpg xúc động bước gần đặt tay lên vai con trai @k4_son_full.jpg đứng bối rối bên trái để động viên. THOẠI TRỰC TIẾP: Người cha mặc vest bên phải nói tiếng Việt trầm ấm rõ chữ khớp khẩu hình: "Sơn ơi trước mắt con cứ để ba hỗ trợ chăm lo sức khỏe cho em gái đã, ba nhất định sẽ thu xếp ổn thỏa để đón hai anh em về!" YÊU CẦU: Giữ nguyên gương mặt trang phục tham chiếu, không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay điện ảnh 6 giây người thật khung dọc 9:16 tại @set_v3bo1.jpg: trung cảnh rộng bên phải ông bố mặc vest @k4_khai_full.jpg ân cần dặn dò con trai @k4_son_full.jpg đứng bên trái. Ông bố nói tiếng Việt rõ chữ: "Con trai đừng lo lắng một mình nữa, việc chăm sóc cho bé An để ba lo liệu trước, rồi ba sẽ thu xếp đón cả hai đứa về đoàn tụ!" Không nhạc nền, không phụ đề, không logo.',
        ],
    },
    {
        "id": "v04_w03_9x16",
        "episode": "v04", "scene": "w03", "ratio": "9:16", "seconds": 6, "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v04", "raw_9x16", "w03.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V4_BO1_CongSanhNhaTu.jpg"), "name": "set_v4bo1.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_tu_full.jpg"), "name": "k4_tu_full.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_basen_full.jpg"), "name": "k4_basen_full.jpg"},
        ],
        "prompts": [
            'Tạo video 6 giây, điện ảnh người thật photorealistic live-action, khung dọc 9:16. BỐI CẢNH: tại @set_v4bo1.jpg trước cổng biệt thự thoáng đãng ban ngày. GÓC MÁY: TOÀN CẢNH RỘNG thấy rõ toàn thân hai nhân vật đứng trước cổng sắt và sảnh nhà. CHỐT KHÔNG GIAN & DIỄN BIẾN: Bên phải chàng rể trẻ @k4_tu_full.jpg rút chiếc điện thoại di động ra vẻ mặt nghiêm túc mời bà cụ @k4_basen_full.jpg đứng bên trái vào bóng mát hiên cổng chờ đợi. THOẠI TRỰC TIẾP: Chàng rể bên phải nói tiếng Việt lễ phép rõ chữ: "Chuyện này lạ thật đó bác, bác cứ đứng nghỉ chân dưới mái hiên mát đợi cháu một lát nhé, để cháu bấm máy gọi cô ấy về hỏi cho ra lẽ ngay!" YÊU CẦU: Giữ nguyên gương mặt trang phục tham chiếu, không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay điện ảnh 6 giây người thật khung dọc 9:16 tại @set_v4bo1.jpg: toàn cảnh rộng trước cổng biệt thự, @k4_tu_full.jpg bên phải cầm điện thoại lễ phép nói với @k4_basen_full.jpg bên trái bằng tiếng Việt rõ chữ: "Bác đi đường xa vất vả rồi, bác đứng nép vào hiên mát chờ cháu ít phút nha, cháu gọi điện bảo vợ cháu chạy về ngay bây giờ ạ!" Không nhạc nền, không phụ đề, không logo.',
        ],
    },
    {
        "id": "v05_w02_9x16",
        "episode": "v05", "scene": "w02", "ratio": "9:16", "seconds": 6, "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v05", "raw_9x16", "w02.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V5_BO3_KhoangXeHoa.jpg"), "name": "set_v5bo3.jpg"},
            {"path": os.path.join(CAST_DIR, "G04_06_Kieu.jpg"), "name": "k4_kieu.jpg"},
            {"path": os.path.join(CAST_DIR, "G05_05c_NhungPhuDau.jpg"), "name": "k4_nhung.jpg"},
        ],
        "prompts": [
            'Tạo video 6 giây, điện ảnh người thật photorealistic live-action, khung dọc 9:16. BỐI CẢNH: bên trong khoang ghế da sau xe cưới @set_v5bo3.jpg có cửa xe mở hé nhìn ra sân nắng. GÓC MÁY: TRUNG CẢNH RỘNG thấy rõ hai người ngồi trên băng ghế sau xe hoa. CHỐT KHÔNG GIAN & DIỄN BIẾN: Cô dâu đội mấn @k4_kieu.jpg ngồi bên trái và phù dâu áo dài ren @k4_nhung.jpg ngồi sát bên phải ghé sát rỉ tai bàn tính giữ giá không chịu bước xuống xe. THOẠI TRỰC TIẾP: Phù dâu bên phải nói tiếng Việt nhỏ mà sắc sảo rõ chữ: "Nghe lời tao cứ ngồi yên trên xe khoan bước xuống vội, giờ làm lễ tới sát nút rồi kiểu gì nhà trai sợ mất thể diện cũng phải chiều ý mình thôi!" YÊU CẦU: Giữ nguyên gương mặt trang phục tham chiếu, không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay điện ảnh 6 giây người thật khung dọc 9:16 trong khoang ghế da xe cưới @set_v5bo3.jpg: trung cảnh rộng cô dâu @k4_kieu.jpg ngồi bên trái cạnh phù dâu @k4_nhung.jpg bên phải. Phù dâu bên phải thì thầm tiếng Việt rõ chữ: "Mày cứ giữ vững lập trường ngồi yên trên xe cho tao, quan khách nhà ảnh đứng đầy ngoài sân kia rồi, đòi thêm sính lễ lúc này chắc chắn được!" Không nhạc nền, không phụ đề, không logo.',
        ],
    },
    {
        "id": "v05_w03_9x16",
        "episode": "v05", "scene": "w03", "ratio": "9:16", "seconds": 6, "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v05", "raw_9x16", "w03.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V5_BO2_DamCuoiDongNguoi.jpg"), "name": "set_v5bo2.jpg"},
            {"path": os.path.join(CAST_DIR, "G05_05c_NhungPhuDau.jpg"), "name": "k4_nhung.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_quan_full.jpg"), "name": "k4_quan_full.jpg"},
        ],
        "prompts": [
            'Tạo video 6 giây, điện ảnh người thật photorealistic live-action, khung dọc 9:16. BỐI CẢNH: tại sân rước dâu đông quan khách hai họ @set_v5bo2.jpg. GÓC MÁY: TOÀN CẢNH RỘNG thấy rõ chiếc xe hoa trắng, đông đảo khách mời hai bên và toàn thân nhân vật đứng giữa sân. CHỐT KHÔNG GIAN & DIỄN BIẾN: Phù dâu áo dài ren trắng @k4_nhung.jpg bước ra đứng khoanh tay chắn trước cửa xe hoa bên trái đối diện chú rể áo dài đen @k4_quan_full.jpg đứng sững sờ bên phải giữa ánh nhìn ngơ ngác của quan khách. THOẠI TRỰC TIẾP: Phù dâu bên trái nói tiếng Việt kiêu kỳ rõ chữ: "Chú rể đứng lùi lại chút đi! Hôm nay nhà trai chưa giải quyết xong yêu cầu sính lễ bổ sung thì cô dâu nhất quyết chưa bước xuống xe đâu!" YÊU CẦU: Giữ nguyên gương mặt trang phục tham chiếu, không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay điện ảnh 6 giây người thật khung dọc 9:16 tại sân cưới đông người @set_v5bo2.jpg: toàn cảnh rộng phù dâu @k4_nhung.jpg đứng chắn cửa xe hoa bên trái đối mặt chú rể @k4_quan_full.jpg bên phải trước mặt họ hàng. Phù dâu nói tiếng Việt rõ chữ: "Bà con hai họ chứng giám luôn nha, nhà trai chưa thu xếp trọn vẹn khoản sính lễ mới thì chưa được phép đón dâu vào sảnh!" Không nhạc nền, không phụ đề, không logo.',
        ],
    },
    {
        "id": "v05_w05_9x16",
        "episode": "v05", "scene": "w05", "ratio": "9:16", "seconds": 6, "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v05", "raw_9x16", "w05.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V5_BO2_DamCuoiDongNguoi.jpg"), "name": "set_v5bo2.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_kieu_full.jpg"), "name": "k4_kieu_full.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_quan_full.jpg"), "name": "k4_quan_full.jpg"},
        ],
        "prompts": [
            'Tạo video 6 giây, điện ảnh người thật photorealistic live-action, khung dọc 9:16. BỐI CẢNH: tại sân cưới đông quan khách hai họ @set_v5bo2.jpg. GÓC MÁY: TOÀN CẢNH RỘNG thấy rõ toàn thân cô dâu chú rể cạnh xe hoa trắng và họ hàng đứng xem hai bên. CHỐT KHÔNG GIAN & DIỄN BIẾN: Cô dâu áo dài trắng @k4_kieu_full.jpg đứng cạnh cửa xe bên trái khoanh tay lạnh lùng lắc đầu từ chối lời khuyên của chú rể @k4_quan_full.jpg đứng bên phải. THOẠI TRỰC TIẾP: Cô dâu bên trái nói tiếng Việt dứt khoát rõ chữ: "Không có chuyện đợi làm lễ xong mới bàn bạc hứa hẹn sau! Hôm nay anh chưa đáp ứng đúng yêu cầu của em ngay tại sân này thì khỏi tiến hành lễ cưới!" YÊU CẦU: Giữ nguyên gương mặt trang phục tham chiếu, không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay điện ảnh 6 giây người thật khung dọc 9:16 tại sân biệt thự đông khách cưới @set_v5bo2.jpg: toàn cảnh rộng cô dâu @k4_kieu_full.jpg đứng bên trái khoanh tay kiêu ngạo trước mặt chú rể @k4_quan_full.jpg bên phải. Cô dâu nói tiếng Việt rõ chữ: "Em nói một lời là một lời, chuyện lễ nghĩa phải dứt điểm ngay trước khi bước qua cổng, không đồng ý thì hôm nay dừng hết tại đây!" Không nhạc nền, không phụ đề, không logo.',
        ],
    },
    {
        "id": "v05_w06_9x16",
        "episode": "v05", "scene": "w06", "ratio": "9:16", "seconds": 7, "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v05", "raw_9x16", "w06.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V5_BO2_DamCuoiDongNguoi.jpg"), "name": "set_v5bo2.jpg"},
            {"path": os.path.join(BODY_DIR, "k4_quan_full.jpg"), "name": "k4_quan_full.jpg"},
            {"path": os.path.join(CAST_DIR, "G05_05c_NhungPhuDau.jpg"), "name": "k4_nhung.jpg"},
        ],
        "prompts": [
            'Tạo video 7 giây, điện ảnh người thật photorealistic live-action, khung dọc 9:16. BỐI CẢNH: tại sân cưới đông đảo quan khách hai họ @set_v5bo2.jpg. GÓC MÁY: TOÀN CẢNH RỘNG CAO TRÀO thấy rõ chiếc xe hoa trắng, toàn thân chú rể và đám đông quan khách sững sờ hai bên. CHỐT KHÔNG GIAN & DIỄN BIẾN: Chú rể áo dài đen @k4_quan_full.jpg bên phải dứt khoát khép cánh cửa xe hoa lại trước vẻ chết sững của @k4_nhung.jpg bên trái rồi khoát tay ra hiệu cho bác tài xế cho xe rời đi. THOẠI TRỰC TIẾP: Chú rể nói lớn tiếng Việt đanh thép rõ chữ giữa sân: "Khỏi cần bước xuống nữa! Nhờ bác tài nổ máy quay đầu xe đưa cô dâu về lại bên nhà ngoại ngay lập tức, gia đình tôi không đón nữa!" YÊU CẦU: Giữ nguyên gương mặt trang phục tham chiếu, không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay điện ảnh 7 giây người thật khung dọc 9:16 tại sân biệt thự đông khách cưới @set_v5bo2.jpg: toàn cảnh rộng chú rể @k4_quan_full.jpg đứng bên phải dứt khoát đóng cửa xe trước mặt @k4_nhung.jpg và ra hiệu cho xe quay đầu. Chú rể nói tiếng Việt rõ chữ: "Đã coi trọng vật chất hơn tình nghĩa vợ chồng thì dừng ngay tại cổng! Bác tài cho xe quay đầu về nhà ngoại liền giùm tôi!" Không nhạc nền, không phụ đề, không logo.',
        ],
    },
]

out_p = os.path.join(BASE_DIR, "flow_v2_retry_6.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(jobs_6, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(jobs_6)} final V2 retry jobs -> {out_p}")
