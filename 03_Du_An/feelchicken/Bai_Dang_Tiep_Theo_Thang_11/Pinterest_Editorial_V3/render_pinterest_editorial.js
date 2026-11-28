const fs = require("node:fs");
const path = require("node:path");

const PROJ = "C:\\AI\\full studio\\projects\\feelchicken_pinterest_v3";
const PLATES = path.join(PROJ, "plates");
const OUT = path.join(PROJ, "out_editorial");
const REF_DIR = "C:\\AI\\full studio\\projects\\feelchicken_3posts_redesign_v2\\refs";
const FONT_DIR = "C:\\AI\\full studio\\BO_KIEN_THUC_TVC_AI_PORTABLE\\03_TAI_NGUYEN_DUNG_CHUNG\\fonts_tvc_vi";

fs.mkdirSync(OUT, { recursive: true });

function dataUri(fullPath) {
  const buf = fs.readFileSync(fullPath);
  const ext = path.extname(fullPath).toLowerCase();
  const mime = ext === ".ttf" ? "font/ttf" : ext === ".png" ? "image/png" : "image/jpeg";
  return `data:${mime};base64,${buf.toString("base64")}`;
}

const FONT_CSS = `
@font-face { font-family: 'Fraunces'; src: url('${dataUri(path.join(FONT_DIR, "Fraunces-Black.ttf"))}') format('truetype'); font-weight: 900; }
@font-face { font-family: 'Fraunces'; src: url('${dataUri(path.join(FONT_DIR, "Fraunces-Bold.ttf"))}') format('truetype'); font-weight: 700; }
@font-face { font-family: 'BigShoulders'; src: url('${dataUri(path.join(FONT_DIR, "BigShouldersDisplay-Black.ttf"))}') format('truetype'); font-weight: 900; }
@font-face { font-family: 'BarlowCond'; src: url('${dataUri(path.join(FONT_DIR, "BarlowCondensed-BlackItalic.ttf"))}') format('truetype'); font-weight: 900; font-style: italic; }
@font-face { font-family: 'BarlowCond'; src: url('${dataUri(path.join(FONT_DIR, "BarlowCondensed-ExtraBold.ttf"))}') format('truetype'); font-weight: 800; font-style: normal; }
@font-face { font-family: 'Jakarta'; src: url('${dataUri(path.join(FONT_DIR, "PlusJakartaSans-ExtraBold.ttf"))}') format('truetype'); font-weight: 800; }
@font-face { font-family: 'Jakarta'; src: url('${dataUri(path.join(FONT_DIR, "PlusJakartaSans-Bold.ttf"))}') format('truetype'); font-weight: 700; }
@font-face { font-family: 'Jakarta'; src: url('${dataUri(path.join(FONT_DIR, "PlusJakartaSans-SemiBold.ttf"))}') format('truetype'); font-weight: 600; }
@font-face { font-family: 'BeVN'; src: url('${dataUri(path.join(FONT_DIR, "BeVietnamPro-ExtraBold.ttf"))}') format('truetype'); font-weight: 800; }
@font-face { font-family: 'BeVN'; src: url('${dataUri(path.join(FONT_DIR, "BeVietnamPro-SemiBold.ttf"))}') format('truetype'); font-weight: 600; }
@font-face { font-family: 'BeVN'; src: url('${dataUri(path.join(FONT_DIR, "BeVietnamPro-Medium.ttf"))}') format('truetype'); font-weight: 500; }
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }
`;

const LOGO = dataUri(path.join(REF_DIR, "fc_logo_rgba.png"));

function buildPages() {
  const p1_01 = dataUri(path.join(PLATES, "BG_P1_01_Hero_Wide.png"));
  const p1_02 = dataUri(path.join(PLATES, "BG_P1_02_Hai_San_Sq.png"));
  const p1_03 = dataUri(path.join(PLATES, "BG_P1_03_Dui_Ga_Sq.png"));
  const p1_04 = dataUri(path.join(PLATES, "BG_P1_04_Combo_89K_Sq.png"));

  const p2_01 = dataUri(path.join(PLATES, "BG_P2_01_Anh_Khang_Sq.png"));
  const p2_02 = dataUri(path.join(PLATES, "BG_P2_02_Flatlay_Inset.png"));

  const p3_01 = dataUri(path.join(PLATES, "BG_P3_01_Cozy_Wide.png"));
  const p3_02 = dataUri(path.join(PLATES, "BG_P3_02_Ga_5_Vi_Sq.png"));
  const p3_03 = dataUri(path.join(PLATES, "BG_P3_03_Ban_Tiec_Sq.png"));

  return [
    // =========================================================================
    // POST 1 (261122 - Mì Cay Ngày Mưa) — SEOUL DARK MOODY POCHA EDITORIAL
    // =========================================================================
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "01 - Mì Cay Hàn Quốc 55K.png",
      w: 1080,
      h: 720,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 1080px; height: 720px; position: relative; overflow: hidden; background: #120f0e; color: #faf6f0; font-family: 'BeVN', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(95deg, rgba(14,11,10,0.92) 0%, rgba(14,11,10,0.78) 42%, rgba(14,11,10,0.12) 68%, rgba(14,11,10,0.0) 100%), linear-gradient(0deg, rgba(12,9,8,0.88) 0%, rgba(12,9,8,0.0) 16%); }
        .top-bar { position: absolute; top: 34px; left: 48px; right: 48px; display: flex; align-items: center; justify-content: space-between; }
        .logo { height: 58px; width: auto; }
        .pill-meta { font-size: 11.5px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #f0d7a8; border: 1px solid rgba(240,215,168,0.35); background: rgba(18,13,12,0.55); padding: 7px 16px; border-radius: 99px; }
        .copy { position: absolute; left: 48px; top: 146px; width: 475px; }
        .kicker { font-size: 12.5px; font-weight: 600; letter-spacing: 0.16em; color: #e8b455; text-transform: uppercase; margin-bottom: 12px; }
        .h1 { font-family: 'BarlowCond', sans-serif; font-weight: 900; font-style: italic; font-size: 88px; line-height: 0.94; letter-spacing: 0.01em; text-transform: uppercase; color: #faf6f0; }
        .h1 span { display: block; color: #ea492e; margin-top: 4px; }
        .desc { margin-top: 22px; padding-left: 14px; border-left: 2.5px solid #e8b455; font-size: 15px; font-weight: 500; line-height: 1.55; color: rgba(250,246,240,0.86); max-width: 420px; }
        .price-row { margin-top: 28px; display: inline-flex; align-items: center; gap: 16px; border: 1px solid rgba(232,180,85,0.48); background: rgba(20,14,13,0.72); padding: 11px 22px; border-radius: 8px; }
        .pr-lbl { font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(250,246,240,0.72); }
        .pr-val { font-family: 'Jakarta', sans-serif; font-weight: 800; font-size: 26px; color: #f4c15d; letter-spacing: -0.01em; }
        .pr-sep { width: 1px; height: 26px; background: rgba(255,255,255,0.18); }
        .pr-lvl { font-size: 13.5px; font-weight: 600; color: #faf6f0; }
        .footer { position: absolute; left: 48px; right: 48px; bottom: 22px; padding-top: 13px; border-top: 1px solid rgba(255,255,255,0.15); display: flex; justify-content: space-between; font-size: 13px; font-weight: 500; color: rgba(250,246,240,0.85); }
        .footer b { color: #f4c15d; font-weight: 600; }
      </style></head><body>
        <img class="bg" src="${p1_01}">
        <div class="grad"></div>
        <div class="top-bar">
          <img class="logo" src="${LOGO}">
          <div class="pill-meta">RAINY SEASON  •  얼큰 해물 짬뽕</div>
        </div>
        <div class="copy">
          <div class="kicker">NHA TRANG NGÀY MƯA SE LẠNH</div>
          <div class="h1">MÌ CAY<span>HÀN QUỐC</span></div>
          <div class="desc">Nước dùng kim chi hầm xương nóng hổi trong thố đá giữ nhiệt, đầy ắp hải sản tươi, bạch tuộc & đùi gà sốt Hàn.</div>
          <div class="price-row">
            <div><div class="pr-lbl">ĐỒNG GIÁ</div><div class="pr-val">55.000đ</div></div>
            <div class="pr-sep"></div>
            <div class="pr-lvl">Đủ 7 Cấp Độ Cay  •  Ship Nóng 15p</div>
          </div>
        </div>
        <div class="footer">
          <span>CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt, Nha Trang</span>
          <span><b>Hotline / Giao nhanh: 0796 601 106</b>  (10:00 – 22:00)</span>
        </div>
      </body></html>`,
    },
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "02 - Mì Cay Hải Sản Bạch Tuộc.png",
      w: 800,
      h: 800,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #131110; color: #faf6f0; font-family: 'BeVN', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(16,13,12,0.92) 0%, rgba(16,13,12,0.72) 32%, rgba(16,13,12,0.0) 52%), linear-gradient(0deg, rgba(12,10,9,0.82) 0%, rgba(12,10,9,0.0) 15%); }
        .hdr { position: absolute; top: 34px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.14); padding-bottom: 14px; }
        .hdr-l { font-size: 11px; font-weight: 600; letter-spacing: 0.16em; color: #e8b455; text-transform: uppercase; }
        .hdr-r { font-size: 11px; font-weight: 500; letter-spacing: 0.1em; color: rgba(250,246,240,0.68); }
        .main { position: absolute; top: 98px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: flex-end; }
        .h1 { font-family: 'BarlowCond', sans-serif; font-weight: 900; font-style: italic; font-size: 66px; line-height: 0.95; text-transform: uppercase; color: #faf6f0; }
        .h1 span { color: #ea492e; display: block; margin-top: 3px; }
        .sub { margin-top: 12px; font-size: 14px; color: rgba(250,246,240,0.82); font-weight: 500; }
        .tag-price { border: 1px solid rgba(232,180,85,0.5); background: rgba(20,15,14,0.75); padding: 10px 18px; border-radius: 8px; text-align: right; }
        .tag-price small { display: block; font-size: 10px; letter-spacing: 0.14em; color: rgba(250,246,240,0.65); text-transform: uppercase; }
        .tag-price b { font-family: 'Jakarta', sans-serif; font-size: 24px; font-weight: 800; color: #f4c15d; }
        .ftr { position: absolute; bottom: 22px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: rgba(250,246,240,0.75); }
        .logo-sm { height: 34px; }
      </style></head><body>
        <img class="bg" src="${p1_02}">
        <div class="grad"></div>
        <div class="hdr">
          <span class="hdr-l">01  •  SEAFOOD & OCTOPUS RAMYEON</span>
          <span class="hdr-r">해물 문어 짬뽕</span>
        </div>
        <div class="main">
          <div>
            <div class="h1">MÌ CAY HẢI SẢN<span>& BẠCH TUỘC</span></div>
            <div class="sub">Tôm sú tươi ngọt  •  Bạch tuộc giòn sần sật  •  Nấm kim châm</div>
          </div>
          <div class="tag-price"><small>MỖI THỐ</small><b>55.000đ</b></div>
        </div>
        <div class="ftr">
          <img class="logo-sm" src="${LOGO}">
          <span>FEEL CHICKEN  •  Nước dùng kim chi Hàn Quốc nấu mới mỗi ngày</span>
        </div>
      </body></html>`,
    },
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "03 - Mì Cay Đùi Gà 7 Cấp Độ.png",
      w: 800,
      h: 800,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #131110; color: #faf6f0; font-family: 'BeVN', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(15,12,11,0.93) 0%, rgba(15,12,11,0.72) 32%, rgba(15,12,11,0.08) 56%), linear-gradient(270deg, rgba(15,12,11,0.90) 0%, rgba(15,12,11,0.65) 34%, rgba(15,12,11,0.0) 54%), linear-gradient(0deg, rgba(12,10,9,0.82) 0%, rgba(12,10,9,0.0) 14%); }
        .hdr { position: absolute; top: 34px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.14); padding-bottom: 14px; }
        .hdr-l { font-size: 11px; font-weight: 600; letter-spacing: 0.16em; color: #e8b455; text-transform: uppercase; }
        .hdr-r { font-size: 11px; font-weight: 500; letter-spacing: 0.1em; color: rgba(250,246,240,0.68); }
        .top-copy { position: absolute; top: 96px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: flex-start; }
        .h1 { font-family: 'BarlowCond', sans-serif; font-weight: 900; font-style: italic; font-size: 66px; line-height: 0.95; text-transform: uppercase; color: #faf6f0; }
        .h1 span { color: #ea492e; }
        .sub { margin-top: 10px; font-size: 14px; color: rgba(250,246,240,0.82); }
        .scale-card { position: absolute; right: 42px; bottom: 72px; width: 236px; background: rgba(18,14,13,0.82); border: 1px solid rgba(255,255,255,0.16); border-radius: 10px; padding: 16px 18px; backdrop-filter: blur(6px); }
        .sc-ttl { font-size: 10.5px; font-weight: 600; letter-spacing: 0.15em; color: #e8b455; text-transform: uppercase; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.12); }
        .sc-row { display: flex; justify-content: space-between; align-items: center; padding: 6.5px 0; border-bottom: 1px solid rgba(255,255,255,0.07); font-size: 12px; }
        .sc-row:last-child { border-bottom: none; }
        .sc-lv { font-family: 'Jakarta', sans-serif; font-weight: 700; color: #faf6f0; width: 52px; }
        .sc-nm { color: rgba(250,246,240,0.72); flex: 1; font-size: 11.5px; }
        .bars { display: flex; gap: 3px; }
        .bar { width: 6px; height: 10px; border-radius: 1.5px; background: rgba(255,255,255,0.14); }
        .bar.on { background: #ea492e; }
        .bar.warm { background: #f0a83a; }
        .ftr { position: absolute; bottom: 22px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: rgba(250,246,240,0.78); }
        .logo-sm { height: 34px; }
      </style></head><body>
        <img class="bg" src="${p1_03}">
        <div class="grad"></div>
        <div class="hdr">
          <span class="hdr-l">02  •  CRISPY DRUMSTICK & SPICE INDEX</span>
          <span class="hdr-r">매운 닭다리 라면</span>
        </div>
        <div class="top-copy">
          <div>
            <div class="h1">MÌ CAY ĐÙI GÀ  •  <span>7 CẤP ĐỘ</span></div>
            <div class="sub">Đùi gà chiên vàng thấm súp cay nồng  •  Đồng giá 55.000đ</div>
          </div>
        </div>
        <div class="scale-card">
          <div class="sc-ttl">SPICE LEVEL  01 — 07</div>
          ${[
            ["LV.01", "The nhẹ", 1],
            ["LV.02", "Ấm vị", 2],
            ["LV.03", "Cay vừa", 3],
            ["LV.04", "Cay nồng", 4],
            ["LV.05", "Cay tê", 5],
            ["LV.06", "Bùng nổ", 6],
            ["LV.07", "Thách thức", 7],
          ]
            .map(
              ([lv, nm, n]) => `<div class="sc-row"><span class="sc-lv">${lv}</span><span class="sc-nm">${nm}</span><div class="bars">${[1,2,3,4,5,6,7]
                .map((k) => `<span class="bar ${k <= n ? (n <= 3 ? "warm" : "on") : ""}"></span>`)
                .join("")}</div></div>`
            )
            .join("")}
        </div>
        <div class="ftr">
          <img class="logo-sm" src="${LOGO}">
          <span>Tự chọn cấp độ cay hợp gu  •  Hotline: 0796 601 106</span>
        </div>
      </body></html>`,
    },
    {
      folder: "261122 - Mì Cay Ngày Mưa",
      file: "04 - Combo Feel Spicy 89K.png",
      w: 800,
      h: 800,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #161210; color: #faf6f0; font-family: 'BeVN', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(18,13,11,0.94) 0%, rgba(18,13,11,0.78) 34%, rgba(18,13,11,0.0) 54%), linear-gradient(0deg, rgba(12,9,8,0.84) 0%, rgba(12,9,8,0.0) 15%); }
        .hdr { position: absolute; top: 34px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.14); padding-bottom: 14px; }
        .hdr-l { font-size: 11px; font-weight: 600; letter-spacing: 0.16em; color: #e8b455; text-transform: uppercase; }
        .hdr-r { font-size: 11px; font-weight: 500; letter-spacing: 0.1em; color: rgba(250,246,240,0.68); }
        .main { position: absolute; top: 96px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: flex-end; }
        .h1 { font-family: 'BarlowCond', sans-serif; font-weight: 900; font-style: italic; font-size: 68px; line-height: 0.94; text-transform: uppercase; color: #faf6f0; }
        .h1 span { color: #f4c15d; display: block; margin-top: 3px; }
        .items { margin-top: 14px; display: flex; gap: 10px; font-size: 13px; font-weight: 600; color: #faf6f0; }
        .items span { background: rgba(255,255,255,0.09); border: 1px solid rgba(255,255,255,0.16); padding: 5px 11px; border-radius: 6px; }
        .price-box { background: #d93824; padding: 12px 20px; border-radius: 8px; text-align: right; }
        .price-box small { display: block; font-size: 10px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.85); text-transform: uppercase; }
        .price-box b { font-family: 'Jakarta', sans-serif; font-size: 28px; font-weight: 800; color: #fff8ec; }
        .ftr { position: absolute; bottom: 22px; left: 42px; right: 42px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: rgba(250,246,240,0.8); }
        .logo-sm { height: 34px; }
      </style></head><body>
        <img class="bg" src="${p1_04}">
        <div class="grad"></div>
        <div class="hdr">
          <span class="hdr-l">03  •  BEST-SELLING SOLO SET</span>
          <span class="hdr-r">스파이시 콤보 세트</span>
        </div>
        <div class="main">
          <div>
            <div class="h1">COMBO<span>FEEL SPICY</span></div>
            <div class="items">
              <span>01 Nồi Mì Cay</span>
              <span>01 Đùi Gà Sốt Hàn</span>
              <span>01 Coca-Cola</span>
            </div>
          </div>
          <div class="price-box"><small>TRỌN BỘ CHỈ</small><b>89.000đ</b></div>
        </div>
        <div class="ftr">
          <img class="logo-sm" src="${LOGO}">
          <span>38 Nguyễn Đình Chiểu  •  35 Trần Hữu Duyệt  |  0796 601 106</span>
        </div>
      </body></html>`,
    },

    // =========================================================================
    // POST 2 (261124 - Thử Thách 5 Phút 1 Triệu 5) — SEOUL CRIMSON × IVORY BENTO
    // =========================================================================
    {
      folder: "261124 - Thử Thách 5 Phút 1 Triệu 5",
      file: "01 - Thử Thách 5 Phút Anh Khang.png",
      w: 800,
      h: 800,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #921915; color: #faf4e8; font-family: 'Jakarta', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(132,20,16,0.65) 0%, rgba(132,20,16,0.0) 26%), linear-gradient(0deg, rgba(20,12,11,0.88) 0%, rgba(20,12,11,0.0) 16%); }
        .frame { position: absolute; inset: 20px; border: 1px solid rgba(250,244,232,0.28); border-radius: 14px; pointer-events: none; }
        .top-row { position: absolute; top: 34px; left: 38px; right: 38px; display: flex; justify-content: space-between; align-items: center; }
        .logo { height: 48px; }
        .badge-top { font-size: 11px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; padding: 6px 14px; border-radius: 99px; border: 1px solid rgba(250,244,232,0.45); color: #faf4e8; }
        .hero-txt { position: absolute; top: 92px; left: 38px; right: 38px; text-align: center; }
        .h1 { font-family: 'BigShoulders', sans-serif; font-weight: 900; font-size: 92px; line-height: 0.92; letter-spacing: 0.01em; color: #faf4e8; text-transform: uppercase; }
        .prize-pill { display: inline-block; margin-top: 12px; background: #f5efe4; color: #921915; font-size: 15.5px; font-weight: 800; letter-spacing: 0.03em; padding: 8px 22px; border-radius: 99px; }
        .btm-bar { position: absolute; bottom: 32px; left: 38px; right: 38px; display: flex; justify-content: space-between; align-items: center; font-family: 'BeVN', sans-serif; font-size: 12.5px; font-weight: 600; color: #faf4e8; padding-top: 10px; border-top: 1px solid rgba(250,244,232,0.24); }
        .timer-tag { background: #191312; color: #f4c44e; padding: 5px 12px; border-radius: 6px; font-family: 'Jakarta', sans-serif; font-weight: 800; letter-spacing: 0.06em; }
      </style></head><body>
        <img class="bg" src="${p2_01}">
        <div class="grad"></div>
        <div class="frame"></div>
        <div class="top-row">
          <img class="logo" src="${LOGO}">
          <span class="badge-top">SPEED MUKBANG  •  5분 푸드 챌린지</span>
        </div>
        <div class="hero-txt">
          <div class="h1">THỬ THÁCH 05 PHÚT</div>
          <div class="prize-pill">ĂN SẠCH NHẬN NGAY 1.500.000Đ TIỀN MẶT</div>
        </div>
        <div class="btm-bar">
          <span>05 Đùi Gà Cỡ Lớn  +  01 Phần Mì Tương Đen</span>
          <span class="timer-tag">TIME LIMIT  05:00</span>
        </div>
      </body></html>`,
    },
    {
      folder: "261124 - Thử Thách 5 Phút 1 Triệu 5",
      file: "02 - Giải Thưởng Và Thể Lệ 1 Triệu 5.png",
      w: 800,
      h: 800,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; background: #f6f1e7; color: #191413; font-family: 'BeVN', sans-serif; padding: 26px; display: flex; flex-direction: column; gap: 14px; }
        .top-bento { display: grid; grid-template-columns: 152px 1fr; gap: 14px; height: 168px; }
        .card-logo { background: #191413; border-radius: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; padding: 14px; }
        .card-logo img { width: 92px; height: auto; }
        .card-logo span { font-size: 11px; color: #f0d59c; letter-spacing: 0.1em; font-weight: 600; }
        .card-prize { background: #9c1d18; border-radius: 16px; padding: 20px 26px; display: flex; flex-direction: column; justify-content: center; color: #faf5ec; position: relative; }
        .cp-kicker { display: inline-block; align-self: flex-start; background: #f3c44e; color: #191413; font-size: 10.5px; font-weight: 800; letter-spacing: 0.1em; padding: 4px 12px; border-radius: 99px; text-transform: uppercase; margin-bottom: 8px; }
        .cp-num { font-family: 'BigShoulders', sans-serif; font-weight: 900; font-size: 74px; line-height: 0.92; letter-spacing: 0.01em; color: #faf5ec; }
        .cp-sub { margin-top: 6px; font-size: 13.5px; font-weight: 600; color: rgba(250,245,236,0.9); }
        .photo-bento { position: relative; flex: 1; border-radius: 16px; border: 2px solid #191413; overflow: hidden; background: #221816; }
        .photo-bento img { width: 100%; height: 100%; object-fit: cover; }
        .float-pill { position: absolute; top: 14px; right: 14px; background: #faf5ec; color: #9c1d18; border: 2px solid #191413; box-shadow: 3px 3px 0 #191413; border-radius: 99px; padding: 6px 15px; font-size: 12px; font-weight: 800; }
        .rules-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .rule-card { background: #ffffff; border: 2px solid #191413; box-shadow: 0 3px 0 #191413; border-radius: 14px; padding: 14px 15px; }
        .rc-hd { font-family: 'Jakarta', sans-serif; font-size: 12.5px; font-weight: 800; color: #9c1d18; margin-bottom: 5px; letter-spacing: 0.02em; }
        .rc-bd { font-size: 12px; font-weight: 500; line-height: 1.45; color: #2a211f; }
        .ftr-bento { background: #191413; color: #faf5ec; border-radius: 12px; padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; font-size: 12.5px; font-weight: 600; }
        .ftr-bento .hl { color: #f3c44e; }
        .cta-btn { background: #9c1d18; color: #ffffff; padding: 6px 14px; border-radius: 99px; font-weight: 800; font-size: 12px; }
      </style></head><body>
        <div class="top-bento">
          <div class="card-logo">
            <img src="${LOGO}">
            <span>5분 챌린지</span>
          </div>
          <div class="card-prize">
            <span class="cp-kicker">GIẢI THƯỞNG TIỀN MẶT TRAO TAY</span>
            <div class="cp-num">1.500.000 VNĐ</div>
            <div class="cp-sub">+ Miễn phí 100% phần ăn khi hoàn thành trong 05 phút</div>
          </div>
        </div>
        <div class="photo-bento">
          <img src="${p2_02}">
          <div class="float-pill">★ THƯỞNG NÓNG TẠI BÀN</div>
        </div>
        <div class="rules-grid">
          <div class="rule-card">
            <div class="rc-hd">01. KHẨU PHẦN</div>
            <div class="rc-bd">Ăn sạch 05 Đùi gà rán cỡ lớn & 01 Phần mì tương đen Hàn Quốc.</div>
          </div>
          <div class="rule-card">
            <div class="rc-hd">02. THỜI GIAN</div>
            <div class="rc-bd">Thử thách cá nhân 01 người hoàn thành trong vòng 05 phút.</div>
          </div>
          <div class="rule-card">
            <div class="rc-hd">03. KHÔNG LO LỖ</div>
            <div class="rc-bd">Chưa vượt qua chỉ thanh toán 250.000đ đúng giá phần ăn.</div>
          </div>
        </div>
        <div class="ftr-bento">
          <span>CS1: <span class="hl">38 Nguyễn Đình Chiểu</span>  •  CS2: <span class="hl">35 Trần Hữu Duyệt</span></span>
          <span class="cta-btn">Đăng ký thi: 0796 601 106</span>
        </div>
      </body></html>`,
    },

    // =========================================================================
    // POST 3 (261128 - Mưa Ghé Feel Ấm Bụng) — SUNLIT CREAM SEOUL MAGAZINE
    // =========================================================================
    {
      folder: "261128 - Mưa Ghé Feel Ấm Bụng",
      file: "01 - Mưa Ương Ương Ghé Feel Ấm Bụng.png",
      w: 1080,
      h: 720,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 1080px; height: 720px; position: relative; overflow: hidden; background: #f5efe6; color: #221714; font-family: 'BeVN', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(92deg, rgba(245,239,230,0.96) 0%, rgba(245,239,230,0.82) 33%, rgba(245,239,230,0.0) 47%); }
        .mast { position: absolute; top: 32px; left: 48px; right: 48px; padding-bottom: 13px; border-bottom: 1px solid rgba(34,23,20,0.15); display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; }
        .mast .l { color: #a3221a; }
        .mast .r { color: #3a2a25; background: rgba(245,239,230,0.84); padding: 2px 8px; border-radius: 4px; }
        .copy { position: absolute; left: 48px; top: 168px; width: 450px; }
        .kicker { font-size: 12px; font-weight: 700; letter-spacing: 0.15em; color: #a3221a; text-transform: uppercase; margin-bottom: 14px; }
        .h1 { font-family: 'Fraunces', serif; font-weight: 900; font-size: 48px; line-height: 1.12; letter-spacing: -0.02em; color: #201512; white-space: nowrap; }
        .rule-red { width: 48px; height: 3px; background: #a3221a; margin: 22px 0; }
        .desc { font-size: 15px; font-weight: 500; line-height: 1.6; color: #463530; max-width: 410px; }
        .chips { margin-top: 26px; display: flex; gap: 10px; flex-wrap: wrap; }
        .chip { font-size: 12.5px; font-weight: 700; padding: 8px 15px; border-radius: 99px; border: 1.5px solid #201512; color: #201512; background: rgba(255,255,255,0.65); }
        .chip.red { background: #a3221a; border-color: #a3221a; color: #faf5ec; }
        .ftr-bar { position: absolute; left: 0; right: 0; bottom: 0; height: 48px; background: #201512; color: #f5efe6; padding: 0 48px; display: flex; justify-content: space-between; align-items: center; font-size: 12.5px; font-weight: 600; }
        .ftr-l { display: flex; align-items: center; gap: 12px; }
        .ftr-l img { height: 30px; }
        .ftr-bar b { color: #f2c35a; }
      </style></head><body>
        <img class="bg" src="${p3_01}">
        <div class="grad"></div>
        <div class="mast">
          <span class="l">FEEL CHICKEN  •  KOREAN KITCHEN</span>
          <span class="r">양념치킨 & 분식  •  RAINY DAY TABLE</span>
        </div>
        <div class="copy">
          <div class="kicker">NHỮNG NGÀY MƯA NHA TRANG</div>
          <div class="h1">Mưa Ương Ương,<br>Ghé Feel Ấm Bụng.</div>
          <div class="rule-red"></div>
          <div class="desc">Phòng ấm khô ráo, mâm gà rán 5 vị sốt Hàn vừa ra lò giòn rụm cùng tokbokki, mì cay & mì tương đen nóng hổi.</div>
          <div class="chips">
            <span class="chip red">Combo Cá Nhân từ 59.000đ</span>
            <span class="chip">Giao Nóng Tận Nhà 15 Phút</span>
          </div>
        </div>
        <div class="ftr-bar">
          <div class="ftr-l"><img src="${LOGO}"><span>CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt, Nha Trang</span></div>
          <span><b>Hotline: 0796 601 106</b>  (10:00 – 22:00)</span>
        </div>
      </body></html>`,
    },
    {
      folder: "261128 - Mưa Ghé Feel Ấm Bụng",
      file: "02 - Gà Rán 5 Vị Sốt Hàn 129K.png",
      w: 800,
      h: 800,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #f5efe6; color: #201512; font-family: 'BeVN', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(245,239,230,0.92) 0%, rgba(245,239,230,0.65) 22%, rgba(245,239,230,0.0) 34%); }
        .mast { position: absolute; top: 28px; left: 42px; right: 42px; padding-bottom: 12px; border-bottom: 1px solid rgba(34,23,20,0.14); display: flex; justify-content: space-between; font-size: 10.5px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; }
        .mast .l { color: #a3221a; }
        .center-hd { position: absolute; top: 74px; left: 42px; right: 42px; text-align: center; }
        .kicker { font-size: 11.5px; font-weight: 700; letter-spacing: 0.16em; color: #a3221a; text-transform: uppercase; margin-bottom: 8px; }
        .h1 { font-family: 'Fraunces', serif; font-weight: 900; font-size: 58px; line-height: 1.04; letter-spacing: -0.02em; color: #201512; }
        .sub { margin-top: 10px; font-size: 13.5px; font-weight: 600; color: #463530; }
        .pill { display: inline-block; margin-top: 14px; background: #a3221a; color: #faf5ec; font-size: 12.5px; font-weight: 700; padding: 7px 20px; border-radius: 99px; letter-spacing: 0.02em; }
        .ftr-bar { position: absolute; left: 0; right: 0; bottom: 0; height: 42px; background: #201512; color: #f5efe6; padding: 0 38px; display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; font-weight: 600; }
        .ftr-bar img { height: 26px; }
        .ftr-bar b { color: #f2c35a; }
      </style></head><body>
        <img class="bg" src="${p3_02}">
        <div class="grad"></div>
        <div class="mast">
          <span class="l">FEEL CHICKEN  •  SIGNATURE</span>
          <span>5가지 양념치킨 & 떡볶이</span>
        </div>
        <div class="center-hd">
          <div class="kicker">CHIÊN TƯƠI NÓNG GIÒN MỖI NGÀY</div>
          <div class="h1">Gà Rán 5 Vị Sốt Hàn</div>
          <div class="sub">Phô Mai  •  Cay Hàn  •  Tỏi Cay  •  Chanh Dây  •  Sốt Tương</div>
          <div class="pill">Combo Đôi Nóng Hổi chỉ từ 129.000đ</div>
        </div>
        <div class="ftr-bar">
          <img src="${LOGO}">
          <span>38 Nguyễn Đình Chiểu  •  35 Trần Hữu Duyệt  |  <b>0796 601 106</b></span>
        </div>
      </body></html>`,
    },
    {
      folder: "261128 - Mưa Ghé Feel Ấm Bụng",
      file: "03 - Bàn Tiệc Hội Bạn 249K.png",
      w: 800,
      h: 800,
      html: `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${FONT_CSS}
        body { width: 800px; height: 800px; position: relative; overflow: hidden; background: #f5efe6; color: #201512; font-family: 'BeVN', sans-serif; }
        .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
        .grad { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(245,239,230,0.92) 0%, rgba(245,239,230,0.65) 22%, rgba(245,239,230,0.0) 34%); }
        .mast { position: absolute; top: 28px; left: 42px; right: 42px; padding-bottom: 12px; border-bottom: 1px solid rgba(34,23,20,0.14); display: flex; justify-content: space-between; font-size: 10.5px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; }
        .mast .l { color: #a3221a; }
        .center-hd { position: absolute; top: 74px; left: 42px; right: 42px; text-align: center; }
        .kicker { font-size: 11.5px; font-weight: 700; letter-spacing: 0.16em; color: #a3221a; text-transform: uppercase; margin-bottom: 8px; }
        .h1 { font-family: 'Fraunces', serif; font-weight: 900; font-size: 58px; line-height: 1.04; letter-spacing: -0.02em; color: #201512; }
        .sub { margin-top: 10px; font-size: 13.5px; font-weight: 600; color: #463530; }
        .pill { display: inline-block; margin-top: 14px; background: #201512; color: #f5efe6; font-size: 12.5px; font-weight: 700; padding: 7px 20px; border-radius: 99px; letter-spacing: 0.02em; }
        .pill span { color: #f2c35a; }
        .ftr-bar { position: absolute; left: 0; right: 0; bottom: 0; height: 42px; background: #201512; color: #f5efe6; padding: 0 38px; display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; font-weight: 600; }
        .ftr-bar img { height: 26px; }
        .ftr-bar b { color: #f2c35a; }
      </style></head><body>
        <img class="bg" src="${p3_03}">
        <div class="grad"></div>
        <div class="mast">
          <span class="l">FEEL CHICKEN  •  GATHERING SET</span>
          <span>파티 세트 메뉴  •  3–4 PAX</span>
        </div>
        <div class="center-hd">
          <div class="kicker">ĐI ĐÔNG ĂN THẢ GA KHÔNG LO NGHĨ</div>
          <div class="h1">Bàn Tiệc Hội Bạn</div>
          <div class="sub">Gà Ngũ Vị  •  Mì Cay 55K  •  Mì Tương Đen  •  Mì Ý  •  Tokbokki</div>
          <div class="pill">Combo Hội Bạn No Căng  <span>249.000đ – 259.000đ</span></div>
        </div>
        <div class="ftr-bar">
          <img src="${LOGO}">
          <span>38 Nguyễn Đình Chiểu  •  35 Trần Hữu Duyệt  |  <b>0796 601 106</b></span>
        </div>
      </body></html>`,
    },
  ];
}

async function main() {
  const { createRequire } = require("node:module");
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
    const dstPath = path.join(dstDir, item.file);
    await tab.screenshot({ path: dstPath, type: "png" });
    console.log("[Rendered 2x Retina]", item.folder, "->", item.file);
  }
  await browser.close();
  console.log("ALL 9 PINTEREST EDITORIAL POSTERS RENDERED!");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
