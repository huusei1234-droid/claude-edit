// V2 Engine: Rapid Multi-App Jumping (Ps / Ai / Me / Web / IDE) + Dynamic Link (Premiere Pro <-> After Effects) + 72 Cursors @ 60fps
(function () {
  const FPS = 60;
  const TOTAL_FRAMES = 1281; // 21.35s @ 60fps
  const TOTAL_SEC = TOTAL_FRAMES / FPS;

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

  // Preload Timeline Filmstrip & Real HTPM Cutout Images for Photoshop Canvas & Dragging
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

  const dragPaths = [
    'assets/thumbs/bin_02_laptop_w.jpg',
    'assets/thumbs/bin_05_gelpk.jpg',
    'assets/thumbs/bin_06_whiteskin.jpg',
    'assets/thumbs/bin_08_nlh_real.jpg',
    'assets/thumbs/SP_WHITESKIN_COMBO_CUTOUT.png'
  ];
  const dragImgs = dragPaths.map(p => { const im = new Image(); im.src = p; return im; });

  // ==================== 1. EXTENDSCRIPT (.JSX) & PYTHON CODE ====================
  const jsxLines = [
    { cls: '',    h: '<span class="cm">// Adobe Dynamic Link Automation: Ps -> Ae -> Pr 2026</span>' },
    { cls: 'add', h: '<span class="kw">const</span> seq = app.project.activeSequence; <span class="cm">// ChiHang_9x16</span>' },
    { cls: 'add', h: '<span class="kw">await</span> photoshop.<span class="fn">batchCutoutSKU</span>(<span class="st">"HTPM_5_Products"</span>, { feather: <span class="nu">0.8</span> });' },
    { cls: '',    h: '<span class="kw">const</span> aeComp = bridge.<span class="fn">linkAfterEffectsComp</span>(<span class="st">"Combo_5SanPham.aep"</span>);' },
    { cls: 'add', h: 'aeComp.layer(<span class="st">"ChiHang_Card"</span>).scale.<span class="fn">setTemporalEase</span>([<span class="nu">82</span>, <span class="nu">0.15</span>]);' },
    { cls: 'add', h: 'seq.videoTracks[<span class="nu">0</span>].<span class="fn">applyLumetri</span>({ lut: <span class="st">"WarmSkin96.cube"</span>, exp: <span class="nu">0.32</span> });' },
    { cls: '',    h: '<span class="kw">await</span> whisper.<span class="fn">verifyZeroRepeat</span>(seq.audioTracks[<span class="nu">0</span>], { lufs: <span class="nu">-14.0</span> });' },
    { cls: 'add', h: '<span class="kw">await</span> webSwarm.<span class="fn">publishAllChannels</span>([<span class="st">"CMS"</span>, <span class="st">"TikTok"</span>, <span class="st">"Fanpage"</span>]);' },
    { cls: '',    h: 'mediaEncoder.<span class="fn">queueH264Nvenc</span>(seq, { fps: <span class="nu">60</span>, cq: <span class="nu">17</span> });' },
    { cls: 'add', h: 'console.<span class="fn">log</span>(<span class="st">"[SYNC OK] 72 AI Agents • Pr + Ae + Ps + Web Active"</span>);' }
  ];

  const swarmLogs = [
    { app: 'Ps', txt: 'ps_batch: Select Subject + Curves Skin 96% -> SP_WhiteSkin.psd', st: 'DONE 84ms' },
    { app: 'Ae', txt: 'ae-3d-effects.jsx: Easy-Ease Bezier Graph [85% influence]', st: 'LINKED' },
    { app: 'Pr', txt: 'premiere.lumetri: Applied Warm_Skin_96.cube on CamA_ChiHang', st: '60.0fps' },
    { app: 'Ai', txt: 'illustrator.svg: Exported HTPM Gold Seal Vector to Ae Comp', st: 'SYNCED' },
    { app: 'Web',txt: 'CDP :9333 -> cms.hangthupharma.vn/5-san-pham-tuoi-25', st: '200 OK' },
    { app: 'Me', txt: 'Media Encoder: H.264 NVENC 1080x1920 60fps (-14.2 LUFS)', st: 'QUEUED' },
    { app: 'QC', txt: 'faster-whisper: 4 câu trọn vẹn • 0% lặp từ • SafeZone PASS', st: 'VERIFIED' },
    { app: 'Ps', txt: 'ps_export_layer: SP_GelPhuKhang_Cutout.png -> Pr Track V2', st: '+1 Layer' },
    { app: 'Ae', txt: 'Roto Brush 3.0 Matte Freeze • 1,281 frames locked', st: '100% OK' },
    { app: 'Web',txt: 'Gemini Pro u/0..u/4 asset check + TikTok Shop SKU bind', st: 'LIVE' }
  ];

  // ==================== 2. RAPID TOP-DESKTOP WINDOW CHOREOGRAPHY ====================
  // Every ~1.52 seconds (91 frames), the Top Desktop jumps focus to a new foreground hero app
  // while surrounding apps cascade & tile smoothly around it!
  const TOP_LAYOUTS = [
    // Step 0: Photoshop Hero Front-Left + Illustrator Right + CMS & Gemini Bottom
    {
      focus: 'ps', dock: 'dk-ps', atIdx: 0,
      rects: {
        ps:    { x: 14,  y: 12,  w: 640, h: 468, z: 30, s: 1.00 },
        ai:    { x: 548, y: 18,  w: 518, h: 396, z: 22, s: 0.98 },
        cms:   { x: 18,  y: 452, w: 530, h: 436, z: 24, s: 0.99 },
        gem:   { x: 552, y: 456, w: 514, h: 430, z: 23, s: 0.98 },
        ide:   { x: 250, y: 230, w: 540, h: 400, z: 14, s: 0.94 },
        swarm: { x: 530, y: 220, w: 510, h: 400, z: 15, s: 0.94 }
      }
    },
    // Step 1: Illustrator Vector Badge Jumps Front-Right + IDE Code Pops Front-Left!
    {
      focus: 'ai', dock: 'dk-ai', atIdx: 3,
      rects: {
        ai:    { x: 495, y: 16,  w: 570, h: 430, z: 31, s: 1.02 },
        ide:   { x: 12,  y: 26,  w: 550, h: 422, z: 29, s: 1.00 },
        ps:    { x: 24,  y: 420, w: 610, h: 465, z: 22, s: 0.97 },
        swarm: { x: 552, y: 456, w: 514, h: 425, z: 26, s: 0.99 },
        cms:   { x: 180, y: 455, w: 520, h: 420, z: 15, s: 0.95 },
        gem:   { x: 520, y: 210, w: 510, h: 410, z: 14, s: 0.94 }
      }
    },
    // Step 2: Chrome Auto-CMS Website Jumps Center-Top + Gemini Pro Right!
    {
      focus: 'cms', dock: 'dk-web', atIdx: 5,
      rects: {
        cms:   { x: 14,  y: 14,  w: 555, h: 452, z: 32, s: 1.01 },
        gem:   { x: 544, y: 18,  w: 522, h: 444, z: 30, s: 1.00 },
        ps:    { x: 16,  y: 442, w: 620, h: 446, z: 25, s: 0.98 },
        swarm: { x: 556, y: 466, w: 510, h: 418, z: 27, s: 0.99 },
        ai:    { x: 260, y: 180, w: 510, h: 390, z: 14, s: 0.94 },
        ide:   { x: 40,  y: 250, w: 530, h: 395, z: 16, s: 0.95 }
      }
    },
    // Step 3: Media Encoder + Swarm CLI Jumps Center-Right + Photoshop Retouch Left!
    {
      focus: 'swarm', dock: 'dk-ag', atIdx: 4,
      rects: {
        ps:    { x: 10,  y: 18,  w: 635, h: 466, z: 29, s: 1.00 },
        swarm: { x: 545, y: 14,  w: 522, h: 432, z: 32, s: 1.02 },
        ide:   { x: 14,  y: 468, w: 552, h: 418, z: 28, s: 1.00 },
        ai:    { x: 548, y: 454, w: 518, h: 428, z: 26, s: 0.98 },
        cms:   { x: 210, y: 440, w: 520, h: 420, z: 15, s: 0.95 },
        gem:   { x: 490, y: 220, w: 510, h: 410, z: 14, s: 0.94 }
      }
    },
    // Step 4: Photoshop Center Hero Spotlight (Generative Mask & Curves) + Surrounding Cascade!
    {
      focus: 'ps', dock: 'dk-ps', atIdx: 0,
      rects: {
        ps:    { x: 215, y: 20,  w: 650, h: 472, z: 34, s: 1.03 },
        cms:   { x: 10,  y: 448, w: 532, h: 438, z: 26, s: 0.98 },
        gem:   { x: 548, y: 450, w: 520, h: 436, z: 27, s: 0.98 },
        ide:   { x: 10,  y: 14,  w: 490, h: 400, z: 19, s: 0.95 },
        ai:    { x: 560, y: 16,  w: 506, h: 392, z: 20, s: 0.95 },
        swarm: { x: 280, y: 470, w: 500, h: 405, z: 18, s: 0.95 }
      }
    }
  ];

  const WIN_IDS = ['ps', 'ai', 'cms', 'gem', 'ide', 'swarm'];

  function getLayoutState(f) {
    const STEP_F = 86; // Jump apps every 1.43s -> super lively, continuous switching!
    const idx = Math.floor(f / STEP_F);
    const localF = f - idx * STEP_F;
    const L0 = TOP_LAYOUTS[idx % TOP_LAYOUTS.length];
    const L1 = TOP_LAYOUTS[(idx + 1) % TOP_LAYOUTS.length];

    // Fast snappy spring transition over first 18 frames (0.30s) of each step
    const transU = Math.min(1, localF / 18);
    const s = minJerk(transU);
    // Slight pop overshoot on focused window
    const popBoost = transU < 1 ? Math.sin(transU * Math.PI) * 0.028 : 0;

    const curRects = {};
    for (const k of WIN_IDS) {
      const r0 = L0.rects[k], r1 = L1.rects[k];
      // Wait until last 18 frames of step to morph to L1, or morph at start of step:
      const a = idx === 0 ? r1 : TOP_LAYOUTS[(idx - 1) % TOP_LAYOUTS.length].rects[k];
      const b = L0.rects[k];
      curRects[k] = {
        x: a.x + (b.x - a.x) * s,
        y: a.y + (b.y - a.y) * s,
        w: a.w + (b.w - a.w) * s,
        h: a.h + (b.h - a.h) * s,
        z: b.z,
        sc: (a.s + (b.s - a.s) * s) + (k === L0.focus ? popBoost : 0)
      };
    }

    const showAltTab = idx > 0 && localF < 15; // Flash Alt+Tab switcher for 0.25s right on jump!
    return { focus: L0.focus, dock: L0.dock, atIdx: L0.atIdx, rects: curRects, showAltTab };
  }

  // ==================== 3. DRAW PHOTOSHOP 2026 CANVAS ====================
  const psCvs = document.getElementById('ps-cvs');
  const psCtx = psCvs.getContext('2d');

  function drawPhotoshop(f, t) {
    const W = 410, H = 365;
    psCtx.clearRect(0, 0, W, H);

    // Subtle studio backdrop glow inside PS smart object
    const grd = psCtx.createRadialGradient(W * 0.5, H * 0.5, 20, W * 0.5, H * 0.5, 200);
    grd.addColorStop(0, 'rgba(49, 168, 255, 0.14)');
    grd.addColorStop(1, 'rgba(0, 0, 0, 0)');
    psCtx.fillStyle = grd;
    psCtx.fillRect(0, 0, W, H);

    // Cycle active retouched HTPM SKU / Chị Hằng smart layer every 2.7s
    const assetIdx = Math.floor(t / 2.7) % psImgs.length;
    const im = psImgs[assetIdx];
    const zoom = 1.0 + Math.sin(t * 2.2) * 0.05;
    if (im && im.complete && im.naturalWidth > 0) {
      const ratio = Math.min((W * 0.74) / im.naturalWidth, (H * 0.80) / im.naturalHeight) * zoom;
      const dw = im.naturalWidth * ratio, dh = im.naturalHeight * ratio;
      const dx = (W - dw) * 0.5, dy = (H - dh) * 0.48;
      psCtx.drawImage(im, dx, dy, dw, dh);

      // Photoshop Free-Transform Cyan Box + 8 Handles
      psCtx.strokeStyle = '#31A8FF';
      psCtx.lineWidth = 1.3;
      psCtx.strokeRect(dx - 6, dy - 6, dw + 12, dh + 12);
      psCtx.fillStyle = '#FFFFFF';
      for (const [hx, hy] of [[dx-6,dy-6],[dx+dw*0.5,dy-6],[dx+dw+6,dy-6],[dx-6,dy+dh+6],[dx+dw+6,dy+dh+6]]) {
        psCtx.fillRect(hx - 3, hy - 3, 6, 6);
        psCtx.strokeRect(hx - 3, hy - 3, 6, 6);
      }

      // Animated Marching Ants Selection Contour around Subject
      psCtx.save();
      psCtx.setLineDash([5, 5]);
      psCtx.lineDashOffset = -(f * 0.8);
      psCtx.strokeStyle = '#FFFFFF';
      psCtx.lineWidth = 1.3;
      psCtx.beginPath();
      psCtx.ellipse(W * 0.5, H * 0.48, dw * 0.44, dh * 0.45, 0, 0, Math.PI * 2);
      psCtx.stroke();
      psCtx.strokeStyle = '#000000';
      psCtx.lineDashOffset = -(f * 0.8) + 5;
      psCtx.stroke();
      psCtx.restore();
    }

    // Floating Photoshop RGB Curves Adjustment Mini-HUD (Top-Right of PS Canvas)
    const cx = W - 102, cy = 10, cw = 92, ch = 92;
    psCtx.fillStyle = 'rgba(30, 30, 34, 0.90)';
    psCtx.fillRect(cx, cy, cw, ch);
    psCtx.strokeStyle = '#52525B';
    psCtx.lineWidth = 1;
    psCtx.strokeRect(cx, cy, cw, ch);
    // Grid
    psCtx.strokeStyle = '#333';
    psCtx.beginPath();
    psCtx.moveTo(cx + cw*0.5, cy); psCtx.lineTo(cx + cw*0.5, cy + ch);
    psCtx.moveTo(cx, cy + ch*0.5); psCtx.lineTo(cx + cw, cy + ch*0.5);
    psCtx.stroke();
    // S-Curve animated
    psCtx.strokeStyle = '#31A8FF';
    psCtx.lineWidth = 1.8;
    psCtx.beginPath();
    psCtx.moveTo(cx + 6, cy + ch - 6);
    const bend = Math.sin(t * 3.5) * 9;
    psCtx.bezierCurveTo(cx + 30, cy + ch - 14 + bend, cx + 60, cy + 12 - bend, cx + cw - 6, cy + 6);
    psCtx.stroke();

    // Retouch Brush Feather Circle moving across subject
    const bx = W * 0.48 + Math.cos(t * 4.2) * 52;
    const by = H * 0.45 + Math.sin(t * 3.1) * 48;
    psCtx.strokeStyle = 'rgba(255,255,255,0.8)';
    psCtx.lineWidth = 1.2;
    psCtx.beginPath(); psCtx.arc(bx, by, 18, 0, Math.PI * 2); psCtx.stroke();

    // Highlight active PS Layer & Tool
    const lIdx = Math.floor(t * 2.0) % 6;
    for (let k = 0; k < 6; k++) {
      document.getElementById(`psl-${k}`).className = k === lIdx ? 'ps-lyr sel' : 'ps-lyr';
    }
    const tIdx = Math.floor(t * 1.7) % 7;
    for (let k = 0; k < 7; k++) {
      document.getElementById(`pst-${k}`).className = k === tIdx ? 'ps-tbtn on' : 'ps-tbtn';
    }
    const psActs = ['Select Subject ✓', 'Frequency Skin 96%', 'Remove Dust ✓', 'Send Layer -> Ae'];
    document.getElementById('ps-act-lbl').textContent = psActs[Math.floor(t * 1.5) % psActs.length];
  }

  // ==================== 4. DRAW ILLUSTRATOR 2026 VECTOR ARTBOARD ====================
  const aiCvs = document.getElementById('ai-cvs');
  const aiCtx = aiCvs.getContext('2d');

  function drawIllustrator(t) {
    const W = 520, H = 372;
    aiCtx.fillStyle = '#1B1B1B';
    aiCtx.fillRect(0, 0, W, H);

    // Artboard
    const ax = 48, ay = 26, aw = 424, ah = 318;
    aiCtx.fillStyle = '#111624';
    aiCtx.fillRect(ax, ay, aw, ah);
    aiCtx.strokeStyle = '#FF9A00';
    aiCtx.lineWidth = 1.2;
    aiCtx.strokeRect(ax, ay, aw, ah);

    // Vector Golden Crest / Badge Path with Live Bezier Handles
    const cx = ax + aw * 0.5, cy = ay + 128;
    const r = 64 + Math.sin(t * 2.6) * 4;

    aiCtx.strokeStyle = '#F59E0B';
    aiCtx.lineWidth = 2.5;
    aiCtx.beginPath();
    aiCtx.arc(cx, cy, r, 0, Math.PI * 2);
    aiCtx.stroke();

    // Bezier Anchor Nodes & Handles (Illustrator Cyan #00FFFF / Orange #FF9A00)
    for (let k = 0; k < 8; k++) {
      const ang = (k / 8) * Math.PI * 2 + t * 0.35;
      const nx = cx + Math.cos(ang) * r;
      const ny = cy + Math.sin(ang) * r;
      const hx1 = nx - Math.sin(ang) * 24, hy1 = ny + Math.cos(ang) * 24;
      const hx2 = nx + Math.sin(ang) * 24, hy2 = ny - Math.cos(ang) * 24;
      aiCtx.strokeStyle = '#38BDF8'; aiCtx.lineWidth = 1;
      aiCtx.beginPath(); aiCtx.moveTo(hx1, hy1); aiCtx.lineTo(hx2, hy2); aiCtx.stroke();
      aiCtx.fillStyle = '#FFFFFF';
      aiCtx.fillRect(nx - 3, ny - 3, 6, 6);
      aiCtx.strokeRect(nx - 3, ny - 3, 6, 6);
      aiCtx.fillStyle = '#38BDF8';
      aiCtx.beginPath(); aiCtx.arc(hx1, hy1, 2.5, 0, Math.PI * 2); aiCtx.fill();
      aiCtx.beginPath(); aiCtx.arc(hx2, hy2, 2.5, 0, Math.PI * 2); aiCtx.fill();
    }

    aiCtx.fillStyle = '#FDE68A';
    aiCtx.font = '900 16px "Segoe UI", sans-serif';
    aiCtx.textAlign = 'center';
    aiCtx.fillText('HẰNG THU PHARMA', cx, cy + 5);
    aiCtx.font = 'bold 11px "Segoe UI", sans-serif';
    aiCtx.fillStyle = '#93C5FD';
    aiCtx.fillText('VECTOR TYPOGRAPHY • 5 SẢN PHẨM TUỔI 25', cx, ay + 258);
    // Bounding outline around text
    aiCtx.strokeStyle = '#FF9A00';
    aiCtx.strokeRect(cx - 148, ay + 240, 296, 26);
    aiCtx.textAlign = 'left';
  }

  // ==================== 5. DRAW AFTER EFFECTS SPEED/VALUE GRAPH EDITOR ====================
  const grCvs = document.getElementById('ae-graph-cvs');
  const grCtx = grCvs.getContext('2d');

  function drawAeGraphEditor(t) {
    const W = 288, H = 118;
    grCtx.fillStyle = '#121212';
    grCtx.fillRect(0, 0, W, H);

    // Grid lines
    grCtx.strokeStyle = '#242424'; grCtx.lineWidth = 1;
    for (let y = 24; y < H; y += 24) {
      grCtx.beginPath(); grCtx.moveTo(0, y); grCtx.lineTo(W, y); grCtx.stroke();
    }
    for (let x = 48; x < W; x += 48) {
      grCtx.beginPath(); grCtx.moveTo(x, 0); grCtx.lineTo(x, H); grCtx.stroke();
    }

    // Classic AE Yellow Speed Bell Curve + Green X/Red Y Value Curve
    const peakShift = Math.sin(t * 3.4) * 26;
    grCtx.strokeStyle = '#FACC15'; grCtx.lineWidth = 2;
    grCtx.beginPath();
    grCtx.moveTo(18, H - 18);
    grCtx.bezierCurveTo(90 + peakShift, H - 18, 95 + peakShift, 16, 144, 16);
    grCtx.bezierCurveTo(192 - peakShift, 16, 198 - peakShift, H - 18, W - 18, H - 18);
    grCtx.stroke();

    // Fill subtle yellow under speed graph
    grCtx.fillStyle = 'rgba(250, 204, 21, 0.12)';
    grCtx.lineTo(W - 18, H - 18); grCtx.closePath(); grCtx.fill();

    // Tangent handles (Yellow circles)
    const h1x = 92 + peakShift * 0.6, h2x = 196 - peakShift * 0.6;
    grCtx.strokeStyle = '#FDE047'; grCtx.lineWidth = 1.2;
    grCtx.beginPath();
    grCtx.moveTo(18, H - 18); grCtx.lineTo(h1x, H - 18);
    grCtx.moveTo(W - 18, H - 18); grCtx.lineTo(h2x, H - 18);
    grCtx.stroke();
    for (const [kx, ky] of [[18, H-18], [144, 16], [W-18, H-18], [h1x, H-18], [h2x, H-18]]) {
      grCtx.fillStyle = '#FACC15';
      grCtx.fillRect(kx - 3, ky - 3, 6, 6);
    }

    // Playhead CTI red line inside Graph Editor
    const gx = ((t * 1.4) % 1) * (W - 24) + 12;
    grCtx.strokeStyle = '#EF4444'; grCtx.lineWidth = 1.2;
    grCtx.beginPath(); grCtx.moveTo(gx, 0); grCtx.lineTo(gx, H); grCtx.stroke();
  }

  // ==================== 6. DRAW PREMIERE PRO <-> AFTER EFFECTS TIMELINE ====================
  const tlCvs = document.getElementById('tl-canvas');
  const tlCtx = tlCvs.getContext('2d');

  function isAfterEffectsMode(t) {
    // Jump dynamically between Premiere Pro (Pr) and After Effects (Ae) 4 times!
    return (t >= 4.2 && t < 8.6) || (t >= 13.4 && t < 17.8);
  }

  function drawTimeline(f, t, aeMode, activeMarquees) {
    const W = 1080, H = 398;
    const HDR_W = 112;
    const TL_W = W - HDR_W - 12;
    const secToX = (sec) => HDR_W + (sec / TOTAL_SEC) * TL_W;

    tlCtx.fillStyle = '#181818';
    tlCtx.fillRect(0, 0, W, H);

    // Timecode Ruler
    tlCtx.fillStyle = '#212121';
    tlCtx.fillRect(0, 0, W, 24);
    tlCtx.font = '9.5px Consolas, monospace';
    tlCtx.fillStyle = '#9CA3AF';
    for (let s = 0; s <= 21; s++) {
      const sx = secToX(s);
      tlCtx.strokeStyle = s % 3 === 0 ? '#52525B' : '#2E2E34';
      tlCtx.beginPath(); tlCtx.moveTo(sx, s % 3 === 0 ? 11 : 17); tlCtx.lineTo(sx, 24); tlCtx.stroke();
      if (s % 3 === 0) tlCtx.fillText(`00:00:${String(s).padStart(2, '0')}:00`, sx - 24, 10);
    }

    if (!aeMode) {
      // ======== PREMIERE PRO 2026 MULTI-TRACK SEQUENCE UI ========
      const prTracks = [
        { lbl: 'V4 [Ae Link]', y: 27,  h: 34 },
        { lbl: 'V3 Graphics',  y: 64,  h: 34 },
        { lbl: 'V2 Ps Cutout', y: 101, h: 44 },
        { lbl: 'V1 Chị Hằng',  y: 148, h: 58 },
        { lbl: 'A1 Voiceover', y: 212, h: 56 },
        { lbl: 'A2 BGM Duck',  y: 271, h: 42 },
        { lbl: 'A3 Micro-SFX', y: 316, h: 42 }
      ];
      for (const tr of prTracks) {
        tlCtx.fillStyle = '#202020'; tlCtx.fillRect(HDR_W, tr.y, W - HDR_W, tr.h);
        tlCtx.fillStyle = '#262626'; tlCtx.fillRect(0, tr.y, HDR_W - 2, tr.h);
        // Pr V1/A1 Blue target patch buttons
        tlCtx.fillStyle = tr.lbl.startsWith('V') ? '#2B579A' : '#1E6B52';
        tlCtx.fillRect(4, tr.y + 5, 22, tr.h - 10);
        tlCtx.fillStyle = '#E4E4E7'; tlCtx.font = 'bold 9px "Segoe UI", sans-serif';
        tlCtx.fillText(tr.lbl, 31, tr.y + tr.h * 0.58);
      }

      // V4: Lilac Dynamic Link AE Comp Clips
      const v4 = [
        { s: 0.0, e: 10.4, lbl: '[Ae] HTPM_5SanPham_MotionStage.aep' },
        { s: 10.6, e: 21.0, lbl: '[Ae] HTPM_NangLuong_3DCards.aep' }
      ];
      for (const c of v4) {
        const x = secToX(c.s), w = secToX(c.e) - x;
        tlCtx.fillStyle = '#6B3FA0'; tlCtx.fillRect(x, 29, w, 30);
        tlCtx.strokeStyle = '#D8B4FE'; tlCtx.strokeRect(x, 29, w, 30);
        tlCtx.fillStyle = '#FAF5FF'; tlCtx.font = 'bold 8.8px "Segoe UI"';
        tlCtx.fillText(c.lbl, x + 6, 47);
      }

      // V3: Premiere Essential Graphics (Rose/Coral)
      for (let i = 0; i < 10; i++) {
        const s = i * 2.08 + 0.05, e = (i + 1) * 2.08 - 0.08;
        const x = secToX(s), w = secToX(e) - x;
        tlCtx.fillStyle = '#9D4EDD'; tlCtx.fillRect(x, 66, w, 30);
        tlCtx.strokeStyle = '#E0AAFF'; tlCtx.strokeRect(x, 66, w, 30);
        tlCtx.fillStyle = '#FFF'; tlCtx.font = '8.2px Consolas';
        tlCtx.fillText(`Caption_${i+1}`, x + 4, 84);
      }

      // V2: Photoshop .PSD Smart Cutout Clips (Caribbean Blue)
      const v2 = [
        { s: 0.6, e: 4.8 + Math.sin(t*3)*0.12, lbl: 'SP_WhiteSkin_Cut.psd' },
        { s: 5.5, e: 10.6, lbl: 'SP_GelPhuKhang_HT.psd' },
        { s: 11.3, e: 15.8 + Math.cos(t*2.5)*0.12, lbl: 'Combo_5SanPham_HTPM.psd' },
        { s: 16.3, e: 20.9, lbl: 'QuayTay_NgocLongHoan.mov' }
      ];
      for (const c of v2) {
        const x = secToX(c.s), w = secToX(c.e) - x;
        tlCtx.fillStyle = '#2563EB'; tlCtx.fillRect(x, 103, w, 40);
        tlCtx.strokeStyle = '#93C5FD'; tlCtx.strokeRect(x, 103, w, 40);
        // Yellow Ripple Trim handle highlight on active edge
        tlCtx.fillStyle = '#FACC15'; tlCtx.fillRect(x + w - 3, 103, 3, 40);
        tlCtx.fillStyle = '#EFF6FF'; tlCtx.font = 'bold 8.8px "Segoe UI"';
        tlCtx.fillText(c.lbl, x + 6, 126);
      }

      // V1: Premiere Iris-Blue Real Chị Hằng Filmstrip (21 thumbs!)
      const v1X = secToX(0), v1W = secToX(21.0) - v1X;
      tlCtx.fillStyle = '#3B669C'; tlCtx.fillRect(v1X, 150, v1W, 54);
      const cw = v1W / 21;
      for (let i = 0; i < 21; i++) {
        const im = stripImgs[i];
        if (im && im.complete && im.naturalWidth > 0) {
          tlCtx.drawImage(im, v1X + i * cw, 164, cw + 0.8, 40);
        }
      }
      tlCtx.fillStyle = 'rgba(28, 54, 94, 0.88)';
      tlCtx.fillRect(v1X, 150, v1W, 14);
      for (const [ct, cl] of [[0,'CamA_ChiHang_Hook.mp4'],[5.0,'CamA_NoiTiet.mp4'],[11.2,'CamA_CanBang.mp4'],[16.0,'CamA_NangLuong.mp4']]) {
        const cx = secToX(ct);
        if (ct > 0) {
          tlCtx.strokeStyle = '#111'; tlCtx.lineWidth = 2.5;
          tlCtx.beginPath(); tlCtx.moveTo(cx, 150); tlCtx.lineTo(cx, 204); tlCtx.stroke();
        }
        tlCtx.fillStyle = '#E0F2FE'; tlCtx.font = 'bold 8.5px Consolas';
        tlCtx.fillText(cl, cx + 4, 160);
      }
      tlCtx.strokeStyle = '#93C5FD'; tlCtx.lineWidth = 1.2; tlCtx.strokeRect(v1X, 150, v1W, 54);

      // A1: Classic Premiere Sea-Green Audio Waveform Track (#1E6F5C)
      const a1W = secToX(TOTAL_SEC) - v1X;
      tlCtx.fillStyle = '#1B5E4A'; tlCtx.fillRect(v1X, 214, a1W, 52);
      tlCtx.strokeStyle = '#4ADE80'; tlCtx.strokeRect(v1X, 214, a1W, 52);
      const wf = (window.AUDIO_DATA && window.AUDIO_DATA.waveform) ? window.AUDIO_DATA.waveform : [];
      const bStep = a1W / Math.max(1, wf.length);
      for (let b = 0; b < wf.length; b++) {
        const bh = Math.max(2, wf[b] * 40);
        tlCtx.fillStyle = '#6EE7B7';
        tlCtx.fillRect(v1X + b * bStep, 242 - bh * 0.5, Math.max(1.4, bStep - 1), bh);
      }
      tlCtx.fillStyle = 'rgba(10,30,24,0.82)'; tlCtx.fillRect(v1X + 4, 215, 275, 12);
      tlCtx.fillStyle = '#D1FAE5'; tlCtx.font = 'bold 8.3px Consolas';
      tlCtx.fillText('VO_ChiHang_Real_48kHz.wav [-14.2 LUFS]', v1X + 7, 224);

      // A2 & A3: Premiere Audio Ducking & SFX Clips
      tlCtx.fillStyle = '#164E63'; tlCtx.fillRect(v1X, 273, a1W, 38);
      tlCtx.strokeStyle = '#FACC15'; tlCtx.lineWidth = 1.5;
      tlCtx.beginPath();
      for (let i = 0; i <= 70; i++) {
        const dx = secToX((i / 70) * TOTAL_SEC);
        const ei = Math.min(TOTAL_FRAMES - 1, Math.floor((i / 70) * (TOTAL_FRAMES - 1)));
        const va = window.AUDIO_DATA ? window.AUDIO_DATA.env_l[ei] : 0.3;
        const dy = 285 + va * 14;
        if (i === 0) tlCtx.moveTo(dx, dy); else tlCtx.lineTo(dx, dy);
      }
      tlCtx.stroke();

      for (const st of [0.2, 1.5, 3.2, 5.0, 7.1, 9.2, 11.2, 13.5, 16.0, 18.4, 20.8]) {
        const sx = secToX(st);
        tlCtx.fillStyle = '#0D9488'; tlCtx.fillRect(sx, 319, 36, 34);
        tlCtx.strokeStyle = '#5EEAD4'; tlCtx.strokeRect(sx, 319, 36, 34);
        tlCtx.fillStyle = '#FFF'; tlCtx.font = '7.8px Consolas'; tlCtx.fillText('SFX', sx + 5, 339);
      }
    } else {
      // ======== AFTER EFFECTS 2026 LAYER STACK & KEYFRAME DOPE SHEET ========
      const aeLayers = [
        { idx: 1, name: 'Null_3D_Camera_Orbit',   col: '#E11D48', s: 0.0, e: 21.0, kfs: [0.5, 4.8, 9.6, 14.2, 19.5] },
        { idx: 2, name: 'HTPM_Gold_Vector.ai',    col: '#D97706', s: 0.2, e: 20.9, kfs: [0.4, 2.2, 5.2, 11.4, 16.2] },
        { idx: 3, name: 'SP_5SanPham_Cutouts.psd',col: '#0284C7', s: 0.8, e: 20.9, kfs: [1.0, 5.0, 8.4, 13.8, 18.0] },
        { idx: 4, name: 'Card_NoiTiet_Glass_UI',  col: '#9333EA', s: 4.5, e: 16.5, kfs: [4.7, 6.2, 11.2, 15.8] },
        { idx: 5, name: 'Deep_Glow_Adjustment',   col: '#DB2777', s: 0.0, e: 21.0, kfs: [2.0, 7.5, 14.6, 20.0] },
        { idx: 6, name: 'ChiHang_RotoBrush3.mov', col: '#059669', s: 0.0, e: 21.0, kfs: [0.0, 5.0, 11.2, 16.0, 20.9] },
        { idx: 7, name: 'VO_ChiHang_Master.wav',  col: '#0D9488', s: 0.0, e: 21.3, kfs: [20.9] }
      ];
      for (let r = 0; r < aeLayers.length; r++) {
        const ly = 30 + r * 48;
        const L = aeLayers[r];
        tlCtx.fillStyle = r % 2 === 0 ? '#1E1E24' : '#18181D';
        tlCtx.fillRect(0, ly, W, 44);
        // Color label swatch + Layer Name + AE switches ([fx] [M] [3D])
        tlCtx.fillStyle = L.col;
        tlCtx.fillRect(4, ly + 8, 8, 28);
        tlCtx.fillStyle = '#E4E4E7'; tlCtx.font = 'bold 8.5px Consolas';
        tlCtx.fillText(`${L.idx} ${L.name.slice(0, 14)}`, 15, ly + 25);

        const lx = secToX(L.s), lw = secToX(L.e) - lx;
        tlCtx.fillStyle = L.col;
        tlCtx.globalAlpha = 0.72;
        tlCtx.fillRect(lx, ly + 7, lw, 30);
        tlCtx.globalAlpha = 1.0;
        tlCtx.strokeStyle = '#FFFFFF'; tlCtx.lineWidth = 0.8;
        tlCtx.strokeRect(lx, ly + 7, lw, 30);
        tlCtx.fillStyle = '#FFFFFF'; tlCtx.font = 'bold 8.8px "Segoe UI"';
        tlCtx.fillText(`${L.name}  [Motion Blur • 3D Layer]`, lx + 8, ly + 25);

        // Gold Easy-Ease Keyframe Diamonds along AE Layer Bar
        for (const kf of L.kfs) {
          const kx = secToX(kf), ky = ly + 22;
          tlCtx.save();
          tlCtx.translate(kx, ky);
          tlCtx.rotate(Math.PI / 4);
          tlCtx.fillStyle = '#FACC15';
          tlCtx.fillRect(-4, -4, 8, 8);
          tlCtx.strokeStyle = '#111'; tlCtx.lineWidth = 1;
          tlCtx.strokeRect(-4, -4, 8, 8);
          tlCtx.restore();
        }
      }
    }

    // Active Marquee Selection Boxes
    for (const mq of activeMarquees) {
      const rx = Math.min(mq.x0, mq.x1);
      const ry = Math.min(mq.y0, mq.y1) - 1522;
      const rw = Math.abs(mq.x1 - mq.x0);
      const rh = Math.abs(mq.y1 - mq.y0);
      if (ry > 20 && ry < H) {
        tlCtx.fillStyle = 'rgba(75, 156, 255, 0.18)';
        tlCtx.fillRect(rx, ry, rw, rh);
        tlCtx.strokeStyle = '#4B9CFF'; tlCtx.lineWidth = 1.2;
        tlCtx.strokeRect(rx, ry, rw, rh);
      }
    }

    // Adobe Blue/Red CTI Playhead
    const phX = secToX(t);
    tlCtx.strokeStyle = aeMode ? '#EF4444' : '#4B9CFF';
    tlCtx.lineWidth = 2;
    tlCtx.beginPath(); tlCtx.moveTo(phX, 8); tlCtx.lineTo(phX, H); tlCtx.stroke();
    tlCtx.fillStyle = aeMode ? '#EF4444' : '#4B9CFF';
    tlCtx.beginPath();
    tlCtx.moveTo(phX - 6, 3); tlCtx.lineTo(phX + 6, 3);
    tlCtx.lineTo(phX + 6, 12); tlCtx.lineTo(phX, 18); tlCtx.lineTo(phX - 6, 12);
    tlCtx.closePath(); tlCtx.fill();
  }

  // ==================== 7. LUMETRI SCOPES ====================
  const sc1 = document.getElementById('sc-1').getContext('2d');
  const sc2 = document.getElementById('sc-2').getContext('2d');
  const sc3 = document.getElementById('sc-3').getContext('2d');

  function drawScopes(t, vAmp) {
    sc1.fillStyle = '#080808'; sc1.fillRect(0, 0, 68, 135);
    sc1.strokeStyle = 'rgba(74, 222, 128, 0.7)'; sc1.beginPath();
    for (let x = 0; x < 68; x += 2) {
      const y = 70 + Math.sin(x * 0.22 + t * 5) * 24 + Math.cos(x * 0.5 - t * 3) * 14 * (0.6 + vAmp);
      if (x === 0) sc1.moveTo(x, y); else sc1.lineTo(x, y);
    }
    sc1.stroke();

    sc2.fillStyle = '#080808'; sc2.fillRect(0, 0, 68, 135);
    const cols = ['rgba(248,113,113,0.75)', 'rgba(74,222,128,0.75)', 'rgba(96,165,250,0.75)'];
    for (let c = 0; c < 3; c++) {
      sc2.fillStyle = cols[c];
      for (let i = 0; i < 9; i++) {
        const bh = 26 + Math.abs(Math.sin(t * 4 + c * 1.7 + i * 0.6)) * 65;
        sc2.fillRect(c * 22 + 3 + i * 2, 120 - bh, 1.5, bh);
      }
    }

    sc3.fillStyle = '#080808'; sc3.fillRect(0, 0, 68, 135);
    sc3.strokeStyle = '#27272A'; sc3.beginPath(); sc3.arc(34, 74, 26, 0, Math.PI * 2); sc3.stroke();
    sc3.strokeStyle = 'rgba(251, 191, 36, 0.7)';
    sc3.beginPath(); sc3.moveTo(34, 74); sc3.lineTo(20, 50); sc3.stroke();
    sc3.fillStyle = 'rgba(253, 186, 116, 0.6)';
    for (let k = 0; k < 14; k++) {
      const a = -2.1 + Math.sin(t * 3 + k) * 0.26, r = 6 + (k / 14) * 16;
      sc3.fillRect(34 + Math.cos(a) * r, 74 + Math.sin(a) * r, 2, 2);
    }
  }

  // ==================== 8. 72 SIMULTANEOUS SWARM CURSORS ====================
  const NUM_CURSORS = 72;
  const cursors = [];

  const badgeMap = {
    0:  { label: 'Ps-Retouch', color: '#0284C7' },
    3:  { label: 'Ps-Mask',    color: '#2563EB' },
    6:  { label: 'Ai-Vector',  color: '#D97706' },
    9:  { label: 'CMS-Auto',   color: '#059669' },
    12: { label: 'TikTok-Bot', color: '#DB2777' },
    15: { label: 'Gemini-Pro', color: '#4F46E5' },
    18: { label: 'JSX-Code',   color: '#0D9488' },
    21: { label: 'Me-Queue',   color: '#7C3AED' },
    25: { label: 'DynLink',    color: '#9333EA' }
  };

  function pickTarget(group, rng) {
    let x, y, ctype = 'arrow';
    if (group === 'top') {
      x = 26 + rng() * 1028;
      y = 48 + rng() * 868;
      ctype = ['arrow', 'hand', 'ibeam', 'cross'][Math.floor(rng() * 4)];
    } else if (group === 'bridge') {
      if (rng() < 0.45) { x = 60 + rng() * 940; y = 120 + rng() * 720; ctype = 'hand'; }
      else { x = 130 + rng() * 920; y = 1545 + rng() * 340; ctype = 'hand'; }
    } else if (group === 'bin') {
      x = 18 + rng() * 244; y = 1005 + rng() * 485; ctype = 'hand';
    } else if (group === 'insp') {
      x = 780 + rng() * 282; y = 995 + rng() * 490;
      ctype = rng() < 0.65 ? 'ew-resize' : 'hand';
    } else if (group === 'monSafe') {
      // Strictly outside Chị Hằng's face (x: 405..610, y: 1020..1330)!
      if (rng() < 0.5) { x = rng() < 0.5 ? (292 + rng()*72) : (646 + rng()*95); y = 1010 + rng()*460; }
      else { x = 385 + rng() * 240; y = 1472 + rng() * 24; }
      ctype = 'hand';
    } else {
      x = 118 + rng() * 946; y = 1540 + rng() * 365;
      ctype = ['arrow', 'ew-resize', 'hand'][Math.floor(rng() * 3)];
    }
    return { x, y, ctype };
  }

  for (let i = 0; i < NUM_CURSORS; i++) {
    const rng = mulberry32(9901 + i * 6151);
    const group = i < 28 ? 'top'
                : i < 33 ? 'bridge'
                : i < 39 ? 'bin'
                : i < 42 ? 'monSafe'
                : i < 51 ? 'insp'
                : 'tl';
    const waypoints = [];
    let f = -Math.floor(rng() * 30);
    let prev = pickTarget(group, rng);

    while (f < TOTAL_FRAMES + 90) {
      const next = pickTarget(group, rng);
      const mDur = Math.floor(16 + rng() * 26);
      const hDur = Math.floor(7 + rng() * 18);
      const isMarquee = group === 'tl' && rng() < 0.24;
      waypoints.push({
        f0: f, f1: f + mDur, f2: f + mDur + hDur,
        x0: prev.x, y0: prev.y, x1: next.x, y1: next.y,
        arc: (rng() - 0.5) * 46,
        ctype: next.ctype,
        isMarquee,
        dx: isMarquee ? (40 + rng() * 90) * (rng() < 0.5 ? 1 : -1) : (group === 'insp' ? (rng()-0.5)*34 : 0),
        dy: isMarquee ? (18 + rng() * 30) : 0,
        carry: group === 'bridge' && next.y > 1400,
        thIdx: i % dragImgs.length
      });
      f += mDur + hDur;
      prev = { x: next.x, y: next.y, ctype: next.ctype };
    }
    cursors.push({ id: i, badge: null, waypoints });
  }

  function drawCursor(ctx, x, y, scale, ctype, badge) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    ctx.shadowColor = 'rgba(0,0,0,0.58)';
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
      // Photoshop / AE Precision Crosshair
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
      ctx.shadowBlur = 2;
      ctx.font = 'bold 8.5px "Segoe UI", sans-serif';
      const tw = ctx.measureText(badge.label).width;
      ctx.fillStyle = badge.color;
      ctx.beginPath(); ctx.roundRect(11, 13, tw + 8, 13, 4); ctx.fill();
      ctx.fillStyle = '#FFF';
      ctx.fillText(badge.label, 15, 22.6);
    }
    ctx.restore();
  }

  // ==================== 9. MASTER FRAME RENDERER ====================
  const curCvs = document.getElementById('cursor-canvas');
  const curCtx = curCvs.getContext('2d');
  const previewImg = document.getElementById('chihang-video-img');
  const cmsStr = '5 sản phẩm cần biết cho phụ nữ sau tuổi 25! Bí quyết chăm sóc chủ động cùng Chị Hằng — Hằng Thu Pharma';

  window.renderFrame = async function (frameIdx) {
    const f = Math.max(0, Math.min(TOTAL_FRAMES - 1, frameIdx));
    const t = f / FPS;
    const aeMode = isAfterEffectsMode(t);

    // 1. Rapid Top-Desktop Window Jumping + Alt+Tab HUD!
    const ls = getLayoutState(f);
    for (const k of WIN_IDS) {
      const el = document.getElementById(`win-${k}`);
      const r = ls.rects[k];
      el.style.left = `${r.x.toFixed(1)}px`;
      el.style.top = `${r.y.toFixed(1)}px`;
      el.style.width = `${r.w.toFixed(1)}px`;
      el.style.height = `${r.h.toFixed(1)}px`;
      el.style.zIndex = String(r.z);
      el.style.transform = `scale(${r.sc.toFixed(3)})`;
      el.className = k === ls.focus ? 'app-win focused' : 'app-win';
    }

    // Highlight active Top Dock app (including Pr/Ae bottom mode!)
    for (const dk of ['dk-ps', 'dk-pr', 'dk-ae', 'dk-ai', 'dk-web', 'dk-ag']) {
      const on = (dk === ls.dock) || (dk === 'dk-ae' && aeMode) || (dk === 'dk-pr' && !aeMode);
      document.getElementById(dk).className = on ? 'dock-pill active' : 'dock-pill';
    }
    document.getElementById('sys-ops').textContent = `${178 + Math.floor(Math.sin(t * 5) * 24 + 24)} ops/s`;

    // Alt+Tab Switcher Overlay flash right on window jump
    const hud = document.getElementById('alt-tab-hud');
    if (ls.showAltTab) {
      hud.style.display = 'flex';
      for (let a = 0; a < 6; a++) {
        document.getElementById(`at-${a}`).className = a === ls.atIdx ? 'at-item sel' : 'at-item';
      }
    } else {
      hud.style.display = 'none';
    }

    // 2. Render Photoshop, Illustrator, CMS, Gemini, IDE & Swarm Contents
    drawPhotoshop(f, t);
    drawIllustrator(t);

    const typed = Math.floor((t * 30) % (cmsStr.length + 16));
    document.getElementById('cms-type').textContent = cmsStr.slice(0, Math.min(cmsStr.length, typed)) + (f % 24 < 12 ? '▋' : '');
    for (let c = 0; c < 3; c++) {
      document.getElementById(`cmsc-${c}`).className = c === (Math.floor(t * 1.8) % 3) ? 'cms-card sel' : 'cms-card';
    }
    document.getElementById('gem-acc').textContent = `u/${Math.floor(t / 3) % 5} ACTIVE`;
    for (let g = 0; g < 4; g++) {
      document.getElementById(`gf-${g}`).style.width = `${Math.min(100, Math.floor(65 + ((t * 25 + g * 17) % 45)))}%`;
    }

    // ExtendScript .jsx IDE
    const curL = Math.floor(t * 4) % jsxLines.length;
    document.getElementById('ide-lines').innerHTML = jsxLines.map((row, idx) =>
      `<div class="cl ${row.cls}${idx === curL ? ' cur' : ''}"><span style="color:#475569;margin-right:7px;">${idx + 1}</span>${row.h}</div>`
    ).join('');
    document.getElementById('ide-stat').textContent = `+${310 + Math.floor(t * 5)} -14`;

    // Swarm + Media Encoder Queue
    const stepS = Math.floor(t * 3.0);
    let sHtml = '';
    for (let r = 0; r < 8; r++) {
      const it = swarmLogs[(stepS + r) % swarmLogs.length];
      sHtml += `<div class="srow${r === 7 ? ' hot' : ''}"><span><b style="color:#67E8F9">[${it.app}]</b> ${it.txt}</span><span style="color:#34D399;font-weight:700;">${it.st}</span></div>`;
    }
    document.getElementById('swarm-rows').innerHTML = sHtml;
    document.getElementById('sw-cnt').textContent = `${520 + Math.floor(t * 9)} tasks ✓`;

    // 3. Switch Bottom NLE Dynamically between Premiere Pro (Pr) & After Effects (Ae)!
    const appBadge = document.getElementById('nle-app-badge');
    const appName = document.getElementById('nle-app-name');
    if (aeMode) {
      appBadge.className = 'cc-badge cc-ae'; appBadge.textContent = 'Ae';
      appName.textContent = 'Adobe After Effects 2026';
      document.getElementById('mon-title').textContent = 'Composition: ChiHang_Master_9x16 [Dynamic Link]';
      document.getElementById('tl-mode-status').textContent = 'Ae Layer Stack • Easy-Ease Graph Active';
      document.getElementById('tl-mode-status').style.color = '#CF96FD';
      document.getElementById('ae-3d-gizmo').style.display = 'block';
    } else {
      appBadge.className = 'cc-badge cc-pr'; appBadge.textContent = 'Pr';
      appName.textContent = 'Adobe Premiere Pro 2026';
      document.getElementById('mon-title').textContent = 'Program: Sequence 01 • Chị Hằng (Video Thực)';
      document.getElementById('tl-mode-status').textContent = 'Pr Multi-Track Sequence • Mercury CUDA';
      document.getElementById('tl-mode-status').style.color = '#9999FF';
      document.getElementById('ae-3d-gizmo').style.display = 'none';
    }

    const activeWs = aeMode ? (t % 2 < 1 ? 2 : 3) : Math.floor(t * 1.2) % 2;
    for (let w = 0; w < 5; w++) {
      document.getElementById(`wstab-${w}`).className = w === activeWs ? (aeMode ? 'ws-tab active-ae' : 'ws-tab active-pr') : 'ws-tab';
    }
    for (let b = 0; b < 8; b++) {
      document.getElementById(`bin-${b}`).className = b === (Math.floor(t * 2.0) % 8) ? 'bin-item sel' : 'bin-item';
    }

    // Sliders, Color Wheels & AE Graph Editor
    const sVals = [
      [100, 105, v => `${v.toFixed(1)}%`],
      [948, 972, v => `${v.toFixed(1)}`],
      [2.5, 6.2, v => `+${v.toFixed(1)}`],
      [0.18,0.48,v => `+${v.toFixed(2)}`],
      [1.8, 3.1, v => `+${v.toFixed(1)}dB`]
    ];
    for (let s = 0; s < 5; s++) {
      const u = 0.5 + 0.38 * Math.sin(t * 2.6 + s * 1.1);
      const val = sVals[s][0] + u * (sVals[s][1] - sVals[s][0]);
      document.getElementById(`sl${s}f`).style.width = `${(u * 100).toFixed(1)}%`;
      document.getElementById(`sl${s}t`).style.left = `${(u * 100).toFixed(1)}%`;
      document.getElementById(`sl${s}v`).textContent = sVals[s][2](val);
    }
    for (let c = 0; c < 3; c++) {
      document.getElementById(`cwd${c}`).style.transform =
        `translate(calc(-50% + ${(Math.sin(t*2.3+c*2)*5).toFixed(1)}px), calc(-50% + ${(Math.cos(t*1.8+c)*5).toFixed(1)}px))`;
    }
    drawAeGraphEditor(t);

    // 4. Program / Composition Monitor: 100% Real Chị Hằng Video + Synced VU Meters
    const secI = Math.floor(t), frmI = Math.floor((t - secI) * 60);
    document.getElementById('mon-tc').textContent = `00:00:${String(secI).padStart(2, '0')}:${String(frmI).padStart(2, '0')}`;
    document.getElementById('mon-mode-pill').textContent =
      t >= 20.95 ? '✓ RENDER COMPLETE • 1080P 60FPS'
      : aeMode   ? 'Ae • ROTO & 3D COMP CHỊ HẰNG'
                 : 'Pr • CAM A CHỊ HẰNG (REAL)';

    const wipe = document.getElementById('pr-lut-wipe');
    if (!aeMode && ((t > 2.2 && t < 2.9) || (t > 11.4 && t < 12.1))) {
      const lu = ((t < 6 ? t - 2.2 : t - 11.4) / 0.7);
      wipe.style.display = 'block';
      wipe.style.width = `${(Math.sin(lu * Math.PI) * 68).toFixed(1)}%`;
    } else {
      wipe.style.display = 'none';
    }

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

    // 5. Render All 72 Cursors + Ghost Drag Assets + Marquees
    curCtx.clearRect(0, 0, 1080, 1920);
    const activeMarquees = [];

    for (const c of cursors) {
      let wp = null;
      for (let k = 0; k < c.waypoints.length; k++) {
        const w = c.waypoints[k];
        if (f >= w.f0 && f < w.f2) { wp = w; break; }
      }
      if (!wp) continue;

      let cx, cy, sc = 1.0;
      if (f < wp.f1) {
        const u = minJerk((f - wp.f0) / Math.max(1, wp.f1 - wp.f0));
        const mx = (wp.x0 + wp.x1) * 0.5 - (wp.y1 - wp.y0) * 0.12 + wp.arc;
        const my = (wp.y0 + wp.y1) * 0.5 + (wp.x1 - wp.x0) * 0.12;
        const inv = 1 - u;
        cx = inv * inv * wp.x0 + 2 * inv * u * mx + u * u * wp.x1;
        cy = inv * inv * wp.y0 + 2 * inv * u * my + u * u * wp.y1;

        if (wp.carry) {
          const gim = dragImgs[wp.thIdx];
          if (gim && gim.complete && gim.naturalWidth > 0) {
            curCtx.save();
            curCtx.globalAlpha = 0.85;
            curCtx.drawImage(gim, cx + 8, cy + 8, 66, 42);
            curCtx.strokeStyle = '#31A8FF'; curCtx.lineWidth = 1.5;
            curCtx.strokeRect(cx + 8, cy + 8, 66, 42);
            curCtx.restore();
          }
        }
      } else {
        const hu = minJerk((f - wp.f1) / Math.max(1, wp.f2 - wp.f1));
        cx = wp.x1 + wp.dx * hu;
        cy = wp.y1 + wp.dy * hu;
        const hf = f - wp.f1;
        if (hf < 6) sc = 0.85;
        if (hf < 11) {
          curCtx.save();
          curCtx.strokeStyle = `rgba(96, 165, 250, ${(1 - hf / 11) * 0.65})`;
          curCtx.lineWidth = 1.4;
          curCtx.beginPath(); curCtx.arc(cx, cy, 3 + hf * 1.35, 0, Math.PI * 2); curCtx.stroke();
          curCtx.restore();
        }
        if (wp.isMarquee) activeMarquees.push({ x0: wp.x1, y0: wp.y1, x1: cx, y1: cy });
      }
      drawCursor(curCtx, cx, cy, sc, wp.ctype, c.badge);
    }

    // 6. Draw Premiere Pro / After Effects Timeline
    drawTimeline(f, t, aeMode, activeMarquees);
  };
})();
