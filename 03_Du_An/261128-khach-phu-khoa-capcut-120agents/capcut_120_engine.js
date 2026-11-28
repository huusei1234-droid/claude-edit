// V6 Master Engine: Exact Beloved 261127 Direct Top-to-Bottom Curved-Arc B-Roll & Text Thrower (ZERO Google Flow!)
// + Overlapping Z-Jumping Top Windows (Photoshop 2026 + ChatGPT Plus + Illustrator 2026 + Auto-Web CMS + IDE + 120-Agent Stream)
// + 100% Authentic Vietnamese CapCut PC (Progressive Media Bin + Multi-View Inspector + Ahead-of-Playhead Timeline + 120 Purposeful Cursors)
(function () {
  const meta = window.AUDIO_DATA || { fps: 60, total_frames: 1110, duration_sec: 18.5, head_top_y: 194 };
  const FPS = meta.fps || 60;
  const TOTAL_FRAMES = meta.total_frames || 1110;
  const SEQ_DUR = meta.duration_sec || (TOTAL_FRAMES / FPS);

  const HDR_W = 52;
  const TL_W  = 1014;
  const secToX = (sec) => HDR_W + (Math.max(0, Math.min(SEQ_DUR, sec)) / SEQ_DUR) * TL_W;

  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function minJerk(u) { u = clamp01(u); return u * u * u * (10 + u * (-15 + 6 * u)); }
  function fastEase(u) { u = clamp01(u); return 1 - Math.pow(1 - u, 3.2); }
  function lerp(a, b, u) { return a + (b - a) * u; }

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  const words = (window.WORDS_DATA && window.WORDS_DATA.words) ? window.WORDS_DATA.words : [];
  function findPhraseTime(kwList, fallbackRatio) {
    for (const kw of kwList) {
      const idx = words.findIndex(w => (w.n || w.w.toLowerCase()).includes(kw));
      if (idx >= 0) return words[idx].s;
    }
    return SEQ_DUR * fallbackRatio;
  }

  const tKi = Math.max(2.3, Math.min(SEQ_DUR * 0.36, findPhraseTime(['thủ', 'kiềm'], 0.28)));
  const tPh = Math.max(tKi + 2.0, Math.min(SEQ_DUR * 0.52, findPhraseTime(['mất', 'ph'], 0.42)));
  const tLk = Math.max(tPh + 1.8, Math.min(SEQ_DUR * 0.66, findPhraseTime(['khi', 'hàng', 'lợi'], 0.52)));
  const tDn = Math.max(tLk + 2.2, Math.min(SEQ_DUR * 0.84, findPhraseTime(['hãy', 'dịu', 'chuẩn'], 0.72)));
  const tEt = Math.max(tDn + 1.6, Math.min(SEQ_DUR - 1.5, findPhraseTime(['êm', 'thoáng'], 0.87)));

  const PUSH_KF = [
    { t: 0.00,       y: 90  },
    { t: 1.95,       y: 90  },
    { t: 2.38,       y: 268 },
    { t: tKi - 0.30, y: 268 },
    { t: tKi + 0.22, y: 355 },
    { t: tPh - 0.22, y: 355 },
    { t: tPh + 0.22, y: 270 },
    { t: tLk - 0.18, y: 270 },
    { t: tLk + 0.38, y: 28  },
    { t: tDn - 0.32, y: 28  },
    { t: tDn + 0.22, y: 350 },
    { t: tEt - 0.20, y: 350 },
    { t: tEt + 0.26, y: 268 },
    { t: SEQ_DUR + 0.5, y: 268 }
  ];
  function getPushY(t) {
    for (let i = 0; i < PUSH_KF.length - 1; i++) {
      const a = PUSH_KF[i], b = PUSH_KF[i + 1];
      if (t >= a.t && t <= b.t) return lerp(a.y, b.y, minJerk((t - a.t) / Math.max(0.001, b.t - a.t)));
    }
    return 268;
  }

  // Preload face filmstrips & B-Roll images
  const faceImgs = [];
  for (let i = 0; i < 20; i++) {
    const imF = new Image();
    imF.src = `assets/thumbs_face/face_${String(i).padStart(2, '0')}.jpg`;
    faceImgs.push(imF);
  }

  const brollDefs = [
    { key: 'pk01', src: 'assets/broll_pk01.jpg', binName: 'Card_01_NiemMac.png', badge: '⚠ TRIỆU CHỨNG', badgeCol: '#E11D48', title: 'NIÊM MẠC KÍCH ỨNG', prompt: 'Tạo ảnh y khoa 9:16: niêm mạc nhạy cảm hồng nhạt bị kích ứng ẩm ngứa...' },
    { key: 'pk02', src: 'assets/broll_pk02.jpg', binName: 'Card_02_KiemManh.png', badge: '✕ THỦ PHẠM',      badgeCol: '#D97706', title: 'DUNG DỊCH KIỀM MẠNH', prompt: 'Tạo ảnh 9:16: bọt xà phòng kiềm mạnh làm khô rát bề mặt cánh hoa cúc...' },
    { key: 'pk03', src: 'assets/broll_pk03.jpg', binName: 'Card_03_ChuanPH.png',  badge: '💧 ĐỘ pH CHUẨN', badgeCol: '#0284C7', title: 'CÂN BẰNG pH 3.8 – 4.5', prompt: 'Tạo ảnh giọt tinh chất cân bằng độ pH 3.8 - 4.5 trong trẻo chuẩn y khoa...' },
    { key: 'pk04', src: 'assets/broll_pk04.jpg', binName: 'Card_04_LoiKhuan.png', badge: '🛡 LỢI KHUẨN',   badgeCol: '#7C3AED', title: 'HÀNG RÀO LỢI KHUẨN', prompt: 'Tạo ảnh 3D lợi khuẩn Lactobacillus đan vòm bảo vệ niêm mạc khỏe mạnh...' },
    { key: 'pk05', src: 'assets/broll_pk05.jpg', binName: 'Card_05_EmThoang.png', badge: '✓ CHĂM SÓC',     badgeCol: '#059669', title: 'ÊM THOÁNG MỖI NGÀY', prompt: 'Tạo ảnh phụ nữ Việt Nam áo trắng rạng rỡ tự tin bên nắng sớm hoa cúc...' }
  ];
  const bImgs = {};
  for (const d of brollDefs) {
    const im = new Image();
    im.src = d.src;
    bImgs[d.key] = im;
  }

  // Exact Viewport inside CapCut `Trình phát: Dòng thời gian 01`
  const vpEl = document.getElementById('cc-viewport-wrap');
  const vpRect = vpEl.getBoundingClientRect();
  const VP_X = vpRect.left || 441;
  const VP_Y = vpRect.top  || 996;
  const VP_W = vpRect.width  || 248;
  const VP_H = vpRect.height || 441;
  const mapX = (x1080) => VP_X + (x1080 / 1080) * VP_W;
  const mapY = (y1920) => VP_Y + (y1920 / 1920) * VP_H;
  const mapW = (w1080) => (w1080 / 1080) * VP_W;
  const mapH = (h1920) => (h1920 / 1920) * VP_H;

  function pushOutOfFaceZone(x, y) {
    if (x > VP_X + 38 && x < VP_X + VP_W - 38 && y > VP_Y + 42 && y < VP_Y + VP_H - 95) {
      return { x: x < VP_X + VP_W * 0.5 ? VP_X + 22 : VP_X + VP_W - 22, y };
    }
    return { x, y };
  }

  // ==================== 1. BELOVED 261127 OVERLAPPING & Z-JUMPING TOP LAYOUTS (ZERO FLOW!) ====================
  const TOP_LAYOUTS = [
    // 0.0..2.4s: Photoshop Front-Left + Illustrator Front-Right + ChatGPT Bottom-Left + CMS Bottom-Right
    { focus: 'ps', dock: 'dk-ps', atIdx: 0, rects: {
      ps:    { x: 10,  y: 36,  w: 612, h: 444, z: 32, s: 1.00 },
      ai:    { x: 548, y: 38,  w: 522, h: 404, z: 28, s: 0.99 },
      gpt:   { x: 12,  y: 462, w: 534, h: 442, z: 26, s: 0.99 },
      cms:   { x: 552, y: 454, w: 518, h: 448, z: 24, s: 0.98 },
      ide:   { x: 210, y: 230, w: 515, h: 380, z: 14, s: 0.94 },
      swarm: { x: 525, y: 225, w: 505, h: 385, z: 15, s: 0.94 }
    }},
    // 2.4..5.6s: ChatGPT Jumps Top-Left + Photoshop Front-Center-Right slicing 3-Card Volley + IDE & Swarm Bottom!
    { focus: 'gpt', dock: 'dk-gpt', atIdx: 1, rects: {
      gpt:   { x: 10,  y: 36,  w: 538, h: 438, z: 33, s: 1.01 },
      ps:    { x: 468, y: 36,  w: 602, h: 446, z: 31, s: 1.00 },
      ide:   { x: 12,  y: 466, w: 536, h: 436, z: 26, s: 0.99 },
      swarm: { x: 554, y: 464, w: 516, h: 438, z: 28, s: 0.99 },
      ai:    { x: 520, y: 185, w: 510, h: 390, z: 16, s: 0.95 },
      cms:   { x: 80,  y: 235, w: 510, h: 410, z: 15, s: 0.94 }
    }},
    // 5.6..9.4s: Photoshop Spotlight Front-Left + Illustrator Vector KeyText Front-Right + CMS + Swarm!
    { focus: 'ai', dock: 'dk-ai', atIdx: 2, rects: {
      ps:    { x: 12,  y: 36,  w: 616, h: 446, z: 31, s: 1.00 },
      ai:    { x: 536, y: 36,  w: 534, h: 418, z: 34, s: 1.01 },
      cms:   { x: 12,  y: 466, w: 530, h: 436, z: 27, s: 0.99 },
      gpt:   { x: 548, y: 460, w: 522, h: 442, z: 29, s: 1.00 },
      ide:   { x: 220, y: 225, w: 515, h: 385, z: 15, s: 0.94 },
      swarm: { x: 520, y: 220, w: 505, h: 385, z: 16, s: 0.95 }
    }},
    // 9.4..13.2s: Auto-Web CMS Jumps Top-Left + Illustrator Top-Right + IDE & ChatGPT Bottom!
    { focus: 'cms', dock: 'dk-cms', atIdx: 3, rects: {
      cms:   { x: 10,  y: 36,  w: 544, h: 438, z: 33, s: 1.01 },
      ai:    { x: 548, y: 38,  w: 522, h: 412, z: 30, s: 1.00 },
      ps:    { x: 12,  y: 460, w: 586, h: 444, z: 31, s: 1.00 },
      swarm: { x: 562, y: 462, w: 508, h: 440, z: 29, s: 0.99 },
      gpt:   { x: 480, y: 210, w: 515, h: 405, z: 16, s: 0.95 },
      ide:   { x: 60,  y: 225, w: 510, h: 385, z: 15, s: 0.94 }
    }},
    // 13.2..18.5s: Photoshop + Illustrator + ChatGPT + 120-Agent Swarm Final Waterfall Volley!
    { focus: 'ps', dock: 'dk-sw', atIdx: 4, rects: {
      ps:    { x: 10,  y: 36,  w: 614, h: 446, z: 34, s: 1.01 },
      ai:    { x: 544, y: 38,  w: 526, h: 410, z: 31, s: 1.00 },
      gpt:   { x: 12,  y: 464, w: 534, h: 438, z: 29, s: 0.99 },
      swarm: { x: 552, y: 460, w: 518, h: 442, z: 32, s: 1.01 },
      cms:   { x: 60,  y: 230, w: 510, h: 410, z: 16, s: 0.95 },
      ide:   { x: 490, y: 220, w: 510, h: 385, z: 15, s: 0.94 }
    }}
  ];
  const WIN_IDS = ['ps', 'ai', 'gpt', 'cms', 'ide', 'swarm'];

  function getLayoutAt(t) {
    const idx = t < 2.4 ? 0 : t < 5.6 ? 1 : t < 9.4 ? 2 : t < 13.2 ? 3 : 4;
    const starts = [0, 2.4, 5.6, 9.4, 13.2];
    const dt = t - starts[idx];
    const L0 = TOP_LAYOUTS[idx];
    const prevL = TOP_LAYOUTS[Math.max(0, idx - 1)];
    const s = minJerk(Math.min(1, dt / 0.28));
    const rects = {};
    for (const k of WIN_IDS) {
      const a = prevL.rects[k], b = L0.rects[k];
      rects[k] = {
        x: lerp(a.x, b.x, s), y: lerp(a.y, b.y, s),
        w: lerp(a.w, b.w, s), h: lerp(a.h, b.h, s),
        z: b.z, sc: lerp(a.s, b.s, s)
      };
    }
    return { focus: L0.focus, dock: L0.dock, atIdx: L0.atIdx, rects, showAltTab: idx > 0 && dt < 0.24 };
  }

  function winCenter(t, winKey, rxRatio, ryRatio) {
    const r = getLayoutAt(t).rects[winKey];
    return { x: r.x + r.w * rxRatio, y: r.y + r.h * ryRatio };
  }

  // ==================== 2. DIRECT CURVED-ARC THROW SCHEDULE (261127 SIGNATURE!) ====================
  // Every single visual element in `talking_head_stage.html` is pre-created up top in ChatGPT/Photoshop/Illustrator
  // and THROWN DIRECTLY DOWN along a glowing cyan curved trajectory into CapCut's `Trình phát` + `Tệp phương tiện` + `Timeline`!
  const BIN_IMPORT_SCHEDULE = [
    { bIdx: 0, key: 'pk01', name: 'Card_01_NiemMac.png', tThrow0: 0.04, tImported: 0.24, tAdded: 0.36, srcWin: 'ps' },
    { bIdx: 1, key: 'pk02', name: 'Card_02_KiemManh.png', tThrow0: 0.12, tImported: 0.34, tAdded: 0.46, srcWin: 'gpt' },
    { bIdx: 2, key: 'pk03', name: 'Card_03_ChuanPH.png',  tThrow0: tKi - 0.52, tImported: tKi - 0.14, tAdded: tKi + 0.08, srcWin: 'ps' },
    { bIdx: 3, key: 'pk04', name: 'Card_04_LoiKhuan.png', tThrow0: tLk - 0.48, tImported: tLk - 0.10, tAdded: tLk + 0.12, srcWin: 'ps' },
    { bIdx: 4, key: 'pk05', name: 'Card_05_EmThoang.png', tThrow0: tDn - 0.48, tImported: tDn - 0.10, tAdded: tDn + 0.08, srcWin: 'ps' }
  ];

  // Screen centers of sequential slots in CapCut `Tệp phương tiện` (`#cc-left-cvs` offset x=78, y=990)
  function binSlotScreenPt(visIdx) {
    const col = visIdx % 2, row = Math.floor(visIdx / 2);
    return { x: 78 + 10 + col * 122 + 57, y: 990 + 54 + row * 96 + 36 };
  }

  const THROW_EVENTS = [
    // --- BEAT 1 [0.18s .. 0.38s]: Hook Banner + Dual Shoulder Cards Thrown Straight Into `Trình phát`! ---
    { kind: 'hook', text: 'VỆ SINH KỸ MÀ VẪN ẨM NGỨA?', t0: 0.02, tLand: 0.20, srcWin: 'ai', rx: 0.50, ry: 0.72, dx: mapX(62), dy: mapY(1310), dw: mapW(816), dh: mapH(175), arcX: 120, agent: 'Ai-Hook', color: '#F59E0B', tlTrack: 'T1', sEnd: 2.26, tlLbl: 'Hook_AmNgua_3s' },
    { kind: 'card', bIdx: 0, t0: 0.05, tLand: 0.28, srcWin: 'ps',  rx: 0.42, ry: 0.52, dx: mapX(78),  dy: mapY(415), dw: mapW(286), dh: mapH(365), arcX: -95, agent: 'Ps-Cutout', color: '#2563EB', tlTrack: 'V2', sEnd: 2.26, tlLbl: 'Card_01_NiemMac.png' },
    { kind: 'card', bIdx: 1, t0: 0.14, tLand: 0.38, srcWin: 'gpt', rx: 0.45, ry: 0.55, dx: mapX(716), dy: mapY(415), dw: mapW(286), dh: mapH(365), arcX: 95,  agent: 'GPT-Source', color: '#10B981', tlTrack: 'V3', sEnd: 2.26, tlLbl: 'Card_02_KiemManh.png' },

    // --- KEY TEXT #1 [2.32s]: Thrown from Illustrator Behind Presenter's Hair Crown! ---
    { kind: 'key', text: 'VẪN ẨM NGỨA QUAY LẠI?', t0: 1.90, tLand: 2.32, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(120), dy: mapY(260), dw: mapW(840), dh: mapH(185), arcX: 110, agent: 'Ai-KeyText', color: '#EC4899', tlTrack: 'T2', sEnd: tKi - 0.14, tlLbl: 'KeyText_01_AmNgua' },

    // --- BEAT 2 [tKi]: 3-CARD RAPID-FIRE FAN VOLLEY ("bam-bam-bam!" Top-to-Bottom like 261127's 5-Icon Volley!) ---
    { kind: 'card', bIdx: 0, t0: tKi - 0.50, tLand: tKi - 0.10, srcWin: 'ps',  rx: 0.38, ry: 0.52, dx: mapX(84),  dy: mapY(286), dw: mapW(292), dh: mapH(378), arcX: -90, agent: 'Ps-Layer1', color: '#0284C7', tlTrack: 'V2', sEnd: tPh - 0.04, tlLbl: 'Fan_01_NiemMac.png' },
    { kind: 'card', bIdx: 2, t0: tKi - 0.38, tLand: tKi + 0.02, srcWin: 'gpt', rx: 0.45, ry: 0.54, dx: mapX(704), dy: mapY(286), dw: mapW(292), dh: mapH(378), arcX: 115, agent: 'GPT-pH45',  color: '#0EA5E9', tlTrack: 'V3', sEnd: tPh - 0.04, tlLbl: 'Card_03_ChuanPH.png' },
    { kind: 'card', bIdx: 1, t0: tKi - 0.26, tLand: tKi + 0.14, srcWin: 'ps',  rx: 0.48, ry: 0.52, dx: mapX(362), dy: mapY(264), dw: mapW(356), dh: mapH(405), arcX: 35,  agent: 'Ps-Hero',   color: '#D97706', tlTrack: null, sEnd: tPh - 0.04, tlLbl: 'Hero_02_KiemManh.png' },

    // --- BEAT 3 + KEY TEXT #2 [tPh]: Thrown from Illustrator & Photoshop Simultaneously! ---
    { kind: 'key',  text: 'MẤT ĐỘ pH TỰ NHIÊN!', t0: tPh - 0.42, tLand: tPh, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(120), dy: mapY(260), dw: mapW(840), dh: mapH(185), arcX: 115, agent: 'Ai-KeyText', color: '#8B5CF6', tlTrack: 'T2', sEnd: tLk - 0.08, tlLbl: 'KeyText_02_MatPH' },
    { kind: 'card', bIdx: 1, t0: tPh - 0.34, tLand: tPh + 0.06, srcWin: 'ps', rx: 0.40, ry: 0.52, dx: mapX(78),  dy: mapY(465), dw: mapW(282), dh: mapH(355), arcX: -85, agent: 'Ps-Cutout', color: '#D97706', tlTrack: 'V2', sEnd: tLk - 0.06, tlLbl: 'Card_02_Left.png' },
    { kind: 'card', bIdx: 2, t0: tPh - 0.22, tLand: tPh + 0.16, srcWin: 'ps', rx: 0.50, ry: 0.52, dx: mapX(720), dy: mapY(465), dw: mapW(282), dh: mapH(355), arcX: 105, agent: 'Ps-Layer',  color: '#0284C7', tlTrack: 'V3', sEnd: tLk - 0.06, tlLbl: 'Card_03_Right.png' },

    // --- BEAT 4 [tLk]: Model Pulled Up + Dual Lợi Khuẩn Cards Thrown Down! ---
    { kind: 'card', bIdx: 0, t0: tLk - 0.40, tLand: tLk + 0.02, srcWin: 'ps',  rx: 0.42, ry: 0.54, dx: mapX(76),  dy: mapY(385), dw: mapW(286), dh: mapH(368), arcX: -85, agent: 'Ps-Cutout', color: '#E11D48', tlTrack: 'V2', sEnd: tDn - 0.06, tlLbl: 'Card_01_Shoulder.png' },
    { kind: 'card', bIdx: 3, t0: tLk - 0.28, tLand: tLk + 0.14, srcWin: 'ps',  rx: 0.48, ry: 0.54, dx: mapX(718), dy: mapY(375), dw: mapW(286), dh: mapH(368), arcX: 110, agent: 'Ps-3DCard', color: '#7C3AED', tlTrack: 'V3', sEnd: tDn - 0.06, tlLbl: 'Card_04_LoiKhuan.png' },

    // --- BEAT 5 [tDn]: 3-CARD WATERFALL VOLLEY ("bam-bam-bam!" into Live View!) ---
    { kind: 'card', bIdx: 3, t0: tDn - 0.46, tLand: tDn - 0.04, srcWin: 'ps',  rx: 0.40, ry: 0.52, dx: mapX(84),  dy: mapY(286), dw: mapW(292), dh: mapH(378), arcX: -95, agent: 'Ps-Deck1',  color: '#7C3AED', tlTrack: 'V2', sEnd: tEt - 0.04, tlLbl: 'Waterfall_04.png' },
    { kind: 'card', bIdx: 4, t0: tDn - 0.34, tLand: tDn + 0.08, srcWin: 'gpt', rx: 0.45, ry: 0.55, dx: mapX(704), dy: mapY(286), dw: mapW(292), dh: mapH(378), arcX: 115, agent: 'GPT-Care',  color: '#059669', tlTrack: 'V3', sEnd: tEt - 0.04, tlLbl: 'Card_05_EmThoang.png' },
    { kind: 'card', bIdx: 2, t0: tDn - 0.22, tLand: tDn + 0.20, srcWin: 'ps',  rx: 0.48, ry: 0.52, dx: mapX(362), dy: mapY(264), dw: mapW(356), dh: mapH(405), arcX: 30,  agent: 'Ps-Hero',   color: '#0284C7', tlTrack: null, sEnd: tEt - 0.04, tlLbl: 'Hero_03_ChuanPH.png' },

    // --- BEAT 6 + CLOSING KEY TEXT #3 [tEt]: Final Radiant Volley! ---
    { kind: 'key',  text: 'ÊM THOÁNG TỰ TIN NGAY!', t0: tEt - 0.42, tLand: tEt, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(120), dy: mapY(260), dw: mapW(840), dh: mapH(185), arcX: 115, agent: 'Ai-KeyText', color: '#10B981', tlTrack: 'T2', sEnd: SEQ_DUR, tlLbl: 'KeyText_03_EmThoang' },
    { kind: 'card', bIdx: 3, t0: tEt - 0.32, tLand: tEt + 0.08, srcWin: 'ps', rx: 0.42, ry: 0.52, dx: mapX(78),  dy: mapY(470), dw: mapW(282), dh: mapH(352), arcX: -85, agent: 'Ps-FinalL', color: '#7C3AED', tlTrack: 'V2', sEnd: SEQ_DUR, tlLbl: 'Card_04_End.png' },
    { kind: 'card', bIdx: 4, t0: tEt - 0.20, tLand: tEt + 0.18, srcWin: 'ps', rx: 0.48, ry: 0.52, dx: mapX(720), dy: mapY(470), dw: mapW(282), dh: mapH(352), arcX: 105, agent: 'Ps-FinalR', color: '#059669', tlTrack: 'V3', sEnd: SEQ_DUR, tlLbl: 'Card_05_End.png' }
  ];

  // Add every Whisper Subtitle Pill thrown from Illustrator (`#win-ai`) straight into `Trình phát` & Track T1!
  const subChunks = [];
  if (words.length > 0) {
    let cur = [];
    for (let i = 0; i < words.length; i++) {
      cur.push(words[i]);
      const span = cur[cur.length - 1].e - cur[0].s;
      const punct = /[?.!,;:]$/.test(words[i].w);
      if (cur.length >= 5 || (cur.length >= 4 && (span >= 1.45 || punct)) || i === words.length - 1) {
        subChunks.push({ s: cur[0].s, e: cur[cur.length - 1].e + 0.14, text: cur.map(x => x.w).join(' ') });
        cur = [];
      }
    }
  }
  subChunks.forEach((sc, idx) => {
    if (sc.s < 2.26) return;
    const inKT = THROW_EVENTS.some(kt => kt.kind === 'key' && sc.s >= kt.tLand - 0.1 && sc.s <= kt.sEnd - 0.2);
    if (inKT) return;
    THROW_EVENTS.push({
      kind: 'sub', text: sc.text,
      t0: Math.max(0.3, sc.s - 0.38), tLand: sc.s,
      srcWin: 'ai', rx: 0.50, ry: 0.72,
      dx: mapX(62), dy: mapY(1348), dw: mapW(816), dh: mapH(86),
      arcX: 155, agent: 'Sub-Whisper', color: '#DB2777',
      tlTrack: 'T1', sEnd: sc.e, tlLbl: `Sub_0${idx + 1}_${sc.text.slice(0, 10)}`
    });
  });

  const KEYFRAME_TIMES = [2.38, tKi + 0.22, tLk + 0.38, tDn + 0.22, tEt + 0.26];
  const SFX_BLOCKS = [0.24, 0.38, 2.32, tKi - 0.10, tKi + 0.14, tPh, tLk + 0.14, tDn - 0.04, tDn + 0.20, tEt];

  // ==================== 3. 120 PURPOSEFUL AGENTS (60 TASK CURSORS + 60 ESCORT/THROWER SWARM) ====================
  const NAMED_BADGES = [
    { label: 'Ps-Cutout',   color: '#2563EB', role: 'psCanvas' },
    { label: 'Ps-Curves',   color: '#0891B2', role: 'psLayers' },
    { label: 'ChatGPT-4o',  color: '#10A37F', role: 'gptGen'   },
    { label: 'Ai-Vector',   color: '#EA580C', role: 'aiArt'    },
    { label: 'Sub-Whisper', color: '#DB2777', role: 'aiArt'    },
    { label: 'CMS-Auto',    color: '#059669', role: 'cmsWeb'   },
    { label: 'TikTok-Reels',color: '#E11D48', role: 'cmsWeb'   },
    { label: 'Bin-Loader',  color: '#0284C7', role: 'binToTl'  },
    { label: 'CC-Keyframe', color: '#7C3AED', role: 'ccInsp'   },
    { label: 'CC-ColorHSL', color: '#D97706', role: 'ccWheels' },
    { label: 'CC-Timeline', color: '#0D9488', role: 'tlAhead'  },
    { label: 'LUFS-14dB',   color: '#10B981', role: 'tlAudio'  }
  ];

  function pickTaskPt(role, t, rng) {
    const ls = getLayoutAt(t).rects;
    const aheadMin = Math.min(SEQ_DUR - 0.4, Math.max(0.1, t - 0.2));
    const aheadMax = Math.min(SEQ_DUR - 0.08, t + 3.4);
    const tx = () => secToX(aheadMin + rng() * Math.max(0.25, aheadMax - aheadMin));

    let visSlots = 2;
    for (const bi of BIN_IMPORT_SCHEDULE) if (t >= bi.tImported) visSlots++;

    if (role === 'psCanvas') {
      return { x: ls.ps.x + 36 + rng() * (ls.ps.w - 195), y: ls.ps.y + 52 + rng() * (ls.ps.h - 70), c: rng() < 0.5 ? 'cross' : 'ew-resize', dx: (rng()-0.5)*34, dy: 0 };
    }
    if (role === 'psLayers') {
      return { x: ls.ps.x + ls.ps.w - 140 + rng() * 125, y: ls.ps.y + 65 + Math.floor(rng() * 6) * 28, c: 'arrow', dx: 0, dy: 0 };
    }
    if (role === 'gptGen') {
      return { x: ls.gpt.x + 25 + rng() * (ls.gpt.w - 50), y: ls.gpt.y + 45 + rng() * (ls.gpt.h - 65), c: rng() < 0.4 ? 'ibeam' : 'arrow', dx: 20, dy: 0 };
    }
    if (role === 'aiArt') {
      return { x: ls.ai.x + 30 + rng() * (ls.ai.w - 60), y: ls.ai.y + 45 + rng() * (ls.ai.h - 60), c: rng() < 0.45 ? 'cross' : 'ibeam', dx: (rng()-0.5)*28, dy: 0 };
    }
    if (role === 'cmsWeb') {
      return { x: ls.cms.x + 25 + rng() * (ls.cms.w - 50), y: ls.cms.y + 55 + rng() * (ls.cms.h - 70), c: rng() < 0.35 ? 'ibeam' : 'arrow', dx: 18, dy: 0 };
    }
    if (role === 'ideSwarm') {
      const w = rng() < 0.5 ? ls.ide : ls.swarm;
      return { x: w.x + 25 + rng() * (w.w - 50), y: w.y + 45 + rng() * (w.h - 60), c: 'arrow', dx: 16, dy: 0 };
    }
    if (role === 'ccRibbon') {
      return { x: 30 + Math.floor(rng() * 7) * 44, y: 968, c: 'arrow', dx: 0, dy: 0 };
    }
    if (role === 'binToTl') {
      if (rng() < 0.48) {
        const pt = binSlotScreenPt(Math.floor(rng() * visSlots));
        return { x: pt.x + (rng()-0.5)*36, y: pt.y + (rng()-0.5)*22, c: 'arrow', dx: 0, dy: 0, carry: true };
      }
      return { x: tx(), y: 1605 + rng() * 95, c: 'arrow', dx: 18, dy: 0, carry: true };
    }
    if (role === 'ccInsp') {
      return { x: 815 + rng() * 235, y: 960 + rng() * 240, c: 'ew-resize', dx: (rng()-0.5)*46, dy: 0 };
    }
    if (role === 'ccWheels') {
      return { x: 810 + rng() * 245, y: 1180 + rng() * 245, c: 'cross', dx: (rng()-0.5)*30, dy: (rng()-0.5)*20 };
    }
    if (role === 'tlAudio') {
      return { x: tx(), y: 1775 + rng() * 70, c: 'ew-resize', dx: (rng()-0.5)*32, dy: 0, mq: rng() < 0.2 };
    }
    // tlAhead: Building Timeline tracks right ahead of Playhead!
    return { x: tx(), y: 1538 + rng() * 215, c: rng() < 0.55 ? 'ew-resize' : 'arrow', dx: 36 + rng()*55, dy: 18 + rng()*24, mq: rng() < 0.25 };
  }

  const ROLE_POOL = [
    'psCanvas','psCanvas','psCanvas','psLayers','psLayers',
    'gptGen','gptGen','gptGen',
    'aiArt','aiArt','aiArt',
    'cmsWeb','cmsWeb','ideSwarm','ideSwarm',
    'ccRibbon','binToTl','binToTl','binToTl',
    'ccInsp','ccInsp','ccInsp','ccWheels','ccWheels',
    'tlAhead','tlAhead','tlAhead','tlAhead','tlAhead','tlAhead','tlAudio','tlAudio'
  ];

  // Group 1: 60 Task Cursors
  const TASK_CURSORS = [];
  for (let i = 0; i < 60; i++) {
    const rng = mulberry32(7717 + i * 6311);
    const spec = i < NAMED_BADGES.length ? NAMED_BADGES[i] : null;
    const role = spec ? spec.role : ROLE_POOL[i % ROLE_POOL.length];
    const wps = [];
    let f = -Math.floor(rng() * 20);
    let prev = pickTaskPt(role, 0, rng);
    while (f < TOTAL_FRAMES + 60) {
      const curT = Math.max(0, f / FPS);
      const nxt = pickTaskPt(role, curT, rng);
      const mDur = Math.floor(10 + rng() * 12);
      const hDur = Math.floor(6 + rng() * 9);
      wps.push({
        f0: f, f1: f + mDur, f2: f + mDur + hDur,
        x0: prev.x, y0: prev.y, x1: nxt.x, y1: nxt.y,
        arc: (rng() - 0.5) * 34,
        ctype: nxt.c,
        dx: nxt.dx || 0, dy: nxt.dy || 0,
        isMq: Boolean(nxt.mq && nxt.y > 1520),
        carry: Boolean(nxt.carry && nxt.y > 1500),
        carryKey: brollDefs[i % 5].key
      });
      f += mDur + hDur;
      prev = nxt;
    }
    TASK_CURSORS.push({
      badge: spec ? { label: spec.label, color: spec.color } : null,
      scale: 0.86 + (i % 3) * 0.06,
      wps
    });
  }

  // Group 2: 60 Escort / Swarm Cursors ("60 con chạy bên cạnh con chuột chính" — surging along every Top->Bottom Throw & Timeline Action!)
  function getHeroTrajectory(t) {
    // Whenever an active B-Roll Card or KeyText Throw is flying in mid-air, the Main Hero Cursor + 60 Escort SwarmRIDE THAT EXACT THROW DOWN!
    const activeThrow = THROW_EVENTS.find(ev => (ev.kind === 'card' || ev.kind === 'key' || ev.kind === 'hook') && t >= ev.t0 && t <= ev.tLand);
    if (activeThrow) {
      const u = minJerk((t - activeThrow.t0) / Math.max(0.05, activeThrow.tLand - activeThrow.t0));
      const sp = winCenter(activeThrow.t0, activeThrow.srcWin, activeThrow.rx, activeThrow.ry);
      const inv = 1 - u;
      const mx = (sp.x + activeThrow.dx) * 0.5 + activeThrow.arcX;
      const my = (sp.y + activeThrow.dy) * 0.46;
      const x = inv * inv * sp.x + 2 * inv * u * mx + u * u * (activeThrow.dx + activeThrow.dw * 0.35);
      const y = inv * inv * sp.y + 2 * inv * u * my + u * u * (activeThrow.dy + activeThrow.dh * 0.25);
      const safe = pushOutOfFaceZone(x, y);
      return { x: safe.x, y: safe.y, clicking: u > 0.85 };
    }
    if (t >= SEQ_DUR - 0.58) {
      return { x: 968, y: 930, clicking: true }; // Final `⇥ Xuất` button!
    }
    // Between throws: surge dynamically between Photoshop Canvas -> CapCut `Tệp phương tiện` -> CapCut Timeline Playhead -> Inspector!
    const cycle = (t * 2.1) % 4;
    const pts = [
      winCenter(t, 'ps', 0.45, 0.52),
      binSlotScreenPt(Math.min(6, Math.floor(t / 2.6))),
      { x: secToX(Math.min(SEQ_DUR - 0.3, t + 0.6)), y: 1655 },
      { x: 895, y: 1140 + Math.sin(t * 4) * 90 }
    ];
    const i0 = Math.floor(cycle), i1 = (i0 + 1) % 4;
    const u = fastEase(cycle - i0);
    const x = lerp(pts[i0].x, pts[i1].x, u);
    const y = lerp(pts[i0].y, pts[i1].y, u);
    const safe = pushOutOfFaceZone(x, y);
    return { x: safe.x, y: safe.y, clicking: (cycle - i0) > 0.82 };
  }

  const ESCORT_SWARM = [];
  for (let i = 0; i < 60; i++) {
    const rng = mulberry32(9901 + i * 4999);
    const ring = Math.floor(i / 12);
    const angle = (i % 12) * (Math.PI * 2 / 12) + ring * 0.28 + (rng() - 0.5) * 0.22;
    const dist = 18 + ring * 14 + rng() * 10;
    ESCORT_SWARM.push({
      lag: 0.012 + ring * 0.022 + rng() * 0.028,
      angle,
      dist,
      wFreq: 5.5 + rng() * 6.0,
      wPhase: rng() * Math.PI * 2,
      scale: 0.74 + rng() * 0.14
    });
  }

  // ==================== 4. CANVAS CONTEXTS & HELPERS ====================
  const psCtx   = document.getElementById('ps-cvs').getContext('2d');
  const aiCtx   = document.getElementById('ai-cvs').getContext('2d');
  const gptCtx  = document.getElementById('gpt-cvs').getContext('2d');
  const leftCtx = document.getElementById('cc-left-cvs').getContext('2d');
  const inspCtx = document.getElementById('cc-insp-cvs').getContext('2d');
  const tlCtx   = document.getElementById('tl-canvas').getContext('2d');
  const fxCtx   = document.getElementById('fx-canvas').getContext('2d');

  function drawFramedCard(ctx, x, y, w, h, def, alpha = 1.0) {
    const im = bImgs[def.key];
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = '#0F172A';
    ctx.beginPath(); ctx.roundRect(x, y, w, h, Math.max(5, w * 0.06)); ctx.fill();
    ctx.save();
    ctx.beginPath(); ctx.roundRect(x, y, w, h, Math.max(5, w * 0.06)); ctx.clip();
    if (im && im.complete && im.naturalWidth > 0) ctx.drawImage(im, x, y, w, h);
    const g = ctx.createLinearGradient(0, y, 0, y + h * 0.54);
    g.addColorStop(0, 'rgba(8,12,24,0.92)'); g.addColorStop(1, 'rgba(8,12,24,0)');
    ctx.fillStyle = g; ctx.fillRect(x, y, w, h * 0.54);

    const fsB = Math.max(6, w * 0.052);
    ctx.font = `800 ${fsB.toFixed(1)}px "MontserratBlack", "Segoe UI"`;
    const bw = Math.min(w * 0.88, ctx.measureText(def.badge).width + fsB * 1.4);
    ctx.fillStyle = def.badgeCol;
    ctx.beginPath(); ctx.roundRect(x + w * 0.06, y + h * 0.05, bw, fsB * 1.65, fsB); ctx.fill();
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(def.badge, x + w * 0.06 + fsB * 0.65, y + h * 0.05 + fsB * 1.2);

    let fsT = Math.max(7, w * 0.076);
    ctx.font = `900 ${fsT.toFixed(1)}px "MontserratBlack", "Segoe UI"`;
    while (ctx.measureText(def.title).width > w * 0.88 && fsT > 6) {
      fsT -= 0.4;
      ctx.font = `900 ${fsT.toFixed(1)}px "MontserratBlack", "Segoe UI"`;
    }
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(def.title, x + w * 0.06, y + h * 0.24);
    ctx.restore();
    ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = Math.max(1.5, w * 0.013);
    ctx.beginPath(); ctx.roundRect(x, y, w, h, Math.max(5, w * 0.06)); ctx.stroke();
    ctx.restore();
  }

  // 4A. Photoshop 2026 (`#win-ps` — Exact Beloved 261127 Transparency Checkerboard + Marching Ants + Curves HUD!)
  function drawPhotoshop(f, t) {
    const W = 430, H = 390;
    psCtx.fillStyle = '#191A1E'; psCtx.fillRect(0, 0, W, H);
    // Checkerboard
    psCtx.fillStyle = '#24262C';
    for (let y = 16; y < H - 42; y += 14) {
      for (let x = 22; x < W - 22; x += 14) {
        if ((Math.floor(x / 14) + Math.floor(y / 14)) % 2 === 0) psCtx.fillRect(x, y, 14, 14);
      }
    }

    // Show the EXACT next/current B-Roll Card being cut out right before throwing down!
    const nextCardEv = THROW_EVENTS.find(e => e.kind === 'card' && t <= e.tLand + 0.15) || THROW_EVENTS.filter(e => e.kind === 'card').slice(-1)[0];
    const bIdx = nextCardEv ? nextCardEv.bIdx : 0;
    const def = brollDefs[bIdx];

    for (let k = 0; k < 6; k++) {
      document.getElementById(`psl-${k}`).className = (k === bIdx) ? 'ps-lyr sel' : 'ps-lyr';
    }

    const cw = 216, ch = 282, cx = (W - cw) * 0.46, cy = 26;
    drawFramedCard(psCtx, cx, cy, cw, ch, def, 1.0);

    // Photoshop #31A8FF Transform Handles + Animated Marching Ants!
    psCtx.strokeStyle = '#31A8FF'; psCtx.lineWidth = 1.6;
    psCtx.strokeRect(cx - 5, cy - 5, cw + 10, ch + 10);
    [[cx-5,cy-5],[cx+cw+5,cy-5],[cx-5,cy+ch+5],[cx+cw+5,cy+ch+5],[cx+cw*0.5,cy-5],[cx+cw*0.5,cy+ch+5]].forEach(([hx, hy]) => {
      psCtx.fillStyle = '#FFFFFF'; psCtx.fillRect(hx - 3.5, hy - 3.5, 7, 7);
      psCtx.strokeStyle = '#31A8FF'; psCtx.strokeRect(hx - 3.5, hy - 3.5, 7, 7);
    });

    psCtx.save();
    psCtx.setLineDash([5, 5]); psCtx.lineDashOffset = -(f * 1.2);
    psCtx.strokeStyle = '#FFFFFF'; psCtx.lineWidth = 1.3;
    psCtx.strokeRect(cx + 6, cy + 6, cw - 12, ch - 12);
    psCtx.restore();

    // Top-right Curves HUD (Exact 261127 look!)
    const gx = W - 96, gy = 12, gw = 84, gh = 84;
    psCtx.fillStyle = 'rgba(20, 22, 28, 0.92)'; psCtx.fillRect(gx, gy, gw, gh);
    psCtx.strokeStyle = '#475569'; psCtx.strokeRect(gx, gy, gw, gh);
    psCtx.strokeStyle = '#38BDF8'; psCtx.lineWidth = 2;
    const bend = Math.sin(t * 5) * 10;
    psCtx.beginPath(); psCtx.moveTo(gx + 6, gy + gh - 6);
    psCtx.bezierCurveTo(gx + 26, gy + gh - 14 + bend, gx + 56, gy + 14 - bend, gx + gw - 6, gy + 6);
    psCtx.stroke();

    // Bottom Action Bar (`Tách Layer -> Ném xuống CapCut ✓`)
    psCtx.fillStyle = '#2563EB';
    psCtx.beginPath(); psCtx.roundRect(74, H - 36, 206, 24, 5); psCtx.fill();
    psCtx.fillStyle = '#FFFFFF'; psCtx.font = '700 9px "Segoe UI"';
    psCtx.fillText('Tách Layer ➔ Gắp xuống CapCut ✓', 88, H - 20);

    psCtx.fillStyle = '#27272A';
    psCtx.beginPath(); psCtx.roundRect(288, H - 36, 78, 24, 5); psCtx.fill();
    psCtx.fillStyle = '#E4E4E7'; psCtx.fillText('Curves 98%', 299, H - 20);
  }

  // 4B. Illustrator 2026 (`#win-ai` — Live KeyText & Subtitle Vector Thrower!)
  function drawIllustrator(t) {
    const W = 510, H = 380;
    aiCtx.fillStyle = '#16171C'; aiCtx.fillRect(0, 0, W, H);
    const ax = 20, ay = 16, aw = W - 40, ah = H - 32;
    aiCtx.fillStyle = '#0F1420'; aiCtx.fillRect(ax, ay, aw, ah);
    aiCtx.strokeStyle = '#F59E0B'; aiCtx.lineWidth = 1.3; aiCtx.strokeRect(ax, ay, aw, ah);

    // Top Vector KeyText Artboard
    const keyList = THROW_EVENTS.filter(e => e.kind === 'key');
    const curKT = keyList.find(e => t <= e.sEnd) || keyList[keyList.length - 1];
    const parts = curKT.text.split(' ');
    const mid = Math.ceil(parts.length / 2);
    const l1 = parts.slice(0, mid).join(' ');
    const l2 = parts.slice(mid).join(' ');

    const cx = ax + aw * 0.5;
    // Rotating gold vector handles ring behind KeyText (261127 signature!)
    const rad = 64 + Math.sin(t * 3.2) * 3;
    aiCtx.strokeStyle = 'rgba(245, 158, 11, 0.55)'; aiCtx.lineWidth = 2;
    aiCtx.beginPath(); aiCtx.arc(cx, ay + 105, rad, 0, Math.PI * 2); aiCtx.stroke();
    for (let k = 0; k < 8; k++) {
      const a = (k / 8) * Math.PI * 2 + t * 0.5;
      aiCtx.fillStyle = '#FFFFFF';
      aiCtx.fillRect(cx + Math.cos(a) * rad - 3, ay + 105 + Math.sin(a) * rad - 3, 6, 6);
    }

    aiCtx.save();
    aiCtx.textAlign = 'center';
    aiCtx.font = '900 28px "MontserratBlack", "Segoe UI"';
    aiCtx.strokeStyle = '#060913'; aiCtx.lineWidth = 7;
    aiCtx.strokeText(l1, cx, ay + 96); aiCtx.strokeText(l2, cx, ay + 134);
    const gr = aiCtx.createLinearGradient(cx - 140, 0, cx + 140, 0);
    gr.addColorStop(0, '#FFF1F2'); gr.addColorStop(0.48, '#FB7185'); gr.addColorStop(1, '#FDE047');
    aiCtx.fillStyle = gr;
    aiCtx.fillText(l1, cx, ay + 96); aiCtx.fillText(l2, cx, ay + 134);
    aiCtx.restore();

    // Bottom Live Subtitle Pill Vector Ready to Throw Down!
    const subList = THROW_EVENTS.filter(e => e.kind === 'sub' || e.kind === 'hook');
    const curSub = subList.find(e => t <= e.tLand + 0.35) || subList[subList.length - 1];
    const px = cx - 190, py = ay + 216, pw = 380, ph = 50;
    aiCtx.fillStyle = '#FFFFFF';
    aiCtx.beginPath(); aiCtx.roundRect(px, py, pw, ph, 25); aiCtx.fill();
    aiCtx.strokeStyle = '#00E5FF'; aiCtx.lineWidth = 2.4; aiCtx.stroke();
    aiCtx.fillStyle = '#0F172A';
    aiCtx.font = '800 14.5px "BeVietnamExtraBold", "Segoe UI"';
    aiCtx.textAlign = 'center';
    aiCtx.fillText(curSub.text.slice(0, 34), cx, py + 30);

    aiCtx.fillStyle = '#67E8F9'; aiCtx.font = '700 9.5px Consolas';
    aiCtx.fillText('⚡ LIVE VECTOR KEYTEXT & SUBTITLE ➔ NÉM XUỐNG CAPCUT', cx, py + 74);
    aiCtx.textAlign = 'left';
  }

  // 4C. ChatGPT Plus (`#win-gpt` — Creates Raw B-Roll Source Images First!)
  function drawChatGpt(t, f) {
    const W = 520, H = 390;
    gptCtx.fillStyle = '#212121'; gptCtx.fillRect(0, 0, W, H);
    gptCtx.fillStyle = '#171717'; gptCtx.fillRect(0, 0, 112, H);
    gptCtx.fillStyle = '#ECECEC'; gptCtx.font = '700 9.5px "Segoe UI"';
    gptCtx.fillText('◎ Dự án Phụ Khoa', 8, 22);

    const activeB = Math.min(4, Math.floor((t / SEQ_DUR) * 5));
    brollDefs.forEach((d, idx) => {
      const done = idx <= activeB;
      gptCtx.fillStyle = idx === activeB ? '#2F2F2F' : 'transparent';
      gptCtx.beginPath(); gptCtx.roundRect(5, 34 + idx * 27, 102, 23, 5); gptCtx.fill();
      gptCtx.fillStyle = done ? '#34D399' : '#9CA3AF'; gptCtx.font = '8.2px "Segoe UI"';
      gptCtx.fillText(`${done ? '✓' : '⟳'} Card_0${idx + 1}`, 11, 49 + idx * 27);
    });

    const def = brollDefs[activeB];
    const genU = clamp01(((t * 1.45) % 1.0) * 1.35);

    // Word-wrapped Prompt Bubble
    gptCtx.fillStyle = '#2F2F2F';
    gptCtx.beginPath(); gptCtx.roundRect(156, 10, 350, 40, 12); gptCtx.fill();
    gptCtx.fillStyle = '#ECECEC'; gptCtx.font = '8.8px "Segoe UI"';
    let l1 = '', l2 = '';
    for (const w of def.prompt.split(' ')) {
      if ((l1 + ' ' + w).trim().length <= 52 && !l2) l1 = (l1 + ' ' + w).trim();
      else l2 = (l2 + ' ' + w).trim();
    }
    gptCtx.fillText(l1, 168, 26); gptCtx.fillText(l2, 168, 40);

    gptCtx.fillStyle = '#34D399'; gptCtx.font = '700 9px "Segoe UI"';
    gptCtx.fillText(`✦ ChatGPT 4o đã tạo Source ${def.binName} ➔ Gắp sang Photoshop & CapCut`, 124, 68);

    // Active Generated Image + 4 Ready Source Thumbnails
    const ix = 124, iy = 78, iw = 182, ih = 236;
    gptCtx.save();
    gptCtx.beginPath(); gptCtx.roundRect(ix, iy, iw, ih, 10); gptCtx.clip();
    const im = bImgs[def.key];
    if (im && im.complete && im.naturalWidth > 0) {
      const bl = (1 - genU) * 12;
      gptCtx.filter = bl > 0.4 ? `blur(${bl.toFixed(1)}px)` : 'none';
      gptCtx.drawImage(im, ix, iy, iw, ih);
      gptCtx.filter = 'none';
    }
    gptCtx.restore();
    gptCtx.strokeStyle = '#10B981'; gptCtx.lineWidth = 1.6;
    gptCtx.beginPath(); gptCtx.roundRect(ix, iy, iw, ih, 10); gptCtx.stroke();

    for (let k = 0; k < 4; k++) {
      const bi = (activeB + k + 1) % 5;
      const gx = 318 + (k % 2) * 96, gy = 78 + Math.floor(k / 2) * 120;
      const gim = bImgs[brollDefs[bi].key];
      gptCtx.save();
      gptCtx.beginPath(); gptCtx.roundRect(gx, gy, 88, 112, 7); gptCtx.clip();
      if (gim && gim.complete && gim.naturalWidth > 0) gptCtx.drawImage(gim, gx, gy, 88, 112);
      gptCtx.restore();
      gptCtx.strokeStyle = '#3F3F46'; gptCtx.beginPath(); gptCtx.roundRect(gx, gy, 88, 112, 7); gptCtx.stroke();
    }

    // Bottom Composer
    const nextP = brollDefs[(activeB + 1) % 5].prompt;
    const typed = Math.floor((t * 52) % (nextP.length + 10));
    gptCtx.fillStyle = '#2F2F2F';
    gptCtx.beginPath(); gptCtx.roundRect(124, 324, 384, 52, 14); gptCtx.fill();
    gptCtx.fillStyle = '#ECECEC'; gptCtx.font = '8.8px "Segoe UI"';
    gptCtx.fillText(nextP.slice(0, typed) + (f % 20 < 10 ? '▌' : ''), 136, 344);
    gptCtx.fillStyle = '#93C5FD'; gptCtx.font = '600 8px "Segoe UI"';
    gptCtx.fillText('🎨 Tạo hình ảnh 9:16   ·   ⚡ Tự động gắp xuống CapCut', 136, 365);
  }

  // ==================== 5. VIETNAMESE CAPCUT LEFT PANE (`Tệp phương tiện` PROGRESSIVE IMPORT — ZERO GAP, ZERO BLOCKING POPUP!) ====================
  function drawCapCutLeftPane(t) {
    const W = 258, H = 490;
    leftCtx.fillStyle = '#1B1C20'; leftCtx.fillRect(0, 0, W, H);

    const anyImporting = BIN_IMPORT_SCHEDULE.some(bi => t >= bi.tThrow0 && t <= bi.tImported);
    leftCtx.fillStyle = anyImporting ? '#00D4D8' : '#262830';
    leftCtx.beginPath(); leftCtx.roundRect(10, 8, 56, 21, 4); leftCtx.fill();
    leftCtx.fillStyle = anyImporting ? '#041E22' : '#00E5E5'; leftCtx.font = '700 8.5px "Segoe UI"';
    leftCtx.fillText('⊕ Nhập', 17, 22);

    leftCtx.fillStyle = '#262830';
    leftCtx.beginPath(); leftCtx.roundRect(70, 8, 42, 21, 4); leftCtx.fill();
    leftCtx.fillStyle = '#D1D5DB'; leftCtx.font = '8px "Segoe UI"';
    leftCtx.fillText('📹 Ghi', 76, 22);

    leftCtx.fillStyle = '#141519';
    leftCtx.beginPath(); leftCtx.roundRect(116, 8, 132, 21, 4); leftCtx.fill();
    leftCtx.fillStyle = '#6B7280'; leftCtx.font = '7.8px "Segoe UI"';
    leftCtx.fillText('🔍 Tìm kiếm tệp...', 122, 22);

    const baseTiles = [
      { name: 'khach_talk_master.mp4', img: faceImgs[2], tIn: 0.0, tAdded: 0.05 },
      { name: 'presenter_cutout.webm', img: faceImgs[8], tIn: 0.001, tAdded: 0.05 }
    ];
    for (const bi of BIN_IMPORT_SCHEDULE) {
      baseTiles.push({ name: bi.name, img: bImgs[bi.key], tIn: bi.tImported, tAdded: bi.tAdded });
    }

    const visTiles = baseTiles.filter(ti => t >= ti.tIn).sort((a, b) => a.tIn - b.tIn);
    leftCtx.fillStyle = '#D1D5DB'; leftCtx.font = '700 8.6px "Segoe UI"';
    leftCtx.fillText(`Tất cả (${visTiles.length})`, 10, 45);

    visTiles.forEach((ti, visIdx) => {
      const col = visIdx % 2, row = Math.floor(visIdx / 2);
      const x = 10 + col * 122, y = 54 + row * 96, w = 114, h = 72;
      const age = t - ti.tIn;
      const justLanded = ti.tIn > 0.01 && age < 0.48;

      leftCtx.save();
      if (ti.tIn > 0.01 && age < 0.18) {
        const sc = lerp(0.72, 1.04, fastEase(age / 0.18));
        leftCtx.translate(x + w * 0.5, y + h * 0.5);
        leftCtx.scale(sc, sc);
        leftCtx.translate(-(x + w * 0.5), -(y + h * 0.5));
      }

      leftCtx.fillStyle = '#121317';
      leftCtx.beginPath(); leftCtx.roundRect(x, y, w, h, 5); leftCtx.fill();
      if (ti.img && ti.img.complete && ti.img.naturalWidth > 0) {
        leftCtx.save();
        leftCtx.beginPath(); leftCtx.roundRect(x + 2, y + 2, w - 4, h - 4, 4); leftCtx.clip();
        const iw = ti.img.naturalWidth, ih = ti.img.naturalHeight;
        const scale = Math.max(w / iw, h / ih);
        leftCtx.drawImage(ti.img, x + (w - iw * scale) * 0.5, y, iw * scale, ih * scale);
        leftCtx.restore();
      }

      leftCtx.fillStyle = t >= ti.tAdded ? 'rgba(18, 20, 24, 0.85)' : 'rgba(0, 229, 255, 0.92)';
      leftCtx.beginPath(); leftCtx.roundRect(x + 5, y + 5, t >= ti.tAdded ? 40 : 46, 14, 3); leftCtx.fill();
      leftCtx.fillStyle = t >= ti.tAdded ? '#E5E7EB' : '#041E22';
      leftCtx.font = '700 7.2px "Segoe UI"';
      leftCtx.fillText(t >= ti.tAdded ? 'Đã thêm' : 'Mới thả', x + 8, y + 14.5);

      leftCtx.fillStyle = '#00D4D8';
      leftCtx.beginPath(); leftCtx.roundRect(x + w - 18, y + h - 18, 14, 14, 3); leftCtx.fill();
      leftCtx.fillStyle = '#041E22'; leftCtx.font = '900 10.5px "Segoe UI"';
      leftCtx.fillText('+', x + w - 14.5, y + h - 7.5);

      if (justLanded) {
        leftCtx.strokeStyle = '#00E5FF'; leftCtx.lineWidth = 2.0;
        leftCtx.beginPath(); leftCtx.roundRect(x, y, w, h, 5); leftCtx.stroke();
      }

      leftCtx.fillStyle = '#9CA3AF'; leftCtx.font = '7.8px "Segoe UI"';
      leftCtx.fillText(ti.name.slice(0, 19), x + 2, y + h + 13);
      leftCtx.restore();
    });

    // Dropzone slot at next empty grid cell showing incoming throw target!
    if (visTiles.length < 8) {
      const col = visTiles.length % 2, row = Math.floor(visTiles.length / 2);
      const dx = 10 + col * 122, dy = 54 + row * 96;
      leftCtx.strokeStyle = anyImporting ? '#00E5FF' : '#323644';
      leftCtx.lineWidth = 1.4; leftCtx.setLineDash([4, 3]);
      leftCtx.beginPath(); leftCtx.roundRect(dx, dy, 114, 72, 5); leftCtx.stroke();
      leftCtx.setLineDash([]);
      leftCtx.fillStyle = anyImporting ? '#00E5FF' : '#7C8190';
      leftCtx.font = '600 7.8px "Segoe UI"'; leftCtx.textAlign = 'center';
      leftCtx.fillText(anyImporting ? '⬇ Đang thả B-Roll...' : '+ Thả tệp vào đây', dx + 57, dy + 40);
      leftCtx.textAlign = 'left';
    }

    leftCtx.fillStyle = '#16181E'; leftCtx.fillRect(0, H - 30, W, 30);
    leftCtx.fillStyle = '#00E5E5'; leftCtx.font = '600 7.8px "Segoe UI"';
    leftCtx.fillText('✦ Công cụ cắt clip bằng AI', 8, H - 11);
    leftCtx.fillStyle = '#00D4D8';
    leftCtx.beginPath(); leftCtx.roundRect(W - 80, H - 23, 72, 17, 4); leftCtx.fill();
    leftCtx.fillStyle = '#041E22'; leftCtx.font = '700 7.4px "Segoe UI"';
    leftCtx.fillText('Bắt đầu cắt clip', W - 75, H - 12);
  }

  // ==================== 6. RAPIDLY CYCLING VIETNAMESE CAPCUT INSPECTOR ====================
  function drawCapCutInspector(t, pushY) {
    const W = 294, H = 506;
    inspCtx.fillStyle = '#1B1C20'; inspCtx.fillRect(0, 0, W, H);

    const modeIdx = Math.floor(t / 0.72) % 5;
    const topMain = (modeIdx === 0) ? 0 : (modeIdx === 1) ? 1 : 2;
    for (let k = 0; k < 4; k++) document.getElementById(`imt-${k}`).className = (k === topMain) ? 'insp-m-tab on' : 'insp-m-tab';

    function subBar(names, onIdx) {
      inspCtx.fillStyle = '#16171B'; inspCtx.fillRect(0, 0, W, 26);
      const sw = (W - 16) / names.length;
      names.forEach((nm, idx) => {
        const x = 8 + idx * sw;
        if (idx === onIdx) {
          inspCtx.fillStyle = '#2A2C35';
          inspCtx.beginPath(); inspCtx.roundRect(x, 4, sw - 4, 18, 4); inspCtx.fill();
        }
        inspCtx.fillStyle = idx === onIdx ? '#FFFFFF' : '#8E93A2';
        inspCtx.font = idx === onIdx ? '700 8px "Segoe UI"' : '8px "Segoe UI"';
        inspCtx.textAlign = 'center';
        inspCtx.fillText(nm, x + (sw - 4) * 0.5, 16);
      });
      inspCtx.textAlign = 'left';
    }

    if (modeIdx === 0) {
      subBar(['Cơ bản', 'Xóa nền', 'Mặt nạ', 'Làm mịn'], 0);
      inspCtx.fillStyle = '#E5E7EB'; inspCtx.font = '700 8.8px "Segoe UI"'; inspCtx.fillText('▾ Biến đổi & Keyframe', 12, 44);
      const sliders = [
        { lbl: 'Tỷ lệ', u: 0.52 + Math.sin(t * 5) * 0.12, val: `${100 + Math.round(Math.sin(t * 5) * 4)}%` },
        { lbl: 'Xoay', u: 0.50 + Math.cos(t * 4) * 0.14, val: `${(Math.cos(t * 4) * 4).toFixed(1)}°` },
        { lbl: 'Độ mờ', u: 0.98, val: '100%' }
      ];
      sliders.forEach((s, idx) => {
        const y = 62 + idx * 32;
        inspCtx.fillStyle = '#9CA3AF'; inspCtx.font = '8.2px "Segoe UI"'; inspCtx.fillText(s.lbl, 12, y + 4);
        inspCtx.fillStyle = '#2C2F3A'; inspCtx.fillRect(72, y, 146, 3);
        inspCtx.fillStyle = '#00D4D8'; inspCtx.fillRect(72, y, 146 * s.u, 3);
        inspCtx.fillStyle = '#FFFFFF'; inspCtx.beginPath(); inspCtx.arc(72 + 146 * s.u, y + 1.5, 4.5, 0, Math.PI * 2); inspCtx.fill();
        inspCtx.fillStyle = '#252730'; inspCtx.beginPath(); inspCtx.roundRect(226, y - 7, 44, 17, 3); inspCtx.fill();
        inspCtx.fillStyle = '#E5E7EB'; inspCtx.font = '8px Consolas'; inspCtx.fillText(s.val, 233, y + 4);
      });
      inspCtx.fillStyle = '#252730';
      inspCtx.beginPath(); inspCtx.roundRect(72, 156, 88, 19, 3); inspCtx.fill();
      inspCtx.beginPath(); inspCtx.roundRect(168, 156, 98, 19, 3); inspCtx.fill();
      inspCtx.fillStyle = '#00E5E5'; inspCtx.font = '700 8.2px Consolas';
      inspCtx.fillText('X     0', 80, 169); inspCtx.fillText(`Y  -${Math.round(pushY)} ◆`, 176, 169);

      inspCtx.fillStyle = '#242731'; inspCtx.beginPath(); inspCtx.roundRect(12, 190, W - 24, 58, 6); inspCtx.fill();
      inspCtx.fillStyle = '#00E5E5'; inspCtx.font = '700 8.6px "Segoe UI"';
      inspCtx.fillText('☑ Tự động xóa nền (RVM Hair Alpha)', 20, 209);
      inspCtx.fillStyle = '#00E5E5'; inspCtx.fillRect(20, 220, W - 40, 7);
      inspCtx.fillStyle = '#9CA3AF'; inspCtx.font = '7.8px "Segoe UI"';
      inspCtx.fillText('Đã khóa chủ thể · Thẻ B-Roll xếp sau lưng', 20, 239);

      inspCtx.fillStyle = '#131419'; inspCtx.beginPath(); inspCtx.roundRect(12, 262, W - 24, 156, 6); inspCtx.fill();
      inspCtx.fillStyle = '#D1D5DB'; inspCtx.font = '700 8px "Segoe UI"';
      inspCtx.fillText('Đồ thị Keyframe · Vị trí Y (Đẩy mẫu / Kéo lên)', 20, 280);
      inspCtx.strokeStyle = '#00E5E5'; inspCtx.lineWidth = 2;
      inspCtx.beginPath();
      for (let x = 0; x <= W - 44; x += 3) {
        const s = (x / (W - 44)) * SEQ_DUR;
        const y = 398 - (getPushY(s) / 380) * 96;
        if (x === 0) inspCtx.moveTo(22 + x, y); else inspCtx.lineTo(22 + x, y);
      }
      inspCtx.stroke();
      const curX = 22 + (t / SEQ_DUR) * (W - 44);
      inspCtx.strokeStyle = '#FFFFFF'; inspCtx.beginPath(); inspCtx.moveTo(curX, 290); inspCtx.lineTo(curX, 408); inspCtx.stroke();
      return;
    }

    if (modeIdx === 1) {
      subBar(['Vào', 'Ra', 'Kết hợp'], Math.floor(t * 3) % 3);
      const anims = ['Không có','Lắc phải','Lắc xuống','Nhập mờ','Phóng to','Trượt lên','Lật sách','Rơi đàn hồi','Xoay 3D','Tia sáng','Thu phóng','Băng tan','Lắc 2','Màn trập','Đàn hồi','Rung nhẹ','Trượt ngang','Xoáy ốc','Bật nảy','Mở nét'];
      const selIdx = 1 + (Math.floor(t * 7) % (anims.length - 1));
      anims.forEach((nm, idx) => {
        const col = idx % 5, row = Math.floor(idx / 5);
        const x = 10 + col * 55, y = 40 + row * 82;
        inspCtx.fillStyle = '#262830'; inspCtx.beginPath(); inspCtx.roundRect(x, y, 49, 54, 6); inspCtx.fill();
        inspCtx.fillStyle = idx === selIdx ? 'rgba(0,229,229,0.22)' : '#1D1F26';
        inspCtx.beginPath(); inspCtx.roundRect(x + 6, y + 6, 37, 42, 4); inspCtx.fill();
        inspCtx.fillStyle = idx === selIdx ? '#00E5E5' : '#6B7280';
        inspCtx.font = '700 11px "Segoe UI"'; inspCtx.textAlign = 'center';
        inspCtx.fillText(idx === 0 ? '⊘' : '✦', x + 24.5, y + 31);
        if (idx === selIdx) {
          inspCtx.strokeStyle = '#00E5E5'; inspCtx.lineWidth = 2;
          inspCtx.beginPath(); inspCtx.roundRect(x, y, 49, 54, 6); inspCtx.stroke();
        }
        inspCtx.fillStyle = idx === selIdx ? '#00E5E5' : '#9CA3AF';
        inspCtx.font = '7.2px "Segoe UI"'; inspCtx.fillText(nm.slice(0, 9), x + 24.5, y + 68);
      });
      inspCtx.textAlign = 'left';
      return;
    }

    if (modeIdx === 2) {
      subBar(['Cơ bản', 'HSL', 'Đường cong', 'Vòng tròn màu'], 0);
      inspCtx.fillStyle = '#00E5E5'; inspCtx.font = '700 8.5px "Segoe UI"';
      inspCtx.fillText('● LUT  ·  CleanSkin_Studio.cube', 12, 46);
      [
        { nm: 'Nhiệt độ màu', c1: '#3B82F6', c2: '#FACC15', off: Math.sin(t * 6) * 0.18 },
        { nm: 'Tông màu',     c1: '#22C55E', c2: '#EC4899', off: Math.cos(t * 5) * 0.14 },
        { nm: 'Độ bão hòa',   c1: '#6B7280', c2: '#EF4444', off: 0.12 + Math.sin(t * 7) * 0.10 },
        { nm: 'Phơi sáng',    c1: '#2B2E38', c2: '#E5E7EB', off: 0.08 + Math.cos(t * 6) * 0.08 },
        { nm: 'Tương phản',   c1: '#2B2E38', c2: '#E5E7EB', off: 0.15 + Math.sin(t * 5) * 0.09 },
        { nm: 'Độ sắc nét',   c1: '#2B2E38', c2: '#00E5E5', off: 0.24 }
      ].forEach((r, idx) => {
        const y = 76 + idx * 58;
        inspCtx.fillStyle = '#D1D5DB'; inspCtx.font = '8px "Segoe UI"'; inspCtx.fillText(r.nm, 12, y);
        const lg = inspCtx.createLinearGradient(12, 0, 224, 0);
        lg.addColorStop(0, r.c1); lg.addColorStop(1, r.c2);
        inspCtx.fillStyle = lg; inspCtx.fillRect(12, y + 10, 212, 3.5);
        inspCtx.fillStyle = '#FFFFFF'; inspCtx.beginPath(); inspCtx.arc(118 + r.off * 180, y + 11.7, 5, 0, Math.PI * 2); inspCtx.fill();
        inspCtx.fillStyle = '#252730'; inspCtx.beginPath(); inspCtx.roundRect(234, y + 2, 46, 18, 3); inspCtx.fill();
        inspCtx.fillStyle = '#E5E7EB'; inspCtx.font = '8px Consolas';
        const iv = Math.round(r.off * 40);
        inspCtx.fillText((iv >= 0 ? '+' : '') + iv, 246, y + 14);
      });
      return;
    }

    if (modeIdx === 3) {
      subBar(['Cơ bản', 'HSL', 'Đường cong', 'Vòng tròn màu'], 3);
      ['#EF4444','#F97316','#EAB308','#22C55E','#06B6D4','#3B82F6','#8B5CF6','#EC4899'].forEach((col, idx) => {
        const cx = 24 + idx * 34, cy = 48, act = idx === (Math.floor(t * 8) % 8);
        inspCtx.strokeStyle = col; inspCtx.lineWidth = act ? 3.2 : 2;
        inspCtx.beginPath(); inspCtx.arc(cx, cy, act ? 9.5 : 7.5, 0, Math.PI * 2); inspCtx.stroke();
      });
      [{ nm: 'Vùng tối', x: 78, y: 162 }, { nm: 'Xám trung tính', x: 214, y: 162 }, { nm: 'Tông màu', x: 78, y: 312 }, { nm: 'Offset', x: 214, y: 312 }].forEach((w, idx) => {
        inspCtx.fillStyle = '#D1D5DB'; inspCtx.font = '600 8px "Segoe UI"'; inspCtx.textAlign = 'center';
        inspCtx.fillText(w.nm, w.x, w.y - 52);
        for (let a = 0; a < 36; a++) {
          inspCtx.strokeStyle = `hsl(${a * 10}, 85%, 55%)`; inspCtx.lineWidth = 6;
          inspCtx.beginPath(); inspCtx.arc(w.x, w.y, 40, (a/36)*Math.PI*2, ((a+1.2)/36)*Math.PI*2); inspCtx.stroke();
        }
        inspCtx.fillStyle = '#141519'; inspCtx.beginPath(); inspCtx.arc(w.x, w.y, 35, 0, Math.PI * 2); inspCtx.fill();
        const px = w.x + Math.cos(t * 5 + idx * 1.7) * 11, py = w.y + Math.sin(t * 6 + idx * 1.3) * 11;
        inspCtx.strokeStyle = '#FFFFFF'; inspCtx.lineWidth = 1.6; inspCtx.beginPath(); inspCtx.arc(px, py, 4.5, 0, Math.PI * 2); inspCtx.stroke();
      });
      inspCtx.textAlign = 'left';
      return;
    }

    subBar(['Cơ bản', 'HSL', 'Đường cong', 'Vòng tròn màu'], 2);
    [{ nm: '● Độ sáng (Luma)', col: '#FFFFFF', y0: 56, bend: Math.sin(t * 6) * 22 }, { nm: '● Red / Cyan', col: '#EF4444', y0: 266, bend: Math.cos(t * 5) * 20 }].forEach((cv) => {
      inspCtx.fillStyle = '#D1D5DB'; inspCtx.font = '700 8px "Segoe UI"'; inspCtx.fillText(cv.nm, 14, cv.y0 - 8);
      const gx = 14, gy = cv.y0, gw = W - 28, gh = 176;
      inspCtx.fillStyle = '#111216'; inspCtx.fillRect(gx, gy, gw, gh);
      inspCtx.strokeStyle = '#232630'; inspCtx.strokeRect(gx, gy, gw, gh);
      inspCtx.strokeStyle = cv.col; inspCtx.lineWidth = 2;
      inspCtx.beginPath(); inspCtx.moveTo(gx, gy + gh);
      const c1x = gx + gw * 0.32, c1y = gy + gh * 0.68 + cv.bend;
      const c2x = gx + gw * 0.68, c2y = gy + gh * 0.30 - cv.bend;
      inspCtx.bezierCurveTo(c1x, c1y, c2x, c2y, gx + gw, gy); inspCtx.stroke();
      [[c1x, c1y], [c2x, c2y]].forEach(([nx, ny]) => { inspCtx.fillStyle = '#FFFFFF'; inspCtx.beginPath(); inspCtx.arc(nx, ny, 4.5, 0, Math.PI * 2); inspCtx.fill(); });
    });
  }

  // ==================== 7. CAPCUT TIMELINE BUILDING AHEAD OF PLAYHEAD (261127 BULLET-TRAIN STYLE!) ====================
  function drawCapCutTimeline(t, marquees) {
    const W = 1080, H = 410;
    tlCtx.fillStyle = '#15161A'; tlCtx.fillRect(0, 0, W, H);

    tlCtx.fillStyle = '#18191E'; tlCtx.fillRect(0, 0, W, 22);
    tlCtx.font = '8.8px Consolas, monospace'; tlCtx.fillStyle = '#6B7280';
    for (let s = 0; s <= Math.ceil(SEQ_DUR); s += 2) {
      const sx = secToX(s);
      tlCtx.strokeStyle = '#2E313D'; tlCtx.beginPath(); tlCtx.moveTo(sx, 14); tlCtx.lineTo(sx, 22); tlCtx.stroke();
      tlCtx.fillText(`00:${String(s).padStart(2, '0')}`, sx - 13, 11);
    }

    const rows = [
      { ico: 'T',  y: 26,  h: 26 },
      { ico: 'T',  y: 55,  h: 26 },
      { ico: '⧉',  y: 85,  h: 34 },
      { ico: '🖼', y: 123, h: 36 },
      { ico: '🖼', y: 162, h: 36 },
      { ico: '🎞', y: 204, h: 56, main: true },
      { ico: '🎵', y: 266, h: 44 },
      { ico: '🎵', y: 314, h: 32 }
    ];
    rows.forEach((r) => {
      tlCtx.fillStyle = r.main ? '#1C1E26' : '#16171C'; tlCtx.fillRect(HDR_W, r.y, W - HDR_W, r.h);
      tlCtx.fillStyle = '#191A20'; tlCtx.fillRect(0, r.y, HDR_W - 1, r.h);
      tlCtx.fillStyle = '#8A8F9E'; tlCtx.font = '9.5px "Segoe UI"'; tlCtx.fillText(r.ico, 10, r.y + r.h * 0.64);
      tlCtx.fillStyle = '#585D6B'; tlCtx.font = '8px "Segoe UI"'; tlCtx.fillText('👁', 30, r.y + r.h * 0.64);
    });

    const v1X = secToX(0);
    const v1BuiltSec = Math.min(SEQ_DUR, t + 3.6);
    const v1W = Math.max(36, secToX(v1BuiltSec) - v1X);
    let builtClips = 2;

    // Main Video Track (Extends smoothly ahead of playhead!)
    tlCtx.save();
    tlCtx.beginPath(); tlCtx.roundRect(v1X, 206, v1W, 52, 4); tlCtx.clip();
    tlCtx.fillStyle = '#123C42'; tlCtx.fillRect(v1X, 206, v1W, 52);
    const cellW = (secToX(SEQ_DUR) - v1X) / 20;
    for (let i = 0; i < 20; i++) {
      const fim = faceImgs[i];
      if (fim && fim.complete && fim.naturalWidth > 0) tlCtx.drawImage(fim, v1X + i * cellW, 219, cellW + 0.8, 39);
    }
    tlCtx.fillStyle = '#165B63'; tlCtx.fillRect(v1X, 206, v1W, 13);
    tlCtx.fillStyle = '#E6FFFA'; tlCtx.font = '600 7.8px "Segoe UI"';
    tlCtx.fillText('khach_talk_master.mp4   00:00:18:27', v1X + 6, 215.5);
    tlCtx.restore();
    tlCtx.strokeStyle = '#67E8F9'; tlCtx.lineWidth = 1.6;
    tlCtx.beginPath(); tlCtx.roundRect(v1X, 206, v1W, 52, 4); tlCtx.stroke();

    // RVM Cutout Track + Keyframes ◆
    tlCtx.save();
    tlCtx.beginPath(); tlCtx.roundRect(v1X, 87, v1W, 30, 4); tlCtx.clip();
    tlCtx.fillStyle = '#252936'; tlCtx.fillRect(v1X, 87, v1W, 30);
    for (let i = 0; i < 20; i++) {
      const fim = faceImgs[i];
      if (fim && fim.complete && fim.naturalWidth > 0) {
        tlCtx.globalAlpha = 0.55;
        tlCtx.drawImage(fim, v1X + i * cellW, 87, cellW + 0.8, 30);
      }
    }
    tlCtx.globalAlpha = 1.0;
    tlCtx.fillStyle = 'rgba(14,16,22,0.78)'; tlCtx.fillRect(v1X, 87, 175, 13);
    tlCtx.fillStyle = '#00E5E5'; tlCtx.font = '600 7.5px "Segoe UI"';
    tlCtx.fillText('✂ presenter_cutout.webm (Xóa nền)', v1X + 5, 96.5);
    tlCtx.restore();

    KEYFRAME_TIMES.forEach((kt) => {
      if (t + 0.35 >= kt) {
        const kx = secToX(kt);
        tlCtx.save(); tlCtx.translate(kx, 108); tlCtx.rotate(Math.PI / 4);
        tlCtx.fillStyle = '#FFFFFF'; tlCtx.fillRect(-3.4, -3.4, 6.8, 6.8);
        tlCtx.strokeStyle = '#00E5E5'; tlCtx.strokeRect(-3.4, -3.4, 6.8, 6.8);
        tlCtx.restore();
      }
    });

    // Thrown B-Roll Cards & Text Clips Snap onto CapCut Tracks RIGHT ON `tLand`!
    for (const ev of THROW_EVENTS) {
      if (!ev.tlTrack || t < ev.tLand - 0.04) continue;
      builtClips++;
      const growU = minJerk((t - (ev.tLand - 0.04)) / 0.28);
      const curEnd = lerp(ev.tLand + 0.35, ev.sEnd, growU);
      const x = secToX(ev.tLand), w = Math.max(12, secToX(curEnd) - x);

      if (ev.tlTrack === 'V2' || ev.tlTrack === 'V3') {
        const ry = ev.tlTrack === 'V2' ? 125 : 164;
        tlCtx.save();
        tlCtx.beginPath(); tlCtx.roundRect(x, ry, w, 32, 4); tlCtx.clip();
        tlCtx.fillStyle = '#232734'; tlCtx.fillRect(x, ry, w, 32);
        const im = bImgs[brollDefs[ev.bIdx || 0].key];
        if (im && im.complete && im.naturalWidth > 0) {
          for (let tx = x; tx < x + w; tx += 32) tlCtx.drawImage(im, tx, ry, 32, 32);
        }
        tlCtx.fillStyle = 'rgba(0,0,0,0.65)'; tlCtx.fillRect(x, ry, w, 12);
        tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = '600 7.4px "Segoe UI"';
        tlCtx.fillText(ev.tlLbl, x + 4, ry + 9.5);
        tlCtx.restore();
        if (t >= ev.tLand && t <= ev.tLand + 1.4) {
          tlCtx.strokeStyle = '#FFFFFF'; tlCtx.lineWidth = 1.8;
          tlCtx.beginPath(); tlCtx.roundRect(x, ry, w, 32, 4); tlCtx.stroke();
        }
      } else {
        const ry = ev.tlTrack === 'T2' ? 27 : 56;
        tlCtx.fillStyle = ev.tlTrack === 'T2' ? '#A45D28' : '#8B4932';
        tlCtx.beginPath(); tlCtx.roundRect(x, ry, w, 23, 4); tlCtx.fill();
        if (t >= ev.tLand && t <= ev.sEnd) {
          tlCtx.strokeStyle = '#FFFFFF'; tlCtx.lineWidth = 1.3;
          tlCtx.beginPath(); tlCtx.roundRect(x, ry, w, 23, 4); tlCtx.stroke();
        }
        if (w > 22) {
          tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x + 4, ry, w - 8, 23); tlCtx.clip();
          tlCtx.fillStyle = '#FEF3C7'; tlCtx.font = '7.5px "Segoe UI"';
          tlCtx.fillText(ev.text || ev.tlLbl, x + 5, ry + 14.5);
          tlCtx.restore();
        }
      }
    }

    // Voiceover Waveform
    tlCtx.save();
    tlCtx.beginPath(); tlCtx.roundRect(v1X, 268, v1W, 40, 4); tlCtx.clip();
    tlCtx.fillStyle = '#164B47'; tlCtx.fillRect(v1X, 268, v1W, 40);
    const wf = meta.waveform || [];
    const fullW = secToX(SEQ_DUR) - v1X;
    const bStep = fullW / Math.max(1, wf.length);
    for (let b = 0; b < wf.length; b++) {
      const bx = v1X + b * bStep;
      if (bx > v1X + v1W - 2) break;
      const bh = Math.max(2, wf[b] * 26);
      tlCtx.fillStyle = '#38E2D2';
      tlCtx.fillRect(bx, 291 - bh * 0.5, Math.max(1.4, bStep - 0.8), bh);
    }
    tlCtx.fillStyle = '#CCFBF1'; tlCtx.font = '7.5px "Segoe UI"';
    tlCtx.fillText('🎵 voice_khach_clean_14lufs.wav', v1X + 5, 278);
    tlCtx.restore();

    // SFX Blocks
    SFX_BLOCKS.forEach((st, idx) => {
      if (t + 0.25 < st) return;
      const sx = secToX(st);
      tlCtx.fillStyle = idx % 2 === 0 ? '#0D9488' : '#D97706';
      tlCtx.beginPath(); tlCtx.roundRect(sx, 316, 36, 26, 4); tlCtx.fill();
      tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = '7px Consolas';
      tlCtx.fillText(idx % 2 === 0 ? 'Whoosh' : 'Pop', sx + 4, 332);
    });

    // Active Cyan Marquee Selection Boxes (261127 signature!)
    for (const mq of marquees) {
      const rx = Math.min(mq.x0, mq.x1), ry = Math.min(mq.y0, mq.y1) - 1508;
      const rw = Math.abs(mq.x1 - mq.x0), rh = Math.abs(mq.y1 - mq.y0);
      if (ry > 20 && ry < H) {
        tlCtx.fillStyle = 'rgba(56, 189, 248, 0.15)'; tlCtx.fillRect(rx, ry, rw, rh);
        tlCtx.strokeStyle = '#38BDF8'; tlCtx.strokeRect(rx, ry, rw, rh);
      }
    }

    document.getElementById('tl-stat-lbl').textContent =
      t >= SEQ_DUR - 0.5 ? `✔ Đã lắp xong ${builtClips} Clips` : `Đang lắp: ${builtClips}/26 Clips...`;

    const phX = secToX(t);
    tlCtx.strokeStyle = '#FFFFFF'; tlCtx.lineWidth = 1.6;
    tlCtx.beginPath(); tlCtx.moveTo(phX, 8); tlCtx.lineTo(phX, H); tlCtx.stroke();
    tlCtx.fillStyle = '#FFFFFF';
    tlCtx.beginPath();
    tlCtx.moveTo(phX - 5, 2); tlCtx.lineTo(phX + 5, 2); tlCtx.lineTo(phX + 5, 9); tlCtx.lineTo(phX, 14); tlCtx.lineTo(phX - 5, 9);
    tlCtx.closePath(); tlCtx.fill();
  }

  // ==================== 8. VECTOR CURSOR RENDERER ====================
  function drawCursor(ctx, x, y, sc, ctype, badge) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(sc, sc);
    ctx.shadowColor = 'rgba(0,0,0,0.58)';
    ctx.shadowBlur = 3.5; ctx.shadowOffsetX = 1; ctx.shadowOffsetY = 1.5;

    if (ctype === 'ew-resize') {
      ctx.beginPath();
      ctx.moveTo(-8,0); ctx.lineTo(-3.8,-4); ctx.lineTo(-3.8,-1.5);
      ctx.lineTo(3.8,-1.5); ctx.lineTo(3.8,-4); ctx.lineTo(8,0);
      ctx.lineTo(3.8,4); ctx.lineTo(3.8,1.5); ctx.lineTo(-3.8,1.5); ctx.lineTo(-3.8,4);
      ctx.closePath();
      ctx.fillStyle = '#FFF'; ctx.fill();
      ctx.lineWidth = 1.2; ctx.strokeStyle = '#090C12'; ctx.stroke();
    } else if (ctype === 'cross') {
      ctx.strokeStyle = '#000'; ctx.lineWidth = 2.6;
      ctx.beginPath(); ctx.moveTo(-6,0); ctx.lineTo(6,0); ctx.moveTo(0,-6); ctx.lineTo(0,6); ctx.stroke();
      ctx.strokeStyle = '#FFF'; ctx.lineWidth = 1.1; ctx.stroke();
    } else if (ctype === 'ibeam') {
      ctx.strokeStyle = '#000'; ctx.lineWidth = 2.6;
      ctx.beginPath(); ctx.moveTo(-3.5,-6.5); ctx.lineTo(3.5,-6.5); ctx.moveTo(0,-6.5); ctx.lineTo(0,6.5); ctx.moveTo(-3.5,6.5); ctx.lineTo(3.5,6.5); ctx.stroke();
      ctx.strokeStyle = '#FFF'; ctx.lineWidth = 1.1; ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.moveTo(0,0); ctx.lineTo(0,16.4); ctx.lineTo(4.2,12.5);
      ctx.lineTo(7.2,18.8); ctx.lineTo(9.6,17.6); ctx.lineTo(6.6,11.4); ctx.lineTo(11.6,11.4);
      ctx.closePath();
      ctx.fillStyle = '#FFFFFF'; ctx.fill();
      ctx.lineWidth = 1.25; ctx.strokeStyle = '#0B0F17'; ctx.stroke();
    }

    if (badge) {
      ctx.shadowBlur = 3;
      ctx.font = '700 8.2px "Segoe UI", sans-serif';
      const tw = ctx.measureText(badge.label).width;
      ctx.fillStyle = badge.color;
      ctx.beginPath(); ctx.roundRect(11, 12, tw + 9, 13.5, 4); ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 0.8; ctx.stroke();
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(badge.label, 15.5, 21.6);
    }
    ctx.restore();
  }

  // ==================== 9. MASTER 60FPS RENDERER ====================
  const liveImg = document.getElementById('liveview-img');
  const snapBox = document.getElementById('cc-snap-box');

  const pyLines = [
    '<span class="cm"># 120-Agent Direct B-Roll & Vector Thrower -> CapCut VN</span>',
    'voice.<span class="fn">onPhraseAhead</span>(<span class="nu">380</span>, <span class="kw">async</span> (beat) => {',
    '  src = <span class="kw">await</span> chatgpt4o.<span class="fn">generate9x16</span>(beat.prompt)',
    '  card = <span class="kw">await</span> photoshop.<span class="fn">craftCutoutCard</span>(src, beat.badge)',
    '  pill = <span class="kw">await</span> illustrator.<span class="fn">renderVectorType</span>(beat.words)',
    '  <span class="kw">await</span> swarm.<span class="fn">throwIntoCapCut</span>([card, pill], bin=<span class="nu">True</span>)',
    '  capcut.timeline.<span class="fn">snapToPlayhead</span>(lufs=<span class="nu">-14.0</span>, fps=<span class="nu">60</span>)',
    '})'
  ];
  const cmsCopy = 'Bí quyết chăm sóc vùng nhạy cảm chuẩn pH 4.5 dịu nhẹ, giữ hàng rào lợi khuẩn khỏe mạnh êm thoáng mỗi ngày!';

  window.renderFrame = async function (frameIdx) {
    const f = Math.max(0, Math.min(TOTAL_FRAMES - 1, frameIdx));
    const t = f / FPS;
    const pushY = getPushY(t);

    // 1. Overlapping Top Windows Jumping Z-Order (`261127` style!)
    const ls = getLayoutAt(t);
    for (const k of WIN_IDS) {
      const el = document.getElementById(`win-${k}`);
      const r = ls.rects[k];
      el.style.left = `${r.x.toFixed(1)}px`; el.style.top = `${r.y.toFixed(1)}px`;
      el.style.width = `${r.w.toFixed(1)}px`; el.style.height = `${r.h.toFixed(1)}px`;
      el.style.zIndex = String(r.z); el.style.transform = `scale(${r.sc.toFixed(3)})`;
      el.className = k === ls.focus ? 'app-win focused' : 'app-win';
    }
    ['dk-ps','dk-gpt','dk-ai','dk-cms','dk-sw'].forEach((did) => {
      document.getElementById(did).className = (did === ls.dock) ? 'dk-item on' : 'dk-item';
    });
    const hud = document.getElementById('alt-tab-hud');
    if (ls.showAltTab) {
      hud.style.display = 'flex';
      for (let a = 0; a < 5; a++) document.getElementById(`at-${a}`).className = (a === ls.atIdx) ? 'at-it sel' : 'at-it';
    } else {
      hud.style.display = 'none';
    }
    document.getElementById('sys-ops').textContent = `${390 + Math.floor(Math.sin(t * 6) * 42 + 42)} ops/s`;

    // 2. Render Top Apps + CMS + IDE + Swarm Stream
    drawPhotoshop(f, t);
    drawIllustrator(t);
    drawChatGpt(t, f);

    const typed = Math.floor((t * 32) % (cmsCopy.length + 14));
    document.getElementById('cms-type').textContent = cmsCopy.slice(0, Math.min(cmsCopy.length, typed)) + (f % 20 < 10 ? '▋' : '');
    for (let c = 0; c < 3; c++) {
      document.getElementById(`cmsc-${c}`).className = (c === Math.floor(t * 2) % 3) ? 'cms-card hot' : 'cms-card';
    }
    const curL = Math.floor(t * 4) % pyLines.length;
    document.getElementById('ide-lines').innerHTML = pyLines.map((h, i) =>
      `<div class="cl${i === curL ? ' cur' : ''}"><span style="color:#475569;margin-right:6px;">${i+1}</span>${h}</div>`
    ).join('');

    const recentThrows = THROW_EVENTS.filter(e => t >= e.t0).slice(-6);
    document.getElementById('swarm-rows').innerHTML = recentThrows.map((ev, idx) => {
      const st = t < ev.tLand ? 'THROWING ↘' : 'LOCKED ✓';
      const nm = ev.text ? `"${ev.text.slice(0, 22)}..."` : ev.tlLbl;
      return `<div class="srow${idx === recentThrows.length - 1 ? ' hot' : ''}"><span><b style="color:#67E8F9">[${ev.agent}]</b> ${nm}</span><span style="color:#34D399;font-weight:700;">${st}</span></div>`;
    }).join('');

    // 3. Render Vietnamese CapCut Left Pane & Inspector
    drawCapCutLeftPane(t);
    drawCapCutInspector(t, pushY);

    // 4. CapCut Player Sync
    const secI = Math.floor(t), frmI = Math.floor((t - secI) * 60);
    document.getElementById('cc-tc').textContent = `00:00:${String(secI).padStart(2, '0')}:${String(frmI).padStart(2, '0')}`;
    document.getElementById('cc-save-txt').textContent = `Tự động lưu: 13:52:${String(18 + secI).padStart(2, '0')}`;
    document.getElementById('tl-zoom-knob').style.left = `${(54 + Math.sin(t * 3) * 12).toFixed(1)}%`;

    const expBtn = document.getElementById('cc-export');
    const playIco = document.getElementById('cc-play-ico');
    if (t >= SEQ_DUR - 0.50) {
      expBtn.textContent = '✔ Đã xuất'; expBtn.className = 'cc-export-btn done';
      playIco.innerHTML = '<span style="color:#10B981;font-size:9px;font-weight:700;">✔ Hoàn tất</span>';
      document.getElementById('cc-live-badge').textContent = '✔ COMPLETED 1080P 60FPS';
    } else {
      expBtn.textContent = '⇥ Xuất'; expBtn.className = 'cc-export-btn';
      playIco.textContent = '⏸';
      document.getElementById('cc-live-badge').textContent = '● LIVE THROW 60FPS';
    }

    const targetFrameSrc = `th_rendered_frames/frame_${String(f).padStart(4, '0')}.jpg`;
    if (!liveImg.src.endsWith(targetFrameSrc)) {
      await new Promise(res => { liveImg.onload = res; liveImg.onerror = res; liveImg.src = targetFrameSrc; });
    }

    // 5. Render 120 Cursors + Direct Curved-Arc Throws on `#fx-canvas`!
    fxCtx.clearRect(0, 0, 1080, 1920);
    const activeMarquees = [];

    // 5A. Group 1: 60 Task Cursors
    for (const tc of TASK_CURSORS) {
      let wp = null;
      for (let k = 0; k < tc.wps.length; k++) {
        const w = tc.wps[k];
        if (f >= w.f0 && f < w.f2) { wp = w; break; }
      }
      if (!wp) continue;

      let cx, cy, sc = tc.scale;
      if (f < wp.f1) {
        const u = minJerk((f - wp.f0) / Math.max(1, wp.f1 - wp.f0));
        const inv = 1 - u;
        const mx = (wp.x0 + wp.x1) * 0.5 + wp.arc;
        const my = (wp.y0 + wp.y1) * 0.5 - wp.arc * 0.5;
        cx = inv * inv * wp.x0 + 2 * inv * u * mx + u * u * wp.x1;
        cy = inv * inv * wp.y0 + 2 * inv * u * my + u * u * wp.y1;

        if (wp.carry && bImgs[wp.carryKey] && bImgs[wp.carryKey].complete) {
          fxCtx.save(); fxCtx.globalAlpha = 0.85;
          fxCtx.drawImage(bImgs[wp.carryKey], cx + 8, cy + 8, 54, 36);
          fxCtx.strokeStyle = '#38BDF8'; fxCtx.lineWidth = 1.4;
          fxCtx.strokeRect(cx + 8, cy + 8, 54, 36);
          fxCtx.restore();
        }
      } else {
        const hf = f - wp.f1;
        const hu = minJerk(hf / Math.max(1, wp.f2 - wp.f1));
        cx = wp.x1 + wp.dx * hu;
        cy = wp.y1 + wp.dy * hu;
        if (hf < 4) sc *= 0.86;
        if (hf < 9) {
          fxCtx.strokeStyle = `rgba(56,189,248,${(1 - hf / 9) * 0.55})`;
          fxCtx.lineWidth = 1.2;
          fxCtx.beginPath(); fxCtx.arc(cx, cy, 3 + hf * 1.2, 0, Math.PI * 2); fxCtx.stroke();
        }
        if (wp.isMq) activeMarquees.push({ x0: wp.x1, y0: wp.y1, x1: cx, y1: cy });
      }
      const safe = pushOutOfFaceZone(cx, cy);
      drawCursor(fxCtx, safe.x, safe.y, sc, wp.ctype, tc.badge);
    }

    // 5B. Group 2: 60 Escort Swarm Cursors ("60 con chạy bên cạnh con chuột chính")!
    const heroNow = getHeroTrajectory(t);
    for (const ec of ESCORT_SWARM) {
      const hp = getHeroTrajectory(Math.max(0, t - ec.lag));
      const spread = hp.clicking ? 0.62 : 1.0;
      const wob = Math.sin(t * ec.wFreq + ec.wPhase) * 6.5;
      const ox = Math.cos(ec.angle) * ec.dist * spread + wob;
      const oy = Math.sin(ec.angle) * ec.dist * spread - wob * 0.5;
      const safe = pushOutOfFaceZone(hp.x + ox, hp.y + oy);
      drawCursor(fxCtx, safe.x, safe.y, hp.clicking ? ec.scale * 0.86 : ec.scale, 'arrow', null);
    }
    drawCursor(fxCtx, heroNow.x, heroNow.y, heroNow.clicking ? 0.96 : 1.08, 'arrow', { label: 'Lead-Agent', color: '#0284C7' });

    // 5C. DIRECT CURVED-ARC THROW INTO CAPCUT `Tệp phương tiện` (Adds item right on arrival — NO modal box!)
    BIN_IMPORT_SCHEDULE.forEach((bi, idx) => {
      if (t >= bi.tThrow0 && t <= bi.tImported) {
        const u = minJerk((t - bi.tThrow0) / (bi.tImported - bi.tThrow0));
        const sp = winCenter(bi.tThrow0, bi.srcWin, 0.44, 0.54);
        const dp = binSlotScreenPt(2 + idx);
        const inv = 1 - u;
        const mx = (sp.x + dp.x) * 0.5 - 75, my = (sp.y + dp.y) * 0.45;
        const cx = inv * inv * sp.x + 2 * inv * u * mx + u * u * (dp.x - 42);
        const cy = inv * inv * sp.y + 2 * inv * u * my + u * u * (dp.y - 34);
        const cw = lerp(110, 92, u), ch = lerp(142, 68, u);

        fxCtx.save();
        fxCtx.strokeStyle = 'rgba(0, 229, 255, 0.55)'; fxCtx.lineWidth = 2.0; fxCtx.setLineDash([6, 4]);
        fxCtx.beginPath(); fxCtx.moveTo(sp.x, sp.y); fxCtx.quadraticCurveTo(mx, my, cx + cw * 0.5, cy + ch * 0.5); fxCtx.stroke();
        fxCtx.restore();

        drawFramedCard(fxCtx, cx, cy, cw, ch, brollDefs[bi.bIdx], 0.96);
        drawCursor(fxCtx, cx + cw * 0.22, cy + 8, 1.02, 'arrow', { label: 'Import-Bin', color: '#0891B2' });
      }
    });

    // 5D. SIGNATURE 261127 DIRECT CURVED-ARC THROWS INTO CAPCUT `Trình phát` (LIVE VIEW)!
    let snapRect = null;
    for (const ev of THROW_EVENTS) {
      if (t >= ev.t0 && t <= ev.tLand) {
        const u = minJerk((t - ev.t0) / (ev.tLand - ev.t0));
        const sp = winCenter(ev.t0, ev.srcWin, ev.rx, ev.ry);
        const inv = 1 - u;
        const mx = (sp.x + ev.dx) * 0.5 + ev.arcX;
        const my = (sp.y + ev.dy) * 0.45;
        const cx = inv * inv * sp.x + 2 * inv * u * mx + u * u * ev.dx;
        const cy = inv * inv * sp.y + 2 * inv * u * my + u * u * ev.dy;
        const cw = lerp(ev.dw * 0.78, ev.dw, u);
        const ch = lerp(ev.dh * 0.78, ev.dh, u);

        // Glowing cyan dashed trajectory arc from Top App straight into `Trình phát`!
        fxCtx.save();
        fxCtx.strokeStyle = 'rgba(0, 229, 255, 0.62)';
        fxCtx.lineWidth = 2.4;
        fxCtx.setLineDash([6, 4]);
        fxCtx.beginPath();
        fxCtx.moveTo(sp.x, sp.y);
        fxCtx.quadraticCurveTo(mx, my, cx + cw * 0.5, cy + ch * 0.5);
        fxCtx.stroke();
        fxCtx.restore();

        // Draw Flying Card / KeyText / Hook / Subtitle Pill!
        fxCtx.save();
        fxCtx.shadowColor = 'rgba(0, 229, 255, 0.68)';
        fxCtx.shadowBlur = 16;
        if (ev.kind === 'card') {
          drawFramedCard(fxCtx, cx, cy, cw, ch, brollDefs[ev.bIdx], 0.96);
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2.2;
          fxCtx.strokeRect(cx, cy, cw, ch);
        } else if (ev.kind === 'hook') {
          fxCtx.fillStyle = '#FFE600';
          fxCtx.beginPath(); fxCtx.roundRect(cx, cy, cw, ch, 10); fxCtx.fill();
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2.2; fxCtx.stroke();
          fxCtx.shadowBlur = 0;
          fxCtx.fillStyle = '#090D16'; fxCtx.font = '800 9.5px "BeVietnamExtraBold", "Segoe UI"'; fxCtx.textAlign = 'center';
          fxCtx.fillText(ev.text, cx + cw * 0.5, cy + ch * 0.58);
          fxCtx.textAlign = 'left';
        } else if (ev.kind === 'key') {
          fxCtx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          fxCtx.beginPath(); fxCtx.roundRect(cx, cy, cw, ch, 12); fxCtx.fill();
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2.2; fxCtx.stroke();
          fxCtx.shadowBlur = 0;
          fxCtx.fillStyle = '#FDE047'; fxCtx.font = '900 10.5px "MontserratBlack", "Segoe UI"'; fxCtx.textAlign = 'center';
          fxCtx.fillText(ev.text, cx + cw * 0.5, cy + ch * 0.58);
          fxCtx.textAlign = 'left';
        } else {
          // Exact 261127 Glowing White/Cyan Subtitle Pill Flying In!
          fxCtx.fillStyle = 'rgba(255, 255, 255, 0.96)';
          fxCtx.beginPath(); fxCtx.roundRect(cx, cy, cw, ch, 12); fxCtx.fill();
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2.0; fxCtx.stroke();
          fxCtx.shadowBlur = 0;
          fxCtx.fillStyle = '#0F172A'; fxCtx.font = '800 9.2px "BeVietnamExtraBold", "Segoe UI"'; fxCtx.textAlign = 'center';
          fxCtx.fillText(ev.text.slice(0, 28), cx + cw * 0.5, cy + ch * 0.62);
          fxCtx.textAlign = 'left';
        }
        fxCtx.restore();

        // Twin Thrower Cursors Carrying Both Corners (Exact 261127 `ref_1_3.2s.jpg`!)
        drawCursor(fxCtx, cx + cw * 0.16, cy + 6, 1.06, 'arrow', { label: ev.agent, color: ev.color });
        drawCursor(fxCtx, cx + cw * 0.84, cy + ch - 4, 0.96, 'arrow', null);
      } else if (t > ev.tLand && t <= ev.tLand + 0.22) {
        snapRect = { l: ev.dx - VP_X, t: ev.dy - VP_Y, w: ev.dw, h: ev.dh };
        const ru = minJerk((t - ev.tLand) / 0.22);
        const rx = lerp(ev.dx + ev.dw * 0.85, ev.dx + ev.dw + 52, ru);
        const ry = lerp(ev.dy + 10, ev.dy - 42, ru);
        const safe = pushOutOfFaceZone(rx, ry);
        drawCursor(fxCtx, safe.x, safe.y, 1.0, 'arrow', { label: ev.agent, color: ev.color });
      }
    }

    if (snapRect) {
      snapBox.style.display = 'block';
      snapBox.style.left = `${snapRect.l.toFixed(1)}px`;
      snapBox.style.top  = `${snapRect.t.toFixed(1)}px`;
      snapBox.style.width  = `${snapRect.w.toFixed(1)}px`;
      snapBox.style.height = `${snapRect.h.toFixed(1)}px`;
    } else {
      snapBox.style.display = 'none';
    }

    // 6. Render CapCut Timeline
    drawCapCutTimeline(t, activeMarquees);
  };
})();
