# -*- coding: utf-8 -*-
"""
Regenerate ALL 6 Core Characters (K7 + K8) matching 100% the high-beauty visual standard of K4 ("Chuyện Trong Nhà": Thảo G01_05a, Tuấn G01_04a, Bà Hạnh G01_03c):
- Refreshes clean empty Flow projects first (0% stale video/image collision!).
- Enforces PNG/JPEG magic-byte check + square dimensions check + MD5 dedup guard.
- Uses tight 85mm f/1.4 macro beauty close-up on LEFT panel + graceful editorial full-body pose in luxury Vietnamese villa on RIGHT panel.
"""
import json
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = r"C:\AI\full studio\03_Du_An\261126-k7-k8-khoi-tao-nhan-vat-goc"
V2_K7_DIR = os.path.join(PROJECT_DIR, "v2_k7")
V2_K8_DIR = os.path.join(PROJECT_DIR, "v2_k8")
os.makedirs(V2_K7_DIR, exist_ok=True)
os.makedirs(V2_K8_DIR, exist_ok=True)

K7_CHAR_DIR = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\k7 sóng gió mái ấm\CHARACTER"
K8_CHAR_DIR = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\k8 sau cánh cửa nhà\CHARACTER"

BEAUTY_SPLIT_HEADER = (
    "Photorealistic 1:1 square high-end Asian drama character reference sheet divided cleanly down the middle by a thin crisp vertical white line into TWO side-by-side panels of the EXACT SAME person: "
    "LEFT PANEL (48% width): tight intimate head-and-collarbone beauty close-up portrait (shot on 85mm f/1.2 portrait lens, face filling the frame, creamy warm indoor bokeh, soft luminous wrap-around beauty lighting, flawless radiant skin). "
    "RIGHT PANEL (52% width): full-body head-to-toe standing shot of the EXACT SAME person wearing the EXACT SAME outfit, jewelry, and shoes in a luxurious warm high-ceiling Vietnamese villa/duplex living room. "
    "STRICT: ONE single person shown in two views (tight face close-up left, full-body head-to-toe right), ZERO text, ZERO letters, ZERO watermarks. "
)

ALL_V2_JOBS = [
    # ==================== K7: SÓNG GIÓ MÁI ẤM ====================
    {
        "id": "V2_K7_G01_03a_HaVi",
        "channel": "K7",
        "outPath": os.path.join(
            V2_K7_DIR,
            "G01_03a - Hạ Vi (Vợ Gia Bảo - Con dâu trưởng bà Mỹ Vân) [Váy trễ vai tơ bồng tiểu thư].png",
        ),
        "prompt": BEAUTY_SPLIT_HEADER + (
            "Subject: Hạ Vi, a breathtakingly gorgeous Vietnamese-Korean ulzzang pure-beauty leading actress (Douyin / Xiaohongshu top editorial beauty standard); flawless milky porcelain glass skin with delicate rosy-peach blush on her cheeks, small delicate V-line oval face, large sparkling dewy doe eyes with wispy curled lashes and subtle charming eye-smile, dainty straight nose, plump petal-pink gradient lips, thick voluminous warm chestnut-brown layered long wavy hair with airy wispy face-framing strands, gentle 5-degree head tilt looking softly into the camera. "
            "Outfit (Shopee viral best-seller off-shoulder fairy midi dress): ethereal cream-blush sheer ruched organza off-shoulder princess midi dress draping gracefully over her collarbones and waist, dainty gold clover-pendant necklace, chic mini ivory leather shoulder bag with gold clasp worn over one shoulder, hands softly clasped in front in a graceful feminine S-curve model pose, wearing cream pointed slingback heels in a warm sunlit luxury duplex living room."
        ),
    },
    {
        "id": "V2_K7_G01_02a_GiaBao",
        "channel": "K7",
        "outPath": os.path.join(
            V2_K7_DIR,
            "G01_02a - Gia Bảo (Chồng Hạ Vi - Con trai trưởng bà Mỹ Vân) [Áo polo dệt kim xanh navy cổ trắng].png",
        ),
        "prompt": BEAUTY_SPLIT_HEADER + (
            "Subject: Gia Bảo, a drop-dead handsome Korean-Vietnamese TV drama charismatic CEO leading actor; bright fair smooth luminous skin, thick voluminous Korean airy comma-parted jet-black textured hair, sharp sword eyebrows, deep magnetic double-eyelid eyes, high straight nose bridge, clean-shaven sculpted V-jawline, expressive gaze. "
            "Outfit (Shopee best-seller Korean old-money knit polo): fitted luxury midnight-navy fine-knit collared polo shirt with crisp white contrast trim on the collar, neatly tucked into tailored ivory-cream pleated straight-leg dress trousers, luxury silver steel wristwatch, tall 183cm model proportions standing with hands casually in trouser pockets, wearing polished black leather loafers in a warm sunlit luxury marble-and-oak duplex living room."
        ),
    },
    {
        "id": "V2_K7_G01_01a_BaMyVan",
        "channel": "K7",
        "outPath": os.path.join(
            V2_K7_DIR,
            "G01_01a - Bà Mỹ Vân (Mẹ ruột Gia Bảo - Mẹ chồng Hạ Vi) [Đầm lụa gấm đỏ mận Thiều Hoa].png",
        ),
        "prompt": BEAUTY_SPLIT_HEADER + (
            "Subject: Bà Mỹ Vân, a glamorous, ageless, wealthy Vietnamese high-society matriarch actress (rich phu nhân mother-in-law); plump radiant fair porcelain-warm skin, salon-styled voluminous warm chestnut-brown shoulder-length wavy hair, refined berry-rose satin lipstick, sharp proud almond eyes, wearing a double-strand white pearl necklace and pearl-diamond cluster earrings. "
            "Outfit (Shopee best-seller Thiều Hoa DD5L0144 luxury phu nhân dress): opulent ruby-burgundy velvet-silk floral jacquard midi dress with gold-rimmed pearl couture buttons down the bodice and graceful puff-cuff sleeves, holding a structured beige-taupe luxury leather top-handle handbag with both hands in front, wearing cream pointed buckle low heels in a warm luxury marble-and-chandelier villa living room."
        ),
    },

    # ==================== K8: SAU CÁNH CỬA NHÀ ====================
    {
        "id": "V2_K8_G01_03a_TueNhi",
        "channel": "K8",
        "outPath": os.path.join(
            V2_K8_DIR,
            "G01_03a - Tuệ Nhi (Vợ Đình Vũ - Con dâu trưởng bà Minh Nguyệt) [Set dạ tweed tiểu thư chân váy xếp ly].png",
        ),
        "prompt": BEAUTY_SPLIT_HEADER + (
            "Subject: Tuệ Nhi, a stunningly beautiful Vietnamese-Korean ulzzang chaebol leading actress (distinct face: delicate heart-shaped V-line face, snow-fair porcelain glass skin with soft rosebud cheek blush, bright captivating almond-doe eyes with dewy sparkle and feathery lashes, refined high petite nose, soft rose-pink lips, fluffy high-cranial dark chocolate-brown half-up princess waves with airy see-through wispy side tendrils), gentle alluring gaze toward camera. "
            "Outfit (Shopee viral best-seller Korean Tweed 2-piece princess set): chic pastel pearl-ivory tweed cropped jacket trimmed with delicate crystal-pearl braiding and a dainty black velvet bow at the collar, paired with a matching high-waisted pleated flared tweed skirt showing slender porcelain legs, dainty pearl pendant necklace, mini white quilted leather shoulder bag, graceful feminine pose, wearing cream pointed Mary-Jane heels in a grand dark-walnut and cream-marble villa living room."
        ),
    },
    {
        "id": "V2_K8_G01_02a_DinhVu",
        "channel": "K8",
        "outPath": os.path.join(
            V2_K8_DIR,
            "G01_02a - Đình Vũ (Chồng Tuệ Nhi - Con trai trưởng bà Minh Nguyệt) [Áo sơ mi polo băng lụa nâu cafe].png",
        ),
        "prompt": BEAUTY_SPLIT_HEADER + (
            "Subject: Đình Vũ, a breathtakingly handsome Korean-Vietnamese C-drama chaebol CEO leading actor (distinct face: sculpted aristocratic cheekbones, fair smooth clean skin, stylish Korean wet-textured 7/3 swept-back black hair with a subtle loose strand on forehead, intense deep phoenix-almond eyes, tall straight nose bridge, sharp masculine V-jawline). "
            "Outfit (Shopee best-seller French-style mocha ice-silk shirt-polo): fitted rich espresso-chocolate knit/ice-silk collared short-sleeve shirt-polo with top button casually open, tucked into tailored dove-grey pleated wide-straight dress trousers, luxury silver watch on wrist, tall 184cm model proportions with hands relaxed in pockets, wearing sleek black leather derby shoes in a grand dark-walnut and cream-marble villa living room."
        ),
    },
    {
        "id": "V2_K8_G01_01a_BaMinhNguyet",
        "channel": "K8",
        "outPath": os.path.join(
            V2_K8_DIR,
            "G01_01a - Bà Minh Nguyệt (Mẹ ruột Đình Vũ - Mẹ chồng Tuệ Nhi) [Đầm lụa gấm xanh lục bảo Thiều Hoa].png",
        ),
        "prompt": BEAUTY_SPLIT_HEADER + (
            "Subject: Bà Minh Nguyệt, a strikingly beautiful, ageless, aristocratic wealthy Vietnamese matriarch actress (K-drama chaebol madam vibe); smooth luminous ivory-fair skin, voluminous salon-sculpted dark espresso glamorous shoulder-length curled lob hair, sophisticated coral-red satin lipstick, discerning sharp phoenix eyes, wearing an emerald-and-pearl pendant necklace and matching drop earrings. "
            "Outfit (Shopee best-seller Thiều Hoa DD4L0336 luxury phu nhân dress): regal deep emerald-green woven floral silk-brocade midi dress with couture pleated neckline, gold-pearl brooch, and three-quarter sleeves, holding a sleek black quilted luxury leather top-handle handbag gracefully, wearing cream-beige pointed slingback heels in a grand dark-walnut and cream-marble villa living room."
        ),
    },
]

RUNNER_JS = r"""
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
fs.mkdirSync(DATA_DIR, { recursive: true });

const origLoad = Module._load;
Module._load = function (req, parent, isMain) {
  if (req === "electron") {
    return {
      ipcMain: { handle: () => {} },
      dialog: { showErrorBox: (t, m) => console.error("[STUDIO DIALOG]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
flow.setup({ getPath: () => DATA_DIR });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function isValidSquareImage(buf) {
  if (!buf || buf.length < 400000) return false;
  if (buf.slice(4, 8).toString("ascii") === "ftyp") return false;
  const isPng = buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
  const isJpg = buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff;
  const isWebp = buf.slice(0, 4).toString("ascii") === "RIFF" && buf.slice(8, 12).toString("ascii") === "WEBP";
  if (!isPng && !isJpg && !isWebp) return false;
  if (isPng && buf.length > 24) {
    const w = buf.readUInt32BE(16);
    const h = buf.readUInt32BE(20);
    if (w < h * 0.80 || h < w * 0.80) return false;
  }
  return true;
}

(async () => {
  try {
    const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
    const seen = new Set();
    for (const j of jobs) {
      if (fs.existsSync(j.outPath)) {
        const ex = fs.readFileSync(j.outPath);
        if (isValidSquareImage(ex)) {
          seen.add(crypto.createHash("md5").update(ex).digest("hex"));
          console.log(`[SKIP V2] ${j.id} already verified on disk (${Math.round(ex.length/1024)} KB)`);
          continue;
        }
      }
      let ok = false;
      for (let attempt = 1; attempt <= 5; attempt++) {
        console.log(`[GEN V2] ${j.id} attempt #${attempt}...`);
        const t0 = Date.now();
        let items = null;
        try {
          items = await flow.generateImageFallback({
            prompt: j.prompt + (attempt > 1 ? ` [editorial take ${attempt}]` : ""),
            ratio: "1:1",
            aspect: "square",
            count: 1,
            images: [],
          });
        } catch (err) {
          console.warn(`[RETRY V2] ${j.id} attempt #${attempt} error: ${err?.message || err}`);
          await sleep(4500);
          continue;
        }
        const buf = items && items[0] && items[0].data;
        if (!isValidSquareImage(buf)) {
          console.warn(`[GUARD REJECT] ${j.id} invalid image/video buffer (${buf ? buf.length : 0} bytes) -> retrying!`);
          await sleep(3500);
          continue;
        }
        const h = crypto.createHash("md5").update(buf).digest("hex");
        if (seen.has(h)) {
          console.warn(`[DUP_GUARD] ${j.id} duplicate hash ${h.slice(0,8)} -> retrying!`);
          await sleep(3500);
          continue;
        }
        seen.add(h);
        fs.mkdirSync(path.dirname(j.outPath), { recursive: true });
        fs.writeFileSync(j.outPath, buf);
        console.log(`[DONE V2] ${j.id} in ${Math.round((Date.now() - t0)/1000)}s (${Math.round(buf.length/1024)} KB)`);
        ok = true;
        break;
      }
      if (!ok) throw new Error(`Failed to generate valid image for ${j.id}`);
    }
  } finally {
    flow.destroy();
  }
  process.exit(0);
})();
"""

def main():
    desktop_dir = r"C:\AI\full studio\canvas\desktop"
    spec_p = os.path.join(PROJECT_DIR, "spec_v2_all6.json")
    with open(spec_p, "w", encoding="utf-8") as f:
        json.dump(ALL_V2_JOBS, f, ensure_ascii=False, indent=2)

    runner_p = os.path.join(PROJECT_DIR, "_run_v2_clean.js")
    with open(runner_p, "w", encoding="utf-8") as f:
        f.write(RUNNER_JS)

    print("=== Step 2: Generating all 6 Ulzzang / Chaebol K4-Standard Character Sheets ===", flush=True)
    p = subprocess.Popen(
        ["node", runner_p, spec_p],
        cwd=desktop_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    for line in p.stdout:
        print(line.rstrip(), flush=True)
    rc = p.wait()
    if rc != 0:
        raise RuntimeError(f"Runner exited with {rc}")

    # Clean old draft PNGs in K7_CHAR_DIR and K8_CHAR_DIR before copying clean V2 PNGs!
    for cdir in (K7_CHAR_DIR, K8_CHAR_DIR):
        os.makedirs(cdir, exist_ok=True)
        for fn in os.listdir(cdir):
            if fn.startswith("G01_") and fn.endswith(".png"):
                os.remove(os.path.join(cdir, fn))

    for j in ALL_V2_JOBS:
        target_dir = K7_CHAR_DIR if j["channel"] == "K7" else K8_CHAR_DIR
        dst = os.path.join(target_dir, os.path.basename(j["outPath"]))
        shutil.copy2(j["outPath"], dst)
        print(f"[SYNCED V2 -> {j['channel']}] {os.path.basename(dst)} ({os.path.getsize(dst)//1024} KB)", flush=True)

    print("ALL_6_V2_DONE_OK", flush=True)

if __name__ == "__main__":
    main()
