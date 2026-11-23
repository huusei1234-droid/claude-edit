import os
import sys
import re
import json
import html
import subprocess
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3_styles_and_helpers import (
    PROJ, COMP_DIR, DC_PATH, FONT_FACES_CSS, SHARED_LUXURY_CSS,
    f_time, bullion_text, write_comp
)
from v3_slides_part1 import build_slides_part1
from v3_slides_part2 import build_slides_part2

# 1. Build all 12 warm cinema slides + reviews-broll
build_slides_part1()
build_slides_part2()

# =========================================================================
# 2. OVERLAYS & HUD COMPOSITION (overlays-hud.html)
#    - Grand Intro Hero Lockup (100% Vietnamese, Bold & Larger)
#    - REMOVED Top-Right Corner Logo per User Feedback (Image 4)
#    - Dual Celebrity KOL Name Tags (Larger & Bolder)
#    - Large Frameless Feathered Broadcast Section Banners (Image 3 Fix!)
#    - Grand End-Card Footer Lockup (100% Vietnamese, Larger)
# =========================================================================
HUD_CARDS = [
    ("hud-koc",     12.57,  3.75, "UY TÍN THƯƠNG HIỆU",        "ĐÔNG ĐẢO KOC & KOL TIN CHỌN",            "Hài lòng khách địa phương lẫn du khách quốc tế"),
    ("hud-f1",      16.45, 10.15, "KHÔNG GIAN TẦNG 01",         "SẢNH ĐÓN TIẾP SANG TRỌNG",               "Nhân viên chào đón niềm nở · Ghế chờ êm ái"),
    ("hud-menu",    26.75,  8.50, "DỊCH VỤ MINH BẠCH",          "BẢNG GIÁ RÕ RÀNG · TƯ VẤN TẬN TÂM",      "Đa dạng gói Combo dễ dàng lựa chọn theo nhu cầu"),
    ("hud-cutzone", 42.75, 10.25, "KHU VỰC TẠO KIỂU",           "KHU CẮT TÓC CHUẨN PHONG ĐỘ",             "Gương sáng · Ghế xịn · Ngồi vào yên tâm, đứng dậy là bảnh"),
    ("hud-priv",    70.35,  9.78, "KHÔNG GIAN RIÊNG TƯ",        "HỆ THỐNG PHÒNG RIÊNG PHỤC VỤ 1 : 1",     "Kéo rèm riêng biệt · Không ồn · Không phiền · Chỉ có thư giãn"),
    ("hud-staff",  136.85, 15.65, "ĐỘI NGŨ KỸ THUẬT VIÊN",      "TAY NGHỀ CHUẨN · TÁC PHONG CHỈNH TỀ",    "Không cắt cho nhanh mà cắt cho chuẩn · Tận tâm chu đáo"),
    ("hud-rev1",   152.80, 19.15, "KHÁCH HÀNG ĐÁNH GIÁ 10/10",  "TRẢI NGHIỆM THỰC TẾ CÙNG GIA ĐÌNH",      "“Không gian sang trọng sạch sẽ · Cả gia đình đều mê!”"),
    ("hud-rev2",   172.10, 16.65, "KHÁCH HÀNG ĐÁNH GIÁ 10/10",  "PHỤC VỤ TẬN TÌNH CHUẨN THƯỢNG ĐẾ",       "“Cắt tóc cực ưng ý · Chăm sóc chu đáo từng chi tiết!”"),
    ("hud-rev3",   188.90, 23.10, "ANH NAM CHẤM 10 / 10",       "KHÁCH HÀNG NAM THÂN THIẾT",              "“Tái tạo năng lượng · Tút lại vẻ đẹp trai & phong độ!”"),
    ("hud-rev4",   212.15, 43.45, "KOL TRẢI NGHIỆM THỰC TẾ",    "HƯNG HUỲNH & HUY · COMBO VIP 5 SAO",     "“Ráy tai nhẹ quá ngủ thiếp đi luôn · Làm xong người nhẹ hẳn!”"),
]

CLAPPER_SVG = """<svg class="kol-clap" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" data-layout-ignore>
  <rect x="5" y="17" width="38" height="25" rx="3" stroke="#F4C867" stroke-width="2.6" fill="rgba(244,200,103,0.10)"/>
  <path d="M6 17L10 7H41L38 17H6Z" stroke="#F4C867" stroke-width="2.6" stroke-linejoin="round" fill="rgba(244,200,103,0.18)"/>
  <line x1="15" y1="7" x2="12" y2="17" stroke="#F4C867" stroke-width="2.6"/>
  <line x1="25" y1="7" x2="22" y2="17" stroke="#F4C867" stroke-width="2.6"/>
  <line x1="35" y1="7" x2="32" y2="17" stroke="#F4C867" stroke-width="2.6"/>
  <polygon points="21,24 21,35 30,29.5" fill="#F4C867"/>
</svg>"""

GROUP_SVG = """<svg style="width:22px;height:22px;vertical-align:-3px;margin-right:6px;" viewBox="0 0 24 24" fill="#F4C867" xmlns="http://www.w3.org/2000/svg" data-layout-ignore>
  <circle cx="9" cy="8" r="3.5"/><path d="M3 19c0-3 2.8-5 6-5s6 2 6 5v1H3v-1z"/>
  <circle cx="17" cy="9" r="2.8"/><path d="M15.5 14.3c2.6.3 5.5 1.9 5.5 4.7v1h-4.5v-1c0-1.8-.6-3.4-1.8-4.7h.8z"/>
</svg>"""

def kol_tag_html(dom_id: str, left_px: int, top_px: int, width_px: int, name_txt: str, role_html: str) -> str:
    return f"""
      <div id="{dom_id}" class="kol-tag-wrap" style="left: {left_px}px; top: {top_px}px; width: {width_px}px;" data-layout-allow-overlap>
        <div class="kol-pill-top"><span>KOL NỔI TIẾNG</span></div>
        <div class="kol-plate">
          <div class="kol-star tl" data-layout-ignore></div>
          <div class="kol-star br" data-layout-ignore></div>
          <div class="kol-inner">
            {CLAPPER_SVG}
            <div class="kol-txt">
              <div class="kol-name">{html.escape(name_txt)}</div>
              <div class="kol-role">{role_html}</div>
            </div>
          </div>
        </div>
      </div>"""

hud_html_parts = []
hud_js_parts = []
for hid, hst, hdur, hkicker, htitle, hsub in HUD_CARDS:
    exit_t = hst + hdur - 0.46
    hud_html_parts.append(f"""
    <div id="{hid}" class="clip wh-fcp-host" data-start="{hst:.6f}" data-duration="{hdur:.6f}" data-track-index="2">
      <div id="{hid}-vp" class="wh-fcp-viewport">
        <div id="{hid}-bg" class="wh-fcp-bg" data-layout-ignore></div>
        <div id="{hid}-gold-run" class="wh-fcp-gold-run" data-layout-ignore></div>
        <div id="{hid}-bar" class="wh-fcp-bar" data-layout-ignore></div>
        <div class="wh-fcp-body">
          <div class="wh-fcp-mask"><div id="{hid}-k" class="wh-fcp-kicker">{html.escape(hkicker)}</div></div>
          <div id="{hid}-rule" class="wh-fcp-rule" data-layout-ignore></div>
          <div class="wh-fcp-mask"><div id="{hid}-t" class="wh-fcp-title">{html.escape(htitle)}</div></div>
          <div class="wh-fcp-mask"><div id="{hid}-s" class="wh-fcp-sub">{html.escape(hsub)}</div></div>
        </div>
      </div>
    </div>""")
    hud_js_parts.append(f"""
    // Final Cut Pro Kinetic Counter-Slide Reveal: Dark plate sweeps RIGHT->LEFT, Gold bar/streak runs LEFT->RIGHT, Masked text slides!
    tl.fromTo("#{hid}-bg", {{ xPercent: 103 }}, {{ xPercent: 0, duration: 0.42, ease: "expo.out" }}, {hst:.4f});
    tl.fromTo("#{hid}-gold-run", {{ xPercent: -115, opacity: 1 }}, {{ xPercent: 245, opacity: 0.92, duration: 0.56, ease: "power3.inOut" }}, {hst + 0.06:.4f});
    tl.fromTo("#{hid}-bar", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.34, ease: "expo.out" }}, {hst + 0.08:.4f});
    tl.fromTo("#{hid}-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.46, ease: "expo.out" }}, {hst + 0.14:.4f});
    tl.fromTo("#{hid}-k", {{ xPercent: -106, opacity: 0 }}, {{ xPercent: 0, opacity: 1, duration: 0.40, ease: "expo.out" }}, {hst + 0.15:.4f});
    tl.fromTo("#{hid}-t", {{ yPercent: 120 }}, {{ yPercent: 0, duration: 0.46, ease: "expo.out" }}, {hst + 0.21:.4f});
    tl.fromTo("#{hid}-s", {{ yPercent: 120, opacity: 0 }}, {{ yPercent: 0, opacity: 1, duration: 0.44, ease: "power3.out" }}, {hst + 0.29:.4f});

    // Crisp Final Cut Pro Reverse Tuck Exit
    tl.fromTo("#{hid}-s", {{ yPercent: 0, opacity: 1 }}, {{ yPercent: 120, opacity: 0, duration: 0.24, ease: "power2.in", immediateRender: false }}, {exit_t:.4f});
    tl.fromTo("#{hid}-t", {{ yPercent: 0 }}, {{ yPercent: -120, duration: 0.26, ease: "power2.in", immediateRender: false }}, {exit_t + 0.04:.4f});
    tl.fromTo("#{hid}-k", {{ xPercent: 0, opacity: 1 }}, {{ xPercent: -106, opacity: 0, duration: 0.24, ease: "power2.in", immediateRender: false }}, {exit_t + 0.06:.4f});
    tl.fromTo("#{hid}-rule", {{ scaleX: 1 }}, {{ scaleX: 0, duration: 0.24, ease: "power2.in", immediateRender: false }}, {exit_t + 0.08:.4f});
    tl.fromTo("#{hid}-bar", {{ scaleY: 1 }}, {{ scaleY: 0, duration: 0.26, ease: "power2.in", immediateRender: false }}, {exit_t + 0.12:.4f});
    tl.fromTo("#{hid}-bg", {{ xPercent: 0 }}, {{ xPercent: 104, duration: 0.34, ease: "power3.in", immediateRender: false }}, {exit_t + 0.10:.4f});""")

write_comp("overlays-hud.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}
    /* Grand Intro Hero Lockup (0.03 - 5.00s) */
    .wh-intro-host {{
      position: absolute;
      inset: 0;
      z-index: 25;
      pointer-events: none;
    }}
    .wh-intro-scrim {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 320px;
      background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(10,7,5,0.86) 100%);
    }}
    .wh-intro-stack {{
      position: absolute;
      left: 80px;
      right: 80px;
      bottom: 48px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }}
    .wh-intro-plaque {{
      margin-top: 12px;
      padding: 14px 52px;
      border-radius: 10px;
      background: linear-gradient(180deg, rgba(32, 22, 15, 0.94) 0%, rgba(15, 11, 8, 0.96) 100%);
      border: 1.5px solid rgba(244, 200, 103, 0.78);
      box-shadow: 0 0 28px rgba(244, 196, 86, 0.28), 0 14px 36px rgba(0,0,0,0.88);
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      font-size: 31px;
      letter-spacing: 0.14em;
      color: #FFF5D6;
      text-transform: uppercase;
    }}

    /* Slanted KOL Name Tag System (Larger & Bolder) */
    .kol-host {{
      position: absolute;
      inset: 0;
      z-index: 27;
      pointer-events: none;
    }}
    .kol-tag-wrap {{
      position: absolute;
      pointer-events: none;
    }}
    .kol-pill-top {{
      display: inline-block;
      margin-left: 34px;
      margin-bottom: -8px;
      position: relative;
      z-index: 3;
      padding: 6px 24px;
      border-radius: 6px;
      transform: skewX(-14deg);
      background: linear-gradient(180deg, #FFE89C 0%, #DF9F2B 100%);
      box-shadow: 0 6px 16px rgba(0,0,0,0.68);
    }}
    .kol-pill-top span {{
      display: inline-block;
      transform: skewX(14deg);
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      font-size: 17px;
      letter-spacing: 0.08em;
      color: #15100A;
      text-transform: uppercase;
    }}
    .kol-plate {{
      position: relative;
      padding: 18px 30px 17px 26px;
      border-radius: 12px;
      transform: skewX(-14deg);
      background: linear-gradient(160deg, rgba(34, 25, 18, 0.96) 0%, rgba(14, 11, 9, 0.98) 100%);
      border: 2px solid #F4C867;
      box-shadow:
        0 0 26px rgba(244, 200, 103, 0.40),
        0 18px 40px rgba(0, 0, 0, 0.88);
    }}
    .kol-star {{
      position: absolute;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #FFF8DC;
      box-shadow: 0 0 14px 5px rgba(255, 218, 115, 0.95);
    }}
    .kol-star.tl {{ right: 14px; top: -5px; }}
    .kol-star.br {{ left: 18px; bottom: -5px; }}
    .kol-inner {{
      transform: skewX(14deg);
      display: flex;
      align-items: center;
      gap: 18px;
    }}
    .kol-clap {{
      width: 50px;
      height: 50px;
      flex-shrink: 0;
      filter: drop-shadow(0 3px 8px rgba(0,0,0,0.7));
    }}
    .kol-name {{
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      font-style: italic;
      font-size: 37px;
      line-height: 1.08;
      letter-spacing: 0.03em;
      color: #FFFFFF;
      text-transform: uppercase;
      text-shadow: 0 3px 12px rgba(0,0,0,0.9);
    }}
    .kol-role {{
      margin-top: 5px;
      font-family: "Be Vietnam Pro", sans-serif;
      font-weight: 600;
      font-style: italic;
      font-size: 21px;
      color: #F7DA8C;
      text-shadow: 0 2px 8px rgba(0,0,0,0.85);
    }}

    /* Final Cut Pro Kinetic Counter-Slide Broadcast Banner (Image 1 Upgrade: Dark R->L, Gold L->R, Masked Text Slide!) */
    .wh-fcp-host {{
      position: absolute;
      left: 54px;
      top: 38px;
      z-index: 24;
      pointer-events: none;
    }}
    .wh-fcp-viewport {{
      position: relative;
      display: inline-flex;
      align-items: stretch;
      overflow: hidden;
      border-radius: 10px 0 0 10px;
      max-width: 1080px;
    }}
    .wh-fcp-bg {{
      position: absolute;
      inset: 0;
      z-index: 1;
      background: linear-gradient(90deg, rgba(18, 12, 8, 0.94) 0%, rgba(22, 15, 10, 0.85) 74%, rgba(22, 15, 10, 0.0) 100%);
      border-radius: 10px 0 0 10px;
      will-change: transform;
    }}
    .wh-fcp-gold-run {{
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      width: 44%;
      z-index: 2;
      pointer-events: none;
      background: linear-gradient(90deg, rgba(244, 198, 92, 0.0) 0%, rgba(244, 198, 92, 0.42) 48%, rgba(255, 232, 156, 0.88) 84%, rgba(255, 248, 220, 0.0) 100%);
      will-change: transform, opacity;
    }}
    .wh-fcp-bar {{
      position: relative;
      z-index: 4;
      width: 7px;
      flex-shrink: 0;
      border-radius: 6px;
      background: linear-gradient(180deg, #FFF2CA 0%, #E5B24C 52%, #9B6E2B 100%);
      box-shadow: 0 0 16px rgba(244, 200, 103, 0.60);
      transform-origin: 50% 100%;
      will-change: transform;
    }}
    .wh-fcp-body {{
      position: relative;
      z-index: 3;
      padding: 18px 72px 18px 26px;
    }}
    .wh-fcp-mask {{
      overflow: hidden;
      padding: 4px 6px 4px 0;
      margin: -4px 0;
    }}
    .wh-fcp-rule {{
      width: 220px;
      height: 2px;
      margin: 5px 0 5px 0;
      border-radius: 2px;
      background: linear-gradient(90deg, #FFE89E 0%, #D9A443 68%, rgba(217, 164, 67, 0.0) 100%);
      transform-origin: 0% 50%;
      will-change: transform;
    }}
    .wh-fcp-kicker {{
      font-family: "Be Vietnam Pro", sans-serif;
      font-weight: 700;
      font-size: 18px;
      letter-spacing: 0.16em;
      color: #F5CE7B;
      text-transform: uppercase;
      text-shadow: 0 2px 10px rgba(0,0,0,0.85);
      will-change: transform, opacity;
    }}
    .wh-fcp-title {{
      margin-top: 2px;
      font-family: "Oswald", sans-serif;
      font-weight: 700;
      font-size: 44px;
      line-height: 1.14;
      color: #FFFDF8;
      letter-spacing: 0.025em;
      text-transform: uppercase;
      text-shadow: 0 3px 14px rgba(0,0,0,0.92);
      will-change: transform;
    }}
    .wh-fcp-sub {{
      margin-top: 5px;
      font-family: "Be Vietnam Pro", sans-serif;
      font-weight: 600;
      font-size: 23px;
      line-height: 1.28;
      color: #F2E9DA;
      text-shadow: 0 2px 10px rgba(0,0,0,0.90);
      will-change: transform, opacity;
    }}

    /* End-Card Lockup (307.566667 - 316.40s — 100% Clean Native 3D Logo Reveal, Zero Bokeh Glitch!) */
    .wh-end-host {{
      position: absolute;
      inset: 0;
      z-index: 26;
      pointer-events: none;
    }}
    .wh-end-top {{
      position: absolute;
      left: 96px;
      right: 96px;
      top: 30px;
      text-align: center;
      opacity: 0;
    }}
    .wh-end-bot {{
      position: absolute;
      left: 64px;
      right: 64px;
      bottom: 40px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 24px;
      opacity: 0;
    }}
    .wh-end-addr {{
      padding: 16px 32px;
      border-radius: 12px;
      background: rgba(24, 17, 12, 0.92);
      border: 1.5px solid rgba(243, 214, 156, 0.48);
      box-shadow: 0 14px 34px rgba(0,0,0,0.85);
      font-family: "Montserrat", sans-serif;
      font-weight: 700;
      font-size: 23px;
      letter-spacing: 0.06em;
      color: var(--ivory);
    }}
    .wh-end-hotline {{
      padding: 17px 38px;
      border-radius: 12px;
      background: linear-gradient(135deg, #A8222B 0%, #681218 100%);
      border: 1.5px solid rgba(255, 232, 184, 0.78);
      box-shadow: 0 14px 38px rgba(0, 0, 0, 0.80);
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      font-size: 25px;
      color: #FFFDF8;
      letter-spacing: 0.08em;
    }}
  </style>

  <div id="root" data-composition-id="overlays-hud" data-width="1920" data-height="1080">
    <!-- 1. GRAND INTRO HERO LOCKUP (0.000000s - 5.000000s) -->
    <div id="intro-hero" class="clip wh-intro-host" data-start="0" data-duration="5.000000" data-track-index="1" data-layout-allow-caption-zone>
      <div class="wh-intro-scrim" data-layout-ignore></div>
      <div id="intro-stack" class="wh-intro-stack">
        <img id="intro-emblem" src="assets/images/winhair_logo_2color_pad.png" alt="Win Hair" style="height: 84px; width: auto; margin-bottom: 6px; opacity: 0;" />
        <div id="intro-kicker" class="wh-eyebrow" style="margin-bottom: 4px; opacity: 0;">
          <span class="wh-eyebrow-star" data-layout-ignore>✦</span>
          <span class="wh-eyebrow-txt" style="font-size: 20px;">THẾ GIỚI TÓC NAM &amp; RELAX · NHA TRANG</span>
          <span class="wh-eyebrow-star" data-layout-ignore>✦</span>
        </div>
        <div id="intro-wordmark" style="opacity: 0;">
          {bullion_text("intro-wm", "WIN HAIR SALON", "wh-disp-xl")}
        </div>
        <div id="intro-flare" class="wh-anamorphic-flare" style="width: 580px; opacity: 0;" data-layout-ignore></div>
        <div id="intro-tagline" class="wh-intro-plaque" style="opacity: 0;" data-var-text="brand_tagline">
          ĐẲNG CẤP TÓC NAM SỐ 1 NHA TRANG
        </div>
      </div>
    </div>

    <!-- 2A. DUAL CELEBRITY KOL NAME TAGS AT 00:15 (12.60s - 15.80s) -->
    <div id="kol-scene-1" class="clip kol-host" data-start="12.600000" data-duration="3.200000" data-track-index="5">
      {kol_tag_html("kol1-h", 488, 662, 504, "HƯNG HUỲNH", "Nhà sáng tạo nội dung")}
      {kol_tag_html("kol1-y", 1136, 662, 476, "HUY", GROUP_SVG + "Gia đình nhà Mặn")}
    </div>

    <!-- 2B. DUAL CELEBRITY KOL NAME TAGS AT INTERVIEW (212.20s - 221.50s) -->
    <div id="kol-scene-2" class="clip kol-host" data-start="212.200000" data-duration="9.300000" data-track-index="6">
      {kol_tag_html("kol2-h", 84, 690, 504, "HƯNG HUỲNH", "Nhà sáng tạo nội dung")}
      {kol_tag_html("kol2-y", 676, 690, 476, "HUY", GROUP_SVG + "Gia đình nhà Mặn")}
    </div>

    <!-- 3. LARGE BROADCAST SECTION & TESTIMONIAL BANNERS (Image 3 Fix!) -->
    {"".join(hud_html_parts)}

    <!-- 4. GRAND END-CARD LOCKUP (307.566667s - 316.400000s — Pure Native 3D Logo Reveal!) -->
    <div id="end-lockup" class="clip wh-end-host" data-start="307.566667" data-duration="8.833333" data-track-index="3" data-layout-allow-caption-zone>
      <div id="end-top" class="wh-end-top">
        <div class="wh-sig-script" style="margin-bottom: 6px;">Tinh Hoa Phong Thái Quý Ông</div>
        <div style="margin-top: 2px;">
          {bullion_text("end-ttl", "HAI ĐIỂM ĐẾN · MỘT CHUẨN MỰC TRẢI NGHIỆM", "wh-disp-lg")}
        </div>
      </div>

      <div id="end-bot" class="wh-end-bot">
        <div class="wh-end-addr" data-var-text="branch_1">CS1: 41 LÝ TỰ TRỌNG</div>
        <div class="wh-end-hotline" data-var-text="hotline">HOTLINE: 0352 956 779</div>
        <div class="wh-end-addr" data-var-text="branch_2">CS2: 59 THÍCH QUẢNG ĐỨC</div>
      </div>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set(["#intro-emblem", "#intro-kicker", "#intro-wordmark", "#intro-flare", "#intro-tagline", "#end-top", "#end-bot"], {{ opacity: 0 }});

    // Intro Hero: WIN HAIR SALON -> ĐẲNG CẤP TÓC NAM SỐ 1 NHA TRANG (synced to team shout at 1.50s!)
    tl.fromTo("#intro-emblem", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 0.06);
    tl.fromTo("#intro-kicker", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power3.out" }}, 0.12);
    tl.fromTo("#intro-wordmark", {{ opacity: 0, y: 24, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "power3.out" }}, 0.16);
    tl.fromTo("#intro-flare", {{ scaleX: 0, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: 0.48, ease: "power3.out" }}, 0.28);
    tl.fromTo("#intro-wm-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.15, ease: "power2.inOut" }}, 0.42);
    tl.fromTo("#intro-tagline", {{ opacity: 0, scale: 0.92, y: 20 }}, {{ opacity: 1, scale: 1.0, y: 0, duration: 0.38, ease: "expo.out" }}, 1.52);

    // Dual KOL Name Tags at 00:15 (12.60s - 15.80s)
    tl.fromTo("#kol1-h", {{ opacity: 0, x: -45, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1.0, duration: 0.34, ease: "expo.out" }}, 12.66);
    tl.fromTo("#kol1-y", {{ opacity: 0, x: 45, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1.0, duration: 0.34, ease: "expo.out" }}, 12.92);
    tl.fromTo(["#kol1-h", "#kol1-y"], {{ opacity: 1 }}, {{ opacity: 0, y: 14, duration: 0.22, ease: "power2.in", immediateRender: false }}, 15.54);

    // Dual KOL Name Tags at Interview (212.20s - 221.50s)
    tl.fromTo("#kol2-h", {{ opacity: 0, x: -45, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1.0, duration: 0.36, ease: "expo.out" }}, 212.35);
    tl.fromTo("#kol2-y", {{ opacity: 0, x: 45, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1.0, duration: 0.36, ease: "expo.out" }}, 214.40);
    tl.fromTo(["#kol2-h", "#kol2-y"], {{ opacity: 1 }}, {{ opacity: 0, y: 14, duration: 0.26, ease: "power2.in", immediateRender: false }}, 221.18);

    // Section & Review HUDs
    {"".join(hud_js_parts)}

    // End-Card Lockup (glides in smoothly after the 3D gold WH emblem emerges cleanly!)
    tl.fromTo("#end-top", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.56, ease: "power3.out" }}, 308.35);
    tl.fromTo("#end-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.25, ease: "power2.inOut" }}, 309.15);
    tl.fromTo("#end-bot", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.56, ease: "power3.out" }}, 308.85);

    window.__timelines["overlays-hud"] = tl;
  </script>
</template>
""")

# =========================================================================
# 3. SEAMLESS WARM CHAMPAGNE OPTICAL TRANSITIONS (tvc-transitions.html)
# =========================================================================
TRANSITION_CUTS = [
    5.000000,    # Intro -> Slide 01
    9.333333,    # Slide 01 -> Salon Tour
    35.366667,   # -> Slide 02 Shampoo
    39.166667,   # Slide 02 -> Shampoo / Haircut Zone (User CapCut sync!)
    54.666667,   # -> Slide 02B VIP Floor 2 (User CapCut sync!)
    59.666667,   # Slide 02B -> Slide 02C Kingsport
    62.766667,   # Kingsport -> Track 0 Reveal
    64.266667,   # -> Real CS2 VIP Drinks
    70.100000,   # Slide 02C -> Private Rooms
    80.233333,   # -> Slide 03 Playing Card Fan
    87.466667,   # Slide 03 -> Bridge
    88.700000,   # -> Slide 04 Master Haircut
    100.000000,  # Slide 04 -> Slide 05 Shave
    104.966667,  # Slide 05 -> Slide 06 Ear Care
    109.533333,  # Slide 06 Beat A -> Beat B Flip
    111.566667,  # Slide 06 -> Track 0 Reveal (User CapCut sync!)
    114.066667,  # -> Slide 07 Steam & Massage
    117.900000,  # Slide 07 Act A -> Act B Rail
    127.000000,  # Slide 07 -> Slide 08 Manicure/Pedicure
    134.366667,  # Slide 08 -> Staff Team (User CapCut sync!)
    277.900000,  # -> Slide 10 Beat 1 Golden Hour -20%
    284.500000,  # Beat 1 -> Beat 2 Combo 129K
    291.133333,  # Beat 2 -> Beat 3 Nap 79K
    302.200000,  # Beat 3 -> Beat 4 Two Branches
]

tr_divs = []
tr_js = []
for idx, t_cut in enumerate(TRANSITION_CUTS):
    tid = f"tr-{idx:02d}"
    st = max(0.0, t_cut - 0.133333)
    dur = 0.300000
    tr_divs.append(f"""
    <div id="{tid}" class="clip tr-host" data-start="{st:.6f}" data-duration="{dur:.6f}" data-track-index="0" data-layout-ignore>
      <div id="{tid}-veil" class="tr-veil"></div>
      <div id="{tid}-streak" class="tr-streak"></div>
    </div>""")
    tr_js.append(f"""
    tl.fromTo("#{tid}-veil",
      {{ opacity: 0 }},
      {{ opacity: 0.26, duration: 0.1333, yoyo: true, repeat: 1, ease: "sine.inOut" }},
      {st:.4f}
    );
    tl.fromTo("#{tid}-streak",
      {{ opacity: 0, scaleX: 0.35 }},
      {{ opacity: 0.48, scaleX: 1.05, duration: 0.1333, yoyo: true, repeat: 1, ease: "sine.inOut" }},
      {st:.4f}
    );""")

write_comp("tvc-transitions.html", f"""<template>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    #root {{
      position: absolute;
      inset: 0;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      pointer-events: none;
    }}
    .tr-host {{
      position: absolute;
      inset: 0;
      overflow: hidden;
      pointer-events: none;
    }}
    .tr-veil {{
      position: absolute;
      inset: 0;
      opacity: 0;
      background: radial-gradient(
        ellipse at 50% 50%,
        rgba(230, 195, 122, 0.25) 0%,
        rgba(28, 19, 13, 0.54) 68%,
        rgba(14, 10, 8, 0.68) 100%
      );
      pointer-events: none;
    }}
    .tr-streak {{
      position: absolute;
      left: 8%;
      right: 8%;
      top: 50%;
      height: 2px;
      margin-top: -1px;
      opacity: 0;
      background: linear-gradient(90deg, transparent 0%, rgba(230, 195, 122, 0.80) 35%, rgba(255, 248, 229, 0.92) 50%, rgba(230, 195, 122, 0.80) 65%, transparent 100%);
      box-shadow: 0 0 22px 3px rgba(230, 195, 122, 0.40);
      mix-blend-mode: screen;
      pointer-events: none;
    }}
  </style>
  <div id="root" data-composition-id="tvc-transitions" data-width="1920" data-height="1080">
    {"".join(tr_divs)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set([".tr-veil", ".tr-streak"], {{ opacity: 0 }});
    {"".join(tr_js)}
    window.__timelines["tvc-transitions"] = tl;
  </script>
</template>
""")

# =========================================================================
# 4. LARGER FRAMELESS CINEMA SUBTITLES (44px Bold + Lingering Scrim!)
# =========================================================================
with open(DC_PATH, "r", encoding="utf-8") as f:
    dc = json.load(f)
texts_map = {t["id"]: t for t in dc["materials"].get("texts", [])}

TEXT_FIXES = {
    "WINHAIR SẼ KHÔNG CHỈ LÀMỘT SALON DÀNH CHO NAM": "WINHAIR SẼ KHÔNG CHỈ LÀ MỘT SALON DÀNH CHO NAM",
    "MASSAGE MẶT VÀ KIM CÓ MASSAGE CỔ VAI GÁY": "MASSAGE MẶT VÀ KIÊM LUÔN MASSAGE CỔ VAI GÁY",
    "CÓ LUÔN GHẾ MÁT XA KING SPORT": "CÓ LUÔN GHẾ MASSAGE KINGSPORT",
    "DỊCH VỤ LÀM  1 :1": "DỊCH VỤ PHỤC VỤ RIÊNG 1 : 1",
    "ĐỂ CHO ANH HAY LUÔN LUÔN CỐ GẮNG": "ĐỂ CHO WINHAIR LUÔN LUÔN CỐ GẮNG",
    "THÌ CÁC BẠN CÓ THỂ GHÉ QUA WINHAIR ĐỂ TRẢI NGHIỆM THỬ": "THÌ CÁC BẠN HÃY GHÉ QUA WINHAIR ĐỂ TRẢI NGHIỆM THỬ",
    "THỨ 2 ĐẾN THỨ 6": "TỪ THỨ 2 ĐẾN THỨ 5",
}

GOLD_KEYWORDS = sorted([
    "WINHAIR SALON", "WIN HAIR", "WINHAIR", "SỐ 1 NHA TRANG", "SỐ MỘT NHA TRANG",
    "DỊCH VỤ ĐA DẠNG", "KHÔNG GIAN ĐẲNG CẤP", "CHUYÊN NGHIỆP 10 ĐIỂM", "CHUYÊN NGHIỆP",
    "KOC", "KOL", "TẦNG 2 KHU VIP", "KHU VIP", "GHẾ MASSAGE KINGSPORT", "KINGSPORT",
    "NƯỚC MIỄN PHÍ", "MIỄN PHÍ", "NƯỚC CAM", "TRÀ CHANH", "CÀ PHÊ", "NGHỈ DƯỠNG",
    "PHỤC VỤ RIÊNG 1 : 1", "1 : 1", "KHÔNG ỒN", "KHÔNG PHIỀN", "THƯ GIÃN",
    "GỘI ĐẦU", "MASSAGE CỔ VAI GÁY", "MASSAGE MẶT", "MASSAGE TAY", "MASSAGE CHÂN", "MASSAGE BODY", "MASSAGE",
    "LẤY RÁY TAI", "NGOÁY TAI", "RÁY TAI", "ĐẮP MẶT", "LỘT MỤN", "FADE", "CẠO MẶT", "XÔNG HƠI",
    "LỰC TAY CHẮC", "KHỎE RE", "BẤM MÓNG TAY", "CẮT MÓNG CHÂN", "CẮT TÓC ĐẸP",
    "SANG TRỌNG VÀ LỊCH SỰ", "SẠCH SẼ", "RẤT LÀ NHIỆT TÌNH", "NHIỆT TÌNH", "TAY NGHỀ CŨNG RẤT LÀ TỐT", "TAY NGHỀ MÌNH THẤY RẤT LÀ TỐT",
    "RẤT LÀ TUYỆT VỜI", "TUYỆT VỜI", "CẢ MỘT GIA ĐÌNH", "THƯỢNG ĐẾ", "RẤT HÀI LÒNG", "RẤT ƯNG",
    "RESET LẠI BẢN THÂN", "VẺ ĐẸP TRAI VÀ PHONG ĐỘ", "NGƯỜI NÓ NHẸ HẲN LUÔN", "RẤT LÀ WOW",
    "NGỦ THIẾP ĐI", "NHẸ QUÁ", "RẤT LÀ NHẸ NHÀNG", "10 ĐIỂM", "10 / 10", "CHÍN ĐIỂM",
    "TỪ THỨ 2 ĐẾN THỨ 5", "THỨ 2 ĐẾN THỨ 5", "GIẢM NGAY 20%", "ĐI SỚM GIÁ NGON", "QUÁ HỜI",
    "COMBO NGỦ TRƯA", "79.000", "TỈNH TÁO", "41 LÝ TỰ TRỌNG", "59 THÍCH QUẢNG ĐỨC",
], key=len, reverse=True)

def highlight_caption(txt: str) -> str:
    s = html.escape(txt.strip())
    placeholders = []
    for kw in GOLD_KEYWORDS:
        ekw = html.escape(kw)
        if ekw in s:
            token = f"__KW_{len(placeholders)}__"
            placeholders.append((token, f'<span class="tv-kw">{ekw}</span>'))
            s = s.replace(ekw, token)
    for token, repl in placeholders:
        s = s.replace(token, repl)
    return s

cap_cues = []
for seg in dc["tracks"][11]["segments"]:
    st = seg["target_timerange"]["start"] / 1e6
    dur = seg["target_timerange"]["duration"] / 1e6
    en = st + dur
    if dur < 0.15 or en <= 5.01 or (284.80 <= st <= 291.10) or st >= 307.50:
        continue
    tmat = texts_map.get(seg["material_id"], {})
    raw = tmat.get("content", "")
    try:
        txt = json.loads(raw).get("text", raw).strip()
    except Exception:
        txt = raw.strip()
    if not txt:
        continue
    txt = TEXT_FIXES.get(txt, txt)
    cap_cues.append((st, dur, en, highlight_caption(txt)))

scrim_blocks = []
for st, dur, en, _ in cap_cues:
    if not scrim_blocks or st - scrim_blocks[-1][1] > 1.35:
        scrim_blocks.append([st, en])
    else:
        scrim_blocks[-1][1] = max(scrim_blocks[-1][1], en)

scrim_divs = []
scrim_tweens = []
for bi, (bst, ben) in enumerate(scrim_blocks):
    prev_limit = 5.00 if bi == 0 else scrim_blocks[bi - 1][1] + 0.90
    s_in = max(prev_limit, bst - 0.30)
    next_bst = scrim_blocks[bi + 1][0] if bi + 1 < len(scrim_blocks) else 307.55
    hard_cap = min(307.55, next_bst - 0.12)
    if ben < 284.85 and next_bst > 290.0:
        hard_cap = min(hard_cap, 284.85)
    hold_end = min(hard_cap - 0.45, ben + 0.45)
    s_out_end = min(hard_cap, max(ben + 0.35, hold_end + 0.75))
    sdur = max(0.50, s_out_end - s_in)
    fade_in_d = min(0.42, sdur * 0.28)
    fade_out_d = max(0.42, min(0.80, s_out_end - max(s_in + fade_in_d, hold_end)))
    sid = f"scrim-blk-{bi:02d}"
    scrim_divs.append(
        f'    <div id="{sid}" class="clip tv-scrim-host" data-start="{s_in:.6f}" data-duration="{sdur:.6f}" data-track-index="0" data-layout-ignore>'
        f'<div id="{sid}-bg" class="tv-scrim"></div></div>'
    )
    scrim_tweens.append(
        f'    tl.fromTo("#{sid}-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: {fade_in_d:.3f}, ease: "sine.out" }}, {s_in:.4f});\n'
        f'    tl.fromTo("#{sid}-bg", {{ opacity: 1 }}, {{ opacity: 0, duration: {fade_out_d:.3f}, ease: "sine.inOut", immediateRender: false }}, {s_out_end - fade_out_d:.4f});'
    )

cap_divs = []
cap_tweens = []
for cap_idx, (st, dur, en, styled_html) in enumerate(cap_cues):
    cid = f"cap-{cap_idx:03d}"
    next_st = cap_cues[cap_idx + 1][0] if cap_idx + 1 < len(cap_cues) else 307.50
    ext_dur = min(dur + 0.24, max(dur, next_st - st - 0.04))
    cap_divs.append(
        f'    <div id="{cid}" class="clip tv-cap-host" data-start="{st:.6f}" data-duration="{ext_dur:.6f}" data-track-index="1">'
        f'<div id="{cid}-in" class="tv-cap-line">{styled_html}</div></div>'
    )
    in_dur = min(0.16, ext_dur * 0.26)
    out_dur = min(0.24, ext_dur * 0.28)
    cap_tweens.append(
        f'    tl.fromTo("#{cid}-in", {{ opacity: 0, y: 10, filter: "blur(4px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: {in_dur:.3f}, ease: "power2.out" }}, {st:.4f});\n'
        f'    tl.fromTo("#{cid}-in", {{ opacity: 1 }}, {{ opacity: 0, duration: {out_dur:.3f}, ease: "sine.inOut", immediateRender: false }}, {st + ext_dur - out_dur:.4f});'
    )

write_comp("captions-tv.html", f"""<template>
  <style>{FONT_FACES_CSS}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    #root {{
      position: absolute;
      inset: 0;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      pointer-events: none;
    }}
    .tv-scrim-host {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 248px;
      pointer-events: none;
      z-index: 28;
    }}
    .tv-cap-host {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 214px;
      display: flex;
      justify-content: center;
      align-items: flex-end;
      padding: 0 96px 40px 96px;
      z-index: 30;
    }}
    .tv-scrim {{
      position: absolute;
      inset: 0;
      opacity: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.0) 0%, rgba(12,9,7,0.48) 46%, rgba(10,7,5,0.88) 100%);
      pointer-events: none;
    }}
    .tv-cap-line {{
      position: relative;
      z-index: 2;
      max-width: 1720px;
      font-family: "Be Vietnam Pro", sans-serif;
      font-weight: 700;
      font-size: 43px;
      line-height: 1.30;
      letter-spacing: 0.015em;
      color: #FFFDF8;
      text-align: center;
      text-transform: uppercase;
      text-shadow:
        0 3px 8px rgba(0, 0, 0, 0.94),
        0 8px 22px rgba(0, 0, 0, 0.82);
    }}
    .tv-kw {{
      display: inline-block;
      font-family: "Be Vietnam Pro", sans-serif;
      font-weight: 700;
      color: #FAD882;
      text-shadow:
        0 3px 8px rgba(0, 0, 0, 0.96),
        0 8px 22px rgba(0, 0, 0, 0.85);
    }}
  </style>
  <div id="root" data-composition-id="captions-tv" data-width="1920" data-height="1080">
{chr(10).join(scrim_divs)}
{chr(10).join(cap_divs)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(scrim_tweens)}
{chr(10).join(cap_tweens)}
    window.__timelines["captions-tv"] = tl;
  </script>
</template>
""")
print(f"Built larger 43px captions-tv.html with {len(cap_cues)} subtitle cues and {len(scrim_blocks)} smooth lingering scrim blocks!")

# =========================================================================
# 5. ROOT COMPOSITION (index.html) + BALANCED, REFINED STUDIO SFX SCORE
#    (Never overdone / never stacked; subtle broadcast levels 0.10 - 0.17!)
# =========================================================================
sfx_dir = os.path.join(PROJ, "assets", "sfx")
SFX_MAX = {}
for sfn in os.listdir(sfx_dir):
    if sfn.lower().endswith((".mp3", ".wav", ".m4a")):
        dur_s = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
            os.path.join(sfx_dir, sfn)
        ]).decode().strip())
        SFX_MAX[sfn] = dur_s

RAW_SFX_EVENTS = [
    # --- ACT 1: Grand Intro Shout & Slide 01 (Pure Morning BGM + Subtle Motion Whooshes!) ---
    ("w_wind_thick.mp3",             0.14, 1.35, 0.16),
    ("w_tvc_smooth.mp3",             1.52, 0.55, 0.17),
    ("whoosh_hit_low2.mp3",          4.90, 2.30, 0.22),  # Into Slide 01
    ("w_deep_warm.mp3",              5.04, 1.40, 0.20),  # Blade 1 glides DOWN
    ("w_swipe_air.mp3",              6.42, 1.25, 0.21),  # Blade 2 glides UP
    ("w_deep_punch.mp3",             7.36, 1.35, 0.21),  # Blade 3 glides DOWN
    ("w_shun_magic.mp3",             9.24, 1.15, 0.19),  # Exit Slide 01

    # --- ACT 2: KOL Name Tags (00:13), Floor 1 Banners & Slide 02 (Shampoo) ---
    ("w_tvc_smooth.mp3",            12.55, 0.55, 0.18),  # HUD KOC glides in
    ("w_swish_crisp.mp3",           12.66, 0.52, 0.20),  # KOL Tag 1: HƯNG HUỲNH
    ("electro_servo_lock.mp3",      12.70, 0.40, 0.17),
    ("w_fuwa_wish.mp3",             12.92, 0.72, 0.19),  # KOL Tag 2: HUY
    ("w_wind_airy.mp3",             15.52, 0.27, 0.16),  # KOL Tags glide out
    ("w_move_soft.mp3",             16.42, 0.95, 0.18),  # HUD Floor 1 glides in
    ("w_swish_velvet.mp3",          25.88, 0.39, 0.15),  # HUD Floor 1 glides out
    ("w_tvc_pip.mp3",               26.74, 0.43, 0.18),  # HUD Menu glides in
    ("cinematic_whoosh_16.mp3",     35.26, 1.70, 0.22),  # Into Slide 02 Shampoo
    ("w_short_2.mp3",               35.42, 0.85, 0.18),  # Card 1 flies from Left
    ("w_swish_crisp.mp3",           35.58, 0.52, 0.18),  # Card 2 flies from Top
    ("w_fuwa_wish.mp3",             35.72, 0.72, 0.18),  # Card 3 flies from Bottom
    ("w_deep_classic.mp3",          39.04, 1.50, 0.20),  # Exit Slide 02 -> Reveal Salon
    ("w_wind_thick.mp3",            42.72, 1.10, 0.18),  # HUD Haircut Zone glides in
    ("w_wind_airy.mp3",             52.28, 0.27, 0.15),  # HUD glides out

    # --- ACT 3: VIP Floor 2 CS2 (Slide 02B, Slide 02C Kingsport + Drinks, Slide 03 5-Card Fan) ---
    ("w_swoosh_long.mp3",           54.56, 2.20, 0.22),  # Into Slide 02B VIP Floor 2
    ("w_swipe_air.mp3",             54.72, 1.10, 0.19),  # Hero VIP flies in
    ("w_swish_velvet.mp3",          54.88, 0.39, 0.18),  # VIP Card 2 flies in
    ("w_tvc_smooth.mp3",            55.02, 0.55, 0.18),  # VIP Card 3 flies in
    ("tech_particle_pass.mp3",      57.28, 0.85, 0.17),  # Mid-slide sheen sweep

    # Slide 02C: Kingsport -> Track 0 Reveal -> Real CS2 Sofa & 3 Vietnamese Drink Plaques
    ("deep_title_wind.mp3",         59.56, 1.25, 0.21),  # Into Kingsport
    ("w_swoosh_4.mp3",              59.72, 1.10, 0.18),  # Left & Right cards fly in
    ("w_fuwa_wish.mp3",             62.66, 0.75, 0.18),  # Fade to Track 0 Reveal
    ("w_deep_warm.mp3",             64.16, 1.45, 0.21),  # Into Real CS2 VIP Drinks
    ("w_swish_crisp.mp3",           65.82, 0.52, 0.18),  # Nước Cam Tươi slides in
    ("ping_glass.mp3",              65.88, 0.70, 0.15),
    ("w_tvc_smooth.mp3",            66.38, 0.55, 0.18),  # Trà Chanh Mát Lạnh slides in
    ("w_move_soft.mp3",             66.92, 0.85, 0.18),  # Cà Phê Đậm Đà slides in
    ("deep_air_whoosh.mp3",         69.98, 0.95, 0.20),  # Exit Slide 02C
    ("w_tvc_pip.mp3",               70.34, 0.43, 0.17),  # HUD Private Rooms glides in

    # Slide 03: 5-Card Poker Fan Deal-Out (Diverse Swishes + Ascending Tactile Ticks)
    ("cinematic_whoosh_16.mp3",     80.14, 1.75, 0.22),
    ("w_swish_velvet.mp3",          80.28, 0.39, 0.18),  # Card 01 fans out
    ("electro_card_1.mp3",          80.32, 0.36, 0.16),
    ("w_wind_airy.mp3",             80.82, 0.27, 0.18),  # Card 02 fans out
    ("electro_card_2.mp3",          80.86, 0.36, 0.16),
    ("w_tvc_pip.mp3",               81.42, 0.43, 0.18),  # Card 03 fans out
    ("electro_card_3.mp3",          81.46, 0.36, 0.17),
    ("w_swish_crisp.mp3",           82.28, 0.50, 0.19),  # Card 04 fans out
    ("electro_card_4.mp3",          82.32, 0.36, 0.17),
    ("w_tvc_smooth.mp3",            83.10, 0.54, 0.19),  # Card 05 fans out
    ("electro_card_5.mp3",          83.14, 0.36, 0.18),
    ("w_shun_magic.mp3",            84.15, 1.20, 0.16),  # Mid-card shimmer switch
    ("w_deep_punch.mp3",            87.36, 1.25, 0.20),  # Exit Slide 03

    # --- ACT 4: Core Services Showcase (Slides 04, 05, 06, 07, 08) ---
    # Slide 04: Master Haircut
    ("whoosh_hit_low2.mp3",         88.60, 2.20, 0.22),
    ("w_short_2.mp3",               88.76, 0.80, 0.18),  # Col 1 & Col 2 glide Up/Down
    ("w_swipe_air.mp3",             89.00, 1.05, 0.19),  # Hero glides in
    ("blade_shine.mp3",             89.18, 1.15, 0.18),
    ("w_tvc_pip.mp3",               91.08, 0.43, 0.16),  # Editorial line 1
    ("deep_swish_tight.mp3",        92.48, 0.78, 0.18),  # Hero video switch 1
    ("w_wind_airy.mp3",             93.28, 0.27, 0.16),  # Editorial line 2
    ("w_move_soft.mp3",             94.34, 0.85, 0.17),  # Left columns switch
    ("w_fuwa_wish.mp3",             96.26, 0.75, 0.18),  # Hero video switch 2 + line 3

    # Slide 05: 3 Diagonal Shave Blades Slicing In
    ("w_deep_classic.mp3",          99.90, 1.60, 0.22),
    ("w_swish_crisp.mp3",          100.05, 0.50, 0.19),  # Diagonal 1
    ("w_tvc_smooth.mp3",           100.18, 0.54, 0.19),  # Diagonal 2
    ("blade_shine.mp3",            100.32, 1.15, 0.18),  # Diagonal 3 + razor gleam

    # Slide 06: Ear Care 2-Beat Flip
    ("w_wind_thick.mp3",           104.88, 1.25, 0.21),  # Beat A twin glide
    ("w_swoosh_4.mp3",             105.08, 1.05, 0.18),
    ("w_deep_warm.mp3",            109.46, 1.35, 0.21),  # Beat A -> Beat B Flip!
    ("w_shun_magic.mp3",           111.46, 1.15, 0.19),  # Exit Slide 06 -> Track 0

    # Slide 07: Hot Steam -> Horizontal Massage Rail
    ("cinematic_whoosh_16.mp3",    113.96, 1.70, 0.22),
    ("w_short_2.mp3",              114.16, 0.85, 0.18),
    ("w_deep_punch.mp3",           117.80, 1.45, 0.22),  # Flip to Horizontal Massage Rail!
    ("w_swipe_air.mp3",            117.95, 1.05, 0.19),  # Massage Tay glides right-to-left
    ("w_move_soft.mp3",            119.52, 0.95, 0.19),  # Massage Chân glides right-to-left
    ("w_swoosh_4.mp3",             120.90, 1.05, 0.19),  # Massage Vai Gáy glides right-to-left
    ("tech_particle_pass.mp3",     122.44, 0.85, 0.17),  # Mid-rail shimmer switch

    # Slide 08: Manicure & Pedicure
    ("deep_title_wind.mp3",        126.90, 1.25, 0.21),
    ("w_tvc_smooth.mp3",           127.18, 0.55, 0.18),
    ("w_fuwa_wish.mp3",            131.82, 0.78, 0.18),  # Mid-card switch
    ("deep_air_whoosh.mp3",        134.26, 0.95, 0.20),  # Exit Slide 08 -> Staff Team
    ("w_tvc_pip.mp3",              136.84, 0.43, 0.17),  # HUD Staff Team glides in

    # --- ACT 5: Customer Reviews (Banners + PiPs In/Out) + KOL Name Tags + Slide 09 6-Step ---
    ("w_tvc_smooth.mp3",           152.78, 0.54, 0.17),  # HUD Rev 1 in
    ("w_swish_crisp.mp3",          155.38, 0.52, 0.18),  # PiP 1 glides in
    ("w_wind_airy.mp3",            160.82, 0.27, 0.15),  # PiP 1 glides out
    ("w_move_soft.mp3",            164.28, 0.85, 0.18),  # PiP 2 glides in
    ("w_swish_velvet.mp3",         169.92, 0.39, 0.15),  # PiP 2 glides out

    ("w_tvc_pip.mp3",              172.08, 0.43, 0.17),  # HUD Rev 2 in
    ("w_fuwa_wish.mp3",            188.88, 0.72, 0.17),  # HUD Rev 3 in
    ("w_deep_warm.mp3",            192.14, 1.20, 0.19),  # Full cutaway in
    ("deep_swish_tight.mp3",       197.04, 0.75, 0.17),  # Cutaway out
    ("w_swipe_air.mp3",            200.28, 0.95, 0.18),  # PiP 3 glides in
    ("w_wind_airy.mp3",            205.52, 0.27, 0.15),  # PiP 3 glides out

    # KOL Hưng Huỳnh & Huy Dual Name Tags
    ("w_tvc_smooth.mp3",           212.14, 0.54, 0.17),  # HUD KOL in
    ("w_swish_crisp.mp3",          212.34, 0.52, 0.20),  # KOL Tag 1: HƯNG HUỲNH
    ("electro_servo_lock.mp3",     212.38, 0.40, 0.17),
    ("w_short_2.mp3",              214.38, 0.75, 0.19),  # KOL Tag 2: HUY
    ("w_swish_velvet.mp3",         221.16, 0.39, 0.15),  # KOL Tags out

    # Slide 09: Camera Left Pan + 6-Step Combo Cards + Smooth Exit Pan
    ("w_swoosh_long.mp3",          255.72, 1.85, 0.21),  # Smooth camera pan left + backdrop!
    ("w_tvc_pip.mp3",              256.70, 0.43, 0.17),  # Step 01
    ("electro_card_1.mp3",         256.74, 0.36, 0.15),
    ("w_swish_velvet.mp3",         258.87, 0.39, 0.17),  # Step 02
    ("electro_card_2.mp3",         258.91, 0.36, 0.15),
    ("w_wind_airy.mp3",            260.05, 0.27, 0.17),  # Step 03
    ("electro_card_3.mp3",         260.09, 0.36, 0.15),
    ("w_swish_crisp.mp3",          261.03, 0.50, 0.18),  # Step 04
    ("electro_card_4.mp3",         261.07, 0.36, 0.16),
    ("w_tvc_smooth.mp3",           262.75, 0.52, 0.18),  # Step 05
    ("electro_card_5.mp3",         262.79, 0.36, 0.16),
    ("w_fuwa_wish.mp3",            264.10, 0.70, 0.18),  # Step 06
    ("card_snap.mp3",              264.14, 0.48, 0.16),
    ("w_shun_magic.mp3",           265.72, 1.25, 0.19),  # Smooth camera pan back & backdrop fade-out!

    # --- ACT 6: Grand Promo Finale (-20%, 129K, 79K, 2 Branches & End-Card) ---
    ("whoosh_hit_low2.mp3",        277.80, 2.30, 0.23),  # Beat 1: Golden Hour -20%
    ("w_swipe_air.mp3",            278.04, 1.05, 0.19),  # Hero & Offer cards glide in
    ("w_move_soft.mp3",            281.20, 0.85, 0.17),  # Second CS2 salon shot sheen
    ("tech_particle_pass.mp3",     281.95, 0.85, 0.18),  # -20% gold sheen

    ("w_deep_punch.mp3",           284.42, 1.40, 0.22),  # Beat 2: 129K 4-Step Grid
    ("w_tvc_pip.mp3",              285.24, 0.43, 0.18),  # Q1 Cut
    ("w_swish_velvet.mp3",         285.61, 0.39, 0.18),  # Q2 Shave
    ("w_swish_crisp.mp3",          286.14, 0.50, 0.18),  # Q3 Ear
    ("w_tvc_smooth.mp3",           286.47, 0.52, 0.18),  # Q4 Wash
    ("w_deep_classic.mp3",         287.02, 1.65, 0.22),  # 129K Center Medallion pops in!
    ("electro_bass_drop.mp3",      288.62, 0.85, 0.20),  # "129K!"

    ("cinematic_whoosh_16.mp3",    291.04, 1.70, 0.22),  # Beat 3: 79K Lunch Nap
    ("w_swoosh_4.mp3",             291.36, 1.05, 0.18),  # Left & Mid cards glide in
    ("tech_particle_pass.mp3",     295.56, 0.85, 0.18),  # "79K!"
    ("w_fuwa_wish.mp3",            296.32, 0.78, 0.17),  # Mid-beat clip switch

    ("deep_title_wind.mp3",        302.12, 1.30, 0.22),  # Beat 4: Two Frontal Storefronts
    ("w_swipe_air.mp3",            302.34, 1.05, 0.19),  # CS1 & CS2 cards glide in
    ("w_short_2.mp3",              304.88, 0.85, 0.18),  # Storefront second angle switch
    ("w_swoosh_long.mp3",          307.55, 2.10, 0.18),  # Clean airy entrance into 3D Logo Reveal
]

lane_ends = []
sfx_tag_list = []
for idx, (sfile, sst, sdur, svol) in enumerate(sorted(RAW_SFX_EVENTS, key=lambda x: x[1])):
    assert sfile in SFX_MAX, f"Missing SFX file in assets/sfx: {sfile}"
    max_file_dur = SFX_MAX[sfile]
    clamped_dur = min(sdur, max(0.12, max_file_dur - 0.02))
    if sst + clamped_dur > 316.38:
        clamped_dur = max(0.12, 316.38 - sst)
    assigned_lane = None
    for li, lend in enumerate(lane_ends):
        if sst >= lend + 0.02:
            assigned_lane = 6 + li
            lane_ends[li] = sst + clamped_dur
            break
    if assigned_lane is None:
        assigned_lane = 6 + len(lane_ends)
        lane_ends.append(sst + clamped_dur)
    fade_out = min(0.08, clamped_dur * 0.25)
    sfx_tag_list.append(
        f'      <audio id="sfx-{idx:03d}" class="clip" src="assets/sfx/{sfile}" '
        f'data-start="{sst:.4f}" data-duration="{clamped_dur:.4f}" '
        f'data-volume="{svol:.2f}" data-fade-in="0.015" data-fade-out="{fade_out:.3f}" '
        f'data-track-index="{assigned_lane}"></audio>'
    )
sfx_tags = "\n".join(sfx_tag_list)

SLIDE_MOUNTS = [
    ("slide-01",    "compositions/slide-01.html",    f_time(150),  f_time(130)),   # 5.000000 .. 9.333333
    ("slide-02",    "compositions/slide-02.html",    f_time(1061), f_time(114)),   # 35.366667 .. 39.166667 (User CapCut sync!)
    ("slide-02b",   "compositions/slide-02b.html",   f_time(1640), f_time(150)),   # 54.666667 .. 59.666667 (User CapCut sync!)
    ("slide-02c-a", "compositions/slide-02c-a.html", f_time(1790), f_time(93)),    # 59.666667 .. 62.766667 (Exact f=1790..1883!)
    ("slide-02c-b", "compositions/slide-02c-b.html", f_time(1928), f_time(175)),   # 64.266667 .. 70.100000 (Exact f=1928..2103!)
    ("slide-03",    "compositions/slide-03.html",    f_time(2407), f_time(217)),   # 80.233333 .. 87.466667
    ("slide-04",    "compositions/slide-04.html",    f_time(2661), f_time(339)),   # 88.700000 .. 100.000000
    ("slide-05",    "compositions/slide-05.html",    f_time(3000), f_time(149)),   # 100.000000 .. 104.966667
    ("slide-06",    "compositions/slide-06.html",    f_time(3149), f_time(198)),   # 104.966667 .. 111.566667 (User CapCut sync!)
    ("slide-07",    "compositions/slide-07.html",    f_time(3422), f_time(388)),   # 114.066667 .. 127.000000
    ("slide-08",    "compositions/slide-08.html",    f_time(3810), f_time(221)),   # 127.000000 .. 134.366667 (User CapCut sync!)
    ("slide-09",    "compositions/slide-09.html",    f_time(7673), f_time(322)),   # 255.766667 .. 266.500000
    ("slide-10",    "compositions/slide-10.html",    f_time(8337), f_time(890)),   # 277.900000 .. 307.566667
]

slide_mount_tags = "\n".join([
    f'      <div id="{mid}" class="clip" data-composition-id="{mid}" data-composition-src="{msrc}" '
    f'data-start="{mst}" data-duration="{mdur}" data-track-index="1" data-track-kind="graphics" '
    f'data-width="1920" data-height="1080" style="position: absolute; inset: 0; z-index: 10;"></div>'
    for mid, msrc, mst, mdur in SLIDE_MOUNTS
])

VARIABLES_JSON = json.dumps([
    {"id": "brand_name", "type": "string", "label": "Tên Thương Hiệu", "default": "WIN HAIR SALON"},
    {"id": "brand_tagline", "type": "string", "label": "Slogan Thương Hiệu", "default": "ĐẲNG CẤP TÓC NAM SỐ 1 NHA TRANG"},
    {"id": "branch_1", "type": "string", "label": "Địa Chỉ Cơ Sở 1", "default": "CS1: 41 LÝ TỰ TRỌNG"},
    {"id": "branch_2", "type": "string", "label": "Địa Chỉ Cơ Sở 2", "default": "CS2: 59 THÍCH QUẢNG ĐỨC"},
    {"id": "hotline", "type": "string", "label": "Số Điện Thoại Hotline", "default": "HOTLINE: 0352 956 779"},
], ensure_ascii=False)

index_html = f"""<!doctype html>
<html lang="vi" data-composition-variables='{VARIABLES_JSON}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>TVC Win Hair Salon CS2 — Final Cinema Edition</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      {FONT_FACES_CSS}
      :root {{
        --ground: #100B08;
        --brand-gold: #F5C542;
        --brand-crimson: #E31824;
      }}
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html, body {{
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: var(--ground);
      }}
      #root {{
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #100B08;
      }}
      .base-bg {{
        position: absolute;
        inset: 0;
        background: #100B08;
        z-index: 0;
      }}
      #base-video {{
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1080px;
        object-fit: cover;
        z-index: 1;
      }}
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="316.400000"
      data-fps="30"
      data-width="1920"
      data-height="1080"
    >
      <div class="base-bg" data-layout-ignore></div>

      <!-- Track 0: Continuous Single-Pass CapCut Color+Beauty Master Video (9,492 exact frames) -->
      <video
        id="base-video"
        class="clip"
        src="assets/video/clean_base_1080p.mp4"
        data-start="0"
        data-duration="316.400000"
        data-track-index="0"
        muted
        playsinline
      ></video>

      <!-- Track 1: 12 Warm Cinema Motion Slides -->
{slide_mount_tags}

      <!-- Track 2: Real Customer Experience B-Roll Cutaways & PiPs -->
      <div
        id="reviews-broll"
        class="clip"
        data-composition-id="reviews-broll"
        data-composition-src="compositions/reviews-broll.html"
        data-start="0"
        data-duration="316.400000"
        data-track-index="2"
        data-track-kind="graphics"
        data-width="1920"
        data-height="1080"
        style="position: absolute; inset: 0; z-index: 14;"
      ></div>

      <!-- Track 3: Hero Intro, Dual KOL Name Tags, Large Broadcast Banners & End-Card -->
      <div
        id="overlays-hud"
        class="clip"
        data-composition-id="overlays-hud"
        data-composition-src="compositions/overlays-hud.html"
        data-start="0"
        data-duration="316.400000"
        data-track-index="3"
        data-track-kind="graphics"
        data-width="1920"
        data-height="1080"
        style="position: absolute; inset: 0; z-index: 20;"
      ></div>

      <!-- Track 4: Seamless Warm Champagne Optical Transitions -->
      <div
        id="tvc-transitions"
        class="clip"
        data-composition-id="tvc-transitions"
        data-composition-src="compositions/tvc-transitions.html"
        data-start="0"
        data-duration="316.400000"
        data-track-index="4"
        data-track-kind="graphics"
        data-width="1920"
        data-height="1080"
        style="position: absolute; inset: 0; z-index: 25;"
      ></div>

      <!-- Track 5: Large 43px Frameless Cinema Subtitles with Gold Keyword Emphasis -->
      <div
        id="captions-tv"
        class="clip"
        data-composition-id="captions-tv"
        data-composition-src="compositions/captions-tv.html"
        data-start="0"
        data-duration="316.400000"
        data-track-index="5"
        data-track-kind="captions"
        data-width="1920"
        data-height="1080"
        style="position: absolute; inset: 0; z-index: 30;"
      ></div>

      <!-- Track 6: Clean Master Voiceover + Interviews + BGM -->
      <audio
        id="master-vo-bgm"
        class="clip"
        src="assets/audio/clean_vo_bgm.mp3"
        data-start="0"
        data-duration="316.400000"
        data-volume="1.06"
        data-fade-in="0.05"
        data-fade-out="0.60"
        data-track-index="5"
      ></audio>

      <!-- Track 7+: Balanced Studio SFX Score (Subtle, refined, zero clutter) -->
{sfx_tags}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#base-video", {{ x: 0 }}, {{ x: -430, duration: 0.50, ease: "sine.out" }}, 255.7667);
      tl.set("#base-video", {{ x: -35 }}, 261.0000);
      tl.to("#base-video", {{ x: 0, duration: 0.72, ease: "sine.inOut" }}, 265.7500);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

with open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print(f"Wrote root index.html! Total balanced Studio SFX cues: {len(RAW_SFX_EVENTS)} across {len(lane_ends)} clean lanes.")

# =========================================================================
# 6. STRICT AUTOMATED VERIFICATION (Zero Repeat, Zero Pop SFX, Pure SDR)
# =========================================================================
slide_files_used = defaultdict(list)
html_targets = [os.path.join(PROJ, "index.html")] + [
    os.path.join(COMP_DIR, fn) for fn in os.listdir(COMP_DIR)
    if fn.endswith(".html") and (fn.startswith("slide-") or fn in ("overlays-hud.html", "captions-tv.html", "reviews-broll.html", "tvc-transitions.html"))
]

for hp in sorted(html_targets):
    with open(hp, "r", encoding="utf-8") as fp:
        txt = fp.read()
    txt_no_comments = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    assert "text-stroke" not in txt_no_comments, f"FORBIDDEN text-stroke found in {hp}!"
    assert "preserve-3d" not in txt_no_comments, f"FORBIDDEN preserve-3d found in {hp}!"
    assert "pop_clean.mp3" not in txt_no_comments, f"FORBIDDEN bubbly pop_clean.mp3 found in {hp}!"
    for m in re.finditer(r'<video[^>]*src="([^"]+)"[^>]*data-duration="([0-9.]+)"', txt):
        src_rel, dur_str = m.group(1), float(m.group(2))
        abs_p = os.path.join(PROJ, src_rel.replace("/", os.sep))
        assert os.path.exists(abs_p), f"Missing video {abs_p} in {hp}"
        if src_rel.startswith("assets/slides/"):
            slide_files_used[src_rel].append((os.path.basename(hp), dur_str))
        out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", abs_p]).decode().strip()
        f_dur = float(out)
        if dur_str > f_dur + 0.05:
            raise AssertionError(f"FROZEN CLIP RISK in {os.path.basename(hp)}: {src_rel} needs {dur_str:.2f}s but file is only {f_dur:.2f}s!")

dups = {k: v for k, v in slide_files_used.items() if len(v) > 1}
assert not dups, f"DUPLICATE SLIDE CLIPS DETECTED: {dups}"
print(f"ALL STRICT V8 CHECKS PASSED: {len(slide_files_used)} unique slide clips (0 repeats!), 0 bubbly pops, 0 text-stroke, 0 frozen clip risks!")
