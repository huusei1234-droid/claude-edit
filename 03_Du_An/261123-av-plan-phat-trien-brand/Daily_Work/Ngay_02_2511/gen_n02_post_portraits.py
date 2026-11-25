# -*- coding: utf-8 -*-
"""
Tạo 5 ảnh chân dung 1:1 bối cảnh TP. Nha Trang cho 5 Bài Thiết Kế Ngày 02 (25/11/2026)
qua ChatGPT Dự án HTPM (song song max_workers=3, tự xóa chat tạm, khóa 100% khuôn mặt từ AV_MODEL_MASTER_SHEET.jpg).
"""
import os, sys
from pathlib import Path

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

WORK = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_02_2511")
OUT_DIR = WORK / "01_ChatGPT_Post_Portraits"
OUT_DIR.mkdir(parents=True, exist_ok=True)
MASTER_FACE = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\01_Mau_USP_Goc\AV_MODEL_MASTER_SHEET.jpg"

FACE_LOCK = (
    "CRITICAL IDENTITY LOCK: Use the EXACT same 27-year-old Vietnamese woman's face, delicate oval jawline, "
    "bright dark almond eyes, natural brows, gentle nose, soft rose lips, fair luminous skin, and radiant warm smile "
    "from the reference image. "
    "COMPOSITION LOCK: Frame her neatly on the RIGHT 44% of the 1:1 square frame (three-quarter / waist-up shot), "
    "leaving the LEFT 56% open bright soft-focus sunlit coastal background for typography and product cutouts. "
    "ZERO text, ZERO labels, ZERO brand logos, ZERO boxes in the photo. Pure editorial commercial lifestyle photography, Canon R5 85mm f/2."
)

SPECS = [
    (
        "N02_POST1_AVP_GYM_NT.png",
        "N02_POST1_AVP",
        FACE_LOCK + " SETTING: Sunlit modern rooftop fitness terrace overlooking turquoise Nha Trang bay with palm fronds and clear morning sky in soft bokeh. "
        "OUTFIT 1: Sleek heather-grey fitted Pilates crop top and matching high-waisted athletic leggings, crisp white fabric headband on a high bouncy ponytail, "
        "tiny pearl stud earrings, white smart sport watch. POSE: Holding a clean transparent glass of creamy light-beige plant protein shake with a bright confident morning smile."
    ),
    (
        "N02_POST2_BOJOMI_RUN5_NT.png",
        "N02_POST2_BOJ",
        FACE_LOCK + " SETTING: Golden morning sunlight along Pham Van Dong coastal boulevard in Nha Trang with coconut palm trees, sunlit sandy beach, and sparkling blue ocean in soft bokeh. "
        "OUTFIT 2: Fresh mint-green breathable running tank top, crisp white athletic pleated skort, sleek white sun visor cap over a neat braided ponytail, sport smartwatch. "
        "POSE: Holding a minimalist ceramic travel mug with warm vanilla cereal drink, refreshed joyful post-run glow."
    ),
    (
        "N02_POST3_KID1Y_CREAM_NT.png",
        "N02_POST3_KID",
        FACE_LOCK + " SETTING: Bright airy luxury ocean-view apartment living room in Nha Trang with floor-to-ceiling glass balcony overlooking sunny turquoise sea and soft cream linen curtains. "
        "OUTFIT 3: Elegant ivory-cream linen midi dress with a delicate pastel sage-mint waist bow ribbon, half-up wavy dark brown hair secured with a small pearl clip, thin gold bracelet. "
        "POSE: Seated warmly on a light beige linen sofa, gentle nurturing motherly smile toward camera, calm clean background on left."
    ),
    (
        "N02_POST4_CURCU_15H_NT.png",
        "N02_POST4_CUR",
        FACE_LOCK + " SETTING: Sunlit modern seaside workspace cafe overlooking Nha Trang bay at 3 PM warm golden afternoon sunlight, soft potted tropical leaves in bokeh. "
        "OUTFIT 4: Chic olive-sage sleeveless linen midi dress with fine gold pendant necklace, soft loose waves dark brown hair, classic rose-gold wristwatch. "
        "POSE: Relaxed at a bright oak desk holding a clean ceramic cup of warm golden creamy turmeric vanilla milk, serene satisfied smile."
    ),
    (
        "N02_POST5_COLLA_TET_NT.png",
        "N02_POST5_COL",
        FACE_LOCK + " SETTING: Glamorous golden sunset terrace overlooking Nha Trang bay with soft coral-pink evening sky and delicate tropical pink bougainvillea in warm bokeh. "
        "OUTFIT 5: Crisp ivory silk blouse layered under a chic lightweight cream knit vest, lustrous glowing porcelain skin, delicate pearl drop earrings, sleek low-bun with soft face-framing tendrils. "
        "POSE: Holding a crystal glass of chilled translucent rosy-peach collagen drink, radiant festive smile."
    ),
]


def main():
    todo = [(fn, tag, pr) for fn, tag, pr in SPECS if not (OUT_DIR / fn).exists()]
    if not todo:
        print("[SKIP] All 5 1:1 Nha Trang post portraits already exist.")
        return

    face_nid = arv.stage_local_ref_image_once(MASTER_FACE, ref_tag="av_face_n02")
    created_nodes = [face_nid]
    try:
        image_specs = [
            {
                "prompt": pr,
                "ref_tag": tag,
                "ratio": "1:1",
                "reference_node_ids": [face_nid],
            }
            for fn, tag, pr in todo
        ]
        results = arv.generate_ref_images_parallel_batch(image_specs, max_workers=3)
        export_map = {}
        for (fn, tag, _), (_, nid, prov) in zip(todo, results):
            created_nodes.append(nid)
            export_map[nid] = str(OUT_DIR / fn)
            print(f"[GENERATED] {fn} via {prov} (node={nid})", flush=True)
        exported = arv.export_canvas_nodes_to_files(export_map)
        print(f"[EXPORTED] {len(exported)}/{len(todo)} portraits to {OUT_DIR}", flush=True)
    finally:
        arv.cleanup_exported_canvas_nodes(created_nodes)
        print("[CLEANUP] Canvas temporary nodes cleared.", flush=True)


if __name__ == "__main__":
    main()
