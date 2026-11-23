const path = require("node:path");
const Module = require("node:module");
const origLoad = Module._load;
Module._load = function (req, parent, isMain) {
  if (req === "electron") {
    return { ipcMain: { handle: () => {} }, dialog: { showErrorBox: () => {} } };
  }
  return origLoad.apply(this, arguments);
};
const flow = require("d:\\AI\\full studio\\canvas\\desktop\\flow-driver.js");
(async () => {
  const b = await flow.ensureBrowser({ visible: true });
  const pages = await b.pages();
  for (const p of pages) {
    if (/chatgpt\.com/i.test(p.url())) {
      const snap = await p.evaluate(() => ({
        url: location.href,
        title: document.title,
        text: (document.body?.innerText || "").slice(0, 600),
        editors: [...document.querySelectorAll("#prompt-textarea, div.ProseMirror, textarea, [contenteditable='true']")].map((e) => ({
          tag: e.tagName,
          id: e.id,
          w: e.getBoundingClientRect().width,
        })),
        projects: [...document.querySelectorAll("[data-app-action-sidebar-project-id], a")].filter((el) =>
          el.hasAttribute("data-app-action-sidebar-project-id") || /\/g\/g-p-/i.test(el.href || "")
        ).map((el) => ({
          id: el.getAttribute("data-app-action-sidebar-project-id") || el.href,
          label: el.getAttribute("data-app-action-sidebar-project-label") || (el.innerText || "").trim(),
        })),
      })).catch((e) => ({ err: String(e) }));
      console.log("CHATGPT SNAP:", JSON.stringify(snap, null, 2));
    }
  }
  flow.destroy();
  process.exit(0);
})();
