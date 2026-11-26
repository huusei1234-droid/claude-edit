
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
fs.mkdirSync(DATA_DIR, { recursive: true });

const handlers = {};
const origLoad = Module._load;
Module._load = function (req, parent, isMain) {
  if (req === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: (t, m) => console.error("[STUDIO DIALOG]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
flow.setup({ getPath: () => DATA_DIR });

(async () => {
  try {
    const pySpec = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
    const seen = new Set();
    // Seed hashes of K7 so 0% collision with K7
    const k7Dir = "C:\\AI\\full studio\\03_Du_An\\261126-k7-k8-khoi-tao-nhan-vat-goc\\raw_k7";
    for (const f of fs.readdirSync(k7Dir)) {
      const fp = path.join(k7Dir, f);
      if (fs.statSync(fp).isFile()) {
        seen.add(crypto.createHash("md5").update(fs.readFileSync(fp)).digest("hex"));
      }
    }
    for (const j of pySpec) {
      let saved = false;
      for (let r = 1; r <= 3; r++) {
        console.log(`[K8 START] ${j.id} attempt #${r}...`);
        const t0 = Date.now();
        const items = await flow.generateImageFallback({
          prompt: j.prompt + (r > 1 ? ` [variation ${r}]` : ""),
          ratio: "1:1",
          aspect: "square",
          count: 1,
          images: [],
        });
        const buf = items && items[0] && items[0].data;
        if (buf && buf.length > 450000) {
          const h = crypto.createHash("md5").update(buf).digest("hex");
          if (seen.has(h)) {
            console.warn(`[K8 DUP_GUARD] ${j.id} collided -> retrying!`);
            continue;
          }
          seen.add(h);
          fs.mkdirSync(path.dirname(j.outPath), { recursive: true });
          fs.writeFileSync(j.outPath, buf);
          console.log(`[K8 DONE] ${j.id} in ${Math.round((Date.now() - t0)/1000)}s (${Math.round(buf.length/1024)} KB)`);
          saved = true;
          break;
        }
      }
      if (!saved) throw new Error(`Failed to generate ${j.id}`);
    }
  } finally {
    flow.destroy();
  }
  process.exit(0);
})();
