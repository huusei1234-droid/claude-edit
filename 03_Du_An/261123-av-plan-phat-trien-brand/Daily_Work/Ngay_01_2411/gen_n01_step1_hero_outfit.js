/**
 * Ngày 01 (24/11/2026) — Step 1: Tạo 2 ảnh chuẩn Master Outfit (Đồ tập Pilates xanh mint pastel)
 * khóa 100% khuôn mặt & vóc dáng từ AV_MODEL_FACE_ANCHOR.png + AV_MODEL_BODY_ANCHOR.png
 * qua ChatGPT Dự án HTPM (tự động xóa chat tạm, fallback Flow/Muse).
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const MODEL_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc";
const OUT_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\01_ChatGPT_Assets";
fs.mkdirSync(OUT_DIR, { recursive: true });

// Ensure chatgpt-driver.json in DATA_DIR points to official HTPM project
const gptCfgPath = path.join(DATA_DIR, "chatgpt-driver.json");
if (!fs.existsSync(gptCfgPath)) {
  fs.writeFileSync(
    gptCfgPath,
    JSON.stringify({
      accounts: [{
        id: "gpt_htpm",
        name: "ChatGPT HTPM",
        profile: "MAIN_BRAVE",
        projectLabel: "HTPM",
        projectId: "g-p-6afbde0b943481919c6ec31a3b4f8642",
      }],
      active: "gpt_htpm",
    }, null, 2)
  );
}

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

function loadRef(filePath, name) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  return { name, mime, base64: buf.toString("base64") };
}

const REF_FACE = loadRef(path.join(MODEL_DIR, "AV_MODEL_FACE_ANCHOR.png"), "av_model_face.png");
const REF_BODY = loadRef(path.join(MODEL_DIR, "AV_MODEL_BODY_ANCHOR.png"), "av_model_body.png");

const CHAR_LOCK =
  "Keep the EXACT SAME young Vietnamese woman (25-27 years old) from the two attached reference photos (av_model_face.png and av_model_body.png) with 100% identical facial identity, eyes, eyebrows, nose, gentle rosy-coral smile, luminous natural fair skin, slender graceful figure, and long dark-chestnut wavy hair styled neatly half-up half-down flowing softly over her shoulders. ";

const OUTFIT_N01 =
  "COMPLETELY REPLACE the floral blue-and-white silk pajamas from the reference photos with a clean, classy, tasteful PASTEL MINT-SAGE PILATES ATHLEISURE SET: a fitted matte pastel mint-green sleeveless ribbed athletic tank top (modest round neckline, waist-length) paired with matching high-waisted pastel mint-green pilates leggings. ";

const JOBS = [
  {
    id: "N01_HERO_MINT_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "N01_HERO_MINT_9x16.png"),
    images: [REF_FACE, REF_BODY],
    prompt:
      CHAR_LOCK +
      OUTFIT_N01 +
      "Vertical 9:16 high-end commercial lifestyle health photography. She stands gracefully beside a sunlit white marble modern kitchen island in a bright luxury apartment with soft morning sunlight streaming through floor-to-ceiling sheer curtains, subtle indoor green plants and rolled yoga mat softly blurred in the background. " +
      "She holds a clean clear glass filled with creamy smooth vanilla-beige plant-based protein shake gently near waist/chest level with a warm radiant confident smile looking softly toward camera. " +
      "Leave generous clean bright negative space in the upper third and right side. " +
      "Shot on 85mm f/2.0 cinema lens, high-key sunlit pearl-ivory and fresh botanical wellness color palette, ultra-crisp 8K photorealistic commercial advertising photography. " +
      "STRICT NEGATIVE: ZERO text, ZERO letters, ZERO logos, ZERO product boxes, ZERO watermarks.",
  },
  {
    id: "N01_HERO_MINT_POSTER_1x1",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "N01_HERO_MINT_POSTER_1x1.png"),
    images: [REF_FACE, REF_BODY],
    prompt:
      CHAR_LOCK +
      OUTFIT_N01 +
      "Square 1:1 luxury wellness editorial campaign portrait. She is positioned slightly on the RIGHT HALF of the frame (around 58%-88% horizontally), standing gracefully at a sunlit bright white-marble kitchen counter with soft morning sunbeams, lush soft-focus green eucalyptus leaves, and a clean minimalist studio-like bright ivory-cream apartment background. " +
      "She holds a sleek crystal-clear glass of smooth creamy plant-protein shake gracefully in one hand, smiling warmly and confidently toward the camera with radiant healthy morning energy. " +
      "Leave the ENTIRE LEFT SIDE and BOTTOM-LEFT of the white marble counter clean, bright, and completely uncluttered so a real product box and Vietnamese typography can be composited cleanly later. " +
      "Shot on 85mm f/2.0, natural sunlit commercial skincare/nutrition photography, ultra-clean 8K realistic skin texture. " +
      "STRICT NEGATIVE: ZERO text, ZERO letters, ZERO logos, ZERO packaging boxes, ZERO watermarks.",
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
  console.log(`[START] ${job.id} (${job.ratio}) via ChatGPT HTPM...`);
  const res = await handlers["chatgpt:generate-image"](null, {
    prompt: job.prompt,
    ratio: job.ratio,
    count: 1,
    images: job.images,
    keepChat: false,
  });
  const buf = extractBuf(res);
  if (buf && buf.length > 30000) {
    fs.writeFileSync(job.outPath, buf);
    console.log(`[DONE] ${job.id} (${res.provider || "chatgpt"}) -> ${buf.length} bytes`);
    return { id: job.id, ok: true, provider: res.provider || "chatgpt" };
  }
  console.error(`[FAIL] ${job.id}:`, res?.error || Object.keys(res || {}));
  return { id: job.id, ok: false, error: res?.error || "no buffer" };
}

(async () => {
  const results = await Promise.all(
    JOBS.map((j, idx) => new Promise((r) => setTimeout(r, idx * 2500)).then(() => runOne(j)))
  );
  console.log("=== STEP 1 HERO OUTFIT RESULTS ===", JSON.stringify(results));
  process.exit(results.every((r) => r.ok) ? 0 : 1);
})();
