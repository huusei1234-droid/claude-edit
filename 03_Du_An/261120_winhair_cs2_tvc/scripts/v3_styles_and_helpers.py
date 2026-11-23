import os
import json
import html

PROJ = r"d:\AI\full studio\projects\winhair-cs2-tvc"
COMP_DIR = os.path.join(PROJ, "compositions")
os.makedirs(COMP_DIR, exist_ok=True)

PDIR = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\TVC WinHair CS2 - ban Reels_v2 (1)-sao chép (1)"
DC_PATH = os.path.join(PROJ, "scratch_media", "capcut_backup_before_v5_roundtrip", "sub_draft_content.json")

# Warm Editorial Cinema TVC Typography System (Zero cold/AI tech UI look, 100% Vietnamese clarity)
FONT_FACES_CSS = """
@font-face {
  font-family: "Playfair Display";
  src: url("assets/fonts/PlayfairDisplay-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Playfair Display";
  src: url("assets/fonts/PlayfairDisplay-ExtraBold.ttf") format("truetype");
  font-weight: 800;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Playfair Display";
  src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype");
  font-weight: 700;
  font-style: italic;
  font-display: block;
}
@font-face {
  font-family: "Cormorant Garamond";
  src: url("assets/fonts/CormorantGaramond-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Cormorant Garamond";
  src: url("assets/fonts/CormorantGaramond-BoldItalic.ttf") format("truetype");
  font-weight: 700;
  font-style: italic;
  font-display: block;
}
@font-face {
  font-family: "Oswald";
  src: url("assets/fonts/Oswald-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Barlow Condensed";
  src: url("assets/fonts/BarlowCondensed-ExtraBold.ttf") format("truetype");
  font-weight: 800;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Barlow Condensed";
  src: url("assets/fonts/BarlowCondensed-Black.ttf") format("truetype");
  font-weight: 900;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Montserrat";
  src: url("assets/fonts/Montserrat-SemiBold.ttf") format("truetype");
  font-weight: 600;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Montserrat";
  src: url("assets/fonts/Montserrat-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Montserrat";
  src: url("assets/fonts/Montserrat-ExtraBold.ttf") format("truetype");
  font-weight: 800;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Be Vietnam Pro";
  src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype");
  font-weight: 600;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "Be Vietnam Pro";
  src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype");
  font-weight: 700;
  font-style: normal;
  font-display: block;
}
@font-face {
  font-family: "WindSong";
  src: url("assets/fonts/WindSong-Medium.ttf") format("truetype");
  font-weight: 500;
  font-style: normal;
  font-display: block;
}
"""

SHARED_LUXURY_CSS = FONT_FACES_CSS + """
:root {
  --obsidian: #16110D;
  --walnut: #2A1C13;
  --champagne: #E6C37A;
  --pale-gold: #FFF1CF;
  --antique-gold: #B68B44;
  --crimson: #9E232B;
  --ivory: #FAF5EC;
  --warm-gray: #E5DAC8;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
#root {
  position: absolute;
  inset: 0;
  width: 1920px;
  height: 1080px;
  overflow: hidden;
  font-family: "Be Vietnam Pro", sans-serif;
  color: var(--ivory);
}
.wh-stage {
  position: absolute;
  inset: 0;
  width: 1920px;
  height: 1080px;
  overflow: hidden;
}

/* Warm Cinema Studio Backdrops (Rich espresso-amber warmth matching Win Hair wood & leather, zero cold terminal black) */
.wh-bg-obsidian {
  position: absolute;
  inset: 0;
  background-color: #120D0A;
  background-image:
    radial-gradient(ellipse at 50% 12%, rgba(96, 66, 36, 0.56) 0%, rgba(28, 20, 15, 0.98) 62%, #120D0A 100%);
}
.wh-bg-walnut {
  position: absolute;
  inset: 0;
  background-color: #120D0A;
  background-image:
    radial-gradient(ellipse at 35% 16%, rgba(112, 74, 40, 0.58) 0%, rgba(30, 21, 15, 0.98) 64%, #120D0A 100%);
}
.wh-bg-crimson {
  position: absolute;
  inset: 0;
  background-color: #120D0A;
  background-image:
    radial-gradient(ellipse at 60% 14%, rgba(114, 42, 34, 0.46) 0%, rgba(28, 19, 15, 0.98) 62%, #120D0A 100%);
}
.wh-bg-beams {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 0%, rgba(242, 206, 134, 0.12) 0%, transparent 52%);
  pointer-events: none;
}
.wh-bokeh-vid {
  position: absolute;
  left: 0;
  top: 0;
  width: 1920px;
  height: 1080px;
  object-fit: cover;
  mix-blend-mode: screen;
  opacity: 0.24;
  pointer-events: none;
}

/* ==========================================================================
   WARM METALLIC GOLD TVC TYPOGRAPHY (0% Stroke, Bold & Readable at Every Size)
   ========================================================================== */
.wh-bullion-wrap {
  position: relative;
  display: inline-block;
}
.wh-bullion-face {
  display: inline-block;
  padding: 48px 22px 28px 22px;
  margin: -44px -22px -24px -22px;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  background-size: 240% 100%, 100% 100%;
  background-position: -130% 0, 0 0;
  filter: drop-shadow(0 5px 18px rgba(0, 0, 0, 0.68));
}
.wh-gold-metal {
  background-image:
    linear-gradient(112deg, rgba(255,255,255,0) 38%, rgba(255,253,244,0.94) 50%, rgba(255,255,255,0) 62%),
    linear-gradient(
      180deg,
      #FFFDF4 0%,
      #F6E2B3 20%,
      #CCA15A 42%,
      #FFF0CA 54%,
      #D4AC67 70%,
      #9A7032 88%,
      #ECD196 100%
    );
}
.wh-gold-price {
  background-image:
    linear-gradient(112deg, rgba(255,255,255,0) 38%, rgba(255,254,246,0.96) 50%, rgba(255,255,255,0) 62%),
    linear-gradient(
      180deg,
      #FFF9E4 0%,
      #F3DCAA 24%,
      #CFA75E 48%,
      #FCEBC4 66%,
      #A87B37 100%
    );
}

/* Bold, Larger TVC Display Sizes */
.wh-disp-xl {
  font-family: "Montserrat", sans-serif;
  font-weight: 800;
  font-size: 92px;
  line-height: 1.10;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.wh-disp-arch {
  font-family: "Playfair Display", serif;
  font-weight: 800;
  font-size: 54px;
  line-height: 1.32;
  letter-spacing: 0.005em;
  text-transform: uppercase;
}
.wh-disp-lg {
  font-family: "Playfair Display", serif;
  font-weight: 800;
  font-size: 56px;
  line-height: 1.32;
  letter-spacing: 0.005em;
  text-transform: uppercase;
}
.wh-disp-edit {
  font-family: "Cormorant Garamond", serif;
  font-weight: 700;
  font-style: italic;
  font-size: 66px;
  line-height: 1.28;
  letter-spacing: 0.005em;
}
.wh-disp-md {
  font-family: "Playfair Display", serif;
  font-weight: 800;
  font-size: 46px;
  line-height: 1.30;
  letter-spacing: 0.005em;
  text-transform: uppercase;
}
.wh-disp-mega {
  font-family: "Barlow Condensed", sans-serif;
  font-weight: 800;
  font-size: 176px;
  line-height: 1.00;
  letter-spacing: -0.015em;
  text-transform: uppercase;
}
.wh-sig-script {
  font-family: "WindSong", cursive;
  font-weight: 500;
  font-size: 48px;
  color: #F2DCAC;
  letter-spacing: 0.01em;
  text-shadow: 0 3px 14px rgba(0,0,0,0.75);
}

/* Full-Width Cinema Header (Corner logo removed -> wide, generous layout!) */
.wh-header {
  position: absolute;
  left: 96px;
  right: 96px;
  top: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 15;
}
.wh-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 4px;
}
.wh-eyebrow-txt {
  font-family: "Be Vietnam Pro", sans-serif;
  font-weight: 700;
  font-size: 19px;
  letter-spacing: 0.16em;
  color: var(--champagne);
  text-transform: uppercase;
  text-shadow: 0 2px 10px rgba(0,0,0,0.65);
}
.wh-eyebrow-star {
  color: var(--champagne);
  font-size: 15px;
  opacity: 0.85;
}
.wh-anamorphic-flare {
  width: 280px;
  height: 2px;
  margin-top: 6px;
  border-radius: 2px;
  background: radial-gradient(ellipse at 50% 50%, rgba(246, 214, 146, 0.78) 0%, transparent 80%);
}

/* Soft Cinema Video Frame (Organic rounded corners + deep film shadow, zero harsh wireframe UI box) */
.wh-card {
  position: absolute;
  border-radius: 18px;
  overflow: hidden;
  background: #17120E;
  border: 1px solid rgba(243, 214, 156, 0.24);
  box-shadow: 0 26px 60px rgba(0, 0, 0, 0.72);
}
.wh-vid-fill {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.wh-card-shade {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 44%;
  background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(14,10,8,0.86) 100%);
  pointer-events: none;
}
.wh-card-sheen {
  position: absolute;
  inset: -25%;
  background: linear-gradient(112deg, transparent 42%, rgba(255, 240, 200, 0.30) 50%, transparent 58%);
  pointer-events: none;
  opacity: 0;
}
.wh-card-caption {
  position: absolute;
  left: 26px;
  right: 26px;
  bottom: 22px;
  z-index: 5;
}
.wh-card-h3 {
  font-family: "Oswald", sans-serif;
  font-weight: 700;
  font-size: 38px;
  line-height: 1.15;
  letter-spacing: 0.02em;
  color: #FFF9EE;
  text-transform: uppercase;
  text-shadow: 0 3px 14px rgba(0, 0, 0, 0.90);
}
.wh-card-p {
  margin-top: 6px;
  font-family: "Be Vietnam Pro", sans-serif;
  font-weight: 600;
  font-size: 20px;
  line-height: 1.36;
  color: #EFE5D6;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.90);
}

/* Frameless Editorial Feature Strip (Replaces boxy SaaS/code .wh-spec-item rectangles!) */
.wh-spec-row {
  position: absolute;
  display: flex;
  gap: 38px;
  align-items: center;
  justify-content: center;
  z-index: 15;
}
.wh-spec-item {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  font-family: "Be Vietnam Pro", sans-serif;
  font-weight: 700;
  font-size: 22px;
  letter-spacing: 0.06em;
  color: #FFF6E6;
  text-transform: uppercase;
  text-shadow: 0 3px 14px rgba(0, 0, 0, 0.88);
}
.wh-spec-item::before {
  content: "✦";
  color: var(--champagne);
  font-size: 18px;
}
"""

def f_time(frame_idx: int) -> str:
    return f"{frame_idx / 30.0:.6f}"

def bullion_text(id_prefix: str, text: str, size_cls: str = "wh-disp-lg", metal_cls: str = "wh-gold-metal") -> str:
    esc = html.escape(text)
    return (
        f'<span class="wh-bullion-wrap {size_cls}">'
        f'<span id="{id_prefix}-sheen" class="wh-bullion-face {metal_cls}">{esc}</span>'
        f'</span>'
    )

def lux_header(id_prefix: str, eyebrow: str, title: str, size_cls: str = "wh-disp-lg") -> str:
    esc_eb = html.escape(eyebrow)
    return f"""
      <div id="{id_prefix}-hdr" class="wh-header">
        <div class="wh-eyebrow">
          <span class="wh-eyebrow-star" data-layout-ignore>✦</span>
          <span class="wh-eyebrow-txt">{esc_eb}</span>
          <span class="wh-eyebrow-star" data-layout-ignore>✦</span>
        </div>
        {bullion_text(f"{id_prefix}-ttl", title, size_cls)}
        <div id="{id_prefix}-flare" class="wh-anamorphic-flare" data-layout-ignore></div>
      </div>"""

def write_comp(filename: str, content: str):
    p = os.path.join(COMP_DIR, filename)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote composition: {filename}")
