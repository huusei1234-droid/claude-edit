# -*- coding: utf-8 -*-
"""
Dựng Video #3 ĐÚNG 100% THEO KỊCH BẢN CHIA SẺ KIẾN THỨC ĐỜI THƯỜNG (0% USP ADS!):
"3. Ăn chay, nhìn thế nào để biết bữa ăn có nguồn đạm?"
- KHÔNG khung bảng USP xanh-vàng, KHÔNG nhãn quảng cáo, KHÔNG thẻ chốt cuối, KHÔNG tiếng whoosh/pop TVC
- CHỈ GIỮ ĐÚNG KỊCH BẢN:
  1. Chữ mở đầu sạch tự nhiên: "MÂM CƠM CHAY NÀY, ĐẠM Ở ĐÂU?"
  2. Phụ đề lời thoại tự nhiên của Chị Hậu (giọng nữ miền Bắc ấm áp như đang trò chuyện với khách)
  3. Đúng 3 Cảnh xuyên suốt ~31 giây (Cảnh 1: Mâm cơm chay & câu hỏi nguồn đạm -> Cảnh 2: Đậu phụ sốt cà, đậu gà, đậu lăng & các hũ đậu + ngũ cốc -> Cảnh 3: Lên thực đơn chọn món đạm từ đầu)
"""
import json, os, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

WORK = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Series_7_Video_Kien_Thuc_Chi_Hau\V03_An_Chay_Nguon_Dam")
VO_DIR = WORK / "01_Voiceover"
CLIP_DIR = WORK / "03_Flow_Clips_9x16"
HF_DIR = WORK / "04_HyperFrames_Project"
OUT_DIR = WORK / "05_Final_Video"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")

COLOR_GRADE_ATTR = (
    'data-color-grading="{&quot;preset&quot;:null,&quot;intensity&quot;:1,'
    '&quot;adjust&quot;:{&quot;exposure&quot;:0.02,&quot;contrast&quot;:0.04,'
    '&quot;highlights&quot;:0.01,&quot;shadows&quot;:0.03,&quot;whites&quot;:0.02,'
    '&quot;blacks&quot;:0,&quot;temperature&quot;:0.02,&quot;tint&quot;:0.01,'
    '&quot;vibrance&quot;:0.06,&quot;saturation&quot;:0.02},'
    '&quot;details&quot;:{&quot;vignette&quot;:0.02,&quot;vignetteMidpoint&quot;:0.5,'
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
        {"type": "peaking", "id": "vlow", "params": {"frequency": 215, "gain": -1.4, "q": 1.1}},
        {"type": "peaking", "id": "vpres", "params": {"frequency": 3000, "gain": 1.5, "q": 1.0}},
        {"type": "limiter", "id": "vlim", "params": {"limit": -1.0}},
    ],
})

BGM_FX = html_json({
    "version": 1,
    "nodes": [
        {"type": "gain", "id": "bgu", "params": {"gain": 0.90}},
        {"type": "highpass", "id": "bhu", "params": {"frequency": 85}},
        {"type": "peaking", "id": "bcu", "params": {"frequency": 2300, "gain": -4.5, "q": 0.85}},
        {"type": "limiter", "id": "blu", "params": {"limit": -3.0}},
    ],
})


def build_ducking(segs, total_dur):
    pts = [{"t": 0.0, "v": 0.36}]
    for seg in segs:
        st, en = float(seg["start_s"]), float(seg["end_s"])
        t_in = max(0.05, round(st - 0.16, 2))
        t_dk = max(t_in + 0.02, round(st, 2))
        t_rl = min(total_dur - 0.15, round(en, 2))
        t_up = min(total_dur - 0.08, round(en + 0.25, 2))
        if t_in > pts[-1]["t"] + 0.04:
            pts.append({"t": t_in, "v": 0.32})
        if t_dk > pts[-1]["t"] + 0.02:
            pts.append({"t": t_dk, "v": 0.20})
        if t_rl > pts[-1]["t"] + 0.02:
            pts.append({"t": t_rl, "v": 0.20})
        if t_up > pts[-1]["t"] + 0.02:
            pts.append({"t": t_up, "v": 0.32})
    pts.append({"t": total_dur, "v": 0.36})
    return html_json({"version": 1, "lanes": [{"target": "volume", "points": pts}]})


def prep_clip_clean(src: Path, dst: Path, min_needed_dur: float = 3.9, crop_top_focus: bool = False):
    raw_dur = float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(src)],
            text=True,
        ).strip()
    )
    usable = max(1.5, raw_dur - 0.14)
    pts_factor = 1.0 if usable >= min_needed_dur else min(1.25, min_needed_dur / usable)
    if crop_top_focus:
        # Slight 6% zoom-up crop so bottom edge stays 100% pure vegan greens/rice/mushrooms/pumpkin soup
        vf = f"trim=start=0.14,setpts={pts_factor:.4f}*(PTS-STARTPTS),scale=1148:2040:force_original_aspect_ratio=increase,crop=1080:1920:34:24,fps=24"
    else:
        vf = f"trim=start=0.14,setpts={pts_factor:.4f}*(PTS-STARTPTS),scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24"
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-vf", vf, "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p",
        str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(src),
            "-vf", vf, "-an",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
            str(dst),
        ], check=True)


def split_even(t0: float, t1: float, n: int):
    dur = round(t1 - t0, 3)
    step = dur / n
    out, cur = [], t0
    for i in range(n):
        nxt = t1 if i == n - 1 else round(cur + step, 2)
        out.append((round(cur, 2), round(nxt - cur, 2)))
        cur = nxt
    return out


def build_subtitle_chunks(segs):
    manual_splits = {
        "vo_01": [
            "Một mâm cơm chay có cơm, rau luộc,",
            "canh bí và nấm xào nhìn rất đầy đặn.",
        ],
        "vo_02": [
            "Trước khi ăn, Hậu hay hỏi một câu:",
            "“Món nào hôm nay là nguồn đạm chính?”",
        ],
        "vo_03": [
            "Nếu chưa có, mình có thể thêm đậu phụ sốt cà,",
            "một phần đậu gà hoặc đậu lăng.",
        ],
        "vo_04": [
            "Ăn chay lâu dài thì đổi qua lại các loại đậu",
            "và ngũ cốc trong ngày",
            "để có nguồn axit amin đa dạng hơn.",
        ],
        "vo_05": [
            "Lần tới nấu cơm chay, thử chọn món đạm",
            "ngay từ lúc lên thực đơn nhé.",
        ],
    }
    subs = []
    for seg in segs:
        st, en = float(seg["start_s"]), float(seg["end_s"])
        dur = en - st
        parts = manual_splits.get(seg["id"], [seg["text"]])
        char_lens = [max(4, len(p)) for p in parts]
        total_chars = sum(char_lens)
        cur = st
        for i, p in enumerate(parts):
            nxt = en if i == len(parts) - 1 else round(cur + dur * (char_lens[i] / total_chars), 2)
            subs.append((round(cur, 2), round(nxt - cur, 2), p))
            cur = nxt
    return subs


def main():
    shutil.rmtree(HF_DIR, ignore_errors=True)
    comp_dir = HF_DIR / "compositions"
    vid_dir = HF_DIR / "assets" / "videos"
    aud_dir = HF_DIR / "assets" / "audio"
    fnt_dir = HF_DIR / "assets" / "fonts"
    for d in (comp_dir, vid_dir, aud_dir, fnt_dir):
        d.mkdir(parents=True, exist_ok=True)

    for fn in ["BeVietnamPro-SemiBold.ttf", "BeVietnamPro-Bold.ttf", "BeVietnamPro-ExtraBold.ttf"]:
        shutil.copy2(FONTS_DIR / fn, fnt_dir / fn)

    vo_data = json.loads((VO_DIR / "vo_manifest.json").read_text(encoding="utf-8"))
    segs = vo_data["segments"]
    sc1_end = float(vo_data["scenes"][0]["end_s"])   # 11.20s
    sc2_end = float(vo_data["scenes"][1]["end_s"])   # 25.12s
    # Natural conversational finish ~1.15s after vo_05 ends -> 30.90s (right in 30–40s, zero USP endcard!)
    total_dur = round(float(segs[-1]["end_s"]) + 1.15, 2)

    shutil.copy2(vo_data["bgm_path"], aud_dir / "bgm_warm_acoustic.mp3")
    for s in segs:
        shutil.copy2(s["path"], aud_dir / f"{s['id']}.wav")

    # ONLY 8 100%-VISUALLY-VERIFIED CLEAN CLIPS (polluted c2_s3 DELETED!)
    clean_clips = ["c1_s1", "c1_s2", "c1_s3", "c2_s1", "c2_s2", "c3_s2", "c3_s1", "c3_s3"]
    for cn in clean_clips:
        src_p = CLIP_DIR / f"{cn}.mp4"
        assert src_p.exists(), f"Missing verified clip: {src_p}"
        need_d = 4.48 if cn in ("c2_s1", "c2_s2", "c3_s2") else 3.85
        prep_clip_clean(src_p, vid_dir / f"{cn}.mp4", min_needed_dur=need_d, crop_top_focus=(cn == "c1_s3"))

    sc2_cut_end = 24.46  # right before vo_05 starts at 25.12s
    # 3 Calm, Cohesive Narrative Scenes (~10–13s/scene), using ONLY the 8 verified clean clips:
    # - Cảnh 1 (0.00 -> 11.20s = 11.20s): Mâm cơm chay & câu hỏi nguồn đạm chính
    w_sc1 = split_even(0.0, sc1_end, 3)
    sc1_shots = [
        ("c1_s1.mp4", 0.0, 1.00, 1.02),
        ("c1_s2.mp4", 0.0, 1.02, 1.00),
        ("c1_s3.mp4", 0.0, 1.00, 1.02),
    ]

    # - Cảnh 2 (11.20 -> 24.46s = 13.26s): Đậu phụ sốt cà -> Đậu gà -> Dàn hũ đậu lăng, các loại đậu & ngũ cốc
    w_sc2 = split_even(sc1_end, sc2_cut_end, 3)
    sc2_shots = [
        ("c2_s1.mp4", 0.0, 1.00, 1.02),      # Đậu phụ sốt cà
        ("c2_s2.mp4", 0.0, 1.02, 1.00),      # Đậu gà
        ("c3_s2.mp4", 0.0, 1.00, 1.02),      # Dàn hũ đậu lăng đỏ, các loại đậu & ngũ cốc đổi qua lại trong ngày
    ]

    # - Cảnh 3 (24.46 -> 30.90s = 6.44s): Chọn món đạm ngay từ lúc lên thực đơn
    w_sc3 = split_even(sc2_cut_end, total_dur, 2)
    sc3_shots = [
        ("c3_s1.mp4", 0.0, 1.00, 1.02),      # Ghi sổ lên thực đơn chọn món đạm
        ("c3_s3.mp4", 0.0, 1.02, 1.00),      # Mỉm cười ấm áp bên mâm cơm chay đủ đạm
    ]

    all_beats = []
    for win, shots in [(w_sc1, sc1_shots), (w_sc2, sc2_shots), (w_sc3, sc3_shots)]:
        for (st, du), (fn, ms, s0, s1) in zip(win, shots):
            all_beats.append((st, du, fn, ms, s0, s1))

    print(f"[PURE SCRIPT TIMELINE] Total={total_dur:.2f}s | 3 Scenes ({sc1_end:.1f}s / {sc2_end-sc1_end:.1f}s / {total_dur-sc2_end:.1f}s) | {len(all_beats)} clean shots (ZERO repeats, ZERO foreign clips!)")

    (HF_DIR / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": False}, "authoringSkill": "hyperframes",
    }, indent=2), encoding="utf-8")
    (HF_DIR / "package.json").write_text(json.dumps({
        "name": "av-hau-v03-anchay-clean", "private": True, "type": "module",
        "scripts": {"check": "npx --yes hyperframes@0.9.38 check", "render": "npx --yes hyperframes@0.9.38 render"},
    }, indent=2), encoding="utf-8")
    (HF_DIR / "meta.json").write_text(json.dumps({
        "title": vo_data["title"], "width": 1080, "height": 1920, "fps": 24, "duration": total_dur,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    bgm_auto = build_ducking(segs, total_dur)
    vo_tags = [
        f'      <audio id="aud-{s["id"]}" class="clip" src="assets/audio/{s["id"]}.wav" '
        f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{5 if i%2==0 else 6}" '
        f'data-volume="1.32" data-fade-in="0.03" data-fade-out="0.05" data-fx-chain="{VO_FX}"></audio>'
        for i, s in enumerate(segs)
    ]

    font_css = """
      @font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-SemiBold.ttf') format('truetype'); font-weight: 600; }
      @font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-Bold.ttf') format('truetype'); font-weight: 700; }
      @font-face { font-family: 'BeVN'; src: url('assets/fonts/BeVietnamPro-ExtraBold.ttf') format('truetype'); font-weight: 800; }
    """

    (HF_DIR / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{vo_data["title"]}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      {font_css}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #1B241D; font-family: 'BeVN', sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .overlay-host {{ position: absolute; inset: 0; z-index: 14; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-fps="24" data-duration="{total_dur}">
      <div id="main-video" class="scene-host" data-composition-id="main-video" data-composition-src="compositions/main-video.html" data-start="0" data-duration="{total_dur}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="safe-overlays" class="overlay-host" data-composition-id="safe-overlays" data-composition-src="compositions/safe-overlays.html" data-start="0" data-duration="{total_dur}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <audio id="bgm-main" class="clip" src="assets/audio/bgm_warm_acoustic.mp3" data-start="0" data-duration="{total_dur}" data-media-start="0" data-track-index="7" data-fade-in="0.35" data-fade-out="1.10" data-fx-chain="{BGM_FX}" data-automation="{bgm_auto}"></audio>
{chr(10).join(vo_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""", encoding="utf-8")

    shot_els, shot_anims = [], []
    for idx, (st, du, fn, ms, sc0, sc1) in enumerate(all_beats):
        rid = f"rig{idx+1}"
        tr = 1 + (idx % 3)
        shot_els.append(
            f'    <div id="{rid}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>\n'
            f'      <video {COLOR_GRADE_ATTR} id="v{idx+1}" class="clip bg-video" src="assets/videos/{fn}" '
            f'data-start="{st}" data-duration="{du}" data-media-start="{ms}" data-hf-media-start-basis="local" '
            f'data-track-index="{tr}" muted playsinline></video>\n'
            f'    </div>'
        )
        shot_anims.append(
            f'    tl.fromTo("#{rid}", {{ scale: {sc0} }}, {{ scale: {sc1}, duration: {du}, ease: "none", immediateRender: false }}, {st});'
        )

    (comp_dir / "main-video.html").write_text(f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: #1B241D; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 42%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
  </style>
  <div id="root" data-composition-id="main-video" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
{chr(10).join(shot_els)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(shot_anims)}
    window.__timelines["main-video"] = tl;
  </script>
</template>
""", encoding="utf-8")

    # safe-overlays.html — ZERO USP BANNERS! ONLY:
    # 1) Chữ mở đầu (0.0s - 3.6s): "MÂM CƠM CHAY NÀY, ĐẠM Ở ĐÂU?" (clean natural creator title, no ad box)
    # 2) Clean natural subtitles at bottom Safe Zone
    subs = build_subtitle_chunks(segs)
    sub_divs, sub_anims = [], []
    for idx, (st, du, raw_txt) in enumerate(subs):
        sid = f"sub{idx+1}"
        sub_divs.append(f'    <div id="{sid}" class="sub-line" data-layout-ignore><span>{raw_txt}</span></div>')
        sub_anims.append(
            f'    tl.fromTo("#{sid}", {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.14, ease: "power2.out", immediateRender: false }}, {st})\n'
            f'      .to("#{sid}", {{ opacity: 0, duration: 0.12 }}, {round(st + du - 0.12, 2)});'
        )

    (comp_dir / "safe-overlays.html").write_text(f"""<template>
  <style>
    {font_css}
    * {{ box-sizing: border-box; }}
    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; pointer-events: none; font-family: 'BeVN', sans-serif; }}

    /* Chữ mở đầu tự nhiên kiểu kênh chia sẻ kiến thức đời thường (không khung hộp quảng cáo USP) */
    .open-title {{
      position: absolute; bottom: 540px; left: 60px; width: 810px;
      text-align: left;
    }}
    .ot-line1 {{
      font-weight: 800; font-size: 48px; line-height: 1.18; color: #FFFFFF;
      -webkit-text-stroke: 8px rgba(24, 38, 28, 0.88); paint-order: stroke fill;
      filter: drop-shadow(0 6px 16px rgba(0,0,0,0.45));
    }}
    .ot-line2 {{
      font-weight: 800; font-size: 56px; line-height: 1.18; color: #FFE484; margin-top: 4px;
      -webkit-text-stroke: 9px rgba(24, 38, 28, 0.90); paint-order: stroke fill;
      filter: drop-shadow(0 6px 16px rgba(0,0,0,0.45));
    }}

    /* Phụ đề trò chuyện tối giản, dễ đọc, nằm gọn trong vùng an toàn TikTok/Reels (bottom 406px, left 60px, max-width 810px) */
    .sub-line {{
      position: absolute; bottom: 406px; left: 60px; width: 810px; opacity: 0;
      display: flex; justify-content: center; text-align: center;
    }}
    .sub-line > span {{
      display: inline-block; max-width: 810px;
      background: rgba(18, 24, 20, 0.68);
      backdrop-filter: blur(4px);
      border-radius: 16px; padding: 12px 22px;
      font-weight: 700; font-size: 32px; line-height: 1.35; color: #FFFFFF;
      text-shadow: 0 2px 6px rgba(0,0,0,0.55);
    }}
  </style>
  <div id="root" data-composition-id="safe-overlays" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
    <div id="open-title" class="open-title" data-layout-ignore>
      <div class="ot-line1">MÂM CƠM CHAY NÀY,</div>
      <div class="ot-line2">ĐẠM Ở ĐÂU?</div>
    </div>
{chr(10).join(sub_divs)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#open-title", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power2.out" }}, 0.0)
      .to("#open-title", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, 3.45);
{chr(10).join(sub_anims)}
    window.__timelines["safe-overlays"] = tl;
  </script>
</template>
""", encoding="utf-8")

    out_mp4 = OUT_DIR / "261126 AVPM Chi Hau 03 - Mam Com Chay Nay Dam O Dau final.mp4"
    hf_short = Path(r"C:\AI\hf_v03")
    shutil.rmtree(hf_short, ignore_errors=True)
    shutil.copytree(HF_DIR, hf_short)

    short_mp4 = hf_short / "out_final.mp4"
    print("[RENDERING CLEAN STORY]", out_mp4.name, "...", flush=True)
    res = subprocess.run(f'npx --yes hyperframes@0.9.38 render --quality delivery -o "{short_mp4}"', cwd=str(hf_short), shell=True, capture_output=True, text=True)
    if res.returncode != 0 or not short_mp4.exists():
        raise RuntimeError(f"Render failed:\nSTDOUT:{res.stdout[-800:]}\nSTDERR:{res.stderr[-800:]}")
    shutil.copy2(short_mp4, out_mp4)
    shutil.rmtree(hf_short, ignore_errors=True)
    print(f"[DONE MP4] {out_mp4} ({out_mp4.stat().st_size / 1e6:.2f} MB)")

    # Extract 1 frame from EVERY SINGLE ONE of the 9 timeline shots so 0% wrong frame can ever slip through!
    tw, th = 280, 498
    qc = Image.new("RGB", (3 * (tw + 12) + 12, 3 * (th + 32) + 12), (18, 22, 18))
    dr = ImageDraw.Draw(qc)
    tmp_f = WORK / "_tmp_qc9.png"
    for idx, (st, du, fn, _, _, _) in enumerate(all_beats):
        ts = round(st + du * 0.45, 2)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(out_mp4), "-frames:v", "1", str(tmp_f)], check=True)
        im = Image.open(tmp_f).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        c, r = idx % 3, idx // 3
        x, y = 12 + c * (tw + 12), 12 + r * (th + 32)
        qc.paste(im, (x, y))
        dr.text((x + 6, y + th + 6), f"Shot {idx+1}: {fn} (@{ts:.1f}s)", fill=(255, 232, 140))
    tmp_f.unlink(missing_ok=True)
    qc_path = OUT_DIR / "QC_9_Shots_Video_03_Clean_Story.jpg"
    qc.save(qc_path, quality=94)
    print("[QC 9 SHOTS]", qc_path)

    drive_vid_dir = Path(r"G:\My Drive\dự án ngoài\An Vượng\03. Video Hoàn Thiện\261126 - Ngày 26.11.2026")
    drive_vid_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_mp4, drive_vid_dir / out_mp4.name)
    print("[SYNCED DRIVE]", drive_vid_dir / out_mp4.name)


if __name__ == "__main__":
    main()
