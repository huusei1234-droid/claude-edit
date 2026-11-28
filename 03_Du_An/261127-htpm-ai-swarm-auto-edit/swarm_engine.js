// Deterministic 60fps Multi-Agent Swarm + Live NLE Timeline Engine
(function () {
  const FPS = 60;
  const TOTAL_FRAMES = 1281; // 21.35s @ 60fps
  const TOTAL_SEC = TOTAL_FRAMES / FPS;

  // Seeded PRNG (Mulberry32) for 100% deterministic trajectories
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Minimum-jerk human/AI easing: 10t^3 - 15t^4 + 6t^5
  function minJerk(u) {
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    return u * u * u * (10 + u * (-15 + 6 * u));
  }

  // Preload Timeline Filmstrip & Drag Thumbnails
  const stripImgs = [];
  for (let i = 0; i < 21; i++) {
    const im = new Image();
    im.src = `assets/thumbs/strip_${String(i).padStart(2, '0')}.jpg`;
    stripImgs.push(im);
  }
  const dragThumbPaths = [
    'assets/thumbs/bin_02_laptop_w.jpg',
    'assets/thumbs/bin_05_gelpk.jpg',
    'assets/thumbs/bin_06_whiteskin.jpg',
    'assets/thumbs/bin_08_nlh_real.jpg',
    'assets/thumbs/poster_01.jpg'
  ];
  const dragImgs = dragThumbPaths.map(p => { const im = new Image(); im.src = p; return im; });

  // ==================== 1. CODE IDE CONTENT ====================
  const codeLinesData = [
    { ln: 101, cls: '', html: '<span class="cm"># Auto-Pipeline: Chị Hằng Real Camera -> CapCut 60fps</span>' },
    { ln: 102, cls: '', html: '<span class="kw">def</span> <span class="fn">sync_chihang_master</span>(clips, vo_wav, lut_cube):' },
    { ln: 103, cls: 'code-add', html: '    segments = <span class="fn">whisper_clean_repeats</span>(vo_wav, rms=<span class="nu">0.012</span>)' },
    { ln: 104, cls: 'code-add', html: '    <span class="kw">assert</span> segments.repeat_rate == <span class="nu">0.0</span>, <span class="st">"0% lặp lời"</span>' },
    { ln: 105, cls: '', html: '    timeline = CapCutTimeline(w=<span class="nu">1080</span>, h=<span class="nu">1920</span>, fps=<span class="nu">60</span>)' },
    { ln: 106, cls: '', html: '    <span class="kw">for</span> idx, shot <span class="kw">in</span> <span class="fn">enumerate</span>(clips):' },
    { ln: 107, cls: 'code-del', html: '        shot.scale = 1.00  # static frame' },
    { ln: 108, cls: 'code-add', html: '        shot.<span class="fn">keyframe_scale</span>(<span class="nu">1.00</span>, <span class="nu">1.05</span>, ease=<span class="st">"cubic_out"</span>)' },
    { ln: 109, cls: 'code-add', html: '        shot.<span class="fn">apply_lut</span>(<span class="st">"Warm_Skin_96.cube"</span>, mix=<span class="nu">0.94</span>)' },
    { ln: 110, cls: '', html: '        timeline.<span class="fn">insert_v1</span>(shot, j_cut_ms=<span class="nu">110</span>)' },
    { ln: 111, cls: 'code-add', html: '    timeline.<span class="fn">place_product_cutout</span>(<span class="st">"SP_DIEU_KINH_HT.png"</span>)' },
    { ln: 112, cls: '', html: '    <span class="fn">verify_tiktok_safe_zone</span>(timeline, right_max=<span class="nu">884</span>)' },
    { ln: 113, cls: 'code-add', html: '    audio = <span class="fn">mix_sidechain_lufs</span>(vo_wav, target=<span class="nu">-14.0</span>)' },
    { ln: 114, cls: '', html: '    <span class="kw">return</span> timeline.<span class="fn">export_nvenc</span>(cq=<span class="nu">17</span>, preset=<span class="st">"p5"</span>)' },
    { ln: 115, cls: '', html: '' },
    { ln: 116, cls: 'code-add', html: '<span class="cm"># CDP Browser Swarm: Auto-Publish Fanpage + TikTok Shop</span>' },
    { ln: 117, cls: 'code-add', html: '<span class="kw">async def</span> <span class="fn">dispatch_web_agents</span>(port=<span class="nu">9333</span>, workers=<span class="nu">16</span>):' },
    { ln: 118, cls: 'code-add', html: '    await <span class="fn">gather</span>(*[ag.<span class="fn">sync_sku</span>() <span class="kw">for</span> ag <span class="kw">in</span> swarm])' },
    { ln: 119, cls: '', html: '    print(<span class="st">"[PASS] 68 Agents synchronized in 14.2ms"</span>)' },
  ];

  // ==================== 2. SWARM TOOL LOG STREAM ====================
  const allToolLogs = [
    { ok: true, txt: 'Read 16 files in 06. Video Quay Gốc (C1275, C4134)', diff: '' },
    { ok: true, txt: 'Ran faster-whisper --clean-repeats (0% thoại lặp)', diff: '18.0s' },
    { ok: true, txt: 'Edited build_v3_real_chihang_videos.py', diff: '+48 -4' },
    { ok: true, txt: 'CDP :9333 -> cms.hangthupharma.vn/sku-dk01', diff: '200 OK' },
    { ok: true, txt: 'Applied 3D LUT Warm_Studio_Skin.cube (Skin 96%)', diff: '+12ms' },
    { ok: true, txt: 'Edited draft_content.json (7 tracks, 42 keyframes)', diff: '+186 -9' },
    { ok: true, txt: 'Gemini Pro u/0 -> u/2 asset B-Roll check', diff: 'READY' },
    { ok: true, txt: 'Checked TikTok/Reels Safe-Zone 9:16 (X<=884px)', diff: 'PASS' },
    { ok: true, txt: 'Synced 220-bar Audio Waveform & Ducking -10.4dB', diff: '-14 LUFS' },
    { ok: true, txt: 'TikTok Shop Auto-Uploader queued Reel HD 60fps', diff: 'SYNCED' },
    { ok: true, txt: 'Placed 14 Micro-SFX ticks (Whoosh / Pop / Glass)', diff: '+14' },
    { ok: true, txt: 'Rendered GPU h264_nvenc frame verification', diff: '60.0fps' },
    { ok: true, txt: 'Updated Zalo OA & Fanpage auto-caption template', diff: '+29 -2' },
    { ok: true, txt: 'Locked SP_DIEU_KINH_HT_CUTOUT.png 100% SKU match', diff: 'VERIFIED' },
  ];

  // ==================== 3. GENERATE 68 REALISTIC SWARM CURSORS ====================
  const NUM_CURSORS = 68;
  const cursors = [];

  // Define realistic interactive target zones across the 1080x1920 screen
  const ZONES = {
    cms:     { x0: 22,  x1: 522, y0: 44,  y1: 482, types: ['arrow', 'hand', 'ibeam'] },
    aiweb:   { x0: 558, x1: 1058,y0: 44,  y1: 482, types: ['arrow', 'hand', 'ibeam'] },
    ide:     { x0: 22,  x1: 540, y0: 510, y1: 924, types: ['ibeam', 'arrow', 'hand'] },
    swarm:   { x0: 570, x1: 1060,y0: 510, y1: 924, types: ['arrow', 'hand'] },
    nleTop:  { x0: 20,  x1: 1055,y0: 946, y1: 974, types: ['hand', 'arrow'] },
    bin:     { x0: 18,  x1: 262, y0: 1008,y1: 1488,types: ['hand', 'arrow'] },
    monCtrl: { x0: 292, x1: 748, y0: 990, y1: 1495,types: ['arrow', 'hand'], avoidFace: true },
    insp:    { x0: 778, x1: 1062,y0: 992, y1: 1488,types: ['ew-resize', 'hand', 'arrow'] },
    tlTools: { x0: 20,  x1: 680, y0: 1509,y1: 1532,types: ['hand'] },
    tlTracks:{ x0: 84,  x1: 1064,y0: 1545,y1: 1906,types: ['arrow', 'ew-resize', 'hand'] }
  };

  // Badge map pinned strictly to matching Top-Zone window; Bottom NLE uses 100% clean OS cursors!
  const badgeByCursorId = {
    0:  { label: 'Web-01',  color: '#2563EB' },
    2:  { label: 'CMS-Bot', color: '#059669' },
    5:  { label: 'TikTok',  color: '#DB2777' },
    8:  { label: 'SEO-Bot', color: '#0D9488' },
    10: { label: 'Gemini',  color: '#0284C7' },
    12: { label: 'Flow-AI', color: '#7C3AED' },
    15: { label: 'AssetQC', color: '#0891B2' },
    18: { label: 'Claude',  color: '#D97706' },
    20: { label: 'Code-Ag', color: '#4F46E5' },
    23: { label: 'Whisper', color: '#9333EA' },
    25: { label: 'Swarm',   color: '#0EA5E9' }
  };

  function pickPointInZone(zoneKey, rng) {
    const z = ZONES[zoneKey];
    let x = z.x0 + rng() * (z.x1 - z.x0);
    let y = z.y0 + rng() * (z.y1 - z.y0);
    // Keep cursors off Chị Hằng's face center (x: 415..595, y: 1030..1310) so her real video stays 100% clean!
    if (z.avoidFace && x > 405 && x < 610 && y > 1020 && y < 1320) {
      if (rng() < 0.5) {
        x = rng() < 0.5 ? (295 + rng() * 72) : (645 + rng() * 95);
      } else {
        y = 1355 + rng() * 135; // lower caption / transport bar
      }
    }
    const ctype = z.types[Math.floor(rng() * z.types.length)];
    return { x, y, ctype };
  }

  for (let i = 0; i < NUM_CURSORS; i++) {
    const rng = mulberry32(10007 + i * 7919);
    let roleZones;
    let isDragBridge = false;

    if (i < 10) roleZones = ['cms'];
    else if (i < 18) roleZones = ['aiweb'];
    else if (i < 23) roleZones = ['ide'];
    else if (i < 28) roleZones = ['swarm'];
    else if (i < 32) { roleZones = ['aiweb', 'bin', 'tlTracks']; isDragBridge = true; }
    else if (i < 37) roleZones = ['bin', 'tlTracks', 'bin'];
    else if (i < 40) roleZones = ['monCtrl', 'tlTracks', 'insp'];
    else if (i < 48) roleZones = ['insp', 'insp', 'tlTracks'];
    else roleZones = ['tlTracks', 'tlTracks', 'tlTools', 'tlTracks'];

    // Pre-build waypoint schedule across 0..1140 frames
    const waypoints = [];
    let f = -Math.floor(rng() * 35);
    let prev = pickPointInZone(roleZones[0], rng);

    while (f < TOTAL_FRAMES + 90) {
      const zk = roleZones[Math.floor(rng() * roleZones.length)];
      const next = pickPointInZone(zk, rng);
      const moveDur = Math.floor(18 + rng() * 28); // 0.30s .. 0.76s brisk smooth move
      const holdDur = Math.floor(8 + rng() * 20);  // 0.13s .. 0.46s click/drag action
      const arc = (rng() - 0.5) * 48;
      const actionKind = (zk === 'tlTracks' && rng() < 0.24) ? 'marquee'
                       : (isDragBridge && zk === 'tlTracks') ? 'dropClip'
                       : (zk === 'insp' && rng() < 0.65) ? 'dragSlider'
                       : 'click';
      const dragdx = actionKind === 'marquee' ? (35 + rng() * 95) * (rng() < 0.5 ? 1 : -1)
                   : actionKind === 'dragSlider' ? (rng() - 0.5) * 38 : 0;
      const dragdy = actionKind === 'marquee' ? (16 + rng() * 32) : 0;

      waypoints.push({
        fStart: f,
        fMoveEnd: f + moveDur,
        fEnd: f + moveDur + holdDur,
        x0: prev.x, y0: prev.y,
        x1: next.x, y1: next.y,
        arc,
        ctype: next.ctype,
        actionKind,
        dragdx, dragdy,
        thumbIdx: i % dragImgs.length,
        carrying: isDragBridge && zk === 'tlTracks'
      });
      f += moveDur + holdDur;
      prev = { x: next.x + dragdx, y: next.y + dragdy, ctype: next.ctype };
    }

    cursors.push({
      id: i,
      badge: badgeByCursorId[i] || null,
      waypoints
    });
  }

  // ==================== 4. DRAW VECTOR OS CURSORS ====================
  function drawArrowCursor(ctx, x, y, scale, ctype, badge) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);

    ctx.shadowColor = 'rgba(0, 0, 0, 0.55)';
    ctx.shadowBlur = 4;
    ctx.shadowOffsetX = 1;
    ctx.shadowOffsetY = 2;

    if (ctype === 'ew-resize') {
      // Horizontal <-> trim cursor on NLE timeline/sliders
      ctx.beginPath();
      ctx.moveTo(-9, 0); ctx.lineTo(-4, -5); ctx.lineTo(-4, -2);
      ctx.lineTo(4, -2);  ctx.lineTo(4, -5);  ctx.lineTo(9, 0);
      ctx.lineTo(4, 5);   ctx.lineTo(4, 2);   ctx.lineTo(-4, 2);
      ctx.lineTo(-4, 5);  ctx.closePath();
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();
      ctx.lineWidth = 1.3;
      ctx.strokeStyle = '#090C12';
      ctx.stroke();
    } else if (ctype === 'ibeam') {
      // Crisp text I-beam cursor
      ctx.strokeStyle = '#090C12';
      ctx.lineWidth = 3.2;
      ctx.beginPath();
      ctx.moveTo(-4, -7); ctx.lineTo(4, -7);
      ctx.moveTo(0, -7);  ctx.lineTo(0, 7);
      ctx.moveTo(-4, 7);  ctx.lineTo(4, 7);
      ctx.stroke();
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 1.4;
      ctx.stroke();
    } else if (ctype === 'hand') {
      // Clean pointer arrow with subtle cyan tip accent or classic OS arrow
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(0, 16.5);
      ctx.lineTo(4.4, 12.6);
      ctx.lineTo(7.4, 19.2);
      ctx.lineTo(9.9, 18.0);
      ctx.lineTo(6.9, 11.5);
      ctx.lineTo(12.0, 11.5);
      ctx.closePath();
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();
      ctx.lineWidth = 1.35;
      ctx.strokeStyle = '#0B0F17';
      ctx.stroke();
    } else {
      // Classic macOS/Windows crisp white pointer arrow with dark border
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(0, 17.5);
      ctx.lineTo(4.6, 13.4);
      ctx.lineTo(7.8, 20.2);
      ctx.lineTo(10.4, 19.0);
      ctx.lineTo(7.2, 12.2);
      ctx.lineTo(12.5, 12.2);
      ctx.closePath();
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();
      ctx.lineWidth = 1.4;
      ctx.strokeStyle = '#0B0F17';
      ctx.stroke();
    }

    if (badge) {
      ctx.shadowBlur = 2;
      ctx.font = 'bold 8.5px "Segoe UI", sans-serif';
      const tw = ctx.measureText(badge.label).width;
      const bx = 11, by = 13, bw = tw + 8, bh = 13;
      ctx.fillStyle = badge.color;
      ctx.beginPath();
      ctx.roundRect(bx, by, bw, bh, 4);
      ctx.fill();
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(badge.label, bx + 4, by + 9.6);
    }

    ctx.restore();
  }

  // ==================== 5. DRAW 7-TRACK NLE TIMELINE CANVAS ====================
  const tlCanvas = document.getElementById('tl-canvas');
  const tlCtx = tlCanvas.getContext('2d');

  const trackDefs = [
    { name: 'T2 Hook',  y: 26,  h: 34, bg: '#181B24' },
    { name: 'T1 Sub',   y: 64,  h: 32, bg: '#161922' },
    { name: 'V3 FX/LUT',y: 100, h: 38, bg: '#181B24' },
    { name: 'V2 B-Roll',y: 142, h: 46, bg: '#161922' },
    { name: 'V1 Chị Hằng', y: 192, h: 58, bg: '#1A1E29' },
    { name: 'A1 Voice', y: 254, h: 52, bg: '#161922' },
    { name: 'A2 BGM/SFX',y: 310,h: 54, bg: '#181B24' }
  ];

  function drawTimeline(frameIdx, t, activeMarquees) {
    const W = 1080, H = 395;
    const HEADER_W = 78;
    const TL_W = W - HEADER_W - 12; // 990px => 55px per second for 18s!

    tlCtx.fillStyle = '#11131A';
    tlCtx.fillRect(0, 0, W, H);

    // 1. Time Ruler (0..24px)
    tlCtx.fillStyle = '#171A23';
    tlCtx.fillRect(0, 0, W, 24);
    tlCtx.strokeStyle = '#2A2F3F';
    tlCtx.beginPath();
    tlCtx.moveTo(0, 24); tlCtx.lineTo(W, 24);
    tlCtx.stroke();

    tlCtx.font = '10px Consolas, monospace';
    tlCtx.fillStyle = '#94A3B8';
    for (let s = 0; s <= 21; s++) {
      const sx = HEADER_W + (s / TOTAL_SEC) * TL_W;
      tlCtx.strokeStyle = s % 3 === 0 ? '#475569' : '#283042';
      tlCtx.beginPath();
      tlCtx.moveTo(sx, s % 3 === 0 ? 11 : 17);
      tlCtx.lineTo(sx, 24);
      tlCtx.stroke();
      if (s % 3 === 0) {
        tlCtx.fillText(`00:${String(s).padStart(2, '0')}`, sx - 13, 10);
      }
    }

    // 2. Track Rows & Left Headers
    for (const tr of trackDefs) {
      tlCtx.fillStyle = tr.bg;
      tlCtx.fillRect(HEADER_W, tr.y, W - HEADER_W, tr.h);
      tlCtx.fillStyle = '#141720';
      tlCtx.fillRect(0, tr.y, HEADER_W - 2, tr.h);
      tlCtx.fillStyle = '#9CA3AF';
      tlCtx.font = 'bold 9.2px "Segoe UI", sans-serif';
      tlCtx.fillText(tr.name, 6, tr.y + tr.h * 0.58);
    }

    const secToX = (sec) => HEADER_W + (sec / TOTAL_SEC) * TL_W;

    // 3. Track T2: Golden Hook & Section Titles
    const t2Clips = [
      { s: 0.0, e: 4.8, lbl: 'HOOK: 5 SẢN PHẨM CẦN BIẾT SAU TUỔI 25!', c: '#D97706' },
      { s: 5.0, e: 11.2, lbl: 'NHÓM 01 • ĐIỀU HÒA NỘI TIẾT TỐ NỮ', c: '#B45309' },
      { s: 11.4, e: 15.8, lbl: 'CÂN BẰNG CƠ THỂ TỪ GỐC • HẰNG THU', c: '#D97706' },
      { s: 16.0, e: 21.0, lbl: 'TRÀN NĂNG LƯỢNG & TỰ TIN MỖI NGÀY', c: '#059669' }
    ];
    for (const c of t2Clips) {
      const x = secToX(c.s), w = secToX(c.e) - x;
      tlCtx.fillStyle = c.c;
      tlCtx.beginPath(); tlCtx.roundRect(x, 29, w, 28, 4); tlCtx.fill();
      tlCtx.strokeStyle = 'rgba(255,255,255,0.32)'; tlCtx.lineWidth = 1; tlCtx.stroke();
      tlCtx.fillStyle = '#FFFBEB'; tlCtx.font = 'bold 9px "Segoe UI", sans-serif';
      tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x + 4, 29, w - 8, 28); tlCtx.clip();
      tlCtx.fillText(c.lbl, x + 6, 46);
      tlCtx.restore();
    }

    // 4. Track T1: Dynamic Word-Synced Subtitle Blocks (animated trim wobble on active block)
    const subCount = 12;
    for (let i = 0; i < subCount; i++) {
      const s = i * (20.95 / subCount) + 0.06;
      let e = (i + 1) * (20.95 / subCount) - 0.08;
      if (i === Math.floor(t / (20.95 / subCount))) {
        e += Math.sin(t * 9) * 0.05; // live micro-trim by agent
      }
      const x = secToX(s), w = Math.max(12, secToX(e) - x);
      const isCur = t >= s && t <= e + 0.1;
      tlCtx.fillStyle = isCur ? '#EA580C' : '#9A3412';
      tlCtx.beginPath(); tlCtx.roundRect(x, 67, w, 26, 3); tlCtx.fill();
      if (isCur) {
        tlCtx.strokeStyle = '#FDBA74'; tlCtx.lineWidth = 1.5; tlCtx.stroke();
      }
      tlCtx.fillStyle = '#FFEDD5'; tlCtx.font = '8.5px "Segoe UI", sans-serif';
      tlCtx.fillText(`Sub #${String(i + 1).padStart(2, '0')}`, x + 5, 83);
    }

    // 5. Track V3: Purple LUT & Light-Leak Adjustment Clips + Pink Keyframe Diamonds
    const fxClips = [
      { s: 0.0, e: 10.6, lbl: 'LUT Warm_Studio_Skin_96.cube', kfs: [0.8, 3.2, 6.4, 9.2] },
      { s: 10.8, e: 21.0, lbl: 'RVM_Depth_Stage + SafeZone_9x16', kfs: [11.6, 14.2, 17.4, 20.1] }
    ];
    for (const c of fxClips) {
      const x = secToX(c.s), w = secToX(c.e) - x;
      tlCtx.fillStyle = '#5B21B6';
      tlCtx.beginPath(); tlCtx.roundRect(x, 103, w, 32, 4); tlCtx.fill();
      tlCtx.strokeStyle = '#A78BFA'; tlCtx.lineWidth = 1; tlCtx.stroke();
      // Automation curve line
      tlCtx.strokeStyle = 'rgba(244, 114, 182, 0.75)';
      tlCtx.beginPath();
      tlCtx.moveTo(x + 4, 125);
      for (const kf of c.kfs) {
        const kx = secToX(kf);
        const ky = 117 + Math.sin(kf * 2 + t * 2) * 5;
        tlCtx.lineTo(kx, ky);
      }
      tlCtx.lineTo(x + w - 4, 123);
      tlCtx.stroke();
      // Pink Keyframe Diamonds
      for (const kf of c.kfs) {
        const kx = secToX(kf);
        const ky = 117 + Math.sin(kf * 2 + t * 2) * 5;
        tlCtx.save();
        tlCtx.translate(kx, ky);
        tlCtx.rotate(Math.PI / 4);
        tlCtx.fillStyle = '#EC4899';
        tlCtx.fillRect(-3.5, -3.5, 7, 7);
        tlCtx.strokeStyle = '#FFFFFF'; tlCtx.lineWidth = 0.8;
        tlCtx.strokeRect(-3.5, -3.5, 7, 7);
        tlCtx.restore();
      }
      tlCtx.fillStyle = '#EDE9FE'; tlCtx.font = 'bold 8.5px "Segoe UI", sans-serif';
      tlCtx.fillText(c.lbl, x + 6, 115);
    }

    // 6. Track V2: Emerald B-Roll / Product Cutout Overlay Clips + Red Gap Measurement Guides!
    const v2Clips = [
      { s: 0.4, e: 4.5 + Math.sin(t * 3.2) * 0.12, lbl: 'Card_5SanPham_Tuoi25.html' },
      { s: 5.2, e: 10.8, lbl: 'UI_DieuHoa_NoiTiet.html' },
      { s: 11.4, e: 15.6 + Math.cos(t * 2.7) * 0.14, lbl: 'Scale_CanBang_CoThe.html' },
      { s: 16.2, e: 20.8, lbl: 'Split_NangLuong_100pct.mp4' }
    ];
    for (let idx = 0; idx < v2Clips.length; idx++) {
      const c = v2Clips[idx];
      const x = secToX(c.s), w = secToX(c.e) - x;
      tlCtx.fillStyle = '#065F46';
      tlCtx.beginPath(); tlCtx.roundRect(x, 145, w, 40, 4); tlCtx.fill();
      tlCtx.strokeStyle = '#34D399'; tlCtx.lineWidth = 1.2; tlCtx.stroke();
      // White left/right trim handles
      tlCtx.fillStyle = 'rgba(255,255,255,0.85)';
      tlCtx.fillRect(x, 151, 3, 28);
      tlCtx.fillRect(x + w - 3, 151, 3, 28);
      tlCtx.fillStyle = '#D1FAE5'; tlCtx.font = 'bold 9px "Segoe UI", sans-serif';
      tlCtx.save(); tlCtx.beginPath(); tlCtx.rect(x + 5, 145, w - 10, 40); tlCtx.clip();
      tlCtx.fillText(c.lbl, x + 7, 168);
      tlCtx.restore();

      // Red frame-gap measurement guide between clips (like reference Reel!)
      if (idx < v2Clips.length - 1 && ((Math.floor(t * 2) + idx) % 2 === 0)) {
        const nx = secToX(v2Clips[idx + 1].s);
        const gx0 = x + w + 2, gx1 = nx - 2;
        if (gx1 - gx0 > 18) {
          tlCtx.strokeStyle = '#F43F5E';
          tlCtx.lineWidth = 1.2;
          tlCtx.beginPath();
          tlCtx.moveTo(gx0, 165); tlCtx.lineTo(gx1, 165);
          tlCtx.moveTo(gx0, 158); tlCtx.lineTo(gx0, 172);
          tlCtx.moveTo(gx1, 158); tlCtx.lineTo(gx1, 172);
          tlCtx.stroke();
          const framesGap = Math.round((v2Clips[idx + 1].s - c.e) * 60);
          tlCtx.fillStyle = '#FB7185';
          tlCtx.font = 'bold 8px Consolas, monospace';
          tlCtx.fillText(`${framesGap}f`, (gx0 + gx1) * 0.5 - 8, 161);
        }
      }
    }

    // 7. Track V1: MAIN HERO FILMSTRIP OF REAL CHỊ HẰNG (21 consecutive real thumbnails!)
    const v1X = secToX(0), v1W = secToX(21.0) - v1X;
    tlCtx.save();
    tlCtx.beginPath();
    tlCtx.roundRect(v1X, 195, v1W, 52, 5);
    tlCtx.clip();
    const cellW = v1W / 21;
    for (let i = 0; i < 21; i++) {
      const im = stripImgs[i];
      if (im && im.complete && im.naturalWidth > 0) {
        tlCtx.drawImage(im, v1X + i * cellW, 195, cellW + 1, 52);
      } else {
        tlCtx.fillStyle = '#1E293B';
        tlCtx.fillRect(v1X + i * cellW, 195, cellW, 52);
      }
    }
    // Dark top label ribbon inside V1
    tlCtx.fillStyle = 'rgba(9, 13, 22, 0.58)';
    tlCtx.fillRect(v1X, 195, v1W, 15);
    tlCtx.restore();

    // Cut lines & Transition icons matching exact Talking-Head beats of 261119 video!
    const cuts = [
      { t: 0.0,  lbl: 'CamA_ChiHang_Hook' },
      { t: 5.0,  lbl: 'CamA_NoiTietToNu' },
      { t: 11.2, lbl: 'CamA_CanBangCoThe' },
      { t: 16.0, lbl: 'CamA_NangLuongTuTin' }
    ];
    tlCtx.strokeStyle = '#00E5FF'; tlCtx.lineWidth = 1.5;
    tlCtx.strokeRect(v1X, 195, v1W, 52);
    for (let i = 0; i < cuts.length; i++) {
      const cx = secToX(cuts[i].t);
      if (i > 0) {
        tlCtx.strokeStyle = '#090D16'; tlCtx.lineWidth = 3;
        tlCtx.beginPath(); tlCtx.moveTo(cx, 195); tlCtx.lineTo(cx, 247); tlCtx.stroke();
        // Transition square icon
        tlCtx.fillStyle = '#F8FAFC';
        tlCtx.fillRect(cx - 5, 216, 10, 10);
        tlCtx.strokeStyle = '#0284C7'; tlCtx.lineWidth = 1;
        tlCtx.strokeRect(cx - 5, 216, 10, 10);
      }
      tlCtx.fillStyle = '#F8FAFC'; tlCtx.font = 'bold 8.5px Consolas, monospace';
      tlCtx.fillText(cuts[i].lbl, cx + 5, 206);
    }

    // 8. Track A1: Real Chị Hằng Voiceover Waveform (240 bars from AUDIO_DATA)
    const a1X = secToX(0), a1W = secToX(TOTAL_SEC) - a1X;
    tlCtx.fillStyle = '#0F3D3E';
    tlCtx.beginPath(); tlCtx.roundRect(a1X, 257, a1W, 46, 4); tlCtx.fill();
    tlCtx.strokeStyle = '#14B8A6'; tlCtx.lineWidth = 1; tlCtx.stroke();

    const wf = (window.AUDIO_DATA && window.AUDIO_DATA.waveform) ? window.AUDIO_DATA.waveform : [];
    const barStep = a1W / Math.max(1, wf.length);
    for (let b = 0; b < wf.length; b++) {
      const amp = wf[b];
      const bh = Math.max(2, amp * 38);
      const bx = a1X + b * barStep;
      const played = (b / wf.length) * TOTAL_SEC <= t;
      tlCtx.fillStyle = played ? '#5EEAD4' : '#2DD4BF';
      tlCtx.fillRect(bx, 280 - bh * 0.5, Math.max(1.5, barStep - 1), bh);
    }
    tlCtx.fillStyle = 'rgba(8, 15, 22, 0.82)';
    tlCtx.fillRect(a1X + 3, 258, 290, 13);
    tlCtx.fillStyle = '#CCFBF1'; tlCtx.font = 'bold 8.5px Consolas, monospace';
    tlCtx.fillText('VO_ChiHang_Master_48kHz.wav (-14.0 LUFS • Micro-Fade ON)', a1X + 6, 268);

    // 9. Track A2: BGM Sidechain Ducking + Tactile Micro-SFX Ticks
    tlCtx.fillStyle = '#1E2952';
    tlCtx.beginPath(); tlCtx.roundRect(a1X, 313, a1W, 26, 3); tlCtx.fill();
    tlCtx.strokeStyle = '#60A5FA'; tlCtx.lineWidth = 1; tlCtx.stroke();
    // Yellow Sidechain Ducking Curve
    tlCtx.strokeStyle = '#FBBF24'; tlCtx.lineWidth = 1.5;
    tlCtx.beginPath();
    for (let i = 0; i <= 70; i++) {
      const st = (i / 70) * TOTAL_SEC;
      const dx = secToX(st);
      const envIdx = Math.min(TOTAL_FRAMES - 1, Math.floor((i / 70) * (TOTAL_FRAMES - 1)));
      const vAmp = window.AUDIO_DATA ? window.AUDIO_DATA.env_l[envIdx] : 0.4;
      const dy = 321 + vAmp * 12; // ducks down when voice is loud!
      if (i === 0) tlCtx.moveTo(dx, dy); else tlCtx.lineTo(dx, dy);
    }
    tlCtx.stroke();

    // Micro-SFX Clips row (y = 342..362)
    const sfxTicks = [0.2, 1.4, 3.0, 5.0, 6.8, 8.6, 11.2, 13.0, 14.8, 16.2, 18.0, 19.6, 20.9];
    for (let i = 0; i < sfxTicks.length; i++) {
      const sx = secToX(sfxTicks[i]);
      tlCtx.fillStyle = i % 2 === 0 ? '#D97706' : '#0284C7';
      tlCtx.beginPath(); tlCtx.roundRect(sx, 342, 34, 19, 3); tlCtx.fill();
      tlCtx.strokeStyle = '#FDE68A'; tlCtx.lineWidth = 0.8; tlCtx.stroke();
      tlCtx.fillStyle = '#FFF'; tlCtx.font = '7.8px Consolas, monospace';
      tlCtx.fillText(i % 2 === 0 ? 'Whoosh' : 'Pop', sx + 3, 354);
    }

    // 10. Active Cyan Marquee Selection Boxes from Timeline Cursors
    for (const mq of activeMarquees) {
      const rx = Math.min(mq.x0, mq.x1);
      const ry = Math.min(mq.y0, mq.y1) - 1534; // convert stage Y -> tl-canvas Y
      const rw = Math.abs(mq.x1 - mq.x0);
      const rh = Math.abs(mq.y1 - mq.y0);
      if (ry > 20 && ry < H) {
        tlCtx.fillStyle = 'rgba(0, 229, 255, 0.16)';
        tlCtx.fillRect(rx, ry, rw, rh);
        tlCtx.strokeStyle = '#00E5FF';
        tlCtx.lineWidth = 1.2;
        tlCtx.strokeRect(rx, ry, rw, rh);
      }
    }

    // 11. Smooth White Playhead (0.0s -> 18.0s)
    const phX = secToX(t);
    tlCtx.strokeStyle = '#FFFFFF';
    tlCtx.lineWidth = 2;
    tlCtx.beginPath();
    tlCtx.moveTo(phX, 8);
    tlCtx.lineTo(phX, H);
    tlCtx.stroke();

    // Playhead Pentagon Cap
    tlCtx.fillStyle = '#00E5FF';
    tlCtx.beginPath();
    tlCtx.moveTo(phX - 6, 3);
    tlCtx.lineTo(phX + 6, 3);
    tlCtx.lineTo(phX + 6, 12);
    tlCtx.lineTo(phX, 18);
    tlCtx.lineTo(phX - 6, 12);
    tlCtx.closePath();
    tlCtx.fill();
  }

  // ==================== 6. DRAW LIVE RGB SCOPES ====================
  const sc1 = document.getElementById('scope-cvs-1').getContext('2d');
  const sc2 = document.getElementById('scope-cvs-2').getContext('2d');
  const sc3 = document.getElementById('scope-cvs-3').getContext('2d');

  function drawScopes(t, vAmp) {
    // Scope 1: Luma Waveform
    sc1.fillStyle = '#090B10'; sc1.fillRect(0, 0, 66, 135);
    sc1.strokeStyle = 'rgba(52, 211, 153, 0.65)'; sc1.lineWidth = 1;
    sc1.beginPath();
    for (let x = 0; x < 66; x += 2) {
      const y = 70 + Math.sin(x * 0.22 + t * 5) * 24 + Math.cos(x * 0.5 - t * 3) * 14 * (0.6 + vAmp);
      if (x === 0) sc1.moveTo(x, y); else sc1.lineTo(x, y);
    }
    sc1.stroke();

    // Scope 2: RGB Parade
    sc2.fillStyle = '#090B10'; sc2.fillRect(0, 0, 66, 135);
    const cols = ['rgba(248,113,113,0.75)', 'rgba(74,222,128,0.75)', 'rgba(96,165,250,0.75)'];
    for (let c = 0; c < 3; c++) {
      sc2.fillStyle = cols[c];
      for (let i = 0; i < 9; i++) {
        const bx = c * 22 + 2 + i * 2;
        const bh = 28 + Math.abs(Math.sin(t * 4 + c * 1.7 + i * 0.6)) * 65;
        sc2.fillRect(bx, 118 - bh, 1.5, bh);
      }
    }

    // Scope 3: Vectorscope + Skin-Tone Line
    sc3.fillStyle = '#090B10'; sc3.fillRect(0, 0, 66, 135);
    sc3.strokeStyle = '#1E293B'; sc3.lineWidth = 1;
    sc3.beginPath(); sc3.arc(33, 74, 26, 0, Math.PI * 2); sc3.stroke();
    // Skin-tone I-line
    sc3.strokeStyle = 'rgba(251, 191, 36, 0.65)';
    sc3.beginPath(); sc3.moveTo(33, 74); sc3.lineTo(19, 51); sc3.stroke();
    // Glowing skin-tone cloud
    sc3.fillStyle = 'rgba(253, 186, 116, 0.55)';
    for (let k = 0; k < 14; k++) {
      const ang = -2.1 + Math.sin(t * 3 + k) * 0.28;
      const rad = 6 + (k / 14) * 16;
      sc3.fillRect(33 + Math.cos(ang) * rad, 74 + Math.sin(ang) * rad, 2, 2);
    }
  }

  // ==================== 7. MASTER DETERMINISTIC RENDER FRAME ====================
  const cursorCanvas = document.getElementById('cursor-canvas');
  const curCtx = cursorCanvas.getContext('2d');
  const previewImg = document.getElementById('chihang-video-img');

  const cmsTypingStr = '5 sản phẩm cần biết cho phụ nữ sau tuổi 25! Bí quyết chăm sóc sức khỏe chủ động cùng Chị Hằng — Hằng Thu Pharma';
  const aiPromptStr = 'Đồng bộ video quay thật Chị Hằng (5 sản phẩm tuổi 25) + B-Roll sản phẩm thật • Chỉnh tươi da 96% • Lọc 0% thoại lặp • Safe-Zone 9:16';

  window.renderFrame = async function (frameIdx) {
    const f = Math.max(0, Math.min(TOTAL_FRAMES - 1, frameIdx));
    const t = f / FPS;

    // 1. Update Top System Bar
    document.getElementById('sys-task-rate').textContent = `${134 + Math.floor(Math.sin(t * 4) * 18 + 18)} ops/sec`;
    document.getElementById('sys-gpu').textContent = `RTX 4070 • ${91 + (Math.floor(t * 3) % 7)}%`;
    const secWhole = Math.floor(18 + t);
    document.getElementById('sys-clock').textContent = `14:45:${String(secWhole % 60).padStart(2, '0')}`;

    // 2. Update Window 1: Automated CMS / Website
    const activeCmsTab = Math.floor(t / 6) % 3;
    for (let k = 0; k < 3; k++) {
      document.getElementById(`cms-tab-${k}`).className = k === activeCmsTab ? 'btab active' : 'btab';
      document.getElementById(`cms-c${k}`).className = k === (Math.floor(t * 1.4) % 3) ? 'cms-card selected' : 'cms-card';
    }
    const urls = [
      'https://cms.hangthupharma.vn/auto-campaigns/dieu-kinh-ht-261127',
      'https://ads.tiktok.com/i18n/perf/htpm-k6-auto-reels-sync',
      'https://hangthupharma.vn/dieu-kinh-bo-trung-chinh-hang?seo=auto'
    ];
    document.getElementById('cms-url').textContent = urls[activeCmsTab];
    document.getElementById('cms-step-lbl').textContent = `DOM Sync #${480 + Math.floor(t * 14)}`;

    // Smooth auto-scroll inside CMS website
    const scrollY = Math.max(0, Math.sin(t * 0.75 - 0.5) * 44 + 28);
    document.getElementById('cms-scroll').style.transform = `translateY(${-scrollY.toFixed(1)}px)`;

    // Live auto-typing Vietnamese copy
    const typedLen = Math.floor(((t * 28) % (cmsTypingStr.length + 18)));
    const caret = (Math.floor(f / 15) % 2 === 0) ? '▋' : '';
    document.getElementById('cms-typing-box').textContent = cmsTypingStr.slice(0, Math.min(cmsTypingStr.length, typedLen)) + caret;

    // Live DOM Inspector Highlight Box jumping between elements
    const domBoxes = [
      { l: 12, t: 46 - scrollY, w: 162, h: 132, tag: 'div.cms-card#sku-dk01 • 162×132' },
      { l: 180, t: 46 - scrollY, w: 162, h: 132, tag: 'div.cms-card#sku-nlh2 • 162×132' },
      { l: 382, t: 10 - scrollY, w: 132, h: 26,  tag: 'button#btn-publish • click()' },
      { l: 12, t: 188 - scrollY, w: 500, h: 46, tag: 'input#campaign-title • type()' },
      { l: 12, t: 252 - scrollY, w: 500, h: 82, tag: 'table.channel-matrix • sync()' }
    ];
    const db = domBoxes[Math.floor(t * 2.2) % domBoxes.length];
    const domEl = document.getElementById('dom-inspect-box');
    domEl.style.left = `${db.l}px`;
    domEl.style.top = `${Math.max(6, db.t)}px`;
    domEl.style.width = `${db.w}px`;
    domEl.style.height = `${db.h}px`;
    document.getElementById('dom-inspect-tag').textContent = db.tag;

    // 3. Update Window 2: Gemini Pro / Flow AI Asset Pipeline
    const activeAiTab = Math.floor(t / 4.5) % 3;
    for (let k = 0; k < 3; k++) {
      document.getElementById(`ai-tab-${k}`).className = k === activeAiTab ? 'btab active' : 'btab';
    }
    document.getElementById('ai-acc-pill').textContent = `u/${Math.floor(t / 3.5) % 6} ACTIVE`;
    const pLen = Math.floor(((t * 36) % (aiPromptStr.length + 22)));
    document.getElementById('ai-prompt-typing').textContent = aiPromptStr.slice(0, Math.min(aiPromptStr.length, pLen)) + caret;
    for (let g = 0; g < 4; g++) {
      const pct = Math.min(100, Math.floor(58 + ((t * 22 + g * 19) % 52)));
      document.getElementById(`gprog-${g}`).style.width = `${pct}%`;
      document.getElementById(`gcard-${g}`).className = pct >= 95 ? 'gen-card ready' : 'gen-card';
    }

    // 4. Update Window 3: Code IDE with multi-cursor live lines
    const codeWrap = document.getElementById('ide-code-wrap');
    const activeLineIdx = Math.floor(t * 3.5) % codeLinesData.length;
    let codeHtml = '';
    for (let i = 0; i < codeLinesData.length; i++) {
      const row = codeLinesData[i];
      const extraCls = (i === activeLineIdx || i === (activeLineIdx + 5) % codeLinesData.length) ? ' code-cur' : '';
      codeHtml += `<div class="code-line ${row.cls}${extraCls}"><span class="code-ln">${row.ln}</span><span>${row.html}</span></div>`;
    }
    codeWrap.innerHTML = codeHtml;
    document.getElementById('ide-diff-stat').textContent = `+${260 + Math.floor(t * 4)} -19 lines`;
    for (let tr = 0; tr < 9; tr++) {
      document.getElementById(`tr-${tr}`).className = tr === (Math.floor(t * 1.2) % 9) ? 'tree-item active' : 'tree-item';
    }

    // 5. Update Window 4: Swarm Tool-Call Stream (scrolling live logs)
    const streamEl = document.getElementById('tool-stream');
    const scrollStep = Math.floor(t * 2.6);
    let logsHtml = '';
    for (let r = 0; r < 9; r++) {
      const item = allToolLogs[(scrollStep + r) % allToolLogs.length];
      const isLatest = r === 8;
      logsHtml += `<div class="tlog${isLatest ? ' active' : ''}">` +
        `<span><span class="${isLatest ? 'run' : 'ok'}">${isLatest ? '▶' : '✓'}</span>${item.txt}</span>` +
        `<span class="diff-p">${item.diff}</span></div>`;
    }
    streamEl.innerHTML = logsHtml;
    document.getElementById('swarm-completed').textContent = `${412 + Math.floor(t * 8)} tasks ✓`;

    // 6. Update Bottom NLE Editor: Media Bin, Inspector Sliders & Color Wheels
    const selBin = Math.floor(t * 1.8) % 8;
    for (let b = 0; b < 8; b++) {
      document.getElementById(`bin-${b}`).className = b === selBin ? 'bin-item selected' : 'bin-item';
    }
    const nleTabIdx = Math.floor(t / 2.6) % 7;
    for (let nt = 0; nt < 7; nt++) {
      document.getElementById(`ntab-${nt}`).className = nt === nleTabIdx ? 'nle-tab active' : 'nle-tab';
    }

    // Animate 9 Inspector Sliders smoothly
    const sliderSpecs = [
      { min: 100, max: 106, fmt: v => `${v.toFixed(1)}%`, ph: 0.4 },
      { min: -6,  max: 6,   fmt: v => `${v.toFixed(1)}`,  ph: 1.1 },
      { min: -18, max: -4,  fmt: v => `${v.toFixed(1)}`,  ph: 2.0 },
      { min: 2.0, max: 6.5, fmt: v => `+${v.toFixed(1)}`, ph: 0.8 },
      { min: 0.15,max: 0.55,fmt: v => `+${v.toFixed(2)}`, ph: 1.7 },
      { min: 7.0, max: 15.0,fmt: v => `+${v.toFixed(1)}`, ph: 2.5 },
      { min: 104, max: 112, fmt: v => `${v.toFixed(1)}%`, ph: 3.1 },
      { min: 1.8, max: 3.2, fmt: v => `+${v.toFixed(1)}dB`,ph: 1.4 },
      { min: -12, max: -8.5,fmt: v => `${v.toFixed(1)}dB`,ph: 2.8 }
    ];
    for (let s = 0; s < sliderSpecs.length; s++) {
      const sp = sliderSpecs[s];
      const norm = 0.5 + 0.38 * Math.sin(t * 2.4 + sp.ph);
      const val = sp.min + norm * (sp.max - sp.min);
      document.getElementById(`sl-${s}-f`).style.width = `${(norm * 100).toFixed(1)}%`;
      document.getElementById(`sl-${s}-t`).style.left = `${(norm * 100).toFixed(1)}%`;
      document.getElementById(`sl-${s}-v`).textContent = sp.fmt(val);
    }

    // Color wheel pucks subtle motion
    for (let cw = 0; cw < 3; cw++) {
      const dx = Math.sin(t * 2.1 + cw * 2) * 5;
      const dy = Math.cos(t * 1.7 + cw) * 5;
      document.getElementById(`cw-${cw}`).style.transform = `translate(calc(-50% + ${dx.toFixed(1)}px), calc(-50% + ${dy.toFixed(1)}px))`;
    }

    // 7. Update HERO PROGRAM MONITOR (Real Video of Chị Hằng + Scopes + Audio Meters)
    const secI = Math.floor(t);
    const frmI = Math.floor((t - secI) * 60);
    document.getElementById('mon-tc').textContent = `00:00:${String(secI).padStart(2, '0')}:${String(frmI).padStart(2, '0')}`;

    const shotLabel = t < 5.0  ? 'CAM A • CHỊ HẰNG (HOOK TUỔI 25)'
                    : t < 11.2 ? 'CAM A • CHỊ HẰNG (NỘI TIẾT TỐ)'
                    : t < 16.0 ? 'CAM A • CHỊ HẰNG (CÂN BẰNG CƠ THỂ)'
                    : t < 20.95? 'CAM A • CHỊ HẰNG (TRÀN NĂNG LƯỢNG)'
                    : '✓ RENDER COMPLETE • 1080P 60FPS';
    document.getElementById('mon-shot-name').textContent = shotLabel;

    // Brief LUT wipe check & Caption Transform Gizmo
    const lutEl = document.getElementById('lut-wipe');
    if ((t > 3.2 && t < 3.9) || (t > 12.8 && t < 13.5)) {
      const localU = (t < 8 ? (t - 3.2) : (t - 12.8)) / 0.7;
      lutEl.style.display = 'block';
      lutEl.style.width = `${(Math.sin(localU * Math.PI) * 72).toFixed(1)}%`;
    } else {
      lutEl.style.display = 'none';
    }
    const gizEl = document.getElementById('mon-gizmo');
    gizEl.style.display = ((t > 1.0 && t < 1.9) || (t > 6.6 && t < 7.5) || (t > 17.2 && t < 18.1)) ? 'block' : 'none';

    // Audio VU Meters driven by Chị Hằng's REAL trimmed voiceover envelope
    const ampL = window.AUDIO_DATA ? window.AUDIO_DATA.env_l[f] : 0.1;
    const ampR = window.AUDIO_DATA ? window.AUDIO_DATA.env_r[f] : 0.1;
    const vuH_L = Math.min(96, Math.max(6, ampL * 92 + 6));
    const vuH_R = Math.min(96, Math.max(6, ampR * 92 + 6));
    document.getElementById('vu-l').style.height = `${vuH_L.toFixed(1)}%`;
    document.getElementById('vu-r').style.height = `${vuH_R.toFixed(1)}%`;
    const dbVal = ampL < 0.02 ? -48.0 : (-24 + Math.max(ampL, ampR) * 14);
    document.getElementById('vu-db-txt').textContent = `${dbVal.toFixed(1)}dB`;

    drawScopes(t, Math.max(ampL, ampR));

    // Load exact frame f+1 of Chị Hằng's real video (locking cleanly at resting smile frame 1258 after 20.95s!)
    const safeVidFrame = Math.min(1258, f + 1);
    const targetSrc = `assets/preview_frames/f_${String(safeVidFrame).padStart(4, '0')}.jpg`;
    if (!previewImg.src.endsWith(targetSrc)) {
      await new Promise((resolve) => {
        previewImg.onload = resolve;
        previewImg.onerror = resolve;
        previewImg.src = targetSrc;
      });
    }

    // 8. Compute All 68 Cursors, Click Ripples, Ghost Drag Cards & Marquees
    curCtx.clearRect(0, 0, 1080, 1920);
    const activeMarquees = [];

    for (const c of cursors) {
      let wp = null;
      for (let k = 0; k < c.waypoints.length; k++) {
        const cand = c.waypoints[k];
        if (f >= cand.fStart && f < cand.fEnd) { wp = cand; break; }
      }
      if (!wp) continue;

      let cx, cy, scale = 1.0;
      if (f < wp.fMoveEnd) {
        const u = (f - wp.fStart) / Math.max(1, wp.fMoveEnd - wp.fStart);
        const s = minJerk(u);
        // Quadratic Bezier curved path
        const mx = (wp.x0 + wp.x1) * 0.5 - (wp.y1 - wp.y0) * 0.12 + wp.arc;
        const my = (wp.y0 + wp.y1) * 0.5 + (wp.x1 - wp.x0) * 0.12;
        const inv = 1 - s;
        cx = inv * inv * wp.x0 + 2 * inv * s * mx + s * s * wp.x1;
        cy = inv * inv * wp.y0 + 2 * inv * s * my + s * s * wp.y1;

        // If carrying a clip from Top Browser / Media Bin to Timeline, draw floating ghost thumbnail!
        if (wp.carrying) {
          const gImg = dragImgs[wp.thumbIdx];
          if (gImg && gImg.complete && gImg.naturalWidth > 0) {
            curCtx.save();
            curCtx.globalAlpha = 0.82;
            curCtx.drawImage(gImg, cx + 8, cy + 8, 68, 42);
            curCtx.strokeStyle = '#00E5FF';
            curCtx.lineWidth = 1.5;
            curCtx.strokeRect(cx + 8, cy + 8, 68, 42);
            curCtx.restore();
          }
        }
      } else {
        // Hold / Click / Drag action phase
        const hu = (f - wp.fMoveEnd) / Math.max(1, wp.fEnd - wp.fMoveEnd);
        const hs = minJerk(hu);
        cx = wp.x1 + wp.dragdx * hs;
        cy = wp.y1 + wp.dragdy * hs;

        // Subtle click squish & ripple ring in first 8 frames of hold
        const hf = f - wp.fMoveEnd;
        if (hf < 6) scale = 0.86;
        if (hf < 12) {
          const rad = 3 + hf * 1.35;
          curCtx.save();
          curCtx.strokeStyle = `rgba(56, 189, 248, ${(1 - hf / 12) * 0.65})`;
          curCtx.lineWidth = 1.4;
          curCtx.beginPath();
          curCtx.arc(cx, cy, rad, 0, Math.PI * 2);
          curCtx.stroke();
          curCtx.restore();
        }

        if (wp.actionKind === 'marquee') {
          activeMarquees.push({ x0: wp.x1, y0: wp.y1, x1: cx, y1: cy });
        }
      }

      drawArrowCursor(curCtx, cx, cy, scale, wp.ctype, c.badge);
    }

    // 9. Draw Timeline Canvas (including active cursor marquees & playhead)
    drawTimeline(f, t, activeMarquees);
  };
})();
