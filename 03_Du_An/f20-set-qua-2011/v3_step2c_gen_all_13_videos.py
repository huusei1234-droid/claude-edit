import base64, io, json, os, subprocess, sys, time, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call

V3_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v3_pro")
IMG_V3 = V3_DIR / "ai_images_916"
VID_V3 = V3_DIR / "videos_v3"
VID_V3.mkdir(parents=True, exist_ok=True)
MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID = "export:folder-1794814915069-643ds"

# 0. Finalize exact pixel placement on V3_im06_hu_say_gion.jpg (ax6=493, ay_top=1030; ex=527, ax_t=583)
im06 = Image.open(IMG_V3 / "_raw_V3_im06_hu_say_gion.jpg").convert("RGBA")
tl6 = Image.new("RGBA", im06.size, (0, 0, 0, 0))
d6 = ImageDraw.Draw(tl6)
ax6, ay_top = 493, 1029
hat_pts = [(ax6 - 9, ay_top - 3), (ax6, ay_top - 12), (ax6 + 9, ay_top - 3)]
ac_pts = [(ax6 + 4, ay_top - 11), (ax6 + 11, ay_top - 17)]
d6.line(hat_pts, fill=(24, 68, 22, 250), width=6, joint="curve")
d6.line(ac_pts, fill=(24, 68, 22, 250), width=5)
d6.line(hat_pts, fill=(238, 236, 98, 255), width=2, joint="curve")
d6.line(ac_pts, fill=(238, 236, 98, 255), width=2)
for cx in (527, 583):
    d6.line([(cx - 5, 1084), (cx, 1078), (cx + 5, 1084)], fill=(22, 68, 28, 245), width=3)
d6.ellipse([525, 1112, 529, 1116], fill=(22, 68, 28, 245))
im06.alpha_composite(tl6.filter(ImageFilter.GaussianBlur(0.35)))
im06.convert("RGB").save(IMG_V3 / "V3_im06_hu_say_gion.jpg", quality=96)

# 1. Upload/resolve all 13 start-frame image nodes on Canvas
UPLOAD_KFS = {
    "v3kf-im06": IMG_V3 / "V3_im06_hu_say_gion.jpg",
    "v3kf-im08": IMG_V3 / "V3_im08_banh_thuyen.jpg",
    "v3kf-im09": IMG_V3 / "V3_im09_kep_hat.jpg",
    "v3kf-im12": IMG_V3 / "V3_im12_kep_hat_bars.jpg",
    "v3kf-im13": IMG_V3 / "V3_im13_gio_mica_real.jpg",
    "v3kf-im14": IMG_V3 / "V3_im14_quai_no_macro.jpg",
}

st = call("canvas_get_state", {})["result"]
img_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "image" and n.get("title")}

for idx, (tag, pth) in enumerate(UPLOAD_KFS.items()):
    im = Image.open(pth).convert("RGB")
    buf = io.BytesIO(); im.save(buf, format="JPEG", quality=94)
    durl = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    if tag in img_by_title:
        call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": img_by_title[tag], "metadata": {"content": durl, "status": "success"}}]})
    else:
        before = {n["id"] for n in call("canvas_get_state", {})["result"]["nodes"]}
        call("canvas_create_node", {
            "nodeType": "image", "title": tag, "x": 42800, "y": idx * 450, "width": 250, "height": 420,
            "metadata": {"content": durl, "status": "success", "mimeType": "image/jpeg", "naturalWidth": im.width, "naturalHeight": im.height}
        })
        time.sleep(0.8)
        st1 = call("canvas_get_state", {})["result"]
        img_by_title[tag] = [n["id"] for n in st1["nodes"] if n["id"] not in before and n["type"] == "image"][-1]
        print(f"Uploaded {tag} -> {img_by_title[tag]}", flush=True)

# 2. Define all 13 V3 video jobs: (name, img_title, preferred_engine, prompt)
JOBS = [
    ("V3_vid01_set_qua_hero", "v3-im01", "flow",
     "Smooth slow commercial gimbal camera push-in under 4 percent on the centered transparent Mica gift basket resting on the wooden pedestal, warm emerald and golden bokeh lights shimmering gently in background, keep the gift basket, burgundy leather handle, beige bow, SKA NEST box and F20 green jars 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("V3_vid02_skanest_box", "v3-im02", "flow",
     "Luxury commercial tabletop slow push-in under 4 percent on the centered round SKA NEST bird's nest box resting on champagne-gold silk, warm morning sunbeams gliding softly across the satin folds, keep the round box and red SKA NEST seal 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("V3_vid03_to_yen_pure", "v3-im03", "flow",
     "Cinematic luxury macro slow camera push-in on the pristine ivory-white edible bird's nest in the crystal dish on champagne silk, warm golden morning sunlight rays and soft bokeh motes drifting gently in the air, keep the bird's nest strands crisp and natural, no hands, no text"),
    ("V3_vid04_tao_do_dtht", "v3-im04", "flow",
     "Appetizing culinary commercial slow camera glide and gentle push-in on the two crystal bowls of glossy crimson Red Jujubes and vibrant golden-orange Cordyceps strands on the sunlit wooden tray, warm golden bokeh shimmering softly in background, crisp food macro, no hands, no text"),
    ("V3_vid05_ky_tu_duong_phen", "v3-im05", "flow",
     "Appetizing culinary commercial slow camera push-in on the dish of bright red Goji Berries and clear box of sparkling white Rock Sugar crystals on the sunlit wooden table, warm morning sunbeams catching the sugar crystals, soft golden bokeh, no hands, no text"),
    ("V3_vid10_chung_yen", "v3-im10", "flow",
     "Warm appetizing culinary commercial shot: delicate wisps of natural white steam rising gently from the freshly stewed golden bird's nest with red jujubes and goji berries inside the white porcelain stewing pot on the wooden tray beside the small blue booklet, subtle 3 percent camera push-in, no hands, no text"),
    ("V3_vid12_kep_hat_bars", "v3kf-im12", "flow",
     "Authentic commercial artisan food close-up: gentle natural 3 percent camera zoom-in on the stack of three thick crispy dark seaweed nut bars held in a clean gloved hand above freshly baked seaweed nut bars, warm sunlit sheen highlighting the crunchy nuts and roasted seaweed texture, keep the bars crisp and unchanged, no extra text"),
    ("V3_vid13_gio_mica_real", "v3kf-im13", "flow",
     "Smooth steady commercial camera push-in under 4 percent on the real transparent Mica gift basket with burgundy leather handle, beige organza bow and red floral accent on the wooden counter, warm store lighting and subtle depth-of-field parallax, keep every product and label inside the basket 100 percent rigid and unchanged, no hands, no text"),
    ("V3_vid14_quai_no_macro", "v3kf-im14", "flow",
     "Cinematic macro slow camera zoom-in on the burgundy red stitched leather basket handle and sheer beige organza ribbon bow, soft warm light catching the translucent ribbon loops and fine leather stitching, keep the handle and bow 100 percent authentic and unchanged, no hands, no text"),

    # Label-critical F20 jars & pouches run on Muse Video (strictly 1-by-1!)
    ("V3_vid06_hu_say_gion", "v3kf-im06", "muse",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the centered F20 Rong Bien Say Gion jar on the woven bamboo tray, sunlit green bokeh leaves swaying softly in background, keep the jar and green F20 label 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("V3_vid07_hu_say_me", "v3-im07", "muse",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the centered F20 Rong Bien Say Me jar on the woven bamboo tray, sunlit green bokeh leaves swaying softly in background, keep the jar and green F20 Tue Tam label 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("V3_vid08_banh_thuyen", "v3kf-im08", "muse",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the centered Banh Thuyen Mix Hat Dinh Duong zip pouch and three nut boat tartlets on the woven bamboo tray, warm golden sunlight bokeh shimmering softly in background, keep the pouch, label and nut boats 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("V3_vid09_kep_hat", "v3kf-im09", "muse",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the centered Tue Tam Rong Bien Kep Hat zip pouch and four seaweed nut bars on the woven bamboo tray, warm golden sunlight bokeh shimmering softly in background, keep the pouch, label and bars 100 percent rigid, sharp and unchanged, no hands, no text"),
]

def vid_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    if s == "success" and m.get("content"): return "success"
    if s in ("error", "failed"): return "error"
    return s

def cfg_status(n):
    if not n: return "none"
    return n.get("metadata", {}).get("status") or "idle"

# Track state per job
state = {}
for idx, (name, img_tag, eng, prompt) in enumerate(JOBS):
    state[name] = {
        "idx": idx, "img_id": img_by_title[img_tag], "engine": eng, "prompt": prompt,
        "flow_vid_id": None, "flow_tries": 0,
        "muse_cfg_id": None, "muse_vid_id": None, "muse_tries": 0,
        "final_vid_id": None,
    }

# Reuse any already-created V3_vid nodes from a prior run if present
st = call("canvas_get_state", {})["result"]
for n in st["nodes"]:
    t = n.get("title") or ""
    if n["type"] == "video" and t in state and vid_status(n) == "success":
        state[t]["final_vid_id"] = n["id"]

def launch_flow(name, info):
    vid_id = f"video-{uuid.uuid4()}"
    img_id = info["img_id"]
    comp = f"@[node:{img_id}] {info['prompt']}"
    meta = {
        "generationMode": "video", "composerContent": comp, "prompt": comp, "status": "idle",
        "model": "flow::flow-omni-1.2-flash", "size": "9:16", "seconds": "6", "vquality": "720",
        "generateAudio": "false", "watermark": "false", "videoMode": "frames",
    }
    call("canvas_apply_ops", {"ops": [
        {"type": "add_node", "nodeType": "video", "id": vid_id, "title": name, "position": {"x": 43500, "y": info["idx"] * 420}, "metadata": meta},
        {"type": "connect_nodes", "fromNodeId": img_id, "toNodeId": vid_id},
        {"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp},
    ]})
    info["flow_vid_id"] = vid_id
    info["flow_tries"] += 1
    print(f"  -> [Flow] Triggered {name} (try {info['flow_tries']})", flush=True)

def launch_muse(name, info):
    img_id = info["img_id"]
    txt_id = f"text-{uuid.uuid4()}"
    cfg_id = f"config-{uuid.uuid4()}"
    comp = f"@[node:{txt_id}]\n@[node:{img_id}]"
    call("canvas_apply_ops", {"ops": [
        {"type": "add_node", "nodeType": "text", "id": txt_id, "title": f"txt_{name}", "position": {"x": 44200, "y": info["idx"] * 420},
         "metadata": {"content": info["prompt"], "status": "idle"}},
        {"type": "add_node", "nodeType": "config", "id": cfg_id, "title": f"cfg_{name}", "position": {"x": 44550, "y": info["idx"] * 420},
         "metadata": {"content": "", "status": "idle", "generationMode": "video", "composerContent": comp, "prompt": comp, "model": "muse::muse-video", "size": "9:16", "seconds": "5"}},
        {"type": "connect_nodes", "fromNodeId": txt_id, "toNodeId": cfg_id},
        {"type": "connect_nodes", "fromNodeId": img_id, "toNodeId": cfg_id},
    ]})
    time.sleep(0.8)
    call("canvas_run_generation", {"nodeId": cfg_id, "mode": "video"})
    info["muse_cfg_id"] = cfg_id
    info["muse_tries"] += 1
    print(f"  -> [Muse 1-by-1] Triggered {name} (try {info['muse_tries']})", flush=True)

t0 = time.time()
while time.time() - t0 < 780:
    st = call("canvas_get_state", {})["result"]
    nodes = {n["id"]: n for n in st["nodes"]}
    conns = st["connections"]

    flow_act = 0
    muse_act = 0
    summary = []

    for name, info in state.items():
        if info["final_vid_id"]:
            summary.append(f"{name[3:8]}:OK")
            continue

        if info["engine"] == "flow":
            fvid = nodes.get(info["flow_vid_id"]) if info["flow_vid_id"] else None
            fs = vid_status(fvid) if fvid else "none"
            if fs == "success":
                info["final_vid_id"] = info["flow_vid_id"]
                summary.append(f"{name[3:8]}:OK")
            elif fs == "loading":
                flow_act += 1
                summary.append(f"{name[3:8]}:F_run")
            elif fs == "error":
                call("canvas_delete_nodes", {"ids": [info["flow_vid_id"]]})
                info["flow_vid_id"] = None
                if info["flow_tries"] >= 2:
                    info["engine"] = "muse"
                    print(f"  [Fallback] Switching {name} from Flow -> Muse (1-by-1)", flush=True)
                    summary.append(f"{name[3:8]}:->M")
                else:
                    summary.append(f"{name[3:8]}:F_ret")
            else:
                summary.append(f"{name[3:8]}:F_q")
        else:
            cid = info["muse_cfg_id"]
            if cid and cid in nodes:
                vids = [c["toNodeId"] for c in conns if c["fromNodeId"] == cid and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "video"]
                mvid_id = vids[-1] if vids else None
                ms = vid_status(nodes.get(mvid_id)) if mvid_id else cfg_status(nodes.get(cid))
                if mvid_id and vid_status(nodes.get(mvid_id)) == "success":
                    info["final_vid_id"] = mvid_id
                    call("canvas_update_node", {"id": mvid_id, "patch": {"title": name}})
                    summary.append(f"{name[3:8]}:OK")
                elif ms == "loading":
                    muse_act += 1
                    summary.append(f"{name[3:8]}:M_run")
                elif ms == "error":
                    if mvid_id:
                        call("canvas_delete_nodes", {"ids": [mvid_id]})
                    info["muse_cfg_id"] = None
                    summary.append(f"{name[3:8]}:M_err")
                else:
                    muse_act += 1
                    summary.append(f"{name[3:8]}:M_{ms}")
            else:
                summary.append(f"{name[3:8]}:M_q")

    done_cnt = sum(1 for info in state.values() if info["final_vid_id"])
    print(f"[{int(time.time()-t0):3d}s] Videos {done_cnt}/13 (FlowAct={flow_act}, MuseAct={muse_act}) | " + " ".join(summary), flush=True)
    if done_cnt >= 13:
        break

    # Launch up to 2 Flow jobs concurrently
    for name, info in state.items():
        if flow_act >= 2:
            break
        if not info["final_vid_id"] and info["engine"] == "flow" and not info["flow_vid_id"] and info["flow_tries"] < 2:
            launch_flow(name, info)
            flow_act += 1
            time.sleep(1.5)

    # Launch strictly 1 Muse job at a time!
    if muse_act < 1:
        for name, info in state.items():
            if not info["final_vid_id"] and info["engine"] == "muse" and not info["muse_cfg_id"] and info["muse_tries"] < 2:
                launch_muse(name, info)
                muse_act += 1
                time.sleep(2.0)
                break

    time.sleep(6)

# 3. Export all completed videos & symmetrically normalize to exact 1080x1920 @ 30fps (1.07x symmetric center zoom to crop any tiny corner watermark cleanly!)
st = call("canvas_get_state", {})["result"]
for name, info in state.items():
    if info["final_vid_id"]:
        call("canvas_update_node", {"id": info["final_vid_id"], "patch": {"title": name}})

ex = [x for x in st["nodes"] if x["id"] == EXPORT_NODE_ID][0]
p = ex["position"]
call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": EXPORT_NODE_ID, "metadata": {"exportAll": True, "exportRequest": f"v3-vids13-{int(time.time())}"}}]})

exported = {}
want_ids = {name: info["final_vid_id"] for name, info in state.items() if info["final_vid_id"]}
for _ in range(20):
    time.sleep(3.0)
    m = json.loads(Path(MANIFEST).read_text(encoding="utf-8"))
    by_id = {it["nodeId"]: it for it in m.get("items", [])}
    if all(vid_id in by_id for vid_id in want_ids.values()):
        break

m = json.loads(Path(MANIFEST).read_text(encoding="utf-8"))
by_id = {it["nodeId"]: it for it in m.get("items", [])}
for name, vid_id in want_ids.items():
    if vid_id in by_id:
        dst = VID_V3 / f"{name}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", "0.10", "-i", by_id[vid_id]["path"],
            "-vf", "scale=1156:2056:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,fps=30,format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            str(dst)
        ], check=True)
        exported[name] = str(dst)
        print(f"Normalized centered 1080x1920 -> {dst.name}")

# Also normalize OUT_f20_v7_anh_hau.mp4 symmetrically without corner watermark into videos_v3!
v7_src = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117\flow_videos\OUT_f20_v7_anh_hau.mp4")
if v7_src.exists():
    dst_v7 = VID_V3 / "V3_vid15_anh_hau.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(v7_src),
        "-vf", "scale=1156:2056:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,fps=30,format=yuv420p",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        str(dst_v7)
    ], check=True)
    exported["V3_vid15_anh_hau"] = str(dst_v7)

# Build QC contact sheet of all V3 AI Videos
all_vids = sorted(VID_V3.glob("V3_vid*.mp4"))
cols = 5
rows = (len(all_vids) + cols - 1) // cols
sheet = Image.new("RGB", (240 * cols, 426 * rows))
tmp_jpg = VID_V3 / "_tmp_qc.jpg"
for i, vp in enumerate(all_vids):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", str(vp), "-frames:v", "1", str(tmp_jpg)], check=True)
    im = Image.open(tmp_jpg).resize((240, 426))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 232, 26], fill=(0, 0, 0))
    d.text((8, 8), vp.stem, fill=(255, 230, 0))
    sheet.paste(im, ((i % cols) * 240, (i // cols) * 426))
if tmp_jpg.exists():
    tmp_jpg.unlink()
sheet.save(VID_V3 / "v3_videos_qc_sheet.jpg", quality=92)
print(f"DONE! Saved {len(all_vids)} V3 centered videos + v3_videos_qc_sheet.jpg!")
