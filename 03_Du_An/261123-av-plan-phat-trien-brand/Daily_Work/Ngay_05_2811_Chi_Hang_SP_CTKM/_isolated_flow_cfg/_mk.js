
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const handlers = {};
Module._load = (function(orig){
  return function(req){
    if(req==="electron") return { ipcMain: { handle: (c,f)=>{handlers[c]=f;}, on: ()=>{} }, dialog: { showErrorBox: ()=>{} }, shell: { openExternal: async ()=>{} } };
    return orig.apply(this, arguments);
  };
})(Module._load);

const DESKTOP = "C:\\AI\\full studio\\canvas\\desktop";
const PRIV = process.argv[2];
const flow = require(path.join(DESKTOP, "flow-driver.js"));
flow.setup({ getPath: () => PRIV });

(async () => {
  const b = await flow.ensureBrowser({ visible: true });
  const p = await flow.createBackgroundPage(b, "https://flow.google.com/u/7/");
  let pid = null;
  try {
    await new Promise(r => setTimeout(r, 3800));
    await p.evaluate(() => {
      const btn = document.querySelector("button.new-project-button") ||
        [...document.querySelectorAll("button")].find(x => /Dự án mới|New project/i.test(x.innerText || ""));
      if (btn) btn.click();
    });
    for (let w = 0; w < 24; w++) {
      await new Promise(r => setTimeout(r, 500));
      const m = (p.url() || "").match(/\/project\/([0-9a-f-]{20,})/i);
      if (m) { pid = m[1]; break; }
    }
    await new Promise(r => setTimeout(r, 2500));
    await p.evaluate(() => {
      for (const btn of document.querySelectorAll("button")) {
        const t = (btn.innerText || "").trim();
        if (/^(Bắt đầu|Get started|Got it|Đã hiểu|Đóng|Close|close)$/i.test(t)) btn.click();
      }
    }).catch(() => {});
  } finally {
    await p.close().catch(() => {});
  }
  if (!pid) { console.error("NO_PID"); process.exit(2); }
  const now = Date.now();
  const cfg = {
    minCredits: { video: 60, image: 10 },
    accounts: [{
      id: "a1",
      name: "Isolated AVPM Sample u/7",
      profile: "MAIN_BRAVE",
      userPrefix: "u/7/",
      projectId: pid,
      preferredEmail: "",
      agentOwnedProjects: [pid],
      prefixCredits: {
        "u/0/": { credits: 0, updatedAt: now, exhaustedUntil: now + 43200000 },
        "u/1/": { credits: 20, updatedAt: now, exhaustedUntil: now + 43200000 },
        "u/2/": { credits: 25, updatedAt: now, exhaustedUntil: now + 43200000 },
        "u/3/": { credits: 50, updatedAt: now, exhaustedUntil: now + 43200000 },
        "u/4/": { credits: 50, updatedAt: now, exhaustedUntil: now + 43200000 },
        "u/5/": { credits: 0, updatedAt: now, exhaustedUntil: now + 43200000 },
        "u/6/": { credits: 50, updatedAt: now, exhaustedUntil: now + 43200000 },
        "u/7/": { credits: 950, email: "hangthumedia@gmail.com", updatedAt: now },
      },
      workerTargets: [{ prefix: "u/7/", projectId: pid, email: "hangthumedia@gmail.com" }],
    }],
    active: "a1",
  };
  fs.writeFileSync(path.join(PRIV, "flow-driver.json"), JSON.stringify(cfg, null, 2), "utf8");
  console.log("ISOLATED PRIVATE PROJECT READY:", pid);
  process.exit(0);
})();
