const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");

const PROJ = "C:\\AI\\full studio\\projects\\feelchicken_pinterest_brave_v4";
const ASSETS = path.join(PROJ, "assets");
const OUT = path.join(PROJ, "out_v4");
const FONT_DIR = "C:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\fonts_tvc_vi";

fs.mkdirSync(OUT, { recursive: true });

function uri(dir, fn) {
  const p = path.join(dir, fn);
  const buf = fs.readFileSync(p);
  const ext = path.extname(p).toLowerCase();
  const mime = ext === ".ttf" ? "font/ttf" : ext === ".png" ? "image/png" : "image/jpeg";
  return `data:${mime};base64,${buf.toString("base64")}`;
}

const FONT_CSS = `
@font-face { font-family: 'BigShoulders'; src: url('${uri(FONT_DIR, "BigShouldersDisplay-Black.ttf")}') format('truetype'); font-weight: 900; }
@font-face { font-family: 'BarlowCond'; src: url('${uri(FONT_DIR, "BarlowCondensed-BlackItalic.ttf")}') format('truetype'); font-weight: 900; font-style: italic; }
@font-face { font-family: 'BarlowCond'; src: url('${uri(FONT_DIR, "BarlowCondensed-Black.ttf")}') format('truetype'); font-weight: 900; font-style: normal; }
@font-face { font-family: 'Anton'; src: url('${uri(FONT_DIR, "Anton-Regular.ttf")}') format('truetype'); font-weight: 400; }
@font-face { font-family: 'Fraunces'; src: url('${uri(FONT_DIR, "Fraunces-Black.ttf")}') format('truetype'); font-weight: 900; }
@font-face { font-family: 'Jakarta'; src: url('${uri(FONT_DIR, "PlusJakartaSans-ExtraBold.ttf")}') format('truetype'); font-weight: 800; }
@font-face { font-family: 'Jakarta'; src: url('${uri(FONT_DIR, "PlusJakartaSans-Bold.ttf")}') format('truetype'); font-weight: 700; }
@font-face { font-family: 'BeVN'; src: url('${uri(FONT_DIR, "BeVietnamPro-ExtraBold.ttf")}') format('truetype'); font-weight: 800; }
@font-face { font-family: 'BeVN'; src: url('${uri(FONT_DIR, "BeVietnamPro-SemiBold.ttf")}') format('truetype'); font-weight: 600; }
@font-face { font-family: 'BeVN'; src: url('${uri(FONT_DIR, "BeVietnamPro-Medium.ttf")}') format('truetype'); font-weight: 500; }
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }
.grid-paper {
  background-color: #faf5eb;
  background-image:
    linear-gradient(to right, rgba(168, 28, 22, 0.065) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(168, 28, 22, 0.065) 1px, transparent 1px);
  background-size: 36px 36px;
}
.checker-strip {
  height: 12px;
  background-image: conic-gradient(#faf3e6 90deg, #a81715 90deg 180deg, #faf3e6 180deg 270deg, #a81715 270deg);
  background-size: 24px 24px;
}
`;

function buildPages() {
  const LOGO = uri(ASSETS, "logo.png");
  const PH_MICAY_29 = uri(ASSETS, "real_micay_chopstick_29.jpg");
  const PH_DIP_14   = uri(ASSETS, "real_feast_dip_14.jpg");
  const PH_GRP_13   = uri(ASSETS, "real_feast_group_13.jpg");
  const PH_MC_08    = uri(ASSETS, "real_micay_hands_08.jpg");
  const PH_JJ_26    = uri(ASSETS, "real_jjajang_pull_26.jpg");
  const PH_SPAG     = uri(ASSETS, "real_spaghetti_09061.jpg");

  const CUT_MC17    = uri(ASSETS, "cut_micay_haisan_17.png");
  const CUT_MCDG    = uri(ASSETS, "cut_micay_duiga_real.png");
  const CUT_DUI     = uri(ASSETS, "cut_dui_ga_sot_cay.png");
  const CUT_COCA    = uri(ASSETS, "cut_coca_can.png");
  const CUT_AK      = uri(ASSETS, "cut_anh_khang_clean.png");
  const CUT_GA08995 = uri(ASSETS, "cut_ga_5_vi_08995.png");
  const CUT_GA21    = uri(ASSETS, "cut_ga_5_vi_21.png");
  const CUT_JJ      = uri(ASSETS, "cut_mi_tuong_den.png");

  const S1 = uri(ASSETS, "sauce_1_phomai.jpg");
  const S2 = uri(ASSETS, "sauce_2_cayhan.jpg");
  const S3 = uri(ASSETS, "sauce_3_toicay.jpg");
  const S4 = uri(ASSETS, "sauce_4_chanhday.jpg");
  const S5 = uri(ASSETS, "sauce_5_tuonghan.jpg");

  // Barcode SVG for BHC Receipt Ticket
  const bars = [3,1,2,4,1,2,1,3,2,1,4,2,1,2,3,1,2,1,3,4,1,2,2,1,3,1,2,4,1,2,1,3];
  let bx = 0;
  const barcodeSvg = `<svg viewBox="0 0 210 38" width="210" height="38">${bars
    .map((w, i) => {
      const rx = bx;
      bx += w * 3.1;
      return i % 2 === 0 ? `<rect x="${rx.toFixed(1)}" y="0" width="${(w * 2.4).toFixed(1)}" height="38" fill="#181312"/>` : "";
    })
    .join("")}</svg>`;

  return [
    // =========================================================================
    // POST 1 — 261122 - Mì Cay Ngày Mưa (4 Hình — 100% Real Sony A1 + Brave Pins)
    // =========================================================================
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "01 - Mì Cay Hàn Quốc 55K.png",
      w: 1080,
      h: 720,
      // Ref: 오늘밤 치킨 한 판 Checkered Red Poster + ZHENGDA 53.000 VNĐ Split Action
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 1080px; height: 720px; display: flex; position: relative; overflow: hidden; font-family: 'BeVN', sans-serif; background: #a81715; }
        .left { width: 495px; height: 100%; background: #a81715; position: relative; display: flex; flex-direction: column; justify-content: space-between; border-right: 4px solid #faf3e6;
          background-image: radial-gradient(circle at 20% 25%, rgba(255,200,120,0.12), transparent 60%), linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px);
          background-size: 100% 100%, 32px 32px, 32px 32px;
        }
        .inner-pad { padding: 28px 38px 24px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .top-brand { display: flex; align-items: center; justify-content: space-between; }
        .top-brand img { height: 56px; }
        .kr-tag { font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #faf3e6; border: 1.5px solid rgba(250,243,230,0.55); padding: 5px 12px; border-radius: 99px; }
        .tilt-tag { display: inline-block; align-self: flex-start; background: #181211; color: #f6ca56; font-size: 12.5px; font-weight: 800; letter-spacing: 0.08em; padding: 6px 15px; transform: rotate(-2deg); margin-bottom: 18px; box-shadow: 3px 3px 0 rgba(0,0,0,0.28); }
        .h1 { font-family: 'BigShoulders', sans-serif; font-weight: 900; font-size: 98px; line-height: 0.98; color: #faf3e6; text-transform: uppercase; letter-spacing: -0.01em; }
        .h1 span { display: block; color: #f6ca56; margin-top: 8px; }
        .sub { margin-top: 16px; font-size: 14.5px; line-height: 1.52; color: rgba(250,243,230,0.92); font-weight: 500; }
        .price-card { margin-top: 18px; background: #faf3e6; color: #181211; border: 2.5px solid #181211; box-shadow: 5px 5px 0 #181211; border-radius: 12px; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; }
        .pc-l small { display: block; font-size: 10.5px; font-weight: 800; letter-spacing: 0.1em; color: #a81715; text-transform: uppercase; }
        .pc-l b { font-family: 'BigShoulders', sans-serif; font-size: 46px; line-height: 0.95; color: #a81715; }
        .pc-r { text-align: right; font-size: 12.5px; font-weight: 800; color: #181211; line-height: 1.4; }
        .addr { font-size: 11.8px; font-weight: 600; color: rgba(250,243,230,0.92); padding-top: 12px; border-top: 1px dashed rgba(250,243,230,0.35); line-height: 1.45; }
        .right { flex: 1; position: relative; overflow: hidden; }
        .right img { width: 100%; height: 100%; object-fit: cover; object-position: center 48%; }
        .seal { position: absolute; left: 495px; top: 50%; transform: translate(-50%, -50%) rotate(-8deg); width: 112px; height: 112px; border-radius: 50%; background: #f6ca56; border: 3px solid #181211; box-shadow: 4px 4px 0 #181211; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; z-index: 10; padding: 8px; }
        .seal b { font-family: 'BigShoulders', sans-serif; font-size: 26px; line-height: 0.95; color: #181211; }
        .seal span { font-size: 10px; font-weight: 800; color: #a81715; margin-top: 3px; text-transform: uppercase; }
      </style></head><body>
        <div class="left">
          <div class="checker-strip"></div>
          <div class="inner-pad">
            <div class="top-brand"><img src="${LOGO}"><span class="kr-tag">얼큰 짬뽕 • 7 LEVEL</span></div>
            <div>
              <div class="tilt-tag">🌧️ MƯA LẠNH NHA TRANG • XÌ XỤP NGAY</div>
              <div class="h1">MÌ CAY<span>HÀN QUỐC</span></div>
              <div class="sub">Hải Sản • Bạch Tuộc • Đùi Gà Sốt Hàn.<br>Nước dùng kim chi nấu mới nóng hổi bốc khói.</div>
              <div class="price-card">
                <div class="pc-l"><small>ĐỒNG GIÁ CHỈ</small><b>55.000 VNĐ</b></div>
                <div class="pc-r">Đủ Cấp 1 → Cấp 7<br><span style="color:#a81715">Ship Nóng 15 Phút</span></div>
              </div>
            </div>
            <div class="addr">CS1: 38 Nguyễn Đình Chiểu • CS2: 35 Trần Hữu Duyệt<br>Mở cửa: 10:00 – 22:00  |  Hotline: <b style="color:#f6ca56">0796 601 106</b></div>
          </div>
          <div class="checker-strip"></div>
        </div>
        <div class="right"><img src="${PH_MICAY_29}"></div>
        <div class="seal"><b>NÓNG<br>HỔI!</b><span>THỐ GIỮ NHIỆT</span></div>
      </body></html>`,
    },
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "02 - Mì Cay Hải Sản Bạch Tuộc.png",
      w: 800,
      h: 800,
      // Ref: SAN CHICKEN Grid Paper + Giant Wall-to-Wall Text BEHIND Real Cutout Bowl!
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; font-family: 'BeVN', sans-serif; padding: 22px; }
        .frame { width: 100%; height: 100%; border: 2.5px solid #a81715; border-radius: 14px; position: relative; overflow: hidden; }
        .top-pill { position: absolute; top: 18px; left: 50%; transform: translateX(-50%); border: 2px solid #181211; background: #ffffff; padding: 5px 18px; border-radius: 99px; font-size: 11.5px; font-weight: 800; letter-spacing: 0.12em; color: #181211; z-index: 5; white-space: nowrap; }
        .giant-back { position: absolute; top: 68px; left: 0; right: 0; text-align: center; font-family: 'BigShoulders', sans-serif; font-weight: 900; font-size: 142px; line-height: 1.02; letter-spacing: -0.01em; color: #a81715; text-transform: uppercase; z-index: 1; user-select: none; }
        .giant-back span { display: block; color: #181211; font-size: 128px; margin-top: 4px; }
        .bowl-wrap { position: absolute; left: 50%; top: 304px; transform: translateX(-50%); width: 414px; height: 414px; z-index: 3; filter: drop-shadow(0 24px 28px rgba(24,14,10,0.38)); }
        .bowl-wrap img { width: 100%; height: 100%; object-fit: contain; }
        .call-tag { position: absolute; z-index: 6; background: #ffffff; border: 2px solid #181211; box-shadow: 3px 3px 0 #181211; border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 800; color: #181211; }
        .call-tag b { color: #a81715; }
        .c1 { left: 26px; top: 365px; transform: rotate(-3deg); }
        .c2 { right: 24px; top: 345px; transform: rotate(3deg); }
        .c3 { left: 32px; bottom: 84px; }
        .price-stamp { position: absolute; right: 28px; bottom: 72px; z-index: 6; background: #a81715; color: #faf3e6; border: 2.5px solid #181211; box-shadow: 4px 4px 0 #181211; border-radius: 12px; padding: 10px 18px; transform: rotate(-3deg); text-align: center; }
        .price-stamp small { display: block; font-size: 10px; font-weight: 800; letter-spacing: 0.1em; color: #f6ca56; }
        .price-stamp b { font-family: 'BigShoulders', sans-serif; font-size: 40px; line-height: 0.95; }
        .ftr { position: absolute; bottom: 0; left: 0; right: 0; height: 44px; background: #181211; color: #faf3e6; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; font-size: 12px; font-weight: 600; z-index: 6; }
        .ftr img { height: 28px; }
      </style></head><body class="grid-paper">
        <div class="frame">
          <div class="top-pill">FEEL CHICKEN  •  해물 문어 짬뽕</div>
          <div class="giant-back">MÌ CAY<span>HẢI SẢN</span></div>
          <div class="bowl-wrap"><img src="${CUT_MC17}"></div>
          <div class="call-tag c1">🦐 <b>Tôm Tươi</b> Ngọt Thịt</div>
          <div class="call-tag c2">🐙 <b>Bạch Tuộc</b> & Chả Cá</div>
          <div class="call-tag c3">🌶️ Súp Kim Chi Hàn Quốc</div>
          <div class="price-stamp"><small>ĐỒNG GIÁ</small><b>55.000Đ</b></div>
          <div class="ftr"><img src="${LOGO}"><span>38 Nguyễn Đình Chiểu • 35 Trần Hữu Duyệt | <b style="color:#f6ca56">0796 601 106</b></span></div>
        </div>
      </body></html>`,
    },
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "03 - Mì Cay Đùi Gà 7 Cấp Độ.png",
      w: 800,
      h: 800,
      // Ref: WANT SAVORY? TRY JJAPAGETTI! + HOT SPICE Diagonal Crimson/Black Split!
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #141110; font-family: 'BeVN', sans-serif; color: #faf3e6; }
        .diag-red { position: absolute; left: -100px; top: -120px; width: 1050px; height: 540px; background: #ad1917; transform: rotate(-12deg); border-bottom: 5px solid #f6ca56; z-index: 1; }
        .tl { position: absolute; top: 34px; left: 40px; z-index: 5; }
        .kicker { display: inline-block; background: #141110; color: #f6ca56; font-size: 11.5px; font-weight: 800; letter-spacing: 0.12em; padding: 5px 13px; margin-bottom: 8px; }
        .h1 { font-family: 'BarlowCond', sans-serif; font-weight: 900; font-style: italic; font-size: 76px; line-height: 0.9; text-transform: uppercase; color: #faf3e6; }
        .h1 span { color: #f6ca56; }
        .tr-logo { position: absolute; top: 32px; right: 38px; height: 54px; z-index: 5; }
        .bowl-center { position: absolute; left: 44px; bottom: 58px; width: 430px; height: 530px; z-index: 4; filter: drop-shadow(0 22px 26px rgba(0,0,0,0.65)); display: flex; align-items: center; justify-content: center; }
        .bowl-center img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .spice-panel { position: absolute; right: 36px; bottom: 68px; width: 268px; z-index: 5; background: #1e1917; border: 2px solid rgba(246,202,86,0.55); border-radius: 14px; padding: 16px 18px; }
        .sp-hd { font-family: 'BigShoulders', sans-serif; font-size: 28px; color: #f6ca56; letter-spacing: 0.03em; border-bottom: 1px solid rgba(255,255,255,0.14); padding-bottom: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: baseline; }
        .sp-hd small { font-family: 'BeVN', sans-serif; font-size: 12px; font-weight: 800; color: #faf3e6; }
        .lv-row { display: flex; align-items: center; justify-content: space-between; padding: 5.5px 0; font-size: 12px; font-weight: 600; border-bottom: 1px dashed rgba(255,255,255,0.08); }
        .lv-row:last-child { border-bottom: none; }
        .dots { display: flex; gap: 3px; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.14); }
        .dot.on { background: #ef4129; }
        .dot.w { background: #f6ca56; }
        .ftr { position: absolute; bottom: 18px; left: 40px; right: 36px; display: flex; justify-content: space-between; font-size: 12px; color: rgba(250,243,230,0.8); z-index: 5; }
      </style></head><body>
        <div class="diag-red"></div>
        <img class="tr-logo" src="${LOGO}">
        <div class="tl">
          <div class="kicker">BẠN CHỊU ĐƯỢC CẤP MẤY?</div>
          <div class="h1">MÌ CAY ĐÙI GÀ<br><span>ĐỦ 7 CẤP ĐỘ!</span></div>
        </div>
        <div class="bowl-center"><img src="${CUT_MCDG}"></div>
        <div class="spice-panel">
          <div class="sp-hd"><span>THANG CAY 1–7</span><small>55.000Đ</small></div>
          ${[
            ["Cấp 01", "The dịu", 1],
            ["Cấp 02", "Ấm nồng", 2],
            ["Cấp 03", "Cay vừa", 3],
            ["Cấp 04", "Cay xuýt xoa", 4],
            ["Cấp 05", "Cay tê lưỡi", 5],
            ["Cấp 06", "Bùng nổ", 6],
            ["Cấp 07", "Thách thức", 7],
          ]
            .map(
              ([lv, lb, n]) => `<div class="lv-row"><span><b style="color:#f6ca56">${lv}</b> • ${lb}</span><div class="dots">${[1,2,3,4,5,6,7]
                .map((k) => `<span class="dot ${k <= n ? (n <= 3 ? "w" : "on") : ""}"></span>`)
                .join("")}</div></div>`
            )
            .join("")}
        </div>
        <div class="ftr"><span>Đùi gà chiên vàng thấm súp kim chi Hàn Quốc</span><span>Hotline / Ship 15p: <b style="color:#f6ca56">0796 601 106</b></span></div>
      </body></html>`,
    },
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "04 - Combo Feel Spicy 89K.png",
      w: 800,
      h: 800,
      // Ref: EXACT CHICKEN COMBO Pin (SHEET_16_PINS_BRAVE.jpg Row 2 Col 3 — Tall Red Condensed Type + Overlapping Real Cutouts!)
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #fbf8f2; color: #b51816; font-family: 'BeVN', sans-serif; }
        .border-in { position: absolute; inset: 18px; border: 2px solid #b51816; pointer-events: none; z-index: 10; }
        .top-meta { position: absolute; top: 30px; left: 36px; right: 36px; display: flex; justify-content: space-between; align-items: center; z-index: 6; font-size: 11.5px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
        .top-meta img { height: 44px; }
        .wall-type { position: absolute; top: 82px; left: 28px; right: 28px; z-index: 1; font-family: 'BigShoulders', sans-serif; font-weight: 900; text-transform: uppercase; color: #c41917; line-height: 0.94; letter-spacing: -0.01em; text-align: center; }
        .wt-1 { font-size: 156px; display: block; }
        .wt-2 { font-size: 164px; display: block; color: #1c1412; margin-top: 2px; }
        .spec-left { position: absolute; left: 36px; top: 382px; z-index: 5; background: #ffffff; border: 2px solid #1c1412; box-shadow: 4px 4px 0 #1c1412; border-radius: 10px; padding: 10px 14px; font-size: 12px; font-weight: 800; line-height: 1.55; color: #1c1412; }
        .spec-left b { color: #c41917; }
        .coca { position: absolute; right: 64px; top: 246px; width: 162px; z-index: 2; filter: drop-shadow(0 18px 20px rgba(30,15,10,0.25)); }
        .bowl { position: absolute; left: 214px; bottom: 68px; width: 342px; z-index: 3; filter: drop-shadow(0 22px 24px rgba(30,15,10,0.32)); }
        .drum { position: absolute; right: 28px; bottom: 62px; width: 332px; z-index: 4; transform: rotate(-8deg); filter: drop-shadow(0 20px 20px rgba(30,15,10,0.34)); }
        .seal-price { position: absolute; left: 36px; bottom: 66px; width: 164px; height: 164px; border-radius: 50%; background: #c41917; color: #fbf8f2; border: 4px solid #fbf8f2; box-shadow: 0 10px 24px rgba(180,20,18,0.38); z-index: 6; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; transform: rotate(-6deg); }
        .seal-price small { font-size: 10.5px; font-weight: 800; letter-spacing: 0.08em; color: #f8cf62; }
        .seal-price b { font-family: 'BigShoulders', sans-serif; font-size: 44px; line-height: 0.95; margin-top: 3px; }
        .ftr { position: absolute; bottom: 26px; left: 38px; right: 38px; display: flex; justify-content: space-between; font-size: 11.5px; font-weight: 800; color: #1c1412; z-index: 6; }
      </style></head><body>
        <div class="border-in"></div>
        <div class="top-meta"><img src="${LOGO}"><span>BEST-SELLING RAINY DAY COMBO  •  NO CĂNG BỤNG</span></div>
        <div class="wall-type">
          <span class="wt-1">FEEL SPICY</span>
          <span class="wt-2">COMBO</span>
        </div>
        <div class="spec-left">
          <b>01</b> Nồi Mì Cay Hàn Quốc<br>
          <b>01</b> Đùi Gà Sốt Hàn Cỡ Lớn<br>
          <b>01</b> Nước Ngọt Coca-Cola
        </div>
        <img class="coca" src="${CUT_COCA}">
        <img class="bowl" src="${CUT_MC17}">
        <img class="drum" src="${CUT_DUI}">
        <div class="seal-price"><small>TRỌN BỘ CHỈ</small><b>89.000Đ</b></div>
        <div class="ftr"><span>CS1: 38 Nguyễn Đình Chiểu • CS2: 35 Trần Hữu Duyệt</span><span style="color:#c41917">SHIP NÓNG 15P: 0796 601 106</span></div>
      </body></html>`,
    },

    // =========================================================================
    // POST 2 — 261124 - Thử Thách 5 Phút 1 Triệu 5 (2 Hình — Mexicana + BHC Receipt!)
    // =========================================================================
    {
      folder: "261124 - Thử Thách 5 Phút 1 Triệu 5",
      file: "01 - Thử Thách 5 Phút Anh Khang.png",
      w: 800,
      h: 800,
      // Ref: EXACT Mexicana 고추바사삭 Pin (SHEET_16_PINS_BRAVE.jpg Row 1 Col 3 — Cream Grid + Crimson Arch + Real Model & Real Platters!)
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; font-family: 'BeVN', sans-serif; }
        .top-bar { position: absolute; top: 20px; left: 32px; right: 32px; display: flex; justify-content: space-between; align-items: center; z-index: 6; }
        .top-bar img { height: 48px; }
        .stamp { background: #181211; color: #f6ca56; font-size: 12px; font-weight: 800; letter-spacing: 0.08em; padding: 6px 15px; transform: rotate(2deg); box-shadow: 3px 3px 0 #a81715; }
        .hd-wrap { position: absolute; top: 72px; left: 24px; right: 24px; text-align: center; z-index: 5; }
        .h1 { font-family: 'BigShoulders', sans-serif; font-weight: 900; font-size: 88px; line-height: 1.02; color: #b51816; text-transform: uppercase; letter-spacing: -0.005em; }
        .sub-pill { display: inline-block; margin-top: 8px; background: #181211; color: #faf5eb; border: 2px solid #181211; padding: 6px 20px; border-radius: 99px; font-size: 14px; font-weight: 800; }
        .sub-pill b { color: #f6ca56; }
        .arch { position: absolute; left: 50%; top: 232px; transform: translateX(-50%); width: 424px; height: 430px; background: #a81715; border: 3px solid #181211; border-radius: 212px 212px 0 0; z-index: 1; box-shadow: 8px 8px 0 rgba(24,18,17,0.14); }
        .ak-host { position: absolute; left: 48%; top: 222px; transform: translateX(-50%); width: 438px; z-index: 2; filter: drop-shadow(0 12px 18px rgba(0,0,0,0.22)); }
        .wood-ledge { position: absolute; left: 0; right: 0; bottom: 0; height: 158px; background: linear-gradient(180deg, #d8a46f 0%, #b98049 100%); border-top: 3px solid #181211; z-index: 3; }
        .platter-ga { position: absolute; left: 26px; bottom: 44px; width: 390px; z-index: 4; filter: drop-shadow(0 16px 18px rgba(20,10,5,0.38)); }
        .platter-mi { position: absolute; right: 24px; bottom: 48px; width: 380px; z-index: 4; filter: drop-shadow(0 16px 18px rgba(20,10,5,0.38)); }
        .burst { position: absolute; z-index: 6; background: #ffffff; border: 2.5px solid #181211; box-shadow: 4px 4px 0 #181211; border-radius: 12px; padding: 8px 13px; font-size: 12.5px; font-weight: 800; color: #181211; line-height: 1.3; }
        .burst b { color: #b51816; display: block; font-size: 14px; }
        .b-l { left: 26px; top: 348px; transform: rotate(-4deg); }
        .b-r { right: 26px; top: 348px; transform: rotate(4deg); }
        .ftr { position: absolute; bottom: 0; left: 0; right: 0; height: 38px; background: #181211; color: #faf5eb; display: flex; align-items: center; justify-content: space-between; padding: 0 26px; font-size: 11.8px; font-weight: 700; z-index: 7; }
      </style></head><body class="grid-paper">
        <div class="top-bar"><img src="${LOGO}"><span class="stamp">🔥 ĐẤU TRƯỜNG ẨM THỰC</span></div>
        <div class="hd-wrap">
          <div class="h1">THỬ THÁCH 05 PHÚT</div>
          <div class="sub-pill">ĂN HẾT TẶNG NGAY <b>1.500.000Đ TIỀN MẶT</b></div>
        </div>
        <div class="arch"></div>
        <img class="ak-host" src="${CUT_AK}">
        <div class="burst b-l"><b>05 ĐÙI GÀ CỠ LỚN</b>Giòn rụm đẫm sốt Hàn!</div>
        <div class="burst b-r"><b>+ 01 MÌ TƯƠNG ĐEN</b>Bấm giờ đúng 05:00!</div>
        <div class="wood-ledge"></div>
        <img class="platter-ga" src="${CUT_GA08995}">
        <img class="platter-mi" src="${CUT_JJ}">
        <div class="ftr"><span>CS1: 38 Nguyễn Đình Chiểu • CS2: 35 Trần Hữu Duyệt</span><span style="color:#f6ca56">ĐĂNG KÝ THI: 0796 601 106</span></div>
      </body></html>`,
    },
    {
      folder: "261124 - Thử Thách 5 Phút 1 Triệu 5",
      file: "02 - Giải Thưởng Và Thể Lệ 1 Triệu 5.png",
      w: 800,
      h: 800,
      // Ref: EXACT BHC Chicken "Sweet BENEFIT! -4,000₩" Clipped Serrated Paper Receipt Poster!
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #1a100e; font-family: 'BeVN', sans-serif; display: flex; align-items: center; justify-content: center; }
        .bg-food { position: absolute; inset: -20px; width: 840px; height: 840px; object-fit: cover; filter: blur(4px) brightness(0.42) saturate(1.15); }
        .vignette { position: absolute; inset: 0; background: radial-gradient(circle, rgba(25,12,10,0.15) 20%, rgba(15,8,6,0.82) 100%); }
        .clip-svg { position: absolute; top: 26px; left: 50%; transform: translateX(-50%); z-index: 10; filter: drop-shadow(0 8px 10px rgba(0,0,0,0.45)); }
        .receipt-wrap { position: relative; width: 548px; margin-top: 28px; z-index: 5; filter: drop-shadow(0 26px 36px rgba(0,0,0,0.62)); }
        .zig-top { height: 14px; background: linear-gradient(-45deg, #fbf6ec 7px, transparent 0), linear-gradient(45deg, #fbf6ec 7px, transparent 0); background-size: 14px 14px; }
        .zig-bot { height: 14px; background: linear-gradient(-135deg, #fbf6ec 7px, transparent 0), linear-gradient(135deg, #fbf6ec 7px, transparent 0); background-size: 14px 14px; }
        .receipt { background: #fbf6ec; color: #191312; padding: 34px 38px 24px; position: relative; }
        .rc-top { text-align: center; border-bottom: 2px dashed #c7b9a5; padding-bottom: 14px; }
        .rc-top small { font-size: 11px; font-weight: 800; letter-spacing: 0.16em; color: #a81715; text-transform: uppercase; display: block; margin-bottom: 12px; }
        .rc-top h2 { font-family: 'BigShoulders', sans-serif; font-size: 50px; line-height: 1.05; color: #191312; text-transform: uppercase; }
        .total-box { margin: 16px 0; background: #a81715; color: #fbf6ec; border-radius: 10px; padding: 14px 20px; text-align: center; }
        .total-box small { font-size: 11px; font-weight: 800; letter-spacing: 0.14em; color: #f6ca56; display: block; }
        .total-box b { font-family: 'BigShoulders', sans-serif; font-size: 74px; line-height: 0.92; display: block; margin-top: 2px; }
        .total-box span { font-size: 12.5px; font-weight: 700; display: block; margin-top: 4px; }
        .rules { border-bottom: 2px dashed #c7b9a5; padding-bottom: 12px; }
        .r-item { display: flex; gap: 12px; padding: 9px 0; border-bottom: 1px solid rgba(25,19,18,0.09); align-items: flex-start; }
        .r-item:last-child { border-bottom: none; }
        .r-no { background: #191312; color: #f6ca56; font-family: 'Jakarta', sans-serif; font-weight: 800; font-size: 12px; padding: 3px 8px; border-radius: 5px; margin-top: 2px; }
        .r-tx b { display: block; font-size: 13.5px; font-weight: 800; color: #a81715; }
        .r-tx p { font-size: 12.5px; font-weight: 600; color: #2d2320; line-height: 1.4; margin-top: 2px; }
        .rc-btm { margin-top: 14px; display: flex; align-items: center; justify-content: space-between; }
        .rc-info { font-size: 11.5px; font-weight: 700; line-height: 1.5; color: #2d2320; }
        .rc-info b { color: #a81715; font-size: 13.5px; }
        .sticker-ga { position: absolute; right: -52px; top: 156px; width: 138px; transform: rotate(14deg); filter: drop-shadow(0 0 0 #fff) drop-shadow(0 8px 14px rgba(0,0,0,0.4)); z-index: 8; }
        .logo-pin { position: absolute; left: -34px; bottom: 52px; width: 102px; transform: rotate(-10deg); filter: drop-shadow(0 8px 14px rgba(0,0,0,0.45)); z-index: 8; }
      </style></head><body>
        <img class="bg-food" src="${PH_JJ_26}">
        <div class="vignette"></div>
        <svg class="clip-svg" width="84" height="68" viewBox="0 0 84 68">
          <path d="M26 28 C26 6, 58 6, 58 28" stroke="#d8d4ce" stroke-width="5" fill="none"/>
          <rect x="12" y="26" width="60" height="36" rx="5" fill="#232020" stroke="#3c3737" stroke-width="2"/>
          <rect x="18" y="34" width="48" height="6" rx="2" fill="#474242"/>
        </svg>
        <div class="receipt-wrap">
          <img class="sticker-ga" src="${CUT_DUI}">
          <img class="logo-pin" src="${LOGO}">
          <div class="zig-top"></div>
          <div class="receipt">
            <div class="rc-top">
              <small>OFFICIAL CHALLENGE TICKET  •  FEEL CHICKEN</small>
              <h2>THỂ LỆ & GIẢI THƯỞNG</h2>
            </div>
            <div class="total-box">
              <small>TIỀN MẶT TRAO TAY NGAY TẠI BÀN</small>
              <b>1.500.000 VNĐ</b>
              <span>+ MIỄN PHÍ 100% PHẦN ĂN KHI CHIẾN THẮNG!</span>
            </div>
            <div class="rules">
              <div class="r-item"><span class="r-no">01</span><div class="r-tx"><b>KHẨU PHẦN THÁCH ĐẤU</b><p>Ăn sạch 05 Đùi Gà Rán Cỡ Lớn + 01 Phần Mì Tương Đen Hàn Quốc.</p></div></div>
              <div class="r-item"><span class="r-no">02</span><div class="r-tx"><b>THỜI GIAN BẤM GIỜ: 05 PHÚT</b><p>Thử thách cá nhân 01 người • Áp dụng tại cả 2 cơ sở Nha Trang.</p></div></div>
              <div class="r-item"><span class="r-no">03</span><div class="r-tx"><b>CHƠI VUI KHÔNG LO LỖ</b><p>Chưa vượt qua chỉ thanh toán đúng 250.000đ giá gốc phần ăn!</p></div></div>
            </div>
            <div class="rc-btm">
              <div class="rc-info">38 Nguyễn Đình Chiểu • 35 Trần Hữu Duyệt<br>Đăng ký thi ngay: <b>0796 601 106</b></div>
              <div>${barcodeSvg}</div>
            </div>
          </div>
          <div class="zig-bot"></div>
        </div>
      </body></html>`,
    },

    // =========================================================================
    // POST 3 — 261128 - Mưa Ghé Feel Ấm Bụng (3 Hình — 100% Real Sony A1 + Pins)
    // =========================================================================
    {
      folder: "261128 - Mưa Ghé Feel Ấm Bụng",
      file: "01 - Mưa Ương Ương Ghé Feel Ấm Bụng.png",
      w: 1080,
      h: 720,
      // Ref: Korean Cream Grid Editorial Split × Real Sony A1 Hand-Dipping Feast (NVA 14)
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 1080px; height: 720px; display: flex; position: relative; overflow: hidden; font-family: 'BeVN', sans-serif; }
        .left { width: 486px; height: 100%; padding: 24px; border-right: 4px solid #1e1512; display: flex; flex-direction: column; }
        .card-in { flex: 1; border: 2px solid #1e1512; border-radius: 14px; padding: 24px 28px; display: flex; flex-direction: column; justify-content: space-between; background: rgba(255,252,246,0.75); }
        .top-b { display: flex; justify-content: space-between; align-items: center; }
        .top-b img { height: 50px; }
        .tag-kr { font-size: 11px; font-weight: 800; color: #a81715; letter-spacing: 0.1em; border: 1.5px solid #a81715; padding: 4px 11px; border-radius: 99px; }
        .tilt-red { display: inline-block; align-self: flex-start; background: #a81715; color: #faf5eb; font-size: 12px; font-weight: 800; padding: 5px 14px; transform: rotate(-2deg); margin-bottom: 12px; box-shadow: 3px 3px 0 #1e1512; }
        .h1 { font-family: 'Fraunces', serif; font-weight: 900; font-size: 40px; line-height: 1.15; color: #1e1512; letter-spacing: -0.02em; white-space: nowrap; }
        .h1 span { color: #a81715; display: block; }
        .desc { margin-top: 14px; font-size: 14px; font-weight: 500; line-height: 1.55; color: #3d2e29; }
        .deals { margin-top: 18px; display: flex; gap: 10px; }
        .dl { flex: 1; background: #ffffff; border: 2px solid #1e1512; box-shadow: 3px 3px 0 #1e1512; border-radius: 10px; padding: 9px 12px; }
        .dl small { display: block; font-size: 10px; font-weight: 800; color: #6e5850; text-transform: uppercase; }
        .dl b { font-family: 'Jakarta', sans-serif; font-size: 19px; font-weight: 800; color: #a81715; }
        .addr { font-size: 11.5px; font-weight: 700; color: #1e1512; padding-top: 12px; border-top: 1.5px dashed rgba(30,21,18,0.25); line-height: 1.48; }
        .right { flex: 1; position: relative; overflow: hidden; }
        .right img { width: 100%; height: 100%; object-fit: cover; }
        .badge-ship { position: absolute; right: 24px; bottom: 24px; background: #1e1512; color: #faf5eb; border: 2px solid #f6ca56; border-radius: 99px; padding: 8px 18px; font-size: 12.5px; font-weight: 800; box-shadow: 0 10px 22px rgba(0,0,0,0.35); }
        .badge-ship b { color: #f6ca56; }
      </style></head><body class="grid-paper">
        <div class="left">
          <div class="card-in">
            <div class="top-b"><img src="${LOGO}"><span class="tag-kr">양념치킨 & 분식</span></div>
            <div>
              <div class="tilt-red">🌧️ NGÀY MƯA NHA TRANG</div>
              <div class="h1">Mưa Ương Ương,<span>Ghé Feel Ấm Bụng!</span></div>
              <div class="desc">Phòng ấm khô ráo, gà rán 5 vị sốt Hàn vừa ra lò giòn rụm cùng mì cay, tokbokki & mì tương đen nóng hổi.</div>
              <div class="deals">
                <div class="dl"><small>Combo 1 Người</small><b>Từ 59.000đ</b></div>
                <div class="dl"><small>Combo Đôi</small><b>Từ 129.000đ</b></div>
              </div>
            </div>
            <div class="addr">CS1: 38 Nguyễn Đình Chiểu • CS2: 35 Trần Hữu Duyệt<br>Mở cửa: 10:00 – 22:00  |  Hotline: <span style="color:#a81715">0796 601 106</span></div>
          </div>
        </div>
        <div class="right">
          <img src="${PH_DIP_14}">
          <div class="badge-ship">🛵 Ngại Mưa? <b>Ship Giữ Nhiệt 15 Phút!</b></div>
        </div>
      </body></html>`,
    },
    {
      folder: "261128 - Mưa Ghé Feel Ấm Bụng",
      file: "02 - Gà Rán 5 Vị Sốt Hàn 129K.png",
      w: 800,
      h: 800,
      // Ref: EXACT SAN CHICKEN Pin (search_chicken_kr.jpg Row 1 Col 5 — Cream Grid + Giant Ochre/Red Text Behind Platter + 5 Real Sauce Medallions!)
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; padding: 20px; font-family: 'BeVN', sans-serif; }
        .frame { width: 100%; height: 100%; border: 2px solid #1e1512; border-radius: 14px; position: relative; overflow: hidden; }
        .top-pill { position: absolute; top: 18px; left: 50%; transform: translateX(-50%); border: 2px solid #1e1512; background: #ffffff; padding: 4px 18px; border-radius: 99px; font-size: 11px; font-weight: 800; letter-spacing: 0.14em; z-index: 6; }
        .giant-bg { position: absolute; top: 68px; left: 0; right: 0; text-align: center; font-family: 'BigShoulders', sans-serif; font-weight: 900; font-size: 138px; line-height: 1.02; color: #d89628; text-transform: uppercase; z-index: 1; letter-spacing: -0.01em; }
        .giant-bg span { display: block; color: #a81715; font-size: 128px; margin-top: 2px; }
        .platter { position: absolute; left: 50%; top: 274px; transform: translateX(-50%); width: 500px; z-index: 3; filter: drop-shadow(0 24px 24px rgba(30,18,12,0.34)); }
        .deal-stamp { position: absolute; right: 24px; top: 252px; z-index: 6; background: #a81715; color: #faf5eb; border: 2.5px solid #1e1512; box-shadow: 4px 4px 0 #1e1512; border-radius: 12px; padding: 8px 15px; transform: rotate(5deg); text-align: center; }
        .deal-stamp small { display: block; font-size: 10px; font-weight: 800; color: #f6ca56; }
        .deal-stamp b { font-family: 'BigShoulders', sans-serif; font-size: 34px; line-height: 0.95; }
        .sauces { position: absolute; left: 22px; right: 22px; bottom: 54px; z-index: 5; display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
        .sc-item { background: #ffffff; border: 2px solid #1e1512; border-radius: 10px; padding: 6px; text-align: center; box-shadow: 2px 2px 0 #1e1512; }
        .sc-item img { width: 58px; height: 58px; border-radius: 50%; object-fit: cover; border: 1.5px solid #1e1512; display: block; margin: 0 auto 4px; }
        .sc-item span { font-size: 10.5px; font-weight: 800; color: #1e1512; display: block; line-height: 1.2; }
        .ftr { position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background: #1e1512; color: #faf5eb; display: flex; align-items: center; justify-content: space-between; padding: 0 22px; font-size: 11.5px; font-weight: 700; z-index: 6; }
        .ftr img { height: 26px; }
      </style></head><body class="grid-paper">
        <div class="frame">
          <div class="top-pill">FEEL CHICKEN SIGNATURE  •  5 KOREAN SAUCES</div>
          <div class="giant-bg">GÀ RÁN<span>NGŨ VỊ</span></div>
          <img class="platter" src="${CUT_GA21}">
          <div class="deal-stamp"><small>COMBO ĐÔI TỪ</small><b>129.000Đ</b></div>
          <div class="sauces">
            <div class="sc-item"><img src="${S1}"><span>Sốt Phô Mai</span></div>
            <div class="sc-item"><img src="${S2}"><span>Sốt Cay Hàn</span></div>
            <div class="sc-item"><img src="${S3}"><span>Sốt Tỏi Cay</span></div>
            <div class="sc-item"><img src="${S4}"><span>Chanh Dây</span></div>
            <div class="sc-item"><img src="${S5}"><span>Sốt Tương</span></div>
          </div>
          <div class="ftr"><img src="${LOGO}"><span>38 Nguyễn Đình Chiểu • 35 Trần Hữu Duyệt | <b style="color:#f6ca56">0796 601 106</b></span></div>
        </div>
      </body></html>`,
    },
    {
      folder: "261128 - Mưa Ghé Feel Ấm Bụng",
      file: "03 - Bàn Tiệc Hội Bạn 249K.png",
      w: 800,
      h: 800,
      // Ref: Seoul Editorial Multi-Angle Real Feast Collage (Zero Duplicate Sony A1 Photos!)
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; padding: 24px; display: flex; flex-direction: column; gap: 12px; font-family: 'BeVN', sans-serif; color: #1e1512; }
        .hdr-box { background: #1e1512; color: #faf5eb; border-radius: 14px; padding: 16px 22px; display: flex; align-items: center; justify-content: space-between; }
        .hdr-l small { display: block; font-size: 11px; font-weight: 800; letter-spacing: 0.14em; color: #f6ca56; text-transform: uppercase; margin-bottom: 10px; }
        .hdr-l h1 { font-family: 'BigShoulders', sans-serif; font-size: 56px; line-height: 1.05; text-transform: uppercase; }
        .hdr-l p { font-size: 12.5px; color: rgba(250,245,235,0.85); margin-top: 6px; }
        .price-tag { background: #a81715; border: 2px solid #f6ca56; border-radius: 12px; padding: 10px 18px; text-align: center; transform: rotate(-2deg); }
        .price-tag small { display: block; font-size: 10px; font-weight: 800; color: #f6ca56; letter-spacing: 0.1em; }
        .price-tag b { font-family: 'BigShoulders', sans-serif; font-size: 38px; line-height: 0.95; color: #ffffff; }
        .bento-photos { flex: 1; display: grid; grid-template-columns: 1.25fr 0.95fr; grid-template-rows: 1fr 1fr; gap: 12px; min-height: 0; }
        .ph-card { position: relative; border: 2.5px solid #1e1512; border-radius: 14px; overflow: hidden; box-shadow: 4px 4px 0 #1e1512; }
        .ph-card.tall { grid-row: 1 / 3; }
        .ph-card img { width: 100%; height: 100%; object-fit: cover; }
        .lbl { position: absolute; left: 12px; bottom: 12px; background: rgba(24,18,17,0.88); color: #faf5eb; border: 1.5px solid #f6ca56; padding: 5px 12px; border-radius: 99px; font-size: 11.5px; font-weight: 800; }
        .ftr { background: #ffffff; border: 2px solid #1e1512; border-radius: 12px; padding: 10px 18px; display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 800; }
        .ftr img { height: 28px; }
      </style></head><body class="grid-paper">
        <div class="hdr-box">
          <div class="hdr-l">
            <small>PARTY SET FOR 3–4 FRIENDS  •  파티 세트</small>
            <h1>BÀN TIỆC HỘI BẠN</h1>
            <p>Gà Ngũ Vị • Mì Cay 55K • Tokbokki • Mì Tương Đen • Mì Ý • Khoai Tây</p>
          </div>
          <div class="price-tag"><small>COMBO HỘI BẠN</small><b>249K – 259K</b></div>
        </div>
        <div class="bento-photos">
          <div class="ph-card tall"><img src="${PH_GRP_13}"><span class="lbl">🍗 Mâm Tiệc Gà Ngũ Vị & Món Hàn</span></div>
          <div class="ph-card"><img src="${PH_MC_08}"><span class="lbl">🍜 Mì Cay Thố Sứ 7 Cấp Độ</span></div>
          <div class="ph-card"><img src="${PH_SPAG}"><span class="lbl">🍝 Mì Ý Sốt Bò Bằm Xúc Xích</span></div>
        </div>
        <div class="ftr"><img src="${LOGO}"><span>38 Nguyễn Đình Chiểu • 35 Trần Hữu Duyệt  |  <span style="color:#a81715">Hotline / Ship 15p: 0796 601 106</span></span></div>
      </body></html>`,
    },
  ];
}

async function main() {
  const reqDesktop = createRequire("C:\\AI\\full studio\\canvas\\desktop\\package.json");
  const puppeteer = reqDesktop("puppeteer-core");
  const chromePaths = [
    "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  ];
  const execPath = chromePaths.find((p) => fs.existsSync(p));
  const browser = await puppeteer.launch({
    executablePath: execPath,
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"],
  });

  const pages = buildPages();
  const tab = await browser.newPage();
  for (const item of pages) {
    await tab.setViewport({ width: item.w, height: item.h, deviceScaleFactor: 2 });
    await tab.setContent(item.html, { waitUntil: "load" });
    await tab.evaluate(() => document.fonts.ready);
    await new Promise((r) => setTimeout(r, 150));
    const dstDir = path.join(OUT, item.folder);
    fs.mkdirSync(dstDir, { recursive: true });
    await tab.screenshot({ path: path.join(dstDir, item.file), type: "png" });
    console.log("[Rendered Brave-Pinterest V4]", item.folder, "->", item.file);
  }
  await browser.close();
  console.log("ALL 9 BRAVE-PINTEREST V4 POSTERS COMPLETED!");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
