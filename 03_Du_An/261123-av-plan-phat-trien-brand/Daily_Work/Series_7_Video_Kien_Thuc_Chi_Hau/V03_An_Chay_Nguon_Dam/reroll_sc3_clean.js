
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Series_7_Video_Kien_Thuc_Chi_Hau\\V03_An_Chay_Nguon_Dam";
const TALK_DIR = path.join(WORK_DIR, "06_Flow_Direct_Talking_3Scenes");

const handlers = {};
const origLoad = Module._load;
Module._load = function (req) {
  if (req === "electron") {
    return { ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } }, dialog: { showErrorBox: () => {} } };
  }
  return origLoad.apply(this, arguments);
};
const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
flow.setup({ getPath: () => DATA_DIR });

const ch1Buf = fs.readFileSync(path.join(WORK_DIR, "02_ChatGPT_Looks_9x16", "V03_LOOK_DINING_SAGE.jpg"));
const CH_1 = { name: "ch1_hau_sage_dining.jpg", mime: "image/jpeg", base64: ch1Buf.toString("base64") };

const prompt =
  "Tạo video 8 giây, photorealistic live-action, phong cách video chia sẻ dinh dưỡng đời thường tự nhiên, tỷ lệ dọc 9:16.\n\n" +
  "IMAGE XUẤT HIỆN:\n- image 1: ch1_hau_sage_dining.jpg (nhân vật Chị Hậu)\n\n" +
  "REFERENCE:\nSử dụng đúng nhân vật trong ch1_hau_sage_dining.jpg. Giữ nguyên 100% khuôn mặt, mái tóc bob nâu hạt dẻ, vóc dáng và chiếc áo sơ mi linen màu xanh bơ nhạt đồng nhất xuyên suốt. Không thêm người khác.\n\n" +
  "BỐI CẢNH & CHỐT KHÔNG GIAN:\nQuầy đảo bếp gỗ ấm sáng nắng tự nhiên trong nhà. Trước mặt Chị Hậu có cuốn sổ tay nhỏ mở sẵn kèm cây bút để lên thực đơn, đặt cạnh đĩa đậu phụ trắng tươi, bát đậu gà và rổ rau xanh sạch.\n\n" +
  "CAMERA:\nMedium close-up (cận trung lấy rõ gương mặt tươi tắn của Chị Hậu và cuốn sổ tay thực đơn phía trước). Một cảnh quay liền mạch duy nhất.\n\n" +
  "DIỄN BIẾN:\nChị Hậu cầm cây bút đặt nhẹ trên cuốn sổ tay thực đơn, ngước mắt nhìn thẳng vào ống kính với nụ cười ấm áp thân thiện, nói trọn vẹn đúng một lần câu thoại rồi khẽ gật đầu mỉm cười hiền hậu kết thúc cảnh.\n\n" +
  "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG ĐÚNG 1 LẦN, KHÔNG LẶP LẠI TỪ):\nChị Hậu nhìn thẳng ống kính nói: “Lần tới nấu cơm chay, thử chọn món đạm ngay từ lúc lên thực đơn nhé.”\n" +
  "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 30 tuổi, âm sắc trong trẻo ấm áp, nhẹ nhàng gần gũi như đang trò chuyện trực tiếp với khách, lip-sync khớp môi chính xác 100%, KHÔNG nhạc nền, KHÔNG phụ đề hay chữ trên màn hình.";

(async () => {
  const outClean = path.join(TALK_DIR, "scene_03_8s.mp4");
  const res = await handlers["flow:generate-video"](null, {
    prompt,
    model: "Omni 1.2 Flash",
    aspect: "portrait",
    resolution: "720p",
    seconds: 8,
    mode: "ingredients",
    count: 1,
    images: [CH_1],
  });
  let buf = null;
  if (res?.videoPath && fs.existsSync(res.videoPath)) buf = fs.readFileSync(res.videoPath);
  else if (res?.data) buf = Buffer.isBuffer(res.data) ? res.data : Buffer.from(String(res.data).replace(/^data:video\/\w+;base64,/, ""), "base64");
  if (buf && buf.length > 250000) {
    fs.writeFileSync(outClean, buf);
    console.log("[DONE] scene_03_8s.mp4 ->", Math.round(buf.length / 1024), "KB");
  }
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  process.exit(0);
})();
