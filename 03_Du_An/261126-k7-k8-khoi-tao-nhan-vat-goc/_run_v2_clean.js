
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
fs.mkdirSync(DATA_DIR, { recursive: true });

const origLoad = Module._load;
Module._load = function (req, parent, isMain) {
  if (req === "electron") {
    return {
      ipcMain: { handle: () => {} },
      dialog: { showErrorBox: (t, m) => console.error("[STUDIO DIALOG]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
flow.setup({ getPath: () => DATA_DIR });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function isValidSquareImage(buf) {
  if (!buf || buf.length < 400000) return false;
  if (buf.slice(4, 8).toString("ascii") === "ftyp") return false;
  const isPng = buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
  const isJpg = buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff;
  const isWebp = buf.slice(0, 4).toString("ascii") === "RIFF" && buf.slice(8, 12).toString("ascii") === "WEBP";
  if (!isPng && !isJpg && !isWebp) return false;
  if (isPng && buf.length > 24) {
    const w = buf.readUInt32BE(16);
    const h = buf.readUInt32BE(20);
    if (w < h * 0.80 || h < w * 0.80) return false;
  }
  return true;
}

(async () => {
  try {
    const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
    const seen = new Set();
    for (const j of jobs) {
      if (fs.existsSync(j.outPath)) {
        const ex = fs.readFileSync(j.outPath);
        if (isValidSquareImage(ex)) {
          seen.add(crypto.createHash("md5").update(ex).digest("hex"));
          console.log(`[SKIP V2] ${j.id} already verified on disk (${Math.round(ex.length/1024)} KB)`);
          continue;
        }
      }
      let ok = false;
      for (let attempt = 1; attempt <= 5; attempt++) {
        console.log(`[GEN V2] ${j.id} attempt #${attempt}...`);
        const t0 = Date.now();
        let items = null;
        try {
          items = await flow.generateImageFallback({
            prompt: j.prompt + (attempt > 1 ? ` [editorial take ${attempt}]` : ""),
            ratio: "1:1",
            aspect: "square",
            count: 1,
            images: [],
          });
        } catch (err) {
          console.warn(`[RETRY V2] ${j.id} attempt #${attempt} error: ${err?.message || err}`);
          await sleep(4500);
          continue;
        }
        const buf = items && items[0] && items[0].data;
        if (!isValidSquareImage(buf)) {
          console.warn(`[GUARD REJECT] ${j.id} invalid image/video buffer (${buf ? buf.length : 0} bytes) -> retrying!`);
          await sleep(3500);
          continue;
        }
        const h = crypto.createHash("md5").update(buf).digest("hex");
        if (seen.has(h)) {
          console.warn(`[DUP_GUARD] ${j.id} duplicate hash ${h.slice(0,8)} -> retrying!`);
          await sleep(3500);
          continue;
        }
        seen.add(h);
        fs.mkdirSync(path.dirname(j.outPath), { recursive: true });
        fs.writeFileSync(j.outPath, buf);
        console.log(`[DONE V2] ${j.id} in ${Math.round((Date.now() - t0)/1000)}s (${Math.round(buf.length/1024)} KB)`);
        ok = true;
        break;
      }
      if (!ok) throw new Error(`Failed to generate valid image for ${j.id}`);
    }
  } finally {
    flow.destroy();
  }
  process.exit(0);
})();
