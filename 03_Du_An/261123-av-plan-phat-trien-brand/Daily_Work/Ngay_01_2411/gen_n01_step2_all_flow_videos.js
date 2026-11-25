/**
 * Ngày 01 (24/11/2026) — Step 2: Tạo song song 13 clip Video Dọc 9:16 (Omni 1.2 Flash, mode: "ingredients" Thành phần)
 * cho Video USP 01 (AV Protein — 7 clips) & Video USP 02 (Combo 4 SP — 6 clips).
 * Khóa 100% khuôn mặt + đồ tập Pilates xanh mint bằng N01_HERO_MINT_9x16.png + hộp sản phẩm thật IS-Net!
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const ASSETS_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\01_ChatGPT_Assets";
const CUTOUT_DIR = "d:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\brand_kits\\07_An_Vuong_Pharma\\02_San_Pham_Cutout_PNG";
const V1_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\video_01_av_protein\\07_HyperFrames_Project\\assets\\videos";
const V2_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\video_02_combo_4sp\\07_HyperFrames_Project\\assets\\videos";
fs.mkdirSync(V1_DIR, { recursive: true });
fs.mkdirSync(V2_DIR, { recursive: true });

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
flow.setup({ getPath: () => DATA_DIR });

function loadImg(filePath, name) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  return { name, mime, base64: buf.toString("base64") };
}

const REF_MINT = loadImg(path.join(ASSETS_DIR, "N01_HERO_MINT_9x16.png"), "n01_mint_hero.png");
const REF_PRO_A = loadImg(path.join(CUTOUT_DIR, "av01_protein_a.png"), "av_protein_box.png");
const REF_BOJ_A = loadImg(path.join(CUTOUT_DIR, "av02_bojomi_a.png"), "av_bojomi_box.png");
const REF_COL_A = loadImg(path.join(CUTOUT_DIR, "av03_collamela_a.png"), "av_collamela_box.png");
const REF_CUR_A = loadImg(path.join(CUTOUT_DIR, "av04_curcumilk_a.png"), "av_curcumilk_box.png");

const SAFE_SUFFIX =
  " Keep the exact same Vietnamese woman and her exact pastel mint-green sleeveless ribbed pilates tank top and leggings from n01_mint_hero.png. " +
  "Smooth cinematic camera movement, crisp sunlit high-key luxury wellness commercial 24fps aesthetic. " +
  "Natural calm breathing, warm gentle closed-mouth smile, ZERO speaking, ZERO lip-syncing, no mouthing words, NO on-screen text, NO subtitles, NO watermarks.";

const JOBS = [
  // ===================== VIDEO 01: AV PROTEIN (7 unique Flow clips) =====================
  {
    id: "v1_s01",
    outPath: path.join(V1_DIR, "s01.mp4"),
    seconds: 5,
    images: [REF_MINT],
    prompt:
      "Vertical 9:16 commercial opening hook shot of the young Vietnamese woman from n01_mint_hero.png standing in her bright sunlit white-marble kitchen island in the morning, gently lifting a clear glass of creamy beige plant-protein shake slightly toward the sunlight with a radiant energetic smile. Gentle slow push-in dolly camera movement, floating soft morning dust motes in warm sunbeams." +
      SAFE_SUFFIX,
  },
  {
    id: "v1_s02",
    outPath: path.join(V1_DIR, "s02.mp4"),
    seconds: 7,
    images: [REF_MINT],
    prompt:
      "Vertical 9:16 lifestyle relatable scene: the same young Vietnamese woman from n01_mint_hero.png sitting at a modern bright home table at 10am with a laptop and a plain white plate of half-eaten white bread/pastry, gently resting her chin on her hand looking slightly tired and low-energy with soft sighed breathing, checking her wrist subtly. Subtle cool-soft daylight contrast, smooth slow lateral camera glide." +
      SAFE_SUFFIX,
  },
  {
    id: "v1_s03",
    outPath: path.join(V1_DIR, "s03.mp4"),
    seconds: 7,
    images: [REF_MINT, REF_PRO_A],
    prompt:
      "Vertical 9:16 hero product reveal commercial shot: the young Vietnamese woman from n01_mint_hero.png stands brightly at the white marble kitchen counter, holding up the real green-and-cream AV Protein box from av_protein_box.png proudly near chest level while smiling warmly and confidently. Bright luminous golden morning sunflare enters softly from the window behind, smooth slow cinematic arc dolly around her and the product box." +
      SAFE_SUFFIX,
  },
  {
    id: "v1_s04a",
    outPath: path.join(V1_DIR, "s04a.mp4"),
    seconds: 6,
    images: [REF_PRO_A],
    prompt:
      "Vertical 9:16 ultra-clean luxury 3D CGI macro commercial nutrition visualization matching the emerald-green and cream-gold aesthetic of av_protein_box.png: fresh bright emerald green peas, pure pearlescent white rice grains, and a silky smooth swirling ribbon of creamy beige plant-protein milk floating gracefully in luminous sunlit white-emerald studio space with delicate golden micro-droplets spinning in slow motion. Zero text, zero letters, zero watermarks, 8K pharmaceutical commercial CGI.",
  },
  {
    id: "v1_s04b",
    outPath: path.join(V1_DIR, "s04b.mp4"),
    seconds: 6,
    images: [REF_MINT],
    prompt:
      "Vertical 9:16 wellness fitness shot: the young Vietnamese woman from n01_mint_hero.png in her exact pastel mint-green pilates tank and leggings performs a graceful, elegant standing side stretch and arm raise on a sage-green yoga mat in her sunlit bright living room next to sheer white curtains and lush indoor plants. Vibrant healthy posture, glowing skin, smooth slow upward tracking camera movement." +
      SAFE_SUFFIX,
  },
  {
    id: "v1_s05",
    outPath: path.join(V1_DIR, "s05.mp4"),
    seconds: 9,
    images: [REF_MINT, REF_PRO_A],
    prompt:
      "Vertical 9:16 close-up lifestyle preparation shot on a sunlit white marble kitchen counter with the AV Protein box av_protein_box.png placed neatly in soft background bokeh: the slender hands of the woman from n01_mint_hero.png pour crystal-clear cool water into a clear glass of silky plant-protein powder, then stir smoothly with a sleek glass spoon as the beverage swirls effortlessly into a smooth velvety creamy drink with zero clumps. Crisp backlit morning light, smooth slow camera push-in." +
      SAFE_SUFFIX,
  },
  {
    id: "v1_s06",
    outPath: path.join(V1_DIR, "s06.mp4"),
    seconds: 7,
    images: [REF_MINT],
    prompt:
      "Vertical 9:16 joyful payoff lifestyle shot: the young Vietnamese woman from n01_mint_hero.png stands by her sunlit apartment window holding her glass of creamy plant-protein shake, takes a gentle delighted sip, lowers the glass slightly and smiles brightly with fresh radiant morning vitality and lightness. Warm golden-pearl sunlit flare, smooth slow cinema glide." +
      SAFE_SUFFIX,
  },

  // ===================== VIDEO 02: COMBO 4 SP CTKM (6 unique Flow clips) =====================
  {
    id: "v2_s01",
    outPath: path.join(V2_DIR, "s01.mp4"),
    seconds: 7,
    images: [REF_MINT],
    prompt:
      "Vertical 9:16 celebratory bright wellness commercial opening: the young Vietnamese woman from n01_mint_hero.png walks gracefully forward into her sunlit luxury modern living room and kitchen with a joyful welcoming smile, delicate warm golden champagne bokeh light particles shimmering softly in the airy pearl-white sunlit space. Smooth backward tracking dolly shot." +
      SAFE_SUFFIX,
  },
  {
    id: "v2_s02",
    outPath: path.join(V2_DIR, "s02.mp4"),
    seconds: 8,
    images: [REF_MINT, REF_PRO_A],
    prompt:
      "Vertical 9:16 morning wellness routine shot: in crisp golden sunrise light near her sunlit window and rolled yoga mat, the woman from n01_mint_hero.png gently shakes a sleek clear glass shaker bottle filled with creamy plant protein next to the AV Protein box av_protein_box.png sitting cleanly on the white marble counter, beaming with morning athletic energy. Smooth cinema orbit camera." +
      SAFE_SUFFIX,
  },
  {
    id: "v2_s03",
    outPath: path.join(V2_DIR, "s03.mp4"),
    seconds: 9,
    images: [REF_MINT, REF_BOJ_A],
    prompt:
      "Vertical 9:16 midday bone-and-nutrition commercial shot: the woman from n01_mint_hero.png stands warmly beside the white marble dining counter where the green-and-cream Bojomi box av_bojomi_box.png sits neatly beside a ceramic mug of warm steaming vanilla cereal milk; she gently cradles the warm cup with both hands and smiles with calm reassuring grace. Bright clean daylight, gentle slow dolly-in." +
      SAFE_SUFFIX,
  },
  {
    id: "v2_s04",
    outPath: path.join(V2_DIR, "s04.mp4"),
    seconds: 8,
    images: [REF_MINT, REF_CUR_A],
    prompt:
      "Vertical 9:16 cozy afternoon snack commercial shot: warm honey-gold afternoon sunlight streams softly onto the marble counter where the golden-yellow and emerald Curcumilk Phyto box av_curcumilk_box.png sits cleanly beside a glass cup of rich velvety golden-amber turmeric coconut milk; the woman from n01_mint_hero.png lifts the warm golden cup gently and smells the soothing vanilla aroma with a peaceful content smile." +
      SAFE_SUFFIX,
  },
  {
    id: "v2_s05",
    outPath: path.join(V2_DIR, "s05.mp4"),
    seconds: 9,
    images: [REF_MINT, REF_COL_A],
    prompt:
      "Vertical 9:16 luminous evening skincare beauty shot: soft warm pearl-rose vanity light in a chic luxury dressing space, the white-and-emerald Collamela box av_collamela_box.png sits beside a crystal glass of clear peach-tinted collagen drink; the woman from n01_mint_hero.png gently touches her glowing hydrated cheek with fingertips and lifts the peach drink with a radiant confident beauty smile." +
      SAFE_SUFFIX,
  },
  {
    id: "v2_s06a",
    outPath: path.join(V2_DIR, "s06a.mp4"),
    seconds: 6,
    images: [REF_MINT, REF_COL_A],
    prompt:
      "Vertical 9:16 celebratory gift-reveal commercial shot: the young Vietnamese woman from n01_mint_hero.png stands smiling joyfully in a bright luxury pearl-white sunlit room with soft floating golden celebration light sparkles, happily presenting the Collamela 20-sachet box av_collamela_box.png forward with both hands as an exciting high-value gift. Crisp studio beauty lighting, smooth subtle push-in." +
      SAFE_SUFFIX,
  },
];

function extractBuf(res) {
  const d = res?.data || res?.items?.[0]?.data;
  if (!d) return null;
  if (Buffer.isBuffer(d)) return d;
  if (d instanceof Uint8Array) return Buffer.from(d);
  return Buffer.from(String(d), "base64");
}

async function runJob(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 200000) {
    console.log(`[SKIP] ${job.id} already cached (${fs.statSync(job.outPath).size} bytes)`);
    return { id: job.id, ok: true, cached: true };
  }
  for (let attempt = 1; attempt <= 1; attempt++) {
    console.log(`[START #${attempt}] ${job.id} (${job.seconds}s, ${job.images.length} refs, 9:16 ingredients)...`);
    try {
      const res = await handlers["flow:generate-video"](null, {
        prompt: job.prompt,
        model: "Omni 1.2 Flash",
        aspect: "portrait",
        resolution: "720p",
        seconds: job.seconds,
        count: 1,
        mode: "ingredients",
        images: job.images,
      });
      if (res && res.ok) {
        const buf = extractBuf(res);
        if (buf && buf.length > 100000) {
          fs.writeFileSync(job.outPath, buf);
          console.log(`[DONE] ${job.id} -> ${job.outPath} (${buf.length} bytes)`);
          return { id: job.id, ok: true, bytes: buf.length };
        }
      }
      console.warn(`[WARN #${attempt}] ${job.id}:`, res?.error || "empty buffer");
    } catch (err) {
      console.error(`[ERR #${attempt}] ${job.id}:`, err.message);
    }
  }
  return { id: job.id, ok: false };
}

// Run gently with concurrency = 2 (zero rate-limit hammering)
async function runPool(items, concurrency) {
  const results = new Array(items.length);
  let nextIdx = 0;
  async function worker(wId) {
    await new Promise((r) => setTimeout(r, wId * 4000));
    while (nextIdx < items.length) {
      const i = nextIdx++;
      results[i] = await runJob(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => worker(k)));
  return results;
}

(async () => {
  const t0 = Date.now();
  const results = await runPool(JOBS, 2);
  const okCount = results.filter((r) => r && r.ok).length;
  console.log(`\n=== STEP 2 FLOW VIDEOS DONE: ${okCount}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(results, null, 2));
  process.exit(okCount === JOBS.length ? 0 : 1);
})();
