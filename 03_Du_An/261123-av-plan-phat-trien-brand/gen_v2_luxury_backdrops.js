/**
 * Generate 2 ULTRA-LUXURY 3D Pharmaceutical Gala Stage Backdrops via Full Studio (ChatGPT HTPM -> Flow 2K fallback)
 * Auto-deletes temporary chats after download (keepChat: false).
 * ZERO text, ZERO product boxes, ZERO cheap cartoon balloons!
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\AI\\full studio_data\\infinite-canvas-flow";
const OUT_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\assets_stage_v2";
fs.mkdirSync(DATA_DIR, { recursive: true });
fs.mkdirSync(OUT_DIR, { recursive: true });

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
    id: "bg_stage_emerald_champagne_v2",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "bg_stage_emerald_champagne_v2.png"),
    prompt:
      "Ultra-luxury international pharmaceutical & skincare anniversary campaign 3D key-visual studio backdrop, square 1:1 composition, inspired by Lancôme, Estée Lauder, and Abbott flagship displays. " +
      "Upper background (top 26%): rich deep imperial emerald-green architectural velvet arch (#053322 to #0A4A32) with delicate brushed 24K champagne-gold trim lines and subtle floating champagne-gold silk ribbons + soft warm golden bokeh sparkles celebrating an anniversary gala (NO cheap balloons, NO clutter). " +
      "Center studio zone (from 26% to 68% height): luminous warm sunlit champagne-ivory and pearl-cream radial studio glow (#FFFDF7 to #F7EED8) creating an airy, high-contrast bright halo so white-and-emerald product boxes placed in front look crisp, radiant, and expensive. " +
      "Lower showcase zone (around 66% to 79% from top): a grand, extra-wide, sleek oval two-tier luxury white Calacatta-gold marble exhibition podium platform with a thin gleaming brushed champagne-brass metallic rim, realistic studio specular highlights, and a soft warm champagne-emerald marble floor below (80% to 100%) for pricing plinths. " +
      "STRICT RULES: ABSOLUTELY NO TEXT, NO LETTERS, NO NUMBERS, NO LOGOS, NO BOTTLES, NO BOXES, NO BALLOONS — the entire marble podium and center stage must be 100% EMPTY and clean. 8K cinema-grade commercial product photography lighting.",
  },
  {
    id: "bg_guide_royal_emerald_v2",
    ratio: "3:4",
    outPath: path.join(OUT_DIR, "bg_guide_royal_emerald_v2.png"),
    prompt:
      "Ultra-luxury editorial pharmaceutical brand guideline & partner handbook background, vertical 3:4 portrait composition. " +
      "Top 20% header area: deep imperial forest-emerald luxury silk & architectural paneling (#053322) accented with delicate warm 24K champagne-gold light rays and subtle sunlit botanical olive/eucalyptus leaves tucked only at the extreme top corners. " +
      "Main body (20% to 93%): pristine warm pearl-ivory fine paper & soft cream marble texture (#FCF9F2) with ultra-subtle champagne ambient glow — completely smooth, bright, and clean for sharp dark-emerald typography and data cards. " +
      "Bottom 7%: deep forest-emerald luxury footer band with a fine brushed gold hairline border. " +
      "STRICT RULES: ABSOLUTELY NO TEXT, NO LETTERS, NO NUMBERS, NO ICONS, NO LOGOS, NO FRAMES, NO BOXES. 8K editorial minimalism.",
  },
];

async function runJob(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 120000) {
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
  const results = [];
  for (const j of JOBS) {
    results.push(await runJob(j));
  }
  console.log("=== V2 BACKDROP RESULTS ===", JSON.stringify(results));
  process.exit(results.every((r) => r.ok) ? 0 : 1);
})();
