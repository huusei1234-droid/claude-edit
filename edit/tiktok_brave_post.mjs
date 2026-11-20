import fs from "node:fs";
import path from "node:path";
import { execFileSync, spawn } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("D:/AI/full studio/voice-studio/node_modules/.bun/playwright@1.63.0/node_modules/playwright/index.js");

const EDIT_DIR = "D:\\AI\\full studio\\edit";
const BRAVE_EXE = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";
const PROFILE_DIR = path.join(EDIT_DIR, ".tiktok-brave-profile");
const STATE_FILE = path.join(EDIT_DIR, ".last_post_state.json");
const LOCK_FILE = path.join(EDIT_DIR, ".tiktok_post.lock");

const CANDIDATE_SRC_DIRS = [
  "Z:\\Máy tính khác\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "Z:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "Z:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\Video Hoàn thiện\\K4 mẹ ck nàng dâu\\đã đăng",
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
  const pyExe =
    process.env.PYTHON && fs.existsSync(process.env.PYTHON)
      ? process.env.PYTHON
      : "C:\\Users\\Hang thu\\AppData\\Local\\Programs\\Python\\Python311\\python.exe";
  const out = path.join(EDIT_DIR, ".tmp_tiktok_cover.png");
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

async function main() {
  const args = parseArgs(process.argv);
  fs.mkdirSync(PROFILE_DIR, { recursive: true });

  // Prevent duplicate slot execution when both Windows Task Scheduler & Antigravity cron run
  if (args.mode === "post" && !args.force && !args.file) {
    if (fs.existsSync(LOCK_FILE)) {
      const lockAge = Date.now() - fs.statSync(LOCK_FILE).mtimeMs;
      if (lockAge < 20 * 60 * 1000) {
        console.log("SKIPPED_LOCKED: Another TikTok upload is currently in progress.");
        return;
      }
    }
    if (fs.existsSync(STATE_FILE)) {
      try {
        const st = JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
        if (st.lastPostedAt && Date.now() - st.lastPostedAt < 90 * 60 * 1000) {
          console.log(`SKIPPED_RECENT_SLOT: Already posted '${st.file}' ${Math.round((Date.now() - st.lastPostedAt) / 60000)}m ago.`);
          return;
        }
      } catch {}
    }
  }

  fs.writeFileSync(LOCK_FILE, String(Date.now()), "utf8");
  let browser = null;
  let context = null;
  let connectedCdp = false;
  let spawnedBrave = null;
  let page = null;

  try {
    try {
      browser = await chromium.connectOverCDP("http://127.0.0.1:19333");
      context = browser.contexts()[0];
      connectedCdp = true;
    } catch {
      // Spawn genuine native Brave without Playwright's --enable-automation flags
      spawnedBrave = spawn(
        BRAVE_EXE,
        [
          "--remote-debugging-port=19333",
          `--user-data-dir=${PROFILE_DIR}`,
          "--no-first-run",
          "--no-default-browser-check",
          "--window-size=1280,860",
        ],
        { detached: true, stdio: "ignore" }
      );
      spawnedBrave.unref();
      for (let retry = 0; retry < 25; retry++) {
        await new Promise((r) => setTimeout(r, 600));
        try {
          browser = await chromium.connectOverCDP("http://127.0.0.1:19333");
          context = browser.contexts()[0];
          connectedCdp = true;
          break;
        } catch {}
      }
      if (!connectedCdp) {
        context = await chromium.launchPersistentContext(PROFILE_DIR, {
          executablePath: BRAVE_EXE,
          headless: false,
          viewport: { width: 1280, height: 860 },
          ignoreDefaultArgs: ["--enable-automation"],
          args: ["--disable-blink-features=AutomationControlled"],
        });
      }
    }

    page = context.pages()[0] || (await context.newPage());
    page.on("dialog", async (d) => {
      await d.accept().catch(() => {});
    });

    if (args.mode === "login") {
      await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 60000 });
      console.log("WAITING_FOR_LOGIN: Please log in to TikTok in the Brave window that just opened...");
      await page.waitForTimeout(3000);
      await page.waitForFunction(
        () => location.hostname.includes("tiktok.com") && !location.pathname.includes("/login"),
        undefined,
        { timeout: 300000 }
      );
      await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.locator('input[type="file"]').first().waitFor({ state: "attached", timeout: 60000 });
      console.log("LOGIN_OK: TikTok Studio upload page is ready.");
      await page.waitForTimeout(3000);
      return;
    }

    // Quick duplicate check on /tiktokstudio/content when picking automatically
    let publishedNorms = [];
    if (!args.file) {
      await page.goto("https://www.tiktok.com/tiktokstudio/content", { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(4500);
      if (page.url().includes("/login")) {
        console.error("AUTH_REQUIRED: Not logged in to TikTok in Brave profile. Run with --login first.");
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

    await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 60000 });
    const leaveBtn = page.locator('button:text-is("Thoát"), button:text-is("Leave")').first();
    if (await leaveBtn.isVisible({ timeout: 1500 }).catch(() => false)) {
      await leaveBtn.click();
      await page.waitForTimeout(1000);
    }

    await page.waitForTimeout(3000);
    if (page.url().includes("/login")) {
      console.error("AUTH_REQUIRED: Not logged in to TikTok in Brave profile. Run with --login first.");
      process.exitCode = 2;
      return;
    }

    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.waitFor({ state: "attached", timeout: 30000 });

    const captionText = (args.caption || fallbackCaption(picked.name)).trim();
    const localTemp = path.join(EDIT_DIR, ".tmp_tiktok_upload.mp4");
    fs.copyFileSync(picked.full, localTemp);
    console.log(`UPLOADING: ${picked.name}`);
    console.log(`CAPTION: ${captionText}`);

    if (connectedCdp) {
      const cdp = await context.newCDPSession(page);
      const { root } = await cdp.send("DOM.getDocument");
      const { nodeId } = await cdp.send("DOM.querySelector", { nodeId: root.nodeId, selector: 'input[type="file"]' });
      await cdp.send("DOM.setFileInputFiles", { files: [localTemp], nodeId });
    } else {
      await fileInput.setInputFiles(localTemp);
    }

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

    const editor = page.locator('[contenteditable="true"]').first();
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
    await page.waitForTimeout(200);
    await page.keyboard.insertText(captionText + " ");
    await page.waitForTimeout(800);
    await page.keyboard.press("Escape");
    console.log("EDITOR_FINAL_TEXT:", (await editor.innerText().catch(() => "")).replace(/\s+/g, " ").trim());

    // Always attach synchronized phrase-safe single-frame cover image
    const coverPath = args.cover && fs.existsSync(args.cover) ? args.cover : makeAutoCover(localTemp, captionText || picked.name);
    if (fs.existsSync(coverPath)) {
      const editCoverBtn = page
        .locator('button:has-text("Sửa ảnh bìa"), div:has-text("Sửa ảnh bìa"), button:has-text("Edit cover"), div:has-text("Edit cover")')
        .last();
      if (await editCoverBtn.isVisible({ timeout: 15000 }).catch(() => false)) {
        await editCoverBtn.click({ force: true });
        const dialog = page.locator('div[role="dialog"]').last();
        await dialog.waitFor({ state: "visible", timeout: 10000 });
        await page.waitForTimeout(800);

        const uploadTab = dialog
          .locator(':text-is("Tải ảnh bìa lên"), :text-is("Upload cover"), :text("Tải ảnh bìa lên"), :text("Upload cover")')
          .last();
        if (await uploadTab.isVisible({ timeout: 5000 }).catch(() => false)) {
          await uploadTab.click({ force: true });
          await page.waitForTimeout(800);
        }

        const dialogInput = dialog.locator('input[type="file"]').first();
        const hasDialogInput = (await dialogInput.count()) > 0;
        console.log("COVER_DIALOG_INPUTS:", await dialog.locator('input[type="file"]').count());
        if (hasDialogInput) {
          await dialogInput.setInputFiles(coverPath);
          await page.waitForTimeout(2000);
        }

        const confirmCoverBtn = dialog
          .locator('button:has-text("Lưu"), button:has-text("Xác nhận"), button:has-text("Xong"), button:has-text("Save"), button:has-text("Confirm"), button:has-text("Done")')
          .last();
        if (await confirmCoverBtn.isVisible({ timeout: 10000 }).catch(() => false)) {
          for (let i = 0; i < 15; i++) {
            if (!(await confirmCoverBtn.isDisabled().catch(() => true))) break;
            await page.waitForTimeout(500);
          }
          await confirmCoverBtn.click({ force: true });
          await dialog.waitFor({ state: "hidden", timeout: 10000 }).catch(() => {});
          await page.waitForTimeout(1000);
          console.log("COVER_ATTACHED:", path.basename(coverPath));
        }
      }
    }

    const postBtn = page.locator('button[data-e2e="post_video_button"], button:text-is("Đăng"), button:text-is("Post")').last();
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
    await page.waitForTimeout(3000);
  } finally {
    try {
      fs.unlinkSync(LOCK_FILE);
    } catch {}
    if (connectedCdp && browser) {
      if (spawnedBrave && page) {
        try {
          const cdp = await context.newCDPSession(page);
          await cdp.send("Browser.close");
        } catch {}
      }
      await browser.close().catch(() => {});
    } else if (context) {
      await context.close().catch(() => {});
    }
  }
}

main().catch((err) => {
  try {
    fs.unlinkSync(LOCK_FILE);
  } catch {}
  console.error("ERROR:", err);
  process.exit(1);
});
