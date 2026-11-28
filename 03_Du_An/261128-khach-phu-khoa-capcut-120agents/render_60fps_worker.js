const fs = require('fs');
const path = require('path');
const puppeteer = require('C:/AI/full studio/canvas/desktop/node_modules/puppeteer-core');

const PROJ_DIR = 'C:/AI/full studio/projects/khach_phu_khoa_capcut_120agents_261128';
const EDGE_PATH = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';

const htmlFile = process.argv[2] || 'talking_head_stage.html';
const outSubDir = process.argv[3] || 'th_rendered_frames';
const mode = process.argv[4] || '--full';

const audioJson = JSON.parse(fs.readFileSync(path.join(PROJ_DIR, 'assets', 'audio_data.json'), 'utf8'));
const TOTAL_FRAMES = audioJson.total_frames || 1200;

function launchBrowser() {
  return puppeteer.launch({
    executablePath: EDGE_PATH,
    headless: 'new',
    protocolTimeout: 180000,
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
    await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
    await page.goto(htmlUrl, { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 400));

    const testFrames = [
      Math.floor(TOTAL_FRAMES * 0.06),
      Math.floor(TOTAL_FRAMES * 0.32),
      Math.floor(TOTAL_FRAMES * 0.58),
      Math.floor(TOTAL_FRAMES * 0.80)
    ];
    for (const f of testFrames) {
      await page.evaluate(idx => window.renderFrame(idx), f);
      const outFile = path.join(PROJ_DIR, `preview_${outSubDir}_${String(f).padStart(4, '0')}.jpg`);
      await page.screenshot({ path: outFile, type: 'jpeg', quality: 94 });
      console.log('Saved preview:', outFile);
    }
    await browser.close();
    return;
  }

  const WORKERS = 6;
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
      await new Promise(r => setTimeout(r, 350));

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
