import os
import json
import html

PROJ = r"d:\AI\full studio\projects\winhair-cs2-tvc"
COMP_DIR = os.path.join(PROJ, "compositions")
os.makedirs(COMP_DIR, exist_ok=True)

PDIR = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\TVC WinHair CS2 - ban Reels_v2 (1)-sao chép (1)"
DC_PATH = os.path.join(PDIR, "Timelines", "C8D29776-5FFB-4dd3-8698-E26DA5C9C410", "draft_content.json")

FONT_FACES_CSS = """
@font-face {
  font-family: "Anton";
  src: url("assets/fonts/Anton-Regular.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Asap Condensed";
  src: url("assets/fonts/AsapCondensed-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Asap Condensed";
  src: url("assets/fonts/AsapCondensed-ExtraBold.ttf") format("truetype");
  font-weight: 800;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Asap Condensed";
  src: url("assets/fonts/AsapCondensed-Black.ttf") format("truetype");
  font-weight: 900;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Montserrat";
  src: url("assets/fonts/Montserrat-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Montserrat";
  src: url("assets/fonts/Montserrat-ExtraBold.ttf") format("truetype");
  font-weight: 800;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Montserrat";
  src: url("assets/fonts/Montserrat-Black.ttf") format("truetype");
  font-weight: 900;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Be Vietnam Pro";
  src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype");
  font-weight: 600;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Be Vietnam Pro";
  src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Be Vietnam Pro";
  src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype");
  font-weight: 800;
  font-style: normal;
  font-display: block;
}
"""

SHARED_SLIDE_CSS = FONT_FACES_CSS + """
* { box-sizing: border-box; margin: 0; padding: 0; }
#root {
  position: absolute;
  inset: 0;
  overflow: hidden;
  font-family: "Montserrat", sans-serif;
  color: #ffffff;
}
.wh-stage {
  position: absolute;
  inset: 0;
  perspective: 1300px;
  transform-style: preserve-3d;
}
.wh-bg-obsidian {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 15%, #3D1114 0%, #1C0B09 48%, #080606 100%);
}
.wh-bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(245, 197, 66, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(245, 197, 66, 0.055) 1px, transparent 1px);
  background-size: 64px 64px;
  pointer-events: none;
}
.wh-bokeh-vid {
  position: absolute;
  left: 0;
  top: 0;
  width: 1920px;
  height: 1080px;
  object-fit: cover;
  mix-blend-mode: screen;
  opacity: 0.42;
  pointer-events: none;
}
/* 2-Layer Metallic Gradient Typography (Generous top padding prevents Vietnamese diacritic clipping) */
.wh-grad-wrap {
  position: relative;
  display: inline-block;
  padding: 16px 12px 6px 12px;
  margin: -12px -12px -4px -12px;
}
.wh-grad-back {
  display: block;
  padding: 0;
  user-select: none;
  paint-order: stroke fill;
  -webkit-text-stroke: 7px #140806;
  color: #140806;
  filter: drop-shadow(0 8px 18px rgba(0, 0, 0, 0.85));
}
.wh-grad-front {
  position: absolute;
  inset: 0;
  padding: 16px 12px 6px 12px;
  display: block;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  background-size: 240% 100%, 100% 100%;
  background-position: -130% 0, 0 0;
}
.wh-gold-fill {
  background-image:
    linear-gradient(115deg, rgba(255,255,255,0) 35%, rgba(255,255,255,0.96) 50%, rgba(255,255,255,0) 65%),
    linear-gradient(180deg, #FFFDF2 0%, #FFE27D 26%, #D69324 54%, #FFEDA8 78%, #9B600C 100%);
}
.wh-ruby-fill {
  background-image:
    linear-gradient(115deg, rgba(255,255,255,0) 35%, rgba(255,255,255,0.94) 50%, rgba(255,255,255,0) 65%),
    linear-gradient(180deg, #FFEBEB 0%, #FF5960 26%, #D6121B 55%, #FF8F94 78%, #7E060C 100%);
}
/* Header block */
.wh-header {
  position: absolute;
  left: 96px;
  right: 96px;
  top: 44px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 12;
}
.wh-kicker {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 22px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(190, 20, 28, 0.92), rgba(115, 8, 14, 0.92));
  border: 1.5px solid rgba(255, 222, 130, 0.78);
  box-shadow: 0 6px 20px rgba(214, 18, 27, 0.45);
  font-family: "Montserrat", sans-serif;
  font-weight: 800;
  font-size: 17px;
  letter-spacing: 0.12em;
  color: #FFF6D6;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.wh-title-lg {
  font-family: "Asap Condensed", sans-serif;
  font-weight: 900;
  font-size: 60px;
  line-height: 1.22;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.wh-flare-bar {
  width: 560px;
  height: 3px;
  margin-top: 8px;
  background: linear-gradient(90deg, transparent 0%, #FFD666 32%, #FFFFFF 50%, #FFD666 68%, transparent 100%);
  box-shadow: 0 0 22px 3px rgba(255, 208, 92, 0.82);
  border-radius: 999px;
}
/* Beveled Luxury Media Card */
.wh-card {
  position: absolute;
  border-radius: 20px;
  overflow: hidden;
  background: #120D0B;
  border: 2px solid rgba(250, 210, 110, 0.78);
  box-shadow:
    0 22px 52px rgba(0, 0, 0, 0.78),
    0 0 26px rgba(245, 190, 66, 0.18),
    inset 0 0 0 1px rgba(255, 255, 255, 0.18);
}
.wh-vid-fill {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.wh-card-shade {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.06) 0%, rgba(0,0,0,0.12) 52%, rgba(8,5,4,0.92) 100%);
  pointer-events: none;
}
.wh-card-sheen {
  position: absolute;
  inset: -20%;
  background: linear-gradient(115deg, transparent 38%, rgba(255, 246, 205, 0.48) 50%, transparent 62%);
  pointer-events: none;
  opacity: 0;
}
.wh-card-caption {
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 16px;
  z-index: 4;
}
.wh-badge-num {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  background: linear-gradient(135deg, #FFE484, #C88418);
  color: #160A04;
  font-family: "Montserrat", sans-serif;
  font-weight: 900;
  font-size: 15px;
  letter-spacing: 0.06em;
  margin-bottom: 6px;
}
.wh-card-h3 {
  font-family: "Asap Condensed", sans-serif;
  font-weight: 900;
  font-size: 32px;
  line-height: 1.1;
  color: #FFF6D6;
  text-transform: uppercase;
  text-shadow: 0 3px 12px rgba(0,0,0,0.9);
}
.wh-card-p {
  margin-top: 3px;
  font-family: "Be Vietnam Pro", sans-serif;
  font-weight: 700;
  font-size: 16px;
  color: #E8DFD5;
  text-shadow: 0 2px 8px rgba(0,0,0,0.9);
}
/* Feature Pill Row */
.wh-pill-row {
  position: absolute;
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: center;
  z-index: 14;
}
.wh-lux-pill {
  padding: 12px 24px;
  border-radius: 14px;
  background: rgba(18, 12, 10, 0.88);
  border: 1.5px solid rgba(248, 205, 98, 0.72);
  box-shadow: 0 12px 28px rgba(0,0,0,0.65);
  font-family: "Montserrat", sans-serif;
  font-weight: 800;
  font-size: 20px;
  color: #FFE999;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
"""

def grad_text(id_prefix, text, cls_size="wh-title-lg", fill_cls="wh-gold-fill"):
    esc = html.escape(text)
    return f"""<span class="wh-grad-wrap {cls_size}" data-layout-allow-overlap>
      <span class="wh-grad-back" aria-hidden="true" data-layout-ignore>{esc}</span>
      <span id="{id_prefix}-sheen" class="wh-grad-front {fill_cls}" data-layout-allow-overlap>{esc}</span>
    </span>"""

def write_comp(filename, content):
    p = os.path.join(COMP_DIR, filename)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("Wrote composition:", filename)

# =========================================================================
# SLIDE 01 (05.00s - 09.33s, dur = 4.33s): 3 TRỤ CỘT ĐẲNG CẤP WINHAIR
# =========================================================================
write_comp("slide-01.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-01" data-width="1920" data-height="1080">
    <div id="s1-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s1-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="4.33" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s1-hdr" class="wh-header">
        <div class="wh-kicker">★ THƯƠNG HIỆU SALON TÓC NAM HÀNG ĐẦU ★</div>
        {grad_text("s1-ttl", "CHUẨN MỰC 5 SAO TẠI WIN HAIR SALON")}
        <div id="s1-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <div id="s1-c1" class="wh-card" style="left: 120px; top: 204px; width: 520px; height: 700px;">
        <video id="s1-v1" class="clip wh-vid-fill" src="assets/slides/v_cut_scissor.mp4" data-start="0" data-duration="4.33" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s1-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">TRỤ CỘT 01</span>
          <div class="wh-card-h3">DỊCH VỤ ĐA DẠNG</div>
          <div class="wh-card-p">Cắt tạo kiểu · Cạo mặt · Ráy tai · Gội dưỡng sinh · Massage</div>
        </div>
      </div>

      <div id="s1-c2" class="wh-card" style="left: 700px; top: 204px; width: 520px; height: 700px;">
        <video id="s1-v2" class="clip wh-vid-fill" src="assets/slides/v_vip_room.mp4" data-start="0" data-duration="4.33" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s1-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">TRỤ CỘT 02</span>
          <div class="wh-card-h3">KHÔNG GIAN ĐẲNG CẤP</div>
          <div class="wh-card-p">2 tầng sang trọng · Phòng VIP 1:1 riêng tư tuyệt đối</div>
        </div>
      </div>

      <div id="s1-c3" class="wh-card" style="left: 1280px; top: 204px; width: 520px; height: 700px;">
        <video id="s1-v3" class="clip wh-vid-fill" src="assets/slides/v_ear_light.mp4" data-start="0" data-duration="4.33" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s1-sh3" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">TRỤ CỘT 03</span>
          <div class="wh-card-h3">KTV CHUYÊN NGHIỆP</div>
          <div class="wh-card-p">Tay nghề chuẩn mực · Tận tâm phục vụ như Thượng Đế</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s1-hdr", {{ opacity: 0, y: -28, filter: "blur(12px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s1-flare", {{ scaleX: 0.1, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: 0.45, ease: "expo.out" }}, 0.12);
    tl.fromTo("#s1-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.85, ease: "power2.inOut" }}, 0.18);

    // Card 1 at 0.05s ("Dịch vụ đa dạng")
    tl.fromTo("#s1-c1", {{ opacity: 0, y: 85, scale: 0.9, rotateY: 14 }}, {{ opacity: 1, y: 0, scale: 1, rotateY: 0, duration: 0.45, ease: "back.out(1.25)" }}, 0.05);
    tl.fromTo("#s1-sh1", {{ xPercent: -120, opacity: 0.9 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 0.25);

    // Card 2 at 1.55s ("Không gian đẳng cấp")
    tl.fromTo("#s1-c2", {{ opacity: 0, y: 85, scale: 0.9, rotateY: 0 }}, {{ opacity: 1, y: 0, scale: 1, rotateY: 0, duration: 0.45, ease: "back.out(1.25)" }}, 1.50);
    tl.fromTo("#s1-sh2", {{ xPercent: -120, opacity: 0.9 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 1.72);

    // Card 3 at 2.45s ("Kỹ thuật viên chuyên nghiệp")
    tl.fromTo("#s1-c3", {{ opacity: 0, y: 85, scale: 0.9, rotateY: -14 }}, {{ opacity: 1, y: 0, scale: 1, rotateY: 0, duration: 0.45, ease: "back.out(1.25)" }}, 2.42);
    tl.fromTo("#s1-sh3", {{ xPercent: -120, opacity: 0.9 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 2.65);

    tl.fromTo("#s1-stage", {{ opacity: 1, scale: 1 }}, {{ opacity: 0, scale: 1.03, duration: 0.22, ease: "power2.in" }}, 4.09);
    window.__timelines["slide-01"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 02 (35.37s - 42.60s, dur = 7.23s): KHU GỘI ĐẦU 2 PHÂN KHU
# =========================================================================
write_comp("slide-02.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-02" data-width="1920" data-height="1080">
    <div id="s2-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s2-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="7.23" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s2-hdr" class="wh-header">
        <div class="wh-kicker">★ KHÔNG GIAN TẦNG 01 · KHU GỘI ĐẦU CHUYÊN BIỆT ★</div>
        {grad_text("s2-ttl", "KHU GỘI ĐẦU CHIA HẲN 2 PHÂN KHU RỘNG THOÁNG")}
        <div id="s2-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <!-- Left Wide Cinema Card -->
      <div id="s2-main" class="wh-card" style="left: 108px; top: 204px; width: 930px; height: 590px;">
        <video id="s2-vh1" class="clip wh-vid-fill" src="assets/slides/h_shampoo_zone1.mp4" data-start="0" data-duration="3.80" data-track-index="1" muted playsinline></video>
        <video id="s2-vh2" class="clip wh-vid-fill" src="assets/slides/h_shampoo_zone2.mp4" data-start="3.80" data-hf-media-start-basis="local" data-duration="3.43" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">QUY MÔ LỚN</span>
          <div class="wh-card-h3">ĐÔNG KHÁCH CỠ NÀO CŨNG KHÔNG PHẢI CHỜ</div>
          <div class="wh-card-p">Hệ thống giường gội hiện đại bố trí khoa học · Thoáng mát dễ chịu</div>
        </div>
      </div>

      <!-- Right 2 Vertical Cards -->
      <div id="s2-vc1" class="wh-card" style="left: 1072px; top: 204px; width: 356px; height: 590px;">
        <video id="s2-vv1" class="clip wh-vid-fill" src="assets/slides/v_wash_halo.mp4" data-start="0" data-duration="7.23" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">01</span>
          <div class="wh-card-h3">GIƯỜNG ÊM</div>
          <div class="wh-card-p">Vòi sen tròn dưỡng sinh</div>
        </div>
      </div>

      <div id="s2-vc2" class="wh-card" style="left: 1456px; top: 204px; width: 356px; height: 590px;">
        <video id="s2-vv2" class="clip wh-vid-fill" src="assets/slides/v_wash_foam.mp4" data-start="0" data-duration="7.23" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">02</span>
          <div class="wh-card-h3">BỒN SẠCH</div>
          <div class="wh-card-p">Vệ sinh khử khuẩn chuẩn</div>
        </div>
      </div>

      <!-- Feature Pills Above Caption Safe Zone -->
      <div class="wh-pill-row" style="left: 108px; right: 108px; top: 822px;">
        <div id="s2-p1" class="wh-lux-pill">✦ 2 KHU GỘI ĐẦU RIÊNG BIỆT</div>
        <div id="s2-p2" class="wh-lux-pill">✦ RỘNG RÃI · MÁT MẺ</div>
        <div id="s2-p3" class="wh-lux-pill">✦ PHỤC VỤ NHANH KHÔNG CHỜ ĐỢI</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s2-hdr", {{ opacity: 0, y: -24, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s2-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "expo.out" }}, 0.12);
    tl.fromTo("#s2-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 0.20);

    tl.fromTo("#s2-main", {{ opacity: 0, x: -70, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, 0.08);
    tl.fromTo("#s2-vc1", {{ opacity: 0, y: 70, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 0.32);
    tl.fromTo("#s2-vc2", {{ opacity: 0, y: 70, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 0.52);

    tl.fromTo("#s2-p1", {{ opacity: 0, y: 20, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out" }}, 1.80);
    tl.fromTo("#s2-p2", {{ opacity: 0, y: 20, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out" }}, 3.50);
    tl.fromTo("#s2-p3", {{ opacity: 0, y: 20, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out" }}, 5.00);

    tl.fromTo("#s2-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 6.99);
    window.__timelines["slide-02"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 02B (53.13s - 59.67s, dur = 6.54s): TẦNG 2 KHU VIP (YÊN TĨNH · KÍN ĐÁO · ÁNH ĐÈN DỊU)
# =========================================================================
write_comp("slide-02b.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-02b" data-width="1920" data-height="1080">
    <div id="s2b-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s2b-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="6.54" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s2b-hdr" class="wh-header" style="left: 220px; right: 260px;">
        <div class="wh-kicker">👑 ĐẶC QUYỀN TẦNG 02 · KHÔNG GIAN THƯ GIÃN THƯỢNG HẠNG 👑</div>
        {grad_text("s2b-ttl", "TẦNG 2 KHU VIP · TRẢI NGHIỆM NGHỈ DƯỠNG")}
        <div id="s2b-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <!-- 3 Vertical 9:16 Luxury VIP Cards -->
      <div id="s2b-c1" class="wh-card" style="left: 120px; top: 206px; width: 520px; height: 586px;">
        <video id="s2b-v1" class="clip wh-vid-fill" src="assets/slides/v_vip_welcome.mp4" data-start="0" data-duration="6.54" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2b-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">ĐẶC QUYỀN 01</span>
          <div class="wh-card-h3">KHÔNG GIAN YÊN TĨNH</div>
          <div class="wh-card-p">Tách biệt hoàn toàn khỏi sự ồn ào phố thị</div>
        </div>
      </div>

      <div id="s2b-c2" class="wh-card" style="left: 700px; top: 206px; width: 520px; height: 586px;">
        <video id="s2b-v2" class="clip wh-vid-fill" src="assets/slides/v_vip_room.mp4" data-start="0" data-duration="6.54" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2b-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">ĐẶC QUYỀN 02</span>
          <div class="wh-card-h3">RIÊNG TƯ &amp; KÍN ĐÁO</div>
          <div class="wh-card-p">Phòng VIP chuyên biệt · Thoải mái thả lỏng</div>
        </div>
      </div>

      <div id="s2b-c3" class="wh-card" style="left: 1280px; top: 206px; width: 520px; height: 586px;">
        <video id="s2b-v3" class="clip wh-vid-fill" src="assets/slides/v_vip_drink.mp4" data-start="0" data-duration="6.54" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2b-sh3" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">ĐẶC QUYỀN 03</span>
          <div class="wh-card-h3">ÁNH ĐÈN DỊU ÊM ÁI</div>
          <div class="wh-card-p">Ánh sáng ấm áp nâng niu giấc nghỉ thư thái</div>
        </div>
      </div>

      <div class="wh-pill-row" style="left: 120px; right: 120px; top: 818px;">
        <div id="s2b-p1" class="wh-lux-pill">✦ YÊN TĨNH TUYỆT ĐỐI</div>
        <div id="s2b-p2" class="wh-lux-pill">✦ KÍN ĐÁO RIÊNG TƯ</div>
        <div id="s2b-p3" class="wh-lux-pill">✦ ÁNH ĐÈN DỊU THƯ THÁI</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s2b-hdr", {{ opacity: 0, y: -24, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s2b-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "expo.out" }}, 0.12);
    tl.fromTo("#s2b-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 0.22);

    tl.fromTo("#s2b-c1", {{ opacity: 0, y: 75, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.44, ease: "back.out(1.22)" }}, 0.10);
    tl.fromTo("#s2b-c2", {{ opacity: 0, y: 75, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.44, ease: "back.out(1.22)" }}, 0.32);
    tl.fromTo("#s2b-c3", {{ opacity: 0, y: 75, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.44, ease: "back.out(1.22)" }}, 0.54);

    // Sync sheens + luxury pills to VO hits: Yên tĩnh (2.75s) | Kín đáo (3.44s) | Ánh đèn dịu (4.27s)
    tl.fromTo("#s2b-sh1", {{ xPercent: -120, opacity: 0.95 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 2.75);
    tl.fromTo("#s2b-p1", {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "power3.out" }}, 2.75);

    tl.fromTo("#s2b-sh2", {{ xPercent: -120, opacity: 0.95 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 3.44);
    tl.fromTo("#s2b-p2", {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "power3.out" }}, 3.44);

    tl.fromTo("#s2b-sh3", {{ xPercent: -120, opacity: 0.95 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 4.27);
    tl.fromTo("#s2b-p3", {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, ease: "power3.out" }}, 4.27);

    tl.fromTo("#s2b-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 6.30);
    window.__timelines["slide-02b"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 03 (80.23s - 87.47s, dur = 7.24s): 5-PANEL VERTICAL VIP ACCORDION
# =========================================================================
write_comp("slide-03.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}
    .s3-col {{ width: 326px; height: 676px; top: 208px; }}
  </style>
  <div id="root" data-composition-id="slide-03" data-width="1920" data-height="1080">
    <div id="s3-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s3-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="7.24" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s3-hdr" class="wh-header">
        <div class="wh-kicker">★ ĐẶC QUYỀN PHÒNG VIP 1:1 · NẰM MỘT CHỖ TẬN HƯỞNG TẤT CẢ ★</div>
        {grad_text("s3-ttl", "TRỌN GÓI 5 TRẢI NGHIỆM THƯ GIÃN HOÀNG GIA")}
        <div id="s3-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <div id="s3-c1" class="wh-card s3-col" style="left: 98px;">
        <video id="s3-v1" class="clip wh-vid-fill" src="assets/slides/v_wash_close.mp4" data-start="0" data-duration="7.24" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">01</span><div class="wh-card-h3">GỘI ĐẦU</div><div class="wh-card-p">Dưỡng sinh thư thái</div></div>
      </div>

      <div id="s3-c2" class="wh-card s3-col" style="left: 448px;">
        <video id="s3-v2" class="clip wh-vid-fill" src="assets/slides/v_msg_neck.mp4" data-start="0" data-duration="7.24" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">02</span><div class="wh-card-h3">MASSAGE</div><div class="wh-card-p">Cổ vai gáy chuyên sâu</div></div>
      </div>

      <div id="s3-c3" class="wh-card s3-col" style="left: 798px;">
        <video id="s3-v3" class="clip wh-vid-fill" src="assets/slides/v_ear_relax.mp4" data-start="0" data-duration="7.24" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">03</span><div class="wh-card-h3">RÁY TAI</div><div class="wh-card-p">Êm dịu chuẩn Hoàng Gia</div></div>
      </div>

      <div id="s3-c4" class="wh-card s3-col" style="left: 1148px;">
        <video id="s3-v4" class="clip wh-vid-fill" src="assets/slides/v_shave_care.mp4" data-start="0" data-duration="7.24" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">04</span><div class="wh-card-h3">ĐẮP MẶT</div><div class="wh-card-p">Cấp ẩm sáng mịn da</div></div>
      </div>

      <div id="s3-c5" class="wh-card s3-col" style="left: 1498px;">
        <video id="s3-v5" class="clip wh-vid-fill" src="assets/slides/v_msg_chill.mp4" data-start="0" data-duration="7.24" data-track-index="5" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">05</span><div class="wh-card-h3">LỘT MỤN</div><div class="wh-card-p">Làm sạch sâu lỗ chân lông</div></div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s3-hdr", {{ opacity: 0, y: -25, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s3-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "expo.out" }}, 0.12);
    tl.fromTo("#s3-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.25);

    const cues = [
      ["#s3-c1", 0.08],
      ["#s3-c2", 0.65],
      ["#s3-c3", 1.25],
      ["#s3-c4", 2.10],
      ["#s3-c5", 2.90],
    ];
    cues.forEach(([sel, t]) => {{
      tl.fromTo(sel, {{ opacity: 0, y: 95, scale: 0.88 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.42, ease: "back.out(1.28)" }}, t);
    }});

    tl.fromTo("#s3-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 7.00);
    window.__timelines["slide-03"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 04 (88.70s - 100.00s, dur = 11.30s): DỊCH VỤ 01 - CẮT TÓC & TẠO KIỂU
# =========================================================================
write_comp("slide-04.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-04" data-width="1920" data-height="1080">
    <div id="s4-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s4-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="11.30" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s4-hdr" class="wh-header">
        <div class="wh-kicker">★ DỊCH VỤ MŨI NHỌN 01 · NGHỆ THUẬT TÓC NAM ★</div>
        {grad_text("s4-ttl", "CẮT TÓC & TẠO KIỂU CHUẨN FORM QUÝ ÔNG")}
        <div id="s4-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <!-- Left Vertical Hero: Scissor Fade -> Blowdry Form -->
      <div id="s4-left" class="wh-card" style="left: 108px; top: 204px; width: 450px; height: 696px;">
        <video id="s4-vv1" class="clip wh-vid-fill" src="assets/slides/v_cut_scissor.mp4" data-start="0" data-duration="6.20" data-track-index="1" muted playsinline></video>
        <video id="s4-vv2" class="clip wh-vid-fill" src="assets/slides/v_cut_blowdry.mp4" data-start="6.20" data-hf-media-start-basis="local" data-duration="5.10" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s4-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">MASTER STYLIST</span>
          <div class="wh-card-h3">CHUẨN FORM SOÁI CA</div>
          <div class="wh-card-p">Sấy vuốt vào nếp · Lột xác diện mạo tức thì</div>
        </div>
      </div>

      <!-- Center Vertical Barber Action -->
      <div id="s4-mid" class="wh-card" style="left: 586px; top: 204px; width: 450px; height: 696px;">
        <video id="s4-vv3" class="clip wh-vid-fill" src="assets/slides/v_cut_angle.mp4" data-start="0" data-duration="5.40" data-track-index="3" muted playsinline></video>
        <video id="s4-vv4" class="clip wh-vid-fill" src="assets/slides/v_cut_barber.mp4" data-start="5.40" data-hf-media-start-basis="local" data-duration="5.90" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">PRECISION CUT</span>
          <div class="wh-card-h3">TỪNG ĐƯỜNG KÉO TỈ MỈ</div>
          <div class="wh-card-p">Thiết kế riêng theo từng dáng khuôn mặt</div>
        </div>
      </div>

      <!-- Right Stacked Horizontal Detail + Checklist -->
      <div id="s4-rt-top" class="wh-card" style="left: 1064px; top: 204px; width: 748px; height: 420px;">
        <video id="s4-vh1" class="clip wh-vid-fill" src="assets/slides/h_barber_wide.mp4" data-start="0" data-duration="5.20" data-track-index="5" muted playsinline></video>
        <video id="s4-vh2" class="clip wh-vid-fill" src="assets/slides/h_fade_close.mp4" data-start="5.20" data-hf-media-start-basis="local" data-duration="6.10" data-track-index="6" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">FADE & TEXTURE</span>
          <div class="wh-card-h3">ĐƯỜNG FADE GỌN GÀNG SẮC NÉT</div>
        </div>
      </div>

      <!-- Right Bottom 3 Kinetic Step Pills -->
      <div style="position: absolute; left: 1064px; top: 644px; width: 748px; display: flex; flex-direction: column; gap: 14px; z-index: 15;">
        <div id="s4-b1" class="wh-lux-pill" style="display: flex; justify-content: space-between;">
          <span>01 · TƯ VẤN KIỂU KỸ CÀNG</span><span style="color:#FFF;">★★★★★</span>
        </div>
        <div id="s4-b2" class="wh-lux-pill" style="display: flex; justify-content: space-between;">
          <span>02 · ĐƯỜNG KÉO & FADE CHUẨN MỰC</span><span style="color:#FFF;">SẮC NÉT</span>
        </div>
        <div id="s4-b3" class="wh-lux-pill" style="display: flex; justify-content: space-between;">
          <span>03 · TẠO KIỂU VÀO FORM ĐẲNG CẤP</span><span style="color:#FFF;">BẢNH TRAI</span>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s4-hdr", {{ opacity: 0, y: -28, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s4-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.48, ease: "expo.out" }}, 0.14);
    tl.fromTo("#s4-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.25);

    tl.fromTo("#s4-left", {{ opacity: 0, x: -70, scale: 0.92 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 0.10);
    tl.fromTo("#s4-sh1", {{ xPercent: -120, opacity: 0.9 }}, {{ xPercent: 140, opacity: 0, duration: 0.70, ease: "power2.out" }}, 0.35);
    tl.fromTo("#s4-mid", {{ opacity: 0, y: 70, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 0.30);
    tl.fromTo("#s4-rt-top", {{ opacity: 0, x: 70, scale: 0.92 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, 0.48);

    tl.fromTo("#s4-b1", {{ opacity: 0, x: 50, filter: "blur(8px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 2.80);
    tl.fromTo("#s4-b2", {{ opacity: 0, x: 50, filter: "blur(8px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 4.80);
    tl.fromTo("#s4-b3", {{ opacity: 0, x: 50, filter: "blur(8px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 7.60);

    tl.fromTo("#s4-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 11.06);
    window.__timelines["slide-04"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 05 (100.00s - 104.97s, dur = 4.97s): DỊCH VỤ 02 - CẠO MẶT ÊM ÁI
# =========================================================================
write_comp("slide-05.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-05" data-width="1920" data-height="1080">
    <div id="s5-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s5-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="4.97" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s5-hdr" class="wh-header">
        <div class="wh-kicker">★ DỊCH VỤ 02 · CHĂM SÓC DIỆN MẠO SÁNG BỪNG ★</div>
        {grad_text("s5-ttl", "CẠO MẶT SẠCH SÂU · LƯỠI DAO ÊM ÁI MỊN MÀNG")}
        <div id="s5-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <div id="s5-c1" class="wh-card" style="left: 116px; top: 206px; width: 510px; height: 694px;">
        <video id="s5-v1" class="clip wh-vid-fill" src="assets/slides/v_shave_bed.mp4" data-start="0" data-duration="4.97" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">BƯỚC 01</span>
          <div class="wh-card-h3">SẠCH SẼ GỌN GÀNG</div>
          <div class="wh-card-p">Làm mềm râu & làm dịu làn da</div>
        </div>
      </div>

      <div id="s5-c2" class="wh-card" style="left: 660px; top: 194px; width: 600px; height: 714px; border-width: 3px;">
        <video id="s5-v2" class="clip wh-vid-fill" src="assets/slides/v_shave_macro.mp4" data-start="0" data-duration="4.97" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s5-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">TAY NGHỀ ĐIÊU LUYỆN</span>
          <div class="wh-card-h3">LƯỠI DAO LƯỚT ÊM TAY</div>
          <div class="wh-card-p">Mịn màng không rát · Nhìn phong độ hẳn</div>
        </div>
      </div>

      <div id="s5-c3" class="wh-card" style="left: 1294px; top: 206px; width: 510px; height: 694px;">
        <video id="s5-v3" class="clip wh-vid-fill" src="assets/slides/v_shave_care.mp4" data-start="0" data-duration="4.97" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">HOÀN THIỆN</span>
          <div class="wh-card-h3">SÁNG MỊN TỰ TIN</div>
          <div class="wh-card-p">Thần thái rạng ngời chuẩn quý ông</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s5-hdr", {{ opacity: 0, y: -24, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s5-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.42, ease: "expo.out" }}, 0.10);
    tl.fromTo("#s5-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.85, ease: "power2.inOut" }}, 0.18);

    tl.fromTo("#s5-c2", {{ opacity: 0, scale: 0.88, y: 60 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.42, ease: "back.out(1.25)" }}, 0.06);
    tl.fromTo("#s5-sh2", {{ xPercent: -130, opacity: 0.95 }}, {{ xPercent: 140, opacity: 0, duration: 0.72, ease: "power2.out" }}, 0.32);
    tl.fromTo("#s5-c1", {{ opacity: 0, x: -70, rotateY: 12 }}, {{ opacity: 1, x: 0, rotateY: 0, duration: 0.42, ease: "power3.out" }}, 0.22);
    tl.fromTo("#s5-c3", {{ opacity: 0, x: 70, rotateY: -12 }}, {{ opacity: 1, x: 0, rotateY: 0, duration: 0.42, ease: "power3.out" }}, 0.36);

    tl.fromTo("#s5-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.20, ease: "power2.in" }}, 4.75);
    window.__timelines["slide-05"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 06 (104.97s - 114.07s, dur = 9.10s): DỊCH VỤ 03 - RÁY TAI HOÀNG GIA
# =========================================================================
write_comp("slide-06.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-06" data-width="1920" data-height="1080">
    <div id="s6-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s6-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="9.10" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s6-hdr" class="wh-header">
        <div class="wh-kicker">★ DỊCH VỤ 03 · THƯ GIÃN THÍNH GIÁC CHUYÊN SÂU ★</div>
        {grad_text("s6-ttl", "RÁY TAI ÊM DỊU & MẶT NẠ MẮT THƯ GIÃN")}
        <div id="s6-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <div id="s6-main" class="wh-card" style="left: 108px; top: 204px; width: 890px; height: 590px;">
        <video id="s6-vh" class="clip wh-vid-fill" src="assets/slides/h_ear_main.mp4" data-start="0" data-duration="9.10" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">CHUẨN SPA ĐẶC QUYỀN</span>
          <div class="wh-card-h3">NẰM MỘT LÁT LÀ CẢ NGƯỜI THẢ LỎNG</div>
          <div class="wh-card-p">Dụng cụ khử trùng sạch sẽ · Thao tác nhẹ như lông hồng</div>
        </div>
      </div>

      <div id="s6-vc1" class="wh-card" style="left: 1028px; top: 204px; width: 376px; height: 590px;">
        <video id="s6-vv1" class="clip wh-vid-fill" src="assets/slides/v_ear_light.mp4" data-start="0" data-duration="9.10" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">SOI RÕ</span>
          <div class="wh-card-h3">ĐÈN CHUYÊN DỤNG</div>
          <div class="wh-card-p">Chuẩn xác từng chi tiết</div>
        </div>
      </div>

      <div id="s6-vc2" class="wh-card" style="left: 1432px; top: 204px; width: 376px; height: 590px;">
        <video id="s6-vv2" class="clip wh-vid-fill" src="assets/slides/v_ear_relax.mp4" data-start="0" data-duration="9.10" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">ÊM ÁI</span>
          <div class="wh-card-h3">MẶT NẠ CHE SÁNG</div>
          <div class="wh-card-p">Dễ chịu chìm vào giấc ngủ</div>
        </div>
      </div>

      <div class="wh-pill-row" style="left: 108px; right: 108px; top: 822px;">
        <div id="s6-p1" class="wh-lux-pill">✦ ÁNH ĐÈN SOI RÕ AN TOÀN</div>
        <div id="s6-p2" class="wh-lux-pill">✦ MẶT NẠ MẮT ÊM DỊU</div>
        <div id="s6-p3" class="wh-lux-pill">✦ TAY NGHỀ KHÉO LÉO · KHÔNG ĐAU</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s6-hdr", {{ opacity: 0, y: -24, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s6-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "expo.out" }}, 0.12);
    tl.fromTo("#s6-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 0.22);

    tl.fromTo("#s6-main", {{ opacity: 0, x: -65, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, 0.08);
    tl.fromTo("#s6-vc1", {{ opacity: 0, y: 65, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 0.30);
    tl.fromTo("#s6-vc2", {{ opacity: 0, y: 65, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 0.50);

    tl.fromTo("#s6-p1", {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28 }}, 0.80);
    tl.fromTo("#s6-p2", {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28 }}, 2.30);
    tl.fromTo("#s6-p3", {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28 }}, 4.60);

    tl.fromTo("#s6-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 8.86);
    window.__timelines["slide-06"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 07 (114.07s - 127.00s, dur = 12.93s): GỘI ĐẦU XÔNG HƠI & TAM ĐẠI MASSAGE
# =========================================================================
write_comp("slide-07.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-07" data-width="1920" data-height="1080">
    <div id="s7-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s7-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="12.93" data-track-index="0" muted playsinline data-layout-ignore></video>

      <!-- PHASE A (0.00s - 3.83s): GỘI ĐẦU · XÔNG HƠI · MASSAGE MẶT -->
      <div id="s7-pha" style="position: absolute; inset: 0;">
        <div id="s7a-hdr" class="wh-header">
          <div class="wh-kicker">★ DỊCH VỤ 04A · THẢI ĐỘC & PHỤC HỒI NĂNG LƯỢNG ★</div>
          {grad_text("s7a-ttl", "GỘI ĐẦU · XÔNG HƠI · MASSAGE MẶT XẢ CĂNG THẲNG")}
          <div class="wh-flare-bar" data-layout-ignore></div>
        </div>

        <div id="s7a-c1" class="wh-card" style="left: 108px; top: 204px; width: 420px; height: 690px;">
          <video id="s7a-v1" class="clip wh-vid-fill" src="assets/slides/v_wash_halo.mp4" data-start="0" data-duration="3.83" data-track-index="1" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><span class="wh-badge-num">01</span><div class="wh-card-h3">GỘI DƯỠNG SINH</div></div>
        </div>

        <div id="s7a-c2" class="wh-card" style="left: 556px; top: 204px; width: 808px; height: 690px;">
          <video id="s7a-v2" class="clip wh-vid-fill" src="assets/slides/h_steam_face.mp4" data-start="0" data-duration="3.83" data-track-index="2" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><span class="wh-badge-num">02 · XÔNG HƠI NÓNG</span><div class="wh-card-h3">XẢ SẠCH BAO NHIÊU MỆT MỎI</div></div>
        </div>

        <div id="s7a-c3" class="wh-card" style="left: 1392px; top: 204px; width: 420px; height: 690px;">
          <video id="s7a-v3" class="clip wh-vid-fill" src="assets/slides/v_wash_foam.mp4" data-start="0" data-duration="3.83" data-track-index="3" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><span class="wh-badge-num">03</span><div class="wh-card-h3">MASSAGE MẶT</div></div>
        </div>
      </div>

      <!-- PHASE B (3.83s - 12.93s): MASSAGE TAY · CHÂN · BODY -->
      <div id="s7-phb" style="position: absolute; inset: 0; opacity: 0;">
        <div id="s7b-hdr" class="wh-header">
          <div class="wh-kicker">★ DỊCH VỤ 04B · TRỊ LIỆU BẤM HUYỆT CHUYÊN SÂU ★</div>
          {grad_text("s7b-ttl", "MASSAGE TAY · CHÂN · BODY — LỰC TAY CHẮC KHỎE RE")}
          <div class="wh-flare-bar" data-layout-ignore></div>
        </div>

        <div id="s7b-c1" class="wh-card" style="left: 116px; top: 204px; width: 520px; height: 594px;">
          <video id="s7b-v1" class="clip wh-vid-fill" src="assets/slides/v_msg_arm.mp4" data-start="3.83" data-hf-media-start-basis="local" data-duration="9.10" data-track-index="4" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">TRỊ LIỆU 01</span>
            <div class="wh-card-h3">MASSAGE TAY — HẾT MỎI</div>
            <div class="wh-card-p">Thả lỏng khớp cổ tay & cánh tay</div>
          </div>
        </div>

        <div id="s7b-c2" class="wh-card" style="left: 700px; top: 204px; width: 520px; height: 594px;">
          <video id="s7b-v2" class="clip wh-vid-fill" src="assets/slides/v_msg_foot.mp4" data-start="3.83" data-hf-media-start-basis="local" data-duration="9.10" data-track-index="5" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">TRỊ LIỆU 02</span>
            <div class="wh-card-h3">MASSAGE CHÂN — HẾT NẶNG</div>
            <div class="wh-card-p">Khai thông huyệt đạo lòng bàn chân</div>
          </div>
        </div>

        <div id="s7b-c3" class="wh-card" style="left: 1284px; top: 204px; width: 520px; height: 594px;">
          <video id="s7b-v3" class="clip wh-vid-fill" src="assets/slides/v_msg_neck.mp4" data-start="3.83" data-hf-media-start-basis="local" data-duration="9.10" data-track-index="6" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">TRỊ LIỆU 03</span>
            <div class="wh-card-h3">MASSAGE BODY — HẾT UỂ OẢI</div>
            <div class="wh-card-p">Cổ vai gáy & lưng phục hồi tức thì</div>
          </div>
        </div>

        <div class="wh-pill-row" style="left: 116px; right: 116px; top: 824px;">
          <div id="s7b-p1" class="wh-lux-pill">✦ KTV LỰC TAY CHẮC</div>
          <div id="s7b-p2" class="wh-lux-pill">✦ BẤM ĐÚNG HUYỆT ĐẠO</div>
          <div id="s7b-p3" class="wh-lux-pill">✦ LÀM XONG KHỎE RE!</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // Phase A
    gsap.set("#s7-phb", {{ opacity: 0 }});
    tl.fromTo("#s7a-hdr", {{ opacity: 0, y: -24 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s7a-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.90, ease: "power2.inOut" }}, 0.18);
    tl.fromTo("#s7a-c1", {{ opacity: 0, x: -60, scale: 0.92 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.38, ease: "power3.out" }}, 0.08);
    tl.fromTo("#s7a-c2", {{ opacity: 0, y: 50, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.38, ease: "power3.out" }}, 0.20);
    tl.fromTo("#s7a-c3", {{ opacity: 0, x: 60, scale: 0.92 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.38, ease: "power3.out" }}, 0.32);
    tl.fromTo("#s7-pha", {{ opacity: 1, x: 0 }}, {{ opacity: 0, x: -90, duration: 0.24, ease: "power2.in" }}, 3.60);

    // Phase B starts at 3.83s (117.90s abs)
    tl.fromTo("#s7-phb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.16 }}, 3.83);
    tl.fromTo("#s7b-hdr", {{ opacity: 0, y: -24 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power3.out" }}, 3.85);
    tl.fromTo("#s7b-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 4.10);

    // VO: 117.90s (rel 3.83) Massage tay -> 119.67s (rel 5.60) Massage chân -> 121.03s (rel 6.96) Massage body
    tl.fromTo("#s7b-c1", {{ opacity: 0, y: 80, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.25)" }}, 3.86);
    tl.fromTo("#s7b-c2", {{ opacity: 0, y: 80, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.25)" }}, 5.55);
    tl.fromTo("#s7b-c3", {{ opacity: 0, y: 80, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.25)" }}, 6.92);

    // VO: 122.93s (rel 8.86) Lực tay chắc -> 124.17s (rel 10.10) Bấm đúng chỗ -> 125.63s (rel 11.56) Làm xong khỏe re
    tl.fromTo("#s7b-p1", {{ opacity: 0, y: 20, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26 }}, 8.82);
    tl.fromTo("#s7b-p2", {{ opacity: 0, y: 20, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26 }}, 10.06);
    tl.fromTo("#s7b-p3", {{ opacity: 0, y: 20, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26 }}, 11.50);

    tl.fromTo("#s7-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 12.69);
    window.__timelines["slide-07"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 08 (127.00s - 136.70s, dur = 9.70s): CHĂM SÓC MÓNG TAY & MÓNG CHÂN
# =========================================================================
write_comp("slide-08.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}</style>
  <div id="root" data-composition-id="slide-08" data-width="1920" data-height="1080">
    <div id="s8-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s8-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="9.70" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s8-hdr" class="wh-header">
        <div class="wh-kicker">★ DỊCH VỤ 05 · CHỈN CHU ĐẾN TỪNG CHI TIẾT NHỎ NHẤT ★</div>
        {grad_text("s8-ttl", "CHĂM SÓC MÓNG TAY & MÓNG CHÂN SẠCH SẼ GỌN GÀNG")}
        <div id="s8-flare" class="wh-flare-bar" data-layout-ignore></div>
      </div>

      <div id="s8-c1" class="wh-card" style="left: 112px; top: 206px; width: 640px; height: 688px;">
        <video id="s8-v1" class="clip wh-vid-fill" src="assets/slides/h_nail_hand.mp4" data-start="0" data-duration="9.70" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">CHĂM SÓC ĐÔI TAY</span>
          <div class="wh-card-h3">BẤM MÓNG TAY TỈ MỈ</div>
          <div class="wh-card-p">Kềm sạch khử khuẩn · Đường cắt gọn êm</div>
        </div>
      </div>

      <div id="s8-c2" class="wh-card" style="left: 780px; top: 206px; width: 640px; height: 688px;">
        <video id="s8-v2" class="clip wh-vid-fill" src="assets/slides/h_nail_foot.mp4" data-start="0" data-duration="9.70" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">CHĂM SÓC ĐÔI CHÂN</span>
          <div class="wh-card-h3">CẮT MÓNG CHÂN SẠCH SẼ</div>
          <div class="wh-card-p">Nhẹ nhàng thư giãn trên ghế êm</div>
        </div>
      </div>

      <div id="s8-c3" class="wh-card" style="left: 1448px; top: 206px; width: 360px; height: 688px;">
        <video id="s8-v3" class="clip wh-vid-fill" src="assets/slides/v_vip_drink.mp4" data-start="0" data-duration="9.70" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <span class="wh-badge-num">VIP RELAX</span>
          <div class="wh-card-h3">THƯ THÁI TUYỆT ĐỐI</div>
          <div class="wh-card-p">Vừa làm đẹp vừa thưởng thức nước mát</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s8-hdr", {{ opacity: 0, y: -24, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.30, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s8-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "expo.out" }}, 0.12);
    tl.fromTo("#s8-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 0.25);

    tl.fromTo("#s8-c1", {{ opacity: 0, x: -70, scale: 0.93 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s8-c2", {{ opacity: 0, y: 70, scale: 0.93 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 0.35);
    tl.fromTo("#s8-c3", {{ opacity: 0, x: 70, scale: 0.93 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, 0.55);

    tl.fromTo("#s8-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 9.46);
    window.__timelines["slide-08"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 09 (255.77s - 266.50s, dur = 10.73s): TRANSPARENT RIGHT-SIDE 6-CARD COMBO OVERLAY
# =========================================================================
write_comp("slide-09.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}
    .s9-backdrop {{
      position: absolute;
      right: 0;
      top: 0;
      width: 940px;
      height: 1080px;
      background: linear-gradient(270deg, rgba(8, 5, 4, 0.90) 0%, rgba(12, 8, 6, 0.72) 68%, transparent 100%);
      pointer-events: none;
    }}
    .s9-mini {{ width: 252px; height: 326px; border-radius: 16px; }}
    .s9-mini .wh-card-h3 {{ font-size: 23px; }}
    .s9-mini .wh-badge-num {{ font-size: 13px; padding: 3px 9px; }}
  </style>
  <div id="root" data-composition-id="slide-09" data-width="1920" data-height="1080">
    <div id="s9-stage" class="wh-stage">
      <div id="s9-shade" class="s9-backdrop" data-layout-ignore></div>

      <div id="s9-hdr" style="position: absolute; left: 1010px; right: 64px; top: 96px; text-align: center; z-index: 12;">
        <div class="wh-kicker" style="font-size: 14px; margin-bottom: 4px;">★ COMBO TRỌN GÓI KHÁCH YÊU THÍCH ★</div>
        <div style="margin-top: 2px;">
          {grad_text("s9-ttl", "1 COMBO · 6 BƯỚC THƯ GIÃN")}
        </div>
      </div>

      <!-- 3x2 Grid of Vertical Cards on Right Half (x: 1020..1824, y: 228..896) -->
      <div id="s9-c1" class="wh-card s9-mini" style="left: 1020px; top: 226px;">
        <video id="s9-v1" class="clip wh-vid-fill" src="assets/slides/v_cut_angle.mp4" data-start="0" data-duration="10.73" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 01</span><div class="wh-card-h3">CẮT TÓC LUÔN</div></div>
      </div>

      <div id="s9-c2" class="wh-card s9-mini" style="left: 1292px; top: 226px;">
        <video id="s9-v2" class="clip wh-vid-fill" src="assets/slides/v_wash_halo.mp4" data-start="0" data-duration="10.73" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 02</span><div class="wh-card-h3">GỘI ĐẦU LUÔN</div></div>
      </div>

      <div id="s9-c3" class="wh-card s9-mini" style="left: 1564px; top: 226px;">
        <video id="s9-v3" class="clip wh-vid-fill" src="assets/slides/v_shave_care.mp4" data-start="0" data-duration="10.73" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 03</span><div class="wh-card-h3">RỬA MẶT SẠCH</div></div>
      </div>

      <div id="s9-c4" class="wh-card s9-mini" style="left: 1020px; top: 568px;">
        <video id="s9-v4" class="clip wh-vid-fill" src="assets/slides/v_msg_foot.mp4" data-start="0" data-duration="10.73" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 04</span><div class="wh-card-h3">CẮT MÓNG TAY CHÂN</div></div>
      </div>

      <div id="s9-c5" class="wh-card s9-mini" style="left: 1292px; top: 568px;">
        <video id="s9-v5" class="clip wh-vid-fill" src="assets/slides/v_ear_light.mp4" data-start="0" data-duration="10.73" data-track-index="5" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 05</span><div class="wh-card-h3">RÁY TAI ÊM RU</div></div>
      </div>

      <div id="s9-c6" class="wh-card s9-mini" style="left: 1564px; top: 568px;">
        <video id="s9-v6" class="clip wh-vid-fill" src="assets/slides/v_msg_neck.mp4" data-start="0" data-duration="10.73" data-track-index="6" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 06</span><div class="wh-card-h3">MASSAGE CỔ VAI GÁY</div></div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s9-shade", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.0);
    tl.fromTo("#s9-hdr", {{ opacity: 0, x: 40 }}, {{ opacity: 1, x: 0, duration: 0.32, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s9-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.90, ease: "power2.inOut" }}, 0.30);

    // Synced to customer's exact words (255.77s base):
    // 256.80s (1.03s): cắt tóc luôn | 258.97s (3.20s): gội đầu luôn | 260.13s (4.36s): rửa mặt luôn
    // 261.10s (5.33s): cắt móng tay chân | 262.83s (7.06s): ngoáy tai | 264.17s (8.40s): massage cổ vai gáy
    const pops = [
      ["#s9-c1", 0.95],
      ["#s9-c2", 3.12],
      ["#s9-c3", 4.30],
      ["#s9-c4", 5.28],
      ["#s9-c5", 7.00],
      ["#s9-c6", 8.35],
    ];
    pops.forEach(([sel, t]) => {{
      tl.fromTo(sel, {{ opacity: 0, scale: 0.78, y: 36 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.36, ease: "back.out(1.35)" }}, t);
    }});

    tl.fromTo("#s9-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, 10.45);
    window.__timelines["slide-09"] = tl;
  </script>
</template>
""")

# =========================================================================
# SLIDE 10 (279.80s - 307.57s, dur = 27.77s): ĐẠI TIỆC 3 ƯU ĐÃI & 2 CƠ SỞ
#   Beat 1 (0.00s - 4.70s | 279.80s - 284.50s): THỨ 2 - THỨ 6 GIẢM NGAY 20%
#   Beat 2 (4.70s - 11.33s | 284.50s - 291.13s): COMBO 129K (CẮT-CẠO-RÁY-XẢ)
#   Beat 3 (11.33s - 22.40s | 291.13s - 302.20s): COMBO NGỦ TRƯA 30 PHÚT 79K
#   Beat 4 (22.40s - 27.77s | 302.20s - 307.57s): HỆ THỐNG 2 CƠ SỞ NHA TRANG
# =========================================================================
write_comp("slide-10.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}
    .wh-mega-num {{
      font-family: "Asap Condensed", sans-serif;
      font-weight: 900;
      font-size: 144px;
      line-height: 1.18;
      letter-spacing: 0.02em;
    }}
    .wh-center-badge {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: 780px;
      margin-left: -390px;
      margin-top: -175px;
      padding: 26px 38px;
      border-radius: 28px;
      background: radial-gradient(circle at 50% 25%, rgba(44, 14, 12, 0.97), rgba(12, 7, 6, 0.98));
      border: 3px solid #F8CE6A;
      box-shadow: 0 30px 80px rgba(0,0,0,0.92), 0 0 55px rgba(245, 192, 66, 0.45);
      text-align: center;
      z-index: 25;
    }}
  </style>
  <div id="root" data-composition-id="slide-10" data-width="1920" data-height="1080">
    <div id="s10-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-grid" data-layout-ignore></div>
      <video id="s10-bk1" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="12.0" data-track-index="0" muted playsinline data-layout-ignore></video>
      <video id="s10-bk2" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="12.0" data-hf-media-start-basis="local" data-duration="12.0" data-track-index="11" muted playsinline data-layout-ignore></video>
      <video id="s10-bk3" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="24.0" data-hf-media-start-basis="local" data-duration="3.77" data-track-index="12" muted playsinline data-layout-ignore></video>

      <!-- ================= BEAT 1 (0.00s - 4.70s): GIẢM NGAY 20% ================= -->
      <div id="s10-b1" style="position: absolute; inset: 0;">
        <div class="wh-header">
          <div class="wh-kicker">★ ĐẠI TIỆC ƯU ĐÃI KHUNG GIỜ VÀNG ★</div>
          {grad_text("s10-b1-ttl", "THỨ 2 ĐẾN THỨ 6 · ĐI SỚM GIÁ NGON")}
          <div class="wh-flare-bar" data-layout-ignore></div>
        </div>

        <div id="s10-b1-vidwrap" class="wh-card" style="left: 112px; top: 210px; width: 960px; height: 676px;">
          <video id="s10-b1-v" class="clip wh-vid-fill" src="assets/slides/h_promo_salon.mp4" data-start="0" data-duration="4.70" data-track-index="1" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">ƯU ĐÃI TUẦN</span>
            <div class="wh-card-h3">ÁP DỤNG KHUNG GIỜ VÀNG THỨ 2 – THỨ 6</div>
            <div class="wh-card-p">Trải nghiệm dịch vụ 5 sao với chi phí siêu tiết kiệm</div>
          </div>
        </div>

        <div id="s10-b1-offer" class="wh-card" style="left: 1108px; top: 210px; width: 700px; height: 676px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 36px; background: radial-gradient(circle at 50% 30%, #590B10 0%, #1C0708 100%);">
          <div class="wh-kicker" style="margin-bottom: 18px;">ƯU ĐÃI ĐẶC BIỆT</div>
          <div style="font-family: 'Asap Condensed', sans-serif; font-weight: 900; font-size: 46px; color: #FFF4D2; margin-bottom: 6px;">GIẢM NGAY</div>
          {grad_text("s10-20pct", "-20%", "wh-mega-num", "wh-gold-fill")}
          <div class="wh-flare-bar" style="width: 380px; margin: 18px 0;" data-layout-ignore></div>
          <div style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 26px; color: #FFE38E;">THỨ 2 – THỨ 6 HÀNG TUẦN</div>
          <div style="margin-top: 10px; font-family: 'Be Vietnam Pro', sans-serif; font-weight: 700; font-size: 20px; color: #FFFFFF;">Đi sớm thảnh thơi · Giá cực hời!</div>
        </div>
      </div>

      <!-- ================= BEAT 2 (4.70s - 11.33s): SIÊU COMBO 129K ================= -->
      <div id="s10-b2" style="position: absolute; inset: 0; opacity: 0;">
        <!-- 2x2 Bento Grid covering full safe zone -->
        <div id="s10-q1" class="wh-card" style="left: 96px; top: 68px; width: 848px; height: 420px;">
          <video id="s10-qv1" class="clip wh-vid-fill" src="assets/slides/v_cut_barber.mp4" data-start="4.70" data-hf-media-start-basis="local" data-duration="6.63" data-track-index="2" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 01</span><div class="wh-card-h3">CẮT TÓC CHUẨN FORM</div></div>
        </div>

        <div id="s10-q2" class="wh-card" style="left: 976px; top: 68px; width: 848px; height: 420px;">
          <video id="s10-qv2" class="clip wh-vid-fill" src="assets/slides/v_shave_macro.mp4" data-start="4.70" data-hf-media-start-basis="local" data-duration="6.63" data-track-index="3" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption" style="text-align: right;"><span class="wh-badge-num">BƯỚC 02</span><div class="wh-card-h3">CẠO MẶT SÁNG MỊN</div></div>
        </div>

        <div id="s10-q3" class="wh-card" style="left: 96px; top: 512px; width: 848px; height: 420px;">
          <video id="s10-qv3" class="clip wh-vid-fill" src="assets/slides/v_ear_light.mp4" data-start="4.70" data-hf-media-start-basis="local" data-duration="6.63" data-track-index="4" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><span class="wh-badge-num">BƯỚC 03</span><div class="wh-card-h3">RÁY TAI ÊM DỊU</div></div>
        </div>

        <div id="s10-q4" class="wh-card" style="left: 976px; top: 512px; width: 848px; height: 420px;">
          <video id="s10-qv4" class="clip wh-vid-fill" src="assets/slides/v_wash_halo.mp4" data-start="4.70" data-hf-media-start-basis="local" data-duration="6.63" data-track-index="5" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption" style="text-align: right;"><span class="wh-badge-num">BƯỚC 04</span><div class="wh-card-h3">XẢ TÓC THƯ GIÃN</div></div>
        </div>

        <!-- Center Explosive Hero Medallion -->
        <div id="s10-129-card" class="wh-center-badge">
          <div class="wh-kicker" style="font-size: 18px; margin-bottom: 10px;">★ SIÊU COMBO CHUẨN PHONG ĐỘ ★</div>
          <div style="font-family: 'Asap Condensed', sans-serif; font-weight: 900; font-size: 38px; color: #FFFFFF; letter-spacing: 0.06em; margin-bottom: 10px;">
            CẮT · CẠO · RÁY · XẢ
          </div>
          {grad_text("s10-129-num", "CHỈ 129K", "wh-mega-num", "wh-gold-fill")}
          <div style="margin-top: 8px; font-family: 'Montserrat', sans-serif; font-weight: 900; font-size: 24px; color: #FF5C62; letter-spacing: 0.08em;">
            TRỌN GÓI 4 BƯỚC — QUÁ HỜI!
          </div>
        </div>
      </div>

      <!-- ================= BEAT 3 (11.33s - 22.40s): COMBO NGỦ TRƯA 79K ================= -->
      <div id="s10-b3" style="position: absolute; inset: 0; opacity: 0;">
        <div class="wh-header">
          <div class="wh-kicker">★ GIẢI PHÁP NẠP NĂNG LƯỢNG GIỜ NGHỈ TRƯA ★</div>
          {grad_text("s10-b3-ttl", "COMBO NGỦ TRƯA 30 PHÚT · TỈNH TÁO CẢ BUỔI CHIỀU")}
          <div class="wh-flare-bar" data-layout-ignore></div>
        </div>

        <div id="s10-b3-left" class="wh-card" style="left: 108px; top: 206px; width: 790px; height: 684px;">
          <video id="s10-b3-vh" class="clip wh-vid-fill" src="assets/slides/h_lunch_nap.mp4" data-start="11.33" data-hf-media-start-basis="local" data-duration="11.07" data-track-index="6" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">30 PHÚT THƯ THÁI</span>
            <div class="wh-card-h3">CHỢP MẮT ÊM ÁI TRONG PHÒNG MÁT</div>
            <div class="wh-card-p">Chiều quay lại làm việc tỉnh táo sảng khoái ngay</div>
          </div>
        </div>

        <div id="s10-b3-mid" class="wh-card" style="left: 924px; top: 206px; width: 380px; height: 684px;">
          <video id="s10-b3-vv" class="clip wh-vid-fill" src="assets/slides/v_wash_foam.mp4" data-start="11.33" data-hf-media-start-basis="local" data-duration="11.07" data-track-index="7" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">BAO GỒM</span>
            <div class="wh-card-h3">GỘI ĐẦU + MASSAGE MẶT</div>
          </div>
        </div>

        <div id="s10-b3-price" class="wh-card" style="left: 1330px; top: 206px; width: 482px; height: 684px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 28px; background: radial-gradient(circle at 50% 30%, #4E0A10 0%, #160708 100%);">
          <div class="wh-kicker" style="margin-bottom: 14px;">COMBO NGỦ TRƯA</div>
          <div style="font-family: 'Asap Condensed', sans-serif; font-weight: 900; font-size: 36px; color: #FFF2CC;">TRỌN GÓI 30 PHÚT</div>
          <div style="margin: 12px 0;">
            {grad_text("s10-79k", "79K", "wh-mega-num", "wh-gold-fill")}
          </div>
          <div class="wh-flare-bar" style="width: 300px; margin: 12px 0;" data-layout-ignore></div>
          <div style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 21px; color: #FFE38E; line-height: 1.35;">
            GỘI ĐẦU MÁT LẠNH<br/>+ MASSAGE MẶT CHILL
          </div>
        </div>
      </div>

      <!-- ================= BEAT 4 (22.40s - 27.77s): HỆ THỐNG 2 CƠ SỞ ================= -->
      <div id="s10-b4" style="position: absolute; inset: 0; opacity: 0;">
        <div class="wh-header">
          <div class="wh-kicker">★ HỆ THỐNG WIN HAIR SALON TẠI TP. NHA TRANG ★</div>
          {grad_text("s10-b4-ttl", "2 CƠ SỞ ĐẲNG CẤP SẴN SÀNG PHỤC VỤ ANH EM")}
          <div class="wh-flare-bar" data-layout-ignore></div>
        </div>

        <!-- CS1 Card -->
        <div id="s10-cs1" class="wh-card" style="left: 112px; top: 206px; width: 824px; height: 684px;">
          <video id="s10-cs1-v" class="clip wh-vid-fill" src="assets/slides/v_cs1_front.mp4" data-start="22.40" data-hf-media-start-basis="local" data-duration="5.37" data-track-index="8" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">📍 CƠ SỞ 01</span>
            <div class="wh-card-h3" style="font-size: 40px;">41 LÝ TỰ TRỌNG — NHA TRANG</div>
            <div class="wh-card-p" style="font-size: 19px;">Trung tâm thành phố · Thuận tiện di chuyển</div>
          </div>
        </div>

        <!-- CS2 Card (Vertical + Flycam swap) -->
        <div id="s10-cs2" class="wh-card" style="left: 984px; top: 206px; width: 824px; height: 684px;">
          <video id="s10-cs2-v1" class="clip wh-vid-fill" src="assets/slides/v_cs2_front.mp4" data-start="22.40" data-hf-media-start-basis="local" data-duration="2.60" data-track-index="9" muted playsinline></video>
          <video id="s10-cs2-v2" class="clip wh-vid-fill" src="assets/slides/h_cs2_flycam.mp4" data-start="25.00" data-hf-media-start-basis="local" data-duration="2.77" data-track-index="10" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <span class="wh-badge-num">📍 CƠ SỞ 02</span>
            <div class="wh-card-h3" style="font-size: 40px;">59 THÍCH QUẢNG ĐỨC — NHA TRANG</div>
            <div class="wh-card-p" style="font-size: 19px;">Không gian lớn 2 tầng VIP · Đón tiếp chu đáo</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set(["#s10-b2", "#s10-b3", "#s10-b4"], {{ opacity: 0 }});

    // Beat 1: 0.00 - 4.70s (279.80 - 284.50s)
    tl.fromTo("#s10-b1-vidwrap", {{ opacity: 0, x: -70, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.42, ease: "power3.out" }}, 0.08);
    tl.fromTo("#s10-b1-offer", {{ opacity: 0, x: 70, scale: 0.90 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.25)" }}, 0.25);
    tl.fromTo("#s10-20pct-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 2.15);
    tl.fromTo("#s10-b1", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.20 }}, 4.50);

    // Beat 2: 4.70 - 11.33s (284.50 - 291.13s)
    // VO hits: Cắt 285.33 (rel 5.53) | Cạo 285.67 (rel 5.87) | Ráy 286.20 (rel 6.40) | Xả 286.53 (rel 6.73) | Chuẩn phong độ 287.10 (rel 7.30) | 129K 288.70 (rel 8.90)
    tl.fromTo("#s10-b2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, 4.70);
    tl.fromTo("#s10-q1", {{ opacity: 0, scale: 0.85, x: -50 }}, {{ opacity: 1, scale: 1, x: 0, duration: 0.30, ease: "back.out(1.3)" }}, 5.45);
    tl.fromTo("#s10-q2", {{ opacity: 0, scale: 0.85, x: 50 }}, {{ opacity: 1, scale: 1, x: 0, duration: 0.30, ease: "back.out(1.3)" }}, 5.82);
    tl.fromTo("#s10-q3", {{ opacity: 0, scale: 0.85, x: -50 }}, {{ opacity: 1, scale: 1, x: 0, duration: 0.30, ease: "back.out(1.3)" }}, 6.35);
    tl.fromTo("#s10-q4", {{ opacity: 0, scale: 0.85, x: 50 }}, {{ opacity: 1, scale: 1, x: 0, duration: 0.30, ease: "back.out(1.3)" }}, 6.68);

    tl.fromTo("#s10-129-card", {{ opacity: 0, scale: 0.65, y: 30 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.45, ease: "back.out(1.45)" }}, 7.25);
    tl.fromTo("#s10-129-num-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.90, ease: "power2.inOut" }}, 8.85);
    tl.fromTo("#s10-b2", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, immediateRender: false }}, 11.11);

    // Beat 3: 11.33 - 22.40s (291.13 - 302.20s)
    tl.fromTo("#s10-b3", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.20 }}, 11.33);
    tl.fromTo("#s10-b3-left", {{ opacity: 0, x: -65, scale: 0.94 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, 11.42);
    tl.fromTo("#s10-b3-mid", {{ opacity: 0, y: 65, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 12.60);
    tl.fromTo("#s10-b3-price", {{ opacity: 0, scale: 0.84, x: 60 }}, {{ opacity: 1, scale: 1, x: 0, duration: 0.48, ease: "back.out(1.3)" }}, 15.80);
    tl.fromTo("#s10-79k-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 17.40);
    tl.fromTo("#s10-b3", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, immediateRender: false }}, 22.18);

    // Beat 4: 22.40 - 27.77s (302.20 - 307.57s)
    tl.fromTo("#s10-b4", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.20 }}, 22.40);
    tl.fromTo("#s10-cs1", {{ opacity: 0, x: -80, scale: 0.92 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 22.48);
    tl.fromTo("#s10-cs2", {{ opacity: 0, x: 80, scale: 0.92 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.2)" }}, 24.95);
    tl.fromTo("#s10-b4-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 23.00);
    tl.fromTo("#s10-stage", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, 27.53);

    window.__timelines["slide-10"] = tl;
  </script>
</template>
""")

# =========================================================================
# OVERLAYS & HUD COMPOSITION (0.00s - 316.40s):
#   - Grand Intro Hero Title (0.10s - 4.95s)
#   - Persistent Corner Brand Emblem (5.00s - 307.40s)
#   - FCP Section Lower-Thirds, VIP Callouts & 4 Customer 10/10 Badges
#   - Grand End-Card Footer Lockup (307.80s - 316.40s)
# =========================================================================
HUD_CARDS = [
    # (id, start, dur, kicker, title, subtitle)
    ("hud-koc", 12.57, 3.18, "★ UY TÍN THƯƠNG HIỆU", "ĐÔNG ĐẢO KOC · KOL TIN CHỌN", "Hài lòng khách địa phương lẫn du khách quốc tế"),
    ("hud-f1", 15.88, 10.65, "📍 KHÔNG GIAN TẦNG 01", "SẢNH ĐÓN TIẾP SANG TRỌNG", "Nhân viên chào đón niềm nở · Ghế chờ gỗ êm ái"),
    ("hud-menu", 26.75, 8.45, "✦ DỊCH VỤ MINH BẠCH", "BẢNG GIÁ RÕ RÀNG · TƯ VẤN TẬN TÂM", "Đa dạng gói Combo dễ dàng lựa chọn theo nhu cầu"),
    ("hud-cutzone", 42.75, 10.20, "✂ KHU VỰC TẠO KIỂU", "KHU CẮT TÓC CHUẨN PHONG ĐỘ", "Gương sáng · Ghế xịn · Ngồi vào yên tâm, đứng dậy là bảnh!"),
    ("hud-king", 59.75, 10.20, "★ TIỆN ÍCH VIP MIỄN PHÍ", "GHẾ MASSAGE KINGSPORT & ĐỒ UỐNG", "Mời miễn phí Nước Cam · Trà Chanh · Cà Phê như đi nghỉ dưỡng"),
    ("hud-priv", 70.35, 9.75, "🔒 KHÔNG GIAN RIÊNG TƯ", "HỆ THỐNG PHÒNG RIÊNG PHỤC VỤ 1 : 1", "Kéo rèm riêng biệt · Không ồn · Không phiền · Chỉ có thư giãn"),
    ("hud-staff", 136.85, 15.55, "★ ĐỘI NGŨ KỸ THUẬT VIÊN", "TAY NGHỀ CHUẨN · TÁC PHONG CHỈNH TỀ", "Không cắt cho nhanh mà cắt cho chuẩn · Tận tâm từ lúc vào đến lúc về"),
    ("hud-rev1", 152.80, 18.90, "★★★★★ ĐÁNH GIÁ 10 / 10", "KHÁCH HÀNG TRẢI NGHIỆM THỰC TẾ", "“Không gian sang trọng sạch sẽ · Cả gia đình đều mê!”"),
    ("hud-rev2", 172.10, 16.45, "★★★★★ ĐÁNH GIÁ 10 / 10", "KHÁCH HÀNG TRẢI NGHIỆM DỊCH VỤ", "“Được chăm sóc tận tình chuẩn Thượng Đế!”"),
    ("hud-rev3", 188.90, 22.85, "★★★★★ ANH NAM CHẤM 10 / 10", "KHÁCH HÀNG NAM THÂN THIẾT", "“Reset lại bản thân · Tút lại vẻ đẹp trai & phong độ!”"),
    ("hud-rev4", 212.15, 43.35, "★★★★★ ANH HƯNG & ANH HUY", "TRẢI NGHIỆM COMBO VIP GỘI · RÁY TAI · MASSAGE", "“Ráy tai nhẹ quá ngủ thiếp đi luôn · Làm xong người nhẹ hẳn!”"),
]

hud_html_parts = []
hud_js_parts = []
for hid, hst, hdur, hkicker, htitle, hsub in HUD_CARDS:
    hud_html_parts.append(f"""
    <div id="{hid}" class="clip wh-fcp-host" data-start="{hst:.2f}" data-duration="{hdur:.2f}" data-track-index="2">
      <div id="{hid}-box" class="wh-fcp-card">
        <div id="{hid}-bar" class="wh-fcp-bar" data-layout-ignore></div>
        <div class="wh-fcp-body">
          <div class="wh-fcp-kicker">{html.escape(hkicker)}</div>
          <div class="wh-fcp-title">{html.escape(htitle)}</div>
          <div class="wh-fcp-sub">{html.escape(hsub)}</div>
        </div>
      </div>
    </div>""")
    hud_js_parts.append(f"""
    tl.fromTo("#{hid}-box", {{ opacity: 0, x: -55, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.34, ease: "power3.out" }}, {hst:.2f});
    tl.fromTo("#{hid}-bar", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.36, ease: "expo.out" }}, {hst + 0.08:.2f});
    tl.fromTo("#{hid}-box", {{ opacity: 1, x: 0, filter: "blur(0px)" }}, {{ opacity: 0, x: -35, filter: "blur(8px)", duration: 0.24, ease: "power2.in", immediateRender: false }}, {hst + hdur - 0.26:.2f});""")

write_comp("overlays-hud.html", f"""<template>
  <style>{SHARED_SLIDE_CSS}
    /* Corner Brand Watermark */
    .wh-corner-host {{
      position: absolute;
      right: 58px;
      top: 42px;
      z-index: 22;
    }}
    .wh-corner-pill {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 18px;
      border-radius: 999px;
      background: rgba(12, 8, 7, 0.72);
      border: 1.5px solid rgba(248, 206, 102, 0.62);
      box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    }}
    .wh-monogram {{
      width: 28px;
      height: 28px;
      border-radius: 6px;
      background: linear-gradient(135deg, #FFE484, #B87914);
      color: #160A04;
      font-family: "Montserrat", sans-serif;
      font-weight: 900;
      font-size: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .wh-corner-txt {{
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      font-size: 15px;
      letter-spacing: 0.08em;
      color: #FFE799;
    }}

    /* Grand Intro Hero Lockup (0.00 - 4.95s) */
    .wh-intro-host {{
      position: absolute;
      inset: 0;
      z-index: 25;
      pointer-events: none;
    }}
    .wh-intro- vignette {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.10) 0%, rgba(0,0,0,0.15) 52%, rgba(8,4,4,0.88) 100%);
    }}
    .wh-intro-stack {{
      position: absolute;
      left: 120px;
      right: 120px;
      bottom: 64px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }}
    .wh-intro-main {{
      font-family: "Anton", sans-serif;
      font-size: 112px;
      line-height: 1.02;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .wh-intro-sub {{
      margin-top: 10px;
      padding: 10px 34px;
      border-radius: 14px;
      background: linear-gradient(90deg, rgba(16, 10, 8, 0.92), rgba(48, 12, 12, 0.92), rgba(16, 10, 8, 0.92));
      border: 2px solid rgba(252, 212, 108, 0.85);
      box-shadow: 0 14px 36px rgba(0,0,0,0.8);
      font-family: "Asap Condensed", sans-serif;
      font-weight: 900;
      font-size: 40px;
      letter-spacing: 0.06em;
      color: #FFF4CC;
      text-transform: uppercase;
    }}

    /* FCP Architectural Lower-Third / Upper-Left HUD Card */
    .wh-fcp-host {{
      position: absolute;
      left: 64px;
      top: 46px;
      z-index: 24;
      pointer-events: none;
    }}
    .wh-fcp-card {{
      display: flex;
      align-items: stretch;
      background: linear-gradient(135deg, rgba(14, 10, 9, 0.90), rgba(32, 12, 12, 0.86));
      border: 1.5px solid rgba(248, 205, 98, 0.65);
      border-radius: 16px;
      box-shadow: 0 16px 38px rgba(0, 0, 0, 0.68);
      overflow: hidden;
      max-width: 720px;
    }}
    .wh-fcp-bar {{
      width: 7px;
      background: linear-gradient(180deg, #FFE896, #D91822);
      transform-origin: 50% 0%;
    }}
    .wh-fcp-body {{
      padding: 14px 24px;
    }}
    .wh-fcp-kicker {{
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      font-size: 14px;
      letter-spacing: 0.10em;
      color: #FFD966;
      text-transform: uppercase;
    }}
    .wh-fcp-title {{
      margin-top: 3px;
      font-family: "Asap Condensed", sans-serif;
      font-weight: 900;
      font-size: 31px;
      line-height: 1.1;
      color: #FFFFFF;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    .wh-fcp-sub {{
      margin-top: 4px;
      font-family: "Be Vietnam Pro", sans-serif;
      font-weight: 600;
      font-size: 16px;
      color: #E8DDD2;
    }}

    /* End-Card Lockup (307.80 - 316.40s) */
    .wh-end-host {{
      position: absolute;
      inset: 0;
      z-index: 26;
      pointer-events: none;
    }}
    .wh-end-top {{
      position: absolute;
      left: 120px;
      right: 120px;
      top: 56px;
      text-align: center;
    }}
    .wh-end-bot {{
      position: absolute;
      left: 96px;
      right: 96px;
      bottom: 54px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 20px;
    }}
    .wh-end-pill {{
      padding: 14px 26px;
      border-radius: 14px;
      background: rgba(14, 10, 8, 0.90);
      border: 1.8px solid rgba(250, 208, 102, 0.80);
      box-shadow: 0 14px 34px rgba(0,0,0,0.8);
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      font-size: 20px;
      color: #FFF3CC;
    }}
    .wh-end-hotline {{
      padding: 15px 32px;
      border-radius: 14px;
      background: linear-gradient(135deg, #D91822, #85080F);
      border: 2px solid #FFE484;
      box-shadow: 0 14px 36px rgba(217, 24, 34, 0.55);
      font-family: "Montserrat", sans-serif;
      font-weight: 900;
      font-size: 22px;
      color: #FFFFFF;
      letter-spacing: 0.04em;
    }}
  </style>

  <div id="root" data-composition-id="overlays-hud" data-width="1920" data-height="1080">
    <!-- 1. GRAND INTRO HERO LOCKUP (0.05s - 4.95s) -->
    <div id="intro-hero" class="clip wh-intro-host" data-start="0.05" data-duration="4.90" data-track-index="1" data-layout-allow-caption-zone>
      <div id="intro-stack" class="wh-intro-stack">
        <div id="intro-kicker" class="wh-kicker" style="font-size: 19px; margin-bottom: 10px;">
          ★ THẾ GIỚI TÓC NAM & RELAX 5 SAO ★
        </div>
        <div id="intro-wordmark">
          {grad_text("intro-wm", "WIN HAIR SALON", "wh-intro-main", "wh-gold-fill")}
        </div>
        <div id="intro-flare" class="wh-flare-bar" style="width: 720px; margin-top: 6px;" data-layout-ignore></div>
        <div id="intro-tagline" class="wh-intro-sub" data-var-text="brand_tagline">
          ĐẲNG CẤP TÓC NAM SỐ 1 NHA TRANG
        </div>
      </div>
    </div>

    <!-- 2. PERSISTENT CORNER BRAND WATERMARK (5.00s - 307.40s) -->
    <div id="corner-bug" class="clip wh-corner-host" data-start="5.00" data-duration="302.40" data-track-index="0">
      <div id="corner-pill" class="wh-corner-pill">
        <div class="wh-monogram">WH</div>
        <div class="wh-corner-txt" data-var-text="brand_name">WIN HAIR SALON</div>
      </div>
    </div>

    <!-- 3. FCP SECTION & TESTIMONIAL LOWER-THIRDS -->
    {"".join(hud_html_parts)}

    <!-- 4. GRAND END-CARD LOCKUP OVER GOLD LOGO REVEAL (307.80s - 316.40s) -->
    <div id="end-lockup" class="clip wh-end-host" data-start="307.80" data-duration="8.60" data-track-index="3" data-layout-allow-caption-zone>
      <div id="end-top" class="wh-end-top">
        <div class="wh-kicker" style="font-size: 18px;">★ HỆ THỐNG SALON TÓC NAM HÀNG ĐẦU KHÁNH HÒA ★</div>
        <div style="margin-top: 6px;">
          {grad_text("end-ttl", "ĐẲNG CẤP TÓC NAM SỐ 1 NHA TRANG", "wh-title-lg", "wh-gold-fill")}
        </div>
      </div>

      <div id="end-bot" class="wh-end-bot">
        <div class="wh-end-pill" data-var-text="branch_1">📍 CS1: 41 LÝ TỰ TRỌNG</div>
        <div class="wh-end-hotline" data-var-text="hotline">☎ HOTLINE: 0352 956 779</div>
        <div class="wh-end-pill" data-var-text="branch_2">📍 CS2: 59 THÍCH QUẢNG ĐỨC</div>
      </div>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});

    // Intro Hero Animation
    tl.fromTo("#intro-kicker", {{ opacity: 0, y: -20, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out" }}, 0.08);
    tl.fromTo("#intro-wordmark", {{ opacity: 0, scale: 1.24, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.38, ease: "back.out(1.35)" }}, 0.14);
    tl.fromTo("#intro-flare", {{ scaleX: 0, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: 0.50, ease: "expo.out" }}, 0.28);
    tl.fromTo("#intro-wm-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.15, ease: "power2.inOut" }}, 0.45);
    tl.fromTo("#intro-tagline", {{ opacity: 0, y: 28, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1.0, duration: 0.38, ease: "back.out(1.25)" }}, 1.48);
    tl.fromTo("#intro-stack", {{ opacity: 1, y: 0 }}, {{ opacity: 0, y: 24, duration: 0.24, ease: "power2.in" }}, 4.68);

    // Corner Bug
    tl.fromTo("#corner-pill", {{ opacity: 0, y: -16 }}, {{ opacity: 1, y: 0, duration: 0.40, ease: "power2.out" }}, 5.05);

    // Section & Review HUDs
    {"".join(hud_js_parts)}

    // End-Card Lockup
    tl.fromTo("#end-top", {{ opacity: 0, y: -28, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.48, ease: "power3.out" }}, 308.10);
    tl.fromTo("#end-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.25, ease: "power2.inOut" }}, 309.00);
    tl.fromTo("#end-bot", {{ opacity: 0, y: 36, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.52, ease: "back.out(1.2)" }}, 308.65);

    window.__timelines["overlays-hud"] = tl;
  </script>
</template>
""")

# =========================================================================
# BROADCAST TV SUBTITLES COMPOSITION (captions-tv.html)
# Large, bold, high-contrast TV commercial subtitles with Gold Highlights!
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
}

GOLD_KEYWORDS = [
    "WINHAIR SALON", "WIN HAIR", "WINHAIR", "SỐ 1 NHA TRANG", "SỐ MỘT NHA TRANG",
    "DỊCH VỤ ĐA DẠNG", "KHÔNG GIAN ĐẲNG CẤP", "CHUYÊN NGHIỆP", "KOC", "KOL",
    "TẦNG 2 KHU VIP", "KHU VIP", "KINGSPORT", "MIỄN PHÍ", "1 : 1",
    "GỘI ĐẦU", "MASSAGE CỔ VAI GÁY", "MASSAGE MẶT", "MASSAGE TAY", "MASSAGE CHÂN", "MASSAGE BODY", "MASSAGE",
    "RÁY TAI", "ĐẮP MẶT", "LỘT MỤN", "FADE", "CẠO MẶT", "XÔNG HƠI",
    "BẤM MÓNG TAY", "CẮT MÓNG CHÂN", "10 ĐIỂM", "10 / 10", "CHÍN ĐIỂM", "THƯỢNG ĐẾ",
    "GIẢM NGAY 20%", "COMBO NGỦ TRƯA", "79.000", "41 LÝ TỰ TRỌNG", "59 THÍCH QUẢNG ĐỨC",
]

def highlight_caption(txt):
    s = html.escape(txt.strip())
    for kw in GOLD_KEYWORDS:
        ekw = html.escape(kw)
        if ekw in s:
            s = s.replace(ekw, f'<span class="tv-kw">{ekw}</span>')
    return s

cap_divs = []
cap_tweens = []
cap_idx = 0
for seg in dc["tracks"][11]["segments"]:
    st = seg["target_timerange"]["start"] / 1e6
    dur = seg["target_timerange"]["duration"] / 1e6
    en = st + dur
    # Skip tiny slivers (<0.15s), Intro Hero (0..5.0s), and 129K Center Slam (285.2..291.1s)
    if dur < 0.15 or en <= 5.01 or (285.20 <= st <= 291.10):
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
    styled_html = highlight_caption(txt)
    cid = f"cap-{cap_idx:03d}"
    cap_divs.append(
        f'    <div id="{cid}" class="clip tv-cap-host" data-start="{st:.2f}" data-duration="{dur:.2f}" data-track-index="0">'
        f'<div id="{cid}-in" class="tv-cap-pill">{styled_html}</div></div>'
    )
    # Crisp subtle pop on key emphasis lines, calm instant legibility on continuous dialogue
    in_dur = min(0.14, dur * 0.25)
    cap_tweens.append(
        f'    tl.fromTo("#{cid}-in", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: {in_dur:.2f}, ease: "power2.out" }}, {st:.2f});'
    )
    cap_idx += 1

write_comp("captions-tv.html", f"""<template>
  <style>{FONT_FACES_CSS}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    #root {{
      position: absolute;
      inset: 0;
      overflow: hidden;
      pointer-events: none;
    }}
    .tv-cap-host {{
      position: absolute;
      left: 130px;
      right: 130px;
      bottom: 42px;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 30;
    }}
    .tv-cap-pill {{
      display: inline-block;
      max-width: 1620px;
      padding: 13px 34px;
      border-radius: 16px;
      background: linear-gradient(180deg, rgba(14, 10, 9, 0.92) 0%, rgba(8, 5, 5, 0.95) 100%);
      border: 2px solid rgba(250, 208, 102, 0.78);
      box-shadow: 0 14px 36px rgba(0, 0, 0, 0.88), 0 0 20px rgba(248, 204, 96, 0.20);
      font-family: "Montserrat", sans-serif;
      font-weight: 900;
      font-size: 38px;
      line-height: 1.25;
      letter-spacing: 0.02em;
      color: #FFFFFF;
      text-align: center;
      text-transform: uppercase;
      text-shadow: 0 3px 10px rgba(0, 0, 0, 0.98);
    }}
    .tv-kw {{
      color: #FFE066;
      font-weight: 900;
      text-shadow: 0 3px 12px rgba(245, 180, 30, 0.45), 0 2px 6px rgba(0, 0, 0, 0.95);
    }}
  </style>
  <div id="root" data-composition-id="captions-tv" data-width="1920" data-height="1080">
{chr(10).join(cap_divs)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(cap_tweens)}
    window.__timelines["captions-tv"] = tl;
  </script>
</template>
""")
print(f"Built captions-tv.html with {cap_idx} TV commercial subtitle segments!")

# =========================================================================
# ROOT COMPOSITION: index.html (1920x1080, 316.40s) + EPIC SFX SCORE
# =========================================================================
SFX_EVENTS = [
    # (id, file, start, dur, vol)
    # Act 1: Grand Intro & 3 Pillars
    ("sfx-01", "epic_hit_low.mp3", 0.05, 4.80, 0.46),
    ("sfx-02", "blade_shine.mp3", 0.45, 1.00, 0.30),
    ("sfx-03", "title_swoosh.mp3", 1.45, 0.90, 0.32),
    ("sfx-04", "metallic_riser.mp3", 3.90, 1.20, 0.28),
    ("sfx-05", "cinematic_whoosh.mp3", 4.95, 1.30, 0.42),
    ("sfx-06", "fast_swoosh.mp3", 6.45, 0.90, 0.28),
    ("sfx-07", "fast_swoosh.mp3", 7.38, 0.90, 0.28),
    ("sfx-08", "luxury_bell.mp3", 12.55, 1.80, 0.24),

    # Act 2: Floor 1 & Shampoo Slide
    ("sfx-09", "title_swoosh.mp3", 15.82, 0.90, 0.26),
    ("sfx-10", "cinematic_whoosh.mp3", 35.30, 1.30, 0.38),
    ("sfx-11", "fast_swoosh.mp3", 35.80, 0.90, 0.24),
    ("sfx-12", "title_swoosh.mp3", 42.70, 0.90, 0.26),

    # Act 3: Floor 2 VIP Slide 02B & 5-Panel Accordion
    ("sfx-13", "metallic_riser.mp3", 52.10, 1.20, 0.26),
    ("sfx-14", "cinematic_whoosh.mp3", 53.10, 1.30, 0.40),
    ("sfx-14a", "card_snap.mp3", 55.88, 0.65, 0.24),
    ("sfx-14b", "card_snap.mp3", 56.55, 0.65, 0.25),
    ("sfx-14c", "card_snap.mp3", 57.38, 0.65, 0.26),
    ("sfx-15", "golden_chimes.mp3", 59.70, 3.50, 0.22),
    ("sfx-16", "title_swoosh.mp3", 70.30, 0.90, 0.25),
    ("sfx-17", "cinematic_whoosh.mp3", 80.18, 1.30, 0.40),
    ("sfx-18", "card_snap.mp3", 80.88, 0.65, 0.24),
    ("sfx-19", "card_snap.mp3", 81.48, 0.65, 0.25),
    ("sfx-20", "card_snap.mp3", 82.33, 0.65, 0.26),
    ("sfx-21", "card_snap.mp3", 83.13, 0.65, 0.26),

    # Act 4: Core Services Showcase (88.70s - 136.70s)
    ("sfx-22", "metallic_riser.mp3", 87.60, 1.20, 0.28),
    ("sfx-23", "epic_hit_low.mp3", 88.68, 4.80, 0.42),
    ("sfx-24", "blade_shine.mp3", 89.05, 1.00, 0.28),
    ("sfx-25", "cinematic_whoosh.mp3", 99.95, 1.30, 0.40),
    ("sfx-26", "blade_shine.mp3", 100.32, 1.00, 0.32),
    ("sfx-27", "cinematic_whoosh.mp3", 104.92, 1.30, 0.38),
    ("sfx-28", "luxury_bell.mp3", 105.30, 1.80, 0.22),
    ("sfx-29", "cinematic_whoosh.mp3", 114.02, 1.30, 0.40),
    ("sfx-30", "cinematic_whoosh.mp3", 117.85, 1.30, 0.40),
    ("sfx-31", "fast_swoosh.mp3", 119.58, 0.90, 0.26),
    ("sfx-32", "fast_swoosh.mp3", 120.95, 0.90, 0.28),
    ("sfx-33", "cinematic_whoosh.mp3", 126.95, 1.30, 0.36),
    ("sfx-34", "title_swoosh.mp3", 136.80, 0.90, 0.26),

    # Act 5: Customer Testimonials & 6-Step Combo Cascade
    ("sfx-35", "luxury_bell.mp3", 152.75, 1.80, 0.22),
    ("sfx-36", "luxury_bell.mp3", 172.05, 1.80, 0.22),
    ("sfx-37", "luxury_bell.mp3", 188.85, 1.80, 0.22),
    ("sfx-38", "luxury_bell.mp3", 212.10, 1.80, 0.22),
    ("sfx-39", "card_snap.mp3", 256.72, 0.65, 0.24),
    ("sfx-40", "card_snap.mp3", 258.89, 0.65, 0.24),
    ("sfx-41", "card_snap.mp3", 260.07, 0.65, 0.25),
    ("sfx-42", "card_snap.mp3", 261.05, 0.65, 0.25),
    ("sfx-43", "card_snap.mp3", 262.77, 0.65, 0.26),
    ("sfx-44", "card_snap.mp3", 264.12, 0.65, 0.26),

    # Act 6: Mega Promos (-20%, Combo 129K, Nap 79K, 2 Branches & Grand Outro)
    ("sfx-45", "metallic_riser.mp3", 278.70, 1.20, 0.30),
    ("sfx-46", "epic_hit_low.mp3", 279.78, 4.60, 0.44),
    ("sfx-47", "blade_shine.mp3", 281.95, 1.00, 0.30),
    ("sfx-48", "cinematic_whoosh.mp3", 284.48, 1.30, 0.42),
    ("sfx-49", "fast_swoosh.mp3", 285.25, 0.80, 0.28),
    ("sfx-50", "fast_swoosh.mp3", 285.62, 0.80, 0.28),
    ("sfx-51", "fast_swoosh.mp3", 286.15, 0.80, 0.30),
    ("sfx-52", "fast_swoosh.mp3", 286.48, 0.80, 0.30),
    ("sfx-53", "epic_hit_low.mp3", 287.05, 4.20, 0.48),
    ("sfx-54", "luxury_bell.mp3", 288.65, 2.00, 0.36),
    ("sfx-55", "blade_shine.mp3", 288.75, 1.00, 0.34),
    ("sfx-56", "cinematic_whoosh.mp3", 291.10, 1.30, 0.40),
    ("sfx-57", "luxury_bell.mp3", 295.60, 2.00, 0.30),
    ("sfx-58", "cinematic_whoosh.mp3", 302.18, 1.30, 0.40),
    ("sfx-59", "fast_swoosh.mp3", 304.75, 0.90, 0.30),
    ("sfx-60", "metallic_riser.mp3", 306.50, 1.20, 0.32),
    ("sfx-61", "epic_hit_low.mp3", 307.58, 6.50, 0.50),
    ("sfx-62", "golden_chimes.mp3", 308.20, 5.50, 0.32),
]

# Assign non-overlapping Studio lanes (5, 6, 7, 8...) for SFX so Studio timeline is 100% clean
lane_ends = []
sfx_tag_list = []
for sid, sfile, sst, sdur, svol in sorted(SFX_EVENTS, key=lambda x: x[2]):
    assigned_lane = None
    for li, lend in enumerate(lane_ends):
        if sst >= lend + 0.02:
            assigned_lane = 5 + li
            lane_ends[li] = sst + sdur
            break
    if assigned_lane is None:
        assigned_lane = 5 + len(lane_ends)
        lane_ends.append(sst + sdur)
    sfx_tag_list.append(
        f'      <audio id="{sid}" class="clip" src="assets/sfx/{sfile}" data-start="{sst:.2f}" data-duration="{sdur:.2f}" data-volume="{svol:.2f}" data-fade-in="0.02" data-fade-out="0.08" data-track-index="{assigned_lane}"></audio>'
    )
sfx_tags = "\n".join(sfx_tag_list)

SLIDE_MOUNTS = [
    ("slide-01", "compositions/slide-01.html", 5.00, 4.33),
    ("slide-02", "compositions/slide-02.html", 35.37, 7.23),
    ("slide-02b", "compositions/slide-02b.html", 53.13, 6.54),
    ("slide-03", "compositions/slide-03.html", 80.23, 7.24),
    ("slide-04", "compositions/slide-04.html", 88.70, 11.30),
    ("slide-05", "compositions/slide-05.html", 100.00, 4.97),
    ("slide-06", "compositions/slide-06.html", 104.97, 9.10),
    ("slide-07", "compositions/slide-07.html", 114.07, 12.93),
    ("slide-08", "compositions/slide-08.html", 127.00, 9.70),
    ("slide-09", "compositions/slide-09.html", 255.77, 10.73),
    ("slide-10", "compositions/slide-10.html", 279.80, 27.77),
]

slide_mount_tags = "\n".join([
    f'      <div id="{mid}" class="clip" data-composition-id="{mid}" data-composition-src="{msrc}" data-start="{mst:.2f}" data-duration="{mdur:.2f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080" style="position: absolute; inset: 0; z-index: 10;"></div>'
    for mid, msrc, mst, mdur in SLIDE_MOUNTS
])

VARIABLES_JSON = json.dumps([
    {"id": "brand_name", "type": "string", "label": "Tên Thương Hiệu", "default": "WIN HAIR SALON"},
    {"id": "brand_tagline", "type": "string", "label": "Slogan Thương Hiệu", "default": "ĐẲNG CẤP TÓC NAM SỐ 1 NHA TRANG"},
    {"id": "branch_1", "type": "string", "label": "Địa Chỉ Cơ Sở 1", "default": "📍 CS1: 41 LÝ TỰ TRỌNG"},
    {"id": "branch_2", "type": "string", "label": "Địa Chỉ Cơ Sở 2", "default": "📍 CS2: 59 THÍCH QUẢNG ĐỨC"},
    {"id": "hotline", "type": "string", "label": "Số Điện Thoại Hotline", "default": "☎ HOTLINE: 0352 956 779"},
], ensure_ascii=False)

index_html = f"""<!doctype html>
<html lang="vi" data-composition-variables='{VARIABLES_JSON}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>TVC Win Hair Salon CS2 — Luxury Commercial Edition</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      {FONT_FACES_CSS}
      :root {{
        --ground: #080606;
        --brand-gold: #F5C542;
        --brand-crimson: #D91822;
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
        background: #080606;
      }}
      .base-bg {{
        position: absolute;
        inset: 0;
        background: #080606;
        z-index: 0;
      }}
      #base-video {{
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1080px;
        object-fit: contain;
        z-index: 1;
      }}
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="316.40"
      data-fps="30"
      data-width="1920"
      data-height="1080"
    >
      <div class="base-bg" data-layout-ignore></div>

      <!-- Track 0: 100% Clean Textless Master Video -->
      <video
        id="base-video"
        class="clip"
        src="assets/video/clean_base_1080p.mp4"
        data-start="0"
        data-duration="316.40"
        data-track-index="0"
        muted
        playsinline
      ></video>

      <!-- Track 1: 10 After Effects × Final Cut Motion Slides (Horizontal + Vertical Sources) -->
{slide_mount_tags}

      <!-- Track 2: Hero Intro, Persistent Brand Bug, FCP Lower-Thirds & End-Card Lockup -->
      <div
        id="overlays-hud"
        class="clip"
        data-composition-id="overlays-hud"
        data-composition-src="compositions/overlays-hud.html"
        data-start="0"
        data-duration="316.40"
        data-track-index="2"
        data-track-kind="graphics"
        data-width="1920"
        data-height="1080"
        style="position: absolute; inset: 0; z-index: 20;"
      ></div>

      <!-- Track 3: Broadcast TV Bold Subtitles -->
      <div
        id="captions-tv"
        class="clip"
        data-composition-id="captions-tv"
        data-composition-src="compositions/captions-tv.html"
        data-start="0"
        data-duration="316.40"
        data-track-index="3"
        data-track-kind="captions"
        data-width="1920"
        data-height="1080"
        style="position: absolute; inset: 0; z-index: 30;"
      ></div>

      <!-- Track 4: Clean Master Voiceover + Interviews + BGM -->
      <audio
        id="master-vo-bgm"
        class="clip"
        src="assets/audio/clean_vo_bgm.mp3"
        data-start="0"
        data-duration="316.40"
        data-volume="1.06"
        data-fade-in="0.05"
        data-fade-out="0.60"
        data-track-index="4"
      ></audio>

      <!-- Track 5: 62 Synchronized Studio Commercial SFX Cues -->
{sfx_tags}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

with open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("Wrote root index.html! Total SFX cues:", len(SFX_EVENTS))
