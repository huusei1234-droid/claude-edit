// V6 Premiere Pro 2026 Master Engine — Feel Chicken "Kiểm Tra Miệng 20/11" (48.467s @ 60fps = 2,908 frames)
// Combines:
// 1. ZERO Google Flow! Overlapping, Z-Jumping 6 Top Windows (Photoshop 2026 + ChatGPT Plus 4o + Illustrator 2026 + Feel Chicken CMS + JSX IDE + 120-Agent Stream)
// 2. Signature 261127 Direct Top-to-Bottom Curved-Arc Throws (Twin Thrower Cursors + Glowing Cyan Dashed Trajectory -> Program Monitor + Progressive Project Bin + Timeline)
// 3. 100% Photo-Authentic Adobe Premiere Pro 2026 Bottom Workspace (Project Bin + Lumetri Scopes + VU Meters + Cycling Effect Controls / Lumetri Color / Essential Graphics + 7-Track Sequence)
// 4. 120 Purposeful Cursors (60 Specialist Task Cursors + 60 Escort Swarm Cursors riding every Throw & Playhead Edit, strictly Face-Safe!)
(function () {
  const meta = window.AUDIO_DATA || { fps: 60, total_frames: 2908, duration_sec: 48.4667, env_l: [], env_r: [], waveform: [] };
  const FPS = meta.fps || 60;
  const TOTAL_FRAMES = meta.total_frames || 2908;
  const SEQ_DUR = meta.duration_sec || (TOTAL_FRAMES / FPS);

  // Timeline Canvas (`#tl-canvas`: width = 1046, height = 416; screen offset: left = 32, top = 1502)
  const TL_SCREEN_X = 32;
  const TL_SCREEN_Y = 1502;
  const HDR_W = 104;
  const TL_W  = 930;
  const secToCanvasX = (sec) => HDR_W + (Math.max(0, Math.min(SEQ_DUR, sec)) / SEQ_DUR) * TL_W;
  const secToScreenX = (sec) => TL_SCREEN_X + secToCanvasX(sec);

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

  // Preload 24 Sequence Filmstrip Thumbnails & 21 Real Cropped Throw Sprites
  const stripImgs = [];
  for (let i = 0; i < 24; i++) {
    const im = new Image();
    im.src = `assets/thumbs/strip_${String(i).padStart(2, '0')}.jpg`;
    stripImgs.push(im);
  }

  const SPRITE_FILES = {
    s1_bub:      'assets/throws/s1_bub.jpg',
    s1_ram:      'assets/throws/s1_ram.jpg',
    s2_pray:     'assets/throws/s2_pray.jpg',
    s2_teacher:  'assets/throws/s2_teacher.jpg',
    s3_hdr2011:  'assets/throws/s3_hdr2011.jpg',
    s3_chicken:  'assets/throws/s3_chicken.jpg',
    s3_chalk:    'assets/throws/s3_chalk.jpg',
    s4_jar:      'assets/throws/s4_jar.jpg',
    q1_lichsu:   'assets/throws/q1_lichsu.jpg',
    q2_nguvan:   'assets/throws/q2_nguvan.jpg',
    q3_dialy:    'assets/throws/q3_dialy.jpg',
    q4_toanhoc:  'assets/throws/q4_toanhoc.jpg',
    q5_hoahoc:   'assets/throws/q5_hoahoc.jpg',
    q6_domeo:    'assets/throws/q6_domeo.jpg',
    s5_coqua:    'assets/throws/s5_coqua.jpg',
    s5_feast:    'assets/throws/s5_feast.jpg',
    s5_pill_tok: 'assets/throws/s5_pill_tok.jpg',
    s6_cert:     'assets/throws/s6_cert.jpg',
    s6_xedui:    'assets/throws/s6_xedui.jpg',
    s6_thom:     'assets/throws/s6_thom.jpg',
    s6_endcard:  'assets/throws/s6_endcard.jpg',
    fc_logo:     'assets/fc_logo.png'
  };
  const spImgs = {};
  for (const [k, p] of Object.entries(SPRITE_FILES)) {
    const im = new Image();
    im.src = p;
    spImgs[k] = im;
  }

  const GPT_SOURCE_PACKS = [
    { key: 's2_pray',    binName: '01_LopHoc_Pray_9x16.mp4',   prompt: 'Tạo cảnh lớp học Việt Nam 9:16: học sinh hồi hộp chắp tay khi cô giáo gọi kiểm tra miệng...' },
    { key: 's2_teacher', binName: '02_KyUc_CoTro_2011.mp4',    prompt: 'Tạo cảnh lớp học 20/11 ấm áp nắng vàng: cô trò Việt Nam rạng rỡ kỷ niệm ngày Nhà giáo...' },
    { key: 's3_chalk',   binName: '03_BangPhan_KiemTra.psd',   prompt: 'Thiết kế bảng phấn xanh 20/11 Kawaii: KIỂM TRA MIỆNG - TRẢ LỜI ĐÚNG NHẬN QUÀ NGAY!...' },
    { key: 'q6_domeo',   binName: '04_Bo6The_CauHoi_2011.psd', prompt: 'Tạo bộ 6 thẻ câu hỏi bốc thăm học đường & đố mẹo lắt léo Feel Chicken 38 Nguyễn Đình Chiểu...' },
    { key: 's5_feast',   binName: '05_BanTiec_8MiengGa.mp4',   prompt: 'Cận cảnh bàn tiệc 8 miếng gà sốt Hàn Quốc đẫm phô mai, tokbokki, salad & khoai chiên nóng hổi...' },
    { key: 's6_endcard', binName: '06_EndCard_38NDC_Kute.psd', prompt: 'Thiết kế thẻ địa chỉ Kawaii Feel Chicken CS1: 38 Nguyễn Đình Chiểu, Nha Trang — Ghé ngay!...' }
  ];

  // Exact Viewport inside Premiere Pro `Program: KiemTraMieng_9x16`
  const vpEl = document.getElementById('pr-viewport-wrap');
  const vpRect = vpEl.getBoundingClientRect();
  const VP_X = vpRect.left || 412;
  const VP_Y = vpRect.top  || 998;
  const VP_W = vpRect.width  || 250;
  const VP_H = vpRect.height || 444;
  const mapX = (x1080) => VP_X + (x1080 / 1080) * VP_W;
  const mapY = (y1920) => VP_Y + (y1920 / 1920) * VP_H;
  const mapW = (w1080) => (w1080 / 1080) * VP_W;
  const mapH = (h1920) => (h1920 / 1920) * VP_H;

  function pushOutOfFaceZone(x, y) {
    if (x > VP_X + 34 && x < VP_X + VP_W - 34 && y > VP_Y + 46 && y < VP_Y + VP_H - 96) {
      return { x: x < VP_X + VP_W * 0.5 ? VP_X + 18 : VP_X + VP_W - 18, y };
    }
    return { x, y };
  }

  // ==================== 1. BELOVED 261127 OVERLAPPING & Z-JUMPING TOP LAYOUTS (ZERO FLOW!) ====================
  const TOP_LAYOUTS = [
    // 0.0..6.0s: Photoshop Front-Left (Skit Bubbles) + Illustrator Top-Right + ChatGPT Bottom-Left + CMS Bottom-Right
    { focus: 'ps', dock: 'dk-ps', atIdx: 0, rects: {
      ps:    { x: 10,  y: 36,  w: 612, h: 444, z: 33, s: 1.00 },
      ai:    { x: 548, y: 38,  w: 522, h: 406, z: 29, s: 0.99 },
      gpt:   { x: 12,  y: 462, w: 534, h: 442, z: 27, s: 0.99 },
      cms:   { x: 552, y: 454, w: 518, h: 448, z: 25, s: 0.98 },
      ide:   { x: 210, y: 230, w: 515, h: 382, z: 14, s: 0.94 },
      swarm: { x: 525, y: 225, w: 505, h: 385, z: 15, s: 0.94 }
    }},
    // 6.0..13.4s: ChatGPT Plus Jumps Top-Left (Classroom B-Rolls!) + Photoshop Top-Right + IDE & Swarm Bottom
    { focus: 'gpt', dock: 'dk-gpt', atIdx: 1, rects: {
      gpt:   { x: 10,  y: 36,  w: 540, h: 440, z: 34, s: 1.01 },
      ps:    { x: 468, y: 36,  w: 602, h: 446, z: 31, s: 1.00 },
      ide:   { x: 12,  y: 466, w: 536, h: 436, z: 27, s: 0.99 },
      swarm: { x: 554, y: 464, w: 516, h: 438, z: 29, s: 0.99 },
      ai:    { x: 520, y: 185, w: 510, h: 390, z: 16, s: 0.95 },
      cms:   { x: 80,  y: 235, w: 510, h: 410, z: 15, s: 0.94 }
    }},
    // 13.4..21.9s: Photoshop Front-Left (Chalkboard 20/11!) + Illustrator Vector Front-Right + CMS + ChatGPT
    { focus: 'ai', dock: 'dk-ai', atIdx: 2, rects: {
      ps:    { x: 12,  y: 36,  w: 614, h: 446, z: 32, s: 1.00 },
      ai:    { x: 536, y: 36,  w: 534, h: 418, z: 34, s: 1.01 },
      cms:   { x: 12,  y: 464, w: 530, h: 438, z: 27, s: 0.99 },
      gpt:   { x: 548, y: 460, w: 522, h: 442, z: 29, s: 1.00 },
      ide:   { x: 220, y: 225, w: 515, h: 385, z: 15, s: 0.94 },
      swarm: { x: 520, y: 220, w: 505, h: 385, z: 16, s: 0.95 }
    }},
    // 21.9..28.2s: 6-QUIZ-CARD VOLLEY! Photoshop Center-Left + Illustrator Top-Right + 120-Agent Swarm Front-Bottom!
    { focus: 'ps', dock: 'dk-ps', atIdx: 0, rects: {
      ps:    { x: 10,  y: 36,  w: 618, h: 448, z: 35, s: 1.01 },
      ai:    { x: 542, y: 38,  w: 528, h: 412, z: 32, s: 1.00 },
      gpt:   { x: 12,  y: 462, w: 534, h: 440, z: 30, s: 0.99 },
      swarm: { x: 552, y: 460, w: 518, h: 442, z: 33, s: 1.01 },
      cms:   { x: 70,  y: 230, w: 510, h: 410, z: 16, s: 0.95 },
      ide:   { x: 490, y: 220, w: 510, h: 385, z: 15, s: 0.94 }
    }},
    // 28.2..36.8s: Feel Chicken CMS Jumps Top-Left + Illustrator Behind-Head Vector + Photoshop Feast Cutout + Swarm!
    { focus: 'cms', dock: 'dk-cms', atIdx: 3, rects: {
      cms:   { x: 10,  y: 36,  w: 544, h: 438, z: 34, s: 1.01 },
      ai:    { x: 548, y: 38,  w: 522, h: 412, z: 31, s: 1.00 },
      ps:    { x: 12,  y: 460, w: 590, h: 444, z: 32, s: 1.00 },
      swarm: { x: 562, y: 462, w: 508, h: 440, z: 29, s: 0.99 },
      gpt:   { x: 480, y: 210, w: 515, h: 405, z: 16, s: 0.95 },
      ide:   { x: 60,  y: 225, w: 510, h: 385, z: 15, s: 0.94 }
    }},
    // 36.8..43.2s: ChatGPT + Photoshop Certificate & Crispy Chicken Callouts + JSX ExtendScript IDE!
    { focus: 'gpt', dock: 'dk-gpt', atIdx: 1, rects: {
      gpt:   { x: 10,  y: 36,  w: 538, h: 438, z: 33, s: 1.01 },
      ps:    { x: 468, y: 36,  w: 602, h: 446, z: 34, s: 1.01 },
      ide:   { x: 12,  y: 464, w: 536, h: 438, z: 29, s: 0.99 },
      ai:    { x: 552, y: 460, w: 518, h: 442, z: 31, s: 1.00 },
      cms:   { x: 80,  y: 230, w: 510, h: 410, z: 16, s: 0.95 },
      swarm: { x: 520, y: 220, w: 505, h: 385, z: 15, s: 0.94 }
    }},
    // 43.2..48.5s: Grand Finale Storefront End-Card `38 Nguyễn Đình Chiểu` + Premiere Quick Export!
    { focus: 'ps', dock: 'dk-sw', atIdx: 4, rects: {
      ps:    { x: 10,  y: 36,  w: 614, h: 446, z: 34, s: 1.01 },
      ai:    { x: 544, y: 38,  w: 526, h: 410, z: 31, s: 1.00 },
      cms:   { x: 12,  y: 462, w: 534, h: 440, z: 30, s: 0.99 },
      swarm: { x: 552, y: 460, w: 518, h: 442, z: 33, s: 1.01 },
      gpt:   { x: 480, y: 215, w: 515, h: 405, z: 16, s: 0.95 },
      ide:   { x: 60,  y: 225, w: 510, h: 385, z: 15, s: 0.94 }
    }}
  ];
  const LAYOUT_STARTS = [0, 6.0, 13.4, 21.9, 28.2, 36.8, 43.2];
  const WIN_IDS = ['ps', 'ai', 'gpt', 'cms', 'ide', 'swarm'];

  function getLayoutAt(t) {
    let idx = 0;
    for (let i = LAYOUT_STARTS.length - 1; i >= 0; i--) {
      if (t >= LAYOUT_STARTS[i]) { idx = i; break; }
    }
    const dt = t - LAYOUT_STARTS[idx];
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

  // ==================== 2. PROGRESSIVE PREMIERE PROJECT BIN + MILLISECOND-EXACT THROW SCHEDULE ====================
  // `#pr-bin-cvs` screen top-left: left = 3, top = 975, width = 294, height = 499
  const BIN_IMPORT_SCHEDULE = [
    { bIdx: 0, spKey: 's1_bub',     psIdx: 0, name: '01_Bub_ThanhOi.psd',   ext: 'PSD', tThrow0: 0.85,  tImported: 1.25,  tAdded: 1.40,  srcWin: 'ps'  },
    { bIdx: 1, spKey: 's2_pray',    psIdx: 1, name: '02_LopHoc_2011.mp4',   ext: 'MP4', tThrow0: 5.55,  tImported: 5.95,  tAdded: 6.10,  srcWin: 'gpt' },
    { bIdx: 2, spKey: 's3_chalk',   psIdx: 2, name: '03_BangPhan_KTM.psd',  ext: 'PSD', tThrow0: 17.55, tImported: 17.98, tAdded: 18.15, srcWin: 'ps'  },
    { bIdx: 3, spKey: 'q6_domeo',   psIdx: 3, name: '04_6The_CauHoi.psd',   ext: 'PSD', tThrow0: 24.65, tImported: 25.10, tAdded: 25.29, srcWin: 'ps'  },
    { bIdx: 4, spKey: 's5_feast',   psIdx: 4, name: '05_BanTiec_GaSot.mp4', ext: 'MP4', tThrow0: 28.95, tImported: 29.35, tAdded: 29.49, srcWin: 'gpt' },
    { bIdx: 5, spKey: 's6_endcard', psIdx: 5, name: '06_EndCard_38NDC.psd', ext: 'PSD', tThrow0: 44.00, tImported: 44.42, tAdded: 44.57, srcWin: 'ps'  }
  ];

  function binSlotScreenPt(visIdx) {
    const col = visIdx % 2, row = Math.floor(visIdx / 2);
    return { x: 3 + 12 + col * 138 + 64, y: 975 + 56 + row * 102 + 38 };
  }

  // Every hero graphic, B-Roll, Chalkboard, 6 Quiz Cards, Feast Table, Certificate & Kawaii End-Card
  // lands on the EXACT timestamp from `step12b_render_fc_v5_master.py`!
  const THROW_EVENTS = [
    // --- SCENE 1 (0.00..4.57s): Classroom Skit ---
    { kind: 'pill', text: 'LỚP HỌC FEEL CHICKEN • 20/11', t0: 0.01, tLand: 0.14, srcWin: 'ai', rx: 0.50, ry: 0.35, dx: mapX(130), dy: mapY(66),   dw: mapW(820), dh: mapH(76),   arcX: 95,  agent: 'Ai-Banner',  color: '#E11D48', tlTrack: 'V4', sEnd: 3.02, tlLbl: '[Ae] Banner_LopHoc_2011.mogrt' },
    { kind: 'img',  spKey: 's1_bub', psIdx: 0, t0: 0.96, tLand: 1.40, srcWin: 'ps', rx: 0.44, ry: 0.52, dx: mapX(92),  dy: mapY(188),  dw: mapW(896), dh: mapH(242),  arcX: -85, agent: 'Ps-Cutout',  color: '#2563EB', tlTrack: 'V2', sEnd: 3.04, tlLbl: '01_Bub_ThanhOi.psd' },
    { kind: 'img',  spKey: 's1_ram', psIdx: 0, t0: 1.06, tLand: 1.42, srcWin: 'ps', rx: 0.55, ry: 0.58, dx: mapX(525), dy: mapY(980),  dw: mapW(340), dh: mapH(270),  arcX: 75,  agent: 'Ps-Impact',  color: '#DC2626', tlTrack: 'V3', sEnd: 2.04, tlLbl: 'FX_Ram_Slap.psd' },
    { kind: 'pill', text: 'Em... em... ơ kìa?!',          t0: 3.30, tLand: 3.72, srcWin: 'ai', rx: 0.50, ry: 0.70, dx: mapX(258), dy: mapY(1441), dw: mapW(564), dh: mapH(148),  arcX: 120, agent: 'Ai-Bubble',  color: '#0284C7', tlTrack: 'V3', sEnd: 4.54, tlLbl: 'Bub_Thanh_OKia.mogrt' },

    // --- SCENE 2 (4.57..13.47s): Praying POV + Nostalgia 20/11 ---
    { kind: 'img',  spKey: 's2_pray', psIdx: 1, t0: 5.64, tLand: 6.10, srcWin: 'gpt', rx: 0.45, ry: 0.54, dx: mapX(0),   dy: mapY(0),    dw: mapW(1080),dh: mapH(1920), arcX: -90, agent: 'GPT-Broll',  color: '#10A37F', tlTrack: 'V2', sEnd: 9.48, tlLbl: '02_Broll_Pray_POV.mp4' },
    { kind: 'key',  text: 'KIỂM TRA MIỆNG!',              t0: 7.62, tLand: 8.05, srcWin: 'ai',  rx: 0.50, ry: 0.36, dx: mapX(70),  dy: mapY(1425), dw: mapW(940), dh: mapH(120),  arcX: 115, agent: 'Ai-PopType', color: '#F59E0B', tlTrack: 'V4', sEnd: 9.48, tlLbl: '[Ae] KTM_Gold_3D.mogrt' },
    { kind: 'pill', text: 'RUNG CẦM CẬP!!',               t0: 8.36, tLand: 8.77, srcWin: 'ai',  rx: 0.50, ry: 0.70, dx: mapX(150), dy: mapY(1585), dw: mapW(780), dh: mapH(110),  arcX: 135, agent: 'Ai-Shake',   color: '#E11D48', tlTrack: 'V3', sEnd: 9.48, tlLbl: 'Txt_RungCamCap.mogrt' },
    { kind: 'img',  spKey: 's2_teacher', psIdx: 1, t0: 11.06, tLand: 11.52, srcWin: 'gpt', rx: 0.45, ry: 0.54, dx: mapX(0), dy: mapY(0), dw: mapW(1080),dh: mapH(1920), arcX: 95,  agent: 'GPT-2011',   color: '#10A37F', tlTrack: 'V2', sEnd: 13.47,tlLbl: 'Broll_KyUc_2011.mp4' },
    { kind: 'pill', text: 'thấy BỒI HỒI GHÊ luôn á!',     t0: 11.84,tLand: 12.25,srcWin: 'ai',  rx: 0.50, ry: 0.70, dx: mapX(75),  dy: mapY(1605), dw: mapW(930), dh: mapH(110),  arcX: 130, agent: 'Ai-Type',    color: '#EC4899', tlTrack: 'V3', sEnd: 13.47,tlLbl: 'Txt_BoiHoiGhe.mogrt' },

    // --- SCENE 3 (13.47..21.97s): 20/11 Header + Cheese Chicken + Green Chalkboard ---
    { kind: 'img',  spKey: 's3_hdr2011', psIdx: 2, t0: 13.05, tLand: 13.47, srcWin: 'ps', rx: 0.44, ry: 0.48, dx: mapX(32), dy: mapY(66),  dw: mapW(1016),dh: mapH(300),  arcX: -85, agent: 'Ps-Header',  color: '#2563EB', tlTrack: 'V4', sEnd: 18.14,tlLbl: 'Hdr_2011_SapToi.psd' },
    { kind: 'img',  spKey: 's3_chicken', psIdx: 2, t0: 15.36, tLand: 15.81, srcWin: 'gpt',rx: 0.46, ry: 0.55, dx: mapX(0),  dy: mapY(380), dw: mapW(1080),dh: mapH(1100), arcX: 95,  agent: 'GPT-Food',   color: '#D97706', tlTrack: 'V2', sEnd: 18.14,tlLbl: 'CS1_GaPhoMai_Tok.mp4' },
    { kind: 'img',  spKey: 's3_chalk',   psIdx: 2, t0: 17.68, tLand: 18.15, srcWin: 'ps', rx: 0.44, ry: 0.52, dx: mapX(34), dy: mapY(405), dw: mapW(1012),dh: mapH(920),  arcX: -80, agent: 'Ps-Chalk',   color: '#059669', tlTrack: 'V2', sEnd: 21.97,tlLbl: '03_BangPhan_KTM.psd' },

    // --- SCENE 4 (21.97..27.93s): Lucky Quiz Jar + 6-CARD RAPID-FIRE STACKING VOLLEY! ---
    { kind: 'img',  spKey: 's4_jar',     psIdx: 3, t0: 21.52, tLand: 21.97, srcWin: 'gpt',rx: 0.45, ry: 0.54, dx: mapX(0),  dy: mapY(0),    dw: mapW(1080),dh: mapH(1920), arcX: 90,  agent: 'GPT-Jar',    color: '#0284C7', tlTrack: 'V2', sEnd: 27.93,tlLbl: 'HuBocTham_2011.mp4' },
    { kind: 'img',  spKey: 'q1_lichsu',  psIdx: 3, t0: 24.88, tLand: 25.29, srcWin: 'ps', rx: 0.40, ry: 0.52, dx: mapX(62), dy: mapY(1405), dw: mapW(956), dh: mapH(265),  arcX: -95, agent: 'Quiz-#01',   color: '#10B981', tlTrack: 'V3', sEnd: 27.93,tlLbl: 'Quiz_01_6Cards_Stack.psd' },
    { kind: 'img',  spKey: 'q2_nguvan',  psIdx: 3, t0: 25.26, tLand: 25.67, srcWin: 'ai', rx: 0.48, ry: 0.50, dx: mapX(58), dy: mapY(1142), dw: mapW(962), dh: mapH(258),  arcX: 110, agent: 'Quiz-#41',   color: '#F59E0B', tlTrack: null, sEnd: 27.93,tlLbl: 'Quiz_02_NguVan.psd' },
    { kind: 'img',  spKey: 'q3_dialy',   psIdx: 3, t0: 25.64, tLand: 26.05, srcWin: 'ps', rx: 0.44, ry: 0.52, dx: mapX(54), dy: mapY(868),  dw: mapW(972), dh: mapH(274),  arcX: -80, agent: 'Quiz-#18',   color: '#0284C7', tlTrack: null, sEnd: 27.93,tlLbl: 'Quiz_03_38NDC.psd' },
    { kind: 'img',  spKey: 'q4_toanhoc', psIdx: 3, t0: 26.02, tLand: 26.43, srcWin: 'gpt',rx: 0.46, ry: 0.54, dx: mapX(58), dy: mapY(605),  dw: mapW(964), dh: mapH(263),  arcX: 95,  agent: 'Quiz-#55',   color: '#8B5CF6', tlTrack: null, sEnd: 27.93,tlLbl: 'Quiz_04_ToanHoc.psd' },
    { kind: 'img',  spKey: 'q5_hoahoc',  psIdx: 3, t0: 26.40, tLand: 26.81, srcWin: 'ps', rx: 0.42, ry: 0.50, dx: mapX(58), dy: mapY(342),  dw: mapW(964), dh: mapH(263),  arcX: -90, agent: 'Quiz-#72',   color: '#EC4899', tlTrack: null, sEnd: 27.93,tlLbl: 'Quiz_05_SotHan.psd' },
    { kind: 'img',  spKey: 'q6_domeo',   psIdx: 3, t0: 26.78, tLand: 27.19, srcWin: 'ai', rx: 0.50, ry: 0.48, dx: mapX(48), dy: mapY(870),  dw: mapW(984), dh: mapH(282),  arcX: 115, agent: 'Quiz-#100',  color: '#E11D48', tlTrack: 'V4', sEnd: 27.93,tlLbl: '[Ae] Quiz_100_Ga2Kg.aep' },

    // --- SCENE 5 (27.93..36.83s): Behind-Head RVM + CÓ QUÀ!! + Feast Table + 20/11 ---
    { kind: 'key',  text: 'SĂN QUÀ CỰC ĐỈNH',             t0: 27.52, tLand: 27.94, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(90),  dy: mapY(345),  dw: mapW(900), dh: mapH(140),  arcX: 110, agent: 'Ae-Orbital', color: '#8B5CF6', tlTrack: 'V4', sEnd: 29.49,tlLbl: '[Ae] BehindHead_SanQua.aep' },
    { kind: 'img',  spKey: 's5_coqua',   psIdx: 4, t0: 28.40, tLand: 28.81, srcWin: 'ps', rx: 0.44, ry: 0.52, dx: mapX(230), dy: mapY(1400), dw: mapW(620), dh: mapH(235),  arcX: -75, agent: 'Ps-CoQua',   color: '#F59E0B', tlTrack: 'V3', sEnd: 29.49,tlLbl: 'Pop_CoQua_Gold.psd' },
    { kind: 'img',  spKey: 's5_feast',   psIdx: 4, t0: 29.06, tLand: 29.49, srcWin: 'ps', rx: 0.44, ry: 0.52, dx: mapX(0),   dy: mapY(240),  dw: mapW(1080),dh: mapH(1280), arcX: -90, agent: 'Ps-Feast',   color: '#E11D48', tlTrack: 'V2', sEnd: 32.85,tlLbl: '05_BanTiec_8MiengGa.mp4' },
    { kind: 'pill', text: 'GÀ SỐT HÀN QUỐC CỰC NGON!!',    t0: 30.24, tLand: 30.65, srcWin: 'ai', rx: 0.50, ry: 0.70, dx: mapX(110), dy: mapY(1300), dw: mapW(860), dh: mapH(130),  arcX: 130, agent: 'Ai-Callout', color: '#EA580C', tlTrack: 'V3', sEnd: 31.77,tlLbl: 'Pill_GaSotHanQuoc.mogrt' },
    { kind: 'img',  spKey: 's5_pill_tok',psIdx: 4, t0: 31.36, tLand: 31.77, srcWin: 'ps', rx: 0.45, ry: 0.54, dx: mapX(135), dy: mapY(1295), dw: mapW(810), dh: mapH(130),  arcX: -80, agent: 'Ps-Pill',    color: '#10B981', tlTrack: 'V3', sEnd: 32.85,tlLbl: 'Pill_Tokbokki_Salad.psd' },
    { kind: 'key',  text: 'AI ĐẾN QUÁN CŨNG CÓ QUÀ!',      t0: 32.42, tLand: 32.85, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(80),  dy: mapY(260),  dw: mapW(920), dh: mapH(250),  arcX: 115, agent: 'Ae-3DBehind',color: '#9333EA', tlTrack: 'V4', sEnd: 35.65,tlLbl: '[Ae] RVM_AiDenCungCoQua.aep' },
    { kind: 'key',  text: 'ÁP DỤNG ĐẾN HẾT 20/11!',        t0: 35.22, tLand: 35.65, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(80),  dy: mapY(260),  dw: mapW(920), dh: mapH(250),  arcX: 115, agent: 'Ae-Firework',color: '#EC4899', tlTrack: 'V4', sEnd: 36.83,tlLbl: '[Ae] HetNgay_2011_FW.aep' },

    // --- SCENE 6 (36.83..48.47s): Certificate + Crispy Bite Callouts + Storefront End-Card ---
    { kind: 'img',  spKey: 's6_cert',    psIdx: 5, t0: 36.44, tLand: 36.86, srcWin: 'ps', rx: 0.44, ry: 0.50, dx: mapX(50),  dy: mapY(68),   dw: mapW(980), dh: mapH(257),  arcX: -85, agent: 'Ps-Cert',    color: '#D97706', tlTrack: 'V4', sEnd: 42.77,tlLbl: 'Cert_HocSinhGioi_2011.psd' },
    { kind: 'img',  spKey: 's6_xedui',   psIdx: 5, t0: 39.18, tLand: 39.61, srcWin: 'ps', rx: 0.40, ry: 0.54, dx: mapX(68),  dy: mapY(1125), dw: mapW(527), dh: mapH(160),  arcX: -80, agent: 'Ps-Callout1',color: '#E11D48', tlTrack: 'V2', sEnd: 41.15,tlLbl: 'Callout_XeDuiGa.psd' },
    { kind: 'img',  spKey: 's6_thom',    psIdx: 5, t0: 39.56, tLand: 39.97, srcWin: 'ai', rx: 0.50, ry: 0.55, dx: mapX(568), dy: mapY(1265), dw: mapW(424), dh: mapH(150),  arcX: 105, agent: 'Ai-Callout2',color: '#EA580C', tlTrack: null, sEnd: 41.15,tlLbl: 'Callout_ThomNucMui.psd' },
    { kind: 'key',  text: 'GIÒN RỤM RỤM!! ĐẪM SỐT HÀN!',   t0: 40.72, tLand: 41.15, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(90),  dy: mapY(1150), dw: mapW(900), dh: mapH(280),  arcX: 115, agent: 'Ae-Bounce',  color: '#F59E0B', tlTrack: 'V2', sEnd: 42.77,tlLbl: '[Ae] Bite_GionRumRum.aep' },
    { kind: 'key',  text: 'GHÉ FEEL CHICKEN NGAY!',        t0: 44.08, tLand: 44.54, srcWin: 'ai', rx: 0.50, ry: 0.36, dx: mapX(80),  dy: mapY(305),  dw: mapW(920), dh: mapH(120),  arcX: 110, agent: 'Ai-CTA',     color: '#E11D48', tlTrack: 'V4', sEnd: SEQ_DUR, tlLbl: '[Ae] CTA_GheFeelChicken.aep' },
    { kind: 'img',  spKey: 's6_endcard', psIdx: 5, t0: 44.14, tLand: 44.56, srcWin: 'ps', rx: 0.44, ry: 0.52, dx: mapX(44),  dy: mapY(1470), dw: mapW(992), dh: mapH(385),  arcX: -85, agent: 'Ps-EndCard', color: '#0284C7', tlTrack: 'V2', sEnd: SEQ_DUR, tlLbl: '06_EndCard_38NDC.psd' }
  ];

  // Add spoken Kawaii Subtitle Phrases from `window.WORDS_DATA` outside hero-typography windows!
  const HERO_WINDOWS = [
    [0.0, 4.57], [6.08, 9.50], [11.45, 13.47], [18.12, 21.97], [24.85, 29.52], [44.40, 49.0]
  ];
  const words = (window.WORDS_DATA && window.WORDS_DATA.words) ? window.WORDS_DATA.words : [];
  if (words.length > 0) {
    let cur = [];
    for (let i = 0; i < words.length; i++) {
      cur.push(words[i]);
      const span = cur[cur.length - 1].e - cur[0].s;
      const punct = /[?.!,;:]$/.test(words[i].w);
      if (cur.length >= 6 || (cur.length >= 4 && (span >= 1.55 || punct)) || i === words.length - 1) {
        const s0 = cur[0].s, e0 = cur[cur.length - 1].e + 0.12;
        const txt = cur.map(x => x.w).join(' ');
        cur = [];
        const blocked = HERO_WINDOWS.some(([hw0, hw1]) => (s0 >= hw0 - 0.15 && s0 <= hw1 + 0.05) || (e0 >= hw0 + 0.10 && s0 <= hw1));
        if (!blocked) {
          THROW_EVENTS.push({
            kind: 'sub', text: txt,
            t0: Math.max(0.3, s0 - 0.36), tLand: s0,
            srcWin: 'ai', rx: 0.50, ry: 0.72,
            dx: mapX(90), dy: mapY(1520), dw: mapW(900), dh: mapH(96),
            arcX: 150, agent: 'Sub-Premiere', color: '#D946EF',
            tlTrack: 'V3', sEnd: e0, tlLbl: `Sub_${txt.slice(0, 12)}`
          });
        }
      }
    }
  }
  THROW_EVENTS.sort((a, b) => a.t0 - b.t0);

  const SFX_BLOCKS = [
    1.40, 3.72, 6.10, 8.05, 11.52, 13.47, 15.81, 18.15, 21.97,
    25.29, 25.67, 26.05, 26.43, 26.81, 27.19,
    28.81, 29.49, 32.85, 35.65, 36.86, 39.61, 41.15, 44.74
  ];

  // ==================== 3. 120 PURPOSEFUL AGENTS (60 TASK CURSORS + 60 ESCORT/THROWER SWARM) ====================
  const NAMED_BADGES = [
    { label: 'Ps-Cutout',     color: '#2563EB', role: 'psCanvas' },
    { label: 'Ps-Curves',     color: '#0891B2', role: 'psLayers' },
    { label: 'ChatGPT-4o',    color: '#10A37F', role: 'gptGen'   },
    { label: 'Ai-Vector',     color: '#EA580C', role: 'aiArt'    },
    { label: 'Sub-Premiere',  color: '#D946EF', role: 'aiArt'    },
    { label: 'FeelChicken',   color: '#E11D48', role: 'cmsWeb'   },
    { label: 'JSX-Bridge',    color: '#6366F1', role: 'ideSwarm' },
    { label: 'Pr-BinLoader',  color: '#0284C7', role: 'binToTl'  },
    { label: 'EffectControls',color: '#7C3AED', role: 'prInsp'   },
    { label: 'Lumetri-Color', color: '#D97706', role: 'prWheels' },
    { label: 'Pr-Razor[C]',   color: '#DC2626', role: 'tlAhead'  },
    { label: 'Audio-14LUFS',  color: '#10B981', role: 'tlAudio'  }
  ];

  function pickTaskPt(role, t, rng) {
    const ls = getLayoutAt(t).rects;
    const aheadMin = Math.min(SEQ_DUR - 0.5, Math.max(0.15, t - 0.3));
    const aheadMax = Math.min(SEQ_DUR - 0.1, t + 5.2);
    const tx = () => secToScreenX(aheadMin + rng() * Math.max(0.3, aheadMax - aheadMin));

    let visSlots = 2;
    for (const bi of BIN_IMPORT_SCHEDULE) if (t >= bi.tImported) visSlots++;

    if (role === 'psCanvas') {
      return { x: ls.ps.x + 36 + rng() * (ls.ps.w - 195), y: ls.ps.y + 52 + rng() * (ls.ps.h - 70), c: rng() < 0.5 ? 'cross' : 'ew-resize', dx: (rng() - 0.5) * 34, dy: 0 };
    }
    if (role === 'psLayers') {
      return { x: ls.ps.x + ls.ps.w - 140 + rng() * 125, y: ls.ps.y + 65 + Math.floor(rng() * 6) * 28, c: 'arrow', dx: 0, dy: 0 };
    }
    if (role === 'gptGen') {
      return { x: ls.gpt.x + 25 + rng() * (ls.gpt.w - 50), y: ls.gpt.y + 45 + rng() * (ls.gpt.h - 65), c: rng() < 0.4 ? 'ibeam' : 'arrow', dx: 20, dy: 0 };
    }
    if (role === 'aiArt') {
      return { x: ls.ai.x + 30 + rng() * (ls.ai.w - 60), y: ls.ai.y + 45 + rng() * (ls.ai.h - 60), c: rng() < 0.45 ? 'cross' : 'ibeam', dx: (rng() - 0.5) * 28, dy: 0 };
    }
    if (role === 'cmsWeb') {
      return { x: ls.cms.x + 25 + rng() * (ls.cms.w - 50), y: ls.cms.y + 55 + rng() * (ls.cms.h - 70), c: rng() < 0.35 ? 'ibeam' : 'arrow', dx: 18, dy: 0 };
    }
    if (role === 'ideSwarm') {
      const w = rng() < 0.5 ? ls.ide : ls.swarm;
      return { x: w.x + 25 + rng() * (w.w - 50), y: w.y + 45 + rng() * (w.h - 60), c: 'arrow', dx: 16, dy: 0 };
    }
    if (role === 'prTools') {
      return { x: 16, y: 1488 + Math.floor(rng() * 8) * 27, c: 'arrow', dx: 0, dy: 0 };
    }
    if (role === 'binToTl') {
      if (rng() < 0.48) {
        const pt = binSlotScreenPt(Math.floor(rng() * visSlots));
        return { x: pt.x + (rng() - 0.5) * 38, y: pt.y + (rng() - 0.5) * 24, c: 'arrow', dx: 0, dy: 0, carry: true };
      }
      return { x: tx(), y: 1555 + rng() * 145, c: 'arrow', dx: 22, dy: 0, carry: true };
    }
    if (role === 'prInsp') {
      return { x: 792 + rng() * 265, y: 985 + rng() * 235, c: 'ew-resize', dx: (rng() - 0.5) * 46, dy: 0 };
    }
    if (role === 'prWheels') {
      return { x: 792 + rng() * 265, y: 1215 + rng() * 240, c: 'cross', dx: (rng() - 0.5) * 30, dy: (rng() - 0.5) * 20 };
    }
    if (role === 'tlAudio') {
      return { x: tx(), y: 1735 + rng() * 145, c: 'ew-resize', dx: (rng() - 0.5) * 34, dy: 0, mq: rng() < 0.2 };
    }
    return { x: tx(), y: 1532 + rng() * 195, c: rng() < 0.55 ? 'ew-resize' : 'arrow', dx: 36 + rng() * 58, dy: 18 + rng() * 24, mq: rng() < 0.25 };
  }

  const ROLE_POOL = [
    'psCanvas','psCanvas','psCanvas','psLayers','psLayers',
    'gptGen','gptGen','gptGen',
    'aiArt','aiArt','aiArt',
    'cmsWeb','cmsWeb','ideSwarm','ideSwarm',
    'prTools','binToTl','binToTl','binToTl',
    'prInsp','prInsp','prInsp','prWheels','prWheels',
    'tlAhead','tlAhead','tlAhead','tlAhead','tlAhead','tlAhead','tlAudio','tlAudio'
  ];

  const CARRY_KEYS = ['s1_bub', 's2_pray', 's3_chalk', 'q6_domeo', 's5_feast', 's6_endcard'];
  const TASK_CURSORS = [];
  for (let i = 0; i < 60; i++) {
    const rng = mulberry32(8123 + i * 6311);
    const spec = i < NAMED_BADGES.length ? NAMED_BADGES[i] : null;
    const role = spec ? spec.role : ROLE_POOL[i % ROLE_POOL.length];
    const wps = [];
    let f = -Math.floor(rng() * 20);
    let prev = pickTaskPt(role, 0, rng);
    while (f < TOTAL_FRAMES + 60) {
      const curT = Math.max(0, f / FPS);
      const nxt = pickTaskPt(role, curT, rng);
      const mDur = Math.floor(10 + rng() * 13);
      const hDur = Math.floor(6 + rng() * 9);
      wps.push({
        f0: f, f1: f + mDur, f2: f + mDur + hDur,
        x0: prev.x, y0: prev.y, x1: nxt.x, y1: nxt.y,
        arc: (rng() - 0.5) * 36,
        ctype: nxt.c,
        dx: nxt.dx || 0, dy: nxt.dy || 0,
        isMq: Boolean(nxt.mq && nxt.y > 1525),
        carry: Boolean(nxt.carry && nxt.y > 1500),
        carryKey: CARRY_KEYS[i % CARRY_KEYS.length]
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

  // Group 2: 60 Escort Swarm Cursors flanking `Lead-Agent` along every Top->Bottom Throw & Premiere Timeline Edit!
  function getHeroTrajectory(t) {
    const activeThrow = THROW_EVENTS.find(ev => ev.kind !== 'sub' && t >= ev.t0 && t <= ev.tLand);
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
    if (t >= SEQ_DUR - 0.65) {
      return { x: 1022, y: 932, clicking: true }; // Premiere `Quick Export` button!
    }
    const cycle = (t * 2.0) % 4;
    const pts = [
      winCenter(t, 'ps', 0.45, 0.52),
      binSlotScreenPt(Math.min(7, Math.floor(t / 6.2))),
      { x: secToScreenX(Math.min(SEQ_DUR - 0.3, t + 1.1)), y: 1640 },
      { x: 915, y: 1135 + Math.sin(t * 4) * 95 }
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
      angle, dist,
      wFreq: 5.5 + rng() * 6.0,
      wPhase: rng() * Math.PI * 2,
      scale: 0.74 + rng() * 0.14
    });
  }

  // ==================== 4. CANVAS CONTEXTS & TOP-APP RENDERERS ====================
  const psCtx   = document.getElementById('ps-cvs').getContext('2d');
  const aiCtx   = document.getElementById('ai-cvs').getContext('2d');
  const gptCtx  = document.getElementById('gpt-cvs').getContext('2d');
  const binCtx  = document.getElementById('pr-bin-cvs').getContext('2d');
  const inspCtx = document.getElementById('pr-insp-cvs').getContext('2d');
  const sc1     = document.getElementById('sc-1').getContext('2d');
  const sc2     = document.getElementById('sc-2').getContext('2d');
  const sc3     = document.getElementById('sc-3').getContext('2d');
  const tlCtx   = document.getElementById('tl-canvas').getContext('2d');
  const fxCtx   = document.getElementById('fx-canvas').getContext('2d');

  function drawSpriteCard(ctx, x, y, w, h, spKey, label, accent = '#38BDF8', alpha = 1.0) {
    const im = spImgs[spKey];
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = '#0F172A';
    ctx.beginPath(); ctx.roundRect(x, y, w, h, 7); ctx.fill();
    if (im && im.complete && im.naturalWidth > 0) {
      ctx.save();
      ctx.beginPath(); ctx.roundRect(x + 2, y + 2, w - 4, h - 4, 6); ctx.clip();
      ctx.drawImage(im, x + 2, y + 2, w - 4, h - 4);
      ctx.restore();
    }
    ctx.strokeStyle = accent;
    ctx.lineWidth = 2.0;
    ctx.beginPath(); ctx.roundRect(x, y, w, h, 7); ctx.stroke();
    if (label && w >= 85 && h >= 44) {
      ctx.fillStyle = 'rgba(9, 13, 24, 0.86)';
      ctx.beginPath(); ctx.roundRect(x + 5, y + 5, Math.min(w - 10, 128), 15, 4); ctx.fill();
      ctx.fillStyle = '#67E8F9';
      ctx.font = '700 7.8px Consolas, "Segoe UI"';
      ctx.fillText(label.slice(0, 20), x + 9, y + 15);
    }
    ctx.restore();
  }

  // 4A. Photoshop 2026 (`#win-ps` — Transparency Checkerboard + Exact Upcoming Sprite + Marching Ants + Curves HUD!)
  function drawPhotoshop(f, t) {
    const W = 430, H = 390;
    psCtx.fillStyle = '#191A1E'; psCtx.fillRect(0, 0, W, H);
    psCtx.fillStyle = '#24262C';
    for (let y = 16; y < H - 42; y += 14) {
      for (let x = 22; x < W - 22; x += 14) {
        if ((Math.floor(x / 14) + Math.floor(y / 14)) % 2 === 0) psCtx.fillRect(x, y, 14, 14);
      }
    }

    const nextImgEv = THROW_EVENTS.find(e => e.kind === 'img' && t <= e.tLand + 0.18) || THROW_EVENTS.filter(e => e.kind === 'img').slice(-1)[0];
    const spKey = nextImgEv ? nextImgEv.spKey : 's6_endcard';
    const psIdx = nextImgEv ? (nextImgEv.psIdx || 0) : 5;

    for (let k = 0; k < 6; k++) {
      document.getElementById(`psl-${k}`).className = (k === psIdx) ? 'ps-lyr sel' : 'ps-lyr';
    }

    const im = spImgs[spKey];
    let cw = 260, ch = 220;
    if (im && im.complete && im.naturalWidth > 0) {
      const r = Math.min(286 / im.naturalWidth, 272 / im.naturalHeight);
      cw = Math.max(120, im.naturalWidth * r);
      ch = Math.max(95, im.naturalHeight * r);
    }
    const cx = (W - 96 - cw) * 0.5 + 14, cy = (H - 46 - ch) * 0.5 + 8;
    drawSpriteCard(psCtx, cx, cy, cw, ch, spKey, nextImgEv ? nextImgEv.tlLbl : 'EndCard_38NDC.psd', '#31A8FF', 1.0);

    psCtx.strokeStyle = '#31A8FF'; psCtx.lineWidth = 1.6;
    psCtx.strokeRect(cx - 5, cy - 5, cw + 10, ch + 10);
    [[cx-5,cy-5],[cx+cw+5,cy-5],[cx-5,cy+ch+5],[cx+cw+5,cy+ch+5],[cx+cw*0.5,cy-5],[cx+cw*0.5,cy+ch+5]].forEach(([hx, hy]) => {
      psCtx.fillStyle = '#FFFFFF'; psCtx.fillRect(hx - 3.5, hy - 3.5, 7, 7);
      psCtx.strokeStyle = '#31A8FF'; psCtx.strokeRect(hx - 3.5, hy - 3.5, 7, 7);
    });

    psCtx.save();
    psCtx.setLineDash([5, 5]); psCtx.lineDashOffset = -(f * 1.2);
    psCtx.strokeStyle = '#FFFFFF'; psCtx.lineWidth = 1.3;
    psCtx.strokeRect(cx + 5, cy + 5, cw - 10, ch - 10);
    psCtx.restore();

    // Curves HUD
    const gx = W - 96, gy = 12, gw = 84, gh = 84;
    psCtx.fillStyle = 'rgba(20, 22, 28, 0.92)'; psCtx.fillRect(gx, gy, gw, gh);
    psCtx.strokeStyle = '#475569'; psCtx.strokeRect(gx, gy, gw, gh);
    psCtx.strokeStyle = '#38BDF8'; psCtx.lineWidth = 2;
    const bend = Math.sin(t * 5) * 10;
    psCtx.beginPath(); psCtx.moveTo(gx + 6, gy + gh - 6);
    psCtx.bezierCurveTo(gx + 26, gy + gh - 14 + bend, gx + 56, gy + 14 - bend, gx + gw - 6, gy + 6);
    psCtx.stroke();

    psCtx.fillStyle = '#2563EB';
    psCtx.beginPath(); psCtx.roundRect(52, H - 35, 232, 23, 5); psCtx.fill();
    psCtx.fillStyle = '#FFFFFF'; psCtx.font = '700 9px "Segoe UI"';
    psCtx.fillText('Tách Layer PSD ➔ Ném xuống Premiere ✓', 64, H - 20);

    psCtx.fillStyle = '#27272A';
    psCtx.beginPath(); psCtx.roundRect(292, H - 35, 84, 23, 5); psCtx.fill();
    psCtx.fillStyle = '#E4E4E7'; psCtx.fillText('Dynamic Link', 302, H - 20);
  }

  // 4B. Illustrator 2026 (`#win-ai` — Feel Chicken 20/11 Crest + Live Essential Graphics Vector Thrower!)
  function drawIllustrator(t) {
    const W = 510, H = 380;
    aiCtx.fillStyle = '#16171C'; aiCtx.fillRect(0, 0, W, H);
    const ax = 20, ay = 16, aw = W - 40, ah = H - 32;
    aiCtx.fillStyle = '#0F1420'; aiCtx.fillRect(ax, ay, aw, ah);
    aiCtx.strokeStyle = '#F59E0B'; aiCtx.lineWidth = 1.3; aiCtx.strokeRect(ax, ay, aw, ah);

    const keyList = THROW_EVENTS.filter(e => e.kind === 'key');
    const curKT = keyList.find(e => t <= e.sEnd) || keyList[keyList.length - 1];
    const parts = curKT.text.split(' ');
    const mid = Math.ceil(parts.length / 2);
    const l1 = parts.slice(0, mid).join(' ');
    const l2 = parts.slice(mid).join(' ');

    const cx = ax + aw * 0.5;
    const rad = 64 + Math.sin(t * 3.2) * 3;
    aiCtx.strokeStyle = 'rgba(245, 158, 11, 0.58)'; aiCtx.lineWidth = 2;
    aiCtx.beginPath(); aiCtx.arc(cx, ay + 104, rad, 0, Math.PI * 2); aiCtx.stroke();
    for (let k = 0; k < 8; k++) {
      const a = (k / 8) * Math.PI * 2 + t * 0.5;
      aiCtx.fillStyle = '#FFFFFF';
      aiCtx.fillRect(cx + Math.cos(a) * rad - 3, ay + 104 + Math.sin(a) * rad - 3, 6, 6);
    }

    aiCtx.save();
    aiCtx.textAlign = 'center';
    aiCtx.font = '900 25px "MontserratBlack", "Segoe UI"';
    aiCtx.strokeStyle = '#060913'; aiCtx.lineWidth = 7;
    aiCtx.strokeText(l1, cx, ay + 96); if (l2) aiCtx.strokeText(l2, cx, ay + 132);
    const gr = aiCtx.createLinearGradient(cx - 140, 0, cx + 140, 0);
    gr.addColorStop(0, '#FFF1F2'); gr.addColorStop(0.48, '#FB7185'); gr.addColorStop(1, '#FDE047');
    aiCtx.fillStyle = gr;
    aiCtx.fillText(l1, cx, ay + 96); if (l2) aiCtx.fillText(l2, cx, ay + 132);
    aiCtx.restore();

    const subList = THROW_EVENTS.filter(e => e.kind === 'sub' || e.kind === 'pill');
    const curSub = subList.find(e => t <= e.tLand + 0.35) || subList[subList.length - 1];
    const px = cx - 196, py = ay + 214, pw = 392, ph = 48;
    aiCtx.fillStyle = '#FFFFFF';
    aiCtx.beginPath(); aiCtx.roundRect(px, py, pw, ph, 24); aiCtx.fill();
    aiCtx.strokeStyle = '#00E5FF'; aiCtx.lineWidth = 2.4; aiCtx.stroke();
    aiCtx.fillStyle = '#0F172A';
    aiCtx.font = '800 13.8px "BeVietnamExtraBold", "Segoe UI"';
    aiCtx.textAlign = 'center';
    aiCtx.fillText(curSub.text.slice(0, 36), cx, py + 29);

    aiCtx.fillStyle = '#67E8F9'; aiCtx.font = '700 9.4px Consolas';
    aiCtx.fillText('⚡ ESSENTIAL GRAPHICS MOGRT ➔ NÉM XUỐNG PREMIERE', cx, py + 72);
    aiCtx.textAlign = 'left';
  }

  // 4C. ChatGPT Plus 4o (`#win-gpt` — Generates Feel Chicken 20/11 Classroom & Sauce Chicken Sources!)
  function drawChatGpt(t, f) {
    const W = 520, H = 390;
    gptCtx.fillStyle = '#212121'; gptCtx.fillRect(0, 0, W, H);
    gptCtx.fillStyle = '#171717'; gptCtx.fillRect(0, 0, 118, H);
    gptCtx.fillStyle = '#ECECEC'; gptCtx.font = '700 9.2px "Segoe UI"';
    gptCtx.fillText('◎ Feel Chicken 20/11', 8, 22);

    const activeB = Math.min(5, Math.floor((t / SEQ_DUR) * 6));
    GPT_SOURCE_PACKS.forEach((d, idx) => {
      const done = idx <= activeB;
      gptCtx.fillStyle = idx === activeB ? '#2F2F2F' : 'transparent';
      gptCtx.beginPath(); gptCtx.roundRect(5, 34 + idx * 26, 108, 22, 5); gptCtx.fill();
      gptCtx.fillStyle = done ? '#34D399' : '#9CA3AF'; gptCtx.font = '8px "Segoe UI"';
      gptCtx.fillText(`${done ? '✓' : '⟳'} ${d.binName.slice(0, 14)}`, 10, 48 + idx * 26);
    });

    const def = GPT_SOURCE_PACKS[activeB];
    const genU = clamp01(((t * 1.35) % 1.0) * 1.35);

    gptCtx.fillStyle = '#2F2F2F';
    gptCtx.beginPath(); gptCtx.roundRect(130, 10, 378, 40, 12); gptCtx.fill();
    gptCtx.fillStyle = '#ECECEC'; gptCtx.font = '8.6px "Segoe UI"';
    let l1 = '', l2 = '';
    for (const w of def.prompt.split(' ')) {
      if ((l1 + ' ' + w).trim().length <= 56 && !l2) l1 = (l1 + ' ' + w).trim();
      else l2 = (l2 + ' ' + w).trim();
    }
    gptCtx.fillText(l1, 142, 26); gptCtx.fillText(l2.slice(0, 62), 142, 40);

    gptCtx.fillStyle = '#34D399'; gptCtx.font = '700 8.8px "Segoe UI"';
    gptCtx.fillText(`✦ ChatGPT 4o đã tạo ${def.binName} ➔ Gắp sang Photoshop & Premiere`, 130, 68);

    const ix = 130, iy = 78, iw = 180, ih = 236;
    gptCtx.save();
    gptCtx.beginPath(); gptCtx.roundRect(ix, iy, iw, ih, 10); gptCtx.clip();
    const im = spImgs[def.key];
    if (im && im.complete && im.naturalWidth > 0) {
      const bl = (1 - genU) * 10;
      gptCtx.filter = bl > 0.4 ? `blur(${bl.toFixed(1)}px)` : 'none';
      gptCtx.drawImage(im, ix, iy, iw, ih);
      gptCtx.filter = 'none';
    }
    gptCtx.restore();
    gptCtx.strokeStyle = '#10B981'; gptCtx.lineWidth = 1.6;
    gptCtx.beginPath(); gptCtx.roundRect(ix, iy, iw, ih, 10); gptCtx.stroke();

    for (let k = 0; k < 4; k++) {
      const bi = (activeB + k + 1) % 6;
      const gx = 322 + (k % 2) * 94, gy = 78 + Math.floor(k / 2) * 120;
      const gim = spImgs[GPT_SOURCE_PACKS[bi].key];
      gptCtx.save();
      gptCtx.beginPath(); gptCtx.roundRect(gx, gy, 86, 112, 7); gptCtx.clip();
      if (gim && gim.complete && gim.naturalWidth > 0) gptCtx.drawImage(gim, gx, gy, 86, 112);
      gptCtx.restore();
      gptCtx.strokeStyle = '#3F3F46'; gptCtx.beginPath(); gptCtx.roundRect(gx, gy, 86, 112, 7); gptCtx.stroke();
    }

    const nextP = GPT_SOURCE_PACKS[(activeB + 1) % 6].prompt;
    const typed = Math.floor((t * 50) % (nextP.length + 10));
    gptCtx.fillStyle = '#2F2F2F';
    gptCtx.beginPath(); gptCtx.roundRect(130, 324, 378, 52, 14); gptCtx.fill();
    gptCtx.fillStyle = '#ECECEC'; gptCtx.font = '8.6px "Segoe UI"';
    gptCtx.fillText(nextP.slice(0, Math.min(58, typed)) + (f % 20 < 10 ? '▌' : ''), 142, 344);
    gptCtx.fillStyle = '#93C5FD'; gptCtx.font = '600 8px "Segoe UI"';
    gptCtx.fillText('🎨 Tạo Source 9:16   ·   ⚡ Tự động gắp xuống Project Bin Premiere', 142, 365);
  }

  // ==================== 5. PREMIERE PRO `Project: FeelChicken_2011` PROGRESSIVE BIN (`#pr-bin-cvs`) ====================
  function drawPremiereProjectBin(t) {
    const W = 294, H = 499;
    binCtx.fillStyle = '#1D1D20'; binCtx.fillRect(0, 0, W, H);

    const anyImporting = BIN_IMPORT_SCHEDULE.some(bi => t >= bi.tThrow0 && t <= bi.tImported);
    binCtx.fillStyle = '#141417';
    binCtx.beginPath(); binCtx.roundRect(10, 8, 188, 21, 3); binCtx.fill();
    binCtx.strokeStyle = anyImporting ? '#4B9CFF' : '#2E2E35';
    binCtx.stroke();
    binCtx.fillStyle = '#8E8E98'; binCtx.font = '8px "Segoe UI"';
    binCtx.fillText('🔍 Filter FeelChicken_2011...', 16, 22);

    binCtx.fillStyle = anyImporting ? '#1473E6' : '#2A2A30';
    binCtx.beginPath(); binCtx.roundRect(204, 8, 80, 21, 3); binCtx.fill();
    binCtx.fillStyle = '#FFFFFF'; binCtx.font = '700 8px "Segoe UI"';
    binCtx.fillText(anyImporting ? '⬇ Importing' : '⊞ Icon View', 214, 22);

    const baseTiles = [
      { name: 'CamA_AnhKhang.mp4', ext: 'MP4', img: stripImgs[2],  tIn: 0.0,   tAdded: 0.05 },
      { name: 'Conan_Master_VO.wav',ext: 'WAV', img: stripImgs[10], tIn: 0.001, tAdded: 0.05 }
    ];
    for (const bi of BIN_IMPORT_SCHEDULE) {
      baseTiles.push({ name: bi.name, ext: bi.ext, img: spImgs[bi.spKey], tIn: bi.tImported, tAdded: bi.tAdded });
    }

    const visTiles = baseTiles.filter(ti => t >= ti.tIn).sort((a, b) => a.tIn - b.tIn);
    binCtx.fillStyle = '#BDBDC4'; binCtx.font = '700 8.4px "Segoe UI"';
    binCtx.fillText(`📁 01_Master_Assets (${visTiles.length} items)`, 12, 45);

    visTiles.forEach((ti, visIdx) => {
      const col = visIdx % 2, row = Math.floor(visIdx / 2);
      const x = 12 + col * 138, y = 56 + row * 102, w = 128, h = 76;
      const age = t - ti.tIn;
      const justLanded = ti.tIn > 0.01 && age < 0.50;

      binCtx.save();
      if (ti.tIn > 0.01 && age < 0.18) {
        const sc = lerp(0.74, 1.04, fastEase(age / 0.18));
        binCtx.translate(x + w * 0.5, y + h * 0.5);
        binCtx.scale(sc, sc);
        binCtx.translate(-(x + w * 0.5), -(y + h * 0.5));
      }

      binCtx.fillStyle = '#121215';
      binCtx.beginPath(); binCtx.roundRect(x, y, w, h, 4); binCtx.fill();
      if (ti.img && ti.img.complete && ti.img.naturalWidth > 0) {
        binCtx.save();
        binCtx.beginPath(); binCtx.roundRect(x + 2, y + 2, w - 4, h - 4, 3); binCtx.clip();
        const iw = ti.img.naturalWidth, ih = ti.img.naturalHeight;
        const scale = Math.max(w / iw, h / ih);
        binCtx.drawImage(ti.img, x + (w - iw * scale) * 0.5, y + (h - ih * scale) * 0.5, iw * scale, ih * scale);
        binCtx.restore();
      }

      // Authentic Premiere Pro Media Type Pill (`PSD` purple / `MP4` blue / `WAV` green)
      const tagCol = ti.ext === 'PSD' ? '#7C3AED' : ti.ext === 'WAV' ? '#059669' : '#1473E6';
      binCtx.fillStyle = tagCol;
      binCtx.beginPath(); binCtx.roundRect(x + 5, y + 5, 28, 13, 2); binCtx.fill();
      binCtx.fillStyle = '#FFFFFF'; binCtx.font = '700 7.2px Consolas';
      binCtx.fillText(ti.ext, x + 9, y + 14);

      if (t >= ti.tAdded) {
        // Premiere blue "Used in Sequence" badge
        binCtx.fillStyle = 'rgba(20, 115, 230, 0.92)';
        binCtx.beginPath(); binCtx.roundRect(x + w - 46, y + h - 16, 42, 13, 2); binCtx.fill();
        binCtx.fillStyle = '#FFFFFF'; binCtx.font = '700 6.8px "Segoe UI"';
        binCtx.fillText('🎞 In Seq', x + w - 43, y + h - 7);
      }

      binCtx.strokeStyle = justLanded ? '#00E5FF' : '#32323A';
      binCtx.lineWidth = justLanded ? 2.2 : 1.0;
      binCtx.beginPath(); binCtx.roundRect(x, y, w, h, 4); binCtx.stroke();

      binCtx.fillStyle = '#D4D4D8'; binCtx.font = '7.8px "Segoe UI"';
      binCtx.fillText(ti.name.slice(0, 20), x + 2, y + h + 13);
      binCtx.restore();
    });

    if (visTiles.length < 8) {
      const col = visTiles.length % 2, row = Math.floor(visTiles.length / 2);
      const dx = 12 + col * 138, dy = 56 + row * 102;
      binCtx.strokeStyle = anyImporting ? '#00E5FF' : '#383842';
      binCtx.lineWidth = 1.4; binCtx.setLineDash([4, 3]);
      binCtx.beginPath(); binCtx.roundRect(dx, dy, 128, 76, 4); binCtx.stroke();
      binCtx.setLineDash([]);
      binCtx.fillStyle = anyImporting ? '#00E5FF' : '#7C7C88';
      binCtx.font = '600 7.8px "Segoe UI"'; binCtx.textAlign = 'center';
      binCtx.fillText(anyImporting ? '⬇ Dropping Asset...' : '+ Import Media', dx + 64, dy + 42);
      binCtx.textAlign = 'left';
    }

    // Premiere Bin bottom status footer
    binCtx.fillStyle = '#161619'; binCtx.fillRect(0, H - 26, W, 26);
    binCtx.fillStyle = '#9999FF'; binCtx.font = '700 7.8px "Segoe UI"';
    binCtx.fillText('⚡ Dynamic Link: Ps + Ai Connected', 10, H - 9);
    binCtx.fillStyle = '#34D399'; binCtx.fillText('60.00 fps', W - 52, H - 9);
  }

  // ==================== 6. PREMIERE PRO LIVE SCOPES & CYCLING INSPECTOR (`Effect Controls` / `Lumetri` / `Essential Graphics`) ====================
  function drawPremiereScopes(t, vAmp) {
    sc1.fillStyle = '#08080A'; sc1.fillRect(0, 0, 64, 140);
    sc1.strokeStyle = 'rgba(74,222,128,0.80)'; sc1.lineWidth = 1.2; sc1.beginPath();
    for (let x = 0; x < 64; x += 2) {
      const y = 72 + Math.sin(x * 0.22 + t * 5.5) * 24 + Math.cos(x * 0.48 - t * 3.5) * 14 * (0.55 + vAmp);
      if (x === 0) sc1.moveTo(x, y); else sc1.lineTo(x, y);
    }
    sc1.stroke();

    sc2.fillStyle = '#08080A'; sc2.fillRect(0, 0, 64, 140);
    const cols = ['rgba(248,113,113,0.82)', 'rgba(74,222,128,0.82)', 'rgba(96,165,250,0.82)'];
    for (let c = 0; c < 3; c++) {
      sc2.fillStyle = cols[c];
      for (let i = 0; i < 8; i++) {
        const bh = 28 + Math.abs(Math.sin(t * 4.4 + c * 1.7 + i * 0.65)) * 68;
        sc2.fillRect(c * 21 + 3 + i * 2.1, 126 - bh, 1.5, bh);
      }
    }

    sc3.fillStyle = '#08080A'; sc3.fillRect(0, 0, 64, 140);
    sc3.strokeStyle = '#27272F'; sc3.beginPath(); sc3.arc(32, 76, 25, 0, Math.PI * 2); sc3.stroke();
    sc3.strokeStyle = 'rgba(251,191,36,0.75)'; sc3.beginPath(); sc3.moveTo(32, 76); sc3.lineTo(18, 52); sc3.stroke();
    sc3.fillStyle = 'rgba(253,186,116,0.72)';
    for (let k = 0; k < 14; k++) {
      const a = -2.1 + Math.sin(t * 3.2 + k) * 0.28, r = 6 + (k / 14) * 16;
      sc3.fillRect(32 + Math.cos(a) * r, 76 + Math.sin(a) * r, 2, 2);
    }
  }

  function drawPremiereInspector(t) {
    const W = 300, H = 499;
    inspCtx.fillStyle = '#202024'; inspCtx.fillRect(0, 0, W, H);

    // Rapidly cycle across 4 authentic Premiere Pro panels every ~1.25s + sync Workspace tabs!
    const modeIdx = Math.floor(t / 1.25) % 4;
    const topTab = modeIdx === 0 ? 0 : (modeIdx === 1 || modeIdx === 2) ? 1 : 2;
    for (let k = 0; k < 3; k++) {
      document.getElementById(`pit-${k}`).className = (k === topTab) ? 'on' : '';
    }
    const wsActive = modeIdx === 0 ? 0 : (modeIdx === 1 || modeIdx === 2) ? 1 : 3;
    for (let w = 0; w < 4; w++) {
      document.getElementById(`pws-${w}`).className = (w === wsActive) ? 'pr-ws on' : 'pr-ws';
    }

    // Mode 0: Premiere Pro `Effect Controls` (Video -> Motion Position/Scale/Rotation + Velocity Bezier Graph!)
    if (modeIdx === 0) {
      inspCtx.fillStyle = '#18181C'; inspCtx.fillRect(0, 0, W, 25);
      inspCtx.fillStyle = '#4B9CFF'; inspCtx.font = '700 8.5px "Segoe UI"';
      inspCtx.fillText('▼ fx  Motion  ·  KiemTraMieng_2011', 10, 16);

      const posX = Math.round(540 + Math.sin(t * 5) * 14);
      const posY = Math.round(960 + Math.cos(t * 4.2) * 28);
      const scaleV = (100 + Math.abs(Math.sin(t * 3.5)) * 12).toFixed(1);
      const rotV = (Math.sin(t * 6) * 2.4).toFixed(1);

      const rows = [
        ['⏱ Position',      `${posX}.0,  ${posY}.0`],
        ['⏱ Scale',         `${scaleV} %`],
        ['⏱ Rotation',      `${rotV}°`],
        ['⏱ Opacity',       '100.0 %'],
        ['⏱ Anti-flicker',  '0.15']
      ];
      rows.forEach(([lbl, val], idx) => {
        const y = 44 + idx * 32;
        inspCtx.fillStyle = '#D4D4D8'; inspCtx.font = '8.2px "Segoe UI"';
        inspCtx.fillText(lbl, 12, y);
        inspCtx.fillStyle = '#4B9CFF'; inspCtx.font = '700 8.4px Consolas';
        inspCtx.fillText(val, 148, y);
        // Keyframe diamonds on mini-track right side
        for (let d = 0; d < 3; d++) {
          const kx = 236 + d * 20;
          inspCtx.save(); inspCtx.translate(kx, y - 3); inspCtx.rotate(Math.PI / 4);
          inspCtx.fillStyle = d === 1 ? '#4B9CFF' : '#A1A1AA';
          inspCtx.fillRect(-3, -3, 6, 6);
          inspCtx.restore();
        }
        inspCtx.strokeStyle = '#2B2B32';
        inspCtx.beginPath(); inspCtx.moveTo(10, y + 10); inspCtx.lineTo(W - 10, y + 10); inspCtx.stroke();
      });

      // Speed / Bezier Keyframe Velocity Editor
      inspCtx.fillStyle = '#141418'; inspCtx.beginPath(); inspCtx.roundRect(12, 214, W - 24, 152, 5); inspCtx.fill();
      inspCtx.strokeStyle = '#2F2F38'; inspCtx.stroke();
      inspCtx.fillStyle = '#9999FF'; inspCtx.font = '700 8px "Segoe UI"';
      inspCtx.fillText('Bezier Spatial & Velocity Graph (Ease Out Back)', 20, 232);

      const shift = Math.sin(t * 4.5) * 22;
      inspCtx.strokeStyle = '#4B9CFF'; inspCtx.lineWidth = 2.2;
      inspCtx.beginPath(); inspCtx.moveTo(24, 346);
      inspCtx.bezierCurveTo(96 + shift, 346, 106 + shift, 252, 154, 252);
      inspCtx.bezierCurveTo(202 - shift, 252, 212 - shift, 346, W - 24, 346);
      inspCtx.stroke();

      const gx = 24 + ((t * 1.4) % 1) * (W - 48);
      inspCtx.strokeStyle = '#EF4444'; inspCtx.lineWidth = 1.2;
      inspCtx.beginPath(); inspCtx.moveTo(gx, 244); inspCtx.lineTo(gx, 356); inspCtx.stroke();

      inspCtx.fillStyle = '#26262E'; inspCtx.beginPath(); inspCtx.roundRect(12, 380, W - 24, 96, 5); inspCtx.fill();
      inspCtx.fillStyle = '#34D399'; inspCtx.font = '700 8.3px "Segoe UI"';
      inspCtx.fillText('▼ fx  Ultra Key / RVM Matte  ·  Active', 20, 400);
      inspCtx.fillStyle = '#A1A1AA'; inspCtx.font = '7.8px "Segoe UI"';
      inspCtx.fillText('Pedestal: 98%   ·   Choke: 1.2px   ·   Soften: 1.1px', 20, 422);
      inspCtx.fillText('Audio Loudness Radar: -14.0 LUFS (Broadcast)', 20, 444);
      return;
    }

    // Mode 1: Premiere Pro `Lumetri Color — Basic Correction`
    if (modeIdx === 1) {
      inspCtx.fillStyle = '#18181C'; inspCtx.fillRect(0, 0, W, 25);
      inspCtx.fillStyle = '#FACC15'; inspCtx.font = '700 8.5px "Segoe UI"';
      inspCtx.fillText('▼ Lumetri Color  ·  FeelChicken_WarmFood.cube', 10, 16);

      const sliders = [
        { nm: 'Temperature', c1: '#3B82F6', c2: '#F59E0B', off: 0.14 + Math.sin(t * 5.5) * 0.12 },
        { nm: 'Tint',        c1: '#22C55E', c2: '#EC4899', off: 0.05 + Math.cos(t * 4.8) * 0.10 },
        { nm: 'Exposure',    c1: '#27272A', c2: '#F4F4F5', off: 0.08 + Math.sin(t * 6.2) * 0.08 },
        { nm: 'Contrast',    c1: '#27272A', c2: '#F4F4F5', off: 0.18 + Math.cos(t * 5.0) * 0.09 },
        { nm: 'Highlights',  c1: '#27272A', c2: '#FDE047', off: -0.08 + Math.sin(t * 4.4) * 0.08 },
        { nm: 'Shadows',     c1: '#18181B', c2: '#93C5FD', off: 0.11 + Math.cos(t * 5.6) * 0.08 },
        { nm: 'Saturation',  c1: '#52525B', c2: '#EF4444', off: 0.22 + Math.sin(t * 6.5) * 0.09 }
      ];
      sliders.forEach((s, idx) => {
        const y = 56 + idx * 60;
        inspCtx.fillStyle = '#D4D4D8'; inspCtx.font = '8px "Segoe UI"'; inspCtx.fillText(s.nm, 14, y);
        const lg = inspCtx.createLinearGradient(14, 0, 228, 0);
        lg.addColorStop(0, s.c1); lg.addColorStop(1, s.c2);
        inspCtx.fillStyle = lg; inspCtx.fillRect(14, y + 10, 214, 4);
        inspCtx.fillStyle = '#FFFFFF';
        inspCtx.beginPath(); inspCtx.arc(121 + s.off * 185, y + 12, 5, 0, Math.PI * 2); inspCtx.fill();
        inspCtx.fillStyle = '#151519'; inspCtx.beginPath(); inspCtx.roundRect(238, y + 2, 48, 18, 3); inspCtx.fill();
        inspCtx.fillStyle = '#4B9CFF'; inspCtx.font = '700 8px Consolas';
        const v = (s.off * 45).toFixed(1);
        inspCtx.fillText((s.off >= 0 ? '+' : '') + v, 244, y + 14);
      });
      return;
    }

    // Mode 2: Premiere Pro `Lumetri Color — Color Wheels & RGB Curves`
    if (modeIdx === 2) {
      inspCtx.fillStyle = '#18181C'; inspCtx.fillRect(0, 0, W, 25);
      inspCtx.fillStyle = '#9999FF'; inspCtx.font = '700 8.5px "Segoe UI"';
      inspCtx.fillText('▼ Color Wheels & Match  ·  RGB Curves', 10, 16);

      const wheels = [
        { nm: 'Shadows',    x: 56,  y: 108 },
        { nm: 'Midtones',   x: 150, y: 108 },
        { nm: 'Highlights', x: 244, y: 108 }
      ];
      wheels.forEach((w, idx) => {
        inspCtx.fillStyle = '#D4D4D8'; inspCtx.font = '600 7.8px "Segoe UI"'; inspCtx.textAlign = 'center';
        inspCtx.fillText(w.nm, w.x, w.y - 46);
        for (let a = 0; a < 36; a++) {
          inspCtx.strokeStyle = `hsl(${a * 10}, 85%, 55%)`; inspCtx.lineWidth = 5.5;
          inspCtx.beginPath(); inspCtx.arc(w.x, w.y, 35, (a / 36) * Math.PI * 2, ((a + 1.25) / 36) * Math.PI * 2); inspCtx.stroke();
        }
        inspCtx.fillStyle = '#141418'; inspCtx.beginPath(); inspCtx.arc(w.x, w.y, 30, 0, Math.PI * 2); inspCtx.fill();
        const px = w.x + Math.cos(t * 5 + idx * 1.9) * 9, py = w.y + Math.sin(t * 6 + idx * 1.4) * 9;
        inspCtx.strokeStyle = '#FFFFFF'; inspCtx.lineWidth = 1.6; inspCtx.beginPath(); inspCtx.arc(px, py, 4, 0, Math.PI * 2); inspCtx.stroke();
      });
      inspCtx.textAlign = 'left';

      // RGB Curves Box
      const gx = 16, gy = 186, gw = W - 32, gh = 282;
      inspCtx.fillStyle = '#121216'; inspCtx.fillRect(gx, gy, gw, gh);
      inspCtx.strokeStyle = '#2C2C36'; inspCtx.strokeRect(gx, gy, gw, gh);
      [
        { col: '#FFFFFF', b: Math.sin(t * 5.2) * 18 },
        { col: '#EF4444', b: Math.cos(t * 4.6) * 22 },
        { col: '#38BDF8', b: -Math.sin(t * 4.2) * 16 }
      ].forEach((c) => {
        inspCtx.strokeStyle = c.col; inspCtx.lineWidth = 1.8;
        inspCtx.beginPath(); inspCtx.moveTo(gx, gy + gh);
        inspCtx.bezierCurveTo(gx + gw * 0.33, gy + gh * 0.68 + c.b, gx + gw * 0.67, gy + gh * 0.30 - c.b, gx + gw, gy);
        inspCtx.stroke();
      });
      return;
    }

    // Mode 3: Premiere Pro `Essential Graphics — Edit Kawaii Layer Stack`
    inspCtx.fillStyle = '#18181C'; inspCtx.fillRect(0, 0, W, 25);
    inspCtx.fillStyle = '#F472B6'; inspCtx.font = '700 8.5px "Segoe UI"';
    inspCtx.fillText('▼ Essential Graphics  ·  Edit Layer Stack', 10, 16);

    const activeEvs = THROW_EVENTS.filter(e => t >= e.t0).slice(-5).reverse();
    activeEvs.forEach((ev, idx) => {
      const y = 38 + idx * 42;
      inspCtx.fillStyle = idx === 0 ? '#2D3250' : '#18181D';
      inspCtx.beginPath(); inspCtx.roundRect(12, y, W - 24, 36, 4); inspCtx.fill();
      inspCtx.strokeStyle = idx === 0 ? '#4B9CFF' : '#2E2E36'; inspCtx.stroke();
      inspCtx.fillStyle = '#FFFFFF'; inspCtx.font = '700 8px "Segoe UI"';
      inspCtx.fillText(`👁  ${(ev.text || ev.tlLbl || 'Graphic_Layer').slice(0, 28)}`, 20, y + 16);
      inspCtx.fillStyle = '#9CA3AF'; inspCtx.font = '7.4px Consolas';
      inspCtx.fillText(`Agent: ${ev.agent} · SafeZone PASS`, 20, y + 29);
    });

    inspCtx.fillStyle = '#16161B'; inspCtx.beginPath(); inspCtx.roundRect(12, 260, W - 24, 218, 5); inspCtx.fill();
    inspCtx.fillStyle = '#E5E7EB'; inspCtx.font = '700 8.2px "Segoe UI"';
    inspCtx.fillText('Text & Stroke Appearance (5-Stop Kawaii)', 20, 280);
    inspCtx.fillStyle = '#FDE047'; inspCtx.fillRect(20, 294, 48, 18);
    inspCtx.fillStyle = '#FB7185'; inspCtx.fillRect(76, 294, 48, 18);
    inspCtx.fillStyle = '#34D399'; inspCtx.fillRect(132, 294, 48, 18);
    inspCtx.fillStyle = '#FFFFFF'; inspCtx.fillRect(188, 294, 48, 18);
    inspCtx.fillStyle = '#9CA3AF'; inspCtx.font = '8px "Segoe UI"';
    inspCtx.fillText('Font: Montserrat Black / Baloo 2 ExtraBold', 20, 334);
    inspCtx.fillText('Outer Stroke: 12px #FFFFFF  ·  Shadow: 68%', 20, 356);
    inspCtx.fillText('Align & Transform: Center Safe Zone 9:16 ✓', 20, 378);
    inspCtx.fillStyle = '#1473E6'; inspCtx.beginPath(); inspCtx.roundRect(20, 400, W - 40, 26, 4); inspCtx.fill();
    inspCtx.fillStyle = '#FFFFFF'; inspCtx.font = '700 8.4px "Segoe UI"';
    inspCtx.fillText('✓ Auto-Sync Master Style Across 36 Clips', 42, 417);
  }

  // ==================== 7. PHOTO-AUTHENTIC PREMIERE PRO 7-TRACK TIMELINE (`#tl-canvas`, 1046×416) ====================
  function drawPremiereTimeline(t, marquees) {
    const W = 1046, H = 416;
    tlCtx.fillStyle = '#17171A'; tlCtx.fillRect(0, 0, W, H);

    // Cycle active Premiere Tool in left Tools Dock (`Selection V`, `Track Select A`, `Ripple B`, `Razor C`, `Slip Y`, `Pen P`, `Type T`)
    const activeTool = Math.floor(t * 2.4) % 8;
    for (let ti = 0; ti < 8; ti++) {
      document.getElementById(`ptl-${ti}`).className = (ti === activeTool || ti === 0) ? 'pr-tbtn on' : 'pr-tbtn';
    }

    // Timecode Ruler (`00:00:00:00` .. `00:00:48:00`)
    tlCtx.fillStyle = '#202025'; tlCtx.fillRect(0, 0, W, 24);
    tlCtx.font = '8.6px Consolas, monospace'; tlCtx.fillStyle = '#9CA3AF';
    for (let s = 0; s <= 48; s += 6) {
      const sx = secToCanvasX(s);
      tlCtx.strokeStyle = '#52525B'; tlCtx.beginPath(); tlCtx.moveTo(sx, 12); tlCtx.lineTo(sx, 24); tlCtx.stroke();
      tlCtx.fillText(`00:00:${String(s).padStart(2, '0')}:00`, sx - 24, 10);
    }

    // 7 Authentic Premiere Pro Track Headers (matches user's beloved screenshot #1!)
    const trRows = [
      { id: 'V4', lbl: 'V4 [Ae Link]',  y: 27,  h: 38, v: true,  badge: '#6D28D9' },
      { id: 'V3', lbl: 'V3 Graphics',   y: 68,  h: 38, v: true,  badge: '#9333EA' },
      { id: 'V2', lbl: 'V2 Ps/B-Roll',  y: 109, h: 46, v: true,  badge: '#1D4ED8' },
      { id: 'V1', lbl: 'V1 Anh Khang',  y: 158, h: 62, v: true,  badge: '#2563EB' },
      { id: 'A1', lbl: 'A1 Voiceover',  y: 225, h: 58, v: false, badge: '#059669' },
      { id: 'A2', lbl: 'A2 Conan BGM',  y: 286, h: 46, v: false, badge: '#0D9488' },
      { id: 'A3', lbl: 'A3 Throw SFX',  y: 335, h: 44, v: false, badge: '#0891B2' }
    ];
    for (const tr of trRows) {
      tlCtx.fillStyle = '#1D1D22'; tlCtx.fillRect(HDR_W, tr.y, W - HDR_W, tr.h);
      tlCtx.fillStyle = '#25252B'; tlCtx.fillRect(0, tr.y, HDR_W - 2, tr.h);
      tlCtx.fillStyle = tr.badge; tlCtx.fillRect(3, tr.y + 4, 20, tr.h - 8);
      tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = '700 7.6px Consolas';
      tlCtx.fillText(tr.id, 6.5, tr.y + tr.h * 0.57);
      tlCtx.fillStyle = '#E4E4E7'; tlCtx.font = '700 8.3px "Segoe UI"';
      tlCtx.fillText(tr.lbl.slice(3), 27, tr.y + tr.h * 0.57);
    }

    let builtClips = 3;
    const v1X = secToCanvasX(0);
    const v1BuiltSec = Math.min(SEQ_DUR, t + 5.2);
    const v1W = Math.max(36, secToCanvasX(v1BuiltSec) - v1X);
    const fullSeqW = secToCanvasX(SEQ_DUR) - v1X;

    // V1 Main Camera Track (`CamA_AnhKhang_Master.mp4` + 24 Filmstrip Thumbnails + Segment Cut Lines!)
    tlCtx.save();
    tlCtx.beginPath(); tlCtx.rect(v1X, 160, v1W, 58); tlCtx.clip();
    tlCtx.fillStyle = '#2C5282'; tlCtx.fillRect(v1X, 160, fullSeqW, 58);
    const cellW = fullSeqW / 24;
    for (let i = 0; i < 24; i++) {
      const im = stripImgs[i];
      if (im && im.complete && im.naturalWidth > 0) tlCtx.drawImage(im, v1X + i * cellW, 175, cellW + 0.8, 43);
    }
    tlCtx.fillStyle = 'rgba(18, 36, 68, 0.90)'; tlCtx.fillRect(v1X, 160, fullSeqW, 15);
    const segStarts = [0, 4.57, 13.47, 21.97, 27.93, 36.83, 42.77, 44.57];
    const segNames  = ['S1_Skit.mp4', 'S2_AnhKhang.mp4', 'S3_2011_Prog.mp4', 'S4_QuizJar.mp4', 'S5_Gifts_RVM.mp4', 'S6A_Outro.mp4', 'S6B.mp4', 'S6C_38NDC.mp4'];
    segStarts.forEach((st, idx) => {
      const sx = secToCanvasX(st);
      tlCtx.strokeStyle = '#93C5FD'; tlCtx.lineWidth = 1.2;
      tlCtx.beginPath(); tlCtx.moveTo(sx, 160); tlCtx.lineTo(sx, 218); tlCtx.stroke();
      tlCtx.fillStyle = '#E0F2FE'; tlCtx.font = '700 7.6px Consolas';
      tlCtx.fillText(segNames[idx], sx + 4, 170.5);
    });
    tlCtx.restore();
    tlCtx.strokeStyle = '#60A5FA'; tlCtx.lineWidth = 1.3; tlCtx.strokeRect(v1X, 160, v1W, 58);

    // Thrown V2, V3, V4 Clips snap onto Premiere Timeline right as each Throw lands!
    for (const ev of THROW_EVENTS) {
      if (!ev.tlTrack || t < ev.tLand - 0.05) continue;
      builtClips++;
      const growU = minJerk(Math.min(1, (t - (ev.tLand - 0.05)) / 0.30));
      const curEnd = lerp(ev.tLand + 0.40, ev.sEnd, growU);
      const x = secToCanvasX(ev.tLand), w = Math.max(10, secToCanvasX(curEnd) - x);

      if (ev.tlTrack === 'V2') {
        tlCtx.fillStyle = '#1D63DC'; tlCtx.fillRect(x, 111, w, 42);
        tlCtx.strokeStyle = '#93C5FD'; tlCtx.lineWidth = 1.2; tlCtx.strokeRect(x, 111, w, 42);
        if (growU < 1) { tlCtx.fillStyle = '#FACC15'; tlCtx.fillRect(x + w - 3, 111, 3, 42); }
        if (w > 24) {
          tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x + 3, 111, w - 6, 42); tlCtx.clip();
          tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = '700 8px "Segoe UI"';
          tlCtx.fillText(ev.tlLbl || 'Broll_Clip', x + 5, 135);
          tlCtx.restore();
        }
      } else if (ev.tlTrack === 'V3') {
        const activeNow = t >= ev.tLand && t <= ev.sEnd;
        tlCtx.fillStyle = activeNow ? '#C026D3' : '#9333EA';
        tlCtx.fillRect(x, 70, w, 34);
        tlCtx.strokeStyle = '#F5D0FE'; tlCtx.lineWidth = 1.1; tlCtx.strokeRect(x, 70, w, 34);
        if (w > 22) {
          tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x + 3, 70, w - 6, 34); tlCtx.clip();
          tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = '7.6px Consolas';
          tlCtx.fillText(ev.tlLbl || ev.text || 'Caption', x + 4, 90);
          tlCtx.restore();
        }
      } else if (ev.tlTrack === 'V4') {
        tlCtx.fillStyle = '#7E22CE'; tlCtx.fillRect(x, 29, w, 34);
        tlCtx.strokeStyle = '#DDD6FE'; tlCtx.lineWidth = 1.2; tlCtx.strokeRect(x, 29, w, 34);
        if (w > 26) {
          tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x + 3, 29, w - 6, 34); tlCtx.clip();
          tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = '700 8px "Segoe UI"';
          tlCtx.fillText(ev.tlLbl || ev.text || '[Ae] Comp', x + 5, 49);
          tlCtx.restore();
        }
      }
    }

    // A1 Voiceover Caribbean-Green Waveform (`VO_AnhKhang_Master_-14LUFS.wav`)
    tlCtx.fillStyle = '#165B45'; tlCtx.fillRect(v1X, 227, v1W, 54);
    tlCtx.strokeStyle = '#4ADE80'; tlCtx.lineWidth = 1.1; tlCtx.strokeRect(v1X, 227, v1W, 54);
    const wf = meta.waveform || [];
    const bStep = fullSeqW / Math.max(1, wf.length);
    for (let b = 0; b < wf.length; b++) {
      const bx = v1X + b * bStep;
      if (bx > v1X + v1W - 2) break;
      const bh = Math.max(2, wf[b] * 40);
      tlCtx.fillStyle = ((b / wf.length) * SEQ_DUR <= t) ? '#A7F3D0' : '#34D399';
      tlCtx.fillRect(bx, 256 - bh * 0.5, Math.max(1.2, bStep - 0.7), bh);
    }
    tlCtx.fillStyle = '#D1FAE5'; tlCtx.font = '700 7.6px Consolas';
    tlCtx.fillText('VO_AnhKhang_KiemTraMieng [-14.0 LUFS]', v1X + 5, 238);

    // A2 Detective Conan BGM Track with Signature Yellow Ducking Rubberband Curve!
    const bgmW = Math.max(36, secToCanvasX(Math.min(SEQ_DUR, t + 4.4)) - v1X);
    tlCtx.fillStyle = '#154E63'; tlCtx.fillRect(v1X, 288, bgmW, 42);
    tlCtx.strokeStyle = '#38BDF8'; tlCtx.strokeRect(v1X, 288, bgmW, 42);
    tlCtx.strokeStyle = '#FACC15'; tlCtx.lineWidth = 1.6;
    tlCtx.beginPath();
    for (let i = 0; i <= 96; i++) {
      const st = (i / 96) * SEQ_DUR;
      const dx = secToCanvasX(st);
      if (dx > v1X + bgmW) break;
      const ei = Math.min(TOTAL_FRAMES - 1, Math.floor((i / 96) * (TOTAL_FRAMES - 1)));
      const va = (meta.env_l && meta.env_l[ei]) ? meta.env_l[ei] : 0.3;
      const dy = 301 + va * 16;
      if (i === 0) tlCtx.moveTo(dx, dy); else tlCtx.lineTo(dx, dy);
    }
    tlCtx.stroke();
    tlCtx.fillStyle = '#BAE6FD'; tlCtx.font = '7.4px Consolas';
    tlCtx.fillText('BGM_DetectiveConan_Theme_Ducked.wav', v1X + 5, 298);

    // A3 Throw & Source-Gen SFX Blocks
    SFX_BLOCKS.forEach((st, idx) => {
      if (t + 0.35 < st) return;
      builtClips++;
      const sx = secToCanvasX(st);
      tlCtx.fillStyle = idx % 2 === 0 ? '#0D9488' : '#D97706';
      tlCtx.fillRect(sx, 338, 22, 36);
      tlCtx.strokeStyle = '#FDE68A'; tlCtx.strokeRect(sx, 338, 22, 36);
      tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = '6.8px Consolas';
      tlCtx.fillText('SFX', sx + 3, 359);
    });

    // Active Cyan Marquee Selection Rectangles
    for (const mq of marquees) {
      const rx = Math.min(mq.x0, mq.x1) - TL_SCREEN_X;
      const ry = Math.min(mq.y0, mq.y1) - TL_SCREEN_Y;
      const rw = Math.abs(mq.x1 - mq.x0), rh = Math.abs(mq.y1 - mq.y0);
      if (ry > 22 && ry < H) {
        tlCtx.fillStyle = 'rgba(75, 156, 255, 0.16)';
        tlCtx.fillRect(rx, ry, rw, rh);
        tlCtx.strokeStyle = '#4B9CFF'; tlCtx.strokeRect(rx, ry, rw, rh);
      }
    }

    document.getElementById('pr-tl-stat').textContent =
      t >= SEQ_DUR - 0.55 ? `✓ Sequence Complete: ${builtClips} Clips • -14.0 LUFS` : `Live Assembling: ${builtClips}/64 Clips...`;

    // Authentic Premiere Pro Blue `#4B9CFF` Playhead
    const phX = secToCanvasX(t);
    tlCtx.strokeStyle = '#4B9CFF'; tlCtx.lineWidth = 2.0;
    tlCtx.beginPath(); tlCtx.moveTo(phX, 8); tlCtx.lineTo(phX, H); tlCtx.stroke();
    tlCtx.fillStyle = '#4B9CFF';
    tlCtx.beginPath();
    tlCtx.moveTo(phX - 6, 2); tlCtx.lineTo(phX + 6, 2); tlCtx.lineTo(phX + 6, 11); tlCtx.lineTo(phX, 17); tlCtx.lineTo(phX - 6, 11);
    tlCtx.closePath(); tlCtx.fill();
  }

  // ==================== 8. VECTOR OS CURSOR RENDERER ====================
  function drawCursor(ctx, x, y, sc, ctype, badge) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(sc, sc);
    ctx.shadowColor = 'rgba(0,0,0,0.60)';
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

  // ==================== 9. MASTER 60FPS FRAME RENDERER ====================
  const liveImg = document.getElementById('liveview-img');
  const snapBox = document.getElementById('pr-snap-box');
  const vuL     = document.getElementById('vu-l');
  const vuR     = document.getElementById('vu-r');
  const vuDb    = document.getElementById('pr-vu-db');

  const jsxLines = [
    '<span class="cm">// 120-Agent Direct B-Roll & Quiz Thrower -> Premiere Pro 2026</span>',
    'voiceStream.<span class="fn">onBeatAhead</span>(<span class="nu">420</span>, <span class="kw">async</span> (cue) => {',
    '  <span class="kw">const</span> src = <span class="kw">await</span> chatgpt4o.<span class="fn">genFeelChicken9x16</span>(cue.prompt);',
    '  <span class="kw">const</span> psd = <span class="kw">await</span> photoshop.<span class="fn">cutoutQuizAndFood</span>(src, cue.tag);',
    '  <span class="kw">const</span> mogrt = illustrator.<span class="fn">exportEssentialGraphic</span>(cue.text);',
    '  <span class="kw">await</span> swarm.<span class="fn">throwToProgramMonitor</span>([psd, mogrt], importBin=<span class="nu">true</span>);',
    '  app.project.activeSequence.<span class="fn">insertAtPlayhead</span>({ lufs: <span class="nu">-14.0</span>, fps: <span class="nu">60</span> });',
    '});'
  ];
  const cmsCopy = 'KIỂM TRA MIỆNG 20/11 — Trả lời đúng nhận quà gà sốt Hàn Quốc cực ngon tại Feel Chicken 38 Nguyễn Đình Chiểu!';

  window.renderFrame = async function (frameIdx) {
    const f = Math.max(0, Math.min(TOTAL_FRAMES - 1, frameIdx));
    const t = f / FPS;

    // 1. Overlapping Top Windows Z-Jumping (`261127` style, ZERO Flow!)
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
    document.getElementById('dk-pr').className = 'dk-item on';

    const hud = document.getElementById('alt-tab-hud');
    if (ls.showAltTab) {
      hud.style.display = 'flex';
      for (let a = 0; a < 5; a++) document.getElementById(`at-${a}`).className = (a === ls.atIdx) ? 'at-it sel' : 'at-it';
    } else {
      hud.style.display = 'none';
    }
    document.getElementById('sys-ops').textContent = `${440 + Math.floor(Math.sin(t * 6) * 48 + 48)} ops/s`;

    // 2. Render Top Apps + CMS + JSX IDE + 120-Agent Throw Stream
    drawPhotoshop(f, t);
    drawIllustrator(t);
    drawChatGpt(t, f);

    const typed = Math.floor((t * 34) % (cmsCopy.length + 14));
    document.getElementById('cms-type').textContent = cmsCopy.slice(0, Math.min(cmsCopy.length, typed)) + (f % 20 < 10 ? '▋' : '');
    for (let c = 0; c < 3; c++) {
      document.getElementById(`cmsc-${c}`).className = (c === Math.floor(t * 2) % 3) ? 'cms-card hot' : 'cms-card';
    }
    const curL = Math.floor(t * 4.2) % jsxLines.length;
    document.getElementById('ide-lines').innerHTML = jsxLines.map((h, i) =>
      `<div class="cl${i === curL ? ' cur' : ''}"><span style="color:#475569;margin-right:6px;">${i + 1}</span>${h}</div>`
    ).join('');

    const recentThrows = THROW_EVENTS.filter(e => t >= e.t0).slice(-6);
    document.getElementById('swarm-rows').innerHTML = recentThrows.map((ev, idx) => {
      const st = t < ev.tLand ? 'THROWING ↘' : 'SNAPPED ✓';
      const nm = ev.text ? `"${ev.text.slice(0, 22)}..."` : (ev.tlLbl || ev.spKey);
      return `<div class="srow${idx === recentThrows.length - 1 ? ' hot' : ''}"><span><b style="color:#9999FF">[${ev.agent}]</b> ${nm}</span><span style="color:#34D399;font-weight:700;">${st}</span></div>`;
    }).join('');

    // 3. Render Premiere Pro Project Bin, Scopes, VU Meters & Inspector
    const ampL = (meta.env_l && meta.env_l[f] !== undefined) ? meta.env_l[f] : 0.35;
    const ampR = (meta.env_r && meta.env_r[f] !== undefined) ? meta.env_r[f] : 0.35;
    vuL.style.height = `${Math.min(96, Math.max(8, ampL * 92 + 6)).toFixed(1)}%`;
    vuR.style.height = `${Math.min(96, Math.max(8, ampR * 92 + 6)).toFixed(1)}%`;
    const dbVal = (-24 + Math.max(ampL, ampR) * 12.2).toFixed(1);
    vuDb.textContent = dbVal;

    drawPremiereProjectBin(t);
    drawPremiereScopes(t, Math.max(ampL, ampR));
    drawPremiereInspector(t);

    // 4. Premiere Program Monitor 1:1 Frame Sync (`assets/preview_frames/f_0001.jpg .. f_2908.jpg`)
    const secI = Math.floor(t), frmI = Math.floor((t - secI) * 60);
    document.getElementById('pr-tc').textContent = `00:00:${String(secI).padStart(2, '0')}:${String(frmI).padStart(2, '0')}`;

    const expBtn = document.getElementById('pr-export');
    const playBtn = document.getElementById('pr-play-btn');
    if (t >= SEQ_DUR - 0.55) {
      expBtn.textContent = '✓ Exported 60fps'; expBtn.className = 'pr-export-pill done';
      playBtn.innerHTML = '<span style="color:#34D399;font-size:9px;font-weight:700;">✓ DONE</span>';
      document.getElementById('pr-live-pill').textContent = '✓ EXPORTED H.264 NVENC 60FPS';
    } else {
      expBtn.textContent = 'Quick Export'; expBtn.className = 'pr-export-pill';
      playBtn.textContent = '❙❙';
      document.getElementById('pr-live-pill').textContent = '● Mercury Playback GPU (CUDA)';
    }

    const frame1Based = Math.max(1, Math.min(2908, f + 1));
    const targetFrameSrc = `assets/preview_frames/f_${String(frame1Based).padStart(4, '0')}.jpg`;
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

        if (wp.carry && spImgs[wp.carryKey] && spImgs[wp.carryKey].complete) {
          fxCtx.save(); fxCtx.globalAlpha = 0.86;
          fxCtx.drawImage(spImgs[wp.carryKey], cx + 8, cy + 8, 56, 36);
          fxCtx.strokeStyle = '#4B9CFF'; fxCtx.lineWidth = 1.4;
          fxCtx.strokeRect(cx + 8, cy + 8, 56, 36);
          fxCtx.restore();
        }
      } else {
        const hf = f - wp.f1;
        const hu = minJerk(hf / Math.max(1, wp.f2 - wp.f1));
        cx = wp.x1 + wp.dx * hu;
        cy = wp.y1 + wp.dy * hu;
        if (hf < 4) sc *= 0.86;
        if (hf < 9) {
          fxCtx.strokeStyle = `rgba(75,156,255,${(1 - hf / 9) * 0.58})`;
          fxCtx.lineWidth = 1.2;
          fxCtx.beginPath(); fxCtx.arc(cx, cy, 3 + hf * 1.2, 0, Math.PI * 2); fxCtx.stroke();
        }
        if (wp.isMq) activeMarquees.push({ x0: wp.x1, y0: wp.y1, x1: cx, y1: cy });
      }
      const safe = pushOutOfFaceZone(cx, cy);
      drawCursor(fxCtx, safe.x, safe.y, sc, wp.ctype, tc.badge);
    }

    // 5B. Group 2: 60 Escort Swarm Cursors flanking `Lead-Agent`!
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
    drawCursor(fxCtx, heroNow.x, heroNow.y, heroNow.clicking ? 0.96 : 1.08, 'arrow', { label: 'Lead-Agent', color: '#1473E6' });

    // 5C. DIRECT CURVED-ARC THROW INTO PREMIERE `Project: FeelChicken_2011` BIN (Zero blocking modal!)
    BIN_IMPORT_SCHEDULE.forEach((bi, idx) => {
      if (t >= bi.tThrow0 && t <= bi.tImported) {
        const u = minJerk((t - bi.tThrow0) / (bi.tImported - bi.tThrow0));
        const sp = winCenter(bi.tThrow0, bi.srcWin, 0.44, 0.54);
        const dp = binSlotScreenPt(2 + idx);
        const inv = 1 - u;
        const mx = (sp.x + dp.x) * 0.5 - 75, my = (sp.y + dp.y) * 0.45;
        const cx = inv * inv * sp.x + 2 * inv * u * mx + u * u * (dp.x - 52);
        const cy = inv * inv * sp.y + 2 * inv * u * my + u * u * (dp.y - 34);
        const cw = lerp(124, 108, u), ch = lerp(92, 68, u);

        fxCtx.save();
        fxCtx.strokeStyle = 'rgba(0, 229, 255, 0.58)'; fxCtx.lineWidth = 2.0; fxCtx.setLineDash([6, 4]);
        fxCtx.beginPath(); fxCtx.moveTo(sp.x, sp.y); fxCtx.quadraticCurveTo(mx, my, cx + cw * 0.5, cy + ch * 0.5); fxCtx.stroke();
        fxCtx.restore();

        drawSpriteCard(fxCtx, cx, cy, cw, ch, bi.spKey, bi.name, '#00E5FF', 0.96);
        drawCursor(fxCtx, cx + cw * 0.20, cy + 8, 1.02, 'arrow', { label: 'Import-Bin', color: '#1473E6' });
      }
    });

    // 5D. SIGNATURE 261127 DIRECT CURVED-ARC THROWS INTO PREMIERE `Program: KiemTraMieng_9x16` MONITOR!
    let snapRect = null;
    for (const ev of THROW_EVENTS) {
      if (t >= ev.t0 && t <= ev.tLand) {
        const u = minJerk((t - ev.t0) / Math.max(0.05, ev.tLand - ev.t0));
        const sp = winCenter(ev.t0, ev.srcWin, ev.rx, ev.ry);
        const inv = 1 - u;
        const mx = (sp.x + ev.dx) * 0.5 + ev.arcX;
        const my = (sp.y + ev.dy) * 0.45;
        const cx = inv * inv * sp.x + 2 * inv * u * mx + u * u * ev.dx;
        const cy = inv * inv * sp.y + 2 * inv * u * my + u * u * ev.dy;
        // Clamp giant full-frame B-Roll throws while high up so they neatly scale into the Program Monitor!
        const startScale = ev.dh > 260 ? 0.46 : 0.78;
        const cw = lerp(ev.dw * startScale, ev.dw, u);
        const ch = lerp(ev.dh * startScale, ev.dh, u);

        fxCtx.save();
        fxCtx.strokeStyle = 'rgba(0, 229, 255, 0.65)';
        fxCtx.lineWidth = 2.4;
        fxCtx.setLineDash([6, 4]);
        fxCtx.beginPath();
        fxCtx.moveTo(sp.x, sp.y);
        fxCtx.quadraticCurveTo(mx, my, cx + cw * 0.5, cy + ch * 0.5);
        fxCtx.stroke();
        fxCtx.restore();

        fxCtx.save();
        fxCtx.shadowColor = 'rgba(0, 229, 255, 0.68)';
        fxCtx.shadowBlur = 16;
        if (ev.kind === 'img') {
          drawSpriteCard(fxCtx, cx, cy, cw, ch, ev.spKey, ev.tlLbl, '#00E5FF', 0.96);
        } else if (ev.kind === 'key') {
          fxCtx.fillStyle = 'rgba(15, 23, 42, 0.93)';
          fxCtx.beginPath(); fxCtx.roundRect(cx, cy, cw, ch, 10); fxCtx.fill();
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2.2; fxCtx.stroke();
          fxCtx.shadowBlur = 0;
          fxCtx.fillStyle = '#FDE047'; fxCtx.font = '900 9.6px "MontserratBlack", "Segoe UI"'; fxCtx.textAlign = 'center';
          fxCtx.fillText(ev.text.slice(0, 28), cx + cw * 0.5, cy + ch * 0.58);
          fxCtx.textAlign = 'left';
        } else if (ev.kind === 'pill') {
          fxCtx.fillStyle = '#FFE4E6';
          fxCtx.beginPath(); fxCtx.roundRect(cx, cy, cw, ch, 12); fxCtx.fill();
          fxCtx.strokeStyle = '#E11D48'; fxCtx.lineWidth = 2.2; fxCtx.stroke();
          fxCtx.shadowBlur = 0;
          fxCtx.fillStyle = '#881337'; fxCtx.font = '800 8.8px "BeVietnamExtraBold", "Segoe UI"'; fxCtx.textAlign = 'center';
          fxCtx.fillText(ev.text.slice(0, 30), cx + cw * 0.5, cy + ch * 0.60);
          fxCtx.textAlign = 'left';
        } else {
          fxCtx.fillStyle = 'rgba(255, 255, 255, 0.96)';
          fxCtx.beginPath(); fxCtx.roundRect(cx, cy, cw, ch, 11); fxCtx.fill();
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2.0; fxCtx.stroke();
          fxCtx.shadowBlur = 0;
          fxCtx.fillStyle = '#0F172A'; fxCtx.font = '800 8.6px "BeVietnamExtraBold", "Segoe UI"'; fxCtx.textAlign = 'center';
          fxCtx.fillText(ev.text.slice(0, 30), cx + cw * 0.5, cy + ch * 0.62);
          fxCtx.textAlign = 'left';
        }
        fxCtx.restore();

        // Twin Thrower Cursors Carrying Both Corners!
        drawCursor(fxCtx, cx + cw * 0.14, cy + 6, 1.06, 'arrow', { label: ev.agent, color: ev.color });
        drawCursor(fxCtx, cx + cw * 0.86, cy + ch - 4, 0.96, 'arrow', null);
      } else if (t > ev.tLand && t <= ev.tLand + 0.22) {
        snapRect = {
          l: Math.max(1, ev.dx - VP_X),
          t: Math.max(1, ev.dy - VP_Y),
          w: Math.min(VP_W - 2, ev.dw),
          h: Math.min(VP_H - 2, ev.dh)
        };
        const ru = minJerk((t - ev.tLand) / 0.22);
        const rx = lerp(ev.dx + ev.dw * 0.85, ev.dx + ev.dw + 48, ru);
        const ry = lerp(ev.dy + 10, ev.dy - 38, ru);
        const safe = pushOutOfFaceZone(rx, ry);
        drawCursor(fxCtx, safe.x, safe.y, 1.0, 'arrow', { label: ev.agent, color: ev.color });
      }
    }

    if (snapRect) {
      snapBox.style.display = 'block';
      snapBox.style.left   = `${snapRect.l.toFixed(1)}px`;
      snapBox.style.top    = `${snapRect.t.toFixed(1)}px`;
      snapBox.style.width  = `${snapRect.w.toFixed(1)}px`;
      snapBox.style.height = `${snapRect.h.toFixed(1)}px`;
    } else {
      snapBox.style.display = 'none';
    }

    // 6. Render Premiere Pro Multi-Track Timeline
    drawPremiereTimeline(t, activeMarquees);
  };
})();
