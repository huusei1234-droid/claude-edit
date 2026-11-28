// V3 Engine: 100% Cause-and-Effect Timeline Build-From-Zero + Task-Locked Multi-Agent Cursors + [SPACE] Smooth Playback
(function () {
  const FPS = 60;
  const TOTAL_FRAMES = 1821; // 30.35s @ 60fps (0..9.00s Build & Scrub, 9.00..29.95s Smooth [Space] Play, 29.95..30.35s Stop & Export)
  const SEQ_DUR = 21.0;      // 21.0s Sequence duration on Timeline
  const PLAY_START_T = 9.00; // Exact moment [SPACE] Play starts!
  const PLAY_END_T   = 29.95;// Exact moment 4th sentence finishes cleanly!

  const HDR_W = 112;
  const TL_W  = 956; // 112 + 956 = 1068
  const TL_STAGE_Y = 1522;
  const secToX = (sec) => HDR_W + (Math.max(0, Math.min(SEQ_DUR, sec)) / SEQ_DUR) * TL_W;

  function minJerk(u) {
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    return u * u * u * (10 + u * (-15 + 6 * u));
  }

  function lerp(a, b, u) { return a + (b - a) * u; }

  // Preload 21 Sequence Filmstrip Thumbs & Real HTPM Product Assets
  const stripImgs = [];
  for (let i = 0; i < 21; i++) {
    const im = new Image();
    im.src = `assets/thumbs/strip_${String(i).padStart(2, '0')}.jpg`;
    stripImgs.push(im);
  }
  const psAssetPaths = [
    'assets/thumbs/SP_WHITESKIN_COMBO_CUTOUT.png',
    'assets/thumbs/SP_ROMANCE_LOVE_CUTOUT.png',
    'assets/thumbs/SP_GEL_PHU_KHANG_CUTOUT.png',
    'assets/thumbs/poster_03.jpg'
  ];
  const psImgs = psAssetPaths.map(p => { const im = new Image(); im.src = p; return im; });

  const ghostImgs = {
    raw:   (() => { const i = new Image(); i.src = 'assets/thumbs/bin_01_desk.jpg'; return i; })(),
    ae1:   (() => { const i = new Image(); i.src = 'assets/thumbs/bin_07_sp_ban.jpg'; return i; })(),
    psd1:  (() => { const i = new Image(); i.src = 'assets/thumbs/SP_WHITESKIN_COMBO_CUTOUT.png'; return i; })(),
    psd2:  (() => { const i = new Image(); i.src = 'assets/thumbs/bin_05_gelpk.jpg'; return i; })(),
    nlh:   (() => { const i = new Image(); i.src = 'assets/thumbs/bin_08_nlh_real.jpg'; return i; })(),
    lut:   (() => { const i = new Image(); i.src = 'assets/thumbs/bin_03_laptop_b.jpg'; return i; })(),
    audio: (() => { const i = new Image(); i.src = 'assets/thumbs/bin_04_exec.jpg'; return i; })()
  };

  // ==================== 1. PLAYHEAD SCRUB & SPACEBAR TIMELINE SCHEDULE ====================
  // Act 1 (0.00..9.00s): Playhead is STOPPED or SCRUBBED by Cursor!
  // Act 2 (9.00..29.95s): Playhead plays smoothly at exact 1.000x speed!
  const phKeyframes = [
    { t: 0.00, sec: 0.00 },
    { t: 0.65, sec: 0.00 }, // V1 drops at 0.65s -> jumps to 0.45s
    { t: 0.75, sec: 0.45 },
    { t: 1.25, sec: 0.45 }, // Hold while Razor slices
    { t: 1.75, sec: 0.90 },
    { t: 2.20, sec: 7.40 }, // Fast scrub right across V1 (Scrub Chirp #1 at 1.95s!)
    { t: 2.75, sec: 2.35 }, // Scrub back to 2.35s & park -> wait for V2 Stage_01 drop at 3.10s!
    { t: 3.55, sec: 2.35 }, // Stage_01 pops ON right at 3.10s while parked here!
    { t: 4.05, sec: 6.80 }, // Scrub right into EMPTY V2 gap (6.80s > 4.7s) -> Top Card VANISHES!
    { t: 4.55, sec: 6.80 }, // Stage_02 drops at 4.35s -> Top Card (5 Icons) POPS ON right here!
    { t: 4.80, sec: 12.60}, // Scrub right into EMPTY V2 gap (12.60s) -> vanishes briefly until 4.85s drop!
    { t: 5.35, sec: 12.60}, // Stage_03 drops at 4.85s & Stage_04 at 5.25s!
    { t: 5.55, sec: 2.45 }, // Scrub back to 2.45s -> wait for V3 Captions cascade (5.60..6.90s)!
    { t: 7.05, sec: 2.45 }, // Caption_02 drops at 5.74s -> Subtitle POPS ON Chị Hằng's blazer!
    { t: 7.65, sec: 5.80 }, // Scrub to 5.80s while V4 Lumetri LUT drops (7.20s) & grades S-Log -> Color!
    { t: 8.62, sec: 5.80 }, // Finish BGM ducking & SFX placement
    { t: 8.86, sec: 0.00 }, // REWIND Playhead all the way to 00:00:00:00!
    { t: 9.00, sec: 0.00 }, // [SPACE] pressed at 8.92s -> Playback begins at 9.00s!
    { t: 29.95,sec: 20.95}, // Exact 1.000x linear real-time playback (20.95s of 4 complete sentences!)
    { t: 30.35,sec: 20.95}  // Paused cleanly after [SPACE] stop at 29.96s!
  ];

  function getPlayheadSec(t) {
    if (t >= PLAY_START_T && t <= PLAY_END_T) {
      return t - PLAY_START_T; // Exact 1.0000x linear speed!
    }
    for (let i = 0; i < phKeyframes.length - 1; i++) {
      const a = phKeyframes[i], b = phKeyframes[i + 1];
      if (t >= a.t && t <= b.t) {
        const u = minJerk((t - a.t) / Math.max(0.001, b.t - a.t));
        return lerp(a.sec, b.sec, u);
      }
    }
    return 20.95;
  }

  // ==================== 2. TIMELINE STATEFUL CLIPS DEFINITIONS ====================
  // Every clip has an exact tDrop (invisible before tDrop!), optional trim animation [tTrim0..tTrim1] from sEnd0 -> sEnd1!
  const v1State = {
    tDrop: 0.65,
    cuts: [
      { sec: 5.0,  tCut: 1.25, lbl: 'CamA_NoiTiet.mp4' },
      { sec: 11.2, tCut: 1.48, lbl: 'CamA_CanBang.mp4' },
      { sec: 16.0, tCut: 1.70, lbl: 'CamA_NangLuong.mp4' }
    ]
  };

  const v2StageClips = [
    { id: 'st0', tDrop: 3.10, s: 0.0,  e0: 3.8,  e1: 4.7,  tTr0: 3.18, tTr1: 3.52, lbl: '[Ae] Stage01_5SanPham_Hook.aep', srcX: 72,  srcY: 1286, g: 'ae1' },
    { id: 'st1', tDrop: 4.35, s: 4.7,  e0: 9.6,  e1: 11.1, tTr0: 4.42, tTr1: 4.74, lbl: '[Ae] Stage02_5NenTang_Icons.aep', srcX: 320, srcY: 260,  g: 'psd1' },
    { id: 'st2', tDrop: 4.85, s: 11.1, e0: 14.5, e1: 15.8, tTr0: 4.92, tTr1: 5.18, lbl: '[Ae] Stage03_CanBang_Scale.aep',  srcX: 200, srcY: 1168, g: 'psd2' },
    { id: 'st3', tDrop: 5.25, s: 15.8, e0: 19.4, e1: 20.95,tTr0: 5.32, tTr1: 5.58, lbl: '[Ps/Ae] Stage04_NangLuong.aep',   srcX: 200, srcY: 1286, g: 'nlh' }
  ];

  const v3Captions = Array.from({ length: 10 }, (_, i) => ({
    id: `cap${i}`,
    tDrop: 5.60 + i * 0.14,
    s: i * 2.09 + 0.04,
    e0: (i + 1) * 2.09 - 0.35,
    e1: (i + 1) * 2.09 - 0.04,
    tTr0: 5.66 + i * 0.14,
    tTr1: 5.86 + i * 0.14,
    lbl: `Sub_${String(i + 1).padStart(2, '0')}`
  }));

  const v4LutLayer = {
    tDrop: 7.20,
    s: 0.0, e0: 15.0, e1: 20.98, tTr0: 7.26, tTr1: 7.62,
    lbl: 'Lumetri_WarmStudio_Skin96.cube [Adjustment]'
  };

  const a2BgmLayer = {
    tDrop: 8.15,
    tDuck0: 8.25, tDuck1: 8.65,
    lbl: 'BGM_Fresh_Wellness_TVC.wav [Sidechain -11dB]'
  };

  const a3SfxClips = [0.2, 2.1, 4.7, 7.2, 11.1, 13.9, 16.0, 18.8].map((st, idx) => ({
    tDrop: 8.18 + idx * 0.06,
    s: st,
    lbl: idx % 2 === 0 ? 'Whoosh' : 'Pop'
  }));

  function clipEndAt(c, t) {
    if (t < c.tTr0) return c.e0;
    if (t >= c.tTr1) return c.e1;
    return lerp(c.e0, c.e1, minJerk((t - c.tTr0) / (c.tTr1 - c.tTr0)));
  }

  // ==================== 3. SLIDER & COLOR GRADE STATE (ONLY MOVES WHEN DRAGGED!) ====================
  // 5 Sliders: Scale, Temp, Exposure, Contrast, Saturation
  const sliderAnim = [
    { t0: 3.15, t1: 3.55, u0: 0.36, u1: 0.50, v0: 96.0, v1: 100.0, fmt: v => `${v.toFixed(1)}%` }, // Scale nudged on V2 card drop
    { t0: 7.28, t1: 7.85, u0: 0.50, u1: 0.74, v0: 0.0,  v1: 4.5,   fmt: v => (v>0?'+':'')+v.toFixed(1) }, // Temp
    { t0: 7.36, t1: 7.95, u0: 0.50, u1: 0.68, v0: 0.00, v1: 0.32,  fmt: v => (v>0?'+':'')+v.toFixed(2) }, // Exposure
    { t0: 7.44, t1: 8.05, u0: 0.50, u1: 0.72, v0: 0.0,  v1: 11.5,  fmt: v => (v>0?'+':'')+v.toFixed(1) }, // Contrast
    { t0: 7.52, t1: 8.15, u0: 0.22, u1: 0.66, v0: 52.0, v1: 104.0, fmt: v => `${v.toFixed(1)}%` }  // Saturation
  ];

  function getSliderState(idx, t) {
    const sa = sliderAnim[idx];
    // Optional subtle fine-tune touch at t = 14.5..15.1s on Temp (idx=1) ahead of playback
    let u = t < sa.t0 ? sa.u0 : t >= sa.t1 ? sa.u1 : lerp(sa.u0, sa.u1, minJerk((t - sa.t0) / (sa.t1 - sa.t0)));
    let v = t < sa.t0 ? sa.v0 : t >= sa.t1 ? sa.v1 : lerp(sa.v0, sa.v1, minJerk((t - sa.t0) / (sa.t1 - sa.t0)));
    if (idx === 1 && t >= 14.5 && t <= 15.2) {
      const k = Math.sin(((t - 14.5) / 0.7) * Math.PI);
      u += k * 0.04; v += k * 0.4;
    }
    return { u, txt: sa.fmt(v) };
  }

  function getColorGradeMix(t, phSec) {
    if (t < v4LutLayer.tDrop) return 0.0;
    const lutEnd = clipEndAt(v4LutLayer, t);
    if (phSec > lutEnd) return 0.0;
    if (t >= 8.15) return 1.0;
    return minJerk((t - 7.25) / 0.90);
  }

  // ==================== 4. BUILD 100% TASK-BOUND CURSOR CHOREOGRAPHY ====================
  // ZERO random wandering! Every cursor executes a concrete list of timed tasks (move -> hold/drag -> exit or next task).
  const agents = [];
  function createAgent() {
    const a = { tasks: [] };
    agents.push(a);
    return a;
  }
  function addTask(agent, t0, tMove, tEnd, x0, y0, x1, y1, x2, y2, ctype, ghostKey) {
    agent.tasks.push({ t0, tMove, tEnd, x0, y0, x1, y1, x2, y2, ctype: ctype || 'arrow', ghostKey: ghostKey || null });
  }

  // --- AGENT 0: Lead Sequence Builder (Drops V1+A1, Drops V4 LUT, Clicks Export at 30.14s!) ---
  const agLead = createAgent();
  addTask(agLead, 0.12, 0.30, 0.65, 340, 1180, 72, 1050, 210, 1699, 'hand', 'raw'); // Drag Raw V1 from Bin-0 -> Track V1!
  addTask(agLead, 0.70, 1.05, 1.80, 210, 1699, 122, 1509, 122, 1509, 'hand');       // Click Razor Tool [C]
  addTask(agLead, 2.80, 3.15, 3.55, 122, 1509, 840 + 0.36*178, 1018, 840 + 0.50*178, 1018, 'ew-resize'); // Drag Scale slider!
  addTask(agLead, 6.75, 6.95, 7.20, 929, 1018, 72, 1404, 240, 1566, 'hand', 'lut'); // Drag Lumetri .cube from Bin-6 -> Track V4!
  addTask(agLead, 7.22, 7.26, 7.62, 240, 1566, secToX(15.0), 1566, secToX(20.98), 1566, 'ew-resize'); // Stretch V4 LUT across full 21s!
  addTask(agLead, 29.50,29.92,30.02,820, 1380, 520, 1483, 520, 1483, 'hand');       // Click Pause [SPACE] at 29.96s!
  addTask(agLead, 30.03,30.13,30.34,520, 1483, 1015,957,  1015,957,  'hand');       // Click Queue in Media Encoder!

  // --- AGENT 1: Dedicated Playhead Scrubber & [SPACE] Play Trigger! ---
  // Dynamically follows getPlayheadSec(t) during Act 1, then clicks Play at 8.92s!
  const agPlayhead = { isPlayheadAgent: true };
  agents.push(agPlayhead);

  // --- AGENT 2: Razor Cutter (Clicks exact 3 split points on V1 at 1.25s, 1.48s, 1.70s!) ---
  const agRazor = createAgent();
  addTask(agRazor, 0.95, 1.22, 1.30, 122, 1509, secToX(5.0),  1699, secToX(5.0),  1699, 'cross');
  addTask(agRazor, 1.31, 1.45, 1.53, secToX(5.0), 1699, secToX(11.2), 1699, secToX(11.2), 1699, 'cross');
  addTask(agRazor, 1.54, 1.67, 1.80, secToX(11.2),1699, secToX(16.0), 1699, secToX(16.0), 1699, 'cross');
  addTask(agRazor, 1.82, 2.05, 2.20, secToX(16.0),1699, 48, 1509, 48, 1509, 'hand'); // Switch back to Selection [V]

  // --- AGENTS 3..6: 4 Stage Card Builders (Drag from Top Photoshop/AE/Bin -> Drop onto V2 -> Trim right edge!) ---
  v2StageClips.forEach((sc) => {
    const ag = createAgent();
    const dropX = secToX((sc.s + sc.e0) * 0.5);
    addTask(ag, sc.tDrop - 0.52, sc.tDrop - 0.34, sc.tDrop, sc.srcX, sc.srcY + 40, sc.srcX, sc.srcY, dropX, 1645, 'hand', sc.g);
    addTask(ag, sc.tDrop + 0.02, sc.tTr0, sc.tTr1, dropX, 1645, secToX(sc.e0), 1645, secToX(sc.e1), 1645, 'ew-resize');
  });

  // --- AGENTS 7..16: 10 Parallel Subtitle Builders (Snap Caption_01..10 onto V3 & Trim right edges!) ---
  v3Captions.forEach((cp, idx) => {
    const ag = createAgent();
    const startX = 180 + (idx % 5) * 165;
    const startY = 1495;
    const dropX = secToX((cp.s + cp.e0) * 0.5);
    addTask(ag, cp.tDrop - 0.35, cp.tDrop - 0.22, cp.tDrop, startX, startY, startX, 1509, dropX, 1603, 'hand');
    addTask(ag, cp.tDrop + 0.02, cp.tTr0, cp.tTr1, dropX, 1603, secToX(cp.e0), 1603, secToX(cp.e1), 1603, 'ew-resize');
    // Subtle polish ahead of playhead during Act 2 for 2 captions
    if (idx === 7) {
      addTask(ag, 11.8, 12.2, 12.7, 900, 1560, secToX(cp.e1), 1603, secToX(cp.e1) + 3, 1603, 'ew-resize');
    }
  });

  // --- AGENTS 17..21: 5 Lumetri Color & Color-Wheel Graders (Physically pull sliders 1..4 & Midtone Wheel!) ---
  [1, 2, 3, 4].forEach((sIdx) => {
    const sa = sliderAnim[sIdx];
    const sy = 1018 + sIdx * 19;
    const ag = createAgent();
    addTask(ag, sa.t0 - 0.28, sa.t0, sa.t1, 960, sy + 40, 840 + sa.u0 * 178, sy, 840 + sa.u1 * 178, sy, 'ew-resize');
    if (sIdx === 1) {
      addTask(ag, 14.3, 14.5, 15.2, 950, 1080, 840 + sa.u1 * 178, sy, 840 + (sa.u1 + 0.04) * 178, sy, 'ew-resize');
    }
  });
  const agWheel = createAgent();
  addTask(agWheel, 7.45, 7.65, 8.20, 918, 1380, 918, 1335, 924, 1330, 'cross'); // Pull Midtones Color Wheel warm!
  addTask(agWheel, 15.0, 15.4, 16.4, 924, 1330, 880, 1200, 945, 1185, 'hand');  // Inspect AE Bezier Speed Graph handle!

  // --- AGENTS 22..32: Audio BGM Drop + 3 Ducking Keyframe Pullers + 7 SFX Placer Cursors ---
  const agBgm = createAgent();
  addTask(agBgm, 7.75, 7.90, 8.15, 200, 1404, 200, 1404, 340, 1814, 'hand', 'audio');
  [4.0, 10.5, 17.2].forEach((secKf, k) => {
    const agKf = createAgent();
    const kx = secToX(secKf);
    addTask(agKf, 8.16 + k*0.05, 8.25 + k*0.05, 8.65, kx, 1790, kx, 1806, kx, 1820, 'cross'); // Pull ducking curve down!
  });
  a3SfxClips.forEach((sc, idx) => {
    const agSfx = createAgent();
    const sx = secToX(sc.s) + 16;
    addTask(agSfx, sc.tDrop - 0.32, sc.tDrop - 0.18, sc.tDrop + 0.08, 200, 1404, 200, 1404, sx, 1859, 'hand');
    if (idx === 6) {
      addTask(agSfx, 17.2, 17.6, 18.2, 860, 1880, sx, 1859, sx + 4, 1859, 'hand');
    }
  });

  // --- AGENTS 33..46: 14 Purposeful Top-Desktop Multi-App Operators (Photoshop, Illustrator, CMS, Gemini, IDE, Encoder) ---
  const topTargets = [
    // Photoshop Brush, Curves, Layers & Select Subject button
    [180, 240, 235, 265, 'cross'], [385, 125, 398, 112, 'cross'], [520, 165, 520, 215, 'hand'], [220, 442, 220, 442, 'hand'],
    // Illustrator Bezier Anchor Pulls
    [760, 185, 782, 198, 'cross'], [845, 210, 830, 195, 'cross'], [790, 310, 790, 310, 'ibeam'],
    // Chrome CMS SKU Select, Input Box Click, Table Row Check
    [110, 560, 265, 560, 'hand'], [180, 648, 310, 648, 'ibeam'], [440, 715, 440, 742, 'hand'],
    // Gemini Asset Queue & Bridge Sync
    [680, 580, 910, 580, 'hand'], [680, 740, 910, 740, 'hand'],
    // IDE Code Line Edit & Media Encoder Queue Check
    [240, 355, 320, 385, 'ibeam'], [780, 340, 960, 365, 'hand']
  ];
  topTargets.forEach((tt, idx) => {
    const ag = createAgent();
    let tCur = 0.10 + (idx % 5) * 0.22;
    let flip = false;
    while (tCur < 29.8) {
      const xA = flip ? tt[2] : tt[0], yA = flip ? tt[3] : tt[1];
      const xB = flip ? tt[0] : tt[2], yB = flip ? tt[1] : tt[3];
      const mDur = 0.42 + (idx % 3) * 0.14;
      const hDur = 0.28 + (idx % 4) * 0.12;
      addTask(ag, tCur, tCur + mDur, tCur + mDur + hDur, xA, yA, xB, yB, xB + (tt[4]==='cross'?8:0), yB, tt[4]);
      tCur += mDur + hDur + 0.18;
      flip = !flip;
    }
  });

  // ==================== 5. TOP MULTI-APP RAPID WINDOW SWITCHING ====================
  const TOP_LAYOUTS = [
    { focus: 'ps', dock: 'dk-ps', atIdx: 0, rects: {
      ps:{x:14,y:12,w:640,h:468,z:30,s:1.00}, ai:{x:548,y:18,w:518,h:396,z:22,s:0.98},
      cms:{x:18,y:452,w:530,h:436,z:24,s:0.99}, gem:{x:552,y:456,w:514,h:430,z:23,s:0.98},
      ide:{x:250,y:230,w:540,h:400,z:14,s:0.94}, swarm:{x:530,y:220,w:510,h:400,z:15,s:0.94}
    }},
    { focus: 'ai', dock: 'dk-ai', atIdx: 3, rects: {
      ai:{x:495,y:16,w:570,h:430,z:31,s:1.01}, ide:{x:12,y:26,w:550,h:422,z:29,s:1.00},
      ps:{x:24,y:420,w:610,h:465,z:22,s:0.97}, swarm:{x:552,y:456,w:514,h:425,z:26,s:0.99},
      cms:{x:180,y:455,w:520,h:420,z:15,s:0.95}, gem:{x:520,y:210,w:510,h:410,z:14,s:0.94}
    }},
    { focus: 'cms', dock: 'dk-web', atIdx: 5, rects: {
      cms:{x:14,y:14,w:555,h:452,z:32,s:1.01}, gem:{x:544,y:18,w:522,h:444,z:30,s:1.00},
      ps:{x:16,y:442,w:620,h:446,z:25,s:0.98}, swarm:{x:556,y:466,w:510,h:418,z:27,s:0.99},
      ai:{x:260,y:180,w:510,h:390,z:14,s:0.94}, ide:{x:40,y:250,w:530,h:395,z:16,s:0.95}
    }},
    { focus: 'swarm', dock: 'dk-ag', atIdx: 4, rects: {
      ps:{x:10,y:18,w:635,h:466,z:29,s:1.00}, swarm:{x:545,y:14,w:522,h:432,z:32,s:1.01},
      ide:{x:14,y:468,w:552,h:418,z:28,s:1.00}, ai:{x:548,y:454,w:518,h:428,z:26,s:0.98},
      cms:{x:210,y:440,w:520,h:420,z:15,s:0.95}, gem:{x:490,y:220,w:510,h:410,z:14,s:0.94}
    }},
    { focus: 'ps', dock: 'dk-ps', atIdx: 0, rects: {
      ps:{x:215,y:20,w:650,h:472,z:34,s:1.02}, cms:{x:10,y:448,w:532,h:438,z:26,s:0.98},
      gem:{x:548,y:450,w:520,h:436,z:27,s:0.98}, ide:{x:10,y:14,w:490,h:400,z:19,s:0.95},
      ai:{x:560,y:16,w:506,h:392,z:20,s:0.95}, swarm:{x:280,y:470,w:500,h:405,z:18,s:0.95}
    }}
  ];
  const WIN_IDS = ['ps', 'ai', 'cms', 'gem', 'ide', 'swarm'];

  function getLayoutState(f) {
    const STEP_F = 115; // Switch focus app every ~1.9s
    const idx = Math.floor(f / STEP_F);
    const localF = f - idx * STEP_F;
    const L0 = TOP_LAYOUTS[idx % TOP_LAYOUTS.length];
    const prevL = TOP_LAYOUTS[(idx === 0 ? 0 : idx - 1) % TOP_LAYOUTS.length];
    const s = minJerk(Math.min(1, localF / 18));
    const curRects = {};
    for (const k of WIN_IDS) {
      const a = prevL.rects[k], b = L0.rects[k];
      curRects[k] = {
        x: lerp(a.x, b.x, s), y: lerp(a.y, b.y, s),
        w: lerp(a.w, b.w, s), h: lerp(a.h, b.h, s),
        z: b.z, sc: lerp(a.s, b.s, s)
      };
    }
    return { focus: L0.focus, dock: L0.dock, atIdx: L0.atIdx, rects: curRects, showAltTab: idx > 0 && localF < 14 };
  }

  // ==================== 6. DRAW PHOTOSHOP, ILLUSTRATOR, GRAPH & SCOPES ====================
  const psCtx = document.getElementById('ps-cvs').getContext('2d');
  const aiCtx = document.getElementById('ai-cvs').getContext('2d');
  const grCtx = document.getElementById('ae-graph-cvs').getContext('2d');
  const sc1 = document.getElementById('sc-1').getContext('2d');
  const sc2 = document.getElementById('sc-2').getContext('2d');
  const sc3 = document.getElementById('sc-3').getContext('2d');
  const tlCtx = document.getElementById('tl-canvas').getContext('2d');
  const curCtx = document.getElementById('cursor-canvas').getContext('2d');

  function drawPhotoshop(f, t) {
    const W = 410, H = 365;
    psCtx.clearRect(0, 0, W, H);
    const assetIdx = Math.floor(t / 3.8) % psImgs.length;
    const im = psImgs[assetIdx];
    if (im && im.complete && im.naturalWidth > 0) {
      const ratio = Math.min((W * 0.74) / im.naturalWidth, (H * 0.80) / im.naturalHeight);
      const dw = im.naturalWidth * ratio, dh = im.naturalHeight * ratio;
      const dx = (W - dw) * 0.5, dy = (H - dh) * 0.48;
      psCtx.drawImage(im, dx, dy, dw, dh);
      psCtx.strokeStyle = '#31A8FF'; psCtx.lineWidth = 1.3;
      psCtx.strokeRect(dx - 5, dy - 5, dw + 10, dh + 10);
      psCtx.save();
      psCtx.setLineDash([5, 5]); psCtx.lineDashOffset = -(f * 0.7);
      psCtx.strokeStyle = '#FFF'; psCtx.beginPath();
      psCtx.ellipse(W * 0.5, H * 0.48, dw * 0.43, dh * 0.44, 0, 0, Math.PI * 2); psCtx.stroke();
      psCtx.restore();
    }
    // Curves mini-box
    const cx = W - 98, cy = 10, cw = 88, ch = 88;
    psCtx.fillStyle = 'rgba(28,28,32,0.92)'; psCtx.fillRect(cx, cy, cw, ch);
    psCtx.strokeStyle = '#52525B'; psCtx.strokeRect(cx, cy, cw, ch);
    psCtx.strokeStyle = '#31A8FF'; psCtx.lineWidth = 1.8;
    psCtx.beginPath(); psCtx.moveTo(cx + 6, cy + ch - 6);
    psCtx.bezierCurveTo(cx + 28, cy + ch - 14, cx + 56, cy + 14, cx + cw - 6, cy + 6); psCtx.stroke();
    for (let k = 0; k < 5; k++) document.getElementById(`psl-${k}`).className = k === (assetIdx + 1) % 5 ? 'ps-lyr sel' : 'ps-lyr';
  }

  function drawIllustrator(t) {
    const W = 520, H = 372;
    aiCtx.fillStyle = '#1B1B1B'; aiCtx.fillRect(0, 0, W, H);
    const ax = 48, ay = 26, aw = 424, ah = 318;
    aiCtx.fillStyle = '#111624'; aiCtx.fillRect(ax, ay, aw, ah);
    aiCtx.strokeStyle = '#FF9A00'; aiCtx.lineWidth = 1.2; aiCtx.strokeRect(ax, ay, aw, ah);
    const cx = ax + aw * 0.5, cy = ay + 128, r = 64;
    aiCtx.strokeStyle = '#F59E0B'; aiCtx.lineWidth = 2.4;
    aiCtx.beginPath(); aiCtx.arc(cx, cy, r, 0, Math.PI * 2); aiCtx.stroke();
    for (let k = 0; k < 8; k++) {
      const a = (k / 8) * Math.PI * 2 + 0.2;
      const nx = cx + Math.cos(a) * r, ny = cy + Math.sin(a) * r;
      aiCtx.fillStyle = '#FFF'; aiCtx.fillRect(nx - 3, ny - 3, 6, 6);
    }
    aiCtx.fillStyle = '#FDE68A'; aiCtx.font = '900 16px "Segoe UI"'; aiCtx.textAlign = 'center';
    aiCtx.fillText('HẰNG THU PHARMA', cx, cy + 5);
    aiCtx.fillStyle = '#93C5FD'; aiCtx.font = 'bold 11px "Segoe UI"';
    aiCtx.fillText('VECTOR TYPOGRAPHY • 5 SẢN PHẨM TUỔI 25', cx, ay + 258);
    aiCtx.textAlign = 'left';
  }

  function drawAeGraph(t) {
    const W = 288, H = 118;
    grCtx.fillStyle = '#121212'; grCtx.fillRect(0, 0, W, H);
    grCtx.strokeStyle = '#242424'; grCtx.lineWidth = 1;
    for (let y = 24; y < H; y += 24) { grCtx.beginPath(); grCtx.moveTo(0, y); grCtx.lineTo(W, y); grCtx.stroke(); }
    grCtx.strokeStyle = '#FACC15'; grCtx.lineWidth = 2;
    grCtx.beginPath(); grCtx.moveTo(18, H - 18);
    grCtx.bezierCurveTo(92, H - 18, 96, 18, 144, 18);
    grCtx.bezierCurveTo(192, 18, 196, H - 18, W - 18, H - 18);
    grCtx.stroke();
    for (const [kx, ky] of [[18,H-18],[144,18],[W-18,H-18]]) {
      grCtx.fillStyle = '#FACC15'; grCtx.fillRect(kx - 3, ky - 3, 6, 6);
    }
  }

  function drawScopes(t, gradeMix, hasV1) {
    sc1.fillStyle = '#080808'; sc1.fillRect(0, 0, 68, 135);
    sc2.fillStyle = '#080808'; sc2.fillRect(0, 0, 68, 135);
    sc3.fillStyle = '#080808'; sc3.fillRect(0, 0, 68, 135);
    if (!hasV1) return; // Scopes stay completely dark when timeline is empty!

    const span = 14 + gradeMix * 24; // Scopes visibly expand when Lumetri LUT is applied!
    sc1.strokeStyle = 'rgba(74,222,128,0.75)'; sc1.beginPath();
    for (let x = 0; x < 68; x += 2) {
      const y = 72 + Math.sin(x * 0.22 + t * 2) * span * 0.7;
      if (x === 0) sc1.moveTo(x, y); else sc1.lineTo(x, y);
    }
    sc1.stroke();

    const cols = ['rgba(248,113,113,0.78)', 'rgba(74,222,128,0.78)', 'rgba(96,165,250,0.78)'];
    for (let c = 0; c < 3; c++) {
      sc2.fillStyle = cols[c];
      for (let i = 0; i < 9; i++) {
        const bh = (18 + gradeMix * 36) + Math.abs(Math.sin(t * 2.2 + c + i * 0.6)) * 28;
        sc2.fillRect(c * 22 + 3 + i * 2, 120 - bh, 1.5, bh);
      }
    }

    sc3.strokeStyle = '#27272A'; sc3.beginPath(); sc3.arc(34, 74, 26, 0, Math.PI * 2); sc3.stroke();
    sc3.strokeStyle = 'rgba(251,191,36,0.7)'; sc3.beginPath(); sc3.moveTo(34, 74); sc3.lineTo(20, 50); sc3.stroke();
    const satRad = 4 + gradeMix * 14;
    sc3.fillStyle = 'rgba(253,186,116,0.65)';
    for (let k = 0; k < 12; k++) {
      const a = -2.1 + (k - 6) * 0.05, r = (k / 12) * satRad;
      sc3.fillRect(34 + Math.cos(a) * r, 74 + Math.sin(a) * r, 2, 2);
    }
  }

  // ==================== 7. DRAW BUILD-FROM-ZERO TIMELINE ====================
  function drawTimeline(t, phSec, aeMode) {
    const W = 1080, H = 398;
    tlCtx.fillStyle = '#181818'; tlCtx.fillRect(0, 0, W, H);

    // Ruler
    tlCtx.fillStyle = '#212121'; tlCtx.fillRect(0, 0, W, 24);
    tlCtx.font = '9.5px Consolas, monospace'; tlCtx.fillStyle = '#9CA3AF';
    for (let s = 0; s <= 21; s += 3) {
      const sx = secToX(s);
      tlCtx.strokeStyle = '#52525B';
      tlCtx.beginPath(); tlCtx.moveTo(sx, 11); tlCtx.lineTo(sx, 24); tlCtx.stroke();
      tlCtx.fillText(`00:00:${String(s).padStart(2, '0')}:00`, sx - 24, 10);
    }

    const trRows = [
      { lbl: 'V4 Color LUT', y: 27,  h: 34, v: true },
      { lbl: 'V3 Captions',  y: 64,  h: 34, v: true },
      { lbl: 'V2 [Ae Stage]',y: 101, h: 44, v: true },
      { lbl: 'V1 Chị Hằng',  y: 148, h: 58, v: true },
      { lbl: 'A1 Voiceover', y: 212, h: 56, v: false },
      { lbl: 'A2 BGM Duck',  y: 271, h: 42, v: false },
      { lbl: 'A3 Micro-SFX', y: 316, h: 42, v: false }
    ];
    for (const tr of trRows) {
      tlCtx.fillStyle = '#1E1E20'; tlCtx.fillRect(HDR_W, tr.y, W - HDR_W, tr.h);
      tlCtx.fillStyle = '#252528'; tlCtx.fillRect(0, tr.y, HDR_W - 2, tr.h);
      tlCtx.fillStyle = tr.v ? (aeMode ? '#581C87' : '#2B579A') : '#1E6B52';
      tlCtx.fillRect(4, tr.y + 5, 22, tr.h - 10);
      tlCtx.fillStyle = '#E4E4E7'; tlCtx.font = 'bold 9px "Segoe UI"';
      tlCtx.fillText(tr.lbl, 31, tr.y + tr.h * 0.58);
    }

    let placedCount = 0;

    // 1. Track V1 + A1 (Appears ONLY at t >= 0.65s!)
    if (t >= v1State.tDrop) {
      placedCount += 2;
      const v1X = secToX(0), v1W = secToX(21.0) - v1X;
      tlCtx.fillStyle = '#3B669C'; tlCtx.fillRect(v1X, 150, v1W, 54);
      const cw = v1W / 21;
      for (let i = 0; i < 21; i++) {
        const im = stripImgs[i];
        if (im && im.complete && im.naturalWidth > 0) tlCtx.drawImage(im, v1X + i * cw, 164, cw + 0.8, 40);
      }
      tlCtx.fillStyle = 'rgba(22, 42, 74, 0.90)'; tlCtx.fillRect(v1X, 150, v1W, 14);
      tlCtx.fillStyle = '#E0F2FE'; tlCtx.font = 'bold 8.5px Consolas';
      tlCtx.fillText('CamA_ChiHang_RawLog.MP4', v1X + 5, 160);

      // Razor cuts appear ONLY at the exact millisecond Razor Cursor clicks them!
      for (const ct of v1State.cuts) {
        if (t >= ct.tCut) {
          placedCount++;
          const cx = secToX(ct.sec);
          tlCtx.strokeStyle = '#09090B'; tlCtx.lineWidth = 3;
          tlCtx.beginPath(); tlCtx.moveTo(cx, 150); tlCtx.lineTo(cx, 266); tlCtx.stroke();
          // Brief red razor flash on cut
          if (t - ct.tCut < 0.22) {
            tlCtx.strokeStyle = '#EF4444'; tlCtx.lineWidth = 2;
            tlCtx.beginPath(); tlCtx.moveTo(cx, 145); tlCtx.lineTo(cx, 270); tlCtx.stroke();
          }
          tlCtx.fillStyle = '#E0F2FE';
          tlCtx.fillText(ct.lbl, cx + 5, 160);
        }
      }
      tlCtx.strokeStyle = '#93C5FD'; tlCtx.lineWidth = 1.2; tlCtx.strokeRect(v1X, 150, v1W, 54);

      // A1 Waveform
      tlCtx.fillStyle = '#1B5E4A'; tlCtx.fillRect(v1X, 214, v1W, 52);
      tlCtx.strokeStyle = '#4ADE80'; tlCtx.strokeRect(v1X, 214, v1W, 52);
      const wf = (window.AUDIO_DATA_V3 && window.AUDIO_DATA_V3.waveform) ? window.AUDIO_DATA_V3.waveform : [];
      const bStep = v1W / Math.max(1, wf.length);
      for (let b = 0; b < wf.length; b++) {
        const bh = Math.max(2, wf[b] * 40);
        const activeBar = (b / wf.length) * 21.0 <= phSec && t >= PLAY_START_T;
        tlCtx.fillStyle = activeBar ? '#A7F3D0' : '#6EE7B7';
        tlCtx.fillRect(v1X + b * bStep, 242 - bh * 0.5, Math.max(1.4, bStep - 1), bh);
      }
      tlCtx.fillStyle = 'rgba(10,30,24,0.84)'; tlCtx.fillRect(v1X + 4, 215, 255, 12);
      tlCtx.fillStyle = '#D1FAE5'; tlCtx.font = 'bold 8.3px Consolas';
      tlCtx.fillText('VO_ChiHang_Real_48kHz.wav [-14.2 LUFS]', v1X + 7, 224);
    }

    // 2. Track V2 [Ae Stage Cards] — Appear one by one at tDrop & stretch live during [tTr0..tTr1]!
    for (const sc of v2StageClips) {
      if (t < sc.tDrop) continue;
      placedCount++;
      const curEnd = clipEndAt(sc, t);
      const x = secToX(sc.s), w = Math.max(8, secToX(curEnd) - x);
      tlCtx.fillStyle = aeMode ? '#7E22CE' : '#2563EB';
      tlCtx.fillRect(x, 103, w, 40);
      tlCtx.strokeStyle = '#93C5FD'; tlCtx.lineWidth = 1.2; tlCtx.strokeRect(x, 103, w, 40);
      if (t >= sc.tTr0 && t <= sc.tTr1 + 0.08) {
        tlCtx.fillStyle = '#FACC15'; tlCtx.fillRect(x + w - 4, 103, 4, 40); // Yellow active trim bracket!
      }
      tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x + 4, 103, Math.max(0, w - 8), 40); tlCtx.clip();
      tlCtx.fillStyle = '#EFF6FF'; tlCtx.font = 'bold 8.6px "Segoe UI"';
      tlCtx.fillText(sc.lbl, x + 6, 126);
      tlCtx.restore();
    }

    // 3. Track V3 Captions — Cascade in 1-by-1!
    for (const cp of v3Captions) {
      if (t < cp.tDrop) continue;
      placedCount++;
      const curEnd = clipEndAt(cp, t);
      const x = secToX(cp.s), w = Math.max(6, secToX(curEnd) - x);
      const isUnderPh = phSec >= cp.s && phSec <= curEnd;
      tlCtx.fillStyle = isUnderPh ? '#C026D3' : '#86198F';
      tlCtx.fillRect(x, 66, w, 30);
      tlCtx.strokeStyle = isUnderPh ? '#F5D0FE' : '#D946EF'; tlCtx.strokeRect(x, 66, w, 30);
      tlCtx.fillStyle = '#FFF'; tlCtx.font = '8px Consolas';
      if (w > 34) tlCtx.fillText(cp.lbl, x + 4, 84);
    }

    // 4. Track V4 Lumetri Color Adjustment Layer (Appears at t >= 7.20s!)
    if (t >= v4LutLayer.tDrop) {
      placedCount++;
      const curEnd = clipEndAt(v4LutLayer, t);
      const x = secToX(0), w = secToX(curEnd) - x;
      tlCtx.fillStyle = '#BE185D'; tlCtx.fillRect(x, 29, w, 30);
      tlCtx.strokeStyle = '#F9A8D4'; tlCtx.strokeRect(x, 29, w, 30);
      tlCtx.fillStyle = '#FDF2F8'; tlCtx.font = 'bold 8.8px "Segoe UI"';
      tlCtx.fillText(v4LutLayer.lbl, x + 7, 47);
    }

    // 5. Track A2 BGM + Live Pulled Ducking Envelope (Appears at t >= 8.15s!)
    if (t >= a2BgmLayer.tDrop) {
      placedCount++;
      const x = secToX(0), w = secToX(21.0) - x;
      tlCtx.fillStyle = '#164E63'; tlCtx.fillRect(x, 273, w, 38);
      tlCtx.strokeStyle = '#38BDF8'; tlCtx.strokeRect(x, 273, w, 38);
      const duckAmt = t < a2BgmLayer.tDuck0 ? 0 : t >= a2BgmLayer.tDuck1 ? 1 : minJerk((t - a2BgmLayer.tDuck0) / 0.40);
      tlCtx.strokeStyle = '#FACC15'; tlCtx.lineWidth = 1.6;
      tlCtx.beginPath();
      for (let i = 0; i <= 60; i++) {
        const dx = lerp(x, x + w, i / 60);
        const dip = Math.sin(i * 0.45) * 0.5 + 0.5;
        const dy = 282 + duckAmt * (6 + dip * 10);
        if (i === 0) tlCtx.moveTo(dx, dy); else tlCtx.lineTo(dx, dy);
      }
      tlCtx.stroke();
      for (const secKf of [4.0, 10.5, 17.2]) {
        const kx = secToX(secKf), ky = 282 + duckAmt * 13;
        tlCtx.fillStyle = '#FACC15'; tlCtx.fillRect(kx - 3, ky - 3, 6, 6);
      }
    }

    // 6. Track A3 Micro-SFX Blocks
    for (const sf of a3SfxClips) {
      if (t < sf.tDrop) continue;
      placedCount++;
      const sx = secToX(sf.s);
      tlCtx.fillStyle = '#0D9488'; tlCtx.fillRect(sx, 319, 36, 34);
      tlCtx.strokeStyle = '#5EEAD4'; tlCtx.strokeRect(sx, 319, 36, 34);
      tlCtx.fillStyle = '#FFF'; tlCtx.font = '7.8px Consolas';
      tlCtx.fillText(sf.lbl, sx + 3, 339);
    }

    document.getElementById('tl-clip-counter').textContent =
      placedCount === 0 ? 'Clips: 0/28 • Empty Sequence'
      : t < PLAY_START_T ? `Assembling: ${placedCount}/28 Clips...`
      : `Sequence Ready • 28/28 Clips • 60fps Playback`;

    // 7. Playhead Line & Cap (Green glow during [SPACE] Play, Blue during Edit/Scrub!)
    const phX = secToX(phSec);
    const isPlaying = t >= PLAY_START_T && t <= PLAY_END_T;
    tlCtx.strokeStyle = isPlaying ? '#34D399' : '#4B9CFF';
    tlCtx.lineWidth = 2;
    tlCtx.beginPath(); tlCtx.moveTo(phX, 8); tlCtx.lineTo(phX, H); tlCtx.stroke();
    tlCtx.fillStyle = isPlaying ? '#10B981' : '#4B9CFF';
    tlCtx.beginPath();
    tlCtx.moveTo(phX - 6, 3); tlCtx.lineTo(phX + 6, 3);
    tlCtx.lineTo(phX + 6, 12); tlCtx.lineTo(phX, 18); tlCtx.lineTo(phX - 6, 12);
    tlCtx.closePath(); tlCtx.fill();
  }

  // ==================== 8. DRAW VECTOR OS CURSORS ====================
  function drawCursor(ctx, x, y, sc, ctype) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(sc, sc);
    ctx.shadowColor = 'rgba(0,0,0,0.6)';
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
    ctx.restore();
  }

  // ==================== 9. MASTER FRAME RENDERER ====================
  const previewImg = document.getElementById('chihang-video-img');
  const maskNoCard = document.getElementById('mask-no-topcard');
  const maskNoSub  = document.getElementById('mask-no-subtitle');
  const emptyBlack = document.getElementById('mon-empty-black');
  const layerStack = document.getElementById('mon-layer-stack');
  const wireframe  = document.getElementById('pr-wireframe');
  const keyHud     = document.getElementById('keystroke-hud');

  const jsxCode = [
    '<span class="cm">// Build Sequence 01 from Empty -> Full 7-Track Master</span>',
    '<span class="kw">const</span> seq = project.<span class="fn">createSequence</span>(<span class="st">"ChiHang_9x16_60fps"</span>);',
    'seq.videoTracks[<span class="nu">0</span>].<span class="fn">insertClip</span>(bin.<span class="fn">find</span>(<span class="st">"CamA_RawLog.MP4"</span>), <span class="nu">0</span>);',
    'seq.<span class="fn">razorSplitAt</span>([<span class="nu">5.0</span>, <span class="nu">11.2</span>, <span class="nu">16.0</span>]);',
    'seq.videoTracks[<span class="nu">1</span>].<span class="fn">linkAeStages</span>([<span class="st">"Hook"</span>, <span class="st">"5Icons"</span>, <span class="st">"Scale"</span>]);',
    'seq.videoTracks[<span class="nu">2</span>].<span class="fn">snapEssentialCaptions</span>(whisperWords);',
    'seq.videoTracks[<span class="nu">3</span>].<span class="fn">applyLumetriLut</span>(<span class="st">"WarmSkin96.cube"</span>);',
    'seq.audioTracks[<span class="nu">1</span>].<span class="fn">keyframeSidechainDuck</span>(<span class="nu">-11.0</span>);',
    'player.<span class="fn">seek</span>(<span class="nu">0.0</span>); player.<span class="fn">pressSpacebarPlay</span>(); <span class="cm">// Smooth 60fps!</span>'
  ];

  const liveActionFeed = [
    { t: 0.0,  app: 'Pr', txt: 'Created Empty Sequence 01 (1080×1920 @ 60fps)', st: '0 Clips' },
    { t: 0.65, app: 'Pr', txt: 'Dropped CamA_ChiHang_RawLog.MP4 -> Track V1 + A1', st: 'RAW S-LOG' },
    { t: 1.25, app: 'Pr', txt: 'Razor Tool [C]: Sliced 4 camera segments on V1', st: '3 CUTS' },
    { t: 3.10, app: 'Ae', txt: 'Linked Stage01_5SanPham_Hook.aep -> Track V2', st: 'CARD ON' },
    { t: 4.35, app: 'Ae', txt: 'Linked Stage02_5NenTang_Icons.aep -> Track V2', st: 'ICONS ON' },
    { t: 5.60, app: 'Pr', txt: 'Snapped 10 Word-Synced Captions -> Track V3', st: 'SUBS ON' },
    { t: 7.20, app: 'Ps', txt: 'Applied Lumetri_WarmSkin96.cube + Color Grade -> V4', st: 'GRADED' },
    { t: 8.15, app: 'Au', txt: 'Placed BGM Sidechain (-11dB) + 8 Micro-SFX -> A2/A3', st: '-14 LUFS' },
    { t: 8.92, app: 'Pr', txt: '[SPACE] Rewind 00:00 & Start Smooth 60fps Playback!', st: 'PLAYING ▶' },
    { t: 14.0, app: 'Ae', txt: 'Dynamic Link Live Inspection • Roto & Bezier OK', st: 'SYNC 100%' },
    { t: 22.0, app: 'Web',txt: 'Chrome Auto-CMS & TikTok Shop Campaign Ready', st: '200 OK' },
    { t: 29.96,app: 'Me', txt: 'Playback Complete -> Queued H.264 NVENC 60fps', st: 'DONE ✓' }
  ];

  const cmsText = '5 sản phẩm cần biết cho phụ nữ sau tuổi 25! Bí quyết chăm sóc từ gốc cùng Chị Hằng — Hằng Thu Pharma';

  window.renderFrame = async function (frameIdx) {
    const f = Math.max(0, Math.min(TOTAL_FRAMES - 1, frameIdx));
    const t = f / FPS;
    const phSec = getPlayheadSec(t);
    const isPlaying = t >= PLAY_START_T && t <= PLAY_END_T;
    const aeMode = (t >= 3.0 && t < 5.5) || (t >= 13.8 && t < 17.6);

    // 1. Top Desktop Multi-App Jumping
    const ls = getLayoutState(f);
    for (const k of WIN_IDS) {
      const el = document.getElementById(`win-${k}`);
      const r = ls.rects[k];
      el.style.left = `${r.x.toFixed(1)}px`; el.style.top = `${r.y.toFixed(1)}px`;
      el.style.width = `${r.w.toFixed(1)}px`; el.style.height = `${r.h.toFixed(1)}px`;
      el.style.zIndex = String(r.z); el.style.transform = `scale(${r.sc.toFixed(3)})`;
      el.className = k === ls.focus ? 'app-win focused' : 'app-win';
    }
    for (const dk of ['dk-ps', 'dk-pr', 'dk-ae', 'dk-ai', 'dk-web', 'dk-ag']) {
      const on = (dk === ls.dock) || (dk === 'dk-ae' && aeMode) || (dk === 'dk-pr' && !aeMode);
      document.getElementById(dk).className = on ? 'dock-pill active' : 'dock-pill';
    }
    const hud = document.getElementById('alt-tab-hud');
    if (ls.showAltTab) {
      hud.style.display = 'flex';
      for (let a = 0; a < 6; a++) document.getElementById(`at-${a}`).className = a === ls.atIdx ? 'at-item sel' : 'at-item';
    } else {
      hud.style.display = 'none';
    }

    drawPhotoshop(f, t);
    drawIllustrator(t);
    drawAeGraph(t);

    const typed = Math.floor((t * 22) % (cmsText.length + 18));
    document.getElementById('cms-type').textContent = cmsText.slice(0, Math.min(cmsText.length, typed)) + (f % 24 < 12 ? '▋' : '');
    const activeCodeStep = Math.min(jsxCode.length - 1, Math.floor((t / 9.0) * jsxCode.length));
    document.getElementById('ide-lines').innerHTML = jsxCode.map((h, i) =>
      `<div class="cl ${i <= activeCodeStep ? 'add' : ''}${i === activeCodeStep ? ' cur' : ''}"><span style="color:#475569;margin-right:6px;">${i + 1}</span>${h}</div>`
    ).join('');

    const visibleLogs = liveActionFeed.filter(x => t >= x.t).slice(-7);
    document.getElementById('swarm-rows').innerHTML = visibleLogs.map((it, idx) =>
      `<div class="srow${idx === visibleLogs.length - 1 ? ' hot' : ''}"><span><b style="color:#67E8F9">[${it.app}]</b> ${it.txt}</span><span style="color:#34D399;font-weight:700;">${it.st}</span></div>`
    ).join('');

    // 2. TRUE TIMELINE EVALUATION -> LIVE VIEW MONITOR ("Gắn gì hiện cái đó"!)
    const hasV1 = t >= v1State.tDrop;
    emptyBlack.style.display = hasV1 ? 'none' : 'flex';

    // Check if ANY placed V2 Stage Card covers current phSec!
    let hasTopCardAtPh = false;
    for (const sc of v2StageClips) {
      if (t >= sc.tDrop && phSec >= sc.s && phSec <= clipEndAt(sc, t)) {
        hasTopCardAtPh = true; break;
      }
    }
    // Check if ANY placed V3 Caption covers current phSec!
    let hasSubAtPh = false;
    for (const cp of v3Captions) {
      if (t >= cp.tDrop && phSec >= cp.s && phSec <= clipEndAt(cp, t)) {
        hasSubAtPh = true; break;
      }
    }

    maskNoCard.style.display = hasTopCardAtPh ? 'none' : 'block';
    maskNoSub.style.display  = hasSubAtPh ? 'none' : 'block';

    // Live S-Log3 -> Lumetri Studio Color Filter!
    const gradeMix = getColorGradeMix(t, phSec);
    const sat = lerp(0.46, 1.02, gradeMix);
    const con = lerp(0.78, 1.02, gradeMix);
    const bri = lerp(0.95, 1.00, gradeMix);
    const scaleState = getSliderState(0, t);
    const scFactor = 1.0 + (parseFloat(scaleState.txt) - 100.0) * 0.004;
    layerStack.style.filter = `saturate(${sat.toFixed(3)}) contrast(${con.toFixed(3)}) brightness(${bri.toFixed(3)})`;
    layerStack.style.transform = `scale(${scFactor.toFixed(3)})`;

    // Show Direct-Manipulation Wireframe Box ONLY right when dropping/adjusting Top Card or Caption!
    if (t >= 3.10 && t <= 3.58) {
      wireframe.style.display = 'block';
      wireframe.style.left = '8px'; wireframe.style.top = '8px';
      wireframe.style.width = '248px'; wireframe.style.height = '152px';
    } else if (t >= 5.72 && t <= 6.25) {
      wireframe.style.display = 'block';
      wireframe.style.left = '46px'; wireframe.style.top = '268px';
      wireframe.style.width = '172px'; wireframe.style.height = '54px';
    } else {
      wireframe.style.display = 'none';
    }

    // Update Monitor Badges, Play Button & Keystroke HUD!
    const appBadge = document.getElementById('nle-app-badge');
    appBadge.className = aeMode ? 'cc-badge cc-ae' : 'cc-badge cc-pr';
    appBadge.textContent = aeMode ? 'Ae' : 'Pr';
    document.getElementById('nle-app-name').textContent = aeMode ? 'Adobe After Effects 2026' : 'Adobe Premiere Pro 2026';

    document.getElementById('mon-title').textContent =
      !hasV1 ? 'Program: Sequence 01 (Empty)'
      : aeMode ? 'Composition: ChiHang_Master_9x16 [Dynamic Link]'
      : 'Program: Sequence 01 • Chị Hằng (Video Thực)';

    const stLbl = document.getElementById('mon-state-lbl');
    const playBtn = document.getElementById('btn-play-toggle');
    if (isPlaying) {
      stLbl.textContent = '▶ PLAYING 60.0 FPS (REALTIME)';
      stLbl.style.color = '#34D399';
      playBtn.textContent = '⏸';
      playBtn.className = 'playing';
    } else if (t > PLAY_END_T) {
      stLbl.textContent = '✓ PLAYBACK COMPLETE • READY';
      stLbl.style.color = '#38BDF8';
      playBtn.textContent = '▶';
      playBtn.className = '';
    } else {
      stLbl.textContent = '⏸ SCRUBBING / ASSEMBLING';
      stLbl.style.color = '#F59E0B';
      playBtn.textContent = '▶';
      playBtn.className = '';
    }

    document.getElementById('mon-mode-pill').textContent =
      !hasV1 ? 'NO CLIPS'
      : t > PLAY_END_T ? '✓ QUEUED IN MEDIA ENCODER'
      : isPlaying ? (aeMode ? 'Ae • LIVE PLAYBACK 60FPS' : 'Pr • LIVE PLAYBACK 60FPS')
      : gradeMix < 0.5 ? 'RAW S-LOG3 • EDITING' : 'LUMETRI GRADED • READY';

    const expBtn = document.getElementById('export-btn');
    if (t >= 30.14) { expBtn.textContent = '✓ Queued 60fps'; expBtn.className = 'adobe-export-btn done'; }
    else { expBtn.textContent = 'Queue in Me 60fps'; expBtn.className = 'adobe-export-btn'; }

    // KeyCastr Shortcut Toast
    let keyMsg = '', keyPlayCls = false;
    if (t >= 0.95 && t <= 1.78) keyMsg = '🪒 [ C ] Razor Split';
    else if (t >= 3.05 && t <= 3.60) keyMsg = '⇄ Link Ae Motion Stage';
    else if (t >= 5.58 && t <= 6.50) keyMsg = 'CC Snap Auto-Captions';
    else if (t >= 7.18 && t <= 8.15) keyMsg = '🎨 Apply Lumetri Skin 96%';
    else if (t >= 8.65 && t < 8.90)  keyMsg = '⏮ [ Home ] 00:00:00:00';
    else if (t >= 8.90 && t <= 10.35){ keyMsg = '␣ SPACE — PLAY FINAL 60FPS ▶'; keyPlayCls = true; }
    else if (t >= 29.95 && t <= 30.35){ keyMsg = '␣ SPACE — STOP & EXPORT ✓'; keyPlayCls = true; }

    if (keyMsg) {
      keyHud.style.display = 'block';
      keyHud.textContent = keyMsg;
      keyHud.className = keyPlayCls ? 'play-on' : '';
    } else {
      keyHud.style.display = 'none';
    }

    // Toolbar active tool highlight (Razor [C] active during 0.95..1.80s!)
    const isRazor = t >= 0.95 && t <= 1.82;
    document.getElementById('tlb-0').className = isRazor ? 'tl-b' : 'tl-b on';
    document.getElementById('tlb-1').className = isRazor ? 'tl-b on' : 'tl-b';

    // Update Sliders & Badges (Motionless unless being dragged!)
    for (let s = 0; s < 5; s++) {
      const st = getSliderState(s, t);
      document.getElementById(`sl${s}f`).style.width = `${(st.u * 100).toFixed(1)}%`;
      document.getElementById(`sl${s}t`).style.left = `${(st.u * 100).toFixed(1)}%`;
      document.getElementById(`sl${s}v`).textContent = st.txt;
    }
    document.getElementById('lut-badge').textContent = gradeMix > 0.1 ? 'WarmSkin96 ON' : 'RAW S-LOG3';
    document.getElementById('lut-badge').style.color = gradeMix > 0.1 ? '#34D399' : '#71717A';
    document.getElementById('cw-status').textContent = gradeMix > 0.1 ? 'Active' : 'Bypass';
    document.getElementById('cw-status').style.color = gradeMix > 0.1 ? '#38BDF8' : '#71717A';
    document.getElementById('cwd1').style.transform = `translate(calc(-50% + ${(gradeMix * 6).toFixed(1)}px), calc(-50% - ${(gradeMix * 5).toFixed(1)}px))`;

    // Update Timecode, Scopes & Audio Master Meters
    const secI = Math.floor(phSec), frmI = Math.floor((phSec - secI) * 60);
    document.getElementById('mon-tc').textContent = `00:00:${String(secI).padStart(2, '0')}:${String(frmI).padStart(2, '0')}`;

    const ampL = window.AUDIO_DATA_V3 ? window.AUDIO_DATA_V3.env_l[f] : 0.0;
    const ampR = window.AUDIO_DATA_V3 ? window.AUDIO_DATA_V3.env_r[f] : 0.0;
    document.getElementById('vu-l').style.height = `${Math.min(96, ampL * 95).toFixed(1)}%`;
    document.getElementById('vu-r').style.height = `${Math.min(96, ampR * 95).toFixed(1)}%`;
    document.getElementById('vu-db').textContent = ampL < 0.015 ? '-∞ dB' : `${(-24 + Math.max(ampL, ampR) * 14).toFixed(1)}dB`;

    drawScopes(t, gradeMix, hasV1);

    // Load Exact Video Frame corresponding to phSec!
    if (hasV1) {
      const vidFrame = Math.max(1, Math.min(1258, Math.round(phSec * 60) + 1));
      const targetSrc = `assets/preview_frames/f_${String(vidFrame).padStart(4, '0')}.jpg`;
      if (!previewImg.src.endsWith(targetSrc)) {
        await new Promise((resolve) => {
          previewImg.onload = resolve;
          previewImg.onerror = resolve;
          previewImg.src = targetSrc;
        });
      }
    }

    // 3. Draw Timeline & All Task-Locked Cursors!
    drawTimeline(t, phSec, aeMode);

    curCtx.clearRect(0, 0, 1080, 1920);
    for (const ag of agents) {
      if (ag.isPlayheadAgent) {
        // Playhead Scrubber Cursor: grabs Playhead cap during 0.70..8.86s, clicks Play (520,1483) at 8.92s, then parks calmly!
        let px, py, psc = 1.0, ptype = 'hand';
        if (t < 0.70) {
          const u = minJerk(t / 0.70);
          px = lerp(420, secToX(0.45), u); py = lerp(1420, 1534, u);
        } else if (t <= 8.86) {
          px = secToX(phSec); py = 1534; ptype = 'ew-resize';
        } else if (t <= 8.95) {
          const u = minJerk((t - 8.86) / 0.09);
          px = lerp(secToX(0), 520, u); py = lerp(1534, 1483, u);
          if (t >= 8.91) psc = 0.82;
        } else if (t <= 9.60) {
          const u = minJerk((t - 8.95) / 0.65);
          px = lerp(520, 752, u); py = lerp(1483, 1485, u); // Park neatly off monitor during smooth playback!
          if (t < 9.08) {
            curCtx.strokeStyle = 'rgba(52, 211, 153, 0.85)'; curCtx.lineWidth = 2;
            curCtx.beginPath(); curCtx.arc(520, 1483, (t - 8.91) * 110, 0, Math.PI * 2); curCtx.stroke();
          }
        } else {
          continue; // Hidden cleanly during smooth playback so 0% idle cursor clutter!
        }
        drawCursor(curCtx, px, py, psc, ptype);
        continue;
      }

      // Find active task for this agent (only draw cursor when actively executing or within 0.15s of a task!)
      let task = null;
      for (let k = 0; k < ag.tasks.length; k++) {
        const tk = ag.tasks[k];
        if (t >= tk.t0 && t <= tk.tEnd + 0.12) { task = tk; break; }
      }
      if (!task) continue;

      let cx, cy, sc = 1.0, ct = task.ctype;
      if (t < task.tMove) {
        const u = minJerk((t - task.t0) / Math.max(0.01, task.tMove - task.t0));
        cx = lerp(task.x0, task.x1, u);
        cy = lerp(task.y0, task.y1, u);
      } else if (t <= task.tEnd) {
        const u = minJerk((t - task.tMove) / Math.max(0.01, task.tEnd - task.tMove));
        cx = lerp(task.x1, task.x2, u);
        cy = lerp(task.y1, task.y2, u);
        if (t - task.tMove < 0.09) sc = 0.85;

        // Draw floating ghost clip ONLY while physically dragging from source to Timeline drop!
        if (task.ghostKey && ghostImgs[task.ghostKey] && ghostImgs[task.ghostKey].complete) {
          curCtx.save();
          curCtx.globalAlpha = 0.86;
          curCtx.drawImage(ghostImgs[task.ghostKey], cx + 8, cy + 8, 68, 42);
          curCtx.strokeStyle = '#4B9CFF'; curCtx.lineWidth = 1.5;
          curCtx.strokeRect(cx + 8, cy + 8, 68, 42);
          curCtx.restore();
        }
      } else {
        cx = task.x2; cy = task.y2;
        if (t - task.tEnd < 0.10) {
          curCtx.strokeStyle = 'rgba(96, 165, 250, 0.7)'; curCtx.lineWidth = 1.5;
          curCtx.beginPath(); curCtx.arc(cx, cy, 4 + (t - task.tEnd) * 90, 0, Math.PI * 2); curCtx.stroke();
        }
      }
      drawCursor(curCtx, cx, cy, sc, ct);
    }
  };
})();
