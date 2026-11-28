import fs from "node:fs";
import path from "node:path";
import puppeteer from "puppeteer-core";

const OUT_DIR = "C:\\AI\\full studio\\huu\\chatgpt_migration_huusei1234";
fs.mkdirSync(OUT_DIR, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function clickVisibleBySelector(page, selector) {
  const handles = await page.$$(selector);
  for (const h of handles) {
    const box = await h.boundingBox().catch(() => null);
    if (box && box.width > 4 && box.height > 4) {
      await h.click();
      return true;
    }
  }
  return false;
}

async function clickVisibleMenuItemMatching(page, regex) {
  const items = await page.$$('[role="menuitem"], [role="option"]');
  for (const it of items) {
    const box = await it.boundingBox().catch(() => null);
    if (!box || box.width <= 4 || box.height <= 4) continue;
    const txt = await it.evaluate((e) => (e.innerText || "").trim());
    if (regex.test(txt)) {
      await it.click();
      return txt;
    }
  }
  return null;
}

async function extractProjectSettings(page, pid) {
  await page.goto(`https://chatgpt.com/g/${pid}/project`, {
    waitUntil: "domcontentloaded",
    timeout: 35000,
  });
  await page.bringToFront();
  await sleep(2800);

  // Wait up to 6s for Project actions button
  for (let i = 0; i < 12; i++) {
    const ok = await page.$('button[aria-label="Project actions"]');
    if (ok) break;
    await sleep(400);
  }

  let projName = pid;
  let instructions = "";
  let settingsRaw = "";

  const clickedPa = await clickVisibleBySelector(page, 'button[aria-label="Project actions"]');
  if (clickedPa) {
    await sleep(900);
    const hit = await clickVisibleMenuItemMatching(page, /project settings|instructions|cài đặt dự án|hướng dẫn/i);
    if (hit) {
      await sleep(1400);
      const info = await page.evaluate(() => {
        const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
        const dlg = dlgs[dlgs.length - 1];
        if (!dlg) return null;
        const nameInput = dlg.querySelector("input");
        const areas = Array.from(dlg.querySelectorAll("textarea, [contenteditable='true']"));
        return {
          raw: (dlg.innerText || "").trim(),
          name: nameInput ? (nameInput.value || "").trim() : "",
          instructions: areas
            .map((a) => (a.value !== undefined ? a.value : a.innerText) || "")
            .map((s) => s.trim())
            .filter(Boolean)
            .join("\n\n"),
        };
      });
      if (info) {
        if (info.name) projName = info.name;
        instructions = info.instructions;
        settingsRaw = info.raw;
      }
      await page.keyboard.press("Escape").catch(() => {});
      await sleep(500);
    }
  }

  // Fallback project name from h1 or title
  if (projName === pid) {
    projName = await page.evaluate(() => {
      const h1 = document.querySelector("main h1, h1");
      return (h1?.innerText || document.title.replace(/\s*-\s*ChatGPT.*$/i, "") || "").trim();
    });
  }

  // Check Sources tab
  const sources = await page.evaluate(async () => {
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    const btns = Array.from(document.querySelectorAll("main button, [role='tab']"));
    const srcBtn = btns.find((b) => /^(sources|files|nguồn|tệp)(\s*\(\d+\)|\s*\d+)?$/i.test((b.innerText || "").trim()));
    if (!srcBtn) return { hasFiles: false, raw: "" };
    srcBtn.click();
    await wait(1200);
    const raw = (document.querySelector("main")?.innerText || "").trim();
    const empty = /Give ChatGPT more context|Add sources to give ChatGPT/i.test(raw);
    return { hasFiles: !empty, raw };
  });

  // Switch back to Chats tab and collect all project chat links
  const projChats = await page.evaluate(async (projectId) => {
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    const btns = Array.from(document.querySelectorAll("main button, [role='tab']"));
    const chatBtn = btns.find((b) => /^(chats|trò chuyện|cuộc trò chuyện)/i.test((b.innerText || "").trim()));
    if (chatBtn) {
      chatBtn.click();
      await wait(1000);
    }
    const main = document.querySelector("main");
    if (main) {
      const scrollers = [main, ...Array.from(main.querySelectorAll("div"))].filter(
        (el) => el.scrollHeight > el.clientHeight + 30
      );
      for (const sc of scrollers) {
        let prev = -1;
        for (let i = 0; i < 15; i++) {
          sc.scrollTop = sc.scrollHeight;
          await wait(300);
          if (sc.scrollTop === prev) break;
          prev = sc.scrollTop;
        }
      }
    }
    const out = new Map();
    for (const a of Array.from((main || document).querySelectorAll("a[href*='/c/']"))) {
      const href = a.getAttribute("href") || "";
      const m = href.match(/\/c\/([a-zA-Z0-9-]+)/);
      if (m && (href.includes(projectId) || (main && main.contains(a)))) {
        out.set(m[1], {
          id: m[1],
          projectId,
          href,
          title: (a.innerText || "").trim().split("\n")[0] || m[1],
          previewText: (a.innerText || "").trim(),
        });
      }
    }
    return Array.from(out.values());
  }, pid);

  return { id: pid, name: projName, instructions, settingsRaw, sources, projChats };
}

async function extractPersonalizationAndMemories(page) {
  await page.goto("https://chatgpt.com/", { waitUntil: "domcontentloaded", timeout: 35000 });
  await page.bringToFront();
  await sleep(2500);

  // Open sidebar if collapsed
  await clickVisibleBySelector(page, 'button[aria-label="Show sidebar"], button[aria-label="Open sidebar"]');
  await sleep(800);

  // Click profile menu
  const openedProf = await clickVisibleBySelector(
    page,
    'button[aria-label="Open profile menu"], [data-testid="accounts-profile-button"]'
  );
  let accountMenuSummary = "";
  if (openedProf) {
    await sleep(900);
    accountMenuSummary = await page.evaluate(() => {
      const menus = Array.from(document.querySelectorAll('[role="menu"]'))
        .map((m) => (m.innerText || "").trim())
        .filter((t) => /log out|upgrade|personalization|settings/i.test(t));
      return menus.join("\n---\n");
    });
    await clickVisibleMenuItemMatching(page, /^personalization$|^cá nhân hóa$/i);
    await sleep(2200);
  }

  // Capture whatever opened (either dialog OR full page main!)
  const persPage = await page.evaluate(() => {
    const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
    const container = dlgs.length > 0 ? dlgs[dlgs.length - 1] : document.querySelector("main") || document.body;
    const fields = Array.from(
      container.querySelectorAll("textarea, input[type='text'], [contenteditable='true']")
    ).map((el) => ({
      tag: el.tagName,
      placeholder: el.getAttribute("placeholder") || "",
      aria: el.getAttribute("aria-label") || "",
      value: ((el.value !== undefined ? el.value : el.innerText) || "").trim(),
    }));
    const buttons = Array.from(container.querySelectorAll("button"))
      .map((b) => (b.innerText || "").trim())
      .filter(Boolean);
    return {
      url: location.href,
      rawText: (container.innerText || "").trim(),
      fields: fields.filter((f) => f.value || f.placeholder),
      buttons,
    };
  });

  // Click "Manage" / "Manage memories" button if present!
  let memoriesRaw = "";
  let memoryItems = [];
  const btns = await page.$$("button, a");
  for (const b of btns) {
    const box = await b.boundingBox().catch(() => null);
    if (!box || box.width <= 4) continue;
    const txt = await b.evaluate((e) => (e.innerText || "").trim());
    if (/^manage$|^manage memories$|^quản lý$/i.test(txt)) {
      await b.click();
      await sleep(1800);
      const memData = await page.evaluate(async () => {
        const wait = (ms) => new Promise((r) => setTimeout(r, ms));
        const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
        const target = dlgs.length > 0 ? dlgs[dlgs.length - 1] : document.querySelector("main") || document.body;
        const scrollers = [target, ...Array.from(target.querySelectorAll("div"))].filter(
          (el) => el.scrollHeight > el.clientHeight + 20
        );
        for (const sc of scrollers) {
          let prev = -1;
          for (let i = 0; i < 25; i++) {
            sc.scrollTop = sc.scrollHeight;
            await wait(300);
            if (sc.scrollTop === prev) break;
            prev = sc.scrollTop;
          }
        }
        const rows = Array.from(target.querySelectorAll("tr, li, [role='row'], [data-testid*='memory']"))
          .map((r) => (r.innerText || "").trim())
          .filter((t) => t && t.length > 2 && !/^(memories|saved memories|delete all|search memories)$/i.test(t));
        return {
          raw: (target.innerText || "").trim(),
          rows: Array.from(new Set(rows)),
        };
      });
      memoriesRaw = memData.raw;
      memoryItems = memData.rows;
      await page.keyboard.press("Escape").catch(() => {});
      await sleep(400);
      break;
    }
  }

  return {
    accountMenuSummary,
    url: persPage.url,
    rawText: persPage.rawText,
    fields: persPage.fields,
    memoriesRaw,
    memoryItems,
  };
}

async function extractFullConversation(page, conv) {
  const url = conv.href.startsWith("http") ? conv.href : `https://chatgpt.com${conv.href}`;
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 40000 });
  await page.bringToFront();

  // Wait up to 12s for [data-turn-key] or non-empty transcript
  const start = Date.now();
  while (Date.now() - start < 12000) {
    const hasTurns = await page
      .evaluate(() => {
        const turns = document.querySelectorAll("[data-turn-key], [data-virtualized-turn]");
        if (turns.length > 0) return true;
        const tr = document.querySelector('[data-rail-chat-transcript="true"]');
        return tr && (tr.innerText || "").trim().length > 20;
      })
      .catch(() => false);
    if (hasTurns) break;
    await sleep(450);
  }
  await sleep(700);

  // Scroll UP to the very top until "Loading older messages" is gone, then sweep TOP -> BOTTOM collecting all virtualized [data-turn-key] turns in exact sequence!
  const result = await page.evaluate(async () => {
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));

    function findScrollHost() {
      const turn = document.querySelector("[data-turn-key], [data-rail-chat-transcript='true']");
      let el = turn ? turn.parentElement : document.querySelector("main");
      while (el && el !== document.body) {
        const st = getComputedStyle(el);
        if (
          (st.overflowY === "auto" || st.overflowY === "scroll") &&
          el.scrollHeight > el.clientHeight + 20
        ) {
          return el;
        }
        el = el.parentElement;
      }
      // Fallback: largest scrollable div in main
      const cands = Array.from(document.querySelectorAll("main div, div")).filter(
        (d) => d.scrollHeight > d.clientHeight + 40
      );
      cands.sort((a, b) => b.scrollHeight - a.scrollHeight);
      return cands[0] || document.scrollingElement || document.documentElement;
    }

    // 1. Scroll up repeatedly until we reach true top and "Loading older messages" disappears
    for (let round = 0; round < 25; round++) {
      const sc = findScrollHost();
      if (sc) sc.scrollTop = 0;
      await wait(650);
      const bodyTxt = document.body?.innerText || "";
      const stillLoadingOlder = /Loading older messages|Đang tải tin nhắn cũ/i.test(bodyTxt);
      if (!stillLoadingOlder && (!sc || sc.scrollTop === 0)) {
        // One extra check after 500ms in case a batch just triggered
        await wait(500);
        if (!/Loading older messages|Đang tải tin nhắn cũ/i.test(document.body?.innerText || "")) {
          if (!sc || sc.scrollTop === 0) break;
        }
      }
    }

    // 2. Sweep from top (0) down to bottom, recording turns in exact order
    const orderedKeys = [];
    const turnMap = new Map();

    function harvestVisibleTurns() {
      const nodes = Array.from(document.querySelectorAll("[data-turn-key]"));
      for (const n of nodes) {
        const key = n.getAttribute("data-turn-key") || "";
        if (!key) continue;
        const raw = (n.innerText || "").trim();
        const imgs = Array.from(n.querySelectorAll("img"))
          .map((im) => ({
            alt: im.getAttribute("alt") || "",
            src: im.getAttribute("src") || "",
          }))
          .filter((im) => im.src && !im.src.startsWith("data:"));

        if (!turnMap.has(key)) {
          orderedKeys.push(key);
        }
        // Keep the longest rendered text for this turnKey (in case markdown was still expanding)
        const prev = turnMap.get(key);
        if (!prev || raw.length >= prev.raw.length) {
          let role = "turn";
          let cleanText = raw;
          if (/^You said:\s*/i.test(raw)) {
            role = "user";
            cleanText = raw.replace(/^You said:\s*/i, "").trim();
          } else if (/^ChatGPT said:\s*/i.test(raw)) {
            role = "assistant";
            cleanText = raw.replace(/^ChatGPT said:\s*/i, "").trim();
          } else if (/^Bạn đã nói:\s*/i.test(raw)) {
            role = "user";
            cleanText = raw.replace(/^Bạn đã nói:\s*/i, "").trim();
          }
          turnMap.set(key, { key, role, raw, text: cleanText, images: imgs });
        }
      }
    }

    const sc = findScrollHost();
    if (sc && sc.scrollHeight > sc.clientHeight + 20) {
      sc.scrollTop = 0;
      await wait(400);
      harvestVisibleTurns();

      let guard = 0;
      while (guard < 120) {
        guard++;
        const step = Math.max(300, Math.floor(sc.clientHeight * 0.65));
        const prevTop = sc.scrollTop;
        sc.scrollTop = Math.min(sc.scrollHeight, sc.scrollTop + step);
        await wait(380);
        harvestVisibleTurns();
        if (sc.scrollTop >= sc.scrollHeight - sc.clientHeight - 5 || sc.scrollTop === prevTop) {
          break;
        }
      }
      // Final harvest at bottom
      sc.scrollTop = sc.scrollHeight;
      await wait(500);
      harvestVisibleTurns();
    } else {
      harvestVisibleTurns();
    }

    const turns = orderedKeys.map((k, idx) => {
      const t = turnMap.get(k);
      return {
        index: idx + 1,
        turnKey: t.key,
        role: t.role,
        text: t.text,
        images: t.images,
      };
    });

    const fallbackTranscript =
      turns.length === 0
        ? (
            document.querySelector('[data-rail-chat-transcript="true"]')?.innerText ||
            document.querySelector("main")?.innerText ||
            ""
          ).trim()
        : "";

    return {
      pageTitle: document.title.replace(/\s*-\s*ChatGPT.*$/i, "").trim(),
      turns,
      fallbackTranscript,
    };
  });

  return {
    id: conv.id,
    projectId: conv.projectId || null,
    href: conv.href,
    title: (conv.title || "").split("\n")[0].trim() || result.pageTitle || conv.id,
    pageTitle: result.pageTitle,
    turnCount: result.turns.length,
    turns: result.turns,
    fallbackTranscript: result.fallbackTranscript,
  };
}

async function main() {
  const browser = await puppeteer.connect({
    browserURL: "http://127.0.0.1:9333",
    defaultViewport: null,
  });

  // Load previously discovered chat list from overview_scan.json + 00_full_export.json so we don't miss anything
  const allChatMap = new Map();
  const prevJsonPath = path.join(OUT_DIR, "00_full_export.json");
  if (fs.existsSync(prevJsonPath)) {
    const prev = JSON.parse(fs.readFileSync(prevJsonPath, "utf8"));
    for (const c of prev.conversations || []) {
      allChatMap.set(c.id, {
        id: c.id,
        projectId: c.projectId || null,
        href: c.href,
        title: c.title,
      });
    }
  }

  const page = await browser.newPage();
  try {
    await page.bringToFront();

    // 1. Personalization & Memories
    console.log("[1/4] Extracting Personalization & Saved Memories...");
    const personalization = await extractPersonalizationAndMemories(page);
    console.log(
      `  Account menu: ${personalization.accountMenuSummary.replace(/\n/g, " | ").slice(0, 120)}`
    );
    console.log(
      `  Personalization fields: ${personalization.fields.length}, memoryItems: ${personalization.memoryItems.length}`
    );

    // 2. Also do a fresh sidebar scan in case any older chats appear on scroll
    await page.goto("https://chatgpt.com/", { waitUntil: "domcontentloaded", timeout: 30000 });
    await sleep(2200);
    await clickVisibleBySelector(page, 'button[aria-label="Show sidebar"], button[aria-label="Open sidebar"]');
    await sleep(800);
    const sidebarChats = await page.evaluate(async () => {
      const wait = (ms) => new Promise((r) => setTimeout(r, ms));
      const nav = document.querySelector("nav");
      if (!nav) return { projs: [], chats: [] };
      const scrollers = [nav, ...Array.from(nav.querySelectorAll("div"))].filter(
        (el) => el.scrollHeight > el.clientHeight + 30
      );
      for (const sc of scrollers) {
        let prev = -1;
        for (let i = 0; i < 30; i++) {
          sc.scrollTop = sc.scrollHeight;
          await wait(320);
          if (sc.scrollTop === prev) break;
          prev = sc.scrollTop;
        }
      }
      const projs = [];
      const chats = [];
      for (const a of Array.from(nav.querySelectorAll("a[href]"))) {
        const href = a.getAttribute("href") || "";
        const txt = (a.innerText || "").trim();
        const pm = href.match(/\/g\/(g-p-[a-zA-Z0-9-]+)/);
        if (pm) projs.push(pm[1]);
        const cm = href.match(/\/c\/([a-zA-Z0-9-]+)/);
        if (cm) {
          chats.push({
            id: cm[1],
            projectId: pm ? pm[1] : null,
            href,
            title: txt.split("\n")[0] || cm[1],
          });
        }
      }
      return { projs: Array.from(new Set(projs)), chats };
    });

    const projIds = new Set([
      "g-p-6ac5c68cc60c8191bab63b740e910809",
      "g-p-6afbde0b943481919c6ec31a3b4f8642",
      ...sidebarChats.projs,
    ]);
    for (const c of sidebarChats.chats) {
      if (!allChatMap.has(c.id) || c.projectId) {
        allChatMap.set(c.id, c);
      }
    }

    // 3. Projects
    console.log(`[2/4] Extracting ${projIds.size} Projects...`);
    const projects = [];
    for (const pid of projIds) {
      const pInfo = await extractProjectSettings(page, pid);
      console.log(
        `  Project [${pInfo.name}] (${pid}): instructions=${pInfo.instructions.length} chars, hasFiles=${pInfo.sources.hasFiles}, chats=${pInfo.projChats.length}`
      );
      for (const pc of pInfo.projChats) {
        allChatMap.set(pc.id, pc);
      }
      projects.push(pInfo);
    }

    // 4. All Conversations
    const convList = Array.from(allChatMap.values());
    console.log(`[3/4] Sweeping full virtualized transcripts for ${convList.length} conversations...`);
    const conversations = [];
    for (let i = 0; i < convList.length; i++) {
      const c = convList[i];
      const full = await extractFullConversation(page, c);
      const totalChars = full.turns.reduce((acc, t) => acc + t.text.length, 0);
      console.log(
        `  [${i + 1}/${convList.length}] ${full.title.slice(0, 50)} -> ${full.turnCount} turns (${totalChars} chars)`
      );
      conversations.push(full);
    }

    const payload = {
      exportedAt: new Date().toISOString(),
      personalization,
      projects,
      conversations,
    };
    fs.writeFileSync(prevJsonPath, JSON.stringify(payload, null, 2), "utf8");
    console.log(`[4/4] Saved full JSON export (${conversations.length} chats) -> ${prevJsonPath}`);
  } finally {
    await page.close().catch(() => {});
    browser.disconnect();
  }
}

main().catch((err) => {
  console.error("FATAL:", err);
  process.exit(1);
});
