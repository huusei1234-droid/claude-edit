// Điều khiển OpenAI Sora Web (https://sora.chatgpt.com / https://sora.com) trên cùng cửa sổ trình duyệt Brave (:9333)
// tận dụng trực tiếp gói đăng ký ChatGPT Plus của người dùng (0 tốn phí API).
const { ipcMain, dialog } = require("electron");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const flow = require("./flow-driver");

const SORA_HOME = "https://sora.chatgpt.com/explore";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let soraBusy = false;
let soraPageRef = null;
let soraIdleTimer = null;

async function ensureSoraPage(create = true) {
  const b = await flow.ensureBrowser({ visible: true });
  if (soraPageRef && !soraPageRef.isClosed()) {
    const ok = await soraPageRef.evaluate("1").catch(() => null);
    if (ok === 1) return soraPageRef;
    soraPageRef = null;
  }
  const pages = await b.pages();
  let page = pages.find((p) => !p.isClosed() && /^https:\/\/sora\.(chatgpt\.)?com\b/i.test(p.url() || "")) || null;
  if (!page && create) {
    page = typeof flow.createBackgroundPage === "function"
      ? await flow.createBackgroundPage(b, SORA_HOME)
      : await b.newPage();
    if (!/^https:\/\/sora\.(chatgpt\.)?com\b/i.test(page.url() || "")) {
      await page.goto(SORA_HOME, { waitUntil: "domcontentloaded", timeout: 45000 }).catch(() => {});
    }
  }
  soraPageRef = page;
  return page;
}

function scheduleCloseIdleSoraTab() {
  if (soraIdleTimer) clearTimeout(soraIdleTimer);
  soraIdleTimer = setTimeout(async () => {
    soraIdleTimer = null;
    if (!soraBusy && soraPageRef && !soraPageRef.isClosed()) {
      const p = soraPageRef;
      soraPageRef = null;
      try { await p.close(); } catch {}
    }
  }, 15000);
  if (soraIdleTimer.unref) soraIdleTimer.unref();
}

async function show() {
  const page = await ensureSoraPage(true);
  await flow.ensureWindowOnScreen(page);
  await page.bringToFront();
  return true;
}

async function status() {
  const alive = !!(await flow.debugAlive());
  return { browserOpen: alive, url: SORA_HOME };
}

async function fetchVideoBytesInPage(page, videoUrl) {
  const b64Res = await page.evaluate(async (u) => {
    const r = await fetch(u, { credentials: "include" });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const blob = await r.blob();
    const mime = blob.type && blob.type.startsWith("video/") ? blob.type : "video/mp4";
    const base64 = await new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => {
        const s = String(fr.result || "");
        const i = s.indexOf(",");
        resolve(i >= 0 ? s.slice(i + 1) : s);
      };
      fr.onerror = reject;
      fr.readAsDataURL(blob);
    });
    return { base64, mime };
  }, videoUrl);
  return {
    data: Buffer.from(b64Res.base64, "base64"),
    mime: b64Res.mime || "video/mp4",
  };
}

async function generateVideo(job = {}) {
  if (soraBusy) {
    throw new Error("Sora đang xử lý một video khác, vui lòng chờ hoàn tất.");
  }
  soraBusy = true;
  if (soraIdleTimer) {
    clearTimeout(soraIdleTimer);
    soraIdleTimer = null;
  }

  let tmpDir = null;
  try {
    const prompt = String(job.prompt || "").trim();
    if (!prompt) throw new Error("Thiếu nội dung prompt cho Sora.");

    const ratio = String(job.ratio || (job.aspect === "portrait" ? "9:16" : "16:9"));
    const seconds = Math.min(20, Math.max(5, Number(job.seconds) || 10));

    const { page, baselineVideos, t0 } = await flow.withUiFocusLock(async () => {
      const p = await ensureSoraPage(true);
      await p.bringToFront().catch(() => {});

      if (!/^https:\/\/sora\.(chatgpt\.)?com\b/i.test(p.url() || "")) {
        await p.goto(SORA_HOME, { waitUntil: "domcontentloaded", timeout: 45000 });
      }
      await sleep(2500);

      // Kiểm tra cổng xác minh hoặc chưa đăng nhập
      const stateCheck = await p.evaluate(() => {
        const title = document.title || "";
        const txt = (document.body?.innerText || "").slice(0, 1500);
        if (/Just a moment|Verify you are human/i.test(title)) {
          return { needAuth: true, reason: "challenge" };
        }
        const loginBtn = Array.from(document.querySelectorAll("button, a")).find((el) =>
          /^(Log in|Sign in|Đăng nhập)$/i.test((el.innerText || "").trim())
        );
        if (loginBtn || /auth\.openai\.com/i.test(location.href)) {
          return { needAuth: true, reason: "login" };
        }
        return { needAuth: false, sample: txt.slice(0, 200) };
      });

      if (stateCheck.needAuth) {
        await p.bringToFront().catch(() => {});
        throw new Error(
          "Cần đăng nhập Sora bằng tài khoản ChatGPT Plus một lần trong cửa sổ Brave (bấm Log in with ChatGPT)."
        );
      }

      // Chuyển sang mục My Media / Library hoặc giữ khung nhập dưới đáy của Sora
      const baseline = await p.evaluate(() =>
        Array.from(document.querySelectorAll("video")).map((v) => v.currentSrc || v.src || "").filter(Boolean)
      );

      // Tải ảnh tham chiếu nếu có
      if (Array.isArray(job.images) && job.images.length > 0) {
        tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "sora-refs-"));
        const im = job.images[0];
        const fp = path.join(tmpDir, (im.name || "ref_1.png").replace(/[^a-zA-Z0-9._-]/g, "_"));
        fs.writeFileSync(fp, Buffer.from(im.base64, "base64"));
        const fInput = await p.$('input[type="file"]');
        if (fInput) {
          await fInput.uploadFile(fp);
          await sleep(2000);
        }
      }

      // Chọn tỷ lệ khung hình & thời lượng nếu nút hiển thị trên thanh composer của Sora
      await p.evaluate(
        ({ wantRatio, wantSec }) => {
          const btns = Array.from(document.querySelectorAll("button, [role='option'], [role='menuitemradio']"));
          const rBtn = btns.find((b) => (b.innerText || "").trim() === wantRatio);
          if (rBtn) rBtn.click();
          const sBtn = btns.find((b) => new RegExp(`^${wantSec}\\s*s\\b`, "i").test((b.innerText || "").trim()));
          if (sBtn) sBtn.click();
        },
        { wantRatio: ratio, wantSec: seconds }
      ).catch(() => {});

      // Tìm ô nhập prompt của Sora
      const composer = await p.$(
        'textarea[placeholder*="Describe" i], textarea[placeholder*="video" i], textarea, div[contenteditable="true"]'
      );
      if (!composer) {
        throw new Error("Không tìm thấy ô nhập prompt trên trang Sora (https://sora.chatgpt.com).");
      }
      await composer.click();
      await sleep(150);

      const cdp = await p.target().createCDPSession();
      try {
        await p.keyboard.down("Control");
        await p.keyboard.press("KeyA");
        await p.keyboard.up("Control");
        await p.keyboard.press("Backspace");
        await sleep(80);
        const fullDirective = `${prompt} (Aspect ratio ${ratio}, duration ${seconds}s)`;
        await cdp.send("Input.insertText", { text: fullDirective });
      } finally {
        await cdp.detach().catch(() => {});
      }
      await sleep(400);

      // Bấm nút Create / Generate / Submit
      const clickedSubmit = await p.evaluate(() => {
        const btns = Array.from(document.querySelectorAll("button"));
        const sub = btns.find(
          (b) =>
            !b.disabled &&
            (/^(Create|Create video|Generate|Remix)$/i.test((b.innerText || "").trim()) ||
              /create|generate|send|submit/i.test(b.getAttribute("aria-label") || ""))
        );
        if (sub) {
          sub.click();
          return true;
        }
        return false;
      });
      if (!clickedSubmit) {
        await p.keyboard.press("Enter");
      }

      return { page: p, baselineVideos: baseline, t0: Date.now() };
    });

    // Mở trang Library / Creations của Sora để đón video mới kết xuất xong
    await sleep(3000);
    await page.goto("https://sora.chatgpt.com/library", { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => {});

    const timeoutMs = (job.timeoutMin || 8) * 60 * 1000;
    const baseSet = new Set(baselineVideos);

    for (;;) {
      await sleep(4000);
      if (Date.now() - t0 > timeoutMs) {
        throw new Error("Hết thời gian chờ Sora kết xuất video (quá 8 phút).");
      }
      const foundUrl = await page
        .evaluate((known) => {
          const knownSet = new Set(known || []);
          const vids = Array.from(document.querySelectorAll("video"));
          for (const v of vids) {
            const u = v.currentSrc || v.src || "";
            if (u && /^https?:/i.test(u) && !knownSet.has(u) && (v.readyState >= 2 || v.videoWidth > 100)) {
              return u;
            }
          }
          return "";
        }, Array.from(baseSet))
        .catch(() => "");

      if (foundUrl) {
        const dl = await fetchVideoBytesInPage(page, foundUrl);
        if (dl.data && dl.data.length > 16384) {
          console.log(`[sora] Đã tải thành công video Sora (${dl.data.length} bytes)`);
          return { ok: true, provider: "sora", data: dl.data, mime: dl.mime };
        }
      }
    }
  } finally {
    soraBusy = false;
    scheduleCloseIdleSoraTab();
    if (tmpDir) {
      try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
    }
  }
}

function setup() {
  ipcMain.handle("sora:status", () => status());
  ipcMain.handle("sora:show", () =>
    show().catch((e) => {
      dialog.showErrorBox("Sora Video", String(e.message || e));
      return false;
    })
  );
  ipcMain.handle("sora:generate-video", async (_e, job) => {
    try {
      return await generateVideo(job || {});
    } catch (e) {
      return { ok: false, error: String(e.message || e) };
    }
  });
}

function destroy() {}

module.exports = { setup, destroy, show, status, generateVideo };
