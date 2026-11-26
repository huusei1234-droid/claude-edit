/**
 * Tạo Nhân Vật Đại Diện Mới 100% BẰNG CHATGPT (Dự án HTPM, noFallback: true):
 * Đính kèm trực tiếp 2 ẢNH GỐC NGUYÊN BẢN (KHÔNG CHE MẶT):
 *   - Ảnh 1 (anh_moi_chi_hau.jpg): Ảnh chân dung gốc sắc nét của Chị Hậu (lấy 100% phần đầu & gương mặt)
 *   - Ảnh 2 (anh_mau_cu_goc.png): Ảnh gốc nguyên bản mẫu cũ AV_MODEL_BODY_ANCHOR.png (giữ 100% tướng tá, vóc dáng, tỷ lệ cơ thể)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\Build_Chi_Hau_2611";
const OUT_DIR = path.join(WORK_DIR, "ChatGPT_2Imgs_Output");
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

function loadImg(filePath, name) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  return { name, mime, base64: buf.toString("base64") };
}

// 2 Ảnh gốc sạch 100% (không che mặt): Ảnh 1 = Chị Hậu mới, Ảnh 2 = Mẫu cũ dáng chuẩn nguyên bản
const IMG_NEW_HAU = loadImg(path.join(WORK_DIR, "HAU_STUDIO_PORTRAIT_SRGB.jpg"), "anh_1_chi_hau_moi.jpg");
const IMG_OLD_MODEL = loadImg(path.join(WORK_DIR, "OLD_BODY_ORIGINAL.png"), "anh_2_mau_cu_goc.png");

const BASE_2IMG_INSTRUCTION =
  "I have attached TWO original unedited reference photos:\n" +
  "- Photo 1 (anh_1_chi_hau_moi.jpg — woman in cream blazer with shoulder-length dark-chestnut bob hair): Use 100% ONLY HER HEAD & FACE IDENTITY — exact eyes, double eyelids, eyebrows, nose, cheekbones, warm coral-rose closed-lip gentle smile, and facial structure. NEVER use the face from Photo 2.\n" +
  "- Photo 2 (anh_2_mau_cu_goc.png — woman standing in floral silk pajama set): Use 100% HER EXACT BODY PROPORTIONS, STATURE & FIGURE — exact tall graceful posture, slender toned arms, defined slim waist, feminine bust and hips, shapely smooth legs, and luminous fair skin tone blended seamlessly with Photo 1's neck and face.\n" +
  "Photorealistic Canon EOS R5 85mm f/2 commercial lifestyle portrait, ZERO text, ZERO watermarks, ZERO logos.\n\n";

const JOBS = [
  {
    id: "NEW_BODY_ANCHOR",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "NEW_BODY_ANCHOR.png"),
    prompt:
      BASE_2IMG_INSTRUCTION +
      "SCENE (MASTER BODY ANCHOR — DIRECT HEAD REPLACEMENT ON PHOTO 2): Recreate Photo 2's exact three-quarter thigh-up standing pose, feminine curvy-slender hourglass body, white-and-blue floral silk short-sleeve pajama set, and warm luxury modern bedroom background, replacing ONLY Photo 2's head and long hair with Photo 1's exact head, face, warm coral-rose smile, delicate gold pendant necklace, and shoulder-length layered dark-chestnut bob hair (relaxing her right hand naturally near her shoulder/collarbone).",
  },
  {
    id: "STYLE_01_SPORTY_TENNIS",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_01_SPORTY_TENNIS.png"),
    prompt:
      BASE_2IMG_INSTRUCTION +
      "SCENE (DAILY STYLE 1 — ENERGETIC MORNING PILATES / TENNIS CHIC): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact head/face on Photo 2's exact slim-waisted feminine hourglass figure and shapely legs. " +
      "OUTFIT & HAIRSTYLE: Sleek fitted pastel sage-green zip active top over a white sports tank paired with a high-waisted crisp white pleated tennis skort, sporty chic half-up dark-chestnut bob hairstyle with a minimalist white hair clip, tiny silver stud earrings, slim smartwatch. " +
      "SETTING: Bright sunlit modern apartment living room & morning wellness corner with sheer white curtains and indoor greenery.",
  },
  {
    id: "STYLE_02_CHIC_EXECUTIVE",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_02_CHIC_EXECUTIVE.png"),
    prompt:
      BASE_2IMG_INSTRUCTION +
      "SCENE (DAILY STYLE 2 — MODERN EXECUTIVE / PHARMACIST-CHIC OFFICE): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact head/face on Photo 2's exact slim-waisted feminine hourglass figure. " +
      "OUTFIT & HAIRSTYLE: Tailored pastel dusty-rose blazer neatly belted/fitted at her slim waist over an ivory silk camisole and high-waisted cream tailored trousers, sleek side-parted dark-chestnut bob tucked behind one ear revealing pearl drop earrings and a fine gold pendant necklace. " +
      "SETTING: Bright sunlit modern corporate office workspace with warm oak desk, sleek laptop, and soft daylight window bokeh.",
  },
  {
    id: "STYLE_03_COZY_AFTERNOON",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_03_COZY_AFTERNOON.png"),
    prompt:
      BASE_2IMG_INSTRUCTION +
      "SCENE (DAILY STYLE 3 — YOUTHFUL COZY AFTERNOON LIFESTYLE): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact head/face on Photo 2's exact feminine hourglass figure and graceful toned arms. " +
      "OUTFIT & HAIRSTYLE: Flattering fitted butter-yellow square-neck ribbed knit midi dress paired with a lightweight ivory knit cardigan draped softly over her forearms, airy soft C-curl chestnut bob hairstyle with delicate gold hoop earrings, holding a clean cream ceramic mug gently. " +
      "SETTING: Warm sunlit wooden home tea corner & cozy modern living room at 3 PM golden afternoon light.",
  },
  {
    id: "STYLE_04_RADIANT_EVENING",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_04_RADIANT_EVENING.png"),
    prompt:
      BASE_2IMG_INSTRUCTION +
      "SCENE (DAILY STYLE 4 — RADIANT EVENING / FESTIVE ELEGANCE): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact head/face on Photo 2's exact feminine hourglass silhouette and slim waist. " +
      "OUTFIT & HAIRSTYLE: Elegant emerald-green satin silk wrap blouse with a flattering V-neckline tucked into a high-waisted champagne silk midi skirt, glamorous soft side-swept wavy bob accented with a delicate pearl hairpin on one side and tiny diamond stud earrings. " +
      "SETTING: Warm lamp-lit upscale home lounge & chic vanity corner in the evening with soft golden interior bokeh.",
  },
];

function extractImgBuf(res) {
  const b64 = res?.data || res?.items?.[0]?.data || res?.items?.[0]?.base64 || res?.images?.[0]?.base64 || res?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  if (b64 instanceof Uint8Array || Array.isArray(b64)) return Buffer.from(b64);
  return Buffer.from(String(b64).replace(/^data:image\/\w+;base64,/, ""), "base64");
}

async function runJob(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 80000) {
    console.log(`[SKIP] ${job.id} cached`);
    return { id: job.id, ok: true, provider: "cached" };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START CHATGPT ONLY] ${job.id} (2 clean refs: New Hậu + Old Model) try ${attempt}/2...`);
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: [IMG_NEW_HAU, IMG_OLD_MODEL],
        keepChat: false,
        noFallback: true, // CHỈ DÙNG CHATGPT 100%, TUYỆT ĐỐI KHÔNG NHẢY SANG FLOW!
      });
      const buf = extractImgBuf(res);
      if (res?.ok && buf && buf.length > 80000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE CHATGPT] ${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true, provider: "chatgpt" };
      }
      console.warn(`[WARN CHATGPT] ${job.id} try ${attempt}:`, res?.error || `buf=${buf?.length}`);
    } catch (e) {
      console.warn(`[ERR CHATGPT] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3000));
  }
  return { id: job.id, ok: false };
}

async function runPool(items, concurrency, fn) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 3000));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

(async () => {
  const t0 = Date.now();
  console.log("=== PURE CHATGPT (2 CLEAN IMAGES: NEW CHI HAU + OLD MODEL ORIGINAL) ===");
  const res = await runPool(JOBS, 3, runJob);
  const okCount = res.filter((r) => r && r.ok).length;
  console.log(`=== CHATGPT COMPLETED ${okCount}/${JOBS.length} IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
  process.exit(okCount === JOBS.length ? 0 : 1);
})();
