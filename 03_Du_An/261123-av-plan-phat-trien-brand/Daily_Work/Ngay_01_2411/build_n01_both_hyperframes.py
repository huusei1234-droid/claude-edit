"""
Dựng HyperFrames 24fps (1080x1920) cho CẢ 2 VIDEO USP NGÀY 01 (24/11/2026) — AN VƯỢNG PHARMA:
- Video 01: AV Protein — Đạm Thực Vật 22,05g & L-Leucine (48.00s @ 24fps, 7 unique Flow clips + Studio End-Card)
- Video 02: Combo 4 Sản Phẩm — Tặng Collamela 20 Gói 920K (52.50s @ 24fps, 6 unique Flow clips + Studio Combo Showcase + Studio End-Card)

Tuân thủ 100%:
1. HyperFrames 12-Rule Render Contract (data-fps="24", gsap.fromTo, immediateRender:false, deterministic animations).
2. Vùng An Toàn Video Dọc 9:16 TikTok x Reels (Y = 256..1538px, X >= 58px, nửa dưới Y >= 860px giữ X <= 880px).
3. Chữ 3D Silk-Satin Emerald & 3D Gold Glitter Bling (2 lớp tách viền + SVG Specular Sweep), 0% che mặt mẫu.
4. BGM 2 nửa C-Major (Fretless -> Life of Riley) + EQ Voice Pocket + Dynamic Ducking + 10 Studio Micro-SFX.
5. Dòng pháp lý TPBS chuẩn hiển thị rõ ràng ở End-Card trong vùng an toàn.
"""
import os
import sys
import json
import shutil

DAY_DIR = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_01_2411"
CUTOUT_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG"
ASSETS_DIR = os.path.join(DAY_DIR, "01_ChatGPT_Assets")
STAGE_BG = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\assets_stage\bg_droppii_8th_stage.png"

LEGAL_TPBS = "Thực phẩm bổ sung. Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh."

COLOR_GRADE_ATTR = (
    'data-color-grading="{&quot;preset&quot;:null,&quot;intensity&quot;:1,'
    '&quot;adjust&quot;:{&quot;exposure&quot;:0.04,&quot;contrast&quot;:0.08,'
    '&quot;highlights&quot;:0.04,&quot;shadows&quot;:0.05,&quot;whites&quot;:0.06,'
    '&quot;blacks&quot;:0,&quot;temperature&quot;:0.03,&quot;tint&quot;:0.02,'
    '&quot;vibrance&quot;:0.12,&quot;saturation&quot;:0.05},'
    '&quot;details&quot;:{&quot;vignette&quot;:0.03,&quot;vignetteMidpoint&quot;:0.5,'
    '&quot;vignetteRoundness&quot;:0,&quot;vignetteFeather&quot;:0.65,&quot;grain&quot;:0,'
    '&quot;grainSize&quot;:0.25,&quot;grainRoughness&quot;:0.5},'
    '&quot;effects&quot;:{&quot;blur&quot;:0,&quot;pixelate&quot;:0,&quot;chromaBleed&quot;:0,'
    '&quot;tapeDamage&quot;:0,&quot;tapeTracking&quot;:0,&quot;tapeNoise&quot;:0,'
    '&quot;tapeSpeed&quot;:0.5,&quot;filmArtifacts&quot;:0,&quot;halftone&quot;:0,'
    '&quot;halftoneSize&quot;:0,&quot;twoInkPrint&quot;:0,&quot;twoInkPrintSize&quot;:0,'
    '&quot;ascii&quot;:0,&quot;asciiSize&quot;:0.065,&quot;asciiInvert&quot;:0,'
    '&quot;asciiStyle&quot;:0,&quot;asciiColor&quot;:1,&quot;asciiRotation&quot;:0,'
    '&quot;dither&quot;:0,&quot;ditherSize&quot;:0,&quot;bloom&quot;:0,&quot;bloomRadius&quot;:8,'
    '&quot;monoScreen&quot;:0,&quot;monoScreenSize&quot;:0,&quot;monoScreenAngle&quot;:0,'
    '&quot;monoScreenSpread&quot;:0,&quot;monoScreenShape&quot;:0,&quot;monoScreenInvert&quot;:0,'
    '&quot;scanlines&quot;:0,&quot;scanlineCount&quot;:0,&quot;scanlineSoftness&quot;:0,'
    '&quot;chromaticAberration&quot;:0,&quot;chromaticAngle&quot;:0,&quot;crtCurvature&quot;:0,'
    '&quot;digitalGlitch&quot;:0,&quot;digitalGlitchColorSplit&quot;:0,'
    '&quot;digitalGlitchLineTear&quot;:0,&quot;digitalGlitchPixelate&quot;:0,'
    '&quot;digitalGlitchBlockAmount&quot;:0,&quot;digitalGlitchBlockDisplacement&quot;:0,'
    '&quot;digitalGlitchBlockOpacity&quot;:0,&quot;digitalGlitchSpeed&quot;:0,'
    '&quot;engraving&quot;:0,&quot;engravingSpacing&quot;:0.41,&quot;engravingMinThickness&quot;:0.2,'
    '&quot;engravingMaxThickness&quot;:0.45,&quot;engravingAngle&quot;:0.25,'
    '&quot;engravingContrast&quot;:0.46,&quot;engravingSharpness&quot;:0.59,'
    '&quot;engravingWave&quot;:0.2,&quot;engravingWaveFrequency&quot;:0.22,'
    '&quot;crosshatch&quot;:0,&quot;crosshatchSpacing&quot;:0.28,&quot;crosshatchThickness&quot;:0.25,'
    '&quot;crosshatchAngle&quot;:0.25,&quot;crosshatchContrast&quot;:0.33,'
    '&quot;crosshatchEdges&quot;:0.5,&quot;crosshatchLineWeight&quot;:0,'
    '&quot;crosshatchWave&quot;:0.33,&quot;crosshatchWaveFrequency&quot;:0.22,'
    '&quot;kuwahara&quot;:0,&quot;kuwaharaRadius&quot;:0.14,&quot;kuwaharaSharpness&quot;:0.31,'
    '&quot;kuwaharaSaturation&quot;:0.5},&quot;lut&quot;:null,&quot;colorSpace&quot;:&quot;rec709&quot;}"'
)


def html_json(obj):
    return json.dumps(obj, separators=(",", ":")).replace('"', "&quot;")


VO_FX_CHAIN = html_json({
    "version": 1,
    "nodes": [
        {"type": "highpass", "id": "vhp", "label": "Clean rumble", "params": {"frequency": 85}},
        {"type": "peaking", "id": "vlow", "label": "Warmth balance", "params": {"frequency": 210, "gain": -1.8, "q": 1.1}},
        {"type": "peaking", "id": "vpres", "label": "Broadcast clarity", "params": {"frequency": 3100, "gain": 1.8, "q": 1.0}},
        {"type": "limiter", "id": "vlim", "params": {"limit": -1.0}},
    ],
})

BGM_INTRO_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "gain", "id": "bg1", "params": {"gain": 6.8}},
        {"type": "highpass", "id": "bh1", "params": {"frequency": 75}},
        {"type": "peaking", "id": "bc1", "params": {"frequency": 2300, "gain": -3.6, "q": 0.85}},
        {"type": "limiter", "id": "bl1", "params": {"limit": -2.5}},
    ],
})

BGM_HERO_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "gain", "id": "bg2", "params": {"gain": 6.4}},
        {"type": "highpass", "id": "bh2", "params": {"frequency": 80}},
        {"type": "peaking", "id": "bc2", "params": {"frequency": 2400, "gain": -3.8, "q": 0.85}},
        {"type": "highshelf", "id": "ba2", "params": {"frequency": 7500, "gain": 1.2}},
        {"type": "limiter", "id": "bl2", "params": {"limit": -2.5}},
    ],
})

LOCAL_FONT_CSS = """
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-SemiBold.ttf') format('truetype'); font-weight: 600; }
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-Bold.ttf') format('truetype'); font-weight: 700; }
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-ExtraBold.ttf') format('truetype'); font-weight: 800; }
@font-face { font-family: 'MontBlk'; src: url('assets/fonts/Montserrat-Black.ttf') format('truetype'); font-weight: 900; }
@font-face { font-family: 'PlayfairBI'; src: url('assets/fonts/PlayfairDisplay-BoldItalic.ttf') format('truetype'); font-weight: 700; font-style: italic; }
@font-face { font-family: 'FrauncesBlk'; src: url('assets/fonts/Fraunces-Black.ttf') format('truetype'); font-weight: 900; }
"""


def build_ducking_automation(segs, clip_start, clip_end, is_first_half):
    pts = []
    dur = round(clip_end - clip_start, 2)
    pts.append({"t": 0.0, "v": 0.58 if is_first_half else 0.60})
    for seg in segs:
        st = seg["start_s"] - clip_start
        en = seg["end_s"] - clip_start
        if en <= 0.05 or st >= dur - 0.05:
            continue
        t_in = max(0.05, round(st - 0.16, 2))
        t_duck = max(t_in + 0.02, round(st, 2))
        t_rel = min(dur - 0.12, round(en, 2))
        t_up = min(dur - 0.05, round(en + 0.24, 2))
        if t_in > pts[-1]["t"] + 0.04:
            pts.append({"t": t_in, "v": 0.54})
        if t_duck > pts[-1]["t"] + 0.02:
            pts.append({"t": t_duck, "v": 0.34})
        if t_rel > pts[-1]["t"] + 0.02:
            pts.append({"t": t_rel, "v": 0.34})
        if t_up > pts[-1]["t"] + 0.02:
            pts.append({"t": t_up, "v": 0.54})
    if is_first_half:
        if pts[-1]["t"] < dur - 0.35:
            pts.append({"t": round(dur - 0.35, 2), "v": 0.36})
        pts.append({"t": dur, "v": 0.0})
    else:
        if pts[-1]["t"] < dur - 0.85:
            pts.append({"t": round(dur - 0.85, 2), "v": 0.74})
        pts.append({"t": dur, "v": 0.76})
    return html_json({"version": 1, "lanes": [{"target": "volume", "points": pts}]})


def make_emerald_gold_svg_defs(prefix):
    return f"""
    <defs>
      <linearGradient id="{prefix}-em-grad" x1="0%" y1="0%" x2="10%" y2="100%">
        <stop offset="0%" stop-color="#E8FFF4"/>
        <stop offset="28%" stop-color="#38B27A"/>
        <stop offset="58%" stop-color="#075B3A"/>
        <stop offset="85%" stop-color="#229664"/>
        <stop offset="100%" stop-color="#043A24"/>
      </linearGradient>
      <linearGradient id="{prefix}-gold-grad" x1="0%" y1="0%" x2="8%" y2="100%">
        <stop offset="0%" stop-color="#FFFCE0"/>
        <stop offset="28%" stop-color="#FCE078"/>
        <stop offset="58%" stop-color="#D99012"/>
        <stop offset="84%" stop-color="#FFF2A8"/>
        <stop offset="100%" stop-color="#A86506"/>
      </linearGradient>
      <filter id="{prefix}-silk" x="-15%" y="-25%" width="130%" height="150%" color-interpolation-filters="sRGB">
        <feDropShadow in="SourceAlpha" dx="0" dy="6" stdDeviation="6" flood-color="#032618" flood-opacity="0.38" result="sh"/>
        <feGaussianBlur in="SourceAlpha" stdDeviation="2.4" result="bl"/>
        <feSpecularLighting in="bl" surfaceScale="7.5" specularConstant="1.4" specularExponent="24" lighting-color="#FFFFFF" result="sp">
          <fePointLight id="{prefix}-lt" x="120" y="-100" z="220"/>
        </feSpecularLighting>
        <feComposite in="sp" in2="SourceAlpha" operator="in" result="spC"/>
        <feMerge>
          <feMergeNode in="sh"/>
          <feMergeNode in="SourceGraphic"/>
          <feMergeNode in="spC"/>
        </feMerge>
      </filter>
    </defs>
    """


def sync_common_images(hf_img_dir):
    os.makedirs(hf_img_dir, exist_ok=True)
    for fn in [
        "av01_protein_a.png", "av02_bojomi_a.png", "av03_collamela_a.png",
        "av04_curcumilk_a.png", "logo_an_vuong_orig.png", "logo_an_vuong_on_dark.png",
    ]:
        src = os.path.join(CUTOUT_DIR, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(hf_img_dir, fn))
    shutil.copy2(os.path.join(ASSETS_DIR, "N01_HERO_MINT_9x16.png"), os.path.join(hf_img_dir, "hero_mint.png"))
    if os.path.exists(STAGE_BG):
        shutil.copy2(STAGE_BG, os.path.join(hf_img_dir, "stage_bg.png"))


def write_project_meta(hf_dir, slug, title, duration):
    with open(os.path.join(hf_dir, "hyperframes.json"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": False},
            "authoringSkill": "hyperframes",
        }, f, indent=2)
    with open(os.path.join(hf_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump({
            "name": slug, "private": True, "type": "module",
            "scripts": {
                "dev": "npx --yes hyperframes@0.9.38 preview",
                "check": "npx --yes hyperframes@0.9.38 check",
                "render": "npx --yes hyperframes@0.9.38 render",
            },
        }, f, indent=2)
    with open(os.path.join(hf_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"title": title, "width": 1080, "height": 1920, "fps": 24, "duration": duration}, f, indent=2, ensure_ascii=False)


def build_video_01():
    vdir = os.path.join(DAY_DIR, "video_01_av_protein")
    hf_dir = os.path.join(vdir, "07_HyperFrames_Project")
    comp_dir = os.path.join(hf_dir, "compositions")
    os.makedirs(comp_dir, exist_ok=True)
    sync_common_images(os.path.join(hf_dir, "assets", "images"))

    vo_data = json.loads(open(os.path.join(vdir, "06_Audio_Voiceover", "vo_manifest.json"), encoding="utf-8").read())
    segs = vo_data["segments"]
    total_dur = float(vo_data["total_duration_s"])  # 48.00s

    # Timeline shots (exact 24fps grid, 7 unique Flow videos + 1 Studio End-Card):
    # s01:  0.00.. 3.75 (3.75s, native 5.00s) | vo_01
    # s02:  3.75..10.00 (6.25s, native 7.00s) | vo_02
    # s03: 10.00..16.50 (6.50s, native 7.00s) | vo_03 -> HERO PORTAL SWITCH!
    # s04a:16.50..21.25 (4.75s, native 6.00s) | vo_04 part 1 (22,05g Đạm + 1.632mg L-Leucine)
    # s04b:21.25..25.75 (4.50s, native 6.00s) | vo_04 part 2 (Giữ cơ săn chắc — Pilates)
    # s05: 25.75..33.50 (7.75s, native 9.00s) | vo_05 (Inulin + B-3 + Pha 20-40°C)
    # s06: 33.50..39.75 (6.25s, native 7.00s) | vo_06 (Thơm béo nhẹ bụng mỗi sáng)
    # end: 39.75..48.00 (8.25s Studio End-Card) | vo_07 (350K + Mua 5 Tặng 1 Bojomi 520K)
    write_project_meta(hf_dir, "av-n01-v1-protein", "AV Protein — Đạm Thực Vật 22,05g (Ngày 01)", total_dur)

    bgm_split = 10.00
    bgm1_auto = build_ducking_automation(segs, 0.0, bgm_split + 0.35, True)
    bgm2_auto = build_ducking_automation(segs, bgm_split - 0.15, total_dur, False)

    # Voiceover audio tags (checkerboard track 5 & 6)
    vo_tags = []
    for i, s in enumerate(segs):
        tr = 5 if i % 2 == 0 else 6
        vo_tags.append(
            f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
            f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{tr}" '
            f'data-volume="1.30" data-fade-in="0.04" data-fade-out="0.06" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        )

    # Tactile Micro-SFX aligned to exact visual hits (-110ms for whoosh, 0ms for pop/chime/shimmer)
    sfx_list = [
        ("sfx-01", "sfx_pop_clean.mp3", 0.18, 0.55, 9, 0.24),
        ("sfx-02", "sfx_whoosh_soft.mp3", 3.64, 0.55, 9, 0.22),
        ("sfx-03", "sfx_whoosh_cinematic.mp3", 9.88, 0.90, 9, 0.28),
        ("sfx-04", "sfx_sparkle_shine.mp3", 10.08, 1.65, 10, 0.26),
        ("sfx-05", "sfx_whoosh_soft.mp3", 16.39, 0.55, 9, 0.22),
        ("sfx-06", "sfx_crystal_shimmer.mp3", 16.70, 2.00, 10, 0.56),
        ("sfx-07", "sfx_ping_glass.mp3", 21.25, 0.85, 11, 0.26),
        ("sfx-08", "sfx_whoosh_soft.mp3", 25.64, 0.55, 9, 0.22),
        ("sfx-09", "sfx_pop_clean.mp3", 26.20, 0.55, 11, 0.22),
        ("sfx-10", "sfx_chime_warm.mp3", 33.55, 2.20, 10, 0.52),
        ("sfx-11", "sfx_whoosh_cinematic.mp3", 39.64, 0.90, 9, 0.28),
        ("sfx-12", "sfx_sparkle_shine.mp3", 39.95, 1.65, 10, 0.28),
        ("sfx-13", "sfx_notification_cta.mp3", 41.20, 2.10, 11, 0.22),
    ]
    sfx_tags = [
        f'      <audio id="{sid}" class="clip" src="assets/audio/{fn}" data-start="{st}" '
        f'data-duration="{du}" data-track-index="{tr}" data-volume="{vol}" data-fade-out="0.16"></audio>'
        for sid, fn, st, du, tr, vol in sfx_list
    ]

    index_html = f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>AV Protein — Ngày 01</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      {LOCAL_FONT_CSS}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #042519; font-family: 'BeVN', sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .overlay-host {{ position: absolute; inset: 0; z-index: 12; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="39.75" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene-host" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="39.75" data-duration="8.25" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <!-- BGM 2 nửa C-Major + EQ Voice Pocket + Dynamic Ducking -->
      <audio id="bgm-intro" class="clip" src="assets/audio/bgm_warm_fretless.mp3" data-start="0" data-duration="{round(bgm_split + 0.35, 2)}" data-media-start="0" data-track-index="7" data-fade-in="0.18" data-fade-out="0.35" data-fx-chain="{BGM_INTRO_FX}" data-automation="{bgm1_auto}"></audio>
      <audio id="bgm-hero" class="clip" src="assets/audio/bgm_bright_riley.mp3" data-start="{round(bgm_split - 0.15, 2)}" data-duration="{round(total_dur - bgm_split + 0.15, 2)}" data-media-start="0" data-track-index="8" data-fade-in="0.28" data-fade-out="0.85" data-fx-chain="{BGM_HERO_FX}" data-automation="{bgm2_auto}"></audio>

{chr(10).join(vo_tags)}
{chr(10).join(sfx_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    open(os.path.join(hf_dir, "index.html"), "w", encoding="utf-8").write(index_html)

    # 1. main-video.html (7 UNIQUE Flow 24fps clips: 0.00..39.75s, ZERO repeated sources, ZERO img leaks!)
    main_vid_html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: #05261A; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 50%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .sun-flare {{
      position: absolute; inset: 0; pointer-events: none; z-index: 12; opacity: 0;
      background: radial-gradient(circle at 50% 42%, rgba(255,248,218,0.94) 0%, rgba(250,224,132,0.52) 38%, rgba(255,255,255,0) 76%);
      mix-blend-mode: screen;
    }}
  </style>
  <div id="root" data-composition-id="main-video" data-width="1080" data-height="1920" data-start="0" data-duration="39.75">
    <div id="rig1" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video {COLOR_GRADE_ATTR} id="v01" class="clip bg-video" src="assets/videos/s01.mp4" data-start="0" data-duration="3.75" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="rig2" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video {COLOR_GRADE_ATTR} id="v02" class="clip bg-video" src="assets/videos/s02.mp4" data-start="3.75" data-duration="6.25" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
    <div id="rig3" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video {COLOR_GRADE_ATTR} id="v03" class="clip bg-video" src="assets/videos/s03.mp4" data-start="10.0" data-duration="6.5" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="rig4a" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video {COLOR_GRADE_ATTR} id="v04a" class="clip bg-video" src="assets/videos/s04a.mp4" data-start="16.5" data-duration="4.75" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
    <div id="rig4b" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video {COLOR_GRADE_ATTR} id="v04b" class="clip bg-video" src="assets/videos/s04b.mp4" data-start="21.25" data-duration="4.5" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="rig5" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video {COLOR_GRADE_ATTR} id="v05" class="clip bg-video" src="assets/videos/s05.mp4" data-start="25.75" data-duration="7.75" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video>
    </div>
    <div id="rig6" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>
      <video {COLOR_GRADE_ATTR} id="v06" class="clip bg-video" src="assets/videos/s06.mp4" data-start="33.5" data-duration="6.25" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>
    </div>
    <div id="flare-hero" class="sun-flare" data-layout-ignore></div>
    <div id="flare-payoff" class="sun-flare" data-layout-ignore></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#rig1",  {{ scale: 1.00 }}, {{ scale: 1.05, duration: 3.75, ease: "none", immediateRender: false }}, 0.0);
    tl.fromTo("#rig2",  {{ scale: 1.04 }}, {{ scale: 1.00, duration: 6.25, ease: "none", immediateRender: false }}, 3.75);
    tl.fromTo("#rig3",  {{ scale: 1.00 }}, {{ scale: 1.05, duration: 6.50, ease: "none", immediateRender: false }}, 10.0);
    tl.fromTo("#rig4a", {{ scale: 1.00 }}, {{ scale: 1.06, duration: 4.75, ease: "none", immediateRender: false }}, 16.5);
    tl.fromTo("#rig4b", {{ scale: 1.04 }}, {{ scale: 1.00, duration: 4.50, ease: "none", immediateRender: false }}, 21.25);
    tl.fromTo("#rig5",  {{ scale: 1.00 }}, {{ scale: 1.05, duration: 7.75, ease: "none", immediateRender: false }}, 25.75);
    tl.fromTo("#rig6",  {{ scale: 1.00 }}, {{ scale: 1.05, duration: 6.25, ease: "none", immediateRender: false }}, 33.5);
    // Warm sunlit transition flashes at Hero Reveal (10.0s) & Payoff (33.5s)
    tl.fromTo("#flare-hero", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.14, ease: "power2.out", immediateRender: false }}, 9.88)
      .to("#flare-hero", {{ opacity: 0, duration: 0.24, ease: "power2.in" }}, 10.02);
    tl.fromTo("#flare-payoff", {{ opacity: 0 }}, {{ opacity: 0.78, duration: 0.14, ease: "power2.out", immediateRender: false }}, 33.38)
      .to("#flare-payoff", {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 33.52);
    window.__timelines["main-video"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "main-video.html"), "w", encoding="utf-8").write(main_vid_html)

    # 2. safe-overlays.html — GIANT CRYSTAL-CLEAR OPENING TEXT HOOK (0.00..3.60s, Frame 0 visible!) + Safe-Zone Cards!
    callouts = [
        ("c2", 4.05, 5.45, "THÓI QUEN TINH BỘT", "10H SÁNG ĐÃ UỂ OẢI?", "Thiếu đạm dễ đói sớm & tụt năng lượng"),
        ("c3", 10.22, 5.95, "AN VƯỢNG PHARMA", "AV PROTEIN THỰC VẬT", "Chiết xuất từ Đậu Hà Lan & Gạo lành tính"),
        ("c4a", 16.75, 4.25, "CÔNG THỨC ĐẬM ĐẶC / 2 GÓI", "22,05g ĐẠM • 1.632mg LEUCINE", "Hỗ trợ giữ cơ săn chắc, bền năng lượng"),
        ("c4b", 21.45, 4.00, "ĐỒNG HÀNH TẬP LUYỆN", "GIỮ DÁNG & SĂN CHẮC", "Phù hợp Pilates • Yoga • Gym • Người bận rộn"),
        ("c5", 26.05, 7.05, "ÊM BỤNG DỄ TIÊU HÓA", "INULIN + LỢI KHUẨN B-3", "Pha nước mát 20–40°C chỉ 30 giây"),
        ("c6", 33.80, 5.55, "TRẢI NGHIỆM MỖI SÁNG", "THƠM BÉO • NHẸ BỤNG", "Dễ uống mỗi ngày — Không đầy hơi"),
    ]
    c_divs = []
    c_anims = []
    for cid, st, du, tag, big, sub in callouts:
        c_divs.append(f"""
      <div id="{cid}" class="safe-card" data-layout-ignore>
        <div class="sc-tag">{tag}</div>
        <div class="sc-big">{big}</div>
        <div class="sc-sub">{sub}</div>
      </div>""")
        c_anims.append(
            f'    tl.fromTo("#{cid}", {{ opacity: 0, y: 26, scale: 0.94, filter: "blur(14px)" }}, '
            f'{{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "power3.out", immediateRender: false }}, {st})\n'
            f'      .to("#{cid}", {{ opacity: 0, y: -10, filter: "blur(10px)", duration: 0.22, ease: "power2.in" }}, {round(st + du - 0.22, 2)});'
        )

    overlays_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; pointer-events: none; font-family: 'BeVN', sans-serif; }}

    /* MASSIVE OPENING BIG TEXT HOOK (Frame 0 visible! Strict border-box X=56..870px, bottom Y=1516px: 0% face cover!) */
    .big-hook-wrap {{
      position: absolute; bottom: 404px; left: 56px; width: 814px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
      padding: 20px 18px 22px;
      background: linear-gradient(180deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.62) 100%);
      backdrop-filter: blur(6px);
      border: 3px solid rgba(255,255,255,0.82); border-radius: 30px;
      box-shadow: 0 18px 40px rgba(0,0,0,0.28); z-index: 20;
    }}
    .bh-badge {{
      background: linear-gradient(135deg, #064F34, #0F7B54); color: #FFF8D6; border: 3px solid #FFE288;
      border-radius: 999px; padding: 9px 28px; font-weight: 800; font-size: 25px;
      letter-spacing: 0.7px; box-shadow: 0 8px 20px rgba(0,0,0,0.28); margin-bottom: 12px;
    }}
    .bh-l1 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 86px; line-height: 1.06;
      color: #05472F; white-space: nowrap;
      -webkit-text-stroke: 13px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 8px 16px rgba(0,0,0,0.34));
    }}
    .bh-l2 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 82px; line-height: 1.08;
      margin-top: 6px; color: #D91A26; white-space: nowrap;
      -webkit-text-stroke: 14px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 10px 20px rgba(0,0,0,0.38));
    }}

    /* Top-left Safe Brand Watermark (Y=258px >= 250px, X=58px >= 54px) */
    .brand-chip {{
      position: absolute; top: 258px; left: 58px;
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.92); border: 2px solid #E2B448;
      border-radius: 18px; padding: 8px 18px;
      box-shadow: 0 8px 22px rgba(4,42,26,0.18);
    }}
    .brand-chip img {{ height: 48px; width: auto; display: block; }}
    .brand-chip span {{ font-weight: 800; font-size: 20px; color: #064D33; letter-spacing: 0.4px; }}

    /* Lower-Left Safe Zone Callout Card: strict border-box X=58..870px (<= 884px), Bottom Y <= 1524px */
    .safe-card {{
      position: absolute; left: 58px; bottom: 396px; width: 812px;
      background: linear-gradient(145deg, rgba(5,48,32,0.90) 0%, rgba(10,82,55,0.86) 100%);
      border: 2.5px solid #F0CA65; border-left: 8px solid #FCE078;
      border-radius: 24px; padding: 20px 24px;
      box-shadow: 0 14px 32px rgba(3,28,18,0.36);
      opacity: 0;
    }}
    .sc-tag {{
      font-weight: 800; font-size: 21px; color: #FCE186; letter-spacing: 0.8px;
      text-transform: uppercase; margin-bottom: 6px;
    }}
    .sc-big {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 42px; line-height: 1.12;
      color: #FFFFFF; text-shadow: 0 3px 10px rgba(0,0,0,0.35);
    }}
    .sc-sub {{
      font-weight: 600; font-size: 24px; color: #E4F8EE; margin-top: 6px; line-height: 1.25;
    }}
  </style>
  <div id="root" data-composition-id="safe-overlays" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <div id="big-hook" class="big-hook-wrap" data-layout-ignore>
      <div class="bh-badge">★ DINH DƯỠNG BUỔI SÁNG ★</div>
      <div class="bh-l1">ĂN ĐỦ NO</div>
      <div class="bh-l2">HAY ĐỦ ĐẠM?</div>
    </div>
    <div id="top-brand" class="brand-chip" data-layout-ignore>
      <img src="assets/images/logo_an_vuong_orig.png" alt="An Vuong" />
      <span>AV PROTEIN</span>
    </div>
    {"".join(c_divs)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#big-hook", {{ scale: 0.94, y: 8 }}, {{ scale: 1.0, y: 0, duration: 0.28, ease: "back.out(1.4)" }}, 0.0)
      .to("#big-hook", {{ opacity: 0, y: -18, filter: "blur(12px)", duration: 0.26, ease: "power2.in" }}, 3.45);
    tl.fromTo("#top-brand", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power2.out", immediateRender: false }}, 0.1)
      .to("#top-brand", {{ opacity: 0, duration: 0.25 }}, 39.45);
{chr(10).join(c_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "safe-overlays.html"), "w", encoding="utf-8").write(overlays_html)

    # 3. endcard.html (39.75..48.00s, dur=8.25s) — 100% REAL IS-Net Boxes + Bé Mẫu + Strict border-box Safe Zone 9:16!
    endcard_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: linear-gradient(165deg, #053926 0%, #0D6644 42%, #F6EFE0 42.5%, #FFFDF7 100%);
      font-family: 'BeVN', sans-serif;
    }}
    .ec-hero-bg {{
      position: absolute; inset: 0; width: 1080px; height: 1920px;
      background: radial-gradient(circle at 50% 34%, rgba(255,244,200,0.35) 0%, rgba(5,56,37,0.0) 58%),
                  linear-gradient(180deg, #043120 0%, #0A5E3E 46%, #063E29 100%);
    }}
    /* Strictly ABOVE Y=856px (0% touching right icon column!) */
    .ec-model-fade {{
      position: absolute; top: 256px; right: 58px; width: 410px; height: 594px;
      border-radius: 30px; overflow: hidden;
      border: 3.5px solid rgba(244,204,100,0.85);
      box-shadow: 0 20px 44px rgba(0,0,0,0.38);
    }}
    .ec-model-fade img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 12%; display: block; }}

    .ec-logo-top {{
      position: absolute; top: 262px; left: 58px;
      background: rgba(255,255,255,0.96); border: 3px solid #E5B442;
      border-radius: 22px; padding: 10px 22px;
      box-shadow: 0 10px 26px rgba(0,0,0,0.25);
    }}
    .ec-logo-top img {{ height: 70px; width: auto; display: block; }}

    .ec-title-wrap {{
      position: absolute; top: 382px; left: 58px; width: 520px;
    }}
    .ec-kicker {{ font-weight: 800; font-size: 23px; color: #FCE186; letter-spacing: 0.8px; }}
    .ec-brand {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 62px; line-height: 1.06;
      color: #FFFFFF; text-shadow: 0 5px 16px rgba(0,0,0,0.35); margin-top: 6px;
    }}
    .ec-sub {{ font-weight: 600; font-size: 23px; color: #DFF7EA; margin-top: 10px; line-height: 1.28; }}

    /* Real IS-Net Product Boxes (Left-Center, strictly X=58..640) */
    .ec-boxes {{
      position: absolute; left: 58px; top: 694px; width: 580px; height: 410px;
      display: flex; align-items: flex-end; gap: 18px;
    }}
    .box-main {{ height: 376px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .box-gift-wrap {{ position: relative; display: flex; flex-direction: column; align-items: center; }}
    .gift-pill {{
      background: linear-gradient(135deg, #E8232E, #A60A15); color: #FFF8DC;
      border: 2.5px solid #FFE288; border-radius: 999px; padding: 6px 18px;
      font-weight: 800; font-size: 18px; margin-bottom: 6px; white-space: nowrap;
      box-shadow: 0 6px 14px rgba(166,10,21,0.4);
    }}
    .box-gift {{ height: 262px; width: auto; filter: drop-shadow(0 16px 24px rgba(0,0,0,0.42)); }}

    /* Price + Promo + CTA Card strict border-box X=58..870 (<= 884px), bottom <= 1456px! */
    .ec-deal-card {{
      position: absolute; left: 58px; top: 1122px; width: 812px;
      background: linear-gradient(155deg, rgba(255,255,255,0.97) 0%, rgba(255,248,228,0.97) 100%);
      border: 3.5px solid #E5B442; border-radius: 28px; padding: 20px 24px;
      box-shadow: 0 18px 36px rgba(0,0,0,0.34);
    }}
    .ec-price-row {{ display: flex; align-items: center; justify-content: space-between; gap: 14px; }}
    .ec-p-left {{ display: flex; flex-direction: column; }}
    .ec-p-lbl {{ font-weight: 800; font-size: 20px; color: #074C32; }}
    .ec-p-num {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 52px; line-height: 1.05; color: #0B40A8; }}
    .ec-p-promo {{
      background: linear-gradient(135deg, #E6222B, #A80A16); border: 2.5px solid #FFE288;
      border-radius: 18px; padding: 11px 16px; text-align: center;
      box-shadow: 0 8px 18px rgba(168,10,22,0.32);
    }}
    .ec-pr-1 {{ font-weight: 800; font-size: 17px; color: #FFF3B0; }}
    .ec-pr-2 {{ font-weight: 800; font-size: 22px; color: #FFFFFF; margin-top: 2px; white-space: nowrap; }}

    .ec-cta-bar {{
      margin-top: 15px; background: linear-gradient(90deg, #074F34, #0E744E);
      border: 2.5px solid #F2CC66; border-radius: 18px; padding: 14px 18px;
      text-align: center; font-weight: 800; font-size: 24px; color: #FFF8D6;
    }}
    .ec-legal {{
      position: absolute; left: 58px; top: 1466px; width: 812px;
      font-weight: 600; font-size: 19px; line-height: 1.32; color: #E2F5EB;
      text-shadow: 0 2px 6px rgba(0,0,0,0.45);
    }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920" data-start="0" data-duration="8.25">
    <div class="ec-hero-bg"></div>
    <div id="ec-model" class="ec-model-fade" data-layout-ignore>
      <img src="assets/images/hero_mint.png" alt="An Vuong Model" />
    </div>
    <div id="ec-logo" class="ec-logo-top" data-layout-ignore>
      <img src="assets/images/logo_an_vuong_orig.png" alt="An Vuong Logo" />
    </div>
    <div id="ec-title" class="ec-title-wrap" data-layout-ignore>
      <div class="ec-kicker">THỰC PHẨM BỔ SUNG</div>
      <div class="ec-brand">AV PROTEIN</div>
      <div class="ec-sub">22,05g Đạm thực vật • 1.632mg L-Leucine • Inulin &amp; Lợi khuẩn B-3</div>
    </div>
    <div id="ec-boxes" class="ec-boxes" data-layout-ignore>
      <img id="ec-b1" class="box-main" src="assets/images/av01_protein_a.png" alt="AV Protein" />
      <div id="ec-b2" class="box-gift-wrap">
        <div class="gift-pill">★ TẶNG 1 BOJOMI</div>
        <img class="box-gift" src="assets/images/av02_bojomi_a.png" alt="Bojomi Gift" />
      </div>
    </div>
    <div id="ec-deal" class="ec-deal-card" data-layout-ignore>
      <div class="ec-price-row">
        <div class="ec-p-left">
          <div class="ec-p-lbl">HỘP 20 GÓI × 15G (300G)</div>
          <div class="ec-p-num">350.000đ</div>
        </div>
        <div class="ec-p-promo">
          <div class="ec-pr-1">CTKM 23/11 – 30/11</div>
          <div class="ec-pr-2">MUA 5 TẶNG 1 (520K)</div>
        </div>
      </div>
      <div class="ec-cta-bar">▸ NHẮN “ĐẠM SẠCH” ĐỂ ĐƯỢC TƯ VẤN NGAY!</div>
    </div>
    <div id="ec-legal" class="ec-legal" data-layout-ignore>
      {LEGAL_TPBS} • Hotline: 0867 399 268 • anvuongpharma.vn
    </div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#ec-model", {{ opacity: 0, scale: 1.06, x: 24 }}, {{ opacity: 1, scale: 1.0, x: 0, duration: 0.45, ease: "power3.out", immediateRender: false }}, 0.05)
      .fromTo("#ec-logo",  {{ opacity: 0, y: -18 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out", immediateRender: false }}, 0.12)
      .fromTo("#ec-title", {{ opacity: 0, x: -24, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.38, ease: "power3.out", immediateRender: false }}, 0.22)
      .fromTo("#ec-b1",    {{ opacity: 0, y: 36, scale: 0.90 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "back.out(1.3)", immediateRender: false }}, 0.32)
      .fromTo("#ec-b2",    {{ opacity: 0, y: 36, scale: 0.90 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "back.out(1.3)", immediateRender: false }}, 0.48)
      .fromTo("#ec-deal",  {{ opacity: 0, y: 30, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.40, ease: "power3.out", immediateRender: false }}, 0.62)
      .fromTo("#ec-legal", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.30, immediateRender: false }}, 0.85)
      .to("#ec-model", {{ scale: 1.03, duration: 7.4, ease: "none" }}, 0.60);
    window.__timelines["endcard"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "endcard.html"), "w", encoding="utf-8").write(endcard_html)
    print(f"[BUILT HF V1] {hf_dir} ({total_dur}s @ 24fps)")


def build_video_02():
    vdir = os.path.join(DAY_DIR, "video_02_combo_4sp")
    hf_dir = os.path.join(vdir, "07_HyperFrames_Project")
    comp_dir = os.path.join(hf_dir, "compositions")
    vid_dir = os.path.join(hf_dir, "assets", "videos")
    os.makedirs(comp_dir, exist_ok=True)
    sync_common_images(os.path.join(hf_dir, "assets", "images"))

    vo_data = json.loads(open(os.path.join(vdir, "06_Audio_Voiceover", "vo_manifest.json"), encoding="utf-8").read())
    segs = vo_data["segments"]
    total_dur = float(vo_data["total_duration_s"])  # 52.50s
    write_project_meta(hf_dir, "av-n01-v2-combo4sp", "Combo 4 Sản Phẩm An Vượng — Tặng Collamela 920K (Ngày 01)", total_dur)

    # Check which Flow clips exist on disk (fallback gracefully to animated studio hero/cutout stage ONLY if a clip failed!)
    has_clip = {k: os.path.exists(os.path.join(vid_dir, f"{k}.mp4")) and os.path.getsize(os.path.join(vid_dir, f"{k}.mp4")) > 100000
                for k in ["s01", "s02", "s03", "s04", "s05", "s06a"]}
    print("[V2 CLIPS AVAILABLE]", has_clip)

    bgm_split = 20.25
    bgm1_auto = build_ducking_automation(segs, 0.0, bgm_split + 0.35, True)
    bgm2_auto = build_ducking_automation(segs, bgm_split - 0.15, total_dur, False)

    vo_tags = []
    for i, s in enumerate(segs):
        tr = 5 if i % 2 == 0 else 6
        vo_tags.append(
            f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
            f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{tr}" '
            f'data-volume="1.30" data-fade-in="0.04" data-fade-out="0.06" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        )

    sfx_list = [
        ("sfx-01", "sfx_sparkle_shine.mp3", 0.18, 1.65, 9, 0.28),
        ("sfx-02", "sfx_whoosh_soft.mp3", 5.64, 0.55, 10, 0.22),
        ("sfx-03", "sfx_pop_clean.mp3", 5.95, 0.55, 11, 0.24),
        ("sfx-04", "sfx_whoosh_soft.mp3", 12.39, 0.55, 10, 0.22),
        ("sfx-05", "sfx_pop_clean.mp3", 12.75, 0.55, 11, 0.24),
        ("sfx-06", "sfx_whoosh_cinematic.mp3", 20.14, 0.90, 9, 0.26),
        ("sfx-07", "sfx_chime_warm.mp3", 20.45, 2.10, 10, 0.50),
        ("sfx-08", "sfx_whoosh_soft.mp3", 27.14, 0.55, 9, 0.22),
        ("sfx-09", "sfx_crystal_shimmer.mp3", 27.55, 2.00, 10, 0.54),
        ("sfx-10", "sfx_whoosh_cinematic.mp3", 34.64, 0.90, 9, 0.28),
        ("sfx-11", "sfx_sparkle_shine.mp3", 39.80, 1.65, 10, 0.28),
        ("sfx-12", "sfx_chime_warm.mp3", 44.60, 2.20, 10, 0.56),
        ("sfx-13", "sfx_notification_cta.mp3", 46.20, 2.10, 11, 0.22),
    ]
    sfx_tags = [
        f'      <audio id="{sid}" class="clip" src="assets/audio/{fn}" data-start="{st}" '
        f'data-duration="{du}" data-track-index="{tr}" data-volume="{vol}" data-fade-out="0.16"></audio>'
        for sid, fn, st, du, tr, vol in sfx_list
    ]

    index_html = f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Combo 4 SP An Vượng — Ngày 01</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      {LOCAL_FONT_CSS}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #042519; font-family: 'BeVN', sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .overlay-host {{ position: absolute; inset: 0; z-index: 12; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="39.75" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="combo-endcard" class="scene-host" data-composition-id="combo-endcard" data-composition-src="compositions/combo-endcard.html" data-start="39.75" data-duration="12.75" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <audio id="bgm-intro" class="clip" src="assets/audio/bgm_warm_fretless.mp3" data-start="0" data-duration="{round(bgm_split + 0.35, 2)}" data-media-start="0" data-track-index="7" data-fade-in="0.18" data-fade-out="0.35" data-fx-chain="{BGM_INTRO_FX}" data-automation="{bgm1_auto}"></audio>
      <audio id="bgm-hero" class="clip" src="assets/audio/bgm_bright_riley.mp3" data-start="{round(bgm_split - 0.15, 2)}" data-duration="{round(total_dur - bgm_split + 0.15, 2)}" data-media-start="0" data-track-index="8" data-fade-in="0.28" data-fade-out="0.85" data-fx-chain="{BGM_HERO_FX}" data-automation="{bgm2_auto}"></audio>

{chr(10).join(vo_tags)}
{chr(10).join(sfx_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    open(os.path.join(hf_dir, "index.html"), "w", encoding="utf-8").write(index_html)

    # Build shots for main-video.html (0..39.75s):
    # s01:  0.00.. 5.75 (5.75s) | s02:  5.75..12.50 (6.75s) | s03: 12.50..20.25 (7.75s)
    # s04: 20.25..27.25 (7.00s) | s05: 27.25..34.75 (7.50s) | s06a:34.75..39.75 (5.00s)
    def shot_el(key, rig_id, st, du, track, fallback_box=None):
        if has_clip[key]:
            return (
                f'    <div id="{rig_id}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>\n'
                f'      <video {COLOR_GRADE_ATTR} id="v-{key}" class="clip bg-video" src="assets/videos/{key}.mp4" '
                f'data-start="{st}" data-duration="{du}" data-media-start="0.25" data-hf-media-start-basis="local" '
                f'data-track-index="{track}" muted playsinline></video>\n'
                f'    </div>'
            )
        # Studio motion fallback (high-res real hero photo + real IS-Net box, zero blank screen!)
        box_html = f'<img class="fb-box" src="assets/images/{fallback_box}" alt="Box" />' if fallback_box else ""
        return (
            f'    <div id="{rig_id}" class="clip cam-rig fb-stage" data-start="{st}" data-duration="{du}" data-track-index="{track}" data-layout-allow-overflow data-layout-allow-overlap>\n'
            f'      <img class="bg-video" src="assets/images/hero_mint.png" alt="Hero" />\n'
            f'      {box_html}\n'
            f'    </div>'
        )

    shots_html = "\n".join([
        shot_el("s01", "rig1", 0.0, 5.75, 1),
        shot_el("s02", "rig2", 5.75, 6.75, 2, "av01_protein_a.png"),
        shot_el("s03", "rig3", 12.5, 7.75, 1, "av02_bojomi_a.png"),
        shot_el("s04", "rig4", 20.25, 7.0, 2, "av04_curcumilk_a.png"),
        shot_el("s05", "rig5", 27.25, 7.5, 1, "av03_collamela_a.png"),
        shot_el("s06a", "rig6", 34.75, 5.0, 2, "av03_collamela_a.png"),
    ])

    main_vid_html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: #05261A; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 50%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .fb-box {{
      position: absolute; left: 74px; bottom: 720px; height: 420px; width: auto;
      filter: drop-shadow(0 18px 28px rgba(0,0,0,0.42));
    }}
    .sun-flare {{
      position: absolute; inset: 0; pointer-events: none; z-index: 12; opacity: 0;
      background: radial-gradient(circle at 50% 42%, rgba(255,248,218,0.94) 0%, rgba(250,224,132,0.52) 38%, rgba(255,255,255,0) 76%);
      mix-blend-mode: screen;
    }}
  </style>
  <div id="root" data-composition-id="main-video" data-width="1080" data-height="1920" data-start="0" data-duration="39.75">
{shots_html}
    <div id="fl1" class="sun-flare" data-layout-ignore></div>
    <div id="fl2" class="sun-flare" data-layout-ignore></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#rig1", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 5.75, ease: "none", immediateRender: false }}, 0.0);
    tl.fromTo("#rig2", {{ scale: 1.04 }}, {{ scale: 1.00, duration: 6.75, ease: "none", immediateRender: false }}, 5.75);
    tl.fromTo("#rig3", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 7.75, ease: "none", immediateRender: false }}, 12.5);
    tl.fromTo("#rig4", {{ scale: 1.04 }}, {{ scale: 1.00, duration: 7.00, ease: "none", immediateRender: false }}, 20.25);
    tl.fromTo("#rig5", {{ scale: 1.00 }}, {{ scale: 1.05, duration: 7.50, ease: "none", immediateRender: false }}, 27.25);
    tl.fromTo("#rig6", {{ scale: 1.00 }}, {{ scale: 1.06, duration: 5.00, ease: "none", immediateRender: false }}, 34.75);
    tl.fromTo("#fl1", {{ opacity: 0 }}, {{ opacity: 0.80, duration: 0.14, immediateRender: false }}, 20.13)
      .to("#fl1", {{ opacity: 0, duration: 0.24 }}, 20.27);
    tl.fromTo("#fl2", {{ opacity: 0 }}, {{ opacity: 0.82, duration: 0.14, immediateRender: false }}, 34.63)
      .to("#fl2", {{ opacity: 0, duration: 0.24 }}, 34.77);
    window.__timelines["main-video"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "main-video.html"), "w", encoding="utf-8").write(main_vid_html)

    # Safe Overlays (0..39.75s) — GIANT OPENING BIG TEXT HOOK (0..5.45s, Frame 0 visible!) + Safe-Zone Cards!
    callouts = [
        ("c2", 5.98, 6.20, "1/4 • BUỔI SÁNG NĂNG LƯỢNG", "AV PROTEIN ĐẠM THỰC VẬT", "22,05g Đạm đậu Hà Lan & gạo • Nhẹ bụng giữ dáng"),
        ("c3", 12.75, 7.15, "2/4 • KHUNG XƯƠNG DẺO DAI", "BOJOMI NGŨ CỐC VỊ VANI", "Canxi tảo biển Aquamin F • D3 • K2 MK-7 • Collagen"),
        ("c4", 20.50, 6.45, "3/4 • BỮA PHỤ ẤM ÊM", "CURCUMILK PHYTO Ý", "343,2mg Curcuminoid Phytosome • Không hăng nghệ"),
        ("c5", 27.50, 6.95, "4/4 • BUỔI TỐI DƯỠNG DA", "COLLAMELA VỊ ĐÀO", "Collagen Tripeptide • HA • Vitamin C & Kẽm"),
        ("c6", 35.00, 4.50, "QUÀ TẶNG GIÁ TRỊ NHẤT", "TẶNG 1 COLLAMELA 20 GÓI", "Trị giá 920.000đ khi mua Combo 4 sản phẩm!"),
    ]
    c_divs = []
    c_anims = []
    for cid, st, du, tag, big, sub in callouts:
        c_divs.append(f"""
      <div id="{cid}" class="safe-card" data-layout-ignore>
        <div class="sc-tag">{tag}</div>
        <div class="sc-big">{big}</div>
        <div class="sc-sub">{sub}</div>
      </div>""")
        c_anims.append(
            f'    tl.fromTo("#{cid}", {{ opacity: 0, y: 26, scale: 0.94, filter: "blur(14px)" }}, '
            f'{{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.28, ease: "power3.out", immediateRender: false }}, {st})\n'
            f'      .to("#{cid}", {{ opacity: 0, y: -10, filter: "blur(10px)", duration: 0.22, ease: "power2.in" }}, {round(st + du - 0.22, 2)});'
        )

    overlays_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; pointer-events: none; font-family: 'BeVN', sans-serif; }}

    /* MASSIVE OPENING BIG TEXT HOOK (Frame 0 visible! Strict border-box X=56..870px, bottom Y=1516px: 0% face cover!) */
    .big-hook-wrap {{
      position: absolute; bottom: 404px; left: 56px; width: 814px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
      padding: 20px 18px 22px;
      background: linear-gradient(180deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.62) 100%);
      backdrop-filter: blur(6px);
      border: 3px solid rgba(255,255,255,0.82); border-radius: 30px;
      box-shadow: 0 18px 40px rgba(0,0,0,0.28); z-index: 20;
    }}
    .bh-badge {{
      background: linear-gradient(135deg, #073882, #1562DF); color: #FFF8D6; border: 3px solid #FFE288;
      border-radius: 999px; padding: 9px 26px; font-weight: 800; font-size: 24px;
      letter-spacing: 0.6px; box-shadow: 0 8px 20px rgba(0,0,0,0.28); margin-bottom: 12px;
    }}
    .bh-l1 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 68px; line-height: 1.06;
      color: #073882; white-space: nowrap;
      -webkit-text-stroke: 13px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 8px 16px rgba(0,0,0,0.34));
    }}
    .bh-l2 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 74px; line-height: 1.08;
      margin-top: 6px; color: #D91A26; white-space: nowrap;
      -webkit-text-stroke: 14px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 10px 20px rgba(0,0,0,0.38));
    }}

    .brand-chip {{
      position: absolute; top: 258px; left: 58px;
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.92); border: 2px solid #E2B448;
      border-radius: 18px; padding: 8px 18px;
      box-shadow: 0 8px 22px rgba(4,42,26,0.18);
    }}
    .brand-chip img {{ height: 48px; width: auto; display: block; }}
    .brand-chip span {{ font-weight: 800; font-size: 20px; color: #0B40A8; letter-spacing: 0.4px; }}
    .safe-card {{
      position: absolute; left: 58px; bottom: 396px; width: 812px;
      background: linear-gradient(145deg, rgba(6,44,32,0.90) 0%, rgba(12,76,54,0.86) 100%);
      border: 2.5px solid #F0CA65; border-left: 8px solid #FCE078;
      border-radius: 24px; padding: 20px 24px;
      box-shadow: 0 14px 32px rgba(3,28,18,0.36);
      opacity: 0;
    }}
    .sc-tag {{ font-weight: 800; font-size: 21px; color: #FCE186; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px; }}
    .sc-big {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 42px; line-height: 1.12; color: #FFFFFF; text-shadow: 0 3px 10px rgba(0,0,0,0.35); }}
    .sc-sub {{ font-weight: 600; font-size: 24px; color: #E4F8EE; margin-top: 6px; line-height: 1.25; }}
  </style>
  <div id="root" data-composition-id="safe-overlays" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <div id="big-hook" class="big-hook-wrap" data-layout-ignore>
      <div class="bh-badge">★ SINH NHẬT DROPPII 8 TUỔI ★</div>
      <div class="bh-l1">COMBO 4 SẢN PHẨM</div>
      <div class="bh-l2">TẶNG QUÀ 920K!</div>
    </div>
    <div id="top-brand" class="brand-chip" data-layout-ignore>
      <img src="assets/images/logo_an_vuong_orig.png" alt="An Vuong" />
      <span>× DROPPII 8 TUỔI</span>
    </div>
    {"".join(c_divs)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#big-hook", {{ scale: 0.94, y: 8 }}, {{ scale: 1.0, y: 0, duration: 0.28, ease: "back.out(1.4)" }}, 0.0)
      .to("#big-hook", {{ opacity: 0, y: -18, filter: "blur(12px)", duration: 0.26, ease: "power2.in" }}, 5.35);
    tl.fromTo("#top-brand", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power2.out", immediateRender: false }}, 0.1)
      .to("#top-brand", {{ opacity: 0, duration: 0.25 }}, 39.45);
{chr(10).join(c_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "safe-overlays.html"), "w", encoding="utf-8").write(overlays_html)

    # Studio Combo 4 SP Showcase + Droppii CTA End-Card (39.75..52.50s, dur=12.75s, 100% REAL IS-Net Boxes + Safe Zone 9:16!)
    combo_ec_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: linear-gradient(170deg, #073882 0%, #0D54B5 38%, #063827 100%);
      font-family: 'BeVN', sans-serif;
    }}
    .stage-bg {{
      position: absolute; inset: 0; width: 1080px; height: 1920px;
      object-fit: cover; opacity: 0.26;
    }}
    .hdr-wrap {{
      position: absolute; top: 256px; left: 58px; right: 58px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
    }}
    .logo-bar {{
      background: rgba(255,255,255,0.96); border: 2.5px solid #E5B442; border-radius: 20px;
      padding: 8px 24px; display: inline-flex; align-items: center; gap: 16px;
      box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }}
    .logo-bar img {{ height: 60px; width: auto; }}
    .logo-bar span {{ font-weight: 800; font-size: 32px; color: #1665F2; }}
    .ec-h1 {{
      margin-top: 16px; font-weight: 800; font-size: 54px; line-height: 1.1; color: #FFF8D4;
      text-shadow: 0 4px 16px rgba(0,0,0,0.38);
    }}
    .ec-sub {{ font-weight: 700; font-size: 25px; color: #DDF6EC; margin-top: 6px; }}

    /* 4 REAL IS-Net Boxes + PLUS + Gift Collamela 20 gói (strictly X=58..874 <= 884px, 0% touch right buttons!) */
    .combo-stage {{
      position: absolute; top: 512px; left: 58px; width: 816px; height: 498px;
      background: linear-gradient(180deg, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0.06) 100%);
      border: 2.5px solid rgba(246,208,104,0.72); border-radius: 30px;
      display: flex; align-items: center; justify-content: space-between; padding: 20px 22px;
      box-shadow: 0 20px 44px rgba(0,0,0,0.28);
    }}
    .four-grid {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 12px 14px; align-items: end;
    }}
    .four-grid img {{ height: 196px; width: auto; filter: drop-shadow(0 12px 18px rgba(0,0,0,0.38)); }}
    .plus-dot {{
      width: 56px; height: 56px; border-radius: 50%; flex-shrink: 0;
      background: linear-gradient(145deg, #FF3B3B, #B00C18); border: 4px solid #FFFFFF;
      color: #FFFFFF; font-weight: 800; font-size: 40px;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 10px 22px rgba(176,12,24,0.45);
    }}
    .gift-col {{ display: flex; flex-direction: column; align-items: center; width: 290px; }}
    .gift-badge {{
      background: linear-gradient(135deg, #E8232E, #A60A15); color: #FFF8DC;
      border: 3px solid #FFE288; border-radius: 999px; padding: 6px 18px;
      font-weight: 800; font-size: 20px; margin-bottom: 8px; white-space: nowrap;
      box-shadow: 0 8px 18px rgba(166,10,21,0.42);
    }}
    .gift-col img {{ height: 274px; width: auto; filter: drop-shadow(0 16px 26px rgba(0,0,0,0.45)); }}
    .gift-val {{
      margin-top: 8px; background: #06452D; border: 2px solid #F4CC62; border-radius: 999px;
      padding: 5px 14px; font-weight: 800; font-size: 17px; color: #FFF4C2; white-space: nowrap;
    }}

    /* Lower-left Safe Deal Card (X=58..874, bottom <= 1538px!) */
    .deal-card {{
      position: absolute; left: 58px; top: 1044px; width: 816px;
      background: linear-gradient(155deg, rgba(255,255,255,0.97), rgba(255,248,228,0.97));
      border: 3.5px solid #E5B442; border-radius: 28px; padding: 20px 26px;
      box-shadow: 0 18px 38px rgba(0,0,0,0.35);
    }}
    .price-row {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
    .p-lbl {{ font-weight: 800; font-size: 21px; color: #074C32; }}
    .p-num {{ font-weight: 800; font-size: 56px; line-height: 1.04; color: #0B40A8; }}
    .save-box {{
      background: linear-gradient(135deg, #E6222B, #A80A16); border: 2.5px solid #FFE288;
      border-radius: 18px; padding: 12px 20px; text-align: center;
    }}
    .s-1 {{ font-weight: 800; font-size: 18px; color: #FFF3B0; }}
    .s-2 {{ font-weight: 800; font-size: 32px; color: #FFFFFF; line-height: 1.08; }}

    .droppii-note {{
      margin-top: 16px; background: linear-gradient(90deg, #074F34, #0E744E);
      border: 2.5px solid #F2CC66; border-radius: 18px; padding: 14px 20px;
      text-align: center;
    }}
    .dn-1 {{ font-weight: 800; font-size: 24px; color: #FFF5C2; }}
    .dn-2 {{ font-weight: 700; font-size: 20px; color: #FFFFFF; margin-top: 4px; }}

    .ec-legal {{
      position: absolute; left: 58px; top: 1446px; width: 816px;
      font-weight: 600; font-size: 19px; line-height: 1.32; color: #E2F5EB;
      text-shadow: 0 2px 6px rgba(0,0,0,0.45);
    }}
  </style>
  <div id="root" data-composition-id="combo-endcard" data-width="1080" data-height="1920" data-start="0" data-duration="12.75">
    <img class="stage-bg" src="assets/images/stage_bg.png" alt="Stage" />
    <div id="ce-hdr" class="hdr-wrap" data-layout-ignore>
      <div class="logo-bar">
        <img src="assets/images/logo_an_vuong_orig.png" alt="An Vuong" />
        <span>× droppii 8 Tuổi</span>
      </div>
      <div class="ec-h1">COMBO 4 SẢN PHẨM TOÀN DIỆN</div>
      <div class="ec-sub">Chăm trọn Đạm • Xương Khớp • Tiêu Hóa • Làn Da</div>
    </div>

    <div id="ce-stage" class="combo-stage" data-layout-ignore>
      <div class="four-grid">
        <img id="cb1" src="assets/images/av01_protein_a.png" alt="AV Protein" />
        <img id="cb2" src="assets/images/av02_bojomi_a.png" alt="Bojomi" />
        <img id="cb3" src="assets/images/av04_curcumilk_a.png" alt="Curcumilk" />
        <img id="cb4" src="assets/images/av03_collamela_a.png" alt="Collamela" />
      </div>
      <div id="cplus" class="plus-dot">+</div>
      <div id="cgift" class="gift-col">
        <div class="gift-badge">★ TẶNG NGAY</div>
        <img src="assets/images/av03_collamela_a.png" alt="Collamela 20 Goi" />
        <div class="gift-val">COLLAMELA 20 GÓI • 920K</div>
      </div>
    </div>

    <div id="ce-deal" class="deal-card" data-layout-ignore>
      <div class="price-row">
        <div>
          <div class="p-lbl">TỔNG COMBO 4 SẢN PHẨM</div>
          <div class="p-num">2.440.000đ</div>
        </div>
        <div class="save-box">
          <div class="s-1">TIẾT KIỆM NGAY</div>
          <div class="s-2">920.000đ</div>
        </div>
      </div>
      <div class="droppii-note">
        <div class="dn-1">✓ CHỌN ĐÚNG MÃ COMBO TRÊN APP DROPPII</div>
        <div class="dn-2">Áp dụng 23/11 – 30/11/2026 • Kiểm tra hiện quà 0đ trước khi chốt đơn</div>
      </div>
    </div>

    <div id="ce-legal" class="ec-legal" data-layout-ignore>
      {LEGAL_TPBS} • Hotline: 0867 399 268 • anvuongpharma.vn
    </div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#ce-hdr",   {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.40, ease: "power3.out", immediateRender: false }}, 0.08)
      .fromTo("#ce-stage", {{ opacity: 0, scale: 0.94 }}, {{ opacity: 1, scale: 1.0, duration: 0.42, ease: "power3.out", immediateRender: false }}, 0.18)
      .fromTo("#cb1", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "back.out(1.4)", immediateRender: false }}, 0.28)
      .fromTo("#cb2", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "back.out(1.4)", immediateRender: false }}, 0.40)
      .fromTo("#cb3", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "back.out(1.4)", immediateRender: false }}, 0.52)
      .fromTo("#cb4", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "back.out(1.4)", immediateRender: false }}, 0.64)
      .fromTo("#cplus", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1.0, duration: 0.28, ease: "back.out(1.7)", immediateRender: false }}, 0.78)
      .fromTo("#cgift", {{ opacity: 0, y: 30, scale: 0.88 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "back.out(1.4)", immediateRender: false }}, 0.90)
      .fromTo("#ce-deal", {{ opacity: 0, y: 28, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.40, ease: "power3.out", immediateRender: false }}, 1.05)
      .fromTo("#ce-legal", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.30, immediateRender: false }}, 1.25);
    window.__timelines["combo-endcard"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "combo-endcard.html"), "w", encoding="utf-8").write(combo_ec_html)
    print(f"[BUILT HF V2] {hf_dir} ({total_dur}s @ 24fps)")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("v1", "both"):
        build_video_01()
    if which in ("v2", "both"):
        build_video_02()
