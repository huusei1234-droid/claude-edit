/**
 * Video #3: "3. Ăn chay, nhìn thế nào để biết bữa ăn có nguồn đạm?"
 * - Stage 1 (100% Pure ChatGPT HTPM, noFallback: true, 2 clean original anchors of Chị Hậu):
 *     Tạo 2 tạo hình Bếp & Bàn ăn chay ấm cúng mới cho Chị Hậu (áo sơ mi linen xanh bơ nhạt + tạp dề kem bếp sáng nắng)
 * - Stage 2 (Google Flow capcut274, portrait 9:16, Ingredients mode, concurrency=4):
 *     Quay 9 cảnh hoạt động bếp & mâm cơm chay thực tế chia đều vào 3 Cảnh lớn (~10–13s/cảnh)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Series_7_Video_Kien_Thuc_Chi_Hau\\V03_An_Chay_Nguon_Dam";
const LOOK_DIR = path.join(WORK_DIR, "02_ChatGPT_Looks_9x16");
const CLIP_DIR = path.join(WORK_DIR, "03_Flow_Clips_9x16");
for (const d of [LOOK_DIR, CLIP_DIR]) fs.mkdirSync(d, { recursive: true });

let ANCHOR_DIR = "G:\\My Drive\\dự án ngoài\\An Vượng\\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\\02. Ảnh Mẫu Nhân Vật Xuyên Suốt";
if (!fs.existsSync(path.join(ANCHOR_DIR, "AV_MODEL_FACE_ANCHOR.png"))) {
  ANCHOR_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc";
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

function loadImg(filePath, name) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  return { name, mime, base64: buf.toString("base64") };
}

const IMG_FACE = loadImg(path.join(ANCHOR_DIR, "AV_MODEL_FACE_ANCHOR.png"), "chi_hau_face_anchor.png");
const IMG_BODY = loadImg(path.join(ANCHOR_DIR, "AV_MODEL_BODY_ANCHOR.png"), "chi_hau_body_anchor.png");

const HAU_LOCK =
  "I have attached two reference photos of the same Vietnamese woman (Chị Hậu): Photo 1 (chi_hau_face_anchor.png) for 100% her exact head and facial identity, and Photo 2 (chi_hau_body_anchor.png) for 100% her exact slender-curvy feminine hourglass body proportions and slim waist. " +
  "Keep 100% her identical face, expressive dark-brown eyes, softly arched brows, warm coral-rose closed-lip gentle smile, shoulder-length layered dark-chestnut bob hair, and slender graceful figure. " +
  "Vertical 9:16 photorealistic Canon EOS R5 85mm f/2 editorial home lifestyle photography. ZERO text, ZERO watermarks, ZERO logos.\n\n";

const LOOK_JOBS = [
  {
    id: "V03_LOOK_DINING_SAGE",
    ratio: "9:16",
    outPath: path.join(LOOK_DIR, "V03_LOOK_DINING_SAGE.png"),
    prompt:
      HAU_LOCK +
      "OUTFIT & SETTING (Everyday Home Dining Chic): Medium-full thigh-up portrait of her wearing a fresh pastel sage-green short-sleeve linen button-up shirt neatly tucked into high-waisted cream cotton trousers, shoulder-length dark-chestnut bob tucked behind one ear with tiny gold stud earrings and delicate gold pendant necklace, standing beside a sunlit warm wooden Vietnamese home dining table.",
  },
  {
    id: "V03_LOOK_APRON_KITCHEN",
    ratio: "9:16",
    outPath: path.join(LOOK_DIR, "V03_LOOK_APRON_KITCHEN.png"),
    prompt:
      HAU_LOCK +
      "OUTFIT & SETTING (Cozy Home Kitchen Cooking Style): Medium-full thigh-up portrait of her wearing a clean oatmeal-cream linen cross-back kitchen apron layered over her pastel sage-green short-sleeve linen shirt, neat half-up dark-chestnut bob secured with a small tortoiseshell clip, tiny gold stud earrings, standing cheerfully in a bright sunlit modern oak home kitchen.",
  },
];

function extractImgBuf(res) {
  const b64 = res?.data || res?.items?.[0]?.data || res?.items?.[0]?.base64 || res?.images?.[0]?.base64 || res?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  if (b64 instanceof Uint8Array || Array.isArray(b64)) return Buffer.from(b64);
  return Buffer.from(String(b64).replace(/^data:image\/\w+;base64,/, ""), "base64");
}

function extractVidBuf(res) {
  if (!res) return null;
  if (res.videoPath && fs.existsSync(res.videoPath)) return fs.readFileSync(res.videoPath);
  const b64 = res.data || res.videoBase64 || res.items?.[0]?.data || res.items?.[0]?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  return Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
}

async function runLookOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 80000) {
    console.log(`[SKIP LOOK] ${job.id} cached`);
    return { id: job.id, ok: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START CHATGPT LOOK] ${job.id} try ${attempt}/2...`);
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: [IMG_FACE, IMG_BODY],
        keepChat: false,
        noFallback: true,
      });
      const buf = extractImgBuf(res);
      if (res?.ok && buf && buf.length > 80000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE LOOK] ${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true };
      }
      console.warn(`[WARN LOOK] ${job.id} try ${attempt}:`, res?.error || "empty");
    } catch (e) {
      console.warn(`[ERR LOOK] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 2500));
  }
  return { id: job.id, ok: false };
}

function buildClipJobs() {
  const LK_DINE = loadImg(path.join(LOOK_DIR, "V03_LOOK_DINING_SAGE.png"), "hau_dining_sage.jpg");
  const LK_COOK = loadImg(path.join(LOOK_DIR, "V03_LOOK_APRON_KITCHEN.png"), "hau_kitchen_apron.jpg");
  const NT = " Natural real-time everyday motion, gentle warm closed-lip smile, ZERO speaking, ZERO lip-syncing, NO text, NO subtitles, NO watermarks.";

  return [
    // === CẢNH 1 (0 - ~12s): Mâm cơm chay (cơm, rau luộc, canh bí, nấm xào) & Câu hỏi nguồn đạm chính ===
    {
      id: "c1_s1",
      outPath: path.join(CLIP_DIR, "c1_s1.mp4"),
      seconds: 4,
      images: [LK_DINE],
      prompt:
        "Vertical 9:16 overhead-angled warm Vietnamese home dining table shot: a neat round wooden tray with a vegetarian meal consisting of ONLY four dishes — a bowl of steaming white rice, a plate of bright green boiled vegetables, a bowl of golden pumpkin soup, and a plate of stir-fried mushrooms — gentle warm steam rising in natural window daylight." + NT,
    },
    {
      id: "c1_s2",
      outPath: path.join(CLIP_DIR, "c1_s2.mp4"),
      seconds: 4,
      images: [LK_DINE],
      prompt:
        "Vertical 9:16 medium shot at a sunlit Vietnamese wooden dining table: the woman from hau_dining_sage.jpg in pastel sage-green linen shirt sits warmly before the vegetarian meal of rice, boiled greens, pumpkin soup, and stir-fried mushrooms, looking thoughtfully over the dishes and gesturing lightly with an open palm as if asking which dish has protein." + NT,
    },
    {
      id: "c1_s3",
      outPath: path.join(CLIP_DIR, "c1_s3.mp4"),
      seconds: 4,
      images: [LK_DINE],
      prompt:
        "Vertical 9:16 close-up tabletop angle: graceful hands of the woman from hau_dining_sage.jpg hold wooden chopsticks hovering thoughtfully over the plates of boiled green vegetables and stir-fried mushrooms beside white rice and pumpkin soup, leaving a clear space on the table for a protein dish." + NT,
    },

    // === CẢNH 2 (~12 - ~25s): Thêm đậu phụ sốt cà, đậu gà, đậu lăng & Đổi các loại đậu + ngũ cốc ===
    {
      id: "c2_s1",
      outPath: path.join(CLIP_DIR, "c2_s1.mp4"),
      seconds: 4,
      images: [LK_COOK],
      prompt:
        "Vertical 9:16 warm dining shot: the Vietnamese woman from hau_kitchen_apron.jpg in cream linen apron over sage-green shirt smiles warmly as she places a steaming ceramic plate of golden tofu braised in rich red tomato sauce garnished with green scallions right onto the center of the vegetarian dining table." + NT,
    },
    {
      id: "c2_s2",
      outPath: path.join(CLIP_DIR, "c2_s2.mp4"),
      seconds: 4,
      images: [LK_COOK],
      prompt:
        "Vertical 9:16 sunlit home kitchen counter shot: the woman from hau_kitchen_apron.jpg neatly sets two wholesome ceramic bowls side-by-side on a wooden board — one bowl of tender cooked golden chickpeas and one bowl of hearty cooked lentils garnished with fresh herbs." + NT,
    },
    {
      id: "c2_s3",
      outPath: path.join(CLIP_DIR, "c2_s3.mp4"),
      seconds: 4,
      images: [LK_COOK],
      prompt:
        "Vertical 9:16 tactile kitchen pantry shot: in her sunlit wooden kitchen, the woman from hau_kitchen_apron.jpg arranges clear glass jars filled with diverse dry legumes (chickpeas, red lentils, mung beans, black beans) alongside whole grains (brown rice and rolled oats), scooping golden chickpeas with a wooden spoon." + NT,
    },

    // === CẢNH 3 (~25 - ~35s): Chọn món đạm ngay từ lúc lên thực đơn ===
    {
      id: "c3_s1",
      outPath: path.join(CLIP_DIR, "c3_s1.mp4"),
      seconds: 4,
      images: [LK_COOK],
      prompt:
        "Vertical 9:16 sunlit modern home kitchen shot: the woman from hau_kitchen_apron.jpg stands at her wooden kitchen island holding a pen and writing a daily meal plan in a neat paper notebook beside fresh white tofu, chickpeas, and vegetables, smiling warmly." + NT,
    },
    {
      id: "c3_s2",
      outPath: path.join(CLIP_DIR, "c3_s2.mp4"),
      seconds: 4,
      images: [LK_COOK],
      prompt:
        "Vertical 9:16 close-up home cooking prep shot: hands of the woman from hau_kitchen_apron.jpg neatly cut fresh firm white tofu into cubes on a clean wooden cutting board beside ripe red tomatoes and a bowl of cooked chickpeas in warm morning light." + NT,
    },
    {
      id: "c3_s3",
      outPath: path.join(CLIP_DIR, "c3_s3.mp4"),
      seconds: 4,
      images: [LK_DINE],
      prompt:
        "Vertical 9:16 warm closing lifestyle shot: the woman from hau_dining_sage.jpg in pastel sage-green linen shirt sits happily at her sunlit wooden dining table before a complete balanced vegetarian meal with tofu in tomato sauce, chickpeas, greens, pumpkin soup, and rice, smiling gently and nodding warmly toward the camera." + NT,
    },
  ];
}

async function runClipOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 120000) {
    console.log(`[SKIP CLIP] ${job.id} cached`);
    return { id: job.id, ok: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START FLOW CLIP] ${job.id} try ${attempt}/2...`);
    try {
      const res = await handlers["flow:generate-video"](null, {
        prompt: job.prompt,
        model: "Omni 1.2 Flash",
        aspect: "portrait",
        resolution: "720p",
        seconds: job.seconds,
        mode: "ingredients",
        count: 1,
        images: job.images,
      });
      const buf = extractVidBuf(res);
      if (buf && buf.length > 120000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE CLIP] ${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true };
      }
      console.warn(`[WARN CLIP] ${job.id} try ${attempt}:`, res?.error || "empty");
    } catch (e) {
      console.warn(`[ERR CLIP] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3500));
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
  const stage = process.argv[2] || "all";
  const t0 = Date.now();

  if (stage === "all" || stage === "looks") {
    console.log("=== [STAGE 1] GENERATING 2 KITCHEN/DINING OUTFIT LOOKS FOR CHI HAU ON CHATGPT ===");
    const lkRes = await runPool(LOOK_JOBS, 2, runLookOne);
    const okLk = lkRes.filter((r) => r && r.ok).length;
    await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
    console.log(`=== LOOKS DONE: ${okLk}/${LOOK_JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
    if (okLk < LOOK_JOBS.length) process.exit(1);
  }

  if (stage === "all" || stage === "clips") {
    const tV = Date.now();
    const clipJobs = buildClipJobs();
    console.log(`=== [STAGE 2] GENERATING ${clipJobs.length} VEGETARIAN PROTEIN CLIPS ON GOOGLE FLOW ===`);
    const clRes = await runPool(clipJobs, 3, runClipOne);
    const okCl = clRes.filter((r) => r && r.ok).length;
    await flow.sweepIdleFlowTabs?.().catch(() => {});
    console.log(`=== CLIPS DONE: ${okCl}/${clipJobs.length} in ${Math.round((Date.now() - tV) / 1000)}s ===`);
    if (okCl < clipJobs.length) process.exit(1);
  }

  process.exit(0);
})();
