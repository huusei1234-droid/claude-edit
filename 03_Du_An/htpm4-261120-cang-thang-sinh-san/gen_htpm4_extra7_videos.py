import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

PROJ  = r"d:\AI\full studio\output\htpm4-261120"
MEDIA = os.path.join(PROJ, "media")
CHECK = os.path.join(PROJ, "check")
os.makedirs(MEDIA, exist_ok=True)
os.makedirs(CHECK, exist_ok=True)

FONTS_SRC      = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
LUT_HARMONIZER = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"
FONT_BOLD      = os.path.join(FONTS_SRC, "BeVietnamPro-Bold.ttf")

EXTRA_SCENES = [
    {
        "scene_id": "htpm4_01b",
        "dest": os.path.join(MEDIA, "st_01b_sleepless_night.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_01b.png"),
        "ratio": "16:9",
        "seconds": 4,
        "image_prompt": (
            "Cinematic editorial bedroom photography at 2 AM in soft moody moonlit blue and warm bedside lamp tones: "
            "a tired 29-year-old Vietnamese woman in silk pajamas sitting awake on her bed hugging a pillow with sleepless exhaustion, 50mm f/1.8."
        ),
        "motion_prompt": (
            "Slow stabilized cinema dolly-in across the quiet dim bedroom as she looks down tiredly with sleepless fatigue."
        ),
    },
    {
        "scene_id": "htpm4_01c",
        "dest": os.path.join(MEDIA, "st_01c_office_pressure.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_01c.png"),
        "ratio": "16:9",
        "seconds": 4,
        "image_prompt": (
            "Editorial modern office lifestyle photography: a 30-year-old Vietnamese woman in a smart ivory blazer sitting overwhelmed "
            "behind stacks of folders and a glowing monitor in late afternoon light, resting her palm against her forehead under heavy work pressure, 85mm lens."
        ),
        "motion_prompt": (
            "Gentle slow camera pan-in as she closes her eyes briefly under mental pressure and exhales softly."
        ),
    },
    {
        "scene_id": "htpm4_02b",
        "dest": os.path.join(MEDIA, "st_02b_irregular_cycle.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_02b.png"),
        "ratio": "16:9",
        "seconds": 4,
        "image_prompt": (
            "Soft sunlit bedroom lifestyle photography: a 29-year-old Vietnamese woman in a pastel rose knit cardigan sitting on the edge of her bed "
            "holding a warm herbal heating pad gently against her lower abdomen with a concerned thoughtful expression, soft natural window light, 85mm."
        ),
        "motion_prompt": (
            "Smooth slow cinema push-in as she holds the warm pad over her lower abdomen with a gentle thoughtful look."
        ),
    },
    {
        "scene_id": "htpm4_02c",
        "dest": os.path.join(MEDIA, "st_02c_ovulation_follicle.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_02c.png"),
        "ratio": "16:9",
        "seconds": 4,
        "image_prompt": (
            "Luxury 3D medical scientific macro render in pastel pearl, rose-quartz and soft sapphire light: "
            "a luminous translucent golden ovum cell surrounded by delicate shimmering endocrine light waves symbolizing ovulation health, ultra-clean 8k."
        ),
        "motion_prompt": (
            "Graceful slow macro orbital camera drift around the luminous translucent golden ovum cell as delicate light waves shimmer."
        ),
    },
    {
        "scene_id": "htpm4_03b",
        "dest": os.path.join(MEDIA, "st_03b_garden_breathing.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_03b.png"),
        "ratio": "16:9",
        "seconds": 4,
        "image_prompt": (
            "Bright editorial morning wellness photography: a serene 30-year-old Vietnamese woman in breathable cream linen seated peacefully "
            "on a wooden garden terrace surrounded by lush green plants and golden morning sunbeams, eyes gently closed in calm mindful breathing, 85mm."
        ),
        "motion_prompt": (
            "Slow smooth cinema tracking shot through warm morning sunbeams as she inhales calmly with a serene peaceful expression."
        ),
    },
    {
        "scene_id": "htpm4_04b",
        "dest": os.path.join(MEDIA, "st_04b_selfcare_glow.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_04b.png"),
        "ratio": "16:9",
        "seconds": 4,
        "image_prompt": (
            "Sunlit luxury home wellness photography: a radiant 29-year-old Vietnamese woman with glowing rosy skin in an ivory blouse "
            "pouring warm golden chamomile herbal tea from a glass teapot in a bright airy kitchen with fresh flowers, 85mm shallow depth of field."
        ),
        "motion_prompt": (
            "Smooth slow cinema dolly-in as warm golden herbal tea pours gently into the glass cup and she smiles peacefully."
        ),
    },
    {
        "scene_id": "htpm4_04c",
        "dest": os.path.join(MEDIA, "st_04c_happy_couple_garden.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_04c.png"),
        "ratio": "16:9",
        "seconds": 4,
        "image_prompt": (
            "Warm romantic lifestyle photography of a happy healthy young Vietnamese husband and wife around 30 years old in coordinated white and beige linen "
            "walking hand-in-hand through a sunlit blooming green garden in golden hour light, tender hopeful closed-lip smiles, 85mm f/1.8."
        ),
        "motion_prompt": (
            "Graceful slow stabilized cinema tracking glide in golden garden sunlight as the couple walks hand-in-hand with warm serene smiles."
        ),
    },
]

# Filter only scenes not yet rendered on disk
todo = [sc for sc in EXTRA_SCENES if not os.path.exists(sc["dest"])]
print(f"[HTPM4 Extra] Generating {len(todo)}/7 new scenes via Streaming Pipeline (ChatGPT HTPM -> Flow Ingredients 4s)...", flush=True)

if todo:
    res_list = arv.generate_scene_assets_pipelined(todo, max_workers=1)
    exp_map = {}
    cleanup_ids = []
    for sc, r in zip(todo, res_list):
        sc["img_provider"] = r["img_provider"]
        sc["vid_provider"] = r["vid_provider"]
        exp_map[r["img_node_id"]] = sc["ref_dest"]
        exp_map[r["vid_node_id"]] = sc["dest"] + ".raw.mp4"
        cleanup_ids.extend([r["img_node_id"], r["vid_node_id"]])

    _, end_nodes = arv.get_canvas_state()
    for nid, n in end_nodes.items():
        if "htpm4_" in (n.get("title") or "").lower():
            cleanup_ids.append(nid)

    arv.export_canvas_nodes_to_files(exp_map, timeout_s=240)
    arv.cleanup_exported_canvas_nodes(cleanup_ids)

    lut_local = os.path.join(MEDIA, "_harm.cube")
    shutil.copy2(LUT_HARMONIZER, lut_local)
    for sc in todo:
        raw_v = sc["dest"] + ".raw.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", "0.20", "-i", raw_v,
            "-r", "30", "-fps_mode", "cfr", "-an",
            "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_harm.cube[bg];[a][bg]blend=all_expr=A*0.34+B*0.66[v]",
            "-map", "[v]",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
            sc["dest"]
        ], cwd=MEDIA, check=True)
        if os.path.exists(raw_v):
            os.remove(raw_v)
        print("READY_EXTRA_CLIP ->", sc["dest"], f"(Img:{sc['img_provider']} -> Vid:{sc['vid_provider']})", flush=True)
    if os.path.exists(lut_local):
        os.remove(lut_local)

# Build 11-clip full visual QC sheet!
all_clips = [
    ("01A", os.path.join(MEDIA, "st_01_chronic_stress.mp4")),
    ("01B", os.path.join(MEDIA, "st_01b_sleepless_night.mp4")),
    ("01C", os.path.join(MEDIA, "st_01c_office_pressure.mp4")),
    ("02A", os.path.join(MEDIA, "st_02_hormone_balance.mp4")),
    ("02B", os.path.join(MEDIA, "st_02b_irregular_cycle.mp4")),
    ("02C", os.path.join(MEDIA, "st_02c_ovulation_follicle.mp4")),
    ("03A", os.path.join(MEDIA, "st_03_nourish_relax.mp4")),
    ("03B", os.path.join(MEDIA, "st_03b_garden_breathing.mp4")),
    ("04A", os.path.join(MEDIA, "st_04_radiant_vitality.mp4")),
    ("04B", os.path.join(MEDIA, "st_04b_selfcare_glow.mp4")),
    ("04C", os.path.join(MEDIA, "st_04c_happy_couple_garden.mp4")),
]
sheet = Image.new("RGB", (1360, 740), (244, 246, 252))
fnt = ImageFont.truetype(FONT_BOLD, 20)
for i, (lbl, vp) in enumerate(all_clips):
    x0 = (i % 4) * 336 + 14
    y0 = (i // 4) * 242 + 12
    tjpg = vp + ".qc.jpg"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.4", "-i", vp, "-frames:v", "1", tjpg], check=True)
    im = Image.open(tjpg).convert("RGB"); im.thumbnail((318, 195))
    sheet.paste(im, (x0, y0 + 28))
    ImageDraw.Draw(sheet).text((x0, y0), f"Clip {lbl} • 0% Loop", font=fnt, fill=(20, 24, 38))
    os.remove(tjpg)

qc_p = os.path.join(CHECK, "flow_htpm4_all11_qc.jpg")
sheet.save(qc_p, quality=92)
print("SAVED_ALL11_QC_SHEET ->", qc_p, flush=True)
