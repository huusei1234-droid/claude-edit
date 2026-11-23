from v3_styles_and_helpers import SHARED_LUXURY_CSS, bullion_text, lux_header, write_comp

def build_slides_part2():
    # =========================================================================
    # SLIDE 07 (frames 3422..3810 | 114.066667s, dur = 12.933333s)
    # =========================================================================
    d7 = "12.933333"
    write_comp("slide-07.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-07" data-width="1920" data-height="1080">
    <div id="s7-stage" class="wh-stage">
      <div class="wh-bg-walnut"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s7-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d7}" data-track-index="0" muted playsinline data-layout-ignore></video>

      <div id="s7-pha" style="position: absolute; inset: 0;">
        {lux_header("s7a", "CHĂM SÓC DA & THƯ GIÃN SÂU", "XÔNG HƠI & MASSAGE MẶT · XẢ CĂNG THẲNG", "wh-disp-lg")}

        <div id="s7a-c1" class="wh-card" style="left: 104px; top: 202px; width: 420px; height: 672px;">
          <video id="s7a-v1" class="clip wh-vid-fill" src="assets/slides/v_wash_cs2_c9702.mp4" data-start="0" data-duration="3.833333" data-track-index="1" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><div class="wh-card-h3">GỘI DƯỠNG SINH</div><div class="wh-card-p">Sạch sâu &amp; sảng khoái</div></div>
        </div>

        <div id="s7a-c2" class="wh-card" style="left: 552px; top: 202px; width: 816px; height: 672px;">
          <video id="s7a-v2" class="clip wh-vid-fill" src="assets/slides/h_steam_face.mp4" data-start="0" data-duration="3.833333" data-track-index="2" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><div class="wh-card-h3">XÔNG HƠI THƯ GIÃN SÂU</div><div class="wh-card-p">Hơi ấm dịu nhẹ mở thoáng lỗ chân lông</div></div>
        </div>

        <div id="s7a-c3" class="wh-card" style="left: 1396px; top: 202px; width: 420px; height: 672px;">
          <video id="s7a-v3" class="clip wh-vid-fill" src="assets/slides/v_face_cs1_rm85.mp4" data-start="0" data-duration="3.833333" data-track-index="3" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><div class="wh-card-h3">MASSAGE MẶT</div><div class="wh-card-p">Nâng cơ sáng khỏe da</div></div>
        </div>
      </div>

      <div id="s7-phb" style="position: absolute; inset: 0; opacity: 0;">
        {lux_header("s7b", "PHỤC HỒI THỂ LỰC TOÀN DIỆN", "GIẢI TỎA MỆT MỎI · TÁI TẠO NĂNG LƯỢNG", "wh-disp-lg")}

        <div id="s7b-rail" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;">
          <div id="s7b-c1" class="wh-card" style="left: 108px; top: 202px; width: 536px; height: 572px;">
            <video id="s7b-v1a" class="clip wh-vid-fill" src="assets/slides/h_msg_arm_c9787.mp4" data-start="3.833333" data-hf-media-start-basis="local" data-duration="4.566667" data-track-index="4" muted playsinline></video>
            <video id="s7b-v1b" class="clip wh-vid-fill" src="assets/slides/v_msg_arm.mp4" data-start="8.400000" data-hf-media-start-basis="local" data-duration="4.533333" data-track-index="5" muted playsinline></video>
            <div class="wh-card-shade"></div>
            <div id="s7b-sh1" class="wh-card-sheen" data-layout-ignore></div>
            <div class="wh-card-caption">
              <div class="wh-card-h3">MASSAGE TAY — HẾT MỎI</div>
              <div class="wh-card-p">Thả lỏng cơ bắp &amp; khớp cổ tay</div>
            </div>
          </div>

          <div id="s7b-c2" class="wh-card" style="left: 692px; top: 202px; width: 536px; height: 572px;">
            <video id="s7b-v2a" class="clip wh-vid-fill" src="assets/slides/h_msg_leg_0147.mp4" data-start="3.833333" data-hf-media-start-basis="local" data-duration="4.566667" data-track-index="6" muted playsinline></video>
            <video id="s7b-v2b" class="clip wh-vid-fill" src="assets/slides/v_msg_foot.mp4" data-start="8.400000" data-hf-media-start-basis="local" data-duration="4.533333" data-track-index="7" muted playsinline></video>
            <div class="wh-card-shade"></div>
            <div id="s7b-sh2" class="wh-card-sheen" data-layout-ignore></div>
            <div class="wh-card-caption">
              <div class="wh-card-h3">MASSAGE CHÂN — NHẸ BƯỚC</div>
              <div class="wh-card-p">Ấn huyệt lưu thông khí huyết</div>
            </div>
          </div>

          <div id="s7b-c3" class="wh-card" style="left: 1276px; top: 202px; width: 536px; height: 572px;">
            <video id="s7b-v3a" class="clip wh-vid-fill" src="assets/slides/h_msg_body_c9776.mp4" data-start="3.833333" data-hf-media-start-basis="local" data-duration="4.566667" data-track-index="8" muted playsinline></video>
            <video id="s7b-v3b" class="clip wh-vid-fill" src="assets/slides/v_msg_aotim_long.mp4" data-start="8.400000" data-hf-media-start-basis="local" data-duration="4.533333" data-track-index="9" muted playsinline></video>
            <div class="wh-card-shade"></div>
            <div id="s7b-sh3" class="wh-card-sheen" data-layout-ignore></div>
            <div class="wh-card-caption">
              <div class="wh-card-h3">MASSAGE CỔ VAI GÁY &amp; LƯNG</div>
              <div class="wh-card-p">Nhẹ người khỏe khoắn tức thì</div>
            </div>
          </div>
        </div>

        <div class="wh-spec-row" style="left: 108px; right: 108px; top: 804px;">
          <div id="s7b-p1" class="wh-spec-item">LỰC TAY CHẮC CHẮN</div>
          <div id="s7b-p2" class="wh-spec-item">BẤM ĐÚNG HUYỆT ĐẠO</div>
          <div id="s7b-p3" class="wh-spec-item">PHỤC HỒI SINH LỰC</div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set("#s7-phb", {{ opacity: 0 }});

    tl.fromTo("#s7a-hdr", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s7a-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.88, ease: "power2.inOut" }}, 0.16);
    tl.fromTo("#s7a-c1", {{ opacity: 0, y: -75 }}, {{ opacity: 1, y: 0, duration: 0.38, ease: "power3.out" }}, 0.06);
    tl.fromTo("#s7a-c2", {{ opacity: 0, scale: 0.96 }}, {{ opacity: 1, scale: 1, duration: 0.38, ease: "power3.out" }}, 0.16);
    tl.fromTo("#s7a-c3", {{ opacity: 0, y: 75 }}, {{ opacity: 1, y: 0, duration: 0.38, ease: "power3.out" }}, 0.26);
    tl.to("#s7-pha", {{ opacity: 0, x: -80, duration: 0.22, ease: "power2.in" }}, 3.60);

    tl.fromTo("#s7-phb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.16 }}, 3.83);
    tl.fromTo("#s7b-hdr", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, 3.85);
    tl.fromTo("#s7b-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 4.05);

    tl.fromTo("#s7b-c1", {{ opacity: 0, x: 110 }}, {{ opacity: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 3.86);
    tl.fromTo("#s7b-c2", {{ opacity: 0, x: 130 }}, {{ opacity: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 5.52);
    tl.fromTo("#s7b-c3", {{ opacity: 0, x: 150 }}, {{ opacity: 1, x: 0, duration: 0.44, ease: "power3.out" }}, 6.90);

    tl.fromTo("#s7b-sh1", {{ xPercent: -120, opacity: 0.72 }}, {{ xPercent: 140, opacity: 0, duration: 0.60, ease: "power2.out" }}, 8.38);
    tl.fromTo("#s7b-sh2", {{ xPercent: -120, opacity: 0.72 }}, {{ xPercent: 140, opacity: 0, duration: 0.60, ease: "power2.out" }}, 8.40);
    tl.fromTo("#s7b-sh3", {{ xPercent: -120, opacity: 0.72 }}, {{ xPercent: 140, opacity: 0, duration: 0.60, ease: "power2.out" }}, 8.42);

    tl.fromTo("#s7b-rail", {{ x: 16 }}, {{ x: -16, duration: 9.0, ease: "sine.inOut" }}, 3.85);

    tl.fromTo("#s7b-p1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 8.82);
    tl.fromTo("#s7b-p2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 10.06);
    tl.fromTo("#s7b-p3", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 11.48);

    window.__timelines["slide-07"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 08 (frames 3810..4031 | 127.000000s, dur = 7.366667s — synced to User's CapCut edit!)
    # =========================================================================
    d8 = "7.366667"
    write_comp("slide-08.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}</style>
  <div id="root" data-composition-id="slide-08" data-width="1920" data-height="1080">
    <div id="s8-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s8-bokeh" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="{d8}" data-track-index="0" muted playsinline data-layout-ignore></video>

      {lux_header("s8", "CHỈN CHU ĐẾN TỪNG CHI TIẾT", "HOÀN THIỆN PHONG THÁI QUÝ ÔNG", "wh-disp-lg")}

      <div id="s8-c1" class="wh-card" style="left: 104px; top: 202px; width: 842px; height: 572px;">
        <video id="s8-v1a" class="clip wh-vid-fill" src="assets/slides/h_nail_hand_real.mp4" data-start="0" data-duration="4.866667" data-track-index="1" muted playsinline></video>
        <video id="s8-v1b" class="clip wh-vid-fill" src="assets/slides/h_nail_hand.mp4" data-start="4.866667" data-hf-media-start-basis="local" data-duration="2.500000" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s8-sh1" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">CHĂM SÓC MÓNG TAY TỈ MỈ</div>
          <div class="wh-card-p">Dụng cụ khử khuẩn riêng · Cắt tỉa gọn gàng chuẩn xác</div>
        </div>
      </div>

      <div id="s8-c2" class="wh-card" style="left: 974px; top: 202px; width: 842px; height: 572px;">
        <video id="s8-v2a" class="clip wh-vid-fill" src="assets/slides/h_nail_foot_real.mp4" data-start="0" data-duration="4.866667" data-track-index="3" muted playsinline></video>
        <video id="s8-v2b" class="clip wh-vid-fill" src="assets/slides/v_hand_cs2_c9748.mp4" data-start="4.866667" data-hf-media-start-basis="local" data-duration="2.500000" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div id="s8-sh2" class="wh-card-sheen" data-layout-ignore></div>
        <div class="wh-card-caption">
          <div class="wh-card-h3">CHĂM SÓC MÓNG CHÂN SẠCH SẼ</div>
          <div class="wh-card-p">Thư thái trên ghế êm · Chỉn chu từ đầu đến cuối</div>
        </div>
      </div>

      <div class="wh-spec-row" style="left: 104px; right: 104px; top: 804px;">
        <div id="s8-p1" class="wh-spec-item">KỀM RIÊNG KHỬ KHUẨN</div>
        <div id="s8-p2" class="wh-spec-item">TỈA GỌN TINH TẾ</div>
        <div id="s8-p3" class="wh-spec-item">CHỈN CHU TOÀN DIỆN</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#s8-hdr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }}, 0.0);
    tl.fromTo("#s8-flare", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.44, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s8-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.95, ease: "power2.inOut" }}, 0.20);

    tl.fromTo("#s8-c1", {{ opacity: 0, x: -95 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 0.06);
    tl.fromTo("#s8-sh1", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 0.30);
    tl.fromTo("#s8-c2", {{ opacity: 0, x: 95 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 0.24);
    tl.fromTo("#s8-sh2", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 0.48);

    tl.fromTo("#s8-sh1", {{ xPercent: -120, opacity: 0.75 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out", immediateRender: false }}, 4.86);
    tl.fromTo("#s8-sh2", {{ xPercent: -120, opacity: 0.75 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out", immediateRender: false }}, 4.88);

    tl.fromTo("#s8-p1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 1.20);
    tl.fromTo("#s8-p2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 3.00);
    tl.fromTo("#s8-p3", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.26 }}, 4.80);

    window.__timelines["slide-08"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # REVIEWS B-ROLL COMPOSITION (152.63s - 255.77s)
    # Pure Vietnamese captions + larger text + soft film rounded frame!
    # =========================================================================
    write_comp("reviews-broll.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}
    .rev-pip-vert {{
      position: absolute;
      right: 72px;
      top: 110px;
      width: 464px;
      height: 730px;
      border-radius: 20px;
      overflow: hidden;
      background: #17120E;
      border: 1.5px solid rgba(243, 214, 156, 0.46);
      box-shadow: 0 28px 68px rgba(0, 0, 0, 0.85);
      opacity: 0;
      pointer-events: none;
    }}
    .rev-pip-horiz {{
      position: absolute;
      right: 68px;
      top: 152px;
      width: 696px;
      height: 476px;
      border-radius: 20px;
      overflow: hidden;
      background: #17120E;
      border: 1.5px solid rgba(243, 214, 156, 0.46);
      box-shadow: 0 28px 68px rgba(0, 0, 0, 0.85);
      opacity: 0;
      pointer-events: none;
    }}
    .rev-cutaway-full {{
      position: absolute;
      inset: 0;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: #120D0A;
      opacity: 0;
      pointer-events: none;
    }}
  </style>
  <div id="root" data-composition-id="reviews-broll" data-width="1920" data-height="1080">
    <div id="rev1-box1" class="rev-pip-vert">
      <video id="rev1-v1" class="clip wh-vid-fill" src="assets/slides/v_rev1_aotim_vip.mp4" data-start="155.400000" data-hf-media-start-basis="local" data-duration="5.700000" data-track-index="0" muted playsinline></video>
      <div class="wh-card-shade"></div>
      <div class="wh-card-caption">
        <div class="wh-card-h3" style="font-size:32px;">KHÔNG GIAN VIP SANG TRỌNG</div>
      </div>
    </div>

    <div id="rev1-box2" class="rev-pip-vert">
      <video id="rev1-v2" class="clip wh-vid-fill" src="assets/slides/v_rev1_aotim_msg.mp4" data-start="164.300000" data-hf-media-start-basis="local" data-duration="5.900000" data-track-index="1" muted playsinline></video>
      <div class="wh-card-shade"></div>
      <div class="wh-card-caption">
        <div class="wh-card-h3" style="font-size:32px;">GỘI ĐẦU &amp; MASSAGE ÊM ÁI</div>
      </div>
    </div>

    <div id="rev3-box1" class="rev-cutaway-full">
      <video id="rev3-v1" class="clip wh-vid-fill" src="assets/slides/h_rev3_anhnam_cut1.mp4" data-start="192.200000" data-hf-media-start-basis="local" data-duration="5.100000" data-track-index="2" muted playsinline></video>
    </div>

    <div id="rev3-box2" class="rev-pip-horiz">
      <video id="rev3-v2" class="clip wh-vid-fill" src="assets/slides/h_rev3_anhnam_cut2.mp4" data-start="200.300000" data-hf-media-start-basis="local" data-duration="5.500000" data-track-index="3" muted playsinline></video>
      <div class="wh-card-shade"></div>
      <div class="wh-card-caption">
        <div class="wh-card-h3" style="font-size:32px;">ĐỊNH HÌNH PHONG ĐỘ &amp; THƯ GIÃN</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set(["#rev1-box1", "#rev1-box2", "#rev3-box1", "#rev3-box2"], {{ opacity: 0 }});

    tl.fromTo("#rev1-box1", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 155.40);
    tl.fromTo("#rev1-box1", {{ opacity: 1, y: 0 }}, {{ opacity: 0, y: 18, duration: 0.24, ease: "power2.in", immediateRender: false }}, 160.84);

    tl.fromTo("#rev1-box2", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 164.30);
    tl.fromTo("#rev1-box2", {{ opacity: 1, y: 0 }}, {{ opacity: 0, y: 18, duration: 0.24, ease: "power2.in", immediateRender: false }}, 169.94);

    tl.fromTo("#rev3-box1", {{ opacity: 0, scale: 1.03 }}, {{ opacity: 1, scale: 1.0, duration: 0.24, ease: "power2.out" }}, 192.20);
    tl.to("#rev3-v1", {{ scale: 1.05, duration: 5.00, ease: "none" }}, 192.20);
    tl.fromTo("#rev3-box1", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.22, ease: "power2.in", immediateRender: false }}, 197.06);

    tl.fromTo("#rev3-box2", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 200.30);
    tl.fromTo("#rev3-box2", {{ opacity: 1, y: 0 }}, {{ opacity: 0, y: 18, duration: 0.24, ease: "power2.in", immediateRender: false }}, 205.54);

    window.__timelines["reviews-broll"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 09 (frames 7673..7995 | 255.766667s, dur = 10.733333s)
    # =========================================================================
    d9 = "10.733333"
    write_comp("slide-09.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}
    .s9-backdrop {{
      position: absolute;
      right: 0;
      top: 0;
      width: 1080px;
      height: 1080px;
      background: linear-gradient(270deg, rgba(20, 14, 10, 0.98) 0%, rgba(20, 14, 10, 0.96) 54%, rgba(20, 14, 10, 0.88) 76%, transparent 100%);
      pointer-events: none;
    }}
    .s9-mini {{ width: 262px; height: 322px; border-radius: 16px; }}
    .s9-mini .wh-card-h3 {{ font-size: 27px; }}
    .s9-num {{
      position: absolute;
      left: 16px;
      top: 10px;
      z-index: 6;
      font-family: "Playfair Display", serif;
      font-weight: 800;
      font-style: italic;
      font-size: 28px;
      color: #FFF0C8;
      text-shadow: 0 2px 10px rgba(0,0,0,0.90);
    }}
  </style>
  <div id="root" data-composition-id="slide-09" data-width="1920" data-height="1080">
    <div id="s9-stage" class="wh-stage">
      <div id="s9-shade" class="s9-backdrop" data-layout-ignore></div>

      <div id="s9-hdr" style="position: absolute; left: 980px; right: 48px; top: 68px; text-align: center; z-index: 15;">
        <div class="wh-eyebrow" style="justify-content: center;">
          <span class="wh-eyebrow-star" data-layout-ignore>✦</span>
          <span class="wh-eyebrow-txt" style="font-size: 17px;">LIỆU TRÌNH TRỌN GÓI VIP</span>
          <span class="wh-eyebrow-star" data-layout-ignore>✦</span>
        </div>
        {bullion_text("s9-ttl", "6 BƯỚC TRẢI NGHIỆM TRỌN VẸN", "wh-disp-md")}
      </div>

      <div id="s9-c1" class="wh-card s9-mini" style="left: 1004px; top: 204px;">
        <video id="s9-v1a" class="clip wh-vid-fill" src="assets/slides/v_cut_cs2_c9523.mp4" data-start="0.800000" data-hf-media-start-basis="local" data-duration="5.000000" data-track-index="1" muted playsinline></video>
        <video id="s9-v1b" class="clip wh-vid-fill" src="assets/slides/v_cut_cs2_dji08.mp4" data-start="5.800000" data-hf-media-start-basis="local" data-duration="4.933333" data-track-index="2" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="s9-num" data-layout-ignore>01</div>
        <div class="wh-card-caption" style="left:18px;right:18px;bottom:16px;"><div class="wh-card-h3">CẮT TẠO KIỂU</div></div>
      </div>

      <div id="s9-c2" class="wh-card s9-mini" style="left: 1284px; top: 204px;">
        <video id="s9-v2a" class="clip wh-vid-fill" src="assets/slides/v_wash_cs1_128.mp4" data-start="2.966667" data-hf-media-start-basis="local" data-duration="3.900000" data-track-index="3" muted playsinline></video>
        <video id="s9-v2b" class="clip wh-vid-fill" src="assets/slides/v_wash_cs1_c6664.mp4" data-start="6.866667" data-hf-media-start-basis="local" data-duration="3.866666" data-track-index="4" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="s9-num" data-layout-ignore>02</div>
        <div class="wh-card-caption" style="left:18px;right:18px;bottom:16px;"><div class="wh-card-h3">GỘI DƯỠNG SINH</div></div>
      </div>

      <div id="s9-c3" class="wh-card s9-mini" style="left: 1564px; top: 204px;">
        <video id="s9-v3a" class="clip wh-vid-fill" src="assets/slides/v_face_cs1_rm94.mp4" data-start="4.133333" data-hf-media-start-basis="local" data-duration="3.300000" data-track-index="5" muted playsinline></video>
        <video id="s9-v3b" class="clip wh-vid-fill" src="assets/slides/v_wash_cs2_3730.mp4" data-start="7.433333" data-hf-media-start-basis="local" data-duration="3.300000" data-track-index="6" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="s9-num" data-layout-ignore>03</div>
        <div class="wh-card-caption" style="left:18px;right:18px;bottom:16px;"><div class="wh-card-h3">CHĂM SÓC DA MẶT</div></div>
      </div>

      <div id="s9-c4" class="wh-card s9-mini" style="left: 1004px; top: 544px;">
        <video id="s9-v4" class="clip wh-vid-fill" src="assets/slides/v_s9_nail.mp4" data-start="5.133333" data-hf-media-start-basis="local" data-duration="5.600000" data-track-index="7" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="s9-num" data-layout-ignore>04</div>
        <div class="wh-card-caption" style="left:18px;right:18px;bottom:16px;"><div class="wh-card-h3">MÓNG TAY CHÂN</div></div>
      </div>

      <div id="s9-c5" class="wh-card s9-mini" style="left: 1284px; top: 544px;">
        <video id="s9-v5" class="clip wh-vid-fill" src="assets/slides/v_ear_cs1_105.mp4" data-start="6.833333" data-hf-media-start-basis="local" data-duration="3.900000" data-track-index="8" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="s9-num" data-layout-ignore>05</div>
        <div class="wh-card-caption" style="left:18px;right:18px;bottom:16px;"><div class="wh-card-h3">RÁY TAI ÊM DỊU</div></div>
      </div>

      <div id="s9-c6" class="wh-card s9-mini" style="left: 1564px; top: 544px;">
        <video id="s9-v6" class="clip wh-vid-fill" src="assets/slides/v_msg_td_dji26.mp4" data-start="8.200000" data-hf-media-start-basis="local" data-duration="2.533333" data-track-index="9" muted playsinline></video>
        <div class="wh-card-shade"></div>
        <div class="s9-num" data-layout-ignore>06</div>
        <div class="wh-card-caption" style="left:18px;right:18px;bottom:16px;"><div class="wh-card-h3">MASSAGE VAI GÁY</div></div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set(["#s9-c1", "#s9-c2", "#s9-c3", "#s9-c4", "#s9-c5", "#s9-c6"], {{ opacity: 0 }});
    tl.fromTo("#s9-shade", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.50, ease: "sine.out" }}, 0.0);
    tl.fromTo("#s9-hdr", {{ opacity: 0, x: 35 }}, {{ opacity: 1, x: 0, duration: 0.36, ease: "power3.out" }}, 0.08);
    tl.fromTo("#s9-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 0.90, ease: "power2.inOut" }}, 0.25);

    const pops = [
      ["#s9-c1", 0.95],
      ["#s9-c2", 3.12],
      ["#s9-c3", 4.30],
      ["#s9-c4", 5.28],
      ["#s9-c5", 7.00],
      ["#s9-c6", 8.35],
    ];
    pops.forEach(([sel, t]) => {{
      tl.fromTo(sel, {{ opacity: 0, scale: 0.94, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.36, ease: "power3.out" }}, t);
    }});

    tl.to(["#s9-hdr", "#s9-c1", "#s9-c2", "#s9-c3", "#s9-c4", "#s9-c5", "#s9-c6"], {{ opacity: 0, x: 24, duration: 0.45, ease: "sine.inOut" }}, 9.95);
    tl.to("#s9-shade", {{ opacity: 0, duration: 0.72, ease: "sine.inOut" }}, 9.98);
    window.__timelines["slide-09"] = tl;
  </script>
</template>
""")

    # =========================================================================
    # SLIDE 10 (frames 8337..9227 | 277.900000s, dur = 29.666667s)
    # Warm Cinema TVC Offer Lockups (100% Vietnamese, Bold Numbers, Soft Glow)
    # =========================================================================
    d10 = "29.666667"
    write_comp("slide-10.html", f"""<template>
  <style>{SHARED_LUXURY_CSS}
    .wh-obsidian-offer {{
      background: radial-gradient(ellipse at 50% 25%, rgba(88, 56, 28, 0.85) 0%, rgba(24, 17, 13, 0.97) 75%);
      border: 1.5px solid rgba(243, 214, 156, 0.52);
      box-shadow: 0 32px 84px rgba(0,0,0,0.88);
    }}
    .wh-center-medallion {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: 790px;
      margin-left: -395px;
      margin-top: -196px;
      padding: 34px 48px;
      border-radius: 22px;
      background: radial-gradient(ellipse at 50% 25%, rgba(86, 54, 26, 0.96) 0%, rgba(20, 14, 10, 0.98) 80%);
      border: 2px solid rgba(243, 214, 156, 0.68);
      box-shadow: 0 36px 90px rgba(0,0,0,0.92);
      text-align: center;
      z-index: 25;
    }}
  </style>
  <div id="root" data-composition-id="slide-10" data-width="1920" data-height="1080">
    <div id="s10-stage" class="wh-stage">
      <div class="wh-bg-obsidian"></div>
      <div class="wh-bg-beams" data-layout-ignore></div>
      <video id="s10-bk1" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="0" data-duration="15.000000" data-track-index="0" muted playsinline data-layout-ignore></video>
      <video id="s10-bk2" class="clip wh-bokeh-vid" src="assets/overlays/golden_dust_16x9.mp4" data-start="15.000000" data-hf-media-start-basis="local" data-duration="14.666667" data-track-index="21" muted playsinline data-layout-ignore></video>

      <!-- ================= BEAT 1 (0.00s - 6.60s): KHUNG GIỜ VÀNG -20% ================= -->
      <div id="s10-b1" style="position: absolute; inset: 0;">
        {lux_header("s10-b1", "ƯU ĐÃI TRONG TUẦN · ĐI SỚM GIÁ TỐT", "ĐẶC QUYỀN KHUNG GIỜ VÀNG", "wh-disp-lg")}

        <div id="s10-b1-hero" class="wh-card" style="left: 104px; top: 202px; width: 996px; height: 668px;">
          <video id="s10-b1-v1" class="clip wh-vid-fill" src="assets/slides/h_cs2_gold_32.mp4" data-start="0" data-duration="3.300000" data-track-index="2" muted playsinline></video>
          <video id="s10-b1-v2" class="clip wh-vid-fill" src="assets/slides/h_cs2_gold_38.mp4" data-start="3.300000" data-hf-media-start-basis="local" data-duration="3.300000" data-track-index="3" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div id="s10-b1-sh" class="wh-card-sheen" data-layout-ignore></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3">TRẢI NGHIỆM 5 SAO TRONG TUẦN</div>
            <div class="wh-card-p">Thảnh thơi tận hưởng dịch vụ cao cấp không cần chờ đợi</div>
          </div>
        </div>

        <div id="s10-b1-offer" class="wh-card wh-obsidian-offer" style="left: 1130px; top: 202px; width: 686px; height: 668px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 40px;">
          <img src="assets/images/winhair_logo_2color_pad.png" alt="Win Hair" style="height: 84px; width: auto; margin-bottom: 16px;" />
          <div style="font-family: 'Be Vietnam Pro', sans-serif; font-weight: 700; font-size: 21px; letter-spacing: 0.14em; color: var(--champagne); margin-bottom: 6px;">ƯU ĐÃI GIẢM NGAY</div>
          {bullion_text("s10-20pct", "-20%", "wh-disp-mega", "wh-gold-price")}
          <div style="width: 84px; height: 3px; border-radius: 2px; background: #D93840; margin: 18px 0;" data-layout-ignore></div>
          <div style="font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 38px; letter-spacing: 0.05em; color: var(--ivory);">GIỜ VÀNG · TỪ THỨ 2 – THỨ 5</div>
          <div style="margin-top: 10px; font-family: 'Be Vietnam Pro', sans-serif; font-weight: 600; font-size: 22px; color: var(--warm-gray);">Áp dụng khung giờ vàng từ Thứ 2 đến Thứ 5 hàng tuần</div>
        </div>
      </div>

      <!-- ================= BEAT 2 (6.60s - 13.233333s): COMBO 4 BƯỚC 129K ================= -->
      <div id="s10-b2" style="position: absolute; inset: 0; opacity: 0;">
        <div id="s10-q1" class="wh-card" style="left: 96px; top: 68px; width: 848px; height: 424px;" data-layout-allow-overlap>
          <video id="s10-qv1a" class="clip wh-vid-fill" src="assets/slides/v_cut_cs1_c6627.mp4" data-start="6.600000" data-hf-media-start-basis="local" data-duration="3.333333" data-track-index="4" muted playsinline></video>
          <video id="s10-qv1b" class="clip wh-vid-fill" src="assets/slides/v_cut_cs2_extra.mp4" data-start="9.933333" data-hf-media-start-basis="local" data-duration="3.300000" data-track-index="5" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><div class="wh-card-h3">01 · CẮT TẠO KIỂU</div></div>
        </div>

        <div id="s10-q2" class="wh-card" style="left: 976px; top: 68px; width: 848px; height: 424px;" data-layout-allow-overlap>
          <video id="s10-qv2a" class="clip wh-vid-fill" src="assets/slides/v_shave_macro.mp4" data-start="6.600000" data-hf-media-start-basis="local" data-duration="3.333333" data-track-index="6" muted playsinline></video>
          <video id="s10-qv2b" class="clip wh-vid-fill" src="assets/slides/v_shave_bed.mp4" data-start="9.933333" data-hf-media-start-basis="local" data-duration="3.300000" data-track-index="7" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption" style="text-align: right;"><div class="wh-card-h3">02 · CẠO MẶT ÊM ÁI</div></div>
        </div>

        <div id="s10-q3" class="wh-card" style="left: 96px; top: 516px; width: 848px; height: 424px;" data-layout-allow-overlap>
          <video id="s10-qv3a" class="clip wh-vid-fill" src="assets/slides/v_ear_light.mp4" data-start="6.600000" data-hf-media-start-basis="local" data-duration="3.333333" data-track-index="8" muted playsinline></video>
          <video id="s10-qv3b" class="clip wh-vid-fill" src="assets/slides/h_ear_main.mp4" data-start="9.933333" data-hf-media-start-basis="local" data-duration="3.300000" data-track-index="9" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption"><div class="wh-card-h3">03 · RÁY TAI THƯ GIÃN</div></div>
        </div>

        <div id="s10-q4" class="wh-card" style="left: 976px; top: 516px; width: 848px; height: 424px;" data-layout-allow-overlap>
          <video id="s10-qv4a" class="clip wh-vid-fill" src="assets/slides/v_wash_cs2_c9699.mp4" data-start="6.600000" data-hf-media-start-basis="local" data-duration="3.333333" data-track-index="10" muted playsinline></video>
          <video id="s10-qv4b" class="clip wh-vid-fill" src="assets/slides/h_cs2_vip_hosp.mp4" data-start="9.933333" data-hf-media-start-basis="local" data-duration="3.300000" data-track-index="11" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption" style="text-align: right;"><div class="wh-card-h3">04 · XẢ TÓC SẢNG KHOÁI</div></div>
        </div>

        <div id="s10-129-card" class="wh-center-medallion" data-layout-allow-overlap>
          <div style="font-family: 'Be Vietnam Pro', sans-serif; font-weight: 700; font-size: 19px; letter-spacing: 0.16em; color: var(--champagne); margin-bottom: 6px;">COMBO ĐẶC QUYỀN PHÁI MẠNH</div>
          <div style="font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 36px; color: var(--ivory); letter-spacing: 0.08em; margin-bottom: 4px;">
            CẮT · CẠO · RÁY · XẢ
          </div>
          {bullion_text("s10-129-num", "129K", "wh-disp-mega", "wh-gold-price")}
          <div style="margin-top: 8px; font-family: 'Be Vietnam Pro', sans-serif; font-weight: 600; font-size: 22px; color: var(--warm-gray);">
            Trọn gói 4 bước chỉn chu phong độ
          </div>
        </div>
      </div>

      <!-- ================= BEAT 3 (13.233333s - 24.30s): COMBO NGỦ TRƯA 79K ================= -->
      <div id="s10-b3" style="position: absolute; inset: 0; opacity: 0;">
        {lux_header("s10-b3", "KHOẢNG NGHỈ TRƯA ÊM ÁI", "30 PHÚT THƯ GIÃN · TÁI TẠO NĂNG LƯỢNG", "wh-disp-lg")}

        <div id="s10-b3-left" class="wh-card" style="left: 104px; top: 202px; width: 796px; height: 668px;">
          <video id="s10-b3-vh1" class="clip wh-vid-fill" src="assets/slides/h_lunch_nap.mp4" data-start="13.233333" data-hf-media-start-basis="local" data-duration="5.200000" data-track-index="12" muted playsinline></video>
          <video id="s10-b3-vh2" class="clip wh-vid-fill" src="assets/slides/h_cs2_relax_bed2.mp4" data-start="18.433333" data-hf-media-start-basis="local" data-duration="5.866667" data-track-index="13" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div id="s10-b3-sh1" class="wh-card-sheen" data-layout-ignore></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3">NGHỈ NGƠI ÊM ÁI GIỮA NGÀY</div>
            <div class="wh-card-p">Thả lỏng chợp mắt thư thái · Buổi chiều tỉnh táo sảng khoái</div>
          </div>
        </div>

        <div id="s10-b3-mid" class="wh-card" style="left: 924px; top: 202px; width: 382px; height: 668px;">
          <video id="s10-b3-vv1" class="clip wh-vid-fill" src="assets/slides/v_msg_chill.mp4" data-start="13.433333" data-hf-media-start-basis="local" data-duration="5.433333" data-track-index="14" muted playsinline></video>
          <video id="s10-b3-vv2" class="clip wh-vid-fill" src="assets/slides/v_msg_td_66.mp4" data-start="18.866666" data-hf-media-start-basis="local" data-duration="5.433334" data-track-index="15" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div id="s10-b3-sh2" class="wh-card-sheen" data-layout-ignore></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3">GỘI ĐẦU &amp; MASSAGE MẶT</div>
          </div>
        </div>

        <div id="s10-b3-price" class="wh-card wh-obsidian-offer" style="left: 1330px; top: 202px; width: 486px; height: 668px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 34px;">
          <img src="assets/images/winhair_logo_2color_pad_b3.png" alt="WH" style="height: 68px; width: auto; margin-bottom: 14px;" />
          <div style="font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 38px; color: var(--ivory); letter-spacing: 0.05em;">COMBO NGỦ TRƯA</div>
          <div style="margin: 6px 0;">
            {bullion_text("s10-79k", "79K", "wh-disp-mega", "wh-gold-price")}
          </div>
          <div style="width: 72px; height: 3px; border-radius: 2px; background: #D93840; margin: 14px 0;" data-layout-ignore></div>
          <div style="font-family: 'Be Vietnam Pro', sans-serif; font-weight: 600; font-size: 22px; color: var(--warm-gray); line-height: 1.45;">
            30 phút nghỉ ngơi thư thái<br/>Gội đầu mát lạnh &amp; Massage mặt
          </div>
        </div>
      </div>

      <!-- ================= BEAT 4 (24.30s - 29.666667s): 2 CƠ SỞ NHA TRANG ================= -->
      <div id="s10-b4" style="position: absolute; inset: 0; opacity: 0;">
        {lux_header("s10-b4", "HỆ THỐNG WIN HAIR SALON NHA TRANG", "HAI ĐIỂM ĐẾN · MỘT CHUẨN MỰC 5 SAO", "wh-disp-lg")}

        <div id="s10-cs1" class="wh-card" style="left: 104px; top: 202px; width: 842px; height: 668px;">
          <video id="s10-cs1-v1" class="clip wh-vid-fill" src="assets/slides/h_cs1_front_c0120.mp4" data-start="24.300000" data-hf-media-start-basis="local" data-duration="2.700000" data-track-index="16" muted playsinline></video>
          <video id="s10-cs1-v2" class="clip wh-vid-fill" src="assets/slides/h_cs1_front_c0057.mp4" data-start="27.000000" data-hf-media-start-basis="local" data-duration="2.666667" data-track-index="17" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3" style="font-size: 44px; color: #FFF3D1;">CƠ SỞ 1 · 41 LÝ TỰ TRỌNG</div>
            <div class="wh-card-p" style="font-size: 22px;">Trung tâm thành phố Nha Trang · Thuận tiện di chuyển</div>
          </div>
        </div>

        <div id="s10-cs2" class="wh-card" style="left: 974px; top: 202px; width: 842px; height: 668px;">
          <video id="s10-cs2-v1" class="clip wh-vid-fill" src="assets/slides/h_cs2_front_fly37.mp4" data-start="24.300000" data-hf-media-start-basis="local" data-duration="2.666667" data-track-index="18" muted playsinline></video>
          <video id="s10-cs2-v2" class="clip wh-vid-fill" src="assets/slides/h_cs2_front_fly46.mp4" data-start="26.966667" data-hf-media-start-basis="local" data-duration="2.700000" data-track-index="19" muted playsinline></video>
          <div class="wh-card-shade"></div>
          <div class="wh-card-caption">
            <div class="wh-card-h3" style="font-size: 44px; color: #FFF3D1;">CƠ SỞ 2 · 59 THÍCH QUẢNG ĐỨC</div>
            <div class="wh-card-p" style="font-size: 22px;">Quy mô lớn 2 tầng VIP · Không gian đẳng cấp 5 sao</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    gsap.set(["#s10-b2", "#s10-b3", "#s10-b4"], {{ opacity: 0 }});

    // Beat 1: Golden Hour -20%
    tl.fromTo("#s10-b1-hdr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 0.04);
    tl.fromTo("#s10-b1-hero", {{ opacity: 0, x: -70 }}, {{ opacity: 1, x: 0, duration: 0.48, ease: "power3.out" }}, 0.10);
    tl.fromTo("#s10-b1-v1", {{ scale: 1.0 }}, {{ scale: 1.04, duration: 3.25, ease: "none" }}, 0.05);
    tl.fromTo("#s10-b1-v2", {{ scale: 1.0 }}, {{ scale: 1.04, duration: 3.25, ease: "none" }}, 3.30);
    tl.fromTo("#s10-b1-sh", {{ xPercent: -120, opacity: 0.8 }}, {{ xPercent: 140, opacity: 0, duration: 0.75, ease: "power2.out" }}, 0.45);
    tl.fromTo("#s10-b1-sh", {{ xPercent: -120, opacity: 0.75 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out", immediateRender: false }}, 3.30);
    tl.fromTo("#s10-b1-offer", {{ opacity: 0, scale: 0.96, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.48, ease: "power3.out" }}, 0.24);
    tl.fromTo("#s10-20pct-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.05, ease: "power2.inOut" }}, 4.05);
    tl.to("#s10-b1", {{ opacity: 0, duration: 0.18 }}, 6.42);

    // Beat 2: 129K
    tl.fromTo("#s10-b2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.16 }}, 6.60);
    tl.fromTo("#s10-q1", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 7.35);
    tl.fromTo("#s10-q2", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 7.72);
    tl.fromTo("#s10-q3", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 8.25);
    tl.fromTo("#s10-q4", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.34, ease: "power3.out" }}, 8.58);

    tl.fromTo("#s10-129-card", {{ opacity: 0, scale: 0.96, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.46, ease: "power3.out" }}, 9.15);
    tl.fromTo("#s10-129-num-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 10.75);
    tl.to("#s10-b2", {{ opacity: 0, duration: 0.18, immediateRender: false }}, 13.05);

    // Beat 3: 79K
    tl.fromTo("#s10-b3", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.16 }}, 13.23);
    tl.fromTo("#s10-b3-left", {{ opacity: 0, x: -65 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 13.30);
    tl.fromTo("#s10-b3-mid", {{ opacity: 0, y: 55 }}, {{ opacity: 1, y: 0, duration: 0.46, ease: "power3.out" }}, 13.48);
    tl.fromTo("#s10-b3-sh1", {{ xPercent: -120, opacity: 0.72 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 18.42);
    tl.fromTo("#s10-b3-sh2", {{ xPercent: -120, opacity: 0.72 }}, {{ xPercent: 140, opacity: 0, duration: 0.65, ease: "power2.out" }}, 18.85);
    tl.fromTo("#s10-b3-price", {{ opacity: 0, scale: 0.96, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.48, ease: "power3.out" }}, 13.68);
    tl.fromTo("#s10-79k-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 19.30);
    tl.to("#s10-b3", {{ opacity: 0, duration: 0.18, immediateRender: false }}, 24.12);

    // Beat 4: Two Frontal Locations
    tl.fromTo("#s10-b4", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.16 }}, 24.30);
    tl.fromTo("#s10-cs1", {{ opacity: 0, x: -75 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 24.36);
    tl.fromTo("#s10-cs2", {{ opacity: 0, x: 75 }}, {{ opacity: 1, x: 0, duration: 0.46, ease: "power3.out" }}, 24.52);
    tl.fromTo("#s10-b4-ttl-sheen", {{ backgroundPosition: "-130% 0, 0 0" }}, {{ backgroundPosition: "210% 0, 0 0", duration: 1.0, ease: "power2.inOut" }}, 24.90);

    window.__timelines["slide-10"] = tl;
  </script>
</template>
""")
