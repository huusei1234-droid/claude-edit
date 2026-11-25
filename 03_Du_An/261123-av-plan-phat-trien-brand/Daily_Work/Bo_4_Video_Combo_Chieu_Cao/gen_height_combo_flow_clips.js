/**
 * Bộ 4 Video Combo Phát Triển Chiều Cao (BOJOMI + AV PROTEIN — 24/11/2026):
 * - Tạo 24 clip Live-Action Dọc 9:16 (Google Flow Omni 1.2 Flash, mode: "ingredients", 720p) khóa 4 trang phục mới + hộp thật Bojomi & AV Protein
 * - Kết hợp 6 clip 3D CGI Macro dinh dưỡng đã kiểm định 10/10 -> Tổng 30 clip động (7-8 clip/video, nhịp dựng cực mượt!)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Combo_Chieu_Cao";
const ASSETS_DIR = path.join(WORK_DIR, "01_ChatGPT_Assets");
const CUTOUT_DIR = "d:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\brand_kits\\07_An_Vuong_Pharma\\02_San_Pham_Cutout_PNG";

const V1_DIR = path.join(WORK_DIR, "height_01_dam_va_canxi", "07_HyperFrames_Project", "assets", "videos");
const V2_DIR = path.join(WORK_DIR, "height_02_4_tru_cot_vang", "07_HyperFrames_Project", "assets", "videos");
const V3_DIR = path.join(WORK_DIR, "height_03_pha_chuan_2_nhiet_do", "07_HyperFrames_Project", "assets", "videos");
const V4_DIR = path.join(WORK_DIR, "height_04_van_dong_va_deal_870k", "07_HyperFrames_Project", "assets", "videos");
for (const d of [V1_DIR, V2_DIR, V3_DIR, V4_DIR]) fs.mkdirSync(d, { recursive: true });

// Pre-copy verified 10/10 3D CGI macro clips for fast crisp pacing!
const CGI_COPIES = [
  ["d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\video_01_av_protein\\07_HyperFrames_Project\\assets\\videos\\s04a.mp4", path.join(V1_DIR, "s04a.mp4")],
  ["d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Bojomi_Chay_Bo\\bojomi_run_01_khung_xuong\\07_HyperFrames_Project\\assets\\videos\\s04a.mp4", path.join(V1_DIR, "s05a.mp4")],
  ["d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Bojomi_Chay_Bo\\bojomi_run_02_bo3_d3_k2\\07_HyperFrames_Project\\assets\\videos\\s04a.mp4", path.join(V2_DIR, "s04a.mp4")],
  ["d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\video_01_av_protein\\07_HyperFrames_Project\\assets\\videos\\s04a.mp4", path.join(V3_DIR, "s04b.mp4")],
  ["d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Bojomi_Chay_Bo\\bojomi_run_04_pha_30s_uu_dai\\07_HyperFrames_Project\\assets\\videos\\s04a.mp4", path.join(V3_DIR, "s05b.mp4")],
  ["d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Bojomi_Chay_Bo\\bojomi_run_03_collagen_deo_dai\\07_HyperFrames_Project\\assets\\videos\\s04a.mp4", path.join(V4_DIR, "s05a.mp4")],
];
for (const [src, dst] of CGI_COPIES) {
  if (fs.existsSync(src)) fs.copyFileSync(src, dst);
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
flow.setup({ getPath: () => DATA_DIR });

function loadImg(filePath, name) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  return { name, mime, base64: buf.toString("base64") };
}

const REF_H1 = loadImg(path.join(ASSETS_DIR, "HEIGHT_LOOK1_NAVY_POLO_9x16.png"), "height_look1_navy.png");
const REF_H2 = loadImg(path.join(ASSETS_DIR, "HEIGHT_LOOK2_LINEN_MINT_9x16.png"), "height_look2_linen.png");
const REF_H3 = loadImg(path.join(ASSETS_DIR, "HEIGHT_LOOK3_BUTTER_KITCHEN_9x16.png"), "height_look3_butter.png");
const REF_H4 = loadImg(path.join(ASSETS_DIR, "HEIGHT_LOOK4_SKY_STRETCH_9x16.png"), "height_look4_sky.png");
const REF_BOJ = loadImg(path.join(CUTOUT_DIR, "av02_bojomi_a.png"), "av_bojomi_box.png");
const REF_PRO = loadImg(path.join(CUTOUT_DIR, "av01_protein_a.png"), "av_protein_box.png");

const H1_LOCK =
  " Keep the exact same Vietnamese woman, her exact crisp-white navy-trim sleeveless athletic polo top, navy pleated athletic skort, white sneakers, high wavy ponytail with white satin scrunchie, pearl studs, silver necklace, and white smartwatch from height_look1_navy.png. " +
  "Natural calm breathing, radiant closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const H2_LOCK =
  " Keep the exact same Vietnamese woman, her exact ivory-cream square-neck linen midi dress, pastel-mint knit cardigan draped over her shoulders, soft loose wavy hair with pearl hairpin, teardrop pearl earrings, dainty gold necklace, and cream leather watch from height_look2_linen.png. " +
  "Natural calm breathing, warm closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const H3_LOCK =
  " Keep the exact same Vietnamese woman, her exact pastel butter-yellow short-sleeve ribbed square-neck top, crisp-ivory wide-leg trousers, half-up top bun with airy bangs, mini gold hoop earrings, gold leaf necklace, and slim gold bangle from height_look3_butter.png. " +
  "Natural calm breathing, bright closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const H4_LOCK =
  " Keep the exact same Vietnamese woman, her exact soft sky-blue fitted long-sleeve athletic croptop, ivory soft-flare yoga trousers, white sneakers, sporty braided side-swept ponytail, silver stud earrings, star necklace, and sky-blue smartwatch from height_look4_sky.png. " +
  "Natural calm breathing, radiant closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const JOBS = [
  // ================= VIDEO H1: NAVY POLO & SKORT (ĐẠM SẠCH + CANXI TẢO BIỂN) =================
  {
    id: "h1_s01", outPath: path.join(V1_DIR, "s01.mp4"), seconds: 6, images: [REF_H1],
    prompt:
      "Vertical 9:16 energetic sunlit commercial opening hook: beside a bright green outdoor park sports court at golden morning sunrise, the tall graceful Vietnamese woman from height_look1_navy.png reaches both arms overhead in a joyful vertical morning stretch and turns smoothly toward camera with a confident tall posture and radiant smile. Slow cinema gimbal push-in." + H1_LOCK,
  },
  {
    id: "h1_s02", outPath: path.join(V1_DIR, "s02.mp4"), seconds: 10, images: [REF_H1],
    prompt:
      "Vertical 9:16 dynamic morning athletic lifestyle shot: on the sunlit park sports court surrounded by fresh green trees, the woman from height_look1_navy.png performs light springy athletic hops and graceful posture warm-up stretches in crisp golden morning light, showcasing active healthy vitality. Smooth tracking cinema dolly." + H1_LOCK,
  },
  {
    id: "h1_s03", outPath: path.join(V1_DIR, "s03.mp4"), seconds: 8, images: [REF_H1, REF_PRO, REF_BOJ],
    prompt:
      "Vertical 9:16 dual-hero product reveal shot: standing gracefully beside a clean white outdoor wellness table in golden sunrise park light, the woman from height_look1_navy.png holds BOTH real An Vuong boxes side by side neatly near chest height — the cream-green AV Protein box from av_protein_box.png in one hand and the emerald-green Bojomi box from av_bojomi_box.png in the other — smiling proudly toward camera. Smooth slow push-in." + H1_LOCK,
  },
  {
    id: "h1_s04b", outPath: path.join(V1_DIR, "s04b.mp4"), seconds: 7, images: [REF_H1, REF_PRO],
    prompt:
      "Vertical 9:16 fresh nutrition preparation shot: at the sunlit white outdoor table beside the real AV Protein box av_protein_box.png, the woman from height_look1_navy.png pours cool clear water into a clear glass of creamy plant protein powder and stirs smoothly with a bright refreshed expression. Crisp morning sunbeams." + H1_LOCK,
  },
  {
    id: "h1_s05b", outPath: path.join(V1_DIR, "s05b.mp4"), seconds: 7, images: [REF_H1, REF_BOJ],
    prompt:
      "Vertical 9:16 warm nutrition preparation shot: on the sunlit outdoor table beside the real Bojomi box av_bojomi_box.png, the woman from height_look1_navy.png gently swirls a sleek gold spoon in a steaming glass mug of rich creamy vanilla Bojomi cereal milk with inviting warm mist rising in golden morning light." + H1_LOCK,
  },
  {
    id: "h1_s06", outPath: path.join(V1_DIR, "s06.mp4"), seconds: 11, images: [REF_H1],
    prompt:
      "Vertical 9:16 uplifting healthy payoff shot: bathed in warm golden morning sunbeams at the park court, the tall poised woman from height_look1_navy.png takes a gentle satisfied sip of her nutritious drink, lowers the glass smiling brightly and walks gracefully forward with confident tall posture and radiant energy. Smooth cinema dolly." + H1_LOCK,
  },

  // ================= VIDEO H2: IVORY LINEN + MINT CARDIGAN (4 TRỤ CỘT VÀNG GIA ĐÌNH) =================
  {
    id: "h2_s01", outPath: path.join(V2_DIR, "s01.mp4"), seconds: 7, images: [REF_H2],
    prompt:
      "Vertical 9:16 refined family-wellness opening hook: in a luminous sunlit modern light-oak dining room framed by sheer white morning curtains, the graceful Vietnamese woman from height_look2_linen.png arranges fresh wholesome breakfast bowls on the table, looks up gently toward camera with a warm reassuring expert smile. Smooth slow cinema push-in." + H2_LOCK,
  },
  {
    id: "h2_s02", outPath: path.join(V2_DIR, "s02.mp4"), seconds: 11, images: [REF_H2],
    prompt:
      "Vertical 9:16 serene healthy home lifestyle montage: bathed in soft morning sunlight in her airy modern home, the woman from height_look2_linen.png gently draws open the sheer curtains letting golden dawn light flood the tidy sunlit room, then walks calmly to her bright dining table with fresh fruits, clean water carafe, and calm nurturing harmony. Smooth slow glide." + H2_LOCK,
  },
  {
    id: "h2_s03", outPath: path.join(V2_DIR, "s03.mp4"), seconds: 9, images: [REF_H2, REF_BOJ, REF_PRO],
    prompt:
      "Vertical 9:16 dual-hero family nutrition reveal: standing gracefully beside her sunlit light-oak dining table, the woman from height_look2_linen.png presents BOTH real An Vuong boxes side by side — the Bojomi box av_bojomi_box.png and the AV Protein box av_protein_box.png — resting cleanly on the bright marble tray as she touches them gently smiling warmly toward camera. Smooth slow arc dolly." + H2_LOCK,
  },
  {
    id: "h2_s04b", outPath: path.join(V2_DIR, "s04b.mp4"), seconds: 6, images: [REF_H2, REF_BOJ],
    prompt:
      "Vertical 9:16 warm close-up lifestyle shot: on the sunlit oak family dining table beside fresh white lilies, the real Bojomi box av_bojomi_box.png stands sharply next to a steaming ceramic cup of smooth creamy vanilla cereal drink; the woman from height_look2_linen.png gently cradles the warm cup with serene healthy elegance." + H2_LOCK,
  },
  {
    id: "h2_s05a", outPath: path.join(V2_DIR, "s05a.mp4"), seconds: 6, images: [REF_H2, REF_PRO],
    prompt:
      "Vertical 9:16 fresh plant-protein close-up: on the sunlit family kitchen counter next to the real AV Protein box av_protein_box.png, the slender hands with cream leather watch of the woman from height_look2_linen.png pour cool clear water into a glass of silky golden-cream plant protein and stir effortlessly until smooth." + H2_LOCK,
  },
  {
    id: "h2_s05b", outPath: path.join(V2_DIR, "s05b.mp4"), seconds: 6, images: [REF_H2, REF_PRO],
    prompt:
      "Vertical 9:16 radiant lifestyle sip: in bright morning window light beside the AV Protein box av_protein_box.png on the table, the woman from height_look2_linen.png lifts her glass of smooth creamy plant protein, takes a gentle delighted sip and smiles warmly toward camera." + H2_LOCK,
  },
  {
    id: "h2_s06", outPath: path.join(V2_DIR, "s06.mp4"), seconds: 10, images: [REF_H2, REF_BOJ, REF_PRO],
    prompt:
      "Vertical 9:16 mindful transparent label-reading payoff: seated warmly at her bright sunlit dining table with BOTH real boxes av_bojomi_box.png and av_protein_box.png neatly displayed in front of her, the woman from height_look2_linen.png attentively inspects the clean nutrition panel on the box with calm trustworthy care, then looks up smiling radiantly toward camera. Slow cinema glide." + H2_LOCK,
  },

  // ================= VIDEO H3: BUTTER YELLOW & IVORY KITCHEN (PHA CHUẨN 2 NHIỆT ĐỘ) =================
  {
    id: "h3_s01", outPath: path.join(V3_DIR, "s01.mp4"), seconds: 7, images: [REF_H3, REF_PRO, REF_BOJ],
    prompt:
      "Vertical 9:16 crisp informative kitchen opening hook: standing behind her bright sunlit white-marble kitchen island where BOTH real boxes av_protein_box.png and av_bojomi_box.png sit neatly beside two separate crystal-clear glass tumblers, the woman from height_look3_butter.png gestures gently toward the two separate glasses with a bright helpful smile toward camera. Smooth push-in." + H3_LOCK,
  },
  {
    id: "h3_s02", outPath: path.join(V3_DIR, "s02.mp4"), seconds: 10, images: [REF_H3],
    prompt:
      "Vertical 9:16 clear educational kitchen demonstration: at her sunlit white-marble kitchen counter, the woman from height_look3_butter.png looks at a single steaming hot mug, gently shakes her head politely with an informative smile, and instead places TWO separate clean clear glasses neatly side by side on a wooden tray ready for separate preparation. Smooth slow side glide." + H3_LOCK,
  },
  {
    id: "h3_s03", outPath: path.join(V3_DIR, "s03.mp4"), seconds: 8, images: [REF_H3, REF_PRO, REF_BOJ],
    prompt:
      "Vertical 9:16 organized morning routine showcase: on the sunlit marble island, the woman from height_look3_butter.png neatly places the real AV Protein box av_protein_box.png on the left beside a cool glass water carafe and the real Bojomi box av_bojomi_box.png on the right beside a warm glass kettle, smiling brightly with organized clarity. Smooth cinema arc." + H3_LOCK,
  },
  {
    id: "h3_s04a", outPath: path.join(V3_DIR, "s04a.mp4"), seconds: 7, images: [REF_H3, REF_PRO],
    prompt:
      "Vertical 9:16 crisp cool-water preparation close-up: beside the real AV Protein box av_protein_box.png on the sunlit white-marble kitchen counter, the manicured hands with slim gold bangle of the woman from height_look3_butter.png pour crystal-clear cool room-temperature water from a clear glass pitcher into a tall glass of AV Protein powder and stir smoothly until silky creamy." + H3_LOCK,
  },
  {
    id: "h3_s05a", outPath: path.join(V3_DIR, "s05a.mp4"), seconds: 7, images: [REF_H3, REF_BOJ],
    prompt:
      "Vertical 9:16 warm 60-degree preparation close-up: beside the real Bojomi box av_bojomi_box.png on the sunlit white-marble kitchen counter, the manicured hands with slim gold bangle of the woman from height_look3_butter.png pour warm steaming water from a clear glass kettle into a clear glass mug of vanilla Bojomi cereal powder, stirring effortlessly into smooth velvety steaming milk." + H3_LOCK,
  },
  {
    id: "h3_s06", outPath: path.join(V3_DIR, "s06.mp4"), seconds: 10, images: [REF_H3, REF_BOJ, REF_PRO],
    prompt:
      "Vertical 9:16 radiant sunlit kitchen payoff shot: standing warmly in golden sunbeams at her white-marble kitchen island with BOTH real boxes av_protein_box.png and av_bojomi_box.png softly framed beside her, the woman from height_look3_butter.png takes a delightful warm sip of her smooth Bojomi vanilla drink and smiles radiantly toward camera full of vibrant morning energy. Slow cinema dolly." + H3_LOCK,
  },

  // ================= VIDEO H4: SKY BLUE STRETCH STUDIO (VẬN ĐỘNG GIÃN CƠ + DEAL 870K) =================
  {
    id: "h4_s01", outPath: path.join(V4_DIR, "s01.mp4"), seconds: 8, images: [REF_H4],
    prompt:
      "Vertical 9:16 uplifting studio fitness opening hook: inside a sun-drenched minimalist stretching studio with floor-to-ceiling windows overlooking sunlit green trees, the graceful woman from height_look4_sky.png performs an elegant overhead vertical stretch lifting gently onto her toes with tall lean poise, then lowers gracefully smiling brightly toward camera. Slow cinema push-in." + H4_LOCK,
  },
  {
    id: "h4_s02", outPath: path.join(V4_DIR, "s02.mp4"), seconds: 10, images: [REF_H4],
    prompt:
      "Vertical 9:16 dynamic graceful flexibility workout shot: in the bright sunlit oak-floor studio, the woman from height_look4_sky.png performs smooth gentle athletic stretching and light energetic warm-up hops in golden morning sunlight streaming across the studio floor, exuding vibrant youthfulness and healthy posture. Smooth tracking cinema shot." + H4_LOCK,
  },
  {
    id: "h4_s03", outPath: path.join(V4_DIR, "s03.mp4"), seconds: 10, images: [REF_H4, REF_PRO, REF_BOJ],
    prompt:
      "Vertical 9:16 dual-product studio hero reveal: standing gracefully beside a sleek minimalist white studio bench bathed in golden sunlight, the woman from height_look4_sky.png holds BOTH real boxes neatly near chest height — the AV Protein box av_protein_box.png and the Bojomi box av_bojomi_box.png — smiling radiantly toward camera. Soft sunlit bokeh, smooth cinema push-in." + H4_LOCK,
  },
  {
    id: "h4_s04", outPath: path.join(V4_DIR, "s04.mp4"), seconds: 11, images: [REF_H4, REF_PRO],
    prompt:
      "Vertical 9:16 post-stretch protein recovery shot: sitting gracefully on the sunlit studio lounge bench beside the real AV Protein box av_protein_box.png, the woman from height_look4_sky.png swirls a clear glass of smooth creamy plant protein shake, takes a refreshing sip and smiles with renewed muscle energy and light comfortable vitality. Slow smooth dolly." + H4_LOCK,
  },
  {
    id: "h4_s05b", outPath: path.join(V4_DIR, "s05b.mp4"), seconds: 8, images: [REF_H4, REF_BOJ],
    prompt:
      "Vertical 9:16 cozy studio warm-nutrition close-up: on a bright minimalist oak table beside the sunlit studio window where the real Bojomi box av_bojomi_box.png stands sharply, the woman from height_look4_sky.png gently holds a steaming glass mug of velvety vanilla Bojomi cereal milk with warm golden morning light glowing softly around her." + H4_LOCK,
  },
  {
    id: "h4_s06", outPath: path.join(V4_DIR, "s06.mp4"), seconds: 11, images: [REF_H4, REF_BOJ, REF_PRO],
    prompt:
      "Vertical 9:16 radiant closing payoff shot: standing tall and poised beside the sunlit studio floor-to-ceiling windows with BOTH real boxes av_protein_box.png and av_bojomi_box.png neatly displayed on the bright marble side table next to her, the woman from height_look4_sky.png takes a satisfied warm sip and beams joyfully toward camera full of healthy confidence. Warm sunrise lens flare, smooth dolly." + H4_LOCK,
  },
];

function extractVidBuf(res) {
  if (!res) return null;
  if (res.videoPath && fs.existsSync(res.videoPath)) return fs.readFileSync(res.videoPath);
  const b64 = res.data || res.videoBase64 || res.items?.[0]?.data || res.items?.[0]?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  return Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
}

async function runOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 200000) {
    console.log(`[SKIP] ${job.id} cached`);
    return { id: job.id, ok: true, cached: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START] ${job.id} (${job.seconds}s, ${job.images.length} refs, 9:16 ingredients) try ${attempt}/2...`);
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
      if (buf && buf.length > 200000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE] ${job.id} -> ${buf.length} bytes`);
        return { id: job.id, ok: true, bytes: buf.length };
      }
      console.warn(`[WARN] ${job.id} try ${attempt}:`, res?.error || Object.keys(res || {}));
    } catch (e) {
      console.warn(`[ERR] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 4000));
  }
  return { id: job.id, ok: false };
}

async function runPool(items, concurrency) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 3500));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await runOne(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

(async () => {
  const t0 = Date.now();
  const res = await runPool(JOBS, 2);
  const ok = res.filter((r) => r && r.ok).length;
  console.log(`\n=== 4 HEIGHT COMBO FLOW VIDEOS DONE: ${ok}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(res, null, 2));
  process.exit(ok === JOBS.length ? 0 : 1);
})();
