# -*- coding: utf-8 -*-
"""
Bespoke Behind-Subject Hologram & Card-Deck Builders (#01 -> #07)
Modeled directly on the 14 original hanh.sung.suong reference reels + Studio Talking-Head FX:
1. 0px vertical/horizontal presenter movement ("đừng có kéo mẫu lên xuống nữa").
2. 100% of ALL B-Roll cards, 3D holograms, canvases & behind-head keywords sit at z-index 6
   STRICTLY BEHIND `#vid-fg` (`presenter_cutout.webm` at z-index 20) -> 0% B-Roll ever covers Chị Hằng!
3. 0% BGM ("không cần nhạc nền luôn") — pure studio voice + subtle tactile micro-SFX.
4. Every video (#01 -> #07) has a unique visual mechanism matched to its topic & reference reel.
"""
import html


def common_base_css(sub_mode: str = "yellow_black"):
    """
    sub_mode:
      - 'yellow_black': #fff200 fill + thick #090d16 stroke (cf. reel_01, 04, 05, 06, 07)
      - 'white_red':    #ffffff fill + thick #b91c1c stroke (cf. reel_02, 03, 11, 12, 13)
      - 'mint_italic':  BarlowItalic #5cf7e0 + #ffe600 accent + Stroke-Up ghost (Style THv3)
      - 'white_black':  #ffffff fill + thick #090d16 stroke (cf. reel_14)
    """
    if sub_mode == "white_red":
        sub_css = """
        .sub-cue {
          position: absolute; left: 54px; top: 1288px; width: 972px; text-align: center;
          font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 50px; line-height: 1.20;
          color: #ffffff; -webkit-text-stroke: 11px #b91c1c; paint-order: stroke fill;
          filter: drop-shadow(0 6px 14px rgba(0,0,0,0.38));
          z-index: 25; opacity: 0; pointer-events: none;
        }
        .sub-cue .hl-yellow { color: #fff799; }
        """
    elif sub_mode == "mint_italic":
        sub_css = """
        .sub-cue {
          position: absolute; left: 54px; top: 1288px; width: 972px; text-align: center;
          font-family: "BarlowItalic", sans-serif; font-weight: 900; font-style: italic; font-size: 64px; line-height: 1.12;
          color: #5cf7e0; -webkit-text-stroke: 10px #08121e; paint-order: stroke fill;
          filter: drop-shadow(0 6px 16px rgba(0,0,0,0.45));
          z-index: 25; opacity: 0; pointer-events: none;
        }
        .sub-cue .hl-yellow { color: #ffe600; }
        """
    elif sub_mode == "white_black":
        sub_css = """
        .sub-cue {
          position: absolute; left: 54px; top: 1288px; width: 972px; text-align: center;
          font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 50px; line-height: 1.20;
          color: #ffffff; -webkit-text-stroke: 11px #090d16; paint-order: stroke fill;
          filter: drop-shadow(0 6px 14px rgba(0,0,0,0.42));
          z-index: 25; opacity: 0; pointer-events: none;
        }
        .sub-cue .hl-yellow { color: #ffe600; }
        """
    else:
        sub_css = """
        .sub-cue {
          position: absolute; left: 54px; top: 1288px; width: 972px; text-align: center;
          font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 50px; line-height: 1.20;
          color: #fff200; -webkit-text-stroke: 11px #090d16; paint-order: stroke fill;
          filter: drop-shadow(0 6px 14px rgba(0,0,0,0.40));
          z-index: 25; opacity: 0; pointer-events: none;
        }
        .sub-cue .hl-yellow { color: #ffffff; }
        """

    return f"""
    @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }}
    @font-face {{ font-family: "BarlowItalic"; src: url("assets/fonts/BarlowCondensed-BlackItalic.ttf") format("truetype"); font-weight: 900; font-style: italic; font-display: block; }}
    @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "Asap"; src: url("assets/fonts/AsapCondensed-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "BeVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}

    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: #f5f2eb; }}
    /* Chị Hằng Base Studio (z-index 1) + Foreground RVM Cutout (z-index 20) — 100% UNSHIFTED & STATIONARY! */
    #vid-bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    #behind-stage {{ position: absolute; inset: 0; z-index: 6; pointer-events: none; perspective: 1100px; }}
    #vid-fg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 20; pointer-events: none; }}

    /* Opening 3s Yellow Hook Box (exact match to image 1 & reel_01..14@1.2s) */
    #hook-slot {{ position: absolute; left: 96px; top: 1158px; width: 888px; height: 342px; z-index: 28; }}
    #hook-yellow-box {{
      position: relative; width: 100%; height: 100%;
      background: linear-gradient(180deg, #ffe800 0%, #ffd200 100%);
      border-radius: 48px;
      box-shadow: 0 22px 46px rgba(0,0,0,0.28);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      padding: 22px 28px; text-align: center; overflow: hidden;
    }}
    #hook-sheen {{
      position: absolute; top: -40%; left: -35%; width: 45%; height: 180%;
      background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.58) 50%, rgba(255,255,255,0) 100%);
      pointer-events: none;
    }}
    .hook-line {{
      font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 51px;
      line-height: 1.18; letter-spacing: -0.015em; color: #080808; text-transform: uppercase;
      position: relative; z-index: 2;
    }}

    /* Reusable Floating Behind-Shoulder Card Base (always inside #behind-stage at z-index 6 < vid-fg 20!) */
    .sh-card {{
      position: absolute; width: 392px; border-radius: 30px;
      background: rgba(255, 255, 255, 0.94); backdrop-filter: blur(10px);
      border: 4px solid #ffffff;
      box-shadow: 0 22px 48px rgba(15, 23, 42, 0.22);
      padding: 12px; display: flex; flex-direction: column; gap: 8px;
      opacity: 0; will-change: transform, opacity;
    }}
    .sh-card img {{ width: 100%; height: 246px; border-radius: 20px; object-fit: cover; display: block; }}
    .sh-badge {{
      align-self: flex-start; padding: 5px 14px; border-radius: 999px;
      font-family: "Montserrat", sans-serif; font-size: 17px; color: #ffffff; background: #0284c7;
    }}
    .sh-head {{ font-family: "BeVN", sans-serif; font-size: 26px; line-height: 1.14; color: #0f172a; text-transform: uppercase; }}
    .sh-desc {{ font-family: "BeVN", sans-serif; font-size: 20px; line-height: 1.20; color: #475569; }}
    {sub_css}
    """


_ACTIVE_TH_CTX = (None, None)


def render_hook_and_subs(sp, plan):
    global _ACTIVE_TH_CTX
    _ACTIVE_TH_CTX = (sp, plan)
    hl1, hl2, hl3 = [html.escape(x) for x in sp["hook_lines"]]
    hook_end = plan["hook_end"]
    out_t = round(max(0.8, hook_end - 0.22), 2)

    hook_html = f"""
    <div id="hook-slot" class="clip" data-start="0" data-duration="{hook_end:.2f}" data-layout-allow-caption-zone data-layout-allow-overflow>
      <div id="hook-yellow-box">
        <div id="hook-sheen" data-layout-ignore></div>
        <div class="hook-line">{hl1}</div>
        <div class="hook-line">{hl2}</div>
        <div class="hook-line">{hl3}</div>
      </div>
    </div>"""

    sub_divs, sub_js = [], []
    for i, p in enumerate(plan["pills"], 1):
        sub_divs.append(
            f'<div id="scue-{i}" class="sub-cue" data-layout-ignore>'
            f'<div class="sub-ghost">{p["html"]}</div>'
            f'<div class="sub-main">{p["html"]}</div>'
            f'</div>'
        )
        sub_js.append(f'{{ id: "#scue-{i}", s: {p["s"]:.2f}, e: {p["e"]:.2f} }}')

    common_js = f"""
    tl.fromTo("#hook-yellow-box", {{ scale: 0.84, y: 36, opacity: 0.92 }}, {{ scale: 1.02, y: -3, opacity: 1, duration: 0.22, ease: "back.out(1.7)" }}, 0);
    tl.to("#hook-yellow-box", {{ scale: 1.0, y: 0, duration: 0.14, ease: "power2.out" }}, 0.22);
    tl.fromTo("#hook-sheen", {{ x: -140, rotation: 18 }}, {{ x: 980, rotation: 18, duration: 0.62, ease: "power2.inOut" }}, 0.28);
    tl.to("#hook-yellow-box", {{ scale: 0.88, y: 30, opacity: 0, duration: 0.20, ease: "power2.in" }}, {out_t:.2f});

    // A5 + A6 Talking-Head Subtitles: Rise + Blur-Focus + Stroke-Up Expanding Outline Ghost!
    const subCues = [{", ".join(sub_js)}];
    for (const c of subCues) {{
      tl.set(c.id, {{ opacity: 1 }}, c.s);
      tl.fromTo(c.id + " .sub-main", {{ y: 26, filter: "blur(10px)", opacity: 0 }}, {{ y: 0, filter: "blur(0px)", opacity: 1, duration: 0.15, ease: "power3.out", immediateRender: false }}, c.s);
      tl.fromTo(c.id + " .sub-ghost", {{ scale: 1.0, opacity: 0.72 }}, {{ scale: 1.72, opacity: 0, duration: 0.32, ease: "power2.out", immediateRender: false }}, c.s + 0.04);
      tl.to(c.id, {{ opacity: 0, duration: 0.08 }}, c.e - 0.08);
    }}"""
    return hook_html + "\n" + "\n".join(sub_divs), common_js


KW_PALETTES = [
    ("Anton", "84px", "normal", "#dc2626", "#0f172a"),
    ("Asap", "86px", "normal", "#6d28d9", "#0284c7"),
    ("BarlowItalic", "88px", "italic", "#059669", "#d97706"),
    ("BeVN", "78px", "italic", "#be123c", "#1d4ed8"),
    ("Montserrat", "76px", "normal", "#0369a1", "#b91c1c"),
]

SUB_ROTATION = ["yellow_black", "white_red", "mint_italic", "white_black", "yellow_black", "white_red", "mint_italic"]


def wrap_stage_template(dur: float, css_extra: str, sub_mode: str, behind_html: str, fg_ui_html: str, anim_js: str):
    from th_fx_injector import get_th_fx_bundle
    sp_ctx, plan_ctx = _ACTIVE_TH_CTX
    th_css, th_backdrop, th_behind, th_js = get_th_fx_bundle(sp_ctx, plan_ctx) if sp_ctx else ("", "", "", "")

    if sp_ctx and plan_ctx:
        idx = sp_ctx["idx"]
        sub_mode = SUB_ROTATION[(idx - 1) % len(SUB_ROTATION)]
        hy = int(plan_ctx.get("head_top_y", 350))
        kw_s, kw_e = plan_ctx["kw_start"], plan_ctx["kw_end"]
        # Guarantee BOTH lines sit cleanly readable above Chị Hằng's hair crown even when hy=249px!
        kw_top_safe = max(14, hy - 186)
        kf, ksz, kst, kc1, kc2 = KW_PALETTES[(idx - 1) % len(KW_PALETTES)]
        kl1, kl2 = [html.escape(x) for x in sp_ctx["behind_kw_lines"]]
        master_kw_css = f"""
        #cards-substage [id$="-kw"] {{ display: none !important; }}
        #top-kw-master {{
          position: absolute; left: 24px; top: {kw_top_safe}px; width: 1032px; text-align: center;
          z-index: 8; opacity: 0; pointer-events: none;
        }}
        .tkm-l1 {{
          font-family: "{kf}", sans-serif; font-size: {ksz}; font-style: {kst}; font-weight: 900;
          line-height: 1.02; color: {kc1}; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill;
          filter: drop-shadow(0 8px 20px rgba(0,0,0,0.32)); text-transform: uppercase;
        }}
        .tkm-l2 {{
          font-family: "{kf}", sans-serif; font-size: {ksz}; font-style: {kst}; font-weight: 900;
          line-height: 1.03; color: {kc2}; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill;
          filter: drop-shadow(0 8px 20px rgba(0,0,0,0.32)); text-transform: uppercase;
        }}
        """
        master_kw_html = f'<div id="top-kw-master"><div class="tkm-l1">{kl1}</div><div class="tkm-l2">{kl2}</div></div>'
        master_kw_js = f"""
    tl.fromTo("#top-kw-master", {{ scale: 0.86, y: 20, opacity: 0 }}, {{ scale: 1.0, y: 0, opacity: 1, duration: 0.22, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#top-kw-master", {{ y: -18, opacity: 0, duration: 0.16, ease: "power2.in" }}, {kw_e - 0.16:.2f});
        """
    else:
        master_kw_css, master_kw_html, master_kw_js = "", "", ""

    return f"""<template>
  <style>
    {common_base_css(sub_mode)}
    {th_css}
    {css_extra}
    {master_kw_css}
  </style>
  <div id="root" data-composition-id="presenter-stage" data-width="1080" data-height="1920">
    <video id="vid-bg" class="clip" src="assets/videos/presenter.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="1" playsinline data-has-audio="true" data-volume="1.0"></video>
    {th_backdrop}
    <div id="behind-stage" data-layout-ignore>
      {th_behind}
      {master_kw_html}
      <div id="cards-substage">
        {behind_html}
      </div>
    </div>
    <video id="vid-fg" class="clip" src="assets/videos/presenter_cutout.webm" data-start="0" data-duration="{dur:.2f}" muted playsinline data-layout-allow-occlusion></video>
    {fg_ui_html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {th_js}
    {master_kw_js}
    {anim_js}
    window.__timelines["presenter-stage"] = tl;
  </script>
</template>
"""


# ═══════════════════════════════════════════════════════════════════════════
# #01: CẮT BAO QUY ĐẦU — Right AR Hourglass + 3-Card Medical Fan Behind Shoulders
# ═══════════════════════════════════════════════════════════════════════════
def build_v01(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 440))
    kw_top = max(38, hy - 142)
    sh_y = max(140, hy - 30)
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v01-ar-box {{
      position: absolute; right: 34px; top: {sh_y}px; width: 410px; height: 420px;
      border-radius: 34px; background: linear-gradient(155deg, rgba(8,47,73,0.90), rgba(14,116,144,0.82));
      border: 3px solid #67e8f9; box-shadow: 0 20px 46px rgba(8,47,73,0.32); opacity: 0; overflow: hidden;
    }}
    #v01-kw {{
      position: absolute; left: 30px; top: {kw_top}px; width: 1020px; text-align: center; opacity: 0;
    }}
    .v01-k1 {{ font-family: "Anton", sans-serif; font-size: 96px; line-height: 1.02; color: #ef4444; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; filter: drop-shadow(0 8px 20px rgba(0,0,0,0.28)); }}
    .v01-k2 {{ font-family: "Anton", sans-serif; font-size: 90px; line-height: 1.04; color: #0f172a; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <div id="v01-ar-box"><canvas id="v01-cvs" width="410" height="420"></canvas></div>
    <div id="v01-kw"><div class="v01-k1">KHÔNG PHẢI CÁCH</div><div class="v01-k2">TRỊ XUẤT SỚM!</div></div>
    <div id="v01-c1" class="sh-card" style="left: 28px; top: {sh_y + 10}px; border-color:#ef4444">
      <img src="assets/images/broll_01_surgical_no.jpg" alt="1" />
      <span class="sh-badge" style="background:#dc2626">✕ SAI MỤC ĐÍCH</span>
      <div class="sh-head">CẮT BAO QUY ĐẦU</div>
      <div class="sh-desc">Không trị xuất tinh sớm</div>
    </div>
    <div id="v01-c2" class="sh-card" style="right: 28px; top: {sh_y}px; border-color:#0284c7">
      <img src="assets/images/broll_02_doctor_consult.jpg" alt="2" />
      <span class="sh-badge">HỎI RÕ BÁC SĨ</span>
      <div class="sh-head">KHÁM ĐÚNG BÁC SĨ</div>
      <div class="sh-desc">Tìm đúng nguyên nhân</div>
    </div>
    <div id="v01-c3" class="sh-card" style="right: 28px; top: {sh_y + 16}px; border-color:#10b981">
      <img src="assets/images/broll_03_medical_reason.jpg" alt="3" />
      <span class="sh-badge" style="background:#059669">✔ ĐÚNG BỆNH LÝ</span>
      <div class="sh-head">CHỈ CẮT KHI BỆNH LÝ</div>
      <div class="sh-desc">Hẹp • Nghẹt • Viêm tái phát</div>
    </div>"""

    js = f"""
    {common_js}
    tl.fromTo("#v01-ar-box", {{ x: 120, scale: 0.85, opacity: 0 }}, {{ x: 0, scale: 1, opacity: 1, duration: 0.34, ease: "back.out(1.6)" }}, 0.15);
    tl.to("#v01-ar-box", {{ x: 100, opacity: 0, duration: 0.24 }}, {max(3.1, kw_s - 0.15):.2f});

    tl.fromTo("#v01-kw", {{ scale: 0.85, y: 24, opacity: 0 }}, {{ scale: 1, y: 0, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v01-kw", {{ y: -20, opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    const cStart = {kw_e + 0.18:.2f};
    tl.fromTo("#v01-c1", {{ x: -200, rotation: -12, opacity: 0 }}, {{ x: 0, rotation: -4, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, cStart);
    tl.fromTo("#v01-c2", {{ x: 200, rotation: 12, opacity: 0 }}, {{ x: 0, rotation: 4, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, cStart + 0.35);
    tl.to("#v01-c2", {{ x: 180, opacity: 0, duration: 0.22 }}, cStart + 2.60);
    tl.fromTo("#v01-c3", {{ x: 220, rotation: 10, opacity: 0 }}, {{ x: 0, rotation: 3.5, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, cStart + 2.75);

    const ctx1 = document.getElementById("v01-cvs").getContext("2d");
    const p1 = {{ t: 0 }};
    tl.to(p1, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p1.t;
        ctx1.clearRect(0, 0, 410, 420);
        // Glowing Hourglass + 02:00 Timer + Swimming Sperm
        ctx1.strokeStyle = "#67e8f9"; ctx1.lineWidth = 5;
        ctx1.beginPath(); ctx1.roundRect(115, 48, 180, 14, 7); ctx1.stroke();
        ctx1.beginPath(); ctx1.roundRect(115, 258, 180, 14, 7); ctx1.stroke();
        ctx1.beginPath(); ctx1.moveTo(135, 62); ctx1.lineTo(275, 258); ctx1.moveTo(275, 62); ctx1.lineTo(135, 258); ctx1.stroke();
        ctx1.fillStyle = "#ffe600"; ctx1.font = "900 42px Montserrat, sans-serif";
        ctx1.fillText("01:58", 142, 330);
        for (let i = 0; i < 4; i++) {{
          const sx = 80 + ((t * 95 + i * 85) % 270);
          const sy = 365 + (i % 2) * 26 + Math.sin(t * 6 + i) * 6;
          ctx1.fillStyle = "#a5f3fc"; ctx1.beginPath(); ctx1.ellipse(sx, sy, 11, 7, 0, 0, Math.PI * 2); ctx1.fill();
          ctx1.strokeStyle = "#67e8f9"; ctx1.lineWidth = 3;
          ctx1.beginPath(); ctx1.moveTo(sx - 10, sy); ctx1.quadraticCurveTo(sx - 28, sy + Math.sin(t * 18 + i) * 10, sx - 46, sy); ctx1.stroke();
        }}
      }}
    }}, 0);"""
    sfx = [("sfx_pop_clean.mp3", kw_s, 0.18), ("sfx_whoosh_soft.mp3", kw_e + 0.18, 0.16), ("sfx_pop_clean.mp3", kw_e + 0.55, 0.16)]
    return wrap_stage_template(dur, css, "yellow_black", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #02: QUAN HỆ NHIỀU CẠN TINH TRÙNG (cf. reel_02: Droplet/Sperm -> 3D Balance Scale -> Green Shield)
# ═══════════════════════════════════════════════════════════════════════════
def build_v02(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 440))
    kw_top = max(36, hy - 142)
    sh_y = max(130, hy - 40)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v02-sperm-screen {{
      position: absolute; right: 30px; top: {sh_y - 20}px; width: 450px; height: 390px;
      border-radius: 32px; background: linear-gradient(145deg, rgba(12,34,58,0.92), rgba(15,62,88,0.86));
      border: 3.5px solid #38bdf8; box-shadow: 0 20px 48px rgba(8,47,73,0.32); opacity: 0;
    }}
    #v02-scale-stage {{
      position: absolute; left: 34px; top: {sh_y - 30}px; width: 1012px; height: 470px;
      border-radius: 38px; background: rgba(255,255,255,0.68); backdrop-filter: blur(8px);
      border: 3px solid rgba(255,255,255,0.92); box-shadow: 0 20px 50px rgba(15,23,42,0.14);
      opacity: 0; overflow: hidden;
    }}
    #v02-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v02-k {{
      font-family: "Anton", sans-serif; font-size: 94px; line-height: 1.03;
      color: #7c3aed; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill;
      filter: drop-shadow(0 8px 20px rgba(0,0,0,0.22));
    }}
    """
    behind = f"""
    <div id="v02-sperm-screen"><canvas id="v02-drop-cvs" width="450" height="390"></canvas></div>
    <div id="v02-scale-stage"><canvas id="v02-scale-cvs" width="1012" height="470"></canvas></div>
    <div id="v02-kw"><div class="v02-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v02-k" style="color:#0284c7">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v02-lab-l" class="sh-card" style="left: 28px; top: {sh_y + 10}px; border-color:#0284c7">
      <img src="assets/images/broll_01.jpg" alt="Lab" />
      <span class="sh-badge">{html.escape(c1['tag'])}</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v02-lab-r" class="sh-card" style="right: 28px; top: {sh_y + 10}px; border-color:#10b981">
      <img src="assets/images/broll_02.jpg" alt="Doc" />
      <span class="sh-badge" style="background:#059669">{html.escape(c2['tag'])}</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    js = f"""
    {common_js}
    tl.fromTo("#v02-sperm-screen", {{ x: 140, scale: 0.85, opacity: 0 }}, {{ x: 0, scale: 1, opacity: 1, duration: 0.34, ease: "back.out(1.6)" }}, 0.12);
    tl.to("#v02-sperm-screen", {{ opacity: 0, y: -30, duration: 0.24 }}, {hook_end + 0.10:.2f});

    // Wide Frosted Balance Scale Stage behind both shoulders (3.4s -> kw_s)
    tl.fromTo("#v02-scale-stage", {{ scale: 0.90, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.34, ease: "power3.out", immediateRender: false }}, {hook_end + 0.16:.2f});
    tl.to("#v02-scale-stage", {{ opacity: 0, duration: 0.22 }}, {max(hook_end + 1.8, kw_s - 0.12):.2f});

    tl.fromTo("#v02-kw", {{ scale: 1.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v02-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    tl.fromTo("#v02-lab-l", {{ x: -180, rotation: -8, opacity: 0 }}, {{ x: 0, rotation: -3.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {kw_e + 0.14:.2f});
    tl.fromTo("#v02-lab-r", {{ x: 180, rotation: 8, opacity: 0 }}, {{ x: 0, rotation: 3.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {kw_e + 0.42:.2f});

    const dctx = document.getElementById("v02-drop-cvs").getContext("2d");
    const sctx = document.getElementById("v02-scale-cvs").getContext("2d");
    const p2 = {{ t: 0 }};
    tl.to(p2, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p2.t;
        // 1. Droplet + 7 Swimming Sperm
        dctx.clearRect(0, 0, 450, 390);
        dctx.save(); dctx.translate(125, 195);
        dctx.beginPath(); dctx.moveTo(0, -88); dctx.bezierCurveTo(68, -10, 72, 82, 0, 88); dctx.bezierCurveTo(-72, 82, -68, -10, 0, -88);
        const dg = dctx.createLinearGradient(0, -88, 0, 88);
        dg.addColorStop(0, "#e0f2fe"); dg.addColorStop(0.55, "#38bdf8"); dg.addColorStop(1, "#0284c7");
        dctx.fillStyle = dg; dctx.fill(); dctx.restore();

        for (let i = 0; i < 7; i++) {{
          const prog = (t * 0.52 + i * 0.14) % 1;
          const sx = 420 - prog * 195;
          const sy = 52 + i * 48 + Math.sin(t * 5 + i) * 8;
          dctx.fillStyle = "#ffffff"; dctx.beginPath(); dctx.ellipse(sx, sy, 12, 7.5, 0, 0, Math.PI * 2); dctx.fill();
          dctx.strokeStyle = "#7dd3fc"; dctx.lineWidth = 3.5; dctx.beginPath();
          for (let k = 0; k <= 8; k++) {{
            const u = k / 8;
            const tx = sx + 10 + u * 44;
            const ty = sy + Math.sin(t * 20 + i - u * 6) * (3 + u * 8);
            if (k === 0) dctx.moveTo(tx, ty); else dctx.lineTo(tx, ty);
          }}
          dctx.stroke();
        }}

        // 2. Wide Balance Scale behind left & right shoulders (cf. reel_02@4.8s!)
        sctx.clearRect(0, 0, 1012, 470);
        const tilt = Math.sin(t * 2.4) * 0.11;
        // Left Beaker (X=175) & Right Scale Pillar (X=835) so Chị Hằng's head in center (330..680) sits naturally between them!
        sctx.fillStyle = "rgba(14,165,233,0.22)";
        sctx.strokeStyle = "#0284c7"; sctx.lineWidth = 5;
        sctx.beginPath(); sctx.roundRect(88, 155, 175, 220, 22); sctx.fill(); sctx.stroke();
        const lvl = 95 + Math.sin(t * 3) * 18;
        sctx.fillStyle = "#38bdf8"; sctx.beginPath(); sctx.roundRect(96, 368 - lvl, 159, lvl, 14); sctx.fill();
        sctx.fillStyle = "#0f172a"; sctx.font = "800 26px BeVN, sans-serif";
        sctx.fillText("LƯỢNG DỊCH", 92, 128);

        // Right Balance Scale (X=820)
        sctx.save(); sctx.translate(825, 140);
        sctx.fillStyle = "#0d9488"; sctx.fillRect(-10, 0, 20, 235);
        sctx.beginPath(); sctx.roundRect(-75, 230, 150, 24, 12); sctx.fill();
        sctx.rotate(tilt);
        sctx.strokeStyle = "#0f766e"; sctx.lineWidth = 8;
        sctx.beginPath(); sctx.moveTo(-125, 10); sctx.lineTo(125, 10); sctx.stroke();
        sctx.fillStyle = "#10b981";
        sctx.beginPath(); sctx.arc(-115, 95, 42, 0, Math.PI); sctx.fill();
        sctx.beginPath(); sctx.arc(115, 95, 42, 0, Math.PI); sctx.fill();
        sctx.restore();
        sctx.fillStyle = "#0f766e"; sctx.font = "800 26px BeVN, sans-serif";
        sctx.fillText("≠ SỐ TINH BINH", 715, 112);
      }}
    }}, 0);"""
    sfx = [("sfx_pop_clean.mp3", hook_end + 0.18, 0.17), ("sfx_whoosh_soft.mp3", kw_s, 0.17), ("sfx_pop_clean.mp3", kw_e + 0.16, 0.17)]
    return wrap_stage_template(dur, css, "white_red", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #03: CƯƠNG TỐT VÌ SAO KHÓ CÓ CON (cf. reel_03: 1-2-3 Arc + Sapphire Sperm->Ovum Screen -> 3D Card Flip)
# ═══════════════════════════════════════════════════════════════════════════
def build_v03(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 340))
    kw_top = max(34, hy - 135)
    sh_y = max(120, hy - 10)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    .kobe-mini {{
      position: absolute; width: 280px; padding: 16px 18px; border-radius: 26px;
      background: #ffffff; border: 3.5px solid #3656fb;
      box-shadow: 0 18px 40px rgba(45,62,140,0.18); opacity: 0;
    }}
    .km-num {{ display:inline-block; width:38px; height:38px; border-radius:50%; background:#141418; color:#fff; font-family:"Montserrat",sans-serif; font-size:20px; text-align:center; line-height:38px; margin-right:8px; }}
    .km-t {{ font-family:"BeVN",sans-serif; font-size:25px; color:#3656fb; }}
    .km-s {{ margin-top:6px; font-family:"BeVN",sans-serif; font-size:20px; color:#334155; }}
    #v03-bio-holo {{
      position: absolute; right: 28px; top: {sh_y}px; width: 440px; height: 390px;
      border-radius: 32px; background: linear-gradient(150deg, #0b1938, #17346e);
      border: 3.5px solid #60a5fa; box-shadow: 0 20px 46px rgba(15,23,42,0.32); opacity: 0; overflow: hidden;
    }}
    #v03-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v03-k {{ font-family: "Anton", sans-serif; font-size: 92px; line-height: 1.03; color: #2563eb; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <div id="v03-kw"><div class="v03-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v03-k" style="color:#e11d48">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="km-1" class="kobe-mini" style="left: 30px; top: {sh_y + 10}px">
      <div><span class="km-num">1</span><span class="km-t">SỐ LƯỢNG</span></div>
      <div class="km-s">Mật độ tinh binh</div>
    </div>
    <div id="km-2" class="kobe-mini" style="left: 30px; top: {sh_y + 175}px">
      <div><span class="km-num">2</span><span class="km-t">ĐỘ DI ĐỘNG</span></div>
      <div class="km-s">Bơi khỏe tới trứng</div>
    </div>
    <div id="km-3" class="kobe-mini" style="left: 30px; top: {sh_y + 340}px">
      <div><span class="km-num">3</span><span class="km-t">HÌNH DẠNG</span></div>
      <div class="km-s">Cấu trúc bình thường</div>
    </div>
    <div id="v03-bio-holo"><canvas id="v03-ovum-cvs" width="440" height="390"></canvas></div>
    <div id="v03-lab-card" class="sh-card" style="right: 28px; top: {sh_y}px; border-color:#10b981">
      <img src="assets/images/broll_01.jpg" alt="Lab" />
      <span class="sh-badge" style="background:#059669">✔ TINH DỊCH ĐỒ</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    s_mid = round(max(hook_end + 0.15, kw_e + 0.15), 2)
    flip_t = round(min(dur - 2.6, s_mid + 3.1), 2)
    js = f"""
    {common_js}
    tl.fromTo("#v03-kw", {{ scale: 0.88, y: 20, opacity: 0 }}, {{ scale: 1, y: 0, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v03-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    tl.fromTo("#km-1", {{ x: -160, opacity: 0 }}, {{ x: 0, rotation: -3, opacity: 1, duration: 0.28, ease: "back.out(1.7)", immediateRender: false }}, {s_mid:.2f});
    tl.fromTo("#km-2", {{ x: -160, opacity: 0 }}, {{ x: 0, rotation: -1, opacity: 1, duration: 0.28, ease: "back.out(1.7)", immediateRender: false }}, {s_mid + 0.35:.2f});
    tl.fromTo("#km-3", {{ x: -160, opacity: 0 }}, {{ x: 0, rotation: 2, opacity: 1, duration: 0.28, ease: "back.out(1.7)", immediateRender: false }}, {s_mid + 0.70:.2f});

    tl.fromTo("#v03-bio-holo", {{ x: 160, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {s_mid + 0.15:.2f});
    // 3D Card Flip from Bio-Holo into Fertility Lab Card!
    tl.to("#v03-bio-holo", {{ rotationY: 90, opacity: 0, duration: 0.24, ease: "power2.in" }}, {flip_t:.2f});
    tl.fromTo("#v03-lab-card", {{ rotationY: -90, opacity: 0 }}, {{ rotationY: 0, rotation: 3, opacity: 1, duration: 0.28, ease: "back.out(1.5)", immediateRender: false }}, {flip_t + 0.24:.2f});

    const octx = document.getElementById("v03-ovum-cvs").getContext("2d");
    const p3 = {{ t: 0 }};
    tl.to(p3, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p3.t;
        octx.clearRect(0, 0, 440, 390);
        // Rose Ovum at right (345, 195)
        const pl = 1 + Math.sin(t * 3.6) * 0.05;
        octx.save(); octx.translate(345, 195); octx.scale(pl, pl);
        octx.beginPath(); octx.arc(0, 0, 58, 0, Math.PI * 2); octx.fillStyle = "rgba(244,114,182,0.28)"; octx.fill();
        octx.beginPath(); octx.arc(0, 0, 40, 0, Math.PI * 2); octx.fillStyle = "#f472b6"; octx.fill();
        octx.restore();
        for (let i = 0; i < 6; i++) {{
          const pr = (t * 0.5 + i * 0.17) % 1;
          const sx = 55 + pr * 225;
          const sy = 58 + i * 54 + Math.sin(t * 4.5 + i) * 9;
          octx.fillStyle = "#93c5fd"; octx.beginPath(); octx.ellipse(sx, sy, 13, 8, 0, 0, Math.PI * 2); octx.fill();
          octx.strokeStyle = "#60a5fa"; octx.lineWidth = 3.5; octx.beginPath();
          for (let k = 0; k <= 8; k++) {{
            const u = k / 8;
            const tx = sx - 10 - u * 44;
            const ty = sy + Math.sin(t * 20 + i - u * 6) * (3 + u * 8);
            if (k === 0) octx.moveTo(tx, ty); else octx.lineTo(tx, ty);
          }}
          octx.stroke();
        }}
      }}
    }}, 0);"""
    sfx = [("sfx_pop_clean.mp3", s_mid, 0.17), ("sfx_pop_clean.mp3", s_mid + 0.35, 0.17), ("sfx_whoosh_soft.mp3", flip_t, 0.17)]
    return wrap_stage_template(dur, css, "white_red", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #04: QUAI BỊ & VÔ SINH (cf. reel_04: Rotating 3D DNA & Cells Arc Behind Head + Twin Shoulder Cards)
# ═══════════════════════════════════════════════════════════════════════════
def build_v04(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 370))
    kw_top = max(34, hy - 138)
    sh_y = max(125, hy - 20)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v04-dna-arc {{ position: absolute; left: 0; top: {max(40, hy - 80)}px; width: 1080px; height: 560px; opacity: 0.92; }}
    #v04-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v04-k {{ font-family: "Anton", sans-serif; font-size: 94px; line-height: 1.03; color: #0891b2; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <canvas id="v04-dna-arc" width="1080" height="560"></canvas>
    <div id="v04-kw"><div class="v04-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v04-k" style="color:#ea580c">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v04-c1" class="sh-card" style="left: 26px; top: {sh_y + 16}px; border-color:#ef4444">
      <img src="assets/images/broll_01.jpg" alt="Ice" />
      <span class="sh-badge" style="background:#dc2626">⚠ BIẾN CHỨNG SƯNG</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v04-c2" class="sh-card" style="right: 26px; top: {sh_y + 16}px; border-color:#10b981">
      <img src="assets/images/broll_02.jpg" alt="Doctor" />
      <span class="sh-badge" style="background:#059669">✔ KHÁM NAM KHOA</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    js = f"""
    {common_js}
    tl.fromTo("#v04-c1", {{ x: -180, rotation: -8, opacity: 0 }}, {{ x: 0, rotation: -3.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {hook_end + 0.15:.2f});
    tl.to("#v04-c1", {{ opacity: 0, x: -120, duration: 0.20 }}, {max(hook_end + 1.8, kw_s - 0.12):.2f});

    tl.fromTo("#v04-kw", {{ scale: 0.88, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v04-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    tl.fromTo("#v04-c2", {{ x: 180, rotation: 8, opacity: 0 }}, {{ x: 0, rotation: 3.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {kw_e + 0.16:.2f});

    const d4 = document.getElementById("v04-dna-arc").getContext("2d");
    const p4 = {{ t: 0 }};
    tl.to(p4, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p4.t;
        d4.clearRect(0, 0, 1080, 560);
        // Diagonal 22-Strand 3D Double-Helix DNA sweeping behind Chị Hằng's shoulders!
        for (let i = 0; i < 24; i++) {{
          const x = 60 + i * 42;
          const baseY = 280 - (i - 12) * 8;
          const ph = t * 3.6 + i * 0.38;
          const y1 = baseY + Math.sin(ph) * 95;
          const y2 = baseY - Math.sin(ph) * 95;
          d4.strokeStyle = "rgba(14,165,233,0.28)"; d4.lineWidth = 3.5;
          d4.beginPath(); d4.moveTo(x, y1); d4.lineTo(x, y2); d4.stroke();
          d4.beginPath(); d4.arc(x, y1, 10, 0, Math.PI * 2); d4.fillStyle = "#06b6d4"; d4.fill();
          d4.beginPath(); d4.arc(x, y2, 10, 0, Math.PI * 2); d4.fillStyle = "#f97316"; d4.fill();
        }}
      }}
    }}, 0);"""
    sfx = [("sfx_pop_clean.mp3", hook_end + 0.18, 0.17), ("sfx_ping_glass.mp3", kw_s, 0.17), ("sfx_pop_clean.mp3", kw_e + 0.18, 0.17)]
    return wrap_stage_template(dur, css, "yellow_black", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #05: CHƯA ĐƯỢC 3 PHÚT ĐÃ XUẤT (cf. reel_05: Digital 03:00 Timer -> Repeat Calendar Ring -> Shield/Warning)
# ═══════════════════════════════════════════════════════════════════════════
def build_v05(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 340))
    kw_top = max(34, hy - 136)
    sh_y = max(120, hy - 15)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v05-timer-hud {{
      position: absolute; left: 190px; top: {max(28, hy - 110)}px; width: 700px; height: 210px;
      border-radius: 34px; background: rgba(12, 24, 44, 0.88); border: 4px solid #38bdf8;
      box-shadow: 0 0 36px rgba(56,189,248,0.45); display: flex; align-items: center; justify-content: center;
      font-family: "Montserrat", sans-serif; font-size: 118px; color: #e0f2fe; letter-spacing: 0.06em;
      text-shadow: 0 0 24px #38bdf8;
    }}
    #v05-ring-cvs {{ position: absolute; left: 0; top: 80px; width: 1080px; height: 700px; opacity: 0; }}
    #v05-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v05-k {{ font-family: "Anton", sans-serif; font-size: 94px; line-height: 1.03; color: #dc2626; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <div id="v05-timer-hud">02:58</div>
    <canvas id="v05-ring-cvs" width="1080" height="700"></canvas>
    <div id="v05-kw"><div class="v05-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v05-k" style="color:#0f172a">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v05-c1" class="sh-card" style="left: 26px; top: {sh_y + 20}px; border-color:#0284c7">
      <img src="assets/images/broll_01.jpg" alt="Consult" />
      <span class="sh-badge">LẶP LẠI NHIỀU LẦN</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v05-c2" class="sh-card" style="right: 26px; top: {sh_y + 20}px; border-color:#ef4444">
      <img src="assets/images/broll_02.jpg" alt="No fake pills" />
      <span class="sh-badge" style="background:#dc2626">✕ CẤM TỰ DÙNG THUỐC</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    js = f"""
    {common_js}
    tl.fromTo("#v05-timer-hud", {{ scale: 0.85, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.28, ease: "back.out(1.6)" }}, 0.08);
    tl.to("#v05-timer-hud", {{ y: -40, opacity: 0, duration: 0.24 }}, {hook_end:.2f});

    tl.to("#v05-ring-cvs", {{ opacity: 1, duration: 0.35 }}, {hook_end + 0.10:.2f});
    tl.fromTo("#v05-kw", {{ scale: 0.88, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v05-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    tl.fromTo("#v05-c1", {{ x: -190, rotation: -8, opacity: 0 }}, {{ x: 0, rotation: -3.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, 8.10);
    tl.fromTo("#v05-c2", {{ x: 190, rotation: 8, opacity: 0 }}, {{ x: 0, rotation: 3.5, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, 11.95);

    const timerEl = document.getElementById("v05-timer-hud");
    const rctx = document.getElementById("v05-ring-cvs").getContext("2d");
    const p5 = {{ t: 0 }};
    tl.to(p5, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p5.t;
        if (t <= {hook_end + 0.2:.2f}) {{
          const rem = Math.max(42, Math.round(179 - t * 38));
          const mm = "0" + Math.floor(rem / 60);
          const ss = String(rem % 60).padStart(2, "0");
          timerEl.textContent = mm + ":" + ss;
        }}
        rctx.clearRect(0, 0, 1080, 700);
        // Rotating Repeat-Cycle Arc behind head (cf. reel_05@8.2s!)
        rctx.save(); rctx.translate(540, 360); rctx.rotate(t * 0.45);
        rctx.strokeStyle = "rgba(2,132,199,0.34)"; rctx.lineWidth = 10; rctx.setLineDash([28, 18]);
        rctx.beginPath(); rctx.arc(0, 0, 310, 0, Math.PI * 2); rctx.stroke();
        rctx.strokeStyle = "rgba(234,88,12,0.28)"; rctx.lineWidth = 6;
        rctx.beginPath(); rctx.arc(0, 0, 370, 0, Math.PI * 2); rctx.stroke();
        rctx.restore();
      }}
    }}, 0);"""
    sfx = [("sfx_click_soft.mp3", 0.15, 0.16), ("sfx_pop_clean.mp3", 8.12, 0.17), ("sfx_pop_clean.mp3", 11.98, 0.18)]
    return wrap_stage_template(dur, css, "yellow_black", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #06: MUỐN GẦN VỢ NHƯNG CƯƠNG KHÔNG NỔI (cf. reel_06: Glowing Red Heart Left + Blue Crystal Right!)
# ═══════════════════════════════════════════════════════════════════════════
def build_v06(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 360))
    kw_top = max(34, hy - 136)
    sh_y = max(125, hy - 25)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v06-twin-cvs {{ position: absolute; left: 0; top: {max(40, sh_y - 60)}px; width: 1080px; height: 520px; opacity: 0; }}
    #v06-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v06-k {{ font-family: Georgia, "Times New Roman", serif; font-weight: 700; font-style: italic; font-size: 88px; line-height: 1.05; color: #be123c; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <canvas id="v06-twin-cvs" width="1080" height="520"></canvas>
    <div id="v06-kw"><div class="v06-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v06-k" style="color:#1d4ed8">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v06-c1" class="sh-card" style="left: 26px; top: {sh_y + 110}px; border-color:#f43f5e">
      <img src="assets/images/broll_01.jpg" alt="Wife" />
      <span class="sh-badge" style="background:#e11d48">❤ CHIA SẺ CÙNG VỢ</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v06-c2" class="sh-card" style="right: 26px; top: {sh_y + 110}px; border-color:#2563eb">
      <img src="assets/images/broll_02.jpg" alt="Doctor" />
      <span class="sh-badge" style="background:#2563eb">🩺 KHÁM MẠCH MÁU</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    cards_t = round(max(8.2, kw_e + 0.25), 2)
    js = f"""
    {common_js}
    tl.fromTo("#v06-twin-cvs", {{ scale: 0.88, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(1.6)", immediateRender: false }}, {hook_end + 0.10:.2f});
    tl.fromTo("#v06-kw", {{ y: 20, filter: "blur(14px)", opacity: 0 }}, {{ y: 0, filter: "blur(0px)", opacity: 1, duration: 0.24, ease: "power3.out", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v06-kw", {{ opacity: 0, duration: 0.16 }}, {kw_e - 0.15:.2f});

    tl.fromTo("#v06-c1", {{ x: -190, rotation: -6, opacity: 0 }}, {{ x: 0, rotation: -3, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {cards_t:.2f});
    tl.fromTo("#v06-c2", {{ x: 190, rotation: 6, opacity: 0 }}, {{ x: 0, rotation: 3, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {cards_t + 1.8:.2f});

    const t6 = document.getElementById("v06-twin-cvs").getContext("2d");
    const p6 = {{ t: 0 }};
    tl.to(p6, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p6.t;
        t6.clearRect(0, 0, 1080, 520);
        // Left Glowing Ruby Heart "Ham muốn" (X=185, Y=195) — exact match to reel_06!
        const hp = 1 + Math.sin(t * 4.2) * 0.06;
        t6.save(); t6.translate(185, 205); t6.scale(hp, hp);
        t6.beginPath(); t6.arc(0, 0, 96, 0, Math.PI * 2); t6.fillStyle = "rgba(244,63,94,0.22)"; t6.fill();
        t6.fillStyle = "#e11d48";
        t6.beginPath(); t6.moveTo(0, 52); t6.bezierCurveTo(-78, -4, -74, -68, 0, -30); t6.bezierCurveTo(74, -68, 78, -4, 0, 52); t6.fill();
        t6.restore();
        t6.fillStyle = "#be123c"; t6.font = "800 32px BeVN, sans-serif"; t6.fillText("HAM MUỐN", 98, 78);

        // Right Glowing Cobalt Crystal Polygon "Cương" (X=895, Y=205) — exact match to reel_06!
        t6.save(); t6.translate(895, 205);
        t6.beginPath(); t6.arc(0, 0, 96, 0, Math.PI * 2); t6.fillStyle = "rgba(37,99,235,0.22)"; t6.fill();
        t6.rotate(Math.sin(t * 2.0) * 0.14);
        t6.fillStyle = "#2563eb"; t6.strokeStyle = "#93c5fd"; t6.lineWidth = 4;
        t6.beginPath();
        for (let k = 0; k < 6; k++) {{
          const a = (k * Math.PI) / 3 - Math.PI / 2;
          const vx = Math.cos(a) * 66, vy = Math.sin(a) * 66;
          if (k === 0) t6.moveTo(vx, vy); else t6.lineTo(vx, vy);
        }}
        t6.closePath(); t6.fill(); t6.stroke();
        t6.restore();
        t6.fillStyle = "#1d4ed8"; t6.font = "800 32px BeVN, sans-serif"; t6.fillText("PHẢN XẠ CƯƠNG", 755, 78);
      }}
    }}, 0);"""
    sfx = [("sfx_chime_warm.mp3", hook_end + 0.14, 0.16), ("sfx_pop_clean.mp3", cards_t, 0.17), ("sfx_pop_clean.mp3", cards_t + 1.8, 0.17)]
    return wrap_stage_template(dur, css, "yellow_black", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #07: CÀNG TỰ XỬ CÀNG DỄ TEO (cf. reel_07: Blood-Flow Vessel Holo -> Equilibrium Check -> Doctor Card)
# ═══════════════════════════════════════════════════════════════════════════
def build_v07(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 420))
    kw_top = max(36, hy - 140)
    sh_y = max(130, hy - 20)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v07-vessel-box {{
      position: absolute; right: 28px; top: {sh_y}px; width: 430px; height: 380px;
      border-radius: 30px; background: rgba(255,255,255,0.92); border: 4px solid #3b82f6;
      box-shadow: 0 20px 44px rgba(15,23,42,0.18); opacity: 0; overflow: hidden;
    }}
    #v07-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v07-k {{ font-family: "Anton", sans-serif; font-size: 94px; line-height: 1.03; color: #059669; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <div id="v07-vessel-box"><canvas id="v07-vessel-cvs" width="430" height="380"></canvas></div>
    <div id="v07-kw"><div class="v07-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v07-k" style="color:#0f172a">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v07-c1" class="sh-card" style="left: 26px; top: {sh_y + 15}px; border-color:#2563eb">
      <img src="assets/images/broll_01.jpg" alt="Rest" />
      <span class="sh-badge">MỀM NGHỈ NGƠI</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v07-c2" class="sh-card" style="right: 26px; top: {sh_y + 15}px; border-color:#10b981">
      <img src="assets/images/broll_02.jpg" alt="Doctor" />
      <span class="sh-badge" style="background:#059669">✔ KHI NÀO KHÁM?</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    c2_t = round(min(dur - 2.3, max(kw_e + 0.5, 9.5)), 2)
    js = f"""
    {common_js}
    tl.fromTo("#v07-vessel-box", {{ x: 160, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {hook_end + 0.12:.2f});
    tl.fromTo("#v07-c1", {{ x: -180, rotation: -6, opacity: 0 }}, {{ x: 0, rotation: -3, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {hook_end + 0.45:.2f});

    tl.fromTo("#v07-kw", {{ scale: 0.88, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v07-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    tl.to("#v07-vessel-box", {{ x: 140, opacity: 0, duration: 0.22 }}, {c2_t - 0.22:.2f});
    tl.fromTo("#v07-c2", {{ x: 180, rotation: 6, opacity: 0 }}, {{ x: 0, rotation: 3, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {c2_t:.2f});

    const v7 = document.getElementById("v07-vessel-cvs").getContext("2d");
    const p7 = {{ t: 0 }};
    tl.to(p7, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p7.t;
        v7.clearRect(0, 0, 430, 380);
        // Top Vessel (Erect blood flow) vs Bottom Vessel (Resting blood return — 0% tissue loss!)
        v7.fillStyle = "#fee2e2"; v7.beginPath(); v7.roundRect(35, 65, 360, 82, 41); v7.fill();
        v7.strokeStyle = "#ef4444"; v7.lineWidth = 4; v7.stroke();
        for (let i = 0; i < 6; i++) {{
          const bx = 65 + ((t * 110 + i * 56) % 300);
          v7.fillStyle = "#ef4444"; v7.beginPath(); v7.arc(bx, 106, 14, 0, Math.PI * 2); v7.fill();
        }}
        v7.fillStyle = "#991b1b"; v7.font = "800 22px BeVN, sans-serif"; v7.fillText("LÚC CƯƠNG: MÁU DỒN ĐẦY", 65, 48);

        v7.fillStyle = "#dbeafe"; v7.beginPath(); v7.roundRect(55, 225, 320, 56, 28); v7.fill();
        v7.strokeStyle = "#2563eb"; v7.lineWidth = 4; v7.stroke();
        for (let i = 0; i < 4; i++) {{
          const bx = 340 - ((t * 65 + i * 68) % 250);
          v7.fillStyle = "#3b82f6"; v7.beginPath(); v7.arc(bx, 253, 10, 0, Math.PI * 2); v7.fill();
        }}
        v7.fillStyle = "#1e40af"; v7.font = "800 22px BeVN, sans-serif"; v7.fillText("SAU XUẤT: NGHỈ NGƠI (0% TEO)", 45, 208);
      }}
    }}, 0);"""
    sfx = [("sfx_pop_clean.mp3", hook_end + 0.16, 0.17), ("sfx_ping_glass.mp3", kw_s, 0.17), ("sfx_pop_clean.mp3", c2_t, 0.17)]
    return wrap_stage_template(dur, css, "yellow_black", behind, fg_html, js), sfx
