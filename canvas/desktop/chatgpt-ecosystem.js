// Bộ điều phối Toàn diện Hệ sinh thái ChatGPT Plus cho Infinite Canvas & Full Studio:
// - Text / Vision / Thinking (Suy luận) / Deep Research / Web Search / Canvas
// - Tự động định tuyến Dự án (HTPM, K4 Phim Chuyện Trong Nhà, hoặc tạo/đồng bộ Sources mới)
// - Kết nối Sora Video, OpenAI Codex, Library, Connectors, Scheduled Tasks
// - Cổng HTTP cục bộ chuẩn OpenAI (http://127.0.0.1:18620/v1) miễn phí 100% qua gói ChatGPT Plus
const { ipcMain } = require("electron");
const http = require("node:http");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");
const flow = require("./flow-driver");

const GATEWAY_PORT = Number(process.env.CHATGPT_GATEWAY_PORT || 18620);
const HOME = "https://chatgpt.com/";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const KNOWN_PROJECTS = {
  HTPM: "g-p-6b093335deb88191accc76e34088233f",
  K4: "g-p-6b09334dab8081919ccd6e3b2d6a06b3",
};

const HUB_URLS = {
  home: "https://chatgpt.com/",
  htpm: `https://chatgpt.com/g/${KNOWN_PROJECTS.HTPM}/project`,
  k4: `https://chatgpt.com/g/${KNOWN_PROJECTS.K4}/project`,
  sora: "https://sora.chatgpt.com/explore",
  codex: "https://chatgpt.com/codex",
  library: "https://chatgpt.com/library",
  scheduled: "https://chatgpt.com/#settings/Schedules",
  connectors: "https://chatgpt.com/#settings/Connectors",
  personalization: "https://chatgpt.com/#settings/Personalization",
  gpts: "https://chatgpt.com/gpts",
};

let chatgptDriver = null;
let soraDriver = null;
let getMainWindow = () => null;
let gatewayServer = null;
let configFilePath = "";

function readDriverProjects() {
  const map = { ...KNOWN_PROJECTS };
  try {
    if (configFilePath && fs.existsSync(configFilePath)) {
      const raw = JSON.parse(fs.readFileSync(configFilePath, "utf8"));
      for (const a of raw.accounts || []) {
        if (a.projectLabel && a.projectId) {
          const key = a.projectLabel.toUpperCase().includes("K4")
            ? "K4"
            : a.projectLabel.toUpperCase().includes("HTPM")
              ? "HTPM"
              : a.projectLabel.trim();
          map[key] = a.projectId;
        }
      }
    }
  } catch {}
  return map;
}

function resolveProjectTarget(job = {}) {
  const projs = readDriverProjects();
  const rawModel = String(job.model || "").toLowerCase();
  const rawProj = String(job.project || job.projectId || "auto").trim();

  if (/^g-p-[a-z0-9-]+$/i.test(rawProj)) {
    return { label: rawProj, id: rawProj, url: `https://chatgpt.com/g/${rawProj}/project` };
  }
  if (rawProj.toLowerCase() === "none" || rawProj.toLowerCase() === "root" || rawProj.toLowerCase() === "general") {
    return { label: "General", id: "", url: HOME };
  }
  if (rawProj.toUpperCase() === "K4" || rawModel.includes("k4")) {
    return { label: "K4 Phim Chuyện Trong Nhà", id: projs.K4, url: `https://chatgpt.com/g/${projs.K4}/project` };
  }
  if (rawProj.toUpperCase() === "HTPM" || rawModel.includes("htpm") || rawModel.includes("brand")) {
    return { label: "HTPM", id: projs.HTPM, url: `https://chatgpt.com/g/${projs.HTPM}/project` };
  }

  // Chế độ auto: tự nhận diện ngữ cảnh K4 Phim AI vs HTPM/An Vượng/Feel Chicken
  const textSample = String(job.prompt || "");
  if (
    /CHỐT KHÔNG GIAN|IMAGE XUẤT HIỆN|ASSET BOARD|BẮT ĐẦU PROMPT|phim chuyện trong nhà|\bK4\b|viết prompt flow|kịch bản gia đình|mẹ chồng nàng dâu/i.test(
      textSample
    )
  ) {
    return { label: "K4 Phim Chuyện Trong Nhà", id: projs.K4, url: `https://chatgpt.com/g/${projs.K4}/project` };
  }
  if (
    /\bHTPM\b|Hằng Thu|An Vượng|AV Protein|Bojomi|Curcumilk|Collamela|Điều Kinh|Phụ Khoa|Feel Chicken|Saranghae/i.test(
      textSample
    )
  ) {
    return { label: "HTPM", id: projs.HTPM, url: `https://chatgpt.com/g/${projs.HTPM}/project` };
  }

  return { label: "General", id: "", url: HOME };
}

function resolveModeFromJob(job = {}) {
  if (job.mode && job.mode !== "auto") return String(job.mode).toLowerCase();
  const m = String(job.model || "").toLowerCase();
  if (m.includes("deep-research") || m.includes("research")) return "deep-research";
  if (m.includes("search")) return "search";
  if (m.includes("canvas")) return "canvas";
  if (m.includes("thinking") || m.includes("reason") || job.reasoningEffort === "high" || job.reasoningEffort === "xhigh") {
    return "thinking";
  }
  return "auto";
}

function normalizeMessagesToPromptAndImages(messages = [], directPrompt = "", directImages = []) {
  const imgs = Array.isArray(directImages) ? [...directImages] : [];
  if (!Array.isArray(messages) || messages.length === 0) {
    return { prompt: String(directPrompt || "").trim(), images: imgs };
  }

  const parts = [];
  for (const msg of messages) {
    if (!msg) continue;
    const role = msg.role || "user";
    let textChunk = "";
    if (typeof msg.content === "string") {
      textChunk = msg.content.trim();
    } else if (Array.isArray(msg.content)) {
      const subTexts = [];
      for (const item of msg.content) {
        if (!item) continue;
        if ((item.type === "text" || item.type === "input_text") && item.text) {
          subTexts.push(item.text);
        } else if (item.type === "image_url" && item.image_url?.url) {
          const m = String(item.image_url.url).match(/^data:([^;]+);base64,(.*)$/);
          if (m) {
            imgs.push({ mime: m[1], base64: m[2], name: `msg_img_${imgs.length + 1}.png` });
          }
        }
      }
      textChunk = subTexts.join("\n").trim();
    }
    if (!textChunk) continue;
    if (role === "system") {
      parts.push(`[CHỈ DẪN HỆ THỐNG]\n${textChunk}`);
    } else if (messages.length === 1) {
      parts.push(textChunk);
    } else {
      const tag = role === "assistant" ? "Trợ lý trước đó" : "Yêu cầu";
      parts.push(`[${tag}]\n${textChunk}`);
    }
  }

  return {
    prompt: (parts.join("\n\n").trim() || String(directPrompt || "").trim()),
    images: imgs,
  };
}

async function uploadAttachmentsToComposer(page, images = [], filePaths = []) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "chatgpt-eco-"));
  const allFiles = [];

  for (let i = 0; i < (images || []).length; i++) {
    const im = images[i];
    if (typeof im === "string" && fs.existsSync(im)) {
      allFiles.push(im);
    } else if (im && im.base64) {
      const safeName = (im.name || `ref_${i + 1}.png`).replace(/[^a-zA-Z0-9._-]/g, "_");
      const fp = path.join(tmpDir, safeName);
      fs.writeFileSync(fp, Buffer.from(im.base64, "base64"));
      allFiles.push(fp);
    }
  }

  for (const fp of filePaths || []) {
    if (fp && fs.existsSync(fp)) allFiles.push(path.resolve(fp));
  }

  if (allFiles.length === 0) {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
    return null;
  }

  let inputHandle =
    (await page.$('input[type="file"][aria-label*="Attach files" i]')) ||
    (await page.$('input[type="file"][multiple]')) ||
    (await page.$('input[type="file"]'));

  if (!inputHandle) {
    await page.evaluate(() => {
      const plus =
        document.querySelector('[data-testid="composer-plus-btn"]') ||
        Array.from(document.querySelectorAll("button")).find((b) =>
          /attach|upload|add files|thêm tệp/i.test((b.getAttribute("aria-label") || "") + " " + (b.innerText || ""))
        );
      if (plus) plus.click();
    });
    await sleep(600);
    inputHandle = (await page.$('input[type="file"][multiple]')) || (await page.$('input[type="file"]'));
  }

  if (!inputHandle) {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
    throw new Error("Không tìm thấy ô đính kèm tệp trên ChatGPT Plus.");
  }

  const isMulti = await inputHandle.evaluate((el) => !!el.multiple).catch(() => false);
  if (isMulti && allFiles.length > 1) {
    await inputHandle.uploadFile(...allFiles);
  } else {
    for (const f of allFiles) {
      const h = (await page.$('input[type="file"][aria-label*="Attach files" i]')) || inputHandle;
      await h.uploadFile(f);
      await sleep(700);
    }
  }

  for (let i = 0; i < 60; i++) {
    await sleep(500);
    await chatgptDriver.inject(page).catch(() => {});
    const settled = await page.evaluate(() => window.__chatgptUi?.uploadsSettled?.()).catch(() => true);
    if (settled && i >= 2) break;
  }
  return tmpDir;
}

async function askChatGPT(job = {}, onDelta = null) {
  const { prompt, images } = normalizeMessagesToPromptAndImages(job.messages, job.prompt, job.images);
  if (!prompt) throw new Error("Thiếu nội dung câu hỏi/prompt gửi sang ChatGPT Plus.");

  const target = resolveProjectTarget(job);
  const mode = resolveModeFromJob(job);
  const keepChat = Boolean(job.keepChat);

  return chatgptDriver.withGptParallelSlot(async (slotIdx) => {
    const { page, prevAssistantCount, prevTurnKeys, t0 } = await flow.withUiFocusLock(async () => {
      const p = await chatgptDriver.chatgptSlotPage(slotIdx, true);
      await p.bringToFront().catch(() => {});

      // Bật cờ bỏ tự nhảy về HTPM nếu người dùng chủ đích vào K4 hoặc General
      await p.evaluateOnNewDocument((skip) => {
        window.__chatgptSkipAutoHtpm = skip;
      }, target.label !== "HTPM").catch(() => {});

      await p.goto(target.url, { waitUntil: "domcontentloaded", timeout: 40000 }).catch(() => {});
      await p.evaluate((skip) => {
        window.__chatgptSkipAutoHtpm = skip;
        window.__chatgptClickedStartResearch = false;
        window.__chatgptLastPollTxt = "";
      }, target.label !== "HTPM").catch(() => {});

      let readyState = null;
      for (let i = 0; i < 40; i++) {
        await sleep(500);
        await chatgptDriver.inject(p).catch(() => {});
        readyState = await p.evaluate(() => window.__chatgptUi?.inspectState?.()).catch(() => null);
        if (readyState?.needManualAuth) {
          await p.bringToFront().catch(() => {});
          throw new Error("Cần đăng nhập tài khoản ChatGPT Plus trong trình duyệt Brave.");
        }
        if (readyState?.ready) break;
      }
      if (!readyState?.ready) {
        throw new Error("Không tìm thấy khung nhập ChatGPT Plus trên trình duyệt Brave.");
      }

      let tmpDir = null;
      try {
        if ((images && images.length) || (job.files && job.files.length)) {
          tmpDir = await uploadAttachmentsToComposer(p, images, job.files || []);
        }

        await chatgptDriver.inject(p).catch(() => {});
        if (mode && mode !== "auto") {
          await p.evaluate((m) => window.__chatgptUi?.activateComposerTool?.(m), mode).catch(() => {});
          await sleep(350);
        }

        const compCenter = await p.evaluate(() => window.__chatgptUi?.getComposerCenter?.());
        if (compCenter) {
          await p.mouse.click(compCenter.x, compCenter.y);
          await sleep(150);
        }

        const cdp = await p.target().createCDPSession();
        try {
          await p.keyboard.down("Control");
          await p.keyboard.press("KeyA");
          await p.keyboard.up("Control");
          await p.keyboard.press("Backspace");
          await sleep(80);
          await cdp.send("Input.insertText", { text: prompt });
        } finally {
          await cdp.detach().catch(() => {});
        }

        await sleep(450);
        await chatgptDriver.inject(p);
        const sendPos = await p.evaluate(() => window.__chatgptUi?.getSendCenter?.());
        if (sendPos) {
          await p.bringToFront().catch(() => {});
          await p.mouse.click(sendPos.x, sendPos.y);
        } else {
          await p.keyboard.press("Enter");
        }

        return {
          page: p,
          prevAssistantCount: readyState.turnCount || 0,
          prevTurnKeys: readyState.turnKeys || [],
          t0: Date.now(),
        };
      } finally {
        if (tmpDir) {
          try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
        }
      }
    });

    const maxMinutes = mode === "deep-research" ? (job.timeoutMin || 18) : (job.timeoutMin || 6);
    const timeoutMs = maxMinutes * 60 * 1000;
    let lastDelta = "";

    for (;;) {
      await sleep(1400);
      if (Date.now() - t0 > timeoutMs) {
        if (!keepChat) await chatgptDriver.cleanupConversationAfterDownload(page, { keepChat: false }).catch(() => {});
        throw new Error(`Hết thời gian chờ ChatGPT Plus phản hồi (quá ${maxMinutes} phút).`);
      }

      await chatgptDriver.inject(page).catch(() => {});
      const st = await page
        .evaluate((arg) => window.__chatgptUi?.pollText?.(arg), {
          prevAssistantCount,
          prevTurnKeys,
          t0,
          mode,
        })
        .catch(() => null);

      if (!st) continue;

      if (st.partialText && st.partialText !== lastDelta) {
        lastDelta = st.partialText;
        if (typeof onDelta === "function") {
          try { onDelta(lastDelta); } catch {}
        }
        if (job.requestId) {
          const w = getMainWindow();
          if (w && !w.isDestroyed()) {
            w.webContents.send("chatgpt:stream-delta", { requestId: job.requestId, text: lastDelta });
          }
        }
      }

      if (st.state === "done") {
        const finalConvUrl = st.convUrl || page.url();
        if (typeof onDelta === "function" && st.text !== lastDelta) {
          try { onDelta(st.text); } catch {}
        }
        if (job.requestId) {
          const w = getMainWindow();
          if (w && !w.isDestroyed()) {
            w.webContents.send("chatgpt:stream-delta", { requestId: job.requestId, text: st.text, done: true });
          }
        }
        if (!keepChat) {
          await chatgptDriver.cleanupConversationAfterDownload(page, { keepChat: false }).catch(() => {});
        }
        return {
          ok: true,
          provider: "chatgpt-plus",
          projectUsed: target.label,
          projectId: target.id,
          mode,
          text: st.text,
          convUrl: keepChat ? finalConvUrl : "",
        };
      }
    }
  });
}

async function syncProject(spec = {}) {
  const name = String(spec.name || "").trim();
  if (!name) throw new Error("Thiếu tên dự án (name) cần đồng bộ trên ChatGPT Plus.");
  const instructions = typeof spec.instructions === "string" ? spec.instructions.trim() : null;
  const sourceFiles = Array.isArray(spec.sourceFiles) ? spec.sourceFiles.filter((f) => f && fs.existsSync(f)) : [];

  return flow.withUiFocusLock(async () => {
    const b = await flow.ensureBrowser({ visible: true });
    const page = await b.newPage();
    try {
      await page.bringToFront();
      await page.goto(HOME, { waitUntil: "domcontentloaded", timeout: 35000 });
      await sleep(2500);

      // Mở thanh bên nếu đang thu gọn
      await page.evaluate(() => {
        const sb =
          document.querySelector('button[aria-label="Show sidebar"]') ||
          document.querySelector('button[aria-label="Open sidebar"]');
        if (sb) sb.click();
      });
      await sleep(700);

      let pid = await page.evaluate((targetName) => {
        for (const a of Array.from(document.querySelectorAll("a[href*='/g/g-p-']"))) {
          const t = (a.innerText || "").trim();
          const m = (a.getAttribute("href") || "").match(/\/g\/(g-p-[a-z0-9-]+)/i);
          if (m && t.toLowerCase() === targetName.toLowerCase()) return m[1];
        }
        return "";
      }, name);

      if (!pid) {
        const clickedAdd = await page.evaluate(() => {
          const btn =
            document.querySelector('button[aria-label="Add new project"]') ||
            document.querySelector("[data-app-action-sidebar-project-create]");
          if (!btn) return false;
          btn.click();
          return true;
        });
        if (!clickedAdd) throw new Error("Không tìm thấy nút Add new project trên ChatGPT Plus.");
        await sleep(1400);

        const inputHandle = await page.$('[role="dialog"] input');
        if (!inputHandle) throw new Error("Không thấy ô nhập tên dự án mới.");
        await page.evaluate((el, val) => {
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
          if (setter) setter.call(el, val);
          else el.value = val;
          el.dispatchEvent(new Event("input", { bubbles: true }));
          el.dispatchEvent(new Event("change", { bubbles: true }));
        }, inputHandle, name);
        await sleep(400);

        const cBtns = await page.$$('[role="dialog"] button');
        for (const cb of cBtns) {
          const t = await cb.evaluate((e) => (e.innerText || "").trim());
          if (/^(create project|create|tạo dự án|tạo)$/i.test(t)) {
            await cb.click();
            break;
          }
        }
        for (let w = 0; w < 25; w++) {
          await sleep(500);
          const m = page.url().match(/\/g\/(g-p-[a-z0-9-]+)/i);
          if (m) {
            pid = m[1];
            break;
          }
        }
      }

      if (!pid) throw new Error("Không lấy được mã dự án g-p-... sau khi tạo.");

      await page.goto(`https://chatgpt.com/g/${pid}/project`, { waitUntil: "domcontentloaded", timeout: 35000 });
      await sleep(2500);

      // Cập nhật Instructions nếu có truyền vào
      let updatedInstructions = false;
      if (instructions !== null) {
        const paBtn = await page.$('button[aria-label="Project actions"]');
        if (paBtn) {
          await paBtn.click();
          await sleep(800);
          const items = await page.$$('[role="menuitem"]');
          for (const it of items) {
            const box = await it.boundingBox().catch(() => null);
            if (!box || box.width <= 4) continue;
            const t = await it.evaluate((e) => (e.innerText || "").trim());
            if (/project settings|instructions|cài đặt dự án|hướng dẫn/i.test(t)) {
              await it.click();
              await sleep(1300);
              break;
            }
          }
          const area = await page.$('[role="dialog"] textarea');
          if (area) {
            await page.evaluate((el, val) => {
              const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
              if (setter) setter.call(el, val);
              else el.value = val;
              el.dispatchEvent(new Event("input", { bubbles: true }));
              el.dispatchEvent(new Event("change", { bubbles: true }));
            }, area, instructions);
            await sleep(500);
            const saveBtns = await page.$$('[role="dialog"] button');
            let saved = false;
            for (const sb of saveBtns) {
              const t = await sb.evaluate((e) => (e.innerText || "").trim());
              if (/^(save|done|apply|update|lưu|xong)$/i.test(t)) {
                await sb.click();
                saved = true;
                await sleep(900);
                break;
              }
            }
            if (!saved) {
              await page.keyboard.press("Escape").catch(() => {});
              await sleep(500);
            }
            updatedInstructions = true;
          }
        }
      }

      // Tải tệp nguồn lên mục Sources
      const uploadedFiles = [];
      if (sourceFiles.length > 0) {
        const mainBtns = await page.$$("main button, [role='tab']");
        for (const b of mainBtns) {
          const t = await b.evaluate((e) => (e.innerText || "").trim());
          if (/^(sources|files|nguồn|tệp)/i.test(t)) {
            await b.click();
            await sleep(1200);
            break;
          }
        }
        for (const fp of sourceFiles) {
          const fInputs = await page.$$('input[type="file"]');
          if (fInputs.length > 0) {
            await fInputs[fInputs.length - 1].uploadFile(fp);
            await sleep(2500);
            uploadedFiles.push(path.basename(fp));
          }
        }
      }

      // Ghi nhớ vào chatgpt-driver.json
      try {
        if (configFilePath && fs.existsSync(configFilePath)) {
          const cfg = JSON.parse(fs.readFileSync(configFilePath, "utf8"));
          cfg.accounts = cfg.accounts || [];
          const ex = cfg.accounts.find((a) => (a.projectLabel || "").toLowerCase() === name.toLowerCase());
          if (ex) {
            ex.projectId = pid;
          } else {
            cfg.accounts.push({
              id: "gpt_" + name.toLowerCase().replace(/[^a-z0-9]+/g, "_").slice(0, 16),
              name: "ChatGPT Plus - " + name,
              profile: "MAIN_BRAVE",
              projectLabel: name,
              projectId: pid,
            });
          }
          fs.writeFileSync(configFilePath, JSON.stringify(cfg, null, 2));
        }
      } catch {}

      return { ok: true, name, projectId: pid, updatedInstructions, uploadedFiles };
    } finally {
      await page.close().catch(() => {});
    }
  });
}

async function openHub(target = "home") {
  const key = String(target || "home").toLowerCase().trim();
  const projs = readDriverProjects();
  let url = HUB_URLS[key] || HOME;
  if (key === "htpm") url = `https://chatgpt.com/g/${projs.HTPM}/project`;
  if (key === "k4") url = `https://chatgpt.com/g/${projs.K4}/project`;
  if (/^https?:\/\//i.test(target)) url = target;

  if (key === "sora" && soraDriver) {
    await soraDriver.show();
    return { ok: true, target: key, url };
  }

  const b = await flow.ensureBrowser({ visible: true });
  const pages = await b.pages();
  let page = pages.find((p) => !p.isClosed() && /^https:\/\/chatgpt\.com\b/i.test(p.url() || "")) || null;
  if (!page) page = await b.newPage();
  await page.evaluateOnNewDocument(() => {
    window.__chatgptSkipAutoHtpm = true;
  }).catch(() => {});
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 35000 }).catch(() => {});
  await flow.ensureWindowOnScreen(page);
  await page.bringToFront();
  return { ok: true, target: key, url };
}

async function scheduleTask(spec = {}) {
  const prompt = String(spec.prompt || "").trim();
  const when = String(spec.when || spec.schedule || "every day at 8:00 AM").trim();
  if (!prompt) throw new Error("Thiếu nội dung công việc định kỳ (prompt).");
  const scheduledDirective = `Create a scheduled task (${when}) to automatically do the following:\n${prompt}`;
  return askChatGPT({
    prompt: scheduledDirective,
    project: spec.project || "none",
    mode: "auto",
    keepChat: true,
  });
}

function findCodexExecutable() {
  const localAppData = process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local");
  const binRoot = path.join(localAppData, "OpenAI", "Codex", "bin");
  try {
    if (fs.existsSync(binRoot)) {
      const dirs = fs
        .readdirSync(binRoot)
        .map((d) => path.join(binRoot, d, "codex.exe"))
        .filter((p) => fs.existsSync(p))
        .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
      if (dirs.length > 0) return dirs[0];
    }
  } catch {}
  const npmShim = path.join(process.env.APPDATA || "", "npm", process.platform === "win32" ? "codex.cmd" : "codex");
  if (fs.existsSync(npmShim)) return npmShim;
  return "codex";
}

function enrichPromptWithLocalProjectContext(prompt, projectHint = "auto") {
  const target = resolveProjectTarget({ prompt, project: projectHint });
  const migBase = "C:\\AI\\full studio\\huu\\chatgpt_migration_huusei1234\\02_PROJECTS";
  let instFile = "";
  if (target.label.includes("K4")) {
    instFile = path.join(migBase, "K4_Phim_Chuyen_Trong_Nha", "INSTRUCTIONS.txt");
  } else if (target.label === "HTPM") {
    instFile = path.join(migBase, "HTPM", "INSTRUCTIONS.txt");
  }
  if (instFile && fs.existsSync(instFile)) {
    const inst = fs.readFileSync(instFile, "utf8").trim();
    return `[QUY CHUẨN DỰ ÁN ${target.label}]\n${inst}\n\n[YÊU CẦU]\n${prompt}`;
  }
  return prompt;
}

async function runCodex(spec = {}) {
  const normalized = normalizeMessagesToPromptAndImages(spec.messages, spec.prompt, spec.images);
  const rawPrompt = normalized.prompt;
  if (!rawPrompt) {
    return openHub("codex");
  }

  const finalPrompt = enrichPromptWithLocalProjectContext(rawPrompt, spec.project || "auto");
  const codexExe = findCodexExecutable();
  const defaultWorkspace = fs.existsSync("C:\\AI\\full studio") ? "C:\\AI\\full studio" : process.cwd();
  const cwd = spec.cwd && fs.existsSync(spec.cwd) ? spec.cwd : defaultWorkspace;
  const model = String(spec.model || "gpt-6.2-sol").replace(/^chatgpt::|^codex-/i, "") || "gpt-6.2-sol";
  const sandbox = ["read-only", "workspace-write", "danger-full-access"].includes(spec.sandbox)
    ? spec.sandbox
    : "read-only";
  const effort = ["low", "medium", "high", "xhigh"].includes(String(spec.reasoningEffort || "").toLowerCase())
    ? String(spec.reasoningEffort).toLowerCase()
    : "";

  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "codex-run-"));
  const outMsgFile = path.join(tmpDir, "last_message.txt");
  const imgPaths = [];

  for (let i = 0; i < (normalized.images || []).length; i++) {
    const im = normalized.images[i];
    if (typeof im === "string" && fs.existsSync(im)) {
      imgPaths.push(im);
    } else if (im && im.base64) {
      const fp = path.join(tmpDir, (im.name || `img_${i + 1}.png`).replace(/[^a-zA-Z0-9._-]/g, "_"));
      fs.writeFileSync(fp, Buffer.from(im.base64, "base64"));
      imgPaths.push(fp);
    }
  }

  const args = ["exec", "--skip-git-repo-check", "-C", cwd, "-s", sandbox, "-m", model, "-o", outMsgFile];
  if (spec.ephemeral !== false && sandbox === "read-only") {
    args.push("--ephemeral");
  }
  if (effort) {
    args.push("-c", `model_reasoning_effort="${effort}"`);
  }
  for (const ip of imgPaths) {
    args.push("-i", ip);
  }
  args.push("--json", "-");

  return new Promise((resolve) => {
    const useShell = /\.cmd$/i.test(codexExe);
    const child = spawn(codexExe, args, {
      cwd,
      shell: useShell,
      windowsHide: true,
    });

    let stdoutBuf = "";
    let stderrBuf = "";
    let streamedText = "";

    const cleanupTmp = () => {
      try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
    };

    const timer = setTimeout(() => {
      try { child.kill(); } catch {}
      cleanupTmp();
      resolve({
        ok: false,
        error: "Codex vượt quá thời gian chờ.",
        text: streamedText,
        stderr: stderrBuf.slice(-800),
      });
    }, (spec.timeoutMin || 8) * 60 * 1000);

    child.stdout.on("data", (chunk) => {
      const s = chunk.toString("utf8");
      stdoutBuf += s;
      // Đọc các dòng JSONL để đẩy streaming text trực tiếp lên Canvas Node nếu có requestId
      const lines = stdoutBuf.split(/\r?\n/);
      stdoutBuf = lines.pop() || "";
      for (const line of lines) {
        if (!line.trim().startsWith("{")) continue;
        try {
          const ev = JSON.parse(line);
          const candidate =
            ev?.item?.text ||
            ev?.msg?.message ||
            ev?.delta ||
            (typeof ev?.text === "string" ? ev.text : "");
          if (candidate) {
            streamedText = candidate;
            if (spec.requestId) {
              const w = getMainWindow();
              if (w && !w.isDestroyed()) {
                w.webContents.send("chatgpt:stream-delta", { requestId: spec.requestId, text: streamedText });
              }
            }
          }
        } catch {}
      }
    });

    child.stderr.on("data", (d) => {
      stderrBuf += d.toString("utf8");
    });

    child.on("error", (err) => {
      clearTimeout(timer);
      cleanupTmp();
      resolve({ ok: false, error: String(err.message || err) });
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      let finalText = "";
      try {
        if (fs.existsSync(outMsgFile)) {
          finalText = fs.readFileSync(outMsgFile, "utf8").trim();
        }
      } catch {}
      if (!finalText) finalText = streamedText.trim();
      cleanupTmp();

      if (spec.requestId && finalText) {
        const w = getMainWindow();
        if (w && !w.isDestroyed()) {
          w.webContents.send("chatgpt:stream-delta", { requestId: spec.requestId, text: finalText, done: true });
        }
      }

      if (code === 0 || finalText) {
        resolve({
          ok: true,
          provider: "openai-codex",
          model,
          sandbox,
          text: finalText,
          stdout: finalText,
        });
      } else {
        resolve({
          ok: false,
          code,
          error: stderrBuf.trim().slice(-600) || `Codex exited with code ${code}`,
        });
      }
    });

    try {
      child.stdin.write(finalPrompt, "utf8");
      child.stdin.end();
    } catch {}
  });
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf8").trim();
        resolve(raw ? JSON.parse(raw) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function sendJson(res, status, data) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
  });
  res.end(JSON.stringify(data));
}

function startGatewayServer() {
  if (gatewayServer) return;
  gatewayServer = http.createServer(async (req, res) => {
    if (req.method === "OPTIONS") {
      res.writeHead(204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
      });
      res.end();
      return;
    }

    const urlPath = (req.url || "/").split("?")[0];
    try {
      if (req.method === "GET" && (urlPath === "/" || urlPath === "/health")) {
        const st = await chatgptDriver.status().catch(() => ({}));
        sendJson(res, 200, {
          ok: true,
          service: "chatgpt-plus-ecosystem-gateway",
          port: GATEWAY_PORT,
          projects: readDriverProjects(),
          hubs: Object.keys(HUB_URLS),
          status: st,
        });
        return;
      }

      if (req.method === "GET" && urlPath === "/v1/models") {
        const models = [
          { id: "codex-gpt-6.2-sol", capability: "text", desc: "OpenAI Codex Cục Bộ (gpt-6.2-sol siêu tốc 2s, 0 mở tab)" },
          { id: "codex-agent-workspace", capability: "text", desc: "OpenAI Codex Agent Toàn Quyền (đọc/ghi code trong Full Studio)" },
          { id: "chatgpt-plus-thinking", capability: "text", desc: "ChatGPT Plus Reasoning / Suy luận sâu" },
          { id: "chatgpt-k4-flow", capability: "text", desc: "Dự án K4 Phim Chuyện Trong Nhà (Asset Board + Prompt Flow)" },
          { id: "chatgpt-htpm-brand", capability: "text", desc: "Dự án HTPM / An Vượng / Feel Chicken" },
          { id: "chatgpt-deep-research", capability: "text", desc: "ChatGPT Plus Deep Research (Nghiên cứu sâu đa nguồn)" },
          { id: "chatgpt-image", capability: "image", desc: "ChatGPT Plus Image Engine (3 luồng song song)" },
          { id: "sora-video", capability: "video", desc: "OpenAI Sora Video (ChatGPT Plus)" },
        ];
        sendJson(res, 200, { object: "list", data: models });
        return;
      }

      if (req.method === "GET" && urlPath === "/v1/projects") {
        sendJson(res, 200, { ok: true, projects: readDriverProjects() });
        return;
      }

      if (req.method === "POST" && urlPath === "/v1/chat/completions") {
        const body = await readJsonBody(req);
        const reqModel = String(body.model || "chatgpt-plus-thinking");
        if (/^(codex|gpt-6)/i.test(reqModel)) {
          const cr = await runCodex({
            model: reqModel.replace(/^codex-/i, "") || "gpt-6.2-sol",
            messages: body.messages,
            prompt: body.prompt,
            images: body.images,
            project: body.project || "auto",
            reasoningEffort: body.reasoningEffort || body.reasoning_effort || "medium",
            sandbox: /workspace/i.test(reqModel) ? "workspace-write" : (body.sandbox || "read-only"),
            cwd: body.cwd,
          });
          if (!cr.ok) {
            sendJson(res, 500, { ok: false, error: cr.error || "Codex error" });
            return;
          }
          sendJson(res, 200, {
            id: "chatcmpl-codex-" + Date.now().toString(36),
            object: "chat.completion",
            created: Math.floor(Date.now() / 1000),
            model: cr.model,
            choices: [
              {
                index: 0,
                message: { role: "assistant", content: cr.text },
                finish_reason: "stop",
              },
            ],
          });
          return;
        }
        const r = await askChatGPT({
          model: body.model || "chatgpt-plus-thinking",
          messages: body.messages,
          prompt: body.prompt,
          images: body.images,
          files: body.files,
          project: body.project || "auto",
          mode: body.mode || "auto",
          keepChat: Boolean(body.keepChat),
          timeoutMin: body.timeoutMin,
        });
        sendJson(res, 200, {
          id: "chatcmpl-" + Date.now().toString(36),
          object: "chat.completion",
          created: Math.floor(Date.now() / 1000),
          model: body.model || "chatgpt-plus-thinking",
          projectUsed: r.projectUsed,
          convUrl: r.convUrl,
          choices: [
            {
              index: 0,
              message: { role: "assistant", content: r.text },
              finish_reason: "stop",
            },
          ],
        });
        return;
      }

      if (req.method === "POST" && urlPath === "/v1/images/generations") {
        const body = await readJsonBody(req);
        const items = await chatgptDriver.generateImages({
          prompt: body.prompt || "",
          ratio: body.ratio || body.size || "1:1",
          count: body.n || body.count || 1,
          images: body.images || [],
          keepChat: Boolean(body.keepChat),
        });
        sendJson(res, 200, {
          created: Math.floor(Date.now() / 1000),
          data: items.map((it) => ({
            mime: it.mime || "image/png",
            b64_json: Buffer.from(it.data).toString("base64"),
          })),
        });
        return;
      }

      if (req.method === "POST" && urlPath === "/v1/videos/sora") {
        const body = await readJsonBody(req);
        const r = await soraDriver.generateVideo(body);
        if (!r.ok) {
          sendJson(res, 500, { ok: false, error: r.error || "Sora error" });
          return;
        }
        if (body.outPath) {
          fs.mkdirSync(path.dirname(path.resolve(body.outPath)), { recursive: true });
          fs.writeFileSync(path.resolve(body.outPath), r.data);
          sendJson(res, 200, { ok: true, outPath: path.resolve(body.outPath), bytes: r.data.length });
          return;
        }
        sendJson(res, 200, {
          ok: true,
          mime: r.mime || "video/mp4",
          bytes: r.data.length,
          b64_json: Buffer.from(r.data).toString("base64"),
        });
        return;
      }

      if (req.method === "POST" && urlPath === "/v1/projects/sync") {
        const body = await readJsonBody(req);
        const r = await syncProject(body);
        sendJson(res, 200, r);
        return;
      }

      if (req.method === "POST" && urlPath === "/v1/tasks/schedule") {
        const body = await readJsonBody(req);
        const r = await scheduleTask(body);
        sendJson(res, 200, r);
        return;
      }

      if (req.method === "POST" && urlPath === "/v1/hub/open") {
        const body = await readJsonBody(req);
        const r = await openHub(body.target || "home");
        sendJson(res, 200, r);
        return;
      }

      if (req.method === "POST" && urlPath === "/v1/codex/exec") {
        const body = await readJsonBody(req);
        const r = await runCodex(body);
        sendJson(res, 200, r);
        return;
      }

      sendJson(res, 404, { ok: false, error: "Unknown route: " + urlPath });
    } catch (err) {
      sendJson(res, 500, { ok: false, error: String(err?.message || err) });
    }
  });

  gatewayServer.on("error", (err) => {
    if (err && err.code === "EADDRINUSE") {
      gatewayServer = null;
      return;
    }
    console.error("[chatgpt-gateway]", err.message || err);
  });

  gatewayServer.listen(GATEWAY_PORT, "127.0.0.1", () => {
    console.log(`[chatgpt-gateway] Cổng Hệ sinh thái ChatGPT Plus sẵn sàng tại http://127.0.0.1:${GATEWAY_PORT}`);
  });
}

function setup({ app, chatgpt, sora, winGetter }) {
  chatgptDriver = chatgpt;
  soraDriver = sora;
  getMainWindow = winGetter || (() => null);
  configFilePath = path.join(app.getPath("userData"), "chatgpt-driver.json");

  ipcMain.handle("chatgpt:ask", async (_e, job) => {
    try {
      return await askChatGPT(job || {});
    } catch (err) {
      return { ok: false, error: String(err?.message || err) };
    }
  });
  ipcMain.handle("chatgpt:list-projects", () => ({ ok: true, projects: readDriverProjects() }));
  ipcMain.handle("chatgpt:sync-project", async (_e, spec) => {
    try {
      return await syncProject(spec || {});
    } catch (err) {
      return { ok: false, error: String(err?.message || err) };
    }
  });
  ipcMain.handle("chatgpt:schedule-task", async (_e, spec) => {
    try {
      return await scheduleTask(spec || {});
    } catch (err) {
      return { ok: false, error: String(err?.message || err) };
    }
  });
  ipcMain.handle("chatgpt:open-hub", async (_e, target) => {
    try {
      return await openHub(target);
    } catch (err) {
      return { ok: false, error: String(err?.message || err) };
    }
  });
  ipcMain.handle("chatgpt:codex", async (_e, spec) => {
    try {
      return await runCodex(spec || {});
    } catch (err) {
      return { ok: false, error: String(err?.message || err) };
    }
  });

  startGatewayServer();
}

function destroy() {
  if (gatewayServer) {
    try { gatewayServer.close(); } catch {}
    gatewayServer = null;
  }
}

module.exports = {
  setup,
  destroy,
  askChatGPT,
  syncProject,
  openHub,
  scheduleTask,
  runCodex,
  findCodexExecutable,
  readDriverProjects,
  GATEWAY_PORT,
};
