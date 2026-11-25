/**
 * Tạo 5 ẢNH MẪU 1:1 BỐI CẢNH TP. NHA TRANG cho BỘ 5 BÀI THIẾT KẾ TEXT CỰC TO (AN VƯỢNG PHARMA):
 * Khóa 100% khuôn mặt Bé Mẫu (1 ref AV_MODEL_MASTER_SHEET.jpg -> ChatGPT HTPM 3 tab song song, tự xóa chat tạm).
 * Cả 5 ảnh đều đặt nhân vật gọn BÊN PHẢI (58%–94%), để trống HOÀN TOÀN NỬA TRÁI sáng trong sạch đẹp để ghép Text To + Hộp thật IS-Net!
 * 1. NT_DES1_BOJOMI_BEACH_RUN: Đồ chạy bộ xanh lục bảo × trắng kem trên đường biển Trần Phú Nha Trang (hàng dừa & biển xanh vịnh Nha Trang)
 * 2. NT_DES2_COMBO_KID1Y_BALCONY: Đầm sơ mi linen trắng kem nơ xanh pastel trên ban công căn hộ hướng vịnh biển Nha Trang
 * 3. NT_DES3_2TEMP_KITCHEN_SEA: Áo blouse xanh bơ sage × váy kem trong bếp sáng căn hộ cửa sổ nhìn ra biển Nha Trang
 * 4. NT_DES4_PROTEIN_YOGA_BAY: Set tập Pilates/Yoga xanh thiên thanh trên ban công kính hướng biển bình minh Nha Trang
 * 5. NT_DES5_COMBO4SP_SUNSET_LOUNGE: Đầm lụa satin champagne/đỏ rượu vang bên cửa kính hoàng hôn vịnh biển Nha Trang
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const MODEL_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc";
const OUT_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_5_Bai_Thiet_Ke_Nha_Trang\\01_ChatGPT_Assets";
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
  "Keep the EXACT SAME young Vietnamese woman (25-27 years old, living in sunny Nha Trang coastal city) from the attached reference photo av_model_master.jpg with 100% identical facial features, expressive dark-brown eyes, soft brows, gentle rosy smile, luminous fair skin, and slender graceful proportions. ";

const LAYOUT_1x1 =
  "Square 1:1 luxury commercial campaign layout. Position her cleanly on the RIGHT HALF of the frame (58% to 94% horizontally) smiling warmly toward camera. " +
  "Leave the ENTIRE LEFT HALF of the image bright, luminous, uncluttered airy negative space ready for giant Vietnamese bold typography and real product box compositing. " +
  "85mm f/2.0 commercial editorial photography, crisp realistic skin, ZERO text, ZERO letters, ZERO brand logos, ZERO product boxes, ZERO watermarks.";

const JOBS = [
  {
    id: "NT_DES1_BOJOMI_BEACH_RUN",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "NT_DES1_BOJOMI_BEACH_RUN.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas with a STUNNING NHA TRANG BEACHFRONT RUNNING LOOK: sleek ivory-white ribbed half-zip athletic running top + emerald-green pleated running skort, high bouncy ponytail with ivory ribbon, pearl stud earrings, white GPS running watch, holding a warm ceramic travel cup lightly. " +
      "BACKGROUND: iconic Tran Phu beachfront jogging boulevard in Nha Trang at golden sunrise, swaying tropical coconut palm trees, turquoise ocean bay and soft golden morning sky bokeh behind. " +
      LAYOUT_1x1,
  },
  {
    id: "NT_DES2_COMBO_KID1Y_BALCONY",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "NT_DES2_COMBO_KID1Y_BALCONY.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas with a WARM MODERN NHA TRANG MOM LOOK: chic ivory-cream belted linen midi shirt dress with delicate pearl buttons, soft half-up wavy hair with pastel-blue silk bow, small pearl earrings, dainty gold necklace, slim cream wristwatch. " +
      "BACKGROUND: bright airy modern high-rise family apartment living room in Nha Trang with floor-to-ceiling glass balcony doors opening to sparkling turquoise Nha Trang ocean bay, sunlit sheer white curtains gently billowing in sea breeze, warm natural oak touches. " +
      LAYOUT_1x1,
  },
  {
    id: "NT_DES3_2TEMP_KITCHEN_SEA",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "NT_DES3_2TEMP_KITCHEN_SEA.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas with a FRESH SUNLIT NHA TRANG KITCHEN LOOK: feminine pastel butter-yellow square-neck knit top tucked into crisp white wide-leg trousers, youthful half-up top bun with airy bangs, mini gold hoop earrings, delicate gold leaf necklace, holding a clean clear glass of creamy white milk gently. " +
      "BACKGROUND: sunlit white-marble coastal apartment kitchen in Nha Trang with bright wide windows overlooking palm trees and turquoise Nha Trang sea bay in soft luminous bokeh. " +
      LAYOUT_1x1,
  },
  {
    id: "NT_DES4_PROTEIN_YOGA_BAY",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "NT_DES4_PROTEIN_YOGA_BAY.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas with a CHIC NHA TRANG MORNING PILATES LOOK: fitted soft sky-blue ribbed athletic tank top paired with high-waisted crisp-white sports leggings, sleek sporty braided ponytail, tiny silver stud earrings, light-blue fitness smartwatch, holding a clear glass of smooth creamy plant protein shake. " +
      "BACKGROUND: sun-drenched luxury ocean-view glass balcony & minimalist morning wellness terrace overlooking sparkling Nha Trang bay with swaying palm silhouettes and golden morning sunlight. " +
      LAYOUT_1x1,
  },
  {
    id: "NT_DES5_COMBO4SP_SUNSET_LOUNGE",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "NT_DES5_COMBO4SP_SUNSET_LOUNGE.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas with a GLAMOROUS NHA TRANG GOLDEN-HOUR EVENING LOOK: elegant deep champagne-rose satin silk midi dress with delicate draped neckline, voluminous glossy dark-chestnut loose curls with pearl hairpin, sparkling crystal-flower earrings, dainty diamond-drop necklace. " +
      "BACKGROUND: luxury coastal penthouse terrace in Nha Trang at luminous pastel golden-hour twilight overlooking the sparkling Nha Trang bay coastline and soft warm fairy bokeh lights. " +
      LAYOUT_1x1,
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

async function runPool(items, concurrency) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 2500));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await runOne(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

(async () => {
  const t0 = Date.now();
  const res = await runPool(JOBS, 3);
  const ok = res.filter((r) => r && r.ok).length;
  console.log(`\n=== 5 NHA TRANG DESIGN LOOKS DONE: ${ok}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(res, null, 2));
  process.exit(ok === JOBS.length ? 0 : 1);
})();
