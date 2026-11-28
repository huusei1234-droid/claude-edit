/**
 * Tạo Bộ Nhân Vật Đại Diện Chị Hằng (100% Nét Mặt Thật Chị Hằng `CHI_HANG_FACE_CROP_CHUAN.jpg`
 * + 100% Vóc Dáng Thon Gọn Đồng Hồ Cát Mẫu An Vượng `AV_BODY_COLLARBONE_DOWN.jpg` KHÔNG CÓ MẶT MẪU CŨ!)
 * Chạy 100% bằng ChatGPT Plus (Dự án HTPM, noFallback: true, keepChat: false):
 *   - 00_MASTER_BODY_ANCHOR.png: Dáng gốc An Vượng ghép mặt Chị Hằng chuẩn 100%
 *   - V01..V07: 7 Phong Cách & 7 Bộ Đồ Riêng Biệt cho 7 Video Kịch Bản
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\Build_Mau_Moi_2711";
const OUT_DIR = path.join(WORK_DIR, "Chi_Hang_8_ChatGPT_Looks");
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

// Ảnh 1: Source cận mặt Chị Hằng đã cắt chuẩn sạch (duy nhất 1 khuôn mặt trong toàn bộ input!)
// Ảnh 2: Dáng mẫu An Vượng cắt từ xương quai xanh trở xuống (0% mặt mẫu cũ -> không bao giờ pha nét mặt!)
const IMG_HANG_FACE = loadImg(path.join(WORK_DIR, "CHI_HANG_FACE_CROP_CHUAN.jpg"), "source_1_mat_chi_hang.jpg");
const IMG_BODY_NECK_DOWN = loadImg(path.join(WORK_DIR, "AV_BODY_COLLARBONE_DOWN.jpg"), "source_2_dang_co_tro_xuong.jpg");

const CORE_LOCK =
  "I have attached TWO clean reference photos:\n" +
  "- Photo 1 (source_1_mat_chi_hang.jpg — headshot of Chị Hằng): CRITICAL IDENTITY LOCK — Preserve 100.0% HER EXACT REAL FACE & LIKENESS! Keep her exact ~36-year-old graceful Vietnamese woman facial structure, natural soft rounded-oval cheeks and gentle jawline (DO NOT slim her jaw into a sharp V-chin, DO NOT de-age her into a 20-year-old K-pop idol, DO NOT genericize her face!), her exact rounded nose tip and nostrils, expressive warm dark-brown eyes, natural arched dark eyebrows, warm coral-red lips with her signature bright toothy smile, fair porcelain skin, and lush side-parted dark-brown wavy hair.\n" +
  "- Photo 2 (source_2_dang_co_tro_xuong.jpg — headless collarbone-down body reference): Use 100% THIS EXACT BODY PROPORTION & SILHOUETTE — graceful feminine hourglass figure, slender toned arms, defined slim waist, natural feminine bust and hips, seamlessly matching Photo 1's fair porcelain neck and skin tone.\n" +
  "Vertical 9:16 photorealistic Canon EOS R5 85mm f/2 editorial lifestyle portrait, natural skin texture, ZERO text, ZERO watermarks, ZERO logos.\n\n";

const JOBS = [
  {
    id: "00_MASTER_BODY_ANCHOR",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "00_MASTER_BODY_ANCHOR.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "MASTER CHARACTER ANCHOR: Seamlessly place Photo 1's exact head, exact real ~36yo Vietnamese woman face, bright toothy smile, and lush side-parted wavy dark-brown hair onto Photo 2's exact standing thigh-up hourglass body wearing the white-and-blue floral silk short-sleeve pajama set in the warm sunlit luxury modern bedroom. Her head proportion, neck connection, and porcelain skin tone must look 100% natural, realistic, and unmistakably the exact same woman as Photo 1.",
  },
  {
    id: "V01_LOOK_SPORTY_SAGE",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "V01_LOOK_SPORTY_SAGE.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "VIDEO 1 OUTFIT & STYLE (Fresh Morning Activewear — Healthy Breakfast & Protein): Medium-full thigh-up portrait of the EXACT woman from Photo 1 (100% identical soft rounded-oval face, nose, eyes, and warm smile) with Photo 2's slender hourglass waist and figure. " +
      "OUTFIT 1: Fitted pastel sage-green zip-up athletic jacket worn open over a crisp white scoop-neck tank top and high-waisted white pleated tennis skort, sporty half-up wavy dark-brown hair with a white clip, small gold stud earrings. " +
      "SETTING: Bright sunlit modern Vietnamese home kitchen & marble breakfast counter in morning daylight.",
  },
  {
    id: "V02_LOOK_ATHLEISURE_POLO",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "V02_LOOK_ATHLEISURE_POLO.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "VIDEO 2 OUTFIT & STYLE (Smart-Sporty Wellness — Strength & Muscle Tone): Medium-full thigh-up portrait of the EXACT woman from Photo 1 (100% identical real face, rounded-oval cheeks, nose, eyes, and warm smile) with Photo 2's slender hourglass figure. " +
      "OUTFIT 2: Fitted ivory fine-knit short-sleeve polo top with navy-blue collar trim neatly tucked into high-waisted sand-beige tailored wide-leg trousers accentuating her slim waist, neat high wavy ponytail with soft side bangs, slim silver wristwatch. " +
      "SETTING: Airy sunlit modern Vietnamese living room with wooden staircase softly blurred behind her.",
  },
  {
    id: "V03_LOOK_LINEN_MINT",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "V03_LOOK_LINEN_MINT.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "VIDEO 3 OUTFIT & STYLE (Minimalist Natural Home — Vegetarian Plant-Protein Meal): Medium-full thigh-up portrait of the EXACT woman from Photo 1 (100% identical real face, rounded-oval cheeks, nose, eyes, and warm smile) with Photo 2's slender hourglass figure. " +
      "OUTFIT 3: Soft pastel mint-olive short-sleeve linen button-up shirt tucked neatly into cream high-waisted linen trousers, lush side-parted dark-brown wavy hair over one shoulder, delicate gold pendant necklace. " +
      "SETTING: Warm sunlit Vietnamese wooden dining room with indoor green plants.",
  },
  {
    id: "V04_LOOK_CARDIGAN_YELLOW",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "V04_LOOK_CARDIGAN_YELLOW.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "VIDEO 4 OUTFIT & STYLE (Warm Family Elegance — Daily Calcium Sources): Medium-full thigh-up portrait of the EXACT woman from Photo 1 (100% identical real face, rounded-oval cheeks, nose, eyes, and warm smile) with Photo 2's feminine hourglass figure. " +
      "OUTFIT 4: Flattering fitted butter-yellow square-neck knit midi dress with a soft cream cardigan draped gently on her shoulders, side-parted wavy dark-brown hair tucked behind one ear with a pearl clip, small pearl stud earrings. " +
      "SETTING: Cozy bright sunlit family dining room table by a sunny window.",
  },
  {
    id: "V05_LOOK_EXECUTIVE_ROSE",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "V05_LOOK_EXECUTIVE_ROSE.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "VIDEO 5 OUTFIT & STYLE (Executive Nutritionist Chic — Reading Supplement Labels): Medium-full thigh-up portrait of the EXACT woman from Photo 1 (100% identical real face, rounded-oval cheeks, nose, eyes, and warm smile) with Photo 2's slim-waisted hourglass figure. " +
      "OUTFIT 5: Tailored pastel dusty-rose waist-cinched blazer worn over a cream silk camisole and high-waisted ivory tailored trousers, signature side-parted voluminous dark-brown wavy hair, gold hoop-stud earrings, elegant watch. " +
      "SETTING: Bright sunlit upscale wooden home study desk with soft natural daylight bokeh.",
  },
  {
    id: "V06_LOOK_SILK_EMERALD",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "V06_LOOK_SILK_EMERALD.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "VIDEO 6 OUTFIT & STYLE (Radiant Fresh Silk Chic — Guava, Vitamin C & Collagen): Medium-full thigh-up portrait of the EXACT woman from Photo 1 (100% identical real face, rounded-oval cheeks, nose, eyes, and warm smile) with Photo 2's slender hourglass silhouette. " +
      "OUTFIT 6: Elegant emerald-green satin wrap blouse with V-neckline tucked into a high-waisted champagne-cream A-line midi skirt, glossy side-parted dark-brown waves, dainty gold earrings. " +
      "SETTING: Sunlit modern kitchen counter with warm oak wood accents and fresh green foliage.",
  },
  {
    id: "V07_LOOK_CULINARY_APRON",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "V07_LOOK_CULINARY_APRON.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "VIDEO 7 OUTFIT & STYLE (Warm Home Culinary Look — Fresh Turmeric vs Curcumin): Medium-full thigh-up portrait of the EXACT woman from Photo 1 (100% identical real face, rounded-oval cheeks, nose, eyes, and warm smile) with Photo 2's slim-waisted hourglass figure. " +
      "OUTFIT 7: Clean oatmeal-beige linen kitchen apron tied neatly around her slim waist over a fitted warm terracotta-coral ribbed 3/4-sleeve top, neat low-clipped wavy dark-brown hair with soft face-framing waves, small gold earrings. " +
      "SETTING: Warm sunlit wooden home kitchen island in golden afternoon light.",
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
    return { id: job.id, ok: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START CHATGPT] ${job.id} try ${attempt}/2...`);
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: job.images,
        keepChat: false,
        noFallback: true,
      });
      const buf = extractImgBuf(res);
      if (res?.ok && buf && buf.length > 80000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE CHATGPT] ${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true };
      }
      console.warn(`[WARN] ${job.id} try ${attempt}:`, res?.error || "empty");
    } catch (e) {
      console.warn(`[ERR] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3000));
  }
  return { id: job.id, ok: false };
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
  const t0 = Date.now();
  console.log("=== GENERATING CHI HANG MASTER BODY ANCHOR + 7 UNIQUE VIDEO OUTFITS ON CHATGPT ===");
  const res = await runPool(JOBS, 3, runJob);
  await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
  const okCnt = res.filter((r) => r && r.ok).length;
  console.log(`=== COMPLETED ${okCnt}/${JOBS.length} IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCnt === JOBS.length ? 0 : 1);
})();
