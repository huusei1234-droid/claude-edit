import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("D:/AI/full studio/voice-studio/node_modules/.bun/playwright@1.63.0/node_modules/playwright/index.js");

const [bgPath, hookLine, mainLine, outPng] = process.argv.slice(2);

function toDataUri(filePath) {
  const ext = path.extname(filePath).toLowerCase() === ".png" ? "image/png" : "image/jpeg";
  return `data:${ext};base64,` + fs.readFileSync(filePath).toString("base64");
}

function findFont(name) {
  const root = "Z:\\Máy tính khác\\My Computer\\Document HT Media\\TLH\\Edit\\04_Font Chữ TVC & Chữ Gradient";
  if (!fs.existsSync(root)) return "";
  for (const entry of fs.readdirSync(root, { recursive: true })) {
    if (String(entry).toLowerCase().endsWith(name.toLowerCase())) {
      return "data:font/ttf;base64," + fs.readFileSync(path.join(root, String(entry))).toString("base64");
    }
  }
  return "";
}

const fontScript = findFont("DancingScript-Bold.ttf") || findFont("PlayfairDisplay-ExtraBold.ttf");
const fontItalic = findFont("CormorantGaramond-BoldItalic.ttf") || findFont("Lora-Italic.ttf") || fontScript;

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  @font-face { font-family: 'PosterScript'; src: url('${fontScript}') format('truetype'); font-weight: 700; }
  @font-face { font-family: 'PosterItalic'; src: url('${fontItalic}') format('truetype'); font-weight: 700; font-style: italic; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1920px; overflow: hidden; position: relative; background: #1a0f08; }
  .bg { position: absolute; inset: 0; background: url('${toDataUri(bgPath)}') center/cover no-repeat; }
  .mist {
    position: absolute; left: 0; right: 0; top: 620px; height: 560px;
    background: radial-gradient(ellipse 92% 66% at 50% 50%, rgba(18, 10, 4, 0.68), transparent 78%);
  }
  /* TikTok 5% side-crop safe margin (56px = 5.18%), text stretched wide edge-to-edge */
  .title-wrap {
    position: absolute; left: 56px; right: 56px; top: 900px; transform: translateY(-50%);
    text-align: center; display: flex; flex-direction: column; align-items: center; gap: 10px;
  }
  .hook-text {
    width: 100%;
    font-family: 'PosterItalic', Georgia, serif; font-style: italic; font-size: 76px; font-weight: 700; line-height: 1.12;
    color: #fff6dc; text-shadow: 0 4px 18px rgba(0, 0, 0, 0.95), 0 2px 6px rgba(0, 0, 0, 0.9);
  }
  .main-text {
    width: 100%;
    font-family: 'PosterScript', cursive, serif; font-size: ${mainLine.length > 34 ? 124 : mainLine.length > 22 ? 142 : 158}px; font-weight: 700; line-height: 1.06;
    color: #f5c163; text-shadow: 0 8px 28px rgba(0, 0, 0, 0.96), 0 3px 8px rgba(20, 10, 2, 0.96);
    padding: 4px 0;
  }
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="mist"></div>
  <div class="title-wrap">
    ${hookLine ? `<div class="hook-text">${hookLine}</div>` : ""}
    <div class="main-text">${mainLine}</div>
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
await page.screenshot({ path: outPng, type: "png" });
await browser.close();
