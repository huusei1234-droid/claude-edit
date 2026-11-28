# -*- coding: utf-8 -*-
"""
Director V7 Coherent "Sự Vô Lý" Intro Highlights (`261126` 20 Films):
1. Highlight ONLY at `0.0s` (Opening Intro) — ZERO highlight at episode endings!
2. Every Opening Intro is a COHERENT, CONNECTED 2–3 turn confrontation exchange right at the peak of
   absurdity / outrageous injustice (`sự vô lý`) so:
   - Nobody is cut off mid-thought (`0%` ngắt lời vô nghĩa).
   - Character relationships (`mẹ chồng - nàng dâu / bố vợ - con rể / vợ - chồng / anh chị - em ruột`) are immediately clear.
   - ZERO spoilers of the final payback/resolution -> viewers boil with indignation and MUST watch on!
3. Split episodes (`tập 1`, `tập 2`) stop the story right at the dramatic cliffhanger turn (`split_after`), with NO end-highlight montage.
"""

CURATED_261126_V6 = {
    # R01: Tiệc tân gia 6 tỷ nhà ngoại nhận vơ khinh thông gia quê (17 shots)
    # Intro: Bố chồng quê xin về bến xe -> Vợ giục chồng đuổi bố mẹ chồng -> Bố vợ vỗ ngực nhận vơ mua nhà 6 tỷ! (0% lộ sao kê!)
    "r01": {
        "split_after": "s08",
        "full_hook": ["s06", "s07", "s08"],
        "tap1_hook": ["s06", "s07", "s08"],
        "tap2_hook": ["s04", "s07", "s08"],
    },
    # R02: Con dâu gửi 5 triệu báo hiếu bố bị mắng ăn bám (16 shots)
    # Intro: Mẹ chồng mắng ăn bám tuồn tiền về ngoại -> Con dâu nghẹn ngào giải thích tiền riêng mua thuốc cho bố -> Chị chồng hoạch họe! (0% lộ lương 40tr!)
    "r02": {
        "split_after": "s06",
        "full_hook": ["s02", "s03", "s04"],
        "tap1_hook": ["s02", "s03", "s04"],
        "tap2_hook": ["s10", "s11"],
    },
    # R03: Con dâu nấu 10 mâm cỗ giỗ bỏng tay bị vu đập bát (16 shots)
    # Intro: Thím Hoa tâng bốc mẹ chồng nấu 10 mâm -> Mẹ chồng hất vỡ bát vu oan con dâu dằn mặt -> Con dâu khóc kêu oan! (0% lộ bẫy túi nấm!)
    "r03": {
        "split_after": "s08",
        "full_hook": ["s04", "s05", "s06"],
        "tap1_hook": ["s04", "s05", "s06"],
        "tap2_hook": ["s05", "s08"],
    },
    # R04: Mẹ quê mang làn trứng lên thăm bị gài bẫy lấy nhẫn kim cương 150tr (15 shots)
    # Intro: Con dâu lôi hộp nhẫn trong làn trứng vu ăn cắp -> Mẹ quê khóc van con trai tin mình -> Mẹ vợ khoanh tay làm chứng giả!
    "r04": {
        "split_after": "s07",
        "full_hook": ["s05", "s06", "s07"],
        "tap1_hook": ["s05", "s06", "s07"],
        "tap2_hook": ["s05", "s07", "s09"],
    },
    # R05: Biếu mẹ ngoại 10tr được khen, biếu mẹ ruột 5tr mua thuốc bị vợ cấm (14 shots)
    # Intro: Chồng hỏi lấy lương mua thuốc cho mẹ có gì sai -> Vợ tuyên bố chỉ cho biếu mẹ đẻ 10tr cấm đưa mẹ chồng 5tr -> Chồng uất ức hỏi vặn!
    "r05": {
        "split_after": "s07",
        "full_hook": ["s04", "s05", "s06"],
        "tap1_hook": ["s04", "s05", "s06"],
        "tap2_hook": ["s05", "s07"],
    },
    # R06: Chị dâu mắng mẹ chồng làm rụng tóc khắp nhà & sợi tóc nhuộm nâu (13 shots)
    # Intro: Mẹ chồng chỉ tóc bạc trắng búi gọn sao đen nâu được -> Chị dâu tóc nâu cãi ngang -> Mẹ chồng nhẫn nhịn nhận quét!
    "r06": {
        "split_after": "s06",
        "full_hook": ["s02", "s03", "s04"],
        "tap1_hook": ["s02", "s03", "s04"],
        "tap2_hook": ["s02", "s03", "s06"],
    },
    # R07: Bà cụ nhặt vỏ chai xin cơm thừa ở quán vỉa hè (14 shots)
    # Intro: Khách cộc cằn xua đuổi bà cụ nghèo đứng cạnh bàn ngứa mắt -> Bà cụ rụt rè xin đĩa cơm thừa khách bỏ lại!
    "r07": {
        "split_after": "s07",
        "full_hook": ["s03", "s05"],
        "tap1_hook": ["s02", "s03", "s05"],
        "tap2_hook": ["s03", "s05"],
    },
    # R08: Ông cụ đãng trí ngồi nhầm bàn ăn bị xua đuổi (13 shots)
    # Intro: Gã khách thô lỗ quát đuổi cụ ông -> Hai chàng trai dìu cụ sang bàn mình mời ăn!
    "r08": {
        "split_after": "s07",
        "full_hook": ["s03", "s04"],
        "tap1_hook": ["s03", "s04"],
        "tap2_hook": ["s03", "s04"],
    },
    # R09: Bà cụ nhặt ve chai trả lại cọc tiền rơi bị cô gái sang chảnh vu ăn cắp (13 shots)
    # Intro: Bà cụ chìa tiền rơi trả lại bị cô gái giật lấy vu móc túi ăn cắp -> Bà cụ sững sờ kêu trời!
    "r09": {
        "split_after": "s07",
        "full_hook": ["s07", "s08"],
        "tap1_hook": ["s02", "s03", "s07"],
        "tap2_hook": ["s07", "s10"],
    },
    # R10: Vợ bắt tống mẹ chồng ngồi xe lăn vào viện dưỡng lão dù đang ở nhà tên mẹ (14 shots)
    # Intro: Chồng đòi đón mẹ đau chân về nhà -> Vợ chỉ xe lăn bắt tống vào viện dưỡng lão hoặc đẩy về quê -> Mẹ già khóc van con! (0% lộ sổ đỏ!)
    "r10": {
        "split_after": "s08",
        "full_hook": ["s07", "s08", "s09"],
        "tap1_hook": ["s06", "s07", "s08"],
        "tap2_hook": ["s06", "s07", "s08"],
    },
    # R11: Giám đốc chi nhánh bắt cô lao công quỳ lau giày (14 shots)
    # Intro: Cô lao công xin thông cảm vì thang hàng bảo trì -> GĐ bắt cúi lau sạch mũi giày -> Khoe chị ruột làm GĐ Nhân sự tổng thích đuổi ai là đuổi!
    "r11": {
        "split_after": "s08",
        "full_hook": ["s02", "s03", "s08"],
        "tap1_hook": ["s02", "s03", "s05"],
        "tap2_hook": ["s02", "s03", "s08"],
    },
    # R12: Dặn chồng giữ thể diện trước bố mẹ vợ, cô vợ ngủ nướng mắng oan chồng (13 shots)
    # Intro: Vợ vừa ngủ dậy thấy đĩa rau mắng chồng trọng nội khinh ngoại mời bố mẹ vợ ăn chay -> Chồng xin nói hết câu -> Vợ tiếp tục mắng oan!
    "r12": {
        "split_after": "s07",
        "full_hook": ["s05", "s06", "s07"],
        "tap1_hook": ["s05", "s06", "s07"],
        "tap2_hook": ["s03", "s05", "s07"],
    },
    # R13: Quản lý ăn chặn 1 triệu tiền công của bà cụ có chồng nằm viện (13 shots)
    # Intro: Bà cụ hỏi thỏa thuận 2 triệu sao đưa 1 triệu -> Quản lý ăn chặn trắng trợn bảo lúc sáng nói miệng -> Dọa gọi bảo vệ lôi cổ!
    "r13": {
        "split_after": "s07",
        "full_hook": ["s02", "s03", "s05"],
        "tap1_hook": ["s02", "s03", "s05"],
        "tap2_hook": ["s02", "s03", "s07"],
    },
    # R14: Con gái trách mẹ kho cá mặn giặt rách áo mà không biết mẹ mờ mắt (13 shots)
    # Intro: Mẹ già nheo mắt tủi thân xin về -> Con gái cằn nhằn cá kho mặn áo lụa giặt rách -> Trách mẹ không chú tâm nhầm hũ muối! (0% lộ bệnh mắt & 10tr!)
    "r14": {
        "split_after": "s05",
        "full_hook": ["s02", "s03", "s05"],
        "tap1_hook": ["s02", "s03", "s05"],
        "tap2_hook": ["s03", "s04", "s05"],
    },
    # R15: Chồng ham bạn nhậu bỏ mặc vợ đợi cơm nguội (12 shots)
    # Intro: Bạn nhậu khích tướng bản lĩnh đàn ông -> Chồng sĩ diện gắt đuổi vợ đi về trước!
    "r15": {
        "split_after": "s06",
        "full_hook": ["s02", "s03"],
        "tap1_hook": ["s02", "s03"],
        "tap2_hook": ["s02", "s03"],
    },
    # R16: Động chút cãi nhau là chặn số xách vali về ngoại (12 shots)
    # Intro: Vợ kéo vali tuyên bố chặn số -> Chồng bình thản chuyển 20 triệu không giữ -> Vợ khựng lại chột dạ hỏi vặn!
    "r16": {
        "split_after": "s06",
        "full_hook": ["s02", "s03", "s04"],
        "tap1_hook": ["s02", "s03", "s04"],
        "tap2_hook": ["s02", "s03", "s04"],
    },
    # R17: Sau đám tang bố già người vợ rụt rè xin nuôi hai cháu mồ côi (11 shots)
    # Intro: Vợ rụt rè xin đón 2 cháu mồ côi nhận làm thêm ca đêm -> Chồng đanh mặt hỏi gắt -> Vợ khóc xin lỗi rút lời! (0% lộ câu trả lời!)
    "r17": {
        "split_after": "s05",
        "full_hook": ["s03", "s04", "s05"],
        "tap1_hook": ["s03", "s04", "s05"],
        "tap2_hook": ["s03", "s04", "s05"],
    },
    # R18: Về quê thăm mẹ già dậy sớm nấu cơm con dâu chê bẩn ném trả tờ 200k (11 shots)
    # Intro: Con dâu chê nhà mẹ chồng chật không thở nổi -> Chồng nhắc mẹ dậy từ 4h sáng -> Con dâu chê cơm ám khói đen nhẻm đòi trả tờ 200k!
    "r18": {
        "split_after": "s06",
        "full_hook": ["s03", "s04", "s05"],
        "tap1_hook": ["s03", "s04", "s05"],
        "tap2_hook": ["s03", "s04", "s05"],
    },
    # R19: Vay 25 cây vàng lúc 45tr nay vàng tăng đòi trả 1 tỷ tiền mặt (11 shots)
    # Intro: Chị dâu tỉnh bơ quy giá vàng cũ 45tr trả 1 tỷ -> Em trai nhắc vay 25 cây vàng -> Anh ruột đập bàn mắng ngược em trai thất đức tính toán!
    "r19": {
        "split_after": "s06",
        "full_hook": ["s02", "s03", "s04"],
        "tap1_hook": ["s02", "s03", "s04"],
        "tap2_hook": ["s02", "s04", "s05"],
    },
    # R20: Con trai lấy tiền lẻ bán rau của mẹ già đi nhậu (13 shots)
    # Intro: Con trai nhét tiền lẻ của mẹ đi nhậu giục mẹ ra chợ bán rau -> Khách nhắc nhở -> Con trai hất cằm bảo người ngoài tránh đường!
    "r20": {
        "split_after": "s07",
        "full_hook": ["s02", "s03", "s04"],
        "tap1_hook": ["s02", "s03", "s04"],
        "tap2_hook": ["s02", "s06", "s07"],
    },
}
