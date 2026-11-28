/**
 * Tạo Bộ Nhân Vật Đại Diện Mới (Ngày 27/11/2026) từ `mẫu.jpg` + `AV_ORIG_BODY_MODEL.png`
 * 100% bằng ChatGPT (Dự án HTPM, noFallback: true):
 *   - Ảnh 1 (mau_moi_face.jpg): Khuôn mặt, nụ cười rạng rỡ & mái tóc uốn sóng nâu đen của cô trong `mẫu.jpg`
 *   - Ảnh 2 (av_body_goc.png): Giữ nguyên 100% tướng tá, vóc dáng thon gọn đồng hồ cát của mẫu An Vượng
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\Build_Mau_Moi_2711";
const OUT_DIR = path.join(WORK_DIR, "ChatGPT_Output");
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

const IMG_NEW_FACE = loadImg(path.join(WORK_DIR, "MAU_MOI_SOURCE_SRGB.jpg"), "anh_1_mau_moi.jpg");
const IMG_AV_BODY = loadImg(path.join(WORK_DIR, "AV_ORIG_BODY_MODEL.png"), "anh_2_dang_an_vuong.png");

const BASE_LOCK =
  "I have attached TWO original unedited reference photos:\n" +
  "- Photo 1 (anh_1_mau_moi.jpg — Vietnamese woman seated in cream blazer): Use 100% ONLY HER EXACT HEAD & FACE IDENTITY — identical facial structure, bright dark-brown eyes, natural eyebrows, nose, radiant warm smile, fair porcelain skin, and lush dark-brown side-parted wavy hair. NEVER use the face from Photo 2.\n" +
  "- Photo 2 (anh_2_dang_an_vuong.png — woman standing in floral silk pajama set): Use 100% HER EXACT BODY PROPORTIONS, STATURE & FIGURE — tall graceful posture, slender toned arms, defined slim waist, feminine bust and hips, and shapely smooth legs blended seamlessly with Photo 1's neck and skin tone.\n" +
  "Photorealistic Canon EOS R5 85mm f/2 commercial lifestyle portrait, ZERO text, ZERO watermarks, ZERO logos.\n\n";

const JOBS = [
  {
    id: "NEW_BODY_ANCHOR",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "NEW_BODY_ANCHOR.png"),
    prompt:
      BASE_LOCK +
      "SCENE (MASTER BODY ANCHOR — DIRECT FACE/HEAD SWAP ON PHOTO 2): Recreate Photo 2's exact three-quarter thigh-up standing pose, feminine curvy-slender hourglass body, white-and-blue floral silk short-sleeve pajama set, and warm cozy luxury modern bedroom background, replacing ONLY Photo 2's head/face with Photo 1's exact face, radiant warm smile, and lush side-parted wavy dark-brown hair.",
  },
  {
    id: "STYLE_01_SPORTY_TENNIS",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_01_SPORTY_TENNIS.png"),
    prompt:
      BASE_LOCK +
      "SCENE (STYLE 1 — MORNING PILATES / TENNIS CHIC): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact face & head on Photo 2's exact slim-waisted feminine hourglass figure. " +
      "OUTFIT & HAIRSTYLE: Sleek fitted pastel sage-green activewear zip top over a crisp white tank paired with a high-waisted white pleated tennis skort, neat sporty high ponytail with soft side waves, tiny stud earrings, slim smartwatch. " +
      "SETTING: Bright sunlit modern apartment living room & wellness corner with sheer white curtains and indoor greenery.",
  },
  {
    id: "STYLE_02_CHIC_EXECUTIVE",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_02_CHIC_EXECUTIVE.png"),
    prompt:
      BASE_LOCK +
      "SCENE (STYLE 2 — MODERN EXECUTIVE OFFICE): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact face & head on Photo 2's exact slim-waisted feminine hourglass figure. " +
      "OUTFIT & HAIRSTYLE: Tailored pastel dusty-rose blazer fitted at her slim waist over an ivory silk camisole and high-waisted cream tailored trousers, lush glossy side-parted dark-brown waves, small pearl drop earrings. " +
      "SETTING: Bright sunlit modern corporate office workspace with warm oak desk, sleek laptop, and soft daylight window bokeh.",
  },
  {
    id: "STYLE_03_COZY_HOME_KITCHEN",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_03_COZY_HOME_KITCHEN.png"),
    prompt:
      BASE_LOCK +
      "SCENE (STYLE 3 — WARM EVERYDAY HOME LIFESTYLE): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact face & head on Photo 2's exact feminine hourglass figure and toned arms. " +
      "OUTFIT & HAIRSTYLE: Flattering butter-yellow square-neck ribbed knit midi dress layered with a soft ivory cardigan, half-up wavy dark-brown hair with a pearl clip, holding a warm cream ceramic mug gently. " +
      "SETTING: Sunlit warm wooden home kitchen & tea corner in soft afternoon light.",
  },
  {
    id: "STYLE_04_RADIANT_EVENING",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "STYLE_04_RADIANT_EVENING.png"),
    prompt:
      BASE_LOCK +
      "SCENE (STYLE 4 — ELEGANT EVENING SILK): Medium-full thigh-up vertical 9:16 portrait keeping Photo 1's exact face & head on Photo 2's exact feminine hourglass silhouette and slim waist. " +
      "OUTFIT & HAIRSTYLE: Elegant emerald-green satin silk wrap blouse tucked into a high-waisted champagne silk midi skirt, glamorous side-swept dark-brown waves and delicate diamond earrings. " +
      "SETTING: Warm lamp-lit upscale modern home lounge & vanity corner in the evening.",
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
        images: [IMG_NEW_FACE, IMG_AV_BODY],
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
  const res = await runPool(JOBS, 3, runJob);
  const okCnt = res.filter((r) => r && r.ok).length;
  await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
  console.log(`=== COMPLETED ${okCnt}/${JOBS.length} IN ${Math.round((Date.now() - t0) / 1000)}s ===`);
  process.exit(okCnt === JOBS.length ? 0 : 1);
})();
