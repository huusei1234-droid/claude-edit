/**
 * UI page driver cho Gemini Web Video (https://gemini.google.com/u/<n>/videos).
 * Hỗ trợ song ngữ Tiếng Việt + Tiếng Anh, chọn thời lượng 10 giây / 15 giây, tỷ lệ Ngang (16:9) / Dọc (9:16),
 * đính kèm ảnh tham chiếu, phát hiện chạm giới hạn lượt tạo video để tự xoay sang tài khoản Google Pro tiếp theo,
 * và tự xóa cuộc trò chuyện tạm vừa tạo để giữ sạch lịch sử người dùng.
 *
 * TUÂN THỦ AN TOÀN: Không bao giờ tự giải/vượt CAPTCHA hay anti-bot; chỉ xóa đúng convId mới do phiên tự động tạo ra.
 */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const txt = (e) =>
    String(e?.innerText || e?.textContent || "")
      .normalize("NFC")
      .trim();
  const attr = (e, k) =>
    String(e?.getAttribute?.(k) || "")
      .normalize("NFC")
      .trim();
  const visible = (e) => {
    if (!e) return false;
    const rc = e.getBoundingClientRect();
    return rc.width > 2 && rc.height > 2;
  };
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function dismissOnboardingPopovers() {
    for (const b of $$("button")) {
      if (!visible(b)) continue;
      const t = txt(b);
      if (/^(Tôi hiểu|Đã hiểu|Got it|OK, got it)$/i.test(t)) {
        b.click();
      }
    }
  }

  // Chặn hộp thoại chọn file của hệ điều hành nếu cần lấy trực tiếp <input type="file">
  const cap = (window.__geminiFileCap = window.__geminiFileCap || { on: false, input: null });
  if (!window.__geminiClickPatched) {
    const orig = HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click = function () {
      if (this.type === "file" && window.__geminiFileCap.on) {
        window.__geminiFileCap.input = this;
        return;
      }
      return orig.apply(this, arguments);
    };
    window.__geminiClickPatched = true;
  }

  const QUOTA_EXHAUSTED_RE =
    /reached your.*(video|generation|daily|veo)?.*limit|video generation limit|can't generate more videos|cannot generate more videos|create more videos tomorrow|generate more videos.*(after|tomorrow|later)|out of video generations|you've reached.*limit.*video|upgrade to generate more videos|upgrade to google ai|đã đạt đến giới hạn.*(video|tạo|hàng ngày)?|đạt giới hạn tạo video|giới hạn tạo video|không thể tạo thêm video|tạo thêm video vào ngày mai|hết lượt tạo video|đã dùng hết lượt.*video|thử lại vào ngày mai|nâng cấp để tạo thêm video|nâng cấp lên google ai/i;

  function composerRoot() {
    return $("input-area-v2") || $("rich-textarea")?.closest("form") || document.body;
  }

  function findEditor() {
    const root = composerRoot();
    return (
      $('rich-textarea .ql-editor[contenteditable="true"]', root) ||
      $('.ql-editor[contenteditable="true"]', root) ||
      $('div[contenteditable="true"][role="textbox"]', root)
    );
  }

  function findSendButton() {
    const root = composerRoot();
    const candidates = [
      $("button.send-button", root),
      $('button[aria-label*="Send message" i]', root),
      $('button[aria-label*="Send prompt" i]', root),
      $('button[aria-label*="Gửi tin nhắn" i]', root),
      $('button[aria-label*="Gửi câu lệnh" i]', root),
      $('button[aria-label="Gửi" i]', root),
      $('button[aria-label="Send" i]', root),
    ].filter(Boolean);
    return (
      candidates.find(
        (b) =>
          visible(b) &&
          !b.disabled &&
          b.getAttribute("aria-disabled") !== "true" &&
          !b.classList.contains("stop")
      ) || null
    );
  }

  function findStopButton() {
    const root = composerRoot();
    const candidates = [
      $("button.stop", root),
      $('button[aria-label*="Stop response" i]', root),
      $('button[aria-label*="Stop generating" i]', root),
      $('button[aria-label*="Dừng phản hồi" i]', root),
      $('button[aria-label*="Dừng" i]', root),
    ].filter(Boolean);
    return candidates.find(visible) || null;
  }

  function readAccountEmail() {
    const accEl = $$("a, button").find((el) =>
      /^(Google Account|Tài khoản Google)/i.test(el.getAttribute("aria-label") || "")
    );
    const aria = accEl?.getAttribute("aria-label") || "";
    const m = aria.match(/\(([^)\s]+@[^)\s]+)\)/) || aria.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
    return m ? m[1].trim().toLowerCase() : "";
  }

  function readUserPrefix() {
    const m = location.pathname.match(/^\/(u\/\d+\/)/);
    return m ? m[1] : "u/0/";
  }

  function readConvId() {
    const m = location.pathname.match(/\/app\/([0-9a-zA-Z_-]{8,})/);
    return m ? m[1] : "";
  }

  function hasVideoToolActive() {
    const root = composerRoot();
    const btns = $$("button", root).filter(visible);
    return btns.some((b) => {
      const label = `${txt(b)} ${b.getAttribute("aria-label") || ""}`;
      return (
        /Deselect Video|Bỏ chọn Video/i.test(label) ||
        /\b(10|15)\s*(s|giây)\b/i.test(label) ||
        /Duration|Thời lượng/i.test(label)
      );
    });
  }

  function inspectState() {
    const url = location.href;
    const title = document.title || "";
    const bodyHead = (document.body?.innerText || "").slice(0, 1800);

    // Phát hiện CAPTCHA hiển thị thật / cổng bảo mật -> dừng ngay, không bao giờ tự bấm (bỏ qua iframe recaptcha enterprise 0x0 ẩn mặc định của Google!)
    const hasVisibleChallengeFrame = $$(
      'iframe[src*="challenges.cloudflare.com"], iframe[src*="recaptcha/api2/bframe"]'
    ).some((f) => {
      if (!visible(f)) return false;
      const st = getComputedStyle(f);
      return st.visibility !== "hidden" && st.display !== "none" && Number(st.opacity || 1) > 0.05;
    });
    const hasChallenge =
      /Verify you are human|Xác minh bạn là con người|unusual traffic from your computer/i.test(
        `${title} ${bodyHead}`
      ) || hasVisibleChallengeFrame;
    if (hasChallenge) {
      return { ready: false, needManualAuth: true, reason: "challenge", url };
    }

    if (/accounts\.google\.com|\/ServiceLogin/i.test(url)) {
      return { ready: false, needManualAuth: true, reason: "auth_redirect", url };
    }

    const email = readAccountEmail();
    const signInLinks = $$("a, button").filter(
      (el) => visible(el) && /^(Sign in|Đăng nhập)$/i.test(txt(el))
    );
    if (!email && signInLinks.length > 0) {
      return { ready: false, needManualAuth: true, reason: "logged_out", url };
    }

    const ed = findEditor();
    const root = composerRoot();
    const pillLabels = $$("button", root)
      .filter(visible)
      .map((b) => txt(b) || b.getAttribute("aria-label") || "")
      .filter(Boolean);

    // Kiểm tra xem ngay ở khung nhập đã hiện cảnh báo hết lượt tạo video chưa
    const composerBanner = txt(root);
    const immediateQuota = QUOTA_EXHAUSTED_RE.test(composerBanner);

    return {
      ready: !!(ed && visible(ed)),
      needManualAuth: false,
      email,
      userPrefix: readUserPrefix(),
      convId: readConvId(),
      hasVideoTool: hasVideoToolActive(),
      immediateQuota,
      immediateQuotaText: immediateQuota ? composerBanner.replace(/\s+/g, " ").slice(0, 240) : "",
      responseCount: $$("model-response").length,
      videoCount: $$("model-response video, video-player video").length,
      pills: pillLabels,
      url,
    };
  }

  async function selectOverlayOption(matchRegex) {
    const items = $$(
      '.cdk-overlay-container [role="menuitem"], .cdk-overlay-container [role="menuitemradio"], .cdk-overlay-container [role="option"], .cdk-overlay-container button'
    ).filter(visible);
    const target = items.find((el) => {
      const label = `${txt(el)} ${el.getAttribute("aria-label") || ""}`;
      return matchRegex.test(label);
    });
    if (target) {
      target.click();
      await sleep(350);
      return true;
    }
    return false;
  }

  async function ensureVideoToolSelected() {
    if (hasVideoToolActive()) return { ok: true, alreadyActive: true };

    const root = composerRoot();
    // Thử bấm nút công cụ / '+' để bật công cụ Video nếu chưa mở qua /videos
    const plusOrTools = $$("button", root).find((b) => {
      if (!visible(b)) return false;
      const label = `${txt(b)} ${b.getAttribute("aria-label") || ""}`;
      return /Tools|Công cụ|Upload|Nội dung tải lên|Tải lên/i.test(label);
    });
    if (plusOrTools) {
      plusOrTools.click();
      await sleep(500);
      const picked = await selectOverlayOption(/\b(Videos|Video|Tạo video)\b/i);
      if (picked) {
        await sleep(500);
        if (hasVideoToolActive()) return { ok: true, activatedViaMenu: true };
      } else {
        document.body.click();
        await sleep(200);
      }
    }
    return { ok: hasVideoToolActive(), reason: "video_tool_not_found" };
  }

  async function configureVideoOptions({ seconds = 10, aspect = "landscape" } = {}) {
    dismissOnboardingPopovers();
    await sleep(150);
    const root = composerRoot();
    const toolRes = await ensureVideoToolSelected();
    if (!toolRes.ok) {
      return { ok: false, reason: "no_video_tool" };
    }

    // 1. Chọn thời lượng: Gemini hỗ trợ 10 giây (10s) và 15 giây (15s)
    const wantSec = Number(seconds) >= 12 ? 15 : 10;
    const durBtn = $$("button", root).find((b) => {
      if (!visible(b)) return false;
      const label = `${txt(b)} ${b.getAttribute("aria-label") || ""}`;
      return /\b(8|10|15)\s*(s|giây)\b|Duration|Thời lượng/i.test(label);
    });

    let selectedDuration = null;
    if (durBtn) {
      const curLabel = `${txt(durBtn)} ${durBtn.getAttribute("aria-label") || ""}`;
      const wantRe = new RegExp(`\\b${wantSec}\\s*(s|giây)\\b`, "i");
      if (wantRe.test(curLabel)) {
        selectedDuration = wantSec;
      } else {
        durBtn.click();
        await sleep(480);
        const picked = await selectOverlayOption(wantRe);
        if (picked) {
          selectedDuration = wantSec;
        } else {
          // Nếu tài khoản chỉ có 10s (chưa mở 15s), chọn 10s hợp lệ thay vì lỗi
          const fallback10 = await selectOverlayOption(/\b10\s*(s|giây)\b/i);
          selectedDuration = fallback10 ? 10 : wantSec;
          if (!fallback10) {
            document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
            await sleep(200);
          }
        }
      }
    }

    // 2. Chọn tỷ lệ khung hình: Ngang (16:9 / Landscape) hoặc Dọc (9:16 / Portrait)
    const wantPortrait =
      aspect === "portrait" || aspect === "9:16" || aspect === "3:4" || aspect === "2:3";
    const wantAspectRe = wantPortrait
      ? /\b(Portrait|Dọc)\b|9:16/i
      : /\b(Landscape|Ngang)\b|16:9/i;

    const aspBtn = $$("button", root).find((b) => {
      if (!visible(b)) return false;
      const label = `${txt(b)} ${b.getAttribute("aria-label") || ""}`;
      return /\b(Landscape|Portrait|Ngang|Dọc)\b|Aspect ratio|Tỷ lệ khung hình/i.test(label);
    });

    let selectedAspect = wantPortrait ? "portrait" : "landscape";
    if (aspBtn) {
      const curLabel = `${txt(aspBtn)} ${aspBtn.getAttribute("aria-label") || ""}`;
      if (!wantAspectRe.test(curLabel)) {
        aspBtn.click();
        await sleep(480);
        const picked = await selectOverlayOption(wantAspectRe);
        if (!picked) {
          document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
          await sleep(200);
        }
      }
    }

    return { ok: true, selectedDuration: selectedDuration || wantSec, selectedAspect };
  }

  async function openUploadFileMenu(interceptInput = false) {
    if (interceptInput) {
      cap.on = true;
      cap.input = null;
    }
    const root = composerRoot();
    const uploadMenuBtn = $$("button", root).find((b) => {
      if (!visible(b)) return false;
      const aria = b.getAttribute("aria-label") || "";
      const t = txt(b);
      return /Upload|Nội dung tải lên|Tải lên|Add files|Thêm tệp/i.test(`${aria} ${t}`);
    });
    if (!uploadMenuBtn) {
      if (interceptInput) cap.on = false;
      return { clickedMenu: false, clickedItem: false };
    }
    uploadMenuBtn.click();
    await sleep(500);

    const items = $$(
      '.cdk-overlay-container [role="menuitem"], .cdk-overlay-container button'
    ).filter(visible);
    const fileItem = items.find((el) => {
      const label = `${txt(el)} ${el.getAttribute("aria-label") || ""}`;
      return /Upload files|Upload image|Tải tệp lên|Tải ảnh lên|Tải hình ảnh lên/i.test(label);
    });
    if (fileItem) {
      fileItem.click();
      await sleep(400);
      if (interceptInput) cap.on = false;
      return { clickedMenu: true, clickedItem: true, hasCapturedInput: !!cap.input };
    }
    if (interceptInput) cap.on = false;
    return { clickedMenu: true, clickedItem: false };
  }

  function uploadsSettled() {
    const root = composerRoot();
    const busy = $$(
      '[role="progressbar"], mat-spinner, mat-progress-spinner, [aria-busy="true"], .loading-spinner',
      root
    ).some(visible);
    return !busy;
  }

  function countComposerAttachments() {
    const root = composerRoot();
    return $$(
      'uploader-file-preview, .file-preview, [data-test-id*="attachment"], [aria-label*="Remove file" i], [aria-label*="Xóa tệp" i], [aria-label*="Xoá tệp" i], img',
      root
    ).filter(visible).length;
  }

  async function fillPromptInEditor(promptText) {
    dismissOnboardingPopovers();
    const ed = findEditor();
    if (!ed) return { ok: false, reason: "no_editor" };
    ed.scrollIntoView({ block: "center" });
    ed.focus();
    await sleep(100);

    // Xóa sạch nội dung cũ trong .ql-editor
    try {
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(ed);
      sel.removeAllRanges();
      sel.addRange(range);
      document.execCommand("delete", false, null);
    } catch {}
    if (txt(ed).length > 0) {
      ed.innerHTML = "<p><br></p>";
    }

    const clean = String(promptText || "").trim();
    ed.focus();
    let inserted = false;
    try {
      inserted = document.execCommand("insertText", false, clean);
    } catch {}
    if (!inserted || !txt(ed)) {
      ed.textContent = clean;
      ed.dispatchEvent(
        new InputEvent("input", { bubbles: true, cancelable: true, inputType: "insertText", data: clean })
      );
    }
    await sleep(350);
    const curLen = txt(ed).length;
    const sendBtn = findSendButton();
    return {
      ok: curLen > 0,
      curLen,
      hasSendBtn: !!sendBtn,
    };
  }

  function clickSendOrGetCenter() {
    dismissOnboardingPopovers();
    captureVideoBaseline();
    const b = findSendButton();
    if (!b) return { clicked: false, center: null };
    b.scrollIntoView({ block: "center" });
    const r = b.getBoundingClientRect();
    b.click();
    return {
      clicked: true,
      center: { x: r.left + r.width / 2, y: r.top + r.height / 2 },
    };
  }

  function checkSubmissionAccepted(prevResponseCount = 0) {
    const ed = findEditor();
    const edEmpty = !ed || txt(ed).length === 0;
    const newTurn = $$("model-response").length > prevResponseCount || !!findStopButton();
    const snack = txt($("mat-snack-bar-container, simple-snack-bar"));
    return {
      accepted: newTurn || edEmpty,
      newTurn,
      edEmpty,
      edLen: ed ? txt(ed).length : 0,
      snack,
      quotaHit: QUOTA_EXHAUSTED_RE.test(snack),
    };
  }

  function getComposerCenter() {
    const ed = findEditor();
    if (!ed) return null;
    ed.scrollIntoView({ block: "center" });
    const r = ed.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }

  function captureVideoBaseline() {
    window.__geminiBaselineVideos = $$("video")
      .map((v) => v.currentSrc || v.src || "")
      .filter(Boolean);
    return window.__geminiBaselineVideos.length;
  }

  function getSendCenter() {
    captureVideoBaseline();
    const b = findSendButton();
    if (!b) return null;
    b.scrollIntoView({ block: "center" });
    const r = b.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }

  function poll({ prevResponseCount = 0, t0 = 0 }) {
    const elapsed = Date.now() - t0;
    const stopBtn = findStopButton();
    const allResponses = $$("model-response");
    const newResponses = allResponses.slice(Math.max(0, prevResponseCount));
    const latest = newResponses.length ? newResponses[newResponses.length - 1] : null;
    const latestText = latest ? txt(latest) : "";
    const snackText = txt($("mat-snack-bar-container, simple-snack-bar, .cdk-overlay-container"));
    const combinedNotice = `${latestText} ${snackText}`.trim();

    // Kiểm tra video mới sinh trong model-response mới
    const baseSet = new Set(window.__geminiBaselineVideos || []);
    const scopeRoot = latest || document.body;
    const videos = $$("video", scopeRoot)
      .map((v) => ({
        src: v.currentSrc || v.src || "",
        readyState: v.readyState || 0,
        w: v.videoWidth || 0,
        h: v.videoHeight || 0,
      }))
      .filter((v) => v.src && !baseSet.has(v.src));

    const dlBtn = latest
      ? $$(
          'button[aria-label*="Download video" i], button[aria-label*="Tải video" i], button[aria-label*="Tải xuống video" i]',
          latest
        ).find(visible)
      : null;

    const hasProgressInTurn = Boolean(
      latest &&
        $$(
          'mat-progress-bar, mat-spinner, mat-progress-spinner, [role="progressbar"], [aria-busy="true"], .loading-skeleton',
          latest
        ).some(visible)
    );
    const hasGeneratingWords =
      elapsed < 360000 &&
      /Generating video|Creating video|Generating your video|Đang tạo video|Đang dựng video|\b\d{1,2}%\b/i.test(
        latestText
      );
    const isGenerating = !!stopBtn || hasProgressInTurn || hasGeneratingWords;

    // Video hoàn tất khi có thẻ <video src="..."> (và nút Download video hoặc hết trạng thái đang tạo)
    if (videos.length > 0 && (dlBtn || !isGenerating) && elapsed > 3000) {
      return {
        state: "done",
        videoSrc: videos[videos.length - 1].src,
        hasDownloadBtn: !!dlBtn,
        convId: readConvId(),
        elapsed,
      };
    }

    // Phát hiện chạm giới hạn tạo video của tài khoản hiện tại -> chuyển ngay sang tài khoản Pro tiếp theo!
    if (videos.length === 0 && QUOTA_EXHAUSTED_RE.test(combinedNotice) && elapsed > 2000) {
      return {
        state: "quota_exhausted",
        error: combinedNotice.replace(/\s+/g, " ").slice(0, 280),
        convId: readConvId(),
        elapsed,
      };
    }

    // Nếu đã dừng hẳn tạo sau > 20 giây mà không có thẻ video hay khung video-player, báo lỗi để xử lý
    const hasVideoPlayerContainer = !!(latest && $("video-player", latest));
    if (
      !isGenerating &&
      !hasVideoPlayerContainer &&
      newResponses.length > 0 &&
      videos.length === 0 &&
      elapsed > 20000 &&
      latestText.length > 15
    ) {
      const isQuota = QUOTA_EXHAUSTED_RE.test(latestText);
      return {
        state: isQuota ? "quota_exhausted" : "failed",
        error: latestText.replace(/\s+/g, " ").slice(0, 280),
        convId: readConvId(),
        elapsed,
      };
    }

    return {
      state: "running",
      isGenerating,
      hasVideoPlayerContainer,
      convId: readConvId(),
      elapsed,
    };
  }

  function clickDownloadVideoInLatest(prevResponseCount = 0) {
    const allResponses = $$("model-response");
    const newResponses = allResponses.slice(Math.max(0, prevResponseCount));
    const scope = newResponses.length
      ? newResponses[newResponses.length - 1]
      : allResponses[allResponses.length - 1] || document.body;

    const dlBtn = $$(
      'button[aria-label*="Download video" i], button[aria-label*="Tải video" i], button[aria-label*="Tải xuống video" i]',
      scope
    ).find(visible);
    if (dlBtn) {
      dlBtn.scrollIntoView({ block: "center" });
      dlBtn.click();
      return { clicked: true, method: "button", label: dlBtn.getAttribute("aria-label") || "" };
    }

    const vid = $("video[src]", scope);
    if (vid && vid.src) {
      const a = document.createElement("a");
      a.href = vid.src;
      a.download = "gemini_video.mp4";
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      a.remove();
      return { clicked: true, method: "anchor", src: vid.src };
    }
    return { clicked: false };
  }

  async function deleteSpecificConversation(expectedConvId) {
    const curConvId = readConvId();
    if (!expectedConvId || !curConvId || curConvId !== expectedConvId) {
      return { deleted: false, skipped: true, reason: "conv_id_mismatch", curConvId, expectedConvId };
    }

    // Tìm đúng dòng hội thoại đang chọn (.selected) trong thanh bên khớp với cuộc trò chuyện vừa tạo
    let activeMore = $$("button").find((b) => {
      if (!visible(b)) return false;
      const a = attr(b, "aria-label");
      if (!/^(More options for|Lựa chọn khác cho)\s+/i.test(a)) return false;
      const row =
        b.closest('[data-test-id="conversation"], .conversation-items-container, li') ||
        b.parentElement;
      return (
        row &&
        (row.classList.contains("selected") ||
          !!row.querySelector(".selected") ||
          row.getAttribute("aria-current") === "page")
      );
    });

    // Nếu thanh bên đang thu gọn, mở tạm thanh bên để thấy mục hội thoại đang chọn
    if (!activeMore) {
      const openNavBtn = $$("button").find((b) =>
        visible(b) && /^(Main menu|Open side panel|Mở thanh bên|Trình đơn chính)/i.test(attr(b, "aria-label"))
      );
      if (openNavBtn) {
        openNavBtn.click();
        await sleep(450);
      }
      const selectedRow =
        $('[data-test-id="conversation"].selected') ||
        $(`a[href*="/app/${expectedConvId}"]`)?.closest("div, li");
      if (selectedRow) {
        selectedRow.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
        await sleep(200);
        const container = selectedRow.parentElement || selectedRow;
        activeMore = $$("button", container).find((b) =>
          /^(More options for|Lựa chọn khác cho)\s+/i.test(attr(b, "aria-label"))
        );
      }
    }

    if (!activeMore) {
      return { deleted: false, reason: "no_active_more_btn", curConvId };
    }

    activeMore.click();
    await sleep(480);

    const menuItems = $$(
      '.cdk-overlay-container button, .cdk-overlay-container [role="menuitem"]'
    ).filter(visible);
    const delItem = menuItems.find((el) =>
      /\b(Delete|Xóa|Xoá)\b/i.test(`${txt(el)} ${attr(el, "data-test-id")}`)
    );
    if (!delItem) {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      return { deleted: false, reason: "no_delete_menuitem", curConvId };
    }

    delItem.click();
    await sleep(480);

    const dlgBtns = $$('mat-dialog-container button, [role="dialog"] button').filter(visible);
    const confirmBtn = dlgBtns.find(
      (b) =>
        /^(Delete|Xóa|Xoá)$/i.test(txt(b).replace(/^delete[_a-z]*\s*/i, "").trim()) ||
        /confirm/i.test(attr(b, "data-test-id"))
    );
    if (confirmBtn) {
      confirmBtn.click();
      await sleep(650);
      return { deleted: true, convId: curConvId };
    }

    return { deleted: false, reason: "no_confirm_btn", curConvId };
  }

  window.__geminiUi = {
    inspectState,
    dismissOnboardingPopovers,
    ensureVideoToolSelected,
    configureVideoOptions,
    openUploadFileMenu,
    uploadsSettled,
    countComposerAttachments,
    fillPromptInEditor,
    clickSendOrGetCenter,
    checkSubmissionAccepted,
    getComposerCenter,
    captureVideoBaseline,
    getSendCenter,
    poll,
    clickDownloadVideoInLatest,
    deleteSpecificConversation,
  };
})();
