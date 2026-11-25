# -*- coding: utf-8 -*-
"""
Step 2: Generate bespoke Studio Backdrops + 2x2 3D Ingredient/Mechanism Illustration Sheets
via Priority #1 ChatGPT (HTPM project on Brave :9333, 3 parallel tabs, auto-delete temp chats)
with automatic fallback to Gemini 2.1 -> Google Flow -> Muse via ai_ref_video.py.
"""
import os, sys, json

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from ai_ref_video import (
    generate_ref_images_parallel_batch,
    export_canvas_nodes_to_files,
    cleanup_exported_canvas_nodes,
)

PROJ = r"d:\AI\full studio\projects\av_htpm_26_posters_2211"
ART_DIR = os.path.join(PROJ, "assets", "ai_art")
os.makedirs(ART_DIR, exist_ok=True)

QUAD_RULE = (
    "Clean 2x2 grid layout of 4 isolated miniature 3D commercial product-infographic illustrations "
    "on a pure solid warm ivory-cream background (#FFFDF6). "
    "Generous empty #FFFDF6 cream margin around the outer edges and a wide empty #FFFDF6 gutter between all 4 quadrants. "
    "STRICTLY NO TEXT, NO LETTERS, NO NUMBERS, NO LABELS, NO DIVIDER LINES, NO BOX FRAMES. "
    "Ultra-crisp 8K medical & botanical 3D studio render, warm appetizing lighting, soft contact shadow under each item: "
)

BG_RULE = (
    "Luxury commercial pharmaceutical & supplement poster background only (STRICTLY NO TEXT, NO LETTERS, NO LOGOS, NO BOTTLES, NO BOXES). "
    "Rich studio depth-of-field, subtle 3D flowing metallic champagne-gold silk ribbon accents at top-right and bottom-left, "
)

SPECS = [
    # ==================== A. STUDIO BACKDROPS (3:4 Portrait) ====================
    {
        "name": "bg_av_emerald_left",
        "out_path": os.path.join(ART_DIR, "bg_av_emerald_left.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Deep royal emerald green (#063B27 to #0B5339) sunlit botanical studio. "
            "On the middle-left side (x=22%, y=46%), a sculpted natural warm travertine stone podium slab with a few fresh green leaves and golden wheat ears beside the podium base, ready for a product box to stand on. "
            "Lush dewy green botanical leaves framing the far-left edge and top-right corner. "
            "The right half and bottom 40% are clean smooth dark emerald-jade gradient vignette."
        ),
    },
    {
        "name": "bg_av_emerald_right",
        "out_path": os.path.join(ART_DIR, "bg_av_emerald_right.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Luminous imperial emerald-teal & warm golden sunbeam studio (#053524 to #0E5A3E). "
            "On the upper-center-right or center-top area, a sleek circular warm natural oak and cream stone pedestal bathed in soft golden rim light with delicate botanical leaves. "
            "Clean smooth dark emerald gradient across the lower half for infographic cards."
        ),
    },
    {
        "name": "bg_ht_ruby_left",
        "out_path": os.path.join(ART_DIR, "bg_ht_ruby_left.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Deep royal ruby-burgundy & velvet rose studio (#580A22 to #881337) with soft golden bokeh. "
            "On the middle-left side (x=22%, y=46%), a luxury cream-white marble cylinder podium with gold trim and soft pink lotus & rose petals around its base. "
            "Clean smooth deep burgundy-crimson gradient on the right side and bottom 40%."
        ),
    },
    {
        "name": "bg_ht_ruby_center",
        "out_path": os.path.join(ART_DIR, "bg_ht_ruby_center.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Regal deep crimson-magenta & champagne-gold silk studio (#4F081E to #7F1133). "
            "Soft glowing rose-gold light rays, subtle pink lotus petals at top corners, warm ivory-gold marble pedestal subtly lit, "
            "clean rich dark ruby gradient across the lower two-thirds for infographic cards."
        ),
    },
    {
        "name": "bg_ht_jade_left",
        "out_path": os.path.join(ART_DIR, "bg_ht_jade_left.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Rich imperial herbal jade-forest green (#073B2C to #0F5C43) sunlit apothecary studio. "
            "On the middle-left side (x=22%, y=46%), a natural warm sandstone & gold-trimmed podium with fresh green medicinal leaves and white herbal blossoms at the base. "
            "Clean smooth dark jade-emerald gradient on the right side and bottom 40%."
        ),
    },
    {
        "name": "bg_ht_plum_left",
        "out_path": os.path.join(ART_DIR, "bg_ht_plum_left.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Sensual luxury royal plum-magenta & rose-gold silk studio (#3E0730 to #6E1153). "
            "On the middle-left side (x=22%, y=46%), a pearl-white & rose-gold podium with glowing pearl water droplets and silk orchid petals. "
            "Clean smooth deep royal plum gradient on the right side and bottom 40%."
        ),
    },
    {
        "name": "bg_ht_obsidian_left",
        "out_path": os.path.join(ART_DIR, "bg_ht_obsidian_left.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Majestic imperial black-obsidian & warm 24K amber-gold luxury studio (#140C05 to #2C1A0B). "
            "On the middle-left side (x=22%, y=46%), a dark black-marble & brushed-gold pedestal with subtle golden light particles and dried precious ginseng roots at the base. "
            "Clean smooth dark obsidian-brown gradient on the right side and bottom 40%."
        ),
    },
    {
        "name": "bg_ht_sapphire_left",
        "out_path": os.path.join(ART_DIR, "bg_ht_sapphire_left.png"),
        "aspect": "3:4",
        "prompt": BG_RULE + (
            "Luxury deep royal sapphire-navy & diamond-crystal water light studio (#061E45 to #0D3B7A). "
            "On the middle-left side (x=22%, y=46%), a luminous white-crystal & silver-gold podium with glowing translucent pearl spheres and water-silk waves. "
            "Clean smooth deep sapphire-blue gradient on the right side and bottom 40%."
        ),
    },

    # ==================== B. 13 PRODUCT INGREDIENT 2x2 QUAD SHEETS (1:1) ====================
    {
        "name": "quad_av01_protein",
        "out_path": os.path.join(ART_DIR, "quad_av01_protein.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) wooden bowl of white rice with fresh open green pea pod, soybeans and golden wheat ears; "
            "(Top-Right) clean 3D pink healthy muscle fiber bundle with a glowing golden BCAA molecular structure beside it; "
            "(Bottom-Left) clean 3D pink intestinal tract icon with a circular blue magnifying inset showing friendly blue rod probiotics; "
            "(Bottom-Right) chicory root and wooden spoon of fine cream prebiotic inulin powder with golden grains and green leaves."
        ),
    },
    {
        "name": "quad_av02_bojomi",
        "out_path": os.path.join(ART_DIR, "quad_av02_bojomi.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) natural red-coral calcified marine algae Lithothamnion with a glowing pearl-white Calcium sphere in clear ocean droplets; "
            "(Top-Right) golden-amber translucent Vitamin D3 softgel droplet radiating warm morning sunshine sparkles; "
            "(Bottom-Left) fresh fermented natto beans & green leaf with a glowing emerald-gold Vitamin K2 molecular orb guiding minerals into a clean white 3D bone trabeculae model; "
            "(Bottom-Right) luminous pearl-pink & gold triple-helix Collagen peptide strands weaving elastic support around a clean white joint cartilage model."
        ),
    },
    {
        "name": "quad_av03_collamela",
        "out_path": os.path.join(ART_DIR, "quad_av03_collamela.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) golden luminous micro-molecular Collagen Tripeptide 3-sphere chain inside a crystal-clear golden serum drop; "
            "(Top-Right) crystal-blue & pearl-gold Hyaluronic Acid water-binding spheres plumping a clean 3D layered skin dermis model; "
            "(Bottom-Left) fresh dewy sliced golden-orange citrus fruit with glowing Vitamin C antioxidant light spheres; "
            "(Bottom-Right) shimmering silver-gold Zinc mineral crystal orb beside healthy glossy hair strands and a smooth pink fingernail icon."
        ),
    },
    {
        "name": "quad_av04_curcumilk",
        "out_path": os.path.join(ART_DIR, "quad_av04_curcumilk.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) fresh sliced vibrant orange turmeric rhizome beside a glowing golden lipid-bilayer Phytosome nano-sphere; "
            "(Top-Right) creamy splash of warm nut & oat milk in a glass cup surrounded by golden oats, almonds and grains; "
            "(Bottom-Left) clean 3D glowing golden protective shield gently coating a healthy pink stomach illustration; "
            "(Bottom-Right) blooming creamy-white Madagascar vanilla orchid flower with two dark vanilla pods and warm golden milk swirl."
        ),
    },
    {
        "name": "quad_ht01_dieu_kinh",
        "out_path": os.path.join(ART_DIR, "quad_ht01_dieu_kinh.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) sliced precious Angelica sinensis (Đương quy) herbal root with warm ruby tonic droplets and green leaves; "
            "(Top-Right) aromatic Cyperus rotundus (Hương phụ) & Bupleurum dried herbal roots in a small wooden apothecary mortar; "
            "(Bottom-Left) vibrant red-orange Carthamus tinctorius (Hồng hoa) saffron-like petals blooming with warm golden Qi glow; "
            "(Bottom-Right) deep red Salvia miltiorrhiza (Đan sâm) & Spatholobus herbal slices beside a clean artistic rose-gold 3D healthy ovarian follicle pearl symbol."
        ),
    },
    {
        "name": "quad_ht02_lt_plus",
        "out_path": os.path.join(ART_DIR, "quad_ht02_lt_plus.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) golden-yellow Phellodendron amurense (Hoàng bá) herbal bark slices with pure golden antibacterial droplets; "
            "(Top-Right) blooming white-and-gold Lonicera japonica (Kim ngân hoa) honeysuckle flowers with fresh green tea leaves; "
            "(Bottom-Left) glossy heart-shaped green Piper betle (Lá trầu không) leaves with dewy water drops and Leonurus (Ích mẫu) flowers; "
            "(Bottom-Right) crystal-clear 3D Lactic Acid pH-balance water droplet shield with gentle pink protective aura."
        ),
    },
    {
        "name": "quad_ht03_da_day",
        "out_path": os.path.join(ART_DIR, "quad_ht03_da_day.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) fresh purple-green Hedyotis capitellata (Dạ cẩm) & Ardisia (Lá khôi) medicinal leaves with soothing emerald dew; "
            "(Top-Right) dried Ampelopsis cantoniensis (Chè dây) & golden Coptis (Hoàng liên) roots with a warm herbal tea cup; "
            "(Bottom-Left) sliced Curcuma zedoaria (Nghệ đen) rhizomes and Aucklandia (Mộc hương) root with golden essential oil drop; "
            "(Bottom-Right) Atractylodes (Bạch truật) root and blooming yellow Dandelion (Bồ công anh) flower with clean 3D soothing stomach shield."
        ),
    },
    {
        "name": "quad_ht04_romance_vip",
        "out_path": os.path.join(ART_DIR, "quad_ht04_romance_vip.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) blooming velvety red Damask rose flower with crystal rose-water essence droplets; "
            "(Top-Right) glowing pearl-pink Botanical Collagen triple-helix ribbons floating in silky moisture; "
            "(Bottom-Left) fresh dewy green Camellia sinensis tea buds and leaves with pure cleansing water splash; "
            "(Bottom-Right) sliced translucent Aloe vera gel leaf beside a golden glowing Vitamin E softgel pearl."
        ),
    },
    {
        "name": "quad_ht05_khit_hong",
        "out_path": os.path.join(ART_DIR, "quad_ht05_khit_hong.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) elegant white Crinum latifolium (Trinh nữ hoàng cung) royal lily blossoms with fresh green ribbon leaves; "
            "(Top-Right) Sophora flavescens (Khổ sâm) & Cnidium monnieri (Xà sàng tử) herbal seeds and white umbel flowers in wooden dish; "
            "(Bottom-Left) golden Phellodendron (Hoàng bá) herbal bark pieces with pure emerald botanical essence drop; "
            "(Bottom-Right) golden-amber Coptis chinensis (Hoàng liên) medicinal rhizome with a glowing pink lotus elasticity symbol."
        ),
    },
    {
        "name": "quad_ht06_romance_love",
        "out_path": os.path.join(ART_DIR, "quad_ht06_romance_love.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) crystal-blue Hyaluronic Acid & Panthenol B5 moisture droplets plumping a silky pink petal surface; "
            "(Top-Right) open white oyster shell holding a luminous iridescent pearl beside golden Collagen helix strands; "
            "(Bottom-Left) glowing white-gold Niacinamide crystal prism beside a warm amber Vitamin E oil droplet; "
            "(Bottom-Right) fresh green Piper betle leaf, green tea bud and golden turmeric extract drop in a clean botanical arrangement."
        ),
    },
    {
        "name": "quad_ht07_ngoc_long",
        "out_path": os.path.join(ART_DIR, "quad_ht07_ngoc_long.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) precious golden Cordyceps militaris (Đông trùng hạ thảo) & sliced velvet deer antler (Nhung hươu) on dark wood with golden aura; "
            "(Top-Right) purple Morinda officinalis (Ba kích tím) root & Curculigo (Sâm cau) rhizome radiating warm vitality; "
            "(Bottom-Left) Eurycoma longifolia (Bá bệnh) sliced root & Tribulus terrestris (Bạch tật lê) golden fruit; "
            "(Bottom-Right) green heart-shaped Epimedium (Dâm dương hoắc) leaves & red Cynomorium (Nấm ngọc cẩu) herb."
        ),
    },
    {
        "name": "quad_ht08_white_skin",
        "out_path": os.path.join(ART_DIR, "quad_ht08_white_skin.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) luminous diamond-white L-Glutathione crystal sphere deflecting dark UV/melanin dots from bright radiant skin layers; "
            "(Top-Right) futuristic glowing blue-and-gold NMN cellular energy coenzyme helix ring sparkling with vitality; "
            "(Bottom-Left) silky pearl-pink Amino Acid Peptide-GP micro-chains rebuilding smooth elastic skin structure; "
            "(Bottom-Right) golden translucent Vitamin E antioxidant oil drop surrounded by dewy water sparkles and white camellia."
        ),
    },
    {
        "name": "quad_ht09_gel_pk",
        "out_path": os.path.join(ART_DIR, "quad_ht09_gel_pk.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) futuristic shimmering metallic Nano Silver (Ag+) spherical particles inside a crystal-clear purifying gel drop; "
            "(Top-Right) white Crinum latifolium (Trinh nữ hoàng cung) lily & soft pink Paeonia lactiflora (Bạch thược) peony blossom; "
            "(Bottom-Left) golden-white Lonicera japonica (Kim ngân hoa) flowers & glossy green Piper betle (Trầu không) leaves; "
            "(Bottom-Right) Poria cocos (Bạch linh) white herbal cubes, Khổ sâm & Xà sàng tử botanicals with fresh mint-water splash."
        ),
    },

    # ==================== C. 4 MECHANISM / LIFESTYLE BENEFIT 2x2 QUAD SHEETS FOR DESIGN #2 ====================
    {
        "name": "quad_mech_nutrition",
        "out_path": os.path.join(ART_DIR, "quad_mech_nutrition.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) glowing 3D emerald-and-gold nutrient absorption shield inside a clean healthy digestive/cellular icon; "
            "(Top-Right) energetic 3D golden vitality figure / strong bone-and-muscle harmony emblem with warm sunbeam; "
            "(Bottom-Left) happy balanced daily meal & wellness clock icon with fresh grains, milk glass and green check badge; "
            "(Bottom-Right) sleek glass cup with warm golden-cream drink being stirred smoothly with a spoon in 1 minute."
        ),
    },
    {
        "name": "quad_mech_women_care",
        "out_path": os.path.join(ART_DIR, "quad_mech_women_care.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) clean 3D rose-gold & crystal water-drop purifying shield gently clearing impurities with lotus petals; "
            "(Top-Right) glowing 3D pH 3.8-4.5 balance scale in soft pink and pearl-gold with protective friendly flora bubbles; "
            "(Bottom-Left) blooming dewy pink silk rose & pearl moisture aura representing softness, elasticity and lasting freshness; "
            "(Bottom-Right) elegant morning-and-evening moon & sun wellness schedule badge with gentle herbal care drop."
        ),
    },
    {
        "name": "quad_mech_internal_health",
        "out_path": os.path.join(ART_DIR, "quad_mech_internal_health.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) clean 3D soothing golden-emerald herbal barrier calming acid waves inside a healthy pink stomach model; "
            "(Top-Right) harmonious ruby-and-gold feminine cycle calendar & glowing healthy pearl follicle balance emblem; "
            "(Bottom-Left) radiant cellular vitality & calm restful sleep-and-digestion harmony icon with herbal leaves; "
            "(Bottom-Right) warm glass of water beside traditional herbal pills on a clean wooden tray with 30-min clock icon."
        ),
    },
    {
        "name": "quad_mech_beauty_men",
        "out_path": os.path.join(ART_DIR, "quad_mech_beauty_men.png"),
        "aspect": "1:1",
        "prompt": QUAD_RULE + (
            "(Top-Left) luminous 3D layered skin cross-section becoming bright, even-toned and hydrated with diamond-pearl glow; "
            "(Top-Right) 3D golden antioxidant umbrella shield blocking UV rays and free-radical sparks; "
            "(Bottom-Left) majestic 3D golden lion/dragon vitality crest & glowing cellular ATP battery emblem for men's stamina; "
            "(Bottom-Right) luxury daily supplement capsule & sachet routine icon with sparkling hydration glass."
        ),
    },
]

if __name__ == "__main__":
    todo = [s for s in SPECS if not (os.path.exists(s["out_path"]) and os.path.getsize(s["out_path"]) > 30_000)]
    print(f"Total AI Art Specs: {len(SPECS)} | Remaining to generate: {len(todo)}", flush=True)
    # Process in chunks of 6 so every 6 images are exported to disk & cleaned from Canvas immediately!
    CHUNK = 6
    for i in range(0, len(todo), CHUNK):
        sub = todo[i : i + CHUNK]
        batch_inp = [
            {
                "ref_tag": s["name"],
                "prompt": s["prompt"],
                "ratio": s["aspect"],
                "timeout_per_tier": 260,
            }
            for s in sub
        ]
        tag_to_dest = {s["name"]: s["out_path"] for s in sub}
        print(f"\n=== Generating Chunk {i//CHUNK + 1} ({[s['name'] for s in sub]}) ===", flush=True)
        gen_out = generate_ref_images_parallel_batch(batch_inp, max_workers=3)
        nid_map = {nid: tag_to_dest[tag] for (tag, nid, _prov) in gen_out if nid}
        exported = export_canvas_nodes_to_files(nid_map, timeout_s=180)
        print(f"Exported {len(exported)}/{len(sub)} files in chunk {i//CHUNK + 1}!", flush=True)
        cleanup_exported_canvas_nodes(list(nid_map.keys()))
    print("ALL AI ART SPECS GENERATED AND SAVED!", flush=True)
