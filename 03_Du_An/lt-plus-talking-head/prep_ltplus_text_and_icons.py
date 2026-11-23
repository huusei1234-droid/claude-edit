import json, os, pathlib, shutil, sys, time
from PIL import Image, ImageDraw, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

PROJ = pathlib.Path(r"d:\AI\full studio\output\lt-plus-talking-head")
AROLL = PROJ / "aroll"
MEDIA = PROJ / "media"
Z_ANH = pathlib.Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\Ảnh")

# ==============================================================================
# 1. FIX 100% VIETNAMESE MEDICAL SPELLING IN main_cut.json
# ==============================================================================
jp = AROLL / "main_cut.json"
d = json.loads(jp.read_text(encoding="utf-8"))

# Exact per-segment word replacements (verified word-by-word against S00..S26)
WORD_FIXES = {
    (0, 1): "hư",
    (0, 6): "máu",
    (0, 28): "dựa",
    (0, 40): "nhân.",
    (1, 6): "triệu",
    (1, 14): "tiết",
    (1, 15): "dịch,",
    (1, 17): "máu",
    (1, 26): "dấu",
    (1, 42): "tra.",
    (2, 0): "Ngứa,",
    (4, 3): "dấu",
    (4, 8): "lộ",
    (4, 9): "tuyến.",
    (5, 1): "tự",
    (6, 0): "rồi",
    (6, 1): "dùng",
    (6, 2): "viên",
    (6, 7): "miệng.",
    (7, 5): "khám",
    (7, 6): "phụ",
    (7, 7): "khoa,",
    (8, 3): "triệu",
    (8, 4): "chứng,",
    (9, 6): "hướng",
    (9, 7): "dẫn",
    (9, 10): "sĩ.",
    (10, 5): "loại",
    (10, 6): "viên",
    (11, 4): "viêm",
    (11, 5): "lộ",
    (11, 6): "tuyến,",
    (13, 0): "viên",
    (13, 6): "Hằng",
    (13, 7): "Thu.",
    (15, 0): "Hoàng",
    (15, 1): "bá,",
    (15, 2): "Ích",
    (15, 3): "mẫu,",
    (15, 4): "Kim",
    (15, 5): "ngân",
    (15, 6): "hoa,",
    (16, 0): "Trà",
    (16, 2): "Trầu",
    (16, 3): "không",
    (17, 1): "Acid",
    (17, 2): "Lactic.",
    (18, 6): "lần.",
    (19, 6): "viên,",
    (21, 2): "ngày,",
    (23, 7): "phẩm.",
    (24, 0): "Nhắn",
    (25, 3): "rõ",
    (26, 2): "mua.",
}

for (si, wi), new_w in WORD_FIXES.items():
    if si < len(d["segments"]) and wi < len(d["segments"][si]["words"]):
        d["segments"][si]["words"][wi]["word"] = new_w

# Merge S13 words 3 ("và") + 4 ("lớn") -> "Plus" (44.90 - 45.42s)
s13w = d["segments"][13]["words"]
if len(s13w) >= 7 and s13w[2]["word"] == "LT" and s13w[3]["word"] in ("và", "Plus"):
    if s13w[3]["word"] == "và":
        s13w[3]["word"] = "Plus"
        s13w[3]["end"] = s13w[4]["end"]
        del s13w[4]

for s in d["segments"]:
    s["text"] = " ".join(w["word"] for w in s["words"])

(AROLL / "main_cut_clean.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
lines_txt = [f"[{si:02d} | {s['start']:5.2f}-{s['end']:5.2f}] {s['text']}" for si, s in enumerate(d["segments"])]
(AROLL / "main_cut_clean.txt").write_text("\n".join(lines_txt), encoding="utf-8")
print("Saved cleaned transcript:")
for ln in lines_txt:
    print(" ", ln)

# ==============================================================================
# 2. PREPARE REAL LT PLUS PRODUCT CARDS & STUDIO PHOTOS FROM Z:\...\Ảnh
# ==============================================================================
def make_product_square_card(src_path, out_path, pad_ratio=0.10):
    S = 600
    yy_idx = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # Soft luxury blush-pearl gradient background
    bg = Image.new("RGBA", (S, S), (253, 243, 247, 255))
    dr = ImageDraw.Draw(bg)
    for r in range(300, 20, -8):
        t = 1.0 - r / 300.0
        col = (int(250 + 5 * t), int(232 + 20 * t), int(240 + 14 * t), 255)
        dr.ellipse([300 - r, 300 - r, 300 + r, 300 + r], fill=col)

    im = Image.open(src_path).convert("RGBA")
    target = int(S * (1.0 - 2 * pad_ratio))
    im.thumbnail((target, target), Image.Resampling.LANCZOS)
    px = (S - im.width) // 2
    py = (S - im.height) // 2

    # Soft studio drop shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if im.mode == "RGBA":
        alpha = im.split()[3]
        # Check if image is rectangular opaque JPG/PNG or transparent cutout
        extrema = alpha.getextrema()
        if extrema[0] < 200:
            sh_mask = alpha.filter(ImageFilter.GaussianBlur(radius=14))
            sh_col = Image.new("RGBA", im.size, (90, 35, 55, 95))
            sh.paste(sh_col, (px + 6, py + 14), mask=sh_mask)
            bg = Image.alpha_composite(bg, sh)
            bg.paste(im, (px, py), mask=alpha)
        else:
            # Clean rounded-rect crop of white-bg product shot
            rm = Image.new("L", im.size, 0)
            ImageDraw.Draw(rm).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=36, fill=255)
            bg.paste(im, (px, py), mask=rm)
    bg.save(out_path)

make_product_square_card(Z_ANH / "4.png", MEDIA / "pack_box_clean.png", pad_ratio=0.06)
make_product_square_card(Z_ANH / "2.png", MEDIA / "pack_bottle_clean.png", pad_ratio=0.07)
make_product_square_card(Z_ANH / "6.png", MEDIA / "pack_open_clean.png", pad_ratio=0.05)

for dsc in ["DSC00268.JPG", "DSC00274.JPG", "DSC00275.JPG"]:
    shutil.copy2(Z_ANH / dsc, MEDIA / dsc)
print("Prepared real LT PLUS product square cards & studio photos in media/!")

# ==============================================================================
# 3. GENERATE 5 CLEAN 3D MEDICAL GYNECOLOGY ICONS ON INFINITY STUDIO CANVAS
# ==============================================================================
ICON_BATCH = [
    {
        "key": "hook_01",
        "title": "LT-ic-hook1",
        "x": 3800, "y": 0,
        "prompt": "Premium 3D women wellness pharmacist icon card, square 1:1 composition, soft blush-pink and mint-pearl glassmorphism badge featuring a luminous crystal-clear pure water droplet beside a delicate pearl lotus protective shield with subtle champagne-gold sparkles, bright clean studio lighting, no people, no anatomy, no blood, no text, no letters, no numbers, no watermark"
    },
    {
        "key": "hook_02",
        "title": "LT-ic-hook2",
        "x": 3800, "y": 480,
        "prompt": "Premium 3D medical pharmacist icon card, square 1:1 composition, soft blush-rose and mint-emerald glassmorphism badge featuring a sleek white-and-gold medical magnifying glass examining a glossy 3D rose-pearl question mark emblem, bright clean studio lighting, no people, no text, no letters, no numbers, no watermark"
    },
    {
        "key": "ic_clinic",
        "title": "LT-ic-clinic",
        "x": 3800, "y": 960,
        "prompt": "Premium 3D medical gynecology checkup icon badge, square 1:1 composition, soft cream-pink and mint glassmorphism card featuring a modern clean white optical microscope next to a glossy pastel-mint medical diagnostic clipboard with a golden checkmark icon and white stethoscope, bright studio lighting, no people, no text, no letters, no numbers, no watermark"
    },
    {
        "key": "ic_herbs",
        "title": "LT-ic-herbs",
        "x": 3800, "y": 1440,
        "prompt": "Premium 3D natural herbal pharmacist icon badge, square 1:1 composition, soft blush-cream and emerald-mint glassmorphism card featuring a pearl ceramic mortar holding fresh green tea leaves, betel leaves, golden honeysuckle blossoms and herbal bark with glowing golden botanical essence droplets, clean studio lighting, no people, no text, no letters, no watermark"
    },
    {
        "key": "ic_ph",
        "title": "LT-ic-ph",
        "x": 3800, "y": 1920,
        "prompt": "Premium 3D feminine care balance icon badge, square 1:1 composition, soft rose-pink and aqua-mint glassmorphism card featuring a glowing translucent rose-aqua hydration dewdrop harmonized with a luminous pearl balance emblem and soft golden sparkles, clean studio lighting, no people, no text, no letters, no numbers, no watermark"
    },
]

for item in ICON_BATCH:
    res = cv.call("canvas_generate_image", {
        "prompt": item["prompt"],
        "model": "flow::flow-nano-banana-pro",
        "size": "1:1",
        "count": 1,
        "title": item["title"],
        "x": item["x"],
        "y": item["y"],
    })
    print("Submitted image", item["title"], "-> ok:", res.get("ok"))
    time.sleep(3)

titles = [x["title"] for x in ICON_BATCH]
for step in range(36):
    time.sleep(8)
    st_res = cv.call("canvas_get_state", {})["result"]
    nodes = {n["id"]: n for n in st_res["nodes"]}
    conns = st_res["connections"]
    status_map = {}
    for t in titles:
        cfgs = [n for n in nodes.values() if n["type"] == "config" and (n.get("title") or "").startswith(t)]
        if not cfgs:
            status_map[t] = "no_cfg"
            continue
        cid = cfgs[-1]["id"]
        outs = [nodes[c["toNodeId"]] for c in conns if c["fromNodeId"] == cid and nodes[c["toNodeId"]]["type"] == "image"]
        if not outs:
            status_map[t] = cfgs[-1].get("metadata", {}).get("status", "pending")
        else:
            m = outs[-1].get("metadata") or {}
            status_map[t] = f"{m.get('status')}|err={str(m.get('error') or '')[:60]}"
    print(f"[Icons {step*8}s]", status_map, flush=True)
    if all(v.startswith("success") or v.startswith("error") for v in status_map.values()):
        print("All 5 icon badges finished!")
        break
