/**
 * DỌN GỌN AN TOÀN CÁC TAB DƯ THỪA TRÊN BRAVE (:9333) — 0% ẢNH HƯỞNG TIẾN ĐỘ ĐANG CHẠY!
 * - Kiểm tra trực tiếp DOM từng tab: nếu tab đang tạo ảnh/video (có nút Stop / % progress / Queued / mat-progress-bar) -> BẢO VỆ 100%, TUYỆT ĐỐI KHÔNG ĐÓNG!
 * - Nếu người dùng đang mở bất kỳ trang web cá nhân nào khác (Zalo, Facebook, Drive, YouTube, Docs...) -> GIỮ NGUYÊN 100%!
 * - Với các tab ChatGPT, Google Flow và Thẻ mới (chrome://newtab) đang rảnh rỗi (IDLE):
 *   chỉ giữ lại đúng 1 Tab Google Flow dự án chính + 1 Tab ChatGPT dự án HTPM, đóng toàn bộ các tab trùng lặp!
 */
const puppeteer = require("d:/AI/full studio/canvas/desktop/node_modules/puppeteer-core");

(async () => {
  const infoRes = await fetch("http://127.0.0.1:9333/json/version", { signal: AbortSignal.timeout(3000) });
  if (!infoRes.ok) {
    console.log("Brave :9333 đang không mở.");
    return;
  }
  const info = await infoRes.json();
  const b = await puppeteer.connect({ browserWSEndpoint: info.webSocketDebuggerUrl, defaultViewport: null });
  const pages = await b.pages();

  const idleFlow = [];
  const idleGpt = [];
  const blankTabs = [];
  let busyCount = 0;
  let userPersonalCount = 0;

  for (const p of pages) {
    if (!p || p.isClosed()) continue;
    const u = p.url() || "";
    if (/^(chrome|brave):\/\/newtab\/?$|^about:blank$/i.test(u)) {
      blankTabs.push(p);
      continue;
    }
    if (/^https:\/\/flow\.google\.com\b/i.test(u)) {
      const busy = await p.evaluate(() => {
        const txt = document.body ? document.body.innerText : "";
        return /\b(\d{1,2}%|Generating|Đang tạo|Queued|Đang xếp hàng)\b/i.test(txt) ||
          !!document.querySelector('mat-progress-bar, mat-spinner, [role="progressbar"]');
      }).catch(() => false);
      if (busy) busyCount++;
      else idleFlow.push(p);
      continue;
    }
    if (/^https:\/\/chatgpt\.com\b/i.test(u)) {
      const busy = await p.evaluate(() =>
        !!document.querySelector('[data-testid="stop-button"], button[aria-label*="Stop"], button[aria-label*="Dừng"]')
      ).catch(() => false);
      if (busy) busyCount++;
      else idleGpt.push(p);
      continue;
    }
    userPersonalCount++;
  }

  const keepFlow = idleFlow.find((p) => /\/project\/[0-9a-f-]{36}/i.test(p.url() || "")) || idleFlow[0] || null;
  const keepGpt = idleGpt.find((p) => /\/g\/g-p-[^/]+\/project/i.test(p.url() || "")) || idleGpt[0] || null;

  let closed = 0;
  for (const p of idleFlow) {
    if (p !== keepFlow) {
      await p.close().catch(() => {});
      closed++;
    }
  }
  for (const p of idleGpt) {
    if (p !== keepGpt) {
      await p.close().catch(() => {});
      closed++;
    }
  }
  for (const p of blankTabs) {
    await p.close().catch(() => {});
    closed++;
  }

  const remain = (await b.pages()).map((p) => p.url());
  console.log(`Đã đóng gọn ${closed} tab thừa nhàn rỗi (bảo vệ ${busyCount} tab đang chạy, ${userPersonalCount} tab cá nhân).`);
  console.log(`Còn lại ${remain.length} tab gọn sạch:`, remain);
  await b.disconnect();
})();
