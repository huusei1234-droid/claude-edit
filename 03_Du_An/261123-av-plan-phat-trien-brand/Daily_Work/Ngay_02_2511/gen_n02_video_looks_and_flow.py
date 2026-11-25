# -*- coding: utf-8 -*-
"""
Ngày 02 (25/11/2026) — Tạo 5 Ảnh Diện Mạo 9:16 TP. Nha Trang (ChatGPT HTPM, song song 3 tab)
+ 20 Clip Video AI 9:16 (Google Flow Ultra, chế độ Thành phần / Ingredients, song song 4 tab,
TỐI ĐA 1 HỘP THẬT IS-NET / 1 PROMPT FLOW — 0% SAI SẢN PHẨM!) + Xuất bảng QC 20 clip thô.
"""
import os, sys, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

WORK = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_02_2511")
LOOKS_DIR = WORK / "04_Video_Looks_9x16"
CLIPS_DIR = WORK / "05_Flow_Raw_Clips"
LOOKS_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

MASTER_FACE = r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\01_Mau_USP_Goc\AV_MODEL_MASTER_SHEET.jpg"
CUTOUT_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG")
BOX_PRO = str(CUTOUT_DIR / "av01_protein_a.png")
BOX_BOJ = str(CUTOUT_DIR / "av02_bojomi_b.png")
BOX_CUR = str(CUTOUT_DIR / "av04_curcumilk_b.png")
BOX_COL = str(CUTOUT_DIR / "av03_collamela_b.png")

LOOK_LOCK = (
    "CRITICAL IDENTITY LOCK: Exact same 27-year-old Vietnamese woman's face, oval jawline, bright dark almond eyes, "
    "soft rose lips, fair luminous skin, and warm radiant smile from the reference image. "
    "Vertical 9:16 editorial commercial portrait, centered medium-full framing, clean natural lighting in sunny Nha Trang coastal Vietnam. "
    "ZERO text, ZERO words, ZERO product boxes, ZERO logos, ZERO watermarks. Photorealistic 85mm commercial photography."
)

LOOK_SPECS = [
    (
        "N02_LOOK1_AVP_GYM_9x16.png", "n02_lk1_avp",
        LOOK_LOCK + " OUTFIT 1: Sleek heather-grey Pilates crop top and matching high-waisted athletic leggings, white fabric headband on high ponytail, pearl studs, white smartwatch. "
        "LOCATION: Sunlit modern rooftop yoga terrace overlooking sparkling turquoise Nha Trang bay with palm fronds in soft bokeh."
    ),
    (
        "N02_LOOK2_BOJOMI_RUN5_9x16.png", "n02_lk2_boj",
        LOOK_LOCK + " OUTFIT 2: Fresh mint-green breathable athletic running singlet, crisp white pleated running skort, sleek white sun visor cap over braided ponytail, sport smartwatch, white running shoes. "
        "LOCATION: Golden morning coastal boulevard Pham Van Dong in Nha Trang lined with coconut palms and sunlit blue sea."
    ),
    (
        "N02_LOOK3_KID1Y_CREAM_9x16.png", "n02_lk3_kid",
        LOOK_LOCK + " OUTFIT 3: Elegant ivory-cream linen midi dress with pastel sage-mint waist bow ribbon, half-up wavy dark brown hair with pearl clip, delicate gold bracelet. "
        "LOCATION: Bright modern sunlit ocean-view apartment living room & white marble kitchen in Nha Trang overlooking blue sea."
    ),
    (
        "N02_LOOK4_CURCU_15H_9x16.png", "n02_lk4_cur",
        LOOK_LOCK + " OUTFIT 4: Chic olive-sage sleeveless linen midi dress, delicate gold pendant necklace, soft loose waves dark brown hair, classic rose-gold watch. "
        "LOCATION: Bright seaside modern office lounge & cafe desk overlooking sunlit Nha Trang bay at 3 PM golden afternoon light."
    ),
    (
        "N02_LOOK5_COLLA_TET_9x16.png", "n02_lk5_col",
        LOOK_LOCK + " OUTFIT 5: Crisp ivory silk blouse layered under a light cream knit vest, glowing porcelain skin, pearl drop earrings, sleek low bun with soft strands. "
        "LOCATION: Luxury golden sunset terrace overlooking Nha Trang bay with warm coral sky and blooming tropical pink bougainvillea."
    ),
]

NO_TALK = "ZERO lip movement, ZERO talking, closed gentle warm smile, smooth cinematic 24fps gimbal camera motion, crisp realistic skin & fabric physics, ZERO text overlays, ZERO distorted hands."


def get_flow_specs(lk_nodes: dict, box_nodes: dict):
    # Each video has 4 crisp fresh Nha Trang shots (s01..s04); MAX 1 box per Flow prompt (V3 has 0 boxes in Flow — real dual IS-Net cutouts composited in HyperFrames!)
    return [
        # --- V1: AV PROTEIN (Gym Rooftop Nha Trang) ---
        {
            "file": "v1_s01.mp4", "out_title": "n02_v1_s01", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"Cinematic 9:16 commercial shot of the Vietnamese woman in heather-grey Pilates crop top and leggings stretching gracefully on a sunlit rooftop terrace overlooking turquoise Nha Trang bay and palms, morning golden sun flare, smooth slow push-in. {NO_TALK}",
        },
        {
            "file": "v1_s02.mp4", "out_title": "n02_v1_s02", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"Close-medium 9:16 lifestyle shot of the same woman in heather-grey Pilates outfit pouring cool clear water into a clean glass shaker and gently swirling creamy light-beige plant protein shake on a bright outdoor counter overlooking Nha Trang sea, sunlit droplets sparkling. {NO_TALK}",
        },
        {
            "file": "v1_s03.mp4", "out_title": "n02_v1_s03", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk1_avp"], "extra_ref_node_ids": [box_nodes["pro"]],
            "motion_prompt": f"High-end 9:16 commercial hero shot of the same woman in heather-grey Pilates set standing on sunlit Nha Trang rooftop terrace, naturally holding the EXACT green-and-cream AV PROTEIN box from the second reference image facing clearly toward camera beside a glass of creamy shake, subtle gentle push-in, exact packaging preserved cleanly. {NO_TALK}",
        },
        {
            "file": "v1_s04.mp4", "out_title": "n02_v1_s04", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"Radiant 9:16 lifestyle shot of the same woman in heather-grey Pilates outfit taking a refreshing sip from a clean glass of creamy beige plant protein drink and smiling brightly with energized posture against sunlit Nha Trang bay breeze. {NO_TALK}",
        },

        # --- V2: BOJOMI RUN #5 (Mint Running Set Pham Van Dong Nha Trang) ---
        {
            "file": "v2_s01.mp4", "out_title": "n02_v2_s01", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"Dynamic 9:16 cinematic commercial tracking shot of the Vietnamese woman in mint-green running tank, white skort, and white visor jogging lightly along sunlit Pham Van Dong seaside promenade in Nha Trang with coconut palms and sparkling turquoise ocean behind, golden morning rays. {NO_TALK}",
        },
        {
            "file": "v2_s02.mp4", "out_title": "n02_v2_s02", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"Crisp 9:16 commercial close-medium shot of the same woman in mint-green running tank at a sunlit seaside bench cafe in Nha Trang stirring a smooth creamy warm vanilla cereal drink in a clear glass cup with a silver spoon, delicate warm steam rising in morning light. {NO_TALK}",
        },
        {
            "file": "v2_s03.mp4", "out_title": "n02_v2_s03", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk2_boj"], "extra_ref_node_ids": [box_nodes["boj"]],
            "motion_prompt": f"High-end 9:16 commercial hero shot of the same woman in mint-green running outfit standing by Nha Trang coastal palm promenade, holding the EXACT white-and-emerald BOJOMI box from the second reference image facing clearly toward camera with a warm refreshed post-run smile, exact box design preserved. {NO_TALK}",
        },
        {
            "file": "v2_s04.mp4", "out_title": "n02_v2_s04", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"Joyful 9:16 lifestyle shot of the same woman in mint-green running outfit and white visor sipping a warm vanilla drink and looking out over the sparkling blue Nha Trang sea with gentle ocean breeze moving her ponytail. {NO_TALK}",
        },

        # --- V3: COMBO BE 1 TUOI+ (Ivory Cream Dress Nha Trang Apartment — ZERO dual boxes in Flow!) ---
        {
            "file": "v3_s01.mp4", "out_title": "n02_v3_s01", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk3_kid"], "extra_ref_node_ids": None,
            "motion_prompt": f"Warm sunlit 9:16 commercial shot of the Vietnamese woman in ivory-cream linen midi dress with sage ribbon bow walking gently across her bright luxury ocean-view living room in Nha Trang, floor-to-ceiling windows showing sunny blue sea, tender caring smile, smooth slow dolly-in. {NO_TALK}",
        },
        {
            "file": "v3_s02.mp4", "out_title": "n02_v3_s02", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk3_kid"], "extra_ref_node_ids": None,
            "motion_prompt": f"Bright 9:16 lifestyle shot of the same woman in ivory-cream linen dress standing at a clean white marble kitchen island overlooking sunny Nha Trang bay, placing two neat minimalist glass cups side by side with calm attentive smile, golden morning sunbeams. {NO_TALK}",
        },
        {
            "file": "v3_s03.mp4", "out_title": "n02_v3_s03", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk3_kid"], "extra_ref_node_ids": [box_nodes["pro"]],
            "motion_prompt": f"Clean 9:16 commercial shot of the same woman in ivory-cream linen dress in sunlit Nha Trang kitchen pouring cool water into a small glass of smooth plant protein milk with the EXACT AV PROTEIN box from the second reference standing neatly on the marble counter beside her, soft natural sunlight. {NO_TALK}",
        },
        {
            "file": "v3_s04.mp4", "out_title": "n02_v3_s04", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk3_kid"], "extra_ref_node_ids": [box_nodes["boj"]],
            "motion_prompt": f"Warm afternoon 9:16 commercial shot of the same woman in ivory-cream linen dress in sunlit Nha Trang apartment gently stirring a cozy warm glass of creamy vanilla cereal milk with the EXACT BOJOMI box from the second reference standing cleanly on the marble counter beside her, golden afternoon glow. {NO_TALK}",
        },

        # --- V4: CURCUMILK 15H (Olive Sage Dress Nha Trang Sea-View Cafe/Office) ---
        {
            "file": "v4_s01.mp4", "out_title": "n02_v4_s01", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk4_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"Golden 3 PM 9:16 cinematic commercial shot of the Vietnamese woman in olive-sage linen midi dress sitting at a bright wooden workspace desk by a large glass window overlooking sunlit Nha Trang ocean, pausing calmly from her sleek laptop and smiling softly in warm golden afternoon light. {NO_TALK}",
        },
        {
            "file": "v4_s02.mp4", "out_title": "n02_v4_s02", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk4_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"Tactile 9:16 commercial shot of the same woman in olive-sage linen dress gently stirring a warm ceramic mug of golden creamy vanilla turmeric milk on a bright oak desk with sunlit Nha Trang bay softly blurred behind, silky golden swirl and gentle warm steam. {NO_TALK}",
        },
        {
            "file": "v4_s03.mp4", "out_title": "n02_v4_s03", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk4_cur"], "extra_ref_node_ids": [box_nodes["cur"]],
            "motion_prompt": f"Premium 9:16 commercial hero shot of the same woman in olive-sage linen dress at the bright Nha Trang seaside desk holding the EXACT cream-and-gold CURCUMILK PHYTO box from the second reference image facing clearly toward camera next to her warm golden mug, exact box label preserved. {NO_TALK}",
        },
        {
            "file": "v4_s04.mp4", "out_title": "n02_v4_s04", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk4_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"Serene 9:16 lifestyle shot of the same woman in olive-sage linen dress taking a cozy soothing sip of warm golden turmeric vanilla milk by the bright Nha Trang ocean window, relaxed content smile bathed in 3 PM amber sunlight. {NO_TALK}",
        },

        # --- V5: COLLAMELA DON TET (Ivory Silk + Cream Vest Nha Trang Sunset Terrace) ---
        {
            "file": "v5_s01.mp4", "out_title": "n02_v5_s01", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk5_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"Luxury 9:16 beauty commercial shot of the Vietnamese woman in crisp ivory silk blouse and cream knit vest on a golden sunset terrace overlooking Nha Trang bay with pink tropical bougainvillea, gently touching her radiant dewy cheek with a luminous festive smile, dreamy sunset glow. {NO_TALK}",
        },
        {
            "file": "v5_s02.mp4", "out_title": "n02_v5_s02", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk5_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"Crisp 9:16 beauty lifestyle shot of the same woman in ivory silk shirt and cream vest swirling a sparkling crystal glass of chilled translucent rosy-peach collagen drink in warm golden Nha Trang sunset light, refreshing clarity and shimmering reflections. {NO_TALK}",
        },
        {
            "file": "v5_s03.mp4", "out_title": "n02_v5_s03", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk5_col"], "extra_ref_node_ids": [box_nodes["col"]],
            "motion_prompt": f"High-end 9:16 beauty hero shot of the same woman in ivory silk blouse and cream knit vest on the Nha Trang sunset terrace holding the EXACT emerald-and-white COLLAMELA box from the second reference image facing clearly toward camera beside her chilled peach glass, exact packaging preserved cleanly. {NO_TALK}",
        },
        {
            "file": "v5_s04.mp4", "out_title": "n02_v5_s04", "seconds": 5,
            "ref_img_node_id": lk_nodes["n02_lk5_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"Radiant 9:16 beauty commercial close-medium shot of the same woman in ivory silk blouse and cream vest taking a graceful sip of the rosy-peach collagen drink and smiling luminously with glowing smooth skin against golden Nha Trang bay twilight. {NO_TALK}",
        },
    ]


def build_raw_qc_sheet():
    clips = sorted(CLIPS_DIR.glob("v*_s0*.mp4"))
    if not clips:
        return
    cols, rows = 4, 5
    tw, th = 270, 480
    sheet = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 34) + 16), (14, 18, 24))
    draw = ImageDraw.Draw(sheet)
    tmp = WORK / "_tmp_raw_qc.png"
    for idx, cp in enumerate(clips[:20]):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.2", "-i", str(cp), "-frames:v", "1", str(tmp)], check=True)
        im = Image.open(tmp).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x = (idx % cols) * (tw + 16) + 16
        y = (idx // cols) * (th + 34) + 16
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + th + 6), cp.name, fill=(255, 232, 120))
    tmp.unlink(missing_ok=True)
    out = WORK / "QA_N02_20_RawClips.jpg"
    sheet.save(out, quality=90)
    print(f"[RAW QC SHEET] {out}", flush=True)


def main():
    # Step A: Generate 5 9:16 Nha Trang Look Anchors (if missing)
    todo_looks = [(fn, tag, pr) for fn, tag, pr in LOOK_SPECS if not (LOOKS_DIR / fn).exists()]
    if todo_looks:
        face_nid = arv.stage_local_ref_image_once(MASTER_FACE, ref_tag="av_face_n02_916")
        tmp_nodes = [face_nid]
        try:
            res = arv.generate_ref_images_parallel_batch(
                [{"prompt": pr, "ref_tag": tag, "ratio": "9:16", "reference_node_ids": [face_nid]} for fn, tag, pr in todo_looks],
                max_workers=3,
            )
            exp = {}
            for (fn, _, _), (_, nid, prov) in zip(todo_looks, res):
                tmp_nodes.append(nid)
                exp[nid] = str(LOOKS_DIR / fn)
                print(f"[LOOK 9x16] {fn} via {prov}", flush=True)
            arv.export_canvas_nodes_to_files(exp)
        finally:
            arv.cleanup_exported_canvas_nodes(tmp_nodes)

    # Step B: Stage 5 Look Anchors + 4 Real IS-Net Product Boxes & Generate missing Flow clips (4-way parallel!)
    stage_nodes = []
    lk_nodes = {}
    for fn, tag, _ in LOOK_SPECS:
        nid = arv.stage_local_ref_image_once(str(LOOKS_DIR / fn), ref_tag=tag)
        lk_nodes[tag] = nid
        stage_nodes.append(nid)

    box_nodes = {}
    for bk, bp in [("pro", BOX_PRO), ("boj", BOX_BOJ), ("cur", BOX_CUR), ("col", BOX_COL)]:
        nid = arv.stage_local_ref_image_once(bp, ref_tag=f"box_{bk}_n02")
        box_nodes[bk] = nid
        stage_nodes.append(nid)

    all_vspecs = get_flow_specs(lk_nodes, box_nodes)
    todo_vids = [sp for sp in all_vspecs if not (CLIPS_DIR / sp["file"]).exists() or (CLIPS_DIR / sp["file"]).stat().st_size < 100_000]
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    def _run_one(sp, delay=0.0):
        if delay > 0:
            time.sleep(delay)
        vnid, prov = arv.generate_video_with_ref(
            motion_prompt=sp["motion_prompt"],
            ref_img_node_id=sp["ref_img_node_id"],
            out_title=sp["out_title"],
            ratio="9:16",
            seconds=int(sp.get("seconds", 5)),
            video_mode="reference",
            extra_ref_node_ids=sp.get("extra_ref_node_ids"),
            timeout_per_tier=390,
        )
        return sp, vnid, prov

    all_vid_nodes = []
    try:
        # Process in chunks of 4 (1 video at a time) at max_workers=3, exporting immediately after each chunk!
        failed_specs = []
        for ci in range(0, len(todo_vids), 4):
            chunk = todo_vids[ci : ci + 4]
            print(f"[FLOW CHUNK {ci//4 + 1}] Running {len(chunk)} clips: {[c['file'] for c in chunk]}", flush=True)
            exp_chunk = {}
            chunk_nodes = []
            with ThreadPoolExecutor(max_workers=3) as pool:
                futs = {pool.submit(_run_one, sp, (i % 3) * 2.5): sp for i, sp in enumerate(chunk)}
                for f in as_completed(futs):
                    sp = futs[f]
                    try:
                        _, vnid, prov = f.result()
                        exp_chunk[vnid] = str(CLIPS_DIR / sp["file"])
                        chunk_nodes.append(vnid)
                        all_vid_nodes.append(vnid)
                        print(f"[FLOW OK] {sp['file']} via {prov} (node={vnid})", flush=True)
                    except Exception as e:
                        print(f"[FLOW RETRY QUEUED] {sp['file']}: {e}", flush=True)
                        failed_specs.append(sp)
            if exp_chunk:
                exported = arv.export_canvas_nodes_to_files(exp_chunk, timeout_s=240)
                print(f"[EXPORTED CHUNK] {len(exported)}/{len(exp_chunk)} clips saved to disk.", flush=True)
                arv.cleanup_exported_canvas_nodes(chunk_nodes)

        # Retry any transient failures sequentially (concurrency=1) up to 2 attempts
        for attempt in (1, 2):
            still_missing = [sp for sp in all_vspecs if not (CLIPS_DIR / sp["file"]).exists() or (CLIPS_DIR / sp["file"]).stat().st_size < 100_000]
            if not still_missing:
                break
            print(f"[RETRY PASS {attempt}] {len(still_missing)} clips: {[s['file'] for s in still_missing]}", flush=True)
            for sp in still_missing:
                try:
                    time.sleep(2.0)
                    _, vnid, prov = _run_one(sp, 0.0)
                    arv.export_canvas_nodes_to_files({vnid: str(CLIPS_DIR / sp["file"])}, timeout_s=240)
                    arv.cleanup_exported_canvas_nodes([vnid])
                    print(f"[RETRY OK] {sp['file']} via {prov}", flush=True)
                except Exception as e:
                    print(f"[RETRY ERR] {sp['file']}: {e}", flush=True)
    finally:
        arv.cleanup_exported_canvas_nodes(stage_nodes)

    have = [sp["file"] for sp in all_vspecs if (CLIPS_DIR / sp["file"]).exists() and (CLIPS_DIR / sp["file"]).stat().st_size >= 100_000]
    print(f"[FLOW FINAL COUNT] {len(have)}/20 clips ready on disk.", flush=True)
    build_raw_qc_sheet()
    if len(have) < 20:
        raise RuntimeError(f"Missing {20 - len(have)} clips after retries!")
    print("\n=== ALL 5 N02 LOOKS & 20 FLOW CLIPS READY! ===", flush=True)


if __name__ == "__main__":
    main()
