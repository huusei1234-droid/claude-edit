/**
 * UI driver — điều khiển giao diện web Google Flow ngay trong trang (không API, không captcha riêng).
 * Electron (desktop/flow-driver.js) nạp file này vào cửa sổ Flow bằng executeJavaScript rồi gọi
 *   window.__flowUi.submit(job)  -> điền ảnh + prompt + cài đặt, bấm tạo, trả {baseline, expect}
 *   window.__flowUi.poll({baseline, expect, t0}) -> {state:'running'|'done'|'failed', videos:[{id,url}]}
 *
 * Selector dùng tên icon Material (add, arrow_forward, close, videocam, crop_free, ...) và class
 * để không phụ thuộc ngôn ngữ giao diện. Mọi selector tập trung ở SEL bên dưới để sửa nhanh.
 */
(() => {

  const SEL = {
    editor: '.ProseMirror',
    composer: '.base-prompt-box',
    generate: 'button.generate-icon-button, button[aria-label="Bắt đầu tạo"], button[aria-label="Start generating"], button[aria-label="Generate"]',
    settings: 'button.settings-trigger-button',
    clearPrompt: 'button[aria-label="Xoá câu lệnh"], button[aria-label="Clear prompt"]',
    addMedia: 'button[aria-label="Thêm thành phần vào ô nhập câu lệnh"], button[aria-label="Add media to prompt"], button[aria-label="Add ingredient to prompt"]',
    pickerSearch: '.cdk-overlay-container input.search-input, .cdk-overlay-container input[aria-label="Tìm kiếm"], .cdk-overlay-container input[aria-label="Tìm kiếm thành phần"], .cdk-overlay-container input[aria-label="Search"], .cdk-overlay-container input[aria-label="Search for assets"]',
    pickerOption: 'button.asset-item, button[role=option].asset-item',
    pickerAdd: 'button.detail-add-to-prompt-btn',
    pickerUpload: 'button.sidebar-upload-btn, .sidebar-footer',
    chip: '.mention-chip',
    composerThumbRemove: '.chip-container',
  };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const txt = (e) => (e?.innerText || e?.textContent || '').trim();
  const log = [];
  const note = (m) => { log.push(`${new Date().toISOString().slice(11, 19)} ${m}`); if (log.length > 200) log.shift(); };

  async function waitFor(fn, timeout = 15000, step = 150, what = '') {
    const t0 = Date.now();
    for (;;) {
      let v;
      try { v = await fn(); } catch { v = null; }
      if (v) return v;
      if (Date.now() - t0 > timeout) throw new Error('UI_TIMEOUT: ' + what);
      await sleep(step);
    }
  }

  // Chặn input.click() của Flow khi ta đang upload để lấy input file mà không mở hộp thoại hệ thống.
  // trạng thái bắt input nằm trên window để bản driver nạp lại vẫn dùng chung bản vá click
  const cap = (window.__flowUiCap = window.__flowUiCap || { on: false, input: null });
  if (!window.__flowUiClickPatched) {
    const orig = HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click = function () {
      if (this.type === 'file' && window.__flowUiCap.on) { window.__flowUiCap.input = this; return; }
      return orig.apply(this, arguments);
    };
    window.__flowUiClickPatched = true;
  }

  const realClick = (el) => {
    if (!el) throw new Error('UI_NO_ELEMENT');
    el.focus?.();
    el.click();
  };

  const iconBtn = (root, icon) => $$('button', root).find((b) => txt(b).split('\n')[0].trim() === icon);

  // ───────── Cài đặt (video/ảnh, khung hình/thành phần, tỉ lệ, model, độ phân giải, giây, số lượng) ─────────
  async function openSettings() {
    const open = () => $$('button[role=radio]').find((b) => /videocam/.test(txt(b)) && b.getBoundingClientRect().width);
    if (open()) return;
    const trigger = await waitFor(() => $(SEL.settings), 10000, 200, 'settings button');
    for (let i = 0; i < 3; i++) {
      realClick(trigger);
      try { await waitFor(open, 2500, 150, 'settings popover'); return; } catch { /* bấm lại */ }
    }
    throw new Error('UI_TIMEOUT: settings popover');
  }
  const radio = (re) => $$('button[role=radio]').find((b) => re.test(txt(b)) && b.getBoundingClientRect().width);
  async function pickRadio(re, label) {
    const b = await waitFor(() => radio(re), 4000, 150, 'radio ' + label);
    if (b.getAttribute('aria-checked') !== 'true') { realClick(b); await sleep(250); }
  }
  async function setModel(name) {
    const btn = $$('button').find((b) => /arrow_drop_down/.test(txt(b)) && b.getBoundingClientRect().width);
    if (!btn) return;
    const aliases = [name];
    if (/Nhanh/i.test(name)) aliases.push(name.replace(/Nhanh/gi, 'Fast'));
    if (/Fast/i.test(name)) aliases.push(name.replace(/Fast/gi, 'Nhanh'));
    if (/Chất lượng/i.test(name)) aliases.push(name.replace(/Chất lượng/gi, 'Quality'));
    if (/Quality/i.test(name)) aliases.push(name.replace(/Quality/gi, 'Chất lượng'));
    if (aliases.some((a) => txt(btn).includes(a))) return;
    realClick(btn);
    const opt = await waitFor(() => $$('[role=option],mat-option,.mat-mdc-option,[role=menuitem]').find((o) => {
      const line0 = txt(o).split('\n')[0].trim();
      return aliases.some((a) => line0.endsWith(a) || line0.includes(a));
    }), 4000, 150, 'model ' + name);
    realClick(opt);
    await sleep(300);
  }
  const chipSeconds = () => { const m = txt($(SEL.settings)).match(/(\d+)\s*(?:giây|s\b|sec)/i); return m ? +m[1] : null; };
  async function setSeconds(sec) {
    const input = $('input.mdc-slider__input');
    if (!input) return;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    const min = +input.min, max = +input.max;
    for (let guess = Math.min(max, Math.max(min, sec - 3)), tries = 0; tries < 6; tries++) {
      setter.call(input, String(guess));
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      await sleep(250);
      const cur = chipSeconds();
      if (cur === sec || cur == null) return;
      guess = Math.min(max, Math.max(min, guess + (sec > cur ? 1 : -1)));
    }
  }

  async function applySettings(job) {
    await openSettings();
    if (job.kind === 'image') {
      await pickRadio(/^\s*image\b/, 'image');
      const ratio = job.ratio || (job.aspect === 'portrait' ? '9:16' : '16:9');
      await pickRadio(new RegExp('(^|\\s)' + ratio.replace(':', ':') + '$'), 'ratio ' + ratio);
      if (job.model) await setModel(job.model);
      if (job.quality) await pickRadio(new RegExp('^\\s*' + job.quality + '\\s*$', 'i'), 'quality ' + job.quality);
      await pickRadio(new RegExp('^x' + (job.count || 1) + '$'), 'count');
      await closeSettings();
      return;
    }
    await pickRadio(/videocam/, 'video');
    await pickRadio(job.mode === 'frames' ? /crop_free/ : /chrome_extension/, 'mode');
    await pickRadio(job.aspect === 'portrait' ? /crop_9_16/ : /crop_16_9/, 'aspect');
    if (job.model) await setModel(job.model);
    // một số model (Veo) không có lựa chọn độ phân giải: bỏ qua thay vì báo lỗi
    await pickRadio(new RegExp('^\\s*(?:info\\s*)?' + (job.resolution || '720p') + '\\b|' + (job.resolution || '720p')), 'resolution').catch(() => {});
    if (job.seconds) await setSeconds(job.seconds);
    await pickRadio(new RegExp('^x' + (job.count || 1) + '$'), 'count');
    await closeSettings();
  }
  const settingsOpen = () => { const r = $$('button[role=radio]').find((b) => /videocam/.test(txt(b))); return !!(r && r.getBoundingClientRect().width); };
  async function closeSettings() {
    if (!settingsOpen()) return;
    realClick($(SEL.settings)); // bấm lại nút cài đặt để đóng bảng
    try { await waitFor(() => !settingsOpen(), 2500, 100, 'close settings'); }
    catch { document.body.click(); await waitFor(() => !settingsOpen(), 2500, 100, 'close settings (click ngoài)'); }
  }

  // ───────── Composer ─────────
  async function clearComposer() {
    const clr = $(SEL.clearPrompt);
    if (clr) { realClick(clr); await sleep(400); }
    const ed = $(SEL.editor);
    if (ed) {
      ed.focus();
      document.execCommand('selectAll', false, null);
      document.execCommand('delete', false, null);
    }
    // Gỡ sạch 100% mọi thumbnail / chip thành phần còn sót (tránh vượt giới hạn 3 ảnh của Flow gây lỗi 'Maximum number of attachments reached')
    for (let i = 0; i < 12; i++) {
      const rm = $$('button', $(SEL.composer) || document).find((b) => {
        const t = txt(b).split('\n').map((s) => s.trim());
        const aria = (b.getAttribute('aria-label') || '').toLowerCase();
        return t.includes('cancel') || t.includes('close') || /remove|xoá|xóa|delete/i.test(aria);
      });
      if (!rm) break;
      realClick(rm); await sleep(220);
    }
  }

  async function openPicker() {
    if ($(SEL.pickerSearch) && $(SEL.pickerSearch).getBoundingClientRect().width) return;
    // chế độ Khung hình không có nút "+": dùng ô "Bắt đầu" để mở cùng hộp chọn ảnh
    const add = $(SEL.addMedia) || iconBtn($(SEL.composer) || document, 'add') || $('.frame-trigger button');
    const shown = () => { const s = $(SEL.pickerSearch); return s && s.getBoundingClientRect().width; };
    await closeSettings().catch(() => {}); // bảng cài đặt còn mở sẽ nuốt cú bấm
    await sleep(300);
    realClick(add);
    // chờ lâu hơn trước khi bấm lại: bấm lần 2 khi hộp đang mở dở sẽ đóng nó lại
    try { await waitFor(shown, 7000, 150, 'asset picker'); }
    catch { if (shown()) return; realClick(add); await waitFor(shown, 7000, 150, 'asset picker (retry)'); }
  }
  const stemOf = (name) => String(name || '').trim().replace(/\.(png|jpe?g|webp|gif)$/i, '').trim();
  const extOf = (name, mime) => {
    const m = String(name || '').match(/\.(png|jpe?g|webp|gif)$/i);
    if (m) return m[0].toLowerCase();
    if (/jpeg|jpg/i.test(mime || '')) return '.jpg';
    if (/webp/i.test(mime || '')) return '.webp';
    return '.png';
  };
  const isGenericAssetName = (name) => /^(ảnh|anh|image|img|asset|node|unnamed|untitled)[\s_-]*\d*$/i.test(stemOf(name));
  const fastHash = (str) => {
    const s = String(str || '');
    let h = 2166136261 >>> 0;
    const step = Math.max(1, Math.floor(s.length / 4096));
    h ^= s.length;
    h = Math.imul(h, 16777619) >>> 0;
    for (let i = 0; i < s.length; i += step) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h.toString(16).padStart(8, '0');
  };
  const isUploadingText = (s) => /Đang tải lên|Uploading|\b\d{1,3}%/i.test(String(s || ''));

  const optName = (o) => {
    if (!o || o.disabled || o.getAttribute('aria-disabled') === 'true') return '';
    const raw = txt(o);
    if (isUploadingText(raw)) return '';
    const lines = raw.split('\n').map((s) => s.trim()).filter(Boolean);
    return lines.find((s) => !/^(image|images|videocam|videos|voice_selection|accessibility_new|face|Hình ảnh|Video|Giọng nói|Image|Audio|Voice)$/i.test(s)) || lines[0] || '';
  };
  const isImageOption = (o) => !/^(videocam)\b|\bVideo\b/i.test(txt(o));

  const pickerShown = () => { const s = $(SEL.pickerSearch); return !!(s && s.getBoundingClientRect().width); };

  async function setPickerSearch(q) {
    const s = $(SEL.pickerSearch);
    if (!s || !s.getBoundingClientRect().width) return false;
    const want = String(q || '');
    if (s.value === want) return true;
    s.focus();
    document.execCommand('selectAll', false, null);
    if (want) document.execCommand('insertText', false, want);
    else document.execCommand('delete', false, null);
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (s.value !== want) {
      if (setter) setter.call(s, want); else s.value = want;
      s.dispatchEvent(new Event('input', { bubbles: true }));
    }
    await sleep(want ? 320 : 220);
    return true;
  }

  function findMatchingOptionInPicker(targetName, allowStemMatch = true) {
    const tLow = String(targetName || '').trim().toLowerCase();
    const tStem = stemOf(targetName).toLowerCase();
    const opts = $$(SEL.pickerOption).filter((o) => o.getBoundingClientRect().width > 0 && isImageOption(o));
    const exact = opts.find((o) => optName(o).toLowerCase() === tLow);
    if (exact) return exact;
    if (allowStemMatch && tStem && !isGenericAssetName(targetName)) {
      return opts.find((o) => {
        const on = optName(o);
        return on && stemOf(on).toLowerCase() === tStem;
      }) || null;
    }
    return null;
  }

  function findExistingNameOnGrid(targetName, allowStemMatch = true) {
    const tLow = String(targetName || '').trim().toLowerCase();
    const tStem = stemOf(targetName).toLowerCase();
    if (!tLow) return '';
    const tiles = $$('flow-image-tile').filter((t) => !t.closest('.cdk-overlay-container') && !isUploadingText(txt(t)) && !!($('img', t)?.src));
    for (const t of tiles) {
      const ft = txt($('.footer-title', t));
      if (ft && ft.toLowerCase() === tLow) return ft;
    }
    if (allowStemMatch && tStem && !isGenericAssetName(targetName)) {
      for (const t of tiles) {
        const ft = txt($('.footer-title', t));
        if (ft && stemOf(ft).toLowerCase() === tStem) return ft;
      }
    }
    return '';
  }

  async function selectOptionElement(opt) {
    realClick(opt);
    await sleep(450);
    // chọn từ "@" thì Flow chèn chip luôn; chọn từ nút + thì phải bấm "Thêm vào câu lệnh"
    const addBtn = await waitFor(() => {
      const b = $(SEL.pickerAdd);
      return b && b.getBoundingClientRect().width && !b.disabled ? b : null;
    }, 1800, 120, 'add').catch(() => null);
    if (addBtn) realClick(addBtn);
    await sleep(650);
  }

  async function uploadFileInOpenPicker(file) {
    if (!$(SEL.pickerUpload)) {
      await closePicker().catch(() => {});
      await sleep(250);
    }
    await openPicker();
    await setPickerSearch('');
    cap.on = true; cap.input = null;
    const up = await waitFor(() => $(SEL.pickerUpload) || $$('button').find((b) => /sidebar-upload-btn|Tải nội dung nghe nhìn lên|Upload media/i.test(b.className + ' ' + txt(b))), 5000, 150, 'upload button');
    realClick(up.closest('button') || up.querySelector('button') || up);
    try { await waitFor(() => cap.input, 4000, 100, 'file input'); } finally { cap.on = false; }
    const dt = new DataTransfer(); dt.items.add(file);
    cap.input.files = dt.files;
    cap.input.dispatchEvent(new Event('change', { bubbles: true }));
    await waitFor(() => findMatchingOptionInPicker(file.name, false), 60000, 300, 'upload ' + file.name);
    await sleep(1200); // chờ thumbnail ổn định sau khi hết trạng thái "Đang tải lên"
  }

  async function pickAsset(name, fallbackIm = null) {
    let opt = findMatchingOptionInPicker(name, true);
    if (!opt) {
      // Nếu dự án có nhiều ảnh khiến ảnh cũ cuộn xuống dưới virtual-scroll -> gõ tìm theo tên để lọc tức thì!
      await setPickerSearch(stemOf(name));
      opt = await waitFor(() => findMatchingOptionInPicker(name, true), 3500, 180, 'asset ' + name).catch(() => null);
    }
    if (!opt && fallbackIm && fallbackIm.base64) {
      note('asset missing in picker, uploading fallback once: ' + name);
      const f = b64ToFile(fallbackIm.base64, fallbackIm.mime, name);
      await uploadFileInOpenPicker(f);
      opt = await waitFor(() => findMatchingOptionInPicker(name, true), 8000, 200, 'asset after fallback ' + name);
    }
    if (!opt) throw new Error('UI_TIMEOUT: asset ' + name);
    await selectOptionElement(opt);
    if (pickerShown()) await setPickerSearch('').catch(() => {});
  }

  async function uploadFile(file) {
    await uploadFileInOpenPicker(file);
    await closePicker();
  }

  async function closePicker() {
    if (!pickerShown()) return;
    await setPickerSearch('').catch(() => {});
    const bd = $('.cdk-overlay-backdrop');
    if (bd) { bd.click(); await sleep(250); }
    if (!pickerShown()) return;
    const s = $(SEL.pickerSearch);
    if (s) {
      for (const type of ['keydown', 'keyup']) {
        s.dispatchEvent(new KeyboardEvent(type, { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }));
      }
    }
    try { await waitFor(() => !pickerShown(), 2000, 100, 'close picker'); } catch { $('.cdk-overlay-backdrop')?.click(); document.body.click(); await sleep(500); }
  }

  /**
   * Đảm bảo ảnh tham chiếu có mặt trong dự án Flow hiện tại mà KHÔNG BAO GIỜ tải trùng lặp:
   * 1. Nếu đã xác thực trong bộ nhớ phiên của project này (cùng mã băm nội dung) -> tái sử dụng ngay (0ms).
   * 2. Nếu đã có sẵn thẻ <flow-image-tile> hoàn tất trên lưới dự án -> tái sử dụng ngay (0ms).
   * 3. Mở hộp chọn thành phần, lọc theo tên -> nếu đã có trong Flow -> tái sử dụng ngay, KHÔNG upload lại!
   * 4. Chỉ khi thực sự chưa có trong dự án Flow mới tải lên đúng 1 lần duy nhất.
   */
  async function ensureAssetInFlow(im, { attachNow = false } = {}) {
    const projKey = location.pathname;
    const reg = (window.__flowAssetRegistry = window.__flowAssetRegistry || {});
    const projMap = (reg[projKey] = reg[projKey] || {});
    const hash = fastHash(im.base64 || '');

    let desiredName = String(im.name || 'ref.png').trim();
    if (isGenericAssetName(desiredName) && hash) {
      desiredName = `ref-${hash}${extOf(desiredName, im.mime)}`;
    } else if (projMap[desiredName] && projMap[desiredName].hash && projMap[desiredName].hash !== hash) {
      // Nội dung ảnh thay đổi nhưng giữ tên node cũ -> gắn hậu tố hash để không dùng nhầm ảnh cũ
      desiredName = `${stemOf(desiredName)}-${hash.slice(0, 6)}${extOf(desiredName, im.mime)}`;
    }

    const allowStem = !isGenericAssetName(desiredName);
    const cached = projMap[desiredName];
    if (cached && cached.hash === hash && cached.flowName) {
      const gridStillThere = findExistingNameOnGrid(cached.flowName, false);
      if (gridStillThere || (Date.now() - (cached.verifiedAt || 0) < 25 * 60 * 1000)) {
        note('reuse cached Flow asset: ' + cached.flowName);
        if (attachNow) {
          await openPicker();
          await pickAsset(cached.flowName, { ...im, name: desiredName });
          await closePicker();
        }
        return cached.flowName;
      }
    }

    const onGrid = findExistingNameOnGrid(desiredName, allowStem);
    if (onGrid) {
      projMap[desiredName] = projMap[im.name] = { hash, flowName: onGrid, verifiedAt: Date.now() };
      note('reuse grid Flow asset: ' + onGrid);
      if (attachNow) {
        await openPicker();
        await pickAsset(onGrid, { ...im, name: desiredName });
        await closePicker();
      }
      return onGrid;
    }

    await openPicker();
    await setPickerSearch(stemOf(desiredName));
    const existingOpt = findMatchingOptionInPicker(desiredName, allowStem);
    if (existingOpt) {
      const foundName = optName(existingOpt);
      projMap[desiredName] = projMap[im.name] = { hash, flowName: foundName, verifiedAt: Date.now() };
      note('reuse picker Flow asset: ' + foundName);
      if (attachNow) {
        await selectOptionElement(existingOpt);
      }
      await closePicker();
      return foundName;
    }

    const f = b64ToFile(im.base64, im.mime, desiredName);
    await uploadFileInOpenPicker(f);
    projMap[desiredName] = projMap[im.name] = { hash, flowName: desiredName, verifiedAt: Date.now() };
    note('uploaded new Flow asset once: ' + desiredName);
    if (attachNow) {
      const newOpt = findMatchingOptionInPicker(desiredName, false);
      if (newOpt) await selectOptionElement(newOpt);
    }
    await closePicker();
    return desiredName;
  }

  const b64ToFile = (b64, mime, name) => {
    const bin = atob(b64); const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new File([u8], name, { type: mime || 'image/png' });
  };

  function focusEditorAtEnd() {
    const ed = $$(SEL.editor).find((e) => e.getBoundingClientRect().width > 0) || $(SEL.editor);
    if (!ed) return null;
    ed.focus();
    try {
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(ed);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
    } catch {}
    return ed;
  }

  async function typeText(s) {
    if (!s) return;
    const ed = focusEditorAtEnd();
    if (!ed) return;
    document.execCommand('insertText', false, s);
    await sleep(120);
  }

  /** Điền prompt; chỉ biến LẦN XUẤT HIỆN ĐẦU TIÊN của mỗi tên ảnh (tối đa 3 chip theo giới hạn của Google Flow) thành mention chip để không bao giờ vượt trần 'Maximum number of attachments reached'! */
  async function fillPrompt(prompt, names, fallbackByName = {}, maxChips = 3) {
    const ed = $$(SEL.editor).find((e) => e.getBoundingClientRect().width > 0) || $(SEL.editor);
    ed.focus();
    document.execCommand('selectAll', false, null);
    document.execCommand('delete', false, null);
    const uniqNames = [...new Set(names.filter(Boolean))].slice(0, maxChips);
    const sorted = [...uniqNames].sort((a, b) => b.length - a.length).map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const re = sorted.length ? new RegExp('@?(' + sorted.join('|') + ')', 'g') : null;
    let last = 0; const parts = [];
    const chippedAlready = new Set();
    if (re) {
      for (const m of prompt.matchAll(re)) {
        parts.push({ t: prompt.slice(last, m.index) });
        if (!chippedAlready.has(m[1]) && chippedAlready.size < maxChips) {
          chippedAlready.add(m[1]);
          parts.push({ ref: m[1] });
        } else {
          // Lần nhắc thứ 2+ của cùng nhân vật giữ chữ thường (bỏ '@') để không bị đính kèm trùng làm tràn 3 slot của Flow!
          parts.push({ t: m[1].replace(/\.[a-z0-9]{2,4}$/i, '') });
        }
        last = m.index + m[0].length;
      }
    }
    parts.push({ t: prompt.slice(last) });
    for (const p of parts) {
      if (p.ref) {
        await waitFor(() => !pickerShown(), 1800, 80, 'prev picker close').catch(() => {});
        // Flow chỉ mở hộp chọn khi "@" đứng sau khoảng trắng/ký tự; ở đầu ô trống thì không
        const curEd = focusEditorAtEnd();
        const before = (curEd?.innerText || '').replace(/\n+$/, '');
        if (!before || !/\s$/.test(before)) await typeText(' ');
        await typeText('@');
        await waitFor(() => pickerShown(), 5000, 150, 'mention picker');
        await pickAsset(p.ref, fallbackByName[p.ref] || null);
        await waitFor(() => !pickerShown(), 2000, 100, 'mention picker close').catch(() => closePicker());
        focusEditorAtEnd();
      } else await typeText(p.t);
    }
  }

  const videoSrc = (v) => (v && (v.currentSrc || v.src || $('source', v)?.src)) || '';
  // baseline = mọi video đang có trên trang (theo src) để nhận ra video MỚI sau khi bấm tạo
  // ảnh sinh ra nằm trong lưới tile; lấy theo src (asb/ hoặc flow-content/image)
  // chữ ký (?Expires=...&Signature=...) đổi liên tục nên so sánh theo URL đã bỏ query
  const keyOf = (u) => String(u || '').split('?')[0];
  const tileImgSrcs = () => $$('cdk-virtual-scroll-viewport img, .tiles-container img')
    .filter((i) => !i.closest('.cdk-overlay-container') && !/\b\d{1,3}%/.test(txt(i.closest('flow-image-tile, .tile, [class*=tile]') || i.parentElement || i)))
    .map((i) => i.currentSrc || i.src || '').filter((u) => /flow\.google\.com\/asb\/|flow-content\.google\/image\//.test(u));
  // video xong: thẻ <flow-video-tile> bản mới có sẵn <video src="...=mm,22,15"> (720p MP4 trực tiếp) hoặc img.thumbnail
  const tileMediaUrl = (t) => videoSrc($('video', t)) || $('img.thumbnail', t)?.src || '';
  const gridTiles = () => $$('flow-video-tile, flow-error-tile').filter((t) => !t.closest('.cdk-overlay-container'));
  const gridVideoTiles = () => $$('flow-video-tile').filter((t) => !t.closest('.cdk-overlay-container'));
  const isPendingDom = (t) => Boolean($('flow-pending-tile, flow-soupy-overlay', t));
  const videoSrcs = () => [...new Set([
    ...gridVideoTiles().filter((t) => !isPendingDom(t) && !/\b\d{1,3}%/.test(txt(t))).map(tileMediaUrl),
    ...$$('video').filter((v) => !v.closest('.cdk-overlay-container')).map(videoSrc),
  ].filter((u) => /flow\.google\.com\/asb\/|flow-content\.google\//.test(u)))];
  const mediaIdsOnPage = (kind) => [...new Set(kind === 'image' ? tileImgSrcs() : videoSrcs())];

  async function submit(job) {
    const jobId = job.jobId || ('fj_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6));
    note('submit [' + jobId + '] ' + (job.prompt || '').slice(0, 40));
    await waitFor(() => $(SEL.editor), 20000, 300, 'editor').catch(() => {}); // trang vừa tải lại: chờ ô nhập
    if (!$(SEL.editor)) throw new Error('UI_NO_EDITOR: mở tab project Flow trước');
    // Tự động đóng hộp thoại "Xem tất cả nhật ký thay đổi / Bắt đầu" (What's New modal) nếu che màn hình!
    const whatsNewBtn = $$('.cdk-overlay-container button').find((b) => /^(Bắt đầu|Got it|Đóng|Close|OK)$/i.test(txt(b)));
    if (whatsNewBtn) { realClick(whatsNewBtn); await sleep(350); }
    await clearComposer();
    await applySettings(job);
    const rawImages = job.images || [];
    const maxAllowedRefs = job.mode === 'frames' ? 2 : 3;
    const dedupedImages = [];
    const seenInputKeys = new Set();
    let promptText = job.prompt || '';

    for (const im of rawImages) {
      const dedupKey = `${im.name || ''}:${fastHash(im.base64 || '')}`;
      if (seenInputKeys.has(dedupKey)) continue;
      seenInputKeys.add(dedupKey);
      dedupedImages.push(im);
    }

    // Ưu tiên giữ các ảnh được gọi tên '@...' trực tiếp trong prompt trước, sau đó cắt đúng trần của Google Flow (tối đa 3 ảnh Thành phần / 2 ảnh Khung hình)
    dedupedImages.sort((a, b) => {
      const score = (x) => {
        if (!x?.name) return 0;
        if (promptText.includes(x.name)) return 2;
        if (!isGenericAssetName(x.name) && new RegExp('@' + stemOf(x.name).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![\\w-])', 'i').test(promptText)) return 2;
        return 1;
      };
      return score(b) - score(a);
    });
    const selectedImages = dedupedImages.slice(0, maxAllowedRefs);
    // Gỡ dấu '@' của các ảnh thừa vượt quá 3 slot (nếu có) để chữ trong prompt vẫn sạch
    for (const dropped of dedupedImages.slice(maxAllowedRefs)) {
      if (dropped?.name) {
        promptText = promptText.split('@' + dropped.name).join(stemOf(dropped.name));
        if (stemOf(dropped.name)) {
          const dropRe = new RegExp('@' + stemOf(dropped.name).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![\\w.-])', 'gi');
          promptText = promptText.replace(dropRe, stemOf(dropped.name));
        }
      }
    }

    const names = [];
    const fallbackByName = {};
    let plusAttachedCount = 0;

    for (const im of selectedImages) {
      // Bước 1: Đảm bảo ảnh có sẵn trên thư viện Flow (CHƯA gắn vội qua nút '+' để tránh gắn đúp 2 lần!)
      const actualName = await ensureAssetInFlow(im, { attachNow: false });
      names.push(actualName);
      fallbackByName[actualName] = { ...im, name: actualName };

      // Bước 2: Đồng bộ tên thực tế vào prompt trước
      if (im.name && actualName !== im.name) {
        promptText = promptText.split('@' + im.name).join('@' + actualName).split(im.name).join(actualName);
      }
      if (!isGenericAssetName(im.name) && stemOf(im.name)) {
        const bareTagRe = new RegExp('@' + stemOf(im.name).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![\\w.-])', 'gi');
        promptText = promptText.replace(bareTagRe, '@' + actualName);
      }

      // Bước 3: Chỉ bấm nút '+' gắn ảnh nếu sau khi đồng bộ tên, ảnh đó KHÔNG xuất hiện trong prompt (nếu có trong prompt thì fillPrompt sẽ tự gắn bằng '@')!
      if (job.mode !== 'frames' && !promptText.includes(actualName)) {
        await openPicker();
        await pickAsset(actualName, fallbackByName[actualName]);
        await closePicker();
        plusAttachedCount++;
      }
    }
    if (job.mode === 'frames' && names.length) await attachFrames(names, fallbackByName);
    if (job.mode === 'frames') for (const n of names) promptText = promptText.split('@' + n).join('').split(n).join(''); // ảnh đã nằm ở ô khung hình, không cần tên file trong prompt
    const cleanPrompt = promptText.replace(/\n{3,}/g, '\n\n').trim();
    const remainingChipSlots = Math.max(0, maxAllowedRefs - plusAttachedCount);
    await fillPrompt(cleanPrompt, job.mode === 'frames' ? [] : names, fallbackByName, remainingChipSlots);
    await sleep(350);

    // Dọn các thẻ lỗi cũ (delete_forever) nếu còn tồn đọng trên lưới dự án để tránh Angular vẽ lại làm nhận nhầm!
    for (const et of $$('flow-error-tile').filter((t) => !t.closest('.cdk-overlay-container')).slice(0, 8)) {
      const delB = $$('button', et.closest('flow-video-tile') || et).find((b) => /delete_forever|Xoá|Delete/i.test((b.getAttribute('aria-label') || '') + ' ' + txt(b)));
      if (delB) { delB.click(); await sleep(180); }
    }

    // Đánh dấu mọi tile cũ trên lưới chính trước lúc bấm Tạo (loại trừ hộp chọn .cdk-overlay-container) để khi chạy song song nhiều luồng, mỗi lệnh nhận diện đúng 100% ô của mình!
    for (const t of gridTiles()) {
      if (!t.dataset.flowJobId) t.dataset.flowJobId = 'prior';
    }
    let plainPrefix = cleanPrompt;
    for (const n of names) plainPrefix = plainPrefix.split('@' + n).join('').split(n).join('');
    plainPrefix = plainPrefix.replace(/\s+/g, ' ').trim().slice(0, 24).toLowerCase();

    const isErrTile = (t) => t.tagName === 'FLOW-ERROR-TILE' || !!t.querySelector('flow-error-tile') || /Không thành công|Generation failed|unusual activity/i.test(txt(t));
    const baseline = mediaIdsOnPage(job.kind);
    const errBefore = gridTiles().filter(isErrTile).length;
    const btn = $(SEL.generate) || iconBtn($(SEL.composer) || document, 'arrow_forward');
    await waitFor(() => btn && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true', 8000, 200, 'generate enabled');
    const state = { jobId, promptPrefix: plainPrefix, baseline, errBefore, t0: Date.now(), expect: job.count || 1, kind: job.kind === 'image' ? 'image' : 'video' };
    if (job.dryRun) return { ...state, dryRun: true, log: log.slice(-12) };
    if (job.trustedClick) {
      // Flow bỏ qua click giả lập ở chế độ ẩn: trả vị trí nút để Electron click bằng chuột thật
      btn.scrollIntoView({ block: 'center' });
      await sleep(180);
      const r = btn.getBoundingClientRect();
      return { ...state, clickAt: { x: r.left + r.width / 2, y: r.top + r.height / 2 }, log: log.slice(-12) };
    }
    realClick(btn);
    await sleep(1200);
    claimSpawnedTiles(jobId, state.expect);
    return { ...state, log: log.slice(-12) };
  }

  function claimSpawnedTiles(jobId, expect = 1) {
    const unclaimed = gridTiles().filter((t) => !t.dataset.flowJobId);
    const picked = unclaimed.slice(0, expect);
    for (const t of picked) {
      t.dataset.flowJobId = jobId;
    }
    const already = gridTiles().filter((t) => t.dataset.flowJobId === jobId);
    return already.length;
  }

  // Khung hình đầu/cuối: bấm ô "Bắt đầu"/"Kết thúc" -> hộp chọn ảnh; chọn ảnh là hộp tự đóng và ô nhận ảnh
  async function attachFrames(names, fallbackByName = {}) {
    for (const [i, n] of names.slice(0, 2).entries()) {
      const slot = await waitFor(() => $$('.frame-trigger')[i], 6000, 200, 'frame slot ' + i);
      await sleep(600); // chờ hộp chọn cũ đóng hẳn, kẻo bấm trúng lúc nó đang đóng
      for (let t = 0; t < 3 && !pickerShown(); t++) {
        realClick($('button', slot) || slot);
        try { await waitFor(pickerShown, 2500, 150, 'frame picker ' + i); } catch { /* bấm lại */ }
      }
      await waitFor(pickerShown, 1000, 150, 'frame picker ' + i);
      await pickAsset(n, fallbackByName[n] || null);
      await waitFor(() => !pickerShown(), 4000, 150, 'frame picker close');
    }
  }

  // Hỗ trợ chạy song song đa Tab (u/0, u/1, u/3): kiểm tra cả thẻ <flow-pending-tile> của giao diện Flow mới để không bao giờ báo xong sớm khi video còn đang render!
  const isRunning = (t) => {
    if (isPendingDom(t)) return true;
    if (/\b\d{1,3}%/.test(txt(t))) return true;
    const pb = $('.progress-bar', t);
    const st = pb?.getAttribute('style') || '';
    const m = st.match(/--progress-percent:\s*(\d+)%/);
    return !!(m && Number(m[1]) > 0 && Number(m[1]) < 100 && !tileMediaUrl(t));
  };

  function findJobTiles(j) {
    const all = gridTiles();
    const expect = j.expect || 1;
    if (j.jobId) {
      const direct = all.filter((t) => t.dataset.flowJobId === j.jobId);
      if (direct.length >= expect) return direct.slice(0, expect);
      // Dự phòng nếu Angular virtual-scroll vẽ lại thẻ DOM làm mất dataset: khớp theo chữ đầu của prompt trên footer-title & không nằm trong baseline
      if (j.promptPrefix && j.promptPrefix.length >= 6) {
        const baseKeys = new Set((j.baseline || []).map(keyOf));
        const isErrDom = (t) => t.tagName === 'FLOW-ERROR-TILE' || !!t.querySelector('flow-error-tile') || /Không thành công|Generation failed|unusual activity/i.test(txt(t));
        const curErrCount = all.filter(isErrDom).length;
        const allowErrFallback = typeof j.errBefore === 'number' ? curErrCount > j.errBefore : true;
        const byPrefix = all.filter((t) => {
          if (t.dataset.flowJobId && t.dataset.flowJobId !== j.jobId) return false;
          if (isErrDom(t) && !allowErrFallback) return false;
          const ft = txt($('.footer-title', t) || '').toLowerCase();
          const u = tileMediaUrl(t);
          if (u && baseKeys.has(keyOf(u))) return false;
          return ft && ft.startsWith(j.promptPrefix.slice(0, 16));
        });
        if (byPrefix.length >= expect) {
          for (const t of byPrefix.slice(0, expect)) t.dataset.flowJobId = j.jobId;
          return byPrefix.slice(0, expect);
        }
      }
      if (direct.length > 0) return direct;
    }
    return all.slice(0, expect);
  }

  function pollVideo(j) {
    const map = (window.__flowPollMap = window.__flowPollMap || {});
    const pKey = j.jobId || String(j.t0);
    const g = (map[pKey] = map[pKey] || { t0: j.t0, seen: false });
    const myTiles = findJobTiles(j);
    const elapsed = Date.now() - j.t0;
    if (myTiles.some((t) => isRunning(t) || t.dataset.flowJobId === j.jobId)) g.seen = true;
    const isErr = (t) => t.tagName === 'FLOW-ERROR-TILE' || !!t.querySelector('flow-error-tile') || /Không thành công|Generation failed|unusual activity/i.test(txt(t));
    const err = myTiles.find(isErr);
    if (err && g.seen) return { state: 'failed', error: txt(err).replace(/\s+/g, ' ').slice(0, 220), videos: [] };
    if (g.seen && myTiles.length >= (j.expect || 1) && myTiles.every((t) => !isRunning(t) && !!tileMediaUrl(t))) {
      return {
        state: 'done',
        videos: myTiles.map((t) => {
          const vDirect = videoSrc($('video', t));
          const u = vDirect || $('img.thumbnail', t)?.src || '';
          return { id: keyOf(u), url: u, directMp4: Boolean(vDirect) };
        }),
      };
    }
    if (!g.seen && elapsed > 120000) return { state: 'failed', error: 'Không thấy ô video mới xuất hiện trên Flow sau khi bấm tạo', videos: [] };
    return { state: 'running', videos: [], elapsed, seen: g.seen };
  }

  function poll(j) {
    if (j.kind !== 'image') return pollVideo(j);
    const videos = [];
    const srcs = j.kind === 'image' ? tileImgSrcs() : videoSrcs();
    for (const u of srcs) {
      const k = keyOf(u);
      if (u && !j.baseline.some((b) => keyOf(b) === k) && !videos.some((x) => keyOf(x.url) === k)) videos.push({ id: k, url: u });
    }
    const failed = $$('[class*=error],[class*=fail]').map(txt).find((t) => /không thể|thất bại|failed|couldn.t|vi phạm|policy/i.test(t));
    if (videos.length >= j.expect) return { state: 'done', videos };
    if (failed && Date.now() - j.t0 > 8000) return { state: 'failed', error: failed.slice(0, 200), videos };
    return { state: 'running', videos, elapsed: Date.now() - j.t0 };
  }

  window.__flowUi = { version: 3, submit, ensureAssetInFlow, claimSpawnedTiles, poll, log, mediaIdsOnPage, SEL };
})();
