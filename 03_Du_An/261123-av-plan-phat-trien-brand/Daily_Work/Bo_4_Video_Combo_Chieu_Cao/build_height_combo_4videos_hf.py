"""
Dựng HyperFrames 24fps (1080x1920) cho TRỌN BỘ 4 VIDEO COMBO PHÁT TRIỂN CHIỀU CAO (BOJOMI + AV PROTEIN):
- H1: Đạm Sạch AV Protein (22,05g) & Canxi Tảo Biển Bojomi (417,6mg) — Look Polo Trắng × Navy
- H2: 4 Trụ Cột Vàng Phát Triển Chiều Cao Khoa Học — Look Đầm Đũi Kem × Cardigan Mint
- H3: Bí Kíp Pha Riêng 2 Nhiệt Độ (AV Protein 20-40°C • Bojomi 60°C) — Look Vàng Bơ × Trắng Bếp Sáng
- H4: Đồng Hành Vận Động Giãn Cơ & Bộ Đôi 870K (Quà tới 520K) — Look Tập Giãn Cơ Xanh Thiên Thanh

Đảm bảo 100%:
- TEXT HOOK MỞ ĐẦU CỰC TO RÕ RÀNG ngay Frame 0 (0% che mặt, 100% Vùng An Toàn TikTok x Reels).
- Strict * { box-sizing: border-box; } -> 0% chạm cột nút phải X=886..1080px, 0% lỗi font emoji.
- End-Card ghép CẢ 2 HỘP THẬT IS-Net (av01_protein_a.png + av02_bojomi_b.png) + ảnh từng diện mạo + Giá Bộ Đôi 870.000đ + CTKM Tặng 520K + Dòng pháp lý TPBS chuẩn!
"""
import os, sys, json, shutil

WORK_DIR = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Bo_4_Video_Combo_Chieu_Cao"
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

    s0, s1, s2, s3, s4, s5, s6 = segs
    t1 = float(s0["shot_end_s"])
    t2 = float(s1["shot_end_s"])
    t3 = float(s2["shot_end_s"])
    t4 = float(s3["shot_end_s"])
    t5 = float(s4["shot_end_s"])
    end_start = float(s5["shot_end_s"])
    end_dur = round(total_dur - end_start, 2)
    bgm_split = t2

    # Build shot plan cleanly using cfg["split_map"] (splitting s04 and/or s05 into a/b so every clip <= 10.5s & CGI <= 5.75s!)
    shots = [
        ("s01.mp4", 0.0, t1, 0.20),
        ("s02.mp4", t1, round(t2 - t1, 2), 0.20),
        ("s03.mp4", t2, round(t3 - t2, 2), 0.20),
    ]
    callouts = [
        ("c2", round(t1 + 0.22, 2), round(t2 - t1 - 0.55, 2), *cfg["callouts"][0]),
        ("c3", round(t2 + 0.22, 2), round(t3 - t2 - 0.55, 2), *cfg["callouts"][1]),
    ]

    if cfg.get("split_s4"):
        d4 = round(t4 - t3, 2)
        a_dur = min(5.75, round((d4 / 2.0) * 4.0) / 4.0)
        b_dur = round(d4 - a_dur, 2)
        if cfg.get("s4_cgi_second"):
            b_dur = min(5.75, round((d4 / 2.0) * 4.0) / 4.0)
            a_dur = round(d4 - b_dur, 2)
        t4m = round(t3 + a_dur, 2)
        shots.append(("s04a.mp4", t3, a_dur, 0.10))
        shots.append(("s04b.mp4", t4m, b_dur, 0.10))
        callouts.append(("c4", round(t3 + 0.22, 2), round(d4 - 0.55, 2), *cfg["callouts"][2]))
    else:
        shots.append(("s04.mp4", t3, round(t4 - t3, 2), 0.20))
        callouts.append(("c4", round(t3 + 0.22, 2), round(t4 - t3 - 0.55, 2), *cfg["callouts"][2]))

    if cfg.get("split_s5"):
        d5 = round(t5 - t4, 2)
        a_dur = min(5.75, round((d5 / 2.0) * 4.0) / 4.0)
        b_dur = round(d5 - a_dur, 2)
        if cfg.get("s5_cgi_second"):
            b_dur = min(5.75, round((d5 / 2.0) * 4.0) / 4.0)
            a_dur = round(d5 - b_dur, 2)
        t5m = round(t4 + a_dur, 2)
        shots.append(("s05a.mp4", t4, a_dur, 0.10))
        shots.append(("s05b.mp4", t5m, b_dur, 0.10))
        callouts.append(("c5", round(t4 + 0.22, 2), round(d5 - 0.55, 2), *cfg["callouts"][3]))
    else:
        shots.append(("s05.mp4", t4, round(t5 - t4, 2), 0.20))
        callouts.append(("c5", round(t4 + 0.22, 2), round(t5 - t4 - 0.55, 2), *cfg["callouts"][3]))

    shots.append(("s06.mp4", t5, round(end_start - t5, 2), 0.20))
    callouts.append(("c6", round(t5 + 0.22, 2), round(end_start - t5 - 0.55, 2), *cfg["callouts"][4]))

    sfx = [
        ("sfx-01", "sfx_pop_clean.mp3", 0.12, 0.55, 9, 0.24),
        ("sfx-02", "sfx_whoosh_soft.mp3", round(t1 - 0.11, 2), 0.55, 9, 0.22),
        ("sfx-03", "sfx_whoosh_cinematic.mp3", round(t2 - 0.12, 2), 0.90, 9, 0.28),
        ("sfx-04", "sfx_sparkle_shine.mp3", round(t2 + 0.08, 2), 1.65, 10, 0.26),
        ("sfx-05", "sfx_crystal_shimmer.mp3", round(t3 + 0.15, 2), 2.00, 10, 0.54),
        ("sfx-06", "sfx_ping_glass.mp3", round(t4 + 0.10, 2), 0.85, 11, 0.24),
        ("sfx-07", "sfx_chime_warm.mp3", round(t5 + 0.05, 2), 2.20, 10, 0.52),
        ("sfx-08", "sfx_whoosh_cinematic.mp3", round(end_start - 0.12, 2), 0.90, 9, 0.28),
        ("sfx-09", "sfx_sparkle_shine.mp3", round(end_start + 0.18, 2), 1.65, 10, 0.28),
        ("sfx-10", "sfx_notification_cta.mp3", round(end_start + 1.55, 2), 2.10, 11, 0.22),
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

    bgm_auto = build_ducking(segs, 0.0, total_dur, False)

    vo_tags = [
        f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
        f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{5 if i%2==0 else 6}" '
        f'data-volume="1.30" data-fade-in="0.04" data-fade-out="0.06" data-fx-chain="{VO_FX}"></audio>'
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
      .overlay-host {{ position: absolute; inset: 0; z-index: 12; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="{end_start}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene-host" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{end_start}" data-duration="{end_dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <audio id="bgm-main" class="clip" src="assets/audio/bgm_unique.mp3" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="7" data-fade-in="0.24" data-fade-out="0.95" data-fx-chain="{BGM_UNIQUE_FX}" data-automation="{bgm_auto}"></audio>

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
        p_mp4 = os.path.join(vid_dir, sfile)
        if os.path.exists(p_mp4) and os.path.getsize(p_mp4) > 100000:
            shot_els.append(
                f'    <div id="{rid}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>\n'
                f'      <video {COLOR_GRADE_ATTR} id="v{idx+1}" class="clip bg-video" src="assets/videos/{sfile}" '
                f'data-start="{st}" data-duration="{du}" data-media-start="{mstart}" data-hf-media-start-basis="local" '
                f'data-track-index="{tr}" muted playsinline></video>\n'
                f'    </div>'
            )
        else:
            shot_els.append(
                f'    <div id="{rid}" class="clip cam-rig" data-start="{st}" data-duration="{du}" data-track-index="{tr}" data-layout-allow-overflow data-layout-allow-overlap>\n'
                f'      <img class="bg-video" src="assets/images/hero_look.png" alt="Hero" />\n'
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
    tl.fromTo("#fl1", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.14, immediateRender: false }}, {round(t2 - 0.12, 2)})
      .to("#fl1", {{ opacity: 0, duration: 0.24 }}, {round(t2 + 0.02, 2)});
    tl.fromTo("#fl2", {{ opacity: 0 }}, {{ opacity: 0.80, duration: 0.14, immediateRender: false }}, {round(t5 - 0.12, 2)})
      .to("#fl2", {{ opacity: 0, duration: 0.24 }}, {round(t5 + 0.02, 2)});
    window.__timelines["main-video"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "main-video.html"), "w", encoding="utf-8").write(main_vid_html)

    # 2. safe-overlays.html
    hk = cfg["big_hook"]
    hk_end = round(t1 - 0.15, 2)
    c_divs, c_anims = [], []
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

    .big-hook-wrap {{
      position: absolute; bottom: 404px; left: 56px; width: 814px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
      padding: 20px 18px 22px;
      background: linear-gradient(180deg, rgba(255,255,255,0.24) 0%, rgba(255,255,255,0.68) 100%);
      backdrop-filter: blur(6px);
      border: 3px solid rgba(255,255,255,0.85); border-radius: 30px;
      box-shadow: 0 18px 40px rgba(0,0,0,0.28); z-index: 20;
    }}
    .bh-badge {{
      background: {hk["badge_bg"]}; color: #FFF8D6; border: 3px solid #FFE288;
      border-radius: 999px; padding: 9px 26px; font-weight: 800; font-size: 24px;
      letter-spacing: 0.6px; box-shadow: 0 8px 20px rgba(0,0,0,0.28); margin-bottom: 12px;
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

    .brand-chip {{
      position: absolute; top: 258px; left: 58px; opacity: 0;
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.94); border: 2.5px solid #E2B448;
      border-radius: 18px; padding: 8px 18px;
      box-shadow: 0 8px 22px rgba(0,0,0,0.20);
    }}
    .brand-chip img {{ height: 48px; width: auto; display: block; }}
    .brand-chip span {{ font-weight: 800; font-size: 20px; color: #064D33; letter-spacing: 0.4px; }}

    .safe-card {{
      position: absolute; left: 58px; bottom: 396px; width: 812px;
      background: {cfg["card_bg"]};
      border: 2.5px solid #F0CA65; border-left: 9px solid #FCE078;
      border-radius: 24px; padding: 20px 24px;
      box-shadow: 0 14px 32px rgba(0,0,0,0.38); opacity: 0;
    }}
    .sc-tag {{ font-weight: 800; font-size: 21px; color: #FCE186; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px; }}
    .sc-big {{ font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 40px; line-height: 1.12; color: #FFFFFF; text-shadow: 0 3px 10px rgba(0,0,0,0.38); }}
    .sc-sub {{ font-weight: 600; font-size: 23px; color: #EFFBF4; margin-top: 6px; line-height: 1.24; }}
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
    tl.fromTo("#big-hook", {{ scale: 0.94, y: 8 }}, {{ scale: 1.0, y: 0, duration: 0.28, ease: "back.out(1.4)" }}, 0.0)
      .to("#big-hook", {{ opacity: 0, y: -18, filter: "blur(12px)", duration: 0.26, ease: "power2.in" }}, {round(hk_end - 0.26, 2)});
    tl.fromTo("#top-brand", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power2.out", immediateRender: false }}, 0.12)
      .to("#top-brand", {{ opacity: 0, duration: 0.25 }}, {round(end_start - 0.28, 2)});
{chr(10).join(c_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
"""
    open(os.path.join(comp_dir, "safe-overlays.html"), "w", encoding="utf-8").write(overlays_html)

    # 3. endcard.html — BOTH REAL IS-Net Boxes (AV Protein + Bojomi) + Look Portrait + 870.000đ Duo Deal + 100% Safe Zone!
    endcard_html = f"""<template>
  <style>
    {LOCAL_FONT_CSS}
    * {{ box-sizing: border-box; }}
    #root {{
      position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: {cfg["ec_bg"]}; font-family: 'BeVN', sans-serif;
    }}
    .ec-model {{
      position: absolute; top: 256px; right: 58px; width: 410px; height: 594px;
      border-radius: 30px; overflow: hidden; border: 3.5px solid rgba(244,204,100,0.88);
      box-shadow: 0 20px 44px rgba(0,0,0,0.38);
    }}
    .ec-model img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 15%; display: block; }}
    .ec-logo {{
      position: absolute; top: 262px; left: 58px;
      background: rgba(255,255,255,0.96); border: 3px solid #E5B442; border-radius: 22px;
      padding: 10px 22px; box-shadow: 0 10px 26px rgba(0,0,0,0.25);
    }}
    .ec-logo img {{ height: 70px; width: auto; display: block; }}
    .ec-title {{ position: absolute; top: 378px; left: 58px; width: 520px; }}
    .ec-kicker {{ font-weight: 800; font-size: 22px; color: #FCE186; letter-spacing: 0.7px; }}
    .ec-brand {{
      font-family: 'BeVN', 'MontBlk', sans-serif; font-weight: 800; font-size: 48px; line-height: 1.08;
      color: #FFFFFF; text-shadow: 0 5px 16px rgba(0,0,0,0.35); margin-top: 6px;
    }}
    .ec-sub {{ font-weight: 600; font-size: 22px; color: #E8F8F0; margin-top: 10px; line-height: 1.28; }}

    /* BOTH REAL IS-Net Boxes (AV Protein + PLUS + Bojomi) strictly X=58..760px! */
    .ec-boxes {{
      position: absolute; left: 58px; top: 700px; width: 720px; height: 400px;
      display: flex; align-items: flex-end; gap: 16px;
    }}
    .b-col {{ display: flex; flex-direction: column; align-items: center; }}
    .b-tag {{
      background: rgba(4,48,32,0.92); color: #FFF8DC; border: 2px solid #F4CC62;
      border-radius: 999px; padding: 4px 14px; font-weight: 800; font-size: 16px;
      margin-bottom: 6px; white-space: nowrap;
    }}
    .b-pro {{ height: 344px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .b-boj {{ height: 350px; width: auto; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.45)); }}
    .b-plus {{
      width: 52px; height: 52px; border-radius: 50%; flex-shrink: 0; margin-bottom: 140px;
      background: linear-gradient(145deg, #FCE078, #D98E10); border: 3.5px solid #FFFFFF;
      color: #053623; font-weight: 900; font-size: 38px;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 10px 20px rgba(0,0,0,0.38);
    }}

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
      background: linear-gradient(135deg, #064D33, #0F7B54); border: 2.5px solid #FFE288;
      border-radius: 18px; padding: 11px 14px; text-align: center;
      box-shadow: 0 8px 18px rgba(6,77,51,0.32);
    }}
    .ep-1 {{ font-weight: 800; font-size: 17px; color: #FFF3B0; }}
    .ep-2 {{ font-weight: 800; font-size: 18px; color: #FFFFFF; margin-top: 3px; white-space: nowrap; }}
    .ec-cta {{
      margin-top: 15px; background: linear-gradient(90deg, #074F34, #0E744E);
      border: 2.5px solid #F2CC66; border-radius: 18px; padding: 14px 18px;
      text-align: center; font-weight: 800; font-size: 23px; color: #FFF8D6;
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
      <div class="ec-kicker">BỘ ĐÔI NỀN TẢNG CHIỀU CAO</div>
      <div class="ec-brand">BOJOMI +<br/>AV PROTEIN</div>
      <div class="ec-sub">Đạm thực vật 22,05g • Canxi Aquamin F 417,6mg • D3 • K2 MK-7 • Collagen</div>
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
          <div class="ep-l">TRỌN BỘ ĐÔI 2 HỘP CHÍNH HÃNG</div>
          <div class="ep-n">870.000đ</div>
        </div>
        <div class="ep-pr">
          <div class="ep-1">★ CHÍNH HÃNG DROPPII</div>
          <div class="ep-2">PROTEIN 350K + BOJOMI 520K</div>
        </div>
      </div>
      <div class="ec-cta">{cfg["ec_cta"]}</div>
    </div>
    <div id="ec-g" class="ec-legal" data-layout-ignore>{LEGAL_TPBS} {cfg.get("ec_footnote", "Hotline: 0867 399 268")}</div>
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
    print(f"[BUILT HF {cfg['vkey']}] {hf_dir} ({total_dur}s @ 24fps, endcard={end_start}..{total_dur}s)")


CFGS = [
    {
        "vkey": "height_01_dam_va_canxi",
        "slug": "av-height-combo-01",
        "title": "Combo Chiều Cao 01 — Đạm Sạch AV Protein & Canxi Tảo Biển Bojomi",
        "look_img": "HEIGHT_LOOK1_NAVY_POLO_9x16.png",
        "bg_dark": "#052538",
        "ec_bg": "linear-gradient(175deg, #04322A 0%, #0A5E46 48%, #042D23 100%)",
        "brand_chip_label": "COMBO CHIỀU CAO",
        "card_bg": "linear-gradient(145deg, rgba(6,44,58,0.90) 0%, rgba(11,80,74,0.86) 100%)",
        "ec_cta": "▸ NHẮN “CHIỀU CAO” ĐỂ ĐƯỢC TƯ VẤN ĐÚNG ĐỘ TUỔI!",
        "split_s4": True, "split_s5": True,
        "big_hook": {
            "badge": "★ BÍ KÍP CHĂM CHIỀU CAO KHOA HỌC ★",
            "l1": "MUỐN VÓC DÁNG CAO RÁO",
            "l2": "PHẢI ĐỦ ĐẠM + CANXI!",
            "c1": "#06365A", "c2": "#D91A26",
            "s1": 56, "s2": 62,
            "badge_bg": "linear-gradient(135deg, #06426B, #0C7564)",
        },
        "callouts": [
            ("NỀN TẢNG VÓC DÁNG", "CANXI + ĐẠM SẠCH SONG HÀNH", "Đạm làm nguyên liệu xây dựng • Canxi tạo khung xương vững"),
            ("AN VƯỢNG PHARMA", "BỘ ĐÔI BOJOMI + AV PROTEIN", "Đồng hành chăm sóc nền tảng dinh dưỡng cho cả gia đình"),
            ("AV PROTEIN • 2 GÓI / NGÀY", "22,05g ĐẠM • 1.632mg LEUCINE", "Thêm chất xơ Inulin & lợi khuẩn B-3 êm bụng dễ tiêu"),
            ("BOJOMI • 1 GÓI 20G", "417,6mg CANXI • D3 • K2 MK-7", "Canxi tảo biển Aquamin F + 201,4mg Collagen vị Vani"),
            ("LỐI SỐNG KHOA HỌC", "DINH DƯỠNG + NGỦ SỚM + VẬN ĐỘNG", "Ngủ trước 22h & chơi thể thao mỗi ngày cho vóc dáng tối ưu"),
        ],
    },
    {
        "vkey": "height_02_4_tru_cot_vang",
        "slug": "av-height-combo-02",
        "title": "Combo Chiều Cao 02 — 4 Trụ Cột Vàng Phát Triển Chiều Cao Khoa Học",
        "look_img": "HEIGHT_LOOK2_LINEN_MINT_9x16.png",
        "bg_dark": "#042E22",
        "ec_bg": "linear-gradient(175deg, #043120 0%, #0A6141 48%, #042B1D 100%)",
        "brand_chip_label": "4 TRỤ CỘT CHIỀU CAO",
        "card_bg": "linear-gradient(145deg, rgba(5,48,34,0.90) 0%, rgba(12,84,58,0.86) 100%)",
        "ec_cta": "▸ NHẮN “CHIỀU CAO” NHẬN BẢNG HƯỚNG DẪN GIA ĐÌNH!",
        "split_s4": True, "split_s5": True,
        "big_hook": {
            "badge": "★ 4 TRỤ CỘT VÀNG CHO GIA ĐÌNH ★",
            "l1": "CHĂM CHIỀU CAO CHUẨN",
            "l2": "ĐỪNG CHỈ UỐNG CANXI LẺ!",
            "c1": "#05472F", "c2": "#D91A26",
            "s1": 58, "s2": 56,
            "badge_bg": "linear-gradient(135deg, #064F34, #0F7B54)",
        },
        "callouts": [
            ("KHOA HỌC PHÁT TRIỂN", "4 TRỤ CỘT QUYẾT ĐỊNH CHIỀU CAO", "Bữa ăn đủ chất • Ngủ trước 22h • Vận động • Di truyền"),
            ("BỘ ĐÔI CHỦ LỰC", "BOJOMI & AV PROTEIN", "Bổ sung nền tảng Canxi & Đạm thực vật minh bạch chỉ số"),
            ("KIỀNG 3 CHÂN XƯƠNG KHỚP", "CANXI AQUAMIN F + D3 + K2 MK-7", "417,6mg Canxi tảo biển hỗ trợ chăm sóc hệ xương vững chắc"),
            ("ĐẠM THỰC VẬT LÀNH TÍNH", "ĐẬU HÀ LAN & GẠO + LỢI KHUẨN B-3", "Êm bụng, dễ tiêu hóa, hỗ trợ khối cơ khỏe mạnh"),
            ("AN TOÀN & CHUẨN NHÃN", "ĐỌC KỸ NHÃN THEO ĐỘ TUỔI", "Kết hợp chế độ ăn đa dạng & tham vấn chuyên gia cho bé"),
        ],
    },
    {
        "vkey": "height_03_pha_chuan_2_nhiet_do",
        "slug": "av-height-combo-03",
        "title": "Combo Chiều Cao 03 — Bí Kíp Pha Riêng 2 Nhiệt Độ Chuẩn Bao Bì",
        "look_img": "HEIGHT_LOOK3_BUTTER_KITCHEN_9x16.png",
        "bg_dark": "#262008",
        "ec_bg": "linear-gradient(175deg, #053322 0%, #0C6242 48%, #042D1F 100%)",
        "brand_chip_label": "PHA CHUẨN 2 NHIỆT ĐỘ",
        "card_bg": "linear-gradient(145deg, rgba(6,48,34,0.90) 0%, rgba(14,84,58,0.86) 100%)",
        "ec_cta": "▸ NHẮN “CHIỀU CAO” NHẬN LỊCH UỐNG CHUẨN NGÀY!",
        "ec_footnote": "CTKM 25/11–30/11: Mua 3 Bojomi hoặc 5 AV Protein tặng 1 Bojomi 520K • Hotline: 0867 399 268",
        "split_s4": True, "s4_cgi_second": True, "split_s5": True, "s5_cgi_second": True,
        "big_hook": {
            "badge": "✦ LƯU Ý QUAN TRỌNG KHI PHA ✦",
            "l1": "ĐỪNG PHA CHUNG 1 LY!",
            "l2": "PHA CHUẨN 2 NHIỆT ĐỘ!",
            "c1": "#05472F", "c2": "#D91A26",
            "s1": 62, "s2": 60,
            "badge_bg": "linear-gradient(135deg, #064F34, #108057)",
        },
        "callouts": [
            ("LỖI HAY GẶP KHI DÙNG COMBO", "MỖI SẢN PHẨM 1 NHIỆT ĐỘ RIÊNG", "Pha nước sôi chung dễ làm giảm hiệu quả lợi khuẩn B-3"),
            ("LỊCH UỐNG KHOA HỌC", "CHIA 2 KHUNG GIỜ TRONG NGÀY", "Hấp thu nhẹ bụng và giữ trọn vẹn hoạt chất quý"),
            ("BUỔI SÁNG • AV PROTEIN", "PHA NƯỚC MÁT / ẤM 20–40°C", "Bảo toàn lợi khuẩn B-3 & Inulin • Nạp 22,05g đạm sạch"),
            ("BUỔI CHIỀU / TỐI • BOJOMI", "PHA 200ML NƯỚC ẤM 60°C", "Tan mịn hương Vani • 417,6mg Canxi + D3 + K2 + Collagen"),
            ("THÓI QUEN ĐỀU ĐẶN", "ĐÚNG NHIỆT ĐỘ + NGỦ SỚM + TẬP ĐỀU", "Chìa khóa giữ trọn năng lượng và vóc dáng dẻo dai"),
        ],
    },
    {
        "vkey": "height_04_van_dong_va_deal_870k",
        "slug": "av-height-combo-04",
        "title": "Combo Chiều Cao 04 — Đồng Hành Vận Động Giãn Cơ & Bộ Đôi 870K",
        "look_img": "HEIGHT_LOOK4_SKY_STRETCH_9x16.png",
        "bg_dark": "#062A3C",
        "ec_bg": "linear-gradient(175deg, #053447 0%, #0A624B 48%, #042D22 100%)",
        "brand_chip_label": "BỘ ĐÔI 870K • DROPPII",
        "card_bg": "linear-gradient(145deg, rgba(6,46,60,0.90) 0%, rgba(12,86,68,0.86) 100%)",
        "ec_cta": "▸ NHẮN “CHIỀU CAO” NHẬN TƯ VẤN ĐÚNG ĐỘ TUỔI!",
        "ec_footnote": "CTKM 25/11–30/11: Mua 3 Bojomi hoặc 5 AV Protein tặng 1 Bojomi 520K • Hotline: 0867 399 268",
        "split_s4": False, "split_s5": True,
        "big_hook": {
            "badge": "★ BỘ ĐÔI DINH DƯỠNG CHIỀU CAO ★",
            "l1": "BOJOMI + AV PROTEIN",
            "l2": "TRỌN BỘ ĐÔI 870K!",
            "c1": "#063D5C", "c2": "#D91A26",
            "s1": 64, "s2": 64,
            "badge_bg": "linear-gradient(135deg, #064468, #0D7A5E)",
        },
        "callouts": [
            ("VẬN ĐỘNG & GIÃN CƠ", "TẬP ĐỀU CẦN ĐỦ ĐẠM & CANXI", "Thiếu dưỡng chất nền tảng dễ nhanh mỏi, khó bền sức"),
            ("TIỆN LỢI CHỈ 30 GIÂY PHA", "BOJOMI + AV PROTEIN AN VƯỢNG", "Đóng gói lẻ gọn gàng mang đi tập, đi học hay đi làm"),
            ("PHỤC HỒI KHỐI CƠ", "22,05g ĐẠM + 1.632mg LEUCINE", "AV Protein đậu Hà Lan & gạo — Êm bụng, không đầy hơi"),
            ("CHĂM KHUNG XƯƠNG DẺO DAI", "417,6mg CANXI + D3 + K2 + COLLAGEN", "Bojomi Canxi tảo biển Aquamin F hương Vani thơm béo"),
            ("PHÙ HỢP CẢ GIA ĐÌNH", "PHA RIÊNG 2 LY — UỐNG NGON MỖI NGÀY", "Mua 3 Bojomi / 5 AV Protein tặng 1 Bojomi (25–30/11)"),
        ],
    },
]

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for i, c in enumerate(CFGS, 1):
        if arg in ("all", f"h{i}", c["vkey"]):
            build_video(c)
