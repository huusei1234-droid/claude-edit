"""
Dựng HyperFrames 24fps (1080x1920) cho 2 VIDEO COMBO CHIỀU CAO BÉ TỪ 1 TUỔI TRỞ LÊN (BOJOMI + AV PROTEIN):
ĐẶC BIỆT NÂNG CẤP THEO YÊU CẦU:
1. THỜI LƯỢNG DƯỚI 1 PHÚT (<= 58.0s — gọn gàng, giữ chân cao).
2. HIỆU ỨNG LỚP PHỦ ĐIỆN ẢNH THẬT (`overlay_cinema.mp4` Bụi Vàng Bokeh / Tia Nắng Cửa Sổ + `overlay_bling.mp4` Sao Ngọc Trai Bling hòa trộn Screen + hiệu ứng quét sáng ánh kim Specular Sheen trên thẻ chữ!).
3. TEXT CỰC TO & SIÊU DỄ ĐỌC (`sc-big: 54px–58px`, `sc-sub: 30px`, `sc-tag: 26px`, Hook mở đầu `66px–76px` viền trắng dày 15px nổi khối — to hơn +45% so với bản thường mà vẫn 100% nằm gọn trong Vùng An Toàn 9:16 X=56..870px, Y<=1534px!).
4. MỖI VIDEO 1 BÀI NHẠC NỀN RIÊNG (`Happy Acoustic` & `A Happy Moment` chuẩn hóa -18 LUFS + EQ Voice Pocket + Ducking).
"""
import os, sys, json, shutil

WORK_DIR = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Bo_2_Video_Chieu_Cao_Be_Tu_1_Tuoi"
CUTOUT_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG"
ASSETS_DIR = os.path.join(WORK_DIR, "01_ChatGPT_Assets")
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
BGM_UNIQUE_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "gain", "id": "bgu", "params": {"gain": 1.2}},
        {"type": "highpass", "id": "bhu", "params": {"frequency": 80}},
        {"type": "peaking", "id": "bcu", "params": {"frequency": 2350, "gain": -4.0, "q": 0.85}},
        {"type": "highshelf", "id": "bau", "params": {"frequency": 7800, "gain": 0.8}},
        {"type": "limiter", "id": "blu", "params": {"limit": -2.5}},
    ],
})

LOCAL_FONT_CSS = """
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-SemiBold.ttf') format('truetype'); font-weight: 600; }
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-Bold.ttf') format('truetype'); font-weight: 700; }
@font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-ExtraBold.ttf') format('truetype'); font-weight: 800; }
@font-face { font-family: 'MontBlk'; src: url('assets/fonts/Montserrat-Black.ttf') format('truetype'); font-weight: 900; }
"""


def build_ducking(segs, total_dur):
    pts = [{"t": 0.0, "v": 0.58}]
    for seg in segs:
        st, en = seg["start_s"], seg["end_s"]
        t_in = max(0.05, round(st - 0.14, 2))
        t_dk = max(t_in + 0.02, round(st, 2))
        t_rl = min(total_dur - 0.12, round(en, 2))
        t_up = min(total_dur - 0.05, round(en + 0.22, 2))
        if t_in > pts[-1]["t"] + 0.04: pts.append({"t": t_in, "v": 0.52})
        if t_dk > pts[-1]["t"] + 0.02: pts.append({"t": t_dk, "v": 0.32})
        if t_rl > pts[-1]["t"] + 0.02: pts.append({"t": t_rl, "v": 0.32})
        if t_up > pts[-1]["t"] + 0.02: pts.append({"t": t_up, "v": 0.52})
    if pts[-1]["t"] < total_dur - 0.80:
        pts.append({"t": round(total_dur - 0.80, 2), "v": 0.72})
    pts.append({"t": total_dur, "v": 0.74})
    return html_json({"version": 1, "lanes": [{"target": "volume", "points": pts}]})


def build_video(cfg: dict):
    vdir = os.path.join(WORK_DIR, cfg["vkey"])
    hf_dir = os.path.join(vdir, "07_HyperFrames_Project")
    comp_dir = os.path.join(hf_dir, "compositions")
    img_dir = os.path.join(hf_dir, "assets", "images")
    vid_dir = os.path.join(hf_dir, "assets", "videos")
    os.makedirs(comp_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    shutil.copy2(os.path.join(ASSETS_DIR, cfg["look_img"]), os.path.join(img_dir, "hero_look.png"))
    shutil.copy2(os.path.join(CUTOUT_DIR, "av02_bojomi_b.png"), os.path.join(img_dir, "box_bojomi.png"))
    shutil.copy2(os.path.join(CUTOUT_DIR, "av01_protein_a.png"), os.path.join(img_dir, "box_protein.png"))
    shutil.copy2(os.path.join(CUTOUT_DIR, "logo_an_vuong_orig.png"), os.path.join(img_dir, "logo_an_vuong_orig.png"))

    vo_data = json.loads(open(os.path.join(vdir, "06_Audio_Voiceover", "vo_manifest.json"), encoding="utf-8").read())
    segs = vo_data["segments"]
    total_dur = float(vo_data["total_duration_s"])
    assert total_dur <= 60.0, f"Video exceeds 60s: {total_dur}"

    # 6 segments: seg 0..4 are main video (7 dynamic shots), seg 5 is End-Card!
    s0, s1, s2, s3, s4, s5 = segs
    t1 = float(s0["shot_end_s"])
    t2 = float(s1["shot_end_s"])
    t3 = float(s2["shot_end_s"])
    t4 = float(s3["shot_end_s"])
    end_start = float(s4["shot_end_s"])
    end_dur = round(total_dur - end_start, 2)

    shots = []
    if cfg["layout"] == "m1":
        # M1: s01, s02, s03, (s04a CGI + s04b live), (s05a CGI + s05b live)
        d3 = round(t4 - t3, 2)
        d3a = min(4.50, round((d3 / 2.0) * 4.0) / 4.0)
        d3b = round(d3 - d3a, 2)
        d4 = round(end_start - t4, 2)
        d4a = min(4.50, round((d4 / 2.0) * 4.0) / 4.0)
        d4b = round(d4 - d4a, 2)
        shots = [
            ("s01.mp4", 0.0, t1, 0.15),
            ("s02.mp4", t1, round(t2 - t1, 2), 0.15),
            ("s03.mp4", t2, round(t3 - t2, 2), 0.15),
            ("s04a.mp4", t3, d3a, 0.10),
            ("s04b.mp4", round(t3 + d3a, 2), d3b, 0.10),
            ("s05a.mp4", t4, d4a, 0.10),
            ("s05b.mp4", round(t4 + d4a, 2), d4b, 0.10),
        ]
    else:
        # M2: s01, s02, (s03a live + s03b CGI), (s04a live + s04b CGI), s05
        d2 = round(t3 - t2, 2)
        d2a = round((d2 / 2.0) * 4.0) / 4.0
        d2b = round(d2 - d2a, 2)
        d3 = round(t4 - t3, 2)
        d3a = round((d3 / 2.0) * 4.0) / 4.0
        d3b = round(d3 - d3a, 2)
        shots = [
            ("s01.mp4", 0.0, t1, 0.15),
            ("s02.mp4", t1, round(t2 - t1, 2), 0.15),
            ("s03a.mp4", t2, d2a, 0.10),
            ("s03b.mp4", round(t2 + d2a, 2), d2b, 0.10),
            ("s04a.mp4", t3, d3a, 0.10),
            ("s04b.mp4", round(t3 + d3a, 2), d3b, 0.10),
            ("s05.mp4", t4, round(end_start - t4, 2), 0.15),
        ]

    callouts = [
        ("c2", round(t1 + 0.16, 2), round(t2 - t1 - 0.40, 2), *cfg["callouts"][0]),
        ("c3", round(t2 + 0.16, 2), round(t3 - t2 - 0.40, 2), *cfg["callouts"][1]),
        ("c4", round(t3 + 0.16, 2), round(t4 - t3 - 0.40, 2), *cfg["callouts"][2]),
        ("c5", round(t4 + 0.16, 2), round(end_start - t4 - 0.40, 2), *cfg["callouts"][3]),
    ]

    sfx = [
        ("sfx-01", "sfx_pop_clean.mp3", 0.10, 0.55, 9, 0.24),
        ("sfx-02", "sfx_whoosh_soft.mp3", round(t1 - 0.11, 2), 0.55, 9, 0.22),
        ("sfx-03", "sfx_whoosh_cinematic.mp3", round(t2 - 0.12, 2), 0.90, 9, 0.28),
        ("sfx-04", "sfx_sparkle_shine.mp3", round(t2 + 0.08, 2), 1.65, 10, 0.26),
        ("sfx-05", "sfx_crystal_shimmer.mp3", round(t3 + 0.12, 2), 2.00, 10, 0.52),
        ("sfx-06", "sfx_ping_glass.mp3", round(t4 + 0.08, 2), 0.85, 11, 0.24),
        ("sfx-07", "sfx_whoosh_cinematic.mp3", round(end_start - 0.12, 2), 0.90, 9, 0.28),
        ("sfx-08", "sfx_sparkle_shine.mp3", round(end_start + 0.16, 2), 1.65, 10, 0.28),
        ("sfx-09", "sfx_notification_cta.mp3", round(end_start + 1.40, 2), 2.10, 11, 0.22),
    ]

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

    bgm_auto = build_ducking(segs, total_dur)
    vo_tags = [
        f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
        f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{5 if i%2==0 else 6}" '
        f'data-volume="1.32" data-fade-in="0.04" data-fade-out="0.06" data-fx-chain="{VO_FX}"></audio>'
        for i, s in enumerate(segs)
    ]
    sfx_tags = [
        f'      <audio id="{sid}" class="clip" src="assets/audio/{fn}" data-start="{st}" '
        f'data-duration="{du}" data-track-index="{tr}" data-volume="{vol}" data-fade-out="0.16"></audio>'
        for sid, fn, st, du, tr, vol in sfx
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
      .fx-host {{ position: absolute; inset: 0; z-index: 8; pointer-events: none; mix-blend-mode: screen; }}
      .overlay-host {{ position: absolute; inset: 0; z-index: 14; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="{end_start}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene-host" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{end_start}" data-duration="{end_dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <!-- REAL CINEMA VIDEO OVERLAYS (Golden Dust Bokeh / Sun Rays + Soft Pearl Sparkles Bling in Screen mode!) -->
      <div id="cinema-fx" class="fx-host" data-composition-id="cinema-fx" data-composition-src="compositions/cinema-fx.html" data-start="0" data-duration="{total_dur}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <audio id="bgm-main" class="clip" src="assets/audio/bgm_unique.mp3" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="7" data-fade-in="0.22" data-fade-out="0.85" data-fx-chain="{BGM_UNIQUE_FX}" data-automation="{bgm_auto}"></audio>

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

    # 1. main-video.html
    shot_els, shot_anims = [], []
    for idx, (sfile, st, du, mstart) in enumerate(shots):
        rid = f"rig{idx+1}"
        tr = 1 if idx % 2 == 0 else 2
        shot_els.append(
            f'    <div id="{rid}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>\n'
            f'      <video {COLOR_GRADE_ATTR} id="v{idx+1}" class="clip bg-video" src="assets/videos/{sfile}" '
            f'data-start="{st}" data-duration="{du}" data-media-start="{mstart}" data-hf-media-start-basis="local" '
            f'data-track-index="{tr}" muted playsinline></video>\n'
            f'    </div>'
        )
        s0_sc, s1_sc = (1.00, 1.05) if idx % 2 == 0 else (1.04, 1.00)
        shot_anims.append(f'    tl.fromTo("#{rid}", {{ scale: {s0_sc} }}, {{ scale: {s1_sc}, duration: {du}, ease: "none", immediateRender: false }}, {st});')

    main_vid_html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: {cfg["bg_dark"]}; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 50%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .sun-flare {{
      position: absolute; inset: 0; pointer-events: none; z-index: 12; opacity: 0;
      background: radial-gradient(circle at 50% 38%, rgba(255,248,215,0.95) 0%, rgba(252,226,136,0.56) 40%, rgba(255,255,255,0) 76%);
      mix-blend-mode: screen;
    }}
  </style>
  <div id="root" data-composition-id="main-video" data-width="1080" data-height="1920" data-start="0" data-duration="{end_start}">
{chr(10).join(shot_els)}
    <div id="fl1" class="sun-flare" data-layout-ignore></div>
    <div id="fl2" class="sun-flare" data-layout-ignore></div>
    <div id="fl3" class="sun-flare" data-layout-ignore></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(shot_anims)}
    tl.fromTo("#fl1", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.14, immediateRender: false }}, {round(t1 - 0.10, 2)})
      .to("#fl1", {{ opacity: 0, duration: 0.24 }}, {round(t1 + 0.04, 2)});
    tl.fromTo("#fl2", {{ opacity: 0 }}, {{ opacity: 0.88, duration: 0.14, immediateRender: false }}, {round(t2 - 0.10, 2)})
      .to("#fl2", {{ opacity: 0, duration: 0.24 }}, {round(t2 + 0.04, 2)});
    tl.fromTo("#fl3", {{ opacity: 0 }}, {{ opacity: 0.82, duration: 0.14, immediateRender: false }}, {round(t4 - 0.10, 2)})
      .to("#fl3", {{ opacity: 0, duration: 0.24 }}, {round(t4 + 0.04, 2)});
    window.__timelines["main-video"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "main-video.html"), "w", encoding="utf-8").write(main_vid_html)

    # 2. cinema-fx.html — REAL 9:16 Cinema Video Overlays (Golden Dust Bokeh / Sun Rays + Soft Pearl Sparkles Bling + Warm Corner Sun Glow!)
    cinema_fx_html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; pointer-events: none; }}
    .ov-vid {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block;
      mix-blend-mode: screen;
    }}
    #ov-main {{ opacity: {cfg["ov_opacity"]}; }}
    #ov-bling {{ opacity: 0.34; }}
    .warm-sun-corner {{
      position: absolute; top: -120px; right: -120px; width: 760px; height: 760px; border-radius: 50%;
      background: radial-gradient(circle, rgba(255,244,196,0.44) 0%, rgba(255,222,128,0.18) 42%, rgba(255,255,255,0) 74%);
      mix-blend-mode: screen;
    }}
  </style>
  <div id="root" data-composition-id="cinema-fx" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <video id="ov-main" class="clip ov-vid" src="assets/videos/overlay_cinema.mp4" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="1" muted playsinline data-layout-ignore></video>
    <video id="ov-bling" class="clip ov-vid" src="assets/videos/overlay_bling.mp4" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="2" muted playsinline data-layout-ignore></video>
    <div id="sun-glow" class="warm-sun-corner" data-layout-ignore></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Gentle organic breathing of corner golden sunbeam overlay
    tl.fromTo("#sun-glow", {{ opacity: 0.45, scale: 0.94 }}, {{ opacity: 0.85, scale: 1.08, duration: {round(total_dur / 2.0, 2)}, ease: "sine.inOut" }}, 0.0)
      .to("#sun-glow", {{ opacity: 0.50, scale: 0.96, duration: {round(total_dur / 2.0, 2)}, ease: "sine.inOut" }}, {round(total_dur / 2.0, 2)});
    window.__timelines["cinema-fx"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "cinema-fx.html"), "w", encoding="utf-8").write(cinema_fx_html)

    # 3. safe-overlays.html — EXTRA-LARGE ULTRA-READABLE TYPOGRAPHY (+45% BIGGER!) + Specular Gloss Sheen + Top-Right Age Pill!
    hk = cfg["big_hook"]
    hk_end = round(t1 - 0.14, 2)
    c_divs, c_anims = [], []
    for idx, (cid, st, du, tag, big, sub) in enumerate(callouts):
        sh_id = f"sh-{cid}"
        c_divs.append(f"""
      <div id="{cid}" class="safe-card" data-layout-ignore>
        <div id="{sh_id}" class="card-sheen"></div>
        <div class="sc-tag">{tag}</div>
        <div class="sc-big">{big}</div>
        <div class="sc-sub">{sub}</div>
      </div>""")
        c_anims.append(
            f'    tl.fromTo("#{cid}", {{ opacity: 0, y: 32, scale: 0.92, filter: "blur(14px)" }}, '
            f'{{ opacity: 1, y: 0, scale: 1.0, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.25)", immediateRender: false }}, {st})\n'
            f'      .fromTo("#{sh_id}", {{ x: -240, opacity: 0.0 }}, {{ x: 960, opacity: 0.65, duration: 0.95, ease: "power2.inOut", immediateRender: false }}, {round(st + 0.35, 2)})\n'
            f'      .to("#{cid}", {{ opacity: 0, y: -12, filter: "blur(10px)", duration: 0.22, ease: "power2.in" }}, {round(st + du - 0.22, 2)});'
        )

    overlays_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; pointer-events: none; font-family: 'BeVN', sans-serif; }}

    /* EXTRA-LARGE OPENING BIG TEXT HOOK (Frame 0 visible! Strict border-box X=56..870px, bottom Y=1520px!) */
    .big-hook-wrap {{
      position: absolute; bottom: 400px; left: 56px; width: 814px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
      padding: 22px 16px 26px; overflow: hidden;
      background: linear-gradient(180deg, rgba(255,255,255,0.42) 0%, rgba(255,255,255,0.82) 100%);
      backdrop-filter: blur(8px);
      border: 4px solid rgba(255,255,255,0.92); border-radius: 32px;
      box-shadow: 0 20px 44px rgba(0,0,0,0.34); z-index: 20;
    }}
    .bh-badge {{
      background: {hk["badge_bg"]}; color: #FFF8D6; border: 3px solid #FFE288;
      border-radius: 999px; padding: 10px 28px; font-weight: 800; font-size: 27px;
      letter-spacing: 0.6px; box-shadow: 0 8px 20px rgba(0,0,0,0.30); margin-bottom: 14px;
    }}
    .bh-l1 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: {hk["s1"]}px; line-height: 1.06;
      color: {hk["c1"]}; white-space: nowrap;
      -webkit-text-stroke: 15px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 8px 16px rgba(0,0,0,0.36));
    }}
    .bh-l2 {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: {hk["s2"]}px; line-height: 1.08;
      margin-top: 8px; color: {hk["c2"]}; white-space: nowrap;
      -webkit-text-stroke: 15px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 10px 20px rgba(0,0,0,0.40));
    }}

    /* Top-Left Brand Chip & Top-Right Age Target Pill (strictly Y=256..330px inside upper Safe Zone!) */
    .brand-chip {{
      position: absolute; top: 256px; left: 58px; opacity: 0;
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.96); border: 3px solid #E2B448;
      border-radius: 18px; padding: 8px 18px;
      box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }}
    .brand-chip img {{ height: 50px; width: auto; display: block; }}
    .brand-chip span {{ font-weight: 800; font-size: 22px; color: #064D33; letter-spacing: 0.4px; }}

    .age-pill {{
      position: absolute; top: 262px; right: 58px; opacity: 0;
      background: linear-gradient(135deg, #D91A26, #A10B16); color: #FFF8DC;
      border: 3px solid #FFE288; border-radius: 999px; padding: 10px 22px;
      font-weight: 800; font-size: 24px; letter-spacing: 0.4px;
      box-shadow: 0 10px 24px rgba(161,11,22,0.38);
    }}

    /* 100% REAL FACTORY IS-Net FLOATING DUO BOX OVERLAY (0% AI box distortion!) strictly X=56..680px, above callout card! */
    .duo-float {{
      position: absolute; left: 56px; bottom: 684px; width: 640px; height: 340px;
      display: flex; align-items: flex-end; justify-content: flex-start; gap: 18px;
      opacity: 0; z-index: 16;
    }}
    .df-box {{
      height: 318px; width: auto;
      filter: drop-shadow(0 18px 28px rgba(0,0,0,0.48)) drop-shadow(0 0 22px rgba(255,240,180,0.55));
    }}
    .df-plus {{
      width: 50px; height: 50px; border-radius: 50%; margin-bottom: 120px; flex-shrink: 0;
      background: linear-gradient(145deg, #FCE078, #D98E10); border: 3px solid #FFFFFF;
      color: #053623; font-weight: 900; font-size: 36px;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 8px 18px rgba(0,0,0,0.40);
    }}

    /* EXTRA-LARGE ULTRA-READABLE CALLOUT CARDS (+45% BIGGER TEXT!) Strict border-box X=56..870px, bottom Y=1526px! */
    .safe-card {{
      position: absolute; left: 56px; bottom: 394px; width: 814px; overflow: hidden;
      background: {cfg["card_bg"]};
      border: 3.5px solid #F4CF68; border-left: 11px solid #FFE480;
      border-radius: 28px; padding: 24px 28px;
      box-shadow: 0 18px 38px rgba(0,0,0,0.44); opacity: 0;
    }}
    .card-sheen {{
      position: absolute; top: 0; bottom: 0; width: 170px; pointer-events: none;
      background: linear-gradient(105deg, rgba(255,255,255,0) 0%, rgba(255,250,210,0.34) 50%, rgba(255,255,255,0) 100%);
      transform: skewX(-20deg); opacity: 0;
    }}
    .sc-tag {{
      font-weight: 800; font-size: 26px; color: #FFE888; letter-spacing: 0.8px;
      text-transform: uppercase; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.40);
    }}
    .sc-big {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 54px; line-height: 1.12;
      color: #FFFFFF; text-shadow: 0 4px 12px rgba(0,0,0,0.46);
    }}
    .sc-sub {{
      font-weight: 700; font-size: 30px; color: #F2FFF8; margin-top: 10px; line-height: 1.26;
      text-shadow: 0 2px 8px rgba(0,0,0,0.35);
    }}
  </style>
  <div id="root" data-composition-id="safe-overlays" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <div id="big-hook" class="big-hook-wrap" data-layout-ignore>
      <div class="bh-badge">{hk["badge"]}</div>
      <div class="bh-l1">{hk["l1"]}</div>
      <div class="bh-l2">{hk["l2"]}</div>
    </div>
    <div id="top-brand" class="brand-chip" data-layout-ignore>
      <img src="assets/images/logo_an_vuong_orig.png" alt="An Vuong" />
      <span>BOJOMI × AV PROTEIN</span>
    </div>
    <div id="top-age" class="age-pill" data-layout-ignore>★ BÉ TỪ 1 TUỔI+ ★</div>
    <div id="duo-real" class="duo-float" data-layout-ignore>
      <img class="df-box" src="assets/images/box_protein.png" alt="AV Protein" />
      <div class="df-plus">+</div>
      <img class="df-box" src="assets/images/box_bojomi.png" alt="Bojomi" />
    </div>
    {"".join(c_divs)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#big-hook", {{ scale: 0.92, y: 10 }}, {{ scale: 1.0, y: 0, duration: 0.28, ease: "back.out(1.45)" }}, 0.0)
      .to("#big-hook", {{ opacity: 0, y: -18, filter: "blur(12px)", duration: 0.26, ease: "power2.in" }}, {round(hk_end - 0.26, 2)});
    tl.fromTo("#top-brand", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power2.out", immediateRender: false }}, 0.12)
      .to("#top-brand", {{ opacity: 0, duration: 0.25 }}, {round(end_start - 0.26, 2)});
    tl.fromTo("#top-age", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1.0, duration: 0.32, ease: "back.out(1.5)", immediateRender: false }}, 0.20)
      .to("#top-age", {{ opacity: 0, duration: 0.25 }}, {round(end_start - 0.26, 2)});
    // Real Factory IS-Net Duo Boxes float cleanly on dual-product reveal segment (100% accurate packaging!)
    tl.fromTo("#duo-real", {{ opacity: 0, y: 38, scale: 0.88 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.38, ease: "back.out(1.35)", immediateRender: false }}, {round(t2 + 0.18, 2) if cfg["layout"] == "m1" else round(t4 + 0.18, 2)})
      .to("#duo-real", {{ opacity: 0, y: -16, filter: "blur(8px)", duration: 0.26, ease: "power2.in" }}, {round(t3 - 0.28, 2) if cfg["layout"] == "m1" else round(end_start - 0.28, 2)});
{chr(10).join(c_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "safe-overlays.html"), "w", encoding="utf-8").write(overlays_html)

    # 4. endcard.html — EXTRA-LARGE EASY-TO-READ END-CARD + BOTH REAL IS-Net Boxes + Strict Safe Zone!
    endcard_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: {cfg["ec_bg"]}; font-family: 'BeVN', sans-serif;
    }}
    .ec-model {{
      position: absolute; top: 256px; right: 58px; width: 404px; height: 590px;
      border-radius: 30px; overflow: hidden; border: 3.5px solid rgba(244,204,100,0.92);
      box-shadow: 0 20px 44px rgba(0,0,0,0.40);
    }}
    .ec-model img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 15%; display: block; }}
    .ec-logo {{
      position: absolute; top: 260px; left: 58px;
      background: rgba(255,255,255,0.96); border: 3px solid #E5B442; border-radius: 22px;
      padding: 10px 22px; box-shadow: 0 10px 26px rgba(0,0,0,0.25);
    }}
    .ec-logo img {{ height: 68px; width: auto; display: block; }}
    .ec-title {{ position: absolute; top: 374px; left: 58px; width: 530px; }}
    .ec-kicker {{
      display: inline-block; background: linear-gradient(135deg, #D91A26, #A10B16); color: #FFF8DC;
      border: 2px solid #FFE288; border-radius: 999px; padding: 5px 18px;
      font-weight: 800; font-size: 22px; letter-spacing: 0.5px; margin-bottom: 8px;
    }}
    .ec-brand {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 52px; line-height: 1.08;
      color: #FFFFFF; text-shadow: 0 5px 16px rgba(0,0,0,0.38);
    }}
    .ec-sub {{ font-weight: 700; font-size: 25px; color: #EFFCF5; margin-top: 10px; line-height: 1.28; }}

    .ec-boxes {{
      position: absolute; left: 58px; top: 696px; width: 720px; height: 396px;
      display: flex; align-items: flex-end; gap: 16px;
    }}
    .b-col {{ display: flex; flex-direction: column; align-items: center; }}
    .b-tag {{
      background: rgba(4,48,32,0.94); color: #FFF8DC; border: 2.5px solid #F4CC62;
      border-radius: 999px; padding: 5px 16px; font-weight: 800; font-size: 19px;
      margin-bottom: 6px; white-space: nowrap;
    }}
    .b-pro {{ height: 334px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .b-boj {{ height: 340px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .b-plus {{
      width: 54px; height: 54px; border-radius: 50%; flex-shrink: 0; margin-bottom: 136px;
      background: linear-gradient(145deg, #FCE078, #D98E10); border: 3.5px solid #FFFFFF;
      color: #053623; font-weight: 900; font-size: 40px;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 10px 20px rgba(0,0,0,0.38);
    }}

    /* EXTRA-BIG EASY-TO-READ DEAL CARD (Strict border-box X=58..870px, bottom <= 1456px!) */
    .ec-deal {{
      position: absolute; left: 58px; top: 1110px; width: 812px;
      background: linear-gradient(155deg, rgba(255,255,255,0.98), rgba(255,248,228,0.98));
      border: 4px solid #E5B442; border-radius: 28px; padding: 20px 24px;
      box-shadow: 0 18px 36px rgba(0,0,0,0.36);
    }}
    .ec-prow {{ display: flex; align-items: center; justify-content: space-between; gap: 14px; }}
    .ep-l {{ font-weight: 800; font-size: 22px; color: #074C32; }}
    .ep-n {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 58px; line-height: 1.02; color: #0B40A8; }}
    .ep-pr {{
      background: linear-gradient(135deg, #064D33, #0F7B54); border: 3px solid #FFE288;
      border-radius: 18px; padding: 12px 16px; text-align: center;
      box-shadow: 0 8px 18px rgba(6,77,51,0.32);
    }}
    .ep-1 {{ font-weight: 800; font-size: 18px; color: #FFF3B0; }}
    .ep-2 {{ font-weight: 800; font-size: 19px; color: #FFFFFF; margin-top: 3px; white-space: nowrap; }}
    .ec-cta {{
      margin-top: 15px; background: linear-gradient(90deg, #074F34, #0E744E);
      border: 3px solid #F2CC66; border-radius: 18px; padding: 15px 18px;
      text-align: center; font-weight: 800; font-size: 27px; color: #FFF8D6;
    }}
    .ec-legal {{
      position: absolute; left: 58px; top: 1464px; width: 812px;
      font-weight: 600; font-size: 20px; line-height: 1.32; color: #F0FCF6;
      text-shadow: 0 2px 6px rgba(0,0,0,0.48);
    }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920" data-start="0" data-duration="{end_dur}">
    <div id="ec-m" class="ec-model" data-layout-ignore><img src="assets/images/hero_look.png" alt="Model" /></div>
    <div id="ec-l" class="ec-logo" data-layout-ignore><img src="assets/images/logo_an_vuong_orig.png" alt="Logo" /></div>
    <div id="ec-t" class="ec-title" data-layout-ignore>
      <div class="ec-kicker">★ CHO BÉ TỪ 1 TUỔI TRỞ LÊN ★</div>
      <div class="ec-brand">BOJOMI +<br/>AV PROTEIN</div>
      <div class="ec-sub">Đạm thực vật + B-3 • Canxi Aquamin F + D3 + K2 MK-7</div>
    </div>
    <div id="ec-b" class="ec-boxes" data-layout-ignore>
      <div id="eb1" class="b-col">
        <div class="b-tag">AV PROTEIN • 350K</div>
        <img class="b-pro" src="assets/images/box_protein.png" alt="AV Protein" />
      </div>
      <div id="eplus" class="b-plus">+</div>
      <div id="eb2" class="b-col">
        <div class="b-tag">BOJOMI • 520K</div>
        <img class="b-boj" src="assets/images/box_bojomi.png" alt="Bojomi" />
      </div>
    </div>
    <div id="ec-d" class="ec-deal" data-layout-ignore>
      <div class="ec-prow">
        <div>
          <div class="ep-l">BỘ ĐÔI 2 HỘP CHÍNH HÃNG</div>
          <div class="ep-n">870.000đ</div>
        </div>
        <div class="ep-pr">
          <div class="ep-1">★ CHÍNH HÃNG DROPPII</div>
          <div class="ep-2">PROTEIN 350K + BOJOMI 520K</div>
        </div>
      </div>
      <div class="ec-cta">{cfg["ec_cta"]}</div>
    </div>
    <div id="ec-g" class="ec-legal" data-layout-ignore>{LEGAL_TPBS} Hotline: 0867 399 268</div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#ec-m", {{ opacity: 0, scale: 1.06, x: 24 }}, {{ opacity: 1, scale: 1.0, x: 0, duration: 0.45, ease: "power3.out", immediateRender: false }}, 0.05)
      .fromTo("#ec-l", {{ opacity: 0, y: -18 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out", immediateRender: false }}, 0.12)
      .fromTo("#ec-t", {{ opacity: 0, x: -24, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.38, ease: "power3.out", immediateRender: false }}, 0.22)
      .fromTo("#eb1",  {{ opacity: 0, y: 36, scale: 0.90 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.40, ease: "back.out(1.3)", immediateRender: false }}, 0.32)
      .fromTo("#eplus",{{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1.0, duration: 0.28, ease: "back.out(1.7)", immediateRender: false }}, 0.44)
      .fromTo("#eb2",  {{ opacity: 0, y: 36, scale: 0.90 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.40, ease: "back.out(1.3)", immediateRender: false }}, 0.52)
      .fromTo("#ec-d", {{ opacity: 0, y: 30, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.40, ease: "power3.out", immediateRender: false }}, 0.66)
      .fromTo("#ec-g", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.30, immediateRender: false }}, 0.88)
      .to("#ec-m", {{ scale: 1.03, duration: {round(end_dur - 0.6, 2)}, ease: "none" }}, 0.60);
    window.__timelines["endcard"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "endcard.html"), "w", encoding="utf-8").write(endcard_html)
    print(f"[BUILT HF {cfg['vkey']}] {hf_dir} ({total_dur}s @ 24fps <= 60s!, endcard={end_start}..{total_dur}s)")


CFGS = [
    {
        "vkey": "kid1y_01_giai_doan_vang",
        "slug": "av-kid1y-01",
        "layout": "m1",
        "title": "Combo Chiều Cao Bé Từ 1 Tuổi 01 — Giai Đoạn Vàng Đạm & Canxi",
        "look_img": "KID1Y_LOOK1_BLUSH_DRESS_9x16.png",
        "bg_dark": "#052C20",
        "ec_bg": "linear-gradient(175deg, #043222 0%, #0A6142 48%, #042B1D 100%)",
        "card_bg": "linear-gradient(145deg, rgba(4,48,32,0.92) 0%, rgba(10,84,56,0.88) 100%)",
        "ov_opacity": "0.46",
        "ec_cta": "▸ NHẮN “BÉ 1 TUỔI” NHẬN TƯ VẤN NGAY!",
        "big_hook": {
            "badge": "★ MẸ CÓ CON TỪ 1 TUỔI+ ★",
            "l1": "CHIỀU CAO CỦA BÉ",
            "l2": "CHĂM TỪ 1 TUỔI NGAY!",
            "c1": "#05472F", "c2": "#D91A26",
            "s1": 74, "s2": 66,
            "badge_bg": "linear-gradient(135deg, #064F34, #0F7B54)",
        },
        "callouts": [
            ("GIAI ĐOẠN VÀNG TỪ 1 TUỔI", "ĐẠM + CANXI SONG HÀNH", "Xây khung xương vững chắc từ sớm"),
            ("AN VƯỢNG PHARMA", "BOJOMI + AV PROTEIN", "Bộ đôi dinh dưỡng gọn nhẹ mỗi ngày"),
            ("AV PROTEIN • ÊM BỤNG", "ĐẠM SẠCH + LỢI KHUẨN B-3", "Thêm chất xơ Inulin dễ tiêu hóa"),
            ("BOJOMI • VỊ VANI NGON", "CANXI TẢO BIỂN + D3 + K2", "Aquamin F + 201,4mg Collagen dễ uống"),
        ],
    },
    {
        "vkey": "kid1y_02_pha_chuan_2_ly",
        "slug": "av-kid1y-02",
        "layout": "m2",
        "title": "Combo Chiều Cao Bé Từ 1 Tuổi 02 — Pha Chuẩn 2 Ly Êm Bụng (870K)",
        "look_img": "KID1Y_LOOK2_SAGE_BLOUSE_9x16.png",
        "bg_dark": "#063024",
        "ec_bg": "linear-gradient(175deg, #043120 0%, #0B6343 48%, #042C1E 100%)",
        "card_bg": "linear-gradient(145deg, rgba(5,50,34,0.92) 0%, rgba(12,86,58,0.88) 100%)",
        "ov_opacity": "0.44",
        "ec_cta": "▸ NHẮN “BÉ 1 TUỔI” NHẬN LỊCH UỐNG CHUẨN!",
        "big_hook": {
            "badge": "★ BÍ KÍP MẸ THÔNG THÁI ★",
            "l1": "PHA CHO BÉ TỪ 1 TUỔI",
            "l2": "SAO ĐỂ ÊM BỤNG NHẤT?",
            "c1": "#05472F", "c2": "#D91A26",
            "s1": 64, "s2": 64,
            "badge_bg": "linear-gradient(135deg, #064F34, #108057)",
        },
        "callouts": [
            ("LƯU Ý QUAN TRỌNG", "KHÔNG PHA CHUNG 1 LY!", "Tránh nước sôi để giữ trọn dưỡng chất"),
            ("BUỔI SÁNG • AV PROTEIN", "PHA NƯỚC MÁT 20–40°C", "Bảo toàn lợi khuẩn B-3 êm bụng con"),
            ("BỮA PHỤ CHIỀU • BOJOMI", "PHA NƯỚC ẤM 60°C", "Ngũ cốc Vani giàu Canxi, D3 & K2"),
            ("CHUẨN NHÃN CHO BÉ 1 TUỔI+", "CHIA LƯỢNG ĐÚNG ĐỘ TUỔI", "Kết hợp ngủ trước 22h & vận động đều"),
        ],
    },
]

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for i, c in enumerate(CFGS, 1):
        if arg in ("all", f"m{i}", c["vkey"]):
            build_video(c)
