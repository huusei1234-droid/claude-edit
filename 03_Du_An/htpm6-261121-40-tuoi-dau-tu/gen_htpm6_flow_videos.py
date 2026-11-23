import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

PROJ  = r"d:\AI\full studio\output\htpm6-261121"
MEDIA = os.path.join(PROJ, "media")
CHECK = os.path.join(PROJ, "check")
os.makedirs(MEDIA, exist_ok=True)
os.makedirs(CHECK, exist_ok=True)

FONTS_SRC      = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
LUT_HARMONIZER = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"
FONT_BOLD      = os.path.join(FONTS_SRC, "BeVietnamPro-Bold.ttf")

# Stage actual speaker portrait from HTPM.mp4 so ALL 11 AI scenes feature the exact same mature Vietnamese woman!
SPEAKER_REF_PATH = os.path.join(PROJ, "aroll", "speaker_ref.png")
speaker_nid = arv.stage_local_ref_image_once(SPEAKER_REF_PATH, ref_tag="htpm6_speaker_anchor")
print(f"[Anchor] Staged HTPM6 speaker reference node -> {speaker_nid}", flush=True)

SCENES = [
    # --- WINDOW 1 (16.22 - 26.26s): 3 Luxury Illusions vs Inner Health ---
    {
        "id": "inv01a",
        "ref_tag": "ref_htpm6_01a",
        "vid_title": "OUT_htpm6_01a",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "inv_01a_bag_sleepless.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_01a.png"),
        "img_prompt": (
            "Using the exact same 38-year-old Vietnamese woman from the reference image: moody night bedroom photography at 2 AM where a luxury quilted leather designer handbag "
            "sits prominently on the nightstand in warm lamp light, while she sits awake in silk pajamas rubbing her temple with sleepless exhaustion, 50mm f/1.8."
        ),
        "vid_prompt": (
            "Slow cinema rack-focus push-in past the luxury designer handbag on the nightstand toward the tired sleepless Vietnamese woman sitting awake in bed with closed lips."
        ),
    },
    {
        "id": "inv01b",
        "ref_tag": "ref_htpm6_01b",
        "vid_title": "OUT_htpm6_01b",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "inv_01b_dress_fatigue.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_01b.png"),
        "img_prompt": (
            "Using the exact same 38-year-old Vietnamese woman from the reference image: luxury walk-in dressing room with glamorous designer dresses hanging on a boutique rack, "
            "while she sits slumped on a velvet bench holding her shoulder with physical fatigue and low energy, soft afternoon window light, 85mm."
        ),
        "vid_prompt": (
            "Smooth slow cinema tracking glide past the rack of designer dresses as the fatigued Vietnamese woman exhales quietly with tired posture and closed lips."
        ),
    },
    {
        "id": "inv01c",
        "ref_tag": "ref_htpm6_01c",
        "vid_title": "OUT_htpm6_01c",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "inv_01c_makeup_tired.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_01c.png"),
        "img_prompt": (
            "Using the exact same 38-year-old Vietnamese woman from the reference image sitting before a glowing Hollywood vanity mirror surrounded by luxury cosmetics and makeup brushes, "
            "looking thoughtfully at her reflection with subtle inner fatigue beneath her makeup, warm editorial lighting, 85mm shallow DOF."
        ),
        "vid_prompt": (
            "Gentle slow cinema push-in toward the glowing vanity mirror as she lowers the makeup brush and looks thoughtfully at her reflection with closed lips."
        ),
    },
    # --- WINDOW 2 (26.52 - 35.54s): 6 Core Investments (Sleep, Nutrition, Fitness, Gyn Health, Knowledge) ---
    {
        "id": "inv02a",
        "ref_tag": "ref_htpm6_02a",
        "vid_title": "OUT_htpm6_02a",
        "ratio": "16:9",
        "seconds": 5,
        "dest": os.path.join(MEDIA, "inv_02a_sleep_nutrition.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_02a.png"),
        "img_prompt": (
            "Using the exact same radiant 38-year-old Vietnamese woman from the reference image in an airy sunlit morning dining room, "
            "enjoying a nutritious wholesome breakfast of fresh berries, avocado, nuts and warm herbal tea after a restful sleep, glowing healthy skin, 85mm."
        ),
        "vid_prompt": (
            "Warm slow cinema dolly-in through morning sunbeams as the refreshed Vietnamese woman holds her cup of warm herbal tea beside the healthy breakfast with a serene closed-lip smile."
        ),
    },
    {
        "id": "inv02b",
        "ref_tag": "ref_htpm6_02b",
        "vid_title": "OUT_htpm6_02b",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "inv_02b_fitness_knowledge.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_02b.png"),
        "img_prompt": (
            "Using the exact same healthy 38-year-old Vietnamese woman from the reference image in graceful cream loungewear sitting by a sunlit garden window, "
            "reading an illustrated women's wellness and endocrine health guide book with a calm knowledgeable smile, 85mm lens."
        ),
        "vid_prompt": (
            "Smooth slow cinema tracking shot in bright natural sunlight as she turns a page of the women's health book and nods gently with a calm smile."
        ),
    },
    # --- WINDOW 3 (45.70 - 56.58s): Love Your Body Early & Radiant at Every Age ---
    {
        "id": "inv03a",
        "ref_tag": "ref_htpm6_03a",
        "vid_title": "OUT_htpm6_03a",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "inv_03a_love_body_early.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_03a.png"),
        "img_prompt": (
            "Using the exact same serene 38-year-old Vietnamese woman from the reference image in a soft ivory linen dress standing in a sunlit green garden, "
            "placing both hands gently over her heart in warm self-care and gratitude for her healthy body, golden morning light, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Graceful slow cinema push-in through warm golden garden light as she holds both hands gently over her heart and breathes calmly with a tender smile."
        ),
    },
    {
        "id": "inv03b",
        "ref_tag": "ref_htpm6_03b",
        "vid_title": "OUT_htpm6_03b",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "inv_03b_vitality_yoga.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_03b.png"),
        "img_prompt": (
            "Using the exact same vibrant 38-year-old Vietnamese woman from the reference image in elegant white activewear practicing gentle morning yoga stretching "
            "on a sunlit wooden terrace surrounded by lush tropical greenery, toned healthy vitality, 85mm."
        ),
        "vid_prompt": (
            "Smooth slow cinema tracking shot across the sunlit garden terrace as she stretches her arms gracefully in calm morning yoga vitality."
        ),
    },
    {
        "id": "inv03c",
        "ref_tag": "ref_htpm6_03c",
        "vid_title": "OUT_htpm6_03c",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "inv_03c_confident_age.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_03c.png"),
        "img_prompt": (
            "Using the exact same poised 40-year-old Vietnamese woman from the reference image in a timeless cream v-neck dress walking gracefully along a sunlit garden pathway, "
            "radiating health, natural beauty and mature self-confidence, golden hour bokeh, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Cinematic slow-motion tracking glide in golden garden sunlight as she walks forward gracefully with a radiant confident closed-lip smile."
        ),
    },
    # --- WINDOW 4 (56.82 - 68.70s): Family Energy, Early Wisdom & 30-40+ Finale ---
    {
        "id": "inv04a",
        "ref_tag": "ref_htpm6_04a",
        "vid_title": "OUT_htpm6_04a",
        "ratio": "16:9",
        "seconds": 5,
        "dest": os.path.join(MEDIA, "inv_04a_family_energy.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_04a.png"),
        "img_prompt": (
            "Using the exact same radiant 38-year-old Vietnamese woman from the reference image in a sunlit modern home sharing fresh fruit and warm laughter "
            "with her loving Vietnamese husband and young daughter at the breakfast table, vibrant positive family energy, 50mm."
        ),
        "vid_prompt": (
            "Warm slow cinema pan across the sunlit family table as the radiant Vietnamese woman shares a joyful gentle smile with her husband and daughter."
        ),
    },
    {
        "id": "inv04b",
        "ref_tag": "ref_htpm6_04b",
        "vid_title": "OUT_htpm6_04b",
        "ratio": "16:9",
        "seconds": 5,
        "dest": os.path.join(MEDIA, "inv_04b_smart_woman.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_04b.png"),
        "img_prompt": (
            "Using the exact same confident 38-year-old Vietnamese woman from the reference image in a chic cream blazer working calmly at a sunlit wooden desk "
            "with a wellness planner and herbal tea, poised productive career confidence, 85mm."
        ),
        "vid_prompt": (
            "Smooth slow cinema push-in at the sunlit desk as she writes a note in her wellness planner and looks up with poised calm confidence."
        ),
    },
    {
        "id": "inv04c",
        "ref_tag": "ref_htpm6_04c",
        "vid_title": "OUT_htpm6_04c",
        "ratio": "16:9",
        "seconds": 5,
        "dest": os.path.join(MEDIA, "inv_04c_radiant_40_close.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm6_04c.png"),
        "img_prompt": (
            "Using the exact same glowing 40-year-old Vietnamese woman from the reference image in a cream v-neck dress standing amidst blooming garden flowers in golden hour light, "
            "luminous rosy skin, serene fulfilled smile embodying timeless feminine health and wisdom, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Graceful slow cinema dolly-in through golden garden sunbeams as a gentle breeze stirs the flowers and she smiles with radiant timeless confidence."
        ),
    },
]

lut_local = os.path.join(MEDIA, "_harm.cube")
shutil.copy2(LUT_HARMONIZER, lut_local)

# Process in safe 2-worker batches with immediate per-scene disk export so completed clips are persisted right away!
from concurrent.futures import ThreadPoolExecutor

PREFERRED_IMG_CHAIN = [
    ("ChatGPT", "chatgpt::chatgpt-image"),
    ("Google-Flow", "flow::flow-nano-banana-pro"),
    ("Gemini-2.1", "flow::flow-nano-banana-2-1"),
    ("Muse", "muse::muse-image"),
]

def build_one_scene(idx_sc):
    idx, sc = idx_sc
    if os.path.exists(sc["dest"]) and os.path.exists(sc["ref_dest"]):
        sc["img_provider"], sc["vid_provider"] = "Cached", "Cached"
        print(f"[{sc['id']}] Already on disk -> skipping!", flush=True)
        return []

    if os.path.exists(sc["ref_dest"]) and os.path.getsize(sc["ref_dest"]) > 60000:
        nid = arv.stage_local_ref_image_once(sc["ref_dest"], ref_tag=sc["ref_tag"])
        iprov = "DiskRef"
        print(f"[{sc['id']}] Reusing verified disk ref image -> {nid}", flush=True)
    else:
        cur_speaker_nid = arv.stage_local_ref_image_once(SPEAKER_REF_PATH, ref_tag="htpm6_speaker_anchor")
        nid, iprov = arv.generate_ref_image_4tier(
            prompt=sc["img_prompt"],
            ref_tag=sc["ref_tag"],
            ratio=sc["ratio"],
            reference_node_ids=[cur_speaker_nid],
            timeout_per_tier=180,
            preferred_chain=PREFERRED_IMG_CHAIN,
        )
        arv.export_canvas_nodes_to_files({nid: sc["ref_dest"]}, timeout_s=150)

    vnid, vprov = None, None
    for v_try in range(2):
        try:
            vnid, vprov = arv.generate_video_with_ref(
                motion_prompt=sc["vid_prompt"],
                ref_img_node_id=nid,
                out_title=f"{sc['vid_title']}_{v_try}",
                ratio=sc["ratio"],
                seconds=sc["seconds"],
                video_mode="reference",
                timeout_per_tier=360,
            )
            break
        except Exception as e:
            print(f"[{sc['id']}] Video attempt {v_try + 1} warning: {e}", flush=True)
            if v_try == 1:
                raise
            import time
            time.sleep(4)
            nid = arv.stage_local_ref_image_once(sc["ref_dest"], ref_tag=sc["ref_tag"])
    raw_v = sc["dest"] + ".raw.mp4"
    arv.export_canvas_nodes_to_files({vnid: raw_v}, timeout_s=180)

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

    sc["img_provider"], sc["vid_provider"] = iprov, vprov
    arv.cleanup_exported_canvas_nodes([nid, vnid])
    print(f"READY_HTPM6_CLIP -> {sc['dest']} (Img:{iprov} -> Vid:{vprov})", flush=True)
    return [nid, vnid]

for idx_sc in enumerate(SCENES):
    build_one_scene(idx_sc)

arv.cleanup_exported_canvas_nodes([arv.stage_local_ref_image_once(SPEAKER_REF_PATH, ref_tag="htpm6_speaker_anchor")])
if os.path.exists(lut_local):
    os.remove(lut_local)

# Build 11-clip visual QC contact sheet!
sheet = Image.new("RGB", (1360, 740), (244, 246, 252))
fnt = ImageFont.truetype(FONT_BOLD, 20)
for i, sc in enumerate(SCENES):
    x0 = (i % 4) * 336 + 14
    y0 = (i // 4) * 242 + 12
    tjpg = sc["dest"] + ".qc.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", sc["dest"], "-frames:v", "1", tjpg], check=True)
    im = Image.open(tjpg).convert("RGB"); im.thumbnail((318, 195))
    sheet.paste(im, (x0, y0 + 28))
    ImageDraw.Draw(sheet).text((x0, y0), f"{sc['id'].upper()} • {sc.get('img_provider','')}->{sc.get('vid_provider','')}", font=fnt, fill=(20, 24, 38))
    os.remove(tjpg)

qc_p = os.path.join(CHECK, "flow_htpm6_all11_qc.jpg")
sheet.save(qc_p, quality=92)
print("SAVED_HTPM6_ALL11_QC ->", qc_p, flush=True)
