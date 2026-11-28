// V6 STEP 2 — GENERATE 12 ULTRA-CLEAN, CRYSTAL-CLEAR SUNLIT DAYLIGHT CLIPS ON CHATGPT + GOOGLE FLOW
// Replaces 100% of shaking/purple podiums and 100% of missing-label/dark clips!
// Pure native 24fps (NO zoompan, NO setpts stretch, NO fake AI bottles!)
const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const V6_DIR = "d:\\AI\\full studio\\output\\htpm-ngay-261125\\12_V6_Crystal_Clear_USP";
const IMG_DIR = path.join(V6_DIR, "02_Clean_Refs");
const VID_DIR = path.join(V6_DIR, "03_Clean_Native24_Clips");
fs.mkdirSync(IMG_DIR, { recursive: true });
fs.mkdirSync(VID_DIR, { recursive: true });

const HANG_RTFN = "d:\\AI\\full studio\\output\\htpm-ai-usp-v4-261125\\00_Clean_Sources\\chihang_rtfn_5632.jpg";

const handlers = {};
const origLoad = Module._load;
Module._load = function (request, parent, isMain) {
  if (request === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: (t, m) => console.error("[DialogError]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const userDataDir = path.join(process.env.APPDATA || "C:\\Users\\Hang thu\\AppData\\Roaming", "infinite-canvas-flow");
const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));
flow.setup({ getPath: () => userDataDir });
chatgpt.setup({ getPath: () => userDataDir });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const AIRY_LOCK = "Ultra-clean 8K high-key commercial daylight cinematography (5500K crystal-clear morning sunlight, bright airy white & pastel palette, luminous clarity, ZERO dark shadows, ZERO neon purple/magenta tint, ZERO glitter/sparkles, zero text, zero bottles, zero boxes). ";
const HANG_LOCK = "[STRICT 100% REAL FACE LOCK]: Keep 100.0% the EXACT SAME Vietnamese woman's face from the portrait reference (warm full round-oval face, full soft cheeks, gently-rounded jawline — NO V-chin, exact dark eyebrows, warm almond eyes, rounded nose tip, coral-rose smile, glossy dark-brown wavy hair, tall 170cm poised figure). Capture natural candid daytime motion, ZERO products in hand, zero speaking. ";

const JOBS = [
  // 6 Sunlit Crystal-Clear Empty Marble/Water Podium Stages (for crisp real PNG product overlay in HTML — 0% zoompan, 0% purple!)
  {
    id: "sunpod_01_rose_water",
    refs: [],
    img_p: AIRY_LOCK + "Vertical 9:16 sunlit luxury cosmetic podium background: a smooth white-and-blush marble circular pedestal resting in crystal-clear sunlit turquoise-and-blush water ripples with fresh dewy pink lotus and chamomile blossoms at the edges, bright airy sunlit sky bokeh in the upper half.",
    vid_p: "Smooth steady slow cinematic camera drift: gentle sunlit water ripples shimmer softly around the white marble pedestal with dewy pink blossoms in crisp morning daylight, no camera shake, no text.",
  },
  {
    id: "sunpod_02_aqua_orchid",
    refs: [],
    img_p: AIRY_LOCK + "Vertical 9:16 sunlit luxury skincare podium background: a pure white Carrara marble cylinder pedestal surrounded by shallow crystal-clear sunlit water ripples, fresh white orchids, and green tea leaves in bright coastal morning sunlight, airy luminous upper half.",
    vid_p: "Smooth steady slow camera glide: crystal-clear sunlit water ripples and white orchid petals sway gently around the white marble pedestal in bright morning light, no shake, no text.",
  },
  {
    id: "sunpod_03_herbal_travertine",
    refs: [],
    img_p: AIRY_LOCK + "Vertical 9:16 bright sunlit herbal wellness podium background: a clean cream travertine stone pedestal in a sunlit glass garden conservatory with fresh green herbal leaves, sliced golden turmeric, and white chamomile flowers around the base, bright airy sunlit greenery bokeh.",
    vid_p: "Smooth steady slow gimbal drift across the sunlit cream travertine pedestal with gentle morning sunbeams and soft leaf movement in the bright garden conservatory, no shake, no text.",
  },
  {
    id: "sunpod_04_ice_pearl",
    refs: [],
    img_p: AIRY_LOCK + "Vertical 9:16 bright sunlit coastal skincare podium background: a luminous pearl-white glass pedestal overlooking sunlit turquoise Nha Trang ocean water and soft white clouds, crystal water droplets and white pearls resting beside the base, ultra-clean bright airy aesthetic.",
    vid_p: "Smooth steady slow camera push-in toward the sunlit pearl-white pedestal with gentle turquoise ocean ripples glittering softly in bright morning daylight, no shake, no text.",
  },
  {
    id: "sunpod_05_emerald_garden",
    refs: [],
    img_p: AIRY_LOCK + "Vertical 9:16 bright sunlit botanical podium background: a smooth ivory-jade marble pedestal bathed in fresh morning sunbeams surrounded by white jasmine flowers, chamomile, and lush green leaves over clear water ripples, bright airy cream-mint upper space.",
    vid_p: "Smooth steady slow camera drift: clear morning water ripples and white jasmine blossoms move gently around the sunlit ivory marble pedestal, no shake, no text.",
  },
  {
    id: "sunpod_06_warm_sunlit_amber",
    refs: [],
    img_p: AIRY_LOCK + "Vertical 9:16 bright sunlit prestige herbal podium background: a warm cream-and-gold marble pedestal in a bright sunlit courtyard with golden morning sunbeams, fresh ginseng roots, cordyceps, and green leaves beside the base, bright airy sunlit cream sky above (ZERO dark purple or murky colors).",
    vid_p: "Smooth steady slow cinematic push-in on the sunlit cream-gold marble pedestal as warm morning sunlight filters gently through courtyard greenery, no shake, no text.",
  },

  // 6 Bright Sunlit Daytime Real-Life Action Clips (replacing all banned missing-label & dark evening clips!)
  {
    id: "day_act_01_vanity_morning",
    refs: [HANG_RTFN],
    img_p: AIRY_LOCK + HANG_LOCK + "Wearing a crisp ivory tailored blazer over a silk blouse in a bright sunlit white coastal dressing room in morning daylight: candid medium shot tucking a strand of hair behind her ear with a pearl earring while looking warmly at a sunlit mirror.",
    vid_p: "Smooth candid morning daylight motion: she gently tucks her glossy dark hair behind her ear in the bright sunlit white room with calm natural poise, lips closed, no text.",
  },
  {
    id: "day_act_02_handbag_zip_walk",
    refs: [HANG_RTFN],
    img_p: AIRY_LOCK + HANG_LOCK + "Wearing a pastel ice-blue midi dress in a bright sunlit white marble home entryway with glass doors and green palms outside: candid medium tracking shot picking up her small white leather handbag from the console table and walking cheerfully toward the sunlit doorway.",
    vid_p: "Smooth sunlit tracking shot: she picks up her small white leather handbag and walks gracefully toward the bright sunlit glass doorway, lips closed, no text.",
  },
  {
    id: "day_act_03_sunlit_tea_sip",
    refs: [HANG_RTFN],
    img_p: AIRY_LOCK + HANG_LOCK + "Wearing an elegant cream-ivory dress sitting in a bright sunlit white ocean-view living room accented with fresh pink peonies: candid medium shot lifting a clear glass cup of warm golden herbal tea with both hands and enjoying its gentle aroma.",
    vid_p: "Smooth sunlit indoor lifestyle shot: sitting beside pink peonies in bright morning light, she lifts a warm cup of herbal tea gracefully, rosy healthy complexion, lips closed, no text.",
  },
  {
    id: "day_act_04_white_kitchen_water",
    refs: [HANG_RTFN],
    img_p: AIRY_LOCK + HANG_LOCK + "Wearing a tailored pure-white belted blazer-dress standing at a bright sunlit white marble kitchen island with fresh fruit and sunlit ocean window behind: candid medium shot pouring crystal-clear water from a glass pitcher into a drinking glass.",
    vid_p: "Smooth sunlit morning kitchen action: she pours pure crystal-clear water from a glass pitcher into a clear glass in bright coastal daylight, lips closed, no text.",
  },
  {
    id: "day_act_05_sunlit_study_journal",
    refs: [HANG_RTFN],
    img_p: AIRY_LOCK + HANG_LOCK + "Wearing a refined cream blazer in a bright airy sunlit home study beside tall sheer white curtains and indoor plants: candid medium shot writing notes in a cream leather wellness planner at a light oak desk.",
    vid_p: "Smooth sunlit indoor study action: sitting by sheer white curtains in bright morning daylight, she writes calmly in her planner with gentle natural focus, lips closed, no text.",
  },
  {
    id: "day_act_06_sunlit_garden_breeze",
    refs: [HANG_RTFN],
    img_p: AIRY_LOCK + HANG_LOCK + "Wearing a chic ivory-blush tweed jacket and skirt strolling along a bright sunlit white marble garden terrace lined with blooming pink roses and turquoise sea sky in daylight: candid tracking shot touching a blooming pink rose gently as she walks.",
    vid_p: "Smooth sunlit garden terrace tracking shot: she walks lightly past blooming pink roses in crisp morning coastal sunlight, hair moving gently in breeze, lips closed, no text.",
  },
];

function fileToImgObj(fp) {
  const ext = path.extname(fp).toLowerCase();
  return { mime: ext === ".png" ? "image/png" : "image/jpeg", base64: fs.readFileSync(fp).toString("base64"), name: "v6_" + path.basename(fp) };
}

function normalizeNative24Nvenc(rawMp4, outMp4) {
  // ZERO setpts stretch! Pure 1:1 native 24fps scale+crop so 0.00% jitter or frame duplication!
  const vf = "fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p";
  execFileSync("ffmpeg", [
    "-y", "-v", "error", "-i", rawMp4,
    "-vf", vf, "-r", "24", "-fps_mode", "cfr", "-an",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-g", "24",
    outMp4
  ], { stdio: "inherit" });
}

(async () => {
  const todo = JOBS.filter((j) => {
    const p = path.join(VID_DIR, `${j.id}.mp4`);
    return !(fs.existsSync(p) && fs.statSync(p).size > 200000);
  });
  console.log(`[V6 Clean Daylight Engine] Todo = ${todo.length}/${JOBS.length} clips...`);
  if (todo.length === 0) process.exit(0);

  const flowQ = [];
  let imgDone = false;
  const needImg = [];

  for (const j of todo) {
    const jpg = path.join(IMG_DIR, `${j.id}.jpg`);
    if (fs.existsSync(jpg) && fs.statSync(jpg).size > 40000) flowQ.push(j);
    else needImg.push(j);
  }

  let iIdx = 0;
  async function imgWorker(w) {
    if (w > 0) await sleep(w * 2500);
    while (iIdx < needImg.length) {
      const j = needImg[iIdx++];
      const png = path.join(IMG_DIR, `${j.id}.png`);
      const jpg = path.join(IMG_DIR, `${j.id}.jpg`);
      if (!(fs.existsSync(png) && fs.statSync(png).size > 180000)) {
        let res = null;
        for (let a = 1; a <= 3; a++) {
          res = await handlers["chatgpt:generate-image"](null, {
            prompt: j.img_p, model: "chatgpt-image", ratio: "9:16", quality: "auto", count: 1,
            images: j.refs.map(fileToImgObj), keepChat: false, noFallback: true,
          });
          if (res && res.ok && res.data && res.data.length > 180000) break;
          await sleep(6000);
        }
        if (!res || !res.ok || !res.data) throw new Error(`ChatGPT failed ${j.id}: ${res?.error}`);
        fs.writeFileSync(png, Buffer.from(res.data));
      }
      execFileSync("ffmpeg", ["-y", "-v", "error", "-i", png, "-vf", "scale='min(1080,iw)':-2", "-q:v", "3", jpg]);
      console.log(`[V6 ImgOK] ${j.id}`);
      flowQ.push(j);
    }
  }

  let doneCount = 0;
  async function flowWorker(w) {
    if (w > 0) await sleep(w * 4000);
    while (true) {
      if (flowQ.length === 0) {
        if (imgDone) break;
        await sleep(1500);
        continue;
      }
      const j = flowQ.shift();
      const jpg = path.join(IMG_DIR, `${j.id}.jpg`);
      const raw = path.join(VID_DIR, `${j.id}_raw.mp4`);
      const out = path.join(VID_DIR, `${j.id}.mp4`);
      let res = null;
      for (let a = 1; a <= 4; a++) {
        res = await handlers["flow:generate-video"](null, {
          prompt: j.vid_p, model: "Omni 1.2 Flash", aspect: "portrait", resolution: "720p",
          seconds: 6, count: 1, mode: "ingredients", images: [fileToImgObj(jpg)],
        });
        if (res && res.ok && res.data && res.data.length > 100000) break;
        await sleep(7000);
      }
      if (!res || !res.ok || !res.data) throw new Error(`Flow failed ${j.id}: ${res?.error}`);
      fs.writeFileSync(raw, Buffer.from(res.data));
      normalizeNative24Nvenc(raw, out);
      doneCount++;
      console.log(`[V6 VidOK] (${doneCount}/${todo.length}) ${j.id}`);
    }
  }

  await Promise.all([imgWorker(0), imgWorker(1)]);
  imgDone = true;
  await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
  console.log("=== [V6 PHASE A: ALL 12 REFS DONE, STARTING PHASE B FLOW] ===");
  await Promise.all([flowWorker(0)]);
  await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  console.log("=== ALL 12 V6 CLEAN DAYLIGHT CLIPS READY ===");
  process.exit(0);
})().catch((e) => {
  console.error("[V6_ERR]", e);
  process.exit(1);
});
