from v3_styles_and_helpers import SHARED_LUXURY_CSS, bullion_text, lux_header, write_comp

def build_slides_part1():
    # =========================================================================
    # SLIDE 01 (frames 150..280 | 5.000000s, dur = 4.333333s)
    # =========================================================================
    d1 = "4.333333"
    write_comp("slide-01.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-01" data-width="1920" data-height="1080">
    <div id="s1-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s1-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d1}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s1", "WIN HAIR SALON · NHA TRANG", "BA GIÁ TRỊ · MỘT TRẢI NGHIỆM KHÁC BIỆT", "wh-disp-lg")}

      <div id="s1-c1" class="wh-card" style="left: 112px; top: 202px; width: 528px; height: 676px;">
        <video id="s1-v1" class="clip wh-vid-fill" src="assets/slides/v_cut_salon.mp4" data-start="0" data-duration="{d1}" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s1-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">DỊCH VỤ ĐA DẠNG</div>
          <div class="wh-card-p">Trọn gói chăm sóc &amp; thư giãn trong một điểm đến</div>
        </div>
      </div>

      <div id="s1-c2" class="wh-card" style="left: 696px; top: 190px; width: 528px; height: 688px; border-color: rgba(243, 214, 156, 0.45);">
        <video id="s1-v2" class="clip wh-vid-fill" src="assets/slides/v_vip_cs1_bed.mp4" data-start="0" data-duration="{d1}" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s1-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">KHÔNG GIAN ĐẲNG CẤP</div>
          <div class="wh-card-p">Quy mô 2 tầng sang trọng · Riêng tư và êm ái</div>
        </div>
      </div>

      <div id="s1-c3" class="wh-card" style="left: 1280px; top: 202px; width: 528px; height: 676px;">
        <video id="s1-v3" class="clip wh-vid-fill" src="assets/slides/v_cut_cs2_c9498.mp4" data-start="0" data-duration="{d1}" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s1-sh3" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">CHUYÊN MÔN TẬN TÂM</div>
          <div class="wh-card-p">Tay nghề chuẩn mực · Chăm chút từng chi tiết</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s1-hdr", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s1-flare", {{ scaleX: 0, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: 0.48, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s1-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.18);

    tl.fromTo("#s1-c1", {{ opacity: 0, y: -110 }}, {{ opacity: 1, y: 0, duration: 0.46, ease: "power3.out" }}, 0.04);
    tl.fromTo("#s1-sh1", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 0.22);

    tl.fromTo("#s1-c2", {{ opacity: 0, y: 115 }}, {{ opacity: 1, y: 0, duration: 0.48, ease: "power3.out" }}, 1.44);
    tl.fromTo("#s1-sh2", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 1.64);

    tl.fromTo("#s1-c3", {{ opacity: 0, y: -110 }}, {{ opacity: 1, y: 0, duration: 0.48, ease: "power3.out" }}, 2.38);
    tl.fromTo("#s1-sh3", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 2.58);

    tl.to("#s1-v1", {{ scale: 1.05, duration: 4.25, ease: "none" }}, 0.04);
    tl.to("#s1-v2", {{ scale: 1.05, duration: 2.85, ease: "none" }}, 1.44);
    tl.to("#s1-v3", {{ scale: 1.05, duration: 1.90, ease: "none" }}, 2.38);

    window.__timelines["slide-01"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 02 (frames 1061..1175 | 35.366667s, dur = 3.800000s — synced to User's CapCut edit!)
    # =========================================================================
    d2 = "3.800000"
    write_comp("slide-02.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-02" data-width="1920" data-height="1080">
    <div id="s2-stage" class="wh-stage">
      <div class="wh-bg-walnut"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s2-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d2}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s2", "KHÔNG GIAN TẦNG 01", "KHU GỘI ĐẦU RỘNG THOÁNG · THƯ GIÃN TRỌN VẸN", "wh-disp-lg")}

      <div id="s2-main" class="wh-card" style="left: 104px; top: 202px; width: 924px; height: 572px;">
        <video id="s2-vh1" class="clip wh-vid-fill" src="assets/slides/h_shampoo_real1.mp4" data-start="0" data-duration="{d2}" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">TÁCH BIỆT ỒN ÀO · ĐÓN TIẾP TỨC THÌ</div>
          <div class="wh-card-p">Hệ thống giường gội bố trí khoa học · Đông khách vẫn thoải mái</div>
        </div>
      </div>

      <div id="s2-vc1" class="wh-card" style="left: 1056px; top: 202px; width: 366px; height: 572px;">
        <video id="s2-vv1a" class="clip wh-vid-fill" src="assets/slides/v_wash_halo_long.mp4" data-start="0" data-duration="{d2}" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">VÒI NƯỚC ẤM</div>
          <div class="wh-card-p">Dưỡng sinh tuần hoàn êm ái</div>
        </div>
      </div>

      <div id="s2-vc2" class="wh-card" style="left: 1450px; top: 202px; width: 366px; height: 572px;">
        <video id="s2-vv2a" class="clip wh-vid-fill" src="assets/slides/v_wash_foam.mp4" data-start="0" data-duration="{d2}" data-track-index="5" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2-sh3" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">CHĂM SÓC SÂU</div>
          <div class="wh-card-p">Thả lỏng nhẹ nhàng sảng khoái</div>
        </div>
      </div>

      <div class="wh-spec-row" style="left: 104px; right: 104px; top: 804px;">
        <div id="s2-p1" class="wh-spec-item">HAI KHU VỰC RIÊNG BIỆT</div>
        <div id="s2-p2" class="wh-spec-item">KHÔNG GIAN RỘNG THOÁNG</div>
        <div id="s2-p3" class="wh-spec-item">PHỤC VỤ TỨC THÌ</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s2-hdr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s2-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.44, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s2-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.18);

    tl.fromTo("#s2-main", {{ opacity: 0, x: -90 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 0.06);
    tl.fromTo("#s2-sh1", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.70, ease: "power2.out" }}, 0.28);
    tl.fromTo("#s2-vc1", {{ opacity: 0, y: -90 }}, {{ opacity: 1, y: 0, duration: 0.48, ease: "power3.out" }}, 0.22);
    tl.fromTo("#s2-vc2", {{ opacity: 0, y: 90 }}, {{ opacity: 1, y: 0, duration: 0.48, ease: "power3.out" }}, 0.36);

    tl.fromTo("#s2-p1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, 0.65);
    tl.fromTo("#s2-p2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, 1.45);
    tl.fromTo("#s2-p3", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, 2.25);

    window.__timelines["slide-02"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 02B (frames 1640..1790 | 54.666667s, dur = 5.000000s — synced to User's CapCut edit!)
    # =========================================================================
    d2b = "5.000000"
    write_comp("slide-02b.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-02b" data-width="1920" data-height="1080">
    <div id="s2b-stage" class="wh-stage">
      <div class="wh-bg-crimson"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s2b-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d2b}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s2b", "KHÔNG GIAN ĐẶC QUYỀN · TẦNG 02", "Không Gian VIP Riêng Tư Chuẩn 5 Sao", "wh-disp-edit")}

      <div id="s2b-hero" class="wh-card" style="left: 104px; top: 202px; width: 956px; height: 572px;">
        <video id="s2b-vh1" class="clip wh-vid-fill" src="assets/slides/h_cs2_vip_52.mp4" data-start="0" data-duration="2.633333" data-track-index="1" muted playsinline></video>
        <video id="s2b-vh2" class="clip wh-vid-fill" src="assets/slides/h_cs2_vip_43.mp4" data-start="2.633333" data-hf-media-start-basis="local" data-duration="2.366667" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2b-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">DÀNH RIÊNG CHO PHÚT GIÂY TẬN HƯỞNG</div>
          <div class="wh-card-p">Tách biệt hoàn toàn khỏi nhịp phố ồn ào · Thư thái chuẩn nghỉ dưỡng</div>
        </div>
      </div>

      <div id="s2b-c2" class="wh-card" style="left: 1088px; top: 202px; width: 350px; height: 572px;">
        <video id="s2b-v2a" class="clip wh-vid-fill" src="assets/slides/v_cs2_vip_c9679.mp4" data-start="0" data-duration="2.633333" data-track-index="3" muted playsinline></video>
        <video id="s2b-v2b" class="clip wh-vid-fill" src="assets/slides/v_cs2_vip_c9686.mp4" data-start="2.633333" data-hf-media-start-basis="local" data-duration="2.366667" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2b-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">KÍN ĐÁO 1 : 1</div>
          <div class="wh-card-p">Phòng riêng thanh tĩnh</div>
        </div>
      </div>

      <div id="s2b-c3" class="wh-card" style="left: 1466px; top: 202px; width: 350px; height: 572px;">
        <video id="s2b-v3a" class="clip wh-vid-fill" src="assets/slides/v_cs2_vip_c9680.mp4" data-start="0" data-duration="2.633333" data-track-index="5" muted playsinline></video>
        <video id="s2b-v3b" class="clip wh-vid-fill" src="assets/slides/h_cs2_vip_63.mp4" data-start="2.633333" data-hf-media-start-basis="local" data-duration="2.366667" data-track-index="6" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2b-sh3" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">ÁNH ĐÈN DỊU ÊM</div>
          <div class="wh-card-p">Nâng niu giấc nghỉ sâu</div>
        </div>
      </div>

      <div class="wh-spec-row" style="left: 104px; right: 104px; top: 804px;">
        <div id="s2b-p1" class="wh-spec-item">YÊN TĨNH TUYỆT ĐỐI</div>
        <div id="s2b-p2" class="wh-spec-item">KÍN ĐÁO RIÊNG TƯ</div>
        <div id="s2b-p3" class="wh-spec-item">ÁNH ĐÈN DỊU ÊM ÁI</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s2b-hdr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s2b-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.44, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s2b-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.20);

    tl.fromTo("#s2b-hero", {{ opacity: 0, x: -95 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 0.06);
    tl.fromTo("#s2b-c2", {{ opacity: 0, x: 90 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 0.22);
    tl.fromTo("#s2b-c3", {{ opacity: 0, x: 110 }}, {{ opacity: 1, x: 0, duration: 0.48, ease: "power3.out" }}, 0.36);

    tl.fromTo("#s2b-p1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26, ease: "power3.out" }}, 1.10);
    tl.fromTo("#s2b-sh1", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.62, ease: "power2.out" }}, 2.61);
    tl.fromTo("#s2b-sh2", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.62, ease: "power2.out" }}, 2.63);
    tl.fromTo("#s2b-sh3", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.62, ease: "power2.out" }}, 2.65);

    tl.fromTo("#s2b-p2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26, ease: "power3.out" }}, 2.35);
    tl.fromTo("#s2b-p3", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26, ease: "power3.out" }}, 3.40);

    window.__timelines["slide-02b"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 02C — SPLIT INTO 2 EXACT FRAME-BOUNDED OPAQUE COMPOSITIONS
    #   - slide-02c-a.html: frames 1790..1883 (59.666667s, dur = 3.100000s)
    #   - [62.766667s .. 64.266667s (f=1883..1928): 100% Clean Track 0 PHÒNG VIP]
    #   - slide-02c-b.html: frames 1928..2103 (64.266667s, dur = 5.833333s)
    #   Zero stage opacity fade -> 0.0% CapCut underlying layer bleed at 01:03!
    # =========================================================================
    d2ca = "3.100000"
    write_comp("slide-02c-a.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-02c-a" data-width="1920" data-height="1080">
    <div id="s2ca-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s2ca-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d2ca}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s2ca", "TIỆN ÍCH ĐẶC QUYỀN KHU VIP", "THƯ GIÃN TOÀN THÂN · GHẾ MASSAGE KINGSPORT", "wh-disp-lg")}

      <div id="s2ca-c1" class="wh-card" style="left: 104px; top: 202px; width: 842px; height: 664px;">
        <video id="s2ca-v1" class="clip wh-vid-fill" src="assets/slides/h_kingsport_1.mp4" data-start="0" data-duration="{d2ca}" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">GHẾ MASSAGE TOÀN THÂN KINGSPORT</div>
          <div class="wh-card-p">Thả lỏng cơ thể êm ái trước hoặc sau khi làm dịch vụ</div>
        </div>
      </div>

      <div id="s2ca-c2" class="wh-card" style="left: 974px; top: 202px; width: 842px; height: 664px;">
        <video id="s2ca-v2" class="clip wh-vid-fill" src="assets/slides/h_kingsport_2.mp4" data-start="0" data-duration="{d2ca}" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">TRẢI NGHIỆM NHƯ KỲ NGHỈ DƯỠNG</div>
          <div class="wh-card-p">Không gian thoáng đãng · Chăm sóc trọn vẹn từng khoảnh khắc</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s2ca-hdr", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s2ca-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 0.16);
    tl.fromTo("#s2ca-c1", {{ opacity: 0, x: -75 }}, {{ opacity: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 0.06);
    tl.fromTo("#s2ca-c2", {{ opacity: 0, x: 75 }}, {{ opacity: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 0.20);
    window.__timelines["slide-02c-a"] = tl;
  </script>
</template>
""")

    d2cb = "5.833333"
    write_comp("slide-02c-b.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}
    .drink-typo-item {{
      padding: 24px 30px;
      border-radius: 16px;
      background: linear-gradient(90deg, rgba(44, 30, 19, 0.82) 0%, rgba(26, 18, 13, 0.45) 100%);
      border-left: 5px solid var(--champagne);
      box-shadow: 0 18px 42px rgba(0,0,0,0.52);
    }}
    .drink-typo-title {{
      font-family: "Oswald", sans-serif;
      font-weight: 700;
      font-size: 46px;
      line-height: 1.12;
      letter-spacing: 0.02em;
      color: #FFF4D4;
      text-transform: uppercase;
      text-shadow: 0 3px 14px rgba(0,0,0,0.85);
    }}
    .drink-typo-desc {{
      margin-top: 6px;
      font-family: "Be Vietnam Pro", sans-serif;
      font-weight: 600;
      font-size: 22px;
      color: #F0E6D6;
      text-shadow: 0 2px 10px rgba(0,0,0,0.85);
    }}
  </style>
  <div id="root" data-composition-id="slide-02c-b" data-width="1920" data-height="1080">
    <div id="s2cb-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s2cb-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d2cb}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s2cb", "PHỤC VỤ TẬN TÂM · HOÀN TOÀN MIỄN PHÍ", "Thưởng Thức Đồ Uống Tươi Mát Tận Ghế", "wh-disp-edit")}

      <div id="s2cb-hero" class="wh-card" style="left: 96px; top: 202px; width: 1150px; height: 664px;">
        <video id="s2cb-vid1" class="clip wh-vid-fill" src="assets/slides/h_cs2_sofa_serve1.mp4" data-start="0" data-duration="2.700000" data-track-index="1" muted playsinline></video>
        <video id="s2cb-vid2" class="clip wh-vid-fill" src="assets/slides/h_cs2_sofa_serve2.mp4" data-start="2.700000" data-hf-media-start-basis="local" data-duration="3.133333" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s2cb-sh" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">CHU ĐÁO NHƯ MỘT KỲ NGHỈ DƯỠNG</div>
          <div class="wh-card-p">Đồ uống chuẩn bị tươi mới phục vụ miễn phí ngay tại ghế khu VIP</div>
        </div>
      </div>

      <div style="position: absolute; left: 1280px; top: 214px; width: 544px; height: 640px; display: flex; flex-direction: column; justify-content: space-between; z-index: 16;">
        <div id="s2cb-d1" class="drink-typo-item">
          <div class="drink-typo-title">NƯỚC CAM TƯƠI</div>
          <div class="drink-typo-desc">Giàu Vitamin C · Tươi mát mỗi ngày</div>
        </div>

        <div id="s2cb-d2" class="drink-typo-item">
          <div class="drink-typo-title">TRÀ CHANH MÁT LẠNH</div>
          <div class="drink-typo-desc">Thanh mát giải nhiệt tức thì</div>
        </div>

        <div id="s2cb-d3" class="drink-typo-item" style="border-left-color: #D94148;">
          <div class="drink-typo-title">CÀ PHÊ ĐẬM ĐÀ</div>
          <div class="drink-typo-desc">Tỉnh táo chuẩn phong vị phái mạnh</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s2cb-hdr", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.30, ease: "power3.out" }}, 0.02);
    tl.fromTo("#s2cb-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.18);
    tl.fromTo("#s2cb-hero", {{ opacity: 0, scale: 0.96, x: -45 }}, {{ opacity: 1, scale: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 0.04);
    tl.fromTo("#s2cb-sh", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.72, ease: "power2.out" }}, 0.28);

    tl.fromTo("#s2cb-vid1", {{ scale: 1.0 }}, {{ scale: 1.04, duration: 2.68, ease: "none" }}, 0.02);
    tl.fromTo("#s2cb-vid2", {{ scale: 1.0 }}, {{ scale: 1.04, duration: 3.10, ease: "none" }}, 2.70);
    tl.fromTo("#s2cb-sh", {{ xPercent: -120, opacity: 0.75 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out", immediateRender: false }}, 2.69);

    tl.fromTo("#s2cb-d1", {{ opacity: 0, x: 55 }}, {{ opacity: 1, x: 0, duration: 0.36, ease: "power3.out" }}, 1.58);
    tl.fromTo("#s2cb-d2", {{ opacity: 0, x: 55 }}, {{ opacity: 1, x: 0, duration: 0.36, ease: "power3.out" }}, 2.14);
    tl.fromTo("#s2cb-d3", {{ opacity: 0, x: 55 }}, {{ opacity: 1, x: 0, duration: 0.36, ease: "power3.out" }}, 2.68);

    window.__timelines["slide-02c-b"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 03 (frames 2407..2624 | 80.233333s, dur = 7.233333s)
    # =========================================================================
    d3 = "7.233333"
    write_comp("slide-03.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}
    .wh-play-card {{
      position: absolute;
      width: 332px;
      height: 608px;
      border-radius: 18px;
      overflow: hidden;
      background: #17120E;
      border: 1.5px solid rgba(243, 214, 156, 0.42);
      box-shadow: 0 28px 60px rgba(0, 0, 0, 0.82);
      transform-origin: 50% 95%;
    }}
    .wh-step-num {{
      position: absolute;
      left: 22px;
      top: 14px;
      z-index: 6;
      font-family: "Playfair Display", serif;
      font-weight: 800;
      font-style: italic;
      font-size: 36px;
      color: #FFF0C8;
      text-shadow: 0 3px 14px rgba(0, 0, 0, 0.92);
    }}
  </style>
  <div id="root" data-composition-id="slide-03" data-width="1920" data-height="1080">
    <div id="s3-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s3-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d3}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s3", "PHỤC VỤ RIÊNG BIỆT 1 : 1", "TRỌN VẸN 5 BƯỚC THƯ GIÃN ĐẶC QUYỀN", "wh-disp-lg")}

      <div id="s3-c1" class="wh-play-card" style="left: 118px; top: 242px; z-index: 5;" data-layout-allow-overlap>
        <video id="s3-v1a" class="clip wh-vid-fill" src="assets/slides/v_wash_cs2_c9700.mp4" data-start="0" data-duration="3.600000" data-track-index="1" muted playsinline></video>
        <video id="s3-v1b" class="clip wh-vid-fill" src="assets/slides/v_wash_cs2_3725.mp4" data-start="3.600000" data-hf-media-start-basis="local" data-duration="3.633333" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s3-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-step-num" data-layout-ignore>01</div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">GỘI ĐẦU</div>
          <div class="wh-card-p">Dưỡng sinh bọt mịn êm ái</div>
        </div>
      </div>

      <div id="s3-c2" class="wh-play-card" style="left: 456px; top: 218px; z-index: 6;" data-layout-allow-overlap>
        <video id="s3-v2a" class="clip wh-vid-fill" src="assets/slides/v_msg_neck.mp4" data-start="0.500000" data-hf-media-start-basis="local" data-duration="3.366667" data-track-index="3" muted playsinline></video>
        <video id="s3-v2b" class="clip wh-vid-fill" src="assets/slides/v_msg_td_93.mp4" data-start="3.866667" data-hf-media-start-basis="local" data-duration="3.366666" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s3-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-step-num" data-layout-ignore>02</div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">MASSAGE</div>
          <div class="wh-card-p">Cổ vai gáy ấn huyệt sâu</div>
        </div>
      </div>

      <div id="s3-c3" class="wh-play-card" style="left: 794px; top: 204px; z-index: 7;" data-layout-allow-overlap>
        <video id="s3-v3a" class="clip wh-vid-fill" src="assets/slides/v_ear_cs1_108.mp4" data-start="1.100000" data-hf-media-start-basis="local" data-duration="3.066667" data-track-index="5" muted playsinline></video>
        <video id="s3-v3b" class="clip wh-vid-fill" src="assets/slides/v_ear_prep.mp4" data-start="4.166667" data-hf-media-start-basis="local" data-duration="3.066666" data-track-index="6" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s3-sh3" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-step-num" data-layout-ignore>03</div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">RÁY TAI</div>
          <div class="wh-card-p">Nhẹ nhàng êm dịu thư thái</div>
        </div>
      </div>

      <div id="s3-c4" class="wh-play-card" style="left: 1132px; top: 218px; z-index: 8;" data-layout-allow-overlap>
        <video id="s3-v4a" class="clip wh-vid-fill" src="assets/slides/v_real_facemask_clean.mp4" data-start="1.966667" data-hf-media-start-basis="local" data-duration="2.633333" data-track-index="7" muted playsinline></video>
        <video id="s3-v4b" class="clip wh-vid-fill" src="assets/slides/v_face_cs1_rm101.mp4" data-start="4.600000" data-hf-media-start-basis="local" data-duration="2.633333" data-track-index="8" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s3-sh4" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-step-num" data-layout-ignore>04</div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">ĐẮP MẶT</div>
          <div class="wh-card-p">Mặt nạ cấp ẩm sáng mịn</div>
        </div>
      </div>

      <div id="s3-c5" class="wh-play-card" style="left: 1470px; top: 242px; z-index: 9;" data-layout-allow-overlap>
        <video id="s3-v5a" class="clip wh-vid-fill" src="assets/slides/v_ai_peel.mp4" data-start="2.800000" data-hf-media-start-basis="local" data-duration="2.300000" data-track-index="9" muted playsinline></video>
        <video id="s3-v5b" class="clip wh-vid-fill" src="assets/slides/v_shave_care.mp4" data-start="5.100000" data-hf-media-start-basis="local" data-duration="2.133333" data-track-index="10" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s3-sh5" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-step-num" data-layout-ignore>05</div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">LỘT MỤN</div>
          <div class="wh-card-p">Than hoạt tính sạch thoáng</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s3-hdr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s3-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.44, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s3-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.22);

    const cards = [
      {{ id: "#s3-c1", sh: "#s3-sh1", dx: 676, rot: -6.0, t: 0.08, tc: 3.60 }},
      {{ id: "#s3-c2", sh: "#s3-sh2", dx: 338, rot: -3.0, t: 0.62, tc: 3.87 }},
      {{ id: "#s3-c3", sh: "#s3-sh3", dx: 0,   rot:  0.0, t: 1.22, tc: 4.17 }},
      {{ id: "#s3-c4", sh: "#s3-sh4", dx: -338, rot: 3.0, t: 2.08, tc: 4.60 }},
      {{ id: "#s3-c5", sh: "#s3-sh5", dx: -676, rot: 6.0, t: 2.90, tc: 5.10 }},
    ];
    cards.forEach((c) => {{
      tl.fromTo(
        c.id,
        {{ opacity: 0, x: c.dx, y: 90, rotation: 0, scale: 0.88 }},
        {{ opacity: 1, x: 0, y: 0, rotation: c.rot, scale: 1.0, duration: 0.48, ease: "power3.out" }},
        c.t
      );
      tl.fromTo(c.sh, {{ xPercent: -120, opacity: 0.85 }}, {{ xPercent: 140, opacity: 0, duration: 0.62, ease: "power2.out" }}, c.t + 0.16);
      tl.to(c.id, {{ y: -14, scale: 1.02, duration: 0.28, yoyo: true, repeat: 1, ease: "sine.inOut" }}, c.t + 0.48);
      tl.fromTo(c.sh, {{ xPercent: -120, opacity: 0.72 }}, {{ xPercent: 140, opacity: 0, duration: 0.58, ease: "power2.out", immediateRender: false }}, c.tc);
    }});

    tl.fromTo("#s3-v4a", {{ scale: 1.0 }}, {{ scale: 1.06, duration: 2.60, ease: "none" }}, 1.98);
    tl.fromTo("#s3-v5a", {{ scale: 1.0 }}, {{ scale: 1.06, duration: 2.28, ease: "none" }}, 2.82);

    window.__timelines["slide-03"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 04 (frames 2661..3000 | 88.700000s, dur = 11.300000s)
    # =========================================================================
    d4 = "11.300000"
    write_comp("slide-04.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-04" data-width="1920" data-height="1080">
    <div id="s4-stage" class="wh-stage">
      <div class="wh-bg-walnut"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s4-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d4}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s4", "TAY NGHỀ CHUẨN MỰC · TẠO KIỂU PHÁI MẠNH", "ĐỊNH HÌNH PHONG CÁCH · TỈ MỈ TỪNG ĐƯỜNG KÉO", "wh-disp-arch")}

      <div id="s4-col1" class="wh-card" style="left: 96px; top: 202px; width: 396px; height: 672px;">
        <video id="s4-vv1" class="clip wh-vid-fill" src="assets/slides/v_cut_scissor.mp4" data-start="0" data-duration="5.650000" data-track-index="1" muted playsinline></video>
        <video id="s4-vv2" class="clip wh-vid-fill" src="assets/slides/v_cut_blowdry_clean.mp4" data-start="5.650000" data-hf-media-start-basis="local" data-duration="5.650000" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s4-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3" style="font-size: 33px;">PHONG THÁI BẢNH BAO</div>
          <div class="wh-card-p">Sấy tạo phồng chuẩn nếp tự nhiên</div>
        </div>
      </div>

      <div id="s4-col2" class="wh-card" style="left: 516px; top: 202px; width: 396px; height: 672px;">
        <video id="s4-vv3" class="clip wh-vid-fill" src="assets/slides/v_cut_angle.mp4" data-start="0" data-duration="5.650000" data-track-index="3" muted playsinline></video>
        <video id="s4-vv4" class="clip wh-vid-fill" src="assets/slides/v_cut_barber.mp4" data-start="5.650000" data-hf-media-start-basis="local" data-duration="5.650000" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3" style="font-size: 33px;">TỈ MỈ TỪNG ĐƯỜNG CẮT</div>
          <div class="wh-card-p">Cân chỉnh hài hòa theo gương mặt</div>
        </div>
      </div>

      <div id="s4-hero" class="wh-card" style="left: 936px; top: 202px; width: 888px; height: 484px;">
        <video id="s4-vh1" class="clip wh-vid-fill" src="assets/slides/h_cut_master1.mp4" data-start="0" data-duration="3.800000" data-track-index="5" muted playsinline></video>
        <video id="s4-vh2" class="clip wh-vid-fill" src="assets/slides/h_cut_master2.mp4" data-start="3.800000" data-hf-media-start-basis="local" data-duration="3.800000" data-track-index="6" muted playsinline></video>
        <video id="s4-vh3" class="clip wh-vid-fill" src="assets/slides/h_cut_fade_clean.mp4" data-start="7.600000" data-hf-media-start-basis="local" data-duration="3.700000" data-track-index="7" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s4-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">PHONG ĐỘ BẮT ĐẦU TỪ SỰ CHỈN CHU</div>
        </div>
      </div>

      <div style="position: absolute; left: 936px; top: 710px; width: 888px; display: flex; flex-direction: column; gap: 16px; z-index: 15;">
        <div id="s4-b1" class="wh-spec-item" style="font-size: 24px;">TƯ VẤN KIỂU TÓC PHÙ HỢP TỪNG KHUÔN MẶT</div>
        <div id="s4-b2" class="wh-spec-item" style="font-size: 24px;">ĐƯỜNG KÉO &amp; CHUYỂN MƯỢT SẮC NÉT</div>
        <div id="s4-b3" class="wh-spec-item" style="font-size: 24px;">VUỐT SÁP TẠO KIỂU LỊCH LÃM CHUẨN QUÝ ÔNG</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s4-hdr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s4-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.out" }}, 0.12);
    tl.fromTo("#s4-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 0.22);

    tl.fromTo("#s4-col1", {{ opacity: 0, y: 95 }}, {{ opacity: 1, y: 0, duration: 0.46, ease: "power3.out" }}, 0.06);
    tl.fromTo("#s4-col2", {{ opacity: 0, y: -95 }}, {{ opacity: 1, y: 0, duration: 0.46, ease: "power3.out" }}, 0.20);
    tl.fromTo("#s4-hero", {{ opacity: 0, x: 90 }}, {{ opacity: 1, x: 0, duration: 0.48, ease: "power3.out" }}, 0.32);

    tl.fromTo("#s4-sh1", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 5.65);
    tl.fromTo("#s4-sh2", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 3.80);
    tl.fromTo("#s4-sh2", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out", immediateRender: false }}, 7.60);

    tl.fromTo("#s4-b1", {{ opacity: 0, x: 40 }}, {{ opacity: 1, x: 0, duration: 0.30, ease: "power3.out" }}, 2.40);
    tl.fromTo("#s4-b2", {{ opacity: 0, x: 40 }}, {{ opacity: 1, x: 0, duration: 0.30, ease: "power3.out" }}, 4.60);
    tl.fromTo("#s4-b3", {{ opacity: 0, x: 40 }}, {{ opacity: 1, x: 0, duration: 0.30, ease: "power3.out" }}, 7.20);

    window.__timelines["slide-04"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 05 (frames 3000..3149 | 100.000000s, dur = 4.966667s)
    # =========================================================================
    d5 = "4.966667"
    write_comp("slide-05.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}
    .wh-diag-card {{
      position: absolute;
      top: 202px;
      height: 672px;
      overflow: hidden;
      background: #17120E;
      clip-path: polygon(6% 0%, 100% 0%, 94% 100%, 0% 100%);
      border-top: 1.5px solid rgba(243, 214, 156, 0.45);
      border-bottom: 1.5px solid rgba(243, 214, 156, 0.45);
      filter: drop-shadow(0 22px 44px rgba(0,0,0,0.82));
    }}
  </style>
  <div id="root" data-composition-id="slide-05" data-width="1920" data-height="1080">
    <div id="s5-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s5-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d5}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s5", "CHĂM SÓC DIỆN MẠO · SÁNG MỊN TỰ TIN", "CẠO MẶT ÊM ÁI · CHỈN CHU TỪNG ĐƯỜNG NÉT", "wh-disp-arch")}

      <div id="s5-c1" class="wh-diag-card" style="left: 86px; width: 572px;" data-layout-allow-overlap>
        <video id="s5-v1" class="clip wh-vid-fill" src="assets/slides/v_shave_foam_m1.mp4" data-start="0" data-duration="{d5}" data-track-index="1" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption" style="left: 48px; right: 48px;">
          <div class="wh-card-h3">LÀM DỊU LÀN DA</div>
          <div class="wh-card-p">Ủ bọt mịn cấp ẩm làm mềm chân râu</div>
        </div>
      </div>

      <div id="s5-c2" class="wh-diag-card" style="left: 674px; width: 572px;" data-layout-allow-overlap>
        <video id="s5-v2" class="clip wh-vid-fill" src="assets/slides/v_shave_blade_m2.mp4" data-start="0" data-duration="{d5}" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s5-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption" style="left: 48px; right: 48px;">
          <div class="wh-card-h3">LƯỠI DAO ÊM ÁI</div>
          <div class="wh-card-p">Đường cạo nhẹ nhàng · Mịn màng không rát</div>
        </div>
      </div>

      <div id="s5-c3" class="wh-diag-card" style="left: 1262px; width: 572px;" data-layout-allow-overlap>
        <video id="s5-v3" class="clip wh-vid-fill" src="assets/slides/v_shave_care_m3.mp4" data-start="0" data-duration="{d5}" data-track-index="3" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="wh-card-caption" style="left: 48px; right: 48px;">
          <div class="wh-card-h3">DIỆN MẠO SÁNG BỪNG</div>
          <div class="wh-card-p">Tự tin lịch lãm chuẩn quý ông</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s5-hdr", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s5-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.40, ease: "power3.out" }}, 0.08);
    tl.fromTo("#s5-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.85, ease: "power2.inOut" }}, 0.16);

    tl.fromTo("#s5-c1", {{ opacity: 0, x: -45, y: 85 }}, {{ opacity: 1, x: 0, y: 0, duration: 0.42, ease: "power3.out" }}, 0.05);
    tl.fromTo("#s5-c2", {{ opacity: 0, x: 45, y: -85 }}, {{ opacity: 1, x: 0, y: 0, duration: 0.42, ease: "power3.out" }}, 0.18);
    tl.fromTo("#s5-sh2", {{ xPercent: -130, opacity: 0.85 }}, {{ xPercent: 140, opacity: 0, duration: 0.68, ease: "power2.out" }}, 0.34);
    tl.fromTo("#s5-c3", {{ opacity: 0, x: -45, y: 85 }}, {{ opacity: 1, x: 0, y: 0, duration: 0.42, ease: "power3.out" }}, 0.30);

    window.__timelines["slide-05"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 06 (frames 3149..3347 | 104.966667s, dur = 6.600000s — synced to User's CapCut edit!)
    # =========================================================================
    d6 = "6.600000"
    write_comp("slide-06.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-06" data-width="1920" data-height="1080">
    <div id="s6-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s6-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d6}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s6", "TẬN TÂM TỪNG CHI TIẾT · LẤY RÁY TAI THƯ GIÃN", "Chăm Chút Những Điều Nhỏ Nhất", "wh-disp-edit")}

      <div id="s6-beata" style="position: absolute; inset: 0;">
        <div id="s6a-left" class="wh-card" style="left: 104px; top: 202px; width: 1120px; height: 572px;">
          <video id="s6a-vh" class="clip wh-vid-fill" src="assets/slides/h_ear_eyemask1.mp4" data-start="0" data-duration="4.566667" data-track-index="1" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3">MẶT NẠ MẮT DỊU ÊM · THƯ GIÃN SÂU</div>
            <div class="wh-card-p">Tái tạo cảm giác dễ chịu · Nhẹ nhàng chìm vào giấc nghỉ</div>
          </div>
        </div>

        <div id="s6a-right" class="wh-card" style="left: 1252px; top: 202px; width: 564px; height: 572px;">
          <video id="s6a-vv" class="clip wh-vid-fill" src="assets/slides/v_ear_eyemask_cs1.mp4" data-start="0" data-duration="4.566667" data-track-index="2" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3">ÊM NHƯ LÔNG HỒNG</div>
            <div class="wh-card-p">Chăm sóc tỉ mỉ không vội vàng</div>
          </div>
        </div>
      </div>

      <div id="s6-beatb" style="position: absolute; inset: 0; opacity: 0;">
        <div id="s6b-left" class="wh-card" style="left: 104px; top: 202px; width: 564px; height: 572px;">
          <video id="s6b-vv" class="clip wh-vid-fill" src="assets/slides/v_ear_cs2_c9712.mp4" data-start="4.566667" data-hf-media-start-basis="local" data-duration="2.033333" data-track-index="3" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3">ĐÈN SOI CHUYÊN DỤNG</div>
            <div class="wh-card-p">Chuẩn xác &amp; an toàn tuyệt đối</div>
          </div>
        </div>

        <div id="s6b-right" class="wh-card" style="left: 696px; top: 202px; width: 1120px; height: 572px;">
          <video id="s6b-vh" class="clip wh-vid-fill" src="assets/slides/h_ear_macro_0083.mp4" data-start="4.566667" data-hf-media-start-basis="local" data-duration="2.033333" data-track-index="4" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div id="s6b-sh" class="wh-card-sheen" data-layout-ignore></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3">DỤNG CỤ KHỬ KHUẨN · THAO TÁC TINH TẾ</div>
            <div class="wh-card-p">Đem lại cảm giác nhẹ nhõm và sảng khoái hoàn toàn</div>
          </div>
        </div>
      </div>

      <div class="wh-spec-row" style="left: 104px; right: 104px; top: 804px;">
        <div id="s6-p1" class="wh-spec-item">ÁNH ĐÈN SOI RÕ AN TOÀN</div>
        <div id="s6-p2" class="wh-spec-item">MẶT NẠ MẮT DỊU ÊM</div>
        <div id="s6-p3" class="wh-spec-item">DỤNG CỤ KHỬ KHUẨN RIÊNG</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set("#s6-beatb", {{ opacity: 0 }});

    tl.fromTo("#s6-hdr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s6-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.44, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s6-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 0.18);

    tl.fromTo("#s6a-left", {{ opacity: 0, x: -80 }}, {{ opacity: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 0.06);
    tl.fromTo("#s6a-right", {{ opacity: 0, x: 80 }}, {{ opacity: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 0.20);
    tl.to("#s6-beata", {{ opacity: 0, x: -70, duration: 0.22, ease: "power2.in" }}, 4.35);

    tl.fromTo("#s6-beatb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.16 }}, 4.56);
    tl.fromTo("#s6b-left", {{ opacity: 0, x: -75 }}, {{ opacity: 1, x: 0, duration: 0.40, ease: "power3.out" }}, 4.57);
    tl.fromTo("#s6b-right", {{ opacity: 0, x: 75 }}, {{ opacity: 1, x: 0, duration: 0.40, ease: "power3.out" }}, 4.65);
    tl.fromTo("#s6b-sh", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 4.80);

    tl.fromTo("#s6-p1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 0.80);
    tl.fromTo("#s6-p2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 2.40);
    tl.fromTo("#s6-p3", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 4.85);

    window.__timelines["slide-06"] = tl;
  </script>
</template>
""")
