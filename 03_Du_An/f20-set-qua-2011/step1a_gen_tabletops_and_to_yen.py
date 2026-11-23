import os, sys, json, time, shutil
from PIL import Image
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call

OUT = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"
BG_DIR = os.path.join(OUT, "flow_bgs")
os.makedirs(BG_DIR, exist_ok=True)
MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID = "export:folder-1794814915069-643ds"

PROMPTS = [
    ("F20_bg1_full_to_yen",
     "Ultra-detailed luxury commercial macro photography 9:16 vertical: one whole pristine ivory-white refined edible bird's nest (full whole curved nest with natural long translucent ivory strands) resting center-stage inside a low faceted crystal dish on warm champagne-gold silk fabric, soft golden morning sunbeams and clean warm bokeh space above and below, pure clean composition with NO floating bubbles, NO extra bowls, NO text, NO letters, NO watermark, photorealistic 8k"),
    ("F20_bg2_wood_seaweed",
     "Luxury food commercial product photography background 9:16 vertical: a clean flat warm honey-oak wooden table surface in the lower third with generous empty center stage, garnished lightly near the front corners with a few crispy roasted dark-green nori seaweed flakes and toasted white sesame seeds, soft warm morning sunlight rays streaming through a window with dreamy golden-green bokeh background, empty center ready to place jars, NO jars, NO bottles, NO plates, NO text, NO watermark"),
    ("F20_bg3_wood_nuts",
     "Luxury healthy snack commercial photography background 9:16 vertical: a clean flat warm natural oak wooden table surface in the lower third with generous empty center stage, garnished lightly around the foreground edges with whole roasted almonds, cashews, green pumpkin seeds and golden honey droplets, warm sunlit bakery morning window rays and creamy golden bokeh background, empty center ready to place a pouch, NO bags, NO pouches, NO bowls, NO text, NO watermark"),
    ("F20_bg4_silk_gold",
     "Luxury festive gift commercial background 9:16 vertical: smooth draped champagne-gold and warm cream satin silk fabric across a studio table with soft golden morning light rays, subtle warm red-and-gold floral bokeh in the distant background, clean empty center stage, NO boxes, NO products, NO text, NO watermark"),
]

def node_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    imgs = m.get("images") or []
    if s == "success" or (imgs and imgs[0].get("status") == "success"): return "success"
    if s in ("error", "failed"): return "error"
    return s

def find_new_node(before_ids, ntype):
    st = call("canvas_get_state", {})["result"]
    cand = [n["id"] for n in st["nodes"] if n["id"] not in before_ids and n["type"] == ntype]
    return cand[-1] if cand else None

st = call("canvas_get_state", {})["result"]
cfg_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "config" and n.get("title")}

cfgs = {}
for idx, (title, prompt) in enumerate(PROMPTS):
    if title in cfg_by_title:
        cfgs[title] = cfg_by_title[title]
    else:
        st0 = call("canvas_get_state", {})["result"]
        before = {n["id"] for n in st0["nodes"]}
        call("canvas_create_generation_flow", {
            "title": title,
            "mode": "image",
            "model": "flow::flow-nano-banana-pro",
            "size": "9:16",
            "x": 36200,
            "y": 600 + idx * 480,
            "prompt": prompt,
            "autoRun": False,
        })
        time.sleep(0.8)
        cfgs[title] = find_new_node(before, "config")
        print(f"Created config {title} -> {cfgs[title]}", flush=True)

t0 = time.time()
outs = {}
retries = {}
while time.time() - t0 < 360:
    st = call("canvas_get_state", {})["result"]
    nodes = {n["id"]: n for n in st["nodes"]}
    conns = st["connections"]
    act = 0
    stat = []
    for k, cid in cfgs.items():
        oids = [c["toNodeId"] for c in conns if c["fromNodeId"] == cid and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "image"]
        outs[k] = oids[-1] if oids else None
        so = node_status(nodes.get(outs[k])) if outs[k] else "none"
        sc = node_status(nodes.get(cid))
        if so == "loading" or sc == "loading":
            act += 1
        stat.append(f"{k[4:]}:{so if outs[k] else sc}")
    done = sum(1 for k in cfgs if outs.get(k) and node_status(nodes.get(outs[k])) == "success")
    print(f"[{int(time.time()-t0):3d}s] FlowBGs {done}/{len(cfgs)} (act={act}) | " + ", ".join(stat), flush=True)
    if done >= len(cfgs):
        break
    for k, cid in cfgs.items():
        oid = outs.get(k)
        so = node_status(nodes.get(oid)) if oid else "none"
        sc = node_status(nodes.get(cid))
        if ((oid is None and sc != "loading") or (so == "error" and retries.get(k, 0) < 2)) and act < 1:
            if oid and so == "error":
                call("canvas_delete_nodes", {"ids": [oid]})
                outs[k] = None
                retries[k] = retries.get(k, 0) + 1
                time.sleep(1.5)
            print(f"  -> Running {k}...", flush=True)
            call("canvas_run_generation", {"nodeId": cid, "mode": "image"})
            act += 1
            time.sleep(2.0)
    time.sleep(5)

# Rename output image nodes cleanly and export!
for k, oid in outs.items():
    if oid:
        call("canvas_update_node", {"id": oid, "patch": {"title": f"OUT_{k}"}})

st = call("canvas_get_state", {})["result"]
ex = [x for x in st["nodes"] if x["id"] == EXPORT_NODE_ID][0]
p = ex["position"]
call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
tok = f"f20-bgs-{int(time.time())}"
call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": EXPORT_NODE_ID, "metadata": {"exportAll": True, "exportRequest": tok}}]})

saved = {}
for _ in range(15):
    time.sleep(2)
    if os.path.exists(MANIFEST):
        m = json.load(open(MANIFEST, encoding="utf-8"))
        by_id = {it["nodeId"]: it for it in m.get("items", [])}
        if all(oid in by_id for oid in outs.values() if oid):
            for k, oid in outs.items():
                src = by_id[oid]["path"]
                im = Image.open(src).convert("RGB")
                # Crop 4% margin so zero corner sparkle watermark!
                w, h = im.size
                im_c = im.crop((int(w*0.03), int(h*0.03), int(w*0.97), int(h*0.955))).resize((1080, 1920), Image.Resampling.LANCZOS)
                dst = os.path.join(BG_DIR, f"{k}.jpg")
                im_c.save(dst, quality=95)
                saved[k] = dst
            break

print("Saved BGs:", json.dumps(saved, indent=2))
