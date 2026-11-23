// Điều khiển Google Flow bằng Brave/Chrome/Edge THẬT (profile riêng, đăng nhập một lần) qua cổng debug.
// Google chặn đăng nhập trong cửa sổ Electron nên không dùng được BrowserWindow.
// Không dùng FlowKit/Python/extension: main process nạp flow-page-driver.js vào trang Flow,
// điền prompt/ảnh/cài đặt, bấm tạo, đợi video rồi tải về cho canvas.
const { ipcMain, dialog } = require("electron");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const DEBUG_PORT = 9333;
const HOME = "https://flow.google.com/";
const BROWSERS = [
  process.env.FLOW_BROWSER,
  path.join(process.env.LOCALAPPDATA || "", "BraveSoftware/Brave-Browser/Application/brave.exe"),
  "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
  "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe",
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  path.join(process.env.LOCALAPPDATA || "", "Google/Chrome/Application/chrome.exe"),
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
].filter(Boolean);

let userData = "";
let configPath = "";
// Nhiều tài khoản Google: mỗi tài khoản có profile trình duyệt riêng (đăng nhập riêng) và project Flow riêng.
// store = { accounts: [{ id, name, profile, projectId }], active: id }
let store = { accounts: [], active: "" };
let onChange = () => {};
const acct = () => store.accounts.find((a) => a.id === store.active) || store.accounts[0];
// config.projectId luôn là project của tài khoản đang dùng
const config = {
  get projectId() { return acct()?.projectId || ""; },
  set projectId(v) { if (acct()) acct().projectId = v; },
  get userPrefix() { return acct()?.userPrefix || ""; },
  set userPrefix(v) { if (acct()) acct().userPrefix = v || ""; },
};
const homeOf = () => `${HOME}${config.userPrefix}`;
let child = null;
let browser = null; // puppeteer Browser
let queue = Promise.resolve();
let pageDriverSrc = "";

// Khóa nhường tiêu điểm giao diện (UI Focus Mutex) dùng chung giữa Tab Google Flow & Tab ChatGPT
// trên CÙNG 1 cửa sổ trình duyệt Brave (cổng 9333), đảm bảo 2 tab không tranh chuột khi bấm nút Tạo/Gửi (~3s),
// còn trong suốt thời gian chờ AI kết xuất (40-90s) cả 2 tab vẫn chạy ngầm song song 100%!
let uiFocusChain = Promise.resolve();
function withUiFocusLock(fn) {
  const next = uiFocusChain.then(fn, fn);
  uiFocusChain = next.catch(() => {});
  return next;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const isMainBraveProfile = (p) => !p || p === "MAIN_BRAVE" || p === "default";

const loadConfig = () => {
  let raw = {};
  try { raw = JSON.parse(fs.readFileSync(configPath, "utf8")); } catch {}
  if (Array.isArray(raw.accounts) && raw.accounts.length) store = { accounts: raw.accounts, active: raw.active, minCredits: raw.minCredits };
  else store = { accounts: [{ id: "a1", name: "Brave Chính (Đồng bộ)", profile: "MAIN_BRAVE", projectId: raw.projectId || "" }], active: "a1", minCredits: raw.minCredits };
  if (!acct() || acct().id !== store.active) store.active = store.accounts[0].id;
};
const saveConfig = () => { try { fs.writeFileSync(configPath, JSON.stringify(store, null, 2)); } catch {} };

async function debugAlive() {
  try { const r = await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/version`, { signal: AbortSignal.timeout(1500) }); return r.ok ? await r.json() : null; } catch { return null; }
}

// Trình duyệt do app mở là cửa sổ thật (profile riêng đã đăng nhập). Chế độ headless bị Flow từ chối nên không dùng mặc định.
let mode = null; // "headless" | "visible" | null (trình duyệt không do app mở)
let browserAccount = null; // tài khoản của trình duyệt do app mở

async function stopOwnBrowser() {
  if (isMainBraveProfile(acct()?.profile)) {
    // Đang đồng bộ trực tiếp trên Brave chính của người dùng -> chỉ ngắt kết nối điều khiển, TUYỆT ĐỐI không đóng trình duyệt chính!
    try { browser?.disconnect(); } catch {}
    browser = null;
    child = null;
    mode = null;
    return;
  }
  try { await browser?.close(); } catch {}
  browser = null;
  if (child) { try { child.kill(); } catch {} child = null; }
  for (let i = 0; i < 20 && (await debugAlive()); i++) await sleep(300);
  mode = null;
}

async function gracefullyCloseUnattachedMainBrave() {
  if (process.platform !== "win32") return;
  await new Promise((resolve) => {
    const ps = spawn("powershell.exe", [
      "-NoProfile",
      "-Command",
      "Get-CimInstance Win32_Process -Filter \"Name='brave.exe'\" | Where-Object { $_.CommandLine -notmatch '--type=' -and $_.CommandLine -notmatch '--user-data-dir=' } | ForEach-Object { taskkill /PID $_.ProcessId | Out-Null }",
    ], { windowsHide: true, stdio: "ignore" });
    ps.on("exit", resolve);
    ps.on("error", resolve);
  });
  for (let i = 0; i < 15; i++) {
    await sleep(350);
    const stillOpen = await new Promise((resolve) => {
      let out = "";
      const ps = spawn("powershell.exe", [
        "-NoProfile",
        "-Command",
        "(Get-CimInstance Win32_Process -Filter \"Name='brave.exe'\" | Where-Object { $_.CommandLine -notmatch '--type=' -and $_.CommandLine -notmatch '--user-data-dir=' } | Measure-Object).Count",
      ], { windowsHide: true });
      ps.stdout.on("data", (d) => { out += d; });
      ps.on("exit", () => resolve(Number(out.trim()) > 0));
      ps.on("error", () => resolve(false));
    });
    if (!stillOpen) break;
  }
}

async function launchBrowser(visible) {
  const exe = BROWSERS.find((p) => fs.existsSync(p));
  if (!exe) throw new Error("Không tìm thấy Brave/Chrome/Edge. Cài một trình duyệt Chromium hoặc đặt biến FLOW_BROWSER trỏ tới chrome.exe.");
  const useMain = isMainBraveProfile(acct().profile);
  if (useMain) visible = true; // Không bao giờ chạy ẩn trên Brave chính của người dùng
  const profile = useMain ? "" : path.join(userData, acct().profile);
  browserAccount = acct().id;
  if (profile) fs.mkdirSync(profile, { recursive: true });
  const start = config.projectId ? `${homeOf()}project/${config.projectId}` : homeOf();
  const gptHtpm = "https://chatgpt.com/g/g-p-6afbde0b943481919c6ec31a3b4f8642/project";

  const buildArgs = (restoreSession) => [
    `--remote-debugging-port=${DEBUG_PORT}`,
    "--remote-debugging-address=127.0.0.1",
    ...(profile ? [`--user-data-dir=${profile}`] : []),
    "--no-first-run",
    "--no-default-browser-check",
    ...(useMain ? [] : ["--window-position=120,70", "--window-size=1280,860"]),
    ...(restoreSession ? ["--restore-last-session"] : []),
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-features=CalculateNativeWinOcclusion",
    ...(visible ? [] : ["--headless=new", "--disable-gpu", "--mute-audio"]),
    start,
    ...(visible ? [gptHtpm] : []),
  ];

  const spawnOnce = (restoreSession) => {
    child = spawn(exe, buildArgs(restoreSession), { detached: Boolean(visible), stdio: "ignore" });
    if (visible && child.unref) child.unref();
    const me = child;
    me.on("exit", () => { if (child === me) { child = null; browser = null; mode = null; } });
    mode = visible ? "visible" : "headless";
    return me;
  };

  const isHiddenShell = Boolean(process.env.ANTIGRAVITY_AGENT || process.env.CLAUDECODE);
  let me = spawnOnce(false);
  let info = null;
  for (let i = 0; i < 40 && !(info = await debugAlive()); i++) {
    await sleep(500);
    // Nếu Brave chính đang mở sẵn từ trước mà chưa gắn cổng 9333 -> chỉ đóng êm & bật lại khi chạy từ giao diện thật của người dùng (Full Studio),
    // TUYỆT ĐỐI không chạy từ shell ẩn của AI để tránh kéo cửa sổ Brave vào màn hình ẩn!
    if (useMain && i >= 4 && me.exitCode !== null) {
      if (isHiddenShell) {
        throw new Error("Brave chính chưa mở cổng đồng bộ 9333. Hãy nháy đúp 'Brave Studio' ngoài màn hình nền (hoặc gọi qua Infinite Canvas :17371) để giữ cửa sổ hiển thị thật.");
      }
      console.log("[flow] Brave chính đang mở ở chế độ thường -> tự động khởi động lại êm (khôi phục nguyên các tab) để gắn cổng đồng bộ 9333...");
      await gracefullyCloseUnattachedMainBrave();
      me = spawnOnce(true);
      break;
    }
  }
  if (!info) {
    for (let i = 0; i < 40 && !(info = await debugAlive()); i++) await sleep(500);
  }
  if (!info) throw new Error("Không mở được trình duyệt Brave chính ở cổng kết nối " + DEBUG_PORT + ".");
  return info;
}

async function ensureBrowser({ visible = true } = {}) {
  if (child && browserAccount && browserAccount !== acct().id) await stopOwnBrowser(); // đã đổi tài khoản: mở trình duyệt với profile của tài khoản đó
  // Flow từ chối trình duyệt ẩn (coi là hoạt động bất thường) → luôn dùng cửa sổ thật; bạn có thể thu nhỏ nó.
  if (visible && mode === "headless") await stopOwnBrowser(); // đổi sang cửa sổ thật để đăng nhập
  if (browser && browser.connected) return browser;
  let info = await debugAlive();
  if (!info) info = await launchBrowser(visible);
  const mod = await import("puppeteer-core"); // ES Module: không dùng được require()
  const puppeteer = mod.default && mod.default.connect ? mod.default : mod;
  browser = await puppeteer.connect({ browserWSEndpoint: info.webSocketDebuggerUrl, defaultViewport: null });
  browser.on("disconnected", () => { browser = null; });
  // nhớ project chính khi chưa cấu hình cụm workerProjectIds / workerTargets đa dự án
  browser.on("targetchanged", (t) => {
    const id = projectOf(t.url());
    const hasPool = (Array.isArray(acct()?.workerProjectIds) && acct().workerProjectIds.length > 0) ||
      (Array.isArray(acct()?.workerTargets) && acct().workerTargets.length > 0);
    if (id && !hasPool && (id !== config.projectId || userPrefixOf(t.url()) !== config.userPrefix)) {
      config.projectId = id;
      config.userPrefix = userPrefixOf(t.url());
      saveConfig();
    }
  });
  return browser;
}

// Mở Tab mới ngầm 100% qua CDP (background: true) để TUYỆT ĐỐI không cướp tiêu điểm chuột của Tab đang bấm nút Tạo/Gửi!
async function createBackgroundPage(b, url = "about:blank") {
  try {
    const cdp = await b.target().createCDPSession();
    let targetId = null;
    try {
      const res = await cdp.send("Target.createTarget", { url: url || "about:blank", background: true });
      targetId = res && res.targetId;
    } finally {
      await cdp.detach().catch(() => {});
    }
    if (targetId) {
      for (let i = 0; i < 35; i++) {
        const pages = await b.pages();
        const found = pages.find((p) => {
          try {
            return p.target()._targetId === targetId ||
              (typeof p.target()._getTargetInfo === "function" && p.target()._getTargetInfo()?.targetId === targetId);
          } catch { return false; }
        });
        if (found) return found;
        const tgt = b.targets().find((t) => t._targetId === targetId || (url !== "about:blank" && t.url() === url));
        if (tgt) {
          const p = await tgt.page().catch(() => null);
          if (p) return p;
        }
        await sleep(100);
      }
    }
  } catch {}
  return await withUiFocusLock(async () => {
    const p = await b.newPage();
    if (url && url !== "about:blank") await p.goto(url, { waitUntil: "domcontentloaded" }).catch(() => {});
    return p;
  });
}

const uaFixed = new WeakSet();
async function fixHeadlessUA(page) {
  if (mode !== "headless" || uaFixed.has(page)) return;
  uaFixed.add(page);
  try { await page.setUserAgent((await page.browser().userAgent()).replace("HeadlessChrome", "Chrome")); } catch {}
}

const projectOf = (url) => (String(url).match(/flow\.google\.com\/(?:u\/\d+\/)?project\/([0-9a-f-]{36})/) || [])[1];
const userPrefixOf = (url) => (String(url).match(/flow\.google\.com\/(u\/\d+\/)/) || [])[1] || "";

async function flowPage(create, opts) {
  const b = await ensureBrowser(opts);
  const pages = await b.pages();
  const flowTabs = pages.filter((p) => /flow\.google\.com/.test(p.url()));
  let page = flowTabs.find((p) => projectOf(p.url()) && (!config.projectId || projectOf(p.url()) === config.projectId))
    || flowTabs[0];
  // TUYỆT ĐỐI không đóng các Tab Worker đang chạy song song (u/0, u/1, u/3) khi kiểm tra trạng thái (flow:status)!
  if (!page && create) {
    const startUrl = config.projectId ? `${homeOf()}project/${config.projectId}` : homeOf();
    page = await createBackgroundPage(b, startUrl);
    await fixHeadlessUA(page);
  }
  if (page) await fixHeadlessUA(page);
  const hasPool = (Array.isArray(acct()?.workerProjectIds) && acct().workerProjectIds.length > 0) ||
    (Array.isArray(acct()?.workerTargets) && acct().workerTargets.length > 0);
  const id = page && projectOf(page.url());
  if (id && !hasPool && (id !== config.projectId || userPrefixOf(page.url()) !== config.userPrefix)) {
    config.projectId = id;
    config.userPrefix = userPrefixOf(page.url());
    saveConfig();
  }
  return page || null;
}

async function ensureWindowOnScreen(page) {
  if (!page) return;
  try {
    const cdp = await page.target().createCDPSession();
    try {
      const w = await cdp.send("Browser.getWindowForTarget");
      const bd = w.bounds || {};
      if (bd.windowState === "minimized") {
        await cdp.send("Browser.setWindowBounds", { windowId: w.windowId, bounds: { windowState: "normal" } });
      }
      if (typeof bd.left === "number" && (bd.left > 1900 || bd.left < -200 || bd.top < -100 || bd.top > 1300)) {
        await cdp.send("Browser.setWindowBounds", {
          windowId: w.windowId,
          bounds: { left: 120, top: 70, width: 1280, height: 860, windowState: "normal" },
        });
      }
    } finally {
      await cdp.detach().catch(() => {});
    }
  } catch {}
}

// mở cửa sổ thật (để đăng nhập Google / chọn project)
async function show() {
  const page = await flowPage(true, { visible: true });
  await ensureWindowOnScreen(page);
  await page.bringToFront();
  return true;
}

async function ensureProjectPage() {
  let page = await flowPage(false);
  if (!config.projectId && !(page && projectOf(page.url()))) {
    await show().catch(() => {});
    throw new Error("Chưa chọn project Flow: trong cửa sổ Chrome vừa mở, đăng nhập Google rồi mở một project, sau đó tạo lại.");
  }
  if (!page) page = await flowPage(true);
  const target = `${homeOf()}project/${config.projectId}`;
  if (!page.url().startsWith(target) || /\/edit\//.test(page.url())) await page.goto(target, { waitUntil: "domcontentloaded" }).catch(() => {});
  for (let i = 0; i < 60; i++) {
    if (/accounts\.google\.com/.test(page.url())) { await show().catch(() => {}); throw new Error("Cần đăng nhập Google trong cửa sổ trình duyệt vừa hiện ra, rồi tạo lại."); }
    if (await page.evaluate(`!!document.querySelector('.ProseMirror')`).catch(() => false)) return page;
    await sleep(500);
  }
  await show().catch(() => {});
  throw new Error("Trang Flow không có ô nhập prompt (kiểm tra project/đăng nhập trong cửa sổ trình duyệt vừa hiện ra).");
}

async function inject(page) {
  pageDriverSrc = fs.readFileSync(path.join(__dirname, "flow-page-driver.js"), "utf8"); // đọc lại mỗi lần: sửa driver không cần mở lại app
  await page.evaluate(pageDriverSrc);
}

// link video là flow.google.com/asb/... cần cookie phiên; fetch trong trang bị chặn nên tải từ Node kèm cookie của trình duyệt
async function downloadVideo(page, url) {
  const cookies = await page.cookies(url);
  const res = await fetch(url, {
    headers: { Cookie: cookies.map((c) => `${c.name}=${c.value}`).join("; "), Referer: HOME, "User-Agent": await page.browser().userAgent() },
  });
  if (!res.ok) throw new Error("Tải video thất bại: HTTP " + res.status);
  return { data: Buffer.from(await res.arrayBuffer()), mime: res.headers.get("content-type") || "video/mp4" };
}

// Tải ảnh độ phân giải cao (2K Upscaled hoặc 1K Original) trực tiếp từ menu "Tuỳ chọn khác -> Tải xuống" của <flow-image-tile>
// thay vì chỉ lấy ảnh thu nhỏ =s512-rw (384x512) trên lưới!
async function downloadImageViaUi(page, key, baseline = [], prefer2K = true, fallbackUrl = "") {
  const dir = fs.mkdtempSync(path.join(require("node:os").tmpdir(), "flow-imgdl-"));
  const cdp = await page.target().createCDPSession();
  let bCdp = null;
  await cdp.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: dir }).catch(() => {});
  try {
    bCdp = await page.browser().target().createCDPSession();
    await bCdp.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: dir, eventsEnabled: true }).catch(() => {});
  } catch {}

  const waitImgFile = async (loops) => {
    for (let i = 0; i < loops; i++) {
      await sleep(500);
      const all = fs.readdirSync(dir);
      const ready = all.filter((n) => !n.endsWith(".crdownload") && !n.endsWith(".tmp"));
      if (ready.length && !all.some((n) => n.endsWith(".crdownload"))) {
        await sleep(300);
        const fpath = path.join(dir, ready[0]);
        const ext = path.extname(ready[0]).toLowerCase();
        const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
        return { data: fs.readFileSync(fpath), mime };
      }
    }
    return null;
  };

  const triggerTileDownload = async (want2K) => {
    return await withUiFocusLock(async () => {
      await page.bringToFront().catch(() => {});
      await page.keyboard.press("Escape").catch(() => {});
      await sleep(250);
      return await page.evaluate(
        async ({ targetKey, baseList, use2K }) => {
          const kOf = (el) => String(el.querySelector("img")?.src || "").split("?")[0];
          const tiles = [...document.querySelectorAll("flow-image-tile")].filter(
            (x) => !x.closest(".cdk-overlay-container") && kOf(x)
          );
          const t =
            tiles.find((x) => kOf(x) === targetKey) ||
            tiles.find((x) => !baseList.includes(kOf(x))) ||
            tiles[0];
          if (!t) return null;
          const more = [...t.querySelectorAll("button")].find((b) =>
            /Tuỳ chọn khác|Tùy chọn khác|More options|more_vert/i.test(
              (b.getAttribute("aria-label") || "") + " " + (b.innerText || "")
            )
          );
          if (!more) return null;
          more.click();
          await new Promise((r) => setTimeout(r, 550));
          const n = (x) => String(x.innerText || "").normalize("NFC");
          const dlItem = [
            ...document.querySelectorAll(
              ".cdk-overlay-container flow-menu-item, .cdk-overlay-container [role=menuitem], .cdk-overlay-container button"
            ),
          ]
            .filter((x) => x.getBoundingClientRect().width > 0)
            .find((x) => /Tải xuống|Download/i.test(n(x)));
          if (!dlItem) {
            document.body.click();
            return null;
          }
          (dlItem.querySelector("button") || dlItem).click();
          await new Promise((r) => setTimeout(r, 650));
          const subItems = [
            ...document.querySelectorAll(
              ".cdk-overlay-container flow-menu-item, .cdk-overlay-container [role=menuitem]"
            ),
          ].filter((x) => x.getBoundingClientRect().width > 0 && !/Tải xuống|Download/i.test(n(x)));
          if (subItems.length) {
            const pick = use2K
              ? subItems.find((x) => /\b2K\b/i.test(n(x))) || subItems.find((x) => /1K|gốc|original/i.test(n(x)))
              : subItems.find((x) => /1K|gốc|original/i.test(n(x))) || subItems[0];
            if (pick) {
              (pick.querySelector("button") || pick).click();
              return n(pick).trim();
            }
          }
          return "direct";
        },
        {
          targetKey: key,
          baseList: baseline.map((u) => String(u).split("?")[0]),
          use2K: want2K,
        }
      ).catch(() => null);
    });
  };

  try {
    if (prefer2K) {
      const picked2K = await triggerTileDownload(true);
      if (picked2K) {
        const got2K = await waitImgFile(/2K/i.test(picked2K) ? 70 : 20);
        if (got2K && got2K.data.length > 60000) return got2K;
      }
    }
    const picked1K = await triggerTileDownload(false);
    if (picked1K) {
      const got1K = await waitImgFile(24);
      if (got1K && got1K.data.length > 50000) return got1K;
    }
  } finally {
    await page.keyboard.press("Escape").catch(() => {});
    try { await cdp.detach(); } catch {}
    try { if (bCdp) await bCdp.detach(); } catch {}
    try { fs.rmSync(dir, { recursive: true, force: true }); } catch {}
  }
  if (fallbackUrl) return await downloadVideo(page, fallbackUrl);
  throw new Error("Không tải được ảnh gốc từ Flow.");
}

// Ảnh thu nhỏ của ô video chỉ là JPEG, không phải video. Lấy mp4 thật bằng nút "Tải xuống" của Flow (chọn 720p/kích thước gốc),
// giữ nguyên đúng URL dự án u/0, u/1, u/3 của từng luồng Worker sau khi tải xong!
async function downloadVideoViaUi(page, key, baseline = [], returnUrl = "") {
  const backUrl = returnUrl || page.url();
  const dir = fs.mkdtempSync(path.join(require("node:os").tmpdir(), "flow-dl-"));
  const cdp = await page.target().createCDPSession();
  await cdp.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: dir }).catch(async () => {
    const bCdp = await browser.target().createCDPSession();
    await bCdp.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: dir }).catch(() => {});
    await bCdp.detach().catch(() => {});
  });
  const waitDownloadedFile = async (loops) => {
    for (let i = 0; i < loops; i++) {
      await sleep(500);
      const all = fs.readdirSync(dir);
      const ready = all.filter((n) => !n.endsWith(".crdownload") && !n.endsWith(".tmp"));
      if (ready.length && !all.some((n) => n.endsWith(".crdownload"))) {
        await sleep(250);
        return { data: fs.readFileSync(path.join(dir, ready[0])), mime: "video/mp4" };
      }
    }
    return null;
  };
  try {
    // Tầng 1: Thử bấm menu "Tuỳ chọn khác" -> "Tải xuống" ngay trên lưới dự án (KHÔNG chuyển trang sang /edit/!)
    const clickedGridDl = await page.evaluate(`(async () => {
      const k = (x) => String(x.querySelector('img.thumbnail')?.src || '').split('?')[0];
      const tiles = [...document.querySelectorAll('flow-video-tile')]
        .filter((x) => !x.closest('.cdk-overlay-container') && !x.querySelector('flow-pending-tile, flow-soupy-overlay') && k(x) && !/\\b\\d{1,3}%/.test(x.innerText));
      const base = ${JSON.stringify(baseline.map((u) => String(u).split("?")[0]))};
      const t = tiles.find((x) => k(x) === ${JSON.stringify(key)}) || tiles.find((x) => !base.includes(k(x))) || tiles[0];
      if (!t) return false;
      const more = [...t.querySelectorAll('button')].find((b) => /Tuỳ chọn khác|More options|more_vert/i.test((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')));
      if (!more) return false;
      more.click();
      await new Promise((r) => setTimeout(r, 450));
      const n = (x) => String(x.innerText || '').normalize('NFC');
      const dlItem = [...document.querySelectorAll('.cdk-overlay-container [role=menuitem], .cdk-overlay-container flow-menu-item, .cdk-overlay-container button')]
        .filter((x) => x.getBoundingClientRect().width > 0)
        .find((x) => /Tải xuống|Download/i.test(n(x)));
      if (!dlItem) { document.body.click(); return false; }
      (dlItem.querySelector('button') || dlItem).click();
      await new Promise((r) => setTimeout(r, 650));
      const subItems = [...document.querySelectorAll('.cdk-overlay-container flow-menu-item, .cdk-overlay-container [role=menuitem]')]
        .filter((x) => x.getBoundingClientRect().width > 0 && !/Tải xuống|Download/i.test(n(x)));
      if (subItems.length) {
        const orig = subItems.find((x) => /gốc|original|720p/i.test(n(x))) || subItems.find((x) => !/GIF|tăng|upscal/i.test(n(x)));
        if (orig) (orig.querySelector('button') || orig).click();
      }
      return true;
    })()`).catch(() => false);
    if (clickedGridDl) {
      const fastGot = await waitDownloadedFile(16);
      if (fastGot) return fastGot;
      await page.keyboard.press("Escape").catch(() => {});
    }

    // Tầng 2 (Dự phòng): Mở /edit/ -> Tải nội dung nghe nhìn xuống -> Chọn bản gốc -> Quay về đúng backUrl của chính Tab đó!
    const opened = await page.evaluate(`(() => {
      const k = (x) => String(x.querySelector('img.thumbnail')?.src || '').split('?')[0];
      const tiles = [...document.querySelectorAll('flow-video-tile')]
        .filter((x) => !x.closest('.cdk-overlay-container') && !x.querySelector('flow-pending-tile, flow-soupy-overlay') && k(x) && !/\\b\\d{1,3}%/.test(x.innerText));
      const base = ${JSON.stringify(baseline.map((u) => String(u).split("?")[0]))};
      const t = tiles.find((x) => k(x) === ${JSON.stringify(key)}) || tiles.find((x) => !base.includes(k(x))) || tiles[0];
      const i = t && t.querySelector('img.thumbnail'); if (!i) return false; i.click(); return true; })()`);
    if (!opened) throw new Error("Không tìm thấy ô video vừa tạo trên trang Flow.");
    for (let i = 0; i < 40 && !/\/edit\//.test(page.url()); i++) await sleep(500);
    const dlBtn = `button[aria-label="Tải nội dung nghe nhìn xuống"], button[aria-label*="Download" i]`;
    for (let i = 0; i < 40 && !(await page.evaluate(`!!document.querySelector('${dlBtn}')`)); i++) await sleep(500);
    await page.evaluate(`document.querySelector('${dlBtn}').click()`);
    await sleep(1200);
    const picked = await page.evaluate(`(() => {
      const n = (x) => String(x.innerText).normalize('NFC');
      const items = [...document.querySelectorAll('flow-menu-item, [role=menuitem]')].filter((x) => x.getBoundingClientRect().width);
      const it = items.find((x) => /gốc|original/i.test(n(x))) || items.find((x) => !/GIF|tăng|upscal/i.test(n(x)));
      const b = it && (it.querySelector('button') || it); if (!b) return false; b.click(); return true; })()`);
    if (!picked) throw new Error("Không thấy lựa chọn chất lượng khi tải video từ Flow.");
    const got = await waitDownloadedFile(240);
    if (got) return got;
    throw new Error("Hết thời gian chờ tải video từ Flow.");
  } finally {
    try { await cdp.detach(); } catch {}
    try { fs.rmSync(dir, { recursive: true, force: true }); } catch {}
    if (/\/edit\//.test(page.url()) && backUrl && !/\/edit\//.test(backUrl)) {
      await page.goto(backUrl, { waitUntil: "domcontentloaded" }).catch(() => {}); // quay về đúng dự án u/0, u/1, u/3 của riêng Tab này!
    }
  }
}

// Bộ điều phối 9 Luồng × Đa Tài Khoản Google (u/0, u/1, u/2) × 9 Dự án Flow Độc Lập chạy song song 100%:
// - Tận dụng đồng thời cả 3 tài khoản Google Pro/Ultra đã đăng nhập sẵn trong Brave chính (mỗi luồng 1 Tab & 1 Project riêng, xoay vòng đều u/0 -> u/1 -> u/2)!
// - Tự đóng bớt các Tab phụ (#2..#9) sau 20s nghỉ để thanh tab Brave luôn gọn gàng!
const MAX_PARALLEL_FLOW = 9;
const flowSlotBusy = Array(MAX_PARALLEL_FLOW).fill(false);
const flowSlotPages = Array(MAX_PARALLEL_FLOW).fill(null);
const flowSlotIdleTimers = Array(MAX_PARALLEL_FLOW).fill(null);
const waitingFlowQueue = [];

function acquireFlowSlot() {
  for (let i = 0; i < MAX_PARALLEL_FLOW; i++) {
    if (!flowSlotBusy[i]) {
      flowSlotBusy[i] = true;
      if (flowSlotIdleTimers[i]) {
        clearTimeout(flowSlotIdleTimers[i]);
        flowSlotIdleTimers[i] = null;
      }
      return Promise.resolve(i);
    }
  }
  return new Promise((resolve) => waitingFlowQueue.push(resolve));
}

function releaseFlowSlot(slotIdx) {
  const next = waitingFlowQueue.shift();
  if (next) {
    next(slotIdx);
    return;
  }
  flowSlotBusy[slotIdx] = false;
  // Tự động đóng bớt các Tab Worker phụ (Slot 1..3) sau 20s nhàn rỗi, chỉ giữ lại 1 Tab Flow chính (Slot 0)
  if (slotIdx > 0) {
    if (flowSlotIdleTimers[slotIdx]) clearTimeout(flowSlotIdleTimers[slotIdx]);
    flowSlotIdleTimers[slotIdx] = setTimeout(async () => {
      flowSlotIdleTimers[slotIdx] = null;
      if (!flowSlotBusy[slotIdx] && flowSlotPages[slotIdx]) {
        const p = flowSlotPages[slotIdx];
        flowSlotPages[slotIdx] = null;
        try { if (!p.isClosed()) await p.close(); } catch {}
      }
    }, 20000);
  }
}

async function withParallelSlot(fn) {
  const slotIdx = await acquireFlowSlot();
  try {
    return await fn(slotIdx);
  } finally {
    releaseFlowSlot(slotIdx);
  }
}

async function ensureWorkerProjectId(slotIdx) {
  const a = acct();
  if (!Array.isArray(a.workerProjectIds)) {
    a.workerProjectIds = a.projectId ? [a.projectId] : [];
  }
  if (a.workerProjectIds[slotIdx]) return a.workerProjectIds[slotIdx];

  // Quét trang chủ Flow để lấy danh sách dự án sẵn có hoặc bấm "+ Dự án mới" tạo thêm đủ dự án cho các luồng song song
  return await withUiFocusLock(async () => {
    if (a.workerProjectIds[slotIdx]) return a.workerProjectIds[slotIdx];
    const b = await ensureBrowser({ visible: true });
    const helper = await b.newPage();
    try {
      await helper.goto(homeOf(), { waitUntil: "domcontentloaded" }).catch(() => {});
      await sleep(2500);
      const foundIds = await helper.evaluate(() => {
        return [...new Set(
          [...document.querySelectorAll('a[href*="/project/"]')]
            .map((el) => (el.href.match(/\/project\/([0-9a-f-]{36})/) || [])[1])
            .filter(Boolean)
        )];
      }).catch(() => []);
      for (const id of foundIds) {
        if (!a.workerProjectIds.includes(id)) a.workerProjectIds.push(id);
      }
      while (a.workerProjectIds.length <= slotIdx) {
        await helper.goto(homeOf(), { waitUntil: "domcontentloaded" }).catch(() => {});
        await sleep(2000);
        const clicked = await helper.evaluate(() => {
          const btn = document.querySelector("button.new-project-button") ||
            [...document.querySelectorAll("button")].find((x) => /Dự án mới|New project/i.test(x.innerText || ""));
          if (!btn) return false;
          btn.click();
          return true;
        }).catch(() => false);
        if (!clicked) break;
        for (let w = 0; w < 20; w++) {
          await sleep(500);
          const newId = projectOf(helper.url());
          if (newId) {
            if (!a.workerProjectIds.includes(newId)) a.workerProjectIds.push(newId);
            break;
          }
        }
      }
      if (!a.projectId && a.workerProjectIds[0]) a.projectId = a.workerProjectIds[0];
      saveConfig();
    } finally {
      await helper.close().catch(() => {});
    }
    return a.workerProjectIds[slotIdx] || a.workerProjectIds[0] || config.projectId;
  });
}

// ───────── Tự động theo dõi điểm & Đổi Nick Google (u/0, u/1, u/3, ...) ngay khi hết điểm Flow ─────────
const CREDIT_EXHAUSTED_TTL_MS = 4 * 3600 * 1000; // đánh dấu tạm nghỉ 4 giờ rồi tự kiểm tra lại (phòng khi Google cộng điểm tháng mới)
const CREDIT_ERR_RE = /không đủ tín dụng|hết tín dụng|hết điểm|không còn tín dụng|mua thêm tín dụng|nâng cấp gói|đạt đến giới hạn tín dụng|not enough credits|insufficient credits|out of credits|no credits|credit limit|upgrade plan|top up credits/i;

function getPrefixCreditsMap() {
  const a = acct();
  if (!a) return {};
  if (!a.prefixCredits || typeof a.prefixCredits !== "object") a.prefixCredits = {};
  return a.prefixCredits;
}

function isPrefixExhausted(prefix, kind = "video") {
  const map = getPrefixCreditsMap();
  const info = map[prefix || "u/0/"];
  if (!info || !info.exhaustedUntil) return false;
  if (Date.now() > info.exhaustedUntil) {
    delete info.exhaustedUntil;
    saveConfig();
    return false;
  }
  const need = minCredits(kind);
  return typeof info.credits === "number" ? info.credits < need : true;
}

function markPrefixExhausted(prefix, credits = 0, email = "") {
  const key = prefix || "u/0/";
  const map = getPrefixCreditsMap();
  map[key] = {
    ...(map[key] || {}),
    credits: typeof credits === "number" ? credits : 0,
    ...(email ? { email } : {}),
    updatedAt: Date.now(),
    exhaustedUntil: Date.now() + CREDIT_EXHAUSTED_TTL_MS,
  };
  saveConfig();
  console.warn(`[flow:AutoSwitch] Nick ${key}${email ? ` (${email})` : ""} còn ${credits ?? 0} điểm -> đánh dấu hết điểm và tự chuyển sang nick khác!`);
}

function recordPrefixHealthyCredits(prefix, credits, email = "") {
  if (typeof credits !== "number") return;
  const key = prefix || "u/0/";
  const map = getPrefixCreditsMap();
  map[key] = {
    ...(map[key] || {}),
    credits,
    ...(email ? { email } : {}),
    updatedAt: Date.now(),
  };
  if (credits >= minCredits("video")) {
    delete map[key].exhaustedUntil;
  }
  saveConfig();
}

async function checkPrefixCreditsLive(prefix) {
  const b = await ensureBrowser({ visible: true });
  const normPrefix = prefix || "u/0/";
  const p = await createBackgroundPage(b, `${HOME}${normPrefix}`);
  try {
    await sleep(3000);
    if (/accounts\.google\.com/.test(p.url())) return null;
    const actualPrefix = userPrefixOf(p.url()) || normPrefix;
    const info = await readCreditsOnPage(p);
    if (!info) return null;
    return { prefix: actualPrefix, credits: info.credits, email: info.email || "" };
  } finally {
    await p.close().catch(() => {});
  }
}

// Quét tự động u/0 .. u/7 trong Brave chính để tìm thêm nick Google mới đăng nhập còn điểm Flow và tự tạo dự án cho nick đó!
async function discoverMoreGoogleNicksInBrave(kind = "video", skipPrefixes = new Set()) {
  const a = acct();
  if (!a || !isMainBraveProfile(a.profile)) return null;
  if (!Array.isArray(a.workerTargets)) a.workerTargets = [];
  const need = minCredits(kind);
  const b = await ensureBrowser({ visible: true });

  for (let idx = 0; idx <= 7; idx++) {
    const candPrefix = `u/${idx}/`;
    if (skipPrefixes.has(candPrefix)) continue;
    const p = await createBackgroundPage(b, `https://flow.google.com/?authuser=${idx}`);
    try {
      await sleep(3200);
      const landUrl = p.url() || "";
      if (/accounts\.google\.com/.test(landUrl)) continue;
      const realPrefix = userPrefixOf(landUrl) || "u/0/";
      if (skipPrefixes.has(realPrefix)) continue;
      const credInfo = await readCreditsOnPage(p);
      if (!credInfo || credInfo.credits < need) {
        if (credInfo) markPrefixExhausted(realPrefix, credInfo.credits, credInfo.email);
        skipPrefixes.add(realPrefix);
        continue;
      }
      recordPrefixHealthyCredits(realPrefix, credInfo.credits, credInfo.email);

      // Thu thập hoặc tạo tối thiểu 2 dự án Flow cho nick mới tìm thấy
      let pids = await p.evaluate(() => {
        return [...new Set(
          [...document.querySelectorAll('a[href*="/project/"]')]
            .map((el) => (el.href.match(/\/project\/([0-9a-f-]{36})/) || [])[1])
            .filter(Boolean)
        )];
      }).catch(() => []);

      while (pids.length < 2) {
        await p.goto(`${HOME}${realPrefix}`, { waitUntil: "domcontentloaded" }).catch(() => {});
        await sleep(1800);
        const clicked = await p.evaluate(() => {
          const btn = document.querySelector("button.new-project-button") ||
            [...document.querySelectorAll("button")].find((x) => /Dự án mới|New project/i.test(x.innerText || ""));
          if (!btn) return false;
          btn.click();
          return true;
        }).catch(() => false);
        if (!clicked) break;
        for (let w = 0; w < 20; w++) {
          await sleep(450);
          const nid = projectOf(p.url());
          if (nid) {
            if (!pids.includes(nid)) pids.push(nid);
            break;
          }
        }
      }

      for (const pid of pids) {
        if (!a.workerTargets.some((t) => t.prefix === realPrefix && t.projectId === pid)) {
          a.workerTargets.push({ prefix: realPrefix, projectId: pid });
        }
      }
      saveConfig();
      if (pids[0]) {
        console.log(`[flow:AutoSwitch] Đã tự động phát hiện & kích hoạt nick ${realPrefix} (${credInfo.email || "Google"}, còn ${credInfo.credits} điểm)!`);
        return { prefix: realPrefix, projectId: pids[0] };
      }
    } finally {
      await p.close().catch(() => {});
    }
  }
  return null;
}

async function resolveHealthyTargetForSlot(slotIdx, kind = "video", triedPrefixes = new Set()) {
  const a = acct();
  const targets = Array.isArray(a?.workerTargets) ? a.workerTargets : [];
  const defaultWt = targets[slotIdx] || null;

  if (defaultWt && defaultWt.projectId && !triedPrefixes.has(defaultWt.prefix) && !isPrefixExhausted(defaultWt.prefix, kind)) {
    return defaultWt;
  }

  // Nếu nick mặc định của Slot này đã hết điểm -> chọn ngay một dự án thuộc nick khác còn điểm (ưu tiên dự án đang rảnh)
  const busyUrls = new Set(
    flowSlotPages
      .map((p, idx) => (idx !== slotIdx && p && !p.isClosed() ? p.url() : ""))
      .filter(Boolean)
  );
  const healthy = targets.filter(
    (t) => t && t.projectId && !triedPrefixes.has(t.prefix) && !isPrefixExhausted(t.prefix, kind)
  );
  if (healthy.length > 0) {
    const freeOne = healthy.find((t) => !busyUrls.has(`${HOME}${t.prefix}project/${t.projectId}`));
    return freeOne || healthy[slotIdx % healthy.length];
  }

  // Nếu cả các nick đã cấu hình đều hết điểm -> tự động quét u/0..u/7 trong Brave xem có nick nào khác còn điểm không!
  const discovered = await discoverMoreGoogleNicksInBrave(kind, new Set(triedPrefixes));
  if (discovered) return discovered;

  return null;
}

async function findOpenTabMatchingAssets(b, slotIdx, kind, triedPrefixes, job) {
  const imgs = Array.isArray(job?.images) ? job.images : [];
  if (!imgs.length) return null;
  const wantStems = imgs
    .map((im) => String(im?.name || "").trim().replace(/\.(png|jpe?g|webp|gif)$/i, "").toLowerCase())
    .filter((s) => s && !/^(ảnh|anh|image|img|asset|node|unnamed|untitled)[\s_-]*\d*$/i.test(s));
  if (!wantStems.length) return null;

  const pages = await b.pages().catch(() => []);
  let best = null;
  let bestScore = 0;
  for (const p of pages) {
    if (!p || p.isClosed()) continue;
    const u = p.url() || "";
    const pid = projectOf(u);
    if (!pid || /\/edit\//.test(u)) continue;
    const pf = userPrefixOf(u) || "u/0/";
    if (triedPrefixes.has(pf) || isPrefixExhausted(pf, kind)) continue;
    // Không tranh tab đang bận của một slot khác
    const heldByOtherBusy = flowSlotPages.some((sp, idx) => idx !== slotIdx && flowSlotBusy[idx] && sp === p);
    if (heldByOtherBusy) continue;

    const score = await p.evaluate((stems) => {
      const reg = (window.__flowAssetRegistry && window.__flowAssetRegistry[location.pathname]) || {};
      const regStems = Object.keys(reg).map((k) => k.replace(/\.(png|jpe?g|webp|gif)$/i, "").toLowerCase());
      const gridStems = [...document.querySelectorAll("flow-image-tile .footer-title")]
        .map((el) => (el.innerText || el.textContent || "").trim().replace(/\.(png|jpe?g|webp|gif)$/i, "").toLowerCase())
        .filter(Boolean);
      const known = new Set([...regStems, ...gridStems]);
      return stems.filter((s) => known.has(s)).length;
    }, wantStems).catch(() => 0);

    if (score > bestScore) {
      bestScore = score;
      best = { page: p, prefix: pf, projectId: pid };
    }
  }
  return best;
}

async function ensureSlotProjectPage(slotIdx, kind = "video", triedPrefixes = new Set(), job = null) {
  const b = await ensureBrowser({ visible: true });

  // Ưu tiên gắn vào Tab dự án Flow đang mở sẵn đã chứa các ảnh tham chiếu của lệnh này (tránh nhảy sang dự án trống phải tải lại ảnh!)
  const affinity = await findOpenTabMatchingAssets(b, slotIdx, kind, triedPrefixes, job);
  if (affinity && affinity.page) {
    affinity.page.__flowSlotIdx = slotIdx;
    flowSlotPages[slotIdx] = affinity.page;
    for (let i = 0; i < 30; i++) {
      if (await affinity.page.evaluate(`!!document.querySelector('.ProseMirror')`).catch(() => false)) {
        return { page: affinity.page, prefix: affinity.prefix };
      }
      await sleep(300);
    }
  }

  const a = acct();
  const hasTargets = Array.isArray(a?.workerTargets) && a.workerTargets.length > 0;
  const wt = hasTargets ? await resolveHealthyTargetForSlot(slotIdx, kind, triedPrefixes) : null;
  if (hasTargets && !wt) {
    const map = getPrefixCreditsMap();
    const summary = Object.entries(map)
      .map(([k, v]) => `${k.replace("/", "")}${v.email ? ` (${v.email})` : ""}: ${v.credits ?? 0} điểm`)
      .join("; ");
    throw new Error(
      `Tất cả các nick Google Flow trong Brave đều đã hết điểm (cần ≥ ${minCredits(kind)} điểm). ${summary ? `[${summary}]. ` : ""}Hãy đăng nhập thêm tài khoản Google mới trong cửa sổ Brave chính, hệ thống sẽ tự nhận ngay!`
    );
  }
  const targetPid = wt?.projectId || (await ensureWorkerProjectId(slotIdx));
  if (!targetPid) return { page: await ensureProjectPage(), prefix: config.userPrefix || "u/0/" };
  const targetPrefix = wt && typeof wt.prefix === "string" ? wt.prefix : (config.userPrefix || "u/0/");
  const targetUrl = `${HOME}${targetPrefix}project/${targetPid}`;

  let page = flowSlotPages[slotIdx];
  if (page && page.isClosed()) {
    page = null;
    flowSlotPages[slotIdx] = null;
  }
  if (!page) {
    const pages = await b.pages();
    page = pages.find((p) => {
      const u = p.url() || "";
      return projectOf(u) === targetPid &&
        (!targetPrefix || userPrefixOf(u) === targetPrefix) &&
        (p.__flowSlotIdx == null || p.__flowSlotIdx === slotIdx) &&
        !flowSlotPages.some((sp, idx) => idx !== slotIdx && sp === p);
    }) || null;
  }
  if (!page) {
    // Mở Tab Worker ngầm 100% (background: true) để KHÔNG bao giờ cướp chuột của Tab khác đang bấm nút Tạo!
    page = await createBackgroundPage(b, targetUrl);
    await fixHeadlessUA(page);
  }
  page.__flowSlotIdx = slotIdx;
  flowSlotPages[slotIdx] = page;
  if (!page.url().startsWith(targetUrl) || /\/edit\//.test(page.url())) {
    await page.goto(targetUrl, { waitUntil: "domcontentloaded" }).catch(() => {});
  }
  for (let i = 0; i < 60; i++) {
    if (/accounts\.google\.com/.test(page.url())) {
      await show().catch(() => {});
      throw new Error("Cần đăng nhập Google trong cửa sổ Brave chính, rồi tạo lại.");
    }
    if (await page.evaluate(`!!document.querySelector('.ProseMirror')`).catch(() => false)) {
      return { page, prefix: targetPrefix };
    }
    await sleep(500);
  }
  throw new Error(`Tab Flow #${slotIdx + 1} (${targetPrefix}) không thấy ô nhập prompt.`);
}

async function generateOnceOnSlot(job, onProgress, slotIdx, page, currentPrefix) {
  const jobId = `fj_s${slotIdx}_${Date.now()}_${Math.random().toString(36).slice(2, 5)}`;
  const activeCount = flowSlotBusy.filter(Boolean).length;
  const tag = `[flow:Tab#${slotIdx + 1}/${MAX_PARALLEL_FLOW} • ${currentPrefix}] ${job.kind}`;
  console.log(`${tag}: bắt đầu (đang chạy song song ${activeCount} dự án Flow cùng lúc)`);
  const sub = await withUiFocusLock(async () => {
    await page.bringToFront().catch(() => {});
    await closeAccountMenu(page);
    await inject(page);
    const s = await page.evaluate(`window.__flowUi.submit(${JSON.stringify({ ...job, jobId, trustedClick: true })}).catch((e) => ({ error: String(e.message || e), log: window.__flowUi.log.slice(-15) }))`);
    if (s.error) { console.log(`${tag}: lỗi khi điền form: ${s.error}`); throw new Error(s.error + (s.log?.length ? "\n" + s.log.join("\n") : "")); }
    if (s.clickAt) {
      await page.bringToFront().catch(() => {});
      await page.mouse.click(s.clickAt.x, s.clickAt.y);
      s.t0 = Date.now();
      const probe = `(() => {
        const e = document.querySelector('.ProseMirror');
        const filled = !!(e && e.innerText.trim());
        const unclaimed = [...document.querySelectorAll('flow-video-tile, flow-error-tile')].filter((t) => !t.closest('.cdk-overlay-container') && !t.dataset.flowJobId).length;
        const dialog = (document.querySelector('.cdk-overlay-container, mat-snack-bar-container')?.innerText || '').trim().slice(0, 260);
        return { filled, unclaimed, dialog };
      })()`;
      let accepted = false, last = null, reclicked = false;
      for (let i = 0; i < 24 && !accepted; i++) {
        await sleep(450);
        last = await page.evaluate(probe).catch(() => null);
        if (last && CREDIT_ERR_RE.test(last.dialog || "")) {
          throw new Error("FLOW_OUT_OF_CREDITS: " + last.dialog.replace(/\s+/g, " "));
        }
        if (last && (!last.filled || last.unclaimed > 0)) accepted = true;
        else if (i === 11 && !reclicked && last?.filled) { reclicked = true; await page.bringToFront().catch(() => {}); await page.mouse.click(s.clickAt.x, s.clickAt.y); }
      }
      if (!accepted) throw new Error("Flow không nhận lệnh tạo (ô nhập vẫn còn nội dung sau khi bấm). Kiểm tra credit/giới hạn của Flow." + (last?.dialog ? " Flow hiện: " + last.dialog.replace(/\s+/g, " ") : ""));
      // Chờ tối đa 4.5s để thẻ tile mới xuất hiện ở đầu lưới rồi đóng dấu jobId ngay lập tức trước khi nhả khóa cho clip tiếp theo!
      if (job.kind !== "image") {
        for (let w = 0; w < 12; w++) {
          const claimed = await page.evaluate((jid, exp) => window.__flowUi?.claimSpawnedTiles?.(jid, exp) || 0, s.jobId, s.expect || 1).catch(() => 0);
          if (claimed >= (s.expect || 1)) break;
          await sleep(380);
        }
      }
    }
    return s;
  });
  console.log(`${tag}: đã gắn lên hàng render đám mây (đã nhả khóa cho clip kế tiếp!)`);
  const timeoutMs = (job.timeoutMin || 10) * 60 * 1000;
  const t0 = Date.now();
  for (;;) {
    await sleep(3000);
    if (Date.now() - t0 > timeoutMs) throw new Error("Hết thời gian chờ video từ Flow.");
    await inject(page).catch(() => {});
    const st = await page.evaluate(`window.__flowUi.poll(${JSON.stringify({ jobId: sub.jobId, promptPrefix: sub.promptPrefix, baseline: sub.baseline, expect: sub.expect, t0: sub.t0, kind: sub.kind })})`).catch(() => null);
    if (!st) continue;
    onProgress?.(st);
    if (st.state === "failed") throw new Error("Flow báo lỗi: " + (st.error || "không rõ"));
    if (st.state === "done") {
      if (job.kind === "image") await sleep(2000);
      console.log(`${tag}: xong, tải trực tiếp ${Math.min(st.videos.length, job.count || 1)} tệp (không rời trang)...`);
      const out = [];
      for (const v of st.videos.slice(0, job.count || 1)) {
        if (job.kind === "image") {
          const prefer2K = job.quality !== "1K";
          out.push(await downloadImageViaUi(page, v.id, sub.baseline, prefer2K, v.url));
        } else {
          let directItem = null;
          if (v.url) {
            try {
              const dl = await downloadVideo(page, v.url);
              if (dl && dl.data && dl.data.length > 16384 && /video/i.test(dl.mime || "")) {
                directItem = { data: dl.data, mime: "video/mp4" };
              }
            } catch (e) {
              console.log(`${tag}: tải trực tiếp fallback sang UI:`, e.message || e);
            }
          }
          if (directItem) {
            out.push(directItem);
          } else {
            const slotHomeUrl = page.url();
            out.push(await withUiFocusLock(async () => { await page.bringToFront().catch(() => {}); return downloadVideoViaUi(page, v.id, sub.baseline, slotHomeUrl); }));
          }
        }
      }
      if (store.accounts.length > 1) {
        await refreshCredits(page).catch(() => {});
      }
      return out; // [{data, mime}]
    }
  }
}

async function generate(job, onProgress, slotIdx = 0) {
  if (store.accounts.length > 1) {
    const page = await pickAccountWithCredits(job);
    return await generateOnceOnSlot(job, onProgress, slotIdx, page, config.userPrefix || "u/0/");
  }

  const triedPrefixes = new Set();
  const maxAttempts = 6;
  let lastErr = null;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const { page, prefix } = await ensureSlotProjectPage(slotIdx, job.kind, triedPrefixes, job);
    try {
      return await generateOnceOnSlot(job, onProgress, slotIdx, page, prefix);
    } catch (err) {
      lastErr = err;
      const msg = String(err && (err.message || err));
      const directCreditHit = msg.includes("FLOW_OUT_OF_CREDITS") || CREDIT_ERR_RE.test(msg);
      const maybeBlockedByCredits = /Flow không nhận lệnh tạo|UI_TIMEOUT: generate enabled/i.test(msg);

      let confirmedLowCredits = directCreditHit;
      let liveCreds = null;
      if (!confirmedLowCredits && maybeBlockedByCredits) {
        liveCreds = await checkPrefixCreditsLive(prefix).catch(() => null);
        if (liveCreds) {
          if (liveCreds.credits < minCredits(job.kind)) {
            confirmedLowCredits = true;
          } else {
            recordPrefixHealthyCredits(prefix, liveCreds.credits, liveCreds.email);
          }
        }
      } else if (confirmedLowCredits) {
        liveCreds = await checkPrefixCreditsLive(prefix).catch(() => null);
      }

      if (confirmedLowCredits) {
        markPrefixExhausted(prefix, liveCreds?.credits ?? 0, liveCreds?.email || "");
        triedPrefixes.add(prefix);
        console.warn(`[flow:AutoSwitch] Lần thử #${attempt + 1}: Nick ${prefix} hết điểm -> tự động chuyển ngay sang nick tiếp theo!`);
        continue;
      }
      throw err;
    }
  }
  throw lastErr || new Error("Không thể tạo trên Flow sau khi thử đổi qua các nick.");
}

function setup(app) {
  userData = app.getPath("userData");
  configPath = path.join(userData, "flow-driver.json");
  loadConfig();

  ipcMain.handle("flow:status", async () => {
    const alive = !!(await debugAlive());
    const page = alive ? await flowPage(false).catch(() => null) : null;
    return { account: acct().name, accounts: store.accounts.map((a) => ({ id: a.id, name: a.name, email: a.email || "", credits: a.credits ?? null, creditsAt: a.creditsAt || null, active: a.id === store.active, hasProject: !!a.projectId })), projectId: config.projectId || "", browserOpen: alive, onFlow: !!page, loggedIn: page ? !/accounts\.google\.com/.test(page.url()) : null };
  });
  ipcMain.handle("flow:accounts", () => status());
  ipcMain.handle("flow:switch-account", (_e, id) => switchAccount(id).then(status));
  ipcMain.handle("flow:add-account", () => addAccount().then(status));
  ipcMain.handle("flow:remove-account", (_e, id) => removeAccount(id).then(status));
  ipcMain.handle("flow:rename-account", (_e, id, name) => { renameAccount(id, name); return status(); });
  ipcMain.handle("flow:open-account", (_e, id) => openAccount(id).then(status));
  ipcMain.handle("flow:refresh-credits", () => refreshAllCredits().then(status));
  ipcMain.handle("flow:set-min-credits", (_e, n) => { setMinCredits(n); return status(); });
  ipcMain.handle("flow:show", () => show().catch((e) => { dialog.showErrorBox("Flow", String(e.message || e)); return false; }));
  // job: {prompt, model, mode, aspect, resolution, seconds, count, images:[{base64,mime,name}]}
  const enqueue = (kind) => (_e, job) => {
    const p = withParallelSlot((slotIdx) => generate({ ...job, kind }, undefined, slotIdx));
    return p.then((items) => ({ ok: true, items, data: items[0].data, mime: items[0].mime }), (e) => ({ ok: false, error: String(e.message || e) }));
  };
  ipcMain.handle("flow:generate-video", enqueue("video"));
  // job: {prompt, model, ratio, quality, count, images:[{base64,mime,name}]} -> items:[{data,mime}]
  ipcMain.handle("flow:generate-image", enqueue("image"));
}

function generateImageFallback(job) {
  return withParallelSlot((slotIdx) => generate({ ...(job || {}), kind: "image" }, undefined, slotIdx));
}

// ───────── Điểm (tín dụng) của tài khoản ─────────
// Điểm nằm trong menu tài khoản Google ở góc phải Flow ("1.038 tín dụng Google Flow").
// Menu tài khoản mà để mở sẽ phủ lên trang và nuốt cú bấm nút tạo: phải đóng hẳn (nút "close"; Escape không đủ)
async function closeAccountMenu(page) {
  const isOpen = () => page.evaluate(() => /Đăng xuất khỏi mọi tài khoản|Sign out of all accounts|Quản lý gói thuê bao|Manage subscription/.test(document.body.innerText)).catch(() => false);
  for (let i = 0; i < 5 && (await isOpen()); i++) {
    await page.evaluate(() => {
      const c = [...document.querySelectorAll("button")].find((x) => x.innerText.trim() === "close" || /^(Đóng|Close)$/i.test(x.getAttribute("aria-label") || ""));
      if (c) c.click();
    }).catch(() => {});
    await sleep(500);
    if (await isOpen()) await page.keyboard.press("Escape").catch(() => {});
  }
}

async function readCreditsOnPage(page) {
  const label = await page.evaluate(() => {
    const b = [...document.querySelectorAll("a,button")].find((x) => /^(Tài khoản Google|Google Account)/i.test(x.getAttribute("aria-label") || ""));
    if (!b) return null;
    b.click();
    return b.getAttribute("aria-label");
  }).catch(() => null);
  if (!label) return null;
  let m = null;
  for (let i = 0; i < 12 && !m; i++) {
    await sleep(400);
    const t = await page.evaluate(() => document.body.innerText).catch(() => "");
    m = t.match(/(\d[\d.,]*)\s*(?:tín dụng|credits?)/i);
  }
  await closeAccountMenu(page);
  if (!m) return null;
  return { credits: parseInt(m[1].replace(/[.,]/g, ""), 10), email: (label.match(/\(([^)\s]+@[^)\s]+)\)/) || [])[1] || "" };
}

// đọc điểm của tài khoản đang dùng và lưu lại (hiện trên menu); không có nút tài khoản ở trang hiện tại thì ghé trang chủ Flow rồi quay lại
async function refreshCredits(page) {
  try {
    let r = await readCreditsOnPage(page);
    if (!r) {
      const back = page.url();
      await page.goto(homeOf(), { waitUntil: "domcontentloaded" }).catch(() => {});
      await sleep(4000);
      r = await readCreditsOnPage(page);
      if (back && back !== page.url()) await page.goto(back, { waitUntil: "domcontentloaded" }).catch(() => {});
    }
    if (!r) return null;
    const a = acct();
    a.credits = r.credits; a.creditsAt = Date.now();
    if (r.email) { a.email = r.email; if (/^Tài khoản \d+$/.test(a.name)) a.name = r.email; } // đặt tên theo email để dễ nhận ra
    saveConfig(); onChange();
    console.log(`[flow] điểm ${a.name}: ${r.credits}`);
    return r.credits;
  } catch (e) { console.log("[flow] không đọc được điểm: " + (e.message || e)); return null; }
}

// tài khoản còn dưới ngưỡng tối thiểu (20 điểm cho video, 5 điểm cho ảnh) thì tự động đổi sang nick tiếp theo để vắt kiệt tối đa điểm từng nick!
const minCredits = (kind) => ({ image: 5, video: 20, ...(store.minCredits || {}) })[kind] ?? 20;

// chọn tài khoản còn đủ điểm: nếu chỉ dùng 1 tài khoản chính (AI Ultra trên Brave chính) thì vào thẳng trang project luôn, không nhảy về trang chủ đếm điểm gây trễ 15-20s mỗi clip!
async function pickAccountWithCredits(job) {
  if (store.accounts.length <= 1) {
    return await ensureProjectPage();
  }
  const need = minCredits(job.kind);
  const original = store.active;
  const order = [original, ...store.accounts.map((a) => a.id).filter((id) => id !== original)];
  const notes = [];
  for (const id of order) {
    const a = store.accounts.find((x) => x.id === id);
    if (id !== store.active) {
      if (!a.projectId) { notes.push(`${a.name}: chưa chọn project`); continue; }
      store.active = id; saveConfig();
      await stopOwnBrowser();
      onChange();
      console.log(`[flow] đổi sang ${a.name}`);
    }
    const page = await ensureProjectPage();
    const credits = await refreshCredits(page);
    if (credits == null || credits >= need) return await ensureProjectPage(); // đọc không được thì cứ chạy, nếu hết điểm Flow sẽ tự báo. Đọc điểm có thể đã chuyển trang: đợi ô nhập sẵn sàng
    notes.push(`${a.name}: còn ${credits} điểm`);
  }
  store.active = original; saveConfig(); onChange();
  throw new Error(`Tất cả tài khoản Flow đều không đủ điểm (cần ≥ ${need}). ${notes.join("; ")}`);
}

// ───────── Nhiều tài khoản ─────────
// Chạy trong hàng đợi tạo để không đổi tài khoản giữa lúc đang tạo.
const inQueue = (fn) => { const p = queue.then(fn); queue = p.catch(() => {}); return p; };
const fail = (e) => dialog.showErrorBox("Flow", String(e.message || e));

function switchAccount(id) {
  return inQueue(async () => {
    if (!store.accounts.some((a) => a.id === id) || id === store.active) return;
    store.active = id; saveConfig();
    await stopOwnBrowser(); // lần tạo sau sẽ mở trình duyệt với profile của tài khoản này
    onChange();
  });
}

// đọc điểm của mọi tài khoản (nếu dùng Brave chính đa nick u/0, u/1, u/3... thì quét toàn bộ các nick trong Brave và cộng tổng điểm khả dụng!)
function refreshAllCredits() {
  return inQueue(async () => {
    const cur = acct();
    if (cur && isMainBraveProfile(cur.profile)) {
      const prefixes = [...new Set(((cur.workerTargets || []).map((t) => t.prefix)).filter(Boolean))];
      let total = 0;
      for (const pf of prefixes) {
        const info = await checkPrefixCreditsLive(pf).catch(() => null);
        if (!info) continue;
        total += info.credits;
        if (info.credits < minCredits("video")) markPrefixExhausted(pf, info.credits, info.email);
        else recordPrefixHealthyCredits(pf, info.credits, info.email);
      }
      await discoverMoreGoogleNicksInBrave("video", new Set(prefixes)).catch(() => {});
      cur.credits = total;
      cur.creditsAt = Date.now();
      saveConfig();
      onChange();
      return;
    }
    const original = store.active;
    for (const a of [...store.accounts]) {
      if (!a.projectId) continue;
      if (a.id !== store.active) { store.active = a.id; await stopOwnBrowser(); }
      try { await refreshCredits(await ensureProjectPage()); } catch (e) { console.log(`[flow] ${a.name}: ${e.message || e}`); }
    }
    if (store.active !== original) { store.active = original; saveConfig(); await stopOwnBrowser(); }
    onChange();
  });
}

function addAccount() {
  return inQueue(async () => {
    const n = store.accounts.length + 1;
    const id = "a" + Date.now().toString(36);
    store.accounts.push({ id, name: "Tài khoản " + n, profile: "flow-browser-profile-" + id, projectId: "" });
    store.active = id; saveConfig();
    await stopOwnBrowser();
    onChange();
    await show(); // mở cửa sổ thật để đăng nhập Google rồi mở/tạo project
  });
}

function removeAccount(id) {
  return inQueue(async () => {
    if (store.accounts.length <= 1 || !store.accounts.some((a) => a.id === id)) return;
    const wasActive = id === store.active;
    store.accounts = store.accounts.filter((x) => x.id !== id);
    if (wasActive) { store.active = store.accounts[0].id; await stopOwnBrowser(); }
    saveConfig();
    onChange();
  });
}

function renameAccount(id, name) {
  const a = store.accounts.find((x) => x.id === id);
  if (a && String(name || "").trim()) { a.name = String(name).trim(); saveConfig(); onChange(); }
}

// mở cửa sổ Flow của một tài khoản (đổi sang tài khoản đó trước) để đăng nhập / chọn project
function openAccount(id) {
  return inQueue(async () => {
    if (!store.accounts.some((a) => a.id === id)) return;
    if (id !== store.active) { store.active = id; saveConfig(); await stopOwnBrowser(); onChange(); }
    await show();
  });
}

function status() {
  return {
    minCredits: { image: minCredits("image"), video: minCredits("video") },
    accounts: store.accounts.map((a) => ({ id: a.id, name: a.name, email: a.email || "", credits: a.credits ?? null, creditsAt: a.creditsAt || null, active: a.id === store.active, hasProject: !!a.projectId })),
  };
}

function setMinCredits(n) {
  const v = Math.max(0, Math.floor(Number(n) || 0));
  store.minCredits = { image: v, video: v };
  saveConfig();
}


function destroy() {
  // trình duyệt ẩn do app mở phải tắt theo app, kẻo chạy ngầm không ai thấy
  if (mode === "headless" && child) { try { child.kill(); } catch {} }
  try { browser?.disconnect(); } catch {}
  // không đóng Chrome của Flow: người dùng có thể đang dùng; phiên đăng nhập nằm trong profile riêng
}

module.exports = { setup, destroy, show, ensureBrowser, debugAlive, withUiFocusLock, ensureWindowOnScreen, createBackgroundPage, generateImageFallback };
