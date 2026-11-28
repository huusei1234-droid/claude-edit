"""
Ngày 01 (24/11/2026) — Dựng hậu kỳ HyperFrames 24fps Dọc 9:16 (1080x1920) cho Video USP:
SP02 — Viên Đặt Phụ Khoa LT Plus Hằng Thu (Tổng thời lượng 57.50s = 1,380 frames)
Tuân thủ 100% chuẩn V2 đã duyệt của Editor:
1. Viết hoa 100% chữ cái đầu câu / đầu dòng trên MỌI Tiêu đề 3D, Thẻ Slide và cả 14 thẻ Phụ đề.
2. Face-Safe & Box-Safe 100% (0% chữ che trán/mắt/mặt Chị Hằng trên S02, S04, S07; đối chiếu thêm với ruler_8shots.jpg).
3. Chèn 5 Lớp Phủ Slide Kính Mờ Hồng Ngọc (Frosted Rose-Silk Liquid-Glass Slide Overlays) trượt êm có trọng lượng vật lý + Micro-SFX.
4. Nằm gọn 100% trong Vùng Trắng An Toàn TikTok x Reels 9:16 (Y in [255..1540], X in [58..1020] trên, X in [58..880] dưới).
"""
import json
import shutil
from pathlib import Path

PROJ_DIR = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124")
VO_MANIFEST_PATH = PROJ_DIR / "06_Audio_Voiceover" / "vo_manifest.json"
HF_DIR = PROJ_DIR / "07_HyperFrames_Project"
COMP_DIR = HF_DIR / "compositions"
IMG_DIR = HF_DIR / "assets" / "images"

BRAND_KIT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")

COLOR_GRADE_ROSESILK = (
    '{&quot;preset&quot;:null,&quot;intensity&quot;:1,&quot;adjust&quot;:{&quot;exposure&quot;:0.04,&quot;contrast&quot;:0.07,'
    '&quot;highlights&quot;:0.03,&quot;shadows&quot;:0.05,&quot;whites&quot;:0.05,&quot;blacks&quot;:0,&quot;temperature&quot;:0.02,'
    '&quot;tint&quot;:0.02,&quot;vibrance&quot;:0.11,&quot;saturation&quot;:0.04},&quot;details&quot;:{&quot;vignette&quot;:0.04,'
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
      background: #2C0918; font-family: "BeVietnamVN", sans-serif;
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
    .script-sub {
      font-family: "DancingVN", cursive;
      font-weight: 700; paint-order: stroke fill;
      stroke: rgba(255, 255, 255, 0.96); stroke-width: 8px; stroke-linejoin: round;
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
      stroke: rgba(255, 255, 255, 0.94); stroke-width: 10px; stroke-linejoin: round;
    }
    .cta-open {
      font-family: "BeVietnamVN", sans-serif;
      font-weight: 800; letter-spacing: 0.01em;
      paint-order: stroke fill;
      stroke: #ffffff; stroke-width: 11px; stroke-linejoin: round; stroke-linecap: round;
    }

    /* Rose-Silk Frosted Liquid-Glass Slide Overlay System (Safe Zone X in [64..865], Face-Safe 100%) */
    .slide-card {
      position: absolute;
      left: 64px;
      border-radius: 26px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 240, 246, 0.91) 100%);
      border: 2.5px solid rgba(201, 24, 96, 0.30);
      box-shadow: 0 14px 34px rgba(72, 10, 36, 0.20), inset 0 1px 0 rgba(255, 255, 255, 0.96);
      padding: 18px 24px;
      z-index: 10;
      pointer-events: none;
    }
    .slide-card-header {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(90deg, #B81456 0%, #DF2E76 100%);
      color: #ffffff;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 19px;
      font-weight: 800;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      padding: 6px 16px;
      border-radius: 999px;
      margin-bottom: 12px;
      box-shadow: 0 4px 12px rgba(184, 20, 86, 0.28);
    }
    .slide-row {
      display: flex;
      align-items: center;
      gap: 12px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: #4A0D27;
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
      background: #FFE5F0;
      color: #B81456;
      border: 2px solid #F6A5C6;
    }
    .slide-badge-gold {
      background: #FFF4DC;
      color: #B56400;
      border: 2px solid #F5CA7B;
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
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(255, 241, 247, 0.93) 100%);
      border-left: 7px solid #C91860;
      border-top: 1.5px solid rgba(255, 255, 255, 0.96);
      border-right: 1.5px solid rgba(201, 24, 96, 0.25);
      border-bottom: 1.5px solid rgba(201, 24, 96, 0.25);
      border-radius: 18px;
      padding: 11px 22px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: #480B24;
      box-shadow: 0 10px 24px rgba(58, 10, 30, 0.18);
      width: fit-content;
      max-width: 785px;
    }
    .slide-pill-gold {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(255, 249, 236, 0.93) 100%);
      border-left: 7px solid #D47A08;
      color: #4A2400;
    }
"""


def svg_defs(prefix: str, light_x: int = 240) -> str:
    return f"""
      <defs>
        <linearGradient id="{prefix}-rose-fill" x1="0%" y1="0%" x2="14%" y2="100%">
          <stop offset="0%" stop-color="#FFF0F6" />
          <stop offset="25%" stop-color="#FF7DB2" />
          <stop offset="52%" stop-color="#C91860" />
          <stop offset="78%" stop-color="#FF97C1" />
          <stop offset="100%" stop-color="#6E0831" />
        </linearGradient>

        <linearGradient id="{prefix}-gold-fill" x1="0%" y1="0%" x2="12%" y2="100%">
          <stop offset="0%" stop-color="#FFFDF2" />
          <stop offset="25%" stop-color="#FFE173" />
          <stop offset="52%" stop-color="#DF840B" />
          <stop offset="78%" stop-color="#FFEC9E" />
          <stop offset="100%" stop-color="#8C4800" />
        </linearGradient>

        <linearGradient id="{prefix}-brand-deep" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#D41B67" />
          <stop offset="55%" stop-color="#9E0E49" />
          <stop offset="100%" stop-color="#5E0529" />
        </linearGradient>

        <filter id="{prefix}-silk-3d" x="-16%" y="-24%" width="132%" height="152%" color-interpolation-filters="sRGB">
          <feMorphology in="SourceAlpha" operator="dilate" radius="1.1" result="extrudeAlpha" />
          <feOffset in="extrudeAlpha" dx="1.2" dy="3.0" result="extrudeShift" />
          <feFlood flood-color="#540625" flood-opacity="0.78" result="extrudeColor" />
          <feComposite in="extrudeColor" in2="extrudeShift" operator="in" result="extrudeRim" />
          <feDropShadow in="SourceAlpha" dx="0" dy="6" stdDeviation="6" flood-color="#3B0419" flood-opacity="0.28" result="softShadow" />
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
          <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#3B0419" flood-opacity="0.24" />
        </filter>
      </defs>
    """


def write_act1(segs: dict, s01_top_safe: bool = True):
    # LT_S01 (0..5.50s) + LT_S02 (5.50..13.50s)
    s1_dur = segs["vo_01"]["shot_duration_s"]
    s2_st = segs["vo_02"]["shot_start_s"]
    s2_dur = segs["vo_02"]["shot_duration_s"]
    act_dur = round(s1_dur + s2_dur, 2)

    # If S01 head is high, place Hook cleanly in lower-left Face-Safe zone; if S01 head is below Y=460, top Y=306..402 is 100% open sky!
    if s01_top_safe:
        hook_block = f"""
    <div id="a1-t1-clip" class="clip float-stage" data-start="0.12" data-duration="{round(s1_dur - 0.24, 2)}" data-track-index="3" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a1t1")}
        <g id="a1-t1-badge" filter="url(#a1t1-clean-lift)">
          <text x="540" y="304" text-anchor="middle" class="upper-claim" font-size="27" fill="#B81456">CÀNG TRA TRIỆU CHỨNG TRÊN MẠNG</text>
        </g>
        <g id="a1-t1-hero">
          <text x="540" y="402" text-anchor="middle" class="satin-hero" font-size="80" fill="url(#a1t1-rose-fill)" filter="url(#a1t1-silk-3d)">Càng hoang mang?</text>
        </g>
      </svg>
    </div>"""
    else:
        hook_block = f"""
    <div id="a1-t1-clip" class="clip float-stage" data-start="0.12" data-duration="{round(s1_dur - 0.24, 2)}" data-track-index="3" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a1t1")}
        <g id="a1-t1-badge" filter="url(#a1t1-clean-lift)">
          <text x="468" y="1185" text-anchor="middle" class="upper-claim" font-size="26" fill="#B81456">TỰ TRA TRIỆU CHỨNG TRÊN MẠNG</text>
        </g>
        <g id="a1-t1-hero">
          <text x="468" y="1278" text-anchor="middle" class="satin-hero" font-size="74" fill="url(#a1t1-rose-fill)" filter="url(#a1t1-silk-3d)">Càng hoang mang?</text>
        </g>
      </svg>
    </div>"""

    sl1_st = round(s2_st + 0.16, 2)
    sl1_dur = round(s2_dur - 0.30, 2)

    html = f"""<template>
  <style>{SHARED_TYPO_CSS}</style>
  <div id="root" data-composition-id="act1-hook" data-width="1080" data-height="1920" data-start="0" data-duration="{act_dur}">
    <div id="a1-rig-01" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a1-v01" class="clip bg-video" src="assets/videos/LT_S01.mp4" data-start="0" data-duration="{s1_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a1-rig-02" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a1-v02" class="clip bg-video" src="assets/videos/LT_S02.mp4" data-start="{s2_st}" data-duration="{s2_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
{hook_block}

    <!-- SLIDE OVERLAY #1 (Shot 2): 3 Nỗi lo 8 tiếng văn phòng (Face-Safe Lower-Left X=64..648, Y=1030..1325) -->
    <div id="a1-slide-office" class="clip slide-card" style="top: 1032px; width: 584px;" data-start="{sl1_st}" data-duration="{sl1_dur}" data-track-index="4" data-layout-ignore>
      <div class="slide-card-header">💼 Nỗi lo 8 tiếng văn phòng</div>
      <div id="a1-r1" class="slide-row"><span class="slide-badge-dot">1</span> Cảm giác ẩm ướt, bí bách</div>
      <div id="a1-r2" class="slide-row"><span class="slide-badge-dot">2</span> Ra dịch nhầy nhiều bất thường</div>
      <div id="a1-r3" class="slide-row" style="color:#B81456;"><span class="slide-badge-dot">3</span> Mùi khó nói làm mất tự tin</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a1-rig-01", {{ scale: 1.00 }}, {{ scale: 1.05, duration: {s1_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a1-rig-02", {{ scale: 1.05 }}, {{ scale: 1.00, duration: {s2_dur}, ease: "none", immediateRender: false }}, {s2_st});

    tl.fromTo("#a1-t1-badge", {{ opacity: 0, y: -14, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.24, ease: "power3.out" }}, 0.14)
      .fromTo("#a1-t1-hero", {{ opacity: 0, scale: 0.90, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.4)" }}, 0.24)
      .fromTo("#a1t1-light", {{ attr: {{ x: 120 }} }}, {{ attr: {{ x: 940 }}, duration: 1.10, ease: "power2.inOut" }}, 0.40)
      .to("#a1-t1-clip", {{ opacity: 0, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, {round(s1_dur - 0.34, 2)});

    tl.fromTo("#a1-slide-office", {{ opacity: 0, x: -70, scale: 0.94, filter: "blur(14px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.3)" }}, {sl1_st})
      .fromTo("#a1-r1", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22, ease: "power2.out" }}, {round(sl1_st + 0.14, 2)})
      .fromTo("#a1-r2", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22, ease: "power2.out" }}, {round(sl1_st + 0.72, 2)})
      .fromTo("#a1-r3", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22, ease: "power2.out" }}, {round(sl1_st + 1.32, 2)})
      .to("#a1-slide-office", {{ opacity: 0, x: -40, filter: "blur(12px)", duration: 0.20, ease: "power2.in" }}, {round(sl1_st + sl1_dur - 0.22, 2)});

    window.__timelines["act1-hook"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act1-hook.html").write_text(html, encoding="utf-8")
    return act_dur


def write_act2(segs: dict):
    # LT_S03 (13.50..21.00s) + LT_S04 (21.00..28.25s)
    act_st = segs["vo_03"]["shot_start_s"]
    s3_dur = segs["vo_03"]["shot_duration_s"]
    s4_local = round(segs["vo_04"]["shot_start_s"] - act_st, 2)
    s4_dur = segs["vo_04"]["shot_duration_s"]
    act_dur = round(s3_dur + s4_dur, 2)

    html = f"""<template>
  <style>{SHARED_TYPO_CSS}</style>
  <div id="root" data-composition-id="act2-insight" data-width="1080" data-height="1920" data-start="0" data-duration="{act_dur}">
    <div id="a2-rig-03" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a2-v03" class="clip bg-video" src="assets/videos/LT_S03.mp4" data-start="0" data-duration="{s3_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a2-rig-04" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a2-v04" class="clip bg-video" src="assets/videos/LT_S04.mp4" data-start="{s4_local}" data-duration="{s4_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>

    <!-- Shot 3 (CGI Metaphor — No human face!): Top 3D Title + Slide Overlay #2 -->
    <div id="a2-t3-clip" class="clip float-stage" data-start="0.15" data-duration="{round(s3_dur - 0.30, 2)}" data-track-index="3" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a2t3")}
        <text id="a2-t3-top" x="540" y="314" text-anchor="middle" class="upper-claim" font-size="27" fill="#B81456" filter="url(#a2t3-clean-lift)">VÌ SAO CHỈ CHE GIẤU BÊN NGOÀI</text>
        <text id="a2-t3-hero" x="540" y="408" text-anchor="middle" class="satin-hero" font-size="76" fill="url(#a2t3-gold-fill)" filter="url(#a2t3-silk-3d)">Dễ quay trở lại?</text>
      </svg>
    </div>

    <!-- SLIDE OVERLAY #2 (Shot 3): 2 Staggered Insight Pills -->
    <div id="a2-slide-why" class="clip slide-pill-stack" style="top: 1090px;" data-start="0.55" data-duration="{round(s3_dur - 0.80, 2)}" data-track-index="4" data-layout-ignore>
      <div id="a2-wp1" class="slide-pill"><span class="slide-badge-dot">!</span> Vùng nhạy cảm mất cân bằng độ ẩm &amp; pH</div>
      <div id="a2-wp2" class="slide-pill slide-pill-gold"><span class="slide-badge-dot slide-badge-gold">✓</span> Cần làm sạch êm dịu &amp; nâng niu từ gốc</div>
    </div>

    <!-- SLIDE OVERLAY #3 (Shot 4 — Chị Hằng cầm LT Plus ở X=590..940: ZERO top text! Compact Pill X=64..548, Y=1175..1315 -> 0% chạm hộp!) -->
    <div id="a2-slide-choice" class="clip slide-pill-stack" style="top: 1180px;" data-start="{round(s4_local + 0.22, 2)}" data-duration="{round(s4_dur - 0.44, 2)}" data-track-index="3" data-layout-ignore>
      <div id="a2-cp1" class="slide-pill" style="max-width: 486px; line-height: 1.32;"><span class="slide-badge-dot">♥</span> Đồng hành cùng<br/>Viên Đặt LT Plus Hằng Thu</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a2-rig-03", {{ scale: 1.00 }}, {{ scale: 1.06, duration: {s3_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a2-rig-04", {{ scale: 1.05 }}, {{ scale: 1.00, duration: {s4_dur}, ease: "none", immediateRender: false }}, {s4_local});

    tl.fromTo("#a2-t3-top", {{ opacity: 0, y: -12, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.24, ease: "power3.out" }}, 0.16)
      .fromTo("#a2-t3-hero", {{ opacity: 0, scale: 0.92, filter: "blur(12px)" }}, {{ opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, 0.28)
      .to("#a2-t3-clip", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s3_dur - 0.36, 2)});

    tl.fromTo("#a2-wp1", {{ opacity: 0, x: -60, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.2)" }}, 0.58)
      .fromTo("#a2-wp2", {{ opacity: 0, x: -60, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.2)" }}, 1.45)
      .to("#a2-slide-why", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s3_dur - 0.45, 2)});

    tl.fromTo("#a2-cp1", {{ opacity: 0, y: 24, scale: 0.94, filter: "blur(12px)" }}, {{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, {round(s4_local + 0.25, 2)})
      .to("#a2-slide-choice", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s4_local + s4_dur - 0.42, 2)});

    window.__timelines["act2-insight"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act2-insight.html").write_text(html, encoding="utf-8")
    return act_st, act_dur


def write_act3(segs: dict):
    # LT_S05 (Packshot Studio 28.25..35.75s) + LT_S06 (Botanical 35.75..44.25s)
    act_st = segs["vo_05"]["shot_start_s"]
    s5_dur = segs["vo_05"]["shot_duration_s"]
    s6_local = round(segs["vo_06"]["shot_start_s"] - act_st, 2)
    s6_dur = segs["vo_06"]["shot_duration_s"]
    act_dur = round(s5_dur + s6_dur, 2)

    html = f"""<template>
  <style>{SHARED_TYPO_CSS}</style>
  <div id="root" data-composition-id="act3-hero-demo" data-width="1080" data-height="1920" data-start="0" data-duration="{act_dur}">
    <div id="a3-rig-05" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a3-v05" class="clip bg-video" src="assets/videos/LT_S05.mp4" data-start="0" data-duration="{s5_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a3-rig-06" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a3-v06" class="clip bg-video" src="assets/videos/LT_S06.mp4" data-start="{s6_local}" data-duration="{s6_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>

    <!-- Shot 5 (Packshot in lower-middle Y=52..84% -> Upper sky Y=285..590px is 100% open!): Top Brand + Slide #4 -->
    <div id="a3-t5-clip" class="clip float-stage" data-start="0.14" data-duration="{round(s5_dur - 0.28, 2)}" data-track-index="3" data-layout-ignore>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a3t5")}
        <text id="a3-t5-sub" x="540" y="294" text-anchor="middle" class="upper-claim" font-size="26" fill="#B81456" filter="url(#a3t5-clean-lift)">VIÊN ĐẶT PHỤ KHOA THẢO DƯỢC</text>
        <text id="a3-t5-hero" x="540" y="388" text-anchor="middle" class="satin-hero" font-size="84" fill="url(#a3t5-rose-fill)" filter="url(#a3t5-silk-3d)">LT Plus Hằng Thu</text>
      </svg>
    </div>

    <!-- SLIDE OVERLAY #4 (Shot 5): 3 Tác động kép ở vùng sky phía trên hộp (Y=435..685px, X=64..664px — 0% chạm hộp dưới!) -->
    <div id="a3-slide-usp" class="clip slide-card" style="top: 432px; width: 610px;" data-start="0.52" data-duration="{round(s5_dur - 0.72, 2)}" data-track-index="4" data-layout-ignore>
      <div class="slide-card-header">✨ Tác động chăm sóc dịu êm</div>
      <div id="a3-u1" class="slide-row"><span class="slide-badge-dot">✓</span> Kháng khuẩn &amp; làm sạch dịch nhầy</div>
      <div id="a3-u2" class="slide-row"><span class="slide-badge-dot">✓</span> Khử mùi hôi khó chịu nhẹ nhàng</div>
      <div id="a3-u3" class="slide-row"><span class="slide-badge-dot slide-badge-gold">✓</span> Duy trì độ ẩm &amp; độ pH tự nhiên</div>
    </div>

    <!-- SLIDE OVERLAY #5 (Shot 6 — Botanical Macro): 4 Thảo dược & Acid Lactic Slide Card -->
    <div id="a3-slide-herb" class="clip slide-card" style="top: 292px; width: 650px;" data-start="{round(s6_local + 0.18, 2)}" data-duration="{round(s6_dur - 0.36, 2)}" data-track-index="3" data-layout-ignore>
      <div class="slide-card-header">🌿 Tinh túy thảo dược lành tính</div>
      <div id="a3-h1" class="slide-row"><span class="slide-badge-dot slide-badge-gold">1</span> Hoàng bá &amp; Kim ngân hoa: Kháng khuẩn</div>
      <div id="a3-h2" class="slide-row"><span class="slide-badge-dot slide-badge-gold">2</span> Trầu không &amp; Trà xanh: Sạch thoáng êm</div>
      <div id="a3-h3" class="slide-row"><span class="slide-badge-dot">3</span> Acid Lactic: Cân bằng pH sinh lý tự nhiên</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a3-rig-05", {{ scale: 1.00 }}, {{ scale: 1.06, duration: {s5_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a3-rig-06", {{ scale: 1.05 }}, {{ scale: 1.00, duration: {s6_dur}, ease: "none", immediateRender: false }}, {s6_local});

    tl.fromTo("#a3-t5-sub", {{ opacity: 0, y: -12, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.22 }}, 0.16)
      .fromTo("#a3-t5-hero", {{ opacity: 0, scale: 0.90, filter: "blur(12px)" }}, {{ opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.4)" }}, 0.26)
      .fromTo("#a3t5-light", {{ attr: {{ x: 110 }} }}, {{ attr: {{ x: 960 }}, duration: 1.25, ease: "power2.inOut" }}, 0.45)
      .to("#a3-t5-clip", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s5_dur - 0.34, 2)});

    tl.fromTo("#a3-slide-usp", {{ opacity: 0, x: -65, scale: 0.94, filter: "blur(14px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, 0.55)
      .fromTo("#a3-u1", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.20 }}, 0.72)
      .fromTo("#a3-u2", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.20 }}, 1.45)
      .fromTo("#a3-u3", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.20 }}, 2.20)
      .to("#a3-slide-usp", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s5_dur - 0.38, 2)});

    tl.fromTo("#a3-slide-herb", {{ opacity: 0, x: -65, scale: 0.94, filter: "blur(14px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, {round(s6_local + 0.20, 2)})
      .fromTo("#a3-h1", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(s6_local + 0.45, 2)})
      .fromTo("#a3-h2", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(s6_local + 1.35, 2)})
      .fromTo("#a3-h3", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(s6_local + 2.25, 2)})
      .to("#a3-slide-herb", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s6_local + s6_dur - 0.38, 2)});

    window.__timelines["act3-hero-demo"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act3-hero-demo.html").write_text(html, encoding="utf-8")
    return act_st, act_dur


def write_act4(segs: dict):
    # LT_S07 (Radiant Payoff 44.25..51.50s — ZERO top text over Chị Hằng's face! Lower-left Face-Safe Pill!)
    act_st = segs["vo_07"]["shot_start_s"]
    act_dur = segs["vo_07"]["shot_duration_s"]

    html = f"""<template>
  <style>{SHARED_TYPO_CSS}</style>
  <div id="root" data-composition-id="act4-payoff" data-width="1080" data-height="1920" data-start="0" data-duration="{act_dur}">
    <div id="a4-rig-07" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a4-v07" class="clip bg-video" src="assets/videos/LT_S07.mp4" data-start="0" data-duration="{act_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>

    <div id="a4-slide-payoff" class="clip slide-pill-stack" style="top: 1188px;" data-start="0.22" data-duration="{round(act_dur - 0.44, 2)}" data-track-index="3" data-layout-ignore>
      <div id="a4-pp1" class="slide-pill"><span class="slide-badge-dot">✨</span> Sạch thoáng êm ái từ bên trong</div>
      <div id="a4-pp2" class="slide-pill slide-pill-gold"><span class="slide-badge-dot slide-badge-gold">♥</span> Nhẹ nhõm, tự tin &amp; trọn vẹn hạnh phúc</div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a4-rig-07", {{ scale: 1.00 }}, {{ scale: 1.05, duration: {act_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a4-pp1", {{ opacity: 0, x: -55, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.25)" }}, 0.24)
      .fromTo("#a4-pp2", {{ opacity: 0, x: -55, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.25)" }}, 1.15)
      .to("#a4-slide-payoff", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(act_dur - 0.42, 2)});

    window.__timelines["act4-payoff"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act4-payoff.html").write_text(html, encoding="utf-8")
    return act_st, act_dur


def write_act6(segs: dict, total_dur: float):
    # LT_S08 (Brand End-Card Lockup 51.50..57.50s)
    # Chị Hằng on LEFT half -> Upper-Right Lockup + Lower Safe-Zone CTA Pill + Real Cutout Packshot Reinforcement!
    act_st = segs["vo_08"]["shot_start_s"]
    act_dur = round(total_dur - act_st, 2)

    html = f"""<template>
  <style>
    {SHARED_TYPO_CSS}
    .end-card-panel {{
      position: absolute;
      left: 442px;
      top: 768px;
      width: 432px;
      border-radius: 28px;
      background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 238, 246, 0.92) 100%);
      border: 2.5px solid rgba(201, 24, 96, 0.32);
      box-shadow: 0 16px 36px rgba(68, 8, 32, 0.24);
      padding: 18px 20px 16px 20px;
      text-align: center;
      z-index: 10;
      pointer-events: none;
    }}
    .end-packshot {{
      display: block;
      margin: 10px auto 0 auto;
      width: 286px;
      height: auto;
      filter: drop-shadow(0 12px 20px rgba(68, 8, 32, 0.24));
    }}
    .end-cta-box {{
      position: absolute;
      left: 64px;
      top: 1335px;
      width: 808px;
      background: linear-gradient(90deg, #B81456 0%, #E02C74 52%, #B81456 100%);
      color: #ffffff;
      border: 3px solid #FFE8A3;
      border-radius: 999px;
      padding: 16px 28px;
      text-align: center;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 29px;
      font-weight: 800;
      box-shadow: 0 14px 32px rgba(138, 12, 62, 0.38);
      z-index: 12;
    }}
    .legal-note {{
      position: absolute;
      left: 64px;
      top: 1452px;
      width: 808px;
      text-align: center;
      font-family: "BeVietnamSemiVN", sans-serif;
      font-size: 18px;
      font-weight: 600;
      color: #4A0D27;
      background: rgba(255, 255, 255, 0.88);
      border-radius: 12px;
      padding: 7px 14px;
      z-index: 12;
    }}
  </style>
  <div id="root" data-composition-id="act6-endcard" data-width="1080" data-height="1920" data-start="0" data-duration="{act_dur}">
    <div id="a6-rig-08" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a6-v08" class="clip bg-video" src="assets/videos/LT_S08.mp4" data-start="0" data-duration="{act_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>

    <!-- Lower-Right Brand End-Card Panel below shoulder level (X=442..874 <= 884px Safe Zone, Y=768..1298 -> 0% touching face/hair!) -->
    <div id="a6-panel" class="clip end-card-panel" data-start="0.12" data-duration="{round(act_dur - 0.12, 2)}" data-track-index="3" data-layout-ignore>
      <div style="font-family:'BeVietnamVN',sans-serif;font-size:19px;font-weight:800;color:#B81456;letter-spacing:0.04em;">VIÊN ĐẶT PHỤ KHOA</div>
      <div style="font-family:'FrauncesVN',Georgia,serif;font-size:58px;font-weight:900;color:#C91860;line-height:1.06;margin-top:2px;">LT Plus</div>
      <div style="font-family:'DancingVN',cursive;font-size:42px;font-weight:700;color:#C87406;line-height:1.08;">Hằng Thu Pharma</div>
      <div style="font-family:'BeVietnamVN',sans-serif;font-size:17px;font-weight:800;color:#5E0529;margin-top:6px;">SẠCH DỊCH NHẦY · KHỬ MÙI · GIỮ PH</div>
      <img id="a6-pack" class="end-packshot" src="assets/images/SP_LT_PLUS_COMBO_CUTOUT.png" alt="LT Plus Hằng Thu" />
    </div>

    <!-- Safe-Zone CTA Pill & Note (X=64..872 <= 884px, Y=1335..1512 <= 1545px!) -->
    <div id="a6-cta" class="clip end-cta-box" data-start="0.32" data-duration="{round(act_dur - 0.32, 2)}" data-track-index="5" data-layout-ignore>
      Nhắn ngay “LT PLUS” · Tư vấn riêng tư 1:1
    </div>
    <div id="a6-legal" class="clip legal-note" data-start="0.40" data-duration="{round(act_dur - 0.40, 2)}" data-track-index="6" data-layout-ignore>
      Hộp 15 viên thảo dược thiên nhiên · Chăm sóc dịu êm &amp; bảo mật cho phái đẹp
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a6-rig-08", {{ scale: 1.00 }}, {{ scale: 1.04, duration: {act_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a6-panel", {{ opacity: 0, x: 45, scale: 0.92, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.3)" }}, 0.14)
      .fromTo("#a6-pack", {{ opacity: 0, y: 18, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.30, ease: "back.out(1.35)" }}, 0.24)
      .fromTo("#a6-cta", {{ opacity: 0, y: 20, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.28, ease: "back.out(1.3)" }}, 0.34)
      .fromTo("#a6-legal", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.24 }}, 0.44);

    window.__timelines["act6-endcard"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "act6-endcard.html").write_text(html, encoding="utf-8")
    return act_st, act_dur


def write_captions(manifest: dict):
    # 100% CAPITALIZED FIRST LETTER ON EVERY SINGLE SUBTITLE CARD!
    # Strictly inside TikTok & Reels White Safe Zone: X=[62..874] <= 884px, Y=[1412..1524] <= 1545px!
    segs = {s["id"]: s for s in manifest["segments"]}

    def split_seg(seg_id, ratio, y1, y2, line1, line2):
        s = segs[seg_id]
        mid = round(s["start_s"] + s["duration_s"] * ratio, 2)
        return [
            (f"cap-{seg_id}a", s["start_s"], mid, y1, line1),
            (f"cap-{seg_id}b", round(mid + 0.03, 2), round(s["end_s"] + 0.10, 2), y2, line2),
        ]

    caps = []
    caps += split_seg("vo_01", 0.54, 1412, 1416, 'Càng âm thầm <span class="cap-kw">tra triệu chứng trên mạng,</span>', 'Chị càng thấy <span class="cap-kw">rối bời và hoang mang?</span>')
    caps += split_seg("vo_02", 0.52, 1416, 1416, 'Ngồi văn phòng 8 tiếng, <span class="cap-kw">ẩm ướt, ra dịch nhiều</span>', 'Hay mùi khó nói lấy đi <span class="cap-kw">sự tự tin của chị.</span>')
    caps += split_seg("vo_03", 0.52, 1412, 1412, 'Khi vùng nhạy cảm <span class="cap-kw">mất cân bằng tự nhiên,</span>', 'Chỉ che giấu bên ngoài <span class="cap-kw">rất dễ quay trở lại.</span>')
    caps += split_seg("vo_04", 0.48, 1424, 1424, 'Lắng nghe cơ thể để <span class="cap-kw">thương mình đúng cách,</span>', 'Chị chọn đồng hành cùng <span class="cap-kw">Viên Đặt LT Plus Hằng Thu.</span>')
    caps += split_seg("vo_05", 0.52, 1416, 1416, '<span class="cap-kw">LT Plus</span> hỗ trợ kháng khuẩn, sạch dịch nhầy,', 'Khử mùi hôi &amp; duy trì <span class="cap-kw">độ ẩm, pH tự nhiên.</span>')
    caps += split_seg("vo_06", 0.54, 1412, 1412, 'Hòa quyện <span class="cap-kw">Hoàng bá, Kim ngân hoa, Trầu không,</span>', 'Trà xanh &amp; Acid Lactic <span class="cap-kw">nâng niu lành tính.</span>')
    caps += split_seg("vo_07", 0.50, 1416, 1416, 'Cảm giác <span class="cap-kw">sạch thoáng, êm ái</span> từ bên trong,', 'Để chị luôn nhẹ nhõm &amp; <span class="cap-kw">trọn vẹn hạnh phúc.</span>')

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

    cap_end = segs["vo_08"]["shot_start_s"]
    html = f"""<template>
  <style>
    @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "PlayfairVNItalic"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
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
      color: #460922;
      paint-order: stroke fill;
      -webkit-text-stroke: 10px #ffffff;
      filter: drop-shadow(0 5px 12px rgba(48, 6, 24, 0.32));
      letter-spacing: -0.01em;
    }}
    .cap-kw {{
      color: #C91860;
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


def write_transitions(segs: dict):
    t1 = segs["vo_03"]["shot_start_s"]
    t_portal = segs["vo_05"]["shot_start_s"]
    t3 = segs["vo_07"]["shot_start_s"]
    t4 = segs["vo_08"]["shot_start_s"]

    html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
    .fx-clip {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
    .sun-flare {{
      position: absolute; inset: 0; opacity: 0;
      background: radial-gradient(
        ellipse at 52% 42%,
        rgba(255, 255, 255, 0.88) 0%,
        rgba(255, 230, 242, 0.74) 32%,
        rgba(232, 92, 148, 0.40) 60%,
        rgba(232, 92, 148, 0) 86%
      );
      mix-blend-mode: screen;
    }}
    .portal-ring {{
      position: absolute;
      left: 50%; top: 50%;
      width: 920px; height: 920px;
      margin-left: -460px; margin-top: -460px;
      opacity: 0; border-radius: 50%;
      border: 66px solid #FFB3D1;
      box-shadow:
        inset 0 0 52px rgba(255, 250, 220, 0.94),
        0 0 72px rgba(201, 24, 96, 0.84);
    }}
  </style>

  <div id="root" data-composition-id="tvc-transitions" data-width="1080" data-height="1920">
    <div id="fx-fl1-clip" class="clip fx-clip" data-start="{round(t1 - 0.25, 3)}" data-duration="0.5" data-track-index="1" data-layout-ignore>
      <div id="fx-fl1" class="sun-flare"></div>
    </div>
    <div id="fx-portal-clip" class="clip fx-clip" data-start="{round(t_portal - 0.375, 3)}" data-duration="0.75" data-track-index="3" data-layout-allow-overflow data-layout-ignore>
      <div id="fx-portal" class="portal-ring"></div>
      <div id="fx-fl2" class="sun-flare"></div>
    </div>
    <div id="fx-fl3-clip" class="clip fx-clip" data-start="{round(t3 - 0.25, 3)}" data-duration="0.5" data-track-index="2" data-layout-ignore>
      <div id="fx-fl3" class="sun-flare"></div>
    </div>
    <div id="fx-fl4-clip" class="clip fx-clip" data-start="{round(t4 - 0.25, 3)}" data-duration="0.5" data-track-index="1" data-layout-ignore>
      <div id="fx-fl4" class="sun-flare"></div>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    [
      {{ id: "#fx-fl1", st: {round(t1 - 0.25, 3)}, pk: {t1} }},
      {{ id: "#fx-fl3", st: {round(t3 - 0.25, 3)}, pk: {t3} }},
      {{ id: "#fx-fl4", st: {round(t4 - 0.25, 3)}, pk: {t4} }}
    ].forEach((f) => {{
      tl.fromTo(f.id, {{ opacity: 0, scale: 0.96 }}, {{ opacity: 0.68, scale: 1.04, duration: 0.25, ease: "sine.in" }}, f.st)
        .to(f.id, {{ opacity: 0, scale: 1.10, duration: 0.25, ease: "sine.out" }}, f.pk);
    }});

    tl.fromTo("#fx-portal", {{ opacity: 0, scale: 0.35, rotation: 0 }}, {{ opacity: 1, scale: 1.15, rotation: 95, duration: 0.375, ease: "power2.in" }}, {round(t_portal - 0.375, 3)})
      .to("#fx-portal", {{ opacity: 0, scale: 2.85, rotation: 190, duration: 0.375, ease: "power3.out" }}, {t_portal});

    tl.fromTo("#fx-fl2", {{ opacity: 0 }}, {{ opacity: 0.84, duration: 0.375, ease: "sine.in" }}, {round(t_portal - 0.375, 3)})
      .to("#fx-fl2", {{ opacity: 0, duration: 0.375, ease: "sine.out" }}, {t_portal});

    window.__timelines["tvc-transitions"] = tl;
  </script>
</template>
"""
    (COMP_DIR / "tvc-transitions.html").write_text(html, encoding="utf-8")


def write_root_index(manifest: dict, acts: dict, cap_end: float):
    total_dur = manifest["total_duration_s"]
    segs = {s["id"]: s for s in manifest["segments"]}
    portal_t = segs["vo_05"]["shot_start_s"]

    vo_tags = []
    for idx, s in enumerate(manifest["segments"]):
        trk = 5 if (idx % 2 == 0) else 6
        vol = "1.32" if idx in (3, 4, 7) else "1.30"
        vo_tags.append(
            f'      <audio id="{s["id"].replace("_", "-")}" class="clip" src="assets/audio/{s["id"]}.wav" '
            f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{trk}" '
            f'data-volume="{vol}" data-fade-in="0.035" data-fade-out="0.055" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        )

    bgm1_dur = round(portal_t + 0.15, 2)
    bgm2_st = round(portal_t - 0.10, 2)
    bgm2_dur = round(total_dur - bgm2_st, 2)
    outro_swell_t = round(bgm2_dur - 1.05, 2)

    s2_t = segs["vo_02"]["shot_start_s"]
    s3_t = segs["vo_03"]["shot_start_s"]
    s4_t = segs["vo_04"]["shot_start_s"]
    s6_t = segs["vo_06"]["shot_start_s"]
    s7_t = segs["vo_07"]["shot_start_s"]
    s8_t = segs["vo_08"]["shot_start_s"]

    html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Viên Đặt LT Plus Hằng Thu — Ngày 01 USP TVC (9:16, 24fps)</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "FrauncesVN"; src: url("assets/fonts/Fraunces-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
      @font-face {{ font-family: "PlayfairVN"; src: url("assets/fonts/PlayfairDisplay-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
      @font-face {{ font-family: "PlayfairVNItalic"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; font-display: block; }}
      @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
      @font-face {{ font-family: "BeVietnamSemiVN"; src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype"); font-weight: 600; font-display: block; }}
      @font-face {{ font-family: "DancingVN"; src: url("assets/fonts/DancingScript-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #2C0918; font-family: sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .captions-host {{ position: absolute; inset: 0; z-index: 12; pointer-events: none; }}
      .transitions-host {{ position: absolute; inset: 0; z-index: 18; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total_dur}" data-width="1080" data-height="1920" data-fps="24">
      <div id="act1-hook" class="scene-host" data-composition-id="act1-hook" data-composition-src="compositions/act1-hook.html" data-start="0" data-duration="{acts['a1'][1]}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act2-insight" class="scene-host" data-composition-id="act2-insight" data-composition-src="compositions/act2-insight.html" data-start="{acts['a2'][0]}" data-duration="{acts['a2'][1]}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act3-hero-demo" class="scene-host" data-composition-id="act3-hero-demo" data-composition-src="compositions/act3-hero-demo.html" data-start="{acts['a3'][0]}" data-duration="{acts['a3'][1]}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act4-payoff" class="scene-host" data-composition-id="act4-payoff" data-composition-src="compositions/act4-payoff.html" data-start="{acts['a4'][0]}" data-duration="{acts['a4'][1]}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act6-endcard" class="scene-host" data-composition-id="act6-endcard" data-composition-src="compositions/act6-endcard.html" data-start="{acts['a6'][0]}" data-duration="{acts['a6'][1]}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <div id="captions-track" class="captions-host" data-composition-id="captions-track" data-composition-src="compositions/captions-track.html" data-start="0" data-duration="{cap_end}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="tvc-transitions" class="transitions-host" data-composition-id="tvc-transitions" data-composition-src="compositions/tvc-transitions.html" data-start="0" data-duration="{total_dur}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

{chr(10).join(vo_tags)}

      <!-- Two-Part Harmonic C-Major Commercial BGM -->
      <audio id="bgm-warm-intro" class="clip" src="assets/audio/bgm_warm_fretless.mp3" data-start="0" data-duration="{bgm1_dur}" data-media-start="0" data-track-index="7" data-fade-in="0.18" data-fade-out="0.45" data-fx-chain="{{&quot;version&quot;:1,&quot;nodes&quot;:[{{&quot;type&quot;:&quot;gain&quot;,&quot;id&quot;:&quot;bgain1&quot;,&quot;label&quot;:&quot;Level match&quot;,&quot;params&quot;:{{&quot;gain&quot;:7.0}}}},{{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;bhp1&quot;,&quot;label&quot;:&quot;Clean low end&quot;,&quot;params&quot;:{{&quot;frequency&quot;:75}}}},{{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;bcarve1&quot;,&quot;label&quot;:&quot;Voice pocket&quot;,&quot;params&quot;:{{&quot;frequency&quot;:2300,&quot;gain&quot;:-3.8,&quot;q&quot;:0.85}}}},{{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;blim1&quot;,&quot;params&quot;:{{&quot;limit&quot;:-2.5}}}}]}}" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.56}},{{&quot;t&quot;:0.22,&quot;v&quot;:0.31}},{{&quot;t&quot;:{round(bgm1_dur - 0.55, 2)},&quot;v&quot;:0.32}},{{&quot;t&quot;:{bgm1_dur},&quot;v&quot;:0.0}}]}}]}}"></audio>
      <audio id="bgm-bright-hero" class="clip" src="assets/audio/bgm_bright_riley.mp3" data-start="{bgm2_st}" data-duration="{bgm2_dur}" data-media-start="0" data-track-index="8" data-fade-in="0.20" data-fade-out="0.65" data-fx-chain="{{&quot;version&quot;:1,&quot;nodes&quot;:[{{&quot;type&quot;:&quot;gain&quot;,&quot;id&quot;:&quot;bgain2&quot;,&quot;label&quot;:&quot;Level match&quot;,&quot;params&quot;:{{&quot;gain&quot;:6.6}}}},{{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;bhp2&quot;,&quot;label&quot;:&quot;Clean low end&quot;,&quot;params&quot;:{{&quot;frequency&quot;:80}}}},{{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;bcarve2&quot;,&quot;label&quot;:&quot;Voice pocket&quot;,&quot;params&quot;:{{&quot;frequency&quot;:2400,&quot;gain&quot;:-3.8,&quot;q&quot;:0.85}}}},{{&quot;type&quot;:&quot;highshelf&quot;,&quot;id&quot;:&quot;bair2&quot;,&quot;label&quot;:&quot;Bright sheen&quot;,&quot;params&quot;:{{&quot;frequency&quot;:7500,&quot;gain&quot;:1.3}}}},{{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;blim2&quot;,&quot;params&quot;:{{&quot;limit&quot;:-2.5}}}}]}}" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.58}},{{&quot;t&quot;:0.35,&quot;v&quot;:0.34}},{{&quot;t&quot;:{round(outro_swell_t - 0.20, 2)},&quot;v&quot;:0.35}},{{&quot;t&quot;:{outro_swell_t},&quot;v&quot;:0.74}},{{&quot;t&quot;:{bgm2_dur},&quot;v&quot;:0.74}}]}}]}}"></audio>

      <!-- Frame-Synced Tactile Studio Micro-SFX (-19dB clean, Disjoint Tracks 9-12) -->
      <audio id="sfx-w1" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="0.06" data-duration="0.50" data-track-index="9" data-volume="0.20" data-fade-out="0.12"></audio>
      <audio id="sfx-w2" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{round(s2_t + 0.08, 2)}" data-duration="0.50" data-track-index="9" data-volume="0.19" data-fade-out="0.12"></audio>
      <audio id="sfx-w3" class="clip" src="assets/audio/sfx_whoosh_transition.mp3" data-start="{round(s3_t - 0.08, 2)}" data-duration="0.55" data-track-index="9" data-volume="0.19" data-fade-out="0.14"></audio>
      <audio id="sfx-portal" class="clip" src="assets/audio/sfx_whoosh_cinematic.mp3" data-start="{round(portal_t - 1.20, 2)}" data-duration="2.60" data-media-start="1.00" data-track-index="9" data-volume="0.20" data-fade-in="0.25" data-fade-out="0.45"></audio>
      <audio id="sfx-w6" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{round(s6_t + 0.10, 2)}" data-duration="0.50" data-track-index="9" data-volume="0.19" data-fade-out="0.12"></audio>
      <audio id="sfx-w7" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{round(s7_t + 0.12, 2)}" data-duration="0.50" data-track-index="9" data-volume="0.19" data-fade-out="0.12"></audio>
      <audio id="sfx-w8" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{round(s8_t - 0.06, 2)}" data-duration="0.55" data-track-index="9" data-volume="0.21" data-fade-out="0.12"></audio>

      <audio id="sfx-p1" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="0.24" data-duration="0.55" data-track-index="10" data-volume="0.21" data-fade-out="0.12"></audio>
      <audio id="sfx-p2" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(s2_t + 0.24, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.19" data-fade-out="0.12"></audio>
      <audio id="sfx-c2a" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s2_t + 0.88, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c2b" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s2_t + 1.48, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-p4" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(s4_t + 0.25, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.21" data-fade-out="0.12"></audio>
      <audio id="sfx-p5" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(portal_t + 0.28, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>
      <audio id="sfx-c5a" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(portal_t + 1.45, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c5b" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(portal_t + 2.20, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c6a" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s6_t + 0.45, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c6b" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s6_t + 1.35, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c6c" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s6_t + 2.25, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.25" data-fade-out="0.08"></audio>
      <audio id="sfx-p8" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(s8_t + 0.34, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>

      <audio id="sfx-ch4" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="{round(s4_t + 0.22, 2)}" data-duration="2.20" data-track-index="11" data-volume="0.52" data-fade-out="0.45"></audio>
      <audio id="sfx-sp5" class="clip" src="assets/audio/sfx_sparkle_shine.mp3" data-start="{round(portal_t - 0.02, 2)}" data-duration="1.70" data-track-index="11" data-volume="0.24" data-fade-out="0.35"></audio>
      <audio id="sfx-sh6" class="clip" src="assets/audio/sfx_crystal_shimmer.mp3" data-start="{round(s6_t + 0.30, 2)}" data-duration="2.10" data-media-start="0.35" data-track-index="11" data-volume="0.60" data-fade-in="0.08" data-fade-out="0.45"></audio>
      <audio id="sfx-ch8" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="{round(s8_t + 0.12, 2)}" data-duration="2.20" data-track-index="11" data-volume="0.58" data-fade-out="0.45"></audio>

      <audio id="sfx-cta8" class="clip" src="assets/audio/sfx_notification_cta.mp3" data-start="{round(s8_t + 0.55, 2)}" data-duration="2.10" data-track-index="12" data-volume="0.19" data-fade-out="0.40"></audio>
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


def main(s01_top_safe: bool = True):
    COMP_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BRAND_KIT / "products_cutout_png" / "SP_LT_PLUS_COMBO_CUTOUT.png", IMG_DIR / "SP_LT_PLUS_COMBO_CUTOUT.png")
    shutil.copy2(BRAND_KIT / "logos_png" / "ht_logo_official.png", IMG_DIR / "ht_logo_official.png")

    manifest = json.loads(VO_MANIFEST_PATH.read_text(encoding="utf-8"))
    segs = {s["id"]: s for s in manifest["segments"]}

    a1_dur = write_act1(segs, s01_top_safe=s01_top_safe)
    a2 = write_act2(segs)
    a3 = write_act3(segs)
    a4 = write_act4(segs)
    a6 = write_act6(segs, manifest["total_duration_s"])
    cap_end = write_captions(manifest)
    write_transitions(segs)
    write_root_index(manifest, {"a1": (0, a1_dur), "a2": a2, "a3": a3, "a4": a4, "a6": a6}, cap_end)
    print(f"[HYPERFRAMES D01 BUILT] {HF_DIR / 'index.html'} (total={manifest['total_duration_s']}s @ 24fps, s01_top_safe={s01_top_safe})")


if __name__ == "__main__":
    import sys as _sys
    top_ok = ("--s01-low" not in _sys.argv)
    main(s01_top_safe=top_ok)
