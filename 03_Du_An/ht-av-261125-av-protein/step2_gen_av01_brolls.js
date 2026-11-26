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

const PROJ = "C:/AI/full studio/output/ht-av-261125";
const MEDIA = path.join(PROJ, "media");
const LUT_SRC = "C:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/luts_chinh_mau/10_AI_Clip_Harmonizer_Natural.cube";
const LUT_LOCAL = path.join(MEDIA, "_harm.cube");
fs.copyFileSync(LUT_SRC, LUT_LOCAL);

const speakerJpg = path.join(PROJ, "aroll", "_speaker_anchor_1280.jpg");
execFileSync("ffmpeg", [
  "-y", "-v", "error", "-i", path.join(PROJ, "aroll", "speaker_ref.png"),
  "-vf", "scale='min(1280,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease",
  "-q:v", "3", speakerJpg,
]);
const speakerB64 = fs.readFileSync(speakerJpg).toString("base64");

const SCENES = [
  {
    id: "av01",
    refTag: "ref_htav_01",
    useSpeaker: false,
    seconds: 4,
    refDest: path.join(MEDIA, "ref_htav_01_carb.png"),
    dest: path.join(MEDIA, "av_01_carb_spike.mp4"),
    imgPrompt: "Warm morning dining photography of a high-carbohydrate Vietnamese breakfast on a wooden table: a steaming bowl of white rice noodles, crispy white baguette slices, and sweet iced condensed milk coffee in golden sunbeams, shallow depth of field, 50mm f/1.8.",
    vidPrompt: "Smooth slow cinema push-in across the steaming bowl of white rice noodles and white bread slices on the morning table in warm sunbeams.",
  },
  {
    id: "av02",
    refTag: "ref_htav_02",
    useSpeaker: true,
    seconds: 4,
    refDest: path.join(MEDIA, "ref_htav_02_sleepy.png"),
    dest: path.join(MEDIA, "av_02_10am_sleepy.mp4"),
    imgPrompt: "Using the exact same 38-year-old Vietnamese woman in a crisp white collared shirt from the reference image: sitting at a modern wooden office desk in front of an open laptop at 10 AM, resting her forehead on her fingers with mid-morning drowsiness and energy crash, natural daylight, 85mm.",
    vidPrompt: "Slow cinema push-in toward the drowsy Vietnamese office woman in a white shirt sitting before her laptop as she rubs her temple tiredly with closed lips.",
  },
  {
    id: "av03",
    refTag: "ref_htav_03",
    useSpeaker: false,
    seconds: 4,
    refDest: path.join(MEDIA, "ref_htav_03_pearice.png"),
    dest: path.join(MEDIA, "av_03_pea_rice_shake.mp4"),
    imgPrompt: "Bright commercial studio food photography of a crystal glass shaker filled with silky creamy vanilla plant-based protein smoothie surrounded by fresh green garden pea pods and wholesome golden rice grains on a sunlit marble counter, clean wellness aesthetic, 85mm.",
    vidPrompt: "Graceful slow-motion cinema tracking glide around the clear glass of creamy plant-based protein shake beside fresh green peas and rice grains in bright morning sunlight.",
  },
  {
    id: "av04",
    refTag: "ref_htav_04",
    useSpeaker: true,
    seconds: 4,
    refDest: path.join(MEDIA, "ref_htav_04_vitality.png"),
    dest: path.join(MEDIA, "av_04_toned_vitality.mp4"),
    imgPrompt: "Using the exact same radiant 38-year-old Vietnamese woman in a crisp white shirt from the reference image: standing poised and energetic by a sunlit office window holding a sleek clear shaker cup of creamy plant protein smoothie, toned healthy vitality, warm confident smile, 85mm f/1.8.",
    vidPrompt: "Warm slow cinema dolly-in through morning sunbeams as the radiant energetic Vietnamese woman holds the creamy protein shaker cup and smiles with calm vitality.",
  },
];

async function generateRefImageWithFallback(sc, idx) {
  if (fs.existsSync(sc.refDest) && fs.statSync(sc.refDest).size > 15000) {
    console.log(`[${sc.id}] Cached ref image -> ${sc.refDest}`);
    return;
  }
  if (idx > 0) await new Promise((r) => setTimeout(r, (idx % 3) * 1500));
  const fullImgPrompt = sc.imgPrompt + " Pure photorealistic commercial photography, clean composition, ZERO text, ZERO letters, ZERO words, ZERO logos, ZERO watermarks.";
  const imgs = sc.useSpeaker ? [{ mime: "image/jpeg", base64: speakerB64, name: "htav_speaker_anchor.jpg" }] : [];

  // Tier 1 & 2: ChatGPT HTPM (2 tries)
  for (let t = 1; t <= 2; t++) {
    try {
      console.log(`[${sc.id}] Trying ChatGPT HTPM image (try #${t})...`);
      const res = await ipcHandlers["chatgpt:generate-image"](null, {
        prompt: fullImgPrompt,
        model: "chatgpt-image",
        ratio: "16:9",
        quality: "auto",
        count: 1,
        images: imgs,
      });
      if (res && res.ok && res.data) {
        fs.writeFileSync(sc.refDest, Buffer.isBuffer(res.data) ? res.data : Buffer.from(res.data));
        console.log(`[${sc.id}] Saved ${sc.refDest} via ChatGPT!`);
        return;
      }
      console.warn(`[${sc.id}] ChatGPT try #${t} non-ok:`, res && res.error);
    } catch (e) {
      console.warn(`[${sc.id}] ChatGPT try #${t} err:`, e.message || e);
    }
  }

  // Tier 3: Google Flow Nano Banana
  for (const flowImgModel of ["Nano Banana 2", "Nano Banana Pro"]) {
    try {
      console.log(`[${sc.id}] Fallback Flow image (${flowImgModel})...`);
      const res = await ipcHandlers["flow:generate-image"](null, {
        prompt: fullImgPrompt,
        model: flowImgModel,
        aspect: "landscape",
        count: 1,
        images: imgs,
      });
      if (res && res.ok && res.data) {
        fs.writeFileSync(sc.refDest, Buffer.isBuffer(res.data) ? res.data : Buffer.from(res.data));
        console.log(`[${sc.id}] Saved ${sc.refDest} via Flow (${flowImgModel})!`);
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
    console.log(`[${sc.id}] Cached video -> ${sc.dest}`);
    return;
  }
  if (wIdx > 0) await new Promise((r) => setTimeout(r, wIdx * 5500));

  const refSmallJpg = sc.refDest + ".flow1280.jpg";
  execFileSync("ffmpeg", [
    "-y", "-v", "error", "-i", sc.refDest,
    "-vf", "scale='min(1280,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease",
    "-q:v", "3", refSmallJpg,
  ]);
  const refSmallBuf = fs.readFileSync(refSmallJpg);
  try { fs.unlinkSync(refSmallJpg); } catch {}

  const safeVidPrompt = `${sc.vidPrompt} Natural calm breathing, closed or gently smiling lips, zero speaking, zero lip-syncing, no text overlays, no watermarks, no logos.`;
  let vidRes = null;
  for (let vTry = 1; vTry <= 3; vTry++) {
    console.log(`[${sc.id}] Generating Flow Ingredients Video (${sc.seconds}s, try #${vTry})...`);
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
    console.warn(`[${sc.id}] Flow video try #${vTry} warning:`, vidRes && vidRes.error);
    await new Promise((r) => setTimeout(r, 7000));
  }
  if (!vidRes || !vidRes.ok || !vidRes.data) {
    throw new Error(`[${sc.id}] Flow video failed: ${vidRes && vidRes.error}`);
  }

  const rawMp4 = sc.dest + ".raw.mp4";
  fs.writeFileSync(rawMp4, Buffer.isBuffer(vidRes.data) ? vidRes.data : Buffer.from(vidRes.data));
  execFileSync("ffmpeg", [
    "-y", "-v", "error", "-ss", "0.22", "-i", rawMp4,
    "-r", "30", "-fps_mode", "cfr", "-an",
    "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_harm.cube[bg];[a][bg]blend=all_expr=A*0.35+B*0.65[v]",
    "-map", "[v]",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
    sc.dest,
  ], { cwd: MEDIA });
  try { fs.unlinkSync(rawMp4); } catch {}
  console.log(`[${sc.id}] VIDEO READY -> ${sc.dest}`);
}

async function main() {
  // Phase 1: Parallel Reference Images (3 workers)
  let cImg = 0;
  async function imgWorker() {
    while (cImg < SCENES.length) {
      const idx = cImg++;
      await generateRefImageWithFallback(SCENES[idx], idx);
    }
  }
  await Promise.all([imgWorker(), imgWorker(), imgWorker()]);

  // Phase 2: Parallel Flow Ingredients Videos (2 workers on capcutvid274)
  let cVid = 0;
  async function vidWorker(wIdx) {
    while (cVid < SCENES.length) {
      const idx = cVid++;
      await generateRefVideo(SCENES[idx], wIdx);
    }
  }
  await Promise.all([vidWorker(0), vidWorker(1)]);

  try { fs.unlinkSync(speakerJpg); } catch {}
  try { fs.unlinkSync(LUT_LOCAL); } catch {}
  flow.destroy();
  console.log("ALL_4_HTAV_BROLL_CLIPS_READY!");
  process.exit(0);
}

main().catch((err) => {
  console.error("BROLL_ERR:", err);
  try { flow.destroy(); } catch {}
  process.exit(1);
});
