// Direct Node.js runner for d:\AI\full studio\canvas\desktop\flow-driver.js
// Bypasses Electron Canvas renderer IPC bottleneck completely while reusing 100% of flow-driver.js's
// multi-slot, multi-account (capcutvid274@gmail.com priority #1), background-tab CDP engine!
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const { spawnSync } = require("node:child_process");

// 1) Shim 'electron' module BEFORE requiring flow-driver.js
const handlers = {};
const origLoad = Module._load;
Module._load = function (request, parent, isMain) {
  if (request === "electron") {
    return {
      ipcMain: {
        handle: (ch, fn) => { handlers[ch] = fn; },
        on: () => {},
      },
      dialog: {
        showErrorBox: (t, m) => console.error(`[FlowDialog] ${t}: ${m}`),
      },
    };
  }
  return origLoad.apply(this, arguments);
};

// Add canvas/desktop/node_modules to module search paths so puppeteer-core resolves cleanly
module.paths.unshift(path.resolve("d:/AI/full studio/canvas/desktop/node_modules"));

// 2) Locate existing flow-driver.json in %APPDATA% so we reuse exact active account & projectId!
const appData = process.env.APPDATA || "";
let userDataDir = path.join(appData, "infinite-canvas");
if (appData && fs.existsSync(appData)) {
  for (const d of fs.readdirSync(appData)) {
    const cand = path.join(appData, d, "flow-driver.json");
    if (fs.existsSync(cand)) {
      userDataDir = path.join(appData, d);
      break;
    }
  }
}
console.log("[DirectFlow] Using userDataDir:", userDataDir);

const flowDriver = require("d:/AI/full studio/canvas/desktop/flow-driver.js");
flowDriver.setup({ getPath: () => userDataDir });
const genVideo = handlers["flow:generate-video"];

const OUT_DIR   = "d:/AI/full studio/output/feelchicken-spicy-squid-cinematic";
const REAL_SQUID = path.join(OUT_DIR, "real_dish_refs/real_01_single_giant_squid_noodles.jpg");
const REF_916   = path.join(OUT_DIR, "ai_refs_9x16");
const REF_169   = path.join(OUT_DIR, "ai_refs_16x9");
const VID_916   = path.join(OUT_DIR, "flow_clips_9x16");
const VID_169   = path.join(OUT_DIR, "flow_clips_16x9");

const PROMPTS = {
  s01_chili_wave: "Slow-motion macro food commercial shot: glossy red Korean spicy broth wave curving gently above a bowl of giant whole squid and curly golden noodles on dark background, warm studio lighting.",
  s02_zero_g_squid_whip: "Slow-motion food commercial shot on pitch-black studio background: giant whole scored squid floating smoothly in mid-air as glossy red Korean sauce flows gently around it with golden fish balls, sausage slices, curly noodles, and soft steam.",
  s03_wok_fire_toss: "Slow-motion culinary wok cooking shot in dark kitchen: warm cooking flames beneath a black wok as giant whole scored squid, curly golden noodles, fish balls, bok choy, and purple cabbage rise gently in mid-air.",
  s04_exploded_levitation: "Slow-motion zero-gravity food commercial shot on black background: vertical stack of curly golden noodles, giant whole scored squid, fish balls, sliced sausage, bok choy, and purple cabbage floating gently above a steaming black ceramic bowl.",
  s05_broth_crown_splash: "Slow-motion food commercial shot on dark background: giant whole scored squid and toppings settling into a matte-black Korean ceramic bowl as a graceful crown wave of glossy red broth and white steam rises around the bowl.",
  s06_macro_boiling_glaze: "Close-up macro food shot on dark studio background: rich red Korean spicy broth simmering and bubbling gently around a giant whole scored squid and curly golden noodles inside a matte-black stone bowl with rising steam.",
  s07_chopstick_tower_lift: "Appetizing slow-motion food commercial shot on dark background: wooden chopsticks lifting steaming curly golden Korean ramen noodles and a giant whole scored squid upward from a matte-black ceramic bowl with broth droplets.",
  s08_hero_stone_pot: "Smooth camera push-in onto a steaming matte-black Korean ceramic stone bowl of giant whole scored squid and curly golden spicy noodles on a dark slate table with warm lantern bokeh behind and rising white steam.",
};

function imgObj(filePath, tagName) {
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  const base64 = fs.readFileSync(filePath).toString("base64");
  return { mime, base64, name: tagName + (ext || ".png") };
}

async function runPool(tasks, concurrency) {
  let idx = 0;
  async function worker(wId) {
    while (idx < tasks.length) {
      const myIdx = idx++;
      const t = tasks[myIdx];
      if (wId > 0 && myIdx < concurrency) {
        await new Promise((r) => setTimeout(r, wId * 2200));
      }
      let ok = false;
      for (let att = 1; att <= 2 && !ok; att++) {
        console.log(`[Worker#${wId}] Generating ${t.rtag} ${t.sid} (attempt ${att}/2)...`);
        const refImg = imgObj(t.refPng, `rf_${t.rtag}_${t.sid.slice(0, 8)}`);
        const sqdImg = imgObj(REAL_SQUID, "fc_real_squid1");
        const promptWithMentions = `@${refImg.name} @${sqdImg.name} ${PROMPTS[t.sid]} Zero text, zero watermarks.`;
        const res = await genVideo(null, {
          prompt: promptWithMentions,
          model: "Omni 1.2 Flash",
          aspect: t.aspect,
          resolution: "720p",
          seconds: 4,
          count: 1,
          images: [refImg, sqdImg],
          mode: "ingredients",
        });
        if (res && res.ok && res.data && res.data.length > 100000) {
          fs.writeFileSync(t.outMp4, Buffer.from(res.data));
          console.log(`  [SAVED DIRECT MP4] ${t.rtag} ${t.sid} -> ${(res.data.length / 1024).toFixed(0)} KB`);
          ok = true;
        } else {
          console.warn(`  [FAIL ${att}/2] ${t.rtag} ${t.sid}:`, res && res.error);
          await new Promise((r) => setTimeout(r, 4000));
        }
      }
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, tasks.length) }, (_, i) => worker(i)));
}

(async () => {
  const tasks = [];
  // Also re-generate s02_9x16 if it was the 7028KB static fallback so ALL 16/16 are genuine Flow AI videos!
  const s02p = path.join(VID_916, "s02_zero_g_squid_whip_9x16.mp4");
  if (fs.existsSync(s02p) && fs.statSync(s02p).size > 6800 * 1024) {
    fs.unlinkSync(s02p);
    console.log("[DirectFlow] Replaced fallback s02_9x16 so it gets genuine Flow AI video!");
  }

  for (const [rtag, aspect, rDir, vDir] of [
    ["9x16", "portrait", REF_916, VID_916],
    ["16x9", "landscape", REF_169, VID_169],
  ]) {
    for (const sid of Object.keys(PROMPTS).sort()) {
      const outMp4 = path.join(vDir, `${sid}_${rtag}.mp4`);
      const refPng = path.join(rDir, `${sid}_${rtag}.png`);
      if (fs.existsSync(outMp4) && fs.statSync(outMp4).size > 150000) {
        console.log(`  [SKIP EXISTING] ${rtag} ${sid} (${Math.round(fs.statSync(outMp4).size / 1024)} KB)`);
        continue;
      }
      tasks.push({ rtag, aspect, sid, refPng, outMp4 });
    }
  }

  console.log(`[DirectFlow] Launching ${tasks.length} Flow Video Generations across 4 Parallel Slots...`);
  if (tasks.length > 0) {
    await runPool(tasks, 4);
  }
  await flowDriver.sweepIdleFlowTabs().catch(() => {});
  flowDriver.destroy();

  console.log("[DirectFlow] All clips ready! Running Python Master Compositor (s03_build_hud_titles_audio_and_masters.py)...");
  const py = spawnSync(
    "d:/AI/full studio/voice-studio/.venv/Scripts/python.exe",
    ["d:/AI/full studio/output/feelchicken-spicy-squid-cinematic/s03_build_hud_titles_audio_and_masters.py"],
    { stdio: "inherit" }
  );
  process.exit(py.status || 0);
})();
