/**
 * Pure Single-File Reference ChatGPT HTPM Generator (0% <input multiple> error!)
 * Generates: NEW_BODY_ANCHOR + STYLE_02 + STYLE_03 + STYLE_04
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\Build_Chi_Hau_2611";
const OUT_DIR = path.join(WORK_DIR, "Clean_Validated");
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
  return { name, mime: "image/jpeg", base64: buf.toString("base64") };
}

const REF_BODY_SWAP = loadImg(path.join(WORK_DIR, "SINGLE_REF_BODY_SWAP.jpg"), "body_swap_ref.jpg");
const REF_HAU_FULL = loadImg(path.join(WORK_DIR, "SINGLE_REF_HAU_FULL_IDENTITY.jpg"), "chi_hau_master_ref.jpg");

const JOBS = [
  {
    id: "NEW_BODY_ANCHOR",
    ratio: "9:16",
    ref: REF_BODY_SWAP,
    outPath: path.join(OUT_DIR, "NEW_BODY_ANCHOR.png"),
    prompt:
      "Generate ONE single full-bleed vertical 9:16 photorealistic portrait (DO NOT output a split-screen or 2-panel image!). " +
      "Recreate the exact three-quarter thigh-up standing portrait shown on the RIGHT side of body_swap_ref.jpg — wearing the exact white-and-blue floral silk short-sleeve pajama set in the warm cozy luxury modern bedroom, keeping 100% her exact feminine curvy-slender hourglass waist, bust, hips, toned slender arms, and shapely smooth thighs — while seamlessly replacing the blank beige oval head with 100% the exact head, face, expressive dark-brown eyes, softly arched brows, warm coral-rose closed-lip gentle smile, delicate gold pendant necklace, and shoulder-length layered dark-chestnut bob hair of the Vietnamese woman shown on the LEFT side of body_swap_ref.jpg. " +
      "Remove the old long wavy hair strands over her right chest so ONLY her clean shoulder-length layered dark-chestnut bob hair is present, with natural seamless neck and fair luminous skin integration. Canon EOS R5 85mm f/2, ZERO text, ZERO watermarks.",
  },
  {
    id: "STYLE_02_CHIC_EXECUTIVE",
    ratio: "9:16",
    ref: REF_HAU_FULL,
    outPath: path.join(OUT_DIR, "STYLE_02_CHIC_EXECUTIVE.png"),
    prompt:
      "Generate ONE single full-bleed vertical 9:16 photorealistic commercial lifestyle portrait (DO NOT output a split-screen!). " +
      "Keep 100% the EXACT SAME Vietnamese woman from chi_hau_master_ref.jpg — identical facial structure, expressive dark-brown eyes, softly arched brows, balanced nose, warm coral-rose gentle closed-lip smile, luminous skin, and 100% identical feminine curvy-slender hourglass body proportions, slim waist, and graceful posture (medium-full thigh-up framing). " +
      "OUTFIT & HAIRSTYLE (Modern Executive Chic): Tailored pastel dusty-rose blazer cinched neatly at her slim waist over an ivory silk camisole and high-waisted cream tailored trousers; sleek side-parted dark-chestnut bob hair tucked neatly behind one ear revealing small pearl drop earrings and a fine gold pendant necklace. " +
      "SETTING: Bright sunlit modern office workspace with warm oak desk, closed sleek laptop, indoor green plant, and soft daylight window bokeh. Canon R5 85mm f/2, ZERO text, ZERO logos.",
  },
  {
    id: "STYLE_03_FEMININE_AFTERNOON",
    ratio: "9:16",
    ref: REF_HAU_FULL,
    outPath: path.join(OUT_DIR, "STYLE_03_FEMININE_AFTERNOON.png"),
    prompt:
      "Generate ONE single full-bleed vertical 9:16 photorealistic commercial lifestyle portrait (DO NOT output a split-screen!). " +
      "Keep 100% the EXACT SAME Vietnamese woman from chi_hau_master_ref.jpg — identical face, expressive dark-brown eyes, softly arched brows, warm coral-rose gentle smile, luminous skin, and 100% identical feminine curvy-slender hourglass body proportions, slim waist, and graceful arms (medium-full thigh-up framing). " +
      "OUTFIT & HAIRSTYLE (Youthful Cozy Afternoon Lifestyle): Flattering fitted butter-yellow square-neck ribbed knit midi dress accentuating her graceful collarbone and slim waist, layered with a soft ivory lightweight knit cardigan draped effortlessly over her forearms; airy soft C-curl dark-chestnut bob hairstyle with delicate gold hoop earrings and a thin gold bracelet, holding a clean cream ceramic mug gently with both hands. " +
      "SETTING: Warm sunlit wooden home tea corner & cozy modern living room at 3 PM golden afternoon indoor light. Canon R5 85mm f/2, ZERO text, ZERO logos.",
  },
  {
    id: "STYLE_04_RADIANT_EVENING",
    ratio: "9:16",
    ref: REF_HAU_FULL,
    outPath: path.join(OUT_DIR, "STYLE_04_RADIANT_EVENING.png"),
    prompt:
      "Generate ONE single full-bleed vertical 9:16 photorealistic commercial lifestyle portrait (DO NOT output a split-screen!). " +
      "Keep 100% the EXACT SAME Vietnamese woman from chi_hau_master_ref.jpg — identical face, expressive dark-brown eyes, softly arched brows, warm coral-rose gentle smile, luminous skin, and 100% identical feminine curvy-slender hourglass body proportions and slim waist (medium-full thigh-up framing). " +
      "OUTFIT & HAIRSTYLE (Radiant Evening / Festive Elegance): Elegant emerald-green satin silk wrap blouse with a flattering V-neckline tucked into a high-waisted champagne satin midi skirt; glamorous soft side-swept wavy bob hairstyle accented with a delicate pearl hairpin on one side and tiny diamond stud earrings. " +
      "SETTING: Warm lamp-lit upscale modern home lounge & chic vanity corner in the evening with soft golden interior bokeh. Canon R5 85mm f/2, ZERO text, ZERO logos.",
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
    console.log(`[START] ${job.id} ChatGPT HTPM (1 single ref) try ${attempt}/2...`);
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: [job.ref],
        keepChat: false,
      });
      const buf = extractImgBuf(res);
      if (buf && buf.length > 80000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE] ${job.id} via ${res.provider || "chatgpt"} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true, provider: res.provider || "chatgpt" };
      }
      console.warn(`[WARN] ${job.id} try ${attempt}:`, res?.error || `small buf ${buf?.length}`);
    } catch (e) {
      console.warn(`[ERR] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 2500));
  }
  return { id: job.id, ok: false };
}

async function runPool(items, concurrency, fn) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 2500));
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
  console.log("=== GENERATING 4 PORTRAITS ON CHATGPT HTPM WITH SINGLE-FILE COMPOSITE REFS ===");
  const res = await runPool(JOBS, 3, runJob);
  const okCount = res.filter((r) => r && r.ok).length;
  console.log(`=== COMPLETED ${okCount}/${JOBS.length} IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCount === JOBS.length ? 0 : 1);
})();
