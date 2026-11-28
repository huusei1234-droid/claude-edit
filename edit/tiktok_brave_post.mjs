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

// === STRICT FIXED SCHEDULE CONSTANTS: EXACTLY 2 VIDEOS / DAY (11:30 & 19:30 VN) ===
const MAX_POSTS_PER_DAY = 2;
const MIN_SLOT_GAP_MS = 4 * 60 * 60 * 1000; // Minimum 4h gap between Slot #1 (11:30) and Slot #2 (19:30)
const VN_TZ = "Asia/Ho_Chi_Minh";

const STATE_FILE = path.join(EDIT_DIR, "tiktok_last_post_state.json");
const HISTORY_FILE = path.join(EDIT_DIR, "tiktok_posted_history.json");
const LOCK_FILE = path.join(EDIT_DIR, "tiktok_post_lock.json");

const PY_CANDIDATES = [
  process.env.PYTHON || "",
  "C:\\Users\\001\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
  "C:\\Users\\Hang thu\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
].filter(Boolean);
const PY_EXE = PY_CANDIDATES.find((p) => fs.existsSync(p)) || "python";

const FFPROBE_CANDIDATES = [
  "C:\\Users\\001\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-9.0.2-full_build\\bin\\ffprobe.exe",
  "ffprobe",
];
const FFPROBE_EXE = FFPROBE_CANDIDATES.find((p) => p === "ffprobe" || fs.existsSync(p)) || "ffprobe";

function getVnDateStr(ms = Date.now()) {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: VN_TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(ms));
}

function isPidAlive(pid) {
  if (!pid || typeof pid !== "number") return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

const CANDIDATE_K4_MASTERS = [
  "G:\\Other computers\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu",
  "G:\\Máy tính khác\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu",
  "G:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu",
  "Z:\\Máy tính khác\\My Computer\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu",
  "Z:\\.shortcut-targets-by-id\\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\\hằng thu pharma\\05. Video Hoàn Thiện\\K4 - Mẹ Chồng Nàng Dâu",
];
const K4_MASTER_DIR = CANDIDATE_K4_MASTERS.find((p) => fs.existsSync(p)) || CANDIDATE_K4_MASTERS[0];
const SRC_DIR = path.join(K4_MASTER_DIR, "đã đăng");
const DST_DIR = path.join(SRC_DIR, "On air Tiktok");
const CLOUD_STATE_FILE = path.join(DST_DIR, ".tiktok_daily_state.json");
const CLOUD_HISTORY_FILE = path.join(DST_DIR, ".tiktok_posted_history.json");
const DEFAULT_TAGS = "#MeChongNangDau #PhimNgan #PhimDrama #DramaGiaDinh #PhimViet";

function parseArgs(argv) {
  const args = { mode: "post", caption: "", file: "", cover: "", force: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--login") args.mode = "login";
    else if (a === "--post") args.mode = "post";
    else if (a === "--status" || a === "--dry-run") args.mode = "status";
    else if (a === "--force") args.force = true;
    else if (a === "--caption" && argv[i + 1]) args.caption = argv[++i];
    else if (a === "--file" && argv[i + 1]) args.file = argv[++i];
    else if (a === "--cover" && argv[i + 1]) args.cover = argv[++i];
  }
  return args;
}

function readJsonSafe(p, fallback) {
  try {
    if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {}
  return fallback;
}

function loadMergedDailyState() {
  const today = getVnDateStr();
  const sLocal = readJsonSafe(STATE_FILE, {});
  const sCloud = readJsonSafe(CLOUD_STATE_FILE, {});

  // Pick whichever record matches today with higher dailyCount / newer lastPostedAt
  const candidates = [sLocal, sCloud].filter((s) => s && typeof s === "object");
  let best = { dailyDate: today, dailyCount: 0, maxPerDay: MAX_POSTS_PER_DAY, filesToday: [], lastPostedAt: 0, file: "", iso: "" };

  for (const c of candidates) {
    const cDate = c.dailyDate || (c.lastPostedAt ? getVnDateStr(c.lastPostedAt) : "");
    const cFiles = Array.isArray(c.filesToday) ? c.filesToday : c.file && cDate === today ? [c.file] : [];
    const cCount = cDate === today ? Math.max(Number(c.dailyCount || 0), cFiles.length) : 0;
    if (cCount > best.dailyCount || ((c.lastPostedAt || 0) > (best.lastPostedAt || 0) && cCount >= best.dailyCount)) {
      best = {
        dailyDate: today,
        dailyCount: cCount,
        maxPerDay: MAX_POSTS_PER_DAY,
        filesToday: cFiles,
        lastPostedAt: Number(c.lastPostedAt || 0),
        file: c.file || (cFiles[cFiles.length - 1] || ""),
        iso: c.iso || "",
      };
    }
  }
  return best;
}

function saveDailyState(stateObj) {
  const txt = JSON.stringify(stateObj, null, 2);
  fs.writeFileSync(STATE_FILE, txt, "utf8");
  try {
    fs.mkdirSync(DST_DIR, { recursive: true });
    fs.writeFileSync(CLOUD_STATE_FILE, txt, "utf8");
  } catch {}
}

function loadPostedHistorySet() {
  const set = new Set();
  for (const f of [HISTORY_FILE, CLOUD_HISTORY_FILE]) {
    const arr = readJsonSafe(f, []);
    if (Array.isArray(arr)) {
      for (const item of arr) {
        if (typeof item === "string") set.add(normalizeForMatch(item));
        else if (item && item.name) set.add(normalizeForMatch(item.name));
      }
    }
  }
  if (fs.existsSync(DST_DIR)) {
    for (const d of fs.readdirSync(DST_DIR, { withFileTypes: true })) {
      if (d.isFile() && d.name.toLowerCase().endsWith(".mp4")) {
        set.add(normalizeForMatch(d.name));
      }
    }
  }
  return set;
}

function recordPostedHistory(filename) {
  const nowIso = new Date().toISOString();
  for (const f of [HISTORY_FILE, CLOUD_HISTORY_FILE]) {
    try {
      const arr = readJsonSafe(f, []);
      const list = Array.isArray(arr) ? arr : [];
      if (!list.some((x) => (typeof x === "string" ? x === filename : x?.name === filename))) {
        list.push({ name: filename, postedAt: nowIso });
      }
      fs.mkdirSync(path.dirname(f), { recursive: true });
      fs.writeFileSync(f, JSON.stringify(list, null, 2), "utf8");
    } catch {}
  }
}

function cleanViTitle(raw) {
  let s = raw
    .replace(/\.mp4$/i, "")
    .replace(/^\d{6}\s+(?:K4\s+)?/i, "")
    .replace(/\(\s*(?:full|\d+)\s*\)/gi, "")
    .replace(/\b(?:full|final)\b$/i, "")
    .replace(/\bnhà trồng\b/gi, "nhà chồng")
    .replace(/\bchữ hiêu\b/gi, "chữ hiếu")
    .replace(/\btrong nha\b/gi, "trong nhà")
    .replace(/\bkhó thể sao\b/gi, "khó thế sao")
    .replace(/\s+/g, " ")
    .trim();
  if (s.length > 0) s = s[0].toUpperCase() + s.slice(1);
  return s;
}

function getViralCaptionAndBadge(filename) {
  try {
    const out = execFileSync(PY_EXE, [path.join(EDIT_DIR, "optimize_tiktok_viral.py"), "--caption", filename], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    const parsed = JSON.parse(out.trim());
    if (parsed && parsed.caption) return parsed;
  } catch {}
  return { caption: `${cleanViTitle(filename)} ${DEFAULT_TAGS}`, badge: cleanViTitle(filename).toUpperCase() };
}

function makeAutoCover(localVideoPath, titleSource) {
  // Strictly picks sharpest frame from video + 2-line title (no AI background poster)
  const out = path.join(EDIT_DIR, "tmp_tiktok_cover.png");
  const coverTitle = cleanViTitle(titleSource);
  execFileSync(PY_EXE, [path.join(EDIT_DIR, "make_tiktok_cover.py"), localVideoPath, out, coverTitle], {
    stdio: "inherit",
  });
  return out;
}

function normalizeForMatch(s) {
  return String(s || "")
    .toLowerCase()
    .replace(/#\S+/g, "")
    .replace(/\.mp4$/i, "")
    .replace(/^\d{6}\s+(?:k4\s+)?/i, "")
    .replace(/\(\s*(?:full|\d+)\s*\)/gi, "")
    .replace(/\b(?:final|full)\b/gi, "")
    .replace(/\bnhà trồng\b/g, "nhà chồng")
    .replace(/\btrong nha\b/g, "trong nhà")
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function probeDurationSec(filePath) {
  try {
    const out = execFileSync(
      FFPROBE_EXE,
      ["-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filePath],
      { encoding: "utf8", timeout: 8000, stdio: ["ignore", "pipe", "ignore"] }
    );
    const d = parseFloat(out.trim());
    return Number.isFinite(d) ? d : -1;
  } catch {
    return -1;
  }
}

function listCandidateMp4s() {
  const postedSet = loadPostedHistorySet();
  const results = [];

  // 1. Priority 1: Crisp episodes in K4_MASTER_DIR (keep masters in place, never delete from brand root!)
  if (fs.existsSync(K4_MASTER_DIR)) {
    const masterEntries = fs
      .readdirSync(K4_MASTER_DIR, { withFileTypes: true })
      .filter((d) => d.isFile() && d.name.toLowerCase().endsWith(".mp4"))
      .filter((d) => {
        const low = d.name.toLowerCase();
        // Skip multi-part full compilations ("tập full final.mp4") and draft Muse variant
        if (/\btập\s*full\b/i.test(low)) return false;
        if (/nha trang muse/i.test(low)) return false;
        return true;
      })
      .map((d) => {
        const full = path.join(K4_MASTER_DIR, d.name);
        const st = fs.statSync(full);
        const is261128 = /^261\d{3}\s+K4\b/i.test(d.name);
        return {
          name: d.name,
          full,
          mtimeMs: st.mtimeMs,
          isFull: false,
          keepMaster: true,
          priorityTier: is261128 ? 0 : 1,
        };
      })
      .sort((a, b) => {
        if (a.priorityTier !== b.priorityTier) return a.priorityTier - b.priorityTier;
        return a.name.localeCompare(b.name, "vi");
      });

    for (const item of masterEntries) {
      const norm = normalizeForMatch(item.name);
      if (postedSet.has(norm)) continue;
      results.push(item);
    }
  }

  // 2. Priority 2: Remaining files in SRC_DIR ("đã đăng\")
  if (fs.existsSync(SRC_DIR)) {
    const legacyFiles = fs
      .readdirSync(SRC_DIR, { withFileTypes: true })
      .filter((d) => d.isFile() && d.name.toLowerCase().endsWith(".mp4"))
      .map((d) => {
        const full = path.join(SRC_DIR, d.name);
        const st = fs.statSync(full);
        const isFull = /\bfull\b/i.test(d.name);
        return {
          name: d.name,
          full,
          mtimeMs: st.mtimeMs,
          isFull,
          keepMaster: false,
          priorityTier: isFull ? 3 : 2,
        };
      })
      .sort((a, b) => (a.priorityTier !== b.priorityTier ? a.priorityTier - b.priorityTier : a.mtimeMs - b.mtimeMs));

    for (const item of legacyFiles) {
      const norm = normalizeForMatch(item.name);
      if (postedSet.has(norm)) continue;
      results.push(item);
    }
  }

  return results;
}

async function preCleanStaleBlankTabs9333() {
  try {
    const res = await fetch("http://127.0.0.1:9333/json/list", { signal: AbortSignal.timeout(2500) });
    if (!res.ok) return false;
    const targets = await res.json();
    if (!Array.isArray(targets)) return true;
    for (const t of targets) {
      if (t.type === "page" && (t.url === "about:blank" || t.url.includes("tiktok.com/tiktokstudio/upload"))) {
        await fetch(`http://127.0.0.1:9333/json/close/${t.id}`, { signal: AbortSignal.timeout(1500) }).catch(() => {});
      }
    }
    return true;
  } catch {
    return false;
  }
}

async function connectMainBraveStudio() {
  const portAlive = await preCleanStaleBlankTabs9333();
  if (portAlive) {
    try {
      const browser = await chromium.connectOverCDP("http://127.0.0.1:9333", { timeout: 90000 });
      return { browser, context: browser.contexts()[0], usingMain9333: true, spawnedFallback: false };
    } catch (e) {
      console.warn("WARN: First connectOverCDP(:9333) attempt failed, retrying once...", e?.message || e);
      await new Promise((r) => setTimeout(r, 1500));
      const browser = await chromium.connectOverCDP("http://127.0.0.1:9333", { timeout: 90000 });
      return { browser, context: browser.contexts()[0], usingMain9333: true, spawnedFallback: false };
    }
  }

  // Launch Brave Studio via explorer.exe so it opens on user's desktop with port 9333
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
    await new Promise((r) => setTimeout(r, 800));
    if (await preCleanStaleBlankTabs9333()) {
      try {
        const browser = await chromium.connectOverCDP("http://127.0.0.1:9333", { timeout: 90000 });
        return { browser, context: browser.contexts()[0], usingMain9333: true, spawnedFallback: false };
      } catch {}
    }
  }

  // Fallback to isolated port 19333 ONLY if unattached Brave blocked port 9333 (never kill user's Brave!)
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
    await new Promise((r) => setTimeout(r, 700));
    try {
      const browser = await chromium.connectOverCDP("http://127.0.0.1:19333", { timeout: 60000 });
      return { browser, context: browser.contexts()[0], usingMain9333: false, spawnedFallback: true };
    } catch {}
  }
  throw new Error("Could not connect to Brave Studio (:9333) or fallback (:19333).");
}

async function main() {
  const args = parseArgs(process.argv);
  const dailyState = loadMergedDailyState();
  const todayVn = getVnDateStr();

  if (args.mode === "status") {
    const queue = listCandidateMp4s();
    const nextItem = queue[0] || null;
    const nextCap = nextItem ? getViralCaptionAndBadge(nextItem.name).caption : null;
    const nextDur = nextItem ? probeDurationSec(nextItem.full) : null;
    console.log(
      JSON.stringify(
        {
          schedule: "Fixed 2 videos/day at 11:30 & 19:30 (Asia/Ho_Chi_Minh)",
          todayVn,
          postedToday: `${dailyState.dailyCount}/${MAX_POSTS_PER_DAY}`,
          filesToday: dailyState.filesToday,
          lastPostedAtIso: dailyState.iso || null,
          queueRemaining: queue.length,
          nextUp: nextItem ? { name: nextItem.name, durationSec: nextDur, keepMaster: nextItem.keepMaster, caption: nextCap } : null,
          previewQueueTop6: queue.slice(0, 6).map((q) => q.name),
        },
        null,
        2
      )
    );
    return;
  }

  // Enforce STRICT 2 VIDEOS / DAY & 4-HOUR SLOT GAP (unless --force is explicitly passed)
  if (args.mode === "post" && !args.force) {
    if (fs.existsSync(LOCK_FILE)) {
      try {
        const lk = JSON.parse(fs.readFileSync(LOCK_FILE, "utf8"));
        if (lk.pid && lk.pid !== process.pid && isPidAlive(lk.pid) && Date.now() - (lk.startedAt || 0) < 20 * 60 * 1000) {
          console.log(`SKIPPED_LOCKED: Another TikTok upload (PID ${lk.pid}) is currently in progress.`);
          return;
        }
      } catch {}
    }

    if (dailyState.dailyDate === todayVn && dailyState.dailyCount >= MAX_POSTS_PER_DAY) {
      console.log(
        `SKIPPED_DAILY_LIMIT: Fixed limit ${dailyState.dailyCount}/${MAX_POSTS_PER_DAY} videos already posted on ${todayVn} (${dailyState.filesToday.join(", ")}). Next slot tomorrow at 11:30.`
      );
      return;
    }

    if (dailyState.lastPostedAt && Date.now() - dailyState.lastPostedAt < MIN_SLOT_GAP_MS) {
      const minsAgo = Math.round((Date.now() - dailyState.lastPostedAt) / 60000);
      console.log(
        `SKIPPED_SLOT_GAP: Last video '${dailyState.file}' posted ${minsAgo}m ago (< ${MIN_SLOT_GAP_MS / 60000}m minimum gap between 11:30 and 19:30).`
      );
      return;
    }
  }

  fs.writeFileSync(LOCK_FILE, JSON.stringify({ pid: process.pid, startedAt: Date.now() }), "utf8");
  let conn = null;
  let page = null;

  try {
    conn = await connectMainBraveStudio();
    const { context, usingMain9333 } = conn;
    console.log("CONNECTED_BRAVE:", usingMain9333 ? "Main Brave Studio (:9333)" : "Fallback Profile (:19333)");

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
      const isMaster = path.resolve(path.dirname(args.file)).toLowerCase() === path.resolve(K4_MASTER_DIR).toLowerCase();
      picked = { name: path.basename(args.file), full: args.file, keepMaster: isMaster };
    } else {
      const candidates = listCandidateMp4s();
      fs.mkdirSync(DST_DIR, { recursive: true });
      for (const cand of candidates) {
        const key = normalizeForMatch(cand.name);
        const alreadyOnChannel =
          key.length >= 10 && publishedNorms.some((p) => p.includes(key) || (key.length >= 18 && p.includes(key.slice(0, 18))));
        if (alreadyOnChannel) {
          recordPostedHistory(cand.name);
          if (!cand.keepMaster) {
            const dupDst = path.join(DST_DIR, cand.name);
            try {
              fs.renameSync(cand.full, dupDst);
            } catch {}
            console.log(`MOVED_ALREADY_POSTED: ${dupDst}`);
          } else {
            console.log(`RECORDED_ALREADY_POSTED_MASTER: ${cand.name}`);
          }
          continue;
        }
        picked = cand;
        break;
      }
    }

    if (!picked || !fs.existsSync(picked.full)) {
      console.log("NO_VIDEO: No unposted .mp4 files remaining in queue.");
      return;
    }

    const { caption: autoCaption, badge: hookBadge } = getViralCaptionAndBadge(picked.name);
    const captionText = (args.caption || autoCaption).trim();
    const localTemp = path.join(EDIT_DIR, "tmp_tiktok_upload.mp4");

    // Episodes dated 261126+ already contain a built-in Cold-Open Climax Hook; legacy clips get a 2.2s cold-open hook prepended
    const alreadyHasColdOpen = /^261\d{3}\s+K4\b/i.test(picked.name);
    if (alreadyHasColdOpen) {
      fs.copyFileSync(picked.full, localTemp);
    } else {
      try {
        execFileSync(PY_EXE, [path.join(EDIT_DIR, "optimize_tiktok_viral.py"), "--prepare", picked.full, localTemp], {
          stdio: "inherit",
        });
      } catch {
        fs.copyFileSync(picked.full, localTemp);
      }
    }

    // Extract sharpest frame from video + 2-line title (no AI background poster)
    const coverPath = args.cover && fs.existsSync(args.cover) ? args.cover : makeAutoCover(localTemp, picked.name || hookBadge);

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
    console.log(`UPLOADING [${dailyState.dailyCount + 1}/${MAX_POSTS_PER_DAY} today]: ${picked.name}`);
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
    recordPostedHistory(picked.name);
    let finalRecordedPath = picked.full;
    if (!picked.keepMaster) {
      const dstPath = path.join(DST_DIR, picked.name);
      fs.renameSync(picked.full, dstPath);
      finalRecordedPath = dstPath;
    }
    try {
      fs.unlinkSync(localTemp);
    } catch {}

    const refreshed = loadMergedDailyState();
    const filesToday = Array.from(new Set([...(refreshed.dailyDate === todayVn ? refreshed.filesToday : []), picked.name]));
    const updatedState = {
      dailyDate: todayVn,
      dailyCount: filesToday.length,
      maxPerDay: MAX_POSTS_PER_DAY,
      filesToday,
      lastPostedAt: Date.now(),
      file: picked.name,
      iso: new Date().toISOString(),
    };
    saveDailyState(updatedState);

    console.log(`POSTED_OK [${updatedState.dailyCount}/${MAX_POSTS_PER_DAY} on ${todayVn}]: ${finalRecordedPath}`);
    await page.waitForTimeout(2500);
  } finally {
    try {
      fs.unlinkSync(LOCK_FILE);
    } catch {}
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
