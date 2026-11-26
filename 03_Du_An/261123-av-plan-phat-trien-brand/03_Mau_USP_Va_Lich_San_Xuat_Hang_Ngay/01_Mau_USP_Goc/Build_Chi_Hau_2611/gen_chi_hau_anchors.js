/**
 * Generate Master Body Anchor (Head = Chị Hậu 100%, Body = Old Model Figure 100%)
 * + 4 Vibrant Multi-Style Daily Lookbook Portraits via ChatGPT HTPM on Brave :9333
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\Build_Chi_Hau_2611";
const OUT_DIR = path.join(WORK_DIR, "Generated_Anchors_And_Styles");
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

const REF_HEAD = loadImg(path.join(WORK_DIR, "HAU_DUAL_HEAD_IDENTITY.jpg"), "chi_hau_head_identity.jpg");
const REF_BODY = loadImg(path.join(WORK_DIR, "OLD_BODY_PROPORTION_ONLY.jpg"), "body_proportion_template.jpg");

const CORE_FUSION_RULE =
  "STRICT HEAD-TO-BODY FUSION LOCK: " +
  "1) HEAD & FACE IDENTITY (100% FROM IMAGE 1 chi_hau_head_identity.jpg): Use the EXACT Vietnamese woman's head and face from Image 1 — identical expressive dark-brown eyes with natural double eyelids, softly arched brows, balanced nose bridge, soft natural cheekbones, warm coral-rose closed-lip gentle smile, and luminous natural skin. Do NOT alter, de-age into a generic doll, or change her facial identity. " +
  "2) BODY PROPORTIONS & FIGURE (100% FROM IMAGE 2 body_proportion_template.jpg): Use the EXACT feminine curvy-slender hourglass body proportions from Image 2 — tall graceful posture, toned slender arms, defined slim waist, feminine bust and hips, shapely smooth legs, and fair luminous skin matching her face seamlessly at the neck. " +
  "3) ZERO text, ZERO watermarks, ZERO logos, ZERO product boxes. Canon EOS R5 85mm f/2 photorealistic commercial lifestyle photography. ";

const JOBS = [
  {
    id: "NEW_BODY_ANCHOR",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "NEW_BODY_ANCHOR.png"),
    prompt:
      CORE_FUSION_RULE +
      "EXACT MASTER BODY ANCHOR REPLACEMENT: Recreate the exact three-quarter thigh-up standing portrait from Image 2 (body_proportion_template.jpg) in the same white-and-blue floral silk short-sleeve pajama set and warm cozy luxury modern bedroom background, replacing the beige-masked head cleanly with 100% the exact head, face, warm coral smile, delicate gold pendant necklace, and shoulder-length layered dark-chestnut bob hair of the woman in Image 1 (chi_hau_head_identity.jpg). Remove any old long hair strands over the chest so ONLY her clean shoulder-length layered chestnut bob hair is present; relax her right hand naturally near her collarbone/shoulder.",
  },
  {
    id: "STYLE_01_SPORTY_ACTIVE",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_01_SPORTY_ACTIVE.png"),
    prompt:
      CORE_FUSION_RULE +
      "DAILY STYLE 1 — ENERGETIC MORNING PILATES / TENNIS CHIC: Medium-full three-quarter vertical 9:16 portrait (thigh-up framing showing her exact slim waist and shapely toned figure from Image 2). " +
      "OUTFIT & HAIRSTYLE: Sleek fitted pastel sage-green activewear zip jacket (zipped halfway over a crisp white sports tank) paired with a high-waisted white pleated tennis skort, sporty chic half-up bob hairstyle secured with a minimalist white claw clip, tiny silver stud earrings, slim Apple/smart fitness watch. " +
      "SETTING: Bright sunlit modern Vietnamese apartment living room & morning wellness corner with sheer white curtains and indoor greenery.",
  },
  {
    id: "STYLE_02_CHIC_EXECUTIVE",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_02_CHIC_EXECUTIVE.png"),
    prompt:
      CORE_FUSION_RULE +
      "DAILY STYLE 2 — MODERN EXECUTIVE / PHARMACIST-CHIC OFFICE: Medium-full three-quarter vertical 9:16 portrait (thigh-up framing accentuating her graceful slim-waisted hourglass proportions from Image 2). " +
      "OUTFIT & HAIRSTYLE: Tailored pastel dusty-rose blazer neatly belted/fitted at her slim waist over an ivory silk camisole and high-waisted cream tailored trousers, sleek side-parted dark-chestnut bob tucked behind one ear revealing small pearl drop earrings and a fine gold pendant necklace. " +
      "SETTING: Sunlit modern upscale office workspace with warm oak desk, sleek laptop, and soft city window bokeh.",
  },
  {
    id: "STYLE_03_FEMININE_AFTERNOON",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_03_FEMININE_AFTERNOON.png"),
    prompt:
      CORE_FUSION_RULE +
      "DAILY STYLE 3 — YOUTHFUL COZY AFTERNOON LIFESTYLE: Medium-full three-quarter vertical 9:16 portrait (thigh-up framing showcasing her slender waist, graceful collarbone, and feminine figure from Image 2). " +
      "OUTFIT & HAIRSTYLE: Flattering fitted butter-yellow square-neck ribbed knit midi dress with a lightweight ivory knit cardigan draped effortlessly over her forearms, airy soft C-curl chestnut bob hairstyle with delicate gold hoop earrings and thin gold bracelet, holding a clean cream ceramic mug gently. " +
      "SETTING: Warm sunlit wooden home tea corner & cozy living room at 3 PM golden afternoon indoor light.",
  },
  {
    id: "STYLE_04_RADIANT_EVENING",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_04_RADIANT_EVENING.png"),
    prompt:
      CORE_FUSION_RULE +
      "DAILY STYLE 4 — RADIANT EVENING / FESTIVE ELEGANCE: Medium-full three-quarter vertical 9:16 portrait (thigh-up framing highlighting her poised hourglass silhouette from Image 2). " +
      "OUTFIT & HAIRSTYLE: Elegant emerald-green satin wrap blouse with a flattering V-neckline tucked into a high-waisted champagne silk midi skirt, glamorous soft side-swept wavy bob accented with a delicate pearl hairpin on one side and tiny diamond earrings. " +
      "SETTING: Warm lamp-lit modern home lounge & chic vanity corner in the evening with soft golden interior bokeh.",
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
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 50000) {
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
        images: [REF_HEAD, REF_BODY],
        keepChat: false,
      });
      const buf = extractImgBuf(res);
      if (buf && buf.length > 30000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE] ${job.id} via ${res.provider || "chatgpt"} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true, provider: res.provider || "chatgpt" };
      }
      console.warn(`[WARN] ${job.id} try ${attempt}:`, res?.error || "empty");
    } catch (e) {
      console.warn(`[ERR] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 2500));
  }
  console.log(`[FALLBACK] ${job.id} -> Google Flow...`);
  try {
    const res = handlers["flow:generate-image"]
      ? await handlers["flow:generate-image"](null, {
          prompt: job.prompt,
          aspect: "portrait",
          count: 1,
          images: [REF_HEAD, REF_BODY],
        })
      : await flow.generateImageFallback({
          prompt: job.prompt,
          ratio: job.ratio,
          count: 1,
          images: [REF_HEAD, REF_BODY],
        });
    const buf = extractImgBuf(res);
    if (buf && buf.length > 30000) {
      fs.writeFileSync(job.outPath, buf);
      console.log(`[DONE] ${job.id} via Flow -> ${(buf.length / 1024).toFixed(0)} KB`);
      return { id: job.id, ok: true, provider: "flow" };
    }
  } catch (e) {
    console.error(`[ERR FLOW] ${job.id}:`, e?.message || e);
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
  console.log("=== GENERATING CHI HAU BODY ANCHOR + 4 MULTI-STYLE LOOKBOOK PORTRAITS ===");
  const res = await runPool(JOBS, 3, runJob);
  const okCount = res.filter((r) => r && r.ok).length;
  console.log(`=== COMPLETED ${okCount}/${JOBS.length} IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCount === JOBS.length ? 0 : 1);
})();
