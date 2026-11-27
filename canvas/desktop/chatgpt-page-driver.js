/**
 * UI page driver cho ChatGPT Web (https://chatgpt.com/).
 * Nạp lại từ đĩa mỗi lần chạy để dễ bảo trì khi giao diện ChatGPT thay đổi mà không cần khởi động lại app.
 * TUÂN THỦ NGHIÊM NGẶT: Không bao giờ tự động bấm/vượt CAPTCHA hay kiểm tra anti-bot; nếu gặp trang đăng nhập
 * hoặc xác minh người dùng thì báo về main process để hiện cửa sổ cho người dùng tự thao tác.
 */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const txt = (e) => (e?.innerText || e?.textContent || "").trim();
  const visible = (e) => {
    if (!e) return false;
    const rc = e.getBoundingClientRect();
    return rc.width > 2 && rc.height > 2;
  };

  // Bắt <input type="file"> ẩn nếu cần mà không mở hộp thoại hệ thống
  const cap = (window.__chatgptFileCap = window.__chatgptFileCap || { on: false, input: null });
  if (!window.__chatgptClickPatched) {
    const orig = HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click = function () {
      if (this.type === "file" && window.__chatgptFileCap.on) {
        window.__chatgptFileCap.input = this;
        return;
      }
      return orig.apply(this, arguments);
    };
    window.__chatgptClickPatched = true;
  }

  function findEditor() {
    return (
      $("#prompt-textarea") ||
      $('div.ProseMirror[contenteditable="true"]') ||
      $('textarea[name="prompt-textarea"]') ||
      $('[data-testid="composer-text-input"]')
    );
  }

  function findSendButton() {
    const candidates = [
      $('[data-testid="send-button"]'),
      $('button[aria-label*="Send prompt" i]'),
      $('button[aria-label*="Send message" i]'),
      $('button[aria-label*="Gửi" i]'),
      ...$$("form button[type='submit']"),
    ].filter(Boolean);
    return candidates.find((b) => visible(b) && !b.disabled && b.getAttribute("aria-disabled") !== "true") || null;
  }

  function findStopButton() {
    const candidates = [
      $('[data-testid="stop-button"]'),
      $('button[aria-label*="Stop streaming" i]'),
      $('button[aria-label*="Stop generating" i]'),
      $('button[aria-label*="Dừng" i]'),
    ].filter(Boolean);
    return candidates.find((b) => visible(b)) || null;
  }

  function inspectState() {
    const url = location.href;
    const title = document.title || "";
    const bodyText = (document.body?.innerText || "").slice(0, 1500);

    // Phát hiện trang xác minh / cổng bảo mật -> dừng ngay để người dùng tự xử lý
    const hasChallenge =
      /Just a moment|Verify you are human|Xác minh bạn là con người/i.test(title) ||
      !!$('iframe[src*="challenges.cloudflare.com"], #challenge-running, #cf-challenge-running');
    if (hasChallenge) {
      return { ready: false, needManualAuth: true, reason: "challenge" };
    }

    // Phát hiện chưa đăng nhập (hoặc đang ở chế độ khách không tạo ảnh được)
    if (/auth\.openai\.com|\/auth\/login/i.test(url)) {
      return { ready: false, needManualAuth: true, reason: "auth_redirect" };
    }
    const loginBtns = $$("button, a").filter(
      (el) => visible(el) && /^(Log in|Sign up|Đăng nhập|Đăng ký)$/i.test(txt(el))
    );
    if (loginBtns.length > 0) {
      return { ready: false, needManualAuth: true, reason: "logged_out" };
    }

    // Tự động chuyển vào Dự án "HTPM" NẾU không tắt cờ __chatgptSkipAutoHtpm và tài khoản hiện tại có dự án HTPM
    if (!window.__chatgptSkipAutoHtpm) {
      const projLink =
        $('[data-app-action-sidebar-project-label="HTPM" i]') ||
        $$("[data-app-action-sidebar-project-id]").find(
          (el) => (el.getAttribute("data-app-action-sidebar-project-label") || "").trim().toUpperCase() === "HTPM"
        ) ||
        $$('a[href*="/g/g-p-"]').find((a) => txt(a).toUpperCase() === "HTPM");
      const detectedPid =
        projLink?.getAttribute("data-app-action-sidebar-project-id") ||
        (projLink?.getAttribute("href")?.match(/\/g\/(g-p-[a-z0-9-]+)/i) || [])[1] ||
        "";
      if (detectedPid && !url.includes(`/g/${detectedPid}`) && !/\/c\/[0-9a-f-]{36}/i.test(url)) {
        if (!window.__chatgptHtpmClickedAt) {
          window.__chatgptHtpmClickedAt = Date.now();
          location.assign(`https://chatgpt.com/g/${detectedPid}/project`);
          return { ready: false, needManualAuth: false, enteringProject: "HTPM" };
        }
        if (Date.now() - window.__chatgptHtpmClickedAt < 2500) {
          return { ready: false, needManualAuth: false, waitingProject: "HTPM" };
        }
      }
    }
    // Nếu đang kẹt ở URL /g/g-p-.../project của tài khoản cũ (Loading project / không có editor sau 3.5s) -> quay ngay về https://chatgpt.com/
    if (/\/g\/g-p-[a-z0-9-]+\/project/i.test(url) && !findEditor()) {
      window.__chatgptDeadProjSince = window.__chatgptDeadProjSince || Date.now();
      if (Date.now() - window.__chatgptDeadProjSince > 3500 || /No projects/i.test(bodyText)) {
        location.assign("https://chatgpt.com/");
        return { ready: false, needManualAuth: false, fallbackRootHome: true };
      }
    }

    // Hỗ trợ đồng thời cả DOM cũ ([data-message-author-role]) và DOM ảo hóa mới ([data-turn-key]) của ChatGPT Plus
    const ed = findEditor();
    const legacyTurns = $$('[data-testid^="conversation-turn-"], [data-message-author-role]');
    const vTurns = $$("[data-turn-key]");
    const turnKeys = vTurns.map((n) => n.getAttribute("data-turn-key") || "").filter(Boolean);
    const assistantVTurns = vTurns.filter((n) => /^ChatGPT said:/i.test(txt(n)));
    const legacyAssistantCount = $$('[data-message-author-role="assistant"]').length;
    const convId = (location.pathname.match(/\/c\/([0-9a-f-]{36})/i) || [])[1] || "";
    return {
      ready: !!(ed && visible(ed)),
      needManualAuth: false,
      turnCount: Math.max(legacyAssistantCount, assistantVTurns.length),
      totalTurns: Math.max(legacyTurns.length, vTurns.length),
      turnKeys,
      convId,
      url,
      preview: bodyText.slice(0, 120),
    };
  }

  function getComposerCenter() {
    const ed = findEditor();
    if (!ed) return null;
    ed.scrollIntoView({ block: "center" });
    const r = ed.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }

  function getSendCenter() {
    // Chụp danh sách ảnh đang có trên trang ngay trước khi bấm Gửi để không bao giờ lấy nhầm ảnh cũ
    window.__chatgptBaseline = collectGeneratedImages(false).map((x) => x.key);
    const b = findSendButton();
    if (!b) return null;
    b.scrollIntoView({ block: "center" });
    const r = b.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }

  function uploadsSettled() {
    // Kiểm tra không còn vòng xoay tiến trình upload trong khung nhập
    const form = findEditor()?.closest("form") || document.body;
    const busy = $$('[role="progressbar"], [aria-busy="true"], [data-testid*="loading"]', form).some(visible);
    return !busy;
  }

  function normImgKey(u) {
    if (!u) return "";
    if (u.startsWith("blob:") || u.startsWith("data:")) return u;
    try {
      const parsed = new URL(u, location.href);
      // Giữ id file của estuary / oaiusercontent, bỏ tham số hết hạn nếu cần
      const idParam = parsed.searchParams.get("id");
      return idParam ? `${parsed.origin}${parsed.pathname}?id=${idParam}` : `${parsed.origin}${parsed.pathname}`;
    } catch {
      return String(u).split("?")[0];
    }
  }

  function collectGeneratedImages(excludeBaseline = true) {
    const root = $("main") || document.body;
    const composerForm = findEditor()?.closest("form");
    const baseSet = new Set(excludeBaseline ? window.__chatgptBaseline || [] : []);
    const seen = new Set();
    const out = [];

    for (const img of $$("img", root)) {
      // Bỏ ảnh nằm trong ô soạn thảo (thumbnail đang đính kèm) hoặc tin nhắn của user
      if (composerForm && composerForm.contains(img)) continue;
      if (img.closest('[data-message-author-role="user"]')) continue;

      const src = img.currentSrc || img.src || "";
      if (!src || /^data:image\/svg/i.test(src) || /auth0\.com\/avatars|gravatar\.com/i.test(src)) continue;

      const nw = img.naturalWidth || 0;
      const nh = img.naturalHeight || 0;
      const rw = img.getBoundingClientRect().width || 0;
      const alt = (img.alt || "").trim();

      // Ảnh kết quả tạo bởi ChatGPT có độ phân giải lớn (>= 384px, thường 1024-1536px) hoặc alt "Ảnh được tạo" / "Generated image"
      const isGeneratedAlt = /Ảnh được tạo|Generated image/i.test(alt);
      if (!img.complete || nw < 384 || nh < 384 || (rw < 100 && !isGeneratedAlt)) continue;

      // Bỏ ảnh tham chiếu nhỏ do user gửi trong bong bóng chat (nếu không có role="user": ảnh user thường có alt="Uploaded image" / "Đã tải lên")
      if (/Uploaded|Đã tải lên/i.test(alt)) continue;

      // Bỏ lớp ảnh nền blur trang trí trùng URL của ChatGPT
      const st = getComputedStyle(img);
      if (st.filter && st.filter.includes("blur")) continue;

      const key = normImgKey(src);
      if (baseSet.has(key) || seen.has(key)) continue;
      seen.add(key);
      out.push({ url: src, key, width: nw, height: nh, alt });
    }
    return out;
  }

  function getLatestAssistantScope(prevAssistantCount = 0, prevTurnKeys = []) {
    const legacyAssistant = $$('[data-message-author-role="assistant"]');
    if (legacyAssistant.length > 0) {
      const slice = legacyAssistant.slice(Math.max(0, prevAssistantCount));
      return { newCount: slice.length, node: slice[slice.length - 1] || null };
    }
    const prevSet = new Set(prevTurnKeys || []);
    const vTurns = $$("[data-turn-key]");
    const newVTurns = vTurns.filter((n) => {
      const k = n.getAttribute("data-turn-key") || "";
      return k && !prevSet.has(k);
    });
    const assistantNew = newVTurns.filter((n) => /^ChatGPT said:/i.test(txt(n)));
    const pool = assistantNew.length > 0 ? assistantNew : newVTurns.slice(1);
    return { newCount: pool.length, node: pool[pool.length - 1] || null };
  }

  function poll({ prevAssistantCount = 0, prevTurnKeys = [], t0 = 0 }) {
    const elapsed = Date.now() - t0;
    const stopBtn = findStopButton();
    const { newCount, node: latestScope } = getLatestAssistantScope(prevAssistantCount, prevTurnKeys);
    const rawScopeText = latestScope ? txt(latestScope).replace(/^ChatGPT said:\s*/i, "").trim() : "";
    const mainText = txt($("main") || document.body);

    // Nhận diện đầy đủ trạng thái đang Suy luận (Thinking) hoặc đang dựng khung ảnh (shimmer/progressbar) của ChatGPT mới
    const hasRenderSkeleton = Boolean(
      latestScope &&
      $$('[role="progressbar"], [aria-busy="true"], [class*="shimmer"], [class*="skeleton"]', latestScope).some(visible)
    );
    const creatingIndicator =
      !!stopBtn ||
      hasRenderSkeleton ||
      (elapsed < 150000 &&
        /Creating image|Đang tạo hình ảnh|Getting started|Đang bắt đầu|Đang suy luận|Thinking\.\.\./i.test(
          rawScopeText || mainText
        ));
    const isStreaming = !!stopBtn || creatingIndicator;

    const images = collectGeneratedImages();

    // Chỉ nhận DONE khi ChatGPT đã dừng stream hoàn toàn (hết nút Stop & hết khung chờ) VÀ có ít nhất 1 ảnh hoàn chỉnh!
    if (!isStreaming && images.length > 0 && elapsed > 3000) {
      return { state: "done", images, elapsed };
    }

    // Loại bỏ dòng tiêu đề 'Đã suy luận trong X giây / Thought for Xs' để không bao giờ nhầm trạng thái Suy luận thành 'trả lời bằng chữ'!
    const cleanedReplyText = rawScopeText
      .replace(/^(Đã suy luận|Suy luận|Thought)\s*(trong|for)?\s*\d+\s*(giây|phút|s|sec|seconds|m)?\s*/gi, "")
      .trim();

    const isHardQuotaOrLimit =
      /not enough usage available|out of images|more will be available after|reached your.*limit|đạt đến giới hạn|đạt giới hạn tạo|try again later|thử lại sau|too many requests/i.test(
        cleanedReplyText || rawScopeText
      );
    if (newCount > 0 && images.length === 0 && isHardQuotaOrLimit && elapsed > 3000) {
      return {
        state: "failed",
        hardLimit: true,
        error: "ChatGPT chạm giới hạn lượt tạo ảnh: " + (cleanedReplyText || rawScopeText).replace(/\s+/g, " ").slice(0, 260),
        images: [],
      };
    }

    // Chờ tối thiểu 45 giây sau khi dừng hẳn stream mà vẫn chỉ có văn bản thực sự (dài > 25 ký tự sau khi bỏ dòng 'Đã suy luận') mới báo lỗi
    if (!isStreaming && newCount > 0 && images.length === 0 && elapsed > 45000 && cleanedReplyText.length > 25) {
      return {
        state: "failed",
        error: "ChatGPT trả lời bằng chữ thay vì tạo ảnh: " + cleanedReplyText.replace(/\s+/g, " ").slice(0, 260),
        images: [],
      };
    }

    return { state: "running", imagesCount: images.length, isStreaming, elapsed };
  }

  async function activateComposerTool(mode = "auto") {
    const waitMs = (ms) => new Promise((r) => setTimeout(r, ms));
    const want = String(mode || "auto").toLowerCase();
    if (!want || want === "auto" || want === "default") return { activated: false, mode: "default" };

    const form = findEditor()?.closest("form") || document.body;
    const matchMap = {
      thinking: /^(Think|Reason|Suy luận)$/i,
      "deep-research": /Deep research|Nghiên cứu sâu/i,
      search: /^(Search|Web search|Tìm kiếm)$/i,
      canvas: /^Canvas$/i,
    };
    const rx = matchMap[want];
    if (!rx) return { activated: false, mode: want };

    // 1. Thử tìm trực tiếp nút công cụ trên thanh composer
    const directBtn = $$("button, [role='button']", form).find(
      (b) => visible(b) && (rx.test(txt(b)) || rx.test(b.getAttribute("aria-label") || ""))
    );
    if (directBtn) {
      const pressed =
        directBtn.getAttribute("aria-pressed") === "true" ||
        directBtn.getAttribute("data-state") === "on";
      if (!pressed) {
        directBtn.click();
        await waitMs(350);
      }
      return { activated: true, via: "direct", mode: want };
    }

    // 2. Mở menu '+' / Tools trên composer để chọn Deep research / Canvas / Web search
    const plusBtn =
      $('[data-testid="composer-plus-btn"]', form) ||
      $$("button", form).find((b) =>
        /add files and more|tools|attach|công cụ|thêm tệp/i.test(
          (b.getAttribute("aria-label") || "") + " " + txt(b)
        )
      );
    if (plusBtn && visible(plusBtn)) {
      plusBtn.click();
      await waitMs(550);
      const item = $$('[role="menuitem"], [role="menuitemcheckbox"], [role="option"]').find(
        (el) => visible(el) && rx.test(txt(el))
      );
      if (item) {
        item.click();
        await waitMs(450);
        return { activated: true, via: "menu", mode: want };
      }
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    }
    return { activated: false, mode: want };
  }

  function pollText({ prevAssistantCount = 0, prevTurnKeys = [], t0 = 0, mode = "thinking" }) {
    const elapsed = Date.now() - t0;
    const stopBtn = findStopButton();
    const { newCount, node: latestScope } = getLatestAssistantScope(prevAssistantCount, prevTurnKeys);

    // Nếu Deep Research hỏi xác nhận "Start research" / "Bắt đầu nghiên cứu", tự bấm để chạy trọn luồng
    if (mode === "deep-research" && latestScope) {
      const startResBtn = $$("button", latestScope).find(
        (b) => visible(b) && /^(Start|Start research|Bắt đầu|Bắt đầu nghiên cứu)$/i.test(txt(b))
      );
      if (startResBtn && !window.__chatgptClickedStartResearch) {
        window.__chatgptClickedStartResearch = true;
        startResBtn.click();
      }
    }

    const rawText = latestScope ? txt(latestScope) : "";
    const cleanText = rawText
      .replace(/^ChatGPT said:\s*/i, "")
      .replace(/^(Đã suy luận|Suy luận|Thought|Thinking)\s*(trong|for)?\s*\d*\s*(giây|phút|s|sec|seconds|m)?\s*\n*/i, "")
      .trim();

    const turnState = latestScope?.getAttribute?.("data-talvt-turn-state") || "";
    const hasBusy = Boolean(
      latestScope &&
      $$('[role="progressbar"], [aria-busy="true"], [data-loading-indicator]', latestScope).some(visible)
    );
    const isResearching =
      mode === "deep-research" &&
      /Researching|Đang nghiên cứu|Searching|Reading sources/i.test(rawText) &&
      !!stopBtn;
    const isStreaming = !!stopBtn || hasBusy || isResearching || (turnState && turnState !== "complete");

    // Theo dõi độ ổn định của văn bản (tránh cắt sớm khi vừa dứt câu)
    if (cleanText !== (window.__chatgptLastPollTxt || "")) {
      window.__chatgptLastPollTxt = cleanText;
      window.__chatgptLastPollChangeAt = Date.now();
    }
    const stableMs = Date.now() - (window.__chatgptLastPollChangeAt || Date.now());
    const images = collectGeneratedImages();

    if (!isStreaming && newCount > 0 && cleanText.length > 0 && stableMs >= 1400 && elapsed > 1800) {
      return {
        state: "done",
        text: cleanText,
        images,
        convUrl: location.href,
        elapsed,
      };
    }

    return {
      state: "running",
      partialText: cleanText,
      isStreaming,
      newCount,
      elapsed,
    };
  }

  async function fetchImageAsBase64(url) {
    const res = await fetch(url, { credentials: "include" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const blob = await res.blob();
    const mime = blob.type && blob.type.startsWith("image/") ? blob.type : "image/png";
    const b64 = await new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => {
        const s = String(fr.result || "");
        const idx = s.indexOf(",");
        resolve(idx >= 0 ? s.slice(idx + 1) : s);
      };
      fr.onerror = reject;
      fr.readAsDataURL(blob);
    });
    return { base64: b64, mime };
  }

  async function deleteCurrentConversation() {
    const waitMs = (ms) => new Promise((r) => setTimeout(r, ms));
    let convId = (location.pathname.match(/\/c\/([0-9a-f-]{36})/i) || [])[1] || "";
    for (let w = 0; w < 6 && !convId; w++) {
      await waitMs(400);
      convId = (location.pathname.match(/\/c\/([0-9a-f-]{36})/i) || [])[1] || "";
    }

    // Tầng 1: Xóa sạch cuộc trò chuyện ngay trong ngữ cảnh trang (nhanh ~200ms, kèm oai-device-id chuẩn để 100% thành công)
    try {
      const sessRes = await fetch("/api/auth/session", { credentials: "include" });
      const sess = sessRes.ok ? await sessRes.json().catch(() => ({})) : {};
      const tok = typeof sess?.accessToken === "string" ? sess.accessToken : "";
      const rawDid = localStorage.getItem("oai-did") || "";
      const did = rawDid.replace(/^"|"$/g, "");
      const headers = { "Content-Type": "application/json" };
      if (tok) headers.Authorization = "Bearer " + tok;
      if (did) headers["oai-device-id"] = did;

      // Nếu URL vẫn chưa kịp gắn /c/<id>, dò 3 cuộc trò chuyện mới nhất vừa tạo trong 5 phút qua có chữ ký tạo ảnh tự động
      if (!convId && tok) {
        const listRes = await fetch("/backend-api/conversations?offset=0&limit=3&order=updated", { credentials: "include", headers });
        if (listRes.ok) {
          const lj = await listRes.json().catch(() => ({}));
          for (const it of lj.items || []) {
            if (/^Generate\b/i.test(it.title || "")) {
              convId = it.id;
              break;
            }
          }
        }
      }

      if (convId) {
        for (let attempt = 0; attempt < 2; attempt++) {
          const patchRes = await fetch(`/backend-api/conversation/${convId}`, {
            method: "PATCH",
            credentials: "include",
            headers,
            body: JSON.stringify({ is_visible: false }),
          });
          if (patchRes.ok) {
            return { deleted: true, method: "api", convId };
          }
          await waitMs(400);
        }
      }
    } catch {}

    if (!convId) {
      return { deleted: false, skipped: true, reason: "no_conv_id" };
    }

    // Tầng 2 (Dự phòng giao diện): Bấm nút menu "..." góc phải cuộc trò chuyện -> Xóa / Delete -> Xác nhận
    const optBtn =
      $('[data-testid="conversation-options-button"]') ||
      $('button[aria-label*="conversation options" i]') ||
      $('button[aria-label*="Tùy chọn cuộc trò chuyện" i]');
    if (optBtn && visible(optBtn)) {
      optBtn.click();
      await waitMs(450);
      const delItem =
        $('[data-testid="delete-chat-menu-item"]') ||
        $$('[role="menuitem"]').find((el) => /^(Delete|Xóa|Xoá)(\s+chat)?$/i.test(txt(el)));
      if (delItem) {
        delItem.click();
        await waitMs(450);
        const confirmBtn =
          $('[data-testid="delete-conversation-confirm-button"]') ||
          $$('[role="dialog"] button').find((b) => /^(Delete|Xóa|Xoá)$/i.test(txt(b)));
        if (confirmBtn) {
          confirmBtn.click();
          await waitMs(500);
          return { deleted: true, method: "ui", convId };
        }
      }
    }

    return { deleted: false, reason: "not_deleted", convId };
  }

  window.__chatgptUi = {
    version: 3,
    inspectState,
    getComposerCenter,
    getSendCenter,
    uploadsSettled,
    poll,
    pollText,
    activateComposerTool,
    fetchImageAsBase64,
    deleteCurrentConversation,
  };
})();
