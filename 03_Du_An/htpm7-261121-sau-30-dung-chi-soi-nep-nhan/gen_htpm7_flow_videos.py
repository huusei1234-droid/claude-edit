import os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

PROJ  = r"d:\AI\full studio\output\htpm7-261121"
MEDIA = os.path.join(PROJ, "media")
CHECK = os.path.join(PROJ, "check")
os.makedirs(MEDIA, exist_ok=True)
os.makedirs(CHECK, exist_ok=True)

FONTS_SRC      = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
LUT_HARMONIZER = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"
FONT_BOLD      = os.path.join(FONTS_SRC, "BeVietnamPro-Bold.ttf")

SPEAKER_REF_PATH = os.path.join(PROJ, "aroll", "speaker_ref.png")
speaker_nid = arv.stage_local_ref_image_once(SPEAKER_REF_PATH, ref_tag="htpm7_speaker_anchor")
print(f"[Anchor] Staged HTPM7 speaker reference node -> {speaker_nid}", flush=True)

SCENES = [
    {
        "id": "sk01a",
        "ref_tag": "ref_htpm7_01a",
        "vid_title": "OUT_htpm7_01a",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(5.0),
        "dest": os.path.join(MEDIA, "sk_01a_cycle_calendar.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_01a.png"),
        "img_prompt": (
            "Using the exact same 36-year-old Vietnamese woman from the reference image: sunlit bedroom vanity where luxury glass skincare serum and cream jars sit on the table, "
            "while she looks thoughtfully at a small monthly paper desk calendar holding a pen with a questioning expression about her irregular cycle, soft morning window light, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Slow cinema rack-focus glide past the glass skincare bottles on the vanity toward the thoughtful Vietnamese woman looking down at her monthly paper calendar with closed lips."
        ),
    },
    {
        "id": "sk01b",
        "ref_tag": "ref_htpm7_01b",
        "vid_title": "OUT_htpm7_01b",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(4.1),
        "dest": os.path.join(MEDIA, "sk_01b_sleep_fatigue.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_01b.png"),
        "img_prompt": (
            "Using the exact same 36-year-old Vietnamese woman from the reference image: moody warm bedroom night photography where she sits awake on the edge of her bed in cream silk pajamas, "
            "gently massaging her temple and shoulder with sleepless exhaustion and physical fatigue, warm bedside lamp glow, 50mm f/1.8."
        ),
        "vid_prompt": (
            "Gentle slow cinema push-in in warm bedside lamp light as the tired sleepless Vietnamese woman rests a hand on her temple and exhales quietly with closed lips."
        ),
    },
    {
        "id": "sk01c",
        "ref_tag": "ref_htpm7_01c",
        "vid_title": "OUT_htpm7_01c",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(4.5),
        "dest": os.path.join(MEDIA, "sk_01c_mood_discomfort.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_01c.png"),
        "img_prompt": (
            "Using the exact same 36-year-old Vietnamese woman from the reference image sitting on a cozy armchair by a window in soft overcast afternoon light, "
            "holding a warm ceramic mug with one hand resting gently near her lower abdomen in subtle physical discomfort and sensitive pensive mood, 85mm shallow DOF."
        ),
        "vid_prompt": (
            "Smooth slow cinema tracking shot by the window as the pensive Vietnamese woman looks out quietly with subtle inner discomfort and closed lips."
        ),
    },
    {
        "id": "sk02a",
        "ref_tag": "ref_htpm7_02a",
        "vid_title": "OUT_htpm7_02a",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(5.2),
        "dest": os.path.join(MEDIA, "sk_02a_age30_changes.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_02a.png"),
        "img_prompt": (
            "Using the exact same poised 36-year-old Vietnamese woman from the reference image in an ivory linen blouse standing beside a sunlit mirror surrounded by indoor plants, "
            "observing herself with calm self-awareness and gentle acceptance rather than worry, warm morning daylight, 85mm."
        ),
        "vid_prompt": (
            "Warm slow cinema dolly-in as the composed Vietnamese woman looks into the sunlit mirror and nods gently with calm self-understanding and closed lips."
        ),
    },
    {
        "id": "sk02b",
        "ref_tag": "ref_htpm7_02b",
        "vid_title": "OUT_htpm7_02b",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(5.3),
        "dest": os.path.join(MEDIA, "ref_htpm7_02b.png"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_02b.png"),
        "img_prompt": (
            "Using the exact same calm 36-year-old Vietnamese woman from the reference image sitting at a sunlit wooden table, placing her smartphone face-down beside a cup of herbal tea "
            "and taking a peaceful breath instead of worrying over internet health rumors, bright natural editorial lighting, 85mm."
        ),
        "vid_prompt": (
            "Smooth slow cinema push-in at the sunlit wooden table as she sets her smartphone face-down and breathes calmly with a reassured gentle smile."
        ),
    },
    {
        "id": "sk03a",
        "ref_tag": "ref_htpm7_03a",
        "vid_title": "OUT_htpm7_03a",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(3.3),
        "dest": os.path.join(MEDIA, "sk_03a_beyond_skin.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_03a.png"),
        "img_prompt": (
            "Using the exact same radiant 36-year-old Vietnamese woman from the reference image standing by an open garden window in soft cream attire, "
            "natural glowing skin illuminated by warm morning sunbeams, embodying authentic inner health beyond surface cosmetics, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Graceful slow cinema push-in through warm morning sunbeams as she turns toward the garden light with luminous natural health and a serene closed-lip smile."
        ),
    },
    {
        "id": "sk03b",
        "ref_tag": "ref_htpm7_03b",
        "vid_title": "OUT_htpm7_03b",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(3.0),
        "dest": os.path.join(MEDIA, "sk_03b_healthy_confident.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_03b.png"),
        "img_prompt": (
            "Using the exact same vibrant 36-year-old Vietnamese woman from the reference image in a modest cream linen top stretching her arms gently in morning sunlight "
            "on a wooden garden terrace surrounded by green foliage, healthy energy and radiant confidence, 85mm."
        ),
        "vid_prompt": (
            "Smooth slow cinema tracking glide across the sunlit garden terrace as she opens her arms gently in healthy morning vitality."
        ),
    },
    {
        "id": "sk03c",
        "ref_tag": "ref_htpm7_03c",
        "vid_title": "OUT_htpm7_03c",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(3.0),
        "dest": os.path.join(MEDIA, "sk_03c_comfortable_body.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_03c.png"),
        "img_prompt": (
            "Using the exact same serene 36-year-old Vietnamese woman from the reference image in a flowing cream linen dress walking peacefully along a sunlit green garden path, "
            "hands relaxed over her heart, feeling completely comfortable and joyful in her own body, golden hour bokeh, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Cinematic slow-motion tracking shot in golden garden sunlight as she walks gently with complete comfort, poise and a warm closed-lip smile."
        ),
    },
    {
        "id": "sk04a",
        "ref_tag": "ref_htpm7_04a",
        "vid_title": "OUT_htpm7_04a",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(4.0),
        "dest": os.path.join(MEDIA, "sk_04a_wisdom_30plus.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_04a.png"),
        "img_prompt": (
            "Using the exact same confident 36-year-old Vietnamese woman from the reference image in a smart navy-and-white collar dress sitting at a sunlit garden cafe table "
            "with a women's wellness journal and warm herbal tea, mature feminine wisdom and clarity, 85mm."
        ),
        "vid_prompt": (
            "Warm slow cinema push-in at the sunlit garden table as she closes her wellness journal gently and looks up with poised confident warmth."
        ),
    },
    {
        "id": "sk04b",
        "ref_tag": "ref_htpm7_04b",
        "vid_title": "OUT_htpm7_04b",
        "ratio": "16:9",
        "seconds": arv.calc_optimal_flow_seconds(4.0),
        "dest": os.path.join(MEDIA, "sk_04b_radiant_finale.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm7_04b.png"),
        "img_prompt": (
            "Using the exact same glowing 36-year-old Vietnamese woman from the reference image in her navy dress with white collar standing amidst lush sunlit garden foliage at golden hour, "
            "rosy healthy skin, warm inviting smile embodying timeless feminine health and confidence, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Graceful slow cinema dolly-in through golden garden bokeh as a gentle breeze moves her hair and she smiles with warm radiant confidence."
        ),
    },
]
# Fix sk02b dest typo check:
SCENES[4]["dest"] = os.path.join(MEDIA, "sk_02b_no_self_panic.mp4")

lut_local = os.path.join(MEDIA, "_harm.cube")
shutil.copy2(LUT_HARMONIZER, lut_local)

# Step 1: Harvest all 8 already-succeeded reference images on Canvas immediately + generate missing 2 (sk03b, sk04b)
ref_node_map = {}
for sc in SCENES:
    if os.path.exists(sc["ref_dest"]) and os.path.getsize(sc["ref_dest"]) > 4096:
        sc["img_provider"] = "CachedDisk"
        ref_node_map[sc["id"]] = arv.stage_local_ref_image_once(sc["ref_dest"], ref_tag=sc["ref_tag"])
    else:
        # generate_ref_image_4tier automatically reuses any existing verified Canvas node with title == ref_tag!
        nid, prov = arv.generate_ref_image_4tier(
            prompt=sc["img_prompt"],
            ref_tag=sc["ref_tag"],
            ratio=sc["ratio"],
            reference_node_ids=[speaker_nid],
            timeout_per_tier=210,
        )
        arv.export_canvas_nodes_to_files({nid: sc["ref_dest"]}, timeout_s=150)
        ref_node_map[sc["id"]] = nid
        sc["img_provider"] = prov
        print(f"[RefSaved] {sc['id']} -> {sc['ref_dest']} ({prov})", flush=True)

# Step 2: Generate & immediately persist each Flow video (max_workers=2 with 2-attempt safety retry, exact reference/Ingredients mode)
def build_one_video(idx_sc):
    idx, sc = idx_sc
    if os.path.exists(sc["dest"]) and os.path.getsize(sc["dest"]) > 8192:
        sc["vid_provider"] = "CachedDisk"
        print(f"[{sc['id']}] Video already on disk -> skipping!", flush=True)
        return
    if idx > 0:
        time.sleep((idx % 2) * 1.6)

    nid = ref_node_map[sc["id"]]
    last_e = None
    for attempt in range(2):
        try:
            vnid, vprov = arv.generate_video_with_ref(
                motion_prompt=sc["vid_prompt"],
                ref_img_node_id=nid,
                out_title=sc["vid_title"],
                ratio=sc["ratio"],
                seconds=sc["seconds"],
                video_mode="reference",
                timeout_per_tier=390,
            )
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
            sc["vid_provider"] = vprov
            arv.cleanup_exported_canvas_nodes([nid, vnid])
            print(f"READY_HTPM7_CLIP -> {sc['dest']} (Img:{sc.get('img_provider')} -> Vid:{vprov})", flush=True)
            return
        except Exception as e:
            last_e = e
            print(f"[{sc['id']}] Attempt {attempt+1} warning: {e} -> retrying in 8s...", flush=True)
            time.sleep(8)
    raise last_e

with ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(build_one_video, enumerate(SCENES)))

arv.cleanup_exported_canvas_nodes(list(ref_node_map.values()) + [speaker_nid])
if os.path.exists(lut_local):
    os.remove(lut_local)

sheet = Image.new("RGB", (1360, 740), (244, 246, 252))
fnt = ImageFont.truetype(FONT_BOLD, 20)
for i, sc in enumerate(SCENES):
    x0 = (i % 4) * 336 + 14
    y0 = (i // 4) * 242 + 12
    tjpg = sc["dest"] + ".qc.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.2", "-i", sc["dest"], "-frames:v", "1", tjpg], check=True)
    im = Image.open(tjpg).convert("RGB"); im.thumbnail((318, 195))
    sheet.paste(im, (x0, y0 + 28))
    ImageDraw.Draw(sheet).text((x0, y0), f"{sc['id'].upper()} • {sc.get('img_provider','')}->{sc.get('vid_provider','')}", font=fnt, fill=(20, 24, 38))
    os.remove(tjpg)

qc_p = os.path.join(CHECK, "flow_htpm7_all10_qc.jpg")
sheet.save(qc_p, quality=92)
print("SAVED_HTPM7_ALL10_QC ->", qc_p, flush=True)
