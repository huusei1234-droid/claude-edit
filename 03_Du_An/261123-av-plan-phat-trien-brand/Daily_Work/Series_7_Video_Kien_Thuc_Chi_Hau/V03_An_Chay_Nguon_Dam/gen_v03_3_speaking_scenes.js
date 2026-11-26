/**
 * Video #3 — CHỊ HẬU TRỰC TIẾP NÓI THOẠI TRÊN HÌNH (0% VOICEOVER RỜI!):
 * Chuẩn skill `phim-ai-flow-prompt` trên Google Flow `Omni 1.2 Flash` (khung dọc 9:16, 10–14 giây/cảnh):
 *   - Cảnh 1 (12s): Mâm cơm chay (cơm, rau luộc, canh bí, nấm xào) — Chị Hậu nói trực tiếp 2 câu đầu.
 *   - Cảnh 2 (14s): Thêm đậu phụ sốt cà, đậu gà, đậu lăng & các hũ đậu + ngũ cốc — Chị Hậu nói trực tiếp 2 câu giữa.
 *   - Cảnh 3 (10s): Lên thực đơn chọn món đạm ngay từ đầu — Chị Hậu nói trực tiếp câu kết.
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Series_7_Video_Kien_Thuc_Chi_Hau\\V03_An_Chay_Nguon_Dam";
const TALK_DIR = path.join(WORK_DIR, "06_Flow_Direct_Talking_3Scenes");
fs.mkdirSync(TALK_DIR, { recursive: true });

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

const ch1Buf = fs.readFileSync(path.join(WORK_DIR, "02_ChatGPT_Looks_9x16", "V03_LOOK_DINING_SAGE.jpg"));
const CH_1 = { name: "ch1_hau_sage_dining.jpg", mime: "image/jpeg", base64: ch1Buf.toString("base64") };

const VOICE_STYLE_LOCK =
  "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 30 tuổi, âm sắc trong trẻo ấm áp, nhẹ nhàng gần gũi, nhịp nói tự nhiên vừa phải như đang ngồi trò chuyện tâm sự trực tiếp với khách đối diện, phát âm tiếng Việt chuẩn rõ từng chữ, lip-sync khớp môi chính xác 100%. Âm thanh thu trực tiếp trong phòng yên tĩnh, KHÔNG nhạc nền, KHÔNG tiếng ồn, KHÔNG phụ đề hay chữ trên màn hình.";

const SCENES = [
  {
    id: "scene_01",
    seconds: 12,
    outPath: path.join(TALK_DIR, "scene_01.mp4"),
    prompt:
      "Tạo video 12 giây, photorealistic live-action, phong cách video chia sẻ dinh dưỡng đời thường tự nhiên, tỷ lệ dọc 9:16.\n\n" +
      "IMAGE XUẤT HIỆN:\n- image 1: ch1_hau_sage_dining.jpg (nhân vật Chị Hậu)\n\n" +
      "REFERENCE:\nSử dụng đúng nhân vật trong ch1_hau_sage_dining.jpg. Giữ nguyên 100% khuôn mặt, mái tóc bob nâu hạt dẻ, vóc dáng và chiếc áo sơ mi linen màu xanh bơ nhạt. Không thêm người khác.\n\n" +
      "BỐI CẢNH & CHỐT KHÔNG GIAN:\nPhòng ăn gia đình Việt Nam ấm cúng có ánh nắng tự nhiên dịu nhẹ. Chị Hậu ngồi ngay ngắn sau bàn ăn gỗ; ngay trước mặt chị trên khay gỗ là mâm cơm chay gồm đúng 4 món: bát cơm trắng, đĩa rau cải luộc xanh, tô canh bí đỏ và đĩa nấm xào.\n\n" +
      "CAMERA:\nMedium close-up (cận trung ngang thắt lưng lấy rõ gương mặt biểu cảm của Chị Hậu và mâm cơm chay phía trước). Một cảnh quay liền mạch, máy quay giữ ổn định tự nhiên, không cắt shot.\n\n" +
      "DIỄN BIẾN:\nĐầu cảnh Chị Hậu nhìn nhẹ xuống mâm cơm chay trước mặt, bàn tay mở nhẹ giới thiệu các món trên mâm, sau đó ngước lên nhìn thẳng vào ống kính với ánh mắt ấm áp thân thiện và trực tiếp nói hết câu thoại.\n\n" +
      "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\nChị Hậu nói trực tiếp với ống kính: “Một mâm cơm chay có cơm, rau luộc, canh bí và nấm xào nhìn rất đầy đặn. Trước khi ăn, Hậu hay hỏi một câu: Món nào hôm nay là nguồn đạm chính?”\n" +
      VOICE_STYLE_LOCK,
  },
  {
    id: "scene_02",
    seconds: 14,
    outPath: path.join(TALK_DIR, "scene_02.mp4"),
    prompt:
      "Tạo video 14 giây, photorealistic live-action, phong cách video chia sẻ dinh dưỡng đời thường tự nhiên, tỷ lệ dọc 9:16.\n\n" +
      "IMAGE XUẤT HIỆN:\n- image 1: ch1_hau_sage_dining.jpg (nhân vật Chị Hậu)\n\n" +
      "REFERENCE:\nSử dụng đúng nhân vật trong ch1_hau_sage_dining.jpg. Giữ nguyên 100% khuôn mặt, mái tóc bob nâu hạt dẻ, vóc dáng và chiếc áo sơ mi linen màu xanh bơ nhạt đồng nhất với Cảnh 1. Không thêm người khác.\n\n" +
      "BỐI CẢNH & CHỐT KHÔNG GIAN:\nCùng không gian bàn ăn nối liền quầy bếp gỗ sáng nắng tự nhiên. Trên mặt bàn gỗ trước mặt Chị Hậu bày đĩa đậu phụ sốt cà chua đỏ au nóng hổi, một bát đậu gà hạt vàng, một bát đậu lăng và cạnh đó là vài hũ thủy tinh nhỏ đựng các loại hạt đậu và yến mạch ngũ cốc.\n\n" +
      "CAMERA:\nMedium close-up (cận trung lấy rõ gương mặt, cử chỉ tay tự nhiên của Chị Hậu và các món đậu phụ sốt cà, đậu gà, đậu lăng, hũ ngũ cốc trên bàn). Một cảnh liền mạch, camera cố định êm ái, không tự chia shot.\n\n" +
      "DIỄN BIẾN:\nChị Hậu đặt nhẹ đĩa đậu phụ sốt cà ngay ngắn lên mặt bàn, ánh mắt nhìn thẳng vào ống kính, vừa trò chuyện thân tình vừa khẽ hướng bàn tay chỉ nhẹ sang bát đậu gà, đậu lăng và các hũ đậu cùng ngũ cốc bên cạnh một cách tự nhiên.\n\n" +
      "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\nChị Hậu nhìn thẳng ống kính nói: “Nếu chưa có, mình có thể thêm đậu phụ sốt cà, một phần đậu gà hoặc đậu lăng. Ăn chay lâu dài thì đổi qua lại các loại đậu và ngũ cốc trong ngày để có nguồn axit amin đa dạng hơn.”\n" +
      VOICE_STYLE_LOCK,
  },
  {
    id: "scene_03",
    seconds: 10,
    outPath: path.join(TALK_DIR, "scene_03.mp4"),
    prompt:
      "Tạo video 10 giây, photorealistic live-action, phong cách video chia sẻ dinh dưỡng đời thường tự nhiên, tỷ lệ dọc 9:16.\n\n" +
      "IMAGE XUẤT HIỆN:\n- image 1: ch1_hau_sage_dining.jpg (nhân vật Chị Hậu)\n\n" +
      "REFERENCE:\nSử dụng đúng nhân vật trong ch1_hau_sage_dining.jpg. Giữ nguyên 100% khuôn mặt, mái tóc bob nâu hạt dẻ, vóc dáng và chiếc áo sơ mi linen màu xanh bơ nhạt đồng nhất xuyên suốt. Không thêm người khác.\n\n" +
      "BỐI CẢNH & CHỐT KHÔNG GIAN:\nQuầy đảo bếp gỗ ấm sáng nắng tự nhiên trong nhà. Trước mặt Chị Hậu có cuốn sổ tay nhỏ mở sẵn kèm cây bút để lên thực đơn, đặt cạnh đĩa đậu phụ trắng tươi, bát đậu gà và rổ rau xanh sạch.\n\n" +
      "CAMERA:\nMedium close-up (cận trung ngang ngực–eo lấy rõ gương mặt tươi tắn, ánh mắt gần gũi của Chị Hậu và cuốn sổ tay thực đơn phía trước). Một cảnh quay liền mạch duy nhất.\n\n" +
      "DIỄN BIẾN:\nChị Hậu vừa viết xong một dòng ngắn vào cuốn sổ tay thực đơn, liền ngước mắt nhìn thẳng vào ống kính với nụ cười ấm áp khích lệ, nói trực tiếp câu nhắn nhủ với người xem rồi khẽ gật đầu mỉm cười hiền hậu kết thúc cảnh.\n\n" +
      "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\nChị Hậu nhìn thẳng ống kính nói: “Lần tới nấu cơm chay, thử chọn món đạm ngay từ lúc lên thực đơn nhé.”\n" +
      VOICE_STYLE_LOCK,
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

async function runScene(sc) {
  if (fs.existsSync(sc.outPath) && fs.statSync(sc.outPath).size > 300000) {
    console.log(`[SKIP] ${sc.id} cached`);
    return { id: sc.id, ok: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START TALKING SCENE] ${sc.id} (${sc.seconds}s, 9:16, Omni 1.2 Flash) try ${attempt}/2...`);
    try {
      const res = await handlers["flow:generate-video"](null, {
        prompt: sc.prompt,
        model: "Omni 1.2 Flash",
        aspect: "portrait",
        resolution: "720p",
        seconds: sc.seconds,
        mode: "ingredients",
        count: 1,
        images: [CH_1],
      });
      const buf = extractVidBuf(res);
      if (buf && buf.length > 300000) {
        fs.writeFileSync(sc.outPath, buf);
        console.log(`[DONE TALKING SCENE] ${sc.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: sc.id, ok: true };
      }
      console.warn(`[WARN] ${sc.id} try ${attempt}:`, res?.error || `small buf ${buf?.length}`);
    } catch (e) {
      console.warn(`[ERR] ${sc.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 4000));
  }
  return { id: sc.id, ok: false };
}

(async () => {
  const t0 = Date.now();
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  // Run all 3 scenes sequentially (1 tab at a time -> 0% tab collision, 0% gallery mix-up!)
  const results = [];
  for (const sc of SCENES) {
    results.push(await runScene(sc));
  }
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  const okCnt = results.filter((r) => r.ok).length;
  console.log(`=== TALKING SCENES COMPLETED: ${okCnt}/${SCENES.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCnt === SCENES.length ? 0 : 1);
})();
