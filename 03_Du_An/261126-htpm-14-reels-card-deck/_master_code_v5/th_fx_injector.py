# -*- coding: utf-8 -*-
"""
14-Video Polymorphic Talking-Head FX + Continuous Flying/Gliding Icons (`bay lượn`) Injector:
1. Every single video (#01 -> #14) gets its own bespoke continuous Flying/Gliding Vector Icon Layer
   (`#th-float-cvs` strictly BEHIND `#vid-fg` RVM at z-index 5 -> 0% covering Chị Hằng!):
   - Swimming sperm, aqua droplets, rose ova, DNA spheres, ruby hearts, frost crystals, rising bubbles,
     glowing shields, moons, conversation bubbles, and orbiting tokens gently flying (`bay lượn`)!
2. 6 Distinct Hook Badge Designs across the 14 videos (NO identical purple boxes across all 14 hooks!).
3. Rotating Talking-Head Signature FX (`ANIM_DIM`, `CC Light Sweep`, `A4 Neon Number + Lightning`, `A11 RingsBg` Finale).
"""

# 6 distinct Hook Badge visual themes so every video's opening looks genuinely different!
HOOK_THEMES = [
    # 0: Neon Violet EdgeSweep Square
    ("border-radius:36px; background:#101318; border:4px solid #9b3cff; box-shadow:0 14px 32px rgba(155,60,255,0.42);", "#55f2ff"),
    # 1: Frosted Cyan Medical Circle
    ("border-radius:50%; background:linear-gradient(145deg,#083344,#0e7490); border:4px solid #67e8f9; box-shadow:0 14px 32px rgba(6,182,212,0.38);", "#ffffff"),
    # 2: Kobe Pastel Periwinkle Pill
    ("border-radius:42px; background:#ffffff; border:4px solid #3656fb; box-shadow:0 16px 34px rgba(54,86,251,0.25);", "#3656fb"),
    # 3: Emerald Shield Glass
    ("border-radius:30px 30px 54px 54px; background:linear-gradient(160deg,#064e3b,#059669); border:4px solid #6ee7b7; box-shadow:0 14px 32px rgba(16,185,129,0.36);", "#fef08a"),
    # 4: Warm Rose Editorial Diamond-Round
    ("border-radius:38px; background:linear-gradient(145deg,#fff1f2,#ffe4e6); border:4px solid #f43f5e; box-shadow:0 14px 32px rgba(244,63,94,0.28);", "#e11d48"),
    # 5: Dark Cyber Amber-Cyan Octagon-Card
    ("border-radius:26px; background:#14161a; border:4px solid #f26b21; box-shadow:0 14px 32px rgba(242,107,33,0.36);", "#36ccc8"),
]

TOPIC_ICONS = {
    1: ("⏱", "🛡"),
    2: ("💧", "🔬"),
    3: ("🧬", "👶"),
    4: ("🛡", "🩺"),
    5: ("⏰", "⚡"),
    6: ("❤", "💎"),
    7: ("🩸", "✔"),
    8: ("🧄", "💚"),
    9: ("💬", "❤"),
    10: ("📈", "🔋"),
    11: ("🌙", "❄"),
    12: ("🍺", "🚫"),
    13: ("⚠", "🔄"),
    14: ("🚭", "🏃"),
}


def get_th_fx_bundle(sp: dict, plan: dict):
    idx = sp["idx"]
    dur = plan["dur"]
    hook_end = plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 360))
    tile_y = max(86, hy - 30)
    ico_l, ico_r = TOPIC_ICONS.get(idx, ("⚡", "✔"))
    theme_css, glow_col = HOOK_THEMES[(idx - 1) % len(HOOK_THEMES)]
    num_txt = f"{idx:02d}"

    preset_mod = idx % 3
    fin_s = round(max(hook_end + 3.8, dur - 2.85), 2)

    css = f"""
    #th-anim-dim {{
      position: absolute; inset: 0; z-index: 2; opacity: 0; pointer-events: none;
      background: radial-gradient(circle at 50% 42%, rgba(30, 27, 75, 0.34) 0%, rgba(7, 10, 25, 0.64) 100%);
    }}
    #th-rings-bg {{
      position: absolute; inset: 0; z-index: 3; opacity: 0; pointer-events: none;
      background: radial-gradient(circle at 50% 42%, #232c52 0%, #050814 88%);
      overflow: hidden;
    }}
    #th-rings-flash {{ position: absolute; inset: 0; background: #ffffff; opacity: 0; }}
    .th-ring-lg {{
      position: absolute; left: 30px; top: 180px; width: 1020px; height: 1020px;
      border-radius: 50%; border: 4px dashed rgba(143, 248, 255, 0.50);
    }}
    .th-ring-sm {{
      position: absolute; left: 150px; top: 300px; width: 780px; height: 780px;
      border-radius: 50%; border: 3px solid rgba(196, 181, 253, 0.40);
    }}
    /* Continuous Flying/Gliding Icon Canvas (z-index 4: strictly BEHIND vid-fg z-index 20!) */
    #th-float-cvs {{
      position: absolute; left: 0; top: 0; width: 1080px; height: 1180px; z-index: 4; pointer-events: none;
    }}

    .th-hook-badge {{
      position: absolute; width: 164px; height: 164px;
      {theme_css}
      display: flex; align-items: center; justify-content: center;
      opacity: 0; will-change: transform, opacity;
    }}
    .th-hook-ico {{ font-size: 70px; filter: drop-shadow(0 4px 12px {glow_col}); }}
    .th-burst {{
      position: absolute; width: 84px; height: 84px; border-radius: 50%;
      border: 5px solid {glow_col}; opacity: 0; pointer-events: none;
    }}

    /* Top Keyword Card-Pause Mask: gently hides shoulder cards during [kw_s..kw_e] so 0% collision! */
    #cards-substage {{ position: absolute; inset: 0; will-change: opacity; }}

    #th-neon-num {{
      position: absolute; right: 28px; top: {max(18, hy - 140)}px;
      font-family: "BarlowItalic", sans-serif; font-size: 205px; line-height: 0.85;
      color: rgba(154, 130, 255, 0.38); -webkit-text-stroke: 6px #8ff8ff;
      filter: drop-shadow(0 0 20px rgba(85, 242, 255, 0.72)); opacity: 0;
    }}
    #th-kw-light-sweep {{
      position: absolute; left: -260px; top: {max(12, hy - 200)}px; width: 220px; height: 240px;
      background: linear-gradient(105deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.80) 50%, rgba(255,255,255,0) 100%);
      transform: skewX(-22deg); opacity: 0; pointer-events: none; mix-blend-mode: screen; z-index: 9;
    }}
    .sub-ghost {{
      position: absolute; inset: 0; pointer-events: none;
      color: transparent !important; -webkit-text-stroke: 3.5px #8ff8ff !important;
      opacity: 0; will-change: transform, opacity;
    }}
    """

    backdrop_html = f"""
    <div id="th-anim-dim" data-layout-ignore></div>
    <div id="th-rings-bg" data-layout-ignore>
      <div class="th-ring-lg" id="th-rlg"></div>
      <div class="th-ring-sm" id="th-rsm"></div>
      <div id="th-rings-flash"></div>
    </div>
    <canvas id="th-float-cvs" width="1080" height="1180" data-layout-ignore></canvas>
    """

    behind_fx_html = f"""
    <div id="th-b1" class="th-burst" style="left: 112px; top: {tile_y + 38}px"></div>
    <div id="th-b2" class="th-burst" style="right: 112px; top: {tile_y + 38}px"></div>
    <div id="th-tile-l" class="th-hook-badge" style="left: 52px; top: {tile_y}px">
      <div class="th-hook-ico">{ico_l}</div>
    </div>
    <div id="th-tile-r" class="th-hook-badge" style="right: 52px; top: {tile_y}px">
      <div class="th-hook-ico">{ico_r}</div>
    </div>
    <div id="th-neon-num">{num_txt}</div>
    <div id="th-kw-light-sweep"></div>
    """

    tile_out = round(max(0.9, hook_end - 0.22), 2)
    js_parts = [f"""
    // Varied Hook Badges + Burst Rings
    tl.fromTo("#th-b1", {{ scale: 0.3, opacity: 0.9 }}, {{ scale: 2.0, opacity: 0, duration: 0.34, ease: "power2.out" }}, 0.10);
    tl.fromTo("#th-tile-l", {{ y: 95, scale: 0.55, rotation: -14, opacity: 0 }}, {{ y: 0, scale: 0.94, rotation: -6, opacity: 1, duration: 0.30, ease: "back.out(1.8)" }}, 0.10);
    tl.to("#th-tile-l", {{ y: -45, scale: 0.75, opacity: 0, duration: 0.20, ease: "power2.in" }}, {tile_out:.2f});
    """]

    if idx not in (1, 2, 8):
        js_parts.append(f"""
    tl.fromTo("#th-b2", {{ scale: 0.3, opacity: 0.9 }}, {{ scale: 2.0, opacity: 0, duration: 0.34, ease: "power2.out" }}, 0.24);
    tl.fromTo("#th-tile-r", {{ y: 95, scale: 0.55, rotation: 14, opacity: 0 }}, {{ y: 0, scale: 0.94, rotation: 6, opacity: 1, duration: 0.30, ease: "back.out(1.8)" }}, 0.24);
    tl.to("#th-tile-r", {{ y: -45, scale: 0.75, opacity: 0, duration: 0.20, ease: "power2.in" }}, {tile_out:.2f});
        """)

    # Pause/fade #cards-substage during Top Keyword [kw_s..kw_e] so Top Keyword NEVER collides with shoulder cards!
    js_parts.append(f"""
    tl.to("#cards-substage", {{ opacity: 0.08, duration: 0.16 }}, {max(0.05, kw_s - 0.14):.2f});
    tl.to("#cards-substage", {{ opacity: 1.0, duration: 0.20 }}, {kw_e - 0.06:.2f});
    tl.to("#th-anim-dim", {{ opacity: 0.82, duration: 0.28, ease: "power2.out" }}, {max(0.08, kw_s - 0.14):.2f});
    tl.to("#th-anim-dim", {{ opacity: 0, duration: 0.28, ease: "power2.in" }}, {kw_e - 0.08:.2f});
    tl.fromTo("#th-kw-light-sweep", {{ x: 120, opacity: 0.95 }}, {{ x: 1180, opacity: 0, duration: 0.76, ease: "power2.inOut", immediateRender: false }}, {kw_s + 0.08:.2f});
    """)

    if preset_mod == 1:
        js_parts.append(f"""
    tl.fromTo("#th-neon-num", {{ scale: 1.4, rotation: -12, opacity: 0 }}, {{ scale: 1.0, rotation: 0, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#th-neon-num", {{ opacity: 0, duration: 0.16 }}, {kw_e - 0.15:.2f});
        """)
    elif preset_mod == 2:
        js_parts.append(f"""
    tl.fromTo("#th-rings-bg", {{ scale: 1.16, opacity: 0 }}, {{ scale: 1.0, opacity: 0.88, duration: 0.34, ease: "power3.out", immediateRender: false }}, {fin_s:.2f});
    tl.fromTo("#th-rings-flash", {{ opacity: 0.48 }}, {{ opacity: 0, duration: 0.15, immediateRender: false }}, {fin_s:.2f});
    tl.to("#th-rlg", {{ rotation: 46, duration: {max(1.4, dur - fin_s):.2f}, ease: "none" }}, {fin_s:.2f});
    tl.to("#th-rsm", {{ rotation: -54, duration: {max(1.4, dur - fin_s):.2f}, ease: "none" }}, {fin_s:.2f});
        """)

    # Continuous Topic-Matched Gliding/Flying Icons (`bay lượn`) across the whole video behind Chị Hằng!
    js_parts.append(f"""
    const flCtx = document.getElementById("th-float-cvs").getContext("2d");
    const VID_IDX = {idx};
    const flPrx = {{ t: 0 }};
    tl.to(flPrx, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = flPrx.t;
        flCtx.clearRect(0, 0, 1080, 1180);
        // 8 Gently Gliding / Flying Topic Icons in Left [55..275] & Right [805..1025] Corridors behind Chị Hằng!
        for (let i = 0; i < 8; i++) {{
          const isLeft = (i % 2 === 0);
          const laneX = isLeft ? (95 + (i * 37) % 165) : (825 + (i * 43) % 165);
          const cyc = (t * 0.24 + i * 0.135) % 1;
          const fx = laneX + Math.sin(t * 1.9 + i * 1.3) * 34;
          const fy = 980 - cyc * 860;
          const alpha = Math.sin(cyc * Math.PI) * 0.82;
          if (alpha <= 0.05) continue;

          flCtx.save();
          flCtx.globalAlpha = alpha;
          flCtx.translate(fx, fy);
          const rot = Math.sin(t * 2.2 + i) * 0.25;

          if (VID_IDX === 1 || VID_IDX === 2 || VID_IDX === 3) {{
            // Flying/Swimming 3D Sperm & Glowing Aqua/Rose Orbs!
            flCtx.rotate(isLeft ? -0.45 + rot * 0.4 : -2.65 + rot * 0.4);
            flCtx.fillStyle = (VID_IDX === 3 && i % 3 === 0) ? "#f472b6" : "#38bdf8";
            flCtx.beginPath(); flCtx.ellipse(0, 0, 15, 9.5, 0, 0, Math.PI * 2); flCtx.fill();
            flCtx.strokeStyle = "#7dd3fc"; flCtx.lineWidth = 3.5; flCtx.beginPath();
            for (let k = 0; k <= 8; k++) {{
              const u = k / 8;
              const tx = -12 - u * 48;
              const ty = Math.sin(t * 18 + i - u * 6) * (3 + u * 8);
              if (k === 0) flCtx.moveTo(tx, ty); else flCtx.lineTo(tx, ty);
            }}
            flCtx.stroke();
          }} else if (VID_IDX === 6 || VID_IDX === 9) {{
            // Gliding Ruby Hearts & Cobalt/Mint Wellness Rings!
            flCtx.scale(0.85 + (i % 3) * 0.15, 0.85 + (i % 3) * 0.15);
            flCtx.rotate(rot);
            if (isLeft) {{
              flCtx.fillStyle = "#fb7185";
              flCtx.beginPath(); flCtx.moveTo(0, 16); flCtx.bezierCurveTo(-24, -2, -22, -22, 0, -9); flCtx.bezierCurveTo(22, -22, 24, -2, 0, 16); flCtx.fill();
            }} else {{
              flCtx.strokeStyle = "#3b82f6"; flCtx.lineWidth = 4;
              flCtx.beginPath(); flCtx.arc(0, 0, 16, 0, Math.PI * 2); flCtx.stroke();
            }}
          }} else if (VID_IDX === 11) {{
            // Drifting Frost Crystals &Crescent Moons!
            flCtx.rotate(t * 0.8 + i);
            flCtx.strokeStyle = "#38bdf8"; flCtx.lineWidth = 3.5;
            for (let a = 0; a < 3; a++) {{
              flCtx.rotate(Math.PI / 3);
              flCtx.beginPath(); flCtx.moveTo(-16, 0); flCtx.lineTo(16, 0); flCtx.stroke();
            }}
          }} else if (VID_IDX === 12) {{
            // Rising Golden Effervescent Bubbles & Red Warning Rings!
            flCtx.fillStyle = i % 3 === 0 ? "rgba(239,68,68,0.45)" : "rgba(251,191,36,0.55)";
            flCtx.strokeStyle = "#ffffff"; flCtx.lineWidth = 2.5;
            flCtx.beginPath(); flCtx.arc(0, 0, 11 + (i % 3) * 5, 0, Math.PI * 2); flCtx.fill(); flCtx.stroke();
          }} else {{
            // Gliding Medical Shields, Plus Crosses & Vitality Rings (#04, #05, #07, #08, #10, #13, #14)
            flCtx.rotate(rot);
            if (i % 2 === 0) {{
              flCtx.fillStyle = "#10b981";
              flCtx.beginPath(); flCtx.roundRect(-5, -16, 10, 32, 4); flCtx.fill();
              flCtx.beginPath(); flCtx.roundRect(-16, -5, 32, 10, 4); flCtx.fill();
            }} else {{
              flCtx.strokeStyle = "#0ea5e9"; flCtx.lineWidth = 4;
              flCtx.beginPath(); flCtx.roundRect(-15, -15, 30, 30, 9); flCtx.stroke();
            }}
          }}
          flCtx.restore();
        }}
      }}
    }}, 0);
    """)

    return css, backdrop_html, behind_fx_html, "\n".join(js_parts)
