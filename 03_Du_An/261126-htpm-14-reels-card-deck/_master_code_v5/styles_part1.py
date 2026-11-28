# -*- coding: utf-8 -*-
"""
Part 1 of Bespoke Non-Occluding Talking-Head Styles (HyperFrames 1080x1920 @ 30fps):
STRICT RULE: 0% B-Roll or UI ever covers Chị Hằng ("không được để broll che mất chị mẫu")!
- Chị Hằng's full real clinic studio (`vid-bg`) + foreground RVM cutout (`vid-fg` at z-index 16) stays 100% visible & unobstructed!
- Top B-Roll / UI strictly sits inside `[22px .. head_top_y - 32px]` (ABOVE her hair crown!).
- Lower B-Roll / Live Sim / Riffle / Subtitles strictly sit inside `[1525px .. 1895px]` (ON the blank white desk below her hands!).
- Multi-cam studio cut (`scale: 1.0 -> 1.05` around `540px 760px`) at `splice_t` when internal speech repetition was spliced out.
"""
import html


def compute_safe_zones(plan: dict):
    head_y = int(plan.get("head_top_y") or 400)
    # Leave generous clearance even if 1.05x camera punch-in occurs at splice_t
    top_y = 22
    top_h = max(272, min(426, head_y - 52))
    # Behind-head 2-line keyword: top 75% sits clearly above hair, bottom 25% tucks 3D behind hair crown!
    kw_top = max(54, head_y - 168)
    desk_y = 1528
    desk_h = 362
    return top_y, top_h, kw_top, desk_y, desk_h


def splice_cam_js(plan: dict, rig_selector: str = "#cam-rig"):
    sp_t = plan.get("splice_t")
    if sp_t is None:
        return ""
    return f'    tl.set("{rig_selector}", {{ scale: 1.05, transformOrigin: "540px 780px" }}, {float(sp_t):.2f});\n'


def hook_box_common_css_and_html(hl1, hl2, hl3, hook_end):
    css = """
    #hook-slot { position: absolute; left: 150px; top: 1485px; width: 780px; height: 336px; z-index: 28; }
    #hook-yellow-box {
      position: relative; width: 100%; height: 100%;
      background: linear-gradient(180deg, #fff200 0%, #ffdb00 100%);
      border-radius: 44px; border: 4px solid #ffffff;
      box-shadow: 0 22px 48px rgba(0,0,0,0.32), inset 0 4px 0 rgba(255,255,255,0.85);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      padding: 20px 26px; text-align: center; overflow: hidden; will-change: transform, opacity;
    }
    #hook-sheen {
      position: absolute; top: -40%; left: -35%; width: 45%; height: 180%;
      background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.65) 50%, rgba(255,255,255,0) 100%);
      pointer-events: none;
    }
    .hook-line {
      font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 47px;
      line-height: 1.17; letter-spacing: -0.015em; color: #080808; text-transform: uppercase;
      position: relative; z-index: 2;
    }
    """
    markup = f"""
    <div id="hook-slot" class="clip" data-start="0" data-duration="{hook_end:.2f}" data-layout-allow-caption-zone data-layout-allow-overflow>
      <div id="hook-yellow-box">
        <div id="hook-sheen" data-layout-ignore></div>
        <div class="hook-line">{hl1}</div>
        <div class="hook-line">{hl2}</div>
        <div class="hook-line">{hl3}</div>
      </div>
    </div>
    """
    out_t = round(max(0.8, hook_end - 0.24), 2)
    js = f"""
    tl.fromTo("#hook-yellow-box", {{ scale: 0.80, y: 42, rotation: -2, opacity: 0.9 }}, {{ scale: 1.03, y: -4, rotation: 0.4, opacity: 1, duration: 0.22, ease: "back.out(1.8)" }}, 0);
    tl.to("#hook-yellow-box", {{ scale: 1.0, y: 0, rotation: 0, duration: 0.14, ease: "power2.out" }}, 0.22);
    tl.fromTo("#hook-sheen", {{ x: -140, rotation: 18 }}, {{ x: 980, rotation: 18, duration: 0.65, ease: "power2.inOut" }}, 0.28);
    tl.to("#hook-yellow-box", {{ x: -380, scale: 0.88, rotation: -6, opacity: 0, duration: 0.22, ease: "power3.in" }}, {out_t:.2f});
    """
    return css, markup, js


# ═══════════════════════════════════════════════════════════════════════════
# STYLE 2: TALKING-HEAD V3 TOP TILTED DUAL B-ROLL + 3 NEON TILES + STROKE-UP
# Chị Hằng 100% UNCOVERED (RVM foreground z-index 16 + Top Cards strictly above head!)
# Used on Video #02 (Tinh dịch ≠ Tinh trùng) & Video #10 (Mềm sau xuất vs Mềm sớm)
# ═══════════════════════════════════════════════════════════════════════════
def build_style2_thv3_dualsplit(sp, plan):
    dur = plan["dur"]
    hook_end = plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    top_y, top_h, kw_top, desk_y, _ = compute_safe_zones(plan)
    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    bkw1, bkw2 = [html.escape(x) for x in sp["behind_kw_lines"]]
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]

    # Upper Twin Neon B-Roll Showcase after Behind-Head Keyword (Chị Hằng stays 100% visible below!)
    split_s = round(min(dur - 3.4, kw_e + 0.25), 2)
    split_e = round(min(dur - 0.35, split_s + 4.20), 2)

    if sp["idx"] == 2:
        tiles = [("💧", "LƯỢNG DỊCH"), ("≠", "KHÁC NHAU"), ("🔬", "TINH BINH")]
        num_str = "02"
        vs_badge = "≠"
    else:
        tiles = [("⚡", "ĐÃ XUẤT"), ("🔋", "HỒI PHỤC"), ("✔", "SINH LÝ")]
        num_str = "10"
        vs_badge = "VS"

    h_css, h_html, h_js = hook_box_common_css_and_html(hl1, hl2, hl3, hook_end)
    tile_h = min(194, top_h - 14)
    tile_out = round(hook_end - 0.22, 2)
    img_h = max(172, top_h - 92)

    cap_divs, cap_js = [], []
    for i, p in enumerate(plan["pills"], 1):
        plain_txt = p["html"].replace('<span class="hl-yellow">', '<span class="su-accent">')
        cap_divs.append(
            f'<div id="su-{i}" class="su-wrap" data-layout-ignore>'
            f'<div class="su-ghost">{plain_txt}</div>'
            f'<div class="su-main">{plain_txt}</div>'
            f'</div>'
        )
        cap_js.append(f'{{ id: "#su-{i}", s: {p["s"]:.2f}, e: {p["e"]:.2f} }}')

    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }}
    @font-face {{ font-family: "BarlowItalic"; src: url("assets/fonts/BarlowCondensed-BlackItalic.ttf") format("truetype"); font-weight: 900; font-style: italic; font-display: block; }}
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "Asap"; src: url("assets/fonts/AsapCondensed-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}

    #root {{ position: absolute; inset: 0; overflow: hidden; background: #0d1117; }}
    #cam-rig {{ position: absolute; inset: 0; transform-origin: 540px 780px; will-change: transform; }}
    #vid-bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    /* Dim plate ONLY dims the studio wall behind Chị Hằng; vid-fg stays 100% crisp & bright! */
    #dim-plate {{
      position: absolute; inset: 0; z-index: 2; opacity: 0;
      background: radial-gradient(circle at 50% 44%, rgba(16, 22, 46, 0.48) 0%, rgba(7, 10, 22, 0.76) 100%);
    }}

    /* Behind-Head Keyword & Neon Number (z-index 6, strictly BEHIND vid-fg z-index 16!) */
    #behind-stage {{ position: absolute; inset: 0; z-index: 6; pointer-events: none; }}
    #neon-num {{
      position: absolute; right: 38px; top: {max(20, kw_top - 45)}px;
      font-family: "BarlowItalic", sans-serif; font-size: 250px; line-height: 0.85;
      color: rgba(154, 130, 255, 0.38); -webkit-text-stroke: 7px #8ff8ff;
      filter: drop-shadow(0 0 22px rgba(143, 248, 255, 0.80)); opacity: 0;
    }}
    #kw-sweep-text {{
      position: absolute; left: 28px; top: {kw_top}px; width: 1024px; text-align: center;
      font-family: "Anton", sans-serif; font-size: 98px; line-height: 1.02; letter-spacing: 0.01em;
      text-transform: uppercase;
      background: linear-gradient(180deg, #ffffff 0%, #e9d5ff 48%, #a78bfa 100%);
      -webkit-background-clip: text; background-clip: text; color: transparent;
      -webkit-text-stroke: 7px #090d18; paint-order: stroke fill;
      filter: drop-shadow(0 10px 24px rgba(0,0,0,0.65)); opacity: 0;
    }}

    /* Upper Twin Neon Showcase Cards (strictly inside Y = {top_y}..{top_y + top_h}px ABOVE head!) */
    #top-dual-showcase {{
      position: absolute; left: 32px; top: {top_y}px; width: 1016px; height: {top_h}px;
      z-index: 12; pointer-events: none;
    }}
    .th-bcard {{
      position: absolute; top: 0; width: 484px; height: {top_h}px; border-radius: 30px;
      background: #0f172a; border: 4px solid #8ff8ff;
      box-shadow: 0 18px 42px rgba(0,0,0,0.46), 0 0 22px rgba(92,247,224,0.32);
      overflow: hidden; display: flex; flex-direction: column; justify-content: space-between;
      opacity: 0;
    }}
    .th-bcard.right-c {{ right: 0; border-color: #a78bfa; box-shadow: 0 18px 42px rgba(0,0,0,0.46), 0 0 22px rgba(167,139,250,0.36); }}
    .th-bcard img {{ width: 100%; height: {img_h}px; object-fit: cover; display: block; }}
    .th-bar {{
      flex: 1; padding: 8px 16px; background: linear-gradient(90deg, #090d18 0%, #172036 100%);
      display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
    }}
    .th-head {{ font-family: "Asap", sans-serif; font-size: 30px; line-height: 1.08; color: #ffffff; text-transform: uppercase; }}
    .th-sub {{ font-family: "Asap", sans-serif; font-size: 21px; color: #5cf7e0; margin-top: 2px; }}
    #th-vs-orb {{
      position: absolute; left: 468px; top: {int(top_h * 0.34)}px; width: 80px; height: 80px;
      border-radius: 50%; background: linear-gradient(135deg, #7c3aed, #06b6d4);
      border: 4px solid #ffffff; box-shadow: 0 10px 26px rgba(0,0,0,0.55);
      display: flex; align-items: center; justify-content: center;
      font-family: "Montserrat", sans-serif; font-size: 28px; color: #ffffff; z-index: 14; opacity: 0;
    }}

    /* FOREGROUND CHỊ HẰNG CUTOUT AT Z-INDEX 16 -> NEVER COVERED BY GRAPHICS! */
    #vid-fg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 16; pointer-events: none; }}

    /* 3 Dark Neon EdgeSweep Icon Tiles on Hook (strictly above head!) */
    .neon-tile {{
      position: absolute; width: 194px; height: {tile_h}px; border-radius: 34px;
      background: radial-gradient(circle at 80% 85%, #2e1065 0%, #101318 72%);
      border: 4px solid #9b3cff;
      box-shadow: 0 14px 32px rgba(0,0,0,0.42), 0 0 20px rgba(155, 60, 255, 0.50);
      display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;
      z-index: 14; opacity: 0; overflow: hidden;
    }}
    .tile-sweep {{
      position: absolute; inset: -40%;
      background: conic-gradient(from 0deg, transparent 0deg, transparent 290deg, #55f2ff 345deg, transparent 360deg);
      opacity: 0.7; z-index: 0;
    }}
    .tile-inner {{
      position: absolute; inset: 5px; border-radius: 29px;
      background: radial-gradient(circle at 80% 85%, #2a1258 0%, #101318 74%); z-index: 1;
    }}
    .tile-ico {{ position: relative; z-index: 2; font-size: 56px; filter: drop-shadow(0 0 12px #55f2ff); }}
    .tile-lbl {{ position: relative; z-index: 2; font-family: "Asap", sans-serif; font-size: 23px; color: #55f2ff; letter-spacing: 0.03em; }}
    .burst-ring {{
      position: absolute; width: 84px; height: 84px; border-radius: 50%;
      border: 5px solid #ffffff; box-shadow: 0 0 16px #55f2ff; z-index: 13; opacity: 0; pointer-events: none;
    }}

    /* Desk-Zone Italic Dual-Glow Subtitles + Stroke-Up Ghost (Y = {desk_y + 30}px on white desk!) */
    .su-wrap {{
      position: absolute; left: 56px; top: {desk_y + 34}px; width: 968px; text-align: center;
      z-index: 22; opacity: 0; pointer-events: none;
    }}
    .su-main {{
      display: inline-block; padding: 12px 30px; border-radius: 26px;
      background: rgba(8, 14, 28, 0.86); border: 2px solid rgba(92,247,224,0.45);
      font-family: "BarlowItalic", sans-serif; font-size: 62px; line-height: 1.08;
      color: #5cf7e0; -webkit-text-stroke: 2px #061318; paint-order: stroke fill;
      box-shadow: 0 14px 32px rgba(0,0,0,0.36);
    }}
    .su-accent {{ color: #ffe600; }}
    .su-ghost {{
      position: absolute; inset: 0; font-family: "BarlowItalic", sans-serif; font-size: 62px; line-height: 1.08;
      color: transparent; -webkit-text-stroke: 3px #5cf7e0; opacity: 0; pointer-events: none;
    }}
    {h_css}
  </style>

  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <div id="cam-rig" data-layout-allow-overflow>
      <video id="vid-bg" class="clip" src="assets/videos/presenter.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="1" playsinline data-has-audio="true" data-volume="1.34"></video>
      <div id="dim-plate" data-layout-ignore></div>
      <div id="behind-stage" data-layout-ignore>
        <div id="neon-num">{num_str}</div>
        <div id="kw-sweep-text"><div>{bkw1}</div><div>{bkw2}</div></div>
      </div>
      <video id="vid-fg" class="clip" src="assets/videos/presenter_cutout.webm" data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
    </div>

    <div id="br-1" class="burst-ring" style="left: 165px; top: {top_y + 42}px" data-layout-ignore></div>
    <div id="br-2" class="burst-ring" style="left: 495px; top: {top_y + 24}px" data-layout-ignore></div>
    <div id="br-3" class="burst-ring" style="left: 825px; top: {top_y + 42}px" data-layout-ignore></div>

    <div id="ntile-1" class="neon-tile" style="left: 112px; top: {top_y + 12}px" data-layout-ignore>
      <div class="tile-sweep"></div><div class="tile-inner"></div>
      <div class="tile-ico">{tiles[0][0]}</div><div class="tile-lbl">{tiles[0][1]}</div>
    </div>
    <div id="ntile-2" class="neon-tile" style="left: 443px; top: {top_y}px" data-layout-ignore>
      <div class="tile-sweep"></div><div class="tile-inner"></div>
      <div class="tile-ico">{tiles[1][0]}</div><div class="tile-lbl">{tiles[1][1]}</div>
    </div>
    <div id="ntile-3" class="neon-tile" style="left: 774px; top: {top_y + 12}px" data-layout-ignore>
      <div class="tile-sweep"></div><div class="tile-inner"></div>
      <div class="tile-ico">{tiles[2][0]}</div><div class="tile-lbl">{tiles[2][1]}</div>
    </div>

    <div id="top-dual-showcase" data-layout-ignore>
      <div id="th-card-l" class="th-bcard" style="left: 0">
        <img src="assets/images/broll_01.jpg" alt="Left B-Roll" />
        <div class="th-bar">
          <div class="th-head">{html.escape(c1['head'])}</div>
          <div class="th-sub">{html.escape(c1['desc'])}</div>
        </div>
      </div>
      <div id="th-vs-orb">{vs_badge}</div>
      <div id="th-card-r" class="th-bcard right-c">
        <img src="assets/images/broll_02.jpg" alt="Right B-Roll" />
        <div class="th-bar">
          <div class="th-head">{html.escape(c2['head'])}</div>
          <div class="th-sub" style="color:#c4b5fd">{html.escape(c2['desc'])}</div>
        </div>
      </div>
    </div>

    {h_html}
    {chr(10).join(cap_divs)}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    {h_js}
{splice_cam_js(plan)}
    const tileStarts = [0.10, 0.24, 0.38];
    [1, 2, 3].forEach((idx, i) => {{
      const ts = tileStarts[i];
      tl.fromTo("#br-" + idx, {{ scale: 0.25, opacity: 0.9 }}, {{ scale: 2.0, opacity: 0, duration: 0.34, ease: "power2.out" }}, ts);
      tl.fromTo("#ntile-" + idx, {{ scale: 0, rotation: i === 0 ? -12 : i === 2 ? 12 : 0, opacity: 0 }}, {{ scale: 1, rotation: i === 0 ? -4 : i === 2 ? 4 : 0, opacity: 1, duration: 0.28, ease: "back.out(1.9)" }}, ts);
      tl.to("#ntile-" + idx + " .tile-sweep", {{ rotation: 360, duration: 2.6, ease: "none" }}, 0);
      tl.to("#ntile-" + idx, {{ y: -60, scale: 0.82, opacity: 0, duration: 0.20, ease: "power2.in" }}, {tile_out:.2f});
    }});

    // Smooth Backdrop Dim Behind RVM Chị Hằng + Giant Behind-Head Keyword ({kw_s:.2f}s -> {kw_e:.2f}s)
    tl.to("#dim-plate", {{ opacity: 1, duration: 0.30, ease: "power2.out" }}, {max(0.1, kw_s - 0.14):.2f});
    tl.fromTo("#neon-num", {{ x: 90, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.26, ease: "back.out(1.6)", immediateRender: false }}, {kw_s:.2f});
    tl.fromTo("#kw-sweep-text", {{ scale: 1.24, y: 20, opacity: 0 }}, {{ scale: 1.0, y: 0, opacity: 1, duration: 0.22, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to(["#kw-sweep-text", "#neon-num"], {{ y: -24, opacity: 0, duration: 0.18, ease: "power2.in" }}, {kw_e - 0.18:.2f});

    // Upper Twin Neon Showcase Cards ABOVE Chị Hằng's Head ({split_s:.2f}s -> {split_e:.2f}s)
    tl.fromTo("#th-card-l", {{ x: -240, y: -30, rotation: -8, opacity: 0 }}, {{ x: 0, y: 0, rotation: -2.2, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {split_s:.2f});
    tl.fromTo("#th-vs-orb", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(2.0)", immediateRender: false }}, {split_s + 0.18:.2f});
    tl.fromTo("#th-card-r", {{ x: 240, y: -30, rotation: 8, opacity: 0 }}, {{ x: 0, y: 0, rotation: 2.2, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {split_s + 0.32:.2f});
    tl.to(["#th-card-l", "#th-card-r", "#th-vs-orb"], {{ y: -50, opacity: 0, duration: 0.24, ease: "power2.in" }}, {split_e - 0.24:.2f});
    tl.to("#dim-plate", {{ opacity: 0, duration: 0.30 }}, {split_e - 0.20:.2f});

    const suCues = [{", ".join(cap_js)}];
    for (const c of suCues) {{
      tl.set(c.id, {{ opacity: 1 }}, c.s);
      tl.fromTo(c.id + " .su-main", {{ y: 28, filter: "blur(12px)", opacity: 0 }}, {{ y: 0, filter: "blur(0px)", opacity: 1, duration: 0.16, ease: "power3.out", immediateRender: false }}, c.s);
      tl.fromTo(c.id + " .su-ghost", {{ scale: 1.0, opacity: 0.75 }}, {{ scale: 1.6, opacity: 0, duration: 0.30, ease: "power2.out", immediateRender: false }}, c.s + 0.04);
      tl.to(c.id, {{ opacity: 0, duration: 0.08 }}, c.e - 0.08);
    }}

    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""
    sfx_cues = [
        ("sfx_pop_clean.mp3", 0.12, 0.30),
        ("sfx_pop_clean.mp3", 0.26, 0.30),
        ("sfx_pop_clean.mp3", 0.40, 0.32),
        ("sfx_whoosh_soft.mp3", max(0.1, kw_s - 0.08), 0.30),
        ("sfx_pop_clean.mp3", split_s + 0.04, 0.28),
        ("sfx_ping_glass.mp3", split_s + 0.34, 0.26),
    ]
    bgm = "bgm_fresh_wellness_tvc.mp3" if sp["idx"] == 2 else "bgm_bright_riley.mp3"
    return scene_html, bgm, sfx_cues


# ═══════════════════════════════════════════════════════════════════════════
# STYLE 3: KOBE LIGHT PASTEL FLOATING TOP-RIBBON + DESK BIO-SIM / RIFFLE 1->5
# Chị Hằng stays 100% FULL STUDIO LIVE & UNCOVERED in the center!
# Used on Video #03 (1🔗2🔗3 Step Ribbon + Desk Ovum/Sperm) & Video #13 (Desk Riffle 1->5)
# ═══════════════════════════════════════════════════════════════════════════
def build_style3_kobe_light_pip(sp, plan):
    dur = plan["dur"]
    hook_end = plan["hook_end"]
    top_y, top_h, _, desk_y, desk_h = compute_safe_zones(plan)
    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    h_css, h_html, h_js = hook_box_common_css_and_html(hl1, hl2, hl3, hook_end)

    stage_s = round(hook_end + 0.06, 2)
    stage_e = round(dur - 0.25, 2)
    span = max(3.0, stage_e - stage_s)
    is_riffle = (sp["idx"] == 13)

    if not is_riffle:
        top_inner = f"""
      <div id="highway-track"></div>
      <div id="step-1" class="kobe-step-card" style="left: 18px">
        <div class="step-top"><span class="step-num">1</span><span class="step-title">SỐ LƯỢNG</span></div>
        <div class="step-ico">🔢</div>
        <div class="step-tag">Mật độ tinh binh</div>
      </div>
      <div id="chain-1" class="chain-badge" style="left: 326px">🔗</div>
      <div id="step-2" class="kobe-step-card" style="left: 358px">
        <div class="step-top"><span class="step-num">2</span><span class="step-title">DI ĐỘNG</span></div>
        <div class="step-ico">⚡</div>
        <div class="step-tag">Bơi thẳng tới trứng</div>
      </div>
      <div id="chain-2" class="chain-badge" style="left: 666px">🔗</div>
      <div id="step-3" class="kobe-step-card" style="left: 698px">
        <div class="step-top"><span class="step-num">3</span><span class="step-title">XÉT NGHIỆM</span></div>
        <div class="step-photo"><img src="assets/images/broll_01.jpg" alt="Lab" /></div>
        <div class="step-tag">Tinh dịch đồ chuẩn</div>
      </div>"""

        desk_inner = """
      <div id="bio-sim-box">
        <div class="kobe-pill-tag"><span>CƯƠNG TỐT ≠ </span><span class="blue-kw">TINH BINH KHỎE!</span></div>
        <canvas id="ovum-canvas" width="980" height="260"></canvas>
        <div class="sim-label">CHẬM CÓ CON → HAI VỢ CHỒNG CÙNG ĐI KIỂM TRA SỚM!</div>
      </div>"""

        anim_js = f"""
    const t1 = {stage_s + 0.14:.2f}, t2 = {stage_s + 0.56:.2f}, t3 = {stage_s + 0.98:.2f};
    tl.fromTo("#pastel-top-ribbon", {{ y: -80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.28, ease: "power3.out", immediateRender: false }}, {stage_s:.2f});
    tl.fromTo("#step-1", {{ y: -70, scale: 0.88, opacity: 0 }}, {{ y: 0, scale: 1, opacity: 1, duration: 0.28, ease: "back.out(1.7)" }}, t1);
    tl.fromTo("#chain-1", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "back.out(2)" }}, t2 - 0.08);
    tl.fromTo("#step-2", {{ y: -70, scale: 0.88, opacity: 0 }}, {{ y: 0, scale: 1, opacity: 1, duration: 0.28, ease: "back.out(1.7)" }}, t2);
    tl.fromTo("#chain-2", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "back.out(2)" }}, t3 - 0.08);
    tl.fromTo("#step-3", {{ y: -70, scale: 0.88, opacity: 0 }}, {{ y: 0, scale: 1, opacity: 1, duration: 0.28, ease: "back.out(1.7)" }}, t3);
    tl.fromTo("#bio-sim-box", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.34, ease: "back.out(1.5)", immediateRender: false }}, {stage_s + 0.32:.2f});

    const octx = document.getElementById("ovum-canvas").getContext("2d");
    const prx = {{ t: 0 }};
    tl.to(prx, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = prx.t;
        octx.clearRect(0, 0, 980, 260);
        const pulse = 1 + Math.sin(t * 3.6) * 0.05;
        octx.save(); octx.translate(835, 134); octx.scale(pulse, pulse);
        octx.beginPath(); octx.arc(0, 0, 62, 0, Math.PI * 2);
        octx.fillStyle = "rgba(244,114,182,0.24)"; octx.fill();
        octx.beginPath(); octx.arc(0, 0, 44, 0, Math.PI * 2);
        const og = octx.createRadialGradient(-12, -12, 5, 0, 0, 44);
        og.addColorStop(0, "#fff1f2"); og.addColorStop(0.55, "#f472b6"); og.addColorStop(1, "#db2777");
        octx.fillStyle = og; octx.fill();
        octx.restore();

        for (let i = 0; i < 5; i++) {{
          const p = ((t * 0.48 + i * 0.21) % 1);
          const sx = 95 + p * 650;
          const sy = 56 + i * 38 + Math.sin(t * 4.2 + i * 1.6) * 10;
          octx.save(); octx.translate(sx, sy);
          octx.beginPath();
          for (let k = 0; k <= 12; k++) {{
            const u = k / 12;
            const tx = -12 - u * 62;
            const ty = (2.5 + u * 9) * Math.sin(t * 20 + i - u * 6.5);
            if (k === 0) octx.moveTo(tx, ty * 0.2); else octx.lineTo(tx, ty);
          }}
          octx.strokeStyle = i < 3 ? "#3656fb" : "#94a3b8";
          octx.lineWidth = 4.5; octx.lineCap = "round"; octx.stroke();
          octx.beginPath(); octx.ellipse(0, 0, 15, 9.5, 0, 0, Math.PI * 2);
          octx.fillStyle = i < 3 ? "#3656fb" : "#94a3b8"; octx.fill();
          octx.restore();
        }}
      }}
    }}, 0);"""
    else:
        # Video #13: Top Pastel Photo Twin + Desk Rapid Riffle 1 -> 5!
        top_inner = f"""
      <div class="rf-top-broll">
        <div class="rf-bcard"><img src="assets/images/broll_01.jpg" alt="1" /><span>{html.escape(c1['head'])}</span></div>
        <div class="rf-bcard"><img src="assets/images/broll_02.jpg" alt="2" /><span>{html.escape(c2['head'])}</span></div>
      </div>"""

        signs = [
            ("DẤU HIỆU 1 / 5", "LÀM LIÊN TỤC DÙ CƠ THỂ ĐANG MỆT", "Kiệt sức vẫn khó tự dừng lại"),
            ("DẤU HIỆU 2 / 5", "THỨC KHUYA XEM NỘI DUNG KÍCH THÍCH", "Mất ngủ, đảo lộn nhịp sinh học"),
            ("DẤU HIỆU 3 / 5", "MẤT TẬP TRUNG KHI LÀM VIỆC", "Tâm trí bị xao nhãng ban ngày"),
            ("DẤU HIỆU 4 / 5", "ĐÒI HỎI MỨC ĐỘ NGÀY CÀNG MẠNH", "Tăng ngưỡng kích thích bất thường"),
            ("DẤU HIỆU 5 / 5", "ÍT CẢM XÚC KHI GẦN BẠN ĐỜI THẬT", "Khó kiểm soát → Hãy gặp chuyên gia!"),
        ]
        # Exact spoken cue starts from v13 transcript: 1@3.50, 2@5.30, 3@6.68, 4@8.26, 5@10.76
        cue_times = [3.45, 5.26, 6.65, 8.22, 10.72]
        cards_html, rf_js = [], [f'tl.fromTo("#pastel-top-ribbon", {{ y: -80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.28, ease: "power3.out", immediateRender: false }}, {stage_s:.2f});']
        for idx_s, (btxt, htxt, dtxt) in enumerate(signs, 1):
            rs = cue_times[idx_s - 1]
            re_t = cue_times[idx_s] if idx_s < 5 else dur
            cards_html.append(f"""
        <div id="rf-{idx_s}" class="riffle-card">
          <div class="rf-top-row">
            <span class="rf-check">⚠ CẦN CHÚ Ý</span>
            <span class="rf-counter">{btxt}</span>
          </div>
          <div class="rf-body-row">
            <div class="riffle-num-big">0{idx_s}</div>
            <div class="rf-texts">
              <div class="rf-head">{htxt}</div>
              <div class="rf-sub">{dtxt}</div>
            </div>
          </div>
        </div>""")
            rf_js.append(
                f'tl.fromTo("#rf-{idx_s}", {{ y: 90, scale: 0.92, filter: "blur(10px)", opacity: 0 }}, '
                f'{{ y: 0, scale: 1.0, filter: "blur(0px)", opacity: 1, duration: 0.22, ease: "back.out(1.6)", immediateRender: false }}, {rs:.2f});'
            )
            if idx_s < 5:
                rf_js.append(f'tl.to("#rf-{idx_s}", {{ y: -70, scale: 0.94, opacity: 0, duration: 0.18, ease: "power2.in" }}, {re_t - 0.18:.2f});')
        desk_inner = '<div id="riffle-window">' + "\n".join(cards_html) + "</div>"
        anim_js = "\n    ".join(rf_js)

    card_inner_h = top_h - 24
    photo_mini_h = max(92, card_inner_h - 118)

    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "BeVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #f4f6fc; }}
    #cam-rig {{ position: absolute; inset: 0; transform-origin: 540px 780px; will-change: transform; }}
    #vid-bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    #vid-fg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 16; pointer-events: none; }}

    /* Top Floating Kobe Light Pastel Dot-Grid Ribbon (strictly Y = {top_y}..{top_y + top_h}px ABOVE head!) */
    #pastel-top-ribbon {{
      position: absolute; left: 32px; top: {top_y}px; width: 1016px; height: {top_h}px;
      border-radius: 34px; border: 4px solid #ffffff;
      background:
        radial-gradient(#cbd5f0 2.5px, transparent 2.5px),
        linear-gradient(180deg, #f6f8ff 0%, #eef2ff 100%);
      background-size: 26px 26px, 100% 100%;
      box-shadow: 0 18px 42px rgba(30, 41, 59, 0.18);
      z-index: 12; overflow: hidden; opacity: 0;
    }}
    #highway-track {{
      position: absolute; left: 0; top: {int(top_h * 0.50)}px; width: 1016px; height: 26px;
      background: #c7d2fe; z-index: 1;
    }}
    #highway-track::after {{
      content: ""; position: absolute; left: 0; right: 0; top: 10px; height: 5px;
      background: repeating-linear-gradient(90deg, #ffffff 0 18px, transparent 18px 34px);
    }}
    .kobe-step-card {{
      position: absolute; top: 12px; width: 300px; height: {card_inner_h}px; border-radius: 26px;
      background: #ffffff; border: 3px solid #dbe4ff;
      box-shadow: 0 12px 28px rgba(45,62,140,0.12);
      padding: 12px 14px; display: flex; flex-direction: column; align-items: center; justify-content: space-between;
      z-index: 3; opacity: 0;
    }}
    .step-top {{ display: flex; align-items: center; gap: 10px; width: 100%; }}
    .step-num {{
      width: 42px; height: 42px; border-radius: 50%; background: #141418; color: #ffffff;
      font-family: "Montserrat", sans-serif; font-size: 22px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }}
    .step-title {{ font-family: "BeVN", sans-serif; font-size: 26px; color: #3656fb; }}
    .step-ico {{ font-size: 62px; line-height: 1; }}
    .step-photo {{ width: 100%; height: {photo_mini_h}px; border-radius: 16px; overflow: hidden; }}
    .step-photo img {{ width: 100%; height: 100%; object-fit: cover; }}
    .step-tag {{ font-family: "BeVN", sans-serif; font-size: 21px; color: #475569; text-align: center; }}
    .chain-badge {{ position: absolute; top: {int(top_h * 0.42)}px; font-size: 34px; z-index: 5; opacity: 0; }}

    .rf-top-broll {{ display: flex; gap: 18px; padding: 12px; width: 100%; height: 100%; }}
    .rf-bcard {{ flex: 1; position: relative; border-radius: 24px; overflow: hidden; border: 3px solid #c7d2fe; }}
    .rf-bcard img {{ width: 100%; height: 100%; object-fit: cover; }}
    .rf-bcard span {{
      position: absolute; left: 12px; right: 12px; bottom: 10px; padding: 8px 14px;
      border-radius: 999px; background: rgba(20,20,24,0.86); color: #ffffff;
      font-family: "BeVN", sans-serif; font-size: 24px; text-align: center;
    }}

    /* Desk-Zone Kobe SaaS Interactive Card (Y = {desk_y}..{desk_y + desk_h}px on blank white table!) */
    #desk-kobe-host {{
      position: absolute; left: 42px; top: {desk_y}px; width: 996px; height: {desk_h}px; z-index: 20; pointer-events: none;
    }}
    #bio-sim-box {{
      position: relative; width: 100%; height: 100%; border-radius: 34px;
      background: #ffffff; border: 4px solid #ced8fa;
      box-shadow: 0 20px 46px rgba(30,41,59,0.22); overflow: hidden; opacity: 0;
      display: flex; flex-direction: column; justify-content: space-between; padding: 14px 18px;
    }}
    .kobe-pill-tag {{
      align-self: center; padding: 6px 26px; border-radius: 999px; background: #eef2ff;
      font-family: "BeVN", sans-serif; font-size: 31px; color: #141418; transform: rotate(-1.2deg);
    }}
    .kobe-pill-tag .blue-kw {{ color: #3656fb; }}
    .sim-label {{ text-align: center; font-family: "BeVN", sans-serif; font-size: 25px; color: #1e293b; }}

    #riffle-window {{ position: relative; width: 100%; height: 100%; }}
    .riffle-card {{
      position: absolute; inset: 0; border-radius: 34px; background: #ffffff;
      border: 4px solid #3656fb; box-shadow: 0 22px 48px rgba(30,41,59,0.24);
      padding: 24px 32px; display: flex; flex-direction: column; justify-content: space-between; opacity: 0;
    }}
    .rf-top-row {{ display: flex; justify-content: space-between; align-items: center; }}
    .rf-check {{ padding: 8px 20px; border-radius: 999px; background: #fee2e2; color: #e11d48; font-family: "BeVN", sans-serif; font-size: 26px; }}
    .rf-counter {{ padding: 8px 24px; border-radius: 999px; background: #141418; color: #ffffff; font-family: "Montserrat", sans-serif; font-size: 26px; }}
    .rf-body-row {{ display: flex; align-items: center; gap: 26px; }}
    .riffle-num-big {{
      width: 146px; height: 146px; border-radius: 26px; background: #eef2ff;
      color: #3656fb; font-family: "Montserrat", sans-serif; font-size: 72px;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }}
    .rf-head {{ font-family: "BeVN", sans-serif; font-size: 38px; line-height: 1.15; color: #141418; }}
    .rf-sub {{ margin-top: 8px; font-family: "BeVN", sans-serif; font-size: 28px; color: #475569; }}
    {h_css}
  </style>

  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <div id="cam-rig" data-layout-allow-overflow>
      <video id="vid-bg" class="clip" src="assets/videos/presenter.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="1" playsinline data-has-audio="true" data-volume="1.34"></video>
      <video id="vid-fg" class="clip" src="assets/videos/presenter_cutout.webm" data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
    </div>

    <div id="pastel-top-ribbon" data-layout-ignore>{top_inner}</div>
    <div id="desk-kobe-host" data-layout-ignore>{desk_inner}</div>
    {h_html}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    {h_js}
{splice_cam_js(plan)}
    {anim_js}
    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""
    sfx_cues = [
        ("sfx_whoosh_soft.mp3", max(0.1, stage_s - 0.06), 0.28),
        ("sfx_pop_clean.mp3", stage_s + 0.22, 0.28),
        ("sfx_pop_clean.mp3", stage_s + span * 0.28, 0.28),
        ("sfx_pop_clean.mp3", stage_s + span * 0.54, 0.30),
        ("sfx_ping_glass.mp3", stage_s + span * 0.78, 0.26),
    ]
    bgm = "bgm_bright_riley.mp3" if not is_riffle else "bgm_fresh_wellness_tvc.mp3"
    return scene_html, bgm, sfx_cues


# ═══════════════════════════════════════════════════════════════════════════
# STYLE 4: KOBE DARK CYBER TOP TELEMETRY + DESK HOLO-CONSOLE (DNA / TANK)
# Chị Hằng stays 100% FULL STUDIO LIVE & UNCOVERED in the center!
# Used on Video #04 (Quai bị & DNA Sinh sản) & Video #12 (Bia rượu & Stamina Tank)
# ═══════════════════════════════════════════════════════════════════════════
def build_style4_kobe_dark_cyber(sp, plan):
    dur = plan["dur"]
    hook_end = plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    top_y, top_h, kw_top, desk_y, desk_h = compute_safe_zones(plan)
    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    bkw1, bkw2 = [html.escape(x) for x in sp["behind_kw_lines"]]
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    h_css, h_html, h_js = hook_box_common_css_and_html(hl1, hl2, hl3, hook_end)

    is_dna = (sp["idx"] == 4)
    cy_s = round(min(dur - 4.2, max(hook_end + 0.10, kw_e + 0.20 if kw_s < hook_end + 2.2 else hook_end + 0.12)), 2)
    # Place Cyber Top Cards AFTER Behind-Head Keyword if Behind-Head Keyword is early, else swap cleanly so zero overlap!
    if kw_s < hook_end + 3.2:
        top_card_s = round(kw_e + 0.22, 2)
    else:
        top_card_s = round(hook_end + 0.12, 2)
    top_card_e = round(dur - 0.25, 2)
    thread_t = round(top_card_s + (top_card_e - top_card_s) * 0.44, 2)
    img_h = max(168, top_h - 86)

    console_title = "MÔ PHỎNG DNA & CHỈ SỐ SINH SẢN NAM" if is_dna else "ĐỒ THỊ RÚT CẠN PHẢN XẠ KHI UỐNG BIA RƯỢU"
    console_sub = "Khai rõ tiền sử sưng đau 1 hay 2 bên khi đi khám!" if is_dna else "Rèn nhịp thở • Tập kiểm soát • Không mượn bia rượu!"

    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }}
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "BeVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}

    #root {{ position: absolute; inset: 0; overflow: hidden; background: #0b0f17; }}
    #cam-rig {{ position: absolute; inset: 0; transform-origin: 540px 780px; will-change: transform; }}
    #vid-bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    #cyber-behind-kw {{
      position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center;
      z-index: 6; opacity: 0; pointer-events: none;
    }}
    .cb-l1 {{ font-family: "Anton", sans-serif; font-size: 102px; line-height: 1.02; color: #36ccc8; -webkit-text-stroke: 8px #091318; paint-order: stroke fill; }}
    .cb-l2 {{ font-family: "Anton", sans-serif; font-size: 94px; line-height: 1.04; color: #f26b21; -webkit-text-stroke: 8px #091318; paint-order: stroke fill; }}
    #vid-fg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 16; pointer-events: none; }}

    /* Top Cyber Twin Telemetry Cards (strictly Y = {top_y}..{top_y + top_h}px ABOVE head!) */
    #cyber-top-zone {{
      position: absolute; left: 32px; top: {top_y}px; width: 1016px; height: {top_h}px; z-index: 12; pointer-events: none;
    }}
    .cy-top-card {{
      position: absolute; top: 0; width: 472px; height: {top_h}px; border-radius: 28px;
      background: #121722; border: 3.5px solid #f26b21;
      box-shadow: 0 16px 38px rgba(0,0,0,0.42), 0 0 20px rgba(242,107,33,0.28);
      overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; opacity: 0;
    }}
    .cy-top-card.right-c {{ right: 0; border-color: #36ccc8; box-shadow: 0 16px 38px rgba(0,0,0,0.42), 0 0 20px rgba(54,204,200,0.32); }}
    .cy-top-card img {{ width: 100%; height: {img_h}px; object-fit: cover; }}
    .cy-cap {{ flex: 1; padding: 8px 14px; display: flex; flex-direction: column; justify-content: center; text-align: center; }}
    .cy-t {{ font-family: "BeVN", sans-serif; font-size: 26px; color: #f26b21; text-transform: uppercase; }}
    .cy-top-card.right-c .cy-t {{ color: #36ccc8; }}
    .cy-d {{ font-family: "BeVN", sans-serif; font-size: 20px; color: #e2e8f0; }}
    #thread-svg {{ position: absolute; left: 468px; top: {int(top_h * 0.42)}px; width: 80px; height: 40px; z-index: 14; }}

    /* Desk Cyber Holo-Console (strictly Y = {desk_y}..{desk_y + desk_h}px on blank white desk!) */
    #cyber-desk-console {{
      position: absolute; left: 42px; top: {desk_y}px; width: 996px; height: {desk_h}px;
      border-radius: 34px; background: rgba(14, 19, 28, 0.94);
      background-image: linear-gradient(rgba(54,204,200,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(54,204,200,0.07) 1px, transparent 1px);
      background-size: 28px 28px;
      border: 3.5px solid #36ccc8; box-shadow: 0 20px 46px rgba(0,0,0,0.42), 0 0 28px rgba(54,204,200,0.28);
      padding: 16px 26px; display: flex; flex-direction: column; justify-content: space-between;
      z-index: 20; opacity: 0; pointer-events: none;
    }}
    .cy-console-hdr {{ font-family: "Montserrat", sans-serif; font-size: 26px; color: #36ccc8; text-align: center; letter-spacing: 0.03em; }}
    .cy-console-ftr {{ font-family: "BeVN", sans-serif; font-size: 25px; color: #ffffff; text-align: center; }}
    {h_css}
  </style>

  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <div id="cam-rig" data-layout-allow-overflow>
      <video id="vid-bg" class="clip" src="assets/videos/presenter.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="1" playsinline data-has-audio="true" data-volume="1.34"></video>
      <div id="cyber-behind-kw" data-layout-ignore>
        <div class="cb-l1">{bkw1}</div>
        <div class="cb-l2">{bkw2}</div>
      </div>
      <video id="vid-fg" class="clip" src="assets/videos/presenter_cutout.webm" data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
    </div>

    <div id="cyber-top-zone" data-layout-ignore>
      <div id="cy-c1" class="cy-top-card" style="left:0">
        <img src="assets/images/broll_01.jpg" alt="1" />
        <div class="cy-cap"><div class="cy-t">{html.escape(c1['head'])}</div><div class="cy-d">{html.escape(c1['desc'])}</div></div>
      </div>
      <svg id="thread-svg" viewBox="0 0 80 40">
        <path id="thread-path" d="M 4 20 L 76 20" stroke="#36ccc8" stroke-width="8" stroke-linecap="round" stroke-dasharray="80" stroke-dashoffset="80" fill="none" />
      </svg>
      <div id="cy-c2" class="cy-top-card right-c">
        <img src="assets/images/broll_02.jpg" alt="2" />
        <div class="cy-cap"><div class="cy-t">{html.escape(c2['head'])}</div><div class="cy-d">{html.escape(c2['desc'])}</div></div>
      </div>
    </div>

    <div id="cyber-desk-console" data-layout-ignore>
      <div class="cy-console-hdr">{console_title}</div>
      <canvas id="cyber-viz" width="940" height="225"></canvas>
      <div class="cy-console-ftr">{console_sub}</div>
    </div>

    {h_html}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    {h_js}
{splice_cam_js(plan)}
    // Behind-Head Keyword ({kw_s:.2f}s -> {kw_e:.2f}s)
    tl.fromTo("#cyber-behind-kw", {{ scale: 0.86, y: 24, opacity: 0 }}, {{ scale: 1.0, y: 0, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#cyber-behind-kw", {{ y: -20, opacity: 0, duration: 0.18 }}, {kw_e - 0.18:.2f});

    // Desk Holo-Console enters right after Hook!
    tl.fromTo("#cyber-desk-console", {{ y: 70, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.34, ease: "back.out(1.5)", immediateRender: false }}, {hook_end + 0.12:.2f});

    // Top Cyber B-Roll 1 -> Thread-Line Laser -> Top Cyber B-Roll 2 (strictly ABOVE head!)
    tl.fromTo("#cy-c1", {{ x: -180, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.30, ease: "back.out(1.6)", immediateRender: false }}, {top_card_s:.2f});
    tl.to("#thread-path", {{ strokeDashoffset: 0, duration: 0.22, ease: "power2.out" }}, {thread_t - 0.14:.2f});
    tl.fromTo("#cy-c2", {{ x: 180, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.30, ease: "back.out(1.6)", immediateRender: false }}, {thread_t:.2f});

    const cctx = document.getElementById("cyber-viz").getContext("2d");
    const IS_DNA = {"true" if is_dna else "false"};
    const cprx = {{ t: 0 }};
    tl.to(cprx, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = cprx.t;
        cctx.clearRect(0, 0, 940, 225);
        if (IS_DNA) {{
          for (let i = 0; i < 26; i++) {{
            const x = 45 + i * 34;
            const ph = t * 4.0 + i * 0.35;
            const y1 = 112 + Math.sin(ph) * 76;
            const y2 = 112 - Math.sin(ph) * 76;
            cctx.strokeStyle = "rgba(255,255,255,0.22)";
            cctx.lineWidth = 3;
            cctx.beginPath(); cctx.moveTo(x, y1); cctx.lineTo(x, y2); cctx.stroke();
            cctx.beginPath(); cctx.arc(x, y1, 9.5, 0, Math.PI * 2);
            cctx.fillStyle = "#36ccc8"; cctx.fill();
            cctx.beginPath(); cctx.arc(x, y2, 9.5, 0, Math.PI * 2);
            cctx.fillStyle = "#f26b21"; cctx.fill();
          }}
        }} else {{
          // Horizontal 8-Cell Escalating Stamina Battery Tank (Green -> Amber -> Red + Sparks!)
          const localP = Math.max(0, Math.min(1, (t - {hook_end + 0.4:.2f}) / 5.2));
          const barsLeft = Math.max(1, Math.round(8 - localP * 7));
          const pct = Math.max(12, Math.round(96 - localP * 82));
          const col = barsLeft >= 6 ? "#10b981" : barsLeft >= 3 ? "#f59e0b" : "#ef4444";

          cctx.strokeStyle = col; cctx.lineWidth = 5;
          cctx.beginPath(); cctx.roundRect(70, 42, 650, 140, 24); cctx.stroke();
          cctx.fillStyle = col; cctx.beginPath(); cctx.roundRect(728, 82, 22, 60, 8); cctx.fill();

          for (let b = 0; b < barsLeft; b++) {{
            const bx = 92 + b * 76;
            cctx.fillStyle = col;
            cctx.beginPath(); cctx.roundRect(bx, 62, 62, 100, 12); cctx.fill();
          }}
          cctx.fillStyle = col;
          cctx.font = "900 54px Montserrat, sans-serif";
          cctx.fillText(pct + "%", 775, 132);

          if (barsLeft <= 3) {{
            for (let p = 0; p < 8; p++) {{
              const pt = (t * 1.9 + p * 0.13) % 1;
              const px = 220 + p * 55 + (p - 3.5) * 20 * pt;
              const py = 55 - 45 * pt + 150 * pt * pt;
              cctx.beginPath(); cctx.arc(px, py, 6.5, 0, Math.PI * 2);
              cctx.fillStyle = "#ef4444"; cctx.fill();
            }}
          }}
        }}
      }}
    }}, 0);

    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""
    sfx_cues = [
        ("sfx_whoosh_soft.mp3", max(0.1, hook_end + 0.08), 0.28),
        ("sfx_pop_clean.mp3", top_card_s + 0.04, 0.28),
        ("sfx_whoosh_transition.mp3", max(0.2, thread_t - 0.10), 0.28),
        ("sfx_ping_glass.mp3", kw_s + 0.05, 0.28),
    ]
    bgm = "bgm_warm_fretless.mp3" if is_dna else "bgm_sunny_carefree.mp3"
    return scene_html, bgm, sfx_cues
