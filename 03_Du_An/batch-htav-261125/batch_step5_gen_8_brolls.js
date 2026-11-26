const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Module = require("node:module");
const { execFileSync } = require("node:child_process");

const appData = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
let userDataDir = path.join(appData, "infinite-canvas-flow");
try {
  const cfgRaw = JSON.parse(fs.readFileSync(path.join(appData, "infinite-canvas-flow-config.json"), "utf8"));
  if (cfgRaw && cfgRaw.dataDir && fs.existsSync(cfgRaw.dataDir)) userDataDir = cfgRaw.dataDir;
} catch {}
fs.mkdirSync(userDataDir, { recursive: true });

const ipcHandlers = {};
const origLoad = Module._load;
Module._load = function (request) {
  if (request === "electron") {
    return {
      ipcMain: { handle: (c, fn) => { ipcHandlers[c] = fn; }, on: () => {} },
      dialog: { showErrorBox: (t, m) => console.error("[Dialog]", t, m), showMessageBox: async () => ({ response: 0 }) },
      app: { getPath: (k) => (k === "userData" ? userDataDir : appData), isPackaged: false },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require("C:/AI/full studio/canvas/desktop/flow-driver.js");
const chatgpt = require("C:/AI/full studio/canvas/desktop/chatgpt-driver.js");
const fakeApp = { getPath: (k) => (k === "userData" ? userDataDir : appData), isPackaged: false };
flow.setup(fakeApp);
chatgpt.setup(fakeApp);

const POOL = "C:/AI/full studio/output/batch-htav-261125/brolls_pool";
fs.mkdirSync(POOL, { recursive: true });

const LUT_SRC = "C:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/luts_chinh_mau/10_AI_Clip_Harmonizer_Natural.cube";
const LUT_LOCAL = path.join(POOL, "_harm.cube");
fs.copyFileSync(LUT_SRC, LUT_LOCAL);

const SCENES = [
  {
    id: "br_coffee_acid",
    refTag: "ref_b_coffee",
    seconds: 4,
    refDest: path.join(POOL, "ref_coffee_acid.png"),
    dest: path.join(POOL, "br_coffee_acid.mp4"),
    imgPrompt: "Moody realistic commercial photography of a cold glass of dark iced Vietnamese black coffee sitting on an empty office desk beside a laptop in early morning light, dramatic warm-amber contrast, shallow depth of field, 50mm f/1.8.",
    vidPrompt: "Slow cinema push-in toward the sweating glass of dark iced coffee on the empty morning office desk as ice cubes glisten subtly.",
  },
  {
    id: "br_herbal_stomach_calm",
    refTag: "ref_b_stomach",
    seconds: 4,
    refDest: path.join(POOL, "ref_herbal_stomach.png"),
    dest: path.join(POOL, "br_herbal_stomach_calm.mp4"),
    imgPrompt: "Bright natural botanical studio photography of fresh golden turmeric slices, purple-green Da Cam herbal leaves, and a crystal bowl of warm golden herbal essence glowing in soft morning sunlight on a clean marble table, 85mm macro.",
    vidPrompt: "Graceful slow-motion cinema glide around the fresh golden turmeric slices, herbal leaves, and warm golden essence rippling gently in sunlight.",
  },
  {
    id: "br_curcumilk_warm_cup",
    refTag: "ref_b_curcu",
    seconds: 4,
    refDest: path.join(POOL, "ref_curcumilk_cup.png"),
    dest: path.join(POOL, "br_curcumilk_warm_cup.mp4"),
    imgPrompt: "Warm cozy afternoon office photography of a clear glass mug filled with silky golden-vanilla turmeric coconut milk with delicate warm steam rising on a sunlit wooden desk beside fresh vanilla pods, 85mm f/1.8.",
    vidPrompt: "Slow cinema dolly-in toward the warm golden-vanilla turmeric milk mug as soft delicate steam rises in golden afternoon sunbeams.",
  },
  {
    id: "br_apple_oxidation",
    refTag: "ref_b_apple",
    seconds: 4,
    refDest: path.join(POOL, "ref_apple_oxid.png"),
    dest: path.join(POOL, "br_apple_oxidation.mp4"),
    imgPrompt: "Crisp high-end skincare metaphor macro photography of two freshly sliced apple halves side by side on white marble: left apple half oxidized dull brown and dry, right apple half dewy crisp bright ivory-white with water droplets, 85mm.",
    vidPrompt: "Smooth slow macro camera pan comparing the dull browned apple half on the left with the bright dewy fresh apple half glistening on the right.",
  },
  {
    id: "br_two_roses_moisture",
    refTag: "ref_b_roses",
    seconds: 4,
    refDest: path.join(POOL, "ref_two_roses.png"),
    dest: path.join(POOL, "br_two_roses_moisture.mp4"),
    imgPrompt: "Artistic luxury beauty macro photography of two pink Bulgarian rose blooms side by side on soft champagne silk: left rose dry and slightly wilted, right rose lush, velvety pink and covered in sparkling morning dewdrops, 85mm f/1.8.",
    vidPrompt: "Gentle slow-motion cinema track from the dry rose petal on the left to the lush velvety pink rose glistening with fresh dewdrops on the right.",
  },
  {
    id: "br_feminine_herbs_pure",
    refTag: "ref_b_femherbs",
    seconds: 4,
    refDest: path.join(POOL, "ref_fem_herbs.png"),
    dest: path.join(POOL, "br_feminine_herbs_pure.mp4"),
    imgPrompt: "Pure spa botanical commercial photography of white Chamomile flowers, golden Honeysuckle blossoms, fresh green Betel leaves, and translucent Aloe Vera gel droplets floating on crystal-clear pure water in soft daylight, 85mm.",
    vidPrompt: "Serene slow-motion water ripple carrying fresh white chamomile blossoms, honeysuckle, and green herbal leaves in crystal-clear sunlit water.",
  },
  {
    id: "br_menstrual_cramp_tea",
    refTag: "ref_b_cramp",
    seconds: 4,
    refDest: path.join(POOL, "ref_cramp_tea.png"),
    dest: path.join(POOL, "br_menstrual_cramp_tea.mp4"),
    imgPrompt: "Warm lifestyle wellness photography of a serene 32-year-old Vietnamese woman in a soft cream cardigan resting comfortably on a sunlit sofa holding a warm porcelain cup of ruby-amber Oriental herbal tea with Angelica root and saffron petals on the table, 85mm.",
    vidPrompt: "Gentle slow cinema push-in as the serene Vietnamese woman holds the warm herbal tea cup with a calm relieved smile in soft golden daylight.",
  },
  {
    id: "br_office_8h_fresh",
    refTag: "ref_b_office",
    seconds: 4,
    refDest: path.join(POOL, "ref_office_fresh.png"),
    dest: path.join(POOL, "br_office_8h_fresh.mp4"),
    imgPrompt: "Bright modern Vietnamese office photography of an elegant 32-year-old Vietnamese office woman in breathable light linen blazer standing up refreshed beside her sunlit glass office desk and green indoor plants, poised confident smile, 85mm.",
    vidPrompt: "Smooth slow cinema tracking shot as the poised Vietnamese office woman stands refreshed beside her sunlit desk with a gentle confident smile.",
  },
];

async function generateRefImageWithFallback(sc, idx) {
  if (fs.existsSync(sc.refDest) && fs.statSync(sc.refDest).size > 15000) {
    console.log(`[${sc.id}] Cached ref image`);
    return;
  }
  if (idx > 0) await new Promise((r) => setTimeout(r, (idx % 3) * 1800));
  const fullImgPrompt = sc.imgPrompt + " Pure photorealistic commercial photography, clean composition, ZERO text, ZERO letters, ZERO words, ZERO logos, ZERO watermarks.";

  for (let t = 1; t <= 2; t++) {
    try {
      console.log(`[${sc.id}] ChatGPT HTPM image (try #${t})...`);
      const res = await ipcHandlers["chatgpt:generate-image"](null, {
        prompt: fullImgPrompt,
        model: "chatgpt-image",
        ratio: "16:9",
        quality: "auto",
        count: 1,
        images: [],
      });
      if (res && res.ok && res.data) {
        fs.writeFileSync(sc.refDest, Buffer.isBuffer(res.data) ? res.data : Buffer.from(res.data));
        console.log(`[${sc.id}] Saved via ChatGPT!`);
        return;
      }
    } catch (e) {
      console.warn(`[${sc.id}] ChatGPT try #${t} err:`, e.message || e);
    }
  }

  for (const flowImgModel of ["Nano Banana 2", "Nano Banana Pro"]) {
    try {
      console.log(`[${sc.id}] Fallback Flow image (${flowImgModel})...`);
      const res = await ipcHandlers["flow:generate-image"](null, {
        prompt: fullImgPrompt,
        model: flowImgModel,
        aspect: "landscape",
        count: 1,
        images: [],
      });
      if (res && res.ok && res.data) {
        fs.writeFileSync(sc.refDest, Buffer.isBuffer(res.data) ? res.data : Buffer.from(res.data));
        console.log(`[${sc.id}] Saved via Flow (${flowImgModel})!`);
        return;
      }
    } catch (e) {
      console.warn(`[${sc.id}] Flow image err:`, e.message || e);
    }
  }
  throw new Error(`[${sc.id}] All image tiers failed!`);
}

async function generateRefVideo(sc, wIdx) {
  if (fs.existsSync(sc.dest) && fs.statSync(sc.dest).size > 25000) {
    console.log(`[${sc.id}] Cached video`);
    return;
  }
  if (wIdx > 0) await new Promise((r) => setTimeout(r, wIdx * 5000));

  const refSmallJpg = sc.refDest + ".flow1280.jpg";
  execFileSync("ffmpeg", [
    "-y", "-v", "error", "-i", sc.refDest,
    "-vf", "scale='min(1280,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease",
    "-q:v", "3", refSmallJpg,
  ]);
  const refSmallBuf = fs.readFileSync(refSmallJpg);
  try { fs.unlinkSync(refSmallJpg); } catch {}

  const safeVidPrompt = `${sc.vidPrompt} Natural calm motion, closed or gently smiling lips, zero speaking, zero lip-syncing, no text overlays, no watermarks, no logos.`;
  let vidRes = null;
  for (let vTry = 1; vTry <= 3; vTry++) {
    console.log(`[${sc.id}] Flow Ingredients Video (${sc.seconds}s, try #${vTry})...`);
    vidRes = await ipcHandlers["flow:generate-video"](null, {
      prompt: safeVidPrompt,
      model: "Omni 1.2 Flash",
      aspect: "landscape",
      resolution: "720p",
      seconds: sc.seconds,
      count: 1,
      mode: "ingredients",
      images: [{ mime: "image/jpeg", base64: refSmallBuf.toString("base64"), name: `${sc.refTag}.jpg` }],
    });
    if (vidRes && vidRes.ok && vidRes.data) break;
    await new Promise((r) => setTimeout(r, 7000));
  }
  if (!vidRes || !vidRes.ok || !vidRes.data) {
    throw new Error(`[${sc.id}] Flow video failed: ${vidRes && vidRes.error}`);
  }

  const rawMp4 = sc.dest + ".raw.mp4";
  fs.writeFileSync(rawMp4, Buffer.isBuffer(vidRes.data) ? vidRes.data : Buffer.from(vidRes.data));
  // Use CPU libx264 veryfast so 0% GPU/NVENC contention with batch_step4!
  execFileSync("ffmpeg", [
    "-y", "-v", "error", "-ss", "0.20", "-i", rawMp4,
    "-r", "30", "-fps_mode", "cfr", "-an",
    "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_harm.cube[bg];[a][bg]blend=all_expr=A*0.35+B*0.65[v]",
    "-map", "[v]",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p",
    sc.dest,
  ], { cwd: POOL });
  try { fs.unlinkSync(rawMp4); } catch {}
  console.log(`[${sc.id}] VIDEO READY -> ${sc.dest}`);
}

async function main() {
  let cImg = 0;
  async function imgWorker() {
    while (cImg < SCENES.length) {
      const idx = cImg++;
      await generateRefImageWithFallback(SCENES[idx], idx);
    }
  }
  await Promise.all([imgWorker(), imgWorker(), imgWorker()]);

  let cVid = 0;
  async function vidWorker(wIdx) {
    while (cVid < SCENES.length) {
      const idx = cVid++;
      await generateRefVideo(SCENES[idx], wIdx);
    }
  }
  await Promise.all([vidWorker(0), vidWorker(1)]);

  try { fs.unlinkSync(LUT_LOCAL); } catch {}
  flow.destroy();
  console.log("ALL_8_POOL_BROLLS_READY!");
  process.exit(0);
}

main().catch((err) => {
  console.error("POOL_BROLL_ERR:", err);
  try { flow.destroy(); } catch {}
  process.exit(1);
});
