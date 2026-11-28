/**
 * Tạo 5 ẢNH CHÂN DUNG 1:1 CHỊ HẰNG (AN VƯỢNG PHARMA — NGÀY 28/11/2026)
 * - Khóa cứng 100% gương mặt gốc Chị Hằng (`CHI_HANG_FACE_CROP_CHUAN.jpg`)
 *   + 100% vóc dáng đồng hồ cát chuẩn An Vượng (`AV_BODY_COLLARBONE_DOWN.jpg`, 0% mặt mẫu cũ)
 * - Chạy song song 3 Tab ChatGPT Plus (`Dự án HTPM`, `noFallback: true`, `keepChat: false`)
 * - 5 bộ trang phục & bối cảnh sinh hoạt đời thường khác nhau 100%, Chị Hằng nằm gọn NỬA PHẢI (58–94%),
 *   NỬA TRÁI thoáng sáng trong trẻo để ghép Text To + Hộp thật IS-Net 100%, 0% Bling-Bling!
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const ANCHOR_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\Build_Mau_Moi_2711";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_05_2811_5_Thiet_Ke";
const OUT_DIR = path.join(WORK_DIR, "01_ChatGPT_Portraits_1x1");
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

const IMG_HANG_FACE = loadImg(path.join(ANCHOR_DIR, "CHI_HANG_FACE_CROP_CHUAN.jpg"), "source_1_mat_chi_hang.jpg");
const IMG_BODY_NECK_DOWN = loadImg(path.join(ANCHOR_DIR, "AV_BODY_COLLARBONE_DOWN.jpg"), "source_2_dang_co_tro_xuong.jpg");

const CORE_LOCK =
  "I have attached TWO clean reference photos:\n" +
  "- Photo 1 (source_1_mat_chi_hang.jpg — real headshot of Chị Hằng): CRITICAL IDENTITY LOCK — Preserve 100.0% HER EXACT REAL FACE & LIKENESS! Keep her exact ~36-year-old graceful Vietnamese woman facial structure, natural soft rounded-oval cheeks and gentle jawline (DO NOT slim her jaw into a sharp V-chin, DO NOT de-age her into a 20-year-old idol, DO NOT swap or genericize her face!), her exact rounded nose tip, expressive warm dark-brown eyes, natural arched dark eyebrows, warm coral-red lips with her signature bright toothy smile, fair luminous skin, and lush side-parted dark-brown wavy hair.\n" +
  "- Photo 2 (source_2_dang_co_tro_xuong.jpg — headless collarbone-down body reference): Use 100% THIS EXACT SLENDER HOURGLASS BODY PROPORTION & SILHOUETTE — toned arms, slim defined waist, graceful feminine posture, seamlessly matching Photo 1's fair porcelain neck and skin tone.\n" +
  "COMPOSITION (MANDATORY): Square 1:1 luxury commercial campaign layout. Position Chị Hằng cleanly on the RIGHT HALF of the square frame (58% to 94% horizontally, medium waist-up/hip-up portrait), facing warmly toward the camera. " +
  "Leave the ENTIRE LEFT HALF (0% to 52% horizontally) bright, airy, luminous, clean uncluttered negative space with soft natural daylight bokeh ready for bold Vietnamese typography and real product box compositing. " +
  "Canon EOS R5 85mm f/2.0 crisp commercial editorial daylight photography, natural skin texture, ZERO sparkles, ZERO glitter, ZERO bling-bling effects, ZERO text, ZERO letters, ZERO brand logos, ZERO product boxes, ZERO watermarks.\n\n";

const JOBS = [
  {
    id: "D01_COMBO4_IVORY_BLAZER",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "D01_COMBO4_IVORY_BLAZER.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "STYLE 01 (Executive Celebration — 2 Final Days Droppii Birthday & Top Partner Appreciation): " +
      "OUTFIT: Tailored ivory-cream structured blazer with delicate pearl buttons worn over a luminous white satin silk camisole, dainty pearl drop earrings, slim gold wristwatch, lush side-parted glossy dark-brown wavy hair. " +
      "POSE: Positioned cleanly on the right side (58%–94%), smiling warmly and confidently toward camera with graceful poised executive posture beside a sleek white-marble desk. " +
      "BACKGROUND: Bright airy sunlit modern executive studio interior with warm oak accents, sheer white curtains, soft green indoor foliage in luminous bokeh, and clean bright ivory-cream negative space filling the entire left half.",
  },
  {
    id: "D02_AVPROTEIN_SAGE_MORNING",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "D02_AVPROTEIN_SAGE_MORNING.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "STYLE 02 (Fresh Active Morning — Healthy Plant-Protein Breakfast & Muscle Retention): " +
      "OUTFIT: Fitted pastel sage-green zip-up athletic wellness jacket worn open over a crisp white scoop-neck tank top and high-waisted white pleated athletic skort accentuating her slim waist, youthful half-up dark-brown wavy hair with a minimal white pearl clip, tiny gold stud earrings. " +
      "POSE: Positioned cleanly on the right side (58%–94%), holding a clean transparent glass of smooth creamy beige plant protein shake naturally near chest level, smiling brightly toward camera. " +
      "BACKGROUND: Bright sun-drenched modern Vietnamese home kitchen with white marble breakfast counter, morning sunlight streaming through sheer curtains, and clean airy cream-white negative space on the entire left half.",
  },
  {
    id: "D03_BOJOMI_POLO_FAMILY",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "D03_BOJOMI_POLO_FAMILY.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "STYLE 03 (Warm Family Nutrition — Adult & Parents Daily Calcium Meal): " +
      "OUTFIT: Chic fitted ivory fine-knit short-sleeve polo top with subtle emerald-green collar and cuff trim neatly tucked into high-waisted warm sand-beige tailored trousers, glossy side-parted dark-brown waves tucked softly behind one ear with a tiny gold hairpin, slim silver wristwatch. " +
      "POSE: Positioned cleanly on the right side (58%–94%), gently holding a clean clear glass mug of warm creamy ivory vanilla cereal milk with a relaxed inviting smile toward camera. " +
      "BACKGROUND: Warm sunlit modern Vietnamese family dining room with light oak wooden table, sunlit airy window, soft indoor plants in bokeh, and clean luminous cream-white negative space filling the entire left half.",
  },
  {
    id: "D04_CURCUMILK_EMERALD_OFFICE",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "D04_CURCUMILK_EMERALD_OFFICE.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "STYLE 04 (Signature Emerald Expert — Warm Soothing Turmeric Milk for Heavy Speakers & Busy Workdays): " +
      "OUTFIT: Signature structured emerald-teal tailored blazer with delicate gold buttons at the cuffs worn over a champagne-ivory satin camisole, small gold hoop earrings, classic watch, glossy side-parted dark-brown wavy hair over shoulders. " +
      "POSE: Positioned cleanly on the right side (58%–94%), holding a warm minimalist ivory ceramic mug filled with smooth golden-yellow creamy turmeric vanilla milk lightly near chest level, smiling warmly toward camera. " +
      "BACKGROUND: Bright airy sunlit home study and workspace with warm light-oak shelves, indoor green potted plants, sunlit sheer white drapes, and clean bright warm-cream negative space across the entire left half.",
  },
  {
    id: "D05_COLLAMELA_BLUSH_SILK",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "D05_COLLAMELA_BLUSH_SILK.png"),
    images: [IMG_HANG_FACE, IMG_BODY_NECK_DOWN],
    prompt:
      CORE_LOCK +
      "STYLE 05 (Radiant Year-End Skin Care — Peach Collagen Tripeptide Ritual): " +
      "OUTFIT: Elegant pastel blush-rose satin silk wrap blouse with gentle draped V-neckline tucked into a high-waisted champagne-ivory satin midi skirt, glossy voluminous dark-brown wavy hair adorned with a dainty pearl hairpin, delicate rose-gold drop earrings. " +
      "POSE: Positioned cleanly on the right side (58%–94%), gracefully raising a clean transparent crystal glass of translucent pastel peach-pink collagen drink near shoulder level, glowing natural smile toward camera. " +
      "BACKGROUND: Bright luminous sunlit modern dressing lounge and tea table with soft ivory drapes, subtle fresh blush-pink roses out of focus, and clean airy blush-ivory negative space across the entire left half.",
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
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 100000) {
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
      if (res?.ok && buf && buf.length > 100000) {
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
  console.log("=== GENERATING 5 UNIQUE 1:1 CHI HANG PORTRAITS (28/11) VIA CHATGPT PLUS (3 PARALLEL TABS) ===");
  const res = await runPool(JOBS, 3, runJob);
  await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
  const okCnt = res.filter((r) => r && r.ok).length;
  console.log(`=== COMPLETED ${okCnt}/${JOBS.length} IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCnt === JOBS.length ? 0 : 1);
})();
