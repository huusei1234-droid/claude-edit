import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

PROJ  = r"d:\AI\full studio\output\htpm4-261120"
MEDIA = os.path.join(PROJ, "media")
CHECK = os.path.join(PROJ, "check")
os.makedirs(MEDIA, exist_ok=True)
os.makedirs(CHECK, exist_ok=True)

# Only clean broken/error nodes belonging to htpm4 (keep all verified 'success' cached nodes!)
_, init_nodes = arv.get_canvas_state()
err_ids = [
    nid for nid, n in init_nodes.items()
    if "htpm4" in (n.get("title") or "").lower()
    and (n.get("metadata") or {}).get("status") == "error"
]
if err_ids:
    arv.cleanup_exported_canvas_nodes(err_ids)
    print(f"[Canvas] Cleaned {len(err_ids)} htpm4 error nodes.", flush=True)

FONTS_SRC      = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
LUT_HARMONIZER = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"
FONT_BOLD      = os.path.join(FONTS_SRC, "AsapCondensed-Bold.ttf")

SCENES = [
    {
        "id": "st01",
        "ref_tag": "ref_htpm4_01",
        "vid_title": "OUT_htpm4_01",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "st_01_chronic_stress.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_01.png"),
        "img_prompt": (
            "Editorial wellness lifestyle photography of a 29-year-old Vietnamese woman in a soft cream blouse sitting at her desk late in the evening "
            "under warm amber lamp light beside a laptop, resting two fingers gently on her temple with a tired stressed sleepless expression, 85mm shallow DOF."
        ),
        "vid_prompt": (
            "Subtle slow stabilized cinema push-in as she sighs quietly with closed lips and gently presses her temple in evening mental fatigue."
        ),
    },
    {
        "id": "st02",
        "ref_tag": "ref_htpm4_02",
        "vid_title": "OUT_htpm4_02",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "st_02_hormone_balance.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_02.png"),
        "img_prompt": (
            "High-end clean 3D medical scientific visualization in a luminous pastel pearl-rose and soft sapphire studio: "
            "delicate glowing golden-rose endocrine hormone spheres floating along a graceful translucent biological rhythm wave, cinema macro depth of field, 8k."
        ),
        "vid_prompt": (
            "Smooth slow orbital macro camera glide as the luminous rose-gold endocrine spheres pulse gently along the shimmering translucent rhythm wave."
        ),
    },
    {
        "id": "st03",
        "ref_tag": "ref_htpm4_03",
        "vid_title": "OUT_htpm4_03",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "st_03_nourish_relax.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_03.png"),
        "img_prompt": (
            "Bright editorial wellness lifestyle photography of a serene 30-year-old Vietnamese woman in breathable ivory linen enjoying a warm herbal tea "
            "beside a nutritious wholesome breakfast bowl of avocado, berries and nuts by a sunlit garden window, calm relaxed morning glow, 85mm lens."
        ),
        "vid_prompt": (
            "Graceful slow cinema dolly-in in warm morning sunbeams as she holds the warm cup of herbal tea with a peaceful relaxed closed-lip smile."
        ),
    },
    {
        "id": "st04",
        "ref_tag": "ref_htpm4_04",
        "vid_title": "OUT_htpm4_04",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "st_04_radiant_vitality.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_htpm4_04.png"),
        "img_prompt": (
            "Radiant luxury lifestyle portrait of a healthy 30-year-old Vietnamese woman in a flowing white blouse standing in a sunlit green garden "
            "bathed in golden morning light, glowing rosy porcelain skin, serene confident closed-lip smile symbolizing balanced feminine vitality, 85mm f/1.8."
        ),
        "vid_prompt": (
            "Smooth slow cinema tracking glide in golden garden sunlight as a gentle breeze moves her dark hair softly, radiant peaceful closed-lip smile."
        ),
    },
]

# Step 1: Parallel 3-Tab ChatGPT (HTPM project, auto-cleanup conversation) -> 4-tier fallback!
img_specs = [
    {
        "prompt": sc["img_prompt"],
        "ref_tag": sc["ref_tag"],
        "ratio": sc["ratio"],
        "timeout_per_tier": 180,
    }
    for sc in SCENES
]
print("[HTPM4] Generating 4 reference images via parallel 3-Tab ChatGPT HTPM (4-tier fallback)...", flush=True)
img_results = arv.generate_ref_images_parallel_batch(img_specs, max_workers=3)
for sc, (_, nid, prov) in zip(SCENES, img_results):
    sc["img_node_id"] = nid
    sc["img_provider"] = prov

# Step 2: Parallel 4-Tab Google Flow (videoMode='reference' / Thành phần, exact 4s) -> fallback Muse!
vid_specs = [
    {
        "motion_prompt": sc["vid_prompt"],
        "ref_img_node_id": sc["img_node_id"],
        "out_title": sc["vid_title"],
        "ratio": sc["ratio"],
        "seconds": sc["seconds"],
        "video_mode": "reference",
        "timeout_per_tier": 360,
    }
    for sc in SCENES
]
print("[HTPM4] Generating remaining reference-locked videos via Google Flow (Ingredients mode, 4s)...", flush=True)
vid_results = arv.generate_videos_parallel_batch(vid_specs, max_workers=3)
for sc, (_, vnid, vprov) in zip(SCENES, vid_results):
    sc["vid_node_id"] = vnid
    sc["vid_provider"] = vprov

# Step 3: Export all 4 image + 4 video nodes & clean up all htpm4 nodes immediately!
exp_map = {}
cleanup_ids = []
for sc in SCENES:
    exp_map[sc["img_node_id"]] = sc["ref_dest"]
    exp_map[sc["vid_node_id"]] = sc["dest"] + ".raw.mp4"
    cleanup_ids.extend([sc["img_node_id"], sc["vid_node_id"]])

_, end_nodes = arv.get_canvas_state()
for nid, n in end_nodes.items():
    if "htpm4" in (n.get("title") or "").lower():
        cleanup_ids.append(nid)

arv.export_canvas_nodes_to_files(exp_map, timeout_s=240)
arv.cleanup_exported_canvas_nodes(cleanup_ids)

# Step 4: Fast GPU NVENC trim (-ss 0.20s) + 66% LUT 10_AI_Clip_Harmonizer_Natural.cube!
lut_local = os.path.join(MEDIA, "_harm.cube")
import shutil
shutil.copy2(LUT_HARMONIZER, lut_local)

for sc in SCENES:
    raw_v = sc["dest"] + ".raw.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "0.20", "-i", raw_v,
        "-r", "30", "-fps_mode", "cfr", "-an",
        "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_harm.cube[bg];[a][bg]blend=all_expr=A*0.34+B*0.66[v]",
        "-map", "[v]",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        sc["dest"]
    ], cwd=MEDIA, check=True)
    print("READY_FLOW_CLIP ->", sc["dest"], f"(Img:{sc['img_provider']} -> Vid:{sc['vid_provider']})", flush=True)

# Step 5: Build visual QC contact sheet!
sheet = Image.new("RGB", (1280, 760), (244, 246, 252))
fnt = ImageFont.truetype(FONT_BOLD, 24)
for idx, sc in enumerate(SCENES):
    x0 = (idx % 2) * 640 + 16
    y0 = (idx // 2) * 375 + 14
    ImageDraw.Draw(sheet).text((x0, y0), f"{sc['id'].upper()} • Img:{sc['img_provider']} -> Vid:{sc['vid_provider']} (4s)", font=fnt, fill=(20, 24, 38))
    if os.path.exists(sc["ref_dest"]):
        im_r = Image.open(sc["ref_dest"]).convert("RGB"); im_r.thumbnail((285, 310))
        sheet.paste(im_r, (x0, y0 + 34))
    tjpg = sc["dest"] + ".qc.jpg"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", sc["dest"], "-frames:v", "1", tjpg], check=True)
    im_v = Image.open(tjpg).convert("RGB"); im_v.thumbnail((310, 310))
    sheet.paste(im_v, (x0 + 296, y0 + 34))
    os.remove(tjpg)

qc_p = os.path.join(CHECK, "flow_htpm4_qc.jpg")
sheet.save(qc_p, quality=92)
print("SAVED_FLOW_QC_SHEET ->", qc_p, flush=True)
