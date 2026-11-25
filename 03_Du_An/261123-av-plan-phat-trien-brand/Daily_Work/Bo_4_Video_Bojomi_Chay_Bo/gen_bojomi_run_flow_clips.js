/**
 * Bộ 4 Video Bojomi Chạy Bộ (24/11/2026): Tạo 28 clip Video Dọc 9:16 (Google Flow Omni 1.2 Flash, mode: "ingredients", 720p)
 * - Video B1 (Emerald Running Skort): 7 clips (chạy ven hồ bình minh + cầm hộp Bojomi + CGI Aquamin F + pha & uống sau chạy)
 * - Video B2 (Coral Blush Shorts + White Windbreaker): 7 clips (chạy ven sông + cầm hộp Bojomi + CGI D3/K2 + pha & uống)
 * - Video B3 (Lavender Tee + Charcoal Biker Shorts): 7 clips (chạy sân tartan nắng mai + cầm hộp Bojomi + CGI Collagen & Canxi + pha & uống)
 * - Video B4 (Baby Blue Jacket + White Skort + White Visor): 7 clips (chạy đại lộ cây xanh + cầm hộp Bojomi + CGI ngũ cốc + pha 30s ngoài trời & uống)
 * Chạy êm ái concurrency = 2 (tránh rate-limit Flow, 100% chế độ Thành phần gắn ảnh tham chiếu, ZERO lip-sync!).
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Bojomi_Chay_Bo";
const ASSETS_DIR = path.join(WORK_DIR, "01_ChatGPT_Assets");
const CUTOUT_DIR = "d:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\brand_kits\\07_An_Vuong_Pharma\\02_San_Pham_Cutout_PNG";

const V1_DIR = path.join(WORK_DIR, "bojomi_run_01_khung_xuong", "07_HyperFrames_Project", "assets", "videos");
const V2_DIR = path.join(WORK_DIR, "bojomi_run_02_bo3_d3_k2", "07_HyperFrames_Project", "assets", "videos");
const V3_DIR = path.join(WORK_DIR, "bojomi_run_03_collagen_deo_dai", "07_HyperFrames_Project", "assets", "videos");
const V4_DIR = path.join(WORK_DIR, "bojomi_run_04_pha_30s_uu_dai", "07_HyperFrames_Project", "assets", "videos");
for (const d of [V1_DIR, V2_DIR, V3_DIR, V4_DIR]) fs.mkdirSync(d, { recursive: true });

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

const REF_R1 = loadImg(path.join(ASSETS_DIR, "RUN_LOOK1_EMERALD_9x16.png"), "run_look1_emerald.png");
const REF_R2 = loadImg(path.join(ASSETS_DIR, "RUN_LOOK2_CORAL_9x16.png"), "run_look2_coral.png");
const REF_R3 = loadImg(path.join(ASSETS_DIR, "RUN_LOOK3_LAVENDER_9x16.png"), "run_look3_lavender.png");
const REF_R4 = loadImg(path.join(ASSETS_DIR, "RUN_LOOK4_BABYBLUE_9x16.png"), "run_look4_babyblue.png");
const REF_BOJ = loadImg(path.join(CUTOUT_DIR, "av02_bojomi_a.png"), "av_bojomi_box.png");

const L1_LOCK =
  " Keep the exact same Vietnamese woman, her exact ivory half-zip sleeveless running croptop, emerald-green pleated athletic running skort, white sneakers, high ponytail with ivory ribbon, pearl stud earrings, gold necklace, and white GPS running watch from run_look1_emerald.png. " +
  "Natural calm breathing, radiant closed-mouth athletic smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const L2_LOCK =
  " Keep the exact same Vietnamese woman, her exact pastel coral-blush racerback running tank, unzipped sheer-white cropped running windbreaker jacket, pastel coral-blush double-layer running shorts, sporty braided ponytail with thin white headband, tiny silver hoops, and blush GPS watch from run_look2_coral.png. " +
  "Natural calm breathing, fresh closed-mouth athletic smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const L3_LOCK =
  " Keep the exact same Vietnamese woman, her exact pastel lavender fitted short-sleeve running tee, charcoal-gray sculpted running biker shorts, high half-up ponytail with silver clip, tiny crystal stud earrings, silver necklace, and silver-gray GPS watch from run_look3_lavender.png. " +
  "Natural calm breathing, confident closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const L4_LOCK =
  " Keep the exact same Vietnamese woman, her exact baby-blue lightweight cropped zip running jacket over white sports tank, crisp-white pleated running skort, white sporty sun visor cap with high neat bun, mini gold hoops, dainty gold necklace, and light-blue GPS watch from run_look4_babyblue.png. " +
  "Natural calm breathing, bright closed-mouth smile, ZERO speaking, ZERO lip-syncing, NO text overlays, NO subtitles, NO watermarks.";

const JOBS = [
  // ================= VIDEO B1: EMERALD SKORT (LAKESIDE PARK — AQUAMIN F) =================
  {
    id: "r1_s01", outPath: path.join(V1_DIR, "s01.mp4"), seconds: 5, images: [REF_R1],
    prompt:
      "Vertical 9:16 energetic luxury commercial opening hook: the young Vietnamese runner from run_look1_emerald.png jogs lightly and gracefully along a sunlit lakeside park path at golden sunrise, slows to a poised stop, glances at her GPS watch and smiles radiantly toward camera with shimmering lake sunlight bokeh behind. Smooth tracking cinema gimbal." + L1_LOCK,
  },
  {
    id: "r1_s02", outPath: path.join(V1_DIR, "s02.mp4"), seconds: 8, images: [REF_R1],
    prompt:
      "Vertical 9:16 authentic running lifestyle scene: along the lush lakeside jogging path in soft golden sunrise light, the woman from run_look1_emerald.png pauses beside a wooden lakeside rail to gently stretch her calf and lightly touch her knee after a long morning run with calm mindful awareness of caring for her bones and joints. Smooth slow cinema pan." + L1_LOCK,
  },
  {
    id: "r1_s03", outPath: path.join(V1_DIR, "s03.mp4"), seconds: 8, images: [REF_R1, REF_BOJ],
    prompt:
      "Vertical 9:16 hero product reveal commercial shot: standing on a sunlit lakeside park wooden deck with sparkling green trees behind, the stylish runner from run_look1_emerald.png gracefully holds up the real green-and-cream Bojomi box from av_bojomi_box.png near chest level with a proud healthy smile. Warm golden morning sun flare, smooth slow push-in." + L1_LOCK,
  },
  {
    id: "r1_s04a", outPath: path.join(V1_DIR, "s04a.mp4"), seconds: 6, images: [REF_BOJ],
    prompt:
      "Vertical 9:16 luxury pharmaceutical 3D CGI macro commercial visualization matching the emerald-green and champagne-gold palette of av_bojomi_box.png: luminous crystalline white-pearl marine calcium spheres rising gracefully from vivid red Aquamin F sea algae in crystal-clear sunlit ocean light, wrapped by warm golden vitamin ribbons. Slow motion 24fps, zero text, zero letters, zero watermarks.",
  },
  {
    id: "r1_s04b", outPath: path.join(V1_DIR, "s04b.mp4"), seconds: 6, images: [REF_R1],
    prompt:
      "Vertical 9:16 uplifting morning running showcase: smooth cinematic side tracking shot of the runner from run_look1_emerald.png jogging gracefully with strong springy light strides along the golden sunrise lakeside tree-lined park trail, hair ponytail bouncing softly in warm golden morning light. Crisp 24fps sports commercial cinematography." + L1_LOCK,
  },
  {
    id: "r1_s05", outPath: path.join(V1_DIR, "s05.mp4"), seconds: 9, images: [REF_R1, REF_BOJ],
    prompt:
      "Vertical 9:16 appetizing outdoor nutrition preparation close-up: on a bright sunlit white outdoor park-cafe table next to the real Bojomi box av_bojomi_box.png, the slender hands with white GPS running watch of the woman from run_look1_emerald.png pour warm steaming water from a sleek thermos into a clear glass mug of fragrant vanilla cereal powder and stir smoothly until creamy velvety cereal milk forms with gentle warm mist." + L1_LOCK,
  },
  {
    id: "r1_s06", outPath: path.join(V1_DIR, "s06.mp4"), seconds: 7, images: [REF_R1],
    prompt:
      "Vertical 9:16 radiant post-run payoff shot: standing in golden lakeside morning sunlight, the athletic woman from run_look1_emerald.png takes a satisfied warm sip from her glass mug of creamy vanilla Bojomi cereal drink, lowers the mug gently and smiles brightly toward camera feeling strong and refreshed. Warm sunlit lens flare, smooth dolly." + L1_LOCK,
  },

  // ================= VIDEO B2: CORAL BLUSH & SHEER WHITE (RIVERSIDE — D3 + K2 MK-7) =================
  {
    id: "r2_s01", outPath: path.join(V2_DIR, "s01.mp4"), seconds: 6, images: [REF_R2],
    prompt:
      "Vertical 9:16 vibrant commercial opening hook: the stylish young Vietnamese runner from run_look2_coral.png runs lightly toward camera along a wide sunlit riverside city promenade at golden sunrise, slows to a poised athletic stance, adjusts her sleek white headband gently and smiles brightly toward camera with airy sunrise skyline bokeh behind. Smooth gimbal push-in." + L2_LOCK,
  },
  {
    id: "r2_s02", outPath: path.join(V2_DIR, "s02.mp4"), seconds: 8, images: [REF_R2],
    prompt:
      "Vertical 9:16 relatable lifestyle scene: resting after a brisk run on a clean bright sunlit riverside wooden bench, the woman from run_look2_coral.png holds a plain unbranded white supplement bottle in one hand, reading the nutrition label thoughtfully with calm discernment and soft golden morning breeze lifting her white windbreaker. Smooth cinema side glide." + L2_LOCK,
  },
  {
    id: "r2_s03", outPath: path.join(V2_DIR, "s03.mp4"), seconds: 10, images: [REF_R2, REF_BOJ],
    prompt:
      "Vertical 9:16 hero product reveal commercial shot: bathed in crisp golden sunrise along the sunlit riverside promenade, the runner from run_look2_coral.png gracefully presents the real green-and-cream Bojomi box from av_bojomi_box.png at chest level with an energetic reassuring smile, sparkling water bokeh shimmering softly in background. Smooth slow arc dolly." + L2_LOCK,
  },
  {
    id: "r2_s04a", outPath: path.join(V2_DIR, "s04a.mp4"), seconds: 7, images: [REF_BOJ],
    prompt:
      "Vertical 9:16 ultra-clean pharmaceutical 3D CGI scientific visualization matching the emerald and gold elegance of av_bojomi_box.png: three luminous crystalline golden-and-pearl nutrient orbs symbolizing Calcium, Vitamin D3, and K2 MK-7 orbiting harmoniously together in radiant sunlit emerald-champagne studio light surrounded by silky swirling vanilla milk ribbons. Slow motion 24fps, zero text, zero letters, zero watermarks.",
  },
  {
    id: "r2_s04b", outPath: path.join(V2_DIR, "s04b.mp4"), seconds: 7, images: [REF_R2, REF_BOJ],
    prompt:
      "Vertical 9:16 crisp morning wellness showcase: sitting happily at a sunlit modern riverside marble cafe counter where the real Bojomi box av_bojomi_box.png stands neatly beside a warm steaming glass of smooth vanilla cereal milk, the runner from run_look2_coral.png gently lifts the warm glass admiring its smooth silky texture with a radiant smile." + L2_LOCK,
  },
  {
    id: "r2_s05", outPath: path.join(V2_DIR, "s05.mp4"), seconds: 9, images: [REF_R2, REF_BOJ],
    prompt:
      "Vertical 9:16 appetizing preparation close-up: on a bright sunlit riverside terrace table beside the real Bojomi box av_bojomi_box.png, the slender hands wearing the pastel-blush GPS watch of the runner from run_look2_coral.png pour warm steaming water into a clear glass of golden-cream vanilla cereal powder and stir effortlessly with a sleek gold spoon until silky smooth with zero clumps." + L2_LOCK,
  },
  {
    id: "r2_s06", outPath: path.join(V2_DIR, "s06.mp4"), seconds: 7, images: [REF_R2],
    prompt:
      "Vertical 9:16 exhilarating morning payoff shot: full of light energetic vitality after finishing her warm drink, the runner from run_look2_coral.png jogs forward gracefully along the sunlit riverside promenade under golden morning sunbeams, glancing back toward camera with a joyful radiant smile. Smooth cinematic tracking shot." + L2_LOCK,
  },

  // ================= VIDEO B3: LAVENDER & CHARCOAL BIKER SHORTS (STADIUM TRACK — COLLAGEN 201.4MG) =================
  {
    id: "r3_s01", outPath: path.join(V3_DIR, "s01.mp4"), seconds: 5, images: [REF_R3],
    prompt:
      "Vertical 9:16 bold athletic commercial opening hook: on a vibrant sunlit terracotta-red stadium running track at crisp morning sunrise, the stylish Vietnamese runner from run_look3_lavender.png glides forward in smooth graceful jogging strides and pauses smoothly facing camera with confident radiant athletic charm. Golden stadium sun flare, cinema gimbal push-in." + L3_LOCK,
  },
  {
    id: "r3_s02", outPath: path.join(V3_DIR, "s02.mp4"), seconds: 9, images: [REF_R3],
    prompt:
      "Vertical 9:16 dynamic stretching & flexibility shot: on the sunlit outdoor stadium running track with lush greenery behind, the runner from run_look3_lavender.png performs a graceful athletic lunge stretch and gentle ankle warm-up with focused poise, showcasing flexible toned athletic form bathed in warm golden morning light. Smooth slow cinema tracking." + L3_LOCK,
  },
  {
    id: "r3_s03", outPath: path.join(V3_DIR, "s03.mp4"), seconds: 8, images: [REF_R3, REF_BOJ],
    prompt:
      "Vertical 9:16 luxury sports-nutrition hero product reveal: standing proudly beside the sunlit stadium running track in warm morning backlight, the runner from run_look3_lavender.png holds up the real green-and-cream Bojomi box from av_bojomi_box.png cleanly at chest level with a glowing confident smile. Golden morning bokeh, smooth commercial push-in." + L3_LOCK,
  },
  {
    id: "r3_s04a", outPath: path.join(V3_DIR, "s04a.mp4"), seconds: 6, images: [REF_BOJ],
    prompt:
      "Vertical 9:16 luxury dual-action 3D CGI commercial macro matching av_bojomi_box.png: luminous pearl-white marine calcium spheres intertwining gracefully with translucent golden-honey collagen liquid droplets and creamy vanilla cereal waves swirling in radiant sunlit emerald-and-gold studio light. Slow motion 24fps, zero text, zero letters, zero watermarks.",
  },
  {
    id: "r3_s04b", outPath: path.join(V3_DIR, "s04b.mp4"), seconds: 5, images: [REF_R3],
    prompt:
      "Vertical 9:16 powerful graceful slow-motion running shot: low-angle cinematic tracking shot of the runner from run_look3_lavender.png sprinting smoothly with effortless flexible strides down the sunlit red tartan stadium track, soft golden morning sunlight illuminating her athletic silhouette. Crisp 24fps commercial cinematography." + L3_LOCK,
  },
  {
    id: "r3_s05", outPath: path.join(V3_DIR, "s05.mp4"), seconds: 8, images: [REF_R3, REF_BOJ],
    prompt:
      "Vertical 9:16 fresh post-track preparation shot: on a bright modern stadium-side stone bench next to the real Bojomi box av_bojomi_box.png, the slender hands with silver-gray GPS watch of the runner from run_look3_lavender.png pour warm steaming water from a sleek stainless flask into a modern glass tumbler of fragrant vanilla Bojomi cereal powder and swirl until creamy velvety smooth." + L3_LOCK,
  },
  {
    id: "r3_s06", outPath: path.join(V3_DIR, "s06.mp4"), seconds: 8, images: [REF_R3],
    prompt:
      "Vertical 9:16 joyful athletic payoff shot: standing in bright morning sunlight beside the stadium track holding her warm creamy vanilla Bojomi tumbler, the runner from run_look3_lavender.png takes a refreshing satisfied sip and beams radiantly toward camera looking energized, flexible, and confident. Warm sunrise lens flare, smooth dolly." + L3_LOCK,
  },

  // ================= VIDEO B4: BABY BLUE JACKET + WHITE SKORT + VISOR (BOULEVARD — 30S PREP & PROMO 520K) =================
  {
    id: "r4_s01", outPath: path.join(V4_DIR, "s01.mp4"), seconds: 6, images: [REF_R4],
    prompt:
      "Vertical 9:16 crisp luxury lifestyle-running opening hook: along a gorgeous sunlit tree-lined green morning boulevard dappled with golden sunrise beams, the chic runner from run_look4_babyblue.png finishes her 5km morning jog, taps her light-blue GPS watch with a joyful triumphant smile and turns brightly toward camera. Smooth tracking gimbal." + L4_LOCK,
  },
  {
    id: "r4_s02", outPath: path.join(V4_DIR, "s02.mp4"), seconds: 8, images: [REF_R4],
    prompt:
      "Vertical 9:16 relatable post-run morning scene: arriving at a sunlit minimalist outdoor garden cafe patio after her morning run, the woman from run_look4_babyblue.png gently wipes her forehead with a clean white sports towel, looks briefly at an overly sugary iced drink on a nearby table and politely shakes her head choosing healthy nutrition instead. Smooth slow pan." + L4_LOCK,
  },
  {
    id: "r4_s03", outPath: path.join(V4_DIR, "s03.mp4"), seconds: 8, images: [REF_R4, REF_BOJ],
    prompt:
      "Vertical 9:16 convenient hero reveal commercial shot: seated at a bright sunlit marble outdoor patio table surrounded by lush green morning foliage, the stylish runner from run_look4_babyblue.png happily lifts the real green-and-cream Bojomi box from av_bojomi_box.png alongside a sleek single-serve sachet near chest level, smiling brightly toward camera. Golden morning bokeh, smooth push-in." + L4_LOCK,
  },
  {
    id: "r4_s04a", outPath: path.join(V4_DIR, "s04a.mp4"), seconds: 6, images: [REF_BOJ],
    prompt:
      "Vertical 9:16 appetizing high-speed 3D CGI commercial macro matching av_bojomi_box.png: fine golden-cream vanilla cereal powder cascading into swirling crystal-clear warm water, transforming instantaneously into a velvety luminous vanilla milk vortex sparkling with tiny pearl calcium and golden vitamin light particles. Slow motion 24fps, zero text, zero letters, zero watermarks.",
  },
  {
    id: "r4_s04b", outPath: path.join(V4_DIR, "s04b.mp4"), seconds: 6, images: [REF_R4, REF_BOJ],
    prompt:
      "Vertical 9:16 fresh morning nutrition table close-up: on the sunlit white outdoor patio table bathed in soft golden sunbeams, the real Bojomi box av_bojomi_box.png stands sharply beside a clear steaming glass cup of creamy vanilla cereal drink; the runner from run_look4_babyblue.png gently swirls a sleek gold spoon through the rich smooth beverage with warm satisfaction." + L4_LOCK,
  },
  {
    id: "r4_s05", outPath: path.join(V4_DIR, "s05.mp4"), seconds: 9, images: [REF_R4, REF_BOJ],
    prompt:
      "Vertical 9:16 quick 30-second beverage prep close-up: the slender hands with light-blue GPS watch of the runner from run_look4_babyblue.png tear open a clean vanilla cereal sachet and pour warm steaming water from a sleek white insulated bottle into a clear glass mug beside the Bojomi box av_bojomi_box.png, stirring smoothly into frothy creamy vanilla cereal milk rising with inviting warm aroma." + L4_LOCK,
  },
  {
    id: "r4_s06", outPath: path.join(V4_DIR, "s06.mp4"), seconds: 8, images: [REF_R4],
    prompt:
      "Vertical 9:16 bright joyful morning payoff shot: at the sunlit outdoor garden terrace overlooking the green tree-lined running boulevard, the chic runner from run_look4_babyblue.png enjoys a warm comforting sip of her creamy Bojomi vanilla cereal drink, lowers the cup gracefully and smiles radiantly toward camera ready for a vibrant productive day. Golden sun flare, smooth cinema dolly." + L4_LOCK,
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
  const res = await runPool(JOBS, 1);
  const ok = res.filter((r) => r && r.ok).length;
  console.log(`\n=== 4 BOJOMI RUNNING FLOW VIDEOS DONE: ${ok}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(res, null, 2));
  process.exit(ok === JOBS.length ? 0 : 1);
})();
