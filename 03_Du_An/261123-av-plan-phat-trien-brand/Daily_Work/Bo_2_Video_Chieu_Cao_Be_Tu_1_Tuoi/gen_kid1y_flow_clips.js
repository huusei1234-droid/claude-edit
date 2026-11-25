/**
 * Bộ 2 Video Combo Chiều Cao Bé Từ 1 Tuổi Trở Lên (BOJOMI + AV PROTEIN — 39.5s & 40.5s <= 60s!):
 * QUY TẮC THÉP CHỐNG SAI SẢN PHẨM 100%:
 * - TUYỆT ĐỐI KHÔNG đưa cùng lúc 2 hộp (AV Protein + Bojomi) vào 1 prompt Flow (tránh AI trộn chữ 2 hộp!).
 * - Các cảnh giới thiệu BỘ ĐÔI (m1_s03, m2_s01, m2_s05): sinh cảnh mẹ tươi cười bên bàn sáng KHÔNG có hộp AI giả -> ghép 100% hộp thật IS-Net PNG nổi 3D chuẩn từng pixel trong HyperFrames!
 * - Các cảnh pha từng ly riêng: tối đa 1 hộp duy nhất (chỉ AV Protein hoặc chỉ Bojomi) + kiểm định visual QC từng clip trước khi render!
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_2_Video_Chieu_Cao_Be_Tu_1_Tuoi";
const ASSETS_DIR = path.join(WORK_DIR, "01_ChatGPT_Assets");
const CUTOUT_DIR = "d:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\brand_kits\\07_An_Vuong_Pharma\\02_San_Pham_Cutout_PNG";

const V1_DIR = path.join(WORK_DIR, "kid1y_01_giai_doan_vang", "07_HyperFrames_Project", "assets", "videos");
const V2_DIR = path.join(WORK_DIR, "kid1y_02_pha_chuan_2_ly", "07_HyperFrames_Project", "assets", "videos");
for (const d of [V1_DIR, V2_DIR]) fs.mkdirSync(d, { recursive: true });

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

const REF_M1 = loadImg(path.join(ASSETS_DIR, "KID1Y_LOOK1_BLUSH_DRESS_9x16.png"), "kid1y_look1_blush.png");
const REF_M2 = loadImg(path.join(ASSETS_DIR, "KID1Y_LOOK2_SAGE_BLOUSE_9x16.png"), "kid1y_look2_sage.png");
const REF_BOJ = loadImg(path.join(CUTOUT_DIR, "av02_bojomi_b.png"), "av_bojomi_box.png");
const REF_PRO = loadImg(path.join(CUTOUT_DIR, "av01_protein_a.png"), "av_protein_box.png");

const M1_LOCK =
  " Keep the exact same Vietnamese young mom, her exact pastel blush-pink belted shirt midi dress, half-up wavy hair with ivory silk bow ribbon, small pearl stud earrings, fine gold necklace, and white-strap watch from kid1y_look1_blush.png. " +
  "Natural calm breathing, warm loving closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const M2_LOCK =
  " Keep the exact same Vietnamese young mom, her exact soft sage-green short puff-sleeve cotton blouse, crisp-ivory pleated midi skirt, low Korean chignon bun with airy bangs, mini gold hoops, gold flower necklace, and beige-leather watch from kid1y_look2_sage.png. " +
  "Natural calm breathing, bright reassuring closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const JOBS = [
  // ================= VIDEO M1: BLUSH PINK DRESS (39.50s <= 60s!) =================
  {
    id: "m1_s01", outPath: path.join(V1_DIR, "s01.mp4"), seconds: 5, images: [REF_M1],
    prompt:
      "Vertical 9:16 warm sunlit family-wellness opening hook: inside her luminous sunlit Scandinavian living room beside a cute natural-wood kids height chart on the bright cream wall, the graceful young mom from kid1y_look1_blush.png gently touches the wooden height ruler with loving care and turns smoothly toward camera with a warm radiant smile. Golden morning sunbeams, slow cinema push-in, NO product boxes." + M1_LOCK,
  },
  {
    id: "m1_s02", outPath: path.join(V1_DIR, "s02.mp4"), seconds: 7, images: [REF_M1],
    prompt:
      "Vertical 9:16 wholesome family nutrition lifestyle shot: standing beside her bright sunlit light-oak family dining table neatly set with fresh fruits, clean breakfast bowls, and two plain crystal-clear glass cups bathed in warm morning sunbeams, the young mom from kid1y_look1_blush.png arranges the healthy morning table thoughtfully with calm loving poise. Smooth slow cinema glide, NO product boxes." + M1_LOCK,
  },
  {
    id: "m1_s03", outPath: path.join(V1_DIR, "s03.mp4"), seconds: 7, images: [REF_M1],
    prompt:
      "Vertical 9:16 bright clean editorial showcase shot: standing poised slightly to the right side of the frame in her sunlit modern living room filled with soft warm golden sunlight and airy bokeh, the young mom from kid1y_look1_blush.png smiles brightly and warmly toward camera with welcoming open gesture toward clean bright sunlit space on the left-center for real studio product box compositing. ZERO boxes in scene, ZERO text, slow smooth dolly." + M1_LOCK,
  },
  {
    id: "m1_s04b", outPath: path.join(V1_DIR, "s04b.mp4"), seconds: 5, images: [REF_M1, REF_PRO],
    prompt:
      "Vertical 9:16 crisp single-product preparation shot: on the sunlit oak dining table where ONLY the exact cream-and-green AV PROTEIN box from av_protein_box.png stands cleanly upright with sharp legible original label, the young mom from kid1y_look1_blush.png pours cool clear water into a clear glass cup of smooth creamy plant protein and stirs gently with a warm caring smile." + M1_LOCK,
  },
  {
    id: "m1_s05b", outPath: path.join(V1_DIR, "s05b.mp4"), seconds: 5, images: [REF_M1, REF_BOJ],
    prompt:
      "Vertical 9:16 crisp single-product preparation shot: on the sunlit oak dining table where ONLY the exact emerald-and-cream BOJOMI box from av_bojomi_box.png stands cleanly upright with sharp legible original label, the young mom from kid1y_look1_blush.png swirls a sleek gold spoon in a steaming warm glass mug of creamy fragrant vanilla cereal milk with loving smile." + M1_LOCK,
  },

  // ================= VIDEO M2: SAGE GREEN BLOUSE (40.50s <= 60s!) =================
  {
    id: "m2_s01", outPath: path.join(V2_DIR, "s01.mp4"), seconds: 6, images: [REF_M2],
    prompt:
      "Vertical 9:16 bright sunlit kitchen opening hook: standing gracefully behind her luminous white-marble family kitchen island where two plain crystal-clear glass cups sit neatly on a wooden tray bathed in golden morning window light, the young mom from kid1y_look2_sage.png smiles warmly toward camera with reassuring modern-mom elegance. ZERO product boxes in scene, smooth slow push-in." + M2_LOCK,
  },
  {
    id: "m2_s02", outPath: path.join(V2_DIR, "s02.mp4"), seconds: 7, images: [REF_M2],
    prompt:
      "Vertical 9:16 clear kitchen demonstration shot: at her sunlit white-marble kitchen island, the young mom from kid1y_look2_sage.png looks at a single steaming hot mug, gently shakes her head politely with an informative smile, and instead places TWO separate clean clear glass cups neatly side by side on a light-oak tray. Smooth slow side glide, ZERO product boxes." + M2_LOCK,
  },
  {
    id: "m2_s03a", outPath: path.join(V2_DIR, "s03a.mp4"), seconds: 5, images: [REF_M2, REF_PRO],
    prompt:
      "Vertical 9:16 crisp single-product cool-water prep close-up: on the sunlit white-marble kitchen island where ONLY the exact cream-and-green AV PROTEIN box from av_protein_box.png stands cleanly upright with sharp accurate original packaging, the manicured hands with beige-leather watch of the mom from kid1y_look2_sage.png pour clear cool water from a glass pitcher into a glass cup of creamy AV Protein shake and stir smoothly." + M2_LOCK,
  },
  {
    id: "m2_s04a", outPath: path.join(V2_DIR, "s04a.mp4"), seconds: 5, images: [REF_M2, REF_BOJ],
    prompt:
      "Vertical 9:16 crisp single-product warm-water prep close-up: on the sunlit white-marble kitchen island where ONLY the exact emerald-and-cream BOJOMI box from av_bojomi_box.png stands cleanly upright with sharp accurate original packaging, the manicured hands with beige-leather watch of the mom from kid1y_look2_sage.png pour warm steaming water from a clear glass kettle into a cup of fragrant vanilla Bojomi cereal milk and stir smoothly." + M2_LOCK,
  },
  {
    id: "m2_s05", outPath: path.join(V2_DIR, "s05.mp4"), seconds: 7, images: [REF_M2],
    prompt:
      "Vertical 9:16 warm joyful family payoff shot: standing in glowing golden sunrise rays beside her sunlit white-marble kitchen island holding a warm steaming glass cup of creamy vanilla milk with fresh fruit nearby, the young mom from kid1y_look2_sage.png takes a gentle delighted sip and smiles radiantly toward camera full of loving warmth. ZERO product boxes in background, smooth cinema dolly." + M2_LOCK,
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
  console.log(`\n=== 2 KID 1Y+ FLOW VIDEOS DONE: ${ok}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(res, null, 2));
  process.exit(ok === JOBS.length ? 0 : 1);
})();
