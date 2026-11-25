/**
 * 1. Download the FULL-RESOLUTION (1K/2K) PNG/JPEG of our just-generated Flow Nano Banana Pro image tile!
 * 2. Run ChatGPT (HTPM Project) with single composite reference board (1024x1536 PNG)!
 */
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "D:\\full studio_data\\infinite-canvas-flow";
const BENCH_DIR = "d:\\AI\\full studio\\projects\\av_htpm_26_posters_v3\\benchmark_3ai";

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

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function downloadFullResLatestFlowImage(outPath) {
  const browser = await flow.ensureBrowser({ visible: true });
  const pages = await browser.pages();
  const page = pages.find((p) => /\/project\//.test(p.url() || ""));
  if (!page) {
    console.log("[Flow2K] No open Flow project page found");
    return false;
  }
  console.log("[Flow2K] Found Flow project page:", page.url());
  const dlDir = fs.mkdtempSync(path.join(os.tmpdir(), "flow-img-2k-"));
  const cdp = await page.target().createCDPSession();
  await cdp.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: dlDir }).catch(async () => {
    const bCdp = await browser.target().createCDPSession();
    await bCdp.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: dlDir }).catch(() => {});
    await bCdp.detach().catch(() => {});
  });

  try {
    await flow.withUiFocusLock(async () => {
      await page.bringToFront().catch(() => {});
      const info = await page.evaluate(async () => {
        const tiles = [...document.querySelectorAll("flow-image-tile, flow-asset-tile, [class*='tile']")].filter(
          (x) => !x.closest(".cdk-overlay-container") && x.querySelector("img")
        );
        const first = tiles[0];
        if (!first) return { err: "no image tile found", html: document.body.innerText.slice(0, 300) };
        const imgSrc = first.querySelector("img")?.src || "";
        // Hover tile to reveal buttons if needed
        first.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
        first.dispatchEvent(new MouseEvent("mouseover", { bubbles: true }));
        await new Promise((r) => setTimeout(r, 350));
        const btns = [...first.querySelectorAll("button")].map((b) => ({
          aria: b.getAttribute("aria-label") || "",
          txt: (b.innerText || "").trim(),
        }));
        const dlDirect = [...first.querySelectorAll("button")].find((b) =>
          /Tải xuống|Download|download/i.test((b.getAttribute("aria-label") || "") + " " + (b.innerText || ""))
        );
        if (dlDirect) {
          dlDirect.click();
          await new Promise((r) => setTimeout(r, 650));
        } else {
          const more = [...first.querySelectorAll("button")].find((b) =>
            /Tuỳ chọn khác|Tùy chọn khác|More options|more_vert/i.test((b.getAttribute("aria-label") || "") + " " + (b.innerText || ""))
          );
          if (more) {
            more.click();
            await new Promise((r) => setTimeout(r, 500));
            const menuDl = [...document.querySelectorAll(".cdk-overlay-container [role=menuitem], .cdk-overlay-container button")]
              .filter((x) => x.getBoundingClientRect().width > 0)
              .find((x) => /Tải xuống|Download/i.test(x.innerText || ""));
            if (menuDl) {
              menuDl.click();
              await new Promise((r) => setTimeout(r, 650));
            }
          }
        }
        const subMenu = [...document.querySelectorAll(".cdk-overlay-container [role=menuitem], .cdk-overlay-container flow-menu-item, .cdk-overlay-container button")]
          .filter((x) => x.getBoundingClientRect().width > 0)
          .map((x) => (x.innerText || "").trim());
        // Prefer 2K or 4K or Original 1K!
        const subEls = [...document.querySelectorAll(".cdk-overlay-container [role=menuitem], .cdk-overlay-container flow-menu-item, .cdk-overlay-container button")].filter(
          (x) => x.getBoundingClientRect().width > 0
        );
        const bestSub =
          subEls.find((x) => /\b2K\b|\b4K\b/i.test(x.innerText || "")) ||
          subEls.find((x) => /1K|gốc|original/i.test(x.innerText || ""));
        if (bestSub) {
          (bestSub.querySelector("button") || bestSub).click();
        }
        return { imgSrc, btns, subMenu, clickedSub: bestSub ? (bestSub.innerText || "").trim() : null };
      });
      console.log("[Flow2K] Tile inspect:", JSON.stringify(info));
    });

    for (let i = 0; i < 40; i++) {
      await sleep(500);
      const files = fs.readdirSync(dlDir);
      const ready = files.filter((n) => !n.endsWith(".crdownload") && !n.endsWith(".tmp"));
      if (ready.length && !files.some((n) => n.endsWith(".crdownload"))) {
        await sleep(300);
        const srcFile = path.join(dlDir, ready[0]);
        fs.copyFileSync(srcFile, outPath);
        console.log(`[Flow2K] Downloaded FULL-RES file (${ready[0]}, ${Math.round(fs.statSync(outPath).size / 1024)} KB) -> ${outPath}`);
        return true;
      }
    }
    console.log("[Flow2K] No file landed in download folder after 20s");
    return false;
  } finally {
    await cdp.detach().catch(() => {});
    try { fs.rmSync(dlDir, { recursive: true, force: true }); } catch {}
  }
}

async function runChatGpt1File() {
  const buf = fs.readFileSync(path.join(BENCH_DIR, "composite_ref_1file.jpg"));
  const singleRef = [{ base64: buf.toString("base64"), mime: "image/jpeg", name: "ref_board.jpg" }];
  const baseJs = fs.readFileSync("d:\\AI\\full studio\\projects\\av_htpm_26_posters_v3\\run_direct_3ai_benchmark.js", "utf8");
  const rawPrompt = baseJs.split("const PROMPT_REF = `")[1].split("`;")[0];
  const prompt = rawPrompt
    .replace(/ref_style_av\.jpg/g, "the left panel of the attached reference board")
    .replace(/ref_dk_box\.jpg/g, "the upper-right product photo in the attached reference board")
    .replace(/ref_ht_logo\.jpg/g, "the lower-right circular Yin-Yang logo in the attached reference board");

  console.log("[ChatGPT 1-file] Starting generation in Project HTPM...");
  const t0 = Date.now();
  const res = await handlers["chatgpt:generate-image"](null, {
    prompt,
    ratio: "2:3",
    count: 1,
    images: singleRef,
    keepChat: false,
    noFallback: true,
  });
  if (res && res.ok && res.data) {
    const out = path.join(BENCH_DIR, "01_chatgpt_1file.png");
    fs.writeFileSync(out, res.data);
    console.log(`[ChatGPT 1-file] SUCCESS in ${Math.round((Date.now() - t0) / 1000)}s -> ${out} (${Math.round(res.data.length / 1024)} KB)`);
    return true;
  }
  console.error("[ChatGPT 1-file] FAILED:", res?.error);
  return false;
}

(async () => {
  const fOk = await downloadFullResLatestFlowImage(path.join(BENCH_DIR, "02_flow_nanobanana_pro_2K.png"));
  const cOk = await runChatGpt1File();
  console.log("DONE ->", { flow2K: fOk, chatgpt1File: cOk });
  process.exit(0);
})();
