import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("D:/AI/full studio/voice-studio/node_modules/.bun/playwright@1.63.0/node_modules/playwright/index.js");

const BRAVE_EXE = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe";
const PROFILE_DIR = "D:\\AI\\full studio\\edit\\.tiktok-brave-profile";
const CANDIDATE_SRC_DIRS = [
  "Z:\\Máy tính khác\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "Z:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu\\đã đăng",
  "Z:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\Video Hoàn thiện\\K4 mẹ ck nàng dâu\\đã đăng",
];
const SRC_DIR = CANDIDATE_SRC_DIRS.find((p) => fs.existsSync(p)) || CANDIDATE_SRC_DIRS[0];
const DST_DIR = path.join(SRC_DIR, "On air Tiktok");
const DEFAULT_TAGS = "#MeChongNangDau #PhimNgan #PhimDrama #DramaGiaDinh #PhimViet";

function parseArgs(argv) {
  const args = { mode: "post", caption: "", file: "", cover: "" };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--login") args.mode = "login";
    else if (a === "--post") args.mode = "post";
    else if (a === "--caption" && argv[i + 1]) args.caption = argv[++i];
    else if (a === "--file" && argv[i + 1]) args.file = argv[++i];
    else if (a === "--cover" && argv[i + 1]) args.cover = argv[++i];
  }
  return args;
}

function makeAutoCover(localVideoPath, titleSource) {
  const pyExe =
    process.env.PYTHON && fs.existsSync(process.env.PYTHON)
      ? process.env.PYTHON
      : "C:\Users\Hang thu\AppData\Local\Programs\Python\Python311\python.exe";
  const out = "D:\AI\full studio\edit\.tmp_tiktok_cover.png";
  execFileSync(
    pyExe,
    ["D:\AI\full studio\edit\make_tiktok_cover.py", localVideoPath, out, titleSource],
    { stdio: "inherit" }
  );
  return out;
}

function pickOldestMp4() {
  if (!fs.existsSync(SRC_DIR)) throw new Error(`Source folder not found: ${SRC_DIR}`);
  const files = fs
    .readdirSync(SRC_DIR, { withFileTypes: true })
    .filter((d) => d.isFile() && d.name.toLowerCase().endsWith(".mp4"))
    .map((d) => {
      const full = path.join(SRC_DIR, d.name);
      const st = fs.statSync(full);
      const isFull = /full/i.test(d.name);
      return { name: d.name, full, mtimeMs: st.mtimeMs, isFull };
    })
    .sort((a, b) => a.mtimeMs - b.mtimeMs);
  const singles = files.filter((f) => !f.isFull);
  return singles[0] || files[0] || null;
}

function fallbackCaption(filename) {
  const base = filename
    .replace(/\.mp4$/i, "")
    .replace(/^\d{6}\s+/, "")
    .trim();
  return `${base} ${DEFAULT_TAGS}`;
}

async function main() {
  const args = parseArgs(process.argv);
  fs.mkdirSync(PROFILE_DIR, { recursive: true });

  let browser = null;
  let context = null;
  let connectedCdp = false;
  try {
    browser = await chromium.connectOverCDP("http://127.0.0.1:19333");
    context = browser.contexts()[0];
    connectedCdp = true;
  } catch {
    context = await chromium.launchPersistentContext(PROFILE_DIR, {
      executablePath: BRAVE_EXE,
      headless: false,
      viewport: { width: 1280, height: 860 },
      args: ["--disable-blink-features=AutomationControlled"],
    });
  }

  const page = context.pages()[0] || (await context.newPage());
  page.on("dialog", async (d) => {
    await d.accept().catch(() => {});
  });
  await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 60000 });
  const leaveBtn = page.locator('button:text-is("Thoát"), button:text-is("Leave")').first();
  if (await leaveBtn.isVisible({ timeout: 1500 }).catch(() => false)) {
    await leaveBtn.click();
    await page.waitForTimeout(1000);
  }

  if (args.mode === "login") {
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
    await context.close();
    return;
  }

  // Check if redirected to login
  await page.waitForTimeout(3000);
  if (page.url().includes("/login")) {
    console.error("AUTH_REQUIRED: Not logged in to TikTok in Brave profile. Run with --login first.");
    await context.close();
    process.exit(2);
  }

  const fileInput = page.locator('input[type="file"]').first();
  await fileInput.waitFor({ state: "attached", timeout: 30000 });

  const picked = args.file
    ? { name: path.basename(args.file), full: args.file }
    : pickOldestMp4();

  if (!picked || !fs.existsSync(picked.full)) {
    console.log("NO_VIDEO: No .mp4 files remaining in source folder.");
    await context.close();
    return;
  }

  const captionText = (args.caption || fallbackCaption(picked.name)).trim();
  const localTemp = path.join("D:\\AI\\full studio\\edit", ".tmp_tiktok_upload.mp4");
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

  // Dismiss any TikTok Studio popup modal or Joyride onboarding tour
  async function dismissModals() {
    for (let i = 0; i < 4; i++) {
      let dismissed = false;
      const modal = page.locator('.TUXModal-overlay[data-transition-status="open"], .TUXModal-overlay').first();
      if (await modal.isVisible({ timeout: 500 }).catch(() => false)) {
        const okBtn = modal.locator('button:has-text("Bật"), button:has-text("Đã hiểu"), button:has-text("Got it"), button:has-text("OK"), button:has-text("Turn on"), button:has-text("Hủy")').first();
        if (await okBtn.isVisible({ timeout: 500 }).catch(() => false)) {
          await okBtn.click();
          await page.waitForTimeout(600);
          dismissed = true;
        }
      }
      const joyride = page.locator('#react-joyride-portal, .react-joyride__overlay').first();
      if (await joyride.isVisible({ timeout: 500 }).catch(() => false)) {
        const skipBtn = page.locator('#react-joyride-portal button:has-text("Bỏ qua"), #react-joyride-portal button:has-text("Đã hiểu"), #react-joyride-portal button:has-text("Skip"), #react-joyride-portal button:has-text("Got it"), #react-joyride-portal button[aria-label="Close"], #react-joyride-portal button[data-action="close"]').first();
        if (await skipBtn.isVisible({ timeout: 500 }).catch(() => false)) {
          await skipBtn.click();
        } else {
          await page.evaluate(() => document.getElementById('react-joyride-portal')?.remove());
        }
        await page.waitForTimeout(600);
        dismissed = true;
      }
      if (!dismissed) break;
    }
  }

  // Wait for caption editor to appear (indicates file accepted & form loaded)
  const editor = page.locator('[contenteditable="true"]').first();
  await editor.waitFor({ state: "visible", timeout: 120000 });
  await page.waitForTimeout(2500);
  await dismissModals();
  await page.evaluate(() => {
    document.querySelectorAll('#react-joyride-portal, .react-joyride__overlay').forEach((el) => el.remove());
  });

  await editor.click({ force: true });
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Backspace");
  await page.keyboard.type(captionText, { delay: 15 });
  await page.waitForTimeout(1000);
  // Dismiss any hashtag autocomplete popup cleanly
  await page.keyboard.press("Escape");

  // Always attach synchronized cover image
  const coverPath = args.cover && fs.existsSync(args.cover) ? args.cover : makeAutoCover(localTemp, captionText || picked.name);
  if (fs.existsSync(coverPath)) {
    const editCoverBtn = page.locator('button:has-text("Sửa ảnh bìa"), div:has-text("Sửa ảnh bìa"), button:has-text("Edit cover"), div:has-text("Edit cover")').last();
    if (await editCoverBtn.isVisible({ timeout: 15000 }).catch(() => false)) {
      await editCoverBtn.click({ force: true });
      const dialog = page.locator('div[role="dialog"]').last();
      await dialog.waitFor({ state: "visible", timeout: 10000 });
      await page.waitForTimeout(800);

      const uploadTab = dialog.locator(':text-is("Tải ảnh bìa lên"), :text-is("Upload cover"), :text("Tải ảnh bìa lên"), :text("Upload cover")').last();
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

      const confirmCoverBtn = dialog.locator('button:has-text("Lưu"), button:has-text("Xác nhận"), button:has-text("Xong"), button:has-text("Save"), button:has-text("Confirm"), button:has-text("Done")').last();
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

  // Wait for upload + checks to finish so the exact Post ("Đăng" / "Post") button is enabled
  const postBtn = page.locator('button[data-e2e="post_video_button"], button:text-is("Đăng"), button:text-is("Post")').last();
  await postBtn.waitFor({ state: "visible", timeout: 60000 });

  const deadline = Date.now() + 600000; // up to 10 min for large files
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
    if (connectedCdp && browser) await browser.close();
    else await context.close();
    process.exit(3);
  }

  await dismissModals();
  await page.evaluate(() => {
    document.querySelectorAll('#react-joyride-portal, .react-joyride__overlay').forEach((el) => el.remove());
  });
  console.log("POST_BTN_TEXT:", (await postBtn.innerText().catch(() => "")).trim());
  await postBtn.click();
  console.log("CLICKED_POST");

  // Handle possible "Đăng ngay" / confirmation modal if TikTok shows one
  const confirmBtn = page.locator('button:has-text("Đăng ngay"), button:has-text("Post now")').first();
  if (await confirmBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await confirmBtn.click();
  }

  // Wait for redirect to /content or success toast
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
  try { fs.unlinkSync(localTemp); } catch {}
  console.log(`POSTED_AND_MOVED: ${dstPath}`);

  await page.waitForTimeout(2000);
  if (connectedCdp && browser) await browser.close();
  else await context.close();
}

main().catch((err) => {
  console.error("ERROR:", err);
  process.exit(1);
});
