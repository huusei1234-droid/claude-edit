import sys, time
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

REF_ID = "image-1794815025568-spoom"

BATCH_1B = [
    {
        "key": "icon_c07",
        "title": "BJ-icon-c07",
        "size": "1:1",
        "x": 1800, "y": 0,
        "refs": [],
        "prompt": "Luxury 3D pharmaceutical icon illustration, square 1:1 composition on soft emerald and cream glassmorphism card, two glowing translucent golden vitamin spheres harmonizing with a luminous pearl-white triple-helix collagen ribbon, soft bokeh sparkles, clean studio lighting, no text, no letters, no numbers, no people, no watermark"
    },
    {
        "key": "icon_c08",
        "title": "BJ-icon-c08",
        "size": "1:1",
        "x": 1800, "y": 500,
        "refs": [],
        "prompt": "Premium 3D medical pharmacist icon card, square 1:1 composition on soft mint-cream glassmorphism badge, natural red marine algae Lithothamnion gently transforming into luminous white calcium mineral crystals beside a pearl-white strong bone matrix icon, clean studio lighting, no people, no text, no letters, no numbers, no watermark"
    },
    {
        "key": "packshot_c08",
        "title": "BJ-packshot-c08",
        "size": "9:16",
        "x": 1800, "y": 1000,
        "refs": [REF_ID],
        "prompt": "Commercial pharmaceutical product studio photography, vertical 9:16, keep the exact BOJOMI AN VUONG product box from Ảnh 1 (bojomi-ref) unchanged with identical packaging, logo, colors and front label, placed on a clean white marble podium next to a dark green ceramic cup of creamy grain milk, vanilla orchid flower, oats and warm morning sunlight rim lighting, ultra crisp packshot, no extra text overlays, no people, no watermark"
    }
]

for item in BATCH_1B:
    inp = {
        "prompt": item["prompt"],
        "model": "flow::flow-nano-banana-pro",
        "size": item["size"],
        "count": 1,
        "title": item["title"],
        "x": item["x"],
        "y": item["y"]
    }
    if item["refs"]:
        inp["referenceNodeIds"] = item["refs"]
    res = cv.call("canvas_generate_image", inp)
    print("Submitted", item["title"], "-> ok:", res.get("ok"))
    time.sleep(4)

titles = [x["title"] for x in BATCH_1B]
for step in range(36):
    time.sleep(10)
    st_res = cv.call("canvas_get_state", {})["result"]
    nodes = {n["id"]: n for n in st_res["nodes"]}
    conns = st_res["connections"]
    status_map = {}
    for t in titles:
        cfgs = [n for n in nodes.values() if n["type"] == "config" and (n.get("title") or "").startswith(t)]
        if not cfgs:
            status_map[t] = "no_cfg"
            continue
        cid = cfgs[-1]["id"]
        outs = [nodes[c["toNodeId"]] for c in conns if c["fromNodeId"] == cid and nodes[c["toNodeId"]]["type"] == "image"]
        if not outs:
            status_map[t] = cfgs[-1].get("metadata", {}).get("status", "pending")
        else:
            img_n = outs[-1]
            m = img_n.get("metadata") or {}
            status_map[t] = f"{m.get('status')}|err={str(m.get('error') or '')[:80]}"
    print(f"[{step*10}s]", status_map, flush=True)
    if all(v.startswith("success") or v.startswith("error") for v in status_map.values()):
        print("Batch 1B finished!")
        break
