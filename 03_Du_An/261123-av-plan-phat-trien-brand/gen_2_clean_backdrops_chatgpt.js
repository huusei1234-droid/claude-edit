/**
 * Generate 2 ULTRA-CLEAN EMPTY 3D Studio Stage Backdrops via ChatGPT (HTPM project on Brave :9333)
 * Auto-deletes temporary chats after download (keepChat: false).
 * ZERO text, ZERO product boxes, ZERO logos in the generated images!
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "D:\\full studio_data\\infinite-canvas-flow";
const OUT_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\assets_stage";
fs.mkdirSync(DATA_DIR, { recursive: true });
fs.mkdirSync(OUT_DIR, { recursive: true });

// Configure official HTPM project in chatgpt-driver.json (per AGENTS.md Rule 3)
fs.writeFileSync(
  path.join(DATA_DIR, "chatgpt-driver.json"),
  JSON.stringify(
    {
      accounts: [
        {
          id: "gpt_htpm",
          name: "ChatGPT HTPM",
          profile: "MAIN_BRAVE",
          projectLabel: "HTPM",
          projectId: "g-p-6afbde0b943481919c6ec31a3b4f8642",
        },
      ],
      active: "gpt_htpm",
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

const JOBS = [
  {
    id: "bg_droppii_8th_stage",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "bg_droppii_8th_stage.png"),
    prompt:
      "Ultra-clean luxury 3D commercial e-commerce product photography stage background, square 1:1 composition, bright celebratory royal-blue, pearl-white and champagne-gold lighting. " +
      "In the top-left corner: three glossy metallic royal-blue and pearl-white helium balloons floating gently with thin gold ribbons. " +
      "In the top-right corner: one elegant pearl-white luxury 3D gift box tied with a shimmering royal-blue satin ribbon bow floating slightly with festive golden confetti ribbons and sparkling golden light bokeh. " +
      "Center background: radiant sunlit soft sky-blue to pure luminous white studio glow, completely clean and uncluttered so products placed later stand out clearly. " +
      "Lower middle (around 66% to 78% from top): a wide, sleek, wide-span circular luxury white marble display podium platform with a gleaming brushed champagne-gold metallic rim and soft mirror-like studio floor reflection. " +
      "Bottom corners: subtle flowing royal-blue translucent silk ribbons framing the bottom edges gracefully. " +
      "STRICT RULES: ABSOLUTELY NO TEXT, NO LETTERS, NO NUMBERS, NO LOGOS, NO PRODUCT BOXES ON THE PODIUM — leave the entire white-and-gold marble podium completely EMPTY and ready for product compositing. Photorealistic 8K cinema-grade advertising studio lighting.",
  },
  {
    id: "bg_av_guide_cream_emerald",
    ratio: "3:4",
    outPath: path.join(OUT_DIR, "bg_av_guide_cream_emerald.png"),
    prompt:
      "Ultra-clean luxury pharmaceutical infographic background, vertical 3:4 portrait composition, warm sunlit ivory-cream marble and delicate botanical sage-emerald accents at top and bottom edges. " +
      "Top border: rich deep forest-emerald green luxury header backdrop band with subtle sunlit eucalyptus and olive leaves peeking softly from the top-left and top-right corners and warm champagne-gold light rays. " +
      "Center area (75% of canvas): luminous soft warm cream-white silk texture with very subtle pale golden-beige geometric glow, completely uncluttered and smooth for crisp dark-emerald typography and instruction cards. " +
      "Bottom border: thin soft emerald-and-gold botanical shadow accent. " +
      "STRICT RULES: ABSOLUTELY NO TEXT, NO LETTERS, NO NUMBERS, NO ICONS, NO LOGOS, NO BOXES, NO PEOPLE. Clean editorial pharmaceutical aesthetic, 8K ultra-crisp lighting.",
  },
];

async function runJob(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 100000) {
    console.log(`[SKIP] ${job.id} already exists`);
    return { id: job.id, ok: true, provider: "cached" };
  }
  console.log(`[START] ${job.id} via ChatGPT HTPM...`);
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: [],
        keepChat: false,
      });
      const b64 =
        res?.data ||
        res?.items?.[0]?.data ||
        res?.items?.[0]?.base64 ||
        res?.images?.[0]?.base64 ||
        res?.image?.base64 ||
        res?.base64 ||
        (Array.isArray(res) && (res[0]?.data || res[0]?.base64));
      const url = res?.items?.[0]?.url || res?.images?.[0]?.url || res?.url;
      if (b64) {
        let buf;
        if (Buffer.isBuffer(b64)) buf = b64;
        else if (b64 instanceof Uint8Array) buf = Buffer.from(b64);
        else if (Array.isArray(b64)) buf = Buffer.from(b64);
        else buf = Buffer.from(String(b64).replace(/^data:image\/\w+;base64,/, ""), "base64");
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE ChatGPT #${attempt}] ${job.id} -> ${job.outPath} (${fs.statSync(job.outPath).size} bytes)`);
        return { id: job.id, ok: true, provider: "chatgpt" };
      } else if (url && url.startsWith("http")) {
        const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE ChatGPT URL #${attempt}] ${job.id} -> ${job.outPath} (${buf.length} bytes)`);
        return { id: job.id, ok: true, provider: "chatgpt" };
      } else if (res?.paths?.[0] && fs.existsSync(res.paths[0])) {
        fs.copyFileSync(res.paths[0], job.outPath);
        console.log(`[DONE ChatGPT Path #${attempt}] ${job.id} -> ${job.outPath}`);
        return { id: job.id, ok: true, provider: "chatgpt" };
      }
      console.warn(`[WARN ChatGPT #${attempt}] Unexpected response keys:`, Object.keys(res || {}));
    } catch (err) {
      console.error(`[ERR ChatGPT #${attempt}] ${job.id}:`, err.message);
    }
  }
  // Fallback to Flow Nano Banana 2 if ChatGPT fails twice
  try {
    console.log(`[FALLBACK Flow] ${job.id}...`);
    const resF = await handlers["flow:generate-image"](null, {
      prompt: job.prompt,
      ratio: job.ratio,
      model: "flow-nano-banana-pro",
      count: 1,
    });
    const b64 = resF?.images?.[0]?.base64 || resF?.base64;
    if (b64) {
      fs.writeFileSync(job.outPath, Buffer.from(b64.replace(/^data:image\/\w+;base64,/, ""), "base64"));
      console.log(`[DONE Flow] ${job.id}`);
      return { id: job.id, ok: true, provider: "flow" };
    }
  } catch (e2) {
    console.error(`[ERR Flow] ${job.id}:`, e2.message);
  }
  return { id: job.id, ok: false };
}

(async () => {
  const results = await Promise.all(JOBS.map((j, i) => new Promise((r) => setTimeout(r, i * 2500)).then(() => runJob(j))));
  console.log("=== BACKDROP RESULTS ===", JSON.stringify(results));
  process.exit(results.every((r) => r.ok) ? 0 : 1);
})();
