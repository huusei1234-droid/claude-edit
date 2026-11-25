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

const flowCfgPath = path.join(userDataDir, "flow-driver.json");
const verifiedTargets = [
  { prefix: "u/0/", projectId: "1d87402e-081d-4463-b301-bf4a6822280b" },
  { prefix: "u/0/", projectId: "48849d74-a827-4ee8-95bd-11ad9501a8a9" },
];
fs.writeFileSync(flowCfgPath, JSON.stringify({
  active: "a1",
  accounts: [{
    id: "a1",
    name: "Brave Chính (Đồng bộ)",
    profile: "MAIN_BRAVE",
    userPrefix: "u/0/",
    projectId: "1d87402e-081d-4463-b301-bf4a6822280b",
    workerTargets: verifiedTargets,
  }],
}, null, 2));

const ipcHandlers = {};
const origLoad = Module._load;
Module._load = function (request) {
  if (request === "electron") {
    return {
      ipcMain: { handle: (channel, fn) => { ipcHandlers[channel] = fn; }, on: () => {} },
      dialog: { showErrorBox: (t, m) => console.error("[Dialog]", t, m), showMessageBox: async () => ({ response: 0 }) },
      app: { getPath: (k) => (k === "userData" ? userDataDir : appData), isPackaged: false },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require("C:/AI/full studio/canvas/desktop/flow-driver.js");
const fakeApp = { getPath: (k) => (k === "userData" ? userDataDir : appData), isPackaged: false };
flow.setup(fakeApp);

const PROJ = "C:/AI/full studio/output/htpm-kb04-261123";
const MEDIA = path.join(PROJ, "media");
const LUT_SRC = "C:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/luts_chinh_mau/10_AI_Clip_Harmonizer_Natural.cube";
const LUT_LOCAL = path.join(MEDIA, "_harm.cube");
fs.copyFileSync(LUT_SRC, LUT_LOCAL);

const SCENES = [
  {
    id: "ws01a",
    refTag: "ref_kb04_v01a",
    seconds: 5,
    dest: path.join(MEDIA, "ws_01a_mirror_glow.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_01a.png"),
    vidPrompt: "Slow cinema dolly-in through soft morning sunbeams as the Vietnamese woman touches her cheek gently before the vanity mirror with a warm serene smile.",
  },
  {
    id: "ws01b",
    refTag: "ref_kb04_v01b",
    seconds: 4,
    dest: path.join(MEDIA, "ws_01b_confident_smile.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_01b.png"),
    vidPrompt: "Graceful slow cinema tracking shot in natural daylight as the Vietnamese woman turns slightly toward the garden window with poised confident warmth.",
  },
  {
    id: "ws01c",
    refTag: "ref_kb04_v01c",
    seconds: 5,
    dest: path.join(MEDIA, "ws_01c_phone_ad_trap.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_01c.png"),
    vidPrompt: "Slow cinema push-in under warm evening lamp light as the Vietnamese woman looks cautiously at her smartphone and pauses thoughtfully with closed lips.",
  },
  {
    id: "ws02a",
    refTag: "ref_kb04_v02a",
    seconds: 4,
    dest: path.join(MEDIA, "ws_02a_pill_illusion.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_02a.png"),
    vidPrompt: "Smooth slow cinema rack-focus from the dish of unbranded capsules on the marble table to the discerning Vietnamese woman shaking her head gently with closed lips.",
  },
  {
    id: "ws02b",
    refTag: "ref_kb04_v02b",
    seconds: 4,
    dest: path.join(MEDIA, "ws_02b_harsh_sun_uv.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_02b.png"),
    vidPrompt: "Slow cinema tracking glide through bright sunlit garden rays as the Vietnamese woman shades her cheek gently from the sun with calm poise.",
  },
  {
    id: "ws02c",
    refTag: "ref_kb04_v02c",
    seconds: 4,
    dest: path.join(MEDIA, "ws_02c_skin_biology.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_02c.png"),
    vidPrompt: "Delicate slow cinema push-in in soft daylight as the Vietnamese woman pats gentle hydrating serum onto her cheek with a calm peaceful smile.",
  },
  {
    id: "ws03a",
    refTag: "ref_kb04_v03a",
    seconds: 4,
    dest: path.join(MEDIA, "ws_03a_read_ingredients.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_03a.png"),
    vidPrompt: "Smooth slow cinema push-in by the sunlit window as the Vietnamese woman inspects the amber glass supplement bottle carefully and nods with informed confidence.",
  },
  {
    id: "ws03b",
    refTag: "ref_kb04_v03b",
    seconds: 4,
    dest: path.join(MEDIA, "ws_03b_holistic_nutrition.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_03b.png"),
    vidPrompt: "Warm slow cinema dolly-in across fresh colorful fruit as the radiant Vietnamese woman holds her glass of pure water with a serene healthy smile.",
  },
  {
    id: "ws03c",
    refTag: "ref_kb04_v03c",
    seconds: 4,
    dest: path.join(MEDIA, "ws_03c_healthy_radiance.mp4"),
    refDest: path.join(MEDIA, "ref_kb04_03c.png"),
    vidPrompt: "Graceful slow cinema push-in through warm golden garden light as she places her hands over her heart and smiles with radiant healthy confidence.",
  },
];

async function cleanStaleFlowTabs() {
  const b = await flow.ensureBrowser({ visible: true });
  for (const p of await b.pages()) {
    const u = p.url() || "";
    if (u.includes("dea6a60a-045f-4595-aa14-928e389b3042") || u.includes("flow.google.com/about") || u.includes("404?reason=project")) {
      await p.close().catch(() => {});
    }
  }
}

async function runScene(sc, workerIdx) {
  if (fs.existsSync(sc.dest) && fs.statSync(sc.dest).size > 25000) {
    console.log(`[${sc.id}] Already generated on disk -> skipping!`);
    return;
  }
  if (workerIdx > 0) {
    await new Promise((r) => setTimeout(r, workerIdx * 7000));
  }

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
    console.log(`[${sc.id}] Generating Ingredients Video (${sc.seconds}s, try #${vTry})...`);
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
    console.warn(`[${sc.id}] Video try #${vTry} warning:`, vidRes && vidRes.error);
    await new Promise((r) => setTimeout(r, 8000));
  }
  if (!vidRes || !vidRes.ok || !vidRes.data) {
    throw new Error(`[${sc.id}] Video generation failed: ${vidRes && vidRes.error}`);
  }

  const rawMp4 = sc.dest + ".raw.mp4";
  fs.writeFileSync(rawMp4, Buffer.isBuffer(vidRes.data) ? vidRes.data : Buffer.from(vidRes.data));
  execFileSync("ffmpeg", [
    "-y", "-v", "error", "-ss", "0.20", "-i", rawMp4,
    "-r", "30", "-fps_mode", "cfr", "-an",
    "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_harm.cube[bg];[a][bg]blend=all_expr=A*0.34+B*0.66[v]",
    "-map", "[v]",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
    sc.dest,
  ], { cwd: MEDIA });
  try { fs.unlinkSync(rawMp4); } catch {}
  console.log(`[${sc.id}] READY -> ${sc.dest}`);
  await new Promise((r) => setTimeout(r, 4500));
}

async function main() {
  await cleanStaleFlowTabs();
  const CONCURRENCY = 2;
  let cursor = 0;
  async function worker(wIdx) {
    while (cursor < SCENES.length) {
      const idx = cursor++;
      await runScene(SCENES[idx], wIdx);
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, (_, wIdx) => worker(wIdx)));
  try { fs.unlinkSync(LUT_LOCAL); } catch {}
  flow.destroy();
  console.log("ALL_9_KB04_CLIPS_DONE!");
  process.exit(0);
}

main().catch((err) => {
  console.error("FATAL:", err);
  try { flow.destroy(); } catch {}
  process.exit(1);
});
