import sys, os, time, json
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

REF_ID = "image-1794815025568-spoom"

# 1. Ensure reference node has short clean title <= 24 chars per import-flow-config.json rule
cv.call("canvas_update_node", {"id": REF_ID, "patch": {"title": "bojomi-ref"}})
print("Updated reference node title -> bojomi-ref")

BATCH_1A = [
    {
        "key": "hook_01",
        "title": "BJ-hook1",
        "size": "1:1",
        "x": 1200, "y": 0,
        "refs": [],
        "prompt": "Premium 3D medical pharmacist icon card, square 1:1 composition, soft cream and emerald green glassmorphism badge featuring a clean wooden growth ruler, a warm glass of creamy milk, and a luminous pearl-white stylized bone icon with subtle golden sparkles, clean studio lighting, no people, no letters, no numbers, no text, no watermark"
    },
    {
        "key": "hook_02",
        "title": "BJ-hook2",
        "size": "1:1",
        "x": 1200, "y": 500,
        "refs": [],
        "prompt": "Premium 3D medical pharmacist icon card, square 1:1 composition, soft cream and mint-emerald glassmorphism badge featuring a neat healthy meal bowl with salmon, broccoli and eggs next to a glossy 3D emerald question mark icon, bright studio lighting, no people, no letters, no text, no watermark"
    },
    {
        "key": "icon_c04",
        "title": "BJ-icon-c04",
        "size": "1:1",
        "x": 1200, "y": 1000,
        "refs": [],
        "prompt": "Premium 3D pharmacist infographic icon badge, square 1:1 composition on soft cream and emerald glassmorphism card, three clean glossy 3D medical icons arranged neatly: a balanced nutrition plate icon, a biological growth clock icon, and a golden-emerald protective shield heart icon, clean studio lighting, no people, no text, no letters, no numbers, no watermark"
    }
]

for item in BATCH_1A:
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

# Poll until all 3 finish (or error)
titles = [x["title"] for x in BATCH_1A]
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
        print("Batch 1A finished!")
        break
