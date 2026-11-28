/**
 * Quay trọn bộ 6 Video còn lại (Video 1, 2, 4, 5, 6, 7) trong chuỗi 7 Kịch bản AI 30–40s cho Hậu:
 * - Mỗi video đúng 3 Cảnh (10–13 giây/cảnh) trên Google Flow `Omni 1.2 Flash` (khung dọc 9:16)
 * - Chị Hậu TRỰC TIẾP NÓI THOẠI trước ống kính (giọng nữ miền Bắc tự nhiên như trò chuyện với khách, lip-sync 100%, 0% Voiceover rời)
 * - Mỗi video 1 trang phục khác nhau từ 6 tạo hình đã duyệt
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const SERIES_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Series_7_Video_Kien_Thuc_Chi_Hau";
const REF_DIR = path.join(SERIES_DIR, "00_Refs_6_Styles_Hau_JPG");

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
flow.setup({ getPath: () => DATA_DIR });

function loadRef(fn) {
  const buf = fs.readFileSync(path.join(REF_DIR, fn));
  return { name: fn, mime: "image/jpeg", base64: buf.toString("base64") };
}

const VOICE_LOCK =
  "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 30 tuổi, âm sắc trong trẻo ấm áp, nhẹ nhàng gần gũi, nhịp nói tự nhiên vừa phải như đang trò chuyện trực tiếp với khách, nói đúng 1 lần không lặp từ, lip-sync khớp môi chính xác 100%. KHÔNG nhạc nền, KHÔNG tiếng ồn, KHÔNG phụ đề hay chữ trên màn hình.";

function makePrompt(sec, refName, outfitDesc, sceneSpace, actionDesc, dialogue) {
  return (
    `Tạo video ${sec} giây, photorealistic live-action, phong cách video chia sẻ dinh dưỡng đời thường ngắn gọn tự nhiên, tỷ lệ dọc 9:16.\n\n` +
    `IMAGE XUẤT HIỆN:\n- image 1: ${refName} (nhân vật Hậu)\n\n` +
    `REFERENCE:\nSử dụng đúng nhân vật trong ${refName}. Giữ nguyên 100% khuôn mặt, mái tóc bob nâu hạt dẻ, vóc dáng và ${outfitDesc}. Không thêm người khác.\n\n` +
    `BỐI CẢNH & CHỐT KHÔNG GIAN:\n${sceneSpace}\n\n` +
    `CAMERA:\nMedium close-up (cận trung lấy rõ gương mặt biểu cảm của Hậu và các đạo cụ thực tế phía trước). Một cảnh quay liền mạch ổn định, không tự chia shot.\n\n` +
    `DIỄN BIẾN:\n${actionDesc}\n\n` +
    `THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\nHậu nhìn thẳng ống kính nói: “${dialogue}”\n` +
    VOICE_LOCK
  );
}

const VIDEO_SPECS = [
  // ================= VIDEO 1: ĂN ĐỦ ĐẠM GIÚP GIẢM CÂN DỄ HƠN =================
  {
    vid: "V01_An_Du_Dam_Giam_Can",
    ref: loadRef("hau_v01_sporty.jpg"),
    outfit: "trang phục áo khoác thể thao xanh sage kéo khóa gọn gàng",
    scenes: [
      {
        id: "scene_01",
        sec: 11,
        space: "Căn bếp gia đình sáng nắng lúc 10 giờ sáng. Hậu đứng cạnh tủ bếp mở nhẹ, trên mặt bàn gỗ phía trước có một đĩa chỉ gồm củ khoai lang luộc và vài lát trái cây.",
        action: "Đầu cảnh Hậu khẽ mở cánh tủ bếp tìm đồ ăn rồi nhìn xuống đĩa khoai với trái cây trên bàn, sau đó quay sang nhìn thẳng ống kính mỉm cười gần gũi và nói trực tiếp lời thoại.",
        text: "Đang giảm cân mà mười giờ sáng đã mở tủ tìm đồ ăn? Thử nhìn lại bữa sáng xem có món nào giàu đạm chưa.",
      },
      {
        id: "scene_02",
        sec: 13,
        space: "Cùng căn bếp sáng nắng. Trên mặt bàn gỗ trước mặt Hậu đặt rõ hai đĩa khoai lang cạnh nhau: đĩa bên trái chỉ có khoai, đĩa bên phải giữ phần khoai và có thêm một quả trứng luộc cùng một hũ sữa chua trắng giàu đạm.",
        action: "Hậu đặt nhẹ hũ sữa chua cạnh đĩa khoai có quả trứng, hướng bàn tay giới thiệu hai đĩa đối chiếu trực quan rồi nhìn thẳng ống kính nói trực tiếp.",
        text: "Nếu sáng nay chỉ ăn khoai với trái cây, mai Hậu gợi ý giữ phần khoai và thêm một quả trứng hoặc một hũ sữa chua giàu đạm. Protein có thể giúp mình thấy no hơn sau bữa ăn.",
      },
      {
        id: "scene_03",
        sec: 12,
        space: "Bàn ăn sáng gọn gàng trong bếp sáng nắng. Trước mặt Hậu là đĩa bữa sáng cân đối gồm khoai lang, một quả trứng luộc bổ đôi và hũ sữa chua giàu đạm.",
        action: "Hậu nhìn đĩa bữa sáng giàu đạm trước mặt với vẻ hài lòng rồi ngước nhìn thẳng vào ống kính, trò chuyện ấm áp khích lệ người xem đến hết câu.",
        text: "Còn cân nặng thay đổi thế nào vẫn phụ thuộc vào tổng năng lượng mình ăn và tiêu hao theo thời gian. Mai thử đổi bữa sáng rồi để ý xem mấy giờ mình bắt đầu đói nhé.",
      },
    ],
  },

  // ================= VIDEO 2: CÙNG GIẢM 2 KÝ, CƠ THỂ THAY ĐỔI GIỐNG NHAU KHÔNG? =================
  {
    vid: "V02_Giam_2_Ky_Thay_Doi_Gi",
    ref: loadRef("hau_v02_casual.jpg"),
    outfit: "áo sơ mi linen ngắn tay màu xanh bơ nhạt và quần kem thanh lịch",
    scenes: [
      {
        id: "scene_01",
        sec: 12,
        space: "Phòng khách gia đình thoáng sáng cạnh lối cầu thang gỗ, trên mặt bàn nhỏ phía trước đặt một chiếc cân sức khỏe điện tử hiện đại.",
        action: "Hậu đặt nhẹ tay lên cạnh chiếc cân sức khỏe trên bàn, ánh mắt nhìn thẳng ống kính chia sẻ tự nhiên với người xem.",
        text: "Cùng giảm hai ký, có người vẫn leo cầu thang khỏe, có người lại thấy yếu đi. Cái cân cho mình biết cân nặng thay đổi bao nhiêu. Số ký giảm có thể gồm cả mỡ, nước và cơ.",
      },
      {
        id: "scene_02",
        sec: 12,
        space: "Cùng phòng khách sáng nắng. Phía sau Hậu là chiếc ghế gỗ, trên tay Hậu cầm một cặp tạ tay nhỏ gọn màu pastel nhẹ nhàng.",
        action: "Đầu cảnh Hậu vừa đứng thẳng người dậy nhẹ nhàng khỏe khoắn khỏi chiếc ghế gỗ, hai tay nâng nhẹ cặp tạ nhỏ vài nhịp gọn gàng, mắt nhìn thẳng ống kính nói trực tiếp.",
        text: "Khi đang giảm cân, ăn đủ đạm và tập sức mạnh giúp mình giữ cơ tốt hơn. Hậu gợi ý theo dõi thêm một việc rất đời thường, như đứng lên khỏi ghế hoặc xách đồ đi chợ.",
      },
      {
        id: "scene_03",
        sec: 9,
        space: "Bàn ăn gia đình sáng sủa nối liền cửa ra vào. Trên bàn có bữa cơm cân bằng gồm đĩa cá áp chảo, đĩa rau xanh và chén cơm vừa phải; tay Hậu khoác nhẹ túi vải đi chợ đựng rau củ tươi.",
        action: "Hậu đặt túi đồ đi chợ gọn gàng cạnh bàn cơm có cá và rau, nhìn thẳng ống kính mỉm cười tươi tắn nói câu kết.",
        text: "Nếu cân đang xuống, hãy để ý xem sức mình thay đổi thế nào qua từng tuần.",
      },
    ],
  },

  // ================= VIDEO 4: ÍT UỐNG SỮA, TÌM CANXI Ở ĐÂU? =================
  {
    vid: "V04_It_Uong_Sua_Tim_Canxi",
    ref: loadRef("hau_v04_cozy_yellow.jpg"),
    outfit: "đầm len tăm màu vàng bơ dịu dàng khoác áo cardigan kem mỏng",
    scenes: [
      {
        id: "scene_01",
        sec: 13,
        space: "Bàn cơm gia đình Việt Nam ấm cúng. Trước mặt Hậu bày rõ đĩa cá mòi kho mềm nguyên con ăn cả xương, đĩa đậu phụ trắng mềm và đĩa rau xanh.",
        action: "Hậu ngồi bên mâm cơm gia đình, mở nhẹ bàn tay giới thiệu đĩa cá mòi và đĩa đậu phụ trên bàn, nhìn thẳng ống kính trò chuyện tự nhiên.",
        text: "Nhà mình có người ngại uống sữa thì tìm canxi ở đâu? Hậu sẽ nhìn ngay vào những món cả nhà vẫn ăn hằng ngày. Ví dụ, cá mòi ăn cả xương là một nguồn canxi. Đậu phụ làm bằng muối canxi cũng là một lựa chọn.",
      },
      {
        id: "scene_02",
        sec: 10,
        space: "Quầy bàn ăn gia đình sáng rõ. Trên tay Hậu cầm một hộp sữa đậu nành giấy màu kem trắng tối giản (không logo thương hiệu).",
        action: "Hậu khẽ lật mặt bên của hộp sữa đậu nành lại, ngón tay chỉ nhẹ vào bảng thông tin dinh dưỡng rồi ngước nhìn thẳng ống kính nói rõ ràng.",
        text: "Còn nếu mua sữa đậu nành, Hậu sẽ lật hộp xem có bổ sung canxi không và mỗi khẩu phần có bao nhiêu miligam.",
      },
      {
        id: "scene_03",
        sec: 10,
        space: "Góc bàn ăn cạnh khung cửa sổ đón ánh nắng ban mai ấm áp, trên bàn có giỏ thức ăn tươi mới đi chợ về gồm đậu phụ, cá nhỏ và rau xanh.",
        action: "Hậu đứng bên giỏ thực phẩm tươi cạnh nắng sớm cửa sổ, nhìn thẳng ống kính mỉm cười thân thiện nhắn nhủ người xem.",
        text: "Có một chi tiết hay nữa là vitamin D giúp cơ thể hấp thu canxi. Lần tới đi chợ, thử tìm một món giàu canxi hợp khẩu vị cả nhà nhé.",
      },
    ],
  },

  // ================= VIDEO 5: MỘT GÓI CÓ 1.000 MG, ĐÓ LÀ 1.000 MG GÌ? =================
  {
    vid: "V05_Mot_Goi_1000mg_La_Gi",
    ref: loadRef("hau_v05_blazer_pink.jpg"),
    outfit: "áo blazer màu hồng đất pastel thanh lịch khoác ngoài áo lụa kem",
    scenes: [
      {
        id: "scene_01",
        sec: 12,
        space: "Bàn gỗ làm việc sáng thoáng. Trước mặt Hậu đặt hai lọ thực phẩm bổ sung màu trắng trơn hoàn toàn tối giản (không logo thương hiệu).",
        action: "Hậu cầm một lọ trắng trơn lên nhìn dòng chữ mặt sau rồi ngước mắt nhìn thẳng ống kính chia sẻ rõ ràng, mạch lạc.",
        text: "Khi xem một sản phẩm bổ sung canxi, Hậu hay đọc phần chữ đi cùng con số. Ví dụ, nếu nhãn ghi một nghìn miligam canxi carbonat thì con số đó là khối lượng của cả hợp chất.",
      },
      {
        id: "scene_02",
        sec: 11,
        space: "Cùng bàn gỗ sáng thoáng với hai lọ trắng trơn đặt ngay ngắn trước mặt Hậu.",
        action: "Hậu đặt nhẹ lọ xuống mặt bàn cạnh lọ thứ hai, dùng ngón tay giải thích từng ý rành mạch và nhìn thẳng vào ống kính trò chuyện tự nhiên.",
        text: "Lượng canxi nguyên tố trong đó khoảng bốn trăm miligam. Giờ mình nhìn thêm một chỗ nữa: lượng này tính cho một viên hay cả một khẩu phần gồm hai viên?",
      },
      {
        id: "scene_03",
        sec: 11,
        space: "Cận trung mặt bàn gỗ trước mặt Hậu: cạnh hai lọ trắng trơn có hai đĩa sứ nhỏ đặt rõ một bên là 1 viên nén trắng, bên kia là 2 viên nén trắng.",
        action: "Hậu chỉ nhẹ vào đĩa 1 viên và đĩa 2 viên để minh họa khẩu phần, rồi nhìn thẳng ống kính mỉm cười đúc kết ngắn gọn.",
        text: "Khi so hai sản phẩm, cứ đưa về cùng đơn vị, chẳng hạn cùng tính miligam canxi nguyên tố trên mỗi khẩu phần, rồi mới so.",
      },
    ],
  },

  // ================= VIDEO 6: VÌ SAO NÓI VỀ COLLAGEN LẠI NHẮC ĐẾN VITAMIN C? =================
  {
    vid: "V06_Collagen_Va_Vitamin_C",
    ref: loadRef("hau_v06_emerald_silk.jpg"),
    outfit: "áo lụa màu xanh ngọc lục bảo sang trọng và tươi tắn",
    scenes: [
      {
        id: "scene_01",
        sec: 11,
        space: "Quầy bếp gỗ sáng nắng tự nhiên. Trên thớt gỗ sạch trước mặt Hậu có hai quả ổi xanh tươi giòn và con dao nhỏ gọt trái cây.",
        action: "Hậu cầm một quả ổi xanh tươi đưa nhẹ lên ngang tầm ngực mỉm cười duyên dáng với ống kính, vừa đặt xuống bổ đôi quả ổi vừa trò chuyện tự nhiên.",
        text: "Nhắc đến collagen mà Hậu lại cầm một quả ổi, nghe hơi lạ đúng không? Cơ thể mình tự tạo collagen, và vitamin C tham gia vào quá trình đó.",
      },
      {
        id: "scene_02",
        sec: 10,
        space: "Cùng quầy bếp gỗ sáng nắng với đĩa ổi xanh vừa cắt miếng giòn ngon đặt trước mặt Hậu.",
        action: "Hậu xếp gọn những miếng ổi tươi ra đĩa sứ trắng, ngước nhìn thẳng vào ống kính với nụ cười rạng rỡ chia sẻ gần gũi.",
        text: "Collagen có trong da và nhiều mô liên kết của cơ thể. Vậy hôm nay làm gì cho dễ? Nhìn xem bữa ăn của mình có thực phẩm giàu vitamin C chưa.",
      },
      {
        id: "scene_03",
        sec: 12,
        space: "Bàn ăn sáng sủa bày sẵn ba đĩa thực phẩm tươi giàu vitamin C màu sắc bắt mắt: đĩa miếng ổi xanh, đĩa cam vàng cắt múi và đĩa rau trộn có ớt chuông đỏ vàng.",
        action: "Hậu chỉ tay duyên dáng lần lượt qua đĩa ổi, đĩa cam vàng và đĩa rau ớt chuông trước mặt, nhìn thẳng ống kính mỉm cười thân thiện kết thúc.",
        text: "Có thể là vài miếng ổi sau bữa trưa, một quả cam cho bữa xế, hoặc thêm ớt chuông vào đĩa rau. Chọn món mình thích để dễ ăn đều hơn nhé.",
      },
    ],
  },

  // ================= VIDEO 7: BỘT NGHỆ VÀ CURCUMIN KHÁC NHAU Ở ĐÂU? =================
  {
    vid: "V07_Bot_Nghe_Va_Curcumin",
    ref: loadRef("hau_v07_kitchen_apron.jpg"),
    outfit: "tạp dề linen màu kem mặc ngoài áo sơ mi xanh bơ nhạt gọn gàng",
    scenes: [
      {
        id: "scene_01",
        sec: 13,
        space: "Bàn bếp gỗ ấm sáng nắng. Trước mặt Hậu bày vài củ nghệ tươi vàng cam, một chiếc thìa gỗ đầy bột nghệ mịn đặt cạnh hai hũ thủy tinh trơn tối giản.",
        action: "Hậu cầm nhẹ chiếc thìa gỗ đựng bột nghệ đặt cạnh nhánh nghệ tươi và hai hũ trơn, nhìn thẳng ống kính giải thích tự nhiên rõ ràng.",
        text: "Một nhãn ghi năm trăm miligam bột nghệ, nhãn kia ghi năm trăm miligam chiết xuất nghệ. Hai con số giống nhau, nhưng mô tả hai nguyên liệu khác nhau. Curcumin là một trong các hợp chất có trong củ nghệ.",
      },
      {
        id: "scene_02",
        sec: 11,
        space: "Cùng bàn bếp gỗ sáng nắng với hai hộp/hũ trơn màu kem đặt song song trước mặt Hậu cạnh củ nghệ tươi.",
        action: "Hậu đặt hai bàn tay chỉ rõ sang hai hũ nguyên liệu đặt cạnh nhau trên bàn để phân biệt, mắt nhìn thẳng ống kính nói mạch lạc.",
        text: "Khi xem nhãn, Hậu đọc tên nguyên liệu trước, rồi xem có ghi riêng lượng curcumin hoặc tổng curcuminoid trên mỗi khẩu phần hay không.",
      },
      {
        id: "scene_03",
        sec: 12,
        space: "Cận trung tại bàn bếp gỗ sáng nắng, trên tay Hậu cầm một hộp thực phẩm trơn màu kem không logo thương hiệu.",
        action: "Hậu khẽ xoay lật mặt sau của chiếc hộp lại, chỉ nhẹ ngón tay dọc theo hàng chữ thành phần rồi ngước nhìn ống kính mỉm cười gật đầu ấm áp.",
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

async function runSceneJob(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 280000) {
    console.log(`[SKIP] ${job.vid}/${job.id} cached`);
    return { key: `${job.vid}/${job.id}`, ok: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START] ${job.vid}/${job.id} (${job.sec}s) try ${attempt}/2...`);
    try {
      const res = await handlers["flow:generate-video"](null, {
        prompt: job.prompt,
        model: "Omni 1.2 Flash",
        aspect: "portrait",
        resolution: "720p",
        seconds: job.sec,
        mode: "ingredients",
        count: 1,
        images: [job.ref],
      });
      const buf = extractVidBuf(res);
      if (buf && buf.length > 280000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE] ${job.vid}/${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
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
    const sdir = path.join(SERIES_DIR, v.vid, "01_Raw_Scenes");
    fs.mkdirSync(sdir, { recursive: true });
    for (const sc of v.scenes) {
      allJobs.push({
        vid: v.vid,
        id: sc.id,
        sec: sc.sec,
        ref: v.ref,
        outPath: path.join(sdir, `${sc.id}.mp4`),
        prompt: makePrompt(sc.sec, v.ref.name, v.outfit, sc.space, sc.action, sc.text),
      });
    }
  }

  const t0 = Date.now();
  console.log(`=== GENERATING ${allJobs.length} DIRECT-SPEAKING SCENES FOR 6 VIDEOS ===`);
  const res = await runPool(allJobs, 4, runSceneJob);
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  const okCnt = res.filter((r) => r && r.ok).length;
  console.log(`=== COMPLETED ${okCnt}/${allJobs.length} SCENES IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCnt === allJobs.length ? 0 : 1);
})();
