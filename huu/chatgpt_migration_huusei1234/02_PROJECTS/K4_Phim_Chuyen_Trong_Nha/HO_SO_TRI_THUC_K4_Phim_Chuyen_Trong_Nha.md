# HỒ SƠ TRI THỨC DỰ ÁN: K4 PHIM CHUYỆN TRONG NHÀ

## I. QUY CHUẨN ĐẠO DIỄN & PROMPT FLOW

Bạn là Đạo diễn & Biên kịch Phim AI chuyên nghiệp cho dự án K4 - Phim Chuyện Trong Nhà (sử dụng Google Flow).
Quy chuẩn bắt buộc khi phân tích kịch bản, lập Asset Board và viết Prompt Video cho Flow:
1. Thời lượng linh hoạt theo từng cảnh (1–15 giây): Cảnh cần bao nhiêu giây thì tạo bấy nhiêu giây (1–3s cho phản ứng ánh mắt, 3–5s hành động đơn giản, 5–10s đối thoại ngắn, 10–15s hành động kết hợp thoại & cảm xúc). Tuyệt đối không ép mặc định 8s hay 15s cố định, giới hạn tối đa 15s/cảnh để tránh mất điểm.
2. Không tự ý chia Shot 1, Shot 2, Shot 3 trong một prompt (mặc định mỗi prompt là một cảnh quay liền mạch trừ khi được yêu cầu rõ).
3. Cấu trúc bắt buộc cho MỌI Prompt Video:
   - IMAGE XUẤT HIỆN: Chỉ liệt kê đúng các mã image (nhân vật, bối cảnh, đạo cụ) thực sự xuất hiện trong cảnh đó. Không mô tả lại ngoại hình/trang phục/đạo cụ đã có sẵn trong ảnh tham chiếu.
   - CHỐT KHÔNG GIAN & VỊ TRÍ: Khóa cứng vị trí trái–phải, khoảng cách, hướng nhìn của từng nhân vật và bối cảnh. Vị trí cuối cùng của nhân vật ở cuối prompt trước BẮT BUỘC là vị trí bắt đầu ở đầu prompt tiếp theo (0% nhảy vị trí hay đảo trục 180 độ).
   - BẮT ĐẦU PROMPT (Số thứ tự): Ưu tiên góc máy CẬN CẢNH (close-up / medium close-up gương mặt, ánh mắt, bàn tay, đạo cụ) làm chủ đạo; giữ nguyên 100% lời thoại đã chốt, phân biệt rõ lời thoại / voice-over / nội tâm; kèm hiệu ứng âm thanh điện ảnh (cinematic sound effects) tinh tế không lấn át thoại; không chèn phụ đề hay chữ lên màn hình.


---

## II. TOÀN BỘ MẪU ASSET BOARD & KỊCH BẢN THỰC CHIẾN TỪ TÀI KHOẢN CŨ


### Cuộc trò chuyện: Phim Chuyện Trong Nhà


#### Lượt 1
à không thêm phần chia nhiều cảnh, mỗi cảnh bao nhiêu giây thì bảo flow tạo bấy nhiêu giây. từ 1 - 15s, prompt chuẩn cho flow
Analysis paused
Analyzed
ChatGPT said:

Đúng rồi, tôi đã chỉnh lại skill theo đúng workflow của bạn: dùng Flow, không mặc định 15 giây và không tự chia Shot.

Đã xuất file Skill dạng Markdown để bạn lưu hoặc đưa vào AI/Flow workflow.

Skill làm phim AI – Flow

Markdown (.md) · Quy chuẩn prompt video

Tải file skill_phim_ai_flow.md

Những điểm đã sửa theo yêu cầu

Thời lượng linh hoạt từ 1–15 giây, tùy nội dung từng cảnh.

Ghi rõ thời lượng video ngay đầu prompt để Flow tạo đúng độ dài.

Không tự chia Shot 1, Shot 2, Shot 3.

Mặc định mỗi prompt là một cảnh quay liền mạch.

Chỉ chia nhiều shot khi bạn yêu cầu rõ.

Cận cảnh là chủ đạo, camera chuyển động có chủ đích.

Giữ nguyên image reference, khuôn mặt, trang phục, bối cảnh.

Thoại, voice-over và suy nghĩ nội tâm phải phân biệt rõ.

Hành động cụ thể, không di chuyển vô nghĩa.

Chốt vị trí nhân vật và continuity giữa các cảnh.

Ví dụ cách viết prompt theo skill mới:

Tạo video 8 giây, photorealistic live-action...

CH-1 ngồi trên giường cạnh nôi em bé. CH-2 mở cửa bước vào, đứng ở cửa phòng, nhìn CH-1 với vẻ khó chịu. Camera giữ góc medium close-up, sau đó di chuyển nhẹ để tập trung vào biểu cảm của CH-2. CH-2 nói...

Không tự chia shot, không tự kéo dài cảnh, Flow tạo video đúng 8 giây.

Từ giờ khi bạn yêu cầu "viết prompt Flow", tôi sẽ áp dụng bộ skill này làm quy chuẩn mặc định.

skill_phim_ai_flow.md
Document


#### Lượt 2
đúng 8 giây cái gì đã bảo tùy cảnh, cảnh bao nhiêu giây thì tạo bấy nhiêu giây, có cảnh từ 1 đến 15s giới hạn để tránh mất điểm
Analyzed
ChatGPT said:

Đúng, tôi đã hiểu sai và đưa ví dụ 8 giây không phù hợp.

Quy tắc chính xác phải là:

Mỗi cảnh có thời lượng riêng, tùy theo nội dung kịch bản.

Có thể từ 1 giây đến tối đa 15 giây.

Cảnh cần 3 giây thì tạo 3 giây; cảnh cần 7 giây thì tạo 7 giây; cảnh cần 12 giây thì tạo 12 giây.

Không ép tất cả cảnh về một thời lượng cố định.

Không kéo dài cảnh để đủ thời gian.

Không nhồi hành động hoặc thoại khiến cảnh bị gấp.

Giới hạn tối đa 15 giây/cảnh để tránh mất điểm và đảm bảo chất lượng tạo video.

Tôi phải tự cân đối thời lượng theo lượng hành động, thoại và nhịp cảm xúc của từng cảnh.

Tôi đã cập nhật lại file Skill, sửa quy tắc thời lượng cho chính xác.

Ví dụ phân bổ thời lượng:

Nội dung cảnh

	

Thời lượng




Một phản ứng ánh mắt

	

1–3 giây




Một hành động đơn giản

	

3–5 giây




Một đoạn đối thoại ngắn

	

5–10 giây




Một hành động kết hợp thoại và cảm xúc

	

10–15 giây

Đây chỉ là ví dụ tham khảo, không phải quy định cứng. Tôi sẽ tự tính theo nội dung thực tế.

Tải file Skill Flow đã cập nhật

Từ giờ nguyên tắc là: Cảnh cần bao nhiêu giây thì tạo bấy nhiêu, tối thiểu 1 giây, tối đa 15 giây. Không tự áp đặt thời lượng.

skill_phim_ai_flow.md
Document


### Cuộc trò chuyện: Viết kịch bản gia đình


#### Lượt 1
kiểm tra thật kĩ vì cảnh đầu tiên là bà mẹ ngồi ở 1 góc nào đó. và sau khi tấ đuổi mẹ xong thì có tuấn ngang thấy. kiểm tra lại assetboard
Đã xử lý trong 19s
ChatGPT said:

Đúng, asset board trước của tôi bị thiếu bối cảnh mở đầu và hành động của Tuấn. Tôi đã gộp tất cả vào phòng ăn gia đình, như vậy chưa bám sát diễn biến câu chuyện.

Tôi rà lại thứ tự câu chuyện và chỉnh lại như sau:

1. Diễn biến mở đầu cần khóa

Bà nội (image 2) ngồi một mình ở một góc, chờ đợi.

Tấn (image 1) mang cơm đến cho mẹ bằng image 6.

Tấn nói mẹ không được đến dự sinh nhật, sau đó rời đi.

Tuấn (image 3) tình cờ đi ngang qua, nhìn thấy sự việc. Đây là chi tiết quan trọng dẫn đến hành động của Tuấn ở những cảnh sau.

2. Asset board điều chỉnh
NHÂN VẬT

Mã

	

Nhân vật

	

Trạng thái




image 1

	

Tấn – ba Tuấn

	

Đã có




image 2

	

Bà nội – mẹ Tấn

	

Đã có




image 3

	

Tuấn – con trai Tấn

	

Đã có




image 4

	

Chú Hùng – bạn Tấn

	

Đã có

BỐI CẢNH

Mã

	

Bối cảnh

	

Công dụng




image 5

	

Góc bà nội ngồi một mình

	

Cảnh mở đầu, Tấn mang cơm đến và Tuấn tình cờ nhìn thấy




image 9

	

Phòng ăn gia đình tổ chức sinh nhật

	

Các cảnh Tấn, Tuấn và chú Hùng trong bữa tiệc

ĐẠO CỤ

Mã

	

Đạo cụ

	

Công dụng




image 6

	

Hộp cơm, bát, đũa

	

Tấn mang cơm cho mẹ




image 7

	

Bàn tiệc, bánh sinh nhật, thức ăn

	

Bữa tiệc sinh nhật




image 8

	

Điện thoại

	

Tuấn phát đoạn ghi âm

3. Cần xác nhận một chi tiết để khóa đúng image 5

Góc bà nội ngồi một mình là ở đâu?

Góc hiên nhà.

Góc sân nhà.

Góc trong nhà, gần cửa ra vào.

Một góc khác.

Tôi chưa tự ý chốt vị trí vì nếu sai, các prompt sau sẽ bị lệch không gian. Tuấn đi ngang nhìn thấy sự việc cũng phải được bố trí đúng trong cùng bối cảnh đó.


#### Lượt 2
làm lại assetboard nào
ChatGPT said:
ASSET BOARD CỐ ĐỊNH

PHIM: SINH NHẬT CỦA BỐ – MÓN QUÀ CỦA TUẤN

BỘ ASSET CHÍNH THỨC

Tôi chỉnh lại theo đúng trình tự câu chuyện: mở đầu là bà nội ngồi một mình ở một góc nhà, Tấn mang cơm đến và đuổi mẹ, Tuấn tình cờ đi ngang nhìn thấy. Sau đó câu chuyện mới chuyển sang bữa tiệc sinh nhật.

1. NHÂN VẬT

IMAGE 1 – TẤN (BA TUẤN)

Nam, 52 tuổi.

Tóc đen, mặc sơ mi trắng, quần tây xám.

Là con trai của bà nội, bố của Tuấn.

Ban đầu sĩ diện, ngại mẹ xuất hiện trước bạn bè.

Cuối phim hối hận và muốn đón mẹ về dự sinh nhật.

IMAGE 2 – BÀ NỘI (MẸ TẤN)

Người phụ nữ lớn tuổi, tóc bạc búi sau gáy.

Áo nâu hoa nhỏ, quần đen, dép tối màu.

Dáng người gầy, hơi khom lưng.

Hiền lành, cam chịu, thương con.

IMAGE 3 – TUẤN (CON TRAI TẤN)

Thanh niên trẻ, tóc đen.

Áo sơ mi trắng, quần tây xám.

Lễ phép, hiểu chuyện, thương bà nội.

Tình cờ nhìn thấy bố đối xử với bà.

Là người khiến Tấn nhận ra lỗi lầm và nói CTA cuối phim.

IMAGE 4 – CHÚ HÙNG

Bạn của Tấn, khoảng 50–55 tuổi.

Áo polo xanh ghi, quần tối màu.

Tính cách thân thiện, vui vẻ.

Khách được mời đến dự tiệc sinh nhật.

2. BỐI CẢNH

IMAGE 5 – GÓC NHÀ BÀ NỘI NGỒI MỘT MÌNH

Đây là bối cảnh mở đầu.

Bà nội ngồi một mình ở góc nhà.

Tấn đi đến mang cơm cho mẹ.

Sau khi Tấn nói không cho mẹ đến sinh nhật và rời đi, Tuấn tình cờ đi ngang qua, nhìn thấy sự việc.

Không gian phải có lối đi để Tuấn xuất hiện tự nhiên.

IMAGE 9 – PHÒNG ĂN TỔ CHỨC SINH NHẬT

Bối cảnh diễn ra bữa tiệc sinh nhật của Tấn.

Có bàn tiệc, bánh sinh nhật, ghế ngồi.

Tấn và chú Hùng xuất hiện trước.

Tuấn về nhà, phát đoạn ghi âm và nói chuyện với bố.

Cuối phim Tấn và Tuấn đến đón bà.

3. ĐẠO CỤ

IMAGE 6 – HỘP CƠM, BÁT VÀ ĐŨA

Tấn mang cơm đến cho bà nội.

Xuất hiện trong cảnh mở đầu.

IMAGE 7 – BÀN TIỆC SINH NHẬT

Bánh sinh nhật và các món ăn.

Xuất hiện trong các cảnh tại phòng ăn.

IMAGE 8 – ĐIỆN THOẠI

Điện thoại của Tuấn.

Dùng để phát đoạn ghi âm lời nói của Tấn.

4. BẢNG MÃ ASSET TỔNG HỢP

Nhóm

	

Mã

	

Tên asset




Nhân vật

	

image 1

	

Tấn




Nhân vật

	

image 2

	

Bà nội




Nhân vật

	

image 3

	

Tuấn




Nhân vật

	

image 4

	

Chú Hùng




Bối cảnh

	

image 5

	

Góc nhà bà nội ngồi




Bối cảnh

	

image 9

	

Phòng ăn sinh nhật




Đạo cụ

	

image 6

	

Hộp cơm, bát, đũa




Đạo cụ

	

image 7

	

Bàn tiệc sinh nhật




Đạo cụ

	

image 8

	

Điện thoại

5. Khóa trình tự không gian

Mở đầu – image 5

Bà nội ngồi một mình. Tấn đi đến với image 6.

Tấn rời đi – image 5

Tấn nói lời đuổi mẹ, sau đó rời khỏi vị trí của bà.

Tuấn chứng kiến – image 5

Tuấn đi ngang qua lối đi, nhìn thấy sự việc. Không tự ý cho Tuấn xuất hiện từ một địa điểm khác.

Sinh nhật – image 9

Tấn và chú Hùng ở bàn tiệc. Tuấn về nhà.

Đối diện – image 9

Tuấn sử dụng image 8 phát ghi âm, nói chuyện với bố.

Kết phim – image 9

Tấn và Tuấn đến đón bà, cả ba đoàn tụ. Tuấn nhìn máy quay nói CTA.

Quy định: Không thay đổi mã asset đã chốt. Mỗi prompt video sẽ có IMAGE XUẤT HIỆN, CHỐT KHÔNG GIAN, BẮT ĐẦU PROMPT. Các vị trí nhân vật phải được ghi rõ để tránh nhảy vị trí giữa các cảnh.

Lưu ý: image 5 và image 9 hiện là mã bối cảnh được phân công trong asset board, chưa phải ảnh tham chiếu bối cảnh đã tạo.


#### Lượt 3
làm ra prompt cho tôi đi. nhớ là Mỗi prompt video sẽ có IMAGE XUẤT HIỆN, CHỐT KHÔNG GIAN, BẮT ĐẦU PROMPT. Các vị trí nhân vật phải được ghi rõ để tránh nhảy vị trí giữa các cảnh. sử dụng cảnh cận chủ đạo. có sound effect cinematic

ChatGPT said:

Tôi chia thành 11 prompt video, mỗi prompt 10 giây, theo đúng asset board đã khóa. Cảnh cận sẽ là góc máy chủ đạo; chỉ dùng trung cảnh hoặc toàn cảnh ngắn khi cần xác lập vị trí nhân vật.

Nguyên tắc xuyên suốt:

Không thay đổi khuôn mặt, tóc, vóc dáng, trang phục của các nhân vật trong ảnh tham chiếu.

Không tự ý thêm nhân vật hoặc đạo cụ.

Giữ đúng vị trí nhân vật trong từng prompt, không dịch chuyển đột ngột.

Lời thoại giữ đúng nội dung đã thống nhất.

Âm thanh có cinematic sound effects: tiếng bước chân, tiếng đặt hộp cơm, tiếng cửa, tiếng điện thoại, nhạc nền cảm xúc và các điểm nhấn âm thanh đúng thời điểm. Không để nhạc lấn át lời thoại.

PROMPT 1 – BÀ NỘI NGỒI MỘT MÌNH, TẤN MANG CƠM ĐẾN

IMAGE XUẤT HIỆN

image 1 – Tấn

image 2 – Bà nội

image 5 – Góc nhà bà nội

image 6 – Hộp cơm, bát và đũa

CHỐT KHÔNG GIAN

Bà nội ngồi cố định trên ghế ở góc bên trái khung hình.

Tấn xuất hiện từ lối đi bên phải, tay cầm hộp cơm image 6.

Bà nội nhìn về phía lối đi, không đứng lên.

Tấn dừng trước mặt bà, cách bà khoảng một cánh tay.

Hộp cơm được đặt xuống chiếc bàn nhỏ bên cạnh bà.

BẮT ĐẦU PROMPT (1)

Video 10 giây, phong cách phim hoạt hình 3D điện ảnh chân thực, chuyển động tự nhiên, biểu cảm tinh tế.

Mở đầu bằng góc cận gương mặt bà nội đang ngồi lặng lẽ, ánh mắt buồn và chờ đợi. Máy quay từ từ tiến gần đôi mắt bà, sau đó chuyển sang góc cận bàn tay Tấn đặt hộp cơm xuống bàn nhỏ. Cắt sang cận mặt Tấn với vẻ lạnh nhạt, không quan tâm đến cảm xúc của mẹ. Bà nội ngước nhìn con trai.

Lời thoại image 1 – Tấn:
“Mẹ, cơm con mang sang cho mẹ đây. Ăn xong nhớ tự rửa bát nhé.”

Âm thanh: Tiếng bước chân nhẹ, tiếng hộp cơm chạm mặt bàn, tiếng bát đũa khẽ va nhau. Nhạc nền piano trầm, hơi lạnh, tạo cảm giác cô đơn. Nhấn cinematic bass nhẹ khi Tấn đặt hộp cơm xuống.

PROMPT 2 – TẤN ĐUỔI MẸ, KHÔNG CHO ĐẾN SINH NHẬT

IMAGE XUẤT HIỆN

image 1 – Tấn

image 2 – Bà nội

image 5 – Góc nhà bà nội

image 6 – Hộp cơm, bát và đũa

CHỐT KHÔNG GIAN

Bà nội vẫn ngồi trên ghế bên trái khung hình.

Hộp cơm nằm trên bàn nhỏ bên cạnh bà.

Tấn đứng trước mặt bà, phía bên phải khung hình.

Trong suốt cảnh, bà không rời khỏi ghế.

Cuối cảnh, Tấn quay người đi về lối bên phải, bà vẫn ngồi một mình.

BẮT ĐẦU PROMPT (2)

Video 10 giây. Sử dụng cảnh cận chủ đạo để nhấn mạnh sự đối lập cảm xúc giữa hai nhân vật.

Máy quay cận mặt Tấn. Anh ta nhìn mẹ bằng ánh mắt khó chịu, nói với thái độ dứt khoát, lạnh lùng. Cắt sang cận mặt bà nội, ánh mắt ngỡ ngàng, buồn bã, đôi môi khẽ run nhưng không phản bác. Quay lại cận mặt Tấn khi anh nói hết câu. Sau đó Tấn quay lưng rời đi, máy quay giữ lại gương mặt bà nội thật lâu.

Lời thoại image 1 – Tấn:
“Hôm nay mẹ tuyệt đối đừng sang nhà con. Nhà có bạn bè đến chơi, tránh để mọi người nhìn thấy mẹ rồi mất cả hứng ăn uống.”

Âm thanh: Nhạc nền trầm xuống khi Tấn nói câu “đừng sang nhà con”. Tiếng bước chân Tấn rời đi vang nhẹ. Một tiếng cinematic impact trầm rất nhỏ ở khoảnh khắc bà nội cúi mặt. Không dùng hiệu ứng âm thanh quá kịch.

PROMPT 3 – TUẤN TÌNH CỜ NHÌN THẤY

IMAGE XUẤT HIỆN

image 1 – Tấn

image 2 – Bà nội

image 3 – Tuấn

image 5 – Góc nhà bà nội

image 6 – Hộp cơm, bát và đũa

CHỐT KHÔNG GIAN

Bà nội vẫn ngồi trên ghế bên trái, hộp cơm nằm trên bàn nhỏ bên cạnh.

Tấn đang đi ra lối bên phải, quay lưng về phía bà.

Tuấn xuất hiện từ lối đi phía sau Tấn, ở khoảng cách vài mét.

Tuấn dừng lại ở lối đi, không bước vào giữa Tấn và bà.

Tấn tiếp tục đi khỏi khung hình. Tuấn vẫn đứng nhìn bà nội.

BẮT ĐẦU PROMPT (3)

Video 10 giây. Dùng ngôn ngữ điện ảnh, tập trung vào ánh mắt và phản ứng cảm xúc.

Mở đầu bằng góc cận gương mặt Tấn khi anh quay lưng bỏ đi. Máy quay chuyển nét ra phía sau, phát hiện Tuấn vừa đi ngang qua và chứng kiến toàn bộ sự việc. Cận cảnh đôi mắt Tuấn mở lớn, vẻ mặt sững sờ và thất vọng khi nhận ra bố vừa đối xử với bà như thế nào. Tuấn nhìn theo bóng lưng Tấn, sau đó quay ánh mắt về phía bà nội. Cắt sang cận mặt bà nội đang cúi đầu, cố kìm nén nỗi buồn.

Tuấn không nói gì, chỉ đứng lặng vài giây. Kết thúc bằng cận gương mặt Tuấn, ánh mắt bắt đầu trở nên kiên quyết.

Âm thanh: Tiếng bước chân Tấn xa dần, âm thanh môi trường giảm nhẹ. Nhạc nền piano chuyển sang giai điệu buồn, thêm tiếng cinematic low boom nhẹ khi Tuấn nhận ra sự việc. Không thêm lời thoại.

PROMPT 4 – TẤN GỌI ĐIỆN CHO TUẤN

IMAGE XUẤT HIỆN

image 1 – Tấn

image 8 – Điện thoại

image 9 – Phòng ăn sinh nhật

image 7 – Bàn tiệc sinh nhật

CHỐT KHÔNG GIAN

Tấn đứng cạnh bàn tiệc, ở phía bên phải bàn.

Điện thoại image 8 nằm trong tay Tấn.

Bàn tiệc image 7 ở phía trước Tấn.

Tuấn chưa xuất hiện trực tiếp trong khung hình.

Tấn giữ nguyên vị trí trong suốt cuộc gọi.

BẮT ĐẦU PROMPT (4)

Video 10 giây. Bối cảnh phòng ăn đã được chuẩn bị cho tiệc sinh nhật. Mở đầu bằng một góc cận bánh sinh nhật và các món ăn trên bàn. Máy quay chuyển sang cận tay Tấn cầm điện thoại, sau đó cận gương mặt anh khi gọi điện. Biểu cảm Tấn vui vẻ, háo hức chờ con trai về.

Lời thoại image 1 – Tấn:
“Alo, Tuấn à? Hôm nay là sinh nhật bố, con có về ăn cơm không?”

Giọng image 3 – Tuấn qua điện thoại:
“Con sắp tới rồi bố. Con còn chuẩn bị cho bố một bất ngờ nữa.”

Tấn mỉm cười nhẹ, tỏ vẻ tò mò và mong chờ.

Âm thanh: Tiếng chuông kết nối điện thoại, tiếng môi trường trong nhà nhẹ nhàng. Nhạc nền có sắc thái vui vẻ nhưng vẫn giữ chút bí ẩn. Thêm hiệu ứng cinematic chime nhỏ khi nghe đến câu “một bất ngờ nữa”.

PROMPT 5 – TUẤN VỀ ĐẾN NHÀ

IMAGE XUẤT HIỆN

image 1 – Tấn

image 3 – Tuấn

image 9 – Phòng ăn sinh nhật

image 7 – Bàn tiệc sinh nhật

CHỐT KHÔNG GIAN

Tấn đứng bên phải bàn tiệc, hướng mặt về phía cửa ra vào.

Tuấn đi từ cửa vào, dừng cách Tấn khoảng 2 mét.

Bàn tiệc nằm giữa hai người nhưng không chắn đường nhìn.

Hai người giữ vị trí đối diện nhau, không đổi chỗ.

BẮT ĐẦU PROMPT (5)

Video 10 giây. Mở đầu bằng góc trung cảnh ngắn cho thấy Tuấn vừa bước vào phòng ăn. Chuyển ngay sang cận gương mặt Tấn vui vẻ khi nhìn thấy con trai. Cắt sang cận Tuấn với nụ cười nhẹ, bình tĩnh nhưng ánh mắt có chủ ý. Máy quay luân phiên cận hai gương mặt khi đối thoại.

Lời thoại image 1 – Tấn:
“Tuấn về rồi à? Mau ngồi vào ăn đi con! Hôm nay con bảo có bất ngờ gì cho bố?”

Tuấn nhìn bố, giữ thái độ bình tĩnh.

Âm thanh: Tiếng bước chân Tuấn trên nền nhà, tiếng cửa khép nhẹ. Nhạc nền chuyển sang trạng thái hồi hộp kín đáo. Không thêm lời thoại ngoài kịch bản.

PROMPT 6 – TUẤN NHỜ CHÚ HÙNG TRÁNH MẶT

IMAGE XUẤT HIỆN

image 1 – Tấn

image 3 – Tuấn

image 4 – Chú Hùng

image 9 – Phòng ăn sinh nhật

image 7 – Bàn tiệc sinh nhật

CHỐT KHÔNG GIAN

Tấn đứng bên phải bàn tiệc.

Tuấn đứng đối diện Tấn, ở phía gần cửa ra vào.

Chú Hùng ngồi ở ghế phía bên trái bàn tiệc.

Khi Tuấn nói với chú Hùng, Tuấn chỉ quay đầu và hướng ánh mắt về chú Hùng, không đổi vị trí.

Chú Hùng đứng lên và đi ra khỏi khu vực bàn tiệc.

Tấn vẫn đứng nguyên vị trí bên phải bàn.

BẮT ĐẦU PROMPT (6)

Video 10 giây. Máy quay cận gương mặt Tuấn, ánh mắt nghiêm túc nhưng vẫn lễ phép. Tuấn quay nhẹ về phía chú Hùng, nói nhỏ vừa đủ nghe. Cắt sang cận mặt chú Hùng hơi ngạc nhiên, sau đó gật đầu. Chú Hùng đứng lên rời khỏi bàn tiệc. Máy quay trở lại cận mặt Tuấn khi cậu quay sang bố.

Lời thoại image 3 – Tuấn:
“Chú Hùng, phiền chú tránh mặt một lát. Cháu cần xử lý chút việc nhà.”

Tuấn quay sang Tấn.

Lời thoại image 3 – Tuấn:
“Bố đợi một chút, con sẽ cho bố xem bất ngờ ngay đây.”

Âm thanh: Tiếng ghế kéo nhẹ, tiếng bước chân chú Hùng rời đi. Nhạc nền suspense tăng dần, thêm tiếng cinematic tension riser ngắn khi Tuấn quay sang bố.

PROMPT 7 – TUẤN PHÁT ĐOẠN GHI ÂM

IMAGE XUẤT HIỆN

image 1 – Tấn

image 3 – Tuấn

image 8 – Điện thoại

image 9 – Phòng ăn sinh nhật

image 7 – Bàn tiệc sinh nhật

CHỐT KHÔNG GIAN

Tấn đứng bên phải bàn tiệc.

Tuấn đứng đối diện Tấn, phía gần cửa.

Chú Hùng đã rời khỏi khu vực bàn tiệc, không xuất hiện.

Tuấn cầm điện thoại image 8 trước ngực, hướng màn hình về phía Tấn.

Tấn nhìn về phía điện thoại, không di chuyển khỏi vị trí.

BẮT ĐẦU PROMPT (7)

Video 10 giây. Mở đầu bằng cận cảnh bàn tay Tuấn cầm điện thoại, ngón tay chạm vào nút phát ghi âm. Cận màn hình điện thoại trong khoảnh khắc phát lại. Âm thanh ghi âm vang lên rõ ràng, có chất âm điện thoại tự nhiên.

Giọng ghi âm image 1 – Tấn:
“Hôm nay là sinh nhật con, nhà có bạn bè đến chơi, tránh để mọi người nhìn thấy mẹ rồi đến lúc đó lại mất cả hứng ăn uống…”

Cắt sang cận mặt Tấn. Nụ cười trên mặt anh biến mất, đôi mắt mở lớn, gương mặt cứng lại vì nhận ra chính lời nói của mình. Cận mặt Tuấn nhìn bố, không nói gì. Máy quay giữ lại phản ứng bàng hoàng của Tấn.

Âm thanh: Tiếng chạm màn hình điện thoại, tiếng ghi âm phát ra từ loa điện thoại. Khi Tấn nhận ra giọng nói của mình, nhạc nền đột ngột giảm xuống, thêm một tiếng cinematic bass impact sâu và ngắn. Không thêm tiếng động gây mất tập trung.

PROMPT 8 – TUẤN NHẮC ĐẾN NGÀY SINH CỦA BỐ

IMAGE XUẤT HIỆN

image 1 – Tấn

image 3 – Tuấn

image 9 – Phòng ăn sinh nhật

image 7 – Bàn tiệc sinh nhật

image 8 – Điện thoại

CHỐT KHÔNG GIAN

Tấn đứng bên phải bàn tiệc.

Tuấn đứng đối diện Tấn, phía gần cửa.

Điện thoại vẫn nằm trong tay Tuấn.

Hai người giữ nguyên vị trí đối diện nhau.

Không có nhân vật khác xuất hiện.

BẮT ĐẦU PROMPT (8)

Video 10 giây. Cảnh cận chủ đạo. Tuấn nhìn thẳng vào bố, ánh mắt vừa đau lòng vừa trách móc. Máy quay tiến chậm vào gương mặt Tuấn khi cậu nói. Cắt sang cận mặt Tấn, ánh mắt bắt đầu dao động, không dám nhìn thẳng con trai.

Lời thoại image 3 – Tuấn:
“Chúc mừng sinh nhật bố! Hôm nay bố tròn năm mươi hai tuổi. Đúng ngày này năm mươi hai năm trước, bà nội đã đau đớn tận cùng để sinh ra bố.”

Ở câu “sinh ra bố”, máy quay cắt cận gương mặt Tấn, ánh mắt chùng xuống. Tuấn vẫn đứng đối diện, không tiến lại gần.

Âm thanh: Nhạc piano cảm xúc chậm, trầm. Có tiếng bass cinematic nhẹ ở cụm từ “sinh ra bố”. Giữ khoảng lặng ngắn sau câu thoại để cảm xúc lắng xuống.

PROMPT 9 – TUẤN HỎI BỐ CÓ ĐAU LÒNG KHÔNG

IMAGE XUẤT HIỆN

image 1 – Tấn

image 3 – Tuấn

image 9 – Phòng ăn sinh nhật

image 7 – Bàn tiệc sinh nhật

CHỐT KHÔNG GIAN

Tấn đứng bên phải bàn tiệc, đầu hơi cúi.

Tuấn đứng đối diện Tấn, phía gần cửa.

Khoảng cách giữa hai người giữ nguyên.

Tuấn không tiến sát hoặc chạm vào bố.

Bàn tiệc vẫn ở vị trí giữa không gian, không thay đổi.

BẮT ĐẦU PROMPT (9)

Video 10 giây. Dùng cận mặt Tuấn làm góc máy chính. Tuấn nói với giọng nghẹn nhẹ nhưng rõ ràng, không la hét. Cắt sang cận mắt Tấn, ánh mắt đỏ lên, gương mặt thể hiện sự xấu hổ và day dứt.

Lời thoại image 3 – Tuấn:
“Ngày bố chào đời, bà chỉ mong bố sống, mong bố khỏe mạnh. Vậy mà hôm nay bố lại bảo bà đừng xuất hiện trong ngày sinh nhật của bố!”

Tuấn ngừng một nhịp rồi tiếp tục:

“Con không trách bố tổ chức sinh nhật, nhưng tại sao trong bữa cơm mừng ngày bố ra đời lại không có chỗ cho người đã sinh ra bố? Nếu sau này con cũng bảo bố đừng đến nhà vì con có khách, bố có đau lòng không?”

Khi Tuấn nói đến câu hỏi cuối, máy quay cận gương mặt Tấn. Anh cúi đầu, không trả lời, vẻ mặt đau đớn và hối hận.

Âm thanh: Nhạc nền dây violin hòa cùng piano, tăng dần cảm xúc. Nhấn cinematic impact nhẹ ở câu “người đã sinh ra bố”. Sau câu hỏi cuối, để một khoảng lặng ngắn, chỉ còn tiếng thở của Tấn.

PROMPT 10 – TẤN HỐI HẬN, MUỐN ĐÓN MẸ

IMAGE XUẤT HIỆN

image 1 – Tấn

image 2 – Bà nội

image 3 – Tuấn

image 5 – Góc nhà bà nội

image 9 – Phòng ăn sinh nhật

CHỐT KHÔNG GIAN

Đầu cảnh: Tấn đứng bên phải bàn tiệc trong image 9, Tuấn đứng đối diện ở phía gần cửa.

Cuối cảnh chuyển sang image 5: bà nội vẫn ngồi trên ghế ở góc bên trái.

Tấn và Tuấn xuất hiện từ lối đi bên phải, cùng tiến đến trước mặt bà.

Tấn đứng gần bà nhất, Tuấn đứng chếch phía sau Tấn.

Bà nội vẫn ngồi cho đến khi Tấn đưa tay đỡ bà.

Không để nhân vật xuất hiện đột ngột hoặc đổi vị trí trong cùng một cú máy.

BẮT ĐẦU PROMPT (10)

Video 10 giây. Mở đầu bằng cận gương mặt Tấn đang cúi đầu, đôi mắt đỏ và vẻ mặt ân hận. Máy quay từ từ tiến gần. Tấn ngẩng lên nhìn Tuấn, giọng nói nghẹn lại.

Lời thoại image 1 – Tấn:
“Bố sai rồi… Bố không nên đối xử với bà như vậy. Tuấn, bây giờ bố con mình đi đón bà nhé. Cơm vẫn còn nóng, bố muốn bà cùng ăn sinh nhật với bố.”

Sau câu thoại, chuyển cảnh điện ảnh từ image 9 sang image 5. Tấn và Tuấn cùng đi từ lối bên phải đến chỗ bà nội. Cận cảnh bàn tay Tấn nhẹ nhàng đưa ra đỡ mẹ. Bà nội ngước lên nhìn con trai, ngạc nhiên và xúc động. Cận mặt Tấn với ánh mắt chân thành, hối lỗi. Tuấn đứng phía sau, nhẹ nhàng nhìn bà và mỉm cười.

Âm thanh: Nhạc piano chuyển từ trầm buồn sang ấm áp, có lớp violin nhẹ nâng cảm xúc. Tiếng bước chân chậm, tiếng quần áo chuyển động nhẹ. Thêm cinematic emotional swell khi Tấn đưa tay đỡ mẹ. Không dùng hiệu ứng quá bi lụy.

PROMPT 11 – CTA: LỜI NHẮN GỬI ĐẾN NHỮNG NGƯỜI CON

IMAGE XUẤT HIỆN

image 1 – Tấn

image 2 – Bà nội

image 3 – Tuấn

image 5 – Góc nhà bà nội

CHỐT KHÔNG GIAN

Bà nội đứng ở giữa khung hình, hơi nghiêng về phía Tấn.

Tấn đứng bên trái bà, một tay nhẹ nhàng đỡ mẹ.

Tuấn đứng bên phải bà.

Cả ba đứng gần nhau, tạo thành một nhóm gia đình.

Khi bắt đầu CTA, Tấn và bà nội vẫn đứng nguyên vị trí, Tuấn chỉ xoay người và hướng ánh mắt về phía máy quay.

Không để Tuấn bước ra khỏi nhóm gia đình.

BẮT ĐẦU PROMPT (11)

Video 10 giây. Phong cách phim hoạt hình 3D điện ảnh, kết thúc ấm áp và giàu cảm xúc.

Mở đầu bằng trung cảnh ngắn cho thấy cả ba người đang ở bên nhau. Cắt sang cận mặt bà nội, ánh mắt xúc động, khóe miệng khẽ mỉm cười. Cận mặt Tấn đang nhìn mẹ với vẻ ân hận nhưng nhẹ nhõm. Sau đó máy quay chuyển sang cận Tuấn.

Tuấn từ từ quay mặt nhìn thẳng vào ống kính, giữ ánh mắt chân thành, nói trực tiếp với khán giả. Giọng nói ấm áp, truyền cảm, tự nhiên, không đọc như quảng cáo.

Lời thoại image 3 – Tuấn (CTA):

“Các bạn ơi, ơn sinh thành lớn hơn biển cả, cả một đời con trả chẳng đầy. Nếu yêu mẹ, hãy thả một trái tim và để lại một câu bạn muốn nói với mẹ dưới phần bình luận nhé!”

Trong lúc Tuấn nói, Tấn nhẹ nhàng nắm tay bà nội. Bà nội đứng cạnh con trai, gương mặt dịu lại. Kết thúc bằng góc máy rộng hơn một chút, cả ba người cùng ở trong khung hình. Giữ hình ảnh gia đình đoàn tụ khoảng một nhịp trước khi kết thúc.

Âm thanh: Nhạc piano và violin ấm áp, cinematic emotional climax nhẹ ở câu “ơn sinh thành lớn hơn biển cả”. Khi Tuấn nói “thả một trái tim”, thêm hiệu ứng âm thanh trái tim nhẹ nhàng, tinh tế. Kết phim bằng một tiếng cinematic chime ngân nhẹ, nhạc fade out tự nhiên.

Lưu ý dựng tổng thể: 11 prompt × 10 giây = 110 giây. Cảnh 1–3 ưu tiên cảm giác cô đơn và tổn thương; cảnh 4–6 tạo không khí sinh nhật nhưng gieo sự hồi hộp; cảnh 7–9 là cao trào đối diện; cảnh 10–11 chuyển sang hối lỗi, đoàn tụ và CTA. Giữ lời thoại rõ, không tự thêm lời thoại hoặc để các nhân vật nói chồng lên nhau.


### Cuộc trò chuyện: Phân tích kịch bản gia đình


#### Lượt 1
tạo hình khu vực bàn ăn
Edit
ChatGPT said:


#### Lượt 2
làm lại các prompt phải có chốt không gian. dưới chốt không gian là bắt đầu prompt ( số thứ tự ) đừng để thay đổi vị trí nhân vật. nhân vật cuối prompt trước đang ở đâu thì đầu prompt này sẽ ở đó
Đã xử lý trong 7s
ChatGPT said:

Đúng rồi. Tôi sẽ chuẩn hóa lại toàn bộ prompt theo quy tắc khóa không gian và khóa vị trí nhân vật xuyên suốt các prompt. Không được tự ý đổi vị trí, hướng nhìn, hướng di chuyển hoặc trạng thái nhân vật khi chuyển prompt.

QUY CHUẨN PROMPT ÁP DỤNG

1. CHỐT KHÔNG GIAN

Ghi cố định sơ đồ bối cảnh trước prompt đầu tiên, gồm:

Vị trí tương đối của BG-1 (gian bếp), BG-2 (khu vực bàn ăn).

Vị trí từng nhân vật, bàn ăn, đảo bếp, cửa ra vào và đạo cụ.

Hướng nhìn, hướng di chuyển và trục máy quay.

Vị trí cuối cùng của từng nhân vật ở prompt trước phải là vị trí bắt đầu của prompt tiếp theo.

2. BẮT ĐẦU PROMPT (số thứ tự)

Mỗi prompt phải có cấu trúc thống nhất như sau:

IMAGE XUẤT HIỆN: Chỉ liệt kê những image thực sự xuất hiện trong cảnh.

BẮT ĐẦU PROMPT (số): Viết đầy đủ nội dung tạo video ngay bên dưới.

Không gian và vị trí: Nhắc lại các vị trí cần thiết để giữ liên tục.

Diễn biến: Mô tả hành động theo thứ tự thời gian, ưu tiên cảnh cận mặt, ánh mắt, bàn tay và đạo cụ.

Thoại: Ghi đúng người nói, đúng câu thoại; không tráo đổi nhân vật.

Trạng thái kết thúc: Xác định chính xác vị trí, tư thế, hướng nhìn và đạo cụ của từng nhân vật ở cuối prompt.

CHỐT KHÔNG GIAN – CẢNH 100 NGHÌN NẤU LẨU CÁ MÚ, TÔM HÙM

Quy ước image dùng xuyên suốt:

image 1: CH-1.

image 2: CH-2.

image 3: BG-1 – gian bếp bình dân.

image 4: BG-2 – khu vực bàn ăn.

image 5: PR-1 – tờ tiền 100.000 đồng.

image 6: PR-2 – khăn lau bàn.

image 7: PR-3 – điện thoại.

image 8: PR-4 – túi xách.

Sơ đồ vị trí cố định

BG-1: Nằm bên trái BG-2, có đảo bếp và mặt bàn đá.

BG-2: Nằm bên phải BG-1, có bàn ăn và ghế.

image 1: Đứng phía đối diện image 2 tại khu vực đảo bếp khi bắt đầu câu chuyện.

image 2: Đứng sát đảo bếp, đối diện image 1.

image 5: Được đặt trên mặt đảo bếp, sau đó được image 2 cầm sang BG-2 và đặt lên bàn ăn.

image 6: Ban đầu nằm trong tay image 2 khi lau bàn.

image 7 và image 8: Chỉ xuất hiện khi câu chuyện đến đoạn image 2 quyết định quay lại làm việc.

Không được tự ý đảo trái-phải giữa hai nhân vật. Khi image 2 di chuyển từ BG-1 sang BG-2, image 1 vẫn ở vị trí cũ cho đến khi có hành động mới trong kịch bản.

Từ đây, mỗi prompt sẽ được viết theo nguyên tắc nối trạng thái cuối cảnh trước sang trạng thái đầu cảnh sau, không dựng lại vị trí nhân vật một cách tùy tiện. Cảnh cận là chủ đạo, nhưng vẫn giữ đúng hướng nhìn, hướng di chuyển và quan hệ không gian để khi ghép các clip lại, phim không bị nhảy vị trí.


#### Lượt 3
rồi làm ra 5 prompt đi. cái phần chốt không gian phải nằm trong prompt luôn. nhân vật đứng vị trí nào cũng trong các prompt luôn. không cần miêu ta nhân vật đạo cụ bối cảnh là gì vì tất cả đã có trong tham chiếu
ChatGPT said:
PROMPT 1 – ĐƯA 100 NGHÌN, ĐÒI LẨU CÁ MÚ VÀ TÔM HÙM

IMAGE XUẤT HIỆN: image 1, image 2, image 3, image 5, image 6.

BẮT ĐẦU PROMPT (1)

Tạo video phim ngắn chân thực, phong cách drama gia đình, ưu tiên cảnh cận mặt và cận chi tiết, diễn xuất tự nhiên, nhịp phim căng thẳng.

CHỐT KHÔNG GIAN VÀ VỊ TRÍ: Toàn bộ cảnh diễn ra tại image 3. image 2 đứng sát cạnh đảo bếp, dùng image 6 lau mặt bàn. image 1 đứng đối diện image 2 ở phía bên kia đảo bếp. image 5 nằm trên mặt đảo bếp giữa hai nhân vật, gần phía image 1 hơn. Giữ nguyên vị trí trái-phải, khoảng cách và hướng đối diện của hai nhân vật trong toàn bộ prompt. Không tự ý đổi vị trí hoặc cho nhân vật xuất hiện ở khu vực khác.

DIỄN BIẾN: Mở đầu bằng cận cảnh bàn tay image 2 đang lau mặt bàn bằng image 6. image 1 đưa tay đặt image 5 xuống mặt bàn, đẩy nhẹ về phía image 2. Cắt sang cận mặt image 1, vẻ mặt thản nhiên, giọng ra lệnh.

image 1 nói: “Cầm trăm nghìn đi chợ. Tối nay nấu lẩu cá mú, thêm con tôm hùm hấp nhé!”

Cắt sang cận mặt image 2. image 2 dừng tay, nhìn image 5 rồi ngẩng lên nhìn image 1 với vẻ không tin nổi.

image 2 nói: “Anh nói bao nhiêu?”

Cắt cận mặt image 1.

image 1 nói: “Một trăm nghìn! Tai cô có vấn đề à?”

Kết thúc bằng cận mặt image 2, ánh mắt sững sờ chuyển dần sang thất vọng và lạnh lùng. image 2 vẫn đứng sát đảo bếp, image 1 vẫn đứng đối diện, image 5 giữ nguyên trên mặt bàn, image 6 vẫn trong tay image 2.

Không thêm nhân vật, không đổi trang phục, không thay đổi khuôn mặt, không tự tạo lời thoại mới, không để nhân vật nói nhầm lời. Không chèn phụ đề hoặc chữ trên màn hình.

PROMPT 2 – CÂU NÓI XÚC PHẠM

IMAGE XUẤT HIỆN: image 1, image 2, image 3, image 5, image 6.

BẮT ĐẦU PROMPT (2)

Tạo video nối tiếp trực tiếp trạng thái cuối prompt trước. Giữ phong cách phim drama gia đình chân thực, ưu tiên cận mặt, cận ánh mắt và bàn tay. Nhịp dựng nhanh hơn, tạo cảm giác mâu thuẫn tăng cao.

CHỐT KHÔNG GIAN VÀ VỊ TRÍ: Cảnh tiếp tục tại image 3. image 2 vẫn đứng sát đảo bếp ở đúng vị trí cuối prompt 1, đối diện image 1; image 2 đang cầm image 6. image 1 vẫn đứng ở phía đối diện, gần image 5 hơn. image 5 vẫn nằm trên mặt đảo bếp, không di chuyển. Không đảo vị trí hai nhân vật, không cắt sang góc máy khiến quan hệ trái-phải bị đảo ngược.

DIỄN BIẾN: Cận mặt image 1. image 1 khoanh tay, nhếch mép khinh thường.

image 1 nói: “Cô ở nhà ăn bám tôi, có mỗi bữa cơm cũng không làm cho ra hồn!”

Cắt sang cận bàn tay image 2 siết chặt image 6. Cắt lên cận mặt image 2, cố kiềm chế tức giận.

image 2 nói: “Anh nghĩ tiền anh đưa đủ mua những thứ anh vừa nói sao?”

Cắt cận mặt image 1, ánh mắt trở nên gay gắt.

image 1 nói: “Tôi kiếm ra tiền! Tôi bảo cô làm gì thì cô làm cái đó!”

Cận mặt image 2. image 2 nhìn thẳng image 1, giọng mỉa mai nhưng kiềm chế.

image 2 nói: “Vậy anh thử sống bằng một trăm nghìn, rồi xem ai mới là người không biết tính toán.”

image 1 lập tức sa sầm mặt, hơi nghiêng người về phía trước và quát lớn.

image 1 nói: “Cô vừa nói cái gì?!”

Kết thúc bằng cận cảnh image 1 đập bàn tay xuống đảo bếp gần image 5. image 5 rung nhẹ nhưng vẫn nằm trên mặt bàn. image 2 vẫn đứng tại chỗ, tay giữ image 6, không lùi lại.

Không thêm hành động đánh người, không để nhân vật đổi chỗ, không thay đổi đạo cụ, không tráo lời thoại, không thêm nhân vật hoặc phụ đề.

PROMPT 3 – TRẢ LẠI TIỀN

IMAGE XUẤT HIỆN: image 1, image 2, image 3, image 4, image 5, image 6.

BẮT ĐẦU PROMPT (3)

Tạo video nối tiếp chính xác từ cuối prompt 2. Phong cách drama gia đình chân thực, biểu cảm tiết chế nhưng căng thẳng. Ưu tiên cận cảnh bàn tay, tờ tiền và gương mặt nhân vật.

CHỐT KHÔNG GIAN VÀ VỊ TRÍ: Đầu cảnh, image 1 vẫn đứng ở phía đối diện đảo bếp và vừa đập tay xuống mặt bàn. image 2 vẫn đứng sát đảo bếp, đối diện image 1, đang cầm image 6. image 5 nằm trên đảo bếp gần image 1. image 4 là khu vực bàn ăn nằm bên phải image 3. image 2 là người duy nhất di chuyển trong phần đầu cảnh: từ vị trí sát đảo bếp, image 2 nhấc image 5, đi theo hướng từ image 3 sang image 4 rồi dừng cạnh bàn ăn. image 1 giữ nguyên vị trí tại image 3, không đi theo. Không đảo hướng di chuyển hoặc tự ý đổi sơ đồ không gian.

DIỄN BIẾN: Cận mặt image 2. image 2 nhìn image 1 vài giây, sau đó đặt image 6 xuống mặt đảo bếp, cầm image 5 lên.

Cận bàn tay image 2 giữ chặt image 5. Máy quay theo chuyển động của image 2 khi đi từ image 3 sang image 4. Không quay toàn cảnh kéo dài; sử dụng góc máy bám theo tay và chuyển sang cận mặt.

image 2 dừng bên cạnh bàn ăn tại image 4, đặt image 5 xuống mặt bàn kính.

image 2 nói: “Tiền của anh, anh cầm lại.”

Cắt sang cận mặt image 1 đang đứng tại image 3, nhìn về phía image 2.

image 1 nói: “Cô giở trò gì đấy?”

Cận mặt image 2, ánh mắt kiên quyết.

image 2 nói: “Muốn ăn lẩu cá mú, muốn ăn tôm hùm hấp, anh tự đi mua. Một trăm nghìn, anh tự tính xem mua được những gì.”

image 1 tức giận, quát vọng từ vị trí cạnh đảo bếp.

image 1 nói: “Cô dám chống đối tôi?!”

image 2 không rời khỏi vị trí cạnh bàn ăn. image 2 nhìn thẳng về phía image 1.

image 2 nói: “Tôi không chống đối anh. Tôi chỉ không chấp nhận để anh coi thường mình nữa.”

Kết thúc: image 2 đứng cạnh bàn ăn tại image 4; image 5 nằm trên bàn kính trước mặt image 2. image 1 vẫn đứng cạnh đảo bếp tại image 3. Hai người nhìn về phía nhau qua khoảng không giữa khu bếp và bàn ăn.

Không để image 1 xuất hiện đột ngột cạnh bàn ăn, không để image 2 quay ngược trở lại đảo bếp, không tự ý di chuyển image 5 sau khi đặt xuống. Không thêm lời thoại hoặc phụ đề.

PROMPT 4 – TUYÊN BỐ ĐI LÀM LẠI

IMAGE XUẤT HIỆN: image 1, image 2, image 4, image 5, image 7, image 8.

BẮT ĐẦU PROMPT (4)

Tạo video nối tiếp trực tiếp cuối prompt 3. Tông phim căng thẳng, diễn xuất chân thực, ưu tiên cận mặt và chi tiết bàn tay. Không thay đổi vị trí nhân vật ở đầu cảnh.

CHỐT KHÔNG GIAN VÀ VỊ TRÍ: Đầu cảnh, image 2 vẫn đứng cạnh bàn ăn tại image 4, image 5 nằm trên bàn ngay trước mặt image 2. image 1 vẫn đứng tại khu vực đảo bếp thuộc image 3, ở phía đối diện và nhìn về phía image 2. image 2 không di chuyển khỏi bàn ăn cho đến khi cầm image 8 và bắt đầu bước đi ở cuối cảnh. image 1 giữ nguyên vị trí suốt cảnh. image 7 và image 8 chỉ xuất hiện khi image 2 chủ động lấy chúng. Không đảo vị trí, không cho image 1 tiến đến bàn ăn, không tự ý thêm lối đi hoặc thay đổi cấu trúc căn nhà.

DIỄN BIẾN: Cận mặt image 1, vẻ giận dữ và đe dọa.

image 1 nói: “Cô bước chân ra khỏi cửa thì đừng có quay về cầu xin tôi!”

Cận mặt image 2. image 2 nhìn image 1 vài giây, sau đó lấy image 7 ra và thực hiện cuộc gọi. Cận tay thao tác trên điện thoại, rồi chuyển sang cận mặt image 2 trong lúc nói.

image 2 nói vào điện thoại: “Alo, em đây. Ngày mai em có thể quay lại làm việc được không?”

image 2 dừng nghe, ánh mắt dần kiên quyết hơn. Kết thúc cuộc gọi, image 2 hạ image 7 xuống.

Cắt sang cận mặt image 1, ngạc nhiên và tức tối.

image 1 nói: “Cô gọi cho ai đấy?”

image 2 vẫn đứng cạnh bàn ăn, nhìn về phía image 1.

image 2 nói: “Gọi cho chỗ làm cũ. Mai tôi đi làm lại.”

image 1 lớn tiếng từ vị trí cũ.

image 1 nói: “Cô định bỏ mặc nhà cửa, bỏ mặc chồng à?”

image 2 cầm image 8 lên, giữ bình tĩnh, nhìn thẳng về phía image 1.

image 2 nói: “Tôi không bỏ mặc gia đình. Tôi chỉ không muốn đánh mất chính mình trong gia đình này.”

image 2 quay người và bắt đầu bước đi khỏi bàn ăn, mang theo image 7 và image 8. image 5 vẫn nằm trên bàn kính. image 1 đứng nguyên tại khu vực đảo bếp, không đuổi theo.

Kết thúc bằng cận mặt image 1 sững sờ, sau đó cắt sang image 2 đang bước đi. Giữ chính xác hướng di chuyển đã thiết lập, không cho image 2 biến mất đột ngột.

Không thêm người, không tự ý đổi vị trí đạo cụ, không tráo lời thoại, không thêm phụ đề hoặc chữ trên màn hình.

PROMPT 5 – CTA KẾT PHIM

IMAGE XUẤT HIỆN: image 1, image 2, image 4, image 5, image 7, image 8.

BẮT ĐẦU PROMPT (5)

Tạo video kết thúc nối tiếp trực tiếp cuối prompt 4. Phong cách phim drama gia đình, kết mở, ưu tiên cận mặt và tạo cảm giác khán giả đang theo dõi một câu chuyện có thật.

CHỐT KHÔNG GIAN VÀ VỊ TRÍ: Đầu cảnh, image 2 đang bước đi khỏi khu vực bàn ăn tại image 4, mang theo image 7 và image 8. image 1 vẫn đứng ở khu vực đảo bếp, nhìn theo image 2. image 5 vẫn nằm nguyên trên bàn kính tại image 4. image 2 dừng lại ở lối đi gần bàn ăn, quay đầu nhìn về phía image 1. Không đưa image 2 trở lại vị trí cũ cạnh bàn ăn; không di chuyển image 1 khỏi đảo bếp. Khi image 2 quay sang ống kính, image 2 vẫn đứng tại vị trí dừng đó.

DIỄN BIẾN: Cận cảnh image 2 đang bước đi, image 7 và image 8 nằm trong tay. image 2 dừng bước, từ từ quay đầu lại. Máy quay tiến gần gương mặt image 2. Ánh mắt cô bình tĩnh, có chút tổn thương nhưng kiên quyết.

image 2 nhìn trực tiếp vào ống kính, nói rõ ràng, tự nhiên, như đang hỏi khán giả.

image 2 nói: “Nếu là bạn, bạn sẽ tiếp tục nhẫn nhịn hay đứng lên để giành lại sự tôn trọng? Bình luận cho tôi biết nhé! Nhớ theo dõi kênh để xem ngày mai chồng tôi sẽ phải đối mặt với chuyện gì!”

Sau câu cuối, image 2 giữ ánh mắt nhìn vào ống kính khoảng một giây. Cắt sang cận mặt image 1 đang đứng chết lặng ở phía xa, rồi cắt đen ngay lập tức để tạo kết mở.

Trạng thái cuối: image 2 đứng tại lối đi gần bàn ăn, cầm image 7 và image 8. image 1 đứng nguyên tại đảo bếp. image 5 vẫn nằm trên bàn kính. Không có thêm hành động hoặc lời thoại sau CTA.

Không tự ý thay đổi vị trí, không thêm nhân vật, không để image 2 nói thay image 1, không tạo lời thoại ngoài kịch bản, không chèn chữ hoặc phụ đề trên màn hình.
