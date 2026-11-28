import shutil
import subprocess
from pathlib import Path
import cv2
from PIL import Image

BASE = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026")
CUT_V7 = BASE / "assets" / "cutouts_v7"
COMBO_V7 = BASE / "assets" / "combos_v7"
OUT_DIR = BASE / "XUAT_MENU_MOI_FEEL_CHICKEN"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ART_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856")
SCR = ART_DIR / "scratch"

FONT_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def file_uri(p: Path) -> str:
    return p.resolve().as_uri()


f_baloo = file_uri(FONT_DIR / "Baloo2-ExtraBold.ttf")
f_script = file_uri(FONT_DIR / "DancingScript-Bold.ttf")
f_bvp_eb = file_uri(FONT_DIR / "BeVietnamPro-ExtraBold.ttf")
f_bvp_b = file_uri(FONT_DIR / "BeVietnamPro-Bold.ttf")
f_bvp_sb = file_uri(FONT_DIR / "BeVietnamPro-SemiBold.ttf")

IMG = {}
for d in (CUT_V7, COMBO_V7):
    for p in list(d.glob("*.png")) + list(d.glob("*.jpg")):
        IMG[p.name] = file_uri(p)

W_PAGE, H_PAGE = 3000, 1941

SVG_CROWN_BIG = """
<svg class="crown-svg" viewBox="0 0 90 74" fill="none">
  <g transform="rotate(-12 45 37)">
    <path d="M12 56L6 20L29 34L45 10L61 34L84 20L78 56H12Z" fill="#FFD426" stroke="#23120B" stroke-width="5" stroke-linejoin="round"/>
    <path d="M14 56H76V64C76 66 74 67 72 67H18C16 67 14 66 14 64V56Z" fill="#FFB800" stroke="#23120B" stroke-width="4.5" stroke-linejoin="round"/>
    <circle cx="6" cy="17" r="5" fill="#FFF066" stroke="#23120B" stroke-width="4"/>
    <circle cx="45" cy="8" r="5.5" fill="#FFF066" stroke="#23120B" stroke-width="4"/>
    <circle cx="84" cy="17" r="5" fill="#FFF066" stroke="#23120B" stroke-width="4"/>
  </g>
</svg>
"""

SVG_FLAME = """
<svg width="32" height="36" viewBox="0 0 28 32" fill="none" style="vertical-align:-5px;margin-right:8px;">
  <path d="M15.5 2C15.5 2 24 9.5 24 18.5C24 24.8 19.3 29.5 14 29.5C8.7 29.5 4 24.8 4 18.5C4 13.5 7 9.2 9.5 7.2C9.2 10.5 11.2 12.5 11.2 12.5C10.8 8.2 13.2 4.5 15.5 2Z" fill="#FFE135" stroke="#7A060A" stroke-width="2"/>
  <path d="M14 14C14 14 18.5 17.8 18.5 22C18.5 24.8 16.5 27 14 27C11.5 27 9.5 24.8 9.5 22C9.5 19.2 11.8 16.2 14 14Z" fill="#FF5722"/>
</svg>
"""

SVG_YELLOW_BRUSH = """
<svg class="brush-bg" viewBox="0 0 620 92" preserveAspectRatio="none">
  <path d="M18,14 C150,4 470,4 602,14 C616,22 618,42 608,55 C616,66 604,81 586,83 C445,90 170,90 26,82 C8,79 4,62 14,50 C4,38 6,20 18,14 Z" fill="#FFD224" stroke="#DC8D00" stroke-width="3"/>
  <path d="M30,22 C175,12 450,12 590,20" stroke="#FFF2A6" stroke-width="5" stroke-linecap="round" fill="none" opacity="0.85"/>
</svg>
"""

SVG_RED_BRUSH_HEADER = """
<svg class="brush-bg" viewBox="0 0 620 92" preserveAspectRatio="none">
  <path d="M18,14 C150,4 470,4 602,14 C616,22 618,42 608,55 C616,66 604,81 586,83 C445,90 170,90 26,82 C8,79 4,62 14,50 C4,38 6,20 18,14 Z" fill="#D4161E" stroke="#8F070C" stroke-width="3"/>
  <path d="M30,22 C175,12 450,12 590,20" stroke="#FF7A7A" stroke-width="4.5" stroke-linecap="round" fill="none" opacity="0.6"/>
</svg>
"""


def price_splash_html(price_str: str, cls: str = "") -> str:
    return f"""
    <div class="price-splash {cls}">
      <svg viewBox="0 0 260 88" preserveAspectRatio="none">
        <path d="M14,13 C72,4 188,4 246,13 C257,20 259,39 250,49 C258,61 249,77 233,80 C176,87 82,87 21,79 C6,76 2,58 11,46 C3,35 5,18 14,13 Z" fill="#D9161D"/>
        <path d="M20,77 C88,84 174,84 238,77" stroke="#8A050A" stroke-width="5.5" stroke-linecap="round" fill="none"/>
      </svg>
      <span>{price_str}</span>
    </div>
    """


COMMON_CSS = f"""
@font-face {{ font-family: 'Baloo'; src: url('{f_baloo}') format('truetype'); font-weight: 800; }}
@font-face {{ font-family: 'Script'; src: url('{f_script}') format('truetype'); font-weight: 700; }}
@font-face {{ font-family: 'BVP'; src: url('{f_bvp_sb}') format('truetype'); font-weight: 600; }}
@font-face {{ font-family: 'BVP'; src: url('{f_bvp_b}') format('truetype'); font-weight: 700; }}
@font-face {{ font-family: 'BVP'; src: url('{f_bvp_eb}') format('truetype'); font-weight: 800; }}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
  width: {W_PAGE}px;
  height: {H_PAGE}px;
  overflow: hidden;
  font-family: 'BVP', sans-serif;
  background: #F9E7C4;
  color: #23110B;
}}

.page {{
  position: relative;
  width: {W_PAGE}px;
  height: {H_PAGE}px;
  background:
    radial-gradient(circle at 50% 12%, #FFFDF8 0%, rgba(255, 247, 228, 0.92) 38%, transparent 68%),
    radial-gradient(circle at 15% 48%, rgba(255, 196, 85, 0.34) 0%, transparent 52%),
    radial-gradient(circle at 85% 50%, rgba(255, 172, 85, 0.30) 0%, transparent 52%),
    linear-gradient(180deg, #FDF2DC 0%, #F9E5BE 54%, #F5DBA9 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 20px 0 20px;
}}

.bg-decor {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; }}

/* HEADER */
.header {{
  position: relative;
  z-index: 6;
  height: 228px;
  display: grid;
  grid-template-columns: 880px 1fr 900px;
  align-items: center;
  padding: 0 4px;
  margin-bottom: 30px;
}}
.brand-left {{ display: flex; align-items: center; gap: 14px; }}
.logo-giant {{
  width: 240px;
  height: 240px;
  flex-shrink: 0;
  transform: rotate(-4deg);
  filter: drop-shadow(0 10px 16px rgba(110, 20, 10, 0.24));
}}
.logo-giant img {{ width: 100%; height: 100%; object-fit: contain; }}
.brand-callig {{ display: flex; flex-direction: column; gap: 6px; flex: 1; }}
.kr-top-row {{ display: flex; align-items: center; gap: 14px; }}
.kr-headline {{ transform: rotate(-5deg); transform-origin: left center; }}
.kr-headline .line1 {{ font-family: 'Script', cursive; font-size: 64px; color: #2B130C; line-height: 0.92; text-shadow: 0 3px 0 #FFFFFF; }}
.kr-headline .line2 {{ font-family: 'Script', cursive; font-size: 62px; color: #D41820; line-height: 0.98; text-shadow: 0 3px 0 #FFFFFF; }}
.kr-stamp {{
  background: linear-gradient(135deg, #D9161E 0%, #B00B12 100%);
  color: #FFE95C;
  border: 3px solid #FFD236;
  border-radius: 18px;
  padding: 8px 14px;
  text-align: center;
  transform: rotate(3deg);
  box-shadow: 0 6px 14px rgba(130, 15, 15, 0.22);
}}
.kr-stamp .st1 {{ font-family: 'Baloo', sans-serif; font-size: 22px; line-height: 1.02; color: #FFE95C; }}
.kr-stamp .st2 {{ font-size: 14.5px; font-weight: 800; color: #FFFFFF; margin-top: 2px; }}

.wifi-pill {{
  background: linear-gradient(90deg, #FFFDF9 0%, #FFF5DC 100%);
  border: 2.8px solid #E5A238;
  border-radius: 16px;
  padding: 8px 16px;
  box-shadow: 0 5px 12px rgba(150, 60, 10, 0.12);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}
.wifi-col {{ display: flex; flex-direction: column; gap: 2px; }}
.wifi-line {{ font-size: 20px; font-weight: 700; color: #361A10; }}
.wifi-line strong {{ color: #D11920; font-weight: 800; }}
.ac-tag {{
  background: #FFE57F;
  color: #8F110B;
  font-size: 16px;
  font-weight: 800;
  padding: 6px 12px;
  border-radius: 11px;
  border: 1.5px solid #E5A238;
  text-align: center;
  line-height: 1.15;
}}

.header-center {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-start; position: relative; }}
.hero-title-svg {{ width: 1180px; height: 158px; overflow: visible; }}
.ribbon-wrap {{
  margin-top: -22px;
  position: relative;
  width: 860px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 6px 12px rgba(140, 12, 16, 0.26));
}}
.ribbon-wrap svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.ribbon-wrap span {{
  position: relative;
  z-index: 2;
  font-family: 'Script', cursive;
  font-size: 46px;
  line-height: 1.25;
  padding-bottom: 4px;
  color: #FFFFFF;
  letter-spacing: 0.4px;
  transform: rotate(-1.2deg);
  text-shadow: 0 3px 6px rgba(80, 0, 0, 0.38);
}}

.info-right {{
  justify-self: end;
  display: flex;
  align-items: center;
  gap: 14px;
  background: rgba(255, 252, 244, 0.94);
  border: 2.5px solid #ECA944;
  border-radius: 22px;
  padding: 10px 14px 10px 20px;
  box-shadow: 0 6px 16px rgba(140, 50, 10, 0.10);
}}
.info-stack {{ display: flex; flex-direction: column; align-items: flex-end; gap: 6px; text-align: right; }}
.branch-line {{ font-size: 20.5px; font-weight: 800; color: #2B140D; line-height: 1.22; }}
.branch-line span.pin {{ display: inline-block; background: #D61820; color: #FFE866; font-size: 16.5px; padding: 1px 9px; border-radius: 99px; margin-right: 5px; }}
.hotline-big {{ display: flex; align-items: center; gap: 9px; font-family: 'Baloo', sans-serif; font-size: 45px; color: #C9141B; line-height: 1; text-shadow: 0 2px 0 #FFFFFF; }}
.hours-pill {{ background: #B91319; color: #FFF9E6; font-size: 18.5px; font-weight: 700; padding: 5px 16px; border-radius: 99px; }}
.qr-bank-card {{ background: #FFFFFF; border: 3px solid #D91820; border-radius: 16px; padding: 6px 8px 5px 8px; display: flex; flex-direction: column; align-items: center; }}
.qr-bank-card img {{ width: 150px; height: 150px; object-fit: contain; image-rendering: crisp-edges; }}
.qr-bank-caption {{ margin-top: 3px; text-align: center; font-size: 14px; font-weight: 800; color: #2B140D; line-height: 1.15; }}
.qr-bank-caption strong {{ color: #D1181F; font-size: 15.5px; display: block; }}

/* CATEGORY PANELS — TIGHT PADDING SO FOOD & TEXT FILL MAXIMUM AREA! */
.cat-panel {{
  position: relative;
  background: linear-gradient(180deg, #FFFDF9 0%, #FFF4DE 100%);
  border: 3.5px solid #DF7E4D;
  border-radius: 28px;
  padding: 34px 8px 12px 8px;
  box-shadow: 0 10px 22px rgba(140, 50, 12, 0.10);
}}
.cat-panel.gold-panel {{
  background: linear-gradient(180deg, #FFFDF6 0%, #FFEFCA 100%);
  border: 3.5px solid #DC8618;
}}
.brush-header {{
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%);
  height: 72px;
  padding: 0 52px 0 64px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  filter: drop-shadow(0 5px 9px rgba(140, 68, 0, 0.22));
  z-index: 4;
}}
.brush-header .brush-bg {{ position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; }}
.brush-header .crown-svg {{ position: absolute; left: -18px; top: -14px; width: 76px; height: 62px; z-index: 3; }}
.brush-header .bh-title {{ position: relative; z-index: 2; font-family: 'Baloo', sans-serif; font-size: 39px; color: #23110A; letter-spacing: 0.4px; line-height: 1; }}
.brush-header.red-bh {{ padding: 0 50px; }}
.brush-header.red-bh .bh-title {{ color: #FFFFFF; text-shadow: 0 2px 4px rgba(80, 0, 0, 0.38); }}

.cat-subline {{
  text-align: center;
  font-family: 'Script', cursive;
  font-size: 31px;
  color: #C9181F;
  margin-top: -6px;
  margin-bottom: 2px;
  line-height: 1.05;
}}

/* FULL-SCALE FLOATING CUTOUT STAGE — EXPLICIT WIDTH & HEIGHT SO EVERY DISH SCALES BIG! */
.cutout-stage {{
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at 50% 56%, rgba(255, 202, 74, 0.38) 0%, rgba(255, 222, 130, 0.14) 52%, transparent 74%);
}}
.cutout-stage img {{
  width: 97%;
  height: 98%;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 12px 15px rgba(88, 26, 6, 0.26));
}}
.front-body .cutout-stage img {{
  width: 99%;
  height: 100%;
  transform: scale(1.07);
}}

/* GIANT PUNCHY PRICE SPLASHES */
.price-splash {{
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 88%;
  max-width: 274px;
  height: 70px;
  padding: 0 24px;
  filter: drop-shadow(0 5px 8px rgba(165, 12, 18, 0.25));
}}
.price-splash svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.price-splash span {{
  position: relative;
  z-index: 2;
  font-family: 'Baloo', sans-serif;
  font-size: 51px;
  color: #FFE838;
  line-height: 1;
  letter-spacing: 0.5px;
  text-shadow: 0 3px 0 #7C070B;
}}
.price-splash.sm {{
  width: auto;
  min-width: 206px;
  height: 58px;
  padding: 0 22px;
}}
.price-splash.sm span {{
  font-size: 37px;
  color: #FFE94D;
  text-shadow: 0 2.5px 0 #7C070B;
}}

/* FOOTER */
.sauce-footer {{
  position: relative;
  z-index: 6;
  margin: 0 -20px;
  height: 130px;
  background: linear-gradient(90deg, #B10C12 0%, #D91820 50%, #B10C12 100%);
  padding: 14px 36px 0 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  color: #FFFFFF;
}}
.footer-wave-svg {{ position: absolute; top: -22px; left: 0; width: 100%; height: 28px; pointer-events: none; }}
.sf-script {{ font-family: 'Script', cursive; font-size: 46px; color: #FFF8E8; text-shadow: 0 3px 8px rgba(80, 0, 0, 0.35); white-space: nowrap; }}
.sf-center-pill {{
  background: linear-gradient(90deg, #FFE252 0%, #FFC21A 100%);
  color: #7D090E;
  font-family: 'Baloo', sans-serif;
  font-size: 25px;
  padding: 9px 28px;
  border-radius: 99px;
  border: 3px solid #FFF7C2;
  box-shadow: 0 5px 14px rgba(70, 0, 0, 0.25);
  white-space: nowrap;
}}
.sf-badges {{ display: flex; align-items: center; gap: 20px; }}
.sf-badge {{ display: flex; align-items: center; gap: 11px; padding-right: 18px; border-right: 2px solid rgba(255, 225, 140, 0.38); }}
.sf-badge:last-of-type {{ border-right: none; padding-right: 4px; }}
.sf-circle {{ width: 54px; height: 54px; border-radius: 50%; background: linear-gradient(180deg, #FFE259 0%, #FFB81C 100%); border: 3px solid #FFF5C0; display: flex; align-items: center; justify-content: center; }}
.sf-btxt {{ font-size: 19.5px; font-weight: 700; line-height: 1.18; color: #FFF7E2; white-space: nowrap; }}
.sf-fb {{ display: flex; align-items: center; gap: 11px; background: rgba(0, 0, 0, 0.22); border: 2px solid rgba(255, 224, 110, 0.75); border-radius: 15px; padding: 5px 10px 5px 14px; }}
.sf-fb-lbl {{ text-align: right; font-size: 16.5px; font-weight: 700; line-height: 1.18; color: #FFEAA0; white-space: nowrap; }}
.sf-fb img {{ width: 74px; height: 74px; background: #FFFFFF; padding: 4px; border-radius: 9px; }}
"""

BG_DECOR_SVG = """
<svg class="bg-decor" viewBox="0 0 3000 1941" preserveAspectRatio="none">
  <g fill="#FFB81C" opacity="0.65">
    <circle cx="905" cy="40" r="9"/><circle cx="2085" cy="42" r="9"/>
    <path d="M915,175 L924,195 L945,204 L924,213 L915,233 L906,213 L885,204 L906,195 Z"/>
    <path d="M2075,172 L2084,192 L2105,201 L2084,210 L2075,230 L2066,210 L2045,201 L2066,192 Z"/>
  </g>
</svg>
"""


def build_header_html(lang: str) -> str:
    is_vi = lang == "vi"
    l1 = "Gà Rán" if is_vi else "Korean"
    l2 = "Hàn Quốc" if is_vi else "Chicken"
    st1 = "100% GÀ TƯƠI" if is_vi else "FRESH DAILY"
    st2 = "SỐT CHUẨN HÀN" if is_vi else "KOREAN SAUCE"
    ac_txt = "PHÒNG LẠNH<br/>THOÁNG MÁT" if is_vi else "COOL A/C<br/>DINE-IN"
    ribbon = "Ăn ngon - Vui hết nấc! • Chuẩn vị Hàn Quốc" if is_vi else "Crispy & Juicy - Authentic Korean Taste!"
    b1 = '<span class="pin">CS1</span> 38 Nguyễn Đình Chiểu, Dốc ĐH Nha Trang' if is_vi else '<span class="pin">B1</span> 38 Nguyen Dinh Chieu (Nha Trang Univ.)'
    b2 = '<span class="pin">CS2</span> 35 Trần Hữu Duyệt, Vĩnh Điềm Trung' if is_vi else '<span class="pin">B2</span> 35 Tran Huu Duyet, Vinh Diem Trung'
    deliv = "10:00 - 22:00 &nbsp;•&nbsp; Grab • ShopeeFood • K Delivery" if is_vi else "10:00 - 22:00 &nbsp;•&nbsp; Grab • ShopeeFood • K Delivery"

    ic_phone = '<svg width="36" height="36" viewBox="0 0 28 28" fill="none"><rect width="28" height="28" rx="8" fill="#D41820"/><path d="M9.5 7.5C9.5 7.5 11.5 7 12.2 9.2L13 11.5C13.2 12.2 12.4 13 11.8 13.5C12.6 15.2 13.8 16.4 15.5 17.2C16 16.6 16.8 15.8 17.5 16L19.8 16.8C22 17.5 21.5 19.5 21.5 19.5C20.8 21 19.2 21.5 17.5 21C12.5 19.8 9.2 16.5 8 11.5C7.5 9.8 8 8.2 9.5 7.5Z" fill="#FFE853"/></svg>'
    ic_wifi = '<svg width="19" height="15" viewBox="0 0 24 20" fill="none" style="vertical-align:-2px;margin-right:4px;"><path d="M2 7C7.5 2 16.5 2 22 7M5.5 11C9.2 7.5 14.8 7.5 18.5 11M9 15C10.8 13.3 13.2 13.3 15 15" stroke="#D11920" stroke-width="2.8" stroke-linecap="round"/><circle cx="12" cy="18" r="2" fill="#D11920"/></svg>'
    ic_key = '<svg width="19" height="15" viewBox="0 0 24 20" fill="none" style="vertical-align:-2px;margin-right:4px;"><circle cx="7.5" cy="10" r="4.5" stroke="#E08A00" stroke-width="2.8"/><path d="M12 10H22M18 10V14M21 10V13" stroke="#E08A00" stroke-width="2.8" stroke-linecap="round"/></svg>'

    return f"""
    <div class="header">
      <div class="brand-left">
        <div class="logo-giant"><img src="{IMG['logo.png']}" /></div>
        <div class="brand-callig">
          <div class="kr-top-row">
            <div class="kr-headline"><div class="line1">{l1}</div><div class="line2">{l2}</div></div>
            <div class="kr-stamp"><div class="st1">{st1}</div><div class="st2">★ {st2} ★</div></div>
          </div>
          <div class="wifi-pill">
            <div class="wifi-col">
              <div class="wifi-line">{ic_wifi}Wifi: <strong>GÀ RÁN FEEL CHICKEN</strong></div>
              <div class="wifi-line">{ic_key}Pass: <strong>feelchicken</strong></div>
            </div>
            <div class="ac-tag">{ac_txt}</div>
          </div>
        </div>
      </div>

      <div class="header-center">
        <svg class="hero-title-svg" viewBox="0 0 1220 175">
          <defs>
            <path id="fcArch" d="M 45,148 Q 610,86 1175,148" />
            <linearGradient id="heroRed" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#FF3A2E"/><stop offset="55%" stop-color="#D9151C"/><stop offset="100%" stop-color="#A50B10"/>
            </linearGradient>
            <filter id="heroSh" x="-10%" y="-15%" width="120%" height="140%">
              <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#6B1208" flood-opacity="0.28"/>
            </filter>
          </defs>
          <g stroke="#FFC719" stroke-width="9" stroke-linecap="round">
            <line x1="28" y1="70" x2="-4" y2="54"/><line x1="20" y1="106" x2="-12" y2="108"/><line x1="34" y1="140" x2="6" y2="156"/>
            <line x1="1192" y1="70" x2="1224" y2="54"/><line x1="1200" y1="106" x2="1232" y2="108"/><line x1="1186" y1="140" x2="1214" y2="156"/>
          </g>
          <g filter="url(#heroSh)" font-family="'Baloo', sans-serif" font-weight="800" font-size="140" letter-spacing="3.5" text-anchor="middle">
            <text dy="10" fill="#FFD22E" stroke="#FFD22E" stroke-width="34" stroke-linejoin="round" paint-order="stroke fill"><textPath href="#fcArch" startOffset="50%">FEEL CHICKEN</textPath></text>
            <text dy="6" fill="#8C080D" stroke="#8C080D" stroke-width="18" stroke-linejoin="round" paint-order="stroke fill"><textPath href="#fcArch" startOffset="50%">FEEL CHICKEN</textPath></text>
            <text dy="0" fill="url(#heroRed)" stroke="#FFFDF5" stroke-width="7" stroke-linejoin="round" paint-order="stroke fill"><textPath href="#fcArch" startOffset="50%">FEEL CHICKEN</textPath></text>
          </g>
        </svg>
        <div class="ribbon-wrap">
          <svg viewBox="0 0 860 96" preserveAspectRatio="none">
            <polygon points="0,26 52,16 46,54 62,86 0,76 22,51" fill="#9A090F"/>
            <polygon points="860,26 808,16 814,54 798,86 860,76 838,51" fill="#9A090F"/>
            <path d="M40,14 Q430,2 820,14 L808,82 Q430,70 52,82 Z" fill="#D91820" stroke="#FFD23F" stroke-width="3.2"/>
          </svg>
          <span>{ribbon}</span>
        </div>
      </div>

      <div class="info-right">
        <div class="info-stack">
          <div class="branch-line">{b1}</div>
          <div class="branch-line">{b2}</div>
          <div class="hotline-big">{ic_phone} 0796 601 106</div>
          <div class="hours-pill">{deliv}</div>
        </div>
        <div class="qr-bank-card">
          <img src="{IMG['tpbank_qr.png']}" />
          <div class="qr-bank-caption">TP BANK • LE HUU KHANG<strong>0000 5989 856</strong></div>
        </div>
      </div>
    </div>
    """


def build_footer_html(lang: str) -> str:
    is_vi = lang == "vi"
    quote = "Feel Chicken - Cùng bạn tạo nên những bữa ăn thật ngon! ♡♡" if is_vi else "Feel Chicken - Creating joyful, delicious meals together! ♡♡"
    mid_cta = "★ ĐẶT MÓN GIAO NÓNG: 0796 601 106 ★" if is_vi else "★ HOT DELIVERY HOTLINE: 0796 601 106 ★"
    b1 = "Nguyên liệu<br/>an toàn" if is_vi else "Safe Quality<br/>Ingredients"
    b2 = "Gà tươi<br/>mỗi ngày" if is_vi else "100% Fresh<br/>Chicken Daily"
    b3 = "Giao hàng<br/>nhanh chóng" if is_vi else "Fast & Hot<br/>Delivery"
    fb_lbl = "Quét xem<br/>Fanpage" if is_vi else "Scan our<br/>Fanpage"

    ic_fork = '<svg width="28" height="28" viewBox="0 0 28 28" fill="none"><path d="M8 4V12C8 14 10 15 10 15V24M8 4V10M11 4V10M5 4V10C5 13 8 15 8 15M19 4C17 7 17 13 19 15V24" stroke="#9E0B11" stroke-width="2.6" stroke-linecap="round"/></svg>'
    ic_shield = '<svg width="28" height="28" viewBox="0 0 28 28" fill="none"><path d="M14 3L23 7V14C23 19.5 19 23.5 14 25.5C9 23.5 5 19.5 5 14V7L14 3Z" stroke="#9E0B11" stroke-width="2.6" fill="none"/><path d="M10 14L13 17L18.5 11" stroke="#9E0B11" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    ic_scooter = '<svg width="30" height="28" viewBox="0 0 30 28" fill="none"><circle cx="7.5" cy="21" r="3.5" stroke="#9E0B11" stroke-width="2.5"/><circle cx="22.5" cy="21" r="3.5" stroke="#9E0B11" stroke-width="2.5"/><path d="M11 21H18L20 12H16M19 8H23L25 16H21M5 17H11L13 12H8" stroke="#9E0B11" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

    return f"""
    <div class="sauce-footer">
      <svg class="footer-wave-svg" viewBox="0 0 3000 30" preserveAspectRatio="none">
        <path d="M0,30 L0,15 Q250,-4 520,15 T1080,13 T1650,17 T2240,11 T2780,15 L3000,9 L3000,30 Z" fill="#C41319"/>
        <path d="M0,17 Q250,-2 520,17 T1080,15 T1650,19 T2240,13 T2780,17 L3000,11" stroke="#FFD242" stroke-width="4" fill="none"/>
      </svg>
      <div class="sf-script">{quote}</div>
      <div class="sf-center-pill">{mid_cta}</div>
      <div class="sf-badges">
        <div class="sf-badge"><div class="sf-circle">{ic_fork}</div><div class="sf-btxt">{b1}</div></div>
        <div class="sf-badge"><div class="sf-circle">{ic_shield}</div><div class="sf-btxt">{b2}</div></div>
        <div class="sf-badge"><div class="sf-circle">{ic_scooter}</div><div class="sf-btxt">{b3}</div></div>
        <div class="sf-fb">
          <div class="sf-fb-lbl">{fb_lbl}<br/><strong>Feel Chicken</strong></div>
          <img src="{IMG['fanpage_qr.png']}" />
        </div>
      </div>
    </div>
    """


def build_front_page_html(lang: str) -> str:
    is_vi = lang == "vi"

    solo_items = [
        ("cb00_com_ga.png", "CƠM GÀ FEEL" if is_vi else "CHICKEN RICE", "1 đùi gà (chọn sốt) +<br/>Salad trộn + 1 Coca" if is_vi else "1 Thigh (choose sauce)<br/>+ Fresh salad + 1 Coca", "45K"),
        ("cb01_solo.png", "FEEL SOLO", "1 đùi gà (chọn sốt) +<br/>Khoai tây chiên + 1 Coca" if is_vi else "1 Thigh (choose sauce)<br/>+ French fries + 1 Coca", "59K"),
        ("cb02_meal.png", "FEEL MEAL", "1 đùi gà (chọn sốt) +<br/>Mì tương đen + 1 Coca" if is_vi else "1 Thigh + Korean<br/>black noodles + 1 Coca", "79K"),
        ("cb03_spicy.png", "FEEL SPICY", "1 đùi gà (chọn sốt) +<br/>Mì cay Hàn Quốc + 1 Coca" if is_vi else "1 Thigh + Korean<br/>spicy noodles + 1 Coca", "89K"),
        ("cb04_cheese.png", "FEEL CHEESE", "1 đùi gà + Bánh gạo<br/>lắc phô mai + 1 Coca" if is_vi else "1 Thigh + Cheese<br/>shake rice cakes + 1 Coca", "89K"),
    ]

    couple_items = [
        ("cb05_love.png", "FEEL LOVE", "2 đùi gà (chọn sốt) +<br/>Tokbokki + Salad trộn" if is_vi else "2 Chicken thighs +<br/>Tokbokki + Fresh salad", "129K"),
        ("cb06_couple.png", "FEEL COUPLE", "2 đùi gà (chọn sốt) +<br/>Mì tương đen Hàn Quốc" if is_vi else "2 Chicken thighs +<br/>Korean black noodles", "139K"),
        ("cb07_party.png", "FEEL PARTY", "4 miếng gà + Khoai tây +<br/>Tokbokki + 2 Coca" if is_vi else "4 Chicken pcs + Fries +<br/>Tokbokki + 2 Coca", "179K"),
    ]

    group_items = [
        ("cb08_friends.png", "FEEL FRIENDS", "6 miếng gà + Tokbokki +<br/>Khoai tây + Salad + 3 Coca" if is_vi else "6 Chicken pcs + Tokbokki +<br/>Fries + Salad + 3 Coca", "249K"),
        ("cb09_nguvi.png", "COMBO NGŨ VỊ" if is_vi else "5-FLAVOR COMBO", "5 đùi gà đủ 5 sốt + Khoai tây +<br/>Salad / Tokbokki / Mì tương đen" if is_vi else "5 Thighs (5 sauces) + Fries +<br/>Salad / Tokbokki / Black noodles", "259K"),
        ("cb10_family.png", "FEEL FAMILY", "8 miếng gà + Tokbokki +<br/>Khoai tây + Salad + 4 Coca" if is_vi else "8 Chicken pcs + Tokbokki +<br/>Fries + Salad + 4 Coca", "329K"),
    ]

    sauces = [
        ("s1_phomai.jpg", "Sốt Phô Mai" if is_vi else "Cheese Sauce", "Sốt sánh mịn hoặc lắc bột phô mai" if is_vi else "Creamy sauce or cheese powder"),
        ("s2_cayhan.jpg", "Sốt Cay Hàn Quốc" if is_vi else "Korean Spicy", "Ớt Gochujang cay nồng cuốn miệng" if is_vi else "Fiery Gochujang sweet-spicy glaze"),
        ("s3_toicay.jpg", "Sốt Tỏi Cay" if is_vi else "Spicy Garlic", "Thơm lừng tỏi phi vàng giòn đậm vị" if is_vi else "Crispy fried garlic zesty glaze"),
        ("s4_chanhday.jpg", "Sốt Chanh Dây" if is_vi else "Passion Fruit", "Chua ngọt thanh mát từ chanh dây tươi" if is_vi else "Tangy-sweet fresh passion fruit"),
        ("s5_tuonghan.jpg", "Sốt Tương Hàn" if is_vi else "Korean Soy", "Mặn ngọt dịu dàng, trẻ em cực mê" if is_vi else "Savory-sweet honey soy glaze"),
    ]

    def render_cutout_lanes(items, img_h: int):
        out = []
        for im_n, name, desc, pr in items:
            out.append(f"""
            <div class="cut-lane">
              <div class="cutout-stage" style="height:{img_h}px;">
                <img src="{IMG[im_n]}" />
              </div>
              <div class="lane-name">{name}</div>
              <div class="lane-desc">{desc}</div>
              <div class="lane-price">{price_splash_html(pr)}</div>
            </div>
            """)
        return "".join(out)

    sauce_html = "".join(
        f"""
        <div class="sauce-lane">
          <div class="sauce-medallion"><img src="{IMG[im_n]}" /></div>
          <div class="sauce-meta">
            <div class="sauce-title">{sn}</div>
            <div class="sauce-note">{ss}</div>
          </div>
        </div>
        """
        for im_n, sn, ss in sauces
    )

    t_solo = "COMBO 1 NGƯỜI & CƠM GÀ" if is_vi else "SOLO COMBOS & CHICKEN RICE"
    s_solo = "— Ăn ngon - Đủ vị - Nhanh gọn mỗi ngày —" if is_vi else "— Crispy, Complete & Satisfying Every Day —"
    t_couple = "COMBO 2 NGƯỜI" if is_vi else "COUPLE COMBOS"
    s_couple = "— Rủ bạn cùng ăn - Nhân đôi niềm vui —" if is_vi else "— Share Together, Double the Joy —"
    t_group = "COMBO NHÓM BẠN & GIA ĐÌNH" if is_vi else "GROUP & FAMILY FEASTS"
    s_group = "— Ăn thật đã - Giá cực hời cho cả hội —" if is_vi else "— Grand Platters, Best Value for Groups —"
    t_sauce = "5 VỊ SỐT HÀN QUỐC ĐỘC QUYỀN – TỰ CHỌN CHO MỌI PHẦN GÀ" if is_vi else "5 SIGNATURE KOREAN SAUCES – FREE CHOICE FOR ALL CHICKEN"

    front_css = """
    .front-body {
      position: relative;
      z-index: 5;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 4px 0 16px 0;
      gap: 36px;
    }
    .lanes-5 { display: grid; grid-template-columns: repeat(5, 1fr); }
    .lanes-3 { display: grid; grid-template-columns: repeat(3, 1fr); }
    .row-mid-split { display: grid; grid-template-columns: 1fr 1.05fr; gap: 20px; }

    .cut-lane {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 0 6px 2px 6px;
      border-right: 2px dashed rgba(205, 125, 65, 0.36);
    }
    .cut-lane:last-child { border-right: none; }

    /* GIANT BOLD COMBO TITLES & DESCRIPTIONS! */
    .lane-name {
      font-family: 'Baloo', sans-serif;
      font-size: 39px;
      color: #C21219;
      line-height: 1.02;
      margin-top: 2px;
      margin-bottom: 4px;
      letter-spacing: 0.3px;
    }
    .lane-desc {
      font-size: 23.5px;
      font-weight: 800;
      color: #2D160D;
      line-height: 1.24;
      min-height: 58px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 8px;
    }
    .lane-price { width: 100%; display: flex; justify-content: center; margin-top: auto; }

    .sauce-panel {
      padding: 36px 12px 12px 12px !important;
      background: linear-gradient(90deg, #FFEEC4 0%, #FFFBF0 50%, #FFEEC4 100%) !important;
      border: 3.5px solid #D94528 !important;
    }
    .sauce-row { display: grid; grid-template-columns: repeat(5, 1fr); }
    .sauce-lane {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 2px 12px;
      border-right: 2px dashed rgba(205, 125, 65, 0.34);
    }
    .sauce-lane:last-child { border-right: none; }
    .sauce-medallion {
      width: 156px;
      height: 156px;
      flex-shrink: 0;
      border-radius: 50%;
      overflow: hidden;
      border: 4.5px solid #FFB81C;
      outline: 3px solid #FFFFFF;
      box-shadow: 0 7px 15px rgba(150, 45, 0, 0.24);
    }
    .sauce-medallion img { width: 100%; height: 100%; object-fit: cover; }
    .sauce-meta { flex: 1; display: flex; flex-direction: column; align-items: flex-start; gap: 5px; }
    .sauce-title { font-family: 'Baloo', sans-serif; font-size: 33px; color: #C9151C; line-height: 1.04; }
    .sauce-note { font-size: 20.5px; font-weight: 700; color: #3D2216; line-height: 1.22; }
    """

    return f"""<!DOCTYPE html>
    <html lang="{lang}">
    <head><meta charset="utf-8"><style>{COMMON_CSS}{front_css}</style></head>
    <body>
      <div class="page">
        {BG_DECOR_SVG}
        {build_header_html(lang)}

        <div class="front-body">
          <div class="cat-panel">
            <div class="brush-header">{SVG_YELLOW_BRUSH}{SVG_CROWN_BIG}<span class="bh-title">{t_solo}</span></div>
            <div class="cat-subline">{s_solo}</div>
            <div class="lanes-5">{render_cutout_lanes(solo_items, 294)}</div>
          </div>

          <div class="row-mid-split">
            <div class="cat-panel">
              <div class="brush-header">{SVG_YELLOW_BRUSH}{SVG_CROWN_BIG}<span class="bh-title">{t_couple}</span></div>
              <div class="cat-subline">{s_couple}</div>
              <div class="lanes-3">{render_cutout_lanes(couple_items, 304)}</div>
            </div>

            <div class="cat-panel gold-panel">
              <div class="brush-header">{SVG_YELLOW_BRUSH}{SVG_CROWN_BIG}<span class="bh-title">{t_group}</span></div>
              <div class="cat-subline">{s_group}</div>
              <div class="lanes-3">{render_cutout_lanes(group_items, 304)}</div>
            </div>
          </div>

          <div class="cat-panel sauce-panel">
            <div class="brush-header red-bh" style="height:66px; top:-33px;">{SVG_RED_BRUSH_HEADER}<span class="bh-title" style="font-size:32px;">{SVG_FLAME}{t_sauce}</span></div>
            <div class="sauce-row">{sauce_html}</div>
          </div>
        </div>

        {build_footer_html(lang)}
      </div>
    </body>
    </html>
    """


def build_back_page_html(lang: str) -> str:
    is_vi = lang == "vi"

    chicken_singles = [
        (
            "ga_phile.png",
            "GÀ PHI LÊ GIÒN" if is_vi else "CHICKEN FILLET",
            "1 phần phi lê gà không xương<br/>• <strong>Tự chọn 1 trong 5 vị sốt Hàn</strong>" if is_vi else "Boneless crispy chicken fillet<br/>• <strong>Choose 1 of 5 Korean sauces</strong>",
            "45.000đ",
        ),
        (
            "cb_dui_canh.png",
            "ĐÙI / CÁNH GÀ RÁN" if is_vi else "THIGH / WING",
            "• Đùi gà: <strong>39K</strong> &nbsp;|&nbsp; Cánh: <strong>35K</strong><br/>• <strong>Tự chọn 1 trong 5 vị sốt Hàn</strong>" if is_vi else "• Thigh: <strong>39K</strong> &nbsp;|&nbsp; Wing: <strong>35K</strong><br/>• <strong>Choose 1 of 5 Korean sauces</strong>",
            "39K / 35K",
        ),
        (
            "cb11_my_y.png",
            "COMBO MỲ Ý GÀ" if is_vi else "PASTA COMBO",
            "• 1 Mì Ý + 1 Đùi + 1 Coca: <strong>79K</strong><br/>• 2 Mì Ý + 2 Đùi + 2 Coca: <strong>149K</strong>" if is_vi else "• 1 Pasta + 1 Thigh + Coca: <strong>79K</strong><br/>• 2 Pasta + 2 Thighs + 2 Coca: <strong>149K</strong>",
            "79K / 149K",
        ),
    ]

    fast_dishes = [
        ("mi_cay_haisan.png", "Mì Cay Hải Sản" if is_vi else "Spicy Seafood", "Tôm, mực, chả cá cay nồng" if is_vi else "Prawns, squid & fish cake", "55.000đ"),
        ("mi_cay_bachtuoc.png", "Mì Cay Bạch Tuộc" if is_vi else "Spicy Octopus", "Bạch tuộc giòn sần sật" if is_vi else "Whole baby octopus hotpot", "55.000đ"),
        ("mi_cay_duiga.png", "Mì Cay Đùi Gà" if is_vi else "Spicy Chicken", "Đùi gà thấm đẫm súp cay" if is_vi else "Tender chicken thigh hotpot", "55.000đ"),
        ("mi_tuong_den.png", "Mì Tương Đen" if is_vi else "Black Noodles", "Sốt tương đen trứng lòng đào" if is_vi else "Jajangmyeon w/ boiled egg", "42.000đ"),
        ("mi_tuong_den_gacay.png", "Mì Đen Gà Cay" if is_vi else "Spicy Chick Black", "Mì tương đen kèm gà sốt cay" if is_vi else "Topped w/ spicy chicken", "60.000đ"),
        ("mi_y.png", "Mì Ý Thịt Bằm" if is_vi else "Spaghetti", "Sốt bò bằm cà chua thơm ngậy" if is_vi else "Rich minced-beef tomato", "40.000đ"),
        ("tokbokki.png", "Tokbokki Hàn" if is_vi else "Classic Tokbokki", "Bánh gạo chả cá cay ngọt" if is_vi else "Chewy rice & fish cakes", "39.000đ"),
        ("tokbokki_phomai.png", "Tokbokki Phô Mai" if is_vi else "Cheese Tokbokki", "Phủ phô mai béo ngậy" if is_vi else "Melted golden mozzarella", "40.000đ"),
        ("salad.png", "Salad Trộn" if is_vi else "Garden Salad", "Rau củ tươi giòn sốt mè" if is_vi else "Crisp veggies & sesame", "25.000đ"),
        ("banh_gao_lac.png", "Bánh Gạo Lắc" if is_vi else "Cheese Rice Cake", "Chiên giòn lắc phô mai" if is_vi else "Crispy w/ cheese powder", "25.000đ"),
    ]

    drinks = [
        ("dr01_soju.png", "Rượu Soju" if is_vi else "Soju Wine", "Chai 360ml Hàn" if is_vi else "360ml bottle", "75.000đ"),
        ("dr02_coca_7up.png", "Coca / 7Up", "Lon ướp lạnh" if is_vi else "Chilled can", "15.000đ"),
        ("dr03_tra_tao.png", "Trà Táo" if is_vi else "Apple Tea", "Trà táo tươi mát" if is_vi else "Fresh apple tea", "25.000đ"),
        ("dr04_tra_dao.png", "Trà Đào" if is_vi else "Peach Tea", "Đào miếng giòn" if is_vi else "Sweet peach tea", "25.000đ"),
        ("dr05_nuoc_suoi.png", "Nước Suối" if is_vi else "Water", "Chai tinh khiết" if is_vi else "Pure water", "10.000đ"),
    ]

    sides = [
        ("khoai_tay_dia.png", "Khoai Tây Chiên" if is_vi else "French Fries", "Chiên vàng giòn rụm" if is_vi else "Golden crinkle fries", "25.000đ"),
        ("khoai_tay_hop.png", "Khoai Lắc Phô Mai" if is_vi else "Cheese Fries", "Lắc đẫm bột phô mai" if is_vi else "Rich cheese powder", "30.000đ"),
        ("phomai_que.png", "Phô Mai Que" if is_vi else "Cheese Sticks", "3 cái: 30K • 5 cái: 40K" if is_vi else "3 pcs: 30K • 5 pcs: 40K", "30K / 40K"),
        ("xuc_xich.png", "Xúc Xích Chiên" if is_vi else "Fried Sausage", "Khứa hoa vàng thơm" if is_vi else "Golden scored sausage", "10.000đ"),
    ]

    singles_html = "".join(
        f"""
        <div class="single-cut-row">
          <div class="cutout-stage single-cut-stage"><img src="{IMG[im_n]}" /></div>
          <div class="single-info">
            <div class="single-title">{sn}</div>
            <div class="single-desc">{sd}</div>
            <div class="single-price">{price_splash_html(sp, 'sm')}</div>
          </div>
        </div>
        """
        for im_n, sn, sd, sp in chicken_singles
    )

    def render_fast_cut_row(sub_items):
        return "".join(
            f"""
            <div class="fast-cut-lane">
              <div class="cutout-stage fast-cut-stage"><img src="{IMG[im_n]}" /></div>
              <div class="dish-title">{dn}</div>
              <div class="dish-note">{ds}</div>
              {price_splash_html(dp, 'sm')}
            </div>
            """
            for im_n, dn, ds, dp in sub_items
        )

    drinks_html = "".join(
        f"""
        <div class="drink-cut-lane">
          <div class="cutout-stage drink-cut-stage"><img src="{IMG[im_n]}" /></div>
          <div class="dish-title">{dn}</div>
          <div class="drink-sub">{dsub}</div>
          {price_splash_html(dp, 'sm')}
        </div>
        """
        for im_n, dn, dsub, dp in drinks
    )

    sides_html = "".join(
        f"""
        <div class="side-cut-cell">
          <div class="cutout-stage side-cut-stage"><img src="{IMG[im_n]}" /></div>
          <div class="side-meta">
            <div class="side-title">{an}</div>
            <div class="side-note">{ad}</div>
            {price_splash_html(ap, 'sm')}
          </div>
        </div>
        """
        for im_n, an, ad, ap in sides
    )

    t_singles = "GÀ RÁN LẺ & MỲ Ý" if is_vi else "FRIED CHICKEN & PASTA"
    t_dishes = "MÓN ĂN GỌN – FAST FOOD HÀN QUỐC" if is_vi else "KOREAN NOODLES, TOKBOKKI & SALAD"
    t_drinks = "GIẢI KHÁT – NƯỚC UỐNG" if is_vi else "REFRESHING DRINKS & SOJU"
    t_sides = "MÓN ĂN VẶT & GỌI THÊM" if is_vi else "CRISPY SNACKS & SIDES"

    back_css = """
    .back-body {
      position: relative;
      z-index: 5;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 4px 0 16px 0;
      gap: 38px;
    }
    .upper-split {
      display: grid;
      grid-template-columns: 880px 1fr;
      gap: 20px;
      align-items: stretch;
    }
    .upper-split > .cat-panel { display: flex; flex-direction: column; }

    .singles-stack { flex: 1; display: grid; grid-template-rows: repeat(3, 1fr); }
    .single-cut-row {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 6px 10px;
      border-bottom: 2px dashed rgba(205, 125, 65, 0.36);
    }
    .single-cut-row:last-child { border-bottom: none; }
    .single-cut-stage { width: 356px; height: 268px; flex-shrink: 0; }
    .single-info { flex: 1; display: flex; flex-direction: column; align-items: flex-start; justify-content: center; gap: 7px; }
    .single-title { font-family: 'Baloo', sans-serif; font-size: 39px; color: #C4141B; line-height: 1.02; }
    .single-desc { font-size: 22px; font-weight: 700; color: #361C12; line-height: 1.3; margin-bottom: 4px; }
    .single-desc strong { color: #C9151C; font-weight: 800; }
    .single-price { width: 100%; }
    .single-price .price-splash.sm { width: 94%; max-width: 292px; height: 64px; }
    .single-price .price-splash.sm span { font-size: 40px; }

    /* 2x5 BIG Fast Food Cutouts & BIG Text */
    .fast-rows-wrap { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .fast-row-5 { display: grid; grid-template-columns: repeat(5, 1fr); }
    .fast-divider {
      height: 2px;
      margin: 6px 14px;
      background: repeating-linear-gradient(90deg, rgba(205,125,65,0.36) 0, rgba(205,125,65,0.36) 10px, transparent 10px, transparent 18px);
    }
    .fast-cut-lane {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 0 6px;
      border-right: 2px dashed rgba(205, 125, 65, 0.34);
    }
    .fast-cut-lane:last-child { border-right: none; }
    .fast-cut-stage { height: 258px; margin-bottom: 2px; }
    .dish-title { font-family: 'Baloo', sans-serif; font-size: 33.5px; color: #1F0E08; line-height: 1.03; margin-bottom: 3px; }
    .dish-note { font-size: 20px; font-weight: 700; color: #4A2B1F; margin-bottom: 7px; line-height: 1.18; }

    /* Bottom Split: 5 Big Drinks + 2x2 Big Sides */
    .bot-split {
      display: grid;
      grid-template-columns: 1.15fr 1fr;
      gap: 20px;
      align-items: stretch;
    }
    .bot-split > .cat-panel { display: flex; flex-direction: column; }
    .drinks-row-5 { flex: 1; display: grid; grid-template-columns: repeat(5, 1fr); }
    .drink-cut-lane {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      text-align: center;
      padding: 2px 6px;
      border-right: 2px dashed rgba(205, 125, 65, 0.34);
    }
    .drink-cut-lane:last-child { border-right: none; }
    .drink-cut-stage { height: 274px; }
    .drink-sub { font-size: 19.5px; font-weight: 700; color: #5B3620; margin-bottom: 6px; }

    .sides-grid-2x2 { flex: 1; display: grid; grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(2, 1fr); }
    .side-cut-cell {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 6px 12px;
      border-right: 2px dashed rgba(205, 125, 65, 0.34);
      border-bottom: 2px dashed rgba(205, 125, 65, 0.34);
    }
    .side-cut-cell:nth-child(2n) { border-right: none; }
    .side-cut-cell:nth-child(n+3) { border-bottom: none; }
    .side-cut-stage { width: 268px; height: 198px; flex-shrink: 0; }
    .side-meta { flex: 1; display: flex; flex-direction: column; align-items: flex-start; justify-content: center; gap: 6px; }
    .side-title { font-family: 'Baloo', sans-serif; font-size: 33.5px; color: #C21219; line-height: 1.03; }
    .side-note { font-size: 20px; font-weight: 700; color: #4A2B1F; margin-bottom: 4px; line-height: 1.18; }
    """

    return f"""<!DOCTYPE html>
    <html lang="{lang}">
    <head><meta charset="utf-8"><style>{COMMON_CSS}{back_css}</style></head>
    <body>
      <div class="page">
        {BG_DECOR_SVG}
        {build_header_html(lang)}

        <div class="back-body">
          <div class="upper-split">
            <div class="cat-panel gold-panel">
              <div class="brush-header">{SVG_YELLOW_BRUSH}{SVG_CROWN_BIG}<span class="bh-title">{t_singles}</span></div>
              <div class="singles-stack">{singles_html}</div>
            </div>

            <div class="cat-panel">
              <div class="brush-header">{SVG_YELLOW_BRUSH}{SVG_CROWN_BIG}<span class="bh-title">{t_dishes}</span></div>
              <div class="fast-rows-wrap">
                <div class="fast-row-5">{render_fast_cut_row(fast_dishes[:5])}</div>
                <div class="fast-divider"></div>
                <div class="fast-row-5">{render_fast_cut_row(fast_dishes[5:])}</div>
              </div>
            </div>
          </div>

          <div class="bot-split">
            <div class="cat-panel">
              <div class="brush-header" style="padding:0 52px;">{SVG_YELLOW_BRUSH}<span class="bh-title">{t_drinks}</span></div>
              <div class="drinks-row-5">{drinks_html}</div>
            </div>

            <div class="cat-panel gold-panel">
              <div class="brush-header red-bh" style="padding:0 52px;">{SVG_RED_BRUSH_HEADER}<span class="bh-title">{t_sides}</span></div>
              <div class="sides-grid-2x2">{sides_html}</div>
            </div>
          </div>
        </div>

        {build_footer_html(lang)}
      </div>
    </body>
    </html>
    """


pages_spec = [
    ("menu_vi_front", "Menu - Việt - Trước.png", build_front_page_html("vi")),
    ("menu_vi_back", "Menu - Việt - Sau.png", build_back_page_html("vi")),
    ("menu_en_front", "Menu - English - Trước.png", build_front_page_html("en")),
    ("menu_en_back", "Menu - English - Sau.png", build_back_page_html("en")),
]

ASCII_TMP = BASE / "assets" / "tmp_render"
ASCII_TMP.mkdir(parents=True, exist_ok=True)

rendered_paths = []
for slug, out_png_name, html_str in pages_spec:
    html_file = ASCII_TMP / f"{slug}.html"
    tmp_png = ASCII_TMP / f"{slug}.png"
    out_png = OUT_DIR / out_png_name
    html_file.write_text(html_str, encoding="utf-8")
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={W_PAGE},{H_PAGE}",
            f"--screenshot={tmp_png}",
            html_file.resolve().as_uri(),
        ],
        check=True,
    )
    im_check = cv2.imread(str(tmp_png))
    print(f"Rendered V7 GIANT {slug} -> {out_png_name}: {im_check.shape}")
    shutil.copy2(tmp_png, out_png)
    rendered_paths.append(tmp_png)
    art_copy = ART_DIR / f"{slug}_v7_preview.png"
    rs_art = cv2.resize(im_check, (1600, int(round(1600 * H_PAGE / W_PAGE))), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(art_copy), rs_art)

# Save exact 100%-zoom comparison crop of FEEL SPICY (the exact spot user screenshotted!) + Back dishes
f_im = cv2.imread(str(rendered_paths[0]))
b_im = cv2.imread(str(rendered_paths[1]))
cv2.imwrite(str(SCR / "v7_zoom_feel_spicy.jpg"), f_im[250:900, 1740:2400], [int(cv2.IMWRITE_JPEG_QUALITY), 95])
cv2.imwrite(str(SCR / "v7_zoom_back_dishes.jpg"), b_im[250:1240, 880:2980], [int(cv2.IMWRITE_JPEG_QUALITY), 92])

pil_imgs = [Image.open(p).convert("RGB") for p in rendered_paths]
pdf_vi = OUT_DIR / "Menu_Feel_Chicken_Tieng_Viet_In_2_Mat_300DPI.pdf"
pdf_en = OUT_DIR / "Menu_Feel_Chicken_English_2_Sided_300DPI.pdf"
pil_imgs[0].save(str(pdf_vi), "PDF", resolution=300.0, save_all=True, append_images=[pil_imgs[1]])
pil_imgs[2].save(str(pdf_en), "PDF", resolution=300.0, save_all=True, append_images=[pil_imgs[3]])
print("V7 GIANT CUTOUT MENU & PDFs COMPLETED!")
