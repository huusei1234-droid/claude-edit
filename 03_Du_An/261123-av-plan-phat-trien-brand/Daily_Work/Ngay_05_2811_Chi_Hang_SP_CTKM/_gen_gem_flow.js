
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const handlers = {};
Module._load = (function(orig){
  return function(req){
    if(req==="electron") return { ipcMain: { handle: (c,f)=>{handlers[c]=f;}, on: ()=>{} }, dialog: { showErrorBox: (t,m)=>console.error(t,m) }, shell: { openExternal: async ()=>{} } };
    return orig.apply(this, arguments);
  };
})(Module._load);

const DESKTOP = "C:\\AI\\full studio\\canvas\\desktop";
const DATA = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const flow = require(path.join(DESKTOP, "flow-driver.js"));
const gemini = require(path.join(DESKTOP, "gemini-driver.js"));
flow.setup({ getPath: () => DATA });
gemini.setup({ getPath: () => DATA });

const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const images = payload.refPaths.map((p) => ({
  name: path.basename(p),
  mime: p.toLowerCase().endsWith(".png") ? "image/png" : "image/jpeg",
  base64: fs.readFileSync(p).toString("base64"),
}));

(async () => {
  const timer = setTimeout(() => { console.error("HARD_TIMEOUT_420S"); process.exit(3); }, 420000);
  timer.unref();
  const res = await handlers["gemini:generate-video"](null, {
    prompt: payload.prompt,
    ratio: "9:16",
    aspect: "portrait",
    seconds: payload.sec,
    flowSeconds: payload.flowSec || payload.sec,
    flowModel: "Omni 1.2 Flash",
    resolution: "720p",
    mode: "ingredients",
    images,
  });
  if (res?.challengeBlocked) {
    console.error("GEMINI_CHALLENGE_BLOCK");
    process.exit(2);
  }
  const b64 = res?.data || res?.videoBase64 || res?.items?.[0]?.data || res?.items?.[0]?.base64;
  if (!res?.ok || !b64) {
    console.error("GEN_ERR:", res?.error || "empty");
    process.exit(1);
  }
  const buf = Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
  if (buf.length > 200000) {
    fs.writeFileSync(payload.outPath, buf);
    console.log("GEN_OK", res.provider || "gemini", res.account || "", Math.round(buf.length / 1024) + "KB");
    process.exit(0);
  }
  console.error("SMALL_BUF", buf.length);
  process.exit(1);
})();
