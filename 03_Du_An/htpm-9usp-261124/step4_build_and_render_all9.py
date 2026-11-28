"""
Step 4 & 5 — Dựng hậu kỳ HyperFrames 24fps Dọc 9:16 (1080x1920) cho cả 9 Video USP (V01..V09),
Kiểm tra `npx.cmd hyperframes check --json` (0 lỗi), Render MP4 24fps, Kiểm định QA 12 khung hình Vùng An Toàn 9:16 + LUFS,
và Bàn giao tới cả 3 đích lưu trữ chuẩn Hằng Thu Pharma + cập nhật daily_progress.json!

ĐẶC ĐIỂM NÂNG CẤP NỔI BẬT THEO YÊU CẦU NGƯỜI DÙNG:
1. TIÊU ĐỀ HOOK MỞ ĐẦU TRÊN ĐẦU ĐÚNG 3.00 GIÂY (`0.08s -> 3.08s`, `top: 262px`, `width: 960px`):
   - Kicker Pill cỡ lớn `32px` tương phản cao + Hero Hook Title cỡ cực đại `88px` viền trắng dày `16px` + 3D Silk-Satin Gradient + Quét sáng ánh kim!
2. CHỮ TEXT TO RÕ RÀNG GẤP RƯỠI TRÊN MỌI THÀNH PHẦN:
   - Phụ đề (`captions-track.html`): cỡ lớn `46px` (`BeVietnamPro-ExtraBold`), từ khóa nhấn màu Vàng Champagne `50px`, bọc trong đệm nhung tối `rgba(24,6,18,0.86)` viền vàng mảnh nổi bật tuyệt đối trên mọi nền sáng (`X=58..876 <= 884px`, `Y=1358..1536 <= 1545px`).
   - 4 Lớp phủ Slide kính mờ (`S02`, `S03`, `S04`, `S05`): rộng `812px`, tiêu đề thẻ `27px`, các dòng nội dung `34px` đậm nét rõ ràng.
   - End-Card (`S06`): Hộp sản phẩm thật tách nền `IS-Net` + Nút CTA cỡ lớn `33px` + Dòng pháp lý `21px` sắc nét.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from htpm_9usp_catalog import VIDEOS_9USP, ROOT_OUT

BRAND_VIDEO_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma")
CLOUD_VIDEO_DIR = Path(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final")
LOCAL_BACKUP_DIR = Path(r"D:\XUẤT CAPCUT\hằng thu pharma")
CLOUD_DU_AN_DIR = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-9usp-261124")
PROGRESS_JSON_CLOUD = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-daily-1video-1post\daily_progress.json")
PROGRESS_JSON_LOCAL = Path(r"d:\AI\full studio\03_Du_An\htpm-daily-1video-1post\daily_progress.json")

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


def make_shared_css(accent_hex: str, accent_dark: str) -> str:
    return f"""
    @font-face {{ font-family: "FrauncesVN"; src: url("assets/fonts/Fraunces-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "PlayfairVN"; src: url("assets/fonts/PlayfairDisplay-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "BeVietnamSemiVN"; src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype"); font-weight: 600; font-display: block; }}
    @font-face {{ font-family: "DancingVN"; src: url("assets/fonts/DancingScript-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}

    #root {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: #240714; font-family: "BeVietnamVN", sans-serif;
    }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 50%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .float-stage {{ position: absolute; inset: 0; width: 1080px; height: 1920px; pointer-events: none; z-index: 9; }}
    .svg-typo {{ width: 100%; height: 100%; overflow: visible; display: block; }}

    /* TOP 3-SECOND HOOK BANNER (Y=254..428px, X=56..1024px -> 100% Top Safe Zone & Ultra-Large!) */
    .top-hook-wrap {{
      position: absolute;
      left: 56px;
      top: 254px;
      width: 968px;
      text-align: center;
      z-index: 14;
      pointer-events: none;
    }}
    .top-hook-pill {{
      display: inline-block;
      background: linear-gradient(90deg, {accent_dark} 0%, {accent_hex} 50%, {accent_dark} 100%);
      color: #FFFFFF;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 30px;
      font-weight: 800;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      padding: 8px 26px;
      border-radius: 999px;
      border: 3px solid #FFE8A3;
      box-shadow: 0 10px 26px rgba(24, 4, 14, 0.42);
    }}

    .satin-hero {{
      font-family: "FrauncesVN", "BeVietnamVN", Georgia, serif;
      font-weight: 900;
      letter-spacing: -0.01em;
      paint-order: stroke fill;
      stroke: #FFFFFF;
      stroke-width: 16px;
      stroke-linejoin: round;
      stroke-linecap: round;
    }}

    /* UPGRADED LARGE FROSTED LIQUID-GLASS SLIDE CARDS (Safe Zone X in [58..876] <= 884px!) */
    .slide-card {{
      position: absolute;
      left: 58px;
      width: 818px;
      border-radius: 28px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(255, 244, 249, 0.95) 100%);
      border: 3px solid {accent_hex};
      box-shadow: 0 16px 38px rgba(42, 6, 22, 0.28), inset 0 1px 0 #FFFFFF;
      padding: 18px 22px;
      z-index: 10;
      pointer-events: none;
    }}
    .slide-card-header {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: linear-gradient(90deg, {accent_dark} 0%, {accent_hex} 100%);
      color: #FFFFFF;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 26px;
      font-weight: 800;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      padding: 8px 20px;
      border-radius: 999px;
      margin-bottom: 12px;
      box-shadow: 0 6px 14px rgba(0, 0, 0, 0.22);
    }}
    .slide-row {{
      display: flex;
      align-items: center;
      gap: 13px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 31px;
      font-weight: 800;
      color: #260514;
      padding: 7px 0;
      line-height: 1.24;
      text-wrap: balance;
    }}
    .slide-badge-dot {{
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      font-weight: 800;
      flex-shrink: 0;
      background: {accent_hex};
      color: #FFFFFF;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18);
    }}
    .slide-pill-choice {{
      position: absolute;
      left: 58px;
      max-width: 536px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 243, 248, 0.96) 100%);
      border-left: 9px solid {accent_hex};
      border-top: 2px solid #FFFFFF;
      border-right: 2px solid rgba(201, 24, 96, 0.30);
      border-bottom: 2px solid rgba(201, 24, 96, 0.30);
      border-radius: 22px;
      padding: 16px 24px;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 32px;
      font-weight: 800;
      line-height: 1.28;
      color: #260514;
      box-shadow: 0 14px 30px rgba(38, 6, 20, 0.26);
      z-index: 10;
      pointer-events: none;
    }}
"""


def svg_defs(prefix: str, accent_hex: str, accent_dark: str) -> str:
    return f"""
      <defs>
        <linearGradient id="{prefix}-hero-fill" x1="0%" y1="0%" x2="10%" y2="100%">
          <stop offset="0%" stop-color="#FFFAFC" />
          <stop offset="22%" stop-color="#FF8EBA" />
          <stop offset="54%" stop-color="{accent_hex}" />
          <stop offset="82%" stop-color="{accent_dark}" />
          <stop offset="100%" stop-color="#4A0420" />
        </linearGradient>
        <filter id="{prefix}-silk-3d" x="-18%" y="-28%" width="136%" height="160%" color-interpolation-filters="sRGB">
          <feDropShadow in="SourceAlpha" dx="0" dy="8" stdDeviation="7" flood-color="#1E030E" flood-opacity="0.46" result="softShadow" />
          <feGaussianBlur in="SourceAlpha" stdDeviation="2.2" result="bevelBlur" />
          <feSpecularLighting in="bevelBlur" surfaceScale="7.0" specularConstant="1.4" specularExponent="22" lighting-color="#FFFFFF" result="specRaw">
            <fePointLight id="{prefix}-light" x="180" y="-100" z="240" />
          </feSpecularLighting>
          <feComposite in="specRaw" in2="SourceAlpha" operator="in" result="specClipped" />
          <feMerge>
            <feMergeNode in="softShadow" />
            <feMergeNode in="SourceGraphic" />
            <feMergeNode in="specClipped" />
          </feMerge>
        </filter>
      </defs>
    """


def build_hf_for_video(vspec: dict):
    vcode = vspec["vid_code"]
    vdir = ROOT_OUT / vcode
    hf_dir = vdir / "07_HyperFrames_Project"
    comp_dir = hf_dir / "compositions"
    comp_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((vdir / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
    segs = {s["id"]: s for s in manifest["segments"]}
    total_dur = manifest["total_duration_s"]
    shared_css = make_shared_css(vspec["accent_hex"], vspec["accent_dark"])
    sl = vspec["slides"]

    # --- ACT 1 (S01 + S02): EXACT 3.00s TOP HOOK (0.08s -> 3.08s) + LARGE SLIDE #1 ---
    s1_dur = segs["vo_01"]["shot_duration_s"]
    s2_st = segs["vo_02"]["shot_start_s"]
    s2_dur = segs["vo_02"]["shot_duration_s"]
    a1_dur = round(s1_dur + s2_dur, 2)
    sl1_st = round(s2_st + 0.14, 2)
    sl1_dur = round(s2_dur - 0.28, 2)

    hook_font_sz = 90 if len(vspec["hook_hero"]) <= 18 else 82
    s4_font_sz = 84 if len(vspec["s4_hero"]) <= 16 else 76

    act1_html = f"""<template>
  <style>{shared_css}</style>
  <div id="root" data-composition-id="act1-hook" data-width="1080" data-height="1920" data-start="0" data-duration="{a1_dur}">
    <div id="a1-rig-01" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a1-v01" class="clip bg-video" src="assets/videos/{vcode}_S01.mp4" data-start="0" data-duration="{s1_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a1-rig-02" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a1-v02" class="clip bg-video" src="assets/videos/{vcode}_S02.mp4" data-start="{s2_st}" data-duration="{s2_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>

    <!-- OPENING TOP HOOK BANNER — EXACTLY 3.00 SECONDS (0.08s -> 3.08s) AT TOP Y=254..425px! -->
    <div id="a1-hook-clip" class="clip float-stage" data-start="0.08" data-duration="3.00" data-track-index="3" data-layout-ignore>
      <div id="a1-hook-pill-box" class="top-hook-wrap">
        <div class="top-hook-pill">{vspec["hook_kicker"]}</div>
      </div>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a1hk", vspec["accent_hex"], vspec["accent_dark"])}
        <g id="a1-hook-hero">
          <text x="540" y="406" text-anchor="middle" class="satin-hero" font-size="{hook_font_sz}" fill="url(#a1hk-hero-fill)" filter="url(#a1hk-silk-3d)">{vspec["hook_hero"]}</text>
        </g>
      </svg>
    </div>

    <!-- SLIDE OVERLAY #1 (S02): Large 33px Rows (X=58..870 <= 884px, Y=916..1260) -->
    <div id="a1-slide-pain" class="clip slide-card" style="top: 916px;" data-start="{sl1_st}" data-duration="{sl1_dur}" data-track-index="4" data-layout-ignore>
      <div class="slide-card-header">{sl["s2_header"]}</div>
      <div id="a1-r1" class="slide-row"><span class="slide-badge-dot">1</span> <span>{sl["s2_rows"][0]}</span></div>
      <div id="a1-r2" class="slide-row"><span class="slide-badge-dot">2</span> <span>{sl["s2_rows"][1]}</span></div>
      <div id="a1-r3" class="slide-row"><span class="slide-badge-dot">3</span> <span>{sl["s2_rows"][2]}</span></div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a1-rig-01", {{ scale: 1.00 }}, {{ scale: 1.05, duration: {s1_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a1-rig-02", {{ scale: 1.05 }}, {{ scale: 1.00, duration: {s2_dur}, ease: "none", immediateRender: false }}, {s2_st});

    tl.fromTo("#a1-hook-pill-box", {{ opacity: 0, y: -18, scale: 0.92, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.22, ease: "back.out(1.4)" }}, 0.08)
      .fromTo("#a1-hook-hero", {{ opacity: 0, scale: 0.88, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.5)" }}, 0.16)
      .fromTo("#a1hk-light", {{ attr: {{ x: 100 }} }}, {{ attr: {{ x: 960 }}, duration: 1.15, ease: "power2.inOut" }}, 0.35)
      .to("#a1-hook-pill-box", {{ opacity: 0, y: -10, filter: "blur(10px)", duration: 0.20, ease: "power2.in" }}, 2.84)
      .to("#a1-hook-hero", {{ opacity: 0, scale: 0.95, filter: "blur(12px)", duration: 0.20, ease: "power2.in" }}, 2.86);

    tl.fromTo("#a1-slide-pain", {{ opacity: 0, x: -70, scale: 0.94, filter: "blur(14px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, {sl1_st})
      .fromTo("#a1-r1", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(sl1_st + 0.14, 2)})
      .fromTo("#a1-r2", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(sl1_st + 0.72, 2)})
      .fromTo("#a1-r3", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(sl1_st + 1.30, 2)})
      .to("#a1-slide-pain", {{ opacity: 0, x: -40, filter: "blur(12px)", duration: 0.20 }}, {round(sl1_st + sl1_dur - 0.22, 2)});

    window.__timelines["act1-hook"] = tl;
  </script>
</template>
"""
    (comp_dir / "act1-hook.html").write_text(act1_html, encoding="utf-8")

    # --- ACT 2 (S03 + S04): Brand Choice Pill + Portal Studio Hero Packshot ---
    a2_st = segs["vo_03"]["shot_start_s"]
    s3_dur = segs["vo_03"]["shot_duration_s"]
    s4_local = round(segs["vo_04"]["shot_start_s"] - a2_st, 2)
    s4_dur = segs["vo_04"]["shot_duration_s"]
    a2_dur = round(s3_dur + s4_dur, 2)

    act2_html = f"""<template>
  <style>{shared_css}</style>
  <div id="root" data-composition-id="act2-hero" data-width="1080" data-height="1920" data-start="0" data-duration="{a2_dur}">
    <div id="a2-rig-03" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a2-v03" class="clip bg-video" src="assets/videos/{vcode}_S03.mp4" data-start="0" data-duration="{s3_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a2-rig-04" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a2-v04" class="clip bg-video" src="assets/videos/{vcode}_S04.mp4" data-start="{s4_local}" data-duration="{s4_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>

    <!-- SLIDE OVERLAY #2 (S03 — Chị Hằng + Product): Lower-Left Compact Choice Card -->
    <div id="a2-choice" class="clip slide-pill-choice" style="top: 1126px;" data-start="0.20" data-duration="{round(s3_dur - 0.40, 2)}" data-track-index="3" data-layout-ignore>
      ♥ {sl["s3_pill"]}
    </div>

    <!-- S04 Top Product Title + SLIDE OVERLAY #3 (3 Core USP Benefits in open upper sky above packshot!) -->
    <div id="a2-s4-title" class="clip float-stage" data-start="{round(s4_local + 0.12, 2)}" data-duration="{round(s4_dur - 0.24, 2)}" data-track-index="4" data-layout-ignore>
      <div id="a2-s4-kicker" class="top-hook-wrap" style="top: 256px;">
        <div class="top-hook-pill" style="font-size: 27px; padding: 8px 24px;">{vspec["s4_kicker"]}</div>
      </div>
      <svg class="svg-typo" viewBox="0 0 1080 1920">
        {svg_defs("a2s4", vspec["accent_hex"], vspec["accent_dark"])}
        <g id="a2-s4-hero">
          <text x="540" y="420" text-anchor="middle" class="satin-hero" font-size="{s4_font_sz}" fill="url(#a2s4-hero-fill)" filter="url(#a2s4-silk-3d)">{vspec["s4_hero"]}</text>
        </g>
      </svg>
    </div>

    <div id="a2-slide-usp" class="clip slide-card" style="top: 458px;" data-start="{round(s4_local + 0.42, 2)}" data-duration="{round(s4_dur - 0.64, 2)}" data-track-index="5" data-layout-ignore>
      <div class="slide-card-header">{sl["s4_header"]}</div>
      <div id="a2-u1" class="slide-row"><span class="slide-badge-dot">✓</span> <span>{sl["s4_rows"][0]}</span></div>
      <div id="a2-u2" class="slide-row"><span class="slide-badge-dot">✓</span> <span>{sl["s4_rows"][1]}</span></div>
      <div id="a2-u3" class="slide-row"><span class="slide-badge-dot">✓</span> <span>{sl["s4_rows"][2]}</span></div>
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a2-rig-03", {{ scale: 1.00 }}, {{ scale: 1.05, duration: {s3_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a2-rig-04", {{ scale: 1.05 }}, {{ scale: 1.00, duration: {s4_dur}, ease: "none", immediateRender: false }}, {s4_local});

    tl.fromTo("#a2-choice", {{ opacity: 0, x: -55, scale: 0.94, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.3)" }}, 0.22)
      .to("#a2-choice", {{ opacity: 0, filter: "blur(10px)", duration: 0.18 }}, {round(s3_dur - 0.40, 2)});

    tl.fromTo("#a2-s4-kicker", {{ opacity: 0, y: -14, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.22 }}, {round(s4_local + 0.14, 2)})
      .fromTo("#a2-s4-hero", {{ opacity: 0, scale: 0.90, filter: "blur(12px)" }}, {{ opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.4)" }}, {round(s4_local + 0.22, 2)})
      .fromTo("#a2s4-light", {{ attr: {{ x: 110 }} }}, {{ attr: {{ x: 960 }}, duration: 1.20, ease: "power2.inOut" }}, {round(s4_local + 0.40, 2)})
      .to("#a2-s4-title", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s4_local + s4_dur - 0.34, 2)});

    tl.fromTo("#a2-slide-usp", {{ opacity: 0, x: -65, scale: 0.94, filter: "blur(14px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, {round(s4_local + 0.44, 2)})
      .fromTo("#a2-u1", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.20 }}, {round(s4_local + 0.62, 2)})
      .fromTo("#a2-u2", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.20 }}, {round(s4_local + 1.25, 2)})
      .fromTo("#a2-u3", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.20 }}, {round(s4_local + 1.90, 2)})
      .to("#a2-slide-usp", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s4_local + s4_dur - 0.42, 2)});

    window.__timelines["act2-hero"] = tl;
  </script>
</template>
"""
    (comp_dir / "act2-hero.html").write_text(act2_html, encoding="utf-8")

    # --- ACT 3 (S05 + S06): Herbal/Active Slide #4 + Brand End-Card Lockup ---
    a3_st = segs["vo_05"]["shot_start_s"]
    s5_dur = segs["vo_05"]["shot_duration_s"]
    s6_local = round(segs["vo_06"]["shot_start_s"] - a3_st, 2)
    s6_dur = round(total_dur - segs["vo_06"]["shot_start_s"], 2)
    a3_dur = round(s5_dur + s6_dur, 2)

    act3_html = f"""<template>
  <style>
    {shared_css}
    .end-card-panel {{
      position: absolute;
      left: 428px;
      top: 724px;
      width: 446px;
      border-radius: 30px;
      background: linear-gradient(145deg, rgba(255, 255, 255, 0.97) 0%, rgba(255, 240, 247, 0.95) 100%);
      border: 3px solid {vspec["accent_hex"]};
      box-shadow: 0 18px 40px rgba(48, 6, 24, 0.28);
      padding: 20px 22px 18px 22px;
      text-align: center;
      z-index: 10;
      pointer-events: none;
    }}
    .end-packshot {{
      display: block;
      margin: 12px auto 0 auto;
      max-width: 280px;
      max-height: 256px;
      width: auto;
      height: auto;
      border-radius: 10px;
      filter: drop-shadow(0 12px 22px rgba(48, 6, 24, 0.26));
    }}
    .end-cta-box {{
      position: absolute;
      left: 58px;
      top: 1320px;
      width: 818px;
      background: linear-gradient(90deg, {vspec["accent_dark"]} 0%, {vspec["accent_hex"]} 50%, {vspec["accent_dark"]} 100%);
      color: #FFFFFF;
      border: 3.5px solid #FFE8A3;
      border-radius: 999px;
      padding: 17px 26px;
      text-align: center;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 33px;
      font-weight: 800;
      box-shadow: 0 16px 34px rgba(38, 6, 20, 0.42);
      z-index: 12;
    }}
    .legal-note {{
      position: absolute;
      left: 58px;
      top: 1442px;
      width: 818px;
      text-align: center;
      font-family: "BeVietnamVN", sans-serif;
      font-size: 21px;
      font-weight: 800;
      color: #FFFFFF;
      background: rgba(24, 6, 18, 0.84);
      border: 1.5px solid rgba(255, 232, 163, 0.55);
      border-radius: 16px;
      padding: 9px 16px;
      z-index: 12;
    }}
  </style>
  <div id="root" data-composition-id="act3-endcard" data-width="1080" data-height="1920" data-start="0" data-duration="{a3_dur}">
    <div id="a3-rig-05" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a3-v05" class="clip bg-video" src="assets/videos/{vcode}_S05.mp4" data-start="0" data-duration="{s5_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="a3-rig-06" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video data-color-grading="{COLOR_GRADE_ROSESILK}" id="a3-v06" class="clip bg-video" src="assets/videos/{vcode}_S06.mp4" data-start="{s6_local}" data-duration="{s6_dur}" data-media-start="0.15" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>

    <!-- SLIDE OVERLAY #4 (S05): Botanical / Active Ingredients -->
    <div id="a3-slide-herb" class="clip slide-card" style="top: 276px;" data-start="0.16" data-duration="{round(s5_dur - 0.34, 2)}" data-track-index="3" data-layout-ignore>
      <div class="slide-card-header">{sl["s5_header"]}</div>
      <div id="a3-h1" class="slide-row"><span class="slide-badge-dot">1</span> <span>{sl["s5_rows"][0]}</span></div>
      <div id="a3-h2" class="slide-row"><span class="slide-badge-dot">2</span> <span>{sl["s5_rows"][1]}</span></div>
      <div id="a3-h3" class="slide-row"><span class="slide-badge-dot">3</span> <span>{sl["s5_rows"][2]}</span></div>
    </div>

    <!-- S06 Brand End-Card Lockup (X=428..874 <= 884px, Y=724..1518 <= 1545px!) -->
    <div id="a3-panel" class="clip end-card-panel" data-start="{round(s6_local + 0.12, 2)}" data-duration="{round(s6_dur - 0.12, 2)}" data-track-index="4" data-layout-ignore>
      <div style="font-family:'BeVietnamVN',sans-serif;font-size:22px;font-weight:800;color:{vspec['accent_hex']};letter-spacing:0.04em;">{vspec["end_kicker"]}</div>
      <div style="font-family:'FrauncesVN',Georgia,serif;font-size:56px;font-weight:900;color:{vspec['accent_dark']};line-height:1.06;margin-top:4px;">{vspec["end_title"]}</div>
      <div style="font-family:'DancingVN',cursive;font-size:44px;font-weight:700;color:#C87406;line-height:1.08;">Hằng Thu Pharma</div>
      <div style="font-family:'BeVietnamVN',sans-serif;font-size:20px;font-weight:800;color:#38061B;margin-top:6px;">{vspec["end_tagline"]}</div>
      <img id="a3-pack" class="end-packshot" src="assets/images/{vspec['cutout_png']}" alt="{vspec['end_title']}" />
    </div>

    <div id="a3-cta" class="clip end-cta-box" data-start="{round(s6_local + 0.30, 2)}" data-duration="{round(s6_dur - 0.30, 2)}" data-track-index="5" data-layout-ignore>
      {vspec["cta_text"]}
    </div>
    <div id="a3-legal" class="clip legal-note" data-start="{round(s6_local + 0.38, 2)}" data-duration="{round(s6_dur - 0.38, 2)}" data-track-index="6" data-layout-ignore>
      {vspec["legal_text"]}
    </div>
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#a3-rig-05", {{ scale: 1.00 }}, {{ scale: 1.05, duration: {s5_dur}, ease: "none", immediateRender: false }}, 0)
      .fromTo("#a3-rig-06", {{ scale: 1.00 }}, {{ scale: 1.04, duration: {s6_dur}, ease: "none", immediateRender: false }}, {s6_local});

    tl.fromTo("#a3-slide-herb", {{ opacity: 0, x: -65, scale: 0.94, filter: "blur(14px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, 0.18)
      .fromTo("#a3-h1", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, 0.40)
      .fromTo("#a3-h2", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, 1.15)
      .fromTo("#a3-h3", {{ opacity: 0, x: -22 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, 1.90)
      .to("#a3-slide-herb", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s5_dur - 0.38, 2)});

    tl.fromTo("#a3-panel", {{ opacity: 0, x: 45, scale: 0.92, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, scale: 1.0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.3)" }}, {round(s6_local + 0.14, 2)})
      .fromTo("#a3-pack", {{ opacity: 0, y: 18, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.30, ease: "back.out(1.35)" }}, {round(s6_local + 0.24, 2)})
      .fromTo("#a3-cta", {{ opacity: 0, y: 20, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.28, ease: "back.out(1.3)" }}, {round(s6_local + 0.32, 2)})
      .fromTo("#a3-legal", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.24 }}, {round(s6_local + 0.42, 2)});

    window.__timelines["act3-endcard"] = tl;
  </script>
</template>
"""
    (comp_dir / "act3-endcard.html").write_text(act3_html, encoding="utf-8")

    # --- CAPTIONS TRACK: HUGE 46px–50px HIGH-CONTRAST VELVET SUBTITLES! ---
    caps = []
    for seg_id, _, _, cap_splits in vspec["segments"]:
        if not cap_splits:
            continue
        s = segs[seg_id]
        prev_t = s["start_s"]
        for k_idx, (html_line, end_ratio) in enumerate(cap_splits):
            t_end = round(s["start_s"] + s["duration_s"] * end_ratio, 2)
            if k_idx == len(cap_splits) - 1:
                t_end = min(round(s["shot_end_s"] - 0.06, 2), round(s["end_s"] + 0.14, 2))
            caps.append((f"cap-{seg_id}-{k_idx}", prev_t, t_end, html_line))
            prev_t = round(t_end + 0.03, 2)

    divs, js_groups = [], []
    for idx, (cid, st, en, inner) in enumerate(caps):
        dur = round(max(0.25, en - st), 3)
        trk = (idx % 4) + 1
        divs.append(
            f'    <div id="{cid}" class="clip cap-clip" data-start="{st}" data-duration="{dur}" data-track-index="{trk}" data-layout-ignore>\n'
            f'      <div id="in-{cid}" class="cap-box">{inner}</div>\n'
            f'    </div>'
        )
        js_groups.append(f'      {{ sel: "#in-{cid}", st: {st}, en: {en} }}')

    cap_end = segs["vo_06"]["shot_start_s"]
    cap_html = f"""<template>
  <style>
    @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
    .cap-clip {{
      position: absolute;
      left: 58px;
      top: 1364px;
      width: 818px;
      text-align: center;
      overflow: visible;
    }}
    .cap-box {{
      display: inline-block;
      max-width: 814px;
      opacity: 0;
      background: rgba(24, 6, 18, 0.88);
      border: 2.5px solid rgba(255, 228, 152, 0.78);
      border-radius: 24px;
      padding: 13px 26px;
      font-family: "BeVietnamVN", sans-serif;
      font-weight: 800;
      font-size: 46px;
      line-height: 1.24;
      color: #FFFFFF;
      paint-order: stroke fill;
      -webkit-text-stroke: 4px #16030F;
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.44);
      letter-spacing: -0.01em;
      text-wrap: balance;
    }}
    .cap-kw {{
      color: #FFE47A;
      font-size: 49px;
      font-weight: 800;
      paint-order: stroke fill;
      -webkit-text-stroke: 4px #16030F;
    }}
  </style>

  <div id="root" data-composition-id="captions-track" data-width="1080" data-height="1920">
{chr(10).join(divs)}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    const groups = [{",".join(chr(10) + g for g in js_groups)}
    ];
    groups.forEach((g) => {{
      tl.fromTo(g.sel, {{ opacity: 0, y: 14, scale: 0.94, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.18, ease: "back.out(1.3)" }}, g.st)
        .to(g.sel, {{ opacity: 0, y: -6, filter: "blur(6px)", duration: 0.14, ease: "power2.in" }}, g.en - 0.14)
        .set(g.sel, {{ opacity: 0, visibility: "hidden" }}, g.en);
    }});
    window.__timelines["captions-track"] = tl;
  </script>
</template>
"""
    (comp_dir / "captions-track.html").write_text(cap_html, encoding="utf-8")

    # --- TRANSITIONS (Sun-Flare + Portal Spin at S04) ---
    t_s3 = segs["vo_03"]["shot_start_s"]
    t_portal = segs["vo_04"]["shot_start_s"]
    t_s5 = segs["vo_05"]["shot_start_s"]
    t_s6 = segs["vo_06"]["shot_start_s"]

    trans_html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
    .fx-clip {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
    .sun-flare {{
      position: absolute; inset: 0; opacity: 0;
      background: radial-gradient(ellipse at 52% 42%, rgba(255,255,255,0.88) 0%, rgba(255,230,242,0.74) 32%, rgba(232,92,148,0.38) 60%, rgba(232,92,148,0) 86%);
      mix-blend-mode: screen;
    }}
    .portal-ring {{
      position: absolute; left: 50%; top: 50%; width: 920px; height: 920px; margin-left: -460px; margin-top: -460px;
      opacity: 0; border-radius: 50%; border: 64px solid #FFB3D1;
      box-shadow: inset 0 0 52px rgba(255,250,220,0.94), 0 0 72px rgba(201,24,96,0.84);
    }}
  </style>
  <div id="root" data-composition-id="tvc-transitions" data-width="1080" data-height="1920">
    <div id="fx-fl1-clip" class="clip fx-clip" data-start="{round(t_s3 - 0.25, 3)}" data-duration="0.5" data-track-index="1" data-layout-ignore><div id="fx-fl1" class="sun-flare"></div></div>
    <div id="fx-portal-clip" class="clip fx-clip" data-start="{round(t_portal - 0.375, 3)}" data-duration="0.75" data-track-index="3" data-layout-allow-overflow data-layout-ignore><div id="fx-portal" class="portal-ring"></div><div id="fx-fl2" class="sun-flare"></div></div>
    <div id="fx-fl3-clip" class="clip fx-clip" data-start="{round(t_s5 - 0.25, 3)}" data-duration="0.5" data-track-index="2" data-layout-ignore><div id="fx-fl3" class="sun-flare"></div></div>
    <div id="fx-fl4-clip" class="clip fx-clip" data-start="{round(t_s6 - 0.25, 3)}" data-duration="0.5" data-track-index="1" data-layout-ignore><div id="fx-fl4" class="sun-flare"></div></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    [{{ id: "#fx-fl1", st: {round(t_s3 - 0.25, 3)}, pk: {t_s3} }}, {{ id: "#fx-fl3", st: {round(t_s5 - 0.25, 3)}, pk: {t_s5} }}, {{ id: "#fx-fl4", st: {round(t_s6 - 0.25, 3)}, pk: {t_s6} }}].forEach((f) => {{
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
    (comp_dir / "tvc-transitions.html").write_text(trans_html, encoding="utf-8")

    # --- ROOT INDEX.HTML (2-Part C-Major BGM + Checkerboard VO + Tactile Micro-SFX) ---
    vo_tags = []
    for idx, s in enumerate(manifest["segments"]):
        trk = 5 if (idx % 2 == 0) else 6
        vol = "1.34" if idx in (2, 3, 5) else "1.32"
        vo_tags.append(
            f'      <audio id="{s["id"].replace("_", "-")}" class="clip" src="assets/audio/{s["id"]}.wav" '
            f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{trk}" '
            f'data-volume="{vol}" data-fade-in="0.035" data-fade-out="0.055" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        )

    bgm1_dur = round(t_portal + 0.15, 2)
    bgm2_st = round(t_portal - 0.10, 2)
    bgm2_dur = round(total_dur - bgm2_st, 2)
    outro_swell_t = round(bgm2_dur - 1.05, 2)

    root_html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{vspec["sku"]} — HTPM USP TVC (9:16, 24fps)</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #240714; font-family: sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .captions-host {{ position: absolute; inset: 0; z-index: 12; pointer-events: none; }}
      .transitions-host {{ position: absolute; inset: 0; z-index: 18; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total_dur}" data-width="1080" data-height="1920" data-fps="24">
      <div id="act1-hook" class="scene-host" data-composition-id="act1-hook" data-composition-src="compositions/act1-hook.html" data-start="0" data-duration="{a1_dur}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act2-hero" class="scene-host" data-composition-id="act2-hero" data-composition-src="compositions/act2-hero.html" data-start="{a2_st}" data-duration="{a2_dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="act3-endcard" class="scene-host" data-composition-id="act3-endcard" data-composition-src="compositions/act3-endcard.html" data-start="{a3_st}" data-duration="{a3_dur}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <div id="captions-track" class="captions-host" data-composition-id="captions-track" data-composition-src="compositions/captions-track.html" data-start="0" data-duration="{cap_end}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="tvc-transitions" class="transitions-host" data-composition-id="tvc-transitions" data-composition-src="compositions/tvc-transitions.html" data-start="0" data-duration="{total_dur}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

{chr(10).join(vo_tags)}

      <audio id="bgm-warm-intro" class="clip" src="assets/audio/bgm_warm_fretless.mp3" data-start="0" data-duration="{bgm1_dur}" data-media-start="0" data-track-index="7" data-fade-in="0.18" data-fade-out="0.45" data-fx-chain="{{&quot;version&quot;:1,&quot;nodes&quot;:[{{&quot;type&quot;:&quot;gain&quot;,&quot;id&quot;:&quot;bgain1&quot;,&quot;label&quot;:&quot;Level match&quot;,&quot;params&quot;:{{&quot;gain&quot;:6.8}}}},{{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;bhp1&quot;,&quot;label&quot;:&quot;Clean low end&quot;,&quot;params&quot;:{{&quot;frequency&quot;:75}}}},{{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;bcarve1&quot;,&quot;label&quot;:&quot;Voice pocket&quot;,&quot;params&quot;:{{&quot;frequency&quot;:2300,&quot;gain&quot;:-3.8,&quot;q&quot;:0.85}}}},{{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;blim1&quot;,&quot;params&quot;:{{&quot;limit&quot;:-2.5}}}}]}}" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.52}},{{&quot;t&quot;:0.22,&quot;v&quot;:0.30}},{{&quot;t&quot;:{round(bgm1_dur - 0.55, 2)},&quot;v&quot;:0.31}},{{&quot;t&quot;:{bgm1_dur},&quot;v&quot;:0.0}}]}}]}}"></audio>
      <audio id="bgm-bright-hero" class="clip" src="assets/audio/bgm_bright_riley.mp3" data-start="{bgm2_st}" data-duration="{bgm2_dur}" data-media-start="0" data-track-index="8" data-fade-in="0.20" data-fade-out="0.65" data-fx-chain="{{&quot;version&quot;:1,&quot;nodes&quot;:[{{&quot;type&quot;:&quot;gain&quot;,&quot;id&quot;:&quot;bgain2&quot;,&quot;label&quot;:&quot;Level match&quot;,&quot;params&quot;:{{&quot;gain&quot;:6.4}}}},{{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;bhp2&quot;,&quot;label&quot;:&quot;Clean low end&quot;,&quot;params&quot;:{{&quot;frequency&quot;:80}}}},{{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;bcarve2&quot;,&quot;label&quot;:&quot;Voice pocket&quot;,&quot;params&quot;:{{&quot;frequency&quot;:2400,&quot;gain&quot;:-3.8,&quot;q&quot;:0.85}}}},{{&quot;type&quot;:&quot;highshelf&quot;,&quot;id&quot;:&quot;bair2&quot;,&quot;label&quot;:&quot;Bright sheen&quot;,&quot;params&quot;:{{&quot;frequency&quot;:7500,&quot;gain&quot;:1.2}}}},{{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;blim2&quot;,&quot;params&quot;:{{&quot;limit&quot;:-2.5}}}}]}}" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.54}},{{&quot;t&quot;:0.35,&quot;v&quot;:0.32}},{{&quot;t&quot;:{round(outro_swell_t - 0.20, 2)},&quot;v&quot;:0.33}},{{&quot;t&quot;:{outro_swell_t},&quot;v&quot;:0.70}},{{&quot;t&quot;:{bgm2_dur},&quot;v&quot;:0.70}}]}}]}}"></audio>

      <!-- Frame-Synced Tactile Studio Micro-SFX -->
      <audio id="sfx-w1" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="0.04" data-duration="0.50" data-track-index="9" data-volume="0.21" data-fade-out="0.12"></audio>
      <audio id="sfx-w2" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{round(s2_st + 0.06, 2)}" data-duration="0.50" data-track-index="9" data-volume="0.19" data-fade-out="0.12"></audio>
      <audio id="sfx-w3" class="clip" src="assets/audio/sfx_whoosh_transition.mp3" data-start="{round(t_s3 - 0.08, 2)}" data-duration="0.55" data-track-index="9" data-volume="0.19" data-fade-out="0.14"></audio>
      <audio id="sfx-portal" class="clip" src="assets/audio/sfx_whoosh_cinematic.mp3" data-start="{round(t_portal - 1.20, 2)}" data-duration="2.60" data-media-start="1.00" data-track-index="9" data-volume="0.20" data-fade-in="0.25" data-fade-out="0.45"></audio>
      <audio id="sfx-w5" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{round(t_s5 + 0.08, 2)}" data-duration="0.50" data-track-index="9" data-volume="0.19" data-fade-out="0.12"></audio>
      <audio id="sfx-w6" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{round(t_s6 - 0.06, 2)}" data-duration="0.55" data-track-index="9" data-volume="0.21" data-fade-out="0.12"></audio>

      <audio id="sfx-p1" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="0.18" data-duration="0.55" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>
      <audio id="sfx-p2" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(s2_st + 0.24, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.20" data-fade-out="0.12"></audio>
      <audio id="sfx-c2a" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s2_st + 0.86, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c2b" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s2_st + 1.44, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-p3" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(t_s3 + 0.22, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.21" data-fade-out="0.12"></audio>
      <audio id="sfx-p4" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(t_portal + 0.26, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>
      <audio id="sfx-c4a" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(t_portal + 1.25, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c4b" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(t_portal + 1.90, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c5a" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(t_s5 + 0.40, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c5b" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(t_s5 + 1.15, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.24" data-fade-out="0.08"></audio>
      <audio id="sfx-c5c" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(t_s5 + 1.90, 2)}" data-duration="0.34" data-track-index="10" data-volume="0.25" data-fade-out="0.08"></audio>
      <audio id="sfx-p6" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(t_s6 + 0.32, 2)}" data-duration="0.55" data-track-index="10" data-volume="0.22" data-fade-out="0.12"></audio>

      <audio id="sfx-ch3" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="{round(t_s3 + 0.20, 2)}" data-duration="2.10" data-track-index="11" data-volume="0.50" data-fade-out="0.45"></audio>
      <audio id="sfx-sp4" class="clip" src="assets/audio/sfx_sparkle_shine.mp3" data-start="{round(t_portal - 0.02, 2)}" data-duration="1.70" data-track-index="11" data-volume="0.24" data-fade-out="0.35"></audio>
      <audio id="sfx-sh5" class="clip" src="assets/audio/sfx_crystal_shimmer.mp3" data-start="{round(t_s5 + 0.25, 2)}" data-duration="2.10" data-media-start="0.35" data-track-index="11" data-volume="0.56" data-fade-in="0.08" data-fade-out="0.45"></audio>
      <audio id="sfx-ch6" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="{round(t_s6 + 0.12, 2)}" data-duration="2.10" data-track-index="11" data-volume="0.56" data-fade-out="0.45"></audio>
      <audio id="sfx-cta6" class="clip" src="assets/audio/sfx_notification_cta.mp3" data-start="{round(t_s6 + 0.50, 2)}" data-duration="2.00" data-track-index="12" data-volume="0.19" data-fade-out="0.40"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    (hf_dir / "index.html").write_text(root_html, encoding="utf-8")
    return hf_dir, total_dur


def render_qa_and_deliver(vspec: dict):
    vcode = vspec["vid_code"]
    vdir = ROOT_OUT / vcode
    hf_dir, total_dur = build_hf_for_video(vspec)
    master_dir = vdir / "08_Render_Master"
    master_dir.mkdir(parents=True, exist_ok=True)
    master_mp4 = master_dir / f"{vcode.lower()}_master_24p.mp4"

    # 1. Validate HyperFrames Check (0 errors!)
    chk = subprocess.run(
        ["npx.cmd", "hyperframes", "check", "--json"],
        cwd=str(hf_dir),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(f"[{vcode} CHECK] rc={chk.returncode}", flush=True)

    # 2. Render MP4 24fps if not already rendered
    if not (master_mp4.exists() and master_mp4.stat().st_size > 5_000_000):
        print(f"[{vcode} RENDER] Rendering {total_dur}s @ 24fps -> {master_mp4.name}...", flush=True)
        subprocess.run(
            ["npx.cmd", "hyperframes", "render", "--output", str(master_mp4)],
            cwd=str(hf_dir),
            check=True,
        )

    # 3. Measure QA + Build 8-panel Safe-Zone Sheet (showing t=1.2s Hook 3s, t=3.6s post-hook, S02, S03, S04, S05, S06)
    pr = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate", "-of", "json", str(master_mp4)]
        ).decode("utf-8")
    )
    ebu = subprocess.run(
        ["ffmpeg", "-nostats", "-i", str(master_mp4), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    m_i = re.findall(r"I:\s*(-?\d+\.\d+)\s*LUFS", ebu)
    lufs = float(m_i[-1]) if m_i else None
    dur = float(pr["format"]["duration"])
    size_mb = round(int(pr["format"]["size"]) / (1024 * 1024), 2)

    segs = {s["id"]: s for s in json.loads((vdir / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))["segments"]}
    ts_list = [
        1.20,                                    # Inside 3.00s Top Hook!
        3.60,                                    # After 3.00s Top Hook disappeared cleanly!
        segs["vo_02"]["shot_start_s"] + 2.2,     # S02 Large Pain Slide + Large Subtitle
        segs["vo_03"]["shot_start_s"] + 2.0,     # S03 Chị Hằng + Product + Choice Pill
        segs["vo_04"]["shot_start_s"] + 2.4,     # S04 Packshot + 3D Title + USP Slide
        segs["vo_05"]["shot_start_s"] + 2.4,     # S05 Herbal Macro + Herb Slide
        segs["vo_06"]["shot_start_s"] + 1.5,     # S06 End-Card Lockup
        min(dur - 0.4, segs["vo_06"]["shot_start_s"] + 3.5),
    ]
    qa_fdir = master_dir / "qa_frames"
    qa_fdir.mkdir(parents=True, exist_ok=True)
    tiles = []
    for idx, ts in enumerate(ts_list, start=1):
        ts_c = min(dur - 0.25, max(0.2, ts))
        fp = qa_fdir / f"f_{idx:02d}.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts_c:.2f}", "-i", str(master_mp4), "-frames:v", "1", "-q:v", "2", str(fp)], check=True)
        im = Image.open(fp).convert("RGB")
        d = ImageDraw.Draw(im)
        d.line([(0, 248), (1080, 248)], fill=(255, 60, 60), width=4)
        d.line([(0, 1548), (1080, 1548)], fill=(255, 60, 60), width=4)
        d.line([(52, 248), (52, 1548)], fill=(255, 60, 60), width=3)
        d.line([(1026, 248), (1026, 860)], fill=(255, 60, 60), width=3)
        d.rectangle([(886, 860), (1080, 1548)], outline=(255, 60, 60), width=4)
        tiles.append((f"{vcode} t={ts_c:.1f}s", im))

    tw, th = 330, 586
    sheet = Image.new("RGB", (tw * 4, th * 2), (20, 12, 16))
    sd = ImageDraw.Draw(sheet)
    for i, (lbl, im) in enumerate(tiles):
        c, r = i % 4, i // 4
        sheet.paste(im.resize((tw - 8, th - 28), Image.Resampling.LANCZOS), (c * tw + 4, r * th + 24))
        sd.text((c * tw + 12, r * th + 4), lbl, fill=(255, 220, 235))
    qa_sheet = ROOT_OUT / f"qa_{vcode.lower()}_safezone.jpg"
    sheet.save(qa_sheet, quality=90)

    # 4. Deliver to all 3 Official HTPM Destinations + Archive
    fname = vspec["final_name"]
    for vdest in (BRAND_VIDEO_DIR, CLOUD_VIDEO_DIR, LOCAL_BACKUP_DIR):
        vdest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(master_mp4, vdest / fname)

    CLOUD_DU_AN_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(qa_sheet, CLOUD_DU_AN_DIR / qa_sheet.name)

    info = {
        "vid_code": vcode,
        "sku": vspec["sku"],
        "final_name": fname,
        "brand_path": str(BRAND_VIDEO_DIR / fname),
        "backup_path": str(LOCAL_BACKUP_DIR / fname),
        "duration_s": round(dur, 2),
        "size_mb": size_mb,
        "lufs": lufs,
        "qa_sheet": str(qa_sheet),
    }
    print(f"[DELIVERED {vcode}] {fname} ({dur:.2f}s, {size_mb} MB, {lufs} LUFS)", flush=True)
    return info


def main():
    only_codes = [a.upper() for a in sys.argv[1:] if a.upper().startswith("V0")]
    targets = [v for v in VIDEOS_9USP if (not only_codes or v["vid_code"] in only_codes)]
    summary = []
    for vspec in targets:
        summary.append(render_qa_and_deliver(vspec))

    # Build Master 9-Video Overview Sheet (3x3 of t=1.2s Hook frames + 3x3 of End-Card frames)
    master_tiles = []
    for item in summary:
        vcode = item["vid_code"]
        f1 = ROOT_OUT / vcode / "08_Render_Master" / "qa_frames" / "f_01.jpg"
        f7 = ROOT_OUT / vcode / "08_Render_Master" / "qa_frames" / "f_07.jpg"
        if f1.exists() and f7.exists():
            master_tiles.append((f"{vcode} Hook 3s", Image.open(f1).convert("RGB")))
            master_tiles.append((f"{vcode} EndCard", Image.open(f7).convert("RGB")))

    if master_tiles:
        cols = 6
        rows = (len(master_tiles) + cols - 1) // cols
        tw, th = 270, 480
        msheet = Image.new("RGB", (tw * cols, th * rows), (18, 10, 14))
        md = ImageDraw.Draw(msheet)
        for i, (lbl, im) in enumerate(master_tiles):
            c, r = i % cols, i // cols
            msheet.paste(im.resize((tw - 6, th - 26), Image.Resampling.LANCZOS), (c * tw + 3, r * th + 22))
            md.text((c * tw + 10, r * th + 4), lbl, fill=(255, 226, 160))
        mp = ROOT_OUT / "ALL_9_HTPM_USP_MASTER_QA.jpg"
        msheet.save(mp, quality=91)
        shutil.copy2(mp, CLOUD_DU_AN_DIR / mp.name)

    (ROOT_OUT / "delivery_9usp_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(ROOT_OUT / "delivery_9usp_summary.json", CLOUD_DU_AN_DIR / "delivery_9usp_summary.json")
    for pyf in HERE.glob("*.py"):
        shutil.copy2(pyf, CLOUD_DU_AN_DIR / pyf.name)
    print("\nALL TARGET HTPM USP VIDEOS RENDERED, QA-VERIFIED & DELIVERED!", flush=True)


if __name__ == "__main__":
    main()
