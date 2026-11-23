import os, shutil, sys
from PIL import Image

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
os.makedirs(CAST_DIR, exist_ok=True)
os.makedirs(ANC_DIR, exist_ok=True)

CHAR_SRC = r"Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"
P_THAO   = os.path.join(CHAR_SRC, "G01_05a - Thảo (Vợ Tuấn - Con dâu bà Hạnh - Chị ruột Mai) [Váy trắng].png")
P_BAHANH = os.path.join(CHAR_SRC, "G01_03a - Bà Hạnh (Mẹ ruột Tuấn & Linh - Mẹ chồng Thảo) [Đầm nâu].png")
P_TUAN   = os.path.join(CHAR_SRC, "G01_04b - Tuấn (Chồng Thảo - Anh trai Linh - Con trưởng ông Tấn) [Sơ mi trắng].png")

# Extract clean left close-up face portrait (0..49% width, zero split line, zero handbag!) for 100% pure identity lock
def crop_left_portrait(src_p, dst_p):
    im = Image.open(src_p).convert("RGB")
    w, h = im.size
    crop = im.crop((0, 0, int(w * 0.488), h))
    crop.save(dst_p, quality=96)
    print("Saved clean K4 portrait:", dst_p, crop.size, flush=True)

crop_left_portrait(P_THAO,   os.path.join(CAST_DIR, "K4_Thao_Face.jpg"))
crop_left_portrait(P_BAHANH, os.path.join(CAST_DIR, "K4_BaHanh_Face.jpg"))
crop_left_portrait(P_TUAN,   os.path.join(CAST_DIR, "K4_Tuan_Face.jpg"))

MS_KIT = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\02_MS_Noi_That\hinh_anh_website_noithat"
MS_THAN_TRE = os.path.join(MS_KIT, "05_phong-khach.webp")
MS_LAM_SONG = os.path.join(MS_KIT, "08_lam-lam-4-song-160x22x3000mm.webp")

# Clean Canvas before starting
st0 = call("canvas_get_state", {})["result"]
orphans = [n["id"] for n in st0["nodes"] if n["type"] != "export:folder"]
if orphans:
    cleanup_exported_canvas_nodes(orphans)

id_thantre = stage_local_ref_image_once(MS_THAN_TRE, "ms_light_thantre", x=55000, y=-400)
id_lamsong = stage_local_ref_image_once(MS_LAM_SONG, "ms_light_lamsong", x=55000, y=100)

# Generate BOTH airy, sunlit, crystal-clear backgrounds on ChatGPT HTPM ONLY!
SET_SPECS = [
    {
        "ref_tag": "SET_BO1_DINING",
        "ratio": "9:16",
        "reference_node_ids": [id_thantre, id_lamsong],
        "timeout_per_tier": 300,
        "preferred_chain": [("ChatGPT", "chatgpt::chatgpt-image")],
        "prompt": (
            "Vertical 9:16 bright, airy, crystal-clear high-key interior photography (exact luminous clean pastel daylight aesthetic of Korean lifestyle live wallpaper, Sony A7R5 50mm f/1.8, soft natural daylight, open bright shadows, fresh natural colors, ZERO heavy contrast, ZERO orange muddiness): "
            "an affluent modern Vietnamese townhouse dining and living room bathed in abundant soft natural daylight streaming through sheer white chiffon curtains and tall glass garden doors with fresh vibrant green foliage outside on the right; "
            "behind the light natural oak dining table and cream linen chairs is a bright, tasteful decorative feature wall combining a glossy white-and-soft-gold marble-vein bamboo charcoal panel in the center flanked symmetrically by warm light honey-oak vertical fluted wood slat panels (lam sóng gỗ sáng); "
            "empty room, ZERO people."
        ),
    },
    {
        "ref_tag": "SET_BO2_GARDEN",
        "ratio": "9:16",
        "reference_node_ids": [id_thantre, id_lamsong],
        "timeout_per_tier": 300,
        "preferred_chain": [("ChatGPT", "chatgpt::chatgpt-image")],
        "prompt": (
            "Vertical 9:16 bright, airy, crystal-clear high-key architectural lifestyle photography (luminous fresh daylight live-wallpaper aesthetic, soft natural sunlight, open shadows, vibrant fresh greens, ZERO heavy dark contrast): "
            "a sunlit covered garden patio terrace right outside an affluent modern Vietnamese home in late afternoon golden-white daylight; "
            "in the foreground is a clean light-teak round garden table and cream rattan chair surrounded by lush sunlit green tropical plants and blooming white flowers; "
            "on the right side are tall clean sliding glass doors looking into the bright airy dining room with its glossy white-gold marble-vein bamboo charcoal wall and light honey-oak vertical fluted wood slat panels; "
            "empty scene, ZERO people."
        ),
    },
]

res = generate_ref_images_parallel_batch(SET_SPECS, max_workers=2)
to_exp = {nid: os.path.join(ANC_DIR, f"{tag}.png") for tag, nid, _ in res}
exported = export_canvas_nodes_to_files(to_exp)
print("Exported crystal-clear ChatGPT sets:", list(exported.values()), flush=True)

st1 = call("canvas_get_state", {})["result"]
cleanup_exported_canvas_nodes([n["id"] for n in st1["nodes"] if n["type"] != "export:folder"])
print("CHATGPT CRYSTAL-CLEAR SETS DONE & CANVAS CLEANED!", flush=True)
