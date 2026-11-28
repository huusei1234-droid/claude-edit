const fs = require('fs');
const path = require('path');
const puppeteer = require('C:/AI/full studio/canvas/desktop/node_modules/puppeteer-core');

const PROJ_DIR = 'C:/AI/full studio/projects/htpm_ai_swarm_auto_edit_261127';
const EDGE_PATH = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const TOTAL_FRAMES = 1281; // 21.35s @ 60fps (Lush 84-Agent Live Voice-Follow Throw Edit)

const audioJsonPath = path.join(PROJ_DIR, 'assets', 'audio_data.json');
const audioInlinePath = path.join(PROJ_DIR, 'assets', 'audio_data_inline.js');
if (fs.existsSync(audioJsonPath)) {
  const raw = fs.readFileSync(audioJsonPath, 'utf8');
  fs.writeFileSync(audioInlinePath, `window.AUDIO_DATA = ${raw};\n`, 'utf8');
}

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
  const mode = process.argv[2] || '--preview';
  const outDir = path.join(PROJ_DIR, 'rendered_frames');
  fs.mkdirSync(outDir, { recursive: true });
  const htmlUrl = 'file:///' + path.join(PROJ_DIR, 'index_v4.html').replace(/\\/g, '/');

  if (mode === '--preview') {
    const browser = await launchBrowser();
    const page = (await browser.pages())[0] || await browser.newPage();
    await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
    await page.goto(htmlUrl, { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 350));

    for (const f of [22, 198, 446, 876]) {
      await page.evaluate(idx => window.renderFrame(idx), f);
      const outFile = path.join(PROJ_DIR, `qc_frame_${String(f).padStart(4, '0')}.jpg`);
      await page.screenshot({ path: outFile, type: 'jpeg', quality: 94 });
      console.log('Saved preview:', outFile);
    }
    await browser.close();
    return;
  }

  // Launch 6 independent Headless Edge processes (1 active foreground tab each => zero compositor throttling!)
  const WORKERS = 6;
  const chunkSize = Math.ceil(TOTAL_FRAMES / WORKERS);
  console.log(`Starting ${WORKERS} independent Edge processes for ${TOTAL_FRAMES} frames...`);
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
      await new Promise(r => setTimeout(r, 300));

      for (let f = startF; f < endF; f++) {
        await page.evaluate(idx => window.renderFrame(idx), f);
        const outPath = path.join(outDir, `frame_${String(f).padStart(4, '0')}.jpg`);
        await page.screenshot({ path: outPath, type: 'jpeg', quality: 95, optimizeForSpeed: true });
      }
      console.log(`Worker ${w} finished [${startF}..${endF - 1}] in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    } finally {
      await browser.close();
    }
  }));

  console.log(`ALL ${TOTAL_FRAMES} frames rendered in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
