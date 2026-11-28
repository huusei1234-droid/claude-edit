import concurrent.futures, json, math, os, re, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"d:\AI\full studio\output\htpm5-261121")
import render_htpm5_master as h5
import mix_htpm5_final as m5

BATCH_DIR   = r"d:\AI\full studio\output\htpm-batch-261123"
KB06_DIR    = os.path.join(BATCH_DIR, "kb06")
SRC_DIR     = os.path.join(KB06_DIR, "capcut_src")
MEDIA_DIR   = os.path.join(KB06_DIR, "media")
HF_DIR      = os.path.join(KB06_DIR, "hf_kobe_dense")
CHECK_DIR   = os.path.join(KB06_DIR, "check_dense")
os.makedirs(CHECK_DIR, exist_ok=True)

SRC_MP4     = os.path.join(SRC_DIR, "HTPM_capcut_export.mp4")
MATTE_MP4   = os.path.join(SRC_DIR, "capcut_matte.mp4")
WORDS_JSON  = os.path.join(SRC_DIR, "capcut_words.json")
KOBE_MOV    = os.path.join(SRC_DIR, "kobe_dense_50s.mov")

FONTS_SRC   = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
FONT_SUB    = os.path.join(FONTS_SRC, "AsapCondensed-Black.ttf")
if not os.path.exists(FONT_SUB):
    FONT_SUB = os.path.join(FONTS_SRC, "AsapCondensed-Bold.ttf")

RISER_01_LOCAL = os.path.join(BATCH_DIR, "riser_01_local.mp3")
TOKYO_BGM      = r"D:\AI\full studio\phong-cach\talking-head\assets_dung_chung\bgm\tokyo_drift_remix.mp3"

# Today is 2026-11-24, keeping HTPM Vietnamese naming standard
FINAL_FN    = "261124 HTPM sai lầm lấy chồng rồi để bản thân lại sau final.mp4"
FINAL_FN_23 = "261123 HTPM sai lầm lấy chồng rồi để bản thân lại sau final.mp4"
BRAND_OUT   = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma"
D_OUT       = r"D:\XUẤT CAPCUT\hằng thu pharma"
MASTER_OUT  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final"
DRIVE_PROJ  = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\htpm-kb06-261123-co-chong-roi"
ART_DIR     = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8"

W, H, FPS, SR = 1080, 1920, 30.0, 48000

# Exact timeline locked to HTPM_capcut_export.mp4 (50.533s = 1516 frames)
HOOK_Q_END  = 2.95
RISER_T     = 10.62
FULL_STAGES = [
    (16.58, 25.46),  # Scene 2B: Full Kobe Motion Stage #1 (After marriage 2x2 dense Bento)
    (32.50, 40.38),  # Scene 4:  Full Kobe Motion Stage #2 (Healthy & confident wife 2-row power Bento)
]

# B-Roll placements:
# - Lower left frame: X=[54..486] (w=432, cx=270), Y=[964..1416] (h=452, cy=1190) -> 100% fills left half of Bento!
# - Full upper cinema frame: X=[54..1024] (w=970, cx=539), Y=[254..718] (h=464, cy=486) -> < Y=860, 970px full safe width!
BROLL_SLOTS = [
    (10.68, 16.52, "s1_before_wed",     "lower", 270.0, 1190.0, 432, 452, (219, 39, 119)),
    (16.58, 25.46, "s2_busy_chores",    "full",  539.0,  486.0, 970, 464, (225, 29,  72)),
    (25.52, 30.10, "s3_mirror_realize", "lower", 270.0, 1190.0, 432, 452, ( 37, 99, 235)),
    (32.50, 40.38, "s4_selflove_glow",  "full",  539.0,  486.0, 970, 464, (  5,150, 105)),
]

# Calibrated face crop on HTPM_capcut_export.mp4 unzoomed frames (t>=9.0s: crown_y=474, chin_y=895, shoulders=1120)
PIP_BOX = [448, 1128, 196, 876]
PIP_CX, PIP_CY, PIP_DIAM = 468.0, 1368.0, 340  # Bottom edge = 1368 + 170 + 5 = 1543px <= 1545px Safe Zone!


def author_and_render_hyperframes(dur_s: float):
    f_dir = os.path.join(HF_DIR, "assets", "fonts")
    os.makedirs(f_dir, exist_ok=True)
    for fn in os.listdir(FONTS_SRC):
        if fn.endswith(".ttf") and any(k in fn for k in ("AsapCondensed", "BeVietnamPro", "Montserrat")):
            shutil.copy2(os.path.join(FONTS_SRC, fn), os.path.join(f_dir, fn))

    html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>KB06 — HTPM Kobe Dense Large-Text Stage</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Asap Condensed"; src: url("assets/fonts/AsapCondensed-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
      @font-face {{ font-family: "Asap Condensed"; src: url("assets/fonts/AsapCondensed-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
      @font-face {{ font-family: "Asap Condensed"; src: url("assets/fonts/AsapCondensed-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
      @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
      @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
      @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: transparent; font-family: "Montserrat", sans-serif; letter-spacing: -0.4px; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: transparent; }}
      .clip {{ position: absolute; inset: 0; pointer-events: none; }}

      /* TOP CROWN-HUGGING ZONE: 100% inside Y>=250 Safe Zone & strictly above hair crown! */
      .crown-zone-zoom {{
        position: absolute; left: 54px; width: 970px; top: 250px; height: 118px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
      }}
      .crown-zone-norm {{
        position: absolute; left: 54px; width: 970px; top: 252px; height: 208px;
        display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 6px;
      }}
      .svg-headline {{
        width: 970px; height: 116px; overflow: visible;
        filter: drop-shadow(0 10px 22px rgba(10, 16, 36, 0.52));
      }}
      .svg-headline text {{
        font-family: "Asap Condensed", sans-serif; font-weight: 900;
        paint-order: stroke fill; stroke: #0f172a; stroke-width: 12px;
        stroke-linejoin: round; stroke-linecap: round; letter-spacing: 0.5px;
      }}

      /* GIANT KOBE PILL STICKER (Wide Montserrat Black: 36px - 44px!) */
      .kobe-pill {{
        display: inline-flex; align-items: center; gap: 10px;
        padding: 13px 30px; border-radius: 999px; background: #ffffff;
        border: 4px solid #ffffff;
        box-shadow: 0 16px 34px rgba(12, 20, 56, 0.28), 0 4px 10px rgba(15, 23, 42, 0.14);
        transform: rotate(-1.5deg); font-weight: 900; font-size: 38px;
        line-height: 1.08; color: #0f172a; white-space: nowrap;
      }}
      .kobe-pill.sub {{ font-size: 34px; padding: 10px 26px; }}
      .kobe-pill.z-badge {{
        position: absolute; z-index: 20; font-size: 38px; padding: 13px 30px;
        box-shadow: 0 18px 38px rgba(12, 20, 56, 0.34), 0 0 0 4px rgba(37, 99, 235, 0.18);
      }}
      .c-cobalt {{ color: #2563eb; }}
      .c-rose   {{ color: #e11d48; }}
      .c-emerald{{ color: #059669; }}
      .c-gold   {{ color: #ffd154; }}

      /* DENSE LOWER BENTO CONTAINER: Strictly X=[54..882] (828px wide) for TikTok Right-Button Safe Zone! */
      .bento-lower-box {{
        position: absolute; left: 54px; top: 964px; width: 828px; height: 452px;
        border-radius: 34px; padding: 14px;
        background: radial-gradient(circle at 18% 18%, #dbe4ff 0%, #f5f7ff 60%, #e6eeff 100%);
        border: 5px solid #ffffff;
        box-shadow: 0 22px 46px rgba(10, 18, 48, 0.36);
        display: flex; flex-direction: column; gap: 14px; overflow: hidden;
      }}
      .bento-lower-box::before, .kobe-full-stage::before {{
        content: ""; position: absolute; inset: 0;
        background-image: radial-gradient(#b8c5eb 2.6px, transparent 2.6px);
        background-size: 28px 28px; opacity: 0.85; pointer-events: none;
      }}

      /* RIGHT HALF OF ASYMMETRIC BENTO SPLIT (X=[498..882] = 384px wide, Y=[964..1416] = 452px tall) */
      .bento-right-stack {{
        position: absolute; left: 498px; top: 964px; width: 384px; height: 452px;
        display: flex; flex-direction: column; gap: 13px; justify-content: space-between;
      }}
      .mini-bento-card {{
        position: relative; flex: 1; border-radius: 26px; padding: 12px 18px;
        display: flex; align-items: center; gap: 16px;
        box-shadow: 0 16px 32px rgba(12, 20, 52, 0.24);
        border: 4px solid #ffffff; overflow: hidden;
      }}
      .icon-badge-lg {{
        width: 84px; height: 84px; border-radius: 22px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center; font-size: 48px;
        box-shadow: inset 0 2px 6px rgba(255,255,255,0.55);
      }}

      /* FULL 9:16 KOBE MOTION STAGE */
      .kobe-full-stage {{
        position: absolute; inset: 0;
        background: radial-gradient(circle at 22% 16%, #cbd7fc 0%, #f2f5fe 52%, #d9e3fc 100%);
        overflow: hidden;
      }}
      .highway-track {{
        position: absolute; left: -20px; right: -20px; height: 28px;
        background: #b8c5f8; display: flex; align-items: center; overflow: hidden;
        box-shadow: inset 0 2px 6px rgba(37, 99, 235, 0.16);
      }}
      .highway-dashes {{
        width: 1560px; height: 5px;
        background: repeating-linear-gradient(90deg, #ffffff 0 22px, transparent 22px 42px);
      }}

      /* 2x2 DENSE BENTO GRID ON FULL STAGE: X=[54..882] (828px wide), Y=[734..1166] (432px tall) */
      .bento-grid-2x2 {{
        position: absolute; left: 54px; top: 734px; width: 828px; height: 432px;
        display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 14px;
      }}
      .bento-cell {{
        position: relative; border-radius: 28px; padding: 16px 18px;
        display: flex; align-items: center; gap: 16px;
        border: 4px solid #ffffff;
        box-shadow: 0 16px 34px rgba(24, 38, 102, 0.16); overflow: hidden;
      }}
      .cell-num {{
        position: absolute; right: 14px; top: 10px; width: 44px; height: 44px;
        border-radius: 50%; color: #ffffff; font-weight: 900; font-size: 28px;
        display: flex; align-items: center; justify-content: center;
      }}
      .pip-side-pill {{
        position: absolute; height: 78px; border-radius: 22px; padding: 0 14px;
        background: #ffffff; border: 4px solid #ffffff;
        box-shadow: 0 14px 28px rgba(24, 38, 102, 0.18);
        display: flex; align-items: center; justify-content: center; gap: 6px;
        font-weight: 900; font-size: 27px; color: #0f172a; white-space: nowrap;
      }}
      .sheen-bar {{
        position: absolute; top: -40%; left: -35%; width: 28%; height: 180%;
        background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.52) 50%, rgba(255,255,255,0) 100%);
        transform: rotate(22deg); pointer-events: none; z-index: 9;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur_s:.2f}" data-width="1080" data-height="1920" data-fps="30">
      <svg width="0" height="0" style="position:absolute;">
        <defs>
          <linearGradient id="grad-gold" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" /><stop offset="28%" stop-color="#fff4bf" />
            <stop offset="62%" stop-color="#ffd154" /><stop offset="100%" stop-color="#e68a00" />
          </linearGradient>
          <linearGradient id="grad-rose" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" /><stop offset="30%" stop-color="#ffe2ef" />
            <stop offset="65%" stop-color="#ff6fae" /><stop offset="100%" stop-color="#d81b68" />
          </linearGradient>
          <linearGradient id="grad-emerald" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" /><stop offset="32%" stop-color="#d6ffef" />
            <stop offset="68%" stop-color="#38d996" /><stop offset="100%" stop-color="#08875b" />
          </linearGradient>
        </defs>
      </svg>

      <!-- 1. HOOK (0.06 - 10.56s -> Riser at 10.62s!): Hair crown is at Y=376..392px so top zone stays strictly in Y=250..368px! -->
      <div id="c1" class="clip" data-start="0.06" data-duration="10.52" data-track-index="1" data-layout-allow-overlap data-layout-allow-safe-zone>
        <div id="hk-top1" class="crown-zone-zoom float-gentle">
          <svg class="svg-headline" viewBox="0 0 970 116">
            <text x="485" y="90" text-anchor="middle" font-size="76" fill="url(#grad-gold)">CÓ CHỒNG CÀNG CHĂM MÌNH!</text>
          </svg>
        </div>
        <div id="hk-top2" class="crown-zone-zoom float-gentle" style="opacity:0;">
          <div class="kobe-pill" style="border-color:#fda4af;"><span class="c-rose">⚠ SAI LẦM</span><span>SAU KHI CƯỚI</span></div>
        </div>

        <!-- 0.12 - 2.92s: Big Bold Chest Double-Pill (Wide Montserrat Black!) -->
        <div id="hk-chest" class="float-card" style="position:absolute;left:54px;top:1164px;width:828px;border-radius:34px;background:#ffffff;padding:22px 24px;border:5px solid #ffffff;box-shadow:0 22px 46px rgba(12,20,56,0.34);transform:rotate(-1.5deg);text-align:center;">
          <div style="font-weight:900;font-size:42px;color:#0f172a;line-height:1.12;">CÓ CHỒNG RỒI</div>
          <div style="margin-top:10px;display:block;padding:12px 18px;border-radius:20px;background:#e11d48;color:#ffffff;font-weight:900;font-size:44px;line-height:1.1;">CÀNG PHẢI CHĂM MÌNH!</div>
        </div>

        <!-- 3.05 - 10.52s: Zero-Whitespace 2-Tile Contrast Bento (BOTH tiles visible immediately — ZERO empty holes!) -->
        <div id="hk-bento" class="bento-lower-box" style="opacity:0;">
          <div class="sheen-bar"></div>
          <div id="hk-t1" class="float-card" style="position:relative;flex:1;border-radius:26px;background:linear-gradient(135deg,#eef2ff 0%,#dbeafe 100%);border:4px solid #3b82f6;padding:14px 20px;display:flex;align-items:center;gap:18px;">
            <div class="icon-badge-lg icon-bob" style="width:106px;height:152px;background:#2563eb;color:#fff;font-size:56px;">👨‍👩‍👧</div>
            <div style="flex:1;">
              <div style="font-weight:900;font-size:44px;color:#0f172a;line-height:1.08;">LO CHO CẢ NHÀ</div>
              <div style="margin-top:10px;display:inline-block;padding:8px 22px;border-radius:14px;background:#2563eb;color:#ffffff;font-weight:900;font-size:33px;">✓ ƯU TIÊN SỐ 1</div>
            </div>
          </div>
          <div id="hk-t2" class="pulse-alert" style="position:relative;flex:1;border-radius:26px;background:linear-gradient(135deg,#fff1f2 0%,#ffe4e6 100%);border:4px solid #e11d48;padding:14px 20px;display:flex;align-items:center;gap:18px;">
            <div class="icon-badge-lg" style="width:106px;height:152px;background:#e11d48;color:#fff;font-size:56px;">⏳</div>
            <div style="flex:1;">
              <div style="font-weight:900;font-size:42px;color:#0f172a;line-height:1.08;">CÒN BẢN THÂN:</div>
              <div style="margin-top:10px;display:inline-block;padding:8px 22px;border-radius:14px;background:#e11d48;color:#ffffff;font-weight:900;font-size:36px;">⚠ LUÔN ĐỂ LẠI SAU!</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2A. BEFORE MARRIAGE (10.66 - 16.54s): Left X=[54..486] holds s1_before_wed.mp4; Right X=[498..882] holds 3 Fat Full-Bleed Cards (ALL 3 visible immediately!) -->
      <div id="c2" class="clip" data-start="10.66" data-duration="5.88" data-track-index="1" data-layout-allow-overlap data-layout-allow-safe-zone>
        <div class="crown-zone-norm float-gentle">
          <div id="b1-pill" class="kobe-pill sub"><span>✨ HỒI CHƯA CƯỚI</span><span class="c-rose">• YÊU MÌNH</span></div>
          <svg id="b1-title" class="svg-headline" viewBox="0 0 970 116">
            <text x="485" y="92" text-anchor="middle" font-size="74" fill="url(#grad-rose)">RẠNG RỠ &amp; CHĂM CHÚT KỸ</text>
          </svg>
        </div>
        <div id="b1-stack" class="bento-right-stack" style="opacity:0;">
          <div id="b1-r1" class="mini-bento-card float-card" style="background:linear-gradient(135deg,#fff0f6,#ffe4ef);border-color:#f472b6;">
            <div class="icon-badge-lg icon-bob" style="background:#db2777;color:#fff;">💆‍♀️</div>
            <div style="font-weight:900;font-size:35px;color:#9d174d;line-height:1.12;">CHĂM DA<br/><span style="color:#0f172a;">CHĂM TÓC</span></div>
          </div>
          <div id="b1-r2" class="mini-bento-card float-card-alt" style="background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-color:#34d399;">
            <div class="icon-badge-lg icon-bob" style="background:#059669;color:#fff;">🥗</div>
            <div style="font-weight:900;font-size:35px;color:#065f46;line-height:1.12;">TẬP ĐỀU<br/><span style="color:#0f172a;">ĂN CHUẨN</span></div>
          </div>
          <div id="b1-r3" class="mini-bento-card float-card" style="background:linear-gradient(135deg,#eef2ff,#dbeafe);border-color:#60a5fa;">
            <div class="icon-badge-lg icon-bob" style="background:#2563eb;color:#fff;">👗</div>
            <div style="font-weight:900;font-size:35px;color:#1e40af;line-height:1.12;">ÁO ĐẸP<br/><span style="color:#0f172a;">RẠNG RỠ</span></div>
          </div>
        </div>
      </div>

      <!-- 2B. FULL KOBE STAGE #1 (16.58 - 25.46s): ALL 4 Bento cells visible immediately, lighting up sequentially on speech! -->
      <div id="c3" class="clip" data-start="16.58" data-duration="8.88" data-track-index="1" data-layout-allow-overlap data-layout-allow-safe-zone>
        <div id="f1-stage" class="kobe-full-stage">
          <div class="bento-grid-2x2">
            <div id="f1-c1" class="bento-cell float-card" style="background:linear-gradient(135deg,#ffffff,#eef2ff);border-color:#3b82f6;padding:14px;">
              <div class="cell-num" style="background:#2563eb;">1</div>
              <div class="icon-badge-lg icon-bob" style="width:76px;height:124px;background:#dbeafe;font-size:44px;">🍲</div>
              <div style="font-weight:900;font-size:31px;color:#0f172a;line-height:1.15;">CHỒNG ĂN?<br/><span class="c-cobalt">CON HỌC?</span></div>
            </div>
            <div id="f1-c2" class="bento-cell float-card-alt" style="background:linear-gradient(135deg,#ffffff,#fff0f6);border-color:#ec4899;padding:14px;">
              <div class="cell-num" style="background:#db2777;">2</div>
              <div class="icon-badge-lg icon-bob" style="width:76px;height:124px;background:#fce7f3;font-size:44px;">⚡</div>
              <div style="font-weight:900;font-size:32px;color:#0f172a;line-height:1.15;">TIỀN ĐIỆN<br/><span class="c-rose">ĐÓNG CHƯA?</span></div>
            </div>
            <div id="f1-c3" class="bento-cell float-card" style="background:linear-gradient(135deg,#ffffff,#ecfdf5);border-color:#10b981;padding:14px;">
              <div class="cell-num" style="background:#059669;">3</div>
              <div class="icon-badge-lg icon-bob" style="width:76px;height:124px;background:#d1fae5;font-size:44px;">🧺</div>
              <div style="font-weight:900;font-size:32px;color:#0f172a;line-height:1.15;">MAI ĐI CHỢ<br/><span class="c-emerald">MUA GÌ?</span></div>
            </div>
            <div id="f1-c4" class="bento-cell pulse-alert" style="background:linear-gradient(135deg,#fff1f2,#ffe4e6);border-color:#e11d48;padding:14px;">
              <div class="cell-num" style="background:#e11d48;">!</div>
              <div class="icon-badge-lg" style="width:76px;height:124px;background:#fecdd3;font-size:44px;">😔</div>
              <div style="font-weight:900;font-size:32px;color:#0f172a;line-height:1.15;">CÒN MÌNH:<br/><span class="c-rose">"ĐỂ MAI!"</span></div>
            </div>
          </div>

          <div class="highway-track" style="top:1178px;"><div class="highway-dashes"></div></div>
          <div id="f1-lp" class="pip-side-pill float-card" style="left:54px;width:228px;top:1330px;"><span class="c-cobalt">24/7</span><span>LO TOAN</span></div>
          <div id="f1-rp" class="pip-side-pill float-card-alt" style="left:654px;width:228px;top:1330px;border-color:#fda4af;"><span class="c-rose">QUÊN MÌNH</span></div>
        </div>
      </div>

      <!-- 3. MIRROR REALIZATION & NOT SELFISH (25.50 - 32.46s) -->
      <div id="c4" class="clip" data-start="25.50" data-duration="6.96" data-track-index="1" data-layout-allow-overlap data-layout-allow-safe-zone>
        <div class="crown-zone-norm float-gentle">
          <div id="m1-pill" class="kobe-pill sub"><span>🪞 NHÌN LẠI MÌNH</span><span class="c-cobalt">• TỈNH THỨC</span></div>
          <svg id="m1-title" class="svg-headline" viewBox="0 0 970 116">
            <text x="485" y="92" text-anchor="middle" font-size="72" fill="url(#grad-gold)">CHĂM MÌNH KHÔNG ÍCH KỶ!</text>
          </svg>
        </div>

        <div id="m1-right" class="bento-right-stack" style="opacity:0;">
          <div class="mini-bento-card float-card" style="background:linear-gradient(135deg,#fff1f2,#ffe4e6);border-color:#fb7185;flex-direction:column;justify-content:center;text-align:center;gap:8px;">
            <div style="font-size:52px;line-height:1;">🪞</div>
            <div style="font-weight:900;font-size:35px;color:#0f172a;line-height:1.12;">ĐÃ RẤT LÂU<br/><span class="c-rose">BỎ QUÊN MÌNH!</span></div>
          </div>
          <div class="mini-bento-card float-card-alt" style="background:#0f172a;border-color:#ffd154;flex-direction:column;justify-content:center;text-align:center;gap:8px;">
            <div style="font-size:48px;line-height:1;">💎</div>
            <div style="font-weight:900;font-size:34px;color:#ffffff;line-height:1.12;">YÊU BẢN THÂN<br/><span class="c-gold">LÀ ĐÚNG ĐẮN!</span></div>
          </div>
        </div>

        <div id="m1-wide" class="bento-lower-box" style="background:#0f172a;border-color:#ffd154;justify-content:center;align-items:center;text-align:center;opacity:0;">
          <div class="sheen-bar"></div>
          <div style="font-weight:800;font-size:34px;color:#fde68a;">💬 HẰNG NÓI THẬT VỚI CHỊ EM:</div>
          <div style="font-weight:900;font-size:50px;color:#ffffff;line-height:1.12;">CHĂM SÓC BẢN THÂN</div>
          <div style="padding:12px 28px;border-radius:22px;background:#ffd154;color:#0f172a;font-weight:900;font-size:48px;line-height:1.1;">KHÔNG PHẢI ÍCH KỶ!</div>
        </div>
      </div>

      <!-- 4. FULL KOBE STAGE #2: HEALTHY & CONFIDENT WIFE (32.50 - 40.38s): BOTH Power Bento rows visible immediately! -->
      <div id="c5" class="clip" data-start="32.50" data-duration="7.88" data-track-index="1" data-layout-allow-overlap data-layout-allow-safe-zone>
        <div id="f2-stage" class="kobe-full-stage">
          <div style="position:absolute;left:54px;top:734px;width:828px;height:432px;display:flex;flex-direction:column;gap:14px;">
            <div id="f2-r1" class="bento-cell float-card" style="flex:1;background:linear-gradient(135deg,#ffffff,#ecfdf5);border-color:#10b981;padding:16px 20px;gap:18px;">
              <div class="icon-badge-lg icon-bob" style="width:104px;height:156px;background:#059669;color:#fff;font-size:54px;">💪</div>
              <div style="flex:1;">
                <div style="font-weight:900;font-size:40px;color:#059669;line-height:1.1;">PHỤ NỮ KHỎE MẠNH</div>
                <div style="margin-top:8px;font-weight:900;font-size:33px;color:#0f172a;line-height:1.14;">→ ĐỦ SỨC CHĂM GIA ĐÌNH</div>
              </div>
            </div>
            <div id="f2-r2" class="bento-cell float-card-alt" style="flex:1;background:linear-gradient(135deg,#ffffff,#eef2ff);border-color:#3b82f6;padding:16px 20px;gap:18px;">
              <div class="icon-badge-lg icon-bob" style="width:104px;height:156px;background:#2563eb;color:#fff;font-size:54px;">✨</div>
              <div style="flex:1;">
                <div style="font-weight:900;font-size:40px;color:#2563eb;line-height:1.1;">PHỤ NỮ TỰ TIN</div>
                <div style="margin-top:8px;font-weight:900;font-size:33px;color:#0f172a;line-height:1.14;">→ SỐNG VUI HẠNH PHÚC</div>
              </div>
            </div>
          </div>

          <div class="highway-track" style="top:1178px;"><div class="highway-dashes"></div></div>
          <div id="f2-lp" class="pip-side-pill float-card" style="left:54px;width:228px;top:1330px;border-color:#6ee7b7;"><span class="c-emerald">💚 KHỎE ĐẸP</span></div>
          <div id="f2-rp" class="pip-side-pill float-card-alt" style="left:654px;width:228px;top:1330px;border-color:#93c5fd;"><span class="c-cobalt">✨ RẠNG RỠ</span></div>
        </div>
      </div>

      <!-- 5. SELF-WORTH & FINALE (40.42 - 50.52s) -->
      <div id="c6" class="clip" data-start="40.42" data-duration="10.10" data-track-index="1" data-layout-allow-overlap data-layout-allow-safe-zone>
        <div class="crown-zone-norm float-gentle">
          <div id="fn-pill" class="kobe-pill sub"><span>♥ HẰNG THU PHARMA</span><span class="c-emerald">• YÊU MÌNH</span></div>
          <svg id="fn-title" class="svg-headline" viewBox="0 0 970 116">
            <text x="485" y="92" text-anchor="middle" font-size="72" fill="url(#grad-emerald)">HẠNH PHÚC KHI SOI GƯƠNG!</text>
          </svg>
        </div>

        <div id="fn-worth" class="float-card" style="position:absolute;left:54px;top:1060px;width:828px;border-radius:34px;background:#ffffff;padding:24px;border:5px solid #3b82f6;box-shadow:0 22px 46px rgba(12,20,56,0.34);transform:rotate(-1.4deg);text-align:center;opacity:0;">
          <div style="font-weight:900;font-size:41px;color:#0f172a;line-height:1.12;">SỨC KHỎE LÀ CỦA CHỊ</div>
          <div style="margin-top:10px;display:block;padding:12px 20px;border-radius:20px;background:#2563eb;color:#ffffff;font-weight:900;font-size:43px;line-height:1.1;">KHÔNG ĐỢI AI KHEN!</div>
        </div>

        <div id="fn-bento" class="bento-lower-box" style="opacity:0;">
          <div class="sheen-bar"></div>
          <div class="float-card" style="flex:1;border-radius:26px;background:linear-gradient(135deg,#fff1f2,#ffe4e6);border:4px solid #fb7185;padding:14px 20px;display:flex;align-items:center;gap:18px;">
            <div class="icon-badge-lg" style="width:94px;height:136px;background:#e11d48;color:#fff;font-size:52px;">✕</div>
            <div style="flex:1;font-weight:900;font-size:36px;color:#0f172a;line-height:1.14;">ĐỪNG CHĂM MÌNH<br/><span class="c-rose">CHỈ ĐỂ CHỒNG NHÌN</span></div>
          </div>
          <div class="float-card-alt" style="flex:1.15;border-radius:26px;background:linear-gradient(135deg,#ecfdf5,#d1fae5);border:5px solid #10b981;padding:14px 20px;display:flex;align-items:center;gap:18px;">
            <div class="icon-badge-lg icon-bob" style="width:94px;height:146px;background:#059669;color:#fff;font-size:52px;">♥</div>
            <div style="flex:1;font-weight:900;font-size:37px;color:#0f172a;line-height:1.14;">HÃY ĐỂ CHÍNH MÌNH<br/><span class="c-emerald">VUI KHI SOI GƯƠNG!</span></div>
          </div>
        </div>
      </div>

    </div>
    <script>
      (function () {{
        gsap.ticker.lagSmoothing(0);
        var tl = gsap.timeline({{ paused: true }});
        tl.to(".highway-dashes", {{ x: -460, duration: {dur_s:.2f}, ease: "none" }}, 0);
        gsap.utils.toArray(".float-gentle").forEach(function (el, i) {{
          tl.fromTo(el, {{ yPercent: 0 }}, {{ yPercent: -2.0, duration: 1.45, repeat: 48, yoyo: true, ease: "sine.inOut", immediateRender: false }}, i * 0.2);
        }});
        gsap.utils.toArray(".float-card").forEach(function (el, i) {{
          tl.fromTo(el, {{ yPercent: 0, rotation: -0.3 }}, {{ yPercent: -1.8, rotation: 0.3, duration: 1.35, repeat: 50, yoyo: true, ease: "sine.inOut", immediateRender: false }}, i * 0.18);
        }});
        gsap.utils.toArray(".float-card-alt").forEach(function (el, i) {{
          tl.fromTo(el, {{ yPercent: 0, rotation: 0.3 }}, {{ yPercent: 1.8, rotation: -0.3, duration: 1.40, repeat: 50, yoyo: true, ease: "sine.inOut", immediateRender: false }}, 0.3 + i * 0.18);
        }});
        gsap.utils.toArray(".icon-bob").forEach(function (el, i) {{
          tl.fromTo(el, {{ scale: 1.0 }}, {{ scale: 1.10, duration: 0.85, repeat: 75, yoyo: true, ease: "sine.inOut", immediateRender: false }}, i * 0.15);
        }});
        gsap.utils.toArray(".pulse-alert").forEach(function (el) {{
          tl.fromTo(el, {{ scale: 1.0 }}, {{ scale: 1.028, duration: 0.65, repeat: 95, yoyo: true, ease: "sine.inOut", immediateRender: false }}, 0.1);
        }});
        gsap.utils.toArray(".sheen-bar").forEach(function (el, i) {{
          for (var tS = 0.8 + (i % 3) * 0.6; tS < {dur_s:.2f} - 1.0; tS += 2.8) {{
            tl.fromTo(el, {{ left: "-35%" }}, {{ left: "125%", duration: 1.15, ease: "power2.inOut", immediateRender: false }}, tS);
          }}
        }});

        function blurIn(sel, t, dur) {{
          tl.fromTo(sel, {{ opacity: 0, scale: 0.90, filter: "blur(16px)" }},
            {{ opacity: 1, scale: 1.0, filter: "blur(0px)", duration: dur || 0.26, ease: "back.out(1.4)", immediateRender: false }}, t);
        }}
        function blurOut(sel, t, dur) {{
          tl.to(sel, {{ opacity: 0, scale: 0.94, filter: "blur(14px)", duration: dur || 0.20, ease: "power2.in" }}, t);
        }}
        function activateTile(sel, tStart, tBeat) {{
          gsap.set(sel, {{ opacity: 0.46, scale: 0.96, filter: "grayscale(0.55)" }});
          tl.to(sel, {{ opacity: 1.0, scale: 1.0, filter: "grayscale(0)", duration: 0.28, ease: "back.out(1.7)" }}, tBeat);
        }}

        // 1. Hook (Zero empty holes: hk-t2 stays in soft preview at 3.08s and lights up vividly at 7.45s!)
        blurIn("#hk-top1", 0.08, 0.26); blurIn("#hk-chest", 0.14, 0.28);
        blurOut("#hk-chest", 2.82, 0.20); blurOut("#hk-top1", 2.85, 0.20);
        blurIn("#hk-top2", 3.05, 0.26); blurIn("#hk-bento", 3.08, 0.28);
        activateTile("#hk-t2", 3.08, 7.45);
        blurOut("#hk-bento", 10.36, 0.20); blurOut("#hk-top2", 10.36, 0.20);

        // 2A. Before Marriage (All 3 cards fill stack from 10.75s, lighting up sequentially on speech!)
        blurIn("#b1-pill", 10.70, 0.24); blurIn("#b1-title", 10.78, 0.28); blurIn("#b1-stack", 10.78, 0.26);
        activateTile("#b1-r2", 10.78, 12.60); activateTile("#b1-r3", 10.78, 14.35);
        blurOut("#b1-pill", 16.34, 0.18); blurOut("#b1-title", 16.34, 0.18); blurOut("#b1-stack", 16.34, 0.18);

        // 2B. Full Stage #1 (All 4 Bento cells fill stage from 16.58s, lighting up 1->2->3->4 on speech!)
        blurIn("#f1-stage", 16.58, 0.22);
        blurIn("#f1-lp", 16.72, 0.26); blurIn("#f1-rp", 16.78, 0.26);
        activateTile("#f1-c2", 16.58, 20.05); activateTile("#f1-c3", 16.58, 21.55); activateTile("#f1-c4", 16.58, 23.30);
        blurOut("#f1-stage", 25.26, 0.18);

        // 3. Mirror Realize & Not Selfish
        blurIn("#m1-pill", 25.54, 0.24); blurIn("#m1-title", 25.62, 0.28);
        blurIn("#m1-right", 25.66, 0.28); blurOut("#m1-right", 29.92, 0.18);
        blurIn("#m1-wide", 30.15, 0.26); blurOut("#m1-wide", 32.26, 0.18);
        blurOut("#m1-pill", 32.26, 0.18); blurOut("#m1-title", 32.26, 0.18);

        // 4. Full Stage #2 (Both Power Bento rows fill stage from 32.50s, Row 2 lights up at 36.85s!)
        blurIn("#f2-stage", 32.50, 0.22);
        blurIn("#f2-lp", 32.64, 0.26); blurIn("#f2-rp", 32.70, 0.26);
        activateTile("#f2-r2", 32.50, 36.85);
        blurOut("#f2-stage", 40.18, 0.18);

        // 5. Self-Worth & Finale
        blurIn("#fn-pill", 40.46, 0.24); blurIn("#fn-title", 40.54, 0.28);
        blurIn("#fn-worth", 40.60, 0.28); blurOut("#fn-worth", 44.14, 0.18);
        blurIn("#fn-bento", 44.36, 0.28);
        blurOut("#fn-bento", 50.24, 0.24); blurOut("#fn-pill", 50.24, 0.24); blurOut("#fn-title", 50.24, 0.24);

        window.__timelines = {{ main: tl }};
      }})();
    </script>
  </body>
</html>
"""
    os.makedirs(HF_DIR, exist_ok=True)
    with open(os.path.join(HF_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[HF] Rendering {HF_DIR} -> {KOBE_MOV} ({dur_s:.2f}s @ 30fps)...", flush=True)
    subprocess.run(["npx.cmd", "hyperframes", "render", HF_DIR, "--format", "mov", "-f", "30", "-o", KOBE_MOV], check=True)
    print("[HF] DONE kobe_dense_50s.mov!", flush=True)


def load_punchy_single_line_captions(max_dur: float):
    raw = json.load(open(WORDS_JSON, encoding="utf-8"))["words"]
    # Fix minor Whisper homophones on mapped words while preserving exact timestamps!
    for i in range(len(raw) - 1):
        if raw[i]["word"].lower() == "ý" and raw[i+1]["word"].lower().startswith("kỷ"):
            raw[i]["word"] = "ích"
        if raw[i]["word"].lower() == "đi" and raw[i+1]["word"].lower().startswith("chờ"):
            raw[i+1]["word"] = "chợ,"
        if raw[i]["word"].lower() == "phù" and raw[i+1]["word"].lower().startswith("thuộc"):
            raw[i]["word"] = "phụ"
    if raw and raw[0]["end"] > 2.95 and raw[6]["word"].lower().startswith("còn"):
        raw[6]["word"] = "Có"

    def allowed(tc):
        if tc < 2.95:  # Covered by giant Hook Chest Double-Pill!
            return False
        return not any(s0 - 0.04 <= tc <= s1 + 0.02 for s0, s1 in FULL_STAGES)

    words = [[w["word"].strip(), float(w["start"]), float(w["end"])]
             for w in raw if w["word"].strip() and allowed((w["start"] + w["end"]) * 0.5)]

    # Group into BIG PUNCHY 3-4 WORD SINGLE LINES (Zero tiny multi-line subtitle blocks!)
    phrases, cur = [], []
    for w in words:
        if cur:
            gap = w[1] - cur[-1][2]
            pt  = cur[-1][0]
            char_len = sum(len(x[0]) + 1 for x in cur) + len(w[0])
            if re.search(r"[.?!…;:]$", pt) or gap >= 0.32 or (re.search(r"[,]$", pt) and len(cur) >= 3) or len(cur) >= 4 or char_len > 21:
                phrases.append(cur); cur = []
        cur.append(w)
    if cur:
        phrases.append(cur)

    for p in phrases:
        p[0][0] = p[0][0].upper()
        for k in range(1, len(p)):
            p[k][0] = p[k][0].upper()

    groups = []
    for i, p in enumerate(phrases):
        t0  = p[0][1] - 0.03
        nxt = phrases[i + 1][0][1] if i + 1 < len(phrases) else max_dur - 0.12
        t1  = min(nxt - 0.03, p[-1][2] + 0.38)
        for s0, _ in FULL_STAGES:
            if t0 < s0 - 0.04 and t1 > s0 - 0.04:
                t1 = s0 - 0.04
        if t1 > t0 + 0.12:
            groups.append({"t0": t0, "t1": t1, "words": p})
    return groups


def draw_clean_broll_frame(canvas: Image.Image, vid_rgb: np.ndarray, t: float, s0: float, s1: float,
                           cx: float, cy: float, bw: int, bh: int, badge_txt: str, accent_rgb):
    dt_in, dt_out = t - s0, s1 - t
    op = min(h5.quintic_smooth(h5.clamp01(dt_in / 0.22)), h5.quintic_smooth(h5.clamp01(dt_out / 0.18)))
    if op <= 0.01:
        return
    sc_pop = 0.94 + 0.06 * h5.ease_out_back_soft(h5.clamp01(dt_in / 0.26), overshoot=1.04)
    z_kb = 1.02 + 0.06 * h5.clamp01((t - s0) / max(0.5, s1 - s0))
    crop = h5.fit_cover_subpixel(vid_rgb, bw, bh, zoom=z_kb, pan_x=0.0, pan_y=-0.02)

    pad = 16
    card = Image.new("RGBA", (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 6, pad + bw, pad + bh + 6], radius=30, fill=(10, 18, 48, 95))
    from PIL import ImageFilter
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(8)))

    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=28, fill=255)
    vl = Image.new("RGBA", card.size, (0, 0, 0, 0))
    vl.paste(crop.convert("RGBA"), (pad, pad), mask)
    card = Image.alpha_composite(card, vl)

    d = ImageDraw.Draw(card)
    d.rounded_rectangle([pad, pad, pad + bw - 1, pad + bh - 1], radius=28, outline=(255, 255, 255, 255), width=6)

    if badge_txt:
        f_b = h5.get_font(FONT_SUB, 36)
        tw = int(d.textlength(badge_txt, font=f_b))
        pw, ph = tw + 36, 54
        bx, by = pad + 16, pad + bh - ph - 16
        d.rounded_rectangle([bx, by, bx + pw, by + ph], radius=18, fill=(*accent_rgb, 242), outline=(255, 255, 255, 255), width=3)
        d.text((bx + 18, by + 6), badge_txt, font=f_b, fill=(255, 255, 255, 255))

    h5.paste_centered_rgba(canvas, card, cx, cy, scale=sc_pop, opacity=op)


def chunk_worker(args):
    c_idx, f_start, f_end = args
    n_frames = f_end - f_start
    t_s, t_e = f_start / FPS, f_end / FPS
    chunk_mp4 = os.path.join(SRC_DIR, f"_dense_chunk_{c_idx:02d}.mp4")

    clips = {
        sn: h5.load_vid_frames_wh(os.path.join(MEDIA_DIR, f"{sn}.mp4"), 1024, 576)
        for bs0, bs1, sn, _, _, _, _, _, _ in BROLL_SLOTS
        if not (bs1 + 0.3 < t_s or bs0 - 0.3 > t_e)
    }
    cap_groups = load_punchy_single_line_captions((f_end + 600) / FPS)
    ROSE_W    = {"CƯỚI", "CHỒNG", "SAI", "LẦM", "ÍCH", "KỶ", "QUÊN", "ĐỪNG"}
    COBALT_W  = {"TIỀN", "ĐIỆN", "CHỢ", "LO", "NHÀ"}
    EMERALD_W = {"KHỎE", "ĐẸP", "HẠNH", "PHÚC", "CHĂM", "YÊU", "MÌNH", "GƯƠNG"}

    pa = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t_s:.6f}", "-i", SRC_MP4,   "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    pm = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t_s:.6f}", "-i", MATTE_MP4, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "gray",  "-"], stdout=subprocess.PIPE)
    pk = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t_s:.6f}", "-i", KOBE_MOV,  "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgba",  "-"], stdout=subprocess.PIPE)

    wr = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-threads", "3", "-pix_fmt", "yuv420p", chunk_mp4], stdin=subprocess.PIPE)

    # Subtle gentle camera micro-drift ONLY on unzoomed sections (t >= 10.65s), keeping 100% of CapCut's native Hook zoom!
    for li in range(n_frames):
        ba, bm, bk = pa.stdout.read(W * H * 3), pm.stdout.read(W * H), pk.stdout.read(W * H * 4)
        if len(ba) < W * H * 3 or len(bm) < W * H:
            break
        rgb_raw   = np.frombuffer(ba, np.uint8).reshape((H, W, 3))
        matte_raw = np.frombuffer(bm, np.uint8).reshape((H, W))
        kobe_rgba = np.frombuffer(bk, np.uint8).reshape((H, W, 4)) if len(bk) == W * H * 4 else None
        t = (f_start + li) / FPS

        # Subtle push-in on punchline beats (30.15..32.45 and 40.45..44.30) without exceeding crown safe margin
        if 30.15 <= t <= 32.45 or 40.45 <= t <= 44.30:
            fg_rgb = np.array(h5.fit_cover_subpixel(rgb_raw, W, H, zoom=1.035, pan_x=0.0, pan_y=0.006))
        else:
            fg_rgb = rgb_raw

        in_full = next(((s0, s1) for s0, s1 in FULL_STAGES if s0 <= t <= s1), None)
        ov_im   = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        if not in_full:
            # 1. HyperFrames Kobe Dense Overlay (Top Crown Headers + Dense Bento Cards)
            if kobe_rgba is not None and kobe_rgba[:, :, 3].max() > 0:
                ov_im.alpha_composite(Image.fromarray(kobe_rgba, "RGBA"), dest=(0, 0))

            # 2. Left-Half Full-Bleed AI B-Roll inside Asymmetric Bento Split (X=[54..486], Y=[964..1416])
            for bs0, bs1, sn, mode, cx_b, cy_b, bw_b, bh_b, ac in BROLL_SLOTS:
                if mode == "lower" and bs0 <= t <= bs1:
                    vf = h5.get_clip_frame_single_pass(clips, sn, t - bs0, bs1 - bs0)
                    badge = "TRƯỚC CƯỚI" if "before" in sn else "NHÌN LẠI"
                    draw_clean_broll_frame(ov_im, vf, t, bs0, bs1, cx_b, cy_b, bw_b, bh_b, badge, ac)

            # 3. BIG BOLD 58px SINGLE-LINE SUBTITLES (Centered at X=468 inside [54..882], Y=1492 <= 1545px!)
            for g in cap_groups:
                if g["t0"] <= t < g["t1"]:
                    dt_in, dt_out = t - g["t0"], g["t1"] - t
                    u_in  = h5.ease_out_back_soft(h5.clamp01(dt_in / 0.18), overshoot=1.05)
                    u_out = h5.septic_smooth(h5.clamp01(dt_out / 0.15))
                    op_g  = min(h5.quintic_smooth(h5.clamp01(dt_in / 0.12)), u_out)
                    if op_g <= 0.01:
                        break
                    cap_sz, gap = 58.0, 13.0
                    x_center, max_w, cy_w = 468.0, 816.0, 1492.0 + (1.0 - u_in) * 10.0
                    wrs, tot_w = [], 0.0
                    for wi, (wtxt, ws, we) in enumerate(g["words"]):
                        is_act = (ws - 0.04 <= t <= we + 0.18)
                        wclean = wtxt.upper().strip(",.?!:;\"")
                        pal = "rose_satin" if wclean in ROSE_W else ("cobalt" if wclean in COBALT_W else ("emerald" if wclean in EMERALD_W else ("gold" if is_act else "pearl")))
                        sp = h5.render_thin_grad_word(wtxt, cap_sz, palette=pal, stroke_w=3)
                        adv = ImageDraw.Draw(ov_im).textlength(wtxt, font=h5.get_font(FONT_SUB, cap_sz)) + 3.0
                        wrs.append((sp, adv, 1.07 if is_act else 1.00))
                        tot_w += adv + (gap if wi > 0 else 0.0)
                    fk = min(1.0, max_w / max(1.0, tot_w))
                    cx_w = x_center - (tot_w * fk) * 0.5
                    for sp, adv, pls in wrs:
                        ea = adv * fk
                        h5.paste_centered_rgba(ov_im, sp, cx_w + ea * 0.5, cy_w, scale=fk * pls, opacity=op_g)
                        cx_w += ea + gap * fk
                    break
            comp_im = Image.alpha_composite(Image.fromarray(fg_rgb, "RGB").convert("RGBA"), ov_im)

        else:
            # FULL KOBE MOTION STAGE (80% Visual Density: 970x464 Cinema Card + Z-Space Pill + 2x2 Bento + Circle PiP!)
            s0_f, s1_f = in_full
            if kobe_rgba is not None:
                ov_im.alpha_composite(Image.fromarray(kobe_rgba[:, :, :3], "RGB").convert("RGBA"), dest=(0, 0))

            # Draw 970x464 Cinema B-Roll BEFORE re-compositing floating Z-space pill so the pill sits IN FRONT!
            for bs0, bs1, sn, mode, cx_b, cy_b, bw_b, bh_b, ac in BROLL_SLOTS:
                if mode == "full" and bs0 <= t <= bs1:
                    vf = h5.get_clip_frame_single_pass(clips, sn, t - bs0, bs1 - bs0)
                    draw_clean_broll_frame(ov_im, vf, t, bs0, bs1, cx_b, cy_b, bw_b, bh_b, "", ac)

            # Re-composite floating Z-Space Kobe Pill (y=250..365) IN FRONT of top cinema frame!
            if kobe_rgba is not None and kobe_rgba[250:370, :, 3].max() > 0:
                # Extract only bright white pill region (above background dot-grid) by rendering pill on top via alpha mask
                pass
            # Let's draw a crisp Z-space Kobe Pill right over top-left of cinema card so it pops 100% cleanly over B-Roll!
            d_ov = ImageDraw.Draw(ov_im)
            f_zp = h5.get_font(FONT_SUB, 46)
            p1 = "SAU KHI CƯỚI • " if s0_f < 25.0 else "PHỤ NỮ BIẾT • "
            p2 = "TRĂM NỖI LO" if s0_f < 25.0 else "YÊU CHÍNH MÌNH"
            c2 = (225, 29, 72, 255) if s0_f < 25.0 else (5, 150, 105, 255)
            w1 = int(d_ov.textlength(p1, font=f_zp))
            w2 = int(d_ov.textlength(p2, font=f_zp))
            pw, ph = w1 + w2 + 56, 78
            pill_im = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
            dp = ImageDraw.Draw(pill_im)
            dp.rounded_rectangle([12, 16, 12 + pw, 16 + ph], radius=39, fill=(10, 18, 48, 85))
            from PIL import ImageFilter
            pill_im = pill_im.filter(ImageFilter.GaussianBlur(5))
            dp = ImageDraw.Draw(pill_im)
            dp.rounded_rectangle([10, 10, 10 + pw, 10 + ph], radius=39, fill=(255, 255, 255, 255), outline=c2, width=4)
            dp.text((38, 19), p1, font=f_zp, fill=(15, 23, 42, 255))
            dp.text((38 + w1, 19), p2, font=f_zp, fill=c2)
            pill_rot = pill_im.rotate(1.6, resample=Image.Resampling.BICUBIC, expand=True)
            ov_im.alpha_composite(pill_rot, dest=(68, 254))

            # Bottom Circle PiP (cx=468, cy=1368, diam=340 -> bottom=1543px <= 1545px Safe Zone!) with Iris Wipe!
            dt_s, dt_e = t - s0_f, s1_f - t
            ir_u = min(h5.quintic_smooth(h5.clamp01(dt_s / 0.22)), h5.quintic_smooth(h5.clamp01(dt_e / 0.20)))
            diam, pad = PIP_DIAM, 20
            py1, py2, px1, px2 = PIP_BOX
            face = Image.fromarray(rgb_raw[py1:py2, px1:px2], "RGB").resize((diam, diam), Image.Resampling.LANCZOS)
            f_m  = Image.fromarray(matte_raw[py1:py2, px1:px2], "L").resize((diam, diam), Image.Resampling.BILINEAR)
            bg_c = Image.new("RGB", (diam, diam), (226, 234, 252))
            dc   = ImageDraw.Draw(bg_c)
            for gy in range(10, diam, 24):
                for gx in range(10, diam, 24):
                    dc.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=(182, 196, 238))
            comp_p = Image.composite(face, bg_c, f_m)

            card = Image.new("RGBA", (diam + pad * 2, diam + pad * 2), (0, 0, 0, 0))
            sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse([pad, pad + 8, pad + diam, pad + diam + 8], fill=(22, 36, 98, 72))
            card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(9)))
            r_now = int(round((diam * 0.5) * max(0.05, ir_u)))
            cm = Image.new("L", (diam, diam), 0)
            cx0 = diam // 2
            ImageDraw.Draw(cm).ellipse([cx0 - r_now, cx0 - r_now, cx0 + r_now, cx0 + r_now], fill=255)
            vl = Image.new("RGBA", card.size, (0, 0, 0, 0))
            vl.paste(comp_p.convert("RGBA"), (pad, pad), cm)
            card = Image.alpha_composite(card, vl)
            d = ImageDraw.Draw(card)
            ring_col = (225, 29, 72, 255) if s0_f < 25.0 else (5, 150, 105, 255)
            d.ellipse([pad - 5, pad - 5, pad + diam + 4, pad + diam + 4], outline=ring_col, width=5)
            d.ellipse([pad - 1, pad - 1, pad + diam, pad + diam], outline=(255, 255, 255, 255), width=8)
            h5.paste_centered_rgba(ov_im, card, PIP_CX, PIP_CY + math.sin((t - s0_f) * 2.2) * 3.0 * ir_u, scale=0.94 + 0.06 * ir_u, opacity=1.0)
            comp_im = ov_im

        wr.stdin.write(np.array(comp_im.convert("RGB"), np.uint8).tobytes())

    wr.stdin.close(); wr.wait()
    for p in (pa, pm, pk):
        p.stdout.close(); p.wait()
    return c_idx, chunk_mp4


def mix_audio_master(vid_dur: float):
    N = int(round(vid_dur * SR))
    voc_wav = os.path.join(SRC_DIR, "vocals_48k.wav")
    voc = m5.decode_stereo_f32(voc_wav, dur_limit=vid_dur, af="highpass=f=75,acompressor=threshold=-18dB:ratio=2.2:attack=10:release=140:makeup=2dB")
    voc = np.vstack([voc, np.zeros((max(0, N - len(voc)), 2), np.float32)])[:N]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vp = np.vstack([voc, np.zeros((n_hops * hop - N, 2), np.float32)])
    vo_rms = np.sqrt(np.mean(vp.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.016).astype(np.float32)

    sp_samples = np.repeat(speaking > 0.5, hop)[:N]
    cur_rms = float(np.sqrt(np.mean(voc[sp_samples] ** 2))) if np.any(sp_samples) else float(np.sqrt(np.mean(voc ** 2)))
    if cur_rms > 1e-4:
        voc *= (0.168 / cur_rms)

    eq_af = f"atrim=60.30:{60.30 + vid_dur + 3.0:.2f},asetpts=PTS-STARTPTS,highpass=f=85,equalizer=f=1800:t=q:w=1.25:g=-4.5,lowpass=f=11500"
    bgm = m5.decode_stereo_f32(TOKYO_BGM, af=eq_af)
    bgm = np.vstack([bgm, np.zeros((max(0, N - len(bgm)), 2), np.float32)])[:N]
    br = float(np.sqrt(np.mean(bgm ** 2)))
    if br > 1e-5:
        bgm *= (0.112 / br)
    sp_dil = np.zeros_like(speaking)
    for ih in range(n_hops):
        if speaking[ih] > 0.5:
            sp_dil[max(0, ih - 12):min(n_hops, ih + 22)] = 1.0
    w_sm = np.hanning(35).astype(np.float32); w_sm /= np.sum(w_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), w_sm, mode="valid")[:n_hops]
    duck_hop = 0.30 * (1.0 - sp_sm) + 0.17 * sp_sm
    duck_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, duck_hop).astype(np.float32)
    t_ax = np.arange(N, dtype=np.float32) / SR
    end_fd = np.clip((vid_dur - t_ax) / 0.80, 0.0, 1.0)[:, None]
    bgm_bus = bgm * duck_env[:, None] * end_fd

    bank = m5.load_sfx_bank()
    if os.path.exists(RISER_01_LOCAL):
        r_arr = m5.decode_stereo_f32(RISER_01_LOCAL, af="atrim=1.65:3.10,asetpts=PTS-STARTPTS,highpass=f=120,equalizer=f=2800:t=q:w=1.10:g=-2.5,lowpass=f=12500")
        n_in, n_out = int(0.18 * SR), int(0.035 * SR)
        r_arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        r_arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(r_arr)))
        if pk > 1e-5:
            r_arr /= pk
        bank["hook_riser"] = (r_arr, int(np.argmax(np.max(np.abs(r_arr), axis=1))))

    sfx_bus = np.zeros((N, 2), np.float32)
    # Tactile Micro-SFX strictly synced to card impacts (-10..-13 dB below Voice!)
    m5.stamp(sfx_bus, bank, "airy_whoosh", 0.08, -11.0)
    m5.stamp(sfx_bus, bank, "pop_clean",   0.18, -11.4, speaking_hops=speaking)
    m5.stamp(sfx_bus, bank, "swoosh_up",   3.02, -10.8)
    m5.stamp(sfx_bus, bank, "pop_round",   3.14, -11.4, speaking_hops=speaking)
    m5.stamp(sfx_bus, bank, "pop_clean",   7.52, -11.2, speaking_hops=speaking)

    # Post-Hook Riser Climax at t=10.62s!
    m5.stamp(sfx_bus, bank, "hook_riser",   RISER_T, -7.8, align_peak=True, speaking_hops=None)
    m5.stamp(sfx_bus, bank, "shimmer_rise", RISER_T, -10.4, align_peak=True, speaking_hops=None)
    m5.stamp(sfx_bus, bank, "airy_whoosh",  RISER_T + 0.02, -10.2, align_peak=True, speaking_hops=None)

    # Before Marriage 3 staggered cards
    for tc in (10.92, 12.68, 14.42):
        m5.stamp(sfx_bus, bank, "pop_clean", tc, -11.6, speaking_hops=speaking)

    # Full Stage #1 4 Bento tiles
    m5.stamp(sfx_bus, bank, "swoosh_up", 16.54, -10.6)
    for tc in (17.02, 20.12, 21.62, 23.38):
        m5.stamp(sfx_bus, bank, "pop_round", tc, -11.2, speaking_hops=speaking)

    # Mirror & Punchline
    m5.stamp(sfx_bus, bank, "airy_whoosh", 25.50, -11.0)
    m5.stamp(sfx_bus, bank, "pop_clean",   30.20, -10.8, speaking_hops=speaking)

    # Full Stage #2 2 Power Bento rows
    m5.stamp(sfx_bus, bank, "swoosh_up", 32.46, -10.6)
    m5.stamp(sfx_bus, bank, "pop_round", 32.82, -11.2, speaking_hops=speaking)
    m5.stamp(sfx_bus, bank, "pop_clean", 36.92, -11.2, speaking_hops=speaking)

    # Finale
    m5.stamp(sfx_bus, bank, "airy_whoosh", 40.42, -11.0)
    m5.stamp(sfx_bus, bank, "pop_round",   44.42, -11.2, speaking_hops=speaking)

    mix = np.tanh((voc + bgm_bus + sfx_bus) * 0.96) * 0.95
    import wave
    raw_mix  = os.path.join(SRC_DIR, "_raw_mix.wav")
    norm_wav = os.path.join(SRC_DIR, "master_norm_dense.wav")
    pcm16 = np.clip(mix * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(raw_mix, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", raw_mix,
        "-af", "loudnorm=I=-14.0:TP=-1.2:LRA=7.0:linear=true",
        "-ar", "48000", "-ac", "2", norm_wav
    ], check=True)
    return norm_wav


def main():
    t0 = time.time()
    pr = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=nb_read_frames:format=duration", "-of", "json", SRC_MP4
    ], text=True))
    n_fr    = int(pr["streams"][0]["nb_read_frames"])
    vid_dur = float(pr["format"]["duration"])

    if not (os.path.exists(KOBE_MOV) and os.path.getsize(KOBE_MOV) > 100_000_000):
        author_and_render_hyperframes(vid_dur)

    raw_vid = os.path.join(SRC_DIR, "_video_only_dense.mp4")
    if not (os.path.exists(raw_vid) and os.path.getsize(raw_vid) > 20_000_000):
        step = (n_fr + 3) // 4
        tasks = [(i, i * step, min(n_fr, (i + 1) * step)) for i in range(4) if i * step < min(n_fr, (i + 1) * step)]
        print(f"[KB06-DENSE] Compositing {n_fr} frames ({vid_dur:.2f}s) across 4 workers...", flush=True)
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as ex:
            res = sorted(list(ex.map(chunk_worker, tasks)), key=lambda x: x[0])

        vlist = os.path.join(SRC_DIR, "_vlist_dense.txt")
        open(vlist, "w", encoding="utf-8").write("".join("file '" + cp.replace("\\", "/") + "'\n" for _, cp in res))

        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", vlist,
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p", raw_vid
        ], check=True)
        for _, cp in res:
            try: os.remove(cp)
            except OSError: pass

    norm_wav = mix_audio_master(vid_dur)
    local_final = os.path.join(KB06_DIR, FINAL_FN)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", raw_vid, "-i", norm_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", local_final
    ], check=True)

    err_c = subprocess.run(["ffmpeg", "-v", "error", "-i", local_final, "-f", "null", "-"], capture_output=True, text=True)
    assert err_c.stderr.strip() == "", f"Decode error: {err_c.stderr}"

    # Build 20-panel QC Contact Sheet + Safe-Zone Overlay Audit Sheet!
    sheet = Image.new("RGB", (270 * 5, 480 * 4), (14, 18, 30))
    fnt = ImageFont.truetype(FONT_SUB, 24)
    key_ts = [0.6, 2.0, 4.2, 8.2, 10.62, 11.4, 13.4, 15.2, 17.6, 20.6, 22.2, 24.2, 26.8, 31.2, 33.8, 37.8, 41.8, 45.2, 47.8, 49.8]
    for idx, ts in enumerate(key_ts):
        ts = min(vid_dur - 0.25, ts)
        tj = os.path.join(CHECK_DIR, f"_q_{idx}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", local_final, "-frames:v", "1", "-q:v", "2", tj], check=True)
        im = Image.open(tj).convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([8, 8, 118, 40], radius=10, fill=(14, 18, 30))
        d.text((16, 10), f"{ts:05.2f}s", font=fnt, fill=(255, 214, 84))
        sheet.paste(im, ((idx % 5) * 270, (idx // 5) * 480))
        os.remove(tj)
    sh_p = os.path.join(ART_DIR, "kb06_kobe_dense_sheet.jpg")
    sheet.save(sh_p, quality=93)

    # Export to HTPM Brand Folder (both 261124 and overwrite 261123 so zero stale copy remains!) + D_OUT + MASTER_OUT
    for dst in [
        os.path.join(BRAND_OUT, FINAL_FN),
        os.path.join(BRAND_OUT, FINAL_FN_23),
        os.path.join(D_OUT, FINAL_FN),
        os.path.join(MASTER_OUT, FINAL_FN),
    ]:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(local_final, dst)
            print("EXPORTED_FINAL ->", dst, flush=True)
        except Exception as e:
            print("Copy warn:", dst, e, flush=True)

    try:
        os.makedirs(DRIVE_PROJ, exist_ok=True)
        shutil.copy2(__file__, os.path.join(DRIVE_PROJ, "build_and_render_kb06_kobe_dense.py"))
        shutil.copy2(sh_p, os.path.join(DRIVE_PROJ, "kb06_kobe_dense_sheet.jpg"))
    except Exception as e:
        print("Drive archive warn:", e, flush=True)

    print(f"ALL_KOBE_DENSE_COMPLETE in {time.time() - t0:.1f}s!", flush=True)


if __name__ == "__main__":
    main()
