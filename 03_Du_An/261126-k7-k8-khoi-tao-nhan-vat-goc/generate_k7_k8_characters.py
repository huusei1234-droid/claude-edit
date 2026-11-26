# -*- coding: utf-8 -*-
import json
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = r"C:\AI\full studio\03_Du_An\261126-k7-k8-khoi-tao-nhan-vat-goc"
RAW_K7_DIR = os.path.join(PROJECT_DIR, "raw_k7")
RAW_K8_DIR = os.path.join(PROJECT_DIR, "raw_k8")
os.makedirs(RAW_K7_DIR, exist_ok=True)
os.makedirs(RAW_K8_DIR, exist_ok=True)

DESKTOP_DIR = r"C:\AI\full studio\canvas\desktop"
DRIVER_JS = r"C:\AI\full studio\output\k4-20-reels-261126\direct_studio_driver.js"

K7_CHAR_DIR = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\k7 sóng gió mái ấm\CHARACTER"
K8_CHAR_DIR = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\k8 sau cánh cửa nhà\CHARACTER"

SHEET_PREFIX = (
    "Photorealistic 1:1 square Vietnamese prime-time TV family drama character reference sheet divided cleanly by a thin vertical white line into TWO side-by-side panels of the EXACT SAME attractive real Vietnamese person: "
    "LEFT PANEL (45% width): close-up chest-up portrait looking naturally toward camera, soft cinema daylight, realistic natural Vietnamese skin texture, expressive eyes, natural refined look. "
    "RIGHT PANEL (55% width): full-body head-to-toe standing photo of the EXACT SAME person wearing the EXACT SAME outfit and shoes from head to toe. "
    "STRICT: ONE single person shown in two views (close-up left, full-body right), ZERO text, ZERO labels, ZERO letters, ZERO watermarks, ZERO CGI/3D plastic look. "
)

K7_JOBS = [
    {
        "id": "K7_G01_01a_BaMyVan",
        "ratio": "1:1",
        "overwrite": True,
        "outPath": os.path.join(
            RAW_K7_DIR,
            "G01_01a - Bà Mỹ Vân (Mẹ ruột Gia Bảo - Mẹ chồng Hạ Vi) [Đầm lụa gấm đỏ mận Thiều Hoa].png",
        ),
        "refs": [],
        "prompt": SHEET_PREFIX + (
            "Subject: Bà Mỹ Vân, a glamorous, sharp-featured 54-year-old urban affluent Vietnamese mother-in-law; radiant well-kept fair warm complexion, sculpted oval-heart face, straight refined nose bridge, piercing observant almond eyes with proud authoritative demeanor, glossy jet-black hair styled in a poised voluminous low bun pinned with a subtle pearl hairpin, small pearl drop earrings. "
            "Outfit (Shopee best-seller Thiều Hoa DD5L0144): luxurious plum-burgundy woven floral silk-brocade midi dress (đầm lụa gấm hoa trung niên sang trọng màu đỏ mận) with a tailored modest V-round neckline accented by delicate pearl buttons, elbow-length slightly puffed sleeves, flattering A-line skirt below the knees, and classic black low-block pointed heels. "
            "Setting in both panels: sunlit modern cream-and-honey-oak Vietnamese townhouse living room."
        ),
    },
    {
        "id": "K7_G01_02a_GiaBao",
        "ratio": "1:1",
        "overwrite": True,
        "outPath": os.path.join(
            RAW_K7_DIR,
            "G01_02a - Gia Bảo (Chồng Hạ Vi - Con trai trưởng bà Mỹ Vân) [Áo polo dệt kim xanh navy cổ trắng].png",
        ),
        "refs": [],
        "prompt": SHEET_PREFIX + (
            "Subject: Gia Bảo, a very handsome, charismatic 30-year-old Vietnamese husband and young manager; clean-cut 7/3 side-parted jet-black hair, straight high nose bridge, warm sincere almond eyes, clean-shaven defined masculine jawline, composed principled expression, NO glasses. "
            "Outfit (Shopee best-seller men's knitted contrast polo): refined dark navy-blue fine-knit short-sleeve collared polo shirt featuring crisp white contrast trim along the collar and placket, neatly tucked into tailored charcoal-grey dress trousers with a matte black leather belt, silver-case black-leather wristwatch, and polished black leather loafers. "
            "Setting in both panels: sunlit modern cream-and-honey-oak Vietnamese townhouse living room."
        ),
    },
    {
        "id": "K7_G01_03a_HaVi",
        "ratio": "1:1",
        "overwrite": True,
        "outPath": os.path.join(
            RAW_K7_DIR,
            "G01_03a - Hạ Vi (Vợ Gia Bảo - Con dâu trưởng bà Mỹ Vân) [Set váy tiểu thư trắng kem VT2480].png",
        ),
        "refs": [],
        "prompt": SHEET_PREFIX + (
            "Subject: Hạ Vi, a naturally beautiful, graceful 27-year-old Vietnamese young wife and virtuous daughter-in-law; delicate oval face, luminous fair natural skin, gentle expressive doe eyes, soft natural coral-pink lips, long silky dark hair in soft natural waves tucked behind one ear. "
            "Outfit (Shopee best-seller VT2480 lady office 2-piece set): elegant cream-white tailored short-sleeve waist-cinched blouse with a modest refined collar/sweetheart neckline paired with a matching cream-white high-waisted flowing A-line midi skirt past the knees, dainty thin gold necklace, and cream pointed flat slingback shoes. "
            "Setting in both panels: sunlit modern cream-and-honey-oak Vietnamese townhouse living room."
        ),
    },
]

K8_JOBS = [
    {
        "id": "K8_G01_01a_BaMinhNguyet",
        "ratio": "1:1",
        "overwrite": True,
        "outPath": os.path.join(
            RAW_K8_DIR,
            "G01_01a - Bà Minh Nguyệt (Mẹ ruột Đình Vũ - Mẹ chồng Tuệ Nhi) [Đầm lụa gấm xanh lục bảo Thiều Hoa].png",
        ),
        "refs": [],
        "prompt": SHEET_PREFIX + (
            "Subject: Bà Minh Nguyệt, a dignified, aristocratic, strict 56-year-old Vietnamese mother-in-law; sculpted cheekbones, straight nose, sharp observant phoenix eyes with a composed perfectionist family-matriarch expression, shoulder-length glossy black hair neatly curled inward at the ends, subtle jade-and-gold stud earrings, NO glasses. "
            "Outfit (Shopee best-seller Thiều Hoa DD4L0336): sophisticated deep emerald-green woven silk-brocade midi dress (đầm lụa gấm cao cấp màu xanh lục bảo) with subtle tone-on-tone jacquard floral sheen, modest pleated round neckline with a small gold-pearl brooch accent, three-quarter sleeves, A-line midi silhouette, and black leather low-heel pumps. "
            "Setting in both panels: refined Vietnamese family villa living room with dark walnut wood accents and warm natural daylight."
        ),
    },
    {
        "id": "K8_G01_02a_DinhVu",
        "ratio": "1:1",
        "overwrite": True,
        "outPath": os.path.join(
            RAW_K8_DIR,
            "G01_02a - Đình Vũ (Chồng Tuệ Nhi - Con trai trưởng bà Minh Nguyệt) [Áo sơ mi polo băng lụa nâu cafe].png",
        ),
        "refs": [],
        "prompt": SHEET_PREFIX + (
            "Subject: Đình Vũ, a strikingly handsome, mature, composed 31-year-old Vietnamese businessman and devoted husband; short neatly swept-back black hair revealing a clean forehead, sculpted cheekbones, straight nose bridge, deep calm expressive eyes, clean-shaven strong jawline, NO glasses. "
            "Outfit (Shopee best-seller French-style ice-silk shirt-polo): sleek espresso-mocha brown smooth ice-silk short-sleeve collared button-up polo shirt neatly tucked into tailored jet-black dress slacks with a brushed-silver buckle leather belt, minimalist metal watch, and dark-brown leather Oxford shoes. "
            "Setting in both panels: refined Vietnamese family villa living room with dark walnut wood accents and warm natural daylight."
        ),
    },
    {
        "id": "K8_G01_03a_TueNhi",
        "ratio": "1:1",
        "overwrite": True,
        "outPath": os.path.join(
            RAW_K8_DIR,
            "G01_03a - Tuệ Nhi (Vợ Đình Vũ - Con dâu trưởng bà Minh Nguyệt) [Set áo cổ nơ xanh pastel chân váy chữ A].png",
        ),
        "refs": [],
        "prompt": SHEET_PREFIX + (
            "Subject: Tuệ Nhi, a breathtakingly pretty, intelligent, poised 27-year-old Vietnamese young wife; delicate symmetrical features, clear ivory-warm natural skin, soulful warm dark eyes conveying quiet resilience and kindness, glossy jet-black hair styled in a graceful half-up half-down hairdo with soft wispy side tendrils. "
            "Outfit (Shopee best-seller Korean office chic A-line 2-piece set): soft pastel sage-celadon blouse with a delicate ribbon-bow collar and gentle short puff sleeves tucked neatly into a sleek black high-waisted A-line midi skirt below the knee, small pearl stud earrings, slim brown-strap wristwatch, and nude low-heel pumps. "
            "Setting in both panels: refined Vietnamese family villa living room with dark walnut wood accents and warm natural daylight."
        ),
    },
]


def run_batch(tag, jobs, target_drive_dir):
    spec_path = os.path.join(PROJECT_DIR, f"spec_{tag}.json")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    env = os.environ.copy()
    env["GPT_MAX_CONC"] = "1"
    p = subprocess.Popen(
        ["node", DRIVER_JS, "gen_images", spec_path],
        cwd=DESKTOP_DIR,
        env=env,
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
        raise RuntimeError(f"Batch {tag} exited with code {rc}")

    os.makedirs(target_drive_dir, exist_ok=True)
    for j in jobs:
        assert os.path.exists(j["outPath"]) and os.path.getsize(j["outPath"]) > 400000, f"Missing output: {j['outPath']}"
        dst = os.path.join(target_drive_dir, os.path.basename(j["outPath"]))
        shutil.copy2(j["outPath"], dst)
        print(f"[SYNCED TO DRIVE] {dst} ({os.path.getsize(dst)//1024} KB)", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("k7", "all"):
        run_batch("k7", K7_JOBS, K7_CHAR_DIR)
    if mode in ("k8", "all"):
        run_batch("k8", K8_JOBS, K8_CHAR_DIR)
