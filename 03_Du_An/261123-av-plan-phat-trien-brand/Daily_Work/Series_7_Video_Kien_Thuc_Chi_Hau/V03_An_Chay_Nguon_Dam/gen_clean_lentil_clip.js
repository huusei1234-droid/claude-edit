
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const WORK_DIR = "C:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Series_7_Video_Kien_Thuc_Chi_Hau\\V03_An_Chay_Nguon_Dam";

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

const lkBuf = fs.readFileSync(path.join(WORK_DIR, "02_ChatGPT_Looks_9x16", "V03_LOOK_APRON_KITCHEN.jpg"));
const LK_COOK = { name: "hau_kitchen_apron.jpg", mime: "image/jpeg", base64: lkBuf.toString("base64") };

(async () => {
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  const outPath = path.join(WORK_DIR, "03_Flow_Clips_9x16", "c2_lentils.mp4");
  const res = await handlers["flow:generate-video"](null, {
    prompt: "Vertical 9:16 sunlit home kitchen tabletop close-up: graceful hands of the woman from hau_kitchen_apron.jpg place a warm ceramic bowl of cooked hearty lentils right beside a bowl of golden chickpeas and a plate of tofu in red tomato sauce on a clean wooden counter, soft natural morning light, ZERO speaking, ZERO text, ZERO watermarks.",
    model: "Omni 1.2 Flash",
    aspect: "portrait",
    resolution: "720p",
    seconds: 4,
    mode: "ingredients",
    count: 1,
    images: [LK_COOK],
  });
  let buf = null;
  if (res?.videoPath && fs.existsSync(res.videoPath)) buf = fs.readFileSync(res.videoPath);
  else if (res?.data) buf = Buffer.isBuffer(res.data) ? res.data : Buffer.from(String(res.data).replace(/^data:video\/\w+;base64,/, ""), "base64");
  if (!buf || buf.length < 120000) throw new Error("Failed generating c2_lentils.mp4");
  fs.writeFileSync(outPath, buf);
  console.log("[DONE] c2_lentils.mp4 ->", Math.round(buf.length / 1024), "KB");
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  process.exit(0);
})();
