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

    // Tự động chuyển vào Dự án "HTPM" trên thanh bên ChatGPT để gom gọn toàn bộ cuộc trò chuyện tạo ảnh vào dự án HTPM
    const DEFAULT_HTPM_PID = "g-p-6afbde0b943481919c6ec31a3b4f8642";
    const inHtpmProject = url.includes(`/g/${DEFAULT_HTPM_PID}`) || (/\/g\/g-p-/i.test(url) && /htpm/i.test(url));
    if (!inHtpmProject && !/\/g\/g-p-/i.test(url)) {
      const projDiv =
        $('[data-app-action-sidebar-project-label="HTPM" i]') ||
        $$("[data-app-action-sidebar-project-id]").find(
          (el) => (el.getAttribute("data-app-action-sidebar-project-label") || "").trim().toUpperCase() === "HTPM"
        );
      const pid = projDiv?.getAttribute("data-app-action-sidebar-project-id") || DEFAULT_HTPM_PID;
      if (pid && !window.__chatgptHtpmClickedAt) {
        window.__chatgptHtpmClickedAt = Date.now();
        location.assign(`https://chatgpt.com/g/${pid}/project`);
        return { ready: false, needManualAuth: false, enteringProject: "HTPM" };
      }
      if (window.__chatgptHtpmClickedAt && Date.now() - window.__chatgptHtpmClickedAt < 2500) {
        return { ready: false, needManualAuth: false, waitingProject: "HTPM" };
      }
    }

    // Đóng hộp thoại chào mừng/thông báo nhỏ nếu có nút Close thông thường (không đụng tới xác minh)
    const ed = findEditor();
    const turns = $$('[data-testid^="conversation-turn-"], [data-message-author-role]');
    const convId = (location.pathname.match(/\/c\/([0-9a-f-]{36})/i) || [])[1] || "";
    return {
      ready: !!(ed && visible(ed)),
      needManualAuth: false,
      turnCount: $$('[data-message-author-role="assistant"]').length,
      totalTurns: turns.length,
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

  function poll({ prevAssistantCount = 0, t0 = 0 }) {
    const elapsed = Date.now() - t0;
    const stopBtn = findStopButton();
    const assistantTurns = $$('[data-message-author-role="assistant"]');
    const newTurns = assistantTurns.slice(Math.max(0, prevAssistantCount));
    const latestScope = newTurns.length ? newTurns[newTurns.length - 1] : null;
    const rawScopeText = latestScope ? txt(latestScope) : "";
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
      /reached your.*limit|đạt đến giới hạn|đạt giới hạn tạo|try again later|thử lại sau|too many requests/i.test(
        cleanedReplyText
      );
    if (!isStreaming && newTurns.length > 0 && images.length === 0 && isHardQuotaOrLimit && elapsed > 5000) {
      return {
        state: "failed",
        hardLimit: true,
        error: "ChatGPT chạm giới hạn lượt tạo ảnh: " + cleanedReplyText.replace(/\s+/g, " ").slice(0, 260),
        images: [],
      };
    }

    // Chờ tối thiểu 45 giây sau khi dừng hẳn stream mà vẫn chỉ có văn bản thực sự (dài > 25 ký tự sau khi bỏ dòng 'Đã suy luận') mới báo lỗi
    if (!isStreaming && newTurns.length > 0 && images.length === 0 && elapsed > 45000 && cleanedReplyText.length > 25) {
      return {
        state: "failed",
        error: "ChatGPT trả lời bằng chữ thay vì tạo ảnh: " + cleanedReplyText.replace(/\s+/g, " ").slice(0, 260),
        images: [],
      };
    }

    return { state: "running", imagesCount: images.length, isStreaming, elapsed };
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
    const convId = (location.pathname.match(/\/c\/([0-9a-f-]{36})/i) || [])[1] || "";
    if (!convId) {
      return { deleted: false, skipped: true, reason: "no_conv_id" };
    }

    // Tầng 1: Xóa sạch cuộc trò chuyện ngay trong ngữ cảnh trang (nhanh ~200ms, không nháy UI, không bao giờ lộ hay trả token ra ngoài)
    try {
      const sessRes = await fetch("/api/auth/session", { credentials: "include" });
      const sess = sessRes.ok ? await sessRes.json().catch(() => ({})) : {};
      const tok = typeof sess?.accessToken === "string" ? sess.accessToken : "";
      const headers = { "Content-Type": "application/json" };
      if (tok) headers.Authorization = "Bearer " + tok;
      const patchRes = await fetch(`/backend-api/conversation/${convId}`, {
        method: "PATCH",
        credentials: "include",
        headers,
        body: JSON.stringify({ is_visible: false }),
      });
      if (patchRes.ok) {
        return { deleted: true, method: "api", convId };
      }
    } catch {}

    // Tầng 2 (Dự phòng giao diện): Bấm nút menu "..." góc phải cuộc trò chuyện -> Xóa / Delete -> Xác nhận
    const waitMs = (ms) => new Promise((r) => setTimeout(r, ms));
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
    version: 2,
    inspectState,
    getComposerCenter,
    getSendCenter,
    uploadsSettled,
    poll,
    fetchImageAsBase64,
    deleteCurrentConversation,
  };
})();
