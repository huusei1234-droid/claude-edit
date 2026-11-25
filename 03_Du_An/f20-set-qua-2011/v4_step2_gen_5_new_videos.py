import base64, io, json, os, subprocess, sys, time, uuid
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call

V3_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v3_pro")
V4_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v4_clean_master")
KF4_DIR = V4_DIR / "kfs_v4"
VID4_DIR = V4_DIR / "videos_v4"
KF4_DIR.mkdir(parents=True, exist_ok=True)
VID4_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID = "export:folder-1794814915069-643ds"

# 1. Extract real Sony A1 macro of the crimson rosebud floral accent on the real F20 gift basket (for V4_vid05_hoa_diem_nhan - Fix Image 6!)
a1_68 = Image.open(r"Z:\Máy tính khác\My Computer\F20\Ảnh (1)\Ảnh đã chỉnh\A1_09768chị Oanh.JPG").convert("RGB")
# In A1_09768 (3936x2216), right basket floral accent is around x=3420..3936, y=820..1740 (width=516, height=918 -> exact 9:16!)
hoa_crop = a1_68.crop((3415, 780, 3936, 1706)).resize((1080, 1920), Image.Resampling.LANCZOS)
hoa_crop.save(KF4_DIR / "V4_kf05_hoa_real.jpg", quality=95)

# Also prepare clean composite reference of the TWO EQUAL-HEIGHT 100g F20 jars side by side so Muse generates 100% equal-sized jars!
j_gion = Image.open(V3_DIR / "ai_images_916" / "V3_im06_hu_say_gion.jpg").convert("RGB").crop((330, 560, 740, 1460)).resize((360, 760), Image.Resampling.LANCZOS)
j_me   = Image.open(V3_DIR / "ai_images_916" / "V3_im07_hu_say_me.jpg").convert("RGB").crop((245, 650, 765, 1465)).resize((360, 760), Image.Resampling.LANCZOS)
ref_two = Image.new("RGB", (900, 900), (242, 238, 225))
ref_two.paste(j_gion, (75, 70))
ref_two.paste(j_me,   (465, 70))
ref_two.save(KF4_DIR / "ref_two_equal_jars.jpg", quality=94)

# Upload refs onto Canvas
st = call("canvas_get_state", {})["result"]
img_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "image" and n.get("title")}

def ensure_uploaded(tag, pth, x_pos, y_pos):
    im = Image.open(pth).convert("RGB")
    buf = io.BytesIO(); im.save(buf, format="JPEG", quality=94)
    durl = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    if tag in img_by_title:
        call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": img_by_title[tag], "metadata": {"content": durl, "status": "success"}}]})
        return img_by_title[tag]
    before = {n["id"] for n in call("canvas_get_state", {})["result"]["nodes"]}
    call("canvas_create_node", {
        "nodeType": "image", "title": tag, "x": x_pos, "y": y_pos, "width": 250, "height": 360,
        "metadata": {"content": durl, "status": "success", "mimeType": "image/jpeg", "naturalWidth": im.width, "naturalHeight": im.height}
    })
    time.sleep(0.9)
    st1 = call("canvas_get_state", {})["result"]
    nid = [n["id"] for n in st1["nodes"] if n["id"] not in before and n["type"] == "image"][-1]
    img_by_title[tag] = nid
    print(f"Uploaded {tag} -> {nid}", flush=True)
    return nid

id_hoa   = ensure_uploaded("v4ref-hoa-real", KF4_DIR / "V4_kf05_hoa_real.jpg", 45500, 0)
id_twoj  = ensure_uploaded("v4ref-two-equal-jars", KF4_DIR / "ref_two_equal_jars.jpg", 45500, 420)
id_bask  = img_by_title["v3kf-im13"]   # Real Sony A1 complete Mica basket with authentic SKA NEST, Rong Bien & Banh Thuyen!
id_skan  = img_by_title["f20-r2-skanest"]
id_met   = img_by_title["f20-r9-met-hat"]

# 2. Generate 4 brand-new 9:16 Keyframes via muse::muse-image (strictly 1-by-1!)
IMG_JOBS = [
    ("V4_kf01_hero_giftset", [id_bask],
     "Warm commercial 9:16 vertical product photography for Vietnamese Teacher's Day 20/11: place the exact transparent Mica gift basket from the reference image dead-center on a warm sunlit oak table, keeping the round yellow SKA NEST bird's nest box, green F20 Rong Bien seaweed jars, Banh Thuyen nut pouch, crimson rosebud accent, burgundy leather handle and sheer beige bow 100 percent authentic and unchanged (DO NOT alter any jar labels, NO mushrooms), styled gracefully beside a soft bouquet of pastel flowers and warm golden bokeh background, generous clean space, no text, no watermark"),
    ("V4_kf02_two_jars_even", [id_twoj],
     "Balanced symmetrical 9:16 vertical food commercial photography: place the TWO clear cylindrical 100g seaweed jars from the reference image standing side-by-side at the EXACT SAME HEIGHT AND IDENTICAL SIZE in the dead center of a round woven bamboo tray on a sunlit wooden table — left jar F20 Rong Bien Say Gion and right jar F20 Rong Bien Say Me Tue Tam — garnished around the tray base with crispy roasted dark-green seaweed flakes and sesame seeds, fresh sunlit emerald-green garden bokeh background, 100 percent symmetrical, no boxes, no extra text, no watermark"),
    ("V4_kf03_24_thanh_hat", [id_met],
     "Mouth-watering 9:16 vertical culinary commercial photography, 45-degree tabletop angle: a round red-rimmed woven bamboo tray (mẹt tre) resting dead-center on a warm sunlit honey-oak table, generously filled with 22 to 24 neatly stacked thick crispy dark-green roasted seaweed nut bars (thanh bánh rong biển kẹp hạt) packed with crunchy almonds, cashews, pumpkin seeds and white sesame seeds, warm morning golden sunbeams, appetizing natural food photography, no hands, no plastic gloves, no text, no watermark"),
    ("V4_kf04_yen_gia_tri_nhat", [id_skan],
     "Opulent full-screen 9:16 vertical luxury commercial photography: a prestigious crimson-and-gold velvet gift box resting open in the exact center of warm draped champagne-gold silk, showcasing a large pristine ivory-white whole refined bird's nest (tổ yến sào tinh chế sợi dài) with long delicate translucent strands catching warm morning sunbeams alongside the red-and-gold SKA NEST emblem, rich harmonious full-bleed vertical composition with zero empty borders, no text overlays, no watermark"),
]

def node_img_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    imgs = m.get("images") or []
    if s == "success" or (imgs and imgs[0].get("status") == "success"): return "success"
    if s in ("error", "failed"): return "error"
    return s

def node_vid_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    if s == "success" and m.get("content"): return "success"
    if s in ("error", "failed"): return "error"
    return s

kf_out_ids = {"V4_kf05_hoa_real": id_hoa}

for idx, (kname, ref_list, prompt) in enumerate(IMG_JOBS):
    txt_id = f"text-{uuid.uuid4()}"
    cfg_id = f"config-{uuid.uuid4()}"
    refs_str = "\n".join(f"@[node:{r}]" for r in ref_list)
    comp = f"@[node:{txt_id}]" + (f"\n{refs_str}" if refs_str else "")
    ops = [
        {"type": "add_node", "nodeType": "text", "id": txt_id, "title": f"t_{kname}", "position": {"x": 46000, "y": idx * 440}, "metadata": {"content": prompt, "status": "idle"}},
        {"type": "add_node", "nodeType": "config", "id": cfg_id, "title": kname, "position": {"x": 46350, "y": idx * 440},
         "metadata": {"content": "", "status": "idle", "generationMode": "image", "composerContent": comp, "prompt": comp, "model": "muse::muse-image", "size": "9:16"}},
        {"type": "connect_nodes", "fromNodeId": txt_id, "toNodeId": cfg_id},
    ]
    for r in ref_list:
        ops.append({"type": "connect_nodes", "fromNodeId": r, "toNodeId": cfg_id})
    call("canvas_apply_ops", {"ops": ops})
    time.sleep(0.8)
    call("canvas_run_generation", {"nodeId": cfg_id, "mode": "image"})
    print(f"[Muse Image 1-by-1] Triggered {kname}...", flush=True)

    t0 = time.time()
    while time.time() - t0 < 120:
        time.sleep(4.5)
        st = call("canvas_get_state", {})["result"]
        nodes = {n["id"]: n for n in st["nodes"]}
        oids = [c["toNodeId"] for c in st["connections"] if c["fromNodeId"] == cfg_id and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "image"]
        if oids and node_img_status(nodes[oids[-1]]) == "success":
            kf_out_ids[kname] = oids[-1]
            call("canvas_update_node", {"id": oids[-1], "patch": {"title": kname}})
            print(f"  -> {kname} SUCCESS ({int(time.time()-t0)}s)", flush=True)
            break

# 3. Animate all 5 V4 Keyframes into smooth, steady 9:16 Commercial Videos via muse::muse-video (strictly 1-by-1!)
VID_JOBS = [
    ("V4_vid01_hero_giftset", "V4_kf01_hero_giftset",
     "Gentle steady commercial camera glide with subtle warm golden bokeh shimmer in the background around the transparent Mica 20/11 gift basket on the oak table, keep the gift basket and every product inside 100 percent sharp, rigid and unchanged, no fast zoom, no hands, no text"),
    ("V4_vid02_two_jars_even", "V4_kf02_two_jars_even",
     "Balanced steady commercial tabletop shot of the two equal-sized green F20 seaweed jars standing side-by-side on the woven bamboo tray, gentle morning sunlight and soft green garden bokeh swaying slightly in background, keep both jars and their labels 100 percent equal height, rigid and sharp, no fast zoom, no hands, no text"),
    ("V4_vid03_24_thanh_hat", "V4_kf03_24_thanh_hat",
     "Appetizing culinary commercial slow tabletop camera glide across the round woven bamboo tray filled with 24 crispy dark seaweed nut bars, warm golden sunbeams catching the crunchy almonds, cashews and sesame seeds, smooth steady motion, no hands, no text"),
    ("V4_vid04_yen_gia_tri_nhat", "V4_kf04_yen_gia_tri_nhat",
     "Luxury commercial slow tabletop glide over the open crimson-and-gold presentation box holding the pristine ivory-white long-strand bird's nest on champagne silk, warm golden light rays drifting softly, steady dignified camera, no fast zoom, no hands, no text"),
    ("V4_vid05_hoa_diem_nhan", "V4_kf05_hoa_real",
     "Delicate macro commercial camera glide focusing on the crimson rosebud and green leaf floral decoration tucked into the corner of the transparent gift basket, warm boutique bokeh lighting shimmering softly in background, keep the flower and basket weave 100 percent authentic, no hands, no text"),
]

vid_out_ids = {}
for idx, (vname, kname, vprompt) in enumerate(VID_JOBS):
    img_id = kf_out_ids[kname]
    txt_id = f"text-{uuid.uuid4()}"
    cfg_id = f"config-{uuid.uuid4()}"
    comp = f"@[node:{txt_id}]\n@[node:{img_id}]"
    call("canvas_apply_ops", {"ops": [
        {"type": "add_node", "nodeType": "text", "id": txt_id, "title": f"tv_{vname}", "position": {"x": 47000, "y": idx * 440}, "metadata": {"content": vprompt, "status": "idle"}},
        {"type": "add_node", "nodeType": "config", "id": cfg_id, "title": f"cv_{vname}", "position": {"x": 47350, "y": idx * 440},
         "metadata": {"content": "", "status": "idle", "generationMode": "video", "composerContent": comp, "prompt": comp, "model": "muse::muse-video", "size": "9:16", "seconds": "5"}},
        {"type": "connect_nodes", "fromNodeId": txt_id, "toNodeId": cfg_id},
        {"type": "connect_nodes", "fromNodeId": img_id, "toNodeId": cfg_id},
    ]})
    time.sleep(0.8)
    call("canvas_run_generation", {"nodeId": cfg_id, "mode": "video"})
    print(f"[Muse Video 1-by-1] Triggered {vname}...", flush=True)

    t0 = time.time()
    while time.time() - t0 < 150:
        time.sleep(5.5)
        st = call("canvas_get_state", {})["result"]
        nodes = {n["id"]: n for n in st["nodes"]}
        vids = [c["toNodeId"] for c in st["connections"] if c["fromNodeId"] == cfg_id and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "video"]
        if vids and node_vid_status(nodes[vids[-1]]) == "success":
            vid_out_ids[vname] = vids[-1]
            call("canvas_update_node", {"id": vids[-1], "patch": {"title": vname}})
            print(f"  -> {vname} SUCCESS ({int(time.time()-t0)}s)", flush=True)
            break

# 4. Export all 4 new KFs + 5 new Videos via export node & normalize symmetrically!
st = call("canvas_get_state", {})["result"]
ex = [x for x in st["nodes"] if x["id"] == EXPORT_NODE_ID][0]
p = ex["position"]
call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": EXPORT_NODE_ID, "metadata": {"exportAll": True, "exportRequest": f"v4-5vids-{int(time.time())}"}}]})

for _ in range(18):
    time.sleep(2.5)
    m = json.loads(Path(MANIFEST).read_text(encoding="utf-8"))
    by_id = {it["nodeId"]: it for it in m.get("items", [])}
    if all(vid in by_id for vid in vid_out_ids.values()):
        break

m = json.loads(Path(MANIFEST).read_text(encoding="utf-8"))
by_id = {it["nodeId"]: it for it in m.get("items", [])}

for kname, kid in kf_out_ids.items():
    if kid in by_id and kname != "V4_kf05_hoa_real":
        Image.open(by_id[kid]["path"]).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS).save(KF4_DIR / f"{kname}.jpg", quality=95)

sheet = Image.new("RGB", (240 * 5, 426))
tmp = VID4_DIR / "_tmp_v4.jpg"
for i, (vname, vid) in enumerate(sorted(vid_out_ids.items())):
    if vid in by_id:
        dst = VID4_DIR / f"{vname}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", "0.10", "-i", by_id[vid]["path"],
            "-vf", "scale=1156:2056:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,fps=30,format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "16", str(dst)
        ], check=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", str(dst), "-frames:v", "1", str(tmp)], check=True)
        im = Image.open(tmp).resize((240, 426))
        d = ImageDraw.Draw(im)
        d.rectangle([4, 4, 232, 26], fill=(0, 0, 0))
        d.text((8, 8), vname, fill=(255, 230, 0))
        sheet.paste(im, (i * 240, 0))
if tmp.exists():
    tmp.unlink()
sheet.save(VID4_DIR / "v4_5videos_qc_sheet.jpg", quality=93)
print(f"DONE! Exported {len(vid_out_ids)}/5 new V4 videos + v4_5videos_qc_sheet.jpg!")
