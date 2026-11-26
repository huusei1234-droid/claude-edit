/**
 * Bổ sung trọn bộ 7 Clip Cận-Trung Pha Chế Thực Tế ("Từ cắt/xé gói stick -> trút bột vào ly -> chế nước vào ly bột")
 * cho cả 4 sản phẩm Ngày 03 (26/11/2026) trên Google Flow (4 tab chạy song song):
 * - v1_s08: AV Protein — Cắt/xé gói stick trắng-xanh & trút dòng bột đạm kem mịn vào ly thủy tinh
 * - v1_s09: AV Protein — Chế nước mát 20–40°C từ bình thủy tinh vào ly đang có bột đạm
 * - v2_s08: Bojomi — Cắt đầu gói stick Bojomi thật (`av02_bojomi_stick.png`) & trút bột ngũ cốc vào cốc thủy tinh (nối vào v2_s04 chế nước ấm 60°C!)
 * - v3_s08: Curcumilk Phyto — Cắt đầu gói stick Curcumilk thật (`av04_curcumilk_stick.png`) & trút bột nghệ vàng mịn vào cốc sứ kem
 * - v3_s09: Curcumilk Phyto — Chế 150ml nước ấm 40–50°C bốc hơi nhẹ từ bình vào cốc sứ đang có bột nghệ vàng
 * - v4_s08: Collamela — Xé/cắt đầu gói stick nhỏ trắng-xanh & trút dòng bột mịn hồng đào vào ly pha lê nhỏ
 * - v4_s09: Collamela — Chế 100ml nước mát trong veo từ bình thủy tinh vào ly pha lê đang có bột đào làm tan ánh hồng đào
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_03_2611";
const LOOK_DIR = path.join(WORK_DIR, "04_Video_Looks_9x16");
const CLIP_DIR = path.join(WORK_DIR, "05_Flow_Raw_Clips");
const CUTOUT_DIR = "G:\\My Drive\\dự án ngoài\\An Vượng\\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\\01. Ảnh Sản Phẩm Tách Nền & Logo";

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

const LK1 = loadImg(path.join(LOOK_DIR, "N03_LOOK1_AVP_MORNING_9x16.png"), "n03_look1_avp.png");
const LK2 = loadImg(path.join(LOOK_DIR, "N03_LOOK2_BOJOMI_OFFICE_9x16.png"), "n03_look2_boj.png");
const LK3 = loadImg(path.join(LOOK_DIR, "N03_LOOK3_CURCU_AFTERNOON_9x16.png"), "n03_look3_cur.png");
const LK4 = loadImg(path.join(LOOK_DIR, "N03_LOOK4_COL_EVENING_9x16.png"), "n03_look4_col.png");

const STICK_BOJ = loadImg(path.join(CUTOUT_DIR, "av02_bojomi_stick.png"), "bojomi_stick.png");
const STICK_CUR = loadImg(path.join(CUTOUT_DIR, "av04_curcumilk_stick.png"), "curcumilk_stick.png");

const NT = " Natural real-time tactile hand physics, closed gentle smile, ZERO speaking, ZERO lip-syncing, NO beach, NO sea, NO text overlays, NO watermarks.";

const PREP_JOBS = [
  // --- V1: AV PROTEIN ---
  {
    id: "v1_s08",
    outPath: path.join(CLIP_DIR, "v1_s08.mp4"),
    seconds: 4,
    images: [LK1],
    prompt:
      "Vertical 9:16 close-medium kitchen preparation shot: at her sunlit wooden home kitchen counter, the woman from n03_look1_avp.png in off-white navy-trim knit polo neatly tears open the top corner of a slim white-and-emerald-green single-serve foil stick sachet packet and pours a clean flowing stream of fine creamy-beige plant protein powder directly into an empty clear glass cup." + NT,
  },
  {
    id: "v1_s09",
    outPath: path.join(CLIP_DIR, "v1_s09.mp4"),
    seconds: 4,
    images: [LK1],
    prompt:
      "Vertical 9:16 close-medium tactile kitchen shot: at her sunlit wooden home kitchen counter, the woman from n03_look1_avp.png in off-white navy-trim knit polo pours a smooth crystal-clear stream of cool water from a glass pitcher directly into the clear glass cup containing fine creamy-beige protein powder, liquid rising cleanly." + NT,
  },

  // --- V2: BOJOMI (v2_s04 already pours 60C water from thermal flask onto powder!) ---
  {
    id: "v2_s08",
    outPath: path.join(CLIP_DIR, "v2_s08.mp4"),
    seconds: 4,
    images: [LK2, STICK_BOJ],
    prompt:
      "Vertical 9:16 close-medium office desk preparation shot: at her bright wooden office desk, the woman from n03_look2_boj.png in ivory silk bow blouse neatly cuts open the gold-crimped top of the white-and-emerald BOJOMI stick packet from bojomi_stick.png with clean small scissors and pours a smooth stream of fine creamy cereal powder directly into an empty clear glass mug." + NT,
  },

  // --- V3: CURCUMILK PHYTO ---
  {
    id: "v3_s08",
    outPath: path.join(CLIP_DIR, "v3_s08.mp4"),
    seconds: 4,
    images: [LK3, STICK_CUR],
    prompt:
      "Vertical 9:16 close-medium cozy kitchen preparation shot: at her warm wooden home counter, the woman from n03_look3_cur.png in butter-yellow cardigan neatly tears open the top gold-crimped edge of the white-and-emerald CURCUMILK stick packet from curcumilk_stick.png and pours a clean stream of fine golden-yellow turmeric cereal powder directly into an empty cream ceramic mug." + NT,
  },
  {
    id: "v3_s09",
    outPath: path.join(CLIP_DIR, "v3_s09.mp4"),
    seconds: 4,
    images: [LK3],
    prompt:
      "Vertical 9:16 close-medium tactile afternoon shot: at her warm wooden home counter, the woman from n03_look3_cur.png in butter-yellow cardigan pours a steady stream of warm steaming water from a sleek white kettle directly into the cream ceramic mug containing golden-yellow turmeric powder, soft warm steam rising." + NT,
  },

  // --- V4: COLLAMELA ---
  {
    id: "v4_s08",
    outPath: path.join(CLIP_DIR, "v4_s08.mp4"),
    seconds: 4,
    images: [LK4],
    prompt:
      "Vertical 9:16 close-medium evening routine shot: at her warm-lit bedroom table, the woman from n03_look4_col.png in pastel sky-blue silk pajamas neatly tears open the top end of a slim glossy white-and-emerald single-serve collagen stick sachet and pours fine light-pinkish peach powder directly into an empty small crystal glass." + NT,
  },
  {
    id: "v4_s09",
    outPath: path.join(CLIP_DIR, "v4_s09.mp4"),
    seconds: 4,
    images: [LK4],
    prompt:
      "Vertical 9:16 close-medium evening beauty prep shot: at her warm-lit bedroom table, the woman from n03_look4_col.png in pastel sky-blue silk pajamas pours 100ml of cool clear water from a sleek glass carafe directly onto the fine peach powder inside the small crystal glass, dissolving into a fresh translucent rosy-peach drink." + NT,
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

async function runVideoOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 120000) {
    console.log(`[SKIP VID] ${job.id} cached`);
    return { id: job.id, ok: true, cached: true };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START PREP VID] ${job.id} (${job.seconds}s, ${job.images.length} refs) try ${attempt}/2...`);
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
      if (buf && buf.length > 120000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE PREP VID] ${job.id} -> ${(buf.length / 1024).toFixed(0)} KB`);
        return { id: job.id, ok: true, bytes: buf.length };
      }
      console.warn(`[WARN PREP VID] ${job.id} try ${attempt}:`, res?.error || "empty buffer");
    } catch (e) {
      console.warn(`[ERR PREP VID] ${job.id} try ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3500));
  }
  return { id: job.id, ok: false };
}

async function runPool(items, concurrency, fn) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 2200));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

(async () => {
  const t0 = Date.now();
  console.log(`=== GENERATING ${PREP_JOBS.length} SACHET-TEAR & WATER-POUR CLIPS (concurrency=4) ===`);
  const res = await runPool(PREP_JOBS, 4, runVideoOne);
  const ok = res.filter((r) => r && r.ok).length;
  console.log(`=== PREP CLIPS DONE: ${ok}/${PREP_JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  process.exit(ok === PREP_JOBS.length ? 0 : 1);
})();
