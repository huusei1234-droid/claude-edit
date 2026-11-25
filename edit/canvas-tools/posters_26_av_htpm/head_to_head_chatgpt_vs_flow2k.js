/**
 * Head-to-Head Full-Resolution Comparison:
 * 1. ChatGPT (1024x1536 PNG inside active Brave ChatGPT project, auto-deletes chat)
 * 2. Google Flow Nano Banana Pro (2K Upscaled / 1K Full-Res PNG/JPG!)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "D:\\full studio_data\\infinite-canvas-flow";
const BENCH_DIR = "d:\\AI\\full studio\\projects\\av_htpm_26_posters_v3\\benchmark_3ai";
fs.mkdirSync(DATA_DIR, { recursive: true });

// Configure ChatGPT driver to use the active logged-in account's project ID!
fs.writeFileSync(
  path.join(DATA_DIR, "chatgpt-driver.json"),
  JSON.stringify({
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
  }, null, 2)
);

const handlers = {};
const origLoad = Module._load;
Module._load = function (req) {
  if (req === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: console.error },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));
flow.setup({ getPath: () => DATA_DIR });
chatgpt.setup({ getPath: () => DATA_DIR });

function fileToRefObj(filePath, customName) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
  return { base64: buf.toString("base64"), mime, name: customName || path.basename(filePath) };
}

const baseJs = fs.readFileSync("d:\\AI\\full studio\\projects\\av_htpm_26_posters_v3\\run_direct_3ai_benchmark.js", "utf8");
const rawPrompt = baseJs.split("const PROMPT_REF = `")[1].split("`;")[0];

async function runChatGPT() {
  const singleRef = [fileToRefObj(path.join(BENCH_DIR, "composite_ref_1file.jpg"), "ref_board.jpg")];
  const prompt = rawPrompt
    .replace(/ref_style_av\.jpg/g, "the left reference poster in ref_board.jpg")
    .replace(/ref_dk_box\.jpg/g, "the upper-right product photo in ref_board.jpg")
    .replace(/ref_ht_logo\.jpg/g, "the lower-right Yin-Yang logo in ref_board.jpg");
  const t0 = Date.now();
  console.log("[ChatGPT Full-Res] Starting...");
  const res = await handlers["chatgpt:generate-image"](null, {
    prompt,
    ratio: "2:3",
    count: 1,
    images: singleRef,
    keepChat: false,
    noFallback: true,
  });
  if (res && res.ok && res.data) {
    const out = path.join(BENCH_DIR, "FINAL_01_ChatGPT_FullRes.png");
    fs.writeFileSync(out, res.data);
    console.log(`[ChatGPT Full-Res] SUCCESS in ${Math.round((Date.now() - t0) / 1000)}s -> ${out} (${Math.round(res.data.length / 1024)} KB)`);
    return true;
  }
  console.error("[ChatGPT Full-Res] FAILED:", res?.error);
  return false;
}

async function runFlow2K() {
  const refs = [
    fileToRefObj("C:\\Users\\Hang thu\\.gemini\\antigravity\\brain\\3c47ebbb-8468-44f7-b584-19bc2acdc8cf\\.user_uploaded\\media_1795404719183_a2e19ad8.jpg", "ref_style_av.jpg"),
    fileToRefObj(path.join(BENCH_DIR, "ref_dk_packshot.jpg"), "ref_dk_box.jpg"),
    fileToRefObj(path.join(BENCH_DIR, "ref_ht_logo.jpg"), "ref_ht_logo.jpg"),
  ];
  const t0 = Date.now();
  console.log("[Flow Nano Banana Pro 2K] Starting...");
  const res = await handlers["flow:generate-image"](null, {
    prompt: `@ref_style_av.jpg @ref_dk_box.jpg @ref_ht_logo.jpg ` + rawPrompt,
    model: "Nano Banana Pro",
    ratio: "3:4",
    quality: "2K",
    count: 1,
    images: refs,
  });
  if (res && res.ok && res.data) {
    const ext = res.mime === "image/png" ? ".png" : res.mime === "image/webp" ? ".webp" : ".jpg";
    const out = path.join(BENCH_DIR, "FINAL_02_Flow_NanoBananaPro_2K" + ext);
    fs.writeFileSync(out, res.data);
    console.log(`[Flow Nano Banana Pro 2K] SUCCESS in ${Math.round((Date.now() - t0) / 1000)}s -> ${out} (${Math.round(res.data.length / 1024)} KB)`);
    return true;
  }
  console.error("[Flow Nano Banana Pro 2K] FAILED:", res?.error);
  return false;
}

(async () => {
  const [cOk, fOk] = await Promise.all([runChatGPT(), runFlow2K()]);
  console.log("HEAD-TO-HEAD COMPLETE:", { chatgpt: cOk, flow2K: fOk });
  process.exit(0);
})();
