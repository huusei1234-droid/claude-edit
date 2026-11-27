// Điều khiển ChatGPT Web (https://chatgpt.com/) trên CÙNG 1 CỬA SỔ TRÌNH DUYỆT BRAVE (cổng CDP 9333)
// chung với Google Flow (mở thành 2 Tab gọn gàng: Tab 1 Flow + Tab 2 ChatGPT, phối hợp qua khóa nhường chuột `withUiFocusLock`).
// Tuân thủ nguyên tắc an toàn: luôn mở cửa sổ thật (không headless), không bao giờ tự giải/vượt CAPTCHA hay bot-check,
// không đọc/in cookie hay token ra log.
const { ipcMain, dialog } = require("electron");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const flow = require("./flow-driver");

const LEGACY_PORT = 9334;
const HOME = "https://chatgpt.com/";
const DEFAULT_PROJECT_LABEL = process.env.CHATGPT_PROJECT || "HTPM";
const DEFAULT_PROJECT_ID = "g-p-6b03c9b49b68819188e93910a01de7b1";

let userData = "";
let configPath = "";
let store = { accounts: [], active: "" };
let onChange = () => {};
let queue = Promise.resolve();

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const acct = () => store.accounts.find((a) => a.id === store.active) || store.accounts[0];

function loadConfig() {
  let raw = {};
  try {
    raw = JSON.parse(fs.readFileSync(configPath, "utf8"));
  } catch {}
  if (Array.isArray(raw.accounts) && raw.accounts.length) {
    store = { accounts: raw.accounts, active: raw.active };
  } else {
    store = {
      accounts: [{ id: "gpt1", name: "ChatGPT (Tab chung Brave)", profile: "flow-browser-profile" }],
      active: "gpt1",
    };
  }
  if (!acct() || acct().id !== store.active) store.active = store.accounts[0].id;
}

function saveConfig() {
  try {
    fs.writeFileSync(configPath, JSON.stringify(store, null, 2));
  } catch {}
}

async function closeLegacy9334IfOpen() {
  try {
    const r = await fetch(`http://127.0.0.1:${LEGACY_PORT}/json/version`, { signal: AbortSignal.timeout(1000) });
    if (!r.ok) return;
    const info = await r.json();
    const mod = await import("puppeteer-core");
    const puppeteer = mod.default && mod.default.connect ? mod.default : mod;
    const oldB = await puppeteer.connect({ browserWSEndpoint: info.webSocketDebuggerUrl, defaultViewport: null });
    await oldB.close().catch(() => {});
    console.log("[chatgpt] đã đóng cửa sổ Brave phụ 9334 cũ (gộp về chung 1 cửa sổ Brave 9333).");
  } catch {}
}

async function debugAlive() {
  return flow.debugAlive();
}

async function stopOwnBrowser() {
  // Đã dùng chung trình duyệt Brave 9333 với Flow -> không đóng cả cửa sổ trình duyệt khi thao tác bên ChatGPT
}

async function ensureBrowser() {
  return flow.ensureBrowser({ visible: true });
}

function targetProjectId() {
  const targetLabel = (acct()?.projectLabel || DEFAULT_PROJECT_LABEL || "HTPM").trim();
  return acct()?.projectId || (targetLabel.toUpperCase() === "HTPM" ? DEFAULT_PROJECT_ID : DEFAULT_PROJECT_ID);
}

function targetProjectUrl() {
  return `https://chatgpt.com/g/${targetProjectId()}/project`;
}

// Bộ điều phối 3 Tab ChatGPT (dự án HTPM) chạy song song cùng lúc:
// - Mỗi luồng sở hữu 1 Tab riêng trong dự án HTPM -> tạo ảnh đồng thời 3 tấm/mẻ nhanh gấp 3 lần, không bao giờ lẫn ảnh!
// - Sau khi tải ảnh xong, từng Tab tự xóa ngay cuộc trò chuyện tạm của riêng nó để sạch bộ nhớ HTPM.
// - Sau 15 giây nhàn rỗi, các Tab phụ (#2, #3) tự động đóng lại, chỉ giữ đúng 1 Tab HTPM gọn gàng trên Brave chính!
const MAX_CHATGPT_WORKERS = 3;
const gptSlotBusy = Array(MAX_CHATGPT_WORKERS).fill(false);
const gptSlotPages = Array(MAX_CHATGPT_WORKERS).fill(null);
const gptSlotIdleTimers = Array(MAX_CHATGPT_WORKERS).fill(null);
const waitingGptQueue = [];

function acquireGptSlot() {
  for (let i = 0; i < MAX_CHATGPT_WORKERS; i++) {
    if (!gptSlotBusy[i]) {
      gptSlotBusy[i] = true;
      if (gptSlotIdleTimers[i]) {
        clearTimeout(gptSlotIdleTimers[i]);
        gptSlotIdleTimers[i] = null;
      }
      return Promise.resolve(i);
    }
  }
  return new Promise((resolve) => waitingGptQueue.push(resolve));
}

async function sweepIdleChatgptTabs() {
  if (gptSlotBusy.some(Boolean) || waitingGptQueue.length > 0) return;
  try {
    const alive = await debugAlive();
    if (!alive) return;
    const b = await ensureBrowser();
    const pages = await b.pages();
    const pid = targetProjectId();
    const gptTabs = [];
    for (const p of pages) {
      if (!p || p.isClosed()) continue;
      const u = p.url() || "";
      if (!/^https:\/\/chatgpt\.com\b/i.test(u)) continue;
      const busyDom = await p.evaluate(() => !!document.querySelector('[data-testid="stop-button"], button[aria-label*="Stop"], button[aria-label*="Dừng"]')).catch(() => false);
      if (!busyDom) gptTabs.push(p);
    }
    if (gptTabs.length <= 1) return;
    // Ưu tiên giữ lại 1 Tab đang nằm trong dự án HTPM (hoặc Tab đầu tiên), đóng gọn toàn bộ Tab phụ nhàn rỗi
    const keeper = gptTabs.find((p) => (p.url() || "").includes(`/g/${pid}`)) || gptTabs[0];
    gptSlotPages[0] = keeper;
    keeper.__gptSlotIdx = 0;
    for (let i = 1; i < MAX_CHATGPT_WORKERS; i++) gptSlotPages[i] = null;
    for (const p of gptTabs) {
      if (p !== keeper) {
        try { if (!p.isClosed()) await p.close(); } catch {}
      }
    }
  } catch {}
}

async function releaseGptSlot(slotIdx) {
  const next = waitingGptQueue.shift();
  if (next) {
    next(slotIdx);
    return;
  }
  gptSlotBusy[slotIdx] = false;
  // Nếu toàn bộ các luồng ChatGPT đã xong -> đóng NGAY LẬP TỨC các Tab phụ (#2, #3) & dọn sạch Tab trùng trước khi hàm trả về!
  if (!gptSlotBusy.some(Boolean) && waitingGptQueue.length === 0) {
    for (let i = 1; i < MAX_CHATGPT_WORKERS; i++) {
      if (gptSlotIdleTimers[i]) { clearTimeout(gptSlotIdleTimers[i]); gptSlotIdleTimers[i] = null; }
      if (gptSlotPages[i]) {
        const p = gptSlotPages[i];
        gptSlotPages[i] = null;
        try { if (!p.isClosed()) await p.close(); } catch {}
      }
    }
    await sweepIdleChatgptTabs().catch(() => {});
    return;
  }
  if (slotIdx > 0) {
    if (gptSlotIdleTimers[slotIdx]) clearTimeout(gptSlotIdleTimers[slotIdx]);
    const t = setTimeout(async () => {
      gptSlotIdleTimers[slotIdx] = null;
      if (!gptSlotBusy[slotIdx] && gptSlotPages[slotIdx]) {
        const p = gptSlotPages[slotIdx];
        gptSlotPages[slotIdx] = null;
        try { if (!p.isClosed()) await p.close(); } catch {}
      }
      await sweepIdleChatgptTabs();
    }, 3000);
    if (t.unref) t.unref();
    gptSlotIdleTimers[slotIdx] = t;
  }
}

async function withGptParallelSlot(fn) {
  const slotIdx = await acquireGptSlot();
  try {
    return await fn(slotIdx);
  } finally {
    await releaseGptSlot(slotIdx);
  }
}

async function chatgptSlotPage(slotIdx = 0, create = true) {
  await closeLegacy9334IfOpen().catch(() => {});
  const b = await ensureBrowser();
  let page = gptSlotPages[slotIdx];
  if (page) {
    const alive = !page.isClosed() && (await page.evaluate("1").catch(() => null)) === 1;
    if (!alive) {
      page = null;
      gptSlotPages[slotIdx] = null;
    }
  }
  const pid = targetProjectId();
  if (!page) {
    const pages = await b.pages();
    const taken = new Set(gptSlotPages.filter(Boolean));
    const freeGpt = pages.filter((p) => {
      const u = p.url() || "";
      return /^https:\/\/chatgpt\.com\b/i.test(u) &&
        (p.__gptSlotIdx == null || p.__gptSlotIdx === slotIdx) &&
        !taken.has(p);
    });
    // Ưu tiên Tab đã mở sẵn trong dự án HTPM; nếu không có thì tái sử dụng ngay Tab trang chủ chatgpt.com (tránh đẻ thêm Tab mới sau khi xóa chat!)
    page = freeGpt.find((p) => (p.url() || "").includes(`/g/${pid}`)) ||
      freeGpt.find((p) => /^https:\/\/chatgpt\.com\/?(\?.*)?$/i.test(p.url() || "")) ||
      null;
    if (page && !(page.url() || "").includes(`/g/${pid}`)) {
      await page.goto(targetProjectUrl(), { waitUntil: "domcontentloaded" }).catch(() => {});
    }
  }
  if (!page && create) {
    // Mở Tab HTPM phụ ngầm 100% (background: true) để không bao giờ cướp tiêu điểm chuột của Tab Flow hay Tab ChatGPT khác!
    page = typeof flow.createBackgroundPage === "function"
      ? await flow.createBackgroundPage(b, targetProjectUrl())
      : await b.newPage();
    if (!page.url().includes(`/g/${targetProjectId()}`)) {
      await page.goto(targetProjectUrl(), { waitUntil: "domcontentloaded" }).catch(() => {});
    }
  }
  if (page) {
    page.__gptSlotIdx = slotIdx;
    gptSlotPages[slotIdx] = page;
  }
  return page || null;
}

async function chatgptPage(create = true) {
  return chatgptSlotPage(0, create);
}

async function inject(page) {
  const src = fs.readFileSync(path.join(__dirname, "chatgpt-page-driver.js"), "utf8");
  await page.evaluate(src);
}

async function show() {
  const page = await chatgptPage(true);
  await flow.ensureWindowOnScreen(page);
  await page.bringToFront();
  return true;
}

function buildDirectivePrompt(userPrompt, ratio) {
  const specMap = {
    "9:16": "vertical portrait 9:16 aspect ratio (1024x1536)",
    "2:3": "vertical portrait 2:3 aspect ratio (1024x1536)",
    "3:4": "vertical portrait 3:4 aspect ratio (1024x1536)",
    "16:9": "horizontal widescreen 16:9 aspect ratio (1536x1024)",
    "3:2": "horizontal landscape 3:2 aspect ratio (1536x1024)",
    "4:3": "horizontal landscape 4:3 aspect ratio (1536x1024)",
    "1:1": "square 1:1 aspect ratio (1024x1024)",
  };
  const ratioDesc = specMap[ratio] || specMap["1:1"];
  return `Generate a high-resolution image directly in ${ratioDesc}. Do not ask follow-up questions and do not output conversational filler—create the image right away based on the prompt below:\n\n${userPrompt}`;
}

async function uploadReferenceImages(page, images) {
  if (!images || !images.length) return null;
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "chatgpt-refs-"));
  const filePaths = [];
  for (let i = 0; i < images.length; i++) {
    const im = images[i];
    const safeName = (im.name || `ref_${i + 1}.png`).replace(/[^a-zA-Z0-9._-]/g, "_");
    const fp = path.join(tmpDir, safeName);
    fs.writeFileSync(fp, Buffer.from(im.base64, "base64"));
    filePaths.push(fp);
  }

  // Tìm <input type="file"> sẵn có trên trang ChatGPT (ưu tiên ô có thuộc tính multiple cho phép đính kèm 2+ ảnh cùng lúc)
  const findFileInput = async () => {
    let h = await page.$('input[type="file"][multiple]');
    if (!h) h = await page.$('input[type="file"]');
    if (!h) {
      await page.evaluate(() => {
        window.__chatgptFileCap.on = true;
        window.__chatgptFileCap.input = null;
        const plus =
          document.querySelector('[data-testid="composer-plus-btn"]') ||
          [...document.querySelectorAll("button")].find((b) =>
            /attach|upload|add files|thêm tệp|đính kèm/i.test(b.getAttribute("aria-label") || b.innerText || "")
          );
        if (plus) plus.click();
      });
      await sleep(600);
      await page.evaluate(() => {
        window.__chatgptFileCap.on = false;
      });
      h = (await page.$('input[type="file"][multiple]')) || (await page.$('input[type="file"]'));
    }
    return h;
  };

  let inputHandle = await findFileInput();
  if (!inputHandle) {
    try {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    } catch {}
    throw new Error("Không tìm thấy ô đính kèm ảnh trên trang ChatGPT (hãy kiểm tra bạn đã đăng nhập tài khoản ChatGPT).");
  }

  if (filePaths.length === 1) {
    await inputHandle.uploadFile(filePaths[0]);
  } else {
    // Hỗ trợ đính kèm nhiều ảnh tham chiếu (2+ ảnh mới + cũ) trên ChatGPT không bao giờ lỗi <input multiple>
    const isMulti = await inputHandle.evaluate((el) => !!el.multiple).catch(() => false);
    if (isMulti) {
      await inputHandle.uploadFile(...filePaths);
    } else {
      for (let k = 0; k < filePaths.length; k++) {
        const hEach = (k === 0 ? inputHandle : await findFileInput()) || inputHandle;
        await hEach.uploadFile(filePaths[k]);
        await sleep(800);
      }
    }
  }
  // Chờ ảnh tải lên hoàn tất (tối đa 35 giây)
  for (let i = 0; i < 70; i++) {
    await sleep(500);
    await inject(page).catch(() => {});
    const settled = await page.evaluate(() => window.__chatgptUi.uploadsSettled()).catch(() => true);
    if (settled && i >= 3) break;
  }
  return tmpDir;
}

async function downloadImageFromChatGPT(page, url) {
  // Tầng 1: tải ngay trong ngữ cảnh trang bằng fetch credentials:include (hỗ trợ cả blob: và oaiusercontent)
  try {
    await inject(page);
    const res = await page.evaluate((u) => window.__chatgptUi.fetchImageAsBase64(u), url);
    if (res && res.base64) {
      const buf = Buffer.from(res.base64, "base64");
      if (buf.length > 4096) return { data: buf, mime: res.mime || "image/png" };
    }
  } catch (e) {
    console.log("[chatgpt] in-page fetch fallback:", e.message || e);
  }

  // Tầng 2: tải từ Node kèm cookie của trình duyệt (vượt CORS nếu CDN đổi tên miền)
  const cookies = await page.cookies(url, HOME);
  const res = await fetch(url, {
    headers: {
      Cookie: cookies.map((c) => `${c.name}=${c.value}`).join("; "),
      Referer: HOME,
      "User-Agent": await page.browser().userAgent(),
    },
  });
  if (!res.ok) throw new Error("Tải ảnh từ ChatGPT thất bại: HTTP " + res.status);
  return {
    data: Buffer.from(await res.arrayBuffer()),
    mime: res.headers.get("content-type") || "image/png",
  };
}

async function navigateToTargetProject(page) {
  const knownPid = targetProjectId();
  const projUrl = `https://chatgpt.com/g/${knownPid}/project`;
  const curUrl = page.url() || "";

  // Luôn bắt đầu mỗi lượt tạo ảnh bằng 1 phiên trống mới tinh ngay tại trang chủ Dự án HTPM (/g/<pid>/project, không có /c/...)
  // để: (1) 100% cuộc trò chuyện nằm gọn trong dự án HTPM, (2) không bị lẫn ngữ cảnh ảnh cũ, và (3) xóa sạch sau khi tải xong mà không ảnh hưởng lịch sử khác!
  const isFreshProjectHome = curUrl.includes(`/g/${knownPid}/project`) && !/\/c\/[0-9a-f-]{36}/i.test(curUrl);
  if (isFreshProjectHome) {
    await inject(page).catch(() => {});
    const st = await page.evaluate(() => window.__chatgptUi?.inspectState()).catch(() => null);
    if (st?.ready && (st.totalTurns || 0) === 0) {
      return;
    }
  }

  await page.goto(projUrl, { waitUntil: "domcontentloaded" }).catch(() => {});
}

async function cleanupConversationAfterDownload(page, job) {
  if (job && job.keepChat === true) return;
  const projUrl = targetProjectUrl();
  try {
    await sleep(350);
    await inject(page).catch(() => {});
    const delRes = await page.evaluate(() => window.__chatgptUi?.deleteCurrentConversation?.()).catch(() => null);
    if (delRes?.deleted) {
      console.log(`[chatgpt] đã tự động xóa đoạn chat tạm trong dự án HTPM để làm sạch bộ nhớ (${delRes.method}).`);
    }
  } catch (e) {
    console.log("[chatgpt] lưu ý khi dọn đoạn chat tạm:", e.message || e);
  } finally {
    // Đưa tab quay sẵn về trang trống của dự án HTPM cho lượt tạo tiếp theo
    await page.goto(projUrl, { waitUntil: "domcontentloaded" }).catch(() => {});
  }
}

async function generateOneImage(job, slotIdx = 0) {
  const tag = `[chatgpt:Tab#${slotIdx + 1}/${MAX_CHATGPT_WORKERS}]`;
  console.log(`${tag} bắt đầu tạo ảnh song song trong dự án HTPM (Brave chính 9333)`);
  const { page, prevAssistantCount, t0 } = await flow.withUiFocusLock(async () => {
    const p = await chatgptSlotPage(slotIdx, true);
    await p.bringToFront().catch(() => {});

    // Mở trong dự án HTPM (tự động gom gọn cuộc trò chuyện vào dự án thay vì tràn ra ngoài lịch sử chính)
    await navigateToTargetProject(p);

    let readyState = null;
    for (let i = 0; i < 40; i++) {
      await sleep(500);
      await inject(p).catch(() => {});
      readyState = await p.evaluate(() => window.__chatgptUi?.inspectState()).catch(() => null);
      if (readyState?.needManualAuth) {
        await p.bringToFront().catch(() => {});
        throw new Error(
          "Cần đăng nhập ChatGPT (1 lần duy nhất trong Tab ChatGPT của cửa sổ Brave chung): sau khi đăng nhập xong tại chatgpt.com, bấm Tạo lại trên Canvas."
        );
      }
      if (readyState?.ready) break;
    }

    if (!readyState?.ready) {
      await p.bringToFront().catch(() => {});
      throw new Error("Không thấy ô nhập prompt trên chatgpt.com. Hãy kiểm tra Tab ChatGPT trong cửa sổ Brave.");
    }

    const prevCount = readyState.turnCount || 0;
    let tmpDir = null;
    try {
      if (job.images && job.images.length) {
        console.log(`[chatgpt] tải lên ${job.images.length} ảnh tham chiếu...`);
        tmpDir = await uploadReferenceImages(p, job.images);
      }

      // Nhấp vào ô nhập bằng chuột thật rồi điền toàn bộ prompt qua CDP Input.insertText
      await inject(p);
      const compCenter = await p.evaluate(() => window.__chatgptUi.getComposerCenter());
      if (compCenter) {
        await p.mouse.click(compCenter.x, compCenter.y);
        await sleep(150);
      }

      const fullPrompt = buildDirectivePrompt(job.prompt || "", job.ratio || "1:1");
      const cdp = await p.target().createCDPSession();
      try {
        await p.keyboard.down("Control");
        await p.keyboard.press("KeyA");
        await p.keyboard.up("Control");
        await p.keyboard.press("Backspace");
        await sleep(100);
        await cdp.send("Input.insertText", { text: fullPrompt });
      } finally {
        await cdp.detach().catch(() => {});
      }

      await sleep(500);
      await inject(p);
      const sendPos = await p.evaluate(() => window.__chatgptUi.getSendCenter());
      if (sendPos) {
        await p.bringToFront().catch(() => {});
        await p.mouse.click(sendPos.x, sendPos.y);
      } else {
        await p.keyboard.press("Enter");
      }
      return { page: p, prevAssistantCount: prevCount, t0: Date.now() };
    } finally {
      if (tmpDir) {
        try {
          fs.rmSync(tmpDir, { recursive: true, force: true });
        } catch {}
      }
    }
  });

  const timeoutMs = (job.timeoutMin || 6) * 60 * 1000;
  console.log("[chatgpt] đã gửi lệnh tạo ảnh (đã nhả khóa chuột cho Tab Flow), đang chờ ChatGPT kết xuất ngầm...");

  for (;;) {
    await sleep(2500);
    if (Date.now() - t0 > timeoutMs) {
      await cleanupConversationAfterDownload(page, job).catch(() => {});
      throw new Error("Hết thời gian chờ ChatGPT tạo ảnh (quá 6 phút).");
    }
    await inject(page).catch(() => {});
    const authCheck = await page.evaluate(() => window.__chatgptUi?.inspectState()).catch(() => null);
    if (authCheck?.needManualAuth) {
      await page.bringToFront().catch(() => {});
      throw new Error("Trình duyệt ChatGPT yêu cầu đăng nhập lại hoặc xác nhận thủ công. Hãy kiểm tra cửa sổ trình duyệt rồi thử lại.");
    }

    const st = await page
      .evaluate((arg) => window.__chatgptUi.poll(arg), { prevAssistantCount, t0 })
      .catch(() => null);
    if (!st) continue;
    if (st.state === "failed") {
      await cleanupConversationAfterDownload(page, job);
      throw new Error(st.error || "ChatGPT báo lỗi khi tạo ảnh.");
    }
    if (st.state === "done" && st.images && st.images.length > 0) {
      await sleep(1500);
      await inject(page).catch(() => {});
      const finalSt = await page
        .evaluate((arg) => window.__chatgptUi.poll(arg), { prevAssistantCount, t0 })
        .catch(() => st);
      const imgs = finalSt?.images?.length ? finalSt.images : st.images;
      const out = [];
      for (const img of imgs) {
        out.push(await downloadImageFromChatGPT(page, img.url));
      }
      console.log(`[chatgpt] xong, đã tải ${out.length} ảnh (${out[0]?.data?.length || 0} bytes)`);
      await cleanupConversationAfterDownload(page, job);
      return out;
    }
  }
}

async function generateImages(job) {
  const want = Math.min(4, Math.max(1, Number(job.count) || 1));
  if (want === 1) {
    const batch = await withGptParallelSlot((slotIdx) => generateOneImage(job, slotIdx));
    return batch.slice(0, 1);
  }
  // Nếu yêu cầu nhiều ảnh (count = 2..4), chia ra nhiều Tab HTPM chạy song song cùng lúc!
  const tasks = Array.from({ length: want }, () =>
    withGptParallelSlot((slotIdx) => generateOneImage({ ...job, count: 1 }, slotIdx))
  );
  const batches = await Promise.all(tasks);
  return batches.flat().slice(0, want);
}

const inQueue = (fn) => {
  const p = queue.then(fn);
  queue = p.catch(() => {});
  return p;
};

async function status() {
  const alive = !!(await debugAlive());
  const page = alive ? await chatgptPage(false).catch(() => null) : null;
  let loggedIn = null;
  if (page) {
    try {
      await inject(page);
      const st = await page.evaluate(() => window.__chatgptUi?.inspectState());
      loggedIn = st ? !st.needManualAuth : null;
    } catch {}
  }
  return {
    browserOpen: alive,
    loggedIn,
    accounts: store.accounts.map((a) => ({
      id: a.id,
      name: a.name,
      active: a.id === store.active,
    })),
  };
}

function switchAccount(id) {
  return inQueue(async () => {
    if (!store.accounts.some((a) => a.id === id) || id === store.active) return;
    store.active = id;
    saveConfig();
    await stopOwnBrowser();
    onChange();
  });
}

function addAccount() {
  return inQueue(async () => {
    const n = store.accounts.length + 1;
    const id = "gpt" + Date.now().toString(36);
    store.accounts.push({ id, name: "ChatGPT " + n, profile: "chatgpt-browser-profile-" + id });
    store.active = id;
    saveConfig();
    await stopOwnBrowser();
    onChange();
    await show();
  });
}

function removeAccount(id) {
  return inQueue(async () => {
    if (store.accounts.length <= 1 || !store.accounts.some((a) => a.id === id)) return;
    const wasActive = id === store.active;
    store.accounts = store.accounts.filter((x) => x.id !== id);
    if (wasActive) {
      store.active = store.accounts[0].id;
      await stopOwnBrowser();
    }
    saveConfig();
    onChange();
  });
}

function renameAccount(id, name) {
  const a = store.accounts.find((x) => x.id === id);
  if (a && String(name || "").trim()) {
    a.name = String(name).trim();
    saveConfig();
    onChange();
  }
}

function openAccount(id) {
  return inQueue(async () => {
    if (!store.accounts.some((a) => a.id === id)) return;
    if (id !== store.active) {
      store.active = id;
      saveConfig();
      await stopOwnBrowser();
      onChange();
    }
    await show();
  });
}

function setup(app) {
  userData = app.getPath("userData");
  configPath = path.join(userData, "chatgpt-driver.json");
  loadConfig();
  closeLegacy9334IfOpen().catch(() => {});

  ipcMain.handle("chatgpt:status", () => status());
  ipcMain.handle("chatgpt:accounts", () => status());
  ipcMain.handle("chatgpt:switch-account", (_e, id) => switchAccount(id).then(status));
  ipcMain.handle("chatgpt:add-account", () => addAccount().then(status));
  ipcMain.handle("chatgpt:remove-account", (_e, id) => removeAccount(id).then(status));
  ipcMain.handle("chatgpt:rename-account", (_e, id, name) => {
    renameAccount(id, name);
    return status();
  });
  ipcMain.handle("chatgpt:open-account", (_e, id) => openAccount(id).then(status));
  ipcMain.handle("chatgpt:show", () =>
    show().catch((e) => {
      dialog.showErrorBox("ChatGPT", String(e.message || e));
      return false;
    })
  );
  ipcMain.handle("chatgpt:generate-image", async (_e, job) => {
    const reqJob = job || {};
    let lastGptErr = null;
    // BẮT BUỘC thử tối đa 2 lần liên tiếp trên chính ChatGPT (dự án HTPM) trước khi được phép chuyển sang Flow dự phòng!
    // (Chỉ nhảy ngay sang Flow ở lần 1 nếu ChatGPT báo rõ ràng đã chạm trần giới hạn lượt tạo tài khoản).
    for (let attempt = 1; attempt <= 2; attempt++) {
      try {
        const items = await generateImages(reqJob);
        return { ok: true, provider: "chatgpt", items, data: items[0].data, mime: items[0].mime };
      } catch (e) {
        lastGptErr = e;
        const msg = String(e?.message || e);
        const isHardLimit = /chạm giới hạn lượt tạo|reached your.*limit|đạt đến giới hạn|too many requests|Cần đăng nhập ChatGPT/i.test(msg);
        if (isHardLimit || attempt === 2) break;
        console.warn(`[chatgpt] Lần thử #1 gặp trục trặc tạm thời (${msg}) -> thử lại lần #2 ngay trên ChatGPT trước khi xét dự phòng!`);
        await sleep(1500);
      }
    }
    const gptErr = lastGptErr || new Error("ChatGPT không phản hồi.");
    {
      if (reqJob.noFallback === true) {
        return { ok: false, error: String(gptErr.message || gptErr) };
      }
      console.warn("[chatgpt -> flow fallback] Cả 2 lần thử ChatGPT đều không tạo được ảnh, mới tự động chuyển sang dự phòng Google Flow / Gemini:", gptErr.message || gptErr);
      try {
        // Tầng 2 (Dự phòng): Google Flow / Gemini Image (Nano Banana)
        if (typeof flow.generateImageFallback === "function") {
          const flowItems = await flow.generateImageFallback({
            prompt: reqJob.prompt || "",
            ratio: reqJob.ratio || "1:1",
            count: reqJob.count || 1,
            images: reqJob.images || [],
          });
          if (flowItems && flowItems.length) {
            return { ok: true, provider: "flow-fallback", items: flowItems, data: flowItems[0].data, mime: flowItems[0].mime };
          }
        }
      } catch (flowErr) {
        console.warn("[flow -> muse fallback] Google Flow cũng gặp lỗi, tự động chuyển sang dự phòng cuối Muse:", flowErr.message || flowErr);
        try {
          // Tầng 3 (Dự phòng cuối): Muse2API cục bộ (:18610)
          const keyPath = path.resolve(__dirname, "..", "muse2api", "data", "api_key");
          const museKey = fs.existsSync(keyPath) ? fs.readFileSync(keyPath, "utf8").trim() : "";
          const sizeMap = { "9:16": "1024x1792", "16:9": "1792x1024", "1:1": "1024x1024" };
          const r = await fetch("http://127.0.0.1:18610/v1/images/generations", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...(museKey ? { Authorization: `Bearer ${museKey}` } : {}),
            },
            body: JSON.stringify({
              model: "muse-image",
              prompt: reqJob.prompt || "",
              n: Math.min(4, Math.max(1, Number(reqJob.count) || 1)),
              size: sizeMap[reqJob.ratio] || "1024x1024",
              response_format: "b64_json",
            }),
          });
          if (r.ok) {
            const j = await r.json();
            const museItems = (j.data || [])
              .map((d) => (d.b64_json ? { data: Buffer.from(d.b64_json, "base64"), mime: "image/png" } : null))
              .filter(Boolean);
            if (museItems.length) {
              return { ok: true, provider: "muse-fallback", items: museItems, data: museItems[0].data, mime: museItems[0].mime };
            }
          }
        } catch {}
        return {
          ok: false,
          error: `Cả ChatGPT -> Flow -> Muse đều lỗi. Lỗi ChatGPT: ${gptErr.message || gptErr} | Lỗi Flow: ${flowErr.message || flowErr}`,
        };
      }
      return { ok: false, error: String(gptErr.message || gptErr) };
    }
  });
}

function destroy() {
  // Dùng chung phiên trình duyệt Brave 9333 do flow-driver quản lý
}

module.exports = { setup, destroy, show, generateImages, sweepIdleChatgptTabs };
