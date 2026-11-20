import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("D:/AI/full studio/voice-studio/node_modules/.bun/playwright@1.63.0/node_modules/playwright/index.js");

const args = process.argv.slice(2);
const bgPath = args[0];
let hookLines = [];
let mainLines = [];
let outPng = "";

if (args.length === 3) {
  const parsed = JSON.parse(args[1]);
  hookLines = parsed.hook || [];
  mainLines = parsed.main || [];
  outPng = args[2];
} else {
  if (args[1]) hookLines = [args[1]];
  if (args[2]) mainLines = [args[2]];
  outPng = args[3];
}

function toDataUri(filePath) {
  const ext = path.extname(filePath).toLowerCase() === ".png" ? "image/png" : "image/jpeg";
  return `data:${ext};base64,` + fs.readFileSync(filePath).toString("base64");
}

function findFont(name) {
  const roots = [
    "D:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\fonts_tvc_vi",
    "Z:\\Máy tính khác\\My Computer\\Document HT Media\\TLH\\Edit\\04_Font Chữ TVC & Chữ Gradient",
  ];
  for (const root of roots) {
    if (!fs.existsSync(root)) continue;
    for (const entry of fs.readdirSync(root, { recursive: true })) {
      if (String(entry).toLowerCase().endsWith(name.toLowerCase())) {
        return "data:font/ttf;base64," + fs.readFileSync(path.join(root, String(entry))).toString("base64");
      }
    }
  }
  return "";
}

const fontMain = findFont("AsapCondensed-Black.ttf") || findFont("Montserrat-Black.ttf") || findFont("BeVietnamPro-ExtraBold.ttf");
const fontHook = findFont("AsapCondensed-ExtraBold.ttf") || findFont("BeVietnamPro-ExtraBold.ttf") || fontMain;

function esc(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  @font-face { font-family: 'CoverMain'; src: url('${fontMain}') format('truetype'); font-weight: 900; }
  @font-face { font-family: 'CoverHook'; src: url('${fontHook}') format('truetype'); font-weight: 800; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1920px; overflow: hidden; position: relative; background: #0d0805; }
  .bg { position: absolute; inset: 0; background: url('${toDataUri(bgPath)}') center/cover no-repeat; }
  .shade {
    position: absolute; left: 0; right: 0; top: 820px; bottom: 0;
    background: linear-gradient(
      to bottom,
      rgba(10, 6, 3, 0) 0%,
      rgba(10, 6, 3, 0.44) 26%,
      rgba(8, 5, 2, 0.82) 58%,
      rgba(6, 4, 2, 0.94) 100%
    );
  }
  /* 60px (>5.5%) safe side margin + bottom 305px (inside TikTok 3:4 grid above 240px cut) */
  .title-wrap {
    position: absolute; left: 60px; right: 60px; bottom: 305px;
    display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px;
  }
  .line-row {
    position: relative; display: inline-block; white-space: nowrap;
  }
  .hook-back, .hook-front {
    font-family: 'CoverHook', sans-serif;
    font-size: 92px;
    font-weight: 800;
    line-height: 1.12;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .hook-back {
    color: transparent;
    -webkit-text-stroke: 15px #0b0603;
    paint-order: stroke fill;
    filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.96));
  }
  .hook-front {
    position: absolute; inset: 0;
    color: #ffffff;
  }

  .main-back, .main-front {
    font-family: 'CoverMain', sans-serif;
    font-size: 132px;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .main-back {
    color: transparent;
    -webkit-text-stroke: 19px #0b0603;
    paint-order: stroke fill;
    filter: drop-shadow(0 10px 26px rgba(0, 0, 0, 0.98)) drop-shadow(0 3px 6px rgba(0, 0, 0, 0.95));
  }
  .main-front {
    position: absolute; inset: 0;
    background: linear-gradient(180deg, #fff9c4 0%, #ffe066 28%, #ffc107 58%, #ffdf70 78%, #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="shade"></div>
  <div class="title-wrap">
    ${hookLines
      .map(
        (ln) => `<div class="line-row hook-row">
          <div class="hook-back">${esc(ln)}</div>
          <div class="hook-front">${esc(ln)}</div>
        </div>`
      )
      .join("")}
    ${mainLines
      .map(
        (ln) => `<div class="line-row main-row">
          <div class="main-back">${esc(ln)}</div>
          <div class="main-front">${esc(ln)}</div>
        </div>`
      )
      .join("")}
  </div>
</body>
</html>`;

const browser = await chromium.launch({
  executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.setContent(html, { waitUntil: "load" });
await page.evaluate(() => document.fonts.ready);

// Auto-fit every semantic line so NONE ever wraps and main lines stretch big & bold up to 948px safe width
await page.evaluate(() => {
  const MAX_W = 948;
  const fitGroup = (selector, textSel, minPx, maxPx, targetFill) => {
    const rows = Array.from(document.querySelectorAll(selector));
    if (!rows.length) return;
    // Measure each row at 100px base
    rows.forEach((r) => r.querySelectorAll(textSel).forEach((el) => (el.style.fontSize = "100px")));
    const maxRowW = Math.max(...rows.map((r) => r.getBoundingClientRect().width));
    let px = Math.floor((MAX_W * targetFill * 100) / Math.max(1, maxRowW));
    px = Math.max(minPx, Math.min(maxPx, px));
    rows.forEach((r) =>
      r.querySelectorAll(textSel).forEach((el) => {
        el.style.fontSize = `${px}px`;
        const stroke = Math.max(12, Math.round(px * 0.145));
        if (el.classList.contains("hook-back") || el.classList.contains("main-back")) {
          el.style.webkitTextStroke = `${stroke}px #0b0603`;
        }
      })
    );
  };
  fitGroup(".hook-row", ".hook-back, .hook-front", 64, 102, 0.92);
  fitGroup(".main-row", ".main-back, .main-front", 76, 152, 0.96);
});

await page.screenshot({ path: outPng, type: "png" });
await browser.close();
