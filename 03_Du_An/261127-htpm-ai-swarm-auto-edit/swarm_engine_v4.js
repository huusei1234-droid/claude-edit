// V4 Engine: Lush 84-Agent Swarm + Top-App Live Creation & Direct Throw Into Live View Following Chị Hằng's Voice (21.35s @ 60fps)
(function () {
  const FPS = 60;
  const TOTAL_FRAMES = 1281; // 21.35s @ 60fps (0..20.95s full 4-sentence voice sync + 0.40s clean smile finish)
  const TOTAL_SEC = TOTAL_FRAMES / FPS;
  const SEQ_DUR = 21.35;

  const HDR_W = 112;
  const TL_W  = 956;
  const secToX = (sec) => HDR_W + (Math.max(0, Math.min(SEQ_DUR, sec)) / SEQ_DUR) * TL_W;

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function minJerk(u) {
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    return u * u * u * (10 + u * (-15 + 6 * u));
  }
  function lerp(a, b, u) { return a + (b - a) * u; }

  // Preload 21 Sequence Filmstrip Thumbs & All 11 Real Extracted Overlay Crops
  const stripImgs = [];
  for (let i = 0; i < 21; i++) {
    const im = new Image();
    im.src = `assets/thumbs/strip_${String(i).padStart(2, '0')}.jpg`;
    stripImgs.push(im);
  }

  const throwImgPaths = {
    hook:  'assets/throws/th_hook_board.jpg',
    icons: 'assets/throws/th_5icons_full.jpg',
    ic1:   'assets/throws/th_icon_1.jpg',
    ic2:   'assets/throws/th_icon_2.jpg',
    ic3:   'assets/throws/th_icon_3.jpg',
    ic4:   'assets/throws/th_icon_4.jpg',
    ic5:   'assets/throws/th_icon_5.jpg',
    dk:    'assets/throws/th_dk_left.jpg',
    scale: 'assets/throws/th_scale_right.jpg',
    tea:   'assets/throws/th_tea_broll.jpg',
    ui100: 'assets/throws/th_ui_100pct.jpg',
    ws:    'assets/thumbs/SP_WHITESKIN_COMBO_CUTOUT.png',
    gel:   'assets/thumbs/bin_05_gelpk.jpg',
    nlh:   'assets/thumbs/bin_08_nlh_real.jpg'
  };
  const tImgs = {};
  for (const [k, p] of Object.entries(throwImgPaths)) {
    const im = new Image();
    im.src = p;
    tImgs[k] = im;
  }

  // ==================== 1. REAL-TIME VOICE-FOLLOW THROW SCHEDULE ====================
  // Monitor Viewport in Stage Coordinates: left = 388, top = 1012, width = 264, height = 468
  // Every visual element that appears in Chị Hằng's video is created up top ~0.5s earlier and THROWN straight into Live View!
  const THROW_EVENTS = [
    // 1. Hook Board (0.55s): "Có 5 sản phẩm mà nếu là phụ nữ sau tuổi 25..."
    { kind: 'img', img: 'hook',  t0: 0.10, tLand: 0.54, sx: 245, sy: 220, dx: 394, dy: 1018, dw: 252, dh: 150, arcX: -30, agent: 'Ae-Motion', color: '#8B5CF6', tlTrack: 'V2', sEnd: 2.85, tlLbl: '[Ae] Hook_5SanPham_Tuoi25.aep' },
    // 2. Pill Subtitle #1 (1.62s): "PHỤ NỮ SAU TUỔI 25"
    { kind: 'txt', text: 'PHỤ NỮ SAU TUỔI 25', t0: 1.18, tLand: 1.62, sx: 760, sy: 285, dx: 438, dy: 1286, dw: 164, dh: 28, arcX: 165, agent: 'Type-Throw', color: '#EC4899', tlTrack: 'V3', sEnd: 2.80, tlLbl: 'Sub_01_Tuoi25' },
    // 3. 5 Medical Mini-Cards Rapid-Fire Throw (2.95s .. 4.00s): "5 NỀN TẢNG KHỎE ĐẸP TỪ BÊN TRONG"
    { kind: 'img', img: 'ic1',   t0: 2.52, tLand: 2.95, sx: 175, sy: 245, dx: 398, dy: 1058, dw: 47,  dh: 88,  arcX: -75, agent: 'Ps-Cutout', color: '#0284C7', tlTrack: 'V2', sEnd: 6.85, tlLbl: '[Ps/Ae] 5_NenTang_Icons.aep' },
    { kind: 'img', img: 'ic2',   t0: 2.78, tLand: 3.20, sx: 230, sy: 245, dx: 447, dy: 1058, dw: 47,  dh: 88,  arcX: -55, agent: 'Icon-Gen',  color: '#0EA5E9' },
    { kind: 'img', img: 'ic3',   t0: 3.02, tLand: 3.45, sx: 285, sy: 245, dx: 496, dy: 1058, dw: 47,  dh: 88,  arcX: 45,  agent: 'Ai-Vector', color: '#D97706' },
    { kind: 'img', img: 'ic4',   t0: 3.28, tLand: 3.70, sx: 340, sy: 245, dx: 545, dy: 1058, dw: 47,  dh: 88,  arcX: 85,  agent: 'Ae-3D',     color: '#9333EA' },
    { kind: 'img', img: 'ic5',   t0: 3.52, tLand: 3.95, sx: 395, sy: 245, dx: 594, dy: 1058, dw: 47,  dh: 88,  arcX: 115, agent: 'Ps-Layer',  color: '#2563EB' },
    // Subtitles #2 & #3
    { kind: 'txt', text: 'Tôi nghĩ chị em nên tìm hiểu để', t0: 2.50, tLand: 2.92, sx: 760, sy: 305, dx: 426, dy: 1292, dw: 188, dh: 28, arcX: 175, agent: 'Sub-Whisper', color: '#DB2777', tlTrack: 'V3', sEnd: 4.65, tlLbl: 'Sub_02_TimHieu' },
    { kind: 'txt', text: 'Chăm sóc sức khỏe & sắc đẹp', t0: 4.28, tLand: 4.70, sx: 760, sy: 305, dx: 426, dy: 1292, dw: 188, dh: 28, arcX: 175, agent: 'Type-Throw',  color: '#EC4899', tlTrack: 'V3', sEnd: 6.85, tlLbl: 'Sub_03_SucKhoe' },
    // 4. Điều Kinh HT Bottle Card + Balance Scale Throw (7.0s .. 7.9s): "Thứ nhất là sản phẩm hỗ trợ điều hòa chu kỳ..."
    { kind: 'txt', text: 'Thứ nhất là sản phẩm hỗ trợ điều hòa', t0: 6.55, tLand: 6.98, sx: 760, sy: 305, dx: 422, dy: 1292, dw: 196, dh: 28, arcX: 180, agent: 'Sub-Whisper', color: '#DB2777', tlTrack: 'V3', sEnd: 9.35, tlLbl: 'Sub_04_DieuHoa' },
    { kind: 'img', img: 'dk',    t0: 7.08, tLand: 7.55, sx: 235, sy: 240, dx: 398, dy: 1052, dw: 96,  dh: 108, arcX: -95, agent: 'Ps-Cutout',  color: '#0284C7', tlTrack: 'V2', sEnd: 13.85,tlLbl: '[Ps] SP_DieuKinhHT_Cut.psd' },
    { kind: 'img', img: 'scale', t0: 7.38, tLand: 7.86, sx: 785, sy: 215, dx: 498, dy: 1052, dw: 144, dh: 108, arcX: 110, agent: 'Ae-Motion',  color: '#8B5CF6', tlTrack: 'V4', sEnd: 13.85,tlLbl: '[Ae] Scale_CanBang_3D.aep' },
    // Subtitles #5, #6, #7
    { kind: 'txt', text: 'Chu kỳ & chăm sóc nội tiết tố nữ', t0: 9.00, tLand: 9.42, sx: 760, sy: 305, dx: 424, dy: 1292, dw: 192, dh: 28, arcX: 178, agent: 'Type-Throw',  color: '#EC4899', tlTrack: 'V3', sEnd: 11.10,tlLbl: 'Sub_05_NoiTiet' },
    { kind: 'txt', text: 'Một cơ thể khỏe mạnh thường bắt đầu', t0: 10.72,tLand: 11.15,sx: 760, sy: 305, dx: 422, dy: 1292, dw: 196, dh: 28, arcX: 180, agent: 'Sub-Whisper', color: '#DB2777', tlTrack: 'V3', sEnd: 12.60,tlLbl: 'Sub_06_KhoeManh' },
    { kind: 'txt', text: 'Từ sự cân bằng bên trong.', t0: 12.22,tLand: 12.64,sx: 760, sy: 305, dx: 432, dy: 1292, dw: 176, dh: 28, arcX: 172, agent: 'Type-Throw',  color: '#EC4899', tlTrack: 'V3', sEnd: 13.95,tlLbl: 'Sub_07_CanBang' },
    // 5. Sunlight Tea Woman B-Roll + 100% Energy SaaS Card Throw (14.4s .. 15.1s): "Khi chăm sóc tốt sức khỏe nội tiết, nhiều chị em..."
    { kind: 'txt', text: 'Khi chăm sóc tốt sức khỏe nội tiết,', t0: 13.72,tLand: 14.14,sx: 760, sy: 305, dx: 424, dy: 1292, dw: 192, dh: 28, arcX: 178, agent: 'Sub-Whisper', color: '#DB2777', tlTrack: 'V3', sEnd: 16.20,tlLbl: 'Sub_08_ChamSoc' },
    { kind: 'img', img: 'tea',   t0: 14.32,tLand: 14.82,sx: 665, sy: 560, dx: 394, dy: 1020, dw: 150, dh: 154, arcX: 95,  agent: 'Gemini-Pro', color: '#0891B2', tlTrack: 'V2', sEnd: 20.92,tlLbl: '[Flow] Broll_TraNangMai.mp4' },
    { kind: 'img', img: 'ui100', t0: 14.56,tLand: 15.05,sx: 265, sy: 240, dx: 548, dy: 1020, dw: 97,  dh: 154, arcX: -60, agent: 'Ai-Vector',  color: '#D97706', tlTrack: 'V4', sEnd: 20.92,tlLbl: '[Ae] UI_NangLuong_100pct.aep' },
    // Final Subtitles #9, #10, #11
    { kind: 'txt', text: 'Nhiều chị em cũng cảm thấy cơ thể', t0: 15.85,tLand: 16.28,sx: 760, sy: 305, dx: 424, dy: 1292, dw: 192, dh: 28, arcX: 178, agent: 'Type-Throw',  color: '#EC4899', tlTrack: 'V3', sEnd: 18.25,tlLbl: 'Sub_09_CoThe' },
    { kind: 'txt', text: 'Có nhiều năng lượng & tự tin hơn', t0: 17.85,tLand: 18.28,sx: 760, sy: 305, dx: 424, dy: 1292, dw: 192, dh: 28, arcX: 178, agent: 'Sub-Whisper', color: '#DB2777', tlTrack: 'V3', sEnd: 19.95,tlLbl: 'Sub_10_NangLuong' },
    { kind: 'txt', text: 'Trong cuộc sống hàng ngày.', t0: 19.55,tLand: 19.98,sx: 760, sy: 305, dx: 432, dy: 1292, dw: 176, dh: 28, arcX: 172, agent: 'Type-Throw',  color: '#EC4899', tlTrack: 'V3', sEnd: 20.95,tlLbl: 'Sub_11_HangNgay' }
  ];

  // SFX hits placed ahead of playhead along A3
  const SFX_BLOCKS = [0.54, 1.62, 2.95, 3.45, 3.95, 4.70, 7.55, 7.86, 11.15, 14.82, 15.05, 18.28, 19.98];

  // ==================== 2. TOP MULTI-APP RAPID JUMPING CHOREOGRAPHY ====================
  const TOP_LAYOUTS = [
    // 0..2.2s: Photoshop + Illustrator crafting Hook & 5 Icons
    { focus: 'ps', dock: 'dk-ps', atIdx: 0, rects: {
      ps:{x:12,y:10,w:635,h:462,z:30,s:1.00}, ai:{x:550,y:14,w:516,h:406,z:26,s:0.99},
      cms:{x:14,y:454,w:528,h:432,z:22,s:0.98}, gem:{x:548,y:452,w:518,h:434,z:24,s:0.98},
      ide:{x:240,y:230,w:535,h:395,z:14,s:0.94}, swarm:{x:532,y:225,w:512,h:395,z:15,s:0.94}
    }},
    // 2.2..5.5s: Photoshop Spotlight slicing 5 Icons + Illustrator Live Subtitle Thrower!
    { focus: 'ai', dock: 'dk-ai', atIdx: 3, rects: {
      ps:{x:10,y:14,w:625,h:458,z:29,s:1.00}, ai:{x:525,y:12,w:542,h:418,z:32,s:1.01},
      ide:{x:14,y:462,w:538,h:420,z:25,s:0.98}, swarm:{x:554,y:458,w:512,h:424,z:27,s:0.99},
      cms:{x:190,y:445,w:520,h:420,z:15,s:0.95}, gem:{x:510,y:220,w:510,h:415,z:14,s:0.94}
    }},
    // 5.5..9.5s: Photoshop Cutout (Điều Kinh HT) + Illustrator/AE Scale Vector + Swarm Log!
    { focus: 'ps', dock: 'dk-ps', atIdx: 0, rects: {
      ps:{x:14,y:12,w:638,h:464,z:33,s:1.01}, ai:{x:542,y:16,w:524,h:412,z:30,s:1.00},
      cms:{x:14,y:456,w:530,h:430,z:26,s:0.98}, swarm:{x:550,y:460,w:516,h:422,z:28,s:0.99},
      ide:{x:230,y:220,w:530,h:395,z:15,s:0.95}, gem:{x:520,y:220,w:510,h:415,z:14,s:0.94}
    }},
    // 9.5..13.5s: Chrome Auto-CMS + Antigravity JSX IDE + Illustrator Subtitle Crafter!
    { focus: 'cms', dock: 'dk-web', atIdx: 4, rects: {
      cms:{x:12,y:14,w:545,h:442,z:32,s:1.01}, ai:{x:546,y:14,w:520,h:412,z:30,s:1.00},
      ide:{x:14,y:460,w:542,h:424,z:28,s:0.99}, gem:{x:552,y:448,w:516,h:436,z:29,s:1.00},
      ps:{x:200,y:210,w:600,h:440,z:16,s:0.95}, swarm:{x:525,y:220,w:510,h:395,z:15,s:0.94}
    }},
    // 13.5..17.5s: Gemini Pro B-Roll Engine Jumps Front-Right + Photoshop UI 100% Front-Left -> THROWS TEA B-ROLL & UI 100%!
    { focus: 'gem', dock: 'dk-ag', atIdx: 5, rects: {
      ps:{x:12,y:14,w:615,h:455,z:30,s:1.00}, gem:{x:532,y:438,w:536,h:448,z:34,s:1.02},
      ai:{x:548,y:12,w:518,h:410,z:29,s:0.99}, cms:{x:14,y:458,w:514,h:428,z:25,s:0.98},
      ide:{x:30,y:230,w:520,h:390,z:15,s:0.94}, swarm:{x:525,y:220,w:508,h:390,z:16,s:0.95}
    }},
    // 17.5..21.35s: Swarm Encoder + Photoshop + Illustrator + CMS Final Sync!
    { focus: 'swarm', dock: 'dk-ps', atIdx: 4, rects: {
      ps:{x:12,y:14,w:625,h:458,z:30,s:1.00}, ai:{x:546,y:14,w:520,h:408,z:29,s:0.99},
      cms:{x:14,y:456,w:528,h:430,z:27,s:0.98}, swarm:{x:548,y:456,w:518,h:426,z:33,s:1.01},
      gem:{x:520,y:215,w:512,h:415,z:16,s:0.95}, ide:{x:210,y:225,w:525,h:395,z:15,s:0.94}
    }}
  ];
  const WIN_IDS = ['ps', 'ai', 'cms', 'gem', 'ide', 'swarm'];

  function getLayoutAt(t, f) {
    const idx = t < 2.2 ? 0 : t < 5.5 ? 1 : t < 9.5 ? 2 : t < 13.5 ? 3 : t < 17.5 ? 4 : 5;
    const starts = [0, 2.2, 5.5, 9.5, 13.5, 17.5];
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

  // ==================== 3. GENERATE LUSH 84-AGENT SWARM CURSORS ====================
  // 18 Dedicated Thrower/Assembler Agents + 66 Dense Specialist Cursors across Top Apps & Bottom NLE!
  const swarmCursors = [];
  const namedSpecs = [
    { label: 'Claude-Opus', color: '#D97706', zone: 'ide' },
    { label: 'Gemini-Pro',  color: '#0284C7', zone: 'gem' },
    { label: 'Flow-Broll',  color: '#7C3AED', zone: 'gem' },
    { label: 'Ps-Cutout',   color: '#2563EB', zone: 'ps' },
    { label: 'Ps-Curves',   color: '#0891B2', zone: 'ps' },
    { label: 'Ai-Vector',   color: '#EA580C', zone: 'ai' },
    { label: 'Sub-Whisper', color: '#DB2777', zone: 'ai' },
    { label: 'CMS-Auto',    color: '#059669', zone: 'cms' },
    { label: 'TikTok-Shop', color: '#E11D48', zone: 'cms' },
    { label: 'JSX-Bridge',  color: '#0D9488', zone: 'swarm' },
    { label: 'Pr-Timeline', color: '#4F46E5', zone: 'tlAhead' },
    { label: 'Pr-Blade',    color: '#DC2626', zone: 'tlAhead' },
    { label: 'Ae-Motion',   color: '#9333EA', zone: 'insp' },
    { label: 'Lumetri-LUT', color: '#0284C7', zone: 'insp' },
    { label: 'SFX-Master',  color: '#059669', zone: 'tlAudio' },
    { label: 'LUFS-Mix',    color: '#10B981', zone: 'tlAudio' },
    { label: 'Bin-Loader',  color: '#2563EB', zone: 'binToTl' },
    { label: 'QC-SafeZone', color: '#0EA5E9', zone: 'monSafe' }
  ];

  function pickZonePt(zone, t, rng) {
    // Keep timeline cursors focused right around/ahead of Playhead (t .. t + 4.5s) so they actively build the track!
    const aheadMin = Math.min(20.2, Math.max(0.2, t - 0.3));
    const aheadMax = Math.min(21.1, t + 4.8);
    if (zone === 'ps')      return { x: 45 + rng()*540,  y: 72 + rng()*375,  c: ['cross','hand','arrow'][Math.floor(rng()*3)] };
    if (zone === 'ai')      return { x: 575 + rng()*465, y: 72 + rng()*340,  c: ['cross','ibeam','hand'][Math.floor(rng()*3)] };
    if (zone === 'cms')     return { x: 35 + rng()*475,  y: 495 + rng()*360, c: ['hand','ibeam','arrow'][Math.floor(rng()*3)] };
    if (zone === 'gem')     return { x: 570 + rng()*475, y: 495 + rng()*365, c: ['hand','arrow'][Math.floor(rng()*2)] };
    if (zone === 'ide')     return { x: 45 + rng()*470,  y: 270 + rng()*320, c: ['ibeam','hand'][Math.floor(rng()*2)] };
    if (zone === 'swarm')   return { x: 565 + rng()*475, y: 270 + rng()*320, c: ['arrow','hand'][Math.floor(rng()*2)] };
    if (zone === 'bin')     return { x: 20 + rng()*240,  y: 1005 + rng()*480,c: 'hand' };
    if (zone === 'binToTl') {
      if (rng() < 0.45) return { x: 24 + rng()*230, y: 1015 + rng()*460, c: 'hand', carry: true };
      return { x: secToX(aheadMin + rng()*(aheadMax - aheadMin)), y: 1555 + rng()*210, c: 'hand', carry: true };
    }
    if (zone === 'insp')    return { x: 782 + rng()*278, y: 995 + rng()*485, c: rng()<0.65 ? 'ew-resize' : 'hand' };
    if (zone === 'monSafe') {
      // Strictly outside Chị Hằng's face (x: 412..598, y: 1135..1270)!
      if (rng() < 0.55) return { x: rng()<0.5 ? (290+rng()*75) : (662+rng()*88), y: 1015 + rng()*455, c: 'hand' };
      return { x: 398 + rng()*244, y: 1020 + rng()*105, c: 'hand' }; // Upper graphic card zone above hair!
    }
    if (zone === 'tlAudio') {
      return { x: secToX(aheadMin + rng()*(aheadMax - aheadMin)), y: 1750 + rng()*150, c: rng()<0.5 ? 'ew-resize' : 'hand' };
    }
    // tlAhead: Video/Caption/Stage tracks right in front of the moving Playhead!
    return { x: secToX(aheadMin + rng()*(aheadMax - aheadMin)), y: 1550 + rng()*205, c: ['ew-resize','hand','arrow'][Math.floor(rng()*3)] };
  }

  const allZonePool = [
    'ps','ps','ps','ai','ai','cms','cms','gem','gem','ide','swarm',
    'bin','binToTl','binToTl','insp','insp','monSafe',
    'tlAhead','tlAhead','tlAhead','tlAhead','tlAhead','tlAudio','tlAudio'
  ];

  for (let i = 0; i < 76; i++) {
    const rng = mulberry32(4409 + i * 7907);
    const spec = i < namedSpecs.length ? namedSpecs[i] : null;
    const zName = spec ? spec.zone : allZonePool[i % allZonePool.length];
    const wps = [];
    let f = -Math.floor(rng() * 24);
    let prev = pickZonePt(zName, 0, rng);

    while (f < TOTAL_FRAMES + 60) {
      const curT = Math.max(0, f / FPS);
      const nxt = pickZonePt(zName, curT, rng);
      const mDur = Math.floor(14 + rng() * 22);
      const hDur = Math.floor(6 + rng() * 14);
      const isMq = (zName === 'tlAhead' || zName === 'tlAudio') && rng() < 0.22;
      wps.push({
        f0: f, f1: f + mDur, f2: f + mDur + hDur,
        x0: prev.x, y0: prev.y, x1: nxt.x, y1: nxt.y,
        arc: (rng() - 0.5) * 44,
        ctype: nxt.c,
        dx: isMq ? (32 + rng()*75) : (zName === 'insp' ? (rng()-0.5)*28 : 0),
        dy: isMq ? (16 + rng()*28) : 0,
        isMq,
        carry: Boolean(nxt.carry && nxt.y > 1500),
        carryKey: ['ws', 'gel', 'nlh', 'ic1', 'dk'][i % 5]
      });
      f += mDur + hDur;
      prev = nxt;
    }
    swarmCursors.push({ badge: spec ? { label: spec.label, color: spec.color } : null, wps });
  }

  // ==================== 4. DRAW PHOTOSHOP & ILLUSTRATOR LIVE PRE-CRAFTING ====================
  const psCtx = document.getElementById('ps-cvs').getContext('2d');
  const aiCtx = document.getElementById('ai-cvs').getContext('2d');
  const grCtx = document.getElementById('ae-graph-cvs').getContext('2d');
  const sc1 = document.getElementById('sc-1').getContext('2d');
  const sc2 = document.getElementById('sc-2').getContext('2d');
  const sc3 = document.getElementById('sc-3').getContext('2d');
  const tlCtx = document.getElementById('tl-canvas').getContext('2d');
  const fxCtx = document.getElementById('fx-canvas').getContext('2d');

  function drawPhotoshop(f, t) {
    const W = 416, H = 364;
    psCtx.clearRect(0, 0, W, H);

    // Dynamically show the EXACT graphic being pre-built right before it gets thrown into Live View!
    let key = 'hook', lyrIdx = 0;
    if (t < 1.6)       { key = 'hook';  lyrIdx = 0; }
    else if (t < 6.0)  { key = 'icons'; lyrIdx = 1; }
    else if (t < 10.5) { key = 'dk';    lyrIdx = 2; }
    else if (t < 13.8) { key = 'scale'; lyrIdx = 3; }
    else if (t < 18.2) { key = 'ui100'; lyrIdx = 4; }
    else               { key = 'ws';    lyrIdx = 5; }

    const im = tImgs[key];
    if (im && im.complete && im.naturalWidth > 0) {
      const ratio = Math.min((W * 0.80) / im.naturalWidth, (H * 0.78) / im.naturalHeight);
      const dw = im.naturalWidth * ratio, dh = im.naturalHeight * ratio;
      const dx = (W - dw) * 0.5, dy = (H - dh) * 0.46;
      psCtx.drawImage(im, dx, dy, dw, dh);

      psCtx.strokeStyle = '#31A8FF'; psCtx.lineWidth = 1.4;
      psCtx.strokeRect(dx - 5, dy - 5, dw + 10, dh + 10);
      for (const [hx, hy] of [[dx-5,dy-5],[dx+dw+5,dy-5],[dx-5,dy+dh+5],[dx+dw+5,dy+dh+5]]) {
        psCtx.fillStyle = '#FFF'; psCtx.fillRect(hx - 3, hy - 3, 6, 6);
      }

      // Animated Marching Ants
      psCtx.save();
      psCtx.setLineDash([5, 5]); psCtx.lineDashOffset = -(f * 0.9);
      psCtx.strokeStyle = '#FFFFFF';
      psCtx.strokeRect(dx + 4, dy + 4, dw - 8, dh - 8);
      psCtx.restore();
    }

    // Curves HUD
    const cx = W - 92, cy = 8, cw = 84, ch = 84;
    psCtx.fillStyle = 'rgba(24,24,28,0.90)'; psCtx.fillRect(cx, cy, cw, ch);
    psCtx.strokeStyle = '#52525B'; psCtx.strokeRect(cx, cy, cw, ch);
    psCtx.strokeStyle = '#31A8FF'; psCtx.lineWidth = 1.8;
    psCtx.beginPath(); psCtx.moveTo(cx+6, cy+ch-6);
    const b = Math.sin(t * 4) * 8;
    psCtx.bezierCurveTo(cx+26, cy+ch-12+b, cx+56, cy+12-b, cx+cw-6, cy+6);
    psCtx.stroke();

    for (let k = 0; k < 6; k++) {
      document.getElementById(`psl-${k}`).className = k === lyrIdx ? 'ps-lyr sel' : 'ps-lyr';
    }
  }

  function drawIllustrator(t) {
    const W = 515, H = 384;
    aiCtx.fillStyle = '#18181C'; aiCtx.fillRect(0, 0, W, H);
    const ax = 28, ay = 20, aw = 459, ah = 344;
    aiCtx.fillStyle = '#101522'; aiCtx.fillRect(ax, ay, aw, ah);
    aiCtx.strokeStyle = '#FF9A00'; aiCtx.lineWidth = 1.2; aiCtx.strokeRect(ax, ay, aw, ah);

    // Find next or current Subtitle being crafted in Illustrator right before throwing!
    let nextSub = 'PHỤ NỮ SAU TUỔI 25';
    for (const ev of THROW_EVENTS) {
      if (ev.kind === 'txt' && t <= ev.tLand + 0.3) { nextSub = ev.text; break; }
    }

    // Vector Crest
    const cx = ax + aw * 0.5, cy = ay + 112, r = 56 + Math.sin(t * 3) * 3;
    aiCtx.strokeStyle = '#F59E0B'; aiCtx.lineWidth = 2.2;
    aiCtx.beginPath(); aiCtx.arc(cx, cy, r, 0, Math.PI * 2); aiCtx.stroke();
    for (let k = 0; k < 8; k++) {
      const a = (k / 8) * Math.PI * 2 + t * 0.4;
      aiCtx.fillStyle = '#FFF';
      aiCtx.fillRect(cx + Math.cos(a)*r - 3, cy + Math.sin(a)*r - 3, 6, 6);
    }
    aiCtx.fillStyle = '#FDE68A'; aiCtx.font = '900 14px "Segoe UI"'; aiCtx.textAlign = 'center';
    aiCtx.fillText('HẰNG THU PHARMA', cx, cy + 5);

    // Live Text Pill Box ready to be thrown into Live View!
    const px = cx - 175, py = ay + 215, pw = 350, ph = 46;
    aiCtx.fillStyle = '#FFFFFF';
    aiCtx.beginPath(); aiCtx.roundRect(px, py, pw, ph, 23); aiCtx.fill();
    aiCtx.strokeStyle = '#00E5FF'; aiCtx.lineWidth = 2; aiCtx.stroke();
    aiCtx.fillStyle = '#0F172A'; aiCtx.font = '800 13.5px "Segoe UI"';
    aiCtx.fillText(nextSub, cx, py + 28);

    aiCtx.fillStyle = '#67E8F9'; aiCtx.font = 'bold 9.5px Consolas';
    aiCtx.fillText('⚡ LIVE SUBTITLE VECTOR -> READY TO THROW DOWN', cx, py + 68);
    aiCtx.textAlign = 'left';
  }

  function drawAeGraph(t) {
    const W = 288, H = 118;
    grCtx.fillStyle = '#121215'; grCtx.fillRect(0, 0, W, H);
    grCtx.strokeStyle = '#24242C';
    for (let y = 24; y < H; y += 24) { grCtx.beginPath(); grCtx.moveTo(0, y); grCtx.lineTo(W, y); grCtx.stroke(); }
    const shift = Math.sin(t * 4) * 24;
    grCtx.strokeStyle = '#FACC15'; grCtx.lineWidth = 2;
    grCtx.beginPath(); grCtx.moveTo(16, H-16);
    grCtx.bezierCurveTo(88+shift, H-16, 94+shift, 16, 144, 16);
    grCtx.bezierCurveTo(194-shift, 16, 200-shift, H-16, W-16, H-16);
    grCtx.stroke();
    const gx = ((t * 1.6) % 1) * (W - 24) + 12;
    grCtx.strokeStyle = '#EF4444'; grCtx.beginPath(); grCtx.moveTo(gx, 0); grCtx.lineTo(gx, H); grCtx.stroke();
  }

  function drawScopes(t, vAmp) {
    sc1.fillStyle = '#08080A'; sc1.fillRect(0, 0, 68, 135);
    sc1.strokeStyle = 'rgba(74,222,128,0.75)'; sc1.beginPath();
    for (let x = 0; x < 68; x += 2) {
      const y = 70 + Math.sin(x*0.22 + t*5)*22 + Math.cos(x*0.5 - t*3)*12*(0.6 + vAmp);
      if (x === 0) sc1.moveTo(x, y); else sc1.lineTo(x, y);
    }
    sc1.stroke();

    sc2.fillStyle = '#08080A'; sc2.fillRect(0, 0, 68, 135);
    const cols = ['rgba(248,113,113,0.78)', 'rgba(74,222,128,0.78)', 'rgba(96,165,250,0.78)'];
    for (let c = 0; c < 3; c++) {
      sc2.fillStyle = cols[c];
      for (let i = 0; i < 9; i++) {
        const bh = 28 + Math.abs(Math.sin(t*4 + c*1.7 + i*0.6))*64;
        sc2.fillRect(c*22 + 3 + i*2, 120 - bh, 1.5, bh);
      }
    }

    sc3.fillStyle = '#08080A'; sc3.fillRect(0, 0, 68, 135);
    sc3.strokeStyle = '#27272A'; sc3.beginPath(); sc3.arc(34, 74, 26, 0, Math.PI*2); sc3.stroke();
    sc3.strokeStyle = 'rgba(251,191,36,0.7)'; sc3.beginPath(); sc3.moveTo(34, 74); sc3.lineTo(20, 50); sc3.stroke();
    sc3.fillStyle = 'rgba(253,186,116,0.65)';
    for (let k = 0; k < 14; k++) {
      const a = -2.1 + Math.sin(t*3+k)*0.26, r = 6 + (k/14)*16;
      sc3.fillRect(34 + Math.cos(a)*r, 74 + Math.sin(a)*r, 2, 2);
    }
  }

  // ==================== 5. BULLET-TRAIN LAY-TRACKS-AHEAD TIMELINE ====================
  function drawTimeline(t, aeMode, marquees) {
    const W = 1080, H = 398;
    tlCtx.fillStyle = '#18181B'; tlCtx.fillRect(0, 0, W, H);

    // Ruler
    tlCtx.fillStyle = '#222226'; tlCtx.fillRect(0, 0, W, 24);
    tlCtx.font = '9.5px Consolas, monospace'; tlCtx.fillStyle = '#9CA3AF';
    for (let s = 0; s <= 21; s += 3) {
      const sx = secToX(s);
      tlCtx.strokeStyle = '#52525B'; tlCtx.beginPath(); tlCtx.moveTo(sx, 11); tlCtx.lineTo(sx, 24); tlCtx.stroke();
      tlCtx.fillText(`00:00:${String(s).padStart(2, '0')}:00`, sx - 24, 10);
    }

    const trRows = [
      { lbl: 'V4 UI / Scale', y: 27,  h: 34, v: true },
      { lbl: 'V3 Subtitles',  y: 64,  h: 34, v: true },
      { lbl: 'V2 B-Roll/Card',y: 101, h: 44, v: true },
      { lbl: 'V1 Chị Hằng',   y: 148, h: 58, v: true },
      { lbl: 'A1 Voiceover',  y: 212, h: 56, v: false },
      { lbl: 'A2 BGM Duck',   y: 271, h: 42, v: false },
      { lbl: 'A3 Micro-SFX',  y: 316, h: 42, v: false }
    ];
    for (const tr of trRows) {
      tlCtx.fillStyle = '#1E1E22'; tlCtx.fillRect(HDR_W, tr.y, W - HDR_W, tr.h);
      tlCtx.fillStyle = '#26262C'; tlCtx.fillRect(0, tr.y, HDR_W - 2, tr.h);
      tlCtx.fillStyle = tr.v ? (aeMode ? '#6B21A8' : '#2B579A') : '#1E6B52';
      tlCtx.fillRect(4, tr.y + 5, 22, tr.h - 10);
      tlCtx.fillStyle = '#E4E4E7'; tlCtx.font = 'bold 9px "Segoe UI"';
      tlCtx.fillText(tr.lbl, 31, tr.y + tr.h * 0.58);
    }

    let builtClips = 2;
    // V1 + A1 extend smoothly 3.2s ahead of Chị Hằng's voice!
    const v1BuiltSec = Math.min(21.0, t + 3.4);
    const v1X = secToX(0), v1W = secToX(v1BuiltSec) - v1X;
    tlCtx.save();
    tlCtx.beginPath(); tlCtx.rect(v1X, 150, v1W, 54); tlCtx.clip();
    tlCtx.fillStyle = '#3B669C'; tlCtx.fillRect(v1X, 150, secToX(21)-v1X, 54);
    const cw = (secToX(21) - v1X) / 21;
    for (let i = 0; i < 21; i++) {
      const im = stripImgs[i];
      if (im && im.complete && im.naturalWidth > 0) tlCtx.drawImage(im, v1X + i*cw, 164, cw+0.8, 40);
    }
    tlCtx.fillStyle = 'rgba(20,40,72,0.88)'; tlCtx.fillRect(v1X, 150, secToX(21)-v1X, 14);
    tlCtx.fillStyle = '#E0F2FE'; tlCtx.font = 'bold 8.4px Consolas';
    tlCtx.fillText('CamA_ChiHang_Master.MP4', v1X + 5, 160);
    tlCtx.restore();
    tlCtx.strokeStyle = '#93C5FD'; tlCtx.lineWidth = 1.2; tlCtx.strokeRect(v1X, 150, v1W, 54);

    // A1 Waveform building ahead
    tlCtx.fillStyle = '#1B5E4A'; tlCtx.fillRect(v1X, 214, v1W, 52);
    tlCtx.strokeStyle = '#4ADE80'; tlCtx.strokeRect(v1X, 214, v1W, 52);
    const wf = (window.AUDIO_DATA && window.AUDIO_DATA.waveform) ? window.AUDIO_DATA.waveform : [];
    const fullW = secToX(21.35) - v1X;
    const bStep = fullW / Math.max(1, wf.length);
    for (let b = 0; b < wf.length; b++) {
      const bx = v1X + b * bStep;
      if (bx > v1X + v1W - 2) break;
      const bh = Math.max(2, wf[b] * 40);
      tlCtx.fillStyle = ((b / wf.length) * 21.35 <= t) ? '#A7F3D0' : '#6EE7B7';
      tlCtx.fillRect(bx, 242 - bh*0.5, Math.max(1.4, bStep - 1), bh);
    }

    // Thrown V2, V3, V4 Clips appear RIGHT AS EACH THROW LANDS!
    for (const ev of THROW_EVENTS) {
      if (!ev.tlTrack || t < ev.tLand - 0.05) continue;
      builtClips++;
      const growU = minJerk(Math.min(1, (t - (ev.tLand - 0.05)) / 0.32));
      const curEnd = lerp(ev.tLand + 0.35, ev.sEnd, growU);
      const x = secToX(ev.tLand), w = Math.max(10, secToX(curEnd) - x);

      if (ev.tlTrack === 'V2') {
        tlCtx.fillStyle = aeMode ? '#7E22CE' : '#2563EB';
        tlCtx.fillRect(x, 103, w, 40);
        tlCtx.strokeStyle = '#7DD3FC'; tlCtx.strokeRect(x, 103, w, 40);
        if (growU < 1) { tlCtx.fillStyle = '#FACC15'; tlCtx.fillRect(x + w - 4, 103, 4, 40); }
        tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x+4, 103, Math.max(0,w-8), 40); tlCtx.clip();
        tlCtx.fillStyle = '#FFF'; tlCtx.font = 'bold 8.5px "Segoe UI"'; tlCtx.fillText(ev.tlLbl, x+6, 126);
        tlCtx.restore();
      } else if (ev.tlTrack === 'V3') {
        const activeSub = t >= ev.tLand && t <= ev.sEnd;
        tlCtx.fillStyle = activeSub ? '#D946EF' : '#86198F';
        tlCtx.fillRect(x, 66, w, 30);
        tlCtx.strokeStyle = '#F5D0FE'; tlCtx.strokeRect(x, 66, w, 30);
        if (w > 32) {
          tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x+3, 66, w-6, 30); tlCtx.clip();
          tlCtx.fillStyle = '#FFF'; tlCtx.font = '8px Consolas'; tlCtx.fillText(ev.tlLbl, x+4, 84);
          tlCtx.restore();
        }
      } else if (ev.tlTrack === 'V4') {
        tlCtx.fillStyle = '#DB2777'; tlCtx.fillRect(x, 29, w, 30);
        tlCtx.strokeStyle = '#FBCFE8'; tlCtx.strokeRect(x, 29, w, 30);
        tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x+4, 29, Math.max(0,w-8), 30); tlCtx.clip();
        tlCtx.fillStyle = '#FFF'; tlCtx.font = 'bold 8.5px "Segoe UI"'; tlCtx.fillText(ev.tlLbl, x+6, 47);
        tlCtx.restore();
      }
    }

    // A2 BGM Ducking building ahead
    if (t >= 0.4) {
      builtClips++;
      const bw = secToX(Math.min(21.0, t + 2.8)) - v1X;
      tlCtx.fillStyle = '#164E63'; tlCtx.fillRect(v1X, 273, bw, 38);
      tlCtx.strokeStyle = '#38BDF8'; tlCtx.strokeRect(v1X, 273, bw, 38);
      tlCtx.strokeStyle = '#FACC15'; tlCtx.lineWidth = 1.5;
      tlCtx.beginPath();
      for (let i = 0; i <= 60; i++) {
        const st = (i / 60) * 21.0;
        const dx = secToX(st);
        if (dx > v1X + bw) break;
        const ei = Math.min(TOTAL_FRAMES - 1, Math.floor((i / 60) * (TOTAL_FRAMES - 1)));
        const va = window.AUDIO_DATA ? window.AUDIO_DATA.env_l[ei] : 0.3;
        const dy = 284 + va * 14;
        if (i === 0) tlCtx.moveTo(dx, dy); else tlCtx.lineTo(dx, dy);
      }
      tlCtx.stroke();
    }

    // A3 Micro-SFX blocks snapping right ahead of Playhead!
    for (let i = 0; i < SFX_BLOCKS.length; i++) {
      if (t + 0.35 < SFX_BLOCKS[i]) continue;
      builtClips++;
      const sx = secToX(SFX_BLOCKS[i]);
      tlCtx.fillStyle = i % 2 === 0 ? '#0D9488' : '#D97706';
      tlCtx.fillRect(sx, 319, 34, 34);
      tlCtx.strokeStyle = '#FDE68A'; tlCtx.strokeRect(sx, 319, 34, 34);
      tlCtx.fillStyle = '#FFF'; tlCtx.font = '7.6px Consolas';
      tlCtx.fillText(i % 2 === 0 ? 'Whoosh' : 'Pop', sx + 3, 339);
    }

    // Active Marquee Selection Rectangles
    for (const mq of marquees) {
      const rx = Math.min(mq.x0, mq.x1), ry = Math.min(mq.y0, mq.y1) - 1522;
      const rw = Math.abs(mq.x1 - mq.x0), rh = Math.abs(mq.y1 - mq.y0);
      if (ry > 20 && ry < H) {
        tlCtx.fillStyle = 'rgba(56, 189, 248, 0.16)';
        tlCtx.fillRect(rx, ry, rw, rh);
        tlCtx.strokeStyle = '#38BDF8'; tlCtx.strokeRect(rx, ry, rw, rh);
      }
    }

    document.getElementById('tl-counter').textContent =
      t >= 20.95 ? `✓ Completed All ${builtClips} Clips • Ready` : `Live Assembling: ${builtClips}/36 Clips...`;

    // Playhead
    const phX = secToX(t);
    tlCtx.strokeStyle = '#34D399'; tlCtx.lineWidth = 2;
    tlCtx.beginPath(); tlCtx.moveTo(phX, 8); tlCtx.lineTo(phX, H); tlCtx.stroke();
    tlCtx.fillStyle = '#10B981';
    tlCtx.beginPath();
    tlCtx.moveTo(phX-6,3); tlCtx.lineTo(phX+6,3); tlCtx.lineTo(phX+6,12); tlCtx.lineTo(phX,18); tlCtx.lineTo(phX-6,12);
    tlCtx.closePath(); tlCtx.fill();
  }

  // ==================== 6. DRAW VECTOR OS CURSORS + AGENT BADGES ====================
  function drawCursor(ctx, x, y, sc, ctype, badge) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(sc, sc);
    ctx.shadowColor = 'rgba(0,0,0,0.62)';
    ctx.shadowBlur = 4; ctx.shadowOffsetX = 1; ctx.shadowOffsetY = 2;

    if (ctype === 'ew-resize') {
      ctx.beginPath();
      ctx.moveTo(-9,0); ctx.lineTo(-4,-5); ctx.lineTo(-4,-2);
      ctx.lineTo(4,-2); ctx.lineTo(4,-5); ctx.lineTo(9,0);
      ctx.lineTo(4,5);  ctx.lineTo(4,2);  ctx.lineTo(-4,2); ctx.lineTo(-4,5);
      ctx.closePath();
      ctx.fillStyle = '#FFF'; ctx.fill();
      ctx.lineWidth = 1.3; ctx.strokeStyle = '#090C12'; ctx.stroke();
    } else if (ctype === 'cross') {
      ctx.strokeStyle = '#000'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(-7,0); ctx.lineTo(7,0); ctx.moveTo(0,-7); ctx.lineTo(0,7); ctx.stroke();
      ctx.strokeStyle = '#FFF'; ctx.lineWidth = 1.3; ctx.stroke();
    } else if (ctype === 'ibeam') {
      ctx.strokeStyle = '#000'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(-4,-7); ctx.lineTo(4,-7); ctx.moveTo(0,-7); ctx.lineTo(0,7); ctx.moveTo(-4,7); ctx.lineTo(4,7); ctx.stroke();
      ctx.strokeStyle = '#FFF'; ctx.lineWidth = 1.3; ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.moveTo(0,0); ctx.lineTo(0,17.2); ctx.lineTo(4.5,13.2);
      ctx.lineTo(7.6,19.8); ctx.lineTo(10.2,18.6); ctx.lineTo(7.0,12.0); ctx.lineTo(12.2,12.0);
      ctx.closePath();
      ctx.fillStyle = '#FFFFFF'; ctx.fill();
      ctx.lineWidth = 1.35; ctx.strokeStyle = '#0B0F17'; ctx.stroke();
    }

    if (badge) {
      ctx.shadowBlur = 3;
      ctx.font = 'bold 8.5px "Segoe UI", sans-serif';
      const tw = ctx.measureText(badge.label).width;
      ctx.fillStyle = badge.color;
      ctx.beginPath(); ctx.roundRect(11, 12, tw + 9, 13.5, 4); ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 0.8; ctx.stroke();
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(badge.label, 15.5, 21.8);
    }
    ctx.restore();
  }

  // ==================== 7. MASTER 60FPS FRAME RENDERER ====================
  const previewImg = document.getElementById('chihang-video-img');
  const snapBox    = document.getElementById('drop-snap-box');

  const jsxLines = [
    '<span class="cm">// 84-Agent Live Voice-Follow Thrower (Ps + Ae + Ai + Gemini -> Pr)</span>',
    'voiceStream.<span class="fn">onPhraseAhead</span>(<span class="nu">450</span>, <span class="kw">async</span> (beat) => {',
    '  <span class="kw">const</span> card = <span class="kw">await</span> photoshop.<span class="fn">craftCutoutLayer</span>(beat.sku);',
    '  <span class="kw">const</span> broll = <span class="kw">await</span> geminiFlow.<span class="fn">fetch9x16Clip</span>(beat.scene);',
    '  <span class="kw">const</span> pill = illustrator.<span class="fn">renderSubtitleVector</span>(beat.words);',
    '  await swarm.<span class="fn">throwIntoLiveMonitor</span>([card, broll, pill]);',
    '  premiere.sequence.<span class="fn">snapToPlayhead</span>({ lufs: <span class="nu">-14.2</span>, fps: <span class="nu">60</span> });',
    '});'
  ];

  const cmsCopy = '5 sản phẩm cần biết cho phụ nữ sau tuổi 25! Chăm sóc chủ động từ bên trong cùng Chị Hằng — Hằng Thu Pharma';

  window.renderFrame = async function (frameIdx) {
    const f = Math.max(0, Math.min(TOTAL_FRAMES - 1, frameIdx));
    const t = f / FPS;
    const aeMode = (t >= 2.8 && t < 6.4) || (t >= 11.0 && t < 15.6);

    // 1. Top Desktop Multi-App Jumping
    const ls = getLayoutAt(t, f);
    for (const k of WIN_IDS) {
      const el = document.getElementById(`win-${k}`);
      const r = ls.rects[k];
      el.style.left = `${r.x.toFixed(1)}px`; el.style.top = `${r.y.toFixed(1)}px`;
      el.style.width = `${r.w.toFixed(1)}px`; el.style.height = `${r.h.toFixed(1)}px`;
      el.style.zIndex = String(r.z); el.style.transform = `scale(${r.sc.toFixed(3)})`;
      el.className = k === ls.focus ? 'app-win focused' : 'app-win';
    }
    const hud = document.getElementById('alt-tab-hud');
    if (ls.showAltTab) {
      hud.style.display = 'flex';
      for (let a = 0; a < 6; a++) document.getElementById(`at-${a}`).className = a === ls.atIdx ? 'at-item sel' : 'at-item';
    } else {
      hud.style.display = 'none';
    }
    document.getElementById('sys-ops').textContent = `${295 + Math.floor(Math.sin(t*5)*32 + 32)} ops/s`;

    drawPhotoshop(f, t);
    drawIllustrator(t);
    drawAeGraph(t);

    const typed = Math.floor((t * 28) % (cmsCopy.length + 16));
    document.getElementById('cms-type').textContent = cmsCopy.slice(0, Math.min(cmsCopy.length, typed)) + (f % 24 < 12 ? '▋' : '');
    const curL = Math.floor(t * 3.5) % jsxLines.length;
    document.getElementById('ide-lines').innerHTML = jsxLines.map((h, i) =>
      `<div class="cl add${i === curL ? ' cur' : ''}"><span style="color:#475569;margin-right:6px;">${i+1}</span>${h}</div>`
    ).join('');

    // Live Throw Feed inside Swarm Window
    const recentThrows = THROW_EVENTS.filter(e => t >= e.t0).slice(-6);
    document.getElementById('swarm-rows').innerHTML = recentThrows.map((ev, idx) => {
      const st = t < ev.tLand ? 'THROWING ↘' : 'LOCKED ✓';
      const nm = ev.kind === 'txt' ? `"${ev.text.slice(0, 24)}..."` : (ev.tlLbl || ev.img);
      return `<div class="srow${idx === recentThrows.length - 1 ? ' hot' : ''}"><span><b style="color:#67E8F9">[${ev.agent}]</b> ${nm}</span><span style="color:#34D399;font-weight:700;">${st}</span></div>`;
    }).join('');

    // 2. Bottom Premiere Pro <-> After Effects Switch & Inspector
    const appBadge = document.getElementById('nle-app-badge');
    appBadge.className = aeMode ? 'cc-badge cc-ae' : 'cc-badge cc-pr';
    appBadge.textContent = aeMode ? 'Ae' : 'Pr';
    document.getElementById('nle-app-name').textContent = aeMode ? 'Adobe After Effects 2026' : 'Adobe Premiere Pro 2026';

    for (let b = 0; b < 8; b++) {
      document.getElementById(`bin-${b}`).className = b === (Math.floor(t * 2.2) % 8) ? 'bin-item sel' : 'bin-item';
    }
    const sDefs = [
      [99.5, 102.5, v => `${v.toFixed(1)}%`],
      [18, 28, v => `${v.toFixed(1)}`],
      [3.8, 5.4, v => `+${v.toFixed(1)}`],
      [9.5, 13.0, v => `+${v.toFixed(1)}`],
      [2.0, 2.9, v => `+${v.toFixed(1)}dB`]
    ];
    for (let s = 0; s < 5; s++) {
      const u = 0.5 + 0.35 * Math.sin(t * 2.5 + s * 1.2);
      const val = lerp(sDefs[s][0], sDefs[s][1], u);
      document.getElementById(`sl${s}f`).style.width = `${(u*100).toFixed(1)}%`;
      document.getElementById(`sl${s}t`).style.left = `${(u*100).toFixed(1)}%`;
      document.getElementById(`sl${s}v`).textContent = sDefs[s][2](val);
    }
    for (let c = 0; c < 3; c++) {
      document.getElementById(`cwd${c}`).style.transform =
        `translate(calc(-50% + ${(Math.sin(t*2.4+c*2)*5).toFixed(1)}px), calc(-50% + ${(Math.cos(t*1.9+c)*5).toFixed(1)}px))`;
    }

    // 3. Live View Monitor: Real Chị Hằng Video + Synced VU Meters
    const secI = Math.floor(t), frmI = Math.floor((t - secI) * 60);
    document.getElementById('mon-tc').textContent = `00:00:${String(secI).padStart(2, '0')}:${String(frmI).padStart(2, '0')}`;
    document.getElementById('mon-mode-pill').textContent =
      t >= 20.95 ? '✓ RENDER COMPLETE • 1080P 60FPS'
      : aeMode   ? 'Ae • LIVE THROW SYNC 60FPS'
                 : 'Pr • LIVE THROW SYNC 60FPS';

    const expBtn = document.getElementById('export-btn');
    if (t >= 21.02) { expBtn.textContent = '✓ Exported 60fps'; expBtn.className = 'adobe-export-btn done'; }
    else { expBtn.textContent = 'Export 60fps'; expBtn.className = 'adobe-export-btn'; }

    const ampL = window.AUDIO_DATA ? window.AUDIO_DATA.env_l[f] : 0.1;
    const ampR = window.AUDIO_DATA ? window.AUDIO_DATA.env_r[f] : 0.1;
    document.getElementById('vu-l').style.height = `${Math.min(96, Math.max(5, ampL * 92 + 5)).toFixed(1)}%`;
    document.getElementById('vu-r').style.height = `${Math.min(96, Math.max(5, ampR * 92 + 5)).toFixed(1)}%`;
    document.getElementById('vu-db').textContent = `${(ampL < 0.02 ? -48.0 : -24 + Math.max(ampL, ampR) * 14).toFixed(1)}dB`;
    drawScopes(t, Math.max(ampL, ampR));

    const safeVidFrame = Math.min(1258, f + 1);
    const targetSrc = `assets/preview_frames/f_${String(safeVidFrame).padStart(4, '0')}.jpg`;
    if (!previewImg.src.endsWith(targetSrc)) {
      await new Promise((resolve) => {
        previewImg.onload = resolve;
        previewImg.onerror = resolve;
        previewImg.src = targetSrc;
      });
    }

    // Keep top wall clean WHILE major cards/B-rolls are still flying in mid-air BEFORE tLand!
    const preThrowMask = document.getElementById('mask-pre-throw');
    const hideTopUntilLand =
      (t < 0.54) ||
      (t >= 2.65 && t < 2.95) ||
      (t >= 6.90 && t < 7.55) ||
      (t >= 14.00 && t < 14.82);
    preThrowMask.style.display = hideTopUntilLand ? 'block' : 'none';

    // 4. Draw Flying Thrown Cards / B-Rolls / Text Pills + Drop-Snap Wireframe + 84 Swarm Cursors!
    fxCtx.clearRect(0, 0, 1080, 1920);
    const activeMarquees = [];

    // 4A. Render background 76 Swarm Cursors first
    for (const sc of swarmCursors) {
      let wp = null;
      for (let k = 0; k < sc.wps.length; k++) {
        const w = sc.wps[k];
        if (f >= w.f0 && f < w.f2) { wp = w; break; }
      }
      if (!wp) continue;

      let cx, cy, cscale = 1.0;
      if (f < wp.f1) {
        const u = minJerk((f - wp.f0) / Math.max(1, wp.f1 - wp.f0));
        const mx = (wp.x0 + wp.x1)*0.5 - (wp.y1 - wp.y0)*0.12 + wp.arc;
        const my = (wp.y0 + wp.y1)*0.5 + (wp.x1 - wp.x0)*0.12;
        const inv = 1 - u;
        cx = inv*inv*wp.x0 + 2*inv*u*mx + u*u*wp.x1;
        cy = inv*inv*wp.y0 + 2*inv*u*my + u*u*wp.y1;

        if (wp.carry && tImgs[wp.carryKey] && tImgs[wp.carryKey].complete) {
          fxCtx.save();
          fxCtx.globalAlpha = 0.84;
          fxCtx.drawImage(tImgs[wp.carryKey], cx + 8, cy + 8, 58, 38);
          fxCtx.strokeStyle = '#38BDF8'; fxCtx.lineWidth = 1.4;
          fxCtx.strokeRect(cx + 8, cy + 8, 58, 38);
          fxCtx.restore();
        }
      } else {
        const hu = minJerk((f - wp.f1) / Math.max(1, wp.f2 - wp.f1));
        cx = wp.x1 + wp.dx * hu;
        cy = wp.y1 + wp.dy * hu;
        const hf = f - wp.f1;
        if (hf < 5) cscale = 0.85;
        if (hf < 10) {
          fxCtx.strokeStyle = `rgba(56,189,248,${(1 - hf/10)*0.65})`;
          fxCtx.lineWidth = 1.3;
          fxCtx.beginPath(); fxCtx.arc(cx, cy, 3 + hf*1.3, 0, Math.PI*2); fxCtx.stroke();
        }
        if (wp.isMq) activeMarquees.push({ x0: wp.x1, y0: wp.y1, x1: cx, y1: cy });
      }
      drawCursor(fxCtx, cx, cy, cscale, wp.ctype, sc.badge);
    }

    // 4B. Render Active Live-Throw Events ON TOP (Flying Graphic + Motion Trail + Thrower Agent Cursor + Landing Snap!)
    let snapRect = null;
    for (const ev of THROW_EVENTS) {
      if (t >= ev.t0 && t <= ev.tLand) {
        const u = minJerk((t - ev.t0) / (ev.tLand - ev.t0));
        const inv = 1 - u;
        const mx = (ev.sx + ev.dx) * 0.5 + ev.arcX;
        const my = (ev.sy + ev.dy) * 0.45;
        const cx = inv*inv*ev.sx + 2*inv*u*mx + u*u*ev.dx;
        const cy = inv*inv*ev.sy + 2*inv*u*my + u*u*ev.dy;
        const cw = lerp(ev.dw * 0.72, ev.dw, u);
        const ch = lerp(ev.dh * 0.72, ev.dh, u);

        // Glowing cyan motion-arc trail from Top App to Live View!
        fxCtx.save();
        fxCtx.strokeStyle = 'rgba(0, 229, 255, 0.52)';
        fxCtx.lineWidth = 2.2;
        fxCtx.setLineDash([6, 4]);
        fxCtx.beginPath();
        fxCtx.moveTo(ev.sx, ev.sy);
        fxCtx.quadraticCurveTo(mx, my, cx + cw * 0.5, cy + ch * 0.5);
        fxCtx.stroke();
        fxCtx.restore();

        // Draw the actual flying Card / B-Roll / Text Pill!
        fxCtx.save();
        fxCtx.shadowColor = 'rgba(0, 229, 255, 0.65)';
        fxCtx.shadowBlur = 16;
        if (ev.kind === 'img' && tImgs[ev.img] && tImgs[ev.img].complete) {
          fxCtx.globalAlpha = 0.95;
          fxCtx.drawImage(tImgs[ev.img], cx, cy, cw, ch);
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2;
          fxCtx.strokeRect(cx, cy, cw, ch);
        } else if (ev.kind === 'txt') {
          fxCtx.fillStyle = 'rgba(255, 255, 255, 0.96)';
          fxCtx.beginPath(); fxCtx.roundRect(cx, cy, cw, ch, 14); fxCtx.fill();
          fxCtx.strokeStyle = '#00E5FF'; fxCtx.lineWidth = 2; fxCtx.stroke();
          fxCtx.shadowBlur = 0;
          fxCtx.fillStyle = '#0F172A'; fxCtx.font = '800 10px "Segoe UI", sans-serif';
          fxCtx.textAlign = 'center';
          fxCtx.fillText(ev.text, cx + cw * 0.5, cy + 17.5);
          fxCtx.textAlign = 'left';
        }
        fxCtx.restore();

        // Draw Thrower Lead Cursor + Helper Cursor carrying it!
        drawCursor(fxCtx, cx + cw * 0.18, cy + 6, 1.05, 'hand', { label: ev.agent, color: ev.color });
        drawCursor(fxCtx, cx + cw * 0.82, cy + ch - 4, 0.95, 'hand', null);
      } else if (t > ev.tLand && t <= ev.tLand + 0.22) {
        // Landing Snap Flash inside Live View Monitor (convert stage coords -> viewport local coords!)
        snapRect = { l: ev.dx - 388, t: ev.dy - 1012, w: ev.dw, h: ev.dh };
        // Retreating Thrower Cursor after release
        const ru = minJerk((t - ev.tLand) / 0.22);
        const rx = lerp(ev.dx + ev.dw * 0.85, ev.dx + ev.dw + 55, ru);
        const ry = lerp(ev.dy + 10, ev.dy - 45, ru);
        drawCursor(fxCtx, rx, ry, 1.0, 'arrow', { label: ev.agent, color: ev.color });
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

    // 5. Draw Timeline
    drawTimeline(t, aeMode, activeMarquees);
  };
})();
