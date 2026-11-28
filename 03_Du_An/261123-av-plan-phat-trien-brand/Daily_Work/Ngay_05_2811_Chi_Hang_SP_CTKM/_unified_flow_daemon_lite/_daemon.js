
const http = require("node:http");
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

process.on("uncaughtException", (err) => console.error("[DAEMON_UNCAUGHT]", err && err.message ? err.message : err));
process.on("unhandledRejection", (err) => console.error("[DAEMON_UNHANDLED]", err && err.message ? err.message : err));

const DESKTOP = "C:\\AI\\full studio\\canvas\\desktop";
const PRIV = process.argv[2];
const PORT = Number(process.argv[3] || 19489);
const flow = require(path.join(DESKTOP, "flow-driver.js"));

(async () => {
  fs.mkdirSync(PRIV, { recursive: true });
  const now = Date.now();
  const ex = now + 43200000;

  // Create a 2nd clean project on u/9/ (1,050 PRO credits!) via flow.ensureBrowser() so Slot A & Slot B run 2 parallel PRO projects on u/9/!
  const bootCfg = {
    minCredits: { video: 30, image: 5 },
    accounts: [{ id: "a1", name: "Boot u/9", profile: "MAIN_BRAVE", userPrefix: "u/9/", projectId: "44e5d459-c4fe-43e9-a700-a03d1ee35203", agentOwnedProjectIds: ["44e5d459-c4fe-43e9-a700-a03d1ee35203"], workerTargets: [{ prefix: "u/9/", projectId: "44e5d459-c4fe-43e9-a700-a03d1ee35203" }] }],
    active: "a1",
  };
  fs.writeFileSync(path.join(PRIV, "flow-driver.json"), JSON.stringify(bootCfg, null, 2), "utf8");
  flow.setup({ getPath: () => PRIV });

  let pid9_b = null;
  try {
    const b0 = await flow.ensureBrowser({ visible: true });
    await new Promise(r => setTimeout(r, 2000));
    const p = await flow.createBackgroundPage(b0, "https://flow.google.com/u/9/");
    if (p) {
      await new Promise(r => setTimeout(r, 2800));
      await p.evaluate(() => {
        const nb = document.querySelector("button.new-project-button") ||
          [...document.querySelectorAll("button")].find(x => /Dự án mới|New project/i.test(x.innerText || ""));
        if (nb) nb.click();
      }).catch(() => {});
      for (let k = 0; k < 20; k++) {
        await new Promise(r => setTimeout(r, 500));
        const pm = (p.url() || "").match(/\/project\/([0-9a-f-]{20,})/i);
        if (pm) { pid9_b = pm[1]; break; }
      }
      if (pid9_b) {
        await new Promise(r => setTimeout(r, 2000));
        await p.evaluate(() => {
          for (const btn of document.querySelectorAll("button")) {
            const t = (btn.innerText || "").trim();
            if (/^(Bắt đầu|Get started|Got it|Đã hiểu|Đóng|Close|close|right_panel_close)$/i.test(t)) btn.click();
          }
        }).catch(() => {});
      }
      await p.close().catch(() => {});
    }
  } catch (e) {
    console.error("[BOOT_P9B]", e.message);
  }

  const pid9_a = "44e5d459-c4fe-43e9-a700-a03d1ee35203";
  const targets = [
    { prefix: "u/9/", projectId: pid9_a, email: "lmtcvn005@gmail.com" },
    ...(pid9_b ? [{ prefix: "u/9/", projectId: pid9_b, email: "lmtcvn005@gmail.com" }] : []),
    { prefix: "u/6/", projectId: "733dbbe0-6db2-4a31-88e0-f10a19b06fb1", email: "capcutvid269@gmail.com" },
    { prefix: "u/8/", projectId: "bd07af14-1d54-4996-8883-72f2e724d0f5", email: "hieulan14d@gmail.com" },
  ];
  const ownedIds = targets.map(t => t.projectId);
  const prefixCredits = {
    "u/0/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/1/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/2/": { credits: 2, updatedAt: now, exhaustedUntil: ex },
    "u/3/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/4/": { credits: 20, updatedAt: now, exhaustedUntil: ex },
    "u/5/": { credits: 9, updatedAt: now, exhaustedUntil: ex },
    "u/7/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
    "u/9/": { credits: 1050, email: "lmtcvn005@gmail.com", updatedAt: now },
    "u/6/": { credits: 50, email: "capcutvid269@gmail.com", updatedAt: now },
    "u/8/": { credits: 22, email: "hieulan14d@gmail.com", updatedAt: now },
  };

  const finalCfg = {
    minCredits: { video: 30, image: 5 },
    accounts: [{
      id: "a1",
      name: "Unified PRO u/9 Pool (1050cr)",
      profile: "MAIN_BRAVE",
      userPrefix: "u/9/",
      projectId: pid9_a,
      preferredEmail: "lmtcvn005@gmail.com",
      agentOwnedProjectIds: ownedIds,
      workerProjectIds: ownedIds,
      prefixCredits,
      workerTargets: targets,
    }],
    active: "a1",
  };
  fs.writeFileSync(path.join(PRIV, "flow-driver.json"), JSON.stringify(finalCfg, null, 2), "utf8");
  flow.setup({ getPath: () => PRIV });

  const srv = http.createServer((req, res) => {
    if (req.url === "/ping") { res.writeHead(200); res.end("OK"); return; }
    if (req.url === "/quit") { res.writeHead(200); res.end("BYE"); setTimeout(() => process.exit(0), 200); return; }
    let body = "";
    req.on("data", ch => { body += ch; });
    req.on("end", async () => {
      try {
        const pl = JSON.parse(body);
        const images = pl.refs.map(r => ({
          name: r.name,
          mime: "image/jpeg",
          base64: fs.readFileSync(r.path).toString("base64"),
        }));
        const out = await handlers["flow:generate-video"](null, {
          prompt: pl.prompt,
          model: "Omni 1.2 Flash",
          aspect: "portrait",
          resolution: "720p",
          seconds: 10,
          mode: "ingredients",
          count: 1,
          images,
        });
        const b64 = out?.data || out?.videoBase64 || out?.items?.[0]?.data || out?.items?.[0]?.base64;
        if (!b64) {
          res.writeHead(500);
          res.end(JSON.stringify({ ok: false, error: out?.error || "empty" }));
          return;
        }
        const buf = Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
        if (buf.length > 200000) {
          fs.writeFileSync(pl.outPath, buf);
          res.writeHead(200);
          res.end(JSON.stringify({ ok: true, kb: Math.round(buf.length / 1024) }));
          return;
        }
        res.writeHead(500);
        res.end(JSON.stringify({ ok: false, error: "SMALL_BUF_" + buf.length }));
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ ok: false, error: String(e.message || e) }));
      }
    });
  });
  srv.listen(PORT, "127.0.0.1", () => console.log(`[DAEMON_READY] http://127.0.0.1:${PORT} targets=${targets.length} (u/9 1050cr)`));
})();
