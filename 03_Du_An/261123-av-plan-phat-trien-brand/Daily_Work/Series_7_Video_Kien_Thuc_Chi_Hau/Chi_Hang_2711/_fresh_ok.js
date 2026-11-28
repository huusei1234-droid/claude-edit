
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const handlers = {};
Module._load = (function(orig){
  return function(req){
    if(req==="electron") return { ipcMain: { handle: (c,f)=>{handlers[c]=f;} }, dialog: { showErrorBox: ()=>{} } };
    return orig.apply(this, arguments);
  };
})(Module._load);
const flow = require("C:\\AI\\full studio\\canvas\\desktop\\flow-driver.js");
flow.setup({ getPath: () => "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow" });
const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const refBuf = fs.readFileSync(payload.refPath);
const ref = { name: payload.uniqueRefName, mime: "image/jpeg", base64: refBuf.toString("base64") };
(async () => {
  const timer = setTimeout(() => { console.error("TIMEOUT"); process.exit(3); }, 240000);
  timer.unref();
  const res = await handlers["flow:generate-video"](null, {
    prompt: payload.prompt, model: "Omni 1.2 Flash", aspect: "portrait", resolution: "720p",
    seconds: payload.sec, mode: "ingredients", count: 1, images: [ref]
  });
  const b64 = res?.data || res?.videoBase64 || res?.items?.[0]?.data || res?.items?.[0]?.base64;
  if (!b64) { console.error("ERR:", res?.error); process.exit(1); }
  const buf = Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
  if (buf.length > 260000) { fs.writeFileSync(payload.outPath, buf); process.exit(0); }
  process.exit(1);
})();
