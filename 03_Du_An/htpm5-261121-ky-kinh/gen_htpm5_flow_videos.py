import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

PROJ = r"d:\AI\full studio\output\htpm5-261121"
MEDIA = os.path.join(PROJ, "media")
CHECK = os.path.join(PROJ, "check")
os.makedirs(MEDIA, exist_ok=True)
os.makedirs(CHECK, exist_ok=True)

FONTS_SRC = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
LUT_HARMONIZER = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"
APPLY_LUT = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\apply_lut.py"
PY_EXE = r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
FONT_BOLD = os.path.join(FONTS_SRC, "AsapCondensed-Bold.ttf")

# 0. Clean all leftover clutter nodes on Canvas first so Canvas & ChatGPT run at 100% speed!
r0, nodes0 = arv.get_canvas_state()
clutter = [
    nid for nid, n in nodes0.items()
    if nid not in {"image-htpm5_char_anchor-6ffc91"} and not str(n.get("type", "")).startswith("export:")
]
if clutter:
    print(f"[Cleanup] Removing {len(clutter)} stale Canvas nodes...", flush=True)
    arv._delete_nodes_safe(clutter)

CHAR_ANCHOR_PATH = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\04_CODE_MAU_HYPERFRAMES_CHUAN\mau_dieu_kinh_3d_satin_24fps\assets\images\DK_IMG_01A_CHAR_PORTRAIT.png"
char_ref_nid = arv.stage_local_ref_image_once(CHAR_ANCHOR_PATH, ref_tag="htpm5_char_anchor")
print(f"[Anchor] Staged protagonist reference node -> {char_ref_nid}", flush=True)

# Strict ChatGPT-first chain (avoids Flow gallery picking old project images!)
CHATGPT_STRICT_CHAIN = [
    ("ChatGPT", "chatgpt::chatgpt-image"),
    ("ChatGPT-2", "chatgpt::chatgpt-image"),
    ("Muse", "muse::muse-image"),
]

SCENES = [
    {
        "id": "cy01",
        "ref_tag": "ref_cy01_cal",
        "vid_title": "OUT_htpm5_cy01",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "cy_01_calendar_mark.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_cy01.png"),
        "img_prompt": "Calendar mark scene",
        "vid_prompt": "Calendar mark motion",
    },
    {
        "id": "cy02",
        "ref_tag": "ref_cy02_pain",
        "vid_title": "OUT_htpm5_cy02_v2",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "cy_02_cramp_pain.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_cy02.png"),
        "img_prompt": "Cramp pain scene",
        "vid_prompt": "Cramp pain motion",
    },
    {
        "id": "cy03",
        "ref_tag": "ref_cy03_conceive",
        "vid_title": "OUT_htpm5_cy03_v2",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "cy_03_trying_conceive.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_cy03.png"),
        "img_prompt": (
            "Using the exact same young Vietnamese woman from the reference image sitting warmly beside her loving Vietnamese husband on a sofa in a bright sunlit living room, "
            "both holding and looking together with hopeful tender smiles at a clean white paper monthly calendar and planner notebook on the table, natural morning sunlight, 85mm."
        ),
        "vid_prompt": (
            "Warm slow cinema push-in as the young Vietnamese couple look together at the monthly calendar notebook in their hands and share a gentle hopeful smile with closed lips."
        ),
    },
    {
        "id": "cy04",
        "ref_tag": "ref_cy04_clinic",
        "vid_title": "OUT_htpm5_cy04_v2",
        "ratio": "16:9",
        "seconds": 4,
        "dest": os.path.join(MEDIA, "cy_04_doctor_consult.mp4"),
        "ref_dest": os.path.join(MEDIA, "ref_cy04.png"),
        "img_prompt": (
            "Bright modern women's health clinic consultation room: a kind senior Vietnamese female doctor wearing a crisp white medical coat and stethoscope "
            "explaining a clean health chart on a digital tablet to the exact same young Vietnamese woman from the reference image sitting attentively across the desk, natural daylight, 85mm."
        ),
        "vid_prompt": (
            "Smooth cinema shot in a bright modern clinic as the Vietnamese female doctor in a white coat points calmly to the digital tablet while the young woman listens attentively and nods gently."
        ),
    },
]

cleanup_ids = [char_ref_nid]

for sc in SCENES:
    sid = sc["id"]
    raw_v = sc["dest"] + ".raw.mp4"

    if os.path.exists(sc["dest"]) and os.path.exists(sc["ref_dest"]):
        sc["img_provider"], sc["vid_provider"] = "Verified-ChatGPT", "Verified-Flow"
        print(f"[{sid}] Already verified on disk -> skipping!", flush=True)
        continue

    nid, prov = arv.generate_ref_image_4tier(
        prompt=sc["img_prompt"],
        ref_tag=sc["ref_tag"],
        ratio=sc["ratio"],
        reference_node_ids=[char_ref_nid],
        preferred_chain=CHATGPT_STRICT_CHAIN,
        timeout_per_tier=260,
    )
    sc["img_node_id"], sc["img_provider"] = nid, prov
    arv.export_canvas_nodes_to_files({nid: sc["ref_dest"]}, timeout_s=120)
    cleanup_ids.append(nid)

    vnid, vprov = arv.generate_video_with_ref(
        motion_prompt=sc["vid_prompt"],
        ref_img_node_id=sc["img_node_id"],
        out_title=sc["vid_title"],
        ratio=sc["ratio"],
        seconds=sc["seconds"],
        video_mode="reference",
        timeout_per_tier=320,
    )
    sc["vid_node_id"], sc["vid_provider"] = vnid, vprov
    arv.export_canvas_nodes_to_files({vnid: raw_v}, timeout_s=180)
    cleanup_ids.append(vnid)

    tmp_t = sc["dest"] + ".trim.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "0.20", "-i", raw_v,
        "-r", "30", "-fps_mode", "cfr", "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        tmp_t
    ], check=True)
    subprocess.run([PY_EXE, "-X", "utf8", APPLY_LUT, tmp_t, sc["dest"], LUT_HARMONIZER, "--intensity", "0.66"], check=True)
    os.remove(tmp_t)
    print("READY_REFERENCED_FLOW_CLIP ->", sc["dest"], f"(Img:{sc['img_provider']} -> Vid:{sc['vid_provider']})", flush=True)

arv.cleanup_exported_canvas_nodes(cleanup_ids)

sheet = Image.new("RGB", (1280, 760), (244, 246, 252))
fnt = ImageFont.truetype(FONT_BOLD, 24)
for idx, sc in enumerate(SCENES):
    x0 = (idx % 2) * 640 + 16
    y0 = (idx // 2) * 375 + 14
    ImageDraw.Draw(sheet).text((x0, y0), f"{sc['id'].upper()} [Ref-Locked] • {sc.get('img_provider','OK')} -> {sc.get('vid_provider','OK')} (4s)", font=fnt, fill=(20, 24, 38))
    if os.path.exists(sc["ref_dest"]):
        im_r = Image.open(sc["ref_dest"]).convert("RGB"); im_r.thumbnail((285, 310))
        sheet.paste(im_r, (x0, y0 + 34))
    tjpg = sc["dest"] + ".qc.jpg"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", sc["dest"], "-frames:v", "1", tjpg], check=True)
    if os.path.exists(tjpg):
        im_v = Image.open(tjpg).convert("RGB"); im_v.thumbnail((285, 310))
        sheet.paste(im_v, (x0 + 305, y0 + 34))
        os.remove(tjpg)

qc_path = os.path.join(CHECK, "flow_htpm5_qc.jpg")
sheet.save(qc_path, quality=93)
print("Saved Reference-Locked Flow QC Sheet ->", qc_path, flush=True)
