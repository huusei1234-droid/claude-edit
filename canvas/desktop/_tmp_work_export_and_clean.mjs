import fs from "node:fs";
import path from "node:path";
import puppeteer from "puppeteer-core";

const OUT_DIR = "C:\\AI\\full studio\\huu\\chatgpt_migration_huusei1234";
fs.mkdirSync(OUT_DIR, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const WORK_CHATS = [
  {
    id: "6ac2a590-bff4-83ec-9dae-9d393aeb1b1a",
    projectId: "g-p-6ac5c68cc60c8191bab63b740e910809",
    projectName: "K4 Phim Chuyện Trong Nhà",
    href: "/g/g-p-6ac5c68cc60c8191bab63b740e910809/c/6ac2a590-bff4-83ec-9dae-9d393aeb1b1a",
    title: "Phim Chuyện Trong Nhà",
  },
  {
    id: "6ac608aa-96fc-83ec-91dd-19ee2ceb9169",
    projectId: "g-p-6ac5c68cc60c8191bab63b740e910809",
    projectName: "K4 Phim Chuyện Trong Nhà",
    href: "/g/g-p-6ac5c68cc60c8191bab63b740e910809/c/6ac608aa-96fc-83ec-91dd-19ee2ceb9169",
    title: "Viết kịch bản gia đình",
  },
  {
    id: "6ad0a4c3-6d04-83ec-a0a8-624746013e68",
    projectId: "g-p-6ac5c68cc60c8191bab63b740e910809",
    projectName: "K4 Phim Chuyện Trong Nhà",
    href: "/g/g-p-6ac5c68cc60c8191bab63b740e910809/c/6ad0a4c3-6d04-83ec-a0a8-624746013e68",
    title: "Phân tích kịch bản gia đình",
  },
  {
    id: "6b03c911-cc6c-83ec-9af5-9c1e981a9b37",
    projectId: "g-p-6afbde0b943481919c6ec31a3b4f8642",
    projectName: "HTPM",
    href: "/g/g-p-6afbde0b943481919c6ec31a3b4f8642/c/6b03c911-cc6c-83ec-9af5-9c1e981a9b37",
    title: "Phân tích sản phẩm HTPM",
  },
  {
    id: "6b01b856-ffa0-83ec-a9ed-25894217bfb7",
    projectId: null,
    projectName: "General",
    href: "/c/6b01b856-ffa0-83ec-a9ed-25894217bfb7",
    title: "Viết content quảng cáo",
  },
];

const TRIVIAL_CHATS_TO_DELETE = [
  { id: "6ae32d8b-5350-83ec-9e2b-ad5bd72d288c", title: "CT tủ" },
  { id: "6b05a422-4ed8-83ec-853d-588ce0df42b6", title: "Sửa tủ lạnh hư" },
  { id: "6b05669a-66d4-83ec-b26a-d844dd746e16", title: "Chở bé bằng xe máy" },
  { id: "6b04ee8f-b8a0-83ec-ae32-582b1859dc85", title: "Khắc phục đưa nôi yếu" },
  { id: "6b044f91-e6a8-83ec-9758-494cb5942f68", title: "Khắc phục RustDesk" },
  { id: "6b01d267-ff1c-83ec-82be-f1fc60eb24a9", title: "Bố trí bàn gọn hơn" },
  { id: "6b01225d-5e98-83ec-9a31-5bb169519ded", title: "Hỏi về Hưng Huỳnh" },
  { id: "6b011d48-7b00-83ec-946a-ccfe51981c1c", title: "Học nghề sắt" },
  { id: "6b0083de-434c-83ec-a366-7fe51060e237", title: "Kiểm tra phiên bản Windows_skip" },
  { id: "6b0083de-434c-83ec-a366-7fe5e060e237", title: "Kiểm tra phiên bản Windows" },
];

async function extractPersonalization(page) {
  await page.goto("https://chatgpt.com/", { waitUntil: "domcontentloaded", timeout: 35000 });
  await page.bringToFront();
  await sleep(2500);

  // Click Show sidebar if visible
  const sbBtns = await page.$$('button[aria-label="Show sidebar"], button[aria-label="Open sidebar"]');
  for (const b of sbBtns) {
    const box = await b.boundingBox().catch(() => null);
    if (box && box.width > 4) {
      await b.click();
      await sleep(900);
      break;
    }
  }

  // Click Open profile menu
  const profBtns = await page.$$('button[aria-label="Open profile menu"], [data-testid="accounts-profile-button"]');
  for (const pb of profBtns) {
    const box = await pb.boundingBox().catch(() => null);
    if (box && box.width > 4) {
      await pb.click();
      await sleep(900);
      break;
    }
  }

  // Click Personalization menuitem
  const mItems = await page.$$('[role="menuitem"]');
  for (const it of mItems) {
    const box = await it.boundingBox().catch(() => null);
    if (!box || box.width <= 4) continue;
    const t = await it.evaluate((e) => (e.innerText || "").trim());
    if (/^personalization$|^cá nhân hóa$/i.test(t)) {
      await it.click();
      await sleep(2800);
      break;
    }
  }

  const persMain = await page.evaluate(() => {
    const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
    const root = dlgs.length > 0 ? dlgs[dlgs.length - 1] : document.querySelector("main") || document.body;
    const fields = Array.from(root.querySelectorAll("textarea, input[type='text'], [contenteditable='true']"))
      .map((el) => ({
        ph: el.getAttribute("placeholder") || "",
        aria: el.getAttribute("aria-label") || "",
        val: ((el.value !== undefined ? el.value : el.innerText) || "").trim(),
      }))
      .filter((f) => f.val);
    return {
      url: location.href,
      rawText: (root.innerText || "").slice(0, 4000),
      fields,
    };
  });

  // Check if there is a Manage memories button
  let memories = [];
  let memoriesRaw = "";
  const allBtns = await page.$$("button, a");
  for (const b of allBtns) {
    const box = await b.boundingBox().catch(() => null);
    if (!box || box.width <= 4) continue;
    const txt = await b.evaluate((e) => (e.innerText || "").trim());
    if (/^manage$|^manage memories$|^quản lý$/i.test(txt)) {
      await b.click();
      await sleep(2000);
      const mRes = await page.evaluate(() => {
        const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
        const root = dlgs.length > 0 ? dlgs[dlgs.length - 1] : document.querySelector("main") || document.body;
        const rows = Array.from(root.querySelectorAll("tr, li, [role='row'], [data-testid*='memory']"))
          .map((r) => (r.innerText || "").trim())
          .filter((s) => s && s.length > 3 && !/^(memories|saved memories|delete all|search memories)$/i.test(s));
        return { raw: (root.innerText || "").slice(0, 5000), rows: Array.from(new Set(rows)) };
      });
      memories = mRes.rows;
      memoriesRaw = mRes.raw;
      await page.keyboard.press("Escape").catch(() => {});
      await sleep(400);
      break;
    }
  }
  await page.keyboard.press("Escape").catch(() => {});
  return { ...persMain, memories, memoriesRaw };
}

// Node-driven virtualized scroll so NO single evaluate ever runs > 1s!
async function extractConversationFast(page, conv) {
  const url = `https://chatgpt.com${conv.href}`;
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 40000 });
  await page.bringToFront();

  for (let w = 0; w < 25; w++) {
    const count = await page.evaluate(() => document.querySelectorAll("[data-turn-key]").length).catch(() => 0);
    if (count > 0) break;
    await sleep(450);
  }
  await sleep(700);

  // Step 1: Scroll up to top (max 30 quick iterations from Node)
  for (let up = 0; up < 30; up++) {
    const state = await page.evaluate(() => {
      const turn = document.querySelector("[data-turn-key]");
      let sc = turn ? turn.parentElement : document.querySelector("main");
      while (sc && sc !== document.body) {
        const st = getComputedStyle(sc);
        if ((st.overflowY === "auto" || st.overflowY === "scroll") && sc.scrollHeight > sc.clientHeight + 20) break;
        sc = sc.parentElement;
      }
      if (!sc || sc === document.body) {
        const cands = Array.from(document.querySelectorAll("main div")).filter((d) => d.scrollHeight > d.clientHeight + 40);
        cands.sort((a, b) => b.scrollHeight - a.scrollHeight);
        sc = cands[0] || null;
      }
      if (sc) sc.scrollTop = 0;
      const loading = /Loading older messages|Đang tải tin nhắn cũ/i.test(document.body?.innerText || "");
      return { top: sc ? sc.scrollTop : 0, loading };
    });
    await sleep(550);
    if (!state.loading && state.top === 0) {
      await sleep(450);
      const recheck = await page.evaluate(() =>
        /Loading older messages|Đang tải tin nhắn cũ/i.test(document.body?.innerText || "")
      );
      if (!recheck) break;
    }
  }

  // Step 2: Sweep from top -> bottom from Node, harvesting visible [data-turn-key] at each step
  const orderedKeys = [];
  const turnMap = new Map();

  const harvestNow = async () => {
    const batch = await page.evaluate(() => {
      return Array.from(document.querySelectorAll("[data-turn-key]")).map((n) => ({
        key: n.getAttribute("data-turn-key") || "",
        raw: (n.innerText || "").trim(),
      }));
    });
    for (const item of batch) {
      if (!item.key) continue;
      if (!turnMap.has(item.key)) orderedKeys.push(item.key);
      const prev = turnMap.get(item.key);
      if (!prev || item.raw.length >= prev.raw.length) {
        let role = "turn";
        let text = item.raw;
        if (/^You said:\s*/i.test(item.raw)) {
          role = "user";
          text = item.raw.replace(/^You said:\s*/i, "").trim();
        } else if (/^ChatGPT said:\s*/i.test(item.raw)) {
          role = "assistant";
          text = item.raw.replace(/^ChatGPT said:\s*/i, "").trim();
        } else if (/^Bạn đã nói:\s*/i.test(item.raw)) {
          role = "user";
          text = item.raw.replace(/^Bạn đã nói:\s*/i, "").trim();
        }
        turnMap.set(item.key, { key: item.key, role, raw: item.raw, text });
      }
    }
  };

  await harvestNow();

  for (let stepIdx = 0; stepIdx < 160; stepIdx++) {
    const pos = await page.evaluate(() => {
      const turn = document.querySelector("[data-turn-key]");
      let sc = turn ? turn.parentElement : document.querySelector("main");
      while (sc && sc !== document.body) {
        const st = getComputedStyle(sc);
        if ((st.overflowY === "auto" || st.overflowY === "scroll") && sc.scrollHeight > sc.clientHeight + 20) break;
        sc = sc.parentElement;
      }
      if (!sc || sc === document.body) {
        const cands = Array.from(document.querySelectorAll("main div")).filter((d) => d.scrollHeight > d.clientHeight + 40);
        cands.sort((a, b) => b.scrollHeight - a.scrollHeight);
        sc = cands[0] || null;
      }
      if (!sc) return { done: true };
      const prev = sc.scrollTop;
      const step = Math.max(350, Math.floor(sc.clientHeight * 0.68));
      sc.scrollTop = Math.min(sc.scrollHeight, sc.scrollTop + step);
      const atEnd = sc.scrollTop >= sc.scrollHeight - sc.clientHeight - 6 || sc.scrollTop === prev;
      return { done: atEnd, top: sc.scrollTop, h: sc.scrollHeight };
    });
    await sleep(320);
    await harvestNow();
    if (pos.done) break;
  }

  const pageTitle = await page.evaluate(() => document.title.replace(/\s*-\s*ChatGPT.*$/i, "").trim());
  const turns = orderedKeys.map((k, idx) => {
    const t = turnMap.get(k);
    return { index: idx + 1, turnKey: t.key, role: t.role, text: t.text };
  });

  return {
    ...conv,
    pageTitle,
    turnCount: turns.length,
    totalChars: turns.reduce((s, t) => s + t.text.length, 0),
    turns,
  };
}

async function deleteChatById(page, chat) {
  if (chat.title.endsWith("_skip")) return false;
  await page.goto(`https://chatgpt.com/c/${chat.id}`, { waitUntil: "domcontentloaded", timeout: 25000 }).catch(() => {});
  await sleep(1600);
  // Inject our local chatgpt-page-driver.js and invoke deleteCurrentConversation()
  await page.addScriptTag({ path: path.resolve("chatgpt-page-driver.js") }).catch(() => {});
  const res = await page.evaluate(() => window.__chatgptUi?.deleteCurrentConversation?.()).catch(() => null);
  if (res?.deleted) return true;

  // Pure UI fallback: click header options (...) -> Delete -> Delete
  const optBtns = await page.$$(
    'button[data-testid="conversation-options-button"], button[aria-label="Conversation actions"], button[aria-label="Open conversation options"]'
  );
  for (const b of optBtns) {
    const box = await b.boundingBox().catch(() => null);
    if (box && box.width > 4) {
      await b.click();
      await sleep(700);
      const items = await page.$$('[role="menuitem"]');
      for (const it of items) {
        const txt = await it.evaluate((e) => (e.innerText || "").trim());
        if (/^delete$|^xóa$/i.test(txt)) {
          await it.click();
          await sleep(800);
          const confBtns = await page.$$('[role="dialog"] button');
          for (const cb of confBtns) {
            const ctxt = await cb.evaluate((e) => (e.innerText || "").trim());
            if (/^delete$|^xóa$/i.test(ctxt)) {
              await cb.click();
              await sleep(900);
              return true;
            }
          }
        }
      }
    }
  }
  return false;
}

async function main() {
  const browser = await puppeteer.connect({
    browserURL: "http://127.0.0.1:9333",
    defaultViewport: null,
    protocolTimeout: 600000,
  });

  const page = await browser.newPage();
  try {
    await page.bringToFront();

    console.log("[1/4] Reading Personalization & Saved Memories...");
    const personalization = await extractPersonalization(page);
    console.log(
      `  Personalization fields=${personalization.fields.length}, memories=${personalization.memories.length}`
    );

    console.log("[2/4] Extracting 5 Work & Project Conversations...");
    const workConversations = [];
    for (let i = 0; i < WORK_CHATS.length; i++) {
      const wc = WORK_CHATS[i];
      const full = await extractConversationFast(page, wc);
      console.log(
        `  [${i + 1}/${WORK_CHATS.length}] [${full.projectName}] ${full.title} -> ${full.turnCount} turns (${full.totalChars} chars)`
      );
      workConversations.push(full);
      // Incremental save after every chat!
      fs.writeFileSync(
        path.join(OUT_DIR, "00_work_export.json"),
        JSON.stringify({ exportedAt: new Date().toISOString(), personalization, workConversations }, null, 2),
        "utf8"
      );
    }

    console.log("[3/4] Deleting trivial Q&A chats on huusei1234...");
    let deletedCount = 0;
    for (const tc of TRIVIAL_CHATS_TO_DELETE) {
      if (tc.title.endsWith("_skip")) continue;
      const ok = await deleteChatById(page, tc);
      console.log(`  Delete [${tc.title}] (${tc.id}): ${ok ? "DELETED" : "SKIPPED/NOT_FOUND"}`);
      if (ok) deletedCount++;
    }
    console.log(`  Total trivial chats deleted on huusei1234: ${deletedCount}`);

    // Clean up extra ChatGPT tabs so only 1 clean ChatGPT tab remains open for user to switch to Plus!
    console.log("[4/4] Tidying duplicate ChatGPT tabs...");
    const allPages = await browser.pages();
    const chatPages = allPages.filter((p) => p !== page && /chatgpt\.com/i.test(p.url()));
    // Keep 1 ChatGPT tab navigated to https://chatgpt.com/ and close duplicates
    if (chatPages.length > 0) {
      await chatPages[0].goto("https://chatgpt.com/", { waitUntil: "domcontentloaded" }).catch(() => {});
      for (let k = 1; k < chatPages.length; k++) {
        await chatPages[k].close().catch(() => {});
      }
      await chatPages[0].bringToFront().catch(() => {});
    }
  } finally {
    await page.close().catch(() => {});
    browser.disconnect();
  }
}

main().catch((err) => {
  console.error("FATAL:", err);
  process.exit(1);
});
