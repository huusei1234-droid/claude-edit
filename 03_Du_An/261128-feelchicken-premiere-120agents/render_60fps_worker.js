const fs = require('fs');
const path = require('path');
const puppeteer = require('C:/AI/full studio/canvas/desktop/node_modules/puppeteer-core');

const PROJ_DIR = 'C:/AI/full studio/projects/feel_chicken_premiere_120agents_261128';
const EDGE_PATH = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';

const htmlFile = process.argv[2] || 'premiere_120_agents.html';
const outSubDir = process.argv[3] || 'rendered_frames';
const mode = process.argv[4] || '--full';

const audioJson = JSON.parse(fs.readFileSync(path.join(PROJ_DIR, 'assets', 'audio_data.json'), 'utf8'));
const TOTAL_FRAMES = audioJson.total_frames || 2908;

function launchBrowser() {
  return puppeteer.launch({
    executablePath: EDGE_PATH,
    headless: 'new',
    protocolTimeout: 240000,
    defaultViewport: { width: 1080, height: 1920, deviceScaleFactor: 1 },
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--allow-file-access-from-files',
      '--disable-web-security',
      '--hide-scrollbars',
      '--disable-background-timer-throttling',
      '--disable-renderer-backgrounding',
      '--disable-backgrounding-occluded-windows',
      '--force-color-profile=srgb'
    ]
  });
}

async function run() {
  const outDir = path.join(PROJ_DIR, outSubDir);
  fs.mkdirSync(outDir, { recursive: true });
  const htmlUrl = 'file:///' + path.join(PROJ_DIR, htmlFile).replace(/\\/g, '/');

  if (mode === '--preview') {
    const browser = await launchBrowser();
    const page = (await browser.pages())[0] || await browser.newPage();
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));
    page.on('console', msg => { if (msg.type() === 'error') pageErrors.push(msg.text()); });

    await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
    await page.goto(htmlUrl, { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 450));

    // Preview 5 key moments:
    // f=72 (1.20s: Bub_ThanhOi flying from Photoshop to Premiere Program Monitor!)
    // f=1075 (17.92s: Green Chalkboard 20/11 flying down + Project Bin importing!)
    // f=1572 (26.20s: Rapid-fire 6 Quiz Cards #01..#100 volley flying & stacking!)
    // f=1758 (29.30s: Feast Table 8 Miếng Gà flying down + Lumetri Color Wheels!)
    // f=2675 (44.58s: Kawaii End-Card 38 Nguyễn Đình Chiểu flying down!)
    const testFrames = [72, 1075, 1572, 1758, 2675];
    for (const f of testFrames) {
      await page.evaluate(idx => window.renderFrame(idx), f);
      const outFile = path.join(PROJ_DIR, `preview_fc_${String(f).padStart(4, '0')}.jpg`);
      await page.screenshot({ path: outFile, type: 'jpeg', quality: 94 });
      console.log('Saved preview:', outFile);
    }
    if (pageErrors.length > 0) {
      console.error('PAGE ERRORS:', pageErrors);
      process.exit(2);
    }
    await browser.close();
    return;
  }

  const WORKERS = 8;
  const chunkSize = Math.ceil(TOTAL_FRAMES / WORKERS);
  console.log(`[Render60fps] ${htmlFile} -> ${outSubDir} (${TOTAL_FRAMES} frames across ${WORKERS} Edge instances)...`);
  const t0 = Date.now();

  await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
    const startF = w * chunkSize;
    const endF = Math.min(TOTAL_FRAMES, (w + 1) * chunkSize);
    if (startF >= endF) return;

    const browser = await launchBrowser();
    try {
      const pages = await browser.pages();
      const page = pages.length > 0 ? pages[0] : await browser.newPage();
      await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
      await page.goto(htmlUrl, { waitUntil: 'load' });
      await new Promise(r => setTimeout(r, 380));

      for (let f = startF; f < endF; f++) {
        await page.evaluate(idx => window.renderFrame(idx), f);
        const outPath = path.join(outDir, `frame_${String(f).padStart(4, '0')}.jpg`);
        await page.screenshot({ path: outPath, type: 'jpeg', quality: 95, optimizeForSpeed: true });
      }
      console.log(`  Worker ${w} done [${startF}..${endF - 1}] in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    } finally {
      await browser.close();
    }
  }));

  console.log(`[Render60fps] DONE ${TOTAL_FRAMES} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
