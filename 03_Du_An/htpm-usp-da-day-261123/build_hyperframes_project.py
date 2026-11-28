"""
Phase 4-6 (V2 Upgrade theo góp ý Editor):
1. Viết hoa 100% chữ cái đầu câu / đầu dòng trên MỌI Tiêu đề 3D, Thẻ Slide và Phụ đề (bao gồm cả "Chị mới...", "Chị chọn...").
2. Face-Safe & Box-Safe tuyệt đối 100% (0% chữ đè lên trán/mắt/mặt mẫu chị Hằng ở các cảnh cận S02, S03, S04, S06, S07, S08, S12
   và 0% chạm hộp DẠ DÀY HT ở S08, S09, S11, S13 — đã đối chiếu từng pixel trên ruler_13shots.jpg).
3. Chèn 6 Lớp Phủ Slide Động (Frosted Liquid-Glass Slide Cards / Checklist / Staggered Botanical Pills) trượt mượt có trọng lượng
   vật lý (Slide + Overshoot + Bidirectional Blur-Focus) kèm Tactile Micro-SFX đúng điểm chạm.
4. Tuân thủ 100% Vùng Trắng An Toàn TikTok x Reels 9:16 (safe_zone_9x16.py):
   Y in [255..1540], X in [58..1020] (Y<860) và X in [58..880] (Y>=860).
"""
import json
from pathlib import Path

PROJ_DIR = Path(r"d:\AI\full studio\output\htpm-usp-da-day-261123")
VO_MANIFEST_PATH = PROJ_DIR / "06_Audio_Voiceover" / "vo_manifest.json"
HF_DIR = PROJ_DIR / "07_HyperFrames_Project"
COMP_DIR = HF_DIR / "compositions"

COLOR_GRADE_WARM = (
    '{&quot;preset&quot;:null,&quot;intensity&quot;:1,&quot;adjust&quot;:{&quot;exposure&quot;:0.04,&quot;contrast&quot;:0.08,'
    '&quot;highlights&quot;:0.04,&quot;shadows&quot;:0.05,&quot;whites&quot;:0.06,&quot;blacks&quot;:0,&quot;temperature&quot;:0.03,'
    '&quot;tint&quot;:0.01,&quot;vibrance&quot;:0.12,&quot;saturation&quot;:0.05},&quot;details&quot;:{&quot;vignette&quot;:0.04,'
    '&quot;vignetteMidpoint&quot;:0.5,&quot;vignetteRoundness&quot;:0,&quot;vignetteFeather&quot;:0.65,&quot;grain&quot;:0,'
    '&quot;grainSize&quot;:0.25,&quot;grainRoughness&quot;:0.5},&quot;effects&quot;:{&quot;blur&quot;:0,&quot;pixelate&quot;:0,'
    '&quot;chromaBleed&quot;:0,&quot;tapeDamage&quot;:0,&quot;tapeTracking&quot;:0,&quot;tapeNoise&quot;:1,&quot;tapeSpeed&quot;:0.5,'
    '&quot;filmArtifacts&quot;:0,&quot;halftone&quot;:0,&quot;halftoneSize&quot;:0,&quot;twoInkPrint&quot;:0,&quot;twoInkPrintSize&quot;:0,'
    '&quot;ascii&quot;:0,&quot;asciiSize&quot;:0.065,&quot;asciiInvert&quot;:0,&quot;asciiStyle&quot;:0,&quot;asciiColor&quot;:1,'
    '&quot;asciiRotation&quot;:0,&quot;dither&quot;:0,&quot;ditherSize&quot;:0,&quot;bloom&quot;:0,&quot;bloomRadius&quot;:8,'
    '&quot;monoScreen&quot;:0,&quot;monoScreenSize&quot;:0,&quot;monoScreenAngle&quot;:0,&quot;monoScreenSpread&quot;:0,'
    '&quot;monoScreenShape&quot;:0,&quot;monoScreenInvert&quot;:0,&quot;scanlines&quot;:0,&quot;scanlineCount&quot;:0,'
    '&quot;scanlineSoftness&quot;:0,&quot;chromaticAberration&quot;:0,&quot;chromaticAngle&quot;:0,&quot;crtCurvature&quot;:0,'
    '&quot;digitalGlitch&quot;:0,&quot;digitalGlitchColorSplit&quot;:0,&quot;digitalGlitchLineTear&quot;:0,'
    '&quot;digitalGlitchPixelate&quot;:0,&quot;digitalGlitchBlockAmount&quot;:0,&quot;digitalGlitchBlockDisplacement&quot;:0,'
    '&quot;digitalGlitchBlockOpacity&quot;:0,&quot;digitalGlitchSpeed&quot;:0,&quot;engraving&quot;:0,&quot;engravingSpacing&quot;:0.41,'
    '&quot;engravingMinThickness&quot;:0.2,&quot;engravingMaxThickness&quot;:0.45,&quot;engravingAngle&quot;:0.25,'
    '&quot;engravingContrast&quot;:0.46,&quot;engravingSharpness&quot;:0.59,&quot;engravingWave&quot;:0.2,'
    '&quot;engravingWaveFrequency&quot;:0.22,&quot;crosshatch&quot;:0,&quot;crosshatchSpacing&quot;:0.28,'
    '&quot;crosshatchThickness&quot;:0.25,&quot;crosshatchAngle&quot;:0.25,&quot;crosshatchContrast&quot;:0.33,'
    '&quot;crosshatchEdges&quot;:0.5,&quot;crosshatchLineWeight&quot;:0,&quot;crosshatchWave&quot;:0.33,'
    '&quot;crosshatchWaveFrequency&quot;:0.22,&quot;kuwahara&quot;:0,&quot;kuwaharaRadius&quot;:0.14,&quot;kuwaharaSharpness&quot;:0.31,'
    '&quot;kuwaharaSaturation&quot;:0.5},&quot;lut&quot;:null,&quot;colorSpace&quot;:&quot;rec709&quot;}'
)

VO_FX_CHAIN = (
    '{&quot;version&quot;:1,&quot;nodes&quot;:['
    '{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;vhp&quot;,&quot;label&quot;:&quot;Clean rumble&quot;,&quot;params&quot;:{&quot;frequency&quot;:85}},'
    '{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;vlow&quot;,&quot;label&quot;:&quot;Warmth balance&quot;,&quot;params&quot;:{&quot;frequency&quot;:210,&quot;gain&quot;:-1.6,&quot;q&quot;:1.1}},'
    '{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;vpres&quot;,&quot;label&quot;:&quot;Broadcast clarity&quot;,&quot;params&quot;:{&quot;frequency&quot;:3100,&quot;gain&quot;:1.8,&quot;q&quot;:1.0}},'
    '{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;vlim&quot;,&quot;params&quot;:{&quot;limit&quot;:-1.0}}]}'
)

SHARED_TYPO_CSS = """
    @font-face { font-family: "FrauncesVN"; src: url("assets/fonts/Fraunces-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }
    @font-face { font-family: "PlayfairVN"; src: url("assets/fonts/PlayfairDisplay-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }
    @font-face { font-family: "PlayfairVNItalic"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; font-display: block; }
    @font-face { font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }
    @font-face { font-family: "BeVietnamSemiVN"; src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype"); font-weight: 600; font-display: block; }
    @font-face { font-family: "DancingVN"; src: url("assets/fonts/DancingScript-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }

    #root {
      position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: #072614; font-family: "BeVietnamVN", sans-serif;
    }
    .cam-rig { position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 50%; }
    .bg-video { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }
    .float-stage {
      position: absolute; inset: 0; width: 1080px; height: 1920px;
      pointer-events: none; z-index: 9;
    }
    .svg-typo { width: 100%; height: 100%; overflow: visible; display: block; }
    .brand-contour {
      font-family: "PlayfairVN", Georgia, serif;
      font-weight: 800; paint-order: stroke fill;
      stroke: #ffffff; stroke-width: 14px; stroke-linejoin: round; stroke-linecap: round;
      letter-spacing: 0.01em;
    }
    .brand-ht {
      font-family: "PlayfairVNItalic", Georgia, serif;
      font-style: italic; font-weight: 700; paint-order: stroke fill;
      stroke: #ffffff; stroke-width: 14px; stroke-linejoin: round; stroke-linecap: round;
    }
    .script-sub {
      font-family: "DancingVN", cursive;
      font-weight: 700; paint-order: stroke fill;
      stroke: rgba(255, 255, 255, 0.95); stroke-width: 8px; stroke-linejoin: round;
    }
    .upper-claim {
      font-family: "BeVietnamVN", sans-serif;
      font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;
      paint-order: stroke fill;
      stroke: rgba(255, 255, 255, 0.96); stroke-width: 9px; stroke-linejoin: round;
    }
    .satin-hero {
      font-family: "FrauncesVN", "PlayfairVN", Georgia, serif;
      font-weight: 900; letter-spacing: -0.01em;
      paint-order: stroke fill;
      stroke: rgba(255, 255, 255, 0.92); stroke-width: 10px; stroke-linejoin: round;
    }
    .cta-open {
      font-family: "BeVietnamVN", sans-serif;
      font-weight: 800; letter-spacing: 0.01em;
      paint-order: stroke fill;
      stroke: #ffffff; stroke-width: 11px; stroke-linejoin: round; stroke-linecap: round;
    }

    /* Frosted Liquid-Glass Slide Overlay System (Safe Zone X in [64..865], Face-Safe 100%) */
    .slide-card {
      position: absolute;
      left: 64px;
      border-radius: 26px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.94) 0%, rgba(240, 252, 244, 0.90) 100%);
      border: 2.5px solid rgba(22, 148, 62, 0.34);
      box-shadow: 0 14px 34px rgba(5, 42, 18, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.95);
      padding: 18px 24px;
      z-index: 10;
      pointer-events: none;
    }
    .slide-card-header {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(90deg, #0B6E2B 0%, #179440 100%);
      color: #ffffff;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 19px;
      font-weight: 800;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      padding: 6px 16px;
      border-radius: 999px;
      margin-bottom: 12px;
      box-shadow: 0 4px 12px rgba(11, 110, 43, 0.28);
    }
    .slide-row {
      display: flex;
      align-items: center;
      gap: 12px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: #083D19;
      padding: 6px 0;
      line-height: 1.28;
    }
    .slide-badge-dot {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 17px;
      font-weight: 800;
      flex-shrink: 0;
      background: #E4F8EA;
      color: #0D7A31;
      border: 2px solid #8BE0A4;
    }
    .slide-badge-warn {
      background: #FFF1DF;
      color: #C95B00;
      border: 2px solid #F7BA77;
    }
    .slide-pill-stack {
      position: absolute;
      left: 64px;
      display: flex;
      flex-direction: column;
      gap: 11px;
      z-index: 10;
      pointer-events: none;
    }
    .slide-pill {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 247, 236, 0.92) 100%);
      border-left: 7px solid #E07A00;
      border-top: 1.5px solid rgba(255, 255, 255, 0.95);
      border-right: 1.5px solid rgba(224, 122, 0, 0.25);
      border-bottom: 1.5px solid rgba(224, 122, 0, 0.25);
      border-radius: 18px;
      padding: 11px 22px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: #4A1E00;
      box-shadow: 0 10px 24px rgba(38, 18, 4, 0.20);
      width: fit-content;
      max-width: 780px;
    }
    .slide-pill-emerald {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(236, 253, 241, 0.93) 100%);
      border-left: 7px solid #0E8A38;
      border-right: 1.5px solid rgba(14, 138, 56, 0.28);
      border-bottom: 1.5px solid rgba(14, 138, 56, 0.28);
      color: #063D18;
    }
"""

def svg_defs(prefix: str, light_x: int = 240) -> str:
    return f"""
      <defs>
        <linearGradient id="{prefix}-emerald-fill" x1="0%" y1="0%" x2="14%" y2="100%">
          <stop offset="0%" stop-color="#EBFFF1" />
          <stop offset="24%" stop-color="#58DF7E" />
          <stop offset="52%" stop-color="#0E8A38" />
          <stop offset="78%" stop-color="#6CEB90" />
          <stop offset="100%" stop-color="#064D1E" />
        </linearGradient>

        <linearGradient id="{prefix}-gold-fill" x1="0%" y1="0%" x2="12%" y2="100%">
          <stop offset="0%" stop-color="#FFFDF2" />
          <stop offset="25%" stop-color="#FFE173" />
          <stop offset="52%" stop-color="#E28708" />
          <stop offset="78%" stop-color="#FFEC9E" />
          <stop offset="100%" stop-color="#8C4800" />
        </linearGradient>

        <linearGradient id="{prefix}-brand-deep" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#0D6E2C" />
          <stop offset="55%" stop-color="#074B1D" />
          <stop offset="100%" stop-color="#042E11" />
        </linearGradient>

        <linearGradient id="{prefix}-ht-accent" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#F59B14" />
          <stop offset="55%" stop-color="#D46B00" />
          <stop offset="100%" stop-color="#8C3E00" />
        </linearGradient>

        <filter id="{prefix}-silk-3d" x="-16%" y="-24%" width="132%" height="152%" color-interpolation-filters="sRGB">
          <feMorphology in="SourceAlpha" operator="dilate" radius="1.1" result="extrudeAlpha" />
          <feOffset in="extrudeAlpha" dx="1.2" dy="3.0" result="extrudeShift" />
          <feFlood flood-color="#053816" flood-opacity="0.78" result="extrudeColor" />
          <feComposite in="extrudeColor" in2="extrudeShift" operator="in" result="extrudeRim" />
          <feDropShadow in="SourceAlpha" dx="0" dy="6" stdDeviation="6" flood-color="#04240E" flood-opacity="0.28" result="softShadow" />
          <feGaussianBlur in="SourceAlpha" stdDeviation="2.4" result="bevelBlur" />
          <feSpecularLighting in="bevelBlur" surfaceScale="7.5" specularConstant="1.45" specularExponent="24" lighting-color="#FFFFFF" result="specRaw">
            <fePointLight id="{prefix}-light" x="{light_x}" y="-110" z="240" />
          </feSpecularLighting>
          <feComposite in="specRaw" in2="SourceAlpha" operator="in" result="specClipped" />
          <feMerge>
            <feMergeNode in="softShadow" />
            <feMergeNode in="extrudeRim" />
            <feMergeNode in="SourceGraphic" />
            <feMergeNode in="specClipped" />
          </feMerge>
        </filter>

        <filter id="{prefix}-clean-lift" x="-14%" y="-22%" width="128%" height="148%">
          <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#04240E" flood-opacity="0.24" />
        </filter>
      </defs>
    """

def write_act1():
    # Global 0.00 - 12.75s:
    # - DD_S01 (0..2.50s): Hair starts at Y=500px -> Top 3D Hook at Y=308..415px is 100% ABOVE her head! Exits at 2.44s!
    # - DD_S02 (2.50..5.25s): Head at Y=160..700px -> ZERO top text! Slide Card #1 ("Nhịp ăn uống thất thường") slides in at Y=1065..1345px!
    # - DD_S03 (5.25..9.00s): Head at Y=120..680px -> ZERO top text! Slide Overlay #2 (3 Symptom Pills) slides in at Y=960..1225px!
    # - DD_S04 (9.00..12.75s): Head at Y=140..670px -> ZERO top text! Compact warm Slide Pill at Y=1255..1340px!
    html = f"""<template>
  <style>{SHARED_TYPO_CSS}</style>
  <div id="root" data-composition-id="act1-hook" data-width="1080" data-height="1920" data-start="0" data-duration="12.75">
    <div id="a1-rig-01" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a1-v01" class="clip bg-video" src="assets/videos/DD_S01.mp4" data-start="0" data-duration="2.5" data-media-start="0.2" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a1-rig-02" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a1-v02" class="clip bg-video" src="assets/videos/DD_S02.mp4" data-start="2.5" data-duration="2.75" data-media-start="0.2" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
    <div id="a1-rig-03" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a1-v03" class="clip bg-video" src="assets/videos/DD_S03.mp4" data-start="5.25" data-duration="3.75" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a1-rig-04" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a1-v04" class="clip bg-video" src="assets/videos/DD_S04.mp4" data-start="9" data-duration="3.75" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>

    <!-- Shot 1 ONLY (0.12 - 2.44s): Top 3D Hook in open sunlit window ABOVE head (Y=308..415px < 490px!) -->
    <div id="a1-t1-clip" class="clip float-stage" data-start="0.12" data-duration="2.32" data-track-index="3" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a1t1")}
        <g id="a1-t1-badge" filter="url(#a1t1-clean-lift)">
          <text x="540" y="308" text-anchor="middle" class="upper-claim" font-size="28" fill="#0B6B29">SÁNG CÀ PHÊ · TRƯA KẸT HỌP</text>
        </g>
        <g id="a1-t1-hero">
          <text x="540" y="410" text-anchor="middle" class="satin-hero" font-size="88" fill="url(#a1t1-gold-fill)" filter="url(#a1t1-silk-3d)">Tối ăn bù?</text>
        </g>
      </svg>
    </div>

    <!-- SLIDE OVERLAY #1 (Shot 2: 2.52 - 5.15s): Frosted Slide Card in Lower-Left Face-Safe Zone (X=64..610, Y=1055..1345) -->
    <div id="a1-slide-meal" class="clip slide-card" style="top: 1058px; width: 548px;" data-start="2.52" data-duration="2.63" data-track-index="4" data-layout-ignore>
      <div class="slide-card-header">⏰ Nhịp ăn uống lệch chuẩn</div>
      <div id="a1-m1" class="slide-row"><span class="slide-badge-dot slide-badge-warn">1</span> Sáng: Uống cà phê vội</div>
      <div id="a1-m2" class="slide-row"><span class="slide-badge-dot slide-badge-warn">2</span> Trưa: Kẹt họp ăn qua loa</div>
      <div id="a1-m3" class="slide-row" style="color:#C95B00;"><span class="slide-badge-dot slide-badge-warn">3</span> Tối về: Ăn bù thật no!</div>
    </div>

    <!-- SLIDE OVERLAY #2 (Shot 3: 5.35 - 8.92s): 3 Staggered Symptom Slide Pills (X=64..540, Y=955..1215 — Clear of face & hand!) -->
    <div id="a1-slide-sym" class="clip slide-pill-stack" style="top: 958px;" data-start="5.35" data-duration="3.57" data-track-index="3" data-layout-ignore>
      <div id="a1-sp1" class="slide-pill"><span class="slide-badge-dot slide-badge-warn">!</span> Nóng rát vùng thượng vị</div>
      <div id="a1-sp2" class="slide-pill"><span class="slide-badge-dot slide-badge-warn">!</span> Ợ hơi · Đầy tức khó tiêu</div>
      <div id="a1-sp3" class="slide-pill"><span class="slide-badge-dot slide-badge-warn">!</span> Cảm giác buồn nôn</div>
    </div>

    <!-- Shot 4 (9.12 - 12.55s): Gentle Self-Care Pill below cup (X=64..620, Y=1255..1340 — 100% Face-Safe!) -->
    <div id="a1-slide-care" class="clip slide-pill-stack" style="top: 1256px;" data-start="9.12" data-duration="3.43" data-track-index="4" data-layout-ignore>
      <div id="a1-care-pill" class="slide-pill slide-pill-emerald"><span class="slide-badge-dot">♥</span> Chăm sóc &amp; thương lấy dạ dày mình</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a1-rig-01", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 2.50, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a1-rig-02", {{ scale: 1.04 }}, {{ scale: 1.00, duration: 2.75, ease: "none", immediateRender: false }}, 2.50)
      .fromTo("#a1-rig-03", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 3.75, ease: "none", immediateRender: false }}, 5.25)
      .fromTo("#a1-rig-04", {{ scale: 1.05 }}, {{ scale: 1.00, duration: 3.75, ease: "none", immediateRender: false }}, 9.00);

    // Shot 1 Top 3D Hook
    tl.fromTo("#a1-t1-badge", {{ opacity: 0, y: -12, scale: 0.93, filter: "blur(12px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.26, ease: "power3.out", immediateRender: false }}, 0.14)
      .fromTo("#a1-t1-hero", {{ opacity: 0, y: 16, scale: 0.93, filter: "blur(14px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "back.out(1.4)", immediateRender: false }}, 0.24)
      .fromTo("#a1t1-light", {{ attr: {{ x: 180 }} }}, {{ attr: {{ x: 900 }}, duration: 1.9, ease: "sine.inOut", immediateRender: false }}, 0.28)
      .to("#a1-t1-clip", {{ opacity: 0, filter: "blur(10px)", duration: 0.18, ease: "power2.in" }}, 2.24);

    // Slide Overlay #1 (Shot 2)
    tl.fromTo("#a1-slide-meal", {{ opacity: 0, x: -160, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.34, ease: "back.out(1.35)", immediateRender: false }}, 2.54)
      .fromTo("#a1-m1", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22, ease: "power2.out", immediateRender: false }}, 2.66)
      .fromTo("#a1-m2", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22, ease: "power2.out", immediateRender: false }}, 2.80)
      .fromTo("#a1-m3", {{ opacity: 0, x: -24, scale: 0.95 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.26, ease: "back.out(1.5)", immediateRender: false }}, 2.96)
      .to("#a1-slide-meal", {{ opacity: 0, x: -90, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 4.92);

    // Slide Overlay #2 (Shot 3 — Staggered Symptom Pills)
    tl.fromTo("#a1-sp1", {{ opacity: 0, x: -140, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.4)", immediateRender: false }}, 5.38)
      .fromTo("#a1-sp2", {{ opacity: 0, x: -140, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.4)", immediateRender: false }}, 6.10)
      .fromTo("#a1-sp3", {{ opacity: 0, x: -140, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.4)", immediateRender: false }}, 6.85)
      .to("#a1-slide-sym", {{ opacity: 0, x: -80, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 8.70);

    // Shot 4 Gentle Pill
    tl.fromTo("#a1-care-pill", {{ opacity: 0, x: -130, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.32, ease: "back.out(1.35)", immediateRender: false }}, 9.15)
      .to("#a1-slide-care", {{ opacity: 0, filter: "blur(8px)", duration: 0.20, ease: "power2.in" }}, 12.32);

    window.__timelines["act1-hook"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act1-hook.html").write_text(html, encoding="utf-8")

def write_act2():
    # Global 12.75 - 33.75s (dur 21.00s):
    # - DD_S05 (0..7.00s — 3D Mucosa CGI, NO FACE): Top 3D Title "Kích ứng niêm mạc" (Y=310..420) + Science Slide Pill (Y=1240..1330)!
    # - DD_S06 (7.00..10.75s) & DD_S07 (10.75..14.50s): Head at Y=220..680 -> ZERO top text!
    #   SLIDE OVERLAY #3: Frosted Liquid-Glass Checklist Card ("4 Điều nhỏ thương dạ dày") at X=64..645, Y=1018..1348!
    # - DD_S08 (14.50..21.00s): Head at Y=200..720, Box at Y=960..1415 -> ZERO top text over face AND ZERO overlap on box!
    #   Compact Slide-In Brand Pill right in the clean cream silk blouse band Y=775..855 (between chin Y=710 and box top Y=955)!
    html = f"""<template>
  <style>{SHARED_TYPO_CSS}</style>
  <div id="root" data-composition-id="act2-insight" data-width="1080" data-height="1920" data-start="0" data-duration="21">
    <div id="a2-rig-01" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a2-v01" class="clip bg-video" src="assets/videos/DD_S05.mp4" data-start="0" data-duration="7" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a2-rig-02" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a2-v02" class="clip bg-video" src="assets/videos/DD_S06.mp4" data-start="7" data-duration="3.75" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
    <div id="a2-rig-03" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a2-v03" class="clip bg-video" src="assets/videos/DD_S07.mp4" data-start="10.75" data-duration="3.75" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a2-rig-04" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a2-v04" class="clip bg-video" src="assets/videos/DD_S08.mp4" data-start="14.5" data-duration="6.5" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>

    <!-- Shot 5 (CGI, No Face): Capitalized 3D Silk-Satin Lockup (0.15 - 6.80s) -->
    <div id="a2-t1-clip" class="clip float-stage" data-start="0.15" data-duration="6.65" data-track-index="3" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a2t1")}
        <g id="a2-t1-badge" filter="url(#a2t1-clean-lift)">
          <text x="540" y="314" text-anchor="middle" class="upper-claim" font-size="29" fill="#B85600">DƯ THỪA ACID DỊCH VỊ</text>
        </g>
        <g id="a2-t1-hero">
          <text x="540" y="418" text-anchor="middle" class="satin-hero" font-size="82" fill="url(#a2t1-gold-fill)" filter="url(#a2t1-silk-3d)">Kích ứng niêm mạc</text>
        </g>
      </svg>
    </div>

    <!-- SLIDE OVERLAY #3 (Shots 6-7: 7.15 - 14.30s): Frosted Checklist Slide Card (X=64..646, Y=1016..1346 — 100% Face-Safe!) -->
    <div id="a2-slide-habits" class="clip slide-card" style="top: 1016px; width: 582px;" data-start="7.15" data-duration="7.15" data-track-index="4" data-layout-ignore>
      <div class="slide-card-header">🌿 Thói quen nhỏ thương dạ dày</div>
      <div id="a2-h1" class="slide-row"><span class="slide-badge-dot">✓</span> Ăn đúng bữa, ăn vừa phải</div>
      <div id="a2-h2" class="slide-row"><span class="slide-badge-dot">✓</span> Hạn chế món gây khó chịu</div>
      <div id="a2-h3" class="slide-row"><span class="slide-badge-dot">✓</span> Ngủ nghỉ điều độ mỗi ngày</div>
      <div id="a2-h4" class="slide-row"><span class="slide-badge-dot">✓</span> Không nằm ngay sau khi ăn</div>
    </div>

    <!-- Shot 8 (14.65 - 20.55s): Compact Slide-In Brand Pill in clean blouse band (Y=782..856 — Clear of chin Y=710 & box Y=955!) -->
    <div id="a2-slide-choice" class="clip slide-pill-stack" style="top: 782px;" data-start="14.65" data-duration="5.9" data-track-index="3" data-layout-ignore>
      <div id="a2-ch-pill" class="slide-pill slide-pill-emerald" style="padding: 10px 22px; font-size: 23px;">
        <span class="slide-badge-dot">★</span> Đồng hành cùng Dạ Dày Hằng Thu
      </div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a2-rig-01", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 7.00, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a2-rig-02", {{ scale: 1.04 }}, {{ scale: 1.00, duration: 3.75, ease: "none", immediateRender: false }}, 7.00)
      .fromTo("#a2-rig-03", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 3.75, ease: "none", immediateRender: false }}, 10.75)
      .fromTo("#a2-rig-04", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 6.50, ease: "none", immediateRender: false }}, 14.50);

    // CGI Lockup
    tl.fromTo("#a2-t1-badge", {{ opacity: 0, y: -12, scale: 0.93, filter: "blur(12px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.28, ease: "power3.out", immediateRender: false }}, 0.16)
      .fromTo("#a2-t1-hero", {{ opacity: 0, y: 18, scale: 0.93, filter: "blur(14px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.34, ease: "back.out(1.4)", immediateRender: false }}, 0.28)
      .fromTo("#a2t1-light", {{ attr: {{ x: 180 }} }}, {{ attr: {{ x: 920 }}, duration: 6.1, ease: "sine.inOut", immediateRender: false }}, 0.35)
      .to("#a2-t1-clip", {{ opacity: 0, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 6.58);

    // Slide Overlay #3 (4 Habits Checklist Card synced with vo_04 words!)
    tl.fromTo("#a2-slide-habits", {{ opacity: 0, x: -180, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.36, ease: "back.out(1.35)", immediateRender: false }}, 7.18)
      .fromTo("#a2-h1", {{ opacity: 0, x: -26 }}, {{ opacity: 1, x: 0, duration: 0.24, ease: "power2.out", immediateRender: false }}, 9.85)
      .fromTo("#a2-h2", {{ opacity: 0, x: -26 }}, {{ opacity: 1, x: 0, duration: 0.24, ease: "power2.out", immediateRender: false }}, 10.95)
      .fromTo("#a2-h3", {{ opacity: 0, x: -26 }}, {{ opacity: 1, x: 0, duration: 0.24, ease: "power2.out", immediateRender: false }}, 11.65)
      .fromTo("#a2-h4", {{ opacity: 0, x: -26 }}, {{ opacity: 1, x: 0, duration: 0.24, ease: "power2.out", immediateRender: false }}, 12.85)
      .to("#a2-slide-habits", {{ opacity: 0, x: -100, filter: "blur(10px)", duration: 0.22, ease: "power2.in" }}, 14.06);

    // Shot 8 Brand Companion Pill
    tl.fromTo("#a2-ch-pill", {{ opacity: 0, x: -140, scale: 0.94, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, scale: 1, filter: "blur(0px)", duration: 0.34, ease: "back.out(1.4)", immediateRender: false }}, 14.70)
      .to("#a2-slide-choice", {{ opacity: 0, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 20.32);

    window.__timelines["act2-insight"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act2-insight.html").write_text(html, encoding="utf-8")

def write_act3():
    # Global 33.75 - 49.50s (dur 15.75s):
    # - DD_S09 (0..7.50s — Hero Packshot, NO FACE, box starts at Y=660px):
    #   Capitalized 4-Tier Lockup in Y=306..622px + Slide-Up 3-Benefit Bar at Y=1265..1355px!
    # - DD_S10 (7.50..11.50s) & DD_S11 (11.50..15.75s — 4 Herbs & Pills, NO FACE, S11 box starts at Y=580px on right X>=520):
    #   Capitalized 3D Title "Tinh túy thảo dược Việt" at Y=308..395px (100% above S11 box!)
    #   + SLIDE OVERLAY #4: 4 Botanical Slide Cards in open left bokeh X=64..495, Y=435..735 (100% left of S11 box & above white bottle Y=950)!
    html = f"""<template>
  <style>
    {SHARED_TYPO_CSS}
    .herb-grid {{
      position: absolute;
      left: 64px;
      top: 438px;
      width: 432px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      z-index: 10;
      pointer-events: none;
    }}
    .herb-chip {{
      display: flex;
      align-items: center;
      gap: 12px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(238, 253, 242, 0.93) 100%);
      border-left: 6px solid #0E8A38;
      border-radius: 16px;
      padding: 10px 18px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 22px;
      font-weight: 800;
      color: #063D18;
      box-shadow: 0 8px 22px rgba(5, 38, 16, 0.20);
    }}
    .herb-sub {{
      font-family: "BeVietnamSemiVN", sans-serif;
      font-size: 16px;
      font-weight: 600;
      color: #B85900;
      margin-left: auto;
    }}
    .usp-bar {{
      position: absolute;
      left: 64px;
      top: 1268px;
      width: 796px;
      display: flex;
      gap: 12px;
      z-index: 10;
      pointer-events: none;
    }}
    .usp-tag {{
      flex: 1;
      text-align: center;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(236, 253, 241, 0.92) 100%);
      border: 2px solid rgba(14, 138, 56, 0.34);
      border-radius: 16px;
      padding: 10px 10px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 20px;
      font-weight: 800;
      color: #07461C;
      box-shadow: 0 8px 20px rgba(4, 34, 14, 0.18);
    }}
  </style>
  <div id="root" data-composition-id="act3-hero-demo" data-width="1080" data-height="1920" data-start="0" data-duration="15.75">
    <div id="a3-rig-01" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a3-v01" class="clip bg-video" src="assets/videos/DD_S09.mp4" data-start="0" data-duration="7.5" data-media-start="0.15" data-playback-rate="0.95" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a3-rig-02" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a3-v02" class="clip bg-video" src="assets/videos/DD_S10.mp4" data-start="7.5" data-duration="4" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
    <div id="a3-rig-03" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a3-v03" class="clip bg-video" src="assets/videos/DD_S11.mp4" data-start="11.5" data-duration="4.25" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>

    <!-- Shot 9: Capitalized 4-Tier Hero Lockup in Open Sky (Y=310..625px, clear of box Y>=660px!) -->
    <div id="a3-kv-clip" class="clip float-stage" data-start="0.125" data-duration="7.25" data-track-index="3" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a3kv")}
        <g id="a3-logo" filter="url(#a3kv-clean-lift)">
          <text x="540" y="314" text-anchor="middle" font-size="54">
            <tspan class="brand-contour" fill="url(#a3kv-brand-deep)">DẠ DÀY </tspan>
            <tspan class="brand-ht" fill="url(#a3kv-ht-accent)" font-size="58">HT</tspan>
          </text>
        </g>
        <g id="a3-script" filter="url(#a3kv-clean-lift)">
          <text x="540" y="376" text-anchor="middle" class="script-sub" font-size="50" fill="#084D1E">Hằng Thu</text>
        </g>
        <g id="a3-claim" filter="url(#a3kv-clean-lift)">
          <text x="540" y="432" text-anchor="middle" class="upper-claim" font-size="28" fill="#C96400">GIẢM ACID · BẢO VỆ NIÊM MẠC</text>
        </g>
        <g id="a3-satin">
          <text x="540" y="530" text-anchor="middle" class="satin-hero" font-size="100" fill="url(#a3kv-emerald-fill)" filter="url(#a3kv-silk-3d)">Xoa dịu êm</text>
          <text x="540" y="632" text-anchor="middle" class="satin-hero" font-size="96" fill="url(#a3kv-gold-fill)" filter="url(#a3kv-silk-3d)">Trào ngược</text>
        </g>
      </svg>
    </div>

    <!-- SLIDE OVERLAY #4A (Shot 9: 3.85 - 7.30s): 3-Chip USP Benefit Slide Bar below marble podium (X=64..860, Y=1268..1345) -->
    <div id="a3-usp-bar" class="clip usp-bar" data-start="3.85" data-duration="3.45" data-track-index="5" data-layout-ignore>
      <div id="a3-u1" class="usp-tag">✓ Dịu đau thượng vị</div>
      <div id="a3-u2" class="usp-tag">✓ Giảm ợ hơi, ợ chua</div>
      <div id="a3-u3" class="usp-tag">✓ Êm bụng, hết buồn nôn</div>
    </div>

    <!-- Shots 10-11: Capitalized Top 3D Title (Y=308..398px — 100% above S11 box at Y=580px!) -->
    <div id="a3-herb-clip" class="clip float-stage" data-start="7.625" data-duration="7.95" data-track-index="4" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a3hb")}
        <g id="a3-hb-top" filter="url(#a3hb-clean-lift)">
          <text x="540" y="308" text-anchor="middle" class="upper-claim" font-size="26" fill="#0B6B29">CÔNG THỨC 4 THẢO DƯỢC ĐÔNG Y</text>
        </g>
        <g id="a3-hb-satin">
          <text x="540" y="396" text-anchor="middle" class="satin-hero" font-size="78" fill="url(#a3hb-gold-fill)" filter="url(#a3hb-silk-3d)">Tinh túy thảo dược Việt</text>
        </g>
      </svg>
    </div>

    <!-- SLIDE OVERLAY #4B (Shots 10-11: 9.10 - 15.55s): 4 Botanical Slide Cards synced to voice in open Left Bokeh (X=64..496, Y=438..735 — 0% box overlap!) -->
    <div id="a3-herb-slides" class="clip herb-grid" data-start="9.1" data-duration="6.45" data-track-index="5" data-layout-ignore>
      <div id="a3-hc1" class="herb-chip"><span class="slide-badge-dot">1</span> Dạ cẩm <span class="herb-sub">Trung hòa acid</span></div>
      <div id="a3-hc2" class="herb-chip"><span class="slide-badge-dot">2</span> Nghệ đen <span class="herb-sub">Êm niêm mạc</span></div>
      <div id="a3-hc3" class="herb-chip"><span class="slide-badge-dot">3</span> Hoàng liên <span class="herb-sub">Thanh nhiệt</span></div>
      <div id="a3-hc4" class="herb-chip"><span class="slide-badge-dot">4</span> Mộc hương <span class="herb-sub">Giảm đầy hơi</span></div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a3-rig-01", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 7.50, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a3-rig-02", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 4.00, ease: "none", immediateRender: false }}, 7.50)
      .fromTo("#a3-rig-03", {{ scale: 1.05 }}, {{ scale: 1.00, duration: 4.25, ease: "none", immediateRender: false }}, 11.50);

    tl.fromTo("#a3-logo", {{ opacity: 0, y: -16, scale: 0.93, filter: "blur(12px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.5)", immediateRender: false }}, 0.14)
      .fromTo("#a3-script", {{ opacity: 0, y: 10, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "power2.out", immediateRender: false }}, 0.26)
      .fromTo("#a3-claim", {{ opacity: 0, y: 12, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out", immediateRender: false }}, 0.36)
      .fromTo("#a3-satin", {{ opacity: 0, y: 22, scale: 0.94, filter: "blur(14px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.40, ease: "back.out(1.4)", immediateRender: false }}, 0.46)
      .fromTo("#a3kv-light", {{ attr: {{ x: 160 }} }}, {{ attr: {{ x: 940 }}, duration: 6.4, ease: "sine.inOut", immediateRender: false }}, 0.50)
      .to("#a3-kv-clip", {{ opacity: 0, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 7.15);

    // 3-Chip USP Slide Bar
    tl.fromTo("#a3-u1", {{ opacity: 0, y: 28, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.5)", immediateRender: false }}, 3.88)
      .fromTo("#a3-u2", {{ opacity: 0, y: 28, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.5)", immediateRender: false }}, 4.08)
      .fromTo("#a3-u3", {{ opacity: 0, y: 28, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.5)", immediateRender: false }}, 4.28)
      .to("#a3-usp-bar", {{ opacity: 0, y: 16, filter: "blur(8px)", duration: 0.20, ease: "power2.in" }}, 7.08);

    // Shots 10-11 Top Title + 4 Staggered Botanical Slide Chips synced to voice timestamps!
    // Global 33.75 + local 9.35 = 43.10s ("Dạ cẩm"), +10.25 = 44.00s ("Nghệ đen"), +11.15 = 44.90s ("Hoàng liên"), +11.70 = 45.45s ("Mộc hương")
    tl.fromTo("#a3-hb-top", {{ opacity: 0, y: -12, scale: 0.93, filter: "blur(12px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.30, ease: "power3.out", immediateRender: false }}, 7.65)
      .fromTo("#a3-hb-satin", {{ opacity: 0, y: 18, scale: 0.94, filter: "blur(14px)", transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.36, ease: "back.out(1.4)", immediateRender: false }}, 7.80)
      .fromTo("#a3hb-light", {{ attr: {{ x: 160 }} }}, {{ attr: {{ x: 940 }}, duration: 7.2, ease: "sine.inOut", immediateRender: false }}, 7.85)
      .to("#a3-herb-clip", {{ opacity: 0, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 15.35);

    tl.fromTo("#a3-hc1", {{ opacity: 0, x: -130, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.4)", immediateRender: false }}, 9.30)
      .fromTo("#a3-hc2", {{ opacity: 0, x: -130, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.4)", immediateRender: false }}, 10.20)
      .fromTo("#a3-hc3", {{ opacity: 0, x: -130, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.4)", immediateRender: false }}, 11.10)
      .fromTo("#a3-hc4", {{ opacity: 0, x: -130, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.4)", immediateRender: false }}, 11.68)
      .to("#a3-herb-slides", {{ opacity: 0, x: -90, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 15.32);

    window.__timelines["act3-hero-demo"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act3-hero-demo.html").write_text(html, encoding="utf-8")

def write_act4():
    # Global 49.50 - 56.50s (dur 7.00s): DD_S12 (Head at Y=120..650px -> ZERO top text over her face!)
    # SLIDE OVERLAY #5: Frosted Golden-Emerald Payoff Slide Card in lower-left chest zone (X=64..660, Y=1115..1345 — 100% Face-Safe!)
    html = f"""<template>
  <style>{SHARED_TYPO_CSS}</style>
  <div id="root" data-composition-id="act4-payoff" data-width="1080" data-height="1920" data-start="0" data-duration="7">
    <div id="a4-rig-01" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="a4-v01" class="clip bg-video" src="assets/videos/DD_S12.mp4" data-start="0" data-duration="7" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>

    <!-- SLIDE OVERLAY #5 (0.20 - 6.75s): Frosted Payoff Slide Card (X=64..654, Y=1110..1346 — 0% face touch!) -->
    <div id="a4-slide-payoff" class="clip slide-card" style="top: 1110px; width: 590px;" data-start="0.2" data-duration="6.55" data-track-index="3" data-layout-ignore>
      <div class="slide-card-header">✨ Dạ dày êm ái mỗi ngày</div>
      <div id="a4-p1" class="slide-row"><span class="slide-badge-dot">✓</span> Bữa ăn trọn vẹn niềm vui</div>
      <div id="a4-p2" class="slide-row"><span class="slide-badge-dot">✓</span> Tối ngủ sâu · Sáng tràn năng lượng</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a4-rig-01", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 7.00, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a4-slide-payoff", {{ opacity: 0, x: -170, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.36, ease: "back.out(1.4)", immediateRender: false }}, 0.24)
      .fromTo("#a4-p1", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.26, ease: "power2.out", immediateRender: false }}, 0.55)
      .fromTo("#a4-p2", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.26, ease: "power2.out", immediateRender: false }}, 3.55)
      .to("#a4-slide-payoff", {{ opacity: 0, x: -90, filter: "blur(10px)", duration: 0.22, ease: "power2.in" }}, 6.50);

    window.__timelines["act4-payoff"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act4-payoff.html").write_text(html, encoding="utf-8")

def write_act6(end_dur: float):
    # Global 56.50 - 63.00s: DD_S13 End-Card — Capitalized "Bụng êm" / "Sống khỏe", 100% Face-Safe & Safe-Zone Verified!
    html = f"""<template>
  <style>
    {SHARED_TYPO_CSS}
    .ec-mist {{
      position: absolute;
      left: 440px; top: 245px; width: 620px; height: 610px;
      background: radial-gradient(
        closest-side at 58% 48%,
        rgba(244, 255, 247, 0.86) 0%,
        rgba(230, 252, 236, 0.50) 58%,
        rgba(230, 252, 236, 0) 100%
      );
      pointer-events: none; z-index: 4;
    }}
    .ec-legal-bar {{
      position: absolute;
      left: 64px; width: 808px; top: 1472px;
      text-align: center; font-size: 18px; line-height: 1.32; font-weight: 800;
      color: #063916;
      paint-order: stroke fill;
      -webkit-text-stroke: 6px #ffffff;
      filter: drop-shadow(0 2px 6px rgba(4, 36, 14, 0.30));
      z-index: 10;
    }}
  </style>
  <div id="root" data-composition-id="act6-endcard" data-width="1080" data-height="1920" data-start="0" data-duration="{end_dur}">
    <div id="ec-cam-01" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_WARM}" id="ec-v01" class="clip bg-video" src="assets/videos/DD_S13.mp4" data-start="0" data-duration="{end_dur}" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>

    <div id="ec-mist-clip" class="clip ec-mist" data-start="0.05" data-duration="{round(end_dur - 0.05, 3)}" data-track-index="3" data-layout-ignore></div>

    <div id="ec-kv-clip" class="clip float-stage" data-start="0.125" data-duration="{round(end_dur - 0.125, 3)}" data-track-index="4" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("eckv", light_x=650)}
        <g id="ec-logo" filter="url(#eckv-clean-lift)">
          <text x="794" y="318" text-anchor="middle" font-size="44">
            <tspan class="brand-contour" fill="url(#eckv-brand-deep)">DẠ DÀY </tspan>
            <tspan class="brand-ht" fill="url(#eckv-ht-accent)" font-size="48">HT</tspan>
          </text>
        </g>
        <g id="ec-script" filter="url(#eckv-clean-lift)">
          <text x="794" y="376" text-anchor="middle" class="script-sub" font-size="44" fill="#084D1E">Hằng Thu</text>
        </g>
        <g id="ec-claim" filter="url(#eckv-clean-lift)">
          <text x="794" y="428" text-anchor="middle" class="upper-claim" font-size="22" fill="#C96400">ÊM DẠ DÀY · KHỎE TIÊU HÓA</text>
        </g>
        <g id="ec-satin">
          <text x="794" y="526" text-anchor="middle" class="satin-hero" font-size="84" fill="url(#eckv-emerald-fill)" filter="url(#eckv-silk-3d)">Bụng êm</text>
          <text x="794" y="624" text-anchor="middle" class="satin-hero" font-size="80" fill="url(#eckv-gold-fill)" filter="url(#eckv-silk-3d)">Sống khỏe</text>
        </g>
        <g id="ec-cta" filter="url(#eckv-clean-lift)">
          <text x="794" y="704" text-anchor="middle" class="cta-open" font-size="24" fill="#074B1D">
            Nhắn <tspan fill="#D46B00">“DẠ DÀY”</tspan> · Tư vấn ngay
          </text>
          <text x="794" y="746" text-anchor="middle" class="cta-open" font-size="19" fill="#0E7C33">#HangThuPharma · #DaDayHangThu</text>
        </g>
      </svg>
    </div>

    <div id="ec-legal-clip" class="clip ec-legal-bar" data-start="0.2" data-duration="{round(end_dur - 0.2, 3)}" data-track-index="5" data-layout-ignore>
      Thực phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#ec-cam-01", {{ x: -64, scale: 1.09 }}, {{ x: -72, scale: 1.13, duration: {end_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#ec-mist-clip", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.45, ease: "power2.out", immediateRender: false }}, 0.08)
      .fromTo("#ec-logo", {{ opacity: 0, y: -14, scale: 0.93, filter: "blur(12px)", transformOrigin: "794px 310px" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "back.out(1.5)", immediateRender: false }}, 0.14)
      .fromTo("#ec-script", {{ opacity: 0, y: 10, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "power2.out", immediateRender: false }}, 0.26)
      .fromTo("#ec-claim", {{ opacity: 0, y: 12, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out", immediateRender: false }}, 0.36)
      .fromTo("#ec-satin", {{ opacity: 0, y: 20, scale: 0.94, filter: "blur(14px)", transformOrigin: "794px 575px" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.40, ease: "back.out(1.4)", immediateRender: false }}, 0.46)
      .fromTo("#ec-cta", {{ opacity: 0, y: 14, scale: 0.95, filter: "blur(10px)", transformOrigin: "794px 725px" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.34, ease: "back.out(1.5)", immediateRender: false }}, 0.62)
      .to("#ec-cta", {{ scale: 1.04, transformOrigin: "794px 725px", duration: 0.55, ease: "sine.inOut" }}, 2.00)
      .to("#ec-cta", {{ scale: 1.00, transformOrigin: "794px 725px", duration: 0.55, ease: "sine.inOut" }}, 2.55)
      .fromTo("#eckv-light", {{ attr: {{ x: 560 }} }}, {{ attr: {{ x: 1020 }}, duration: {round(end_dur - 0.6, 2)}, ease: "sine.inOut", immediateRender: false }}, 0.50);

    window.__timelines["act6-endcard"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act6-endcard.html").write_text(html, encoding="utf-8")

def write_captions(manifest: dict):
    # 100% CAPITALIZED FIRST LETTER ON EVERY SINGLE SUBTITLE CARD!
    # Also placed at top: 1416px (and 1434px on S08) so 0% overlap with Slide Cards above AND <= 1540px Safe Zone!
    segs = {s["id"]: s for s in manifest["segments"]}
    caps = [
        ("cap-01a", segs["vo_01"]["start_s"], round(segs["vo_01"]["start_s"] + 2.95, 2), 1412, 'Bữa sáng <span class="cap-kw">ly cà phê vội</span>, trưa thì kẹt họp,'),
        ("cap-01b", round(segs["vo_01"]["start_s"] + 2.98, 2), round(segs["vo_01"]["end_s"] + 0.10, 2), 1416, 'Tối về lại <span class="cap-kw">ăn bù thật no?</span>'),
        ("cap-02a", segs["vo_02"]["start_s"], round(segs["vo_02"]["start_s"] + 3.25, 2), 1416, 'Đến lúc <span class="cap-kw">bụng trên nóng rát</span>, ợ hơi, buồn nôn,'),
        ("cap-02b", round(segs["vo_02"]["start_s"] + 3.28, 2), round(segs["vo_02"]["end_s"] + 0.10, 2), 1412, 'Chị mới giật mình chưa <span class="cap-kw">thương lấy dạ dày mình.</span>'),
        ("cap-03a", segs["vo_03"]["start_s"], round(segs["vo_03"]["start_s"] + 3.65, 2), 1412, 'Ăn uống thất thường khiến <span class="cap-kw">acid dịch vị dư thừa,</span>'),
        ("cap-03b", round(segs["vo_03"]["start_s"] + 3.68, 2), round(segs["vo_03"]["end_s"] + 0.10, 2), 1412, 'Dễ làm tổn thương <span class="cap-kw">lớp niêm mạc mỏng manh.</span>'),
        ("cap-04a", segs["vo_04"]["start_s"], round(segs["vo_04"]["start_s"] + 4.35, 2), 1416, 'Hãy bắt đầu từ điều nhỏ: <span class="cap-kw">ăn đúng bữa, vừa phải,</span>'),
        ("cap-04b", round(segs["vo_04"]["start_s"] + 4.38, 2), round(segs["vo_04"]["end_s"] + 0.10, 2), 1416, 'Ngủ nghỉ điều độ &amp; <span class="cap-kw">đừng nằm ngay sau ăn.</span>'),
        ("cap-05a", segs["vo_05"]["start_s"], round(segs["vo_05"]["start_s"] + 3.55, 2), 1434, 'Và để <span class="cap-kw">dạ dày luôn khỏe êm</span> suốt ngày bận rộn,'),
        ("cap-05b", round(segs["vo_05"]["start_s"] + 3.58, 2), round(segs["vo_05"]["end_s"] + 0.10, 2), 1434, 'Chị chọn đồng hành cùng <span class="cap-kw">Dạ Dày Hằng Thu.</span>'),
        ("cap-06a", segs["vo_06"]["start_s"], round(segs["vo_06"]["start_s"] + 3.95, 2), 1416, '<span class="cap-kw">Dạ Dày Hằng Thu</span> hỗ trợ giảm acid, bảo vệ niêm mạc,'),
        ("cap-06b", round(segs["vo_06"]["start_s"] + 3.98, 2), round(segs["vo_06"]["end_s"] + 0.10, 2), 1416, 'Xoa dịu cơn <span class="cap-kw">đau dạ dày, ợ hơi &amp; trào ngược.</span>'),
        ("cap-07a", segs["vo_07"]["start_s"], round(segs["vo_07"]["start_s"] + 4.65, 2), 1412, 'Tinh túy <span class="cap-kw">Dạ cẩm, Nghệ đen, Hoàng liên, Mộc hương</span>'),
        ("cap-07b", round(segs["vo_07"]["start_s"] + 4.68, 2), round(segs["vo_07"]["end_s"] + 0.10, 2), 1412, 'Giúp nâng niu hệ tiêu hóa từ <span class="cap-kw">thảo dược thiên nhiên.</span>'),
        ("cap-08a", segs["vo_08"]["start_s"], round(segs["vo_08"]["start_s"] + 3.45, 2), 1416, '<span class="cap-kw">Dạ dày êm ái</span> để mỗi bữa ăn trọn vẹn niềm vui,'),
        ("cap-08b", round(segs["vo_08"]["start_s"] + 3.48, 2), round(segs["vo_08"]["end_s"] + 0.10, 2), 1416, 'Tối ngủ thật sâu &amp; sáng mai <span class="cap-kw">tràn đầy năng lượng.</span>'),
    ]

    divs = []
    js_groups = []
    for idx, (cid, st, en, top_y, inner) in enumerate(caps):
        dur = round(en - st, 3)
        trk = (idx % 4) + 1
        divs.append(
            f'    <div id="{cid}" class="clip cap-clip" style="top: {top_y}px;" data-start="{st}" data-duration="{dur}" data-track-index="{trk}" data-layout-ignore>\n'
            f'      <div id="in-{cid}" class="cap-line">{inner}</div>\n'
            f'    </div>'
        )
        js_groups.append(f'      {{ sel: "#in-{cid}", st: {st}, en: {en} }}')

    cap_end = segs["vo_09"]["shot_start_s"]
    html = f"""<template>
  <style>
    @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "PlayfairVNItalic"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
    /* Strictly inside TikTok & Reels White Safe Zone: X=[62..874] <= 884px, Y=[1412..1524] <= 1545px */
    .cap-clip {{
      position: absolute;
      left: 62px;
      width: 812px;
      text-align: center;
      overflow: visible;
    }}
    .cap-line {{
      display: inline-block;
      max-width: 808px;
      opacity: 0;
      font-family: "BeVietnamVN", sans-serif;
      font-weight: 800;
      font-size: 31px;
      line-height: 1.30;
      color: #063B17;
      paint-order: stroke fill;
      -webkit-text-stroke: 10px #ffffff;
      filter: drop-shadow(0 5px 12px rgba(4, 34, 14, 0.34));
      letter-spacing: -0.01em;
    }}
    .cap-kw {{
      color: #D46B00;
      font-family: "PlayfairVNItalic", Georgia, serif;
      font-style: italic;
      font-weight: 700;
      font-size: 35px;
      paint-order: stroke fill;
      -webkit-text-stroke: 10px #ffffff;
    }}
  </style>

  <div id="root" data-composition-id="captions-track" data-width="1080" data-height="1920">
{chr(10).join(divs)}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    const groups = [
{",".join(chr(10) + g for g in js_groups)}
    ];
    groups.forEach((g) => {{
      tl.fromTo(g.sel, {{ opacity: 0, y: 12, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.18, ease: "power3.out" }}, g.st)
        .to(g.sel, {{ opacity: 0, y: -6, filter: "blur(6px)", duration: 0.14, ease: "power2.in" }}, g.en - 0.14)
        .set(g.sel, {{ opacity: 0, visibility: "hidden" }}, g.en);
    }});
    window.__timelines["captions-track"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "captions-track.html").write_text(html, encoding="utf-8")
    return cap_end

def write_transitions():
    html = """<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
    .fx-clip { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
    .sun-flare {
      position: absolute; inset: 0; opacity: 0;
      background: radial-gradient(
        ellipse at 52% 42%,
        rgba(255, 255, 255, 0.86) 0%,
        rgba(232, 255, 238, 0.72) 32%,
        rgba(82, 212, 118, 0.42) 60%,
        rgba(82, 212, 118, 0) 86%
      );
      mix-blend-mode: screen;
    }
    .portal-ring {
      position: absolute;
      left: 50%; top: 50%;
      width: 920px; height: 920px;
      margin-left: -460px; margin-top: -460px;
      opacity: 0; border-radius: 50%;
      border: 68px solid #88EE9E;
      box-shadow:
        inset 0 0 52px rgba(255, 250, 215, 0.94),
        0 0 72px rgba(22, 168, 72, 0.86);
    }
  </style>

  <div id="root" data-composition-id="tvc-transitions" data-width="1080" data-height="1920">
    <div id="fx-fl1-clip" class="clip fx-clip" data-start="12.5" data-duration="0.5" data-track-index="1" data-layout-ignore>
      <div id="fx-fl1" class="sun-flare"></div>
    </div>
    <div id="fx-fl2-clip" class="clip fx-clip" data-start="19.5" data-duration="0.5" data-track-index="2" data-layout-ignore>
      <div id="fx-fl2" class="sun-flare"></div>
    </div>
    <div id="fx-portal-clip" class="clip fx-clip" data-start="33.375" data-duration="0.75" data-track-index="3" data-layout-allow-overflow data-layout-ignore>
      <div id="fx-portal" class="portal-ring"></div>
      <div id="fx-fl3" class="sun-flare"></div>
    </div>
    <div id="fx-fl4-clip" class="clip fx-clip" data-start="49.25" data-duration="0.5" data-track-index="2" data-layout-ignore>
      <div id="fx-fl4" class="sun-flare"></div>
    </div>
    <div id="fx-fl5-clip" class="clip fx-clip" data-start="56.25" data-duration="0.5" data-track-index="1" data-layout-ignore>
      <div id="fx-fl5" class="sun-flare"></div>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({ paused: true });
    [
      { id: "#fx-fl1", st: 12.50, pk: 12.75 },
      { id: "#fx-fl2", st: 19.50, pk: 19.75 },
      { id: "#fx-fl4", st: 49.25, pk: 49.50 },
      { id: "#fx-fl5", st: 56.25, pk: 56.50 }
    ].forEach((f) => {
      tl.fromTo(f.id, { opacity: 0, scale: 0.96 }, { opacity: 0.68, scale: 1.04, duration: 0.25, ease: "sine.in" }, f.st)
        .to(f.id, { opacity: 0, scale: 1.10, duration: 0.25, ease: "sine.out" }, f.pk);
    });

    tl.fromTo("#fx-portal", { opacity: 0, scale: 0.35, rotation: 0 }, { opacity: 1, scale: 1.15, rotation: 95, duration: 0.375, ease: "power2.in" }, 33.375)
      .to("#fx-portal", { opacity: 0, scale: 2.85, rotation: 190, duration: 0.375, ease: "power3.out" }, 33.75);

    tl.fromTo("#fx-fl3", { opacity: 0 }, { opacity: 0.84, duration: 0.375, ease: "sine.in" }, 33.375)
      .to("#fx-fl3", { opacity: 0, duration: 0.375, ease: "sine.out" }, 33.75);

    window.__timelines["tvc-transitions"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "tvc-transitions.html").write_text(html, encoding="utf-8")

def write_root_index(manifest: dict, cap_end: float):
    total_dur = manifest["total_duration_s"]
    end_dur = round(total_dur - 56.50, 2)

    vo_tags = []
    for idx, s in enumerate(manifest["segments"]):
        trk = 5 if (idx % 2 == 0) else 6
        vol = "1.32" if idx in (5, 6, 8) else "1.30"
        vo_tags.append(
            f'      <audio id="{s["id"].replace("_", "-")}" class="clip" src="assets/audio/{s["id"]}.wav" '
            f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{trk}" '
            f'data-volume="{vol}" data-fade-in="0.035" data-fade-out="0.055" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        )

    bgm2_dur = round(total_dur - 33.65, 2)
    outro_swell_t = round(bgm2_dur - 1.05, 2)

    html = f"""<!doctype html>
<html
  lang="vi"
  data-composition-variables='[
    {{"id":"brand_name","type":"string","label":"Thương hiệu","default":"DẠ DÀY HT"}},
    {{"id":"brand_script","type":"string","label":"Dòng chữ ký","default":"Hằng Thu"}},
    {{"id":"hero_claim","type":"string","label":"Công dụng chính","default":"GIẢM ACID · BẢO VỆ NIÊM MẠC"}},
    {{"id":"cta_keyword","type":"string","label":"Từ khóa CTA","default":"Nhắn “DẠ DÀY” · Tư vấn ngay"}},
    {{"id":"legal_text","type":"string","label":"Khuyến cáo","default":"Thực phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh"}}
  ]'
>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Dạ Dày Hằng Thu — Bài 5 USP TVC V2 (Face-Safe, Slide Overlays, 24p)</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "FrauncesVN"; src: url("assets/fonts/Fraunces-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
      @font-face {{ font-family: "PlayfairVN"; src: url("assets/fonts/PlayfairDisplay-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
      @font-face {{ font-family: "PlayfairVNItalic"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; font-display: block; }}
      @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
      @font-face {{ font-family: "BeVietnamSemiVN"; src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype"); font-weight: 600; font-display: block; }}
      @font-face {{ font-family: "DancingVN"; src: url("assets/fonts/DancingScript-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #072614; font-family: sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .captions-host {{ position: absolute; inset: 0; z-index: 12; pointer-events: none; }}
      .transitions-host {{ position: absolute; inset: 0; z-index: 18; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total_dur}" data-width="1080" data-height="1920" data-fps="24">
      <!-- Sequential Acts — 13 Unique Video Clips (DD_S01..DD_S13), Zero Repeats -->
      <div id="act1-hook" class="scene-host" data-composition-id="act1-hook" data-composition-src="compositions/act1-hook.html" data-start="0" data-duration="12.75" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act2-insight" class="scene-host" data-composition-id="act2-insight" data-composition-src="compositions/act2-insight.html" data-start="12.75" data-duration="21" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act3-hero-demo" class="scene-host" data-composition-id="act3-hero-demo" data-composition-src="compositions/act3-hero-demo.html" data-start="33.75" data-duration="15.75" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act4-payoff" class="scene-host" data-composition-id="act4-payoff" data-composition-src="compositions/act4-payoff.html" data-start="49.5" data-duration="7" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act6-endcard" class="scene-host" data-composition-id="act6-endcard" data-composition-src="compositions/act6-endcard.html" data-start="56.5" data-duration="{end_dur}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <!-- 9:16 Safe-Zone Subtitles & Emerald-Gold Portal Spin Transitions -->
      <div id="captions-track" class="captions-host" data-composition-id="captions-track" data-composition-src="compositions/captions-track.html" data-start="0" data-duration="{cap_end}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="tvc-transitions" class="transitions-host" data-composition-id="tvc-transitions" data-composition-src="compositions/tvc-transitions.html" data-start="0" data-duration="{total_dur}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <!-- Checkerboard Vietnamese Voiceover (THANH THANH TVC) -->
{chr(10).join(vo_tags)}

      <!-- Two-Part Harmonic C-Major Commercial BGM ("Fretless" -> "Life of Riley" @ 33.75s Hero Reveal) -->
      <audio id="bgm-warm-intro" class="clip" src="assets/audio/bgm_warm_fretless.mp3" data-start="0" data-duration="33.90" data-media-start="0" data-track-index="7" data-fade-in="0.18" data-fade-out="0.45" data-fx-chain="{{&quot;version&quot;:1,&quot;nodes&quot;:[{{&quot;type&quot;:&quot;gain&quot;,&quot;id&quot;:&quot;bgain1&quot;,&quot;label&quot;:&quot;Level match&quot;,&quot;params&quot;:{{&quot;gain&quot;:7.0}}}},{{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;bhp1&quot;,&quot;label&quot;:&quot;Clean low end&quot;,&quot;params&quot;:{{&quot;frequency&quot;:75}}}},{{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;bcarve1&quot;,&quot;label&quot;:&quot;Voice pocket&quot;,&quot;params&quot;:{{&quot;frequency&quot;:2300,&quot;gain&quot;:-3.8,&quot;q&quot;:0.85}}}},{{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;blim1&quot;,&quot;params&quot;:{{&quot;limit&quot;:-2.5}}}}]}}" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.58}},{{&quot;t&quot;:0.22,&quot;v&quot;:0.32}},{{&quot;t&quot;:4.9,&quot;v&quot;:0.32}},{{&quot;t&quot;:5.12,&quot;v&quot;:0.50}},{{&quot;t&quot;:5.42,&quot;v&quot;:0.32}},{{&quot;t&quot;:12.25,&quot;v&quot;:0.32}},{{&quot;t&quot;:12.55,&quot;v&quot;:0.50}},{{&quot;t&quot;:12.92,&quot;v&quot;:0.31}},{{&quot;t&quot;:19.35,&quot;v&quot;:0.31}},{{&quot;t&quot;:19.65,&quot;v&quot;:0.50}},{{&quot;t&quot;:19.95,&quot;v&quot;:0.32}},{{&quot;t&quot;:26.95,&quot;v&quot;:0.32}},{{&quot;t&quot;:27.22,&quot;v&quot;:0.50}},{{&quot;t&quot;:27.45,&quot;v&quot;:0.34}},{{&quot;t&quot;:33.35,&quot;v&quot;:0.34}},{{&quot;t&quot;:33.90,&quot;v&quot;:0.0}}]}}]}}"></audio>
      <audio id="bgm-bright-hero" class="clip" src="assets/audio/bgm_bright_riley.mp3" data-start="33.65" data-duration="{bgm2_dur}" data-media-start="0" data-track-index="8" data-fade-in="0.20" data-fade-out="0.65" data-fx-chain="{{&quot;version&quot;:1,&quot;nodes&quot;:[{{&quot;type&quot;:&quot;gain&quot;,&quot;id&quot;:&quot;bgain2&quot;,&quot;label&quot;:&quot;Level match&quot;,&quot;params&quot;:{{&quot;gain&quot;:6.6}}}},{{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;bhp2&quot;,&quot;label&quot;:&quot;Clean low end&quot;,&quot;params&quot;:{{&quot;frequency&quot;:80}}}},{{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;bcarve2&quot;,&quot;label&quot;:&quot;Voice pocket&quot;,&quot;params&quot;:{{&quot;frequency&quot;:2400,&quot;gain&quot;:-3.8,&quot;q&quot;:0.85}}}},{{&quot;type&quot;:&quot;highshelf&quot;,&quot;id&quot;:&quot;bair2&quot;,&quot;label&quot;:&quot;Bright sheen&quot;,&quot;params&quot;:{{&quot;frequency&quot;:7500,&quot;gain&quot;:1.3}}}},{{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;blim2&quot;,&quot;params&quot;:{{&quot;limit&quot;:-2.5}}}}]}}" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.60}},{{&quot;t&quot;:0.35,&quot;v&quot;:0.34}},{{&quot;t&quot;:7.1,&quot;v&quot;:0.34}},{{&quot;t&quot;:7.4,&quot;v&quot;:0.56}},{{&quot;t&quot;:7.8,&quot;v&quot;:0.34}},{{&quot;t&quot;:15.4,&quot;v&quot;:0.34}},{{&quot;t&quot;:15.7,&quot;v&quot;:0.56}},{{&quot;t&quot;:16.05,&quot;v&quot;:0.35}},{{&quot;t&quot;:22.4,&quot;v&quot;:0.35}},{{&quot;t&quot;:22.75,&quot;v&quot;:0.56}},{{&quot;t&quot;:23.08,&quot;v&quot;:0.35}},{{&quot;t&quot;:{round(outro_swell_t - 0.2, 2)},&quot;v&quot;:0.35}},{{&quot;t&quot;:{outro_swell_t},&quot;v&quot;:0.74}},{{&quot;t&quot;:{bgm2_dur},&quot;v&quot;:0.74}}]}}]}}"></audio>

      <!-- Frame-Synced Tactile Studio Micro-SFX (Synced to Slide Overlays & Transitions, Disjoint Tracks 9-13) -->
      <audio id="sfx-hook-swipe" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="0.06" data-duration="0.50" data-track-index="9" data-volume="0.22" data-fade-out="0.12"></audio>
      <audio id="sfx-slide1-swipe" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="2.44" data-duration="0.50" data-track-index="9" data-volume="0.20" data-fade-out="0.12"></audio>
      <audio id="sfx-slide2-swipe" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="5.28" data-duration="0.50" data-track-index="9" data-volume="0.18" data-fade-out="0.12"></audio>
      <audio id="sfx-cgi-swipe" class="clip" src="assets/audio/sfx_whoosh_transition.mp3" data-start="12.66" data-duration="0.55" data-track-index="9" data-volume="0.20" data-fade-out="0.14"></audio>
      <audio id="sfx-slide3-swipe" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="19.82" data-duration="0.50" data-track-index="9" data-volume="0.20" data-fade-out="0.12"></audio>
      <audio id="sfx-portal-swell" class="clip" src="assets/audio/sfx_whoosh_cinematic.mp3" data-start="32.25" data-duration="3.00" data-media-start="1.00" data-track-index="9" data-volume="0.20" data-fade-in="0.25" data-fade-out="0.45"></audio>
      <audio id="sfx-slide5-swipe" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="49.62" data-duration="0.50" data-track-index="9" data-volume="0.20" data-fade-out="0.12"></audio>
      <audio id="sfx-endcard-swipe" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="56.42" data-duration="0.55" data-track-index="9" data-volume="0.22" data-fade-out="0.12"></audio>

      <audio id="sfx-hook-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="0.22" data-duration="0.60" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>
      <audio id="sfx-meal-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="2.56" data-duration="0.60" data-track-index="10" data-volume="0.20" data-fade-out="0.12"></audio>
      <audio id="sfx-sym1-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="5.40" data-duration="0.55" data-track-index="10" data-volume="0.20" data-fade-out="0.12"></audio>
      <audio id="sfx-sym2-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="6.12" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-sym3-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="6.86" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-cgi-ping" class="clip" src="assets/audio/sfx_ping_glass.mp3" data-start="12.92" data-duration="1.20" data-track-index="10" data-volume="0.20" data-fade-out="0.25"></audio>
      <audio id="sfx-h1-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="22.60" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-h3-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="24.40" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-h4-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="25.60" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-choice-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="27.45" data-duration="0.60" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>
      <audio id="sfx-hero-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="34.10" data-duration="0.60" data-track-index="10" data-volume="0.24" data-fade-out="0.12"></audio>
      <audio id="sfx-usp-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="37.65" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-hc1-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="43.05" data-duration="0.50" data-track-index="10" data-volume="0.20" data-fade-out="0.10"></audio>
      <audio id="sfx-hc2-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="43.95" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-hc3-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="44.85" data-duration="0.34" data-track-index="10" data-volume="0.26" data-fade-out="0.08"></audio>
      <audio id="sfx-hc4-click" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="45.45" data-duration="0.34" data-track-index="10" data-volume="0.28" data-fade-out="0.08"></audio>
      <audio id="sfx-payoff-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="49.75" data-duration="0.60" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>
      <audio id="sfx-cta-pop" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="57.10" data-duration="0.60" data-track-index="10" data-volume="0.24" data-fade-out="0.12"></audio>

      <audio id="sfx-choice-chime" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="27.32" data-duration="2.30" data-track-index="11" data-volume="0.56" data-fade-out="0.45"></audio>
      <audio id="sfx-portal-sparkle" class="clip" src="assets/audio/sfx_sparkle_shine.mp3" data-start="33.72" data-duration="1.75" data-track-index="11" data-volume="0.26" data-fade-out="0.35"></audio>
      <audio id="sfx-hero-shimmer" class="clip" src="assets/audio/sfx_crystal_shimmer.mp3" data-start="35.80" data-duration="2.20" data-media-start="0.15" data-track-index="11" data-volume="0.66" data-fade-in="0.08" data-fade-out="0.50"></audio>
      <audio id="sfx-herb-shimmer" class="clip" src="assets/audio/sfx_crystal_shimmer.mp3" data-start="41.65" data-duration="2.20" data-media-start="0.55" data-track-index="11" data-volume="0.68" data-fade-in="0.08" data-fade-out="0.50"></audio>
      <audio id="sfx-payoff-chime" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="49.62" data-duration="2.30" data-track-index="11" data-volume="0.58" data-fade-out="0.45"></audio>
      <audio id="sfx-endcard-chime" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="56.62" data-duration="2.30" data-track-index="11" data-volume="0.62" data-fade-out="0.45"></audio>

      <audio id="sfx-gold-sweep" class="clip" src="assets/audio/sfx_sparkle_shine.mp3" data-start="57.30" data-duration="1.75" data-track-index="12" data-volume="0.24" data-fade-out="0.35"></audio>
      <audio id="sfx-cta-chime" class="clip" src="assets/audio/sfx_notification_cta.mp3" data-start="57.45" data-duration="2.25" data-track-index="13" data-volume="0.20" data-fade-out="0.40"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (HF_DIR / "index.html").write_text(html, encoding="utf-8")

def main():
    COMP_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(VO_MANIFEST_PATH.read_text(encoding="utf-8"))
    end_dur = round(manifest["total_duration_s"] - 56.50, 2)

    write_act1()
    write_act2()
    write_act3()
    write_act4()
    write_act6(end_dur)
    cap_end = write_captions(manifest)
    write_transitions()
    write_root_index(manifest, cap_end)
    print(f"[HYPERFRAMES V2 UPGRADED] {HF_DIR / 'index.html'} (total={manifest['total_duration_s']}s @ 24fps)")

if __name__ == "__main__":
    main()
