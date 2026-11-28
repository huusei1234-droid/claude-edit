# -*- coding: utf-8 -*-
"""
V5 — 10 ẤN PHẨM THIẾT KẾ THƯƠNG MẠI ĐỘC LẬP (`1600x2000` 4:5 `.JPG` ONLY — 0 FILE `.PSD`!):
- Hoàn toàn KHÔNG liên quan tới khung hình/bối cảnh video!
- MỖI THIẾT KẾ MỘT KIỂU BỐ CỤC, BẢNG MÀU & CONCEPT RIÊNG BIỆT (10 Archetypes khác hẳn nhau 100%!).
- Chữ lớn nổi bật, sản phẩm thật `SP_*_CUTOUT.png` phóng đại sắc nét, 0% chữ hay sản phẩm chạm mặt người!
"""
import base64
import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageCms, ImageDraw, ImageEnhance

BATCH_ROOT = Path(r"d:\AI\full studio\output\htpm-ngay-261125")
V5_IMG_DIR = BATCH_ROOT / "10_V5_Action_USP" / "01_Refs"
OUT_DIR = BATCH_ROOT / "11_V5_10_Unique_Designs"
HTML_TMP = OUT_DIR / "_html_tmp"
OUT_DIR.mkdir(parents=True, exist_ok=True)
HTML_TMP.mkdir(parents=True, exist_ok=True)

BRAND_KIT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")
PROD_DIR = BRAND_KIT / "products_cutout_png"
FONTS_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
LOGO_PNG = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124\10_Bai_Thiet_Ke_Soft_Editorial\ht_logo_33mp_clean.png")
if not LOGO_PNG.exists():
    LOGO_PNG = BRAND_KIT / "logos_png" / "ht_logo_official.png"

K6_DAY25_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026")
LOCAL_DAY25_DIR = Path(r"D:\XUẤT CAPCUT\hằng thu pharma\261125 - Ngày 25.11.2026")
ARTIFACT_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682")

W, H = 1600, 2000
SRGB_BYTES = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def find_browser() -> str:
    for p in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("No Chromium browser found!")


BROWSER = find_browser()


def data_uri(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "ttf": "font/ttf"}.get(ext, "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def prod_uri(cutout_fn: str, max_dim: int = 1200) -> str:
    """Crop tight alpha bbox, sharpen slightly, encode PNG data URI."""
    cache_p = HTML_TMP / f"_crop_{cutout_fn}"
    if not cache_p.exists():
        im = Image.open(PROD_DIR / cutout_fn).convert("RGBA")
        if im.getbbox():
            im = im.crop(im.getbbox())
        im.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        im = ImageEnhance.Sharpness(im).enhance(1.18)
        im.save(cache_p, format="PNG")
    return data_uri(cache_p)


def font_css() -> str:
    pairs = [
        ("BeVNSemi", "BeVietnamPro-SemiBold.ttf"),
        ("BeVNBold", "BeVietnamPro-Bold.ttf"),
        ("BeVNExtra", "BeVietnamPro-ExtraBold.ttf"),
        ("FrauncesBlk", "Fraunces-Black.ttf"),
        ("PlayfairBlk", "PlayfairDisplay-ExtraBold.ttf"),
        ("PlayfairItal", "PlayfairDisplay-BoldItalic.ttf"),
        ("ScriptVN", "DancingScript-Bold.ttf"),
    ]
    rules = []
    for fam, fn in pairs:
        fp = FONTS_DIR / fn
        if fp.exists():
            rules.append(f"@font-face {{ font-family: '{fam}'; src: url('{data_uri(fp)}') format('truetype'); }}")
    return "\n".join(rules)


BASE_CSS = f"""
{font_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1600px; height: 2000px; overflow: hidden; font-family: 'BeVNBold', sans-serif; -webkit-font-smoothing: antialiased; }}
.canvas {{ position: relative; width: 1600px; height: 2000px; overflow: hidden; }}
.bg-cover {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.ht-badge {{ display: inline-flex; align-items: center; gap: 14px; background: rgba(255,255,255,0.94); padding: 10px 24px 10px 12px; border-radius: 999px; box-shadow: 0 10px 28px rgba(0,0,0,0.12); }}
.ht-badge img {{ width: 54px; height: 54px; border-radius: 50%; object-fit: contain; }}
.ht-badge .b-txt {{ font-family: 'BeVNExtra'; font-size: 22px; letter-spacing: 0.05em; color: #8A1538; line-height: 1.15; }}
.ht-badge .b-sub {{ font-family: 'BeVNSemi'; font-size: 15px; color: #555; letter-spacing: 0.04em; display: block; }}
"""


def render_poster_html(name: str, body_html: str, out_jpg: Path):
    full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style></head><body>{body_html}</body></html>"
    hp = HTML_TMP / f"{name}.html"
    pp = HTML_TMP / f"{name}.png"
    hp.write_text(full_html, encoding="utf-8")
    url = "file:///" + str(hp).replace("\\", "/")
    subprocess.run(
        [
            BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", f"--window-size={W},{H}", f"--screenshot={pp}", url,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    im = Image.open(pp).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.Resampling.LANCZOS)
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_jpg, format="JPEG", quality=95, subsampling=0, icc_profile=SRGB_BYTES)
    return im


def build_all_10_posters():
    logo_u = data_uri(LOGO_PNG)
    bg = {i: data_uri(V5_IMG_DIR / fn) for i, fn in [
        (1, "p01_studio_rosequartz.png"),
        (2, "p02_handbag_flatlay.png"),
        (3, "p03_herbal_travertine.png"),
        (4, "p04_tearoom_arch_hang.png"),
        (5, "p05_ruby_watersplash.png"),
        (6, "p06_clinical_prism.png"),
        (7, "p07_home_window_hang.png"),
        (8, "p08_satin_medallion.png"),
        (9, "p09_imperial_gold_herbs.png"),
        (10, "p10_ceo_sedan_arrival.png"),
    ]}

    specs = []

    # ==========================================================================
    # DESIGN 01 (LT Plus): CENTERED K-BEAUTY ROSE-QUARTZ PODIUM & RADIAL CALLOUTS
    # ==========================================================================
    p1_img = prod_uri("SP_LT_PLUS_COMBO_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 01 viên đặt LT Plus bục thạch anh dịu êm chuẩn pH.jpg",
        f"""<div class="canvas">
          <img class="bg-cover" src="{bg[1]}"/>
          <div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 22%, rgba(255,248,251,0.94) 0%, rgba(255,240,246,0.52) 48%, rgba(92,12,42,0.22) 100%);"></div>
          <div style="position:absolute;top:52px;left:0;width:1600px;text-align:center;">
            <div class="ht-badge"><img src="{logo_u}"/><div class="b-txt">HẰNG THU PHARMA<span class="b-sub">CHĂM SÓC PHỤ KHOA CHUYÊN SÂU</span></div></div>
            <div style="margin-top:28px;font-family:'ScriptVN';font-size:58px;color:#B81D5B;">Giải pháp êm dịu không lo khô rát</div>
            <h1 style="font-family:'FrauncesBlk';font-size:118px;color:#5E0B2C;line-height:1.02;letter-spacing:-0.02em;text-shadow:0 6px 24px rgba(255,255,255,0.9);">VIÊN ĐẶT LT PLUS</h1>
            <div style="display:inline-block;margin-top:16px;background:linear-gradient(90deg,#9E144B,#D83174);color:#FFF;font-family:'BeVNExtra';font-size:28px;padding:12px 42px;border-radius:999px;letter-spacing:0.06em;box-shadow:0 12px 28px rgba(158,20,75,0.32);">KHÁNG KHUẨN • KHỬ MÙI • GIỮ ẨM CHUẨN PH</div>
          </div>
          <!-- Center Giant Product Hero on Rose-Quartz Podium -->
          <div style="position:absolute;left:430px;top:690px;width:740px;height:860px;display:flex;align-items:center;justify-content:center;">
            <div style="position:absolute;width:640px;height:640px;border-radius:50%;border:3px dashed rgba(196,30,96,0.38);background:radial-gradient(circle,rgba(255,255,255,0.88) 0%,rgba(255,215,232,0.18) 72%);"></div>
            <img src="{p1_img}" style="position:relative;max-width:680px;max-height:760px;filter:drop-shadow(0 32px 44px rgba(82,10,38,0.36));"/>
          </div>
          <!-- 3 Radial Callout Glass Cards -->
          <div style="position:absolute;left:64px;top:760px;width:420px;background:rgba(255,255,255,0.95);border:3px solid #E86B9C;border-radius:30px;padding:24px 28px;box-shadow:0 18px 38px rgba(90,12,42,0.16);">
            <div style="font-family:'BeVNExtra';font-size:24px;color:#C2185B;margin-bottom:6px;">01 • KHÁNG KHUẨN SÂU</div>
            <div style="font-size:28px;color:#330A1B;line-height:1.3;">Hỗ trợ làm sạch dịch bẩn &amp; khử mùi khó chịu từ bên trong</div>
          </div>
          <div style="position:absolute;right:64px;top:830px;width:420px;background:rgba(255,255,255,0.95);border:3px solid #E86B9C;border-radius:30px;padding:24px 28px;box-shadow:0 18px 38px rgba(90,12,42,0.16);">
            <div style="font-family:'BeVNExtra';font-size:24px;color:#C2185B;margin-bottom:6px;">02 • ÊM DỊU CHUẨN PH</div>
            <div style="font-size:28px;color:#330A1B;line-height:1.3;">Duy trì độ ẩm sinh lý tự nhiên, không gây cảm giác khô rát</div>
          </div>
          <div style="position:absolute;left:64px;top:1210px;width:420px;background:rgba(255,255,255,0.95);border:3px solid #E86B9C;border-radius:30px;padding:24px 28px;box-shadow:0 18px 38px rgba(90,12,42,0.16);">
            <div style="font-family:'BeVNExtra';font-size:24px;color:#C2185B;margin-bottom:6px;">03 • NGỪA TÁI VIÊM</div>
            <div style="font-size:28px;color:#330A1B;line-height:1.3;">Bảo vệ vùng nhạy cảm thoáng sạch suốt tuần năng động</div>
          </div>
          <!-- Bottom Pill Footer -->
          <div style="position:absolute;bottom:56px;left:120px;right:120px;height:106px;background:linear-gradient(90deg,#5E0B2C,#A61750);border-radius:999px;display:flex;align-items:center;justify-content:space-between;padding:0 44px;color:#FFF;box-shadow:0 20px 44px rgba(64,6,28,0.38);">
            <div style="font-size:28px;font-family:'BeVNSemi';">Hộp 15 viên chính hãng • Dịu êm cho phái đẹp</div>
            <div style="background:#FFE4EE;color:#7A0D38;font-family:'BeVNExtra';font-size:28px;padding:16px 36px;border-radius:999px;">TƯ VẤN KÍN ĐÁO 1:1 →</div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 02 (Gel Phụ Khang): TOP-DOWN FLAT-LAY "WHAT'S IN HER HANDBAG?"
    # ==========================================================================
    p2_combo = prod_uri("SP_GEL_PHU_KHANG_COMBO_CUTOUT.png")
    p2_sachet = prod_uri("SP_GEL_PHU_KHANG_SACHET_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 02 Gel Phụ Khang bảo bối nhỏ gọn trong túi xách.jpg",
        f"""<div class="canvas">
          <img class="bg-cover" src="{bg[2]}"/>
          <!-- Editorial Diagonal Magazine Card Top-Right -->
          <div style="position:absolute;right:68px;top:64px;width:850px;background:rgba(255,252,254,0.96);border-left:14px solid #B52B6B;border-radius:36px;padding:44px 52px;box-shadow:0 28px 60px rgba(48,12,30,0.18);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
              <span style="background:#FCE6F0;color:#9E1B59;font-family:'BeVNExtra';font-size:23px;padding:8px 22px;border-radius:999px;">WHAT'S IN MY BAG • GÓI 5ML TIỆN LỢI</span>
              <img src="{logo_u}" style="width:58px;height:58px;"/>
            </div>
            <h1 style="font-family:'BeVNExtra';font-size:66px;color:#380B20;line-height:1.14;">Bận mấy cũng nhớ<br/><span style="color:#C2236E;font-family:'PlayfairItal';font-size:74px;">gói nhỏ sạch thơm</span><br/>mang theo bên mình!</h1>
            <p style="margin-top:18px;font-size:29px;color:#5C3246;font-family:'BeVNSemi';line-height:1.4;">Không còn cảnh mang chai lớn cồng kềnh khi đi làm văn phòng hay du lịch xa.</p>
          </div>
          <!-- Flat-lay Products Arranged Naturally on Marble -->
          <img src="{p2_combo}" style="position:absolute;right:85px;top:790px;width:860px;transform:rotate(-4deg);filter:drop-shadow(0 28px 36px rgba(40,15,28,0.30));"/>
          <img src="{p2_sachet}" style="position:absolute;left:90px;top:980px;width:620px;transform:rotate(9deg);filter:drop-shadow(0 22px 30px rgba(40,15,28,0.28));"/>
          <!-- Bottom 3-Column Spec Dock -->
          <div style="position:absolute;left:64px;right:64px;bottom:60px;background:#3A0B21;border-radius:40px;padding:36px 46px;color:#FFF;box-shadow:0 24px 50px rgba(36,6,20,0.36);">
            <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid rgba(255,255,255,0.16);padding-bottom:22px;margin-bottom:24px;">
              <div>
                <div style="font-size:24px;color:#FF9EC7;letter-spacing:0.08em;font-family:'BeVNExtra';">GEL CHĂM SÓC DỊU NHẸ HẰNG THU</div>
                <div style="font-family:'FrauncesBlk';font-size:74px;color:#FFF;line-height:1.05;">GEL PHỤ KHANG</div>
              </div>
              <div style="background:linear-gradient(90deg,#FF6FA8,#D92672);padding:20px 40px;border-radius:999px;font-family:'BeVNExtra';font-size:30px;">HỘP 5 TÚI × 5ML</div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:26px;font-size:27px;line-height:1.32;">
              <div style="background:rgba(255,255,255,0.09);padding:20px 24px;border-radius:22px;"><strong style="color:#FFB3D2;display:block;margin-bottom:4px;">✓ Gọn nhẹ tinh tế</strong>Bỏ vừa ví cầm tay đi làm, công tác</div>
              <div style="background:rgba(255,255,255,0.09);padding:20px 24px;border-radius:22px;"><strong style="color:#FFB3D2;display:block;margin-bottom:4px;">✓ Sạch êm khử mùi</strong>Thoáng sạch suốt 8 tiếng ngồi lâu</div>
              <div style="background:rgba(255,255,255,0.09);padding:20px 24px;border-radius:22px;"><strong style="color:#FFB3D2;display:block;margin-bottom:4px;">✓ Không khô rát</strong>Mềm mịn, thơm mát thảo dược</div>
            </div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 03 (Dạ Dày HT): SWISS 4-CELL BENTO HEALTH INFOGRAPHIC
    # ==========================================================================
    p3_combo = prod_uri("SP_DA_DAY_HT_COMBO_CUTOUT.png")
    p3_pills = prod_uri("SP_DA_DAY_HT_PILLS_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 03 Dạ Dày HT cẩm nang thảo mộc êm thượng vị.jpg",
        f"""<div class="canvas" style="background:#F5F2EA;padding:54px;">
          <!-- Header Masthead -->
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:34px;">
            <div class="ht-badge" style="background:#FFF;"><img src="{logo_u}"/><div class="b-txt" style="color:#1B5E20;">HẰNG THU PHARMA<span class="b-sub">CHUYÊN GIA TIÊU HÓA THẢO MỘC</span></div></div>
            <div style="background:#1B5E20;color:#FFF;font-family:'BeVNExtra';font-size:25px;padding:14px 34px;border-radius:999px;">CẨM NANG CHĂM SÓC DẠ DÀY BẬN RỘN</div>
          </div>
          <!-- Bento Row 1 -->
          <div style="display:grid;grid-template-columns:1.12fr 0.88fr;gap:30px;height:520px;margin-bottom:30px;">
            <div style="background:linear-gradient(135deg,#123F17,#256D2B);border-radius:42px;padding:44px 48px;color:#FFF;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 20px 44px rgba(18,63,23,0.22);">
              <span style="background:rgba(255,213,79,0.22);color:#FFE082;border:2px solid #FFD54F;align-self:flex-start;padding:8px 22px;border-radius:999px;font-family:'BeVNExtra';font-size:23px;">THÓI QUEN DỄ GÂY TRÀO NGƯỢC</span>
              <h1 style="font-family:'BeVNExtra';font-size:62px;line-height:1.14;">Sáng vội <span style="color:#FFD54F;">cà phê đá,</span><br/>trưa ăn trễ giờ<br/>nóng rát thượng vị?</h1>
              <div style="font-size:27px;color:#DCEDC8;font-family:'BeVNSemi';">Ợ hơi, ợ chua, đầy chướng làm mất tập trung &amp; khó ngủ sâu.</div>
            </div>
            <div style="background:#FFFFFF;border:3px solid #C8E6C9;border-radius:42px;padding:40px 42px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 14px 34px rgba(0,0,0,0.06);">
              <div style="font-family:'BeVNExtra';font-size:26px;color:#2E7D32;">🌿 TỨ VỊ THẢO MỘC VIỆT</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;">
                <div style="background:#F1F8E9;border-radius:24px;padding:20px;font-size:27px;color:#1B431E;"><strong>Dạ Cẩm</strong><span style="display:block;font-size:22px;color:#4A6B4D;font-family:'BeVNSemi';">Trung hòa acid, dịu rát</span></div>
                <div style="background:#FFF8E1;border-radius:24px;padding:20px;font-size:27px;color:#5D4037;"><strong>Nghệ Đen</strong><span style="display:block;font-size:22px;color:#795548;font-family:'BeVNSemi';">Hỗ trợ lành niêm mạc</span></div>
                <div style="background:#F1F8E9;border-radius:24px;padding:20px;font-size:27px;color:#1B431E;"><strong>Hoàng Liên</strong><span style="display:block;font-size:22px;color:#4A6B4D;font-family:'BeVNSemi';">Kháng khuẩn êm bụng</span></div>
                <div style="background:#FFF8E1;border-radius:24px;padding:20px;font-size:27px;color:#5D4037;"><strong>Mộc Hương</strong><span style="display:block;font-size:22px;color:#795548;font-family:'BeVNSemi';">Giảm đầy hơi chướng</span></div>
              </div>
            </div>
          </div>
          <!-- Bento Row 2: Giant Pop-out Product Showcase + 3 Mechanism Steps -->
          <div style="position:relative;height:1180px;border-radius:46px;overflow:hidden;box-shadow:0 26px 56px rgba(20,50,24,0.18);">
            <img class="bg-cover" src="{bg[3]}"/>
            <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,253,248,0.18) 0%,rgba(255,253,248,0.95) 48%,rgba(246,252,246,0.98) 100%);"></div>
            <img src="{p3_combo}" style="position:absolute;left:46px;bottom:64px;width:710px;filter:drop-shadow(0 30px 42px rgba(16,48,20,0.34));"/>
            <img src="{p3_pills}" style="position:absolute;left:540px;bottom:48px;width:270px;filter:drop-shadow(0 16px 24px rgba(0,0,0,0.28));"/>
            <div style="position:absolute;right:56px;top:64px;width:710px;">
              <div style="font-family:'ScriptVN';font-size:54px;color:#2E7D32;">Bảo vệ dạ dày êm khỏe mỗi ngày</div>
              <h2 style="font-family:'FrauncesBlk';font-size:108px;color:#123F17;line-height:1.0;">DẠ DÀY HT</h2>
              <div style="margin-top:34px;display:flex;flex-direction:column;gap:22px;">
                <div style="background:#FFF;border-left:10px solid #2E7D32;border-radius:24px;padding:24px 30px;font-size:30px;color:#18361B;box-shadow:0 12px 26px rgba(0,0,0,0.08);"><strong>1. Giảm acid dịch vị</strong> dư thừa gây ợ chua, nóng rát</div>
                <div style="background:#FFF;border-left:10px solid #43A047;border-radius:24px;padding:24px 30px;font-size:30px;color:#18361B;box-shadow:0 12px 26px rgba(0,0,0,0.08);"><strong>2. Bao phủ &amp; bảo vệ</strong> niêm mạc dạ dày – tá tràng</div>
                <div style="background:#FFF;border-left:10px solid #F9A825;border-radius:24px;padding:24px 30px;font-size:30px;color:#18361B;box-shadow:0 12px 26px rgba(0,0,0,0.08);"><strong>3. Giảm triệu chứng</strong> viêm loét &amp; trào ngược dạ dày</div>
              </div>
              <div style="margin-top:38px;display:flex;align-items:center;justify-content:space-between;background:#1B5E20;color:#FFF;padding:22px 36px;border-radius:999px;">
                <span style="font-size:22px;font-family:'BeVNSemi';">TPBVSK • Không phải là thuốc chữa bệnh</span>
                <span style="background:#FFD54F;color:#123F17;font-family:'BeVNExtra';font-size:26px;padding:12px 28px;border-radius:999px;">NHẬN LIỆU TRÌNH →</span>
              </div>
            </div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 04 (Điều Kinh HT): 2-COLUMN ORIENTAL TEA-ROOM ARCH + EDITORIAL SIDEBAR
    # (Chị Hằng inside clean Left Roman Arch — 0% text touching portrait!)
    # ==========================================================================
    p4_prod = prod_uri("SP_DIEU_KINH_HT_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 04 Điều Kinh HT thưởng trà dưỡng khí huyết hồng hào.jpg",
        f"""<div class="canvas" style="background:linear-gradient(135deg,#FBF5F9 0%,#F3E4F0 100%);">
          <!-- Left Clean Roman Arch Portrait Frame (ZERO text on photo!) -->
          <div style="position:absolute;left:58px;top:64px;width:710px;height:1420px;border-radius:360px 360px 44px 44px;overflow:hidden;border:10px solid #FFF;box-shadow:0 28px 60px rgba(90,18,72,0.22);">
            <img src="{bg[4]}" style="width:100%;height:100%;object-fit:cover;object-position:center 22%;"/>
          </div>
          <!-- Bottom-Left Caption Plaque below Arch -->
          <div style="position:absolute;left:58px;bottom:64px;width:710px;background:#4A0D3A;color:#FFF;border-radius:36px;padding:34px 40px;box-shadow:0 20px 42px rgba(74,13,58,0.28);">
            <div style="font-family:'ScriptVN';font-size:46px;color:#F8BBD0;">Tâm sự cùng CEO Nguyễn Thị Hằng</div>
            <div style="font-size:28px;font-family:'BeVNSemi';line-height:1.38;margin-top:6px;">“Phụ nữ sau tuổi 30 muốn da dẻ hồng hào, trước hết khí huyết bên trong phải êm hòa thông suốt.”</div>
          </div>
          <!-- Right Editorial Column + Giant Bottle -->
          <div style="position:absolute;right:58px;top:64px;width:730px;bottom:64px;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
              <div class="ht-badge"><img src="{logo_u}"/><div class="b-txt" style="color:#7B1FA2;">HẰNG THU PHARMA<span class="b-sub">DƯỠNG KHÍ HUYẾT PHÁI ĐẸP</span></div></div>
              <h1 style="margin-top:34px;font-family:'PlayfairBlk';font-size:70px;color:#4A0D3A;line-height:1.12;">Đừng coi nhẹ<br/><span style="color:#AD1457;font-style:italic;">kỳ dâu thất thường</span><br/>&amp; đau bụng âm ỉ!</h1>
              <div style="margin-top:26px;background:#FFF;border-radius:32px;padding:30px 34px;border:2px solid #E1BEE7;box-shadow:0 14px 32px rgba(90,18,72,0.09);">
                <div style="font-size:28px;color:#38092C;margin-bottom:16px;">🌸 <strong>Bổ huyết &amp; hoạt huyết</strong> từ Đương quy, Hương phụ</div>
                <div style="font-size:28px;color:#38092C;margin-bottom:16px;">🌸 <strong>Điều hòa kinh nguyệt</strong> đều đặn tự nhiên mỗi tháng</div>
                <div style="font-size:28px;color:#38092C;">🌸 <strong>Giảm đau bụng kinh,</strong> nuôi sắc diện tươi tắn</div>
              </div>
            </div>
            <!-- Product Pedestal Box -->
            <div style="position:relative;height:860px;background:radial-gradient(circle at 68% 62%,#FFFFFF 0%,#F8E1F2 75%);border-radius:42px;border:3px solid #FFF;box-shadow:0 22px 48px rgba(90,18,72,0.16);padding:34px;display:flex;flex-direction:column;justify-content:space-between;">
              <div style="max-width:440px;">
                <div style="font-family:'BeVNExtra';font-size:23px;color:#9C27B0;letter-spacing:0.06em;">VIÊN UỐNG BỔ HUYẾT THẢO DƯỢC</div>
                <div style="font-family:'FrauncesBlk';font-size:68px;color:#4A0D3A;line-height:1.04;margin-top:4px;">ĐIỀU KINH HT</div>
                <div style="margin-top:18px;font-size:25px;color:#5E2750;font-family:'BeVNSemi';line-height:1.38;">Chiết xuất Đương quy, Hương phụ quý giúp chu kỳ êm dịu nhẹ tênh mỗi tháng.</div>
              </div>
              <img src="{p4_prod}" style="position:absolute;right:28px;bottom:76px;height:520px;filter:drop-shadow(0 28px 36px rgba(74,13,58,0.34));"/>
              <div>
                <div style="width:350px;background:linear-gradient(90deg,#7B1FA2,#C2185B);color:#FFF;padding:20px 24px;border-radius:26px;font-family:'BeVNExtra';font-size:25px;text-align:center;box-shadow:0 14px 28px rgba(123,31,162,0.32);margin-bottom:16px;">TƯ VẤN CƠ ĐỊA →</div>
                <div style="font-size:19px;color:#6A4662;font-family:'BeVNSemi';">TPBVSK • Không phải là thuốc, không thay thế thuốc chữa bệnh</div>
              </div>
            </div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 05 (DDVS Romance VIP): DARK-RUBY FRENCH PERFUME & WATER-CROWN KV
    # ==========================================================================
    p5_prod = prod_uri("SP_ROMANCE_VIP_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 05 DDVS Romance VIP tinh chất hoa hồng mềm mịn.jpg",
        f"""<div class="canvas">
          <img class="bg-cover" src="{bg[5]}"/>
          <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(42,3,16,0.82) 0%,rgba(42,3,16,0.14) 42%,rgba(34,2,13,0.88) 100%);"></div>
          <!-- Top Gold Vogue Header -->
          <div style="position:absolute;top:56px;left:70px;right:70px;display:flex;align-items:center;justify-content:space-between;">
            <div class="ht-badge"><img src="{logo_u}"/><div class="b-txt">HẰNG THU PHARMA<span class="b-sub">LUXURY FEMININE CARE</span></div></div>
            <div style="border:2px solid #FFD98E;color:#FFE7B3;padding:12px 30px;border-radius:999px;font-family:'BeVNExtra';font-size:23px;letter-spacing:0.08em;">CHAI 150ML CAO CẤP</div>
          </div>
          <div style="position:absolute;top:178px;left:80px;right:80px;text-align:center;">
            <div style="font-family:'ScriptVN';font-size:62px;color:#FFB6C8;">Thay vì rửa thật nhiều lần gây khô căng...</div>
            <h1 style="font-family:'PlayfairBlk';font-size:126px;background:linear-gradient(180deg,#FFF8EB 0%,#FFD28C 55%,#E69D45 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.02;filter:drop-shadow(0 10px 28px rgba(0,0,0,0.55));">ROMANCE VIP</h1>
            <div style="margin-top:12px;font-size:32px;color:#FFE4EC;letter-spacing:0.08em;font-family:'BeVNExtra';">TINH CHẤT THẢO DƯỢC DỊU ÊM • DƯỠNG ẨM CHUẨN PH</div>
          </div>
          <!-- Center Spotlight Tall Bottle -->
          <div style="position:absolute;left:0;right:0;top:510px;height:1020px;display:flex;align-items:center;justify-content:center;">
            <div style="position:absolute;width:520px;height:520px;border-radius:50%;background:radial-gradient(circle,rgba(255,190,210,0.55) 0%,rgba(255,190,210,0) 72%);filter:blur(24px);"></div>
            <img src="{p5_prod}" style="position:relative;height:930px;filter:drop-shadow(0 36px 56px rgba(0,0,0,0.72));"/>
          </div>
          <!-- Bottom 3 Velvet-Gold Glass Tiles -->
          <div style="position:absolute;bottom:62px;left:70px;right:70px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;">
            <div style="background:rgba(68,8,28,0.86);border:2px solid rgba(255,215,150,0.55);border-radius:30px;padding:28px 30px;color:#FFF;backdrop-filter:blur(10px);">
              <div style="color:#FFD584;font-family:'BeVNExtra';font-size:26px;margin-bottom:8px;">✦ SẠCH DỊU ÊM</div>
              <div style="font-size:26px;color:#FCE4EC;font-family:'BeVNSemi';line-height:1.34;">Làm sạch nhẹ nhàng từ thảo dược, không gây khô rát</div>
            </div>
            <div style="background:rgba(68,8,28,0.86);border:2px solid rgba(255,215,150,0.55);border-radius:30px;padding:28px 30px;color:#FFF;backdrop-filter:blur(10px);">
              <div style="color:#FFD584;font-family:'BeVNExtra';font-size:26px;margin-bottom:8px;">✦ MỀM MỊN 24H</div>
              <div style="font-size:26px;color:#FCE4EC;font-family:'BeVNSemi';line-height:1.34;">Cấp ẩm tự nhiên từ Hoa hồng, Lô hội &amp; Vitamin E</div>
            </div>
            <div style="background:rgba(68,8,28,0.86);border:2px solid rgba(255,215,150,0.55);border-radius:30px;padding:28px 30px;color:#FFF;backdrop-filter:blur(10px);">
              <div style="color:#FFD584;font-family:'BeVNExtra';font-size:26px;margin-bottom:8px;">✦ NGĂN MÙI HÔI</div>
              <div style="font-size:26px;color:#FCE4EC;font-family:'BeVNSemi';line-height:1.34;">Lưu hương thanh khiết, giữ trọn sự quyến rũ tự tin</div>
            </div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 06 (Legend WhiteSkin): CLINICAL DERMATOLOGY PRISM LAB SPLIT
    # ==========================================================================
    p6_prod = prod_uri("SP_WHITESKIN_COMBO_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 06 Legend WhiteSkin lăng kính dưỡng sáng từ gốc.jpg",
        f"""<div class="canvas">
          <img class="bg-cover" src="{bg[6]}"/>
          <div style="position:absolute;inset:0;background:linear-gradient(155deg,rgba(240,249,255,0.92) 0%,rgba(225,243,254,0.45) 52%,rgba(6,42,78,0.88) 100%);"></div>
          <!-- Top Clinical Bar -->
          <div style="position:absolute;top:58px;left:68px;right:68px;display:flex;align-items:center;justify-content:space-between;">
            <div class="ht-badge"><img src="{logo_u}"/><div class="b-txt" style="color:#01579B;">HẰNG THU PHARMA<span class="b-sub">CELLULAR BRIGHTENING SCIENCE</span></div></div>
            <div style="background:#01579B;color:#FFF;font-family:'BeVNExtra';font-size:24px;padding:12px 32px;border-radius:999px;">HỘP 30 VIÊN NANG CHÍNH HÃNG</div>
          </div>
          <!-- Upper-Left Clinical Headline -->
          <div style="position:absolute;top:190px;left:72px;width:960px;">
            <div style="display:inline-block;background:#E1F5FE;border:2px solid #0288D1;color:#01579B;font-family:'BeVNExtra';font-size:25px;padding:8px 24px;border-radius:12px;margin-bottom:18px;">CHỈ BÔI KEM BÊN NGOÀI THÔI CHƯA ĐỦ</div>
            <h1 style="font-family:'BeVNExtra';font-size:80px;color:#042B4E;line-height:1.08;">Nuôi làn da<br/><span style="color:#0277BD;">sáng mịn trong trẻo</span><br/>từ tầng sâu nội sinh</h1>
          </div>
          <!-- 3 Floating Molecular Orbs Left -->
          <div style="position:absolute;left:72px;top:670px;width:620px;display:flex;flex-direction:column;gap:26px;">
            <div style="display:flex;align-items:center;gap:24px;background:rgba(255,255,255,0.95);border-radius:999px;padding:18px 34px 18px 20px;box-shadow:0 18px 38px rgba(4,43,78,0.14);border:2px solid #B3E5FC;">
              <div style="width:94px;height:94px;border-radius:50%;background:radial-gradient(circle at 32% 30%,#FFF,#4FC3F7,#0277BD);color:#FFF;display:flex;align-items:center;justify-content:center;font-family:'BeVNExtra';font-size:24px;flex-shrink:0;">GLUT</div>
              <div><div style="font-family:'BeVNExtra';font-size:30px;color:#042B4E;">L-Glutathione</div><div style="font-size:25px;color:#456884;font-family:'BeVNSemi';">Dưỡng da trắng hồng, mờ sạm màu</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:24px;background:rgba(255,255,255,0.95);border-radius:999px;padding:18px 34px 18px 20px;box-shadow:0 18px 38px rgba(4,43,78,0.14);border:2px solid #FFE082;">
              <div style="width:94px;height:94px;border-radius:50%;background:radial-gradient(circle at 32% 30%,#FFF,#FFD54F,#F57F17);color:#FFF;display:flex;align-items:center;justify-content:center;font-family:'BeVNExtra';font-size:26px;flex-shrink:0;">NMN</div>
              <div><div style="font-family:'BeVNExtra';font-size:30px;color:#042B4E;">NMN &amp; Peptide-GP</div><div style="font-size:25px;color:#456884;font-family:'BeVNSemi';">Trẻ hóa nền da căng mướt đàn hồi</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:24px;background:rgba(255,255,255,0.95);border-radius:999px;padding:18px 34px 18px 20px;box-shadow:0 18px 38px rgba(4,43,78,0.14);border:2px solid #B3E5FC;">
              <div style="width:94px;height:94px;border-radius:50%;background:radial-gradient(circle at 32% 30%,#FFF,#81D4FA,#01579B);color:#FFF;display:flex;align-items:center;justify-content:center;font-family:'BeVNExtra';font-size:26px;flex-shrink:0;">VIT-E</div>
              <div><div style="font-family:'BeVNExtra';font-size:30px;color:#042B4E;">Vitamin E Tự Nhiên</div><div style="font-size:25px;color:#456884;font-family:'BeVNSemi';">Chống oxy hóa trước tia UV nắng gắt</div></div>
            </div>
          </div>
          <!-- Giant Hero Product Right -->
          <img src="{p6_prod}" style="position:absolute;right:56px;top:630px;width:800px;filter:drop-shadow(0 36px 52px rgba(3,28,54,0.46));"/>
          <!-- Bottom Navy Glass Bar -->
          <div style="position:absolute;bottom:60px;left:72px;right:72px;background:rgba(4,34,64,0.92);border:2px solid rgba(129,212,250,0.5);border-radius:36px;padding:30px 44px;display:flex;align-items:center;justify-content:space-between;color:#FFF;">
            <div>
              <div style="font-size:22px;color:#81D4FA;font-family:'BeVNExtra';letter-spacing:0.08em;">VIÊN UỐNG BỔ SUNG DƯỠNG SÁNG</div>
              <div style="font-family:'FrauncesBlk';font-size:66px;line-height:1.05;">LEGEND WHITESKIN</div>
            </div>
            <div style="background:linear-gradient(90deg,#29B6F6,#0288D1);padding:22px 42px;border-radius:999px;font-family:'BeVNExtra';font-size:28px;">TỰ TIN CAM THƯỜNG →</div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 07 (Viên Đặt Phụ Khoa Hằng Thu): SAGE JOURNAL POLAROID + CHECKLIST
    # (Chị Hằng inside clean Top-Right Polaroid — 0% text on photo!)
    # ==========================================================================
    p7_prod = prod_uri("SP_VIEN_DAT_HOP_XANH_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 07 Viên Đặt Phụ Khoa Hằng Thu thấu hiểu mẹ sau sinh.jpg",
        f"""<div class="canvas" style="background:linear-gradient(160deg,#EEF6F0 0%,#DCECE1 55%,#C7E2D0 100%);">
          <!-- Left Header -->
          <div style="position:absolute;left:68px;top:62px;width:820px;">
            <div class="ht-badge"><img src="{logo_u}"/><div class="b-txt" style="color:#1B5E3A;">HẰNG THU PHARMA<span class="b-sub">THẤU HIỂU PHỤ NỮ SAU SINH</span></div></div>
            <div style="margin-top:34px;font-family:'ScriptVN';font-size:58px;color:#2E7D52;">Đừng âm thầm chịu đựng một mình...</div>
            <h1 style="font-family:'BeVNExtra';font-size:74px;color:#0F3822;line-height:1.12;margin-top:6px;">Thiên chức làm mẹ<br/>xứng đáng được<br/><span style="color:#1E7E48;">yêu chiều trọn vẹn</span></h1>
          </div>
          <!-- Top-Right Tilted Polaroid Photo Frame (ZERO text over Chị Hằng!) -->
          <div style="position:absolute;right:68px;top:66px;width:580px;background:#FFF;padding:22px 22px 68px 22px;border-radius:18px;transform:rotate(3.2deg);box-shadow:0 26px 54px rgba(15,56,34,0.20);">
            <img src="{bg[7]}" style="width:100%;height:610px;object-fit:cover;object-position:center 18%;border-radius:10px;"/>
            <div style="position:absolute;bottom:18px;left:0;right:0;text-align:center;font-family:'ScriptVN';font-size:36px;color:#2E5E42;">Phút bình yên của người phụ nữ</div>
          </div>
          <!-- Middle Checklist Paper Card -->
          <div style="position:absolute;left:68px;top:660px;width:880px;background:#FFFFFF;border-radius:38px;padding:42px 46px;box-shadow:0 22px 48px rgba(15,56,34,0.12);border-top:12px solid #1E7E48;">
            <div style="font-family:'BeVNExtra';font-size:28px;color:#1E7E48;margin-bottom:22px;letter-spacing:0.04em;">3 LÝ DO MẸ SAU SINH TIN CHỌN HỘP XANH HẰNG THU:</div>
            <div style="display:flex;align-items:center;gap:20px;font-size:31px;color:#143321;margin-bottom:20px;"><span style="width:46px;height:46px;border-radius:12px;background:#E8F5E9;color:#1E7E48;display:inline-flex;align-items:center;justify-content:center;font-family:'BeVNExtra';flex-shrink:0;">✓</span><span>Làm sạch thoáng &amp; hỗ trợ <strong>săn khít tự nhiên</strong></span></div>
            <div style="display:flex;align-items:center;gap:20px;font-size:31px;color:#143321;margin-bottom:20px;"><span style="width:46px;height:46px;border-radius:12px;background:#E8F5E9;color:#1E7E48;display:inline-flex;align-items:center;justify-content:center;font-family:'BeVNExtra';flex-shrink:0;">✓</span><span>Duy trì <strong>độ ẩm &amp; độ pH</strong> sinh lý thật êm dịu</span></div>
            <div style="display:flex;align-items:center;gap:20px;font-size:31px;color:#143321;"><span style="width:46px;height:46px;border-radius:12px;background:#E8F5E9;color:#1E7E48;display:inline-flex;align-items:center;justify-content:center;font-family:'BeVNExtra';flex-shrink:0;">✓</span><span>Ngăn ngừa <strong>viêm nhiễm, nấm ngứa &amp; khí hư có mùi</strong></span></div>
          </div>
          <!-- Bottom Emerald Showcase Stage + Giant Wide Green Box -->
          <div style="position:absolute;left:68px;right:68px;bottom:58px;height:690px;background:linear-gradient(135deg,#0D3B23,#1E6B43);border-radius:46px;padding:46px 54px;color:#FFF;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 28px 60px rgba(12,50,30,0.32);">
            <div>
              <div style="color:#A5D6A7;font-size:25px;font-family:'BeVNExtra';letter-spacing:0.08em;">THẢO MỘC TRUYỀN THỐNG CHÍNH HÃNG</div>
              <div style="font-family:'FrauncesBlk';font-size:74px;line-height:1.06;margin-top:6px;">VIÊN ĐẶT PHỤ KHOA<br/>HẰNG THU</div>
            </div>
            <div style="align-self:flex-start;background:#FFD54F;color:#0D3B23;font-family:'BeVNExtra';font-size:29px;padding:20px 42px;border-radius:999px;">TƯ VẤN RIÊNG KÍN ĐÁO →</div>
          </div>
          <img src="{p7_prod}" style="position:absolute;right:78px;bottom:84px;width:850px;filter:drop-shadow(0 32px 44px rgba(0,0,0,0.48));"/>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 08 (Romance Love): HAUTE-COUTURE GOLDEN MEDALLION & SILK RIBBON KV
    # ==========================================================================
    p8_prod = prod_uri("SP_ROMANCE_LOVE_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 08 Romance Love món quà giữ lửa yêu thương.jpg",
        f"""<div class="canvas">
          <img class="bg-cover" src="{bg[8]}"/>
          <div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(255,245,250,0.20) 0%,rgba(74,6,36,0.68) 100%);"></div>
          <!-- Ornate Gold Frame Border -->
          <div style="position:absolute;inset:44px;border:3px solid rgba(255,224,178,0.65);border-radius:42px;pointer-events:none;"></div>
          <div style="position:absolute;top:82px;left:0;width:1600px;text-align:center;">
            <div class="ht-badge"><img src="{logo_u}"/><div class="b-txt" style="color:#AD1457;">HẰNG THU PHARMA<span class="b-sub">BÍ QUYẾT HẠNH PHÚC LỨA ĐÔI</span></div></div>
            <div style="margin-top:26px;font-family:'ScriptVN';font-size:64px;color:#FFE0EB;text-shadow:0 4px 16px rgba(60,4,28,0.5);">Đừng để khô hạn làm vơi cảm xúc yêu thương</div>
            <h1 style="font-family:'PlayfairBlk';font-size:116px;color:#FFF;line-height:1.04;text-shadow:0 10px 32px rgba(58,4,28,0.6);">ROMANCE LOVE</h1>
          </div>
          <!-- Center Golden Wreath Medallion + Giant Magenta Box -->
          <div style="position:absolute;left:360px;top:520px;width:880px;height:880px;border-radius:50%;background:radial-gradient(circle,#FFFFFF 0%,#FFE8F2 68%,rgba(255,190,218,0.2) 100%);border:6px solid #FFD996;box-shadow:0 32px 70px rgba(48,4,24,0.45);display:flex;align-items:center;justify-content:center;">
            <img src="{p8_prod}" style="width:760px;transform:rotate(-5deg);filter:drop-shadow(0 30px 40px rgba(88,8,44,0.38));"/>
          </div>
          <!-- Bottom 3 Horizontal Luxury Pills -->
          <div style="position:absolute;bottom:84px;left:100px;right:100px;display:flex;flex-direction:column;gap:18px;">
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;">
              <div style="background:rgba(255,255,255,0.96);border-radius:26px;padding:24px 26px;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,0.22);">
                <div style="font-family:'BeVNExtra';font-size:27px;color:#C2185B;margin-bottom:6px;">💎 CẤP ẨM SÂU</div>
                <div style="font-size:25px;color:#3D0A20;font-family:'BeVNSemi';">Xoa dịu khô rát, mềm mịn tự nhiên</div>
              </div>
              <div style="background:rgba(255,255,255,0.96);border-radius:26px;padding:24px 26px;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,0.22);">
                <div style="font-family:'BeVNExtra';font-size:27px;color:#C2185B;margin-bottom:6px;">💎 TƯƠI SÁNG</div>
                <div style="font-size:25px;color:#3D0A20;font-family:'BeVNSemi';">Nuôi dưỡng nét xuân hồng hào</div>
              </div>
              <div style="background:rgba(255,255,255,0.96);border-radius:26px;padding:24px 26px;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,0.22);">
                <div style="font-family:'BeVNExtra';font-size:27px;color:#C2185B;margin-bottom:6px;">💎 TRỌN LỬA YÊU</div>
                <div style="font-size:25px;color:#3D0A20;font-family:'BeVNSemi';">Hộp 5 viên dưỡng tinh tế kín đáo</div>
              </div>
            </div>
            <div style="background:linear-gradient(90deg,#880E4F,#D81B60);color:#FFF;border:2px solid #FFD996;border-radius:999px;padding:20px 44px;display:flex;justify-content:space-between;align-items:center;font-size:28px;font-family:'BeVNExtra';">
              <span>VIÊN DƯỠNG TRẺ HÓA ROMANCE LOVE CHÍNH HÃNG</span>
              <span style="color:#FFE082;">TRÒ CHUYỆN KÍN ĐÁO 1:1 →</span>
            </div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 09 (Ngọc Long Hoàn): IMPERIAL OBSIDIAN-GOLD ORIENTAL HERBAL POSTER
    # ==========================================================================
    p9_prod = prod_uri("SP_NGOC_LONG_HOAN_CUTOUT.png")
    specs.append((
        "261125 HTPM thiết kế 09 Ngọc Long Hoàn vương dược bồi bổ nguyên khí phái mạnh.jpg",
        f"""<div class="canvas">
          <img class="bg-cover" src="{bg[9]}"/>
          <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(24,10,4,0.88) 0%,rgba(28,12,5,0.22) 48%,rgba(18,7,2,0.92) 100%);"></div>
          <div style="position:absolute;inset:40px;border:3px solid rgba(238,190,104,0.58);border-radius:28px;pointer-events:none;"></div>
          <!-- Royal Header -->
          <div style="position:absolute;top:76px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center;">
            <div class="ht-badge" style="background:rgba(38,16,8,0.92);border:2px solid #E5B660;"><img src="{logo_u}"/><div class="b-txt" style="color:#FFD984;">HẰNG THU PHARMA<span class="b-sub" style="color:#E0C392;">MÓN QUÀ SỨC KHỎE PHÁI MẠNH</span></div></div>
            <div style="background:linear-gradient(90deg,#8C5A16,#D49E3F);color:#1E0D04;font-family:'BeVNExtra';font-size:24px;padding:12px 32px;border-radius:999px;">LỌ 40 VIÊN CHÍNH HÃNG</div>
          </div>
          <div style="position:absolute;top:196px;left:80px;right:80px;text-align:center;">
            <div style="font-size:30px;color:#F5CFA0;letter-spacing:0.12em;font-family:'BeVNExtra';">BỒI BỔ TỪ GỐC • VỮNG VÀNG BẢN LĨNH TUỔI 35+</div>
            <h1 style="margin-top:10px;font-family:'FrauncesBlk';font-size:122px;background:linear-gradient(180deg,#FFF6D6 0%,#F5C469 52%,#B87B1E 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.04;filter:drop-shadow(0 12px 28px rgba(0,0,0,0.8));">NGỌC LONG HOÀN</h1>
            <div style="margin-top:8px;font-size:31px;color:#FFE8C2;font-family:'PlayfairItal';">“Đằng sau người đàn ông bền bỉ là sự chăm sóc tinh tế của người vợ”</div>
          </div>
          <!-- Center Giant Jar on Obsidian Pedestal -->
          <div style="position:absolute;left:0;right:0;top:520px;height:940px;display:flex;align-items:center;justify-content:center;">
            <div style="position:absolute;width:580px;height:580px;border-radius:50%;background:radial-gradient(circle,rgba(255,185,70,0.42) 0%,rgba(255,185,70,0) 70%);filter:blur(22px);"></div>
            <img src="{p9_prod}" style="position:relative;height:840px;filter:drop-shadow(0 38px 54px rgba(0,0,0,0.82));"/>
          </div>
          <!-- Bottom Gold-Framed Plaques -->
          <div style="position:absolute;bottom:74px;left:76px;right:76px;">
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;margin-bottom:20px;">
              <div style="background:linear-gradient(180deg,rgba(54,24,10,0.92),rgba(30,12,4,0.96));border:2px solid #D4A14A;border-radius:24px;padding:24px 26px;color:#FFF;">
                <div style="color:#FFD57E;font-family:'BeVNExtra';font-size:26px;margin-bottom:6px;">01 • BỔ THẬN KHÍ</div>
                <div style="font-size:25px;color:#F3DEC0;font-family:'BeVNSemi';">Bồi bổ nguyên khí &amp; sinh lực bền vững từ gốc</div>
              </div>
              <div style="background:linear-gradient(180deg,rgba(54,24,10,0.92),rgba(30,12,4,0.96));border:2px solid #D4A14A;border-radius:24px;padding:24px 26px;color:#FFF;">
                <div style="color:#FFD57E;font-family:'BeVNExtra';font-size:26px;margin-bottom:6px;">02 • GIẢM ĐAU MỎI</div>
                <div style="font-size:25px;color:#F3DEC0;font-family:'BeVNSemi';">Hỗ trợ giảm đau lưng, mỏi gối, uể oải cuối ngày</div>
              </div>
              <div style="background:linear-gradient(180deg,rgba(54,24,10,0.92),rgba(30,12,4,0.96));border:2px solid #D4A14A;border-radius:24px;padding:24px 26px;color:#FFF;">
                <div style="color:#FFD57E;font-family:'BeVNExtra';font-size:26px;margin-bottom:6px;">03 • GIỮ PHONG ĐỘ</div>
                <div style="font-size:25px;color:#F3DEC0;font-family:'BeVNSemi';">Dẻo dai thể lực • Tư vấn hoàn toàn bảo mật</div>
              </div>
            </div>
            <div style="text-align:center;color:#CBB292;font-size:21px;font-family:'BeVNSemi';">Thực phẩm bảo vệ sức khỏe • Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh</div>
          </div>
        </div>"""
    ))

    # ==========================================================================
    # DESIGN 10 (CEO Nguyễn Thị Hằng & Hệ Sinh Thái HTPM): FORBES EXECUTIVE COVER
    # + 8-SKU GOLDEN SHOWCASE DOCK (0% text over Chị Hằng's face!)
    # ==========================================================================
    p10_shelf = prod_uri("SP_HTPM_FULL_8SKU_SHELF.png", max_dim=1500)
    specs.append((
        "261125 HTPM thiết kế 10 CEO Nguyễn Thị Hằng hệ sinh thái giá trị thật.jpg",
        f"""<div class="canvas" style="background:#071E36;">
          <!-- Upper Executive Photo Frame (shifted below masthead so hair crown has 100% breathing room!) -->
          <div style="position:absolute;top:110px;left:0;right:0;height:1180px;overflow:hidden;">
            <img src="{bg[10]}" style="width:100%;height:100%;object-fit:cover;object-position:center 12%;"/>
            <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,30,54,0.35) 0%,rgba(5,24,46,0.0) 18%,rgba(5,24,46,0.0) 72%,rgba(7,30,54,1.0) 100%);"></div>
          </div>
          <!-- Top Magazine Masthead Bar (clean navy header bar Y=0..118px above photo!) -->
          <div style="position:absolute;top:24px;left:56px;right:56px;display:flex;justify-content:space-between;align-items:center;">
            <div class="ht-badge"><img src="{logo_u}"/><div class="b-txt" style="color:#072A4A;">HẰNG THU PHARMA<span class="b-sub">HƠN MỘT THẬP KỶ TÂM HUYẾT</span></div></div>
            <div style="background:rgba(7,34,62,0.95);border:2px solid #F5C76B;color:#FFE29E;padding:12px 30px;border-radius:999px;font-family:'BeVNExtra';font-size:23px;">CEO NGUYỄN THỊ HẰNG</div>
          </div>
          <!-- Lower Editorial Quote + Golden 8-SKU Ecosystem Showcase Dock (Y=1110..1948px) -->
          <div style="position:absolute;left:56px;right:56px;bottom:52px;background:linear-gradient(180deg,rgba(9,39,70,0.96) 0%,#05192E 100%);border:3px solid rgba(245,199,107,0.62);border-radius:44px;padding:42px 50px 38px 50px;color:#FFF;box-shadow:0 30px 70px rgba(0,0,0,0.55);">
            <div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:26px;">
              <div>
                <div style="color:#FFD67E;font-family:'BeVNExtra';font-size:25px;letter-spacing:0.08em;">TẦM NHÌN KINH DOANH BỀN VỮNG</div>
                <h1 style="font-family:'BeVNExtra';font-size:58px;line-height:1.14;margin-top:6px;">Đi đường dài chỉ có thể bằng<br/><span style="color:#FFE082;">sản phẩm thật &amp; sự tử tế!</span></h1>
              </div>
              <div style="background:linear-gradient(90deg,#F5C469,#D4942A);color:#061B30;font-family:'BeVNExtra';font-size:27px;padding:20px 38px;border-radius:999px;flex-shrink:0;">ĐỒNG HÀNH KHỞI NGHIỆP →</div>
            </div>
            <!-- Golden Shelf Holding All 8 Real HTPM Products -->
            <div style="background:radial-gradient(ellipse at 50% 65%,#FFFFFF 0%,#E3F2FD 65%,#B3E5FC 100%);border-radius:32px;padding:22px 28px 14px 28px;border:2px solid #FFE082;text-align:center;">
              <img src="{p10_shelf}" style="width:100%;max-height:360px;object-fit:contain;filter:drop-shadow(0 18px 24px rgba(5,25,46,0.28));"/>
              <div style="margin-top:8px;font-family:'BeVNExtra';font-size:23px;color:#072A4A;letter-spacing:0.05em;">HỆ SINH THÁI CHĂM SÓC SỨC KHỎE &amp; SẮC ĐẸP CHÍNH HÃNG HẰNG THU PHARMA</div>
            </div>
          </div>
        </div>"""
    ))

    # Clean old Nha Trang clone .jpg and any .psd in K6 & Local Day-25 folders!
    for folder in (K6_DAY25_DIR, LOCAL_DAY25_DIR):
        if folder.exists():
            for old_f in list(folder.iterdir()):
                if old_f.suffix.lower() == ".psd":
                    old_f.unlink()
                    print(f"[REMOVED PSD] {old_f.name}")
                elif old_f.suffix.lower() == ".jpg" and "thiết kế" in old_f.name.lower():
                    old_f.unlink()
                    print(f"[REMOVED OLD CLONE JPG] {old_f.name}")

    rendered_imgs = []
    for idx, (jpg_fn, body_html) in enumerate(specs, start=1):
        out_p = OUT_DIR / jpg_fn
        im = render_poster_html(f"v5_poster_{idx:02d}", body_html, out_p)
        rendered_imgs.append((f"#{idx:02d}", jpg_fn, im))
        for dst_dir in (K6_DAY25_DIR, LOCAL_DAY25_DIR):
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(out_p, dst_dir / jpg_fn)
        print(f"[POSTER #{idx:02d} DELIVERED] {jpg_fn}")

    # Build 5x2 Overview Contact Sheet
    tw, th = 360, 450
    sheet = Image.new("RGB", (tw * 5, th * 2), (16, 22, 34))
    for i, (tag, fn, im) in enumerate(rendered_imgs):
        r, c = divmod(i, 5)
        thumb = im.resize((tw - 12, th - 12), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (c * tw + 6, r * th + 6))

    sheet_k6 = K6_DAY25_DIR / "00 - Bảng Xem Nhanh 10 Thiết Kế Ngày 25.11.jpg"
    sheet.save(sheet_k6, format="JPEG", quality=93, icc_profile=SRGB_BYTES)
    shutil.copy2(sheet_k6, OUT_DIR / sheet_k6.name)
    shutil.copy2(sheet_k6, ARTIFACT_DIR / "htpm_261125_10_unique_designs_v5.jpg")
    print("=== ALL 10 COMPLETELY UNIQUE POSTERS (0 PSD) DELIVERED TO K6 ===")


if __name__ == "__main__":
    build_all_10_posters()
