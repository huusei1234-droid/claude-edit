# -*- coding: utf-8 -*-
"""
Builds 26 ultra-clear single-file composite reference boards (1920x1200) + 26 bespoke ChatGPT Masterpiece prompts:
- Left panel: Chị Hằng's AV PROTEIN approved reference poster (layout clarity, giant text, huge illustrations, stone podium, cute vector icons)
- Right-top HUGE panel (1100x860): Ultra-sharp studio product packshot (+ upright stick sachet for An Vượng) so ChatGPT preserves 100% of packaging text ungarbled!
- Right-bottom panel: Official Brand Logo (An Vượng Pharma or Hằng Thu Pharma)
"""
import json, os, shutil, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

V3_DIR = r"d:\AI\full studio\projects\av_htpm_26_posters_v3"
sys.path.insert(0, V3_DIR)
from step3_product_catalog_26_designs import POSTERS_26

CUT_DIR = os.path.join(V3_DIR, "assets", "cutouts")
V4_DIR = os.path.join(V3_DIR, "v4_chatgpt_masterpieces")
REF_DIR = os.path.join(V4_DIR, "ref_boards")
RAW_OUT_DIR = os.path.join(V4_DIR, "raw_pngs")
os.makedirs(REF_DIR, exist_ok=True)
os.makedirs(RAW_OUT_DIR, exist_ok=True)

STYLE_REF_PATH = r"C:\Users\Hang thu\.gemini\antigravity\brain\3c47ebbb-8468-44f7-b584-19bc2acdc8cf\.user_uploaded\media_1795404719183_a2e19ad8.jpg"

# Copy already-verified 100/100 HT01_TK1 benchmark output into RAW_OUT_DIR so we don't regenerate it!
bench_ht01 = os.path.join(V3_DIR, "benchmark_3ai", "FINAL_01_ChatGPT_FullRes.png")
if os.path.exists(bench_ht01):
    shutil.copy2(bench_ht01, os.path.join(RAW_OUT_DIR, "HT01_TK1.png"))

# Bespoke Scenic World + Natural Side Decor + Custom Footer Line Icons per Product!
PRODUCT_SCENE_DNA = {
    "AV01": {
        "scene_a": "lush sunlit royal emerald-green botanical garden studio with dewy tropical green leaves framing the left, top-left and bottom-left corners, warm golden morning sunbeams, soft bokeh, and 3D flowing metallic champagne-gold silk ribbons",
        "scene_b": "sunlit emerald-jade & warm golden nature studio with lush green foliage, soft golden light rays, floating golden botanical sparkles, and 3D champagne-gold silk ribbons",
        "podium_decor": "a chiseled rustic natural travertine stone slab, surrounded right beside the box and upright sachet by rich natural ingredient decor: golden wheat stalks, fresh open green edamame pea pods, scattered golden soybeans, and a small wooden scoop of fine protein powder",
        "pack_desc": "the white-and-emerald 'AV PROTEIN' box (20 gói x 15g, 300g, showing the glass of soy milk splash on the front) standing next to its upright 'AV PROTEIN 15g' stick sachet",
        "footer_icons": "healthy grain bowl + running athlete + protein shaker bottle",
    },
    "AV02": {
        "scene_a": "sunlit royal emerald-green & warm golden sunlit botanical garden studio with lush green leaves at the corners, warm morning sunbeams, and flowing 3D champagne-gold silk ribbons",
        "scene_b": "warm luminous emerald-teal & golden sunlight wellness studio with lush green botanical leaves, warm bokeh, and 3D champagne-gold ribbons",
        "podium_decor": "a sculpted natural cream limestone & oak slab, surrounded right beside the box and upright sachet by rich natural decor: natural calcified coral-algae pieces, golden oat ears, almonds, a blooming creamy-white vanilla orchid flower, and warm golden grain sparkles",
        "pack_desc": "the white-and-emerald 'BOJOMI' nutritional cereal box (14 gói x 20g, showing the green cup of cereal milk) paired with its upright 'BOJOMI 20g' stick sachet",
        "footer_icons": "calcium bone icon + outdoor sunshine person + warm mug of cereal",
    },
    "AV03": {
        "scene_a": "luminous royal emerald-green & golden-dew botanical spa garden with glossy green camellia leaves, shimmering golden water droplets, soft warm sunbeams, and 3D champagne-gold silk ribbons",
        "scene_b": "sunlit emerald-jade & rose-gold beauty botanical studio with dewy green leaves, blooming white blossoms in soft bokeh, and flowing 3D gold silk ribbons",
        "podium_decor": "a sculpted cream travertine marble slab, surrounded right beside the box and sachet by rich beauty-ingredient decor: fresh dewy sliced golden oranges, glowing golden Collagen serum droplets, white camellia blossoms, and lush green leaves",
        "pack_desc": "the white-and-emerald 'COLLAMELA Collagen Tripeptide' box (showing the golden glowing droplet emblem on the front) paired with its 'COLLAMELA' stick sachet",
        "footer_icons": "glowing skin droplet + shining beauty face + water glass",
    },
    "AV04": {
        "scene_a": "sunlit royal emerald-green & warm amber botanical apothecary garden with lush green turmeric leaves at the corners, golden sunbeams, and flowing 3D champagne-gold silk ribbons",
        "scene_b": "luminous emerald-forest & warm golden-amber wellness studio with lush green leaves, warm golden bokeh, and 3D champagne-gold ribbons",
        "podium_decor": "a chiseled natural warm sandstone slab, surrounded right beside the box and sachet by rich natural decor: vibrant freshly sliced orange turmeric rhizomes, a wooden spoon of golden curcumin powder, blooming white vanilla orchid flower, golden oats, and green leaves",
        "pack_desc": "the white-and-emerald 'ANVUONG CURCUMILK PHYTO' box (14 gói x 15g, showing the glowing golden Phytosome sphere & milk splash) paired with its upright 'CURCUMILK PHYTO' stick sachet",
        "footer_icons": "turmeric root bowl + soothing stomach heart + warm cup of milk",
    },
    "HT01": {
        "scene_a": "lush sunlit royal ruby-crimson & traditional herbal garden studio with blooming pink lotus flowers, dewy green medicinal leaves framing the corners, warm golden sunbeams, and 3D champagne-gold silk ribbons",
        "scene_b": "regal deep crimson-burgundy & sunlit rose-gold silk botanical studio with blooming pink lotus blossoms, soft golden rays, green herbal leaves, and flowing 3D gold ribbons",
        "podium_decor": "a sculpted natural stone slab, surrounded right beside the box and bottle by rich traditional herbal decor: sliced Đương quy roots, vibrant red Hồng hoa saffron blossoms, green medicinal leaves, red jujubes, and dark-brown herbal pills",
        "pack_desc": "the magenta-and-white 'ĐIỀU KINH HT' box and white bottle with dark herbal pills",
        "footer_icons": "herbal mortar bowl + meditating yoga woman + warm water cup",
    },
    "HT02": {
        "scene_a": "sunlit royal ruby-rose & blooming botanical spa garden with soft pink lotus flowers, dewy green tea & betel leaves framing the corners, warm golden sunbeams, and 3D champagne-gold silk ribbons",
        "scene_b": "luminous deep rose-burgundy & pearl-gold botanical wellness studio with blooming white-and-gold honeysuckle flowers, soft pink petals, green leaves, and 3D gold silk ribbons",
        "podium_decor": "a sculpted cream-white marble slab, surrounded right beside the box and bottle by rich natural herbal decor: blooming white-and-gold Kim ngân hoa (honeysuckle) flowers, glossy green Trầu không leaves with water drops, golden Hoàng bá bark slices, and soft pink petals",
        "pack_desc": "the soft-pink 'VIÊN ĐẶT PHỤ KHOA LT PLUS HẰNG THU' box, pink sachet, and small white pill bottle",
        "footer_icons": "herbal flower leaf + bedtime moon clock + protective shield",
    },
    "HT03": {
        "scene_a": "sunlit imperial herbal jade-emerald apothecary garden with lush green medicinal leaves at the corners, warm golden morning sunbeams, soft bokeh, and flowing 3D champagne-gold silk ribbons",
        "scene_b": "luminous forest-jade & warm golden herbal wellness studio with fresh medicinal foliage, warm sunrays, and 3D champagne-gold silk ribbons",
        "podium_decor": "a chiseled natural warm sandstone slab, surrounded right beside the box and bottle by rich herbal decor: fresh purple-green Dạ cẩm leaves, sliced Nghệ đen rhizomes, blooming yellow dandelion flower, dried herbal roots, and a warm ceramic cup of herbal tea",
        "pack_desc": "the green-and-white 'DẠ DÀY HT' box (showing the stomach illustration and Dạ Cẩm label) and white bottle of herbal pills",
        "footer_icons": "herbal mortar bowl + balanced meal plate + warm water cup",
    },
    "HT04": {
        "scene_a": "luxurious sunlit royal ruby-crimson & velvety Damask rose garden studio with blooming red roses, dewy green leaves at the corners, warm golden bokeh, and 3D champagne-gold silk ribbons",
        "scene_b": "sensual deep burgundy-rose & champagne-gold silk spa studio with blooming velvety red roses, crystal water droplets, green leaves, and flowing 3D gold ribbons",
        "podium_decor": "a sculpted white Carrara marble slab, surrounded right beside the box and bottle by rich botanical decor: velvety blooming red Damask roses with crystal dew drops, fresh green tea leaves, translucent green aloe vera slices, and soft rose petals",
        "pack_desc": "the white 'Romance' feminine wash box (showing the red rose artwork) and sleek bottle",
        "footer_icons": "rose water droplet + sparkling feather + 24h freshness clock",
    },
    "HT05": {
        "scene_a": "lush sunlit imperial emerald-jade royal herbal garden with blooming white-pink Crinum lilies (Trinh nữ hoàng cung), dewy green leaves framing the corners, warm golden sunbeams, and 3D champagne-gold silk ribbons",
        "scene_b": "regal deep jade-green & warm golden palace botanical studio with blooming white herbal blossoms, lush green leaves, warm bokeh, and 3D gold silk ribbons",
        "podium_decor": "a sculpted warm jade-veined stone slab, surrounded right beside the box and bottle by rich herbal decor: blooming white-pink Trinh nữ hoàng cung lily flowers, golden Hoàng bá bark slices, fresh green medicinal leaves, and pure morning dew drops",
        "pack_desc": "the emerald-green 'VIÊN ĐẶT PHỤ KHOA Hằng Thu' box (Hộp 10 viên) and matching green-labeled bottle",
        "footer_icons": "herbal blossom bowl + gentle water drop + evening moon star",
    },
    "HT06": {
        "scene_a": "luxurious sunlit royal plum-magenta & rose-gold silk orchid garden studio with blooming pink Phalaenopsis orchids, dewy green leaves, shimmering light bokeh, and 3D champagne-gold silk ribbons",
        "scene_b": "sensual deep plum-burgundy & champagne-gold luxury spa studio with blooming pink orchids, soft rose petals, warm golden rays, and flowing 3D gold ribbons",
        "podium_decor": "a sculpted pearl-white marble slab, surrounded right beside the box and sachets by rich luxury decor: blooming pink Phalaenopsis orchid flowers, a white seashell holding a lustrous pearl, glossy green betel leaves, and crystal Hyaluronic essence droplets",
        "pack_desc": "the vibrant magenta-pink 'ROMANCE LOVE' luxury box (showing the satin pink ribbon graphic) with its matching magenta foil sachets",
        "footer_icons": "pink orchid flower + sparkling pearl drop + loving heart",
    },
    "HT07": {
        "scene_a": "majestic imperial black-obsidian, deep amber & 24K gold oriental royal apothecary studio with warm golden sunbeams, lush dark-green ginseng leaves at the corners, golden light particles, and 3D metallic gold silk ribbons",
        "scene_b": "regal dark mahogany-obsidian & glowing 24K amber-gold luxury studio with warm golden rays, precious herbal silhouettes, and flowing 3D gold ribbons",
        "podium_decor": "a sculpted black-and-gold veined marble slab, surrounded right beside the box and bottle by rich precious tonic decor: whole golden Korean ginseng root, golden Cordyceps (Đông trùng hạ thảo), sliced deer antler (Nhung hươu), vibrant red goji berries, and red capsules",
        "pack_desc": "the dark-brown & gold 'NGỌC LONG HOÀN HẰNG THU' box (45 viên) and dark amber bottle with red capsules",
        "footer_icons": "precious ginseng root + strong vitality flexing arm + sleep moon",
    },
    "HT08": {
        "scene_a": "luminous royal sapphire-navy & diamond crystal water-light studio with blooming white snow-lotus flowers, dewy green leaves at the corners, shimmering golden-blue bokeh, and 3D champagne-gold silk ribbons",
        "scene_b": "luxury deep sapphire-blue & sunlit pearl-gold beauty studio with crystal water ripples, white blossoms, warm golden sparkles, and flowing 3D gold silk ribbons",
        "podium_decor": "a sculpted luminous white crystal-marble slab, surrounded right beside the box and bottle by rich brightening decor: a white seashell with lustrous pearls, fresh dewy sliced bright lemon (Vitamin C), glowing golden NMN spheres, white blossoms, and golden softgel capsules",
        "pack_desc": "the blue-and-white 'LEGEND WhiteSkin' box (showing the radiant woman's face & NMN L-Glutathione text) and amber glass bottle",
        "footer_icons": "radiant sun shield + glowing skin face + daily water glass",
    },
    "HT09": {
        "scene_a": "sunlit rose-ruby & morning-dew botanical garden studio with blooming white Trinh nữ hoàng cung flowers, delicate pink butterflies, dewy green herbal leaves framing the corners, and 3D champagne-gold silk ribbons",
        "scene_b": "luminous deep rose-plum & pearl-pink botanical spa studio with soft pink blossoms, green medicinal leaves, shimmering silver-gold dew, and 3D gold silk ribbons",
        "podium_decor": "a sculpted cream-white marble slab, surrounded right beside the pink boxes and sachet by rich botanical decor: blooming white Trinh nữ hoàng cung lily blossoms, fresh green Trầu không leaves, white-gold Kim ngân hoa flowers, and crystal-clear Nano Silver water droplets",
        "pack_desc": "the pastel-pink 'Gel phụ khang HẰNG THU' box (with delicate pink butterfly artwork) and matching sleek pink-and-white sachet",
        "footer_icons": "herbal flower leaf + pure silver droplet + comfort shield",
    },
}


def build_single_ref_board(spec: dict) -> str:
    code = spec["code"]
    out_jpg = os.path.join(REF_DIR, f"ref_board_{code}.jpg")

    board = Image.new("RGB", (1920, 1200), (246, 245, 241))
    # Left panel (x=20..760): Chị Hằng's approved AV PROTEIN reference poster
    st = Image.open(STYLE_REF_PATH).convert("RGB")
    st.thumbnail((740, 1160), Image.Resampling.LANCZOS)
    board.paste(st, (20, (1200 - st.height) // 2))

    # Right-top HUGE panel (x=800..1895, y=20..920): Official Product Cutout + Stick Sachet at ULTRA-CRISP scale!
    cut = Image.open(os.path.join(CUT_DIR, spec["cutout"])).convert("RGBA")
    stick_f = spec.get("extra_stick")
    if stick_f and os.path.exists(os.path.join(CUT_DIR, stick_f)):
        st_im = Image.open(os.path.join(CUT_DIR, stick_f)).convert("RGBA")
        bh = cut.height
        sh = int(bh * 0.82)
        sw = int(round(st_im.width * (sh / st_im.height)))
        st_r = st_im.resize((sw, sh), Image.Resampling.LANCZOS)
        combo = Image.new("RGBA", (cut.width + int(sw * 0.68), bh + 12), (0, 0, 0, 0))
        combo.alpha_composite(cut, dest=(0, 0))
        combo.alpha_composite(st_r, dest=(cut.width - int(sw * 0.34), bh - sh + 8))
        cut = combo

    cut.thumbnail((1060, 880), Image.Resampling.LANCZOS)
    # Enhance sharpness slightly so every tiny packaging word is 100% crisp for ChatGPT vision!
    r, g, b, a = cut.split()
    rgb_c = ImageEnhance.Sharpness(Image.merge("RGB", (r, g, b))).enhance(1.18)
    cut = Image.merge("RGBA", (*rgb_c.split(), a))

    prod_card = Image.new("RGBA", (1090, 900), (255, 255, 255, 255))
    prod_card.alpha_composite(cut, dest=((1090 - cut.width) // 2, (900 - cut.height) // 2))
    board.paste(prod_card.convert("RGB"), (805, 20))

    # Right-bottom panel (x=805..1895, y=940..1180): Official Brand Logo
    if spec["brand_group"] == "AN_VUONG":
        lg = Image.open(os.path.join(CUT_DIR, "logo_an_vuong_on_dark.png")).convert("RGBA")
        lg.thumbnail((460, 220), Image.Resampling.LANCZOS)
        lg_bg = Image.new("RGBA", (520, 240), (8, 58, 38, 255))
        lg_bg.alpha_composite(lg, dest=((520 - lg.width) // 2, (240 - lg.height) // 2))
        board.paste(lg_bg.convert("RGB"), (805, 940))
    else:
        lg = Image.open(os.path.join(CUT_DIR, "logo_hang_thu.png")).convert("RGBA")
        lg.thumbnail((220, 220), Image.Resampling.LANCZOS)
        lg_bg = Image.new("RGBA", (260, 240), (255, 255, 255, 255))
        lg_bg.alpha_composite(lg, dest=((260 - lg.width) // 2, (240 - lg.height) // 2))
        board.paste(lg_bg.convert("RGB"), (805, 940))

    board.save(out_jpg, quality=96, subsampling=0)
    return out_jpg


def build_prompt_for_spec(spec: dict) -> str:
    p_key = spec["code"].split("_")[0]
    dna = PRODUCT_SCENE_DNA[p_key]
    is_a = (spec["layout"] == "A")
    scene_desc = dna["scene_a"] if is_a else dna["scene_b"]

    if spec["brand_group"] == "AN_VUONG":
        brand_line = (
            "Official An Vượng Pharma golden-green 'A' emblem and crisp white-gold text "
            "'AN VƯỢNG PHARMA — An tâm sức khỏe - Vững vàng Thịnh Vượng' from the lower-right panel of ref_board.jpg."
        )
    else:
        brand_line = (
            "Official circular red-blue Yin-Yang HT emblem from the lower-right panel of ref_board.jpg "
            "with crisp white-gold text 'HẰNG THU PHARMA — Tinh Hoa Thảo Dược Việt'."
        )

    c1, c2, c3, c4 = spec["cards"]

    if is_a:
        layout_block = (
            "LAYOUT ARCHITECTURE (Layout A — Exact Hero-Left + Stone Slab + 4 Compact Cream Cards like the left panel of ref_board.jpg):\n"
            f"- Top-left: {brand_line}\n"
            f"- Top-right MASSIVE 3D brushed-metallic gold headline (HUGE, ultra-bold, filling the upper-right width): \"{spec['title']}\"\n"
            f"- Underneath headline: Large crisp bold white subtitle \"{spec['subtitle_1']}\" and warm gold subtitle \"{spec['subtitle_2']}\".\n"
            f"- Below subtitle on the right: Rounded dark luxury highlight banner with GIANT 3D gold number \"{spec['badge_num']}\" and bold uppercase white/gold text \"{spec['badge_l1']} / {spec['badge_l2']}\".\n"
            f"- Middle-left Hero Stage: Place the EXACT real product ({dna['pack_desc']}) from the upper-right photo of ref_board.jpg at LARGE, COMMANDING HERO SCALE, naturally lit with warm studio rim-light so it blends 100% seamlessly into the scene (ZERO pasted cutout look!), standing firmly on {dna['podium_decor']}. CRITICAL: Keep EVERY SINGLE Vietnamese word, logo, and number on the product packaging 100% sharp, faithful, and ungarbled!\n"
            "- Four Compact Warm-Cream Bento Cards with gold borders & dark numbered top badges (Cards 01 & 02 side-by-side on middle-right beside the product; Cards 03 & 04 side-by-side on bottom-right starting at x=24% so the stone slab, herbs/grains & lush leaves remain richly visible at bottom-left! ZERO empty cream space — HUGE vivid 3D illustrations filling 85%+ of each card + warm golden pill bar behind the bold metric/benefit):"
        )
    else:
        layout_block = (
            "LAYOUT ARCHITECTURE (Layout B — Dynamic Top-Right Hero Product on Stone Podium with Rich Decor + Top-Left Giant Title + 2x2 Large Bento Grid):\n"
            f"- Top-left: {brand_line}\n"
            f"- Upper-left MASSIVE 3D brushed-metallic gold headline (HUGE, ultra-bold, stacked cleanly): \"{spec['title']}\"\n"
            f"- Underneath headline on left: Large crisp bold white subtitle \"{spec['subtitle_1']}\" and warm gold subtitle \"{spec['subtitle_2']}\".\n"
            f"- Below subtitle on left: Rounded dark luxury highlight banner with GIANT 3D gold number \"{spec['badge_num']}\" and bold uppercase white/gold text \"{spec['badge_l1']} / {spec['badge_l2']}\".\n"
            f"- Upper-right Hero Stage: Place the EXACT real product ({dna['pack_desc']}) from the upper-right photo of ref_board.jpg at LARGE, COMMANDING HERO SCALE, naturally lit with warm studio rim-light so it blends 100% seamlessly into the scene (ZERO pasted cutout look!), standing firmly on {dna['podium_decor']}. CRITICAL: Keep EVERY SINGLE Vietnamese word, logo, and number on the product packaging 100% sharp, faithful, and ungarbled!\n"
            "- Lower half: 2x2 Grid of 4 Large Warm-Cream Bento Cards (01, 02, 03, 04) with gold borders, each card packed full with ZERO empty space — featuring a HUGE vivid 3D illustration on the left half of the card and LARGE bold uppercase title + golden highlight pill + bold Vietnamese description on the right half:"
        )

    cards_block = (
        f"\n  * Card {c1[0]}: Title \"{c1[1]}\" | HUGE vivid 8K 3D illustration depicting {c1[1]} & {c1[3]} | Golden highlight pill \"{c1[2]}\" | Bold dark text \"{c1[3]}\""
        f"\n  * Card {c2[0]}: Title \"{c2[1]}\" | HUGE vivid 8K 3D illustration depicting {c2[1]} & {c2[3]} | Golden highlight pill \"{c2[2]}\" | Bold dark text \"{c2[3]}\""
        f"\n  * Card {c3[0]}: Title \"{c3[1]}\" | HUGE vivid 8K 3D illustration depicting {c3[1]} & {c3[3]} | Golden highlight pill \"{c3[2]}\" | Bold dark text \"{c3[3]}\""
        f"\n  * Card {c4[0]}: Title \"{c4[1]}\" | HUGE vivid 8K 3D illustration depicting {c4[1]} & {c4[3]} | Golden highlight pill \"{c4[2]}\" | Bold dark text \"{c4[3]}\""
    )

    footer_block = (
        f"\n\nBOTTOM CREAM FOOTER BAR WITH CUSTOM DRAWN VECTOR ICONS:\n"
        f"- Left: Circular dark-gold emblem icon + bold clear text \"{spec['usage_text']}\"\n"
        f"- Center divider: 3 cute custom minimalist line-art icons ({dna['footer_icons']}) separated by '+' signs\n"
        f"- Right: Clean italic text \"{spec['disclaimer']}\"\n\n"
        "STRICT QUALITY RULES: Every single Vietnamese diacritic (dấu tiếng Việt) on the poster and on the product box MUST be 100% accurate, extra-large, bold, high-contrast, and super easy to read on a phone screen!"
    )

    return (
        "Create a super-clear, masterpiece luxury commercial product infographic poster (vertical 2:3 portrait, 1024x1536) "
        "matching the exact visual richness, giant typography, huge 3D card illustrations, custom icons, and natural stone podium aesthetics of the left reference poster in ref_board.jpg, "
        f"set in a {scene_desc} (MUST have rich real botanical/scenic depth, NEVER a plain flat background!).\n\n"
        + layout_block
        + cards_block
        + footer_block
    )


def main():
    jobs = []
    for sp in POSTERS_26:
        code = sp["code"]
        ref_jpg = build_single_ref_board(sp)
        prm = build_prompt_for_spec(sp)
        raw_png = os.path.join(RAW_OUT_DIR, f"{code}.png")
        jobs.append({
            "id": code,
            "brand_group": sp["brand_group"],
            "product_folder": sp["product_folder"],
            "file_title": sp["file_title"],
            "cutout": sp["cutout"],
            "ratio": "2:3",
            "refs": [{"path": ref_jpg, "name": "ref_board.jpg"}],
            "prompt": prm,
            "outPath": raw_png,
        })
    spec_json = os.path.join(V4_DIR, "jobs_26_chatgpt.json")
    with open(spec_json, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"Prepared {len(jobs)} bespoke ChatGPT masterpiece jobs -> {spec_json}", flush=True)


if __name__ == "__main__":
    main()
