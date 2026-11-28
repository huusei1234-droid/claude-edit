import puppeteer from "puppeteer-core";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const browser = await puppeteer.connect({ browserURL: "http://127.0.0.1:9333", defaultViewport: null });
const page = await browser.newPage();
try {
  await page.bringToFront();
  await page.goto("https://chatgpt.com/g/g-p-6ac5c68cc60c8191bab63b740e910809/project", { waitUntil: "domcontentloaded" });
  await sleep(2500);

  // 1. Click Project actions -> Project settings
  const paBtn = await page.$('button[aria-label="Project actions"]');
  if (paBtn) {
    await paBtn.click();
    await sleep(700);
    const items = await page.$$('[role="menuitem"]');
    for (const it of items) {
      const txt = await it.evaluate((e) => (e.innerText || "").trim());
      if (/project settings|cài đặt dự án/i.test(txt)) {
        await it.click();
        break;
      }
    }
    await sleep(1200);
    const dlgInfo = await page.evaluate(() => {
      const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
      return dlgs.map((d) => ({
        text: (d.innerText || "").trim(),
        areas: Array.from(d.querySelectorAll("textarea, input, [contenteditable='true']")).map((a) => ({
          tag: a.tagName,
          ph: a.getAttribute("placeholder") || "",
          val: (a.value !== undefined ? a.value : a.innerText) || "",
        })),
      }));
    });
    console.log("K4_PROJECT_SETTINGS:", JSON.stringify(dlgInfo, null, 2));
    await page.keyboard.press("Escape");
    await sleep(500);
  }

  // Also check HTPM Project settings!
  await page.goto("https://chatgpt.com/g/g-p-6afbde0b943481919c6ec31a3b4f8642/project", { waitUntil: "domcontentloaded" });
  await sleep(2200);
  const paBtn2 = await page.$('button[aria-label="Project actions"]');
  if (paBtn2) {
    await paBtn2.click();
    await sleep(700);
    const items = await page.$$('[role="menuitem"]');
    for (const it of items) {
      const txt = await it.evaluate((e) => (e.innerText || "").trim());
      if (/project settings|cài đặt dự án/i.test(txt)) {
        await it.click();
        break;
      }
    }
    await sleep(1200);
    const dlgInfo2 = await page.evaluate(() => {
      const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
      return dlgs.map((d) => ({
        text: (d.innerText || "").trim(),
        areas: Array.from(d.querySelectorAll("textarea, input, [contenteditable='true']")).map((a) => ({
          tag: a.tagName,
          ph: a.getAttribute("placeholder") || "",
          val: (a.value !== undefined ? a.value : a.innerText) || "",
        })),
      }));
    });
    console.log("HTPM_PROJECT_SETTINGS:", JSON.stringify(dlgInfo2, null, 2));
    await page.keyboard.press("Escape");
    await sleep(500);
  }

  // 2. Open sidebar -> click Open profile menu -> Personalization
  const showSb = await page.$('button[aria-label="Show sidebar"]');
  if (showSb) {
    const box = await showSb.boundingBox();
    if (box) {
      await showSb.click();
      await sleep(800);
    }
  }
  const profBtns = await page.$$('button[aria-label="Open profile menu"], [data-testid="accounts-profile-button"]');
  for (const pb of profBtns) {
    const box = await pb.boundingBox();
    if (box && box.width > 5) {
      await pb.click();
      await sleep(800);
      break;
    }
  }
  const profMenu = await page.evaluate(() =>
    Array.from(document.querySelectorAll('[role="menu"], [role="menuitem"]')).map((e) => (e.innerText || "").trim())
  );
  console.log("PROF_MENU:", JSON.stringify(profMenu));

  // Click Personalization or Settings
  const mItems = await page.$$('[role="menuitem"]');
  for (const mi of mItems) {
    const t = await mi.evaluate((e) => (e.innerText || "").trim());
    if (/personalization|customize|settings|cá nhân hóa|cài đặt/i.test(t)) {
      await mi.click();
      await sleep(1300);
      break;
    }
  }
  const settingsDlg = await page.evaluate(() => {
    const dlgs = Array.from(document.querySelectorAll('[role="dialog"]'));
    return dlgs.map((d) => ({
      text: (d.innerText || "").slice(0, 1500),
      btns: Array.from(d.querySelectorAll("button, [role='tab']")).map((b) => (b.innerText || "").trim()).filter(Boolean),
      areas: Array.from(d.querySelectorAll("textarea, input, [contenteditable='true']")).map((a) => ({
        ph: a.getAttribute("placeholder") || "",
        val: (a.value !== undefined ? a.value : a.innerText) || "",
      })),
    }));
  });
  console.log("SETTINGS_DLG:", JSON.stringify(settingsDlg, null, 2));
} finally {
  await page.close().catch(() => {});
  browser.disconnect();
}
