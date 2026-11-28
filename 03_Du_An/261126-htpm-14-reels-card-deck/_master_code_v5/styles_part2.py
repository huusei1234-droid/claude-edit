# -*- coding: utf-8 -*-
"""
Part 2 of Bespoke Non-Occluding Talking-Head Styles (HyperFrames 1080x1920 @ 30fps):
STRICT RULE: 0% B-Roll or UI ever covers Chị Hằng ("không được để broll che mất chị mẫu")!
- STYLE 5 (v05, v14): Callaway HD2 Concentric `RingsBg` Halo Behind Chị Hằng + Top Twin Capsule B-Roll + Desk `Trim-Path` Lit Pills
- STYLE 6 (v06, v09): Minimal Premium Editorial (HD-CL) Top Ivory Polaroid Pair + Desk Dual-Curve Psychophysiological Graph + Serif Blur-Focus
- STYLE 7 (v07, v08, v11): Việt-Hàn × Kobe Framing Bento (Cells 01-02 Above Head + Cells 03-04 On Desk) + Frosted A9 Summary Bar
"""
import html
from styles_part1 import compute_safe_zones, hook_box_common_css_and_html, splice_cam_js


# ═══════════════════════════════════════════════════════════════════════════
# STYLE 5: CALLAWAY HD2 — RINGS HALO + TOP CAPSULE B-ROLL + DESK TRIM-PATH PILLS
# Chị Hằng stays 100% CENTERED & UNCROPPED (0% side panel covering her shoulder!)
# Used on Video #05 (<3 phút & Thuốc trôi nổi) & Video #14 (5 Thói quen giảm phong độ)
# ═══════════════════════════════════════════════════════════════════════════
def build_style5_callaway_split(sp, plan):
    dur = plan["dur"]
    hook_end = plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    top_y, top_h, kw_top, desk_y, desk_h = compute_safe_zones(plan)
    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    bkw1, bkw2 = [html.escape(x) for x in sp["behind_kw_lines"]]
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    h_css, h_html, h_js = hook_box_common_css_and_html(hl1, hl2, hl3, hook_end)

    is_5habits = (sp["idx"] == 14)
    sp_s = round(hook_end + 0.10, 2)
    top_card_s = round(kw_e + 0.22, 2) if (not is_5habits and kw_s < hook_end + 4.5) else round(hook_end + 0.14, 2)
    img_h = max(168, top_h - 84)

    if not is_5habits:
        items = [
            ("01", "HỒI HỘP TẠM THỜI ≠ MẮC BỆNH", "#38bdf8", sp_s + 0.20),
            ("02", "LẶP LẠI LIÊN TỤC → KHÁM CHUYÊN KHOA", "#fbbf24", max(sp_s + 1.8, 8.15)),
            ("03", "✕ TUYỆT ĐỐI CẤM TỰ MUA THUỐC TRÔI NỔI", "#ef4444", max(sp_s + 3.4, 12.15)),
        ]
        grid_css = "display: flex; flex-direction: column; gap: 14px; padding-left: 28px;"
        pill_pad = "16px 22px"
        txt_sz = "32px"
    else:
        # Exact spoken cue starts for 5 habits in v14: 1@2.76, 2@4.14, 3@6.62, 4@8.36, 5@10.62
        items = [
            ("01", "THỨC KHUYA LIÊN TỤC", "#f87171", 3.12),
            ("02", "LẠM DỤNG RƯỢU BIA", "#fb923c", 4.20),
            ("03", "HÚT THUỐC HẠI MẠCH MÁU", "#facc15", 6.62),
            ("04", "NGỒI LÌ ÍT VẬN ĐỘNG", "#38bdf8", 8.38),
            ("05", "CĂNG THẲNG KÉO DÀI — ĐỔI SỚM!", "#c084fc", 10.62),
        ]
        grid_css = "display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding-left: 24px;"
        pill_pad = "14px 18px"
        txt_sz = "27px"

    rows_html, rows_js = [], []
    for idx_i, (num, label, col, it_s) in enumerate(items, 1):
        span_col = 'grid-column: 1 / -1;' if (is_5habits and idx_i == 5) else ''
        rows_html.append(f"""
        <div id="cw-row-{idx_i}" class="cw-pill-row" style="border-color:{col}; {span_col}">
          <div id="cw-tri-{idx_i}" class="cw-tri" style="color:{col}">▶</div>
          <div class="cw-num" style="background:{col}">{num}</div>
          <div class="cw-txt">{label}</div>
        </div>""")
        rows_js.append(f"""
    tl.fromTo("#cw-row-{idx_i}", {{ x: 90, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.26, ease: "back.out(1.6)", immediateRender: false }}, {it_s:.2f});
    tl.fromTo("#cw-tri-{idx_i}", {{ scale: 0, rotation: 90 }}, {{ scale: 1, rotation: 0, duration: 0.28, ease: "back.out(2.0)" }}, {it_s + 0.04:.2f});""")

    kw_anim = ""
    if not is_5habits:
        kw_anim = f"""
    tl.fromTo("#cw-behind-kw", {{ scale: 1.24, opacity: 0 }}, {{ scale: 1.0, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#cw-behind-kw", {{ y: -20, opacity: 0, duration: 0.18 }}, {kw_e - 0.18:.2f});"""

    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "Asap"; src: url("assets/fonts/AsapCondensed-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #070b14; }}
    #cam-rig {{ position: absolute; inset: 0; transform-origin: 540px 780px; will-change: transform; }}
    #vid-bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}

    /* A11 RingsBg Halo strictly BEHIND Chị Hằng's RVM Cutout! */
    #rings-halo {{ position: absolute; inset: 0; z-index: 3; opacity: 0; pointer-events: none; }}
    .r-circle {{
      position: absolute; border-radius: 50%;
      border: 3.5px dashed rgba(56, 189, 248, 0.46);
      box-shadow: 0 0 26px rgba(56, 189, 248, 0.20);
    }}

    #cw-behind-kw {{
      position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; z-index: 6; opacity: 0; pointer-events: none;
    }}
    .cw-k1 {{ font-family: "Asap", sans-serif; font-size: 106px; line-height: 1.0; color: #ffe600; -webkit-text-stroke: 8px #0f172a; paint-order: stroke fill; }}
    .cw-k2 {{ font-family: "Asap", sans-serif; font-size: 96px; line-height: 1.02; color: #ffffff; -webkit-text-stroke: 8px #dc2626; paint-order: stroke fill; }}
    #vid-fg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 16; pointer-events: none; }}

    /* Top Callaway Twin Capsule B-Roll (strictly Y = {top_y}..{top_y + top_h}px ABOVE head!) */
    #cw-top-capsules {{
      position: absolute; left: 32px; top: {top_y}px; width: 1016px; height: {top_h}px;
      display: flex; gap: 22px; z-index: 12; pointer-events: none;
    }}
    .cw-cap-card {{
      flex: 1; height: {top_h}px; border-radius: 34px; overflow: hidden;
      background: #0f172a; border: 4px solid #38bdf8;
      box-shadow: 0 16px 38px rgba(0,0,0,0.38);
      display: flex; flex-direction: column; justify-content: space-between; opacity: 0;
    }}
    .cw-cap-card.green-c {{ border-color: #10b981; }}
    .cw-cap-card img {{ width: 100%; height: {img_h}px; object-fit: cover; }}
    .cw-cap-lbl {{
      flex: 1; display: flex; align-items: center; justify-content: center; text-align: center;
      font-family: "Asap", sans-serif; font-size: 27px; color: #ffffff; padding: 4px 12px;
    }}

    /* Desk Callaway Trim-Path Lit Pills (strictly Y = {desk_y}..{desk_y + desk_h}px on blank white desk!) */
    #callaway-desk-box {{
      position: absolute; left: 40px; top: {desk_y}px; width: 1000px; height: {desk_h}px;
      border-radius: 34px; background: linear-gradient(180deg, rgba(10, 18, 34, 0.95) 0%, rgba(7, 13, 24, 0.97) 100%);
      border: 3.5px solid #38bdf8; box-shadow: 0 20px 46px rgba(0,0,0,0.42);
      padding: 20px 26px; display: flex; flex-direction: column; justify-content: center;
      z-index: 20; opacity: 0; pointer-events: none;
    }}
    #cw-list-wrap {{ position: relative; {grid_css} }}
    #cw-trim-line {{
      position: absolute; left: 4px; top: 8px; width: 6px; height: 92%;
      background: linear-gradient(180deg, #38bdf8, #ef4444); border-radius: 4px;
      transform-origin: top center;
    }}
    .cw-pill-row {{
      display: flex; align-items: center; gap: 12px; padding: {pill_pad};
      border-radius: 22px; background: rgba(255,255,255,0.09); border: 3px solid #38bdf8;
      opacity: 0;
    }}
    .cw-tri {{ font-size: 22px; font-weight: 900; flex-shrink: 0; }}
    .cw-num {{
      width: 44px; height: 44px; border-radius: 12px; color: #090d16;
      font-family: "Montserrat", sans-serif; font-size: 22px;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }}
    .cw-txt {{ font-family: "Asap", sans-serif; font-size: {txt_sz}; line-height: 1.10; color: #ffffff; }}
    {h_css}
  </style>

  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <div id="cam-rig" data-layout-allow-overflow>
      <video id="vid-bg" class="clip" src="assets/videos/presenter.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="1" playsinline data-has-audio="true" data-volume="1.34"></video>
      <div id="rings-halo" data-layout-ignore>
        <div id="rc-1" class="r-circle" style="left:110px; top:420px; width:860px; height:860px"></div>
        <div id="rc-2" class="r-circle" style="left:220px; top:530px; width:640px; height:640px; border-color:rgba(250,204,21,0.42)"></div>
      </div>
      <div id="cw-behind-kw" data-layout-ignore>
        <div class="cw-k1">{bkw1}</div>
        <div class="cw-k2">{bkw2}</div>
      </div>
      <video id="vid-fg" class="clip" src="assets/videos/presenter_cutout.webm" data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
    </div>

    <div id="cw-top-capsules" data-layout-ignore>
      <div id="cw-c1" class="cw-cap-card">
        <img src="assets/images/broll_01.jpg" alt="Top 1" />
        <div class="cw-cap-lbl">{html.escape(c1['head'])}</div>
      </div>
      <div id="cw-c2" class="cw-cap-card green-c">
        <img src="assets/images/broll_02.jpg" alt="Top 2" />
        <div class="cw-cap-lbl">{html.escape(c2['head'])}</div>
      </div>
    </div>

    <div id="callaway-desk-box" data-layout-ignore>
      <div id="cw-list-wrap">
        <div id="cw-trim-line"></div>
        {chr(10).join(rows_html)}
      </div>
    </div>

    {h_html}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    {h_js}
{splice_cam_js(plan)}
    tl.to("#rings-halo", {{ opacity: 0.9, duration: 0.45 }}, {sp_s:.2f});
    tl.to("#rc-1", {{ rotation: 180, duration: {dur:.2f}, ease: "none" }}, 0);
    tl.to("#rc-2", {{ rotation: -180, duration: {dur:.2f}, ease: "none" }}, 0);
    {kw_anim}

    tl.fromTo("#cw-c1", {{ y: -80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.30, ease: "back.out(1.6)", immediateRender: false }}, {top_card_s:.2f});
    tl.fromTo("#cw-c2", {{ y: -80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.30, ease: "back.out(1.6)", immediateRender: false }}, {top_card_s + 0.35:.2f});

    tl.fromTo("#callaway-desk-box", {{ y: 80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.32, ease: "power3.out", immediateRender: false }}, {sp_s:.2f});
    tl.fromTo("#cw-trim-line", {{ scaleY: 0 }}, {{ scaleY: 1, duration: {max(2.5, dur - sp_s - 1.5):.2f}, ease: "none" }}, {sp_s + 0.15:.2f});
    {chr(10).join(rows_js)}

    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""
    sfx_cues = [
        ("sfx_whoosh_transition.mp3", max(0.1, sp_s - 0.06), 0.28),
        ("sfx_pop_clean.mp3", items[0][3], 0.28),
        ("sfx_pop_clean.mp3", items[1][3], 0.28),
        ("sfx_pop_clean.mp3", items[2][3], 0.30),
        ("sfx_chime_warm.mp3", items[-1][3], 0.26),
    ]
    bgm = "bgm_coconut_groove_tvc.mp3" if not is_5habits else "bgm_bright_riley.mp3"
    return scene_html, bgm, sfx_cues


# ═══════════════════════════════════════════════════════════════════════════
# STYLE 6: MINIMAL PREMIUM EDITORIAL (HD-CL) — TOP POLAROID PAIR + DESK GRAPH
# Chị Hằng stays 100% VISIBLE & UNCOVERED in the center (0% full-screen paper wall!)
# Used on Video #06 (Muốn gần vợ cương không nổi) & Video #09 (Thương vợ ít gần gũi)
# ═══════════════════════════════════════════════════════════════════════════
def build_style6_minimal_editorial(sp, plan):
    dur = plan["dur"]
    hook_end = plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    top_y, top_h, kw_top, desk_y, desk_h = compute_safe_zones(plan)
    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    bkw1, bkw2 = [html.escape(x) for x in sp["behind_kw_lines"]]
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    h_css, h_html, h_js = hook_box_common_css_and_html(hl1, hl2, hl3, hook_end)

    ed_s = round(min(dur - 4.2, kw_e + 0.24), 2)
    ed_e = round(min(dur - 0.25, ed_s + 4.80), 2)
    img_h = max(168, top_h - 80)

    # Subtitles ONLY appear outside [kw_s..kw_e] AND outside [ed_s..ed_e] (when Desk Chart is active)!
    active_pills = [
        p for p in plan["pills"]
        if not (p["s"] < ed_e - 0.05 and p["e"] > ed_s + 0.05)
    ]
    cap_divs, cap_js = [], []
    for i, p in enumerate(active_pills, 1):
        txt = p["html"].replace('<span class="hl-yellow">', '<span class="ed-serif-em">')
        cap_divs.append(f'<div id="edc-{i}" class="ed-cap-card" data-layout-ignore>{txt}</div>')
        cap_js.append(f'{{ id: "#edc-{i}", s: {p["s"]:.2f}, e: {p["e"]:.2f} }}')

    line1_lbl = "❤ TÌNH CẢM VỢ CHỒNG (Đong đầy)" if sp["idx"] == 6 else "📈 ÁP LỰC & MẤT NGỦ (Tăng cao)"
    line2_lbl = "⚡ MẠCH MÁU CƯƠNG (Tạm giảm)" if sp["idx"] == 6 else "📉 NỘI TIẾT HAM MUỐN (Suy giảm)"

    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "BeVN"; src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
    @font-face {{ font-family: "BeVNExtra"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #faf8f4; }}
    #cam-rig {{ position: absolute; inset: 0; transform-origin: 540px 780px; will-change: transform; }}
    #vid-bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}

    #ed-behind-wrap {{
      position: absolute; left: 36px; top: {kw_top}px; width: 1008px; text-align: center;
      z-index: 6; opacity: 0; pointer-events: none;
    }}
    .ed-k-serif {{
      font-family: Georgia, "Times New Roman", serif; font-weight: 700; font-style: italic;
      font-size: 92px; line-height: 1.04; color: #111827;
      -webkit-text-stroke: 10px #ffffff; paint-order: stroke fill;
      filter: drop-shadow(0 10px 24px rgba(17,24,39,0.22));
    }}
    #vid-fg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 16; pointer-events: none; }}

    /* Top Warm Ivory Paper Photo Pair (strictly Y = {top_y}..{top_y + top_h}px ABOVE head!) */
    #ed-top-photos {{
      position: absolute; left: 32px; top: {top_y}px; width: 1016px; height: {top_h}px;
      display: flex; gap: 22px; z-index: 12; pointer-events: none;
    }}
    .ed-pframe {{
      flex: 1; height: {top_h}px; border-radius: 28px; background: #fcfaf5;
      border: 5px solid #ffffff; box-shadow: 0 18px 40px rgba(17,24,39,0.18);
      overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; opacity: 0;
    }}
    .ed-pframe img {{ width: 100%; height: {img_h}px; object-fit: cover; }}
    .ed-pcap {{
      flex: 1; display: flex; align-items: center; justify-content: center; text-align: center;
      font-family: "BeVNExtra", sans-serif; font-size: 24px; color: #1e293b; padding: 4px 12px;
    }}

    /* Desk Warm Ivory Psychophysiological Dual-Curve Chart (strictly Y = {desk_y}..{desk_y + desk_h}px!) */
    #ed-desk-chart {{
      position: absolute; left: 42px; top: {desk_y}px; width: 996px; height: {desk_h}px;
      border-radius: 34px; background: #fcfaf5; border: 4px solid #e2dccf;
      box-shadow: 0 20px 46px rgba(17,24,39,0.22); padding: 18px 28px;
      display: flex; flex-direction: column; justify-content: space-between;
      z-index: 20; opacity: 0; pointer-events: none;
    }}
    .ed-chart-title {{ font-family: "BeVNExtra", sans-serif; font-size: 27px; color: #0f172a; text-align: center; }}
    .ed-legend {{ display: flex; justify-content: space-around; gap: 16px; }}
    .ed-leg-item {{ font-family: "BeVNExtra", sans-serif; font-size: 23px; }}

    .ed-cap-card {{
      position: absolute; left: 70px; top: {desk_y + 42}px; width: 940px; padding: 20px 30px;
      border-radius: 28px; background: rgba(252, 250, 245, 0.96); border: 3px solid #cbd5e1;
      box-shadow: 0 16px 38px rgba(15,23,42,0.18); text-align: center;
      font-family: "BeVN", sans-serif; font-size: 42px; line-height: 1.20; color: #0f172a;
      z-index: 21; opacity: 0; pointer-events: none;
    }}
    .ed-serif-em {{ font-family: Georgia, serif; font-style: italic; font-weight: 700; color: #2563eb; }}
    {h_css}
  </style>

  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <div id="cam-rig" data-layout-allow-overflow>
      <video id="vid-bg" class="clip" src="assets/videos/presenter.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="1" playsinline data-has-audio="true" data-volume="1.34"></video>
      <div id="ed-behind-wrap" data-layout-ignore>
        <div class="ed-k-serif"><div>{bkw1}</div><div>{bkw2}</div></div>
      </div>
      <video id="vid-fg" class="clip" src="assets/videos/presenter_cutout.webm" data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
    </div>

    <div id="ed-top-photos" data-layout-ignore>
      <div id="ed-p1" class="ed-pframe">
        <img src="assets/images/broll_01.jpg" alt="Couple" />
        <div class="ed-pcap">{html.escape(c1['head'])}</div>
      </div>
      <div id="ed-p2" class="ed-pframe">
        <img src="assets/images/broll_02.jpg" alt="Doctor" />
        <div class="ed-pcap">{html.escape(c2['head'])}</div>
      </div>
    </div>

    <div id="ed-desk-chart" data-layout-ignore>
      <div class="ed-chart-title">BIỂU ĐỒ TÂM SINH LÝ NAM GIỚI</div>
      <svg viewBox="0 0 920 205" width="940" height="205">
        <line x1="40" y1="185" x2="890" y2="185" stroke="#cbd5e1" stroke-width="3" />
        <line x1="40" y1="20" x2="40" y2="185" stroke="#cbd5e1" stroke-width="3" />
        <path id="curve-rose" d="M 55 155 Q 420 50 875 34" fill="none" stroke="#e11d48" stroke-width="14" stroke-linecap="round" stroke-dasharray="950" stroke-dashoffset="950" />
        <path id="curve-cobalt" d="M 55 58 Q 430 90 875 168" fill="none" stroke="#2563eb" stroke-width="14" stroke-linecap="round" stroke-dasharray="950" stroke-dashoffset="950" />
      </svg>
      <div class="ed-legend">
        <span class="ed-leg-item" style="color:#e11d48">{line1_lbl}</span>
        <span class="ed-leg-item" style="color:#2563eb">{line2_lbl}</span>
      </div>
    </div>

    {chr(10).join(cap_divs)}
    {h_html}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    {h_js}
{splice_cam_js(plan)}
    tl.fromTo("#ed-behind-wrap",
      {{ y: 22, filter: "blur(16px)", opacity: 0 }},
      {{ y: 0, filter: "blur(0px)", opacity: 1, duration: 0.24, ease: "power3.out", immediateRender: false }},
      {kw_s:.2f}
    );
    tl.to("#ed-behind-wrap", {{ filter: "blur(12px)", opacity: 0, duration: 0.16 }}, {kw_e - 0.16:.2f});

    // Top Polaroid Pair + Desk Dual-Curve Chart ({ed_s:.2f}s -> {ed_e:.2f}s) — Chị Hằng 100% visible in center!
    tl.fromTo("#ed-p1", {{ y: -70, rotation: -4, opacity: 0 }}, {{ y: 0, rotation: -1.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {ed_s:.2f});
    tl.fromTo("#ed-p2", {{ y: -70, rotation: 4, opacity: 0 }}, {{ y: 0, rotation: 1.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {ed_s + 0.22:.2f});
    tl.fromTo("#ed-desk-chart", {{ y: 70, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.34, ease: "power3.out", immediateRender: false }}, {ed_s + 0.10:.2f});
    tl.to("#curve-rose", {{ strokeDashoffset: 0, duration: 1.35, ease: "power2.out" }}, {ed_s + 0.32:.2f});
    tl.to("#curve-cobalt", {{ strokeDashoffset: 0, duration: 1.45, ease: "power2.out" }}, {ed_s + 0.56:.2f});
    tl.to(["#ed-p1", "#ed-p2", "#ed-desk-chart"], {{ opacity: 0, duration: 0.24 }}, {ed_e - 0.24:.2f});

    const edCues = [{", ".join(cap_js)}];
    for (const c of edCues) {{
      tl.fromTo(c.id,
        {{ y: 18, filter: "blur(14px)", opacity: 0 }},
        {{ y: 0, filter: "blur(0px)", opacity: 1, duration: 0.18, ease: "power3.out", immediateRender: false }},
        c.s
      );
      tl.to(c.id, {{ filter: "blur(10px)", opacity: 0, duration: 0.10 }}, c.e - 0.10);
    }}

    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""
    sfx_cues = [
        ("sfx_click_soft.mp3", kw_s, 0.28),
        ("sfx_whoosh_soft.mp3", max(0.2, ed_s - 0.06), 0.28),
        ("sfx_chime_warm.mp3", ed_s + 0.40, 0.24),
    ]
    return scene_html, "bgm_warm_fretless.mp3", sfx_cues


# ═══════════════════════════════════════════════════════════════════════════
# STYLE 7: VIỆT-HÀN × KOBE FRAMING BENTO (TOP 01-02 + DESK 03-04) + SUMMARY BAR
# Chị Hằng sits LIVE & 100% UNCOVERED right in the center between Top & Desk Bento!
# Used on Video #07 (Tự xử sợ teo), Video #08 (Ăn tỏi), & Video #11 (4 Tác hại phim)
# ═══════════════════════════════════════════════════════════════════════════
def build_style7_medical_bento(sp, plan):
    dur = plan["dur"]
    hook_end = plan["hook_end"]
    top_y, top_h, _, desk_y, desk_h = compute_safe_zones(plan)
    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    bkw1, bkw2 = [html.escape(x) for x in sp["behind_kw_lines"]]
    h_css, h_html, h_js = hook_box_common_css_and_html(hl1, hl2, hl3, hook_end)

    bt_s = round(hook_end + 0.10, 2)
    bt_e = round(dur - 2.15, 2)
    span = max(3.2, bt_e - bt_s)

    if sp["idx"] == 7:
        cells = [
            ("01", "LÚC CƯƠNG", "Máu dồn đầy thể hang", "#fff1f2", "#e11d48", "assets/images/broll_hook.jpg"),
            ("02", "SAU XUẤT TINH", "Máu rút về nghỉ ngơi", "#eff6ff", "#2563eb", "assets/images/broll_01.jpg"),
            ("03", "0% MẤT KÍCH THƯỚC", "Không hề bị teo đi!", "#ecfdf5", "#059669", ""),
            ("04", "KHI NÀO ĐI KHÁM?", "Chỉ khi đau / tổn thương", "#fef3c7", "#d97706", "assets/images/broll_02.jpg"),
        ]
    elif sp["idx"] == 8:
        cells = [
            ("01", "TỎI ĐƠN LẺ", "Chỉ hỗ trợ nhẹ tuần hoàn", "#fff1f2", "#e11d48", "assets/images/broll_hook.jpg"),
            ("02", "ĂN LÀNH MẠNH", "Đủ kẽm, đạm & rau xanh", "#fef3c7", "#d97706", "assets/images/broll_01.jpg"),
            ("03", "TẬP & NGỦ ĐỦ", "Tăng sức bền mạch máu", "#eff6ff", "#2563eb", "assets/images/broll_02.jpg"),
            ("04", "KHÁM TOÀN DIỆN", "Xử lý đúng gốc rối loạn", "#ecfdf5", "#059669", ""),
        ]
    else:
        cells = [
            ("01", "THỨC KHUYA", "Tốn thời gian & suy nhược", "#fff1f2", "#e11d48", "assets/images/broll_hook.jpg"),
            ("02", "RỐI LOẠN CƯƠNG", "Phản xạ thất thường", "#fef2f2", "#dc2626", "assets/images/broll_01.jpg"),
            ("03", "TRƠ CẢM XÚC", "Giảm lửa khi gần vợ thật", "#fff7ed", "#ea580c", ""),
            ("04", "KHÓ XUẤT TINH", "Xuất muộn / mất khoái cảm", "#f0fdf4", "#059669", "assets/images/broll_02.jpg"),
        ]

    top_img_h = max(135, top_h - 116)
    desk_img_h = max(165, desk_h - 122)
    step_b = (span - 0.3) / 4.0

    def render_cell(idx_c, cell, media_h):
        num, title, sub, bg_c, bd_c, img_src = cell
        media_el = (
            f'<img src="{img_src}" class="bt-img" alt="{title}" />'
            if img_src
            else f'<div class="bt-big-badge" style="color:{bd_c}">{num}</div>'
        )
        return f"""
        <div id="bt-cell-{idx_c}" class="bento-cell" style="background:{bg_c}; border-color:{bd_c}">
          <div class="bt-top">
            <span class="bt-num" style="background:{bd_c}">{num}</span>
            <span class="bt-title" style="color:{bd_c}">{title}</span>
          </div>
          <div class="bt-media" style="height:{media_h}px">{media_el}</div>
          <div class="bt-sub">{sub}</div>
        </div>"""

    top_cells_html = render_cell(1, cells[0], top_img_h) + render_cell(2, cells[1], top_img_h)
    desk_cells_html = render_cell(3, cells[2], desk_img_h) + render_cell(4, cells[3], desk_img_h)

    bento_js = []
    for i in range(1, 5):
        cs = round(bt_s + (i - 1) * step_b, 2)
        dy = -50 if i <= 2 else 60
        bento_js.append(
            f'tl.fromTo("#bt-cell-{i}", {{ scale: 0.84, y: {dy}, opacity: 0 }}, '
            f'{{ scale: 1.0, y: 0, opacity: 1, duration: 0.28, ease: "back.out(1.7)", immediateRender: false }}, {cs:.2f});'
        )

    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "Asap"; src: url("assets/fonts/AsapCondensed-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "BeVN"; src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #f8fafc; }}
    #cam-rig {{ position: absolute; inset: 0; transform-origin: 540px 780px; will-change: transform; }}
    #vid-bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    #vid-fg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 16; pointer-events: none; }}

    /* Top Bento Row (Cells 01 & 02 strictly ABOVE Chị Hằng's head: Y = {top_y}..{top_y + top_h}px!) */
    #bento-top-row {{
      position: absolute; left: 32px; top: {top_y}px; width: 1016px; height: {top_h}px;
      display: grid; grid-template-columns: 1fr 1fr; gap: 18px; z-index: 12; pointer-events: none;
    }}
    /* Bottom Bento Row (Cells 03 & 04 strictly ON blank white desk: Y = {desk_y}..{desk_y + desk_h}px!) */
    #bento-desk-row {{
      position: absolute; left: 32px; top: {desk_y}px; width: 1016px; height: {desk_h}px;
      display: grid; grid-template-columns: 1fr 1fr; gap: 18px; z-index: 20; pointer-events: none;
    }}
    .bento-cell {{
      border-radius: 28px; border: 4px solid #cbd5e1; padding: 12px 16px;
      display: flex; flex-direction: column; justify-content: space-between;
      box-shadow: 0 16px 36px rgba(15,23,42,0.18); opacity: 0; overflow: hidden;
    }}
    .bt-top {{ display: flex; align-items: center; gap: 10px; }}
    .bt-num {{
      width: 44px; height: 44px; border-radius: 12px; color: #ffffff;
      font-family: "Montserrat", sans-serif; font-size: 22px;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }}
    .bt-title {{ font-family: "Asap", sans-serif; font-size: 30px; line-height: 1.05; text-transform: uppercase; }}
    .bt-media {{ width: 100%; border-radius: 18px; overflow: hidden; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.8); }}
    .bt-img {{ width: 100%; height: 100%; object-fit: cover; }}
    .bt-big-badge {{ font-family: "Montserrat", sans-serif; font-size: 92px; }}
    .bt-sub {{ font-family: "BeVN", sans-serif; font-size: 22px; line-height: 1.18; color: #1e293b; text-align: center; }}

    /* A9 T.logoBar Frosted Glass Summary Bar on Closing Desk */
    #glass-summary-bar {{
      position: absolute; left: 60px; top: {desk_y + 52}px; width: 960px; height: 210px;
      border-radius: 46px; background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(12px);
      border: 4px solid #ffe600; box-shadow: 0 22px 48px rgba(0,0,0,0.38);
      padding: 20px 36px; display: flex; align-items: center; justify-content: center;
      text-align: center; font-family: "Montserrat", sans-serif; font-size: 38px; line-height: 1.24;
      color: #ffffff; z-index: 24; transform: translateX(1060px); pointer-events: none;
    }}
    {h_css}
  </style>

  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <div id="cam-rig" data-layout-allow-overflow>
      <video id="vid-bg" class="clip" src="assets/videos/presenter.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="1" playsinline data-has-audio="true" data-volume="1.34"></video>
      <video id="vid-fg" class="clip" src="assets/videos/presenter_cutout.webm" data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
    </div>

    <div id="bento-top-row" data-layout-ignore>{top_cells_html}</div>
    <div id="bento-desk-row" data-layout-ignore>{desk_cells_html}</div>
    <div id="glass-summary-bar" data-layout-ignore>{bkw1} — {bkw2}</div>
    {h_html}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    {h_js}
{splice_cam_js(plan)}
    {chr(10).join(bento_js)}

    // Fold Bottom Bento Cells & Slide in A9 Frosted Glass Summary Bar on Desk ({bt_e:.2f}s)!
    tl.to(["#bt-cell-3", "#bt-cell-4"], {{ y: 50, opacity: 0, duration: 0.22, ease: "power2.in" }}, {bt_e:.2f});
    tl.to("#glass-summary-bar", {{ x: 0, duration: 0.34, ease: "back.out(1.4)" }}, {bt_e + 0.16:.2f});

    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""
    sfx_cues = [
        ("sfx_pop_clean.mp3", bt_s + 0.04, 0.28),
        ("sfx_pop_clean.mp3", bt_s + step_b, 0.28),
        ("sfx_pop_clean.mp3", bt_s + step_b * 2, 0.30),
        ("sfx_pop_clean.mp3", bt_s + step_b * 3, 0.30),
        ("sfx_whoosh_transition.mp3", bt_e + 0.12, 0.28),
    ]
    bgm = "bgm_sunny_carefree.mp3" if sp["idx"] == 7 else ("bgm_fresh_wellness_tvc.mp3" if sp["idx"] == 8 else "bgm_coconut_groove_tvc.mp3")
    return scene_html, bgm, sfx_cues
