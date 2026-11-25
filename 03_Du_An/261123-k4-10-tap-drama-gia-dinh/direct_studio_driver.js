/**
 * Direct Studio Driver Bridge v3 — Cinema Director Edition
 * - ChatGPT Image Generation (`keepChat: false` -> immediate auto-delete of temporary chat)
 * - Google Flow Video Generation (`Omni 1.2 Flash`, `ingredients` mode, MD5 `DUP_GUARD`, buffered `seconds` 8..12s)
 */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "D:\\full studio_data\\infinite-canvas-flow";
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
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));

const mockApp = { getPath: () => DATA_DIR };
flow.setup(mockApp);
chatgpt.setup(mockApp);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function fileToRefObj(filePath, customName) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
  const name = customName || path.basename(filePath);
  return { base64: buf.toString("base64"), mime, name };
}

async function runImageJobs(specPath) {
  const jobs = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const maxConc = Number(process.env.GPT_MAX_CONC || 3);
  let cursor = 0;
  const results = [];

  async function worker(wId) {
    if (wId > 1) await sleep((wId - 1) * 1500);
    while (cursor < jobs.length) {
      const idx = cursor++;
      const j = jobs[idx];
      if (fs.existsSync(j.outPath) && fs.statSync(j.outPath).size > 250000 && !j.overwrite) {
        console.log(`[ChatGPT SKIP] ${j.id} already exists (${Math.round(fs.statSync(j.outPath).size / 1024)} KB)`);
        results[idx] = { id: j.id, ok: true, cached: true, outPath: j.outPath };
        continue;
      }
      // Always pass <= 1 composite reference image so ChatGPT single-file upload works 100% natively!
      const imgs = (j.refs || []).slice(0, 1).map((r) => fileToRefObj(r.path, r.name));
      let okDone = false;
      for (let att = 1; att <= 2; att++) {
        console.log(`[ChatGPT START #${wId}] ${j.id} (att ${att}/2, ${j.ratio || "1:1"}, refs=${imgs.length})...`);
        const t0 = Date.now();
        const res = await handlers["chatgpt:generate-image"](null, {
          prompt: j.prompt,
          ratio: j.ratio || "1:1",
          count: 1,
          images: imgs,
          keepChat: false,
        });
        if (res && res.ok && res.data && res.data.length > 50000) {
          fs.mkdirSync(path.dirname(j.outPath), { recursive: true });
          fs.writeFileSync(j.outPath, res.data);
          console.log(`[ChatGPT DONE] ${j.id} via ${res.provider} in ${Math.round((Date.now() - t0) / 1000)}s (${Math.round(res.data.length / 1024)} KB, chat deleted)`);
          results[idx] = { id: j.id, ok: true, provider: res.provider, outPath: j.outPath };
          okDone = true;
          break;
        }
        console.warn(`[ChatGPT RETRY] ${j.id} att ${att} failed: ${res?.error || "small/no buffer"}`);
        await sleep(4000);
      }
      if (!okDone) {
        console.error(`[ChatGPT FAIL] ${j.id} failed after 2 attempts`);
        results[idx] = { id: j.id, ok: false };
      }
    }
  }

  await Promise.all(Array.from({ length: Math.min(maxConc, jobs.length) }, (_, i) => worker(i + 1)));
  const okCount = results.filter((r) => r && r.ok).length;
  console.log(`\n=== CHATGPT IMAGE SUMMARY: ${okCount}/${jobs.length} SUCCEEDED ===`);
  return results;
}

async function runVideoJobs(specPath) {
  const jobs = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const maxConc = Number(process.env.FLOW_MAX_CONC || (jobs.length <= 6 ? 2 : 3));
  let cursor = 0;
  const results = [];
  const failedIds = [];
  const seenHashes = new Map();
  for (const j of jobs) {
    if (fs.existsSync(j.outPath) && fs.statSync(j.outPath).size > 80000 && !j.overwrite) {
      const h = crypto.createHash("md5").update(fs.readFileSync(j.outPath)).digest("hex");
      seenHashes.set(h, j.id);
    }
  }

  async function worker(wId) {
    if (wId > 1) await sleep((wId - 1) * 5000);
    while (cursor < jobs.length) {
      const idx = cursor++;
      const j = jobs[idx];
      if (fs.existsSync(j.outPath) && fs.statSync(j.outPath).size > 80000 && !j.overwrite) {
        console.log(`[Flow SKIP] ${j.id} already on disk (${Math.round(fs.statSync(j.outPath).size / 1024)} KB)`);
        results[idx] = { id: j.id, ok: true, cached: true, outPath: j.outPath };
        continue;
      }
      const imgs = j.refs.slice(0, 3).map((r) => fileToRefObj(r.path, r.name));
      const baseVariants = Array.isArray(j.prompts) && j.prompts.length ? j.prompts : [j.prompt];
      const variants = [
        ...baseVariants,
        baseVariants[baseVariants.length - 1] + " Tất cả nhân vật đều là người lớn trưởng thành đang trò chuyện gia đình văn minh lịch sự."
      ];
      const aspect = ["9:16", "3:4", "portrait"].includes(String(j.ratio || "9:16")) ? "portrait" : "landscape";
      const seconds = Math.min(15, Math.max(6, Math.round(Number(j.seconds) || 8)));

      let saved = false;
      let lastErr = "";
      for (let vIdx = 0; vIdx < variants.length; vIdx++) {
        const prm = variants[vIdx];
        console.log(`[Flow START #${wId}] ${j.id} [${j.ratio || "9:16"}, ${seconds}s, v#${vIdx + 1}/${variants.length}, refs=${imgs.map((x) => x.name).join(",")}]`);
        const t0 = Date.now();
        const res = await handlers["flow:generate-video"](null, {
          prompt: prm,
          model: "Omni 1.2 Flash",
          mode: "ingredients",
          aspect,
          resolution: "720p",
          seconds,
          count: 1,
          images: imgs,
        });
        if (res && res.ok && res.data && res.data.length > 50000) {
          const h = crypto.createHash("md5").update(res.data).digest("hex");
          if (seenHashes.has(h) && seenHashes.get(h) !== j.id) {
            lastErr = `Duplicate grid download collision with ${seenHashes.get(h)} (md5=${h.slice(0, 8)})`;
            console.warn(`[Flow DUP_GUARD] ${j.id} collided with ${seenHashes.get(h)} -> retrying cleanly!`);
            await sleep(5000);
            continue;
          }
          seenHashes.set(h, j.id);
          fs.mkdirSync(path.dirname(j.outPath), { recursive: true });
          fs.writeFileSync(j.outPath, res.data);
          console.log(`[Flow DONE] ${j.id} (${j.ratio}) in ${Math.round((Date.now() - t0) / 1000)}s (${Math.round(res.data.length / 1024)} KB) -> ${j.outPath}`);
          results[idx] = { id: j.id, ok: true, provider: "flow-omni-1.2-flash", outPath: j.outPath };
          saved = true;
          break;
        }
        lastErr = res?.error || "empty video data";
        console.warn(`[Flow RETRY] ${j.id} v#${vIdx + 1} failed: ${lastErr}`);
        await sleep(/unusual activity/i.test(lastErr) ? 14000 : 6500);
      }

      if (!saved) {
        console.error(`[Flow NEEDS_SECOND_PASS] ${j.id} failed all ${variants.length} attempts: ${lastErr}`);
        failedIds.push({ id: j.id, error: lastErr });
        results[idx] = { id: j.id, ok: false, error: lastErr };
      }
    }
  }

  await Promise.all(Array.from({ length: Math.min(maxConc, jobs.length) }, (_, i) => worker(i + 1)));
  console.log(`\n=== BATCH SUMMARY: ${jobs.length - failedIds.length}/${jobs.length} SUCCEEDED ===`);
  if (failedIds.length) {
    const failPath = specPath.replace(/\.json$/i, ".failed.json");
    fs.writeFileSync(failPath, JSON.stringify(failedIds, null, 2));
    console.log(`Saved failed list -> ${failPath}`);
  }
  return results;
}

(async () => {
  const mode = process.argv[2];
  const spec = process.argv[3];
  if (mode === "gen_images") {
    await runImageJobs(spec);
  } else if (mode === "gen_videos") {
    await runVideoJobs(spec);
  } else {
    console.error("Usage: node direct_studio_driver.js <gen_images|gen_videos> <spec.json>");
    process.exit(1);
  }
  process.exit(0);
})();
