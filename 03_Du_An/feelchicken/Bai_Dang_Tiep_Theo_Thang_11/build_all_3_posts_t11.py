import shutil
import subprocess
from pathlib import Path
import cv2
import numpy as np

BASE = Path(r"d:\AI\full studio\projects\feelchicken_3posts_t11")
ASSETS = BASE / "assets"
OUT_ROOT = BASE / "XUAT_3_BAI_THANG_11"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

CUT_V7 = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\cutouts_v7")
COMBO_V7 = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\combos_v7")
NVA_DIR = Path(r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Ảnh Feel ngũ vị\Ngũ vị A")
ART_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856")
SCR = ART_DIR / "scratch"

FONT_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def u(p: Path) -> str:
    return p.resolve().as_uri()


# Prepare crisp Sony A1 close-ups for Post 1 sub-cards (chopstick lift & claypot)
def prep_sony_crop(src: Path, out_name: str, sz: int = 1080):
    im = cv2.imdecode(np.fromfile(str(src), dtype=np.uint8), cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    m = min(h, w)
    oy, ox = (h - m) // 2, (w - m) // 2
    sq = cv2.resize(im[oy : oy + m, ox : ox + m], (sz, sz), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(sq, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.07, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.03, 0, 255)
    sq = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    dst = ASSETS / out_name
    cv2.imwrite(str(dst), sq, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    return dst


p_micay_lift = prep_sony_crop(NVA_DIR / "260628 ngũ vị A  (29).png", "sony_micay_lift.jpg")
p_micay_pot = prep_sony_crop(NVA_DIR / "260628 ngũ vị A  (17).png", "sony_micay_pot.jpg")

# Create pure-skin foreground pointing-hand layer from Anh Khang cutout (ZERO white shirt!)
_k_rgba = cv2.imread(str(ASSETS / "anh_khang_cutout.png"), cv2.IMREAD_UNCHANGED)
_kh, _kw = _k_rgba.shape[:2]
_k_bgr = _k_rgba[:, :, :3]
_k_hsv = cv2.cvtColor(_k_bgr, cv2.COLOR_BGR2HSV)
# Skin tone on left arm/pointing hand: x < 0.435*W, y > 0.45*H, warm skin saturation & R > B
_yy, _xx = np.mgrid[0:_kh, 0:_kw]
_skin = (
    (_xx < int(_kw * 0.435))
    & (_yy > int(_kh * 0.46))
    & (_k_rgba[:, :, 3] > 100)
    & (_k_hsv[:, :, 1] >= 36)
    & (_k_hsv[:, :, 0] <= 26)
    & (_k_bgr[:, :, 2].astype(np.int16) - _k_bgr[:, :, 0].astype(np.int16) >= 22)
).astype(np.uint8)
_skin = cv2.morphologyEx(_skin, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
_nl, _lb, _st, _ = cv2.connectedComponentsWithStats(_skin)
_arm_mask = np.zeros((_kh, _kw), dtype=np.uint8)
if _nl > 1:
    _best = 1 + int(np.argmax(_st[1:, cv2.CC_STAT_AREA]))
    _arm_mask = (_lb == _best).astype(np.uint8) * 255
    _arm_mask = cv2.GaussianBlur(_arm_mask, (5, 5), 0.9)
_k_arm = _k_rgba.copy()
_k_arm[:, :, 3] = np.minimum(_k_rgba[:, :, 3], _arm_mask)
cv2.imwrite(str(ASSETS / "anh_khang_arm_fg.png"), _k_arm)

f_baloo = u(FONT_DIR / "Baloo2-ExtraBold.ttf")
f_paytone = u(FONT_DIR / "PaytoneOne-Regular.ttf")
f_script = u(FONT_DIR / "DancingScript-Bold.ttf")
f_bvp_eb = u(FONT_DIR / "BeVietnamPro-ExtraBold.ttf")
f_bvp_b = u(FONT_DIR / "BeVietnamPro-Bold.ttf")

FONTS_CSS = f"""
@font-face {{ font-family: 'Baloo'; src: url('{f_baloo}') format('truetype'); font-weight: 800; }}
@font-face {{ font-family: 'Paytone'; src: url('{f_paytone}') format('truetype'); font-weight: 400; }}
@font-face {{ font-family: 'Script'; src: url('{f_script}') format('truetype'); font-weight: 700; }}
@font-face {{ font-family: 'BVP'; src: url('{f_bvp_b}') format('truetype'); font-weight: 700; }}
@font-face {{ font-family: 'BVP'; src: url('{f_bvp_eb}') format('truetype'); font-weight: 800; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
"""

ASCII_TMP = BASE / "tmp_render"
ASCII_TMP.mkdir(parents=True, exist_ok=True)


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
# BÀI 1 (22/11): MƯA LẠNH THÌ ĂN GÌ? MỘT TÔ MÌ CAY NÓNG HỔI LÀ CHÂN ÁI!
# Format: 1 Banner 2:1 (2160x1080) + 3 Tấm Vuông 1:1 (1080x1080) = Bộ 4 tấm FB Grid
# ==============================================================================
DIR_P1 = OUT_ROOT / "Bai_01_Mi_Cay_Ngay_Mua_4_Tam"
DIR_P1.mkdir(parents=True, exist_ok=True)

STEAM_SVG = """
<svg viewBox="0 0 320 180" fill="none" style="position:absolute;top:-115px;left:50%;transform:translateX(-50%);width:280px;height:150px;pointer-events:none;opacity:0.78;">
  <path d="M90 165 C65 125, 118 90, 92 40 C78 15, 105 5, 110 0" stroke="url(#stm)" stroke-width="14" stroke-linecap="round"/>
  <path d="M165 170 C140 120, 198 85, 168 30 C155 10, 178 2, 182 0" stroke="url(#stm)" stroke-width="18" stroke-linecap="round"/>
  <path d="M235 162 C215 125, 260 92, 238 45" stroke="url(#stm)" stroke-width="13" stroke-linecap="round"/>
  <defs>
    <linearGradient id="stm" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.0"/>
      <stop offset="45%" stop-color="#FFF7EC" stop-opacity="0.72"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.0"/>
    </linearGradient>
  </defs>
</svg>
"""

p1_banner_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
html, body {{ width:2160px; height:1080px; overflow:hidden; font-family:'BVP',sans-serif; }}
.stage {{
  position:relative; width:2160px; height:1080px;
  background: url('{u(ASSETS / "fc_t11_bg_post1_micay.png")}') center/cover no-repeat;
}}
/* Warm dark-red top readability vignette on left/center while keeping right chick mascot bright! */
.veil {{
  position:absolute; inset:0;
  background:
    radial-gradient(ellipse at 39% 23%, rgba(52, 7, 5, 0.74) 0%, rgba(38, 5, 4, 0.34) 48%, transparent 72%),
    linear-gradient(180deg, rgba(32, 4, 3, 0.54) 0%, rgba(32, 4, 3, 0.10) 44%, rgba(22, 4, 2, 0.32) 100%);
}}
.logo-box {{
  position:absolute; top:22px; left:36px; width:188px; height:188px; z-index:8;
  filter: drop-shadow(0 8px 18px rgba(0,0,0,0.45));
  transform: rotate(-4deg);
}}
.logo-box img {{ width:100%; height:100%; object-fit:contain; }}

.price-burst {{
  position:absolute; top:20px; right:42px; z-index:8;
  background: linear-gradient(135deg, #FFE63B 0%, #FF9E00 100%);
  border: 5px solid #FFF9D2;
  border-radius: 32px;
  padding: 10px 30px;
  text-align:center;
  transform: rotate(2.5deg);
  box-shadow: 0 14px 28px rgba(0,0,0,0.38);
}}
.price-burst .pb1 {{ font-size:22px; font-weight:800; color:#8C0B10; letter-spacing:0.5px; }}
.price-burst .pb2 {{ font-family:'Baloo',sans-serif; font-size:66px; color:#C80E15; line-height:0.94; text-shadow:0 3px 0 #FFFFFF; }}
.price-burst .pb3 {{ font-size:20px; font-weight:800; color:#2E1208; margin-top:2px; }}

.hero-head {{
  position:absolute; top:24px; left:235px; width:1365px; text-align:center; z-index:7;
}}
.top-pill {{
  display:inline-block;
  background: rgba(185, 16, 22, 0.94);
  border: 3px solid #FFD54F;
  color: #FFF6C4;
  font-size: 27px; font-weight: 800;
  padding: 8px 34px; border-radius: 99px;
  letter-spacing: 0.8px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.32);
  margin-bottom: 6px;
}}
.h-3d-wrap {{ position:relative; height:225px; width:1365px; }}

.sub-ribbon {{
  display:inline-flex; align-items:center; gap:16px;
  background: linear-gradient(90deg, #FFFDF5 0%, #FFE89E 50%, #FFFDF5 100%);
  border: 4px solid #D91820;
  color: #8F0A10;
  font-family: 'Baloo', sans-serif;
  font-size: 35px;
  padding: 7px 40px;
  border-radius: 99px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.34);
  margin-top: -8px;
}}

/* 3 Real Steaming Mì Cay Claypots on the Wooden Table (x = 48..1588px, leaving right chick 100% clear!) */
.pots-stage {{
  position:absolute; bottom:104px; left:48px;
  width:1545px; height:520px; z-index:6;
}}
.pot-card {{
  position:absolute; display:flex; flex-direction:column; align-items:center;
}}
.pot-card img {{
  width:100%; height:auto; object-fit:contain;
  filter: drop-shadow(0 24px 24px rgba(25, 8, 2, 0.62));
}}
.pot-tag {{
  margin-top:-18px; position:relative; z-index:3;
  background: linear-gradient(90deg, #B80D14 0%, #E01E26 50%, #B80D14 100%);
  border: 3px solid #FFE066;
  color: #FFFDF2;
  font-family: 'Baloo', sans-serif;
  font-size: 30px;
  padding: 5px 26px;
  border-radius: 99px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.38);
  white-space: nowrap;
}}
.pot-left  {{ left: 8px;   bottom: 20px; width: 475px; }}
.pot-right {{ right: 8px;  bottom: 20px; width: 475px; }}
.pot-mid   {{ left: 50%; transform: translateX(-50%); bottom: 4px; width: 575px; z-index: 7; }}
.pot-mid .pot-tag {{ font-size: 34px; background: linear-gradient(90deg, #FFD426 0%, #FFA800 100%); color:#7A070B; border-color:#FFFFFF; }}

.chick-badge {{
  position:absolute; bottom:114px; right:48px; z-index:8;
  background: linear-gradient(135deg, #FFFDF5 0%, #FFE799 100%);
  border: 4px solid #D9161E; border-radius:99px;
  padding: 8px 30px; font-family:'Baloo',sans-serif; font-size:31px; color:#9E0910;
  box-shadow: 0 10px 22px rgba(0,0,0,0.38);
}}

.footer-bar {{
  position:absolute; bottom:0; left:0; right:0; height:88px; z-index:9;
  background: linear-gradient(90deg, #9E0A10 0%, #CE161E 50%, #9E0A10 100%);
  border-top: 4px solid #FFD54F;
  display:flex; align-items:center; justify-content:space-between;
  padding: 0 56px; color:#FFFFFF;
}}
.fb-brand {{ font-family:'Baloo',sans-serif; font-size:40px; color:#FFE44D; letter-spacing:0.5px; }}
.fb-info  {{ font-size:25px; font-weight:800; color:#FFF9E8; }}
.fb-hot   {{ background:#FFE44D; color:#94080D; font-family:'Baloo',sans-serif; font-size:32px; padding:6px 26px; border-radius:99px; }}
</style></head><body>
<div class="stage">
  <div class="veil"></div>
  <div class="logo-box"><img src="{u(CUT_V7 / 'logo.png')}" /></div>
  <div class="price-burst">
    <div class="pb1">ĐỒNG GIÁ CHỈ</div>
    <div class="pb2">55K</div>
    <div class="pb3">Đủ 7 Cấp Độ Cay!</div>
  </div>

  <div class="hero-head">
    <div class="top-pill">🌧️ MƯA LẠNH THÌ ĂN GÌ? • XÌ XỤP NÓNG HỔI NGAY!</div>
    <svg class="h-3d-wrap" viewBox="0 0 1460 225">
      <defs>
        <linearGradient id="fireGold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FFF799"/>
          <stop offset="52%" stop-color="#FFD026"/>
          <stop offset="100%" stop-color="#FF8800"/>
        </linearGradient>
        <linearGradient id="hotRed" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FF5238"/>
          <stop offset="55%" stop-color="#D9141C"/>
          <stop offset="100%" stop-color="#96070D"/>
        </linearGradient>
        <filter id="sh3d" x="-10%" y="-15%" width="120%" height="140%">
          <feDropShadow dx="0" dy="10" stdDeviation="8" flood-color="#290402" flood-opacity="0.65"/>
        </filter>
      </defs>
      <g filter="url(#sh3d)" font-family="'Baloo', sans-serif" font-weight="800" text-anchor="middle">
        <text x="730" y="102" font-size="108" fill="#590609" stroke="#590609" stroke-width="28" stroke-linejoin="round" paint-order="stroke fill">MÌ CAY NÓNG HỔI</text>
        <text x="730" y="95"  font-size="108" fill="url(#fireGold)" stroke="#FFFFFF" stroke-width="10" stroke-linejoin="round" paint-order="stroke fill">MÌ CAY NÓNG HỔI</text>

        <text x="730" y="204" font-size="96" fill="#FFE252" stroke="#FFE252" stroke-width="26" stroke-linejoin="round" paint-order="stroke fill">CHÂN ÁI NGÀY MƯA LẠNH!</text>
        <text x="730" y="198" font-size="96" fill="url(#hotRed)" stroke="#FFFDF6" stroke-width="8" stroke-linejoin="round" paint-order="stroke fill">CHÂN ÁI NGÀY MƯA LẠNH!</text>
      </g>
    </svg>
    <div class="sub-ribbon">🔥 Nước Dùng Kim Chi Đậm Đà • Ship Nóng Tận Nơi 15 Phút!</div>
  </div>

  <div class="pots-stage">
    <div class="pot-card pot-left">
      {STEAM_SVG}
      <img src="{u(CUT_V7 / 'mi_cay_bachtuoc.png')}" />
      <div class="pot-tag">🐙 Mì Cay Bạch Tuộc • 55K</div>
    </div>
    <div class="pot-card pot-mid">
      {STEAM_SVG}
      <img src="{u(CUT_V7 / 'mi_cay_haisan.png')}" />
      <div class="pot-tag">🦐 Mì Cay Hải Sản Đầy Ụ • 55K</div>
    </div>
    <div class="pot-card pot-right">
      {STEAM_SVG}
      <img src="{u(CUT_V7 / 'mi_cay_duiga.png')}" />
      <div class="pot-tag">🍗 Mì Cay Đùi Gà • 55K</div>
    </div>
  </div>
  <div class="chick-badge">🌶️ Cấp 1 → Cấp 7 Cay Xuýt Xoa!</div>

  <div class="footer-bar">
    <div class="fb-brand">FEEL CHICKEN</div>
    <div class="fb-info">📍 CS1: 38 Nguyễn Đình Chiểu &nbsp;|&nbsp; 📍 CS2: 35 Trần Hữu Duyệt &nbsp;•&nbsp; ⏰ 10:00 – 22:00</div>
    <div class="fb-hot">📞 0796 601 106</div>
  </div>
</div>
</body></html>"""


def build_p1_square_photo_card(bg_jpg: Path, badge: str, title: str, desc: str, price: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    {FONTS_CSS}
    html, body {{ width:1080px; height:1080px; overflow:hidden; font-family:'BVP',sans-serif; }}
    .card {{
      position:relative; width:1080px; height:1080px;
      background: url('{u(bg_jpg)}') center/cover no-repeat;
    }}
    .grad {{
      position:absolute; inset:0;
      background: linear-gradient(180deg, rgba(35,6,4,0.68) 0%, transparent 32%, transparent 56%, rgba(28,5,3,0.90) 100%);
    }}
    .frame {{
      position:absolute; inset:20px; border:4px solid rgba(255, 216, 84, 0.78); border-radius:32px; pointer-events:none;
    }}
    .top-bar {{
      position:absolute; top:42px; left:46px; right:46px; display:flex; align-items:center; justify-content:space-between;
    }}
    .pill {{
      background: linear-gradient(90deg, #D9161E 0%, #FF4B2B 100%);
      border: 3px solid #FFE45C; color:#FFF9D6; font-size:26px; font-weight:800;
      padding: 8px 28px; border-radius:99px; box-shadow:0 6px 16px rgba(0,0,0,0.35);
    }}
    .mini-logo {{ width:126px; height:126px; filter:drop-shadow(0 6px 12px rgba(0,0,0,0.4)); }}
    .bot-box {{
      position:absolute; bottom:44px; left:46px; right:46px;
      display:flex; align-items:flex-end; justify-content:space-between; gap:20px;
    }}
    .b-title {{
      font-family:'Baloo',sans-serif; font-size:66px; color:#FFE44D; line-height:1.0;
      text-shadow: 0 5px 14px rgba(0,0,0,0.65); margin-bottom:8px;
    }}
    .b-desc {{ font-size:27px; font-weight:700; color:#FFF8EB; line-height:1.28; text-shadow:0 3px 8px rgba(0,0,0,0.6); }}
    .b-price {{
      flex-shrink:0;
      background: linear-gradient(135deg, #D9161E 0%, #9E080E 100%);
      border: 4px solid #FFE44D; border-radius:28px; padding: 14px 32px; text-align:center;
      box-shadow: 0 10px 22px rgba(0,0,0,0.45);
    }}
    .b-price span {{ font-family:'Baloo',sans-serif; font-size:62px; color:#FFE83B; line-height:1; }}
    </style></head><body>
    <div class="card">
      <div class="grad"></div>
      <div class="frame"></div>
      <div class="top-bar">
        <div class="pill">{badge}</div>
        <img class="mini-logo" src="{u(CUT_V7 / 'logo.png')}" />
      </div>
      <div class="bot-box">
        <div>
          <div class="b-title">{title}</div>
          <div class="b-desc">{desc}</div>
        </div>
        <div class="b-price"><span>{price}</span></div>
      </div>
    </div>
    </body></html>"""


p1_card4_combo_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
html, body {{ width:1080px; height:1080px; overflow:hidden; font-family:'BVP',sans-serif; }}
.card {{
  position:relative; width:1080px; height:1080px;
  background:
    radial-gradient(circle at 50% 48%, #FFFDF6 0%, #FFE4A3 54%, #F5B452 100%);
  display:flex; flex-direction:column; align-items:center; justify-content:space-between;
  padding: 36px 40px 36px 40px;
}}
.frame {{ position:absolute; inset:18px; border:5px solid #D91820; border-radius:32px; pointer-events:none; }}
.c-logo {{ position:absolute; top:30px; right:34px; width:124px; height:124px; filter:drop-shadow(0 6px 12px rgba(0,0,0,0.25)); transform:rotate(4deg); z-index:5; }}
.c-save {{
  position:absolute; top:250px; left:38px; z-index:6;
  background: linear-gradient(135deg, #FFE63B 0%, #FFA200 100%);
  border: 4px solid #FFFFFF; border-radius: 24px; padding: 10px 22px;
  font-family:'Baloo',sans-serif; font-size:30px; color:#9E080E; line-height:1.05;
  transform: rotate(-6deg); box-shadow: 0 10px 20px rgba(120,20,5,0.25); text-align:center;
}}
.top-pill {{
  background:#D9161E; color:#FFE853; border:3px solid #FFE853;
  font-size:27px; font-weight:800; padding:8px 34px; border-radius:99px;
  box-shadow:0 6px 16px rgba(140,12,18,0.26);
}}
.title {{ font-family:'Baloo',sans-serif; font-size:84px; color:#C21017; line-height:0.98; text-align:center; text-shadow:0 4px 0 #FFFFFF; margin-top:6px; }}
.sub {{ font-size:29px; font-weight:800; color:#3E1D10; text-align:center; margin-top:2px; }}
.hero-img {{ position:relative; width:1000px; height:610px; display:flex; align-items:center; justify-content:center; margin: -12px 0; }}
.hero-img img {{ width:100%; height:100%; object-fit:contain; transform:scale(1.15); filter:drop-shadow(0 24px 26px rgba(85,22,6,0.34)); }}
.price-bar {{
  position:relative; z-index:6;
  background: linear-gradient(90deg, #A80A11 0%, #E31C24 50%, #A80A11 100%);
  border: 5px solid #FFD54F; border-radius:99px; padding: 12px 64px;
  display:flex; align-items:center; gap:24px; box-shadow:0 12px 26px rgba(140,12,18,0.34);
}}
.price-bar .lbl {{ font-size:31px; font-weight:800; color:#FFF7DC; }}
.price-bar .val {{ font-family:'Baloo',sans-serif; font-size:76px; color:#FFE838; line-height:0.95; text-shadow:0 4px 0 #75060A; }}
</style></head><body>
<div class="card">
  <div class="frame"></div>
  <img class="c-logo" src="{u(CUT_V7 / 'logo.png')}" />
  <div class="c-save">★ NO CĂNG BỤNG ★<br/><span style="font-size:24px;color:#3E1B0E;">Đủ Mì + Gà + Nước!</span></div>
  <div style="display:flex;flex-direction:column;align-items:center;z-index:4;">
    <div class="top-pill">★ COMBO ẤM BỤNG BÁN CHẠY NHẤT ★</div>
    <div class="title">COMBO FEEL SPICY</div>
    <div class="sub">01 Nồi Mì Cay Hàn Quốc + 01 Đùi Gà Sốt Hàn + 01 Coca</div>
  </div>
  <div class="hero-img"><img src="{u(COMBO_V7 / 'cb03_spicy.png')}" /></div>
  <div class="price-bar"><span class="lbl">TRỌN BỘ CHỈ</span><span class="val">89.000Đ</span></div>
</div>
</body></html>"""


# ==============================================================================
# BÀI 2 (24/11): 5 ĐÙI GÀ + 1 MÌ TƯƠNG ĐEN TRONG 5 PHÚT – NHẬN 1.500.000Đ!
# Format: Poster 2:1 (2160x1080) -> Cắt chuẩn 2 Tấm Vuông 1:1 (1080x1080) sát mép!
# CRITICAL SEAM RULE: ZERO text/face crosses x = 1080px!
# ==============================================================================
DIR_P2 = OUT_ROOT / "Bai_02_Thu_Thach_5_Phut_1500K_2_Tam"
DIR_P2.mkdir(parents=True, exist_ok=True)

p2_full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
html, body {{ width:2160px; height:1080px; overflow:hidden; font-family:'BVP',sans-serif; }}
.stage {{
  position:relative; width:2160px; height:1080px;
  background: url('{u(ASSETS / "fc_t11_bg_post2_challenge.png")}') center/cover no-repeat;
  display:grid; grid-template-columns: 1080px 1080px;
}}
.dark-top {{
  position:absolute; inset:0; pointer-events:none;
  background: linear-gradient(180deg, rgba(42,4,4,0.58) 0%, rgba(35,4,4,0.16) 52%, rgba(25,4,2,0.48) 100%);
}}

/* LEFT HALF (x = 0..1080): Title + Anh Khang + 5 Đùi Gà & Mì Tương Đen */
.left-half {{
  position:relative; width:1080px; height:1080px; padding: 24px 34px 106px 38px; z-index:5;
}}
.l-top {{ display:flex; align-items:center; gap:18px; }}
.l-logo {{ width:168px; height:168px; flex-shrink:0; filter:drop-shadow(0 8px 16px rgba(0,0,0,0.45)); transform:rotate(-4deg); }}
.l-logo img {{ width:100%; height:100%; object-fit:contain; }}
.l-kicker {{
  background: linear-gradient(90deg, #FFE249 0%, #FFA800 100%);
  color:#85080D; font-family:'Baloo',sans-serif; font-size:31px;
  padding: 8px 28px; border-radius:99px; border:3px solid #FFFFFF;
  box-shadow:0 8px 18px rgba(0,0,0,0.35);
}}

.khang-wrap {{
  position:absolute; bottom:212px; left:92px; width:700px; height:562px; z-index:4;
}}
.khang-wrap img {{
  width:100%; height:100%; object-fit:contain; object-position:bottom center;
  filter: drop-shadow(0 14px 24px rgba(0,0,0,0.48));
}}
.khang-arm-fg {{
  position:absolute; bottom:212px; left:92px; width:700px; height:562px; z-index:8; pointer-events:none;
}}
.khang-arm-fg img {{
  width:100%; height:100%; object-fit:contain; object-position:bottom center;
  filter: drop-shadow(0 10px 14px rgba(0,0,0,0.38));
}}

/* Real 5 Drumsticks + Mì Tương Đen Feast right underneath Anh Khang's pointing finger & seamlessly covering lower shirt edge! */
.feast-wrap {{
  position:absolute; bottom:94px; left:28px; width:1022px; height:405px; z-index:6;
}}
.feast-ga5 {{
  position:absolute; bottom:26px; left:18px; width:510px; z-index:7;
  filter: drop-shadow(0 22px 24px rgba(20,5,0,0.68));
}}
.feast-mtd {{
  position:absolute; bottom:34px; right:18px; width:490px; z-index:6;
  filter: drop-shadow(0 20px 22px rgba(20,5,0,0.62));
}}
.feast-label {{
  position:absolute; bottom:0px; left:50%; transform:translateX(-50%); z-index:9;
  background: linear-gradient(90deg, #8F060C 0%, #CF151D 50%, #8F060C 100%);
  border:3.5px solid #FFE44D; color:#FFFDF0; white-space:nowrap;
  font-family:'Baloo',sans-serif; font-size:32px; padding:6px 38px; border-radius:99px;
  box-shadow:0 10px 20px rgba(0,0,0,0.52);
}}

/* RIGHT HALF (x = 1080..2160): Prize 1.500.000Đ + 3 Crystal-Clear Rules + Hall-of-Fame Strip + CTA! */
.right-half {{
  position:relative; width:1080px; height:1080px;
  padding: 28px 42px 102px 34px; z-index:5;
  display:flex; flex-direction:column; justify-content:space-between;
}}
.board {{
  background: linear-gradient(180deg, #FFFDF8 0%, #FFF2D4 100%);
  border: 5px solid #FFB81C;
  outline: 4px solid #96080E;
  border-radius: 34px;
  padding: 30px 36px 28px 36px;
  box-shadow: 0 22px 44px rgba(25, 3, 2, 0.55);
  display:flex; flex-direction:column; gap:20px;
}}
.prize-banner {{
  background: linear-gradient(135deg, #C80E16 0%, #8F060B 100%);
  border: 4px solid #FFE24A;
  border-radius: 24px;
  padding: 20px 26px;
  text-align:center;
  box-shadow: 0 10px 20px rgba(130, 8, 12, 0.30);
}}
.pz-top {{ font-size:28px; font-weight:800; color:#FFEAA0; letter-spacing:1px; }}
.pz-num {{
  font-family:'Baloo',sans-serif; font-size:116px; color:#FFE838; line-height:0.95;
  text-shadow: 0 6px 0 #5E0407, 0 10px 20px rgba(0,0,0,0.35);
}}
.pz-sub {{ font-size:26px; font-weight:800; color:#FFFFFF; margin-top:6px; }}

.rule-row {{
  display:flex; align-items:center; gap:22px;
  background:#FFFFFF; border:3px solid #F0B64C; border-radius:22px;
  padding: 19px 24px;
  box-shadow: 0 6px 14px rgba(140,55,10,0.10);
}}
.rule-num {{
  width:76px; height:76px; border-radius:20px; flex-shrink:0;
  background: linear-gradient(180deg, #FFD426 0%, #FF9900 100%);
  border: 3px solid #2B130B;
  display:flex; align-items:center; justify-content:center;
  font-family:'Baloo',sans-serif; font-size:42px; color:#231009;
}}
.rule-txt .rt1 {{ font-family:'Baloo',sans-serif; font-size:35px; color:#B80F16; line-height:1.05; }}
.rule-txt .rt2 {{ font-size:24px; font-weight:700; color:#331A10; line-height:1.26; margin-top:3px; }}

.fame-note {{
  background: linear-gradient(90deg, #8F060B 0%, #BD1017 50%, #8F060B 100%);
  border: 3px solid #FFE252; border-radius: 18px; padding: 12px 20px;
  text-align:center; font-size:23px; font-weight:800; color:#FFF7D6;
}}

.cta-strip {{
  background: linear-gradient(90deg, #FFD629 0%, #FFAE00 100%);
  border: 4px solid #FFFFFF;
  border-radius: 99px;
  padding: 15px 34px;
  text-align:center;
  font-family:'Baloo',sans-serif; font-size:36px; color:#7D070C;
  box-shadow: 0 12px 24px rgba(0,0,0,0.38);
}}

/* SEAM-SAFE SPLIT FOOTER PILLS (Left inside 0..1050, Right inside 1110..2160!) */
.foot-left {{
  position:absolute; bottom:18px; left:30px; width:1020px; height:64px; z-index:9;
  background: linear-gradient(90deg, #9E090F 0%, #CE161E 100%);
  border: 3px solid #FFD54F; border-radius:99px;
  display:flex; align-items:center; justify-content:center;
  font-size:23.5px; font-weight:800; color:#FFF9E6;
  box-shadow:0 8px 18px rgba(0,0,0,0.4);
}}
.foot-right {{
  position:absolute; bottom:18px; right:30px; width:1020px; height:64px; z-index:9;
  background: linear-gradient(90deg, #CE161E 0%, #9E090F 100%);
  border: 3px solid #FFD54F; border-radius:99px;
  display:flex; align-items:center; justify-content:center; gap:18px;
  font-size:23.5px; font-weight:800; color:#FFF9E6;
  box-shadow:0 8px 18px rgba(0,0,0,0.4);
}}
</style></head><body>
<div class="stage">
  <div class="dark-top"></div>

  <div class="left-half">
    <div class="l-top">
      <div class="l-logo"><img src="{u(CUT_V7 / 'logo.png')}" /></div>
      <div>
        <div class="l-kicker">🔥 ĐẤU TRƯỜNG ẨM THỰC FEEL CHICKEN</div>
        <svg width="790" height="215" viewBox="0 0 790 215" style="margin-top:6px;overflow:visible;">
          <defs>
            <linearGradient id="chGold" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#FFF8A6"/><stop offset="55%" stop-color="#FFD024"/><stop offset="100%" stop-color="#FF8400"/>
            </linearGradient>
            <filter id="chSh" x="-10%" y="-15%" width="120%" height="140%">
              <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#240302" flood-opacity="0.7"/>
            </filter>
          </defs>
          <g filter="url(#chSh)" font-family="'Baloo',sans-serif" font-weight="800">
            <text x="8" y="88" font-size="88" fill="#5E0509" stroke="#5E0509" stroke-width="22" stroke-linejoin="round" paint-order="stroke fill">THỬ THÁCH 5 PHÚT</text>
            <text x="8" y="82" font-size="88" fill="url(#chGold)" stroke="#FFFFFF" stroke-width="8" stroke-linejoin="round" paint-order="stroke fill">THỬ THÁCH 5 PHÚT</text>

            <text x="8" y="182" font-size="78" fill="#FFE249" stroke="#FFE249" stroke-width="20" stroke-linejoin="round" paint-order="stroke fill">BẠN DÁM THỬ KHÔNG?</text>
            <text x="8" y="177" font-size="78" fill="#D9141C" stroke="#FFFFFF" stroke-width="7" stroke-linejoin="round" paint-order="stroke fill">BẠN DÁM THỬ KHÔNG?</text>
          </g>
        </svg>
      </div>
    </div>

    <div class="khang-wrap"><img src="{u(ASSETS / 'anh_khang_cutout.png')}" /></div>

    <div class="feast-wrap">
      <img class="feast-mtd" src="{u(CUT_V7 / 'mi_tuong_den.png')}" />
      <img class="feast-ga5" src="{u(CUT_V7 / 'ga_5_nguvi.png')}" />
      <div class="feast-label">★ 05 Đùi Gà Cỡ Lớn + 01 Mì Tương Đen ★</div>
    </div>

    <div class="khang-arm-fg"><img src="{u(ASSETS / 'anh_khang_arm_fg.png')}" /></div>
  </div>

  <div class="right-half">
    <div class="board">
      <div class="prize-banner">
        <div class="pz-top">★ GIẢI THƯỞNG TIỀN MẶT TRAO TAY ★</div>
        <div class="pz-num">1.500.000Đ</div>
        <div class="pz-sub">+ MIỄN PHÍ 100% PHẦN ĂN KHI THẮNG KÈO!</div>
      </div>

      <div class="rule-row">
        <div class="rule-num">01</div>
        <div class="rule-txt">
          <div class="rt1">KHẨU PHẦN THÁCH ĐẤU</div>
          <div class="rt2">Ăn sạch <strong>05 Đùi Gà Rán Cỡ Lớn + 01 Phần Mì Tương Đen</strong></div>
        </div>
      </div>

      <div class="rule-row">
        <div class="rule-num">02</div>
        <div class="rule-txt">
          <div class="rt1">THỜI GIAN BẤM GIỜ: 05 PHÚT</div>
          <div class="rt2">Thử thách cá nhân 1 người • Áp dụng trực tiếp tại 2 cơ sở</div>
        </div>
      </div>

      <div class="rule-row">
        <div class="rule-num">03</div>
        <div class="rule-txt">
          <div class="rt1">CHƠI VUI KHÔNG LO LỖ</div>
          <div class="rt2">Nếu chưa vượt qua chỉ thanh toán <strong>250.000đ</strong> đúng giá phần ăn!</div>
        </div>
      </div>

      <div class="fame-note">★ Thưởng nóng tại bàn • Ghi danh Bảng Vàng Chiến Thần Feel Chicken ★</div>
    </div>

    <div class="cta-strip">★ TAG NGAY "CHIẾN THẦN ĂN UỐNG" VÀO NHẬN KÈO! ★</div>
  </div>

  <div class="foot-left">strong&nbsp;FEEL CHICKEN&nbsp;•&nbsp;CS1: 38 Nguyễn Đình Chiểu &nbsp;|&nbsp; CS2: 35 Trần Hữu Duyệt</div>
  <div class="foot-right">⏰ Mở cửa: 10:00 – 22:00 &nbsp;|&nbsp; 📞 Đăng ký thi ngay: <span style="color:#FFE44D;font-family:'Baloo',sans-serif;font-size:29px;">0796 601 106</span></div>
</div>
</body></html>""".replace("strong&nbsp;FEEL CHICKEN", "<span style='color:#FFE44D;font-family:Baloo,sans-serif;font-size:29px;'>FEEL CHICKEN</span>")


# ==============================================================================
# BÀI 3 (28/11): MỘT NGÀY MƯA ƯƠNG ƯƠNG, GHÉ FEEL CHICKEN ĂN NGON CHO ẤM BỤNG!
# Format: Poster Tổng 2160x2160 -> Cắt chuẩn Bộ 3 Tấm Facebook:
#   01_Tren_Ngang_2x1 (2160x1080) + 02_Duoi_Trai_1x1 (1080x1080) + 03_Duoi_Phai_1x1 (1080x1080)
# ==============================================================================
DIR_P3 = OUT_ROOT / "Bai_03_Mua_Uong_Uong_Ghe_Feel_Am_Bung_3_Tam"
DIR_P3.mkdir(parents=True, exist_ok=True)

p3_full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTS_CSS}
html, body {{ width:2160px; height:2160px; overflow:hidden; font-family:'BVP',sans-serif; }}
.stage {{
  position:relative; width:2160px; height:2160px;
  background: url('{u(ASSETS / "fc_t11_bg_post3_cozyrain.png")}') center/cover no-repeat;
}}
.top-glow {{
  position:absolute; top:0; left:760px; right:0; height:1080px; pointer-events:none;
  background:
    radial-gradient(ellipse at 54% 46%, rgba(255, 250, 236, 0.88) 0%, rgba(255, 234, 198, 0.48) 58%, transparent 86%);
}}

/* TOP HALF (y = 0..1080 — 01_Tren_Ngang_2x1.png): Left side shows adorable raincoat chick UNOBSTRUCTED, Right side holds big festive headline! */
.top-half {{
  position:absolute; top:0; left:0; width:2160px; height:1080px; z-index:6;
}}
.chick-speech {{
  position:absolute; top:38px; left:72px; z-index:8;
  background: #FFFDF8; border: 5px solid #E58A3C; border-radius: 42px;
  padding: 16px 38px; box-shadow: 0 14px 28px rgba(95,35,8,0.24);
  text-align:center; transform: rotate(-3deg);
}}
.chick-speech::after {{
  content:''; position:absolute; bottom:-24px; left:180px;
  border-width: 24px 20px 0 20px; border-style:solid;
  border-color: #E58A3C transparent transparent transparent;
}}
.chick-speech .cp1 {{ font-size:26px; font-weight:800; color:#5C3422; }}
.chick-speech .cp2 {{ font-family:'Baloo',sans-serif; font-size:44px; color:#D1161E; line-height:1.05; }}

.right-hero {{
  position:absolute; top:28px; left:815px; width:1295px; height:1010px;
  display:flex; flex-direction:column; align-items:center; justify-content:space-between;
}}
.rh-top {{
  width:100%; display:flex; align-items:center; justify-content:center; gap:34px;
}}
.center-logo {{ width:228px; height:228px; filter:drop-shadow(0 12px 20px rgba(110,25,10,0.28)); transform:rotate(-3deg); }}
.center-logo img {{ width:100%; height:100%; object-fit:contain; }}

.price-cloud {{
  background: linear-gradient(135deg, #FFE85E 0%, #FFB319 100%);
  border: 5px solid #FFFFFF; border-radius:42px;
  padding: 16px 42px; box-shadow:0 14px 28px rgba(140,55,0,0.26);
  text-align:center; transform:rotate(2.5deg);
}}
.price-cloud .pc1 {{ font-size:27px; font-weight:800; color:#7A0A0F; }}
.price-cloud .pc2 {{ font-family:'Baloo',sans-serif; font-size:64px; color:#C40E15; line-height:0.96; text-shadow:0 3px 0 #FFFFFF; }}

.warm-ribbon {{
  background: linear-gradient(90deg, #B80F17 0%, #E62932 50%, #B80F17 100%);
  border: 5px solid #FFE259;
  color: #FFFDF4;
  font-family:'Baloo',sans-serif; font-size:38px;
  padding: 12px 44px; border-radius:99px; white-space:nowrap;
  box-shadow: 0 14px 28px rgba(120,12,16,0.34);
  margin-bottom: 18px;
}}

/* BOTTOM HALF (y = 1080..2160): Grand Warm Feast split cleanly into Left (0..1080) & Right (1080..2160) */
.bot-half {{
  position:absolute; top:1080px; left:0; width:2160px; height:1080px; z-index:6;
}}
/* Left Quadrant (x = 0..1080): Keep top-left y=0..215 clear of chick's red umbrella! */
.q-left {{ position:absolute; top:0; left:0; width:1080px; height:1080px; }}
/* Right Quadrant (x = 1080..2160): Mì Cay + Mì Ý + Salad + 2 Coca */
.q-right {{ position:absolute; top:0; left:1080px; width:1080px; height:1080px; }}

.dish-drop {{ position:absolute; filter:drop-shadow(0 24px 26px rgba(45,14,4,0.52)); }}

.q-tag {{
  position:absolute; bottom:126px; left:50%; transform:translateX(-50%);
  background: linear-gradient(90deg, #FFFDF7 0%, #FFE9A8 100%);
  border: 4px solid #D91820; border-radius:99px;
  padding: 10px 38px; white-space:nowrap;
  font-family:'Baloo',sans-serif; font-size:36px; color:#9E0B11;
  box-shadow: 0 12px 24px rgba(45,12,4,0.32); z-index:9;
}}

.p3-foot-left {{
  position:absolute; bottom:24px; left:30px; width:1020px; height:76px; z-index:10;
  background: linear-gradient(90deg, #A50B11 0%, #D4171F 100%);
  border: 3.5px solid #FFE059; border-radius:99px;
  display:flex; align-items:center; justify-content:center;
  font-size:25px; font-weight:800; color:#FFF9E8;
  box-shadow:0 10px 22px rgba(0,0,0,0.38);
}}
.p3-foot-right {{
  position:absolute; bottom:24px; right:30px; width:1020px; height:76px; z-index:10;
  background: linear-gradient(90deg, #D4171F 0%, #A50B11 100%);
  border: 3.5px solid #FFE059; border-radius:99px;
  display:flex; align-items:center; justify-content:center; gap:14px;
  font-size:25px; font-weight:800; color:#FFF9E8;
  box-shadow:0 10px 22px rgba(0,0,0,0.38);
}}
</style></head><body>
<div class="stage">
  <div class="top-glow"></div>

  <div class="top-half">
    <div class="chick-speech">
      <div class="cp1">🌧️ Mưa ương ương lạnh bụng?</div>
      <div class="cp2">Vào Feel Trú Mưa Nha!</div>
    </div>

    <div class="right-hero">
      <div class="rh-top">
        <div class="center-logo"><img src="{u(CUT_V7 / 'logo.png')}" /></div>
        <div class="price-cloud">
          <div class="pc1">Combo Nóng Giòn</div>
          <div class="pc2">Chỉ Từ 59K!</div>
        </div>
      </div>

      <svg width="1280" height="585" viewBox="0 0 1280 585" style="overflow:visible;">
        <defs>
          <linearGradient id="wRed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FF5938"/><stop offset="55%" stop-color="#D9151D"/><stop offset="100%" stop-color="#98070D"/>
          </linearGradient>
          <linearGradient id="wGold" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FFF48F"/><stop offset="55%" stop-color="#FFC719"/><stop offset="100%" stop-color="#F07800"/>
          </linearGradient>
          <filter id="wSh" x="-10%" y="-15%" width="120%" height="140%">
            <feDropShadow dx="0" dy="12" stdDeviation="9" flood-color="#3E1004" flood-opacity="0.48"/>
          </filter>
        </defs>
        <g filter="url(#wSh)" font-family="'Baloo',sans-serif" font-weight="800" text-anchor="middle">
          <text x="640" y="155" font-size="126" fill="#6E070C" stroke="#6E070C" stroke-width="34" stroke-linejoin="round" paint-order="stroke fill">Mưa Ương Ương</text>
          <text x="640" y="145" font-size="126" fill="url(#wRed)" stroke="#FFFFFF" stroke-width="12" stroke-linejoin="round" paint-order="stroke fill">Mưa Ương Ương</text>

          <text x="640" y="315" font-size="132" fill="#6B2804" stroke="#6B2804" stroke-width="34" stroke-linejoin="round" paint-order="stroke fill">Ghé Feel Ăn Ngon</text>
          <text x="640" y="305" font-size="132" fill="url(#wGold)" stroke="#FFFDF7" stroke-width="12" stroke-linejoin="round" paint-order="stroke fill">Ghé Feel Ăn Ngon</text>

          <text x="640" y="468" font-size="122" fill="#6E070C" stroke="#6E070C" stroke-width="32" stroke-linejoin="round" paint-order="stroke fill">Cho Ấm Bụng Nha!</text>
          <text x="640" y="458" font-size="122" fill="url(#wRed)" stroke="#FFFFFF" stroke-width="12" stroke-linejoin="round" paint-order="stroke fill">Cho Ấm Bụng Nha!</text>

          <text x="640" y="556" font-family="'BVP',sans-serif" font-size="40" font-weight="800" fill="#5E080C" stroke="#FFFFFF" stroke-width="10" paint-order="stroke fill">Ăn Là Mê, 사랑해! • Phòng Lạnh Khô Ráo • Ship Nóng 15 Phút</text>
        </g>
      </svg>

      <div class="warm-ribbon">🍗 Gà Rán 5 Sốt • Mì Cay 7 Cấp • Tokbokki • Mì Tương Đen • Mì Ý!</div>
    </div>
  </div>

  <div class="bot-half">
    <!-- Left 1080x1080 Tile: keep top-left clear of raincoat chick's red umbrella! -->
    <div class="q-left">
      <img class="dish-drop" src="{u(CUT_V7 / 'tokbokki.png')}" style="top:52px; left:525px; width:495px; transform:rotate(-4deg);" />
      <img class="dish-drop" src="{u(CUT_V7 / 'khoai_tay_dia.png')}" style="top:235px; left:36px; width:475px; transform:rotate(4deg);" />
      <img class="dish-drop" src="{u(CUT_V7 / 'ga_5_nguvi.png')}" style="top:295px; left:225px; width:715px; z-index:5;" />
      <div class="q-tag">🍗 Gà Rán 5 Vị Sốt • Combo Đôi Từ 129K</div>
    </div>

    <!-- Right 1080x1080 Tile: Full overflowing feast (Mì Tương Đen + Salad + 2 Coca + Mì Cay + Mì Ý) -->
    <div class="q-right">
      <img class="dish-drop" src="{u(CUT_V7 / 'mi_tuong_den.png')}" style="top:24px; left:34px; width:465px; transform:rotate(-3deg);" />
      <img class="dish-drop" src="{u(CUT_V7 / 'lon_coca.png')}" style="top:20px; right:158px; height:365px; transform:rotate(-3deg);" />
      <img class="dish-drop" src="{u(CUT_V7 / 'lon_coca.png')}" style="top:36px; right:48px; height:365px; transform:rotate(4deg);" />
      <img class="dish-drop" src="{u(CUT_V7 / 'salad.png')}" style="top:72px; left:492px; width:425px; z-index:4;" />
      <img class="dish-drop" src="{u(CUT_V7 / 'mi_cay_haisan.png')}" style="top:280px; left:28px; width:585px; z-index:5;" />
      <img class="dish-drop" src="{u(CUT_V7 / 'mi_y.png')}" style="top:375px; right:30px; width:555px; z-index:6;" />
      <div class="q-tag">★ Mì Cay 55K • Combo Hội Bạn 249K - 259K ★</div>
    </div>

    <div class="p3-foot-left"><span style="color:#FFE44D;font-family:'Baloo',sans-serif;font-size:32px;margin-right:10px;">FEEL CHICKEN</span> • CS1: 38 Nguyễn Đình Chiểu &nbsp;|&nbsp; CS2: 35 Trần Hữu Duyệt</div>
    <div class="p3-foot-right">⏰ Mở cửa: 10:00 – 22:00 &nbsp;|&nbsp; 🛵 Giao nóng 15p: <span style="color:#FFE44D;font-family:'Baloo',sans-serif;font-size:32px;">0796 601 106</span></div>
  </div>
</div>
</body></html>"""


# --- EXECUTE ALL RENDERS & SLICE FOR FACEBOOK MULTI-IMAGE GRIDS! ---
# 1. Post 1 (4 images: 1x 2160x1080 + 3x 1080x1080)
p1_01 = render_html("p1_01", p1_banner_html, 2160, 1080, DIR_P1 / "01_Banner_Mi_Cay_2x1.png")
p1_02 = render_html(
    "p1_02",
    build_p1_square_photo_card(p_micay_lift, "🌶️ SỢI MÌ DAI NGON • SÚP CAY NỒNG", "MÌ CAY HẢI SẢN", "Tôm tươi, mực giòn, chả cá Hàn, nấm kim châm", "55K"),
    1080, 1080, DIR_P1 / "02_Mi_Cay_Hai_San_1x1.png",
)
p1_03 = render_html(
    "p1_03",
    build_p1_square_photo_card(p_micay_pot, "🔥 ĐỦ 7 CẤP ĐỘ CAY TỰ CHỌN", "BẠCH TUỘC • ĐÙI GÀ", "Nước dùng kim chi Hàn Quốc nóng hổi bốc khói", "55K"),
    1080, 1080, DIR_P1 / "03_Mi_Cay_7_Cap_Do_1x1.png",
)
p1_04 = render_html("p1_04", p1_card4_combo_html, 1080, 1080, DIR_P1 / "04_Combo_Feel_Spicy_89K_1x1.png")

# Build Facebook 4-Image Feed Mockup Preview for Post 1 (Top 2:1 + Bottom 3x 1:1 with white 8px gutter!)
w_fb = 1200
top_fb = cv2.resize(p1_01, (w_fb, 600), interpolation=cv2.INTER_AREA)
g = 8
cw3 = (w_fb - 2 * g) // 3
b_cards = [cv2.resize(x, (cw3, cw3), interpolation=cv2.INTER_AREA) for x in (p1_02, p1_03, p1_04)]
bot_row = np.full((cw3, w_fb, 3), 255, dtype=np.uint8)
bot_row[:, 0:cw3] = b_cards[0]
bot_row[:, cw3 + g : 2 * cw3 + g] = b_cards[1]
bot_row[:, 2 * (cw3 + g) : 2 * (cw3 + g) + cw3] = b_cards[2]
fb_p1 = np.vstack([top_fb, np.full((g, w_fb, 3), 255, np.uint8), bot_row])
cv2.imwrite(str(DIR_P1 / "Xem_Truoc_Hien_Thi_Facebook_4_Tam.jpg"), fb_p1, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
cv2.imwrite(str(ART_DIR / "post1_micay_fb_preview.jpg"), fb_p1, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

# 2. Post 2 (Poster 2160x1080 -> 2 Seamless 1080x1080 Squares!)
p2_full_dir = DIR_P2 / "File_Goc_Va_Xem_Truoc"
p2_full = render_html("p2_full", p2_full_html, 2160, 1080, p2_full_dir / "Poster_Thu_Thach_1500K_Goc_2160x1080.png")
cv2.imwrite(str(DIR_P2 / "01_Thu_Thach_Trai_1x1.png"), p2_full[:, :1080])
cv2.imwrite(str(DIR_P2 / "02_Thu_Thach_Phai_1x1.png"), p2_full[:, 1080:])
# Facebook 2-Image Side-by-Side Feed Mockup (with 6px white center gutter!)
fb_p2 = np.hstack([
    cv2.resize(p2_full[:, :1080], (600, 600), interpolation=cv2.INTER_AREA),
    np.full((600, 6, 3), 255, np.uint8),
    cv2.resize(p2_full[:, 1080:], (600, 600), interpolation=cv2.INTER_AREA),
])
cv2.imwrite(str(p2_full_dir / "Xem_Truoc_Hien_Thi_Facebook_2_Tam.jpg"), fb_p2, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
cv2.imwrite(str(ART_DIR / "post2_challenge_fb_preview.jpg"), fb_p2, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

# 3. Post 3 (Poster 2160x2160 -> 3 Seamless Facebook Slices: 01_Tren_2x1 + 02_Duoi_Trai_1x1 + 03_Duoi_Phai_1x1!)
p3_full_dir = DIR_P3 / "File_Goc_Va_Xem_Truoc"
p3_full = render_html("p3_full", p3_full_html, 2160, 2160, p3_full_dir / "Poster_Tong_Ghe_Feel_Am_Bung_2160x2160.png")
cv2.imwrite(str(DIR_P3 / "01_Tren_Ngang_2x1.png"), p3_full[:1080, :])
cv2.imwrite(str(DIR_P3 / "02_Duoi_Trai_1x1.png"), p3_full[1080:, :1080])
cv2.imwrite(str(DIR_P3 / "03_Duoi_Phai_1x1.png"), p3_full[1080:, 1080:])
# Facebook 3-Image Grid Mockup (with 8px white gutters!)
top3 = cv2.resize(p3_full[:1080, :], (1200, 600), interpolation=cv2.INTER_AREA)
bl3 = cv2.resize(p3_full[1080:, :1080], (596, 596), interpolation=cv2.INTER_AREA)
br3 = cv2.resize(p3_full[1080:, 1080:], (596, 596), interpolation=cv2.INTER_AREA)
bot3 = np.hstack([bl3, np.full((596, 8, 3), 255, np.uint8), br3])
fb_p3 = np.vstack([top3, np.full((8, 1200, 3), 255, np.uint8), bot3])
cv2.imwrite(str(p3_full_dir / "Xem_Truoc_Hien_Thi_Facebook_3_Tam.jpg"), fb_p3, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
cv2.imwrite(str(ART_DIR / "post3_cozy_fb_preview.jpg"), fb_p3, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

print("ALL 3 NOVEMBER POSTS RENDERED & SLICED FOR FACEBOOK!")
