const fs = require("fs");
const path = require("path");
const puppeteer = require("D:/AI/full studio/canvas/desktop/node_modules/puppeteer-core");

const V5 = "D:/AI/full studio/output/f20-set-qua-2011/v5_master";
const V7 = "D:/AI/full studio/output/f20-set-qua-2011/v7_master";
const SPRITES = path.join(V7, "typos_v7");
fs.mkdirSync(SPRITES, { recursive: true });

const FONT_DIR = "D:/AI/full studio/BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fonts_tvc_vi";
const LOGO_PNG = "D:/AI/full studio/output/f20-set-qua-2011/v3_pro/refs_clean/f20_logo_official.png";

function fontDataUrl(fn) {
  const b64 = fs.readFileSync(path.join(FONT_DIR, fn)).toString("base64");
  return `data:font/ttf;base64,${b64}`;
}
const logoDataUrl = "data:image/png;base64," + fs.readFileSync(LOGO_PNG).toString("base64");

const tl = JSON.parse(fs.readFileSync(path.join(V5, "timeline_v5_master.json"), "utf8"));
const bmap = Object.fromEntries(tl.blocks.map((b) => [b.id, b]));
const bt = (id) => [bmap[id].start, bmap[id].end];

const [b01_s, b01_e] = bt("b01_open_live");
const [b02_s, b02_e] = bt("b02_nhatrang_real");
const [b03_s, b03_e] = bt("b03_ship_104_clean");
const [b04_s, b04_e] = bt("b04_wide_oanh_104_live");
const [b05_s, b05_e] = bt("b05_intro_set_live");
const [b06_s, b06_e] = bt("b06_4items_real_tight");
const [b07a_s, b07a_e] = bt("b07a_yen_giatri_real");
const [b07b_s, b07b_e] = bt("b07b_camnang_live");
const [b08_s, b08_e] = bt("b08_chungyen_clean");
const [b09a_s, b09a_e] = bt("b09a_giomica_real");
const [b09b_s, b09b_e] = bt("b09b_quai_da_live");
const [b09c_s, b09c_e] = bt("b09c_hoa_no_real");
const [b10a_s, b10a_e] = bt("b10a_sx_live");
const [b10b_s, b10b_e] = bt("b10b_sx_yentam_real");
const [b11a_s, b11a_e] = bt("b11a_cta_live1");
const [b11b_s, b11b_e] = bt("b11b_cta_2011_real");
const [b11c_s, b11c_e] = bt("b11c_cta_inbox_live");

// Clean, well-paced 2-line editorial subtitles with natural inline highlighted spans!
const SUBTITLES = [
  [b01_s + 0.05, 8.65,  [["Hôm nay bên Oanh chuẩn bị"], ["<em>104 SET QUÀ</em> cho khách đặt"]]],
  [8.72,        10.82,  [["để làm <em>QUÀ BIẾU TẶNG</em>"], ["tri ân quý thầy cô giáo"]]],
  [10.88,       b01_e,  [["nhân dịp lễ <em>20 THÁNG 11</em>"], ["sắp tới đây nha!"]]],

  [b02_s + 0.04, 15.80, [["Ở <em>NHA TRANG</em> hôm nay"], ["bên Oanh có 02 đơn lớn:"]]],
  [15.88,       19.55,  [["01 là <em>ANH HẬU</em> • Đăng Khoa Edu"], ["đặt liền <em>77 SET QUÀ</em>"]]],
  [19.62,       b02_e,  [["và 01 nhóm <em>HỘI PHỤ HUYNH</em>"], ["đặt thêm <em>13 SET QUÀ</em>"]]],

  [b03_s + 0.05, 26.55, [["Ngoài <em>HÀ NỘI</em> một khách quen"], ["đặt <em>10 SET</em> gửi xe ra"]]],
  [26.62,       29.55,  [["ở <em>TP. HỒ CHÍ MINH</em>"], ["khách đặt thêm <em>04 SET</em>"]]],
  [29.62,       b03_e,  [["Tổng sáng nay bên Oanh chuẩn bị"], ["đủ <em>104 SET QUÀ</em> nha!"]]],

  [b04_s + 0.05, b04_e, [["Đây là những <em>SET QUÀ</em>"], ["bên Oanh đã chuẩn bị xong!"]]],
  [b05_s + 0.05, b05_e, [["Bây giờ Oanh giới thiệu chi tiết"], ["<em>01 SET QUÀ</em> cho mọi người xem!"]]],

  [b06_s + 0.05, 48.05, [["Một <em>SET QUÀ TẶNG</em> sang trọng"], ["bên trong sẽ gồm 04 món:"]]],
  [48.12,       50.42,  [["Đầu tiên là <em>01 SET YẾN SÀO</em>"], ["cao cấp thương hiệu SKA NEST"]]],
  [50.48,       53.60,  [["gồm <em>01 TỔ YẾN TINH CHẾ</em>"], ["sợi dài • dòng tiêu chuẩn"]]],
  [53.68,       56.85,  [["kèm theo đầy đủ"], ["<em>NGUYÊN LIỆU CHƯNG</em> gồm:"]]],
  [56.92,       58.05,  [["<em>TÁO ĐỎ</em> • <em>ĐÔNG TRÙNG HẠ THẢO</em>"]]],
  [58.12,       60.20,  [["cùng <em>KỶ TỬ</em> và <em>ĐƯỜNG PHÈN</em>"]]],
  [60.28,       63.42,  [["Thứ 2 là <em>02 HỘP RONG BIỂN</em>"], ["sấy giòn thương hiệu Tuệ Tâm"]]],
  [63.48,       65.72,  [["01 hộp <em>SẤY GIÒN CAY NHẸ</em>"]]],
  [65.78,       68.00,  [["và 01 hộp <em>SẤY MÈ KHÔNG CAY</em>"]]],
  [68.08,       72.70,  [["Thứ 3 là 01 gói <em>BÁNH THUYỀN</em>"], ["mix hạt dinh dưỡng <em>250G</em>"]]],
  [72.78,       77.08,  [["Thứ 4 là 01 gói <em>RONG BIỂN KẸP HẠT</em>"], ["túi lớn trọng lượng <em>500G</em>"]]],
  [77.14,       b06_e,  [["bên trong có <em>22 – 24 THANH</em>"], ["bánh hạt dinh dưỡng nhé!"]]],

  [b07a_s + 0.05, b07a_e, [["Giá trị nhất là <em>TỔ YẾN TINH CHẾ</em>"], ["dòng tiêu chuẩn <em>SỢI DÀI</em>"]]],
  [b07b_s + 0.05, 95.10,  [["Bên Oanh chuẩn bị kèm theo"], ["<em>01 TỜ CẨM NANG</em> hướng dẫn"]]],
  [95.18,        b07b_e,  [["ghi rõ <em>CÁCH CHƯNG YẾN</em>"], ["và công dụng của yến sào"]]],
  [b08_s + 0.05, b08_e,   [["để người nhận dễ dàng chế biến"], ["ra <em>CHÉN YẾN THƠM NGON</em>!"]]],

  [b09a_s + 0.05, b09a_e, [["Tất cả được gói ghém chỉn chu"], ["trong <em>GIỎ QUÀ MICA</em> trong suốt"]]],
  [b09b_s + 0.05, b09b_e, [["bên trên có <em>QUAI XÁCH DA</em>"], ["màu đỏ đô rất sang trọng!"]]],
  [b09c_s + 0.05, 115.35, [["Có điểm nhấn thêm"], ["<em>BÔNG HOA TRANG TRÍ</em> tinh tế"]]],
  [115.42,       b09c_e,  [["cùng chiếc <em>NƠ VOAN MÀU BE</em>"], ["rất xinh xắn như thế này!"]]],

  [b10a_s + 0.05, b10a_e, [["Toàn bộ đều là sản phẩm do"], ["<em>CÔNG TY F20</em> trực tiếp sản xuất"]]],
  [b10b_s + 0.05, b10b_e, [["nên anh chị hoàn toàn yên tâm"], ["về <em>CHẤT LƯỢNG & XUẤT XỨ</em>!"]]],

  [b11a_s + 0.05, b11a_e, [["Anh chị có nhu cầu đặt"], ["<em>SET QUÀ TẶNG</em> dịp lễ"]]],
  [b11b_s + 0.05, b11b_e, [["tri ân <em>20 THÁNG 11</em>"], ["hoặc các dịp lễ sắp tới"]]],
  [b11c_s + 0.05, b11c_e, [["hãy <em>NHẮN TIN CHO BÊN OANH</em>"], ["để được tư vấn chi tiết nhé!"]]],
];

const PIP_LABELS = [
  "QUÀ BIẾU 20/11",
  "04 MÓN TRONG SET",
  "22 – 24 THANH HẠT",
  "CẨM NANG CHƯNG YẾN",
  "F20 TRỰC TIẾP SX",
  "ĐẶT SỈ & LẺ 20/11",
  "QUAI DA ĐỎ ĐÔ",
];

const ING_ITEMS = [
  { text: "01 • TÁO ĐỎ TÂN CƯƠNG", dot: "#E64858" },
  { text: "02 • ĐÔNG TRÙNG HẠ THẢO", dot: "#E8A230" },
  { text: "03 • KỶ TỬ HỮU CƠ", dot: "#E0553C" },
  { text: "04 • ĐƯỜNG PHÈN KẾT TINH", dot: "#4CD48A" },
];

const BASE_CSS = `
  @font-face { font-family: 'BVP'; font-weight: 600; src: url('${fontDataUrl("BeVietnamPro-SemiBold.ttf")}') format('truetype'); }
  @font-face { font-family: 'BVP'; font-weight: 700; src: url('${fontDataUrl("BeVietnamPro-Bold.ttf")}') format('truetype'); }
  @font-face { font-family: 'BVP'; font-weight: 800; src: url('${fontDataUrl("BeVietnamPro-ExtraBold.ttf")}') format('truetype'); }
  @font-face { font-family: 'Mont'; font-weight: 800; src: url('${fontDataUrl("Montserrat-ExtraBold.ttf")}') format('truetype'); }
  @font-face { font-family: 'Mont'; font-weight: 900; src: url('${fontDataUrl("Montserrat-Black.ttf")}') format('truetype'); }
  @font-face { font-family: 'Playfair'; font-weight: 800; src: url('${fontDataUrl("PlayfairDisplay-ExtraBold.ttf")}') format('truetype'); }
  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }
  html, body { background: transparent !important; overflow: hidden; }

  /* Two-layer zero-stroke-loss 3D Champagne Gold Extruded Span (NO thick black cartoon border, NO gray box!) */
  .gold-wrap {
    position: relative;
    display: inline-block;
    font-family: 'Mont', sans-serif;
    font-weight: 900;
    font-size: 42px;
    letter-spacing: -0.01em;
    margin: 0 2px;
    vertical-align: -1px;
  }
  .gold-back {
    paint-order: stroke fill;
    -webkit-text-stroke: 3.4px #3B2106;
    color: #3B2106;
    text-shadow: 0 2.5px 0 #2B1603, 0 5px 12px rgba(0, 0, 0, 0.62);
  }
  .gold-front {
    position: absolute;
    inset: 0;
    -webkit-text-stroke: 0px transparent !important;
    text-shadow: none !important;
    background: linear-gradient(180deg, #FFFFFA 0%, #FFEC99 28%, #F2AF32 56%, #FFF3C4 80%, #D48A16 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent !important;
  }
`;

function wrapEmGold(lineHtml) {
  return lineHtml.replace(/<em>(.*?)<\/em>/g, (_, inner) =>
    `<span class="gold-wrap"><span class="gold-back">${inner}</span><span class="gold-front">${inner}</span></span>`
  );
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"],
  });
  const page = await browser.newPage();

  // 1. Render 36 Boxless 3D-Extruded Editorial Subtitles (1080x280 transparent sprites — separate line1 & line2 for staggered kinetic animation!)
  await page.setViewport({ width: 1080, height: 280, deviceScaleFactor: 1 });
  const subManifest = [];
  for (let i = 0; i < SUBTITLES.length; i++) {
    const [t0, t1, lines] = SUBTITLES[i];
    const lineFiles = [];
    for (let li = 0; li < lines.length; li++) {
      const html = `<!doctype html><html><head><style>${BASE_CSS}
        .stage {
          width: 1080px; height: 130px;
          display: flex; align-items: center; justify-content: center;
        }
        .sub-line {
          max-width: 940px;
          text-align: center;
          font-family: 'BVP', sans-serif;
          font-size: 38px;
          font-weight: 800;
          line-height: 1.25;
          letter-spacing: -0.015em;
          color: #FFFFFF;
          paint-order: stroke fill;
          -webkit-text-stroke: 2.8px rgba(24, 18, 14, 0.82);
          text-shadow: 0 2px 0 rgba(18, 14, 10, 0.65);
          filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.62)) drop-shadow(0 1px 3px rgba(0, 0, 0, 0.75));
        }
      </style></head><body><div class="stage"><div class="sub-line">${wrapEmGold(lines[li][0])}</div></div></body></html>`;
      await page.setViewport({ width: 1080, height: 130, deviceScaleFactor: 1 });
      await page.setContent(html, { waitUntil: "load" });
      await page.evaluate(() => document.fonts.ready);
      const fn = `sub_${String(i).padStart(2, "0")}_L${li}.png`;
      await page.screenshot({ path: path.join(SPRITES, fn), omitBackground: true });
      lineFiles.push(fn);
    }
    subManifest.push({ index: i, t0, t1, lines: lineFiles });
  }
  fs.writeFileSync(path.join(SPRITES, "subtitles_manifest.json"), JSON.stringify(subManifest, null, 2));
  console.log(`Rendered ${subManifest.length} staggered boxless 3D editorial subtitle groups!`);

  // 2. Render Opening Luxury Hook Header (1080x320)
  await page.setViewport({ width: 1080, height: 320, deviceScaleFactor: 1 });
  const hookHtml = `<!doctype html><html><head><style>${BASE_CSS}
    .stage {
      width: 1080px; height: 320px;
      display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px;
    }
    .eyebrow {
      display: inline-flex; align-items: center; gap: 10px;
      padding: 8px 22px; border-radius: 999px;
      background: linear-gradient(180deg, rgba(14, 62, 38, 0.88), rgba(9, 42, 25, 0.92));
      border: 1.5px solid rgba(246, 212, 128, 0.72);
      box-shadow: 0 8px 22px rgba(0,0,0,0.34);
      font-family: 'BVP', sans-serif; font-weight: 800; font-size: 21px;
      letter-spacing: 0.06em; color: #FFF8E6;
    }
    .eyebrow img { width: 28px; height: 28px; border-radius: 50%; background: #fff; padding: 1px; }
    .hero-wrap { position: relative; display: inline-block; font-family: 'Mont', sans-serif; font-weight: 900; font-size: 52px; letter-spacing: 0.01em; }
    .hero-back {
      paint-order: stroke fill;
      -webkit-text-stroke: 6px rgba(24, 14, 6, 0.85);
      color: #2A1808;
      filter: drop-shadow(0 8px 20px rgba(0,0,0,0.52));
    }
    .hero-front {
      position: absolute; inset: 0;
      background: linear-gradient(180deg, #FFFDF4 0%, #FCE38A 26%, #DA9A2E 54%, #FFF0BA 78%, #A86B10 100%);
      -webkit-background-clip: text; background-clip: text; color: transparent;
    }
  </style></head><body><div class="stage">
    <div class="eyebrow"><img src="${logoDataUrl}"/><span>THỰC PHẨM F20 × YẾN SÀO SKA NEST</span></div>
    <div class="hero-wrap"><span class="hero-back">SET QUÀ TRI ÂN 20/11</span><span class="hero-front">SET QUÀ TRI ÂN 20/11</span></div>
  </div></body></html>`;
  await page.setContent(hookHtml, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(SPRITES, "hook_header.png"), omitBackground: true });

  // 3. Render 7 PIP / Loupe Caption Pills (380x64)
  await page.setViewport({ width: 380, height: 64, deviceScaleFactor: 1 });
  for (let i = 0; i < PIP_LABELS.length; i++) {
    const h = `<!doctype html><html><head><style>${BASE_CSS}
      .stage { width: 380px; height: 64px; display: flex; align-items: center; justify-content: center; }
      .pill {
        padding: 7px 18px; border-radius: 999px;
        background: linear-gradient(180deg, rgba(16, 58, 36, 0.92), rgba(10, 38, 23, 0.95));
        border: 1.5px solid rgba(244, 210, 128, 0.82);
        box-shadow: 0 5px 14px rgba(0,0,0,0.35);
        font-family: 'BVP', sans-serif; font-weight: 800; font-size: 18px;
        letter-spacing: 0.03em; color: #FFF9EB; white-space: nowrap;
      }
    </style></head><body><div class="stage"><div class="pill">${PIP_LABELS[i]}</div></div></body></html>`;
    await page.setContent(h, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(SPRITES, `pip_${i}.png`), omitBackground: true });
  }

  // 4. Render 4 Frosted Ingredient Pills (460x72)
  await page.setViewport({ width: 460, height: 72, deviceScaleFactor: 1 });
  for (let i = 0; i < ING_ITEMS.length; i++) {
    const it = ING_ITEMS[i];
    const h = `<!doctype html><html><head><style>${BASE_CSS}
      .stage { width: 460px; height: 72px; display: flex; align-items: center; justify-content: center; }
      .ing {
        display: inline-flex; align-items: center; gap: 10px;
        padding: 9px 20px; border-radius: 999px;
        background: rgba(20, 22, 26, 0.74);
        border: 1.5px solid rgba(250, 220, 148, 0.68);
        box-shadow: 0 6px 18px rgba(0,0,0,0.32);
        font-family: 'BVP', sans-serif; font-weight: 800; font-size: 20px;
        color: #FFFDF7; white-space: nowrap;
      }
      .dot { width: 11px; height: 11px; border-radius: 50%; background: ${it.dot}; box-shadow: 0 0 8px ${it.dot}; }
    </style></head><body><div class="stage"><div class="ing"><span class="dot"></span><span>${it.text}</span></div></div></body></html>`;
    await page.setContent(h, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(SPRITES, `ing_${i}.png`), omitBackground: true });
  }

  // 5. Render Luxury Editorial End-Card Base (1080x1920)
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  const endHtml = `<!doctype html><html><head><style>${BASE_CSS}
    .card {
      width: 1080px; height: 1920px;
      background: radial-gradient(circle at 50% 34%, #1A5C3A 0%, #0D3822 52%, #072013 100%);
      display: flex; flex-direction: column; align-items: center; padding-top: 175px;
      color: #fff; font-family: 'BVP', sans-serif;
    }
    .logo-ring {
      width: 126px; height: 126px; border-radius: 50%; background: #fff; padding: 6px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.38), 0 0 0 3px rgba(244, 210, 128, 0.78);
      margin-bottom: 530px;
    }
    .logo-ring img { width: 100%; height: 100%; object-fit: contain; border-radius: 50%; }
    .brand {
      font-family: 'Mont', sans-serif; font-weight: 900; font-size: 42px; letter-spacing: 0.02em;
      background: linear-gradient(180deg, #FFFDF4 0%, #FCE38A 35%, #DA9A2E 65%, #FFF0BA 95%);
      -webkit-background-clip: text; background-clip: text; color: transparent;
      filter: drop-shadow(0 4px 12px rgba(0,0,0,0.45));
      margin-bottom: 10px;
    }
    .sub { font-weight: 700; font-size: 25px; color: #E4F5EC; letter-spacing: 0.08em; margin-bottom: 34px; }
    .box {
      width: 820px; padding: 26px 34px; border-radius: 26px;
      background: rgba(255, 255, 255, 0.07);
      border: 1.5px solid rgba(244, 210, 128, 0.48);
      box-shadow: 0 14px 36px rgba(0,0,0,0.32);
      text-align: center; display: flex; flex-direction: column; gap: 11px;
    }
    .hl { font-weight: 800; font-size: 29px; color: #FFE394; letter-spacing: 0.02em; }
    .addr { font-weight: 600; font-size: 22px; color: #F2F9F5; line-height: 1.45; }
    .web { font-weight: 700; font-size: 22px; color: #9EF0C0; margin-top: 4px; }
  </style></head><body><div class="card">
    <div class="logo-ring"><img src="${logoDataUrl}"/></div>
    <div class="brand">THỰC PHẨM F20 × SKA NEST</div>
    <div class="sub">SET QUÀ TẶNG TRI ÂN 20/11</div>
    <div class="box">
      <div class="hl">Hotline / Zalo: 0979 512 289 • 0706 001 626</div>
      <div class="addr">CS1: 149 Trần Nhật Duật, TP. Nha Trang</div>
      <div class="addr">CS2: 17/3 Điện Biên Phủ, Vĩnh Hòa, Nha Trang</div>
      <div class="web">Website: thucphamf20.com</div>
    </div>
  </div></body></html>`;
  await page.setContent(endHtml, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(SPRITES, "endcard_bg.png") });

  await browser.close();
  console.log("ALL V7 CHROME CSS/SVG TYPOGRAPHY SPRITES RENDERED!");
})();
