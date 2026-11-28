# -*- coding: utf-8 -*-
"""
Bespoke Behind-Subject Hologram & Card-Deck Builders (#08 -> #14)
Modeled directly on the original hanh.sung.suong reference reels (#08..#14) + Studio Talking-Head FX:
- #08: 4-Card Orbiting Wellness Fan Behind Shoulders (Garlic -> Healthy Plate + Green Heart Shield -> Exercise -> Doctor)
- #09: Dual ECG / Hormone Wave Arc Behind Head + Warm Couple/Doctor Dialogue Cards
- #10: Talking-Head v3 Cyan Physiology Recovery Monitor Behind Right Shoulder + Outlined 10 + Mint Italic Subs
- #11: 4-Act Metaphors Behind Head (Midnight Clock -> ED Card -> Twin 3D Frozen Ice Cubes "BỊ TRƠ" -> Cooling Thermometer)
- #12: Dark-Cyan Neural/Vascular Suppression HUD + Draining Stamina Gauge -> Foaming Beer Mug (✕) + Recovery Card
- #13: 3D Curved 5-Card Carousel Orbiting Behind Head (Signs 1 -> 5)
- #14: 5 Flying Habit Cards + Clinking Beer Glasses + Narrowed Cigarette Blood Vessel Behind Shoulders
"""
import html
from behind_styles_01_07 import render_hook_and_subs, wrap_stage_template


# ═══════════════════════════════════════════════════════════════════════════
# #08: ĂN TỎI CƯƠNG TỐT HƠN? (cf. reel_08: 4-Card Orbiting Wellness Fan + Green Heart Shield)
# ═══════════════════════════════════════════════════════════════════════════
def build_v08(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 420))
    kw_top = max(36, hy - 140)
    sh_y = max(130, hy - 25)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v08-shield-orb {{
      position: absolute; right: 54px; top: {sh_y - 10}px; width: 330px; height: 330px; opacity: 0;
    }}
    #v08-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v08-k {{ font-family: "Anton", sans-serif; font-size: 94px; line-height: 1.03; color: #d97706; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <canvas id="v08-shield-orb" width="330" height="330"></canvas>
    <div id="v08-kw"><div class="v08-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v08-k" style="color:#059669">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v08-c0" class="sh-card" style="right: 28px; top: {sh_y + 10}px; border-color:#f59e0b">
      <img src="assets/images/broll_hook.jpg" alt="Garlic" />
      <span class="sh-badge" style="background:#d97706">01 • MÓN ĐƠN LẺ</span>
      <div class="sh-head">CHỈ ĂN TỎI</div>
      <div class="sh-desc">Không tự chữa khỏi bệnh</div>
    </div>
    <div id="v08-c1" class="sh-card" style="left: 28px; top: {sh_y + 10}px; border-color:#10b981">
      <img src="assets/images/broll_01.jpg" alt="Diet" />
      <span class="sh-badge" style="background:#059669">02 • ĂN LÀNH MẠNH</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v08-c2" class="sh-card" style="right: 28px; top: {sh_y + 18}px; border-color:#0284c7">
      <img src="assets/images/broll_02.jpg" alt="Sport" />
      <span class="sh-badge">03 • TẬP & KHÁM SỚM</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    t_c2 = round(max(9.2, kw_e + 1.2), 2)
    js = f"""
    {common_js}
    // Card 0 (Garlic) deals on Hook behind right shoulder, then flies across behind head!
    tl.fromTo("#v08-c0", {{ x: 160, rotation: 8, opacity: 0 }}, {{ x: 0, rotation: 4, opacity: 1, duration: 0.32, ease: "back.out(1.6)" }}, 0.15);
    tl.to("#v08-c0", {{ x: -640, y: -30, rotation: -8, opacity: 0, duration: 0.42, ease: "power2.inOut" }}, {hook_end:.2f});

    // Healthy Plate left + Glowing Green Heart Shield right (cf. reel_08@4.8s!)
    tl.fromTo("#v08-c1", {{ x: -180, rotation: -8, opacity: 0 }}, {{ x: 0, rotation: -3.5, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, {hook_end + 0.20:.2f});
    tl.fromTo("#v08-shield-orb", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.34, ease: "back.out(1.8)", immediateRender: false }}, {hook_end + 0.35:.2f});

    tl.fromTo("#v08-kw", {{ scale: 0.88, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v08-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    tl.to("#v08-shield-orb", {{ scale: 0.7, opacity: 0, duration: 0.22 }}, {t_c2 - 0.22:.2f});
    tl.fromTo("#v08-c2", {{ x: 180, rotation: 8, opacity: 0 }}, {{ x: 0, rotation: 3.5, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, {t_c2:.2f});

    const s8 = document.getElementById("v08-shield-orb").getContext("2d");
    const p8 = {{ t: 0 }};
    tl.to(p8, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p8.t;
        s8.clearRect(0, 0, 330, 330);
        const sc = 1 + Math.sin(t * 3.8) * 0.05;
        s8.save(); s8.translate(165, 165); s8.scale(sc, sc);
        s8.beginPath(); s8.arc(0, 0, 130, 0, Math.PI * 2); s8.fillStyle = "rgba(16,185,129,0.20)"; s8.fill();
        s8.fillStyle = "#10b981"; s8.strokeStyle = "#ffffff"; s8.lineWidth = 6;
        s8.beginPath(); s8.moveTo(0, -105); s8.lineTo(92, -62); s8.quadraticCurveTo(88, 58, 0, 112); s8.quadraticCurveTo(-88, 58, -92, -62); s8.closePath();
        s8.fill(); s8.stroke();
        s8.fillStyle = "#ffffff"; s8.font = "900 72px Montserrat, sans-serif"; s8.fillText("♥", -26, 28);
        s8.restore();
      }}
    }}, 0);"""
    sfx = [("sfx_whoosh_soft.mp3", hook_end, 0.16), ("sfx_pop_clean.mp3", hook_end + 0.24, 0.17), ("sfx_pop_clean.mp3", t_c2, 0.17)]
    return wrap_stage_template(dur, css, "yellow_black", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #09: CÒN YÊU VỢ SAO ÍT MUỐN GẦN GŨI (cf. reel_09: ECG Stress Wave + Warm Dialogue Cards)
# ═══════════════════════════════════════════════════════════════════════════
def build_v09(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 370))
    kw_top = max(34, hy - 138)
    sh_y = max(125, hy - 20)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v09-ecg-cvs {{ position: absolute; left: 0; top: {max(50, sh_y - 40)}px; width: 1080px; height: 420px; opacity: 0; }}
    #v09-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v09-k {{ font-family: Georgia, serif; font-weight: 700; font-style: italic; font-size: 88px; line-height: 1.04; color: #e11d48; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <canvas id="v09-ecg-cvs" width="1080" height="420"></canvas>
    <div id="v09-kw"><div class="v09-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v09-k" style="color:#0f172a">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v09-c1" class="sh-card" style="left: 26px; top: {sh_y + 20}px; border-color:#f43f5e">
      <img src="assets/images/broll_01.jpg" alt="Talk" />
      <span class="sh-badge" style="background:#e11d48">💬 ĐỪNG IM LẶNG</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v09-c2" class="sh-card" style="right: 26px; top: {sh_y + 20}px; border-color:#0284c7">
      <img src="assets/images/broll_02.jpg" alt="Check" />
      <span class="sh-badge">🩺 KHÁM NỘI TIẾT</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    c_start = round(max(8.2, kw_e + 0.25), 2)
    js = f"""
    {common_js}
    tl.to("#v09-ecg-cvs", {{ opacity: 1, duration: 0.35 }}, {hook_end + 0.10:.2f});
    tl.fromTo("#v09-kw", {{ y: 20, filter: "blur(14px)", opacity: 0 }}, {{ y: 0, filter: "blur(0px)", opacity: 1, duration: 0.24, immediateRender: false }}, {kw_s:.2f});
    tl.to("#v09-kw", {{ opacity: 0, duration: 0.16 }}, {kw_e - 0.15:.2f});

    tl.fromTo("#v09-c1", {{ x: -180, rotation: -6, opacity: 0 }}, {{ x: 0, rotation: -3, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {c_start:.2f});
    tl.fromTo("#v09-c2", {{ x: 180, rotation: 6, opacity: 0 }}, {{ x: 0, rotation: 3, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {c_start + 2.1:.2f});

    const e9 = document.getElementById("v09-ecg-cvs").getContext("2d");
    const p9 = {{ t: 0 }};
    tl.to(p9, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p9.t;
        e9.clearRect(0, 0, 1080, 420);
        // Animated Stress ECG Wave behind both shoulders (cf. reel_09@4.8s!)
        e9.strokeStyle = "#10b981"; e9.lineWidth = 6; e9.beginPath();
        for (let x = 40; x <= 1040; x += 8) {{
          const ph = (x * 0.025) - t * 5.0;
          const spike = Math.exp(-Math.pow(((x + t * 220) % 260) - 130, 2) / 180) * 85 * Math.sin(ph * 4);
          const y = 210 + Math.sin(ph) * 18 - spike;
          if (x === 40) e9.moveTo(x, y); else e9.lineTo(x, y);
        }}
        e9.stroke();
      }}
    }}, 0);"""
    sfx = [("sfx_chime_warm.mp3", hook_end + 0.15, 0.16), ("sfx_pop_clean.mp3", c_start, 0.17), ("sfx_pop_clean.mp3", c_start + 2.1, 0.17)]
    return wrap_stage_template(dur, css, "yellow_black", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #10: VỪA XUẤT RA ĐÃ MỀM (cf. reel_10: Cyan Physiology Monitor Screen + Outlined 10 + Mint Italic)
# ═══════════════════════════════════════════════════════════════════════════
def build_v10(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 310))
    kw_top = max(28, hy - 132)
    sh_y = max(115, hy)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v10-monitor {{
      position: absolute; right: 24px; top: {sh_y}px; width: 448px; height: 396px;
      border-radius: 30px; background: linear-gradient(150deg, rgba(8,28,44,0.94), rgba(12,52,72,0.90));
      border: 3.5px solid #22d3ee; box-shadow: 0 20px 46px rgba(8,47,73,0.34); opacity: 0; overflow: hidden;
    }}
    #v10-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v10-k {{ font-family: "Anton", sans-serif; font-size: 92px; line-height: 1.02; color: #0891b2; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <div id="v10-monitor"><canvas id="v10-mon-cvs" width="448" height="396"></canvas></div>
    <div id="v10-kw"><div class="v10-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v10-k" style="color:#059669">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v10-c1" class="sh-card" style="left: 24px; top: {sh_y + 15}px; border-color:#ef4444">
      <img src="assets/images/broll_01.jpg" alt="Early" />
      <span class="sh-badge" style="background:#dc2626">⚠ MỀM GIỮA CHỪNG</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>"""

    js = f"""
    {common_js}
    tl.fromTo("#v10-monitor", {{ x: 170, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, {hook_end + 0.14:.2f});
    tl.fromTo("#v10-kw", {{ scale: 0.88, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v10-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});

    tl.fromTo("#v10-c1", {{ x: -180, rotation: -6, opacity: 0 }}, {{ x: 0, rotation: -3, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, 8.15);

    const m10 = document.getElementById("v10-mon-cvs").getContext("2d");
    const p10 = {{ t: 0 }};
    tl.to(p10, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p10.t;
        m10.clearRect(0, 0, 448, 396);
        m10.strokeStyle = "rgba(34,211,238,0.18)"; m10.lineWidth = 1.5;
        for (let g = 50; g < 380; g += 55) {{ m10.beginPath(); m10.moveTo(28, g); m10.lineTo(420, g); m10.stroke(); }}
        // Green Normal Post-Ejaculation Recovery Curve vs Red Early Loss Curve (cf. reel_10@8.2s!)
        const drawW = Math.min(370, Math.max(40, (t - 3.2) * 85));
        m10.strokeStyle = "#34d399"; m10.lineWidth = 7; m10.beginPath();
        for (let x = 0; x <= drawW; x += 6) {{
          const y = x < 210 ? 95 : 95 + (x - 210) * 1.15;
          if (x === 0) m10.moveTo(38 + x, y); else m10.lineTo(38 + x, Math.min(295, y));
        }}
        m10.stroke();
        if (t >= 8.0) {{
          m10.strokeStyle = "#fb7185"; m10.lineWidth = 6; m10.setLineDash([12, 8]); m10.beginPath();
          m10.moveTo(38, 110); m10.lineTo(135, 295); m10.lineTo(395, 295); m10.stroke(); m10.setLineDash([]);
        }}
        m10.fillStyle = "#6ee7b7"; m10.font = "800 21px BeVN, sans-serif"; m10.fillText("✔ MỀM SAU XUẤT = BÌNH THƯỜNG", 36, 48);
        m10.fillStyle = "#fda4af"; m10.fillText("⚠ MỀM SỚM 2–3P = CẦN KHÁM", 36, 358);
      }}
    }}, 0);"""
    sfx = [("sfx_pop_clean.mp3", hook_end + 0.16, 0.17), ("sfx_ping_glass.mp3", kw_s, 0.17), ("sfx_pop_clean.mp3", 8.18, 0.17)]
    return wrap_stage_template(dur, css, "mint_italic", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #11: 4 TÁC HẠI XEM PHIM NHẠY CẢM (cf. reel_11: Clock -> ED Card -> Twin 3D Ice Cubes "BỊ TRƠ" -> Thermometer)
# ═══════════════════════════════════════════════════════════════════════════
def build_v11(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    hy = int(plan.get("head_top_y", 300))
    sh_y = max(115, hy)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v11-fx-cvs {{ position: absolute; left: 0; top: {max(30, sh_y - 50)}px; width: 1080px; height: 540px; }}
    """
    behind = f"""
    <canvas id="v11-fx-cvs" width="1080" height="540"></canvas>
    <div id="v11-c1" class="sh-card" style="left: 26px; top: {sh_y + 20}px; border-color:#dc2626">
      <img src="assets/images/broll_01.jpg" alt="ED" />
      <span class="sh-badge" style="background:#dc2626">02 • RỐI LOẠN CƯƠNG</span>
      <div class="sh-head">{html.escape(c1['head'])}</div>
      <div class="sh-desc">{html.escape(c1['desc'])}</div>
    </div>
    <div id="v11-c2" class="sh-card" style="right: 26px; top: {sh_y + 20}px; border-color:#059669">
      <img src="assets/images/broll_02.jpg" alt="Adjust" />
      <span class="sh-badge" style="background:#059669">✔ ĐIỀU CHỈNH SỚM</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    # Spoken cues in v11: 1@4.34 (thức khuya), 2@5.96 (rối loạn cương), 3@7.08 (bị trơ), 4@9.54 (khó xuất), close@12.16
    js = f"""
    {common_js}
    tl.fromTo("#v11-c1", {{ x: -180, rotation: -6, opacity: 0 }}, {{ x: 0, rotation: -3, opacity: 1, duration: 0.28, ease: "back.out(1.6)", immediateRender: false }}, 5.85);
    tl.to("#v11-c1", {{ x: -160, opacity: 0, duration: 0.20 }}, 7.05);
    tl.fromTo("#v11-c2", {{ x: 180, rotation: 6, opacity: 0 }}, {{ x: 0, rotation: 3, opacity: 1, duration: 0.30, ease: "back.out(1.6)", immediateRender: false }}, 11.90);

    const f11 = document.getElementById("v11-fx-cvs").getContext("2d");
    const p11 = {{ t: 0 }};
    tl.to(p11, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p11.t;
        f11.clearRect(0, 0, 1080, 540);
        if (t >= 4.1 && t < 5.95) {{
          // Act 1: Spinning Midnight Clock behind right shoulder (cf. reel_11@4.8s!)
          f11.save(); f11.translate(875, 225);
          f11.fillStyle = "rgba(255,255,255,0.92)"; f11.strokeStyle = "#dc2626"; f11.lineWidth = 8;
          f11.beginPath(); f11.arc(0, 0, 118, 0, Math.PI * 2); f11.fill(); f11.stroke();
          f11.strokeStyle = "#0f172a"; f11.lineWidth = 7; f11.lineCap = "round";
          f11.beginPath(); f11.moveTo(0, 0); f11.lineTo(Math.cos(t * 9) * 82, Math.sin(t * 9) * 82); f11.stroke();
          f11.beginPath(); f11.moveTo(0, 0); f11.lineTo(Math.cos(t * 1.5) * 54, Math.sin(t * 1.5) * 54); f11.stroke();
          f11.restore();
          f11.fillStyle = "#b91c1c"; f11.font = "900 30px Montserrat, sans-serif"; f11.fillText("01 • THỨC KHUYA", 735, 78);
        }} else if (t >= 7.05 && t < 9.55) {{
          // Act 3: Twin Frosted 3D Ice Cubes "BỊ TRƠ" behind Left & Right of Head (exact match to reel_11@8.2s!)
          [[190, 225], [890, 225]].forEach(([ix, iy], idx) => {{
            f11.save(); f11.translate(ix, iy); f11.rotate(idx === 0 ? -0.08 : 0.08);
            const ig = f11.createLinearGradient(-110, -110, 110, 110);
            ig.addColorStop(0, "rgba(224,242,254,0.95)"); ig.addColorStop(0.5, "rgba(125,211,252,0.88)"); ig.addColorStop(1, "rgba(2,132,199,0.85)");
            f11.fillStyle = ig; f11.strokeStyle = "#ffffff"; f11.lineWidth = 6;
            f11.beginPath(); f11.roundRect(-115, -115, 230, 230, 34); f11.fill(); f11.stroke();
            f11.fillStyle = "#0c4a6e"; f11.font = "900 34px Montserrat, sans-serif";
            f11.fillText(idx === 0 ? "BỊ TRƠ" : "GIẢM LỬA", -82, 12);
            f11.restore();
          }});
        }} else if (t >= 9.55 && t < 11.95) {{
          // Act 4: Cooling Thermometer left + Fading Heart right (exact match to reel_11@11.2s!)
          f11.fillStyle = "#ffffff"; f11.strokeStyle = "#0284c7"; f11.lineWidth = 6;
          f11.beginPath(); f11.roundRect(145, 95, 56, 220, 28); f11.fill(); f11.stroke();
          f11.beginPath(); f11.arc(173, 325, 48, 0, Math.PI * 2); f11.fillStyle = "#38bdf8"; f11.fill(); f11.stroke();
          f11.fillStyle = "#0369a1"; f11.font = "900 28px Montserrat, sans-serif"; f11.fillText("04 • KHÓ XUẤT", 68, 70);
        }}
      }}
    }}, 0);"""
    sfx = [("sfx_click_soft.mp3", 4.20, 0.16), ("sfx_pop_clean.mp3", 5.88, 0.17), ("sfx_ping_glass.mp3", 7.12, 0.18), ("sfx_pop_clean.mp3", 11.92, 0.17)]
    return wrap_stage_template(dur, css, "white_red", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #12: UỐNG BIA TRƯỚC KHI GẦN GŨI (cf. reel_12: Dark-Cyan Neural HUD + Draining Stamina -> Beer Mug ✕ + Clock)
# ═══════════════════════════════════════════════════════════════════════════
def build_v12(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    kw_s, kw_e = plan["kw_start"], plan["kw_end"]
    hy = int(plan.get("head_top_y", 350))
    kw_top = max(34, hy - 136)
    sh_y = max(120, hy - 15)
    c1, c2 = sp["broll_cards"][0], sp["broll_cards"][1]
    fg_html, common_js = render_hook_and_subs(sp, plan)

    css = f"""
    #v12-hud-cvs {{ position: absolute; left: 0; top: {max(40, sh_y - 45)}px; width: 1080px; height: 520px; opacity: 0; }}
    #v12-kw {{ position: absolute; left: 24px; top: {kw_top}px; width: 1032px; text-align: center; opacity: 0; }}
    .v12-k {{ font-family: "Anton", sans-serif; font-size: 94px; line-height: 1.03; color: #dc2626; -webkit-text-stroke: 9px #ffffff; paint-order: stroke fill; }}
    """
    behind = f"""
    <canvas id="v12-hud-cvs" width="1080" height="520"></canvas>
    <div id="v12-kw"><div class="v12-k">{html.escape(sp['behind_kw_lines'][0])}</div><div class="v12-k" style="color:#0284c7">{html.escape(sp['behind_kw_lines'][1])}</div></div>
    <div id="v12-c2" class="sh-card" style="right: 26px; top: {sh_y + 15}px; border-color:#10b981">
      <img src="assets/images/broll_02.jpg" alt="Healthy" />
      <span class="sh-badge" style="background:#059669">✔ RÈN NHỊP THỞ</span>
      <div class="sh-head">{html.escape(c2['head'])}</div>
      <div class="sh-desc">{html.escape(c2['desc'])}</div>
    </div>"""

    c2_t = round(max(9.5, kw_e + 0.35), 2)
    js = f"""
    {common_js}
    tl.to("#v12-hud-cvs", {{ opacity: 1, duration: 0.32 }}, {hook_end + 0.08:.2f});
    tl.fromTo("#v12-kw", {{ scale: 0.88, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "back.out(1.8)", immediateRender: false }}, {kw_s:.2f});
    tl.to("#v12-kw", {{ opacity: 0, duration: 0.18 }}, {kw_e - 0.16:.2f});
    tl.fromTo("#v12-c2", {{ x: 180, rotation: 6, opacity: 0 }}, {{ x: 0, rotation: 3, opacity: 1, duration: 0.32, ease: "back.out(1.6)", immediateRender: false }}, {c2_t:.2f});

    const h12 = document.getElementById("v12-hud-cvs").getContext("2d");
    const p12 = {{ t: 0 }};
    tl.to(p12, {{
      t: {dur:.2f}, duration: {dur:.2f}, ease: "none",
      onUpdate: () => {{
        const t = p12.t;
        h12.clearRect(0, 0, 1080, 520);
        // Left Foaming Golden Beer Mug with Red X (cf. reel_12@11.2s!)
        h12.save(); h12.translate(185, 240);
        h12.fillStyle = "rgba(255,255,255,0.92)"; h12.strokeStyle = "#f59e0b"; h12.lineWidth = 6;
        h12.beginPath(); h12.roundRect(-78, -95, 156, 205, 22); h12.fill(); h12.stroke();
        h12.fillStyle = "#fbbf24"; h12.beginPath(); h12.roundRect(-68, -45, 136, 145, 14); h12.fill();
        // Foam bubbles on top
        [[-45,-95,28],[0,-105,34],[45,-95,28]].forEach(([bx,by,br]) => {{ h12.fillStyle="#ffffff"; h12.beginPath(); h12.arc(bx,by,br,0,Math.PI*2); h12.fill(); }});
        h12.fillStyle = "#dc2626"; h12.beginPath(); h12.arc(68, -82, 36, 0, Math.PI * 2); h12.fill();
        h12.fillStyle = "#ffffff"; h12.font = "900 42px Montserrat, sans-serif"; h12.fillText("✕", 48, -67);
        h12.restore();

        // Right Draining Stamina Tank (before c2_t)
        if (t < {c2_t:.2f}) {{
          const pr = Math.max(0, Math.min(1, (t - 3.0) / 4.8));
          const bars = Math.max(1, Math.round(5 - pr * 4));
          const col = bars >= 4 ? "#10b981" : bars >= 2 ? "#f59e0b" : "#ef4444";
          h12.save(); h12.translate(875, 235);
          h12.fillStyle = "rgba(15,23,42,0.88)"; h12.strokeStyle = col; h12.lineWidth = 6;
          h12.beginPath(); h12.roundRect(-95, -135, 190, 270, 26); h12.fill(); h12.stroke();
          for (let b = 0; b < bars; b++) {{
            h12.fillStyle = col; h12.beginPath(); h12.roundRect(-72, 82 - b * 44, 144, 32, 8); h12.fill();
          }}
          h12.fillStyle = "#ffffff"; h12.font = "800 22px BeVN, sans-serif"; h12.fillText("PHẢN XẠ CƯƠNG", -84, -152);
          h12.restore();
        }}
      }}
    }}, 0);"""
    sfx = [("sfx_pop_clean.mp3", hook_end + 0.12, 0.17), ("sfx_ping_glass.mp3", kw_s, 0.17), ("sfx_pop_clean.mp3", c2_t, 0.17)]
    return wrap_stage_template(dur, css, "white_red", behind, fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #13: 5 DẤU HIỆU MẤT KIỂM SOÁT (cf. reel_13: 3D Curved 5-Card Carousel Orbiting Behind Her Head!)
# ═══════════════════════════════════════════════════════════════════════════
def build_v13(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    hy = int(plan.get("head_top_y", 340))
    sh_y = max(115, hy - 15)
    fg_html, common_js = render_hook_and_subs(sp, plan)

    signs = [
        ("01", "LÀM LIÊN TỤC DÙ MỆT", "Kiệt sức vẫn khó dừng", "#ef4444", 3.45),
        ("02", "THỨC KHUYA XEM", "Mất ngủ, rối loạn nhịp", "#f97316", 5.26),
        ("03", "MẤT TẬP TRUNG", "Xao nhãng công việc", "#eab308", 6.65),
        ("04", "ĐÒI MỨC CÀNG MẠNH", "Tăng ngưỡng kích thích", "#8b5cf6", 8.22),
        ("05", "ÍT CẢM XÚC THẬT", "Gặp chuyên gia hỗ trợ!", "#06b6d4", 10.72),
    ]
    css = f"""
    .car-card {{
      position: absolute; top: {sh_y + 10}px; width: 356px; padding: 20px 22px; border-radius: 28px;
      background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(30,41,59,0.88));
      border: 4px solid #38bdf8; box-shadow: 0 20px 46px rgba(15,23,42,0.28);
      opacity: 0; will-change: transform, opacity;
    }}
    .cc-num {{ display:inline-block; padding:6px 16px; border-radius:999px; font-family:"Montserrat",sans-serif; font-size:22px; color:#fff; margin-bottom:10px; }}
    .cc-h {{ font-family:"BeVN",sans-serif; font-size:29px; line-height:1.15; color:#ffffff; }}
    .cc-s {{ margin-top:6px; font-family:"BeVN",sans-serif; font-size:21px; color:#cbd5e1; }}
    """
    cards_html, cards_js = [], []
    for idx_i, (num, htxt, stxt, col, cue_t) in enumerate(signs, 1):
        side_style = "right: 26px;" if idx_i % 2 == 1 else "left: 26px;"
        from_x = 220 if idx_i % 2 == 1 else -220
        rot = 4 if idx_i % 2 == 1 else -4
        cards_html.append(f"""
    <div id="cc-{idx_i}" class="car-card" style="{side_style} border-color:{col}">
      <div class="cc-num" style="background:{col}">DẤU HIỆU {num}/05</div>
      <div class="cc-h">{htxt}</div>
      <div class="cc-s">{stxt}</div>
    </div>""")
        cards_js.append(
            f'tl.fromTo("#cc-{idx_i}", {{ x: {from_x}, scale: 0.82, rotationY: {rot * 6}, opacity: 0 }}, '
            f'{{ x: 0, scale: 1, rotationY: 0, rotation: {rot}, opacity: 1, duration: 0.30, ease: "back.out(1.7)", immediateRender: false }}, {cue_t:.2f});'
        )
        if idx_i <= 3:
            next_same_side_t = signs[idx_i + 1][4] - 0.18
            cards_js.append(f'tl.to("#cc-{idx_i}", {{ y: -60, scale: 0.86, opacity: 0, duration: 0.22 }}, {next_same_side_t:.2f});')

    js = f"""
    {common_js}
    {chr(10).join(cards_js)}
    """
    sfx = [("sfx_pop_clean.mp3", s[4], 0.16) for s in signs]
    return wrap_stage_template(dur, css, "white_red", "\n".join(cards_html), fg_html, js), sfx


# ═══════════════════════════════════════════════════════════════════════════
# #14: 5 THÓI QUEN GIẢM PHONG ĐỘ (cf. reel_14: 5 Flying Habit Cards + Beer Mugs + Cigarette Vessel)
# ═══════════════════════════════════════════════════════════════════════════
def build_v14(sp, plan):
    dur, hook_end = plan["dur"], plan["hook_end"]
    hy = int(plan.get("head_top_y", 360))
    sh_y = max(120, hy - 15)
    fg_html, common_js = render_hook_and_subs(sp, plan)

    habits = [
        ("01", "🌙 THỨC KHUYA", "Suy giảm nội tiết nam", "#ef4444", 2.76, "left"),
        ("02", "🍻 RƯỢU BIA NHIỀU", "Cương kém ổn định", "#f59e0b", 4.16, "right"),
        ("03", "🚬 HÚT THUỐC LÁ", "Xơ hẹp mạch máu nuôi", "#dc2626", 6.62, "left"),
        ("04", "🪑 NGỒI NHIỀU LÌ", "Trì trệ tuần hoàn chậu", "#0284c7", 8.38, "right"),
        ("05", "⚡ CĂNG THẲNG DÀI", "Thay đổi sớm ngay nhé!", "#8b5cf6", 10.62, "left"),
    ]
    css = f"""
    .hb-card {{
      position: absolute; top: {sh_y + 14}px; width: 364px; padding: 20px 22px; border-radius: 28px;
      background: rgba(255,255,255,0.95); border: 4px solid #0f172a;
      box-shadow: 0 20px 44px rgba(15,23,42,0.22); opacity: 0;
    }}
    .hb-top {{ font-family:"Montserrat",sans-serif; font-size:21px; color:#fff; display:inline-block; padding:5px 15px; border-radius:999px; margin-bottom:8px; }}
    .hb-h {{ font-family:"BeVN",sans-serif; font-size:30px; color:#0f172a; }}
    .hb-s {{ margin-top:4px; font-family:"BeVN",sans-serif; font-size:21px; color:#475569; }}
    """
    h_html, h_js = [], []
    for idx_i, (num, htxt, stxt, col, ct, side) in enumerate(habits, 1):
        pos = "left: 26px;" if side == "left" else "right: 26px;"
        fx = -200 if side == "left" else 200
        rot = -3.5 if side == "left" else 3.5
        img_el = '<img src="assets/images/broll_01.jpg" style="width:100%;height:175px;border-radius:16px;object-fit:cover;margin-bottom:8px" />' if idx_i == 1 else (
            '<img src="assets/images/broll_02.jpg" style="width:100%;height:175px;border-radius:16px;object-fit:cover;margin-bottom:8px" />' if idx_i == 4 else ''
        )
        h_html.append(f"""
    <div id="hb-{idx_i}" class="hb-card" style="{pos} border-color:{col}">
      {img_el}
      <div class="hb-top" style="background:{col}">THÓI QUEN {num}</div>
      <div class="hb-h">{htxt}</div>
      <div class="hb-s">{stxt}</div>
    </div>""")
        h_js.append(
            f'tl.fromTo("#hb-{idx_i}", {{ x: {fx}, rotation: {rot * 3}, opacity: 0 }}, '
            f'{{ x: 0, rotation: {rot}, opacity: 1, duration: 0.30, ease: "back.out(1.7)", immediateRender: false }}, {ct:.2f});'
        )
        if idx_i <= 3:
            hide_t = habits[idx_i + 1][4] - 0.18
            h_js.append(f'tl.to("#hb-{idx_i}", {{ y: -50, opacity: 0, duration: 0.20 }}, {hide_t:.2f});')

    js = f"""
    {common_js}
    {chr(10).join(h_js)}
    """
    sfx = [("sfx_pop_clean.mp3", h[4], 0.16) for h in habits]
    return wrap_stage_template(dur, css, "white_black", "\n".join(h_html), fg_html, js), sfx
