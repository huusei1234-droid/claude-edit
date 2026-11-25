/**
 * Ngày 01 Phần 2 (24/11/2026): Tạo 14 clip Video Dọc 9:16 (Omni 1.2 Flash, mode: "ingredients", 720p)
 * - Video 03 (Bojomi — 7 clips): Khóa diện mạo Look #2 (Sơ mi lụa kem + tóc búi thấp + bông tai ngọc trai + dây chuyền vàng)
 * - Video 04 (Collamela — 7 clips): Khóa diện mạo Look #3 (Đầm lụa hồng đào + xoăn kẹp ngọc trai + bông tai pha lê + dây chuyền giọt sương)
 * Chạy êm ái concurrency = 2 (nhả tải Google Flow, 0% rate-limit!).
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const ASSETS_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\01_ChatGPT_Assets";
const CUTOUT_DIR = "d:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\brand_kits\\07_An_Vuong_Pharma\\02_San_Pham_Cutout_PNG";
const V3_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\video_03_bojomi\\07_HyperFrames_Project\\assets\\videos";
const V4_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\video_04_collamela\\07_HyperFrames_Project\\assets\\videos";
fs.mkdirSync(V3_DIR, { recursive: true });
fs.mkdirSync(V4_DIR, { recursive: true });

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

const REF_L2 = loadImg(path.join(ASSETS_DIR, "N01_LOOK2_BOJOMI_9x16.png"), "n01_look2_office.png");
const REF_L3 = loadImg(path.join(ASSETS_DIR, "N01_LOOK3_COLLAMELA_9x16.png"), "n01_look3_peach.png");
const REF_BOJ = loadImg(path.join(CUTOUT_DIR, "av02_bojomi_a.png"), "av_bojomi_box.png");
const REF_COL = loadImg(path.join(CUTOUT_DIR, "av03_collamela_a.png"), "av_collamela_box.png");

const L2_LOCK =
  " Keep the exact same Vietnamese woman, her exact ivory silk V-neck office blouse, beige trousers, low Korean bun hairstyle with wispy bangs, teardrop pearl earrings, gold dainty necklace, and brown leather watch from n01_look2_office.png. " +
  "Natural calm breathing, gentle closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const L3_LOCK =
  " Keep the exact same Vietnamese woman, her exact blush peach-pink satin silk cowl-neck dress, loose wavy hair with ivory pearl claw clip, sparkling flower crystal earrings, and silver teardrop necklace from n01_look3_peach.png. " +
  "Natural calm breathing, gentle closed-mouth radiant smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const JOBS = [
  // ===================== VIDEO 03: BOJOMI (7 unique Flow clips) =====================
  {
    id: "v3_s01",
    outPath: path.join(V3_DIR, "s01.mp4"),
    seconds: 5,
    images: [REF_L2],
    prompt:
      "Vertical 9:16 commercial opening hook: the young Vietnamese office woman from n01_look2_office.png stands gracefully in her sunlit bright white-marble office kitchen holding her warm steaming ceramic mug of vanilla cereal milk, turning smoothly toward camera with a confident poised smile. Slow cinematic push-in, soft golden morning sunbeams." +
      L2_LOCK,
  },
  {
    id: "v3_s02",
    outPath: path.join(V3_DIR, "s02.mp4"),
    seconds: 7,
    images: [REF_L2],
    prompt:
      "Vertical 9:16 thoughtful lifestyle scene: the same Vietnamese office woman from n01_look2_office.png sitting at her sleek white desk carefully holding up a plain unbranded white supplement pill bottle, inspecting the nutrition label thoughtfully with gentle curiosity and calm focus, soft daylight from tall office windows, smooth slow side glide." +
      L2_LOCK,
  },
  {
    id: "v3_s03",
    outPath: path.join(V3_DIR, "s03.mp4"),
    seconds: 8,
    images: [REF_L2, REF_BOJ],
    prompt:
      "Vertical 9:16 hero product reveal commercial shot: the elegant office woman from n01_look2_office.png stands in bright sunlit studio light beside her white marble table, holding up the real green-and-cream Bojomi box from av_bojomi_box.png gracefully near chest height with a warm reassuring smile. Golden sunlight bokeh gleams gently behind, smooth slow arc dolly." +
      L2_LOCK,
  },
  {
    id: "v3_s04a",
    outPath: path.join(V3_DIR, "s04a.mp4"),
    seconds: 7,
    images: [REF_BOJ],
    prompt:
      "Vertical 9:16 luxury pharmaceutical 3D CGI macro commercial visualization matching the emerald-green and champagne-gold palette of av_bojomi_box.png: luminous crystalline white-pearl marine calcium spheres rising from delicate red sea algae, interlaced with warm golden sunlight ribbons and creamy swirling vanilla oat milk droplets in bright sunlit studio space. Slow motion 24fps, zero text, zero letters, zero watermarks.",
  },
  {
    id: "v3_s04b",
    outPath: path.join(V3_DIR, "s04b.mp4"),
    seconds: 7,
    images: [REF_L2, REF_BOJ],
    prompt:
      "Vertical 9:16 close-up lifestyle nutrition shot: on a sunlit white marble table beside fresh white tulips, the real Bojomi box av_bojomi_box.png stands sharply next to a steaming glass mug of smooth creamy vanilla cereal drink; the office woman from n01_look2_office.png gently swirls a sleek gold spoon in the warm silky beverage with a serene appreciative expression." +
      L2_LOCK,
  },
  {
    id: "v3_s05",
    outPath: path.join(V3_DIR, "s05.mp4"),
    seconds: 11,
    images: [REF_L2, REF_BOJ],
    prompt:
      "Vertical 9:16 appetizing beverage preparation close-up: the slender manicured hands with brown leather watch of the woman from n01_look2_office.png pour warm steaming water from a clear glass kettle into a ceramic cup of fragrant vanilla cereal powder next to the Bojomi box av_bojomi_box.png softly framed in background, stirring effortlessly until smooth velvety creamy cereal milk forms with rising warm mist." +
      L2_LOCK,
  },
  {
    id: "v3_s06",
    outPath: path.join(V3_DIR, "s06.mp4"),
    seconds: 8,
    images: [REF_L2],
    prompt:
      "Vertical 9:16 warm lifestyle payoff shot: the refined office woman from n01_look2_office.png stands gracefully near bright sunlit sheer curtains holding her warm ceramic mug of vanilla Bojomi cereal milk, takes a gentle satisfied sip, lowers the mug slightly and smiles radiantly with healthy poised elegance. Warm pearl sunlight flare, slow cinema glide." +
      L2_LOCK,
  },

  // ===================== VIDEO 04: COLLAMELA (7 unique Flow clips) =====================
  {
    id: "v4_s01",
    outPath: path.join(V4_DIR, "s01.mp4"),
    seconds: 5,
    images: [REF_L3],
    prompt:
      "Vertical 9:16 luxury beauty commercial opening hook: the young Vietnamese woman from n01_look3_peach.png in her blush peach satin dress stands in luminous pearl-rose vanity light, gently touching her radiant dewy cheek with delicate fingertips while turning softly toward camera with a glowing captivating smile. Slow cinema dolly-in, floating soft champagne bokeh." +
      L3_LOCK,
  },
  {
    id: "v4_s02",
    outPath: path.join(V4_DIR, "s02.mp4"),
    seconds: 9,
    images: [REF_L3],
    prompt:
      "Vertical 9:16 intimate luxury skincare ritual shot: the woman from n01_look3_peach.png sits gracefully before her sunlit pearl-marble vanity mirror framed by soft pink peonies and warm fairy-like bokeh lamps, softly brushing a lock of glossy wavy hair behind her crystal-earring ear and admiring her smooth hydrated skin in the mirror with calm festive anticipation. Slow cinema pan." +
      L3_LOCK,
  },
  {
    id: "v4_s03",
    outPath: path.join(V4_DIR, "s03.mp4"),
    seconds: 8,
    images: [REF_L3, REF_COL],
    prompt:
      "Vertical 9:16 luxury beauty hero product reveal: the woman from n01_look3_peach.png smiles radiantly in luminous sunlit pearl-blush beauty studio light, presenting the real white-and-emerald Collamela box from av_collamela_box.png gracefully near chest height with delicate golden sparkling light particles floating around the frame. Slow smooth commercial push-in." +
      L3_LOCK,
  },
  {
    id: "v4_s04a",
    outPath: path.join(V4_DIR, "s04a.mp4"),
    seconds: 6,
    images: [REF_COL],
    prompt:
      "Vertical 9:16 ultra-luxury 3D CGI beauty commercial visualization matching the honey-gold and emerald elegance of av_collamela_box.png: glistening golden honey-amber collagen tripeptide liquid droplets merging with crystal-clear translucent hyaluronic acid water spheres and delicate rosy-peach blossom petals swirling in luminous champagne studio light. Slow motion 24fps, zero text, zero letters, zero watermarks.",
  },
  {
    id: "v4_s04b",
    outPath: path.join(V4_DIR, "s04b.mp4"),
    seconds: 6,
    images: [REF_COL],
    prompt:
      "Vertical 9:16 ultra-luxury 3D CGI cosmetic nutrition macro shot matching the fresh peach and champagne-gold tone of av_collamela_box.png: fresh dewy ripe pink peach slices splashing gently into luminous golden-rose hydration ripples with sparkling crystal Vitamin C droplets and soft pale-pink peony petals floating gracefully in bright sunlit pearl studio light. Slow motion 24fps, zero text, zero letters, zero watermarks.",
  },
  {
    id: "v4_s05",
    outPath: path.join(V4_DIR, "s05.mp4"),
    seconds: 8,
    images: [REF_L3, REF_COL],
    prompt:
      "Vertical 9:16 aesthetic beauty beverage preparation close-up on a sunlit pearl-white marble table with the Collamela box av_collamela_box.png standing cleanly nearby and pale-pink petals: delicate hands of the woman from n01_look3_peach.png pour sparkling cool clear water into a stemmed crystal glass containing peach collagen powder, swirling gently into a crystal-clear translucent rosy-peach drink catching golden sunlight." +
      L3_LOCK,
  },
  {
    id: "v4_s06",
    outPath: path.join(V4_DIR, "s06.mp4"),
    seconds: 7,
    images: [REF_L3],
    prompt:
      "Vertical 9:16 radiant festive payoff shot: the woman from n01_look3_peach.png lifts her crystal glass of translucent peach collagen drink, takes a light refreshed sip, and beams warmly toward camera with dewy glowing skin and joyful holiday-ready confidence amidst warm sunlit golden-pink bokeh. Smooth slow push-in." +
      L3_LOCK,
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
    console.log(`[SKIP] ${job.id} cached`);
    return { id: job.id, ok: true, cached: true };
  }
  console.log(`[START] ${job.id} (${job.seconds}s, ${job.images.length} refs, 9:16 ingredients)...`);
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
        console.log(`[DONE] ${job.id} -> ${buf.length} bytes`);
        return { id: job.id, ok: true, bytes: buf.length };
      }
    }
    console.warn(`[WARN] ${job.id}:`, res?.error || "empty buffer");
    return { id: job.id, ok: false, error: res?.error || "empty" };
  } catch (err) {
    console.error(`[ERR] ${job.id}:`, err.message);
    return { id: job.id, ok: false, error: err.message };
  }
}

// Gentle concurrency = 2 to stay 100% smooth on Google Flow!
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
  console.log(`\n=== V3 & V4 FLOW VIDEOS DONE: ${okCount}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(results, null, 2));
  process.exit(okCount === JOBS.length ? 0 : 1);
})();
