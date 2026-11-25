// Electron shell: serves the built canvas and drives Google Flow through its own window (flow-driver.js).
const { app, BrowserWindow, Menu, shell, dialog, ipcMain, clipboard } = require("electron");
const { spawn } = require("node:child_process");
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

// Chặn lỗi ống dẫn stdout/stderr (EPIPE khi mở từ full studido.exe không có console) và mọi lỗi mạng/CDP tạm thời làm tự tắt toàn bộ Studio
process.stdout?.on?.("error", () => {});
process.stderr?.on?.("error", () => {});

function writeLifecycleLog(event, detail) {
  try {
    const dir = path.join(process.env.APPDATA || require("node:os").homedir(), "infinite-canvas-flow");
    fs.mkdirSync(dir, { recursive: true });
    const logFile = path.join(dir, "studio-lifecycle.log");
    try {
      if (fs.existsSync(logFile) && fs.statSync(logFile).size > 262144) {
        const tail = fs.readFileSync(logFile, "utf8").slice(-131072);
        fs.writeFileSync(logFile, tail);
      }
    } catch {}
    const msg = typeof detail === "string" ? detail : (detail && (detail.stack || detail.message || JSON.stringify(detail))) || "";
    fs.appendFileSync(logFile, `[${new Date().toISOString()}] pid=${process.pid} ${event} ${msg}\n`);
  } catch {}
}

function safeWriteStdout(text) {
  try {
    if (process.stdout && process.stdout.writable) process.stdout.write(text);
  } catch {}
}

function detectHiddenAgentShell() {
  if (process.env.ANTIGRAVITY_AGENT || process.env.CLAUDECODE || process.env.CODEX_SANDBOX) return true;
  // Phát hiện kể cả khi một tab AI khác cố tình xóa biến ANTIGRAVITY_AGENT rồi gọi canvas\app.bat trong màn hình ẩn!
  if (process.platform === "win32") {
    try {
      const { execFileSync } = require("node:child_process");
      const out = execFileSync(
        "powershell.exe",
        [
          "-NoProfile",
          "-Command",
          "$c=" + process.pid + "; for($i=0;$i -lt 7 -and $c -gt 0;$i++){ $p=Get-CimInstance Win32_Process -Filter \"ProcessId=$c\" -ErrorAction SilentlyContinue; if(-not $p){break}; if($p.Name -match 'language_server|codex|claude'){ 'HIDDEN_AI'; break }; $c=$p.ParentProcessId }",
        ],
        { encoding: "utf8", timeout: 2500, windowsHide: true }
      );
      if (out && out.includes("HIDDEN_AI")) return true;
    } catch {}
  }
  return false;
}

const isHiddenAgentShell = detectHiddenAgentShell();
writeLifecycleLog("startup", `hiddenAgent=${isHiddenAgentShell}`);

process.on("uncaughtException", (err) => {
  writeLifecycleLog("uncaughtException", err);
  try { console.error("[studio uncaughtException]", err && (err.stack || err.message || err)); } catch {}
});
process.on("unhandledRejection", (reason) => {
  writeLifecycleLog("unhandledRejection", reason);
  try { console.error("[studio unhandledRejection]", reason && (reason.stack || reason.message || reason)); } catch {}
});

// isHiddenAgentShell đã được xác định ngay đầu tệp bằng cả biến môi trường lẫn cây tiến trình cha (language_server)

const WEB_PORT = 3100;
const root = app.isPackaged ? process.resourcesPath : path.resolve(__dirname, "..");
const webDir = app.isPackaged ? path.join(root, "web") : path.join(root, "app", "web", "dist");
const flow = require("./flow-driver");
const chatgpt = require("./chatgpt-driver");

const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ico": "image/x-icon", ".woff2": "font/woff2", ".woff": "font/woff", ".mp4": "video/mp4", ".wasm": "application/wasm" };

let server;
let muse2api;
let voiceStudio; // only set when this shell started it
let proxy;
let win;

// Data folder: the canvas/media/settings live in Chromium's profile (userData). The chosen folder is
// remembered in a small config file that stays in the default location so it can be read before startup.
const configFile = path.join(app.getPath("appData"), "infinite-canvas-flow-config.json");
function readConfig() { try { return JSON.parse(fs.readFileSync(configFile, "utf8")); } catch { return {}; } }
function writeConfig(cfg) { fs.mkdirSync(path.dirname(configFile), { recursive: true }); fs.writeFileSync(configFile, JSON.stringify(cfg, null, 2)); }

(function applyDataDir() {
  const cfg = readConfig();
  if (!cfg.dataDir) return;
  try {
    fs.mkdirSync(cfg.dataDir, { recursive: true });
    // one-time copy of the previous profile into an empty target folder (runs before Chromium opens any file)
    if (cfg.migrateFrom && fs.existsSync(cfg.migrateFrom) && fs.readdirSync(cfg.dataDir).length === 0) {
      fs.cpSync(cfg.migrateFrom, cfg.dataDir, { recursive: true });
    }
    delete cfg.migrateFrom;
    writeConfig(cfg);
    app.setPath("userData", cfg.dataDir);
  } catch (e) {
    console.error("Cannot use data folder", cfg.dataDir, e);
  }
})();

async function chooseDataDir() {
  // returns false when the user cancels; on success the app relaunches
  const current = app.getPath("userData");
  const { canceled, filePaths } = await dialog.showOpenDialog(win, { title: "Chọn thư mục lưu trữ", defaultPath: current, properties: ["openDirectory", "createDirectory"] });
  if (canceled || !filePaths[0]) return false;
  const target = path.resolve(filePaths[0]);
  if (target === path.resolve(current)) return false;
  const empty = fs.existsSync(target) && fs.readdirSync(target).length === 0;
  let migrate = false;
  if (empty) {
    const r = await dialog.showMessageBox(win, { type: "question", buttons: ["Chép dữ liệu hiện tại sang", "Bắt đầu trống"], defaultId: 0, message: "Thư mục mới đang trống.", detail: "Chép canvas, ảnh, video và cài đặt hiện tại sang thư mục mới?" });
    migrate = r.response === 0;
  }
  const r = await dialog.showMessageBox(win, { type: "info", buttons: ["Khởi động lại ngay", "Hủy"], defaultId: 0, message: "Cần khởi động lại để dùng thư mục mới.", detail: target });
  if (r.response !== 0) return false;
  writeConfig({ ...readConfig(), dataDir: target, ...(migrate ? { migrateFrom: current } : {}) });
  app.relaunch();
  app.exit(0);
  return true;
}

ipcMain.handle("desktop:get-data-dir", () => app.getPath("userData"));
ipcMain.handle("desktop:choose-data-dir", () => chooseDataDir());
ipcMain.handle("desktop:open-data-dir", () => shell.openPath(app.getPath("userData")));

function openMuse2apiDashboard() {
  const w = new BrowserWindow({ width: 1200, height: 800, title: "muse2api", autoHideMenuBar: true });
  w.loadURL("http://127.0.0.1:18610/dashboard").catch(() => {});
}

function copyMuse2apiKey() {
  try {
    clipboard.writeText(fs.readFileSync(path.join(muse2apiDir, "data", "api_key"), "utf8").trim());
    dialog.showMessageBox({ message: "Đã sao chép API key muse2api vào clipboard." });
  } catch (e) {
    dialog.showErrorBox("Không đọc được API key", `${e.message}

muse2api cần chạy ít nhất một lần.`);
  }
}

function buildMenu() {
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { label: "Tệp", submenu: [
      { label: "Chọn thư mục lưu trữ…", click: chooseDataDir },
      { label: "Mở thư mục lưu trữ", click: () => shell.openPath(app.getPath("userData")) },
      { type: "separator" },
      { label: "Thoát", role: "quit" },
    ] },
    { label: "muse2api", submenu: [
      { label: "Mở Dashboard (thêm tài khoản)", click: openMuse2apiDashboard },
      { label: "Sao chép API key", click: copyMuse2apiKey },
    ] },
    { label: "ChatGPT", submenu: [
      { label: "Mở cửa sổ ChatGPT (đăng nhập)", click: () => chatgpt.show().catch((e) => dialog.showErrorBox("ChatGPT", String(e.message || e))) },
    ] },
    { label: "Agent", submenu: [
      { label: "Kết nối Claude Agent", click: () => connectCanvasAgent(true) },
    ] },
    { label: "Xem", submenu: [{ role: "reload" }, { role: "toggleDevTools" }, { role: "togglefullscreen" }] },
  ]));
}

function startWebServer() {
  return new Promise((resolve, reject) => {
    server = http.createServer((req, res) => {
      const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
      let file = path.normalize(path.join(webDir, urlPath));
      if (!file.startsWith(webDir)) { res.writeHead(403).end(); return; }
      if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(webDir, "index.html"); // SPA fallback
      res.writeHead(200, { "Content-Type": MIME[path.extname(file)] || "application/octet-stream" });
      fs.createReadStream(file).pipe(res);
    });
    server.once("error", (err) => {
      if (err && err.code === "EADDRINUSE") {
        // Nếu cổng 3100 đã có tiến trình phục vụ web sẵn, dùng tiếp thay vì văng hộp thoại lỗi khởi động
        server = null;
        resolve();
        return;
      }
      reject(err);
    });
    server.listen(WEB_PORT, "127.0.0.1", resolve);
  });
}

// muse2api gateway (port 18610): optional, only started when the muse2api folder is present.
const muse2apiDir = path.join(root, "muse2api");
function startMuse2api() {
  if (!fs.existsSync(path.join(muse2apiDir, "pyproject.toml"))) return;
  const python = process.env.PYTHON || "python";
  muse2api = spawn(python, ["-m", "muse2api"], { cwd: muse2apiDir, env: { ...process.env }, windowsHide: true });
  muse2api.on("error", (e) => { try { console.error("muse2api:", e.message); } catch {} });
  muse2api.stdout.on("data", (d) => safeWriteStdout(`[muse2api] ${d}`));
  muse2api.stderr.on("data", (d) => safeWriteStdout(`[muse2api] ${d}`));
}

// VoiceStudio (backend on :3900): launches the installed app unless it is already running.
const voiceStudioExe = process.env.VOICESTUDIO_EXE || "C:/Program Files/VoiceStudio/VoiceStudio.exe";
function startVoiceStudio() {
  if (isHiddenAgentShell) return; // Không bật ngầm giao diện VoiceStudio trong màn hình ẩn của AI
  if (!fs.existsSync(voiceStudioExe)) return;
  const probe = http.get("http://127.0.0.1:3900/system/info", { timeout: 1500 }, (res) => { res.resume(); }); // already running: leave it alone
  probe.on("error", () => {
    voiceStudio = spawn(voiceStudioExe, [], { cwd: path.dirname(voiceStudioExe), windowsHide: false });
    voiceStudio.on("error", (e) => console.error("VoiceStudio:", e.message));
  });
  probe.on("timeout", () => probe.destroy());
}

// Local forwarding proxy (port 23210): lets the canvas call services that do not send CORS headers (e.g. VoiceStudio).
const proxyDir = app.isPackaged ? path.join(root, "canvas-proxy") : path.join(root, "app", "canvas-proxy");
function startProxy() {
  const entry = path.join(proxyDir, "index.js");
  if (!fs.existsSync(entry)) return;
  proxy = spawn(process.execPath, [entry], { cwd: proxyDir, stdio: "ignore", env: { ...process.env, ELECTRON_RUN_AS_NODE: "1" }, windowsHide: true });
  proxy.on("error", (e) => console.error("canvas-proxy:", e.message));
}

// Canvas Agent (port 17371): lets Claude Code drive the canvas through the infinite-canvas MCP.
// Started here unless already running; its URL + token are written into the page's localStorage so the panel connects itself.
const AGENT_URL = "http://127.0.0.1:17371";
const agentConfigFile = path.join(require("node:os").homedir(), ".infinite-canvas", "canvas-agent.json");
let canvasAgent;
function agentReady() {
  return new Promise((resolve) => {
    const req = http.get(`${AGENT_URL}/config`, { timeout: 1500 }, (res) => { res.resume(); resolve(res.statusCode === 200); });
    req.on("error", () => resolve(false));
    req.on("timeout", () => { req.destroy(); resolve(false); });
  });
}
async function startCanvasAgent() {
  if (await agentReady()) return true;
  if (!canvasAgent || canvasAgent.exitCode !== null) {
    canvasAgent = spawn("npx", ["-y", "@basketikun/canvas-agent@latest"], { shell: true, windowsHide: true });
    canvasAgent.on("error", (e) => { try { console.error("canvas-agent:", e.message); } catch {} });
    canvasAgent.stdout.on("data", (d) => safeWriteStdout(`[canvas-agent] ${d}`));
    canvasAgent.stderr.on("data", (d) => safeWriteStdout(`[canvas-agent] ${d}`));
  }
  for (let i = 0; i < 90; i++) {
    if (await agentReady()) return true;
    await new Promise((r) => setTimeout(r, 1000));
  }
  return false;
}
async function connectCanvasAgent(notify) {
  const ok = await startCanvasAgent();
  let token = "";
  try { token = JSON.parse(fs.readFileSync(agentConfigFile, "utf8")).token || ""; } catch {}
  if (!ok || !token || !win) {
    if (notify) dialog.showErrorBox("Không kết nối được Canvas Agent", "Cần Node.js/npx và mạng để tải @basketikun/canvas-agent lần đầu.");
    return;
  }
  const openPath = await win.webContents.executeJavaScript(`(async () => {
    localStorage.setItem("canvas-agent-url", ${JSON.stringify(AGENT_URL)});
    localStorage.setItem("canvas-agent-token", ${JSON.stringify(token)});
    try {
      const pid = await new Promise((res) => {
        const req = indexedDB.open("infinite-canvas");
        req.onsuccess = () => {
          const db = req.result;
          const storeName = db.objectStoreNames.contains("app_state")
            ? "app_state"
            : db.objectStoreNames.contains("keyvaluepairs")
              ? "keyvaluepairs"
              : null;
          if (!storeName) { db.close(); return res(null); }
          const g = db.transaction(storeName, "readonly").objectStore(storeName).get("infinite-canvas:canvas_store");
          g.onsuccess = () => {
            try {
              const parsed = typeof g.result === "string" ? JSON.parse(g.result) : g.result;
              const projs = parsed?.state?.projects || [];
              if (projs.length > 0) {
                db.close();
                // Nếu đang ở đúng 1 dự án hợp lệ thì giữ nguyên trang đó
                const curId = location.pathname.startsWith("/canvas/") ? location.pathname.split("/")[2] : "";
                if (curId && projs.some((p) => p.id === curId)) return res("/canvas/" + curId);
                const withExp = projs.find((p) => (p.nodes || []).some((n) => n.type === "export:folder"));
                return res("/canvas/" + (withExp || projs[0]).id);
              }
              // Nếu ổ C mới chưa có dự án nào -> tự khởi tạo 1 bảng Canvas mặc định để không bao giờ bị trang lỗi Not Found!
              const newId = "studio-main-" + Date.now().toString(36);
              const now = new Date().toISOString();
              const initStore = JSON.stringify({
                state: {
                  projects: [{
                    id: newId,
                    title: "Full Studio Canvas",
                    createdAt: now,
                    updatedAt: now,
                    nodes: [],
                    connections: [],
                    chatSessions: [],
                    activeChatId: null,
                    backgroundMode: "lines",
                    showImageInfo: false,
                    viewport: { x: 0, y: 0, k: 1 }
                  }],
                  deletedProjects: []
                },
                version: 0
              });
              const wtx = db.transaction(storeName, "readwrite");
              wtx.objectStore(storeName).put(initStore, "infinite-canvas:canvas_store");
              wtx.oncomplete = () => { db.close(); res("/canvas/" + newId); };
              wtx.onerror = () => { db.close(); res("/"); };
            } catch {
              db.close();
              res(null);
            }
          };
          g.onerror = () => { db.close(); res(null); };
        };
        req.onerror = () => res(null);
      });
      if (pid) return pid;
    } catch {}
    const link = document.querySelector('a[href^="/canvas/"]');
    return link ? link.getAttribute("href").split("?")[0] : "/";
  })()`);
  await win.loadURL(`http://127.0.0.1:${WEB_PORT}${openPath}#agentUrl=${encodeURIComponent(AGENT_URL)}&agentToken=${encodeURIComponent(token)}`); // auto-open valid canvas & connect via URL hash!
  if (notify) dialog.showMessageBox(win, { message: "Đã kết nối Canvas Agent. Mở phiên Claude Code mới để dùng." });
}

function stopAll() {
  if (canvasAgent && !canvasAgent.killed) {
    if (process.platform === "win32") spawn("taskkill", ["/pid", String(canvasAgent.pid), "/T", "/F"]);
    else canvasAgent.kill();
  }
  if (proxy && !proxy.killed) proxy.kill();
  if (muse2api && !muse2api.killed) {
    if (process.platform === "win32") spawn("taskkill", ["/pid", String(muse2api.pid), "/T", "/F"]);
    else muse2api.kill();
  }
  if (voiceStudio && !voiceStudio.killed) {
    if (process.platform === "win32") spawn("taskkill", ["/pid", String(voiceStudio.pid), "/T", "/F"]);
    else voiceStudio.kill();
  }
  flow.destroy();
  chatgpt.destroy();
  if (server) server.close();
}

// Giữ script Flow và ChatGPT Web trong cài đặt nhà cung cấp luôn khớp với thư mục flow-canvas/,
// đồng thời đặt ChatGPT Web (chatgpt::chatgpt-image) làm model tạo ảnh mặc định trên Canvas.
async function syncFlowScripts() {
  let scripts;
  try {
    const dir = path.join(root, "flow-canvas");
    scripts = {
      image: fs.readFileSync(path.join(dir, "flow-image-script.js"), "utf8"),
      video: fs.readFileSync(path.join(dir, "flow-video-script.js"), "utf8"),
      chatgptImage: fs.readFileSync(path.join(dir, "chatgpt-image-script.js"), "utf8"),
    };
  } catch { return; }
  const changed = await win.webContents.executeJavaScript(`(() => {
    const key = "infinite-canvas:ai_config_store";
    const raw = localStorage.getItem(key);
    if (!raw) return false;
    const data = JSON.parse(raw);
    const cfg = data && data.state && data.state.config;
    const channels = cfg && cfg.channels;
    if (!Array.isArray(channels)) return false;
    const scripts = ${JSON.stringify(scripts)};
    let changed = false;

    // 1. Đồng bộ kênh ChatGPT Web (tự động) & đặt làm model tạo ảnh mặc định
    let gptCh = channels.find((c) => c.id === "chatgpt");
    if (!gptCh) {
      gptCh = {
        id: "chatgpt",
        name: "ChatGPT Web (tự động)",
        baseUrl: "https://chatgpt.com",
        apiKey: "chatgpt-web",
        apiFormat: "openai",
        models: [{ name: "chatgpt-image", capability: "image", script: scripts.chatgptImage }],
      };
      channels.unshift(gptCh);
      changed = true;
    } else {
      if (gptCh.name !== "ChatGPT Web (tự động)") { gptCh.name = "ChatGPT Web (tự động)"; changed = true; }
      if (!gptCh.apiKey) { gptCh.apiKey = "chatgpt-web"; changed = true; }
      if (!Array.isArray(gptCh.models) || !gptCh.models.some((m) => m.name === "chatgpt-image")) {
        gptCh.models = [{ name: "chatgpt-image", capability: "image", script: scripts.chatgptImage }];
        changed = true;
      } else {
        for (const m of gptCh.models) {
          if (m.name === "chatgpt-image" && m.script !== scripts.chatgptImage) {
            m.script = scripts.chatgptImage;
            changed = true;
          }
        }
      }
    }

    // Đặt chatgpt::chatgpt-image làm model tạo ảnh mặc định nếu đang ở default::* hoặc flow::* lần đầu chuyển
    if (!cfg._chatgptDefaultApplied || cfg.imageModel === "default::gpt-image-2" || !cfg.imageModel) {
      cfg.imageModel = "chatgpt::chatgpt-image";
      cfg.model = "chatgpt::chatgpt-image";
      cfg._chatgptDefaultApplied = true;
      changed = true;
    }
    if (Array.isArray(cfg.models) && !cfg.models.includes("chatgpt::chatgpt-image")) {
      cfg.models = ["chatgpt::chatgpt-image", ...cfg.models.filter((x) => x !== "default::gpt-image-2")];
      changed = true;
    }

    // 2. Đồng bộ kênh Google Flow (tự động)
    for (const ch of channels) {
      if (ch.id !== "flow") continue;
      if (ch.name !== "Google Flow (tự động)") { ch.name = "Google Flow (tự động)"; changed = true; }
      const ren = { "flow-omni-flash": "flow-omni-1.2-flash", "flow-omni-flash-11": "flow-omni-1.1-flash" };
      const models = ch.models || [];
      const kept = models.filter((m) => !String(m.name).startsWith("flow-veo"));
      for (const m of kept) if (ren[m.name]) { m.name = ren[m.name]; changed = true; }
      const base = kept.find((m) => m.name === "flow-omni-1.2-flash");
      if (base && !kept.some((m) => m.name === "flow-omni-1.1-flash")) kept.splice(kept.indexOf(base) + 1, 0, { ...base, name: "flow-omni-1.1-flash" });
      if (kept.length !== models.length || kept.some((m, i) => m !== models[i])) { ch.models = kept; changed = true; }
      for (const k of Object.keys(cfg)) {
        const v = cfg[k];
        if (typeof v === "string" && v.startsWith("flow::") && ren[v.slice(6)]) { cfg[k] = "flow::" + ren[v.slice(6)]; changed = true; }
      }
      for (const m of ch.models || []) {
        const s = scripts[m.capability];
        if (s && m.script !== s) { m.script = s; changed = true; }
      }
    }
    if (changed) localStorage.setItem(key, JSON.stringify(data));
    return changed;
  })()`).catch(() => false);
  if (changed) win.webContents.reload(); // store đọc lại cài đặt khi tải trang
}

async function main() {
  await startWebServer();
  flow.setup(app);
  chatgpt.setup(app);
  startMuse2api();
  startVoiceStudio();
  startProxy();
  buildMenu();
  win = new BrowserWindow({ width: 1440, height: 900, title: "Infinite Canvas Flow", autoHideMenuBar: true, backgroundColor: "#0a0a0a", webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true } });
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: "deny" }; });
  win.webContents.on("render-process-gone", (_e, details) => {
    writeLifecycleLog("render-process-gone", details);
    if (details && details.reason !== "clean-exit") {
      setTimeout(() => {
        if (win && !win.isDestroyed()) win.reload();
      }, 800);
    }
  });
  win.on("unresponsive", () => writeLifecycleLog("window-unresponsive", ""));
  win.on("closed", () => writeLifecycleLog("window-closed", ""));
  await win.loadURL(`http://127.0.0.1:${WEB_PORT}`);
  await Promise.race([syncFlowScripts(), new Promise((r) => setTimeout(r, 8000))]).catch((e) => console.error("sync flow scripts:", e));
  console.log("[flow] đồng bộ script xong");
  connectCanvasAgent(false).catch((e) => console.error("canvas-agent connect:", e));
  // Tự động bật cửa sổ Brave chính (hiển thị thật 100%, không bao giờ chạy ẩn) khi người dùng mở Full Studio
  if (!isHiddenAgentShell) {
    setTimeout(() => {
      flow.show().catch((e) => writeLifecycleLog("auto-show-brave", e));
    }, 1800);
  }
  // agent có thể chết (vd. tiến trình cũ còn sót lúc mở lại app) -> tự bật lại, không tải lại trang
  setInterval(() => agentReady().then((ok) => { if (!ok) startCanvasAgent().catch(() => {}); }), 30000);
}

function attachSecondInstanceHandler() {
  app.on("second-instance", () => {
    // Nếu phiên hiện tại do AI bật ngầm (không có cửa sổ trên màn hình người dùng), tự nhả khóa và thoát ngay
    // để phiên thật người dùng vừa bấm mở lên bình thường, không bao giờ làm cửa sổ của người dùng tự tắt!
    if (isHiddenAgentShell) {
      try { stopAll(); } catch {}
      try { app.releaseSingleInstanceLock(); } catch {}
      app.exit(0);
      return;
    }
    if (win) {
      if (win.isMinimized()) win.restore();
      win.show();
      win.focus();
    }
  });
}

const gotInitialLock = app.requestSingleInstanceLock();
if (gotInitialLock) {
  attachSecondInstanceHandler();
  app.whenReady().then(main).catch((e) => { dialog.showErrorBox("Lỗi khởi động", String(e)); app.quit(); });
} else if (isHiddenAgentShell) {
  // AI gọi trùng khi đã có phiên khác chạy -> thoát êm
  app.quit();
} else {
  // Người dùng mở app nhưng đang vướng khóa (có thể từ phiên AI chạy ngầm vừa nhận lệnh nhả khóa): chờ 1.2s rồi lấy lại khóa!
  app.whenReady().then(async () => {
    for (let i = 0; i < 6; i++) {
      await new Promise((r) => setTimeout(r, 250));
      if (app.requestSingleInstanceLock()) {
        attachSecondInstanceHandler();
        await main();
        return;
      }
    }
    app.quit();
  }).catch((e) => { dialog.showErrorBox("Lỗi khởi động", String(e)); app.quit(); });
}
app.on("window-all-closed", () => { writeLifecycleLog("window-all-closed", ""); app.quit(); });
app.on("before-quit", () => { writeLifecycleLog("before-quit", ""); stopAll(); });
