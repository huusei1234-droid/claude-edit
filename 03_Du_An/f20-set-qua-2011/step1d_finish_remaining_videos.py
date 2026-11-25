import json, os, subprocess, sys, time, uuid
from PIL import Image, ImageDraw
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call

OUT = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"
VID_OUT_DIR = os.path.join(OUT, "flow_videos")
os.makedirs(VID_OUT_DIR, exist_ok=True)
MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID = "export:folder-1794814915069-643ds"

def node_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    if s == "success" and m.get("content"): return "success"
    if s in ("error", "failed"): return "error"
    return s

st = call("canvas_get_state", {})["result"]
nodes = {n["id"]: n for n in st["nodes"]}
conns = st["connections"]
img_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "image" and n.get("title")}
cfg_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "config" and n.get("title")}

# Locate existing Flow direct video nodes
flow_nodes = {}
for n in st["nodes"]:
    if n["type"] == "video" and (n.get("title") or "").startswith("OUT_f20_v"):
        flow_nodes[n["title"]] = n["id"]
print("Existing Flow video nodes:", {k: (v, node_status(nodes.get(v))) for k, v in flow_nodes.items()}, flush=True)

# Flow queue: v3 (if needed) + v5 (skanest_box)
FLOW_REM = [
    ("OUT_f20_v3_banh_thuyen", "f20-k3-banh-thuyen",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the F20 Banh Thuyen nut boat snack pouch standing on the sunlit wooden table surrounded by almonds and cashews, warm golden sunbeams and soft bokeh shimmer in background, keep the pouch and its Vietnamese label 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("OUT_f20_v5_skanest_box", "f20-k5-skanest",
     "Luxury slow macro camera push-in under 4 percent on the round SKA NEST bird's nest gift box resting on draped champagne-gold satin silk, warm golden light sheen sweeping softly across the clear lid and silk folds, keep the red SKA NEST seal and contents 100 percent sharp and unchanged, no hands, no text"),
]

# Muse queue (strictly 1-by-1!): v4 (kep_hat) + v6 (gio_mica) + v7 & v8 already done!
MUSE_REM = [
    ("F20_muse_v4_kep_hat", "f20-k4-kep-hat", "OUT_f20_v4_kep_hat",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the F20 Tue Tam seaweed nut bar pouch standing on the sunlit oak wooden table, warm morning sunlight rays and gentle bokeh shimmer in background, keep the pouch and its Vietnamese label 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("F20_muse_v6_gio_mica", "f20-k6-gio-mica", "OUT_f20_v6_gio_mica",
     "Smooth cinematic slow camera push-in and subtle parallax across the sunlit transparent Mica gift baskets with burgundy leather handles and ribbons on the wooden table, warm natural daylight and soft background bokeh, keep all gift items inside the transparent basket 100 percent unchanged, no text"),
    ("F20_muse_v7_anh_hau", "f20-k7-anh-hau", "OUT_f20_v7_anh_hau", ""),
    ("F20_muse_v8_showroom", "f20-k8-showroom", "OUT_f20_v8_showroom", ""),
]

muse_cfgs = {}
for idx, (mtitle, tag, out_name, mprompt) in enumerate(MUSE_REM):
    if mtitle in cfg_by_title:
        muse_cfgs[mtitle] = cfg_by_title[mtitle]
    else:
        before = {n["id"] for n in st["nodes"]}
        call("canvas_create_generation_flow", {
            "title": mtitle,
            "mode": "video",
            "model": "muse::muse-video",
            "size": "9:16",
            "seconds": "5",
            "x": 38200,
            "y": 1800 + idx * 460,
            "prompt": mprompt,
            "referenceNodeIds": [img_by_title[tag]],
            "autoRun": False,
        })
        time.sleep(1.0)
        st = call("canvas_get_state", {})["result"]
        cand = [n["id"] for n in st["nodes"] if n["id"] not in before and n["type"] == "config"]
        muse_cfgs[mtitle] = cand[-1]
        print(f"Created Muse cfg {mtitle} -> {muse_cfgs[mtitle]}", flush=True)

flow_retries = {}
muse_retries = {}
muse_outs = {}

t0 = time.time()
while time.time() - t0 < 420:
    st = call("canvas_get_state", {})["result"]
    nodes = {n["id"]: n for n in st["nodes"]}
    conns = st["connections"]

    # Check Flow
    act_flow = 0
    f_stat = []
    for vt in ["OUT_f20_v1_full_to_yen", "OUT_f20_v2_hai_rong_bien", "OUT_f20_v3_banh_thuyen", "OUT_f20_v5_skanest_box"]:
        vid_id = flow_nodes.get(vt)
        so = node_status(nodes.get(vid_id)) if vid_id in nodes else "none"
        if so == "loading":
            act_flow += 1
        f_stat.append(f"{vt[8:10]}:{so}")

    # Check Muse
    act_muse = 0
    m_stat = []
    for mtitle, _, out_name, _ in MUSE_REM:
        cid = muse_cfgs[mtitle]
        oids = [c["toNodeId"] for c in conns if c["fromNodeId"] == cid and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "video"]
        muse_outs[mtitle] = oids[-1] if oids else None
        so = node_status(nodes.get(muse_outs[mtitle])) if muse_outs[mtitle] else "none"
        sc = nodes[cid]["metadata"].get("status") if cid in nodes else "none"
        if so == "loading" or sc == "loading":
            act_muse += 1
        m_stat.append(f"{out_name[8:10]}:{so if muse_outs[mtitle] else sc}")

    done_f = sum(1 for vt in ["OUT_f20_v1_full_to_yen", "OUT_f20_v2_hai_rong_bien", "OUT_f20_v3_banh_thuyen", "OUT_f20_v5_skanest_box"]
                 if flow_nodes.get(vt) in nodes and node_status(nodes[flow_nodes[vt]]) == "success")
    done_m = sum(1 for mt, _, _, _ in MUSE_REM if muse_outs.get(mt) and node_status(nodes[muse_outs[mt]]) == "success")
    print(f"[{int(time.time()-t0):3d}s] Flow {done_f}/4 (act={act_flow}) [{' '.join(f_stat)}] | Muse {done_m}/4 (act={act_muse}) [{' '.join(m_stat)}]", flush=True)

    if done_f >= 4 and done_m >= 4:
        break

    # Trigger Flow 1-by-1
    if act_flow < 1:
        for idx, (vt, tag, vp) in enumerate(FLOW_REM):
            vid_id = flow_nodes.get(vt)
            so = node_status(nodes.get(vid_id)) if vid_id in nodes else "none"
            if so == "none" or (so == "error" and flow_retries.get(vt, 0) < 2):
                if vid_id and vid_id in nodes and so == "error":
                    call("canvas_delete_nodes", {"ids": [vid_id]})
                    flow_retries[vt] = flow_retries.get(vt, 0) + 1
                    time.sleep(1.5)
                new_vid_id = f"video-{uuid.uuid4()}"
                img_id = img_by_title[tag]
                comp = f"@[node:{img_id}] {vp}"
                meta = {
                    "generationMode": "video", "composerContent": comp, "prompt": comp, "status": "idle",
                    "model": "flow::flow-omni-1.2-flash", "size": "9:16", "seconds": "6", "vquality": "720",
                    "generateAudio": "false", "watermark": "false", "videoMode": "frames",
                }
                ops = [
                    {"type": "add_node", "nodeType": "video", "id": new_vid_id, "title": vt, "position": {"x": 38050, "y": 900 + idx * 900}, "metadata": meta},
                    {"type": "connect_nodes", "fromNodeId": img_id, "toNodeId": new_vid_id},
                    {"type": "run_generation", "nodeId": new_vid_id, "mode": "video", "prompt": comp},
                ]
                call("canvas_apply_ops", {"ops": ops})
                flow_nodes[vt] = new_vid_id
                act_flow += 1
                print(f"  -> [Flow 1-by-1] Triggered {vt}", flush=True)
                time.sleep(2.0)
                break

    # Trigger Muse strictly 1-by-1!
    if act_muse < 1:
        for mtitle, tag, out_name, mprompt in MUSE_REM:
            cid = muse_cfgs[mtitle]
            oid = muse_outs.get(mtitle)
            so = node_status(nodes.get(oid)) if oid else "none"
            sc = nodes[cid]["metadata"].get("status") if cid in nodes else "none"
            if (oid is None and sc != "loading") or (so == "error" and muse_retries.get(mtitle, 0) < 2):
                if oid and so == "error":
                    call("canvas_delete_nodes", {"ids": [oid]})
                    muse_outs[mtitle] = None
                    muse_retries[mtitle] = muse_retries.get(mtitle, 0) + 1
                    time.sleep(1.5)
                call("canvas_run_generation", {"nodeId": cid, "mode": "video"})
                act_muse += 1
                print(f"  -> [Muse 1-by-1] Triggered {mtitle}", flush=True)
                time.sleep(2.0)
                break

    # If Muse finished its 4 and any Flow video is still unstarted or failed, let Muse finish that single remaining video 1-by-1 so we never get stuck!
    if done_m >= 4 and act_muse < 1:
        for vt, tag, vp in FLOW_REM:
            vid_id = flow_nodes.get(vt)
            so = node_status(nodes.get(vid_id)) if vid_id in nodes else "none"
            if so == "error" and flow_retries.get(vt, 0) >= 2:
                # Fallback via Muse 1-by-1
                fb_title = f"FB_{vt}"
                if fb_title not in cfg_by_title:
                    before = {n["id"] for n in st["nodes"]}
                    call("canvas_create_generation_flow", {
                        "title": fb_title, "mode": "video", "model": "muse::muse-video", "size": "9:16", "seconds": "5",
                        "x": 38600, "y": 900, "prompt": vp, "referenceNodeIds": [img_by_title[tag]], "autoRun": True,
                    })
                    time.sleep(1.5)
                    st2 = call("canvas_get_state", {})["result"]
                    cfg_by_title[fb_title] = [n["id"] for n in st2["nodes"] if n["id"] not in before and n["type"] == "config"][-1]
                break

    time.sleep(7)

# Export ALL 8 finished videos!
st = call("canvas_get_state", {})["result"]
nodes = {n["id"]: n for n in st["nodes"]}
conns = st["connections"]

wanted = {}
for vt in ["OUT_f20_v1_full_to_yen", "OUT_f20_v2_hai_rong_bien", "OUT_f20_v3_banh_thuyen", "OUT_f20_v5_skanest_box"]:
    vid_id = flow_nodes.get(vt)
    if vid_id and vid_id in nodes and node_status(nodes[vid_id]) == "success":
        call("canvas_update_node", {"id": vid_id, "patch": {"title": vt}})
        wanted[vt] = vid_id

for mtitle, _, out_name, _ in MUSE_REM:
    cid = muse_cfgs[mtitle]
    oids = [c["toNodeId"] for c in conns if c["fromNodeId"] == cid and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "video"]
    if oids and node_status(nodes[oids[-1]]) == "success":
        call("canvas_update_node", {"id": oids[-1], "patch": {"title": out_name}})
        wanted[out_name] = oids[-1]

print("Ready to export", len(wanted), "videos:", list(wanted.keys()), flush=True)

ex = [x for x in st["nodes"] if x["id"] == EXPORT_NODE_ID][0]
p = ex["position"]
call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
tok = f"f20-all8-{int(time.time())}"
call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": EXPORT_NODE_ID, "metadata": {"exportAll": True, "exportRequest": tok}}]})

exported_map = {}
for _ in range(20):
    time.sleep(3)
    m = json.load(open(MANIFEST, encoding="utf-8"))
    by_id = {it["nodeId"]: it for it in m.get("items", [])}
    if all(nid in by_id for nid in wanted.values()):
        for name, nid in sorted(wanted.items()):
            src_mp4 = by_id[nid]["path"]
            dst_mp4 = os.path.join(VID_OUT_DIR, f"{name}.mp4")
            ss_trim = "0.25" if "v1_" in name or "v2_" in name or "v3_" in name or "v5_" in name else "0.05"
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-ss", ss_trim, "-i", src_mp4,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
                dst_mp4
            ], check=True)
            exported_map[name] = dst_mp4
        break

json.dump(exported_map, open(os.path.join(VID_OUT_DIR, "flow_videos_manifest.json"), "w", encoding="utf-8"), indent=2)
print("Exported & normalized:", len(exported_map), "videos!", flush=True)

items = sorted(exported_map.items())
cols = 4
rows = max(1, (len(items) + cols - 1) // cols)
sheet = Image.new("RGB", (270 * cols, 480 * rows))
tmp_f = os.path.join(VID_OUT_DIR, "_tmp_f.jpg")
for i, (k, vp) in enumerate(items):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", tmp_f], check=True)
    im = Image.open(tmp_f).resize((270, 480))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 245, 26], fill=(0,0,0))
    d.text((8, 8), k, fill=(255,230,0))
    sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
sheet.save(os.path.join(VID_OUT_DIR, "flow_videos_qc_sheet.jpg"), quality=92)
print("Saved flow_videos_qc_sheet.jpg!", flush=True)
