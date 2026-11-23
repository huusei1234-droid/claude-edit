import os, sys, time
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call
from ai_ref_video import (
    stage_local_ref_image_once,
    generate_ref_images_parallel_batch,
    export_canvas_nodes_to_files,
    cleanup_exported_canvas_nodes,
)

PROJ_DIR = r"d:\AI\full studio\output\k4-muse-trong-treo"
CAST_DIR = os.path.join(PROJ_DIR, "official_cast")
ANC_DIR  = os.path.join(PROJ_DIR, "chatgpt_sets")
KF_DIR   = os.path.join(PROJ_DIR, "chatgpt_keyframes")
os.makedirs(KF_DIR, exist_ok=True)

# Clean Canvas before staging anchors
st0 = call("canvas_get_state", {})["result"]
orphans = [n["id"] for n in st0["nodes"] if n["type"] != "export:folder"]
if orphans:
    cleanup_exported_canvas_nodes(orphans)

id_thao   = stage_local_ref_image_once(os.path.join(CAST_DIR, "K4_Thao_Face.jpg"),   "k4_thao",   x=54000, y=-600)
id_bahanh = stage_local_ref_image_once(os.path.join(CAST_DIR, "K4_BaHanh_Face.jpg"), "k4_bahanh", x=54000, y=-150)
id_tuan   = stage_local_ref_image_once(os.path.join(CAST_DIR, "K4_Tuan_Face.jpg"),   "k4_tuan",   x=54000, y=300)
id_bo1    = stage_local_ref_image_once(os.path.join(ANC_DIR,  "SET_BO1_DINING.png"), "k4_bo1",    x=54500, y=-400)
id_bo2    = stage_local_ref_image_once(os.path.join(ANC_DIR,  "SET_BO2_GARDEN.png"), "k4_bo2",    x=54500, y=150)

AIRY_STYLE = (
    "Vertical 9:16 bright, airy, crystal-clear high-key Korean-drama & live-wallpaper cinematography "
    "(abundant soft natural window daylight, luminous creamy skin tones, open bright shadows, fresh natural pastel colors, Sony A7R5 85mm f/1.8, ZERO dark muddy shadows, ZERO heavy orange contrast): "
)

CHAINS = [("ChatGPT", "chatgpt::chatgpt-image"), ("Muse", "muse::muse-image")]

KF_SPECS = [
    {
        "ref_tag": "kf_s01",
        "ratio": "9:16",
        "reference_node_ids": [id_thao, id_bahanh, id_tuan, id_bo1],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "medium shot inside the exact bright sunlit dining room from reference (showing the white-gold marble-vein bamboo charcoal panel and light honey-oak vertical fluted wood slats softly lit in the background, sheer white curtains & sunlit green plants by the window): "
            "in the foreground-left stands Thảo (exact young sweet-faced woman from reference wearing an elegant cream-white tailored office blazer over a white silk blouse and carrying a small white leather shoulder bag, looking tired and surprised at the table); "
            "seated at the light-oak dining table in the mid-ground are Bà Hạnh (exact 55-year-old wavy-haired mother-in-law in brown dress with 3 fabric shoulder roses on the left of table) and Tuấn (exact curly-haired husband in crisp white dress shirt on the right of table) who have already finished eating, leaving only an almost-empty plate of boiled greens on the table."
        ),
    },
    {
        "ref_tag": "kf_s02",
        "ratio": "9:16",
        "reference_node_ids": [id_bahanh, id_bo1],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "tight facial close-up from shoulders up (NO hands in frame) of Bà Hạnh (exact 55-year-old wavy-haired mother-in-law in brown dress with 3 fabric roses on right shoulder from reference) seated on the left side of the bright sunlit dining room, "
            "with the light honey-oak vertical fluted wood slats and white-gold marble-vein accent wall softly blurred in bright natural daylight behind her; she glances sideways with a cold, dismissive expression."
        ),
    },
    {
        "ref_tag": "kf_s03",
        "ratio": "9:16",
        "reference_node_ids": [id_tuan, id_bo1],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "tight facial close-up from shoulders up (NO hands in frame) of Tuấn (exact young Vietnamese husband with textured black hair in crisp white dress shirt from reference) seated on the right side of the bright sunlit dining room, "
            "with the glossy white-gold marble-vein bamboo charcoal panel and light-oak fluted wood slats softly lit in natural daylight behind him; he furrows his brows looking toward the left to scold his wife."
        ),
    },
    {
        "ref_tag": "kf_s04",
        "ratio": "9:16",
        "reference_node_ids": [id_thao, id_bo1],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "tight facial close-up from shoulders up (NO hands in frame) of Thảo (exact sweet-faced young woman from reference wearing cream-white office blazer over white blouse and delicate clover necklace) standing on the left side of the bright sunlit dining room, "
            "with the bright white-gold marble-vein bamboo charcoal panel and light honey-oak fluted wood slats softly lit behind her and sunlit green window light on her hair; her round eyes glisten with hurt tears and resolute dignity looking toward the right."
        ),
    },
    {
        "ref_tag": "kf_s05",
        "ratio": "9:16",
        "reference_node_ids": [id_thao, id_bahanh, id_tuan, id_bo1],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "medium close-up inside the bright sunlit dining room: in the foreground Thảo (exact young woman in cream-white office blazer) holds a white smartphone to her right ear with a composed, decisive half-smile (only right hand holding phone, left arm down out of frame); "
            "in the bright soft-focus background in front of the white-gold marble-vein bamboo charcoal and light-oak fluted wood slat wall, Bà Hạnh (brown 3-rose dress) and Tuấn (white shirt) stand staring at her in surprise."
        ),
    },
    {
        "ref_tag": "kf_s06",
        "ratio": "9:16",
        "reference_node_ids": [id_thao, id_bahanh, id_tuan, id_bo2],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "medium shot on the bright sunlit lush green garden patio terrace from reference in golden-white afternoon daylight: "
            "in the foreground at the round light-teak garden table sits Thảo (exact sweet-faced young woman in cream-white blazer) happily enjoying a steaming gourmet platter of golden cheese-baked lobster, grilled prawns, and fresh fruit juice surrounded by sunlit green leaves; "
            "right behind the clean glass sliding doors on the right (showing the bright dining room's light-oak fluted wood slats inside), Tuấn (white shirt) and Bà Hạnh (brown 3-rose dress) stand staring out at her feast in stunned disbelief."
        ),
    },
    {
        "ref_tag": "kf_s07",
        "ratio": "9:16",
        "reference_node_ids": [id_tuan, id_bo2],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "tight facial close-up from shoulders up (NO hands in frame) of Tuấn (exact husband in crisp white dress shirt from reference) standing right outside the sunlit glass garden patio door in bright afternoon daylight, "
            "with the bright living room's light honey-oak vertical fluted wood slats and white-gold marble-vein wall visible behind him; he looks down-left in shocked, annoyed disbelief."
        ),
    },
    {
        "ref_tag": "kf_s08",
        "ratio": "9:16",
        "reference_node_ids": [id_thao, id_bo2],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "tight facial close-up from shoulders up (NO hands in frame) of Thảo (exact sweet-faced young woman in cream-white blazer and clover necklace from reference) seated on the bright sunlit garden patio, "
            "with luminous sunlit green foliage and soft creamy bokeh sparkling behind her; she looks up-right with a radiant, unbothered, confident smile."
        ),
    },
    {
        "ref_tag": "kf_s09",
        "ratio": "9:16",
        "reference_node_ids": [id_thao, id_bahanh, id_tuan, id_bo2],
        "timeout_per_tier": 300,
        "preferred_chain": CHAINS,
        "prompt": AIRY_STYLE + (
            "close-up from shoulders up (NO hands in frame) of Thảo (exact sweet-faced young woman in cream-white blazer from reference) seated in the foreground on the bright sunlit garden patio, looking straight into the camera lens with bright, poised confidence; "
            "in the bright soft-focus background behind her beside the glass patio doors and light-oak fluted wood slats, Bà Hạnh (brown 3-rose dress on left) and Tuấn (white shirt on right) stand speechless amidst sunlit green garden plants."
        ),
    },
]

# Run in clean batches of 2 on ChatGPT HTPM so Brave tabs never bottleneck!
all_exported = {}
for i in range(0, len(KF_SPECS), 2):
    batch = KF_SPECS[i:i+2]
    res = generate_ref_images_parallel_batch(batch, max_workers=2)
    bmap = {nid: os.path.join(KF_DIR, f"{tag}.png") for tag, nid, _ in res}
    exp = export_canvas_nodes_to_files(bmap)
    all_exported.update(exp)
    # Delete exported generated image nodes immediately to keep Canvas fast (keep only our 5 staged anchors!)
    cleanup_exported_canvas_nodes(list(bmap.keys()))
    print(f"Batch {i//2 + 1} exported: {list(exp.values())}", flush=True)

st_end = call("canvas_get_state", {})["result"]
cleanup_exported_canvas_nodes([n["id"] for n in st_end["nodes"] if n["type"] != "export:folder"])
print("\n=== ALL 9 CRYSTAL-CLEAR CHATGPT KEYFRAMES READY & CANVAS CLEANED! ===", flush=True)
