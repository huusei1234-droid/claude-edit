/**
 * 3-Worker Parallel ChatGPT Masterpiece Poster Batch Runner (with automatic Flow 2K fallback if ChatGPT hits account limit!)
 * Auto-deletes every temporary chat in ChatGPT right after downloading each PNG.
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "D:\\full studio_data\\infinite-canvas-flow";
const V4_DIR = "d:\\AI\\full studio\\projects\\av_htpm_26_posters_v3\\v4_chatgpt_masterpieces";
fs.mkdirSync(DATA_DIR, { recursive: true });

fs.writeFileSync(
  path.join(DATA_DIR, "chatgpt-driver.json"),
  JSON.stringify(
    {
      accounts: [
        {
          id: "gpt1",
          name: "ChatGPT (Active Project)",
          profile: "MAIN_BRAVE",
          projectLabel: "ADS",
          projectId: "g-p-6ae816c24d308191b3d09468f10fa0fa",
        },
      ],
      active: "gpt1",
    },
    null,
    2
  )
);

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
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));
flow.setup({ getPath: () => DATA_DIR });
chatgpt.setup({ getPath: () => DATA_DIR });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function fileToRefObj(filePath, customName) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
  return { base64: buf.toString("base64"), mime, name: customName || path.basename(filePath) };
}

async function main() {
  const specPath = path.join(V4_DIR, "jobs_26_chatgpt.json");
  const jobs = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const maxConc = 3;
  let cursor = 0;
  let doneCount = 0;
  const results = [];

  async function worker(wId) {
    if (wId > 1) await sleep((wId - 1) * 2200);
    while (cursor < jobs.length) {
      const idx = cursor++;
      const j = jobs[idx];
      if (fs.existsSync(j.outPath) && fs.statSync(j.outPath).size > 120000) {
        doneCount++;
        console.log(`[SKIP ${doneCount}/${jobs.length}] ${j.id} already rendered (${Math.round(fs.statSync(j.outPath).size / 1024)} KB)`);
        results[idx] = { id: j.id, ok: true, provider: "cached", outPath: j.outPath };
        continue;
      }

      const imgs = (j.refs || []).map((r) => fileToRefObj(r.path, r.name));
      console.log(`[Worker#${wId} START] ${j.id} (${j.file_title})...`);
      const t0 = Date.now();
      let res = await handlers["chatgpt:generate-image"](null, {
        prompt: j.prompt,
        ratio: j.ratio || "2:3",
        count: 1,
        images: imgs,
        keepChat: false,
      });

      if (!res || !res.ok || !res.data || res.data.length < 80000) {
        console.warn(`[Worker#${wId} RETRY] ${j.id} first batch call returned err (${res?.error || "small"}), retrying once...`);
        await sleep(3000);
        res = await handlers["chatgpt:generate-image"](null, {
          prompt: j.prompt,
          ratio: j.ratio || "2:3",
          count: 1,
          images: imgs,
          keepChat: false,
        });
      }

      if (res && res.ok && res.data && res.data.length >= 60000) {
        fs.mkdirSync(path.dirname(j.outPath), { recursive: true });
        fs.writeFileSync(j.outPath, res.data);
        doneCount++;
        console.log(
          `[DONE ${doneCount}/${jobs.length}] ${j.id} via ${res.provider} in ${Math.round((Date.now() - t0) / 1000)}s (${Math.round(res.data.length / 1024)} KB)`
        );
        results[idx] = { id: j.id, ok: true, provider: res.provider, outPath: j.outPath };
      } else {
        console.error(`[FAIL] ${j.id}: ${res?.error || "no valid buffer"}`);
        results[idx] = { id: j.id, ok: false, error: res?.error || "failed" };
      }
    }
  }

  await Promise.all(Array.from({ length: maxConc }, (_, i) => worker(i + 1)));
  fs.writeFileSync(path.join(V4_DIR, "batch_results.json"), JSON.stringify(results, null, 2));
  const okTotal = results.filter((r) => r && r.ok).length;
  console.log(`=== BATCH FINISHED: ${okTotal}/${jobs.length} POSTERS GENERATED SUCCESSFULLY ===`);
  process.exit(okTotal === jobs.length ? 0 : 1);
}

main();
