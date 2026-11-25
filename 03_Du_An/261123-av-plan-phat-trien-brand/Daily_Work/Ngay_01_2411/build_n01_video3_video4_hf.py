"""
Dựng HyperFrames 24fps (1080x1920) cho Video 03 (Bojomi) & Video 04 (Collamela) — Ngày 01 (24/11/2026):
- Video 03 (Bojomi): Look #2 Công sở kem sữa + búi thấp + bông tai ngọc trai + dây vàng (53.50s @ 24fps)
- Video 04 (Collamela): Look #3 Đầm lụa hồng đào + xoăn kẹp ngọc trai + bông tai hoa pha lê (49.50s @ 24fps)
ĐẶC BIỆT:
1. TEXT HOOK ĐẦU TIÊN CỰC TO RÕ RÀNG (86px-94px viền trắng dày nổi khối, xuất hiện ngay Frame 0 trên vùng tường trống trên đầu mẫu, 100% Vùng An Toàn 9:16!).
2. Toàn bộ thẻ callout nửa dưới giữ gọn trong X = 58..874px, Y <= 1534px (0% chạm cột nút tương tác TikTok/Reels).
3. End-Card ghép 100% hộp thật IS-Net (av02_bojomi_b.png / av03_collamela_b.png) + dòng pháp lý TPBS chuẩn.
4. BGM 2 nửa C-Major + EQ Voice Pocket + Dynamic Ducking + 10 Studio Micro-SFX.
"""
import os, sys, json, shutil

DAY_DIR = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_01_2411"
CUTOUT_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG"
ASSETS_DIR = os.path.join(DAY_DIR, "01_ChatGPT_Assets")
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


VO_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "highpass", "id": "vhp", "params": {"frequency": 85}},
        {"type": "peaking", "id": "vlow", "params": {"frequency": 210, "gain": -1.8, "q": 1.1}},
        {"type": "peaking", "id": "vpres", "params": {"frequency": 3100, "gain": 1.8, "q": 1.0}},
        {"type": "limiter", "id": "vlim", "params": {"limit": -1.0}},
    ],
})
BGM1_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "gain", "id": "bg1", "params": {"gain": 6.8}},
        {"type": "highpass", "id": "bh1", "params": {"frequency": 75}},
        {"type": "peaking", "id": "bc1", "params": {"frequency": 2300, "gain": -3.6, "q": 0.85}},
        {"type": "limiter", "id": "bl1", "params": {"limit": -2.5}},
    ],
})
BGM2_FX = html_json({
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
"""


def build_ducking(segs, clip_start, clip_end, is_first):
    pts = [{"t": 0.0, "v": 0.58 if is_first else 0.60}]
    dur = round(clip_end - clip_start, 2)
    for seg in segs:
        st, en = seg["start_s"] - clip_start, seg["end_s"] - clip_start
        if en <= 0.05 or st >= dur - 0.05:
            continue
        t_in = max(0.05, round(st - 0.16, 2))
        t_dk = max(t_in + 0.02, round(st, 2))
        t_rl = min(dur - 0.12, round(en, 2))
        t_up = min(dur - 0.05, round(en + 0.24, 2))
        if t_in > pts[-1]["t"] + 0.04: pts.append({"t": t_in, "v": 0.54})
        if t_dk > pts[-1]["t"] + 0.02: pts.append({"t": t_dk, "v": 0.34})
        if t_rl > pts[-1]["t"] + 0.02: pts.append({"t": t_rl, "v": 0.34})
        if t_up > pts[-1]["t"] + 0.02: pts.append({"t": t_up, "v": 0.54})
    if is_first:
        if pts[-1]["t"] < dur - 0.35: pts.append({"t": round(dur - 0.35, 2), "v": 0.36})
        pts.append({"t": dur, "v": 0.0})
    else:
        if pts[-1]["t"] < dur - 0.85: pts.append({"t": round(dur - 0.85, 2), "v": 0.74})
        pts.append({"t": dur, "v": 0.76})
    return html_json({"version": 1, "lanes": [{"target": "volume", "points": pts}]})


def build_usp_video(cfg: dict):
    vdir = os.path.join(DAY_DIR, cfg["vkey"])
    hf_dir = os.path.join(vdir, "07_HyperFrames_Project")
    comp_dir = os.path.join(hf_dir, "compositions")
    img_dir = os.path.join(hf_dir, "assets", "images")
    vid_dir = os.path.join(hf_dir, "assets", "videos")
    os.makedirs(comp_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    for src_p, dst_n in cfg["copy_images"]:
        shutil.copy2(src_p, os.path.join(img_dir, dst_n))

    vo_data = json.loads(open(os.path.join(vdir, "06_Audio_Voiceover", "vo_manifest.json"), encoding="utf-8").read())
    segs = vo_data["segments"]
    total_dur = float(vo_data["total_duration_s"])
    end_start = float(cfg["endcard_start"])
    end_dur = round(total_dur - end_start, 2)

    json.dump({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": False}, "authoringSkill": "hyperframes",
    }, open(os.path.join(hf_dir, "hyperframes.json"), "w", encoding="utf-8"), indent=2)
    json.dump({
        "name": cfg["slug"], "private": True, "type": "module",
        "scripts": {"check": "npx --yes hyperframes@0.9.38 check", "render": "npx --yes hyperframes@0.9.38 render"},
    }, open(os.path.join(hf_dir, "package.json"), "w", encoding="utf-8"), indent=2)
    json.dump({"title": cfg["title"], "width": 1080, "height": 1920, "fps": 24, "duration": total_dur},
              open(os.path.join(hf_dir, "meta.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    bgm_split = cfg["bgm_split"]
    bgm1_auto = build_ducking(segs, 0.0, bgm_split + 0.35, True)
    bgm2_auto = build_ducking(segs, bgm_split - 0.15, total_dur, False)

    vo_tags = [
        f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
        f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{5 if i%2==0 else 6}" '
        f'data-volume="1.30" data-fade-in="0.04" data-fade-out="0.06" data-fx-chain="{VO_FX}"></audio>'
        for i, s in enumerate(segs)
    ]
    sfx_tags = [
        f'      <audio id="{sid}" class="clip" src="assets/audio/{fn}" data-start="{st}" '
        f'data-duration="{du}" data-track-index="{tr}" data-volume="{vol}" data-fade-out="0.16"></audio>'
        for sid, fn, st, du, tr, vol in cfg["sfx"]
    ]

    index_html = f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{cfg["title"]}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      {LOCAL_FONT_CSS}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: {cfg["bg_dark"]}; font-family: 'BeVN', sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .overlay-host {{ position: absolute; inset: 0; z-index: 12; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="{end_start}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene-host" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{end_start}" data-duration="{end_dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <audio id="bgm-intro" class="clip" src="assets/audio/bgm_warm_fretless.mp3" data-start="0" data-duration="{round(bgm_split + 0.35, 2)}" data-media-start="0" data-track-index="7" data-fade-in="0.18" data-fade-out="0.35" data-fx-chain="{BGM1_FX}" data-automation="{bgm1_auto}"></audio>
      <audio id="bgm-hero" class="clip" src="assets/audio/bgm_bright_riley.mp3" data-start="{round(bgm_split - 0.15, 2)}" data-duration="{round(total_dur - bgm_split + 0.15, 2)}" data-media-start="0" data-track-index="8" data-fade-in="0.28" data-fade-out="0.85" data-fx-chain="{BGM2_FX}" data-automation="{bgm2_auto}"></audio>

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

    # 1. main-video.html (7 unique Flow clips)
    shot_els, shot_anims = [], []
    for idx, (sfile, st, du) in enumerate(cfg["shots"]):
        rid = f"rig{idx+1}"
        tr = 1 if idx % 2 == 0 else 2
        p_mp4 = os.path.join(vid_dir, sfile)
        if os.path.exists(p_mp4) and os.path.getsize(p_mp4) > 100000:
            shot_els.append(
                f'    <div id="{rid}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>\n'
                f'      <video {COLOR_GRADE_ATTR} id="v{idx+1}" class="clip bg-video" src="assets/videos/{sfile}" '
                f'data-start="{st}" data-duration="{du}" data-media-start="0.25" data-hf-media-start-basis="local" '
                f'data-track-index="{tr}" muted playsinline></video>\n'
                f'    </div>'
            )
        else:
            shot_els.append(
                f'    <div id="{rid}" class="clip cam-rig" data-start="{st}" data-duration="{du}" data-track-index="{tr}" data-layout-allow-overflow data-layout-allow-overlap>\n'
                f'      <img class="bg-video" src="assets/images/hero_look.png" alt="Hero" />\n'
                f'    </div>'
            )
        s0, s1 = (1.00, 1.05) if idx % 2 == 0 else (1.04, 1.00)
        shot_anims.append(f'    tl.fromTo("#{rid}", {{ scale: {s0} }}, {{ scale: {s1}, duration: {du}, ease: "none", immediateRender: false }}, {st});')

    fl1_t, fl2_t = cfg["flares"]
    main_vid_html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: {cfg["bg_dark"]}; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 50%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .sun-flare {{
      position: absolute; inset: 0; pointer-events: none; z-index: 12; opacity: 0;
      background: radial-gradient(circle at 50% 42%, rgba(255,248,218,0.94) 0%, rgba(250,224,132,0.52) 38%, rgba(255,255,255,0) 76%);
      mix-blend-mode: screen;
    }}
  </style>
  <div id="root" data-composition-id="main-video" data-width="1080" data-height="1920" data-start="0" data-duration="{end_start}">
{chr(10).join(shot_els)}
    <div id="fl1" class="sun-flare" data-layout-ignore></div>
    <div id="fl2" class="sun-flare" data-layout-ignore></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(shot_anims)}
    tl.fromTo("#fl1", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.14, immediateRender: false }}, {round(fl1_t - 0.12, 2)})
      .to("#fl1", {{ opacity: 0, duration: 0.24 }}, {round(fl1_t + 0.02, 2)});
    tl.fromTo("#fl2", {{ opacity: 0 }}, {{ opacity: 0.80, duration: 0.14, immediateRender: false }}, {round(fl2_t - 0.12, 2)})
      .to("#fl2", {{ opacity: 0, duration: 0.24 }}, {round(fl2_t + 0.02, 2)});
    window.__timelines["main-video"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "main-video.html"), "w", encoding="utf-8").write(main_vid_html)

    # 2. safe-overlays.html — GIANT CRYSTAL-CLEAR OPENING TEXT HOOK (Frame 0 visible!) + Safe-Zone Lower Cards!
    hk = cfg["big_hook"]
    c_divs, c_anims = [], []
    for cid, st, du, tag, big, sub in cfg["callouts"]:
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

    /* MASSIVE OPENING BIG TEXT HOOK (Frame 0 visible! Sits lower-chest X=56..870px, Y~1120..1512px: 100% Safe Zone & 0% covering face!) */
    .big-hook-wrap {{
      position: absolute; bottom: 404px; left: 56px; width: 814px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
      padding: 20px 18px 22px;
      background: linear-gradient(180deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.62) 100%);
      backdrop-filter: blur(6px);
      border: 3px solid rgba(255,255,255,0.82); border-radius: 30px;
      box-shadow: 0 18px 40px rgba(0,0,0,0.28);
      z-index: 20;
    }}
    .bh-badge {{
      background: {hk["badge_bg"]}; color: #FFF8D6; border: 3px solid #FFE288;
      border-radius: 999px; padding: 9px 28px; font-weight: 800; font-size: 25px;
      letter-spacing: 0.7px; box-shadow: 0 8px 20px rgba(0,0,0,0.28); margin-bottom: 12px;
    }}
    .bh-l1 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: {hk["s1"]}px; line-height: 1.06;
      color: {hk["c1"]}; white-space: nowrap;
      -webkit-text-stroke: 13px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 8px 16px rgba(0,0,0,0.34));
    }}
    .bh-l2 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: {hk["s2"]}px; line-height: 1.08;
      margin-top: 6px; color: {hk["c2"]}; white-space: nowrap;
      -webkit-text-stroke: 14px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 10px 20px rgba(0,0,0,0.38));
    }}

    /* Top-Left Brand Chip (appears right after Opening Hook clears at ~4.0s!) */
    .brand-chip {{
      position: absolute; top: 258px; left: 58px; opacity: 0;
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.94); border: 2.5px solid #E2B448;
      border-radius: 18px; padding: 8px 18px;
      box-shadow: 0 8px 22px rgba(0,0,0,0.20);
    }}
    .brand-chip img {{ height: 48px; width: auto; display: block; }}
    .brand-chip span {{ font-weight: 800; font-size: 20px; color: {cfg["chip_txt_color"]}; letter-spacing: 0.4px; }}

    /* Lower-Left Safe Callout Card (strict border-box X=58..870px <= 884px, bottom Y <= 1526px <= 1548px!) */
    .safe-card {{
      position: absolute; left: 58px; bottom: 396px; width: 812px;
      background: {cfg["card_bg"]};
      border: 2.5px solid #F0CA65; border-left: 9px solid #FCE078;
      border-radius: 24px; padding: 20px 24px;
      box-shadow: 0 14px 32px rgba(0,0,0,0.38); opacity: 0;
    }}
    .sc-tag {{ font-weight: 800; font-size: 21px; color: #FCE186; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px; }}
    .sc-big {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 42px; line-height: 1.12; color: #FFFFFF; text-shadow: 0 3px 10px rgba(0,0,0,0.38); }}
    .sc-sub {{ font-weight: 600; font-size: 24px; color: #EFFBF4; margin-top: 6px; line-height: 1.24; }}
  </style>
  <div id="root" data-composition-id="safe-overlays" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <div id="big-hook" class="big-hook-wrap" data-layout-ignore>
      <div class="bh-badge">{hk["badge"]}</div>
      <div class="bh-l1">{hk["l1"]}</div>
      <div class="bh-l2">{hk["l2"]}</div>
    </div>
    <div id="top-brand" class="brand-chip" data-layout-ignore>
      <img src="assets/images/logo_an_vuong_orig.png" alt="An Vuong" />
      <span>{cfg["brand_chip_label"]}</span>
    </div>
    {"".join(c_divs)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Opening Giant Hook: visible immediately on Frame 0 (pop punch-in 0.94 -> 1.00), cleanly exits at 3.85s
    tl.fromTo("#big-hook", {{ scale: 0.94, y: 8 }}, {{ scale: 1.0, y: 0, duration: 0.28, ease: "back.out(1.4)" }}, 0.0)
      .to("#big-hook", {{ opacity: 0, y: -18, filter: "blur(12px)", duration: 0.26, ease: "power2.in" }}, {round(hk["end_s"] - 0.26, 2)});
    tl.fromTo("#top-brand", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power2.out", immediateRender: false }}, {round(hk["end_s"] + 0.05, 2)})
      .to("#top-brand", {{ opacity: 0, duration: 0.25 }}, {round(end_start - 0.28, 2)});
{chr(10).join(c_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "safe-overlays.html"), "w", encoding="utf-8").write(overlays_html)

    # 3. endcard.html (100% REAL IS-Net Boxes + Look Portrait + 100% TikTok/Reels Safe Zone!)
    ec = cfg["endcard"]
    endcard_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: {ec["bg"]}; font-family: 'BeVN', sans-serif;
    }}
    /* Model portrait strictly ABOVE Y=856px (0% touching lower-right TikTok buttons!) */
    .ec-model {{
      position: absolute; top: 256px; right: 58px; width: 410px; height: 594px;
      border-radius: 30px; overflow: hidden; border: 3.5px solid rgba(244,204,100,0.88);
      box-shadow: 0 20px 44px rgba(0,0,0,0.38);
    }}
    .ec-model img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 16%; display: block; }}
    .ec-logo {{
      position: absolute; top: 262px; left: 58px;
      background: rgba(255,255,255,0.96); border: 3px solid #E5B442; border-radius: 22px;
      padding: 10px 22px; box-shadow: 0 10px 26px rgba(0,0,0,0.25);
    }}
    .ec-logo img {{ height: 70px; width: auto; display: block; }}
    .ec-title {{ position: absolute; top: 378px; left: 58px; width: 520px; }}
    .ec-kicker {{ font-weight: 800; font-size: 23px; color: #FCE186; letter-spacing: 0.7px; }}
    .ec-brand {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 62px; line-height: 1.06;
      color: #FFFFFF; text-shadow: 0 5px 16px rgba(0,0,0,0.35); margin-top: 6px;
    }}
    .ec-sub {{ font-weight: 600; font-size: 23px; color: #E8F8F0; margin-top: 10px; line-height: 1.28; }}

    /* Real IS-Net Boxes strictly X=58..640px (100% clear of right icon column!) */
    .ec-boxes {{
      position: absolute; left: 58px; top: 694px; width: 580px; height: 410px;
      display: flex; align-items: flex-end; gap: 22px;
    }}
    .b-main {{ height: 376px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .b-gift-w {{ display: flex; flex-direction: column; align-items: center; }}
    .g-pill {{
      background: linear-gradient(135deg, #E8232E, #A60A15); color: #FFF8DC;
      border: 2.5px solid #FFE288; border-radius: 999px; padding: 6px 18px;
      font-weight: 800; font-size: 18px; margin-bottom: 6px; white-space: nowrap;
      box-shadow: 0 6px 14px rgba(166,10,21,0.4);
    }}
    .b-gift {{ height: 262px; width: auto; filter: drop-shadow(0 16px 24px rgba(0,0,0,0.42)); }}

    /* Deal Card strict border-box X=58..870px (<= 884px), bottom <= 1456px! */
    .ec-deal {{
      position: absolute; left: 58px; top: 1122px; width: 812px;
      background: linear-gradient(155deg, rgba(255,255,255,0.97), rgba(255,248,228,0.97));
      border: 3.5px solid #E5B442; border-radius: 28px; padding: 20px 24px;
      box-shadow: 0 18px 36px rgba(0,0,0,0.34);
    }}
    .ec-prow {{ display: flex; align-items: center; justify-content: space-between; gap: 14px; }}
    .ep-l {{ font-weight: 800; font-size: 20px; color: #074C32; }}
    .ep-n {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 52px; line-height: 1.04; color: #0B40A8; }}
    .ep-pr {{
      background: linear-gradient(135deg, #E6222B, #A80A16); border: 2.5px solid #FFE288;
      border-radius: 18px; padding: 11px 16px; text-align: center;
      box-shadow: 0 8px 18px rgba(168,10,22,0.32);
    }}
    .ep-1 {{ font-weight: 800; font-size: 17px; color: #FFF3B0; }}
    .ep-2 {{ font-weight: 800; font-size: 22px; color: #FFFFFF; margin-top: 2px; white-space: nowrap; }}
    .ec-cta {{
      margin-top: 15px; background: {ec["cta_bg"]};
      border: 2.5px solid #F2CC66; border-radius: 18px; padding: 14px 18px;
      text-align: center; font-weight: 800; font-size: 24px; color: #FFF8D6;
    }}
    .ec-legal {{
      position: absolute; left: 58px; top: 1466px; width: 812px;
      font-weight: 600; font-size: 19px; line-height: 1.32; color: #EFFBF4;
      text-shadow: 0 2px 6px rgba(0,0,0,0.45);
    }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920" data-start="0" data-duration="{end_dur}">
    <div id="ec-m" class="ec-model" data-layout-ignore><img src="assets/images/hero_look.png" alt="Model" /></div>
    <div id="ec-l" class="ec-logo" data-layout-ignore><img src="assets/images/logo_an_vuong_orig.png" alt="Logo" /></div>
    <div id="ec-t" class="ec-title" data-layout-ignore>
      <div class="ec-kicker">{ec["kicker"]}</div>
      <div class="ec-brand">{ec["brand"]}</div>
      <div class="ec-sub">{ec["sub"]}</div>
    </div>
    <div id="ec-b" class="ec-boxes" data-layout-ignore>
      <img id="eb1" class="b-main" src="assets/images/{ec["box_main"]}" alt="Main" />
      <div id="eb2" class="b-gift-w">
        <div class="g-pill">{ec["gift_pill"]}</div>
        <img class="b-gift" src="assets/images/{ec["box_gift"]}" alt="Gift" />
      </div>
    </div>
    <div id="ec-d" class="ec-deal" data-layout-ignore>
      <div class="ec-prow">
        <div>
          <div class="ep-l">{ec["spec_lbl"]}</div>
          <div class="ep-n">{ec["price"]}</div>
        </div>
        <div class="ep-pr">
          <div class="ep-1">CTKM 23/11 – 30/11</div>
          <div class="ep-2">{ec["promo"]}</div>
        </div>
      </div>
      <div class="ec-cta">{ec["cta"]}</div>
    </div>
    <div id="ec-g" class="ec-legal" data-layout-ignore>{LEGAL_TPBS} • Hotline: 0867 399 268 • anvuongpharma.vn</div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#ec-m", {{ opacity: 0, scale: 1.06, x: 24 }}, {{ opacity: 1, scale: 1.0, x: 0, duration: 0.45, ease: "power3.out", immediateRender: false }}, 0.05)
      .fromTo("#ec-l", {{ opacity: 0, y: -18 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out", immediateRender: false }}, 0.12)
      .fromTo("#ec-t", {{ opacity: 0, x: -24, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.38, ease: "power3.out", immediateRender: false }}, 0.22)
      .fromTo("#eb1",  {{ opacity: 0, y: 36, scale: 0.90 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "back.out(1.3)", immediateRender: false }}, 0.32)
      .fromTo("#eb2",  {{ opacity: 0, y: 36, scale: 0.90 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "back.out(1.3)", immediateRender: false }}, 0.48)
      .fromTo("#ec-d", {{ opacity: 0, y: 30, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.40, ease: "power3.out", immediateRender: false }}, 0.62)
      .fromTo("#ec-g", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.30, immediateRender: false }}, 0.85)
      .to("#ec-m", {{ scale: 1.03, duration: {round(end_dur - 0.6, 2)}, ease: "none" }}, 0.60);
    window.__timelines["endcard"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "endcard.html"), "w", encoding="utf-8").write(endcard_html)
    print(f"[BUILT HF {cfg['vkey']}] {hf_dir} ({total_dur}s @ 24fps)")


V3_CFG = {
    "vkey": "video_03_bojomi",
    "slug": "av-n01-v3-bojomi",
    "title": "Bojomi — Canxi Tảo Biển Aquamin F + D3 + K2 MK-7 (Ngày 01)",
    "bg_dark": "#042519",
    "bgm_split": 10.00,
    "endcard_start": 44.50,
    "flares": (10.00, 37.50),
    "chip_txt_color": "#064D33",
    "brand_chip_label": "BOJOMI CANXI",
    "card_bg": "linear-gradient(145deg, rgba(5,48,32,0.90) 0%, rgba(10,82,55,0.86) 100%)",
    "copy_images": [
        (os.path.join(ASSETS_DIR, "N01_LOOK2_BOJOMI_9x16.png"), "hero_look.png"),
        (os.path.join(CUTOUT_DIR, "av02_bojomi_b.png"), "box_main.png"),
        (os.path.join(CUTOUT_DIR, "logo_an_vuong_orig.png"), "logo_an_vuong_orig.png"),
    ],
    "shots": [
        ("s01.mp4", 0.0, 4.0),
        ("s02.mp4", 4.0, 6.0),
        ("s03.mp4", 10.0, 7.0),
        ("s04a.mp4", 17.0, 5.5),
        ("s04b.mp4", 22.5, 5.5),
        ("s05.mp4", 28.0, 9.5),
        ("s06.mp4", 37.5, 7.0),
    ],
    "big_hook": {
        "badge": "★ BÍ KÍP CHỌN CANXI CHUẨN ★",
        "l1": "CHỌN CANXI",
        "l2": "ĐỪNG NHÌN MILIGAM!",
        "c1": "#05472F", "c2": "#D91A26",
        "s1": 88, "s2": 66,
        "badge_bg": "linear-gradient(135deg, #064F34, #0F7B54)",
        "end_s": 3.85,
    },
    "callouts": [
        ("c2", 4.20, 5.40, "ĐỌC KỸ NHÃN TRƯỚC KHI UỐNG", "THIẾU BỘ DẪN ĐƯỜNG?", "Uống Canxi mãi vẫn dễ nặng bụng, khó hấp thu"),
        ("c3", 10.22, 6.30, "AN VƯỢNG PHARMA", "BOJOMI CANXI TẢO BIỂN", "Aquamin F + Vitamin D3 + K2 MK-7 chuẩn khoa học"),
        ("c4a", 17.25, 4.95, "HÀM LƯỢNG CHUẨN / 1 GÓI 20G", "417,6mg CANXI • D3 • K2 MK-7", "779,4 IU D3 & 169,8µg K2 MK-7 hỗ trợ hấp thu"),
        ("c4b", 22.75, 4.95, "NGŨ CỐC VỊ VANI THƠM BÉO", "BỔ SUNG 201,4mg COLLAGEN", "Dạng bột pha dễ dùng cho cả nhà & bố mẹ lớn tuổi"),
        ("c5", 28.30, 8.70, "CÁCH PHA CHUẨN 30 GIÂY", "200ML NƯỚC ẤM 60°C", "Bột tan mịn thơm ngon — Không vón, không ngán"),
        ("c6", 37.80, 6.20, "CHĂM KHUNG XƯƠNG DẺO DAI", "TIỆN LỢI MỖI NGÀY", "Đóng 14 gói nhỏ gọn mang đi làm hay du lịch"),
    ],
    "sfx": [
        ("sfx-01", "sfx_pop_clean.mp3", 0.12, 0.55, 9, 0.24),
        ("sfx-02", "sfx_whoosh_soft.mp3", 3.89, 0.55, 9, 0.22),
        ("sfx-03", "sfx_whoosh_cinematic.mp3", 9.88, 0.90, 9, 0.28),
        ("sfx-04", "sfx_sparkle_shine.mp3", 10.08, 1.65, 10, 0.26),
        ("sfx-05", "sfx_crystal_shimmer.mp3", 17.20, 2.00, 10, 0.54),
        ("sfx-06", "sfx_ping_glass.mp3", 22.50, 0.85, 11, 0.24),
        ("sfx-07", "sfx_whoosh_soft.mp3", 27.89, 0.55, 9, 0.22),
        ("sfx-08", "sfx_chime_warm.mp3", 37.55, 2.20, 10, 0.52),
        ("sfx-09", "sfx_whoosh_cinematic.mp3", 44.38, 0.90, 9, 0.28),
        ("sfx-10", "sfx_sparkle_shine.mp3", 44.70, 1.65, 10, 0.28),
        ("sfx-11", "sfx_notification_cta.mp3", 46.20, 2.10, 11, 0.22),
    ],
    "endcard": {
        "bg": "linear-gradient(175deg, #043120 0%, #0A5E3E 48%, #053A26 100%)",
        "kicker": "NGŨ CỐC DINH DƯỠNG",
        "brand": "BOJOMI",
        "sub": "417,6mg Canxi tảo biển Aquamin F • D3 • K2 MK-7 • Collagen",
        "box_main": "box_main.png", "box_gift": "box_main.png",
        "gift_pill": "★ TẶNG 1 BOJOMI",
        "spec_lbl": "HỘP 14 GÓI × 20G (280G)",
        "price": "520.000đ",
        "promo": "MUA 3 TẶNG 1 (520K)",
        "cta_bg": "linear-gradient(90deg, #074F34, #0E744E)",
        "cta": "▸ NHẮN “BOJOMI” XEM NHÃN & NHẬN ƯU ĐÃI!",
    },
}

V4_CFG = {
    "vkey": "video_04_collamela",
    "slug": "av-n01-v4-collamela",
    "title": "Collamela — Collagen Tripeptide + HA + C + Kẽm Đón Tết (Ngày 01)",
    "bg_dark": "#3A061C",
    "bgm_split": 11.50,
    "endcard_start": 39.75,
    "flares": (11.50, 33.50),
    "chip_txt_color": "#9A0F4A",
    "brand_chip_label": "COLLAMELA VỊ ĐÀO",
    "card_bg": "linear-gradient(145deg, rgba(96,10,48,0.90) 0%, rgba(148,22,74,0.86) 100%)",
    "copy_images": [
        (os.path.join(ASSETS_DIR, "N01_LOOK3_COLLAMELA_9x16.png"), "hero_look.png"),
        (os.path.join(CUTOUT_DIR, "av03_collamela_b.png"), "box_main.png"),
        (os.path.join(CUTOUT_DIR, "logo_an_vuong_orig.png"), "logo_an_vuong_orig.png"),
    ],
    "shots": [
        ("s01.mp4", 0.0, 4.0),
        ("s02.mp4", 4.0, 7.5),
        ("s03.mp4", 11.5, 6.5),
        ("s04a.mp4", 18.0, 4.5),
        ("s04b.mp4", 22.5, 4.25),
        ("s05.mp4", 26.75, 6.75),
        ("s06.mp4", 33.5, 6.25),
    ],
    "big_hook": {
        "badge": "✦ CÒN 60 NGÀY TỚI TẾT 2027 ✦",
        "l1": "SẮP TIỆC MỚI CHĂM DA",
        "l2": "LÀ ĐÃ MUỘN RỒI!",
        "c1": "#7C0839", "c2": "#D91A42",
        "s1": 60, "s2": 76,
        "badge_bg": "linear-gradient(135deg, #A3144F, #DF2D72)",
        "end_s": 3.85,
    },
    "callouts": [
        ("c2", 4.25, 6.80, "60 NGÀY ĐÓN TẾT XINH", "NUÔI DA TỪ GỐC NGAY HÔM NAY", "Đừng đợi 28 Tết mới vội tìm cách cấp tốc!"),
        ("c3", 11.75, 5.90, "AN VƯỢNG PHARMA", "COLLAMELA TRIPEPTIDE", "Collagen phân tử nhỏ giúp cơ thể dễ dàng hấp thu"),
        ("c4a", 18.20, 4.05, "BỘ 4 DƯỠNG CHẤT / 2 GÓI", "2.530mg COLLAGEN • 25,68mg HA", "Kết hợp 87mg Vitamin C & 3,9mg Kẽm"),
        ("c4b", 22.70, 3.80, "CHĂM SẮC BỀN VỮNG", "CẤP ẨM & ĐÀN HỒI LÀN DA", "Giúp da luôn ẩm mịn, tươi tắn rạng rỡ"),
        ("c5", 27.00, 6.10, "VỊ ĐÀO THANH MÁT", "PHA 100ML — KHÔNG TANH", "Uống ngon mỗi ngày • Dạng gói tiện mang theo"),
        ("c6", 33.75, 5.55, "LỊCH TRÌNH ĐÓN TẾT", "NGỦ SỚM + UỐNG ĐỀU MỖI NGÀY", "Rạng rỡ tự tin đón mọi buổi tiệc cuối năm"),
    ],
    "sfx": [
        ("sfx-01", "sfx_pop_clean.mp3", 0.12, 0.55, 9, 0.24),
        ("sfx-02", "sfx_whoosh_soft.mp3", 3.89, 0.55, 9, 0.22),
        ("sfx-03", "sfx_whoosh_cinematic.mp3", 11.38, 0.90, 9, 0.28),
        ("sfx-04", "sfx_sparkle_shine.mp3", 11.60, 1.65, 10, 0.26),
        ("sfx-05", "sfx_crystal_shimmer.mp3", 18.15, 2.00, 10, 0.56),
        ("sfx-06", "sfx_ping_glass.mp3", 22.50, 0.85, 11, 0.26),
        ("sfx-07", "sfx_whoosh_soft.mp3", 26.64, 0.55, 9, 0.22),
        ("sfx-08", "sfx_chime_warm.mp3", 33.55, 2.20, 10, 0.52),
        ("sfx-09", "sfx_whoosh_cinematic.mp3", 39.63, 0.90, 9, 0.28),
        ("sfx-10", "sfx_sparkle_shine.mp3", 39.95, 1.65, 10, 0.28),
        ("sfx-11", "sfx_notification_cta.mp3", 41.30, 2.10, 11, 0.22),
    ],
    "endcard": {
        "bg": "linear-gradient(175deg, #4B0624 0%, #8A1044 46%, #3A051C 100%)",
        "kicker": "COLLAGEN TRIPEPTIDE VỊ ĐÀO",
        "brand": "COLLAMELA",
        "sub": "2.530mg Collagen • 25,68mg HA • 87mg Vitamin C • 3,9mg Kẽm",
        "box_main": "box_main.png", "box_gift": "box_main.png",
        "gift_pill": "★ TẶNG HỘP 10 GÓI",
        "spec_lbl": "HỘP 20 GÓI × 4G (80G)",
        "price": "920.000đ",
        "promo": "MUA 2 TẶNG 10G (480K)",
        "cta_bg": "linear-gradient(90deg, #074F34, #0E744E)",
        "cta": "▸ NHẮN “DA ĐẸP” NHẬN LỊCH 60 NGÀY ĐÓN TẾT!",
    },
}

if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "both"
    if w in ("v3", "both"):
        build_usp_video(V3_CFG)
    if w in ("v4", "both"):
        build_usp_video(V4_CFG)
