/**
 * Tạo 2 DIỆN MẠO MẸ TRẺ HIỆN ĐẠI CỰC ĐẸP cho BỘ 2 VIDEO COMBO CHIỀU CAO BÉ TỪ 1 TUỔI (BOJOMI + AV PROTEIN):
 * - Look M1 (Blush Pink Shirt Dress): Đầm sơ mi midi hồng phấn pastel thắt eo + tóc buộc nửa kẹp nơ lụa kem + ngọc trai + phòng khách nắng ấm
 * - Look M2 (Sage Green Puff Blouse): Áo blouse tay bồng xanh bơ sage + chân váy xếp ly trắng kem + búi thấp Hàn Quốc + khuyên tròn vàng + bếp sáng nắng
 * Khóa 100% khuôn mặt Bé Mẫu từ AV_MODEL_MASTER_SHEET.jpg -> ChatGPT HTPM (2 tab song song, tự xóa chat tạm).
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const MODEL_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc";
const OUT_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_2_Video_Chieu_Cao_Be_Tu_1_Tuoi\\01_ChatGPT_Assets";
fs.mkdirSync(OUT_DIR, { recursive: true });

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
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));
flow.setup({ getPath: () => DATA_DIR });
chatgpt.setup({ getPath: () => DATA_DIR });

const MASTER_BUF = fs.readFileSync(path.join(MODEL_DIR, "AV_MODEL_MASTER_SHEET.jpg"));
const REF_MASTER = { name: "av_model_master.jpg", mime: "image/jpeg", base64: MASTER_BUF.toString("base64") };

const FACE_LOCK =
  "Keep the EXACT SAME young Vietnamese woman (26-28 years old) from the attached reference photo av_model_master.jpg with 100% identical facial features, expressive dark-brown eyes, soft brows, gentle rosy radiant smile, luminous fair skin, and slender graceful proportions. ";

const JOBS = [
  {
    id: "KID1Y_LOOK1_BLUSH_DRESS_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "KID1Y_LOOK1_BLUSH_DRESS_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a WARM RADIANT MODERN YOUNG MOM LOOK #1 (PASTEL BLUSH PINK & IVORY): " +
      "OUTFIT: a chic tailored pastel blush-pink cotton-linen belted midi shirt dress with rolled elbow sleeves and subtle pearl buttons. " +
      "HAIRSTYLE: glossy chestnut hair styled in soft half-up loose waves secured with a delicate ivory silk bow ribbon and soft wispy bangs. " +
      "ACCESSORIES: delicate small pearl stud earrings, a dainty 18K gold minimal chain necklace, and a slim white-strap gold-trim wristwatch. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter warm family-home portrait in a bright sunlit Scandinavian living room with warm natural oak floor, pastel wooden kids height-chart & neat wooden toys softly blurred in background, golden morning sunbeams streaming through sheer white curtains. She smiles warmly and tenderly toward camera full of loving modern-mom elegance. " +
      "85mm f/2.0 luxury lifestyle commercial photography, crisp realistic skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
  {
    id: "KID1Y_LOOK2_SAGE_BLOUSE_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "KID1Y_LOOK2_SAGE_BLOUSE_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a FRESH SUNLIT MODERN MOM KITCHEN LOOK #2 (SOFT SAGE GREEN & CRISP IVORY): " +
      "OUTFIT: a feminine soft sage-green round-neck short puff-sleeve cotton blouse tucked neatly into a flowy crisp-ivory pleated midi skirt. " +
      "HAIRSTYLE: glossy chestnut hair styled in a neat chic low Korean chignon bun with soft airy face-framing bangs. " +
      "ACCESSORIES: delicate mini polished gold hoop earrings, a fine dainty gold flower-charm necklace, and a slim beige-leather wristwatch. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter portrait standing gracefully beside a bright sunlit white-marble and light-oak modern family kitchen island with fresh fruit bowl, clean glass pitcher, and golden morning sunlight sparkling softly behind. She smiles brightly and reassuringly toward camera. " +
      "85mm f/2.0 luxury editorial photography, crisp natural skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
];

function extractBuf(res) {
  const b64 = res?.data || res?.items?.[0]?.data || res?.items?.[0]?.base64 || res?.images?.[0]?.base64 || res?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  if (b64 instanceof Uint8Array) return Buffer.from(b64);
  if (Array.isArray(b64)) return Buffer.from(b64);
  return Buffer.from(String(b64).replace(/^data:image\/\w+;base64,/, ""), "base64");
}

async function runOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 100000) {
    console.log(`[SKIP] ${job.id} cached`);
    return { id: job.id, ok: true, provider: "cached" };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START] ${job.id} ChatGPT HTPM try ${attempt}/2...`);
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: [REF_MASTER],
        keepChat: false,
      });
      const buf = extractBuf(res);
      if (buf && buf.length > 30000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE] ${job.id} (${res.provider || "chatgpt"}) -> ${buf.length} bytes`);
        return { id: job.id, ok: true, provider: res.provider || "chatgpt" };
      }
      console.warn(`[WARN] ${job.id} try ${attempt}:`, res?.error || Object.keys(res || {}));
    } catch (e) {
      console.warn(`[ERR] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3000));
  }
  return { id: job.id, ok: false };
}

(async () => {
  const t0 = Date.now();
  const res = await Promise.all(JOBS.map((j, i) => new Promise((r) => setTimeout(() => r(runOne(j)), i * 2500))));
  const ok = res.filter((r) => r && r.ok).length;
  console.log(`\n=== 2 KID 1Y+ LOOKS DONE: ${ok}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(res, null, 2));
  process.exit(ok === JOBS.length ? 0 : 1);
})();
