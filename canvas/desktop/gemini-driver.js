// Điều khiển Gemini Web Video (https://gemini.google.com/u/<n>/videos) trên CÙNG CỬA SỔ TRÌNH DUYỆT BRAVE (:9333)
// chung với Google Flow & ChatGPT:
// - Hỗ trợ thời lượng 10 giây (10s) & 15 giây (15s), tỷ lệ Ngang (16:9) & Dọc (9:16), kèm ảnh tham chiếu.
// - Tự động quét TẤT CẢ các tài khoản Google Pro/Ultra đang đăng nhập trong Brave (u/0, u/1, u/2, ...).
// - Khi một tài khoản chạm giới hạn lượt tạo video trong ngày -> tự động xoay ngay sang tài khoản Pro tiếp theo!
// - Chỉ khi TẤT CẢ các tài khoản Gemini Pro trong Brave đều không tạo thêm được nữa mới tự động chuyển qua Google Flow -> Muse!
const _electron = (() => {
  try {
    const e = require("electron");
    return e && typeof e === "object" ? e : {};
  } catch {
    return {};
  }
})();
const { ipcMain, dialog } = _electron;
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const flow = require("./flow-driver");

const GEMINI_HOME = "https://gemini.google.com/";
const QUOTA_COOLDOWN_MS = 6 * 3600 * 1000; // tạm nghỉ 6 giờ cho nick đã hết lượt tạo video trong ngày
const MAX_SCAN_NICKS = 10; // quét tối đa u/0 .. u/9

let userData = "";
let configPath = "";
let store = {
  accounts: [], // [{ prefix: "u/0/", email: "...", exhaustedUntil: 0, lastUsedAt: 0, lastError: "" }]
  activePrefix: "",
  lastScanAt: 0,
};

let geminiTab = null;
let geminiIdleTimer = null;
let jobMutex = Promise.resolve();

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function withGeminiJobLock(fn) {
  const next = jobMutex.then(fn, fn);
  jobMutex = next.catch(() => {});
  return next;
}

function resolveDefaultConfigPath() {
  if (configPath) return configPath;
  const appData = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
  const dir = path.join(appData, "infinite-canvas-flow");
  fs.mkdirSync(dir, { recursive: true });
  configPath = path.join(dir, "gemini-driver.json");
  return configPath;
}

function loadConfig() {
  const fp = resolveDefaultConfigPath();
  try {
    const raw = JSON.parse(fs.readFileSync(fp, "utf8"));
    if (raw && Array.isArray(raw.accounts)) {
      store = {
        accounts: raw.accounts,
        activePrefix: raw.activePrefix || "",
        lastScanAt: raw.lastScanAt || 0,
      };
    }
  } catch {}
}

function saveConfig() {
  const fp = resolveDefaultConfigPath();
  try {
    fs.writeFileSync(fp, JSON.stringify(store, null, 2));
  } catch {}
}

function videosUrlForPrefix(prefix = "u/0/") {
  const clean = String(prefix || "u/0/").replace(/^\/+|\/+$/g, "");
  return `${GEMINI_HOME}${clean}/videos`;
}

async function inject(page) {
  const src = fs.readFileSync(path.join(__dirname, "gemini-page-driver.js"), "utf8");
  await page.evaluate(src);
}

function isAccountExhausted(acc) {
  if (!acc || !acc.exhaustedUntil) return false;
  if (Date.now() > acc.exhaustedUntil) {
    delete acc.exhaustedUntil;
    delete acc.lastQuotaReason;
    saveConfig();
    return false;
  }
  return true;
}

function markAccountExhausted(prefix, email, reason = "") {
  let acc = store.accounts.find(
    (a) => (email && a.email === email) || a.prefix === prefix
  );
  if (!acc) {
    acc = { prefix, email: email || "" };
    store.accounts.push(acc);
  }
  acc.exhaustedUntil = Date.now() + QUOTA_COOLDOWN_MS;
  acc.lastQuotaReason = String(reason || "").slice(0, 240);
  acc.updatedAt = Date.now();
  saveConfig();
  console.warn(
    `[gemini:AutoSwitch] Tài khoản ${acc.email || acc.prefix} (${acc.prefix}) đã hết lượt tạo video -> tự động xoay sang tài khoản Pro tiếp theo!`
  );
}

function markAccountHealthy(prefix, email) {
  let acc = store.accounts.find(
    (a) => (email && a.email === email) || a.prefix === prefix
  );
  if (!acc) {
    acc = { prefix, email: email || "" };
    store.accounts.push(acc);
  }
  if (email) acc.email = email;
  acc.prefix = prefix;
  delete acc.exhaustedUntil;
  delete acc.lastQuotaReason;
  acc.lastUsedAt = Date.now();
  acc.videosGenerated = (acc.videosGenerated || 0) + 1;
  store.activePrefix = prefix;
  saveConfig();
}

async function closeIdleGeminiTabsNow() {
  if (geminiIdleTimer) {
    clearTimeout(geminiIdleTimer);
    geminiIdleTimer = null;
  }
  try {
    const alive = await flow.debugAlive();
    if (!alive) return;
    const b = await flow.ensureBrowser({ visible: true });
    const pages = await b.pages();
    const idleGemTabs = [];
    for (const p of pages) {
      if (!p || p.isClosed()) continue;
      const u = p.url() || "";
      if (!/^https:\/\/gemini\.google\.com\b/i.test(u)) continue;
      // Chỉ đóng các tab /videos tự động do driver mở, không đóng tab hội thoại riêng của người dùng!
      if (/\/videos(\?.*)?$/i.test(u) || p === geminiTab) idleGemTabs.push(p);
    }
    if (idleGemTabs.length === 0) return;
    const otherCount = pages.filter((p) => p && !p.isClosed() && !idleGemTabs.includes(p)).length;
    if (otherCount === 0 && typeof flow.createBackgroundPage === "function") {
      await flow.createBackgroundPage(b, "chrome://newtab/").catch(() => {});
    }
    geminiTab = null;
    for (const p of idleGemTabs) {
      await p.close().catch(() => {});
    }
  } catch {}
}

function scheduleIdleCleanup() {
  return closeIdleGeminiTabsNow();
}

async function ensureGeminiWorkerPage(create = true) {
  const b = await flow.ensureBrowser({ visible: true });
  if (geminiTab) {
    const alive = !geminiTab.isClosed() && (await geminiTab.evaluate("1").catch(() => null)) === 1;
    if (!alive) geminiTab = null;
  }
  if (!geminiTab) {
    const pages = await b.pages();
    // Chỉ tái sử dụng tab đang ở trang trống /videos (không lấy tab /app/... đang mở hội thoại riêng của người dùng!)
    geminiTab =
      pages.find((p) => /^https:\/\/gemini\.google\.com\/(?:u\/\d+\/)?videos(\?.*)?$/i.test(p.url() || "")) ||
      null;
  }
  if (!geminiTab && create) {
    geminiTab = await b.newPage();
  }
  return geminiTab;
}

// Tự động quét toàn bộ các tài khoản Google đang đăng nhập trong Brave (u/0, u/1, u/2, ...)
// để lập danh sách xoay vòng đầy đủ các nick Pro/Ultra!
async function discoverGeminiAccounts({ forceResetCooldown = false } = {}) {
  loadConfig();
  const b = await flow.ensureBrowser({ visible: true });
  const prevByEmail = new Map();
  for (const oldAcc of store.accounts || []) {
    if (oldAcc.email) prevByEmail.set(oldAcc.email.toLowerCase(), oldAcc);
  }

  const discovered = [];
  const seenEmails = new Set();
  const seenPrefixes = new Set();
  let duplicateOrUnauthStreak = 0;

  await flow.withUiFocusLock(async () => {
    const probePage = await b.newPage();
    try {
      await probePage.bringToFront().catch(() => {});
      for (let idx = 0; idx < MAX_SCAN_NICKS; idx++) {
        const reqPrefix = `u/${idx}/`;
        await probePage
          .goto(videosUrlForPrefix(reqPrefix), { waitUntil: "domcontentloaded", timeout: 20000 })
          .catch(() => {});

        let st = null;
        for (let w = 0; w < 22; w++) {
          await sleep(380);
          const curUrl = probePage.url() || "";
          if (/accounts\.google\.com|\/ServiceLogin/i.test(curUrl)) {
            st = { needManualAuth: true };
            break;
          }
          await inject(probePage).catch(() => {});
          st = await probePage.evaluate(() => window.__geminiUi?.inspectState()).catch(() => null);
          if (st?.needManualAuth) break;
          if (st?.ready && st?.email && (st.hasVideoTool || w >= 6)) break;
        }

        if (!st || st.needManualAuth) {
          duplicateOrUnauthStreak++;
          if (idx >= 2 && duplicateOrUnauthStreak >= 3) break;
          continue;
        }

        const realPrefix = st.userPrefix || reqPrefix;
        const email = (st.email || "").toLowerCase();
        const dedupKey = email || realPrefix;
        if (seenEmails.has(dedupKey) || seenPrefixes.has(realPrefix)) {
          duplicateOrUnauthStreak++;
          if (idx >= 2 && duplicateOrUnauthStreak >= 3) break;
          continue;
        }

        duplicateOrUnauthStreak = 0;
        if (email) seenEmails.add(email);
        seenPrefixes.add(realPrefix);

        const prev = email ? prevByEmail.get(email) : null;
        const entry = {
          prefix: realPrefix,
          email,
          hasVideoTool: Boolean(st.hasVideoTool),
          videosGenerated: prev?.videosGenerated || 0,
          lastUsedAt: prev?.lastUsedAt || 0,
          ...(!forceResetCooldown && prev?.exhaustedUntil ? { exhaustedUntil: prev.exhaustedUntil } : {}),
          ...(!forceResetCooldown && prev?.lastQuotaReason ? { lastQuotaReason: prev.lastQuotaReason } : {}),
        };
        if (st.immediateQuota) {
          entry.exhaustedUntil = Date.now() + QUOTA_COOLDOWN_MS;
          entry.lastQuotaReason = st.immediateQuotaText || "Đã hết lượt tạo video";
        }
        discovered.push(entry);
      }
    } finally {
      await probePage.close().catch(() => {});
    }
  });

  if (discovered.length > 0) {
    discovered.sort((a, b) => a.prefix.localeCompare(b.prefix, undefined, { numeric: true }));
    store.accounts = discovered;
    store.lastScanAt = Date.now();
    if (!store.activePrefix || !discovered.some((x) => x.prefix === store.activePrefix)) {
      store.activePrefix = discovered[0].prefix;
    }
    saveConfig();
    console.log(
      `[gemini] Đã phát hiện ${discovered.length} tài khoản Google trong Brave: ` +
        discovered.map((a) => `${a.email || a.prefix} (${a.prefix})`).join(", ")
    );
  }
  return store.accounts;
}

async function getCandidateAccounts() {
  loadConfig();
  const staleScan = !store.accounts.length || Date.now() - (store.lastScanAt || 0) > 30 * 60 * 1000;
  if (staleScan) {
    await discoverGeminiAccounts().catch((e) =>
      console.warn("[gemini] quét danh sách nick:", e.message || e)
    );
  }

  let healthy = store.accounts.filter((a) => !isAccountExhausted(a));
  if (healthy.length === 0) {
    // Quét lại Brave một lần nữa phòng trường hợp người dùng vừa đăng nhập thêm nick Google Pro mới!
    await discoverGeminiAccounts().catch(() => {});
    healthy = store.accounts.filter((a) => !isAccountExhausted(a));
  }

  // Sắp xếp đưa activePrefix lên đầu
  const active = store.activePrefix;
  return [...healthy].sort((a, b) => {
    if (a.prefix === active && b.prefix !== active) return -1;
    if (b.prefix === active && a.prefix !== active) return 1;
    return 0;
  });
}

async function uploadReferenceImagesToGemini(page, images) {
  if (!images || !images.length) return null;
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "gemini-refs-"));
  const filePaths = [];
  // Gemini Video nhận tốt nhất 1-3 ảnh tham chiếu rõ nét
  const sliceImgs = images.slice(0, 3);
  for (let i = 0; i < sliceImgs.length; i++) {
    const im = sliceImgs[i];
    const safeName = (im.name || `ref_${i + 1}.png`).replace(/[^a-zA-Z0-9._-]/g, "_");
    const fp = path.join(tmpDir, safeName);
    fs.writeFileSync(fp, Buffer.from(im.base64, "base64"));
    filePaths.push(fp);
  }

  await inject(page);
  const beforeAttachments = await page.evaluate(() => window.__geminiUi.countComposerAttachments()).catch(() => 0);

  // Mở menu '+' một lần để Gemini gắn thẻ <input type="file" accept="image/*,video/*"> vào DOM, rồi đóng menu và nạp thẳng file!
  let uploaded = false;
  let imgInput = await page.$('input[type="file"][accept*="image"]');
  if (!imgInput) {
    await page.evaluate(async () => {
      const vis = (el) => {
        const rc = el.getBoundingClientRect();
        return rc.width > 2 && rc.height > 2;
      };
      const root = document.querySelector("input-area-v2") || document.body;
      const plusBtn = [...root.querySelectorAll("button")].find(
        (b) =>
          vis(b) &&
          /Upload|Nội dung tải lên|Tải lên|Add files|Thêm tệp/i.test(
            (b.getAttribute("aria-label") || "") + " " + (b.innerText || "")
          )
      );
      if (plusBtn) plusBtn.click();
    });
    await sleep(650);
    imgInput = await page.$('input[type="file"][accept*="image"]');
    await page.keyboard.press("Escape").catch(() => {});
    await sleep(250);
  }

  if (imgInput) {
    await imgInput.uploadFile(...filePaths);
    uploaded = true;
  }

  // Dự phòng cuối: Dán ảnh đầu tiên qua ClipboardEvent DataTransfer vào .ql-editor
  if (!uploaded && sliceImgs[0]) {
    await page.evaluate(
      async ({ b64, mime, name }) => {
        const ed = document.querySelector('rich-textarea .ql-editor[contenteditable="true"]');
        if (!ed) return false;
        ed.focus();
        const bin = atob(b64);
        const arr = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
        const file = new File([arr], name || "reference.png", { type: mime || "image/png" });
        const dt = new DataTransfer();
        dt.items.add(file);
        ed.dispatchEvent(new ClipboardEvent("paste", { bubbles: true, cancelable: true, clipboardData: dt }));
        return true;
      },
      { b64: sliceImgs[0].base64, mime: sliceImgs[0].mime || "image/png", name: sliceImgs[0].name || "ref_1.png" }
    );
    uploaded = true;
  }

  if (!uploaded) {
    fs.rmSync(tmpDir, { recursive: true, force: true });
    throw new Error("Không đính kèm được ảnh tham chiếu lên khung tạo video của Gemini.");
  }

  // Chờ ảnh tham chiếu tải xong hoàn toàn (phải thấy thumbnail đính kèm tăng lên VÀ hết vòng xoay tiến trình!)
  let attachedConfirmed = false;
  for (let i = 0; i < 60; i++) {
    await sleep(500);
    await inject(page).catch(() => {});
    const settled = await page.evaluate(() => window.__geminiUi.uploadsSettled()).catch(() => true);
    const curAttachments = await page.evaluate(() => window.__geminiUi.countComposerAttachments()).catch(() => 0);
    if (curAttachments > beforeAttachments && settled && i >= 3) {
      attachedConfirmed = true;
      break;
    }
  }
  if (!attachedConfirmed) {
    console.warn("[gemini] Lưu ý: chưa xác nhận được thumbnail tăng lên sau 30s, tiếp tục gửi...");
  }
  await sleep(600);
  return tmpDir;
}

async function downloadCompletedGeminiVideo(page, prevResponseCount) {
  const b = page.browser();
  const dlDir = fs.mkdtempSync(path.join(os.tmpdir(), "gemini-mp4-"));
  const browserCdp = await b.target().createCDPSession();
  try {
    await flow.withUiFocusLock(async () => {
      await page.bringToFront().catch(() => {});
      await browserCdp.send("Browser.setDownloadBehavior", {
        behavior: "allow",
        downloadPath: dlDir,
        eventsEnabled: true,
      });
      await inject(page);
      const clickRes = await page.evaluate(
        (prevCnt) => window.__geminiUi.clickDownloadVideoInLatest(prevCnt),
        prevResponseCount
      );
      if (!clickRes?.clicked) {
        throw new Error("Không tìm thấy nút Download video trên Gemini.");
      }
      await sleep(600);
    });

    let lastSize = -1;
    let stableTicks = 0;
    for (let i = 0; i < 80; i++) {
      await sleep(500);
      const files = fs
        .readdirSync(dlDir)
        .filter((f) => !f.endsWith(".crdownload") && !f.endsWith(".tmp") && !f.startsWith("."));
      if (files.length > 0) {
        const fp = path.join(dlDir, files[0]);
        const st = fs.statSync(fp);
        if (st.size > 32768) {
          if (st.size === lastSize) {
            stableTicks++;
            if (stableTicks >= 2) {
              const data = fs.readFileSync(fp);
              // Xác thực header MP4 hợp lệ (ftyp ở byte 4..8)
              const magic = data.subarray(4, 8).toString("ascii");
              if (magic !== "ftyp" && data.subarray(0, 12).toString("utf8").includes("<html")) {
                throw new Error("Tệp tải về là trang HTML thay vì MP4 hợp lệ.");
              }
              return { data, mime: "video/mp4" };
            }
          } else {
            lastSize = st.size;
            stableTicks = 0;
          }
        }
      }
    }
    throw new Error("Quá thời gian chờ tải tệp MP4 từ Gemini về ổ đĩa.");
  } finally {
    await browserCdp.send("Browser.setDownloadBehavior", { behavior: "default" }).catch(() => {});
    await browserCdp.detach().catch(() => {});
    try {
      fs.rmSync(dlDir, { recursive: true, force: true });
    } catch {}
  }
}

async function cleanupTemporaryGeminiChat(page, createdConvId, prefix, keepChat = false) {
  if (keepChat || !createdConvId) return;
  try {
    await flow.withUiFocusLock(async () => {
      await page.bringToFront().catch(() => {});
      await inject(page).catch(() => {});
      const del = await page
        .evaluate((cid) => window.__geminiUi?.deleteSpecificConversation?.(cid), createdConvId)
        .catch(() => null);
      if (del?.deleted) {
        console.log(`[gemini] Đã tự động xóa đoạn chat video tạm (/app/${createdConvId}) trên ${prefix}.`);
      }
    });
  } catch (e) {
    console.log("[gemini] lưu ý khi dọn đoạn chat tạm:", e.message || e);
  } finally {
    await page.goto(videosUrlForPrefix(prefix), { waitUntil: "domcontentloaded" }).catch(() => {});
  }
}

async function generateOneVideoOnAccount(job, acc) {
  const prefix = acc.prefix || "u/0/";
  const targetUrl = videosUrlForPrefix(prefix);
  const wantSec = Number(job.seconds) >= 12 ? 15 : 10;
  const aspect =
    job.aspect === "portrait" || job.ratio === "9:16" || job.ratio === "3:4"
      ? "portrait"
      : "landscape";

  console.log(
    `[gemini:${acc.email || prefix}] Bắt đầu tạo video (${wantSec}s, ${aspect === "portrait" ? "Dọc 9:16" : "Ngang 16:9"}) tại ${targetUrl}`
  );

  const { page, prevResponseCount, preConvId, t0, realEmail } = await flow.withUiFocusLock(async () => {
    const p = await ensureGeminiWorkerPage(true);
    await p.bringToFront().catch(() => {});
    await p.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 25000 }).catch(() => {});

    let st = null;
    for (let i = 0; i < 35; i++) {
      await sleep(450);
      await inject(p).catch(() => {});
      st = await p.evaluate(() => window.__geminiUi?.inspectState()).catch(() => null);
      if (st?.needManualAuth) {
        const err = new Error(
          st.reason === "challenge"
            ? `GEMINI_CHALLENGE_BLOCK: Google hiển thị trang xác minh con người (${st.url || prefix}) -> dừng ngay để người dùng tự tích xác nhận trên Brave.`
            : `GEMINI_AUTH_REQUIRED: Tài khoản ${prefix} cần đăng nhập lại.`
        );
        err.code = st.reason === "challenge" ? "GEMINI_CHALLENGE_BLOCK" : "GEMINI_AUTH_REQUIRED";
        throw err;
      }
      if (st?.immediateQuota) {
        const err = new Error(`GEMINI_QUOTA_EXHAUSTED: ${st.immediateQuotaText || "Đã hết lượt tạo video"}`);
        err.code = "GEMINI_QUOTA_EXHAUSTED";
        throw err;
      }
      if (st?.ready) break;
    }

    if (!st?.ready) {
      throw new Error(`Không mở được khung nhập tạo video trên Gemini (${prefix}).`);
    }

    // Chọn công cụ Video + Thời lượng (10 giây / 15 giây) + Tỷ lệ (Ngang / Dọc)
    await inject(p);
    const cfgRes = await p.evaluate(
      (opts) => window.__geminiUi.configureVideoOptions(opts),
      { seconds: wantSec, aspect }
    );
    if (!cfgRes?.ok) {
      const err = new Error(
        `GEMINI_QUOTA_EXHAUSTED: Tài khoản ${st.email || prefix} không có công cụ tạo Video (hoặc đã khóa lượt tạo).`
      );
      err.code = "GEMINI_QUOTA_EXHAUSTED";
      throw err;
    }

    let tmpDir = null;
    try {
      if (job.images && job.images.length > 0) {
        console.log(`[gemini:${st.email || prefix}] Đang tải lên ${Math.min(3, job.images.length)} ảnh tham chiếu...`);
        tmpDir = await uploadReferenceImagesToGemini(p, job.images);
      }

      await inject(p);
      const cleanPrompt = String(job.prompt || "").trim();
      const fillRes = await p.evaluate((txtPrompt) => window.__geminiUi.fillPromptInEditor(txtPrompt), cleanPrompt);
      if (!fillRes?.ok) {
        const compCenter = await p.evaluate(() => window.__geminiUi.getComposerCenter());
        if (compCenter) {
          await p.mouse.click(compCenter.x, compCenter.y);
          await sleep(150);
        }
        const cdp = await p.target().createCDPSession();
        try {
          await cdp.send("Input.insertText", { text: cleanPrompt });
        } finally {
          await cdp.detach().catch(() => {});
        }
      }

      await sleep(450);
      await inject(p);
      await p.bringToFront().catch(() => {});
      const sendRes = await p.evaluate(() => window.__geminiUi.clickSendOrGetCenter());
      if (!sendRes?.clicked) {
        await p.keyboard.press("Enter");
      }

      // Xác nhận chắc chắn Gemini đã nhận câu lệnh (ô nhập rỗng hoặc đã sinh model-response mới)
      let submittedOk = false;
      for (let chk = 0; chk < 14; chk++) {
        await sleep(450);
        await inject(p).catch(() => {});
        const accChk = await p
          .evaluate((prevCnt) => window.__geminiUi.checkSubmissionAccepted(prevCnt), st.responseCount || 0)
          .catch(() => null);
        if (accChk?.quotaHit) {
          const err = new Error(`GEMINI_QUOTA_EXHAUSTED: ${accChk.snack}`);
          err.code = "GEMINI_QUOTA_EXHAUSTED";
          err.email = st.email || acc.email || "";
          throw err;
        }
        if (accChk?.newTurn || (accChk?.edEmpty && chk >= 2)) {
          submittedOk = true;
          break;
        }
        if (chk === 5 && !accChk?.edEmpty) {
          const retrySend = await p.evaluate(() => window.__geminiUi.getSendCenter());
          if (retrySend) {
            await p.bringToFront().catch(() => {});
            await p.mouse.click(retrySend.x, retrySend.y);
          } else {
            await p.keyboard.press("Enter");
          }
        }
      }
      if (!submittedOk) {
        throw new Error(`Gemini (${st.email || prefix}) không nhận lệnh gửi sau khi điền prompt.`);
      }

      return {
        page: p,
        prevResponseCount: st.responseCount || 0,
        preConvId: st.convId || "",
        t0: Date.now(),
        realEmail: st.email || acc.email || "",
      };
    } finally {
      if (tmpDir) {
        try {
          fs.rmSync(tmpDir, { recursive: true, force: true });
        } catch {}
      }
    }
  });

  console.log(
    `[gemini:${realEmail || prefix}] Đã gửi lệnh tạo video (${wantSec}s), đã nhả khóa chuột cho các tab khác & đang chờ kết xuất...`
  );

  const timeoutMs = (job.timeoutMin || 8) * 60 * 1000;
  let createdConvId = "";

  for (;;) {
    await sleep(3000);
    if (Date.now() - t0 > timeoutMs) {
      if (createdConvId && createdConvId !== preConvId) {
        await cleanupTemporaryGeminiChat(page, createdConvId, prefix, job.keepChat).catch(() => {});
      }
      throw new Error(`Hết thời gian chờ Gemini (${realEmail || prefix}) kết xuất video.`);
    }

    await inject(page).catch(() => {});
    const st = await page
      .evaluate((arg) => window.__geminiUi?.poll(arg), { prevResponseCount, t0 })
      .catch(() => null);
    if (!st) continue;

    if (st.convId && st.convId !== preConvId) {
      createdConvId = st.convId;
    }

    if (st.state === "quota_exhausted") {
      if (createdConvId) {
        await cleanupTemporaryGeminiChat(page, createdConvId, prefix, job.keepChat).catch(() => {});
      }
      const err = new Error(`GEMINI_QUOTA_EXHAUSTED: ${st.error || "Đã chạm giới hạn tạo video"}`);
      err.code = "GEMINI_QUOTA_EXHAUSTED";
      err.email = realEmail;
      throw err;
    }

    if (st.state === "failed") {
      if (createdConvId) {
        await cleanupTemporaryGeminiChat(page, createdConvId, prefix, job.keepChat).catch(() => {});
      }
      throw new Error(`Gemini (${realEmail || prefix}) báo lỗi: ${st.error || "Không tạo được video"}`);
    }

    if (st.state === "done") {
      await sleep(1200);
      const mp4Item = await downloadCompletedGeminiVideo(page, prevResponseCount);
      markAccountHealthy(prefix, realEmail);
      console.log(
        `[gemini:${realEmail || prefix}] HOÀN TẤT tải video MP4 (${(mp4Item.data.length / 1048576).toFixed(2)} MB)!`
      );
      if (createdConvId) {
        await cleanupTemporaryGeminiChat(page, createdConvId, prefix, job.keepChat).catch(() => {});
      }
      scheduleIdleCleanup();
      return {
        items: [mp4Item],
        account: realEmail || prefix,
        prefix,
      };
    }
  }
}

async function generateVideoWithMultiAccountAndFlowFallback(rawJob) {
  const job = rawJob || {};
  return await withGeminiJobLock(async () => {
    const candidates = await getCandidateAccounts();
    const geminiErrors = [];

    for (const acc of candidates) {
      try {
        const res = await generateOneVideoOnAccount(job, acc);
        return {
          ok: true,
          provider: "gemini",
          account: res.account,
          prefix: res.prefix,
          items: res.items,
          data: res.items[0].data,
          mime: res.items[0].mime || "video/mp4",
        };
      } catch (err) {
        const msg = String(err?.message || err);
        geminiErrors.push(`${acc.email || acc.prefix}: ${msg}`);
        if (err?.code === "GEMINI_CHALLENGE_BLOCK" || /google\.com\/sorry|GEMINI_CHALLENGE_BLOCK/i.test(msg)) {
          // Dừng ngay lập tức khi gặp cổng CAPTCHA của Google, tuyệt đối không quét tiếp các nick khác gây khóa dây chuyền!
          return {
            ok: false,
            challengeBlocked: true,
            error: msg,
          };
        }
        if (
          err?.code === "GEMINI_QUOTA_EXHAUSTED" ||
          err?.code === "GEMINI_AUTH_REQUIRED" ||
          /GEMINI_QUOTA_EXHAUSTED|reached your.*limit|đã đạt đến giới hạn|không thể tạo thêm video|hết lượt tạo video/i.test(msg)
        ) {
          markAccountExhausted(acc.prefix, err.email || acc.email || "", msg);
          continue;
        }
        console.warn(
          `[gemini] Tài khoản ${acc.email || acc.prefix} gặp lỗi (${msg}) -> tự động thử sang tài khoản Gemini Pro tiếp theo!`
        );
      }
    }

    await closeIdleGeminiTabsNow().catch(() => {});

    if (job.noFallback === true) {
      return {
        ok: false,
        error:
          geminiErrors.length > 0
            ? `Tất cả tài khoản Gemini trong Brave đều không tạo được video: ${geminiErrors.join(" | ")}`
            : "Không tìm thấy tài khoản Gemini nào đã đăng nhập trong Brave (:9333).",
      };
    }

    // Khi TẤT CẢ các tài khoản Gemini Pro trong Brave đều đã hết lượt tạo video -> tự động chuyển qua Google Flow!
    console.warn(
      `[gemini -> flow fallback] Đã thử hết ${candidates.length} tài khoản Gemini Pro trong Brave (${geminiErrors.join(" ; ") || "hết lượt"}) -> tự động chuyển sang dự phòng Google Flow!`
    );
    try {
      if (typeof flow.generateVideoFallback === "function") {
        const aspect =
          job.aspect === "portrait" || job.ratio === "9:16" || job.ratio === "3:4"
            ? "portrait"
            : "landscape";
        const flowSeconds = Math.min(15, Math.max(3, Math.round(Number(job.flowSeconds || job.seconds) || 6)));
        const flowImgs = Array.isArray(job.images) ? job.images : [];
        const flowItems = await flow.generateVideoFallback({
          prompt: job.prompt || "",
          model: job.flowModel || "Omni 1.2 Flash",
          aspect,
          resolution: job.resolution || "720p",
          seconds: flowSeconds,
          count: 1,
          images: flowImgs,
          mode: job.mode === "frames" && flowImgs.length && flowImgs.length <= 2 ? "frames" : "ingredients",
        });
        if (flowItems && flowItems.length > 0) {
          return {
            ok: true,
            provider: "flow-fallback",
            items: flowItems,
            data: flowItems[0].data,
            mime: flowItems[0].mime || "video/mp4",
          };
        }
      }
    } catch (flowErr) {
      console.error("[gemini -> flow fallback] Google Flow cũng gặp lỗi:", flowErr.message || flowErr);
      return {
        ok: false,
        error: `Đã hết lượt trên tất cả tài khoản Gemini Pro (${geminiErrors.join(" | ") || "0 nick khả dụng"}) VÀ dự phòng Google Flow cũng lỗi: ${flowErr.message || flowErr}`,
      };
    }

    return {
      ok: false,
      error: `Không thể tạo video trên cả chuỗi Gemini Pro -> Google Flow (${geminiErrors.join(" | ")})`,
    };
  });
}

async function show() {
  const candidates = await getCandidateAccounts().catch(() => []);
  const prefix = candidates[0]?.prefix || store.activePrefix || "u/0/";
  const page = await ensureGeminiWorkerPage(true);
  await page.goto(videosUrlForPrefix(prefix), { waitUntil: "domcontentloaded" }).catch(() => {});
  await flow.ensureWindowOnScreen(page);
  await page.bringToFront();
  return true;
}

async function status() {
  loadConfig();
  const alive = !!(await flow.debugAlive());
  return {
    browserOpen: alive,
    activePrefix: store.activePrefix || "u/0/",
    accounts: (store.accounts || []).map((a) => ({
      prefix: a.prefix,
      email: a.email || "",
      exhausted: isAccountExhausted(a),
      exhaustedUntil: a.exhaustedUntil || null,
      videosGenerated: a.videosGenerated || 0,
      active: a.prefix === store.activePrefix,
    })),
  };
}

function setup(app) {
  userData = app.getPath("userData");
  configPath = path.join(userData, "gemini-driver.json");
  loadConfig();

  ipcMain.handle("gemini:status", () => status());
  ipcMain.handle("gemini:accounts", () => status());
  ipcMain.handle("gemini:refresh-accounts", (_e, opts) =>
    discoverGeminiAccounts({ forceResetCooldown: Boolean(opts?.resetCooldown) }).then(status)
  );
  ipcMain.handle("gemini:show", () =>
    show().catch((e) => {
      dialog.showErrorBox("Gemini Video", String(e.message || e));
      return false;
    })
  );
  ipcMain.handle("gemini:generate-video", (_e, job) => generateVideoWithMultiAccountAndFlowFallback(job));
}

function destroy() {
  if (geminiIdleTimer) {
    clearTimeout(geminiIdleTimer);
    geminiIdleTimer = null;
  }
}

module.exports = {
  setup,
  destroy,
  show,
  status,
  discoverGeminiAccounts,
  generateVideo: generateVideoWithMultiAccountAndFlowFallback,
};
