import shutil
import subprocess
from pathlib import Path
import cv2
import numpy as np

BASE = Path(r"d:\AI\full studio\projects\feelchicken_micay_muc_chay")
ASSETS = BASE / "assets"
OUT_DIR = BASE / "XUAT_MI_CAY_MUC_THAT_CHAY"
GRID_DIR = OUT_DIR / "01_Bo_4_Tam_Facebook_Grid"
SINGLE_DIR = OUT_DIR / "02_Poster_Don_4x5_Chay_Ads"
GRID_DIR.mkdir(parents=True, exist_ok=True)
SINGLE_DIR.mkdir(parents=True, exist_ok=True)

CUT_V7 = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\cutouts_v7")
ART_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856")
FONT_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def u(p: Path) -> str:
    return p.resolve().as_uri()


f_baloo = u(FONT_DIR / "Baloo2-ExtraBold.ttf")
f_paytone = u(FONT_DIR / "PaytoneOne-Regular.ttf")
f_anton = u(FONT_DIR / "Anton-Regular.ttf")
f_bvp_eb = u(FONT_DIR / "BeVietnamPro-ExtraBold.ttf")
f_bvp_b = u(FONT_DIR / "BeVietnamPro-Bold.ttf")

FONTS_CSS = f"""
@font-face {{ font-family: 'Baloo'; src: url('{f_baloo}') format('truetype'); font-weight: 800; }}
@font-face {{ font-family: 'Paytone'; src: url('{f_paytone}') format('truetype'); font-weight: 400; }}
@font-face {{ font-family: 'Anton'; src: url('{f_anton}') format('truetype'); font-weight: 400; }}
@font-face {{ font-family: 'BVP'; src: url('{f_bvp_b}') format('truetype'); font-weight: 700; }}
@font-face {{ font-family: 'BVP'; src: url('{f_bvp_eb}') format('truetype'); font-weight: 800; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
"""

# Custom Illustrator-grade vector Flame & Chili SVG icons (zero flat OS emojis!)
FLAME_ICON = """<svg width="32" height="36" viewBox="0 0 32 36" fill="none" style="display:inline-block;vertical-align:-6px;flex-shrink:0;">
  <path d="M17.5 1C17.5 1 26 9.2 26 18.5C26 25.8 20.8 33 14.5 34.5C17.2 31.2 17.8 26.8 15.5 23.8C13.8 26.5 11.2 27.6 10.5 31.2C5.5 28.4 3 23.2 3 17.8C3 11.4 7.8 6.5 10.2 4.5C9.6 8.2 11.4 10.8 13.2 11.5C12.2 7.2 14.5 3.2 17.5 1Z" fill="url(#flg)"/>
  <path d="M16 14C16 14 21 18.8 21 24C21 28.4 17.8 32.5 14 33.5C10.2 32.5 8.5 28.8 8.5 25C8.5 21.2 12.2 17.2 16 14Z" fill="#FFF380"/>
  <defs><linearGradient id="flg" x1="15" y1="1" x2="15" y2="35" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="#FFE838"/><stop offset="50%" stop-color="#FF6A00"/><stop offset="100%" stop-color="#D90B14"/>
  </linearGradient></defs>
</svg>"""

CHILI_ICON = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" style="display:inline-block;vertical-align:-5px;flex-shrink:0;">
  <path d="M24 7C26.5 4.5 28.5 4 30 4.5" stroke="#4ADE80" stroke-width="3.2" stroke-linecap="round"/>
  <path d="M21 6.5C24.5 8.5 26 13.5 22.5 19.5C18.5 26.2 10.5 29.5 3.5 28.5C8.5 25.5 12.5 21.2 15.2 15.5C17.2 11.2 18.2 7.5 21 6.5Z" fill="url(#chg)" stroke="#FFE566" stroke-width="1.4"/>
  <defs><linearGradient id="chg" x1="25" y1="7" x2="4" y2="28" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="#FF4D2A"/><stop offset="60%" stop-color="#D90D15"/><stop offset="100%" stop-color="#8A0409"/>
  </linearGradient></defs>
</svg>"""

STEAM_FIRE_SVG = """
<svg viewBox="0 0 420 220" fill="none" style="position:absolute;top:-145px;left:50%;transform:translateX(-50%);width:390px;height:195px;pointer-events:none;z-index:2;">
  <path d="M105 205 C72 155, 138 110, 102 42 C88 18, 118 4, 125 0" stroke="url(#stf)" stroke-width="18" stroke-linecap="round"/>
  <path d="M210 212 C175 148, 252 102, 212 28 C196 8, 224 2, 232 0" stroke="url(#stf)" stroke-width="24" stroke-linecap="round"/>
  <path d="M315 202 C285 152, 348 112, 315 48" stroke="url(#stf)" stroke-width="17" stroke-linecap="round"/>
  <circle cx="85" cy="95" r="4.5" fill="#FFB800" opacity="0.85"/>
  <circle cx="275" cy="72" r="5.5" fill="#FF6B00" opacity="0.9"/>
  <circle cx="345" cy="120" r="3.8" fill="#FFE64D" opacity="0.85"/>
  <circle cx="155" cy="52" r="4.2" fill="#FF8800" opacity="0.8"/>
  <defs>
    <linearGradient id="stf" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="#FF9E44" stop-opacity="0.0"/>
      <stop offset="42%" stop-color="#FFF2DF" stop-opacity="0.62"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.0"/>
    </linearGradient>
  </defs>
</svg>
"""

EMBERS_OVERLAY_SVG = """
<svg viewBox="0 0 1080 1080" fill="none" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:7;">
  <circle cx="110" cy="340" r="5" fill="#FFD438" opacity="0.85"/>
  <circle cx="165" cy="740" r="6.5" fill="#FF6A00" opacity="0.8"/>
  <circle cx="960" cy="310" r="5.5" fill="#FFB800" opacity="0.88"/>
  <circle cx="920" cy="690" r="7" fill="#FF5500" opacity="0.78"/>
  <circle cx="840" cy="240" r="4" fill="#FFF078" opacity="0.9"/>
  <circle cx="210" cy="255" r="4.2" fill="#FF8C00" opacity="0.82"/>
</svg>
"""

ASCII_TMP = BASE / "tmp_render"
ASCII_TMP.mkdir(parents=True, exist_ok=True)

# Clean any gray/white marble shadow below y > 77% on cut_1muc_hero45.png (keep ONLY sleek dark black underplate V <= 95!)
_c1 = cv2.imread(str(ASSETS / "cut_1muc_hero45.png"), cv2.IMREAD_UNCHANGED)
if _c1 is not None:
    _h1, _w1 = _c1.shape[:2]
    _hsv1 = cv2.cvtColor(_c1[:, :, :3], cv2.COLOR_BGR2HSV)
    _yy1, _xx1 = np.mgrid[0:_h1, 0:_w1]
    _pale_under = (_yy1 > int(_h1 * 0.77)) & (_xx1 < int(_w1 * 0.68)) & (_hsv1[:, :, 2] > 92) & (_hsv1[:, :, 1] < 58)
    _a1 = _c1[:, :, 3].copy()
    _a1[_pale_under] = 0
    _nl, _lb, _st, _ = cv2.connectedComponentsWithStats((_a1 > 30).astype(np.uint8))
    if _nl > 1:
        _best = 1 + int(np.argmax(_st[1:, cv2.CC_STAT_AREA]))
        _a1 = np.minimum(_a1, cv2.GaussianBlur((_lb == _best).astype(np.uint8) * 255, (5, 5), 1.0))
    _c1[:, :, 3] = _a1
    cv2.imwrite(str(ASSETS / "cut_1muc_hero45.png"), _c1)

# Smoothly round any flat camera-frame edge on the far-left handle tip (x < 28px) across all pot cutouts!
for _cn in ["cut_2muc_hero45.png", "cut_2muc_top.png", "cut_1muc_top.png", "cut_1muc_hero45.png"]:
    _cp = ASSETS / _cn
    _im = cv2.imread(str(_cp), cv2.IMREAD_UNCHANGED)
    if _im is None:
        continue
    _ch, _cw = _im.shape[:2]
    _al = _im[:, :, 3]
    _ys_left = np.where(_al[:, :14].max(axis=1) > 100)[0]
    if len(_ys_left) > 30:
        _yc = 0.5 * (_ys_left.min() + _ys_left.max())
        _yr = max(20.0, 0.52 * (_ys_left.max() - _ys_left.min()))
        _yy, _xx = np.mgrid[0:_ch, 0:_cw]
        # Parabolic arc inset on left 26px so handle ear curves naturally instead of vertical straight cut!
        _curve_x = 24.0 * np.square(np.clip((_yy - _yc) / _yr, -1.5, 1.5))
        _fade = np.clip((_xx - _curve_x) / 6.0, 0.0, 1.0)
        _only_left = (_xx < 34).astype(np.float32)
        _new_al = _al.astype(np.float32) * (1.0 - _only_left + _only_left * _fade)
        _im[:, :, 3] = np.clip(_new_al, 0, 255).astype(np.uint8)
        cv2.imwrite(str(_cp), _im)

# Also crop the badass Flame-Headband Chick Mascot from fc_muc_bg_wide.png for Card 04 Check-In!
_bgw = cv2.imread(str(ASSETS / "fc_muc_bg_wide.png"), cv2.IMREAD_COLOR)
if _bgw is not None:
    _bh, _bw = _bgw.shape[:2]
    # Right side chick + roaring fire stage crop (square crop around chick & dark table)
    _sq_sz = _bh
    _x0 = max(0, _bw - _sq_sz)
    cv2.imwrite(str(ASSETS / "fc_muc_bg_chick_sq.jpg"), _bgw[:, _x0 : _x0 + _sq_sz], [int(cv2.IMWRITE_JPEG_QUALITY), 96])


def render_html(slug: str, html: str, w: int, h: int, out_png: Path) -> np.ndarray:
    hf = ASCII_TMP / f"{slug}.html"
    tf_png = ASCII_TMP / f"{slug}.png"
    hf.write_text(html, encoding="utf-8")
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={w},{h}",
            f"--screenshot={tf_png}",
            hf.resolve().as_uri(),
        ],
        check=True,
    )
    out_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tf_png, out_png)
    return cv2.imread(str(tf_png))


# ==============================================================================
# CARD 01 (2160 x 1080): HERO BANNER 2:1 — MÌ CAY MỰC KHỔNG LỒ (ZERO PRICE!)
# ==============================================================================
banner_2x1_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
html, body {{ width:2160px; height:1080px; overflow:hidden; font-family:'BVP',sans-serif; background:#140302; }}
.stage {{
  position:relative; width:2160px; height:1080px;
  background: url('{u(ASSETS / "fc_muc_bg_wide.png")}') center/cover no-repeat;
}}
/* Deep dramatic top readability vignette on left/center while keeping right flame-headband chick 100% bright & unobstructed! */
.veil {{
  position:absolute; inset:0;
  background:
    radial-gradient(ellipse at 34% 20%, rgba(22, 2, 1, 0.84) 0%, rgba(30, 3, 2, 0.38) 42%, transparent 64%),
    linear-gradient(90deg, rgba(16, 2, 1, 0.36) 0%, rgba(16, 2, 1, 0.12) 58%, transparent 72%);
}}
.logo-box {{
  position:absolute; top:18px; left:30px; width:184px; height:184px; z-index:9;
  filter: drop-shadow(0 10px 22px rgba(0,0,0,0.72));
  transform: rotate(-4deg);
}}
.logo-box img {{ width:100%; height:100%; object-fit:contain; }}

/* Bottom-Right Hype Burst right on the slate table under the chick (NO PRICE — chick's head & flame bow 100% clear!) */
.hype-burst {{
  position:absolute; bottom:108px; right:44px; z-index:9;
  background: linear-gradient(135deg, #FFF05A 0%, #FF9900 55%, #FF4500 100%);
  border: 5px solid #FFFBE0;
  border-radius: 32px;
  padding: 14px 36px;
  text-align:center;
  transform: rotate(-2deg);
  box-shadow: 0 16px 32px rgba(0,0,0,0.65), 0 0 28px rgba(255,115,0,0.52);
}}
.hype-burst .hb1 {{ font-size:23px; font-weight:800; color:#6E0408; letter-spacing:1px; }}
.hype-burst .hb2 {{ font-family:'Baloo',sans-serif; font-size:54px; color:#A8060C; line-height:0.95; text-shadow:0 3px 0 #FFFFFF; }}
.hype-burst .hb3 {{ font-size:22px; font-weight:800; color:#FFFFFF; background:#9E060C; border-radius:99px; padding:4px 20px; margin-top:6px; display:inline-block; }}

.hero-head {{
  position:absolute; top:16px; left:212px; width:1185px; text-align:center; z-index:8;
}}
.trend-pill {{
  display:inline-flex; align-items:center; gap:10px;
  background: linear-gradient(90deg, #8F050B 0%, #D9141C 50%, #8F050B 100%);
  border: 3.5px solid #FFE14D;
  color: #FFF8D6;
  font-size: 25.5px; font-weight: 800;
  padding: 7px 32px; border-radius: 99px;
  letter-spacing: 0.5px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.55), 0 0 22px rgba(255,80,0,0.45);
}}
.sub-ribbon {{
  display:inline-flex; align-items:center; gap:12px;
  background: linear-gradient(90deg, #FFFDF2 0%, #FFE27A 50%, #FFFDF2 100%);
  border: 4px solid #C80E16;
  color: #7D050A;
  font-family: 'Baloo', sans-serif;
  font-size: 31px;
  padding: 5px 34px;
  border-radius: 99px;
  box-shadow: 0 12px 26px rgba(0,0,0,0.52);
  margin-top: -12px;
}}

/* Dual Giant Real Squid Noodle Pots grounded cleanly BELOW headline & LEFT of glowing chili chick! */
.pots-zone {{
  position:absolute; bottom:94px; left:36px; width:1410px; height:540px; z-index:6;
}}
.fire-under-glow {{
  position:absolute; bottom:6px; left:40px; right:40px; height:160px;
  background: radial-gradient(ellipse at 50% 60%, rgba(255, 94, 0, 0.58) 0%, rgba(215, 20, 10, 0.25) 55%, transparent 80%);
  filter: blur(14px); pointer-events:none;
}}
.pot-hero-main {{
  position:absolute; left:10px; bottom:8px; width:700px; z-index:7;
  display:flex; flex-direction:column; align-items:center;
}}
.pot-hero-main img {{
  width:100%; height:auto; object-fit:contain;
  filter: drop-shadow(0 26px 26px rgba(0,0,0,0.80)) drop-shadow(0 -4px 20px rgba(255,102,0,0.34));
}}
.pot-hero-sec {{
  position:absolute; right:10px; bottom:12px; width:640px; z-index:6;
  display:flex; flex-direction:column; align-items:center;
}}
.pot-hero-sec img {{
  width:100%; height:auto; object-fit:contain;
  filter: drop-shadow(0 26px 26px rgba(0,0,0,0.76)) drop-shadow(0 -4px 18px rgba(255,94,0,0.32));
}}
.pot-pill-gold {{
  margin-top:-22px; position:relative; z-index:9;
  background: linear-gradient(90deg, #FFE44D 0%, #FF9900 100%);
  border: 4px solid #FFFFFF; color:#6E0409;
  font-family:'Baloo',sans-serif; font-size:34px; padding:6px 36px; border-radius:99px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.58); white-space:nowrap;
}}
.pot-pill-red {{
  margin-top:-20px; position:relative; z-index:9;
  background: linear-gradient(90deg, #9E060D 0%, #E01922 50%, #9E060D 100%);
  border: 3.5px solid #FFE252; color:#FFFDF2;
  font-family:'Baloo',sans-serif; font-size:31px; padding:6px 32px; border-radius:99px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.55); white-space:nowrap;
}}

.mascot-tag {{
  position:absolute; bottom:112px; right:42px; z-index:9;
  background: linear-gradient(135deg, #B80B12 0%, #FF3B1D 100%);
  border: 4px solid #FFE459; border-radius:99px;
  padding: 8px 30px; font-family:'Baloo',sans-serif; font-size:31px; color:#FFFDF4;
  box-shadow: 0 12px 24px rgba(0,0,0,0.58);
}}

.footer-bar {{
  position:absolute; bottom:0; left:0; right:0; height:88px; z-index:10;
  background: linear-gradient(90deg, #7A0409 0%, #BD0F17 50%, #7A0409 100%);
  border-top: 4px solid #FFD54F;
  display:flex; align-items:center; justify-content:space-between;
  padding: 0 52px; color:#FFFFFF;
}}
.fb-brand {{ font-family:'Baloo',sans-serif; font-size:42px; color:#FFE44D; letter-spacing:0.5px; }}
.fb-info  {{ font-size:25px; font-weight:800; color:#FFF9E8; }}
.fb-hot   {{ background:linear-gradient(90deg,#FFE84D,#FFA800); color:#7D050A; font-family:'Baloo',sans-serif; font-size:32px; padding:6px 28px; border-radius:99px; border:2.5px solid #FFFFFF; }}
</style></head><body>
<div class="stage">
  <div class="veil"></div>
  <div class="logo-box"><img src="{u(CUT_V7 / 'logo.png')}" /></div>

  <div class="hype-burst">
    <div class="hb1">★ SIÊU PHẨM MỚI ★</div>
    <div class="hb2">7 CẤP ĐỘ CAY</div>
    <div class="hb3">THÁCH THỨC VỊ GIÁC!</div>
  </div>

  <div class="hero-head">
    <div class="trend-pill">{FLAME_ICON} MÓN HOT TREND ĐÃ CÓ MẶT TẠI NHA TRANG! {FLAME_ICON}</div>
    <svg width="1185" height="216" viewBox="0 0 1185 216" style="margin-top:2px;overflow:visible;">
      <defs>
        <linearGradient id="moltenGold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FFFBE0"/>
          <stop offset="32%" stop-color="#FFE44D"/>
          <stop offset="72%" stop-color="#FF9900"/>
          <stop offset="100%" stop-color="#FF4800"/>
        </linearGradient>
        <linearGradient id="lavaRed" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FF6A3D"/>
          <stop offset="52%" stop-color="#E0121B"/>
          <stop offset="100%" stop-color="#8A040A"/>
        </linearGradient>
        <filter id="fireSh" x="-12%" y="-18%" width="124%" height="145%">
          <feDropShadow dx="0" dy="12" stdDeviation="9" flood-color="#1A0201" flood-opacity="0.88"/>
          <feDropShadow dx="0" dy="0" stdDeviation="16" flood-color="#FF5500" flood-opacity="0.45"/>
        </filter>
      </defs>
      <g filter="url(#fireSh)" font-family="'Baloo', sans-serif" font-weight="800" text-anchor="middle">
        <text x="592" y="102" font-size="110" fill="#4A0306" stroke="#4A0306" stroke-width="28" stroke-linejoin="round" paint-order="stroke fill">MÌ CAY MỰC KHỔNG LỒ</text>
        <text x="592" y="94"  font-size="110" fill="url(#moltenGold)" stroke="#FFFFFF" stroke-width="10" stroke-linejoin="round" paint-order="stroke fill">MÌ CAY MỰC KHỔNG LỒ</text>

        <text x="592" y="192" font-size="74" fill="#FFE44D" stroke="#FFE44D" stroke-width="20" stroke-linejoin="round" paint-order="stroke fill">MỰC ỐNG NGUYÊN CON • CAY BÙNG VỊ GIÁC!</text>
        <text x="592" y="187" font-size="74" fill="url(#lavaRed)" stroke="#FFFDF5" stroke-width="6.5" stroke-linejoin="round" paint-order="stroke fill">MỰC ỐNG NGUYÊN CON • CAY BÙNG VỊ GIÁC!</text>
      </g>
    </svg>
    <div class="sub-ribbon">{CHILI_ICON} Mực Tươi Giòn Ngọt Ngập Nồi • Nước Dùng Kim Chi Sôi Sùng Sục!</div>
  </div>

  <div class="pots-zone">
    <div class="fire-under-glow"></div>
    <div class="pot-hero-main">
      {STEAM_FIRE_SVG}
      <img src="{u(ASSETS / 'cut_2muc_hero45.png')}" />
      <div class="pot-pill-gold">★ Mực Ống Nguyên Con Căng Mọng ★</div>
    </div>
    <div class="pot-hero-sec">
      {STEAM_FIRE_SVG}
      <img src="{u(ASSETS / 'cut_1muc_hero45.png')}" />
      <div class="pot-pill-red">★ Mì Hàn Dai Ngon • Full Topping ★</div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="fb-brand">FEEL CHICKEN</div>
    <div class="fb-info">CS1: 38 Nguyễn Đình Chiểu &nbsp;|&nbsp; CS2: 35 Trần Hữu Duyệt &nbsp;•&nbsp; Mở cửa: 10:00 – 22:00</div>
    <div class="fb-hot">Đặt Món / Ship Nóng: 0796 601 106</div>
  </div>
</div>
</body></html>"""


# ==============================================================================
# HELPER FOR 3 EXPLOSIVE SQUARE CARDS 1:1 (1080 x 1080 — ZERO PRICE!)
# ==============================================================================
def build_fiery_square_card(
    bg_png: Path,
    cutout_png: Path,
    top_kicker: str,
    big_line1: str,
    big_line2: str,
    desc_text: str,
    cta_badge: str,
    show_7level_meter: bool = False,
    pot_scale_w: int = 880,
    pot_top: int = 215,
) -> str:
    meter_html = ""
    if show_7level_meter:
        bars = "".join(
            f'<div style="padding:5px 14px;border-radius:12px;font-family:Baloo,sans-serif;font-size:22px;'
            f'background:{bgc};color:#FFFFFF;border:2px solid #FFE566;box-shadow:0 4px 10px rgba(0,0,0,0.4);">CẤP {lv}</div>'
            for lv, bgc in [
                (1, "#F59E0B"), (2, "#EA580C"), (3, "#DC2626"),
                (4, "#B91C1C"), (5, "#991B1B"), (6, "#7F1D1D"), (7, "#450A0A"),
            ]
        )
        meter_html = f'<div style="position:absolute;top:148px;left:50%;transform:translateX(-50%);display:flex;gap:8px;z-index:8;white-space:nowrap;">{bars}</div>'

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    {FONTS_CSS}
    html, body {{ width:1080px; height:1080px; overflow:hidden; font-family:'BVP',sans-serif; background:#140302; }}
    .card {{
      position:relative; width:1080px; height:1080px;
      background: url('{u(bg_png)}') center/cover no-repeat;
    }}
    .shade {{
      position:absolute; inset:0;
      background:
        radial-gradient(circle at 50% 52%, rgba(255, 94, 0, 0.24) 0%, transparent 62%),
        linear-gradient(180deg, rgba(22,2,1,0.82) 0%, rgba(20,2,1,0.18) 30%, rgba(20,2,1,0.18) 64%, rgba(18,2,1,0.94) 100%);
    }}
    .border-glow {{
      position:absolute; inset:18px; border:4px solid rgba(255, 210, 72, 0.85); border-radius:32px;
      box-shadow: inset 0 0 28px rgba(255, 72, 0, 0.32); pointer-events:none; z-index:10;
    }}
    .top-row {{
      position:absolute; top:36px; left:42px; right:42px; z-index:9;
      display:flex; align-items:center; justify-content:space-between;
    }}
    .kicker {{
      display:inline-flex; align-items:center; gap:10px;
      background: linear-gradient(90deg, #9E060C 0%, #E61E27 50%, #9E060C 100%);
      border: 3px solid #FFE252; color:#FFF9DB;
      font-size:25px; font-weight:800; padding:8px 28px; border-radius:99px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.55);
    }}
    .mini-logo {{ width:128px; height:128px; filter:drop-shadow(0 8px 16px rgba(0,0,0,0.65)); transform:rotate(3deg); }}

    .pot-wrap {{
      position:absolute; top:{pot_top}px; left:50%; transform:translateX(-50%);
      width:{pot_scale_w}px; z-index:6; display:flex; justify-content:center;
    }}
    .pot-wrap img {{
      width:100%; height:auto; object-fit:contain;
      filter: drop-shadow(0 28px 28px rgba(0,0,0,0.82)) drop-shadow(0 0 26px rgba(255,90,0,0.38));
    }}

    .bot-panel {{
      position:absolute; bottom:38px; left:42px; right:42px; z-index:9;
      display:flex; flex-direction:column; align-items:center; text-align:center;
    }}
    .cta-pill {{
      background: linear-gradient(90deg, #FFE642 0%, #FF9900 100%);
      border: 3.5px solid #FFFFFF; color:#6E0409;
      font-family:'Baloo',sans-serif; font-size:29px; padding:5px 34px; border-radius:99px;
      box-shadow: 0 10px 22px rgba(0,0,0,0.58); margin-bottom:6px;
    }}
    .b-desc {{
      font-size:25.5px; font-weight:700; color:#FFF4DC; line-height:1.26;
      text-shadow: 0 3px 10px rgba(0,0,0,0.85); margin-top:4px;
    }}
    </style></head><body>
    <div class="card">
      <div class="shade"></div>
      {EMBERS_OVERLAY_SVG}
      <div class="border-glow"></div>

      <div class="top-row">
        <div class="kicker">{FLAME_ICON} {top_kicker}</div>
        <img class="mini-logo" src="{u(CUT_V7 / 'logo.png')}" />
      </div>
      {meter_html}

      <div class="pot-wrap">
        {STEAM_FIRE_SVG}
        <img src="{u(cutout_png)}" />
      </div>

      <div class="bot-panel">
        <div class="cta-pill">{cta_badge}</div>
        <svg width="990" height="{158 if big_line2 else 92}" viewBox="0 0 990 {158 if big_line2 else 92}" style="overflow:visible;">
          <defs>
            <linearGradient id="sqGold" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#FFFCE0"/><stop offset="45%" stop-color="#FFE042"/><stop offset="100%" stop-color="#FF7B00"/>
            </linearGradient>
            <filter id="sqSh" x="-12%" y="-18%" width="124%" height="145%">
              <feDropShadow dx="0" dy="8" stdDeviation="7" flood-color="#140100" flood-opacity="0.9"/>
            </filter>
          </defs>
          <g filter="url(#sqSh)" font-family="'Baloo',sans-serif" font-weight="800" text-anchor="middle">
            <text x="495" y="74" font-size="78" fill="#4F0307" stroke="#4F0307" stroke-width="22" stroke-linejoin="round" paint-order="stroke fill">{big_line1}</text>
            <text x="495" y="68" font-size="78" fill="url(#sqGold)" stroke="#FFFFFF" stroke-width="7.5" stroke-linejoin="round" paint-order="stroke fill">{big_line1}</text>
            {f'<text x="495" y="146" font-size="68" fill="#FFE44D" stroke="#FFE44D" stroke-width="18" stroke-linejoin="round" paint-order="stroke fill">{big_line2}</text><text x="495" y="141" font-size="68" fill="#E0141C" stroke="#FFFFFF" stroke-width="6.5" stroke-linejoin="round" paint-order="stroke fill">{big_line2}</text>' if big_line2 else ''}
          </g>
        </svg>
        <div class="b-desc">{desc_text}</div>
      </div>
    </div>
    </body></html>"""


# ==============================================================================
# STANDALONE 4:5 VERTICAL MEGA-POSTER (1440 x 1800 — ZERO PRICE!)
# ==============================================================================
poster_4x5_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
html, body {{ width:1440px; height:1800px; overflow:hidden; font-family:'BVP',sans-serif; background:#140302; }}
.stage {{
  position:relative; width:1440px; height:1800px;
  background: url('{u(ASSETS / "fc_muc_bg_fire1.png")}') center/cover no-repeat;
}}
.veil {{
  position:absolute; inset:0;
  background:
    radial-gradient(ellipse at 50% 18%, rgba(25,2,1,0.86) 0%, rgba(25,2,1,0.35) 55%, transparent 80%),
    radial-gradient(circle at 50% 62%, rgba(255,94,0,0.34) 0%, transparent 58%),
    linear-gradient(180deg, rgba(18,2,1,0.72) 0%, transparent 36%, rgba(18,2,1,0.22) 72%, rgba(18,2,1,0.92) 100%);
}}
.frame {{
  position:absolute; inset:24px; border:4px solid rgba(255,214,74,0.78); border-radius:38px; pointer-events:none; z-index:10;
}}
.top-bar {{
  position:absolute; top:48px; left:58px; right:58px; z-index:9;
  display:flex; align-items:center; justify-content:space-between;
}}
.logo {{ width:195px; height:195px; filter:drop-shadow(0 10px 20px rgba(0,0,0,0.68)); transform:rotate(-4deg); }}
.hot-badge {{
  background: linear-gradient(135deg, #FFF059 0%, #FF9500 60%, #FF3D00 100%);
  border: 5px solid #FFFFFF; border-radius:30px; padding: 14px 34px; text-align:center;
  transform: rotate(3deg); box-shadow: 0 14px 28px rgba(0,0,0,0.58);
}}
.hot-badge .t1 {{ font-size:23px; font-weight:800; color:#6E0408; }}
.hot-badge .t2 {{ font-family:'Baloo',sans-serif; font-size:52px; color:#A8060C; line-height:0.95; text-shadow:0 3px 0 #FFFFFF; }}

.head-zone {{
  position:absolute; top:198px; left:50%; transform:translateX(-50%); width:1320px; text-align:center; z-index:8;
}}
.nhatrang-pill {{
  display:inline-flex; align-items:center; gap:12px;
  background: linear-gradient(90deg, #8F050B 0%, #E0161F 50%, #8F050B 100%);
  border: 4px solid #FFE252; color:#FFF9DB;
  font-size:32px; font-weight:800; padding:10px 44px; border-radius:99px;
  box-shadow: 0 12px 26px rgba(0,0,0,0.58);
}}
.usp-pills {{
  display:flex; justify-content:center; gap:18px; margin-top:2px;
}}
.u-pill {{
  background: rgba(255, 248, 225, 0.96); border:3.5px solid #D9141C; color:#7A050A;
  font-family:'Baloo',sans-serif; font-size:32px; padding:6px 32px; border-radius:99px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.48);
}}

.hero-pot {{
  position:absolute; bottom:212px; left:50%; transform:translateX(-50%);
  width:1135px; z-index:6; display:flex; flex-direction:column; align-items:center;
}}
.hero-pot img {{
  width:100%; height:auto; object-fit:contain;
  filter: drop-shadow(0 34px 34px rgba(0,0,0,0.86)) drop-shadow(0 0 34px rgba(255,94,0,0.42));
}}

.bot-cta {{
  position:absolute; bottom:128px; left:50%; transform:translateX(-50%); z-index:9;
  background: linear-gradient(90deg, #FFE642 0%, #FFA200 100%);
  border: 4.5px solid #FFFFFF; border-radius:99px; padding: 12px 52px; white-space:nowrap;
  font-family:'Baloo',sans-serif; font-size:38px; color:#6E0409;
  box-shadow: 0 14px 28px rgba(0,0,0,0.65);
}}
.foot {{
  position:absolute; bottom:24px; left:48px; right:48px; height:84px; z-index:9;
  background: linear-gradient(90deg, #85050A 0%, #C8121A 50%, #85050A 100%);
  border: 3.5px solid #FFD54F; border-radius:99px;
  display:flex; align-items:center; justify-content:space-between; padding:0 42px; color:#FFF9E8;
}}
</style></head><body>
<div class="stage">
  <div class="veil"></div>
  <div class="frame"></div>

  <div class="top-bar">
    <img class="logo" src="{u(CUT_V7 / 'logo.png')}" />
    <div class="hot-badge">
      <div class="t1">★ SIÊU PHẨM MỚI ★</div>
      <div class="t2">HOT TREND!</div>
    </div>
  </div>

  <div class="head-zone">
    <div class="nhatrang-pill">{FLAME_ICON} MÓN HOT TREND ĐÃ CÓ MẶT TẠI NHA TRANG! {FLAME_ICON}</div>
    <svg width="1320" height="310" viewBox="0 0 1320 310" style="margin-top:6px;overflow:visible;">
      <defs>
        <linearGradient id="vGold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FFFCE0"/><stop offset="38%" stop-color="#FFE247"/><stop offset="78%" stop-color="#FF9100"/><stop offset="100%" stop-color="#FF4500"/>
        </linearGradient>
        <linearGradient id="vRed" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FF6A3D"/><stop offset="55%" stop-color="#E0121B"/><stop offset="100%" stop-color="#8A040A"/>
        </linearGradient>
        <filter id="vSh" x="-12%" y="-18%" width="124%" height="145%">
          <feDropShadow dx="0" dy="14" stdDeviation="10" flood-color="#140100" flood-opacity="0.9"/>
          <feDropShadow dx="0" dy="0" stdDeviation="18" flood-color="#FF5500" flood-opacity="0.45"/>
        </filter>
      </defs>
      <g filter="url(#vSh)" font-family="'Baloo',sans-serif" font-weight="800" text-anchor="middle">
        <text x="660" y="152" font-size="162" fill="#4A0306" stroke="#4A0306" stroke-width="38" stroke-linejoin="round" paint-order="stroke fill">MÌ CAY MỰC</text>
        <text x="660" y="142" font-size="162" fill="url(#vGold)" stroke="#FFFFFF" stroke-width="13" stroke-linejoin="round" paint-order="stroke fill">MÌ CAY MỰC</text>

        <text x="660" y="278" font-size="102" fill="#FFE44D" stroke="#FFE44D" stroke-width="26" stroke-linejoin="round" paint-order="stroke fill">NGUYÊN CON KHỔNG LỒ!</text>
        <text x="660" y="271" font-size="102" fill="url(#vRed)" stroke="#FFFDF5" stroke-width="8.5" stroke-linejoin="round" paint-order="stroke fill">NGUYÊN CON KHỔNG LỒ!</text>
      </g>
    </svg>
    <div class="usp-pills">
      <div class="u-pill">★ Mực Ống Tươi Giòn Sần Sật</div>
      <div class="u-pill">{CHILI_ICON} Thách Thức Đủ 7 Cấp Độ Cay</div>
    </div>
  </div>

  <div class="hero-pot">
    {STEAM_FIRE_SVG}
    <img src="{u(ASSETS / 'cut_2muc_hero45.png')}" />
  </div>

  <div class="bot-cta">★ LÊN KÈO CHIẾN NGAY HÔM NAY TẠI FEEL CHICKEN! ★</div>

  <div class="foot">
    <div style="font-size:24px;font-weight:800;"><span style="color:#FFE44D;font-family:'Baloo',sans-serif;font-size:31px;">FEEL CHICKEN</span> &nbsp;•&nbsp; CS1: 38 Nguyễn Đình Chiểu &nbsp;|&nbsp; CS2: 35 Trần Hữu Duyệt</div>
    <div style="background:#FFE44D;color:#7A0409;font-family:'Baloo',sans-serif;font-size:29px;padding:6px 24px;border-radius:99px;">0796 601 106</div>
  </div>
</div>
</body></html>"""


# Render all 4 Grid Images + 1 Standalone 4:5 Poster!
c01 = render_html("muc_01", banner_2x1_html, 2160, 1080, GRID_DIR / "01_Banner_Mi_Cay_Muc_2x1.png")

c02 = render_html(
    "muc_02",
    build_fiery_square_card(
        bg_png=ASSETS / "fc_muc_bg_fire1.png",
        cutout_png=ASSETS / "cut_2muc_top.png",
        top_kicker="TOPPING TRÀN NỒI",
        big_line1="MỰC ỐNG NGUYÊN CON",
        big_line2="",
        desc_text="Khía khoanh dày căng mọng • Tươi giòn ngọt lịm từng miếng!",
        cta_badge="★ TƯƠI NGON MỖI NGÀY ★",
        show_7level_meter=False,
        pot_scale_w=815,
        pot_top=175,
    ),
    1080, 1080, GRID_DIR / "02_Muc_Ong_Nguyen_Con_1x1.png",
)

c03 = render_html(
    "muc_03",
    build_fiery_square_card(
        bg_png=ASSETS / "fc_muc_bg_fire2.png",
        cutout_png=ASSETS / "cut_1muc_top.png",
        top_kicker="THÁCH THỨC VỊ GIÁC",
        big_line1="SÚP CAY 7 CẤP ĐỘ",
        big_line2="",
        desc_text="Sợi mì Hàn dai ngon thấm đẫm nước dùng kim chi sôi sùng sục!",
        cta_badge="★ CAY TÊ ĐẦU LƯỠI ★",
        show_7level_meter=True,
        pot_scale_w=790,
        pot_top=215,
    ),
    1080, 1080, GRID_DIR / "03_Sup_Cay_7_Cap_Do_1x1.png",
)

# Distinct Card 04: Mascot Flame Chick + Steaming Squid Pot + Glazed Korean Chicken + Icy Coca Check-In Card! (ZERO image repetition!)
card04_checkin_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
html, body {{ width:1080px; height:1080px; overflow:hidden; font-family:'BVP',sans-serif; background:#140302; }}
.card {{
  position:relative; width:1080px; height:1080px;
  background: url('{u(ASSETS / "fc_muc_bg_chick_sq.jpg")}') center/cover no-repeat;
}}
.shade {{
  position:absolute; inset:0;
  background:
    linear-gradient(180deg, rgba(20,2,1,0.82) 0%, rgba(20,2,1,0.08) 28%, rgba(20,2,1,0.12) 62%, rgba(16,2,1,0.95) 100%);
}}
.border-glow {{
  position:absolute; inset:18px; border:4px solid rgba(255, 210, 72, 0.85); border-radius:32px;
  box-shadow: inset 0 0 28px rgba(255, 72, 0, 0.32); pointer-events:none; z-index:10;
}}
.top-row {{
  position:absolute; top:36px; left:42px; right:42px; z-index:9;
  display:flex; align-items:center; justify-content:space-between;
}}
.kicker {{
  display:inline-flex; align-items:center; gap:10px;
  background: linear-gradient(90deg, #9E060C 0%, #E61E27 50%, #9E060C 100%);
  border: 3px solid #FFE252; color:#FFF9DB;
  font-size:25px; font-weight:800; padding:8px 28px; border-radius:99px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.55);
}}
.mini-logo {{ width:126px; height:126px; filter:drop-shadow(0 8px 16px rgba(0,0,0,0.65)); }}
.feast-combo {{
  position:absolute; bottom:248px; left:28px; width:1024px; height:520px; z-index:7;
}}
.fc-coca {{
  position:absolute; bottom:110px; left:28px; height:330px; transform:rotate(-6deg); z-index:5;
  filter: drop-shadow(0 18px 20px rgba(0,0,0,0.75));
}}
.fc-pot {{
  position:absolute; bottom:0px; left:95px; width:640px; z-index:7;
  filter: drop-shadow(0 26px 26px rgba(0,0,0,0.85)) drop-shadow(0 0 22px rgba(255,90,0,0.4));
}}
.fc-drum {{
  position:absolute; bottom:6px; right:20px; width:385px; transform:rotate(8deg); z-index:8;
  filter: drop-shadow(0 20px 22px rgba(0,0,0,0.82));
}}
.bot-panel {{
  position:absolute; bottom:36px; left:40px; right:40px; z-index:9;
  display:flex; flex-direction:column; align-items:center; text-align:center;
}}
.cta-pill {{
  background: linear-gradient(90deg, #FFE642 0%, #FF9900 100%);
  border: 3.5px solid #FFFFFF; color:#6E0409;
  font-family:'Baloo',sans-serif; font-size:28px; padding:5px 34px; border-radius:99px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.58); margin-bottom:4px;
}}
.b-desc {{
  font-size:24.5px; font-weight:800; color:#FFF6DE; line-height:1.25;
  text-shadow: 0 3px 10px rgba(0,0,0,0.9); margin-top:4px;
}}
</style></head><body>
<div class="card">
  <div class="shade"></div>
  <div class="border-glow"></div>
  <div class="top-row">
    <div class="kicker">{FLAME_ICON} CƠN LỐC ẨM THỰC</div>
    <img class="mini-logo" src="{u(CUT_V7 / 'logo.png')}" />
  </div>
  <div class="feast-combo">
    <img class="fc-coca" src="{u(CUT_V7 / 'lon_coca.png')}" />
    <img class="fc-pot" src="{u(ASSETS / 'cut_2muc_hero45.png')}" />
    <img class="fc-drum" src="{u(CUT_V7 / 'ga_5_nguvi.png')}" />
  </div>
  <div class="bot-panel">
    <div class="cta-pill">★ LÊN KÈO GHÉ FEEL CHIẾN NGAY ★</div>
    <svg width="990" height="154" viewBox="0 0 990 154" style="overflow:visible;">
      <defs>
        <linearGradient id="c4Gold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FFFCE0"/><stop offset="45%" stop-color="#FFE042"/><stop offset="100%" stop-color="#FF7B00"/>
        </linearGradient>
        <filter id="c4Sh" x="-12%" y="-18%" width="124%" height="145%">
          <feDropShadow dx="0" dy="8" stdDeviation="7" flood-color="#140100" flood-opacity="0.9"/>
        </filter>
      </defs>
      <g filter="url(#c4Sh)" font-family="'Baloo',sans-serif" font-weight="800" text-anchor="middle">
        <text x="495" y="72" font-size="76" fill="#4F0307" stroke="#4F0307" stroke-width="22" stroke-linejoin="round" paint-order="stroke fill">HOT TREND ĐỔ BỘ</text>
        <text x="495" y="66" font-size="76" fill="url(#c4Gold)" stroke="#FFFFFF" stroke-width="7.5" stroke-linejoin="round" paint-order="stroke fill">HOT TREND ĐỔ BỘ</text>
        <text x="495" y="142" font-size="68" fill="#FFE44D" stroke="#FFE44D" stroke-width="18" stroke-linejoin="round" paint-order="stroke fill">NHA TRANG!</text>
        <text x="495" y="137" font-size="68" fill="#E0141C" stroke="#FFFFFF" stroke-width="6.5" stroke-linejoin="round" paint-order="stroke fill">NHA TRANG!</text>
      </g>
    </svg>
    <div class="b-desc">CS1: 38 Nguyễn Đình Chiểu • CS2: 35 Trần Hữu Duyệt | Ship: 0796 601 106</div>
  </div>
</div>
</body></html>"""

c04 = render_html("muc_04", card04_checkin_html, 1080, 1080, GRID_DIR / "04_Hot_Trend_Nha_Trang_1x1.png")

p4x5 = render_html("muc_4x5", poster_4x5_html, 1440, 1800, SINGLE_DIR / "Poster_Don_Mi_Cay_Muc_4x5_1440x1800.png")

# Build Facebook 4-Image Feed Mockup Preview (Top 2:1 + Bottom 3x 1:1 with 8px white gutter)
w_fb = 1200
top_fb = cv2.resize(c01, (w_fb, 600), interpolation=cv2.INTER_AREA)
g = 8
cw3 = (w_fb - 2 * g) // 3
b_cards = [cv2.resize(x, (cw3, cw3), interpolation=cv2.INTER_AREA) for x in (c02, c03, c04)]
bot_row = np.full((cw3, w_fb, 3), 255, dtype=np.uint8)
bot_row[:, 0:cw3] = b_cards[0]
bot_row[:, cw3 + g : 2 * cw3 + g] = b_cards[1]
bot_row[:, 2 * (cw3 + g) : 2 * (cw3 + g) + cw3] = b_cards[2]
fb_grid = np.vstack([top_fb, np.full((g, w_fb, 3), 255, np.uint8), bot_row])

cv2.imwrite(str(OUT_DIR / "Xem_Truoc_Bo_4_Tam_Facebook.jpg"), fb_grid, [int(cv2.IMWRITE_JPEG_QUALITY), 93])
cv2.imwrite(str(ART_DIR / "micay_muc_fb_grid_preview.jpg"), fb_grid, [int(cv2.IMWRITE_JPEG_QUALITY), 91])
cv2.imwrite(str(ART_DIR / "micay_muc_4x5_preview.jpg"), cv2.resize(p4x5, (960, 1200), interpolation=cv2.INTER_AREA), [int(cv2.IMWRITE_JPEG_QUALITY), 91])
print("RENDERED EXPLOSIVE MI CAY MUC SET SUCCESSFULLY!")
