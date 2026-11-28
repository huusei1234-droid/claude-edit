/**
 * Sản xuất trọn bộ 7 Video AI 30–40 giây cho Chị Hằng (An Vượng Pharma — 27/11/2026):
 * - Mỗi video đúng 3 Cảnh (10–13 giây/cảnh), khung dọc 9:16
 * - Tuân thủ Quy tắc 3: Ưu tiên số 1 chạy qua `gemini-driver.js` (xoay cạn 100% tài khoản Gemini Web Pro u/0..u/9 trong Brave :9333 với 10s/15s) -> khi hết sạch mới tự động chuyển sang Google Flow `Omni 1.2 Flash`!
 * - Chị Hằng TRỰC TIẾP NÓI THOẠI trước ống kính (giọng nữ miền Bắc ấm áp tự nhiên như trò chuyện với khách, lip-sync 100%, 0% Voiceover rời)
 * - Mỗi video 1 phong cách & 1 bộ trang phục riêng biệt của Chị Hằng (`hang_v01.jpg` .. `hang_v07.jpg`)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const SERIES_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Series_7_Video_Kien_Thuc_Chi_Hau";
const OUT_SERIES_DIR = path.join(SERIES_DIR, "Chi_Hang_2711");
const REF_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\Build_Mau_Moi_2711\\Chi_Hang_Flow_Refs_JPG";

const handlers = {};
const origLoad = Module._load;
Module._load = function (req) {
  if (req === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: (t, m) => console.error("[DIALOG]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
const gemini = require(path.join(DESKTOP_DIR, "gemini-driver.js"));
flow.setup({ getPath: () => DATA_DIR });
gemini.setup({ getPath: () => DATA_DIR });

function loadRef(fn) {
  const buf = fs.readFileSync(path.join(REF_DIR, fn));
  return { name: fn, mime: "image/jpeg", base64: buf.toString("base64") };
}

const VOICE_LOCK =
  "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 35 tuổi, âm sắc trong trẻo ấm áp, truyền cảm nhẹ nhàng gần gũi, nhịp nói tự nhiên vừa phải như đang trò chuyện trực tiếp với khách, nói đúng 1 lần không lặp từ, lip-sync khớp môi chính xác 100%. KHÔNG nhạc nền, KHÔNG tiếng ồn, KHÔNG phụ đề hay chữ trên màn hình.";

function makePrompt(sec, refName, outfitDesc, sceneSpace, actionDesc, dialogue) {
  return (
    `Tạo video ${sec} giây, photorealistic live-action, phong cách video chia sẻ dinh dưỡng đời thường ngắn gọn tự nhiên, tỷ lệ dọc 9:16.\n\n` +
    `IMAGE XUẤT HIỆN:\n- image 1: ${refName} (nhân vật Chị Hằng)\n\n` +
    `REFERENCE:\nSử dụng đúng nhân vật người phụ nữ Việt Nam trong ${refName}. Giữ nguyên 100% khuôn mặt thật phúc hậu thanh tú của Chị Hằng, mái tóc nâu đen uốn sóng rẽ ngôi tự nhiên, vóc dáng thon gọn và ${outfitDesc}. Không thêm người khác.\n\n` +
    `BỐI CẢNH & CHỐT KHÔNG GIAN:\n${sceneSpace}\n\n` +
    `CAMERA:\nMedium close-up (cận trung lấy rõ gương mặt biểu cảm tươi tắn của Chị Hằng và các đạo cụ thực tế phía trước). Một cảnh quay liền mạch ổn định, không tự chia shot.\n\n` +
    `DIỄN BIẾN:\n${actionDesc}\n\n` +
    `THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾP TRƯỚC ỐNG KÍNH):\nChị Hằng nhìn thẳng ống kính nói rõ ràng trọn vẹn: “${dialogue}”\n` +
    VOICE_LOCK
  );
}

const VIDEO_SPECS = [
  // ================= VIDEO 1: TẠI SAO ĂN ĐỦ ĐẠM GIÚP GIẢM CÂN DỄ HƠN? =================
  {
    vid: "V01_An_Du_Dam_Giam_Can",
    refFn: "hang_v01.jpg",
    outfit: "trang phục thể thao năng động áo khoác xanh sage mặc ngoài áo trắng và chân váy thể thao trắng",
    scenes: [
      {
        id: "scene_01",
        sec: 11,
        space: "Căn bếp gia đình hiện đại sáng nắng lúc 10 giờ sáng. Chị Hằng đứng cạnh tủ bếp mở nhẹ, trên mặt bàn bếp phía trước có một đĩa chỉ gồm củ khoai lang luộc và vài lát trái cây.",
        action: "Đầu cảnh Chị Hằng khẽ mở cánh tủ bếp tìm đồ ăn rồi nhìn xuống đĩa khoai với trái cây trên bàn, sau đó quay sang nhìn thẳng ống kính mỉm cười gần gũi và nói trực tiếp lời thoại.",
        text: "Đang giảm cân mà mười giờ sáng đã mở tủ tìm đồ ăn? Thử nhìn lại bữa sáng xem có món nào giàu đạm chưa.",
      },
      {
        id: "scene_02",
        sec: 13,
        space: "Cùng căn bếp sáng nắng. Trên mặt bàn bếp trước mặt Chị Hằng đặt rõ hai đĩa khoai lang cạnh nhau: đĩa bên trái chỉ có khoai, đĩa bên phải giữ phần khoai và có thêm một quả trứng luộc cùng một hũ sữa chua trắng giàu đạm.",
        action: "Chị Hằng đặt nhẹ hũ sữa chua cạnh đĩa khoai có quả trứng, hướng bàn tay giới thiệu hai đĩa đối chiếu trực quan rồi nhìn thẳng ống kính nói trực tiếp.",
        text: "Nếu sáng nay chỉ ăn khoai với trái cây, mai Hằng gợi ý giữ phần khoai và thêm một quả trứng hoặc một hũ sữa chua giàu đạm. Protein có thể giúp mình thấy no hơn sau bữa ăn.",
      },
      {
        id: "scene_03",
        sec: 12,
        space: "Đảo bếp ăn sáng gọn gàng trong nắng sớm. Trước mặt Chị Hằng là đĩa bữa sáng cân đối gồm khoai lang, một quả trứng luộc bổ đôi và hũ sữa chua giàu đạm.",
        action: "Chị Hằng nhìn đĩa bữa sáng giàu đạm trước mặt với vẻ hài lòng rồi ngước nhìn thẳng vào ống kính, trò chuyện ấm áp khích lệ người xem đến hết câu.",
        text: "Còn cân nặng thay đổi thế nào vẫn phụ thuộc vào tổng năng lượng mình ăn và tiêu hao theo thời gian. Mai thử đổi bữa sáng rồi để ý xem mấy giờ mình bắt đầu đói nhé.",
      },
    ],
  },

  // ================= VIDEO 2: CÙNG GIẢM 2 KÝ, CƠ THỂ THAY ĐỔI GIỐNG NHAU KHÔNG? =================
  {
    vid: "V02_Giam_2_Ky_Thay_Doi_Gi",
    refFn: "hang_v02.jpg",
    outfit: "áo polo len mịn màu trắng kem cổ viền xanh navy sơ vin quần âu be cạp cao tôn eo thon",
    scenes: [
      {
        id: "scene_01",
        sec: 12,
        space: "Phòng khách gia đình thoáng sáng cạnh lối cầu thang gỗ, trên mặt bàn nhỏ phía trước đặt một chiếc cân sức khỏe điện tử hiện đại.",
        action: "Chị Hằng đặt nhẹ tay lên cạnh chiếc cân sức khỏe trên bàn, ánh mắt nhìn thẳng ống kính chia sẻ tự nhiên với người xem.",
        text: "Cùng giảm hai ký, có người vẫn leo cầu thang khỏe, có người lại thấy yếu đi. Cái cân cho mình biết cân nặng thay đổi bao nhiêu. Số ký giảm có thể gồm cả mỡ, nước và cơ.",
      },
      {
        id: "scene_02",
        sec: 12,
        space: "Cùng phòng khách sáng nắng. Phía sau Chị Hằng là chiếc ghế gỗ, trên tay Chị Hằng cầm một cặp tạ tay nhỏ gọn màu pastel nhẹ nhàng.",
        action: "Đầu cảnh Chị Hằng vừa đứng thẳng người dậy nhẹ nhàng khỏe khoắn khỏi chiếc ghế gỗ, hai tay nâng nhẹ cặp tạ nhỏ vài nhịp gọn gàng, mắt nhìn thẳng ống kính nói trực tiếp.",
        text: "Khi đang giảm cân, ăn đủ đạm và tập sức mạnh giúp mình giữ cơ tốt hơn. Hằng gợi ý theo dõi thêm một việc rất đời thường, như đứng lên khỏi ghế hoặc xách đồ đi chợ.",
      },
      {
        id: "scene_03",
        sec: 10,
        space: "Bàn ăn gia đình sáng sủa nối liền cửa ra vào. Trên bàn có bữa cơm cân bằng gồm đĩa cá áp chảo, đĩa rau xanh và chén cơm vừa phải; tay Chị Hằng khoác nhẹ túi vải đi chợ đựng rau củ tươi.",
        action: "Chị Hằng đặt túi đồ đi chợ gọn gàng cạnh bàn cơm có cá và rau, nhìn thẳng ống kính mỉm cười tươi tắn nói câu kết.",
        text: "Nếu cân đang xuống, hãy để ý xem sức mình thay đổi thế nào qua từng tuần.",
      },
    ],
  },

  // ================= VIDEO 3: ĂN CHAY, NHÌN THẾ NÀO ĐỂ BIẾT BỮA ĂN CÓ NGUỒN ĐẠM? =================
  {
    vid: "V03_An_Chay_Nguon_Dam",
    refFn: "hang_v03.jpg",
    outfit: "áo sơ mi linen ngắn tay màu xanh mint nhạt sơ vin quần kem thanh lịch",
    scenes: [
      {
        id: "scene_01",
        sec: 12,
        space: "Phòng ăn gia đình ấm cúng bàn gỗ tự nhiên. Trước mặt Chị Hằng bày mâm cơm chay gọn đẹp gồm bát cơm trắng, đĩa rau luộc xanh, bát canh bí đỏ và đĩa nấm xào.",
        action: "Chị Hằng ngồi bên mâm cơm chay thanh đạm, mở nhẹ bàn tay giới thiệu các món trên mâm rồi nhìn thẳng ống kính đặt câu hỏi tự nhiên gần gũi.",
        text: "Một mâm cơm chay có cơm, rau luộc, canh bí và nấm xào nhìn rất đầy đặn. Trước khi ăn, Hằng hay hỏi một câu: Món nào hôm nay là nguồn đạm chính?",
      },
      {
        id: "scene_02",
        sec: 11,
        space: "Cùng mâm cơm chay trên bàn gỗ sáng nắng. Trên tay Chị Hằng bưng một đĩa đậu phụ sốt cà chua chín đỏ hấp dẫn đặt thêm vào giữa mâm cơm.",
        action: "Chị Hằng nhẹ nhàng đặt đĩa đậu phụ sốt cà vào mâm cơm chay, bên cạnh có thêm chén nhỏ đậu gà và đậu lăng luộc chín mềm, ngước nhìn thẳng ống kính nói tươi tắn.",
        text: "Nếu chưa có, mình có thể thêm đậu phụ sốt cà, một phần đậu gà hoặc đậu lăng.",
      },
      {
        id: "scene_03",
        sec: 12,
        space: "Cận trung bàn ăn gỗ sáng thoáng. Trước mặt Chị Hằng bày rõ ba bát sứ trắng sạch sẽ đựng đậu phụ sốt cà, hạt đậu gà vàng bùi và đậu lăng nấu chín cạnh bát cơm gạo lứt.",
        action: "Chị Hằng chỉ nhẹ bàn tay qua ba món đậu phụ, đậu gà và đậu lăng đa dạng trước mặt, nhìn thẳng ống kính mỉm cười ấm áp nhắn nhủ câu kết.",
        text: "Ăn chay lâu dài thì đổi qua lại các loại đậu và ngũ cốc trong ngày để có nguồn axit amin đa dạng hơn. Lần tới nấu cơm chay, thử chọn món đạm ngay từ lúc lên thực đơn nhé.",
      },
    ],
  },

  // ================= VIDEO 4: ÍT UỐNG SỮA, TÌM CANXI Ở ĐÂU? =================
  {
    vid: "V04_It_Uong_Sua_Tim_Canxi",
    refFn: "hang_v04.jpg",
    outfit: "đầm len cổ vuông màu vàng bơ tôn dáng khoác nhẹ áo cardigan kem trên vai",
    scenes: [
      {
        id: "scene_01",
        sec: 13,
        space: "Bàn cơm gia đình Việt Nam ấm cúng bên khung cửa sổ nắng mai. Trước mặt Chị Hằng bày rõ đĩa cá mòi kho mềm nguyên con ăn cả xương, đĩa đậu phụ trắng mềm và đĩa rau xanh.",
        action: "Chị Hằng ngồi bên mâm cơm gia đình, mở nhẹ bàn tay giới thiệu đĩa cá mòi và đĩa đậu phụ trên bàn, nhìn thẳng ống kính trò chuyện tự nhiên.",
        text: "Nhà mình có người ngại uống sữa thì tìm canxi ở đâu? Hằng sẽ nhìn ngay vào những món cả nhà vẫn ăn hằng ngày. Ví dụ, cá mòi ăn cả xương là một nguồn canxi. Đậu phụ làm bằng muối canxi cũng là một lựa chọn.",
      },
      {
        id: "scene_02",
        sec: 10,
        space: "Quầy bàn ăn gia đình sáng rõ. Trên tay Chị Hằng cầm một hộp sữa đậu nành giấy màu kem trắng tối giản không logo thương hiệu.",
        action: "Chị Hằng khẽ lật mặt bên của hộp sữa đậu nành lại, ngón tay chỉ nhẹ vào bảng thông tin dinh dưỡng rồi ngước nhìn thẳng ống kính nói rõ ràng.",
        text: "Còn nếu mua sữa đậu nành, Hằng sẽ lật hộp xem có bổ sung canxi không và mỗi khẩu phần có bao nhiêu miligam.",
      },
      {
        id: "scene_03",
        sec: 11,
        space: "Góc bàn ăn cạnh khung cửa sổ đón ánh nắng ban mai ấm áp, trên bàn có giỏ thức ăn tươi mới đi chợ về gồm đậu phụ, cá nhỏ và rau xanh.",
        action: "Chị Hằng đứng bên giỏ thực phẩm tươi cạnh nắng sớm cửa sổ, nhìn thẳng ống kính mỉm cười thân thiện nhắn nhủ người xem.",
        text: "Có một chi tiết hay nữa là vitamin D giúp cơ thể hấp thu canxi. Lần tới đi chợ, thử tìm một món giàu canxi hợp khẩu vị cả nhà nhé.",
      },
    ],
  },

  // ================= VIDEO 5: MỘT GÓI CÓ 1.000 MG, ĐÓ LÀ 1.000 MG GÌ? =================
  {
    vid: "V05_Mot_Goi_1000mg_La_Gi",
    refFn: "hang_v05.jpg",
    outfit: "áo blazer chiết eo màu hồng đất pastel thanh lịch khoác ngoài áo lụa kem và quần âu trắng kem",
    scenes: [
      {
        id: "scene_01",
        sec: 12,
        space: "Bàn gỗ phòng làm việc sáng thoáng. Trước mặt Chị Hằng đặt hai lọ thực phẩm bổ sung màu trắng trơn hoàn toàn tối giản không logo thương hiệu.",
        action: "Chị Hằng cầm một lọ trắng trơn lên nhìn dòng chữ mặt sau rồi ngước mắt nhìn thẳng ống kính chia sẻ rõ ràng, mạch lạc.",
        text: "Khi xem một sản phẩm bổ sung canxi, Hằng hay đọc phần chữ đi cùng con số. Ví dụ, nếu nhãn ghi một nghìn miligam canxi carbonat thì con số đó là khối lượng của cả hợp chất.",
      },
      {
        id: "scene_02",
        sec: 11,
        space: "Cùng bàn gỗ sáng thoáng với hai lọ trắng trơn đặt ngay ngắn trước mặt Chị Hằng.",
        action: "Chị Hằng đặt nhẹ lọ xuống mặt bàn cạnh lọ thứ hai, dùng ngón tay giải thích từng ý rành mạch và nhìn thẳng vào ống kính trò chuyện tự nhiên.",
        text: "Lượng canxi nguyên tố trong đó khoảng bốn trăm miligam. Giờ mình nhìn thêm một chỗ nữa: lượng này tính cho một viên hay cả một khẩu phần gồm hai viên?",
      },
      {
        id: "scene_03",
        sec: 11,
        space: "Cận trung mặt bàn gỗ trước mặt Chị Hằng: cạnh hai lọ trắng trơn có hai đĩa sứ nhỏ đặt rõ một bên là 1 viên nén trắng, bên kia là 2 viên nén trắng.",
        action: "Chị Hằng chỉ nhẹ vào đĩa 1 viên và đĩa 2 viên để minh họa khẩu phần, rồi nhìn thẳng ống kính mỉm cười đúc kết ngắn gọn.",
        text: "Khi so hai sản phẩm, cứ đưa về cùng đơn vị, chẳng hạn cùng tính miligam canxi nguyên tố trên mỗi khẩu phần, rồi mới so.",
      },
    ],
  },

  // ================= VIDEO 6: VÌ SAO NÓI VỀ COLLAGEN LẠI NHẮC ĐẾN VITAMIN C? =================
  {
    vid: "V06_Collagen_Va_Vitamin_C",
    refFn: "hang_v06.jpg",
    outfit: "áo lụa đắp chéo màu xanh ngọc lục bảo sang trọng phối chân váy midi kem",
    scenes: [
      {
        id: "scene_01",
        sec: 11,
        space: "Quầy bếp gỗ sáng nắng tự nhiên. Trên thớt gỗ sạch trước mặt Chị Hằng có hai quả ổi xanh tươi giòn và con dao nhỏ gọt trái cây.",
        action: "Chị Hằng cầm một quả ổi xanh tươi đưa nhẹ lên ngang tầm ngực mỉm cười duyên dáng với ống kính, vừa đặt xuống bổ đôi quả ổi vừa trò chuyện tự nhiên.",
        text: "Nhắc đến collagen mà Hằng lại cầm một quả ổi, nghe hơi lạ đúng không? Cơ thể mình tự tạo collagen, và vitamin C tham gia vào quá trình đó.",
      },
      {
        id: "scene_02",
        sec: 10,
        space: "Cùng quầy bếp gỗ sáng nắng với đĩa ổi xanh vừa cắt miếng giòn ngon đặt trước mặt Chị Hằng.",
        action: "Chị Hằng xếp gọn những miếng ổi tươi ra đĩa sứ trắng, ngước nhìn thẳng vào ống kính với nụ cười rạng rỡ chia sẻ gần gũi.",
        text: "Collagen có trong da và nhiều mô liên kết của cơ thể. Vậy hôm nay làm gì cho dễ? Nhìn xem bữa ăn của mình có thực phẩm giàu vitamin C chưa.",
      },
      {
        id: "scene_03",
        sec: 12,
        space: "Bàn ăn sáng sủa bày sẵn ba đĩa thực phẩm tươi giàu vitamin C màu sắc bắt mắt: đĩa miếng ổi xanh, đĩa cam vàng cắt múi và đĩa rau trộn có ớt chuông đỏ vàng.",
        action: "Chị Hằng chỉ tay duyên dáng lần lượt qua đĩa ổi, đĩa cam vàng và đĩa rau ớt chuông trước mặt, nhìn thẳng ống kính mỉm cười thân thiện kết thúc.",
        text: "Có thể là vài miếng ổi sau bữa trưa, một quả cam cho bữa xế, hoặc thêm ớt chuông vào đĩa rau. Chọn món mình thích để dễ ăn đều hơn nhé.",
      },
    ],
  },

  // ================= VIDEO 7: BỘT NGHỆ VÀ CURCUMIN KHÁC NHAU Ở ĐÂU? =================
  {
    vid: "V07_Bot_Nghe_Va_Curcumin",
    refFn: "hang_v07.jpg",
    outfit: "tạp dề linen màu kem thắt eo gọn gàng mặc ngoài áo thun tăm màu cam đất ấm áp",
    scenes: [
      {
        id: "scene_01",
        sec: 13,
        space: "Đảo bếp gỗ ấm sáng nắng. Trước mặt Chị Hằng bày vài củ nghệ tươi vàng cam, một chiếc thìa gỗ đầy bột nghệ mịn đặt cạnh hai hũ thủy tinh trơn tối giản.",
        action: "Chị Hằng cầm nhẹ chiếc thìa gỗ đựng bột nghệ đặt cạnh nhánh nghệ tươi và hai hũ trơn, nhìn thẳng ống kính giải thích tự nhiên rõ ràng.",
        text: "Một nhãn ghi năm trăm miligam bột nghệ, nhãn kia ghi năm trăm miligam chiết xuất nghệ. Hai con số giống nhau, nhưng mô tả hai nguyên liệu khác nhau. Curcumin là một trong các hợp chất có trong củ nghệ.",
      },
      {
        id: "scene_02",
        sec: 11,
        space: "Cùng bàn bếp gỗ sáng nắng với hai hộp trơn màu kem đặt song song trước mặt Chị Hằng cạnh củ nghệ tươi.",
        action: "Chị Hằng đặt hai bàn tay chỉ rõ sang hai hũ nguyên liệu đặt cạnh nhau trên bàn để phân biệt, mắt nhìn thẳng ống kính nói mạch lạc.",
        text: "Khi xem nhãn, Hằng đọc tên nguyên liệu trước, rồi xem có ghi riêng lượng curcumin hoặc tổng curcuminoid trên mỗi khẩu phần hay không.",
      },
      {
        id: "scene_03",
        sec: 12,
        space: "Cận trung tại bàn bếp gỗ sáng nắng, trên tay Chị Hằng cầm một hộp thực phẩm trơn màu kem không logo thương hiệu.",
        action: "Chị Hằng khẽ xoay lật mặt sau của chiếc hộp lại, chỉ nhẹ ngón tay dọc theo hàng chữ thành phần rồi ngước nhìn ống kính mỉm cười gật đầu ấm áp.",
        text: "Nếu nhãn chỉ ghi lượng bột nghệ hoặc chiết xuất, mình chưa biết chính xác lượng curcumin từ con số đó. Lật mặt sau đọc thêm một dòng là rõ hơn nhiều.",
      },
    ],
  },
];

function extractVidBuf(res) {
  if (!res) return null;
  if (res.videoPath && fs.existsSync(res.videoPath)) return fs.readFileSync(res.videoPath);
  const b64 = res.data || res.videoBase64 || res.items?.[0]?.data || res.items?.[0]?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  return Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
}

let geminiAllExhausted = false;

async function runSceneJob(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 260000) {
    console.log(`[SKIP] ${job.vid}/${job.id} cached`);
    return { key: `${job.vid}/${job.id}`, ok: true };
  }
  for (let attempt = 1; attempt <= 3; attempt++) {
    console.log(`[START] ${job.vid}/${job.id} (${job.sec}s) try ${attempt}/3 [mode=${geminiAllExhausted ? "flow-parallel" : "gemini-first"}]...`);
    try {
      let res;
      if (!geminiAllExhausted) {
        // Ưu tiên số 1: Gemini Web Pro xoay vòng toàn bộ u/0..u/9 -> nếu hết sạch tự fallback sang Flow!
        res = await handlers["gemini:generate-video"](null, {
          prompt: job.prompt,
          ratio: "9:16",
          aspect: "portrait",
          seconds: job.sec,
          flowSeconds: job.sec,
          flowModel: "Omni 1.2 Flash",
          resolution: "720p",
          mode: "ingredients",
          images: [job.ref],
        });
        if (res?.challengeBlocked) {
          console.error("[BLOCKED BY GOOGLE CHALLENGE] Stopping Gemini scan immediately per anti-CAPTCHA rule!");
          process.exit(2);
        }
        if (res?.provider === "flow-fallback") {
          console.log("[SWITCH] Toàn bộ tài khoản Gemini Pro đã hết lượt -> mở luồng song song trên Google Flow!");
          geminiAllExhausted = true;
        }
      } else {
        res = await handlers["flow:generate-video"](null, {
          prompt: job.prompt,
          model: "Omni 1.2 Flash",
          aspect: "portrait",
          resolution: "720p",
          seconds: job.sec,
          mode: "ingredients",
          count: 1,
          images: [job.ref],
        });
      }
      const buf = extractVidBuf(res);
      if (buf && buf.length > 260000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE ${res?.provider || "flow"}] ${job.vid}/${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { key: `${job.vid}/${job.id}`, ok: true };
      }
      console.warn(`[WARN] ${job.vid}/${job.id} try ${attempt}:`, res?.error || "empty");
    } catch (e) {
      console.warn(`[ERR] ${job.vid}/${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3500));
  }
  return { key: `${job.vid}/${job.id}`, ok: false };
}

async function runPool(items, concurrency, fn) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 3500));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

(async () => {
  const allJobs = [];
  for (const v of VIDEO_SPECS) {
    const refObj = loadRef(v.refFn);
    const sdir = path.join(OUT_SERIES_DIR, v.vid, "01_Raw_Scenes");
    fs.mkdirSync(sdir, { recursive: true });
    for (const sc of v.scenes) {
      allJobs.push({
        vid: v.vid,
        id: sc.id,
        sec: sc.sec,
        ref: refObj,
        outPath: path.join(sdir, `${sc.id}.mp4`),
        prompt: makePrompt(sc.sec, refObj.name, v.outfit, sc.space, sc.action, sc.text),
      });
    }
  }

  const t0 = Date.now();
  console.log(`=== GENERATING ${allJobs.length} DIRECT-SPEAKING SCENES FOR ALL 7 CHI HANG VIDEOS ===`);
  const res = await runPool(allJobs, 2, runSceneJob);
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  const okCnt = res.filter((r) => r && r.ok).length;
  console.log(`=== COMPLETED ${okCnt}/${allJobs.length} SCENES IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCnt === allJobs.length ? 0 : 1);
})();
