# -*- coding: utf-8 -*-
"""
Builds `flow_k5ep01_v6_master.json` (11 V6 scenes: fixes fake white boxes in s06/s07/s09/s13,
fixes repeated/swallowed words in s03/s11/s16/s17, adds s10b [Linh hiding 2 real BOJOMI boxes]
and s12b [Wide Shot of Tuấn & Thảo rushing over to Linh's corner to catch her red-handed],
and upgrades s03/s09/s12b/s17 to lively Wide/Medium-Long blocking shots).
"""
import json
import os

BASE = r"C:\AI\full studio\output\k5-ep01-v4"
RAW6 = os.path.join(BASE, "raw_v6_master")
SETS = os.path.join(BASE, "sets")
CAST = os.path.join(BASE, "cast_clean")
PAIR = os.path.join(BASE, "cast_pairs")

BO_EMPTY = {"path": os.path.join(SETS, "bo1_empty_9x16.jpg"), "name": "bo1_empty.jpg"}
BO_2BOJ  = {"path": os.path.join(SETS, "bo1_2bojomi_nobag_9x16.jpg"), "name": "bo1_2boj.jpg"}
PR_2BOJ  = {"path": os.path.join(SETS, "pr_2bojomi_nobag_1x1.jpg"), "name": "pr_2bojomi_box.jpg"}

C_THAO   = {"path": os.path.join(CAST, "k5_thao.jpg"), "name": "k5_thao.jpg"}
C_TUAN   = {"path": os.path.join(CAST, "k5_tuan.jpg"), "name": "k5_tuan.jpg"}
C_HANH   = {"path": os.path.join(CAST, "k5_bahanh.jpg"), "name": "k5_bahanh.jpg"}
C_LINH   = {"path": os.path.join(CAST, "k5_linh.jpg"), "name": "k5_linh.jpg"}
C_NGAN   = {"path": os.path.join(CAST, "k5_ngan.jpg"), "name": "k5_ngan.jpg"}
P_TUAN_THAO = {"path": os.path.join(PAIR, "pair_tuan_thao_full.jpg"), "name": "pair_tuan_thao_full.jpg"}


def make_job(scene, scale, refs, body_prompt, dlg_speaker, dlg_line, seconds=10, alt_refs=None):
    base_header = (
        f"Tạo video {seconds} giây, photorealistic live-action người Việt Nam thật, "
        "phong cách phim truyền hình gia đình Việt Nam chất lượng điện ảnh 8k sáng rõ tự nhiên, tỷ lệ dọc 9:16.\n\n"
    )
    footer = (
        f"\n\nTHOẠI TRỰC TIẾP (GIỌNG MIỀN NAM VIỆT NAM TỰ NHIÊN, ĐỌC ĐÚNG NGUYÊN VĂN MỘT LẦN DUY NHẤT, KHÔNG LẶP TỪ, NÓI XONG KHÉP MÔI):\n"
        f"{dlg_speaker}: “{dlg_line}”\n"
        "(Giọng miền Nam truyền cảm đời thường như diễn viên phim truyền hình thật, phát âm tròn vành rõ chữ không nuốt âm, "
        "TUYỆT ĐỐI KHÔNG LẶP LẠI TỪ CUỐI CÂU HAY GIỮA CÂU, nói dứt câu là khép môi tự nhiên nghỉ nhịp thở 2 giây cuối cảnh; "
        "nhân vật khác chỉ diễn nét mặt phản ứng, không mở miệng nói chèn).\n\n"
        "YÊU CẦU BẮT BUỘC:\n"
        "TUYỆT ĐỐI KHÔNG HIỂN THỊ PHỤ ĐỀ, KHÔNG CHỮ ĐÈ LÊN MÀN HÌNH, không khung đen trên dưới, không watermark."
    )
    p1 = base_header + body_prompt.replace("{TIMING}", "4.2 giây đầu") + footer
    p2 = base_header + body_prompt.replace("{TIMING}", "3.8 giây đầu, nhịp nói dứt khoát trôi chảy") + footer
    job = {
        "id": f"k5v6_{scene}_9x16",
        "episode": "k5ep01_v6",
        "scene": scene,
        "scale": scale,
        "ratio": "9:16",
        "seconds": seconds,
        "outPath": os.path.join(RAW6, f"{scene}.mp4"),
        "refs": refs,
        "prompt": p1,
        "prompts": [p1, p2],
        "overwrite": True,
    }
    if alt_refs:
        job["altRefs"] = alt_refs
    return job


JOBS = [
    # 1. s03 (WS - Cảnh Toàn sinh động Bà Hạnh bước tới bàn ăn thấy 2 hộp BOJOMI thật gọi Linh, 0% lặp từ 'đi')
    make_job(
        "s03", "WS",
        [BO_2BOJ, C_HANH, PR_2BOJ],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Phòng ăn sáng sủa có 2 hộp giấy BOJOMI trên bàn)\n"
            "- image 2: CH-1 (Bà Hạnh mặc đồ bộ nhung đỏ đô)\n"
            "- image 3: PR-1 (Đúng 2 hộp giấy cứng chữ nhật đứng nắp phẳng AN VƯỢNG PHARMA BOJOMI màu trắng xanh lá đậm)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 từ image 2. Hai hộp trên bàn BẮT BUỘC giữ nguyên 100% hình dáng "
            "HỘP GIẤY CỨNG NẮP PHẲNG màu trắng - xanh lá đậm có in hình tách xanh và chữ BOJOMI của ĐÚNG 2 HỘP từ image 3 "
            "(tuyệt đối không có túi giấy, không hộp trắng trơn, không nắp vặn nhựa).\n\n"
            "CAMERA & BỐ CỤC CẢNH TOÀN SINH ĐỘNG (WIDE / MEDIUM-LONG SHOT):\n"
            "Góc máy Toàn dọc rộng rãi (thấy từ ngang đùi trở lên và trọn không gian phòng ăn ấm cúng cùng mặt bàn đá phía trước): "
            "CH-1 từ phía sau bước nhanh lại sát bàn ăn nơi đặt 2 hộp BOJOMI thật, một tay đặt lên cạnh hộp quà vẻ mặt hớn hở tham lam, "
            "tay kia áp điện thoại lên tai gọi con gái trong {TIMING}."
        ),
        "CH-1",
        "Alo Linh hả con gái! Qua nhà má lẹ lên con, chị vợ thằng Tuấn mới đem qua hai hộp Bojomi xịn lắm nè!",
    ),

    # 2. s06 (MCU - Linh bưng tách sứ xanh lá khen ngon với Bà Hạnh, MẶT BÀN TRỐNG 0% HỘP GIẢ!)
    make_job(
        "s06", "MCU",
        [BO_EMPTY, C_LINH, C_HANH],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Không gian phòng ăn bếp mặt bàn trống gọn gàng)\n"
            "- image 2: CH-1 (Linh mặc áo sơ mi trắng bên phải)\n"
            "- image 3: CH-2 (Bà Hạnh mặc đồ bộ nhung đỏ đô bên trái)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 và CH-2. "
            "QUY TẮC ĐẠO CỤ TUYỆT ĐỐI: Trên mặt bàn và trong khung hình TUYỆT ĐỐI KHÔNG CÓ bất kỳ hộp giấy, hộp sữa hay túi quà nào! "
            "Chỉ duy nhất trên tay CH-1 đang cầm một chiếc TÁCH SỨ MÀU XANH LÁ ĐẬM nhỏ gọn.\n\n"
            "CAMERA & DIỄN BIẾN (MEDIUM CLOSE-UP):\n"
            "Trung cận hai mẹ con đứng trò chuyện đắc ý trong bếp (mặt bàn trống sạch hoàn toàn): CH-1 vừa nhấp một ngụm nhỏ từ tách sứ xanh lá đậm "
            "vừa quay sang CH-2 xuýt xoa khen ngon trong {TIMING}, CH-2 đứng cạnh gật gù cười chiều chuộng."
        ),
        "CH-1",
        "Công nhận sữa hạt Bojomi của chị Thảo uống thơm thanh thiệt đó má, thảo nào một hộp hơn năm trăm ngàn!",
    ),

    # 3. s07 (CU - Bà Hạnh xúi Linh đem 2 hộp về uống, MẶT BÀN TRỐNG SẠCH 0% HỘP TRẮNG GIẢ!)
    make_job(
        "s07", "CU",
        [BO_EMPTY, C_HANH, C_LINH],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Phòng ăn bếp ấm cúng mặt bàn trống)\n"
            "- image 2: CH-1 (Bà Hạnh mặc đồ bộ nhung đỏ đô bên trái)\n"
            "- image 3: CH-2 (Linh mặc áo trắng bên phải)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 và CH-2. "
            "QUY TẮC ĐẠO CỤ TUYỆT ĐỐI: Khung hình cận từ ngang ngực trở lên, KHÔNG CÓ mặt bàn lộn xộn, TUYỆT ĐỐI KHÔNG CÓ bất kỳ hộp giấy hay hộp quà nào xuất hiện trong cảnh này!\n\n"
            "CAMERA & DIỄN BIẾN (CLOSE-UP):\n"
            "Cận cảnh hai mẹ con: CH-1 âu yếm vỗ nhẹ lên cánh tay CH-2 thiên vị ra mặt, nói nhỏ rủ rỉ trong {TIMING}; CH-2 cười tít mắt đắc ý."
        ),
        "CH-1",
        "Con gái má cành vàng lá ngọc mới xứng uống canxi tảo biển, lát con đem nguyên hai hộp đó về uống luôn đi!",
    ),

    # 4. s09 (WS - CẢNH TOÀN đối đầu trong bếp giữa Thảo & Bà Hạnh, MẶT BÀN TRỐNG SẠCH 0% SẢN PHẨM!)
    make_job(
        "s09", "WS",
        [BO_EMPTY, C_HANH, C_THAO],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Không gian rộng phòng ăn - bếp mặt bàn trống trơn chỉ có bình hoa góc bàn)\n"
            "- image 2: CH-1 (Bà Hạnh mặc đồ bộ nhung đỏ đô đứng bên phải)\n"
            "- image 3: CH-2 (Thảo mặc pijama lụa hồng đứng bên trái)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 và CH-2. "
            "CẤM TUYỆT ĐỐI ĐẶT HỘP SẢN PHẨM: Mặt bàn đá cẩm thạch ở giữa hoàn toàn trống sạch như image 1, TUYỆT ĐỐI KHÔNG CÓ bất kỳ hộp giấy, hộp sữa hay chữ BOJOMI nào trên bàn!\n\n"
            "CAMERA & BỐ CỤC CẢNH TOÀN SINH ĐỘNG (WIDE FULL-ROOM BLOCKING SHOT):\n"
            "Cảnh Toàn dọc (thấy từ đầu gối trở lên của cả hai nhân vật trong không gian phòng bếp rộng thoáng): CH-2 (Thảo, bên trái) mắt đỏ hoe đứng uất ức đối diện má chồng; "
            "CH-1 (Bà Hạnh, bên phải) chống một tay ngang hông, tay kia chỉ thẳng vào bếp quát nạt đuổi con dâu trong {TIMING}."
        ),
        "CH-1",
        "Tao lấy cho con gái ruột tao uống đó rồi sao?! Bước vô nhà này thì cái gì cũng của nhà này, vô bếp đi!",
    ),

    # 5. s10b (MLS - CẢNH MỚI LOGIC #1: Linh giật mình lén chụp ôm giấu 2 hộp BOJOMI thật ra sau lưng ở góc tủ!)
    make_job(
        "s10b", "MLS",
        [BO_2BOJ, C_LINH, PR_2BOJ],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Góc bàn và hệ tủ gỗ phòng ăn có đặt đúng 2 hộp giấy BOJOMI)\n"
            "- image 2: CH-1 (Linh mặc áo sơ mi trắng)\n"
            "- image 3: PR-1 (Đúng 2 hộp giấy cứng chữ nhật đứng nắp phẳng AN VƯỢNG PHARMA BOJOMI màu trắng xanh lá đậm)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 từ image 2. Hai hộp sản phẩm CH-1 cầm BẮT BUỘC giữ nguyên 100% thiết kế "
            "HỘP GIẤY CỨNG NẮP PHẲNG màu trắng - xanh lá đậm có in hình tách xanh và chữ BOJOMI của ĐÚNG 2 HỘP từ image 3 (không túi giấy, không hộp trắng trơn).\n\n"
            "CAMERA & DIỄN BIẾN LOGIC GIẤU TANG VẬT (MEDIUM-LONG SHOT):\n"
            "Cảnh Trung-Toàn sinh động từ ngang đùi trở lên bên góc tủ gỗ phòng ăn: Nghe tiếng anh Hai vừa về ngoài cửa, CH-1 giật bắn mình tái mặt nhìn ngoái ra hướng cửa, "
            "hai tay cuống cuồng gom chụp lấy ĐÚNG 2 HỘP BOJOMI trên bàn ôm giấu sát ra phía sau lưng rồi lùi nép người sát vào cạnh tủ gỗ, miệng lẩm bẩm hoảng hốt trong {TIMING}."
        ),
        "CH-1",
        "Chết rồi, anh Hai về bất thình lình, phải lén giấu hai hộp này ra sau lưng mới được!",
    ),

    # 6. s11 (CU - Bà Hạnh đóng kịch vu oan trước mặt Tuấn, rõ chữ 'gào khóc hỗn hào')
    make_job(
        "s11", "CU",
        [BO_EMPTY, C_HANH],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Phòng ăn ấm cúng nền mờ tự nhiên)\n"
            "- image 2: CH-1 (Bà Hạnh mặc đồ bộ nhung đỏ đô)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1. Không có bất kỳ hộp giấy nào trong cảnh.\n\n"
            "CAMERA & DIỄN BIẾN (CLOSE-UP):\n"
            "Cận cảnh CH-1 vội vã bước ra giả bộ nhăn mặt ấm ức đóng kịch mách lẻo với con trai (nhìn về bên trái khung hình), nói mạch lạc rõ từng chữ trong {TIMING}."
        ),
        "CH-1",
        "Vợ mày ích kỷ lắm Tuấn ơi! Má mới xin uống thử một ly mà nó gào khóc hỗn hào với má kìa!",
    ),

    # 7. s12 (MCU - Chị Hai Ngân đứng cạnh Tuấn tinh mắt chỉ thẳng về góc tủ nơi Linh đang lén giấu)
    make_job(
        "s12", "MCU",
        [BO_EMPTY, C_NGAN, C_TUAN],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Không gian phòng khách - phòng ăn, mặt bàn trống sạch)\n"
            "- image 2: CH-1 (Chị Hai Ngân mặc sơ mi trắng đeo thẻ công sở đứng bên trái)\n"
            "- image 3: CH-2 (Tuấn mặc sơ mi trắng quần tây đứng kế bên phải)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 và CH-2. Mặt bàn hoàn toàn trống sạch, tuyệt đối không có hộp giấy nào.\n\n"
            "CAMERA & DIỄN BIẾN (MEDIUM CLOSE-UP):\n"
            "Trung cận hai người từ ngang thắt lưng trở lên: CH-1 ánh mắt sắc sảo nhìn phát hiện về phía góc tủ bên phải, giơ tay chỉ thẳng về hướng góc tủ vạch trần trong {TIMING}; "
            "CH-2 đứng cạnh lập tức quay phắt ánh mắt nhìn theo tay chỉ của chị vợ với vẻ mặt sững sờ."
        ),
        "CH-1",
        "Bác kêu chỉ xin thử một ly, vậy cô Linh đang nép góc tủ lén giấu cái gì sau lưng kia vậy bác?!",
    ),

    # 8. s12b (WS - CẢNH MỚI LOGIC #2: CẢNH TOÀN ĐỘNG Tuấn & Thảo bước nhanh ùa qua chỗ Linh bắt quả tang!)
    make_job(
        "s12b", "WS",
        [BO_EMPTY, P_TUAN_THAO, C_LINH],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Không gian rộng toàn cảnh phòng ăn và hệ tủ gỗ phía sau, mặt bàn trống sạch)\n"
            "- image 2: CH-1 (Tuấn mặc sơ mi trắng quần tây bên phải ảnh 2) và CH-2 (Thảo mặc pijama hồng bên trái ảnh 2)\n"
            "- image 3: CH-3 (Linh mặc áo trắng đứng nép ở góc tủ bên phải khung hình)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục của Tuấn, Thảo từ image 2 và Linh từ image 3. "
            "QUY TẮC ĐẠO CỤ: Mặt bàn trống sạch 100%, hai tay của CH-3 (Linh) đang giấu chặt ra phía sau lưng sát vách tủ nên TUYỆT ĐỐI KHÔNG vẽ hộp giấy lộ trên mặt bàn!\n\n"
            "CAMERA & CHUYỂN ĐỘNG CẢNH TOÀN BẮT QUẢ TANG (WIDE DYNAMIC GROUP BLOCKING SHOT):\n"
            "Cảnh Toàn dọc sinh động thấy rõ toàn bộ chuyển động cơ thể từ đầu gối trở lên trong căn phòng: Từ phía bên trái khung hình, CH-1 (Tuấn) dẫn đầu cùng CH-2 (Thảo) "
            "bước nhanh dồn dập băng ngang phòng ùa thẳng qua sát góc tủ bên phải nơi CH-3 (Linh) đang giật mình lùi sát tường giấu hai tay sau lưng; "
            "CH-1 đứng sừng sững ngay trước mặt CH-3 chỉ tay nghiêm giọng bắt đưa đồ giấu sau lưng ra trong {TIMING}."
        ),
        "CH-1",
        "Đứng lại đó Linh! Đưa ngay cái thứ em đang lén giấu sau lưng ra đây cho anh coi!",
    ),

    # 9. s13 (MCU - Tuấn đối diện chất vấn Linh sau khi đặt 2 hộp lên bàn ở cu_boj_03, 0% HỘP TRẮNG GIẢ!)
    make_job(
        "s13", "MCU",
        [BO_EMPTY, C_TUAN, C_LINH],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Không gian phòng ăn ấm cúng)\n"
            "- image 2: CH-1 (Tuấn mặc sơ mi trắng đứng bên trái)\n"
            "- image 3: CH-2 (Linh mặc áo trắng đứng bên phải)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 và CH-2. "
            "CẤM TUYỆT ĐỐI ĐẶT HỘP TRONG KHUNG HÌNH NÀY: Khung hình lấy từ ngang ngực trở lên, tiền cảnh hoàn toàn trống thoáng, "
            "TUYỆT ĐỐI KHÔNG CÓ bất kỳ hộp giấy trắng hay vật thể nào che trước người nhân vật!\n\n"
            "CAMERA & DIỄN BIẾN (MEDIUM CLOSE-UP):\n"
            "Trung cận căng thẳng: CH-1 (Tuấn, bên trái) chau mày giận dữ nhìn thẳng chất vấn em gái trong {TIMING}; "
            "CH-2 (Linh, bên phải) sợ xanh mặt rụt vai cúi mắt không dám cãi."
        ),
        "CH-1",
        "Cái gì đây Linh?! Nguyên hai hộp Bojomi của chị dâu em lén giấu đem về mà còn hùa nhau vu oan cho Thảo hả?!",
    ),

    # 10. s16 (MCU - Linh cúi đầu xin lỗi Thảo & Chị Hai Ngân bên cạnh Bà Hạnh muối mặt, 0% lặp chữ 'tham lam')
    make_job(
        "s16", "MCU",
        [BO_EMPTY, C_LINH, C_HANH],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Không gian phòng ăn ấm cúng)\n"
            "- image 2: CH-1 (Linh mặc áo sơ mi trắng đứng tiền cảnh bên phải)\n"
            "- image 3: CH-2 (Bà Hạnh mặc đồ bộ nhung đỏ đô đứng lùi phía sau kế bên)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục CH-1 và CH-2. Mặt bàn và tiền cảnh trống thoáng, không có hộp giấy.\n\n"
            "CAMERA & DIỄN BIẾN (MEDIUM CLOSE-UP):\n"
            "Trung cận hả dạ từ ngang thắt lưng trở lên: CH-1 hai tay đan khép nép trước bụng, cúi thấp đầu hối lỗi hướng về bên trái khung hình nói trọn vẹn câu xin lỗi "
            "mạch lạc liền một hơi trong {TIMING} (tuyệt đối không ngắc ngứ lặp từ); CH-2 đứng kế bên cũng tái mặt cúi gằm đầu xấu hổ im lặng."
        ),
        "CH-1",
        "Em xin lỗi chị Hai Ngân, em xin lỗi chị Thảo, từ nay em không dám tham lam lấy đồ của chị nữa.",
    ),

    # 11. s17 (WS/MLS - Cảnh Toàn kết phim ấm áp Tuấn khoác vai Thảo bên đúng 2 hộp BOJOMI thật, 0% lặp chữ)
    make_job(
        "s17", "WS",
        [BO_2BOJ, P_TUAN_THAO, PR_2BOJ],
        (
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: BO-1 (Phòng ăn sáng ấm có đúng 2 hộp giấy BOJOMI đặt ngay ngắn trên bàn)\n"
            "- image 2: CH-1 (Thảo mặc pijama hồng bên trái) và CH-2 (Tuấn mặc sơ mi trắng bên phải)\n"
            "- image 3: PR-1 (Đúng 2 hộp giấy cứng chữ nhật đứng nắp phẳng AN VƯỢNG PHARMA BOJOMI màu trắng xanh lá đậm)\n\n"
            "REFERENCE BẮT BUỘC:\n"
            "Giữ nguyên 100% khuôn mặt, kiểu tóc, trang phục của Thảo và Tuấn từ image 2. Hai hộp đặt trên mặt bàn phía trước BẮT BUỘC giữ nguyên 100% "
            "HỘP GIẤY CỨNG NẮP PHẲNG màu trắng - xanh lá đậm có in hình tách xanh và chữ BOJOMI của ĐÚNG 2 HỘP từ image 3 (không túi giấy, không hộp trắng trơn).\n\n"
            "CAMERA & BỐ CỤC CẢNH TOÀN KẾT PHIM (WIDE / MEDIUM-LONG WARM TABLEAU):\n"
            "Cảnh Toàn-Trung rộng thoáng thấy rõ không gian phòng ăn ấm áp, hai vợ chồng đứng phía sau bàn ăn có 2 hộp BOJOMI vừa đòi lại được: "
            "CH-2 (Tuấn) vòng tay khoác vai CH-1 (Thảo đang mỉm cười hạnh phúc nhẹ nhõm), Tuấn nhìn thẳng ống kính nói dõng dạc mạch lạc trong {TIMING}."
        ),
        "CH-2",
        "Từ nay trong nhà này ai còn ức hiếp Thảo là tui đưa vợ ra ở riêng ngay! Tui xử lý vậy đã hợp tình hợp lý chưa cô chú anh chị?",
        seconds=10,
    ),
]

out_json = os.path.join(BASE, "flow_k5ep01_v6_master.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(JOBS, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(JOBS)} V6 jobs -> {out_json}")
