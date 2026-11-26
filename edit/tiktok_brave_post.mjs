import fs from "node:fs";
import path from "node:path";
import { execFileSync, spawn } from "node:child_process";
import { createRequire } from "node:module";

import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const EDIT_DIR = path.dirname(fileURLToPath(import.meta.url));
const STUDIO_ROOT = path.resolve(EDIT_DIR, "..");
const PLAYWRIGHT_CANDIDATES = [
  path.join(STUDIO_ROOT, "voice-studio", "node_modules", "playwright", "index.js"),
  "C:/AI/full studio/voice-studio/node_modules/playwright/index.js",
  "D:/AI/full studio/voice-studio/node_modules/.bun/playwright@1.63.0/node_modules/playwright/index.js",
];
const { chromium } = require(PLAYWRIGHT_CANDIDATES.find((p) => fs.existsSync(p)) || PLAYWRIGHT_CANDIDATES[0]);

const BRAVE_CANDIDATES = [
  "C:\\Users\\001\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
  "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
  process.env.LOCALAPPDATA ? path.join(process.env.LOCALAPPDATA, "BraveSoftware\\Brave-Browser\\Application\\brave.exe") : "",
].filter(Boolean);
const BRAVE_EXE = BRAVE_CANDIDATES.find((p) => fs.existsSync(p)) || BRAVE_CANDIDATES[0];

const BRAVE_STUDIO_LNKS = [
  "C:\\Users\\001\\Desktop\\Brave Studio.lnk",
  "C:\\Users\\Hang thu\\Desktop\\Brave Studio.lnk",
];
const BRAVE_STUDIO_LNK = BRAVE_STUDIO_LNKS.find((p) => fs.existsSync(p)) || "";
const FALLBACK_PROFILE_DIR = path.join(EDIT_DIR, ".tiktok-brave-profile");
const STATE_FILE = path.join(EDIT_DIR, "tiktok_last_post_state.json");
const LOCK_FILE = path.join(EDIT_DIR, "tiktok_post_lock.json");

function isPidAlive(pid) {
  if (!pid || typeof pid !== "number") return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

const CANDIDATE_SRC_DIRS = [
  "G:\\Other computers\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "G:\\Máy tính khác\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "G:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "Z:\\Máy tính khác\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "Z:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
];
const SRC_DIR = CANDIDATE_SRC_DIRS.find((p) => fs.existsSync(p)) || CANDIDATE_SRC_DIRS[0];
const DST_DIR = path.join(SRC_DIR, "On air Tiktok");
const DEFAULT_TAGS = "#MeChongNangDau #PhimNgan #PhimDrama #DramaGiaDinh #PhimViet";

function parseArgs(argv) {
  const args = { mode: "post", caption: "", file: "", cover: "", force: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--login") args.mode = "login";
    else if (a === "--post") args.mode = "post";
    else if (a === "--force") args.force = true;
    else if (a === "--caption" && argv[i + 1]) args.caption = argv[++i];
    else if (a === "--file" && argv[i + 1]) args.file = argv[++i];
    else if (a === "--cover" && argv[i + 1]) args.cover = argv[++i];
  }
  return args;
}

function cleanViTitle(raw) {
  let s = raw
    .replace(/\.mp4$/i, "")
    .replace(/^\d{6}\s+/, "")
    .replace(/\(\s*(?:full|\d+)\s*\)/gi, "")
    .replace(/\bfull\b$/i, "")
    .replace(/\bnhà trồng\b/gi, "nhà chồng")
    .replace(/\bchữ hiêu\b/gi, "chữ hiếu")
    .replace(/\btrong nha\b/gi, "trong nhà")
    .replace(/\bkhó thể sao\b/gi, "khó thế sao")
    .replace(/\s+/g, " ")
    .trim();
  if (s.length > 0) s = s[0].toUpperCase() + s.slice(1);
  return s;
}

function fallbackCaption(filename) {
  return `${cleanViTitle(filename)} ${DEFAULT_TAGS}`;
}

function makeAutoCover(localVideoPath, titleSource) {
  const pyCandidates = [
    process.env.PYTHON || "",
    "C:\\Users\\001\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
    "C:\\Users\\Hang thu\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
  ].filter(Boolean);
  const pyExe = pyCandidates.find((p) => fs.existsSync(p)) || "python";
  const out = path.join(EDIT_DIR, "tmp_tiktok_cover.png");
  execFileSync(pyExe, [path.join(EDIT_DIR, "make_tiktok_cover.py"), localVideoPath, out, titleSource], {
    stdio: "inherit",
  });
  return out;
}

function listCandidateMp4s() {
  if (!fs.existsSync(SRC_DIR)) throw new Error(`Source folder not found: ${SRC_DIR}`);
  const files = fs
    .readdirSync(SRC_DIR, { withFileTypes: true })
    .filter((d) => d.isFile() && d.name.toLowerCase().endsWith(".mp4"))
    .map((d) => {
      const full = path.join(SRC_DIR, d.name);
      const st = fs.statSync(full);
      const isFull = /\bfull\b/i.test(d.name);
      return { name: d.name, full, mtimeMs: st.mtimeMs, isFull };
    })
    .sort((a, b) => a.mtimeMs - b.mtimeMs);
  const singles = files.filter((f) => !f.isFull);
  return singles.length > 0 ? [...singles, ...files.filter((f) => f.isFull)] : files;
}

function normalizeForMatch(s) {
  return String(s || "")
    .toLowerCase()
    .replace(/#\S+/g, "")
    .replace(/\.mp4$/i, "")
    .replace(/^\d{6}\s+/, "")
    .replace(/\bnhà trồng\b/g, "nhà chồng")
    .replace(/\btrong nha\b/g, "trong nhà")
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

async function connectMainBraveStudio() {
  // 1. Try existing Brave Studio on port 9333 (shared with Google Flow & ChatGPT HTPM)
  try {
    const browser = await chromium.connectOverCDP("http://127.0.0.1:9333");
    return { browser, context: browser.contexts()[0], usingMain9333: true, spawnedFallback: false };
  } catch {}

  // 2. Launch Brave Studio via explorer.exe so it opens on user's desktop with port 9333
  if (fs.existsSync(BRAVE_STUDIO_LNK)) {
    const launcher = spawn("explorer.exe", [BRAVE_STUDIO_LNK], { detached: true, stdio: "ignore" });
    launcher.unref();
  } else {
    const launcher = spawn(
      BRAVE_EXE,
      [
        "--remote-debugging-port=9333",
        "--remote-debugging-address=127.0.0.1",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--disable-features=CalculateNativeWinOcclusion",
      ],
      { detached: true, stdio: "ignore" }
    );
    launcher.unref();
  }

  for (let i = 0; i < 25; i++) {
    await new Promise((r) => setTimeout(r, 700));
    try {
      const browser = await chromium.connectOverCDP("http://127.0.0.1:9333");
      return { browser, context: browser.contexts()[0], usingMain9333: true, spawnedFallback: false };
    } catch {}
  }

  // 3. Fallback to isolated port 19333 ONLY if unattached Brave blocked port 9333 (never kill user's Brave!)
  fs.mkdirSync(FALLBACK_PROFILE_DIR, { recursive: true });
  const fb = spawn(
    BRAVE_EXE,
    [
      "--remote-debugging-port=19333",
      `--user-data-dir=${FALLBACK_PROFILE_DIR}`,
      "--no-first-run",
      "--no-default-browser-check",
      "--window-size=1280,860",
    ],
    { detached: true, stdio: "ignore" }
  );
  fb.unref();
  for (let i = 0; i < 25; i++) {
    await new Promise((r) => setTimeout(r, 600));
    try {
      const browser = await chromium.connectOverCDP("http://127.0.0.1:19333");
      return { browser, context: browser.contexts()[0], usingMain9333: false, spawnedFallback: true };
    } catch {}
  }
  throw new Error("Could not connect to Brave Studio (:9333) or fallback (:19333).");
}

async function main() {
  const args = parseArgs(process.argv);

  if (args.mode === "post" && !args.force && !args.file) {
    if (fs.existsSync(LOCK_FILE)) {
      try {
        const lk = JSON.parse(fs.readFileSync(LOCK_FILE, "utf8"));
        if (lk.pid && lk.pid !== process.pid && isPidAlive(lk.pid) && Date.now() - (lk.startedAt || 0) < 20 * 60 * 1000) {
          console.log(`SKIPPED_LOCKED: Another TikTok upload (PID ${lk.pid}) is currently in progress.`);
          return;
        }
      } catch {}
    }
    if (fs.existsSync(STATE_FILE)) {
      try {
        const st = JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
        if (st.lastPostedAt && Date.now() - st.lastPostedAt < 35 * 60 * 1000) {
          console.log(`SKIPPED_RECENT_SLOT: Already posted '${st.file}' ${Math.round((Date.now() - st.lastPostedAt) / 60000)}m ago.`);
          return;
        }
      } catch {}
    }
  }

  fs.writeFileSync(LOCK_FILE, JSON.stringify({ pid: process.pid, startedAt: Date.now() }), "utf8");
  let conn = null;
  let page = null;

  try {
    conn = await connectMainBraveStudio();
    const { context, usingMain9333 } = conn;
    console.log("CONNECTED_BRAVE:", usingMain9333 ? "Main Brave Studio (:9333)" : "Fallback Profile (:19333)");

    // Always open a dedicated temporary tab so existing Flow / ChatGPT / TikTok tabs are untouched
    page = await context.newPage();
    page.on("dialog", async (d) => {
      await d.accept().catch(() => {});
    });

    if (args.mode === "login") {
      await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 90000 });
      console.log("WAITING_FOR_LOGIN: Please log in to TikTok in the Brave window...");
      await page.waitForTimeout(3000);
      await page.waitForFunction(
        () => location.hostname.includes("tiktok.com") && !location.pathname.includes("/login"),
        undefined,
        { timeout: 300000 }
      );
      await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 90000 });
      await page.locator('input[type="file"]').first().waitFor({ state: "attached", timeout: 60000 });
      console.log("LOGIN_OK: TikTok Studio upload page is ready.");
      await page.waitForTimeout(2000);
      return;
    }

    // Check /tiktokstudio/content for duplicates before uploading
    let publishedNorms = [];
    if (!args.file) {
      await page.goto("https://www.tiktok.com/tiktokstudio/content", { waitUntil: "domcontentloaded", timeout: 90000 });
      await page.waitForTimeout(4500);
      if (page.url().includes("/login")) {
        console.error("AUTH_REQUIRED: Not logged in to TikTok. Please log in on Brave Studio.");
        process.exitCode = 2;
        return;
      }
      const bodyText = await page.evaluate(() => document.body.innerText || "");
      publishedNorms = bodyText
        .split(/\r?\n/)
        .map((ln) => normalizeForMatch(ln))
        .filter((ln) => ln.length >= 10);
    }

    let picked = null;
    if (args.file) {
      picked = { name: path.basename(args.file), full: args.file };
    } else {
      const candidates = listCandidateMp4s();
      fs.mkdirSync(DST_DIR, { recursive: true });
      for (const cand of candidates) {
        const key = normalizeForMatch(cand.name);
        const alreadyOnChannel =
          key.length >= 10 && publishedNorms.some((p) => p.includes(key) || (key.length >= 18 && p.includes(key.slice(0, 18))));
        if (alreadyOnChannel) {
          const dupDst = path.join(DST_DIR, cand.name);
          fs.renameSync(cand.full, dupDst);
          console.log(`MOVED_ALREADY_POSTED: ${dupDst}`);
          continue;
        }
        picked = cand;
        break;
      }
    }

    if (!picked || !fs.existsSync(picked.full)) {
      console.log("NO_VIDEO: No unposted .mp4 files remaining in source folder.");
      return;
    }

    const captionText = (args.caption || fallbackCaption(picked.name)).trim();
    const localTemp = path.join(EDIT_DIR, "tmp_tiktok_upload.mp4");
    fs.copyFileSync(picked.full, localTemp);
    // Prepare cover BEFORE opening /tiktokstudio/upload so synchronous Drive copy + ffmpeg never stalls the upload page
    const coverPath = args.cover && fs.existsSync(args.cover) ? args.cover : makeAutoCover(localTemp, captionText || picked.name);

    await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 90000 });
    const leaveBtn = page.locator('button:text-is("Thoát"), button:text-is("Leave")').first();
    if (await leaveBtn.isVisible({ timeout: 1500 }).catch(() => false)) {
      await leaveBtn.click();
      await page.waitForTimeout(1000);
    }

    await page.waitForTimeout(3500);
    if (page.url().includes("/login")) {
      console.error("AUTH_REQUIRED: Not logged in to TikTok. Please log in on Brave Studio.");
      process.exitCode = 2;
      return;
    }

    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.waitFor({ state: "attached", timeout: 30000 });
    console.log(`UPLOADING: ${picked.name}`);
    console.log(`CAPTION: ${captionText}`);

    await page.bringToFront().catch(() => {});
    const cdp = await context.newCDPSession(page);
    const { root } = await cdp.send("DOM.getDocument");
    const { nodeId } = await cdp.send("DOM.querySelector", { nodeId: root.nodeId, selector: 'input[type="file"]' });
    await cdp.send("DOM.setFileInputFiles", { files: [localTemp], nodeId });

    async function dismissModals() {
      for (let i = 0; i < 4; i++) {
        let dismissed = false;
        const modal = page.locator('.TUXModal-overlay[data-transition-status="open"], .TUXModal-overlay').first();
        if (await modal.isVisible({ timeout: 500 }).catch(() => false)) {
          const okBtn = modal
            .locator('button:has-text("Bật"), button:has-text("Đã hiểu"), button:has-text("Got it"), button:has-text("OK"), button:has-text("Turn on"), button:has-text("Hủy")')
            .first();
          if (await okBtn.isVisible({ timeout: 500 }).catch(() => false)) {
            await okBtn.click();
            await page.waitForTimeout(600);
            dismissed = true;
          }
        }
        const joyride = page.locator('#react-joyride-portal, .react-joyride__overlay').first();
        if (await joyride.isVisible({ timeout: 500 }).catch(() => false)) {
          const skipBtn = page
            .locator('#react-joyride-portal button:has-text("Bỏ qua"), #react-joyride-portal button:has-text("Đã hiểu"), #react-joyride-portal button:has-text("Skip"), #react-joyride-portal button:has-text("Got it"), #react-joyride-portal button[aria-label="Close"], #react-joyride-portal button[data-action="close"]')
            .first();
          if (await skipBtn.isVisible({ timeout: 500 }).catch(() => false)) {
            await skipBtn.click();
          } else {
            await page.evaluate(() => document.getElementById("react-joyride-portal")?.remove());
          }
          await page.waitForTimeout(600);
          dismissed = true;
        }
        if (!dismissed) break;
      }
    }

    const editor = page.locator('.public-DraftEditor-content, [contenteditable="true"]').first();
    await editor.waitFor({ state: "visible", timeout: 120000 });
    await page.waitForTimeout(2500);
    await dismissModals();
    await page.evaluate(() => {
      document.querySelectorAll("#react-joyride-portal, .react-joyride__overlay").forEach((el) => el.remove());
    });

    await editor.click({ force: true });
    await page.waitForTimeout(300);
    await page.keyboard.press("Control+A");
    await page.keyboard.press("Backspace");
    await page.waitForTimeout(300);
    await page.evaluate((text) => {
      const el = document.querySelector(".public-DraftEditor-content") || document.querySelector('[contenteditable="true"]');
      if (!el) return;
      el.focus();
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(el);
      sel.removeAllRanges();
      sel.addRange(range);
      const dt = new DataTransfer();
      dt.setData("text/plain", text + " ");
      el.dispatchEvent(new ClipboardEvent("paste", { clipboardData: dt, bubbles: true, cancelable: true }));
    }, captionText);
    await page.waitForTimeout(900);
    await page.keyboard.press("Escape");
    console.log("EDITOR_FINAL_TEXT:", (await editor.innerText().catch(() => "")).replace(/\s+/g, " ").trim());

    if (fs.existsSync(coverPath)) {
      const editCoverBtn = page.locator(':text-is("Sửa ảnh bìa"), :text-is("Edit cover")').first();
      if (await editCoverBtn.isVisible({ timeout: 15000 }).catch(() => false)) {
        await editCoverBtn.click({ force: true });
        const dialog = page.locator('div[role="dialog"]').last();
        await dialog.waitFor({ state: "visible", timeout: 10000 });
        await page.waitForTimeout(800);

        const uploadTab = dialog.locator(':text-is("Tải ảnh bìa lên"), :text-is("Upload cover")').last();
        if (await uploadTab.isVisible({ timeout: 5000 }).catch(() => false)) {
          await uploadTab.click({ force: true });
          await page.waitForTimeout(800);
        }

        const dialogInputCount = await dialog.locator('input[type="file"]').count();
        console.log("COVER_DIALOG_INPUTS:", dialogInputCount);
        if (dialogInputCount > 0) {
          const { root: dRoot } = await cdp.send("DOM.getDocument");
          const { nodeIds } = await cdp.send("DOM.querySelectorAll", {
            nodeId: dRoot.nodeId,
            selector: 'div[role="dialog"] input[type="file"]',
          });
          if (nodeIds && nodeIds.length > 0) {
            await cdp.send("DOM.setFileInputFiles", { files: [coverPath], nodeId: nodeIds[nodeIds.length - 1] });
          } else {
            await dialog.locator('input[type="file"]').first().setInputFiles(coverPath);
          }
          await page.waitForTimeout(2200);
        }

        const confirmCoverBtn = dialog
          .locator('button:has-text("Lưu"), button:has-text("Xác nhận"), button:has-text("Xong"), button:has-text("Save"), button:has-text("Confirm"), button:has-text("Done")')
          .last();
        if (await confirmCoverBtn.isVisible({ timeout: 10000 }).catch(() => false)) {
          for (let i = 0; i < 15; i++) {
            if (!(await confirmCoverBtn.isDisabled().catch(() => true))) break;
            await page.waitForTimeout(500);
          }
          await confirmCoverBtn.evaluate((el) => el.click());
          await dialog.waitFor({ state: "hidden", timeout: 10000 }).catch(() => {});
          await page.waitForTimeout(1000);
          console.log("COVER_ATTACHED:", path.basename(coverPath));
        }
      }
    }

    const postBtn = page.locator('button[data-e2e="post_video_button"]').first();
    await postBtn.scrollIntoViewIfNeeded().catch(() => {});
    await postBtn.waitFor({ state: "visible", timeout: 60000 });

    const deadline = Date.now() + 600000;
    while (Date.now() < deadline) {
      const disabled = await postBtn.isDisabled().catch(() => true);
      const ariaDisabled = await postBtn.getAttribute("aria-disabled").catch(() => null);
      const dataLoading = await postBtn.getAttribute("data-loading").catch(() => null);
      if (!disabled && ariaDisabled !== "true" && dataLoading !== "true") break;
      await page.waitForTimeout(2000);
    }

    const stillDisabled = await postBtn.isDisabled().catch(() => true);
    if (stillDisabled) {
      console.error("POST_TIMEOUT: Post button remained disabled.");
      process.exitCode = 3;
      return;
    }

    // Wait 15s for TikTok Studio background copyright & content quality checks to finish cleanly
    await page.waitForTimeout(15000);
    await dismissModals();
    await page.evaluate(() => {
      document.querySelectorAll("#react-joyride-portal, .react-joyride__overlay").forEach((el) => el.remove());
    });
    console.log("POST_BTN_TEXT:", (await postBtn.innerText().catch(() => "")).trim());
    await postBtn.click();
    console.log("CLICKED_POST");

    const confirmBtn = page.locator('button:has-text("Đăng ngay"), button:has-text("Post now")').first();
    if (await confirmBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await confirmBtn.click();
    }

    await page.waitForFunction(
      () =>
        location.href.includes("/content") ||
        document.body.innerText.includes("Đã đăng") ||
        document.body.innerText.includes("Your video has been uploaded") ||
        document.body.innerText.includes("Quản lý bài đăng"),
      undefined,
      { timeout: 60000 }
    );

    fs.mkdirSync(DST_DIR, { recursive: true });
    const dstPath = path.join(DST_DIR, picked.name);
    fs.renameSync(picked.full, dstPath);
    try {
      fs.unlinkSync(localTemp);
    } catch {}
    fs.writeFileSync(
      STATE_FILE,
      JSON.stringify({ lastPostedAt: Date.now(), file: picked.name, iso: new Date().toISOString() }, null, 2),
      "utf8"
    );
    console.log(`POSTED_AND_MOVED: ${dstPath}`);
    await page.waitForTimeout(2500);
  } finally {
    try {
      fs.unlinkSync(LOCK_FILE);
    } catch {}
    // Close ONLY our temporary upload tab; NEVER close user's Main Brave Studio (:9333)!
    if (page) {
      await page.close().catch(() => {});
    }
    if (conn && conn.spawnedFallback && conn.context) {
      try {
        const p0 = conn.context.pages()[0];
        if (p0) {
          const cdp2 = await conn.context.newCDPSession(p0);
          await cdp2.send("Browser.close");
        }
      } catch {}
    }
  }
}

main()
  .then(() => {
    process.exit(process.exitCode || 0);
  })
  .catch((err) => {
    try {
      fs.unlinkSync(LOCK_FILE);
    } catch {}
    console.error("ERROR:", err);
    process.exit(1);
  });
