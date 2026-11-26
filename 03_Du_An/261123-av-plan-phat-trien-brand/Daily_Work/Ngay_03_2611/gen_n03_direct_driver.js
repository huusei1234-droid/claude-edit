/**
 * Ngày 03 (26/11/2026) — Direct Node.js Driver qua Brave :9333 CDP (0% nghẽn Canvas UI!):
 * - Stage "images": 4 Ảnh Chân dung 1:1 Bài Thiết Kế + 4 Ảnh Diện mạo 9:16 Video Anchor
 *   (Ưu tiên số 1 ChatGPT HTPM 2 lần thử -> tự động fallback Google Flow `flow:generate-image`!)
 * - Stage "videos": 28 Clip Hoạt động Sinh hoạt Đời thường 9:16 (7 cảnh/video × 4 video,
 *   Google Flow `capcut274` chế độ Thành phần / Ingredients, song song 4 tab ngầm!)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const { execFileSync } = require("node:child_process");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_03_2611";
const POST_DIR = path.join(WORK_DIR, "01_ChatGPT_Post_Portraits");
const LOOK_DIR = path.join(WORK_DIR, "04_Video_Looks_9x16");
const CLIP_DIR = path.join(WORK_DIR, "05_Flow_Raw_Clips");
const CUTOUT_DIR = "G:\\My Drive\\dự án ngoài\\An Vượng\\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\\01. Ảnh Sản Phẩm Tách Nền & Logo";

for (const d of [POST_DIR, LOOK_DIR, CLIP_DIR]) fs.mkdirSync(d, { recursive: true });

let MASTER_FILE = "G:\\My Drive\\dự án ngoài\\An Vượng\\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\\02. Ảnh Mẫu Nhân Vật Xuyên Suốt\\AV_MODEL_MASTER_SHEET.jpg";
if (!fs.existsSync(MASTER_FILE)) {
  MASTER_FILE = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc\\AV_MODEL_MASTER_SHEET.jpg";
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

const REF_MASTER = loadImg(MASTER_FILE, "av_model_master.jpg");

const POST_LOCK =
  "Keep the EXACT SAME young Vietnamese woman (26-27 years old) from the attached reference photo av_model_master.jpg with 100% identical facial features, expressive dark-brown eyes, soft brows, gentle rosy smile, luminous fair skin, and slender graceful proportions. " +
  "COMPOSITION LOCK: Frame her neatly on the RIGHT 44% of the 1:1 square frame (three-quarter / waist-up shot), leaving the LEFT 56% open bright soft-focus indoor background for typography and product cutouts. " +
  "NO beach, NO ocean, NO palm trees. Authentic everyday modern Vietnamese home or office interior. ZERO text, ZERO labels, ZERO brand logos, ZERO boxes in the photo. Canon R5 85mm f/2 editorial lifestyle photography. ";

const LOOK_LOCK =
  "Keep the EXACT SAME young Vietnamese woman (26-27 years old) from the attached reference photo av_model_master.jpg with 100% identical facial features, expressive dark-brown eyes, soft brows, gentle rosy smile, luminous fair skin, and slender graceful proportions. " +
  "Vertical 9:16 editorial commercial portrait, centered medium-full framing, authentic everyday modern Vietnamese indoor lifestyle setting (NO beach, NO ocean, NO palm trees). " +
  "ZERO text, ZERO words, ZERO product boxes, ZERO logos, ZERO watermarks. Photorealistic 85mm commercial photography. ";

const IMAGE_JOBS = [
  // --- 4 Square 1:1 Post Portraits ---
  {
    id: "N03_POST1_AVP_KITCHEN",
    ratio: "1:1",
    outPath: path.join(POST_DIR, "N03_POST1_AVP_KITCHEN.png"),
    prompt:
      POST_LOCK +
      "SETTING: Bright sunlit cozy modern Vietnamese family kitchen & breakfast island in early morning light with warm oak cabinets and a small plate of sliced banana in soft bokeh. " +
      "OUTFIT 1: Crisp off-white fine-knit polo shirt with navy collar trim, neat high ponytail, tiny silver stud earrings, slim silver wristwatch. " +
      "POSE: Holding a clean transparent glass of creamy light-beige plant protein smoothie with an energized happy morning smile before going to work.",
  },
  {
    id: "N03_POST2_BOJOMI_OFFICE",
    ratio: "1:1",
    outPath: path.join(POST_DIR, "N03_POST2_BOJOMI_OFFICE.png"),
    prompt:
      POST_LOCK +
      "SETTING: Bright modern corporate office workspace with clean wooden desk, sleek closed laptop, indoor green plant, and soft daylight windows in bokeh. " +
      "OUTFIT 2: Elegant ivory silk blouse with a neat soft bow at the neck paired with a tailored beige high-waisted pencil skirt, polished high bun hairstyle, small gold hoop earrings. " +
      "POSE: Holding a clear glass mug of warm creamy vanilla cereal milk with a poised confident professional smile.",
  },
  {
    id: "N03_POST3_CURCU_HOME",
    ratio: "1:1",
    outPath: path.join(POST_DIR, "N03_POST3_CURCU_HOME.png"),
    prompt:
      POST_LOCK +
      "SETTING: Warm cozy sunlit wooden living room & tea corner at 3 PM golden afternoon indoor light, soft linen curtains and bookshelf in bokeh. " +
      "OUTFIT 3: Effortless ivory-white linen dress with a soft butter-yellow lightweight knit cardigan draped comfortably over her shoulders, natural loose dark-brown hair with soft bangs, delicate gold hoops. " +
      "POSE: Holding a clean cream ceramic mug of warm golden vanilla-coconut turmeric milk with a serene cozy smile.",
  },
  {
    id: "N03_POST4_COL_VANITY",
    ratio: "1:1",
    outPath: path.join(POST_DIR, "N03_POST4_COL_VANITY.png"),
    prompt:
      POST_LOCK +
      "SETTING: Cozy warm-lit modern bedroom & neat skincare vanity table in the evening with warm bedside lamp bokeh and soft cream headboard. " +
      "OUTFIT 4: Chic pastel sky-blue silk loungewear pajama shirt with crisp white piping, soft wavy dark-brown hair half-pinned with a pearl clip, tiny diamond stud earrings, dewy glowing skin. " +
      "POSE: Holding a delicate crystal glass of chilled translucent rosy-peach collagen drink with a radiant relaxed evening smile.",
  },
  // --- 4 Vertical 9:16 Video Look Anchors ---
  {
    id: "N03_LOOK1_AVP_MORNING_9x16",
    ratio: "9:16",
    outPath: path.join(LOOK_DIR, "N03_LOOK1_AVP_MORNING_9x16.png"),
    prompt:
      LOOK_LOCK +
      "OUTFIT 1: Crisp off-white fine-knit polo shirt with navy collar trim tucked into tailored light-beige trousers, neat high ponytail, silver stud earrings, slim silver wristwatch. " +
      "SETTING: Sunlit warm modern Vietnamese apartment kitchen and wooden breakfast counter in early morning.",
  },
  {
    id: "N03_LOOK2_BOJOMI_OFFICE_9x16",
    ratio: "9:16",
    outPath: path.join(LOOK_DIR, "N03_LOOK2_BOJOMI_OFFICE_9x16.png"),
    prompt:
      LOOK_LOCK +
      "OUTFIT 2: Elegant ivory silk bow-neck office blouse tucked into a tailored beige midi pencil skirt, neat high bun hairstyle, small gold hoop earrings, classic leather-strap watch. " +
      "SETTING: Bright sunlit modern office workspace with wooden desk, sleek laptop, and indoor greenery.",
  },
  {
    id: "N03_LOOK3_CURCU_AFTERNOON_9x16",
    ratio: "9:16",
    outPath: path.join(LOOK_DIR, "N03_LOOK3_CURCU_AFTERNOON_9x16.png"),
    prompt:
      LOOK_LOCK +
      "OUTFIT 3: Relaxed ivory-white linen midi dress layered with a soft butter-yellow lightweight knit cardigan, natural loose dark-brown hair with soft bangs, thin gold hoop earrings. " +
      "SETTING: Cozy warm sunlit home living room & wooden tea table at 3 PM afternoon.",
  },
  {
    id: "N03_LOOK4_COL_EVENING_9x16",
    ratio: "9:16",
    outPath: path.join(LOOK_DIR, "N03_LOOK4_COL_EVENING_9x16.png"),
    prompt:
      LOOK_LOCK +
      "OUTFIT 4: Chic pastel sky-blue silk pajama shirt with white piping and matching trousers, soft wavy hair half-up with a pearl clip, tiny crystal stud earrings, luminous dewy skin. " +
      "SETTING: Warm cozy modern bedroom & softly lit evening vanity mirror.",
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

async function runImageOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 50000) {
    console.log(`[SKIP IMG] ${job.id} cached`);
    return { id: job.id, ok: true, provider: "cached" };
  }
  // Tier 1: ChatGPT HTPM (2 tries, built-in fallback inside chatgpt-driver if configured)
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START IMG] ${job.id} (${job.ratio}) ChatGPT HTPM try ${attempt}/2...`);
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: [REF_MASTER],
        keepChat: false,
      });
      const buf = extractImgBuf(res);
      if (buf && buf.length > 30000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE IMG] ${job.id} via ${res.provider || "chatgpt"} -> ${buf.length} bytes`);
        return { id: job.id, ok: true, provider: res.provider || "chatgpt" };
      }
      console.warn(`[WARN IMG] ${job.id} ChatGPT try ${attempt}:`, res?.error || "empty buffer");
    } catch (e) {
      console.warn(`[ERR IMG] ${job.id} ChatGPT try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 2500));
  }
  // Tier 2: Google Flow Nano Banana fallback
  console.log(`[FALLBACK IMG] ${job.id} (${job.ratio}) -> Google Flow...`);
  try {
    const aspect = job.ratio === "9:16" ? "portrait" : job.ratio === "16:9" ? "landscape" : "square";
    const res = handlers["flow:generate-image"]
      ? await handlers["flow:generate-image"](null, {
          prompt: job.prompt,
          aspect,
          count: 1,
          images: [REF_MASTER],
        })
      : await flow.generateImageFallback({
          prompt: job.prompt,
          ratio: job.ratio,
          count: 1,
          images: [REF_MASTER],
        });
    const buf = extractImgBuf(res);
    if (buf && buf.length > 30000) {
      fs.writeFileSync(job.outPath, buf);
      console.log(`[DONE IMG] ${job.id} via Google-Flow -> ${buf.length} bytes`);
      return { id: job.id, ok: true, provider: "flow" };
    }
  } catch (e) {
    console.error(`[ERR FLOW IMG] ${job.id}:`, e?.message || e);
  }
  return { id: job.id, ok: false };
}

async function runPool(items, concurrency, fn) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 2200));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

function buildVideoJobs() {
  const LK1 = loadImg(path.join(LOOK_DIR, "N03_LOOK1_AVP_MORNING_9x16.png"), "n03_look1_avp.png");
  const LK2 = loadImg(path.join(LOOK_DIR, "N03_LOOK2_BOJOMI_OFFICE_9x16.png"), "n03_look2_boj.png");
  const LK3 = loadImg(path.join(LOOK_DIR, "N03_LOOK3_CURCU_AFTERNOON_9x16.png"), "n03_look3_cur.png");
  const LK4 = loadImg(path.join(LOOK_DIR, "N03_LOOK4_COL_EVENING_9x16.png"), "n03_look4_col.png");

  const BOX_PRO = loadImg(path.join(CUTOUT_DIR, "av01_protein_a.png"), "av_protein_box.png");
  const BOX_BOJ = loadImg(path.join(CUTOUT_DIR, "av02_bojomi_b.png"), "av_bojomi_box.png");
  const BOX_CUR = loadImg(path.join(CUTOUT_DIR, "av04_curcumilk_b.png"), "av_curcumilk_box.png");
  const BOX_COL = loadImg(path.join(CUTOUT_DIR, "av03_collamela_b.png"), "av_collamela_box.png");

  const NT = " Natural real-time everyday human motion, closed or gently smiling lips, ZERO speaking, ZERO lip-syncing, NO beach, NO sea, NO text overlays, NO subtitles, NO watermarks.";

  return [
    // === V1: AV PROTEIN (7 cảnh sinh hoạt sáng bận rộn đi làm) ===
    { id: "v1_s01", outPath: path.join(CLIP_DIR, "v1_s01.mp4"), seconds: 4, images: [LK1],
      prompt: "Vertical 9:16 morning routine shot: the young Vietnamese woman from n03_look1_avp.png in off-white navy-trim knit polo opens sheer white apartment curtains letting warm morning sunlight into her living room and glances at her wristwatch getting ready for work." + NT },
    { id: "v1_s02", outPath: path.join(CLIP_DIR, "v1_s02.mp4"), seconds: 4, images: [LK1],
      prompt: "Vertical 9:16 relatable morning shot: the woman from n03_look1_avp.png sits briefly at her home wooden breakfast table looking at a plate of dry toast bread and gently shakes her head with a relatable expression as she has no appetite for dry food when rushing." + NT },
    { id: "v1_s03", outPath: path.join(CLIP_DIR, "v1_s03.mp4"), seconds: 4, images: [LK1],
      prompt: "Vertical 9:16 brisk kitchen activity shot: the woman from n03_look1_avp.png steps up to her sunlit modern home kitchen island and places a clean clear glass cup beside fresh sliced banana on a wooden board with a bright smile." + NT },
    { id: "v1_s04", outPath: path.join(CLIP_DIR, "v1_s04.mp4"), seconds: 4, images: [LK1],
      prompt: "Vertical 9:16 tactile kitchen prep shot: the woman from n03_look1_avp.png pours cool clear water from a glass pitcher into fine plant protein powder in a clear glass and stirs briskly with a spoon until smooth creamy light-beige." + NT },
    { id: "v1_s05", outPath: path.join(CLIP_DIR, "v1_s05.mp4"), seconds: 4, images: [LK1, BOX_PRO],
      prompt: "Vertical 9:16 crisp single-product home kitchen shot: in her sunlit home kitchen, the woman from n03_look1_avp.png holds ONLY the exact cream-and-green AV PROTEIN box from av_protein_box.png clearly upright beside her glass of creamy beige shake on the counter, sharp accurate original label." + NT },
    { id: "v1_s06", outPath: path.join(CLIP_DIR, "v1_s06.mp4"), seconds: 4, images: [LK1],
      prompt: "Vertical 9:16 morning enjoyment shot: the woman from n03_look1_avp.png stands by her home breakfast counter taking a smooth refreshing sip of the creamy beige plant protein drink and rests a relaxed hand lightly on her comfortable stomach with a happy smile." + NT },
    { id: "v1_s07", outPath: path.join(CLIP_DIR, "v1_s07.mp4"), seconds: 4, images: [LK1],
      prompt: "Vertical 9:16 energized work departure shot: the woman from n03_look1_avp.png slings a neat leather work tote over her shoulder, picks up her planner, and walks briskly toward her bright apartment doorway ready for a productive morning." + NT },

    // === V2: BOJOMI (7 cảnh sinh hoạt dân văn phòng & người lớn — 0% trẻ em!) ===
    { id: "v2_s01", outPath: path.join(CLIP_DIR, "v2_s01.mp4"), seconds: 4, images: [LK2],
      prompt: "Vertical 9:16 relatable office shot: the Vietnamese office woman from n03_look2_boj.png in ivory silk bow blouse sits at her modern wooden office desk typing on a laptop, pausing to gently roll her shoulders and stretch her neck after hours indoors." + NT },
    { id: "v2_s02", outPath: path.join(CLIP_DIR, "v2_s02.mp4"), seconds: 4, images: [LK2],
      prompt: "Vertical 9:16 office stretch activity shot: the woman from n03_look2_boj.png stands up beside a bright office window overlooking city buildings and stretches her arms and wrists gracefully to refresh." + NT },
    { id: "v2_s03", outPath: path.join(CLIP_DIR, "v2_s03.mp4"), seconds: 4, images: [LK2, BOX_BOJ],
      prompt: "Vertical 9:16 crisp single-product office shot: at her tidy wooden office desk, the woman from n03_look2_boj.png holds ONLY the exact white-and-emerald BOJOMI box from av_bojomi_box.png clearly visible while reading its nutrition panel with an approving informed smile." + NT },
    { id: "v2_s04", outPath: path.join(CLIP_DIR, "v2_s04.mp4"), seconds: 4, images: [LK2],
      prompt: "Vertical 9:16 office pantry prep shot: the woman from n03_look2_boj.png pours warm 60-degree water from a sleek thermal flask into a clear glass mug of fine cereal powder, delicate warm steam rising softly." + NT },
    { id: "v2_s05", outPath: path.join(CLIP_DIR, "v2_s05.mp4"), seconds: 4, images: [LK2],
      prompt: "Vertical 9:16 tactile stirring shot: the woman from n03_look2_boj.png stirs the warm creamy vanilla cereal milk in a clear glass mug with a silver spoon on her office desk until velvety smooth with zero clumps." + NT },
    { id: "v2_s06", outPath: path.join(CLIP_DIR, "v2_s06.mp4"), seconds: 4, images: [LK2],
      prompt: "Vertical 9:16 pleasant office break shot: the woman from n03_look2_boj.png sits comfortably at her desk taking a warm soothing sip of the vanilla cereal drink beside her laptop, smiling with relaxed satisfaction." + NT },
    { id: "v2_s07", outPath: path.join(CLIP_DIR, "v2_s07.mp4"), seconds: 4, images: [LK2],
      prompt: "Vertical 9:16 active office lifestyle shot: the woman from n03_look2_boj.png walks briskly and gracefully down a bright modern office corridor carrying a neat notebook with confident posture and warm smile." + NT },

    // === V3: CURCUMILK PHYTO (7 cảnh sinh hoạt chiều bận rộn & ấm cúng gia đình) ===
    { id: "v3_s01", outPath: path.join(CLIP_DIR, "v3_s01.mp4"), seconds: 4, images: [LK3],
      prompt: "Vertical 9:16 relatable afternoon shot: the Vietnamese woman from n03_look3_cur.png in ivory linen dress and butter-yellow cardigan works on notes at a home wooden table at 3 PM, pausing to rest a gentle hand over her hungry stomach after eating lunch late." + NT },
    { id: "v3_s02", outPath: path.join(CLIP_DIR, "v3_s02.mp4"), seconds: 4, images: [LK3],
      prompt: "Vertical 9:16 cozy indoor activity shot: the woman from n03_look3_cur.png closes her laptop on the living room table and walks calmly into her sunlit warm wooden home kitchen for an afternoon break." + NT },
    { id: "v3_s03", outPath: path.join(CLIP_DIR, "v3_s03.mp4"), seconds: 4, images: [LK3],
      prompt: "Vertical 9:16 home kitchen routine shot: the woman from n03_look3_cur.png takes a clean cream ceramic mug from a wooden shelf and sets it on a tidy warm countertop bathed in afternoon sunlight." + NT },
    { id: "v3_s04", outPath: path.join(CLIP_DIR, "v3_s04.mp4"), seconds: 4, images: [LK3],
      prompt: "Vertical 9:16 tactile afternoon prep shot: the woman from n03_look3_cur.png pours warm 45-degree water into the cream ceramic mug and stirs a silky golden-yellow vanilla coconut turmeric milk swirl with gentle warm steam." + NT },
    { id: "v3_s05", outPath: path.join(CLIP_DIR, "v3_s05.mp4"), seconds: 4, images: [LK3, BOX_CUR],
      prompt: "Vertical 9:16 crisp single-product cozy home shot: at her warm wooden tea table, the woman from n03_look3_cur.png holds ONLY the exact cream-and-gold CURCUMILK PHYTO box from av_curcumilk_box.png clearly upright beside her warm golden ceramic mug, sharp accurate label." + NT },
    { id: "v3_s06", outPath: path.join(CLIP_DIR, "v3_s06.mp4"), seconds: 4, images: [LK3],
      prompt: "Vertical 9:16 sensory enjoyment shot: the woman from n03_look3_cur.png holds the warm ceramic mug with both hands, inhales the gentle sweet coconut-vanilla aroma with delighted expression and takes a soothing sip." + NT },
    { id: "v3_s07", outPath: path.join(CLIP_DIR, "v3_s07.mp4"), seconds: 4, images: [LK3],
      prompt: "Vertical 9:16 cozy afternoon relaxation shot: the woman from n03_look3_cur.png sits comfortably in a plush living room armchair turning pages of a book beside her warm mug of golden milk in soft amber indoor light." + NT },

    // === V4: COLLAMELA (7 cảnh sinh hoạt tối chăm da 10s đón Tết) ===
    { id: "v4_s01", outPath: path.join(CLIP_DIR, "v4_s01.mp4"), seconds: 4, images: [LK4],
      prompt: "Vertical 9:16 evening skincare routine shot: the Vietnamese woman from n03_look4_col.png in pastel sky-blue silk pajamas sits at a warm-lit bedroom vanity mirror after cleansing and gently pats both cheeks checking her hydrated skin." + NT },
    { id: "v4_s02", outPath: path.join(CLIP_DIR, "v4_s02.mp4"), seconds: 4, images: [LK4],
      prompt: "Vertical 9:16 tidy evening habit shot: the woman from n03_look4_col.png organizes her neat wooden vanity tray with skincare bottles under warm cozy bedroom lamp light, smiling gently." + NT },
    { id: "v4_s03", outPath: path.join(CLIP_DIR, "v4_s03.mp4"), seconds: 4, images: [LK4],
      prompt: "Vertical 9:16 quick evening prep shot: the woman from n03_look4_col.png pours 100ml of cool clear water from a sleek glass carafe into a small crystal glass on her warm bedroom side table." + NT },
    { id: "v4_s04", outPath: path.join(CLIP_DIR, "v4_s04.mp4"), seconds: 4, images: [LK4],
      prompt: "Vertical 9:16 tactile peach drink shot: the woman from n03_look4_col.png stirs a small crystal glass of translucent rosy-peach collagen drink with a delicate stirrer until crystal clear and sparkling." + NT },
    { id: "v4_s05", outPath: path.join(CLIP_DIR, "v4_s05.mp4"), seconds: 4, images: [LK4, BOX_COL],
      prompt: "Vertical 9:16 crisp single-product evening vanity shot: at her warm-lit bedroom vanity, the woman from n03_look4_col.png holds ONLY the exact white-and-emerald COLLAMELA box from av_collamela_box.png clearly upright beside her small glass of rosy-peach drink, sharp accurate label." + NT },
    { id: "v4_s06", outPath: path.join(CLIP_DIR, "v4_s06.mp4"), seconds: 4, images: [LK4],
      prompt: "Vertical 9:16 evening beauty sip shot: the woman from n03_look4_col.png takes a pleasant refreshing sip from the small glass of rosy-peach drink and smiles brightly at the sweet peach taste." + NT },
    { id: "v4_s07", outPath: path.join(CLIP_DIR, "v4_s07.mp4"), seconds: 4, images: [LK4],
      prompt: "Vertical 9:16 convenient daily habit shot: the woman from n03_look4_col.png neatly slips a small cosmetic pouch into her handbag for tomorrow's workday and smiles warmly in her cozy lamp-lit bedroom." + NT },
  ];
}

async function runVideoOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 120000) {
    console.log(`[SKIP VID] ${job.id} cached`);
    return { id: job.id, ok: true, cached: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START VID] ${job.id} (${job.seconds}s, ${job.images.length} refs, 9:16 ingredients) try ${attempt}/2...`);
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
        console.log(`[DONE VID] ${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true, bytes: buf.length };
      }
      console.warn(`[WARN VID] ${job.id} try ${attempt}:`, res?.error || "empty buffer");
    } catch (e) {
      console.warn(`[ERR VID] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3500));
  }
  return { id: job.id, ok: false };
}

(async () => {
  const stage = process.argv[2] || "all";
  const t0 = Date.now();

  if (stage === "all" || stage === "images") {
    console.log("=== [STAGE 1] GENERATING 8 LIFESTYLE PORTRAITS (4x 1:1 + 4x 9:16) ===");
    const imgRes = await runPool(IMAGE_JOBS, 3, runImageOne);
    const okImgs = imgRes.filter((r) => r && r.ok).length;
    console.log(`=== IMAGES DONE: ${okImgs}/${IMAGE_JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
    if (okImgs < IMAGE_JOBS.length) {
      process.exit(1);
    }
  }

  if (stage === "all" || stage === "videos") {
    const tV = Date.now();
    const vJobs = buildVideoJobs();
    console.log(`=== [STAGE 2] GENERATING ${vJobs.length} FAST LIFESTYLE FLOW CLIPS (concurrency=4) ===`);
    const vidRes = await runPool(vJobs, 4, runVideoOne);
    const okVids = vidRes.filter((r) => r && r.ok).length;
    console.log(`=== VIDEOS DONE: ${okVids}/${vJobs.length} in ${Math.round((Date.now() - tV) / 1000)}s ===`);
    await flow.sweepIdleFlowTabs?.().catch(() => {});
    if (okVids < vJobs.length) {
      process.exit(1);
    }
  }

  process.exit(0);
})();
