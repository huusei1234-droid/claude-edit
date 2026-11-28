/**
 * Retake chính xác 4 cảnh cần quay lại trên Google Flow `Omni 1.2 Flash` để khớp 100% từng chữ kịch bản:
 *   1. V01_An_Du_Dam_Giam_Can / scene_01 (11s)
 *   2. V04_It_Uong_Sua_Tim_Canxi / scene_01 (15s — câu dài 41 chữ, tăng lên 15s để không cụt chữ cuối "lựa chọn")
 *   3. V05_Mot_Goi_1000mg_La_Gi / scene_03 (11s — thay cảnh lẫn từ tab khác)
 *   4. V07_Bot_Nghe_Va_Curcumin / scene_01 (15s — câu dài 38 chữ, nói chuẩn từng chữ kịch bản)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const OUT_SERIES_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Series_7_Video_Kien_Thuc_Chi_Hau\\Chi_Hang_2711";
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
flow.setup({ getPath: () => DATA_DIR });

function loadRef(fn) {
  const buf = fs.readFileSync(path.join(REF_DIR, fn));
  return { name: fn, mime: "image/jpeg", base64: buf.toString("base64") };
}

const VOICE_LOCK =
  "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 35 tuổi, âm sắc trong trẻo ấm áp, nhịp nói vừa phải rõ chữ, nói ĐÚNG 1 LẦN trọn vẹn câu thoại rồi mỉm cười khép môi nghỉ (TUYỆT ĐỐI KHÔNG lặp lại cụm từ cuối câu), lip-sync khớp môi chính xác 100%. KHÔNG nhạc nền, KHÔNG tiếng ồn, KHÔNG chữ trên màn hình.";

function makePrompt(sec, refName, outfitDesc, sceneSpace, actionDesc, dialogue) {
  return (
    `Tạo video ${sec} giây, photorealistic live-action, phong cách video chia sẻ dinh dưỡng đời thường ngắn gọn tự nhiên, tỷ lệ dọc 9:16.\n\n` +
    `IMAGE XUẤT HIỆN:\n- image 1: ${refName} (nhân vật Chị Hằng)\n\n` +
    `REFERENCE:\nSử dụng đúng nhân vật người phụ nữ Việt Nam trong ${refName}. Giữ nguyên 100% khuôn mặt thật phúc hậu thanh tú của Chị Hằng, mái tóc nâu đen uốn sóng rẽ ngôi tự nhiên, vóc dáng thon gọn và ${outfitDesc}. Không thêm người khác.\n\n` +
    `BỐI CẢNH & CHỐT KHÔNG GIAN:\n${sceneSpace}\n\n` +
    `CAMERA:\nMedium close-up (cận trung lấy rõ gương mặt biểu cảm tươi tắn của Chị Hằng và các đạo cụ thực tế phía trước). Một cảnh quay liền mạch ổn định, không tự chia shot.\n\n` +
    `DIỄN BIẾN:\n${actionDesc}\n\n` +
    `THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG ĐÚNG NGUYÊN VĂN):\nChị Hằng nhìn thẳng ống kính nói rõ ràng đúng 1 lần: “${dialogue}”\n` +
    VOICE_LOCK
  );
}

const RETAKES = [
  {
    vid: "V01_An_Du_Dam_Giam_Can",
    id: "scene_01",
    sec: 11,
    refFn: "hang_v01.jpg",
    outfit: "trang phục thể thao năng động áo khoác xanh sage mặc ngoài áo trắng và chân váy thể thao trắng",
    space: "Căn bếp gia đình hiện đại sáng nắng lúc 10 giờ sáng. Chị Hằng đứng cạnh tủ bếp mở nhẹ, trên mặt bàn bếp phía trước có một đĩa chỉ gồm củ khoai lang luộc và vài lát trái cây.",
    action: "Đầu cảnh Chị Hằng khẽ mở cánh tủ bếp tìm đồ ăn rồi nhìn xuống đĩa khoai với trái cây trên bàn, sau đó quay sang nhìn thẳng ống kính mỉm cười gần gũi và nói trực tiếp lời thoại.",
    text: "Đang giảm cân mà mười giờ sáng đã mở tủ tìm đồ ăn? Thử nhìn lại bữa sáng xem có món nào giàu đạm chưa.",
  },
  {
    vid: "V04_It_Uong_Sua_Tim_Canxi",
    id: "scene_01",
    sec: 15,
    refFn: "hang_v04.jpg",
    outfit: "đầm len cổ vuông màu vàng bơ tôn dáng khoác nhẹ áo cardigan kem trên vai",
    space: "Bàn cơm gia đình Việt Nam ấm cúng bên khung cửa sổ nắng mai. Trước mặt Chị Hằng bày rõ đĩa cá mòi kho mềm nguyên con ăn cả xương, đĩa đậu phụ trắng mềm và đĩa rau xanh.",
    action: "Chị Hằng ngồi bên mâm cơm gia đình, mở nhẹ bàn tay giới thiệu đĩa cá mòi và đĩa đậu phụ trên bàn, nhìn thẳng ống kính trò chuyện tự nhiên trọn vẹn hết câu.",
    text: "Nhà mình có người ngại uống sữa thì tìm canxi ở đâu? Hằng sẽ nhìn ngay vào những món cả nhà vẫn ăn hằng ngày. Ví dụ, cá mòi ăn cả xương là một nguồn canxi. Đậu phụ làm bằng muối canxi cũng là một lựa chọn.",
  },
  {
    vid: "V05_Mot_Goi_1000mg_La_Gi",
    id: "scene_03",
    sec: 11,
    refFn: "hang_v05.jpg",
    outfit: "áo blazer chiết eo màu hồng đất pastel thanh lịch khoác ngoài áo lụa kem và quần âu trắng kem",
    space: "Cận trung mặt bàn gỗ trước mặt Chị Hằng: cạnh hai lọ trắng trơn không chữ có hai đĩa sứ nhỏ đặt rõ một bên là 1 viên nén trắng, bên kia là 2 viên nén trắng.",
    action: "Chị Hằng chỉ nhẹ vào đĩa 1 viên và đĩa 2 viên để minh họa khẩu phần, rồi nhìn thẳng ống kính mỉm cười đúc kết ngắn gọn.",
    text: "Khi so hai sản phẩm, cứ đưa về cùng đơn vị, chẳng hạn cùng tính miligam canxi nguyên tố trên mỗi khẩu phần, rồi mới so.",
  },
  {
    vid: "V07_Bot_Nghe_Va_Curcumin",
    id: "scene_01",
    sec: 15,
    refFn: "hang_v07.jpg",
    outfit: "tạp dề linen màu kem thắt eo gọn gàng mặc ngoài áo thun tăm màu cam đất ấm áp",
    space: "Đảo bếp gỗ ấm sáng nắng. Trước mặt Chị Hằng bày vài củ nghệ tươi vàng cam, một chiếc thìa gỗ đầy bột nghệ mịn đặt cạnh hai hũ thủy tinh trơn tối giản không nhãn thương hiệu.",
    action: "Chị Hằng cầm nhẹ chiếc thìa gỗ đựng bột nghệ đặt cạnh nhánh nghệ tươi và hai hũ trơn, nhìn thẳng ống kính giải thích tự nhiên rõ ràng trọn vẹn câu thoại.",
    text: "Một nhãn ghi năm trăm miligam bột nghệ, nhãn kia ghi năm trăm miligam chiết xuất nghệ. Hai con số giống nhau, nhưng mô tả hai nguyên liệu khác nhau. Curcumin là một trong các hợp chất có trong củ nghệ.",
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

async function runOne(item) {
  const ref = loadRef(item.refFn);
  const outPath = path.join(OUT_SERIES_DIR, item.vid, "01_Raw_Scenes", `${item.id}.mp4`);
  if (fs.existsSync(outPath)) fs.unlinkSync(outPath);
  const prompt = makePrompt(item.sec, ref.name, item.outfit, item.space, item.action, item.text);

  for (let attempt = 1; attempt <= 3; attempt++) {
    console.log(`[RETAKE START] ${item.vid}/${item.id} (${item.sec}s) try ${attempt}/3...`);
    try {
      const res = await handlers["flow:generate-video"](null, {
        prompt,
        model: "Omni 1.2 Flash",
        aspect: "portrait",
        resolution: "720p",
        seconds: item.sec,
        mode: "ingredients",
        count: 1,
        images: [ref],
      });
      const buf = extractVidBuf(res);
      if (buf && buf.length > 260000) {
        fs.writeFileSync(outPath, buf);
        console.log(`[RETAKE DONE] ${item.vid}/${item.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return true;
      }
      console.warn(`[WARN] ${item.vid}/${item.id} try ${attempt}:`, res?.error || "empty");
    } catch (e) {
      console.warn(`[ERR] ${item.vid}/${item.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3500));
  }
  return false;
}

(async () => {
  // Chạy tuần tự 2 cặp (concurrency=2) sạch tuyệt đối
  let idx = 0;
  const results = new Array(RETAKES.length);
  async function worker(w) {
    await new Promise((r) => setTimeout(r, w * 4000));
    while (idx < RETAKES.length) {
      const i = idx++;
      results[i] = await runOne(RETAKES[i]);
    }
  }
  await Promise.all([worker(0), worker(1)]);
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  const ok = results.filter(Boolean).length;
  console.log(`=== RETAKES COMPLETED: ${ok}/${RETAKES.length} ===`);
  process.exit(ok === RETAKES.length ? 0 : 1);
})();
