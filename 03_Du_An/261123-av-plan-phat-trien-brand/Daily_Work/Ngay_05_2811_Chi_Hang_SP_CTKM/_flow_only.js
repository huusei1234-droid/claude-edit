
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
flow.setup({ getPath: () => DATA });

const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const images = payload.refs.map((r) => ({
  name: r.name,
  mime: r.path.toLowerCase().endsWith(".png") ? "image/png" : "image/jpeg",
  base64: fs.readFileSync(r.path).toString("base64"),
}));

(async () => {
  const timer = setTimeout(() => { console.error("HARD_TIMEOUT_300S"); process.exit(3); }, 300000);
  timer.unref();
  const res = await handlers["flow:generate-video"](null, {
    prompt: payload.prompt,
    model: "Omni 1.2 Flash",
    aspect: "portrait",
    resolution: "720p",
    seconds: payload.sec,
    mode: "ingredients",
    count: 1,
    images,
  });
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  const b64 = res?.data || res?.videoBase64 || res?.items?.[0]?.data || res?.items?.[0]?.base64;
  if (!b64) {
    console.error("FLOW_ERR:", res?.error || "empty");
    process.exit(1);
  }
  const buf = Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
  if (buf.length > 240000) {
    fs.writeFileSync(payload.outPath, buf);
    console.log("FLOW_OK", Math.round(buf.length / 1024) + "KB");
    process.exit(0);
  }
  console.error("SMALL_BUF", buf.length);
  process.exit(1);
})();
